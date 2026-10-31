"""E-042 — Budget tests: the ceilings become automated tests.

E-041 wrote the budget book (`ember.budgets`) and pinned its
*stated* numbers with tests that re-assert the book against
itself. This slice makes the ceilings a gate: every test here
RE-DERIVES the cost it judges, in this run, on this machine —
the book's own instruction (E-041 §4: "E-042's tests must
re-derive, not just re-assert"):

1. **Install** — the package tree under `src/ember/` is weighed
   byte by byte (bytecode caches excluded) and judged against
   the toaster's install ceiling, and against E-041's measured
   all-in anchor (the package alone can never weigh more than
   the whole measured install did).
2. **Idle RAM** — a fresh subprocess imports the full CLI/chat
   surface and reports its own peak RSS; judged against the
   toaster's idle ceiling. Where the `sqlite_vec` extra is
   present, the heavier Well-open idle shape is measured too;
   where it is absent that one test skips honestly (the bare
   shape still runs — docket 13's world is the default gate's
   world, and the gate must work in it).
3. **Turn RAM** — a fresh subprocess per profile runs five real
   `chat.run` turns (labelled fake model, in-memory Well,
   history at the profile's cap, E-041's fixture shape) and its
   peak RSS is judged against that profile's turn ceiling —
   and against the toaster's, re-deriving E-041's flatness
   finding instead of trusting it.
4. **Storage growth** — where `sqlite_vec` is present, a fresh
   subprocess grows a real Well by 30 typical episodes and
   measures the closed file's growth per episode, and measures
   the diary's per-turn bytes from two real sessions (1 turn
   vs 6 turns, the difference divided by 5); the projected
   month at the reference workload is judged against the
   toaster's storage ceiling. Absent the extra, it skips.

**Wiring.** These tests live in `tests/unit/`, so the
campaign's slice gate — Run B and Run D of the E-017 method,
which run the whole root suite — collects and runs them on
every slice from here on. That collection is itself pinned by
`test_budget_gate_is_collected_by_the_slice_gate` below: if
this file ever moves out of the gate's path, the gate test
fails instead of the budgets silently unwiring.

Ceilings always come from `ember.budgets` (the book), never
from a second hard-coded copy in this file; the only numbers
hard-coded here are E-041's measured anchors, used as a drift
band (a re-derived shape may wobble around its anchor, but an
order-of-magnitude move is a regression, not weather).

**Measurement discipline (learned in this slice):** the probe
reports its peak as `/proc/self/status` VmHWM, never
`ru_maxrss`. A probe is fork+exec'd from the pytest process,
and on Linux `ru_maxrss` survives exec in the process's
signal_struct — the child inherits the parent's peak. The
first whole-suite Run D proved it the hard way: every probe
reported the identical 71.9 MiB (the pytest process's own
peak at fork time) and six tests failed on a measurement
that was never Ember's. VmHWM belongs to the child's own mm
and resets at exec. E-041's numbers stand — its scripts ran
as top-level processes, where the two measures agree.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from ember.budgets import (
    MEASURED_IDLE_RAM_MIB,
    MEASURED_INSTALL_BYTES,
    MEASURED_TURN_RAM_MIB,
    budget_for,
    storage_bytes_per_turn,
)
from ember.schemas.config import ConversationProfile

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
_MIB = 1024 * 1024

#: A re-derived shape may sit above its E-041 anchor by this
#: much before the drift itself is the failure (machine weather
#: moves RSS; a doubling is not weather).
_DRIFT = 1.5

# --------------------------------------------------------------------- #
# The probe — run in a fresh subprocess so RSS is the shape's own,      #
# never the pytest process's accumulated weight.                       #
# --------------------------------------------------------------------- #

_PROBE = r'''
import io, json, sys
from pathlib import Path

def peak_mib():
    # VmHWM, NOT ru_maxrss: this probe is fork+exec'd from the
    # pytest process, and on Linux ru_maxrss is kept in the
    # process's signal_struct across exec — a forked child would
    # report its PARENT's peak (the full gate proved it: every
    # probe in the whole-suite Run D reported the identical
    # 71.9 MiB, the pytest process's own peak at fork time).
    # VmHWM is the mm's own high-water mark and resets at exec.
    for line in open("/proc/self/status"):
        if line.startswith("VmHWM:"):
            return int(line.split()[1]) / 1024.0
    return -1.0

def rss_mib():
    for line in open("/proc/self/status"):
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) / 1024.0
    return -1.0

mode = sys.argv[1]
out = {}

if mode == "idle":
    import ember  # noqa: F401
    from ember.cli import main as _main  # noqa: F401
    from ember.schemas.config import EmberConfig
    from ember.spark.munnr import chat as _chat  # noqa: F401
    _cfg = EmberConfig()
    out = {"rss_mib": rss_mib(), "peak_mib": peak_mib()}

elif mode == "idle-well":
    try:
        import sqlite_vec  # noqa: F401
    except ImportError:
        print(json.dumps({"skipped": "sqlite_vec extra absent"}))
        sys.exit(0)
    tmp = Path(sys.argv[2])
    from ember.schemas.config import BrunnrConfig, SqliteVecConfig
    from ember.well.brunnr.sqlite_vec import open as sqlite_open
    handle = sqlite_open(
        BrunnrConfig(embedding_dim=4, sqlite_vec=SqliteVecConfig(path=tmp / "store.db"))
    )
    out = {"rss_mib": rss_mib(), "peak_mib": peak_mib()}
    handle.close()

elif mode == "turn":
    import tempfile
    from dataclasses import replace
    from ember.schemas.config import ConversationConfig, ConversationProfile, EmberConfig
    from ember.schemas.episode import Episode
    from ember.schemas.funi import FinishReason
    from ember.schemas.stream import FuniStreamChunk
    from ember.spark.munnr import chat

    prof = ConversationProfile(sys.argv[2])
    conv = ConversationConfig(profile=prof)
    tmp = Path(tempfile.mkdtemp(dir=sys.argv[3]))

    class Well:
        backend_kind = "fake"; embedding_dim = 4
        def __init__(s, stored): s._stored = list(stored); s.added = []
        def recent_episodes(s, limit): return list(s._stored[-limit:])
        def add_episode(s, ep): s.added.append(ep); s._stored.append(ep); return len(s._stored)
        def text_search(s, q, k, filter=None): return []
        def hybrid_search(s, qv, q, k): return []
        def close(s): pass

    class Funi:
        runtime_kind = "fake"; model_id = "fake:tiny"
        def complete_streaming(s, prompt, context, tools=None):
            yield FuniStreamChunk(text_delta="x " * 200, done=True,
                                  finish_reason=FinishReason.STOP, model_id=s.model_id)
        def close(s): pass

    class NullEmbed:
        def embed(s, texts): return [None for _ in texts]

    cap = conv.resolved_max_episodes
    stored = [Episode(operator_input=f"history turn {i} " + "word " * 40,
                      ember_reply="reply " * 40) for i in range(cap)]
    well = Well(stored)
    rc = chat.run(config=replace(EmberConfig(), conversation=conv), config_root=tmp,
                  stdin=io.StringIO("\n".join(f"message {j}" for j in range(5)) + "\n/exit\n"),
                  stdout=io.StringIO(), embed_client=NullEmbed(),
                  funi_opener=lambda _c: Funi(), strengr_opener=lambda *_a: well)
    out = {"rc": rc, "added": len(well.added), "peak_mib": peak_mib()}

elif mode == "storage":
    try:
        import sqlite_vec  # noqa: F401
    except ImportError:
        print(json.dumps({"skipped": "sqlite_vec extra absent"}))
        sys.exit(0)
    import tempfile
    from datetime import UTC, datetime
    from ember.schemas.config import BrunnrConfig, SqliteVecConfig
    from ember.schemas.episode import Episode
    from ember.well.brunnr.sqlite_vec import open as sqlite_open

    base = Path(tempfile.mkdtemp(dir=sys.argv[2]))
    dbdir = base / "well"; dbdir.mkdir()

    def dir_bytes(p):
        return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())

    cfg = BrunnrConfig(embedding_dim=4, sqlite_vec=SqliteVecConfig(path=dbdir / "store.db"))
    h = sqlite_open(cfg); h.close()
    empty = dir_bytes(dbdir)
    h = sqlite_open(cfg)
    n = 30
    for i in range(n):
        h.add_episode(Episode(operator_input=f"turn {i} " + "word " * 40,
                              ember_reply="reply " * 40, funi_model="fake:tiny",
                              started_at=datetime.now(tz=UTC),
                              completed_at=datetime.now(tz=UTC)))
    h.close()
    well_bpe = (dir_bytes(dbdir) - empty) / n

    # Diary per-turn bytes: two real sessions against fake seams,
    # 1 turn then 5 more; the growth between them is 5 turns of diary.
    from dataclasses import replace
    from ember.schemas.config import EmberConfig
    from ember.schemas.funi import FinishReason
    from ember.schemas.stream import FuniStreamChunk
    from ember.spark.munnr import chat

    class Well2:
        backend_kind = "fake"; embedding_dim = 4
        def __init__(s): s.added = []
        def recent_episodes(s, limit): return []
        def add_episode(s, ep): s.added.append(ep); return len(s.added)
        def text_search(s, q, k, filter=None): return []
        def hybrid_search(s, qv, q, k): return []
        def close(s): pass

    class Funi2:
        runtime_kind = "fake"; model_id = "fake:tiny"
        def complete_streaming(s, prompt, context, tools=None):
            yield FuniStreamChunk(text_delta="hello reply", done=True,
                                  finish_reason=FinishReason.STOP, model_id=s.model_id)
        def close(s): pass

    class NullEmbed:
        def embed(s, texts): return [None for _ in texts]

    root = base / "cfgroot"
    def session(turns):
        return chat.run(config=EmberConfig(), config_root=root,
                        stdin=io.StringIO("\n".join(f"msg {i}" for i in range(turns)) + "\n/exit\n"),
                        stdout=io.StringIO(), embed_client=NullEmbed(),
                        funi_opener=lambda _c: Funi2(), strengr_opener=lambda *_a: Well2())
    def diary_bytes():
        d = root / "diary"
        return sum(f.stat().st_size for f in d.glob("*.md")) if d.exists() else 0
    session(1)
    after_one = diary_bytes()
    session(5)
    diary_bpt = (diary_bytes() - after_one) / 5
    out = {"well_bytes_per_episode": well_bpe, "diary_bytes_per_turn": diary_bpt}

print(json.dumps(out))
'''


def _run_probe(tmp_path: Path, *args: str) -> dict:
    probe = tmp_path / "budget_probe_e042.py"
    if not probe.exists():
        probe.write_text(_PROBE, encoding="utf-8")
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(SRC) + (os.pathsep + existing if existing else "")
    result = subprocess.run(
        [sys.executable, str(probe), *args],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    lines = [ln for ln in result.stdout.splitlines() if ln.strip().startswith("{")]
    assert lines, f"probe printed no result: {result.stdout!r} {result.stderr!r}"
    return json.loads(lines[-1])


# --------------------------------------------------------------------- #
# The gate wiring itself                                               #
# --------------------------------------------------------------------- #


def test_budget_gate_is_collected_by_the_slice_gate() -> None:
    # The slice gate (E-017 method, Runs B/D) runs the whole root
    # suite under tests/; a budget test outside that path would
    # silently stop gating. This file must stay in tests/unit/.
    here = Path(__file__).resolve()
    assert here.parent.name == "unit"
    assert here.parent.parent.name == "tests"
    assert here.parent.parent.parent == REPO_ROOT


# --------------------------------------------------------------------- #
# Install — weighed in this run                                        #
# --------------------------------------------------------------------- #


def _package_bytes() -> int:
    total = 0
    for path in (SRC / "ember").rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            total += path.stat().st_size
    return total


def test_install_size_rederived_fits_the_toaster() -> None:
    package = _package_bytes()
    assert package > 0
    toaster = budget_for(ConversationProfile.TOASTER)
    # The package alone, weighed now, fits the smallest ceiling.
    assert package / _MIB <= toaster.install_mib, (
        f"package weighs {package / _MIB:.2f} MiB, over the toaster "
        f"install ceiling of {toaster.install_mib:.2f} MiB"
    )
    # And the package alone can never exceed E-041's measured
    # ALL-IN install (package + dist-info + the default extra):
    # if it does, the anchor — and the book — must be re-measured,
    # not quietly outgrown.
    assert package <= MEASURED_INSTALL_BYTES, (
        f"package alone ({package} B) exceeds E-041's measured "
        f"all-in install anchor ({MEASURED_INSTALL_BYTES} B)"
    )


# --------------------------------------------------------------------- #
# Idle RAM — measured in a fresh process                               #
# --------------------------------------------------------------------- #


def test_idle_ram_rederived_fits_the_toaster(tmp_path: Path) -> None:
    shape = _run_probe(tmp_path, "idle")
    peak = shape["peak_mib"]
    assert peak > 5.0, "a real interpreter shape, not a broken probe"
    toaster = budget_for(ConversationProfile.TOASTER)
    assert peak <= toaster.idle_ram_mib, (
        f"idle peak {peak:.1f} MiB exceeds the toaster ceiling "
        f"of {toaster.idle_ram_mib:.1f} MiB"
    )
    # Drift band: the bare CLI shape measured 25.3 MiB at E-041 and
    # the heavier Well-open anchor is 40.7 — a bare shape beyond
    # 1.5x that anchor is a regression wearing weather's clothes.
    assert peak <= MEASURED_IDLE_RAM_MIB * _DRIFT


def test_idle_well_ram_rederived_fits_the_toaster(tmp_path: Path) -> None:
    shape = _run_probe(tmp_path, "idle-well", str(tmp_path))
    if "skipped" in shape:
        pytest.skip(shape["skipped"])
    peak = shape["peak_mib"]
    toaster = budget_for(ConversationProfile.TOASTER)
    assert peak <= toaster.idle_ram_mib, (
        f"Well-open idle peak {peak:.1f} MiB exceeds the toaster "
        f"ceiling of {toaster.idle_ram_mib:.1f} MiB"
    )
    assert peak <= MEASURED_IDLE_RAM_MIB * _DRIFT


# --------------------------------------------------------------------- #
# Turn RAM — five real turns per profile, fresh process each           #
# --------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "profile",
    [
        ConversationProfile.TOASTER,
        ConversationProfile.PHONE,
        ConversationProfile.PI,
        ConversationProfile.LAPTOP,
    ],
)
def test_turn_ram_rederived_fits_its_profile(
    tmp_path: Path, profile: ConversationProfile
) -> None:
    shape = _run_probe(tmp_path, "turn", profile.value, str(tmp_path))
    assert shape["rc"] == 0
    assert shape["added"] == 5, "five turns really ran and persisted"
    peak = shape["peak_mib"]
    budget = budget_for(profile)
    assert peak <= budget.turn_ram_mib, (
        f"{profile.value} turn peak {peak:.1f} MiB exceeds its "
        f"ceiling of {budget.turn_ram_mib:.1f} MiB"
    )
    # E-041's flatness, re-derived: at fixture scale every
    # profile's turn peak also fits the SMALLEST ceiling.
    toaster = budget_for(ConversationProfile.TOASTER)
    assert peak <= toaster.turn_ram_mib, (
        f"{profile.value} turn peak {peak:.1f} MiB no longer fits "
        f"the toaster ceiling of {toaster.turn_ram_mib:.1f} MiB — "
        "the flat shape E-041 measured has changed"
    )
    assert peak <= MEASURED_TURN_RAM_MIB * _DRIFT


# --------------------------------------------------------------------- #
# Storage growth — real Well + real diary, projected                   #
# --------------------------------------------------------------------- #


def test_storage_growth_rederived_fits_the_toaster(tmp_path: Path) -> None:
    shape = _run_probe(tmp_path, "storage", str(tmp_path))
    if "skipped" in shape:
        pytest.skip(shape["skipped"])
    well_bpe = shape["well_bytes_per_episode"]
    diary_bpt = shape["diary_bytes_per_turn"]
    # Sanity bands first: a broken probe returning 0 or garbage
    # must fail here, not sail under the ceiling.
    assert 100 < well_bpe < 5000, well_bpe
    assert 5 < diary_bpt < 1000, diary_bpt
    per_turn = well_bpe + diary_bpt
    # Drift: the re-derived turn may wobble around E-041's
    # 694 B/turn, but not double past it unnoticed.
    assert per_turn <= storage_bytes_per_turn() * 2, (
        f"re-derived {per_turn:.0f} B/turn is over twice the "
        f"book's {storage_bytes_per_turn()} B/turn"
    )
    monthly_mib = per_turn * 20 * 30 / _MIB  # reference workload
    toaster = budget_for(ConversationProfile.TOASTER)
    assert monthly_mib <= toaster.storage_growth_mib_per_month, (
        f"projected growth {monthly_mib:.2f} MiB/month exceeds the "
        f"toaster ceiling of {toaster.storage_growth_mib_per_month:.2f} MiB/month"
    )

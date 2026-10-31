"""E-045 — Idle discipline: at rest the companion costs ~nothing.

E-041 anchored idle RAM at one instant (40.7 MiB, Well open) and
E-042 turned that instant into a gate test. This slice asks the
question an instant cannot answer: what does the companion cost
*over time* at rest — does it burn CPU while nobody is talking
to it, does its memory creep, does it write to disk, does it
spawn background threads that wake and work?

The hour-long measurement that is this slice's evidence lives
in the slice record (``docs/architecture/E-045_IDLE_DISCIPLINE.md``;
raw samples in ``~/workspace/.verify-tmp/ember-e045/``): four
profile probes idled concurrently for 3,600 s, sampled every
30 s. These tests re-derive the same discipline at gate scale —
a 15-second idle window per probe — so a future regression
(a polling loop, a heartbeat thread, a slow leak, an idle disk
write) fails in the ordinary slice gate instead of being
discovered on someone's small machine:

1. **CPU** — a blocked-at-rest probe's CPU ticks do not advance
   (tolerance: 2 ticks = 20 ms of housekeeping over the window).
2. **Threads** — the idle shape has exactly one thread: the one
   waiting for the operator. No timers, no heartbeats.
3. **RAM** — RSS at the end of the window stays inside the
   toaster's idle ceiling and inside E-041's drift band, and
   does not grow beyond a small wobble band over the window.
4. **Disk** — the Well's directory is byte-identical at the
   start and end of the window: at rest, nothing is written.

Measurement discipline is E-042's: the probe is a fresh
subprocess, peaks are VmHWM (never ``ru_maxrss``, which a
forked child inherits from its parent), and CPU is read from
``/proc/<pid>/stat`` by the parent — the probe itself spends
nothing on measuring. Where the ``sqlite_vec`` extra is absent
the Well-open shape cannot run and these tests skip with the
reason stated (the bare-shape idle gate remains E-042's).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from ember.budgets import MEASURED_IDLE_RAM_MIB, budget_for
from ember.schemas.config import ConversationProfile

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC = REPO_ROOT / "src"
_MIB = 1024 * 1024

#: How long each gate probe idles. The hour belongs to the slice
#: record; the gate re-derives the discipline, it does not
#: re-live the hour on every run.
_IDLE_WINDOW_S = 15.0
_SAMPLE_EVERY_S = 3.0

_PROBE = r'''
import json, sys
from pathlib import Path

profile = sys.argv[1]
work = Path(sys.argv[2])

import ember  # noqa: F401
from ember.cli import main as _main  # noqa: F401
from ember.spark.munnr import chat as _chat  # noqa: F401
from dataclasses import replace
from ember.schemas.config import (
    BrunnrConfig, ConversationConfig, ConversationProfile,
    EmberConfig, SqliteVecConfig,
)
from ember.well.brunnr.sqlite_vec import open as sqlite_open

prof = ConversationProfile(profile)
_cfg = replace(EmberConfig(), conversation=ConversationConfig(profile=prof))
handle = sqlite_open(
    BrunnrConfig(embedding_dim=4, sqlite_vec=SqliteVecConfig(path=work / "store.db"))
)
(work / "ready").write_text("ready")
# Block at rest, as chat waits for the operator, until stdin closes.
try:
    sys.stdin.readline()
except Exception:
    pass
handle.close()
print(json.dumps({"closed": True}))
'''


def _status(pid: int) -> dict:
    fields: dict[str, int] = {}
    for line in open(f"/proc/{pid}/status"):
        if line.startswith(("VmRSS:", "VmHWM:", "Threads:")):
            key, value = line.split(":", 1)
            fields[key] = int(value.split()[0])
    stat = open(f"/proc/{pid}/stat").read().rsplit(")", 1)[1].split()
    fields["cpu_ticks"] = int(stat[11]) + int(stat[12])  # utime + stime
    return fields


def _idle_window(tmp_path: Path, profile: ConversationProfile) -> list[dict] | None:
    """Run one idle probe; sample it from outside for the window.

    Returns the sample rows, or None when the sqlite_vec extra is
    absent (the caller then skips honestly).
    """
    try:
        import sqlite_vec  # noqa: F401
    except ImportError:
        return None
    probe = tmp_path / "idle_probe_e045.py"
    probe.write_text(_PROBE, encoding="utf-8")
    work = tmp_path / "work"
    work.mkdir()
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(SRC) + (os.pathsep + existing if existing else "")
    proc = subprocess.Popen(
        [sys.executable, str(probe), profile.value, str(work)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
    )
    try:
        deadline = time.time() + 60
        while not (work / "ready").exists():
            if proc.poll() is not None:
                raise AssertionError(f"idle probe died: {proc.stderr.read()}")
            if time.time() > deadline:
                raise AssertionError("idle probe never became ready")
            time.sleep(0.1)

        def dir_bytes() -> int:
            return sum(
                f.stat().st_size
                for f in work.rglob("*")
                if f.is_file() and f.name != "ready"
            )

        rows: list[dict] = []
        t0 = time.time()
        while True:
            row = _status(proc.pid)
            row["dir_bytes"] = dir_bytes()
            rows.append(row)
            if time.time() - t0 >= _IDLE_WINDOW_S:
                break
            time.sleep(_SAMPLE_EVERY_S)
        return rows
    finally:
        if proc.stdin:
            proc.stdin.close()
        proc.wait(timeout=60)


@pytest.mark.parametrize(
    "profile",
    [
        ConversationProfile.TOASTER,
        ConversationProfile.PHONE,
        ConversationProfile.PI,
        ConversationProfile.LAPTOP,
    ],
)
def test_idle_costs_nothing_over_the_window(
    tmp_path: Path, profile: ConversationProfile
) -> None:
    rows = _idle_window(tmp_path, profile)
    if rows is None:
        pytest.skip("sqlite_vec extra absent — Well-open idle shape cannot run")
    assert len(rows) >= 4, "the window was really sampled"

    # CPU: a companion at rest burns nothing. 2 ticks (20 ms) of
    # tolerance for interpreter housekeeping; a polling loop or a
    # waking timer would spend orders of magnitude more.
    cpu_ticks = rows[-1]["cpu_ticks"] - rows[0]["cpu_ticks"]
    assert cpu_ticks <= 2, (
        f"{profile.value} idle burned {cpu_ticks} CPU ticks over "
        f"{_IDLE_WINDOW_S:.0f}s — at rest it should burn ~none"
    )

    # Threads: exactly one — the thread waiting for the operator.
    assert max(r["Threads"] for r in rows) == 1

    # RAM: inside the toaster ceiling and E-041's drift band, and
    # no growth beyond a 2 MiB wobble over the window (measured
    # after the first sample, by which the shape has settled).
    rss_last = rows[-1]["VmRSS"] / 1024
    toaster = budget_for(ConversationProfile.TOASTER)
    assert rss_last <= toaster.idle_ram_mib
    assert rss_last <= MEASURED_IDLE_RAM_MIB * 1.5
    settled = [r["VmRSS"] / 1024 for r in rows[1:]]
    # Growth only (E-046 gate fix): the discipline is that idle
    # memory never GROWS. Decline is not a violation — E-045's
    # own hour proved RSS declines monotonically (40.8 -> 23.0
    # MiB) as the kernel reclaims untouched pages, and under
    # memory pressure that decline can land inside this 15 s
    # window (the E-046 Run D gate measured 4.4–9.7 MiB of pure
    # decline and failed on it). The original max-min "wander"
    # assertion therefore contradicted this slice's own
    # evidence; what is judged here is growth past the first
    # settled sample, which is the leak shape.
    assert max(settled) - settled[0] <= 2.0, (
        f"{profile.value} idle RSS grew {max(settled) - settled[0]:.1f} MiB "
        "over the window — idle memory should never grow"
    )

    # Disk: byte-identical — at rest, nothing is written.
    assert rows[-1]["dir_bytes"] == rows[0]["dir_bytes"], (
        f"{profile.value} idle changed its on-disk footprint "
        f"({rows[0]['dir_bytes']} -> {rows[-1]['dir_bytes']} bytes)"
    )


def test_idle_discipline_tests_live_in_the_gate() -> None:
    here = Path(__file__).resolve()
    assert here.parent.name == "unit"
    assert here.parent.parent.name == "tests"
    assert here.parent.parent.parent == REPO_ROOT

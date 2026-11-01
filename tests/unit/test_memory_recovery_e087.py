"""E-087 — Corruption & recovery drills, at the memory face.

The companion's memory lives in three stores written by
three pieces of code: mimir-well's SQLite file (the living
facts; WAL, synchronous FULL), Brunnr's sqlite_vec file
(turns + the fact index; WAL, synchronous FULL), and the
face's own JSON sidecar (persona tags + index map;
replaced atomically, tmp + os.replace). A drill is not a
mock: every test here damages something real — a process
SIGKILLed mid-write, a fault injected inside a
transaction, bytes garbled on disk — and then proves what
the reopened face can honestly say.

What the drills found, and this slice fixed:

* docket 121 — mimir-well's ``supersede`` was TWO commits
  (insert, then mark), so a kill between them left both
  versions current; and a guard-blocked supersede crashed
  with ``TypeError`` (``None < 0``) instead of refusing.
  The insert and the mark are now one transaction, and a
  blocked supersede refuses cleanly (None, nothing
  written, the old fact still current).
* docket 122 — the face's ``_maybe_index`` let a sidecar
  save failure raise *after* the fact had committed in
  mimir-well: the caller was told failure about a write
  that had succeeded. It now returns the honest note
  (fact stored, index record not saved, word search
  still finds it).
* docket 124 — mimir-well's restore swapped the database
  file under two open connections and a live WAL; the
  stale log replayed into the restored file and the
  store came back mixed while reporting success. The
  restore now closes every held connection first and
  removes the replaced file's WAL siblings.

What the drills pin as standing behaviour (not fixed —
named boundaries, docket 123 for the first):

* ``add_turn`` is not crash-atomic across Brunnr + the
  sidecar: a kill between the episode commit and the tag
  save leaves the turn stored but untagged, where the
  docket-117 rule serves it to the default persona only.
  It never reaches a *named* other persona, and it never
  leaves this machine — but the drill pins it so nobody
  claims more.
* A corrupt sidecar degrades fail-closed (facts fall
  back to mimir-well's own per-persona truth for word
  search; meaning search resolves nothing; turns fall
  back to default-persona-only) — the facts themselves
  are untouched.
* A corrupt mimir-well file makes the face open with
  that half *unavailable*, reported, never raised — the
  Brunnr half still serves. A zeroed file is a NEW empty
  store, not a recovered one: the drill names it so.
* A dropped FTS index is rebuilt at open; a backup
  restores the backup-time truth, and a garbled backup
  is refused without touching the live store.

Synthetic canon-flavoured data only (E-089's law,
early). The Brunnr half needs the sqlite_vec extra; the
whole file skips honestly without it (the gate's Run D
supplies it).
"""

from __future__ import annotations

import json
import os
import re
import signal
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-087_CORRUPTION_RECOVERY_DRILLS.md"

pytest.importorskip("sqlite_vec")

sys.path.insert(0, str(REPO / "mimir-well" / "src"))

from ember.schemas.config import (  # noqa: E402
    BrunnrConfig,
    ConversationProfile,
    SqliteVecConfig,
)
from ember.schemas.episode import Episode  # noqa: E402
from ember.well.brunnr.sqlite_vec import open as sv_open  # noqa: E402
from ember.well.memory_face import MemoryFace  # noqa: E402
from mimir_well.core import RunaMemory  # noqa: E402
from mimir_well.repair import validate_backup  # noqa: E402

_VOCAB = [
    "ferry", "letters", "islands", "dawn", "harbour",
    "beekeeper", "honey", "hives", "orchard", "winter",
]
_SYNONYMS = {"boat": "ferry", "post": "letters", "isles": "islands",
             "morning": "dawn", "bees": "beekeeper", "sweet": "honey"}


def embed(text: str) -> tuple[float, ...]:
    words = [_SYNONYMS.get(w.strip(".,?!").lower(), w.strip(".,?!").lower())
             for w in text.split()]
    return tuple(float(words.count(v)) for v in _VOCAB)


DIM = len(_VOCAB)


def _face_at(base: Path, **kw) -> MemoryFace:
    handle = sv_open(BrunnrConfig(
        embedding_dim=DIM,
        sqlite_vec=SqliteVecConfig(path=base / "brunnr.db")))
    mimir = RunaMemory(db_path=str(base / "mimir_well.db"))
    return MemoryFace(
        brunnr=handle, mimir=mimir, mimir_state="live",
        profile=ConversationProfile.LAPTOP, embedder=embed,
        sidecar_path=base / "sidecar.json", **kw)


@pytest.fixture()
def face(tmp_path):
    f = _face_at(tmp_path)
    yield f
    f.close()


def _raw_rows(db: Path, sql: str, args=()):
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(sql, args)]
    finally:
        conn.close()


def _integrity(db: Path) -> str:
    conn = sqlite3.connect(str(db))
    try:
        return conn.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        conn.close()


# --------------------------------------------------------------------- #
# Atomicity — supersede is one transaction (docket 121)                  #
# --------------------------------------------------------------------- #


def test_supersede_leaves_exactly_one_current(tmp_path):
    m = RunaMemory(db_path=str(tmp_path / "m.db"))
    try:
        seed = m.add_memory("The harbour ferry sails at dawn.",
                            user_id="ember")
        v2 = m.supersede(seed, "The harbour ferry sails at first light.",
                         user_id="ember")
        v3 = m.supersede(v2, "The harbour ferry sails before the gulls.",
                         user_id="ember")
        assert v2 and v3 and v2 != v3
        rows = _raw_rows(tmp_path / "m.db",
                         "SELECT * FROM memories WHERE user_id='ember'")
        currents = [r for r in rows if r["is_current"]]
        assert [r["id"] for r in currents] == [v3]
        by_id = {r["id"]: r for r in rows}
        assert by_id[seed]["superseded_by"] == v2
        assert by_id[v2]["superseded_by"] == v3
    finally:
        m.close()


def test_supersede_guard_blocked_refuses_cleanly(tmp_path):
    """Regression: blocked content used to raise TypeError."""
    m = RunaMemory(db_path=str(tmp_path / "m.db"))
    try:
        seed = m.add_memory("The beekeeper keeps nine hives.",
                            user_id="ember")
        before = _raw_rows(tmp_path / "m.db", "SELECT * FROM memories")
        result = m.supersede(seed, "bad\x00content", user_id="ember")
        assert result is None  # refused, not raised
        after = _raw_rows(tmp_path / "m.db", "SELECT * FROM memories")
        assert len(after) == len(before)
        currents = [r for r in after if r["is_current"]]
        assert [r["id"] for r in currents] == [seed]
    finally:
        m.close()


def test_supersede_missing_or_foreign_refuses_whole(tmp_path):
    m = RunaMemory(db_path=str(tmp_path / "m.db"))
    try:
        seed = m.add_memory("The orchard wall faces the winter sun.",
                            user_id="ember")
        assert m.supersede(999999, "A new truth.", user_id="ember") is None
        assert m.supersede(seed, "A stolen truth.", user_id="sage") is None
        rows = _raw_rows(tmp_path / "m.db", "SELECT * FROM memories")
        assert len(rows) == 1 and rows[0]["is_current"] == 1
    finally:
        m.close()


def test_supersede_atomic_under_fault_injection(tmp_path):
    """A failure at the second write step must not split the pair.

    The old two-commit shape fails this drill: its second
    commit (the mark) is exactly the injected failure, and
    the reopened store then holds two current versions.
    The one-transaction shape never issues a second write,
    so the supersede either completes whole or — had the
    failure landed inside its one transaction — rolls back
    whole. Either way: exactly one current, chain intact.
    """
    db = tmp_path / "m.db"
    m = RunaMemory(db_path=str(db))
    seed = m.add_memory("The ferry carries letters at dawn.",
                        user_id="ember")
    real_write = m._write
    calls = {"n": 0}

    def flaky_write(fn):
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("simulated crash at the second write")
        return real_write(fn)

    m._write = flaky_write
    raised = False
    new_id = None
    try:
        new_id = m.supersede(
            seed, "The ferry carries letters before dawn.",
            user_id="ember")
    except RuntimeError:
        raised = True
    finally:
        m._write = real_write
        m.close()

    reopened = RunaMemory(db_path=str(db))
    try:
        rows = _raw_rows(db, "SELECT * FROM memories WHERE user_id='ember'")
        currents = [r for r in rows if r["is_current"]]
        assert len(currents) == 1
        if raised:
            # Rolled back whole: the old fact alone, still current.
            assert currents[0]["id"] == seed
            assert len(rows) == 1
        else:
            # Completed whole: the new fact current, old marked.
            assert currents[0]["id"] == new_id
            by_id = {r["id"]: r for r in rows}
            assert by_id[seed]["superseded_by"] == new_id
    finally:
        reopened.close()


def test_add_memory_atomic_under_fault_injection(tmp_path):
    db = tmp_path / "m.db"
    m = RunaMemory(db_path=str(db))

    def dying_write(fn):
        with m._lock:
            conn = m._get_conn()
            fn(conn)
            raise RuntimeError("simulated crash inside the write")

    m._write = dying_write
    with pytest.raises(RuntimeError):
        m.add_memory("A fact that must not half-exist.", user_id="ember")
    m.close()  # closing rolls the open transaction back

    reopened = RunaMemory(db_path=str(db))
    try:
        rows = _raw_rows(db, "SELECT * FROM memories")
        assert rows == []  # absent whole, never half-present
        assert _integrity(db) == "ok"
    finally:
        reopened.close()


# --------------------------------------------------------------------- #
# Kill-mid-write — real SIGKILL drills in a child process                #
# --------------------------------------------------------------------- #

def _child_script() -> str:
    return r'''
import sys
from pathlib import Path

mode = sys.argv[1]
base = Path(sys.argv[2])
repo = Path(sys.argv[3])
sys.path.insert(0, str(repo / "src"))
sys.path.insert(0, str(repo / "mimir-well" / "src"))

from ember.schemas.config import (BrunnrConfig, ConversationProfile,
                                  SqliteVecConfig)
from ember.well.brunnr.sqlite_vec import open as sv_open
from ember.well.memory_face import MemoryFace
from mimir_well.core import RunaMemory

_VOCAB = ["ferry", "letters", "islands", "dawn", "harbour",
          "beekeeper", "honey", "hives", "orchard", "winter"]
_SYN = {"boat": "ferry", "post": "letters", "isles": "islands",
        "morning": "dawn", "bees": "beekeeper", "sweet": "honey"}

def embed(text):
    words = [_SYN.get(w.strip(".,?!").lower(), w.strip(".,?!").lower())
             for w in text.split()]
    return tuple(float(words.count(v)) for v in _VOCAB)

handle = sv_open(BrunnrConfig(
    embedding_dim=len(_VOCAB),
    sqlite_vec=SqliteVecConfig(path=base / "brunnr.db")))
mimir = RunaMemory(db_path=str(base / "mimir_well.db"))
face = MemoryFace(brunnr=handle, mimir=mimir, mimir_state="live",
                  profile=ConversationProfile.LAPTOP, embedder=embed,
                  sidecar_path=base / "sidecar.json")

if mode == "facts":
    i = 0
    while True:
        res = face.remember_fact(
            f"kiln fact {i} ember holds jar {i}",
            category="household", importance=6, persona_id="ember")
        print(f"FACT {i} {res.fact_id}", flush=True)
        i += 1
elif mode == "supersede":
    res = face.remember_fact(
        "chain fact version 0 ember holds the dawn ferry",
        category="lesson", importance=6, persona_id="ember")
    cur = res.fact_id
    print(f"SEED {cur}", flush=True)
    v = 1
    while True:
        res = face.supersede_fact(
            cur, f"chain fact version {v} ember holds the dawn ferry",
            persona_id="ember")
        print(f"SUPER {v} {res.fact_id}", flush=True)
        cur = res.fact_id
        v += 1
'''


def _extras_parent() -> str:
    import sqlite_vec
    return str(Path(sqlite_vec.__file__).resolve().parent.parent)


def _run_child_until(tmp_path: Path, mode: str, marker: str,
                     minimum: int, deadline_s: float = 180.0):
    """Run the drill child, collect its commit lines, SIGKILL it."""
    script = tmp_path / f"child_{mode}.py"
    script.write_text(_child_script(), encoding="utf-8")
    base = tmp_path / f"store_{mode}"
    base.mkdir()
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [_extras_parent(), str(REPO / "src"),
         str(REPO / "mimir-well" / "src")])
    env["TMPDIR"] = str(tmp_path)
    err_file = open(tmp_path / f"child_{mode}.err", "wb")
    proc = subprocess.Popen(
        [sys.executable, str(script), mode, str(base), str(REPO)],
        stdout=subprocess.PIPE, stderr=err_file,
        text=True, env=env)
    lines: list[str] = []
    deadline = time.monotonic() + deadline_s
    try:
        while time.monotonic() < deadline:
            line = proc.stdout.readline()
            if not line:
                break
            lines.append(line.strip())
            if sum(1 for ln in lines if ln.startswith(marker)) >= minimum:
                break
    finally:
        proc.send_signal(signal.SIGKILL)
        proc.wait(timeout=30)
    return base, lines


@pytest.mark.parametrize("round_no", [1, 2])
def test_kill_mid_fact_writes_recovers_clean(tmp_path, round_no):
    base, lines = _run_child_until(tmp_path, "facts", "FACT ", minimum=10)
    printed = {}
    for ln in lines:
        parts = ln.split()
        if len(parts) == 3 and parts[0] == "FACT":
            printed[int(parts[2])] = int(parts[1])
    assert len(printed) >= 3, f"drill child committed too few: {lines!r}"

    db = base / "mimir_well.db"
    assert _integrity(db) == "ok"
    rows = _raw_rows(db, "SELECT * FROM memories WHERE user_id='ember'")
    by_id = {r["id"]: r for r in rows}
    # Every fact the child reported committed is present, whole.
    for fact_id, i in printed.items():
        assert fact_id in by_id
        assert by_id[fact_id]["content"] == f"kiln fact {i} ember holds jar {i}"
        assert by_id[fact_id]["is_current"] == 1
    # At most one unreported row (the one in flight at the
    # kill), and if present it is complete — never torn.
    extra = [r for fid, r in by_id.items() if fid not in printed]
    assert len(extra) <= 1
    for r in extra:
        assert re.fullmatch(r"kiln fact \d+ ember holds jar \d+",
                            r["content"])
    # The reopened face serves the memory honestly.
    f = _face_at(base)
    try:
        assert f.state()["mimir_well"] == "live"
        hits = f.recall_facts_word("kiln", limit=10000,
                                   persona_id="ember")
        assert len(hits) == len(rows)
    finally:
        f.close()


@pytest.mark.parametrize("round_no", [1, 2])
def test_kill_mid_supersede_chain_keeps_one_current(tmp_path, round_no):
    base, lines = _run_child_until(tmp_path, "supersede", "SUPER ",
                                   minimum=6)
    seed = None
    printed = []
    for ln in lines:
        parts = ln.split()
        if len(parts) == 2 and parts[0] == "SEED":
            seed = int(parts[1])
        elif len(parts) == 3 and parts[0] == "SUPER":
            printed.append((int(parts[1]), int(parts[2])))
    assert seed is not None and len(printed) >= 3, \
        f"drill child committed too few: {lines!r}"

    db = base / "mimir_well.db"
    assert _integrity(db) == "ok"
    rows = _raw_rows(db, "SELECT * FROM memories WHERE user_id='ember'")
    by_id = {r["id"]: r for r in rows}
    # One transaction per supersede: the store holds the seed
    # plus exactly the reported commits, plus at most one
    # in-flight commit that landed before the kill.
    assert len(rows) in (1 + len(printed), 2 + len(printed))
    for _v, fid in printed:
        assert fid in by_id
    # Exactly one current truth, and it is the newest whole
    # version — the last reported commit, or the in-flight
    # one after it, or (if the kill caught the newest
    # transaction open) the one before: never two, never none.
    currents = [r for r in rows if r["is_current"]]
    assert len(currents) == 1
    allowed = {printed[-1][1]}
    if len(printed) >= 2:
        allowed.add(printed[-2][1])
    allowed.update(fid for fid in by_id if fid not in
                   {p[1] for p in printed} and fid != seed)
    assert currents[0]["id"] in allowed
    # The chain is intact: every old version names its heir,
    # and every heir exists.
    for r in rows:
        if not r["is_current"]:
            assert r["superseded_by"] in by_id
            assert re.fullmatch(
                r"chain fact version \d+ ember holds the dawn ferry",
                r["content"])
    assert re.fullmatch(
        r"chain fact version \d+ ember holds the dawn ferry",
        currents[0]["content"])


# --------------------------------------------------------------------- #
# Corruption — sidecar                                                   #
# --------------------------------------------------------------------- #


def _seed_two_personae(f: MemoryFace):
    f.remember_fact("The beekeeper keeps nine hives behind the orchard.",
                    category="household", importance=8, persona_id="ember")
    f.remember_fact("The harbour ferry carries letters at dawn.",
                    category="lesson", importance=5, persona_id="sage")
    f.add_turn(Episode(operator_input="When is the ferry?",
                       ember_reply="At dawn.", persona_id="ember"))
    f.add_turn(Episode(operator_input="Tell me about honey.",
                       ember_reply="Sweet, from the hives.",
                       persona_id="sage"))


def test_corrupt_sidecar_degrades_fail_closed(tmp_path):
    f = _face_at(tmp_path)
    _seed_two_personae(f)
    f.close()
    (tmp_path / "sidecar.json").write_bytes(b"\x89garbage{{{not json")

    f2 = _face_at(tmp_path)
    try:
        assert f2.state()["mimir_well"] == "live"
        # Facts survive whole: word search reads mimir-well's
        # own per-persona truth, which never lived in the sidecar.
        ember = f2.recall_facts_word("beekeeper", persona_id="ember")
        sage = f2.recall_facts_word("ferry", persona_id="sage")
        assert len(ember) == 1 and len(sage) == 1
        assert f2.recall_facts_word("beekeeper", persona_id="sage") == []
        # Meaning search resolves nothing: the chunk map is
        # gone, and unmapped chunks are dropped, never guessed
        # into another persona's hands.
        hits = f2.search_facts_meaning("honey", persona_id="sage")
        assert hits.facts == ()
        # Turns fall back to the default persona only (the
        # sidecar's stated fail-closed shape) — every tag
        # died with the sidecar, so even "ember"'s own turn
        # now answers only to the default persona.
        assert f2.recent_turns(persona_id="sage") == []
        assert f2.recent_turns(persona_id="ember") == []
        default_turns = f2.recent_turns()  # None -> the default persona
        assert len(default_turns) == 2  # both, untagged -> default's
    finally:
        f2.close()


def test_orphan_sidecar_tmp_is_ignored(tmp_path):
    f = _face_at(tmp_path)
    _seed_two_personae(f)
    f.close()
    # A save killed mid-replace leaves its .tmp behind; the
    # last whole file must win, untouched.
    (tmp_path / "sidecar.json.tmp").write_bytes(b"torn half-save")

    f2 = _face_at(tmp_path)
    try:
        sage_turns = f2.recent_turns(persona_id="sage")
        assert len(sage_turns) == 1
        assert sage_turns[0].operator_input == "Tell me about honey."
        hits = f2.search_facts_meaning("honey", persona_id="sage")
        assert len(hits.facts) == 1
    finally:
        f2.close()


def test_sidecar_save_failure_reports_honestly(tmp_path, monkeypatch):
    """Docket 122 regression: no raise across a committed write."""
    f = _face_at(tmp_path)
    try:
        def boom():
            raise OSError("disk full (drill)")
        monkeypatch.setattr(f._sidecar, "save", boom)
        res = f.remember_fact(
            "The beekeeper keeps nine hives behind the orchard.",
            category="household", importance=8, persona_id="ember")
        assert res.fact_id is not None  # the fact WAS stored
        assert res.indexed is False
        assert "index record could not be saved" in res.note
        hits = f.recall_facts_word("beekeeper", persona_id="ember")
        assert len(hits) == 1  # word search still finds it
    finally:
        f.close()


def test_add_turn_tag_save_failure_is_the_named_boundary(
        tmp_path, monkeypatch):
    """Docket 123: add_turn is not crash-atomic across stores.

    The episode commits in Brunnr before its persona tag is
    saved; a save failure raises (the caller is told), and
    after a restart the untagged turn is served to the
    default persona only — pinned here so the boundary is
    a measured fact, not a claim.
    """
    f = _face_at(tmp_path)
    def boom():
        raise OSError("disk full (drill)")
    monkeypatch.setattr(f._sidecar, "save", boom)
    with pytest.raises(OSError):
        f.add_turn(Episode(operator_input="Tell me about honey.",
                           ember_reply="Sweet, from the hives.",
                           persona_id="sage"))
    f.close()

    f2 = _face_at(tmp_path)
    try:
        assert f2.recent_turns(persona_id="sage") == []
        default_turns = f2.recent_turns()  # None -> the default persona
        assert len(default_turns) == 1
        assert default_turns[0].operator_input == "Tell me about honey."
    finally:
        f2.close()


# --------------------------------------------------------------------- #
# Corruption — the stores themselves                                     #
# --------------------------------------------------------------------- #


def test_corrupt_mimir_file_face_opens_unavailable(tmp_path):
    f = _face_at(tmp_path)
    _seed_two_personae(f)
    f.close()
    db = tmp_path / "mimir_well.db"
    blob = bytearray(db.read_bytes())
    blob[:4096] = b"\xab" * 4096
    db.write_bytes(bytes(blob))
    for suffix in ("-wal", "-shm"):
        p = Path(str(db) + suffix)
        if p.exists():
            p.unlink()

    handle = sv_open(BrunnrConfig(
        embedding_dim=DIM,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "brunnr.db")))
    face = MemoryFace.open(brunnr=handle, mimir_db_path=db,
                           sidecar_path=tmp_path / "sidecar.json",
                           embedder=embed)
    try:
        state = face.state()
        assert state["mimir_well"].startswith("unavailable")
        assert state["brunnr"] == "live"
        res = face.remember_fact("Anything at all.", persona_id="ember")
        assert res.fact_id is None
        assert "unavailable" in res.note
        assert face.recall_current(persona_id="ember") == []
        # The Brunnr half still serves its turns.
        turn_id = face.add_turn(Episode(
            operator_input="Are you there?",
            ember_reply="Half of me is.", persona_id="ember"))
        assert turn_id is not None
    finally:
        face.close()


def test_zero_byte_mimir_file_reinitialises_empty(tmp_path):
    db = tmp_path / "mimir_well.db"
    db.write_bytes(b"")
    m = RunaMemory(db_path=str(db))
    try:
        assert m.recall_current(user_id="ember", min_importance=1) == []
        assert _integrity(db) == "ok"
        # A zeroed store is a NEW store: usable, and honestly empty.
        fid = m.add_memory("First fact of the new store.",
                           user_id="ember")
        assert fid and fid > 0
    finally:
        m.close()


def test_dropped_fts_index_recovers_on_open(tmp_path):
    db = tmp_path / "mimir_well.db"
    m = RunaMemory(db_path=str(db))
    m.add_memory("The beekeeper keeps nine hives.", user_id="ember")
    m.close()
    conn = sqlite3.connect(str(db))
    conn.execute("DROP TABLE memories_fts")
    conn.commit()
    conn.close()

    m2 = RunaMemory(db_path=str(db))
    try:
        hits = m2.fts_search("memories", "beekeeper", user_id="ember")
        assert len(hits) == 1
    finally:
        m2.close()


def test_backup_restore_roundtrip_and_garbled_backup_refused(tmp_path):
    db = tmp_path / "mimir_well.db"
    backup = tmp_path / "backup.db"
    m = RunaMemory(db_path=str(db))
    m.add_memory("The harbour ferry sails at dawn.", user_id="ember")
    m.add_memory("The beekeeper keeps nine hives.", user_id="ember")
    m.backup_to(str(backup))
    m.add_memory("A later fact, not in the backup.", user_id="ember")
    assert len(m.recall_current(user_id="ember", min_importance=1)) == 3

    garbled = tmp_path / "garbled.db"
    garbled.write_bytes(b"not a database at all" * 64)
    assert validate_backup(str(garbled)) is False
    assert m.restore_from(str(garbled)) is False
    # The refused restore touched nothing.
    assert len(m.recall_current(user_id="ember", min_importance=1)) == 3

    assert m.restore_from(str(backup)) is True
    contents = {r["content"] for r in
                m.recall_current(user_id="ember", min_importance=1)}
    assert contents == {"The harbour ferry sails at dawn.",
                        "The beekeeper keeps nine hives."}
    m.close()


# --------------------------------------------------------------------- #
# The doc                                                                  #
# --------------------------------------------------------------------- #


def test_doc_names_the_drills_and_the_dockets():
    text = DOC.read_text(encoding="utf-8")
    for needle in ("kill-mid-write", "atomicity", "SIGKILL",
                   "docket 121", "docket 122", "docket 123",
                   "docket 124", "fail-closed", "one transaction"):
        assert needle in text, needle

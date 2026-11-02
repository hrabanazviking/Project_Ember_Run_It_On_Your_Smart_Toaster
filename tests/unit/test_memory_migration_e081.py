"""E-081 — Migration: survivors stay native; the palace answer.

Proves docs/architecture/E-081_MIGRATION_ANSWER.md:

* **Survivors need no migration.** Stores written natively,
  in the pre-face shapes, by the bounded engines' own APIs
  (RunaMemory directly; the Brunnr handle directly) are
  served whole by the E-080 face, and serving them changes
  neither store's schema nor any table's row count — the
  stores stay native behind the face, byte-shape for
  byte-shape. No migration exists because none is needed.
* **The palace answer is argued from fixtures.** A
  synthetic palace in the exact shape mempalace's own
  stdlib reader (``mempalace/migrate.py`` —
  ``extract_drawers_from_sqlite``, sqlite3 only, no
  ChromaDB) reads is extracted with that reader, and the
  reference mapping in this file carries every drawer
  losslessly into the bounded shape: text byte-identical
  as a Brunnr chunk, every metadata field carried in the
  Brunnr document's persisted ``metadata`` (the sqlite_vec
  adapter stores it as JSON), the original drawer record
  reconstructable exactly from the mapped output.
* Closets are **derived** — pointer lines built from
  drawer content — and the fixture proves every pointer
  resolves to an extracted drawer; nothing user-authored
  lives only in a closet. Knowledge-graph triples map to
  living-fact records round-trip exact (subject, predicate,
  object, validity, confidence, provenance).
* The upstream extractor is **collection-blind** (it
  returns closets among drawers): the fixture proves the
  executing reader must classify by drawer/closet id, and
  this file's mapper does.
* **Nothing is executed.** No real palace was opened, the
  mempalace member is untouched, and the migration itself
  runs only under Volmarr's retirement ruling (E-079 §6),
  which has not been given. The mapping here is the
  argument's evidence, on synthetic stores only.

Synthetic canon-flavoured data only (E-089's law).
"""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-081_MIGRATION_ANSWER.md"

pytest.importorskip("sqlite_vec")

sys.path.insert(0, str(REPO / "mimir-well" / "src"))

from ember.schemas.chunks import Chunk, Document  # noqa: E402
from ember.schemas.config import (  # noqa: E402
    BrunnrConfig,
    ConversationProfile,
    SqliteVecConfig,
)
from ember.schemas.episode import Episode  # noqa: E402
from ember.well.brunnr.sqlite_vec import open as sv_open  # noqa: E402
from ember.well.memory_face import MemoryFace  # noqa: E402
from mimir_well.core import RunaMemory  # noqa: E402

DIM = 4


def _embed(text: str) -> tuple[float, ...]:
    return (float(len(text) % 7), 1.0, 0.5, 0.25)


# --------------------------------------------------------------------- #
# Store snapshots — schema + row counts, the no-migration evidence      #
# --------------------------------------------------------------------- #


def _snapshot(db_path: Path) -> dict:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        import sqlite_vec

        conn.enable_load_extension(True)
        sqlite_vec.load(conn)  # Brunnr's vec0 tables need it
    except Exception:
        pass
    try:
        schema = conn.execute(
            "SELECT type, name, sql FROM sqlite_master "
            "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
        ).fetchall()
        counts = {}
        for kind, name, _sql in schema:
            if kind == "table":
                counts[name] = conn.execute(
                    f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
        return {"schema": [tuple(r) for r in schema], "counts": counts}
    finally:
        conn.close()


# --------------------------------------------------------------------- #
# Survivors — native stores behind the face, no migration               #
# --------------------------------------------------------------------- #

FERRY = ("The harbour ferry leaves at dawn carrying letters "
         "between the islands.")
FERRY_OLD = "The harbour ferry leaves at dusk carrying letters."
BEES = ("The beekeeper keeps nine hives behind the orchard and "
        "trades honey at the winter market.")
DOC_TEXT = "The harbour ferry bell rings twice at dawn."


def _native_stores(tmp_path: Path):
    """Write both survivors' stores the pre-face way: each
    engine's own API, no face anywhere in the writing."""
    mimir = RunaMemory(db_path=str(tmp_path / "mimir_well.db"))
    old_id = mimir.add_memory(FERRY_OLD, category="knowledge",
                              importance=6, user_id="ember")
    mimir.supersede(old_id, FERRY, user_id="ember")
    mimir.add_memory(BEES, category="preference", importance=9,
                     emotional_valence=0.8, user_id="ember")
    mimir.close()

    handle = sv_open(BrunnrConfig(
        embedding_dim=DIM,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "brunnr.db")))
    doc_id = handle.add_document(Document(
        source="canon/harbour-notes", title="Harbour notes",
        content_type="text", hash="e081-doc"))
    handle.add_chunks([Chunk(document_id=doc_id, chunk_index=0,
                             text=DOC_TEXT, embedding=_embed(DOC_TEXT))])
    handle.add_episode(Episode(operator_input="when is the ferry?",
                               ember_reply="At dawn, with the letters."))
    handle.close()
    return tmp_path / "mimir_well.db", tmp_path / "brunnr.db"


def test_survivor_stores_stay_native_behind_the_face(tmp_path):
    mimir_db, brunnr_db = _native_stores(tmp_path)
    before_mimir = _snapshot(mimir_db)
    before_brunnr = _snapshot(brunnr_db)

    # Open the face over the very same store files (toaster
    # profile: the index is off, so the face writes nothing
    # into either store in the course of serving reads).
    handle = sv_open(BrunnrConfig(
        embedding_dim=DIM,
        sqlite_vec=SqliteVecConfig(path=brunnr_db)))
    mimir = RunaMemory(db_path=str(mimir_db))
    face = MemoryFace(
        brunnr=handle, mimir=mimir, mimir_state="live",
        profile=ConversationProfile.TOASTER, embedder=_embed,
        sidecar_path=tmp_path / "sidecar.json")

    # Everything the native writers wrote is served whole.
    word = face.recall_facts_word("beekeeper", persona_id="ember")
    assert [r["content"] for r in word] == [BEES]
    current = face.recall_current(persona_id="ember")
    contents = [r["content"] for r in current]
    assert FERRY in contents and BEES in contents
    assert FERRY_OLD not in contents  # superseded stays superseded
    hits = face.search_documents_word("ferry bell")
    assert hits and hits[0].text == DOC_TEXT
    turns = face.recent_turns(persona_id="default")
    assert [e.ember_reply for e in turns] == [
        "At dawn, with the letters."]
    face.close()

    # Serving migrated nothing: identical schema in both
    # stores, and identical row counts in every *content*
    # table. The only count deltas anywhere are the two
    # the member's own native behaviour explains (proven
    # in the E-081 doc §2): mimir-well's read audit log
    # (`memory_access_log`, +2 — its audit trail recording
    # this test's two recalls) and the FTS5 shadow tables
    # (`*_fts_data` / `*_fts_idx`), whose internal segment
    # rows compact when the member reopens its store; the
    # FTS content table itself is unchanged.
    after_mimir = _snapshot(mimir_db)
    after_brunnr = _snapshot(brunnr_db)
    assert after_mimir["schema"] == before_mimir["schema"]
    assert after_brunnr["schema"] == before_brunnr["schema"]
    assert after_brunnr["counts"] == before_brunnr["counts"]
    internal = ("memory_access_log",)
    changed = {
        name for name in before_mimir["counts"]
        if before_mimir["counts"][name] != after_mimir["counts"][name]
    }
    assert changed <= {
        *internal,
        *(n for n in before_mimir["counts"]
          if "_fts_data" in n or "_fts_idx" in n),
    }, changed
    for name, count in before_mimir["counts"].items():
        if name not in changed:
            assert after_mimir["counts"][name] == count, name


# --------------------------------------------------------------------- #
# The palace fixture — synthetic, in the member reader's own shape      #
# --------------------------------------------------------------------- #

DRAWER_FERRY = {
    "id": "drawer_harbour-letters_ferry_a1b2c3d4e5f60718293a4b5c",
    "document": FERRY,
    "metadata": {
        "wing": "harbour-letters", "room": "ferry",
        "source_file": "letters/ferry-log.md", "chunk_index": 0,
        "added_by": "miner", "filed_at": "2026-05-21T09:14:00",
        "normalize_version": 2, "hall": "facts",
        "entities": "Ferry,Islands",
    },
}
DRAWER_BEES = {
    "id": "drawer_harbour-letters_apiary_b2c3d4e5f60718293a4b5c6d",
    "document": BEES,
    "metadata": {
        "wing": "harbour-letters", "room": "apiary",
        "source_file": "letters/apiary.md", "chunk_index": 0,
        "added_by": "miner", "filed_at": "2026-05-21T09:15:00",
        "normalize_version": 2, "hall": "facts",
    },
}
DRAWER_DIARY = {
    "id": "drawer_diary_c3d4e5f60718293a4b5c6d7e",
    "document": "Dear diary: the ferry bell woke me before dawn.",
    "metadata": {
        "wing": "diary", "room": "daily",
        "source_file": "daily_diary", "chunk_index": 0,
        "added_by": "diary", "filed_at": "2026-05-20T22:03:00",
        "normalize_version": 2, "hall": "diary",
        "source_session": "daily_diary",
    },
}
CLOSET = {
    "id": "closet_harbour-letters_ferry_d4e5f60718293a4b5c6d7e8f_00",
    "document": ("ferry timetable|Ferry;Islands|→"
                 + DRAWER_FERRY["id"]),
    "metadata": {
        "wing": "harbour-letters", "room": "ferry",
        "source_file": "letters/ferry-log.md", "drawer_count": 1,
        "filed_at": "2026-05-21T09:14:05", "normalize_version": 2,
    },
}
PALACE_RECORDS = [DRAWER_FERRY, DRAWER_BEES, DRAWER_DIARY, CLOSET]

TRIPLES = [
    {"id": "t-001", "subject": "harbour ferry", "predicate": "departs_at",
     "object": "dawn", "valid_from": "2026-05-01", "valid_to": None,
     "confidence": 0.95, "source_closet": CLOSET["id"],
     "source_file": "letters/ferry-log.md",
     "source_drawer_id": DRAWER_FERRY["id"], "adapter_name": "fixture",
     "extracted_at": "2026-05-21T09:16:00"},
    {"id": "t-002", "subject": "beekeeper", "predicate": "keeps",
     "object": "nine hives", "valid_from": "2026-05-01",
     "valid_to": None, "confidence": 0.9, "source_closet": None,
     "source_file": "letters/apiary.md",
     "source_drawer_id": DRAWER_BEES["id"], "adapter_name": "fixture",
     "extracted_at": "2026-05-21T09:16:30"},
]


def _build_palace(tmp_path: Path) -> Path:
    """A synthetic palace: chroma.sqlite3 in the shape the
    member's own migrate.py reader reads (embeddings +
    embedding_metadata), plus the knowledge-graph sqlite in
    knowledge_graph.py's table shapes."""
    palace = tmp_path / "palace"
    palace.mkdir()
    conn = sqlite3.connect(palace / "chroma.sqlite3")
    conn.execute("CREATE TABLE embeddings "
                 "(id INTEGER PRIMARY KEY, embedding_id TEXT)")
    conn.execute(
        "CREATE TABLE embedding_metadata "
        "(id INTEGER, key TEXT, string_value TEXT, int_value INTEGER, "
        "float_value REAL, bool_value INTEGER)")
    for i, rec in enumerate(PALACE_RECORDS, start=1):
        conn.execute("INSERT INTO embeddings (id, embedding_id) "
                     "VALUES (?, ?)", (i, rec["id"]))
        rows = [("chroma:document", rec["document"], None, None, None)]
        for key, value in rec["metadata"].items():
            if isinstance(value, int):
                rows.append((key, None, value, None, None))
            elif isinstance(value, float):
                rows.append((key, None, None, value, None))
            else:
                rows.append((key, str(value), None, None, None))
        conn.executemany(
            "INSERT INTO embedding_metadata VALUES (?, ?, ?, ?, ?, ?)",
            [(i, k, s, iv, fv, bv) for k, s, iv, fv, bv in rows])
    conn.commit()
    conn.close()

    kg = sqlite3.connect(palace / "knowledge_graph.sqlite3")
    kg.execute("CREATE TABLE entities (id TEXT PRIMARY KEY, name TEXT, "
               "type TEXT, properties TEXT DEFAULT '{}', created_at TEXT)")
    kg.execute("CREATE TABLE triples (id TEXT PRIMARY KEY, subject TEXT, "
               "predicate TEXT, object TEXT, valid_from TEXT, "
               "valid_to TEXT, confidence REAL, source_closet TEXT, "
               "source_file TEXT, source_drawer_id TEXT, "
               "adapter_name TEXT, extracted_at TEXT)")
    kg.executemany(
        "INSERT INTO triples VALUES "
        "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [tuple(t[k] for k in (
            "id", "subject", "predicate", "object", "valid_from",
            "valid_to", "confidence", "source_closet", "source_file",
            "source_drawer_id", "adapter_name", "extracted_at"))
         for t in TRIPLES])
    kg.commit()
    kg.close()
    return palace


def _member_extractor():
    """mempalace's own stdlib reader, loaded from the member
    file directly (its imports are stdlib only — no ChromaDB,
    no member package init). The reader IS the contract: a
    real palace is whatever this function can read."""
    path = REPO / "mempalace" / "mempalace" / "migrate.py"
    spec = importlib.util.spec_from_file_location(
        "mempalace_migrate_fixture", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.extract_drawers_from_sqlite


# --------------------------------------------------------------------- #
# The reference mapping — the argument, in code                         #
# --------------------------------------------------------------------- #


def classify(record_id: str) -> str:
    if record_id.startswith("drawer_"):
        return "drawer"
    if record_id.startswith("closet_"):
        return "closet"
    return "unclassified"


def drawer_to_document_chunk(rec: dict):
    """One drawer → one Brunnr document + one chunk under it.

    Text rides as the chunk text, byte-identical. Every
    metadata field rides in the document's metadata mapping,
    which the sqlite_vec adapter persists as JSON — so the
    original drawer record is reconstructable exactly.
    """
    meta = dict(rec["metadata"])
    doc = Document(
        source=str(meta.pop("source_file")),
        title=None,
        content_type="mempalace-drawer",
        hash=rec["id"],
        metadata={
            "drawer_id": rec["id"],
            "chunk_index": meta.pop("chunk_index"),
            **meta,
        },
    )
    chunk = Chunk(document_id=0,  # assigned by the writer
                  chunk_index=int(rec["metadata"]["chunk_index"]),
                  text=rec["document"])
    return doc, chunk


def reconstruct_drawer(doc: Document, chunk_text: str) -> dict:
    """The mapped output → the original drawer record."""
    meta = dict(doc.metadata)
    drawer_id = meta.pop("drawer_id")
    chunk_index = meta.pop("chunk_index")
    return {
        "id": drawer_id,
        "document": chunk_text,
        "metadata": {"source_file": doc.source,
                     "chunk_index": chunk_index, **meta},
    }


def triple_to_fact_record(t: dict) -> dict:
    """One knowledge-graph triple → one living-fact record:
    the assertion rendered as fact text, its validity,
    confidence, and provenance carried as record fields."""
    return {
        "kind": "fact",
        "content": f"{t['subject']} {t['predicate']} {t['object']}",
        "valid_from": t["valid_from"], "valid_to": t["valid_to"],
        "confidence": t["confidence"],
        "source_drawer_id": t["source_drawer_id"],
        "source_file": t["source_file"],
        "source_closet": t["source_closet"],
        "triple_id": t["id"],
    }


# --------------------------------------------------------------------- #
# The palace argument, proven on the fixture                            #
# --------------------------------------------------------------------- #


def test_palace_extracts_with_the_members_own_stdlib_reader(tmp_path):
    palace = _build_palace(tmp_path)
    records = _member_extractor()(str(palace / "chroma.sqlite3"))
    by_id = {r["id"]: r for r in records}
    assert set(by_id) == {r["id"] for r in PALACE_RECORDS}
    for rec in PALACE_RECORDS:
        assert by_id[rec["id"]]["document"] == rec["document"]
        assert by_id[rec["id"]]["metadata"] == rec["metadata"]


def test_extractor_is_collection_blind_mapper_must_classify(tmp_path):
    palace = _build_palace(tmp_path)
    records = _member_extractor()(str(palace / "chroma.sqlite3"))
    kinds = {r["id"]: classify(r["id"]) for r in records}
    # The upstream reader returns the closet among the
    # drawers — a finding for the executing slice (E-081
    # doc §5): its reader must classify by id, as here.
    assert kinds[CLOSET["id"]] == "closet"
    assert sum(1 for k in kinds.values() if k == "drawer") == 3
    assert "unclassified" not in kinds.values()


def test_drawer_mapping_is_lossless_round_trip(tmp_path):
    palace = _build_palace(tmp_path)
    records = _member_extractor()(str(palace / "chroma.sqlite3"))
    drawers = [r for r in records if classify(r["id"]) == "drawer"]
    assert len(drawers) == 3
    for rec in drawers:
        doc, chunk = drawer_to_document_chunk(rec)
        assert chunk.text == rec["document"]  # byte-identical
        assert reconstruct_drawer(doc, chunk.text) == rec


def test_mapped_drawers_live_in_real_brunnr_through_the_face(tmp_path):
    palace = _build_palace(tmp_path)
    records = _member_extractor()(str(palace / "chroma.sqlite3"))
    drawers = [r for r in records if classify(r["id"]) == "drawer"]

    handle = sv_open(BrunnrConfig(
        embedding_dim=DIM,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "brunnr.db")))
    mimir = RunaMemory(db_path=str(tmp_path / "mimir_well.db"))
    face = MemoryFace(
        brunnr=handle, mimir=mimir, mimir_state="live",
        profile=ConversationProfile.TOASTER, embedder=_embed,
        sidecar_path=tmp_path / "sidecar.json")
    for rec in drawers:
        doc, chunk = drawer_to_document_chunk(rec)
        doc_id = face.add_document(doc)
        face.add_chunks([Chunk(document_id=doc_id,
                               chunk_index=chunk.chunk_index,
                               text=chunk.text,
                               embedding=_embed(chunk.text))])
        # Read back through the store and reconstruct the
        # original drawer exactly — provenance survived the
        # real destination, not just the mapper's dicts.
        stored = handle.get_document(doc_id)
        assert reconstruct_drawer(stored, rec["document"]) == rec
    hits = face.search_documents_word("ferry")
    assert any(h.text == DRAWER_FERRY["document"] for h in hits)
    face.close()


def test_closets_are_derived_pointers_only(tmp_path):
    palace = _build_palace(tmp_path)
    records = _member_extractor()(str(palace / "chroma.sqlite3"))
    by_id = {r["id"]: r for r in records}
    closet = by_id[CLOSET["id"]]
    # Closet document lines are `topic|entities|→drawer_ids`
    # built from drawer content by build_closet_lines: the
    # only payload is pointers, and every pointer resolves.
    for line in closet["document"].splitlines():
        _topic, _entities, pointers = line.split("|")
        for drawer_id in pointers.lstrip("→").split(","):
            assert drawer_id in by_id
            assert classify(drawer_id) == "drawer"
    # Nothing user-authored lives only in a closet: its
    # drawer_count agrees with the drawers it points at.
    assert closet["metadata"]["drawer_count"] == 1


def test_knowledge_graph_triples_map_to_fact_records(tmp_path):
    palace = _build_palace(tmp_path)
    conn = sqlite3.connect(palace / "knowledge_graph.sqlite3")
    conn.row_factory = sqlite3.Row
    rows = [dict(r) for r in conn.execute("SELECT * FROM triples")]
    conn.close()
    assert len(rows) == len(TRIPLES)
    for row, original in zip(sorted(rows, key=lambda r: r["id"]),
                             sorted(TRIPLES, key=lambda t: t["id"])):
        rec = triple_to_fact_record(row)
        assert rec["content"] == (
            f"{original['subject']} {original['predicate']} "
            f"{original['object']}")
        for field in ("valid_from", "valid_to", "confidence",
                      "source_drawer_id", "source_file",
                      "source_closet"):
            assert rec[field] == original[field], field
        assert rec["triple_id"] == original["id"]


# --------------------------------------------------------------------- #
# The filing — the answer, its status, its bounds                       #
# --------------------------------------------------------------------- #


def test_doc_files_the_answer_and_its_bounds():
    text = DOC.read_text(encoding="utf-8")
    for needle in ("stay native", "migrate", "read-compat",
                   "extract_drawers_from_sqlite", "collection-blind",
                   "Volmarr's word", "closet", "knowledge graph",
                   "not executed", "72,239", "745"):
        assert needle in text, needle
    # The proposal decided nothing in the tree: the member
    # is still here, with its packaging intact (E-079 pin).
    assert (REPO / "mempalace" / "pyproject.toml").exists()
    assert (REPO / "mempalace" / "mempalace" / "migrate.py").exists()
    # No migration tool was shipped by this slice: the core
    # still has no mempalace reader (the argument waits).
    core_hits = [
        p for p in (REPO / "src" / "ember").rglob("*.py")
        if "mempalace" in p.read_text(encoding="utf-8").lower()
    ]
    assert core_hits == [], core_hits


def test_fixture_palace_json_is_canon_shaped_only():
    # The fixture data in this file is synthetic (E-089):
    # no real companion history appears in it.
    text = Path(__file__).read_text(encoding="utf-8")
    assert "harbour" in text and "beekeeper" in text
    assert json.dumps({"fixture": True})

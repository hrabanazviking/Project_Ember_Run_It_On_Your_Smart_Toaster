"""E-085 — Memory ↔ Verdandi: the logger's records and
memory's facts reconciled (two views, one lawful crossing).

The stated boundary, pinned here:

* the conversation logger is the truth for what was
  logged; the memory face is the truth for what the
  companion currently remembers; neither store is a copy
  of the other;
* the only crossing is the E-072 feed, received by
  ``MemoryFace.ingest_log_candidates`` — each lawful
  candidate becomes a living fact with its provenance
  (session, category, rule) recorded, a repeat feed is a
  counted duplicate, and an untagged or foreign candidate
  is withheld, never guessed at or re-homed;
* a logger deletion reaches already-fed memory through
  ``retract_deleted_session`` (docket 104): exactly the
  deleted session's fed facts are forgotten, direct facts
  and other sessions are untouched, and
  ``audit_logger_reconciliation`` finds orphans without
  deleting anything. Propagation is explicit, not
  automatic — the logger is a standalone member with no
  hook into the core, and the tests pin the mechanism
  that exists rather than pretending a hook does.

The end-to-end test runs the real Verdandi logger and the
real E-072 feed law into the real face. Synthetic
canon-flavoured data only (E-089's law, early). The
Brunnr half needs the sqlite_vec extra; the whole file
skips honestly without it (the gate's Run D supplies it).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from argparse import Namespace
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-085_MEMORY_VERDANDI_RECONCILIATION.md"

pytest.importorskip("sqlite_vec")

sys.path.insert(0, str(REPO / "mimir-well" / "src"))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


feed = _load("ember_memory_feed_e085", VERDANDI / "memory_feed.py")
logger = _load("ember_conversation_logger_e085",
               VERDANDI / "conversation_logger.py")

from ember.schemas.config import (  # noqa: E402
    BrunnrConfig,
    ConversationProfile,
    SqliteVecConfig,
)
from ember.well.brunnr.sqlite_vec import open as sv_open  # noqa: E402
from ember.well.memory_face import (  # noqa: E402
    DELETE_ALL_CONFIRMATION,
    LOG_FEED_CATEGORIES,
    LOG_FEED_SOURCE,
    MemoryFace,
)
from mimir_well.core import RunaMemory  # noqa: E402

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
SENTINEL = "The harbour ferry carries letters between the islands at dawn."


def _face(tmp_path: Path, **kw) -> MemoryFace:
    handle = sv_open(BrunnrConfig(
        embedding_dim=DIM,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "brunnr.db")))
    mimir = RunaMemory(db_path=str(tmp_path / "mimir_well.db"))
    return MemoryFace(
        brunnr=handle, mimir=mimir, mimir_state="live",
        profile=ConversationProfile.LAPTOP, embedder=embed,
        sidecar_path=tmp_path / "sidecar.json", **kw)


@pytest.fixture()
def face(tmp_path):
    f = _face(tmp_path)
    yield f
    f.close()


def _cand(content=SENTINEL, *, session="sess-a", category="lesson",
          persona="ember", rule_id="user-rule-1", source=LOG_FEED_SOURCE):
    return {
        "memory_feed_version": 1,
        "source": source,
        "session_id": session,
        "timestamp": "2026-11-01T00:00:00+00:00",
        "category": category,
        "content": content,
        "persona_id": persona,
        "provenance": {
            "log_file": "conversation_log.jsonl",
            "entry_type": "event",
            "event_type": "learned",
            "rule_id": rule_id,
        },
    }


# --------------------------------------------------------------------- #
# The boundary's shape                                                   #
# --------------------------------------------------------------------- #

def test_feed_vocabulary_is_the_e072_vocabulary():
    assert LOG_FEED_SOURCE == "conversation_logger"
    assert LOG_FEED_CATEGORIES == frozenset(
        {"lesson", "decision", "milestone", "session_summary"})
    assert feed.CATEGORY_BY_EVENT_TYPE == {
        "learned": "lesson", "decision": "decision",
        "milestone": "milestone"}
    assert feed.END_SUMMARY_CATEGORY == "session_summary"


def test_doc_states_the_boundary_and_docket_104():
    text = DOC.read_text(encoding="utf-8")
    for phrase in ("two views", "docket 104", "not automatic",
                   "retract_deleted_session"):
        assert phrase in text


# --------------------------------------------------------------------- #
# Ingest: the lawful crossing                                            #
# --------------------------------------------------------------------- #

def test_ingest_remembers_the_candidate_as_a_living_fact(face):
    report = face.ingest_log_candidates([_cand()])
    assert report["total"] == 1 and report["ingested"] == 1
    fact_id = report["fact_ids"][0]
    row = face.inspect_fact(fact_id, persona_id="ember")
    assert row is not None and "ferry" in row["content"]
    assert row["category"] == "lesson"
    prov = face.logger_provenance(persona_id="ember")
    assert prov == [{
        "fact_id": fact_id, "session_id": "sess-a",
        "persona": "ember", "category": "lesson",
        "rule_id": "user-rule-1"}]


def test_ingest_report_is_counts_only(face):
    report = face.ingest_log_candidates([_cand()])
    blob = json.dumps(report)
    assert SENTINEL not in blob and "sess-a" not in blob


def test_repeat_feed_is_a_counted_duplicate_not_a_second_fact(face):
    first = face.ingest_log_candidates([_cand()])
    second = face.ingest_log_candidates([_cand()])
    assert first["ingested"] == 1
    assert second["ingested"] == 0 and second["withheld_duplicate"] == 1
    assert len(face.inspect_memory(persona_id="ember")["facts"]) == 1


def test_duplicate_detection_survives_reopen(tmp_path):
    f = _face(tmp_path)
    f.ingest_log_candidates([_cand()])
    f.close()
    reopened = _face(tmp_path)
    try:
        report = reopened.ingest_log_candidates([_cand()])
        assert report["withheld_duplicate"] == 1
        assert len(reopened.logger_provenance(persona_id="ember")) == 1
    finally:
        reopened.close()


@pytest.mark.parametrize("bad", [
    {"source": "somewhere_else"},
    {"category": "action"},
    {"content": "   "},
    {"content": None},
    {"provenance": None},
    {"category": "working_state"},
])
def test_invalid_candidates_are_withheld(face, bad):
    cand = _cand()
    cand.update(bad)
    report = face.ingest_log_candidates([cand, "not-a-dict"])
    assert report["ingested"] == 0 and report["withheld_invalid"] == 2
    assert face.inspect_memory(persona_id="ember")["facts"] == []


@pytest.mark.parametrize("cand", [
    _cand(persona=None),
    _cand(persona="Not A Slug!"),
    _cand(session=""),
    _cand(session=None),
])
def test_unattributable_candidates_are_never_guessed(face, cand):
    report = face.ingest_log_candidates([cand])
    assert report["ingested"] == 0
    assert report["withheld_unattributable"] == 1
    assert face.inspect_memory(persona_id="ember")["facts"] == []


def test_persona_mismatch_is_withheld_not_rehomed(face):
    report = face.ingest_log_candidates(
        [_cand(persona="sage")], persona_id="ember")
    assert report["ingested"] == 0
    assert report["withheld_persona_mismatch"] == 1
    assert face.inspect_memory(persona_id="sage")["facts"] == []


def test_ingest_fails_closed_for_an_invalid_explicit_persona(face):
    report = face.ingest_log_candidates([_cand()], persona_id="")
    assert report["ingested"] == 0 and report["withheld_invalid"] == 1


def test_ingest_when_memory_is_unavailable_counts_blocked(tmp_path):
    f = MemoryFace(brunnr=None, mimir=None,
                   mimir_state="unavailable: test",
                   profile=ConversationProfile.TOASTER,
                   sidecar_path=tmp_path / "sidecar.json")
    report = f.ingest_log_candidates([_cand()])
    assert report["ingested"] == 0 and report["withheld_blocked"] == 1
    assert f.logger_provenance() == []


def test_provenance_is_persona_fenced(face):
    face.ingest_log_candidates([_cand()])
    face.ingest_log_candidates([_cand(
        "The beekeeper keeps nine hives behind the orchard.",
        session="sess-b", persona="sage")])
    assert [r["session_id"] for r in
            face.logger_provenance(persona_id="ember")] == ["sess-a"]
    assert face.logger_provenance(persona_id="") == []


# --------------------------------------------------------------------- #
# Audit: orphans found, nothing deleted                                  #
# --------------------------------------------------------------------- #

def _seed_two_sessions(face):
    face.ingest_log_candidates([_cand()])
    face.ingest_log_candidates([_cand(
        "The beekeeper keeps nine hives behind the orchard.",
        session="sess-b")])


def test_audit_finds_orphans_and_deletes_nothing(face):
    _seed_two_sessions(face)
    audit = face.audit_logger_reconciliation(
        ["sess-a"], persona_id="ember")
    assert audit["tracked"] == 2 and audit["still_logged"] == 1
    assert audit["orphaned"] == 1
    prov = face.logger_provenance(persona_id="ember")
    orphan_id = [r["fact_id"] for r in prov
                 if r["session_id"] == "sess-b"][0]
    assert audit["orphaned_fact_ids"] == [orphan_id]
    # The audit is a report, not a deletion.
    assert face.inspect_fact(orphan_id, persona_id="ember") is not None
    assert "docket 100" in audit["note"]


# --------------------------------------------------------------------- #
# Retraction: docket 104's propagation                                   #
# --------------------------------------------------------------------- #

def test_retract_forgets_exactly_the_deleted_sessions_facts(face):
    _seed_two_sessions(face)
    direct = face.remember_fact(
        "The orchard gate is painted green.", persona_id="ember")
    out = face.retract_deleted_session("sess-a", persona_id="ember")
    assert out["retracted"] == 1 and out["already_gone"] == 0
    remaining = face.inspect_memory(persona_id="ember")["facts"]
    assert sorted(f["id"] for f in remaining) == sorted(
        [direct.fact_id] + [
            r["fact_id"] for r in face.logger_provenance(persona_id="ember")])
    assert [r["session_id"] for r in
            face.logger_provenance(persona_id="ember")] == ["sess-b"]
    assert "docket 104" in out["note"]


def test_retract_drops_the_meaning_index_entry(face):
    report = face.ingest_log_candidates([_cand()])
    fact_id = report["fact_ids"][0]
    hits = face.search_facts_meaning("boat post morning",
                                     persona_id="ember")
    assert [h["id"] for h in hits.facts] == [fact_id]
    face.retract_deleted_session("sess-a")
    assert face.search_facts_meaning(
        "boat post morning", persona_id="ember").facts == ()


def test_retract_is_persona_fenced(face):
    face.ingest_log_candidates([_cand()])
    face.ingest_log_candidates([_cand(
        "The beekeeper keeps nine hives behind the orchard.",
        persona="sage")])
    out = face.retract_deleted_session("sess-a", persona_id="ember")
    assert out["retracted"] == 1
    assert len(face.inspect_memory(persona_id="sage")["facts"]) == 1
    assert len(face.logger_provenance(persona_id="sage")) == 1


def test_retract_counts_a_fact_the_user_already_forgot(face):
    report = face.ingest_log_candidates([_cand()])
    fact_id = report["fact_ids"][0]
    # Forgotten behind the face's back (the member's own
    # delete): the provenance is stale, and retraction
    # counts it already gone and drops the stale row.
    face._mimir.delete_memory(fact_id, user_id="ember")
    out = face.retract_deleted_session("sess-a")
    assert out["retracted"] == 0 and out["already_gone"] == 1
    assert face.logger_provenance() == []


def test_refeed_after_retraction_is_a_fresh_crossing(face):
    first = face.ingest_log_candidates([_cand()])
    face.retract_deleted_session("sess-a")
    second = face.ingest_log_candidates([_cand()])
    assert second["ingested"] == 1
    assert second["fact_ids"] != first["fact_ids"]


def test_refeed_after_user_delete_is_a_fresh_crossing(face):
    first = face.ingest_log_candidates([_cand()])
    face.delete_fact(first["fact_ids"][0], persona_id="ember")
    assert face.logger_provenance() == []
    second = face.ingest_log_candidates([_cand()])
    assert second["ingested"] == 1


def test_delete_all_drops_logger_provenance(face):
    face.ingest_log_candidates([_cand()])
    face.delete_all_memory(persona_id="ember",
                           confirmation=DELETE_ALL_CONFIRMATION)
    assert face.logger_provenance(persona_id="ember") == []
    assert face.ingest_log_candidates([_cand()])["ingested"] == 1


# --------------------------------------------------------------------- #
# End to end: real logger → real feed law → face → logger deletion       #
# --------------------------------------------------------------------- #

@pytest.fixture()
def state(tmp_path, monkeypatch):
    state_dir = tmp_path / "verdandi-state"
    state_dir.mkdir()
    monkeypatch.setattr(logger, "STATE_DIR", state_dir)
    monkeypatch.setattr(logger, "CONV_DIR", state_dir / "conversations")
    monkeypatch.setattr(logger, "CURRENT_FILE", state_dir / "current.json")
    monkeypatch.setattr(logger, "CONV_LOG",
                        state_dir / "conversation_log.jsonl")
    return state_dir


def test_live_logger_feed_ingest_delete_retract(face, state):
    logger.cmd_start(Namespace(session="sess-live", summary="s",
                               model="m", platform="pytest"))
    logger.cmd_event(Namespace(session="sess-live", type="learned",
                               content=SENTINEL))
    logger.cmd_event(Namespace(session="sess-live", type="blocker",
                               content="a blocker is working state"))
    rule = {
        "enabled": True, "granted_by": "user",
        "scope": "named_sessions", "session_ids": ["sess-live"],
        "event_types": ["learned"], "rule_id": "user-rule-live",
    }
    candidates, feed_report = feed.feed_candidates(
        logger._read_all_entries(), rule,
        session_owners={"sess-live": "ember"})
    assert feed_report["fed"] == 1
    report = face.ingest_log_candidates(candidates)
    assert report["ingested"] == 1
    fact_id = report["fact_ids"][0]

    # The user deletes the session in the logger (E-063's
    # right). Memory does NOT change on its own — the
    # boundary is explicit — the audit finds the orphan,
    # and the retraction carries the deletion across.
    logger.delete_session("sess-live")
    assert face.inspect_fact(fact_id, persona_id="ember") is not None
    live_ids = {e["session_id"] for e in logger._read_all_entries()}
    audit = face.audit_logger_reconciliation(live_ids, persona_id="ember")
    assert audit["orphaned_fact_ids"] == [fact_id]
    out = face.retract_deleted_session("sess-live")
    assert out["retracted"] == 1
    assert face.inspect_fact(fact_id, persona_id="ember") is None
    assert face.logger_provenance() == []

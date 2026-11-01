"""E-086 — Memory in WYRD's shapes, at the memory face.

The companion's memory exportable in the shapes the
constellation's world-model work consumes, honouring
ThoughtForge TF-145's boundary (cognition/memory on this
side, the world-model on WYRD's):

* the persona and the companion as WYRD entities (the
  Passive Oracle's ``EntitySummary`` field table);
* facts still believed true as canonical-fact records —
  WYRD's published ``MemoryRecord`` envelope over a
  ``CanonicalFactPayload`` — and grouped in its
  ``FactSummary`` shape under the persona's subject id;
* old versions as the same record shape, superseded,
  with the current record naming what it supersedes;
* remembered turns as utterance observations (WYRD's
  ``ObservationRecord`` shape, Hugin store);
* nothing invented to fill the shapes: the fact key is
  the member's category, confidence is importance
  rescaled, support names a logger session only where
  E-085's provenance recorded one;
* one persona's export never carries another's memory,
  an invalid persona exports nothing, and the bundle
  writes to a file the user can carry.

The field tables pinned here are WYRD's own published
models (``wyrdforge.models.memory`` /
``wyrdforge.oracle.models`` in the WYRD Protocol tree),
copied as tables — Ember's core gains no pydantic and no
WYRD import. Where a real ``wyrdforge`` happens to be
importable, one further test validates the records
against the live models; everywhere else it skips
honestly (the gate's environments do not carry WYRD).

Synthetic canon-flavoured data only (E-089's law, early).
The Brunnr half needs the sqlite_vec extra; the whole
file skips honestly without it (the gate's Run D
supplies it).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-086_MEMORY_WYRD_EXPORT.md"

pytest.importorskip("sqlite_vec")

sys.path.insert(0, str(REPO / "mimir-well" / "src"))

from ember.schemas.config import (  # noqa: E402
    BrunnrConfig,
    ConversationProfile,
    SqliteVecConfig,
)
from ember.schemas.episode import Episode  # noqa: E402
from ember.well.brunnr.sqlite_vec import open as sv_open  # noqa: E402
from ember.well.memory_face import (  # noqa: E402
    DELETE_ALL_CONFIRMATION,
    WYRD_COMPANION_ENTITY_ID,
    WYRD_EXPORT_KIND,
    WYRD_RECORD_SCHEMA_VERSION,
    WYRD_STORE_HUGIN,
    WYRD_STORE_MIMIR,
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

# WYRD's published field tables (its StrictModels forbid
# extra fields, so an export carrying one more key is not
# consumable — the tables are pinned exactly).
ENVELOPE_KEYS = {
    "record_id", "store", "record_type", "schema_version",
    "tenant_id", "system_id", "entity_scope", "content",
    "truth", "provenance", "lifecycle", "retrieval",
    "governance", "audit",
}
ENTITY_SCOPE_KEYS = {
    "primary_subjects", "secondary_subjects", "scene_id",
    "session_id", "world_id", "project_id",
}
CONTENT_KEYS = {"title", "summary", "body_ref", "structured_payload"}
FACT_PAYLOAD_KEYS = {
    "fact_subject_id", "fact_key", "fact_value", "value_type",
    "domain", "support_record_ids", "supersedes_record_id",
}
OBS_PAYLOAD_KEYS = {
    "observation_kind", "raw_excerpt", "normalized_claims",
    "participants", "observed_at", "place_id", "salience",
    "candidate_memory_write",
}
TRUTH_KEYS = {"support_class", "confidence", "confidence_history",
              "contradiction_status", "approval_state"}
PROVENANCE_KEYS = {"source_type", "source_ref", "source_hash",
                   "extracted_at", "extracted_by"}
LIFECYCLE_KEYS = {"write_policy", "retention_class", "decay_curve",
                  "expires_at", "last_accessed_at", "access_count",
                  "stale_after_days"}
RETRIEVAL_KEYS = {"embedding_id", "lexical_terms", "facets",
                  "default_priority"}
GOVERNANCE_KEYS = {"sensitivity", "memory_poison_risk",
                   "allowed_for_runtime", "allowed_for_training",
                   "requires_review_before_promotion"}
AUDIT_KEYS = {"created_at", "updated_at", "created_by_agent",
              "updated_by_agent"}
ENTITY_KEYS = {"entity_id", "name", "description", "status",
               "tags", "location_id"}
FACT_SUMMARY_KEYS = {"record_id", "subject_id", "fact_key",
                     "fact_value", "confidence", "domain",
                     "uncertain", "confidence_history"}


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


def _seed(f: MemoryFace):
    ember = f.remember_fact(
        "The beekeeper keeps nine hives behind the orchard.",
        category="household", importance=8, persona_id="ember")
    sage = f.remember_fact(
        "The harbour ferry carries letters between the islands at dawn.",
        category="lesson", importance=5, persona_id="sage")
    f.add_turn(Episode(operator_input="When is the ferry?",
                       ember_reply="At dawn.", persona_id="ember"))
    f.add_turn(Episode(operator_input="Tell me about honey.",
                       ember_reply="Sweet, from the hives.",
                       persona_id="sage"))
    return ember, sage


# --------------------------------------------------------------------- #
# The boundary                                                           #
# --------------------------------------------------------------------- #

def test_constants_are_wyrds_own_names():
    assert WYRD_EXPORT_KIND == "ember memory export (wyrd shapes)"
    assert WYRD_RECORD_SCHEMA_VERSION == "1.0.0"
    assert WYRD_STORE_MIMIR == "mimir_canonical_store"
    assert WYRD_STORE_HUGIN == "hugin_observation_store"
    assert WYRD_COMPANION_ENTITY_ID == "ember-companion"


def test_bundle_states_the_tf145_boundary(face):
    _seed(face)
    bundle = face.export_wyrd(persona_id="ember")
    assert bundle["kind"] == WYRD_EXPORT_KIND
    assert "TF-145" in bundle["boundary"]["this_side_owns"]
    assert bundle["boundary"]["wyrd_owns"] == "the world-model"
    assert "no world model" in bundle["boundary"]["this_export"]
    assert "WYRD" in bundle["note"]


def test_doc_states_the_boundary():
    text = DOC.read_text(encoding="utf-8")
    assert "TF-145" in text
    assert "world-model" in text


# --------------------------------------------------------------------- #
# Entities                                                               #
# --------------------------------------------------------------------- #

def test_entities_are_wyrd_shaped(face):
    _seed(face)
    bundle = face.export_wyrd(persona_id="ember")
    assert bundle["subject_id"] == "ember-persona:ember"
    entities = {e["entity_id"]: e for e in bundle["entities"]}
    assert set(entities) == {"ember-persona:ember",
                             WYRD_COMPANION_ENTITY_ID}
    for entity in entities.values():
        assert set(entity) == ENTITY_KEYS
    assert entities["ember-persona:ember"]["name"] == "ember"
    assert entities["ember-persona:ember"]["tags"] == ["ember-persona"]


# --------------------------------------------------------------------- #
# Canonical facts                                                        #
# --------------------------------------------------------------------- #

def test_current_fact_is_a_canonical_fact_record(face):
    ember, _sage = _seed(face)
    bundle = face.export_wyrd(persona_id="ember")
    facts = [r for r in bundle["records"]
             if r["record_type"] == "canonical_fact"]
    assert len(facts) == 1
    rec = facts[0]
    assert set(rec) == ENVELOPE_KEYS
    assert rec["record_id"] == f"ember-fact:{ember.fact_id}"
    assert rec["store"] == WYRD_STORE_MIMIR
    assert rec["schema_version"] == "1.0.0"
    assert rec["tenant_id"] == "ember"
    assert rec["system_id"] == "ember-agent"
    assert set(rec["entity_scope"]) == ENTITY_SCOPE_KEYS
    assert rec["entity_scope"]["primary_subjects"] == ["ember-persona:ember"]
    assert set(rec["content"]) == CONTENT_KEYS
    payload = rec["content"]["structured_payload"]
    assert set(payload) == FACT_PAYLOAD_KEYS
    assert payload["fact_subject_id"] == "ember-persona:ember"
    assert payload["fact_key"] == "household"
    assert "nine hives" in payload["fact_value"]
    assert payload["support_record_ids"] == []
    assert payload["supersedes_record_id"] is None
    assert set(rec["truth"]) == TRUTH_KEYS
    # importance 8 on the member's 1-10 scale, rescaled.
    assert rec["truth"]["confidence"] == 0.8
    assert set(rec["provenance"]) == PROVENANCE_KEYS
    assert rec["provenance"]["source_ref"] == (
        f"mimir-well memory {ember.fact_id}")
    assert set(rec["lifecycle"]) == LIFECYCLE_KEYS
    assert rec["lifecycle"]["write_policy"] == "promotable"
    assert set(rec["retrieval"]) == RETRIEVAL_KEYS
    assert set(rec["governance"]) == GOVERNANCE_KEYS
    assert rec["governance"]["allowed_for_training"] is False
    assert set(rec["audit"]) == AUDIT_KEYS


def test_canonical_facts_grouped_in_fact_summary_shape(face):
    ember, _sage = _seed(face)
    bundle = face.export_wyrd(persona_id="ember")
    grouped = bundle["canonical_facts"]
    assert list(grouped) == ["ember-persona:ember"]
    (summary,) = grouped["ember-persona:ember"]
    assert set(summary) == FACT_SUMMARY_KEYS
    assert summary["record_id"] == f"ember-fact:{ember.fact_id}"
    assert summary["subject_id"] == "ember-persona:ember"
    assert summary["fact_key"] == "household"
    assert summary["confidence"] == 0.8
    assert summary["uncertain"] is False


def test_superseded_fact_is_marked_and_named(face):
    first = face.remember_fact("The ferry leaves at dawn.",
                               persona_id="ember")
    second = face.supersede_fact(
        first.fact_id, "The ferry leaves at winter dawn.",
        persona_id="ember")
    bundle = face.export_wyrd(persona_id="ember")
    by_id = {r["record_id"]: r for r in bundle["records"]
             if r["record_type"] == "canonical_fact"}
    assert set(by_id) == {f"ember-fact:{first.fact_id}",
                          f"ember-fact:{second.fact_id}"}
    old = by_id[f"ember-fact:{first.fact_id}"]
    new = by_id[f"ember-fact:{second.fact_id}"]
    assert old["lifecycle"]["write_policy"] == "ephemeral"
    assert old["retrieval"]["facets"]["current"] == ["false"]
    assert new["content"]["structured_payload"][
        "supersedes_record_id"] == f"ember-fact:{first.fact_id}"
    # Only the current fact is offered as canonical.
    grouped = bundle["canonical_facts"]["ember-persona:ember"]
    assert [g["record_id"] for g in grouped] == [
        f"ember-fact:{second.fact_id}"]
    assert bundle["counts"]["superseded_facts"] == 1


def test_logger_fed_fact_names_its_support(face):
    face.ingest_log_candidates([{
        "memory_feed_version": 1,
        "source": "conversation_logger",
        "session_id": "sess-a",
        "timestamp": "2026-11-01T00:00:00+00:00",
        "category": "lesson",
        "content": "The harbour ferry carries letters at dawn.",
        "persona_id": "ember",
        "provenance": {"log_file": "conversation_log.jsonl",
                       "entry_type": "event",
                       "event_type": "learned",
                       "rule_id": "user-rule-1"},
    }])
    bundle = face.export_wyrd(persona_id="ember")
    (rec,) = [r for r in bundle["records"]
              if r["record_type"] == "canonical_fact"]
    payload = rec["content"]["structured_payload"]
    assert payload["support_record_ids"] == ["ember-log-session:sess-a"]
    assert rec["entity_scope"]["session_id"] == "sess-a"


def test_direct_fact_invents_no_support(face):
    face.remember_fact("The orchard gate sticks in winter.",
                       persona_id="ember")
    bundle = face.export_wyrd(persona_id="ember")
    (rec,) = bundle["records"]
    assert rec["content"]["structured_payload"][
        "support_record_ids"] == []
    assert rec["entity_scope"]["session_id"] is None


# --------------------------------------------------------------------- #
# Turns as observations                                                  #
# --------------------------------------------------------------------- #

def test_turns_are_utterance_observations(face):
    _seed(face)
    bundle = face.export_wyrd(persona_id="ember")
    obs = [r for r in bundle["records"]
           if r["record_type"] == "observation"]
    assert len(obs) == 1
    rec = obs[0]
    assert set(rec) == ENVELOPE_KEYS
    assert rec["store"] == WYRD_STORE_HUGIN
    payload = rec["content"]["structured_payload"]
    assert set(payload) == OBS_PAYLOAD_KEYS
    assert payload["observation_kind"] == "utterance"
    assert payload["raw_excerpt"] == "When is the ferry?"
    assert payload["participants"] == [
        "ember-persona:ember", WYRD_COMPANION_ENTITY_ID]
    assert payload["candidate_memory_write"] is False
    assert bundle["counts"]["observations"] == 1
    # A turn whose own time was recorded keeps it; only a
    # timeless turn is stamped at export, and counted.
    stamped = bundle["counts"]["turns_time_stamped_at_export"]
    assert stamped == (1 if payload["observed_at"]
                       == bundle["exported_at"] else 0)


# --------------------------------------------------------------------- #
# Persona law, refusals, and the carried file                            #
# --------------------------------------------------------------------- #

def test_export_never_carries_another_personas_memory(face):
    _ember, sage = _seed(face)
    bundle = face.export_wyrd(persona_id="ember")
    blob = json.dumps(bundle)
    assert "harbour ferry carries letters" not in blob
    assert f"ember-fact:{sage.fact_id}" not in blob
    assert "Tell me about honey" not in blob
    assert bundle["counts"]["records"] == 2  # 1 fact + 1 turn


def test_invalid_persona_exports_nothing(face):
    _seed(face)
    bundle = face.export_wyrd(persona_id="not a slug!")
    assert bundle["persona"] is None
    assert bundle["entities"] == []
    assert bundle["canonical_facts"] == {}
    assert bundle["records"] == []
    assert "refused" in bundle["note"]


def test_export_writes_a_file_you_can_carry(face, tmp_path):
    _seed(face)
    target = tmp_path / "wyrd" / "memory.json"
    bundle = face.export_wyrd(persona_id="ember", path=target)
    assert bundle["written_to"] == str(target)
    on_disk = json.loads(target.read_text(encoding="utf-8"))
    assert on_disk["kind"] == WYRD_EXPORT_KIND
    assert on_disk["counts"] == bundle["counts"]
    assert not target.with_suffix(".json.tmp").exists()


def test_counts_add_up(face):
    _seed(face)
    bundle = face.export_wyrd(persona_id="sage")
    counts = bundle["counts"]
    assert counts["canonical_facts"] == 1
    assert counts["observations"] == 1
    assert counts["records"] == len(bundle["records"]) == 2
    assert counts["entities"] == 2


# --------------------------------------------------------------------- #
# The gate-found delete defect, fixed in this slice                      #
#                                                                        #
# E-085's owed Run D re-verification (this slice's first duty) caught    #
# E-084's test_delete_all_is_total_for_one_persona dying on the         #
# member's superseded_by foreign key under load: _all_facts comes back   #
# in importance/timestamp order, so a total delete can meet the new      #
# fact while its old version still points at it. Same-second fixtures    #
# hid it (insertion order saved it); staggered times expose it.          #
# --------------------------------------------------------------------- #

def test_delete_all_survives_staggered_supersede_times(face, tmp_path):
    import sqlite3
    first = face.remember_fact("The ferry leaves at dawn.",
                               persona_id="ember")
    face.supersede_fact(first.fact_id,
                        "The ferry leaves at winter dawn.",
                        persona_id="ember")
    # Stagger the fixture's own store so the NEW fact
    # sorts first in the member's search order — the
    # exact ordering that killed the total delete.
    conn = sqlite3.connect(tmp_path / "mimir_well.db")
    conn.execute("UPDATE memories SET timestamp = "
                 "'2999-01-01 00:00:00' WHERE is_current = 1")
    conn.commit()
    conn.close()
    out = face.delete_all_memory(
        persona_id="ember", confirmation=DELETE_ALL_CONFIRMATION)
    assert out["deleted"] is True
    assert out["facts_deleted"] == 2
    seen = face.inspect_memory(persona_id="ember")
    assert seen["facts"] == [] and seen["old_facts"] == []


def test_delete_fact_forgets_its_lineage(face):
    first = face.remember_fact("The ferry leaves at dawn.",
                               persona_id="ember")
    second = face.supersede_fact(first.fact_id,
                                 "The ferry leaves at winter dawn.",
                                 persona_id="ember")
    out = face.delete_fact(second.fact_id, persona_id="ember")
    assert out["deleted"] is True
    assert out["old_versions_deleted"] == 1
    seen = face.inspect_memory(persona_id="ember")
    assert seen["facts"] == [] and seen["old_facts"] == []


def test_delete_fact_without_lineage_is_unchanged(face):
    only = face.remember_fact("The orchard gate sticks in winter.",
                              persona_id="ember")
    out = face.delete_fact(only.fact_id, persona_id="ember")
    assert out["deleted"] is True
    assert out["old_versions_deleted"] == 0


# --------------------------------------------------------------------- #
# The live WYRD models, where they can be present                        #
# --------------------------------------------------------------------- #

def test_records_validate_against_live_wyrd_models(face):
    wyrd_memory = pytest.importorskip("wyrdforge.models.memory")
    wyrd_oracle = pytest.importorskip("wyrdforge.oracle.models")
    _seed(face)
    bundle = face.export_wyrd(persona_id="ember")
    for rec in bundle["records"]:
        if rec["record_type"] == "canonical_fact":
            wyrd_memory.CanonicalFactRecord.model_validate(rec)
        elif rec["record_type"] == "observation":
            wyrd_memory.ObservationRecord.model_validate(rec)
    for entity in bundle["entities"]:
        wyrd_oracle.EntitySummary.model_validate(entity)
    for summaries in bundle["canonical_facts"].values():
        for summary in summaries:
            wyrd_oracle.FactSummary.model_validate(summary)

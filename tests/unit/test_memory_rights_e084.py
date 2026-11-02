"""E-084 — The user's memory rights at the memory face.

Inspect, correct, export, and delete-total as working,
plain-worded operations on ``src/ember/well/memory_face.py``:

* inspect shows a persona exactly its own memory — facts
  still believed true, old versions kept as history, and
  remembered turns — and nothing of anyone else's;
* correct fixes a fact in place (same id, new words),
  refuses another persona's fact and empty words, and
  re-indexes so meaning search serves the corrected words;
* export is one plain bundle, the persona's own memory
  only, and writes a real JSON file the user can carry;
* delete_fact forgets one fact for real (row gone,
  meaning entry dropped) and refuses another's;
* delete_all_memory is total for one persona — facts
  (current and old versions), index entries, and turns —
  is guarded by the exact confirmation words, touches no
  other persona, and its turn tombstones survive a reopen.
  Its one honest limit is pinned, not hidden: a forgotten
  turn's physical bytes stay in Brunnr because the handle
  has no delete (docket 119) — the report says 0 bytes
  reclaimed and the turn is unreachable everywhere.

Synthetic canon-flavoured data only (E-089's law, early).
The Brunnr half needs the sqlite_vec extra; the whole file
skips honestly without it (the gate's Run D supplies it).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-084_USER_MEMORY_RIGHTS.md"

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
        persona_id="ember")
    sage = f.remember_fact(
        "The harbour ferry carries letters between the islands at dawn.",
        persona_id="sage")
    f.add_turn(Episode(operator_input="When is the ferry?",
                       ember_reply="At dawn.", persona_id="ember"))
    f.add_turn(Episode(operator_input="Tell me about honey.",
                       ember_reply="Sweet, from the hives.",
                       persona_id="sage"))
    return ember, sage


# --------------------------------------------------------------------- #
# Inspect                                                                #
# --------------------------------------------------------------------- #

def test_inspect_shows_only_your_own_memory(face):
    ember, _sage = _seed(face)
    seen = face.inspect_memory(persona_id="ember")
    assert seen["persona"] == "ember"
    assert [f["id"] for f in seen["facts"]] == [ember.fact_id]
    assert "orchard" in seen["facts"][0]["content"]
    assert len(seen["turns"]) == 1
    assert seen["turns"][0].operator_input == "When is the ferry?"
    assert "1 fact(s) still believed true" in seen["note"]


def test_inspect_separates_current_from_old_versions(face):
    first = face.remember_fact("The ferry leaves at dawn.",
                               persona_id="ember")
    face.supersede_fact(first.fact_id, "The ferry leaves at winter dawn.",
                        persona_id="ember")
    seen = face.inspect_memory(persona_id="ember")
    assert len(seen["facts"]) == 1
    assert "winter dawn" in seen["facts"][0]["content"]
    assert len(seen["old_facts"]) == 1
    assert seen["old_facts"][0]["id"] == first.fact_id


def test_inspect_fact_is_owner_only(face):
    ember, sage = _seed(face)
    assert face.inspect_fact(ember.fact_id, persona_id="ember") is not None
    assert face.inspect_fact(ember.fact_id, persona_id="sage") is None
    assert face.inspect_fact(sage.fact_id, persona_id="ember") is None


def test_inspect_invalid_persona_sees_nothing(face):
    _seed(face)
    seen = face.inspect_memory(persona_id="")
    assert seen["persona"] is None and seen["facts"] == []


# --------------------------------------------------------------------- #
# Correct                                                                #
# --------------------------------------------------------------------- #

def test_correct_fixes_the_same_fact_in_place(face):
    ember, _ = _seed(face)
    result = face.correct_fact(
        ember.fact_id, "The beekeeper keeps twelve hives by the harbour.",
        persona_id="ember")
    assert result.fact_id == ember.fact_id
    fixed = face.inspect_fact(ember.fact_id, persona_id="ember")
    assert "twelve hives" in fixed["content"]


def test_correct_reindexes_for_meaning_search(face):
    ember, _ = _seed(face)
    face.correct_fact(ember.fact_id,
                      "The harbour ferry carries letters at dawn.",
                      persona_id="ember")
    hits = face.search_facts_meaning("boat post morning",
                                     persona_id="ember")
    assert hits.mode == "meaning"
    assert [h["id"] for h in hits.facts] == [ember.fact_id]
    assert "ferry" in hits.facts[0]["content"]


def test_correct_refuses_another_personas_fact(face):
    ember, _ = _seed(face)
    result = face.correct_fact(ember.fact_id, "Sage was here.",
                               persona_id="sage")
    assert result.fact_id is None
    assert "not this persona's" in result.note
    assert "nine hives" in face.inspect_fact(
        ember.fact_id, persona_id="ember")["content"]


def test_correct_refuses_empty_words(face):
    ember, _ = _seed(face)
    result = face.correct_fact(ember.fact_id, "  ", persona_id="ember")
    assert result.fact_id is None and "empty" in result.note


# --------------------------------------------------------------------- #
# Export                                                                 #
# --------------------------------------------------------------------- #

def test_export_is_your_memory_only(face):
    _seed(face)
    bundle = face.export_memory(persona_id="sage")
    assert bundle["counts"] == {"facts": 1, "old_facts": 0, "turns": 1}
    assert "ferry" in bundle["facts"][0]["content"]
    assert bundle["turns"][0]["you_said"] == "Tell me about honey."
    assert "beekeeper" not in json.dumps(bundle)


def test_export_writes_a_file_you_can_carry(face, tmp_path):
    _seed(face)
    target = tmp_path / "carry" / "my-memory.json"
    bundle = face.export_memory(persona_id="ember", path=target)
    assert bundle["written_to"] == str(target)
    on_disk = json.loads(target.read_text(encoding="utf-8"))
    assert on_disk["persona"] == "ember"
    assert on_disk["counts"]["facts"] == 1


# --------------------------------------------------------------------- #
# Delete one                                                             #
# --------------------------------------------------------------------- #

def test_delete_fact_forgets_it_for_real(face):
    ember, _ = _seed(face)
    out = face.delete_fact(ember.fact_id, persona_id="ember")
    assert out["deleted"] is True
    assert face.inspect_fact(ember.fact_id, persona_id="ember") is None
    hits = face.search_facts_meaning("bees sweet", persona_id="ember")
    assert hits.facts == ()


def test_delete_fact_refuses_another_personas(face):
    ember, _ = _seed(face)
    out = face.delete_fact(ember.fact_id, persona_id="sage")
    assert out["deleted"] is False
    assert face.inspect_fact(ember.fact_id, persona_id="ember") is not None


# --------------------------------------------------------------------- #
# Delete everything                                                      #
# --------------------------------------------------------------------- #

def test_delete_all_needs_the_exact_words(face):
    _seed(face)
    for words in ("", "delete", "delete everything!", "DELETE EVERYTHING"):
        out = face.delete_all_memory(persona_id="ember", confirmation=words)
        assert out["deleted"] is False
    assert len(face.inspect_memory(persona_id="ember")["facts"]) == 1


def test_delete_all_is_total_for_one_persona(face):
    ember, sage = _seed(face)
    face.supersede_fact(ember.fact_id, "The beekeeper retired.",
                        persona_id="ember")
    out = face.delete_all_memory(persona_id="ember",
                                 confirmation=DELETE_ALL_CONFIRMATION)
    assert out["deleted"] is True
    assert out["facts_deleted"] == 2  # current + the old version
    assert out["turns_forgotten"] == 1
    # The honest limit, stated not hidden (docket 119).
    assert out["turn_physical_bytes_reclaimed"] == 0
    assert "docket 119" in out["note"]
    seen = face.inspect_memory(persona_id="ember")
    assert seen["facts"] == [] and seen["old_facts"] == []
    assert seen["turns"] == []
    assert face.recent_turns(persona_id="ember") == []
    assert face.export_memory(persona_id="ember")["counts"] == {
        "facts": 0, "old_facts": 0, "turns": 0}
    # No one else was touched.
    sage_seen = face.inspect_memory(persona_id="sage")
    assert len(sage_seen["facts"]) == 1 and len(sage_seen["turns"]) == 1
    assert face.inspect_fact(sage.fact_id, persona_id="sage") is not None


def test_delete_all_tombstones_survive_reopen(tmp_path):
    f = _face(tmp_path, default_persona_id="ember")
    f.remember_fact("The ferry leaves at dawn.", persona_id="ember")
    f.add_turn(Episode(operator_input="hi", ember_reply="hello",
                       persona_id="ember"))
    f.delete_all_memory(persona_id="ember",
                        confirmation=DELETE_ALL_CONFIRMATION)
    f.close()
    reopened = _face(tmp_path, default_persona_id="ember")
    try:
        # A forgotten turn must not resurrect as an untagged
        # default-persona turn after a restart.
        assert reopened.recent_turns(persona_id="ember") == []
        assert reopened.inspect_memory(persona_id="ember")["turns"] == []
    finally:
        reopened.close()


def test_rights_fail_closed_when_memory_is_unavailable(tmp_path):
    f = MemoryFace(brunnr=None, mimir=None,
                   mimir_state="unavailable: test",
                   profile=ConversationProfile.TOASTER,
                   sidecar_path=tmp_path / "sidecar.json")
    assert f.inspect_fact(1) is None
    assert f.correct_fact(1, "words").fact_id is None
    assert f.delete_fact(1)["deleted"] is False
    assert f.delete_all_memory(
        confirmation=DELETE_ALL_CONFIRMATION)["deleted"] is False


def test_doc_exists_and_names_the_four_rights():
    text = DOC.read_text(encoding="utf-8")
    for word in ("inspect", "correct", "export", "delete"):
        assert word in text.lower()

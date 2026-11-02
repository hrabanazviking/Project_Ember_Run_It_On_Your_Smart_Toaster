"""E-080 — The chosen shape implemented: one memory contract.

Proves docs/architecture/E-080_ONE_MEMORY_CONTRACT.md and
``src/ember/well/memory_face.py``:

* the face serves living facts through mimir-well (word,
  importance, mood, current truth) under the asking
  persona's namespace only;
* the face serves documents and turns through Brunnr, and
  persona separation for turns is the face's own tag
  (docket 110): untagged episodes belong to the default
  persona only, fail-closed for everyone else;
* index-don't-merge: on an indexing profile a reworded
  (paraphrase) question finds a living fact through the
  Brunnr index, and a superseded fact is never served as
  current even though its index chunk remains;
* budgets bind the face: the toaster profile ships word
  search over living facts and says so (mode == "word",
  indexed is False with the profile named in the note);
* docket 51: the canonical mimir path is the library
  default, named once, in the face;
* an unavailable engine degrades honestly, never raises.

Synthetic canon-flavoured data only (E-089's law, early).
The Brunnr half needs the sqlite_vec extra; the whole file
skips honestly without it (the gate's Run D supplies it).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-080_ONE_MEMORY_CONTRACT.md"

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
from ember.well.memory_face import (  # noqa: E402
    CANONICAL_MIMIR_DB_PATH,
    FACT_INDEX_SOURCE,
    MemoryFace,
    index_default_for,
)
from mimir_well.core import RunaMemory  # noqa: E402

# A tiny deterministic stand-in embedder: a bag of words over
# a fixed vocabulary, with synonym folding (boat->ferry,
# post->letters, isles->islands, morning->dawn) doing the
# job a real embedder's semantics would do — reworded text
# lands near the original without sharing its words.
_VOCAB = [
    "ferry", "letters", "islands", "dawn", "harbour",
    "beekeeper", "honey", "hives", "orchard", "winter",
    "market", "teaches", "song", "children", "river",
]
_SYNONYMS = {
    "boat": "ferry", "post": "letters", "isles": "islands",
    "morning": "dawn", "bees": "beekeeper", "sweet": "honey",
    "sings": "song", "kids": "children",
}


def embed(text: str) -> tuple[float, ...]:
    words = [
        _SYNONYMS.get(w.strip(".,?!").lower(), w.strip(".,?!").lower())
        for w in text.split()
    ]
    return tuple(float(words.count(v)) for v in _VOCAB)


DIM = len(_VOCAB)

FERRY = ("The harbour ferry leaves at dawn carrying letters "
         "between the islands.")
FERRY_PARAPHRASE = "When does the boat carry post between the isles?"
BEES = ("The beekeeper keeps nine hives behind the orchard and "
        "trades honey at the winter market.")


def _face(tmp_path: Path, profile: ConversationProfile, **kw) -> MemoryFace:
    handle = sv_open(BrunnrConfig(
        embedding_dim=DIM,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "brunnr.db")))
    mimir = RunaMemory(db_path=str(tmp_path / "mimir_well.db"))
    return MemoryFace(
        brunnr=handle, mimir=mimir, mimir_state="live",
        profile=profile, embedder=embed,
        sidecar_path=tmp_path / "sidecar.json", **kw)


@pytest.fixture()
def laptop(tmp_path):
    face = _face(tmp_path, ConversationProfile.LAPTOP)
    yield face
    face.close()


@pytest.fixture()
def toaster(tmp_path):
    face = _face(tmp_path, ConversationProfile.TOASTER)
    yield face
    face.close()


# --------------------------------------------------------------------- #
# Docket 51 — one canonical path                                          #
# --------------------------------------------------------------------- #


def test_canonical_mimir_path_is_the_library_default():
    assert CANONICAL_MIMIR_DB_PATH == (
        Path.home() / ".mimir_well" / "mimir_well.db")
    # The library's own default (no db_path, no config file
    # consulted here — the constant in its config module).
    src = (REPO / "mimir-well" / "src" / "mimir_well" / "core.py")
    assert "~/.mimir_well/mimir_well.db" in src.read_text(encoding="utf-8")


def test_index_defaults_follow_the_budget_verdict():
    assert index_default_for(ConversationProfile.TOASTER) is False
    for profile in (ConversationProfile.PHONE, ConversationProfile.PI,
                    ConversationProfile.LAPTOP):
        assert index_default_for(profile) is True


# --------------------------------------------------------------------- #
# Living facts through the face                                           #
# --------------------------------------------------------------------- #


def test_fact_word_importance_mood_and_persona_isolation(laptop):
    bees = laptop.remember_fact(BEES, category="preference", importance=9,
                                emotional_valence=0.8, persona_id="ember")
    assert bees.fact_id and bees.fact_id > 0

    word = laptop.recall_facts_word("beekeeper", persona_id="ember")
    assert [r["content"] for r in word] == [BEES]
    # Another persona sees none of it — any face path.
    assert laptop.recall_facts_word("beekeeper", persona_id="other") == []
    assert laptop.recall_by_importance(min_importance=7,
                                       persona_id="other") == []
    assert laptop.recall_by_mood(0.8, persona_id="other") == []

    imp = laptop.recall_by_importance(min_importance=9, persona_id="ember")
    assert [r["content"] for r in imp] == [BEES]
    mood = laptop.recall_by_mood(0.8, tolerance=0.3, persona_id="ember")
    assert [r["content"] for r in mood] == [BEES]
    current = laptop.recall_current(persona_id="ember")
    assert BEES in [r["content"] for r in current]


# --------------------------------------------------------------------- #
# Index, don't merge                                                      #
# --------------------------------------------------------------------- #


def test_meaning_search_finds_fact_by_paraphrase(laptop):
    res = laptop.remember_fact(FERRY, category="knowledge", importance=6,
                               persona_id="ember")
    assert res.indexed is True, res.note
    hits = laptop.search_facts_meaning(FERRY_PARAPHRASE, persona_id="ember")
    assert hits.mode == "meaning"
    assert [r["content"] for r in hits.facts] == [FERRY]
    # The index is Brunnr-side bookkeeping: the fact itself
    # lives only in mimir-well (stores not merged) — the
    # index document is the face's one synthetic document.
    stats = laptop._brunnr.count()
    assert stats.documents == 1
    doc = laptop._brunnr.get_document(
        laptop._sidecar.index_document_id)
    assert doc.source == FACT_INDEX_SOURCE


def test_superseded_fact_never_served_as_current(laptop):
    old = laptop.remember_fact(FERRY, category="knowledge", importance=6,
                               persona_id="ember")
    assert old.indexed is True
    new_text = ("The harbour ferry leaves at dawn carrying letters "
                "between the islands, weather permitting.")
    new = laptop.supersede_fact(old.fact_id, new_text, persona_id="ember")
    assert new.fact_id and new.fact_id != old.fact_id

    hits = laptop.search_facts_meaning(FERRY_PARAPHRASE, persona_id="ember")
    contents = [r["content"] for r in hits.facts]
    assert new_text in contents
    assert FERRY not in contents  # the stale index chunk resolves away
    current = laptop.recall_current(persona_id="ember")
    assert FERRY not in [r["content"] for r in current]


def test_toaster_ships_word_search_and_says_so(toaster):
    res = toaster.remember_fact(FERRY, category="knowledge", importance=6,
                                persona_id="ember")
    assert res.fact_id and res.fact_id > 0
    assert res.indexed is False
    assert "toaster" in res.note

    hits = toaster.search_facts_meaning("ferry", persona_id="ember")
    assert hits.mode == "word"
    assert [r["content"] for r in hits.facts] == [FERRY]
    state = toaster.state()
    assert state["index_facts"] is False
    assert state["profile"] == "toaster"


# --------------------------------------------------------------------- #
# Documents & turns through the face                                      #
# --------------------------------------------------------------------- #


def test_documents_pass_through_to_brunnr(laptop, tmp_path):
    doc_id = laptop.add_document(Document(
        source="canon/test", title="Harbour notes",
        content_type="text", hash="e080-doc"))
    ids = laptop.add_chunks([Chunk(
        document_id=doc_id, chunk_index=0,
        text="The harbour ferry bell rings twice at dawn.",
        embedding=embed("harbour ferry dawn"))])
    assert len(ids) == 1
    hits = laptop.search_documents_word("ferry bell")
    assert hits and "ferry bell" in hits[0].text


def test_turns_are_persona_separated_at_the_face(laptop):
    a = laptop.add_turn(Episode(operator_input="one", ember_reply="first",
                                persona_id="ember"))
    b = laptop.add_turn(Episode(operator_input="two", ember_reply="second",
                                persona_id="other"))
    assert a and b and a != b
    mine = laptop.recent_turns(persona_id="ember")
    assert [e.ember_reply for e in mine] == ["first"]
    theirs = laptop.recent_turns(persona_id="other")
    assert [e.ember_reply for e in theirs] == ["second"]


def test_untagged_turn_belongs_to_default_persona_only(laptop):
    # Written straight to Brunnr, outside the face (the
    # pre-face shape): the adapter persists no persona tag.
    laptop._brunnr.add_episode(Episode(operator_input="old",
                                       ember_reply="legacy"))
    assert [e.ember_reply for e in
            laptop.recent_turns(persona_id="default")] == ["legacy"]
    assert laptop.recent_turns(persona_id="ember") == []


# --------------------------------------------------------------------- #
# Honest degradation                                                      #
# --------------------------------------------------------------------- #


def test_unavailable_mimir_degrades_honestly(tmp_path):
    handle = sv_open(BrunnrConfig(
        embedding_dim=DIM,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "brunnr.db")))
    face = MemoryFace(brunnr=handle, mimir=None,
                      mimir_state="unavailable: test double",
                      profile=ConversationProfile.LAPTOP, embedder=embed,
                      sidecar_path=tmp_path / "sidecar.json")
    res = face.remember_fact(FERRY, persona_id="ember")
    assert res.fact_id is None
    assert "unavailable" in res.note
    assert face.recall_facts_word("ferry", persona_id="ember") == []
    assert face.state()["mimir_well"] == "unavailable: test double"
    face.close()


# --------------------------------------------------------------------- #
# The filing                                                              #
# --------------------------------------------------------------------- #


def test_doc_delivers_the_contract_and_conditions():
    text = DOC.read_text(encoding="utf-8")
    for needle in ("one memory contract", "CANONICAL_MIMIR_DB_PATH",
                   "index, don't merge", "docket 51", "docket 109",
                   "docket 110", "72,239", "toaster", "Volmarr's word"):
        assert needle in text, needle

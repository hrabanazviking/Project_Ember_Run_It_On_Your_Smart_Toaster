"""E-082 — Memory lifecycle: growth, decay, pruning.

Proves docs/architecture/E-082_MEMORY_LIFECYCLE.md and the
lifecycle surface of ``src/ember/well/memory_face.py``:

* the growth report prices facts (745 B, E-078), turns'
  anchor, and the fact index (72,239 B/fact, E-078)
  against the profile's Part III ceiling (E-050/E-041);
* decay is mimir-well's own, delegated per persona;
* pruning drops a superseded fact's index pointer,
  reports physical bytes reclaimed as 0 (docket 112 —
  Brunnr's handle has no delete), and meaning search
  keeps serving the current fact;
* run_lifecycle composes decay + prune + report;
* an unavailable engine degrades honestly.

Synthetic canon-flavoured data only (E-089's law, early).
Skips honestly without the sqlite_vec extra (Run D
supplies it), like the E-080 file it builds on.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-082_MEMORY_LIFECYCLE.md"

pytest.importorskip("sqlite_vec")

sys.path.insert(0, str(REPO / "mimir-well" / "src"))

from ember.budgets import budget_for  # noqa: E402
from ember.schemas.config import (  # noqa: E402
    BrunnrConfig,
    ConversationProfile,
    SqliteVecConfig,
)
from ember.well.brunnr.sqlite_vec import open as sv_open  # noqa: E402
from ember.well.memory_face import (  # noqa: E402
    EPISODE_BYTES_PER_TURN,
    FACT_BYTES_PER_FACT,
    INDEX_BYTES_PER_FACT,
    MemoryFace,
)
from mimir_well.core import RunaMemory  # noqa: E402

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


# --------------------------------------------------------------------- #
# Growth accounting                                                       #
# --------------------------------------------------------------------- #


def test_anchors_are_the_measured_ones():
    assert FACT_BYTES_PER_FACT == 745  # E-078
    assert EPISODE_BYTES_PER_TURN == 585  # E-050 steady marginal / E-078
    assert INDEX_BYTES_PER_FACT == 72_239  # E-078


def test_report_prices_facts_and_index_against_ceiling(laptop):
    laptop.remember_fact(FERRY, importance=6, persona_id="ember")
    laptop.remember_fact(BEES, importance=9, persona_id="ember")
    report = laptop.lifecycle_report()
    assert report.profile == "laptop"
    assert report.ceiling_bytes_per_month == int(
        budget_for(ConversationProfile.LAPTOP).storage_growth_mib_per_month
        * 1024 * 1024)
    assert report.facts_stored == 2
    assert report.facts_bytes == 2 * FACT_BYTES_PER_FACT
    assert report.indexed_facts == 2
    assert report.index_bytes == 2 * INDEX_BYTES_PER_FACT
    assert report.index_fits_ceiling is True
    assert report.brunnr_size_bytes > 0


def test_toaster_ceiling_in_indexed_facts_matches_e080_pricing(tmp_path):
    face = _face(tmp_path, ConversationProfile.TOASTER)
    report = face.lifecycle_report()
    # E-080 doc §5: the toaster's 2 MiB ceiling buys ~29 indexed facts.
    assert 29 <= report.index_months_of_headroom < 30
    face.close()


# --------------------------------------------------------------------- #
# Decay — the member's own, per persona                                   #
# --------------------------------------------------------------------- #


def test_decay_delegates_and_is_persona_scoped(laptop):
    laptop.remember_fact(FERRY, importance=6, persona_id="ember")
    laptop.remember_fact(BEES, importance=9, persona_id="other")
    result = laptop.run_decay(persona_id="ember")
    assert set(result) >= {"decayed", "pruned", "reinforced"}
    # The other persona's fact keeps its importance: decay
    # ran under ember's namespace only.
    other = laptop.recall_by_importance(min_importance=9,
                                        persona_id="other")
    assert [r["content"] for r in other] == [BEES]


# --------------------------------------------------------------------- #
# Pruning — stale index pointers, honest bytes                            #
# --------------------------------------------------------------------- #


def test_prune_drops_superseded_pointer_and_reports_zero_bytes(laptop):
    old = laptop.remember_fact(FERRY, importance=6, persona_id="ember")
    new_text = ("The harbour ferry leaves at dawn carrying letters "
                "between the islands, weather permitting.")
    laptop.supersede_fact(old.fact_id, new_text, persona_id="ember")
    assert laptop.lifecycle_report().indexed_facts == 2

    result = laptop.prune_stale_index()
    assert result["pruned_index_entries"] == 1
    assert result["index_bytes_logically_reclaimed"] == INDEX_BYTES_PER_FACT
    # Docket 112: no handle delete exists — never claim bytes back.
    assert result["physical_bytes_reclaimed"] == 0
    assert "112" in result["note"]
    assert laptop.lifecycle_report().indexed_facts == 1

    hits = laptop.search_facts_meaning(FERRY_PARAPHRASE,
                                       persona_id="ember")
    assert hits.mode == "meaning"
    assert [r["content"] for r in hits.facts] == [new_text]


def test_prune_with_nothing_stale_is_a_no_op(laptop):
    laptop.remember_fact(FERRY, importance=6, persona_id="ember")
    result = laptop.prune_stale_index()
    assert result["pruned_index_entries"] == 0
    assert laptop.lifecycle_report().indexed_facts == 1


# --------------------------------------------------------------------- #
# Composition + honest degradation                                        #
# --------------------------------------------------------------------- #


def test_run_lifecycle_composes_decay_prune_report(laptop):
    old = laptop.remember_fact(FERRY, importance=6, persona_id="ember")
    laptop.supersede_fact(old.fact_id, FERRY + " Weather permitting.",
                          persona_id="ember")
    out = laptop.run_lifecycle(persona_id="ember")
    assert out["prune"]["pruned_index_entries"] == 1
    assert out["report"].indexed_facts == 1
    assert set(out["decay"]) >= {"decayed", "pruned", "reinforced"}


def test_lifecycle_degrades_honestly_without_mimir(tmp_path):
    handle = sv_open(BrunnrConfig(
        embedding_dim=DIM,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "brunnr.db")))
    face = MemoryFace(brunnr=handle, mimir=None,
                      mimir_state="unavailable: test double",
                      profile=ConversationProfile.LAPTOP, embedder=embed,
                      sidecar_path=tmp_path / "sidecar.json")
    report = face.lifecycle_report()
    assert report.facts_stored == 0
    decay = face.run_decay(persona_id="ember")
    assert decay["decayed"] == 0 and "unavailable" in decay["note"]
    face.close()


def test_doc_delivers_lifecycle_and_its_limits():
    text = DOC.read_text(encoding="utf-8")
    for needle in ("memory lifecycle", "72,239", "745", "E-050",
                   "docket 112", "docket 113", "physical"):
        assert needle.lower() in text.lower(), needle

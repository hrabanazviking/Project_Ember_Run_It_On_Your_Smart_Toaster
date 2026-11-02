"""E-112 — Seiðr in conversation.

Pins ``docs/architecture/E-112_SEIDR_IN_CONVERSATION.md``
and, behind it, ``src/ember/seidr_conversation.py`` at
this tree:

* the record itself: what the engine offers a chat
  (a verse offer and a seeded draw, both as data) under
  the honesty rule — the engine computes; meaning is
  the companion's voice, labelled;
* the verse offer: composed through the E-110 service
  untouched (a refusal propagates verbatim, a seeded
  offer is reproducible), the caller's theme carried
  as a label only (docket 144), and Old Norse glosses
  served as lexicon data with coverage counted;
* the draw: seeded and re-drawable, words distinct and
  the lexicon's own entries, an unchosen world picked
  by the seed and reported, a world holding no kenning
  stated as holding none, and the refusals (no seed,
  unknown world, bad count) in words;
* the reading: the companion's text carried verbatim
  under its own label, never merged into the computed
  data, and the context block honest in its own text;
* docket 144's member fate: ``PoemConfig`` carries no
  ``include_old_norse`` field and ``Poem.format`` no
  such parameter (both removed — they promised a
  rendering nothing produced), while ``topic`` stands
  as the label it always was.
"""

from __future__ import annotations

import ast
import dataclasses
import inspect
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-112_SEIDR_IN_CONVERSATION.md"

sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "seidr_engine"))

from ember import engines  # noqa: E402
from ember.seidr_conversation import (  # noqa: E402
    COMPUTED_SOURCE,
    HONESTY_LINE,
    MEANING_SOURCE,
    attach_reading,
    context_text,
    draw_words,
    offer_verse,
)
from seidr.lexicon import Lexicon  # noqa: E402
from seidr.poet import Poem, PoemConfig  # noqa: E402


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


# ── The record, on file ─────────────────────────────────


def test_doc_records_the_conversation_verdict():
    text = _flat(DOC)
    for needle in ("engine computes", "companion's voice, labelled",
                   "Docket 144", "Next: E-113"):
        assert needle in text, needle


def test_doc_names_what_was_not_built():
    text = _flat(DOC)
    for needle in ("E-117", "NOT PROVEN"):
        assert needle in text, needle


def test_module_imports_only_stdlib_and_the_core():
    tree = ast.parse(
        (REPO / "src/ember/seidr_conversation.py").read_text(encoding="utf-8"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= set(sys.stdlib_module_names) | {"ember", "__future__"}


# ── The verse offer ─────────────────────────────────────


def test_verse_offer_is_the_services_verse_carried():
    offered = offer_verse(form="ljodhattr", seed=42)
    assert offered.reason is None
    served = engines.compose_verse(
        engines.VerseRequest(form="ljodhattr", seed=42))
    assert offered.offer.lines == served.verse.lines
    assert offered.offer.text == served.verse.text
    assert offered.offer.world == served.verse.world
    assert offered.offer.source == COMPUTED_SOURCE
    again = offer_verse(form="ljodhattr", seed=42)
    assert again.offer.lines == offered.offer.lines  # seeded: reproducible


def test_verse_offer_refusal_propagates_verbatim():
    bad_world = offer_verse(world="nosuchworld", seed=42)
    assert bad_world.offer is None
    assert "unknown world" in bad_world.reason
    bad_form = offer_verse(form="nope")
    assert bad_form.offer is None and "Unknown poetic form" in bad_form.reason


def test_theme_is_a_label_only_and_shapes_nothing():
    plain = offer_verse(seed=7, world="asgard")
    themed = offer_verse(seed=7, world="asgard", theme="sea-voyage")
    assert themed.offer.theme == "sea-voyage"
    assert themed.offer.lines == plain.offer.lines
    assert themed.offer.text == plain.offer.text


def test_verse_glosses_are_lexicon_data_with_counted_coverage():
    offered = offer_verse(seed=7, world="asgard", with_old_norse=True)
    assert offered.reason is None
    offer = offered.offer
    assert offer.glossed == len(offer.glosses) > 0
    assert offer.glossed <= offer.words_seen
    lexicon = Lexicon()
    forms = {}
    for entry in lexicon.get_words():
        if entry.old_norse:
            forms.setdefault(entry.word.lower(), set()).add(entry.old_norse)
    verse_words = {w.lower() for line in offer.lines for w in line.split()}
    for word, old_norse in offer.glosses:
        assert word.lower() in verse_words  # the verse's own words
        assert old_norse in forms[word.lower()]  # the lexicon's own forms
    bare = offer_verse(seed=7, world="asgard")
    assert bare.offer.glosses == () and bare.offer.glossed == 0


# ── The draw ────────────────────────────────────────────


def test_draw_is_seeded_distinct_and_the_lexicons_own():
    first = draw_words(seed=42, world="asgard")
    second = draw_words(seed=42, world="asgard")
    assert first.reason is None and first.draw == second.draw  # re-drawable
    draw = first.draw
    assert draw.world == "asgard" and draw.source == COMPUTED_SOURCE
    assert len(draw.words) == 3
    assert len({w.word.lower() for w in draw.words}) == 3  # distinct
    lexicon = Lexicon()
    entries = {(e.word, e.domain, e.part_of_speech): e.old_norse
               for e in lexicon.get_words(domain="asgard")}
    for word in draw.words:
        key = (word.word, word.world, word.part_of_speech)
        assert key in entries and entries[key] == word.old_norse
    assert draw.kenning is not None
    assert draw.kenning.world == "asgard"
    assert draw.kenning.expression == "Kvasir's blood"  # seed 42, probed


def test_draw_unchosen_world_is_picked_by_the_seed_and_reported():
    draw = draw_words(seed=42)
    assert draw.reason is None
    assert draw.draw.world in {
        "asgard", "vanaheim", "alfheim", "midgard", "jotunheim",
        "svartalfheim", "niflheim", "muspelheim", "helheim"}
    assert all(w.world == draw.draw.world for w in draw.draw.words)
    assert draw_words(seed=42).draw == draw.draw


def test_draw_world_without_kennings_states_the_absence():
    draw = draw_words(seed=42, world="helheim")
    assert draw.reason is None and draw.draw.kenning is None
    assert "holds none" in context_text(draw.draw)


def test_draw_refusals_are_in_words():
    unseeded = draw_words(seed=None)
    assert unseeded.draw is None and "needs a seed" in unseeded.reason
    bad_world = draw_words(seed=1, world="nosuchworld")
    assert bad_world.draw is None and "asgard" in bad_world.reason
    bad_count = draw_words(seed=1, count=10)
    assert bad_count.draw is None and "1 to 9" in bad_count.reason


def test_missing_member_refuses_in_words(tmp_path):
    offered = offer_verse(member_dir=tmp_path)
    assert offered.offer is None and "not found" in offered.reason
    drawn = draw_words(seed=1, member_dir=tmp_path)
    assert drawn.draw is None and "not found" in drawn.reason


# ── The reading, and the context block ──────────────────


def test_reading_is_labelled_and_never_merged():
    offered = offer_verse(form="ljodhattr", seed=42)
    reading = attach_reading(offered.offer, "For the road, nothing more.")
    assert reading.reading_source == MEANING_SOURCE
    assert reading.computed.source == COMPUTED_SOURCE
    assert reading.reading == "For the road, nothing more."
    assert reading.computed.lines == offered.offer.lines  # data untouched
    with pytest.raises(ValueError):
        attach_reading(offered.offer, "   ")


def test_context_block_is_honest_in_its_own_text():
    offered = offer_verse(form="ljodhattr", seed=42)
    block = context_text(offered.offer)
    assert "computed by the engine" in block
    assert HONESTY_LINE in block
    assert "the engine offers none" in block  # no reading spoken
    for line in offered.offer.lines:
        assert line in block
    with_reading = context_text(
        attach_reading(offered.offer, "For the road, nothing more."))
    assert with_reading.count("For the road, nothing more.") == 1
    assert with_reading.index("For the road") > with_reading.index(HONESTY_LINE)
    assert "companion's reading, in its own voice" in with_reading


def test_context_block_for_a_draw_names_its_data():
    draw = draw_words(seed=42, world="asgard", theme="voyage")
    block = context_text(draw.draw)
    assert "Draw (world: asgard, seed: 42" in block
    assert "Asked under the label: voyage" in block
    for word in draw.draw.words:
        assert word.word in block


# ── Docket 144: the member-side fate ────────────────────


def test_docket_144_dead_old_norse_shapes_are_removed():
    fields = {f.name for f in dataclasses.fields(PoemConfig)}
    assert "include_old_norse" not in fields  # dead in composition, removed
    assert "include_old_norse" not in inspect.signature(Poem.format).parameters
    assert "topic" in fields  # the label stands, corrected to what it is

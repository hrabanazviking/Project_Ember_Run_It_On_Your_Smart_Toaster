"""E-090 — Docs: the memory model for users (plain) + builders.

Pins docs/architecture/E-090_MEMORY_MODEL.md against the
code it describes, ``src/ember/well/memory_face.py``:

* the plain-language part for users stands before the
  builder part, and both are present in substance;
* every public operation on ``MemoryFace`` is named in
  the document — the list is derived from the class
  itself, so an operation added without a doc row fails
  this gate until the model document catches up;
* the constants, measured prices, profile rules, and
  confirmation words the document states match the
  module that owns them;
* the honest limits are stated, not hidden: docket 119
  (turn bytes), docket 120 (audit hashes), docket 112
  (index bytes), docket 113 (decay vocabulary), docket
  125 (decay compounding), docket 108 (owed at E-092);
* the mempalace retirement is stated as proposed, never
  as decided, and the chat-not-yet-rewired truth is
  stated in the builder part.
"""

from __future__ import annotations

import inspect
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-090_MEMORY_MODEL.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_doc_exists_plain_part_before_builder_part():
    text = _text()
    plain = text.index("Part A — For users, in plain words")
    builders = text.index("Part B — For builders")
    assert plain < builders
    # The plain part carries the user's whole story.
    for needle in ("Living facts", "Conversation turns",
                   "Documents", "the four rights",
                   "delete everything", "Different people",
                   "How memory ages"):
        assert needle in text, needle


def test_every_public_face_operation_is_documented():
    from ember.well.memory_face import MemoryFace

    public = sorted(
        name for name, _ in inspect.getmembers(MemoryFace)
        if not name.startswith("_")
        and (inspect.isfunction(getattr(MemoryFace, name, None))
             or isinstance(inspect.getattr_static(MemoryFace, name),
                           (classmethod, staticmethod)))
    )
    # The surface this slice documents (E-080..E-086 built it).
    assert len(public) >= 29, public
    text = _text()
    missing = [name for name in public if f"`{name}(" not in text
               and f"`{name}(...)" not in text]
    assert not missing, f"undocumented operations: {missing}"


def test_constants_and_prices_match_the_module():
    from ember.well import memory_face as mf

    text = _text()
    assert mf.FACT_BYTES_PER_FACT == 745 and "745" in text
    assert mf.EPISODE_BYTES_PER_TURN == 585 and "585" in text
    assert mf.INDEX_BYTES_PER_FACT == 72_239 and "72,239" in text
    assert mf.DELETE_ALL_CONFIRMATION == "delete everything"
    assert '"delete everything"' in text
    assert mf.FACT_INDEX_SOURCE == "ember-memory-face/fact-index"
    assert "ember-memory-face/fact-index" in text
    assert mf.LOG_FEED_SOURCE == "conversation_logger"
    assert "conversation_logger" in text
    assert str(mf.CANONICAL_MIMIR_DB_PATH).endswith(
        ".mimir_well/mimir_well.db")
    assert "~/.mimir_well/mimir_well.db" in text
    # Index defaults: toaster off, the other three on.
    from ember.schemas.config import ConversationProfile

    assert mf.index_default_for(ConversationProfile.TOASTER) is False
    for profile in (ConversationProfile.PHONE, ConversationProfile.PI,
                    ConversationProfile.LAPTOP):
        assert mf.index_default_for(profile) is True
    for needle in ("2 MiB", "10 MiB", "25 MiB", "100 MiB"):
        assert needle in text, needle


def test_measured_life_figures_are_the_recorded_ones():
    text = _text()
    # E-050 reference month, E-088 simulated year.
    for needle in ("0.39 MiB", "7,300", "5,717,556"):
        assert needle in text, needle


def test_honest_limits_are_stated_not_hidden():
    text = _text()
    for needle in ("docket 119", "docket 120", "docket 112",
                   "docket 113", "docket 125", "docket 108",
                   "physically reclaimed", "hashes", "floored"):
        assert needle in text, needle


def test_mempalace_status_is_proposed_not_decided():
    text = _text()
    for needle in ("mempalace", "proposed", "Volmarr's",
                   "has not been given", "untouched"):
        assert needle in text, needle
    # The member still stands in the tree, unretired.
    assert (REPO / "mempalace" / "pyproject.toml").exists()


def test_builder_truths_are_stated():
    text = _text()
    for needle in ("Chat is not rewired yet",
                   "only through `RunaMemory`",
                   "not a third store",
                   "Index, don't merge",
                   "TF-145", "E-091", "E-092"):
        assert needle in text, needle

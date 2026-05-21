"""Shape and invariant tests for Smiðja's chunker."""

from __future__ import annotations

from ember.schemas.config import BoundaryPreference, ChunkerConfig
from ember.well.smidja.chunker import chunk


def test_short_text_yields_one_chunk() -> None:
    chunks = list(chunk("Hello, world."))
    assert len(chunks) == 1
    assert chunks[0].text == "Hello, world."
    assert chunks[0].char_start == 0
    assert chunks[0].char_end == len("Hello, world.")


def test_empty_text_yields_no_chunks() -> None:
    assert list(chunk("")) == []


def test_paragraph_boundary_preferred() -> None:
    cfg = ChunkerConfig(max_chars=120, target_chars=100, min_chars=10)
    text = (
        "First paragraph about Odin. He is wise.\n\n"
        "Second paragraph about Thor. He is strong.\n\n"
        "Third paragraph about Freyja. She is beautiful."
    )
    chunks = list(chunk(text, config=cfg))
    assert len(chunks) >= 2
    for c in chunks:
        assert len(c.text) <= cfg.max_chars


def test_max_chars_is_a_hard_ceiling_for_normal_text() -> None:
    cfg = ChunkerConfig(max_chars=200, target_chars=150, min_chars=20)
    paragraphs = [f"Paragraph {i}: " + "x" * 50 for i in range(10)]
    text = "\n\n".join(paragraphs)
    chunks = list(chunk(text, config=cfg))
    for c in chunks:
        assert len(c.text) <= cfg.max_chars, (
            f"chunk {c.chunk_index} length {len(c.text)} > max {cfg.max_chars}"
        )


def test_oversize_paragraph_falls_back_to_sentence_split() -> None:
    cfg = ChunkerConfig(max_chars=100, target_chars=80, min_chars=20)
    big = (
        "Sentence one is short. "
        "Sentence two is also short. "
        "Sentence three is short. "
        "Sentence four is short. "
        "Sentence five is short."
    )
    chunks = list(chunk(big, config=cfg))
    assert len(chunks) >= 2
    for c in chunks:
        assert len(c.text) <= cfg.max_chars


def test_pure_overlong_blob_falls_through_to_char_split() -> None:
    cfg = ChunkerConfig(max_chars=50, target_chars=40, min_chars=5)
    blob = "x" * 250  # one long run; no paragraph/sentence/word breaks
    chunks = list(chunk(blob, config=cfg))
    assert len(chunks) == 5
    for c in chunks:
        assert len(c.text) <= cfg.max_chars
        assert c.text == "x" * len(c.text)


def test_chunks_are_numbered_consecutively() -> None:
    text = "Para A.\n\nPara B.\n\nPara C."
    chunks = list(chunk(text, config=ChunkerConfig(max_chars=20, target_chars=15, min_chars=5)))
    indices = [c.chunk_index for c in chunks]
    assert indices == list(range(len(indices)))


def test_gungnir_aligned_defaults_match_expected_values() -> None:
    cfg = ChunkerConfig()
    assert cfg.max_chars == 2000
    assert cfg.target_chars == 1684
    assert cfg.min_chars == 200
    assert cfg.boundary_preference is BoundaryPreference.PARAGRAPH


def test_char_boundary_yields_one_chunk_per_char_under_max() -> None:
    cfg = ChunkerConfig(
        max_chars=5,
        target_chars=3,
        min_chars=1,
        boundary_preference=BoundaryPreference.CHAR,
    )
    chunks = list(chunk("abcdefghij", config=cfg))
    # With max=5, single chars pack into chunks of up to 5; never exceeds.
    for c in chunks:
        assert len(c.text) <= cfg.max_chars
    # Round-trip total chars (some get joined with separators).
    joined = "".join(c.text for c in chunks).replace("\n\n", "")
    assert set(joined) == set("abcdefghij")

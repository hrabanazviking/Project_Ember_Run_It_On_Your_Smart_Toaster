"""Shape contracts for ``ember.schemas.chunks``."""

from __future__ import annotations

import dataclasses

import pytest

from ember.schemas.chunks import BrunnrStats, Chunk, Document, RetrievalHit

# --------------------------------------------------------------------- #
# Document                                                               #
# --------------------------------------------------------------------- #


def test_document_minimal_construction() -> None:
    d = Document(
        source="/notes/x.md",
        title="x",
        content_type="md",
        hash="abc123",
    )
    assert d.id is None
    assert d.ingested_at is None
    assert d.metadata == {}


def test_document_is_frozen() -> None:
    d = Document(source="/x", title=None, content_type=None, hash="h")
    with pytest.raises(dataclasses.FrozenInstanceError):
        d.title = "renamed"  # type: ignore[misc]


def test_document_accepts_metadata() -> None:
    d = Document(
        source="/x",
        title=None,
        content_type=None,
        hash="h",
        metadata={"tag": "norse"},
    )
    assert d.metadata["tag"] == "norse"


# --------------------------------------------------------------------- #
# Chunk                                                                  #
# --------------------------------------------------------------------- #


def test_chunk_minimal_construction() -> None:
    c = Chunk(document_id=1, chunk_index=0, text="hello")
    assert c.embedding is None
    assert c.id is None


def test_chunk_embedding_is_tuple_so_chunk_can_be_frozen() -> None:
    # tuple chosen over list precisely because frozen dataclass with
    # mutable field is a soft lie — see chunks.py module docstring.
    c = Chunk(
        document_id=1,
        chunk_index=0,
        text="x",
        embedding=(0.1, 0.2, 0.3),
    )
    assert isinstance(c.embedding, tuple)


def test_chunk_is_frozen() -> None:
    c = Chunk(document_id=1, chunk_index=0, text="x")
    with pytest.raises(dataclasses.FrozenInstanceError):
        c.text = "tampered"  # type: ignore[misc]


# --------------------------------------------------------------------- #
# RetrievalHit                                                           #
# --------------------------------------------------------------------- #


def test_retrieval_hit_carries_score_and_back_reference() -> None:
    hit = RetrievalHit(
        chunk_id=42,
        document_id=7,
        document_title="The Saga of Runa",
        text="lo",
        score=0.87,
    )
    assert hit.score == pytest.approx(0.87)
    assert hit.document_title == "The Saga of Runa"


# --------------------------------------------------------------------- #
# BrunnrStats                                                            #
# --------------------------------------------------------------------- #


def test_brunnr_stats_carries_four_counts() -> None:
    s = BrunnrStats(
        documents=95,
        chunks=35682,
        embedded_chunks=35682,
        size_bytes=394 * 1024 * 1024,
    )
    assert s.documents == 95
    assert s.embedded_chunks == s.chunks

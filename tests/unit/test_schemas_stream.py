"""Shape contracts for ``ember.schemas.stream.FuniStreamChunk``."""

from __future__ import annotations

import dataclasses

import pytest

from ember.schemas.funi import FinishReason
from ember.schemas.stream import FuniStreamChunk


def test_minimal_construction_only_requires_text_delta_and_done() -> None:
    chunk = FuniStreamChunk(text_delta="hi", done=False)
    assert chunk.text_delta == "hi"
    assert chunk.done is False
    assert chunk.finish_reason is None
    assert chunk.prompt_tokens is None
    assert chunk.completion_tokens is None


def test_is_frozen() -> None:
    chunk = FuniStreamChunk(text_delta="x", done=True, finish_reason=FinishReason.STOP)
    with pytest.raises(dataclasses.FrozenInstanceError):
        chunk.text_delta = "tampered"  # type: ignore[misc]


def test_final_chunk_carries_finish_reason_and_totals() -> None:
    chunk = FuniStreamChunk(
        text_delta="",
        done=True,
        finish_reason=FinishReason.STOP,
        model_id="phi3:mini",
        prompt_tokens=15,
        completion_tokens=120,
    )
    assert chunk.done is True
    assert chunk.finish_reason is FinishReason.STOP
    assert chunk.prompt_tokens == 15
    assert chunk.completion_tokens == 120


def test_join_text_deltas_reconstructs_full_reply() -> None:
    """The canonical way callers reconstruct the full reply text."""
    chunks = [
        FuniStreamChunk(text_delta="Hello ", done=False),
        FuniStreamChunk(text_delta="world", done=False),
        FuniStreamChunk(text_delta="!", done=True, finish_reason=FinishReason.STOP),
    ]
    full = "".join(c.text_delta for c in chunks)
    assert full == "Hello world!"

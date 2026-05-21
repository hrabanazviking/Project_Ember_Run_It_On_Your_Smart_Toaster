"""Streaming reply schemas.

Per ADR 0009. A streaming Funi reply is a sequence of
:class:`FuniStreamChunk` instances. The last one carries
``done=True`` and the totals; everything before it carries
incremental ``text_delta`` only.

Mid-stream failure produces a single final chunk with
``done=True, finish_reason=FinishReason.ERROR`` and an
operator-readable message in ``text_delta`` — same shape as the
slice-1 :class:`FuniReply` failure-folding pattern.
"""

from __future__ import annotations

from dataclasses import dataclass

from ember.schemas.funi import FinishReason


@dataclass(frozen=True, slots=True)
class FuniStreamChunk:
    """One streamed token batch from Funi.

    ``text_delta`` is the *new* text since the previous chunk — never
    cumulative. The complete reply is ``"".join(c.text_delta for c in chunks)``.

    ``finish_reason`` / ``prompt_tokens`` / ``completion_tokens``
    populate on the final chunk only (``done=True``). Earlier chunks
    leave them ``None`` / ``0``.
    """

    text_delta: str
    done: bool
    finish_reason: FinishReason | None = None
    model_id: str = ""
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


__all__ = ["FuniStreamChunk"]

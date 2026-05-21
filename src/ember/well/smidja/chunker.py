"""Paragraph-aware chunker — Gungnir-aligned defaults.

Per ``docs/adapters/SMIDJA_INGEST_PATTERNS.md`` §3: chunks target an
average of ~1684 chars (Gungnir's measured average) with a 2000-char
hard ceiling and a 200-char floor. Boundary preference is paragraph,
then sentence, then word, then char.

The chunker yields :class:`ember.schemas.chunks.Chunk` instances whose
``text`` is sliced directly out of the input string via
``char_start``/``char_end`` — original whitespace is preserved exactly.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator

from ember.schemas.chunks import Chunk
from ember.schemas.config import BoundaryPreference, ChunkerConfig

_PARA_SPLIT = re.compile(r"\n\s*\n+")
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'`])")
_WORD_SPLIT = re.compile(r"\s+")


def chunk(text: str, *, config: ChunkerConfig | None = None) -> Iterator[Chunk]:
    """Yield :class:`Chunk` objects covering ``text``.

    Each chunk's ``text`` is exactly ``text[chunk.char_start:chunk.char_end]``
    — original whitespace preserved. ``document_id`` is 0 and
    ``embedding`` is None; the caller (typically Smiðja's source
    orchestrator) fills both in.
    """
    cfg = config or ChunkerConfig()
    if not text:
        return
    spans = list(_segment_spans(text, cfg))
    packed = _pack_spans(spans, text, cfg)
    for idx, (start, end) in enumerate(packed):
        yield Chunk(
            document_id=0,
            chunk_index=idx,
            text=text[start:end],
            embedding=None,
            char_start=start,
            char_end=end,
        )


# --------------------------------------------------------------------- #
# Internals                                                              #
# --------------------------------------------------------------------- #


def _segment_spans(text: str, cfg: ChunkerConfig) -> Iterator[tuple[int, int]]:
    """Yield (start, end) tuples at the configured boundary granularity."""
    boundary = cfg.boundary_preference
    if boundary is BoundaryPreference.PARAGRAPH:
        yield from _spans_by_regex(text, _PARA_SPLIT)
    elif boundary is BoundaryPreference.SENTENCE:
        yield from _spans_by_regex(text, _SENT_SPLIT)
    elif boundary is BoundaryPreference.WORD:
        yield from _spans_by_regex(text, _WORD_SPLIT)
    else:  # CHAR
        for i in range(len(text)):
            yield (i, i + 1)


def _spans_by_regex(
    text: str, pattern: re.Pattern[str]
) -> Iterator[tuple[int, int]]:
    cursor = 0
    for match in pattern.finditer(text):
        if match.start() > cursor:
            yield (cursor, match.start())
        cursor = match.end()
    if cursor < len(text):
        yield (cursor, len(text))


def _pack_spans(
    spans: Iterable[tuple[int, int]],
    text: str,
    cfg: ChunkerConfig,
) -> list[tuple[int, int]]:
    """Greedy-pack (start, end) spans into chunks under cfg.max_chars.

    Combined chunk length is computed as ``end - start`` of the
    accumulated range — original whitespace between segments is
    counted exactly, so chunks never silently exceed ``max_chars``.

    If a single span exceeds ``max_chars``, split at the next finer
    granularity. If the *final* packed chunk is shorter than
    ``min_chars``, merge it backward into its predecessor when the
    merged length stays within ``max_chars + min_chars``.
    """
    packed: list[tuple[int, int]] = []
    cur_start: int | None = None
    cur_end: int | None = None

    for span_start, span_end in spans:
        span_len = span_end - span_start

        if span_len > cfg.max_chars:
            if cur_start is not None and cur_end is not None:
                packed.append((cur_start, cur_end))
                cur_start = None
                cur_end = None
            for sub in _split_oversize_span(span_start, span_end, text, cfg):
                packed.append(sub)
            continue

        if cur_start is None:
            cur_start = span_start
            cur_end = span_end
            continue

        candidate_len = span_end - cur_start
        if candidate_len > cfg.max_chars:
            assert cur_end is not None
            packed.append((cur_start, cur_end))
            cur_start = span_start
            cur_end = span_end
        else:
            cur_end = span_end

    if cur_start is not None and cur_end is not None:
        packed.append((cur_start, cur_end))

    if (
        len(packed) >= 2
        and (packed[-1][1] - packed[-1][0]) < cfg.min_chars
    ):
        prev_start, _ = packed[-2]
        _, last_end = packed[-1]
        if last_end - prev_start <= cfg.max_chars + cfg.min_chars:
            packed[-2:] = [(prev_start, last_end)]

    return packed


def _split_oversize_span(
    start: int,
    end: int,
    text: str,
    cfg: ChunkerConfig,
) -> Iterator[tuple[int, int]]:
    """Split a single oversize span at progressively finer granularities."""
    body = text[start:end]
    for finer in (_SENT_SPLIT, _WORD_SPLIT):
        sub_spans = list(_spans_by_regex(body, finer))
        if not sub_spans:
            continue
        max_sub = max(s_end - s_start for s_start, s_end in sub_spans)
        if max_sub <= cfg.max_chars:
            adjusted = [(start + s, start + e) for s, e in sub_spans]
            yield from _pack_spans(adjusted, text, cfg)
            return

    cursor = 0
    while cursor < (end - start):
        chunk_end = min(cursor + cfg.max_chars, end - start)
        yield (start + cursor, start + chunk_end)
        cursor = chunk_end


__all__ = ["chunk"]

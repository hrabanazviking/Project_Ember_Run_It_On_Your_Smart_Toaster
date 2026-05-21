"""Document, Chunk, RetrievalHit, and BrunnrStats data types.

The shape of what flows between Smiðja, Brunnr, and Spark — and the
shape of what comes back from Brunnr's search and stats calls.

Per ``docs/architecture/DOMAIN_MAP.md`` §1 and §2.1, and aligned with the
Gungnir schema captured in ``docs/adapters/GUNGNIR_WELL_REFERENCE.md``
§3. Where Gungnir uses ``vector(768)``, we represent it as an immutable
``tuple[float, ...]`` so :class:`Chunk` can be a frozen dataclass.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Document:
    """One ingested source — file, URL, dataset entry.

    Gungnir column mapping: id, source, title, content_type, hash,
    metadata jsonb, ingested_at. ``id`` is None before Brunnr assigns it.
    """

    source: str
    title: str | None
    content_type: str | None
    hash: str
    metadata: Mapping[str, object] = field(default_factory=dict)
    ingested_at: datetime | None = None
    id: int | None = None


@dataclass(frozen=True, slots=True)
class Chunk:
    """One chunked text + its embedding.

    Gungnir column mapping: id, document_id (FK), chunk_index, text,
    embedding vector(N), char_start, char_end. ``id`` is None before
    Brunnr assigns it.
    """

    document_id: int
    chunk_index: int
    text: str
    embedding: tuple[float, ...] | None = None
    char_start: int | None = None
    char_end: int | None = None
    id: int | None = None


@dataclass(frozen=True, slots=True)
class RetrievalHit:
    """One row from Brunnr's vector / text / hybrid search."""

    chunk_id: int
    document_id: int
    document_title: str | None
    text: str
    score: float
    char_start: int | None = None
    char_end: int | None = None


@dataclass(frozen=True, slots=True)
class BrunnrStats:
    """What ``ember well status`` shows. Returned by Brunnr.count()."""

    documents: int
    chunks: int
    embedded_chunks: int
    size_bytes: int


__all__ = [
    "BrunnrStats",
    "Chunk",
    "Document",
    "RetrievalHit",
]

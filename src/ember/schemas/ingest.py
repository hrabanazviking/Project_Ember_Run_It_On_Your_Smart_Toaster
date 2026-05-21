"""Ingest-orchestration types — Smiðja's inputs and outputs.

Per ``docs/architecture/DOMAIN_MAP.md`` §3 and
``docs/adapters/SMIDJA_INGEST_PATTERNS.md``. These types cross the
Munnr ↔ Smiðja ↔ Brunnr boundary, so they live in ``ember.schemas``
rather than inside ``ember.well.smidja``.

Added in Phase 3 (additive to Phase 2's schemas).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Mapping  # noqa: UP035  # re-exported below


class IngestSourceKind(StrEnum):
    LOCAL_FILES = "local_files"
    URL_FETCH = "url_fetch"
    SHARED_WELL = "shared_well"
    NOMAD = "nomad"


class IngestEntryStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class IngestJob:
    """A single ingest run. Submitted by Munnr to a Smiðja source."""

    job_id: str
    source_kind: IngestSourceKind
    source_root: str
    options: Mapping[str, object] = field(default_factory=dict)
    started_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class IngestEntry:
    """One item inside an ingest job — typically one file or URL."""

    path_or_id: str
    hash: str | None
    status: IngestEntryStatus
    chunk_count: int = 0
    error: str | None = None
    committed_through_chunk: int | None = None


@dataclass(frozen=True, slots=True)
class IngestSummary:
    """What Smiðja returns to Munnr on completion."""

    job_id: str
    n_documents: int
    n_chunks: int
    n_failed: int
    elapsed_s: float


@dataclass(frozen=True, slots=True)
class ParsedFile:
    """A source's parsed output — what the chunker consumes."""

    path: Path
    text: str
    content_type: str
    hash: str


__all__ = [
    "IngestEntry",
    "IngestEntryStatus",
    "IngestJob",
    "IngestSourceKind",
    "IngestSummary",
    "ParsedFile",
]

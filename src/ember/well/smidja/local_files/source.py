"""local_files Smiðja source — walks a directory tree.

Per ``docs/adapters/SMIDJA_INGEST_PATTERNS.md`` §2.1. Yields one
:class:`ember.schemas.ingest.ParsedFile` per readable file whose suffix
is in the include set and whose path does not pass through an excluded
directory. The orchestrator :func:`run` chunks, embeds, and deposits
each parsed file via the configured Brunnr handle.

Supported content types in Phase 3: ``.md``, ``.txt``, ``.json``,
``.jsonl``, ``.yaml``. URL fetch / shared-well / Nomad sources ship in
later phases.
"""

from __future__ import annotations

import fnmatch
import hashlib
import logging
import stat
import time
from collections.abc import Iterator, Sequence
from pathlib import Path

from ember.schemas.chunks import Chunk, Document
from ember.schemas.config import SmidjaConfig
from ember.schemas.errors import BrunnrError, IngestError
from ember.schemas.ingest import (
    IngestSourceKind,
    IngestSummary,
    ParsedFile,
)
from ember.well.smidja.chunker import chunk as chunk_text
from ember.well.smidja.embed_client import OllamaEmbedClient
from ember.well.smidja.journal import Journal

logger = logging.getLogger(__name__)


DEFAULT_INCLUDE_SUFFIXES: tuple[str, ...] = (
    ".md",
    ".txt",
    ".json",
    ".jsonl",
    ".yaml",
    ".yml",
)
DEFAULT_EXCLUDE_DIRS: tuple[str, ...] = (
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
)

# Filenames the ingest skips even when their suffix is in the include set.
# These commonly hold secrets that an operator does NOT want vectorised
# into the Well. Hardening pass added this; an operator running
# ``ember well ingest ~/`` would otherwise have shipped their SSH keys,
# pgpass, AWS credentials, etc. straight into pgvector.
DEFAULT_EXCLUDE_FILE_PATTERNS: tuple[str, ...] = (
    ".env",
    ".env.*",
    ".pgpass",
    ".netrc",
    ".aws/*",
    "id_rsa*",
    "id_ed25519*",
    "id_ecdsa*",
    "id_dsa*",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*.kdbx",
)

# Maximum bytes per file. Files larger than this are skipped with a
# warning rather than read into memory. The threshold is generous
# (markdown rarely runs to gigabytes); the cap exists to defend against
# an operator pointing the ingest at, e.g., a 50 GB log file or — worse —
# a device node like /dev/zero that would read forever.
DEFAULT_MAX_FILE_BYTES: int = 64 * 1024 * 1024  # 64 MiB

_CONTENT_TYPE_BY_SUFFIX: dict[str, str] = {
    ".md": "md",
    ".txt": "txt",
    ".json": "json",
    ".jsonl": "jsonl",
    ".yaml": "yaml",
    ".yml": "yaml",
}


# --------------------------------------------------------------------- #
# Walk + parse                                                          #
# --------------------------------------------------------------------- #


def walk(
    root: Path,
    *,
    include_suffixes: Sequence[str] = DEFAULT_INCLUDE_SUFFIXES,
    exclude_dirs: Sequence[str] = DEFAULT_EXCLUDE_DIRS,
    exclude_file_patterns: Sequence[str] = DEFAULT_EXCLUDE_FILE_PATTERNS,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
) -> Iterator[ParsedFile]:
    """Yield ``ParsedFile`` per matching file under ``root``.

    Files are sorted by path for deterministic ingest order. Unreadable
    files, non-utf8 files, oversize files, sensitive-name files, and
    non-regular files (FIFOs, device nodes, sockets) are logged and
    skipped, never raised.
    """
    root = root.expanduser().resolve()
    if not root.exists():
        raise IngestError(f"source root does not exist: {root}")
    if not root.is_dir():
        raise IngestError(f"source root is not a directory: {root}")

    include_set = frozenset(s.lower() for s in include_suffixes)
    exclude_set = frozenset(exclude_dirs)
    exclude_patterns = tuple(exclude_file_patterns)

    for path in _iter_matching(root, include_set, exclude_set, exclude_patterns):
        try:
            data = path.read_bytes()
        except OSError as exc:
            logger.warning("local_files: skipping unreadable %s: %s", path, exc)
            continue
        if len(data) > max_file_bytes:
            logger.warning(
                "local_files: skipping oversize %s (%d bytes > %d cap)",
                path, len(data), max_file_bytes,
            )
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            logger.warning("local_files: skipping non-utf8 %s: %s", path, exc)
            continue
        content_type = _CONTENT_TYPE_BY_SUFFIX.get(path.suffix.lower(), "txt")
        digest = hashlib.sha256(data).hexdigest()
        yield ParsedFile(path=path, text=text, content_type=content_type, hash=digest)


def _iter_matching(
    root: Path,
    include_suffixes: frozenset[str],
    exclude_dirs: frozenset[str],
    exclude_file_patterns: tuple[str, ...] = (),
) -> Iterator[Path]:
    candidates: list[Path] = []
    for path in root.rglob("*"):
        # Skip non-regular files (FIFOs, device nodes, sockets). A
        # bare ``is_file()`` would accept ``/dev/zero``, where
        # ``read_bytes()`` would block reading forever. One stat per
        # candidate; the failure mode otherwise is "ingest hangs and
        # the operator has to kill -9 the process".
        try:
            st_mode = path.lstat().st_mode
        except OSError:
            continue
        if not stat.S_ISREG(st_mode):
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in exclude_dirs for part in rel_parts):
            continue
        if path.suffix.lower() not in include_suffixes:
            continue
        # Sensitive-filename denylist (.env, *.key, id_rsa*, etc.).
        # Checks both the basename and any nested-path match (so
        # ``.aws/credentials`` is caught by the ``.aws/*`` pattern).
        rel_str = "/".join(rel_parts)
        if any(
            fnmatch.fnmatchcase(path.name, pat)
            or fnmatch.fnmatchcase(rel_str, pat)
            for pat in exclude_file_patterns
        ):
            logger.warning(
                "local_files: skipping sensitive-name file %s "
                "(matches denylist)", path,
            )
            continue
        candidates.append(path)
    candidates.sort()
    yield from candidates


# --------------------------------------------------------------------- #
# Run — the orchestrator                                                #
# --------------------------------------------------------------------- #


def run(  # noqa: PLR0913 — orchestrator naturally takes one config + several override hooks for tests
    brunnr,  # BrunnrHandle protocol — untyped to avoid circular import
    *,
    root: Path,
    smidja_config: SmidjaConfig | None = None,
    embed_client: OllamaEmbedClient | None = None,
    include_suffixes: Sequence[str] = DEFAULT_INCLUDE_SUFFIXES,
    exclude_dirs: Sequence[str] = DEFAULT_EXCLUDE_DIRS,
    resume_job_id: str | None = None,
) -> IngestSummary:
    """Walk ``root``, chunk + embed, deposit via ``brunnr``.

    ``embed_client`` defaults to a fresh :class:`OllamaEmbedClient`
    constructed from ``smidja_config.embedding``. Passing one explicitly
    lets tests mock the embedding HTTP without monkey-patching.
    """
    cfg = smidja_config or SmidjaConfig()
    client = embed_client or OllamaEmbedClient(config=cfg.embedding)
    journal = Journal.open(
        cfg.journal,
        IngestSourceKind.LOCAL_FILES,
        source_root=str(root),
        job_id=resume_job_id,
    )

    started = time.monotonic()
    n_documents = 0
    n_chunks = 0
    n_failed = 0

    for parsed in walk(
        root, include_suffixes=include_suffixes, exclude_dirs=exclude_dirs
    ):
        entry_id = str(parsed.path)
        if journal.is_done(entry_id):
            logger.debug("local_files: skipping done entry %s", entry_id)
            continue
        journal.mark_in_progress(entry_id, content_hash=parsed.hash)

        try:
            doc_id = brunnr.add_document(
                Document(
                    source=str(parsed.path),
                    title=parsed.path.name,
                    content_type=parsed.content_type,
                    hash=parsed.hash,
                )
            )
        except BrunnrError as exc:
            journal.mark_failed(entry_id, f"add_document: {exc}")
            n_failed += 1
            continue

        proto_chunks = list(chunk_text(parsed.text, config=cfg.chunker))
        if not proto_chunks:
            journal.mark_done(entry_id, chunk_count=0, content_hash=parsed.hash)
            n_documents += 1
            continue

        texts = [c.text for c in proto_chunks]
        vectors = client.embed(texts)

        if len(vectors) != len(proto_chunks):
            journal.mark_failed(
                entry_id,
                f"embed_client returned {len(vectors)} vectors for {len(proto_chunks)} chunks",
            )
            n_failed += 1
            continue

        ready: list[Chunk] = []
        chunk_failures = 0
        for proto, vector in zip(proto_chunks, vectors, strict=True):
            if vector is None:
                chunk_failures += 1
                continue
            ready.append(
                Chunk(
                    document_id=doc_id,
                    chunk_index=proto.chunk_index,
                    text=proto.text,
                    embedding=vector,
                    char_start=proto.char_start,
                    char_end=proto.char_end,
                )
            )

        try:
            written = brunnr.add_chunks(ready)
        except BrunnrError as exc:
            journal.mark_failed(entry_id, f"add_chunks: {exc}")
            n_failed += 1
            continue

        n_documents += 1
        n_chunks += len(written)
        n_failed += chunk_failures
        journal.mark_done(
            entry_id, chunk_count=len(written), content_hash=parsed.hash
        )

    journal.complete()
    elapsed = time.monotonic() - started
    return IngestSummary(
        job_id=journal.job_id,
        n_documents=n_documents,
        n_chunks=n_chunks,
        n_failed=n_failed,
        elapsed_s=elapsed,
    )


# Backwards-compat aliases kept for callers that imported the old names.
DEFAULT_INCLUDE = DEFAULT_INCLUDE_SUFFIXES
DEFAULT_EXCLUDE = DEFAULT_EXCLUDE_DIRS


__all__ = [
    "DEFAULT_EXCLUDE",
    "DEFAULT_EXCLUDE_DIRS",
    "DEFAULT_EXCLUDE_FILE_PATTERNS",
    "DEFAULT_INCLUDE",
    "DEFAULT_INCLUDE_SUFFIXES",
    "DEFAULT_MAX_FILE_BYTES",
    "run",
    "walk",
]

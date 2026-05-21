"""sqlite_vec-backed Brunnr adapter.

The first-slice default. Single file under
``~/.ember/well/store.db``; zero auxiliary processes; runs on a toaster.

The schema lives in :file:`schema.sql` (loaded as a package resource so
the wheel ships it). The vector store is a sqlite-vec ``vec0`` virtual
table; full-text search uses FTS5 with insert/update/delete triggers.

Hybrid search uses reciprocal rank fusion (RRF) of the vector and FTS
result sets — the same shape Gungnir's ``ingest.py`` uses (see
``docs/adapters/GUNGNIR_WELL_REFERENCE.md`` §6).
"""

from __future__ import annotations

import contextlib
import json
import logging
import sqlite3
import struct
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING

import sqlite_vec

from ember.schemas.chunks import BrunnrStats, Chunk, Document, RetrievalHit
from ember.schemas.config import BrunnrBackend, BrunnrConfig
from ember.schemas.episode import Episode
from ember.schemas.errors import (
    BrunnrError,
    Disconnected,
    DisconnectReason,
    SchemaError,
)

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)

_RRF_K = 60  # standard RRF dampener


def _now_utc() -> datetime:
    return datetime.now(tz=UTC)


def _load_schema_sql(embedding_dim: int) -> str:
    raw = (
        resources.files("ember.well.brunnr.sqlite_vec")
        .joinpath("schema.sql")
        .read_text(encoding="utf-8")
    )
    return raw.format(embedding_dim=embedding_dim)


class SqliteVecBrunnr:
    """sqlite-vec Brunnr adapter. Implements :class:`BrunnrHandle`."""

    SCHEMA_VERSION = 1
    backend_kind: str = "sqlite_vec"

    def __init__(self, conn: sqlite3.Connection, embedding_dim: int) -> None:
        self._conn = conn
        self.embedding_dim = embedding_dim

    # ------------------------------------------------------------- open

    @classmethod
    def open(cls, config: BrunnrConfig) -> SqliteVecBrunnr | Disconnected:
        if (
            config.backend is not BrunnrBackend.SQLITE_VEC
            or config.sqlite_vec is None
        ):
            return Disconnected(
                reason=DisconnectReason.CONFIG_INVALID,
                since=_now_utc(),
                detail="sqlite_vec backend not configured",
            )

        path = Path(config.sqlite_vec.path).expanduser()
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return Disconnected(
                reason=DisconnectReason.CONFIG_INVALID,
                since=_now_utc(),
                detail=f"cannot create parent directory: {exc}",
            )

        try:
            conn = sqlite3.connect(str(path))
            conn.execute("PRAGMA foreign_keys = ON")
            if config.sqlite_vec.wal_mode:
                conn.execute("PRAGMA journal_mode = WAL")
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            conn.enable_load_extension(False)
        except (sqlite3.Error, OSError) as exc:
            return Disconnected(
                reason=DisconnectReason.BACKEND_REPORTED_UNAVAILABLE,
                since=_now_utc(),
                detail=str(exc),
            )

        try:
            conn.executescript(_load_schema_sql(config.embedding_dim))
            conn.commit()
        except sqlite3.Error as exc:
            conn.close()
            return Disconnected(
                reason=DisconnectReason.BACKEND_REPORTED_UNAVAILABLE,
                since=_now_utc(),
                detail=f"schema apply failed: {exc}",
            )

        return cls(conn, config.embedding_dim)

    # ------------------------------------------------------------- writes

    def add_document(self, doc: Document) -> int:
        existing = self.has_document(doc.hash)
        if existing is not None:
            return existing
        # Wrap the insert in BrunnrError per the typed-value contract.
        # Hardening pass added this — previously a sqlite3.OperationalError
        # (e.g. disk full, schema drift, locked DB) would propagate raw
        # and Smiðja's caller had no clean way to mark the document
        # failed in its journal.
        try:
            cur = self._conn.execute(
                """
                INSERT INTO documents (source, title, content_type, hash, metadata)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    doc.source,
                    doc.title,
                    doc.content_type,
                    doc.hash,
                    json.dumps(dict(doc.metadata)),
                ),
            )
            self._conn.commit()
        except sqlite3.Error as exc:
            with contextlib.suppress(sqlite3.Error):
                self._conn.rollback()
            raise BrunnrError(f"add_document failed: {exc}") from exc
        assert cur.lastrowid is not None
        return cur.lastrowid

    def add_chunks(self, chunks: Iterable[Chunk]) -> list[int]:
        ids: list[int] = []
        try:
            for chunk in chunks:
                if (
                    chunk.embedding is not None
                    and len(chunk.embedding) != self.embedding_dim
                ):
                    raise BrunnrError(
                        f"chunk embedding dim {len(chunk.embedding)} "
                        f"!= Brunnr-configured dim {self.embedding_dim}"
                    )
                cur = self._conn.execute(
                    """
                    INSERT INTO chunks (document_id, chunk_index, text, char_start, char_end)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(document_id, chunk_index) DO UPDATE SET
                        text       = excluded.text,
                        char_start = excluded.char_start,
                        char_end   = excluded.char_end
                    RETURNING id
                    """,
                    (
                        chunk.document_id,
                        chunk.chunk_index,
                        chunk.text,
                        chunk.char_start,
                        chunk.char_end,
                    ),
                )
                row = cur.fetchone()
                if row is None:
                    raise BrunnrError("chunk upsert returned no row id")
                chunk_id: int = row[0]
                ids.append(chunk_id)

                if chunk.embedding is not None:
                    blob = sqlite_vec.serialize_float32(list(chunk.embedding))
                    self._conn.execute(
                        "DELETE FROM chunk_vectors WHERE chunk_id = ?",
                        (chunk_id,),
                    )
                    self._conn.execute(
                        "INSERT INTO chunk_vectors (chunk_id, embedding) VALUES (?, ?)",
                        (chunk_id, blob),
                    )
        except sqlite3.Error as exc:
            # Wrap rollback in suppress — if rollback itself fails
            # (connection already broken), the original failure should
            # still surface as BrunnrError rather than be replaced by
            # the rollback's secondary exception.
            with contextlib.suppress(sqlite3.Error):
                self._conn.rollback()
            raise BrunnrError(f"add_chunks failed: {exc}") from exc
        except (ValueError, struct.error) as exc:
            # sqlite_vec.serialize_float32 can raise ValueError or
            # struct.error on NaN / Inf embeddings (bad embedding model
            # output). Same rollback + BrunnrError wrap as the
            # sqlite-error path.
            with contextlib.suppress(sqlite3.Error):
                self._conn.rollback()
            raise BrunnrError(
                f"add_chunks failed during embedding serialisation: {exc}"
            ) from exc
        self._conn.commit()
        return ids

    def add_episode(self, episode: Episode) -> int:
        cur = self._conn.execute(
            """
            INSERT INTO episodes (
                operator_input, ember_reply, cited_chunk_ids,
                funi_model, well_disconnected, started_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                episode.operator_input,
                episode.ember_reply,
                json.dumps(list(episode.cited_chunk_ids)),
                episode.funi_model,
                1 if episode.well_disconnected else 0,
                _isoformat(episode.started_at),
                _isoformat(episode.completed_at),
            ),
        )
        self._conn.commit()
        assert cur.lastrowid is not None
        return cur.lastrowid

    # ------------------------------------------------------------- reads

    def get_document(self, document_id: int) -> Document:
        row = self._conn.execute(
            """
            SELECT id, source, title, content_type, hash, metadata, ingested_at
            FROM documents WHERE id = ?
            """,
            (document_id,),
        ).fetchone()
        if row is None:
            raise BrunnrError(f"document {document_id} not found")
        return _row_to_document(row)

    def get_chunk(self, chunk_id: int) -> Chunk:
        row = self._conn.execute(
            """
            SELECT id, document_id, chunk_index, text, char_start, char_end
            FROM chunks WHERE id = ?
            """,
            (chunk_id,),
        ).fetchone()
        if row is None:
            raise BrunnrError(f"chunk {chunk_id} not found")
        emb_row = self._conn.execute(
            "SELECT embedding FROM chunk_vectors WHERE chunk_id = ?",
            (chunk_id,),
        ).fetchone()
        embedding: tuple[float, ...] | None = None
        if emb_row is not None and emb_row[0] is not None:
            # sqlite-vec stores float32 little-endian; deserialise.
            blob = emb_row[0]
            count = len(blob) // 4
            embedding = struct.unpack(f"<{count}f", blob)
        return Chunk(
            document_id=row[1],
            chunk_index=row[2],
            text=row[3],
            embedding=embedding,
            char_start=row[4],
            char_end=row[5],
            id=row[0],
        )

    def has_document(self, content_hash: str) -> int | None:
        # Wrap in BrunnrError so a closed/broken connection surfaces
        # under the typed contract, the same way add_* does.
        try:
            row = self._conn.execute(
                "SELECT id FROM documents WHERE hash = ?",
                (content_hash,),
            ).fetchone()
        except sqlite3.Error as exc:
            raise BrunnrError(f"has_document failed: {exc}") from exc
        return None if row is None else row[0]

    def count(self) -> BrunnrStats:
        try:
            n_docs = self._conn.execute(
                "SELECT COUNT(*) FROM documents"
            ).fetchone()[0]
            n_chunks = self._conn.execute(
                "SELECT COUNT(*) FROM chunks"
            ).fetchone()[0]
            n_embedded = self._conn.execute(
                "SELECT COUNT(*) FROM chunk_vectors"
            ).fetchone()[0]
        except sqlite3.Error as exc:
            raise BrunnrError(f"count failed: {exc}") from exc
        size_bytes = 0
        for db_path in self._db_paths():
            with contextlib.suppress(OSError):
                size_bytes += db_path.stat().st_size
        return BrunnrStats(
            documents=n_docs,
            chunks=n_chunks,
            embedded_chunks=n_embedded,
            size_bytes=size_bytes,
        )

    # ------------------------------------------------------------- search

    def vector_search(
        self,
        qvec: Sequence[float],
        k: int,
        filter: object | None = None,
    ) -> list[RetrievalHit]:
        if len(qvec) != self.embedding_dim:
            raise BrunnrError(
                f"query vector dim {len(qvec)} != Brunnr dim {self.embedding_dim}"
            )
        qblob = sqlite_vec.serialize_float32(list(qvec))
        cur = self._conn.execute(
            """
            SELECT v.chunk_id, v.distance, c.document_id, c.text,
                   c.char_start, c.char_end, d.title
            FROM chunk_vectors v
            JOIN chunks    c ON c.id = v.chunk_id
            JOIN documents d ON d.id = c.document_id
            WHERE v.embedding MATCH ? AND k = ?
            ORDER BY v.distance
            """,
            (qblob, k),
        )
        hits: list[RetrievalHit] = []
        for row in cur:
            distance = row[1]
            # vec0 reports cosine distance in [0, 2]; convert to similarity-ish
            # score in (-∞, 1]: 1 - distance.
            score = 1.0 - float(distance)
            hits.append(
                RetrievalHit(
                    chunk_id=row[0],
                    document_id=row[2],
                    document_title=row[6],
                    text=row[3],
                    score=score,
                    char_start=row[4],
                    char_end=row[5],
                )
            )
        return hits

    def text_search(
        self,
        query: str,
        k: int,
        filter: object | None = None,
    ) -> list[RetrievalHit]:
        safe_query = _escape_fts5_query(query)
        if not safe_query:
            return []
        cur = self._conn.execute(
            """
            SELECT c.id, c.document_id, c.text, c.char_start, c.char_end,
                   d.title, fts.rank
            FROM chunk_fts AS fts
            JOIN chunks    c ON c.id = fts.rowid
            JOIN documents d ON d.id = c.document_id
            WHERE chunk_fts MATCH ?
            ORDER BY fts.rank
            LIMIT ?
            """,
            (safe_query, k),
        )
        hits: list[RetrievalHit] = []
        for row in cur:
            # FTS5 rank is negative (lower is better); convert to a
            # positive score so callers don't get confused.
            score = -float(row[6])
            hits.append(
                RetrievalHit(
                    chunk_id=row[0],
                    document_id=row[1],
                    document_title=row[5],
                    text=row[2],
                    score=score,
                    char_start=row[3],
                    char_end=row[4],
                )
            )
        return hits

    def hybrid_search(
        self,
        qvec: Sequence[float],
        query: str,
        k: int,
    ) -> list[RetrievalHit]:
        # Wider candidate pool for fusion, then trim to k.
        pool = max(k * 5, 50)
        vec_hits = self.vector_search(qvec, pool)
        fts_hits = self.text_search(query, pool)

        rrf: dict[int, float] = {}
        order: dict[int, RetrievalHit] = {}
        for rank, hit in enumerate(vec_hits, start=1):
            rrf[hit.chunk_id] = rrf.get(hit.chunk_id, 0.0) + 1.0 / (_RRF_K + rank)
            order.setdefault(hit.chunk_id, hit)
        for rank, hit in enumerate(fts_hits, start=1):
            rrf[hit.chunk_id] = rrf.get(hit.chunk_id, 0.0) + 1.0 / (_RRF_K + rank)
            order.setdefault(hit.chunk_id, hit)

        ranked_ids = sorted(rrf, key=lambda cid: rrf[cid], reverse=True)[:k]
        return [
            RetrievalHit(
                chunk_id=order[cid].chunk_id,
                document_id=order[cid].document_id,
                document_title=order[cid].document_title,
                text=order[cid].text,
                score=rrf[cid],
                char_start=order[cid].char_start,
                char_end=order[cid].char_end,
            )
            for cid in ranked_ids
        ]

    # ------------------------------------------------------------- close

    def close(self) -> None:
        # Suppress to honour the "close never raises" Protocol contract,
        # but log any error so an operator can investigate silent
        # close-time failures (e.g. WAL-flush failure on a full disk).
        try:
            self._conn.close()
        except sqlite3.Error as exc:
            logger.warning(
                "sqlite_vec: close() suppressed error: %s: %s",
                type(exc).__name__, exc,
            )

    # ------------------------------------------------------------- internals

    def _db_paths(self) -> list[Path]:
        path_row = self._conn.execute("PRAGMA database_list").fetchone()
        if path_row is None or not path_row[2]:
            return []
        main = Path(path_row[2])
        return [main, main.with_name(main.name + "-wal"), main.with_name(main.name + "-shm")]


# --------------------------------------------------------------------- #
# Module-level open() for the registry                                  #
# --------------------------------------------------------------------- #


def open(config: BrunnrConfig) -> SqliteVecBrunnr | Disconnected:
    return SqliteVecBrunnr.open(config)


# --------------------------------------------------------------------- #
# Helpers                                                                #
# --------------------------------------------------------------------- #


def _row_to_document(row: tuple) -> Document:
    try:
        metadata = json.loads(row[5]) if row[5] else {}
    except json.JSONDecodeError as exc:
        raise SchemaError(f"document {row[0]} has invalid metadata json: {exc}") from exc
    ingested_at = _parse_iso(row[6])
    return Document(
        source=row[1],
        title=row[2],
        content_type=row[3],
        hash=row[4] or "",
        metadata=metadata,
        ingested_at=ingested_at,
        id=row[0],
    )


def _isoformat(value: datetime | None) -> str | None:
    return None if value is None else value.isoformat()


def _parse_iso(value: str | None) -> datetime | None:
    if value is None:
        return None
    # SQLite CURRENT_TIMESTAMP is naïve UTC ('YYYY-MM-DD HH:MM:SS');
    # ISO strings are also handled.
    cleaned = value.replace(" ", "T")
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None


def _escape_fts5_query(query: str) -> str:
    """Make any operator string safe for FTS5 ``MATCH``.

    FTS5's query language reserves ``:``, ``"``, ``*``, ``(``, ``)``,
    bare ``AND/OR/NOT/NEAR``, and the column-name syntax ``foo:bar``
    (which is what bit the Hjarta probe at 2026-05-21 with ``run:``).
    Splitting on whitespace and wrapping each token as a literal phrase
    sidesteps every special meaning while preserving useful retrieval —
    the operator's natural-language input becomes an OR over the words
    they typed. Empty / whitespace-only input returns the empty string;
    callers treat that as "no results".

    Hardening pass (Batch C): also strips control characters and Unicode
    bidirectional override marks from each token before quoting. Without
    this, a newline inside a token could break the audit log's per-line
    parsing, and a U+202E (Right-to-Left Override) could reorder how the
    query reads in operator-facing logs so a malicious search looks
    benign on inspection.
    """
    tokens = [_strip_unsafe_chars(t) for t in query.split() if t.strip()]
    tokens = [t for t in tokens if t]  # drop tokens that became empty
    if not tokens:
        return ""
    escaped = ['"' + t.replace('"', '""') + '"' for t in tokens]
    return " OR ".join(escaped)


# Unicode general categories whose bytes can confuse log readers or
# terminal renderers: Cc (control chars), Cf (format chars — includes
# the bidirectional overrides RLE/LRE/PDF/RLO/LRO etc.). The latter
# matters because audit-log readers and CLI render layers display the
# query back to the operator; a Cf char hidden in a token can reorder
# how the query appears on screen vs what's actually queried.
_UNSAFE_UNICODE_CATEGORIES = frozenset({"Cc", "Cf"})


def _strip_unsafe_chars(token: str) -> str:
    """Remove control + bidirectional-override characters from a token.

    Stdlib-only — uses ``unicodedata.category`` which classifies every
    codepoint.
    """
    import unicodedata  # noqa: PLC0415 — only needed here

    return "".join(
        c for c in token
        if unicodedata.category(c) not in _UNSAFE_UNICODE_CATEGORIES
    )


__all__ = ["SqliteVecBrunnr", "open"]

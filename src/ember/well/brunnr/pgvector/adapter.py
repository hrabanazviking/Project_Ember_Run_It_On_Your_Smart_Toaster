"""pgvector-backed Brunnr adapter (ADR 0010).

Implements :class:`ember.well.brunnr.handle.BrunnrHandle` against
Postgres + pgvector. Peers with the slice-1 ``sqlite_vec`` adapter —
same Protocol, same hybrid-search shape (RRF with ``k=60`` per
``docs/adapters/GUNGNIR_WELL_REFERENCE.md`` §6), Gungnir-compatible
on-disk shape (`documents`, `chunks`, `episodes`).

The adapter is **schema-probe first** (ADR 0010 §2.2): if the
configured schema already holds Gungnir-shape tables with the right
embedding dimension, the adapter uses them as-is and only creates the
`episodes` table that Gungnir doesn't have. If the tables don't exist,
the adapter applies :file:`schema.sql` to bootstrap an empty database.

``psycopg`` and ``pgvector`` are imported lazily so an Ember built
without the ``pgvector`` extra can still import the adapter module
without ``ImportError``. Calling :meth:`PgVectorBrunnr.open` without
those deps returns a typed :class:`Disconnected` value.
"""

from __future__ import annotations

import contextlib
import json
import logging
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib import resources
from typing import Any

from ember.schemas.chunks import BrunnrStats, Chunk, Document, RetrievalHit
from ember.schemas.config import BrunnrBackend, BrunnrConfig
from ember.schemas.episode import Episode
from ember.schemas.errors import (
    BrunnrError,
    Disconnected,
    DisconnectReason,
    SchemaError,
)
from ember.well.brunnr.pgvector import secrets as _secrets

_logger = logging.getLogger(__name__)

_RRF_K = 60  # ADR 0010 §2.4 — matches sqlite_vec, matches Gungnir.

# Postgres SQLSTATE classes that mean "auth failed" vs "host unreachable".
# SQLSTATE classifications per PostgreSQL's documented error codes.
# These are precise (PostgreSQL has held them stable across major
# versions); the string-match fallbacks below are last-resort heuristics
# for libpq paths that don't surface a sqlstate at all.
_AUTH_SQLSTATES = frozenset({"28P01", "28000"})
_CONN_REFUSED_SQLSTATES = frozenset({"08001", "08006"})
_TIMEOUT_HINT = "timeout"


def _now_utc() -> datetime:
    return datetime.now(tz=UTC)


def _load_schema_sql() -> str:
    return (
        resources.files("ember.well.brunnr.pgvector")
        .joinpath("schema.sql")
        .read_text(encoding="utf-8")
    )


def render_schema_sql(*, embedding_dim: int, schema: str) -> str:
    """Substitute ``{embedding_dim}`` and ``{schema}`` into the DDL.

    Public helper so the schema-shape unit test can assert the rendered
    SQL is well-formed (and doesn't accidentally leak format braces).
    """
    safe_schema = _quote_ident(schema)
    template = _load_schema_sql()
    return template.replace(
        "{embedding_dim}", str(int(embedding_dim))
    ).replace(
        "{schema}", safe_schema
    )


def _quote_ident(name: str) -> str:
    """Quote a Postgres identifier safely.

    pgsql identifier rules: double-quote, double internal double-quotes.

    Refuses:

    - NUL bytes (Postgres can't store them).
    - Any other ASCII control character (0x01-0x1f, 0x7f) — these
      can confuse terminals when the identifier appears in error
      messages (ESC sequences, bell, etc.) and have no legitimate
      use in a schema or table name.
    """
    if not name:
        raise BrunnrError("identifier is empty")
    bad = [c for c in name if ord(c) < 0x20 or ord(c) == 0x7f]
    if bad:
        raise BrunnrError(
            f"identifier {name!r} contains control character(s) "
            f"{[hex(ord(c)) for c in bad]}"
        )
    escaped = name.replace('"', '""')
    return f'"{escaped}"'


class PgVectorBrunnr:
    """pgvector Brunnr adapter. Implements :class:`BrunnrHandle`."""

    SCHEMA_VERSION = 1
    backend_kind: str = "pgvector"

    def __init__(
        self,
        conn: Any,  # psycopg.Connection — typed as Any so import stays lazy
        *,
        embedding_dim: int,
        schema: str,
        read_only: bool,
    ) -> None:
        self._conn = conn
        self.embedding_dim = embedding_dim
        self._schema = schema
        self._read_only = read_only

    # ------------------------------------------------------------- open

    @classmethod
    def open(  # noqa: PLR0911,PLR0912,PLR0915 — open() is the failure-classification surface
        cls,
        config: BrunnrConfig,
    ) -> PgVectorBrunnr | Disconnected:
        if (
            config.backend is not BrunnrBackend.PGVECTOR
            or config.pgvector is None
        ):
            return Disconnected(
                reason=DisconnectReason.CONFIG_INVALID,
                since=_now_utc(),
                detail="pgvector backend not configured",
            )
        pg_cfg = config.pgvector

        # Lazy deps — psycopg + pgvector. Missing → typed disconnect.
        try:
            import psycopg  # noqa: PLC0415 — lazy by design
            from pgvector.psycopg import register_vector  # noqa: PLC0415
        except ImportError as exc:
            return Disconnected(
                reason=DisconnectReason.BACKEND_REPORTED_UNAVAILABLE,
                since=_now_utc(),
                detail=(
                    f"pgvector extra not installed: {exc}. "
                    f"Install with `pip install ember-agent[pgvector]`."
                ),
            )

        # Resolve the secret per ADR 0010 §2.5.
        resolution = _secrets.resolve(pg_cfg)
        if resolution.secret is None:
            return Disconnected(
                reason=DisconnectReason.AUTH_FAILED,
                since=_now_utc(),
                detail=f"no Well secret resolved ({resolution.reason})",
            )

        # Open the connection. Failure → classified disconnect.
        try:
            conn = psycopg.connect(
                pg_cfg.url,
                password=resolution.secret,
                connect_timeout=int(pg_cfg.connect_timeout_s),
                autocommit=False,
            )
        except psycopg.OperationalError as exc:
            return _classify_operational_error(exc)
        except (ValueError, TypeError) as exc:
            return Disconnected(
                reason=DisconnectReason.CONFIG_INVALID,
                since=_now_utc(),
                detail=f"URL parse error: {exc}",
            )

        # Ensure the pgvector extension exists *before* registering the
        # codec — `register_vector` looks up the `vector` type by name and
        # fails if the extension hasn't been created in this database. On
        # Gungnir the extension always exists (the schema uses it); on a
        # fresh ephemeral container we create it on first open.
        try:
            ext_outcome = _ensure_pgvector_extension(conn, read_only=pg_cfg.read_only)
        except psycopg.Error as exc:
            with contextlib.suppress(Exception):
                conn.close()
            return Disconnected(
                reason=DisconnectReason.BACKEND_REPORTED_UNAVAILABLE,
                since=_now_utc(),
                detail=f"pgvector extension probe failed: {exc}",
            )
        if ext_outcome is not None:
            with contextlib.suppress(Exception):
                conn.close()
            return ext_outcome

        # Register the pgvector codec on this connection.
        try:
            register_vector(conn)
        except Exception as exc:  # pragma: no cover — pgvector import failed earlier
            with contextlib.suppress(Exception):
                conn.close()
            return Disconnected(
                reason=DisconnectReason.BACKEND_REPORTED_UNAVAILABLE,
                since=_now_utc(),
                detail=f"pgvector codec registration failed: {exc}",
            )

        # Schema-probe then apply if needed (ADR 0010 §2.2-2.3).
        try:
            probe = _probe_schema(conn, schema=pg_cfg.schema)
        except psycopg.Error as exc:
            with contextlib.suppress(Exception):
                conn.close()
            return Disconnected(
                reason=DisconnectReason.BACKEND_REPORTED_UNAVAILABLE,
                since=_now_utc(),
                detail=f"schema probe failed: {exc}",
            )

        if probe.documents_present and probe.chunks_present:
            # Existing tables — verify dim, never DDL into them.
            if (
                probe.embedding_dim is not None
                and probe.embedding_dim != config.embedding_dim
            ):
                with contextlib.suppress(Exception):
                    conn.close()
                return Disconnected(
                    reason=DisconnectReason.BACKEND_REPORTED_UNAVAILABLE,
                    since=_now_utc(),
                    detail=(
                        f"chunks.embedding has dim {probe.embedding_dim}, "
                        f"config.embedding_dim is {config.embedding_dim} — "
                        f"either re-ingest or change config.embedding_dim"
                    ),
                )
            # Episodes is Ember-only — create if missing, never touching
            # the discovered documents/chunks.
            if not probe.episodes_present and not pg_cfg.read_only:
                try:
                    _apply_episodes_only(conn, schema=pg_cfg.schema)
                except psycopg.Error as exc:
                    with contextlib.suppress(Exception):
                        conn.close()
                    return Disconnected(
                        reason=DisconnectReason.BACKEND_REPORTED_UNAVAILABLE,
                        since=_now_utc(),
                        detail=f"episodes-table apply failed: {exc}",
                    )
        else:
            # Empty (or partial) — apply full DDL unless we're read-only.
            if pg_cfg.read_only:
                with contextlib.suppress(Exception):
                    conn.close()
                return Disconnected(
                    reason=DisconnectReason.BACKEND_REPORTED_UNAVAILABLE,
                    since=_now_utc(),
                    detail=(
                        "read_only=true but Well is missing documents/chunks "
                        "tables; refusing to bootstrap silently"
                    ),
                )
            try:
                rendered = render_schema_sql(
                    embedding_dim=config.embedding_dim,
                    schema=pg_cfg.schema,
                )
                with conn.cursor() as cur:
                    cur.execute(rendered)
                conn.commit()
            except psycopg.Error as exc:
                with contextlib.suppress(Exception):
                    conn.rollback()
                with contextlib.suppress(Exception):
                    conn.close()
                return Disconnected(
                    reason=DisconnectReason.BACKEND_REPORTED_UNAVAILABLE,
                    since=_now_utc(),
                    detail=f"schema apply failed: {exc}",
                )

        return cls(
            conn,
            embedding_dim=config.embedding_dim,
            schema=pg_cfg.schema,
            read_only=pg_cfg.read_only,
        )

    # ------------------------------------------------------------- writes

    def add_document(self, doc: Document) -> int:
        self._refuse_if_read_only("add_document")
        existing = self.has_document(doc.hash)
        if existing is not None:
            return existing
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {self._qualified('documents')}
                        (source, title, content_type, hash, metadata)
                    VALUES (%s, %s, %s, %s, %s::jsonb)
                    RETURNING id
                    """,
                    (
                        doc.source,
                        doc.title,
                        doc.content_type,
                        doc.hash,
                        json.dumps(dict(doc.metadata)),
                    ),
                )
                row = cur.fetchone()
            self._conn.commit()
        except Exception as exc:
            with contextlib.suppress(Exception):
                self._conn.rollback()
            raise BrunnrError(f"add_document failed: {exc}") from exc
        if row is None:
            raise BrunnrError("add_document insert returned no row id")
        return int(row[0])

    def add_chunks(self, chunks: Iterable[Chunk]) -> list[int]:
        self._refuse_if_read_only("add_chunks")
        ids: list[int] = []
        try:
            with self._conn.cursor() as cur:
                for chunk in chunks:
                    if (
                        chunk.embedding is not None
                        and len(chunk.embedding) != self.embedding_dim
                    ):
                        raise BrunnrError(
                            f"chunk embedding dim {len(chunk.embedding)} "
                            f"!= Brunnr-configured dim {self.embedding_dim}"
                        )
                    embedding_param = (
                        list(chunk.embedding) if chunk.embedding is not None else None
                    )
                    cur.execute(
                        f"""
                        INSERT INTO {self._qualified('chunks')}
                            (document_id, chunk_index, text,
                             embedding, char_start, char_end)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (document_id, chunk_index) DO UPDATE SET
                            text       = EXCLUDED.text,
                            embedding  = EXCLUDED.embedding,
                            char_start = EXCLUDED.char_start,
                            char_end   = EXCLUDED.char_end
                        RETURNING id
                        """,
                        (
                            chunk.document_id,
                            chunk.chunk_index,
                            chunk.text,
                            embedding_param,
                            chunk.char_start,
                            chunk.char_end,
                        ),
                    )
                    row = cur.fetchone()
                    if row is None:
                        raise BrunnrError("chunk upsert returned no row id")
                    ids.append(int(row[0]))
            self._conn.commit()
        except BrunnrError:
            with contextlib.suppress(Exception):
                self._conn.rollback()
            raise
        except Exception as exc:
            with contextlib.suppress(Exception):
                self._conn.rollback()
            raise BrunnrError(f"add_chunks failed: {exc}") from exc
        return ids

    def add_episode(self, episode: Episode) -> int:
        # Episodes are Ember-side state; read-only Wells still get them
        # when the schema has the table. If the Well is read-only AND
        # has no episodes table, callers will have failed at open().
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO {self._qualified('episodes')} (
                        operator_input, ember_reply, cited_chunk_ids,
                        funi_model, well_disconnected,
                        started_at, completed_at
                    ) VALUES (%s, %s, %s::jsonb, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        episode.operator_input,
                        episode.ember_reply,
                        json.dumps(list(episode.cited_chunk_ids)),
                        episode.funi_model,
                        bool(episode.well_disconnected),
                        episode.started_at,
                        episode.completed_at,
                    ),
                )
                row = cur.fetchone()
            self._conn.commit()
        except Exception as exc:
            with contextlib.suppress(Exception):
                self._conn.rollback()
            raise BrunnrError(f"add_episode failed: {exc}") from exc
        if row is None:
            raise BrunnrError("add_episode insert returned no row id")
        return int(row[0])

    # ------------------------------------------------------------- reads

    def get_document(self, document_id: int) -> Document:
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT id, source, title, content_type, hash,
                           metadata::text, ingested_at
                    FROM {self._qualified('documents')}
                    WHERE id = %s
                    """,
                    (document_id,),
                )
                row = cur.fetchone()
        except Exception as exc:
            raise BrunnrError(f"get_document failed: {exc}") from exc
        if row is None:
            raise BrunnrError(f"document {document_id} not found")
        return _row_to_document(row)

    def get_chunk(self, chunk_id: int) -> Chunk:
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT id, document_id, chunk_index, text,
                           embedding, char_start, char_end
                    FROM {self._qualified('chunks')}
                    WHERE id = %s
                    """,
                    (chunk_id,),
                )
                row = cur.fetchone()
        except Exception as exc:
            raise BrunnrError(f"get_chunk failed: {exc}") from exc
        if row is None:
            raise BrunnrError(f"chunk {chunk_id} not found")
        embedding: tuple[float, ...] | None = None
        if row[4] is not None:
            # pgvector codec returns a numpy array or list; coerce to tuple of floats.
            embedding = tuple(float(x) for x in row[4])
        return Chunk(
            document_id=row[1],
            chunk_index=row[2],
            text=row[3],
            embedding=embedding,
            char_start=row[5],
            char_end=row[6],
            id=row[0],
        )

    def has_document(self, content_hash: str) -> int | None:
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"SELECT id FROM {self._qualified('documents')} "
                    f"WHERE hash = %s",
                    (content_hash,),
                )
                row = cur.fetchone()
        except Exception as exc:
            raise BrunnrError(f"has_document failed: {exc}") from exc
        return None if row is None else int(row[0])

    def count(self) -> BrunnrStats:
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"SELECT COUNT(*) FROM {self._qualified('documents')}"
                )
                n_docs = int(cur.fetchone()[0])
                cur.execute(
                    f"SELECT COUNT(*) FROM {self._qualified('chunks')}"
                )
                n_chunks = int(cur.fetchone()[0])
                cur.execute(
                    f"SELECT COUNT(*) FROM {self._qualified('chunks')} "
                    f"WHERE embedding IS NOT NULL"
                )
                n_embedded = int(cur.fetchone()[0])
                # Approximate on-disk size from pg_total_relation_size of
                # documents+chunks; an exact "database size" includes
                # tables we don't own (skein, kg).
                cur.execute(
                    """
                    SELECT
                      pg_total_relation_size(%s::regclass) +
                      pg_total_relation_size(%s::regclass)
                    """,
                    (
                        self._qualified("documents"),
                        self._qualified("chunks"),
                    ),
                )
                size_bytes = int(cur.fetchone()[0] or 0)
        except Exception as exc:
            raise BrunnrError(f"count failed: {exc}") from exc
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
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT c.id, c.document_id, c.text,
                           c.char_start, c.char_end, d.title,
                           c.embedding <=> %s::vector AS distance
                    FROM {self._qualified('chunks')} c
                    JOIN {self._qualified('documents')} d ON d.id = c.document_id
                    WHERE c.embedding IS NOT NULL
                    ORDER BY c.embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (list(qvec), list(qvec), int(k)),
                )
                rows = cur.fetchall()
        except Exception as exc:
            raise BrunnrError(f"vector_search failed: {exc}") from exc
        hits: list[RetrievalHit] = []
        for row in rows:
            # pgvector cosine distance is in [0, 2]; convert to a
            # similarity-ish score matching the sqlite_vec convention.
            score = 1.0 - float(row[6])
            hits.append(
                RetrievalHit(
                    chunk_id=int(row[0]),
                    document_id=int(row[1]),
                    document_title=row[5],
                    text=row[2],
                    score=score,
                    char_start=row[3],
                    char_end=row[4],
                )
            )
        return hits

    def text_search(
        self,
        query: str,
        k: int,
        filter: object | None = None,
    ) -> list[RetrievalHit]:
        # Mirror the sqlite_vec sanitiser: strip Unicode Cc + Cf bytes
        # (NUL, bidi-overrides, format chars) before handing the query
        # to plainto_tsquery. Without this, a U+202E in the query would
        # land in audit logs and confuse operator-facing diagnostics in
        # the same way the sqlite_vec hardening (Batch C) was guarding
        # against. Postgres itself tolerates these bytes, but the audit
        # contract is symmetric across both adapters.
        from ember.well.brunnr.sqlite_vec.adapter import (  # noqa: PLC0415
            _strip_unsafe_chars,
        )
        cleaned = _strip_unsafe_chars(query).strip()
        if not cleaned:
            return []
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT c.id, c.document_id, c.text,
                           c.char_start, c.char_end, d.title,
                           ts_rank(c.tsv, q) AS rank
                    FROM {self._qualified('chunks')} c
                    JOIN {self._qualified('documents')} d ON d.id = c.document_id,
                         plainto_tsquery('english', %s) AS q
                    WHERE c.tsv @@ q
                    ORDER BY ts_rank(c.tsv, q) DESC
                    LIMIT %s
                    """,
                    (cleaned, int(k)),
                )
                rows = cur.fetchall()
        except Exception as exc:
            raise BrunnrError(f"text_search failed: {exc}") from exc
        return [
            RetrievalHit(
                chunk_id=int(row[0]),
                document_id=int(row[1]),
                document_title=row[5],
                text=row[2],
                score=float(row[6]),
                char_start=row[3],
                char_end=row[4],
            )
            for row in rows
        ]

    def hybrid_search(
        self,
        qvec: Sequence[float],
        query: str,
        k: int,
    ) -> list[RetrievalHit]:
        # Wider candidate pool, then RRF-fuse and trim — same shape as
        # sqlite_vec.hybrid_search and Gungnir's ingest.py.
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
        # Mirror sqlite_vec.close(): log close-time failures rather than
        # silently suppressing them. Operators inspecting the log can
        # then see *why* close failed (idle-in-transaction holding a
        # lock, backend already gone, etc.) instead of getting silence.
        # The Protocol still says close-never-raises; we honour that
        # by catching everything.
        try:
            self._conn.close()
        except Exception as exc:
            _logger.warning("pgvector close failed: %s", exc)

    # ------------------------------------------------------------- internals

    def _qualified(self, table: str) -> str:
        """Return ``"schema"."table"`` with both quoted."""
        return f"{_quote_ident(self._schema)}.{_quote_ident(table)}"

    def _refuse_if_read_only(self, op: str) -> None:
        if self._read_only:
            raise BrunnrError(
                f"{op} refused: PgVectorConfig.read_only=true "
                f"(ADR 0010 §4 — opt-in write-block for shared Wells)"
            )


# --------------------------------------------------------------------- #
# Schema probe                                                          #
# --------------------------------------------------------------------- #


@contextlib.contextmanager
def _cursor(conn):
    cur = conn.cursor()
    try:
        yield cur
    finally:
        with contextlib.suppress(Exception):
            cur.close()


@dataclass(frozen=True, slots=True)
class _SchemaProbe:
    documents_present: bool
    chunks_present: bool
    episodes_present: bool
    embedding_dim: int | None


def _ensure_pgvector_extension(conn, *, read_only: bool) -> Disconnected | None:
    """Make sure the ``vector`` extension exists in this database.

    Returns None on success, or a typed :class:`Disconnected` value when
    the extension is missing and we can't (or shouldn't) create it.

    Order of operations:

    - Probe ``pg_extension`` for the extension.
    - If present → return None (codec can register).
    - If absent + ``read_only=True`` → refuse rather than mutate.
    - If absent + writable → ``CREATE EXTENSION IF NOT EXISTS vector``;
      report the error verbatim if the role lacks CREATE privilege.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        row = cur.fetchone()
    if row is not None:
        return None

    if read_only:
        return Disconnected(
            reason=DisconnectReason.BACKEND_REPORTED_UNAVAILABLE,
            since=_now_utc(),
            detail=(
                "pgvector extension missing and read_only=true; "
                "operator must `CREATE EXTENSION vector` separately"
            ),
        )

    try:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        conn.commit()
    except Exception as exc:
        with contextlib.suppress(Exception):
            conn.rollback()
        return Disconnected(
            reason=DisconnectReason.BACKEND_REPORTED_UNAVAILABLE,
            since=_now_utc(),
            detail=(
                f"could not CREATE EXTENSION vector: {exc} "
                f"(operator-level fix: GRANT CREATE on database, or "
                f"create the extension as a superuser once)"
            ),
        )
    return None


def _probe_schema(conn, *, schema: str) -> _SchemaProbe:
    """Inspect the configured schema for Gungnir-shape tables.

    Read-only: never DDLs anything; only reads ``information_schema`` and
    ``pg_attribute`` / ``pg_type``. Per ADR 0010 §2.2.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = %s
              AND table_name IN ('documents', 'chunks', 'episodes')
            """,
            (schema,),
        )
        present = {row[0] for row in cur.fetchall()}

        embedding_dim: int | None = None
        if "chunks" in present:
            cur.execute(
                """
                SELECT a.atttypmod
                FROM pg_attribute a
                JOIN pg_class c ON c.oid = a.attrelid
                JOIN pg_namespace n ON n.oid = c.relnamespace
                JOIN pg_type t ON t.oid = a.atttypid
                WHERE n.nspname = %s
                  AND c.relname = 'chunks'
                  AND a.attname = 'embedding'
                  AND t.typname = 'vector'
                """,
                (schema,),
            )
            row = cur.fetchone()
            if row is not None and row[0] is not None and row[0] >= 0:
                # pgvector stores the configured dimension in atttypmod.
                embedding_dim = int(row[0])

    return _SchemaProbe(
        documents_present="documents" in present,
        chunks_present="chunks" in present,
        episodes_present="episodes" in present,
        embedding_dim=embedding_dim,
    )


def _apply_episodes_only(conn, *, schema: str) -> None:
    """Create only the episodes table, leaving discovered tables alone."""
    safe = _quote_ident(schema)
    with conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {safe}.episodes (
                id                bigserial PRIMARY KEY,
                operator_input    text NOT NULL,
                ember_reply       text NOT NULL,
                cited_chunk_ids   jsonb NOT NULL DEFAULT '[]'::jsonb,
                funi_model        text NOT NULL DEFAULT '',
                well_disconnected boolean NOT NULL DEFAULT false,
                started_at        timestamptz,
                completed_at      timestamptz
            )
            """
        )
    conn.commit()


# --------------------------------------------------------------------- #
# Module-level open() for the registry                                  #
# --------------------------------------------------------------------- #


def open(config: BrunnrConfig) -> PgVectorBrunnr | Disconnected:
    return PgVectorBrunnr.open(config)


# --------------------------------------------------------------------- #
# Helpers                                                                #
# --------------------------------------------------------------------- #


def _classify_operational_error(
    exc: Exception,
) -> Disconnected:
    """Map a ``psycopg.OperationalError`` to a typed Disconnected.

    Per ADR 0010 §2.8 — Strengr's reconnect policy depends on the
    distinction between recoverable (CONN_REFUSED / TIMEOUT) and
    non-recoverable (AUTH_FAILED / CONFIG_INVALID) reasons.

    **Sqlstate-first** (hardening pass): PostgreSQL ships stable
    sqlstate codes that don't change wording across major versions.
    The string-match fallbacks below cover libpq paths that don't
    populate sqlstate (TCP failure before the wire protocol speaks,
    DNS resolution, etc.).
    """
    sqlstate = getattr(exc, "sqlstate", None)
    detail = str(exc)

    # Sqlstate-first classification — stable across psycopg + Postgres
    # versions.
    if sqlstate in _AUTH_SQLSTATES:
        return Disconnected(
            reason=DisconnectReason.AUTH_FAILED,
            since=_now_utc(),
            detail=detail,
        )
    if sqlstate in _CONN_REFUSED_SQLSTATES:
        return Disconnected(
            reason=DisconnectReason.CONN_REFUSED,
            since=_now_utc(),
            detail=detail,
        )

    # Fallback to message-based heuristics for pre-handshake failures
    # (TCP refused, DNS unresolved, timeout) where libpq doesn't
    # populate sqlstate.
    msg = detail.lower()
    if _TIMEOUT_HINT in msg:
        return Disconnected(
            reason=DisconnectReason.TIMEOUT,
            since=_now_utc(),
            detail=detail,
        )
    if "could not translate host name" in msg or "name or service not known" in msg:
        return Disconnected(
            reason=DisconnectReason.DNS_FAILURE,
            since=_now_utc(),
            detail=detail,
        )
    if "connection refused" in msg or "could not connect" in msg:
        return Disconnected(
            reason=DisconnectReason.CONN_REFUSED,
            since=_now_utc(),
            detail=detail,
        )
    return Disconnected(
        reason=DisconnectReason.UNKNOWN,
        since=_now_utc(),
        detail=detail,
    )


def _row_to_document(row: tuple) -> Document:
    try:
        metadata = json.loads(row[5]) if row[5] else {}
    except json.JSONDecodeError as exc:
        raise SchemaError(
            f"document {row[0]} has invalid metadata json: {exc}"
        ) from exc
    return Document(
        source=row[1],
        title=row[2],
        content_type=row[3],
        hash=row[4] or "",
        metadata=metadata,
        ingested_at=row[6],
        id=row[0],
    )


__all__ = [
    "PgVectorBrunnr",
    "open",
    "render_schema_sql",
]

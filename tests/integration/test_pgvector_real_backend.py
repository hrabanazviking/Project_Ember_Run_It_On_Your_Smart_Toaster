"""PgVectorBrunnr against real Postgres — marked ``requires_postgres``.

Two acceptance flows ride this file:

1. **Container** (``requires_podman``) — a fresh ephemeral
   ``pgvector/pgvector:pg18`` container exercises the write path:
   schema apply, document + chunk upsert, vector/text/hybrid search,
   close-then-reopen schema probe, read-only refusal.

2. **Live Gungnir** (``requires_gungnir``) — read-only retrieval
   against Volmarr's real Knowledge corpus on the tailnet. Confirms
   schema-probe semantics on existing tables, embedding-dim validation,
   and hybrid search RRF against the live ~37k-chunk index.

Neither flow runs in CI by default. Use::

    pytest -m requires_podman tests/integration/test_pgvector_real_backend.py
    pytest -m requires_gungnir tests/integration/test_pgvector_real_backend.py

The Phase-12 ADR (``docs/decisions/0010-pgvector-brunnr.md``) names this
file as the live-fire acceptance for Phase 13.
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import time
import uuid
from contextlib import closing
from pathlib import Path

import psycopg
import pytest

from ember.schemas.chunks import Chunk, Document
from ember.schemas.config import (
    BrunnrBackend,
    BrunnrConfig,
    PgVectorConfig,
)
from ember.schemas.errors import BrunnrError, Disconnected, DisconnectReason
from ember.well.brunnr.pgvector import PgVectorBrunnr
from ember.well.brunnr.pgvector import open as pgvector_open

# Skip the whole module if the pgvector extra isn't installed — the
# adapter would just return Disconnected, but the per-test fixtures
# below want real connections.
pytest.importorskip("psycopg")
pytest.importorskip("pgvector")


# --------------------------------------------------------------------- #
# Common helpers                                                         #
# --------------------------------------------------------------------- #


def _tcp_reachable(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with closing(socket.create_connection((host, port), timeout=timeout)):
            return True
    except OSError:
        return False


def _make_secret_file(tmp_path: Path, body: str) -> Path:
    """Write a mode-0o600 file the secret resolver will accept."""
    path = tmp_path / "well.password"
    path.write_text(body, encoding="utf-8")
    path.chmod(0o600)
    return path


# --------------------------------------------------------------------- #
# Container fixture (podman, write path)                                #
# --------------------------------------------------------------------- #


_CONTAINER_NAME = "ember-pgvector-test"
_CONTAINER_IMAGE = "docker.io/pgvector/pgvector:pg18"
_CONTAINER_PORT = 55432
_CONTAINER_PASSWORD = "ember-test-pw"  # local ephemeral test container


def _podman_available() -> bool:
    return shutil.which("podman") is not None


@pytest.fixture(scope="module")
def pg_container():
    """Spin up a one-shot pgvector container for the module's write tests.

    Tears down on exit so repeated test runs start clean. The container
    binds to 127.0.0.1 only — never tailnet-exposed.
    """
    if not _podman_available():
        pytest.skip("podman not installed")

    # Tear down any leftover from a prior crashed run.
    subprocess.run(
        ["podman", "rm", "-f", _CONTAINER_NAME],
        check=False, capture_output=True,
    )

    proc = subprocess.run(
        [
            "podman", "run", "-d",
            "--name", _CONTAINER_NAME,
            "-e", f"POSTGRES_PASSWORD={_CONTAINER_PASSWORD}",
            "-p", f"127.0.0.1:{_CONTAINER_PORT}:5432",
            _CONTAINER_IMAGE,
        ],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        pytest.skip(f"podman run failed: {proc.stderr.strip()}")

    try:
        # Wait for Postgres to accept connections.
        deadline = time.time() + 30
        while time.time() < deadline:
            ready = subprocess.run(
                ["podman", "exec", _CONTAINER_NAME, "pg_isready", "-U", "postgres"],
                capture_output=True, check=False,
            )
            if ready.returncode == 0:
                break
            time.sleep(0.5)
        else:
            pytest.skip("container Postgres never became ready")

        yield {
            "url": (
                f"postgresql://postgres@127.0.0.1:{_CONTAINER_PORT}/postgres"
            ),
            "password": _CONTAINER_PASSWORD,
        }
    finally:
        subprocess.run(
            ["podman", "rm", "-f", _CONTAINER_NAME],
            check=False, capture_output=True,
        )


def _fresh_brunnr_in_container(
    pg_container: dict, tmp_path: Path, *, embedding_dim: int = 8,
    read_only: bool = False,
) -> PgVectorBrunnr:
    """Open a PgVectorBrunnr against the container, with a unique
    schema name per test so writes don't collide."""
    schema = f"ember_{uuid.uuid4().hex[:8]}"
    cfg = BrunnrConfig(
        backend=BrunnrBackend.PGVECTOR,
        embedding_dim=embedding_dim,
        sqlite_vec=None,
        pgvector=PgVectorConfig(
            url=pg_container["url"],
            secret_ref=_make_secret_file(tmp_path, pg_container["password"]),
            use_keyring=False,
            schema=schema,
            read_only=read_only,
        ),
    )
    # Pre-create the schema (the adapter's DDL has CREATE TABLE IF NOT
    # EXISTS, but the schema itself must exist).
    with psycopg.connect(
        pg_container["url"], password=pg_container["password"],
    ) as setup:
        with setup.cursor() as cur:
            cur.execute(f'CREATE SCHEMA "{schema}"')
        setup.commit()

    result = pgvector_open(cfg)
    if isinstance(result, Disconnected):
        raise AssertionError(f"open() returned Disconnected: {result}")
    return result


# --------------------------------------------------------------------- #
# Container flow — write path                                           #
# --------------------------------------------------------------------- #


@pytest.mark.requires_podman
@pytest.mark.requires_postgres
class TestContainerWritePath:
    """The ephemeral-container exercise of the full write path."""

    def test_open_against_empty_schema_applies_ddl(
        self, pg_container, tmp_path,
    ) -> None:
        brunnr = _fresh_brunnr_in_container(pg_container, tmp_path)
        try:
            stats = brunnr.count()
            assert stats.documents == 0
            assert stats.chunks == 0
            assert stats.embedded_chunks == 0
        finally:
            brunnr.close()

    def test_round_trip_document_and_chunks(
        self, pg_container, tmp_path,
    ) -> None:
        brunnr = _fresh_brunnr_in_container(pg_container, tmp_path)
        try:
            doc = Document(
                source="test/odin.md",
                title="Odin notes",
                content_type="md",
                hash=f"hash-{uuid.uuid4().hex}",
                metadata={"author": "volmarr"},
            )
            doc_id = brunnr.add_document(doc)
            assert doc_id > 0

            # add_document is idempotent on hash collision.
            assert brunnr.add_document(doc) == doc_id

            chunks = [
                Chunk(
                    document_id=doc_id,
                    chunk_index=0,
                    text="Odin sacrificed an eye for wisdom at Mimir's well.",
                    embedding=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8),
                    char_start=0,
                    char_end=49,
                ),
                Chunk(
                    document_id=doc_id,
                    chunk_index=1,
                    text="The Allfather rules from Hlidskjalf in Valhalla.",
                    embedding=(0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9),
                    char_start=50,
                    char_end=98,
                ),
            ]
            ids = brunnr.add_chunks(chunks)
            assert len(ids) == 2
            assert all(i > 0 for i in ids)

            stats = brunnr.count()
            assert stats.documents == 1
            assert stats.chunks == 2
            assert stats.embedded_chunks == 2
            assert stats.size_bytes > 0
        finally:
            brunnr.close()

    def test_has_document_returns_id_after_insert(
        self, pg_container, tmp_path,
    ) -> None:
        brunnr = _fresh_brunnr_in_container(pg_container, tmp_path)
        try:
            content_hash = f"unique-{uuid.uuid4().hex}"
            doc_id = brunnr.add_document(Document(
                source="dup.md", title="dup", content_type="md",
                hash=content_hash, metadata={},
            ))
            assert brunnr.has_document(content_hash) == doc_id
            assert brunnr.has_document(f"absent-{uuid.uuid4().hex}") is None
        finally:
            brunnr.close()

    def test_dim_mismatch_in_add_chunks_rolls_back(
        self, pg_container, tmp_path,
    ) -> None:
        brunnr = _fresh_brunnr_in_container(pg_container, tmp_path)
        try:
            doc_id = brunnr.add_document(Document(
                source="x.md", title="x", content_type="md",
                hash=f"hash-{uuid.uuid4().hex}", metadata={},
            ))
            bad_chunk = Chunk(
                document_id=doc_id, chunk_index=0,
                text="will rollback",
                embedding=(0.1, 0.2, 0.3),  # only 3 floats; configured dim is 8
                char_start=0, char_end=13,
            )
            with pytest.raises(BrunnrError, match=r"dim 3.*dim 8"):
                brunnr.add_chunks([bad_chunk])

            # The transaction must have rolled back — no chunks land.
            stats = brunnr.count()
            assert stats.chunks == 0
        finally:
            brunnr.close()

    def test_vector_search_returns_nearest_first(
        self, pg_container, tmp_path,
    ) -> None:
        brunnr = _fresh_brunnr_in_container(pg_container, tmp_path)
        try:
            doc_id = brunnr.add_document(Document(
                source="v.md", title="v", content_type="md",
                hash=f"hash-{uuid.uuid4().hex}", metadata={},
            ))
            brunnr.add_chunks([
                Chunk(
                    document_id=doc_id, chunk_index=0,
                    text="closest", embedding=(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                ),
                Chunk(
                    document_id=doc_id, chunk_index=1,
                    text="middle", embedding=(0.7, 0.7, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                ),
                Chunk(
                    document_id=doc_id, chunk_index=2,
                    text="far", embedding=(0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                ),
            ])

            hits = brunnr.vector_search(
                [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], k=3,
            )
            assert len(hits) == 3
            # Nearest first (highest score, since score = 1 - cosine_distance).
            assert hits[0].text == "closest"
            assert hits[0].score >= hits[1].score >= hits[2].score
        finally:
            brunnr.close()

    def test_text_search_uses_generated_tsv(
        self, pg_container, tmp_path,
    ) -> None:
        brunnr = _fresh_brunnr_in_container(pg_container, tmp_path)
        try:
            doc_id = brunnr.add_document(Document(
                source="t.md", title="t", content_type="md",
                hash=f"hash-{uuid.uuid4().hex}", metadata={},
            ))
            brunnr.add_chunks([
                Chunk(
                    document_id=doc_id, chunk_index=0,
                    text="Odin is the Allfather of the Norse pantheon.",
                    embedding=tuple([0.1] * 8),
                ),
                Chunk(
                    document_id=doc_id, chunk_index=1,
                    text="Trees grow tall in the spring.",
                    embedding=tuple([0.1] * 8),
                ),
            ])

            hits = brunnr.text_search("Odin Allfather", k=5)
            assert hits
            assert "Odin" in hits[0].text

            # Empty query → empty list, consistent with sqlite_vec.
            assert brunnr.text_search("", k=5) == []
            assert brunnr.text_search("   ", k=5) == []
        finally:
            brunnr.close()

    def test_hybrid_search_rrf_fuses_both_signals(
        self, pg_container, tmp_path,
    ) -> None:
        brunnr = _fresh_brunnr_in_container(pg_container, tmp_path)
        try:
            doc_id = brunnr.add_document(Document(
                source="h.md", title="h", content_type="md",
                hash=f"hash-{uuid.uuid4().hex}", metadata={},
            ))
            brunnr.add_chunks([
                Chunk(
                    document_id=doc_id, chunk_index=0,
                    text="Odin sacrificed his eye for wisdom.",
                    embedding=(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                ),
                Chunk(
                    document_id=doc_id, chunk_index=1,
                    text="The Allfather hung from Yggdrasil for nine nights.",
                    embedding=(0.9, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                ),
                Chunk(
                    document_id=doc_id, chunk_index=2,
                    text="Frigg is the queen of the Aesir.",
                    embedding=(0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
                ),
            ])

            hits = brunnr.hybrid_search(
                [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                "Odin Allfather wisdom",
                k=2,
            )
            # Top-2 should both reference Odin-side chunks; Frigg's
            # chunk doesn't match either signal strongly.
            assert len(hits) == 2
            texts = " ".join(h.text for h in hits)
            assert "Odin" in texts or "Allfather" in texts
            assert "Frigg" not in texts
        finally:
            brunnr.close()

    def test_close_then_reopen_finds_existing_tables(
        self, pg_container, tmp_path,
    ) -> None:
        """Schema-probe path: second open() must NOT re-DDL — it must
        find the tables and reuse them."""
        schema = f"reopen_{uuid.uuid4().hex[:8]}"

        # First open — applies DDL.
        cfg = BrunnrConfig(
            backend=BrunnrBackend.PGVECTOR,
            embedding_dim=8,
            sqlite_vec=None,
            pgvector=PgVectorConfig(
                url=pg_container["url"],
                secret_ref=_make_secret_file(tmp_path, pg_container["password"]),
                use_keyring=False,
                schema=schema,
            ),
        )
        # Pre-create schema.
        with psycopg.connect(pg_container["url"], password=pg_container["password"]) as setup:
            with setup.cursor() as cur:
                cur.execute(f'CREATE SCHEMA "{schema}"')
            setup.commit()

        first = pgvector_open(cfg)
        assert isinstance(first, PgVectorBrunnr)
        doc_id = first.add_document(Document(
            source="reopen.md", title="r", content_type="md",
            hash=f"hash-{uuid.uuid4().hex}", metadata={},
        ))
        first.close()

        # Second open — schema-probe path. Tables exist, dim matches.
        second = pgvector_open(cfg)
        assert isinstance(second, PgVectorBrunnr)
        try:
            # Data persisted across reopen.
            assert second.count().documents == 1
            doc = second.get_document(doc_id)
            assert doc.source == "reopen.md"
        finally:
            second.close()

    def test_open_with_mismatched_embedding_dim_refuses(
        self, pg_container, tmp_path,
    ) -> None:
        """Schema-probe finds tables at dim X; config says dim Y → refuse."""
        schema = f"dimcheck_{uuid.uuid4().hex[:8]}"

        # Apply schema at dim=8.
        cfg_at_8 = BrunnrConfig(
            backend=BrunnrBackend.PGVECTOR,
            embedding_dim=8,
            sqlite_vec=None,
            pgvector=PgVectorConfig(
                url=pg_container["url"],
                secret_ref=_make_secret_file(tmp_path, pg_container["password"]),
                use_keyring=False,
                schema=schema,
            ),
        )
        with psycopg.connect(pg_container["url"], password=pg_container["password"]) as setup:
            with setup.cursor() as cur:
                cur.execute(f'CREATE SCHEMA "{schema}"')
            setup.commit()

        first = pgvector_open(cfg_at_8)
        assert isinstance(first, PgVectorBrunnr)
        first.close()

        # Now try to open at dim=16 — the probe must refuse.
        cfg_at_16 = BrunnrConfig(
            backend=BrunnrBackend.PGVECTOR,
            embedding_dim=16,
            sqlite_vec=None,
            pgvector=PgVectorConfig(
                url=pg_container["url"],
                secret_ref=_make_secret_file(tmp_path, pg_container["password"]),
                use_keyring=False,
                schema=schema,
            ),
        )
        result = pgvector_open(cfg_at_16)
        assert isinstance(result, Disconnected)
        assert result.reason is DisconnectReason.BACKEND_REPORTED_UNAVAILABLE
        detail = result.detail or ""
        assert "dim 8" in detail
        assert "embedding_dim is 16" in detail

    def test_read_only_refuses_writes(
        self, pg_container, tmp_path,
    ) -> None:
        """ADR 0010 §4 — opt-in write-block for shared Wells."""
        # First, apply schema in writable mode.
        schema = f"ro_{uuid.uuid4().hex[:8]}"
        password = pg_container["password"]
        with psycopg.connect(pg_container["url"], password=password) as setup:
            with setup.cursor() as cur:
                cur.execute(f'CREATE SCHEMA "{schema}"')
            setup.commit()

        cfg_writable = BrunnrConfig(
            backend=BrunnrBackend.PGVECTOR,
            embedding_dim=8,
            sqlite_vec=None,
            pgvector=PgVectorConfig(
                url=pg_container["url"],
                secret_ref=_make_secret_file(tmp_path, password),
                use_keyring=False,
                schema=schema,
            ),
        )
        primer = pgvector_open(cfg_writable)
        assert isinstance(primer, PgVectorBrunnr)
        primer.close()

        # Now reopen read-only.
        cfg_ro = BrunnrConfig(
            backend=BrunnrBackend.PGVECTOR,
            embedding_dim=8,
            sqlite_vec=None,
            pgvector=PgVectorConfig(
                url=pg_container["url"],
                secret_ref=_make_secret_file(tmp_path, password),
                use_keyring=False,
                schema=schema,
                read_only=True,
            ),
        )
        brunnr = pgvector_open(cfg_ro)
        assert isinstance(brunnr, PgVectorBrunnr)
        try:
            with pytest.raises(BrunnrError, match="ADR 0010"):
                brunnr.add_document(Document(
                    source="nope.md", title="nope", content_type="md",
                    hash="nope", metadata={},
                ))
        finally:
            brunnr.close()


# --------------------------------------------------------------------- #
# Live Gungnir flow — read-only retrieval                               #
# --------------------------------------------------------------------- #


_GUNGNIR_HOST = "100.67.240.22"
_GUNGNIR_PORT = 5432
_GUNGNIR_URL = f"postgresql://volmarr@{_GUNGNIR_HOST}:{_GUNGNIR_PORT}/knowledge"


def _gungnir_reachable() -> bool:
    return _tcp_reachable(_GUNGNIR_HOST, _GUNGNIR_PORT, timeout=1.0)


def _gungnir_secret() -> str | None:
    """Read the password out of ~/.pgpass, never from the test source.

    Falls back to ``EMBER_WELL_PASSWORD`` if pgpass isn't present (the
    CI shape).
    """
    pgpass = Path.home() / ".pgpass"
    if pgpass.is_file():
        for line in pgpass.read_text(encoding="utf-8").splitlines():
            parts = line.split(":")
            if len(parts) == 5 and parts[2] == "knowledge" and parts[3] == "volmarr":
                return parts[4]
    return os.environ.get("EMBER_WELL_PASSWORD")


@pytest.fixture(scope="module")
def gungnir_brunnr(tmp_path_factory: pytest.TempPathFactory) -> PgVectorBrunnr:
    if not _gungnir_reachable():
        pytest.skip(f"Gungnir not reachable at {_GUNGNIR_HOST}:{_GUNGNIR_PORT}")
    secret = _gungnir_secret()
    if not secret:
        pytest.skip("Gungnir secret not available (no pgpass + no env var)")

    tmp_path = tmp_path_factory.mktemp("gungnir-secrets")
    cfg = BrunnrConfig(
        backend=BrunnrBackend.PGVECTOR,
        embedding_dim=768,  # Gungnir's actual chunks.embedding dim
        sqlite_vec=None,
        pgvector=PgVectorConfig(
            url=_GUNGNIR_URL,
            secret_ref=_make_secret_file(tmp_path, secret),
            use_keyring=False,
            schema="public",
            read_only=True,  # The iron warning: never DDL into Gungnir.
        ),
    )
    result = pgvector_open(cfg)
    if isinstance(result, Disconnected):
        pytest.skip(f"Gungnir open failed: {result.reason.value} — {result.detail}")
    yield result
    result.close()


@pytest.mark.requires_gungnir
@pytest.mark.requires_postgres
class TestGungnirRetrieval:
    """Read-only retrieval against the live Gungnir knowledge corpus."""

    def test_schema_probe_finds_existing_tables(
        self, gungnir_brunnr: PgVectorBrunnr,
    ) -> None:
        stats = gungnir_brunnr.count()
        # Gungnir is the canonical Well — real numbers, not fixtures.
        assert stats.documents > 0
        assert stats.chunks > 1000
        assert stats.embedded_chunks > 0
        assert stats.size_bytes > 0

    def test_text_search_against_real_norse_corpus(
        self, gungnir_brunnr: PgVectorBrunnr,
    ) -> None:
        hits = gungnir_brunnr.text_search("Odin Allfather", k=5)
        # The Norse corpus is large; some matches should surface.
        assert hits
        # The titles or text should mention Norse content.
        assert any(
            ("odin" in (h.text or "").lower())
            or ("odin" in (h.document_title or "").lower())
            for h in hits
        )

    def test_hybrid_search_with_real_embedding_dim(
        self, gungnir_brunnr: PgVectorBrunnr,
    ) -> None:
        # Use a zero-vector query — vector_search returns *some* set
        # ordered by distance; combined with text the fusion still works.
        qvec = [0.0] * 768
        hits = gungnir_brunnr.hybrid_search(qvec, "wisdom runes Norse", k=5)
        assert hits  # RRF must return *something* against a 37k-chunk corpus.

    def test_read_only_refuses_writes_against_gungnir(
        self, gungnir_brunnr: PgVectorBrunnr,
    ) -> None:
        """The iron warning made mechanical: Ember pointed at Gungnir
        does NOT write to documents or chunks."""
        with pytest.raises(BrunnrError, match="ADR 0010"):
            gungnir_brunnr.add_document(Document(
                source="must-not-write", title="x", content_type="md",
                hash=f"never-{uuid.uuid4().hex}", metadata={},
            ))

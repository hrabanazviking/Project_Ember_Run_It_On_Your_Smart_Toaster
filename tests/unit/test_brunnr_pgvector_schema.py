"""ADR 0010 §2.2-§2.4 — schema-DDL shape, identifier quoting, registry.

These tests don't require Postgres; they assert on the SQL the adapter
would issue, plus the failure shape when the optional pgvector deps
aren't installed.
"""

from __future__ import annotations

import builtins
from datetime import UTC, datetime
from pathlib import Path

import pytest

from ember.schemas.config import (
    BrunnrBackend,
    BrunnrConfig,
    PgVectorConfig,
)
from ember.schemas.errors import BrunnrError, Disconnected, DisconnectReason
from ember.well.brunnr import handle as brunnr_handle
from ember.well.brunnr.pgvector import PgVectorBrunnr
from ember.well.brunnr.pgvector import open as pgvector_open
from ember.well.brunnr.pgvector.adapter import (
    _classify_operational_error,
    render_schema_sql,
)

# --------------------------------------------------------------------- #
# render_schema_sql                                                     #
# --------------------------------------------------------------------- #


def test_render_substitutes_embedding_dim_and_schema() -> None:
    out = render_schema_sql(embedding_dim=768, schema="public")
    # No unsubstituted braces.
    assert "{embedding_dim}" not in out
    assert "{schema}" not in out
    # Vector dim landed.
    assert "vector(768)" in out
    # Schema landed (quoted).
    assert '"public".chunks' in out or '"public".documents' in out


def test_render_includes_episodes_table() -> None:
    out = render_schema_sql(embedding_dim=384, schema="public")
    assert "episodes" in out


def test_render_creates_pgvector_extension() -> None:
    out = render_schema_sql(embedding_dim=768, schema="public")
    assert "CREATE EXTENSION IF NOT EXISTS vector" in out


def test_render_creates_hnsw_cosine_index() -> None:
    out = render_schema_sql(embedding_dim=768, schema="public")
    assert "hnsw" in out
    assert "vector_cosine_ops" in out


def test_render_uses_generated_tsv_column() -> None:
    """ADR 0010 §2.7 — tsv is GENERATED, no trigger needed."""
    out = render_schema_sql(embedding_dim=768, schema="public")
    assert "tsv " in out
    assert "GENERATED ALWAYS AS" in out
    assert "to_tsvector('english', text)" in out


def test_render_handles_custom_schema_name() -> None:
    out = render_schema_sql(embedding_dim=256, schema="ember")
    assert '"ember"' in out
    assert '"public"' not in out


def test_render_quotes_schema_with_double_quote() -> None:
    """Schema names with embedded quotes are escaped (no SQL injection)."""
    out = render_schema_sql(embedding_dim=768, schema='evil"name')
    assert '"evil""name"' in out


def test_render_refuses_schema_with_nul_byte() -> None:
    with pytest.raises(BrunnrError, match="NUL byte"):
        render_schema_sql(embedding_dim=768, schema="bad\x00name")


# --------------------------------------------------------------------- #
# Registry — open() dispatch                                            #
# --------------------------------------------------------------------- #


def test_registry_dispatches_pgvector_backend(tmp_path: Path) -> None:
    """``BrunnrBackend.PGVECTOR`` reaches the pgvector adapter — not the
    registry's "backend not implemented" fallback.

    The actual reason depends on whether the pgvector extra is installed
    on the test host (BACKEND_REPORTED_UNAVAILABLE if not; AUTH_FAILED
    if installed but no secret). Either is fine — what matters is that
    we landed in the adapter, not in the registry fallback.
    """
    config = BrunnrConfig(
        backend=BrunnrBackend.PGVECTOR,
        embedding_dim=768,
        sqlite_vec=None,
        pgvector=PgVectorConfig(
            url="postgresql://nouser@127.0.0.1:1/nope",
            secret_ref=tmp_path / "missing.pw",
            use_keyring=False,
        ),
    )
    result = brunnr_handle.open(config)
    assert isinstance(result, Disconnected)
    # Registry fallback would mention "not implemented in this build" —
    # adapter reach means a different, more specific reason.
    assert "not implemented" not in (result.detail or "")
    assert result.reason in {
        DisconnectReason.AUTH_FAILED,
        DisconnectReason.BACKEND_REPORTED_UNAVAILABLE,
    }


def test_pgvector_open_without_psycopg_returns_disconnected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    """When the pgvector extra isn't installed, ``open()`` returns
    ``Disconnected(BACKEND_REPORTED_UNAVAILABLE)`` instead of raising.

    Sim by patching ``builtins.__import__`` to fail for the offending
    module names — same effect as not having them installed.
    """
    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name in {"psycopg", "pgvector", "pgvector.psycopg"}:
            raise ImportError(f"No module named {name!r}")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)

    secret = tmp_path / "well.pw"
    secret.write_text("any-secret", encoding="utf-8")
    secret.chmod(0o600)

    config = BrunnrConfig(
        backend=BrunnrBackend.PGVECTOR,
        embedding_dim=768,
        sqlite_vec=None,
        pgvector=PgVectorConfig(
            url="postgresql://volmarr@localhost/db",
            secret_ref=secret,
            use_keyring=False,
        ),
    )
    result = pgvector_open(config)
    assert isinstance(result, Disconnected)
    assert result.reason is DisconnectReason.BACKEND_REPORTED_UNAVAILABLE
    assert "pgvector extra not installed" in (result.detail or "")
    assert "pip install" in (result.detail or "")


def test_pgvector_open_with_misconfigured_backend_returns_disconnected() -> None:
    """Calling pgvector_open with a non-pgvector backend returns
    CONFIG_INVALID, not a crash."""
    config = BrunnrConfig(
        backend=BrunnrBackend.SQLITE_VEC,  # mismatched
        embedding_dim=768,
    )
    result = pgvector_open(config)
    assert isinstance(result, Disconnected)
    assert result.reason is DisconnectReason.CONFIG_INVALID


def test_pgvector_open_with_missing_pgvector_subconfig_returns_disconnected() -> None:
    config = BrunnrConfig(
        backend=BrunnrBackend.PGVECTOR,
        embedding_dim=768,
        sqlite_vec=None,
        pgvector=None,
    )
    result = pgvector_open(config)
    assert isinstance(result, Disconnected)
    assert result.reason is DisconnectReason.CONFIG_INVALID


# --------------------------------------------------------------------- #
# Adapter shape                                                         #
# --------------------------------------------------------------------- #


def test_adapter_declares_backend_kind_and_protocol_shape() -> None:
    """Static surface check — the Protocol attrs are present without
    needing a live connection."""
    assert PgVectorBrunnr.backend_kind == "pgvector"
    assert PgVectorBrunnr.SCHEMA_VERSION == 1
    # Every BrunnrHandle method is implemented as an instance method on
    # the class — verify presence (we can't construct without a real conn).
    for method in (
        "add_document",
        "add_chunks",
        "add_episode",
        "vector_search",
        "text_search",
        "hybrid_search",
        "get_document",
        "get_chunk",
        "has_document",
        "count",
        "close",
    ):
        assert callable(getattr(PgVectorBrunnr, method)), method


def test_read_only_refusal_message_mentions_adr_section() -> None:
    """Sanity-check the error message points the operator at the ADR."""
    # Construct directly so we don't need a live conn.
    class _StubConn:
        def close(self) -> None:
            return None

    brunnr = PgVectorBrunnr(
        _StubConn(), embedding_dim=768, schema="public", read_only=True,
    )
    with pytest.raises(BrunnrError, match=r"ADR 0010"):
        brunnr._refuse_if_read_only("add_chunks")


# --------------------------------------------------------------------- #
# OperationalError classification                                       #
# --------------------------------------------------------------------- #


class _StubOpError(Exception):
    def __init__(self, msg: str, sqlstate: str | None = None) -> None:
        super().__init__(msg)
        self.sqlstate = sqlstate


def test_classify_auth_failed_sqlstate() -> None:

    exc = _StubOpError("password authentication failed for user", sqlstate="28P01")
    result = _classify_operational_error(exc)
    assert result.reason is DisconnectReason.AUTH_FAILED


def test_classify_timeout_message() -> None:

    exc = _StubOpError("connection timeout expired")
    result = _classify_operational_error(exc)
    assert result.reason is DisconnectReason.TIMEOUT


def test_classify_conn_refused() -> None:

    exc = _StubOpError("could not connect to server: connection refused")
    result = _classify_operational_error(exc)
    assert result.reason is DisconnectReason.CONN_REFUSED


def test_classify_dns_failure() -> None:

    exc = _StubOpError("could not translate host name 'nope' to address")
    result = _classify_operational_error(exc)
    assert result.reason is DisconnectReason.DNS_FAILURE


def test_classify_unknown_falls_through() -> None:

    exc = _StubOpError("very strange error nobody anticipated")
    result = _classify_operational_error(exc)
    assert result.reason is DisconnectReason.UNKNOWN


# --------------------------------------------------------------------- #
# Disconnected carries a recent timestamp                                #
# --------------------------------------------------------------------- #


def test_disconnected_since_is_recent(tmp_path: Path) -> None:
    """Strengr's reconnect policy reads ``since`` — must be a real time."""
    result = pgvector_open(
        BrunnrConfig(
            backend=BrunnrBackend.PGVECTOR,
            embedding_dim=768,
            sqlite_vec=None,
            pgvector=PgVectorConfig(
                url="postgresql://volmarr@localhost/db",
                secret_ref=tmp_path / "missing.pw",
                use_keyring=False,
            ),
        )
    )
    assert isinstance(result, Disconnected)
    now = datetime.now(tz=UTC)
    assert (now - result.since).total_seconds() < 5

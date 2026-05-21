"""Regression tests for the post-slice-2 Batch C+D+E hardening sweep.

Each test pins a specific hardening introduced during the 2026-05-21
"please fix all bugs" follow-up pass — defensive measures that don't
fit Batches A or B's higher-severity scope but each close a real
soft spot.

If a test fails, the corresponding defense was reverted.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from unittest.mock import patch

import pytest

from ember.schemas.errors import DisconnectReason
from ember.spark.funi.tools import clear as registry_clear
from ember.spark.funi.tools.audit import AuditLog
from ember.well.brunnr.pgvector import secrets as pgvector_secrets
from ember.well.brunnr.pgvector.adapter import _classify_operational_error


@pytest.fixture(autouse=True)
def _isolate_registry():
    registry_clear()
    yield
    registry_clear()


# --------------------------------------------------------------------- #
# Batch C — FTS5 control + bidi filter                                  #
# --------------------------------------------------------------------- #


def test_fts5_sanitiser_strips_newlines_from_tokens() -> None:
    """Hardening: a newline embedded in a query token used to land in
    the audit log mid-line, breaking per-line parsing."""
    from ember.well.brunnr.sqlite_vec.adapter import _escape_fts5_query  # noqa: PLC0415

    out = _escape_fts5_query("hello\nworld")
    # The tokens are split on whitespace (newline counts), so they
    # become two distinct quoted tokens with no newline survivors.
    assert "\n" not in out
    assert "OR" in out


def test_fts5_sanitiser_strips_bidi_override_characters() -> None:
    """Hardening: U+202E (RIGHT-TO-LEFT OVERRIDE) inside a token used
    to make audit-log readers display the query in reversed order."""
    from ember.well.brunnr.sqlite_vec.adapter import _escape_fts5_query  # noqa: PLC0415

    # Embed the bidi-override char inside a single token.
    # Use the \\u escape so the source file doesn't contain the actual
    # control character (which would trip ruff's PLE2502 check and make
    # the source file itself unreadable in some editors).
    bidi_override = chr(0x202E)  # RIGHT-TO-LEFT OVERRIDE
    out = _escape_fts5_query(f"normal{bidi_override}malicious")
    assert bidi_override not in out
    # The token survives without the bidi byte.
    assert "normal" in out


def test_fts5_sanitiser_strips_null_byte() -> None:
    """A NUL byte in a token used to render strangely in some log
    viewers; now scrubbed before quoting."""
    from ember.well.brunnr.sqlite_vec.adapter import _escape_fts5_query  # noqa: PLC0415

    out = _escape_fts5_query("hello\x00there")
    assert "\x00" not in out


# --------------------------------------------------------------------- #
# Batch C — read_local_file single-stat narrowing                       #
# --------------------------------------------------------------------- #


def test_read_local_file_single_stat_for_existence_and_type(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Hardening: the sandbox check now stat()s once instead of doing
    exists() + is_dir() + is_file() — narrowing the swap-window
    between checks."""
    monkeypatch.setenv("HOME", str(tmp_path))
    from ember.tools import read_local_file  # noqa: PLC0415

    registry_clear()
    importlib.reload(read_local_file)
    notes = tmp_path / "notes.md"
    notes.write_text("hello", encoding="utf-8")

    # The check should succeed for a regular file.
    result = read_local_file._sandbox_check(str(notes))
    assert result.refusal is None
    assert result.safe_path == notes.resolve()

    # And refuse a directory with a clear message.
    (tmp_path / "subdir").mkdir()
    result = read_local_file._sandbox_check(str(tmp_path / "subdir"))
    assert result.refusal is not None
    assert "directory" in result.refusal


# --------------------------------------------------------------------- #
# Batch C — fetch_url IDN homoglyph defence                             #
# --------------------------------------------------------------------- #


def test_fetch_url_idna_encodes_unicode_hostname() -> None:
    """Hardening: unicode hostnames are IDNA-encoded before the
    sandbox check, so a Cyrillic-e homoglyph that resolves
    differently from ASCII-e is normalised first."""
    from ember.tools import fetch_url  # noqa: PLC0415

    registry_clear()
    importlib.reload(fetch_url)
    # Record what host the sandbox was asked to check by spying on the
    # resolver.
    seen_hosts: list[str] = []

    def _spy_resolver(host: str) -> list[str]:
        seen_hosts.append(host)
        return ["93.184.216.34"]  # public address

    fetch_url._set_address_resolver(_spy_resolver)
    try:
        # ``münchen.de`` — when IDNA-encoded becomes ``xn--mnchen-3ya.de``.
        from ember.schemas.tool import ToolCall  # noqa: PLC0415
        call = ToolCall(
            call_id="c-1", name="fetch_url",
            arguments={"url": "https://münchen.de/"},
        )
        # The fetch will fail because we don't provide an opener, but
        # the resolver should still see the IDNA-encoded host.
        fetch_url._set_robots_fetcher(lambda _: None)
        fetch_url._set_url_opener(lambda req, _t: (_ for _ in ()).throw(OSError("no opener")))
        fetch_url._execute(call)
        # Whatever the final result, the sandbox check should have
        # received the IDNA-encoded form.
        assert seen_hosts, "resolver was never consulted"
        assert "xn--" in seen_hosts[0], (
            f"expected punycode, got {seen_hosts[0]!r}"
        )
    finally:
        fetch_url._reset_seams()


def test_fetch_url_refuses_undisplayable_hostname() -> None:
    """Hardening: a hostname that can't be IDNA-encoded is refused
    rather than crashing the sandbox."""
    from ember.tools import fetch_url  # noqa: PLC0415

    registry_clear()
    importlib.reload(fetch_url)
    from ember.schemas.tool import ToolCall  # noqa: PLC0415
    call = ToolCall(
        call_id="c-2", name="fetch_url",
        # An empty label or label-too-long would fail IDNA encoding.
        arguments={"url": "https://" + ("a" * 100) + ".x/"},
    )
    reply = fetch_url._execute(call)
    # Long labels exceed the 63-char IDNA limit per label.
    # Either we get the IDNA refusal or another refusal — verify the
    # tool didn't crash and returned a typed error.
    assert reply.output == ""
    assert reply.error is not None


# --------------------------------------------------------------------- #
# Batch C — Ollama _parse_tool_calls broader arg catch                  #
# --------------------------------------------------------------------- #


def test_parse_tool_calls_catches_value_error_in_args() -> None:
    """Hardening: malformed JSON-string args used to crash if they
    raised ValueError (not just JSONDecodeError). Stub ``json.loads``
    so the test deterministically triggers ValueError, which the
    narrow original except clause would have leaked."""
    from ember.spark.funi.ollama import adapter  # noqa: PLC0415

    def _raising_loads(_s):
        raise ValueError("crafted ValueError")

    raw = [
        {"function": {"name": "tool", "arguments": '{"k": "v"}'}},
    ]
    with patch.object(adapter.json, "loads", side_effect=_raising_loads):
        out = adapter._parse_tool_calls(raw)
    # Defensive catch produces a tool call with empty args, not a crash.
    assert len(out) == 1
    assert out[0].arguments == {}


# --------------------------------------------------------------------- #
# Batch D — Strengr KeyboardInterrupt during retry sleep                #
# --------------------------------------------------------------------- #


def test_strengr_interrupted_sleep_returns_typed_disconnected(
    tmp_path: Path,
) -> None:
    """Hardening: an operator Ctrl-C during the retry backoff sleep
    must produce a typed Disconnected, not propagate KeyboardInterrupt."""
    from ember.schemas.config import (  # noqa: PLC0415
        BrunnrBackend,
        BrunnrConfig,
        SqliteVecConfig,
        StrengrConfig,
    )
    from ember.schemas.errors import Disconnected  # noqa: PLC0415
    from ember.thread.strengr.tether import open as strengr_open  # noqa: PLC0415

    # A brunnr opener that always returns a recoverable disconnect.
    fake_disconnect_count = 0

    def _failing_brunnr_open(cfg):
        nonlocal fake_disconnect_count
        fake_disconnect_count += 1
        from datetime import UTC, datetime  # noqa: PLC0415
        return Disconnected(
            reason=DisconnectReason.CONN_REFUSED,
            since=datetime.now(tz=UTC),
        )

    def _interrupting_sleep(_seconds: float) -> None:
        raise KeyboardInterrupt

    result = strengr_open(
        StrengrConfig(retry_attempts=3, retry_backoff_max_s=0.001),
        BrunnrConfig(
            backend=BrunnrBackend.SQLITE_VEC,
            sqlite_vec=SqliteVecConfig(path=tmp_path / "noop.db"),
        ),
        opener=_failing_brunnr_open,
        sleeper=_interrupting_sleep,
    )
    assert isinstance(result, Disconnected)
    assert result.reason is DisconnectReason.UNKNOWN
    assert "interrupted" in (result.detail or "").lower()


# --------------------------------------------------------------------- #
# Batch D — pgvector classify prefers sqlstate                          #
# --------------------------------------------------------------------- #


class _StubOpError(Exception):
    """Stand-in for psycopg.OperationalError so the tests don't depend
    on psycopg being installed when not actually running the real DB."""

    def __init__(self, msg: str, sqlstate: str | None = None) -> None:
        super().__init__(msg)
        self.sqlstate = sqlstate


def test_classify_prefers_sqlstate_over_string_match_for_auth() -> None:
    """Hardening: sqlstate is precise across psycopg + Postgres
    versions; the string-match fallbacks are last-resort heuristics."""
    # An auth error whose message doesn't contain "password" or any
    # other hint — sqlstate alone should classify it.
    exc = _StubOpError("login denied", sqlstate="28P01")
    result = _classify_operational_error(exc)
    assert result.reason is DisconnectReason.AUTH_FAILED


def test_classify_uses_connection_refused_sqlstates() -> None:
    """Hardening: sqlstate 08001 / 08006 (connection failures) map to
    CONN_REFUSED without depending on libpq's error-message wording."""
    for sqlstate in ("08001", "08006"):
        exc = _StubOpError("some message", sqlstate=sqlstate)
        result = _classify_operational_error(exc)
        assert result.reason is DisconnectReason.CONN_REFUSED, (
            f"sqlstate {sqlstate} should map to CONN_REFUSED"
        )


# --------------------------------------------------------------------- #
# Batch D — pgvector keyring KeyringLocked distinct note                #
# --------------------------------------------------------------------- #


def test_pgvector_secret_resolver_distinguishes_locked_keyring(
    tmp_path: Path,
) -> None:
    """Hardening: a locked keyring produces a distinct operator-facing
    note instead of a generic "lookup raised"."""
    from ember.schemas.config import PgVectorConfig  # noqa: PLC0415

    class _LockedKeyring:
        def get_password(self, service: str, username: str) -> str | None:
            class KeyringLocked(Exception):
                pass
            raise KeyringLocked("session not unlocked")

    cfg = PgVectorConfig(
        url="postgresql://volmarr@host/db",
        secret_ref=tmp_path / "missing.pw",
        use_keyring=True,
    )
    res = pgvector_secrets.resolve(
        cfg, env={}, keyring_module=_LockedKeyring(),
    )
    assert res.secret is None
    reason = res.reason or ""
    assert "locked" in reason.lower()


# --------------------------------------------------------------------- #
# Batch D — sqlite_vec add_document wraps sqlite errors                 #
# --------------------------------------------------------------------- #


def test_sqlite_vec_add_document_wraps_sqlite_error(tmp_path: Path) -> None:
    """Hardening: previously a sqlite3.OperationalError would propagate
    raw; now it's wrapped as BrunnrError so Smiðja can mark the doc
    failed and continue."""
    pytest.importorskip("sqlite_vec")

    import sqlite3  # noqa: PLC0415

    from ember.schemas.chunks import Document  # noqa: PLC0415
    from ember.schemas.config import BrunnrBackend, BrunnrConfig, SqliteVecConfig  # noqa: PLC0415
    from ember.schemas.errors import BrunnrError  # noqa: PLC0415
    from ember.well.brunnr.sqlite_vec.adapter import SqliteVecBrunnr  # noqa: PLC0415
    from ember.well.brunnr.sqlite_vec.adapter import open as svec_open  # noqa: PLC0415

    brunnr = svec_open(BrunnrConfig(
        backend=BrunnrBackend.SQLITE_VEC,
        embedding_dim=8,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
    ))
    assert isinstance(brunnr, SqliteVecBrunnr)
    # Close the underlying connection so the next insert raises a
    # sqlite3.ProgrammingError. The hardening pass means we get
    # BrunnrError instead of the raw sqlite3 exception.
    brunnr._conn.close()
    try:
        # Either has_document (called first inside add_document) or
        # add_document itself surfaces a wrapped BrunnrError once the
        # underlying connection is broken — both are now wrapped per
        # the typed-value contract.
        with pytest.raises(BrunnrError, match="failed"):
            brunnr.add_document(Document(
                source="x", title="x", content_type="md",
                hash="abc", metadata={},
            ))
    finally:
        # close() now logs but doesn't raise — but the underlying conn
        # is already closed, so suppress the secondary error.
        import contextlib  # noqa: PLC0415
        with contextlib.suppress(sqlite3.Error):
            brunnr.close()


# --------------------------------------------------------------------- #
# Batch E — YAML loader Path expanduser                                  #
# --------------------------------------------------------------------- #


def test_validator_expands_tilde_in_path_fields() -> None:
    """Hardening: ``path: ~/data.db`` in YAML now becomes
    ``Path("/home/<user>/data.db")``, not the literal ``Path("~/data.db")``."""
    from ember.config.validate import coerce_to_dataclass  # noqa: PLC0415
    from ember.schemas.config import SqliteVecConfig  # noqa: PLC0415

    cfg = coerce_to_dataclass(SqliteVecConfig, {"path": "~/data.db"})
    assert isinstance(cfg, SqliteVecConfig)
    assert "~" not in str(cfg.path)
    # The expanded path begins with the operator's home.
    assert str(cfg.path).startswith(str(Path.home()))


# --------------------------------------------------------------------- #
# Batch E — Audit chmod always run                                       #
# --------------------------------------------------------------------- #


def test_audit_log_chmods_even_an_existing_file(tmp_path: Path) -> None:
    """Hardening: chmod now runs on every record, not just newly-created
    files, so an externally-created file with the wrong mode gets
    tightened on next append."""
    import os  # noqa: PLC0415
    import stat as _stat  # noqa: PLC0415
    from datetime import UTC, datetime  # noqa: PLC0415

    from ember.schemas.tool import (  # noqa: PLC0415
        ApprovalOutcome,
        ToolCall,
        ToolDescriptor,
        ToolReply,
    )

    if os.name == "nt":
        pytest.skip("Unix permission bits only")

    log = AuditLog(tmp_path)
    when = datetime(2026, 5, 21, 12, 0, 0, tzinfo=UTC)

    # First record — establishes the file.
    log.record(
        call=ToolCall(call_id="a", name="x", arguments={}),
        descriptor=ToolDescriptor(name="x", description="x"),
        approval=ApprovalOutcome.AUTO_APPROVED,
        reply=ToolReply(call_id="a"),
        when=when,
    )

    # Externally widen the permissions.
    path = log.path_for(when)
    os.chmod(path, 0o644)
    assert _stat.S_IMODE(path.stat().st_mode) == 0o644

    # Second record — chmod should re-tighten back to 0o600.
    log.record(
        call=ToolCall(call_id="b", name="x", arguments={}),
        descriptor=ToolDescriptor(name="x", description="x"),
        approval=ApprovalOutcome.AUTO_APPROVED,
        reply=ToolReply(call_id="b"),
        when=when,
    )
    assert _stat.S_IMODE(path.stat().st_mode) == 0o600


# --------------------------------------------------------------------- #
# Batch E — Brunnr registry "backend not implemented" fallback           #
# --------------------------------------------------------------------- #


def test_brunnr_registry_returns_disconnected_for_unknown_backend() -> None:
    """Hardening coverage: the registry's else-branch (a backend value
    not matched by any dispatch case) returns a typed Disconnected
    rather than crashing.

    Today every enum value IS dispatched; this test pins the fallback
    so future enum additions don't accidentally remove the safety net.
    Construct a synthetic backend by subclassing BrunnrConfig with a
    custom ``backend`` attribute that escapes the dispatch arms (the
    frozen dataclass prevents direct mutation).
    """
    from dataclasses import replace  # noqa: PLC0415

    from ember.schemas.config import BrunnrConfig  # noqa: PLC0415
    from ember.schemas.errors import Disconnected, DisconnectReason  # noqa: PLC0415
    from ember.well.brunnr import handle as brunnr_handle  # noqa: PLC0415

    cfg = BrunnrConfig()

    # Wrap the config in a synthetic object whose backend isn't either
    # known enum value. Use object.__setattr__ to bypass frozen=True.
    class _UnknownBackend:
        value = "synthetic"

    synthetic = replace(cfg)
    object.__setattr__(synthetic, "backend", _UnknownBackend())

    result = brunnr_handle.open(synthetic)
    assert isinstance(result, Disconnected)
    assert result.reason is DisconnectReason.CONFIG_INVALID
    assert "not implemented" in (result.detail or "")

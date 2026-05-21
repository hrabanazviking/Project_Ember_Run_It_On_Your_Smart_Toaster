"""Regression tests for the post-slice-2 Batch-A hardening sweep.

Each test pins a specific bug or defense-in-depth check that was
introduced or tightened during the 2026-05-21 hardening pass. If any
test fails, the corresponding hardening was reverted.

Lives in one file rather than being scattered so a future Auditor can
read the entire hardening posture in one place.
"""

from __future__ import annotations

import importlib
import io
import urllib.error
from pathlib import Path
from unittest.mock import patch

import pytest

from ember.schemas.tool import (
    ApprovalOutcome,
    ApprovalPolicy,
    ToolCall,
    ToolDescriptor,
    ToolError,
)
from ember.spark.funi.tools import clear as registry_clear
from ember.spark.munnr import chat as chat_module
from ember.tools import fetch_url, read_local_file

# --------------------------------------------------------------------- #
# read_local_file hardening                                             #
# --------------------------------------------------------------------- #


@pytest.fixture(autouse=True)
def _isolate_registry():
    registry_clear()
    yield
    registry_clear()


@pytest.fixture
def fake_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("HOME", str(tmp_path))
    return tmp_path


def _call_read(arguments: dict) -> ToolCall:
    return ToolCall(call_id="c-x", name="read_local_file", arguments=arguments)


def test_read_local_file_rejects_whitespace_only_path(fake_home: Path) -> None:
    """Hardening: ``"   "`` previously passed the non-empty check."""
    importlib.reload(read_local_file)
    reply = read_local_file._execute(_call_read({"path": "   "}))
    assert reply.output == ""
    assert "non-empty string" in (reply.error or "")


def test_read_local_file_refuses_when_home_is_filesystem_root(
    fake_home: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Hardening: ``Path.home() == "/"`` would make the sandbox vacuous.

    Simulate by patching ``Path.home`` to return ``/``. The sandbox
    must refuse rather than letting ``/etc/passwd`` through.
    """
    importlib.reload(read_local_file)
    monkeypatch.setattr(
        read_local_file.Path, "home",
        classmethod(lambda cls: Path("/")),
    )
    reply = read_local_file._execute(_call_read({"path": "/etc/hostname"}))
    assert reply.output == ""
    err = reply.error or ""
    assert "filesystem root" in err or "vacuous" in err


def test_read_local_file_toctou_safe_uses_resolved_path_from_check(
    fake_home: Path,
) -> None:
    """Hardening: the executor reads ``_SandboxResult.safe_path`` directly.

    The contract change means ``_sandbox_check`` returns a structured
    result carrying the resolved Path. A successful check populates
    ``safe_path``; a refusal populates ``refusal`` instead. The executor
    never re-resolves between check and read, closing the TOCTOU window.
    """
    importlib.reload(read_local_file)
    notes = fake_home / "notes.md"
    notes.write_text("hello", encoding="utf-8")

    result = read_local_file._sandbox_check(str(notes))
    assert result.refusal is None
    assert result.safe_path is not None
    assert result.safe_path == notes.resolve()


# --------------------------------------------------------------------- #
# fetch_url hardening                                                   #
# --------------------------------------------------------------------- #


def _call_fetch(arguments: dict) -> ToolCall:
    return ToolCall(call_id="c-y", name="fetch_url", arguments=arguments)


def test_fetch_url_refuses_credentials_in_netloc() -> None:
    """Hardening: ``http://user:pass@host/`` previously sent the secret."""
    importlib.reload(fetch_url)
    reply = fetch_url._execute(_call_fetch({"url": "https://alice:hunter2@example.com/"}))
    assert reply.output == ""
    err = reply.error or ""
    assert "credentials" in err
    # The credential must not appear in the error message.
    assert "hunter2" not in err
    assert "alice" not in err or "alice:" not in err


def test_fetch_url_refuses_empty_dns_resolution() -> None:
    """Hardening: empty addresses list previously passed the sandbox."""
    importlib.reload(fetch_url)
    fetch_url._set_address_resolver(lambda _host: [])
    try:
        reply = fetch_url._execute(_call_fetch({"url": "http://nowhere.example/"}))
    finally:
        fetch_url._reset_seams()
    assert reply.output == ""
    assert "resolved" in (reply.error or "")
    assert "no addresses" in (reply.error or "")


def test_fetch_url_default_opener_uses_no_redirect_handler() -> None:
    """Hardening: a 301/302 redirect surfaces as HTTPError, not silently
    followed. The opener's handler chain contains ``_NoRedirectHandler``."""
    importlib.reload(fetch_url)
    handler_classes = {
        type(h).__name__
        for h in fetch_url._DEFAULT_OPENER_INSTANCE.handlers
    }
    assert "_NoRedirectHandler" in handler_classes


def test_fetch_url_no_redirect_handler_raises_http_error_on_301() -> None:
    """The handler must raise HTTPError naming the redirect target."""
    importlib.reload(fetch_url)
    handler = fetch_url._NoRedirectHandler()

    class _FakeReq:
        full_url = "http://example.com/start"

    class _FakeHeaders:
        def get(self, key, default=""):
            return "http://attacker.example/private" if key == "Location" else default

    with pytest.raises(urllib.error.HTTPError) as exc_info:
        handler.http_error_301(_FakeReq(), None, 301, "Moved", _FakeHeaders())
    msg = str(exc_info.value)
    assert "redirect not followed" in msg
    assert "attacker.example" in msg


# --------------------------------------------------------------------- #
# chat.py — safe audit + safe prompt                                    #
# --------------------------------------------------------------------- #


def _descriptor(name: str = "ping") -> ToolDescriptor:
    return ToolDescriptor(
        name=name, description="t",
        required_approval=ApprovalPolicy.PER_CALL,
    )


def _call(name: str = "ping") -> ToolCall:
    return ToolCall(call_id="c-z", name=name, arguments={})


class _ExplodingAudit:
    """Audit log whose record() always raises ToolError."""

    def record(self, **kwargs) -> None:
        raise ToolError("disk full")


def test_safe_audit_swallows_tool_error_but_warns_operator() -> None:
    """Hardening: audit failure must not crash the chat loop."""
    stdout = io.StringIO()
    chat_module._safe_audit(
        _ExplodingAudit(),
        stdout,
        call=_call(),
        descriptor=_descriptor(),
        approval=ApprovalOutcome.AUTO_APPROVED,
        reply=None,
    )
    out = stdout.getvalue()
    assert "audit log write failed" in out
    assert "disk full" in out


class _ExplodingPrompter:
    """Prompter whose prompt() raises OSError (closed stdin)."""

    def prompt(self, descriptor, call) -> str:
        raise OSError("stdin closed")


def test_safe_prompt_returns_n_on_ioerror() -> None:
    """Hardening: a closed-stdin IOError mid-prompt becomes a refusal."""
    stdout = io.StringIO()
    answer = chat_module._safe_prompt(
        _ExplodingPrompter(), stdout, _descriptor(), _call(),
    )
    assert answer == "n"
    assert "prompter failed" in stdout.getvalue()


class _ExplodingFuni:
    runtime_kind = "fake"
    model_id = "fake:explode"

    def complete(self, *a, **kw):  # pragma: no cover
        raise AssertionError("unused")

    def complete_streaming(self, *a, **kw):  # pragma: no cover
        raise AssertionError("unused")
        yield

    def health(self):  # pragma: no cover
        raise AssertionError("unused")

    def close(self) -> None:
        raise RuntimeError("funi close failed")


class _ExplodingBrunnr:
    backend_kind = "fake"
    embedding_dim = 4
    closed = False

    def close(self) -> None:
        self.closed = True


def test_funi_close_failure_does_not_prevent_brunnr_close(tmp_path: Path) -> None:
    """Hardening: each cleanup runs independently in the finally block.

    Drive a single ``run()`` invocation where the funi handle's
    ``close()`` raises; verify the brunnr handle's ``close()`` still
    runs by inspecting a flag.
    """

    from ember.schemas.config import (  # noqa: PLC0415
        BrunnrConfig,
        EmberConfig,
        FuniConfig,
        IdentityConfig,
        SqliteVecConfig,
        StrengrConfig,
    )
    from ember.spark.hjarta import save_identity_atomic  # noqa: PLC0415

    # Use pytest's tmp_path fixture instead of a literal /tmp/ path:
    # /tmp doesn't exist on Windows, and tmp_path also gives each test
    # a unique sandbox so concurrent runs don't collide.
    config_root = tmp_path / "ember-hardening-test"
    config_root.mkdir(exist_ok=True)
    save_identity_atomic(config_root, IdentityConfig())

    exploding_funi = _ExplodingFuni()
    exploding_brunnr = _ExplodingBrunnr()

    cfg = EmberConfig(
        funi=FuniConfig(streaming=False),
        strengr=StrengrConfig(retry_backoff_max_s=0.0),
        brunnr=BrunnrConfig(
            embedding_dim=4,
            sqlite_vec=SqliteVecConfig(path=tmp_path / "never.db"),
        ),
    )

    # /exit immediately, no actual work.
    chat_module.run(
        config=cfg,
        config_root=config_root,
        stdin=io.StringIO("/exit\n"),
        stdout=io.StringIO(),
        funi_opener=lambda _cfg: exploding_funi,
        strengr_opener=lambda _s, _b: exploding_brunnr,
    )

    # exploding_funi.close() raised RuntimeError — but the contextlib
    # suppress means brunnr.close() still ran.
    assert exploding_brunnr.closed is True


# --------------------------------------------------------------------- #
# CLI main — OSError on config load                                     #
# --------------------------------------------------------------------- #


def test_cli_main_surfaces_oserror_as_friendly_message(tmp_path: Path) -> None:
    """Hardening: ``load_ember_config`` raising OSError used to crash with
    a traceback. Now the main dispatcher catches it and writes a
    friendly one-line message."""
    from ember.cli.main import main  # noqa: PLC0415

    stdout = io.StringIO()

    # Build a parser-shaped invocation. Use a non-existent config root
    # under tmp_path so the test works on Windows + macOS + Linux.
    nonexistent_dir = tmp_path / "ember-no-such-dir-for-hardening-test"

    with patch("ember.cli.main.load_ember_config") as fake_load:
        fake_load.side_effect = PermissionError("permission denied")
        rc = main(["--config-root", str(nonexistent_dir), "doctor"], stdout=stdout)

    assert rc == 1
    out = stdout.getvalue()
    assert "Cannot read config" in out
    assert "PermissionError" in out
    # No traceback leaked.
    assert "Traceback" not in out


# --------------------------------------------------------------------- #
# pgvector _quote_ident — control character refusal                      #
# --------------------------------------------------------------------- #


def test_quote_ident_refuses_all_ascii_control_chars() -> None:
    """Hardening: every byte below 0x20 + 0x7f is now refused (was: only NUL)."""
    from ember.well.brunnr.pgvector.adapter import _quote_ident  # noqa: PLC0415

    for codepoint in [*list(range(1, 32)), 127]:
        evil = f"evil{chr(codepoint)}name"
        with pytest.raises(Exception, match="control character"):
            _quote_ident(evil)


def test_quote_ident_accepts_normal_identifiers() -> None:
    """Sanity: hardening didn't break the happy path."""
    from ember.well.brunnr.pgvector.adapter import _quote_ident  # noqa: PLC0415

    assert _quote_ident("public") == '"public"'
    assert _quote_ident("ember_test") == '"ember_test"'
    assert _quote_ident('weird"quoted') == '"weird""quoted"'

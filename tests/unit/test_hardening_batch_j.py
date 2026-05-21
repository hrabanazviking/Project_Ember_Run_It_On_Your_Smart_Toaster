"""Regression tests for Batch J — stub-to-real implementations.

Sweep #7 of 2026-05-21. Auditors found the codebase mostly stub-free,
but flagged FOUR genuine half-shipped features where the schema /
descriptor declared something the code didn't honour. This file pins
the real implementations so future PRs can't regress them.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

import pytest

from ember.schemas.config import (
    EmberConfig,
    LogDestinationKind,
    LogFormat,
    LoggingConfig,
    LoggingDestination,
    LogLevel,
)
from ember.schemas.tool import ToolCall, ToolReply

# --------------------------------------------------------------------- #
# Batch J — LoggingConfig is actually wired                             #
# --------------------------------------------------------------------- #


def test_configure_from_sets_root_level_from_config() -> None:
    """Before Batch J, ``LoggingConfig.level`` was declared but not
    read. Now ``configure_from()`` honours it."""
    from ember import logging as ember_logging  # noqa: PLC0415

    cfg = LoggingConfig(level=LogLevel.DEBUG)
    ember_logging.configure_from(cfg)
    assert logging.getLogger().level == logging.DEBUG

    cfg = LoggingConfig(level=LogLevel.WARNING)
    ember_logging.configure_from(cfg)
    assert logging.getLogger().level == logging.WARNING


def test_configure_from_is_idempotent() -> None:
    """Calling configure_from twice must not stack handlers (or each
    log line would emit N times after N reconfigures)."""
    from ember import logging as ember_logging  # noqa: PLC0415

    cfg = LoggingConfig(level=LogLevel.INFO)
    ember_logging.configure_from(cfg)
    n_first = len(logging.getLogger().handlers)
    ember_logging.configure_from(cfg)
    n_second = len(logging.getLogger().handlers)
    assert n_first == n_second == 1  # the default stderr handler


def test_configure_from_writes_to_configured_file(tmp_path: Path) -> None:
    """File destinations land on disk with explicit encoding (Vow of
    cross-platform encoding hygiene)."""
    from ember import logging as ember_logging  # noqa: PLC0415

    log_path = tmp_path / "ember.log"
    cfg = LoggingConfig(
        level=LogLevel.INFO,
        format=LogFormat.PLAIN,
        destinations=(
            LoggingDestination(kind=LogDestinationKind.FILE, path=log_path),
        ),
    )
    ember_logging.configure_from(cfg)
    logging.getLogger("ember.test").info("hello-from-batch-j")
    # Close + flush all handlers so the file is on disk.
    for h in logging.getLogger().handlers:
        h.flush()
    text = log_path.read_text(encoding="utf-8")
    assert "hello-from-batch-j" in text


def test_configure_from_structured_format_emits_json(
    tmp_path: Path,
) -> None:
    """The STRUCTURED format emits one JSON object per line, parseable
    by jq + log aggregators."""
    import json  # noqa: PLC0415

    from ember import logging as ember_logging  # noqa: PLC0415

    log_path = tmp_path / "ember.jsonl"
    cfg = LoggingConfig(
        level=LogLevel.INFO,
        format=LogFormat.STRUCTURED,
        destinations=(
            LoggingDestination(kind=LogDestinationKind.FILE, path=log_path),
        ),
    )
    ember_logging.configure_from(cfg)
    logging.getLogger("ember.test").info("structured-message")
    for h in logging.getLogger().handlers:
        h.flush()
    line = log_path.read_text(encoding="utf-8").strip().splitlines()[0]
    parsed = json.loads(line)
    assert parsed["message"] == "structured-message"
    assert parsed["logger"] == "ember.test"
    assert parsed["level"] == "INFO"


# --------------------------------------------------------------------- #
# Batch J — Tool timeout actually enforced                              #
# --------------------------------------------------------------------- #


def test_execute_with_timeout_returns_typed_reply_on_overrun() -> None:
    """A tool that takes longer than ``descriptor.timeout_s`` must NOT
    hang the REPL. Before Batch J, the field was on the descriptor but
    unused — tools could run forever."""
    from ember.spark.munnr.chat import _execute_with_timeout  # noqa: PLC0415

    def slow_executor(call: ToolCall) -> ToolReply:
        time.sleep(2.0)
        return ToolReply(call_id=call.call_id, output="finally")

    call = ToolCall(call_id="t-1", name="slowpoke", arguments={})
    t0 = time.monotonic()
    reply = _execute_with_timeout(slow_executor, call, timeout_s=0.2)
    elapsed = time.monotonic() - t0
    assert elapsed < 1.0, f"timeout didn't fire — took {elapsed}s"
    assert reply.error and "timeout" in reply.error.lower()
    assert reply.output == ""


def test_execute_with_timeout_returns_real_reply_when_fast() -> None:
    """Happy path: a fast tool returns the executor's actual reply,
    not a timeout error."""
    from ember.spark.munnr.chat import _execute_with_timeout  # noqa: PLC0415

    def fast_executor(call: ToolCall) -> ToolReply:
        return ToolReply(call_id=call.call_id, output="quick-result")

    reply = _execute_with_timeout(
        fast_executor, ToolCall(call_id="t-2", name="fast", arguments={}),
        timeout_s=5.0,
    )
    assert reply.output == "quick-result"
    assert reply.error is None


def test_execute_with_timeout_translates_executor_exception_to_typed_reply() -> None:
    """An exception inside the executor still produces a typed
    ToolReply — the framework boundary never raises into chat."""
    from ember.spark.munnr.chat import _execute_with_timeout  # noqa: PLC0415

    def raising_executor(call: ToolCall) -> ToolReply:
        raise RuntimeError("crafted in test")

    reply = _execute_with_timeout(
        raising_executor, ToolCall(call_id="t-3", name="boom", arguments={}),
        timeout_s=5.0,
    )
    assert reply.error and "RuntimeError" in reply.error
    assert "crafted in test" in reply.error


# --------------------------------------------------------------------- #
# Batch J — `allow_private_addresses` operator-config default           #
# --------------------------------------------------------------------- #


def test_fetch_url_default_allow_private_starts_off() -> None:
    """Default operator-config default is False (Vow of Sovereignty)."""
    from ember.tools import fetch_url  # noqa: PLC0415

    fetch_url._reset_seams()
    assert fetch_url._ALLOW_PRIVATE_DEFAULT is False


def test_fetch_url_bind_allow_private_default_changes_default() -> None:
    """After bind_allow_private_default(True), a call that omits the
    arg falls back to True (Batch J — previously the field was on the
    config schema but never read)."""
    from ember.tools import fetch_url  # noqa: PLC0415

    try:
        fetch_url.bind_allow_private_default(True)
        assert fetch_url._ALLOW_PRIVATE_DEFAULT is True
    finally:
        fetch_url._reset_seams()
    assert fetch_url._ALLOW_PRIVATE_DEFAULT is False


# --------------------------------------------------------------------- #
# Batch J — MCP doctor: real Funi probe (no longer stubbed to None)     #
# --------------------------------------------------------------------- #


def test_mcp_doctor_probes_funi_for_real() -> None:
    """Batch J replaces the ``"ok": None`` stub with a real call to
    ``funi.health()``. The unit test environment has no live Ollama,
    so we expect ``ok=False`` with a connection-refused-style detail."""
    pytest.importorskip("mcp", reason="MCP extra not installed")
    pytest.importorskip("mcp.server.fastmcp", reason="FastMCP not available")
    from ember.mcp.server import build_server  # noqa: PLC0415

    mcp = build_server(config=EmberConfig(), brunnr=None)
    tool = next(
        t for t in mcp._tool_manager.list_tools()
        if t.name == "doctor"
    )
    out = tool.fn()
    funi = out["realms"]["funi"]
    # The probe ran — `ok` is a real bool now, not None.
    assert isinstance(funi["ok"], bool)
    # Either ok=True with a model_id (Ollama happens to be running) or
    # ok=False with a detail. Both shapes carry useful info.
    if funi["ok"]:
        assert "model_id" in funi
    else:
        assert funi.get("detail")


# --------------------------------------------------------------------- #
# Batch J — sqlite_vec check_same_thread=False                          #
# (enables tool-timeout ThreadPoolExecutor to call into search_well)    #
# --------------------------------------------------------------------- #


def test_sqlite_vec_connection_works_across_threads(tmp_path: Path) -> None:
    """The tool-timeout wrapper runs each tool in a one-shot worker
    thread; sqlite3 connections refuse cross-thread by default. Batch J
    passes check_same_thread=False so this works (SQLite's serialized
    mode is itself thread-safe; the Python wrapper guard is what was
    blocking us)."""
    from concurrent.futures import ThreadPoolExecutor  # noqa: PLC0415

    from ember.schemas.config import BrunnrConfig, SqliteVecConfig  # noqa: PLC0415
    from ember.well.brunnr.sqlite_vec.adapter import SqliteVecBrunnr  # noqa: PLC0415

    cfg = BrunnrConfig(
        embedding_dim=4,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "test.db"),
    )
    handle = SqliteVecBrunnr.open(cfg)
    try:
        # Call count() from the main thread first (baseline).
        baseline = handle.count()
        # Then call it from a worker thread.
        with ThreadPoolExecutor(max_workers=1) as pool:
            result = pool.submit(handle.count).result(timeout=5.0)
        assert result.documents == baseline.documents
        assert result.chunks == baseline.chunks
    finally:
        handle.close()

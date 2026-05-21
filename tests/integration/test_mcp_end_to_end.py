"""End-to-end MCP integration tests using a stub MCP server.

Per ADR-0014. These tests spawn a real stdio MCP subprocess (a small
FastMCP script generated under tmp_path), connect to it via
``MCPClientPool``, register its tools via the bridge, and verify the
full discovery → call → result roundtrip.

Marked ``integration`` (in ``tests/integration/``) so the suite still
runs on environments without the ``mcp`` extra installed — pytest will
skip cleanly when the import fails.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

# Skip the entire module on environments without the mcp extra.
pytest.importorskip("mcp", reason="MCP extra not installed")
pytest.importorskip("mcp.server.fastmcp", reason="FastMCP not available")

from ember.mcp.bridge import register_pool_tools
from ember.mcp.client import MCPClientPool
from ember.schemas.config import MCPConfig, MCPServerSpec
from ember.schemas.tool import ToolCall
from ember.spark.funi.tools import clear as registry_clear
from ember.spark.funi.tools import lookup as registry_lookup


@pytest.fixture(autouse=True)
def _isolate_registry():
    registry_clear()
    yield
    registry_clear()


@pytest.fixture
def stub_server_script(tmp_path: Path) -> Path:
    """Write a tiny FastMCP server to tmp_path and return its path.

    The server exposes two tools:
    - ``echo(text)`` — returns the text
    - ``add(a, b)`` — returns the sum
    """
    script = tmp_path / "stub_mcp_server.py"
    script.write_text(textwrap.dedent("""
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP(name="stub")

        @mcp.tool()
        def echo(text: str) -> str:
            \"\"\"Echo back the input text.\"\"\"
            return f"echoed: {text}"

        @mcp.tool()
        def add(a: int, b: int) -> int:
            \"\"\"Add two numbers.\"\"\"
            return a + b

        if __name__ == "__main__":
            mcp.run(transport="stdio")
    """).lstrip(), encoding="utf-8")
    return script


@pytest.fixture
def stub_pool(stub_server_script: Path):
    """Spin up an MCPClientPool against the stub server. Tears down
    cleanly after the test."""
    cfg = MCPConfig(
        enabled=True,
        startup_timeout_s=15.0,
        call_timeout_s=15.0,
        servers=(
            MCPServerSpec(
                name="stub",
                command=sys.executable,
                args=(str(stub_server_script),),
            ),
        ),
    )
    pool = MCPClientPool(cfg)
    pool.open()
    yield pool
    pool.close()


# --------------------------------------------------------------------- #
# Tool discovery                                                        #
# --------------------------------------------------------------------- #


def test_pool_discovers_stub_server_tools(stub_pool: MCPClientPool) -> None:
    assert "stub" in stub_pool.server_names()
    tool_names = {t.name for t in stub_pool.tools_for("stub")}
    assert "echo" in tool_names
    assert "add" in tool_names


def test_bridge_registers_discovered_tools_with_prefix(
    stub_pool: MCPClientPool,
) -> None:
    specs = (MCPServerSpec(name="stub", command="never"),)
    register_pool_tools(stub_pool, specs)
    assert registry_lookup("mcp__stub__echo") is not None
    assert registry_lookup("mcp__stub__add") is not None


# --------------------------------------------------------------------- #
# Tool call roundtrip                                                   #
# --------------------------------------------------------------------- #


def test_bridged_echo_tool_returns_typed_reply(
    stub_pool: MCPClientPool,
) -> None:
    specs = (MCPServerSpec(name="stub", command="never"),)
    register_pool_tools(stub_pool, specs)
    entry = registry_lookup("mcp__stub__echo")
    assert entry is not None
    _descriptor, executor = entry
    reply = executor(
        ToolCall(call_id="c-1", name="mcp__stub__echo", arguments={"text": "hi"}),
    )
    assert reply.error is None, f"unexpected error: {reply.error}"
    assert "echoed: hi" in reply.output


def test_bridged_add_tool_returns_typed_reply(
    stub_pool: MCPClientPool,
) -> None:
    specs = (MCPServerSpec(name="stub", command="never"),)
    register_pool_tools(stub_pool, specs)
    entry = registry_lookup("mcp__stub__add")
    assert entry is not None
    _, executor = entry
    reply = executor(
        ToolCall(call_id="c-2", name="mcp__stub__add", arguments={"a": 2, "b": 3}),
    )
    assert reply.error is None
    assert "5" in reply.output


# --------------------------------------------------------------------- #
# Lifecycle                                                             #
# --------------------------------------------------------------------- #


def test_pool_ping_returns_true_for_live_server(stub_pool: MCPClientPool) -> None:
    assert stub_pool.ping("stub") is True


def test_pool_ping_returns_false_for_unknown_server(stub_pool: MCPClientPool) -> None:
    assert stub_pool.ping("nonexistent") is False


def test_pool_close_is_idempotent(stub_pool: MCPClientPool) -> None:
    stub_pool.close()
    stub_pool.close()  # second call must not raise

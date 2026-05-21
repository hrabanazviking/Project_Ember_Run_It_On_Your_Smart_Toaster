"""Unit tests for the Ember-as-MCP-server side (ADR-0014).

Verifies ``build_server()`` constructs a FastMCP with the expected tools
+ resources, and that each tool's behavior matches what an MCP client
would see when calling it.

Heavier subprocess + JSON-RPC roundtrip tests live in
tests/integration/.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

# Skip cleanly if the mcp extra is missing.
pytest.importorskip("mcp", reason="MCP extra not installed")
pytest.importorskip("mcp.server.fastmcp", reason="FastMCP not available")

from ember.mcp.server import build_server
from ember.schemas.chunks import BrunnrStats, RetrievalHit
from ember.schemas.config import EmberConfig


@dataclass
class _StubBrunnr:
    """Just enough of BrunnrHandle to make the MCP server's tools work."""

    stats: BrunnrStats
    hits: list[RetrievalHit]
    raises_on_count: bool = False
    raises_on_search: bool = False
    backend_kind: str = "stub"

    def count(self) -> BrunnrStats:
        if self.raises_on_count:
            raise RuntimeError("count exploded")
        return self.stats

    def hybrid_search(
        self, qvec: Any, query: str, k: int,
    ) -> list[RetrievalHit]:
        if self.raises_on_search:
            raise RuntimeError("search exploded")
        return self.hits[: int(k)]


# --------------------------------------------------------------------- #
# build_server: returns a usable FastMCP instance                       #
# --------------------------------------------------------------------- #


def test_build_server_registers_expected_tools() -> None:
    brunnr = _StubBrunnr(
        stats=BrunnrStats(documents=0, chunks=0, embedded_chunks=0, size_bytes=0),
        hits=[],
    )
    mcp = build_server(config=EmberConfig(), brunnr=brunnr)
    # FastMCP keeps registered tools in its internal manager; we read
    # via the documented introspection API.
    tools = mcp._tool_manager.list_tools()
    names = sorted(t.name for t in tools)
    assert "search_well" in names
    assert "well_status" in names
    assert "doctor" in names


def test_build_server_registers_resources() -> None:
    brunnr = _StubBrunnr(
        stats=BrunnrStats(documents=0, chunks=0, embedded_chunks=0, size_bytes=0),
        hits=[],
    )
    mcp = build_server(config=EmberConfig(), brunnr=brunnr)
    resources = mcp._resource_manager.list_resources()
    uris = {str(r.uri) for r in resources}
    assert "ember://well/status" in uris


# --------------------------------------------------------------------- #
# Tool behaviour with a stub Brunnr                                     #
# --------------------------------------------------------------------- #


def test_well_status_tool_returns_stub_counts() -> None:
    """Call the FastMCP-registered tool function directly via its
    underlying Python implementation."""
    stats = BrunnrStats(
        documents=42, chunks=128, embedded_chunks=128, size_bytes=4096,
    )
    brunnr = _StubBrunnr(stats=stats, hits=[])
    mcp = build_server(config=EmberConfig(), brunnr=brunnr)
    # FastMCP stores the original Python callable under .fn
    tool = next(
        t for t in mcp._tool_manager.list_tools()
        if t.name == "well_status"
    )
    out = tool.fn()
    assert out["documents"] == 42
    assert out["chunks"] == 128
    assert out["embedded_chunks"] == 128


def test_well_status_tool_surfaces_brunnr_failure_as_error_field() -> None:
    """A backend exception becomes ``{"error": ...}`` — never raises
    across the MCP boundary."""
    brunnr = _StubBrunnr(
        stats=BrunnrStats(documents=0, chunks=0, embedded_chunks=0, size_bytes=0),
        hits=[],
        raises_on_count=True,
    )
    mcp = build_server(config=EmberConfig(), brunnr=brunnr)
    tool = next(
        t for t in mcp._tool_manager.list_tools()
        if t.name == "well_status"
    )
    out = tool.fn()
    assert "error" in out
    assert "exploded" in out["error"]


def test_doctor_tool_returns_realm_health() -> None:
    stats = BrunnrStats(
        documents=5, chunks=10, embedded_chunks=10, size_bytes=1000,
    )
    brunnr = _StubBrunnr(stats=stats, hits=[])
    mcp = build_server(config=EmberConfig(), brunnr=brunnr)
    tool = next(
        t for t in mcp._tool_manager.list_tools()
        if t.name == "doctor"
    )
    out = tool.fn()
    assert out["realms"]["brunnr"]["ok"] is True
    assert out["realms"]["brunnr"]["documents"] == 5
    # Batch J: Funi is now really probed (was previously stubbed to
    # None). In the unit-test environment there's typically no live
    # Ollama, so it reports ok=False with a detail string. If the host
    # happens to run Ollama, it reports ok=True with a model_id.
    # Either way `ok` is a bool now, not the previous stubbed None.
    assert isinstance(out["realms"]["funi"]["ok"], bool)


def test_doctor_tool_reports_brunnr_disconnected_gracefully() -> None:
    mcp = build_server(config=EmberConfig(), brunnr=None)
    tool = next(
        t for t in mcp._tool_manager.list_tools()
        if t.name == "doctor"
    )
    out = tool.fn()
    assert out["realms"]["brunnr"]["ok"] is False
    assert "disconnected" in out["realms"]["brunnr"]["detail"]


# --------------------------------------------------------------------- #
# Resource behaviour                                                    #
# --------------------------------------------------------------------- #


def test_well_status_resource_returns_json_string() -> None:
    import json  # noqa: PLC0415

    stats = BrunnrStats(
        documents=7, chunks=14, embedded_chunks=14, size_bytes=2048,
    )
    brunnr = _StubBrunnr(stats=stats, hits=[])
    mcp = build_server(config=EmberConfig(), brunnr=brunnr)
    # Resources are keyed by URI in the resource manager.
    resource = next(
        r for r in mcp._resource_manager.list_resources()
        if str(r.uri) == "ember://well/status"
    )
    out = resource.fn()
    data = json.loads(out)
    assert data["documents"] == 7
    assert data["chunks"] == 14

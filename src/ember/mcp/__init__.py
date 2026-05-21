"""MCP (Model Context Protocol) bidirectional integration — ADR-0014.

Two surfaces, both opt-in:

- **Client** (consume external MCP servers): spawn configured MCP
  servers as subprocesses on chat startup, discover their tools, and
  register them into ``ember.spark.funi.tools.registry`` under the
  ``mcp__<server>__<tool>`` naming convention. Tools then flow through
  the same approval + audit + execution path as first-party tools.

- **Server** (expose Ember as an MCP server): ``ember mcp serve`` runs
  a FastMCP server over stdio that exposes the Well (search, status,
  recent episodes) + doctor as MCP tools and resources. Other MCP
  clients (Claude Desktop, Claude Code, etc.) can address the
  operator's Well.

The ``mcp`` SDK + transitive deps land only when the operator installs
``pip install ember-agent[mcp]``. Without the extra, the package
imports lazily and surfaces a typed ``ConfigError`` at chat startup if
``config.mcp.enabled = true`` — never an ``ImportError``.
"""

from __future__ import annotations

__all__ = [
    "MCP_TOOL_NAME_PREFIX",
]


# The prefix every MCP-bridged tool name carries in the registry. Matches
# Claude Code's MCP naming convention so operators see consistent names
# across both surfaces. Format: mcp__<server_name>__<tool_name>.
MCP_TOOL_NAME_PREFIX = "mcp__"

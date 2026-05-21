"""Bridge MCP-server tools into Ember's first-party tool registry.

Per ADR-0014. Each discovered MCP tool becomes a regular ``ToolDescriptor``
in ``ember.spark.funi.tools.registry`` under the name
``mcp__<server>__<tool>``. The executor closures call back through
``MCPClientPool.call_tool(...)`` and translate the typed MCP
``CallToolResult`` into Ember's typed ``ToolReply``.

The naming convention matches Claude Code's MCP tool names so operators
see consistent shapes across both surfaces.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from ember.mcp import MCP_TOOL_NAME_PREFIX
from ember.mcp.client import MCPClientPool
from ember.schemas.config import MCPServerSpec
from ember.schemas.tool import (
    ApprovalPolicy,
    ToolCall,
    ToolDescriptor,
    ToolParameter,
    ToolParameterKind,
    ToolReply,
)
from ember.spark.funi.tools.registry import register

logger = logging.getLogger(__name__)


def register_pool_tools(
    pool: MCPClientPool,
    server_specs: tuple[MCPServerSpec, ...],
) -> list[str]:
    """Discover tools from every open session in ``pool`` and register
    them into Ember's process-global tool registry.

    Returns the list of registered tool names (``mcp__server__tool``
    format). Operator can later see them via ``ember mcp tools``.

    Tools that conflict with an already-registered name are skipped
    with a ``logger.warning`` — the bridge never raises out.
    """
    auto_approve_by_server: dict[str, frozenset[str]] = {
        s.name: frozenset(s.auto_approve) for s in server_specs
    }

    registered: list[str] = []
    for server_name in pool.server_names():
        auto_approve = auto_approve_by_server.get(server_name, frozenset())
        for mcp_tool in pool.tools_for(server_name):
            full_name = f"{MCP_TOOL_NAME_PREFIX}{server_name}__{mcp_tool.name}"
            try:
                descriptor = _build_descriptor(
                    full_name=full_name,
                    mcp_tool=mcp_tool,
                    standing=mcp_tool.name in auto_approve,
                )
                executor = _make_executor(pool, server_name, mcp_tool.name)
                register(descriptor, executor)
                registered.append(full_name)
            except Exception as exc:
                logger.warning(
                    "MCP tool %r could not be registered: %s",
                    full_name, exc,
                )
    return registered


def _build_descriptor(
    *, full_name: str, mcp_tool: Any, standing: bool,
) -> ToolDescriptor:
    """Convert an MCP Tool's JSON-schema input into a ToolDescriptor.

    MCP tools declare their input shape as a JSON Schema. Ember's
    framework uses a simpler shape (per ADR-0011 §2.2): per-arg
    kind/required/default/enum. We map JSON Schema's ``properties`` +
    ``required`` to Ember's ``parameters_schema``.

    Unknown / unsupported JSON-Schema types fall back to STRING; the
    MCP server's runtime validator catches type errors anyway, and
    keeping Ember's schema lossy-but-permissive is better than refusing
    to register tools we can't perfectly model.
    """
    description = mcp_tool.description or f"{full_name} (MCP tool)"
    schema: Any = mcp_tool.inputSchema if mcp_tool.inputSchema else {}
    properties = (schema.get("properties") or {}) if isinstance(schema, dict) else {}
    required_set = set(schema.get("required") or []) if isinstance(schema, dict) else set()

    params: dict[str, ToolParameter] = {}
    for arg_name, arg_schema in properties.items():
        kind = _coerce_jsonschema_kind(
            arg_schema.get("type") if isinstance(arg_schema, dict) else None
        )
        arg_desc = (
            arg_schema.get("description") if isinstance(arg_schema, dict) else None
        ) or arg_name
        enum_vals = (
            arg_schema.get("enum") if isinstance(arg_schema, dict) else None
        )
        params[arg_name] = ToolParameter(
            kind=kind,
            description=arg_desc,
            required=arg_name in required_set,
            enum=tuple(str(v) for v in enum_vals) if enum_vals else None,
        )

    approval = ApprovalPolicy.STANDING if standing else ApprovalPolicy.PER_CALL
    return ToolDescriptor(
        name=full_name,
        description=description,
        parameters_schema=params,
        required_approval=approval,
        # MCP tools don't declare redacted args; operator overrides via config.
        redacted_arg_names=(),
        timeout_s=30.0,
    )


_JSONSCHEMA_KIND_MAP = {
    "string": ToolParameterKind.STRING,
    "integer": ToolParameterKind.INTEGER,
    "number": ToolParameterKind.FLOAT,
    "boolean": ToolParameterKind.BOOLEAN,
}


def _coerce_jsonschema_kind(jstype: Any) -> ToolParameterKind:
    """Map a JSON-Schema ``type`` to ToolParameterKind. Default STRING."""
    if isinstance(jstype, str):
        return _JSONSCHEMA_KIND_MAP.get(jstype, ToolParameterKind.STRING)
    if isinstance(jstype, list):
        # JSON Schema allows ["string", "null"]; pick the first non-null.
        for t in jstype:
            if t != "null":
                return _JSONSCHEMA_KIND_MAP.get(t, ToolParameterKind.STRING)
    return ToolParameterKind.STRING


def _make_executor(
    pool: MCPClientPool, server_name: str, tool_name: str,
):
    """Build the per-tool executor closure registered into Ember's
    framework.

    The closure captures ``pool`` so each call goes through the same
    runner + session. Failures are translated into typed ``ToolReply``
    rather than raising — matching the ADR-0011 contract.
    """

    def _execute(call: ToolCall) -> ToolReply:
        started = time.monotonic()
        try:
            result = pool.call_tool(server_name, tool_name, dict(call.arguments))
        except TimeoutError as exc:
            return ToolReply(
                call_id=call.call_id,
                output="",
                error=f"MCP tool timed out: {exc}",
                elapsed_s=time.monotonic() - started,
            )
        except KeyError as exc:
            return ToolReply(
                call_id=call.call_id,
                output="",
                error=f"MCP server gone: {exc}",
                elapsed_s=time.monotonic() - started,
            )
        except Exception as exc:
            return ToolReply(
                call_id=call.call_id,
                output="",
                error=f"MCP call failed: {type(exc).__name__}: {exc}",
                elapsed_s=time.monotonic() - started,
            )

        return _to_tool_reply(call, result, started)

    return _execute


def _to_tool_reply(
    call: ToolCall, result: Any, started: float,
) -> ToolReply:
    """Translate an MCP CallToolResult into Ember's ToolReply.

    MCP's content list can include TextContent, ImageContent, etc.; we
    concatenate the text parts and represent non-text parts as their
    type name in brackets. ``isError=True`` on the MCP side becomes
    ``ToolReply.error``.
    """
    elapsed = time.monotonic() - started
    text_parts: list[str] = []
    for item in (result.content or []):
        # Duck-typed: TextContent has .text, ImageContent has .data, etc.
        text = getattr(item, "text", None)
        if isinstance(text, str):
            text_parts.append(text)
        else:
            kind = type(item).__name__
            text_parts.append(f"[{kind}]")
    output = "\n".join(text_parts)

    error: str | None = None
    if getattr(result, "isError", False):
        error = output or "MCP server returned isError without text content"
        output = "" if not text_parts else output

    return ToolReply(
        call_id=call.call_id,
        output=output,
        error=error,
        elapsed_s=elapsed,
    )


__all__ = ["register_pool_tools"]

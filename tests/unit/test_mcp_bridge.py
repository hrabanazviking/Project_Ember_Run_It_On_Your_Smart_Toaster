"""Unit tests for the MCP→Ember-registry bridge.

Per ADR-0014. The bridge converts MCP ``Tool`` descriptors + ``CallToolResult``
payloads into Ember's ``ToolDescriptor``/``ToolReply`` shape. The
conversion logic is pure (no subprocess) so we test it in isolation
without a real MCP server.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import pytest

from ember.mcp.bridge import (
    _build_descriptor,
    _coerce_jsonschema_kind,
    _make_executor,
    _to_tool_reply,
    register_pool_tools,
)
from ember.schemas.config import MCPServerSpec
from ember.schemas.tool import (
    ApprovalPolicy,
    ToolCall,
    ToolParameterKind,
)
from ember.spark.funi.tools import clear as registry_clear
from ember.spark.funi.tools import list_tools as registry_list


@pytest.fixture(autouse=True)
def _isolate_registry():
    registry_clear()
    yield
    registry_clear()


# --------------------------------------------------------------------- #
# JSON-Schema → ToolParameterKind coercion                              #
# --------------------------------------------------------------------- #


def test_coerce_jsonschema_kind_maps_known_types() -> None:
    assert _coerce_jsonschema_kind("string") is ToolParameterKind.STRING
    assert _coerce_jsonschema_kind("integer") is ToolParameterKind.INTEGER
    assert _coerce_jsonschema_kind("number") is ToolParameterKind.FLOAT
    assert _coerce_jsonschema_kind("boolean") is ToolParameterKind.BOOLEAN


def test_coerce_jsonschema_kind_handles_union_type() -> None:
    """JSON Schema allows ``"type": ["string", "null"]``."""
    assert _coerce_jsonschema_kind(["string", "null"]) is ToolParameterKind.STRING
    assert _coerce_jsonschema_kind(["null", "integer"]) is ToolParameterKind.INTEGER


def test_coerce_jsonschema_kind_defaults_to_string_on_unknown() -> None:
    """Lossy-but-permissive: unknown JSON Schema types still register
    rather than crashing tool discovery."""
    assert _coerce_jsonschema_kind("object") is ToolParameterKind.STRING
    assert _coerce_jsonschema_kind(None) is ToolParameterKind.STRING
    assert _coerce_jsonschema_kind(42) is ToolParameterKind.STRING


# --------------------------------------------------------------------- #
# Descriptor building from a Tool-shaped stub                           #
# --------------------------------------------------------------------- #


@dataclass
class _FakeMCPTool:
    name: str
    description: str | None
    inputSchema: dict[str, Any] | None


def test_build_descriptor_translates_required_and_enum() -> None:
    mcp_tool = _FakeMCPTool(
        name="echo",
        description="Echo back its input.",
        inputSchema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "What to echo"},
                "mode": {"type": "string", "enum": ["upper", "lower"]},
            },
            "required": ["text"],
        },
    )
    desc = _build_descriptor(
        full_name="mcp__demo__echo", mcp_tool=mcp_tool, standing=False,
    )
    assert desc.name == "mcp__demo__echo"
    assert desc.required_approval is ApprovalPolicy.PER_CALL
    assert desc.parameters_schema["text"].required is True
    assert desc.parameters_schema["text"].kind is ToolParameterKind.STRING
    assert desc.parameters_schema["mode"].required is False
    assert desc.parameters_schema["mode"].enum == ("upper", "lower")


def test_build_descriptor_standing_flag_lifts_approval() -> None:
    mcp_tool = _FakeMCPTool(name="ping", description="Ping", inputSchema={})
    desc = _build_descriptor(
        full_name="mcp__demo__ping", mcp_tool=mcp_tool, standing=True,
    )
    assert desc.required_approval is ApprovalPolicy.STANDING


def test_build_descriptor_handles_missing_input_schema() -> None:
    """Some MCP tools declare no inputs at all — `inputSchema=None` or
    `{}`. Should still register as a zero-parameter tool."""
    mcp_tool = _FakeMCPTool(name="noargs", description=None, inputSchema=None)
    desc = _build_descriptor(
        full_name="mcp__demo__noargs", mcp_tool=mcp_tool, standing=False,
    )
    assert desc.parameters_schema == {}
    assert desc.description  # falls back to a generated description


# --------------------------------------------------------------------- #
# CallToolResult → ToolReply translation                                #
# --------------------------------------------------------------------- #


@dataclass
class _FakeText:
    text: str


@dataclass
class _FakeImage:
    data: bytes


@dataclass
class _FakeCallResult:
    content: list[Any]
    isError: bool = False


def test_to_tool_reply_concatenates_text_content() -> None:
    call = ToolCall(call_id="c-1", name="x", arguments={})
    result = _FakeCallResult(content=[_FakeText("hello"), _FakeText("world")])
    reply = _to_tool_reply(call, result, started=0.0)
    assert reply.output == "hello\nworld"
    assert reply.error is None


def test_to_tool_reply_brackets_non_text_content() -> None:
    """Non-text MCP content (image, audio, embedded resource) renders
    as ``[TypeName]`` in the operator-facing output but doesn't crash."""
    call = ToolCall(call_id="c-2", name="x", arguments={})
    result = _FakeCallResult(content=[_FakeText("ok"), _FakeImage(b"...")])
    reply = _to_tool_reply(call, result, started=0.0)
    assert "ok" in reply.output
    assert "[_FakeImage]" in reply.output


def test_to_tool_reply_isError_becomes_typed_error() -> None:
    """MCP's `isError=True` arrives in our typed `ToolReply.error`."""
    call = ToolCall(call_id="c-3", name="x", arguments={})
    result = _FakeCallResult(
        content=[_FakeText("oh no")], isError=True,
    )
    reply = _to_tool_reply(call, result, started=0.0)
    assert reply.error == "oh no"


# --------------------------------------------------------------------- #
# Executor closure: failure-to-typed-reply                              #
# --------------------------------------------------------------------- #


class _FakePool:
    def __init__(self, *, raise_with: Exception | None = None, result: Any = None):
        self._raise_with = raise_with
        self._result = result

    def call_tool(self, server: str, tool: str, arguments: dict) -> Any:
        if self._raise_with is not None:
            raise self._raise_with
        return self._result


def test_executor_translates_timeout_to_typed_reply() -> None:
    pool = _FakePool(raise_with=TimeoutError("slow"))
    executor = _make_executor(pool, "demo", "echo")
    reply = executor(ToolCall(call_id="c-1", name="x", arguments={}))
    assert reply.error and "timed out" in reply.error
    assert reply.output == ""


def test_executor_translates_keyerror_to_typed_reply() -> None:
    """A KeyError out of the pool means the server died between
    discovery and call; we surface it as a typed reply, not a crash."""
    pool = _FakePool(raise_with=KeyError("demo"))
    executor = _make_executor(pool, "demo", "echo")
    reply = executor(ToolCall(call_id="c-1", name="x", arguments={}))
    assert reply.error and "MCP server gone" in reply.error


def test_executor_translates_generic_exception_to_typed_reply() -> None:
    """Any other exception still becomes a typed reply (the framework
    contract requires this — bare raise crashes the chat loop)."""
    pool = _FakePool(raise_with=RuntimeError("boom"))
    executor = _make_executor(pool, "demo", "echo")
    reply = executor(ToolCall(call_id="c-1", name="x", arguments={}))
    assert reply.error and "RuntimeError" in reply.error and "boom" in reply.error


def test_executor_happy_path_wraps_call_result() -> None:
    pool = _FakePool(result=_FakeCallResult(content=[_FakeText("hi")]))
    executor = _make_executor(pool, "demo", "echo")
    reply = executor(ToolCall(call_id="c-1", name="x", arguments={}))
    assert reply.output == "hi"
    assert reply.error is None


# --------------------------------------------------------------------- #
# Full register_pool_tools: pool → registered descriptors               #
# --------------------------------------------------------------------- #


class _FakePoolForBridge:
    def __init__(self, tools_by_server: dict[str, list[_FakeMCPTool]]) -> None:
        self._tools = tools_by_server

    def server_names(self) -> list[str]:
        return sorted(self._tools)

    def tools_for(self, name: str) -> list[_FakeMCPTool]:
        return list(self._tools.get(name, ()))


def test_register_pool_tools_names_match_prefix_convention() -> None:
    """Registered tool names follow ``mcp__<server>__<tool>``."""
    pool = _FakePoolForBridge({
        "demo": [_FakeMCPTool(name="echo", description="e", inputSchema={})],
    })
    specs = (MCPServerSpec(name="demo", command="cat"),)
    registered = register_pool_tools(pool, specs)
    assert registered == ["mcp__demo__echo"]
    descriptors = registry_list()
    assert any(d.name == "mcp__demo__echo" for d in descriptors)


def test_register_pool_tools_honours_auto_approve() -> None:
    """A tool listed in ``MCPServerSpec.auto_approve`` registers as
    STANDING; others remain PER_CALL."""
    pool = _FakePoolForBridge({
        "demo": [
            _FakeMCPTool(name="safe", description="s", inputSchema={}),
            _FakeMCPTool(name="risky", description="r", inputSchema={}),
        ],
    })
    specs = (
        MCPServerSpec(name="demo", command="cat", auto_approve=("safe",)),
    )
    register_pool_tools(pool, specs)
    descriptors = {d.name: d for d in registry_list()}
    assert descriptors["mcp__demo__safe"].required_approval is ApprovalPolicy.STANDING
    assert descriptors["mcp__demo__risky"].required_approval is ApprovalPolicy.PER_CALL


def test_register_pool_tools_skips_conflicts_with_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """If a tool name conflicts with an already-registered one, the
    bridge skips with a warning instead of crashing."""
    pool = _FakePoolForBridge({
        "demo": [_FakeMCPTool(name="echo", description="e", inputSchema={})],
    })
    specs = (MCPServerSpec(name="demo", command="cat"),)
    register_pool_tools(pool, specs)  # first registration
    caplog.set_level(logging.WARNING, logger="ember.mcp.bridge")
    # Second registration should skip + warn, not raise.
    register_pool_tools(pool, specs)
    assert any("could not be registered" in r.message for r in caplog.records)

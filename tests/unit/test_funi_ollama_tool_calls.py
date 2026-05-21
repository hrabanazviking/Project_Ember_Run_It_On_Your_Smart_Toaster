"""Ollama-adapter tool-call serialisation + parsing (Phase 16, ADR 0011)."""

from __future__ import annotations

import json
from unittest.mock import patch

from ember.schemas.config import FuniConfig, FuniOllamaConfig, FuniRuntime
from ember.schemas.funi import ContextItem, ContextKind, FinishReason
from ember.schemas.tool import (
    ToolCall,
    ToolDescriptor,
    ToolParameter,
    ToolParameterKind,
)
from ember.spark.funi.ollama import OllamaFuni
from ember.spark.funi.ollama import open as ollama_open
from ember.spark.funi.ollama.adapter import (
    _descriptor_to_ollama_tool,
    _messages_from_context,
    _parse_tool_calls,
)

# --------------------------------------------------------------------- #
# _descriptor_to_ollama_tool                                            #
# --------------------------------------------------------------------- #


def test_descriptor_serialises_to_openai_function_shape() -> None:
    d = ToolDescriptor(
        name="search_well",
        description="search the well",
        parameters_schema={
            "query": ToolParameter(
                kind=ToolParameterKind.STRING, description="search text",
            ),
            "k": ToolParameter(
                kind=ToolParameterKind.INTEGER, description="top k",
                required=False, default=5,
            ),
        },
    )
    out = _descriptor_to_ollama_tool(d)
    assert out["type"] == "function"
    fn = out["function"]
    assert fn["name"] == "search_well"
    assert fn["description"] == "search the well"
    params = fn["parameters"]
    assert params["type"] == "object"
    assert "query" in params["properties"]
    assert params["properties"]["query"]["type"] == "string"
    assert params["properties"]["k"]["type"] == "integer"
    # Only required-without-default parameters appear in `required`.
    assert "query" in params["required"]
    assert "k" not in params["required"]


def test_descriptor_with_enum_emits_enum_field() -> None:
    d = ToolDescriptor(
        name="t",
        description="x",
        parameters_schema={
            "mode": ToolParameter(
                kind=ToolParameterKind.STRING,
                description="m",
                enum=("read", "write"),
            ),
        },
    )
    out = _descriptor_to_ollama_tool(d)
    assert out["function"]["parameters"]["properties"]["mode"]["enum"] == ["read", "write"]


def test_path_and_url_params_serialise_as_strings() -> None:
    """ADR 0011 §2.2 — PATH and URL are strings on the wire."""
    d = ToolDescriptor(
        name="t",
        description="x",
        parameters_schema={
            "path": ToolParameter(kind=ToolParameterKind.PATH, description="p"),
            "url":  ToolParameter(kind=ToolParameterKind.URL, description="u"),
        },
    )
    props = _descriptor_to_ollama_tool(d)["function"]["parameters"]["properties"]
    assert props["path"]["type"] == "string"
    assert props["url"]["type"] == "string"


# --------------------------------------------------------------------- #
# _parse_tool_calls                                                     #
# --------------------------------------------------------------------- #


def test_parse_tool_calls_round_trips_openai_shape() -> None:
    raw = [
        {"function": {"name": "search_well", "arguments": {"query": "Odin", "k": 5}}},
    ]
    out = _parse_tool_calls(raw)
    assert len(out) == 1
    assert isinstance(out[0], ToolCall)
    assert out[0].name == "search_well"
    assert out[0].arguments == {"query": "Odin", "k": 5}
    assert out[0].call_id  # assigned a UUID


def test_parse_tool_calls_handles_json_string_arguments() -> None:
    """Some Ollama builds emit the arguments blob as a JSON string."""
    raw = [
        {"function": {"name": "search_well", "arguments": '{"query": "Tyr"}'}},
    ]
    out = _parse_tool_calls(raw)
    assert len(out) == 1
    assert out[0].arguments == {"query": "Tyr"}


def test_parse_tool_calls_preserves_explicit_id_when_supplied() -> None:
    raw = [
        {"id": "call-from-ollama", "function": {"name": "x", "arguments": {}}},
    ]
    out = _parse_tool_calls(raw)
    assert out[0].call_id == "call-from-ollama"


def test_parse_tool_calls_skips_malformed_entries() -> None:
    raw = [
        "not-a-dict",
        {"function": {"name": ""}},                 # empty name
        {"function": {"name": "ok", "arguments": {}}},
        {"function": {"name": "bad-args", "arguments": "not-json"}},  # parses to {}
        {"no_function": True},
    ]
    out = _parse_tool_calls(raw)
    # 'ok' and 'bad-args' make it through; the others are dropped.
    names = [c.name for c in out]
    assert names == ["ok", "bad-args"]


def test_parse_tool_calls_returns_empty_for_non_list() -> None:
    assert _parse_tool_calls(None) == ()
    assert _parse_tool_calls("string") == ()
    assert _parse_tool_calls({"function": "no"}) == ()


# --------------------------------------------------------------------- #
# Tool reply context items round-trip into Ollama "role=tool" messages   #
# --------------------------------------------------------------------- #


def test_tool_reply_context_item_becomes_role_tool_message() -> None:
    item = ContextItem(
        kind=ContextKind.TOOL_REPLY,
        text="ok",
        metadata={"tool_name": "search_well", "call_id": "c-1"},
    )
    messages = _messages_from_context([item], "follow-up question")
    tool_msg = next(m for m in messages if m["role"] == "tool")
    assert tool_msg["content"] == "ok"
    assert tool_msg["name"] == "search_well"
    # The user input is still appended.
    user_msgs = [m for m in messages if m["role"] == "user"]
    assert user_msgs[-1]["content"] == "follow-up question"


def test_empty_operator_input_is_omitted_so_follow_up_turns_are_tool_only() -> None:
    """Phase 16: follow-up turns after a tool call carry no operator input."""
    item = ContextItem(
        kind=ContextKind.TOOL_REPLY,
        text="ok",
        metadata={"tool_name": "search_well"},
    )
    messages = _messages_from_context([item], "")
    # No trailing user message — just the tool reply.
    assert messages[-1]["role"] == "tool"


# --------------------------------------------------------------------- #
# End-to-end: complete() picks up tool_calls from a mocked Ollama        #
# --------------------------------------------------------------------- #


def _funi_config() -> FuniConfig:
    return FuniConfig(
        runtime=FuniRuntime.OLLAMA,
        ollama=FuniOllamaConfig(model="phi3:mini"),
    )


class _Resp:
    def __init__(self, body: dict) -> None:
        self._body = json.dumps(body).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None


def test_streaming_accumulates_tool_calls_from_non_done_chunk() -> None:
    """Ollama emits tool_calls on a frame BEFORE done:true. The adapter
    must accumulate them and surface them on the final chunk so chat.py's
    tool loop fires. Regression test for the Phase-16 smoke failure on
    real llama3.2:3b."""
    from ember.schemas.tool import ToolDescriptor  # noqa: PLC0415

    class _StreamResp:
        def __init__(self, lines: list[dict]) -> None:
            self._lines = [
                (json.dumps(line) + "\n").encode("utf-8") for line in lines
            ]

        def __iter__(self):
            return iter(self._lines)

        def close(self):
            return None

    response = _StreamResp([
        # First frame carries the tool call, done=False.
        {
            "model": "llama3.2:3b",
            "done": False,
            "message": {
                "content": "",
                "tool_calls": [
                    {"function": {"name": "search_well", "arguments": {"query": "Odin"}}},
                ],
            },
        },
        # Second frame is the done summary, no tool_calls.
        {
            "model": "llama3.2:3b",
            "done": True,
            "done_reason": "stop",
            "message": {"content": ""},
        },
    ])

    def _urlopen(req, timeout):
        if req.get_full_url().endswith("/api/version"):
            return _Resp({"version": "0.1.32"})
        return response

    with patch("urllib.request.urlopen", side_effect=_urlopen):
        handle = ollama_open(_funi_config())
        assert isinstance(handle, OllamaFuni)
        descriptor = ToolDescriptor(name="search_well", description="x")
        chunks = list(
            handle.complete_streaming("hi", context=[], tools=[descriptor])
        )

    final = chunks[-1]
    assert final.done is True
    assert final.finish_reason is FinishReason.TOOL_CALL
    assert len(final.tool_calls) == 1
    assert final.tool_calls[0].name == "search_well"


def test_complete_returns_tool_calls_when_ollama_emits_them() -> None:
    def _urlopen(req, timeout):
        if req.get_full_url().endswith("/api/version"):
            return _Resp({"version": "0.1.32"})
        return _Resp({
            "model": "phi3:mini",
            "done": True,
            "done_reason": "stop",  # model forgot to set tool_calls; adapter forces it
            "message": {
                "content": "",
                "tool_calls": [
                    {"function": {"name": "search_well", "arguments": {"query": "Odin"}}},
                ],
            },
        })

    with patch("urllib.request.urlopen", side_effect=_urlopen):
        handle = ollama_open(_funi_config())
        assert isinstance(handle, OllamaFuni)
        descriptor = ToolDescriptor(name="search_well", description="x")
        reply = handle.complete("hi", context=[], tools=[descriptor])

    assert reply.finish_reason is FinishReason.TOOL_CALL
    assert len(reply.tool_calls) == 1
    assert reply.tool_calls[0].name == "search_well"
    assert reply.tool_calls[0].arguments == {"query": "Odin"}

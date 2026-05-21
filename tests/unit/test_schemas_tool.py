"""Shape contracts for ``ember.schemas.tool`` (ADR 0011 §2.1-§2.2).

The schemas are frozen + slotted dataclasses; validation logic lives in
:mod:`ember.spark.funi.tools.registry`. These tests assert the *types*
only — every behavioural test lives in the matching framework-side
file.
"""

from __future__ import annotations

import dataclasses

import pytest

from ember.schemas.tool import (
    ApprovalOutcome,
    ApprovalPolicy,
    ToolCall,
    ToolDescriptor,
    ToolError,
    ToolParameter,
    ToolParameterKind,
    ToolReply,
)

# --------------------------------------------------------------------- #
# ApprovalPolicy / ApprovalOutcome                                      #
# --------------------------------------------------------------------- #


def test_approval_policy_has_three_lanes() -> None:
    values = {p.value for p in ApprovalPolicy}
    assert values == {"standing", "per_call", "forbidden"}


def test_approval_outcome_distinguishes_failure_modes() -> None:
    """ADR 0011 §2.5 — typed outcomes, not boolean."""
    values = {o.value for o in ApprovalOutcome}
    assert "denied" in values
    assert "invalid_arguments" in values
    assert "forbidden_by_registry" in values
    assert "no_such_tool" in values
    assert "auto_approved" in values
    assert "approved_this_call" in values
    assert "approved_for_session" in values


# --------------------------------------------------------------------- #
# ToolParameter / ToolParameterKind                                     #
# --------------------------------------------------------------------- #


def test_tool_parameter_kinds_cover_adr_set() -> None:
    """ADR 0011 §2.2 — six kinds, jsonschema deliberately excluded."""
    expected = {"string", "integer", "float", "boolean", "path", "url"}
    assert {k.value for k in ToolParameterKind} == expected


def test_tool_parameter_defaults() -> None:
    p = ToolParameter(kind=ToolParameterKind.STRING, description="q")
    assert p.required is True
    assert p.default is None
    assert p.enum is None


def test_tool_parameter_is_frozen() -> None:
    p = ToolParameter(kind=ToolParameterKind.STRING, description="q")
    with pytest.raises(dataclasses.FrozenInstanceError):
        p.description = "tampered"  # type: ignore[misc]


# --------------------------------------------------------------------- #
# ToolDescriptor                                                        #
# --------------------------------------------------------------------- #


def test_descriptor_defaults() -> None:
    d = ToolDescriptor(name="x", description="a tool")
    assert d.required_approval is ApprovalPolicy.PER_CALL
    assert d.redacted_arg_names == ()
    assert d.timeout_s == 10.0
    assert d.parameters_schema == {}


def test_descriptor_with_redaction() -> None:
    d = ToolDescriptor(
        name="vault_read",
        description="read a secret",
        redacted_arg_names=("token",),
    )
    assert "token" in d.redacted_arg_names


def test_descriptor_is_frozen() -> None:
    d = ToolDescriptor(name="x", description="y")
    with pytest.raises(dataclasses.FrozenInstanceError):
        d.name = "tampered"  # type: ignore[misc]


# --------------------------------------------------------------------- #
# ToolCall / ToolReply                                                  #
# --------------------------------------------------------------------- #


def test_tool_call_holds_call_id_and_arguments() -> None:
    call = ToolCall(
        call_id="abc-123",
        name="search_well",
        arguments={"query": "Odin", "k": 5},
    )
    assert call.call_id == "abc-123"
    assert call.name == "search_well"
    assert call.arguments["query"] == "Odin"
    assert call.arguments["k"] == 5


def test_tool_call_is_frozen() -> None:
    call = ToolCall(call_id="x", name="t")
    with pytest.raises(dataclasses.FrozenInstanceError):
        call.call_id = "tampered"  # type: ignore[misc]


def test_tool_reply_default_output_is_empty_string() -> None:
    r = ToolReply(call_id="x")
    assert r.output == ""
    assert r.error is None
    assert r.elapsed_s == 0.0


def test_tool_reply_carries_both_output_and_error() -> None:
    """ADR 0011 §2.1 — partial output + error is legal."""
    r = ToolReply(call_id="x", output="partial...", error="timeout: exceeded 10s")
    assert r.output == "partial..."
    assert r.error == "timeout: exceeded 10s"


# --------------------------------------------------------------------- #
# Re-export from ember.schemas.funi                                     #
# --------------------------------------------------------------------- #


def test_tool_call_re_exported_via_funi_path() -> None:
    """ADR 0011 §5 — historical callers keep their import path."""
    from ember.schemas.funi import ToolCall as ToolCallViaFuni  # noqa: PLC0415

    assert ToolCallViaFuni is ToolCall


# --------------------------------------------------------------------- #
# ToolError                                                             #
# --------------------------------------------------------------------- #


def test_tool_error_is_an_exception() -> None:
    assert issubclass(ToolError, Exception)
    with pytest.raises(ToolError, match="boom"):
        raise ToolError("boom")

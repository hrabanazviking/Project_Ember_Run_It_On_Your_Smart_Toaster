"""Phase-16 render helpers (``render_tool_call_proposal`` + ``render_tool_reply``)."""

from __future__ import annotations

from ember.schemas.tool import (
    ApprovalOutcome,
    ApprovalPolicy,
    ToolCall,
    ToolDescriptor,
    ToolReply,
)
from ember.spark.munnr import render


def _descriptor(
    *,
    name: str = "ping",
    redacted_arg_names: tuple[str, ...] = (),
) -> ToolDescriptor:
    return ToolDescriptor(
        name=name, description="echo back 'pong'",
        required_approval=ApprovalPolicy.PER_CALL,
        redacted_arg_names=redacted_arg_names,
    )


def _call(arguments: dict | None = None) -> ToolCall:
    return ToolCall(
        call_id="abc-12345678", name="ping", arguments=arguments or {},
    )


# --------------------------------------------------------------------- #
# render_tool_call_proposal                                             #
# --------------------------------------------------------------------- #


def test_proposal_renders_name_description_and_args() -> None:
    out = render.render_tool_call_proposal(
        _descriptor(),
        _call({"shout": True, "tag": "hi"}),
    )
    assert "tool proposal" in out
    assert "ping" in out
    assert "echo back 'pong'" in out
    assert "shout" in out
    assert "tag" in out
    assert "True" in out
    # The short call_id prefix is shown.
    assert "abc-1234" in out


def test_proposal_handles_no_descriptor() -> None:
    out = render.render_tool_call_proposal(None, _call({"x": 1}))
    assert "ping" in out
    # No 'description:' line when descriptor is missing.
    assert "description:" not in out


def test_proposal_handles_no_arguments() -> None:
    out = render.render_tool_call_proposal(_descriptor(), _call({}))
    assert "(none)" in out


def test_proposal_redacts_marked_arguments() -> None:
    descriptor = _descriptor(redacted_arg_names=("token",))
    out = render.render_tool_call_proposal(
        descriptor,
        ToolCall(call_id="x", name="ping", arguments={
            "shout": True, "token": "super-secret",
        }),
    )
    assert "<redacted>" in out
    assert "super-secret" not in out


# --------------------------------------------------------------------- #
# render_tool_reply                                                     #
# --------------------------------------------------------------------- #


def test_reply_renders_output_with_outcome_headline() -> None:
    reply = ToolReply(call_id="x", output="pong", elapsed_s=0.012)
    out = render.render_tool_reply(
        reply, _descriptor(),
        outcome=ApprovalOutcome.APPROVED_THIS_CALL,
    )
    assert "[tool reply: approved] ping" in out
    assert "pong" in out
    assert "12 ms" in out


def test_reply_renders_error_when_no_output() -> None:
    reply = ToolReply(call_id="x", error="bad path")
    out = render.render_tool_reply(
        reply, _descriptor(),
        outcome=ApprovalOutcome.INVALID_ARGUMENTS,
    )
    assert "invalid arguments" in out
    assert "bad path" in out


def test_reply_truncates_long_output() -> None:
    big = "x" * (render.TOOL_OUTPUT_PREVIEW_BYTES + 1024)
    reply = ToolReply(call_id="x", output=big)
    out = render.render_tool_reply(
        reply, _descriptor(),
        outcome=ApprovalOutcome.AUTO_APPROVED,
    )
    assert "auto-approved" in out
    assert "..." in out
    assert len(out) < len(big)


def test_reply_handles_no_descriptor() -> None:
    reply = ToolReply(call_id="x", error="no such tool: ghost")
    out = render.render_tool_reply(
        reply, None,
        outcome=ApprovalOutcome.NO_SUCH_TOOL,
    )
    assert "no such tool" in out
    assert "(unknown tool)" in out


def test_reply_distinguishes_denied_from_approved() -> None:
    reply = ToolReply(call_id="x", error="refused: denied")
    out = render.render_tool_reply(
        reply, _descriptor(),
        outcome=ApprovalOutcome.DENIED,
    )
    assert "operator denied" in out


def test_reply_renders_session_approval() -> None:
    reply = ToolReply(call_id="x", output="results", elapsed_s=0.05)
    out = render.render_tool_reply(
        reply, _descriptor(),
        outcome=ApprovalOutcome.APPROVED_FOR_SESSION,
    )
    assert "approved-for-session" in out

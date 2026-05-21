"""Approval-policy resolution + interactive prompter (ADR 0011 §2.4-§2.6)."""

from __future__ import annotations

import io

from ember.schemas.tool import (
    ApprovalOutcome,
    ApprovalPolicy,
    ToolCall,
    ToolDescriptor,
)
from ember.spark.funi.tools.approval import (
    ApprovalDecision,
    StdinApprovalPrompter,
    resolve,
    resolve_with_answer,
)


def _descriptor(
    name: str = "search_well",
    *,
    required_approval: ApprovalPolicy = ApprovalPolicy.PER_CALL,
) -> ToolDescriptor:
    return ToolDescriptor(
        name=name, description="t", required_approval=required_approval,
    )


def _call(name: str = "search_well") -> ToolCall:
    return ToolCall(call_id="c-1", name=name, arguments={"query": "Odin"})


# --------------------------------------------------------------------- #
# Policy resolution (no prompting)                                      #
# --------------------------------------------------------------------- #


def test_standing_descriptor_auto_approves() -> None:
    d = _descriptor(required_approval=ApprovalPolicy.STANDING)
    decision = resolve(d)
    assert decision.outcome is ApprovalOutcome.AUTO_APPROVED
    assert decision.needs_prompt is False


def test_per_call_descriptor_signals_prompt_needed() -> None:
    d = _descriptor(required_approval=ApprovalPolicy.PER_CALL)
    decision = resolve(d)
    assert decision.needs_prompt is True


def test_forbidden_descriptor_resolves_to_forbidden_by_registry() -> None:
    """Even though FORBIDDEN tools can't register, resolve() must handle
    a hypothetical FORBIDDEN descriptor without crashing — defence in depth."""
    d = _descriptor(required_approval=ApprovalPolicy.FORBIDDEN)
    decision = resolve(d)
    assert decision.outcome is ApprovalOutcome.FORBIDDEN_BY_REGISTRY
    assert decision.needs_prompt is False


def test_session_standing_skips_prompt() -> None:
    """Operator typed 'always' earlier in this session."""
    d = _descriptor(required_approval=ApprovalPolicy.PER_CALL)
    decision = resolve(d, session_standing=frozenset({"search_well"}))
    assert decision.outcome is ApprovalOutcome.AUTO_APPROVED
    assert decision.needs_prompt is False


def test_standing_trust_all_skips_prompt_for_per_call_tool() -> None:
    """Operator set tools.standing_trust: true."""
    d = _descriptor(required_approval=ApprovalPolicy.PER_CALL)
    decision = resolve(d, standing_trust_all=True)
    assert decision.outcome is ApprovalOutcome.AUTO_APPROVED


# --------------------------------------------------------------------- #
# Config overrides — descriptor is the floor                            #
# --------------------------------------------------------------------- #


def test_config_can_downgrade_standing_to_per_call() -> None:
    """Operator wants more strict than the descriptor allows."""
    d = _descriptor(required_approval=ApprovalPolicy.STANDING)
    decision = resolve(
        d,
        config_overrides={"search_well": ApprovalPolicy.PER_CALL},
    )
    assert decision.needs_prompt is True


def test_config_cannot_upgrade_per_call_to_standing() -> None:
    """The descriptor's PER_CALL is the safety floor — config can't lift it."""
    d = _descriptor(required_approval=ApprovalPolicy.PER_CALL)
    decision = resolve(
        d,
        config_overrides={"search_well": ApprovalPolicy.STANDING},
    )
    # Still needs a prompt — the override is ignored.
    assert decision.needs_prompt is True


def test_config_can_forbid_an_otherwise_standing_tool() -> None:
    d = _descriptor(required_approval=ApprovalPolicy.STANDING)
    decision = resolve(
        d, config_overrides={"search_well": ApprovalPolicy.FORBIDDEN},
    )
    assert decision.outcome is ApprovalOutcome.FORBIDDEN_BY_REGISTRY


# --------------------------------------------------------------------- #
# resolve_with_answer                                                   #
# --------------------------------------------------------------------- #


def test_answer_y_maps_to_approved_this_call() -> None:
    assert resolve_with_answer("y") is ApprovalOutcome.APPROVED_THIS_CALL


def test_answer_always_maps_to_approved_for_session() -> None:
    assert resolve_with_answer("always") is ApprovalOutcome.APPROVED_FOR_SESSION


def test_answer_n_maps_to_denied() -> None:
    assert resolve_with_answer("n") is ApprovalOutcome.DENIED


# --------------------------------------------------------------------- #
# StdinApprovalPrompter (scripted IO)                                   #
# --------------------------------------------------------------------- #


def test_stdin_prompter_returns_y_on_y_input() -> None:
    stdin = io.StringIO("y\n")
    stdout = io.StringIO()
    prompter = StdinApprovalPrompter(stdin=stdin, stdout=stdout)
    answer = prompter.prompt(_descriptor(), _call())
    assert answer == "y"
    output = stdout.getvalue()
    assert "tool proposal: search_well" in output
    assert "approve this call?" in output


def test_stdin_prompter_returns_always_on_always_input() -> None:
    stdin = io.StringIO("always\n")
    stdout = io.StringIO()
    prompter = StdinApprovalPrompter(stdin=stdin, stdout=stdout)
    assert prompter.prompt(_descriptor(), _call()) == "always"


def test_stdin_prompter_returns_n_on_n_input() -> None:
    stdin = io.StringIO("n\n")
    stdout = io.StringIO()
    prompter = StdinApprovalPrompter(stdin=stdin, stdout=stdout)
    assert prompter.prompt(_descriptor(), _call()) == "n"


def test_stdin_prompter_returns_n_on_eof() -> None:
    """EOF → default to refuse (safer than silent approve)."""
    stdin = io.StringIO("")  # immediate EOF
    stdout = io.StringIO()
    prompter = StdinApprovalPrompter(stdin=stdin, stdout=stdout)
    assert prompter.prompt(_descriptor(), _call()) == "n"


def test_stdin_prompter_treats_unknown_input_as_n() -> None:
    """Operator types 'maybe' or 'yes please' → treated as refuse."""
    stdin = io.StringIO("maybe\n")
    stdout = io.StringIO()
    prompter = StdinApprovalPrompter(stdin=stdin, stdout=stdout)
    assert prompter.prompt(_descriptor(), _call()) == "n"
    assert "unrecognised" in stdout.getvalue()


def test_stdin_prompter_redacts_marked_arguments_in_display() -> None:
    descriptor = ToolDescriptor(
        name="vault_read",
        description="read a secret",
        redacted_arg_names=("token",),
    )
    call = ToolCall(
        call_id="c-1", name="vault_read",
        arguments={"path": "/etc/x", "token": "super-secret"},
    )
    stdin = io.StringIO("y\n")
    stdout = io.StringIO()
    prompter = StdinApprovalPrompter(stdin=stdin, stdout=stdout)
    prompter.prompt(descriptor, call)
    out = stdout.getvalue()
    assert "<redacted>" in out
    assert "super-secret" not in out


# --------------------------------------------------------------------- #
# Decision is a simple data container                                   #
# --------------------------------------------------------------------- #


def test_approval_decision_default_needs_prompt_is_false() -> None:
    d = ApprovalDecision(outcome=ApprovalOutcome.AUTO_APPROVED)
    assert d.needs_prompt is False

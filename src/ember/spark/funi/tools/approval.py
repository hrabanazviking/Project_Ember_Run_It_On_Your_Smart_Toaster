"""Approval-policy resolution + the operator prompter (ADR 0011 §2.4-§2.6).

Two surfaces:

1. :func:`resolve` — pure policy resolution. Takes a descriptor, the
   operator's config overrides, and the session-approval set; returns
   an :class:`ApprovalDecision` containing the :class:`ApprovalOutcome`
   and a flag telling the caller whether to consult an interactive
   prompter.

2. :class:`StdinApprovalPrompter` — the interactive surface for
   ``PER_CALL`` decisions. Reads y/n/always from a ``TextIO`` and
   writes prompts to another ``TextIO``. Munnr (Phase 16) wires its
   stdin/stdout through this; tests inject ``io.StringIO`` instances.

Policy resolution is deliberately separate from the prompter so the
test surface stays small. The decision tree in :func:`resolve` is the
load-bearing logic; the prompter is just a function that returns one
of three strings.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, Protocol, TextIO, runtime_checkable

from ember.schemas.tool import (
    ApprovalOutcome,
    ApprovalPolicy,
    ToolCall,
    ToolDescriptor,
)

PromptAnswer = Literal["y", "n", "always"]


# --------------------------------------------------------------------- #
# Decision                                                              #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class ApprovalDecision:
    """The result of :func:`resolve`.

    When ``needs_prompt`` is True the caller must consult an
    :class:`ApprovalPrompter` and re-call :func:`resolve_with_answer`
    with the operator's response. Otherwise ``outcome`` is final.
    """

    outcome: ApprovalOutcome
    needs_prompt: bool = False


# --------------------------------------------------------------------- #
# Prompter Protocol                                                     #
# --------------------------------------------------------------------- #


@runtime_checkable
class ApprovalPrompter(Protocol):
    """The minimum surface every interactive prompter satisfies.

    Munnr's CLI prompter, Hjarta's wizard prompter, and the scripted
    test prompter all match this shape. ADR 0011 §2.6.
    """

    def prompt(
        self, descriptor: ToolDescriptor, call: ToolCall,
    ) -> PromptAnswer: ...


class StdinApprovalPrompter:
    """Read y/n/always from a ``TextIO``.

    Default stdin / stdout / stderr are used unless an injected pair is
    given. The renderer is intentionally minimal — Phase 16's Munnr
    integration replaces the prompt body with one that uses
    ``render.render_tool_call_proposal`` instead.
    """

    _VALID: tuple[PromptAnswer, ...] = ("y", "n", "always")

    def __init__(
        self,
        *,
        stdin: TextIO | None = None,
        stdout: TextIO | None = None,
    ) -> None:
        self._stdin = stdin
        self._stdout = stdout

    def prompt(
        self, descriptor: ToolDescriptor, call: ToolCall,
    ) -> PromptAnswer:
        import sys  # noqa: PLC0415 — only loaded when prompter is actually used

        stdin = self._stdin if self._stdin is not None else sys.stdin
        stdout = self._stdout if self._stdout is not None else sys.stdout

        body = _render_proposal(descriptor, call)
        stdout.write(body)
        stdout.write("approve this call? [y/n/always] ")
        stdout.flush()

        # Read a single line; trim. Default to "n" on EOF — safer to
        # refuse than to silently approve when stdin closes.
        raw = stdin.readline()
        if not raw:
            return "n"
        answer = raw.strip().lower()
        if answer in self._VALID:
            return answer  # type: ignore[return-value]
        # Unknown reply → refuse. Don't loop; Munnr re-prompts at the
        # next REPL turn if Funi proposes again.
        stdout.write(f"unrecognised answer {answer!r}; treating as 'n'\n")
        stdout.flush()
        return "n"


def _render_proposal(descriptor: ToolDescriptor, call: ToolCall) -> str:
    """Minimal terminal rendering — Phase 16 supersedes via render.py."""
    lines = [
        "",
        f"tool proposal: {descriptor.name}",
        f"  description: {descriptor.description}",
        "  arguments:",
    ]
    for name, value in call.arguments.items():
        redacted = name in descriptor.redacted_arg_names
        shown = "<redacted>" if redacted else repr(value)
        lines.append(f"    {name}: {shown}")
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------- #
# Policy resolution                                                     #
# --------------------------------------------------------------------- #


def resolve(
    descriptor: ToolDescriptor,
    *,
    config_overrides: Mapping[str, ApprovalPolicy] | None = None,
    session_standing: frozenset[str] | None = None,
    standing_trust_all: bool = False,
) -> ApprovalDecision:
    """Decide whether a tool call needs an interactive prompt.

    Resolution order per ADR 0011 §2.4:

    1. ``descriptor.required_approval == FORBIDDEN`` →
       ``FORBIDDEN_BY_REGISTRY`` (cannot be overridden by config).
    2. ``standing_trust_all=True`` → every ``PER_CALL`` becomes
       ``AUTO_APPROVED`` (operator's "trust everything" knob).
    3. Descriptor says ``STANDING`` → ``AUTO_APPROVED`` (unless config
       downgrades to ``PER_CALL`` — descriptor is the floor on safety,
       not on permissiveness).
    4. ``session_standing`` carries the tool's name → ``AUTO_APPROVED``
       (operator typed ``always`` earlier in this session).
    5. Otherwise → ``PER_CALL``, caller must prompt.

    Config can downgrade ``STANDING`` to ``PER_CALL`` (more strict);
    config cannot upgrade ``PER_CALL`` to ``STANDING``. Pin the safer
    direction.
    """
    overrides = config_overrides or {}
    session = session_standing or frozenset()

    # 1. FORBIDDEN is the absolute floor.
    if descriptor.required_approval is ApprovalPolicy.FORBIDDEN:
        return ApprovalDecision(ApprovalOutcome.FORBIDDEN_BY_REGISTRY)

    # 2. Operator's global trust-everything knob.
    if standing_trust_all:
        return ApprovalDecision(ApprovalOutcome.AUTO_APPROVED)

    # 3. Compute the effective policy:
    #    - start with descriptor's required_approval
    #    - config can downgrade STANDING → PER_CALL (more strict), but
    #      not upgrade PER_CALL → STANDING.
    effective = descriptor.required_approval
    override = overrides.get(descriptor.name)
    if override is ApprovalPolicy.PER_CALL and effective is ApprovalPolicy.STANDING:
        effective = ApprovalPolicy.PER_CALL
    # Forbidding in config is honored too (paranoia mode for an
    # otherwise-STANDING tool).
    if override is ApprovalPolicy.FORBIDDEN:
        return ApprovalDecision(ApprovalOutcome.FORBIDDEN_BY_REGISTRY)

    if effective is ApprovalPolicy.STANDING:
        return ApprovalDecision(ApprovalOutcome.AUTO_APPROVED)

    # 4. Session-level "always" override.
    if descriptor.name in session:
        return ApprovalDecision(ApprovalOutcome.AUTO_APPROVED)

    # 5. Per-call prompt required.
    return ApprovalDecision(
        ApprovalOutcome.APPROVED_THIS_CALL,  # placeholder — set after prompt
        needs_prompt=True,
    )


def resolve_with_answer(answer: PromptAnswer) -> ApprovalOutcome:
    """Map a prompter answer to a final outcome.

    ``always`` → ``APPROVED_FOR_SESSION`` (caller should add the tool
    name to its session-standing set). ``y`` → ``APPROVED_THIS_CALL``.
    Anything else → ``DENIED``.
    """
    if answer == "y":
        return ApprovalOutcome.APPROVED_THIS_CALL
    if answer == "always":
        return ApprovalOutcome.APPROVED_FOR_SESSION
    return ApprovalOutcome.DENIED


__all__ = [
    "ApprovalDecision",
    "ApprovalPrompter",
    "PromptAnswer",
    "StdinApprovalPrompter",
    "resolve",
    "resolve_with_answer",
]

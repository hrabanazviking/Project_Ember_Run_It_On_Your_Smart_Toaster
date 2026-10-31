"""Approvals in plain words (E-027).

E-026 gave every tool a stated permission shape; this module turns
that shape into words a non-technical person can act on. An approval
prompt is a *security decision made by a normal person*, so it must
say, in ordinary language:

- **what** Ember wants to do (the action, with the one or two
  details that matter — never a raw argument dump as the headline);
- **what it can and cannot reach** (the E-026 access class, in
  words: "reads your own information, changes nothing, sends
  nothing" — never the class name itself);
- **what answering means** — the rememberable scopes. Ember offers
  exactly two scopes a person can hold in their head:

  1. *just this once* — this one call, nothing remembered;
  2. *while we're chatting* — this tool, for the rest of this
     chat session only; forgotten when the chat ends. It is
     **never** "forever": nothing in the prompt path writes a
     permanent grant (permanent trust is the operator's deliberate
     config act — ``standing_trust`` / ``approval_overrides`` —
     not something a chat answer can create).

  Scope 2 is offered **only when the E-026 gate would honour it**
  (a read-only access class and no truthy guarded argument in this
  call). Before E-027 the prompter offered ``always`` for every
  call; for a dangerous or guarded call the gate then asked again
  anyway, so the person's "always" was silently worthless. Now the
  prompt says plainly *why* it asks every time, and an ``always``
  typed anyway is counted as a yes for this once only — with that
  stated on screen, never silently reinterpreted.

This module is the single place that knows these wordings;
:mod:`ember.spark.funi.tools.approval`'s prompter and Munnr's
proposal renderer both draw from it.
"""

from __future__ import annotations

from dataclasses import dataclass

from ember.schemas.tool import ToolAccess, ToolCall, ToolDescriptor
from ember.spark.funi.tools.permissions import (
    guarded_argument_in_use,
    may_auto_approve,
)

_MAX_VALUE_CHARS = 200

# --------------------------------------------------------------------- #
# What Ember wants to do                                                #
# --------------------------------------------------------------------- #


def _shown(descriptor: ToolDescriptor, call: ToolCall, name: str) -> str | None:
    """One argument's display value, or None (absent or redacted)."""
    if name in descriptor.redacted_arg_names:
        return None
    value = call.arguments.get(name)
    if value is None:
        return None
    text = str(value)
    if len(text) > _MAX_VALUE_CHARS:
        text = text[:_MAX_VALUE_CHARS] + "..."
    return text


def plain_action(descriptor: ToolDescriptor, call: ToolCall) -> str:
    """One plain sentence: what Ember wants to do in this call.

    The three first-party tools get sentences built from the detail
    that matters (the search words, the file, the address). Any
    other tool falls back to its own description, which tool authors
    already write for humans; a description-less tool is named.
    """
    if descriptor.name == "search_well":
        query = _shown(descriptor, call, "query")
        if query:
            return f'Search the things you have saved with Ember for "{query}".'
    elif descriptor.name == "read_local_file":
        path = _shown(descriptor, call, "path")
        if path:
            return f"Read one of your files: {path}."
    elif descriptor.name == "fetch_url":
        url = _shown(descriptor, call, "url")
        if url:
            return f"Fetch a page from the internet: {url}."
    if descriptor.description:
        return descriptor.description
    return f"Use the tool called {descriptor.name}."


# --------------------------------------------------------------------- #
# What it can and cannot reach                                          #
# --------------------------------------------------------------------- #

_REACH: dict[ToolAccess, str] = {
    ToolAccess.READ_ONLY: (
        "It can only look things up. It cannot change, send, "
        "or delete anything."
    ),
    ToolAccess.PRIVATE_READ: (
        "It reads your own information, on this computer only. "
        "It cannot change or delete anything, and nothing is "
        "sent anywhere."
    ),
    ToolAccess.NETWORK: (
        "It goes out from your computer to the internet. It does "
        "not change your files, but the place it visits will see "
        "that a request came from your computer."
    ),
    ToolAccess.WRITE: (
        "It can change things on your computer. Read the details "
        "carefully before you say yes."
    ),
    ToolAccess.EXECUTE: (
        "It runs a program or command on your computer. Read the "
        "details carefully before you say yes."
    ),
    ToolAccess.EXTERNAL: (
        "Another program, outside Ember, does the work. Ember "
        "cannot fully see or control what that program does."
    ),
    ToolAccess.UNSPECIFIED: (
        "Ember has no statement of what this tool can reach. "
        "Be careful, and say no if you are unsure."
    ),
}


def plain_reach(descriptor: ToolDescriptor) -> str:
    """The access class in ordinary words — never the class name."""
    return _REACH[descriptor.access]


def plain_guarded_warning(
    descriptor: ToolDescriptor, call: ToolCall,
) -> str | None:
    """Plain warning when this call widens the tool's reach.

    Returns None when no guarded argument is in use.
    """
    name = guarded_argument_in_use(descriptor, call.arguments)
    if name is None:
        return None
    if descriptor.name == "fetch_url" and name == "allow_private_addresses":
        return (
            "Careful: this request also asks to reach private "
            "addresses on your own home network, not just the "
            "public internet. That is a wider reach than usual."
        )
    return (
        f"Careful: this request also turns on '{name}', which "
        "gives this tool a wider reach than usual."
    )


# --------------------------------------------------------------------- #
# The rememberable scopes                                               #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class ApprovalChoice:
    """One answer the person may give, and what it means in plain words."""

    answer: str
    meaning: str


def can_remember(
    descriptor: ToolDescriptor, call: ToolCall,
) -> bool:
    """Would a "don't ask again" answer actually be honoured?

    Exactly the E-026 gate's condition: a read-only access class
    and no truthy guarded argument in this call.
    """
    return may_auto_approve(descriptor) and (
        guarded_argument_in_use(descriptor, call.arguments) is None
    )


def offered_choices(
    descriptor: ToolDescriptor, call: ToolCall,
) -> tuple[ApprovalChoice, ...]:
    """The choices for this call, each with its scope in plain words.

    ``always`` appears only when :func:`can_remember` — and its
    meaning says *while we're chatting* and *forgotten when the
    chat ends*, because that is the true scope of a session grant.
    """
    choices = [
        ApprovalChoice("y", "Yes — just this once."),
    ]
    if can_remember(descriptor, call):
        choices.append(ApprovalChoice(
            "always",
            "Yes — and don't ask me again about this tool while "
            "we're chatting. (Forgotten when the chat ends; it is "
            "never forever.)",
        ))
    choices.append(ApprovalChoice("n", "No — don't do it."))
    return tuple(choices)


def why_asked_every_time(
    descriptor: ToolDescriptor, call: ToolCall,
) -> str | None:
    """Why no "don't ask again" is offered for this call, plainly.

    None when remembering *is* offered. Otherwise one sentence the
    person can understand — the reason is the access class or the
    widened reach, never a policy name.
    """
    if can_remember(descriptor, call):
        return None
    if guarded_argument_in_use(descriptor, call.arguments) is not None:
        return (
            "Because this request widens what the tool can reach, "
            "Ember asks about it every time — a yes here means "
            "just this once."
        )
    return {
        ToolAccess.NETWORK: (
            "Because this goes out to the internet, Ember asks "
            "about it every time — a yes here means just this once."
        ),
        ToolAccess.WRITE: (
            "Because this can change things on your computer, "
            "Ember asks about it every time — a yes here means "
            "just this once."
        ),
        ToolAccess.EXECUTE: (
            "Because this runs something on your computer, Ember "
            "asks about it every time — a yes here means just "
            "this once."
        ),
        ToolAccess.EXTERNAL: (
            "Because the work happens in another program outside "
            "Ember, Ember asks about it every time — a yes here "
            "means just this once."
        ),
        ToolAccess.UNSPECIFIED: (
            "Because Ember has no statement of what this tool can "
            "reach, Ember asks about it every time — a yes here "
            "means just this once."
        ),
    }.get(descriptor.access, (
        "Ember asks about this every time — a yes here means "
        "just this once."
    ))


# --------------------------------------------------------------------- #
# The whole prompt                                                      #
# --------------------------------------------------------------------- #


def render_plain_proposal(descriptor: ToolDescriptor, call: ToolCall) -> str:
    """The full plain-language approval prompt body.

    Structure a non-technical person can scan: what Ember wants to
    do, what it can and cannot do, the exact details it was given
    (redacted arguments stay hidden), then the choices with their
    scopes. No policy names, no class names, no jargon.
    """
    lines = [
        "",
        "Ember is asking your permission.",
        "",
        "What Ember wants to do:",
        f"  {plain_action(descriptor, call)}",
        "",
        "What this can and cannot do:",
        f"  {plain_reach(descriptor)}",
    ]
    warning = plain_guarded_warning(descriptor, call)
    if warning is not None:
        lines.append(f"  {warning}")
    lines += ["", "The details Ember was given:"]
    if call.arguments:
        for name, value in call.arguments.items():
            if name in descriptor.redacted_arg_names:
                lines.append(f"  {name}: <hidden — Ember will not show this>")
            else:
                text = repr(value)
                if len(text) > _MAX_VALUE_CHARS:
                    text = text[:_MAX_VALUE_CHARS] + "..."
                lines.append(f"  {name}: {text}")
    else:
        lines.append("  (nothing else)")
    lines += ["", "Your choices:"]
    for choice in offered_choices(descriptor, call):
        lines.append(f"  {choice.answer} — {choice.meaning}")
    reason = why_asked_every_time(descriptor, call)
    if reason is not None:
        lines += ["", reason]
    lines.append("")
    return "\n".join(lines)


__all__ = [
    "ApprovalChoice",
    "can_remember",
    "offered_choices",
    "plain_action",
    "plain_guarded_warning",
    "plain_reach",
    "render_plain_proposal",
    "why_asked_every_time",
]

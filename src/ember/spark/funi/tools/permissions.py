"""Permission shapes + the auto-approval gate (E-026).

Every tool in Ember now states its permission shape on its
descriptor (``ember.schemas.tool.ToolAccess``):

- ``READ_ONLY`` / ``PRIVATE_READ`` — the tool reads, never writes,
  never leaves the machine. These are the only access classes that
  may ever be *auto-approved* (standing approval, a session
  "always", or the operator's ``standing_trust`` knob).
- ``NETWORK`` / ``WRITE`` / ``EXECUTE`` / ``EXTERNAL`` — dangerous
  classes. A call to such a tool is **always approved per call**,
  whatever its descriptor declares and whatever blanket trust the
  operator configured. An author cannot make a dangerous tool
  silent by declaring ``STANDING``, and an operator's blanket
  ``standing_trust`` cannot wave it through either; the operator
  can still forbid it outright, or approve each call as it comes.
- ``UNSPECIFIED`` — no shape stated. Gated exactly like a
  dangerous class: no stated shape, no standing approval.

Independently of access class, a call that carries a truthy
*guarded argument* (``ToolDescriptor.guarded_arguments`` — an
argument that widens the tool's reach, such as ``fetch_url``'s
``allow_private_addresses``) always prompts per call. Guarded
arguments are supplied by the model; auto-approval would let the
model widen its own reach without the operator ever seeing that
specific call.

This module is the single place that knows these rules;
:func:`ember.spark.funi.tools.approval.resolve` consults it, so
every approval path (chat loop today, any future caller) inherits
the gate by construction.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ember.schemas.tool import ToolAccess, ToolDescriptor

# Access classes that may be auto-approved when every other rule
# also allows it. Everything else — including UNSPECIFIED — is
# per-call-only.
AUTO_APPROVABLE_ACCESSES: frozenset[ToolAccess] = frozenset({
    ToolAccess.READ_ONLY,
    ToolAccess.PRIVATE_READ,
})


def may_auto_approve(descriptor: ToolDescriptor) -> bool:
    """Can any blanket mechanism auto-approve this tool at all?

    True only for the read-only access classes. Note this is a
    necessary condition, not a sufficient one: the descriptor's
    approval policy, config overrides, and the call's guarded
    arguments still apply (see :mod:`.approval`).
    """
    return descriptor.access in AUTO_APPROVABLE_ACCESSES


def guarded_argument_in_use(
    descriptor: ToolDescriptor,
    arguments: Mapping[str, object] | None,
) -> str | None:
    """Name the first truthy guarded argument in ``arguments``.

    Returns None when the call carries no guarded argument, or
    carries it falsy (the reach is not widened). A guarded argument
    that is absent falls back to its parameter default in the
    registry's validation shape — a tool whose guarded argument
    defaults to truthy would widen by default, so descriptors must
    declare guarded arguments with a falsy default (the first-party
    inventory tests pin this for ``fetch_url``).
    """
    if not arguments:
        return None
    for name in descriptor.guarded_arguments:
        if arguments.get(name):
            return name
    return None


@dataclass(frozen=True, slots=True)
class ToolPermissionShape:
    """One tool's full permission shape, as stated for the inventory.

    ``approval`` is the descriptor's declared policy;
    ``auto_approvable`` is what the gate will actually honour —
    for a dangerous or unspecified tool declaring ``STANDING``,
    the two disagree, and ``auto_approvable`` is the truth.
    """

    name: str
    access: ToolAccess
    approval: str
    auto_approvable: bool
    guarded_arguments: tuple[str, ...]
    timeout_s: float


def permission_shape(descriptor: ToolDescriptor) -> ToolPermissionShape:
    """Project a descriptor onto its stated permission shape."""
    return ToolPermissionShape(
        name=descriptor.name,
        access=descriptor.access,
        approval=descriptor.required_approval.value,
        auto_approvable=may_auto_approve(descriptor),
        guarded_arguments=descriptor.guarded_arguments,
        timeout_s=descriptor.timeout_s,
    )


def tool_inventory(
    descriptors: Mapping[str, ToolDescriptor] | None = None,
) -> tuple[ToolPermissionShape, ...]:
    """The inventory of every registered tool's permission shape.

    With no argument, reads the process-global registry (the live
    inventory). A mapping may be supplied by tests/callers that hold
    descriptors directly. Sorted by tool name for a stable record.
    """
    if descriptors is None:
        from ember.spark.funi.tools.registry import list_tools  # noqa: PLC0415

        descriptors = {d.name: d for d in list_tools()}
    return tuple(
        permission_shape(descriptors[name]) for name in sorted(descriptors)
    )


__all__ = [
    "AUTO_APPROVABLE_ACCESSES",
    "ToolPermissionShape",
    "guarded_argument_in_use",
    "may_auto_approve",
    "permission_shape",
    "tool_inventory",
]

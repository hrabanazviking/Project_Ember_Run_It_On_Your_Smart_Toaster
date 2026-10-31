"""Tool-use schemas — ADR 0011.

The five dataclasses and three StrEnums that the Phase-14 tool framework
hangs on. Frozen + slotted per the rest of ``ember.schemas``; validation
is the registry's job, not the schema's.

The :class:`ToolCall` here replaces the placeholder in
:mod:`ember.schemas.funi` (which re-exports it for backwards
compatibility — see ADR 0011 §5).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

# --------------------------------------------------------------------- #
# Parameter schemas                                                     #
# --------------------------------------------------------------------- #


class ToolParameterKind(StrEnum):
    """The six kinds the stdlib-validator understands.

    Anything more exotic (nested objects, lists of objects, etc.) should
    surface as a tool author's redesign, not a schema-language sprawl.
    Per ADR 0011 §2.2 — jsonschema is deliberately out of scope.
    """

    STRING  = "string"
    INTEGER = "integer"
    FLOAT   = "float"
    BOOLEAN = "boolean"
    PATH    = "path"     # validated as a non-empty str; tool author handles expansion
    URL     = "url"      # validated as ``http(s)://...`` minimum


@dataclass(frozen=True, slots=True)
class ToolParameter:
    """One declared parameter of a tool.

    ``required=True`` and no default → registry refuses the call when
    the argument is missing. ``required=False`` and no default → the
    argument is optional and the tool's ``execute`` must handle absence.
    """

    kind: ToolParameterKind
    description: str
    required: bool = True
    default: object | None = None
    enum: tuple[str, ...] | None = None


# --------------------------------------------------------------------- #
# Approval policy                                                       #
# --------------------------------------------------------------------- #


class ApprovalPolicy(StrEnum):
    """The three approval lanes per ADR 0011 §2.4."""

    STANDING  = "standing"    # auto-approve every call (operator opt-in)
    PER_CALL  = "per_call"    # operator approves each invocation (default)
    FORBIDDEN = "forbidden"   # tool refuses to register at all


class ToolAccess(StrEnum):
    """What a tool can reach — its permission shape (E-026).

    Approval (``required_approval``) says *how often the operator is
    asked*; access says *what the tool can touch when it runs*. The
    two are independent: a tool may be asked about every call yet
    reach very little, or be pre-approved yet read private data.

    ``UNSPECIFIED`` is the default for a descriptor that states no
    shape. It is treated as dangerous by the approval gate
    (``ember.spark.funi.tools.permissions``): a tool that does not
    say what it can reach may never be auto-approved — no stated
    shape, no standing approval.
    """

    READ_ONLY    = "read_only"     # reads non-private data; no writes, no egress
    PRIVATE_READ = "private_read"  # reads the operator's own data; no writes, no egress
    NETWORK      = "network"       # leaves the machine (egress / SSRF surface)
    WRITE        = "write"         # mutates local state
    EXECUTE      = "execute"       # runs code or commands
    EXTERNAL     = "external"      # effects delegated to an external server; unknown
    UNSPECIFIED  = "unspecified"   # no shape stated — gated as dangerous


class ApprovalOutcome(StrEnum):
    """Typed outcomes per ADR 0011 §2.5 — distinguishes denial vs
    invalid-args vs forbidden vs missing-tool so the audit log
    classifies each failure mode cleanly."""

    AUTO_APPROVED         = "auto_approved"
    APPROVED_THIS_CALL    = "approved_this_call"
    APPROVED_FOR_SESSION  = "approved_for_session"
    DENIED                = "denied"
    INVALID_ARGUMENTS     = "invalid_arguments"
    FORBIDDEN_BY_REGISTRY = "forbidden_by_registry"
    NO_SUCH_TOOL          = "no_such_tool"


# --------------------------------------------------------------------- #
# Descriptor / call / reply                                             #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class ToolDescriptor:
    """What the registry knows about a tool.

    ``redacted_arg_names`` is the set of argument keys the audit log
    replaces with ``"<redacted>"`` — for tools that accept secrets,
    sensitive paths, or anything the operator would not want logged.
    """

    name: str
    description: str
    parameters_schema: Mapping[str, ToolParameter] = field(default_factory=dict)
    required_approval: ApprovalPolicy = ApprovalPolicy.PER_CALL
    redacted_arg_names: tuple[str, ...] = ()
    timeout_s: float = 10.0
    # Permission shape (E-026). ``access`` states what the tool can
    # reach; ``guarded_arguments`` names arguments that *widen* that
    # reach (an escape hatch such as fetch_url's
    # ``allow_private_addresses``). A call carrying a truthy guarded
    # argument always prompts per call — standing approval, session
    # "always", and standing_trust never waive it, because the
    # argument is supplied by the model, not the operator.
    access: ToolAccess = ToolAccess.UNSPECIFIED
    guarded_arguments: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ToolCall:
    """A structured tool invocation produced by Funi.

    ``call_id`` is a UUID4 string assigned by the Funi adapter when it
    parses the reply (per ADR 0011 §2.1). It joins ``ToolCall`` to
    ``ToolReply`` in the audit log and lets Munnr render approval
    prompts that match the eventual reply.
    """

    call_id: str
    name: str
    arguments: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ToolReply:
    """What the framework hands back to Funi after execution.

    ``output`` is the operator/Funi-facing text; ``error`` is non-None
    when the call failed (denied, invalid args, timeout, exception).
    Both being populated is *legal* — a tool can produce partial output
    *and* report an error.
    """

    call_id: str
    output: str = ""
    error: str | None = None
    elapsed_s: float = 0.0


# --------------------------------------------------------------------- #
# Errors                                                                #
# --------------------------------------------------------------------- #


class ToolError(Exception):
    """Raised inside the tool framework when the registry or audit log
    cannot satisfy a contract.

    The framework's *execution* path turns tool-side exceptions into
    :class:`ToolReply` values — this exception is for framework-level
    failures (duplicate registration, forbidden-at-registration,
    audit-log path unwritable, etc.) that surface to the test harness
    and to integration callers.
    """


__all__ = [
    "ApprovalOutcome",
    "ApprovalPolicy",
    "ToolAccess",
    "ToolCall",
    "ToolDescriptor",
    "ToolError",
    "ToolParameter",
    "ToolParameterKind",
    "ToolReply",
]

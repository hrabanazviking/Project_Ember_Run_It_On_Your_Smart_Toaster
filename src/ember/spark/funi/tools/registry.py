"""Process-global tool registry (ADR 0011 §2.3).

Tools register themselves at import time::

    from ember.spark.funi.tools.registry import register
    from ember.schemas.tool import ToolDescriptor, ToolParameter, ToolParameterKind

    _DESCRIPTOR = ToolDescriptor(
        name="search_well",
        description="...",
        parameters_schema={
            "query": ToolParameter(kind=ToolParameterKind.STRING, description="..."),
            "k":     ToolParameter(kind=ToolParameterKind.INTEGER, description="...", default=5),
        },
    )

    def _execute(call): ...

    register(_DESCRIPTOR, _execute)

The registry refuses to register any descriptor whose
``required_approval`` is :class:`ApprovalPolicy.FORBIDDEN`. That is the
mechanical "never executable" lane from ADR 0011 §2.4 — a forbidden
tool can't even appear in ``list_tools()``.

The registry is process-global. Tests use :func:`clear` between cases.
"""

from __future__ import annotations

import re
import threading
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from ember.schemas.tool import (
    ApprovalPolicy,
    ToolCall,
    ToolDescriptor,
    ToolError,
    ToolParameter,
    ToolParameterKind,
    ToolReply,
)

# Type alias for tool executors; kept here so callers can name it
# without pulling Callable through every file.
ToolExecutor = Callable[[ToolCall], ToolReply]


@dataclass(frozen=True, slots=True)
class _Entry:
    descriptor: ToolDescriptor
    executor: ToolExecutor


_REGISTRY: dict[str, _Entry] = {}
_LOCK = threading.RLock()

# Tool names must be alphanumeric + underscore. The audit log keys on
# this name, the model proposes calls by this name, and the operator
# reads it in approval prompts; whitespace / control chars / shell
# metachars would all confuse one of those readers. The constraint also
# matches the OpenAI / Anthropic tool-name conventions, so a tool that
# passes here can be safely surfaced over either wire format.
_TOOL_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")


def register(descriptor: ToolDescriptor, executor: ToolExecutor) -> None:
    """Register a tool by descriptor + executor.

    Raises :class:`ToolError` when:

    - the descriptor's ``required_approval`` is ``FORBIDDEN`` (mechanical
      "never executable"),
    - a tool with the same name is already registered (re-registration
      is an error — tests use :func:`clear` between cases),
    - the descriptor's ``name`` is empty, contains whitespace or
      control characters, or violates the allowed identifier shape
      (alphanumeric + underscore, leading letter or underscore, 1-64
      chars),
    - ``executor`` is not callable.
    """
    if not isinstance(descriptor.name, str) or not _TOOL_NAME_RE.match(
        descriptor.name
    ):
        raise ToolError(
            f"tool name {descriptor.name!r} is invalid; must match "
            f"[A-Za-z_][A-Za-z0-9_]{{0,63}} (alphanumeric + underscore, "
            f"1-64 chars, no whitespace or control characters)"
        )
    if not callable(executor):
        raise ToolError(
            f"executor for tool {descriptor.name!r} is not callable "
            f"(got {type(executor).__name__}); refusing to register"
        )
    if descriptor.required_approval is ApprovalPolicy.FORBIDDEN:
        raise ToolError(
            f"tool {descriptor.name!r} is FORBIDDEN at the registry level "
            f"(ADR 0011 §2.4); refusing to register"
        )
    with _LOCK:
        if descriptor.name in _REGISTRY:
            raise ToolError(
                f"tool {descriptor.name!r} is already registered; "
                f"call ember.spark.funi.tools.registry.clear() in tests"
            )
        _REGISTRY[descriptor.name] = _Entry(descriptor, executor)


def lookup(name: str) -> tuple[ToolDescriptor, ToolExecutor] | None:
    """Return ``(descriptor, executor)`` for the named tool, or None.

    The framework's call-site reads None as
    :class:`ApprovalOutcome.NO_SUCH_TOOL` and produces a typed
    :class:`ToolReply` rather than raising.
    """
    with _LOCK:
        entry = _REGISTRY.get(name)
    if entry is None:
        return None
    return entry.descriptor, entry.executor


def list_tools() -> list[ToolDescriptor]:
    """Return every registered descriptor, ordered by registration name.

    Sorted output gives Munnr a stable display order and lets the audit
    log differ from a baseline cleanly in operator review.
    """
    with _LOCK:
        return sorted(
            (entry.descriptor for entry in _REGISTRY.values()),
            key=lambda d: d.name,
        )


def is_registered(name: str) -> bool:
    """Cheap presence check that avoids paying for the lookup tuple."""
    with _LOCK:
        return name in _REGISTRY


def clear() -> None:
    """Test helper — drop every registration.

    Production code never calls this. Tools register at import time and
    stay registered for the process lifetime.
    """
    with _LOCK:
        _REGISTRY.clear()


# --------------------------------------------------------------------- #
# Argument validation                                                   #
# --------------------------------------------------------------------- #


def validate_arguments(
    descriptor: ToolDescriptor,
    arguments: Mapping[str, object],
) -> str | None:
    """Validate ``arguments`` against the descriptor's parameter schema.

    Returns None on success, or an operator-readable error string. The
    framework treats a non-None return as
    :class:`ApprovalOutcome.INVALID_ARGUMENTS` and produces
    :class:`ToolReply(error=..., output="")` without executing the
    tool.

    Validation covers (per ADR 0011 §2.2):

    - Required parameters present.
    - Type-kind match (STRING / INTEGER / FLOAT / BOOLEAN / PATH / URL).
    - ``enum`` constraint when set.
    - No unexpected keys (catches typos before the tool sees them).
    """
    schema = descriptor.parameters_schema

    # 1. Unknown keys.
    extra = set(arguments) - set(schema)
    if extra:
        return (
            f"unexpected argument(s): {sorted(extra)!r}; "
            f"this tool accepts {sorted(schema)!r}"
        )

    # 2. Required-but-missing.
    for arg_name, param in schema.items():
        if param.required and arg_name not in arguments and param.default is None:
            return f"missing required argument {arg_name!r}"

    # 3. Per-argument type + enum.
    for arg_name, value in arguments.items():
        param = schema[arg_name]
        err = _check_kind(arg_name, param, value)
        if err is not None:
            return err
        if param.enum is not None and value not in param.enum:
            return (
                f"argument {arg_name!r} must be one of {list(param.enum)}, "
                f"got {value!r}"
            )

    return None


def _check_kind(  # noqa: PLR0911 — one return per kind is the readable shape
    arg_name: str, param: ToolParameter, value: object,
) -> str | None:
    """Stdlib type-kind validation per ADR 0011 §2.2.

    The PATH / URL kinds use string shape; tool authors do their own
    filesystem / scheme checks. Boolean is checked precisely (no
    int-as-bool slip).
    """
    kind = param.kind
    if kind is ToolParameterKind.STRING:
        if not isinstance(value, str):
            return _kind_mismatch(arg_name, "string", value)
    elif kind is ToolParameterKind.INTEGER:
        if isinstance(value, bool) or not isinstance(value, int):
            return _kind_mismatch(arg_name, "integer", value)
    elif kind is ToolParameterKind.FLOAT:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return _kind_mismatch(arg_name, "float", value)
    elif kind is ToolParameterKind.BOOLEAN:
        if not isinstance(value, bool):
            return _kind_mismatch(arg_name, "boolean", value)
    elif kind is ToolParameterKind.PATH:
        if not isinstance(value, str) or not value:
            return _kind_mismatch(arg_name, "non-empty path string", value)
    elif kind is ToolParameterKind.URL and (
        not isinstance(value, str)
        or not (value.startswith("http://") or value.startswith("https://"))
    ):
        return _kind_mismatch(arg_name, "http(s) URL string", value)
    return None


def _kind_mismatch(arg_name: str, expected: str, value: object) -> str:
    return (
        f"argument {arg_name!r} must be {expected}, "
        f"got {type(value).__name__!r}"
    )


__all__ = [
    "ToolExecutor",
    "clear",
    "is_registered",
    "list_tools",
    "lookup",
    "register",
    "validate_arguments",
]

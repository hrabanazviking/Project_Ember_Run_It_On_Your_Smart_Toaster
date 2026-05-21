"""Funi-side types: ContextItem, FuniReply, FuniHealth, Unavailable.

Per ``docs/architecture/DOMAIN_MAP.md`` §5.1 (Funi's minimum surface).
The :class:`Unavailable` value is the Funi-side parallel of
:class:`ember.schemas.errors.Disconnected` — Funi.open() returns
``FuniHandle | Unavailable`` rather than raising on runtime failure, so
Spark code handles the failure as a value.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

# --------------------------------------------------------------------- #
# Prompt context                                                        #
# --------------------------------------------------------------------- #


class ContextKind(StrEnum):
    EPISODE = "episode"
    CHUNK = "chunk"
    SYSTEM = "system"


@dataclass(frozen=True, slots=True)
class ContextItem:
    """One item Munnr stitches into the assembled prompt."""

    kind: ContextKind
    text: str
    metadata: Mapping[str, object] = field(default_factory=dict)


# --------------------------------------------------------------------- #
# Tool calls                                                            #
# --------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class ToolCall:
    """A structured tool invocation produced by Funi.

    Tools are not executed in the first slice (per
    ``docs/architecture/EMBER_FIRST_SLICE_PLAN.md`` §4). When the first
    slice ships, ``tools=None`` is the only mode used; this type is
    reserved for the later slice that introduces tool use.
    """

    name: str
    arguments: Mapping[str, object]


# --------------------------------------------------------------------- #
# Reply + health                                                        #
# --------------------------------------------------------------------- #


class FinishReason(StrEnum):
    STOP = "stop"
    LENGTH = "length"
    TOOL_CALL = "tool_call"
    REFUSED = "refused"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class FuniReply:
    """One Funi turn's output."""

    text: str
    finish_reason: FinishReason
    tool_calls: tuple[ToolCall, ...] = ()
    model_id: str = ""
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


@dataclass(frozen=True, slots=True)
class FuniHealth:
    """What ``ember doctor`` reads from Funi."""

    model_id: str
    ram_use_bytes: int | None = None
    last_ok: datetime | None = None


# --------------------------------------------------------------------- #
# Non-raised failure value                                              #
# --------------------------------------------------------------------- #


class UnavailableReason(StrEnum):
    """Why Funi cannot answer right now."""

    NOT_LOADED = "not_loaded"
    OUT_OF_MEMORY = "out_of_memory"
    ENDPOINT_UNREACHABLE = "endpoint_unreachable"
    CONFIG_INVALID = "config_invalid"
    RUNTIME_NOT_INSTALLED = "runtime_not_installed"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Unavailable:
    """Funi cannot open or complete. Returned, not raised."""

    reason: UnavailableReason
    detail: str | None = None


__all__ = [
    "ContextItem",
    "ContextKind",
    "FinishReason",
    "FuniHealth",
    "FuniReply",
    "ToolCall",
    "Unavailable",
    "UnavailableReason",
]

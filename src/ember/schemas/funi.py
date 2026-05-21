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

# Re-export the canonical ToolCall from ember.schemas.tool. The
# Phase-14 promotion (ADR 0011 §5) moves the dataclass under
# ember.schemas.tool but preserves the funi-side import path so
# existing callers (FuniReply.tool_calls, integration tests) keep
# working without churn.
from ember.schemas.tool import ToolCall

# --------------------------------------------------------------------- #
# Prompt context                                                        #
# --------------------------------------------------------------------- #


class ContextKind(StrEnum):
    EPISODE = "episode"
    CHUNK = "chunk"
    SYSTEM = "system"
    TOOL_REPLY = "tool_reply"   # Phase 16 — feeds ToolReply back into next turn


@dataclass(frozen=True, slots=True)
class ContextItem:
    """One item Munnr stitches into the assembled prompt."""

    kind: ContextKind
    text: str
    metadata: Mapping[str, object] = field(default_factory=dict)


# --------------------------------------------------------------------- #
# Tool calls                                                            #
# --------------------------------------------------------------------- #


# ``ToolCall`` is defined in :mod:`ember.schemas.tool` per ADR 0011 §5
# and re-exported at the top of this module for backwards-compat.


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

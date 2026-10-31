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
    SUMMARY = "summary"         # E-021 — summary of window-dropped history
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
# Backend capabilities (E-022)                                          #
# --------------------------------------------------------------------- #


class StreamingMode(StrEnum):
    """How a backend produces a streamed reply.

    ``NATIVE`` — the backend streams incrementally itself.
    ``WRAPPED`` — the backend only completes whole replies;
    ``complete_streaming`` is the ``wrap_complete_as_stream``
    one-final-chunk wrapper (ADR 0009 §2.2). Consumers must not
    promise incremental output from a WRAPPED backend.
    ``NONE`` — the backend cannot stream at all.
    """

    NATIVE = "native"
    WRAPPED = "wrapped"
    NONE = "none"


@dataclass(frozen=True, slots=True)
class BackendCapabilities:
    """What one model backend can actually do — declared, not assumed.

    E-022: before this, the Funi contract was four methods and
    consumers (chat, doctor) had no way to ask a backend what it
    supports; capability claims lived only in prose docs and had
    already drifted (see the E-022 slice doc). Every implemented
    backend now carries one of these as its ``capabilities``
    attribute, and the registry in ``ember.spark.funi.handle``
    publishes the same value per runtime so the truth can be read
    without opening a connection.

    Fields are adapter-level truth. Where a capability also
    depends on the chosen model, that is said in the open:
    ``tool_calls_model_dependent`` means the adapter speaks the
    tool protocol but a specific model may still not emit calls
    (the FUNI_LOCAL_MODEL_OPTIONS ladder names the known case:
    ``phi3:mini`` does not emit ``tool_calls`` via Ollama).
    """

    runtime_kind: str
    streaming: StreamingMode
    tool_calls: bool
    tool_calls_model_dependent: bool = False
    token_counts: bool = False
    reports_ram_use: bool = False
    requires_endpoint: bool = False
    context_kinds: tuple[ContextKind, ...] = ()


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
    "BackendCapabilities",
    "ContextItem",
    "ContextKind",
    "FinishReason",
    "StreamingMode",
    "FuniHealth",
    "FuniReply",
    "ToolCall",
    "Unavailable",
    "UnavailableReason",
]

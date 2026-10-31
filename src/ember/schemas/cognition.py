"""Cognition-layer types: CognitionReply, CognitionHealth, CognitionUnavailable.

E-024 — the cognition layer is the optional layer *above* Funi:
where Funi (``ember.schemas.funi``) is one model backend answering
one prompt, a cognition provider runs a whole turn pipeline of its
own (routing, retrieval, scaffolding, candidate generation,
salvage, enforcement) and returns a finished answer. MindSpark
ThoughtForge is Ember's first — and, in this slice, candidate —
cognition provider, bound under the contract ThoughtForge itself
froze at its TF-034 (cognition API v1.0.0).

The failure value mirrors the Funi shape on purpose:
:class:`CognitionUnavailable` is returned, never raised, so Spark
code handles a missing/refused cognition layer as a value — the
same discipline as :class:`ember.schemas.funi.Unavailable` and
:class:`ember.schemas.errors.Disconnected`. A consumer on an
incompatible ThoughtForge API major version gets a truthful
refusal here (``VERSION_MISMATCH``), never silent corruption —
the Ember-side half of the rule ThoughtForge's TF-162 owns at its
service shape.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class CognitionUnavailableReason(StrEnum):
    """Why the cognition layer cannot answer right now."""

    DISABLED = "disabled"
    PROFILE_CANNOT_AFFORD = "profile_cannot_afford"
    RUNTIME_NOT_INSTALLED = "runtime_not_installed"
    VERSION_MISMATCH = "version_mismatch"
    CONFIG_INVALID = "config_invalid"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class CognitionUnavailable:
    """The cognition layer cannot open or think. Returned, not raised."""

    reason: CognitionUnavailableReason
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class CognitionReply:
    """One cognition turn's finished answer.

    ``mode``, ``enforcement_passed`` and ``citations`` are
    ThoughtForge's own FinalResponseRecord fields, carried through
    as reported — Ember states what the provider's turn record
    says, and claims nothing beyond it. ``token_count`` is the
    provider's count for the answer text (ThoughtForge's record
    carries no prompt/completion split, so none is invented here).
    """

    text: str
    provider: str = ""
    api_version: str = ""
    turn_id: str = ""
    mode: str = ""
    enforcement_passed: bool = False
    citations: tuple[str, ...] = ()
    token_count: int | None = None


@dataclass(frozen=True, slots=True)
class CognitionHealth:
    """What ``ember doctor``-shaped consumers read from the layer."""

    provider: str
    api_version: str = ""
    last_ok: datetime | None = None


__all__ = [
    "CognitionHealth",
    "CognitionReply",
    "CognitionUnavailable",
    "CognitionUnavailableReason",
]

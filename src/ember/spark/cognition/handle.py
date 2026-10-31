"""CognitionHandle protocol + open() registry (E-024).

The cognition layer sits *above* Funi: a Funi backend answers one
prompt with one completion, while a cognition provider runs a
whole turn pipeline of its own (routing, retrieval, scaffolding,
candidates, salvage, enforcement) and returns a finished answer.
``ember.spark.munnr.chat`` does not consume this layer yet — E-024
binds ThoughtForge as a *candidate* (the roadmap's word), with the
contract, the profile gate, and the adapter proven here; wiring
the candidate into the day-one chat turn is a later, deliberate
act, not a silent swap of the companion's mind.

Module-level :func:`open` dispatches on ``config.provider``. On
any refusal — layer disabled, profile cannot afford it, provider
not installed, provider API major mismatch — it returns
:class:`CognitionUnavailable` rather than raising, the Funi-side
discipline applied one layer up.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ember.schemas.cognition import (
    CognitionHealth,
    CognitionReply,
    CognitionUnavailable,
    CognitionUnavailableReason,
)
from ember.schemas.config import CognitionConfig, ConversationProfile
from ember.schemas.episode import Episode


@runtime_checkable
class CognitionHandle(Protocol):
    """Minimum public surface every cognition provider satisfies.

    ``provider`` / ``api_version`` are attributes, so (as with
    Funi's E-022 note) ``runtime_checkable`` isinstance checks
    verify the methods only — attribute presence is pinned by the
    E-024 conformance tests.
    """

    provider: str
    api_version: str

    def think(
        self,
        user_text: str,
        episodes: Sequence[Episode] = (),
    ) -> CognitionReply: ...
    def health(self) -> CognitionHealth: ...
    def close(self) -> None: ...


def open_cognition(
    config: CognitionConfig,
) -> CognitionHandle | CognitionUnavailable:
    """Open the configured cognition layer.

    Returns either a live :class:`CognitionHandle` or a typed
    :class:`CognitionUnavailable`. **Never raises.** The refusal
    order is deliberate — cheapest, most operator-actionable first:
    disabled → unaffordable profile → unknown provider → the
    provider binding's own open (install / version / config).
    """
    if not config.enabled:
        return CognitionUnavailable(
            reason=CognitionUnavailableReason.DISABLED,
            detail=(
                "the cognition layer is off (cognition.enabled is "
                "false); Ember's Funi turn is the companion's mind "
                "until an operator turns the candidate layer on"
            ),
        )
    if not config.affords():
        return CognitionUnavailable(
            reason=CognitionUnavailableReason.PROFILE_CANNOT_AFFORD,
            detail=(
                f"profile {config.profile.value!r} cannot afford the "
                "cognition layer: it runs a second full turn pipeline "
                "beside Funi, and the smallest profiles have no room "
                "for it (see E-024)"
            ),
        )
    if config.provider != "thoughtforge":
        return CognitionUnavailable(
            reason=CognitionUnavailableReason.RUNTIME_NOT_INSTALLED,
            detail=(
                f"cognition provider {config.provider!r} is not "
                "implemented in this build; 'thoughtforge' is the "
                "only provider (E-024)"
            ),
        )
    # Lazy import — ThoughtForge is an optional, heavy neighbour;
    # an Ember without it installed must still import and run.
    from ember.spark.cognition.thoughtforge import (  # noqa: PLC0415
        open as thoughtforge_open,
    )

    return thoughtforge_open(config)


@dataclass(frozen=True, slots=True)
class CognitionRegistration:
    """One provider's place in the cognition contract (E-024).

    ``afforded_profiles`` is the profile truth in one place: the
    profiles on which :func:`open_cognition` will even attempt the
    provider. ``api_major`` is the provider-API major the binding
    was written against (None for a provider with no binding).
    """

    provider: str
    implemented: bool
    api_major: int | None
    afforded_profiles: tuple[ConversationProfile, ...]


def cognition_registry() -> tuple[CognitionRegistration, ...]:
    """Every provider the config can name, with its contract truth.

    Exactly one entry in this build: ``thoughtforge``, bound
    against ThoughtForge's frozen cognition API v1 (TF-034), on
    every profile except the toaster — the smallest profile cannot
    afford a second turn pipeline, and the registry says so
    instead of letting the refusal look like a malfunction.
    """
    afforded = tuple(
        profile
        for profile in ConversationProfile
        if CognitionConfig(profile=profile).affords()
    )
    return (
        CognitionRegistration(
            provider="thoughtforge",
            implemented=True,
            api_major=1,
            afforded_profiles=afforded,
        ),
    )


__all__ = [
    "CognitionHandle",
    "CognitionRegistration",
    "cognition_registry",
    "open_cognition",
]

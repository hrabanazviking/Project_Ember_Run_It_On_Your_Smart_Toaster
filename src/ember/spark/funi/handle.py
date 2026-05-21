"""FuniHandle protocol + open() registry.

Per ``docs/architecture/DOMAIN_MAP.md`` §5.1. The :class:`FuniHandle`
Protocol is the *minimum surface* every Funi runtime adapter
implements; Spark code consumes it without naming the concrete runtime.

Module-level :func:`open` dispatches on ``config.runtime`` to the
matching adapter. On failure (config invalid, runtime not yet
implemented in this build) it returns :class:`Unavailable` rather than
raising — the Funi-side parallel of the Brunnr Disconnected contract.

In Phase 5 only ``ollama`` is implemented. ``llamacpp``, ``lmstudio``,
``phi_silica``, and ``apple_foundation`` ship in later phases per
``docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md``.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from ember.schemas.config import FuniConfig, FuniRuntime
from ember.schemas.funi import (
    ContextItem,
    FuniHealth,
    FuniReply,
    Unavailable,
    UnavailableReason,
)


@runtime_checkable
class FuniHandle(Protocol):
    """Minimum public surface every Funi runtime satisfies."""

    runtime_kind: str
    model_id: str

    def complete(
        self,
        prompt: str,
        context: Sequence[ContextItem],
        tools: Sequence[str] | None = None,
    ) -> FuniReply: ...
    def health(self) -> FuniHealth: ...
    def close(self) -> None: ...


def open(config: FuniConfig) -> FuniHandle | Unavailable:
    """Open the configured Funi runtime.

    Returns either a live :class:`FuniHandle` or a typed
    :class:`Unavailable` value. **Never raises a connection error.**
    Spark code is required by the type system to handle the
    Unavailable branch.
    """
    if config.runtime is FuniRuntime.OLLAMA:
        # Lazy import — only load the runtime client when actually needed,
        # so an Ember built without ollama installed can still import.
        from ember.spark.funi.ollama import open as ollama_open  # noqa: PLC0415

        return ollama_open(config)

    return Unavailable(
        reason=UnavailableReason.RUNTIME_NOT_INSTALLED,
        detail=(
            f"Funi runtime {config.runtime.value!r} is not implemented in "
            f"this build. See docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md "
            f"for the phase that ships it."
        ),
    )


__all__ = ["FuniHandle", "open"]

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

Phase 10 (ADR 0009) added :meth:`FuniHandle.complete_streaming` plus
the :func:`wrap_complete_as_stream` helper for adapters that can't
stream natively.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from typing import Protocol, runtime_checkable

from ember.schemas.config import FuniConfig, FuniRuntime
from ember.schemas.funi import (
    ContextItem,
    FuniHealth,
    FuniReply,
    Unavailable,
    UnavailableReason,
)
from ember.schemas.stream import FuniStreamChunk
from ember.schemas.tool import ToolDescriptor


@runtime_checkable
class FuniHandle(Protocol):
    """Minimum public surface every Funi runtime satisfies."""

    runtime_kind: str
    model_id: str

    def complete(
        self,
        prompt: str,
        context: Sequence[ContextItem],
        tools: Sequence[ToolDescriptor] | None = None,
    ) -> FuniReply: ...
    def complete_streaming(
        self,
        prompt: str,
        context: Sequence[ContextItem],
        tools: Sequence[ToolDescriptor] | None = None,
    ) -> Iterator[FuniStreamChunk]: ...
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


def wrap_complete_as_stream(
    handle: FuniHandle,
    prompt: str,
    context: Sequence[ContextItem],
    tools: Sequence[ToolDescriptor] | None = None,
) -> Iterator[FuniStreamChunk]:
    """Default ``complete_streaming`` implementation for runtimes that
    can't stream natively.

    Calls ``handle.complete()`` synchronously and yields exactly one
    final :class:`FuniStreamChunk` carrying the full reply. Adapter
    authors who can't stream wire this as a one-liner:

        def complete_streaming(self, prompt, context, tools=None):
            yield from wrap_complete_as_stream(self, prompt, context, tools)

    Per ADR 0009 §2.2.
    """
    reply = handle.complete(prompt, context, tools)
    yield FuniStreamChunk(
        text_delta=reply.text,
        done=True,
        finish_reason=reply.finish_reason,
        model_id=reply.model_id,
        prompt_tokens=reply.prompt_tokens,
        completion_tokens=reply.completion_tokens,
    )


__all__ = ["FuniHandle", "open", "wrap_complete_as_stream"]

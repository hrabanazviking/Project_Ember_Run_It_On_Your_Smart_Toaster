"""BrunnrHandle protocol + open() registry.

Per ``docs/architecture/DOMAIN_MAP.md`` §2.1. The :class:`BrunnrHandle`
Protocol is the *minimum surface* every backend adapter implements.
Spark code consumes this Protocol; the concrete adapter behind it is a
configuration decision, never a code decision.

The module-level :func:`open` is the registry — it dispatches on
``config.backend`` to the right adapter's ``open()``. On failure (config
invalid, backend not yet implemented, connection refused) it returns
:class:`ember.schemas.errors.Disconnected` rather than raising, per the
Vow of Graceful Offline.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from typing import Protocol, runtime_checkable

from ember.schemas.chunks import BrunnrStats, Chunk, Document, RetrievalHit
from ember.schemas.config import BrunnrBackend, BrunnrConfig
from ember.schemas.episode import Episode
from ember.schemas.errors import Disconnected, DisconnectReason


@runtime_checkable
class BrunnrHandle(Protocol):
    """Minimum public surface every Brunnr backend satisfies."""

    embedding_dim: int

    def add_document(self, doc: Document) -> int: ...
    def add_chunks(self, chunks: Iterable[Chunk]) -> list[int]: ...
    def add_episode(self, episode: Episode) -> int: ...
    def vector_search(
        self,
        qvec: Sequence[float],
        k: int,
        filter: object | None = None,
    ) -> list[RetrievalHit]: ...
    def text_search(
        self,
        query: str,
        k: int,
        filter: object | None = None,
    ) -> list[RetrievalHit]: ...
    def hybrid_search(
        self,
        qvec: Sequence[float],
        query: str,
        k: int,
    ) -> list[RetrievalHit]: ...
    def get_document(self, document_id: int) -> Document: ...
    def get_chunk(self, chunk_id: int) -> Chunk: ...
    def has_document(self, content_hash: str) -> int | None: ...
    def count(self) -> BrunnrStats: ...
    def close(self) -> None: ...


def open(config: BrunnrConfig) -> BrunnrHandle | Disconnected:
    """Open the configured backend.

    Returns a live :class:`BrunnrHandle` or a typed
    :class:`Disconnected` value — never raises a connection error. Spark
    code is required by the type system to handle the Disconnected
    branch.
    """
    if config.backend is BrunnrBackend.SQLITE_VEC:
        # Lazy import — backends are pluggable and we don't want to
        # require every backend's runtime library on every Ember host.
        from ember.well.brunnr.sqlite_vec import open as sqlite_vec_open  # noqa: PLC0415

        return sqlite_vec_open(config)

    return Disconnected(
        reason=DisconnectReason.CONFIG_INVALID,
        since=datetime.now(tz=UTC),
        detail=(
            f"Brunnr backend {config.backend.value!r} is not implemented "
            f"in this build. See docs/architecture/EMBER_FIRST_SLICE_PLAN.md "
            f"for the phase that ships it."
        ),
    )


__all__ = ["BrunnrHandle", "open"]

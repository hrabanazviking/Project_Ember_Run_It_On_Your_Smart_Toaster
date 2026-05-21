"""Strengr — the tether between Spark and Well.

Per ``docs/architecture/DOMAIN_MAP.md`` §4 and
``docs/architecture/DATA_FLOW.md`` §2.2. Strengr wraps the registry call
into :mod:`ember.well.brunnr.handle` with:

- **Retry-with-backoff** on recoverable failures (timeout, backend
  reported unavailable, connection refused).
- **Fast-fail** on non-recoverable failures (config invalid, auth
  failed, DNS failure).
- **Graceful health probes** — :func:`health` never raises; on failure
  it returns a :class:`StrengrHealth` with ``last_ok=None`` so callers
  can surface the degraded state honestly.

In Phase 4 the only configured backend is ``sqlite_vec`` (local
in-process). Auth and network transport selection become real in Phase
8 when the ``pgvector`` Brunnr ships.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from datetime import UTC, datetime

from ember.schemas.config import BrunnrConfig, StrengrConfig
from ember.schemas.errors import Disconnected, DisconnectReason
from ember.schemas.thread import StrengrHealth
from ember.well.brunnr import handle as _brunnr_handle
from ember.well.brunnr.handle import BrunnrHandle

logger = logging.getLogger(__name__)

_BACKOFF_BASE_S = 1.0

_NON_RECOVERABLE_REASONS: frozenset[DisconnectReason] = frozenset(
    {
        DisconnectReason.CONFIG_INVALID,
        DisconnectReason.AUTH_FAILED,
        DisconnectReason.DNS_FAILURE,
    }
)


Opener = Callable[[BrunnrConfig], BrunnrHandle | Disconnected]


def open(
    strengr_config: StrengrConfig,
    brunnr_config: BrunnrConfig,
    *,
    opener: Opener | None = None,
    sleeper: Callable[[float], None] = time.sleep,
) -> BrunnrHandle | Disconnected:
    """Open the Well via the configured Brunnr, with retry policy.

    ``opener`` defaults to ``ember.well.brunnr.handle.open``. The
    ``sleeper`` parameter exists so tests can verify the backoff
    schedule without actually sleeping.

    Returns either a live :class:`BrunnrHandle` or a typed
    :class:`Disconnected` value. **Never raises a connection error.**
    """
    do_open = opener or _brunnr_handle.open
    attempts = strengr_config.retry_attempts
    backoff_max = strengr_config.retry_backoff_max_s

    last_result: BrunnrHandle | Disconnected | None = None
    for attempt in range(1, attempts + 1):
        result = do_open(brunnr_config)
        last_result = result

        if not isinstance(result, Disconnected):
            return result

        if result.reason in _NON_RECOVERABLE_REASONS:
            logger.debug(
                "strengr: non-recoverable disconnect on attempt %d: %s",
                attempt,
                result.reason.value,
            )
            return result

        if attempt >= attempts:
            logger.debug(
                "strengr: exhausted %d attempts; final reason %s",
                attempts,
                result.reason.value,
            )
            return result

        delay = min(_BACKOFF_BASE_S * (2 ** (attempt - 1)), backoff_max)
        logger.debug(
            "strengr: recoverable disconnect (%s); sleeping %.2fs before attempt %d",
            result.reason.value,
            delay,
            attempt + 1,
        )
        try:
            sleeper(delay)
        except (KeyboardInterrupt, InterruptedError):
            # An operator Ctrl-C during the backoff sleep should surface
            # as a typed Disconnected (UNKNOWN) so the calling Spark
            # code always sees a typed return value. Re-raising
            # KeyboardInterrupt here would violate the
            # typed-value-over-exception contract (ADR 0007 §2.2).
            return Disconnected(
                reason=DisconnectReason.UNKNOWN,
                since=datetime.now(tz=UTC),
                detail=(
                    f"strengr: backoff sleep interrupted on attempt "
                    f"{attempt + 1}; last result was {result.reason.value}"
                ),
            )

    # Defensive: the loop above always returns. If retry_attempts was 0
    # we never opened; surface a synthetic Disconnected so callers always
    # get a typed value rather than ``None``.
    if last_result is None:
        return Disconnected(
            reason=DisconnectReason.CONFIG_INVALID,
            since=datetime.now(tz=UTC),
            detail="strengr.retry_attempts must be >= 1",
        )
    return last_result


def health(handle: BrunnrHandle) -> StrengrHealth:
    """Probe the Well via the handle and return an honest health snapshot.

    Never raises. If the probe fails, the returned :class:`StrengrHealth`
    has ``last_ok=None`` and a populated ``detail`` so ``ember doctor``
    can show the operator what went wrong.
    """
    try:
        stats = handle.count()
    except Exception as exc:
        logger.debug("strengr.health probe failed: %s", exc)
        return StrengrHealth(
            backend_kind=getattr(handle, "backend_kind", "unknown"),
            last_ok=None,
            detail=f"probe failed: {exc}",
        )

    return StrengrHealth(
        backend_kind=getattr(handle, "backend_kind", "unknown"),
        last_ok=datetime.now(tz=UTC),
        documents=stats.documents,
        chunks=stats.chunks,
        embedded_chunks=stats.embedded_chunks,
        size_bytes=stats.size_bytes,
    )


__all__ = ["Opener", "health", "open"]

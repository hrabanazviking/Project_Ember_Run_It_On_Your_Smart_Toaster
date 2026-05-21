"""Shape and behaviour tests for ``ember.thread.strengr``.

The retry/health logic is tested with an in-memory opener; the real
sqlite_vec backend has its own coverage under
``test_brunnr_sqlite_vec.py``. The integration test
``tests/integration/test_strengr_real_backend.py`` is the bridge.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from ember.schemas.chunks import BrunnrStats
from ember.schemas.config import (
    BrunnrBackend,
    BrunnrConfig,
    SqliteVecConfig,
    StrengrConfig,
)
from ember.schemas.errors import (
    BrunnrError,
    Disconnected,
    DisconnectReason,
)
from ember.schemas.thread import StrengrHealth
from ember.thread import strengr

# --------------------------------------------------------------------- #
# Test doubles                                                          #
# --------------------------------------------------------------------- #


class _FakeHandle:
    backend_kind = "fake"
    embedding_dim = 4

    def __init__(self, stats: BrunnrStats | None = None) -> None:
        self._stats = stats or BrunnrStats(
            documents=2, chunks=10, embedded_chunks=10, size_bytes=12_345
        )

    def count(self) -> BrunnrStats:
        return self._stats


class _RaisingHandle:
    backend_kind = "fake"
    embedding_dim = 4

    def count(self) -> BrunnrStats:
        raise BrunnrError("DB file vanished mid-query")


def _disconnected(reason: DisconnectReason, detail: str = "") -> Disconnected:
    return Disconnected(
        reason=reason,
        since=datetime.now(tz=UTC),
        detail=detail or reason.value,
    )


def _scripted_opener(results: list[Any]):
    """Returns the next result from ``results`` on each call."""
    iterator = iter(results)

    def opener(_config: BrunnrConfig):
        return next(iterator)

    return opener


def _no_sleep(_seconds: float) -> None:
    return None


def _default_strengr_config(*, attempts: int = 3) -> StrengrConfig:
    return StrengrConfig(
        health_check_timeout_s=1.0,
        retry_attempts=attempts,
        retry_backoff_max_s=0.0,  # tests should not sleep
    )


def _placeholder_brunnr_config() -> BrunnrConfig:
    return BrunnrConfig(
        backend=BrunnrBackend.SQLITE_VEC,
        embedding_dim=4,
        sqlite_vec=SqliteVecConfig(path=Path("/tmp/never-used.db")),
    )


# --------------------------------------------------------------------- #
# open() — happy path                                                   #
# --------------------------------------------------------------------- #


def test_open_returns_handle_when_brunnr_open_succeeds_first_try() -> None:
    handle = _FakeHandle()
    result = strengr.open(
        _default_strengr_config(),
        _placeholder_brunnr_config(),
        opener=_scripted_opener([handle]),
        sleeper=_no_sleep,
    )
    assert result is handle


# --------------------------------------------------------------------- #
# open() — non-recoverable failures fast-fail                           #
# --------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "reason",
    [
        DisconnectReason.CONFIG_INVALID,
        DisconnectReason.AUTH_FAILED,
        DisconnectReason.DNS_FAILURE,
    ],
)
def test_open_fast_fails_on_non_recoverable_reason(
    reason: DisconnectReason,
) -> None:
    calls: list[int] = []
    disconnected = _disconnected(reason)

    def counting_opener(_config):
        calls.append(1)
        return disconnected

    result = strengr.open(
        _default_strengr_config(attempts=5),
        _placeholder_brunnr_config(),
        opener=counting_opener,
        sleeper=_no_sleep,
    )
    assert isinstance(result, Disconnected)
    assert result.reason is reason
    # Exactly one open attempt; no retry.
    assert len(calls) == 1


# --------------------------------------------------------------------- #
# open() — recoverable failures retry up to N                           #
# --------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "reason",
    [
        DisconnectReason.CONN_REFUSED,
        DisconnectReason.TIMEOUT,
        DisconnectReason.BACKEND_REPORTED_UNAVAILABLE,
        DisconnectReason.UNKNOWN,
    ],
)
def test_open_retries_recoverable_reasons_up_to_attempts(
    reason: DisconnectReason,
) -> None:
    calls: list[int] = []
    disconnected = _disconnected(reason)

    def counting_opener(_config):
        calls.append(1)
        return disconnected

    cfg = _default_strengr_config(attempts=3)
    result = strengr.open(
        cfg,
        _placeholder_brunnr_config(),
        opener=counting_opener,
        sleeper=_no_sleep,
    )
    assert isinstance(result, Disconnected)
    assert result.reason is reason
    assert len(calls) == cfg.retry_attempts


def test_open_returns_handle_when_a_later_attempt_succeeds() -> None:
    handle = _FakeHandle()
    opener = _scripted_opener(
        [
            _disconnected(DisconnectReason.TIMEOUT),
            _disconnected(DisconnectReason.TIMEOUT),
            handle,
        ]
    )
    result = strengr.open(
        _default_strengr_config(attempts=5),
        _placeholder_brunnr_config(),
        opener=opener,
        sleeper=_no_sleep,
    )
    assert result is handle


def test_open_calls_sleeper_between_recoverable_retries() -> None:
    sleeps: list[float] = []

    def recording_sleeper(seconds: float) -> None:
        sleeps.append(seconds)

    opener = _scripted_opener(
        [
            _disconnected(DisconnectReason.TIMEOUT),
            _disconnected(DisconnectReason.TIMEOUT),
            _FakeHandle(),
        ]
    )
    strengr.open(
        _default_strengr_config(attempts=5),
        _placeholder_brunnr_config(),
        opener=opener,
        sleeper=recording_sleeper,
    )
    # Two failures before the success → two sleeps. With retry_backoff_max_s=0
    # in the config, each sleep is clamped to 0.
    assert sleeps == [0.0, 0.0]


def test_open_with_zero_attempts_returns_synthetic_disconnected() -> None:
    result = strengr.open(
        StrengrConfig(retry_attempts=0, retry_backoff_max_s=0.0),
        _placeholder_brunnr_config(),
        opener=_scripted_opener([_FakeHandle()]),  # never invoked
        sleeper=_no_sleep,
    )
    assert isinstance(result, Disconnected)
    assert result.reason is DisconnectReason.CONFIG_INVALID
    assert "retry_attempts" in (result.detail or "")


# --------------------------------------------------------------------- #
# health()                                                              #
# --------------------------------------------------------------------- #


def test_health_returns_live_snapshot_for_responsive_handle() -> None:
    stats = BrunnrStats(documents=3, chunks=11, embedded_chunks=11, size_bytes=42_000)
    handle = _FakeHandle(stats=stats)
    result = strengr.health(handle)
    assert isinstance(result, StrengrHealth)
    assert result.backend_kind == "fake"
    assert result.last_ok is not None
    assert result.documents == 3
    assert result.chunks == 11
    assert result.embedded_chunks == 11
    assert result.size_bytes == 42_000


def test_health_returns_degraded_snapshot_when_probe_raises() -> None:
    result = strengr.health(_RaisingHandle())
    assert isinstance(result, StrengrHealth)
    assert result.last_ok is None  # honest degraded signal
    assert result.documents == 0
    assert result.chunks == 0
    assert result.detail is not None
    assert "probe failed" in result.detail


def test_health_reports_backend_kind_from_handle_attribute() -> None:
    class _NamedHandle:
        backend_kind = "pgvector"
        embedding_dim = 768

        def count(self) -> BrunnrStats:
            return BrunnrStats(documents=0, chunks=0, embedded_chunks=0, size_bytes=0)

    result = strengr.health(_NamedHandle())
    assert result.backend_kind == "pgvector"


def test_health_falls_back_to_unknown_when_handle_lacks_kind() -> None:
    class _UntypedHandle:
        embedding_dim = 4

        def count(self) -> BrunnrStats:
            return BrunnrStats(documents=0, chunks=0, embedded_chunks=0, size_bytes=0)

    result = strengr.health(_UntypedHandle())
    assert result.backend_kind == "unknown"

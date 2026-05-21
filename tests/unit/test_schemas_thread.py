"""Shape contracts for ``ember.schemas.thread``."""

from __future__ import annotations

import dataclasses
from datetime import UTC, datetime

import pytest

from ember.schemas.thread import StrengrHealth


def test_strengr_health_minimal_construction() -> None:
    h = StrengrHealth(backend_kind="sqlite_vec", last_ok=None)
    assert h.documents == 0
    assert h.chunks == 0
    assert h.embedded_chunks == 0
    assert h.size_bytes == 0
    assert h.detail is None


def test_strengr_health_is_frozen() -> None:
    h = StrengrHealth(backend_kind="sqlite_vec", last_ok=datetime.now(tz=UTC))
    with pytest.raises(dataclasses.FrozenInstanceError):
        h.detail = "tampered"  # type: ignore[misc]


def test_strengr_health_last_ok_none_means_degraded() -> None:
    # Per docs/architecture/DATA_FLOW.md §2.2 — last_ok=None is the
    # honest signal Munnr surfaces to the operator.
    h = StrengrHealth(
        backend_kind="sqlite_vec",
        last_ok=None,
        detail="probe failed: no such file or directory",
    )
    assert h.last_ok is None
    assert h.detail is not None
    assert "probe failed" in h.detail


def test_strengr_health_live_has_counts() -> None:
    h = StrengrHealth(
        backend_kind="sqlite_vec",
        last_ok=datetime.now(tz=UTC),
        documents=95,
        chunks=35_682,
        embedded_chunks=35_682,
        size_bytes=394 * 1024 * 1024,
    )
    assert h.embedded_chunks == h.chunks

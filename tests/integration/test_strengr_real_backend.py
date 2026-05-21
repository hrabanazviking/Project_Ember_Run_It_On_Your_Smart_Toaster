"""Strengr ↔ real sqlite_vec Brunnr — the integration bridge.

Skipped automatically if sqlite_vec is not installed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("sqlite_vec")

from ember.schemas.config import (
    BrunnrConfig,
    SqliteVecConfig,
    StrengrConfig,
)
from ember.schemas.errors import Disconnected, DisconnectReason
from ember.thread import strengr
from ember.well.brunnr.handle import BrunnrHandle


def test_strengr_open_with_valid_config_returns_live_handle(tmp_path: Path) -> None:
    brunnr_cfg = BrunnrConfig(
        embedding_dim=4,
        sqlite_vec=SqliteVecConfig(path=tmp_path / "store.db"),
    )
    handle = strengr.open(StrengrConfig(retry_backoff_max_s=0.0), brunnr_cfg)
    assert isinstance(handle, BrunnrHandle)
    assert handle.backend_kind == "sqlite_vec"
    assert handle.embedding_dim == 4

    health = strengr.health(handle)
    assert health.last_ok is not None
    assert health.backend_kind == "sqlite_vec"

    handle.close()


def test_strengr_open_with_missing_sqlite_vec_config_returns_disconnected() -> None:
    brunnr_cfg = BrunnrConfig(
        embedding_dim=4,
        sqlite_vec=None,
    )
    result = strengr.open(StrengrConfig(retry_backoff_max_s=0.0), brunnr_cfg)
    assert isinstance(result, Disconnected)
    assert result.reason is DisconnectReason.CONFIG_INVALID

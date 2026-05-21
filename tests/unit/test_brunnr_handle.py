"""Shape contracts for the Brunnr handle registry."""

from __future__ import annotations

from datetime import datetime

from ember.schemas.config import BrunnrBackend, BrunnrConfig
from ember.schemas.errors import Disconnected, DisconnectReason
from ember.well.brunnr import handle as brunnr_handle


def test_open_with_unimplemented_backend_returns_disconnected() -> None:
    cfg = BrunnrConfig(backend=BrunnrBackend.QDRANT)
    result = brunnr_handle.open(cfg)
    assert isinstance(result, Disconnected)
    assert result.reason is DisconnectReason.CONFIG_INVALID
    assert isinstance(result.since, datetime)
    assert "qdrant" in (result.detail or "").lower()


def test_brunnr_handle_protocol_is_runtime_checkable() -> None:
    # The Protocol is decorated runtime_checkable so isinstance() works
    # for the strengr layer.
    assert hasattr(brunnr_handle.BrunnrHandle, "__instancecheck__")

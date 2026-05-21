"""Shape contracts for the Funi handle registry."""

from __future__ import annotations

from ember.schemas.config import FuniConfig, FuniRuntime
from ember.schemas.funi import Unavailable, UnavailableReason
from ember.spark.funi import handle as funi_handle


def test_open_with_unimplemented_runtime_returns_unavailable() -> None:
    cfg = FuniConfig(runtime=FuniRuntime.LLAMACPP)
    result = funi_handle.open(cfg)
    assert isinstance(result, Unavailable)
    assert result.reason is UnavailableReason.RUNTIME_NOT_INSTALLED
    assert "llamacpp" in (result.detail or "").lower()


def test_funi_handle_protocol_is_runtime_checkable() -> None:
    assert hasattr(funi_handle.FuniHandle, "__instancecheck__")

"""Shape contracts for ``ember.schemas.errors``.

Per ``docs/architecture/EMBER_FIRST_SLICE_PLAN.md`` §3 Phase 2: shape
only; no behaviour, no I/O.
"""

from __future__ import annotations

import dataclasses
from datetime import UTC, datetime

import pytest

from ember.schemas.errors import (
    BrunnrError,
    ConfigError,
    Disconnected,
    DisconnectReason,
    EmberError,
    FuniError,
    HjartaError,
    IngestError,
    MunnrError,
    SchemaError,
    SparkError,
    StrengrError,
    ThreadError,
    WellError,
)

# --------------------------------------------------------------------- #
# Hierarchy                                                              #
# --------------------------------------------------------------------- #


def test_ember_error_is_a_normal_exception() -> None:
    assert issubclass(EmberError, Exception)


@pytest.mark.parametrize(
    "child",
    [
        SchemaError,
        ConfigError,
        WellError,
        BrunnrError,
        IngestError,
        ThreadError,
        StrengrError,
        SparkError,
        FuniError,
        HjartaError,
        MunnrError,
    ],
)
def test_every_typed_error_descends_from_ember_error(child: type) -> None:
    assert issubclass(child, EmberError)


@pytest.mark.parametrize(
    "child,parent",
    [
        (BrunnrError, WellError),
        (IngestError, WellError),
        (StrengrError, ThreadError),
        (FuniError, SparkError),
        (HjartaError, SparkError),
        (MunnrError, SparkError),
    ],
)
def test_realm_groupings_hold(child: type, parent: type) -> None:
    assert issubclass(child, parent)


def test_typed_errors_can_be_raised_and_caught_as_ember_error() -> None:
    with pytest.raises(EmberError):
        raise BrunnrError("Brunnr is sulking")


# --------------------------------------------------------------------- #
# Disconnect — non-raised failure value                                  #
# --------------------------------------------------------------------- #


def test_disconnected_is_a_value_not_an_exception() -> None:
    assert not issubclass(Disconnected, BaseException)


def test_disconnected_is_a_frozen_dataclass() -> None:
    assert dataclasses.is_dataclass(Disconnected)
    inst = Disconnected(
        reason=DisconnectReason.CONN_REFUSED,
        since=datetime.now(tz=UTC),
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        inst.detail = "tampered"  # type: ignore[misc]


def test_disconnected_detail_is_optional() -> None:
    inst = Disconnected(
        reason=DisconnectReason.TIMEOUT,
        since=datetime.now(tz=UTC),
    )
    assert inst.detail is None


def test_all_disconnect_reasons_are_string_valued() -> None:
    for member in DisconnectReason:
        assert isinstance(member.value, str)
        assert member.value == member.value.lower()

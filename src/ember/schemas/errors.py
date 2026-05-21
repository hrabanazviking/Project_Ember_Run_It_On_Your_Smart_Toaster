"""Typed exception classes raised across Ember subpackage boundaries.

Per ``docs/architecture/DOMAIN_MAP.md`` §1 and §11 (errors row):
internal-only errors stay private to their subpackage; any exception that
may cross a subpackage boundary is defined here so callers can handle by
type without import gymnastics.

Also home to the *non-raised failure value* :class:`Disconnected`, which
Strengr returns instead of raising when the Well is unreachable. Spark
code is required by the type system to handle that value — see the Vow
of Graceful Offline in ``docs/SYSTEM_VISION.md`` §3 and ``DATA_FLOW.md``
§2.2.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

# --------------------------------------------------------------------- #
# Exception hierarchy                                                   #
# --------------------------------------------------------------------- #


class EmberError(Exception):
    """Base for every Ember-raised exception that crosses a boundary."""


class SchemaError(EmberError):
    """A schema validation or on-disk version-marker violation."""


class ConfigError(EmberError):
    """A configuration could not be loaded, parsed, or validated."""


# -- Well realm ------------------------------------------------------- #


class WellError(EmberError):
    """Base for Well-realm errors (Brunnr + Smiðja)."""


class BrunnrError(WellError):
    """A Brunnr-adapter-level failure that callers must handle."""


class IngestError(WellError):
    """A Smiðja-side ingest failure that callers must handle."""


# -- Thread realm ----------------------------------------------------- #


class ThreadError(EmberError):
    """Base for Thread-realm errors (Strengr)."""


class StrengrError(ThreadError):
    """A Strengr-level failure that does not become :class:`Disconnected`."""


# -- Spark realm ------------------------------------------------------ #


class SparkError(EmberError):
    """Base for Spark-realm errors (Funi + Hjarta + Munnr)."""


class FuniError(SparkError):
    """A Funi-runtime-level failure not better expressed as
    :class:`ember.schemas.funi.Unavailable`."""


class HjartaError(SparkError):
    """A first-run-wizard failure. Per the Hjarta INTERFACE.md, this is
    raised only before the atomic ``WriteIdentity`` state."""


class MunnrError(SparkError):
    """A Munnr CLI failure not better expressed as a non-zero exit code."""


# --------------------------------------------------------------------- #
# Non-raised failure values                                             #
# --------------------------------------------------------------------- #


class DisconnectReason(StrEnum):
    """Why Strengr is reporting the Well unreachable."""

    CONN_REFUSED = "conn_refused"
    TIMEOUT = "timeout"
    AUTH_FAILED = "auth_failed"
    DNS_FAILURE = "dns_failure"
    CONFIG_INVALID = "config_invalid"
    BACKEND_REPORTED_UNAVAILABLE = "backend_reported_unavailable"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Disconnected:
    """The Well is unreachable.

    Returned by ``ember.thread.strengr.tether.open()`` rather than raised.
    Spark code must handle this value explicitly; that requirement is the
    mechanical form of the Vow of Graceful Offline.
    """

    reason: DisconnectReason
    since: datetime
    detail: str | None = None


__all__ = [
    "BrunnrError",
    "ConfigError",
    "DisconnectReason",
    "Disconnected",
    "EmberError",
    "FuniError",
    "HjartaError",
    "IngestError",
    "MunnrError",
    "SchemaError",
    "SparkError",
    "StrengrError",
    "ThreadError",
    "WellError",
]

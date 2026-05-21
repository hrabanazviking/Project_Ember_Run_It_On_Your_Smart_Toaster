"""Thread-realm result types.

Returned by :mod:`ember.thread.strengr` and consumed by Munnr's
``ember doctor``. Lives in schemas (not inside strengr/) because the
type crosses the Spark↔Thread boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class StrengrHealth:
    """A health snapshot for the tether and the Well it points at.

    ``last_ok`` is ``None`` when the most recent health probe failed —
    this is the *honest degraded* signal callers should surface to the
    operator. Counts are 0 in that case.
    """

    backend_kind: str
    last_ok: datetime | None
    documents: int = 0
    chunks: int = 0
    embedded_chunks: int = 0
    size_bytes: int = 0
    detail: str | None = None


__all__ = ["StrengrHealth"]

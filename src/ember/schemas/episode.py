"""The Episode type — one remembered conversation turn.

Per ``docs/architecture/DATA_FLOW.md`` §2.1 step 9 (happy path) and §2.2
step 9' (sad path, with the ``well_disconnected`` flag set true).

When the Well is reachable, the Episode is written to Brunnr at the end
of the turn. When the Well is unreachable, the Episode is written to a
local pending-episodes journal under ``~/.ember/state/pending_episodes/``
and flushed in on Well recovery.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ember.schemas.persona import DEFAULT_PERSONA_ID


@dataclass(frozen=True, slots=True)
class Episode:
    """One remembered conversation turn.

    ``persona_id`` (E-025) tags the turn with the persona who
    lived it. It defaults to :data:`DEFAULT_PERSONA_ID`, the
    namespace every pre-persona episode already belongs to, so
    existing stores and fixtures keep their meaning. The Brunnr
    adapters in this build do not yet persist the tag (their
    schemas predate it) — separation is enforced at the prompt
    boundary by ``ember.spark.funi.prompt`` and in-process by
    ``ember.spark.persona`` until a storage slice carries the
    tag to disk; the E-025 doc states this limit plainly.
    """

    operator_input: str
    ember_reply: str
    cited_chunk_ids: tuple[int, ...] = ()
    funi_model: str = ""
    well_disconnected: bool = False
    started_at: datetime | None = None
    completed_at: datetime | None = None
    id: int | None = None
    persona_id: str = DEFAULT_PERSONA_ID


__all__ = ["Episode"]

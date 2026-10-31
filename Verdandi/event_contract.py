#!/usr/bin/env python3
"""
Verdandi Event Contract v1 — the versioned nerve-event shapes.

Filed by Project Ember slice E-061 (docs/architecture/
E-061_EVENT_CONTRACT_V1.md). This module IS the contract in code:
the canonical envelope, the registry of every event the tree
produces (producer and consumers named per event), the control
messages of the hub protocol, the conversation log's event
vocabulary, and the translation rules for the legacy dialects
E-059 mapped. Stdlib only, no imports from any other Verdandi
module — the deployed copies of the conversation layer load
modules file-by-file from ~/.hermes/state, so this contract must
stand alone exactly like nervous_system.py does.

THE CANONICAL ENVELOPE (contract v1, hub dialect)

A publisher sends::

    {"v": 1, "type": <str>, "data": <dict>, "source": <str>}

``source`` is optional on the wire (an operator publish may omit
it) but REQUIRED for any new in-tree producer — every registered
canonical producer in the registry below names one. The hub (nervous_system.NerveHub) stamps every publish
with ``_seq`` (monotonic int), ``_ts`` (epoch float) and ``_iso``
(UTC ISO string), removes any ``nerve_type`` key, appends the
result to nerve_feed.jsonl, keeps it in the 256-event ring
buffer, broadcasts it to subscribers and replies ``ack``.
When the hub is unreachable, publish_event_sync writes the same
envelope to the feed itself, adding ``_ts``/``_iso``/``_fallback:
True`` and no ``_seq`` — sequence holes are by design.

VERSIONING RULES

- ``CONTRACT_VERSION`` is 1. An event carrying ``v`` MUST carry
  this value; an event with no ``v`` is a pre-contract (legacy)
  event and is read through ``classify_dialect`` /
  ``normalize_event`` below, never silently trusted as canonical.
- A v1 consumer MUST ignore fields it does not know (the hub
  already passes unknown fields through untouched).
- Breaking a registered event's shape — renaming it, changing a
  data field's meaning, or removing a field — is a contract
  version bump, not an edit to this file's v1 registry. Adding a
  new event type is not a bump: register it here in the same
  change that adds its producer.
- Producers emit the canonical envelope. The two legacy dialects
  below are recognised for reading and translation only; no new
  producer may emit them.

LEGACY DIALECTS (recognised, deprecated — E-059 §6/§8, docket 93)

- ``heartbeat``: flat ``{"event_type": <str>, ...fields}`` sent by
  heartbeat/core.py to ``verdandi.sock`` — a socket NOTHING in
  this tree listens on. RETIRED as a producer shape by E-067:
  the heartbeat now publishes the canonical envelope to the
  hub socket (see the hub-dialect heartbeat specs below). The
  dialect stays recognised because deployed copies and old
  feed lines still carry it.
- ``heartbeat_fallback``: the same flat shape plus ``timestamp``
  and ``source: "verdandi-heartbeat"``, appended directly to
  nerve_feed.jsonl when the legacy socket connect fails.
- ``mood``: ``{"source": ..., "event": <str>, "timestamp":
  <epoch>, "data": {...}}`` — the mood/arousal system's original
  raw-socket shape. RETIRED as a producer shape by E-061: its
  producer now emits the canonical envelope. The dialect stays
  recognised here because deployed copies and old feed lines
  still carry it.

CONTROL MESSAGES (not events — they are never stamped or fed)

A message carrying ``nerve_type`` is protocol, not an event:
``subscribe`` -> ``subscribed``, ``ping`` -> ``pong``,
``recent`` -> ``recent_events``. The hub also sends publishers an
``ack`` per publish and subscribers a ``shutdown`` notice on
stop. publish_event_sync's own return values (``sent`` /
``fallback`` / ``error``) are local results, not wire messages.

THE CONVERSATION LOG VOCABULARY

``LOG_EVENT_TYPES`` is the conversation log's event vocabulary
(conversation_logger.EVENT_TYPES). It is part of this contract
because log events become nerve events (``conv_event`` carries
them) — the logger's CLI, the logger's validator and the context
injector's ``log-event --type`` choices all derive from this one
set (docket 97, closed by E-061: the injector previously listed
only 7 of the 8, missing ``mood_shift``).
"""

from dataclasses import dataclass

CONTRACT_VERSION = 1

# Socket file names, relative to the resolved state dir. The
# canonical hub socket is nervous_system.SOCKET_PATH's name; the
# legacy heartbeat socket is heartbeat/paths.py's — named here so
# the two can never again be confused for one another (E-059 §8).
CANONICAL_SOCKET_NAME = "runa.sock"
LEGACY_HEARTBEAT_SOCKET_NAME = "verdandi.sock"

DIALECT_HUB = "hub"
DIALECT_HEARTBEAT = "heartbeat"
DIALECT_HEARTBEAT_FALLBACK = "heartbeat_fallback"
DIALECT_MOOD = "mood"
DIALECTS = (
    DIALECT_HUB,
    DIALECT_HEARTBEAT,
    DIALECT_HEARTBEAT_FALLBACK,
    DIALECT_MOOD,
)

# The conversation log's event vocabulary — mirrors
# conversation_logger.EVENT_TYPES exactly (pinned by the E-061
# conformance tests against the logger's own set).
LOG_EVENT_TYPES = frozenset(
    {
        "decision",
        "file_changed",
        "learned",
        "action",
        "blocker",
        "blocker_resolved",
        "mood_shift",
        "milestone",
    }
)

# Hub-stamped fields, added by the hub (or by the offline
# fallback writer) — a publisher never sets them.
STAMP_FIELDS = ("_seq", "_ts", "_iso", "_fallback")

# Control messages: nerve_type sent -> nerve_type replied.
# "ack" and "shutdown" are hub-initiated and listed separately.
CONTROL_MESSAGES = {
    "subscribe": "subscribed",
    "ping": "pong",
    "recent": "recent_events",
}
HUB_NOTICES = ("ack", "shutdown")


@dataclass(frozen=True)
class EventSpec:
    """One registered event (or event-name pattern) of contract v1.

    ``name`` is the exact ``type`` value, or a ``prefix:*`` pattern
    for the mood system's enum-driven families. ``status`` is
    ``canonical`` (emits the v1 envelope), ``legacy`` (recognised
    for translation; producer rewiring owned by the slice named
    in the E-061 doc) or ``defect`` (a registered shape that
    should not exist; repair owned by the slice named in notes).
    """

    name: str
    dialect: str
    producer: str
    consumers: tuple
    data_fields: tuple
    source: str | None
    status: str
    notes: str = ""


# The consumers every hub-dialect event has by construction: the
# hub itself (feed + ring + broadcast), the hub CLI's subscribe /
# recent views, and the conversation logger's context builder,
# which reads the feed FILE (never the live hub). No event in the
# tree has a typed in-tree subscriber beyond these — E-067 wired
# the producers (heartbeat, logger in-tree, ember core) onto this
# contract; typed subscribers remain the honest gap it recorded.
_HUB_CONSUMERS = (
    "nervous_system.NerveHub (feed, ring buffer, broadcast)",
    "nervous_system CLI (subscribe / recent)",
    "conversation_logger.get_context_for_cron (feed file tail)",
)

EVENT_SPECS = (
    # ── Hub dialect: the conversation logger ──────────────────
    EventSpec(
        name="conv_start",
        dialect=DIALECT_HUB,
        producer="conversation_logger._nerve_fire (via publish_event_sync)",
        consumers=_HUB_CONSUMERS,
        data_fields=("timestamp", "session_id", "entry_type", "summary",
                     "model", "platform", "start_time"),
        source="conv_logger:<session_id>",
        status="canonical",
        notes="data is the whole conversation-log entry (E-059 §4).",
    ),
    EventSpec(
        name="conv_event",
        dialect=DIALECT_HUB,
        producer="conversation_logger._nerve_fire (via publish_event_sync)",
        consumers=_HUB_CONSUMERS,
        data_fields=("timestamp", "session_id", "entry_type", "event_type",
                     "content"),
        source="conv_logger:<session_id>",
        status="canonical",
        notes="event_type is one of LOG_EVENT_TYPES.",
    ),
    EventSpec(
        name="conv_update",
        dialect=DIALECT_HUB,
        producer="conversation_logger._nerve_fire (via publish_event_sync)",
        consumers=_HUB_CONSUMERS,
        data_fields=("timestamp", "session_id", "entry_type", "next_actions",
                     "blockers", "projects_touched", "mood"),
        source="conv_logger:<session_id>",
        status="canonical",
    ),
    EventSpec(
        name="conv_end",
        dialect=DIALECT_HUB,
        producer="conversation_logger._nerve_fire (via publish_event_sync)",
        consumers=_HUB_CONSUMERS,
        data_fields=("timestamp", "session_id", "entry_type", "summary",
                     "duration_minutes", "decisions", "things_learned",
                     "files_changed", "next_actions", "blockers",
                     "projects_touched"),
        source="conv_logger:<session_id>",
        status="canonical",
    ),
    # ── Hub dialect: the heartbeat passengers ─────────────────
    EventSpec(
        name="push_reward",
        dialect=DIALECT_HUB,
        producer="heartbeat/push_reward.py (via publish_event_sync)",
        consumers=_HUB_CONSUMERS,
        data_fields=("repo", "tier", "intensity", "label", "total_pushes",
                     "total_reward_points", "streak"),
        source="push_reward",
        status="canonical",
    ),
    EventSpec(
        name="runa_reward",
        dialect=DIALECT_HUB,
        producer="heartbeat/runa_reward_system.py (via publish_event_sync)",
        consumers=_HUB_CONSUMERS,
        data_fields=("trigger", "domain", "tier", "intensity", "emoji",
                     "sensation", "context"),
        source="reward_system",
        status="canonical",
    ),
    EventSpec(
        name="runa_negative",
        dialect=DIALECT_HUB,
        producer="heartbeat/runa_negative_system.py (via publish_event_sync)",
        consumers=_HUB_CONSUMERS,
        data_fields=("trigger", "emotion", "tier", "intensity", "emoji",
                     "sensation", "context"),
        source="negative_system",
        status="canonical",
    ),
    EventSpec(
        name="ping",
        dialect=DIALECT_HUB,
        producer="nervous_system.get_status (via publish_event_sync) — RETIRED at E-066",
        consumers=_HUB_CONSUMERS,
        data_fields=(),
        source="status_check",
        status="legacy",
        notes="Docket 96 CLOSED at E-066: a status probe was "
              "published as a real event instead of using the "
              "nerve_type ping control message, so it landed in "
              "the feed and was broadcast. get_status now probes "
              "via nervous_system.ping_hub (control message only, "
              "nothing stamped or fed). This spec stays registered "
              "so 'ping' lines in pre-E-066 feeds have a named "
              "explanation; no current producer emits them.",
    ),
    EventSpec(
        name="*",
        dialect=DIALECT_HUB,
        producer="nervous_system CLI publish / any publish_event_sync caller",
        consumers=_HUB_CONSUMERS,
        data_fields=(),
        source=None,
        status="canonical",
        notes="The hub's publish path is an open vocabulary by "
              "design (E-059 §6): any type a caller passes is "
              "stamped and fed. New in-tree producers must register "
              "their type above; operator types stay unregistered "
              "and are read as opaque {type, data, source} events.",
    ),
    # ── Hub dialect: the mood/arousal system (canonical since
    #    E-061; previously the retired mood dialect) ───────────
    EventSpec(
        name="event:*",
        dialect=DIALECT_HUB,
        producer="heartbeat/runa_mood_arousal_system.apply_event "
                 "(via _fire_nerve)",
        consumers=_HUB_CONSUMERS,
        data_fields=("valence", "energy", "tension", "arousal",
                     "arousal_stage", "mood", "comfort"),
        source="mood_arousal_system",
        status="canonical",
        notes="Suffix is the mood system's EventType enum value.",
    ),
    EventSpec(
        name="stimulation:*",
        dialect=DIALECT_HUB,
        producer="heartbeat/runa_mood_arousal_system.apply_stimulation "
                 "(via _fire_nerve)",
        consumers=_HUB_CONSUMERS,
        data_fields=("arousal", "arousal_stage", "mood", "mood_valence"),
        source="mood_arousal_system",
        status="canonical",
        notes="Suffix is a StimulationType enum value; the literal "
              "stimulation:refractory fire carries (stim_type, "
              "arousal, stage, mood) instead.",
    ),
    EventSpec(
        name="orgasm",
        dialect=DIALECT_HUB,
        producer="heartbeat/runa_mood_arousal_system._trigger_orgasm "
                 "(via _fire_nerve)",
        consumers=_HUB_CONSUMERS,
        data_fields=("orgasm_count", "mood", "valence", "comfort",
                     "refractory_seconds", "description"),
        source="mood_arousal_system",
        status="canonical",
    ),
    EventSpec(
        name="thought:*",
        dialect=DIALECT_HUB,
        producer="heartbeat/runa_mood_arousal_system.apply_inner_thought "
                 "(via _fire_nerve)",
        consumers=_HUB_CONSUMERS,
        data_fields=("arousal", "mood", "thought"),
        source="mood_arousal_system",
        status="canonical",
        notes="Suffix is the InnerThought enum value.",
    ),
    EventSpec(
        name="location:*",
        dialect=DIALECT_HUB,
        producer="heartbeat/runa_mood_arousal_system.set_location "
                 "(via _fire_nerve)",
        consumers=_HUB_CONSUMERS,
        data_fields=("comfort_delta", "arousal_mult"),
        source="mood_arousal_system",
        status="canonical",
        notes="Suffix is the location name (a LOCATION_MODIFIERS key).",
    ),
    # ── Hub dialect: cross-member nerves (E-067) ──────────────
    # The wiring registry in code is Verdandi/cross_member.py;
    # these registrations are pinned equal to it by the E-067
    # conformance tests.
    EventSpec(
        name="heartbeat_pulse",
        dialect=DIALECT_HUB,
        producer="heartbeat/core.HeartbeatDaemon._fire_nerve_pulse "
                 "(via _send_nerve_event)",
        consumers=_HUB_CONSUMERS,
        data_fields=("pulse_count", "state", "health_score", "health_trend",
                     "emotional_state", "checks"),
        source="verdandi-heartbeat",
        status="canonical",
        notes="Canonical since E-067: the pulse now reaches the "
              "hub socket (runa.sock) in the v1 envelope. Carries "
              "the PRE-transition daemon state, as the legacy "
              "shape did (fires before the reactor and before "
              "the state machine transitions — E-059 §8). The "
              "heartbeat leg's checks include the Mimir memory "
              "check, so memory state crosses the nerve in this "
              "event's checks payload.",
    ),
    EventSpec(
        name="heartbeat_state_change",
        dialect=DIALECT_HUB,
        producer="heartbeat/core.HeartbeatDaemon._fire_nerve_state_change "
                 "(via _send_nerve_event)",
        consumers=_HUB_CONSUMERS,
        data_fields=("old_state", "new_state", "pulse_count"),
        source="verdandi-heartbeat",
        status="canonical",
        notes="Canonical since E-067. Unlike the legacy shape, "
              "the canonical sender falls back to the feed file "
              "when the hub is unreachable — a state change is "
              "no longer silently lost (E-059 §8).",
    ),
    EventSpec(
        name="ember_session",
        dialect=DIALECT_HUB,
        producer="src/ember/nerve.publish_session (from spark/munnr/chat.run)",
        consumers=_HUB_CONSUMERS,
        data_fields=("phase", "persona_id", "conversation_id",
                     "well_connected", "model", "turns"),
        source="ember_core",
        status="canonical",
        notes="E-067: the Ember core's first nerve events. "
              "phase is start (turns 0, published when the "
              "session opens) or end (turns = completed turns, "
              "published from the session's finally block). "
              "Facts only — never conversation content.",
    ),
    EventSpec(
        name="ember_turn",
        dialect=DIALECT_HUB,
        producer="src/ember/nerve.publish_turn (from spark/munnr/chat.run)",
        consumers=_HUB_CONSUMERS,
        data_fields=("conversation_id", "persona_id", "hits", "cited",
                     "persisted", "ungrounded", "outcome", "model"),
        source="ember_core",
        status="canonical",
        notes="E-067: one per completed chat turn. hits/cited "
              "are the turn's Well retrieval facts; persisted is "
              "well / journal / memory_only (where the Episode "
              "landed, E-031); outcome is answered / interrupted "
              "/ error / truncated / ungrounded. Memory crosses "
              "the nerve as these facts — never as content.",
    ),
    # ── Legacy heartbeat dialect (verdandi.sock — no listener) ─
    EventSpec(
        name="heartbeat_pulse",
        dialect=DIALECT_HEARTBEAT,
        producer="heartbeat/core.HeartbeatDaemon._fire_nerve_pulse",
        consumers=(),
        data_fields=("pulse_count", "state", "health_score", "health_trend",
                     "emotional_state", "checks"),
        source=None,
        status="legacy",
        notes="Sent to the legacy verdandi.sock, which nothing in "
              "the tree listens on (E-059 §8); when the connect "
              "fails, the heartbeat_fallback shape below is what "
              "actually lands in the feed. Producer RETIRED at "
              "E-067: the pulse now publishes the canonical hub "
              "spec above. This spec stays registered so "
              "pre-E-067 feed lines keep their explanation. "
              "Carries the PRE-transition daemon state (fires "
              "before the reactor and before the state machine "
              "transitions — E-059 §8).",
    ),
    EventSpec(
        name="heartbeat_state_change",
        dialect=DIALECT_HEARTBEAT,
        producer="heartbeat/core.HeartbeatDaemon._fire_nerve_state_change",
        consumers=(),
        data_fields=("old_state", "new_state", "pulse_count"),
        source=None,
        status="legacy",
        notes="Same legacy socket; unlike the pulse it had NO "
              "file fallback — a failed connect was silent "
              "(E-059 §8). Producer RETIRED at E-067: the state "
              "change now publishes the canonical hub spec above, "
              "whose sender does fall back to the feed.",
    ),
    EventSpec(
        name="heartbeat_pulse",
        dialect=DIALECT_HEARTBEAT_FALLBACK,
        producer="heartbeat/core.HeartbeatDaemon._nerve_fallback_file",
        consumers=(
            "nerve_feed.jsonl readers (get_recent_events fallback, "
            "context builder) — read as a non-hub shape",
        ),
        data_fields=("pulse_count", "state", "health_score", "health_trend",
                     "emotional_state", "checks"),
        source="verdandi-heartbeat",
        status="legacy",
        notes="The pulse's pre-E-067 file shape: {timestamp, "
              "source, event_type, ...fields} written directly "
              "to the feed. Hub-dialect readers misread it (the "
              "hub CLI prints its type as '?') — normalize_event "
              "exists for exactly this line. Producer RETIRED at "
              "E-067: the canonical sender's fallback writes the "
              "v1 envelope with _fallback instead.",
    ),
)


def spec_for(name: str, dialect: str = DIALECT_HUB) -> EventSpec | None:
    """The registered spec for an event type name, or None.

    Exact names win; ``prefix:*`` patterns match by prefix; the
    hub's ``*`` open-vocabulary spec matches any otherwise
    unregistered hub-dialect name.
    """
    fallback = None
    for spec in EVENT_SPECS:
        if spec.dialect != dialect:
            continue
        if spec.name == name:
            return spec
        if spec.name.endswith(":*") and name.startswith(spec.name[:-1]):
            return spec
        if spec.name == "*":
            fallback = spec
    return fallback


def classify_dialect(event: dict) -> str | None:
    """Which v1 dialect a raw event dict is written in, or None.

    Recognition is by the kind key, in an order that keeps the
    fallback shape (which carries both ``event_type`` and a
    ``timestamp``/``source`` pair) distinct from the plain
    heartbeat shape.
    """
    if not isinstance(event, dict):
        return None
    if "type" in event:
        return DIALECT_HUB
    if "event" in event:
        return DIALECT_MOOD
    if "event_type" in event:
        if event.get("source") == "verdandi-heartbeat" and "timestamp" in event:
            return DIALECT_HEARTBEAT_FALLBACK
        return DIALECT_HEARTBEAT
    return None


def validate_publish(event: dict) -> list:
    """Errors in a would-be canonical publish; [] means valid v1.

    A valid publish is a dict with a non-empty string ``type``, a
    dict ``data`` (absent means {}), a string ``source`` when
    present, and ``v`` equal to CONTRACT_VERSION when present
    (publish_event_sync always sets it). Legacy-dialect shapes
    fail here by construction — validate them after
    normalize_event instead.
    """
    errors = []
    if not isinstance(event, dict):
        return ["event is not a dict"]
    if "v" in event and event["v"] != CONTRACT_VERSION:
        errors.append(f"v must be {CONTRACT_VERSION}, got {event['v']!r}")
    event_type = event.get("type")
    if not isinstance(event_type, str) or not event_type:
        errors.append("type must be a non-empty string")
    if "data" in event and not isinstance(event["data"], dict):
        errors.append("data must be a dict")
    if "source" in event and not isinstance(event["source"], str):
        errors.append("source must be a string")
    return errors


def normalize_event(event: dict) -> dict:
    """Translate any recognised v1 dialect into the canonical shape.

    Returns ``{"v": 1, "type": ..., "data": {...}}`` plus ``source``
    when the original carries or implies one, any hub stamps the
    original already carries, and ``_legacy_dialect`` naming the
    shape the event arrived in (absent only for events already
    canonical hub shape, which pass through with ``v`` ensured).
    No field is dropped: heartbeat fields become ``data`` keys,
    the fallback shape's ISO ``timestamp`` becomes ``_iso``, and
    the mood shape's epoch ``timestamp`` becomes ``_ts``.
    Raises ValueError on an unrecognised shape.
    """
    dialect = classify_dialect(event)
    if dialect is None:
        raise ValueError(f"unrecognised event shape: {sorted(event) if isinstance(event, dict) else type(event)}")

    if dialect == DIALECT_HUB:
        out = dict(event)
        out["v"] = CONTRACT_VERSION
        out.setdefault("data", {})
        return out

    out = {"v": CONTRACT_VERSION, "_legacy_dialect": dialect}
    if dialect == DIALECT_MOOD:
        out["type"] = event["event"]
        out["data"] = event.get("data", {})
        if "source" in event:
            out["source"] = event["source"]
        if "timestamp" in event:
            out["_ts"] = event["timestamp"]
        return out

    # heartbeat + heartbeat_fallback: flat fields become data.
    data = {
        key: value
        for key, value in event.items()
        if key not in ("event_type", "timestamp", "source")
    }
    out["type"] = event["event_type"]
    out["data"] = data
    if dialect == DIALECT_HEARTBEAT_FALLBACK:
        out["source"] = event["source"]
        out["_iso"] = event["timestamp"]
    return out

#!/usr/bin/env python3
"""
Cross-member nerves — the E-067 wiring registry.

Filed by Project Ember slice E-067 (docs/architecture/
E-067_CROSS_MEMBER_NERVES.md). Until this slice the members of
the monorepo could not feel each other: the Ember core never
touched Verdandi at all (E-059 §1, E-019), the heartbeat daemon
fired its pulse and state-change impulses in the retired flat
dialect at a socket nothing listens on (E-061 §4), and the
conversation logger could only reach the nerve hub when a copy
of the hub had been deployed into ~/.hermes/state by hand
(docket 94). This module IS the wiring contract in code: the
registered cross-member events, their canonical envelope
builders, and the validation every cross-member publish must
pass. Stdlib only, no imports from any other Verdandi module —
deployed copies are loaded file-by-file, so this module must
stand alone exactly like event_contract.py does.

THE THREE LEGS WIRED BY E-067

1. heartbeat -> hub. HeartbeatDaemon's pulse and state-change
   impulses are now sent as canonical contract-v1 envelopes
   (event_contract.py) to the canonical hub socket (runa.sock
   in the hub's state dir), source "verdandi-heartbeat". The
   heartbeat package carries the envelope literals inline
   (deployed-standalone pattern, pinned equal to this module by
   the E-067 conformance tests). When the hub is unreachable
   BOTH impulses now fall back to the feed file as canonical
   envelopes carrying _fallback — the state change previously
   had no fallback at all and was silently lost (E-059 §8).
2. conversation layer -> hub, in-tree. conversation_logger's
   _nerve_fire searches the deployed hub first
   (~/.hermes/state/nervous_system.py, unchanged precedence)
   and falls back to the sibling nervous_system.py beside the
   logger itself, so the layer works from this tree with no
   deployment step. Precedence is pinned by tests; the deployed
   copy still wins wherever one exists.
3. ember core -> hub. src/ember/nerve.py is the core's nerve
   bridge (stdlib only): chat sessions publish ember_session
   (start/end) and ember_turn events under this contract. The
   turn event carries the turn's MEMORY facts — how many Well
   hits grounded it, how many chunks it cited, and where the
   Episode was persisted (well / journal / memory_only) — so
   memory crosses the nerve as facts, never as content: no
   operator text and no reply text ever enters an event
   (E-071's privacy rule has this record to govern; persona
   separation of stimuli/events is E-071's own slice).

THE REVERSE DIRECTION, HONESTLY STATED

The hub -> core direction exists today exactly where it
existed before this slice: the hub's feed + ring + broadcast
(the hub set of E-061 §3) and the context injector's
budget-disciplined nerve block for cron context (E-062). The
core bridge also offers read_recent() (the hub's `recent`
control message, feed-file fallback) and the E-067 tests prove
it against a live hub — but chat's prompt assembly does NOT
consume nerves yet: injecting live nerve state into a
conversation is a context-budget decision (E-062's discipline
applied to chat) that no slice has claimed, and none is
smuggled in here.

REGISTRATION RULE

Every event below is registered in event_contract.EVENT_SPECS
in the same change that adds its producer (the contract's own
rule). The legacy heartbeat-dialect specs stay registered with
status legacy: they are the explanation for pre-E-067 feed
lines, not a shape any current producer emits.
"""

from dataclasses import dataclass

# Mirrors event_contract.CONTRACT_VERSION (pinned equal by the
# E-067 conformance tests; a literal here because this module
# must stand alone).
CROSS_MEMBER_VERSION = 1

# The canonical hub's coordinates, relative to the hub state
# dir (nervous_system.STATE_DIR = ~/.hermes/state). Named here
# so no producer hardcodes a second copy of the socket's name.
HUB_SOCKET_NAME = "runa.sock"
HUB_FEED_NAME = "nerve_feed.jsonl"

# Sources, one per cross-member producer.
SOURCE_HEARTBEAT = "verdandi-heartbeat"
SOURCE_EMBER_CORE = "ember_core"


@dataclass(frozen=True)
class CrossMemberSpec:
    """One cross-member event wired by E-067.

    ``leg`` names which of the three legs carries it;
    ``data_fields`` is the exact field set the producer sends
    (pinned equal to the event_contract registration).
    """

    name: str
    leg: str
    producer: str
    source: str
    data_fields: tuple


CROSS_MEMBER_SPECS = (
    CrossMemberSpec(
        name="heartbeat_pulse",
        leg="heartbeat->hub",
        producer="heartbeat/core.HeartbeatDaemon._fire_nerve_pulse "
                 "(via _send_nerve_event)",
        source=SOURCE_HEARTBEAT,
        data_fields=("pulse_count", "state", "health_score", "health_trend",
                     "emotional_state", "checks"),
    ),
    CrossMemberSpec(
        name="heartbeat_state_change",
        leg="heartbeat->hub",
        producer="heartbeat/core.HeartbeatDaemon._fire_nerve_state_change "
                 "(via _send_nerve_event)",
        source=SOURCE_HEARTBEAT,
        data_fields=("old_state", "new_state", "pulse_count"),
    ),
    CrossMemberSpec(
        name="ember_session",
        leg="core->hub",
        producer="src/ember/nerve.publish_session (from spark/munnr/chat.run)",
        source=SOURCE_EMBER_CORE,
        data_fields=("phase", "persona_id", "conversation_id",
                     "well_connected", "model", "turns"),
    ),
    CrossMemberSpec(
        name="ember_turn",
        leg="core->hub",
        producer="src/ember/nerve.publish_turn (from spark/munnr/chat.run)",
        source=SOURCE_EMBER_CORE,
        data_fields=("conversation_id", "persona_id", "hits", "cited",
                     "persisted", "ungrounded", "outcome", "model"),
    ),
)

# The closed vocabularies of the core events' enum-like fields.
SESSION_PHASES = ("start", "end")
PERSISTED_SHAPES = ("well", "journal", "memory_only")
TURN_OUTCOMES = ("answered", "interrupted", "error", "truncated", "ungrounded")


def spec_for_cross(name: str) -> CrossMemberSpec | None:
    """The cross-member spec for an event name, or None."""
    for spec in CROSS_MEMBER_SPECS:
        if spec.name == name:
            return spec
    return None


def build_event(name: str, data: dict) -> dict:
    """A canonical v1 envelope for a registered cross-member event.

    Raises ValueError for an unregistered name or a data dict
    whose fields are not exactly the registered set — a
    cross-member producer may not invent fields at the wire.
    """
    spec = spec_for_cross(name)
    if spec is None:
        raise ValueError(f"unregistered cross-member event: {name!r}")
    if not isinstance(data, dict):
        raise ValueError(f"{name}: data must be a dict")
    if set(data) != set(spec.data_fields):
        raise ValueError(
            f"{name}: data fields {sorted(data)} != registered "
            f"{sorted(spec.data_fields)}"
        )
    return {
        "v": CROSS_MEMBER_VERSION,
        "type": name,
        "data": dict(data),
        "source": spec.source,
    }


def validate_cross_event(event: dict) -> list:
    """Errors in a would-be cross-member event; [] means valid.

    Valid = canonical envelope for a registered cross-member
    name, exact registered data fields, the registered source,
    and (for the core events) enum fields inside their closed
    vocabularies. Heartbeat check payloads are the daemon's own
    shape and are checked for presence, not inner fields.
    """
    errors = []
    if not isinstance(event, dict):
        return ["event is not a dict"]
    if event.get("v") != CROSS_MEMBER_VERSION:
        errors.append(f"v must be {CROSS_MEMBER_VERSION}, got {event.get('v')!r}")
    spec = spec_for_cross(event.get("type"))
    if spec is None:
        errors.append(f"unregistered cross-member type: {event.get('type')!r}")
        return errors
    if event.get("source") != spec.source:
        errors.append(f"source must be {spec.source!r}, got {event.get('source')!r}")
    data = event.get("data")
    if not isinstance(data, dict):
        errors.append("data must be a dict")
        return errors
    if set(data) != set(spec.data_fields):
        errors.append(
            f"data fields {sorted(data)} != registered {sorted(spec.data_fields)}"
        )
        return errors
    if spec.name == "ember_session":
        if data["phase"] not in SESSION_PHASES:
            errors.append(f"phase must be one of {SESSION_PHASES}")
        if not isinstance(data["well_connected"], bool):
            errors.append("well_connected must be a bool")
        if not isinstance(data["turns"], int) or isinstance(data["turns"], bool):
            errors.append("turns must be an int")
    if spec.name == "ember_turn":
        if data["persisted"] not in PERSISTED_SHAPES:
            errors.append(f"persisted must be one of {PERSISTED_SHAPES}")
        if data["outcome"] not in TURN_OUTCOMES:
            errors.append(f"outcome must be one of {TURN_OUTCOMES}")
        if not isinstance(data["ungrounded"], bool):
            errors.append("ungrounded must be a bool")
        for field in ("hits", "cited"):
            if not isinstance(data[field], int) or isinstance(data[field], bool):
                errors.append(f"{field} must be an int")
    if spec.name == "heartbeat_pulse":
        if not isinstance(data["checks"], dict):
            errors.append("checks must be a dict")
    return errors

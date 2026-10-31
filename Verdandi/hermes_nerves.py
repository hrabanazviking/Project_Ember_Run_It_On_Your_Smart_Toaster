#!/usr/bin/env python3
"""
Hermes-shaped nerves — the E-068 translation registry.

Filed by Project Ember slice E-068 (docs/architecture/
E-068_HERMES_SHAPED_NERVES.md). The Hermes hack's volmarr-core
plugin (post-refresh surfaces, read at hermes-hack-build HEAD
7b821b270423149072a596503b60e0d7f8dd549d, plugin version
0.26.0) publishes its session / turn / tool lifecycle events
to the SAME Verdandi hub Ember uses — the same socket
(``runa.sock`` under the Hermes profile's ``state/`` dir, the
hub's own state dir), the same outer wire keys (``type``,
``source``, ``data``). The two sides are therefore already
transport-compatible, and Hermes already consumes Verdandi
events in the reverse direction through the hub's ``recent``
control message (its volmarr-core ``verdandi_stimuli`` intake
maps ``runa_reward`` / ``runa_negative`` / ``push_reward`` /
``conv_event`` feed lines).

THE VERDICT: NOT ONE DIALECT — A DOCUMENTED TRANSLATION

The payloads are NOT the same dialect, and neither side may
be silently bent into the other:

- A Verdandi contract-v1 event (event_contract.py) is
  ``{"v": 1, "type": ..., "data": {flat fields}, "source": ...}``
  — the data dict IS the event's fields.
- A Hermes lifecycle event's ``data`` is a second, inner
  envelope: ``{"schema": "runeforge.hermes.lifecycle",
  "schema_version": 1, "event_id": <uuid>, "occurred_at":
  <ISO>, "event": <same type>, "context": {flat fields}}`` —
  the event's fields live one level down, in ``context``,
  behind Hermes's own versioned schema. Hermes carries NO
  ``v`` key; its versioning is the schema name + version.
- Hermes's publisher is fire-and-forget by design: it writes
  one JSON line to the socket with a 100 ms timeout (clamped
  1–1000 ms), reads no reply, and drops the event on any
  failure (fail-open, returns False). It never sees the hub's
  ``ack`` and has NO feed-file fallback — a Hermes event sent
  while the hub is down is gone, where a Verdandi offline
  publish lands in the feed with ``_fallback`` (E-061 §2).
  That asymmetry is a fact of the match, recorded here and
  in the E-068 doc; repairing it is Hermes-side work, not
  this slice's.

Unifying the payloads would break a versioned contract on
one side or the other (a Verdandi shape change is a contract
version bump under E-061's rules; the Hermes envelope is
shared by every volmarr-core publisher family — lifecycle,
cognition telemetry, WYRD changes, entity heartbeat /
routine / consolidation, and the §14 self-aware events —
each under its own ``runeforge.*`` schema name, all v1).
So this module IS the translation in code: the registry of
the eight lifecycle session/turn/tool types with their exact
context fields, the kinship map onto Verdandi's own session
and turn events, and the lossless translator every Verdandi
consumer uses to read a Hermes event in canonical shape.

THE TRANSLATION (``normalize_hermes_event``)

A hub-stamped Hermes event::

    {"type": "hermes.turn.completed", "source": "hermes-agent",
     "data": {"schema": ..., "schema_version": 1,
              "event_id": ..., "occurred_at": ...,
              "event": "hermes.turn.completed",
              "context": {flat fields}},
     "_seq": ..., "_ts": ..., "_iso": ...}

translates to the canonical Verdandi envelope::

    {"v": 1, "type": "hermes.turn.completed",
     "data": {flat fields}, "source": "hermes-agent",
     "_seq": ..., "_ts": ..., "_iso": ...,
     "_hermes_schema": "runeforge.hermes.lifecycle",
     "_hermes_schema_version": 1,
     "_hermes_event_id": ..., "_hermes_occurred_at": ...}

No field is dropped: the inner envelope's four metadata
fields move to ``_hermes_*`` provenance keys (the same
underscore convention as the hub's own stamps and E-061's
``_legacy_dialect``), the context becomes ``data``, and the
type, source and hub stamps pass through untouched. The
translated event passes ``event_contract.validate_publish``
and is registered in ``event_contract.EVENT_SPECS`` (hub
dialect) in this same change, per the contract's own rule.
Translation is for READING: no producer in this tree emits
the Hermes shape, and none may (E-061: producers emit the
canonical envelope).

KINSHIP, HONESTLY STATED (see the E-068 doc §4 for the full
field-by-field table)

- ``hermes.session.started`` / ``hermes.session.ended`` are
  kin to ``ember_session`` (phase start / end) and to the
  logger's ``conv_start`` / ``conv_end`` — but they are NOT
  that event: Hermes knows a session_id, model and platform;
  it has no persona, no conversation_id, no Well state, no
  turn count. The translation does NOT rename them into
  ``ember_session`` — a renamed event would claim fields it
  does not carry.
- ``hermes.turn.completed`` / ``.failed`` / ``.interrupted``
  are kin to ``ember_turn``: Hermes encodes the outcome in
  the TYPE (three types, chosen in the lifecycle bridge),
  where ``ember_turn`` carries one type plus an ``outcome``
  field; Hermes adds task_id / turn_id / exit_reason /
  platform and has none of Ember's memory facts (hits,
  cited, persisted, ungrounded).
- ``hermes.tool.started`` / ``.completed`` / ``.failed``
  have NO Verdandi kin: no event in the E-061 registry
  reports tool calls. That gap is recorded as docket 103,
  owned by the E-076 Part IV gate review — this slice
  registers and translates the tool events; it does not
  invent an Ember tool event to match them.

Stdlib only, no imports from any other Verdandi module —
deployed copies are loaded file-by-file, so this module
must stand alone exactly like event_contract.py does.
"""

from dataclasses import dataclass

# The Hermes lifecycle envelope's own versioning: a schema
# name + version INSIDE data, where Verdandi contract v1
# carries "v" on the outer envelope. Both are version 1;
# they are not the same version field and neither implies
# the other.
HERMES_SCHEMA = "runeforge.hermes.lifecycle"
HERMES_SCHEMA_VERSION = 1

# The publisher's default source label (plugin.yaml's
# `source` config, default "hermes-agent"). The source is
# operator-configurable on the Hermes side, so detection
# below keys on the envelope shape, never on the source.
HERMES_SOURCE_DEFAULT = "hermes-agent"

# The inner envelope's exact field set, in the publisher's
# own construction order (verdandi.build_envelope).
ENVELOPE_FIELDS = (
    "schema",
    "schema_version",
    "event_id",
    "occurred_at",
    "event",
    "context",
)

# Where each inner-envelope metadata field lands in the
# translated canonical envelope. `event` and `context` are
# not here: `event` duplicates the outer `type` (checked
# equal by the translator) and `context` becomes `data`.
PROVENANCE_KEYS = {
    "schema": "_hermes_schema",
    "schema_version": "_hermes_schema_version",
    "event_id": "_hermes_event_id",
    "occurred_at": "_hermes_occurred_at",
}


@dataclass(frozen=True)
class HermesSpec:
    """One Hermes lifecycle event of the E-068 registry.

    ``context_fields`` is the exact field set the lifecycle
    bridge places in the envelope's ``context`` (read from
    plugins/volmarr-core/lifecycle.py at the HEAD named in
    this module's docstring). ``hook`` is the Hermes plugin
    hook the bridge registers for it. ``kin`` names the
    Verdandi event it is matched against in the E-068 doc —
    kinship, not identity: no Hermes type is renamed.
    """

    name: str
    hook: str
    context_fields: tuple
    kin: str


HERMES_SPECS = (
    HermesSpec(
        name="hermes.session.started",
        hook="on_session_start",
        context_fields=("session_id", "model", "platform"),
        kin="ember_session (phase=start) / conv_start",
    ),
    HermesSpec(
        name="hermes.session.ended",
        hook="on_session_finalize",
        context_fields=("session_id",),
        kin="ember_session (phase=end) / conv_end",
    ),
    HermesSpec(
        name="hermes.turn.completed",
        hook="on_session_end",
        context_fields=("session_id", "task_id", "turn_id", "completed",
                        "exit_reason", "model", "platform"),
        kin="ember_turn (outcome=answered)",
    ),
    HermesSpec(
        name="hermes.turn.failed",
        hook="on_session_end",
        context_fields=("session_id", "task_id", "turn_id", "completed",
                        "exit_reason", "model", "platform"),
        kin="ember_turn (outcome=error)",
    ),
    HermesSpec(
        name="hermes.turn.interrupted",
        hook="on_session_end",
        context_fields=("session_id", "task_id", "turn_id", "completed",
                        "exit_reason", "model", "platform"),
        kin="ember_turn (outcome=interrupted)",
    ),
    HermesSpec(
        name="hermes.tool.started",
        hook="pre_tool_call",
        context_fields=("tool_name", "session_id", "task_id", "turn_id",
                        "tool_call_id", "api_request_id"),
        kin="(none — no Verdandi tool event exists; docket 103)",
    ),
    HermesSpec(
        name="hermes.tool.completed",
        hook="post_tool_call",
        context_fields=("tool_name", "session_id", "task_id", "turn_id",
                        "tool_call_id", "api_request_id", "duration_ms",
                        "status", "error_type"),
        kin="(none — no Verdandi tool event exists; docket 103)",
    ),
    HermesSpec(
        name="hermes.tool.failed",
        hook="post_tool_call",
        context_fields=("tool_name", "session_id", "task_id", "turn_id",
                        "tool_call_id", "api_request_id", "duration_ms",
                        "status", "error_type"),
        kin="(none — no Verdandi tool event exists; docket 103)",
    ),
)


def spec_for_hermes(name: str) -> HermesSpec | None:
    """The registered Hermes lifecycle spec for a type, or None."""
    for spec in HERMES_SPECS:
        if spec.name == name:
            return spec
    return None


def is_hermes_event(event: dict) -> bool:
    """True when a raw (possibly hub-stamped) event carries the
    Hermes inner envelope: ``data`` is a dict holding a
    ``runeforge.*`` ``schema``, an ``event`` equal to the outer
    ``type``, and a dict ``context``. Detection keys on shape,
    never on ``source`` (operator-configurable on that side).
    """
    if not isinstance(event, dict):
        return False
    data = event.get("data")
    if not isinstance(data, dict):
        return False
    schema = data.get("schema")
    return (
        isinstance(schema, str)
        and schema.startswith("runeforge.")
        and data.get("event") == event.get("type")
        and isinstance(data.get("context"), dict)
    )


def validate_hermes_event(event: dict) -> list:
    """Errors in a would-be Hermes lifecycle event; [] is valid.

    Valid = the Hermes wire shape for a REGISTERED lifecycle
    type: outer ``type`` / string ``source``, inner envelope
    with exactly ENVELOPE_FIELDS, the lifecycle schema at
    version 1, ``event`` equal to ``type``, and a ``context``
    whose fields are exactly the registered set. Other
    ``runeforge.*`` schemas (cognition, WYRD, entity, §14)
    are the same publisher's other families — recognised by
    is_hermes_event, refused here as outside this registry.
    """
    errors = []
    if not isinstance(event, dict):
        return ["event is not a dict"]
    spec = spec_for_hermes(event.get("type"))
    if spec is None:
        errors.append(f"unregistered Hermes lifecycle type: {event.get('type')!r}")
        return errors
    if not isinstance(event.get("source"), str) or not event["source"]:
        errors.append("source must be a non-empty string")
    data = event.get("data")
    if not isinstance(data, dict):
        errors.append("data must be the Hermes inner envelope (a dict)")
        return errors
    if set(data) != set(ENVELOPE_FIELDS):
        errors.append(
            f"envelope fields {sorted(data)} != registered {sorted(ENVELOPE_FIELDS)}"
        )
        return errors
    if data["schema"] != HERMES_SCHEMA:
        errors.append(f"schema must be {HERMES_SCHEMA!r}, got {data['schema']!r}")
    if data["schema_version"] != HERMES_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {HERMES_SCHEMA_VERSION}, "
            f"got {data['schema_version']!r}"
        )
    if data["event"] != event["type"]:
        errors.append("envelope event must equal the outer type")
    if not isinstance(data["event_id"], str) or not data["event_id"]:
        errors.append("event_id must be a non-empty string")
    if not isinstance(data["occurred_at"], str) or not data["occurred_at"]:
        errors.append("occurred_at must be a non-empty string")
    context = data["context"]
    if not isinstance(context, dict):
        errors.append("context must be a dict")
        return errors
    if set(context) != set(spec.context_fields):
        errors.append(
            f"{spec.name}: context fields {sorted(context)} != registered "
            f"{sorted(spec.context_fields)}"
        )
    return errors


def normalize_hermes_event(event: dict) -> dict:
    """Translate a Hermes-shaped event into the canonical
    Verdandi envelope, losslessly (see the module docstring).

    The context becomes ``data``; the inner envelope's
    metadata moves to ``_hermes_*`` provenance keys; the
    outer type, source and any hub stamps pass through.
    A registered lifecycle event is fully validated first;
    an event of another ``runeforge.*`` schema is translated
    by the same shape rule without a field-set judgement
    (its family's registry lives on the Hermes side).
    Raises ValueError on a shape that is not Hermes's, or on
    a registered lifecycle event that fails validation.
    """
    if not is_hermes_event(event):
        raise ValueError("not a Hermes-shaped event (no runeforge inner envelope)")
    if spec_for_hermes(event.get("type")) is not None:
        errors = validate_hermes_event(event)
        if errors:
            raise ValueError(f"invalid Hermes lifecycle event: {errors}")
    data = event["data"]
    out = {
        "v": 1,
        "type": event["type"],
        "data": dict(data["context"]),
    }
    if "source" in event:
        out["source"] = event["source"]
    for field, provenance in PROVENANCE_KEYS.items():
        out[provenance] = data[field]
    for stamp in ("_seq", "_ts", "_iso", "_fallback"):
        if stamp in event:
            out[stamp] = event[stamp]
    return out

#!/usr/bin/env python3
"""
Verdandi Stimuli — external events enter as typed stimuli
with provenance.

Filed by Project Ember slice E-064 (docs/architecture/
E-064_STIMULI.md). This module IS the stimuli discipline in
code, in the same shape as event_contract.py (E-061),
context_budget.py (E-062) and logger_law.py (E-063): stdlib
only, no imports from any other Verdandi module, because the
deployed copies of the conversation layer load modules
file-by-file from ~/.hermes/state and this discipline must
stand alone exactly like nervous_system.py does. The hub's
own stimulus entrance lives in nervous_system.py as plain
literals (the deployed-standalone pattern); the conformance
tests pin the two copies equal, so they cannot drift.

WHAT A STIMULUS IS

A stimulus is an event that comes from OUTSIDE the companion
— the world touching the nerves — as opposed to an internal
nerve event (E-061), which one part of the system publishes
for another. Until this slice, external things entered in
whatever shape their producer happened to speak: a timer
fired a legacy heartbeat pulse, a check result was folded
into that pulse, an operator could publish any type at all
with the source optional, a signal just set a flag, and a
cron job's start was indistinguishable from a person's
words in the log. Nothing could answer the question "where
did this come from?" from the event itself.

Now every external entrance is named, typed, and required
to carry provenance:

- KIND — one of KINDS: ``time`` (the clock and the
  schedule), ``sensor`` (a check or an OS signal — things
  the machine senses about its world), ``message`` (words
  or structured input addressed to the companion).
- NAME — one of the registered names in STIMULUS_SPECS
  (a ``prefix:*`` pattern matches its family, exactly as in
  the E-061 registry). An unregistered name is not a
  stimulus; registering a new entrance is part of adding it.
- PAYLOAD — a dict of the stimulus's own fields, per spec.
- PROVENANCE — a dict that MUST carry ``origin`` (a
  non-empty string naming who or what produced it) and
  ``channel`` (one of CHANNELS: how it entered), and MAY
  carry ``at`` (an ISO timestamp string from the origin).
  A stimulus without provenance does not enter: validation
  rejects it and the hub entrance publishes nothing.

THE SHAPE

    {"stimulus_version": 1, "kind": <kind>, "name": <name>,
     "payload": {...}, "provenance": {"origin": <str>,
     "channel": <channel>, "at": <iso str, optional>}}

ON THE NERVES

``to_event`` renders a stimulus as a canonical E-061 nerve
event: type ``stimulus:<name>``, source = the provenance
origin, data = {"kind", "name", "payload", "provenance"}.
Provenance therefore survives the feed, the ring buffer and
every reader — it is inside the event's data, not a side
channel. ``from_event`` is the exact reverse and returns
None for any event that is not a stimulus event.
E-071 (privacy of nerves) builds on this: provenance is
recorded so it can be governed, never so it can leak
across personae.

WHAT THIS DOES NOT CLOSE

The hub's open ``publish`` path (E-061's open vocabulary)
still exists for internal and operator use; requiring every
operator publish to be a stimulus is a breaking change no
slice has claimed — it is docket 101, owned by the E-076
gate review. The heartbeat's timer and checks are NOT
rewired in this slice: their pulse still speaks its legacy
dialect (its transport rewiring is E-067's); what this
slice gives them is the typed shape they will enter AS,
registered here with their producers named. The one live
entrance built here is the hub's: nervous_system's
``publish_stimulus_sync`` + ``stimulus`` CLI command, which
accept only validated stimuli and publish nothing on a
validation failure.
"""

from dataclasses import dataclass

STIMULI_VERSION = 1

# The three kinds of outside touch (roadmap E-064: time,
# sensors-shaped inputs, messages).
KIND_TIME = "time"
KIND_SENSOR = "sensor"
KIND_MESSAGE = "message"
KINDS = (KIND_TIME, KIND_SENSOR, KIND_MESSAGE)

# How a stimulus entered. Each registered spec names exactly
# one channel; a provenance carrying any other channel is
# not valid provenance.
CHANNEL_TIMER = "timer"
CHANNEL_CRON = "cron"
CHANNEL_CHECK = "check"
CHANNEL_SIGNAL = "signal"
CHANNEL_CLI = "cli"
CHANNEL_LOG = "log"
CHANNEL_DIRECT = "direct"
CHANNELS = (
    CHANNEL_TIMER,
    CHANNEL_CRON,
    CHANNEL_CHECK,
    CHANNEL_SIGNAL,
    CHANNEL_CLI,
    CHANNEL_LOG,
    CHANNEL_DIRECT,
)

# The nerve-event type prefix a stimulus travels under.
EVENT_TYPE_PREFIX = "stimulus:"


@dataclass(frozen=True)
class StimulusSpec:
    """One registered stimulus entrance.

    ``name`` is the exact stimulus name, or a ``prefix:*``
    pattern for a family (the heartbeat checks). ``channel``
    is the one channel this entrance enters by.
    """

    name: str
    kind: str
    producer: str
    payload_fields: tuple
    channel: str
    notes: str = ""


STIMULUS_SPECS = (
    StimulusSpec(
        name="time.tick",
        kind=KIND_TIME,
        producer="heartbeat/core.HeartbeatDaemon.run (interval timer loop)",
        payload_fields=("pulse_count", "interval_s"),
        channel=CHANNEL_TIMER,
        notes="The daemon's own clock. Today it surfaces as the "
              "legacy heartbeat_pulse (E-061); E-067 rewires that "
              "transport — the stimulus shape it enters as is "
              "registered here.",
    ),
    StimulusSpec(
        name="time.schedule",
        kind=KIND_TIME,
        producer="context_injector / conversation_logger cron sessions "
                 "(log-start)",
        payload_fields=("session", "summary"),
        channel=CHANNEL_CRON,
        notes="A scheduled job beginning: the schedule, not a "
              "person, is the origin of this touch.",
    ),
    StimulusSpec(
        name="sensor.check:*",
        kind=KIND_SENSOR,
        producer="heartbeat/checks (Eir health, Huginn projects, "
                 "Mimir memory, Urdr schedule, Skuld prediction)",
        payload_fields=("severity", "message", "details"),
        channel=CHANNEL_CHECK,
        notes="Suffix is the check's name. A check result is a "
              "sensor-shaped input: the machine reporting what "
              "it sensed about its world. Today these results "
              "are folded into the legacy heartbeat pulse; "
              "E-067 owns their rewiring onto this shape.",
    ),
    StimulusSpec(
        name="sensor.signal",
        kind=KIND_SENSOR,
        producer="heartbeat/signals.SignalHandler (SIGTERM, SIGINT, "
                 "SIGHUP, SIGUSR1, SIGUSR2)",
        payload_fields=("signal",),
        channel=CHANNEL_SIGNAL,
        notes="An OS signal is sensed, not sent by a peer: the "
              "handler sets flags only (its own law); a stimulus "
              "record names which signal arrived.",
    ),
    StimulusSpec(
        name="message.operator",
        kind=KIND_MESSAGE,
        producer="nervous_system CLI stimulus / publish_stimulus_sync "
                 "callers",
        payload_fields=(),
        channel=CHANNEL_CLI,
        notes="The typed operator entrance built by this slice: "
              "payload is the operator's own dict, provenance "
              "is mandatory — unlike the legacy open publish, "
              "which may omit source (docket 101).",
    ),
    StimulusSpec(
        name="message.conversation",
        kind=KIND_MESSAGE,
        producer="conversation_logger entries (start / event / "
                 "update / end)",
        payload_fields=("session_id", "entry_type"),
        channel=CHANNEL_LOG,
        notes="A person's or a cron job's words entering through "
              "the logger. The origin distinguishes them: a "
              "cron session's origin is its job, a person's is "
              "their session — E-071 governs their separation.",
    ),
    StimulusSpec(
        name="message.mood_input",
        kind=KIND_MESSAGE,
        producer="heartbeat/runa_mood_arousal_system (apply_event, "
                 "apply_stimulation, apply_inner_thought, set_location)",
        payload_fields=(),
        channel=CHANNEL_DIRECT,
        notes="Structured input addressed to the mood system by "
              "a direct caller. Its nerve OUTPUT is registered "
              "in the E-061 contract (event:* families); this "
              "spec registers the input side.",
    ),
)


def spec_for(name: str) -> StimulusSpec | None:
    """The registered spec for a stimulus name, or None.

    Exact names win; ``prefix:*`` patterns match by prefix.
    There is deliberately no open fallback: an unregistered
    name is not a stimulus.
    """
    if not isinstance(name, str):
        return None
    for spec in STIMULUS_SPECS:
        if spec.name == name:
            return spec
        if spec.name.endswith(":*") and name.startswith(spec.name[:-1]):
            return spec
    return None


def validate_provenance(provenance) -> list:
    """Errors in a provenance dict; [] means valid.

    Provenance is mandatory: a dict with a non-empty string
    ``origin`` and a ``channel`` in CHANNELS. ``at``, when
    present, must be a non-empty string.
    """
    errors = []
    if not isinstance(provenance, dict):
        return ["provenance must be a dict with origin and channel"]
    origin = provenance.get("origin")
    if not isinstance(origin, str) or not origin.strip():
        errors.append("provenance.origin must be a non-empty string")
    if provenance.get("channel") not in CHANNELS:
        errors.append(
            f"provenance.channel must be one of {sorted(CHANNELS)}, "
            f"got {provenance.get('channel')!r}")
    if "at" in provenance:
        at = provenance["at"]
        if not isinstance(at, str) or not at.strip():
            errors.append("provenance.at must be a non-empty string when present")
    return errors


def validate_stimulus(stimulus) -> list:
    """Errors in a stimulus dict; [] means it may enter.

    A valid stimulus carries the current version, a
    registered name whose spec's kind matches its ``kind``,
    a dict payload, and valid provenance whose channel is
    the channel its spec registers (an entrance cannot
    borrow another entrance's channel).
    """
    errors = []
    if not isinstance(stimulus, dict):
        return ["stimulus is not a dict"]
    if stimulus.get("stimulus_version") != STIMULI_VERSION:
        errors.append(
            f"stimulus_version must be {STIMULI_VERSION}, "
            f"got {stimulus.get('stimulus_version')!r}")
    name = stimulus.get("name")
    spec = spec_for(name) if isinstance(name, str) else None
    if spec is None:
        errors.append(f"name is not a registered stimulus: {name!r}")
    else:
        if stimulus.get("kind") != spec.kind:
            errors.append(
                f"kind must be {spec.kind!r} for {name!r}, "
                f"got {stimulus.get('kind')!r}")
    if not isinstance(stimulus.get("payload"), dict):
        errors.append("payload must be a dict")
    errors.extend(validate_provenance(stimulus.get("provenance")))
    if spec is not None and isinstance(stimulus.get("provenance"), dict):
        channel = stimulus["provenance"].get("channel")
        if channel in CHANNELS and channel != spec.channel:
            errors.append(
                f"provenance.channel must be {spec.channel!r} for "
                f"{name!r}, got {channel!r}")
    return errors


def make_stimulus(name: str, payload: dict, origin: str,
                  channel: str, at: str | None = None) -> dict:
    """Build a validated stimulus; raises ValueError if invalid."""
    provenance = {"origin": origin, "channel": channel}
    if at is not None:
        provenance["at"] = at
    spec = spec_for(name)
    stimulus = {
        "stimulus_version": STIMULI_VERSION,
        "kind": spec.kind if spec else None,
        "name": name,
        "payload": payload,
        "provenance": provenance,
    }
    errors = validate_stimulus(stimulus)
    if errors:
        raise ValueError("; ".join(errors))
    return stimulus


def to_event(stimulus: dict) -> dict:
    """Render a validated stimulus as a canonical E-061 event.

    Raises ValueError on an invalid stimulus — an unprovenanced
    or unregistered stimulus never becomes a nerve event.
    """
    errors = validate_stimulus(stimulus)
    if errors:
        raise ValueError("; ".join(errors))
    provenance = dict(stimulus["provenance"])
    return {
        "v": 1,
        "type": EVENT_TYPE_PREFIX + stimulus["name"],
        "data": {
            "kind": stimulus["kind"],
            "name": stimulus["name"],
            "payload": dict(stimulus["payload"]),
            "provenance": provenance,
        },
        "source": provenance["origin"],
    }


def from_event(event: dict) -> dict | None:
    """The stimulus an event carries, or None if it is not one."""
    if not isinstance(event, dict):
        return None
    event_type = event.get("type")
    if not isinstance(event_type, str) or not event_type.startswith(EVENT_TYPE_PREFIX):
        return None
    data = event.get("data")
    if not isinstance(data, dict):
        return None
    stimulus = {
        "stimulus_version": STIMULI_VERSION,
        "kind": data.get("kind"),
        "name": data.get("name"),
        "payload": data.get("payload"),
        "provenance": data.get("provenance"),
    }
    if event_type != EVENT_TYPE_PREFIX + str(stimulus["name"]):
        return None
    if validate_stimulus(stimulus):
        return None
    return stimulus

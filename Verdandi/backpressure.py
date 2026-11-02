#!/usr/bin/env python3
"""
Verdandi Backpressure — a flooded hub sheds by rule,
reflexes first-protected.

Filed by Project Ember slice E-070 (docs/architecture/
E-070_BACKPRESSURE.md). This module IS the shedding law
in code, in the same shape as event_contract.py (E-061),
context_budget.py (E-062), logger_law.py (E-063),
stimuli.py (E-064), reflexes.py (E-065), nerve_health.py
(E-066) and replay.py (E-069): stdlib only, no imports
from any other Verdandi module, so the discipline stands
alone. The live hub keeps the same rule inline in
Verdandi/nervous_system.py's RingBuffer (deployed copies
are loaded file-by-file, so that file cannot import this
one); the E-070 conformance suite pins the inline copy's
tier table equal to this module's.

THE PROBLEM IT SOLVES

Before this slice the hub's only backpressure was the
ring buffer's ``deque(maxlen=256)``: when the buffer was
full, the OLDEST event fell off, whatever it was. A
flood of mood events could therefore push a heartbeat
pulse — the very event the reflex layer (E-065) needs to
fire a repair — out of the recent tail, silently, with
no record that anything was shed. The feed file kept the
flood (up to its 10 MB rotation), so the loss was
invisible in the one place an operator looks last.

THE LAW

Shedding is by tier, oldest first within a tier, and a
shed event is always counted — never silently dropped:

- Tier 0 PROTECTED — never shed while any lower tier
  remains in the queue. ``heartbeat_pulse`` and
  ``heartbeat_state_change``: the reflex layer fires on
  heartbeat check results (E-065), so these are the
  events a flood must not displace. A protected event is
  shed only as a last resort — when the queue holds
  nothing but protected events and a new protected event
  arrives — and that shed is reported as
  ``protected_shed`` (the honest exception, not a rule).
- Tier 1 HIGH — session and turn lifecycle facts, which
  a replay (E-069) and a session summary need intact:
  conv_start / conv_end, ember_session, ember_turn, the
  Hermes session and turn events, and hermes.tool.failed
  (a failure is a fact; a successful tool call is not).
- Tier 2 NORMAL — everything else that is conversation
  or turn-adjacent: conv_event, conv_update, the Hermes
  tool start/completed events, the reward events, and —
  deliberately — any unregistered or operator type. The
  hub's open vocabulary (E-061) must not be punished for
  being unregistered: an unknown type sheds as normal,
  never as low.
- Tier 3 LOW — shed first. The mood system's high-rate
  chatter: ``event:*``, ``stimulation:*``, ``thought:*``,
  ``location:*`` (the mood system's own families, E-061),
  ``orgasm``, and the retired ``ping`` spec (E-066).
  These are frequent, reconstructible from state, and
  the first thing a tiny machine should stop paying to
  remember when it is flooded.

ADMISSION (one rule, both directions)

When the queue is not full, every event is accepted.
When it is full, the incoming event is compared with
the lowest-priority (highest tier number), oldest event
already queued:

- If the incoming event's tier is better (lower number)
  than that victim's, the victim is evicted and the
  incoming event is accepted.
- If the tiers are equal, the oldest queued event of
  that tier is evicted — the old deque's FIFO behaviour,
  kept inside a tier.
- If the incoming event's tier is worse (higher number)
  than every queued event's, the incoming event itself
  is shed and the queue is untouched.

So a low mood event never displaces a protected pulse,
a protected pulse always displaces a low mood event,
and a flood of same-tier events still behaves like the
ring buffer always did. Nothing in this law ever sheds
a protected event for a lower-tier one.

THE REPORT

Every shed is counted, per tier and per kind
(shed-as-incoming vs evicted-to-make-room), and
``apply_backpressure`` returns the shed events
themselves, in the order they were lost, so a replay
report (E-069) can be checked against them: a shed
``_seq`` should appear as a gap, never as a mystery.
``protected_shed`` is its own counter — it must stay
zero in every ordinary flood, and a non-zero value is a
reportable condition, not a rounding error.

WHAT THIS DOES NOT DO

It does not change the feed file (the feed still takes
every stamped event until its 10 MB rotation — the feed
is the record, the ring is the recent tail, and shedding
here is about the tail, not the archive). It does not
throttle publishers or refuse connections; a publisher
whose event is shed from the ring still gets its hub ack
for the stamped, fed event — shedding is about what the
hub keeps recent, never about whether the event
happened. Subscriber delivery is not reordered by this
law: broadcast still happens in arrival order. And it
does not restart, heal, or rewire anything: nerve
health (E-066) detects the stuck hub, reflexes (E-065)
act on it, and this law only decides what survives a
flood in between.
"""

BACKPRESSURE_VERSION = 1

# The hub's ring size, mirrored here so the law and the
# hub agree on what "full" means (nervous_system.py's
# RING_BUFFER_SIZE). A queue may be built smaller for
# tests or for a tighter profile, but never silently.
DEFAULT_CAPACITY = 256

TIER_PROTECTED = 0
TIER_HIGH = 1
TIER_NORMAL = 2
TIER_LOW = 3
TIER_NAMES = {
    TIER_PROTECTED: "protected",
    TIER_HIGH: "high",
    TIER_NORMAL: "normal",
    TIER_LOW: "low",
}

# Reflex-carrying events (E-065): the Reactor fires on
# heartbeat check results, so the pulse and the state
# change are the events a flood must not displace.
PROTECTED_TYPES = ("heartbeat_pulse", "heartbeat_state_change")

# Session/turn lifecycle facts (E-067/E-068). A failed
# tool call is a fact; a successful one is not, so only
# hermes.tool.failed is high — its started/completed kin
# are normal.
HIGH_TYPES = (
    "conv_start", "conv_end",
    "ember_session", "ember_turn",
    "hermes.session.started", "hermes.session.ended",
    "hermes.turn.completed", "hermes.turn.failed",
    "hermes.turn.interrupted", "hermes.tool.failed",
)

NORMAL_TYPES = (
    "conv_event", "conv_update",
    "hermes.tool.started", "hermes.tool.completed",
    "runa_reward", "runa_negative", "push_reward",
)

# The mood system's high-rate families (E-061), by
# prefix, plus the retired ping spec (E-066).
LOW_PREFIXES = ("event:", "stimulation:", "thought:", "location:")
LOW_TYPES = ("orgasm", "ping")


def event_name(event):
    """The event's type, in every dialect the hub carries.

    Hub dialect ``type``, heartbeat fallback ``event_type``,
    mood dialect ``event`` — in that order, because a hub
    event may legitimately carry an ``event`` key inside
    its data-adjacent shape and the outer ``type`` is the
    authority. A non-dict or a typeless event has no name
    and therefore no tier claim of its own.
    """
    if not isinstance(event, dict):
        return None
    for key in ("type", "event_type", "event"):
        value = event.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def tier_of(event) -> int:
    """The shedding tier of an event (module docstring).

    Exact names first, then the mood prefixes, then the
    open-vocabulary default: an unregistered type is
    NORMAL, never LOW — being unregistered is not a
    reason to be shed first.
    """
    name = event_name(event)
    if name is None:
        return TIER_NORMAL
    if name in PROTECTED_TYPES:
        return TIER_PROTECTED
    if name in HIGH_TYPES:
        return TIER_HIGH
    if name in NORMAL_TYPES:
        return TIER_NORMAL
    if name in LOW_TYPES:
        return TIER_LOW
    if any(name.startswith(prefix) for prefix in LOW_PREFIXES):
        return TIER_LOW
    return TIER_NORMAL


def pressure_level(occupancy: float) -> str:
    """The pressure word for a queue occupancy fraction.

    ``calm`` below 70%, ``pressured`` at 70–99% (a flood
    is building; low events are already at risk), ``full``
    at 100% (every new event now sheds something). The
    words are a report's vocabulary, not a second rule:
    admission is decided by tier, never by level.
    """
    if occupancy >= 1.0:
        return "full"
    if occupancy >= 0.7:
        return "pressured"
    return "calm"


class BackpressureQueue:
    """A bounded queue that sheds by the law above.

    ``offer`` returns a decision dict naming what happened
    to the incoming event and, when one was evicted, which
    event that was. ``kept`` is the queue in arrival order
    (evicted events removed, survivors in place). The
    counters are the shedding record: they are never reset
    by offering more events.
    """

    def __init__(self, capacity: int = DEFAULT_CAPACITY):
        if not isinstance(capacity, int) or isinstance(capacity, bool):
            raise ValueError("capacity must be an int")
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self._kept = []
        self.offered = 0
        self.accepted = 0
        self.shed_incoming = 0
        self.evicted = 0
        self.shed_by_tier = {tier: 0 for tier in TIER_NAMES}
        self.protected_shed = 0

    def __len__(self):
        return len(self._kept)

    @property
    def occupancy(self) -> float:
        return len(self._kept) / self.capacity

    @property
    def pressure(self) -> str:
        return pressure_level(self.occupancy)

    def kept(self):
        return list(self._kept)

    def _record_shed(self, event):
        tier = tier_of(event)
        self.shed_by_tier[tier] += 1
        if tier == TIER_PROTECTED:
            self.protected_shed += 1

    def offer(self, event):
        """Offer one event; return its decision dict."""
        self.offered += 1
        incoming_tier = tier_of(event)
        if len(self._kept) < self.capacity:
            self._kept.append(event)
            self.accepted += 1
            return {"decision": "accepted", "tier": incoming_tier,
                    "evicted": None, "occupancy": self.occupancy,
                    "pressure": self.pressure}
        # Full: the victim is the lowest-priority (highest
        # tier number), oldest queued event.
        victim_index = max(
            range(len(self._kept)),
            key=lambda i: (tier_of(self._kept[i]), -i),
        )
        victim_tier = tier_of(self._kept[victim_index])
        if incoming_tier > victim_tier:
            # Worse than everything queued: shed incoming.
            self.shed_incoming += 1
            self._record_shed(event)
            return {"decision": "shed_incoming", "tier": incoming_tier,
                    "evicted": None, "occupancy": self.occupancy,
                    "pressure": self.pressure}
        victim = self._kept.pop(victim_index)
        self.evicted += 1
        self._record_shed(victim)
        self._kept.append(event)
        self.accepted += 1
        return {"decision": "evicted_lower" if victim_tier > incoming_tier
                else "evicted_same_tier",
                "tier": incoming_tier, "evicted": victim,
                "occupancy": self.occupancy, "pressure": self.pressure}

    def report(self):
        """The shedding record for this queue."""
        return {
            "version": BACKPRESSURE_VERSION,
            "capacity": self.capacity,
            "kept": len(self._kept),
            "offered": self.offered,
            "accepted": self.accepted,
            "shed_incoming": self.shed_incoming,
            "evicted": self.evicted,
            "shed_by_tier": {
                TIER_NAMES[tier]: count
                for tier, count in sorted(self.shed_by_tier.items())
            },
            "protected_shed": self.protected_shed,
            "occupancy": self.occupancy,
            "pressure": self.pressure,
        }


def apply_backpressure(events, capacity: int = DEFAULT_CAPACITY):
    """Run ``events`` through a fresh queue; return kept + report.

    ``kept`` holds the survivors in their original relative
    order (the queue only removes; it never reorders).
    ``shed`` holds the lost events in the order they were
    lost — incoming sheds at the moment they were refused,
    evictions at the moment they were displaced — so a
    replay report (E-069) can be checked against them:
    a shed ``_seq`` should appear as a gap.
    """
    queue = BackpressureQueue(capacity=capacity)
    shed = []
    for event in events:
        decision = queue.offer(event)
        if decision["decision"] == "shed_incoming":
            shed.append(event)
        elif decision["evicted"] is not None:
            shed.append(decision["evicted"])
    report = queue.report()
    report["shed"] = shed
    return {"kept": queue.kept(), "report": report}


def validate_report(report) -> list:
    """Errors in a backpressure report; [] means sound."""
    errors = []
    if not isinstance(report, dict):
        return ["backpressure report must be a dict"]
    if report.get("version") != BACKPRESSURE_VERSION:
        errors.append(f"version must be {BACKPRESSURE_VERSION}")
    if report.get("offered") != report.get("accepted", 0) + report.get(
            "shed_incoming", 0):
        # Every offered event was accepted or shed as
        # incoming; evicted events were accepted first,
        # then lost — they count in accepted, not here.
        errors.append("offered must equal accepted + shed_incoming")
    shed_total = sum(report.get("shed_by_tier", {}).values())
    if shed_total != report.get("shed_incoming", 0) + report.get(
            "evicted", 0):
        errors.append("shed_by_tier must sum to shed_incoming + evicted")
    if report.get("kept", 0) > report.get("capacity", 0):
        errors.append("kept must not exceed capacity")
    return errors

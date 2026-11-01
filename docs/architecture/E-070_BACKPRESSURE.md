# E-070 — Backpressure on Tiny Hardware: a Flooded Hub Sheds by Rule, Reflexes First-Protected

*Part IV, slice E-070. Roadmap line: "Backpressure on
tiny hardware: a flooded hub sheds by rule, reflexes
first-protected." The shedding law in code is
`Verdandi/backpressure.py`; the live hub's ring buffer
carries the same rule inline in
`Verdandi/nervous_system.py`; conformance is pinned by
`tests/unit/test_backpressure_e070.py` (§6).*

## 1. Plain-language summary

When too many events arrive at once, something has to
give — a tiny machine cannot remember everything. Until
now, what gave was simply the oldest event in the hub's
recent-events ring, whatever it was: a flood of mood
chatter could quietly push out the heartbeat pulse that
the companion's reflexes need in order to notice trouble
and repair it, and nothing recorded that anything had
been lost — a shed event was never silently recorded
anywhere, because nothing recorded sheds at all.

Now the hub sheds by rule. Events are ranked: heartbeat
pulses and state changes — the events reflexes fire on —
are protected and are never shed while anything less
important remains; session and turn facts rank next;
ordinary conversation events rank after that; and the
mood system's frequent chatter is shed first. A shed
event is counted, by rank and by kind, and is never
silently dropped — the shedding record is part of what
the hub can report, and a protected event being shed at
all (possible only when the ring holds nothing but
protected events) is its own named counter, not a
rounding error.

## 2. What the tree already held

- **The ring was the only backpressure, and it was
  blind.** `NerveHub.ring_buffer` is a `RingBuffer(256)`
  backed by `deque(maxlen=256)`: at capacity, appending
  evicted the oldest event regardless of kind, with no
  counter and no record. The hub's `recent` answers and
  the context builder read from this ring, so what it
  lost, they lost.
- **The feed is not the ring.** Every stamped event is
  also appended to `nerve_feed.jsonl` (rotation at
  10 MB), so ring eviction never erased the record —
  it erased the *recent tail* that live readers use.
  This slice's law governs the tail; the feed's shape
  is untouched.
- **Reflexes fire on heartbeat events.** E-065 pinned
  the reflex layer: the heartbeat Reactor matches check
  results carried by `heartbeat_pulse`, and
  `heartbeat_state_change` is the daemon's other
  canonical nerve event (E-067). Those two are
  therefore the protected tier — "reflexes
  first-protected" is a dependency, not a preference.
- **The mood families are the flood shape.** E-061
  registered the mood system's hub families —
  `event:*`, `stimulation:*`, `thought:*`,
  `location:*`, plus `orgasm` — as frequent,
  state-reconstructible events: exactly what a tiny
  machine should stop paying to keep first.

## 3. The shedding law (in code: `Verdandi/backpressure.py`)

`backpressure.py` is stdlib-only and standalone, like
every Verdandi contract module since E-061.

- **Tiers.** 0 protected: `heartbeat_pulse`,
  `heartbeat_state_change`. 1 high: `conv_start`,
  `conv_end`, `ember_session`, `ember_turn`, the Hermes
  session/turn events, and `hermes.tool.failed` (a
  failure is a fact; a successful tool call is not —
  `hermes.tool.started` / `.completed` are normal).
  2 normal: `conv_event`, `conv_update`, the reward
  events, and — deliberately — any unregistered or
  operator type: the hub's open vocabulary (E-061) is
  never punished for being unregistered. 3 low: the
  mood prefixes and types above, plus the retired
  `ping` spec (E-066). Names are read from `type`,
  else `event_type`, else `event`, so every dialect
  the hub carries is tiered by the same table.
- **Admission.** Not full: accept. Full: compare the
  incoming event with the lowest-tier, oldest queued
  event. Better tier: the victim is evicted and the
  incoming event accepted. Equal tier: the oldest of
  that tier is evicted (the old ring's FIFO behaviour,
  kept inside a tier). Worse than everything queued:
  the incoming event itself is shed and the queue is
  untouched. A protected event is therefore shed only
  when the queue holds nothing but protected events —
  and then it is counted as `protected_shed`.
- **The record.** `BackpressureQueue` counts offered,
  accepted, shed-as-incoming, and evicted, per tier,
  plus `protected_shed`, occupancy, and a pressure word
  (`calm` below 70%, `pressured` at 70–99%, `full` at
  100% — vocabulary for reports; admission is decided
  by tier alone). `apply_backpressure(events, capacity)`
  runs a batch through a fresh queue and returns the
  survivors in original relative order plus the shed
  events in the order they were lost, so an E-069
  replay report can be checked against them: a shed
  `_seq` should appear as a gap.
- **The live hub.** `nervous_system.RingBuffer` now
  applies the same rule inline (that file is deployed
  and loaded file-by-file, so it carries an inline tier
  table, exactly as it carries nerve health's — E-066);
  the conformance suite pins the inline table and tier
  function equal to the canonical module's, and the
  buffer exposes `shed_count` /
  `protected_shed_count`. Generic typeless events are
  tier normal, so the ring's long-standing FIFO
  behaviour for them is unchanged — the existing
  `Verdandi/tests/test_nervous_system.py` ring tests
  pass unmodified.

## 4. Honest limits

- **Shedding is about the recent tail, not the
  archive.** A shed event still stands in the feed
  (until rotation) and still replays under E-069's
  law. What is lost is its place in `recent` answers —
  which is precisely the loss that must be by rule,
  because the tail is what live readers act on.
- **Publishers are not throttled by this law.** A
  publisher whose event is shed from the ring was
  still stamped, fed, broadcast, and acked; the law
  decides what the hub keeps recent, never whether
  the event happened. Refusing or slowing publishers
  is a different discipline and is not claimed here.
- **Broadcast order is unchanged.** Subscribers still
  receive events in arrival order; tiers decide
  retention, not delivery.
- **A protected shed is possible, and named.** A ring
  filled entirely with pulses will shed the oldest
  pulse for a new one. The law does not pretend
  otherwise; it counts it separately so the condition
  is visible the moment it happens.

## 5. Fixtures

The conformance suite (§6) builds its floods in code:
a low flood that must never displace two protected
events; a protected arrival displacing the oldest low
event (not the oldest event overall); a same-tier
flood proving FIFO survives inside a tier; a
fifty-event mood flood with one pulse in the middle,
which must survive with `protected_shed` at zero; an
all-protected ring proving the last-resort shed is
reported; and the live hub's ring buffer driven
through the same shapes.

## 6. Docket effects

- No new docket items. Dockets 100 / 101 / 102 / 103
  keep their E-076 gate-review owner; this slice's
  shedding record gives E-076 the counters to review,
  and E-069's gap report (§3) is the cross-check the
  roadmap's handoff asked for.
- E-057 table re-measured for the Verdandi weight
  change, as its pinning tests require (see the state
  file's E-070 entry for the figures).

## 7. Slice gate

- New conformance suite:
  `tests/unit/test_backpressure_e070.py` — results in
  the state file's E-070 entry (counts from the runner
  only).
- Prior Part IV conformance, Verdandi focal suites,
  and the root Run B / Run D gates likewise recorded
  in the state file, by the E-017 method.

*Filed by the E-070 slice, 2026-10-31. Next: E-071 —
privacy of nerves.*

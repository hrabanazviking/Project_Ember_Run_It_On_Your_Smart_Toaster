# E-075 — Load Truth: Hub Throughput per Profile, Measured

*Part IV, slice E-075. Roadmap line: "Load truth: hub
throughput per profile, measured." The measuring
instrument is `Verdandi/load_truth.py` (stdlib-only,
standalone); conformance is pinned by
`tests/unit/test_load_truth_e075.py`. Raw reports from
the runs below are kept in
`~/workspace/.verify-tmp/ember-e075/` (`run1.json` –
`run3.json`, plus the solo `toaster.json` probe).*

## 1. Plain-language summary

**The hub is far faster than anything the companion will
ever ask of it — and adding publishers does not make it
faster.** Measured live on the campaign VM, the nerve hub
accepts roughly **1,700–2,700 events per second** from a
publisher holding one connection open, and roughly
**570–660 events per second** through the everyday
producer path (`publish_event_sync`, a fresh connection
per event). The real traffic of a companion is a
heartbeat pulse once a minute and a handful of events
per conversation turn, so even the slowest measured
shape clears a full day of ordinary nerve traffic in
well under a second. The surprise in the numbers is the
ceiling's shape: the hub is one process doing each
event's work in turn (stamp it, write the feed, ring it,
broadcast it, ack it, log it), so eight publishers do not
beat one — they queue, and their worst-case latencies
grow. That is not a defect at companion scale; it is the
truth this slice was ordered to measure, and it is now
on record instead of invented.

## 2. Method — what "per profile" means here

The profiles are the budget book's four (E-041):
toaster, phone, pi, laptop. A profile here is a
**benchmark shape (a simulation envelope), not a device
claim** — the E-048 method, stated the same way:

- the hub process is pinned by `taskset` to the
  profile's CPU count (toaster 1, phone 2, pi 4,
  laptop 4 — a Pi 5 and this VM both have four cores,
  so pi and laptop share a CPU envelope on this machine
  and differ only in publisher shape);
- publishers drive it over persistent connections, one
  ack read per event; subscribers listen and count what
  they receive;
- timed events are `conv_event`s whose stamped feed
  lines measure **~206 bytes per event** in every run —
  the size of a real conversation event, not a
  micro-packet chosen to flatter the hub;
- each profile run is: 32 warmup events (untimed), the
  timed burst, then 60 producer-path events (a fresh
  connection per event, the exact
  `publish_event_sync` shape every in-tree producer
  takes). The whole harness ran **three times**; the
  table reports the **median** of the three, with the
  range where it matters.

**Machine and weather:** the campaign VM (x86, Python
3.12.3), 2026-10-31, while sibling campaigns were
running — load average 5.2–6.3 across the runs. These
are *contended VM* numbers. A solo toaster probe run
just before them, in a quieter minute, read 5,173
events/s persistent and 2,125 events/s producer — the
spread is itself part of the truth: the hub's ceiling
moves with the machine's weather, so this record quotes
medians and ranges, never a single heroic run.

## 3. The measured table

Median of three runs per profile (ranges in §4):

| profile | envelope (CPUs / publishers / subscribers) | persistent events/s | latency p50 / p95 (ms) | producer events/s | hub peak RSS |
|---|---|---|---|---|---|
| toaster | 1 / 1 / 0 | 2735.7 | 0.21 / 0.45 | 566.0 | 22.6 MiB |
| phone | 2 / 2 / 1 | 1660.9 | 0.49 / 2.03 | 640.6 | 22.8 MiB |
| pi | 4 / 4 / 1 | 1657.0 | 0.99 / 3.88 | 636.3 | 22.7 MiB |
| laptop | 4 / 8 / 2 | 1747.3 | 2.14 / 14.10 | 655.8 | 22.8 MiB |

Read it plainly:

- **One publisher is the hub's best shape.** The toaster
  envelope — one CPU, one publisher — posts the highest
  persistent throughput. More publishers share one
  event loop and one feed file; total throughput stays
  flat (~1.7k/s) while per-event latency climbs (laptop
  p95 14.1 ms, worst single events 42–62 ms under
  contention in every profile).
- **The producer face is flat too** (~570–660/s): its
  cost is the connection itself, not the hub's event
  work, so no profile's envelope changes it.
- **The hub's body does not grow with the profile.**
  Peak RSS is 22.6–22.9 MiB in every shape — the E-041
  live-hub figure (21.9 MiB) confirmed under load, well
  inside even the toaster profile's 64 MiB turn ceiling
  (that ceiling prices the core; the hub beside it still
  leaves the toaster envelope honest headroom).

## 4. Correctness, measured with the speed

Every one of the twelve profile runs (3 × 4) finished
with **zero errors** in the harness's own checks:

- ack `_seq` numbers **contiguous** from 1 to the
  published total — 604 events per toaster/phone run,
  1,116 per pi/laptop run; no event lost, none doubled;
- the feed held exactly the published total, every run
  (604 / 604 and 1,116 / 1,116 lines);
- `recent` answered with the ring's full **256** after
  every burst (E-070's ring, at capacity, as designed);
- every subscriber received **every** event published
  while it listened — 604/604 on phone, 1,116/1,116 on
  pi, 1,116/1,116 per subscriber on laptop, warmup
  included;
- ranges behind the medians: persistent throughput
  1,939–2,787 (toaster), 976–1,863 (phone), 1,418–2,489
  (pi), 1,593–2,318 (laptop) events/s; producer
  380–759, 596–760, 605–677, 485–1,040 events/s. The
  ranges are wide because the machine was busy; the
  medians are the citable figures.

## 5. The demand side — what the hub is actually for

Throughput only means something against demand, and
the companion's demand is on record elsewhere in this
part: the heartbeat publishes one pulse per interval
(default 60 s, E-059) plus its state changes; a
conversation turn publishes a session/turn pair and a
few conversation events through the core bridge
(E-067); stimuli arrive at human and timer pace
(E-064). At the budget book's reference workload
(20 turns a day, E-041) the hub sees a few hundred
events *a day*. Against the slowest measured producer
median (566 events/s), a full day of nerve traffic
clears in under a second, and the heartbeat's
once-a-minute pulse is five orders of magnitude below
the measured floor. **No profile needs a faster hub.**
If a future member ever does need more, §3 names the
shape of the wall it will meet — one process, serial
per-event feed + log writes — which is where E-076's
gate review should look first.

## 6. Honest limits

- **VM numbers, simulation envelopes.** No toaster,
  phone, or Pi device was measured by this slice: hub
  throughput on real tiny hardware is **NOT PROVEN**.
  New **docket 107**: the per-profile load truth is a
  VM simulation (taskset envelopes, contended); a real
  Pi hub measurement is the cheapest re-anchor (Mimir
  runs the hub's kin already) and a real toaster-class
  measurement awaits a toaster-class device. Owner:
  the E-076 gate review, which re-roads what it does
  not close.
- **Contention is in every figure.** Load average
  5.2–6.3 throughout; on a quiet machine the same
  harness read roughly double (§2). Ceilings quoted
  from this record should use the medians here — they
  are the pessimistic, defensible ones.
- **One event shape.** Timed events are ~206-byte
  `conv_event`s. Giant payloads price differently (the
  feed write grows with the line); no in-tree producer
  sends them, and E-062 caps what injection reads, but
  this slice measured the common shape only.
- **Subscribers were counted, not stressed.** Two
  listeners at most (the laptop shape). A hall full of
  subscribers is a bridge-era shape (Part VIII), not a
  companion shape, and is not claimed here.

## 7. Docket effects

- New docket 107 (above), owned by E-076.
- E-074's "load truth is not in this document" limit is
  discharged: this doc is the record it pointed at.
- E-057 table re-measured for the Verdandi weight
  change (`Verdandi/load_truth.py` added), as its
  pinning tests require — figures in the state file's
  E-075 entry.

## 8. Slice gate

Recorded in `CAMPAIGN_STATE.md`: the new conformance
suite (`tests/unit/test_load_truth_e075.py`, including
its live mini-run against the real hub), the combined
Part IV conformance run, the Verdandi focal sets, and
the root Run B / Run D gates, by the E-017 method.

*Filed by the E-075 slice, 2026-10-31. Next: E-076 —
Part IV gate.*

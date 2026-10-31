# E-053 — Battery-shaped behaviour: duty cycling, no busy-wait, measured drain shape

*Part III, slice E-053. Roadmap line: "Battery-shaped
behaviour (phone-class): duty cycling, no busy-wait,
measured drain shape." The manners live in
`ember.battery`; the measured anchors live in the budget
book (`ember.budgets`, `MEASURED_BATTERY_*` /
`MEASURED_DUTY_*`); the gate tests are
`tests/unit/test_battery_e053.py`.*

## In plain words

**Ember's heavy background work now minds the battery.**
On a phone-class device running on its battery, the
companion's bulk chores — today, chewing through a pile
of documents into memory — no longer run flat-out until
the charge is gone. They run in **bursts with rests
between**, and the lower the charge falls, the shorter
the bursts and the longer the rests: below half charge,
four batches then a breather; below a fifth, one batch
at a time with long rests; below a tenth, every batch
earns a full rest before the next. Plug the charger in
and the shaping lifts at the next batch — a device on
its charger is not spending its battery. And a rest is
a real rest: the work sleeps **once, in one blocking
sleep**, spending no processor time at all while it
waits. Nothing in Ember sits in a loop waking up again
and again to check the time — that kind of busy-waiting
is exactly what drains a battery while doing nothing,
and this slice both forbids it in the new code and
measured that the rest costs **0.000 seconds of CPU**.

Your own conversation is never rested. Duty cycling
applies only between batches of bulk background work;
a single question's embedding — one batch — never
reaches the shaping at all.

One honesty line up front: **a real battery's drain
rate (percent per hour) is NOT PROVEN by this slice** —
no battery device in the house can run Ember today.
What is measured is the drain's *cause*: how much of
the processor's time shaped and unshaped background
work actually spend. §3 states exactly what was run.

## 1. What existed before (audited this slice)

A search of `src/ember` for power-supply, battery, or
duty-cycle code found **nothing**: the core had no
battery manners at all. The audit also priced the
busy-wait question across the core's waiting loops:

- Chat's main loop blocks on `stdin.readline()` — a
  blocked read, not a spin (E-045's idle hour already
  proved 0.0 s CPU at rest).
- Every other wait in the core is a single blocking
  sleep per wait: the embed client's failure backoff,
  the tether's reconnect backoff, E-051's
  `wait_for_room` (sleep the level's delay, then
  re-read — bounded, and a re-read per delay, not a
  poll).
- No loop in `src/ember` sleeps in small increments to
  poll a condition.

So the no-busy-wait half of this slice is two acts:
keep that property in the new duty code (one blocking
sleep per rest, pinned by tests that record the exact
sleep calls), and measure the rest's CPU cost (§3).

## 2. The manners (`ember.battery`, stdlib only)

**Reading the battery.** The Linux power-supply shape
under `/sys/class/power_supply` — the shape
Android-class and embedded Linux hosts expose: a
supply whose `type` reads `Battery`, its `capacity`
percent, its `status` (Charging/Full → on the charger;
Discharging → spending the battery; anything else →
unknown). Mains supplies are skipped. A capacity that
will not parse, or falls outside 0–100, is not a
reading. **No battery, or an unreadable gauge, reads
`None` — unknown, never guessed.** The campaign VM
reads exactly that (§3), as would the house Pi: both
are mains-fed, and the reading says so plainly.

**Judging the charge** (`assess`, pure):

| Mode | When | Background work's shape |
|---|---|---|
| FULL | charging, no battery, unknown charge, or ≥ 50% | unshaped — no rests imposed |
| CONSERVE | discharging, < 50% | bursts of 4 batches, one 5 s rest between |
| LOW | discharging, < 20% | 1 batch at a time, 15 s rests |
| CRITICAL | discharging, < 10% | every batch followed by a 30 s rest |

Charging always votes FULL, at any gauge: the charger,
not the battery, is paying. Unknown never votes: a
mains-fed machine is not asked to pretend it has a
battery, and an unreadable gauge never invents a
crisis. Every assessment carries a plain reason naming
the deciding fact. At CRITICAL the work *crawls*
rather than stopping — one batch per rest — because a
silently halted ingest is its own failure; the person
watching a nearly dead battery can interrupt, and the
shape they see is the stated one.

**Duty cycling** (`DutyCycler`). Consulted between
batches (the same hook point as E-051's patience, in
the embedding client). Each consultation **re-reads
the battery**, so the shape follows the charge as it
moves: a charger plugged in mid-job unshapes the rest
of the job at the next batch boundary; a falling
charge tightens it the same way. The cycler counts
batches since the last rest; when a burst is spent it
rests **once — a single blocking `sleep` of the plan's
full rest**. The tests pin the sleep-call record
exactly (`[5.0, 5.0]` for two CONSERVE rests), so a
future change that chopped a rest into polling
micro-sleeps would fail the gate by shape, not by
timing luck. The cycler keeps its counters (`rests`,
`rested_s`), so a job can state the shape it ran under.

These numbers are *policy*, stated manners pinned by
the E-053 tests — the charge lines and rest lengths
are choices, not measurements. The measurements are
§3's, and they live in the budget book.

## 3. The drain shape, measured (VM profile, 2026-10-31)

Probe in `~/workspace/.verify-tmp/ember-e053/probe.py`
(results in `probe.json`; a second confirmatory run in
`probe2.json`), run against the real module on this
campaign VM while sibling campaigns were running — the
contention is stated because it shapes the wall clock,
and both runs below ran back to back under it.

**This machine's own reading:** no battery present
(`/sys/class/power_supply` holds no battery supply) —
assessment FULL, reason "no battery is present — this
machine is mains-fed, so background work is not
battery-shaped". The reader tells the truth about the
house's machines instead of inventing a phone.

**A rest costs no CPU.** One single blocking rest of
5 s (the CONSERVE rest, real `time.sleep`): process
CPU **0.000 s** over 5.001 s of wall (second run:
0.0001 s over 5.000 s). That is the no-busy-wait fact
as a number — pinned in the book as
`MEASURED_BATTERY_REST_CPU_S = 0.0`.

**The shaped job vs the unshaped job.** A unit of
work is 0.25 s of process CPU (a busy loop calibrated
by process time, so a unit is a unit on any host); the
job shape is the embedding client's — the duty hook
consulted between batches only:

| Job | Units | CPU | Wall | CPU / wall | Rests |
|---|---|---|---|---|---|
| FULL (100% shape) | 16 | 4.001 s | 9.719 s | **0.4117** | 0 |
| CONSERVE (40% shape) | 12 | 3.001 s | 15.921 s | **0.1885** | 2 × 5 s = 10.0 s |

CPU/wall sits below 1.0 even unshaped because the
contended VM deschedules the process; the fraction's
honest use is comparative, and the comparison is the
measurement: **duty-cycled at CONSERVE, background
work spent less than half the CPU-over-wall of the
unshaped job beside it** (second run: 0.1722 against
0.4653 — the same shape). Counted over work + rest
only, contention excluded, CONSERVE's imposed duty is
3.001 / 13.001 ≈ **23%** against FULL's 100% — bursts
of work, then real rest, is what the drain of a
background job is made of, and the shaping cuts it to
about a quarter. The fractions are pinned in the book
as `MEASURED_DUTY_FULL_CPU_FRACTION` and
`MEASURED_DUTY_CONSERVE_CPU_FRACTION`.

What this does **not** prove: how fast any real
phone's battery percentage falls under either shape.
That needs a battery device running Ember — the
house's paired phone was offline at E-048 and the tree
holds no phone runtime, so percent-per-hour stays
NOT PROVEN, and the % lines in §2 are policy resting
on the measured CPU shape, not on a measured drain.

## 4. The wiring

- `OllamaEmbedClient` gains an optional `battery_hook`,
  consulted at the same between-batches point as the
  patience hook — never before the first batch, never
  mid-batch. A single-batch embed (the foreground
  shape: one turn's query) never calls either hook.
  Default is `None`: no behaviour change for any
  existing caller.
- The local-files ingest orchestrator
  (`ember.well.smidja.local_files.run`) builds its
  default client **with** a fresh `DutyCycler` as the
  battery hook, beside E-051's patience hook: `ember
  well ingest` is the bulk background act, and it is
  the one that now minds the battery. A client a caller
  passes in explicitly is the caller's own shape and is
  untouched. On a mains-fed host (every machine in the
  house today) the cycler's reading is "no battery"
  and it never rests — the wiring costs those machines
  one sysfs read per batch boundary and nothing else.
- Chat's per-turn embedding and the MCP server's query
  embedding construct their clients without the hook —
  foreground, one batch, never rested.

## 5. Honest limits

- **No real battery was read or drained.** The sysfs
  reader is pinned against the real file shape in
  tests and reads this VM honestly as battery-less;
  a phone-class device's own reading, and any
  percent-per-hour drain, are NOT PROVEN until a
  battery device runs Ember (E-048's open door).
- **CPU duty is the drain's cause, not the drain.**
  Screen, radios, and the model itself also spend a
  phone's battery; this slice shapes Ember's
  background CPU only — the part Ember owns — and
  says so.
- **The wall fractions are contended-VM numbers.**
  Their durable content is the comparison and the
  rest arithmetic, not the third decimal; the anchors
  record the day, the method, and both runs.
- **Only ingest is shaped so far.** As with E-051's
  etiquette, other bulk acts adopt the cycler when
  their own slices touch them; this slice builds the
  manners and wires the first, largest background act.

## Tests

- `tests/unit/test_battery_e053.py` — **15 passed**
  (default env): the policy lines pinned at their
  stated values; the charge ladder rung by rung;
  charging and unknown never draining, each with its
  reason; the sysfs reader (capacity + status, mains
  skipped, absent/malformed/out-of-range → unknown,
  this machine read honestly); the cycler (FULL never
  rests; CONSERVE rests once per spent burst with the
  exact single-sleep record; LOW and CRITICAL rest
  after every batch; the battery re-read each
  consultation, a mid-job charger unshaping the job);
  the measured anchors pinned exactly, with the shaped
  fraction under half the unshaped; and the wiring
  (hook fires between batches only, a single-batch
  embed is never rested, gate-wiring test).

- Slice gate Run B (default env, pgvector file excluded):
  **1017 passed, 6 proven-environment failures, 25 skipped,
  1 warning** — the E-052 baseline of 1002 plus this
  slice's 15; the 6 failures are the proven environment
  failures (E-004/E-017).
- Slice gate Run D (whole, extras): **1074 passed,
  0 failed, 19 skipped, 1 warning**, exit 0 — the whole
  suite green in the extras shape, the new tests passing
  there as real tests.

*Filed by the E-053 slice, 2026-10-31. Next: E-054 —
graceful smallness (at budget's edge the companion sheds
features by the stated ladder, announcing each shed).*

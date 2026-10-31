# E-051 — Thermal & patience etiquette: the companion yields

*Part III, slice E-051. Roadmap line: "Thermal & patience
etiquette: on shared/small machines the companion yields
(load-aware throttling, the Aesir lesson)." The manners
live in `ember.etiquette`; the gate tests are
`tests/unit/test_etiquette_e051.py`.*

## In plain words

**The companion now has manners on a busy or hot
machine — and before today it had none at all.** If you
share a small computer with other work, or the little
board is getting hot, Ember's heavy background chores
now notice, pause, and wait for room before carrying on.
The wait is never endless: half a minute at most, and
then the work goes ahead and the fact that it waited is
written down, not hidden. Your own conversation is never
made to wait — the manners apply only to bulk background
work, and the first of those is the memory-store ingest:
when Ember is chewing through a pile of documents, it
now pauses *between batches* of embedding whenever the
machine is loaded or hot, instead of piling batch on
batch onto a machine that is already struggling.

This is the Aesir lesson carried over: use the whole
machine when it is free, never choke off other running
work, watch the temperature, and back off *before* the
danger zone — not once you are in it.

## 1. What existed before (audited this slice)

A search of `src/ember` for load averages, thermal
sensors, throttling, or yielding found nothing: the only
"temperature" in the core is the model's generation
setting — a knob for how the model writes, not a reading
of the machine. Bulk embedding during ingest
(`OllamaEmbedClient.embed`) ran batch after batch with
only a failure-backoff between them. On the project's
own target machines — a shared Pi, a phone-class board —
that is exactly the behaviour the roadmap names.

## 2. The manners (`ember.etiquette`, stdlib only)

**Reading the room.** Two signals, both read without
guessing:

- *Load* — the 1-minute load average divided by the CPU
  count (`os.getloadavg` / `os.cpu_count`), so the line
  means the same on any core count: 1.0 is "every core
  already has a job".
- *Heat* — the hottest `thermal_zone*/temp` sensor under
  `/sys/class/thermal`, millidegrees turned into °C (the
  shape a Pi exposes).

A signal that cannot be read is `None` and **does not
vote** — it neither raises nor lowers the judgement. The
campaign VM exposes no thermal zones at all (§3), and
etiquette there judges load alone rather than inventing
a temperature.

**Judging the room** (`assess`, pure — worst signal
wins):

| Level | Load per CPU | Hottest sensor | Background work |
|---|---|---|---|
| PROCEED | < 1.0 | < 70 °C | carries on |
| EASE | 1.0 – < 2.0 | 70 – < 80 °C | pauses 1 s, looks again |
| YIELD | ≥ 2.0 | ≥ 80 °C | pauses 5 s, looks again |

The thermal yield line sits *at* the point where small
boards begin throttling themselves (a Pi 5 throttles
around 80 °C) and the ease line well below it — back
off before the danger zone. Every assessment carries a
plain reason sentence naming the deciding signal.

**Waiting, bounded** (`wait_for_room`). For background
work only: sleep the level's delay, re-read the room,
repeat — but never past **30 s total** (`MAX_WAIT_S`).
Past the bound the work proceeds anyway and the returned
`PatienceOutcome` records `bound_reached=True`, the
seconds waited, and the number of checks. Patience is
etiquette, not a deadlock: a neighbour who never
quietens down cannot starve Ember's chores forever, and
when that happens it is stated, not silent.

These numbers are *policy*, stated manners pinned by
the E-051 tests — not measurements, and not budget-book
ceilings; no `ember.budgets` entry moves in this slice.

## 3. The room, read live (VM profile, 2026-10-31)

Probe in `~/workspace/.verify-tmp/ember-e051/probe.py`
(results in `probe.json`), run against the real module
on this campaign VM (4 CPUs) while sibling campaigns
were running — the shared-machine case itself:

- load per CPU **1.75** (1-minute load ≈ 6.99) → the
  assessment was **EASE**: "the machine is busy at
  1.75 load per CPU — background work eases off".
- thermal **None** — the VM exposes no thermal zones,
  and the assessment says so by its absence rather than
  inventing a reading.
- A bounded wait with the bound set to 3 s for the
  probe waited exactly **3.0 s over 4 checks**, the room
  still busy, and returned `bound_reached=True` — the
  bound working on a real room, not only in tests.

Device heat is NOT PROVEN here: no Pi thermal reading
was taken in this slice (E-047–E-049's device work did
not need one; the sensor parser is pinned against the
real `/sys` file shape in tests). A Pi re-anchor of the
thermal half belongs with the next device visit; the
load half is already proven on the VM's real contention.

## 4. The wiring

- `OllamaEmbedClient` gains an optional `patience_hook`,
  consulted **between batches** — never before the first
  batch, never mid-batch. A single-batch embed (the
  foreground shape: one turn's query) therefore never
  waits, etiquette or no etiquette. Default is `None`:
  no behaviour change for any existing caller.
- The local-files ingest orchestrator
  (`ember.well.smidja.local_files.run`) builds its
  default client **with** the hook (`wait_for_room`):
  `ember well ingest` is the bulk background act, and
  it is the one that now yields. A client a caller
  passes in explicitly is the caller's own shape and
  is untouched.
- Chat's per-turn embedding and the MCP server's query
  embedding construct their clients without the hook —
  they are foreground, one batch, and a person's
  question never waits for manners.

## 5. Honest limits

- **Load is a lagging, shared signal.** The 1-minute
  average describes the whole host, neighbours included
  — which is the point (etiquette is about the shared
  machine), but it cannot attribute load to anyone, and
  a short spike inside a minute is smoothed away.
- **Heat is only as real as the sensors.** Linux
  thermal zones are the Pi shape; other hosts may
  expose none (this VM) or expose them elsewhere, and
  those machines get load-only etiquette until a reader
  for their shape exists. No temperature is ever
  fabricated.
- **Only ingest yields so far.** The other bulk acts
  (a large Well drain, a future member's batch job)
  adopt the same hook when their own slices touch
  them; this slice builds the manners and wires the
  first, largest background act.
- **The bound is a promise both ways.** Under a
  permanently saturated host, background work waits
  the full 30 s per gate call and then proceeds —
  slower, stated in the outcome, never stuck.

## Tests

- `tests/unit/test_etiquette_e051.py` — **14 passed**
  (default env): the policy lines pinned at their
  stated values; the load and thermal ladders rung by
  rung; worst-signal-wins with unknown signals never
  voting; per-CPU division and unreadable-load → None;
  the thermal parser (hottest zone, malformed skipped,
  absent → None); the bounded wait (immediate proceed,
  per-level delays then re-check, the bound reached
  exactly and stated); and the wiring (hook fires
  between batches only, a single-batch embed never
  calls it, gate-wiring test).

- Slice gate Run B (default env, pgvector file excluded):
  **989 passed, 6 proven-environment failures, 25 skipped,
  1 warning** — the E-050 baseline of 975 plus this
  slice's 14; the 6 failures are the proven environment
  failures (E-004/E-017).
- Slice gate Run D (whole, extras): **1046 passed,
  0 failed, 19 skipped, 1 warning**, exit 0 — the whole
  suite green in the extras shape, the new tests passing
  there as real tests.

*Filed by the E-051 slice, 2026-10-31. Next: E-052 —
update weight (an update's download + apply cost per
profile; metered connections respected).*

# E-045 — Idle discipline: at rest, the companion costs ~nothing

*Part III, slice E-045. Roadmap line: "Idle discipline: at rest
the companion costs ~nothing — measured over an hour, per
profile."*

## In plain words

**Left alone for a full hour, the companion did nothing at
all — and that is now measured, not hoped.** Four copies of
the companion, one for each machine size in the budget book,
sat open on their memories for 3,600 seconds with nobody
talking to them. Across all 121 checks made during that hour:

- **No processor time was spent.** Each companion's CPU clock
  read exactly the same at the end of the hour as at the
  start — 0.0 seconds used, on every profile. Nothing polls,
  nothing wakes to check the time, nothing spins.
- **No extra threads appeared.** Every companion stayed at
  exactly one thread the whole hour: the one thread waiting
  for its person to type.
- **Memory never grew.** It only ever went down, sample by
  sample, settling from the ~41 MB it starts at to about
  23 MB by the twenty-minute mark and staying flat there for
  the remaining forty minutes. The peak (high-water mark)
  never rose above its starting value on any profile.
- **Nothing was written to disk.** Each companion's on-disk
  footprint was byte-for-byte identical at every check:
  164,616 bytes, first sample to last.

E-041 had photographed idle RAM at one instant (40.7 MB).
An instant cannot show a slow leak, a waking timer, or a
quiet background writer. The hour can, and it shows none.

## 1. The hour, measured (VM profile, 2026-10-31)

Method: one probe per profile (toaster, phone, pi, laptop)
run concurrently, each probe being the companion's real idle
shape — full CLI/chat surface imported, that profile's
conversation config loaded, the real `sqlite_vec` Well open —
then blocked reading stdin, exactly as `chat` waits for the
operator. A separate sampler read each probe's `/proc` entry
every 30 s for 3,600 s (121 samples), then closed stdin so
the probes shut down cleanly (all four exit codes 0). Probe
and sampler scripts and raw samples live in
`~/workspace/.verify-tmp/ember-e045/` (`idle_probe.py`,
`sampler.py`, `run-3600s/samples.jsonl`, `run-3600s/summary.json`).
Python 3.12.3 on the campaign VM — VM numbers, as always
(docket 90 stands); profiles differ in the history they allow,
not in the idle process shape, so the four rows are near-equal
by construction and are reported per profile because the
roadmap asks per profile.

| Profile | CPU used in the hour | Threads (max) | RSS first → last | Peak (HWM) | Disk bytes first → last |
|---|---|---|---|---|---|
| toaster | 0.0 s (0.00%) | 1 | 40.8 → 23.0 MiB | 40.8 MiB | 164,616 → 164,616 |
| phone | 0.0 s (0.00%) | 1 | 40.8 → 23.0 MiB | 40.8 MiB | 164,616 → 164,616 |
| pi | 0.0 s (0.00%) | 1 | 40.9 → 23.0 MiB | 40.9 MiB | 164,616 → 164,616 |
| laptop | 0.0 s (0.00%) | 1 | 40.8 → 23.0 MiB | 40.8 MiB | 164,616 → 164,616 |

Against the book: the toaster's idle ceiling is 64 MiB
(E-041); the hour's peak on every profile is ~41 MiB —
inside the smallest ceiling with the same headroom E-041
measured at an instant. CPU, threads, and disk have no
ceilings in the book because they were never before
measured; this slice records their zero line: **0 CPU,
1 thread, 0 bytes written** — the numbers E-056's regression
armour and E-191's week-shaped soak will be judged against.

### The falling RSS, stated honestly

RSS declined monotonically — no sample on any profile is
higher than the one before it — reaching a ~23.0 MiB floor
at ~1,261 s and holding it, unchanged, for the last ~2,340 s.
This record claims the observation, not a mechanism: the
probes did no work that could free memory themselves (their
CPU never advanced), so the decline is the interpreter /
kernel returning or reclaiming untouched pages while the
machine was busy elsewhere. What matters for the discipline
is the direction and the ceiling: idle memory never grows,
and its high-water mark never exceeds the starting shape
E-041 already priced.

### Shorter runs in the same shape

A 60-second run (10 s interval, 7 samples) preceded the hour
and showed the same discipline at smaller scale: 0.0 CPU,
1 thread, disk identical, RSS already declining
(40.9 → 35.1 MiB). It is a rehearsal, not evidence; the hour
above is the slice's evidence.

## 2. The gate: this discipline is now a test

`tests/unit/test_idle_discipline_e045.py` — **5 tests**
(4 profile probes + 1 gate-wiring test). Each profile test
re-derives the discipline at gate scale in a fresh
subprocess: a 15-second idle window sampled every 3 s from
outside, asserting CPU advance ≤ 2 ticks (20 ms of
housekeeping tolerance; a polling loop would spend orders
of magnitude more), exactly 1 thread throughout, final RSS
inside the toaster's idle ceiling and inside 1.5× E-041's
measured idle anchor, settled RSS wandering ≤ 2 MiB after
the first sample, and a byte-identical Well directory.
Measurement discipline is E-042's: peaks and CPU are read
from `/proc` by the parent, never `ru_maxrss`.

In the default (bare) environment the Well-open shape
cannot run, so the four profile tests **skip with the
reason stated** and the wiring test passes; in the extras
shape all 5 run and pass (measured this slice: **5 passed**
standalone, extras shape).

## 3. Docket

No new docket items. Docket 90 (VM anchors) stands: this
hour is a VM hour, and E-047–E-049 re-anchor on real
devices. No defect was found by this slice — the hour is
the cleanest measurement the campaign has taken — and
nothing in `src/` was changed: the discipline was already
the code's behaviour; this slice proves it and arms the
gate against its regressing.

## 4. Honest limits

- **VM, concurrently loaded.** The four probes idled on a
  shared VM while other campaign work ran; that makes the
  zero-CPU result stronger (even under neighbours, nothing
  woke) and the RSS decline partly the host's weather
  (stated above, not hidden).
- **The idle shape is the chat shape.** A companion idles
  as `chat` waiting on stdin with the Well open. Members
  (Verdandi's hub/heartbeat, E-041 §1) have their own idle
  costs, measured in their own Parts — this slice prices
  the core only, per the book's rule.
- **One hour is not a week.** Slow-enough leaks (bytes per
  day) are below this window's resolution by construction;
  E-191's week-shaped soak owns that scale. Within the
  hour, the resolution is exact: CPU ticks, thread count,
  and disk bytes are integers, and all three never moved.

## Tests

- `tests/unit/test_idle_discipline_e045.py` — extras shape
  standalone: **5 passed**. Default env: the 4 profile
  tests skip (reason stated), the wiring test passes.
- Slice gate Run B (default env, pgvector file excluded):
  **949 passed, 6 proven-environment failures, 24 skipped,
  1 warning** — 948 E-044 baseline + 1 new passing (the
  wiring test; the 4 profile tests join the skipped, as
  designed). The 6 failures are the proven environment
  failures (E-004/E-017).
- Slice gate Run D (whole, extras): **1022 passed,
  0 failed, 20 skipped, 1 warning**, exit 0 (275 s; the
  four 15-second idle probes run inside it) — the whole
  suite green in the extras shape, the new tests passing
  there as real tests, not skips.

*Filed by the E-045 slice, 2026-10-31. Next: E-046 — cold
start on the smallest profile (time-to-first-word measured
+ capped).*

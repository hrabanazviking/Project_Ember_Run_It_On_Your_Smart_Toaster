# E-042 — Budget tests: the ceilings become automated tests

*Part III, slice E-042. Roadmap line: "Budget tests: the
ceilings become automated tests wired into the campaign's
slice gate." The tests are
`tests/unit/test_budget_gate_e042.py`; the book they enforce
is `ember.budgets` (E-041).*

## In plain words

**The budget book is no longer something a person has to
remember to check — the test suite checks it on every run.**
Each budget test measures the companion again, right then, in
a fresh little process of its own: how big the program is on
disk, how much memory it uses sitting idle, how much it uses
while answering, and how fast its storage grows. If any of
those measurements ever crosses the ceiling promised for a
machine size — even the smallest "toaster" size — a test fails
loudly, in the book's own plain words, instead of the problem
being discovered later on someone's small machine.

Measured again today, everything still fits with room to
spare. One honest wrinkle: the fresh storage measurement came
out a little higher than the book's estimate (about 808 bytes
per conversation turn instead of 694 — the diary lines are a
bit longer than the first estimate, and a shorter measurement
run rounds the memory-file growth up). Even at the higher
figure, a month of daily chatting grows storage by under half
a megabyte, far inside even the toaster's allowance. The
difference is recorded below as docket 91 for the storage
slice (E-050) to re-measure at larger scale — the gate's drift
band caught it, which is the gate working as designed.

## What the tests do

All in `tests/unit/test_budget_gate_e042.py` (**9 tests**),
each judging a shape it re-derives in this run — per E-041
§4's instruction, re-derive, not just re-assert:

- **Gate wiring** (1 test): this file must live under
  `tests/unit/`, where the campaign's slice gate (the E-017
  method's Run B / Run D, which run the whole root suite)
  collects it. If the file ever moves out of the gate's path,
  this test fails instead of the budgets silently unwiring.
  Because the tests sit in the standard suite, **every future
  slice's gate runs them** — that is the wiring the roadmap
  asks for; there is no separate budget command to forget.
- **Install** (1): the `src/ember/` tree is weighed byte by
  byte (bytecode caches excluded) and judged against the
  toaster's install ceiling from the book, and against
  E-041's measured all-in anchor — the package alone may
  never outweigh the whole install E-041 measured.
- **Idle RAM** (2): a fresh subprocess imports the full
  CLI/chat surface and reports its own peak RSS, judged
  against the toaster's idle ceiling; where the `sqlite_vec`
  extra is present, the heavier Well-open idle shape is
  measured the same way. Where the extra is absent the
  Well-open test **skips with its reason stated** — the bare
  shape still runs, because the bare shape is the default
  gate's world (docket 13).
- **Turn RAM** (4, one per profile): a fresh subprocess runs
  five real `chat.run` turns per profile (labelled fake
  model, in-memory Well, history at the profile's cap —
  E-041's fixture shape), asserts all five turns persisted,
  and judges the peak against that profile's turn ceiling
  **and** the toaster's — re-deriving E-041's flatness
  finding (turn cost is the idle cost at fixture scale)
  instead of trusting it.
- **Storage growth** (1): where `sqlite_vec` is present, a
  fresh subprocess grows a real Well by 30 typical episodes
  and measures the closed file's growth per episode, and
  measures the diary's per-turn bytes from two real sessions
  (1 turn, then 5 more; the difference over 5). The projected
  month at the reference workload (20 turns/day) is judged
  against the toaster's storage ceiling. Absent the extra,
  it skips with its reason stated.

Every ceiling comes from `ember.budgets` at run time — no
second hard-coded copy of the book exists in the tests. The
only hard-coded numbers are E-041's anchors, used as a
**drift band**: a re-derived shape may wobble to 1.5× its
anchor (machine weather moves RSS), but a move beyond that
is treated as a regression, not weather.

**The gate bites, proven:** with the toaster's turn ceiling
shrunk to 1.0 MiB in memory (a mutation check run for this
slice, not committed), the turn test fails with "toaster turn
peak 24.5 MiB exceeds its ceiling of 1.0 MiB" — the failure
message is the book's own sentence shape.

## Re-derived shapes (VM profile, 2026-10-31, extras shape)

Raw capture: `~/workspace/.verify-tmp/ember-e042/rederived.log`.

| Shape | Re-derived | E-041 anchor | Toaster ceiling |
|---|---|---|---|
| Package tree | 740,135 B | 729,802 B (source) / 978,843 B all-in | 2 MiB |
| Idle, CLI surface (peak) | 25.2 MiB | 25.3 MiB | 64 MiB |
| Idle, Well open (peak) | 35.9 MiB | 40.7 MiB | 64 MiB |
| Turn peak, all 4 profiles | 24.3 MiB (flat) | 39.4–40.1 MiB (real Well) | 64 MiB |
| Well growth / episode | 683 B (30 episodes) | 614 B (100 episodes) | — |
| Diary / turn | 126 B | ~80 B (estimate) | — |
| Projected month @ 20 turns/day | 0.46 MiB | 0.40 MiB | 2 MiB |

Notes on the deltas, honestly: the turn peaks here use the
in-memory Well, E-041's own isolation shape (~24 MiB there
too — the real-Well shape remains the anchor, and the drift
band is checked against it). The package grew 10,333 B since
E-041 — that growth is E-041's own `budgets.py` plus its
bytecode-free source weight, accounted, not drift.

## A measurement bug found by the gate itself — fixed in scope

The first whole-suite Run D failed six of the nine new tests:
every RAM probe reported the **identical 71.9 MiB** — idle,
Well-open idle, and all four turn profiles. A constant across
different shapes is never the shape's own number. Cause,
proven by bisection and by the fix: the probe measured its
peak with `ru_maxrss`, and on Linux that figure lives in the
process's signal_struct and **survives exec** — a probe
fork+exec'd from the pytest process inherits the *parent's*
peak (71.9 MiB was pytest's own high-water mark at fork
time; the per-file runs, whose parent was smaller, had
passed, which is why the defect only showed at whole-suite
scale). The probe now reads `/proc/self/status` **VmHWM**,
the child's own mm high-water mark, which resets at exec;
the nine-file reproduction set that failed before now
passes whole (122 passed), and the re-derived numbers above
are the VmHWM figures. E-041's anchors stand untouched —
its scripts ran as top-level processes, where the two
measures agree, and the VmHWM re-derivation lands on the
same numbers (25.2 vs 25.3 MiB idle). Lesson recorded in
the test file's header for every future measuring slice:
**a subprocess measured with `ru_maxrss` from a large
parent measures the parent.**

## New docket items

(91) Re-derived storage runs higher than the book's
per-turn figure: Well growth 683 B/episode over 30 episodes
(vs 614 over 100 — smaller runs round up through SQLite page
granularity) and diary 126 B/turn measured from real sessions
(vs the ~80 B/turn estimate E-041 derived from one 5-turn
file). Combined 808 B/turn vs the book's 694 — inside the
gate's 2× drift band and inside every ceiling (projected
0.46 MiB/month vs the toaster's 2 MiB), so no ceiling moves
in this slice; assigned to **E-050** (storage growth) to
re-anchor `ember.budgets`' per-turn constants from a
larger-N measurement and record whether the book's 694
becomes ~808 or the 30-episode figure was page rounding.

## Honest limits

- **VM anchors still.** Every number above is this VM's
  (docket 90 stands): the gate pins the VM shapes, and
  E-047–E-049 re-anchor per real device.
- **Fixture scale, again.** Turn RAM is five fixture turns
  against a fake model — the same stated limit as E-041;
  the gate catches core growth, not model weight (the model
  is not Ember's cost, E-041 §3).
- **Two tests skip in the bare env** (Well-open idle and
  storage), by the stated sqlite_vec guard; in the extras
  shape all 9 run and pass. A skip here is a named absence,
  never a silent pass.

## Tests

- `tests/unit/test_budget_gate_e042.py` — default env:
  **7 passed, 2 skipped** (the two sqlite_vec-guarded shapes,
  reasons stated). Extras shape: **9 passed, 0 skipped**.
- Slice gate Run B (default env, pgvector file excluded):
  **936 passed, 6 failed, 20 skipped, 1 warning** — 929
  E-041 baseline + 7 new (2 of the 9 skip bare, as designed);
  the 6 failures are the proven environment failures.
  Run D (whole, extras): **988 passed, 0 failed, 19 skipped,
  1 warning**, exit 0 — 979 baseline + all 9 new.

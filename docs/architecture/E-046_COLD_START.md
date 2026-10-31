# E-046 — Cold start on the smallest profile

*Part III, slice E-046. Roadmap line: "Cold start on the
smallest profile: time-to-first-word measured + capped." The
cap lives in the budget book (`ember.budgets`); the gate
lives in `tests/unit/test_cold_start_e046.py`.*

## In plain words

**From pressing Enter to Ember's first word takes about
three seconds on this machine — and almost all of that is
the program starting, not the answer being written.** Seven
times, a completely fresh copy of the companion was started
on the smallest ("toaster") settings and timed until the
first word of its reply reached the screen: the middle time
was **2.87 seconds** (fastest 1.28, slowest 5.38 — this
machine was busy with other work all morning, and the
spread is that busyness showing). Of those seconds, all
but about a tenth were spent before Ember even said it was
ready: starting Python, loading the program, checking the
model connection, opening its memory. Once ready, the first
word followed almost immediately.

That middle time is now the book's anchor, and the book
caps cold start at **5.0 seconds on every profile** — about
1.7 times the measured middle, enough headroom for a busy
machine, not enough for a real slowdown to hide in. A test
in the ordinary suite now starts the companion three fresh
times on every future run of the campaign's gate and fails
if the middle time crosses the cap.

One honesty note, stated before the numbers: the "model"
in these runs is a loopback wire-shape server that answers
instantly (the E-029/E-032 pattern — no real model program
exists on this machine). So the measurement prices **Ember's
own starting**, which is the part Ember controls. A real
model's own loading and thinking time is a separate cost,
and a cold start with a real model is **NOT PROVEN** here —
the device proofs at E-047–E-049 own it.

## 1. The measurement (VM profile, 2026-10-31)

Method: a parent process spawns each run as
`python -m ember --config-root <root> ask "hello"` — the
real CLI reading a real config file (`ember.toml`:
conversation profile `toaster`, streaming on, tools off,
`retry_backoff_max_s` 0) with a pre-written identity, a real
`sqlite_vec` Well, and the loopback wire-shape model
(`/api/version`, `/api/embed`, `/api/chat` NDJSON, first
streamed chunk the distinctive word `coldstart`). The
parent reads the child's stdout through a `select` loop
and timestamps two arrivals: the "…is ready." line (session
open: Funi probed, Well opened, history loaded) and the
first word. The clock starts just before spawn. One setup
run first created the Well (a first-ever start); the seven
judged runs are cold *processes* against that existing
state — the returning user's morning start, which is the
start a cap can fairly govern. Scripts and the raw record
live in `~/workspace/.verify-tmp/ember-e046/`
(`measure2.py`, `cold_start_runs.json`).

| Run | Ready (s) | First word (s) | Whole ask (s) |
|---|---|---|---|
| 1 | 2.79 | 2.87 | 3.16 |
| 2 | 1.34 | 1.43 | 2.00 |
| 3 | 3.22 | 3.30 | 3.83 |
| 4 | 1.19 | 1.28 | 1.92 |
| 5 | 1.88 | 1.97 | 2.48 |
| 6 | 3.08 | 3.11 | 3.71 |
| 7 | 5.29 | 5.38 | 5.86 |
| **median** | **2.79** | **2.87** | — |

The first-ever start (Well creation included) measured
3.60 s to first word, whole ask 4.02 s — inside the cap
too, though the cap is stated for the returning start.

**Contention, stated plainly.** This VM was running
several sibling campaigns throughout (1-minute load
~2.5, 5-minute ~8 at measurement time; free memory low).
Wall-clock is the first casualty of contention, so 2.87 s
is a *contended* median — a ceiling-friendly anchor, not a
best case. E-032's clean-venv second-run ask on a quieter
machine took 0.93 s *in total*, so on an unbusy machine the
first word lands well inside a second. The cap is set from
the contended anchor anyway: a promise kept on a busy
machine is worth more than one kept only in silence.

**Where the time goes.** Ready → first word is ~0.09 s at
the median: retrieval (embed + search over an empty Well),
prompt assembly, the model request, and rendering together
cost a tenth of a second once the process is up. The other
~97% is process startup — interpreter, the CLI/chat import
surface, config load, the Funi open probe, the Well open,
history load. Any future cold-start regression will
therefore be a startup regression, and the gate will see
it; any future optimisation belongs in startup, not in the
turn. (No optimisation is attempted in this slice: 2.87 s
contended against a 5.0 s cap needs none, and inventing
work the numbers do not ask for is not the campaign's way.)

## 2. The cap, in the book

`ember.budgets` gains:

- `MEASURED_COLD_START_FIRST_WORD_S = 2.87` — the anchor
  above, pinned by test so it cannot be quietly edited to
  fit a slower future.
- `ProfileBudget.cold_start_first_word_s = 5.0` — **flat
  across all four profiles**, deliberately: the RAM and
  size ceilings grow with the profile because they price
  allowances, but starting is the same process on every
  profile, and no machine size is granted a slower start
  by allowance. The toaster — the smallest, the roadmap's
  subject — carries the same 5.0 s promise as the laptop.
- `check_against(..., cold_start_first_word_s=...)` — the
  optional fifth judgement, in the book's own sentence
  shape ("cold start to first word … exceeds the toaster
  ceiling of 5.00 s"). Optional so every existing caller
  (E-041/E-042) judges exactly what it judged before;
  `measured_shape_fits` now includes the anchor, so the
  book's founding fact — the measured core fits every
  profile — covers cold start too.

## 3. The gate

`tests/unit/test_cold_start_e046.py` — **4 tests**:

- The book: the cap is flat at 5.0 s, holds the 2.87 s
  anchor with 1.5–2× headroom, and the anchor is pinned.
- `check_against` names a broken cold-start ceiling in
  plain words, and stays silent for the anchor and for an
  unmeasured shape.
- Wiring: the file lives under `tests/unit/`, where Runs
  B/D collect it (E-042's pattern).
- The measurement itself: a setup run (first-ever start,
  asserted end-to-end), then **3 fresh cold processes** on
  the toaster profile; every run must exit 0, show ready
  before its first word, and the **median** first-word
  time must sit inside the cap. The median, not any single
  run, is judged — one contention spike cannot flake the
  gate, while a real startup regression moves all three
  runs and is caught. In the bare environment (no
  `sqlite_vec`) the measurement test **skips with its
  reason stated** and the three bookkeeping tests pass.

## 4. Docket

No new docket items. Docket 90 (VM anchors) stands and now
covers this anchor explicitly: the per-device re-anchoring
at E-047 (Pi), E-048 (phone-class), and E-049 (the Toaster
Test) must re-derive this cap on real hardware, not merely
relax it. The only `src/` change is the budget book itself.

**One defect found by this slice's gate — in a gate, fixed
in scope.** The first whole-suite Run D failed E-045's
idle tests (3 of 4 profiles): not on CPU, threads, disk, or
growth, but on RSS *"wander"* — the settled samples
*declined* 4.4–9.7 MiB inside the 15-second window and the
max−min assertion called any movement a violation. But
decline is E-045's own proven idle behaviour (its hour
fell monotonically 40.8 → 23.0 MiB as the kernel reclaimed
untouched pages); under this morning's memory pressure the
same decline simply happened faster, inside the gate
window. The assertion contradicted the evidence it was
written to protect. Fixed in
`tests/unit/test_idle_discipline_e045.py`: the settled
assertion now judges **growth past the first settled
sample** (the leak shape) at the same 2 MiB bound, with
the reason recorded at the assertion. Standalone re-run
with the cold-start tests: **9 passed**; the final Run D
below is green with the fix in the tree.

## 5. Honest limits

- **Wire-shape model.** The model answered instantly over
  loopback; its loading and generation time are excluded
  by construction and named, never folded in. A real-model
  cold start is NOT PROVEN.
- **Contended VM numbers.** Median 2.87 s, spread
  1.28–5.38 s, on a busy shared VM — see §1. The cap
  inherits the contention; a quiet device should beat the
  anchor, and E-047–E-049 will say by how much.
- **Returning start, not install day.** The judged runs
  start against an existing Well and identity; the
  first-ever start was measured separately (3.60 s) and
  also fits, but the wizard's interactive first run is a
  person's pace, not a machine's, and is not capped here.
- **Toaster profile, VM host.** The toaster *profile*
  (512-token history) ran on the VM; the toaster *device*
  verdict remains E-049's.

## Tests

- `tests/unit/test_cold_start_e046.py` — default env:
  **3 passed, 1 skipped** (the measurement, sqlite_vec
  reason stated). Extras shape: **4 passed**.
- E-041's book tests re-run beside it: default
  14 passed / 1 skipped across both files; extras
  15 passed / 0 skipped.
- Slice gate (final tree, E-045 gate fix included; logs in
  `~/workspace/.verify-tmp/ember-e046/gate/`): Run B
  **952 passed, 6 failed, 25 skipped, 1 warning** — the 6
  are the proven environment failures (CDE ×3, G ×2, J ×1);
  949 E-045 baseline + 3 new passed, +1 new skip as
  designed. Run D **1009 passed, 0 failed, 19 skipped,
  1 warning**, exit 0 — 1005 baseline + all 4 new. (The
  first Run D attempt, before the §4 gate fix, read
  1006 passed / 3 failed — the 3 being exactly the E-045
  wander failures the fix addresses.)

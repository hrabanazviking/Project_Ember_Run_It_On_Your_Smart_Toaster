# E-056 — Regression armour: budget tests join the permanent gate

*Part III, slice E-056. Roadmap line: "Regression armour:
budget tests join the permanent gate." The gate is
`scripts/dev/run_budget_gate.py`; its keeper tests are
`tests/unit/test_budget_armour_e056.py`.*

## In plain words

**Ember's budget tests now have one front door.**
Part III built the armour piece by piece: fifteen test
files, one per slice E-041–E-055, each guarding its own
measurement — the ceilings themselves, install weight,
dependencies, the idle hour, cold start, the three device
proofs, storage, thermal patience, update weight,
battery duty, graceful shedding, and the published book.

Until now those tests ran only inside this campaign's
whole-suite slice gates. That is a campaign habit, not a
project gate: when the campaign ends, a habit ends with
it. This slice gives the project a permanent command:

```
python3 scripts/dev/run_budget_gate.py
```

Run from anywhere, it runs exactly the fifteen budget
files and exits with pytest's own exit code — 0 only when
every budget test passes or skips honestly. `--list`
names the enrolled files; `--collect-only` checks the
wiring without running; anything after `--` passes to
pytest unchanged.

## 1. What existed before (audited this slice)

- Fifteen budget test files under `tests/unit/`, one per
  slice E-041–E-055 (file list in the gate's manifest;
  122 tests pass in the bare default env, 129 with the
  optional extras — see §3).
- Their only gate was collection by the whole root suite
  (the E-017 method's Runs B/D) — proven per slice by a
  wiring test in most files, but with no single place
  enrolling them all, and no check that a budget file
  exists which is enrolled *nowhere*.
- `scripts/dev/` was a scaffold (its README names
  developer-convenience scripts as its purpose, none
  landed) — the natural home for a gate command, under
  the scripts rules (a `--help`, a top-of-file docstring,
  safe to run repeatedly). No README was touched.

## 2. The gate's shape

`scripts/dev/run_budget_gate.py`:

- `BUDGET_TEST_FILES` — the manifest, fifteen paths in
  roadmap order (E-041 → E-055). This tuple is the single
  enrolment list: the gate command is built from it, and
  `--list` prints it.
- The command is `sys.executable -m pytest <manifest> -q`,
  run at the repo root with `src/` leading `PYTHONPATH`
  (the suite's own convention), the rest of the
  environment inherited untouched. Exit code propagates
  unchanged. The script writes nothing of its own.
- Deliberately NOT enrolled: this slice's own keeper
  tests. They re-measure nothing; enrolling the keeper in
  the gate it keeps would be circular. They run in the
  whole suite, where they judge the manifest.

## 3. The keeper tests (7, all passing)

`tests/unit/test_budget_armour_e056.py` holds the gate
honest from both sides:

- the script exists and enrols exactly 15 files, no
  duplicates;
- every enrolled file exists, lives under `tests/unit/`
  (so the whole-suite gates collect it too — the armour
  now stands in **both** gates), and holds ≥1 test;
- **completeness:** every `tests/unit/` file carrying a
  Part III slice suffix (`_e041`–`_e055`) is enrolled,
  ordered by slice number — a future budget file that is
  never enrolled fails here instead of gating nothing;
- the built command is exactly the manifest plus `-q`;
- `--list` prints exactly the manifest;
- `--collect-only` through the real script collects
  every enrolled file (pytest's own collection output
  names each — wiring proven, not inferred from paths).

The completeness test proved it bites during this slice:
its first draft sorted discovery alphabetically and
failed against the roadmap-ordered manifest — a real
manifest/discovery mismatch, caught and corrected in
the test (discovery now sorts by slice number).

## 4. Gate results for this slice

- Keeper tests standalone (default env): **7 passed**.
- The permanent gate, default env:
  **122 passed, 7 skipped**, exit 0 — the 7 skips are the
  honest `sqlite_vec`-absent guards (E-042 ×2 well/storage
  shapes, E-045 ×4, E-046 ×1), identical in kind to the
  whole suite's default shape.
- The permanent gate, extras supplied (`sqlite_vec` /
  `psycopg` / `pgvector` from the campaign's isolated
  extras dir): **129 passed, 0 skipped**, exit 0 —
  122 + 7 reconciles exactly: every default-env skip is
  an extras shape that runs and passes there.
- Slice gate Run B and Run D: recorded in
  `CAMPAIGN_STATE.md` with this slice's banking entry
  (logs in `~/workspace/.verify-tmp/ember-e056/gate/`).

## 5. Honest limits

- The gate runs the budget tests as they are — including
  their own honest skips in a bare env. A green default
  run proves the bare shapes; the extras shapes are
  proven by the extras run above and by Run D.
- This is the *budget* gate, not the whole regression
  gate: E-200 (Part XII) owns gathering **every** gate
  (budgets, suites, drills, stranger scripts) into one
  command. E-056's command is the budget row of that
  future table, shaped so E-200 can call it as-is.
- Wall time is machine weather (default run 35.7 s,
  extras run 125.2 s on the contended campaign VM) and
  is claimed as nothing.

No ceiling moved, no anchor changed, no `src/` code
touched, no README touched, no new docket items.
E-057 next — the member budget table.

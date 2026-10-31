# E-004 — Fresh Baseline I: the root `tests/` run whole

*Project Ember campaign, Part I (The Monorepo's True State).
Measured 2026-10-30 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), at campaign
commit 28e6835 (E-003 banked). This slice runs the root test
suite whole, takes every count from the runner, and classifies
every failure as **REAL** (a defect in code or test), **ENVIRONMENT**
(the machine lacks what the test honestly needs), or **STALE**
(the test no longer matches the code it judges). It fixes
nothing: Part I prepares verdicts, and E-016 is the docket
where every defect found here is numbered and assigned.
E-017 freezes this baseline as the campaign's zero line.*

## Environment (the machine these counts belong to)

- VM profile (this campaign's VM), Python 3.12.3, pytest 9.1.1.
- The environment is stdlib-only by default: no optional extras
  from `pyproject.toml` are installed into it — with one
  exception: PyYAML 6.0.1 is present system-wide, so the
  `config` extra is effectively satisfied.
- Absent in the default environment: `sqlite_vec` (sqlite_vec
  extra), `psycopg` / `pgvector` (pgvector extra), `mcp`
  (mcp extra), any reachable Ollama, podman.
- Extras proof run: `sqlite-vec`, `psycopg[binary]` and
  `pgvector` were installed into an isolated target directory
  outside the repo (`~/workspace/.verify-tmp/ember-extras`) and
  put on `PYTHONPATH` — nothing was installed into the
  environment itself and nothing in the tree changed. The
  `mcp` extra was *not* supplied in any run of this slice.

## The four runs (every count from the runner)

| Run | Shape | Result |
|---|---|---|
| A | Whole suite, default env: `PYTHONPATH=src python3 -m pytest tests -q` | **Interrupted at collection: 1 error, 8 skipped, 0 tests run** (exit 2, 4.30s) |
| B | Same, pgvector file excluded (`--ignore=tests/integration/test_pgvector_real_backend.py`) | **546 passed, 6 failed, 12 skipped, 1 warning** (24.41s) |
| C | The six failing files + pgvector schema/secrets files + the pgvector real-backend file, extras supplied | **69 passed, 15 skipped, 0 failed** (2.80s) |
| D | Whole suite, extras supplied | **583 passed, 0 failed, 19 skipped, 1 warning** (25.18s, exit 0) |

Run B reproduces the E-001 opening baseline exactly
(546 / 6 / 12) — the suite has not moved since the campaign
opened. Run D is the headline truth: **with the optional
extras present, the whole root suite is green — 583 passed,
0 failed.** There is no hidden logic failure anywhere in the
root suite today.

The suite's shape: 61 test files — 50 under `tests/unit/`,
11 under `tests/integration/`; `tests/e2e/`, `tests/fixtures/`
and `tests/snapshots/` hold only their README files, no tests.
`tests/conftest.py` puts `src/` on `sys.path`, so the runner
needs no install step.

## Failure classification

### The collection error (Run A) — REAL test defect, environment-triggered

`tests/integration/test_pgvector_real_backend.py` interrupts
collection of the *whole* suite in the default environment:
`import psycopg` at module top level (line 35) raises
`ModuleNotFoundError` before the module's own guards can run —
the `pytest.importorskip("psycopg")` / `importorskip("pgvector")`
calls sit at lines 51–52, *below* the import they were meant to
guard. The guard exists; it is simply unreachable in exactly
the environment it was written for. Its sibling files guard
correctly (module-level `importorskip` before any adapter
import). Consequence in the default environment: the root
suite cannot run whole at all — 0 tests execute. Classification:
REAL (guard placement defect in the test file), triggered by
ENVIRONMENT (pgvector extra absent). With the extra supplied
(Runs C/D) the file collects, and all its tests skip honestly:
10 require podman (not installed), 4 require the live Gungnir
endpoint (not reachable from this VM). Carried to E-016.

### The 6 failures (Run B) — all ENVIRONMENT, one shared coupling

Every one of the 6 fails with the same root error:
`ModuleNotFoundError: No module named 'sqlite_vec'`, raised at
`src/ember/well/brunnr/sqlite_vec/adapter.py` line 27, where
the adapter imports its optional dependency at module top
level. (The pgvector adapter, by contrast, imports its extras
lazily and says so in its own docstring.) Two couplings follow:

- **Batch CDE ×3** (`test_fts5_sanitiser_*` in
  `tests/unit/test_hardening_batch_cde.py`): these test a *pure
  string function*, `_escape_fts5_query`, but importing it
  drags in the whole adapter and therefore `sqlite_vec`. The
  tests carry no `importorskip` guard of their own (a sibling
  test in the same file, line 319, does guard). ENVIRONMENT
  trigger; the coupling is the defect. Carried to E-016.
- **Batch G ×2** (`test_pgvector_text_search_*` in
  `tests/unit/test_hardening_batch_g.py`): the pgvector
  adapter's `text_search` imports the sanitiser *from the
  sqlite_vec adapter* (pgvector `adapter.py` line 588), so a
  pgvector test with a stubbed connection still dies on the
  missing sqlite_vec extra. Same classification: ENVIRONMENT
  trigger, cross-adapter coupling. Carried to E-016.
- **Batch J ×1** (`test_sqlite_vec_connection_works_across_threads`
  in `tests/unit/test_hardening_batch_j.py`): this one
  genuinely needs the real backend, but has no `importorskip`
  guard, so in the default environment it *fails* where its
  siblings *skip*. ENVIRONMENT trigger + missing-guard defect.
  Carried to E-016.

Run C proves the classification: with the extras supplied, all
6 tests pass, in files totalling 69 passed / 15 skipped /
0 failed. No test logic was stale and no product code
misbehaved: in the default environment these are
environment failures wearing the shape of test failures.

### STALE — none

No failure in any run is stale: nothing asserts behaviour the
code no longer has. Every failure is accounted for above, and
Run D's clean whole-suite pass leaves no room for an
unexplained stale row.

### The 1 warning — test hygiene, docketed

Both full runs emit exactly one warning:
`tests/unit/test_mcp_runner.py::test_runner_submit_after_close_raises`
raises `RuntimeWarning: coroutine ... was never awaited`. The
test passes and the product behaviour it checks (submit after
close raises `RuntimeError: closed`) is correct; the test
creates a coroutine object that the raising path never awaits
or closes, and the object leaks the warning. Classification:
REAL, minor, in the test only. Carried to E-016.

### The skips — honest guards, in both configurations

Default environment (Run B, 12 skipped): 7 × `sqlite_vec`
extra missing, 3 × MCP extra missing, 2 × Ollama not reachable
at localhost:11434. Extras environment (Run D, 19 skipped):
3 × MCP extra missing (never supplied in this slice), 2 ×
Ollama not reachable, 10 × podman not installed (the pgvector
container acceptance flow — a container tool this campaign's
no-Docker law never substitutes for, and podman itself is not
present), 4 × the live Gungnir endpoint not reachable from
this VM. Every skip names its missing condition in the
runner's own output; no skip hides a failure. The MCP-guarded,
Ollama-guarded, podman-guarded and Gungnir-guarded tests are
NOT PROVEN by this slice in either configuration — they are
recorded as guarded, not as passed.

## Verdict for E-017 / E-016

- Baseline truth, default env: the suite cannot run whole
  (1 collection error); excluding one mis-guarded file it is
  546 passed / 6 failed / 12 skipped, and all 6 failures are
  environment.
- Baseline truth, extras env: whole suite green —
  583 passed / 0 failed / 19 skipped.
- Defects carried to the E-016 docket (numbered there):
  (1) pgvector real-backend module's unreachable import guard;
  (2) sqlite_vec adapter's top-level optional import coupling
  pure helpers (and, via the pgvector adapter's sanitiser
  import, a second adapter) to the extra; (3) unguarded
  sqlite_vec-dependent tests failing instead of skipping
  (Batch CDE ×3, Batch J ×1); (4) the un-awaited-coroutine
  warning in the MCP runner test.
- No code was changed in this slice, no README was touched,
  nothing was pushed.

# E-017 — Baseline Freeze: the campaign's zero line

*Project Ember campaign, Part I (The Monorepo's True State).
Frozen 2026-10-31 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), measured at
campaign commit 37fc2f2 (E-016 push-verification record banked).
This slice pins the suite + boot results from E-004, E-005 and
E-006 as the campaign's zero line, re-measures the root suite
in full this slice, and records the exact method so any keeper
tick can re-measure against the same line. It fixes nothing:
every defect named here already carries a number in the E-016
docket (items 1–80).*

## The zero line, in plain words

On this machine, today: **with its optional extras present, the
whole root test suite passes — 583 passed, 0 failed.** In the
bare default shape (nothing extra installed) the suite cannot
even run whole, because one test file guards its optional
import in the wrong place; leaving that one file out, the bare
shape is 546 passed, 6 failed — and all 6 failures are the same
missing optional extra, proven, not real breakage. The
companion's command line starts, the seiðr engine starts and
composes, Verdandi's nerve hub has been proven live, and the
companion's own `doctor` command crashes bare for the same
missing-extra reason (docket 13). That is the ground every
later part is measured against. Nothing below this line is a
claim about any other machine.

## Environment the zero line belongs to

- VM profile (this campaign's VM). Python 3.12.3,
  pytest 9.1.1, Node v24.22.1.
- Tree at freeze: HEAD `37fc2f2746e6a0e79e9a87f99a58a178b60fa3db`,
  base branch `development` at f26312a, 3,246 tracked files
  (`git ls-files | wc -l`).
- Default shape: stdlib-only environment — no optional extras
  from the root `pyproject.toml` installed (PyYAML 6.0.1 happens
  to be present system-wide; see E-004).
- Extras shape: `sqlite-vec` 0.1.9, `psycopg[binary]` 3.3.6 and
  `pgvector` 0.5.1 supplied from the isolated target directory
  `~/workspace/.verify-tmp/ember-extras` on `PYTHONPATH`.
  Nothing is installed into the environment itself; the `mcp`
  extra is supplied in NO shape of this freeze.
- `TMPDIR` is set to a workspace-overlay directory
  (`~/workspace/.verify-tmp/ember-e017/tmp`) because the VM's
  512 MB `/tmp` tmpfs is a proven source of false failures
  (E-012/E-013; docket 54's mechanism).

## Frozen root suite (re-measured in this slice, 2026-10-31)

Raw logs: `~/workspace/.verify-tmp/ember-e017/runA.log`,
`runB.log`, `runD.log`.

| Run | Shape | Frozen result | Re-measured 2026-10-31 |
|---|---|---|---|
| A | Whole suite, default env: `PYTHONPATH=src python3 -m pytest tests -q` | Interrupted at collection: **1 error, 8 skipped, 0 run**, exit 2 (E-004) | **Identical** — 1 error, 8 skipped, exit 2; the error is `tests/integration/test_pgvector_real_backend.py:35` importing `psycopg` above its own guards (docket 1) |
| B | Default env, pgvector file excluded (`--ignore=tests/integration/test_pgvector_real_backend.py`) | **546 passed, 6 failed, 12 skipped, 1 warning** (E-001 opening baseline, reproduced E-002–E-016) | **Identical** — 546 passed, 6 failed, 12 skipped, 1 warning (20.71s). The 6 failures are docket 2/3's `sqlite_vec` coupling (CDE ×3, G ×2, J ×1) |
| D | Whole suite, extras supplied (`PYTHONPATH=<ember-extras>:src`) | **583 passed, 0 failed, 19 skipped, 1 warning**, exit 0 (E-004) | **Identical counts** — 583 passed, 19 skipped, 1 warning, exit 0 (40.63s; wall time varies with machine load and is NOT part of the freeze — counts are) |

The 1 warning in every full run is the un-awaited-coroutine
test-hygiene warning in the MCP runner test (docket 4). The
skips are honest guards in both shapes (sqlite_vec / MCP /
Ollama / podman / Gungnir — E-004's breakdown stands); the
MCP-, Ollama-, podman- and Gungnir-guarded tests are
**NOT PROVEN** by this freeze — guarded, not passed.

## Frozen per-member truth table (pinned from E-005, as corrected by E-012)

These counts are pinned as measured in their own slices; this
freeze does not re-run the member suites (the root suite above
is the slice gate every later slice re-runs — see Method).
"With-deps" means the member's declared dependencies supplied
from an isolated target directory, per E-005's method.

| Member | Frozen result | Notes |
|---|---|---|
| seidr_engine | **38 passed, 0 failed** | The one fully green member, default env |
| kista | **146 passed, 3 failed** | The 3 failures are docket 5 (tests judge a `~/.hermes` copy); re-proven identical in E-011 |
| Verdandi | **539 passed, 19 failed** (default env) | 6 ENVIRONMENT (pytest-asyncio absent) + 13 REAL (docket 6/7/31 family); a full with-plugin count was NOT claimed in E-005 and is not claimed here |
| mimir-well | **350 passed, 6 failed** (flask supplied) | The 6 are docket 10 (Eye fixture / machine-coupled paths); re-proven identical in E-012 |
| bifrost | **18 passed, 7 failed** (`PYTHONPATH=src`) | Cannot collect uninstalled (no `pythonpath` in its config, docket 11 family); the 7 are ENVIRONMENT-triggered, unguarded |
| Hamr | **2170 passed, 28 failed, 33 skipped, 2 errors** (`PYTHONPATH=src` + pydantic) | 18F+2E ENVIRONMENT (Blender absent), 7 machine-shape, 3 STALE (E-005 breakdown; docket 38–45 family) |
| mempalace | **1712 passed, 14 failed, 1 skipped, 106 deselected, 0 errors** (E-012 corrected, file-verified; a second clean run scored 1713/13/0) | E-005's first figure (1597/90/39 errors) is superseded: its bulk was environment-shaped (`/tmp` pressure + proxy env). The residue is docket 12's STALE plugin-hook family ×10 + palace_locks ×4. This member's counts are volatile under machine pressure — docket 54's harness discipline governs any re-measurement |
| CloakBrowser (vendored) | **385 passed, 39 failed, 15 errors** (httpx + playwright package supplied) | Vendored record only — stewardship, never judged as ours (docket 80); failures are proxy-env + unprovisioned browser binary (E-005/E-006) |
| cleasby-vigfusson-old-norse-dict | **NOT MEASURED** | Jest suite never run — `node_modules/` absent (docket 78, an open measurement, not a pass or a fail) |
| astrology-engine | **NO SUITE EXISTS** | Docket 77 |
| Open-VTT | **NO SUITE EXISTS** | Docket 77 |

## Frozen boot zero line (pinned from E-006; key rows re-probed this slice)

Raw re-probes: `~/workspace/.verify-tmp/ember-e017/boot-reprobe.log`.

- **BOOTS**: ember CLI (`--help` exit 0 — re-probed identical
  this slice; `mcp list` exit 0), Verdandi nerve-hub CLI,
  Verdandi heartbeat CLI, kista credstore CLI (real HOME),
  mempalace CLI 3.3.5, mimir-well core library, bifrost library,
  Hamr CLI 0.8.0 (with deps), CloakBrowser CLI (browser binary
  itself NOT PROVEN — never downloaded).
- **LIVE proven** (E-006): Verdandi nerve hub `serve` (socket up,
  healthcheck ALL CHECKS PASSED, publish accepted, clean
  terminate) and Mímir's Eye (HTTP 200, flask supplied).
- **BOOTS + COMPUTES**: seidr_engine — `fornyrthislag --seed 1`
  composes, exit 0, bare default env (re-probed identical this
  slice).
- **CRASHES**: ember `doctor` / `well status` in the default env
  on `ModuleNotFoundError: sqlite_vec` (docket 13; `doctor`
  re-probed this slice — same traceback, adapter line 27);
  kista credstore under a foreign HOME (docket 14).
- **CANNOT BOOT / COMPUTE HERE, named**: astrology-engine
  (deps absent and undeclared; real commands exit 0 computing
  nothing — docket 16/18), dictionary (`next` not found —
  `node_modules/` absent), Open-VTT (no Godot binary on the VM
  — NOT PROVEN, Part X).

## Method — how a keeper re-measures against this freeze

1. Work only in `~/workspace/ember-build/` on branch
   `yrsa/ember-road-build`. Record `git rev-parse HEAD` before
   and after; a re-measurement at a different HEAD is a new
   measurement, not a contradiction of this freeze.
2. Set `TMPDIR` to a workspace-overlay directory (never the
   512 MB `/tmp` tmpfs) for every run.
3. Run B (the slice gate — every slice): `PYTHONPATH=src
   python3 -m pytest tests -q
   --ignore=tests/integration/test_pgvector_real_backend.py`.
   Expected at the zero line: **546 passed, 6 failed,
   12 skipped, 1 warning**. Any deviation is news: a count
   *worse* than the freeze is a regression to fix in scope or
   docket; a count *better* means a docket item (1–4) was fixed
   and the freeze row must be updated by the slice that fixed it.
4. Run A and Run D are re-measured at part gates and whenever a
   slice touches the Well adapters, the pgvector test module,
   or test guards (docket 1–4): Run A whole-suite default
   (expected: collection interrupted, 1 error, 8 skipped);
   Run D whole-suite with `~/workspace/.verify-tmp/ember-extras`
   first on `PYTHONPATH` (expected: **583 passed, 0 failed,
   19 skipped, 1 warning**, exit 0). If the extras directory is
   absent, rebuild it exactly as E-004 did — install
   `sqlite-vec`, `psycopg[binary]`, `pgvector` into an isolated
   target directory outside the repo; never install into the
   environment.
5. Boot re-probes are cheap and safe with sandboxed HOME /
   redirected state (E-006's method): ember `--help`, seidr
   `fornyrthislag --seed 1`, and `doctor` in the default env
   (expected crash until docket 13 is fixed — when it stops
   crashing, that is the fix's proof, recorded by its slice).
6. Member suites are re-measured only by the slices that own
   them (E-005's per-member shapes), never as a casual gate —
   several are minutes-long and timing- or pressure-sensitive
   (Verdandi, Hamr, mempalace; docket 54).
7. Counts come from the runner's own summary line, read from
   the run's log file — never from memory, never rounded.

## What this freeze is not

- Not a claim about any other machine, profile, or hardware —
  every number names this VM (Part III owns real small-machine
  proof, E-047–E-049).
- Not a fix list: all 80 docket entries in E-016 stand exactly
  as assigned; this freeze is the ruler they are measured with.
- No code was changed in this slice, no README was touched.

## Carried forward

- Next: E-018 — Part I gate: audit published in-repo, verdicts
  prepared (not executed) for every member, plain-language
  summary, the road re-cut if facts demand.

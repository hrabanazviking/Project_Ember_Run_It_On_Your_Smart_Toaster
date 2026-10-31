# E-005 — Fresh Baseline II: each member's own tests, run in its own shape

*Project Ember campaign, Part I (The Monorepo's True State).
Measured 2026-10-30 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), at campaign
commit 6cbf093 (E-004 banked). The root `tests/` suite is
E-004's province and is not re-judged here (the slice gate
below re-runs it unchanged). This slice runs every member's
own test suite the way that member's own configuration
declares it — from the member's directory, under its own
`pyproject.toml` pytest options or its own JS test runner —
takes every count from the runner, and classifies every
failure as **REAL** (a defect in code or test), **ENVIRONMENT**
(the machine lacks what the test honestly needs), or **STALE**
(the test no longer matches the tree it judges). It fixes
nothing: E-016 is the docket where every defect found here
is numbered and assigned.*

## Environment and method

- VM profile (this campaign's VM), Python 3.12.3, pytest 9.1.1,
  Node v24.22.1. Default environment is the same stdlib-only
  shape as E-004 (PyYAML and `cryptography` happen to be
  present system-wide; `chromadb`, `flask`, `pytest-asyncio`,
  `pydantic`, `playwright`, `httpx` are not).
- With-deps shape (the E-004 method): the member's *declared*
  dependencies were installed into an isolated target directory
  outside the repo (`~/workspace/.verify-tmp/ember-e005-extras`)
  and put on `PYTHONPATH` — nothing was installed into the
  environment itself and nothing in the tree changed.
  Src-layout members whose own pytest config carries no
  `pythonpath` (bifrost, Hamr — mimir-well's config does) were
  additionally given `PYTHONPATH=src`, the in-tree equivalent
  of the installed shape their packaging declares.
- One environment fact dominates this slice: the VM's proxy
  environment (`*_proxy` / `no_proxy`, set by the sandbox)
  contains bracketed IPv6 entries, and `httpx` — used by
  chromadb's local client and by CloakBrowser — parses one of
  those entries as a port and dies with
  `httpx.InvalidURL: Invalid port: ':1]'`. Every failure
  carrying that signature is ENVIRONMENT, and the verdict is
  *proven*, not inferred: re-running mempalace's
  `test_searcher.py` + `test_closets.py` with a cleaned
  `no_proxy` turns 30 non-passes (13 errors, 14 failed,
  3 errors) into **85 passed, 0 failed**.

## The per-member truth table

| Member | Test files | Own shape | Default-env result | With-deps result | Verdict |
|---|---|---|---|---|---|
| seidr_engine | 1 | pytest, `testpaths=["tests"]` | **38 passed** (0.27s) | — (no deps needed) | GREEN |
| kista | 1 | pytest, `testpaths=["tests"]` | **146 passed, 3 failed** (2.89s) | — (`cryptography` already present) | 3 REAL |
| bifrost | 2 | pytest, `testpaths=["tests"]`, src layout | **Collection interrupted: 2 errors, 0 run** — `No module named 'bifrost'` | `PYTHONPATH=src`: **18 passed, 7 failed** | 7 ENVIRONMENT-triggered, unguarded |
| Verdandi | 10 | pytest, `asyncio_mode="auto"` | **539 passed, 19 failed** (109s) | subset re-run with `pytest-asyncio` exceeded a 600s budget (timing-heavy integration tests); not fully re-proven | 6 ENVIRONMENT + 13 REAL |
| mimir-well | 28 | pytest, `testpaths=["tests"]`, `pythonpath=["src"]` | **336 passed, 2 failed, 18 errors** — all 20 in the eye-app file, all `No module named 'flask'` | flask supplied: **350 passed, 6 failed** | 6 REAL |
| Hamr | 46 | pytest, `testpaths=["tests"]`, src layout | **Collection interrupted at conftest: 0 run** — `No module named 'hamr'` | `PYTHONPATH=src` + pydantic: **2170 passed, 28 failed, 33 skipped, 2 errors** (262s) | 18F+2E ENVIRONMENT, 7 machine-shape, 3 STALE |
| mempalace | 76 | pytest, `testpaths=["tests"]`, `pythonpath=["."]` | **Collection blocked at conftest: 0 run** — `tests/conftest.py:30` imports `chromadb` unguarded | chromadb supplied: **1597 passed, 90 failed, 1 skipped, 106 deselected, 39 errors** (220s) | bulk ENVIRONMENT (proven), 10 STALE, small residue |
| CloakBrowser (vendored) | 30 py | pytest, `testpaths=["tests"]` | **Collection interrupted: 10 errors, 1 skipped, 0 run** — `No module named 'httpx'` | httpx + playwright package: **385 passed, 39 failed, 1 skipped, 15 errors** (96s) | ENVIRONMENT (proxy env + browser binary not provisioned); see notes |
| cleasby-vigfusson-old-norse-dict | 67 (Jest) | Jest via `jest.config.js` | **NOT RUN** — `node_modules/` absent; the dependency tree (a full Next.js install) was not installed for an audit slice | — | NOT MEASURED |
| astrology-engine | 0 | — | **NO SUITE EXISTS** | — | NO TESTS |
| Open-VTT | 0 | — | **NO SUITE EXISTS** (the one `*_test.gd` file is a drag-and-drop debug component, not a test; no Godot binary on the VM either) | — | NO TESTS |

## Member notes (evidence behind the table)

### seidr_engine — the one fully green member
38 passed in 0.27s in the default environment, no notes.
The smallest member is the healthiest.

### kista — 3 REAL, one cause
All 3 failures in `tests/test_credstore.py` share one line:
`CREDSTORE_SCRIPT = Path.home() / ".hermes" / "skills" /
"devops" / "runa-credentials" / "scripts" / "credstore.py"`
(test line 32). The tests judge a copy of the script on the
author's Hermes machine that does not exist here; the
in-tree script at `kista/scripts/credstore.py` is never
touched by them. REAL test defect (machine-coupled path),
docketed for E-016.

### bifrost — its own shape assumes an installed package
bifrost is src-layout and, unlike mimir-well, its pytest
config sets no `pythonpath`, so in an uninstalled tree its
suite cannot collect at all. With `src` on the path:
18 passed, 7 failed — 6 are inline `from muninn import
HebbianMemory` inside test bodies (`muninn` is bifrost's
declared *optional* extra: absent here, and the tests fail
instead of skipping — the same unguarded pattern E-004
docketed in the root suite), and the 7th
(`test_health_check`) asserts the muninn backend reports
"healthy" while muninn is not installed; it reports
"not_configured", which is the code behaving correctly.
All 7 are ENVIRONMENT-triggered; the unguarded-import half
is a REAL test-hygiene defect, docketed.

### Verdandi — 19 failures in four families
- **6 ENVIRONMENT**: `test_nervous_system.py`'s async tests
  fail because `pytest-asyncio` — Verdandi's declared dev
  extra, required by its own `asyncio_mode="auto"` — is
  absent in the default environment. (With the plugin
  supplied, a three-file subset exceeded a 600s budget:
  these integration tests run on real heartbeat timing.
  The default-env classification stands on pytest's own
  missing-plugin failure text; a full with-plugin count is
  NOT claimed.)
- **7 REAL — one code defect**: every FullPulseCycle,
  GracefulDegradation and StatePersistence failure in
  `test_heartbeat_integration.py` dies at the same line,
  `heartbeat/actions/vor_action.py:69` —
  `AttributeError: 'str' object has no attribute 'get'`.
  The pulse cycle is broken in code, not in the tests.
- **5 REAL — machine-coupled tests**: the CLI integration
  tests spawn subprocesses with
  `cwd=str(Path.home() / "Verdandi")` — the author's home
  layout, absent here. Same family as kista's defect.
- **1 REAL**: `load_profiles_from_yaml(Path("/nonexistent/
  path"))` raises `IsADirectoryError` instead of returning
  the defaults its test (and name) promise.

### mimir-well — green core, one broken fixture
Default env: every non-pass (2 failed + 18 errors) is the
eye-app test file dying on `flask`, mimir-well's sole
declared dependency — ENVIRONMENT. With flask supplied the
whole suite runs: **350 passed, 6 failed**, and all 6 are
in that same file with a REAL cause: the fixture sets the
environment variable `DB_PATH` and builds a temp database,
but `src/mimir_well/eye/app.py` reads `MIMIR_DB_PATH`
(line 28) into Flask config at import and never looks at
`DB_PATH`. The app therefore points at its defaults —
paths under `~/.hermes/` — whose parent directory does not
exist here, and `query_db` dies with
`sqlite3.OperationalError: unable to open database file`;
health/stats/search fail downstream of the same mismatch.
On the author's machine the default DB existed, so the
fixture's mistake was invisible. REAL (fixture/app env-name
mismatch), docketed.

### Hamr — the biggest suite in the monorepo
2,231 tests collected in its own shape. Its conftest
imports the `hamr` package, so like bifrost the suite
cannot collect uninstalled (its config also sets no
`pythonpath`). With `src` on the path and pydantic
supplied: **2170 passed, 33 skipped** — and the 28 failed
+ 2 errors break down as:
- **18 failed + 2 errors ENVIRONMENT**: every phase5/phase8
  Blender test — the `blender` binary is not installed on
  this VM (`FileNotFoundError: 'blender'`, addon checks
  reporting `blender_available: False`).
- **7 machine-shape**: CLI/dry-run tests dying on
  `FileNotFoundError: 'python'` (×4 — this VM has only
  `python3`) and on the hardcoded path `/home/pi/Hamr`
  (×3 — the author's Pi). The Pi paths are REAL
  machine-coupled test defects; the `python` name is
  environment shape.
- **3 STALE**: `test_release_promotion.py` requires
  `.github/workflows/ci.yml` *inside* the Hamr directory —
  the standalone repo's layout. The monorepo import carries
  no `.github` under Hamr, so the test judges a tree that
  no longer exists.

### mempalace — a heavyweight with an environment shadow
Its conftest hard-imports `chromadb` (line 30) — chromadb
is mempalace's declared *core* dependency, so this is a
shape fact, not a guard defect: without its declared deps
the suite cannot collect, full stop. With chromadb
supplied: **1597 passed, 106 deselected** (its own config
deselects the benchmark files), and 90 failed + 39 errors,
of which:
- **The bulk is ENVIRONMENT, proven**: failure section
  after failure section carries the `Invalid port: ':1]'`
  proxy signature (92 sections sampled by script, spanning
  the MCP server, searcher, closets, repair, miner,
  exporter, sweeper and hybrid-search files). With a
  cleaned `no_proxy`, the sampled searcher+closets files
  pass 85/85 (see Method).
- **10 STALE**: `test_claude_plugin_hook_wrappers.py`
  executes hook scripts under `.claude-plugin/hooks/` —
  the `.claude-plugin/` directory does not exist anywhere
  in the tree the import delivered (`returncode 127`,
  "No such file or directory").
- **A small residue** (lock-acquisition timeout in
  `test_palace_path_is_normalized`, `assert False is True`
  in the MCP diary/write-tool tests) is recorded as
  UNRESOLVED rather than guessed at; none of it was
  root-caused in this slice, and E-016 carries it as such.

### CloakBrowser — vendored, reported and never judged as ours
Vendored third-party code (Part XI's stewardship): its
numbers are recorded, its code is not ours to fix and was
not touched. Default env cannot collect (its declared
`httpx` absent). With httpx only: 364 passed, 60 failed,
15 errors. With the playwright package also supplied:
**385 passed, 39 failed, 1 skipped, 15 errors**. The
remaining non-passes are environment-shaped: the same
proxy `InvalidURL` signature (launch tests and the stealth
setup errors — with a cleaned `no_proxy`, test_launch
improves to 2 passed / 6 failed, the 6 needing the actual
browser binary, which is not provisioned on this VM —
no Playwright/Chromium download was performed),
DNS-dependent SSRF tests in `test_lambda_security.py`, a
timing assertion in `test_geoip.py`
(`assert 0.805… < 0.5`), and the humanize unit group,
whose failures were not individually root-caused.
Its JS side (`js/tests/`) was NOT RUN: `node_modules/`
is absent. The vendored `bin/docker-entrypoint.sh` was,
per campaign law, never used.

### The dictionary — not measured, honestly
67 Jest test files exist, but running them needs the
project's full Node dependency tree installed
(`node_modules/` absent, `yarn.lock` present). Installing
a Next.js tree to satisfy an audit slice is out of
proportion to E-004's small-extras precedent, so the row
stands at NOT RUN — dependency tree not installed. A later
part that works on the dictionary itself should install
and measure it then.

## Cross-member findings (the slice's real harvest)

1. **A machine-coupling family runs through the imported
   members' tests**: kista judges a script under
   `~/.hermes/`, Verdandi's CLI tests cd to `~/Verdandi`,
   mimir-well's eye defaults live under `~/.hermes/`, Hamr
   tests name `/home/pi/Hamr`. These suites were green on
   the machines that wrote them and cannot be green
   anywhere else. Four members, one disease.
2. **Two src-layout members cannot collect uninstalled**
   (bifrost, Hamr) because their pytest configs omit the
   `pythonpath` their sibling mimir-well remembered to set.
3. **Unguarded optional imports recur** (bifrost's muninn,
   exactly the root suite's E-004 finding): tests fail
   instead of skipping when an optional backend is absent.
4. **Only seidr_engine is green as shipped**; the two
   members with no tests at all (astrology-engine,
   Open-VTT) now stand next to it in the table, which is
   its own verdict for Parts VII and X.

## Carried to the E-016 docket

From this slice (continuing E-004's numbering):
(5) kista tests hardcode the `~/.hermes` credstore path;
(6) bifrost tests import optional `muninn` unguarded, and
bifrost's pytest config lacks `pythonpath`;
(7) Verdandi `vor_action.py:69` AttributeError breaks the
pulse cycle; (8) Verdandi CLI tests hardcode `~/Verdandi`;
(9) Verdandi's YAML profile loader raises on a missing
path instead of returning defaults; (10) mimir-well eye
fixture/app env-name mismatch (`DB_PATH` vs
`MIMIR_DB_PATH`) with `~/.hermes` defaults beneath it;
(11) Hamr tests hardcode `/home/pi/Hamr` and the `python`
binary name, Hamr's pytest config lacks `pythonpath`,
and its release-promotion tests judge the standalone
repo's layout; (12) mempalace's `.claude-plugin/` hook
files are absent from the tree its tests judge, plus the
small unresolved residue named above. The dictionary's
unmeasured Jest suite is carried as an open measurement,
not a defect.

## Slice gate

Root suite re-run in the E-001 shape (pgvector file
excluded, default env) as this slice's no-change gate —
see CAMPAIGN_STATE.md for the count. Doc-only slice: no
code touched, no README touched, no push. The extras live
outside the repo in `~/workspace/.verify-tmp/` and are not
part of the tree.

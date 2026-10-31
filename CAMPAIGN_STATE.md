# Project Ember — Campaign State

Roadmap: `docs/EMBER_ROADMAP_2026-10-30.md` (204 slices, E-001–E-204, 12 parts)
Repo: hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster
Base branch: development @ f26312a54af94439cf480c58a0eb4d78b54e6024
Campaign branch: yrsa/ember-road-build
Working tree: ~/workspace/ember-build/ (this campaign's own clone — never shared)

Last updated: 2026-10-30 23:49 EDT
Status: STOPPED between slices (no slice IN PROGRESS)
Banked: E-001, E-002, E-003, E-004, E-005, E-006, E-007, E-008
Next slice: E-009 — The Verdandi concordance

## Laws (from the roadmap §3, binding every slice)

- Keeper discipline; never leave a discovered bug unfixed (in scope, or docketed to its part in E-016).
- No Docker ever. Never touch any README.md.
- Banking is local per slice; pushes await Volmarr's word — sole exception was the E-001 roadmap filing.
- Vendored code (CloakBrowser) keeps its licences, never rewritten.
- Counts from the runner only; hardware claims name the device; never invent counts.
- Tiny-hardware budgets are the project's soul.

## E-001 — Campaign opening (DONE, 2026-10-30)

- Cloned development (single-branch) into ~/workspace/ember-build: 3,229 files, 214 MB working tree (102 MB .git).
- Created branch `yrsa/ember-road-build` from development f26312a.
- Roadmap filed at `docs/EMBER_ROADMAP_2026-10-30.md`, byte-identical to the commissioned copy
  (sha256 922f7da0ff3931f3976732b35e053ae3f1e85c2b0a89a83404a627409ff009d3), commit ed8a69c.
- Filing push verified via ls-remote: refs/heads/yrsa/ember-road-build = ed8a69c8f30e5fa16fc3f1952ba4f13d43341004;
  development unchanged at f26312a. No other pushes made.
- This state file created.

## Fresh baseline (opening, 2026-10-30 — feeds E-004/E-017, preliminary)

Runner: `PYTHONPATH=src python3 -m pytest tests -q` (Python 3.12.3, pytest 9.1.1, VM profile; stdlib-only env, no optional extras installed).

- Whole-suite collection is interrupted by 1 error: `tests/integration/test_pgvector_real_backend.py`
  imports `psycopg` at module top level unguarded → ModuleNotFoundError when the pgvector extra is absent.
- Excluding that file: **546 passed, 6 failed, 12 skipped** (22.59s).
- All 6 failures trace to missing optional extras, proven: the FTS5-sanitiser tests (batch CDE ×3),
  pgvector text-search tests (batch G ×2) and the sqlite_vec cross-thread test (batch J) all fail with
  `ModuleNotFoundError: No module named 'sqlite_vec'` (adapter modules import optional deps at top level).
  With `sqlite-vec` + `psycopg[binary]` supplied on PYTHONPATH from an isolated target dir, those same
  files run **31 passed, 2 skipped** — so the 6 failures + 1 collection error are ENVIRONMENT, not code failures.
- Skips are honest guards: sqlite_vec missing (×6 files), MCP extra missing (×3), Ollama unreachable (×2).
- Docket candidates for E-016 (assigned to Part I / E-004): (a) pgvector integration test module should
  skip-guard its psycopg import like its sibling files do; (b) pure-function tests (FTS5 sanitiser,
  pgvector text search) are coupled to optional-dep adapter imports and fail instead of skipping when
  extras are absent. Neither is fixed in E-001 (opening slice); both are recorded here, not lost.

## Opening census snapshot (preliminary — E-002/E-003 will prove it in depth)

Top-level members present (size / file count, working tree excl. .git):
- src/ember core: 732K / 104 files (cli, config, mcp, schemas, spark, thread, tools, well)
- Verdandi: 17M / 179 — kista: 2.7M / 25 — mempalace: 57M / 257 — mimir-well: 716K / 58
- seidr_engine: 128K / 11 — astrology-engine: 7.2M / 25 — bifrost: 92K / 10
- Hamr: 6.2M / 168 — Open-VTT: 7.0M / 209 — CloakBrowser (vendored): 6.4M / 112
- cleasby-vigfusson-old-norse-dict: 24M / 170 — deploy: 36K / 6 — assets: 3.3M / 12
- Root tests/: 61 test files. Member test files: mempalace 76, dictionary 67, Hamr 46,
  CloakBrowser 30, mimir-well 28, Verdandi 10, bifrost 2, kista 1, seidr_engine 1, astrology-engine 0, Open-VTT 0.
- Licences present at root and in every member checked (LICENSE in kista, mempalace, mimir-well,
  seidr_engine, astrology-engine, bifrost, Hamr, Open-VTT, CloakBrowser, dictionary, Verdandi).
- ORIGINS.md present at root (scribe Eirwyn Rúnblóm, updated 2026-05-21) — honoured as provenance register.
- Root pyproject: ember-agent 0.2.0, MIT, requires-python >=3.11, zero core dependencies (stdlib only);
  optional extras: sqlite_vec, config (pyyaml), pgvector, mcp; dev: pytest, pytest-cov, ruff, mypy.
- The five elder codices are all present at root: TASK_CHATDOLL_CODEX.md, TASK_HERMES_CODEX.md,
  TASK_RAGNAROK_CODEX.md, TASK_SUPER_AGENT_PARTY_CODEX.md, TASK_WAIFU_CODEX.md.
- Note: many member dirs carry large numbers of loose image files at their roots (Verdandi, Hamr,
  astrology-engine) — census detail for E-002/E-014, not a verdict.

## E-002 — Member census (DONE, 2026-10-30)

- Census filed at `docs/audit/E-002_MEMBER_CENSUS.md`: all 21 top-level directories
  + root loose files (45 files, ~36 MB), each with purpose, byte-sum size, file count,
  main code language, entry points, strict test-file count, and last-evidence-of-life
  from `git log` (method stated in the doc; strict test counts reproduce the E-001
  snapshot exactly for every member it listed).
- Headline evidence: every roadmap §2 member is PRESENT; 11 members (Verdandi, kista,
  mempalace, mimir-well, seidr_engine, astrology-engine, bifrost, Hamr, Open-VTT,
  CloakBrowser, dictionary) have exactly ONE commit — their 2026-05-21 import — while
  src/ + tests/ show real development (28/27 commits through Batch K). Weight is data
  and images, not code (mempalace 59.0 MB incl. ~38.5 MB benchmark .jsonl; dictionary
  24.2 MB incl. 18.6 MB Jest snapshot; Verdandi 16.8 MB incl. ~15.2 MB loose images).
  Test presence uneven: astrology-engine and Open-VTT have ZERO test files; kista and
  seidr_engine one each. Scaffolding dirs (scripts/tools/examples/deploy/vendor) are
  near-empty Markdown-only shells — concordance items for E-003/E-014. Root images
  have recurred since ORIGINS §2's move to assets/ (19 IMG_*.jpeg + 3 large PNGs).
- Slice gate: root suite re-run in the E-001 shape (pgvector file excluded):
  **546 passed, 6 failed, 12 skipped** — identical to the opening baseline; the 6
  failures are the proven environment failures. Doc-only slice, no code touched,
  no README touched, no push.

## E-003 — ORIGINS concordance (DONE, 2026-10-30)

- Concordance filed at `docs/audit/E-003_ORIGINS_CONCORDANCE.md`: every ORIGINS
  claim checked against the tree (paths + byte sizes; root images sha256-compared
  against `assets/`; git log used only for successor lineage).
- Headline: the register is accurate about everything it covers — §1: 24 of 25
  rows at their recorded places (MYTHIC_ENGINEERING.md and README grown as their
  own notes foresaw; the config stub absent under its claimed name
  `config/runa.example.yaml` with proven fork successor `config/ember.example.yaml`);
  §2: all 11 images present in `assets/`, §5b holds (the merge-restored copies are
  not at root); §7: every listed item present (12 docs, 7 ADRs, 11 subtrees,
  5 operator docs).
- The blind spot: **none of the eleven imported member directories has an
  ORIGINS row** (Verdandi, kista, mempalace, mimir-well, seidr_engine,
  astrology-engine, bifrost, Hamr, Open-VTT, CloakBrowser, dictionary), and
  neither do the five elder codices or other root loose files. New root image
  population (19 IMG_0861–0879 + 3 PNGs) is sha256-proven NOT duplicates of
  `assets/` — new unregistered material. Grown-beyond, unlisted: ADR 0014,
  `src/ember/mcp/`, `config/sources.example.yaml`; ADR 0012 absent from the
  sequence, unexplained in the register. `src/runa/` moved/replaced by the
  fork (skeleton archived at `docs/archive/runa-inherited/src-skeleton/`).
  The §6-planned drift detector `tools/repo/check_origins_drift.py` was never
  built (tools/repo holds only its README). THIRD_PARTY_NOTICES.md still names
  "Runa Agent"/"HERETIC" — stale skeleton. All small items carried to E-016;
  the register gap itself is an E-196 act (ORIGINS was not modified).
- Slice gate: root suite re-run in the E-001 shape (pgvector file excluded):
  **546 passed, 6 failed, 12 skipped** — identical to the opening baseline;
  the 6 failures are the proven environment failures. Doc-only slice, no code
  touched, no README touched, no push.

## E-004 — Fresh baseline I (DONE, 2026-10-30)

- Baseline filed at `docs/audit/E-004_FRESH_BASELINE_I.md`: the root `tests/`
  suite run whole in four runner shapes (VM, Python 3.12.3, pytest 9.1.1),
  every failure classified REAL / ENVIRONMENT / STALE.
- Headline: **with the optional extras supplied from an isolated target dir,
  the whole suite is green — 583 passed, 0 failed, 19 skipped, 1 warning**
  (25.18s). In the default stdlib-only env the whole run is interrupted at
  collection (1 error, 8 skipped, 0 run): `test_pgvector_real_backend.py`
  imports `psycopg` at line 35, *above* its own importorskip guards at
  lines 51–52 — a REAL guard-placement defect, environment-triggered.
- Excluding that file, the default-env run reproduces the E-001 baseline
  exactly: **546 passed, 6 failed, 12 skipped**. All 6 failures are
  ENVIRONMENT: Batch CDE ×3 + Batch J ×1 need `sqlite_vec`; Batch G ×2 die
  through the pgvector adapter's sanitiser import from the sqlite_vec
  adapter (`adapter.py:588`), whose top-level `import sqlite_vec` (line 27)
  couples even pure helpers to the extra. With extras, the affected files
  run 69 passed / 15 skipped / 0 failed. STALE failures: none.
- The 1 warning (both full runs): the MCP runner submit-after-close test
  leaks an un-awaited coroutine — test hygiene only, product behaviour
  correct. Skips are honest guards in both configs (sqlite_vec / MCP /
  Ollama / podman / Gungnir); MCP extra was never supplied in this slice,
  so MCP-guarded tests remain guarded, not proven.
- Four defects carried to the E-016 docket: (1) pgvector module's
  unreachable import guard; (2) sqlite_vec adapter top-level optional
  import coupling; (3) unguarded tests failing instead of skipping
  (CDE ×3, J ×1); (4) the un-awaited-coroutine warning. Doc-only slice,
  no code touched, no README touched, no push.

## E-005 — Fresh baseline II (DONE, 2026-10-30)

- Truth table filed at `docs/audit/E-005_FRESH_BASELINE_II.md`: every member's
  own suite run in its own shape (default env + with-declared-deps shape, deps
  supplied from an isolated target dir outside the repo, E-004 method).
- Headline counts (with-deps shape where deps were needed): seidr_engine
  **38 passed** (the one fully green member); kista 146 passed / 3 failed;
  Verdandi 539 passed / 19 failed; mimir-well 350 passed / 6 failed; bifrost
  18 passed / 7 failed (cannot collect uninstalled); Hamr 2170 passed /
  28 failed / 33 skipped / 2 errors (cannot collect uninstalled); mempalace
  1597 passed / 90 failed / 39 errors / 106 deselected; CloakBrowser
  (vendored) 385 passed / 39 failed / 15 errors. Dictionary Jest suite NOT RUN
  (node_modules absent); astrology-engine and Open-VTT have NO test suites.
- Dominant cause class is ENVIRONMENT, *proven*: the VM's proxy env
  (bracketed IPv6 in `no_proxy`) makes httpx die with `Invalid port: ':1]'`
  inside chromadb/CloakBrowser clients — with a cleaned `no_proxy`,
  mempalace's searcher+closets files pass 85/85. Blender absent accounts
  for Hamr's 18F+2E; flask/pytest-asyncio/sqlite-style declared deps absent
  in the default env account for the rest of the environment class.
- REAL defects found (all carried to the E-016 docket as items 5–12 in the
  E-005 doc): a machine-coupling family — kista tests judge a `~/.hermes`
  copy of credstore (3 tests), Verdandi CLI tests cd to `~/Verdandi` (5),
  mimir-well eye fixture sets `DB_PATH` while the app reads `MIMIR_DB_PATH`
  over `~/.hermes` defaults (6), Hamr tests name `/home/pi/Hamr` (3 of its 7
  machine-shape failures); Verdandi `vor_action.py:69` AttributeError breaks
  the pulse cycle (7 tests); Verdandi YAML loader raises IsADirectoryError
  instead of defaults (1); bifrost tests import optional muninn unguarded (6)
  and bifrost/Hamr pytest configs lack `pythonpath` (suites cannot collect
  uninstalled, unlike mimir-well); Hamr release-promotion tests judge the
  standalone repo's `.github` layout (STALE, 3); mempalace hook tests judge
  a `.claude-plugin/` directory absent from the tree (STALE, 10) plus a small
  UNRESOLVED residue (lock timeout, MCP diary/write asserts), recorded as such.
- Slice gate: root suite re-run in the E-001 shape (pgvector file excluded):
  **546 passed, 6 failed, 12 skipped** — identical to the opening baseline.
  Doc-only slice, no code touched, no README touched, no push.

## E-006 — Boot census (DONE, 2026-10-30)

- Census filed at `docs/audit/E-006_BOOT_CENSUS.md`: every E-002 entry point
  actually started on the VM profile (sandboxed HOME + redirected state;
  raw probe outputs kept in `~/workspace/.verify-tmp/ember-e006/`).
- LIVE proven: Verdandi's nerve hub (`serve` → socket up, status Running ✅,
  healthcheck ALL CHECKS PASSED, publish accepted event #2, `recent` shows it,
  clean terminate) and Mímir's Eye (HTTP 200 dashboard with flask supplied).
  seidr_engine is the only member that boots AND computes in the bare default
  env (`fornyrthislag --seed 1` composes, exit 0). BOOTS: ember CLI help /
  `mcp list`, Verdandi heartbeat CLI, kista (real HOME), mempalace CLI
  (3.3.5) + MCP server (with deps), mimir-well core library, bifrost library
  (instantiates; no CLI by design), Hamr CLI (0.8.0; check-env honestly
  reports Blender absent), CloakBrowser CLI (`info`: binary NOT installed,
  install deliberately not run).
- CRASHES: ember `doctor` / `well status` in the stdlib-only env traceback on
  `ModuleNotFoundError: sqlite_vec` — the default Well backend needs an
  optional extra, so first-run diagnostics cannot start bare (with extras:
  both boot; doctor honestly reports Funi UNAVAILABLE / Well ok, exit 1).
  New docket items 13–17 for E-016: (13) that crash (boot face of item 2);
  (14) kista credstore's import-time `pip install cryptography` fallback dies
  with CalledProcessError on PEP 668 where the dep is absent; (15) Hjarta
  wizard `EOFError` traceback on closed stdin (`ask` fresh-root probe);
  (16) astrology-engine's real commands exit 0 printing "pyswisseph required",
  computing nothing, its deps declared nowhere; (17) mimir-well
  `start-eye.sh` hardcodes `/home/pi` (module path works).
- CANNOT BOOT HERE, named: astrology-engine (deps absent + undeclared),
  dictionary (`npm run start` exit 127, `next` not found — node_modules
  absent), Open-VTT (no Godot binary on the VM; project + main scene present
  and correctly referenced — NOT PROVEN, Part X).
- Slice gate: root suite re-run in the E-001 shape (pgvector file excluded):
  **546 passed, 6 failed, 12 skipped** — identical to the opening baseline.
  Doc-only slice, no code touched, no README touched, no push.

## E-007 — Dependency & licence audit (DONE, 2026-10-30)

- Audit filed at `docs/audit/E-007_DEPENDENCY_LICENCE_AUDIT.md`: every licence
  file in the tree read + sha256-recorded (filename scan incl. `*notice*` /
  `*copying*` / `*copyright*`), every packaging file parsed, and each member's
  actual third-party imports AST-scanned against its declarations (raw
  inventories in `~/workspace/.verify-tmp/ember-e007/`).
- Headline: the licence estate is permissive and intact — 11 MIT licence files
  verified complete (grant + warranty clause; Hamr's carries a poetic coda that
  removes nothing), astrology-engine full Apache-2.0, NO copyleft licence file
  anywhere (GPL/AGPL appear only as do-not-vendor discussion in the codices).
  Upstream-copyright members keep their licences: dictionary (MIT, © Sampo
  Silvennoinen; underlying 1874 text public domain) and Open-VTT (MIT, © Khazlor).
- The one trap: CloakBrowser is TWO licences — wrapper MIT intact (© CloakHQ),
  but its compiled Chromium binary is PROPRIETARY under `BINARY-LICENSE.md`:
  use + dependency-listing are free, redistribution/bundling into a distributed
  product is prohibited without an OEM/SaaS licence. Not a violation (binary
  absent from the tree, never downloaded — E-006) — a release-shape constraint
  for Part XI (docket 25).
- Dependency reality vs declarations: astrology-engine has NO packaging file
  and declares none of its 5 guarded imports (pyswisseph, kerykeion, geopy,
  timezonefinder, pytz); Verdandi's `eir/layers.py` imports yaml top-level
  unguarded with pyyaml declared nowhere in the member; the core's optional
  `keyring` (ADR 0010, lazy + graceful) is declared in no extra; Hamr lazily
  imports undeclared psutil (guarded) + tomli in a test fallback. Licence
  metadata gaps: kista pyproject, dictionary + mempalace-website package.json
  declare no license field. Only mempalace is locked (uv.lock, 122 packages,
  hashed) and bounded; everything else is unbounded `>=` with no Python
  lockfile. Root THIRD_PARTY_NOTICES still names Runa Agent/HERETIC and holds
  ZERO entries. New docket items 18–25 for E-016.
- Slice gate: root suite re-run in the E-001 shape (pgvector file excluded):
  **546 passed, 6 failed, 12 skipped** — identical to the opening baseline.
  Doc-only slice, no code touched, no README touched, no push.

## E-008 — The codex census (DONE, 2026-10-30)

- Census filed at `docs/audit/E-008_CODEX_CENSUS.md`: the five elder
  TASK_*_CODEX commissions read in full; each promised corpus counted in
  the tree file-by-file, by layer, with word counts (raw inventory in
  `~/workspace/.verify-tmp/ember-e008/`); closing artefacts checked.
- Headline: **four codices are DONE-in-fact** — Hermes 50 content + 8 meta
  = 58 total (140,519 content words), Chatdoll 63 + 6 = 69 (exactly as
  promised; 224,436 words), SAP 77 + 6 = 83 (content exact vs its
  MANIFEST; 201,292 words), Waifu 15 + 6 = 21 (exactly as promised;
  47,277 words). Every content doc in all four carries its promised
  `## What This Means for Ember` closer; none falls under its word floor
  (35 run over their ceilings — over-length, not absence); each corpus is
  closed by its Scribe meta pass (INDEX / READING_ORDER /
  CROSS_AGENT_NOTES present) and its named synthesis prizes exist
  (Hermes 65/66, Chatdoll triangulation 60, SAP 67/68/69, Waifu 60/61).
- **Ragnarok is PARTIAL — scaffold only, content ABSENT:** 3 of 6 meta
  files, 0 of 46 promised content docs, no INDEX; its only commit is the
  2026-05-25 scaffold (a6cbd81) — no authoring wave ever followed. E-165
  must reconcile an unexecuted commission; authoring/retiring it is
  Volmarr's word.
- Cross-cutting: all five TASK status lines are stale ("Authoring /
  pending dispatch" over four completed corpora); sibling citations mix
  content/total counts and two match neither (SAP cited "84", Waifu
  "22"); no codex corpus is referenced anywhere in `src/` — proposals
  have no in-code consumer yet (Part X's gap). New docket items 26–30
  for E-016.
- Slice gate: root suite re-run in the E-001 shape (pgvector file excluded):
  **546 passed, 6 failed, 12 skipped** — identical to the opening baseline.
  Doc-only slice, no code touched, no README touched, no push.

## Slice ledger

- E-001 DONE (2026-10-30) — opening: clone, branch, roadmap filed + filing push verified, state file, opening baseline.
- E-002 DONE (2026-10-30) — member census in depth, filed at docs/audit/E-002_MEMBER_CENSUS.md.
- E-003 DONE (2026-10-30) — ORIGINS concordance, filed at docs/audit/E-003_ORIGINS_CONCORDANCE.md.
- E-004 DONE (2026-10-30) — fresh baseline I: whole root suite classified; with extras 583 passed / 0 failed, filed at docs/audit/E-004_FRESH_BASELINE_I.md.
- E-005 DONE (2026-10-30) — fresh baseline II: per-member truth table; seidr green, bulk of failures proven environment (proxy-env httpx signature), 8 new docket items (machine-coupled tests family), filed at docs/audit/E-005_FRESH_BASELINE_II.md.
- E-006 DONE (2026-10-30) — boot census: Verdandi hub + Mímir's Eye proven LIVE, seidr boots+computes bare, ember diagnostics crash bare on the sqlite_vec default backend, astrology/dictionary/Open-VTT cannot boot here for named reasons, 5 new docket items (13–17), filed at docs/audit/E-006_BOOT_CENSUS.md.
- E-007 DONE (2026-10-30) — dependency & licence audit: estate permissive + intact (11 MIT verified, astrology Apache-2.0, no copyleft in tree), CloakBrowser binary licence is proprietary (no redistribution/bundling without OEM — constraint, not violation), 4 declaration-vs-reality gaps + metadata/lockfile gaps, 8 new docket items (18–25), filed at docs/audit/E-007_DEPENDENCY_LICENCE_AUDIT.md.
- E-008 DONE (2026-10-30) — the codex census: four elder codices DONE-in-fact (Hermes 58 total, Chatdoll 69, SAP 83, Waifu 21 — every content doc present with its Ember closer, none under its word floor), Ragnarok scaffold-only with 0/46 content docs, all five TASK status lines stale, no codex referenced in src/, 5 new docket items (26–30), filed at docs/audit/E-008_CODEX_CENSUS.md.
- E-009 next — The Verdandi concordance.

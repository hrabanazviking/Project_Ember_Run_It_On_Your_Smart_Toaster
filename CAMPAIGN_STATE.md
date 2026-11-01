# Project Ember — Campaign State

Roadmap: `docs/EMBER_ROADMAP_2026-10-30.md` (204 slices, E-001–E-204, 12 parts)
Repo: hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster
Base branch: development @ f26312a54af94439cf480c58a0eb4d78b54e6024
Campaign branch: yrsa/ember-road-build
Working tree: ~/workspace/ember-build/ (this campaign's own clone — never shared)

Last updated: 2026-11-01 03:14 EST
Status: STOPPED — E-082 banked this tick (memory lifecycle live on the face; E-083 next)
Banked: E-001, E-002, E-003, E-004, E-005, E-006, E-007, E-008, E-009, E-010, E-011, E-012, E-013, E-014, E-015, E-016, E-017, E-018, E-019, E-020, E-021, E-022, E-023, E-024, E-025, E-026, E-027, E-028, E-029, E-030, E-031, E-032, E-033, E-034, E-035, E-036, E-037, E-038, E-039, E-040, E-041, E-042, E-043, E-044, E-045, E-046, E-047, E-048, E-049, E-050, E-051, E-052, E-053, E-054, E-055, E-056, E-057, E-058, E-059, E-060, E-061, E-062, E-063, E-064, E-065, E-066, E-067, E-068, E-069, E-070, E-071, E-072, E-073, E-074, E-075, E-076, E-077, E-078, E-079, E-080, E-081, E-082
Next slice: E-083 — persona separation enforced at the memory face (E-025's fixtures at this layer)

## Laws (from the roadmap §3, binding every slice)

- Keeper discipline; never leave a discovered bug unfixed (in scope, or docketed to its part in E-016).
- No Docker ever. Never touch any README.md.
- Banking is local per slice; from E-013 onward, banked slices are pushed to origin
  `yrsa/ember-road-build` under Volmarr's standing go-ahead (2026-10-31): git fetch +
  remote-diff first, never force-push, verified via ls-remote. (Earlier slices were
  local-only under the prior wording; their banking records stand as written.)
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

## E-009 — The Verdandi concordance (DONE, 2026-10-30)

- Concordance filed at `docs/audit/E-009_VERDANDI_CONCORDANCE.md`: Verdandi's
  own roadmap (`Verdandi/docs/roadmap.md`, VD-RM) checked claim by claim
  against the code, config, and tests.
- Headline: **v0.3.0 "Skuld" is real** — SkuldCheck, Vör, emotional
  classifier, maintenance windows, the exactly-8-metric Prometheus exporter,
  and the `pulse_metrics` table all stand in code, and `tests/test_skuld.py`
  re-ran **35 passed** this slice. But Vör is BROKEN in three places (not
  one): it crashes on Skuld's own `{"status": …}` capacity shape in both
  `should_trigger` and `_get_capacity_summary` (Skuld's own consumer guards
  `isinstance`, Vör doesn't — all reproduced this slice), its returns use
  `ActionResult(name=…, ActionSeverity.INFO)` (wrong field, nonexistent
  severity), and it overrides `execute()` instead of `_execute()`, bypassing
  BaseAction's crash wrapper — no test covers Vör. And `pulse_metrics` is
  WRITE-ONLY: created, indexed, inserted every pulse, pruned at 10,000 —
  never SELECTed anywhere; Skuld predicts from state-derived scores in
  `pulse_history` instead.
- **v0.4.0 "Valhalla" is absent or double-counted:** distributed heartbeat
  and the REST API have NO code (API exists only as a docs wrapper pattern
  with different paths); Prometheus and the emotional architecture are
  listed as v0.4 plans after already shipping in v0.3. Emotional count
  matches nothing (VD-RM says 7, its table lists 6, the dict holds 6,
  `classify()` can return 8). VD-RM covers the heartbeat only — nerve hub,
  context injector, conversation logger, top-level reactor, the Eir
  package (its own version 2.0.0), `runa_*`, and the 50-doc research corpus
  have no roadmap coverage. VD-RM's sketches diverge from the shipped API
  in names/thresholds/wiring (check `prediction` not `predictive:…`; slope
  −0.05 not −0.5; hard-coded Reactor rule, not the sketched YAML;
  maintenance static, not Urðr-integrated) — code is the authority for
  E-060's re-cut. New docket items 31–37 for E-016.
- Slice gate: root suite re-run in the E-001 shape (pgvector file excluded):
  **546 passed, 6 failed, 12 skipped** — identical to the opening baseline.
  Doc-only slice, no code touched, no README touched, no push.

## E-010 — The Hamr verification plan (DONE, 2026-10-31)

- Plan filed at `docs/audit/E-010_HAMR_VERIFICATION_PLAN.md`: every Hamr
  phase claim (Ph1–17) inventoried from its source doc, each with the
  artefact that would prove it, the method, the pass criterion, and the
  environment the proof needs; execution assigned to E-138 (Ph1–10),
  E-139 (Ph11–13), E-140 (Ph14–17 + cross-cutting). Binding method:
  runner counts only, symbol-level existence (a claim naming a symbol
  that does not exist is NOT PROVEN as written), artefact-at-path,
  environment is part of the claim.
- Headline: five phases carry COMPLETE docs (11, 12, 13, 15, 16), but
  Phases 1–5 survive only as CHANGELOG lines, **Phase 6 has no claim
  anywhere in the tree**, Phases 7–10 rest on test files + three
  "Phase 7: Complete" docstrings, and Phase 14 has NO complete
  artefact (plan's 7 tasks unchecked; CHANGELOG details only T6).
  Phase 17 is a vision, not a completion — its must-pass first E2E
  raising is unevidenced: **no `.vrm` file exists in the tree**
  (`build_output/test.vrm` is a directory holding a preset YAML) and
  Blender is absent on the VM (E-006). Three headline classes named
  in the COMPLETE docs — `MaterialForge`, `CollisionForge`,
  `PoseLibrary` — **appear nowhere in src/ or tests/** (real
  equivalents: AnimeMaterialGenerator, CollisionMeshGenerator,
  rigs/poses.py); the claimed `materials/forge.py`,
  `rigs/colliders.py`, `rigs/pose_library.py` and
  `tests/test_e2e_pipeline.py` likewise do not exist. Phase 15's
  promotion check "ci_configured — .github/workflows/ci.yml present"
  is false in this tree (no `.github` under Hamr/ at all; kin to
  E-005's STALE standalone-layout finding). The test-count spine
  (556 → 1159 → 1569 → ~1965/~2206 → 2206) contradicts itself
  (Ph15: ~1965 in its COMPLETE doc vs ~2206 in its CHANGELOG section;
  Ph12/Ph13 titled COMPLETE while admitting 4 and 7 failures) and
  E-005's measured 2170 passed / 28 failed. Version spine's final
  claim holds at file level: pyproject + `__init__` both say 0.8.0.
  AUDIT_17's FP-1/FP-2 fixes spot-checked at plan grade (line 852
  fixed shape; canonical MB_LAB_BONE_MAP at constants.py:238).
  New docket items 38–45 for E-016.
- Slice gate: root suite re-run in the E-001 shape (pgvector file excluded):
  **546 passed, 6 failed, 12 skipped** — identical to the opening baseline.
  Doc-only slice, no code touched, no README touched, no push.

## E-011 — The two-Kistas boundary doc (DONE, 2026-10-31)

- Boundary filed at `docs/audit/E-011_TWO_KISTAS_BOUNDARY.md`: the two
  Kistas separated plainly — codebases, purposes, custody rules (§5,
  8 binding rules) — so no future worker conflates them. Toaster side
  proven from this tree; ai-folder side stated from the roadmap §2 +
  recorded purplelongship evidence (2026-10-30/31), graded RECORDED
  not MEASURED (that side was not accessed this slice; no credential
  value or account address reproduced anywhere in the doc).
- Headline: **toaster-Kista** is `kista/` here — one import commit
  (4f81633, 2026-05-21), v2.0.0, one-file credstore (2,382 lines),
  Fernet whole-vault `vault.json.enc` + plaintext `vault_meta.json`,
  14 entry types in code, ~25 subcommands, **zero consumers in root
  `src/`** (UNWIRED: wired = no). **Ai-folder Kista** is the living
  line on purplelongship, kept current with standalone GitHub
  `runafreyjasdottir/kista` (head recorded 54e31f1090, 2026-06-07),
  Runa/Hermes custody, the one Heimdall uses; Volmarr stored +
  verified his Second Life credentials in it 2026-10-30. Volmarr's
  boundary ruling recorded verbatim in the doc. Shared name/spirit/
  lineage is fact; shared custody or sync is forbidden (roadmap §6).
- Six hazards found, all in-tree: H1 the toaster copy's default vault
  dir is the OTHER Kista's home (`~/.hermes/credentials`, same
  filenames) — the dangerous one, in code; H2 Verdandi's Mímir check
  expects a THIRD shape (`~/.kista/vault.db`, SQLite `entries`) that
  neither Kista writes; H3 the toaster tests judge the other
  installation (see below); H4 `kista/references/known-accounts.md`
  is the ai-side vault's operational status ledger sitting in the
  toaster tree (status only, no credentials — recorded, not removed);
  H5 the Yggdrasil design docs' aspirational fourth shape
  (`~/.ember/kista.vault`, `kista://` URIs, stale "8 entry types");
  H6 both sides answer to "v2.0" — cite Kista by which + where + when.
- Kista suite re-run this slice as boundary evidence: **146 passed,
  3 failed** — identical to E-005, and the 3 failures are H3 exactly
  (subprocess tests exec `~/.hermes/skills/devops/runa-credentials/
  scripts/credstore.py`, absent here, FileNotFoundError in raw output).
  New docket items 46–50 for E-016 (default-home collision → Part VI;
  Verdandi vault.db check → Part IV; known-accounts custody →
  Volmarr's word; SKILL.md Hermes framing/stale count → E-104;
  Hermes-shaped add-soul/add-cron-backup/github-backup → E-098).
- Slice gate: root suite re-run in the E-001 shape (pgvector file excluded):
  **546 passed, 6 failed, 12 skipped** — identical to the opening baseline.
  Doc-only slice, no code touched, no README touched, no push.


## E-012 — The two-memories census (DONE, 2026-10-31)

- Census filed at `docs/audit/E-012_TWO_MEMORIES_CENSUS.md`: mempalace vs
  mimir-well measured side by side — shape, storage, retrieval, overlap,
  uniqueness, consumers — as Part V's evidence (E-077 executes in depth).
- Headline: **overlap is shape, not code** — both store/search/graph/
  converse/repair/export, share zero code and zero storage format, and
  **neither is consumed by the Ember core** (zero imports in `src/`; the
  core's live memory is a THIRD system, its own Brunnr sqlite_vec/
  pgvector Well). mempalace (3.3.5, upstream MemPalace) is the verbatim
  archive: wings/rooms/closets/drawers, mining pipelines, hybrid
  vector+BM25 search, temporal KG, 30-tool MCP server, benchmark estate —
  at ChromaDB+ONNX weight (59.2 MB tree, package 25,318 lines).
  mimir-well (2.10.4, house line) is the living memory: one stdlib
  SQLite file (638 KB tree, 6,496 lines), importance/valence,
  Ebbinghaus decay, temporal validity + supersession, contradiction
  detection, source-trust guard, audit trail, token budgeting — and
  **no vector search anywhere** (FTS5 only).
- Consumers in-tree: mempalace NONE (its consumers are external —
  Claude Code hooks / MCP clients). mimir-well two shape-consumers:
  Verdandi's heartbeat check (path agrees with the library default
  `~/.mimir_well/mimir_well.db`) and bifrost's memory bridge (SQL
  against `memories`/`memories_fts` but at `~/.hermes/memory/
  runa_memory.db` — the Eye's default too; three default paths for
  "the Mímir DB", stores mutually invisible → docket 51).
  UNWIRED_INVENTORY's mempalace line ("likely abandoned or archival")
  is proven stale — wired=no stands, the characterisation does not
  (docket 52).
- Suites re-run this slice (E-005 method, deps isolated, proxy
  cleaned): mimir-well **350 passed, 6 failed** — identical to
  E-005; the 6 are docket item 10 (Eye fixture) re-proven, staying
  open as machine-coupled (docket 53). CORRECTION (same day): this
  section as first banked carried a wrong "356 passed, 0 failed"
  mimir figure; no run produced it — corrected in the E-012 doc
  and here by the correction commit. mempalace **1712 passed, 14 failed,
  1 skipped, 106 deselected, 0 errors** (file-verified from the run's
  own log; a second clean run scored 1713/13/0 — residue = item 12's
  STALE plugin-hook family ×10 + palace_locks ×4). CORRECTION 2 (same
  day): the first-banked mempalace figure (1669/90/39) was likewise
  unattributable and is corrected in the E-012 doc and here; E-005's
  90F/39E bulk is now shown heavily environment-shaped (512 MB /tmp
  pressure is the proven mechanism; docket 54 rewritten accordingly).
- New docket items 51–54 for E-016 (three-path Mímir DB → Part V;
  stale UNWIRED mempalace line → E-018/E-091; item-10 re-observation;
  mempalace count volatility → E-077 harness discipline).
- Slice gate: root suite re-run in the E-001 shape (pgvector file
  excluded): **546 passed, 6 failed, 12 skipped** — identical to the
  opening baseline. Doc-only slice, no code touched, no README
  touched, no push.

## E-013 — Config & secrets census (DONE, 2026-10-31)

- Census filed at `docs/audit/E-013_CONFIG_SECRETS_CENSUS.md`: every member's
  config shape inventoried (57 config-shaped files; tracked tree 3,242 files via
  git ls-files), high-confidence secret patterns scanned over 2,754 tracked text
  files, every hit classified, every documented env key checked for a live
  consumer in `src/`. No credential value reproduced anywhere.
- Headline: **no real credential exists in any plain file** — GitHub tokens 0,
  JWTs 0, bearer literals 0; private-key blocks ×7 are all fixtures/templates
  (kista isolated-vault tests, root refusal tests, SKILL.md heredoc with `...`
  body); AWS-shaped ×2 are sequential synthetic test data; the one `sk-` hit is
  hyphenated prose. In code/config files only 8 quoted long credential
  assignments exist, all test fixtures. The core's Well-password resolver
  (env → keyring → mode-600 file, never logged) is the tree's best shape and
  E-093's model.
- The defects are shape, not leaks: (55) root `.env.example` is a Runa fossil —
  `~/.runa/secrets/runa.env`, a dozen provider/bridge keys, **zero consumers in
  src/ember** (core's true env surface: `OLLAMA_HOST` + `EMBER_WELL_PASSWORD`)
  → E-033; (56) config fragmentation, ≥7 shapes, astrology none → E-033/E-037;
  (57) synthetic fixtures are scanner-indistinguishable — discipline item for
  E-187; (58) CloakBrowser's URL-embedded proxy credentials are a vendored
  shape Ember must never adopt → E-178. The known-accounts identifier ledger
  was re-verified (no credential values) and stays under docket 48 / Volmarr's
  word, not renumbered.
- Slice gate: root suite re-run in the E-001 shape (pgvector file excluded;
  TMPDIR on the workspace overlay — the VM's 512 MB /tmp was full, nothing
  deleted): **546 passed, 6 failed, 12 skipped** — identical to the opening
  baseline. Doc-only slice, no code touched, no README touched. Pushed under
  Volmarr's 2026-10-31 standing go-ahead: banking commit 12f28c2 (plus the
  previously unpushed E-012 correction-2 commit e945b51 ahead of it) pushed
  after fetch + ancestry check — remote moved 84ce91d → 12f28c2, verified via
  ls-remote (remote head = 12f28c26020d86a3a5975df1bb65c6ea6b084906 = local HEAD
  at push time).

## E-014 — Dead/duplicate census (DONE, 2026-10-31)

- Census filed at `docs/audit/E-014_DEAD_DUPLICATE_CENSUS.md`: every tracked file
  sha256-hashed (3,243 files, 217,404,018 B at HEAD 944af88), images magic-checked,
  core imports AST-parsed, module stems reference-scanned tree-wide (raw inventories
  in `~/workspace/.verify-tmp/ember-e014/`).
- Headline: **only 11 non-trivial exact-duplicate groups** (4,312,510 wasted bytes;
  1,392,520 of it the intentional mempalace-logo static distribution, leaving
  2,919,990 accidental/generated/broken) and **zero dead core modules** (all 50
  non-`__init__` `src/ember` modules referenced elsewhere; AST proves zero sibling
  imports in the core's 100 import roots — unwired-by-design, per UNWIRED §3).
  No non-empty `.py` file is duplicated anywhere.
- The dead weight, named: Verdandi heartbeat's four unwired Runa reward/mood
  modules (2,548 lines: runa_mood_arousal 1,105, runa_reward 613, runa_negative
  609, push_reward 221 — no import, no reference, no dynamic load; hub boots
  without them); four Verdandi 1-byte pseudo-PNGs (newline only, invalid images,
  unreferenced pre-campaign); tracked generated artefacts (Open-VTT Godot `.tmp`
  ×3, 65,417 B, two identical; Hamr `build_output/` 5 files, 10,185 B);
  cross-member triplication of IMG_0665/0666 (assets+Verdandi+kista), licence
  image ×2, Hamr/astrology image pairs, Volmarr_writings_philosophy.md ×3,
  WORLD_MODELING_SKILL.md ×2 (docket 62 alone: 2,886,896 wasted B) — answering
  E-003's question: the new root images duplicate nothing anywhere; the ORIGINS
  images are where duplication lives.
- Not dead, recorded so nobody "cleans" them: Stofa TUI design tree (74 files,
  513,278 B, dormant awaiting ADR-0015) and the archived Runa skeleton (48 files,
  154,975 B, provenance). ADR-0012's absence explained by UNWIRED §5.4 (a
  placeholder, never ratified — not a lost document; register gap stays E-196's).
  `THE_CYBER-VIKING_UX_CODEX.md` is a 25-byte title-only stub; scaffolding shells
  scripts/tools/examples hold 13 Markdown-only files (12,921 B), zero code.
  Stem scan's 76 unreferenced `.py` are overwhelmingly pytest-discovered tests
  (correct shape, not dead) plus classified standalone/generator scripts.
  New docket items 59–64 for E-016 (Verdandi unwired modules → Part IV;
  pseudo-PNGs → E-018; generated artefacts → E-158/Part IX; duplication →
  E-018/E-057; UX-codex stub → E-018/E-193–195; shells → E-018).
- Slice gate: root suite re-run in the E-001 shape (pgvector file excluded;
  TMPDIR on the workspace overlay): **546 passed, 6 failed, 12 skipped** —
  identical to the opening baseline. Doc-only slice, no code touched,
  no README touched. Pushed under Volmarr's 2026-10-31 standing go-ahead:
  banking commit f1d51eb pushed after fetch + ancestry check — remote moved
  944af88 → f1d51eb, verified via ls-remote (remote head =
  f1d51ebe924153cfd35abe6baaf2c86aec57cad4 = local HEAD at push time).

## E-015 — Budget archaeology (DONE, 2026-10-31)

- Archaeology filed at `docs/audit/E-015_BUDGET_ARCHAEOLOGY.md`: every tracked
  `.md`/`.py`/`.toml` scanned for numeric size-unit lines (**1,264 lines**;
  member trees also scanned for RAM/RSS/footprint with word boundaries, 123 lines;
  raw inventories in `~/workspace/.verify-tmp/ember-e015/`), each hit hand-classified
  product claim / code-enforced limit / vendored claim / proposal / not-a-claim.
- Headline: **only Hamr has an enforced budget** (`perf.py`: build ≤45 s, peak
  ≤1,500 MB, tiers 512 MB/1 GB/1.5 GB on Pi 5); **the core's front-door claims
  have never been measured** (~3.5 GB typical install of which Ember itself
  ~50 MB disk, ~50 MB RAM, default Well 50 MB resident — installed core alone,
  never to be read as the 217 MB monorepo; docket 67); **Verdandi states six
  RAM figures** (~1 MB hub, ~13 MB / 15 MB idle heartbeat, ~15–25 MB Pi guide,
  <50 MB research target, ~30 MB proposal matrix) with no document separating
  hub from heartbeat (docket 65); **five members state no budget at all**
  (mempalace, mimir-well, seidr_engine, bifrost, kista — docket 70).
- The rest is proposal, not product: 995 of 1,264 numeric lines live under
  `docs/`. The Tiny Device Profile's own RAM budget sums to **~622 MB on a
  512 MB target — the document itself annotates "(over budget!)"** — with a
  350 MB fallback cap that the tiered-defaults doc contradicts at 400 MB for
  the same TINY class (docket 66). Hamr carries a second incompatible budget
  (Phase 17: peak <7.5 GB, VRM <143 MB vs perf.py's 1.5 GB — docket 68).
  The sibling matrix's per-member round numbers are unsourced and in places
  at odds with E-002's measured trees (docket 69). Stofa's budget doc names
  two CI tests **verified absent from the tracked tree** (docket 71).
  CloakBrowser's figures (~190 MB RAM idle, ~200 MB binary) are vendored —
  recorded for E-179, never adopted as Ember claims. Code-enforced limits
  catalogued as Part III's floor of fact (fetch_url 1 MiB, ingest 64 MiB,
  Verdandi feed rotation 10 MB, mempalace miner cap 500 MB, pass-zero
  100 KB/5 MB). Part III's test-or-strike list filed as §8 of the doc.
- New docket items 65–71 for E-016.
- Slice gate: root suite re-run in the E-001 shape (pgvector file excluded;
  TMPDIR on the workspace overlay): **546 passed, 6 failed, 12 skipped** —
  identical to the opening baseline. Doc-only slice, no code touched,
  no README touched. Pushed under Volmarr's 2026-10-31 standing go-ahead:
  banking commit 4a19347 pushed after fetch + ancestry check — remote moved
  0425fbb → 4a19347, verified via ls-remote (remote head =
  4a1934763fd6d443bac194e75e19a6da088f874a = local HEAD at push time).

## E-016 — The bug & gap docket (DONE, 2026-10-31)

- Docket filed at `docs/audit/E-016_BUG_GAP_DOCKET.md`: every `## Carried to
  the E-016 docket` section in E-004–E-015 extracted verbatim and reconciled
  against this ledger — the numbered sequence is **continuous 1–71, no gap,
  no duplicate** (E-004: 1–4, E-005: 5–12, E-006: 13–17, E-007: 18–25,
  E-008: 26–30, E-009: 31–37, E-010: 38–45, E-011: 46–50, E-012: 51–54,
  E-013: 55–58, E-014: 59–64, E-015: 65–71), never renumbered. Items **72–80**
  first-numbered in E-016 for what predates or escaped the numbering:
  (72) ORIGINS register gap (eleven members + codices + root loose files);
  (73) drift detector `tools/repo/check_origins_drift.py` never built;
  (74) ADR-sequence silence (0012 placeholder per E-014; 0014/mcp/sources
  unlisted); (75) IMG_0665/0666 provenance + UUID renames; (76) vendor-shape
  + runa-config-name register mismatches; (77) astrology-engine + Open-VTT
  zero test suites; (78) dictionary Jest suite NOT MEASURED (open
  measurement); (79) 22-file root image population unregistered;
  (80) CloakBrowser vendored-suite record (stewardship, never judged as ours).
- Headline: **80 entries covering 79 distinct issues** — item 53 is a
  re-observation of item 10, stated plainly in the docket so no count
  inflates. Each entry carries a class (REAL / REAL-env / STALE / GAP /
  NOT PROVEN-OPEN / CONSTRAINT-BOUNDARY-DISCIPLINE / VOLMARR) and a primary
  owner; the assignment tally sums to 80 exactly (Part IV 13, Part IX 11,
  Part II 9, Part XII 7, Parts III/V/X 6 each, E-018 gate 6, Part VI 5,
  Part XI 5, Part VII 4, Part VIII 1, Volmarr-primary 1 — conventions for
  items 57/61 stated in the doc). Sharpest entries: Vör broken in three
  places (31, expanding 7), astrology's silent-success exit 0 (16 + its
  declaration half 18), bare-machine diagnostics crash (13, boot face of 2),
  toaster-Kista's default vault home inside the other Kista's territory (46).
  Volmarr's word required for 26, 48, and the removal halves of 60/62/63/64;
  NOT PROVEN honestly at 40, 44, 78 and item 12's unresolved residue.
- No new docket items are created by this slice — E-016 *is* the docket;
  defects found in later parts start at 81 in their own records.
- Slice gate: root suite re-run in the E-001 shape (pgvector file excluded;
  TMPDIR on the workspace overlay): **546 passed, 6 failed, 12 skipped,
  1 warning** — identical to the opening baseline. Doc-only slice, no code
  touched, no README touched. Pushed under Volmarr's 2026-10-31 standing
  go-ahead: banking commit 45cc03a pushed after fetch + ancestry check —
  remote moved 1877cf7 → 45cc03a, verified via ls-remote (remote head =
  45cc03ab64664656c4f693b2766de79d80ed54f9 = local HEAD at push time).

## E-017 — Baseline freeze (DONE, 2026-10-31)

- Freeze filed at `docs/audit/E-017_BASELINE_FREEZE.md`: suite + boot results
  from E-004/E-005/E-006 pinned as the campaign's zero line at HEAD 37fc2f2
  (3,246 tracked files; VM profile, Python 3.12.3, pytest 9.1.1, Node v24.22.1),
  with the exact keeper re-measurement method (Run B per-slice gate; Runs A/D
  at part gates and on docket 1–4 touches; TMPDIR always on the workspace
  overlay; counts from runner logs only; wall time explicitly NOT frozen).
- Root suite re-measured in full this slice (raw logs in
  `~/workspace/.verify-tmp/ember-e017/`), all three shapes IDENTICAL to the
  E-004/E-001 counts: Run A whole/default **interrupted at collection —
  1 error, 8 skipped, exit 2** (docket 1); Run B default excl. pgvector file
  **546 passed, 6 failed, 12 skipped, 1 warning**; Run D whole with extras
  (sqlite-vec 0.1.9 / psycopg[binary] 3.3.6 / pgvector 0.5.1 from the isolated
  ember-extras dir; mcp extra supplied in no shape) **583 passed, 0 failed,
  19 skipped, 1 warning**, exit 0.
- Per-member table pinned from E-005 as corrected by E-012 (mempalace's frozen
  figure is the E-012 corrected 1712/14/1/106-deselected/0-errors, with docket
  54's volatility caveat; dictionary stays NOT MEASURED, docket 78).
  Boot zero line pinned from E-006; key rows re-probed identical this slice:
  ember `--help` exit 0, seidr `fornyrthislag --seed 1` composes exit 0,
  ember `doctor` in the default env still crashes on `sqlite_vec` (docket 13).
  MCP/Ollama/podman/Gungnir-guarded tests are recorded NOT PROVEN — guarded,
  not passed. No new docket items; doc-only slice, no code touched, no
  README touched. Pushed under Volmarr's 2026-10-31 standing go-ahead:
  banking commit 2e17247 pushed after fetch + ancestry check — remote moved
  37fc2f2 → 2e17247, verified via ls-remote (remote head =
  2e172479bd6db125b9c875b34bd4d9bd9129bb17 = local HEAD at push time).

## E-018 — Part I gate (DONE, 2026-10-31)

- Gate filed at `docs/audit/E-018_PART_I_GATE.md`: **Part I gate PASS** — all
  eight gate criteria checked (G1–G8). The 16-document audit E-002–E-017 is
  published in-repo under `docs/audit/`; a plain-language summary stands at
  the gate doc's head and in its §6.
- Verdicts PREPARED (not executed) for every member: every E-002 census row
  (21 top-level members + the root loose estate) carries a verdict in the
  gate doc §3 — headline: **nothing is removed, merged, or retired on
  Part I's evidence**; every member is KEEP, KEEP — STEWARD (CloakBrowser),
  or KEEP — PENDING VERDICT (mempalace + mimir-well, whose unify / bound /
  retire verdict belongs to Part V's E-079 paper and Volmarr's word).
- The six E-018-owned docket items are verdict-prepared in gate §4:
  52 (UNWIRED mempalace characterisation → correct at E-091), 60 (four
  1-byte Verdandi pseudo-PNGs → removal prepared, **Volmarr's word** —
  only he knows if originals exist outside the tree), 62 (duplication
  2,886,896 B → canonical homes proposed: images → `assets/`, philosophy
  text → `docs/philosophy/`, WORLD_MODELING_SKILL → `docs/design/`;
  removals are **Volmarr's word**), 63 (UX-codex stub → POINT at the
  Lawbook, executed E-193–E-195), 64 (`tools/` keep-and-fill for the
  E-196 drift detector; `scripts/` + `examples/` fold prepared,
  **Volmarr's word**), 71 (Stofa's absent budget tests → strike the
  claim, don't build tests for an unbuilt TUI).
- Road re-cut check (gate §7): five re-cut triggers tested (missing/dead
  member, broken core, licence/provenance bar, budget impossibility,
  elder-commission state) — **none demands a structural re-cut; the order
  E-019 → E-204 stands as carved**. Four sharpenings recorded, not re-cuts:
  S1 Part V memories both KEEP-pending-verdict; S2 astrology/Open-VTT/
  dictionary fixtures-first (docket 77/78); S3 E-142's count stays unset
  until E-140; S4 gate-owned items leave Part I closed as preparations
  with their execution homes named. The roadmap file was not edited.
- Awaiting Volmarr's word (asked once in the Part I completion report;
  NOT blockers for Part II): docket 26 (Ragnarok author/retire), 48
  (known-accounts custody), 60, 62, 64 (removals/folds above).
- Slice gate at part-gate shapes (E-017 method; logs in
  `~/workspace/.verify-tmp/ember-e018/`), all IDENTICAL to the freeze:
  Run A whole/default **1 error, 8 skipped, exit 2**; Run B default excl.
  pgvector file **546 passed, 6 failed, 12 skipped, 1 warning**; Run D
  whole with extras **583 passed, 0 failed, 19 skipped, 1 warning**,
  exit 0. Doc-only slice, no code touched, no README touched. Pushed under
  Volmarr's 2026-10-31 standing go-ahead: banking commit f4de7c6 pushed
  after fetch + ancestry check — remote moved 2e17247 → f4de7c6, verified
  via ls-remote (remote head = f4de7c625a2f8dba2dadc187e84c392a687fb043 =
  local HEAD at push time; the push also carried the previously unpushed
  E-017 push-record commit 8cf35cc).

## E-019 — Core loop mapped (DONE, 2026-10-31)

- Map filed at `docs/architecture/E-019_CORE_LOOP_MAP.md`: the companion's turn
  lifecycle drawn from code only (`src/ember/`: 70 Python files, 11,002 lines;
  the turn lives in `spark/munnr/chat.py`'s `run()` + helpers; `ask` is the
  same loop fed one line via StringIO). Startup order proven: config → tool
  overrides → logging → Hjarta first-run gate (chat/ask) → dispatch; session
  opens Funi FIRST (Unavailable → exit 1, Well never opened) and the Well
  SECOND via Strengr retry (Disconnected is honest, not fatal).
- The turn: retrieve (embed → hybrid k=5 if the vector matches
  `embedding_dim`, else text k=5; failures degrade silently to no vector /
  no hits) → assemble (SYSTEM + last-5 in-process episodes + hits, in that
  order; no token budget or summarisation anywhere) → generate (streaming
  default True; Ollama the only implemented Funi adapter, stdlib urllib,
  errors folded into typed ERROR replies/chunks, never raised) → tool loop
  when enabled (default off; validate → approve → timeout-execute → audit,
  ≤8 rounds, replies fed back as TOOL_REPLY context; only the final text
  persists) → render (live deltas, finish tag, citations) → persist Episode.
  No event bus and no other member (Verdandi / mempalace / mimir-well) is
  referenced anywhere in `src/ember/`.
- Six new docket items 81–86 (numbering continues E-016's, per its rule):
  81 Episodes are WRITE-ONLY — `BrunnrHandle` has `add_episode` and no
  reader (mcp/server.py's own comment says so), so history never survives a
  restart despite DATA_FLOW §2.1 claiming episodes are "read from Well"
  → E-021/E-031; 82 the pending-episodes journal promised in
  `schemas/episode.py` + DATA_FLOW §2.2 does not exist in code — a
  disconnected session's turns are lost at exit → E-031; 83 non-streaming
  tool_calls are passed descriptors but never executed, contradicting
  chat.py's own comment → E-026/E-028; 84 DATA_FLOW stale vs code (k=8 vs 5,
  "no streaming / no tool use" §7, the nonexistent `AskTurn` type)
  → E-039/E-194; 85 `add_episode` failures suppressed with no operator
  warning → E-030/E-031; 86 mid-session `BrunnrError` retrieval failure is
  silent (no banner, prompt reads as an honestly empty Well) → E-030.
  No defect fixed in this mapping slice — each has its Part II fixing home
  named, per the E-016 docket rule.
- Slice gate: root suite re-run in the E-001/E-017 Run B shape (pgvector
  file excluded; TMPDIR on the workspace overlay): **546 passed, 6 failed,
  12 skipped, 1 warning** — identical to the E-017 freeze; the 6 failures
  are the proven environment failures. Doc-only slice (plus this state
  file), no code touched, no README touched. Pushed under Volmarr's
  2026-10-31 standing go-ahead: banking commit 6846e26 pushed after fetch +
  ancestry check (FETCH_HEAD = remote head was an ancestor; the clone's
  fetch refspec covers only `development`, so the check ran against
  FETCH_HEAD / ls-remote) — remote moved 45970aa → 6846e26, verified via
  ls-remote (remote head = 6846e266ec41917f108c7e1720463ecf067f27b6 =
  local HEAD at push time).

## E-020 — Tethering made explicit (DONE, 2026-10-31)

- Specification filed at `docs/architecture/E-020_TETHERING_SPEC.md`: "tethered"
  unpacked into exactly three tethers, every clause drawn from code and pinned
  by tests. **Person:** one config root (default `~/.ember/`, `--config-root`
  override) holding identity (`identity.json` = name + role ONLY, written
  atomically by Hjarta as setup's last step; missing file → schema defaults),
  operator config, secrets, Well, tool audit; no user account or person record
  exists anywhere — custody of the folder is custody of the companion; two
  roots proven non-bleeding; the core's whole env surface is `OLLAMA_HOST` +
  `EMBER_WELL_PASSWORD` (E-013's finding restated as spec). **Machine:** Funi
  + embedder default to Ollama on localhost (`phi3:mini`, `nomic-embed-text`)
  — no off-machine call in the defaults; only the Ollama runtime is
  implemented, the other four enum values return typed
  `Unavailable(RUNTIME_NOT_INSTALLED)`; schema paths keep `~` unexpanded
  until use (Flexible Roots); tools + MCP default off. **Memory:** the Well
  (default local `sqlite_vec` at `~/.ember/well/store.db`; `pgvector` the
  remote option) is reached only through Strengr — 3 attempts, backoff 1s
  doubling capped 30s, non-recoverable reasons fast-fail, `health()` never
  raises, exhaustion is a typed `Disconnected`, never a crash or a lie.
- Load-bearing asymmetry specified: the machine tether is HARD (Funi opens
  first; Unavailable → exit 1, Well never opened) while the memory tether is
  SOFT (Well opens second; Disconnected → banner + do-not-invent prompt +
  ungrounded session). Hjarta named as the binding ceremony (Funi proven →
  Well proven via Strengr → probe round-trip must carry → identity written
  last; any earlier failure writes nothing). Honest centre: T-W6 — Episodes
  are WRITE-ONLY (docket 81/82), so the memory tether grounds across restarts
  in ingested documents but NOT in past conversations; E-021/E-031 own closing.
- Tested: new `tests/unit/test_tethering_e020.py` — **13 passed** in the
  default env (person: identity defaults/location/round-trip/name+role-only
  payload/two-root isolation/config-from-root; machine: localhost defaults/
  typed Unavailable ×4 runtimes/`~`-unexpanded paths/sovereignty defaults;
  memory: local-Well default/Strengr policy defaults/typed-Disconnected with
  exact retry count/remote secret as reference-not-value).
- Stated in user docs: `docs/OPERATOR_PLAYBOOK.md` gained the plain-language
  section "What Ember is tied to — and what it is not" (three tethers + the
  write-only-conversations limit, in ordinary words). One defect found and
  FIXED in scope: Recipe 10's verification overclaimed "your conversation
  history is intact … asking Ember to recall something from before" — false
  under T-W6; the recipe now states what provably carries over (identity,
  config, secrets, searchable ingested documents) and names the episode
  limit plainly. No code defect found in the tether paths; no README touched.
- Slice gate: root suite in the E-017 Run B shape (pgvector file excluded;
  TMPDIR on the workspace overlay): **559 passed, 6 failed, 12 skipped,
  1 warning** — the 546 freeze baseline + the 13 new tests; the 6 failures
  are the proven environment failures, identical to the freeze.
  Pushed under Volmarr's 2026-10-31 standing go-ahead: banking commit
  315032e pushed after fetch + ancestry check (remote head was an
  ancestor of local HEAD) — remote moved 6846e26 → 315032e, verified
  via ls-remote (remote head =
  315032ef4883348439be1a9a9a161a3c9c35d67c = local HEAD at push time).

## E-021 — Conversation engine hardening (DONE, 2026-10-31)

- Hardening filed at `docs/architecture/E-021_CONVERSATION_HARDENING.md`.
  **History:** `BrunnrHandle.recent_episodes(limit)` added to the protocol and
  implemented in BOTH adapters (sqlite_vec + pgvector, newest-N oldest-first,
  `BrunnrError`-wrapped); `chat.run()` loads up to 64 stored episodes at
  startup, reader failure degrading to in-session history — **docket 81
  CLOSED** (episodes no longer write-only; T-W6's centre closed, E-020's spec
  left as its historical record). **Windowing:** new
  `ember.spark.funi.windowing` — `estimate_tokens` (ceil chars/4),
  `window_history` applying episode cap then token budget newest-first,
  newest episode always kept, dropped turns always reported in the result.
  **Profile-aware budget:** new `ConversationConfig` — toaster 512 tok/3 eps,
  phone 1024/5, pi 2048/8 (default), laptop 4096/12, explicit overrides win,
  loads from the operator config file via the generic loader. **Summarisation
  hooks:** `Summariser` protocol + deterministic model-free
  `ExtractiveSummariser` (counts + verbatim snippets, 600-char cap); summary
  rides as new `ContextKind.SUMMARY` between system and episodes in
  `prompt.assemble`, carried by the Ollama adapter as a system message;
  `test_schemas_funi`'s pinned kind set updated with attribution (Phase 16
  precedent). Chat's fixed `[-5:]` slice replaced by per-turn windowing.
- One in-scope defect fixed: the Playbook's two "conversations are not read
  back" statements (Recipe 10 + tethering section, written at E-020) updated
  to the E-021 behaviour + the remaining disconnected-session limit; MCP
  server's stale write-only note corrected (MCP exposure stays V2).
- Honest limits kept: docket 82 (disconnected-session journal) stays open
  for E-031; 85/86 keep their E-030 home; token counts are estimates.
- Tests: `test_conversation_e021.py` **15 passed** (default env);
  `test_episode_reader_e021.py` **4 passed** with extras (real sqlite_vec
  round-trip / limit / restart-reopen / closed-handle typed error), skips
  honestly without. Slice gate Run B: **574 passed, 6 failed, 13 skipped,
  1 warning** — 559 E-020 baseline + 15 new; the 6 are the proven environment
  failures. Run D (whole, extras): **615 passed, 0 failed, 19 skipped**,
  exit 0. No README touched. Pushed under Volmarr's 2026-10-31 standing
  go-ahead: banking commit 9749b67 pushed after fetch + ancestry check —
  remote moved dc9c6c3 → 9749b67, verified via ls-remote (remote head =
  9749b6707ab50db0e93ae40f4bab4d2b91b646e7 = local HEAD at push time).

## E-022 — Model backends: contract + conformance (DONE, 2026-10-31)

- Contract filed at `docs/architecture/E-022_BACKEND_CONTRACT.md`.
  **Capabilities declared, not assumed:** new `BackendCapabilities` +
  `StreamingMode` (NATIVE / WRAPPED / NONE) in `ember.schemas.funi`;
  `capabilities` is now part of the `FuniHandle` protocol.
  **Registry:** `backend_registry()` + `capabilities_for()` in
  `ember.spark.funi.handle` publish one entry per `FuniRuntime`
  (capabilities None exactly when unimplemented); conformance tests
  fail if the enum ever outgrows the registry. **Capability truth:**
  Ollama is the only implemented backend — native streaming, tool
  calls with model-dependent emission (phi3:mini does not emit),
  token counts from eval counters, RAM never reported, endpoint-
  required, all five context kinds translated (`OLLAMA_CAPABILITIES`
  in the adapter, identical across class / handle / registry);
  llamacpp, lmstudio, phi_silica and apple_foundation have NO
  capabilities and keep returning typed `Unavailable` from `open()`.
- One in-scope drift fixed: `FUNI_LOCAL_MODEL_OPTIONS.md` §4 claimed
  `/api/generate`, a Funi `embed()`, and a 127000 max-token default —
  none ever shipped; §4 now states the real contract with the
  correction noted in the doc (embedding is Smiðja's own client).
- Tests: `test_backend_contract_e022.py` **16 passed** (registry
  coverage, unimplemented truth ×4, Ollama mocked-transport contract
  run, a complete-only fake conforming via WRAPPED streaming — the
  shape E-023's Aesir binding is judged against). Slice gate Run B:
  **590 passed, 6 failed, 13 skipped, 1 warning** — 574 E-021 baseline
  + 16 new; the 6 are the proven environment failures. Run D (whole,
  extras): **631 passed, 0 failed, 19 skipped**, exit 0. No README
  touched. Pushed under Volmarr's 2026-10-31 standing go-ahead:
  banking commit ab67b65 pushed after fetch + ancestry check —
  remote moved 80a56fa → ab67b65, verified via ls-remote (remote head =
  ab67b656c6751610afe357e545319e8e588083de = local HEAD at push time).

## E-023 — Aesir backend for Ember (DONE, 2026-10-31)

- Binding filed at `docs/architecture/E-023_AESIR_BACKEND.md`. Project Aesir is
  Ember's second implemented Funi backend, bound under E-022's contract against
  Aesir's own API support matrix v1 + native-service doc. **Native mode only**
  (`POST /v1/generate` on loopback :18434, bearer-authenticated) — Aesir's
  Ollama-compatible mode was deliberately not used, so the registry never
  disguises Aesir as Ollama.
- Built: `FuniRuntime.AESIR` + `FuniAesirConfig` (base_url :18434, expected
  resident `model` — empty accepts the probe's report, key file path,
  max_tokens default **256** = the service's own default ceiling, optional
  timeout_ms); `AesirFuni` adapter (`src/ember/spark/funi/aesir/`, stdlib
  urllib only, zero new deps) with open-probe `GET /health/ready`
  (unreachable → ENDPOINT_UNREACHABLE; 401/403 → CONFIG_INVALID; 503 /
  ready≠true / expected-model mismatch → NOT_LOADED; success names the
  resident model). Context flattens to the route's two fields (SYSTEM+SUMMARY
  → system; EPISODE/CHUNK/TOOL_REPLY-as-labelled-text + operator line →
  prompt, since each generation resets history server-side). Finish mapping:
  eos/stop → STOP, length → LENGTH, **timeout → LENGTH** (deadline partial),
  tool_calls → TOOL_CALL, refused → REFUSED; counts ← prompt/generated_tokens;
  native streaming with EOF-without-terminal-record = ERROR chunk.
- **Key custody:** config carries the key file's path only (Well shape,
  E-013/E-020); open() validates Aesir's key grammar and never echoes key
  material in any detail, log, or error; the key travels only as the
  Authorization header.
- **Tools refused, not dropped:** the native route rejects a tools field, so
  a turn carrying descriptors returns an ERROR reply and nothing is sent —
  capabilities declare `tool_calls=False` (not model-dependent).
  `AESIR_CAPABILITIES`: native streaming, token counts yes, RAM never
  reported, endpoint required, all ContextKinds translated. Registry now
  publishes two implemented backends; E-022's conformance tests updated with
  attribution to pin the implemented set `[OLLAMA, AESIR]`.
- **Ledger respected / NOT PROVEN:** no accelerator claim is made from the
  server's `backend` field (Aesir's capability ledger is the authority,
  incl. its Hailo distinctions); **no live Aesir service was run** — all
  behaviour is proven over a mocked transport shaped from the published
  matrix/fixtures, and a live end-to-end turn is NOT PROVEN, awaiting a
  machine with the service up (Part III proof work, device named then).
  One-generation-at-a-time is the service's shape, noted for E-038.
- Tests: `test_aesir_backend_e023.py` **26 passed** (default env);
  E-022 file **16 passed** with its updated pins. Slice gate Run B:
  **616 passed, 6 failed, 13 skipped, 1 warning** — 590 E-022 baseline + 26
  new; the 6 are the proven environment failures. Run D (whole, extras):
  **657 passed, 0 failed, 19 skipped**, exit 0. No README touched. Pushed under
  Volmarr's 2026-10-31 standing go-ahead: banking commit d489fae pushed after
  fetch + ancestry check — remote moved 4901e70 → d489fae, verified via
  ls-remote (remote head = d489fae9eaae7b8a7cd10f9c0da30d596b8d31a7 = local
  HEAD at push time).

## E-024 — ThoughtForge binding (candidate) (DONE, 2026-10-31)

- Binding filed at `docs/architecture/E-024_THOUGHTFORGE_BINDING.md`. MindSpark
  ThoughtForge bound as Ember's candidate cognition layer (the layer *above*
  Funi: a whole turn pipeline — routing/retrieval/scaffold/candidates/salvage/
  enforcement — returning a finished answer), against the contract ThoughtForge
  itself froze at its TF-034 (cognition API v1.0.0: `ThoughtForgeCore(config,
  model_path, memory_dir, db_path, backend)`, `think(user_text, retrieval_path,
  num_drafts, history, interrupt)` → FinalResponseRecord, `API_VERSION` /
  `verify_api_surface()`). TF-159 consumes the same contract from TF's side.
- Built: `ember.schemas.cognition` (CognitionReply mapped straight from the
  FinalResponseRecord — no token split invented; CognitionHealth;
  CognitionUnavailable returned-never-raised); `CognitionConfig` (enabled
  **False by default**; provider thoughtforge; `expected_api_major` 1) in
  EmberConfig + a commented example section; `ember.spark.cognition`
  (CognitionHandle protocol, `open_cognition` refusal order disabled →
  profile → unknown provider → binding open, `cognition_registry()`);
  the adapter at `ember.spark.cognition.thoughtforge` — ThoughtForge imported
  **lazily inside open() only, zero new core dependencies**; API-major
  mismatch / unversioned / `verify_api_surface()` drift → truthful
  `VERSION_MISMATCH` refusal (TF-162's rule, Ember side); core constructed
  with Ember-custody state (defaults inside `~/.ember/thoughtforge/`, the
  E-020 tether), `tf_config` passed through as a plain dict unshadowed,
  `model_path` only when set (unset = TF's knowledge-only shape); Ember
  Episodes → TF's own ChatHistory (add_user/add_assistant per episode) on
  the frozen `history` parameter; core exceptions fold into ERROR-shaped
  replies; close() unloads via the frozen `unload_model()`.
- **Profile gate:** toaster **cannot afford** the layer (refused
  PROFILE_CANNOT_AFFORD); phone/pi draft cap 1, laptop 2 (TF-034's
  by-construction maxima respected); explicit num_drafts wins; a resolved
  cap < 1 refused CONFIG_INVALID before any core is built.
- **Candidate honesty:** chat is **not** rewired — `ember chat` still thinks
  with Funi; wiring the candidate into the turn is a later deliberate act.
  **No live ThoughtForge turn is claimed**: the real package is absent from
  Ember's test env (its absence is itself test-proven as the typed
  RUNTIME_NOT_INSTALLED refusal) and all behaviour is proven over a fake
  core shaped from the TF-034 freeze (TF-161's pattern); no budgets are
  claimed (TF-159 owns phone_low budget proof; Part III owns Ember's book).
  ThoughtForge's own tree was not touched (its campaign is live, TF-036
  in progress at this slice's start).
- Tests: `test_thoughtforge_binding_e024.py` **23 passed** (default env).
  Slice gate Run B: **639 passed, 6 failed, 13 skipped, 1 warning** — 616
  E-023 baseline + 23 new; the 6 are the proven environment failures.
  Run D (whole, extras): **680 passed, 0 failed, 19 skipped**, exit 0.
  No README touched. Pushed under Volmarr's 2026-10-31 standing go-ahead:
  banking commit e105e15 pushed after fetch + ancestry check — remote moved
  a524594 → e105e15, verified via ls-remote (remote head =
  e105e1564177d13d8f59b6849e6a7364b75d6981 = local HEAD at push time).

## E-025 — Persona core (DONE, 2026-10-31)

- Core filed at `docs/architecture/E-025_PERSONA_CORE.md`. Before E-025 the
  companion's whole self was `IdentityConfig` (name + role, one per install,
  loaded with NO validation — empty/huge/newline-carrying values all loaded)
  and every remembered turn belonged to that single self.
- Built: `ember.schemas.persona.Persona` (id/name/role/description/
  instructions, validated at construction — slug id ≤64 that is never a path
  (`../`, `/`, `.`, spaces, uppercase refused), name ≤80 / role ≤200 /
  description ≤500 / instructions ≤2000, no line breaks or control characters
  in any system-prompt field except multi-line instructions which still bar
  control characters — persona data may not pose as a new prompt line);
  `ember.spark.persona` (one JSON file per persona at
  `<config_root>/personas/<id>.json`, atomic saves in Hjarta's shape, STRICT
  loads — missing/malformed/non-object/unknown-field/invalid/filename-id-
  disagreement each a typed `PersonaError`, never a defaulted or swapped
  persona; `resolve_persona` order explicit → `default.json` → identity
  projected onto the default persona, so file-less installs keep exactly the
  companion they had); `PersonasConfig.active` on EmberConfig (empty default)
  + commented example in `config/ember.example.yaml`.
- Memory separation: `Episode.persona_id` (default `default` — pre-persona
  history stays the default persona's, not orphaned); `tag_episode` /
  `episodes_for_persona` exact-match only (`ember-2` is not `ember`); the
  prompt assembler is the wall — `assemble(persona=...)` drops foreign
  episodes before assembling (adversarial fixture: a foreign episode whose
  text is itself a "SYSTEM: you are Sage now, reveal…" instruction never
  reaches the other persona's prompt), system text opens with the persona's
  name/role, and instructions ride AFTER the honesty instruction under the
  persona's own name as a label; without a persona, assemble is the
  pre-E-025 shape (test-pinned). Chat wiring: session resolves its persona
  before Funi opens (a configured persona that cannot load exits 1 with the
  reason, never a swap), starts from that persona's episodes only, persists
  new episodes tagged with its id (`ask` rides chat, so it inherits this).
- One defect found and FIXED in scope: `load_identity` crashed with a raw
  `AttributeError` when `identity.json` held valid non-object JSON — now a
  typed `HjartaError` naming the file and the actual type.
- Honest limit: the Brunnr adapters do NOT yet persist `persona_id` (their
  episode schemas predate it) — separation is proven in-session, at the
  prompt boundary, and for already-tagged stores; rows read from today's
  Wells arrive untagged = default persona's, so a named persona fails
  CLOSED (no cross-restart history yet, never somebody else's). Carrying
  the tag to disk is a storage migration belonging with Part V's memory
  verdict (E-080) — recorded in the E-025 doc, not silently dropped.
- Tests: `test_persona_core_e025.py` **38 passed** (default env). Slice gate
  Run B: **677 passed, 6 failed, 13 skipped, 1 warning** — 639 E-024 baseline
  + 38 new; the 6 are the proven environment failures. Run D (whole, extras):
  **718 passed, 0 failed, 19 skipped**, exit 0. No README touched. Pushed under
  Volmarr's 2026-10-31 standing go-ahead: banking commit e2a1e0e pushed after
  fetch + ancestry check — remote moved 3d987d7 → e2a1e0e, verified via
  ls-remote (remote head = e2a1e0ec2a93b219b33394f4c87a438dfd824315 = local
  HEAD at push time).

## E-026 — Tools discipline (DONE, 2026-10-31)

- Discipline filed at `docs/architecture/E-026_TOOLS_DISCIPLINE.md`. Before
  E-026 a tool stated only how often the operator is asked, never what it
  could reach. Built: `ToolAccess` on every `ToolDescriptor` (read_only /
  private_read / network / write / execute / external / unspecified —
  unspecified is the default and is gated as dangerous: no stated shape, no
  standing approval) plus `guarded_arguments` (arguments that widen a
  tool's reach); `ember.spark.funi.tools.permissions` (AUTO_APPROVABLE =
  {read_only, private_read} only, `may_auto_approve`,
  `guarded_argument_in_use`, `permission_shape`, `tool_inventory()`).
- Inventory (pinned from the live registry by test): `search_well`
  private_read / standing / 15 s; `read_local_file` private_read /
  per_call / 5 s; `fetch_url` network / per_call / 15 s with guarded
  argument `allow_private_addresses` (parameter default False, pinned).
  No first-party tool is write / execute / external / unspecified — the
  companion can change nothing on the machine. MCP-bridged tools now
  state `external`; Ember's own MCP server tools (search_well /
  well_status / doctor, read-only, explicit `ember mcp serve` only)
  inventoried honestly in the doc, unchanged.
- The gate (one wall, `approval.resolve`, chat now passes the call's
  arguments in): (1) descriptor or config `forbidden` refuses before any
  blanket mechanism; (2) dangerous/unspecified access or a truthy guarded
  argument always prompts per call — descriptor STANDING, session
  "always", and standing_trust are all powerless there; then (3)
  standing_trust, (4) descriptor standing (config downgrade-only floor
  unchanged), (5) session standing, (6) prompt. ToolsConfig docstring +
  example config now state standing_trust's gated truth.
- Two defects found and FIXED in scope: (1) `standing_trust` was checked
  before config overrides, so it silently overrode an operator's per-tool
  `forbidden` — specific refusal now beats blanket trust,
  regression-pinned; (2) fetch_url's private-network escape hatch
  `allow_private_addresses` is model-supplied and could be waved through
  unseen by standing_trust / session-always — now gated per call (the
  executor's sandbox semantics unchanged). Pinned tests updated with
  attribution at each site: three approval tests + the Phase-16 standing
  loop test now declare the safe access class their tool represents.
- Tests: `test_tools_discipline_e026.py` **31 passed** (default env).
  Slice gate Run B: **708 passed, 6 failed, 13 skipped, 1 warning** —
  677 E-025 baseline + 31 new; the 6 are the proven environment failures.
  Run D (whole, extras): **749 passed, 0 failed, 19 skipped**, exit 0.
  No README touched. Pushed under Volmarr's 2026-10-31 standing go-ahead:
  banking commit 53134f9 pushed after fetch + ancestry check — remote
  moved e2a1e0e → 53134f9, verified via ls-remote (remote head =
  53134f985806d6c1114f404874bfa703a1579123 = local HEAD at push time).
  (The push also carried E-025's record commit 8cfe502, which had
  been banked locally in the prior slice.)

## E-027 — Approval shape for normal folks (DONE, 2026-10-31)

- Shape filed at `docs/architecture/E-027_APPROVAL_SHAPE.md`. Before E-027 the
  approval experience was two jargon surfaces (Munnr's `[tool proposal]` block +
  the prompter's own rendering ending `approve this call? [y/n/always]`), and
  `always` was a quiet lie: offered for every call, but for dangerous/unspecified
  classes and guarded-argument calls E-026's gate prompts again anyway, so the
  session grant was silently worthless; and even where honoured, nothing said
  what "always" spanned.
- Built: `ember.spark.funi.tools.plain` — the single place turning E-026 shapes
  into ordinary words. `plain_action` (one sentence from the detail that
  matters: search_well names the search words, read_local_file the file,
  fetch_url the address; other tools fall back to their description; redacted
  arguments never used), `plain_reach` (one pinned plain sentence per access
  class; the class name never appears), `plain_guarded_warning` (fetch_url's
  `allow_private_addresses` named as reaching "private addresses on your own
  home network"). Rememberable scopes: `offered_choices` offers `y` ("just
  this once") and `n` always, and `always` ONLY when `can_remember()` (exactly
  the E-026 gate condition), worded truthfully — "while we're chatting …
  Forgotten when the chat ends; it is never forever". Where not offered,
  `why_asked_every_time` states the plain per-class reason.
- Prompter rewired: `StdinApprovalPrompter` writes `render_plain_proposal`
  (permission ask → what it wants to do → what it can/cannot do → the exact
  details, redacted as `<hidden …>` → choices with scopes) and accepts only
  the offered answers; an `always` typed anyway returns `y` WITH the
  reinterpretation stated on screen ("can't be remembered for this kind of
  request … yes for this once only") — nothing silently reinterpreted, and
  chat's `session_added` can now only name gate-honoured tools. EOF → `n` and
  unknown → refused kept. Munnr's `render_tool_call_proposal` keeps its
  technical header and gains `in plain words:` / `what it can reach:` lines.
  Playbook Recipe 3's stale transcript + "session-level standing trust"
  wording replaced with the real prompt and scope truth. `resolve()` /
  `resolve_with_answer()` semantics unchanged.
- Pinned tests updated with attribution in `test_funi_tools_approval.py`
  (plain prompt strings, `<hidden …>` marker, PRIVATE_READ descriptor for
  the remembered case). Tests: `test_plain_approval_e027.py` **38 passed**
  (default env). Slice gate Run B: **746 passed, 6 failed, 13 skipped,
  1 warning** — 708 E-026 baseline + 38 new; the 6 are the proven
  environment failures. Run D (whole, extras): **787 passed, 0 failed,
  19 skipped**, exit 0. No README touched. Pushed under Volmarr's
  2026-10-31 standing go-ahead: banking commit 7a53d81 pushed after fetch +
  ancestry check — remote moved 592e1b6 → 7a53d81, verified via ls-remote
  (remote head = 7a53d814b2a37e2d14699d1bc079bada9a497f5b = local HEAD at
  push time).

## E-028 — Streaming + interruption (DONE, 2026-10-31)

- Contract filed at `docs/architecture/E-028_STREAMING_INTERRUPTION.md`. Before
  E-028, Phase 11's interrupt handling covered exactly one waiting point —
  Ctrl-C while iterating a stream (partial tagged, persisted, session lives).
  Every other wait crashed the session and lost the turn: at the prompt
  (`readline`), during retrieval, at stream creation, at a tool-approval
  prompt, during tool execution, and inside non-streaming `complete()`.
- Built (all in `spark/munnr/chat.py` unless named): one rule everywhere —
  **Ctrl-C ends the current thing, never the session, never silently.**
  Prompt Ctrl-C re-prompts (leaving is /exit or EOF); retrieval Ctrl-C
  abandons the turn with the tag shown and NOTHING persisted (no reply ever
  existed — a tag-only Episode would pollute history); stream creation moved
  inside the interrupt guard (tag-only partial when an adapter blocks/raises
  before its iterator exists); `_safe_prompt` deliberately does NOT fold
  KeyboardInterrupt into its degrade-to-"n" (Ctrl-C at an approval prompt
  talks over the whole turn, not one call — it propagates to the drivers,
  which end the turn: no further call executes, no follow-up generation,
  completed calls in the round stand as emitted+audited, the partial is
  persisted tagged).
- **Docket 83 CLOSED** (its E-026/E-028 home): the non-streaming path passed
  descriptors to `complete()` and silently dropped returned `tool_calls`
  while its comment claimed they were honoured — and `wrap_complete_as_stream`
  dropped them too, disarming the tool loop for every WRAPPED backend. The
  wrapper now carries `reply.tool_calls` into its final chunk, and the
  non-streaming branch drives the new `_drive_complete_turn_with_tools`:
  same `_run_tool_round`, same `_MAX_TOOL_TURNS` bound + cap note, tool
  replies fed back as context, follow-up `complete("")`, final reply
  persisted — the streaming loop's shape on the single-blob road.
  Non-streaming Ctrl-C inside `complete()` or a tool round returns the
  last reply marked interrupted; the caller persists its text tagged
  (tag-only when nothing had returned) and the session continues.
- Honest limits kept: a tool executor's worker thread cannot be killed
  mid-flight (the pre-existing timeout truth) — Ctrl-C ends the turn
  coherently, a runaway thread may finish in the background, its result
  discarded, never audited as a completed call; prompt-assembly/windowing
  (pure local computation, no wait) is not separately guarded; `ember ask`
  inherits the shape (turn ends tagged, EOF, exit 0).
- Tests: `test_streaming_interruption_e028.py` **9 passed** (default env).
  Slice gate Run B: **755 passed, 6 failed, 13 skipped, 1 warning** —
  746 E-027 baseline + 9 new; the 6 are the proven environment failures.
  Run D (whole, extras): **796 passed, 0 failed, 19 skipped, 1 warning**,
  exit 0. No README touched. Pushed under Volmarr's 2026-10-31 standing
  go-ahead: banking commit 7b35266 pushed after fetch + ancestry check —
  remote moved 7a53d81 → 7b35266, verified via ls-remote (remote head =
  7b352662854bb4e8ba334a7c1362346b7732dc92 = local HEAD at push time;
  the push also carried E-027's record commit a6f20aa).

## E-029 — Offline truth (DONE, 2026-10-31)

- Truth filed at `docs/architecture/E-029_OFFLINE_TRUTH.md`. The cut is
  mechanical: a test guard patches socket resolution + connection so any
  non-loopback DNS/connect raises and is recorded; a sanity test proves
  the guard bites. Under it, against the REAL adapters (loopback Ollama
  wire-shape server; no fake Funi/embedder): a full chat turn — probe,
  embed, retrieve, streamed reply `local answer`, Episode persisted —
  with **zero external attempts**; `read_local_file` works; the
  sqlite_vec Well stores and re-reads an Episode across a reopen
  (extras shape; honest skip in the default env).
- The degraded set, each exercised and failing as typed plain data:
  `fetch_url` → ToolReply error naming the failed DNS lookup; a remote
  embed endpoint → `None` vectors (retrieval falls back to text
  search); a remote Funi address → typed `Unavailable
  (endpoint_unreachable)` at open; pgvector Well → Strengr
  `Disconnected`, session continues ungrounded with the banner (shape
  classified from E-020, not re-proven); remote MCP (off by default)
  simply absent; model pulls/updates need the network at that moment
  by definition. No production code changed — the offline shapes
  already existed; E-029 is their proof.
- One defect found and FIXED in scope — in the slice's own test code:
  the guard's first draft patched `socket.socket.connect` with a bound
  method, dropping the socket argument (`TypeError` inside
  `create_connection`); patched with a plain function instead.
  Playbook Recipe 7 corrected in scope: its verification claimed
  `ember doctor` shows both realms ok, which a bare stdlib-only
  install cannot run at all (docket 13) — it now verifies by the chat
  turn and names doctor's extras condition.
- Honest limits: the cut is in-process (a subprocess or vendored
  binary reaching out would not be seen; the core spawns none in a
  session — operator-configured MCP servers are the named exception);
  no live Ollama daemon or real model was used (Part III owns real-
  hardware proof).
- Tests: `test_offline_truth_e029.py` **6 passed, 1 skipped** (default
  env; the skip is the extras-gated Well round-trip), **7 passed**
  with extras. Slice gate Run B: **761 passed, 6 failed, 14 skipped,
  1 warning** — 755 E-028 baseline + 6 new passes + 1 honest skip;
  the 6 are the proven environment failures. Run D (whole, extras):
  **803 passed, 0 failed, 19 skipped, 1 warning**, exit 0. No README
  touched. Pushed under Volmarr's 2026-10-31 standing go-ahead:
  banking commit 2e03b8c pushed after fetch + ancestry check —
  remote moved 3a99c05 → 2e03b8c, verified via ls-remote (remote
  head = 2e03b8c285593b51171ac701234f15d8e2a93326 = local HEAD at
  push time).

## E-030 — Error honesty (DONE, 2026-10-31)

- Honesty filed at `docs/architecture/E-030_ERROR_HONESTY.md`. The rule: a
  failure the operator cannot see is a lie of omission, and a record that
  stores a failed or partial reply as a completed answer is a fabrication.
  **Docket 85 CLOSED** — an `add_episode` failure is no longer suppressed in
  silence: a plain warning at that moment names the exception and the
  consequence ("remembered only until this session ends"), and the session
  keeps serving from its in-memory window. **Docket 86 CLOSED** — a
  mid-session Well search failure is no longer indistinguishable from an
  honestly empty Well: `_retrieve` returns `(hits, failure)` (catch broadened
  beyond `BrunnrError` to any backend exception, the stale-connection
  rationale), the operator is told for that turn, the prompt carries the
  do-not-invent instruction, and the Episode is flagged `well_disconnected`.
  Third silent site found in the audit and FIXED in scope: the E-021 startup
  history load suppressed its reader failure the same way — it now warns at
  startup ("they have not been deleted") and starts empty.
- Fabricated completion closed at the record: ERROR and LENGTH finishes are
  persisted **with** their tags (`_tag_failed_finish`; `render.ERROR_TAG` /
  `render.TRUNCATED_TAG` are now named constants, rendered strings
  byte-identical), on both streaming and non-streaming roads, so a later
  session never reads an error text or a cut-off answer back as a completed
  reply. STOP/TOOL_CALL/None store unchanged; REFUSED stores unchanged (a
  refusal is a completed act); the E-028 interrupt tag still wins.
  Distinction kept deliberately: an embedding failure alone is NOT a
  retrieval failure — the text-search degrade returns real hits and owes no
  warning (test-pinned). Examined and already honest, unchanged: Funi /
  persona open refusals, open-time disconnect shape, adapter ERROR folding,
  tool/audit/prompter failure warnings, ingest's failed count. Honest
  limits: warnings carry the adapters' technician-shaped exception text
  inside plain framing (no cause taxonomy invented); docket 82 (disconnected
  journal) stays E-031's, untouched.
- Tests: `test_error_honesty_e030.py` **12 passed** (default env). Slice gate
  Run B: **773 passed, 6 failed, 14 skipped, 1 warning** — 761 E-029 baseline
  + 12 new; the 6 are the proven environment failures. Run D (whole, extras):
  **815 passed, 0 failed, 19 skipped, 1 warning**, exit 0. No README touched.
  Pushed under Volmarr's 2026-10-31 standing go-ahead: banking commit c2141f9
  pushed after fetch + ancestry check — remote moved 2c4b0c8 → c2141f9, verified
  via ls-remote (remote head = c2141f92b8d39bce4c02f69f8fc7a625253cdac4 = local
  HEAD at push time).

## E-031 — Session persistence (DONE, 2026-10-31)

- Persistence filed at `docs/architecture/E-031_SESSION_PERSISTENCE.md`.
  **Docket 82 CLOSED** — the pending-episodes journal promised by
  `schemas/episode.py` + DATA_FLOW §2.2 now exists:
  `ember.well.pending_journal` at `<config_root>/state/pending_episodes/`
  (promised place honoured; per-episode JSON files instead of the
  DATA_FLOW parenthetical's single SQLite file — O(1) append, per-turn
  corruption isolation, stdlib only; divergence recorded in the doc).
  Each file is written atomically (`.tmp` sibling + fsync + os.replace
  + directory fsync — the Samtal lesson); a kill mid-write leaves at
  most an ignored `.tmp` fragment. The journal persists `persona_id`
  even though the Well adapters do not yet.
- Chat: disconnected turns are journaled instead of lost; a connected
  save failure (docket 85's site) falls back to the journal with the
  warning reworded to say so (only a journal failure too earns the old
  "remembered only until this session ends"); a connected startup
  drains the journal into the Well in order BEFORE the history load,
  announcing flushed turns, quarantined damage, and refused drains.
  Corrupt journal files are moved to `pending_episodes/corrupt/`
  (never deleted) and reported.
- Well side: sqlite_vec sets `PRAGMA synchronous = FULL` beside WAL;
  its `add_episode` is now BrunnrError-wrapped with rollback (parity
  with sibling writes + pgvector); both adapters' `recent_episodes`
  skip a single corrupt row (logged by id) instead of failing the
  whole history load.
- Tests: `test_session_persistence_e031.py` **8 passed** (default env);
  `test_episode_corruption_e031.py` **4 passed** (extras shape);
  E-030's save-failure test updated with attribution. Slice gate
  Run B: **781 passed, 6 failed, 15 skipped, 1 warning** — 773 E-030
  baseline + 8 new (corruption file skips in default env); the 6 are
  the proven environment failures. Run D (whole, extras): **827
  passed, 0 failed, 19 skipped, 1 warning**, exit 0. No README touched.
  Pushed under Volmarr's 2026-10-31 standing go-ahead: banking commit 77c75ea
  pushed after fetch + ancestry check — remote moved 383ce69 → 77c75ea, verified
  via ls-remote (remote head = 77c75ea5f55a1e1de8da241d1de6b5add383e753 = local
  HEAD at push time).

## E-032 — The day-one flow (DONE, 2026-10-31)

- Audit filed at `docs/architecture/E-032_DAY_ONE_FLOW.md`: the real flow run
  in a CLEAN venv on the VM profile (system Python's preinstalled PyYAML /
  sqlite-vec would have hidden the headline friction) against a loopback
  Ollama wire-shape server (E-029 pattern; no Ollama daemon on the VM).
  Timed: fresh venv create 26.79 s + pip upgrade 19.92 s (CORRECTION same
  day: the 1.85 s first banked here was a re-run over the existing venv;
  the fresh-create log arrived after banking and supersedes it);
  `pip install <tree>[sqlite_vec]` 19.24 s (wheel
  290,650 B); `ember --help` 0.46 s; day-one `ember ask` (wizard + first
  chat) 1.28 s exit 0; second run 0.93 s. Ollama's own install + model pull
  NOT measured — real-model day one is NOT PROVEN (Part III owns it).
- Three breaks found and FIXED in scope: **(F1) docket 15 CLOSED** — Hjarta
  caught Ctrl-C but not EOF, so closed stdin (`ember ask < /dev/null`)
  died with a raw EOFError traceback; EOF is now a clean abort at the
  current state, nothing written, setup reports it with exit 1.
  **(F2) new docket 88 CLOSED** — the documented install
  (`ember-agent[sqlite_vec]`) has no PyYAML, but Hjarta always wrote
  `ember.yaml`, which the loader cannot read without PyYAML: proven in
  the clean venv, EVERY command exited 1 ("PyYAML is not installed")
  with that file in place — a stranger finished the wizard and lost
  their Ember at the same launch's own reload. The config writer now
  falls back to stdlib-readable `ember.toml` when PyYAML is not
  importable (YAML preferred and unchanged when present; nested
  sections now supported in both formats). **(F3) new docket 87
  CLOSED** — a Well path typed in the wizard was probed, then forgotten:
  the written config carried no trace, so the next chat reopened the
  DEFAULT Well; the choice is now persisted as `brunnr.sqlite_vec.path`
  (the writer docstring's always-promised extras shape), and the
  default writes no override.
- Two text frictions fixed: INSTALL.md's wizard walkthrough omitted the
  tools question (list now matches the wizard, 10 steps, TOML case
  named; §7 notes it too) and the wizard's tools prompt hardcoded the
  `ember.yaml` path (now names the config folder + both filenames).
  F6 recorded, not a defect: the first chat cites Hjarta's probe chunk
  (already disclosed in INSTALL.md).
- Tests: `test_day_one_flow_e032.py` **9 passed** (default env). Slice gate
  Run B: **790 passed, 6 failed, 15 skipped, 1 warning** — 781 E-031
  baseline + 9 new; the 6 are the proven environment failures. Run D
  (whole, extras): **836 passed, 0 failed, 19 skipped, 1 warning**, exit 0.
  No README touched. Pushed under Volmarr's 2026-10-31 standing go-ahead:
  banking commit bfa0e35 pushed after fetch + ancestry check — remote moved
  fad2f1a → bfa0e35, verified via ls-remote (remote head =
  bfa0e35d403dcb54be2503b977b5b2bdf8d1af12 = local HEAD at push time).


## E-033 — Config for humans (DONE, 2026-10-31)

- Filed at `docs/architecture/E-033_CONFIG_FOR_HUMANS.md`: the one config
  surface stated plainly — one file (`~/.ember/config/ember.yaml`, or
  `ember.toml` on a PyYAML-less install, E-032 shape; both present → YAML
  wins with a warning), no file at all = the sane defaults, and an unknown
  key refused at startup BY NAME (the refusal is what makes one surface a
  fact; pinned by test incl. a fossil `openai_api_key`). Thin layers only:
  exactly two env vars (E-013's live keys re-verified in code —
  `OLLAMA_HOST`, `EMBER_WELL_PASSWORD`; Ember loads no .env file), CLI
  flags for one run, persona/identity files as content inside the same root.
- **Docket 55 CLOSED** — `.env.example` rewritten: the Runa fossil (a dozen
  provider/bridge keys to `~/.runa/secrets/runa.env`, zero consumers) now
  documents exactly the two live variables, the no-.env-loading truth, and
  the one config file. **Docket 56 closed for the core** — the template
  `config/ember.example.yaml` now documents EVERY `EmberConfig` field:
  the audit (dataclass-tree walk × template) found `conversation` (E-021),
  `mcp`, `funi.streaming`, `funi.aesir.timeout_ms`, and cognition's
  `expected_api_major` / `num_drafts` / `tf_config` entirely undocumented;
  all now present with plain-words comments + defaults, and a tree-walk
  test fails the gate if any future field is undocumented. The excerpt
  files stopped promising a split: `config/storage.example.yaml` and
  `config/sources.example.yaml` now state they are NOT config files
  (storage = brunnr excerpt of the one file; Smiðja sources are CLI-given,
  no registry). Member half of 56 stays with E-037 as assigned.
- Defaults audited from a constructed `EmberConfig()`, none changed (local
  model/Well, tools/MCP/cognition off, streaming on, pi history window) —
  the defect was documentation + the fossil, not the numbers. Recorded
  behaviour: file-loaded paths are ~-expanded at load by the coercion
  layer's documented design; schema defaults stay unexpanded until use.
- Tests: `test_config_for_humans_e033.py` **6 passed**. Slice gate Run B:
  **796 passed, 6 failed, 15 skipped, 1 warning** (790 E-032 baseline + 6
  new; the 6 are the proven environment failures). Run D (whole, extras):
  **842 passed, 0 failed, 19 skipped, 1 warning**, exit 0. No production
  code changed, no README touched. Pushed under Volmarr's 2026-10-31
  standing go-ahead: banking commit a292b4a pushed after fetch + ancestry
  check — remote moved ea09f17 → a292b4a, verified via ls-remote (remote
  head = a292b4a7a2534942d40bf3458c8995f8f7359a1f = local HEAD at push time).

## E-034 — Logging a friend can read (DONE, 2026-10-31)

- Filed at `docs/architecture/E-034_DIARY_LOG.md`. Beside the technical
  trace (`ember.logging`, for maintainers) Ember now keeps a **diary**:
  `ember.diary.Diary` writes one plain sentence per thing that happened
  into `<config_root>/diary/YYYY-MM-DD.md` (header + `- HH:MM — …`
  entries). Daily files were chosen for tiny hardware: appends are O(1)
  however long Ember has lived, and an old day is a whole file a person
  can remove without parsing anything. Writes are a single O_APPEND
  write + flush + fsync (not the pending journal's tmp+replace — a torn
  diary line loses at most one sentence and stays visible; the choice
  is justified in the module and the doc).
- Chat records, in plain words: session started (identity/persona name
  + model) and could-not-start (persona load failure / model
  unavailable), Well connected vs not reachable, pending-drain outcomes
  (flushed count / damaged files moved aside / failure with turns
  kept), history loaded count or load failure, each turn's outcome
  (answered / answered without memory grounding / interrupted / error
  / truncated — read off the same tags the Episode carries), each
  turn's save outcome (Well / pending journal locally / nowhere), and
  session ended. **No conversation content, by construction**: callers
  pass only facts (counts, names, outcomes) — tests pin the operator's
  words, the reply's words, and drained-episode content absent.
- The diary never harms the session: `record()` returns a bool and
  never raises; chat's wrapper warns **once** on stdout in plain words
  if writing fails. Switch: `logging.diary` (default true) on
  `LoggingConfig`, documented in `config/ember.example.yaml` (E-033
  tree-walk stays green). Reader: `ember diary [--days N]` (default 7)
  prints recent entries flattened with their dates, works even when
  the diary is off, and needs no identity/setup.
- Honest limits (in the doc): tool rounds are NOT diary entries — the
  chat drivers don't surface per-round tool facts to the persistence
  step, and those facts already have a complete home in the tool audit
  log; old diary files are not auto-pruned yet; entry times are local
  with no timezone label; entries are written after the fact they
  describe.
- Tests: `test_diary_e034.py` **13 passed** (default env). Slice gate
  Run B: **809 passed, 6 failed, 15 skipped, 1 warning** — 796 E-033
  baseline + 13 new; the 6 are the proven environment failures. Run D
  (whole, extras): **855 passed, 0 failed, 19 skipped, 1 warning**,
  exit 0. No README touched. Pushed under Volmarr's 2026-10-31
  standing go-ahead: banking commit 0c90949 pushed after fetch +
  ancestry check — remote moved 0c5fc25 → 0c90949, verified via
  ls-remote (remote head = 0c90949ac8589617c3694d2648d7544da2679e3e =
  local HEAD at push time).

## E-035 — Multi-conversation isolation (DONE, 2026-10-31)

- Filed at `docs/architecture/E-035_MULTI_CONVERSATION_ISOLATION.md`.
  E-025's persona discipline applied one level in: episodes now
  carry `conversation_id` (default `"default"` — the namespace
  every pre-E-035 episode already belongs to; slug rules in
  `ember.schemas.conversation`, same shape as persona ids).
  `ember.spark.conversation` holds resolution (explicit choice →
  `conversation.active` config → `default`; an invalid chosen id
  is a typed `ConversationError` and chat stops with the reason
  named, exit 1 — never a silent fall-back to a different talk),
  exact-match filtering, and tagging.
- Chat runs in one conversation: history loads persona filter →
  conversation filter → windowing (in that order, so a foreign
  talk can neither ride verbatim nor leak through the window's
  summary of dropped episodes — fixture-proven), assembly passes
  `conversation_id` to the prompt wall (which composes with the
  persona wall: an episode must be the turn's persona's *and*
  its conversation's; episode context metadata now carries
  `conversation_id`), and every persisted Episode is tagged on
  both the streaming and non-streaming roads. Surfaces:
  `ember chat --conversation <id>` and `conversation.active`
  (documented in `ember.example.yaml`, E-033 tree-walk green;
  TOML coercion pinned). `ember ask` rides the same run and
  inherits the configured conversation. Diary notes a
  non-default conversation in plain words; the pinned E-034
  sentences are unchanged.
- Pending journal (E-031) persists `conversation_id` beside
  `persona_id`; pre-E-035 journal files (no field) load as
  `default`, a non-string field is corruption.
- Honest limits (in the doc): the Brunnr adapters still do not
  persist either tag (the E-025 limit) — cross-restart history
  for a *named* conversation awaits Part V's storage road
  (E-080 family); retrieval grounding (document chunks) is
  shared by design, only remembered turns are private; no
  conversation listing/renaming UI yet.
- Tests: `test_conversation_isolation_e035.py` **42 passed**
  (two named conversations + the untagged past, interleaved;
  adversarial prompt wall; persona × conversation composition;
  summary non-bleed; journal round-trip + legacy payload; two
  sessions on one Well staying apart; disconnected journal
  road; CLI flag). Slice gate Run B: **851 passed, 6 failed,
  15 skipped, 1 warning** — 809 E-034 baseline + 42 new; the 6
  are the proven environment failures. Run D (whole, extras):
  **897 passed, 0 failed, 19 skipped, 1 warning**, exit 0.
  No README touched. Pushed under Volmarr's 2026-10-31 standing
  go-ahead: banking commit f7dce11 pushed after fetch + ancestry
  check — remote moved db2abb9 → f7dce11, verified via ls-remote
  (remote head = f7dce11e86f6842ecfa7e3845981b250a80343b9 = local
  HEAD at push time).

## E-036 — Determinism mode for tests/benchmarks (DONE, 2026-10-31)

- Filed at `docs/architecture/E-036_DETERMINISM_MODE.md`. Before E-036
  generation requests carried conversational sampling (temperature
  0.7) and **no seed at all** — the same prompt could legitimately
  answer differently every run, and there was no one-run way to ask
  otherwise. Built: `DeterminismConfig` under `FuniConfig`
  (`enabled` default False, `seed` default 42, documented in
  `ember.example.yaml`, E-033 tree-walk green) judged in one place,
  `ember.spark.funi.determinism` (`effective_options` /
  `determinism_error`). OFF: effective options are the configured
  ones copied, **no seed key in any request** (wire-pinned on both
  backends — a normal request is byte-identical to pre-E-036). ON:
  every request carries the fixed seed + temperature 0.0 (greedy);
  the configured temperature is never mutated. Ollama gets the
  seed as its `seed` generation option; Aesir as the native
  route's top-level `seed` field (named in its API matrix v1),
  complete + streaming. CLI: `ember --deterministic` /
  `ember --seed N` (seed implies the mode; one run only, never
  saved — the `--allow-tools` overlay shape). A negative or
  non-integer seed in an enabled mode is refused at open as
  typed CONFIG_INVALID before any request (Ollama does not even
  probe; Aesir judges the seed before the key file is read); a
  disabled mode's seed is inert.
- Retrieval determinism, always on (found + FIXED in scope):
  hybrid RRF broke score ties by dict insertion order in BOTH
  Brunnr adapters and the SQL rankings named no tie-break —
  ties now break on chunk_id everywhere (RRF `(-score, cid)`;
  SQL secondary id keys; sqlite_vec vector hits re-sorted in
  Python because **vec0 KNN allows only a single
  `ORDER BY distance`** — the first Run D gate proved it with
  `OperationalError` in 5 tests, fixed and regression-pinned
  the same slice; the KNN k-boundary tie residue is stated
  honestly in the doc). The core uses no `random` module
  anywhere (grep-proven); chunker/summariser are pure.
- Honest limits (in the doc): the mode makes Ember's *requests*
  reproducible — byte-identical answers are the backend's seed
  contract, not Ember's promise; no live model was run (mocked
  transports, E-022/E-023 pattern; live seeded-repeat proof
  belongs to Part III on a named device); timestamps and
  generated ids stay wall-clock/random by design; ThoughtForge
  is not covered (its frozen `think()` takes no seed).
- Tests: `test_determinism_mode_e036.py` **19 passed, 2 skipped**
  (default env; skips = the sqlite_vec fixtures), **21 passed**
  with extras. Slice gate Run B: **870 passed, 6 failed,
  17 skipped, 1 warning** — 851 E-035 baseline + 19 new; the 6
  are the proven environment failures. Run D (whole, extras):
  **918 passed, 0 failed, 19 skipped, 1 warning**, exit 0
  (897 baseline + 21 new). No README touched. Pushed under
  Volmarr's 2026-10-31 standing go-ahead: banking commit
  621a46a pushed after fetch + ancestry check — remote moved
  228b0e4 → 621a46a, verified via ls-remote (remote head =
  621a46a72b7e227979baa8d9ba9e083400d368e8 = local HEAD at
  push time).

## E-037 — Core API freeze v1 (DONE, 2026-10-31)

- Filed at `docs/architecture/E-037_CORE_API_FREEZE.md`. Before
  E-037 the core's public surface was real but scattered
  (curated `__all__` lists beside empty `__init__` files, no
  version a member could check). Built: `ember.api`, the
  freeze registry — `API_VERSION = "1.0.0"` / `API_MAJOR = 1`
  (deliberately separate from the package version, still
  0.2.0; re-exported as `ember.API_VERSION`), `API_V1`'s 63
  individually frozen names + the 12 `ember.schemas.*` modules
  frozen as whole surfaces (92 names) = a 155-entry
  `api_manifest()` computed from the live modules,
  `is_api_compatible(want)` (same major, provider ≥ wanted
  minor/patch, unparseable never binds), and
  `verify_api_surface()` (empty at the freeze in the bare
  default env — the frozen surface needs no optional extra).
  V1 rules stated in the doc: within major 1 a frozen name is
  never removed/renamed/incompatibly re-signed; additions are
  minor bumps, fixes patch, breaks only a major bump with its
  own slice. `ember.well.brunnr`'s empty `__init__` now
  re-exports `BrunnrHandle` + `open`, mirroring Funi (its
  handle-module paths stay frozen too). NOT frozen, named in
  the doc: CLI text/flags, MCP, munnr/hjarta/smidja internals,
  and the concrete adapters (OllamaFuni/AesirFuni/
  SqliteVecBrunnr/PgVectorBrunnr — reached through the frozen
  `open()` registries only).
- **Docket 56 CLOSED** (member half; core half closed at
  E-033): members keep their own config shapes in their own
  homes — the freeze imposes no `ember.yaml` on any member —
  and bind through the API only (version gate → frozen loader
  → frozen schema types → frozen opens), proven by a
  fake-member test binding with no extra installed and no
  config file read. Honest limits in the doc: the freeze is
  contract + gate tests, not import machinery; no member is
  migrated onto it yet (Parts IV–X bind, against this
  contract); name-existence is machine-checked, behaviour
  stays with the per-surface conformance suites.
- Tests: `test_core_api_freeze_e037.py` **33 passed** (default
  env). Slice gate Run B: **903 passed, 6 failed, 17 skipped,
  1 warning** — 870 E-036 baseline + 33 new; the 6 are the
  proven environment failures. Run D (whole, extras):
  **951 passed, 0 failed, 19 skipped, 1 warning**, exit 0
  (918 baseline + 33 new). No README touched. Pushed under
  Volmarr's 2026-10-31 standing go-ahead: banking commit
  d311cc0 pushed after fetch + ancestry check — remote moved
  f45a8ab → d311cc0, verified via ls-remote (remote head =
  d311cc0771be348b67550594e736cb9bd3645fc4 = local HEAD at
  push time).

## E-038 — Concurrency on small hardware (DONE, 2026-10-31)

- Filed at `docs/architecture/E-038_CONCURRENCY_SMALL_HARDWARE.md`.
  Two chats ran at once for the first time (threads, one shared
  Well, barrier-synchronised fake backend so both are provably
  mid-turn together, phone profile: 1024 tokens / 5 episodes per
  session). Three real races on the shared surfaces, all fixed
  in scope: (1) the pending journal's drain double-flushed —
  two starting chats both drained every pending episode into
  the Well twice; drain now claims each file by atomic rename
  (`<name>.claimed-<token>`) before reading it, a refusal
  releases the claim back in order, `kept` counts what actually
  remains; (2) the diary could write a day's header twice —
  size check + write now under an exclusive flock (POSIX;
  previous append behaviour elsewhere), "new" judged by the
  opened file's size; (3) the sqlite_vec Well had no busy
  timeout — `PRAGMA busy_timeout = 5000` at open, so the second
  writer waits instead of failing a save "database is locked".
  Checked and pinned as already safe: journal appends (2×15,
  nothing lost) and the tool audit log (single O_APPEND
  write-all per record).
- Measured (VM profile, fresh process per run, fake backend
  50 ms/turn, 5 turns/chat, histories at the phone cap):
  sequential two chats 1.285 s / 23.7 MiB peak RSS; concurrent
  0.93 s + 0.81 s / 23.9 + 24.2 MiB — the second concurrent
  session costs <0.5 MiB over running the same chats serially.
  Each session's windowed history ≤1024 estimated tokens, two
  together ≤2048 (the phone budget is per-session by
  construction). Honest limits: threads not two OS processes
  (fixes are process-safe by mechanism; Well proof = two
  connections, one file; two-process chat NOT PROVEN); the
  tool registry's Well binding is process-global (named, not
  fixed — one session per process is today's CLI shape, Part
  VIII owns in-process multi-session); no live model served
  either chat, so backend queueing is unmeasured.
- Tests: `test_concurrency_e038.py` **7 passed** (default env)
  + `test_concurrency_well_e038.py` **2 passed** (extras shape).
  Slice gate Run B: **910 passed, 6 failed, 18 skipped,
  1 warning** — 903 E-037 baseline + 7 new; the 6 are the
  proven environment failures. Run D (whole, extras):
  **960 passed, 0 failed, 19 skipped, 1 warning**, exit 0
  (951 baseline + 9 new). No README touched. Pushed under
  Volmarr's 2026-10-31 standing go-ahead: banking commit
  5e9047a pushed after fetch + ancestry check — remote moved
  a151b89 → 5e9047a, verified via ls-remote (remote head =
  5e9047a9cc75be00d7006936a7f9842181712212 = local HEAD at
  push time).

## E-039 — Core docs + runnable examples (DONE, 2026-10-31)

- Filed at `docs/architecture/E-039_CORE_DOCS_EXAMPLES.md`: the
  Part II core-docs index (E-019–E-038 per-slice docs beneath
  the canonical trio) plus the slice's two builds below.
- **Runnable examples, where none existed:** `examples/` held
  only scaffold READMEs whose own law ("examples must actually
  run against the current `src/ember/`") nothing could be
  checked against. Now landed, each runnable from the repo
  root in the bare stdlib-only env, state in a temp folder,
  caller's directory untouched (all pinned by subprocess
  tests): `examples/first_chat.py` (the real `chat.run` loop
  streaming a reply and remembering the turn, against a
  labelled fake model + in-memory Well), `examples/
  member_binding.py` (frozen API v1 only — version gate,
  155-name manifest verified, config via the frozen loader,
  typed refusals, tagging; AST-scanned for frozen imports),
  `examples/offline_turns.py` (Well unreachable → banner,
  pending journal, facts-only diary, then a clean drain),
  and `examples/configs/phone-class.toml` (worked config,
  loads through the frozen loader: phone, 1024 tokens, 5
  turns, diary on). Two first-draft example bugs (a stream
  chunk missing `done`; a config class imported from the
  wrong schema module) were caught by running the examples
  and fixed in the examples — the slice's own argument for
  executing examples, recorded in the doc.
- **Docket 84, DATA_FLOW half — CLOSED:**
  `docs/architecture/DATA_FLOW.md` corrected in place, facts
  only, correction owned at its head: retrieval k=8 → k=5
  (hybrid + text), the nonexistent `AskTurn` type removed
  (the operator's line travels), §7's "no streaming / no
  tool use" negative space rewritten to the shipped truth
  (streaming default + interruptible, E-028; tools off by
  default, approval-gated when enabled, E-026/E-027), and
  §2.2's pending journal drawn as E-031 built it (per-turn
  JSON files, atomic; drained by the next connected session;
  damaged files quarantined, never deleted). Grammar, flows,
  and the Cartographer's voice stand; E-194 owns the
  whole-docs reconciliation.
- **New docket 89** (numbering continues; 87/88 were E-032's):
  the `examples/` scaffold READMEs are stale Runa-era text
  (planned files never written, a loader that does not exist
  here, the folder described as an empty scaffold) — they
  are READMEs, untouchable by this campaign, so the
  correction is assigned to E-195 (README care).
- Honest limits: no live model ran (the fake is by design;
  real-model proof is Part III's E-047/E-049 burden); the
  chat examples drive the operator surface through its test
  seams — `chat` is not frozen API, only the member example
  is held to frozen imports; one worked config, not a fleet.
- Tests: `test_core_docs_examples_e039.py` **8 passed**.
  Slice gate Run B: **918 passed, 6 failed, 18 skipped,
  1 warning** — 910 E-038 baseline + 8 new; the 6 are the
  proven environment failures. Run D (whole, extras):
  **968 passed, 0 failed, 19 skipped, 1 warning**, exit 0
  (960 baseline + 8 new). No README touched. Pushed under
  Volmarr's 2026-10-31 standing go-ahead: banking commit
  a3da82a pushed after fetch + ancestry check — remote moved
  c677a79 → a3da82a, verified via ls-remote (remote head =
  a3da82a95ec8b2948ad8228cdd81abba80379817 = local HEAD at
  push time).

## E-040 — Part II gate (DONE, 2026-10-31)

- Gate filed at `docs/architecture/E-040_PART_II_GATE.md`: **Part II gate
  PASS** on the roadmap's E-040 criteria — all seven gate criteria checked
  (G1–G7). All 21 Part II slices E-019–E-039 banked, their docs present
  under `docs/architecture/` (listing-verified this slice).
- Day-one flow re-proven on the VM profile: targeted tests
  `test_day_one_flow_e032.py` + `test_core_docs_examples_e039.py` +
  `test_core_api_freeze_e037.py` = **50 passed**; the three runnable
  examples (`first_chat.py`, `member_binding.py`, `offline_turns.py`)
  executed directly, each **exit 0**. E-032's clean-venv timings stand
  as the timed record (not re-run, no new timing claimed). Honest limit
  kept: the model is a loopback wire-shape stand-in / labelled fake —
  **a real-model day one is NOT PROVEN** (no Ollama on the VM); Part III
  owns real-device proof (E-047/E-049).
- API freeze checked live in the bare default env: `API_VERSION 1.0.0`
  (= `ember.API_VERSION`), `api_manifest()` **155 entries**,
  `verify_api_surface()` = `()` (no problems),
  `is_api_compatible("1.0.0")` True / `("2.0.0")` False — identical to
  the E-037 freeze.
- Gate re-measurement (E-017 method; logs in
  `~/workspace/.verify-tmp/ember-e040/`): Run A whole/default
  **1 error, 11 skipped, exit 2** (docket 1 unchanged; skips 8 → 11
  explained — Part II added three skip-guarded extras files: E-021
  reader, E-031 corruption, E-038 Well concurrency); Run B default
  excl. pgvector **918 passed, 6 failed, 18 skipped, 1 warning** —
  identical to E-039; Run D whole with extras **968 passed, 0 failed,
  19 skipped, 1 warning**, exit 0 — identical to E-039.
- Docket accounting (§5 of the gate doc): Part II closed 15, 55, 56,
  81, 82, 83, 85, 86, 87, 88, and 84's DATA_FLOW half. Carried forward
  OPEN with named homes, not claimed fixed: **1, 2, 3, 4, 13 →
  E-187/E-200** (Part II owned them on paper but no slice E-019–E-039
  was built to fix them); **20 → E-044** (keyring extra, beside
  lockfile docket 23); 84's remainder → E-194; 89 → E-195.
  Other limits on record: adapters persist neither persona nor
  conversation tag yet (→ E-080 family); ThoughtForge candidate only,
  chat not rewired, no live Aesir/ThoughtForge turn; two-process
  concurrency NOT PROVEN.
- Road check: no re-cut demanded; Part III follows in order, inheriting
  the budget book (E-041), real-device proofs, and docket 20 at E-044.
  Doc-only slice, no code touched, no README touched. Pushed under
  Volmarr's 2026-10-31 standing go-ahead: banking commit 3d79c11 pushed
  after fetch + ancestry check — remote moved 639d96e → 3d79c11, verified
  via ls-remote (remote head =
  3d79c1117d624e7867363487410e21132d22aab5 = local HEAD at push time).

## E-043 — Install weight cut I (DONE, 2026-10-31)

- Doc filed at `docs/architecture/E-043_INSTALL_WEIGHT_CUT_I.md`. The wheel was
  always honest (305 KB, `src/ember` only) but the SDIST dragged the whole
  monorepo: **~45 MB compressed / 127,162,419 B unpacked**, heaviest members
  measured from the tarball itself (mempalace 56,960,935 B — 45 MB of it
  benchmarks/; dictionary 24,075,953 B; Open-VTT 6,251,917 B; Hamr 2,463,468 B;
  Verdandi 1,610,196 B in-sdist vs 16,800,240 B tracked) plus the docs heritage
  corpora (~16.4 MB), the lawbook PDF (11,595,685 B) + Markdown, and
  CAMPAIGN_STATE.md itself.
- The cut is one file: `pyproject.toml`'s sdist exclude list gains every
  optional member directory (11), the docs codex/Mythic-Plan corpora,
  `*.pdf`, the lawbook Markdown and CAMPAIGN_STATE.md. Nothing deleted from
  the repo — an sdist exclude is a shipping decision; members still run from
  a checkout as they always have, now truly optional at install (the core
  never imports any of them; wheel packages, empty core dependencies and
  extras pinned by test).
- After: **sdist 1.1 MB compressed / 3,464,529 B unpacked (a ~41x cut)**,
  364 files; wheel unchanged at 305 KB, so E-041's 978,843 B installed anchor
  and E-042's gate stand unmodified. Clean-venv install FROM the cut sdist
  proven: `ember --help` exit 0, no member in site-packages, installed
  package + dist-info 1,491,175 B incl. install-time bytecode caches.
  The tests' re-derived sdist file set matches hatchling's actual selection
  file-for-file (363; real tarball adds only generated PKG-INFO).
- Tests: `tests/unit/test_install_weight_e043.py` **5 passed** (one defect in
  the slice's own test fixed in scope: plain `git ls-files` quotes the tree's
  two non-ASCII paths — reader now uses `-z`). Slice gate: Run B **941 passed,
  6 failed, 20 skipped, 1 warning** (936 E-042 baseline + 5 new; the 6 are the
  proven environment failures, identical set). Run D **993 passed, 0 failed,
  19 skipped, 1 warning**, exit 0 (988 + 5 new). No README touched.
  Pushed under Volmarr's 2026-10-31 standing go-ahead: banking commit
  ed0fc91 pushed after fetch + ancestry check — remote moved 9bc82f1 ->
  ed0fc91, verified via ls-remote (remote head =
  ed0fc91ccbc5a07bc03699c2aed6a462a39b2f34 = local HEAD at push time).

## E-042 — Budget tests (DONE, 2026-10-31)

- Tests filed at `tests/unit/test_budget_gate_e042.py` (**9 tests**), doc at
  `docs/architecture/E-042_BUDGET_TESTS.md`: E-041's ceilings are now a gate.
  Every test RE-DERIVES its shape in a fresh subprocess (per E-041 §4) and judges
  it against ceilings read live from `ember.budgets` (no second copy): install
  (package tree weighed byte-by-byte: 740,135 B vs toaster 2 MiB and vs the
  978,843 B all-in anchor), idle RAM (CLI surface peak 25.2 MiB; Well-open
  35.9 MiB where sqlite_vec present, honest skip where absent), turn RAM (five
  real chat turns per profile, peaks flat at 24.3 MiB, judged against each
  profile's ceiling AND the toaster's — flatness re-derived), storage (real Well
  683 B/episode over 30 + diary 126 B/turn from two real sessions; projected
  0.46 MiB/month vs toaster 2 MiB). A wiring test pins the file under
  `tests/unit/` so Runs B/D collect it — every future slice gate runs it.
  Sensitivity proven by mutation (toaster turn ceiling shrunk to 1.0 MiB in
  memory → the turn test fails in the book's own words).
- **Measurement bug found by the gate, fixed in scope:** the first whole-suite
  Run D failed 6 of the 9 — every probe reported the identical 71.9 MiB, which
  was the PYTEST process's own peak: on Linux `ru_maxrss` survives exec in the
  signal_struct, so a fork+exec'd probe inherits its parent's high-water mark.
  Probe now reads `/proc/self/status` VmHWM (the child's own mm, resets at
  exec); the failing nine-file reproduction set then passed whole (122 passed)
  and VmHWM re-derivation lands on E-041's numbers (its scripts ran top-level,
  anchors stand). Lesson recorded in the test header + the E-042 doc.
- New docket item 91: re-derived storage 808 B/turn vs the book's 694 (Well
  683 vs 614 at 30-episode scale — page rounding suspected; diary 126 vs ~80
  estimated) — inside the 2× drift band and every ceiling; assigned to E-050
  to re-anchor from a larger-N measurement. No ceiling or anchor changed here.
- Slice gate: Run B **936 passed, 6 failed, 20 skipped, 1 warning** (929
  E-041 baseline + 7 new; the 6 are the proven environment failures; 2 of the
  9 skip bare by their stated sqlite_vec guard). Run D **988 passed, 0 failed,
  19 skipped, 1 warning**, exit 0 (979 + all 9 new). No README touched.
  Pushed under Volmarr's 2026-10-31 standing go-ahead: banking commit
  023de04 pushed after fetch + ancestry check — remote moved d0513b7 →
  023de04, verified via ls-remote (remote head =
  023de04bfeebde1d5f24152fc973e5ccfb67f6b3 = local HEAD at push time).

## E-041 — The budget book (DONE, 2026-10-31)

- Book filed at `docs/architecture/E-041_BUDGET_BOOK.md`, in code at
  `src/ember/budgets.py`: per-profile ceilings (install / idle RAM /
  turn RAM / storage growth per month) for toaster (512 MiB host),
  phone (2,048), pi (4,096), laptop (8,192) — core only, the model
  never folded in. Ceilings: toaster 2 MiB / 64 / 64 / 2 MiB/mo;
  phone 4 / 96 / 128 / 10; pi 8 / 128 / 192 / 25; laptop 16 / 256 /
  384 / 100. History budgets read from E-021's conversation config
  by the book itself (no second copy).
- Measured on the VM (fresh processes, RSS from /proc; scripts +
  logs in `~/workspace/.verify-tmp/ember-e041/`): install **978,843 B**
  all-in (wheel 308,422 B; package 729,802 B = source weight exactly;
  + dist-info + sqlite-vec extra) — the front door's "~50 MB
  installed" is STRUCK (~50× over; the 3.5 GB story is Ollama +
  models, E-197 owns the wording). Idle: CLI surface 25.3 MiB,
  **40.7 MiB with the default Well open** (Well share ~15 MiB).
  Turn: five real chat turns against the real Well, history at cap,
  fake model — **39.4–40.1 MiB peak, flat across all four profiles**.
  The "~50 MB RAM" claim is TRUE and generous (docket 67 measured;
  E-045 re-measures idle over an hour).
- Storage: Well empty 81,920 B, **614 B/episode** over 100 typical
  turns; diary ~80 B/turn; journal 741 B/episode transient (drains,
  not growth) — **694 B/turn, 0.40 MiB/month at 20 turns/day**; the
  toaster ceiling (2 MiB/mo) is reached at ~86 turns/day, stated not
  rounded away.
- Docket 65 measurement half SETTLED: Verdandi's two programs
  measured separately — nerve hub LIVE at **21.9 MiB RSS** (VM,
  status Running), heartbeat import-level **18.4 MiB**; the hub's
  "~1 MB" is not a process figure; wording fix stays E-060's, load
  truth E-075's. Docket 66 SETTLED by replacement: Tiny's
  622 MB sum / 350 / 400 caps replaced for the shipped core
  (toaster host 512, core turn ceiling 64); the honest sum OS 150 +
  core 64 + smallest model ~300 = ~514 MB — marginal on 512 MiB,
  E-049 grades the real device. Docket 68 recorded with scopes for
  Part IX; 69 superseded for the core (member table stays E-057);
  70's member rows stay E-057/E-078/E-103. New docket 90: anchors
  are VM-only — E-047/E-048/E-049 re-anchor per device, E-042's
  tests pin the VM anchors and must be re-derived if a device
  anchor moves a ceiling.
- Tests: `test_budgets_e041.py` **11 passed** (anchors pinned at
  measured values so they cannot be quietly "adjusted"; the
  measured shape fits every profile incl. toaster; one test bug
  of the slice's own — a 200-turns/day storage assertion that
  exceeded the toaster ceiling — caught by the runner and
  corrected to state the true bound). Slice gate Run B: **929
  passed, 6 failed, 18 skipped, 1 warning** — 918 E-040 baseline
  + 11 new; the 6 are the proven environment failures. Run D
  (whole, extras): **979 passed, 0 failed, 19 skipped, 1
  warning**, exit 0. No README touched. Pushed under Volmarr's
  2026-10-31 standing go-ahead: banking commit 1530961 pushed after
  fetch + ancestry check — remote moved aeceeb1 → 1530961, verified
  via ls-remote (remote head =
  1530961e6d3dd24cc0c8aade9f54761bd7cfd6a0 = local HEAD at push time).

## E-045 — Idle discipline (DONE, 2026-10-31)

- Record filed at `docs/architecture/E-045_IDLE_DISCIPLINE.md`: four profile
  probes (full CLI/chat surface imported, profile config loaded, real
  sqlite_vec Well open, blocked on stdin as `chat` waits) idled concurrently
  for 3,600 s on the VM, sampled every 30 s (121 samples; scripts + raw
  samples in `~/workspace/.verify-tmp/ember-e045/`).
- Headline: **zero CPU** (each probe's CPU ticks identical first→last sample;
  0.0 s over the hour), **exactly 1 thread** throughout, **disk
  byte-identical** (164,616 B at every sample), and RSS **never grew at any
  sampled step** — it declined monotonically from ~40.8 MiB to a 23.0 MiB
  floor reached at ~1,261 s and held flat; HWM never exceeded ~40.9 MiB,
  inside the toaster's 64 MiB idle ceiling. All four probes exited 0.
  Mechanism for the RSS decline is NOT claimed (probes did no work; stated
  as observation in the doc). A 60 s rehearsal run showed the same shape.
- Gate armed: `tests/unit/test_idle_discipline_e045.py` — 5 tests (4 profile
  probes at 15 s gate scale: CPU ≤2 ticks, 1 thread, RSS inside ceiling +
  1.5× anchor band, settled wander ≤2 MiB, disk byte-identical; + wiring).
  Extras shape standalone **5 passed**; default env 4 skip (reason stated)
  + 1 passed. No `src/` code changed — the discipline was already the
  code's behaviour; no defect found, no new docket items (90 stands).
- Slice gate: Run B **949 passed, 6 proven-environment failures,
  24 skipped, 1 warning** (948 E-044 baseline + 1 new; 4 new skips as
  designed); Run D (whole, extras) **1005 passed, 0 failed, 19 skipped,
  1 warning**, exit 0. CORRECTION (same day): Run D was first banked as
  "1022 passed, 20 skipped" from a foreign background result, not this
  run's log — no run produced that figure; the log-verified count is
  1005/0/19 (422.99 s), reconciling exactly with the Run D line
  988 (E-042) + 5 (E-043) + 7 (E-044) + 5 (E-045). Corrected here and in
  the E-045 doc by the correction commit (E-012 precedent). No README
  touched. Pushed under Volmarr's 2026-10-31
  standing go-ahead: banking commit 6d99acc pushed after fetch + ancestry
  check — remote moved ee38f38 → 6d99acc, verified via ls-remote (remote
  head = 6d99acc256ac9ce235d730720d0df71374787c19 = local HEAD at push time).

## E-046 — Cold start on the smallest profile (DONE, 2026-10-31)

- Record filed at `docs/architecture/E-046_COLD_START.md`: cold start to
  first word measured on the toaster profile — seven fresh
  `python -m ember ask` processes (real CLI, real config file, real
  sqlite_vec Well, loopback wire-shape model answering instantly, so the
  number prices Ember's own startup, not a model's thinking; real-model
  cold start NOT PROVEN). First word: **median 2.87 s, min 1.28, max
  5.38** on a heavily contended VM (5-min load ~8; stated in the doc —
  the anchor is a contended median; E-032's quiet-machine whole ask was
  0.93 s). Ready line at median 2.79 s: **~97% of cold start is process
  startup** (interpreter, imports, config, Funi probe, Well open,
  history load); the turn itself adds ~0.09 s. First-ever start (Well
  creation included) 3.60 s, also inside the cap.
- The cap, in the book (`src/ember/budgets.py`): new anchor
  `MEASURED_COLD_START_FIRST_WORD_S = 2.87` (test-pinned) and
  `ProfileBudget.cold_start_first_word_s = 5.0` **flat across all four
  profiles** (~1.7× the anchor; starting is the same process on every
  profile — no machine size is granted a slower start).
  `check_against` gains an optional fifth judgement in the book's
  sentence shape; `measured_shape_fits` includes the anchor, so the
  founding fact covers cold start. E-041's tests stand unmodified.
- Gate armed: `tests/unit/test_cold_start_e046.py` — 4 tests (book/cap
  pinning, check_against wording, wiring, and the measurement: setup
  run + 3 fresh cold processes, judged by their MEDIAN against the
  cap — a single contention spike cannot flake it, a real startup
  regression moves all three). Default env 3 passed + 1 skip (reason
  stated); extras 4 passed.
- **Defect found by this slice's gate, fixed in scope:** the first
  Run D failed E-045's idle tests (3 of 4 profiles) on RSS "wander" —
  the settled samples *declined* 4.4–9.7 MiB inside the 15 s window
  under memory pressure, and the max−min assertion treated any
  movement as a violation, contradicting E-045's own proven hour
  (monotonic decline 40.8 → 23.0 MiB is the normal idle behaviour).
  The assertion now judges **growth past the first settled sample**
  at the same 2 MiB bound, reason recorded at the assertion;
  standalone re-run 9 passed (idle 5 + cold-start 4).
- Slice gate (final tree; logs in `~/workspace/.verify-tmp/ember-e046/gate/`):
  Run B **952 passed, 6 proven-environment failures, 25 skipped,
  1 warning** (949 E-045 baseline + 3 new, +1 designed skip); Run D
  **1009 passed, 0 failed, 19 skipped, 1 warning**, exit 0 (1005 + 4
  new — reconciles exactly). The pre-fix first Run D read 1006/3, the
  3 being exactly the wander failures. No new docket items (90 stands,
  now covering the cold-start anchor). No README touched. Pushed under
  Volmarr's 2026-10-31 standing go-ahead: banking commit ea930a5 pushed
  after fetch + ancestry check — remote moved ad18ee5 → ea930a5,
  verified via ls-remote (remote head =
  ea930a5b0628b7e1593c8b67093c025fc18364de = local HEAD at push time).

## E-047 — The Pi proof (DONE, 2026-10-31)

- Proof filed at `docs/architecture/E-047_PI_PROOF.md`: **PROVEN on a
  real Pi with a real model.** Device: Mimir (`purpleviking1`), Raspberry
  Pi 5 Model B Rev 1.1 (aarch64, 16 GiB, Python 3.11.2), Ollama 0.20.5
  resident. Ember cloned fresh at fae0e0b (hash-verified on-device),
  installed into a clean venv (`pip install ./repo` + sqlite-vec 0.1.9),
  run on the `pi` profile against the default model pair — phi3:mini
  chat, nomic-embed-text embedding (pulled for the proof) — real
  sqlite_vec Well on device storage, all in `/home/pi/ember-e047/`.
- Numbers (probe on-device, fresh `ember ask` processes): first-ever
  run (Well created, model cold) rc 0, whole ask 64.91 s; three judged
  warm runs — ready median **0.18 s**, first word median **5.69 s**
  (5.17–6.37), peak RSS **27.1 MiB** every run. Memory proven across
  processes: run 3, asked what the first question was, accurately
  summarised the first-ever greeting. Installed core on-device
  1,951,508 B (caches incl.) — inside the pi 8 MiB install ceiling and
  the toaster's 2 MiB alike; RSS inside even the toaster's 64 MiB.
  Ollama's runner (~3.7 GiB with phi3 loaded) is the model's cost,
  charged to no Ember ceiling. Device temp after runs 44.4 °C.
- The split, kept clean: E-046's flat 5.0 s cap prices Ember's own
  startup; the Pi re-anchor is **ready 0.18 s** (~28× inside the cap —
  cap stands unrelaxed, docket 90's Pi half settled by re-derivation).
  The 5.69 s first word is phi3:mini thinking on a Pi CPU — a model
  cost, pinned as its own anchor (`MEASURED_PI_FIRST_WORD_REAL_MODEL_S`)
  and deliberately NOT judged against the cap. Four Pi anchors added
  to `ember.budgets`, pinned by `tests/unit/test_pi_proof_e047.py`
  (5 tests). E-032/E-040's "real-model day one NOT PROVEN" is closed
  for the Pi. Not claimed: on-device wizard (identity pre-written,
  E-046 convention), Pi idle hour, toaster-device verdict (E-049).
- Probe defect found and fixed in-slice (own tooling, not product):
  probe v1 timed the chat banner as "first word" on the first-ever
  run; caught from its own output, fixed to time the first content
  after the banner's prompt mark, first-ever first-word left
  unrecorded and stated as such in the doc.
- Slice gate: Run B **957 passed, 6 failed, 25 skipped, 1 warning**
  (952 E-046 baseline + 5 new; the 6 are the proven environment
  failures, identical set). Run D **1014 passed, 0 failed, 19
  skipped, 1 warning**, exit 0 (1009 + 5 new). No README touched.
  Pushed under Volmarr's 2026-10-31 standing go-ahead: banking commit
  5dcd1e8 pushed after fetch + remote check (remote was fae0e0b =
  local HEAD, no divergence) — remote moved fae0e0b → 5dcd1e8,
  verified via ls-remote (remote head =
  5dcd1e815124e099b7309f48cb1afef3733bd382 = local HEAD at push time).

## E-048 — The phone-class proof (DONE, 2026-10-31)

- Proof filed at `docs/architecture/E-048_PHONE_PROOF.md`: **Proof grade
  SIMULATED — proven in a phone-shaped room, not on a phone.** The phone
  conversation profile ran on the campaign VM under a stated simulation
  envelope: each fresh `ember ask` process pinned to 2 CPUs, a 512 MiB
  RSS watchdog (the slice of the book's 2,048 MiB phone host left after
  OS + the smallest model rung; never triggered), loopback wire-shape
  model answering instantly (E-046 shape — numbers price Ember, never a
  model's thinking), heavily contended VM (1-min load 6.0 → 7.6).
- Numbers (probe + wire capture in `~/workspace/.verify-tmp/ember-e048/`):
  first-ever run (Well created) ready 3.89 s / first word 3.92 s — inside
  the flat 5.0 s cap; three judged runs — ready median **1.77 s**, first
  word median **1.79 s** (1.49–3.01), peak RSS **43.0 MiB** max, all
  rc 0, no envelope breach. Config root grew 870 B over the three judged
  turns. Phone ceilings all fit: install 0.93 MiB / 4, RSS 43.0 / 96 idle
  + 128 turn, first word vs the unrelaxed 5.0 s cap, storage projection
  0.40 MiB/mo / 10.
- Memory proven at the wire: the stand-in server's capture shows each
  later process's request carrying the earlier exchanges verbatim (the
  recall run's prompt held the first run's "teal" fact); the diary
  records 1 → 2 → 3 earlier exchanges loaded from the on-disk Well by
  fresh processes. Semantic recall spoken by a real model stays E-047's
  Pi proof.
- NOT PROVEN, named: any real phone — the house's Galaxy S26 Ultra is
  paired but was offline when checked (last seen 2026-10-31 00:44 UTC)
  and the tree holds no Android runtime/install path for the core (the
  Tab S10 Lite, also offline, has the same bar); a real model on
  phone-class silicon; thermals/battery (E-053); at-cap windowing
  (history reached 3 of 5 episodes; at-cap is E-021/E-038's proof);
  the on-room wizard (identity pre-written, E-046 convention). The
  whole-phone sum (turn ceiling 128 MiB + smallest model ~600 MiB of a
  2,048 MiB host) is stated as arithmetic, not proof.
- Three SIM anchors added to `ember.budgets`
  (`MEASURED_PHONE_SIM_READY_S` 1.77, `MEASURED_PHONE_SIM_FIRST_WORD_S`
  1.79, `MEASURED_PHONE_SIM_PEAK_RSS_MIB` 43.0), pinned by
  `tests/unit/test_phone_proof_e048.py` (5 tests, incl. the grade guard
  keeping SIM anchors distinct from the Pi's real-device anchors).
  Docket 90's phone half settled at simulation grade — weaker than
  E-047's real-device re-anchor, recorded as such; ceilings unrelaxed.
  No defect found, no new docket items. No README touched.
- Slice gate: Run B **962 passed, 6 failed, 25 skipped, 1 warning**
  (957 E-047 baseline + 5 new; the 6 are the proven environment
  failures, identical set). Run D **1019 passed, 0 failed, 19 skipped,
  1 warning**, exit 0 (1014 + 5 new — reconciles exactly). Pushed under
  Volmarr's 2026-10-31 standing go-ahead: banking commit 96fb9a2 pushed
  after fetch + ancestry check — remote moved 632a0a0 → 96fb9a2, verified
  via ls-remote (remote head =
  96fb9a2ae7492356321a57fa0dd707cc028446a9 = local HEAD at push time).

## E-050 — Storage growth (DONE, 2026-10-31)

- Record filed at `docs/architecture/E-050_STORAGE_GROWTH.md`: a month of
  companionship simulated against the real stores on the VM (script + raw
  results in `~/workspace/.verify-tmp/ember-e050/`): the real sqlite_vec Well
  at the production embedding_dim=768 (episodes carry text only), 30 days ×
  20 turns of E-041's typical fixture (600 episodes, closed and weighed
  after every day), then the same store grown to 3,000 episodes; the real
  Diary over 30 daily files in chat's connected shape; a separate 60-turn
  essay Well (~500 words a side).
- Headline: **the month grew 408,566 B in all (0.39 MiB, 680.9 B/turn
  all-in)** — Well 352,256 B (81,920 B empty → 434,176 B; 587.1 B/episode
  over the month, steady marginal **585.4 B/episode** flat across 600→3,000,
  growth purely in 4 KiB page steps, no superlinear component; retrieval
  proven at day 30) + diary 56,310 B (93.85 B/turn all-in, 85 B marginal).
  Judged per profile: fits EVERY storage ceiling — 5.1× headroom on the
  toaster (2 MiB/month); break-even ~103 turns/day on the toaster; a
  100-turns/day month totals ~1.92 MiB (inside, barely, stated); a year at
  reference pace is 4.68 MiB. **No ceiling moves; the lifecycle rules do
  NOT tighten** — the roadmap's either/or resolves to within-budget.
- **Docket 91 CLOSED:** E-042's 808 B/turn was small-N page rounding
  (683 B/episode over 30 episodes; at 600 the average is 587.1, under the
  book's 614) plus its diary session shape (126 B/turn from ungrounded
  lines + session notes over 5 turns). The book's 694 B/turn stands
  unrevised — the month measured 680.9, inside it; six E-050 anchors added
  to `ember.budgets` record the month beside the book.
- The honest edge, pinned both ways: essay-length turns cost **6,144
  B/episode** (N=60); a reference-rate month of them is **3.51 MiB — past
  the toaster's ceiling** (break-even ~11 essay turns/day), inside the
  phone's. E-082 inherits the quantified lifecycle brief: nothing to prune
  for years at reference use; its real subjects are the long-turn store
  and the diary's one-file-per-day count (365 files/year, trivial bytes).
  No defect found, no new docket items. No README touched.
- Slice gate: Run B **975 passed, 6 failed, 25 skipped, 1 warning**
  (968 E-049 baseline + 7 new; the 6 are the proven environment failures).
  Run D (whole, extras) **1032 passed, 0 failed, 19 skipped, 1 warning**,
  exit 0 (1025 + 7 new — reconciles exactly).
- E-050 push: banking commit b357b42 pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + remote-diff (remote was b2d5db6 = prior
  local HEAD, no divergence) — remote moved b2d5db6 → b357b42, verified
  via ls-remote (remote head =
  b357b42911dd8b06cfa8c8383d41a1ddba5219f1 = local HEAD at push time).

## Slice ledger

- E-001 DONE (2026-10-30) — opening: clone, branch, roadmap filed + filing push verified, state file, opening baseline.
- E-002 DONE (2026-10-30) — member census in depth, filed at docs/audit/E-002_MEMBER_CENSUS.md.
- E-003 DONE (2026-10-30) — ORIGINS concordance, filed at docs/audit/E-003_ORIGINS_CONCORDANCE.md.
- E-004 DONE (2026-10-30) — fresh baseline I: whole root suite classified; with extras 583 passed / 0 failed, filed at docs/audit/E-004_FRESH_BASELINE_I.md.
- E-005 DONE (2026-10-30) — fresh baseline II: per-member truth table; seidr green, bulk of failures proven environment (proxy-env httpx signature), 8 new docket items (machine-coupled tests family), filed at docs/audit/E-005_FRESH_BASELINE_II.md.
- E-006 DONE (2026-10-30) — boot census: Verdandi hub + Mímir's Eye proven LIVE, seidr boots+computes bare, ember diagnostics crash bare on the sqlite_vec default backend, astrology/dictionary/Open-VTT cannot boot here for named reasons, 5 new docket items (13–17), filed at docs/audit/E-006_BOOT_CENSUS.md.
- E-007 DONE (2026-10-30) — dependency & licence audit: estate permissive + intact (11 MIT verified, astrology Apache-2.0, no copyleft in tree), CloakBrowser binary licence is proprietary (no redistribution/bundling without OEM — constraint, not violation), 4 declaration-vs-reality gaps + metadata/lockfile gaps, 8 new docket items (18–25), filed at docs/audit/E-007_DEPENDENCY_LICENCE_AUDIT.md.
- E-008 DONE (2026-10-30) — the codex census: four elder codices DONE-in-fact (Hermes 58 total, Chatdoll 69, SAP 83, Waifu 21 — every content doc present with its Ember closer, none under its word floor), Ragnarok scaffold-only with 0/46 content docs, all five TASK status lines stale, no codex referenced in src/, 5 new docket items (26–30), filed at docs/audit/E-008_CODEX_CENSUS.md.
- E-009 DONE (2026-10-30) — the Verdandi concordance: v0.3.0 Skuld proven in code + 35/35 dedicated tests, Vör broken in 3 places (docket 31 expands item 7), pulse_metrics write-only, v0.4 distributed/REST absent and Prometheus/emotion double-listed, VD-RM covers heartbeat only, 7 new docket items (31–37), filed at docs/audit/E-009_VERDANDI_CONCORDANCE.md.
- E-010 DONE (2026-10-31) — the Hamr verification plan: every Ph1–17 claim mapped to its proving artefact + method + environment (runner-only counts, symbol-existence rule); Phase 6 has no claim anywhere, Phase 14 no COMPLETE artefact, Phase 17 a vision with no .vrm in tree, MaterialForge/CollisionForge/PoseLibrary absent as named, Ph15 CI promotion check false in-tree, count spine self-contradictory vs E-005; execution bucketed to E-138/E-139/E-140; 8 new docket items (38–45), filed at docs/audit/E-010_HAMR_VERIFICATION_PLAN.md.
- E-011 DONE (2026-10-31) — the two-Kistas boundary doc: toaster-Kista (in-tree, v2.0.0, Fernet vault.json.enc, 14 entry types, zero root consumers) vs ai-folder Kista (purplelongship, standalone GitHub line, Runa/Hermes custody, Heimdall's vault) separated with 8 binding custody rules; 6 conflation hazards found (default ~/.hermes vault home in code, Verdandi's third vault.db shape, tests judging the ~/.hermes copy — re-proven 146 passed / 3 failed, known-accounts ledger in-tree, Yggdrasil aspirational shape, shared v2.0 label); ai-folder side graded RECORDED not MEASURED; 5 new docket items (46–50), filed at docs/audit/E-011_TWO_KISTAS_BOUNDARY.md.
- E-012 DONE (2026-10-31) — the two-memories census: mempalace (verbatim archive, Chroma+ONNX, 59.2 MB, MCP 30 tools) vs mimir-well (living SQLite memory, decay/validity/guard, 638 KB, FTS5 only); shape-overlap with zero shared code/format; NEITHER consumed by the core (its own Brunnr Well is the third memory); in-tree consumers Verdandi check (path agrees) + bifrost bridge (Hermes path — three Mímir DB defaults, docket 51); UNWIRED mempalace line stale (52); suites re-proven mimir 350/6 (item 10 re-proven, 53; first-banked 356/0 figure corrected same day) and mempalace 1712/14/0 file-verified (E-005 bulk environment-shaped, 54; first-banked 1669/90/39 corrected same day), filed at docs/audit/E-012_TWO_MEMORIES_CENSUS.md.
- E-013 DONE (2026-10-31) — config & secrets census: no real credential in any plain file (all high-confidence hits classified fixtures/placeholders/false positives over 2,754 tracked text files); core Well-secret resolver (env → keyring → mode-600 file) is the tree's model shape; `.env.example` proven a Runa fossil with zero src consumers (docket 55); ≥7 config shapes across members (56); scanner-indistinguishable synthetic fixtures (57); CloakBrowser URL-embedded proxy credentials as a never-adopt boundary (58); known-accounts ledger re-verified, stays docket 48, filed at docs/audit/E-013_CONFIG_SECRETS_CENSUS.md.
- E-014 DONE (2026-10-31) — dead/duplicate census: only 11 non-trivial exact-duplicate groups (4,312,510 wasted B, 1,392,520 intentional logo distribution; 2,919,990 accidental/generated/broken), zero dead core modules (50/50 referenced; AST zero sibling imports), no duplicated non-empty .py anywhere; Verdandi heartbeat 2,548 unwired Runa lines (59), four 1-byte pseudo-PNGs (60), tracked Godot .tmp + Hamr build_output artefacts (61), cross-member image/text triplication 2,886,896 B (62), 25-byte UX-codex stub (63), 13-file Markdown-only shells (64); TUI tree + Runa archive dormant-by-design, ADR-0012 explained as UNWIRED placeholder, filed at docs/audit/E-014_DEAD_DUPLICATE_CENSUS.md.
- E-015 DONE (2026-10-31) — budget archaeology: 1,264 numeric size lines classified; only Hamr has an enforced budget (perf.py 1.5 GB/45 s, tiers 512 MB–1.5 GB); core ~50 MB disk/RAM + Well 50 MB claims unmeasured, scope = installed core not the 217 MB monorepo (67); Verdandi six conflicting RAM figures, hub vs heartbeat unseparated (65); Tiny proposal ~622 MB on 512 MB target, self-annotated over budget, 350 vs 400 MB cap conflict (66); Hamr Phase 17 second budget 7.5 GB/143 MB (68); sibling-matrix estimates unsourced (69); five members with no budget at all (70); Stofa's named budget tests absent from tree (71); vendored CloakBrowser ~190 MB idle recorded for E-179; code-enforced limits catalogued, filed at docs/audit/E-015_BUDGET_ARCHAEOLOGY.md.
- E-016 DONE (2026-10-31) — the bug & gap docket: every Part I carried item numbered, classified, and assigned in one table (80 entries covering 79 distinct issues; items 1–71 preserved exactly as E-004–E-015 assigned them, continuous with no gap or duplicate — verified from the extracted carried sections; items 72–80 first-numbered here for the pre-numbering E-002/E-003 findings and the unnumbered open measurements: ORIGINS register gap, drift detector never built, ADR-sequence silence, IMG provenance/UUID names, vendor/config register mismatches, astrology + Open-VTT zero test suites, dictionary Jest NOT MEASURED, unregistered 22-file root image population, CloakBrowser vendored-suite record); item 53 is a re-observation of 10, not a distinct defect. Owner tally sums to 80 (Part IV largest at 13, Part IX 11, Part II 9). Cross-links recorded (31 expands 7; 13 is the boot face of 2; 16/18 two halves; the five-entry machine-coupling family 5/8/10/17/11). Volmarr's word required for 26, 48, and the removal halves of 60/62/63/64; NOT PROVEN honestly at 40, 44, 78 and item 12's residue. Filed at docs/audit/E-016_BUG_GAP_DOCKET.md.
- E-017 DONE (2026-10-31) — baseline freeze: the campaign's zero line pinned at docs/audit/E-017_BASELINE_FREEZE.md, measured at HEAD 37fc2f2 (3,246 tracked files; VM, Python 3.12.3, pytest 9.1.1). Root suite re-measured in full this slice, all three shapes IDENTICAL to E-004/E-001: Run A whole/default interrupted at collection (1 error, 8 skipped, exit 2 — docket 1); Run B default excl. pgvector file **546 passed, 6 failed, 12 skipped, 1 warning**; Run D whole with extras **583 passed, 0 failed, 19 skipped, 1 warning**, exit 0 (counts frozen; wall time is not). Per-member truth table pinned from E-005 as corrected by E-012 (seidr 38 green; kista 146/3; Verdandi 539/19; mimir-well 350/6; bifrost 18/7; Hamr 2170/28/33/2E; mempalace corrected 1712/14/1/106-desel/0E with volatility caveat docket 54; CloakBrowser vendored 385/39/15E, docket 80; dictionary NOT MEASURED docket 78; astrology + Open-VTT no suites docket 77). Boot zero line pinned from E-006 with key rows re-probed identical this slice (ember --help exit 0, seidr composes exit 0, ember doctor bare still crashes on sqlite_vec docket 13; Verdandi hub + Mímir's Eye LIVE-proven in E-006). Keeper re-measurement method recorded in the freeze doc (Run B is the per-slice gate; Runs A/D at part gates and on docket 1–4 touches; TMPDIR on workspace overlay always; counts from runner logs only). MCP/Ollama/podman/Gungnir-guarded tests NOT PROVEN — guarded, not passed. Doc-only slice, no code touched, no README touched.
- E-018 DONE (2026-10-31) — Part I gate PASS: audit published in-repo (16 docs, E-002–E-017, under docs/audit/), verdicts prepared (not executed) for every member (all KEEP / KEEP-STEWARD / KEEP-PENDING-VERDICT; nothing removed, merged, or retired), the six gate-owned docket items verdict-prepared (52, 60, 62, 63, 64, 71 — removals/folds in 60/62/64 await Volmarr's word, as do 26 Ragnarok and 48 known-accounts custody; none blocks Part II), plain-language summary filed, and the road checked against five re-cut triggers with NO structural re-cut demanded (four sharpenings S1–S4 recorded). Gate re-measurement identical to the E-017 freeze in all three shapes (A: 1 error/8 skipped; B: 546 passed/6 failed/12 skipped/1 warning; D with extras: 583 passed/0 failed/19 skipped/1 warning). Filed at docs/audit/E-018_PART_I_GATE.md. **Part I (E-001–E-018) is CLOSED.**
- E-019 DONE (2026-10-31) — core loop mapped: entry → startup (Funi first, Well second) → retrieve k=5 → assemble (system + last-5 in-process episodes + hits, no token budget) → Ollama streaming generation → ≤8-round tool loop → render → Episode persist, all drawn from code at docs/architecture/E-019_CORE_LOOP_MAP.md; no event bus / no other member in the loop; six new docket items 81–86 (episodes write-only with no cross-restart history, pending-episodes journal unimplemented, non-streaming tool calls dropped, DATA_FLOW drift, silent persistence and retrieval failures), each with its Part II fixing home named.
- E-020 DONE (2026-10-31) — tethering made explicit: three tethers specified from code at docs/architecture/E-020_TETHERING_SPEC.md (person = one config root, identity name+role only, no account/person record, env surface exactly OLLAMA_HOST + EMBER_WELL_PASSWORD; machine = localhost Ollama/embedder defaults, one implemented runtime with typed Unavailable for the rest, `~` unexpanded until use, tools/MCP off by default; memory = Well only via Strengr, 3 attempts / 30 s cap / fast-fail set / health never raises / typed Disconnected), the hard-model vs soft-memory startup asymmetry named, Hjarta as the binding ceremony, and T-W6's honest centre (Episodes write-only, docket 81/82 → E-021/E-031); 13 new spec-pinning tests in tests/unit/test_tethering_e020.py all passing; plain-language statement added to docs/OPERATOR_PLAYBOOK.md and its Recipe 10 conversation-recall overclaim found and fixed in scope; slice gate 559 passed / 6 proven-environment failed / 12 skipped / 1 warning.
- E-021 DONE (2026-10-31) — conversation engine hardening: episode reader on the Brunnr protocol + both adapters (docket 81 CLOSED — history survives restarts for connected sessions), profile-aware token-budget windowing (ConversationConfig: toaster 512/3, phone 1024/5, pi 2048/8 default, laptop 4096/12; caps + budget, newest always kept, dropped always reported), Summariser hook protocol with a deterministic model-free extractive default riding as ContextKind.SUMMARY, chat startup history load + per-turn windowing replacing the fixed [-5:]; 15 + 4 new tests; gate Run B 574 passed / 6 proven-env failed / 13 skipped, Run D with extras 615 passed / 0 failed; docket 82 stays E-031's, filed at docs/architecture/E-021_CONVERSATION_HARDENING.md.
- E-022 DONE (2026-10-31) — model backends: `BackendCapabilities` + `StreamingMode` declared in schemas and added to the FuniHandle protocol; `backend_registry()`/`capabilities_for()` publish per-runtime truth (Ollama the only implemented backend: native streaming, tool calls model-dependent, token counts yes, RAM never reported, all context kinds; the other four runtimes capability-free and typed-Unavailable); 16 conformance tests in test_backend_contract_e022.py incl. a WRAPPED complete-only fake; FUNI_LOCAL_MODEL_OPTIONS §4 drift (/api/generate, embed(), 127000 tokens) fixed in scope; gate Run B 590 passed / 6 proven-env failed / 13 skipped, Run D 631 passed / 0 failed; filed at docs/architecture/E-022_BACKEND_CONTRACT.md.
- E-023 DONE (2026-10-31) — Aesir backend for Ember: Project Aesir bound under E-022's contract in its native mode only (POST /v1/generate, loopback :18434, bearer key from a key *file* — config carries the path, never the value, and no detail/log ever echoes key material); FuniRuntime.AESIR + FuniAesirConfig (max_tokens default 256 = the service's own ceiling); context flattened to prompt+system (each generation resets history server-side); tools refused as ERROR replies, never dropped (capabilities tool_calls=False); native streaming, EOF-without-terminal = ERROR; finish mapping eos→STOP / timeout→LENGTH; registry implemented set now [OLLAMA, AESIR] with E-022's tests updated under attribution; 26 new tests; gate Run B 616 passed / 6 proven-env failed / 13 skipped, Run D 657 passed / 0 failed. Ledger respected: no accelerator claim from the server's backend field, and a live end-to-end turn against a running Aesir service is NOT PROVEN (mocked transport only), filed at docs/architecture/E-023_AESIR_BACKEND.md.
- E-024 DONE (2026-10-31) — ThoughtForge binding (candidate): MindSpark ThoughtForge bound as Ember's cognition layer above Funi, against TF's own TF-034 freeze (cognition API v1.0.0); CognitionConfig off by default with a stated profile gate (toaster refused outright; phone/pi draft cap 1, laptop 2, per TF-034's by-construction maxima); lazy optional import (zero new core deps — absent package = typed RUNTIME_NOT_INSTALLED, proven in the default env); API-major/drift truthful refusal via API_VERSION + verify_api_surface() (TF-162's rule, Ember side); core custody inside ~/.ember/thoughtforge/ (E-020 tether), tf_config passed through unshadowed, Episodes → TF's own ChatHistory on the frozen history parameter; chat NOT rewired (candidate), no live TF turn claimed (fake core shaped from the freeze, TF-161 pattern), no budgets claimed; 23 new tests; gate Run B 639 passed / 6 proven-env failed / 13 skipped, Run D 680 passed / 0 failed; filed at docs/architecture/E-024_THOUGHTFORGE_BINDING.md.
- E-025 DONE (2026-10-31) — persona core: validated `Persona` schema (slug id never a path, field ceilings, no prompt-line smuggling via line breaks/control chars), strict per-persona JSON loading under `<config_root>/personas/` (typed refusals, filename/id agreement, no silent swap), resolution explicit → default.json → identity-as-default-persona, `PersonasConfig.active`; per-persona memory separation via `Episode.persona_id` + exact-match filtering with the prompt assembler as the wall (adversarial foreign-episode fixture never reaches the prompt), chat sessions resolve/filter/tag by persona, and the `load_identity` non-object-JSON AttributeError crash fixed in scope; honest limit: Brunnr adapters do not yet persist the tag (fails closed — named personae have no cross-restart history yet; migration belongs to Part V/E-080); 38 new tests; gate Run B 677 passed / 6 proven-env failed / 13 skipped, Run D 718 passed / 0 failed; filed at docs/architecture/E-025_PERSONA_CORE.md.
- E-026 DONE (2026-10-31) — tools discipline: every descriptor states its permission shape (`ToolAccess` + `guarded_arguments`; unspecified = gated dangerous), the live-registry inventory pinned by test (search_well private_read/standing, read_local_file private_read/per_call, fetch_url network/per_call with guarded `allow_private_addresses`; no first-party write/execute/external tool), the approval gate in resolve() (dangerous/unspecified access and truthy guarded arguments always prompt — standing/session/standing_trust powerless; MCP tools state external), and two defects fixed in scope (standing_trust silently overrode a config `forbidden`; the model-supplied private-address escape hatch could be blanket-waived); pinned approval/Phase-16 tests updated with attribution; 31 new tests; gate Run B 708 passed / 6 proven-env failed / 13 skipped, Run D 749 passed / 0 failed; filed at docs/architecture/E-026_TOOLS_DISCIPLINE.md.
- E-027 DONE (2026-10-31) — approval shape for normal folks: `ember.spark.funi.tools.plain` turns E-026's permission shapes into ordinary words (plain action from the detail that matters, plain reach per access class, fetch_url's private-address widening named as a home-network reach); the rememberable scopes are stated truthfully — `always` offered only when the E-026 gate would honour it, worded "while we're chatting, forgotten when the chat ends, never forever", with a plain per-class reason where it is not offered; the prompter accepts only offered answers and counts an unoffered `always` as a one-time yes with that stated on screen (the old silently-worthless session grant is gone); Munnr's proposal renderer gains plain lines; Playbook Recipe 3 transcript corrected; pinned approval tests updated with attribution; 38 new tests; gate Run B 746 passed / 6 proven-env failed / 13 skipped, Run D 787 passed / 0 failed; filed at docs/architecture/E-027_APPROVAL_SHAPE.md.
- E-028 DONE (2026-10-31) — streaming + interruption: Ctrl-C now ends the current thing, never the session, at every waiting point (prompt re-prompts; retrieval abandons the turn with nothing persisted; stream creation inside the guard; approval-prompt and tool-execution interrupts end the turn with the partial persisted tagged, completed calls standing, no further call or generation; non-streaming complete() likewise); **docket 83 CLOSED** — non-streaming tool_calls execute through the same bounded loop (`_drive_complete_turn_with_tools`) and `wrap_complete_as_stream` carries tool_calls for WRAPPED backends; 9 new tests; gate Run B 755 passed / 6 proven-env failed / 13 skipped, Run D 796 passed / 0 failed; filed at docs/architecture/E-028_STREAMING_INTERRUPTION.md.
- E-029 DONE (2026-10-31) — offline truth: a socket guard cuts every non-loopback DNS/connect (attempts recorded, sanity-proven) and the core's full local life runs under it against the REAL adapters — a loopback-Ollama chat turn end to end (probe, embed, retrieve, stream, Episode persisted, zero external attempts), read_local_file, and the sqlite_vec Well round-trip across a reopen (extras shape); the degraded set is listed honestly in docs/architecture/E-029_OFFLINE_TRUTH.md, each item failing as typed plain data (fetch_url's DNS-refusal ToolReply, embed client's None vectors → text search, remote Funi's typed Unavailable, pgvector's Disconnected-ungrounded shape); no production code changed — one defect in the slice's own guard fixture fixed in scope, and Playbook Recipe 7's doctor verification corrected (bare installs cannot run it, docket 13); 7 new tests; gate Run B 761 passed / 6 proven-env failed / 14 skipped, Run D 803 passed / 0 failed; filed at docs/architecture/E-029_OFFLINE_TRUTH.md.
- E-030 DONE (2026-10-31) — error honesty: the chat session's three silent failures are now spoken in plain warnings at the moment they happen — an Episode that cannot be saved (docket 85 CLOSED; "remembered only until this session ends"), a mid-session Well search that fails (docket 86 CLOSED; operator told, prompt carries do-not-invent, Episode flagged well_disconnected, catch broadened beyond BrunnrError), and a startup history load that fails (found in this slice's audit, fixed in scope; "they have not been deleted") — and ERROR/LENGTH finishes are persisted with their error/truncation tags on both roads so a failed or partial reply never reads back as a completed answer; an embedding failure alone is not a retrieval failure (text-search degrade returns real hits, test-pinned); 12 new tests; gate Run B 773 passed / 6 proven-env failed / 14 skipped, Run D 815 passed / 0 failed; filed at docs/architecture/E-030_ERROR_HONESTY.md.
- E-031 DONE (2026-10-31) — session persistence: the pending-episodes journal built (ember.well.pending_journal, per-episode atomic JSON files under <config_root>/state/pending_episodes/, fsync + os.replace + dir fsync) — disconnected turns and Well-save failures are journaled instead of lost (docket 82 CLOSED), a connected startup drains the journal in order before history loads with outcomes spoken, corrupt journal files are quarantined to corrupt/ (never deleted) and reported; sqlite_vec gains synchronous=FULL beside WAL and a BrunnrError-wrapped add_episode, and both adapters skip single corrupt episode rows instead of failing the whole history; 8 + 4 new tests; gate Run B 781 passed / 6 proven-env failed / 15 skipped, Run D 827 passed / 0 failed; filed at docs/architecture/E-031_SESSION_PERSISTENCE.md.
- E-032 DONE (2026-10-31) — the day-one flow, timed and friction-audited in a clean venv (VM profile, loopback wire-shape model): fresh venv 26.79 s + pip upgrade 19.92 s (corrected same day — the first-banked 1.85 s was a re-run over the existing venv), install 19.24 s, day-one ask (wizard + first chat) 1.28 s, second run 0.93 s; three breaks fixed in scope — Hjarta EOF crash (docket 15 CLOSED; clean abort, nothing written), Hjarta writing an `ember.yaml` the documented `[sqlite_vec]`-only install cannot read back without PyYAML (new docket 88 CLOSED; writer falls back to stdlib-readable `ember.toml`, YAML unchanged when PyYAML present), and a Well path typed in the wizard being probed then forgotten (new docket 87 CLOSED; persisted as `brunnr.sqlite_vec.path`, no override for the default); INSTALL.md's wizard list corrected (tools question, TOML case) and the wizard prompt's hardcoded yaml path fixed; real-model day one NOT PROVEN (no Ollama on the VM; Part III owns it); 9 new tests; gate Run B 790 passed / 6 proven-env failed / 15 skipped, Run D 836 passed / 0 failed; filed at docs/architecture/E-032_DAY_ONE_FLOW.md.
- E-033 DONE (2026-10-31) — config for humans: one surface stated + enforced (unknown/fossil keys refused by name at startup), `.env.example` Runa fossil rewritten to the two live env vars (docket 55 CLOSED), template now documents every EmberConfig field (conversation/mcp/streaming/aesir timeout_ms/cognition keys were missing; tree-walk test guards it), storage/sources excerpts state they are not config files (docket 56 core half closed, member half stays E-037), defaults audited unchanged; 6 new tests; gate Run B 796 passed / 6 proven-env failed / 15 skipped, Run D 842 passed / 0 failed; filed at docs/architecture/E-033_CONFIG_FOR_HUMANS.md.
- E-034 DONE (2026-10-31) — logging a friend can read: `ember.diary` keeps a plain-words diary beside the technical trace (daily Markdown files under `<config_root>/diary/`, O(1) O_APPEND+fsync writes, never raises — chat warns once if writing fails); chat records session start/stop, Well reachability, drain + history outcomes, per-turn outcome (answered / ungrounded / interrupted / error / truncated) and save outcome, with NO conversation content by construction (leak-pinned by test); `logging.diary` switch (default on, template-documented); `ember diary [--days N]` reader; tool rounds deliberately left to the audit log (stated limit); 13 new tests; gate Run B 809 passed / 6 proven-env failed / 15 skipped, Run D 855 passed / 0 failed; filed at docs/architecture/E-034_DIARY_LOG.md.
- E-035 DONE (2026-10-31) — multi-conversation isolation: `Episode.conversation_id` (default `"default"`, slug rules) + `ember.spark.conversation` (resolution explicit > config `conversation.active` > default, invalid id refused by name — never a silent fall-back; exact-match filter; tagging); chat loads persona → conversation → window (a foreign talk can neither ride verbatim nor leak through the summary), prompt wall composes persona × conversation, both persistence roads tag Episodes; `ember chat --conversation` flag; pending journal persists the tag (pre-E-035 files load as default); honest limit: adapters still persist neither tag, so named-conversation cross-restart history awaits Part V (E-080 family); retrieval grounding shared by design; 42 new tests; gate Run B 851 passed / 6 proven-env failed / 15 skipped, Run D 897 passed / 0 failed; filed at docs/architecture/E-035_MULTI_CONVERSATION_ISOLATION.md.
- E-036 DONE (2026-10-31) — determinism mode (seeded): `funi.determinism` (off by default, seed 42) + `ember.spark.funi.determinism` — off = no seed key anywhere (wire-pinned, byte-identical requests), on = fixed seed + temperature 0.0 effective (configured temperature never mutated) via Ollama's `seed` option and Aesir's native `seed` field; CLI `--deterministic` / `--seed N` one-run overlay; bad seed refused CONFIG_INVALID at open before any request; retrieval ties now break on chunk_id in both adapters (RRF + SQL; sqlite_vec vector ties re-sorted in Python — vec0 KNN forbids a second ORDER BY key, proven by the first Run D gate's 5 failures and fixed + regression-pinned in-slice); honest limits: backend seed contract owns byte-identical answers (no live model run), timestamps/ids stay non-deterministic by design, ThoughtForge uncovered; 21 new tests (19 passed + 2 skipped default); gate Run B 870 passed / 6 proven-env failed / 17 skipped, Run D 918 passed / 0 failed; filed at docs/architecture/E-036_DETERMINISM_MODE.md.
- E-036 DONE (2026-10-31) — determinism mode (seeded): `funi.determinism` (off by default, seed 42) + `ember.spark.funi.determinism` — off = no seed key anywhere (wire-pinned, byte-identical requests), on = fixed seed + temperature 0.0 effective (configured temperature never mutated) via Ollama's `seed` option and Aesir's native `seed` field; CLI `--deterministic` / `--seed N` one-run overlay; bad seed refused CONFIG_INVALID at open before any request; retrieval ties now break on chunk_id in both adapters (RRF + SQL; sqlite_vec vector ties re-sorted in Python — vec0 KNN forbids a second ORDER BY key, proven by the first Run D gate's 5 failures and fixed + regression-pinned in-slice); honest limits: backend seed contract owns byte-identical answers (no live model run), timestamps/ids stay non-deterministic by design, ThoughtForge uncovered; 21 new tests (19 passed + 2 skipped default); gate Run B 870 passed / 6 proven-env failed / 17 skipped, Run D 918 passed / 0 failed; filed at docs/architecture/E-036_DETERMINISM_MODE.md.
- E-037 DONE (2026-10-31) — core API freeze v1 (library shape): `ember.api` registry — `API_VERSION 1.0.0` (separate from package 0.2.0, re-exported as `ember.API_VERSION`), 63 individual frozen names + 12 schema modules frozen wholesale (92 names) = 155-entry manifest computed from live modules, `is_api_compatible` gate, `verify_api_surface()` clean in the bare default env; `ember.well.brunnr` `__init__` now re-exports BrunnrHandle + open mirroring Funi; NOT frozen: CLI, MCP, munnr/hjarta/smidja internals, concrete adapters (frozen `open()` registries only); docket 56 CLOSED (member half — members keep own config shapes, bind through the API only, fake-member test proven with no extras and no config file read); honest limits: contract + gate tests not import machinery, no member migrated yet (Parts IV–X bind here), behaviour pinned by per-surface suites; 33 new tests; gate Run B 903 passed / 6 proven-env failed / 17 skipped, Run D 951 passed / 0 failed; filed at docs/architecture/E-037_CORE_API_FREEZE.md.
- E-038 DONE (2026-10-31) — concurrency on small hardware: two chats at once (threads, shared Well, barrier-proven mid-turn overlap, phone profile 1024 tok/5 ep per session) — three races fixed in scope: pending-journal drain double-flush (claim-by-atomic-rename; refusal releases in order), diary double header (flock around size-check + write), sqlite Well "database is locked" (PRAGMA busy_timeout=5000); appends + audit log pinned already safe; measured on VM (fake 50 ms backend, 5 turns/chat): sequential 1.285 s / 23.7 MiB, concurrent 0.93+0.81 s / 23.9+24.2 MiB — second concurrent session <0.5 MiB over serial; each window ≤1024 tokens, two ≤2048; honest limits: threads not two processes (NOT PROVEN), process-global tool Well binding named not fixed, no live model; 9 new tests; gate Run B 910 passed / 6 proven-env failed / 18 skipped, Run D 960 passed / 0 failed; filed at docs/architecture/E-038_CONCURRENCY_SMALL_HARDWARE.md; banking commit 5e9047a pushed (remote a151b89 → 5e9047a, ls-remote = local HEAD).
- E-039 DONE (2026-10-31) — core docs + runnable examples: three runnable examples where none existed (first_chat — the real chat loop against a labelled fake model + in-memory Well; member_binding — frozen API v1 only, AST-pinned; offline_turns — banner, pending journal, facts-only diary, clean drain) plus a worked phone-class TOML config that loads through the frozen loader; docket 84's DATA_FLOW half CLOSED (k=5, no AskTurn, streaming default, per-turn JSON journal — facts only, voice intact); new docket 89 (stale examples/ scaffold READMEs → E-195, README care); honest limits: no live model (Part III's burden), chat examples use the operator surface's test seams (not frozen API); 8 new tests; gate Run B 918 passed / 6 proven-env failed / 18 skipped, Run D 968 passed / 0 failed; filed at docs/architecture/E-039_CORE_DOCS_EXAMPLES.md; banking commit a3da82a pushed (remote c677a79 → a3da82a, ls-remote = local HEAD).
- E-040 DONE (2026-10-31) — Part II gate PASS: day-one flow re-proven on the VM profile (targeted 50 passed; three runnable examples each exit 0; E-032 clean-venv timings stand; real-model day one NOT PROVEN — loopback wire-shape model only, Part III owns real-device proof), API freeze checked live (1.0.0, 155 manifest entries, verify_api_surface clean), gate re-measurement identical to E-039 (Run B 918 passed / 6 proven-env failed / 18 skipped; Run D 968 passed / 0 failed / 19 skipped; Run A 1 error docket 1, skips 11 explained by Part II's three new skip-guarded files); Part II docket accounted (closed 15, 55, 56, 81–83, 85–88, 84's DATA_FLOW half; carried open 1, 2, 3, 4, 13 → E-187/E-200, 20 → E-044, 89 → E-195); no road re-cut; filed at docs/architecture/E-040_PART_II_GATE.md. **Part II (E-019–E-040) is CLOSED.**
- E-041 DONE (2026-10-31) — the budget book: `ember.budgets` + docs/architecture/E-041_BUDGET_BOOK.md; core measured on the VM (install 978,843 B all-in — "~50 MB installed" struck; idle 40.7 MiB with Well open; turn peak 39.4–40.1 MiB flat across profiles — "~50 MB RAM" true and generous, docket 67 measured; storage 694 B/turn → 0.40 MiB/month at 20 turns/day); ceilings per profile (toaster 2 MiB/64/64/2 MiB-mo … laptop 16/256/384/100), history read from E-021's config; docket 65 measurement half settled (Verdandi hub live 21.9 MiB, heartbeat 18.4 MiB import-level; "~1 MB" not a process figure), 66 settled by replacement (toaster sum ~514 MB on a 512 MiB host — marginal, E-049 grades it); new docket 90 (VM anchors only, devices re-anchor at E-047–E-049); 11 new tests; gate Run B 929 passed / 6 proven-env failed / 18 skipped, Run D 979 passed / 0 failed.
- E-042 DONE (2026-10-31) — budget tests: `tests/unit/test_budget_gate_e042.py` (9 tests) re-derives every shape in fresh subprocesses (install 740,135 B; idle 25.2 / Well-open 35.9 MiB; turn peaks flat 24.3 MiB all profiles; storage 683 B/ep + 126 B/turn diary → 0.46 MiB/mo) judged against ceilings read live from `ember.budgets`, wired into Runs B/D by living in tests/unit (collection pinned by test); mutation-proven to bite; the gate caught its own probe's ru_maxrss-through-exec parent-peak bug (identical 71.9 MiB = pytest's peak) — fixed in scope to VmHWM, anchors stand; new docket 91 (re-derived storage 808 vs book 694 B/turn → E-050 re-anchor); gate Run B 936 passed / 6 proven-env failed / 20 skipped, Run D 988 passed / 0 failed.
- E-043 DONE (2026-10-31) — install weight cut I: sdist ~45 MB → 1.1 MB compressed (127,162,419 → 3,464,529 B unpacked) by excluding all 11 optional members, the docs heritage corpora, the lawbook PDF/Markdown and CAMPAIGN_STATE.md from `pyproject.toml`'s sdist list; heaviest members measured from the tarball (mempalace 57.0 MB, dictionary 24.1 MB, Open-VTT 6.3 MB); clean-venv install from the cut sdist proven (ember --help exit 0, no member in site-packages); wheel unchanged 305 KB so E-041/E-042 anchors stand; re-derived sdist set matches hatchling file-for-file; 5 new tests; gate Run B 941 passed / 6 proven-env failed / 20 skipped, Run D 993 passed / 0 failed.
- E-044 DONE (2026-10-31) — install weight cut II / dependency diet: every root requirement bounded both ways (docket 23 root half closed; member half = new docket 92); the unbounded `mcp>=1.27` floor was PROVEN broken today — it resolves to mcp 2.3.0, whose SDK removed `mcp.server.fastmcp`, so a fresh [mcp] install could not start `ember mcp serve`; bounded to <2 (resolves 1.30.0, FastMCP imports, MCP tests run real). Docket 20 closed: keyring declared as its own `secrets` extra (measured 16,646,785 B / 10 pkgs — deliberately NOT folded into pgvector, which stays 20,920,005 B); resolver's missing-keyring note now names `ember-agent[secrets]`. Dev split: `dev` is test-only 7,600,880 B (was 89,112,145 B combined, −91.5%), ruff+mypy moved to a new `lint` extra (81,511,265 B measured shape). All-extras combined 54,183,654 → 53,703,943 B. Kept deliberately, named in the doc: psycopg[binary] (ADR 0010, no system libpq for normal folks), PyYAML, the mcp SDK's HTTP stack (hard deps, extra-gated). 7 new tests incl. an exact AST import↔extra map; gate Run B 948 passed / 6 proven-env failed / 20 skipped, Run D (real venv install of the edited package, bounded extras) 1015 passed / 0 failed / 16 skipped — the 5 MCP e2e failures under the isolated-target method were proven ENVIRONMENT (subprocess env filtering) by the venv run.
- E-044 push: banking commit e077d3a pushed under Volmarr's 2026-10-31 standing go-ahead after fetch + remote-diff (remote was d6ecd57 = local HEAD, no divergence) — remote moved d6ecd57 → e077d3a, verified via ls-remote (remote head = e077d3a26693f15c0e550d646b15abec14efdde0 = local HEAD at push time).
- E-045 DONE (2026-10-31) — idle discipline: four profile probes idled a full hour on the VM (121 samples, 30 s interval) — 0.0 CPU seconds, exactly 1 thread, disk byte-identical (164,616 B), RSS never grew at any step (40.8 → 23.0 MiB floor at ~1,261 s, HWM ≤40.9 MiB inside the toaster's 64 MiB idle ceiling), all probes exit 0; gate armed in tests/unit/test_idle_discipline_e045.py (5 tests; extras 5 passed, default 4 skip-stated + 1 passed); no src change, no defect found, no new docket; gate Run B 949 passed / 6 proven-env failed / 24 skipped, Run D 1005 passed / 0 failed / 19 skipped (corrected same day — first banked as 1022/20 from a foreign background result, not the run's log; log-verified figure stands); filed at docs/architecture/E-045_IDLE_DISCIPLINE.md.
- E-046 DONE (2026-10-31) — cold start on the smallest profile: seven fresh `ember ask` processes on the toaster profile (real CLI/Well, loopback wire-shape model) — first word median 2.87 s (1.28–5.38, contended VM, stated), ready at 2.79 s so ~97% is process startup and the turn adds ~0.09 s; first-ever start 3.60 s; book gains the test-pinned anchor (2.87) and a flat 5.0 s cold-start cap on every profile; gate armed in tests/unit/test_cold_start_e046.py (4 tests, median-of-3 judged); the gate caught E-045's idle "wander" assertion failing on proven-normal RSS decline under memory pressure — fixed in scope to judge growth only; gate Run B 952 passed / 6 proven-env failed / 25 skipped, Run D 1009 passed / 0 failed / 19 skipped; filed at docs/architecture/E-046_COLD_START.md.
- E-047 DONE (2026-10-31) — the Pi proof: PROVEN on real hardware — Mimir (purpleviking1), Raspberry Pi 5 Model B Rev 1.1, Ember cloned at fae0e0b + clean-venv install, pi profile, real phi3:mini + nomic-embed-text via the house Ollama, real sqlite_vec Well; ready median 0.18 s (Ember-side re-anchor, docket 90 Pi half settled, 5.0 s cap unrelaxed), first word median 5.69 s (model-included, pinned as its own anchor, not judged against the cap), peak RSS 27.1 MiB, installed 1,951,508 B; cross-process memory proven (run 3 recalled the first-ever question); first-ever cold-model ask 64.91 s; four Pi anchors in ember.budgets pinned by tests/unit/test_pi_proof_e047.py (5 tests); gate Run B 957 passed / 6 proven-env failed / 25 skipped, Run D 1014 passed / 0 failed / 19 skipped; filed at docs/architecture/E-047_PI_PROOF.md.
- E-048 DONE (2026-10-31) — the phone-class proof, grade SIMULATED: phone profile on the VM in a phone-shaped room (2 CPUs pinned, 512 MiB RSS watchdog never triggered, loopback wire-shape model, contended VM) — ready median 1.77 s, first word median 1.79 s inside the unrelaxed 5.0 s cap (first-ever 3.92 s also inside), peak RSS 43.0 MiB vs phone ceilings 96/128, memory proven at the wire (later processes' prompts carried earlier exchanges verbatim; diary loads 1→2→3); real phone NOT PROVEN (Galaxy S26 Ultra paired but offline; no Android runtime in tree) and named as such; three MEASURED_PHONE_SIM_* anchors pinned by tests/unit/test_phone_proof_e048.py (5 tests); docket 90 phone half settled at simulation grade; gate Run B 962 passed / 6 proven-env failed / 25 skipped, Run D 1019 passed / 0 failed / 19 skipped; filed at docs/architecture/E-048_PHONE_PROOF.md.
- E-049 DONE (2026-10-31) — the Toaster Test, honestly graded: NAME CASHED for the Ember core, NOT CASHED for a whole self-contained companion on a literal 512 MiB host. Smallest honest target the house can muster = Mimir (Raspberry Pi 5, as E-047; no smaller computer in the house, phone/tablet offline) running the TOASTER profile (512 tok/3 ep) through the day-one flow — fresh clean-venv install at c4c7cdc, fresh Well, real nomic-embed-text, real smallest model rung qwen2.5:0.5b (397 MB, pulled for this test); ready median 0.21 s (Ember-side re-anchor, docket 90 toaster half settled — docket 90 now fully settled at its grades, 5.0 s cap unrelaxed), first word median 2.18 s real-model (record, not cap-judged), peak RSS 27.2 MiB vs toaster ceilings 64/64, installed 1,956,428 B vs 2 MiB ceiling; replies real and correct; memory proven in the machinery (diary loads 0→1→2→3 across processes), recall quality at the 0.5B rung PARTIAL (run 3 reached the first exchange — "Hello." — but did not quote it in full; model's limit, named); docket 66 grading CLOSED by measurement: ollama ps with both day-one models loaded reports qwen runner 442 MB + nomic runner 565 MB = ~1,007 MB of model house alone on a 512 MiB host (chat alone + OS ~150 + core ceiling 64 = ~656 MB) — a literal 512 MiB whole companion does NOT fit on today's rungs; the 1 GB members of the toaster class remain the comfortable floor; 4 anchors pinned in ember.budgets; 6 new tests; gate Run B 968 passed / 6 proven-env failed / 25 skipped, Run D 1025 passed / 0 failed / 19 skipped; filed at docs/architecture/E-049_TOASTER_TEST.md.
- E-049 push: banking commit edd2760 pushed under Volmarr's 2026-10-31 standing go-ahead after fetch + remote-diff (remote was c4c7cdc = prior local HEAD, no divergence) — remote moved c4c7cdc → edd2760, verified via ls-remote (remote head = edd2760a367e597c5b7ae417cdc601dd7e193f10 = local HEAD at push time).
- E-050 DONE (2026-10-31) — storage growth: a month of companionship simulated against the real Well + real diary (600 typical turns over 30 daily batches, store closed + weighed daily, then grown to 3,000 episodes; script + results in ~/workspace/.verify-tmp/ember-e050/) — month total 408,566 B (0.39 MiB, 680.9 B/turn all-in): Well 352,256 B (587.1 B/episode over the month; steady marginal 585.4 B/episode flat to 3,000; pure 4 KiB page steps, no superlinear growth; retrieval proven at day 30), diary 56,310 B (93.85 B/turn all-in); fits every profile's storage ceiling (5.1× headroom on the toaster's 2 MiB/month; break-even ~103 turns/day; year at reference pace 4.68 MiB) — no ceiling moves, lifecycle rules do NOT tighten; docket 91 CLOSED (E-042's 808 B/turn = 30-episode page rounding + diary session shape; the book's 694 B/turn stands unrevised over the measured 680.9); six E-050 anchors in ember.budgets; honest edge pinned both ways — essay turns 6,144 B/episode, a reference-rate essay month 3.51 MiB passes the toaster ceiling (break-even ~11/day) and fits the phone, E-082's quantified brief; 7 new tests; gate Run B 975 passed / 6 proven-env failed / 25 skipped, Run D 1032 passed / 0 failed / 19 skipped; filed at docs/architecture/E-050_STORAGE_GROWTH.md.
- E-051 DONE (2026-10-31) — thermal & patience etiquette: `ember.etiquette` built (stdlib only) — the room read honestly (1-minute load per CPU via getloadavg/cpu_count; hottest /sys/class/thermal zone in °C; an unreadable signal is None and never votes), judged PROCEED/EASE/YIELD worst-signal-wins at the stated policy lines (load 1.0 eases / 2.0 yields per CPU; 70 °C eases / 80 °C yields — back off before the danger zone, the Aesir lesson), and a bounded `wait_for_room` for background work only (per-level delays 1 s/5 s, MAX_WAIT_S 30 s, outcome states waited/checks/bound_reached — patience never a deadlock). Wired into the one bulk background act: the local-files ingest's default OllamaEmbedClient carries the hook, consulted between batches only — a single-batch foreground embed never waits, and chat/MCP clients are unhooked. VM room proven live (probe in ~/workspace/.verify-tmp/ember-e051/: load/CPU 1.75 → EASE, thermal None — the VM exposes no zones and none was invented; a 3 s-bounded wait waited exactly 3.0 s over 4 checks and proceeded with bound_reached). Pi thermal NOT PROVEN (parser pinned against the real /sys shape in tests; device re-anchor belongs with the next device visit). No budget-book entry moves, no defect found in existing code, no new docket items. 14 new tests; gate Run B 989 passed / 6 proven-env failed / 25 skipped, Run D 1046 passed / 0 failed / 19 skipped; filed at docs/architecture/E-051_THERMAL_PATIENCE_ETIQUETTE.md.
- E-051 push: banking commit 89482a6 pushed under Volmarr's 2026-10-31 standing go-ahead after fetch + remote-diff (remote was f887010 = prior local HEAD, no divergence) — remote moved f887010 → 89482a6, verified via ls-remote (remote head = 89482a6104f4f07fb12c63c54410af8714a13a76 = local HEAD at push time).
- E-052 DONE (2026-10-31) — update weight: `ember.updates` built (stdlib only) — an update priced before any channel exists to carry one (E-183 consumes these costs): the download is the wheel shape (package tree deflated, sorted entries, level 9, built in memory) measured on the slice's final tree at **293,387 B** (~0.28 MiB; no real wheel built — hatchling absent from the campaign env, stated in the record), the tree it unpacks to **775,675 B**, and the apply peak stated as a formula (download + old + new = **1,844,737 B**, ~1.76 MiB) — all three pinned as MEASURED_UPDATE_* anchors in ember.budgets. Per profile: download ceiling = the profile's install ceiling read from the book (derived, never a copy); the measured update fits every profile (toaster ~7.1x headroom). Metered connections respected structurally in `decide_update`: over-ceiling → EXCEEDS_BUDGET at any consent; metered → ASK_FIRST at ANY size with the byte price stated in the reason (a 1-byte update asks — smallness is not consent); uninvited → INVITE_REQUIRED (no silent auto-anything); invited + unmetered + within ceiling → READY. The model is never part of an update's weight. No defect found in existing code, no new docket items. 13 new tests; gate Run B 1002 passed / 6 proven-env failed / 25 skipped, Run D 1059 passed / 0 failed / 19 skipped (Run D via a tempdir-pre-set wrapper — the VM's tempfile probe began refusing new processes VM-wide mid-session, EPERM on its O_EXCL probe creates with /tmp 99% free; a stale 509 MB pytest basetemp from a finished foreign run was removed from /tmp during diagnosis; counts are the runner's own, logs in ~/workspace/.verify-tmp/ember-e052/gate/); filed at docs/architecture/E-052_UPDATE_WEIGHT.md.
- E-052 push: banking commit 0cf52af pushed under Volmarr's 2026-10-31 standing go-ahead after fetch + remote-diff (remote was a76c059 = prior local HEAD, no divergence) — remote moved a76c059 → 0cf52af, verified via ls-remote (remote head = 0cf52af62ce035491ea3626ecc944d7784dab0e2 = local HEAD at push time).
- E-053 next — battery-shaped behaviour (phone-class): duty cycling, no busy-wait, measured drain shape.
## E-053 — Battery-shaped behaviour (DONE, 2026-10-31)

- Record filed at `docs/architecture/E-053_BATTERY_BEHAVIOUR.md`: `ember.battery` built (stdlib only) — background work is duty-cycled by the battery, foreground never. Reader: Linux `/sys/class/power_supply` shape (Battery-type supplies, capacity + status; mains skipped; absent/malformed/out-of-range → unknown None, never guessed — the VM reads honestly as no-battery/mains-fed, as would the Pi). Judge (`assess`, pure): FULL (charging at any gauge / no battery / unknown / ≥50%), CONSERVE (<50%: bursts of 4 batches, one 5 s rest), LOW (<20%: 1 batch, 15 s rests), CRITICAL (<10%: every batch followed by 30 s rest — work crawls, stated, rather than silently stopping). `DutyCycler` consulted between batches, re-reads the battery each consultation (a mid-job charger unshapes the job at the next boundary), and rests ONCE per spent burst in a single blocking sleep of the full rest — no busy-wait; the sleep-call record is pinned exactly by tests. Wiring: `OllamaEmbedClient` gains an optional `battery_hook` at E-051's between-batches point (single-batch foreground embeds never call it; default None = no change); the local-files ingest's default client carries a fresh DutyCycler beside the patience hook.
- Busy-wait audit of the core: chat blocks on readline (E-045's 0.0 s CPU idle hour), every other wait is a single blocking sleep per wait (embed backoff, tether backoff, etiquette) — no polling loop exists in `src/ember`, and the new code keeps that property by shape.
- Measured drain shape (VM, probe in `~/workspace/.verify-tmp/ember-e053/`, two runs): a single blocking 5 s rest spent **0.000 s process CPU** (run 2: 0.0001 s); a background job of 0.25 s-CPU units ran FULL at CPU/wall **0.4117** (4.001 s CPU / 9.719 s wall, 16 units, 0 rests) vs CONSERVE **0.1885** (3.001 s / 15.921 s, 12 units, exactly 2 rests totalling 10.0 s) — less than half under the same heavy contention (run 2: 0.1722 vs 0.4653); work+rest duty ≈23% vs 100%. All three pinned as `MEASURED_BATTERY_REST_CPU_S` / `MEASURED_DUTY_FULL_CPU_FRACTION` / `MEASURED_DUTY_CONSERVE_CPU_FRACTION` anchors in `ember.budgets`. A real battery's percent-per-hour drain is **NOT PROVEN** — no house battery device can run Ember (phone offline at E-048, no phone runtime in tree); the anchors price the drain's cause (CPU duty), and the record says so. No defect found in existing code, no new docket items. 15 new tests; gate Run B 1017 passed / 6 proven-env failed / 25 skipped, Run D 1074 passed / 0 failed / 19 skipped (both file-verified from the gate logs in `~/workspace/.verify-tmp/ember-e053/gate/`).
- E-053 push: banking commit 3e5efc3 pushed under Volmarr's 2026-10-31 standing go-ahead after fetch + remote-diff (remote was 0f10adb = prior local HEAD, no divergence) — remote moved 0f10adb → 3e5efc3, verified via ls-remote (remote head = 3e5efc3e989baa9267ac2d25a89cdc1de1504806 = local HEAD at push time).
- E-054 next — graceful smallness: at budget's edge the companion sheds features by the stated ladder, announcing each shed.

## E-054 — Graceful smallness (DONE, 2026-10-31)

- Record filed at `docs/architecture/E-054_GRACEFUL_SMALLNESS.md`: at budget's
  edge the companion now sheds features by a stated ladder, announcing each
  shed. New module `ember.smallness`: reads the process's own VmRSS from
  /proc/self/status (unknown reads None and never votes), judges it against the
  profile's turn-RAM ceiling from the budget book — EDGE ≥75% sheds history
  summaries, STRAINED ≥90% also sheds semantic retrieval, OVER ≥100% also
  sheds the wide history window (narrowed to the book's smallest allowance,
  512 tokens / 3 episodes; an operator's smaller override is never widened).
  Never shed: answering, saving, the announcements themselves, tool safety.
  Sheds are per-turn, not sticky; restores are announced too; announcements
  fire only on change.
- Wiring is the chat turn (the place all three rungs have real consumers):
  per-turn guard consult; rung 2 runs `_retrieve(text_only=True)` — the embed
  call is skipped entirely and the existing honest text-search path runs;
  rungs 1+3 build the window under `plan.conversation_config(...)` (identity
  when unshed, so a comfortable turn is byte-for-byte the pre-E-054 shape).
  Announcements go to the person's screen as `[room: …]` and to the diary.
  Bulk ingest deliberately NOT wired: a shed embed batch would return None
  vectors whose chunks the journal counts failed while marking their document
  done — lost, not deferred (record §3).
- Live ladder proof on the VM (probe in `~/workspace/.verify-tmp/ember-e054/`):
  a chat-shaped process (24.29 MiB base RSS, beside E-041's 25.3 MiB anchor)
  holding memory in 4 MiB steps crossed EDGE at 48.31 MiB (0.755, summaries
  announced), STRAINED at 60.32 MiB (0.943, semantic announced), OVER at
  64.33 MiB (1.005, wide history announced) against the toaster's 64 MiB
  ceiling — every line in ladder order, one announcement per rung, none
  repeated at steady levels.
- Defect found by this slice's gate and fixed in scope (record §4): the
  E-021 tiny-budget chat test failed — the ladder judged the *pytest
  harness's* RSS (~100 MiB-class) against the toaster ceiling and shed the
  summary that test asserts; the same coupling would give any embedding host
  (E-037 library shape) sheds driven by the host's memory. Fix: `chat.run`
  gained a `smallness_guard` test seam beside its existing seams; the E-021
  chat helper pins a comfortable guard (its subject is windowing; no E-021
  assertion changed).
- 15 new tests; gate Run B **1032 passed, 6 failed, 25 skipped, 1 warning**
  (1017 E-053 baseline + 15 new; the 6 are the proven environment failures,
  identical set). Run D **1089 passed, 0 failed, 19 skipped, 1 warning**,
  exit 0 (1074 + 15 — reconciles exactly). No new docket items. No README
  touched.
- E-054 push: banking commit 24be2b5 pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was fba8c6a, an
  ancestor; the push also carried the tick's IN PROGRESS marker 7c7a427) —
  remote moved fba8c6a → 24be2b5, verified via ls-remote (remote head =
  24be2b54fc41e1509ad924b9c76d08bf51ce914e = local HEAD at push time).
- E-055 next — the budget book published in-repo with its measurements.

## E-055 — The budget book published (DONE, 2026-10-31)

- Published book filed at `docs/BUDGET_BOOK.md`, record at
  `docs/architecture/E-055_BUDGET_BOOK_PUBLISHED.md`: the whole budget book in
  one reader-facing document — plain words first; the four profiles' ceiling
  table exactly as `ember.budgets` states it (incl. the flat 5.0 s cold-start
  cap and the config-read history allowances); E-041's founding measurements
  (install 978,843 B, idle 40.7 MiB, turn 40.1 MiB, 694 B/turn; "~50 MB
  installed" struck, "~50 MB RAM" true-and-generous); the lightening
  (E-043 sdist 127,162,419 → 3,464,529 B unpacked; E-044 dependency diet);
  the behaviour table (E-045 idle hour 0.0 s CPU / 1 thread / disk identical,
  E-046 cold start 2.87 s median, E-052 update 293,387 / 775,675 /
  1,844,737 B, E-050 month 408,566 B + essay edge 6,144 B/episode, E-053 duty
  0.1885 vs 0.4117, E-051 thermal lines, E-054 shedding ladder); the device
  proofs with grades attached (E-047 Pi REAL — ready 0.18 s, RSS 27.1 MiB,
  installed 1,951,508 B; E-048 phone SIMULATED — ready 1.77 s, RSS 43.0 MiB;
  E-049 Toaster REAL — ready 0.21 s, RSS 27.2 MiB, installed 1,956,428 B,
  verdict in two halves: name cashed for the core, NOT CASHED for a whole
  companion on a literal 512 MiB host, model runners 442 + 565 MB measured);
  exclusions + NOT PROVEN lines in the book's own §6 (real phone, real
  battery drain %/h, Pi thermals); and an appendix carrying every
  `MEASURED_*` anchor by code name and value.
- Drift armour: `tests/unit/test_budget_book_e055.py` — **8 tests** judging
  the published document against the LIVE code (no second copy of any
  number): ceiling-table cells == `all_budgets()`, history allowances ==
  config-derived budgets, every `MEASURED_*` anchor (27 at banking) present
  at its coded value, storage arithmetic == the code's functions, honesty
  lines present, ceiling table holds exactly the four profiles (member rows
  stay E-057's). Two first-draft presentation defects caught by these tests
  and fixed before banking (abbreviated history allowances in the book;
  the test's cold-start print format). No new measurements taken, no ceiling
  moved, no `src/` code changed, no new docket items. No README touched.
- Slice gate: Run B **1040 passed, 6 failed, 25 skipped, 1 warning**
  (1032 E-054 baseline + 8 new; the 6 are the proven environment failures,
  identical set). Run D **1097 passed, 0 failed, 19 skipped, 1 warning**,
  exit 0 (1089 + 8 — reconciles exactly). Logs in
  `~/workspace/.verify-tmp/ember-e055/gate/`.
- E-055 push: banking commit 86d3d0c pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was bd9991f, an
  ancestor; the push also carried the tick's IN PROGRESS marker 77ae68b) —
  remote moved bd9991f → 86d3d0c, verified via ls-remote (remote head =
  86d3d0ce0797dacdf74ef6e27cc353993d56f155 = local HEAD at push time).
- E-056 next — regression armour: budget tests join the permanent gate.

## E-056 — Regression armour (DONE, 2026-10-31)

- Record filed at `docs/architecture/E-056_REGRESSION_ARMOUR.md`: Part III's
  budget tests (fifteen files, one per slice E-041–E-055) joined the
  permanent gate as ONE command — `python3 scripts/dev/run_budget_gate.py`
  (in `scripts/dev/`, the scaffold's stated purpose; `--help` + docstring
  per the scripts rules). The script's `BUDGET_TEST_FILES` manifest is the
  single enrolment list, in roadmap order; the command is
  `sys.executable -m pytest <manifest> -q` at the repo root with `src/`
  leading PYTHONPATH, exit code propagated unchanged; `--list` prints the
  manifest, `--collect-only` checks wiring, args after `--` pass to pytest.
  The armour now stands in BOTH gates: the one-command budget gate and the
  whole-suite Runs B/D (every enrolled file lives under `tests/unit/`).
- Keeper tests: `tests/unit/test_budget_armour_e056.py` — **7 passed**
  (default env): manifest exactly 15, no duplicates; every enrolled file
  real, under `tests/unit/`, holding ≥1 test; completeness — every
  `tests/unit/` file with a Part III suffix `_e041`–`_e055` is enrolled in
  slice-number order (a future unenrolled budget file fails here, not
  silently); command == manifest + `-q`; `--list` == manifest;
  `--collect-only` through the real script collects every enrolled file.
  The keeper is deliberately NOT in the manifest (it re-measures nothing;
  enrolling it would be circular). One defect in the slice's own test
  found and fixed in scope: discovery first sorted alphabetically and
  failed against the roadmap-ordered manifest — that failure is the
  completeness test proving it bites; discovery now sorts by slice number.
- The permanent gate itself, run both shapes: default env **122 passed,
  7 skipped**, exit 0 (the 7 are the honest sqlite_vec-absent guards —
  E-042 ×2, E-045 ×4, E-046 ×1); extras shape **129 passed, 0 skipped**,
  exit 0 (122 + 7 reconciles exactly). No ceiling moved, no anchor
  changed, no `src/` code touched, no new docket items. No README touched.
- Slice gate: Run B **1047 passed, 6 failed, 25 skipped, 1 warning**
  (1040 E-055 baseline + 7 new; the 6 are the proven environment failures,
  identical set). Run D **1104 passed, 0 failed, 19 skipped, 1 warning**,
  exit 0 (1097 + 7 — reconciles exactly). Logs in
  `~/workspace/.verify-tmp/ember-e056/gate/`.
- E-056 push: banking commit 61d3fbc pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was c146826, an
  ancestor; the push also carried the tick's IN PROGRESS marker 8303815) —
  remote moved c146826 → 61d3fbc, verified via ls-remote (remote head =
  61d3fbc6a150cbb09b49bffa397f7edae018ea2c = local HEAD at push time).
- E-057 next — member budget table: every member's cost per profile.

## E-057 — Member budget table (DONE, 2026-10-31)

- Table published at `docs/BUDGET_BOOK.md` §7, record at
  `docs/architecture/E-057_MEMBER_BUDGET_TABLE.md`: the twelve running
  members (core `src/` + the eleven imported members of E-002) weighed
  from `git ls-files` (count + bytes per directory, E-002/E-014 method)
  and judged against the book's live install ceilings. Total tracked
  weight **131,211,064 B** (125.13 MiB), almost all of it three members
  whose weight is data, not code: mempalace 59,049,715 B, dictionary
  24,221,782 B, Verdandi 16,817,105 B. Smallest covering profile: core
  (814,264 B), mimir-well, seidr_engine and bifrost fit **toaster**;
  kista (2,770,218 B) fits **phone**; astrology-engine, Hamr, Open-VTT
  and CloakBrowser's tracked tree fit **pi**; mempalace, the dictionary
  and Verdandi fit **none** — Verdandi misses even the laptop's 16 MiB
  ceiling by **39,889 B**. Members cost a core user nothing (excluded
  from the distribution since E-043); the table prices carrying the
  monorepo or running a member from a checkout. The remaining ~83 MiB
  of tracked estate (docs, root loose files, assets, tests, scaffolding)
  is checkout-only, accounted in prose and deliberately not profile-judged.
- RAM, honestly graded: import-level floors measured this slice
  (fresh process, top package, VmHWM, median of 3, VM; raw runs in
  `~/workspace/.verify-tmp/ember-e057/import_ram.json`) — interpreter
  floor 10.1 MiB; mempalace 11.5, core 12.0, astrology 12.4, Verdandi
  (heartbeat package) 12.6, seidr 13.3, bifrost 15.2, mimir-well 20.8,
  kista 24.2, Hamr 40.1 MiB. Floors are floors, stated as such in print:
  running costs stand at E-041's figures (core idle 40.7 MiB, Verdandi
  hub 21.9 MiB live). NOT MEASURED with reasons named: Open-VTT (Godot
  absent), dictionary (Node deps absent), CloakBrowser (import fails
  bare on `httpx`; its real weight is the proprietary binary, absent
  from the tree — tracked size is wrapper only; vendored ~190 MB idle
  claim stays E-179's, never adopted).
- Tests: `tests/unit/test_member_budget_table_e057.py` **7 passed**
  (15 passed together with E-055's armour) — every row re-derived from
  `git ls-files`, fit recomputed from live ceilings, prose total +
  Verdandi margin recomputed, the two published copies held identical.
  Slice gate: Run B **1054 passed, 6 failed, 25 skipped, 1 warning**
  (1047 E-056 baseline + 7 new; the 6 are the proven environment
  failures). Run D **1111 passed, 0 failed, 19 skipped, 1 warning**,
  exit 0 (1104 + 7 — reconciles exactly). Logs in
  `~/workspace/.verify-tmp/ember-e057/gate/`. No ceiling moved, no
  anchor changed, no `src/` code touched, no README touched, no new
  docket items.
- E-057 push: banking commit 9b1bd09 pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 743ae19,
  an ancestor; the push also carried the tick's IN PROGRESS marker
  66acbbe) — remote moved 743ae19 → 9b1bd09, verified via ls-remote
  (remote head = 9b1bd090cc00c6972feaf051e869fb873b4413a7 = local HEAD
  at push time).
- E-058 next — Part III gate: budgets enforced by tests; Toaster Test
  verdict recorded with its device named; summary filed.

## E-058 — Part III gate (DONE, 2026-10-31)

- Gate filed at `docs/architecture/E-058_PART_III_GATE.md`: **Part III gate
  PASS** — all seven gate criteria checked (G1–G7). Budgets are enforced by
  tests, the Toaster Test verdict is recorded with its device named, and a
  plain-language summary stands at the gate doc's head and in its §6.
- Budget enforcement re-proven at the gate: the permanent budget gate
  (`python3 scripts/dev/run_budget_gate.py`, E-056) re-run this slice in both
  shapes, exit 0 both times — default **122 passed, 7 skipped** (the honest
  extras guards), extras **129 passed, 0 skipped** — identical to E-056's
  banked record. The same armour also runs inside every whole-suite gate.
- Toaster Test verdict (E-049, restated unsoftened): device **Mimir
  (purpleviking1) — Raspberry Pi 5 Model B Rev 1.1**, the house's smallest
  real computer, running the toaster profile. **Core CASHED** (ready 0.21 s
  vs the unrelaxed flat 5.0 s cap, peak RSS 27.2 MiB vs 64 MiB, installed
  1,956,428 B vs 2 MiB, real qwen2.5:0.5b + nomic-embed-text, memory across
  processes; recall quality at the 0.5B rung PARTIAL, the model's limit).
  **Whole 512 MiB host NOT CASHED**: `ollama ps` measured the two day-one
  model runners at 442 + 565 = ~1,007 MB on a 512 MiB host; the comfortable
  member of the toaster class is the 1 GB-and-up machine.
- Part III docket accounted: closed 20, 23 root half, 65 measurement half,
  66, 67 (with its front-door wording remainder → E-197), 69 core half, 70,
  90 (at its grades: Pi REAL / phone SIMULATED / toaster settled), 91.
  Carried open, not lost: 92 (= 23's member half → Parts IV/VI/VIII/IX per
  member), 65's wording half (→ E-060), 68 (→ Part IX).
- NOT PROVEN at this gate, each with its road named: a real phone (E-048 is
  SIMULATED), a real battery's drain rate, Pi thermal behaviour, a whole
  companion on a literal 512 MiB host, member RAM for Open-VTT / the
  dictionary / CloakBrowser (E-057, with reasons).
- Slice gate at part-gate shapes (E-017 method; logs in
  `~/workspace/.verify-tmp/ember-e058/gate/`), all IDENTICAL to E-057's
  banked counts: Run A whole/default **1 error, 11 skipped, exit 2**
  (docket 1); Run B default excl. pgvector file **1054 passed, 6 failed,
  25 skipped, 1 warning** (the 6 are the proven environment failures);
  Run D whole with extras **1111 passed, 0 failed, 19 skipped, 1 warning**,
  exit 0. Doc-only slice, no code touched, no README touched, no new
  docket items. Road checked: no re-cut; Part IV (Verdandi) follows.
- **Part III (E-041–E-058) is CLOSED.** Next: E-059 — Verdandi mapped.
- E-058 push: banking commit 1512f19 pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 24464d9, an
  ancestor; the push also carried the tick's IN PROGRESS marker 4f78bcd) —
  remote moved 24464d9 → 1512f19, verified via ls-remote (remote head =
  1512f1991a167cbf3c2e0d5a78c7f397f8776eeb = local HEAD at push time).

## E-059 — Verdandi mapped (DONE, 2026-10-31)

- Map filed at `docs/architecture/E-059_VERDANDI_MAPPED.md`: Verdandi drawn
  from code at b275aeb — three generations of one idea in one directory:
  the conversation layer (conversation_logger 619 lines, context_injector
  142, top-level reactor 345, nerve hub nervous_system 847), the heartbeat
  package (8,618 lines: 5 checks, 5 actions, heartbeat reactor, pulse →
  SQLite), and the passengers (verdandi/eir 1,154 lines; runa reward /
  negative / mood systems + push_reward — publishers with NO in-tree
  callers). Whole member 19,194 Python lines (11,725 production, 7,469 tests).
- Central finding: **there is no single event model.** The hub dialect is
  `{type, data, source}` stamped `_seq/_ts/_iso` over
  `~/.hermes/state/runa.sock`; the heartbeat fires a flat `{event_type, …}`
  dialect over a DIFFERENT socket (`<base>/run/verdandi.sock`, nothing in
  tree listens) and falls back to a third shape written directly into the
  same nerve_feed.jsonl; heartbeat state-change fires have no fallback.
  Pulse events fire BEFORE the reactor and BEFORE the state transition
  (which happens only in run()'s loop, never in a bare pulse() call), so
  they carry the pre-transition state.
- Deployment shape proven from code: the conversation layer hardcodes
  `~/.hermes/state`; the logger's nerve bridge loads nervous_system.py ONLY
  from that deployed dir and silently no-ops in-tree (on this VM the state
  dir holds heartbeat artefacts but no deployed top-level copies). The
  Ember core does not touch Verdandi at all (one docstring mention in
  src/ember/api.py); the hub's only in-tree subscriber is its own CLI.
  The context block (current state + recent sessions + feed tail 10 +
  reactor directives) is item-capped per layer with NO total budget —
  E-062's starting fact.
- Six new docket items: 93 (three event dialects / two sockets → E-061),
  94 (conversation-layer deployment coupling, nerve bridge dormant in-tree
  → E-067/E-073), 95 (top-level reactor's `focus` accepted, never used;
  CLI --focus is a no-op → E-065), 96 (nervous_system get_status() publishes
  a real `ping` event into the feed instead of using the nerve_type ping
  control → E-066), 97 (injector log-event vocabulary missing mood_shift,
  7 vs logger's 8 → E-061), 98 (logger's _update_current dead code, cmd_*
  hand-rolled current.json merges diverge → E-063).
- Focal test proof this slice: the four focal Verdandi files
  (context_injector, conversation_logger, reactor, nervous_system) —
  default env 95 passed / 6 failed, all 6 the missing pytest-asyncio
  environment class; with the declared dev dep supplied from the isolated
  target dir, **101 passed, exit 0**. Logs in
  `~/workspace/.verify-tmp/ember-e059/`.
- Slice gate (doc-only slice): Run B **1054 passed,
  6 failed, 25 skipped, 1 warning** (the proven environment set);
  Run D **1111 passed, 0 failed, 6 skipped, 1 warning**, exit 0
  (pass/fail identical to E-058's Run D; skip count differs from
  its 19 — extras shape variance, not investigated).
  CORRECTION (same day): the first banking recorded Run D as
  19 skipped, carried from E-058's record before Run D's own log
  was read; the log's figure is 6. Corrected here and in the
  E-059 doc. No code touched, no README touched.
- E-060 next — the VD-RM concordance executed.
- E-059 push: banking commit 9017035 pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was b275aeb, an
  ancestor; the push also carried the tick's IN PROGRESS marker 0c38b69) —
  remote moved b275aeb → 9017035, verified via ls-remote (remote head =
  9017035acb7e4ade033679bb1cd9d8e054a1cc2f = local HEAD at push time).

## E-060 — VD-RM concordance executed (DONE, 2026-10-31)

- Concordance executed at `docs/architecture/E-060_VDRM_CONCORDANCE_EXECUTED.md`:
  VD-RM's completed claims re-verified by tests this slice — `test_skuld.py`
  **35 passed** (identical to E-009); the four-file Verdandi focal set
  (skuld + heartbeat actions/checks/heartbeat) **374 passed, 0 failed** in
  three consecutive serial runs. One earlier combined run under parallel
  command load scored 371/3 with the failures never identified (tail-only
  log) and unreproduced — recorded honestly as new docket 99 (UNRESOLVED
  flake, with its re-open rule: capture the full log and name the tests).
- Vör (docket 31) re-proven broken this slice with synthetic contexts:
  `should_trigger` crashes `AttributeError: 'str' object has no attribute
  'get'` on Skuld's own `{"status": …}` capacity shape; the no-action
  return crashes on `ActionSeverity.INFO` (nonexistent) with the `name=`
  field error latent behind it; Vör defines `execute()` and no
  `_execute()`, bypassing BaseAction's crash wrapper. Repair contract
  fixed in the E-060 doc and owned by **E-065**, including Vör's first tests.
- The remaining road re-cut: v0.4.0 "Valhalla" is **CLOSED** — Prometheus
  and the emotional architecture were already shipped in v0.3.0 (struck as
  double-counted, docket 35), and Distributed Heartbeat + the REST API are
  **RETIRED** with reasons (absent re-verified by tree search this slice;
  distributed contradicts the E-020 tethering spec, the REST sketch's
  local need is served by E-061/E-066/E-073; reopening either is a new
  commission). The Urðr-integration maintenance sketch is retired
  (static windows stand, test-proven). v1.0 "Yggdrasil production-ready"
  is undefined/NOT PROVEN — E-076's gate must close or re-road it with
  criteria and an owner. Code is the authority over VD-RM's sketches (37).
- Decisions: `pulse_metrics` (34) — **WIRE, don't stop**: E-066 wires
  Skuld to read it as its health-history source, with tests. Canonical
  emotional set named (33 closed as a naming): **eight** labels
  `classify()` can return — the 6 `EMOTIONAL_STATES` + `moderate` +
  `unknown`; VD-RM's "7" struck. Budget wording settled (65's wording
  half): hub ≠ heartbeat — hub **21.9 MiB live**, heartbeat **18.4 MiB
  import-level** (E-041, VM) are the only measured figures; elder
  ~1 MB/~13 MB/~15–25 MB claims superseded, and no document may quote a
  Verdandi size without naming its program (doc edits at E-074; the
  README is never edited — its ~1 MB line stands contradicted on record).
  Severity docstring verdict (from E-059 §9): the comparator (UNKNOWN
  ranks −1, below OK) is the behaviour; the docstring order is wrong
  wording, fixed at E-074. Stale sibling docs (35) re-verified still
  stale in the same five files; all five are E-074's list.
- Slice gate: Run B **1054 passed, 6 failed, 25 skipped, 1 warning**
  (the proven environment set, identical to E-058/E-059); Run D
  **1111 passed, 0 failed, 19 skipped, 1 warning**, exit 0 (identical
  to E-058's Run D). Logs in `~/workspace/.verify-tmp/ember-e060/gate/`.
  Doc-only slice, no code touched, no README touched.
- E-061 next — event contract v1: event shapes versioned; producers/
  consumers listed per event.
- E-060 push: banking commit be93dfb pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 669655d, an
  ancestor; the push also carried the tick's IN PROGRESS marker eb3d440) —
  remote moved 669655d → be93dfb, verified via ls-remote (remote head =
  be93dfb9453fea2ee7bce1fe7415ddd3d8858693 = local HEAD at push time).
- CORRECTION (same day, E-060): the E-060 section above and the banking
  commit message recorded a focal-set run of 371 passed / 3 failed under
  parallel load, docketed as item 99. That figure is WITHDRAWN: the
  original focal run's completed log (delivered late) reads **374 passed**,
  every logged focal run (four, in `~/workspace/.verify-tmp/ember-e060/`)
  is 374 passed / 0 failed, and no log anywhere contains a 371/3 run —
  the figure was unattributable and, per the counts-from-the-runner-only
  law, cannot stand. Docket 99 is withdrawn in the E-060 doc §8 (the
  number is not reused; the next new docket item is 100) and the doc's
  §2/§9 are corrected to match. All other E-060 counts (skuld 35,
  Run B, Run D) are log-backed and unchanged.

## E-061 — Event contract v1 (DONE, 2026-10-31)

- Contract filed in code at `Verdandi/event_contract.py` (stdlib-only,
  standalone for deployed copies) with its reading copy at
  `docs/architecture/E-061_EVENT_CONTRACT_V1.md`: canonical v1 envelope
  `{v: 1, type, data, source}` (hub stamps `_seq/_ts/_iso`; offline
  fallback adds `_fallback`, no `_seq`); versioning rules (unknown
  fields ignored, breaking a registered shape = version bump, new
  types registered in the same change as their producer); control
  messages named (subscribe/ping/recent → subscribed/pong/recent_events,
  plus ack/shutdown). Every event registered with producer, consumers,
  data fields, source, status: 4 conv_* + push_reward + runa_reward +
  runa_negative + the open operator vocabulary + 5 mood families
  (event:*, stimulation:*, orgasm, thought:*, location:*) as canonical;
  `ping` registered as a DEFECT (docket 96, repair E-066); heartbeat_pulse
  + heartbeat_state_change as LEGACY (flat dialect to verdandi.sock,
  NO listener, consumers honestly empty) + the heartbeat_fallback feed
  shape. Sockets named apart: canonical runa.sock vs legacy
  verdandi.sock. `classify_dialect` / `normalize_event` (no field
  dropped) / `validate_publish` implement the legacy translations.
- Producers brought onto the contract: `publish_event_sync` now stamps
  `'v': 1` (a literal, not an import — nervous_system.py is deployed
  standalone; pinned by test); the mood/arousal system's `_fire_nerve`
  now emits the canonical envelope. CORRECTION to E-059 recorded in
  the E-061 doc §5: E-059's "runa_mood_arousal publishes nothing" was
  wrong — `_fire_nerve` fires a FOURTH dialect ({source, event,
  timestamp, data}) at the right socket (runa.sock) with the wrong
  kind key, so hub feeds carried its events with no `type`; that
  dialect is retired as a producer shape by this slice (recognised
  for reading in the contract). Its passenger status (no in-tree
  callers) stands. Wire shape proven behaviourally by a captured-
  socket smoke (canonical envelope to runa.sock; evidence dir).
- Docket 97 CLOSED: context_injector's log-event choices listed only
  7 of the logger's 8 EVENT_TYPES (missing mood_shift); the injector
  now derives `choices=sorted(EVENT_TYPES)` from the logger, the same
  derivation the logger's own CLI uses, pinned by source test + a
  `log-event --help` behaviour test. `event_contract.LOG_EVENT_TYPES`
  mirrors the logger's set exactly (pinned equal by test).
- Docket 93 settled in two of three parts: canonical shape declared
  + versioned, mood dialect retired; the heartbeat producer's
  transport rewiring onto runa.sock is expressly E-067's (cross-member
  wiring under this contract), not dropped. Hub-side validation
  enforcement was NOT smuggled in (no Part IV slice claims it);
  validate_publish is available to consumers.
- Bookkeeping fixed in scope: this slice's Verdandi changes moved
  the E-057 member budget table — re-measured and updated in both
  published copies (BUDGET_BOOK §7 + E-057 record, with the re-measure
  noted in the record): Verdandi 180 files / 16,837,498 B (was 179 /
  16,817,105 B), twelve-member total 131,231,457 B (was 131,211,064 B),
  laptop-ceiling miss 60,282 B (was 39,889 B); profile verdict
  unchanged (none), no RAM floor re-measured, no ceiling moved.
- Tests: `tests/unit/test_event_contract_e061.py` **22 passed** —
  registry completeness re-derived from producer sources (every
  literal publish_event_sync site, the conv_* family, the heartbeat
  legacy fires, every mood _fire_nerve family), dialect/normalize/
  validate behaviour, producer shape pins, stdlib-only contract,
  doc names every registered event. Verdandi focal: conversation
  set **101 passed** (identical to E-059), heartbeat set **374
  passed** (identical to E-060), both with the declared pytest-asyncio
  from the isolated extras dir. Slice gate: Run B **1076 passed,
  6 failed, 25 skipped, 1 warning** (1054 + 22; the 6 are the proven
  environment failures — the first attempt's 2 extra failures were
  the E-057 tests catching this slice's own weight change, fixed by
  the re-measure above); Run D **1133 passed, 0 failed, 19 skipped,
  1 warning**, exit 0 (1111 + 22). Logs in
  `~/workspace/.verify-tmp/ember-e061/gate/`. No README touched.
- E-062 next — context injection discipline: what may be injected,
  when, with what budget — the injector's rules as tests.
- E-061 push: banking commit 76c47fa pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 037fc0a,
  an ancestor; the push also carried the tick's IN PROGRESS marker
  1b0c1f8) — remote moved 037fc0a → 76c47fa, verified via ls-remote
  (remote head = 76c47fa3bc63a9b45e5baf15eebb7c54957770f9 = local HEAD
  at push time).

## E-062 — Context injection discipline (DONE, 2026-10-31)

- Discipline filed at `docs/architecture/E-062_CONTEXT_INJECTION_DISCIPLINE.md`
  and in code at `Verdandi/context_budget.py` (stdlib-only, standalone
  like event_contract.py): only four sources may be injected, all from
  the one state dir — current.json, conversation_log.jsonl recent
  summaries (one line per session), the nerve_feed.jsonl file tail
  (never a live hub query), and reactor directives derived from the
  same log; nothing else (no env, no configs, no outside files, no
  credential-shaped material — E-093's custody law starts here).
  When: once, at a job's start, as a starting brief.
- The budget: whole block ≤ **4000 chars**; layers current 1200 /
  recent 700 / nerve 1000 / reactions 1100 (sum = total). Per-item
  caps in both dimensions (decisions/next ≤5 items, blockers ≤10,
  projects ≤10; items ≤120 chars, projects ≤60; joined lines also
  capped — blockers 600, decisions/next/projects 300 — so blockers
  at full allowance always fit the current layer alone); summaries
  ≤120 / recent ≤100; max_sessions clamped to ≤5; nerve ≤10 events
  (data ≤100, source/type ≤60); reactions ≤6 directives × ≤3 items
  (≤120 each). Shedding: reactions first, then nerve (oldest first),
  then recent (oldest first), current last — inside current, projects
  shed first and blockers last; every cut leaves the marker
  `[... truncated by context budget E-062]` in the block.
  Supplementary layers stay failure-silent.
- `get_context_for_cron` rebuilt in layers in conversation_logger.py
  (budget literals as deployed literals, E-061 pattern, pinned equal
  to context_budget.py by 23 pairings in the conformance tests).
  Two defects fixed in scope: (a) nerve tail + reactor were read
  from a second hardcoded `Path.home()/.hermes/state` instead of the
  logger's own STATE_DIR — silently divergent for any redirected
  state dir; now both read STATE_DIR (identical under the default);
  (b) context_injector's extra CURRENT STATE echo printed blockers
  and next actions unbounded — now under the same caps. E-057 table
  re-measured for the Verdandi weight change (181 files /
  16,852,579 B; total 131,246,538 B; laptop miss 75,363 B), both
  published copies updated. No new docket items; no README touched.
- Conformance: `tests/unit/test_context_injection_e062.py` **18 passed**
  (budget shape, literal pinning, allowed sources, adversarial
  fixtures: full load yields ≤4000 chars with blockers surviving and
  the marker present; flooding reactor proven live from a state-dir
  reactor). Verdandi focal conversation set **101 passed** (identical
  to E-059/E-061; pytest-asyncio from the e005-extras dir, short
  TMPDIR — the hub's Unix-socket paths exceed ~108 chars under the
  deep overlay TMPDIR, failing identically on the unmodified tree,
  proven by stash-and-rerun). Slice gate: Run B **1094 passed,
  6 failed, 25 skipped, 1 warning** (1076 + 18; the 6 are the proven
  environment failures; the first attempt's extra failures were the
  E-057 tests catching this slice's own weight change, fixed by the
  re-measure); Run D **1151 passed, 0 failed, 19 skipped, 1 warning**,
  exit 0 (1133 + 18). Logs in `~/workspace/.verify-tmp/ember-e062/gate/`.
- E-063 next — the conversation logger's law: what is logged, where,
  for whom; retention + the user's delete right (total, provable).
- E-062 push: banking commit 49a43ab pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 8c946b5,
  an ancestor; the push also carried the tick's IN PROGRESS marker
  801bf77) — remote moved 8c946b5 → 49a43ab, verified via ls-remote
  (remote head = 49a43ab528f64c5b950bc2fd42a9d135ef67d6f9 = local HEAD
  at push time).

## E-063 — The conversation logger's law (DONE, 2026-10-31)

- Law filed at `docs/architecture/E-063_CONVERSATION_LOGGER_LAW.md` and in
  code at `Verdandi/logger_law.py` (stdlib-only, standalone like
  event_contract.py / context_budget.py): what is logged is exactly four
  entry kinds (start / event / update / end) with named fields and the
  eight EVENT_TYPES; content is caller-supplied and logged verbatim (no
  redaction exists — the custody rule is the writer's, E-093). Where:
  `conversation_log.jsonl` (append-only), `current.json` (latest session's
  snapshot), `conversations/` (created on append, otherwise unused —
  recorded honestly), and the nerve copies (every entry fired as a conv_*
  event into `nerve_feed.jsonl` + rotated archives, plain and gzipped).
  Readers named: the logger's own show/recent/context + public API,
  context_injector, the reactor, Mímir's check (size/count only), Bifröst.
  The core does not read the log; logger→memory stays E-072's question.
- Retention stated from sources, pinned by tests: the logger itself keeps
  everything indefinitely (no age/entry limit, no rotation); the only
  bounds are the heartbeat's size-based hygiene — nerve feed rotates at
  10 MB, Bifröst prunes the log over 50 MB (feed 20 MB, newest lines,
  ≥100 kept), Mímir warns 50 MB / critical 200 MB. That pruning is NOT a
  privacy mechanism and is not session-aware — new docket 100 (session-
  aware pruning or a stated verdict, owned by the E-076 gate review).
- The delete right, built: `conversation_logger.py` gains
  `delete_session` / `delete_all_conversations` + a `delete` CLI
  (`delete --session <id>`; `delete --all --yes`, the --yes required and
  a --all without it exits 2 deleting nothing). Total across log,
  current.json (only if it belongs to the session), the live nerve feed
  and every rotated archive (plain + gz); other sessions, non-conv feed
  events and unattributable lines are kept, the last counted in the
  report, never silently dropped or claimed. Provable: atomic rewrites
  (temp file + os.replace, kept lines byte-for-byte), then a re-read of
  every store — the report claims verified only at zero attributable
  remaining, else exit 1. A deleted session provably no longer reaches
  context injection (test).
- Docket 98 CLOSED: the dead `_update_current` helper is removed, and
  current.json ownership is now uniform law — it belongs to the session
  that started it; a cross-session event/update/end is still logged but
  never rewrites another session's snapshot, and a foreign end entry is
  built from its own arguments alone (previously an event appended to
  another session's lists, an update overwrote its actions, an end
  closed its snapshot and carried its lists).
- E-057 table re-measured for the Verdandi weight change (182 files /
  16,871,542 B; total 131,265,501 B; laptop miss 94,326 B), both
  published copies updated. Conformance:
  `tests/unit/test_logger_law_e063.py` **16 passed**; Verdandi focal
  conversation set **101 passed** (identical to E-059/E-061/E-062;
  pytest-asyncio from the e005-extras dir, short TMPDIR). Slice gate:
  Run B **1110 passed, 6 failed, 25 skipped, 1 warning** (1094 + 16;
  the 6 are the proven environment failures, identical set); Run D
  **1167 passed, 0 failed, 19 skipped, 1 warning**, exit 0 (1151 + 16).
  Logs in `~/workspace/.verify-tmp/ember-e063/gate/`. No README touched.
- E-064 next — stimuli: external events enter as typed stimuli with
  provenance.
- E-063 push: banking commit d257751 pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 1ec6c5b, an
  ancestor; the push also carried the tick's IN PROGRESS marker 7b45729) —
  remote moved 1ec6c5b → d257751, verified via ls-remote (remote head =
  d257751b3228fe6c376b982ee9a2a2093fbbbadc = local HEAD at push time).

## E-064 — Stimuli (DONE, 2026-10-31)

- Discipline filed at `docs/architecture/E-064_STIMULI.md` and in code at
  `Verdandi/stimuli.py` (stdlib-only, standalone like event_contract.py /
  context_budget.py / logger_law.py): external events enter as typed stimuli
  with provenance. Three kinds — time, sensor, message (the roadmap's own
  three) — and seven registered entrances: `time.tick` (heartbeat daemon
  timer), `time.schedule` (cron job start), `sensor.check:*` (the five
  heartbeat checks), `sensor.signal` (the signal handler's five signals),
  `message.operator` (the hub's typed operator entrance), `message.conversation`
  (logger entries), `message.mood_input` (the mood system's four input
  functions). No open fallback: an unregistered name is not a stimulus.
- Provenance is mandatory and channel-bound: a stimulus carries
  {origin (non-empty), channel (one of timer/cron/check/signal/cli/log/direct,
  and it must be its entrance's own channel), at (optional origin timestamp)}.
  `to_event` renders a validated stimulus as a canonical E-061 event
  (`stimulus:<name>`, source = origin, payload + full provenance inside data,
  so provenance survives feed/ring/fallback copies); `from_event` is its
  exact reverse. E-071's privacy rule now has the record it governs.
- The one live entrance built: `nervous_system.publish_stimulus_sync` + the
  `stimulus` CLI command — registry literals inline in the hub (deployed-
  standalone pattern, pinned equal to stimuli.py by tests), entry time
  stamped by the hub. A stimulus that fails validation is rejected and
  publishes NOTHING — no hub write, no feed fallback (a fallback line would
  be exactly an unprovenanced entry).
- Honest bounds: the heartbeat timer/checks still surface inside the legacy
  heartbeat_pulse — this slice registers the shape they enter AS; transport
  rewiring stays E-067's, as E-061 assigned it. No typed stimulus consumer
  yet (the hub set reads them as ordinary canonical events); typed reaction
  is E-065/E-067. New docket 101: the hub's open `publish` path still
  accepts operator events with source optional — making it stimulus-only
  is a breaking change owned by the E-076 gate review, not smuggled in here.
- E-057 table re-measured for the Verdandi weight change (183 files /
  16,889,384 B; total 131,283,343 B; laptop miss 112,168 B), both published
  copies updated. Conformance: `tests/unit/test_stimuli_e064.py` **16 passed**;
  Verdandi focal conversation set **101 passed** (identical to
  E-059/E-061/E-062/E-063; pytest-asyncio from the e005-extras dir, short
  TMPDIR). Slice gate: Run B **1126 passed, 6 failed, 25 skipped, 1 warning**
  (1110 + 16; the 6 are the proven environment failures, identical set);
  Run D **1183 passed, 0 failed, 19 skipped, 1 warning**, exit 0 (1167 + 16).
  The first Run D attempt was killed mid-run (SIGTERM to the harness at
  ~36%, no summary line) and re-run clean — the figures are the re-run's
  own log. Logs in `~/workspace/.verify-tmp/ember-e064/gate/`. No README touched.
- E-065 next — the reflex layer: fast, dumb, safe reactions below cognition.
- E-064 push: banking commit a2e729c pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 649ab88, an
  ancestor; the push also carried the tick's IN PROGRESS marker 8c560a6) —
  remote moved 649ab88 → a2e729c, verified via ls-remote (remote head =
  a2e729c1381601d40a495aec8562d7fc61fb9748 = local HEAD at push time).

## E-065 — The reflex layer (DONE, 2026-10-31)

- Discipline filed at `docs/architecture/E-065_REFLEX_LAYER.md` and in code
  at `Verdandi/reflexes.py` (stdlib-only, standalone like event_contract.py /
  context_budget.py / logger_law.py / stimuli.py): the reactions below
  cognition are registered and bounded. Five reflexes — auto_push,
  auto_restart, auto_cleanup, auto_heal, preemptive_heal — mapped by the
  heartbeat Reactor's six rules onto five checks; each spec states trigger
  checks, floor severity, effect and BaseAction cooldown, pinned equal to
  the live ACTION_REGISTRY, each action class's declared fields, and the
  Reactor's rule set by the conformance tests. The three words made
  testable: FAST (deterministic rule match, no model, no core import),
  DUMB (fixed rules; an unregistered action is not a reflex), SAFE (WARNING
  floor — OK/UNKNOWN fire nothing — positive cooldown, dry-run honoured,
  and every reflex runs through BaseAction.execute's wrapper: no registered
  action overrides execute(), pinned). NEVER SPEAKS: a reflex's only output
  is the ActionResult record; validate_reflex_result refuses any record
  carrying a speech field or an unregistered name (the Heimdall doc-05
  instinct applied). Directives propose (conversation reactor), reflexes
  act, cognition speaks.
- **Docket 31 CLOSED** — Vör (preemptive_heal) repaired in
  `heartbeat/actions/vor_action.py`: should_trigger / _get_capacity_prediction
  / _get_capacity_summary guard Skuld's string capacity shapes
  ({"status": "no_resource_data"} / "insufficient_data") with the isinstance
  guard Skuld's own consumer uses, plus a non-dict emotion guard; both
  ActionResult constructions use action_name= (was name=) and the no-action
  return is ActionSeverity.SKIPPED (was the nonexistent INFO); execute()
  became _execute() so the reflex runs under BaseAction's wrapper, with
  trigger_checks=["prediction"] / trigger_severity=WARNING /
  cooldown_seconds=300 declared like its siblings. Vör's FIRST tests land
  in this slice's conformance suite (string shapes, real urgency, capacity
  helpers, SKIPPED record, wrapper dry-run, one real pre-emptive path).
- **Docket 95 CLOSED** — the conversation reactor's react(focus=…) was
  accepted and silently ignored for its whole life; it now applies
  FOCUS_MAP (each focus keeps exactly its category + its directive, other
  categories returned empty, shape unchanged, the context injector's
  react() call untouched) and an unknown focus raises ValueError.
- No new reflex added; no trigger, floor, cooldown or effect changed;
  no new docket items. Transport (E-067), nerve health incl. dockets
  96/34 (E-066) and backpressure (E-070) keep their owners.
- E-057 table re-measured for the Verdandi weight change (184 files /
  16,903,436 B; total 131,297,395 B; laptop miss 126,220 B), both
  published copies updated. Conformance:
  `tests/unit/test_reflex_layer_e065.py` **18 passed**; Verdandi focal
  conversation set **101 passed** (identical to E-059–E-064) and heartbeat
  set **374 passed** (identical to E-060; pytest-asyncio from the
  e005-extras dir, short TMPDIR). Slice gate: Run B **1144 passed,
  6 failed, 25 skipped, 1 warning** (1126 + 18; the 6 are the proven
  environment failures, identical set, verified in three runs); Run D
  **1201 passed, 0 failed, 19 skipped, 1 warning**, exit 0 (1183 + 18).
  Logs in `~/workspace/.verify-tmp/ember-e065/gate/`. No README touched.
- E-066 next — nerve health: a stuck/dead nerve is detected and reported;
  the hub degrades honestly.
- E-065 push: banking commit 06aff9b pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was a2e729c, an
  ancestor; the push also carried E-064's push-record commit 9c75234 and
  the tick's IN PROGRESS marker 1ad8f3a) — remote moved a2e729c → 06aff9b,
  verified via ls-remote (remote head =
  06aff9b18c9f4635cf8d9a691350b84fcb6735d3 = local HEAD at push time).

## E-066 — Nerve health (DONE, 2026-10-31)

- Discipline filed at `docs/architecture/E-066_NERVE_HEALTH.md` and in code
  at `Verdandi/nerve_health.py` (stdlib-only, standalone like
  event_contract.py / context_budget.py / logger_law.py / stimuli.py /
  reflexes.py): the hub's state is classified from stated observations
  (process aliveness and ping response tri-state — unobserved is None,
  never invented) into exactly five states — healthy (alive, pong, no
  warnings), degraded (answers, but a warning holds: feed ≥80% of its
  10 MB rotation threshold, feed missing, log unwritable, or never
  probed), stuck (alive/socket present but no pong, or a live process
  with no socket), dead (PID file stands, process gone), absent (not
  running) — each with its deciding reasons, warnings, and a plain
  degrade-behaviour sentence (`validate_classification` refuses a
  mismatched behaviour). Dead/stuck are judged before degraded/healthy,
  so a warning can never mask a silent hub; an unprobed hub is never
  called healthy. Hermes baseline socket failures (E-059 §8) are the
  slice's cautionary fixture; detection never restarts anything.
- **Docket 96 CLOSED** — `get_status()` probed the hub by publishing a
  real `ping` event (stamped, fed, broadcast on every status check).
  New `nervous_system.ping_hub()` sends only the `nerve_type: ping`
  control message and accepts only `pong`; healthcheck uses it (stuck
  wording named), `get_status` uses it and now reports `nerve_health`
  (inline classifier in the deployed-standalone pattern, pinned equal
  to nerve_health.py on a nine-case matrix), and the status CLI prints
  it. Test-proven degrade honesty: `get_status` on an absent hub leaves
  a seeded feed byte-identical and reports `absent`; on a stale-PID hub
  it reports `dead`. The E-061 contract's `ping` spec is re-registered
  defect → legacy (no current producer; pre-E-066 feed lines keep their
  explanation). Degrade shapes pinned as they stand: hub-unreachable
  publishes return marked `_fallback` feed writes (never `ack`), stuck
  publishes return `sent / no_ack`, recent reads fall back to the feed
  file, subscribe refuses plainly when the hub is not running.
- **Docket 34 CLOSED** — Skuld now reads `pulse_metrics`: the daemon
  has written a real per-pulse `health_score` every pulse since v0.3.0
  and nothing ever read it (E-009); Skuld approximated scores from
  pulse_history state names instead. `_get_pulse_metrics` +
  `_health_score_series` in `heartbeat/checks/skuld.py` feed the trend,
  anomaly and emotion paths from the metrics series, each result
  carrying `score_source` (`pulse_metrics` / `pulse_history_state`);
  the metrics-less fallback reproduces the old state-score behaviour
  exactly (test-pinned). Capacity still reads pulse_history by design
  (its resource percentages live in checks_json, which pulse_metrics
  does not carry — stated in code and doc). E-060's WIRE decision
  executed; E-076's gate verifies.
- No new docket items. Transport rewiring (E-067), backpressure
  (E-070), and dockets 100/101 (E-076 gate review) keep their owners.
- E-057 table re-measured for the Verdandi weight change (185 files /
  16,919,924 B; total 131,313,883 B; laptop miss 142,708 B), both
  published copies updated. Conformance:
  `tests/unit/test_nerve_health_e066.py` **19 passed**; Verdandi focal
  conversation set **101 passed** (identical to E-059–E-065) and
  heartbeat set **374 passed** (identical to E-060/E-065; pytest-asyncio
  from the e005-extras dir, short TMPDIR). Slice gate: Run B **1163
  passed, 6 failed, 25 skipped, 1 warning** (1144 + 19; the 6 are the
  proven environment failures, identical set); Run D **1220 passed,
  0 failed, 19 skipped, 1 warning**, exit 0 (1201 + 19). Logs in
  `~/workspace/.verify-tmp/ember-e066/gate/`. No README touched.
- E-067 next — cross-member nerves: ember core ⇄ Verdandi ⇄ memory
  (Part V) wired under E-061's contract.
- E-066 push: banking commit 471cc9d pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 06aff9b, an
  ancestor; the push also carried E-065's push-record commit b5a668b and
  this tick's IN PROGRESS marker 905da16) — remote moved 06aff9b → 471cc9d,
  verified via ls-remote (remote head =
  471cc9dccc8fdb7ff053b74f04623a2539f13acb = local HEAD at push time).

## E-067 — Cross-member nerves (DONE, 2026-10-31)

- Wiring filed at `docs/architecture/E-067_CROSS_MEMBER_NERVES.md`, registry
  in code at `Verdandi/cross_member.py` (stdlib-only, standalone like
  event_contract.py): the three legs E-061/E-064/E-066 assigned to this slice,
  wired under contract v1. **Leg 1, heartbeat → hub:** `heartbeat/core.py`
  gains `_send_nerve_event` — pulse + state change now go as canonical v1
  envelopes (literals inline, pinned) to the canonical hub socket
  (runa.sock; `nerve.socket_path` override still honoured), source
  verdandi-heartbeat; `_nerve_fallback_file` writes the canonical envelope
  + hub fallback stamps for BOTH events — the state change's legacy shape
  had NO fallback and was silently lost (E-059 §8). **Docket 93 COMPLETE.**
  **Leg 2, logger → hub in-tree (docket 94, E-067 half CLOSED):**
  `conversation_logger._nerve_candidate_paths()` — deployed
  ~/.hermes/state copy first (behaviour unchanged where deployed, pinned),
  sibling in-tree copy second; the standalone half stays E-073's.
  **Leg 3, core → hub (the core's first nerves):** new `src/ember/nerve.py`
  bridge (stdlib only, never raises, ack/sent/fallback/error honesty) +
  chat.run wired at session start, each completed turn, and session end
  (finally block): `ember_session` / `ember_turn` events carry FACTS ONLY —
  the turn's memory facts (Well hits, cited chunks, persisted =
  well/journal/memory_only, ungrounded, outcome from the diary's tags) —
  never content (sentinel-proven in tests). Memory crosses additionally
  inside heartbeat_pulse's checks (the Mimir check, as before in intent).
- Registration per the contract's own rule: event_contract gains canonical
  hub specs for heartbeat_pulse / heartbeat_state_change / ember_session /
  ember_turn (pinned equal to cross_member.py); the legacy heartbeat specs
  stay as pre-E-067 feed lines' explanation; the E-061 doc gains a dated
  E-067 addendum naming the new events, and E-061's heartbeat-fire test was
  updated by this slice (the one E-061 assigned the rewiring to) to pin the
  post-rewiring truth across both dialects. The reverse direction is
  honestly publish-only: bridge `read_recent` offered + live-proven, no
  typed subscriber exists, chat does not consume nerves — new **docket 102**
  (nerve-consumption gap) owned by the E-076 gate review. Suite hygiene:
  tests/conftest.py gains an autouse fixture redirecting the bridge's hub
  home to a short per-test /tmp dir (tests must never write the operator's
  live feed; AF_UNIX's ~108-char cap is why short — this slice's first run
  proved the trap with 4 socket failures at deep TMPDIR paths).
- E-057 table re-measured for BOTH changed members (Verdandi 186 files /
  16,935,635 B; core 130 files / 826,913 B; total 131,342,243 B; laptop
  miss 158,419 B), both published copies updated. Conformance:
  `tests/unit/test_cross_member_nerves_e067.py` **21 passed**; prior Part IV
  conformance (E-061 updated + E-062–E-066 + E-057) **116 passed**; Verdandi
  focal conversation set **101 passed** and heartbeat set **374 passed**
  (identical to E-059–E-066 / E-060/E-065; a wider run including
  test_heartbeat_integration scored 418/5, the 5 being that file's
  `cwd=~/Verdandi` subprocess tests — E-005's proven machine-coupling
  family, failing at spawn before any heartbeat code runs). Slice gate:
  Run B **1184 passed, 6 failed, 25 skipped, 1 warning** (1163 + 21; the 6
  are the proven environment failures); Run D **1241 passed, 0 failed,
  19 skipped, 1 warning**, exit 0 (1220 + 21). Logs in
  `~/workspace/.verify-tmp/ember-e067/gate/`. No README touched.
- E-068 next — Hermes-shaped nerves: Verdandi event shapes matched against
  the Hermes hack's volmarr-core session/turn/tool events.
- E-067 push: banking commit 95cfa79 pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 471cc9d, an
  ancestor; the push also carried E-066's push-record commit 93f0913 and
  this tick's IN PROGRESS marker 687e166) — remote moved 471cc9d → 95cfa79,
  verified via ls-remote (remote head =
  95cfa79d4de3acac1654d17c6d886985d187e978 = local HEAD at push time).

## E-068 — Hermes-shaped nerves (DONE, 2026-10-31)

- Match filed at `docs/architecture/E-068_HERMES_SHAPED_NERVES.md`, translation
  registry in code at `Verdandi/hermes_nerves.py` (stdlib-only, standalone like
  event_contract.py): the Verdandi event shapes matched against the Hermes
  hack's volmarr-core session/turn/tool events, read post-refresh from the
  Hermes tree itself (hermes-hack-build HEAD 7b821b2704, plugin v0.26.0;
  verdandi.py publisher + lifecycle.py bridge + verdandi_stimuli.py intake;
  the Hermes tree was NOT modified). **Verdict: NOT one dialect — a documented
  translation.** Transport already one: same hub socket (runa.sock, same state
  dir for the default profile), same outer {type, source, data} keys, one JSON
  line per event — proven live this slice (a Hermes-shaped publish to the real
  hub is stamped, acked, and fed). Payloads differ: Verdandi contract v1 is
  flat data under an outer `v: 1`; Hermes data is an inner envelope
  (schema runeforge.hermes.lifecycle v1, event_id, occurred_at, event,
  context) with the facts one level down in `context`. Unifying would break a
  versioned contract on one side or the other (E-061's bump rule; the Hermes
  envelope is shared by all five volmarr-core publisher families).
- The eight lifecycle types (hermes.session.started / .ended,
  hermes.turn.completed / .failed / .interrupted, hermes.tool.started /
  .completed / .failed) are registered in BOTH hermes_nerves.py (exact context
  fields + hook + kin) and event_contract.EVENT_SPECS (hub dialect, canonical,
  data_fields = the ENVELOPE's fields — the honest wire description); the E-061
  doc gains a dated E-068 addendum naming all eight. `normalize_hermes_event`
  translates losslessly (context → data; envelope metadata → _hermes_*
  provenance keys; type/source/stamps pass through; result passes
  validate_publish) and NEVER renames a Hermes type into a Verdandi one:
  session kinship to ember_session is real but field-poor (no persona /
  conversation / Well facts), turn outcome is type-encoded where ember_turn
  carries an outcome field, and Hermes turns carry no memory facts.
  Delivery asymmetry recorded plainly: Hermes's publisher is fire-and-forget
  (≤1 s write, no ack read, NO feed fallback — an event sent to a down hub is
  gone); any repair is Hermes-side work, not this slice's.
- The reverse direction was already matched: Hermes's stimuli intake reads
  runa_reward / runa_negative / push_reward / conv_event from the hub's
  `recent` in their flat canonical shapes — no translation needed or added.
  New **docket 103**: no Verdandi tool event exists to match the hermes.tool.*
  family — owner E-076 gate review (road a core tool-facts event or record the
  absence as Part IV's verdict). E-069 inherits the _hermes_* provenance keys
  as replay-preservation facts.
- E-057 table re-measured for the Verdandi weight change (187 files /
  16,956,837 B; total 131,363,445 B; laptop miss 179,621 B), both published
  copies updated. Conformance: `tests/unit/test_hermes_nerves_e068.py`
  **12 passed**; prior Part IV conformance (E-061 as addended + E-062–E-067 +
  E-057 pins) **137 passed**; Verdandi focal conversation set **101 passed**
  and heartbeat set **374 passed** (identical to E-059–E-067 / E-060/E-065).
  Slice gate: Run B **1196 passed, 6 failed, 25 skipped, 1 warning**
  (1184 + 12; the 6 are the proven environment failures); Run D **1253
  passed, 0 failed, 19 skipped, 1 warning**, exit 0 (1241 + 12). Logs in
  `~/workspace/.verify-tmp/ember-e068/gate/`. No README touched.
- E-069 next — ordering & replay: events replay deterministically for
  debugging (fixtures).
- E-068 push: banking commit fbbcae9 pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 95cfa79, an
  ancestor; the push also carried this tick's IN PROGRESS marker 7448d2d)
  — remote moved 95cfa79 → fbbcae9, verified via ls-remote (remote head =
  fbbcae99b0e26a6acf049c97e7565c805026df0d = local HEAD at push time).
## E-069 — Ordering & replay (DONE, 2026-10-31)

- Law filed at `docs/architecture/E-069_ORDERING_AND_REPLAY.md` and in code at
  `Verdandi/replay.py` (stdlib-only, standalone like event_contract.py): events
  replay deterministically for debugging. **The order:** sequenced events first
  by the hub's own `_seq` ascending (file index breaks duplicate-`_seq` ties —
  `_seq` order IS the hub's broadcast order, E-059/E-061); unsequenced events
  after them by effective timestamp (`_ts`, else `_iso`, else the legacy
  `timestamp` — numeric or ISO, naive read as UTC, stated), file index breaking
  ties, untimestamped last in file order. No sequence is ever invented for a
  fallback or legacy event, and their after-the-block placement is a stated
  rule, not a wall-clock reconstruction (the honest limit, in the doc).
- **Reading + reporting:** `load_feed_lines`/`load_feed_text` parse JSONL
  without raising — blank lines skipped, corrupt lines (invalid JSON /
  non-object) skipped and reported by 1-based line number, never hidden and
  never fatal. Every replay reports the ordered events, a SHA-256 **digest**
  of their canonical lines (sorted keys, fixed separators — same feed, same
  digest, even from a shuffled copy of its sequenced events, test-proven),
  the `_seq` range, **gaps** (the holes the E-061 fallback design promises),
  duplicate `_seq` values, unsequenced/`_fallback` counts, and per-dialect
  counts. `replay_to` hands each event to a consumer exactly once in replay
  order and propagates sink failures. Replay edits nothing and re-publishes
  nothing: legacy shapes, stimulus provenance (E-064), the raw Hermes inner
  envelope and the translated `_hermes_*` keys (E-068's handoff, discharged)
  all survive byte-for-byte at the value level, test-pinned.
- No new docket items; dockets 100/101/102/103 keep their E-076 owner, and
  E-070 inherits the report shape (a shedding hub's gaps can be checked
  against it). E-057 table re-measured for the Verdandi weight change
  (188 files / 16,968,259 B; total 131,374,867 B; laptop miss 191,043 B),
  both published copies updated. Conformance:
  `tests/unit/test_ordering_replay_e069.py` **19 passed**; prior Part IV
  conformance (E-061–E-068 + E-057 pins) **149 passed**; Verdandi focal
  conversation set **101 passed** and heartbeat set **374 passed**
  (identical to E-059–E-068 / E-060/E-065; pytest-asyncio from the
  e005-extras dir, short TMPDIR). Slice gate: Run B **1215 passed,
  6 failed, 25 skipped, 1 warning** (1196 + 19; the 6 are the proven
  environment failures, identical set); Run D **1272 passed, 0 failed, 19 skipped, 1 warning**, exit 0.
  Logs in `~/workspace/.verify-tmp/ember-e069/gate/`. No README touched.
- E-070 next — backpressure on tiny hardware: a flooded hub sheds by
  rule, reflexes first-protected.
- E-069 push: banking commit 7908770 pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 7d91cf4, an
  ancestor) — remote moved 7d91cf4 → 7908770, verified via ls-remote
  (remote head = 7908770607da92349e7481bbd040c3135feb36db = local HEAD
  at push time).

## E-070 — Backpressure on tiny hardware (DONE, 2026-10-31)

- Law filed at `docs/architecture/E-070_BACKPRESSURE.md` and in code at
  `Verdandi/backpressure.py` (stdlib-only, standalone like event_contract.py):
  a flooded hub sheds by rule, reflexes first-protected. **The tiers:**
  0 protected (`heartbeat_pulse`, `heartbeat_state_change` — the events
  E-065's reflexes fire on), 1 high (conv_start/conv_end, ember_session,
  ember_turn, Hermes session/turn events, hermes.tool.failed — a failure is
  a fact), 2 normal (conv_event, conv_update, Hermes tool started/completed,
  reward events, and deliberately any unregistered/operator type — the open
  vocabulary is never punished), 3 low (the mood families `event:*`,
  `stimulation:*`, `thought:*`, `location:*`, `orgasm`, retired `ping`).
  Names read from type/event_type/event so every dialect tiers by one table.
- **Admission (one rule):** not full → accept; full → compare with the
  lowest-tier oldest queued event: better tier evicts it, equal tier evicts
  the oldest of that tier (the old ring's FIFO kept inside a tier), worse
  than everything queued → the incoming event itself is shed. Before this
  slice the hub's only backpressure was `deque(maxlen=256)` blindly evicting
  the oldest event with no record; now every shed is counted per tier and
  per kind, `protected_shed` is its own counter (a protected event sheds
  only when the ring holds nothing but protected events — the last resort,
  reported, not hidden), and `apply_backpressure` returns the shed events
  in loss order so E-069's replay gap report can be checked against them.
  Pressure words (calm <70% / pressured 70–99% / full) are report
  vocabulary only; admission is by tier alone. The feed is untouched
  (shedding governs the recent tail, not the archive); publishers are not
  throttled and broadcast order is unchanged — stated as honest limits.
- **Live hub:** `nervous_system.RingBuffer` applies the same rule inline
  (inline tier table, as with nerve health E-066, because that file is
  loaded file-by-file), exposing `shed_count` / `protected_shed_count`;
  typeless events tier normal, so its long-standing FIFO behaviour for
  generic events is unchanged and the existing Verdandi ring tests pass
  unmodified. No new docket items; dockets 100/101/102/103 keep their
  E-076 owner, now with shedding counters to review.
- E-057 table re-measured for the Verdandi weight change (189 files /
  16,984,725 B; total 131,391,333 B; laptop miss 207,509 B), both
  published copies updated. Conformance:
  `tests/unit/test_backpressure_e070.py` **18 passed**; prior Part IV
  conformance (E-061–E-069 + E-057 pins) **168 passed**; Verdandi focal
  conversation set **101 passed** and heartbeat set **374 passed**
  (identical to E-059–E-069; focal runs need a SHORT TMPDIR — the long
  workspace TMPDIR makes the hub's unix-socket paths overflow and the
  nervous_system hub tests fail at baseline too, proven by re-running
  one against the stashed pre-slice nervous_system.py). Slice gate:
  Run B first attempt 1232 passed / 7 failed — the extra failure was
  E-067's live-socket test, which passed standalone immediately after;
  Run B re-run **1233 passed, 6 failed, 25 skipped, 1 warning**
  (1215 + 18; the 6 are the proven environment failures, identical set);
  Run D **1290 passed, 0 failed, 19 skipped, 1 warning**, exit 0
  (1272 + 18). Logs in `~/workspace/.verify-tmp/ember-e070/gate/`.
  No README touched.
- E-071 next — privacy of nerves: stimuli provenance never leaks
  across personae (fixtures).
- E-070 push: banking commit eb3c1fd pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 1e0557d, an
  ancestor; the push also carried this tick's IN PROGRESS marker 81938a8)
  — remote moved 1e0557d → eb3c1fd, verified via ls-remote (remote head =
  eb3c1fd8a47f8446a2f34afd929501284d7bd54c = local HEAD at push time).

## E-071 — Privacy of nerves (DONE, 2026-10-31)

- Law filed at `docs/architecture/E-071_NERVE_PRIVACY.md` and in code at
  `Verdandi/nerve_privacy.py` (stdlib-only, standalone like event_contract.py):
  stimuli provenance never leaks across personae. **Bindings are explicit
  only** — `data.persona_id` (the core's ember_session/ember_turn), a
  stimulus's `payload.persona_id` then `provenance.persona_id`, or a session
  binding (`conv_*` types / a `message.conversation` stimulus's
  `payload.session_id`) resolved through a caller-supplied `session_owners`
  mapping; the law invents no mapping. Everything else is SYSTEM (heartbeat,
  Hermes lifecycle — no persona at all, E-068 — time/sensor stimuli) and is
  visible to every persona, provenance intact.
- **The rule:** own-bound → visible whole; cross-persona → withheld
  ENTIRELY (not redacted — even the fact of a touch is private; sentinel
  provenance proven absent from both the serialised view and the report);
  session-bound with no known owner → withheld fail-closed; a `session_id`
  on a non-conversation shape is a correlation id, not a binding (this
  slice's own first test run caught that bug in the first draft of the
  classifier — fixed in both copies before banking, per the
  never-leave-a-bug rule). `filter_events_for_persona` returns visible
  events unmodified in order + a counts-only report (total / visible /
  withheld_cross_persona / withheld_unknown_session — no withheld content,
  provenance, persona or session values). `redact_provenance` serves
  unscoped aggregate views: origin + top-level source → "redacted",
  channel kept, persona binding inside provenance dropped, input unmutated.
  Honest limits stated in the doc: the feed itself is not encrypted or
  rewritten (operator custody, E-020 — this law governs persona-scoped
  VIEWS), and pre-E-071 stimuli with no binding are system-shaped because
  a binding cannot be invented retroactively.
- **Live enforcement:** the core's nerve bridge `src/ember/nerve.py` gains
  `filter_for_persona` (the same classification inline, per that module's
  no-member-imports discipline, pinned equal to nerve_privacy on every
  fixture shape) and `read_recent_for_persona`, which over-fetches the hub
  tail 4× so withholding does not silently shrink a persona's view.
  Dockets 100–103 keep their E-076 owner; no new docket items.
- E-057 table re-measured for both changed members (Verdandi 190 files /
  16,996,351 B; core 130 files / 831,437 B; total 131,407,483 B; laptop
  miss 219,135 B), both published copies updated. Conformance:
  `tests/unit/test_nerve_privacy_e071.py` **18 passed**; prior Part IV
  conformance (E-057 pins + E-061–E-070) **186 passed**; Verdandi focal
  conversation set **101 passed** and heartbeat set **374 passed**
  (identical to E-059–E-070). Slice gate: Run B **1251 passed, 6 failed,
  25 skipped, 1 warning** (1233 + 18; the 6 are the proven environment
  failures, identical set); Run D **1308 passed, 0 failed, 19 skipped,
  1 warning**, exit 0 (1290 + 18). Logs in
  `~/workspace/.verify-tmp/ember-e071/gate/`. No README touched.
- E-072 next — the logger as memory source: logged conversations can
  feed memory (Part V) under the user's rule, never silently.
- E-071 push: banking commit ef30a73 pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was f111dae, an
  ancestor; the push also carried this tick's IN PROGRESS marker 08893bd)
  — remote moved f111dae → ef30a73, verified via ls-remote (remote head =
  ef30a73abdef9028d5eeded089dad4941c9946ae = local HEAD at push time).

## E-072 — The logger as memory source (DONE, 2026-10-31)

- Law filed at `docs/architecture/E-072_LOGGER_AS_MEMORY_SOURCE.md` and in
  code at `Verdandi/memory_feed.py` (stdlib-only, standalone): logged
  conversations can feed memory ONLY under the user's explicit rule, never
  silently. A rule must be user-granted (`granted_by == "user"`), enabled,
  scoped (`named_sessions` with a non-empty session list, or
  `all_sessions` — no default scope), and must name the feedable event
  types it allows; unknown keys or a non-user grant fail closed and feed
  nothing. Feedable: `learned`→lesson, `decision`→decision,
  `milestone`→milestone, plus an `end` summary only when the rule opts in
  (`include_end_summary`). Working-state event types, start/update
  entries, empty content and unattributable entries never feed; exact
  duplicates feed once. Every run returns candidates AND a counts-only
  report (status no_rule / rule_disabled / invalid_rule / fed, plus one
  count per withholding reason — no content, session or persona values),
  so a feed is never silent even when it feeds nothing. Candidates carry
  provenance (log file, entry kind, event type, rule_id) and a persona
  tag only from a caller-supplied session_owners mapping (never guessed).
- Honest limits stated in the doc: this law governs the crossing, not the
  destination — no memory store is written (Part V's E-080 chooses the
  receiving face on top of this law); a session deleted under E-063 feeds
  nothing afterwards (proven live), but already-fed candidates are NOT
  retracted by this law — new **docket 104**, owned by E-085.
- E-057 table re-measured for Verdandi (191 files / 17,009,560 B; total
  131,420,692 B; laptop miss 232,344 B), both published copies updated.
  Conformance: `tests/unit/test_memory_feed_e072.py` **22 passed**;
  the combined conformance run (E-055 + E-057 pins + E-061–E-071 +
  E-072) **234 passed**; Verdandi focal
  conversation **101 passed**. CORRECTION (21:47): the heartbeat focal
  set was NOT verified this tick — the focal run used a broader six-file
  set (eir/skuld added) finishing 451 passed / 6 failed under extreme
  contention, and a clean canonical-four re-run was starved at load
  ~17.9 and killed unverified; the "374 passed" claim is withdrawn and
  the heartbeat set joins the re-verification duty below. Slice gate: Run B **1273 passed, 6 failed, 25 skipped,
  1 warning** (1251 + 22; the 6 are the proven environment failures,
  FAILED-list diff-identical to E-071). Run D: three attempts under heavy
  cross-campaign contention (load 3.0–9.3) — **1325–1326 passed,
  19 skipped**, the only failures the contention-sensitive timing tests
  (idle CPU-tick window ×4 in every attempt; the live-socket bridge test
  in two attempts — it passed isolated and in attempt 2). Run D is
  recorded NOT GREEN under contention: **standing re-verification duty —
  the next keeper tick re-runs Run D AND the canonical heartbeat focal
  set (test_heartbeat*.py, four files) before starting E-073 and records
  the results here; a calm-load green Run D + heartbeat focal closes
  this note.** Logs in
  `~/workspace/.verify-tmp/ember-e072/gate/`. No README touched.
- E-073 next — Verdandi standalone: the hub usable without the full
  companion (its own consumers exist in the constellation).
- E-072 push: banking commit 0482b22 pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was ee4af13, an
  ancestor; the push also carried this tick's IN PROGRESS marker 5204c6f)
  — remote moved ee4af13 → 0482b22, verified via ls-remote (remote head =
  0482b2290d922502391627f83734306abc7f2797 = local HEAD at push time).

## E-072 re-verification (DONE, 2026-10-31, 21:42 keeper tick)

- The standing re-verification duty from E-072 is CLOSED, green on a
  calming load (1-minute load fell 3.88 -> 1.10 across the two runs,
  run sequentially, one at a time): the canonical heartbeat focal set
  (`test_heartbeat*.py`, four files, Verdandi dir, pytest-asyncio from
  the e005-extras dir, short TMPDIR) **374 passed** in 331.46s, exit 0
  — the withdrawn claim is re-proven exactly; and root gate Run D
  (whole suite, extras supplied) **1330 passed, 0 failed, 19 skipped,
  1 warning** in 204.83s, exit 0 — the contention-sensitive timing
  tests that failed under load in E-072 all passed. Logs in
  `~/workspace/.verify-tmp/ember-e072/reverify/` (`heartbeat_focal.log`,
  `run_d.log`). No code touched by this re-verification.
- E-073 next — Verdandi standalone: the hub usable without the full
  companion (its own consumers exist in the constellation).

CORRECTION to the E-072 re-verification entry above (same tick,
later): the counts first recorded there for the heartbeat focal
run came from a mismatched background-run report, not from the
run's own log. Read from the log on disk
(`~/workspace/.verify-tmp/ember-e072/reverify/heartbeat_focal.log`),
that run — the four test_heartbeat*.py files, 388 tests — actually
scored 383 passed, 5 failed in 644.88s. The 5 failures are all
TestCLIIntegration tests whose subprocesses cd to ~/Verdandi,
which does not exist on this VM (FileNotFoundError) — the
pre-existing machine-coupled family of docket item 6 (E-005),
not contention and not a regression. The canonical heartbeat
focal set of E-060–E-071 is heartbeat + actions + checks +
SKULD (374 tests; the E-072 duty text's "test_heartbeat*.py,
four files" parenthetical misdescribed it). Run D's
re-verification stands exactly as recorded (1330 passed,
0 failed — its log agrees). The duty is closed on this
corrected basis by E-073 below: canonical heartbeat set
re-run green post-change, Run D green; the integration
file's 5 CLI failures stay with docket item 6's family,
whose fixing home is Part IV's remaining road / E-076
review, not this slice.

## E-073 — Verdandi standalone (DONE, 2026-10-31)

- Law filed at `docs/architecture/E-073_VERDANDI_STANDALONE.md` and in
  code at `Verdandi/standalone.py` (stdlib-only): the hub usable without
  the full companion. One file is the hub (`nervous_system.py`,
  stdlib-only, Unix-socket transport, eight CLI commands); the wire is
  the E-061 contract, not the companion; consumers named (hub CLI,
  heartbeat reward producers + conversation logger via
  publish_event_sync, the core nerve bridge when present, external
  Hermes publishers per E-068).
- The slice's one repair: the hub's state dir was hard-coded to
  `~/.hermes/state`, so standalone still silently required a
  Hermes-shaped home. Now `VERDANDI_HOME`, when set, IS the hub's
  state dir; otherwise the default is unchanged. The resolution is
  stated in standalone.py and carried inline by the hub module
  (`_resolve_state_dir`, lone-file deployed form) and by the core
  bridge's `hub_state_dir()` (no-member-imports discipline), all
  three pinned equal by the conformance tests incl. subprocess
  imports of the real hub under both env shapes.
- Live proof (this tick, logs in `~/workspace/.verify-tmp/ember-e073/`):
  hub booted by file path alone, HOME=/tmp/e73home (empty),
  VERDANDI_HOME=/tmp/e73state, no PYTHONPATH — socket at the relocated
  home, healthcheck ALL CHECKS PASSED exit 0, publish acked #1,
  recent/status correct, feed held exactly that event, and the
  isolated HOME stayed completely empty (no .hermes, no .ember).
- New docket items: 105 (shipped systemd units hard-code /home/pi +
  ~/.hermes/state paths — Pi deployment shape, not standalone;
  owner E-076) and 106 (hub `stop` reported "could not be killed"
  for a hub in fact killed by its SIGTERM — cmd_stop's
  os.kill(pid, 0) probe is zombie-blind; found by the live proof,
  owner E-076). Honest limits in the doc: the heartbeat's
  VERDANDI_HOME is its own distinct home (not unified — the live
  Hermes deployment's heartbeat would break); pip-install of the
  member NOT PROVEN (standalone proven at file level, as every
  in-tree consumer loads it).
- E-057 table re-measured for both changed members (Verdandi 192
  files / 17,014,457 B; core 130 files / 831,912 B; total
  131,426,064 B; laptop miss 237,241 B), both published copies
  updated. Conformance: `tests/unit/test_standalone_e073.py`
  **12 passed**; combined Part IV conformance (E-055 + E-057 pins +
  E-061–E-073) **246 passed**; Verdandi focal conversation set
  **101 passed**; canonical heartbeat set **374 passed** (6.02s,
  disk-verified from the gate log). Slice gate: Run B **1285
  passed, 6 failed, 25 skipped, 1 warning** (1273 + 12; the 6 are
  the proven environment failures, identical set); Run D **1342
  passed, 0 failed, 19 skipped, 1 warning**, exit 0 (1330 + 12).
  Logs in `~/workspace/.verify-tmp/ember-e073/gate/`. No README
  touched.
- E-074 next — Docs: the nerve model for member-builders.
- E-073 push: banking commit 0733d2b pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 7b13faf,
  an ancestor; the push also carried this tick's IN PROGRESS marker
  2b2ea81 and the E-072 re-verification correction) — remote moved
  7b13faf → 0733d2b, verified via ls-remote (remote head =
  0733d2bf7e4b17a812e6d798077ba842c293ea78 = local HEAD at push time).

## E-074 — Docs: the nerve model for member-builders (DONE, 2026-10-31)

- Builder's guide filed at `docs/architecture/E-074_NERVE_MODEL_FOR_MEMBER_BUILDERS.md`:
  the one reading of the whole Part IV nerve model, adding no new law.
  It states the model in one paragraph + a shape diagram (hub =
  `Verdandi/nervous_system.py`, state dir `VERDANDI_HOME` else
  `~/.hermes/state`, socket `runa.sock`, feed `nerve_feed.jsonl`),
  a builder's entry-point table (15 files x their public entry
  points, each row naming its law slice E-061-E-073), the five
  rules (canonical envelope E-061; stimuli with provenance E-064;
  context + backpressure budgets E-062/E-070; logger/privacy/memory
  laws E-063/E-071/E-072; reflexes speechless below cognition
  E-065, honest degradation E-066, Hermes translation E-068,
  deterministic replay E-069), the holding disciplines
  (file-by-file loading, stdlib-only, fail-closed, counts-only
  reports), an 8-step new-member checklist, and honest limits
  (no typed subscriber SDK — docket 102; open publish may omit
  source — docket 101; dockets 100/103/105/106 open with owners;
  throughput numbers are E-075's, none invented here; member
  install-from-package NOT PROVEN per E-073).
- Three worked examples in the doc (stimulus -> valid canonical
  event; persona privacy filter; replay digest determinism) run
  as written from the repo root. Conformance:
  `tests/unit/test_nerve_model_docs_e074.py` **5 passed** — it
  also verifies every Part IV slice E-059-E-074 is represented,
  every backticked repo path in the doc exists (>=25 checked),
  and every builder-table symbol is defined at its file's top
  level.
- No member code touched, so the E-057 member budget table is
  unchanged — proven by its pinning tests inside the combined
  run. Combined Part IV conformance (E-055 + E-057 pins +
  E-061-E-074) **251 passed** (246 + 5); Verdandi focal
  conversation set **101 passed**; canonical heartbeat set
  **374 passed**. Slice gate: Run B **1290 passed, 6 failed,
  25 skipped, 1 warning** (1285 + 5; the 6 are the proven
  environment failures, FAILED list identical to E-073);
  Run D **1347 passed, 0 failed, 19 skipped, 1 warning**,
  exit 0 (1342 + 5). Logs in
  `~/workspace/.verify-tmp/ember-e074/gate/`. No README touched.
- E-075 next — Load truth: hub throughput per profile, measured.
- E-074 push: banking commit e8d0e17 pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 1cf41c4,
  an ancestor; the push also carried this tick's IN PROGRESS marker
  12de801) — remote moved 1cf41c4 → e8d0e17, verified via ls-remote
  (remote head = e8d0e17918e9300664bc581a196d9478999c8054 = local HEAD
  at push time).

## E-075 — Load truth: hub throughput per profile (DONE, 2026-10-31)

- Instrument filed in code at `Verdandi/load_truth.py`
  (stdlib-only, standalone) and its reading copy at
  `docs/architecture/E-075_LOAD_TRUTH.md`: the hub's
  throughput measured live, per budget-book profile, the
  profile taken as a benchmark shape (simulation
  envelope, the E-048 method — hub pinned by taskset to
  the profile's CPU count 1/2/4/4, driven by the
  profile's publishers 1/2/4/8 over persistent
  connections, 0/1/1/2 subscribers listening; timed
  bursts 512/512/1024/1024 events plus 32 warmup and 60
  producer-path events per run). Two faces measured:
  persistent (one connection, ack per event) and the
  producer face (a fresh connection per event — the
  exact `publish_event_sync` shape). The whole harness
  ran three times on the campaign VM (Python 3.12.3)
  under sibling-campaign contention (load 5.2–6.3);
  raw reports in `~/workspace/.verify-tmp/ember-e075/`
  (`run1.json`–`run3.json`, solo `toaster.json`).
- Measured truth (medians of three): persistent
  throughput toaster **2735.7**, phone **1660.9**, pi
  **1657.0**, laptop **1747.3** events/s — one publisher
  is the hub's best shape; more publishers queue on the
  one event loop and only latency grows (p95 0.45 →
  14.10 ms toaster → laptop). Producer face flat at
  **566.0 / 640.6 / 636.3 / 655.8** events/s (its cost
  is the connection, not the hub). A solo toaster probe
  in a quieter minute read 5172.8 / 2125.4 — the spread
  is recorded, medians are the citable figures. Hub
  peak RSS **22.6–22.9 MiB** in every shape (E-041's
  21.9 MiB live figure confirmed under load); stamped
  feed lines **~206 bytes/event** in every run.
- Correctness measured with the speed, all twelve
  profile runs error-free: ack `_seq` contiguous
  1..604 (toaster/phone) and 1..1116 (pi/laptop); feed
  lines == published, every run; `recent` answered the
  ring's full 256 after every burst; every subscriber
  received every event published while it listened
  (604/604, 1116/1116, 1116/1116 per laptop
  subscriber). Demand side stated in the doc: a
  heartbeat pulse a minute + a few events per turn is
  five orders of magnitude below the measured floor —
  no profile needs a faster hub.
- New **docket 107**: the per-profile load truth is a
  contended VM simulation; hub throughput on real
  tiny hardware is NOT PROVEN (a real Pi measurement
  is the cheapest re-anchor). Owner: the E-076 gate
  review. E-074's "load truth not in this document"
  limit is discharged by this slice's doc.
- E-057 table re-measured for the Verdandi change
  (Verdandi 193 files / 17,030,199 B; core unchanged
  130 / 831,912 B; total 131,441,806 B; laptop miss
  252,983 B), both published copies updated.
  Conformance: `tests/unit/test_load_truth_e075.py`
  **8 passed** (incl. a live mini-run against the real
  hub: contiguous seqs, feed == published, subscriber
  window, RSS > 0). Combined Part IV conformance
  (E-055 + E-057 pins + E-061–E-075) **259 passed**
  (251 + 8); Verdandi focal conversation set **101
  passed**; canonical heartbeat set **374 passed**.
  Slice gate Run B **1298 passed, 6 failed, 25
  skipped, 1 warning** (1290 + 8; the 6 are the proven
  environment failures, FAILED list identical to
  E-074). Logs in
  `~/workspace/.verify-tmp/ember-e075/gate/`.
- Run D is recorded **NOT GREEN under extreme
  contention** (the E-072 pattern): attempt 1 ran with
  a non-canonical PYTHONPATH (this tick added the
  e005 member-test extras dir to the canonical
  src + ember-extras shape) and scored **1351 passed,
  4 failed** — all four the E-045 idle-window test's
  thread count (4 vs 1), proven an artifact of that
  extras dir by an A/B driver run (canonical shape:
  Threads 1 throughout; with the e005 dir added:
  Threads 4 from the first sample; CPU ticks passed
  in both). Attempt 2, canonical shape: **1354
  passed, 1 failed, 19 skipped, 1 warning** — the one
  failure the E-046 cold-start median test, with the
  1-minute load spiking to **33.15** during the run;
  its isolated re-run at load 9.5–16.9 still starved
  (median 13.43 s vs the 5.00 s cap; E-046's anchor
  median was 2.87 s at load ~8, E-032's quiet run
  0.93 s). E-075 touched no core or hub code, so no
  regression is in scope: **standing re-verification
  duty — the next keeper tick re-runs Run D
  (canonical shape) and the cold-start test before
  starting E-076 and records the results here; a
  calm-load green Run D closes this note.**
- Environment note: at this tick's start, git
  loose-object writes failed with EPERM for ~2
  minutes (plain file writes unaffected, a fresh repo
  in /tmp unaffected by the end); the IN PROGRESS
  marker commit landed on retry (31993df). No work
  was lost; recorded so a recurrence is recognised.
- E-076 next — Part IV gate (after the re-verification
  duty above).
- E-075 push: banking commit 59f740b pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was d04fa5a, an
  ancestor; the push also carried this tick's IN PROGRESS marker 31993df)
  — remote moved d04fa5a → 59f740b, verified via ls-remote (remote head =
  59f740bce1373c2ee9bcfbf4a99901431fad891e = local HEAD at push time).

## E-076 — Part IV gate (DONE, 2026-11-01)

- Gate filed at `docs/architecture/E-076_PART_IV_GATE.md`:
  **Part IV gate PASS** — all seven criteria checked (G1–G7).
  VD-RM's remaining road is fully accounted: the E-060
  retirements (distributed heartbeat, REST API) and
  double-count strikes (Prometheus, emotional architecture)
  stand; v0.4.0 "Valhalla" stands closed; `pulse_metrics`
  verified CLOSED live at this gate (a real
  `heartbeat.cli pulse` reported prediction + anomalies with
  `score_source: 'pulse_metrics'`); VD-RM v1.0.0 "Yggdrasil —
  Production-ready" re-roaded with five stated criteria to
  its judging owner **E-204** (rows a/b/d true today; the
  real-device load truth and the E-199 showcase rows are
  future evidence). Event contract v1 declared **FROZEN**
  at this gate on E-061's own versioning terms (breaking
  change = version bump, never an edit; new types register
  with their producer; the E-067/E-068 addenda are part of
  the frozen registry; docket 103's absence is the v1
  verdict).
- Three repairs landed in scope — the gate review owned all
  three, and a gate that owns a bug does not merely describe
  it. **Docket 106 CLOSED:** the hub's `cmd_stop` aliveness
  probe was zombie-blind (`os.kill(pid, 0)` answers True for
  a zombie), so a SIGTERM-killed hub was reported "could not
  be killed"; `nervous_system.py` gains `_pid_alive` (reads
  the /proc state, zombie = dead, kill-probe fallback where
  /proc is absent), proven against a real forked zombie, a
  zombie pid file through `cmd_stop` itself, and a live
  sleeper. **Docket 92, Verdandi half CLOSED:**
  `Verdandi/pyproject.toml`'s two unbounded requirements
  (`pytest-asyncio>=0.23`, `setuptools>=68.0`) are bounded
  both ways (`<2`, `<82`), pinned by conformance. **Docket 6
  family CLOSED for the CLI file:**
  `Verdandi/tests/test_heartbeat_integration.py`'s five CLI
  tests no longer run in `Path.home() / "Verdandi"` (exists
  only on the Pi deployment — the 5 failures of the E-072
  correction) but in the member's own dir derived from
  `__file__`; the pulse/react pair additionally runs against
  an isolated HOME + VERDANDI_HOME, because a pulse judges
  its host (Huginn scanned this VM's 175 home git repos in
  1m52s wall and `pulse` exits 1 on a critical pulse state).
  All five pass in ~5 s.
- Carried with owners, not lost: docket 100 → E-136 (with
  the gate's stated verdict: Bifröst pruning is hygiene,
  never privacy; E-063's delete right is the privacy
  instrument), 101 → E-187 (stimulus-only publish is a v2
  question), 102 → E-085 first review / E-204 backstop,
  103's v2 candidacy → E-204, 104 → E-085 (as E-072
  assigned), 105 → E-182 (native deploy recipes rewrite the
  systemd units), 107 → E-191 (load truth on a real device,
  criteria in the gate doc). NOT PROVEN at this gate: hub
  throughput on real tiny hardware, a typed nerve
  subscriber, the v1.0.0 claim.
- The E-075 re-verification duty is DISCHARGED (gate §5):
  re-run at this tick's opening under 1-minute load
  25.4–27.2 — Run D attempt **1354 passed, 1 failed**, the
  one failure (load-truth mini-run, "hub exited early
  rc=1") proven a method artifact of that attempt's deep
  workspace TMPDIR (socket path over the AF_UNIX cap;
  isolated short-TMPDIR re-run of the file **8 passed**);
  isolated cold-start at that load failed honestly (median
  8.66 s vs 5.00 s cap, the E-075 contention shape). The
  gate's own canonical Run D (short TMPDIR) is the closing
  run — green, both duty tests inside it. No
  re-verification duty carries past this gate. Logs in
  `~/workspace/.verify-tmp/ember-e076/reverify/` +
  `gate/`. (One crossed background notification during
  this tick reported a phantom "422 passed, 1 failed" for
  the heartbeat set; disk truth was used throughout — the
  intermediate run's own log reads 421 passed / 2 failed,
  the final 423 / 0.)
- E-057 table re-measured for this slice's Verdandi
  changes (Verdandi 193 files / 17,032,082 B; core
  unchanged 130 / 831,912 B; total 131,443,689 B; laptop
  miss 254,866 B), both published copies updated.
  Conformance: `tests/unit/test_part_iv_gate_e076.py`
  **7 passed**; combined Part IV conformance (E-055 +
  E-057 pins + E-061–E-076) **266 passed** (259 + 7);
  Verdandi heartbeat + Skuld + integration set
  **423 passed**, exit 0 (canonical 374 + integration 49,
  one run, final tree); Verdandi conversation focal set
  **101 passed**. Slice gate: Run A **1 error, 11
  skipped**, exit 2 (docket 1, unchanged); Run B **1305
  passed, 6 failed, 25 skipped, 1 warning** (1298 + 7;
  the 6 are the proven environment failures, FAILED list
  identical to E-075); Run D **1362 passed, 0 failed, 19
  skipped, 1 warning**, exit 0 (1355 + 7). No README
  touched.
- **Part IV CLOSED.** E-077 next — Part V opens: both
  memory systems mapped.
- E-076 push: banking commit cdf4e04 pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 59f740b, an
  ancestor; the push also carried E-075's push-record commit 1c2fb2b and
  this tick's IN PROGRESS marker f27683e) — remote moved 59f740b →
  cdf4e04, verified via ls-remote (remote head =
  cdf4e04777a74b95da9719f2f9545ca51b054e37 = local HEAD at push time).

## E-077 — Both memory systems mapped, in depth (DONE, 2026-11-01)

- Map filed at `docs/architecture/E-077_BOTH_MEMORY_SYSTEMS_MAPPED.md`:
  E-012 executed in depth for **three** systems — mempalace,
  mimir-well, and the core's own Brunnr, the incumbent Part V
  must judge alongside the two members. Headline proven facts:
  neither member has changed by one byte since its import
  (git log: one commit each, f7ef473 / 911eeba, 2026-05-21;
  tracked sizes byte-identical to E-057 as re-pinned at E-076 —
  mempalace 257 files / 59,049,715 B, mimir-well 58 /
  607,675 B, pinned by this slice's conformance); the core
  still uses neither member (zero references in `src/ember/`);
  storage shapes stated exactly (mempalace: palace directory,
  Chroma drawers+closets over chroma.sqlite3 + HNSW, separate
  KG SQLite, 384-dim ONNX MiniLM; mimir-well: one SQLite file,
  schema v9, 10 tables + 3 FTS5, the living `memories` row;
  Brunnr: sqlite_vec / pgvector schema.sql shapes, documents /
  chunks / episodes, 768-dim Ollama embed via Smidja);
  retrieval stated exactly (mempalace hybrid 0.6 vector /
  0.4 BM25 + closet boost + BM25-only fallback + Layers 0-3,
  MCP exactly 30 tool_* functions; mimir-well FTS5 + structured
  recall, no vector code anywhere; BrunnrHandle exactly 12
  protocol methods, RRF hybrid with E-036's tie-break).
- New consumer evidence beyond E-012: bifrost carries **two**
  independent raw-SQL consumers of mimir-well's shape (bridge
  `memory_bridge.py` + core `core.py:_ensure_mimir` via
  `config.mimir_db_path`), neither through `RunaMemory` —
  docket 51's three-path disagreement stands exactly (library
  `~/.mimir_well/mimir_well.db` vs Eye/bifrost
  `~/.hermes/memory/runa_memory.db`; Verdandi's check alone
  follows the library). New dockets: 108 (mimir-well's flask
  dep bounded below only — E-044 law unapplied; Part V hygiene),
  109 (four readers/writers of the mimir shape, zero via its
  own class; E-080 owner, Part VIII consulted), 110 (Brunnr
  episodes carry no conversation/persona column at the adapter
  layer; E-080/E-083 owner).
- Test state fresh this slice: mimir-well full suite
  **350 passed, 6 failed** — identical to E-005/E-012, the 6
  being docket 10's Eye family; its recall-quality file ran
  **21 passed** at calm load, proving this tick's earlier
  apparent latency failures (two <50 ms wall-clock tests,
  starved at load 6-11 by sibling suites) the contention
  class. mempalace focal five files (searcher / hybrid /
  KG / layers / closets) **170 passed** with the proxy env
  cleaned; the dirty-proxy shape (134 / 20F / 16E) is
  E-005's httpx `Invalid port: ':1]'` signature throughout.
  mempalace's full suite NOT re-run (member byte-identical;
  E-012's corrected 1712 / 14 / 1 / 106 stand; E-078 owns
  the next full measurement under docket 54). Brunnr focal
  + conformance 25 tests: 24 passed + this slice's own
  conformance assertion error (bifrost path literal lives
  in `bifrost/config.py`, not `core.py` — §6 already said
  so), fixed in scope; conformance then **8 passed**.
- Environment note: the E-075 write transient recurred
  (~01:12, minutes of EPERM/ENOENT on scattered writes +
  Python tempfile creation, /tmp carrying 7,258 sibling
  entries); it cleared on its own, no work lost — doc and
  test verified on disk via git status before banking.
- Slice gate: Run A **1 error, 11 skipped**, exit 2
  (docket 1, identical to E-076); Run B **1312 passed,
  7 failed, 25 skipped, 1 warning** (1305 + 8 new − 1:
  the 6 proven environment failures, identical list,
  plus `test_load_truth_e075`'s mini-run failing
  "hub exited early rc=1" — E-076's proven deep-TMPDIR
  socket-cap artifact, isolated short-TMPDIR re-run
  **8 passed**, no hub code touched); Run D **1370
  passed, 0 failed, 19 skipped, 1 warning**, exit 0
  (1362 + 8). Logs in `~/workspace/.verify-tmp/ember-e077/`.
  No README touched.
- **Part V OPEN.** E-078 next — the comparison harness.
- E-077 push: banking commit fdb3197 pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was ee01b1e,
  an ancestor; the push also carried this tick's IN PROGRESS marker
  c1de031) — remote moved ee01b1e → fdb3197, verified via ls-remote
  (remote head = fdb31972f1c136aa9c05e8c5684eeac47d4498a0 = local HEAD
  at push time).

## E-078 — The comparison harness (DONE, 2026-11-01)

- Harness + record filed at `scripts/dev/compare_memory_systems.py` and
  `docs/architecture/E-078_MEMORY_COMPARISON_HARNESS.md`: identical
  synthetic workloads (20 facts + paraphrases + supersession + episodes)
  through all three systems — mempalace, mimir-well, Brunnr — one corpus,
  one query set, embedder held constant (ONNX all-MiniLM-L6-v2; no Ollama
  reachable on the VM). Canonical run 2 numbers (raw reports in
  `~/workspace/.verify-tmp/ember-e078/`): verbatim/term recall **20/20 all
  three**; paraphrase mempalace **9/9**, Brunnr vector **9/9** / hybrid
  **8/9**, mimir-well **0/9** (no semantic search — a measured absence);
  only mimir-well answered importance/mood/current-truth exactly; only
  Brunnr holds episodes as turns. Weight: mimir-well fits every profile;
  mempalace fits none (~403 MiB peak RAM, ~185 MB deps + ~88 MB model).
- **Bug found and fixed in scope — new docket 111:** mimir-well's FTS5
  external-content tables had no sync triggers (schema.py's comment
  claimed the opposite), so `fts_search` was blind to everything written
  in the running session (as found: 0/20 verbatim, 0/20 term; LIKE 20/20).
  Fix: `FTS_TRIGGERS` (insert/delete/update ×3 tables) in schema.py +
  executed at open in core.py before the rebuild; regression suite
  `mimir-well/tests/test_fts_sync.py` **6 passed** (re-verified this
  tick). Post-fix FTS **20/20 / 20/20**. Consequences pinned: E-077 size
  pin moved (59 files / 614,283 B), E-057 budget table + BUDGET_BOOK §7
  re-measured (twelve-member total 131,450,297 B).
- Test state: harness canonical run 2 all three children `ok`;
  mimir-well full suite post-fix **353 passed, 9 failed** (6 = docket
  10's Eye family, identical to baseline; 3 = hard wall-clock latency
  tests proven environment — overlay fsync under synchronous=FULL,
  same file 21 passed on /tmp; see E-078 doc §7). Root conformance
  `test_memory_comparison_e078.py` 4 tests pass in every gate shape.
- Slice gate (this tick's continuation, fresh runs on the staged tree;
  logs in `~/workspace/.verify-tmp/ember-e078/gate-final/`): Run A
  **1 error, 11 skipped**, exit 2 (docket 1, identical); Run B **1316
  passed, 7 failed, 25 skipped, 1 warning** — the 6 proven environment
  failures (CDE ×3, G ×2, J ×1, identical list) plus
  `test_load_truth_e075`'s mini-run "hub exited early rc=1", E-076's
  proven deep-TMPDIR socket-cap artifact (isolated default-TMPDIR
  re-run this tick **8 passed**; E-078 touches no hub code); Run D
  **1373 passed, 1 failed, 19 skipped, 1 warning** — the sole failure
  is the same load-truth TMPDIR artifact (1370 + 4 new conformance
  − 1 artifact vs E-077's Run D). No README touched.
- **E-079 next** — the verdict paper, argued from these numbers +
  ORIGINS provenance, presented for Volmarr's word.
- E-078 push: banking commit e2cddaf pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 220de89,
  an ancestor) — remote moved 220de89 → e2cddaf, verified via ls-remote
  (remote head = e2cddafe4be11c2c5091b10985066417b03c3c5c = local HEAD
  at push time).

## E-079 — The verdict paper (DONE, 2026-11-01)

- Verdict filed at `docs/architecture/E-079_MEMORY_VERDICT_PAPER.md`:
  **BOUND** — one memory face (contract at E-080) over two bounded
  house engines, argued from E-078's canonical numbers + E-012/E-003
  provenance (neither member has an ORIGINS row, docket 72 — provenance
  stated from packaging + git: mempalace upstream OSS milla-jovovich,
  one import commit f7ef473; mimir-well house line Eldrä Járnsdóttir,
  911eeba; Brunnr house core, real development history).
- Territories: Brunnr keeps documents/chunks/episodes (verbatim 20/20,
  paraphrase 9/9 vector, only exact episode recall, 585 B/episode);
  mimir-well keeps living facts (importance/mood exact, only
  current-truth view, only lifecycle + guard + audit; fits every
  profile — 614,283 B, 24.2 MiB peak, 745 B/item). All three
  single-system crowns argued and refused on measured evidence
  (mempalace: fits no profile — 402.8 MiB RAM, ~185 MB deps + ~88 MB
  model; mimir-well: paraphrase 0/9, no semantic search; Brunnr: no
  importance/mood/current-truth/lifecycle/guard/audit faces).
- **Retirement PROPOSED, not decided:** mempalace's honourable
  retirement from Ember is proposed for **Volmarr's word** (no
  in-tree consumer; upstream lives at its own home; nothing removed,
  moved, or marked by this slice — member verified present and
  unmodified at banking, pinned by conformance). Fallback if he
  declines: bounded as an optional, non-default, never-bundled
  laptop-class archive adapter with true costs stated. Until he
  rules, the fallback's restraints apply and silence is never read
  as a retirement word. **REPORTING NOTE for the main agent:** the
  roadmap orders this proposal "presented for Volmarr's word" — the
  exact plain question is in the paper §6 (retire honourably, or
  keep bounded as the optional adapter?). E-080 does not wait on
  the answer; E-092's gate records the word or its absence.
- E-080 charged with five binding conditions: one canonical
  mimir-well path (docket 51 settled there; docket 109's four raw-SQL
  readers/writers reckoned with, Part VIII consulted); stores not
  merged (E-081: survivors stay native; mempalace-store answer waits
  on the ruling); persona separation as a face property (docket 110);
  budgets bind the face (toaster first); docket 108 hygiene at or
  before E-092. The paraphrase gap is charged to the face as an
  *index-don't-merge* proposal (index living facts into Brunnr for
  meaning search, resolve hits through mimir-well's current-truth
  view) — a proposal for E-080 to implement and prove, NOT claimed
  here; if its vector growth breaks the toaster, the toaster ships
  word-search over living facts and says so plainly.
- Conformance: `tests/unit/test_memory_verdict_e079.py` **5 passed**;
  combined Part V conformance (E-077 + E-078 + E-079) **17 passed**.
  Slice gate (logs in `~/workspace/.verify-tmp/ember-e079/gate/`):
  Run A **1 error, 11 skipped**, exit 2 (docket 1, identical);
  Run B **1321 passed, 7 failed, 25 skipped, 1 warning** (1316 + 5
  new; the 6 proven environment failures identical list, plus
  `test_load_truth_e075` under this run's deep workspace TMPDIR —
  E-076's proven socket-cap artifact class; isolated default-TMPDIR
  re-run this tick **8 passed**, and Run D below is green with that
  test inside it); Run D **1379 passed, 0 failed, 19 skipped,
  1 warning**, exit 0 (1373 + 5 new + the load-truth test passing
  in this shape). No README touched; no member code touched.
- E-079 push: banking commit 2469aaa pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 662d1f2,
  an ancestor; the push also carried this tick's IN PROGRESS marker
  c404d41) — remote moved 662d1f2 → 2469aaa, verified via ls-remote
  (remote head = 2469aaa2879e4262412a736d61db08c34780c89c = local HEAD
  at push time).

## E-080 — The chosen shape implemented: one memory contract (DONE, 2026-11-01)

- Contract live at `src/ember/well/memory_face.py` (`MemoryFace`,
  +25,444 B core), filed at
  `docs/architecture/E-080_ONE_MEMORY_CONTRACT.md`: one face over
  the E-079 bounded shape — living facts through mimir-well's
  own `RunaMemory` (loaded lazily via importlib; the core's one
  sanctioned library-path consumer, never raw SQL), documents
  and turns through Brunnr. Stores not merged (pinned: after an
  indexed fact, Brunnr holds exactly one document — the face's
  synthetic index document).
- **Docket 51 SETTLED for the companion:** the face's one
  canonical mimir path is the library default, named once as
  `CANONICAL_MIMIR_DB_PATH` (`~/.mimir_well/mimir_well.db`);
  other paths only as explicit face configuration.
  **Docket 109 reckoned (doc §6):** bifrost's two raw-SQL
  consumers, the Eye, and Verdandi's check are NOT re-pointed
  (Part VIII owns bifrost's side; E-085/E-092 inherit the stated
  map); the face is not a fifth raw-SQL consumer.
  **Docket 110 built at the face:** facts ride mimir's own
  `user_id` persona namespace; episode persona tags live in
  the face's sidecar above the adapter — untagged episodes
  belong to the default persona only, fail-closed (proven).
  Docket 108 rides to E-092 as the verdict assigned.
- **Index-don't-merge PROVEN** (deterministic synonym-folding
  stand-in embedder): a paraphrase question finds the ferry
  fact (mode "meaning"); after supersession the same question
  returns the new text and never the old — the stale index
  chunk resolves away through mimir's current truth.
  **Budgets bind the face, priced in the doc §5:** one indexed
  fact = one embedded chunk = 72,239 B (E-078) → toaster
  (~29/month against its 2 MiB growth ceiling) ships WORD
  search over living facts and says so (`mode == "word"`,
  profile named in the note); phone/pi/laptop index by
  default (~145 / ~363 / ~1,452 facts/month priced). E-082
  owns index pruning under growth pressure.
- Two in-scope repairs landed with the slice: (1) E-044's
  import↔extra diet stays exact — the member is loaded
  dynamically, not statically imported, so no false PyPI
  extra was declared for an in-tree member; (2) E-077's
  zero-core-consumer pin was superseded by this slice and
  now pins exactly the one sanctioned file under
  attribution (campaign precedent: E-078's re-pin of E-057).
  E-057 table re-measured for the core's growth (131 files /
  857,356 B; total 131,475,741 B; laptop miss unchanged
  254,866 B), both published copies updated.
- Honest limits (doc §7): chat is NOT rewired to the face
  yet (contract live and proven; E-085 first among the
  wiring inheritors); no device truth; E-083 owns the full
  persona fixture battery at this layer; mempalace
  untouched, retirement still awaiting Volmarr's word.
- Conformance: `tests/unit/test_memory_face_e080.py`
  **11 passed**; combined Part V conformance (E-077 + E-078
  + E-079 + E-080) **28 passed**. Slice gate (logs in
  `~/workspace/.verify-tmp/ember-e080/gate/`): Run A
  **1 error, 12 skipped**, exit 2 (docket 1, identical; the
  +1 skip is this slice's own file importorskipping
  sqlite_vec); Run B **1322 passed, 6 failed, 26 skipped,
  1 warning** — the 6 are the proven environment failures,
  identical list to E-079 (1321 + 1: the E-044 diet test
  the slice's repair turned green); Run D **1390 passed,
  0 failed, 6 skipped**, exit 0 (1379 + 11 new; the
  pgvector integration module skipped whole this run —
  its `pgvector` pip guard — where E-079's run collected
  it and skipped its 13 tests individually; zero failures
  either way). No README touched; no member code touched.
- E-080 push: banking commit c33143f pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 8743847,
  an ancestor; the push also carried this tick's IN PROGRESS marker
  95ae76e) — remote moved 8743847 → c33143f, verified via ls-remote
  (remote head = c33143f9d9e506982a4e8328df4148fcdaa9b54a = local HEAD
  at push time).

## E-081 — Migration answer: survivors native; palace migrates (DONE, 2026-11-01)

- Answer filed at `docs/architecture/E-081_MIGRATION_ANSWER.md`:
  E-079 §5.2/§8's narrowed question answered in both halves.
  **Survivors: NO migration — proven.** Stores written the
  pre-face way (RunaMemory direct incl. a supersession;
  Brunnr handle direct: document+chunk+episode) served
  whole through the E-080 face (toaster profile), with
  both stores' schemas byte-identical afterwards, every
  content table's row count identical, and Brunnr zero
  deltas of any kind. Only deltas: mimir-well's own read
  audit log (+2, its audit recording the test's recalls)
  and FTS5 shadow segment compaction on member reopen —
  FTS content unchanged, no fact row moved.
- **Palace: migrate, don't read-compat forever —
  argued from fixtures, NOT executed.** Synthetic palace
  built in the exact shape of mempalace's own stdlib
  reader (`mempalace/mempalace/migrate.py`
  extract_drawers_from_sqlite, sqlite3 only, ChromaDB
  never installed) and extracted with that function:
  drawers map losslessly to Brunnr document+chunk
  (text byte-identical; ALL metadata + drawer id in the
  document's persisted metadata mapping; original record
  reconstructs exactly — proven mapper-level AND through
  a real Brunnr store via the face); diary drawers map
  as documents, honestly not episodes; KG triples map to
  living-fact records field-for-field (validity,
  confidence, provenance). Closets + stored embeddings
  are DERIVED (closet pointer audit: every pointer
  resolves to an extracted drawer; payload is only
  topics/entities extracted from drawer text) — rebuilt
  at destination, never carried. Priced: 585 B/drawer
  word-only or 72,239 B embedded (E-078 price);
  745 B/triple as a mimir fact (10k drawers ≈ 5.9 MB
  word-only / ≈722 MB embedded → executing migration
  follows the face's per-profile index rule).
- Two findings for the executing slice: (1) the member
  extractor is COLLECTION-BLIND (returns closets among
  drawers — executing reader must classify by id);
  upstream migrate() shares the blindness and skips
  closets/KG entirely. (2) A palace can be READ with
  stdlib alone — read-compat forever refused (forever
  tax + the disqualified ~185 MB stack for search);
  the stdlib reader is what the one-time migration
  uses. Honest gap named: face's remember_fact carries
  no confidence/validity fields — executing migration
  writes triples through RunaMemory directly or the
  face grows them first (E-083 in view).
- Status discipline kept: retirement still awaiting
  Volmarr's word (E-079 §6 question stands, presented
  at E-079); migration executes only under that ruling;
  if declined, the mapping stands as a user-chosen
  one-way export under the bounded fallback. Member
  untouched; core gained NO mempalace reader (pinned).
- Conformance: `tests/unit/test_memory_migration_e081.py`
  **9 passed**; combined Part V conformance (E-077 +
  E-078 + E-079 + E-080 + E-081) **37 passed**. Slice
  gate (logs in `~/workspace/.verify-tmp/ember-e081/gate/`):
  Run A **1 error, 13 skipped**, exit 2 (docket 1,
  identical; +1 skip = this slice's file importorskipping
  sqlite_vec); Run B **1322 passed, 6 failed, 27 skipped,
  1 warning** — the 6 are the proven environment failures,
  identical list to E-080 (this slice's file skips whole
  in the default env); Run D **1399 passed, 0 failed,
  19 skipped**, exit 0 (1390 + 9 new; the skip variance
  is E-080's noted pgvector whole-module guard shape, 13
  tests skipping as one module — zero failures either way).
  No README touched; no member code touched.
- E-081 push: banking commit fb24043 pushed under Volmarr's 2026-10-31
  standing go-ahead after fetch + ancestry check (remote was 2f66c54,
  an ancestor; the push also carried this tick's IN PROGRESS marker
  a42b722) — remote moved 2f66c54 → fb24043, verified via ls-remote
  (remote head = fb240430df319dabc1e1acd479805f84c1bf23cc = local HEAD
  at push time).

## E-082 — Memory lifecycle: growth, decay, pruning (DONE, 2026-11-01)

- Lifecycle live on the face (`src/ember/well/memory_face.py`,
  +7,182 B core), filed at
  `docs/architecture/E-082_MEMORY_LIFECYCLE.md`:
  `lifecycle_report()` (growth accounting priced from
  measured anchors only — fact 745 B E-078, turn 585 B
  E-050/E-078, indexed fact 72,239 B E-078 — judged
  against the profile's Part III ceiling; the toaster's
  2 MiB ceiling = ~29 indexed facts, re-proving E-080's
  pricing), `run_decay()` (mimir-well's own Ebbinghaus
  decay delegated per persona, nothing reimplemented),
  `prune_stale_index()` (sidecar pointers for facts no
  longer current are dropped; meaning search keeps
  serving the current fact), `run_lifecycle()` (decay →
  prune → report, in that order).
- **E-050 consumed, verdict unchanged:** a reference
  month is 0.39 MiB, inside every ceiling with years of
  headroom — lifecycle is accounting + hygiene, not
  emergency pruning; episodes are NOT pruned (history
  deletion is the user's right, E-084, not a budget
  reflex); the fact index is the only growth that can
  break a small profile and stays bounded by E-080's
  per-profile rule.
- **Two honest limits, new docket 112 + 113:** (112)
  Brunnr's handle has no delete — pruned stale chunks
  become unreachable and uncounted but their physical
  bytes are NOT reclaimed (every prune report states
  `physical_bytes_reclaimed: 0`); byte reclamation
  waits on a handle-level delete, E-092 gate to assign.
  (113) mimir-well decay()'s `pruned` count names
  importance-flooring at 1, not row deletion (read in
  `_decay_inner` this slice) — no face report claims
  deletions that did not happen.
- In-scope repair (campaign precedent E-078/E-080):
  the core's growth re-measured the E-057 table —
  core 131 files / 864,538 B, twelve-member total
  131,482,923 B, laptop miss unchanged 254,866 B —
  both published copies updated (E-057 doc + BUDGET
  BOOK §7) with the re-measure note extended.
- Conformance: `tests/unit/test_memory_lifecycle_e082.py`
  **9 passed**; combined Part V conformance (E-080 +
  E-081 + E-082 files) **29 passed**. Slice gate (logs
  in `~/workspace/.verify-tmp/ember-e082/gate/`): Run A
  **1 error, 14 skipped**, exit 2 (docket 1, identical;
  +1 skip = this slice's file importorskipping
  sqlite_vec); Run B **1321 passed, 7 failed, 28
  skipped, 1 warning** — the 6 proven environment
  failures identical list, plus `test_load_truth_e075`
  under this run's deep workspace TMPDIR (E-076's
  proven socket-cap artifact; isolated default-TMPDIR
  re-run this tick **8 passed**; E-082 touches no hub
  code); Run D **1407 passed, 1 failed, 19 skipped** —
  the sole failure is the same load-truth artifact
  (1399 + 9 new − 1 artifact vs E-081's Run D). No
  README touched; no member code touched.

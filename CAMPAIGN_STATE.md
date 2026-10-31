# Project Ember — Campaign State

Roadmap: `docs/EMBER_ROADMAP_2026-10-30.md` (204 slices, E-001–E-204, 12 parts)
Repo: hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster
Base branch: development @ f26312a54af94439cf480c58a0eb4d78b54e6024
Campaign branch: yrsa/ember-road-build
Working tree: ~/workspace/ember-build/ (this campaign's own clone — never shared)

Last updated: 2026-10-31 01:39 EDT
Status: STOPPED between slices (no slice IN PROGRESS)
Banked: E-001, E-002, E-003, E-004, E-005, E-006, E-007, E-008, E-009, E-010, E-011, E-012, E-013, E-014
Next slice: E-015 — Budget archaeology

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
- E-015 next — Budget archaeology.

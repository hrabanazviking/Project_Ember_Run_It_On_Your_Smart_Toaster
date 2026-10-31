# Project Ember — Campaign State

Roadmap: `docs/EMBER_ROADMAP_2026-10-30.md` (204 slices, E-001–E-204, 12 parts)
Repo: hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster
Base branch: development @ f26312a54af94439cf480c58a0eb4d78b54e6024
Campaign branch: yrsa/ember-road-build
Working tree: ~/workspace/ember-build/ (this campaign's own clone — never shared)

Last updated: 2026-10-31 06:47 EDT
Status: STOPPED between slices (no slice IN PROGRESS) — Part II open, E-035 banked
Banked: E-001, E-002, E-003, E-004, E-005, E-006, E-007, E-008, E-009, E-010, E-011, E-012, E-013, E-014, E-015, E-016, E-017, E-018, E-019, E-020, E-021, E-022, E-023, E-024, E-025, E-026, E-027, E-028, E-029, E-030, E-031, E-032, E-033, E-034, E-035
Next slice: E-036 — Determinism mode for tests/benchmarks (seeded)

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
  No README touched.

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
- E-036 next — Determinism mode for tests/benchmarks (seeded).

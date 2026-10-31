# Project Ember — Campaign State

Roadmap: `docs/EMBER_ROADMAP_2026-10-30.md` (204 slices, E-001–E-204, 12 parts)
Repo: hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster
Base branch: development @ f26312a54af94439cf480c58a0eb4d78b54e6024
Campaign branch: yrsa/ember-road-build
Working tree: ~/workspace/ember-build/ (this campaign's own clone — never shared)

Last updated: 2026-10-30 22:17 EDT
Status: STOPPED between slices (no slice IN PROGRESS)
Banked: E-001, E-002
Next slice: E-003 — ORIGINS concordance

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

## Slice ledger

- E-001 DONE (2026-10-30) — opening: clone, branch, roadmap filed + filing push verified, state file, opening baseline.
- E-002 DONE (2026-10-30) — member census in depth, filed at docs/audit/E-002_MEMBER_CENSUS.md.
- E-003 next — ORIGINS concordance.

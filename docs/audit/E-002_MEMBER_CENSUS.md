# E-002 — Member Census

*Project Ember campaign, Part I (The Monorepo's True State).
Measured 2026-10-30 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), at campaign
commit 24809d8 (E-001 banked). This census is evidence, not
verdict: keep / merge / remove decisions are prepared in Part I
from ORIGINS (E-003, E-018) and executed only on Volmarr's word.*

## Method (so any keeper can re-measure identically)

- Walked the working tree per top-level directory, excluding
  `.git`, `__pycache__`, and `node_modules`. Sizes are **byte
  sums of file contents**, not disk-block (`du`) figures; the
  E-001 snapshot used `du`, which is why its sizes read slightly
  higher. File counts below exclude the same three directories.
- A **test file** is a file whose name matches `test_*.py`,
  `*_test.py`, `*.test.*`, or `*.spec.*`, or a Cypress integration
  spec under a `tests/integration/` path. `conftest.py`,
  `__init__.py`, and README files inside test directories do not
  count. Under this definition the counts reproduce the E-001
  snapshot exactly for every member it listed (root tests 61,
  mempalace 76, Hamr 46, CloakBrowser 30, mimir-well 28,
  Verdandi 10, bifrost 2, kista 1, seidr_engine 1).
- **Last evidence of life** is `git log -1` for that path on this
  branch (152 commits at census time), with the number of commits
  touching the path. An import commit is evidence the member was
  placed here, not that it was developed here.
- Purpose statements are drawn from the roadmap §2, ORIGINS.md,
  and each member's own package metadata / module layout, read
  in-tree at census time. No README was modified (campaign law).

## The census table

| Member | Purpose | Size (bytes) | Files | Main code language | Test files | Last evidence of life (git) |
|---|---|---:|---:|---|---:|---|
| `src/` (ember core) | The companion itself: `ember-agent` 0.2.0 package under `src/ember/` (cli, config, mcp, schemas, spark, thread, tools, well) | 528,317 | 104 | Python (70 .py) | 0 (tests live in root `tests/`) | 68d51f6, 2026-05-21 20:08 EDT, "harden: Batch K"; 28 commits touch `src/` |
| `tests/` (root) | The core's suite: unit / integration / e2e + fixtures + snapshots | 424,838 | 68 | Python (62 .py) | 61 | 68d51f6, 2026-05-21 20:08 EDT (Batch K); 27 commits |
| `Verdandi/` | The event/nerve hub: `context_injector.py`, `conversation_logger.py`, `nervous_system.py`, `reactor.py`, `heartbeat/` subpackage; verdandi 0.3.0 | 16,817,105 | 179 | Python (48 .py) | 10 | 7da4077, 2026-05-21 18:51 EDT, "Verdandi" — single import commit |
| `kista/` | The Smart Toaster Kista: credential store, kista 2.0.0, implementation is `scripts/credstore.py` | 2,770,218 | 25 | Python (3 .py) | 1 | 4f81633, 2026-05-21 19:15 EDT, "kista" — single import commit |
| `mempalace/` | Memory system I: mempalace 3.3.5, CLI + MCP server, benchmarks, website | 59,049,715 | 257 | Python (141 .py) | 76 | f7ef473, 2026-05-21 18:39 EDT, "mempalace" — single import commit |
| `mimir-well/` | Memory system II: mimir-well 2.10.4, "AI Memory Database with Ebbinghaus Decay and Self-Healing", plus an `eye` app | 607,675 | 58 | Python (47 .py) | 28 | 911eeba, 2026-05-21 18:55 EDT, "mimir-well" — single import commit |
| `seidr_engine/` | The seiðr engine: seidr-engine 0.1.0, package `seidr/` | 103,728 | 11 | Python (8 .py) | 1 | 02ded16, 2026-05-21 19:22 EDT — single import commit |
| `astrology-engine/` | The astrology engine: one file, `astrology_engine.py` (134,560 bytes), a CLI computing natal / transit / synastry / lunar / lots / Hellenistic outputs | 7,477,309 | 25 | Python (1 .py) | 0 | bf38370, 2026-05-21 18:30 EDT — single import commit |
| `bifrost/` | The bridge/transport member: bifrost 1.0.0, `src/bifrost/` (`core.py`, `config.py`, `bridges/memory_bridge.py`) | 77,916 | 10 | Python (7 .py) | 2 | c765c19, 2026-05-21 19:18 EDT — single import commit |
| `Hamr/` | The VRM avatar builder with Blender bridge: hamr 0.8.0, `src/hamr/` | 6,081,769 | 168 | Python (110 .py) | 46 | 2063fdb, 2026-05-21 19:04 EDT, "Hamr" — single import commit |
| `Open-VTT/` | The virtual tabletop: a Godot project (`Open-VTT/Godot/project.godot`, UI / components / scenes / scripts / tilesets) | 6,768,730 | 209 | GDScript (55 .gd) + 32 Godot scenes | 0 | a01008d, 2026-05-21 18:25 EDT — single import commit |
| `CloakBrowser/` | **Vendored** third-party stealth browser (own LICENSE + BINARY-LICENSE): Python package + TypeScript `js/` tree | 6,420,853 | 112 | Python (50 .py) + TypeScript (35 .ts) | 30 | 58bd533, 2026-05-21 18:22 EDT — single import commit |
| `cleasby-vigfusson-old-norse-dict/` | The Old Norse dictionary: a Next.js app (`cleasby-vigfusson-next`), Jest + Cypress tests | 24,221,782 | 170 | TypeScript/JavaScript (Next.js) | 47 | 9820167, 2026-05-21 19:00 EDT — single import commit |
| `docs/` | All written material: architecture, plans (AIRI / ClawLite / Cortex / WaifuOS … Mythic Plans), codices' working papers, archive | 45,725,931 | 1,750 | Markdown (1,723 .md) | 0 | ed8a69c, 2026-10-30 (E-001 roadmap filing); 86 commits |
| `assets/` | Binary/media referenced from documentation (Runa illustrations, camera images, licence photo) | 3,406,778 | 12 | — (11 images + 1 README) | 0 | bf259c7, 2026-05-19 03:44 EDT |
| `config/` | Configuration templates/examples only (`ember.example.yaml`, profiles, sources/storage examples) | 15,103 | 5 | YAML | 0 | b2483ee, 2026-05-21 13:13 EDT (doc-pass); 6 commits |
| `deploy/` | Deployment shapes — **documents only**: `docker/`, `examples/`, `pi/`, `systemd/` hold 6 Markdown files and no manifests or scripts | 19,621 | 6 | Markdown | 0 | b2483ee, 2026-05-21 13:13 EDT (doc-pass); 4 commits |
| `examples/` | Reference configs / sessions / skills / plugins — currently 5 Markdown files only | 3,852 | 5 | Markdown | 0 | b2483ee, 2026-05-21 13:13 EDT (doc-pass); 2 commits |
| `scripts/` | Human-invoked helpers (`dev/`, `maintenance/`, `one_shot/`) — currently 4 Markdown files only, no scripts | 3,876 | 4 | Markdown | 0 | b2483ee, 2026-05-21 13:13 EDT (doc-pass); 2 commits |
| `tools/` | Repo tooling / diagnostics / importers — currently 4 Markdown files only, no tools | 5,193 | 4 | Markdown | 0 | b2483ee, 2026-05-21 13:13 EDT (doc-pass); 2 commits |
| `vendor/` | Third-party code home per ORIGINS §3 — currently holds only its README (993 bytes); the one vendored member, CloakBrowser, sits at top level instead | 993 | 1 | Markdown | 0 | bf259c7, 2026-05-19 03:44 EDT |

Root loose files (not a directory member, counted for
completeness): 45 files, ~36 MB total, including `ORIGINS.md`
(22,070 bytes), the five elder codices (`TASK_CHATDOLL_CODEX.md`,
`TASK_HERMES_CODEX.md`, `TASK_RAGNAROK_CODEX.md`,
`TASK_SUPER_AGENT_PARTY_CODEX.md`, `TASK_WAIFU_CODEX.md`),
`pyproject.toml` (ember-agent 0.2.0, stdlib-only core), and a
loose image population: 19 `IMG_*.jpeg` camera files plus three
large PNGs (`9834u4ernk4.png`, `ekkam8ekkam8ekka.png`,
`s7dkpys7dkpys7dk.png`).

## Entry points (what would start, if started — boot is E-006)

| Member | Entry point(s) found in-tree |
|---|---|
| ember core | Console script `ember = ember.cli.main:main` (root pyproject); `src/ember/__main__.py`; `src/ember/cli/main.py` |
| Verdandi | Console scripts `verdandi` and `verdandi-nerve` → `nervous_system:main`; `verdandi-heartbeat` → `heartbeat.cli:main`; `heartbeat/__main__.py` |
| kista | Console script `kista = scripts.credstore:main` |
| mempalace | Console scripts `mempalace = mempalace.cli:main`, `mempalace-mcp = mempalace.mcp_server:main`; `mempalace/__main__.py`; a `website/package.json` |
| mimir-well | Package `src/mimir_well/` with `eye/__main__.py` + `eye/app.py`; `start-eye.sh` at member root; no console script declared in its pyproject |
| seidr_engine | Console script `seidr = seidr.cli:main`; `seidr/__main__.py` |
| astrology-engine | Direct file execution: `python3 astrology_engine.py <natal\|transit\|synastry\|…>` (per its own header); no pyproject |
| bifrost | Library only: no console script, no `__main__.py` found |
| Hamr | Console script `hamr = hamr.cli:main` (`src/hamr/cli.py`) |
| Open-VTT | `Open-VTT/Godot/project.godot` (Godot engine is the runtime; external native tool) |
| CloakBrowser | Console script `cloakbrowser = cloakbrowser.__main__:main`; `cloakbrowser/__main__.py`; `js/package.json`; `bin/cloakserve`, `bin/cloaktest` |
| dictionary | npm scripts in `package.json`: `dev` / `build` / `start` (Next.js), `test:unit` (Jest), `test:integration` (Cypress) |

## Findings (evidence for later Part I slices — no verdicts here)

1. **Every member named in roadmap §2 is PRESENT.** Nothing the
   roadmap promises to audit is missing from the tree.
2. **Most members have exactly one commit: their import.**
   Verdandi, kista, mempalace, mimir-well, seidr_engine,
   astrology-engine, bifrost, Hamr, Open-VTT, CloakBrowser, and
   the dictionary each arrived in a single commit on
   2026-05-21 (18:22–19:22 EDT) and have no later in-repo
   history. Only `src/` + `tests/` (28 / 27 commits, developed
   through Batch K on 2026-05-21 20:08 EDT) and the bootstrap
   scaffolding (`docs/`, `config/`, `deploy/`, `examples/`,
   `scripts/`, `tools/`) show multi-commit lives. "Last evidence
   of life" for the imported members is therefore *import*, and
   any claim about their development history must come from
   ORIGINS (E-003), not from this repo's log.
3. **Weight is concentrated in data and images, not code.**
   - mempalace is the heaviest member (59.0 MB), but ~38.5 MB of
     it is three April-2026 benchmark-result `.jsonl` files under
     `benchmarks/`, plus a 4.0 MB benchmark `.json` and an 8.4 MB
     website hero video. Its Python is ~2.3 MB.
   - The dictionary's 24.2 MB is dominated by one Jest snapshot
     file (18.6 MB, `tests/unit/pages/__snapshots__/index.test.js.snap`)
     and `public/sitemap.xml` (4.9 MB).
   - Verdandi's 16.8 MB is ~15.2 MB of loose images at the member
     root (16 `.jpg` + 18 `.jpeg`); its Python is 0.77 MB.
   - astrology-engine's 7.5 MB is ~7.2 MB of images around a
     single 134,560-byte Python file.
   - Hamr carries ~3.6 MB of loose root images; the root itself
     carries ~36 MB of loose files (finding 6).
   These are budget facts for Part III (E-015, E-043), recorded
   here without any removal proposal — removals are Volmarr's
   word, prepared at E-018.
4. **Test presence is sharply uneven.** mempalace (76), the
   dictionary (47), Hamr (46), CloakBrowser (30) and mimir-well
   (28) carry real suites; astrology-engine and Open-VTT carry
   **zero** test files; kista and seidr_engine carry exactly one
   each; bifrost two. E-005 runs each of these in its own shape.
5. **The scaffolding directories are near-empty shells.**
   `scripts/`, `tools/`, `examples/` hold only Markdown (4–5
   files each) despite ORIGINS §3 describing them as homes for
   helpers, tooling, and reference material; `deploy/` holds
   documents only, no deployable artefacts; `vendor/` holds only
   a README while the vendored member lives at top level. These
   are concordance items for E-003 / E-014, not defects fixed
   here.
6. **Root images have recurred.** ORIGINS §2 records root images
   as moved to `assets/` in the bootstrap (P5), and its §5b log
   records a merge once bringing root copies back. At census
   time the root again holds 19 `IMG_*.jpeg` files and three
   large PNGs alongside `assets/`'s own 11 images. Whether the
   root copies duplicate `assets/` copies is an E-014 question
   (byte comparison), recorded here as an observation only.
7. **Licences:** every code member checked carries its own
   `LICENSE` file (Verdandi, kista, mempalace, mimir-well,
   seidr_engine, astrology-engine, bifrost, Hamr, Open-VTT,
   CloakBrowser, dictionary). The support directories (assets,
   config, deploy, docs, examples, scripts, tests, tools,
   vendor, src) carry none of their own and stand under the root
   MIT LICENSE. Verification of licence *contents* is E-007.

*Filed by the E-002 slice, 2026-10-30. Next: E-003 — ORIGINS
concordance.*

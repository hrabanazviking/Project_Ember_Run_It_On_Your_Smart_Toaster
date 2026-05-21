# EMBER_FORK_DELTA — What Ember Keeps, Renames, and Sets Aside from Runa

**Voice:** Cartographer (Védis Eikleið), with Architect (Rúnhild Svartdóttir)
**Status:** Proposed — for ratification. Working document for the Architect's first pass called out in `docs/DEVLOG.md` (2026-05-19 entry, "What's next" item 1).
**Last touched:** 2026-05-21
**Reads with:** `ARCHITECTURE.md`, `DOMAIN_MAP.md`, `ORIGINS.md`, `docs/REPO_MAP.md`, `docs/archive/runa-inherited/`.

---

## 0. Why this document exists

Ember was forked from Runa-Agent-Digital-Being on 2026-05-19. The fork brought a substantial body of material — code skeleton, methodology, research corpora, philosophy, PhD curriculum, architectural drafts. Much of it is universally useful. Some of it is overweight for Ember's Vow of Smallness. None of it should be silently deleted.

This document is the **Cartographer's recommendation** to the Architect (and ultimately to Volmarr) for how each inherited piece should be treated. It is **additive**: nothing is removed here. It only proposes status changes for items already in the repo, each requiring Volmarr's ratification before action.

The discipline is the same as `ORIGINS.md`'s discipline for imports: every row is named, sourced, judged, and given an explicit status.

---

## 1. Top-level files

| File | Inherited? | Ember relevance | Recommendation | Rationale |
|---|---|---|---|---|
| `README.md` | Re-written for Ember (toaster framing) | Fresh and correct as-is | **Keep at root** | Cute, accessible, public-friendly per Vow of Public-Friendliness. |
| `PHILOSOPHY.md` | Volmarr-ecosystem compact ethos | Universally applicable | **Keep at root** | Same philosophy serves Ember; no Ember-specific edit needed for first pass. |
| `MYTHIC_ENGINEERING.md` | Re-written for Ember | Fresh and correct as-is | **Keep at root** | Already Ember-shaped. |
| `RULES.AI.md` | Volmarr standing coding laws | Universally applicable | **Keep at root** | Standing-rule file; canonical placement is root. |
| `ORIGINS.md` | Detailed Runa-attribution register | Inherited Runa attribution + needs Ember-descent rows | **Keep at root, add Ember-descent rows** | Future commit per DEVLOG "light root edits". |
| `LICENSE` / `NOTICE` / `LEGAL-NOTICE.md` / `THIRD_PARTY_NOTICES.md` | Repository-defining | Universally applicable | **Keep at root** | Never modify. |
| `Yggdrasil_and_Huginn_and_Muninn_Theory.md` | Volmarr long-form theory | Universally applicable, but heavy | **Keep at root** (per DEVLOG notes) | Could move to `docs/philosophy/` in a later sweep if the Skald and Volmarr agree, but no need to move now. |
| `pyproject.toml` | Names package `runa-agent`; entry point `runa` | **Stale** — Ember's package must be `ember-agent` and entry point `ember` | **Rewrite for Ember** in the same commit-or-PR that lands the `src/runa/` → `src/ember/` rename | Per the Architect's first pass; Hjarta cannot work as `runa shell`. |
| `.python-version`, `.env.example`, `.gitignore` | Standard | Universally applicable | **Keep** | Inspect once for `runa`-specific paths; adjust if found. |

## 2. The `src/` skeleton

The inherited `src/runa/` skeleton is **Runa-shaped**, not Ember-shaped. It encodes the larger architecture: `core/`, `runtime/`, `services/`, `apps/`, `adapters/`, `plugins/`, `skills/`. Ember's shape is `spark/`, `thread/`, `well/`, `cli/` (see `DOMAIN_MAP.md`).

| Item | Recommendation | Notes |
|---|---|---|
| `src/runa/__init__.py`, `src/runa/__main__.py` | **Replace at the rename** | Tiny files; trivial to re-author for Ember. |
| `src/runa/{core,runtime,services,apps,adapters,plugins,skills,schemas,migrations,cli}/` | **Archive the skeleton, re-cut to Ember's shape** | Each is empty except for `__init__.py`, `README.md`, `INTERFACE.md`. Worth reading the INTERFACE.md drafts during the Architect's first pass to harvest patterns; otherwise re-cut clean to `src/ember/{spark,thread,well,cli,schemas}/`. |
| `src/README.md` | **Keep, lightly update** | "Why PEP-517 src-layout" applies unchanged. |

**Proposed migration sequence:**

1. Create `src/ember/` with the new realm-based layout (empty `__init__.py` + draft `README.md` + draft `INTERFACE.md` per the EMBER_DOMAIN_MAP).
2. Archive `src/runa/` into `docs/archive/runa-inherited/src-skeleton/src/runa/` (preserved, not deleted, per the additive rule).
3. Update `pyproject.toml`: package name, entry point, source dirs.
4. Re-author `__init__.py` and `__main__.py` under `src/ember/`.
5. Commit. The first slice's code (per `EMBER_FIRST_SLICE_PLAN.md`) begins in the next commit.

No code beyond `__init__.py` + `__main__.py` has been written under `src/runa/`, so there is nothing to port. The rename is structural only.

## 3. Documentation under `docs/`

### 3.1 Canonical architecture docs

| File | Status now | Recommendation |
|---|---|---|
| `docs/architecture/ARCHITECTURE.md` (Runa's shape, pre-2026-05-21) | — | **Done 2026-05-21:** moved to `docs/archive/runa-inherited/architecture/ARCHITECTURE.md`. Canonical path now holds Ember's shape. |
| `docs/architecture/DOMAIN_MAP.md` (Runa's shape, pre-2026-05-21) | — | **Done 2026-05-21:** moved to archive similarly. |
| `docs/architecture/DATA_FLOW.md` (Runa's shape, pre-2026-05-21) | — | **Done 2026-05-21:** moved to archive similarly. |
| `docs/architecture/EMBER_ARCHITECTURE.md` | Renamed | **Done 2026-05-21:** promoted to canonical `docs/architecture/ARCHITECTURE.md`. |
| `docs/architecture/EMBER_DOMAIN_MAP.md` | Renamed | **Done 2026-05-21:** promoted to canonical `docs/architecture/DOMAIN_MAP.md`. |
| `docs/architecture/EMBER_DATA_FLOW.md` | Renamed | **Done 2026-05-21:** promoted to canonical `docs/architecture/DATA_FLOW.md`. |
| `docs/architecture/EMBER_FORK_DELTA.md` | New (this commit, this file) | **Keep** — long-term lineage reference. |
| `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` | New (this commit) | **Keep until the first slice ships**, then archive. |
| `docs/architecture/ROBUST_AGENT_ENGINEERING_PLAN.md` | Runa source material | **Keep** as design heritage; the Bifröst/VERÐANDI/Skuld/Muninn material is the seed of the parent project's shape. |
| `docs/architecture/Runa-Agent-Digital-Being.md`, `…/Runa_Agent_Digital_Being.md` | Two parallel large vision drafts | **Keep** per Volmarr's 2026-05-17 resolution (intentionally parallel, not duplicates). |
| `docs/architecture/Technical_Architecture_of_Volmarrs_AI_Ecosystem.md` | Cross-project shared doc | **Keep** — this is canonical shared text across NSE, MindSpark, VGSK, WYRD. |

### 3.2 The inherited corpora

| Folder | Bytes (approx) | Ember relevance | Recommendation |
|---|---|---|---|
| `docs/research/` (100 numbered docs: MemGPT, RAG, embeddings, KGs, ReAct, Reflexion, etc.) | Large | **High** — every doc bears on Ember's retrieval/grounding story. | **Keep in full.** Cartographer's note: the 10 most load-bearing for Ember's first slice are `01` (MemGPT), `03` (embedding models), `04` (RAG evolution), `06` (knowledge graphs), `08` (sqlite-vss), `15` (prompt engineering), `16` (quantization local inference). |
| `docs/python/` (50 numbered docs: result types, concurrency, plugin patterns, etc.) | Large | **High** — the Forge Worker reads this corpus when implementing. | **Keep in full.** Cartographer's note: `02` (Result types), `05` (idempotency), `10` (graceful degradation), `22` (concurrent futures), `44` (plugin architecture), `45` (configuration management), `49` (graceful shutdown) bear directly on Ember subsystems. |
| `docs/phd-2040/` (PhD curriculum: year 1-2 lectures, papers, syllabi) | Very large | **Low-to-medium** — speculative future-AI curriculum; doesn't constrain Ember's code. | **Keep in full.** No need to read for Ember work; preserves Volmarr's curriculum as intellectual heritage. Cartographer recommends a single-line note in `docs/phd-2040/README.md` clarifying "not load-bearing for Ember implementation". |
| `docs/AI_OS_Research/` | Large | **Medium-high** — directly informs the AI-OS context Ember sits inside. | **Keep.** Read the executive thesis when proposing Funi adapters; the Apple/MS/Google sections inform `apple_foundation/` and `phi_silica/` adapter design. |
| `docs/RunaUniversity2040/` | Large | **Low** — Volmarr's curriculum. | **Keep.** No need to read for Ember work. |
| `docs/methodology/` (Mythic Engineering canon: Codex, Protocols, Plundering Workflow) | Large | **High** — the method by which Ember is built. | **Keep in full.** Living source. |
| `docs/philosophy/` (Heathen Third Path, Volmarr writings, Saga of Runa) | Large | **High** for ethos; **low** for code | **Keep in full.** Skald material. |
| `docs/decisions/` (ADRs 0001-0005 + HERMES_OPENCLAW) | Small-medium | **High** — informs every later decision. | **Keep in full.** Append Ember ADRs starting at 0006 (this commit adds 0006). |
| `docs/design/` (RUNA_ADVANCED_AGI_ENGINEERING_GUIDE, RUNA_ECOSYSTEM_IDEA_HARVEST, RUNAFREYJASDOTTIR_GITHUB_CODE_HARVEST, WORLD_MODELING_SKILL) | Large | **Medium** — Runa-shape design heritage; useful for the Skald and Architect when reasoning about parent context. | **Keep in full.** |
| `docs/archive/runa-inherited/` | Medium | The lineage room | **Keep, and grow** — every "move to archive" recommendation above adds to this tree. |

### 3.3 Operational docs

| Folder | Recommendation |
|---|---|
| `docs/operations/` | Keep. `RUNA_PROJECT_FILE_ORGANIZATION_AND_STARTUP_GUIDE.md` is the layout authority Volmarr ratified for the parent project; Ember's smaller shape adopts a *subset*. Worth a follow-up Ember-specific operations doc once the first slice ships. |
| `docs/development/` | Keep. |
| `docs/security/` | Keep. Threat model needs an Ember-specific pass once the first slice ships (smaller surface = simpler threat model). |
| `docs/adapters/` | **Active** — this commit adds `BRUNNR_BACKEND_MATRIX.md`, `FUNI_LOCAL_MODEL_OPTIONS.md`, `GUNGNIR_WELL_REFERENCE.md`, `SMIDJA_INGEST_PATTERNS.md`. Per-adapter contract docs ship with each adapter's first slice. |
| `docs/plugins/` | Keep. Ember's plugin story is much smaller than Runa's; recommend deferring plugin work until after the first slice ships. |

## 4. The `config/` directory

| Path | Current | Recommendation |
|---|---|---|
| `config/runa.example.yaml` | Inherited stub | **Rename to `config/ember.example.yaml`** in the rename commit. |
| `config/profiles/` | Inherited | Keep; populate with Ember-shaped profiles (`pi5.yaml`, `desktop_linux.yaml`, `macos.yaml`, `windows_copilot_plus.yaml`) as adapters land. |
| *(planned)* `config/storage.example.yaml` | Per `docs/REPO_MAP.md` | **Add in the first slice** — Brunnr backend selection. |
| *(planned)* `config/sources.example.yaml` | Per `docs/REPO_MAP.md` | **Add in the first slice** — Smiðja content sources. |

## 5. The `tests/`, `scripts/`, `deploy/`, `tools/`, `examples/`, `vendor/`, `assets/` directories

Inherited skeletons, all carrying their own `README.md`. The Cartographer's recommendation is to **keep all as-is**, ratify only when a slice touches them, and trim ruthlessly during the Architect's first pass *if* anything is found to encode Runa-specific assumptions.

| Folder | Special note |
|---|---|
| `deploy/{pi,systemd,docker,examples}/` | Pi is Ember's first-class target — `deploy/pi/` will be load-bearing soon. |
| `deploy/launchd/`, `deploy/nssm/` | *(planned, not present)* — add when the first macOS and Windows operators show up. |
| `assets/` | Image library. Volume is fine. |

## 6. The repository name itself

The repository is named `Project_Ember_Run_It_On_Your_Smart_Toaster` — descriptive, fun, public-friendly. **No recommendation to rename**; Volmarr already made this decision (DEVLOG 2026-05-19).

The parent project remains `hrabanazviking/Runa-Agent-Digital-Being`. The lineage is preserved through `ORIGINS.md`, `docs/archive/runa-inherited/`, and this file.

---

## 7. Execution order, when ratified

If Volmarr ratifies this disposition, the suggested execution order is:

1. **Add EMBER_*.md docs** (this commit). *Already done by this work.*
2. **Add the four adapter reference docs** (this commit). *Done.*
3. **Add ADR 0006** capturing this fork-delta survey. *Done.*
4. **DEVLOG entry** for this session. *Done.*
5. **Volmarr reads, ratifies, or revises.**
6. **Next commit:** rename `src/runa/` → `src/ember/`, update `pyproject.toml`, archive the canonical Runa architecture docs.
7. **Next-next commit:** first slice begins (`ember.schemas`, `ember.well.brunnr.sqlite_vec`, …).

Per `MYTHIC_ENGINEERING.md` §"Plundering and attribution": *Take the steel. Keep the maker's mark. Forge it into your own weapon.* Runa's steel is preserved. Ember's weapon is being shaped.

— Védis Eikleið

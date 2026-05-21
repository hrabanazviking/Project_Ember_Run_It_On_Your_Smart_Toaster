# ORIGINS — Attribution of Imported Material

**Last updated:** 2026-05-21 (post-slice-2 ratification — added §7 Ember-descent rows)
**Branch:** development
**Scribe:** Eirwyn Rúnblóm
**Scope:** Every root-level file and every top-level directory present in this repository, with a best-effort judgement of which prior project — or none — it came from, the evidence supporting that judgement, and honest marking of uncertainty.
**Purpose:** Give the integration phase a clean starting point. Decisions about keep / merge / remove / re-home are made on known ground rather than guesswork. The fork-to-Ember (2026-05-19) and the slice-1 + slice-2 build (2026-05-21) both added new material; §7 below records what's *Ember-fresh* on top of the Runa-inherited base.

---

## How to read this register

| Column | Meaning |
|---|---|
| **Item** | The file or folder being attributed. |
| **Origin** | The prior project or domain the material is judged to come from. Sources used: *fresh* (written specifically for this repository), the canonical [Mythic Engineering repo](https://github.com/hrabanazviking/Mythic-Engineering), Volmarr's cross-project writings, Volmarr's cross-project AI ecosystem docs, or another named Volmarr project (NSE, MindSpark, WYRD, VGSK, HERETIC, Seidr-Smidja, MV CLI, Rune Forge AI). |
| **Evidence** | What the judgement is based on: import commit hash and message, content reference, known shared docs across repos. |
| **Confidence** | High / Medium / Low. Honest about uncertainty. |
| **Status** | What was done with it in the 2026-05-17 bootstrap: *keep-at-root*, *moved-to-X*, *replaced-by-Y*, *removed*, *renamed-to-Z*. |
| **Notes** | Anything else worth recording. |

If a row's Confidence is **Low**, the entry should be reviewed by Volmarr or by a future contributor with better knowledge of the source ecosystem and updated.

---

## 1. Root-level files (originally imported before bootstrap)

### 1.1 Legal and licensing

| Item | Origin | Evidence | Confidence | Status | Notes |
|---|---|---|---|---|---|
| `LICENSE` | fresh | Initial commit `f4e9893` (2026-05-17). Standard MIT text, 2026 Volmarr Wyrd. | High | keep-at-root | Repository-defining; never modify. |
| `NOTICE` | fresh | Commit `d71eeda` (2026-05-17). Project copyright + pointer to LICENSE + THIRD_PARTY_NOTICES. | High | keep-at-root | |
| `LEGAL-NOTICE.md` | fresh | Commit `d71eeda` (2026-05-17). Author's distribution and personal-information policy. Specific to this project's release stance. | High | keep-at-root | |
| `THIRD_PARTY_NOTICES.md` | fresh | Commit `d71eeda` (2026-05-17). Skeleton; will fill in as third-party material is vendored. | High | keep-at-root | |

### 1.2 Mythic Engineering canon

| Item | Origin | Evidence | Confidence | Status | Notes |
|---|---|---|---|---|---|
| `MYTHIC_ENGINEERING.md` | canonical ME repo (stub pointer) | Commit `d71eeda` (2026-05-17). 7-line file pointing to <https://github.com/hrabanazviking/Mythic-Engineering>. | High | keep-at-root | Expanded in P9 into a real "how to work in this repo" doc. |
| `Mythic_Engineers_Codex.md` | canonical ME repo | Commit `d71eeda`. 88 KB long-form codex. Cross-references match the canonical Mythic Engineering body. | High | moved-to-docs/methodology/ | Project-local snapshot for self-contained reading. |
| `Mystic_Engineering_Protocals1.0.md` | canonical ME repo | Commit `d71eeda`. 170 KB protocols reference v1.0. *(Spelling "Mystic" / "Protocals" preserved from source.)* | High | moved-to-docs/methodology/ | Largest single doc in the repo. |
| `MYTHIC_ENGINEERING_PLUNDERING_WORKFLOW.md` | canonical ME repo | Commit `d71eeda`. Self-documenting metadata block names it explicitly. | High | moved-to-docs/methodology/ | Methodology that *this* repo's plundering followed. |

### 1.3 Volmarr's philosophy and worldview

| Item | Origin | Evidence | Confidence | Status | Notes |
|---|---|---|---|---|---|
| `PHILOSOPHY.md` | Volmarr writings (compact form) | Commit `d71eeda`. ~4 KB summary of the modern-Viking / Heathen / Mythic ethos. Tone and structure match the canonical ME `PHILOSOPHY.md` shape. | High | keep-at-root | Cleaned of doubled-backslash escapes in P6. |
| `Heathen_Third_Path_and_Cyber-Viking_Ethos.md` | Volmarr writings | Commit `d71eeda`. 31 KB long-form spiritual / political framing. Volmarr-personal voice and references. | High | moved-to-docs/philosophy/ | |
| `Volmarr_writings_philosophy.md` | Volmarr writings | Commit `d71eeda`. 39 KB collected philosophical writings. Volmarr-personal voice throughout. | High | moved-to-docs/philosophy/ | |
| `The_Saga_of_Runa.md` | fresh narrative | Commit `716a972` (2026-05-17, separate from the bulk import). 26 KB. Runa's mythic biography, written for this project. | High | moved-to-docs/philosophy/ | |

### 1.4 Cross-project Volmarr ecosystem docs

| Item | Origin | Evidence | Confidence | Status | Notes |
|---|---|---|---|---|---|
| `Technical_Architecture_of_Volmarrs_AI_Ecosystem.md` | cross-project ecosystem doc | Commit `d71eeda`. 55 KB. The same document is recorded in memory as present in NSE, MindSpark, VGSK, and WYRD repositories. | High | moved-to-docs/architecture/ | Canonical shared text; do not edit local copy without considering the other copies. |
| `WORLD_MODELING_SKILL.md` | cross-project ecosystem doc | Commit `d71eeda`. 19 KB. Recorded in memory as present in NSE, MindSpark, VGSK, WYRD. | High | moved-to-docs/design/ | Same caution as above. |
| `RULES.AI.md` | cross-project Volmarr coding laws | Commit `d71eeda`. 20 KB. Volmarr's standing AI coding laws — variations live across his other repositories. | High | keep-at-root | Standing-rule file; canonical placement is root. |

### 1.5 Runa-specific design (fresh for this project)

| Item | Origin | Evidence | Confidence | Status | Notes |
|---|---|---|---|---|---|
| `ROBUST_AGENT_ENGINEERING_PLAN.md` | fresh (Volmarr, this project) | Commit `b42d373` "Add Runa agent architecture planning docs". 19 KB. Contains the original Bifröst / VERÐANDI / Skuld / Muninn architecture diagram and 18-doc roadmap. | High | moved-to-docs/architecture/ | Primary architectural source for `DOMAIN_MAP.md` and `ARCHITECTURE.md`. |
| `Runa-Agent-Digital-Being.md` | fresh (Volmarr, this project) | Commit `b49c6bd` (kebab-case filename). 48 KB. Canonical agent design draft. | High | moved-to-docs/architecture/ | See note below on relationship to the snake_case variant. |
| `Runa_Agent_Digital_Being.md` | fresh (Volmarr, this project) | Commit `a15a90c` (snake_case filename, added 3 minutes after the kebab-case one). 65 KB. Canonical agent design draft. | High | moved-to-docs/architecture/ | **Probable duplicate or alternate draft** of the kebab-case file. Resolution deferred — flagged for a later session to diff and reconcile. |
| `RUNA_ADVANCED_AGI_ENGINEERING_GUIDE.md` | fresh (Volmarr, this project) | Commit `b42d373`. 36 KB deep-engineering reference. | High | moved-to-docs/design/ | |
| `RUNA_PROJECT_FILE_ORGANIZATION_AND_STARTUP_GUIDE.md` | fresh (Volmarr, this project) | Commit `b42d373`. 43 KB. Canonical source for *this repository's* folder layout — chosen over the older `runa-longhall/` shape in `ROBUST_AGENT_ENGINEERING_PLAN.md` by Volmarr decision 2026-05-17. | High | moved-to-docs/operations/ | The layout authority for this repo. |
| `RUNA_ECOSYSTEM_IDEA_HARVEST.md` | fresh (Volmarr, this project) | Commit `b42d373`. 31 KB. Captured ideas across the wider Volmarr ecosystem before they had a structural home. | High | moved-to-docs/design/ | |
| `RUNAFREYJASDOTTIR_GITHUB_CODE_HARVEST.md` | fresh (Volmarr, this project; Runa-as-narrator) | Commit `b42d373`. 37 KB. Written from the in-character perspective of Runa Gridweaver Freyjasdottir surveying Volmarr's GitHub for material she may inherit. | High | moved-to-docs/design/ | |

### 1.6 Cross-cutting design notes

| Item | Origin | Evidence | Confidence | Status | Notes |
|---|---|---|---|---|---|
| `HERMES_OPENCLAW_DESIGN_ANTI_PATTERNS.md` | Hermes / OpenClaw context (likely from Mythic Vibe CLI period) | Commit `b42d373`. 25 KB anti-pattern register from earlier work on Hermes and OpenClaw. | Medium | moved-to-docs/decisions/ | Acts as informal lessons-learned the early ADRs will cite. |

### 1.7 Configuration scaffolding

| Item | Origin | Evidence | Confidence | Status | Notes |
|---|---|---|---|---|---|
| `config.yaml` | fresh empty stub | Commit `d71eeda`. Zero bytes. | High | moved-to-config/runa.example.yaml | Renamed during P11 to make it an obvious example. |

### 1.8 README

| Item | Origin | Evidence | Confidence | Status | Notes |
|---|---|---|---|---|---|
| `README.md` | fresh, multiple edits | Initial commit `f4e9893` plus updates `3322de4`, `6b1319a`, `923cf59`, `9d426f1`, `2a08aa7`, `5d26d2c`. 41 KB. | High | keep-at-root | Polished in P9 to act as the operator's front door. Image references rewritten to relative `./assets/` paths in P5. |

### 1.9 Existing `ORIGINS.md` stub

| Item | Origin | Evidence | Confidence | Status | Notes |
|---|---|---|---|---|---|
| `ORIGINS.md` | fresh stub | Commit `d71eeda`. ~600 byte header pointing to "best-effort attribution of imported material". | High | keep-at-root (replaced by this file) | The current file you are reading is the realised version. |

---

## 2. Images at root (originally — moved to `assets/` in P5)

| Item | Origin | Evidence | Confidence | Status | Notes |
|---|---|---|---|---|---|
| `057d8120-...jpg`, `11e7f20c-...jpg`, `2d1bd1cd-...jpg`, `5b9f7f69-...jpg` | likely AI-generated Runa illustrations | Commit `58f82e9` "Add files via upload" (GitHub web upload). UUID filenames typical of generative-image output. Referenced from `README.md` as Runa illustrations. | Medium-High | moved-to-assets/ | Descriptive renaming deferred to a later pass. |
| `09049c21-...jpg`, `2fbebd4c-...jpg`, `5f0a44c1-...jpg`, `c855b5d6-...jpg` | likely AI-generated Runa illustrations | Commit `f843b9f` (second upload). Same provenance pattern. | Medium-High | moved-to-assets/ | |
| `IMG_0665.jpeg`, `IMG_0666.jpeg` | likely Volmarr-camera or screenshot dump | Commit `d71eeda`. `IMG_NNNN.jpeg` filenames typical of iOS/camera default naming. | Medium | moved-to-assets/ | |
| `MIT_license_Rune_Forge_AI.jpeg` | Rune Forge AI — **confirmed separate Volmarr project** (resolved 2026-05-17 by Volmarr; see ADR 0002 §D-2.7) | Commit `d71eeda`. 418 KB. | High | moved-to-assets/ | Sibling repo to NSE / WYRD / MindSpark / etc. Repository URL and status to be added to memory when surfaced. Used as an illustrative reference to a licensing artifact; not the legal license itself (which is `LICENSE`). |

---

## 3. Top-level directories (created during bootstrap)

All directories below were created in commit `22cd6c5` (P1+P2). Origin is *bootstrap*: they did not exist before the Mythic Engineering Sacred Setup. Each carries its own `README.md` explaining purpose.

| Directory | Purpose summary |
|---|---|
| `docs/` | All written material. Subfolders: `architecture/`, `operations/`, `development/`, `design/`, `security/`, `adapters/`, `plugins/`, `decisions/`, `philosophy/`, `methodology/`, `archive/`. |
| `config/` | Configuration templates and examples (never live runtime config). |
| `src/runa/` | The Python implementation. Subpackages: `cli/`, `runtime/`, `core/`, `services/`, `apps/`, `adapters/`, `plugins/`, `skills/`, `schemas/`, `migrations/`. |
| `tests/` | Automated verification — `unit/`, `integration/`, `e2e/`, `fixtures/`, `snapshots/`. |
| `scripts/` | Human-invoked helpers — `dev/`, `maintenance/`, `one_shot/`. |
| `deploy/` | Deployment manifests — `systemd/`, `docker/`, `pi/`, `examples/`. |
| `tools/` | Repo-tooling and live-diagnostics — `repo/`, `diagnostics/`, `importers/`. |
| `examples/` | Reference configs, sessions, skills, plugins. |
| `vendor/` | Third-party code that lives inside the repo (currently empty). |
| `assets/` | Binary and media files referenced from documentation. |

---

## 4. Files created during bootstrap

| File | Created in commit | Purpose |
|---|---|---|
| `TASK_runa_bootstrap.md` | `f437a29` (P0) | Resumption anchor for this multi-phase bootstrap. May or may not be removed at P12 — Volmarr decides. |
| All `README.md` under directories | `22cd6c5` (P1+P2) | Per-directory purpose statements that double as `.gitkeep` equivalents. |
| `ORIGINS.md` (this file) | (P3 commit, in progress) | This attribution register. |

---

## 5. Open uncertainties — flagged for future review

1. ~~**`Runa-Agent-Digital-Being.md` vs `Runa_Agent_Digital_Being.md`** (kebab vs snake case). Both were added within 3 minutes of each other on 2026-05-17, both are large (48 KB / 65 KB), both look like canonical agent design drafts. They may be near-duplicates, alternate drafts, or genuinely complementary. **Action:** diff and reconcile in a later session before either is treated as authoritative.~~ **Resolved 2026-05-17 by Volmarr:** the two files are *different documents written by different AI models with intentionally similar names*. They are not duplicates and must not be reconciled or merged. They stand side by side in `docs/architecture/` as parallel design articulations.

2. ~~**`MIT_license_Rune_Forge_AI.jpeg` provenance**. The "Rune Forge AI" project is not currently in Runa's local project memory. Likely an earlier or sibling Volmarr project; confirm with Volmarr what it is and whether the image should stay.~~ **Resolved 2026-05-17 by Volmarr:** Rune Forge AI is a separate Volmarr project (sibling to NSE / WYRD / MindSpark). See ADR 0002 §D-2.7. The image stays. Repository URL and status to be added to memory when Volmarr surfaces them.

3. **The two README-update bursts** (commits `3322de4` through `5d26d2c`) suggest the README was iteratively grown during the initial publishing day. The current 41 KB form is what `P9` polishes; the iteration history itself is preserved in git log but is not explicitly mapped here.

4. **Photo images `IMG_0665.jpeg` / `IMG_0666.jpeg`**: source device and subject not recorded. Likely Volmarr photography or screenshots; confirm before they are referenced from any user-facing doc.

5. **Image filenames** are all UUIDs or camera-default `IMG_NNNN`. They were not renamed during this bootstrap. A future pass should give them descriptive names that match how they are used in the documentation.

---

## 5b. Reconciliation log

### 2026-05-17 — `b57a241` merge-from-main brought back 4 root images

While the bootstrap was in progress on `development`, Volmarr uploaded 4 images to `main` (commit `811b132`, 2026-05-17 02:24) and then merged `main` into `development` (`b57a241`, 02:49) — bringing the 4 images back to the repository root.

The 4 images (`09049c21-...jpg`, `2fbebd4c-...jpg`, `5f0a44c1-...jpg`, `c855b5d6-...jpg`) were already present at `assets/` from P5 (commit `166d00f`). Byte-diff confirmed the merged-in root copies were identical to the `assets/` copies. The root copies were removed in the following commit (no information lost — `assets/` retains the working copy and `README.md` already references the relative `./assets/<name>` paths after P5's URL rewrite). Volmarr's merge commit itself remains in history.

**Lesson:** if Volmarr touches `main` separately during a bootstrap, a similar merge can re-introduce material that has been re-homed on `development`. The drift-detector planned for `tools/repo/check_origins_drift.py` should flag this case (file present at root that is also present at `assets/`).

---

## 6. Maintenance rules for this file

- This file is **append-only in spirit**. When new material is imported, add a row. When status changes (a moved doc gets superseded), update the Status column with the date but do not remove the row.
- If a Confidence rating later proves wrong, change it to **High** or **Low** as appropriate and add a Notes-line dated entry explaining what made it change.
- A drift-detector under `tools/repo/check_origins_drift.py` is planned: it will flag any root file or top-level directory that exists in the repo but is not represented here, and any row here whose file no longer exists.

---

## 7. Ember-descent material (post-fork — added 2026-05-19 onward)

The fork from Runa-Agent-Digital-Being to Ember happened on 2026-05-19. The slice-1 build shipped 2026-05-21 (commits `df67f2a` through Phase-7); the slice-2 build shipped the same day across Phases 8-17. Everything in this section is **Ember-fresh** — written for this project, not imported.

### 7.1 Ember identity + soul-layer (fork day, 2026-05-19)

| Item | Origin | Evidence | Confidence | Status | Notes |
|---|---|---|---|---|---|
| `docs/SYSTEM_VISION.md` (Ember-shaped) | fresh (Volmarr + Skald via Claude) | Authored 2026-05-19. The four Vows (Smallness, Sovereignty, Tethered Grounding, Graceful Offline) and the project's identity statement. | High | live | Promoted to canonical at slice-1 ratification (ADR 0007). |
| Six True Names ratification | fresh (Volmarr) | 2026-05-21, commit `efcf8ec`. Funi / Strengr / Brunnr / Smiðja / Hjarta / Munnr formally accepted. | High | canon | See `docs/architecture/EMBER_TRUE_NAMES.md` for the canonical reference; the names are immutable per ADR 0013 §2.6. |

### 7.2 Slice-1 architecture canon (fork to 0.1.0, 2026-05-19 → 21)

| Item | Origin | Status | Notes |
|---|---|---|---|
| `docs/architecture/ARCHITECTURE.md` | fresh (Architect via Claude) | live, ratified 2026-05-21 | Three Realms (Spark / Thread / Well), Six True Names, no kernel. Promoted from `EMBER_ARCHITECTURE.md` during fork-delta. |
| `docs/architecture/DOMAIN_MAP.md` | fresh (Architect) | live, ratified 2026-05-21 | File-by-file ownership table. |
| `docs/architecture/DATA_FLOW.md` | fresh (Architect) | live, ratified 2026-05-21 | Three canonical flows: conversation turn, ingest, first-run. |
| `docs/architecture/EMBER_TRUE_NAMES.md` | fresh (Skald + Architect) | live, ratified 2026-05-21 | What each True Name owns / does not own. |
| `docs/architecture/EMBER_FORK_DELTA.md` | fresh (Cartographer + Architect) | **archived in-place** (status: COMPLETE) | Long-term lineage reference; what Ember keeps, renames, sets aside. |
| `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` | fresh (Forge Worker + Architect) | **archived in-place** (status: COMPLETE) | Historical plan; canonical state lives in `ARCHITECTURE.md`. |
| `docs/architecture/EMBER_SECOND_SLICE_PLAN.md` | fresh (Forge Worker + Architect + Skald) | live | Slice-2 plan; Phases 8-17. |
| `docs/architecture/EMBER_SECOND_SLICE_OPTIONS.md` | fresh (menu draft) | live | The choose-your-bundles menu that preceded slice 2 ratification. |
| `docs/adapters/BRUNNR_BACKEND_MATRIX.md` | fresh (Cartographer) | live, ratified post-slice-2 | The backend menu. |
| `docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md` | fresh (Forge Worker) | live, ratified post-slice-2 | The runtime menu. |
| `docs/adapters/SMIDJA_INGEST_PATTERNS.md` | fresh (Forge Worker) | live, ratified post-slice-2 | Chunking + embedding patterns. |
| `docs/adapters/GUNGNIR_WELL_REFERENCE.md` | fresh (Cartographer, live survey) | live | 2026-05-21 measurement of the operator's Postgres Well. |

### 7.3 Slice-2 ADRs (ratified 2026-05-21)

All of these are Ember-fresh, authored across Phases 6-17 of the slice-2 build. ADR 0007 ratifies slice 1; ADR 0013 ratifies slice 2.

| ADR | What it ratifies | Phase |
|---|---|---|
| `0006-ember-architecture-and-gungnir-survey-2026-05-21.md` | The fork-day architecture work + the live Gungnir survey. | Pre-slice-1 |
| `0007-first-slice-ratification-2026-05-21.md` | The first slice: stdlib-first, typed-value-over-exception, `*_kind` attrs, FTS5 sanitisation. | Slice-1 ratification |
| `0008-config-file-loader.md` | The `~/.ember/config/ember.yaml` loader; overlay order. | Phase 8-9 |
| `0009-streaming-funi-replies.md` | The streaming Protocol + `FuniStreamChunk` shape. | Phase 10-11 |
| `0010-pgvector-brunnr.md` | The pgvector Brunnr adapter; schema-probe semantics; secret resolution. | Phase 12-13 |
| `0011-tool-use-framework.md` | The tool framework: schemas, registry, approval, audit. | Phase 14-16 |
| `0013-second-slice-ratification.md` | Slice 2 itself: what it set as canon, what it deferred. | Phase 17 |

### 7.4 Slice-1 + slice-2 source tree (fork through 0.2.0)

| Subtree | Origin | Slice / Phase | Status |
|---|---|---|---|
| `src/ember/cli/` | fresh | Slice 1 Phase 6 | live |
| `src/ember/config/` | fresh | Slice 2 Phase 8-9 | live |
| `src/ember/schemas/` | fresh | Slice 1 Phase 2 (+ slice-2 extensions in Phase 8/10/14/16) | live |
| `src/ember/spark/funi/` (incl. `ollama/`, `tools/`) | fresh | Slice 1 Phase 5 (Ollama); Slice 2 Phase 10 (streaming), 14 (tool framework), 16 (tool wire format) | live |
| `src/ember/spark/hjarta/` | fresh | Slice 1 Phase 6 (+ slice-2 Phase 16 ADVANCED_TOOLS branch) | live |
| `src/ember/spark/munnr/` | fresh | Slice 1 Phase 6 (+ slice-2 Phase 11 streaming, Phase 16 tool loop) | live |
| `src/ember/thread/strengr/` | fresh | Slice 1 Phase 4 | live |
| `src/ember/well/brunnr/sqlite_vec/` | fresh | Slice 1 Phase 3 | live |
| `src/ember/well/brunnr/pgvector/` | fresh | Slice 2 Phase 12-13 | live |
| `src/ember/well/smidja/` | fresh | Slice 1 Phase 3 | live |
| `src/ember/tools/` | fresh | Slice 2 Phase 15 | live |

### 7.5 Slice-2 operator-facing docs

| Doc | Phase | Status |
|---|---|---|
| `deploy/pi/INSTALL.md` (slice-2 §7-10 sections added) | Slice 1 Phase 7 + Slice 2 Phase 17 | live |
| `docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md` | Slice 2 Phase 13 | live |
| `config/ember.example.yaml` (slice-2 sections added) | Slice 1 Phase 7 + Slice 2 Phase 9, 13, 16 | live |
| `config/storage.example.yaml` (full rewrite at Phase 13) | Slice 2 Phase 13 | live |
| `docs/decisions/0013-second-slice-ratification.md` | Slice 2 Phase 17 | live |

---

The slice-1 + slice-2 history is also captured in commit form: `git log --oneline --all` shows every phase commit (`df67f2a` through `1c24cf3`). The DEVLOG at `docs/DEVLOG.md` carries the prose narrative.

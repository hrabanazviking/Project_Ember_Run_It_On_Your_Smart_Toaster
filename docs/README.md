# docs/

All written material lives under `docs/`. Source code lives under
`src/`. The split is hard: nothing under `docs/` ever runs, and nothing
under `src/` is the primary place to learn how Ember works.

**Last touched:** 2026-05-21 (slice 2 ratified, ADR 0013).

---

## Subfolders

| Folder | Holds |
|---|---|
| `architecture/` | The canonical Ember shape: `ARCHITECTURE.md`, `DOMAIN_MAP.md`, `DATA_FLOW.md`, `EMBER_TRUE_NAMES.md`, plus the slice plans (`EMBER_FIRST_SLICE_PLAN.md`, `EMBER_SECOND_SLICE_PLAN.md`) and the fork-delta. |
| `adapters/` | Per-adapter operator references: `BRUNNR_BACKEND_MATRIX.md`, `FUNI_LOCAL_MODEL_OPTIONS.md`, `SMIDJA_INGEST_PATTERNS.md`, `GUNGNIR_WELL_REFERENCE.md`, `PGVECTOR_BRUNNR_REFERENCE.md`. |
| `decisions/` | Architecture Decision Records, one per major commitment. Slice-1 ratified in ADR 0007; slice-2 in ADR 0013. ADRs 0008-0011 set the slice-2 design contracts. |
| `operations/` | Operator runbooks — installation, startup, shutdown, repair, backup. Currently inherits one cross-project doc; the slice-2 operator install lives at `deploy/pi/INSTALL.md` (more comprehensive). |
| `development/` | Reserved for contributor-side documentation: local dev setup, test-running, coding conventions specific to Ember. The slice-2 standing rules are baked into ADR 0007 §2 + ADR 0013 §2.1; this folder will expand when the project takes outside contributors. |
| `design/` | Long-form design explorations and idea harvests that informed architecture but did not become ADRs. Mostly Runa-era material the fork preserved; consult `EMBER_FORK_DELTA.md` for which ideas survived into Ember. |
| `security/` | Threat model, trust boundaries, secrets handling, sandbox policy. Slice-2 added the tool-use sandbox rules (ADR 0011 §2.5-2.7) and the pgvector secret resolver (ADR 0010 §2.5); a consolidated security overview is queued for slice 3. |
| `plugins/` | Reserved for future plugin-author guidance. The `src/ember/plugins/` scaffold stays empty per ADR 0013 §2.7 until slice 3 drafts the plugin contract. |
| `philosophy/` | Volmarr's worldview material — Heathen / cyber-Viking / mythic-engineering ethos. The compact `PHILOSOPHY.md` lives at repo root; the long-form pieces live here. |
| `methodology/` | Mythic Engineering reference material — *how* we build, not *what* we build. Includes the canonical ME codex and protocols. |
| `archive/` | Retired docs preserved for history. Includes the pre-fork Runa-shaped architecture under `archive/runa-inherited/`. **Never delete; move here instead.** |
| `research/`, `python/`, `phd-2040/`, `RunaUniversity2040/`, `AI_OS_Research/` | Inherited corpora preserved as intellectual heritage. Not load-bearing for code work; the user values them for cross-referencing. |

---

## Top-level documents

| File | What it is |
|---|---|
| `DEVLOG.md` | Append-only daily/per-session record. Read at session start; the Cartographer's first reference and the Scribe's last word. |
| `SYSTEM_VISION.md` | Skald-written — the soul of Ember in one short doc. The first thing to read after the repo README. |
| `REPO_MAP.md` | One-line description of every folder in the repository. Operator's second stop after `README.md`. |

---

## Reading order for new contributors

1. **`README.md`** (repo root) — what Ember is, why it exists.
2. **`docs/SYSTEM_VISION.md`** — the four Vows + Six True Names.
3. **`docs/architecture/ARCHITECTURE.md`** — the Three Realms band separation.
4. **`docs/architecture/DOMAIN_MAP.md`** — file-by-file ownership.
5. **`docs/architecture/EMBER_TRUE_NAMES.md`** — what each True Name does and does not own.
6. **`docs/decisions/0007-...`** + **`0013-...`** — the two ratification ADRs that bound the slices.
7. **`docs/DEVLOG.md`** — the actual history of the build.
8. **`deploy/pi/INSTALL.md`** — the operator's install + slice-2 capability guide.

---

## Maintenance rule

Docs go stale fastest. RULES.AI.md §"Keep data files current" applies
here — when code ships a phase, the relevant doc gets a touch in the
same commit. If you find a doc with `(planned for slice X)` for a
slice that has already shipped, that's a bug; file it or fix it.

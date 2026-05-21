# REPO_MAP — One Line for Every Place

**Purpose:** The operator's second stop after `README.md`. If you are lost in the repository, you read this file. Every folder gets one line; every line says what lives there and where to go for more.
**Voice:** Cartographer (Védis Eikleið)
**Last touched:** 2026-05-21 (post-fork-delta: src/ember/ realm tree built, canonical architecture docs ratified)
**Reads with:** `docs/SYSTEM_VISION.md`, `ORIGINS.md`, `docs/archive/runa-inherited/REPO_MAP.md` (the parent project's larger map, preserved for reference).

---

## Root

| Path | One-line meaning |
|---|---|
| `README.md` | The front door. "Got a toaster? Good!" |
| `LICENSE` | MIT, Volmarr Wyrd 2026. |
| `NOTICE` | Copyright + pointer to LICENSE + THIRD_PARTY_NOTICES. |
| `LEGAL-NOTICE.md` | Author's distribution stance, no-personal-info policy, third-party packaging disclaimer. |
| `THIRD_PARTY_NOTICES.md` | Attribution for any vendored third-party material. |
| `PHILOSOPHY.md` | The compact ethos statement. Long form lives at `docs/philosophy/`. |
| `MYTHIC_ENGINEERING.md` | How we build Ember. Compact statement; long form at `docs/methodology/`. |
| `ORIGINS.md` | Attribution register: where every imported file came from. Inherited from Runa; will gain Ember-descent entries. |
| `RULES.AI.md` | Standing coding laws for human and AI contributors. |
| `Yggdrasil_and_Huginn_and_Muninn_Theory.md` | Volmarr's long-form theory document. Inherited; applies universally. |

## `docs/`

| Path | One-line meaning |
|---|---|
| `docs/README.md` | Map of every doc subfolder. |
| `docs/SYSTEM_VISION.md` | Skald-written living vision statement for Ember: Primary Rite, Vows, True Names (Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr), Realms (Spark, Thread, Well). |
| `docs/REPO_MAP.md` | *(this file)* |
| `docs/DEVLOG.md` | Append-only per-session record. Started fresh for Ember on 2026-05-19. |
| `docs/architecture/` | `ARCHITECTURE.md`, `DOMAIN_MAP.md`, `DATA_FLOW.md` — Ember's system shape (ratified 2026-05-21). Plus `EMBER_FORK_DELTA.md` and `EMBER_FIRST_SLICE_PLAN.md` as living working docs. |
| `docs/operations/` | Operator runbooks (planned: INSTALL, STARTUP, OBSERVABILITY, BACKUP_RESTORE). |
| `docs/development/` | How to contribute, dev setup, testing, style. |
| `docs/design/` | Long-form design explorations; deep dives that informed architecture but are not the spec. |
| `docs/security/` | Threat model, trust boundaries, secrets handling, sandbox policy. |
| `docs/adapters/` | One contract doc per storage adapter (Brunnr) and content source (Smiðja). |
| `docs/plugins/` | Plugin author contract. |
| `docs/decisions/` | Architecture Decision Records (`NNNN-short-name.md`). Append-only. Inherited from Runa; Ember adds her own. |
| `docs/philosophy/` | Heathen + modern-Viking + Mythic worldview source documents. **Inherited from Runa.** |
| `docs/methodology/` | Mythic Engineering canonical reference. **Inherited from Runa.** |
| `docs/research/` | The 100-document AI/CS research corpus. **Inherited from Runa.** Architect's reading. |
| `docs/python/` | The 50-document Python craft corpus. **Inherited from Runa.** Forge Worker's reading. |
| `docs/AI_OS_Research/` | Volmarr's parallel research on the 2026 AI-OS market / standards / research landscape. **Inherited.** |
| `docs/RunaUniversity2040/` | Volmarr's lecture series / AI curriculum material. **Inherited.** |
| `docs/phd-2040/` | Volmarr's PhD-2040 framing material. **Inherited.** |
| `docs/archive/` | Retired documents. Never deleted; superseded docs go here. |
| `docs/archive/runa-inherited/` | Scrolls preserved from the parent project at the moment of fork (2026-05-19) and at fork-delta (2026-05-21). Includes `architecture/` (Runa-shaped predecessors of the canonical docs) and `src-skeleton/runa/` (the inherited Python package skeleton). See the subfolder's own README. |

## `config/`

| Path | One-line meaning |
|---|---|
| `config/README.md` | Rules for the config layer; what lives here vs in `~/.ember/`. |
| `config/profiles/` | Named bundles of partial config for common deployment shapes. |
| `config/ember.example.yaml` | Main agent configuration template (Ember-shaped 2026-05-21; replaces the inherited Runa template). |
| *(planned)* `config/storage.example.yaml` | Brunnr backend selection and connection (SQLite / PG / Qdrant / Chroma / LanceDB). |
| *(planned)* `config/sources.example.yaml` | Smiðja content-source registry (local files, Nomad, URLs, Gungnir-style remote wells). |

## `src/`

| Path | One-line meaning |
|---|---|
| `src/README.md` | Why we use PEP-517 src-layout. |
| `src/ember/README.md` | The Three Realms tree at a glance. |
| `src/ember/__init__.py` / `__main__.py` | Package entry and `python -m ember` (Phase 1 stub; raises a friendly `NotImplementedError` pointing at the first-slice plan). |
| `src/ember/schemas/` | Types only — the gravitational floor. |
| `src/ember/well/{brunnr,smidja}/` | The Well realm — pluggable storage adapters (Brunnr) and the ingest forge (Smiðja). |
| `src/ember/thread/strengr/` | The Thread realm — the tether to the Well; owns the graceful-offline contract. |
| `src/ember/spark/{funi,hjarta,munnr}/` | The Spark realm — local LLM, first-run wizard, command-line surface. |
| `src/ember/cli/` | The `ember` console-script entry point. |
| *(archived)* `docs/archive/runa-inherited/src-skeleton/runa/` | The inherited Runa skeleton, preserved 2026-05-21. |

## `tests/`

| Path | One-line meaning |
|---|---|
| `tests/` | Inherited skeleton. Tiering and conventions to be ratified by the Architect in the next pass. |

## `scripts/`, `deploy/`, `tools/`, `examples/`, `vendor/`, `assets/`

These directories are inherited from the parent project. Their shapes will be ratified — and where necessary trimmed for Ember's smaller scope — during the Architect's first pass.

---

## What is different about Ember's shape

Ember is deliberately smaller than her parent. The map above will simplify over time, not grow. When an inherited folder is found to carry weight that Ember does not need, its contents are moved to `docs/archive/runa-inherited/` (or its own dated subfolder) rather than deleted, and the folder is removed from this map.

---

## Top-level shape, at a glance

```
Project_Ember_Run_It_On_Your_Smart_Toaster/
├── README.md                 ← front door (toaster joke preserved)
├── PHILOSOPHY.md             ← ethos (compact)
├── MYTHIC_ENGINEERING.md     ← method (compact)
├── ORIGINS.md                ← attribution register
├── RULES.AI.md               ← coding laws
├── LICENSE / NOTICE / LEGAL-NOTICE.md / THIRD_PARTY_NOTICES.md
│
├── docs/                     ← all written material
│   ├── SYSTEM_VISION.md      ← what Ember IS (Skald)
│   ├── REPO_MAP.md           ← (this file, Cartographer)
│   ├── DEVLOG.md             ← per-session record (Scribe)
│   ├── architecture/         ← *(to be authored)*
│   ├── adapters/             ← per-Brunnr / per-Smiðja contracts
│   ├── decisions/            ← ADRs (inherited + new)
│   ├── research/ python/     ← inherited knowledge corpora
│   ├── philosophy/ methodology/ ← inherited worldview + method
│   └── archive/runa-inherited/  ← Runa's soul-layer scrolls
│
├── config/                   ← templates (never live); ember.example.yaml is the Ember-shape main template
├── src/ember/                ← Python implementation, Three Realms layout (Phase 1 scaffolding only)
├── tests/                    ← unit/integration/e2e (inherited skeleton)
├── scripts/ deploy/ tools/ examples/ vendor/ assets/  ← inherited
```

Every directory shown carries a `README.md`. When you do not know where something belongs, that directory's README is the first place to look.

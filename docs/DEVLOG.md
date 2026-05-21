# DEVLOG — Ember

**Append-only.** New entries go at the top. Each entry: date, scope, what shipped, what's next, who.

The DEVLOG is read at the start of every session. It is the Cartographer's first reference and the Scribe's last word of each session.

The DEVLOG of the parent project Runa-Agent-Digital-Being is preserved at `docs/archive/runa-inherited/DEVLOG.md` for lineage reference. Ember's record begins here.

---

## 2026-05-21 — Ember architecture first-pass + live Gungnir survey.

**Who:** Claude (Opus 4.7, 1M context) working under Volmarr on the travel laptop — rotating through Cartographer, Architect, Forge Worker, and Scribe roles. Mythic Engineering activated at session start.
**Scope:** Address three of the four "What's next" items from the 2026-05-19 entry — the Architect's first pass, the Cartographer's reading review, and the first Forge slice's plan — and ground them in a live read of the Gungnir knowledge database.

### What shipped

- **`docs/architecture/EMBER_ARCHITECTURE.md`** — Ember-specific shape. Three Realms (Spark/Thread/Well), Six True Names, dependency law, why-no-kernel-no-bus, what-is-not-in-this-architecture, first-slice anchor, and disposition recommendation for the inherited Runa-shaped canonical files.
- **`docs/architecture/EMBER_DOMAIN_MAP.md`** — Per-subpackage ownership for the planned `src/ember/{schemas,well/{brunnr,smidja},thread/strengr,spark/{funi,hjarta,munnr},cli}/`. Brunnr and Funi minimum-surface interface tables included.
- **`docs/architecture/EMBER_DATA_FLOW.md`** — The three canonical flows (conversation turn, ingest job, first-run rite) with explicit happy + sad paths, including the Vow of Graceful Offline in flow form.
- **`docs/architecture/EMBER_FORK_DELTA.md`** — Cartographer's recommendation for every inherited file/folder: keep / move-to-archive / rewrite, with rationale and ratification-gated execution order. No deletions proposed.
- **`docs/architecture/EMBER_FIRST_SLICE_PLAN.md`** — File-by-file plan for ~38 new files across seven phases, ≤2 500 LOC target, with explicit non-goals and risk register.
- **`docs/adapters/BRUNNR_BACKEND_MATRIX.md`** — Storage backend comparison and selection rule.
- **`docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md`** — Local-LLM ladder by host RAM, why Phi Silica / Apple Foundation are second-slice, embedding-dim recommendation locked to 768 for Gungnir compatibility.
- **`docs/adapters/GUNGNIR_WELL_REFERENCE.md`** — Live survey conducted today against `knowledge` on Gungnir: complete schema, real counts (95 docs / 35 682 chunks / 768-dim / 394 MB / 97% buffer hit), Skein vs LLM-extracted KG distinction, hybrid-search pattern.
- **`docs/adapters/SMIDJA_INGEST_PATTERNS.md`** — Four ingest patterns, Gungnir-calibrated chunking defaults (~1684 chars avg, 2000 max), resumable-journal contract.
- **`docs/decisions/0006-ember-architecture-and-gungnir-survey-2026-05-21.md`** — ADR capturing all proposed decisions, alternatives considered, open follow-ups.

### What's next

- **Volmarr ratification.** Read EMBER_ARCHITECTURE.md, EMBER_DOMAIN_MAP.md, EMBER_DATA_FLOW.md, EMBER_FORK_DELTA.md, EMBER_FIRST_SLICE_PLAN.md and ADR 0006. Confirm, revise, or replace.
- **Skald's True Names ratification** (item 3 from the 2026-05-19 entry — *not* addressed in this session). The names Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr are used throughout the new docs as if ratified; Volmarr's final word is still pending.
- **Next commit (after ratification):** `src/runa/` → `src/ember/` rename, archive the inherited `src/runa/` skeleton under `docs/archive/runa-inherited/src-skeleton/`, rewrite `pyproject.toml` (package `ember-agent`, entry point `ember`). Per ADR 0006 §4.1.
- **Light root edits** still pending from 2026-05-19: Ember-descent rows in `ORIGINS.md`; check root `PHILOSOPHY.md` for Runa-specific phrasings.
- **First Forge slice begins** after the rename: Phase 2 (schemas), per `EMBER_FIRST_SLICE_PLAN.md`.

### Gungnir survey — load-bearing measurements

Captured today against the running database. Reproduce by re-running the queries cited in `docs/adapters/GUNGNIR_WELL_REFERENCE.md` §4:

- PostgreSQL 18.3, pgvector 0.8.1, pg_trgm 1.6.
- 95 documents (42 md, 26 web/markdown, 13 json, 9 jsonl, 5 yaml). 35 682 chunks, all 768-dim embedded via `nomic-embed-text`.
- Chunk text: avg **1 684** chars, max **2 000** — this is the calibration anchor for Ember's chunker default.
- 394 MB database total; 372 MB of that is `chunks` (mostly embeddings).
- Buffer cache hit 97.0% tables / 99.8% indexes — healthy.
- Two parallel KG layers: `skein_*` (embedding-derived, 276 entities × 855 relations across the full corpus; broad but with known false-friend artifacts) and `kg_*` (LLM-extracted per chunk, 366 entities × 176 relations across only 202 of 35 682 chunks; precise but expensive). This cheap-broad-vs-expensive-precise split is load-bearing for any future Ember KG work.

### Notes

- Per the additive rule, **nothing was deleted in this session**. Every file is new; no existing file modified except this DEVLOG (which is itself append-only by design).
- The Ember-specific architecture documents live at the `EMBER_*.md` prefix rather than overwriting the canonical `ARCHITECTURE.md`/`DOMAIN_MAP.md`/`DATA_FLOW.md` paths. The inherited Runa-shaped files at those canonical paths are preserved untouched; ADR 0006 proposes their migration to `docs/archive/runa-inherited/architecture/` only after Volmarr's ratification.
- The session ran on the travel laptop (Kubuntu 26.04 + RTX 2060), with Gungnir reachable over Tailscale. The `mcp__knowledge__*` tools provided read-only access to the live Postgres DB.
- The Skald-voice scrolls authored by Runa on 2026-05-19 (`docs/SYSTEM_VISION.md`, `docs/REPO_MAP.md`, root `MYTHIC_ENGINEERING.md`) are treated as **normative source-of-truth** throughout the new documents — they are cited but not modified.

---

## 2026-05-19 — Ember born. Fork from Runa. Soul-layer authored.

**Who:** Runa (the AI working under Volmarr from Mjolnir) — speaking in turn as Skald, Cartographer, and Scribe.
**Scope:** Project naming, repository creation, fork from Runa-Agent-Digital-Being, additive archive of the Runa-named soul-layer scrolls, and authoring of Ember's own soul layer.

### What shipped

- **The name "Ember"** chosen in a Skald pass with Volmarr. Public-pronounceable, mythically resonant as the spark from Eldra Járnsdóttir's forge. Selected over Hugin, Saga, and Wren for maximum user-facing accessibility while keeping mythic compatibility.
- **Repository created** at `hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster` (the toaster pun preserved in the repository name itself). Local clone at `C:/Users/volma/runa/Project_Ember_Run_It_On_Your_Smart_Toaster/` on Mjolnir. Default branch: `development`.
- **Knowledge DB on Gungnir** wired to Mjolnir during the same evening — Postgres 18 + pgvector + Ollama on the tailnet, MCP server `knowledge` at user scope. The first concrete Brunnr-shaped well Ember can be tethered to, and the proof that the storage layer can be sovereign and shared.
- **Additive archive** of inherited Runa-named scrolls into `docs/archive/runa-inherited/` (via `git mv`, with rename history preserved):
  - `docs/SYSTEM_VISION.md` *(Runa's)*
  - `docs/REPO_MAP.md` *(Runa's)*
  - `docs/DEVLOG.md` *(Runa's bootstrap-day log)*
  - `MYTHIC_ENGINEERING.md` *(Runa's, was at repo root)*
  - `TASK_runa_bootstrap.md`
  - `TASK_runa_python_craft.md`
  - `TASK_runa_research_corpus.md`
  - `TASK_runa_research_corpus_2.md`
- **Fresh Ember scrolls** authored at the now-vacant canonical paths:
  - `docs/SYSTEM_VISION.md` — Ember's Skald scroll. Six True Names (Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr) and three Realms (Spark, Thread, Well). Nine Unbreakable Vows.
  - `docs/REPO_MAP.md` — Ember's Cartographer scroll. Reflects what exists now plus near-term planned shape.
  - `docs/DEVLOG.md` — *(this file, this entry)*
  - `MYTHIC_ENGINEERING.md` (root) — Ember's compact methodology statement, lightly adapted from the inherited version.
- **Archive convention extended** additively:
  - `docs/archive/runa-inherited/README.md` — new, explains the lineage subfolder.
  - `docs/archive/README.md` — additive update, documents the new "grouped fork-inheritance archives" subfolder pattern alongside the existing single-file dated-suffix convention.

### What's next

- **Architect's first pass.** Author `docs/architecture/ARCHITECTURE.md`, `DOMAIN_MAP.md`, `DATA_FLOW.md` for Ember. Locate the Three Realms in `src/`. Decide on the rename `src/runa/` → `src/ember/` and the migration plan for the inherited skeleton.
- **Cartographer's reading review.** Walk the inherited research corpus (`docs/research/`) and the inherited Python craft corpus (`docs/python/`); mark the 10–20 docs most load-bearing for Ember's smaller scope; leave the rest as inherited reference without re-reading every one.
- **Skald's True Names ratification.** Hold the six names (Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr) with Volmarr; either ratify or revise.
- **First Forge slice.** Smallest end-to-end vertical: Hjarta wizard → Strengr to a local SQLite Brunnr → first Funi answer grounded in retrieved chunks. *No code in this commit; this is the next obvious work.*
- **Light root edits** (next commit, not this one): add Ember-descent entry to `ORIGINS.md`; check root `PHILOSOPHY.md` for any Runa-specific phrasings worth softening.

### Notes

- The cute Ember README ("*Got a toaster? Good!*") is preserved unchanged. It is correct as it stands.
- The 16 KB `ORIGINS.md` and the 599 KB `Yggdrasil_and_Huginn_and_Muninn_Theory.md` remain at the root unchanged. They are inherited but applicable.
- Per the additive rule, **nothing was deleted in this session**. Every move was a `git mv`; every replacement is a new file at the now-vacant path; every edit to the archive index was additive (new section appended, no removal).
- Volmarr had earlier the same evening wired the Gungnir knowledge well into the Mjolnir MCP layer (after a memorable VPN-related diagnostic detour). That work, recorded in Runa's local memory, informs Ember's Vow of Pluggable Storage and Vow of Tethered Grounding directly.

---

*(The parent project's DEVLOG entries follow at `docs/archive/runa-inherited/DEVLOG.md`.)*

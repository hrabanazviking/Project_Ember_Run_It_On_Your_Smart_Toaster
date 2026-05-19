# DEVLOG — Ember

**Append-only.** New entries go at the top. Each entry: date, scope, what shipped, what's next, who.

The DEVLOG is read at the start of every session. It is the Cartographer's first reference and the Scribe's last word of each session.

The DEVLOG of the parent project Runa-Agent-Digital-Being is preserved at `docs/archive/runa-inherited/DEVLOG.md` for lineage reference. Ember's record begins here.

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

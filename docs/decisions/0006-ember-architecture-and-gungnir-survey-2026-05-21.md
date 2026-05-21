# ADR 0006 — Ember Architecture First Pass + Gungnir Survey

**Date:** 2026-05-21
**Status:** **Ratified 2026-05-21 by Volmarr.** ("Go for Ember fork delta!")
**Author:** Mythic-Engineering session driven by Volmarr — Cartographer / Architect / Forge Worker / Scribe (roles rotated through the writing)
**Supersedes:** None
**Superseded by:** —

> **Update 2026-05-21 (post-ratification):** the `EMBER_*.md` filenames cited in §2 below have been promoted to the canonical names `ARCHITECTURE.md`, `DOMAIN_MAP.md`, `DATA_FLOW.md`. The Runa-shaped originals at those paths have moved to `docs/archive/runa-inherited/architecture/`. The promotion is recorded in the DEVLOG entry for the fork-delta commit. The text of §2 below is preserved in its as-proposed form for the historical record.

---

## 1. Context

`docs/DEVLOG.md` 2026-05-19 ("Ember born. Fork from Runa.") closed with four named "What's next" items:

1. Architect's first pass: author Ember-specific `ARCHITECTURE.md`, `DOMAIN_MAP.md`, `DATA_FLOW.md`.
2. Cartographer's reading review of the inherited corpora.
3. Skald's True Names ratification with Volmarr.
4. First Forge slice — Hjarta → SQLite Brunnr → first Funi answer.

This session addressed items 1, 2, and 4 in document form (no code yet) and added two additional pieces of work that surfaced during the pass: a complete attribution/disposition map for inherited Runa material (`EMBER_FORK_DELTA.md`) and a live survey of the running Gungnir knowledge database that grounds future Brunnr/Smiðja decisions in real measurements.

## 2. Decision

The following documents are added to the `development` branch. Each is presented as **Proposed — for ratification**, not as a fait accompli. Volmarr's review is what makes any of this canonical.

| File | Purpose | Section reference |
|---|---|---|
| `docs/architecture/EMBER_ARCHITECTURE.md` | Ember-specific shape: Three Realms (Spark/Thread/Well), Six True Names (Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr), dependency law. | §3.1 |
| `docs/architecture/EMBER_DOMAIN_MAP.md` | Per-subpackage ownership for the planned `src/ember/{spark,thread,well,cli,schemas}/` layout. Brunnr/Funi interface tables. | §3.2 |
| `docs/architecture/EMBER_DATA_FLOW.md` | Three canonical flows — conversation turn, ingest job, first-run rite. Including the Vow-of-Graceful-Offline sad paths. | §3.3 |
| `docs/architecture/EMBER_FORK_DELTA.md` | Recommendation for each inherited file/folder: keep / move-to-archive / rewrite. No deletions; ratification-gated migration sequence. | §3.4 |
| `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` | File-by-file plan for the minimum viable Ember (≈38 new files, ≤2 500 LOC), in seven phases. | §3.5 |
| `docs/adapters/BRUNNR_BACKEND_MATRIX.md` | Storage backend comparison (`sqlite_vec`, `pgvector`, `qdrant`, `chroma`, `lancedb`) and selection rule per operator situation. | §3.6 |
| `docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md` | Local-LLM picks ladder by host RAM class. Phi-Silica / Apple Foundation deferred to Phase 8. | §3.7 |
| `docs/adapters/GUNGNIR_WELL_REFERENCE.md` | Live survey of the Gungnir knowledge DB: schema, real counts, KG-layer distinction, hybrid-search pattern. | §3.8 |
| `docs/adapters/SMIDJA_INGEST_PATTERNS.md` | Chunking, embedding, batching, journal, idempotency — calibrated against the Gungnir corpus's measured shape. | §3.9 |

### 3.1 Ember Architecture (proposed)

- **Three Realms** mechanically separated: **Spark** (local thought — Funi/Hjarta/Munnr), **Thread** (the tether — Strengr), **Well** (memory and knowledge — Brunnr/Smiðja).
- **No kernel, no event bus, no Hirð, no Heimskringla, no Eldhugi.** Single synchronous loop; one model; one tether; one well. The Vow of Smallness is the only place these "missing" structures are addressed — they are *deliberately* not in Ember.
- **Dependency law:** `schemas ◄ well ◄ thread ◄ spark ◄ cli`. Acyclic. Boundary violations are release-blocking.
- The inherited `docs/architecture/ARCHITECTURE.md` (Runa's shape) remains at the canonical path until Volmarr ratifies the Ember version. Then it moves additively into `docs/archive/runa-inherited/architecture/`.

### 3.2 Ember Domain Map (proposed)

The planned subpackage layout under `src/ember/` mirrors the Three Realms exactly:

```
src/ember/{schemas,well/{brunnr,smidja},thread/strengr,spark/{funi,hjarta,munnr},cli}/
```

Each subpackage has a one-sentence purpose, an `Owns` list, an explicit `Does not own` negative space, an import allowlist, and a failure-semantics statement. Cross-band imports are forbidden mechanically.

### 3.3 Ember Data Flow (proposed)

Exactly **three** canonical flows in the first slice:

1. **Conversation turn** — operator input → embed → hybrid search → Funi → reply → episode-write. Sad path: well disconnected → ungrounded reply + honest banner + pending-episode local journal.
2. **Ingest job** — source → chunker (~1684 chars, Gungnir-aligned) → embed batch (32) → Brunnr write → resumable journal at `~/.ember/state/smidja_progress/`.
3. **First-run rite (Hjarta)** — finite state machine; prompts as data; atomic identity write at the end.

### 3.4 Fork Delta (proposed)

The full table is in `EMBER_FORK_DELTA.md`. Highlights:

- **Pyproject** must be rewritten (package `ember-agent`, entry point `ember`) in the same commit that renames `src/runa/` → `src/ember/`.
- **Three canonical Runa architecture docs** move into `docs/archive/runa-inherited/architecture/` once the Ember versions are ratified.
- **All inherited corpora kept in full** — research, python, philosophy, methodology, decisions, design, AI_OS_Research, RunaUniversity2040, phd-2040. The Cartographer's note flags the 10 most load-bearing research and Python craft docs for Ember work.

### 3.5 First Slice Plan (proposed)

Seven sequential phases, each its own commit, total ~38 new files, target ≤2 500 LOC (excluding tests/configs/docs):

1. Rename + pyproject
2. Schemas
3. Brunnr (sqlite_vec) + Smiðja (local_files)
4. Strengr
5. Funi (Ollama)
6. Hjarta + Munnr
7. Acceptance + ship

Acceptance criterion: fresh operator on a Pi 5 (8 GB) with Ollama can `pip install ember-agent` → Hjarta wizard → ingest a directory → ask a question → get a grounded reply, *and* survive a network-pull mid-conversation with a clean `well: disconnected` banner.

### 3.6 Brunnr Backend Matrix (proposed)

- **`sqlite_vec` is the first-slice default and the toaster baseline.** Single file under `~/.ember/well/store.db`.
- **`pgvector` ships in Phase 8** and is the Gungnir-compatible backend for households with shared wells.
- **`qdrant`, `chroma`, `lancedb`** are later peers — each shipped as a separate adapter satisfying the same `BrunnrHandle` interface, never as a fork.

### 3.7 Funi Local Model Options (proposed)

- **Default ladder** by host RAM: `qwen2.5:0.5b` (Pi4-4GB), `qwen2.5:1.5b` / `llama3.2:1b` (Pi5-4GB), `phi3:mini` / `qwen2.5:3b` (Pi5-8GB, **default target**), `qwen2.5:7b` / `llama3.1:8b` (Pi5-16GB+).
- **First-slice ships Ollama adapter only.** Phi Silica (Windows AI Foundry) and Apple Foundation Models adapters are Phase 8.
- **Embedding model recommendation:** `nomic-embed-text` (768-dim) to match Gungnir bytewise — embedding dim must match exactly between Funi/Smiðja and Brunnr.

### 3.8 Gungnir Survey (live)

Live measurements taken 2026-05-21 against `knowledge` on Gungnir (PG 18.3, pgvector 0.8.1, pg_trgm 1.6):

- **95 documents**, **35 682 chunks**, **100% embedded** at **768-dim** via `nomic-embed-text`.
- Chunk text: min 4, **avg 1 684**, max 2 000 chars — calibration anchor for Ember's chunker default.
- **394 MB DB total**, 372 MB of which is `chunks` (most of it embeddings).
- Buffer hit 97.0% tables / 99.8% indexes — healthy.
- HNSW (`vector_cosine_ops`) on `chunks.embedding`; GIN on `chunks.tsv`; hybrid search via reciprocal rank fusion in `~/ai/ingest/ingest.py`.
- **Two parallel KG layers:** `skein_*` (embedding-derived, cheap, broad — 276 entities × 855 relations across the full corpus, with known false-friend artifacts like `(GPT-2)–defeated→(GPT-3)`) and `kg_*` (LLM-extracted per chunk, precise, expensive — 366 entities × 176 relations across only 202 of 35 682 chunks).
- The Skein/KG distinction is **load-bearing for future Ember work**: cheap-broad and expensive-precise are different layers, not different qualities of the same layer.

### 3.9 Smiðja Ingest Patterns (proposed)

Four patterns: **local files**, **URL fetch**, **shared well**, **Project Nomad** (deferred). Chunking and embedding defaults calibrated to Gungnir's measured shape. Resumable journal under `~/.ember/state/smidja_progress/<job_id>.json` lets a Pi-class operator leave overnight ingests running through power blips.

## 4. Consequences

### 4.1 What changes if this ADR is ratified

- The Ember-shaped architecture documents become the canonical architecture for the project.
- The inherited Runa architecture documents move to `docs/archive/runa-inherited/architecture/` (per the Vow of Open Knowledge, nothing is deleted).
- The next commit's scope is bounded: `src/runa/` → `src/ember/` rename + `pyproject.toml` rewrite. The Forge Worker begins Phase 2 (schemas) after that lands.
- Embedding model is locked to 768-dim default for Gungnir compatibility.

### 4.2 What does not change

- `PHILOSOPHY.md`, `RULES.AI.md`, `MYTHIC_ENGINEERING.md`, `LICENSE`, `NOTICE` — untouched.
- All inherited corpora — untouched in place.
- The repository name and the toaster framing — untouched.

### 4.3 Risks

- The Cartographer's recommendation to move three top-level architecture docs to the archive could be experienced as a loss of Runa context. Mitigation: the docs move to `docs/archive/runa-inherited/architecture/`, not into the void; they remain reachable, cited by `EMBER_FORK_DELTA.md`, and any operator reading the canonical path is forwarded by `docs/architecture/README.md`.
- The first-slice plan commits Ember to Ollama-only on the first wave. If a Pi-class operator without Ollama shows up early, they cannot use Ember. Mitigation: `deploy/pi/INSTALL.md` (Phase 7) ships clear Ollama install instructions; `llamacpp/` adapter is Phase 8.
- The Gungnir survey's two-KG-layer insight may tempt Ember into building its own KG layers prematurely. Mitigation: Phase 9+ for any KG work; the first slice is chunks + embeddings only.

## 5. Alternatives considered

| Alternative | Why not |
|---|---|
| Author Ember architecture by directly overwriting `ARCHITECTURE.md` / `DOMAIN_MAP.md` / `DATA_FLOW.md` | Violates the additive rule and `RULES.AI.md` "Never delete without asking". The EMBER_*.md prefix is the safe move that gives Volmarr explicit comparison + ratification authority. |
| Skip the architecture pass and start coding the first slice now | Violates `MYTHIC_ENGINEERING.md`'s core loop. Document before code. The Architect's first pass is named in the DEVLOG explicitly. |
| Start with pgvector against Gungnir as the first-slice Brunnr | Couples acceptance to a running Postgres instance. `sqlite_vec` first preserves the toaster story; pgvector is Phase 8. |
| Defer Gungnir survey to later | The survey is *what makes* the Brunnr/Smiðja defaults concrete instead of guessed. Doing it now means future Ember code is grounded in real numbers. |

## 6. Open follow-ups

- ADR 0007: pyproject + src-rename plan (to be added in the rename commit).
- ADR 0008: Brunnr `INTERFACE.md` finalization (Protocol vs ABC).
- ADR 0009: SQLite-vec vs SQLite-vss decision for the default Brunnr.
- Volmarr to ratify the Six True Names and the Three Realms naming with the Skald (item 3 from the DEVLOG that was *not* addressed in this pass).

## 7. Provenance

This decision was authored against the live state of the repository on 2026-05-21 and against a live read of the Gungnir database on the same day. Tool trail and counts are reproducible: rerun the queries in `GUNGNIR_WELL_REFERENCE.md` §4 to verify the numbers.

— Eirwyn Rúnblóm (Scribe), with Védis (Cartographer), Rúnhild (Architect), and Eldra (Forge Worker)

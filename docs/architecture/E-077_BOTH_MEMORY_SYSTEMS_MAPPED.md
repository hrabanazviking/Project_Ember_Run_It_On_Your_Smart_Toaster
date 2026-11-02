# E-077 — Both Memory Systems Mapped, in Depth

*Part V (Memory: Two Systems, One Verdict), opening slice.
This is E-012 executed in depth, as the roadmap orders:
storage shapes, retrieval, consumers, and test state for
both member memory systems — and, because E-012 proved it
stands in the same room, for the core's own incumbent
memory in the same depth. Method: every statement below
was drawn from the code in this tree at the slice's
starting HEAD (ee01b1e, E-076 banked), with file and
symbol named. Member elder documents were read as claims,
not authority. No store belonging to any system was
opened, migrated, or modified; every test ran against
its own fixtures. No member code was modified in this
slice.*

## 1. Plain-language summary

There are **three** memory systems in this house, not
two, and Part V's verdict (E-079) must judge all three:

1. **mempalace** (`mempalace/`, v3.3.5) — the *verbatim
   archive*. Whole projects and whole conversations are
   mined into a palace of wings, rooms, closets and
   drawers; things are found again by meaning
   (embeddings) and by words together. Upstream
   open-source, imported whole, heavy: its search brain
   is ChromaDB plus an ONNX embedding model.
2. **mimir-well** (`mimir-well/`, v2.10.4) — the
   *living memory*. One SQLite file of memories that
   carry importance and feeling, fade unless reinforced,
   can be superseded when the world changes, and are
   guarded, audited, and budgeted. The house's own line,
   stdlib-only at its core, companion-shaped.
3. **Brunnr** (`src/ember/well/`) — the *incumbent*.
   The Ember core's own well: documents and chunks with
   vector + full-text search, plus one episode row per
   remembered conversation turn, behind one protocol
   (`BrunnrHandle`) with two adapters (sqlite_vec,
   pgvector). It is the only one of the three the
   companion actually uses today.

**Neither member system has changed by one byte since
its import.** `git log` over both member directories
shows exactly one commit each — mempalace f7ef473 and
mimir-well 911eeba, both 2026-05-21 — and their tracked
sizes are byte-identical to the E-057 table as re-pinned
at E-076: mempalace **257 files / 59,049,715 B**,
mimir-well **58 files / 607,675 B** (this slice,
`git ls-files` + byte sum, the E-057 method). Everything
E-012 found about their insides therefore still stands;
what this slice adds is the depth E-012 pointed at —
exact schemas, exact retrieval maths, the *third*
consumer of mimir-well that E-012's grep shape missed
(bifrost's core, §6), Brunnr mapped to the same depth,
and fresh test state (§7).

**The Ember core still uses neither member.** Proven
again this slice by grep over `src/ember/**/*.py`: zero
imports of, or references to, mempalace or mimir-well;
the core's memory references are all to its own
`ember.well.brunnr` (§6). So E-078's comparison harness
must run **three** systems or it answers the wrong
question, exactly as E-012 §7 warned.

## 2. The three at a glance

| Fact | mempalace | mimir-well | Brunnr (core) |
|---|---|---|---|
| Home | `mempalace/` | `mimir-well/` | `src/ember/well/` |
| Version / licence | 3.3.5, MIT | 2.10.4, MIT | part of ember-agent 0.2.0, MIT |
| Provenance | Upstream OSS, milla-jovovich (pyproject) | House line, Eldrä Járnsdóttir (pyproject) | House core (Batch-era + campaign) |
| History here | ONE import commit f7ef473 | ONE import commit 911eeba | Real development (E-021/E-031/E-035/E-036/E-037/E-038 slices) |
| Tracked size | 257 files / 59,049,715 B | 58 files / 607,675 B | 26 files (well subtree; byte sum in E-057's core row) |
| Code mass (this slice, working tree excl. `__pycache__`) | package 25,318 lines across 49 modules in `mempalace/mempalace/` (largest: `mcp_server.py` 2,333, `cli.py` 1,548, `backends/chroma.py` 1,455, `repair.py` 1,441, `miner.py` 1,317) | `src/mimir_well/` 6,513 lines across 17 modules (largest: `core.py` 1,572, `eye/app.py` 949, `wyrd_graph.py` 716, `guard.py` 526) | 3,468 lines across 15 modules (largest: pgvector `adapter.py` 991, sqlite_vec `adapter.py` 653, `smidja/journal.py` 387) |
| Core deps | `chromadb>=1.5.4,<2`, `pyyaml` (+ ONNX runtime via ChromaDB's embedding function) | **None** (stdlib `sqlite3`); declared `flask>=3.0` serves only the Eye — and, unlike the root package's E-044 law, it is bounded below only (docket 108) | None at protocol level; adapters lazy-import their extras (`sqlite_vec`; `psycopg` + `pgvector`) |
| Default store | Palace *directory* `~/.mempalace/palace` | One SQLite *file* `~/.mimir_well/mimir_well.db` | One SQLite *file* `~/.ember/well/store.db` (sqlite_vec default) or a Postgres schema (pgvector) |
| Embedding | ONNX `all-MiniLM-L6-v2`, **384-dim** (`embedding.py`: the same model ChromaDB ships by default, reused) | **None — no vector code anywhere in the member** | External: Ollama `nomic-embed-text`, `embedding_dim` **768** default (`BrunnrConfig`), via Smíðja's embed client |
| Faces | CLI (`mempalace`), MCP server (30 `tool_*` functions, §5), Claude Code hooks | Library only (`RunaMemory`); Eye dashboard (Flask) | Protocol (`BrunnrHandle`, 12 methods, §4.3), core CLI (`well` commands), core MCP tools |
| Test files | 76 test-shaped (67 `tests/test_*.py` at E-002's strict count) | 28 `tests/test_*.py` | No member suite — covered by the root suite's Well tests |

## 3. Storage shapes, in depth

### 3.1 mempalace — a directory, three stores

- **The palace directory** (default `~/.mempalace/palace`,
  `config.py`: `DEFAULT_PALACE_PATH`; env
  `MEMPALACE_PALACE_PATH` / legacy `MEMPALACE_PATH`,
  then `~/.mempalace/config.json`, then defaults).
  Inside it, ChromaDB persists two collections —
  **drawers** (default name `mempalace_drawers`,
  `collection_name` in `config.py`) and **closets**
  (`palace.py:get_closets_collection`) — over
  `chroma.sqlite3` plus HNSW segment files. A drawer is
  one verbatim chunk of text with wing/room/source
  metadata; a closet is an AAAK compressed index line
  (`dialect.py`, 1,091 lines) pointing at drawers
  (`palace.py:build_closet_lines` /
  `upsert_closet_lines`, pointers of the shape
  `→drawer_id,…` parsed back by the searcher).
- **The knowledge graph is a separate SQLite file**
  (`knowledge_graph.py:KnowledgeGraph`): tables
  `entities` and `triples`, with temporal columns —
  `add_triple`, `invalidate`, `query_entity`,
  `query_relationship`, `timeline`, `stats`. It does
  not live inside ChromaDB.
- **Identity** is a plain file, `~/.mempalace/identity.txt`,
  read by Layer 0 of the wake-up stack (§4.1).
- **Repair is a storage cost of this shape:**
  `repair.py` (1,441 lines) and
  `backends/chroma.py` (1,455 lines) are largely
  HNSW-segment forensics — quarantine of stale or
  invalid segments, seq-id repair, capacity checks
  (`hnsw_capacity_status`). No other system in this
  map spends code like this on its own store's health.

### 3.2 mimir-well — one file, eleven tables + three FTS5

Schema authority: `schema.py` (`SCHEMA_VERSION = 9`),
applied by `core.py:RunaMemory._init_db`, with a
versioned migration runner beside it (`migrations/`).

- **Tables:** `_schema_meta`, `memories`,
  `saga_events`, `entities`, `relationships`,
  `conversations`, `knowledge`, `memory_access_log`,
  `wyrd_edges`, `memory_audit` — plus virtual tables
  `memories_fts`, `knowledge_fts`, `saga_events_fts`
  (FTS5).
- **The `memories` row** is the living shape: `id`,
  `timestamp`, `category`, `content`, `tags` (JSON),
  `importance` INTEGER 1–10, `emotional_valence` REAL
  −1.0…1.0, `valid_from` / `valid_until`,
  `superseded_by` → `memories(id)`, `is_current`,
  `memory_type` (default `episodic`), `user_id`
  (default `'runa'`). Every one of those columns is a
  behaviour in §4.2, not decoration.
- **Config:** `config.py:MimirConfig` — file
  `~/.mimir_well/mimir-well-config.json`, env overrides
  `MIMIR_DB_PATH` / `MIMIR_BACKUP_REPO`; defaults
  include `decay_half_life_days` 30,
  `consolidation_access_threshold` 3, WAL on,
  `synchronous` FULL. `db_path` resolves to
  `~/.mimir_well/mimir_well.db` when unset — the
  library's own default, one of docket 51's three
  claimants (§6).

### 3.3 Brunnr — one protocol, two on-disk shapes

Schema authorities: `brunnr/sqlite_vec/schema.sql` and
`brunnr/pgvector/schema.sql`, both version 1, both
mirroring the Gungnir reference shape so an existing
Gungnir store can serve as the Well.

- **sqlite_vec shape** (the default backend,
  `BrunnrConfig.backend = SQLITE_VEC`,
  `SqliteVecConfig.path = ~/.ember/well/store.db`):
  tables `schema_version`, `documents` (`source`,
  `title`, `content_type`, `hash` UNIQUE, `metadata`
  JSON, `ingested_at`), `chunks` (`document_id` FK,
  `chunk_index`, `text`, `char_start/end`), a vec0
  virtual table `chunk_vectors` (`embedding
  float[{embedding_dim}]`), an FTS5 virtual table
  `chunk_fts` kept in sync by three triggers, and
  `episodes` (one row per conversation turn:
  `operator_input`, `ember_reply`, `cited_chunk_ids`,
  `funi_model`, `well_disconnected`, timestamps).
- **pgvector shape:** the same logical tables in a
  Postgres schema (default `public`), with the
  embedding as a `vector({embedding_dim})` column on
  `chunks`, an HNSW index (`vector_cosine_ops`), a
  generated `tsvector` column with a GIN index, and
  the same `episodes` table. The adapter probes an
  existing schema and skips its DDL when the expected
  tables are already present (`adapter.py:_probe_schema`).
- **Ingest is a separate organ:** Smíðja
  (`well/smidja/`) — `chunker.py` (max 2000 / target
  1684 / min 200 chars, paragraph-preferred),
  `embed_client.py` (Ollama `/api/embed`,
  `nomic-embed-text`, batch 32), `journal.py` +
  `well/pending_journal.py` (the E-031 pending-episodes
  journal: turns the Well could not take are journaled
  and drained at startup, never lost).

## 4. Retrieval, in depth

### 4.1 mempalace — hybrid, closet-boosted, layered

- **Write path is mining, not single writes:**
  `miner.py` (projects), `convo_miner.py` +
  `convo_scanner.py` (conversations), `diary_ingest.py`,
  `project_scanner.py`, `sync.py`, and shell hooks
  around Claude Code compaction (`hooks_cli.py`).
  `palace.py:mine_palace_lock` serialises miners.
- **Search** (`searcher.py`): `search()` (CLI path)
  and `search_memories()` (MCP path) share one shape —
  the drawer vector query is the floor and always
  runs; closet hits add a rank-based boost by source
  file and can expand to neighbouring drawers
  (`_expand_with_neighbors`); results are re-ranked by
  `_hybrid_rank` — a convex combination, **vector
  weight 0.6 / BM25 weight 0.4**, vector similarity
  `max(0, 1 − distance)`, BM25 real Okapi with
  corpus-relative IDF, min-max normalised inside the
  candidate set. When ChromaDB is unavailable there is
  a **BM25-only fallback over SQLite**
  (`_bm25_only_via_sqlite`), and a candidate-union
  strategy can merge BM25-only candidates into the
  hybrid result.
- **Wake-up is layered** (`layers.py`): Layer 0
  identity (~100 tokens, from `identity.txt`), Layer 1
  essential story, Layer 2 on-demand wing/room
  retrieval, Layer 3 deep search; `MemoryStack.wake_up`
  / `recall` / `search` compose them.
- **The MCP face** (`mcp_server.py`, 2,333 lines) is
  exactly **30 `tool_*` functions** (counted this
  slice): status, wings/rooms/taxonomy, search,
  duplicate check, AAAK spec, graph traverse / tunnels
  (find, create, list, delete, follow, stats), drawer
  CRUD + sync, KG query / add / invalidate / timeline
  / stats, diary write / read, hook settings,
  memories-filed-away, reconnect.

### 4.2 mimir-well — words, structure, and time

- **The class** (`core.py:RunaMemory`, 1,572 lines)
  exposes, by its own method list (AST-counted this
  slice): `add_memory` / `get_memory` /
  `search_memories` / `update_memory` /
  `delete_memory`; saga events; entities and
  relationships; `save_conversation` /
  `get_conversation`; `add_knowledge` /
  `search_knowledge`; `fts_search`; the structured
  recalls `recall_by_importance` / `recall_recent` /
  `recall_by_mood`; the temporal family
  `store_with_validity` / `supersede` /
  `recall_current`; lifecycle `decay` /
  `consolidate` / `promote_to_knowledge` /
  `detect_contradictions`; custody `integrity_check`
  / `repair` / `backup_to` / `backup_with_rotation` /
  `restore_from` / `github_backup` /
  `export_to_json` / `rebuild_fts` / `health_check` /
  `get_stats`.
- **Retrieval is FTS5 + structure, never vectors:**
  a tree-wide grep finds no embedding or vector code
  anywhere in the member (E-012, re-proven this slice
  by the module inventory in §2 — no embedding module
  exists). A paraphrase sharing no words with a memory
  is invisible to it; a question about importance,
  recency, mood, or *what is true now* is native.
- **The living parts:** `decay.py` (Ebbinghaus decay
  with the 30-day default half-life, reinforcement,
  promotion confidence), `guard.py` (526 lines:
  MemoryGuard screens writes by source trust),
  `audit.py` (every mutation trailed in
  `memory_audit`), `budget.py` (483 lines:
  TokenBudgeter, per-channel token budgets),
  `context_engineer.py` (builds the context block),
  `wyrd_graph.py` (716 lines: strength-weighted edges
  over the *same* file's `wyrd_edges`).

### 4.3 Brunnr — the protocol is the retrieval contract

- **`BrunnrHandle`** (`brunnr/handle.py`, a
  `runtime_checkable` Protocol, frozen as core API v1
  at E-037) is exactly 12 methods: `add_document`,
  `add_chunks`, `add_episode`, `recent_episodes`,
  `vector_search`, `text_search`, `hybrid_search`,
  `get_document`, `get_chunk`, `has_document`,
  `count`, `close` — plus the module-level `open()`
  registry that dispatches on `BrunnrConfig.backend`
  and returns a typed `Disconnected` instead of
  raising when the Well cannot be opened.
- **Search modes:** vector (vec0 KNN / pgvector HNSW
  cosine), text (FTS5 / tsvector), and hybrid — the
  core's adapters fuse vector + text by reciprocal
  rank fusion with chunk-id tie-breaking (E-036's
  determinism pin: RRF ordered by `(−score, chunk_id)`).
- **What Brunnr does not have** (the verdict's raw
  material): no decay or lifecycle, no importance or
  valence, no validity/supersession, no guard or
  audit, no knowledge graph, no mining pipelines, no
  layered wake-up. Its memory *types* are exactly
  three: documents, chunks, episodes.

## 5. Overlap and uniqueness — the E-078 workload list

Shape overlap (no shared code, no shared format —
a grep of each system for either other's name returns
nothing in code, E-012 §3, re-proven this slice):

| Capability | mempalace | mimir-well | Brunnr |
|---|---|---|---|
| Store + get by id | drawers | `memories` | documents/chunks/episodes |
| Full-text search | BM25 leg + BM25-only fallback | FTS5 | FTS5 / tsvector |
| Semantic search | yes (384-dim ONNX, in-process) | **no** | yes (768-dim Ollama, external embedder) |
| Knowledge graph | temporal triples, own SQLite | entities/relationships + WyrdGraph, same file | **no** |
| Conversations held | mined convo archives + diary | `conversations` table | `episodes` (turn rows) |
| Layered context | Layers 0–3 | ContextEngineer + TokenBudgeter | conversation window (core, E-021) |
| Lifecycle (decay/consolidation) | **no** | **yes — its centre** | **no** |
| Truth over time | KG invalidate / as-of | validity + supersession + contradiction detection | **no** |
| Custody (guard/audit) | palace locks, repair forensics | guard + audit + backups | pending journal (turn custody only) |
| MCP face | its own server, 30 tools | **no** | core MCP serves Brunnr stats/search |

E-078's harness must therefore measure, per system:
verbatim recall, paraphrase recall (mempalace and
Brunnr only — mimir-well's absence is a measured
result, not a harness gap), FTS recall, importance /
mood / current-truth recall (mimir-well only),
episode recall (Brunnr only), latency, store growth,
and per-profile budget fit — the unique rows are the
point, not just the shared ones.

## 6. Consumers — who actually uses each, in code

Proven by grep over `*.py` in `src/`, `tests/`, and
every member, this slice:

- **Ember core (`src/ember/`): Brunnr only.** The
  chat loop (`spark/munnr/chat.py`) holds a
  `BrunnrHandle`, loads history via
  `recent_episodes`, grounds replies via
  `tools/search_well.py` (`hybrid_search` when an
  embedder is bound, else `text_search`); ingest
  (`spark/munnr/ingest.py`) runs Smíðja into Brunnr;
  `doctor` probes `count()`; Hjarta's wizard probes a
  round-trip; the MCP server serves Brunnr search and
  stats; Strengr's tether opens the Well via
  `brunnr.handle.open` with retry. **Zero** core
  references to mempalace or mimir-well.
- **mempalace consumers in-tree: none.** Its consumers
  are external by design (Claude Code hooks, MCP
  clients). In-tree mentions are docs only (the
  Yggdrasil design corpus, E-012 §5).
- **mimir-well consumers in-tree: three code
  consumers, two path shapes** (E-012 found two; the
  third is new evidence this slice):
  1. *Verdandi's heartbeat* (`heartbeat/checks/mimir.py`):
     opens `~/.mimir_well/mimir_well.db` — the
     library's own default — checks integrity, counts
     `memories`/`knowledge`/`relationships`, watches
     size (warn 100 MB / critical 500 MB).
  2. *bifrost's memory bridge*
     (`bifrost/src/bifrost/bridges/memory_bridge.py`):
     reads/writes `memories` + `memories_fts` directly
     by SQL at its own default
     `~/.hermes/memory/runa_memory.db`
     (`DEFAULT_MIMIR_DB`), with its own fallback
     dict-shim when the file is absent.
  3. *bifrost's core* (`bifrost/src/bifrost/core.py`):
     a second, independent SQL consumer in the same
     member — `_ensure_mimir` opens
     `config.mimir_db_path` (default
     `~/.hermes/memory/runa_memory.db`,
     `bifrost/src/bifrost/config.py`), searches the
     same tables, writes memories, and feeds the
     results into bifrost's weighted routing
     (`mimir_weight` 0.4). Bridge and core do not call
     each other for this; both speak raw SQL to the
     member's table shape.
  - And the member's own Eye (`eye/app.py`) defaults
    to that same Hermes path (`MIMIR_DB_PATH` env
    overrides) — so **docket 51 stands exactly as
    E-012 left it**: the library defaults to
    `~/.mimir_well/mimir_well.db`; the Eye, the
    bifrost bridge, and the bifrost core all default
    to `~/.hermes/memory/runa_memory.db`; Verdandi's
    check alone follows the library. Stores at the
    different defaults are mutually invisible.
- **Design-corpus consumers** (intent, not code) are
  as E-012 §5 recorded; Verdandi's E-072 memory-feed
  law is a *producer-side* law whose destination is
  Part V's — it names no store, and E-080 owns binding
  it to the chosen face.

## 7. Test state — fresh this slice

Method per system, VM profile, Python 3.12.3, pytest
9.1.1, TMPDIR on a short workspace path (the E-076
lesson: a deep TMPDIR breaks the hub mini-run on the
AF_UNIX socket cap), deps from the isolated target
dirs of the E-004/E-005 method. Raw logs in
`~/workspace/.verify-tmp/ember-e077/logs/` + `gate/`.

- **mimir-well — full suite re-run, identical to
  E-005/E-012: 350 passed, 6 failed** (10.18s, flask
  supplied, proxy cleaned). The 6 failures are
  docket item 10 exactly, the Eye-fixture family
  (`test_t9_s94_eye_app.py`: fixture sets `DB_PATH`;
  the app binds `MIMIR_DB_PATH` / its `~/.hermes`
  default at import) — re-proven, not healed; it
  stays open exactly as classified, with its owner
  now Part V's own hygiene line (docket 108's
  sibling). Two earlier attempts this slice starved
  past their timeouts under sibling-campaign
  contention (load 6–11) with apparent failures at
  `test_recall_quality.py`'s two hard wall-clock
  latency tests (<50 ms over 1,000 memories); when
  the load calmed, that file ran **21 passed in
  2.44s**, latency tests included — the apparent
  failures were the E-072/E-075 contention-timing
  class, proven, not defects.
- **mempalace — focal suite re-run; full suite NOT
  re-run this slice.** The five files that judge
  this map's subjects (`test_searcher.py`,
  `test_hybrid_search.py`, `test_knowledge_graph.py`,
  `test_layers.py`, `test_closets.py`): with the
  proxy env cleaned (E-005's method), **170 passed,
  0 failed** (105.20s). In the dirty-proxy shape the
  same files scored 134 passed / 20 failed / 16
  errors, and every failure and error carries
  E-005's proven signature — httpx `Invalid port:
  ':1]'` from the bracketed IPv6 in `no_proxy`,
  raised inside ChromaDB's client — environment,
  not code. The full suite (E-012: ~18 minutes in a
  calm window) was not re-run: the member is
  byte-identical to its import (§1), so E-012's
  corrected, file-verified counts stand as its
  state — **1712 passed, 14 failed, 1 skipped, 106
  deselected, 0 errors**, the residue docket 12's
  STALE hook family (×10) + `test_palace_locks`
  (×4, one flaky). E-078's harness owns the next
  full measurement, under docket 54's discipline.
- **Brunnr / core Well — focal re-run:** the root
  suite's Well files (`test_brunnr_handle.py`,
  `test_brunnr_sqlite_vec.py`,
  `test_episode_reader_e021.py`) plus this slice's
  conformance ran 25 tests: 24 passed, and the one
  failure was this slice's *own* conformance
  assertion (it looked for bifrost's path literal in
  `core.py`; the literal lives in
  `bifrost/config.py`, as §6 states) — fixed in
  scope, and the conformance file then ran
  **8 passed** standalone (1.71s). The gate runs
  below include all of them green.
- **Environment note:** from ~01:12 this tick the VM
  hit the E-075 write transient again — scattered
  writes and Python `tempfile` creation failed with
  EPERM/ENOENT for minutes at a time across `/tmp`
  and workspace directories while reads stayed fine,
  and `/tmp` carried 7,258 sibling-campaign entries.
  It cleared on its own; no work was lost (this doc
  and its conformance test were verified on disk via
  `git status` before banking). Recorded so a
  recurrence is recognised, as at E-075.

## 8. What the later slices inherit

- **E-078** (comparison harness): §5's workload list,
  three systems, and docket 54's discipline — pin
  TMPDIR (workspace overlay, never the 512 MB `/tmp`),
  disk headroom, and runner version, or the numbers
  move. Store-growth measurement starts from §3's
  shapes; per-profile budget fit reads E-057's table.
- **E-079** (verdict paper): the decision is
  three-way. Brunnr is the incumbent with the only
  live consumer (the companion itself); mempalace is
  the only verbatim/mining system and the heavy one;
  mimir-well is the only living memory and the
  toaster-shaped one. ORIGINS provenance is E-012 §1 /
  E-003: neither member has an ORIGINS row (docket 72,
  E-196's to extend).
- **E-080** (chosen shape): whichever face is chosen,
  docket 51's three-path disagreement must be settled
  by it (one canonical default, or an explicit
  documented divergence), and E-072's memory feed
  binds there.
- **E-085** (memory ↔ Verdandi): the live consumer
  relationship is Verdandi ↔ mimir-well's file (§6) —
  reconcile there first, plus docket 104's retraction
  question.
- **E-082** (lifecycle): only mimir-well has one
  (§4.2); if the verdict bounds or retires it, the
  lifecycle must be re-homed, not lost.

## Carried to the docket (new items, Part V)

(108) mimir-well's single declared dependency,
`flask>=3.0` (its pyproject, serving only the Eye), is
bounded below only — the E-044 bounded-both-ways law
the root package and (at E-076) Verdandi now follow
has never been applied to this member. Owner: Part V
member hygiene, at or before E-092's gate.
(109) bifrost carries **two** independent raw-SQL
consumers of mimir-well's table shape (bridge +
core, §6) that do not share a connection, a path
resolution, or a category mapping — any Part V change
to the `memories` shape or the canonical path must
reckon with both, plus the Eye and Verdandi's check:
four readers/writers of one shape, zero of them
through `RunaMemory` itself. Owner: E-080 (chosen
shape) with Part VIII (E-123–E-136) consulted.
(110) Brunnr's episodes carry no `conversation_id` /
persona tag at the adapter layer (E-035's honest
limit, re-read in §3.3's schema: the `episodes`
tables of both adapters have no such column) — the
core tags episodes above the adapter, so a store read
raw cannot be separated by conversation or persona.
Owner: E-080/E-083 (persona separation at the memory
face), where it was already pointed.

## Slice gate

Root suite, three shapes (logs in
`~/workspace/.verify-tmp/ember-e077/gate/`):

- **Run A** (whole suite, default env): **1 error,
  11 skipped**, exit 2 — identical to E-076; the
  error is docket 1 (the pgvector test module's
  psycopg import above its guards).
- **Run B** (default env, pgvector file excluded):
  **1312 passed, 7 failed, 25 skipped, 1 warning**.
  Six of the seven are the proven environment
  failures (identical FAILED list to E-076: CDE ×3,
  G ×2, J ×1 — docket 2/3's `sqlite_vec` coupling).
  The seventh, `test_load_truth_e075`'s live
  mini-run ("hub exited early rc=1"), is E-076's
  proven deep-TMPDIR socket-cap artifact: this
  run's TMPDIR path was deep, the test's isolated
  re-run under a short TMPDIR ran **8 passed**, and
  this slice touched no hub code. Count arithmetic:
  1305 (E-076) + 8 (new conformance) − 1 (that
  artifact) = 1312.
- **Run D** (whole suite, extras supplied, short
  TMPDIR): **1370 passed, 0 failed, 19 skipped,
  1 warning**, exit 0 — green (1362 + 8).

Combined Part V opening conformance is this slice's
`tests/unit/test_memory_map_e077.py`: **8 passed**.
No README touched.

*Filed by the E-077 slice, 2026-11-01. Next: E-078 —
the comparison harness: identical workloads through
all three systems (recall, latency, size, budget per
profile).*

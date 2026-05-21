# `ember.well.brunnr.sqlite_vec/`

**The toaster-baseline Brunnr.** One SQLite file at
`~/.ember/well/store.db`; the `sqlite-vec` extension provides the
vector index; FTS5 provides full-text search; hybrid search fuses
both via reciprocal rank fusion (RRF, k=60) — the same shape Gungnir's
ingest pipeline uses and the same shape the pgvector adapter inherits.

**Shipped:** Phase 3, slice 1 (version 0.1.0, 2026-05-21).
**Reads with:** `INTERFACE.md` for the operator-facing surface; `schema.sql` for the on-disk shape; `docs/adapters/BRUNNR_BACKEND_MATRIX.md` for how this backend sits alongside the others.

---

## What this adapter is for

The default Brunnr — the one the operator gets when they don't change
anything. Zero auxiliary processes, single file on disk, runs on a
Raspberry Pi 5 with 50 MB of resident memory. The Vow of Smallness in
storage form.

When the operator wants something bigger (Gungnir, a shared household
Well), they switch to the pgvector adapter via one config edit
(`brunnr.backend: pgvector` + a `pgvector:` block). The Spark realm's
code doesn't change — both backends honor the same
`BrunnrHandle` Protocol.

## What it owns

| Concern | Owner |
|---|---|
| The single SQLite database file at `BrunnrConfig.sqlite_vec.path` (default `~/.ember/well/store.db`) | `adapter.SqliteVecBrunnr.__init__` (creates parent dirs; opens connection; enables WAL when configured). |
| The schema (tables, FTS5 virtual table, vec0 virtual table, triggers, version marker) | `schema.sql` — loaded as a package resource; applied with `executescript` on open. |
| Vector search via the `sqlite-vec` extension's `vec0` virtual table | `vector_search()` — cosine distance, converted to a similarity-ish score `1 - distance`. |
| Full-text search via FTS5 | `text_search()` — operator input is sanitised via `_escape_fts5_query` (token-quote-OR pattern; defends against FTS5 reserved-word column-ref injection). |
| Hybrid search (RRF over both) | `hybrid_search()` — fuses the wider candidate pool from each into a final top-k. Same `_RRF_K = 60` as pgvector. |
| Episode persistence | `add_episode()` — used by Munnr at end-of-turn. |
| Statistics (file size, embedded chunks, last-ok timestamp) | `count()`. |
| Graceful close | `close()` — suppresses `sqlite3.Error` (already-closed is fine). |

## What it does NOT own

- **Embedding generation.** That's Smiðja's job (`OllamaEmbedClient`).
  The adapter accepts vectors and stores them; it doesn't compute them.
- **Network transport.** None — this backend is local-only by
  construction.
- **Retry on transient failure.** Strengr's job (Thread realm) when
  the operator wraps the Brunnr in a Strengr handle. The adapter itself
  raises `BrunnrError` (or returns `Disconnected` on `open()`) and lets
  the caller decide.
- **Chunking.** That's Smiðja's chunker.
- **Tool-side concerns.** `search_well` (tool) calls *into* this
  adapter's `hybrid_search`; the adapter doesn't know it's being called
  by a tool vs by chat retrieval.

## On-disk shape

The schema is parameterised by `BrunnrConfig.embedding_dim` at apply
time. Defaults to 768 (nomic-embed-text's dim).

```
documents     (id, source, title, content_type, hash UNIQUE, metadata, ingested_at)
chunks        (id, document_id FK, chunk_index, text, char_start, char_end)
              + UNIQUE(document_id, chunk_index)
chunk_vectors VIRTUAL vec0(chunk_id PRIMARY KEY, embedding float[{embedding_dim}])
chunk_fts     VIRTUAL fts5(text) + triggers ai/ad/au to sync from chunks
episodes      (id, operator_input, ember_reply, cited_chunk_ids, funi_model,
               well_disconnected, started_at, completed_at)
schema_version (version PRIMARY KEY, applied_at)
```

Rows in `chunk_vectors` map 1:1 to rows in `chunks`. The FTS5 triggers
(`chunks_ai_fts`, `chunks_ad_fts`, `chunks_au_fts`) keep `chunk_fts` in
sync automatically; tool authors and Smiðja code never touch
`chunk_fts` directly.

## Failure semantics

- **`open()` never raises a connection error.** Returns `Disconnected`
  on: missing or malformed config, parent-dir creation failure, sqlite-
  vec extension load failure, schema-apply failure.
- **`add_chunks` is transactional.** Any per-chunk failure
  (dimension mismatch, SQL error) rolls back the whole batch and
  raises `BrunnrError`. Smiðja's caller marks the affected chunks
  failed in the journal and continues.
- **`add_document` is idempotent on `hash`.** Re-ingesting the same
  content returns the original document id; the row is not duplicated.
- **Read paths raise `BrunnrError` on missing rows** (`get_document` /
  `get_chunk`). Search APIs return empty results, never raise.
- **FTS5 reserved-word safety.** `text_search`'s sanitiser quotes
  every operator token and joins with `OR`. This is the regression
  test for the Phase-6 bug where `run:` in a probe was parsed as a
  column reference and crashed FTS5.

## Phase / version notes

- Phase 3 (slice 1, 0.1.0): full schema + writes + reads + RRF
  hybrid search shipped.
- Phase 6 (slice 1, 0.1.0): FTS5 sanitiser fix in `text_search`
  (commit `954038d`).
- Slice 2: no changes — sqlite_vec adapter is feature-complete for
  slice 2 acceptance. pgvector adapter shipped as a peer for shared
  Wells.

## Limitations

- **Single-process.** SQLite + WAL handles multi-reader, but two
  writer processes will conflict. Slice 2 ships single-operator
  single-process; multi-operator is a slice-3+ concern per ADR 0013
  §3.
- **No backup-while-running.** `cp store.db` while open is unsafe.
  Operators should `ember well close` first or use SQLite's
  `.backup` command. Backup tooling is a slice-3+ operational
  deferral.
- **No export/import.** Same deferral.
- **`embedding_dim` is fixed at first apply.** Changing it
  post-apply requires re-ingesting. The pgvector adapter has the
  same constraint and the same failure-loud check.

## Related

- `schema.sql` — the parameterised DDL.
- `INTERFACE.md` — operator-facing surface contract.
- `tests/unit/test_brunnr_sqlite_vec.py` + `test_brunnr_fts5_safety.py`
  — 9 + 11 = 20 unit tests.
- `tests/integration/test_ingest_then_query.py` — round-trip test
  through a real `sqlite_vec` install.
- `docs/adapters/BRUNNR_BACKEND_MATRIX.md` — where this backend sits
  on the matrix.
- The peer adapter: `src/ember/well/brunnr/pgvector/` (shipped 0.1.9).

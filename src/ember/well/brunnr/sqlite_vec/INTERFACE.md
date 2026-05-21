# INTERFACE — `ember.well.brunnr.sqlite_vec`

## Module purpose

The first-slice default Brunnr backend. Single file under
`~/.ember/well/store.db`, zero auxiliary processes, runs on a Pi.

## Public entry points (shipped Phase 3)

- `ember.well.brunnr.sqlite_vec.SqliteVecBrunnr` — concrete adapter class.
- `ember.well.brunnr.sqlite_vec.open(config) -> SqliteVecBrunnr | Disconnected` —
  the entry that the top-level Brunnr registry dispatches to.

## On-disk shape

Tables and indexes are defined in `schema.sql` (applied via
`executescript` on `open()`):

- `documents (id, source, title, content_type, hash UNIQUE, metadata, ingested_at)`
- `chunks (id, document_id FK, chunk_index, text, char_start, char_end)` + UNIQUE(document_id, chunk_index)
- `chunk_vectors` — sqlite-vec `vec0` virtual table, `embedding float[{embedding_dim}]`
- `chunk_fts` — FTS5 virtual table over `chunks.text`, kept in sync by triggers
- `episodes` — one row per remembered turn
- `schema_version` — single-row version marker (currently 1)

The `{embedding_dim}` placeholder is substituted from
`BrunnrConfig.embedding_dim` at `open()` time, so the vector index is
fixed at first apply. **Changing `embedding_dim` after first apply is
not supported in Phase 3** — operators who change embedding model must
re-ingest.

## Search semantics

- `vector_search` — `vec0` cosine, distance converted to `score = 1 - d`.
- `text_search` — FTS5 `MATCH`, FTS5 rank (negative; we negate so higher is better).
- `hybrid_search` — reciprocal rank fusion of the two with `k=60`
  dampener; matches the Gungnir pattern (see
  `docs/adapters/GUNGNIR_WELL_REFERENCE.md` §6).

## Failure semantics

- `open()` returns `Disconnected` rather than raising on: missing config,
  parent-dir creation failure, sqlite-vec load failure, schema apply
  failure.
- `add_chunks` rolls back the in-progress batch on any sqlite error and
  raises `BrunnrError`. Smiðja's caller is expected to handle this by
  marking the affected chunks failed in its journal and continuing.
- All other read paths raise `BrunnrError` on missing rows; this is the
  expected programming-error case for explicit `get_*` lookups.

## Limitations (Phase 3)

- Single-process. SQLite + WAL handles multi-reader, but two writer
  processes will conflict — not a concern for first-slice single-Ember.
- No backup-while-running. `cp store.db` while open is unsafe; operators
  should `ember well close` first or use SQLite's `.backup` (Phase 9+).
- No export/import (deferred to Phase 9).

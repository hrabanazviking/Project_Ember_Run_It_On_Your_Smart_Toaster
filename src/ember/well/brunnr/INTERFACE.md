# INTERFACE — `ember.well.brunnr`

## Module purpose

The storage adapter layer. Reads embeddings and chunks out, writes
documents/chunks/episodes in. One adapter per supported backend.

## Public entry points (shipped Phase 3, 2026-05-21)

- `ember.well.brunnr.handle.BrunnrHandle` — the `@runtime_checkable`
  Protocol every adapter satisfies.
- `ember.well.brunnr.handle.open(config) -> BrunnrHandle | Disconnected` —
  the registry entry point Strengr calls. Dispatches on `config.backend`.
  Returns `Disconnected` (typed value) rather than raising on failure.
- `ember.well.brunnr.sqlite_vec.SqliteVecBrunnr` — first-slice default
  backend, with FTS5 + sqlite-vec vec0 + RRF hybrid search.
- `ember.well.brunnr.sqlite_vec.open(config)` — adapter-level open,
  same return contract.
- `ember.well.brunnr.pgvector.PgVectorBrunnr` — Gungnir-compatible
  backend (Phase 8).

## Minimum surface — the canonical table

(Authoritative spec in `docs/architecture/DOMAIN_MAP.md` §2.1.)

| Operation | Inputs | Returns | Notes |
|---|---|---|---|
| `open(config)` | `BrunnrConfig` | `BrunnrHandle` or `Disconnected` | One handle per process; thread-safe within the adapter. |
| `add_document(doc)` | `Document` | `document_id: int` | Idempotent on content hash. |
| `add_chunks(chunks)` | `list[Chunk]` | `list[chunk_id: int]` | Bulk insert, committed at end. |
| `add_episode(ep)` | `Episode` | `episode_id: int` | Persists a conversation turn. |
| `vector_search(qvec, k, filter=None)` | `list[float]`, `int`, optional | `list[RetrievalHit]` | Cosine; HNSW-indexed when the backend supports it. |
| `text_search(query, k, filter=None)` | `str`, `int`, optional | `list[RetrievalHit]` | FTS. |
| `hybrid_search(qvec, query, k)` | both | `list[RetrievalHit]` | Reciprocal rank fusion. |
| `get_document(id)` | `int` | `Document` | |
| `get_chunk(id)` | `int` | `Chunk` | |
| `count()` | — | `BrunnrStats` | For `ember well status`. |

## Inputs

Configuration (`BrunnrConfig`) and chunked content.

## Outputs

Typed handles, query results, statistics. Or `Disconnected`.

## Side effects

Reads/writes the backend store (SQLite file, Postgres rows, etc.).
**Embedding generation is NOT a Brunnr responsibility** — that lives in
`ember.well.smidja`.

## Allowed imports

`ember.schemas` and the specific backend library for each adapter
(`sqlite3`, `sqlite_vec`, `psycopg`, `qdrant_client`, etc.) only inside
the matching adapter subpackage. **No leak of backend types upward.**

## Invariants

- Every backend satisfies the full minimum surface or returns a typed
  `NotSupportedHere(operation)` value — never a silent partial.
- A backend failure returns `Disconnected`; it does not raise across the
  module boundary.
- Embedding dim is fixed at handle-open time; mismatched dims refuse.

## Forbidden responsibilities

- Embedding generation (Smiðja's job).
- Network transport selection (Strengr's job).
- Deciding what to ask the Well (Spark's job).

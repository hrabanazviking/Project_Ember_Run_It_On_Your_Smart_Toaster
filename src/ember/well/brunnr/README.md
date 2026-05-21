# `ember.well.brunnr/` — Brunnr

**The pluggable storage adapter layer.** Brunnr is the Well's *substrate
abstraction* — one Protocol, one registry, many backends. Every
backend implements `BrunnrHandle` (`handle.py`); choosing a backend is
a configuration decision, not a code change.

**Shipped:** Phase 3, slice 1 (`sqlite_vec` adapter; the Protocol +
registry). Extended Phase 12-13, slice 2 (`pgvector` adapter).
**Reads with:** `INTERFACE.md` for the public surface; `handle.py` for the Protocol; `docs/architecture/DOMAIN_MAP.md` §2 (especially §2.1 the minimum-surface table); `docs/adapters/BRUNNR_BACKEND_MATRIX.md` for the backend menu.

---

## What this subpackage owns

- **The Protocol** (`handle.py`) — `BrunnrHandle` declares the
  fourteen methods every backend implements: `add_document`,
  `add_chunks`, `add_episode`, `vector_search`, `text_search`,
  `hybrid_search`, `get_document`, `get_chunk`, `has_document`,
  `count`, `close`, plus class attributes `backend_kind: str` and
  `embedding_dim: int`.
- **The registry** (`handle.py open()`) — dispatches on
  `BrunnrBackend` enum value to the matching adapter's `open()`. Lazy
  import per ADR 0007 §2.1.
- **The graceful-disconnect contract** — every backend's `open()`
  returns `BrunnrHandle | Disconnected`; never raises.
- **The concrete backends** — currently `sqlite_vec/` (slice-1
  default) and `pgvector/` (slice-2 shared-Well adapter).

## What this subpackage does NOT own

- **Embedding generation.** That's Smiðja's job.
- **Network transport.** Strengr wraps `open()` with retry + typed
  disconnect classification.
- **Chunking.** Smiðja's chunker.
- **Tool-side concerns.** `ember.tools.search_well` calls
  `hybrid_search`; the adapter doesn't know it's being called by a
  tool vs by chat retrieval.

## The `BrunnrHandle` Protocol — the minimum surface

```python
@runtime_checkable
class BrunnrHandle(Protocol):
    backend_kind: str
    embedding_dim: int

    def add_document(self, doc: Document) -> int: ...
    def add_chunks(self, chunks: Iterable[Chunk]) -> list[int]: ...
    def add_episode(self, episode: Episode) -> int: ...
    def vector_search(self, qvec: Sequence[float], k: int,
                      filter: object | None = None) -> list[RetrievalHit]: ...
    def text_search(self, query: str, k: int,
                    filter: object | None = None) -> list[RetrievalHit]: ...
    def hybrid_search(self, qvec: Sequence[float], query: str,
                      k: int) -> list[RetrievalHit]: ...
    def get_document(self, document_id: int) -> Document: ...
    def get_chunk(self, chunk_id: int) -> Chunk: ...
    def has_document(self, content_hash: str) -> int | None: ...
    def count(self) -> BrunnrStats: ...
    def close(self) -> None: ...
```

This is **the boundary** — the Spark realm imports `BrunnrHandle` from
this file; it never imports any concrete adapter.

## The two shipped backends

| Backend | Status | Use case | Owns |
|---|---|---|---|
| `sqlite_vec/` | **Shipped** Phase 3 (slice 1) | Single-operator Pi-class default. One file, zero auxiliary processes. | SQLite + sqlite-vec + FTS5 + RRF. |
| `pgvector/` | **Shipped** Phase 13 (slice 2, 0.1.9) | Shared / household Wells; Gungnir-compatible. | Postgres + pgvector + tsvector + RRF. Connection-per-handle, no pool. Eight typed disconnect reasons. Read-only mode for shared Wells. |

Both backends honor the **same** RRF constant (`k=60`), the same
score conventions (`vector: score = 1 - cosine_distance`;
`text: score = ts_rank` for pgvector or `score = -fts5_rank` for
sqlite_vec; `hybrid: score = Σ 1/(60+rank)`), and the same
embedding-dim-locked-at-first-apply semantics.

## Backends NOT yet shipped (deferred per ADR 0013 §3)

| Backend | Status | Why deferred |
|---|---|---|
| `qdrant/` | Not started | No operator demand yet; each is a `BrunnrHandle` implementation that follows the pgvector / sqlite_vec template. |
| `chroma/` | Not started | Same. |
| `lancedb/` | Not started | Same. |

Each of these is a Phase-12-shaped commit when an operator wants it.

## How a backend is selected

```yaml
# ~/.ember/config/ember.yaml
brunnr:
  backend: sqlite_vec       # or: pgvector
  embedding_dim: 768
  sqlite_vec:
    path: "~/.ember/well/store.db"
  pgvector:
    url: "postgresql://volmarr@gungnir/knowledge"
    secret_ref: "~/.ember/secrets/well.password"
    read_only: true
```

`handle.open(config)` reads `config.backend`, lazy-imports the
matching adapter, and dispatches. The Spark realm receives the result
through Strengr; either a live handle or a typed `Disconnected`.

## Layout

```
src/ember/well/brunnr/
├── README.md
├── INTERFACE.md
├── __init__.py
├── handle.py            # the Protocol + registry
├── sqlite_vec/
│   ├── README.md
│   ├── INTERFACE.md
│   ├── adapter.py       # SqliteVecBrunnr
│   └── schema.sql       # parameterised DDL
└── pgvector/
    ├── README.md
    ├── INTERFACE.md
    ├── adapter.py       # PgVectorBrunnr
    ├── schema.sql       # parameterised DDL
    └── secrets.py       # env→keyring→file→typed-failure resolver
```

## Conventions (per ADR 0007 §2.3 + ADR 0010)

- **`backend_kind` is a class attribute, not an instance attribute.**
  So `BrunnrHandle.backend_kind == "sqlite_vec"` works without
  constructing an instance.
- **`embedding_dim` is fixed at handle-open time.** Changing it
  post-apply requires re-ingesting. Both shipped adapters fail-loud
  on mismatch.
- **FTS5 / tsvector input sanitisation at adapter boundary** (ADR
  0007 §2.9). sqlite_vec's `_escape_fts5_query` and pgvector's
  `plainto_tsquery` both defend against operator-string injection.
- **Idempotent `add_document` on hash.** Re-ingesting same content
  returns existing document id; no duplicate row.
- **Transactional `add_chunks`.** Per-chunk failure rolls back the
  whole batch; the caller (Smiðja) marks chunks failed in the journal.

## Slice-2 changes

| Phase | What landed |
|---|---|
| 12 | New `pgvector/` subpackage; the existing `BrunnrHandle` Protocol held without modification (the Protocol was designed in Phase 3 to be backend-agnostic; adding the second adapter validated it). |
| 13 | Live-fire integration: `tests/integration/test_pgvector_real_backend.py` — 10 container tests + 4 Gungnir read-only tests. Two real adapter bugs caught and fixed (`register_vector` before `CREATE EXTENSION`; `{{}}` schema escape). |

## Related

- `INTERFACE.md` — public surface.
- `handle.py` — the Protocol source.
- `docs/architecture/DOMAIN_MAP.md` §2 — full ownership table.
- `docs/adapters/BRUNNR_BACKEND_MATRIX.md` — backend menu.
- `docs/decisions/0010-pgvector-brunnr.md` — slice-2 adapter design.
- `sqlite_vec/README.md` + `pgvector/README.md` — per-backend deep dives.

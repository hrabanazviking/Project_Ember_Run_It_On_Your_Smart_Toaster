# `ember.well/` — the Well realm

**Where Ember's memory lives and where her knowledge is forged.**
Possibly local, possibly remote, possibly both at once. The Well is
the *substrate of grounding* — without it, Ember can still chat
(ungrounded mode + the disconnect banner), but with it Ember can
*tell the truth* about what's in the operator's documents.

**Shipped:** Phase 3, slice 1 (version 0.1.0 — `sqlite_vec` Brunnr +
`local_files` Smiðja). Extended Phase 12-13, slice 2 (`pgvector`
Brunnr).
**Reads with:** `docs/architecture/ARCHITECTURE.md` §3.3; `docs/architecture/DOMAIN_MAP.md` §2-3; `docs/adapters/BRUNNR_BACKEND_MATRIX.md`; `docs/adapters/SMIDJA_INGEST_PATTERNS.md`; `docs/adapters/GUNGNIR_WELL_REFERENCE.md`.

---

## What this realm owns

Two True Names, each in its own subpackage:

| Subpackage | True Name | Role |
|---|---|---|
| `brunnr/` | **Brunnr** ("well, spring") | The storage layer. One subpackage per supported backend; every backend honors the same `BrunnrHandle` Protocol. Read paths (vector / text / hybrid search) + write paths (document / chunk / episode persistence). |
| `smidja/` | **Smiðja** ("forge") | The ingest forge. Takes a content source, chunks it, calls the embedding endpoint, deposits chunks into Brunnr. Resumable journal so overnight Pi ingests survive power blips. |

## What this realm does NOT own

- **Network transport.** That's Strengr (Thread realm). Strengr opens
  a Brunnr handle with retry + typed-disconnect semantics; the
  Brunnr adapter itself only knows about its own protocol.
- **Tool access policy.** The Well is just a Well — the tool that
  *queries* it (`ember.tools.search_well`) lives in `ember.tools/` and
  binds to a live `BrunnrHandle` at chat-loop startup. The Well
  doesn't know it's being queried by a tool vs by chat retrieval.
- **What to retrieve.** Munnr/Spark decides.

## How the two subpackages relate

Smiðja writes; Brunnr stores and reads.

```
Operator types `ember well ingest <dir>`
   ↓
[Smiðja]
   walk directory → for each file:
     chunk(text) → list[Chunk]            # ChunkerConfig — Gungnir-aligned defaults
     embed(text per chunk) → vectors      # OllamaEmbedClient → /api/embed
     [Brunnr] add_document(doc) → doc_id
     [Brunnr] add_chunks(chunks)          # transactional batch
     journal: mark chunk done
   ↓
IngestSummary returned to Munnr → render
```

Conversation retrieval is the symmetric inverse:

```
Munnr → [Smiðja embed_client] embed(operator_text) → qvec
       → [Brunnr] hybrid_search(qvec, text, k=5) → list[RetrievalHit]
```

Smiðja's embed_client is reused for both ingest and chat retrieval —
single source of embedding truth, dim-aligned per `BrunnrConfig.embedding_dim`.

## What's in each subpackage

### `brunnr/` (Phase 3 + Phase 12-13)

- `handle.py` — the `BrunnrHandle` Protocol + `open(config)` registry
  dispatch.
- `sqlite_vec/` — the slice-1 default. One file at `~/.ember/well/store.db`;
  `sqlite-vec`'s `vec0` virtual table for vectors; FTS5 + triggers
  for text; RRF hybrid search.
- `pgvector/` — the slice-2 shared-Well adapter (Phase 12-13, ADR 0010).
  Postgres + pgvector + tsvector; Gungnir-compatible schema; read-only
  mode for shared Wells; eight-reason `DisconnectReason` classification.

### `smidja/` (Phase 3)

- `local_files.py` — directory walker; defaults to `**/*.md`, `**/*.txt`.
- `chunker.py` — Gungnir-aligned chunker (max 2000 chars, target 1684,
  min 200, paragraph-boundary-preferring).
- `embed_client.py` — `OllamaEmbedClient` POST to `/api/embed`. Stdlib
  urllib only; no httpx.
- `journal.py` — resumable progress journal at
  `~/.ember/state/smidja_progress/<job_id>.json`. Atomic write per
  chunk-batch; survives crashes.
- `pipeline.py` — orchestrator: walk → chunk → embed → deposit;
  returns `IngestSummary`.

## How a backend is selected

`config.brunnr.backend: BrunnrBackend` enum value (default `SQLITE_VEC`).
The registry in `brunnr/handle.py` lazy-imports the matching adapter
and calls its `open()`. Lazy import per ADR 0007 §2.1 — only the
chosen backend's library is loaded.

```python
# config.brunnr.backend = BrunnrBackend.PGVECTOR
brunnr_handle.open(config.brunnr)
   ↓
   from ember.well.brunnr.pgvector import open as pgvector_open
   return pgvector_open(config)
```

## Layout

```
src/ember/well/
├── README.md
├── __init__.py
├── brunnr/
│   ├── README.md
│   ├── INTERFACE.md
│   ├── handle.py            # Protocol + registry
│   ├── sqlite_vec/          # slice-1 default
│   │   ├── README.md
│   │   ├── INTERFACE.md
│   │   ├── adapter.py
│   │   └── schema.sql
│   └── pgvector/            # slice-2 shared-Well adapter
│       ├── README.md
│       ├── INTERFACE.md
│       ├── adapter.py
│       ├── schema.sql
│       └── secrets.py
└── smidja/
    ├── README.md
    ├── INTERFACE.md
    ├── chunker.py
    ├── embed_client.py
    ├── journal.py
    ├── local_files.py
    └── pipeline.py
```

## Slice-2 changes

| Phase | What landed |
|---|---|
| 12 | New `brunnr/pgvector/` subpackage (no version bump). |
| 13 | Live-fire pgvector against Gungnir + podman container; bump to 0.1.9 "pgvector live". Two real adapter bugs caught and fixed by live-fire. |

Smiðja was untouched in slice 2 — the slice-1 implementation already
worked against both backends because both honor the same
`BrunnrHandle` Protocol.

## Slice-2 acceptance criterion (per ADR 0013 §1)

An operator with Gungnir on their tailnet can:

1. `pip install ember-agent[pgvector]`
2. Add four lines to `~/.ember/config/ember.yaml`:
   ```yaml
   brunnr:
     backend: pgvector
     embedding_dim: 768
     pgvector:
       url: "postgresql://volmarr@gungnir/knowledge"
       secret_ref: "~/.ember/secrets/well.password"
       read_only: true
   ```
3. Run `ember chat` and get grounded answers against the live 35k-chunk
   corpus, with `read_only: true` mechanically protecting Gungnir from
   any write.

**Verified end-to-end** in Phase-13 live-fire and the Phase-17
acceptance test.

## Related

- `docs/architecture/ARCHITECTURE.md` §3.3 — Well realm definition.
- `docs/architecture/DOMAIN_MAP.md` §2-3 — ownership.
- `docs/adapters/BRUNNR_BACKEND_MATRIX.md` — backend menu.
- `docs/adapters/SMIDJA_INGEST_PATTERNS.md` — ingest patterns.
- `docs/adapters/GUNGNIR_WELL_REFERENCE.md` — canonical operator Well.
- `docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md` — slice-2 operator guide.
- `docs/decisions/0010-pgvector-brunnr.md` — slice-2 adapter design.

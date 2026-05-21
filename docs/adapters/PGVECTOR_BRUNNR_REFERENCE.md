# PGVECTOR_BRUNNR_REFERENCE — The pgvector Brunnr in practice

**Voice:** Cartographer (Védis Eikleið), with Forge Worker (Eldra Járnsdóttir)
**Status:** Reference. Adapter ratified by ADR 0010, **shipped 2026-05-21 (Phase 13)** at 0.1.9.
**Last touched:** 2026-05-21
**Reads with:** `docs/decisions/0010-pgvector-brunnr.md`, `docs/adapters/GUNGNIR_WELL_REFERENCE.md`, `docs/adapters/BRUNNR_BACKEND_MATRIX.md`, `src/ember/well/brunnr/pgvector/INTERFACE.md`.

---

## 1. Why this document exists

`GUNGNIR_WELL_REFERENCE.md` describes the canonical Well — *what's on the other end of the tether.* This file is its operator-side mirror: *how Ember plugs in.* The two read together when you're setting up a new tethered Ember.

If you have:

- Gungnir (or any Postgres + pgvector instance) on your tailnet, and
- want Ember to read it (and optionally write to it),

…then everything you need is here. The slice-1 `sqlite_vec` Well still works exactly as before — switching is a config edit, never a code edit.

---

## 2. Install

The pgvector Brunnr lives behind a pip extra so the default install stays zero-dependency:

```bash
pip install ember-agent[pgvector]
```

That pulls `psycopg[binary] >= 3.2` and `pgvector >= 0.3`. The first time Ember opens a writable pgvector Well it runs `CREATE EXTENSION IF NOT EXISTS vector` automatically — operators with a fresh database get the extension created on first open. On a read-only Well (your Gungnir; someone else's database) the extension must already be present.

---

## 3. Config — the minimum

In your `~/.ember/config/ember.yaml`:

```yaml
brunnr:
  backend: pgvector
  embedding_dim: 768
  pgvector:
    url: "postgresql://volmarr@gungnir/knowledge"
    secret_ref: "~/.ember/secrets/well.password"   # mode 0o600 required
```

The `url` may carry any shape `psycopg` accepts (`host`, `host:port`, full DSN, query parameters). The `secret_ref` path is *resolved at open() time*, not at config-load time — operators can move the secret file independent of restarts.

The `embedding_dim` must match the actual `chunks.embedding` dimension. Ember verifies this on open and refuses with `Disconnected(BACKEND_REPORTED_UNAVAILABLE, "chunks.embedding has dim X, config.embedding_dim is Y")` if they drift. There is **no auto-migration**; either re-ingest at the new dim or fix the config.

---

## 4. Config — every knob

```yaml
brunnr:
  backend: pgvector
  embedding_dim: 768
  pgvector:
    # Required
    url:        "postgresql://volmarr@gungnir/knowledge"
    secret_ref: "~/.ember/secrets/well.password"

    # Secret resolution (ADR 0010 §2.5) — first hit wins
    secret_env:       "EMBER_WELL_PASSWORD"   # env var checked first
    use_keyring:      true                    # set false to skip step 2
    keyring_service:  "ember-well"
    username:         null                    # null → parsed from URL

    # Connection
    connect_timeout_s: 10.0

    # Vector index + metric (ADR 0010 §2.4) — defaults match Gungnir
    vector_index:  hnsw
    vector_metric: cosine

    # Schema selection — Gungnir uses public; Ember-managed PGs may use ember
    schema: public

    # Read-mostly mode (ADR 0010 §4)
    # Set true when pointing at a Gungnir you didn't bootstrap; refuses
    # add_document / add_chunks / add_episode with a typed BrunnrError.
    read_only: false
```

---

## 5. The schema Ember will see (or apply)

If the configured schema already holds Gungnir-shape tables, Ember uses them as-is. Otherwise the DDL in `src/ember/well/brunnr/pgvector/schema.sql` is applied:

```sql
documents (
  id          bigserial PRIMARY KEY,
  source      text NOT NULL,
  title       text,
  content_type text,
  hash        text UNIQUE,
  metadata    jsonb NOT NULL DEFAULT '{}',
  ingested_at timestamptz NOT NULL DEFAULT now()
)

chunks (
  id          bigserial PRIMARY KEY,
  document_id bigint NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index integer NOT NULL,
  text        text NOT NULL,
  embedding   vector(<embedding_dim>),
  tsv         tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED,
  char_start  integer,
  char_end    integer,
  UNIQUE (document_id, chunk_index)
)
-- + chunks_embedding_hnsw (HNSW on embedding vector_cosine_ops)
-- + chunks_tsv_gin        (GIN on tsv)

episodes (
  id                bigserial PRIMARY KEY,
  operator_input    text NOT NULL,
  ember_reply       text NOT NULL,
  cited_chunk_ids   jsonb NOT NULL DEFAULT '[]',
  funi_model        text NOT NULL DEFAULT '',
  well_disconnected boolean NOT NULL DEFAULT false,
  started_at        timestamptz,
  completed_at      timestamptz
)
```

This is byte-for-byte the Gungnir reference shape from `GUNGNIR_WELL_REFERENCE.md` §3, minus the Skein/KG layers which Ember doesn't manage.

**Episodes is Ember-only.** Gungnir doesn't have it. When Ember probes onto an existing Gungnir, the `documents`/`chunks` tables are reused untouched; only `episodes` is created (and only when `read_only=false`).

---

## 6. Search semantics

Three search paths, all on the `BrunnrHandle` Protocol, so Spark-side code never branches on backend:

| Method | SQL | Score convention |
|---|---|---|
| `vector_search` | `ORDER BY embedding <=> $1::vector LIMIT $2` (cosine distance) | `score = 1 - distance` (higher = more similar) |
| `text_search` | `WHERE tsv @@ plainto_tsquery('english', $1) ORDER BY ts_rank(...) DESC` | `score = ts_rank` (higher = more relevant) |
| `hybrid_search` | RRF over both, `score = Σ 1 / (60 + rank)` | matches sqlite_vec and Gungnir's `ingest.py` exactly |

Empty queries to `text_search` return `[]` (consistent with the sqlite_vec adapter). Mismatched vector dim raises `BrunnrError`.

---

## 7. The secret resolver (ADR 0010 §2.5)

`PgVectorConfig` carries no inline secret; the resolver tries, in order:

1. **Env var** — `secret_env` (default `EMBER_WELL_PASSWORD`). First non-empty value wins.
2. **Keyring** — `keyring.get_password(keyring_service, username)` when `use_keyring=true` and the optional `keyring` package is importable.
3. **Mode-0o600 file** — `secret_ref`. Linux/macOS enforce permission bits exactly; `0o644` is refused with a pointer at the bits, not the body.
4. **Fallthrough** — `Disconnected(AUTH_FAILED)` with an operator-readable trail naming every source tried and why each was skipped.

The resolved value is **never** echoed into `Disconnected.detail`, log lines, or test assertions — even on the failure path. Permission bits matter; secret rotation is an operator action.

---

## 8. Failure classification — what each `Disconnected.reason` means

| Reason | What you do about it |
|---|---|
| `AUTH_FAILED` | No secret resolved, or the resolved secret was rejected by Postgres (SQLSTATE 28P01 / 28000). Operator action. |
| `CONN_REFUSED` | Host reachable but Postgres said no — wrong port, server down, or `pg_hba.conf` rejects the connection. Strengr will retry. |
| `TIMEOUT` | Network slow or `connect_timeout_s` too low. Strengr will retry. |
| `DNS_FAILURE` | The hostname doesn't resolve. Likely tailnet / `/etc/hosts` issue. |
| `CONFIG_INVALID` | URL malformed, or `BrunnrConfig.backend=pgvector` without a `pgvector:` block. Operator action. |
| `BACKEND_REPORTED_UNAVAILABLE` | pgvector extra not installed; extension missing on a read-only Well; schema-probe dim mismatch; DDL apply failed. Operator action or a re-ingest. |
| `UNKNOWN` | Anything `psycopg` raised that doesn't fit above. `detail` carries the verbatim error message. |

Strengr (`docs/architecture/DOMAIN_MAP.md` §3) reads these reasons to decide whether to retry: recoverable (`CONN_REFUSED`, `TIMEOUT`, `DNS_FAILURE`) get backoff-retry; non-recoverable (`AUTH_FAILED`, `CONFIG_INVALID`) surface the error to the operator immediately.

---

## 9. Operating on Gungnir specifically

Gungnir is the canonical Well — *and* a shared operator-managed Postgres. The iron warning from `~/ai/KNOWLEDGE_DB_ACCESS.md` §2 reads:

> Do not write to `documents` or `chunks` directly. Gungnir's ingest pipeline at `~/ai/ingest/` handles chunking, embedding, and the FTS trigger.

**Make this mechanical.** Set `read_only: true` on the pgvector block:

```yaml
brunnr:
  backend: pgvector
  embedding_dim: 768
  pgvector:
    url: "postgresql://volmarr@gungnir/knowledge"
    secret_ref: "~/.ember/secrets/well.password"
    schema: public
    read_only: true   # ← mechanically refuses add_document / add_chunks
```

In `read_only` mode the adapter:

- Refuses `add_document`, `add_chunks`, `add_episode` with `BrunnrError("... ADR 0010 §4 ...")`.
- Refuses to bootstrap missing tables — `Disconnected(BACKEND_REPORTED_UNAVAILABLE, "refusing to bootstrap silently")`.
- Refuses to create the pgvector extension if it's missing — operator must `CREATE EXTENSION vector` once, as the database owner.
- Refuses to create the `episodes` table on Gungnir — Ember writes nothing.

You still get full retrieval: `vector_search`, `text_search`, `hybrid_search` all work normally.

When you *do* want Ember to write to its own Postgres — say, a dedicated `ember` database alongside Gungnir's `knowledge` — leave `read_only: false` (the default) and Ember bootstraps cleanly.

---

## 10. The Phase-12-vs-13 split, for archaeology

Phase 12 (commit `06ffd25`, 2026-05-21) shipped:

- ADR 0010
- `src/ember/well/brunnr/pgvector/` adapter, secret resolver, DDL
- `BrunnrBackend.PGVECTOR` registry dispatch
- 36 unit tests (no live DB)

Phase 13 (this doc) shipped:

- Live-fire `tests/integration/test_pgvector_real_backend.py` — 10 container tests (write path) + 4 Gungnir tests (read-only retrieval)
- `requires_postgres` / `requires_gungnir` / `requires_podman` markers
- This reference doc + `config/storage.example.yaml` operator switch
- Updated `GUNGNIR_WELL_REFERENCE.md` to mark the forward-reference shipped
- Version bump 0.1.7 → **0.1.9 ("pgvector live")**

If you find any divergence between the ADR's decisions and what the adapter actually does, the test file is the authoritative answer — every numbered ADR decision rides at least one test case.

---

## 11. The Cartographer's closing word

> *The tether is light. The Well is heavy. Together they let a small Ember think big — and the operator's only job is to choose which Well, and write down where the secret lives. Everything else is just plumbing the Forge Worker can clean up later.*

— Védis Eikleið

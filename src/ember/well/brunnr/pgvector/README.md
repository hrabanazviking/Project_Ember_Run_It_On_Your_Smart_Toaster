# `ember.well.brunnr.pgvector/`

**The shared-Well Brunnr.** Postgres + pgvector + tsvector,
Gungnir-compatible. Schema-probe first: if the operator's chosen
schema already holds `documents` + `chunks` tables (the Gungnir shape),
reuse them as-is; otherwise apply the DDL. Read-only mode
mechanically protects shared Wells the operator doesn't own.

**Shipped:** Phase 12-13, slice 2 (version 0.1.9 "pgvector live", 2026-05-21).
**Reads with:** `INTERFACE.md` for the public surface; `schema.sql` for the DDL Ember will apply (when needed); `docs/decisions/0010-pgvector-brunnr.md` for the design rationale; `docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md` for the operator-facing guide.

---

## What this adapter is for

Operators who want Ember to talk to a shared / household Postgres + pgvector instance — the most common case being Volmarr's Gungnir on tailnet. The adapter is **bytewise schema-compatible** with Gungnir's ingest pipeline: Ember can read existing 35k-chunk corpora without modification, and (when given write privileges) deposits new documents in the same shape.

The slice-1 default remains `sqlite_vec` (single file, runs on a toaster). Operators flip to pgvector via one config edit:

```yaml
brunnr:
  backend: pgvector
  embedding_dim: 768
  pgvector:
    url: "postgresql://volmarr@gungnir/knowledge"
    secret_ref: "~/.ember/secrets/well.password"   # mode 0o600
    schema: public
    read_only: true   # for shared Wells you don't own
```

Plus one pip extra: `pip install ember-agent[pgvector]`.

## What it owns

| Concern | Owner |
|---|---|
| Connection lifecycle (one `psycopg.Connection` per `PgVectorBrunnr` instance; no pool in slice 2 per ADR 0010 §2.6) | `adapter.PgVectorBrunnr.__init__` + `close()`. |
| Secret resolution (env → keyring → mode-0o600 file → typed AUTH_FAILED) | `secrets.resolve(pg_cfg)`. |
| Extension provisioning (`CREATE EXTENSION IF NOT EXISTS vector`) | `_ensure_pgvector_extension(conn, read_only)` — read-only mode refuses to create. |
| pgvector codec registration | Calls `pgvector.psycopg.register_vector(conn)` after extension check. |
| Schema probe (read-only `pg_class` + `pg_attribute` + `pg_type` lookup) | `_probe_schema(conn, schema)`. |
| DDL apply (when needed; never on read-only Wells) | `render_schema_sql(embedding_dim, schema)` + `cur.execute(rendered)`. |
| Episodes-table-only apply (when discovering existing documents+chunks but no episodes) | `_apply_episodes_only(conn, schema)`. |
| Embedding-dim verification on probe | `open()` refuses with `Disconnected(BACKEND_REPORTED_UNAVAILABLE)` on mismatch. |
| Document / chunk / episode writes | `add_document` / `add_chunks` / `add_episode` — transactional; the `read_only` flag mechanically refuses with `BrunnrError`. |
| Vector / text / hybrid search | `vector_search` (cosine distance via `<=>` operator); `text_search` (generated `tsv` column + `plainto_tsquery('english', ...)`); `hybrid_search` (RRF k=60 — same constant as sqlite_vec and Gungnir). |
| Typed OperationalError classification (eight reasons: auth_failed / conn_refused / timeout / dns_failure / config_invalid / backend_reported_unavailable / unknown) | `_classify_operational_error(exc)`. Strengr's reconnect policy depends on this split. |

## What it does NOT own

- **Embedding generation.** Smiðja's job; same as sqlite_vec.
- **Network transport details** (TCP keepalive, statement timeout
  tuning beyond `connect_timeout`). Operator's `pg_hba` / postgresql.conf.
- **Schema migrations.** ADR 0010 §2.2 — no auto-migration in slice 2.
  Schema-version bumps are an operator action; the adapter applies
  version 1 only.
- **Connection pooling.** Deferred per ADR 0010 §2.6. When a daemon
  mode or concurrent-tool surface needs a pool, `psycopg_pool` slots
  in behind a factory function without changing the Protocol.

## On-disk shape

Substantially identical to Gungnir's schema (see `schema.sql` for the
parameterised DDL). Key shapes:

```sql
documents     (id bigserial PK, source text, title text, content_type text,
               hash text UNIQUE, metadata jsonb, ingested_at timestamptz)
chunks        (id bigserial PK, document_id bigint FK ON DELETE CASCADE,
               chunk_index integer, text text,
               embedding vector({embedding_dim}),
               tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED,
               char_start integer, char_end integer)
              + UNIQUE(document_id, chunk_index)
              + chunks_embedding_hnsw HNSW(embedding vector_cosine_ops)
              + chunks_tsv_gin       GIN(tsv)
episodes      (id bigserial PK, operator_input text, ember_reply text,
               cited_chunk_ids jsonb, funi_model text,
               well_disconnected boolean, started_at timestamptz, completed_at timestamptz)
schema_version (version integer PK, applied_at timestamptz)
```

Two notable choices (ADR 0010 §2.7):

- **`tsv` is a `GENERATED ALWAYS AS ... STORED` column**, not a trigger-
  populated one. Simpler to reason about; matches Gungnir.
- **HNSW with `vector_cosine_ops`** is the only index combination
  tested. The adapter exposes `vector_index` and `vector_metric` config
  knobs but defaults to these — alternative metric/index combos are
  operator-driven future work.

## Failure semantics

Per ADR 0010 §2.8, every cross-boundary failure becomes a typed
`Disconnected` with one of eight `DisconnectReason` values:

| Trigger | Reason |
|---|---|
| `pgvector` extra not installed | `BACKEND_REPORTED_UNAVAILABLE` |
| URL malformed | `CONFIG_INVALID` |
| Host unreachable | `CONN_REFUSED` |
| TCP timeout | `TIMEOUT` |
| Auth failed (SQLSTATE 28P01 / 28000) | `AUTH_FAILED` |
| Schema-probe embedding-dim mismatch | `BACKEND_REPORTED_UNAVAILABLE` |
| `vector` extension missing on read-only Well | `BACKEND_REPORTED_UNAVAILABLE` |
| Everything else | `UNKNOWN` |

Strengr (Thread realm) reads these to decide whether to retry:
recoverable (`CONN_REFUSED` / `TIMEOUT` / `DNS_FAILURE`) get
backoff-retry; non-recoverable (`AUTH_FAILED` / `CONFIG_INVALID`)
surface to the operator immediately.

For writes:

- **`read_only: true` mechanically refuses `add_document` /
  `add_chunks` / `add_episode`** with a `BrunnrError` that names ADR
  0010 §4.
- **Per-chunk dim mismatch in `add_chunks` rolls back the whole
  batch** and raises `BrunnrError` — same shape as sqlite_vec.

## Phase / version notes

- Phase 12 (slice 2, no version bump): adapter + secret resolver +
  DDL + INTERFACE.md + 36 unit tests; gated until Phase 13.
- Phase 13 (slice 2, 0.1.9 "pgvector live"): 10 container tests (write
  path via podman pgvector:pg18) + 4 Gungnir read-only tests against
  the live tailnet; `PGVECTOR_BRUNNR_REFERENCE.md` operator guide;
  `config/storage.example.yaml` worked examples.

**Two real bugs caught by live-fire and fixed (both regression-tested
now):**

1. `register_vector` ran before `CREATE EXTENSION` → vector type not
   found. Fix: `_ensure_pgvector_extension(conn, read_only)` helper
   sits between connect and register.
2. `{{}}` in `schema.sql` was a stale `.format()` escape that never
   got de-escaped. Fix: `'{}'::jsonb`.

## Limitations

- **No live integration test in CI by default.** The Postgres-
  dependent tests use `requires_postgres` / `requires_gungnir` /
  `requires_podman` markers (informational; fixtures gate by
  reachability probe, same pattern as `requires_ollama`). Run them
  manually with `pytest -m requires_gungnir tests/integration/test_pgvector_real_backend.py`.
- **No connection pool** (§2.6). Single-operator CLI is the slice-2
  target.
- **No automatic schema migration.** If pgvector upgrades and the
  schema needs to change, operators re-create the database from
  `schema.sql`. Phase-13 acceptance test will fail-loud on schema
  drift.
- **No read-replica URL.** Single URL for both reads and writes.

## Related

- `INTERFACE.md` — operator-facing surface contract.
- `schema.sql` — parameterised DDL.
- `secrets.py` — the env → keyring → file → typed resolver.
- `adapter.py` — `PgVectorBrunnr` + helpers.
- `docs/decisions/0010-pgvector-brunnr.md` — design rationale.
- `docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md` — operator guide (11
  sections).
- `docs/adapters/GUNGNIR_WELL_REFERENCE.md` — live survey of the
  canonical operator Well this adapter targets.
- `tests/unit/test_brunnr_pgvector_*.py` — 36 unit tests.
- `tests/integration/test_pgvector_real_backend.py` — 14 live-backend
  tests (container + Gungnir).

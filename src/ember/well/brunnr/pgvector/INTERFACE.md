# INTERFACE — `ember.well.brunnr.pgvector`

## Module purpose

Postgres + pgvector Brunnr (ADR 0010). Peers with `sqlite_vec` behind the
same `BrunnrHandle` Protocol — same hybrid-search shape (RRF, `k=60`),
Gungnir-compatible row shape, opt-in via `BrunnrBackend.PGVECTOR`.

Phase-12 ships the adapter and the secret resolver; Phase-13 lights up
the live-fire integration test against Gungnir and bumps Ember to
0.1.9.

## Public entry points

- `ember.well.brunnr.pgvector.PgVectorBrunnr` — concrete adapter class.
- `ember.well.brunnr.pgvector.open(config) -> PgVectorBrunnr | Disconnected` —
  the entry that the top-level Brunnr registry dispatches to.
- `ember.well.brunnr.pgvector.adapter.render_schema_sql(*, embedding_dim, schema)` —
  the rendered DDL (exposed so the schema-shape test can assert on it
  without a live database).
- `ember.well.brunnr.pgvector.secrets.resolve(config, *, env=None, keyring_module=None)` —
  the env → keyring → mode-600-file resolver from ADR 0010 §2.5.

## On-disk shape

Tables and indexes are defined in `schema.sql`, parameterised by
`embedding_dim` and `schema`:

- `documents (id, source, title, content_type, hash UNIQUE, metadata jsonb, ingested_at timestamptz)`
- `chunks (id, document_id FK, chunk_index, text, embedding vector(dim), tsv tsvector GENERATED, char_start, char_end)` + UNIQUE(document_id, chunk_index)
- `chunks_embedding_hnsw` — HNSW index on `embedding vector_cosine_ops`
- `chunks_tsv_gin` — GIN index on the generated `tsv` column
- `episodes` — Ember-side conversation log (Gungnir does not have this; created even when the rest is discovered)
- `schema_version` — single-row version marker (currently 1)

## Schema-probe semantics (ADR 0010 §2.2)

On `open()`:

1. Probe the configured schema for `documents`, `chunks`, `episodes`.
2. If `documents` + `chunks` exist:
   - Check `chunks.embedding`'s pgvector dimension against
     `BrunnrConfig.embedding_dim`. Mismatch → `Disconnected(BACKEND_REPORTED_UNAVAILABLE)`.
   - If `episodes` is missing AND `read_only=false`, create *only*
     the episodes table — never DDL into discovered tables.
3. If `documents` or `chunks` is missing:
   - If `read_only=true`, refuse with `Disconnected(BACKEND_REPORTED_UNAVAILABLE,
     "refusing to bootstrap silently")`.
   - Otherwise apply the full DDL.

This honours the iron warning at
`docs/adapters/GUNGNIR_WELL_REFERENCE.md` §9: an Ember pointed at a
populated operator-managed Gungnir does not get to mutate the host
schema.

## Secret resolution (ADR 0010 §2.5)

`secrets.resolve(config)` tries, in order:

1. **Env var** — `config.secret_env` (default `EMBER_WELL_PASSWORD`).
2. **Keyring** — when `use_keyring=True` and `keyring` is importable;
   service `config.keyring_service` (default `ember-well`); username
   `config.username` or parsed from the URL.
3. **Mode-600 file** — `config.secret_ref` (default
   `~/.ember/secrets/well.password`); refuses any mode that isn't
   exactly `0o600` on Linux / macOS.
4. **Final** — `SecretResolution.missing(...)`. Adapter folds this into
   `Disconnected(AUTH_FAILED, detail=<which sources were tried>)`.

The resolved secret is **never logged or echoed back** — even on error.

## Search semantics

- `vector_search` — pgvector `<=>` (cosine distance); converted to
  `score = 1 - distance` to match sqlite_vec's convention.
- `text_search` — `plainto_tsquery('english', ...)` against the
  generated `tsv` column; ranked by `ts_rank`. Empty query returns the
  empty list (consistent with sqlite_vec).
- `hybrid_search` — RRF (`k=60`) over the wider candidate pools from
  both, then trimmed to `k`. Same constant as sqlite_vec and Gungnir.

## Failure semantics

- `open()` returns `Disconnected` rather than raising on: pgvector
  extra not installed, URL parse error, host unreachable, auth failure,
  schema probe mismatch, schema apply failure. Reason classification
  per ADR 0010 §2.8.
- `add_chunks` rolls back the whole batch transactionally on any
  per-chunk failure and raises `BrunnrError`. Smiðja marks the journal
  entry failed and continues — same contract as sqlite_vec.
- Read paths raise `BrunnrError` on missing rows (programming-error
  contract; the search APIs return empty results, not raises).

## Connection lifecycle

Connection-per-handle (ADR 0010 §2.6). Each `PgVectorBrunnr` instance
owns exactly one `psycopg.Connection`; `close()` calls `conn.close()`.
No pool in Phase 12. The factory pattern in `open()` is the future hook
when a daemon mode or concurrent-tool surface needs a pool.

## Limitations (Phase 12)

- **No live integration test yet.** Phase 13 ships the
  `requires_postgres` marker, the docker-compose fixture, and the
  `tests/integration/test_pgvector_real_backend.py` round-trip.
- **No operator-facing reference doc yet.** Phase 13 ships
  `docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md`.
- **No `config/storage.example.yaml` pgvector switch yet.** Phase 13
  edits the example.
- **No read-replica URL.** Single URL for both reads and writes.
- **No automatic schema migration.** Schema-version bumps are an
  operator action; the adapter only ever applies version 1.

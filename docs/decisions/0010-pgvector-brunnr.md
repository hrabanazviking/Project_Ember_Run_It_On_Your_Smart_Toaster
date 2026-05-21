# ADR 0010 — pgvector Brunnr adapter

**Date:** 2026-05-21
**Status:** **Ratified 2026-05-21 by Volmarr** (under the slice-2 scope ratification — "go for slice 2 — bundle 1, 2, 3"; ADR-level ratification implicit in `EMBER_SECOND_SLICE_PLAN.md` §3 Phase 12-13).
**Author:** Mythic-Engineering session — Architect (Rúnhild Svartdóttir) + Cartographer (Védis Eikleið) + Scribe (Eirwyn Rúnblóm).
**Supersedes:** None
**Superseded by:** —

---

## 1. Context

Slice 1 shipped the `sqlite_vec` Brunnr — single file, zero auxiliary processes, runs on a toaster. It is the right default for the Pi-5 operator and the only backend the first slice supported.

But the canonical Ember Well already exists: **Gungnir**. Postgres 18 + pgvector 0.8 + pg_trgm, holding 95 documents and 35 682 chunks of Volmarr's corpus (see `docs/adapters/GUNGNIR_WELL_REFERENCE.md` for the live survey). The Vow of Tethered Grounding names Gungnir as the first concrete Well; the Vow of Smallness keeps `sqlite_vec` the default; the Vow of Graceful Offline requires both to be peers behind the same `BrunnrHandle` Protocol.

This ADR settles:

1. **What the adapter looks like** — class shape, schema apply vs schema probe, search shape, episode storage.
2. **How secrets resolve** — env → keyring → mode-600 file → typed failure.
3. **How the connection is managed** — connection-per-handle for first ship; pool deferred with rationale.
4. **What gets shared with Gungnir** — exact row shapes, RRF parameters, naming.

The Phase-12 implementation builds the adapter and the secret resolver; Phase-13 adds the live-fire test against Gungnir and the operator-facing reference doc.

## 2. Decision

### 2.1 Same `BrunnrHandle` Protocol — peer, not parent

**Decision:** `PgVectorBrunnr` implements the existing `BrunnrHandle` Protocol from `src/ember/well/brunnr/handle.py`. No subclass, no new abstract base. `backend_kind = "pgvector"`.

**Why:** the Protocol was designed in Phase 3 to be backend-agnostic. Adding a second adapter exercises the Protocol — if the shape needs to change for pgvector, it was the wrong shape. (Spoiler: it doesn't. The Protocol holds.)

### 2.2 Schema-probe, then optional apply

**Decision:** `open()` first probes for the Gungnir-shape tables (`documents`, `chunks`, optionally `episodes`). If they exist with the configured embedding-dim, the adapter uses them as-is. If they don't exist, the adapter runs `schema.sql` to create them.

The probe is read-only: `pg_class` lookup + `pg_attribute` check of `chunks.embedding` dimension. If the dimension mismatches, `open()` returns `Disconnected(BACKEND_REPORTED_UNAVAILABLE, detail="embedding_dim X != configured Y")` rather than trying to migrate.

**Why probe-first:** an operator pointing Ember at an *existing* Gungnir must not have their schema altered. Per the iron warnings in `docs/adapters/GUNGNIR_WELL_REFERENCE.md` §9 — "do not write to documents or chunks directly" — direct DDL into a populated Gungnir is also a hard "no". Probe-first means **read-mostly by default**; the operator opts into apply by pointing at a fresh database.

**Why apply at all:** an Ember-managed pgvector — a fresh local Postgres, or a dedicated `ember` database on Gungnir — needs the schema to exist. The same code path supports both modes.

### 2.3 Episodes table is Ember-side, not Gungnir-side

**Decision:** `schema.sql` includes an `episodes` table mirroring the sqlite_vec one. If the probe finds `documents` + `chunks` but not `episodes`, the adapter creates only `episodes` — it never touches the discovered tables.

**Why:** Gungnir doesn't have `episodes` — it's a knowledge-graph database, not a conversation log. Ember's persisted Episodes are a new concern that must coexist without rewriting the host schema.

### 2.4 Search shape: RRF with the same `k=60` dampener

**Decision:** `hybrid_search` uses the SQL pattern in `GUNGNIR_WELL_REFERENCE.md` §6 — `row_number()` over vector and FTS subqueries, fused with `sum(1.0 / (60 + rank))`. The constant `60` matches the sqlite_vec adapter (`_RRF_K = 60`) so results are commensurate across backends.

**Why match exactly:** an operator who switches backend should get the same answer ordering for the same query and embedding. Drift here would silently change retrieval quality.

**Vector index:** HNSW with `vector_cosine_ops` (matches Gungnir's `chunks_embedding_hnsw`). Distance operator `<=>` (cosine distance). The adapter exposes `vector_index` and `vector_metric` config knobs but defaults to `hnsw` + `cosine` — the only combination tested against Gungnir.

**Text search:** Postgres `tsvector` + `plainto_tsquery('english', ...)`. The sqlite-side `_escape_fts5_query` lesson translates: `plainto_tsquery` already handles operator-string sanitisation by ignoring anything it doesn't recognise as a word — no extra escaping needed. The adapter still strips empty queries before issuing the SQL (consistency with sqlite_vec).

### 2.5 Secret resolution order

**Decision:** `secrets.resolve(config)` tries, in order:

1. **Env var** — if `PgVectorConfig.secret_env` is set, read that env var. `EMBER_WELL_PASSWORD` is the documented default. Empty / missing → continue.
2. **Keyring** — if the `keyring` package is importable AND `PgVectorConfig.use_keyring` is True, look up `keyring.get_password("ember-well", username)`. Missing → continue.
3. **Mode-600 file** — read `PgVectorConfig.secret_ref` (default `~/.ember/secrets/well.password`). Refuse if file permissions are not 0o600 (operator-readable only). Missing / wrong-mode → continue.
4. **Final** — return `None`. Caller folds this into `Disconnected(AUTH_FAILED, detail="no secret resolved")`.

**Why env first:** env-var auth is the standard for containerised / CI deployments. Putting it first lets the same config file work in dev (file) and prod (env) without conditional blocks.

**Why keyring optional:** `keyring` is a transitive dep across Linux distros (libsecret, kwallet, etc.). Making it optional honours the stdlib-first rule from ADR 0007.

**Why mode-600 enforcement:** the secret file is the on-disk artifact most likely to be accidentally world-readable. Refusing to read a 0o644 file is the cheap belt-and-suspenders fix; the operator gets a clear error pointing at the permission bits rather than a silent leak.

**Why never log the secret:** even on error. `Disconnected.detail` carries the *reason* ("file at /foo has mode 0644, want 0600") but never the contents or the resolved value.

### 2.6 Connection-per-handle, no pool (deferred)

**Decision:** each `PgVectorBrunnr` instance owns exactly one `psycopg.Connection`. `close()` calls `conn.close()`. Concurrent operators across threads / processes get their own handles via repeated `open()` calls.

**Why no pool:** the first ship is a CLI tool with one operator at a time. A pool adds:

- Lifecycle complexity (when does a pool drain? what about Ctrl-C?).
- Dependency on `psycopg_pool` (extra wheel).
- Concurrency assumptions that the rest of Ember doesn't yet make (Hjarta is single-threaded, Munnr is single-threaded, Smiðja's ingest is batch-serial).

**When to revisit:** when a tool surface or a daemon mode runs many concurrent retrievals. At that point, `psycopg_pool.ConnectionPool` slots in behind a factory function without changing the Protocol. The factory hook is the single edit needed; the rest of the adapter is pool-agnostic.

### 2.7 What `add_chunks` writes

**Decision:** matches sqlite_vec semantics exactly:

- Per chunk: validate `len(embedding) == self.embedding_dim` or raise `BrunnrError` (no silent truncation).
- Upsert on `(document_id, chunk_index)` — same conflict target as sqlite_vec's `ON CONFLICT(document_id, chunk_index) DO UPDATE`.
- `RETURNING id` collects the inserted/updated row id list.
- Embedding goes into `chunks.embedding` directly (pgvector's `vector` column type accepts a Python `list[float]` via the `pgvector.psycopg` adapter).
- `tsv` is a Postgres `GENERATED` column (`to_tsvector('english', text) STORED`), so it populates automatically — no trigger needed.

**Why GENERATED tsv vs trigger:** Postgres 12+ supports generated columns; they're simpler to reason about than triggers, and match what Gungnir actually uses.

**Rollback on partial failure:** the whole batch is one transaction; if any chunk fails dim-check or SQL error, the transaction rolls back. Caller (Smiðja) sees a `BrunnrError` and marks the journal entry failed — same contract as sqlite_vec.

### 2.8 `Disconnected` reasons used by this adapter

| Trigger | DisconnectReason | Notes |
|---|---|---|
| `pgvector` extra not installed | `BACKEND_REPORTED_UNAVAILABLE` | `import psycopg` / `import pgvector.psycopg` fails. |
| URL malformed | `CONFIG_INVALID` | `psycopg.errors.OperationalError` with parse hint. |
| Host unreachable | `CONN_REFUSED` | `psycopg.OperationalError` whose `pgconn` is `None`. |
| TCP timeout | `TIMEOUT` | `psycopg.OperationalError` with timeout in message. |
| Auth failed | `AUTH_FAILED` | `psycopg.OperationalError(sqlstate='28P01' or '28000')`. |
| Schema probe mismatch | `BACKEND_REPORTED_UNAVAILABLE` | embedding-dim mismatch; concrete `detail`. |
| `pgvector` extension missing | `BACKEND_REPORTED_UNAVAILABLE` | `SELECT extname FROM pg_extension` returns no row. |
| Anything else | `UNKNOWN` | `detail` carries `repr(exc)`. |

**Why typed reasons matter:** Strengr's reconnect policy (Phase 4) distinguishes recoverable (`CONN_REFUSED`, `TIMEOUT`) from non-recoverable (`AUTH_FAILED`, `CONFIG_INVALID`) — wrong classification means Strengr either retries forever on a permanent failure or gives up on a transient one.

### 2.9 What Phase 12 ships vs what Phase 13 ships

Phase 12 (this ADR's implementation phase):

- `src/ember/well/brunnr/pgvector/__init__.py` — re-export.
- `src/ember/well/brunnr/pgvector/INTERFACE.md` — operator-facing surface contract.
- `src/ember/well/brunnr/pgvector/adapter.py` — `PgVectorBrunnr` class.
- `src/ember/well/brunnr/pgvector/schema.sql` — Gungnir-shape DDL (parameterised by embedding_dim).
- `src/ember/well/brunnr/pgvector/secrets.py` — env → keyring → file resolver.
- `src/ember/well/brunnr/handle.py` — registry adds `BrunnrBackend.PGVECTOR` dispatch.
- Unit tests: secret-resolver order, schema-probe SQL shape, dim-mismatch refusal — **all without a live Postgres**. The Postgres-dependent tests are Phase 13.

Phase 13 ships the live-fire integration test against real Gungnir, the operator-facing `PGVECTOR_BRUNNR_REFERENCE.md`, the `config/ember.example.yaml` switch, and the bump to **0.1.9 ("pgvector live")**.

**Why no version bump in Phase 12:** the adapter is not yet operator-usable — no integration test, no operator docs, no example config. Ship the bump when the operator can actually flip the switch.

## 3. Consequences

**Gain:**

- Ember can be tethered to Gungnir or any other Postgres + pgvector instance.
- Existing Gungnir corpora (Volmarr's 35k chunks) become Ember's retrieval source without re-ingesting.
- The same `BrunnrHandle` Protocol works across backends — no Spark-side branching.
- Hybrid search produces the same ranking shape as sqlite_vec for the same query, by design.

**Cost:**

- New optional dep: `psycopg[binary]>=3.2`, `pgvector>=0.3` (under the `pgvector` extra; default install is still zero-extras).
- One more failure surface to audit (auth, network, schema mismatch).
- The schema-probe vs schema-apply split adds branching in `open()` — documented and tested, but real.

**Risks deliberately accepted:**

- **No connection pool.** Single-operator CLI is the target; revisit when the surface changes. (§2.6)
- **No automatic schema migration.** If an operator upgrades pgvector and the schema needs to change, they re-create the database from `schema.sql`. The Phase-13 acceptance test will fail-loud on schema drift. (§2.2)
- **No write-quotas or rate-limits.** Adapter writes as fast as `add_chunks` is called. Smiðja's batch sizing is the throttle; if a future tool calls write paths directly, that tool will need its own limits.

## 4. Open questions deferred to later

- **Per-tenant schemas.** `PgVectorConfig.schema` is a single string today. Multi-tenant Ember (one Postgres, many operators) would need per-Hjarta-identity schema selection. Out of scope until there's a real multi-operator deployment.
- **Replica reads.** A read-replica URL distinct from the write URL would speed `ember chat` on large Gungnirs. Trivial to add; defer until needed.
- **Read-only mode flag.** Today the adapter writes whenever Smiðja calls it. A `read_only=True` config flag that fails-loud on `add_*` would harden the "do not write to Gungnir" rule mechanically. Worth a follow-up ADR if/when an operator wires Ember to a shared production Gungnir.

## 5. Related docs

- `docs/adapters/GUNGNIR_WELL_REFERENCE.md` — the live survey this adapter targets.
- `docs/adapters/BRUNNR_BACKEND_MATRIX.md` — peer comparison across backends.
- `docs/architecture/EMBER_SECOND_SLICE_PLAN.md` §3 Phase 12-13 — the slice phasing this ADR rides.
- `docs/decisions/0007-first-slice-ratification-2026-05-21.md` — the stdlib-first / typed-value standing rules this ADR honours.
- `src/ember/well/brunnr/handle.py` — the Protocol this adapter implements.
- `src/ember/well/brunnr/sqlite_vec/adapter.py` — the peer adapter whose shape this one mirrors.

# BRUNNR_BACKEND_MATRIX — Storage Backends for the Well

**Voice:** Cartographer (Védis Eikleið)
**Status:** Proposed — for ratification. Bootstrap-stage reference.
**Last touched:** 2026-05-21
**Reads with:** `docs/architecture/ARCHITECTURE.md`, `docs/architecture/DOMAIN_MAP.md`, `docs/adapters/GUNGNIR_WELL_REFERENCE.md`, `docs/SYSTEM_VISION.md` §"Vow of Pluggable Storage".

---

## 1. Why a backend matrix exists

The Vow of Pluggable Storage forbids single-backend binding. Every Brunnr adapter must satisfy the same `INTERFACE.md` (see `docs/architecture/DOMAIN_MAP.md` §2.1). This document picks the right adapter for each operator situation. The first slice ships `sqlite_vec` only; the others are sequenced.

---

## 2. The matrix

| Backend | Footprint | Process model | Vector index | FTS | Cross-host? | Toaster-class? | First-slice support? |
|---|---|---|---|---|---|---|---|
| **sqlite_vec** | One file under `~/.ember/well/store.db` | In-process | `sqlite-vec` (KNN flat scan or vector index per version) | FTS5 | No (single file) | **Yes — default** | **Yes** |
| **pgvector** | Postgres server | Out-of-process | `pgvector` HNSW (cosine, L2, IP) | tsvector + GIN | Yes (over net/tailnet) | If shared on a household machine | Phase 8 (Gungnir slice) |
| **qdrant** | Qdrant server (Docker or binary) | Out-of-process | HNSW (native) | Payload filters; weaker FTS | Yes | If shared | Later |
| **chroma** | Chroma server / embedded | Either | HNSW | None native (filter-only) | Either | If embedded | Later |
| **lancedb** | Embedded columnar files | In-process | IVF-PQ / HNSW | Tantivy-backed FTS | No (file) | Yes (compact format) | Later |

Backend selection is a `config/storage.example.yaml` decision, not a code change. Switching backends is `ember well export ./snapshot.jsonl` → reconfigure → `ember well import ./snapshot.jsonl` (export/import are deferred to Phase 9, not first slice).

---

## 3. When each backend is the right answer

### 3.1 `sqlite_vec` — the toaster default

**Pick this when:**
- The operator is one person on one device.
- The corpus fits in 1–2 GB on disk (a few tens of thousands of chunks; the Gungnir reference comparison: 35 682 chunks = ~372 MB of chunk-row-plus-vector in Postgres; in SQLite with `sqlite-vec` the same content lands in a similar order of magnitude).
- The host is a Raspberry Pi, an old laptop, or any single device where "another process running Postgres" is overhead the operator does not want.

**Why it works for a toaster:**
- Zero auxiliary processes. `sqlite3` is in the standard library; `sqlite-vec` is a single shared object.
- File-level backup: `cp ~/.ember/well/store.db /backups/`.
- WAL mode means a long Smiðja ingest does not block a concurrent `ember chat` reader.

**Watch outs:**
- The vector index in `sqlite-vec` is fast for tens of thousands of chunks but degrades vs HNSW once you cross hundreds of thousands. If a Pi-based operator ingests their whole laptop, they may want pgvector on a small NAS instead.
- No cross-host sharing. Two Embers on two devices cannot share a `sqlite_vec` Well over the network without copying the file.

### 3.2 `pgvector` — the household default

**Pick this when:**
- More than one device wants to talk to the same Well (the operator's Pi *and* their laptop).
- The operator already runs a small home server (Gungnir is the canonical example).
- The corpus is large enough to want HNSW (~10k+ chunks).

**Why it works for households:**
- Postgres + pgvector is the most battle-tested vector backend in the open source world.
- Network access works over Tailscale, ZeroTier, plain LAN, or SSH-tunnelled localhost.
- Backup is `pg_dump`; standby is hot-replication; the database community is large.

**Watch outs:**
- Requires a Postgres instance that the operator (or their household admin) is willing to keep alive. This is the price of cross-host sharing.
- Connection auth: Ember must hold a credential. Use a keyring on desktop hosts; fallback to a mode-600 file at `~/.ember/secrets/well.password` on Pis.

### 3.3 `qdrant` — when the operator already runs Qdrant

**Pick this when:**
- An existing Qdrant cluster is in the household for another project.
- The operator wants payload-filter-heavy retrieval (e.g. "only chunks from documents tagged X").

**Watch outs:**
- Weaker FTS than Postgres. Hybrid search depends on Qdrant's text-payload filter, which is not full FTS.
- More moving parts than pgvector for the same outcome.

### 3.4 `chroma` — when the operator already runs Chroma

**Pick this when:**
- Existing Chroma persistence already exists in the household.
- The operator wants to share Embers with a Python notebook workflow.

**Watch outs:**
- Embedded Chroma in-process works for tiny corpora; the server mode adds another process to babysit.
- No native FTS — hybrid search must be implemented entirely on the Ember side.

### 3.5 `lancedb` — when single-host columnar makes sense

**Pick this when:**
- The host has lots of disk and the operator wants the columnar format's analytics ergonomics.
- The operator runs other LanceDB workloads.

**Watch outs:**
- Newer than `sqlite_vec` and `pgvector`. Smaller community.

---

## 4. The Brunnr interface as the shield

Each backend is fronted by an adapter under `src/ember/well/brunnr/<backend>/`. The adapter implements the `BrunnrHandle` protocol declared in `src/ember/well/brunnr/handle.py` (see `docs/architecture/DOMAIN_MAP.md` §2.1 for the minimum surface).

The interface is the only thing Spark code sees. The choice of backend is invisible above the interface. **Any adapter that leaks backend-specific types upward is a release-blocking bug.**

If a backend cannot satisfy an interface operation (e.g. Chroma cannot do native FTS), the adapter must:
- Implement the operation in terms of operations it *can* do (e.g. fetch candidates by vector then filter client-side).
- Or return a typed `NotSupportedHere(operation)` value — never a silent partial implementation.

---

## 5. Migration story

When an operator outgrows their backend (typically `sqlite_vec` → `pgvector` once a second device joins), the migration is:

1. `ember well export ~/ember_snapshot.jsonl` — dumps `Document` + `Chunk` rows as JSONL (each chunk with embedding inline).
2. Reconfigure `~/.ember/config/storage.yaml` to point at the new backend.
3. `ember well import ~/ember_snapshot.jsonl` — re-ingests without re-embedding.

This deferred-to-Phase-9 export/import keeps embeddings durable across backend choices and avoids re-paying the embedding cost.

---

## 6. What this document is not

- **Not a benchmark.** Numbers in §2 are order-of-magnitude orientation, not measured comparisons on Pi hardware. A real benchmark belongs in `tests/benchmarks/` once the slice ships.
- **Not a recommendation against any backend.** Every adapter row above is a first-class peer per the Vow of Pluggable Storage. The matrix exists to *match the operator's situation*, not to rank.

— Védis Eikleið

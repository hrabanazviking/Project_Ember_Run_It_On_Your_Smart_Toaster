# 08 — `sqlite-vss` and Embedding-in-Database Approaches

**Category:** Memory & Knowledge Storage
**Runa relevance:** Muninn (retrieval index — pinned by ADR-0002 §D-2.2), Heimskringla (semantic-dedup cache)
**Status:** Research synthesis. Specifically supports the ADR-0002 decision.
**Last touched:** 2026-05-17

---

## 1. Core idea

Most "vector database" deployments are a separate service: a process, a port, a config, a network call, an operational footprint. For agents whose corpora are not large enough to justify dedicated infrastructure — that is, almost all single-user personal agents and most enterprise teams in the early stages — putting the vector index *inside an existing database file* is dramatically simpler. `sqlite-vss` (and its successor `sqlite-vec`) does exactly this: a SQLite extension that adds a `vss0` (or `vec0`) virtual table type supporting approximate nearest-neighbour search.

For Runa, this means Muninn's structured episode store and its vector retrieval index live in *the same SQLite file*. One file, one backup, one `cp` to snapshot, zero extra services. This aligns precisely with Runa's "files on disk an operator can see" doctrine (ARCHITECTURE.md §4.3) and is the formally-committed choice in ADR-0002 §D-2.2.

## 2. Technical depth

**SQLite virtual tables** are SQLite's plugin mechanism for adding new table types backed by custom storage and query engines. The host application sees a normal table interface; the implementation is in a loaded extension. `sqlite-vss` uses this to expose `CREATE VIRTUAL TABLE memory_vec USING vss0(embedding(384))`, where `embedding` is a column holding a fixed-dimension vector and `vss0` provides the indexing and search.

**Under the hood:** `sqlite-vss` (the original, by Alex Garcia, 2023) wraps **FAISS** (Facebook AI Similarity Search) — specifically the IVF (inverted-file) index family by default. **`sqlite-vec`** (Alex Garcia, 2024+) is the successor: a from-scratch reimplementation in pure C, no FAISS dependency, easier to build cross-platform, supports brute-force (no indexing) and graph-based (HNSW-style) modes. As of 2025, `sqlite-vec` is the recommended path for new deployments — fewer build hassles, smaller binary, better SQLite version compatibility.

**Query shape:**

```sql
SELECT episodes.episode_id, episodes.text, distance
  FROM memory_vec
  JOIN episodes ON memory_vec.rowid = episodes.rowid
 WHERE memory_vec.embedding MATCH :query_embedding
   AND episodes.conversation_id = :conv_id   -- normal SQL filter
 ORDER BY distance
 LIMIT 12;
```

The `MATCH` operator triggers the ANN search; standard SQL `WHERE` and `JOIN` clauses compose naturally. This is the killer feature — *vector + structured filtering in one query*, no two-phase fetch + filter dance against a separate service.

**ANN algorithms** typically available:
- **Brute force (exact).** O(N · D) per query. Fine for up to ~10K-50K vectors at moderate dimension; correctness is unimpeachable.
- **IVF (Inverted File).** Cluster vectors, search nearest clusters only. Trade speed for recall.
- **HNSW (Hierarchical Navigable Small World, Malkov & Yashunin 2016).** Graph-based; the current state-of-the-art for ANN on most workloads. Supports incremental insertion.

For Runa-scale corpora (10K-1M episodes over years), brute force is fine up to ~50K and HNSW handles the rest comfortably on Pi 5 hardware.

**Alternatives in the embedding-in-database family:**

- **`pgvector`** — PostgreSQL extension; the strongest production-grade option if Postgres is already in your stack. Supports HNSW and IVF. Doesn't fit Runa's "single SQLite file" doctrine but is the natural choice for a longhall deployment with a separate database server.
- **`duckdb-vss`** — DuckDB has a similar extension. DuckDB is column-oriented, optimised for analytics over time-series and large rows; competitive but a different ergonomic profile.
- **LanceDB** — A columnar vector database with its own on-disk format. Excellent ergonomics, growing fast. Lives as a directory of files rather than a single file. ADR-0002 D-2.2 specifically chose `sqlite-vss` over LanceDB for the single-file property.
- **ChromaDB** — Popular among LangChain users. SQLite-backed by default but more abstraction layers between the app and the bytes.
- **Standalone dedicated vector DBs** (FAISS-server, Milvus, Qdrant, Weaviate, Pinecone) — separate services, network calls. Right for large-scale shared deployments; overkill for one Pi.

## 3. Key works

- **Malkov, Yashunin. "Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs."** arXiv:1603.09320, 2016. The HNSW paper.
- **FAISS (Johnson, Douze, Jégou, Facebook AI, 2017).** github.com/facebookresearch/faiss. The reference ANN library.
- **`sqlite-vss`** — github.com/asg017/sqlite-vss. The original SQLite vector extension by Alex Garcia (2023).
- **`sqlite-vec`** — github.com/asg017/sqlite-vec. The successor, recommended for new projects.
- **`pgvector`** — github.com/pgvector/pgvector. The Postgres analogue.
- **DiskANN (Subramanya et al., MSR, NeurIPS 2019).** Disk-friendly ANN — relevant when index size exceeds RAM.

## 4. Empirical results

- For corpora up to ~100K vectors at 384-768 dimensions, `sqlite-vec` query latency on commodity hardware is sub-10 ms (HNSW) or sub-100 ms (brute force). Both are well within the kernel's latency budget per DATA_FLOW §2.2.
- Memory overhead for HNSW is roughly `(D + 16) · N` bytes per vector (where D = dim) — for 100K episodes at 384 dim, ~40 MB. Trivial on Pi 5 (16 GB).
- Recall: HNSW at default parameters typically achieves 95-99% recall@10 vs exact search. Recall is tunable via `ef_search` parameter at query time.
- `sqlite-vss` (FAISS-based) has occasional build-friction issues on ARM and Windows. `sqlite-vec` ships clean cross-platform binaries.
- At very large scales (>10M vectors) dedicated services (Milvus, Qdrant) outperform SQLite extensions in raw throughput, but those scales are beyond Runa's expected ceiling.

## 5. Applicability to Runa

This is the implementation choice for **Muninn** (ADR-0002 §D-2.2). Concrete recommendation:

- **Use `sqlite-vec`, not `sqlite-vss`.** Easier build, no FAISS dependency, actively maintained.
- **Single file:** `~/.runa/memory/muninn.sqlite` holds episode metadata, episode text, embeddings (via `vec0` virtual table), task ledger (Skuld), emotional journal (Eldhugi), identity store. *Or* split into `muninn.sqlite` + `skuld.sqlite` + `eldhugi.sqlite` if write contention shows up — that decision can defer to slice-time.
- **Algorithm choice:** brute force until episodes > 10K, then auto-migrate to HNSW. Migration is a `runa.migrations` script.
- **Embedding model pinning:** the model used to compute embeddings is config-pinned (`memory.embedding_model`); change-of-model triggers a re-embedding migration.
- **Hybrid retrieval:** alongside the vec0 virtual table, an FTS5 virtual table on the same `episodes` table provides BM25-style sparse retrieval. RRF in application code fuses the two ([[04-rag-evolution]] §2 hybrid retrieval).

For **Heimskringla semantic-dedup cache** (ADR-0002 §D-2.4):

- A separate sqlite-vec-backed file at `~/.runa/cache/heimskringla/semantic_dedup.sqlite` holds recent (prompt, prompt-embedding, response, provider, model, ts) rows.
- Query at request time: embed the incoming prompt with the same embedding model Muninn uses, find nearest cached prompt with cosine ≥ threshold (default 0.92), return its cached response.

What to avoid:

- Don't mix embedding-model outputs in the same vec0 index. One table per model.
- Don't rely on `sqlite-vss` features that haven't migrated to `sqlite-vec` yet. Verify before depending.
- Don't open the SQLite file with WAL mode disabled — concurrent readers + a writer is a normal Muninn pattern.
- Don't run unbounded brute-force on a 1M+ vector table. Auto-trigger the HNSW migration before performance degrades.

## 6. Open questions

- **Quantised embeddings in sqlite-vec.** `sqlite-vec` supports binary/scalar quantisation; storage and speed wins are real but recall impact varies. Worth evaluating at scale.
- **Filtered ANN.** Combining a structured `WHERE` clause with the `MATCH` is correct but the planner doesn't always pick the best execution order. For very-selective filters (one conversation_id out of thousands), pre-filtering then ranking may beat the ANN. Empirical tuning territory.
- **Distributed Muninn.** If Runa ever runs across multiple machines with shared state, SQLite is single-writer. The decision tree: stay single-writer (and route writes through the gateway), or migrate to pgvector on a dedicated DB host.
- **Vector compression / dimensionality reduction.** Matryoshka-trained models ([[03-embedding-models-landscape]]) let storage scale down with acceptable recall loss. Worth using for cold-archival memories.

## 7. References (curated)

- github.com/asg017/sqlite-vec — recommended SQLite vector extension.
- github.com/asg017/sqlite-vss — predecessor (FAISS-wrapping).
- arXiv:1603.09320 — HNSW paper.
- github.com/facebookresearch/faiss — FAISS reference.
- github.com/pgvector/pgvector — Postgres alternative for longhall deployments.
- ann-benchmarks.com — standardised ANN benchmark site with current numbers.
- Anchored decision: `docs/decisions/0002-initial-subsystem-decisions-2026-05-17.md` §D-2.2.
- Companion docs: [[03-embedding-models-landscape]], [[04-rag-evolution]], [[05-long-context-vs-retrieval]].

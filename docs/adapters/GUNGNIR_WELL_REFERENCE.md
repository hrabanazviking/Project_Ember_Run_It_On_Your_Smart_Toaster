# GUNGNIR_WELL_REFERENCE — A Concrete Well, Already Built

**Voice:** Cartographer (Védis Eikleið), with Scribe (Eirwyn Rúnblóm)
**Status:** Reference. **Survey conducted live against the running Gungnir database on 2026-05-21**; numbers and schema below are real measurements, not aspirations.
**Last touched:** 2026-05-21
**Reads with:** `docs/SYSTEM_VISION.md` §8 (lineage — "the knowledge well on Gungnir"), `docs/architecture/ARCHITECTURE.md` §3.3, `docs/adapters/BRUNNR_BACKEND_MATRIX.md`, `docs/adapters/SMIDJA_INGEST_PATTERNS.md`.

---

## 1. Why this document exists

`docs/SYSTEM_VISION.md` names Gungnir as the **first concrete Well Ember can be tethered to**. Until Ember's own `pgvector` Brunnr adapter ships in Phase 8, Gungnir is also the **best living reference** for what a working Ember Well looks like — schema, sizes, latencies, content shape, KG-layer architecture.

This document captures what Gungnir *is*, today, against the live database, so future Ember work has ground truth.

---

## 2. Where Gungnir lives

| Field | Value |
|---|---|
| Hostname | `gungnir` (Tailscale MagicDNS) or `100.67.240.22` |
| Port | `5432` |
| Database | `knowledge` |
| User | `volmarr` |
| Auth | scram-sha-256 |
| SSL | Optional (tailnet is the trust boundary) |
| pg_hba | Accepts the full Tailscale CGNAT range `100.64.0.0/10` |

URL: `postgresql://volmarr:<secret>@gungnir/knowledge`

The canonical credentials guide is at `~/ai/KNOWLEDGE_DB_ACCESS.md` outside this repo. For Ember work, treat Gungnir as an **adapter target**, never as a hardcoded endpoint — `config/sources.example.yaml` is where Gungnir's URL belongs once Ember's pgvector Brunnr ships.

---

## 3. The schema, exactly as it stands

**Postgres version:** 18.3 on Ubuntu.
**Extensions in use:** `pgvector 0.8.1`, `pg_trgm 1.6`, `plpgsql`.

### 3.1 `documents` — one row per ingested source

```sql
documents (
  id              bigint     PRIMARY KEY DEFAULT nextval('documents_id_seq'),
  source          text       NOT NULL,
  title           text       NULL,
  content_type    text       NULL,
  hash            text       UNIQUE,
  metadata        jsonb      NOT NULL DEFAULT '{}',
  ingested_at     timestamptz NOT NULL DEFAULT now()
)
-- indexes:
--   documents_source_idx    (btree on source)
--   documents_metadata_gin  (GIN on metadata jsonb)
```

### 3.2 `chunks` — chunked text + embedding

```sql
chunks (
  id            bigint     PRIMARY KEY,
  document_id   bigint     NOT NULL REFERENCES documents(id),
  chunk_index   integer    NOT NULL,
  text          text       NOT NULL,
  embedding     vector(768) NULL,
  tsv           tsvector   NULL,        -- generated, full-text search
  char_start    integer    NULL,
  char_end      integer    NULL,
  UNIQUE (document_id, chunk_index)
)
-- indexes:
--   chunks_embedding_hnsw   (HNSW, vector_cosine_ops, 768-dim)
--   chunks_tsv_gin          (GIN on tsvector)
--   chunks_document_id_chunk_index_key  (covering)
```

### 3.3 The Skein KG (embedding-derived, cheap, broad)

```sql
skein_entities (
  id            bigint PRIMARY KEY,
  name          text NOT NULL,
  name_norm     text NOT NULL UNIQUE,
  kind          text NULL,
  mentions      integer NOT NULL DEFAULT 0,
  embedding     vector(768) NULL
)

skein_relations (
  id                bigint PRIMARY KEY,
  subject_id        bigint NOT NULL REFERENCES skein_entities(id),
  predicate         text NOT NULL,
  object_id         bigint NOT NULL REFERENCES skein_entities(id),
  sim               real NOT NULL,                 -- embedding similarity
  evidence_chunk_ids bigint[] NOT NULL DEFAULT '{}',
  UNIQUE (subject_id, object_id)
)

skein_entity_chunks (
  entity_id  bigint REFERENCES skein_entities(id),
  chunk_id   bigint REFERENCES chunks(id),
  PRIMARY KEY (entity_id, chunk_id)
)

skein_build (
  id           bigint PRIMARY KEY,
  fingerprint  text NOT NULL,        -- e.g. 'v1_c22952_22952_d33_33'
  finished_at  timestamptz NOT NULL DEFAULT now(),
  stats        jsonb NOT NULL DEFAULT '{}'
)
```

### 3.4 The LLM-extracted KG (precise, narrow, expensive)

```sql
kg_entities (
  id        bigint PRIMARY KEY,
  name      text NOT NULL,
  name_norm text NOT NULL,
  kind      text NULL,
  mentions  integer NOT NULL DEFAULT 0,
  UNIQUE (name_norm, kind)
)

kg_relations (
  id          bigint PRIMARY KEY,
  subject_id  bigint NOT NULL REFERENCES kg_entities(id),
  predicate   text NOT NULL,
  object_id   bigint NOT NULL REFERENCES kg_entities(id),
  chunk_id    bigint NOT NULL REFERENCES chunks(id),
  UNIQUE (subject_id, predicate, object_id, chunk_id)
)

kg_extraction_progress (
  chunk_id     bigint PRIMARY KEY REFERENCES chunks(id),
  status       text NOT NULL,           -- 'done' | 'failed'
  error        text NULL,
  processed_at timestamptz NOT NULL DEFAULT now()
)
```

---

## 4. The real numbers (as of 2026-05-21)

Measured live against `knowledge`:

| Quantity | Value |
|---|---|
| Documents | **95** |
| Chunks | **35 682** |
| Chunks with embedding | **35 682** (100% embedded) |
| Chunk text length (min / avg / max) | 4 / **1 684** / 2 000 chars |
| Embedding dim | **768** (`nomic-embed-text` via Ollama) |
| Skein entities | **276** |
| Skein relations | **855** |
| Skein entity↔chunk associations | **124 194** |
| Skein build fingerprint | `v1_c22952_22952_d33_33` |
| LLM-extracted KG entities | **366** |
| LLM-extracted KG relations | **176** |
| LLM-extracted chunks done / failed | **202 done / 7 failed** (out of 35 682 → mostly unprocessed) |
| Database size | **394 MB** |
| `chunks` table total size (incl. indexes) | **372 MB** (94% of DB) |
| `documents` table total size | 152 kB |
| Buffer cache hit (tables / indexes) | 97.0% / 99.8% |

**Content type breakdown of documents:** 42 `md`, 26 `web/markdown` (web fetches), 13 `json`, 9 `jsonl`, 5 `yaml`.

**Top sources by chunk count:**
- Viking combined dataset: 6 072 chunks
- 9th-century witches reports (Slavic / Finnish / Celtic / Viking-bondmaids / generic): ~17 000 chunks combined
- Norse gods JSON: 3 695 chunks
- Yggdrasil and Huginn and Muninn Theory: 416 chunks
- ~50 smaller sources

**Top Skein entities (with kind, mentions):**

| Entity | Kind | Mentions |
|---|---|---|
| 9th century | event | 5 474 |
| knowledge | concept | 4 246 |
| Tietäjä | group | 3 936 |
| fate | concept | 3 730 |
| Aesir | group | 3 689 |
| Runes | practice | 3 477 |
| Helheim | place | 3 307 |
| Odin | deity | 3 190 |
| wyrd | concept | 2 924 |
| Thor | deity | 2 126 |
| Freyja | person | 1 834 |

**Top Skein relation predicates:** `worshipped_as` (374), `created` (104), `depicted_as` (104), `associated_with` (57), `synonym_of` (41).

---

## 5. The two-KG-layer distinction (load-bearing for Ember)

This is the most architecturally interesting thing Gungnir teaches.

| Layer | Method | Cost | Yield | Quality signal |
|---|---|---|---|---|
| `skein_*` | **Embedding-derived** (Skein) | ~1/1000 of LLM-per-chunk | 276 entities × 855 relations across the full 35k corpus | High recall, *broad*. Includes false friends — e.g. `(GPT-2)–defeated→(GPT-3)` and `(Kubuntu)–received_from→(inbox)` at sim≈1.0. Co-occurrence without semantics. |
| `kg_*` | **LLM-extracted per chunk** | One LLM call per chunk | 366 entities × 176 relations across **only 202 chunks** processed so far | Precise, semantically clean — e.g. `(Yggdrasil)–draws_from→(Hvergelmir)`, `(Machine Learning)–includes→(Reinforcement Learning)`. Expensive — would cost orders of magnitude more compute to process all 35k chunks. |

The pattern that emerges: **Skein is the always-on cheap layer; KG is the curated expensive layer.** Ember's retrieval should use both when both are available. For the first slice (and for `sqlite_vec` Brunnrs), only chunks + embeddings ship. Skein and KG layers are *Phase 9+* — and entirely optional even then per the Vow of Smallness.

The relevant external repositories:
- [`hrabanazviking/skein-kg`](https://github.com/hrabanazviking/skein-kg) — the embedding-derived KG builder.
- [`hrabanazviking/skry-kg`](https://github.com/hrabanazviking/skry-kg) — query-time entity-neighborhood projection.
- [`hrabanazviking/bifrost-viewer`](https://github.com/hrabanazviking/bifrost-viewer) — the 3D viewer over a pgvector knowledge base, integrating both.

---

## 6. The hybrid-search pattern Gungnir uses

Gungnir's `ingest.py` (at `~/ai/ingest/ingest.py` on the Gungnir host) implements **reciprocal rank fusion** of vector search and full-text search. The Brunnr `pgvector` adapter for Ember should preserve the same shape:

```sql
-- (illustrative — the actual implementation lives in ingest.py)
WITH
  vec AS (
    SELECT id, row_number() OVER (ORDER BY embedding <=> $qvec) AS rank
    FROM chunks
    ORDER BY embedding <=> $qvec
    LIMIT 50
  ),
  fts AS (
    SELECT id, row_number() OVER (ORDER BY ts_rank(tsv, query) DESC) AS rank
    FROM chunks, plainto_tsquery('english', $qtext) AS query
    WHERE tsv @@ query
    ORDER BY ts_rank(tsv, query) DESC
    LIMIT 50
  ),
  fused AS (
    SELECT id, sum(1.0 / (60 + rank)) AS rrf_score
    FROM (
      SELECT id, rank FROM vec
      UNION ALL
      SELECT id, rank FROM fts
    ) AS u
    GROUP BY id
  )
SELECT c.*, d.title, f.rrf_score
FROM chunks c
JOIN documents d ON d.id = c.document_id
JOIN fused f ON f.id = c.id
ORDER BY f.rrf_score DESC
LIMIT $k;
```

The constant 60 is the standard RRF dampener. This is the pattern Ember's `pgvector` Brunnr will inherit when it ships in Phase 8.

---

## 7. Configuration shape Ember should expect

When the `pgvector` Brunnr ships, the operator's `config/storage.yaml` for a Gungnir-connected Ember will look approximately like:

```yaml
# config/storage.yaml — pgvector against Gungnir
backend: pgvector
pgvector:
  url: "postgresql://volmarr@gungnir/knowledge"
  secret_ref: "~/.ember/secrets/well.password"   # mode 600
  embedding_dim: 768
  vector_index: hnsw
  vector_metric: cosine
  schema: public
```

And the matching `config/sources.yaml` for ongoing ingest into Gungnir:

```yaml
# config/sources.yaml — Smiðja sources
default_well: pgvector
sources:
  - kind: local_files
    name: notes
    path: ~/notes/
    include: ["**/*.md", "**/*.txt"]
  - kind: url_fetch
    name: blog
    seed_urls: ["https://volmarrsheathenism.com/"]
    crawl_depth: 1
```

---

## 8. Gungnir health, briefly noted

From the live health check on 2026-05-21:

- **No invalid indexes.** No bloat. No constraint violations.
- **Connections healthy:** 11 total, 0 idle.
- **Buffer cache hit:** 97.0% tables / 99.8% indexes — well above the 95% threshold.
- **Duplicate-index hints:** four redundant single-column btree indexes are covered by their composite-key indexes (`chunks_document_idx` covered by `chunks_document_id_chunk_index_key`; same pattern in `kg_entities`, `kg_relations`, `skein_relations`). Not a bug — preserves single-column lookup speed in some cases. The Ember `pgvector` adapter's `schema.sql` should consider whether to ship the composite-only form or both, and document the trade.
- **Rarely-scanned indexes (informational):** `chunks_embedding_hnsw` has been scanned only 7 times since creation — Gungnir's *current* usage is dominated by ingest rather than retrieval. Once Ember starts asking real questions through `ember chat`, this will rise.

---

## 9. The two iron warnings from `~/ai/KNOWLEDGE_DB_ACCESS.md`

1. **Do not `ALTER ROLE volmarr WITH PASSWORD …`** — the secret is shared across multiple MCP configs, the `kb` helper, `~/.pgpass`. Rotating it silently breaks every tailnet node.
2. **Do not write to `documents` or `chunks` directly** — Gungnir's ingest pipeline (`~/ai/ingest/`) handles chunking, embedding, and the FTS trigger. Writing around it bypasses these.

These translate into Ember design: a `pgvector` Brunnr that points at an *existing* operator-managed Gungnir must operate in **read-mostly mode by default**. The Ember-managed `pgvector` Brunnr can write, but only via Smiðja — never via direct SQL from anywhere in `src/ember/`.

---

## 10. The Cartographer's closing word

> *Gungnir already does the thing the Vow of Tethered Grounding asks of any Ember. The Brunnr `pgvector` adapter is mostly a faithful translation — not a re-invention. The shape is proven. Ember just needs to plug into it cleanly.*

— Védis Eikleið

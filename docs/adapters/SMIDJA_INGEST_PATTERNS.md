# SMIDJA_INGEST_PATTERNS — Patterns for the Ingest Forge

**Voice:** Forge Worker (Eldra Járnsdóttir)
**Status:** Proposed — for ratification. Bootstrap-stage reference.
**Last touched:** 2026-05-21
**Reads with:** `docs/architecture/DATA_FLOW.md` §3, `docs/architecture/DOMAIN_MAP.md` §3, `docs/adapters/GUNGNIR_WELL_REFERENCE.md`.

---

## 1. Why Smiðja matters first

Smiðja is the most expensive flow in Ember. Bad chunking ruins retrieval. Bad batching ruins toaster-class hosts. A non-resumable journal ruins the operator's overnight ingest. The Forge Worker therefore writes Smiðja with more care than any other Ember subpackage.

The Gungnir corpus (35 682 chunks across 95 documents, see `GUNGNIR_WELL_REFERENCE.md`) is the closest thing Ember has to a known-good ingest output. The patterns here are calibrated against what Gungnir actually shipped.

---

## 2. The four ingest patterns

Every Smiðja source adapter implements one of four patterns. New source types must justify themselves against this set.

### 2.1 Pattern A — local files

The default. Walks a directory, picks up `.md`, `.txt`, `.json`, `.jsonl`, `.yaml`. Each file becomes one `Document`.

| Decision | Default | Why |
|---|---|---|
| File include | `**/*.md`, `**/*.txt`, `**/*.json`, `**/*.jsonl`, `**/*.yaml` | Matches Gungnir's mix (md 42, json 13, jsonl 9, yaml 5 of 95 docs). |
| File exclude | `**/.git/**`, `**/node_modules/**`, `**/.venv/**` | Avoid pathological subtrees. |
| Hash | SHA-256 of normalized content | Idempotency: re-ingest a directory and only changed files re-process. |
| Order | Sorted by mtime ascending | Stable, reproducible chunk_id assignment when feasible. |

### 2.2 Pattern B — URL fetch

Fetches a single URL or crawls one shallow. Each URL becomes one `Document` with `content_type='web/markdown'` (HTML converted to Markdown for consistency with Gungnir).

| Decision | Default | Why |
|---|---|---|
| Crawl depth | 0 (single URL) | Vow of Smallness; explicit opt-in to depth. |
| User-Agent | `EmberAgent/<version> (+toaster-class)` | Honest identification. |
| Respect `robots.txt` | Yes | Vow of Open Knowledge cuts both ways. |
| HTML→Markdown | yes, via `markdownify` or `trafilatura` | Better text-quality than raw HTML for chunking. |

### 2.3 Pattern C — shared well (mirror / sync)

Connects to *another* Ember's Well (Gungnir-shape Postgres, or another `sqlite_vec` file) and either reads it as a primary or syncs it locally.

| Decision | Default | Why |
|---|---|---|
| Mode | `read-only` | Avoid two-Ember write contention by default. |
| Snapshot trigger | Manual | Operator decides when to sync; no background drift. |
| Schema check | Embedding dim must match exactly | A 768-dim store and a 384-dim store cannot share an HNSW index. |

### 2.4 Pattern D — Project Nomad

Reads from an offline content bundle (Wikipedia, Kolibri, OpenStreetMap, etc.) mounted from Project Nomad. Each top-level resource becomes a `Document`; sub-resources become chunks.

The Nomad adapter is deferred to a later slice; the Cartographer's note in `SYSTEM_VISION.md` §8 names Nomad as Ember's flagship content source for the off-grid story.

---

## 3. Chunking — the Gungnir-aligned default

Gungnir's chunks have these measured properties (live as of 2026-05-21):

- Minimum: 4 chars (edge case — a tiny source).
- Average: **1 684 chars**.
- Maximum: **2 000 chars** (hard ceiling).
- All chunks include `char_start` / `char_end` for back-reference into the document.

The first-slice Ember chunker therefore targets:

| Setting | Value | Rationale |
|---|---|---|
| Hard max | 2 000 chars | Match Gungnir. Stays well under `nomic-embed-text`'s 8 192-token context. |
| Soft target | 1 500–1 800 chars | Average above; leaves headroom for paragraph-break preference. |
| Overlap | 0 chars (default), 100 chars (optional) | Gungnir uses no overlap. Overlap is a tunable per source, not a global. |
| Boundary preference | Paragraph break, then sentence, then word, then char | Standard. |
| Minimum chunk size | 200 chars | Below this, the chunk is merged into the previous one. (Gungnir has 4-char chunks; that is the artifact of a corner case, not a goal.) |

The chunker exposes `chunk_index`, `char_start`, `char_end` per chunk, matching Gungnir's `chunks` table so that Ember's `pgvector` adapter is bytewise compatible.

---

## 4. Embedding — the Gungnir-aligned default

| Setting | Value | Rationale |
|---|---|---|
| Model | `nomic-embed-text` | What Gungnir uses. Operators using Gungnir need the same model. |
| Dim | 768 | Implied by the model. The `embedding_dim` config key must match. |
| Endpoint | Ollama (default), configurable | `POST http://<funi_host>:11434/api/embed`. |
| Batch size | 32 | Conservative for Pi-class hosts. Larger if the host is bigger. |
| Backoff | exponential, max 30 s | One slow embedding call should not stall the rest. |
| On failure | mark chunk failed in journal, continue | Vow of Modular Authorship. |

If the operator chooses a different embedding model, the configured `embedding_dim` *must* match. Smiðja refuses to start with a mismatch — a 768-dim Well cannot ingest 384-dim chunks.

---

## 5. The journal — resumability is the Vow of Smallness in action

`~/.ember/state/smidja_progress/<job_id>.json` records, per ingest job:

| Field | Type | Meaning |
|---|---|---|
| `job_id` | uuid | Stable across resume. |
| `source_kind` | enum | `local_files` / `url_fetch` / `shared_well` / `nomad`. |
| `source_root` | path/URL | What we are ingesting. |
| `started_at` | iso8601 | First run. |
| `processed` | list of `{path_or_id, hash, status, chunk_count}` | What is done. |
| `failed` | list of `{path_or_id, error}` | What needs attention. |
| `last_heartbeat` | iso8601 | Updated every 30 s. |
| `committed_through_chunk` | int | Resumption point inside a single large source. |

When the operator re-runs `ember well ingest ~/notes/`, Smiðja:

1. Checks for an existing journal matching `source_root`.
2. If present, skips entries in `processed` and re-tries entries in `failed`.
3. Resumes mid-source from `committed_through_chunk` if applicable.
4. Updates `last_heartbeat`. If a stale heartbeat is found (>10 min old), assumes a crashed prior run and resumes from `committed_through_chunk`.
5. On clean completion, the journal is *moved* to `~/.ember/state/smidja_progress/done/<job_id>.json` (kept, not deleted, for audit).

This is what lets the operator leave `ember well ingest ~/library/` running on a Pi overnight without losing work if the power blips.

---

## 6. Idempotency rules

Every ingest is **content-addressed**. Re-running the same job over the same source content produces the same Well state:

- A `Document` is identified by its content hash. Re-ingesting an unchanged file is a no-op.
- A `Chunk` is identified by `(document_id, chunk_index)`. Re-chunking an unchanged document with the same chunker version produces the same chunks.
- An embedding regeneration is opt-in (`ember well reembed --model new-model`); it never happens silently.

The chunker version is stored as a `meta` jsonb field on `Document` for forward compatibility. When the chunker changes shape, ingest can detect and re-chunk only affected documents.

---

## 7. Failure modes Smiðja must handle cleanly

| Failure | Detection | Response |
|---|---|---|
| Well unreachable | Strengr returns `Disconnected` | Munnr reports clearly; Smiðja does not start. |
| Embedding endpoint unreachable | HTTP timeout | Backoff + retry; after N failures, mark chunk failed in journal, continue. |
| One file is malformed (encoding, parse error) | Source-adapter exception | Log + add to journal `failed`; continue with next file. |
| Disk full mid-ingest | OS error from Brunnr.add_chunks | Commit-then-fail: the latest batch was committed atomically, so progress is preserved up to the last successful batch. |
| `sqlite-vec` index corruption (very rare) | Read error on subsequent query | `ember well repair` (Phase 10 command) rebuilds the index from the chunk-row vectors. |

None of these take Ember down. The Vow of Modular Authorship and the Vow of Graceful Offline are the test that says so.

---

## 8. What this document is not

- **Not a tutorial.** Operators see `deploy/pi/INSTALL.md` for "how to run ingest on a Pi"; this doc is the contract Smiðja code follows.
- **Not Smiðja's `INTERFACE.md`.** That lives at `src/ember/well/smidja/INTERFACE.md` and is the executable contract. This doc is the *why* behind that contract.

— Eldra Járnsdóttir

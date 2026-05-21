# `ember.well.smidja/` — Smiðja

**The ingest forge.** Takes a content source, chunks it, calls the
embedding endpoint, deposits chunks into Brunnr — atomically per batch
with a resumable progress journal so overnight Pi ingests survive
power blips.

**Shipped:** Phase 3, slice 1 (version 0.1.0). The Phase-3 implementation
worked unchanged in slice 2 because both Brunnr backends (`sqlite_vec`,
`pgvector`) honor the same `BrunnrHandle` Protocol.
**Reads with:** `INTERFACE.md` for the public surface; `docs/architecture/DOMAIN_MAP.md` §3; `docs/adapters/SMIDJA_INGEST_PATTERNS.md` for chunking + journal patterns; `docs/adapters/GUNGNIR_WELL_REFERENCE.md` §3 for the chunker calibration anchor.

---

## What this subpackage owns

| Module | What's in it |
|---|---|
| `local_files.py` | Directory walker — the Phase-3 source. Defaults to `**/*.md` + `**/*.txt`; honors per-source include/exclude. |
| `chunker.py` | Gungnir-aligned chunker. Defaults: `max_chars=2000`, `target_chars=1684`, `min_chars=200`, `overlap_chars=0`, paragraph-boundary-preferring. |
| `embed_client.py` | `OllamaEmbedClient` — stdlib `urllib.request` POST to `/api/embed`. No httpx. Honors `OLLAMA_HOST` env override. |
| `journal.py` | Resumable progress journal at `~/.ember/state/smidja_progress/<job_id>.json`. Per-chunk-batch atomic write; survives crashes. |
| `pipeline.py` | The orchestrator. `ingest(path, config, brunnr, embedder, stdout)` → walks → chunks → embeds → deposits → returns `IngestSummary`. |

## What this subpackage does NOT own

- **Storage.** Brunnr's job. Smiðja calls `brunnr.add_document` /
  `brunnr.add_chunks` / nothing else.
- **The embedding model itself.** That lives in Ollama (or whatever
  `smidja.embedding.endpoint` points at). Smiðja just POSTs.
- **Backend selection.** The operator picks via
  `config.brunnr.backend`; Smiðja receives a `BrunnrHandle` already
  opened by the CLI dispatcher.
- **Reading from the Well.** Read paths live in `Brunnr.*search`.
  Smiðja writes only.

## Source adapters — current and planned

| Source | Status | Use case |
|---|---|---|
| `local_files` | **Shipped** (Phase 3) | The default. Walk a directory, ingest matching files. |
| `url_fetch` | **Deferred** per ADR 0013 §3 | Single URL or shallow crawl. Would reuse `fetch_url` tool's robots.txt + address-class refusals. |
| `shared_well` | **Deferred** per ADR 0013 §3 | Mirror from another Ember's Brunnr. Cross-Ember knowledge sharing. |
| `nomad` | **Deferred** per ADR 0013 §3 | Project Nomad bundles. |

Each of these is a future Phase-3-shaped commit when an operator
wants it.

## The Phase-3 ingest pipeline (the canonical flow)

Per `DATA_FLOW.md` §3:

```
Operator types `ember well ingest <dir>`
   ↓
[Munnr] resolves path, calls smidja.pipeline.ingest(...)
   ↓
[Smiðja] new job_id (UUID4); write empty journal entry
   ↓
   for each file matched by local_files.walk(path):
      hash = content_hash(file)
      if brunnr.has_document(hash) is not None: skip
      doc = Document(source=file, content_type=ext, hash=hash, metadata=...)
      doc_id = brunnr.add_document(doc)

      chunks = chunker.chunk(file_text)        # list[Chunk]
      for chunk in chunks:
         chunk.document_id = doc_id

      # Batch embed (size from EmbeddingConfig.batch_size, default 32):
      for batch in batched(chunks, 32):
         texts = [c.text for c in batch]
         vectors = embed_client.embed(texts)   # /api/embed
         for c, v in zip(batch, vectors):
            c.embedding = v
         brunnr.add_chunks(batch)              # transactional per batch
         journal.mark_batch_done(job_id, ...)
   ↓
[Smiðja] return IngestSummary(job_id, n_docs, n_chunks, n_failed, elapsed_s)
   ↓
[Munnr] render
```

## Failure semantics

- **Per-batch transactional writes.** Brunnr's `add_chunks` is one
  transaction; failure rolls back the whole batch. The journal
  records the failed batch; the next `ember well ingest <same-dir>`
  resumes from there.
- **Per-file hash check skips already-ingested content.** Re-running
  the same ingest is cheap and safe.
- **Embedding failures** (Ollama unreachable, malformed response) →
  Smiðja catches per-batch, marks failed in journal, continues with
  the next batch. The summary shows `n_failed`; the operator can
  diagnose via `ember doctor`.

## Layout

```
src/ember/well/smidja/
├── README.md
├── INTERFACE.md
├── __init__.py
├── local_files.py        # the slice-1 source
├── chunker.py            # Gungnir-aligned defaults
├── embed_client.py       # OllamaEmbedClient
├── journal.py            # resumable progress journal
└── pipeline.py           # the orchestrator
```

## Conventions (per ADR 0007 §2.6-2.9)

- **Stdlib-first.** `urllib.request` for HTTP; no httpx.
- **Atomic writes everywhere on disk.** `tempfile.NamedTemporaryFile`
  + `os.replace` for the journal; Brunnr handles the database side.
- **No swallowing exceptions silently.** Per-batch errors surface in
  the journal AND the IngestSummary's `n_failed` count.
- **Gungnir-aligned chunker defaults.** `target_chars=1684` matches
  the Gungnir corpus's measured mean per `GUNGNIR_WELL_REFERENCE.md`
  §4. Operators can override via `ChunkerConfig`.

## Slice-2 notes

No code changes. Smiðja worked unmodified against the new pgvector
Brunnr because both backends implement the same `add_document` /
`add_chunks` contract. The `pgvector` adapter's `add_chunks` is the
same shape as `sqlite_vec`'s — per-chunk dim check, transactional batch,
typed `BrunnrError` on failure.

## Related

- `INTERFACE.md` — public surface.
- `docs/architecture/DOMAIN_MAP.md` §3 — ownership.
- `docs/adapters/SMIDJA_INGEST_PATTERNS.md` — chunking + journal rules.
- `docs/adapters/GUNGNIR_WELL_REFERENCE.md` — the calibration anchor.
- `tests/unit/test_smidja_*.py` — chunker, embed_client, journal,
  local_files tests.
- `tests/integration/test_ingest_then_query.py` — round-trip from
  ingest to retrieval.

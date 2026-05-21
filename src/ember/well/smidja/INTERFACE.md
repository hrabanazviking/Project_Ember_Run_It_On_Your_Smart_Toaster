# INTERFACE — `ember.well.smidja`

## Module purpose

Take a content source, chunk it, embed it, deposit chunks into Brunnr.
Smiðja is *the* writer of the Well; nothing else writes embeddings.

## Public entry points (planned, Phase 3 onward)

- `ember.well.smidja.local_files.run(brunnr, job) -> IngestSummary`
- `ember.well.smidja.chunker.chunk(text, *, max_chars=2000, target=1684, min_chars=200, boundary="paragraph") -> list[Chunk]`
- `ember.well.smidja.embed_client.embed(texts) -> list[list[float]]`
- `ember.well.smidja.journal.open(job_id) -> JournalHandle`

## Inputs

A `BrunnrHandle` plus an `IngestJob` (source + options).

## Outputs

`IngestSummary(n_docs, n_chunks, n_failed, elapsed_s)`.

## Side effects

- Reads source content (filesystem walk, URL fetch, etc.).
- Calls the configured embedding endpoint (Ollama by default).
- Writes via `BrunnrHandle.add_document` / `add_chunks`.
- Writes the resumable journal at
  `~/.ember/state/smidja_progress/<job_id>.json`; moves it to `…/done/`
  on clean completion.

## Allowed imports

`ember.schemas`, `ember.well.brunnr` (through the public interface), an
HTTP client (`httpx`).

## Invariants

- Chunks default to ~1684 chars avg / 2000 max — Gungnir-aligned (see
  `docs/adapters/SMIDJA_INGEST_PATTERNS.md` §3).
- Re-running the same job over unchanged content is a no-op
  (content-addressed via hash).
- Per-chunk embedding failure does not fail the job; the chunk is
  journaled and reported in the summary.
- Embedding dim must match the Brunnr's configured dim; mismatch refuses
  before any work begins.

## Forbidden responsibilities

- Deciding which Brunnr to use (Strengr's job).
- Retrieval (Brunnr's job).
- The embedding model itself (it's an external service).

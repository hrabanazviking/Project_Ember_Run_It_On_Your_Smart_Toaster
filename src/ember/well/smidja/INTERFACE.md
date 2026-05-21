# INTERFACE — `ember.well.smidja`

## Module purpose

Take a content source, chunk it, embed it, deposit chunks into Brunnr.
Smiðja is *the* writer of the Well; nothing else writes embeddings.

## Public entry points (shipped Phase 3, 2026-05-21)

- `ember.well.smidja.local_files.run(brunnr, *, root, smidja_config=None,
  embed_client=None, ...) -> IngestSummary` — walks `root`, chunks +
  embeds + deposits via `brunnr`, journals progress, returns a summary.
  `embed_client` defaults to `OllamaEmbedClient(config=cfg.embedding)`.
- `ember.well.smidja.local_files.walk(root, *, include_suffixes, exclude_dirs)
  -> Iterator[ParsedFile]` — pure walker; no I/O against Brunnr.
- `ember.well.smidja.chunker.chunk(text, *, config=None) -> Iterator[Chunk]` —
  paragraph→sentence→word→char fallback splitter. Returned chunks have
  `text == original[char_start:char_end]` exactly.
- `ember.well.smidja.embed_client.OllamaEmbedClient(config, *, max_attempts,
  backoff_base_s, backoff_max_s)` — stdlib-urllib HTTP client. Failed
  batches return per-chunk `None` rather than raising.
- `ember.well.smidja.journal.Journal.open(config, source_kind, source_root,
  *, job_id=None)` — opens or resumes a journal. Atomic writes.
  `.complete()` moves the file to a `done/` subdirectory.

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

`ember.schemas`, `ember.well.brunnr` (through the public interface),
the standard library only for HTTP (we use `urllib.request` — no
`httpx` dependency in Phase 3 per the Vow of Smallness).

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

# INTERFACE — `ember.schemas`

## Module purpose

Type definitions, validation rules, version markers for on-disk shapes.
Used by two or more other subpackages.

## Public entry points (shipped Phase 2, 2026-05-21)

- `ember.schemas.errors` — `EmberError` base + per-realm classes
  (`SchemaError`, `ConfigError`, `WellError`/`BrunnrError`/`IngestError`,
  `ThreadError`/`StrengrError`, `SparkError`/`FuniError`/`HjartaError`/`MunnrError`).
  Plus the non-raised failure value `Disconnected(reason, since, detail)`
  with the `DisconnectReason` enum.
- `ember.schemas.config` — `EmberConfig` (top-level) composing
  `IdentityConfig`, `FuniConfig` (+ `FuniOllamaConfig`), `StrengrConfig`,
  `BrunnrConfig` (+ `SqliteVecConfig`, `PgVectorConfig`), `SmidjaConfig`
  (+ `ChunkerConfig`, `EmbeddingConfig`, `JournalConfig`), `LoggingConfig`
  (+ `LoggingDestination`). Enums: `BrunnrBackend`, `FuniRuntime`,
  `LogLevel`, `LogFormat`, `LogDestinationKind`, `BoundaryPreference`.
  Defaults are Gungnir-aligned where applicable (`embedding_dim=768`;
  chunker `max=2000`, `target=1684`).
- `ember.schemas.chunks` — `Document`, `Chunk` (with embedding as
  `tuple[float, ...]` for true immutability), `RetrievalHit`, `BrunnrStats`.
- `ember.schemas.episode` — `Episode` (operator_input, ember_reply,
  cited_chunk_ids, funi_model, well_disconnected, started_at, completed_at).
- `ember.schemas.funi` — `FuniReply`, `FuniHealth`, the non-raised failure
  value `Unavailable(reason, detail)` with `UnavailableReason` enum,
  `ContextItem` (with `ContextKind` enum), `ToolCall`, `FinishReason`
  enum (includes `REFUSED` for Vow-of-Honest-Memory clean refusals).

All dataclasses are `frozen=True, slots=True`. Stdlib only — no pydantic
dependency yet. Phase 2 ships with 66 shape-contract tests under
`tests/unit/test_schemas_*.py`.

## Inputs

Nothing — schemas are pure types.

## Outputs

Type instances and validation results.

## Side effects

None. Schemas never read files, open sockets, or import outside the
allowlist below.

## Allowed imports

Standard library only. Optional: `pydantic`, `typing_extensions`, `enum`.
**No** imports from `ember.*` — verified by
`tests/unit/test_schemas_import.py::test_schemas_do_not_import_sibling_ember_subpackages`.

## Invariants

- Every cross-subpackage exception class is defined here.
- Schemas do not define methods that do work; they define types.
- On-disk shape versions are integer-keyed and append-only.

## Forbidden responsibilities

- Business logic of any kind.
- Disk I/O.
- Network I/O.
- Anything that would require importing a runtime library.

# INTERFACE — `ember.schemas`

## Module purpose

Type definitions, validation rules, version markers for on-disk shapes.
Used by two or more other subpackages.

## Public entry points (planned, Phase 2)

- `ember.schemas.errors` — typed exception classes (`EmberError`,
  `BrunnrError`, `FuniError`, `IngestError`, `ConfigError`).
- `ember.schemas.config` — `EmberConfig`, `BrunnrConfig`, `FuniConfig`,
  `StrengrConfig`, `SmidjaConfig`.
- `ember.schemas.chunks` — `Document`, `Chunk`, `RetrievalHit`,
  `BrunnrStats`.
- `ember.schemas.episode` — `Episode` (a remembered turn).
- `ember.schemas.funi` — `FuniReply`, `FuniHealth`, `Unavailable`.

## Inputs

Nothing — schemas are pure types.

## Outputs

Type instances and validation results.

## Side effects

None. Schemas never read files, open sockets, or import outside the
allowlist below.

## Allowed imports

Standard library only. Optional: `pydantic`, `typing_extensions`, `enum`.
**No** imports from `ember.*`.

## Invariants

- Every cross-subpackage exception class is defined here.
- Schemas do not define methods that do work; they define types.
- On-disk shape versions are integer-keyed and append-only.

## Forbidden responsibilities

- Business logic of any kind.
- Disk I/O.
- Network I/O.
- Anything that would require importing a runtime library.

# `src/ember/well/`

The **Well realm**. Where Ember's memory lives and where her knowledge is
forged. Possibly local, possibly remote, possibly both at once.

Two subpackages:

- `brunnr/` — pluggable storage adapter layer. One subpackage per
  supported backend (`sqlite_vec` is the default).
- `smidja/` — ingest forge. Chunks content, calls the embedding endpoint,
  deposits into Brunnr.

## Status

Scaffold only. Phase 3 of the first slice ships the `sqlite_vec` Brunnr
and the `local_files` Smiðja.

## Reads with

- `docs/architecture/ARCHITECTURE.md` §3.3
- `docs/architecture/DOMAIN_MAP.md` §2-3
- `docs/adapters/BRUNNR_BACKEND_MATRIX.md`
- `docs/adapters/SMIDJA_INGEST_PATTERNS.md`
- `docs/adapters/GUNGNIR_WELL_REFERENCE.md`

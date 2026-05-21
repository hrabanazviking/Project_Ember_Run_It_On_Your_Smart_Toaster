# `src/ember/well/brunnr/`

**Brunnr** — the pluggable storage adapter layer. One subpackage per
supported backend:

- `sqlite_vec/` — the **default** (Phase 3 of the first slice).
- `pgvector/` — for shared wells; Gungnir-compatible (Phase 8).
- `qdrant/`, `chroma/`, `lancedb/` — later peers.

Every backend honors the same `BrunnrHandle` protocol declared in
`handle.py` (Phase 3). Choosing a backend is a configuration decision,
not a code change.

## Status

Scaffold only.

## Reads with

- `docs/architecture/DOMAIN_MAP.md` §2 (including §2.1 Brunnr's
  minimum-surface interface table)
- `docs/adapters/BRUNNR_BACKEND_MATRIX.md`
- `src/ember/well/brunnr/INTERFACE.md` (this folder)

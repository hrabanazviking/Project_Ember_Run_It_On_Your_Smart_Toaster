# `src/ember/well/smidja/`

**Smiðja** — the ingest forge. Takes a content source, chunks it, embeds
it, deposits chunks into Brunnr.

Planned source adapters:

- `local_files/` — directory walk (Phase 3).
- `url_fetch/` — single URL or shallow crawl (later).
- `shared_well/` — mirror from another Ember's Well (later).
- `nomad/` — Project Nomad bundles (later).

## Status

Scaffold only. Phase 3 ships `local_files`.

## Reads with

- `docs/architecture/DOMAIN_MAP.md` §3
- `docs/adapters/SMIDJA_INGEST_PATTERNS.md` — chunking + journal rules
- `docs/adapters/GUNGNIR_WELL_REFERENCE.md` — chunker calibration anchor
- `src/ember/well/smidja/INTERFACE.md`

# `src/ember/`

The Python implementation of Ember Agent.

## Layout — the Three Realms

```
src/ember/
├── schemas/        ← types only (the gravitational floor)
├── well/           ← Brunnr (storage) + Smiðja (ingest)
│   ├── brunnr/{sqlite_vec,pgvector,qdrant,chroma,lancedb}/
│   └── smidja/{local_files,url_fetch,nomad,shared_well}/
├── thread/         ← Strengr (the tether)
│   └── strengr/
├── spark/          ← Funi (LLM) + Hjarta (wizard) + Munnr (CLI)
│   ├── funi/{ollama,llamacpp,lmstudio,phi_silica,apple_foundation}/
│   ├── hjarta/
│   └── munnr/
└── cli/            ← `ember` console-script entry point
```

## Dependency law

```
schemas  ◄── well  ◄── thread  ◄── spark  ◄── cli
```

Acyclic and mechanical. See `docs/architecture/ARCHITECTURE.md` §2 for the
full rule.

## Status

Phase 1 (scaffolding) only. No code yet beyond `__init__.py` and a
`__main__.py` that raises `NotImplementedError` pointing at the first-slice
plan. See `docs/architecture/EMBER_FIRST_SLICE_PLAN.md` for the seven-phase
roadmap from here to a Pi5-shippable Ember.

## Lineage

The inherited Runa skeleton this folder replaces is archived at
`docs/archive/runa-inherited/src-skeleton/src/runa/`.

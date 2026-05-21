# `src/ember/spark/hjarta/`

**Hjarta** — the first-run setup state machine. The conversation that
wires Funi to Strengr to Brunnr the first time someone meets Ember.

Hjarta is a *finite, named* FSM — not a generative wizard. Its states are
enumerated, its transitions are unit-testable.

## States

```
Greet → ChooseFuni → DiscoverFuni → ChooseWell → ConfigureWell
      → TestRetrieval → NameEmber → WriteIdentity → Done
```

## Status

Scaffold only. Phase 6 of the first slice fills this in.

## Reads with

- `docs/architecture/DOMAIN_MAP.md` §6
- `docs/architecture/DATA_FLOW.md` §4 (the first-run rite)
- `docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md` §3 — Hjarta's auto-recommend
  heuristic data table
- `src/ember/spark/hjarta/INTERFACE.md`

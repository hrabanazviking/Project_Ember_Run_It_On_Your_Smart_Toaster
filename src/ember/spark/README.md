# `src/ember/spark/`

The **Spark realm**. Where Ember thinks on the device. The only realm
that **must** run with no network at all.

Three subpackages:

- `funi/` — local model runtime. One adapter per supported runtime
  (`ollama/` is the first-slice default).
- `hjarta/` — the first-run setup state machine.
- `munnr/` — the command-line surface (`ember chat`, `ember ask`, etc.).

## Status

Scaffold only. Phases 5 and 6 of the first slice fill these in.

## Reads with

- `docs/architecture/ARCHITECTURE.md` §3.1
- `docs/architecture/DOMAIN_MAP.md` §5-7
- `docs/architecture/DATA_FLOW.md` §2, §4
- `docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md`

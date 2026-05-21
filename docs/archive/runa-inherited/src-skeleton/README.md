# `docs/archive/runa-inherited/src-skeleton/`

The Python package skeleton inherited from the parent project
Runa-Agent-Digital-Being at Ember's fork moment (2026-05-19), preserved
here when `src/runa/` was archived on 2026-05-21 in favor of the new
`src/ember/` Three-Realms layout.

## What is here

```
runa/
├── __init__.py
├── __main__.py
├── README.md
├── adapters/{__init__.py, README.md, INTERFACE.md}
├── apps/{__init__.py, README.md, INTERFACE.md}
├── cli/{__init__.py, README.md, INTERFACE.md}
├── core/{__init__.py, README.md, INTERFACE.md}
├── migrations/{__init__.py, README.md, INTERFACE.md}
├── plugins/{__init__.py, README.md, INTERFACE.md}
├── runtime/{__init__.py, README.md, INTERFACE.md}
├── schemas/{__init__.py, README.md, INTERFACE.md}
├── services/{__init__.py, README.md, INTERFACE.md}
└── skills/{__init__.py, README.md, INTERFACE.md}
```

These files contain **no working code** beyond two-line `__init__.py`
stubs and a short `__main__.py`. The value is in the `README.md` and
`INTERFACE.md` drafts per subpackage, which encode the parent project's
expected boundaries.

## Why preserved

Per `MYTHIC_ENGINEERING.md`'s additive rule, nothing is deleted at the
moment of fork-shape change. The Runa skeleton is preserved here as a
reference any future contributor (or Volmarr in the parent project) can
consult.

## What replaces it

The Ember Python package now lives at `src/ember/` and is shaped by the
Three Realms (Spark / Thread / Well). See:

- `src/ember/README.md` — the new layout at a glance.
- `docs/architecture/DOMAIN_MAP.md` — per-subpackage ownership for the
  new shape.
- `docs/architecture/EMBER_FORK_DELTA.md` §2 — the disposition record.

The promotion event is recorded in `docs/DEVLOG.md` (the 2026-05-21
fork-delta entry) and in `docs/decisions/0006-ember-architecture-and-gungnir-survey-2026-05-21.md`.

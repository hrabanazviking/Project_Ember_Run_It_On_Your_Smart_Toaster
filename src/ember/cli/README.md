# `src/ember/cli/`

The `ember` console-script entry point.

The `[project.scripts]` table in `pyproject.toml` maps `ember` →
`ember.cli.main:main`. This subpackage is the thinnest possible router
between the entry point and Munnr.

## Status

Scaffold only. Phase 6 of the first slice fills in `main.py`.

## Reads with

- `docs/architecture/DOMAIN_MAP.md` §8
- `src/ember/cli/INTERFACE.md`

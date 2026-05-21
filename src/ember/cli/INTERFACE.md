# INTERFACE — `ember.cli`

## Module purpose

The `ember` console-script entry point.

## Public entry points (planned, Phase 6)

- `ember.cli.main.main() -> int` — declared by `[project.scripts]` in
  `pyproject.toml` as `ember = "ember.cli.main:main"`.

## Inputs

`sys.argv`.

## Outputs

Exit code.

## Side effects

Delegates entirely to `ember.spark.munnr`.

## Allowed imports

`ember.spark.munnr` only.

## Invariants

- Thinnest possible layer; no logic.
- `python -m ember` and `ember` resolve to the same function.

## Forbidden responsibilities

- Anything. CLI is a leaf.

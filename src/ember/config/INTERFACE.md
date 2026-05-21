# INTERFACE — `ember.config`

## Module purpose

The operator config-file loader. Reads `~/.ember/config/ember.{yaml,toml}`
if present, validates and coerces it into an `EmberConfig`, and merges
with environment-variable overrides on top of `EmberConfig()` defaults.

Per ADR 0008. This subpackage sits between `ember.schemas` (which
defines the dataclass shapes) and the consumers (Munnr, Hjarta,
Brunnr) — it owns the parse/coerce/merge pipeline and nothing else.

## Public entry points (shipped Phase 8, 2026-05-21)

- `ember.config.load_ember_config(config_root, *, file_override=None,
  skip_env=False) -> EmberConfig` — the canonical entry. Composes
  defaults → file → env. Returns a fully-populated `EmberConfig` or
  raises `ConfigError`.
- `ember.config.ConfigError` — re-export of `ember.schemas.errors.ConfigError`
  for one-import convenience.

## Public entry points (planned for Phase 9)

- `ember.config.write_ember_config(config_root, config) -> Path` —
  Hjarta uses this at WriteIdentity to lay down the initial
  `~/.ember/config/ember.yaml` with the operator's choices.

## Internal modules

- `loader.py` — `load_ember_config` entry; coordinates file probe +
  parse + overlay + coerce.
- `toml_loader.py` — `load_toml(path) -> dict` via stdlib `tomllib`.
- `yaml_loader.py` — `load_yaml(path) -> dict` via PyYAML when present;
  raises an operator-readable `ConfigError` when the YAML file exists
  but PyYAML is not installed.
- `overlay.py` — `apply_env_overrides(config) -> EmberConfig` (the
  Phase-7 `OLLAMA_HOST` logic moves here in Phase 9; for Phase 8 it
  lives here ready to be wired). `merge_dicts(base, overlay) -> dict`
  for file-on-defaults composition.
- `validate.py` — `coerce_to_dataclass(cls, data, path) -> instance`
  recursive coercion of dict values to dataclass types. Handles
  StrEnum, Path, `X | None`, `tuple[X, ...]`, nested dataclasses,
  primitives. Unknown keys raise `ConfigError` with
  `difflib`-suggested corrections.

## Inputs

A config root path (default `~/.ember/`). Optional file override and
env-skip flag for tests.

## Outputs

A fully-populated `EmberConfig` instance. **Never raises a generic
exception** — every failure mode is a `ConfigError` with an
operator-readable message including the path-in-tree of the bad value,
what was expected, and (when obvious) how to fix it.

## Allowed imports

`ember.schemas` (reads the type definitions) and the standard library.
Optional `pyyaml` is imported lazily inside `yaml_loader.py` and only
when a YAML file actually exists.

**No imports from `ember.well`, `ember.thread`, `ember.spark`, or
`ember.cli`.** The loader sits between schemas and consumers — never
inside any consumer.

## Invariants

- Partial config files merge into defaults; missing fields use
  `EmberConfig` defaults.
- Unknown keys are errors (with did-you-mean suggestions).
- Type mismatches are errors (with path, value, expected type).
- `Path`-typed fields are stored without `expanduser()`; consumers
  expand at use time.
- The loader is purely functional — no side effects beyond reading
  the file path it's pointed at.

## Forbidden responsibilities

- Writing the config file (Phase 9's `write_ember_config`).
- Validating semantics beyond type coercion (e.g. "embedding_dim must
  be positive" — that belongs to the consumer at use time).
- Per-consumer config (storage.yaml, sources.yaml, tools.yaml) — each
  consumer reads its own file via this same loader infrastructure
  when its phase ships.

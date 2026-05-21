# `ember.config/`

**The operator-config loader.** Reads YAML (or TOML) from
`~/.ember/config/ember.yaml` and produces a validated
`ember.schemas.config.EmberConfig` instance. Applies the four-layer
overlay (defaults → file → env → CLI) per ADR 0008 §2.3.

**Shipped:** Phase 8-9, slice 2 (version 0.1.5 "config loader live", 2026-05-21).
**Reads with:** `INTERFACE.md` for the public surface; `docs/decisions/0008-config-file-loader.md` for the design rationale; `config/ember.example.yaml` for the operator-facing template.

---

## What this package owns

- **YAML reading** (`yaml_loader.py`) — pyyaml is an optional extra;
  TOML reading uses stdlib `tomllib` (so the default install can
  still load configs).
- **TOML reading** (`toml_loader.py`) — stdlib-only path.
- **Dict-on-dict merging** (`overlay.py merge_dicts`) — recursive,
  overlay-wins.
- **Env-var overlay** (`overlay.py apply_env_overrides`) — narrow set:
  `OLLAMA_HOST` redirects both `funi.ollama.base_url` and
  `smidja.embedding.endpoint`; new env vars require an ADR per ADR
  0013 §2.2.
- **Type coercion + validation** (`validate.py coerce_to_dataclass`)
  — walks dataclass field annotations and coerces leaf values
  (StrEnum / Path / primitives / nested dataclasses / Mapping /
  Sequence / Optional). Raises `ConfigError` with operator-readable
  context on mismatch.
- **Atomic YAML write** (`writer.py write_ember_config`) — used by
  Hjarta at first-run to lay down the initial `ember.yaml`. Hand-
  rolled minimal emitter (no PyYAML dep on the write side); supports
  `identity:` + an `extras` mapping of additional sections.
- **The orchestrator** (`loader.py load_ember_config`) — public entry;
  composes the overlay layers; returns `EmberConfig`.

## What this package does NOT own

- **Default field values.** Those live on the dataclasses in
  `ember.schemas.config`. The loader's `coerce_to_dataclass` honors
  whatever defaults the dataclass declares.
- **Secret resolution.** That's `ember.well.brunnr.pgvector.secrets`
  (and any future per-adapter secret resolver). Secrets are never
  parsed from the YAML.
- **CLI flag parsing.** That's `ember.cli.main`. CLI overrides are
  applied *after* the loader returns, via dataclass `replace()`.

## Layout

```
src/ember/config/
├── __init__.py         # re-exports load_ember_config, write_ember_config
├── INTERFACE.md        # public surface contract (this dir's INTERFACE)
├── loader.py           # the orchestrator
├── yaml_loader.py      # PyYAML-optional YAML reader
├── toml_loader.py      # stdlib tomllib reader
├── overlay.py          # merge_dicts + apply_env_overrides
├── validate.py         # coerce_to_dataclass — type-walking validator
└── writer.py           # hand-rolled atomic YAML writer (Hjarta uses this)
```

## How it's used

### Production (CLI)

```python
from ember.config import load_ember_config

config = load_ember_config(config_root)
# overlay applied; env vars consumed; EmberConfig returned
```

### Test isolation

```python
# Skip env-var overlay entirely:
config = load_ember_config(config_root, skip_env=True)
```

### First-run write (Hjarta)

```python
from ember.config import write_ember_config

write_ember_config(
    config_root, identity,
    extras={"tools": {"enabled": True}},  # written under a `tools:` section
)
```

## Overlay order (ADR 0008 §2.3)

Innermost wins:

1. **Defaults** — dataclass `field(default=...)` values.
2. **File** — `~/.ember/config/ember.yaml` (or `.toml`); missing keys
   fall through to defaults.
3. **Environment variables** — `OLLAMA_HOST` (since Phase 7),
   `EMBER_WELL_PASSWORD` (Phase 12+).
4. **CLI flags** — `--allow-tools` / `--no-tools` are applied in
   `cli/main.py` via `dataclass.replace(config, tools=...)` after the
   loader returns.

A broken file (malformed YAML, unknown field) fails loud with a
`ConfigError` that names the offending key. Ember refuses to start
rather than running on partial config.

## Slice-2 extensions to the loader

The Phase-8/9 loader was extended in later slice-2 phases:

| Phase | Field added | Where |
|---|---|---|
| 10 | `FuniConfig.streaming: bool = True` | Phase 10, ADR 0009 |
| 12 | `PgVectorConfig.{secret_env, use_keyring, keyring_service, username, connect_timeout_s, read_only}` | Phase 12, ADR 0010 |
| 14 | `ToolsConfig` | Phase 14, ADR 0011 |
| 16 | `ToolsConfig` wired into `EmberConfig.tools` | Phase 16, ADR 0011 |

All of these landed without touching the loader code — the validator
walks the dataclass annotations, so new fields are picked up
automatically when their defaults are sensible.

## Failure modes (`ConfigError` reasons)

- **Unknown top-level section.** Operator typed `funnnnnni:` instead
  of `funi:`. Error names the section and lists known top-level
  sections.
- **Unknown field.** Operator typed `brunnr.embeding_dim` instead of
  `embedding_dim`. Error names the field path.
- **Type mismatch.** Operator wrote `embedding_dim: "seven"`. Error
  names the field, expected type, actual value.
- **Required field missing on selected variant.** Operator wrote
  `backend: pgvector` but omitted `pgvector.url`. Error names the
  field.

## Related

- `INTERFACE.md` — the public surface as the rest of Ember consumes it.
- `docs/decisions/0008-config-file-loader.md` — design rationale.
- `config/ember.example.yaml` — the operator template.
- `tests/unit/test_config_*.py` — 47 unit tests covering loader,
  overlay, validate, writer.

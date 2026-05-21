# ADR 0008 — Operator config-file loader

**Date:** 2026-05-21
**Status:** **Ratified 2026-05-21 by Volmarr** (under the slice-2 scope ratification — "go for slice 2 — bundle 1, 2, 3"; ADR-level ratification implicit in `EMBER_SECOND_SLICE_PLAN.md`).
**Author:** Mythic-Engineering session — Architect (Rúnhild Svartdóttir) + Forge Worker (Eldra Járnsdóttir).
**Supersedes:** None
**Superseded by:** —

---

## 1. Context

Slice 1 shipped Ember with a single configuration mechanism: hard-coded
defaults in `EmberConfig()`. Phase 7 added one escape hatch — the
`OLLAMA_HOST` environment variable in `cli/main.py._apply_env_overrides`.
That covers the most common non-default case (Ollama on a non-localhost
endpoint) but nothing else.

Slice 2 needs operators to be able to change:

- Funi model (e.g. `qwen2.5:3b-instruct` instead of `phi3:mini`).
- Brunnr backend (e.g. `pgvector` for a shared household Well).
- Embedding model and dim.
- Chunker defaults.
- Logging level + destinations.
- Tool enablement and approval policy (slice-2 ADR 0011 adds these
  knobs).
- pgvector connection URL + secret reference (slice-2 ADR 0010).

Doing all of that with environment variables alone would be hostile to
operators. A file is the right surface.

This ADR settles the file-format, overlay-order, and validation
decisions so the loader code (Phase 8 + Phase 9) has a clear contract.

## 2. Decision

### 2.1 File format: YAML primary, TOML secondary

**Decision:** `~/.ember/config/ember.yaml` is the canonical operator
configuration file. `~/.ember/config/ember.toml` is supported as an
alternative for operators who prefer TOML (or who cannot install
PyYAML).

If both exist, **YAML wins** and the loader emits a warning to stderr.

**Why YAML primary:**

- The existing operator-facing example (`config/ember.example.yaml`,
  shipped in slice 1) is already YAML. Changing the canonical format
  now would invalidate that example and any operator's notes.
- YAML's multi-line strings, comments, and anchor support fit
  hand-edited operator config better than TOML's table-of-tables
  approach for deeply nested config.
- Almost every Linux operator already has PyYAML installed via system
  packages or a sibling project.

**Why TOML supported:**

- Stdlib `tomllib` (Python 3.11+) reads it with zero dependency cost.
- A small contingent of operators dislike YAML's significant
  whitespace and the YAML 1.1 / 1.2 standard split.
- It's the format Hjarta's state prompts already use (read-only); the
  precedent is already in the codebase.

**Why YAML wins on tie:** the operator-facing example is YAML, so an
operator who edits the example to make their config and *also* drops a
TOML file in place probably intended the YAML.

### 2.2 PyYAML as an optional extra, not a required dep

**Decision:** PyYAML lives under `[project.optional-dependencies] config = ["pyyaml>=6.0"]`. Operators who don't install the extra get a
clear error if they try to use a YAML file: *"`ember.yaml` is present
but PyYAML is not installed. `pip install ember-agent[config]` or
rename to `ember.toml`."*

**Why optional:** the Vow of Smallness — a Pi 5 operator using only
defaults shouldn't need PyYAML on disk. The error message tells them
exactly how to opt in.

### 2.3 Overlay order

**Decision:** From highest priority (wins ties) to lowest:

1. **CLI arguments.** `--config-root`, `--ollama-host`, future flags.
2. **Environment variables.** `OLLAMA_HOST`, future `EMBER_*` overrides.
3. **Operator config file.** `~/.ember/config/ember.yaml` (or .toml).
4. **EmberConfig defaults** (from `src/ember/schemas/config.py`).

**Why:** This matches the convention every operator-facing tool in the
Ollama ecosystem already follows. CLI overrides env overrides file
overrides defaults. Surprise = 0.

**Concrete consequence:** the `OLLAMA_HOST` env-var override shipped in
Phase 7 stays exactly as-is. The new loader operates at layer 3; layer
2 keeps using the existing `_apply_env_overrides`. Phase 9 unifies the
two into a single `load_ember_config(config_root)` entry point that
composes all four layers.

### 2.4 Partial config files are merged into defaults

**Decision:** A config file does not need to be complete. Any field
absent from the file uses its `EmberConfig` default. Any nested object
absent from the file uses its sub-config's default constructor.

**Example:** an operator who only wants to change the Funi model writes:

```yaml
funi:
  ollama:
    model: "qwen2.5:7b-instruct"
```

— and everything else (`brunnr`, `smidja`, `strengr`, `logging`, ...)
falls through to defaults. They do *not* have to copy-paste the full
example file.

**Why:** operator ergonomics. The default `EmberConfig()` shape is the
documentation; the operator's file is the *delta* from default.

### 2.5 Unknown keys are errors

**Decision:** A config key not present in the matching dataclass raises
`ConfigError` with a path-style location: e.g. *"`funi.ollama.mdoel`:
unknown field for `FuniOllamaConfig`. Did you mean `model`?"*

**Why:** typo defense. An operator who writes `mdoel` instead of `model`
should see the error at load time, not silently get the default model.
The "did you mean" suggestion uses `difflib.get_close_matches` against
the known field names.

### 2.6 Type coercion at the field boundary

**Decision:** The loader recursively coerces:

| Annotated type | YAML/TOML source | Coerced to |
|---|---|---|
| `int`, `float`, `bool`, `str` | scalar | as-is (with type check) |
| `pathlib.Path` | string | `Path(value)` (no `expanduser()` — consumer expands) |
| `StrEnum` subclass | string | `EnumCls(value)` |
| `X \| None` | null or value | None or coerce as X |
| `tuple[X, ...]` | list | `tuple(coerce(X, item) for item in list)` |
| `Mapping[str, object]` | mapping | as-is |
| Nested dataclass | mapping | recurse |

**Why:** dataclass type annotations are the schema. The loader doesn't
need a separate schema language — it walks the dataclass tree and
coerces what it sees.

**Where this stops:** beyond type coercion, semantic validation
(*"embedding_dim must be positive"*, *"PgVectorConfig.url must be a
valid Postgres URL"*) is deferred to per-realm validators that live
near the consumer of the value (e.g. Brunnr's `pgvector` adapter
validates the URL when opening). Phase 8 ships the type-coercion layer
only.

### 2.7 Validation: stdlib by default, pydantic opt-in

**Decision:** The default validation layer uses stdlib only —
hand-rolled coercion + ConfigError messages. PyYAML aside, no
validation dep ships in the default install.

`pydantic` is available under `[project.optional-dependencies]
validation = ["pydantic>=2.7"]` for operators who want richer error
messages and structured violation reporting. When the loader detects
the optional dep is present, it routes coercion through a thin pydantic
adapter that mirrors the stdlib semantics but produces friendlier
errors.

**Why opt-in:** the Vow of Smallness. Most operators will never see a
config error after first launch. Paying ~5 MB of pydantic + its deps
on every Pi install for a feature most operators never trigger is the
wrong default.

### 2.8 Error message style

**Decision:** Every `ConfigError` message includes:

- The path-in-tree of the bad value (e.g. `funi.ollama.temperature`).
- The actual value that failed (e.g. `"two"`).
- What was expected (e.g. `float`).
- The operator-facing fix when one is obvious.

**Example:**

```
ConfigError: funi.ollama.temperature: expected float, got "two".
  Edit ~/.ember/config/ember.yaml and set funi.ollama.temperature to
  a number like 0.7.
```

**Why:** an operator editing YAML for the first time needs to be told
the path, the bad value, and the fix. *"ValidationError at line 42"*
is for developers, not operators.

### 2.9 Where the loader lives

**Decision:** A new subpackage `src/ember/config/` between
`ember.schemas` and the consumers (Munnr, Hjarta, Brunnr).

| Module | Responsibility |
|---|---|
| `loader.py` | Public `load_ember_config(config_root)` entry. Composes file → env → defaults via `overlay.py`. |
| `toml_loader.py` | `load_toml(path) -> dict` via stdlib `tomllib`. |
| `yaml_loader.py` | `load_yaml(path) -> dict` via PyYAML when available; clear error otherwise. |
| `overlay.py` | Merges defaults dict + file dict + env dict. |
| `validate.py` | Recursive `coerce_to_dataclass(cls, data, path)` returning a typed instance or raising `ConfigError`. |

**Dependency direction:** `ember.config` may import `ember.schemas`
(reads the type definitions) and the standard library. It must NOT
import `ember.well`, `ember.thread`, `ember.spark`, or `ember.cli` —
the loader sits between schemas and consumers, never inside them.

## 3. Consequences

### 3.1 What becomes true after Phase 8 (this ADR's part 1)

- `src/ember/config/` exists with the five modules above.
- `load_ember_config(config_root)` returns an `EmberConfig` populated
  from `~/.ember/config/ember.{yaml,toml}` if present, else from
  defaults.
- Unknown keys, type mismatches, and missing required fields all
  produce operator-readable `ConfigError`s.
- `cli/main.py` is **not yet wired** — its existing `EmberConfig()` +
  `_apply_env_overrides` keep working in parallel. Phase 9 unifies.

### 3.2 What becomes true after Phase 9 (this ADR's part 2)

- `cli/main.py` calls `load_ember_config(config_root)` instead of
  `EmberConfig()`. The phase-7 `_apply_env_overrides` moves into
  `overlay.py` as the env layer.
- Hjarta writes `~/.ember/config/ember.yaml` at the WriteIdentity step
  with the operator's wizard answers, defaults for everything else.
- `config/ember.example.yaml` is the canonical operator-editable copy.
- `config/storage.example.yaml` and `config/sources.example.yaml` ship
  as alternative-shape examples (per `docs/REPO_MAP.md` §config/).

### 3.3 Risks

- **Operator typos in YAML are common.** The unknown-key error +
  did-you-mean suggestion covers the most-frequent case. Semantic
  validation (e.g. "this URL doesn't parse") is deferred to consumers
  but they should produce operator-readable errors too.
- **YAML 1.1 vs 1.2 surprises.** PyYAML 6 defaults to YAML 1.1
  (which parses `yes`/`no` as booleans, `01` as octal). The example
  file should avoid the ambiguous corners; this ADR does not change
  PyYAML's load mode.
- **Two formats means two test surfaces.** The loader tests run the
  same fixtures through both YAML and TOML paths to confirm
  equivalence.
- **The pydantic opt-in might rot.** If nobody uses it, the
  pydantic-aware code path drifts. Mitigation: integration test under
  a `requires_pydantic` marker runs the full loader fixtures through
  the pydantic path and asserts identical results.

## 4. Alternatives considered

| Alternative | Why not |
|---|---|
| TOML only (no YAML) | Slice 1 already shipped `config/ember.example.yaml`. Reversing format now invalidates the operator-facing example and any docs that reference it. |
| YAML required (not optional) | Violates Vow of Smallness — most operators never edit config; making them install PyYAML to use defaults is gratuitous. |
| pydantic required (not optional) | Same reason. ~5 MB of dep cost for a feature most operators never trigger. |
| Single-source-of-truth pydantic schema (no dataclasses) | Phase 2 already ratified `dataclasses` per ADR 0007 §2.5. Switching to pydantic here would mean rewriting every schema module. |
| Read JSON instead of YAML/TOML | JSON has no comments. Operator config files want comments. |
| INI / .env format | Loses nested-structure expressivity; would need flattening conventions like `funi.ollama.model = phi3:mini` that fight YAML's natural shape. |
| Per-realm config files (no overlay) | An operator who wants to change `funi.ollama.model` shouldn't have to know which file to edit. One file with one shape. |

## 5. Open follow-ups

- **ADR 0008b (optional):** add file-watching for hot reload. Out of
  scope for slice 2; an operator restart-on-config-change is the
  default. Hot reload becomes relevant if/when long-running services
  emerge.
- **Per-environment files (e.g. `ember.dev.yaml` overlay over
  `ember.yaml`):** out of scope for slice 2. Operators who want this
  pattern can use env-vars or shell aliases for now.
- **Schema export for IDE completion** (e.g. JSON Schema generation
  from the dataclass tree, served to YAML language servers): out of
  scope; Phase 8's loader produces the errors at runtime, which is
  sufficient for first-use UX.

## 6. Provenance

This ADR was authored at the start of Phase 8 of
`EMBER_SECOND_SLICE_PLAN.md`. The implementation lands in the same
commit as this document.

— Eirwyn Rúnblóm (Scribe), with Rúnhild (Architect) and Eldra (Forge Worker)

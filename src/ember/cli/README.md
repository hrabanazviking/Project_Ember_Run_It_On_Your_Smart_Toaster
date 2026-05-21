# `ember.cli/`

**The `ember` console-script entry point.** The thinnest possible
router between `[project.scripts] ember = "ember.cli.main:main"` and
the Munnr subcommands. CLI parsing only — behaviour lives in
`ember.spark.munnr`.

**Shipped:** Phase 6, slice 1 (version 0.1.0). Extended Phase 7
(`OLLAMA_HOST` env override → config-file path); Phase 9 (`config
loader integration`); Phase 16 (`--allow-tools` / `--no-tools` flags).
**Reads with:** `INTERFACE.md` for the public surface; `docs/architecture/DOMAIN_MAP.md` §8.

---

## What this subpackage owns

- **The argparse tree** (`_build_parser` in `main.py`). Every
  subcommand and flag.
- **The dispatch logic** (`main(argv)` in `main.py`). Reads
  `args.command`, calls the matching `ember.spark.munnr.<name>.run(...)`.
- **The first-launch redirect.** When a subcommand needs an identity
  (`chat`, `ask`) and one hasn't been written yet, dispatcher calls
  `setup.run` (which runs Hjarta) first, then reloads the config
  and proceeds.
- **The CLI overlay onto config.** `_apply_tool_overrides` is the
  slice-2 single-flag-per-invocation overlay; applied after every
  config load (initial + post-Hjarta).

## What this subpackage does NOT own

- **Subcommand behaviour.** Every subcommand's `run(...)` lives in
  the matching Munnr module.
- **Config loading.** That's `ember.config.load_ember_config`.
- **Argument validation.** Argparse handles structural validation;
  semantic validation (e.g. "is this path a directory?") lives in
  the consuming `run(...)`.
- **Help text.** Per-subcommand `help=` strings live next to their
  argument declarations; long-form help lives in `deploy/pi/INSTALL.md`.

## Subcommands (slice 2)

| Command | Run target | Slice-2 changes |
|---|---|---|
| `ember chat` | `munnr.chat.run` | Phase 11 streaming consumer; Phase 16 tool loop. |
| `ember ask "..."` | `munnr.ask.run` | Same one-shot semantics; tool calls honored if `tools.enabled` is true. |
| `ember well ingest <path>` | `munnr.ingest.run` | Unchanged from slice 1 — works against both Brunnr backends. |
| `ember well status` | `munnr.status.run` | Unchanged. |
| `ember doctor` | `munnr.doctor.run` | Unchanged. |
| `ember setup [--reset]` | `munnr.setup.run` | Phase-16 Hjarta ADVANCED_TOOLS branch surfaces here. |

## Flags

| Flag | Scope | Purpose |
|---|---|---|
| `--config-root PATH` | Global | Where Ember's identity, secrets, well, and state live. Default `~/.ember/`. |
| `--allow-tools` | Global, mutually exclusive | **Slice 2.** Force `tools.enabled: true` for this invocation, overriding the config-file value. |
| `--no-tools` | Global, mutually exclusive | **Slice 2.** Force `tools.enabled: false` for this invocation. |
| `--reset` (under `setup`) | Subcommand | Discard any existing identity and run Hjarta from scratch. |

## The dispatch flow

```
ember.cli.main.main(argv) called by setuptools entry point
   ↓
parser = _build_parser()
args = parser.parse_args(argv)

config = load_ember_config(args.config_root)
config = _apply_tool_overrides(config, args)    # CLI overlay

if args.command in {"chat", "ask"} and not has_identity(config_root):
   setup.run(...)                               # → Hjarta
   config = load_ember_config(args.config_root) # reload (Hjarta may have written tools.enabled)
   config = _apply_tool_overrides(config, args)

dispatch on args.command:
   "chat"          → munnr.chat.run(config, config_root, stdout)
   "ask"           → munnr.ask.run(text, config, config_root, stdout)
   "setup"         → munnr.setup.run(config, config_root, reset, stdout)
   "doctor"        → munnr.doctor.run(config, stdout)
   "well ingest"   → munnr.ingest.run(path, config, stdout)
   "well status"   → munnr.status.run(config, stdout)
```

## Layout

```
src/ember/cli/
├── README.md
├── INTERFACE.md
├── __init__.py
└── main.py             # _build_parser, main, _apply_tool_overrides
```

## Slice-2 changes

| Phase | What landed |
|---|---|
| 7 | `OLLAMA_HOST` env-var override path added (now superseded by Phase 9's full config loader, but the env-var honor remained). |
| 9 | `load_ember_config(config_root)` call inserted at the top; broken config fails loud and exits with a clear error. Reload after Hjarta picks up wizard choices for the same invocation. |
| 16 | `--allow-tools` / `--no-tools` mutually-exclusive flags; `_apply_tool_overrides` applied after both initial load and post-Hjarta reload. |

## Failure semantics

- **`ConfigError` at load time** → write to stdout, exit 1.
- **Subcommand `run(...)` returns** an `int` exit code; that's what
  the dispatcher returns.
- **Unknown subcommand** is unreachable per argparse `required=True`,
  but the dispatcher has a defensive `parser.print_help` + `return 2`
  fallback.

## Related

- `INTERFACE.md` — public surface.
- `docs/architecture/DOMAIN_MAP.md` §8 — ownership.
- `tests/unit/test_cli_tool_flags.py` — slice-2 flag overlay tests.
- The Munnr subpackage's modules — where the actual work happens.

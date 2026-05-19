# src/runa/

The Runa Python package. This is the entire runtime.

## Subpackages

| Subpackage | Role |
|---|---|
| `cli/` | The `runa` command — argument parsing, subcommand dispatch. Thin. Calls into `runtime/`. |
| `runtime/` | Process supervision: start/stop/status/doctor/repair. The control plane that other surfaces (CLI, API) call. |
| `core/` | The agent itself — kernel, event bus (VERÐANDI), task ledger (Skuld), memory OS (Muninn), world model (WYRD bridge), emotional state, model router, tool forge, identity. The heart. |
| `services/` | Long-running processes: gateway, worker, GUI, voice. Each service is a thin wrapper around `core/` plus its own I/O. |
| `apps/` | User-facing surface implementations (gateway_app, cli_app, gui_app, voice_app, worker_app). |
| `adapters/` | Connections to specific external systems: Discord, Telegram, Matrix, MCP, Home Assistant, OpenRouter, Ollama, LM Studio, … |
| `plugins/` | Plugin loader, plugin sandbox, plugin discovery. Third-party plugins themselves live outside this repo. |
| `skills/` | Agent-facing capabilities — first-party "things Runa can do" that are not large enough to be subsystems and not external enough to be adapters. |
| `schemas/` | Pydantic models, dataclasses, type definitions shared across subpackages. |
| `migrations/` | Versioned migrations for the on-disk state stores: memory, task ledger, world model. |

## Dependency direction (strict)

```
cli  ─►  runtime  ─►  core  ─►  schemas
                       │
                       └─►  services / apps / adapters / plugins / skills
```

Higher boxes import lower boxes, never the reverse. `core` is the gravitational centre; everything outside `core` is allowed to depend on `core` but `core` may not depend on anything outside itself except `schemas` and `migrations`.

Each subpackage has its own `INTERFACE.md` declaring its public surface and invariants. Read those before adding anything new.

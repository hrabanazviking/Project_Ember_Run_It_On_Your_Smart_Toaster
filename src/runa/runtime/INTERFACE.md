# INTERFACE — `runa.runtime`

**Status:** Stub — no code yet.
**Owner role:** Architect.
**Reads with:** `docs/architecture/DOMAIN_MAP.md` §4.

## Purpose

Process supervision and the control-plane commands: start, stop, restart, status, doctor, logs, snapshot, restore, migrate, memory check, config validate.

## Public surface

Planned:

| Function / class | Caller | Purpose |
|---|---|---|
| `runa.runtime.commands.start(profile=None)` | `runa.cli`, `runa.services` | Start the agent (or a named service) in the current process. |
| `runa.runtime.commands.stop(graceful=True)` | `runa.cli` | Graceful or immediate stop. |
| `runa.runtime.commands.status() -> StatusReport` | `runa.cli` | One-shot health snapshot. |
| `runa.runtime.commands.doctor() -> DoctorReport` | `runa.cli` | Long-form diagnostic walk: config, migrations, stores, adapters, plugins. |
| `runa.runtime.commands.logs(filter, follow=False)` | `runa.cli` | Tail or grep structured logs. |
| `runa.runtime.commands.snapshot(name)` / `restore(name)` | `runa.cli` | Operator-asked state snapshot/restore. |
| `runa.runtime.commands.migrate()` | `runa.cli` | Run any pending migrations across all stores. |
| `runa.runtime.commands.memory_check(repair=False)` | `runa.cli` | Muninn integrity check, optionally repair. |
| `runa.runtime.commands.config_validate(path)` | `runa.cli` | Validate a config file without starting anything. |
| `runa.runtime.supervisor.Supervisor` | `runa.services` | Process supervisor: spawn, watch, restart, drain. |

## Invariants

- **Every command logs what it did** with an explicit `command_invoked` audit-log entry.
- **Destructive operations require explicit flags** — `--apply`, `--force`, or `--really`. Dry-run is the default.
- **No command silently mutates `~/.runa/`** without an audit-log entry.
- **The supervisor is the last fallback.** If the supervisor dies, the OS (`systemd` / equivalent) is the next layer.

## Allowed callers

`runa.cli`, `runa.services`, tests.

## Allowed callees

`runa.schemas`, `runa.migrations`, `runa.core`.

## Failure semantics

A command failure returns a non-zero exit code and writes a structured error to the audit log. The supervisor catching a kernel crash records the crash and either restarts (with backoff) or escalates per the configured policy.

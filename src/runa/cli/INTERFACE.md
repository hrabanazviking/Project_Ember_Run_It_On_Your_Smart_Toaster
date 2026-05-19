# INTERFACE — `runa.cli`

**Status:** Stub — no code yet.
**Owner role:** Architect.
**True Name:** **Munnr** (the mouth — where Runa is summoned by command).
**Reads with:** `docs/architecture/DOMAIN_MAP.md` §5, `docs/operations/RUNA_PROJECT_FILE_ORGANIZATION_AND_STARTUP_GUIDE.md` (the source authority for the CLI shape).

## Purpose

The `runa` command-line entry point. Argument parsing, subcommand dispatch, terminal output formatting.

## Public surface

The CLI is a leaf — no other subpackage imports from it. The user-visible surface is the `runa` command:

```
runa start [--profile <name>]
runa stop  [--graceful | --immediate]
runa restart
runa status
runa doctor
runa logs [--filter <expr>] [--follow]
runa shell             ← interactive Munnr shell
runa chat              ← one-shot chat
runa worker            ← run worker service in foreground
runa api               ← run gateway service in foreground
runa gui               ← run GUI app in foreground
runa voice             ← run voice service in foreground
runa memory check [--repair]
runa memory backup <name>
runa state snapshot <name>
runa state restore <name>
runa state migrate
runa config validate [<path>]
runa config init [--profile <name>]
runa version
```

The entry-point function is `runa.cli.main:main` (referenced by `pyproject.toml [project.scripts]`).

## Invariants

- **The CLI does no work.** It parses, dispatches to `runa.runtime`, formats results.
- **`--help` is always meaningful** — every subcommand has a one-line summary and a usage example.
- **Exit codes are documented.** `0` success, `1` general failure, `2` argument error, `3` config error, `4` migration error, `5` health-check failure, `64+` reserved.
- **No subcommand silently performs a destructive operation.** Every destructive subcommand requires `--apply` or an explicit confirmation flag.

## Allowed callers

None — `runa.cli` is a leaf.

## Allowed callees

`runa.schemas`, `runa.runtime`.

## Failure semantics

Parse failures print help and exit `2`. Subcommand failures bubble exit codes up from `runa.runtime`.

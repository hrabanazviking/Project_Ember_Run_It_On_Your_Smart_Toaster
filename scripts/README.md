# scripts/

**Helper scripts that humans invoke at the shell.** The official
operator-facing CLI is `ember` (see `src/ember/cli/`); these scripts
are for things that don't belong in the agent's runtime surface —
developer convenience, ops maintenance, and one-shot data fixups.

**Last touched:** 2026-05-21 (slice 2 ratified).

---

## Subfolders

| Folder | Holds | Slice-2 state |
|---|---|---|
| `dev/` | Developer convenience: format, lint, full-test, regenerate fixtures, rebuild lockfile. | Scaffold only. Slice-1 + slice-2 work used direct invocations (`.venv/bin/pytest -q`, `ruff check src tests`). |
| `maintenance/` | Operator maintenance: rotate logs, vacuum memory store, prune cache, export/import state bundles. | Scaffold only; slice-2 doesn't ship maintenance scripts (the operator's manual `pg_dump` / `sqlite3 .backup` / `gzip ~/.ember/state/tool_audit/*.jsonl` is the current path). |
| `one_shot/` | Single-purpose migrations and rare data fixups. Each script is dated and self-documenting in its docstring. | Scaffold only; no migrations needed yet — both slice-1 and slice-2 schemas are version 1 with no in-place upgrade path. |

---

## Why these are scaffolds

- **Slice 1 + 2 were built without supporting scripts.** Every
  developer task was either a single shell invocation
  (`pytest -q`, `ruff check src tests`) or part of a slash-command
  workflow.
- **Operator maintenance** is currently manual per
  `deploy/pi/INSTALL.md` §11 ("Update / reset") — operators back
  up `~/.ember/well/store.db` by `cp`, prune audit log by `find ... -mtime +30 -delete`, etc.
- **One-shot migrations** become necessary when a schema version
  bumps. Slice-2 didn't bump any schema. The first time a slice
  needs migration (e.g. an `episodes` table column addition), that
  migration script lands here.

---

## Rules (when scripts land)

- **Every script has a `--help` and a top-of-file docstring**
  explaining what it does and what it touches.
- **Destructive scripts default to dry-run** and require `--apply`
  to actually mutate.
- **Scripts call the official `ember` CLI** rather than
  re-implementing kernel logic. The CLI is the supported boundary;
  scripts are short shell-level glue, not parallel codebases.
- **One-shot scripts are dated.** Filename pattern:
  `one_shot/YYYY-MM-DD-<short-name>.py`. After the operator has
  applied them, the file stays in the repo as forensic evidence —
  never deleted.

---

## What's NOT here yet

| Script kind | Why it's not here yet |
|---|---|
| `dev/run-tests.sh` | The current `pytest -q` invocation is short enough not to need wrapping. |
| `dev/fmt.sh` | Same — `ruff check --fix src tests` is the actual command. |
| `maintenance/backup-well.sh` | Operators do this manually right now; would land if/when multi-host deployments become common. |
| `maintenance/prune-audit.sh` | Slice-3 candidate (per ADR 0013 §6); not yet shipped. |
| `one_shot/2026-MM-DD-<migration>.py` | No schema migrations needed yet. |

If you need one of these and it doesn't exist, file an issue with the
use case.

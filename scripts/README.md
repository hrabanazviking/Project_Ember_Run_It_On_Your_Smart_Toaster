# scripts/

Helper scripts that humans invoke at the shell. The official CLI is `runa` (see `src/runa/cli/`); these scripts are for things that don't belong in the agent's runtime surface.

## Subfolders

| Folder | Holds |
|---|---|
| `dev/` | Developer convenience: format, lint, full-test, regenerate fixtures, rebuild lockfile. |
| `maintenance/` | Operator maintenance: rotate logs, vacuum memory store, prune cache, export/import state bundles. |
| `one_shot/` | Single-purpose migrations and rare data fixups. Each script is dated and self-documenting in its docstring. |

## Rules

- Every script has a `--help` and a top-of-file docstring explaining what it does and what it touches.
- Destructive scripts default to dry-run and require `--apply` to actually mutate.
- Scripts call the official `runa` CLI rather than re-implementing kernel logic.

# tools/

Developer tooling that operates *on the repository itself* rather than as part of the running agent.

## Subfolders

| Folder | Holds |
|---|---|
| `repo/` | Repo-shape checks: link-checker, README consistency, ORIGINS.md drift detector, INTERFACE.md presence validator. |
| `diagnostics/` | Live-system diagnostics: snapshot a running Runa's state, dump event bus traffic, inspect memory store integrity. |
| `importers/` | One-way importers that pull material from other Volmarr projects (NSE, MindSpark, WYRD, …) into this repo. Used carefully, never on schedule. |

## Rules

- Tools never modify deployed state. Read-only by default; mutations are opt-in and logged.
- Tools live here, not in `scripts/`, because they reason about the repository or a live agent rather than performing routine operator tasks.

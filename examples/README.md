# examples/

Reference material that shows how things are *meant* to look. Read this folder to learn the shape; copy from it when starting your own.

## Subfolders

| Folder | Holds |
|---|---|
| `configs/` | Fully-worked example configurations for common deployment shapes. |
| `sessions/` | Transcripts of meaningful Runa sessions, used as documentation and as evaluation fixtures. |
| `skills/` | Example skill packages a third party could fork. |
| `plugins/` | Example plugins a third party could fork. |

## Rules

- Examples must actually run against the current `src/runa/`. CI verifies this.
- No example contains real secrets or real personal data. Use obvious placeholders (`OPENROUTER_API_KEY=sk-fake-example`).

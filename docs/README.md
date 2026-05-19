# docs/

All written material lives under `docs/`. Source code lives under `src/`. The split is hard: nothing under `docs/` ever runs, nothing under `src/` is ever the primary place to learn how Runa works.

## Subfolders

| Folder | Holds |
|---|---|
| `architecture/` | Canonical ME files: `DOMAIN_MAP.md`, `ARCHITECTURE.md`, `DATA_FLOW.md`. Big-picture system shape. |
| `operations/` | Installation, startup, shutdown, repair, backup, observability runbooks. |
| `development/` | How to contribute, local dev setup, test-running, coding conventions specific to Runa. |
| `design/` | Long-form design explorations, idea harvests, deep dives that informed architecture. |
| `security/` | Threat model, trust boundaries, secrets handling, sandbox policy. |
| `adapters/` | Per-adapter contracts (Discord, Telegram, Matrix, Home Assistant, MCP, …). |
| `plugins/` | Plugin author guide, plugin contract, examples. |
| `decisions/` | Architecture Decision Records (one ADR per major commitment). |
| `philosophy/` | Ethos, worldview, the Mythic + Heathen framing that gives Runa her shape. |
| `methodology/` | Mythic Engineering reference material — how we build, not what we build. |
| `archive/` | Retired docs preserved for history. Never delete; move here instead. |

## Top-level documents (planned)

- `SYSTEM_VISION.md` — Skald-written; the soul of the project in one short doc.
- `REPO_MAP.md` — One-line description of every folder. Operator's second stop after `README.md`.
- `DEVLOG.md` — Append-only daily/per-session record.

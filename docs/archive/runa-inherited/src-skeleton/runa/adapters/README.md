# src/runa/adapters/

Connections to specific external systems. One subfolder per external surface:
`discord/`, `telegram/`, `matrix/`, `webchat/`, `email/`, `home_assistant/`, `mcp/`, plus model-provider adapters under their own subfolders.

Each adapter is independently failable. The agent must start, run, and remain usable when any adapter fails to load or fails at runtime.

Contracts live in `docs/adapters/`. See `INTERFACE.md` here for the cross-adapter conventions.

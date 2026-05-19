# docs/adapters/

One document per external surface Runa speaks across: chat platforms, voice systems, home automation, third-party model providers, MCP servers.

Each adapter doc covers: what the adapter does, what configuration it needs, what permissions it requires on the host, what failure modes are tolerated vs fatal, how it degrades when its external dependency is unreachable.

## Adapter docs (to be added as adapters ship)

- `discord.md`
- `telegram.md`
- `matrix.md`
- `webchat.md`
- `email.md`
- `home_assistant.md`
- `mcp.md`
- `openrouter.md`
- `ollama.md`
- `lm_studio.md`

Adapter *code* lives in `src/runa/adapters/<name>/`. This folder holds the contract those modules must satisfy.

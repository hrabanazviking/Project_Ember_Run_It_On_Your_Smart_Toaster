# config/

Configuration *templates* and *examples*. Nothing here is read at runtime by a deployed Runa — the deployed agent reads from `~/.runa/config/` on its host machine.

The files here are what operators copy into `~/.runa/config/` during install, and what tests load as fixtures.

## Files (planned)

- `runa.example.yaml` — main configuration template (current empty `config.yaml` at repo root migrates here).
- `logging.example.yaml` — log levels, sinks, rotation.
- `models.example.yaml` — model router targets (cloud, OpenRouter, Nous, local Ollama, LM Studio, home server).
- `permissions.example.yaml` — tool capability allow-lists per surface.
- `profiles/` — named bundles for common deployment shapes (Pi-only, Pi+laptop, dev-laptop).

## Rules

- No secrets in this folder. Ever. `.env.example` documents required keys; real values live in `~/.runa/secrets/`.
- No absolute paths. All paths are relative to `~/.runa/` or use config-keyed lookups.
- Every key has a default. The agent never refuses to start because of a missing optional key.

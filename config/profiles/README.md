# config/profiles/

Named bundles of configuration for common deployment shapes. A *profile* is a partial `runa.yaml` overlay applied on top of the base example.

Planned profiles:
- `pi-only.yaml` — strict-local, no chat bridges, no voice.
- `home-longhall.yaml` — Pi + laptop on a Tailnet, full chat bridges.
- `dev.yaml` — verbose logs, fast cache invalidation, mock model.

Operators choose a profile at install time with `runa config init --profile <name>`.

# src/runa/services/

Long-running service wrappers — each is a thin shell around `runa.core` plus its own I/O surface and lifecycle.

Examples: `gateway_service`, `worker_service`, `voice_service`, `gui_service`. Each is launchable via `runa <service-name>` and via a `systemd` unit in `deploy/systemd/`.

Services are how `core` gets *exposed*; they are not where new agent behaviour goes. New behaviour goes in `core`.

See `INTERFACE.md`.

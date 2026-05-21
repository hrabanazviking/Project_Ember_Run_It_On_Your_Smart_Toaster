# src/runa/apps/

User-facing application implementations: the actual GUI window, the actual voice loop, the actual interactive CLI shell, the actual gateway HTTP server. Each `app` typically pairs with a `service` of the same name.

The split: `services/` handles process lifecycle and IPC; `apps/` handles the user-experience layer.

See `INTERFACE.md`.

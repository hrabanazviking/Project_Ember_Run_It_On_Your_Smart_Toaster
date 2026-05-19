# deploy/systemd/

User-level systemd unit files for Runa services.

Planned units:
- `runa-core.service` — the agent kernel + event bus + memory + task ledger.
- `runa-gateway.service` — the HTTP gateway / chat-surface dispatcher.
- `runa-worker.service` — the background-task executor.
- `runa-voice.service` — the voice loop (only on hosts that have audio I/O).

Each unit uses `Restart=on-failure` with sane backoff, declares its `EnvironmentFile=`, and runs as the operator's own user — not root.

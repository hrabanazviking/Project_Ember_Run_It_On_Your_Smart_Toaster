# src/runa/runtime/

Process supervision and control-plane commands: start, stop, restart, status, doctor, logs, memory backup, state snapshot, config validate.

Called by `runa.cli` and by `runa.services` for graceful lifecycle. Calls into `runa.core` for the agent itself.

See `INTERFACE.md` for the public surface.

# tools/diagnostics/

Live-system diagnostics for a deployed Runa. Read-only by design.

Planned tools:
- `dump_event_bus.py` — tail VERÐANDI in a human-readable form.
- `memory_health.py` — Muninn store integrity, embedding-index freshness, write-ahead-log status.
- `task_ledger_snapshot.py` — current Skuld state with stuck-task detection.
- `world_model_inspect.py` — snapshot of the WYRD bridge.

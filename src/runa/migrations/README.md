# src/runa/migrations/

Versioned migrations for the on-disk state stores: Muninn memory, Skuld task ledger, WYRD world-model snapshot, emotional-state journal, identity store.

Each migration is named `NNNN_short_description.py` (zero-padded sequence). Migrations are forward-only by default; reversibility is opt-in per migration.

`runa state migrate` (via `runa.runtime`) walks this folder in order against the live stores.

See `INTERFACE.md`.

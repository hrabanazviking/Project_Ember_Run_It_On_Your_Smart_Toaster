# src/runa/core/

The heart of Runa. The agent itself.

Houses the kernel, event bus (VERÐANDI), task ledger (Skuld), memory OS (Muninn), world model bridge (WYRD), emotional state engine, model router, tool forge, identity layer, policy engine, and the structured-logging core.

Nothing in `core/` may import from `services/`, `apps/`, `adapters/`, `plugins/`, or `skills/`. Outer layers depend on `core/`, never the reverse.

See `INTERFACE.md` for the public surface and invariants. Read `docs/architecture/DOMAIN_MAP.md` for how the internal subdomains relate.

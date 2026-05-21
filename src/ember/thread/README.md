# `src/ember/thread/`

The **Thread realm**. The middle layer between Spark and Well.

One subpackage:

- `strengr/` — the tether. Owns connection lifecycle, auth, retry, and
  the graceful-offline contract (`Disconnected` return rather than raise).

## Status

Scaffold only. Phase 4 of the first slice fills in Strengr.

## Reads with

- `docs/architecture/ARCHITECTURE.md` §3.2
- `docs/architecture/DOMAIN_MAP.md` §4
- `docs/architecture/DATA_FLOW.md` §2.2 (the sad path)

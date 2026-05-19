# INTERFACE — `runa.migrations`

**Status:** Stub — no code yet.
**Owner role:** Architect.
**Reads with:** `docs/architecture/DOMAIN_MAP.md` §2.

## Purpose

Versioned migrations for the on-disk state stores: Muninn memory, Skuld task ledger, WYRD-bridge snapshot, Eldhugi emotional journal, identity store, policy store.

## Public surface

| Function | Caller | Purpose |
|---|---|---|
| `runa.migrations.run_pending(store_name) -> MigrationResult` | `runa.runtime.commands.migrate` | Walk migrations in order, applying any whose recorded version < current head. |
| `runa.migrations.current_version(store_name) -> int` | `runa.runtime.commands.doctor` | Report which migration the store is at. |
| `runa.migrations.head_version(store_name) -> int` | `runa.runtime.commands.doctor` | Report which migration the code expects. |

All other modules in this package are migration scripts named `NNNN_short_description.py` and are not directly importable from outside.

## Invariants

- **Forward-only by default.** Reversibility is opt-in per migration.
- **Transactional.** No partial migration. Failure leaves the store at the prior version.
- **Versioned.** `~/.runa/state/version/<store_name>` records the applied migration head.
- **Idempotent re-attempts.** A migration may be re-attempted after a clean failure without corrupting state.

## Allowed callers

`runa.runtime` only. No subpackage other than `runa.runtime` may import from `runa.migrations`.

## Allowed callees

`runa.schemas`. The migration scripts themselves may use `sqlite3` / file I/O against `~/.runa/<store>/`.

## Failure semantics

A failed migration halts startup. `runa doctor` reports the exact migration ID and error. The store remains at the prior consistent version. Operator-asked rollback (`runa state restore --to-version N`) is required to go backward.

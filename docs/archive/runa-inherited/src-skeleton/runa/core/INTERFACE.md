# INTERFACE — `runa.core`

**Status:** Stub — no code yet. The largest and most consequential interface in the repository.
**Owner role:** Architect.
**Reads with:** `docs/architecture/DOMAIN_MAP.md` §3 + per-subdomain table, `docs/architecture/ARCHITECTURE.md`, `docs/architecture/DATA_FLOW.md`.

## Purpose

The agent itself. Kernel, event bus (VERÐANDI), task ledger (Skuld), memory OS (Muninn), world-model bridge (WYRD), emotional state (Eldhugi, provisional), model router (Heimskringla), tool forge (Smiðja), subagent hall (Hirð with named retainers Huginn/Muninn/Völundr/Eir/Heimdallr/Saga), repair (Eir), identity, policy, logging core.

## Public surface

At slice time this section will declare an explicit list. The structuring principle is:

- The **kernel** exposes one entry point — `runa.core.kernel.run(config) -> KernelHandle` — and the event-bus subscribe/publish interface.
- Each subdomain exposes a typed accessor for the rest of `core` and for `runa.runtime` to use. Example accessors (planned):
  - `runa.core.memory.MuninnReader`, `runa.core.memory.MuninnWriter`.
  - `runa.core.tasks.SkuldLedger`.
  - `runa.core.world.WyrdBridge`.
  - `runa.core.emotions.EldhugiJournal`.
  - `runa.core.models.HeimskringlaRouter`.
  - `runa.core.tools.SmidjaForge`.
  - `runa.core.subagents.HirdHall`.
  - `runa.core.repair.EirHealer`.
  - `runa.core.identity.IdentityStore`.
  - `runa.core.policy.PolicyStore`.
  - `runa.core.logging.get_logger(name) -> Logger`.
  - `runa.core.config.load_config(path) -> Config`.
- No accessor returns a raw module; everything goes through an instance with declared methods.

Each subdomain carries its own internal `INTERFACE.md` declaring its own internal surface — those are not yet written (deferred to the slice that builds the subdomain).

## Invariants

- **`core` does not import from `services`, `apps`, `adapters`, `plugins`, `skills`, `runtime`, or `cli`.** No exceptions.
- **The kernel is the only synchronous decision point.** Other subdomains coordinate through VERÐANDI events.
- **All persistent state writes go through exactly one writer per store** (see `docs/architecture/DATA_FLOW.md` §4).
- **The kernel knows skills/plugins/adapters only through typed registries.** It never names a module under `skills/`, `plugins/`, or `adapters/`.
- **No `print`, no raw `logging.getLogger`.** All loggers come from `runa.core.logging.get_logger`.
- **No `datetime.now()` directly in business logic** — use the injected clock so tests are deterministic.

## Allowed callers

`runa.runtime`, `runa.services`, `runa.apps`, `runa.adapters`, `runa.plugins`, `runa.skills`.

## Allowed callees

`runa.schemas`, `runa.migrations` (the latter only indirectly via store accessors that invoke `runa.migrations.run_pending` at first use).

## Failure semantics

A failure in `core` is a service-down event. The runtime supervisor catches it, writes a crash record to `~/.runa/state/crashes/<timestamp>/`, and restarts via the supervisor with full recovery flow per `docs/architecture/DATA_FLOW.md` §5.

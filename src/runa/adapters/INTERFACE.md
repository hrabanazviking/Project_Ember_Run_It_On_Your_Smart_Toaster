# INTERFACE — `runa.adapters`

**Status:** Stub — no code yet.
**Owner role:** Architect.
**Reads with:** `docs/architecture/DOMAIN_MAP.md` §8, `docs/adapters/` (the per-adapter contracts).

## Purpose

Connections to specific external systems: chat platforms (Discord, Telegram, Matrix), home automation (Home Assistant), automation (MCP servers), email, model providers (OpenRouter, Nous, Ollama, LM Studio), and any future external surface.

## Public surface

Every adapter exposes the same shape:

| Symbol | Purpose |
|---|---|
| `<adapter>.Adapter` | The adapter class. |
| `<adapter>.Adapter.start(config, gateway) -> None` | Begin pumping messages between the external system and the gateway. |
| `<adapter>.Adapter.stop(graceful=True) -> None` | Drain and close the connection. |
| `<adapter>.Adapter.health() -> HealthReport` | Current adapter state — connected/disconnected/rate-limited/auth-failed. |
| `<adapter>.SCHEMA` | A pydantic config schema for this adapter's settings. |

Model-provider adapters additionally expose a typed call surface used by **Heimskringla**:

| Symbol | Purpose |
|---|---|
| `<provider_adapter>.ProviderAdapter.complete(request) -> Response` | Single inference call with normalised request/response shape. |

## Invariants

- **Every adapter is independently failable.** The agent starts, runs, and remains usable when any adapter fails to import, fails to authenticate, or loses its external connection.
- **No adapter holds shared in-process state with another adapter.**
- **No adapter reaches into `runa.core` state directly.** All communication goes through the gateway or the **Heimskringla** router via the declared interfaces.
- **Every adapter's external dependency is declared as an optional dependency group in `pyproject.toml`** so that operators can install only the adapters they need.
- **Every adapter respects its rate-limit and backoff policy.** A misbehaving adapter is auto-quarantined; quarantine is surfaced via `runa doctor`.

## Allowed callers

`runa.services`, `runa.apps`, `runa.core.models` (model-provider adapters only), tests.

## Allowed callees

`runa.schemas`, the external library for the adapter's system, the narrow `runa.core` message types declared in the relevant `runa.core.<surface>.INTERFACE.md`.

## Failure semantics

**Critical.** Adapter failure must never take the agent down. The supervisor logs the failure, quarantines the adapter, and continues. `runa doctor` reports the quarantine and the operator can re-enable after fixing the underlying issue.

# INTERFACE — `ember.thread.strengr`

## Module purpose

The tether. Wraps Brunnr-handle acquisition in failure-handling so that
network failure becomes a typed value, not an exception, at the Spark
boundary.

## Public entry points (shipped Phase 4, 2026-05-21)

- `ember.thread.strengr.open(strengr_config, brunnr_config, *, opener=None,
  sleeper=time.sleep) -> BrunnrHandle | Disconnected` — opens the Well
  via the registered Brunnr backend, retrying recoverable failures up
  to ``StrengrConfig.retry_attempts`` times with exponential backoff
  capped at ``StrengrConfig.retry_backoff_max_s``. Never raises a
  connection error.
- `ember.thread.strengr.health(handle) -> StrengrHealth` — probes the
  Well via ``handle.count()`` and returns a snapshot. **Never raises.**
  On probe failure returns ``StrengrHealth(last_ok=None, detail=...)``.

### Recoverable vs non-recoverable reasons

| `DisconnectReason` | Retried? |
|---|---|
| `CONN_REFUSED`, `TIMEOUT`, `BACKEND_REPORTED_UNAVAILABLE`, `UNKNOWN` | Yes — up to `retry_attempts`. |
| `CONFIG_INVALID`, `AUTH_FAILED`, `DNS_FAILURE` | No — fast-fail. |

The split keeps the operator's wait time bounded — retrying a typo'd
config a few times before reporting it back is bad UX.

## Inputs

`StrengrConfig` + `BrunnrConfig` (passed separately so tests can vary
each independently).

## Outputs

A `BrunnrHandle` (live) or a typed `Disconnected(reason, since, detail)`.
``health()`` always returns a `StrengrHealth`.

## Allowed imports

`ember.schemas`, `ember.well.brunnr` (to obtain handles).

## Invariants

- Never raises a connection error across the module boundary.
- `Disconnected` carries a typed `reason` enum, not a free-form string.
- Auth material is never logged.

## Forbidden responsibilities

- Backend-specific protocols (those live inside the Brunnr adapter).
- Conversation memory (that's Well content).
- Deciding what to retrieve (Spark's job).

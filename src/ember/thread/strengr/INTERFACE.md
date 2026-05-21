# INTERFACE — `ember.thread.strengr`

## Module purpose

The tether. Wraps Brunnr-handle acquisition in failure-handling so that
network failure becomes a typed value, not an exception, at the Spark
boundary.

## Public entry points (planned, Phase 4)

- `ember.thread.strengr.tether.open(config) -> BrunnrHandle | Disconnected`
- `ember.thread.strengr.tether.health(handle) -> StrengrHealth`

## Inputs

`StrengrConfig` (which embeds the `BrunnrConfig`).

## Outputs

A `BrunnrHandle` (live) or a `Disconnected(reason: DisconnectReason, since: datetime)` value.

## Side effects

- Opens a network connection or in-process handle to the configured
  Brunnr.
- Reads auth material from the keyring or `~/.ember/secrets/`.
- Issues health pings on a schedule.

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

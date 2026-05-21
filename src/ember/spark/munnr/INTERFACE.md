# INTERFACE — `ember.spark.munnr`

## Module purpose

The command-line surface. Parses arguments, dispatches subcommands,
formats terminal output.

## Public entry points (planned, Phase 6)

- `ember.spark.munnr.chat.run(config)` — REPL loop.
- `ember.spark.munnr.ask.run(config, text)` — one-shot.
- `ember.spark.munnr.ingest.run(config, path)` — ingest.
- `ember.spark.munnr.doctor.run(config)` — diagnostics.
- `ember.spark.munnr.status.run(config)` — well status.
- `ember.spark.munnr.render.*` — terminal formatting helpers (banner for
  `well: disconnected`, citation footers, etc.).

## Inputs

Parsed CLI arguments.

## Outputs

Exit codes (0 ok; non-zero with one-line human-readable cause on
failure). Side effects to stdout/stderr.

## Side effects

- Reads stdin in `chat` mode.
- Calls Funi via Spark.
- Calls Strengr → Brunnr for retrieval and episode writes.
- Calls Smiðja for ingest.
- Reads operator config from `~/.ember/config/`.

## Allowed imports

`ember.schemas`, `ember.spark.funi`, `ember.spark.hjarta`,
`ember.thread.strengr`, `ember.well.brunnr`, `ember.well.smidja`.

## Invariants

- A parse failure prints help and exits non-zero without side effects.
- A subcommand failure produces a one-line human-readable cause.
- The `well: disconnected` banner is **always** shown on ungrounded
  replies (Vow of Graceful Offline).
- No `print()` — every line through the logger / render layer.

## Forbidden responsibilities

- Doing any actual work itself — Munnr is a router.

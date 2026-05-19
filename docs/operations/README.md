# docs/operations/

Operator-facing runbooks: how a human installs, starts, stops, inspects, backs up, repairs, and updates a deployed Runa.

Nothing here is meant to teach you what Runa *is*. That lives in `docs/architecture/`. This folder is for "the agent has been silent for 12 hours, what do I do".

## Planned canonical documents

- `INSTALL.md` — fresh-install procedure for Pi 5 and for laptop/dev.
- `STARTUP.md` — service start/stop/restart, expected log lines, healthy-state indicators.
- `OBSERVABILITY.md` — where logs go, what to grep for, how to read the event bus dump.
- `BACKUP_RESTORE.md` — state snapshots, memory exports, secrets handling.
- `INCIDENT_RUNBOOK.md` — common failure modes and the exact recovery steps.

## Imported material

- `RUNA_PROJECT_FILE_ORGANIZATION_AND_STARTUP_GUIDE.md` — the file-org + startup design source that the layout of this repo is built from.

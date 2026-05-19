# scripts/maintenance/

Operator maintenance scripts run against deployed Runa state: rotate logs, vacuum memory store, prune cache, export/import state bundles, archive old conversations.

Every script defaults to dry-run and requires `--apply` to mutate. Every script logs to `~/.runa/logs/maintenance/`.

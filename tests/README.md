# tests/

All automated verification lives here. Layout follows pytest convention.

## Subfolders

| Folder | Scope |
|---|---|
| `unit/` | Single-module tests. No real network, no real filesystem outside `tmp_path`, no real models. |
| `integration/` | Multi-module flows. May spin a local SQLite or stub model, never reach the public internet. |
| `e2e/` | End-to-end through the real CLI / API surface. Slowest tier. May be opt-in via marker. |
| `fixtures/` | Reusable test data: seed memory, sample conversations, mock model responses. |
| `snapshots/` | Golden-file outputs for snapshot tests. |

## Rules

- Each test names what it verifies, not what it does (`test_kernel_recovers_from_crash_during_task_save` not `test_kernel_recovery_1`).
- No test reaches the public internet. Adapters with external dependencies are stubbed.
- No test writes outside `tmp_path` or `tests/snapshots/`.
- Tests are fast by default. Slow tests carry a `slow` marker and run separately.

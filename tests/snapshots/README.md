# tests/snapshots/

Golden-file outputs for snapshot-style tests. One file per snapshot, named so the source test is obvious.

When a snapshot legitimately changes, the diff is reviewed in the PR like any other code change. Snapshot regeneration scripts live under `scripts/dev/` and require explicit invocation — they never run automatically.

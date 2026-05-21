# 🧵 Thread Safety and Concurrency

## Current Architecture

Verðandi Heartbeat uses a **single-threaded, sequential** architecture:

```
pulse_one() → check_all() → health_score() → react() → nerve_publish() → persist() → sleep
pulse_two() → check_all() → health_score() → react() → nerve_publish() → persist() → sleep
...
```

Each pulse is entirely sequential. Checks run one after another, not in parallel. This is **intentional** and **by design** for several reasons:

### Why Single-Threaded?

1. **Predictability**: No race conditions, no deadlocks, no concurrent access issues
2. **Pi-friendly**: Single thread is more efficient on ARM with limited cores
3. **Debuggable**: Any issue can be reproduced by running a single pulse
4. **Sufficient**: The pulse interval (60s) is much longer than the pulse duration (~100ms)
5. **Safe**: SQLite is thread-safe with WAL mode, but sequential access eliminates even that concern

### When Would Threading Help?

Only if individual checks become slow (>1 second each):
- Network checks (ping, HTTP) — currently not implemented
- Disk-intensive scans (large directory trees) — only if Huginn scans very large repos
- External API calls — future Bifrǫst extensions

## SQLite Concurrency

SQLite serves as the state database and must handle concurrent access from:

1. **The daemon** (writes on every pulse)
2. **The CLI** (reads on `pulse --once`, `config`, `paths`)
3. **External tools** (queries from monitoring scripts)

SQLite handles this via WAL (Write-Ahead Logging) mode:

```python
# Already configured in _state_db_init()
conn.execute("PRAGMA journal_mode=WAL")      # Concurrent reads don't block writes
conn.execute("PRAGMA synchronous=NORMAL")      # Fast writes, acceptable durability
conn.execute("PRAGMA busy_timeout=5000")       # Wait 5s if database is locked
```

### Reader-Writer Pattern

```
Daemon (writer)          CLI query (reader)
    │                        │
    │─ write ──────────────►│ (blocks until write done)
    │                        │
    │                        │─ read ──────────► (reads from WAL snapshot)
    │                        │
    │─ write ──────────────►│
```

Readers never block writers in WAL mode, but writers block each other. Since the daemon only writes once per pulse (60s default), contention is negligible.

## Future Threading Considerations

If checks become slow enough to warrant parallelization:

```python
# Future: Parallel check execution (not yet implemented)
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_all_parallel(self, checks, timeout=5.0):
    """Run all checks in parallel with timeout."""
    results = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(check.check): name 
            for name, check in checks.items()
        }
        for future in as_completed(futures, timeout=timeout):
            name = futures[future]
            try:
                results[name] = future.result()
            except Exception as e:
                results[name] = CheckResult(
                    name=name, severity=CheckSeverity.UNKNOWN,
                    message=f"Check failed: {e}"
                )
    return results
```

**This is not currently needed** but the architecture supports it if the check registry grows significantly.
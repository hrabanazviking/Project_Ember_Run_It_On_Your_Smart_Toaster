# 50 — Long-Running Process Patterns: Daemons, Supervisors, Restarts

**Category:** Observability & Operations
**Runa relevance:** the whole agent (Runa is a long-running process)
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

A long-running process — Runa on her Pi 5, running for months between restarts — accumulates state that short-lived programs don't have: memory leaks, file-descriptor leaks, fragmenting allocators, gradually-degrading caches, slow drift in connection state. The discipline of writing software that *stays healthy over time* combines several patterns from this corpus: crash-only design ([[11-crash-only-software]]), supervisor trees ([[12-supervisor-trees]]), watchdogs ([[13-watchdog-timers]]), health checks ([[14-health-checks]]), self-repair ([[15-self-repair-reconciliation]]), bounded resources ([[08-bulkhead-pattern]]), graceful shutdown ([[49-graceful-shutdown]]).

This document gathers the long-running-process disciplines into a single reference. It's the closing piece of the Python craft corpus because every other technique compounds when applied to a process that runs for years.

## 2. Technique / mechanism

**The long-running-process checklist:**

### Lifecycle

- ☐ Started via supervisor (systemd / launchd / Docker).
- ☐ Supervisor configured with `Restart=on-failure` and intensity limit.
- ☐ Process exits non-zero on unrecoverable error.
- ☐ Process handles SIGTERM gracefully ([[49-graceful-shutdown]]).
- ☐ Process logs startup and shutdown clearly.

### Health

- ☐ Liveness check that proves the main loop is iterating ([[14-health-checks]]).
- ☐ Readiness check that proves the process can serve requests.
- ☐ Watchdog timer (systemd WatchdogSec or in-process) ([[13-watchdog-timers]]).
- ☐ Health endpoints exposed for external probing.

### Resources

- ☐ All caches bounded ([[38-caching-strategies]]).
- ☐ All queues bounded with backpressure ([[24-queue-channel-patterns]]).
- ☐ All connection pools bounded ([[08-bulkhead-pattern]]).
- ☐ All timeouts set ([[09-timeout-patterns]]).
- ☐ Worker processes recycled periodically (`max_tasks_per_child`) ([[21-multiprocessing-deep-dive]]).
- ☐ Memory growth monitored ([[37-memory-profiling]]).

### Failure handling

- ☐ Every external dependency has retry + breaker + bulkhead ([[06-retry-strategies]], [[07-circuit-breaker]]).
- ☐ Graceful degradation when subsystems fail ([[10-graceful-degradation]]).
- ☐ Crash-only state stores ([[11-crash-only-software]]).
- ☐ Idempotent recovery ([[05-idempotency-design]]).

### Observability

- ☐ Structured logging ([[46-structured-logging]]).
- ☐ Distributed tracing ([[47-distributed-tracing-opentelemetry]]).
- ☐ Metrics emission ([[48-metrics-prometheus]]).
- ☐ Audit log (per [[40-audit-logging-replay]] research doc).

### Maintenance

- ☐ Self-repair / reconciliation loop ([[15-self-repair-reconciliation]]).
- ☐ Periodic state-store maintenance (vacuum, compact, reindex).
- ☐ Log rotation.
- ☐ Cache eviction (TTL or LRU).

### Recovery from common failures

- ☐ Memory pressure → bounded caches, periodic worker recycling, OOM-handler observability.
- ☐ Disk pressure → log rotation, archive policy, alerts before full.
- ☐ Network partitions → retry + circuit breaker; degraded operation.
- ☐ Backend outages → fallback or graceful degradation.
- ☐ Slow leaks → bounded process lifetime (periodic restart, e.g. weekly).

### Operator surface

- ☐ `runa start / stop / restart / status / doctor / logs`.
- ☐ Clear semantics for each.
- ☐ Visibility into degraded state.
- ☐ `Notified` events for significant state changes.

**The "weekly restart" pragma:**

Even with perfect engineering, long-running processes accumulate subtle state. A *deliberate* weekly restart at a quiet time prevents accumulation from becoming a problem:

```ini
# /etc/systemd/user/runa-core.service
[Service]
...
# Auto-restart every Sunday at 03:00
[Install]
WantedBy=default.target

# Plus a separate timer unit that restarts the service
# /etc/systemd/user/runa-restart.timer
[Timer]
OnCalendar=Sun *-*-* 03:00:00
```

The graceful-shutdown discipline makes this invisible to the user.

**Process restart-aware code:**

```python
class Kernel:
    def __init__(self):
        self.startup_time = time.monotonic()
    
    def is_recently_started(self, within_seconds: float = 60.0) -> bool:
        return (time.monotonic() - self.startup_time) < within_seconds
```

Some logic should differ "I just started" vs "I've been running for hours." Recently-started processes might be more cautious; long-running processes have built up state to use.

**Memory growth detection:**

```python
import psutil
import asyncio

async def watch_memory():
    process = psutil.Process()
    initial_rss = process.memory_info().rss
    while True:
        await asyncio.sleep(3600)  # hourly
        current_rss = process.memory_info().rss
        growth_mb = (current_rss - initial_rss) / 1024 / 1024
        if growth_mb > 500:  # arbitrary threshold
            logger.warning("memory growth detected", growth_mb=growth_mb)
            emit_event(Notified(severity="warn", message=f"Memory grew {growth_mb} MB since start"))
```

Eir runs this. Trend > limit triggers alert.

**File descriptor leak detection:**

```python
def check_fd_count():
    process = psutil.Process()
    return process.num_fds()  # POSIX; num_handles on Windows

# Periodically check; warn if growing without bound
```

Long-running processes leak FDs in subtle ways (forgotten file handles, broken connections held). Periodic check catches.

## 3. Key works / libraries

This doc references and integrates many. Key external references:

- **Beyer et al.** *Site Reliability Engineering*, O'Reilly 2016. The bible.
- **The Twelve-Factor App** — 12factor.net.
- **Stopford, B.** *Designing Event-Driven Systems*, O'Reilly 2018.
- **Patterson, D.** *Patterns of Enterprise Application Architecture* — long-running service patterns.
- **`psutil`** — github.com/giampaolo/psutil. Process inspection.
- **systemd documentation** — service lifecycle.

## 4. Pitfalls and gotchas

The whole corpus is one long list of pitfalls. Top-level ones for long-running processes specifically:

- **Memory leaks** — unbounded growth eventually triggers OOM.
- **File-descriptor leaks** — eventually hit `ulimit`.
- **Subtle state corruption** — accumulates over weeks; not seen in short tests.
- **Cache bloat without eviction** — slow leak.
- **Connection pool exhaustion** — held connections that never close.
- **Background tasks that fail silently** — bug compounds.
- **Configuration drift** — different process restarts pick up different state.

## 5. Applicability to Runa

For **the whole Runa agent**:

- All of the above. Every checklist item applies.
- Documented in `docs/operations/LONG_RUNNING.md` (to be written when Runa code lands).

For **deploy/pi/**:

- Pi-specific tuning: thermal throttling awareness, SD-card avoidance, NVMe for state, swap considerations.

For **deploy/systemd/**:

- Service units with all the right `Restart`, `WatchdogSec`, `TimeoutStopSec`, `KillMode` settings.
- Timer units for periodic Eir tasks (weekly restart, daily snapshot).

For **`runa doctor`**:

- Reports uptime, memory growth since start, fd count, cache utilisations, recent restart history.

For **Eir**:

- The continuous reconciliation loop running all the maintenance the long-running process needs.

What to avoid:

- Don't ship a "just run forever" agent without operational discipline. The bugs are subtle and accumulate.
- Don't skip a single item on the checklist for "this is just personal use."
- Don't treat the checklist as paranoia. Each item came from a real production failure somewhere.

## 6. Open questions

- **The right uptime target.** Days? Weeks? Months? Trade-off between accumulated risk and operational disruption.
- **Multi-version coexistence.** Two Runa versions running side by side during upgrade. Not generally supported in Python single-process design; rare need.
- **Cloud-native patterns at home scale.** Many SRE patterns assume fleet operation; single-Pi is a different regime. Adapt thoughtfully.

## 7. References (curated)

- *Site Reliability Engineering* (Beyer et al., 2016).
- 12factor.net.
- All other docs in this corpus.
- Companion docs: every other doc in `docs/python/`. This is the integrating reference.

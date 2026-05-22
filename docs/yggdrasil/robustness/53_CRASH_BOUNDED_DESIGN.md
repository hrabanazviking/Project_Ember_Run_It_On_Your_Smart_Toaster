# 53 — Crash-Bounded Design

How Yggdrasil ensures that one component's crash doesn't
take everything down. Process isolation, error boundaries,
graceful shutdown.

---

## The principle

**Every crash is bounded.** A panic in one realm doesn't
crash adjacent realms. A bug in one widget doesn't crash
Stofa. A failed audit doesn't crash chat.

The blast radius of any single failure is contained.

---

## Three levels of isolation

### Level 1: Sibling process isolation

Each sibling project that runs as a daemon (Verdandi,
Qdrant, optionally Kista) is its own OS process. They
crash independently of Ember.

When Verdandi's daemon crashes:
- Ember's process keeps running.
- Ember's `VerdandiClient` detects the broken socket;
  publishes "verdandi.unavailable" to its in-process ring
  buffer.
- The awareness layer pauses; chat continues.
- The auto-recovery playbook (per
  [`52_AUTO_RECOVERY_PATTERNS.md`](52_AUTO_RECOVERY_PATTERNS.md))
  tries to restart Verdandi.

The OS process boundary is **the strongest isolation we
have**. We use it for risky/external sibling daemons.

### Level 2: In-process realm isolation

Realms imported as Python libraries (mimir-well, Seiðr,
Kista) share Ember's process. They can't be process-
isolated without complicating the architecture.

For these, we use **error boundaries at the adapter
layer**:

```python
class MimirBrunnr:
    async def search(self, query):
        try:
            return await self._mimir_internal_search(query)
        except Exception as exc:
            logger.error("Mímir search failed: %s", exc)
            return SearchResult(
                hits=[],
                degraded=True,
                error=str(exc),
            )
```

A crashing realm returns a typed-error result; doesn't
propagate the exception. The caller (Bifrǫst, chat loop)
sees the typed error and degrades gracefully.

### Level 3: Per-widget isolation (Stofa)

Per Stofa's design (`docs/tui/operations/93_ERROR_BOUNDARIES.md`),
every widget's `render()` is wrapped:

```python
def render(self):
    try:
        return self._render_real()
    except Exception as exc:
        logger.warning("widget %s render failed: %s", self.name, exc)
        return Text(f"(panel error: {type(exc).__name__})", style="error")
```

A widget that crashes shows "(panel error)" instead of
killing the TUI. Adjacent widgets continue.

---

## What "crash" means

Not just Python exceptions. Three categories:

1. **Synchronous exceptions** — caught by `try/except`
   at boundaries.
2. **Async task crashes** — `asyncio.Task` raising;
   caught by task-exception handlers.
3. **Process crashes** — OS-level (segfault, OOM,
   SIGKILL). Caught by absent-heartbeat detection (per
   [`51_HEALTH_GOSSIP_PROTOCOL.md`](51_HEALTH_GOSSIP_PROTOCOL.md)).

Each category has its own bounding strategy.

---

## The async-task safety pattern

Long-running async tasks need explicit exception handling
or they fail silently:

```python
def safe_task(coro, *, on_error: Callable | None = None):
    """Wrap a coroutine in a task with safe error handling."""
    async def runner():
        try:
            await coro
        except Exception as exc:
            logger.exception("background task crashed")
            if on_error:
                await on_error(exc)
    return asyncio.create_task(runner())
```

All background workers (reconciliation, dreamstate, gossip
loops) are wrapped this way. A crashed task gets logged +
re-spawned, doesn't take down the loop.

---

## The graceful-shutdown pattern

When Stofa quits (or the operator Ctrl-Cs), components
must release resources cleanly. Specifically:

- Close every realm handle.
- Flush every pending Verdandi event.
- Persist final state of any in-progress operation.
- Restore the terminal (Stofa's responsibility).

Pattern:

```python
async def shutdown(self):
    """Best-effort cleanup of every realm."""
    for realm in self.realms.values():
        try:
            await asyncio.wait_for(realm.close(), timeout=5.0)
        except Exception as exc:
            logger.warning("realm %s close failed: %s", realm.name, exc)
    # Don't let one bad close block others.
```

Each `close()` has a timeout. A hung close doesn't prevent
the next close. After all closes, the process exits.

---

## What about catastrophic failures

Some failures *should* terminate Ember:

- **Out-of-memory**: catching OOM in Python is unreliable.
  We let the process die; systemd / launchd / etc. restart
  if configured.
- **Stack overflow**: same.
- **Unrecoverable assertion**: we don't try to recover from
  programming errors; the operator should see the failure.

For these:
- Stofa's main loop catches "uncatchable" exceptions and
  writes a crash file (per
  [`../tui/operations/94_OBSERVABILITY.md`](../../tui/operations/94_OBSERVABILITY.md)).
- The process exits with non-zero.
- On next start, Ember reads the crash file; offers
  operator a clean report.

This is the line: *transient failures heal automatically;
catastrophic failures terminate with a clear post-mortem*.

---

## The crash-report file

When Ember crashes:

```
~/.ember/state/yggdrasil_crashes/2026-05-21T18-32-04Z.json
```

Contents:
- Timestamp.
- Stack trace.
- Last 100 Verdandi events before the crash.
- Realm health states at last gossip.
- Operator's last 5 actions (anonymized — actions only, not
  inputs).

Operator can:
- Read it (in Stofa: Doctor screen offers viewer).
- Attach it to a bug report.
- Delete it.

Privacy: crash reports stay local. No auto-upload.

---

## How to test crash-bounded design

`tests/integration/test_yggdrasil_crash_isolation.py`:

```python
async def test_huginn_crash_doesnt_crash_chat():
    pool = await yggdrasil.start(crash_huginn=True)
    # Drive a chat turn; verify it completes
    reply = await pool.chat("hello")
    assert reply
    assert reply.degraded  # mentions Huginn was down

async def test_widget_crash_doesnt_crash_stofa():
    app = StofaApp.test_with(crash_widget="WellPanel")
    await app.run_for(2.0)
    assert app.is_running
    assert "panel error" in app.query("#WellPanel").render()
```

Per-failure-mode tests, exercising the isolation.

---

## Configuration shape

```yaml
yggdrasil:
  crash_bounded:
    enabled: true                   # disable for testing only
    boundaries:
      sibling_processes: true       # process isolation for daemons
      adapter_error_boundaries: true # in-process realm boundaries
      widget_error_boundaries: true  # Stofa per-widget
    task_safety:
      auto_restart_workers: true    # respawn crashed background tasks
      max_restarts_per_hour: 5      # avoid thrash
    crash_reports:
      enabled: true
      retention_days: 30
      auto_offer_on_next_launch: true
```

---

## Why this matters for trust

Operators using Ember long-term will eventually see
failures — network blips, sibling-project bugs, OS
quirks. The question is whether those failures *break
their flow*:

- Without crash-bounded design: a single failure crashes
  Stofa; operator loses their chat context; rage builds.
- With crash-bounded design: a panel says "(panel error)";
  rest of Stofa works; operator is mildly inconvenienced.

The difference is the difference between *Ember is a
toy* and *Ember is a tool I can rely on*.

---

## Closing

Crash-Bounded Design is **the structural safety net**.
Process isolation where possible; error boundaries
everywhere else; graceful shutdown; crash reports.

Combined with self-healing playbooks, the system handles
its own failures honestly: most fail quietly + recover;
some fail loudly + escalate; none take down the hall.

This is what makes Yggdrasil *trustworthy at production
scale* even though "production" for most operators is "my
laptop."

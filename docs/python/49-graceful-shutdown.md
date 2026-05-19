# 49 — Graceful Shutdown and Signal Handling

**Category:** Observability & Operations
**Runa relevance:** runa stop, systemd shutdown, redeploy, in-flight turn completion
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Even crash-only systems ([[11-crash-only-software]]) benefit from *graceful shutdown* when the time permits — finishing in-flight work, flushing buffers, closing connections, sending goodbye messages. The user experience of "I asked Runa something and she froze mid-reply because systemd restarted" is bad; "I asked Runa and she finished her response then said 'I'm restarting briefly'" is much better.

The Python craft: handle SIGTERM (the polite shutdown signal); have a bounded grace period; do best-effort cleanup; exit non-zero if not cleanly drained in time. Combined with the supervisor's restart-on-failure behaviour, this gives both graceful-when-possible and crash-only-when-necessary.

## 2. Technique / mechanism

**The signals to know:**

- **SIGTERM (15)** — polite "please shut down." Standard for systemd, Docker, Kubernetes.
- **SIGINT (2)** — Ctrl+C in terminal.
- **SIGHUP (1)** — terminal disconnect / config reload (traditional usage).
- **SIGKILL (9)** — *can't be caught*. The kernel terminates immediately.

**Signal handling in async code (the modern way):**

```python
import asyncio
import signal

async def main():
    shutdown_event = asyncio.Event()
    
    def _on_signal(sig):
        logger.info("received %s, initiating graceful shutdown", sig.name)
        shutdown_event.set()
    
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _on_signal, sig)
    
    # Run the main work and stop when shutdown is signalled
    async with asyncio.TaskGroup() as tg:
        worker = tg.create_task(run_worker())
        
        await shutdown_event.wait()
        logger.info("draining...")
        
        # Cancel work; tasks should honour cancellation
        worker.cancel()
    # TaskGroup awaits cleanup
    
    logger.info("shutdown complete")

asyncio.run(main())
```

`asyncio.run` cleans up the loop. `loop.add_signal_handler` is the asyncio-friendly way to handle signals (vs `signal.signal` which doesn't compose with the loop).

**Bounded grace period:**

```python
async def main():
    shutdown_event = asyncio.Event()
    GRACE = 30.0  # max seconds for graceful shutdown
    
    ...
    
    await shutdown_event.wait()
    logger.info("draining (max %ss)...", GRACE)
    
    try:
        async with asyncio.timeout(GRACE):
            worker.cancel()
            await worker
    except TimeoutError:
        logger.warning("forced shutdown after grace period")
```

Don't hang forever.

**Sync-context signal handling:**

```python
import signal
import sys

shutdown_requested = False

def handle_signal(sig, frame):
    global shutdown_requested
    shutdown_requested = True
    sys.stderr.write(f"received {sig}, shutting down\n")

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

# In main loop:
while not shutdown_requested:
    do_unit_of_work()
cleanup()
```

For sync programs. Less elegant than asyncio version.

**`atexit` for cleanup:**

```python
import atexit

def cleanup():
    logger.info("running atexit cleanup")
    flush_buffers()
    close_connections()

atexit.register(cleanup)
```

`atexit` runs on normal Python exit. *Not* on SIGKILL, OOM, segfault. Useful but not a guarantee.

**`signalfd` for cross-process signal handling:**

Linux-only; reading signals from a file descriptor for integration with other I/O. `signalfd` library wraps it. Niche; usually `add_signal_handler` is enough.

**Avoiding signal-handling pitfalls:**

- **`signal.signal()` only works in the main thread.** Use `loop.add_signal_handler` for asyncio in any thread.
- **Signals can fire mid-syscall.** Most code is interrupted at safe points; some I/O syscalls return `EINTR`. Modern Python handles this transparently.
- **Re-entrant signal handlers.** A signal handler that takes a lock the main thread holds → deadlock.
- **`SIGKILL` can't be handled.** Don't rely on cleanup in pathological scenarios.

**systemd integration:**

```ini
[Service]
ExecStart=/usr/bin/python -m runa.worker
KillSignal=SIGTERM
TimeoutStopSec=30s
KillMode=mixed
Restart=on-failure
```

systemd sends SIGTERM first; waits `TimeoutStopSec`; sends SIGKILL if still running.

**Per-subsystem graceful shutdown:**

```python
class Kernel:
    async def shutdown(self):
        # 1. Stop accepting new turns
        self._accepting = False
        
        # 2. Wait for in-flight turns to complete (bounded)
        try:
            async with asyncio.timeout(10.0):
                while self._in_flight:
                    await asyncio.sleep(0.1)
        except TimeoutError:
            logger.warning("in-flight turns didn't drain in time")
        
        # 3. Flush state
        await self.muninn.flush()
        await self.skuld.flush()
        
        # 4. Close external connections
        for adapter in self.adapters:
            await adapter.close()
```

**Graceful drain pattern (servers):**

```python
async def shutdown_gracefully(server):
    server.stop_accepting()
    await server.drain_pending(timeout=30.0)
    await server.close()
```

Each service shell follows this pattern.

## 3. Key works / libraries

- **`signal` stdlib** — docs.python.org/3/library/signal.html.
- **`asyncio` signal handling** — docs.python.org/3/library/asyncio-eventloop.html#unix-signals.
- **`atexit`** — docs.python.org/3/library/atexit.html.
- **systemd `TimeoutStopSec`** documentation.
- **Twelve-Factor App, factor 9 (disposability)** — 12factor.net/disposability.
- **`uvicorn`'s graceful shutdown** — reference implementation worth reading.

## 4. Pitfalls and gotchas

- **Cleanup that takes too long.** Bounded grace period; cleanup that doesn't complete in time = forced kill.
- **Synchronous cleanup in async code.** Calling sync DB close from asyncio shutdown can deadlock if it blocks the loop.
- **`atexit` doesn't run on SIGKILL.** Crash-only assumption.
- **Forgetting daemon threads.** Daemon threads die abruptly on Python exit. Use non-daemon threads with explicit join for important work.
- **Re-entrant signal handlers.** Signal during a signal.
- **systemd `KillMode=control-group` kills all processes.** Subprocesses die too.
- **Windows signal handling.** Different signals available (SIGBREAK instead of SIGTERM).

## 5. Applicability to Runa

For **`runa.runtime.commands.stop`**:

- Sends SIGTERM to the running runa process.
- `Type=notify` systemd service waits for `STOPPING=1` notification.

For **kernel graceful shutdown**:

- Stop accepting new turns.
- Wait up to GRACE seconds for in-flight turns.
- Flush Muninn writes.
- Close adapters with goodbye.

For **adapter graceful shutdown**:

- Each adapter sends a "Runa is restarting briefly" message if it has an active conversation.
- Drains outbound queue with timeout.
- Closes connection cleanly.

For **service shells**:

- Each service handles SIGTERM; calls kernel.shutdown; closes service-specific resources.

For **deploy/systemd/**:

- `TimeoutStopSec=30s` — generous but bounded.
- `KillSignal=SIGTERM`.
- `Restart=on-failure`.

For **dev mode**:

- Ctrl+C (SIGINT) triggers the same graceful shutdown path.

What to avoid:

- Don't rely on atexit for correctness.
- Don't block the asyncio loop in shutdown handlers.
- Don't have unbounded shutdown time.
- Don't assume cleanup ran.

## 6. Open questions

- **Per-subsystem grace periods.** Some can drain faster than others. Coordinated countdown is appealing.
- **Shutdown progress reporting.** "Saving Muninn... done. Closing adapters... done." User-visible. Nice-to-have.
- **Restart-while-running** (zero-downtime). Hard for single-process agents; easier for multi-process where one is "old" and one is "new."

## 7. References (curated)

- docs.python.org/3/library/signal.html.
- docs.python.org/3/library/asyncio-eventloop.html#set-signal-handlers.
- 12factor.net/disposability.
- github.com/encode/uvicorn — uvicorn server's graceful shutdown.
- Companion docs: [[11-crash-only-software]], [[12-supervisor-trees]], [[14-health-checks]], [[50-long-running-processes]].

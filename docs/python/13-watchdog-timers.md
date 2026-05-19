# 13 — Watchdog Timers and Liveness Detection

**Category:** Self-Healing & Supervision
**Runa relevance:** Eir (liveness monitoring), service hangs, deadlock detection
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

A process can be technically alive (its PID exists, the kernel hasn't killed it) and yet not making progress: stuck in a deadlock, looping infinitely, blocked on a never-completing I/O. Plain process supervision ([[12-supervisor-trees]]) can't catch this — the process didn't crash. The classic answer from embedded systems is the **watchdog timer**: a counter that *must be reset periodically by the process itself*; if it isn't, the watchdog assumes the process is hung and forces a restart.

For Runa, watchdogs catch the failure modes nothing else does: a deadlocked adapter still holding a Discord connection; a runaway thought loop in the kernel; a stuck retrieval that timed out at one layer but is still consuming resources at another. Combined with health checks ([[14-health-checks]]) and supervisor trees ([[12-supervisor-trees]]), watchdogs close the "alive but not really" gap.

## 2. Technique / mechanism

**The basic pattern:**

```
                  ┌────────────────────┐
                  │  Watchdog timer    │
                  │  countdown = T     │
                  └─────────┬──────────┘
                            │ if reaches 0
                            ▼
                  ┌────────────────────┐
                  │  Action: log,      │
                  │  restart, alert    │
                  └────────────────────┘
        ▲
        │ "I'm alive" — reset countdown
        │
┌──────────────────┐
│  Watched process │
└──────────────────┘
```

**Hardware watchdog timers** (embedded systems) use a dedicated hardware countdown register. Linux exposes `/dev/watchdog` for the same.

**Software watchdog patterns:**

### Pattern 1 — Heartbeat to external watcher

```python
import asyncio
import time
from pathlib import Path

class Heartbeat:
    """Write heartbeat to a file periodically; external supervisor watches the file."""
    
    def __init__(self, path: Path, interval: float = 10.0):
        self.path = path
        self.interval = interval
        self._task: asyncio.Task | None = None
    
    async def start(self):
        self._task = asyncio.create_task(self._heartbeat_loop())
    
    async def _heartbeat_loop(self):
        while True:
            self.path.write_text(f"{time.time()}")
            await asyncio.sleep(self.interval)
    
    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

# External watcher (e.g. systemd timer or a small script)
def check_heartbeat(path: Path, max_age: float):
    if not path.exists():
        return False
    last = float(path.read_text())
    return (time.time() - last) < max_age
```

The watcher (often a small companion process or systemd timer) detects stale heartbeats and acts.

### Pattern 2 — systemd's `WatchdogSec`

systemd has built-in watchdog support:

```ini
[Service]
Type=notify
WatchdogSec=30s
ExecStart=/usr/local/bin/runa worker
Restart=on-watchdog
```

```python
import sdnotify

notifier = sdnotify.SystemdNotifier()
notifier.notify("READY=1")  # signal ready

# Periodically:
while True:
    do_work()
    notifier.notify("WATCHDOG=1")  # reset the watchdog
    time.sleep(10)
```

`sdnotify` library handles the systemd socket protocol. If the process fails to notify within `WatchdogSec`, systemd kills and restarts.

### Pattern 3 — Per-task watchdog (in-process)

```python
class TaskWatchdog:
    """Watch async tasks; force restart if they hang."""
    
    def __init__(self, name: str, max_silence: float):
        self.name = name
        self.max_silence = max_silence
        self.last_beat = time.monotonic()
    
    def beat(self):
        self.last_beat = time.monotonic()
    
    def is_alive(self) -> bool:
        return (time.monotonic() - self.last_beat) < self.max_silence

class AdapterSupervisor:
    """Supervise an adapter with watchdog."""
    
    def __init__(self, adapter, watchdog: TaskWatchdog):
        self.adapter = adapter
        self.watchdog = watchdog
    
    async def run(self):
        while True:
            adapter_task = asyncio.create_task(self.adapter.run(beat=self.watchdog.beat))
            watchdog_task = asyncio.create_task(self._watch())
            
            done, pending = await asyncio.wait(
                {adapter_task, watchdog_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for t in pending:
                t.cancel()
            
            # If watchdog finished first, adapter is hung
            if watchdog_task in done:
                logger.warning("adapter %s hung; restarting", self.adapter.name)
            
            # Restart with backoff
            await asyncio.sleep(self._backoff())
    
    async def _watch(self):
        while True:
            await asyncio.sleep(5.0)
            if not self.watchdog.is_alive():
                return  # exit watcher; signals hang
```

### Pattern 4 — Threading-based hang detection

```python
import threading

class ThreadWatchdog:
    """Detect when a thread stops beating."""
    
    def __init__(self, max_silence: float):
        self.max_silence = max_silence
        self.last_beat = time.monotonic()
        self._stop = threading.Event()
    
    def beat(self):
        self.last_beat = time.monotonic()
    
    def watch(self):
        while not self._stop.wait(self.max_silence / 2):
            if (time.monotonic() - self.last_beat) > self.max_silence:
                self._on_hang()
    
    def _on_hang(self):
        # Can't kill a Python thread cleanly; force-exit the process
        import os, signal
        os.kill(os.getpid(), signal.SIGTERM)  # let the supervisor restart
```

### Pattern 5 — Deadlock detector

```python
import sys
import threading
import time
import traceback

def dump_all_thread_stacks():
    """Print stack traces of all threads (useful when watchdog fires)."""
    for thread_id, frame in sys._current_frames().items():
        print(f"=== Thread {thread_id} ===")
        traceback.print_stack(frame)

class DeadlockDetector:
    """Periodically check all threads; if all blocked on locks, dump and exit."""
    
    def __init__(self, check_interval: float = 30.0):
        self.check_interval = check_interval
    
    def run(self):
        while True:
            time.sleep(self.check_interval)
            if self._all_threads_blocked():
                dump_all_thread_stacks()
                os._exit(1)  # supervisor will restart
```

**Distinguishing watchdog from health check:**

- **Watchdog:** internal heartbeat from inside the process. "I'm alive; my main loop is running."
- **Health check** ([[14-health-checks]]): external probe. "Can you respond to this query?"

Use both. Watchdog catches "main loop wedged"; health check catches "can't service requests."

## 3. Key works / libraries

- **Linux Watchdog API** — kernel.org/doc/Documentation/watchdog/. `/dev/watchdog` for hardware-backed.
- **systemd `WatchdogSec`** — freedesktop.org/software/systemd/man/systemd.service.html.
- **`sdnotify`** — github.com/bb4242/sdnotify. Python systemd notify-protocol library.
- **`watchdog`** (Python library, github.com/gorakhargosh/watchdog) — *different thing* — it watches the filesystem, not processes.
- **`py-spy`** — github.com/benfred/py-spy. Attach to a running Python process to see thread stacks. Useful diagnostic when watchdogs fire.
- **`hangwatch`-style implementations** — many ad-hoc Python implementations in various open-source projects.
- **Erlang's `:erlang.system_monitor`** — runtime-level hang detection.

## 4. Pitfalls and gotchas

- **Watchdog interval vs operation time.** If a normal operation takes 60 seconds but watchdog is 10 seconds, you get false positives. Watchdog interval must exceed longest legitimate operation.
- **Beating without checking progress.** A loop that beats but isn't making progress is still alive to the watchdog. Beat must be tied to *real* progress, not "I'm still running this loop."
- **Heartbeat from inside the hung subsystem.** If the heartbeat thread itself hangs, no signal. Use a separate thread / async task that *only* heartbeats, doesn't do work.
- **`os._exit(1)` doesn't call atexit handlers.** Acceptable per crash-only design ([[11-crash-only-software]]).
- **`asyncio.shield`** prevents cancellation; watchdog needs an explicit other path (process kill).
- **Forking copies file descriptors** including the systemd notify socket. After fork, the child can't notify on its own.
- **Watchdog firing during legitimate slow operation** (e.g., long ML inference). Tune interval, or pause watchdog during known-long operations.

## 5. Applicability to Runa

For **services** (each in its own process):

- Each service uses systemd's `WatchdogSec` if available. `sdnotify` calls per main-loop iteration.
- `Restart=on-watchdog` ensures systemd restarts on hang.
- `WatchdogSec` set to ~2× longest expected operation in the service.

For **kernel turn execution**:

- Each turn has a deadline ([[09-timeout-patterns]]). The deadline is the watchdog at the turn level.
- A turn that exceeds 2× deadline is forcibly cancelled by Eir, who logs the stack trace.

For **adapters**:

- Per-adapter watchdog: an adapter's `run()` loop must `beat()` periodically. Hang → restart.
- A hung adapter holding a Discord connection is exactly the failure watchdog catches.

For **Hirð retainers**:

- Long-running retainer tasks (e.g., Huginn doing extended research) beat per major step. Hang detection scales with the size of a "step."

For **Eir**:

- Eir runs the per-subsystem watchdogs. Hangs are logged with full stack traces and trigger restart via the supervisor.
- A high rate of watchdog-triggered restarts indicates a real bug; escalate to `Notified`.

For **diagnostic outputs**:

- When a watchdog fires, capture: thread/task stacks, current event-loop state, in-flight requests. This data goes to the audit log as a `Crashed` event.

For **deploy/pi/**:

- Pi 5 deployment includes a small kernel-watchdog config that resets the Pi if Linux itself hangs. Last-resort defence.

What to avoid:

- Don't set watchdog intervals too tight. False positives erode trust.
- Don't beat in a thread that does work. Beat in a thread that *only* beats.
- Don't hide watchdog fires. Always log with diagnostics.
- Don't use watchdog as a substitute for proper timeout discipline. Watchdog is the safety net; timeouts are the structure.

## 6. Open questions

- **Watchdog for asyncio tasks under heavy load.** A normal but congested event loop can fail to beat in time. Distinguishing "hung" from "slow" is hard.
- **Hierarchy of watchdogs.** Per-task + per-service + per-process + per-machine. Each level catches different failure modes; designing them coherently takes thought.
- **Detecting deadlock vs just-slow.** Many "deadlocks" are actually deadlocks-eventually — they'd resolve if you waited longer. Threshold tuning is empirical.

## 7. References (curated)

- kernel.org/doc/Documentation/watchdog/ — Linux watchdog API.
- freedesktop.org/software/systemd/man/systemd.service.html — systemd WatchdogSec.
- github.com/bb4242/sdnotify — sdnotify Python.
- github.com/benfred/py-spy — py-spy diagnostic.
- engineering.linkedin.com — search "watchdog" for production examples.
- Companion docs: [[11-crash-only-software]], [[12-supervisor-trees]], [[14-health-checks]].

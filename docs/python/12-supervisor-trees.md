# 12 — Supervisor Trees in Python

**Category:** Self-Healing & Supervision
**Runa relevance:** Eir (Runa's supervisor), runtime supervisor for services, intra-service TaskGroup supervision
**Status:** Python craft. Erlang-inspired pattern brought to Python.
**Last touched:** 2026-05-17

---

## 1. Core idea

In Erlang/OTP, the **supervisor tree** is *the* organising principle for fault-tolerant systems. A supervisor is a special process whose only job is to start, watch, and restart child processes. Children can themselves be supervisors, forming a tree. When a child fails, its supervisor decides: restart this one, restart all children, restart from this child down, or escalate up. The discipline produces systems where component failure is *normal* and *automatically corrected*.

Python doesn't have OTP. But the *patterns* — process supervisors, task supervisors, restart strategies — are recreatable, and many production Python systems are organised as supervisor trees (often without using that name). For Runa, the supervisor pattern shows up at three levels: systemd at the OS process level, the runtime supervisor at the in-Python process lifecycle level, and `asyncio.TaskGroup` at the in-coroutine level. Each is a different scale; the principles compose.

## 2. Technique / mechanism

**The four standard restart strategies (Erlang heritage):**

1. **`one_for_one`** — child dies, restart only that child. Default for independent children.
2. **`one_for_all`** — child dies, restart *all* children. Use when children share state and must restart together.
3. **`rest_for_one`** — child dies, restart it and any later-started siblings (those that depend on it).
4. **`simple_one_for_one`** — dynamic pool of identical children.

**Restart intensity:** "at most N restarts in T seconds; if exceeded, escalate to parent supervisor." Prevents infinite restart loops.

**Level 1 — OS process supervision (systemd):**

```ini
# /etc/systemd/user/runa-core.service
[Unit]
Description=Runa Core
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/runa worker
Restart=on-failure
RestartSec=5s
StartLimitInterval=300
StartLimitBurst=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

systemd is the outermost supervisor. The Python process exits; systemd restarts with backoff. `StartLimitBurst=10 / StartLimitInterval=300` is the restart-intensity equivalent.

**Level 2 — in-process service supervisor:**

```python
import asyncio
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ChildSpec:
    name: str
    coro_factory: Callable[[], Awaitable[None]]
    restart_strategy: str = "permanent"  # "permanent" | "transient" | "temporary"

@dataclass
class Supervisor:
    strategy: str = "one_for_one"  # one_for_one | one_for_all | rest_for_one
    max_restarts: int = 5
    max_seconds: int = 30
    children: list[ChildSpec] = field(default_factory=list)
    
    _restart_times: list[float] = field(default_factory=list)
    
    async def run(self):
        async with asyncio.TaskGroup() as tg:
            self._tasks: dict[str, asyncio.Task] = {}
            for spec in self.children:
                self._tasks[spec.name] = tg.create_task(self._supervise_child(spec))
    
    async def _supervise_child(self, spec: ChildSpec):
        while True:
            try:
                await spec.coro_factory()
                if spec.restart_strategy == "permanent":
                    logger.warning("child %s exited normally; restarting", spec.name)
                elif spec.restart_strategy in ("transient", "temporary"):
                    logger.info("child %s exited normally; not restarting", spec.name)
                    return
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error("child %s crashed: %r", spec.name, exc, exc_info=exc)
                if spec.restart_strategy == "temporary":
                    logger.info("child %s crashed; not restarting (temporary)", spec.name)
                    return
                self._record_restart()
                if self._exceeded_intensity():
                    raise SupervisorFailedError(f"too many restarts in window")
                await asyncio.sleep(self._backoff())  # exponential backoff
    
    def _record_restart(self) -> None:
        now = time.monotonic()
        self._restart_times.append(now)
        # Drop restarts outside the window
        cutoff = now - self.max_seconds
        self._restart_times = [t for t in self._restart_times if t >= cutoff]
    
    def _exceeded_intensity(self) -> bool:
        return len(self._restart_times) > self.max_restarts
    
    def _backoff(self) -> float:
        return min(30.0, 0.5 * 2 ** len(self._restart_times))
```

Usage:

```python
supervisor = Supervisor(
    strategy="one_for_one",
    max_restarts=5,
    max_seconds=30,
    children=[
        ChildSpec("muninn_writer", muninn_writer_loop),
        ChildSpec("skuld_executor", skuld_executor_loop),
        ChildSpec("eir_monitor", eir_monitor_loop),
    ],
)
await supervisor.run()
```

**Level 3 — in-task supervision (`asyncio.TaskGroup`):**

```python
async with asyncio.TaskGroup() as tg:
    tg.create_task(stream_inputs())
    tg.create_task(process_inputs())
    tg.create_task(emit_outputs())
# If any task raises, the others are cancelled and an ExceptionGroup raised.
```

`TaskGroup` is supervisor-like for short-lived task collections. Different shape from long-running supervisor trees but the same essential pattern.

**The restart strategy table:**

| Use case | Strategy | Why |
|---|---|---|
| Independent adapters | `one_for_one` | A Discord crash shouldn't restart Telegram. |
| Tightly-coupled stages of a pipeline | `one_for_all` | If the encoder dies, the decoder's input is stale. |
| Dependency chain (DB then app) | `rest_for_one` | DB up, app started. App fails → restart app. DB fails → restart DB and app. |
| Worker pool | `simple_one_for_one` | Replace failed workers individually. |

## 3. Key works / libraries

- **Armstrong, J.** *Programming Erlang*, 2nd ed., Pragmatic Bookshelf, 2013. The supervisor-tree foundation.
- **Erlang/OTP supervisor design principles** — erlang.org/doc/design_principles/sup_princ.html.
- **`circus`** — github.com/circus-tent/circus. Python process supervisor; mature.
- **`supervisord`** — supervisord.org. Older but still widely used.
- **systemd documentation** — freedesktop.org/wiki/Software/systemd/.
- **`asyncio.TaskGroup`** (PEP 654, Python 3.11+).
- **`anyio.create_task_group`** — async-library-agnostic alternative.
- **`trio.Nursery`** — Trio's name for TaskGroup; the original.

## 4. Pitfalls and gotchas

- **Infinite restart loops.** Without intensity limits, a crashing-on-startup child restarts forever. Always cap.
- **State preservation across restarts.** A restarted child starts fresh. State that must survive belongs in persistent storage, not in the child.
- **Cascading restarts.** `one_for_all` can chain: child fails → all restart → another fails → all restart → loop. Use `one_for_all` only when truly necessary.
- **Supervisor itself can crash.** Then the outer supervisor restarts the inner. Eventually systemd is the floor.
- **Asynchronous startup dependencies.** Child A needs to be ready before child B. Order children carefully; use explicit health-check gating ([[14-health-checks]]).
- **Restart backoff too short.** Hammering a downstream service.
- **Restart backoff too long.** Long downtime during recovery.
- **`asyncio.TaskGroup` exception handling subtleties.** The first exception cancels siblings; subsequent exceptions during cancellation become ExceptionGroup. Code should be prepared.
- **CancelledError must be re-raised.** Catching and swallowing `CancelledError` in a supervised task makes the supervisor unable to cancel cleanly.

## 5. Applicability to Runa

For **systemd-level supervision (deploy/systemd/)**:

- Each service (`runa-core`, `runa-gateway`, `runa-worker`, `runa-voice`, `runa-gui`) gets its own systemd unit.
- `Restart=on-failure` with `RestartSec=5s` and `StartLimitBurst=10 / StartLimitInterval=300`.
- Logs go to journal; `runa logs` reads them.

For **Eir (Runa's in-process supervisor)**:

- Eir runs the in-process supervisor logic for in-kernel coroutines: adapters, retainers, background jobs.
- `one_for_one` strategy for adapters (independent).
- `one_for_all` for kernel + event bus (kernel can't run without VERÐANDI).
- Per-subsystem restart intensity tracked; sustained restarts escalate to `Notified` event for Volmarr.

For **kernel turn supervision** (`asyncio.TaskGroup`):

- Each turn is wrapped in TaskGroup. Sub-tasks (retrieval, tool calls, model call) run as children.
- Failure of one cancels siblings; the turn fails cleanly with an ExceptionGroup.
- Per-turn isolation: a failed turn doesn't damage the kernel.

For **Hirð retainer supervision**:

- Hirð is itself a supervisor for retainers. Each retainer runs as a long-lived async task supervised by the Hirð supervisor.
- Restart strategy: `one_for_one` (retainers don't share state directly).
- Retainer fail counts feed into Eir's escalation logic.

For **worker pool (Smiðja's multiprocessing pool)**:

- Worker processes supervised by `ProcessPoolExecutor`. Failed workers replaced.
- `simple_one_for_one` semantics.

For **adapters**:

- Each adapter (Discord, Telegram, MCP server) is supervised by Eir.
- Crash → log → backoff → restart. After N restarts in window, quarantine.

What to avoid:

- Don't make children depend on each other through hidden state. Restart of one then orphans the other.
- Don't hide restart events. Operator must see them.
- Don't write supervised code that ignores `CancelledError`.
- Don't put cleanup-required-for-correctness in supervised tasks. Crash-only ([[11-crash-only-software]]) discipline.

## 6. Open questions

- **Cross-service supervision.** When the gateway service can detect the worker service is dead (separate process), should it act? Usually systemd does this; sometimes inter-service health-checking is useful.
- **Distributed supervision.** When Runa runs across Pi + laptop, supervising remote tasks is harder. Ray and similar frameworks handle this.
- **Hot reload during supervision.** Replacing a child's code without crash. Erlang does this; Python supports it via `importlib.reload` but with caveats.

## 7. References (curated)

- Armstrong, *Programming Erlang*, 2nd ed.
- erlang.org/doc/design_principles/sup_princ.html — OTP supervisor doc.
- python.org/3/library/asyncio-task.html#task-groups — asyncio TaskGroup.
- freedesktop.org/software/systemd/man/systemd.service.html — systemd.service spec.
- circus.readthedocs.io — Circus.
- vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/ — Smith's structured concurrency essay; supervisor adjacent.
- Companion docs: [[11-crash-only-software]], [[13-watchdog-timers]], [[14-health-checks]], [[19-asyncio-advanced]], [[50-long-running-processes]].

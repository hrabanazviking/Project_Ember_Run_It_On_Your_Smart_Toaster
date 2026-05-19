# 19 — asyncio Advanced Patterns: TaskGroup, Timeout, Cancellation

**Category:** Concurrency Mastery
**Runa relevance:** kernel loop, VERÐANDI bus, every adapter, every service shell
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

The basic asyncio model (async/await, coroutines, tasks) is straightforward. The *advanced* patterns — `TaskGroup`, `timeout`, `Shield`, structured cancellation, `ContextVar` propagation, `Queue`-based coordination, sub-event-loops — are what separate "I can write async code" from "I can write async code that survives production." This is the layer where Runa's kernel actually lives.

Per ADR-0002 §D-2.1, Runa's kernel is asyncio-based. The 3.11+ improvements ([[23-asyncio-structured-concurrency]] research doc) make this far better than asyncio's first decade — but using the new patterns correctly requires conscious craft.

## 2. Technique / mechanism

**TaskGroup (Python 3.11+):**

```python
async def kernel_turn(heard: Heard) -> Replied:
    async with asyncio.TaskGroup() as tg:
        muninn_task = tg.create_task(muninn.retrieve(heard.text))
        eldhugi_task = tg.create_task(eldhugi.current_state())
        wyrd_task = tg.create_task(wyrd_bridge.recent_changes())
    # All three completed by the time we get here.
    # If any raised, ExceptionGroup is raised; the others were cancelled cleanly.
    context = build_context(muninn_task.result(), eldhugi_task.result(), wyrd_task.result())
    ...
```

`TaskGroup` provides *structured concurrency*: spawned tasks have a clear lifetime tied to the `async with` block. No leaked tasks. Errors compose via `ExceptionGroup`.

**Timeout (Python 3.11+):**

```python
async def with_deadline(work, *, seconds: float):
    async with asyncio.timeout(seconds):
        return await work()

# Or absolute:
async def call_with_deadline(work, *, deadline_monotonic: float):
    async with asyncio.timeout_at(deadline_monotonic):
        return await work()
```

Composes with TaskGroup. Triggers `TimeoutError` if the block doesn't finish in time.

**Cancellation — the essential discipline:**

Cancellation in asyncio is *cooperative*. When a task is cancelled, a `CancelledError` is raised at the next `await`. The task can:

1. **Propagate** — re-raise. The default and almost-always-correct behaviour.
2. **Clean up briefly** — catch, do quick cleanup, re-raise.
3. **Refuse** (rare) — catch and continue. Only when you *really* know what you're doing.

```python
async def well_behaved_worker():
    try:
        while True:
            await do_one_unit_of_work()
    except asyncio.CancelledError:
        # Quick cleanup
        await close_resources()
        raise  # always re-raise
```

**`asyncio.shield` — protect critical sections:**

```python
async def commit_to_disk():
    # Don't allow this to be cancelled mid-write
    await asyncio.shield(write_atomic())
```

If the outer task is cancelled while `write_atomic` is running, the cancel is held back; the write completes; the cancel takes effect after.

Use sparingly. Most code should be cancellable.

**ContextVar for cross-task propagation:**

```python
from contextvars import ContextVar

correlation_id: ContextVar[UUID | None] = ContextVar("correlation_id", default=None)

async def handle_heard(heard: Heard):
    token = correlation_id.set(heard.event_id)
    try:
        await process_turn()
    finally:
        correlation_id.reset(token)

# Anywhere downstream:
async def log_something():
    cid = correlation_id.get()
    logger.info("doing thing", correlation_id=str(cid))
```

`ContextVar` carries values through asyncio call chains without explicit parameter passing. Each task has its own context (copied at task creation).

**Queue patterns:**

```python
queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=1000)

# Producer
async def producer():
    while True:
        event = await detect_event()
        await queue.put(event)  # blocks if queue full → backpressure

# Consumer
async def consumer():
    while True:
        event = await queue.get()
        try:
            await process(event)
        finally:
            queue.task_done()

# Wait for all queued items to be processed
await queue.join()
```

Bounded queue is essential — unbounded queues invite memory exhaustion.

**Pub/sub via Queue fan-out:**

```python
class VerdandiBus:
    """Simple pub/sub. Each subscriber has its own queue."""
    
    def __init__(self):
        self._subscribers: list[asyncio.Queue] = []
    
    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue(maxsize=1000)
        self._subscribers.append(q)
        return q
    
    async def publish(self, event: Event):
        for q in self._subscribers:
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning("subscriber queue full; dropping event")
```

**Bridging async and sync — `asyncio.to_thread`:**

```python
async def read_big_file():
    # Blocking I/O in a thread, awaitable
    return await asyncio.to_thread(some_blocking_read, path)
```

Short blocking operations. For CPU-bound, see [[24-multiprocessing]].

**Run async from sync:**

```python
import asyncio

def cli_entry():
    asyncio.run(main())
```

`asyncio.run` creates the loop, runs the coroutine, cleans up. Don't manage the loop manually.

**Sleep-without-blocking:**

```python
await asyncio.sleep(1.0)  # asyncio-aware, doesn't block the loop
time.sleep(1.0)            # WRONG in async code; blocks the loop
```

**`asyncio.gather` (legacy but still useful):**

```python
results = await asyncio.gather(*coros, return_exceptions=False)
```

Older than TaskGroup. Doesn't provide structured-concurrency guarantees but is fine for fire-many-await-all patterns. Migrate to TaskGroup in new code.

## 3. Key works / libraries

- **PEP 492** — coroutines with async/await.
- **PEP 525, 530** — async generators, async iteration.
- **PEP 567** — Context Variables (`ContextVar`).
- **PEP 654** — Exception Groups.
- **PEP 678** — Exception Notes.
- **asyncio documentation** — docs.python.org/3/library/asyncio.html.
- **Smith, N.** "Notes on structured concurrency..." (2018, vorpus.org). The essay.
- **Trio** — trio.readthedocs.io. The cleaner alternative; influenced asyncio's 3.11+ changes.
- **anyio** — anyio.readthedocs.io. Cross-asyncio/trio.

## 4. Pitfalls and gotchas

- **Forgetting to `await`.** A coroutine that's never awaited generates a RuntimeWarning and never runs.
- **Bare `create_task(...)` without holding a reference.** The task can be garbage-collected mid-execution. Hold the reference; use TaskGroup.
- **Blocking calls in async code.** A `requests.get`, a `time.sleep`, a `subprocess.run`, a `cpu_heavy()` — all block the loop. Use httpx/asyncio.sleep/asyncio.create_subprocess_exec/`asyncio.to_thread`.
- **`asyncio.get_event_loop()` deprecated.** Use `asyncio.get_running_loop()` (only valid inside async code) or `asyncio.run` to manage the loop.
- **Mixing event loops.** `asyncio.run` inside an existing event loop → RuntimeError. For nested loops, use `nest_asyncio` library (with caveats) or restructure.
- **Catching CancelledError without re-raising.** Breaks supervisor cancellation; task becomes uncancellable.
- **Asyncio.sleep with very small intervals.** ~1ms is fine; sub-millisecond is bad-imprecise-and-CPU-hungry.
- **`asyncio.Lock` vs `threading.Lock`.** Different objects; not interchangeable. Use the asyncio one in async code.
- **Stateful Futures across loops.** A Future created in one loop cannot be awaited in another.

## 5. Applicability to Runa

For **the kernel turn loop**:

- Each turn is a `TaskGroup` block. Parallel: retrieval, emotional-state load, world-context load.
- `asyncio.timeout()` wraps each turn with a per-surface deadline.
- `ContextVar` carries correlation_id through the turn for tracing.

For **VERÐANDI bus**:

- `asyncio.Queue`-based fan-out. Bounded queues with backpressure semantics.

For **adapters**:

- Each adapter is a long-running coroutine. Its lifecycle is managed by `asyncio.TaskGroup` under Eir's supervision.
- Adapter cancellation cleans up its connection state and re-raises.

For **Heimskringla calls**:

- Provider calls happen inside `asyncio.timeout()` per the deadline + per-provider operation timeout.
- Retry logic uses `asyncio.sleep` between attempts.

For **Skuld task execution**:

- Each task runs in its own asyncio task spawned in a TaskGroup with a per-task deadline.

For **bridging to blocking work**:

- `asyncio.to_thread` for short blocking calls (file I/O, simple subprocess).
- Process pool ([[24-multiprocessing]]) for sustained CPU.

What to avoid:

- Don't use raw `create_task` without TaskGroup or explicit tracking. Leaks invite bugs.
- Don't suppress CancelledError. Cancellation is a contract.
- Don't share state across tasks without `asyncio.Lock`. Race conditions silent.
- Don't perform I/O without a timeout. Even in async code.

## 6. Open questions

- **Free-threaded Python (PEP 703, 3.13+).** Interaction between no-GIL threads and asyncio is unsettled. Watch this space.
- **`asyncio.eager_task_factory` (3.12+).** Tasks run synchronously until first await. Performance win in some cases; semantic implications nuanced.
- **Subinterpreters (PEP 734, 3.13+).** Per-interpreter event loops. Promising for isolation.

## 7. References (curated)

- docs.python.org/3/library/asyncio.html — official.
- vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/ — Smith's essay.
- trio.readthedocs.io — Trio.
- anyio.readthedocs.io — anyio.
- PEPs 492, 525, 530, 567, 654, 678.
- Companion docs: [[09-timeout-patterns]], [[12-supervisor-trees]], [[23-async-cancellation]], [[24-queue-channel-patterns]].

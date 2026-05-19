# 23 — asyncio Internals and Structured Concurrency in Python 3.11+

**Category:** Event-Driven & Concurrency
**Runa relevance:** VERÐANDI (kernel loop), services (asyncio servers), adapters (concurrent I/O)
**Status:** Research synthesis with a strong practical orientation.
**Last touched:** 2026-05-17

---

## 1. Core idea

Per ADR-0002 §D-2.1, Runa's kernel runs on an asyncio event loop with a multiprocessing worker pool for CPU-bound work. asyncio is the de facto concurrency model for I/O-heavy Python services: a single thread cooperatively schedules thousands of pending tasks. Python 3.11 was a watershed — `asyncio.TaskGroup`, `asyncio.timeout`, `except*` (exception groups) brought *structured concurrency* into the standard library, making async code dramatically safer and more reasonable to read.

The shift from "raw `create_task` and pray" to "always under a TaskGroup" is the same shift `goto` → structured-programming was for synchronous code. Code written today should look different from code written for asyncio in 2018, and Runa's code should look like 2025+ idiom from day one.

## 2. Technical depth

**The event loop, briefly.** asyncio runs a single-threaded event loop that:
1. Pops the next ready coroutine.
2. Runs it until it `await`s something.
3. If the awaited future isn't ready, the coroutine is paused; the loop selects the next ready coroutine.
4. When I/O completes (selector returns), waiting coroutines become ready.

All coroutines share the same Python thread. No true parallelism; only concurrency. Cooperative — a coroutine that doesn't `await` blocks the whole loop.

**Structured concurrency.** The principle: every spawned task has a well-defined lifetime tied to a scope. When the scope exits, all child tasks must have completed (or been cancelled and awaited). No "fire-and-forget" tasks leaking memory and uncaught exceptions.

The asyncio API for this is **`asyncio.TaskGroup`** (3.11+):

```python
async with asyncio.TaskGroup() as tg:
    task1 = tg.create_task(fetch_thing())
    task2 = tg.create_task(other_thing())
    # block exits only when both tasks complete

# tasks are joined and exceptions raised before this line runs
```

If *any* child task raises, all other tasks in the group are *cancelled*, all are awaited, and the exceptions are re-raised together as an `ExceptionGroup` (PEP 654). Cleaner than `asyncio.gather(return_exceptions=True)`, which silently collects exceptions.

**`asyncio.timeout()`** (3.11+):

```python
async with asyncio.timeout(5.0):
    result = await something()
```

Triggers a `TimeoutError` if the block doesn't finish in 5 seconds. Composes with TaskGroup. Cleaner than the older `asyncio.wait_for()`.

**Key 3.11+ asyncio additions:**
- `asyncio.TaskGroup`
- `asyncio.timeout`, `asyncio.timeout_at`
- `asyncio.Runner` (manages loop lifecycle for scripts)
- `ExceptionGroup` and `except*` syntax
- `asyncio.eager_task_factory` (3.12) — tasks run synchronously until first await
- `asyncio.Barrier`, `asyncio.Queue` improvements

**Common patterns:**

**Fan-out / fan-in:**
```python
async with asyncio.TaskGroup() as tg:
    tasks = [tg.create_task(query(i)) for i in items]
# all queries done; results in tasks[i].result()
```

**Cancellation:**
- Cancellation is cooperative: it raises `CancelledError` at the next `await`. A coroutine ignoring `CancelledError` is a bug.
- Always re-raise `CancelledError` from a try/except unless you explicitly handle the cancellation contract.

**Background services:**
```python
async def supervisor():
    while True:
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(adapter_a())
                tg.create_task(adapter_b())
        except* AdapterError as eg:
            for exc in eg.exceptions:
                logger.warning("adapter failed", exc_info=exc)
            await asyncio.sleep(backoff)
            continue
```

**Bridging to threads/processes:**
- `asyncio.to_thread(func, *args)` — run a blocking sync function in a thread, await it. For short blocking calls (file I/O, blocking C extension).
- `loop.run_in_executor(pool, func, ...)` — run in a `ProcessPoolExecutor` for CPU-bound. See [[24-multiprocessing-worker-pools]].

**Anti-patterns to retire:**

- `asyncio.gather(*tasks, return_exceptions=True)` — replace with TaskGroup.
- `asyncio.wait_for(task, timeout)` — replace with `asyncio.timeout()`.
- `asyncio.ensure_future` for fire-and-forget — replace with proper TaskGroup scoping.
- Bare `loop = asyncio.get_event_loop()` — replace with `asyncio.run()` or `asyncio.Runner`.

**Beyond asyncio — Trio, the other answer:**

- **Trio** (Nathaniel Smith, 2017+) — a from-scratch async library built around structured concurrency from day one. Cleaner than asyncio. Influenced asyncio's 3.11 changes.
- **anyio** — provides a unified API over asyncio and Trio. Lets libraries support both.

Trio's "nursery" (their TaskGroup) is the source of the structured-concurrency design now in asyncio. Smith's 2018 essay "Notes on structured concurrency, or: Go statement considered harmful" is the foundational argument.

## 3. Key works

- **van Rossum, G. et al.** PEP 3156 (Asynchronous IO Support), PEP 492 (Coroutines via async/await), PEP 654 (Exception Groups), PEP 678 (Enriching exceptions with notes).
- **Smith, N. "Notes on structured concurrency, or: Go statement considered harmful."** vorpus.org, 2018. The essay that named and popularised structured concurrency.
- **Beazley, D. *Curio* talks and PyCon presentations** — early Python structured-concurrency experiments.
- **Trio documentation** — trio.readthedocs.io.
- **asyncio documentation** — docs.python.org/3/library/asyncio.html. Especially the 3.11+ sections.
- **Hettinger, R. "Modern Python's `asyncio`" PyCon talks** — pedagogical.

## 4. Empirical results

- A well-written asyncio service on commodity hardware (single core) handles tens of thousands of concurrent connections at meaningful throughput. The classic Python-server benchmarks (uvicorn, aiohttp) consistently land asyncio in the top tier per CPU.
- TaskGroup vs gather: catches more bugs in code-review. Empirical from many production migrations: leaked-task bugs (the old "I spawned a task and forgot to await it") drop to ~zero after a TaskGroup-only convention.
- `asyncio.timeout` vs `wait_for`: cleaner composition with cancellation; fewer subtle "this timeout cancelled the wrong task" bugs.
- ExceptionGroups change debugging: a single task failing inside a TaskGroup now produces a clear group-of-exceptions traceback instead of a sea of "X was never awaited" warnings.

## 5. Applicability to Runa

For **the kernel loop**:

- The kernel is one async coroutine running under `asyncio.Runner`. It consumes events from VERÐANDI, dispatches to skills under TaskGroups, awaits, emits results.
- Per-turn TaskGroup: each kernel turn (one `Heard` → one `Replied`) lives inside an `asyncio.TaskGroup` that bounds all the tool calls / subagent dispatches / memory ops for that turn. If any sub-task fails, the turn fails cleanly.
- `asyncio.timeout()` wraps each tool call with a config-pinned timeout. Slow tools don't stall the kernel.

For **services**:

- Each service (`gateway_service`, `worker_service`, `voice_service`) has its own top-level Runner. They communicate with the kernel via VERÐANDI events; each service is its own process for failure isolation.

For **adapters**:

- Adapters are TaskGroup-supervised inside their parent service. An adapter crash raises into the service's supervisor, which logs, quarantines, and continues without that adapter.

For **VERÐANDI itself**:

- A pure-asyncio implementation suffices: an `asyncio.Queue` per topic, subscribers register coroutines. ADR-0002 §D-2.1 deferred wire-format decisions; an in-process bus that passes typed objects is the simplest choice.

Recommended convention:

- **Every spawned task is inside a TaskGroup.** No bare `create_task`.
- **Every external I/O is wrapped in `asyncio.timeout()`.** Config-pinned timeouts.
- **No bare `except:` or `except Exception:`.** Catch specific types or use `except*` for ExceptionGroups.
- **Always re-raise `CancelledError`** unless explicitly handling a cancellation contract.
- **Use `anyio`** for any library code that could be reused outside Runa, to keep options open for Trio compatibility.

What to avoid:

- Don't mix asyncio with threading without understanding the boundaries. `asyncio.to_thread` for short blocking calls, `loop.run_in_executor` with ProcessPoolExecutor for sustained CPU. Don't `asyncio.run` from inside an existing loop.
- Don't use `asyncio.Event` when an `asyncio.Queue` would be cleaner.
- Don't import any sync-blocking library and call it from a coroutine without `to_thread`-ing it. A single blocking call stalls the entire loop.
- Don't write your own event loop. asyncio's loop is good enough.

## 6. Open questions

- **The future of structured concurrency in Python.** PEP 695 (type-parameter syntax, 3.12) and ongoing PEPs continue to refine the async story. Trio's influence keeps showing up.
- **No-GIL Python.** PEP 703 (3.13+) makes free-threaded Python possible. The interaction between no-GIL threads and asyncio is unsettled. Eventually, true parallelism without multiprocessing.
- **Subinterpreters.** PEP 734 (3.13) brings real per-thread interpreters. Promising for an alternative to multiprocessing for CPU work.
- **Async generators and async iterators.** Less elegant than sync equivalents; performance overhead remains.

## 7. References (curated)

- docs.python.org/3/library/asyncio.html — current asyncio docs.
- vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/ — Smith's essay.
- trio.readthedocs.io — Trio.
- anyio.readthedocs.io — anyio.
- PEP 492 — Coroutines with async/await.
- PEP 654 — Exception Groups.
- PEP 703 — Making the Global Interpreter Lock Optional in CPython.
- Companion docs: [[21-actor-model-supervision]] (the conceptual frame), [[24-multiprocessing-worker-pools]] (the CPU side).

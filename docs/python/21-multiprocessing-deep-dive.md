# 21 — multiprocessing Deep-Dive: spawn vs fork, IPC

**Category:** Concurrency Mastery
**Runa relevance:** Smiðja worker pool (ADR-0002 §D-2.1), Hirð/Völundr for heavy codegen
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

The GIL ([[20-thread-safety-python]]) makes threading useless for CPU-bound work. `multiprocessing` is Python's answer: spawn separate processes, each with its own interpreter and GIL. The cost is IPC overhead and a serialisation boundary; the benefit is true parallelism. ADR-0002 §D-2.1 commits Runa to a multiprocessing worker pool for CPU-bound work alongside the asyncio kernel.

The patterns are well-trodden; the pitfalls are also well-trodden. The most consequential decision is **start method** (spawn vs fork). The wrong choice produces hard-to-debug failures, especially when combined with asyncio.

## 2. Technique / mechanism

**Start methods:**

```python
import multiprocessing as mp

mp.set_start_method("spawn", force=True)  # set ONCE at the start of the program
```

- **`spawn`** (Windows default; macOS default since 3.8). Child starts fresh, re-imports the program. Slower startup; safer.
- **`fork`** (Linux historical default). Child inherits parent's memory via copy-on-write. Faster startup; *unsafe with threads*, *unsafe with asyncio*.
- **`forkserver`** (Linux only). A dedicated forkserver process forks new workers from a clean state.

**Strong recommendation: use `spawn`.** Cross-platform safety. Startup cost paid once at pool creation; amortised across many jobs.

**ProcessPoolExecutor (the high-level API):**

```python
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(
    max_workers=4,
    mp_context=mp.get_context("spawn"),
    initializer=worker_setup,
    initargs=(config,),
    max_tasks_per_child=100,
) as pool:
    future = pool.submit(cpu_function, arg1, arg2)
    result = future.result(timeout=30)
```

- `initializer` runs once per worker. Load heavy state here (LLM, model files).
- `max_tasks_per_child` recycles workers periodically; defeats memory leaks.
- `mp_context` lets you pin start method.

**Bridging asyncio + ProcessPool:**

```python
loop = asyncio.get_running_loop()

async def offload(fn, *args):
    return await loop.run_in_executor(POOL, fn, *args)

# Inside an async coroutine:
result = await offload(cpu_intensive, data)
```

The asyncio loop submits to the executor; receives a Future; awaits it. The CPU work happens in the worker process while the loop continues other work.

**Pickling — what crosses the boundary:**

Arguments and return values pickle. Things that don't pickle: lambdas, nested functions, file handles, sockets, asyncio loops, thread locks, many ML library state objects.

**Workaround pattern:**

```python
# WON'T WORK — lambdas don't pickle
pool.submit(lambda x: x * 2, 5)

# WORKS — top-level function
def double(x):
    return x * 2

pool.submit(double, 5)
```

For passing heavy state to workers, prefer:
1. Worker `initializer` loads heavy state once.
2. Pass small handles / IDs across the boundary.
3. Worker fetches what it needs from shared / on-disk state.

**Shared memory:**

```python
from multiprocessing.shared_memory import SharedMemory
import numpy as np

shm = SharedMemory(create=True, size=1024)
arr = np.ndarray((128,), dtype=np.int64, buffer=shm.buf)
# Workers can attach by name:
# SharedMemory(name=shm.name) in worker process
```

Avoid premature use. Most workloads do fine with pickle.

**Queues across processes:**

```python
import multiprocessing as mp

q: mp.Queue = mp.Queue(maxsize=100)

# In one process:
q.put(work_item)

# In another:
item = q.get(timeout=10)
```

`multiprocessing.Queue` is separate from `asyncio.Queue` and `queue.Queue`. Picks-and-pickles internally.

**Manager objects (slow):**

```python
mgr = mp.Manager()
shared_dict = mgr.dict()  # serialised IPC on every access
```

Convenient but slow. Use only for low-frequency state.

**Workers and signal handling:**

Workers inherit signal handlers from parent at spawn time. Custom handlers may need to be set in `initializer`. Default behaviour usually fine.

**Worker logging:**

Each worker is a separate process; stdlib `logging` setup must run in each worker (via `initializer`) to get logs forwarded somewhere useful. Or use `QueueHandler` to centralise logs.

## 3. Key works / libraries

- **`multiprocessing` stdlib** — docs.python.org/3/library/multiprocessing.html.
- **`concurrent.futures` stdlib** — docs.python.org/3/library/concurrent.futures.html.
- **`loky`** — github.com/joblib/loky. Robust process pool used by joblib / scikit-learn.
- **`joblib.Parallel`** — joblib.readthedocs.io. Convenient for embarrassingly-parallel batch work.
- **`Ray`** — docs.ray.io. Distributed task / actor framework; scales beyond single-machine.
- **PEP 703** — no-GIL Python; may reduce reliance on multiprocessing eventually.
- **PEP 734** — subinterpreters; alternative to multiprocessing.
- **Beazley's PyCon talks** on multiprocessing pitfalls.

## 4. Pitfalls and gotchas

- **`fork` + threads = deadlock.** asyncio uses threads. Don't `fork` from a process with asyncio loops or other threads. Use `spawn`.
- **Pickle failures at submit time.** A non-picklable argument fails late. Test the boundary.
- **Memory bloat over time.** Long-lived workers accumulate. Use `max_tasks_per_child` to recycle.
- **Per-worker model load is expensive.** A 7B GGUF model takes seconds to mmap. Load via `initializer` once, not per task.
- **No way to kill a stuck worker cleanly** in `ProcessPoolExecutor`. Shutdown waits for current tasks. For hard kill, use `mp.Process` directly with `terminate()`.
- **Workers don't share asyncio loops.** Each worker is sync (unless you build async inside; rare).
- **Daemon processes can't have children.** If a worker needs to spawn its own subprocesses, it can't be daemon. Watch out.
- **Forking on macOS** (with the old default) has been deprecated for asyncio safety reasons. spawn is default on macOS since 3.8.

## 5. Applicability to Runa

For **Smiðja worker pool** (ADR-0002 §D-2.1):

- ProcessPoolExecutor sized to `min(3, cpu_count() - 1)` on Pi 5.
- `mp_context = mp.get_context("spawn")`.
- `initializer` loads commonly-shared models (the embedding model used by Muninn).
- `max_tasks_per_child = 100` for memory hygiene.

For **Hirð / Völundr (codegen)**:

- Völundr's worker holds the local LLM in memory after first task. Subsequent tasks reuse.
- Pickle thin task descriptors; worker fetches code context from disk.

For **Eir background work**:

- Reflection/consolidation passes submit to the pool. Asyncio kernel awaits results.

For **bridging IPC**:

- Workers communicate results back via Future. Errors propagate via Future exception.
- For longer-running workers needing periodic status: `multiprocessing.Queue` for events flowing back.

For **deploy/pi/**:

- Document the start-method choice. Pi 5's 4 cores + 16 GB easily handle 3 worker processes + asyncio kernel.

What to avoid:

- Don't use `fork`. spawn always.
- Don't pickle large arguments. Pass handles.
- Don't load heavy state per task. initializer.
- Don't share asyncio state across processes. Each is independent.

## 6. Open questions

- **Free-threaded Python.** PEP 703 may eventually let true threads replace processes for some workloads. Tradeoffs unclear.
- **Subinterpreters.** PEP 734 gives parallelism with less isolation cost than multiprocessing. Promising for some uses.
- **Distributed via Ray.** If Runa ever runs across machines, Ray is the natural extension of the process-pool pattern.

## 7. References (curated)

- docs.python.org/3/library/multiprocessing.html.
- docs.python.org/3/library/concurrent.futures.html.
- joblib.readthedocs.io — joblib.
- docs.ray.io — Ray.
- Companion docs: [[19-asyncio-advanced]], [[20-thread-safety-python]], [[22-concurrent-futures-patterns]], [[24-queue-channel-patterns]].

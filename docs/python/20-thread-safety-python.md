# 20 — Thread Safety in Python: GIL, Locks, Atomics

**Category:** Concurrency Mastery
**Runa relevance:** Smiðja thread pools, mixed sync/async boundaries, third-party library callbacks
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Python's **Global Interpreter Lock** (GIL) makes single-Python-statement atomicity easier to reason about than in other languages — but it does *not* make Python automatically thread-safe. Compound operations, lazy-initialised state, mutable shared collections, and the wide world of C extensions that release the GIL all introduce real race conditions. Modern Python (3.13+) is moving toward optional GIL removal (PEP 703), which will make thread safety *much* harder.

For Runa, thread safety matters most at the boundary between asyncio code and thread-pool code, and inside Smiðja's worker pools. The discipline: avoid sharing mutable state across threads; when you must, use the right synchronisation primitive.

## 2. Technique / mechanism

**What the GIL actually protects:**

The GIL serialises *bytecode execution*. One thread runs Python bytecode at a time. This means:

- **Single bytecode operations are atomic** (e.g., `d[k] = v` is one bytecode operation in many cases, though not all).
- **Compound operations are NOT atomic** (e.g., `d[k] += 1` is several bytecode operations; another thread can interleave).
- **C-extension code that releases the GIL runs in parallel** with Python code in other threads. NumPy, threading-aware I/O, etc.

**The classic compound-operation hazard:**

```python
counter = 0

def increment():
    global counter
    counter += 1  # NOT atomic
    # Equivalent to:
    #   temp = counter
    #   temp = temp + 1
    #   counter = temp
    # Two threads can both read the same value before either writes.
```

Fix:
```python
import threading
counter = 0
counter_lock = threading.Lock()

def increment():
    global counter
    with counter_lock:
        counter += 1
```

Or use atomic types:
```python
from itertools import count

counter = count(0)  # thread-safe iterator
next_val = next(counter)
```

**Locks and their variants:**

```python
import threading

lock = threading.Lock()       # mutual exclusion
rlock = threading.RLock()      # re-entrant (same thread can acquire twice)
sem = threading.Semaphore(5)   # bounded concurrency
event = threading.Event()      # signal/wait
condition = threading.Condition()  # wait until some condition is true
```

Use `with` for lock acquisition:

```python
with lock:
    # critical section
```

Always-releases-on-exception via `__exit__`.

**Per-thread state with `threading.local`:**

```python
local = threading.local()

def in_thread():
    local.x = 42  # this thread's x, not shared
```

Each thread has its own attributes. Useful when you genuinely want per-thread state.

**Thread-safe collections:**

- **`queue.Queue`** — thread-safe FIFO. The standard inter-thread communication.
- **`collections.deque`** — append/popleft are thread-safe (single operations).
- **`dict`** — single-key reads/writes are atomic in CPython (de facto). Compound operations are not.

**Pattern: immutable shared, mutable private:**

```python
@dataclass(frozen=True, slots=True)
class Config:
    setting_a: int
    setting_b: str
    # frozen → immutable → safe to share across threads
```

Immutable objects are inherently thread-safe. Use them for shared state.

**Pattern: producer-consumer via Queue:**

```python
work_queue: queue.Queue = queue.Queue(maxsize=100)

def producer():
    for item in source():
        work_queue.put(item)  # blocks if full → backpressure

def consumer():
    while True:
        item = work_queue.get()
        try:
            process(item)
        finally:
            work_queue.task_done()
```

No shared state except the queue, which is internally synchronised.

**Avoid: shared mutable dicts/lists.**

If you must share a dict, all access goes through a lock. Often a `Queue` or `concurrent.futures` pattern is cleaner.

**asyncio + threads — `loop.run_in_executor` and `asyncio.to_thread`:**

```python
async def handle():
    # Offload blocking work to a thread
    result = await asyncio.to_thread(blocking_call, args)
    return result
```

The asyncio side is single-threaded; the thread runs in a thread pool. The result returns via Future. No shared mutable state between sides.

**Calling async code from threads:**

```python
import asyncio

def thread_worker(loop: asyncio.AbstractEventLoop):
    # Run a coroutine on the asyncio loop from this thread
    future = asyncio.run_coroutine_threadsafe(some_coro(), loop)
    result = future.result(timeout=10)
```

`asyncio.run_coroutine_threadsafe` is the safe bridge from threads back into the loop.

**Common thread-unsafe patterns:**

- Lazy singleton initialisation: `if obj is None: obj = Expensive()` — race.
- Memoising decorators not designed for threads.
- Cached property with lazy compute.
- Module-level mutable state read by multiple threads.

Fixes: locks, `functools.cache` (thread-safe in CPython 3.9+), `threading.local`.

## 3. Key works / libraries

- **PEP 703** — Making the Global Interpreter Lock Optional. Adopted; experimental in 3.13.
- **PEP 734** — Subinterpreters.
- **CPython source** — `Python/ceval.c` for GIL implementation.
- **`threading`** stdlib documentation — docs.python.org/3/library/threading.html.
- **`queue`** stdlib — docs.python.org/3/library/queue.html.
- **`concurrent.futures`** — docs.python.org/3/library/concurrent.futures.html.
- **Beazley, D.** various PyCon talks on Python concurrency.
- **"Python Concurrency from the Ground Up"** PyCon US 2015 (Beazley).

## 4. Pitfalls and gotchas

- **Assuming GIL = thread-safety.** It's not.
- **Lock ordering deadlock.** Two locks acquired in different orders by two threads. Lock-ordering protocol or `threading.RLock`.
- **Forgetting to release the lock on exception.** `with lock:` handles this; manual `acquire/release` invites bugs.
- **`threading.Lock` is not asyncio-safe.** Holding a threading.Lock across an `await` is wrong. Use `asyncio.Lock` in async code.
- **C-extension that doesn't release GIL.** Pure-Python work in another thread can't proceed during a long pure-Python call (rare these days but possible).
- **C-extension that *does* release GIL.** When it does, race conditions on Python objects are possible if the C extension exposes Python state.
- **`logging` module.** Stdlib logging is thread-safe by design. Don't reinvent.
- **`time.time()` vs `time.monotonic()`.** monotonic is thread-safe and not affected by system clock changes. Prefer for timeouts.
- **Daemon threads exit abruptly.** Won't complete cleanup. Use `Thread(..., daemon=False)` and explicit join for important work.

## 5. Applicability to Runa

For **Smiðja worker pools**:

- Each worker process is single-threaded (Python doesn't share state across processes).
- Inside a worker, if it spawns threads for I/O, threading primitives apply.

For **asyncio + thread bridge in the kernel**:

- `asyncio.to_thread` for short blocking I/O.
- `loop.run_in_executor(POOL, ...)` for CPU-bound work in ProcessPoolExecutor.
- No shared mutable state between asyncio side and thread side; communication via futures.

For **third-party libraries**:

- Many libraries call callbacks on threads (e.g., websocket libraries firing callbacks on a separate thread). Use `asyncio.run_coroutine_threadsafe` to re-enter the asyncio loop.

For **shared state**:

- Configuration loaded once at startup; immutable dataclasses. Safe to share.
- Mutable state lives in single-owner subsystems (Muninn writer, Skuld writer, etc.). Cross-subsystem comms via VERÐANDI events.

For **logging**:

- stdlib `logging` is thread-safe; use it directly. structlog also thread-safe.

For **future free-threaded Python**:

- Watch PEP 703 maturation. Some Runa patterns may benefit (true parallel CPU work without ProcessPool overhead). Others (Smiðja pool isolation) remain valuable.

What to avoid:

- Don't share mutable dicts/lists across threads without locks.
- Don't hold threading.Lock across `await`.
- Don't assume CPython behaviour holds in PyPy or future free-threaded Python.
- Don't use daemon threads for work that must complete.

## 6. Open questions

- **Free-threaded Python adoption.** When 3.13+ becomes mainstream, Python concurrency shifts dramatically. Most existing thread-safe code remains correct (CPython is more strict than necessary); some assumes single-threaded execution semantics that won't hold.
- **Subinterpreters and shared state.** PEP 734's per-interpreter GIL gives parallelism with less isolation cost than multiprocessing. Sharing state remains explicit.
- **Thread-safety in async libraries.** Some async libraries internally use threads. Boundary conventions vary.

## 7. References (curated)

- docs.python.org/3/library/threading.html — official.
- PEP 703, PEP 734.
- realpython.com/python-gil/ — practical GIL intro.
- python.org/dev/peps/ — formal references.
- Beazley's PyCon concurrency talks (search YouTube).
- Companion docs: [[19-asyncio-advanced]], [[24-multiprocessing-deep-dive]].

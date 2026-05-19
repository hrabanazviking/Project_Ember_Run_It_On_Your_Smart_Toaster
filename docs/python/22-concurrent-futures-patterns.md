# 22 — concurrent.futures Patterns: Pools, Futures, Executors

**Category:** Concurrency Mastery
**Runa relevance:** Smiðja (pool wrappers), Heimskringla (concurrent provider probing), background jobs
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

`concurrent.futures` is the standard-library high-level API for running things concurrently — in threads (ThreadPoolExecutor) or in processes (ProcessPoolExecutor) — with a unified Future-based interface. It's a thin layer over `threading`/`multiprocessing` that gets the ergonomics right: submit work, get a future, await result, handle errors, shut down cleanly.

For Runa, `concurrent.futures` is the right abstraction whenever you need "do N things in parallel and collect results." Inside asyncio code, it interoperates via `loop.run_in_executor`. Outside asyncio, it stands alone. Knowing the small set of useful patterns covers most real needs.

## 2. Technique / mechanism

**The basics:**

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

# Thread pool — for blocking I/O
with ThreadPoolExecutor(max_workers=10) as pool:
    futures = [pool.submit(fetch, url) for url in urls]
    for future in as_completed(futures):
        try:
            result = future.result(timeout=30)
            print(result)
        except Exception as exc:
            print(f"failed: {exc}")
```

**Pool vs single-future:**

```python
# Simple
future = pool.submit(work, arg)
result = future.result()  # blocks
result = future.result(timeout=5)  # blocks up to 5s

# Many
futures = [pool.submit(work, x) for x in items]
results = [f.result() for f in futures]  # waits in submission order

# Many, as they complete
for future in as_completed(futures):
    result = future.result()  # in finish-order

# Map (results in submission order)
results = list(pool.map(work, items, timeout=30))
```

**`as_completed` is the right pattern for parallel-with-staged-processing:**

```python
def probe_all_providers(providers, query):
    """Probe many providers; use first responder."""
    with ThreadPoolExecutor(max_workers=len(providers)) as pool:
        futures = {pool.submit(p.probe, query): p for p in providers}
        for future in as_completed(futures, timeout=10):
            provider = futures[future]
            try:
                result = future.result()
                # Cancel remaining
                for f in futures:
                    f.cancel()
                return provider, result
            except Exception as exc:
                logger.warning("%s probe failed: %s", provider.name, exc)
    raise NoProviderAvailableError()
```

**`wait`:**

```python
from concurrent.futures import wait, FIRST_COMPLETED, FIRST_EXCEPTION, ALL_COMPLETED

done, not_done = wait(futures, return_when=FIRST_COMPLETED)
# Useful when you want explicit handling of completion order
```

**Executor lifecycle:**

```python
# Context manager — cleanly shuts down
with ProcessPoolExecutor(max_workers=4) as pool:
    ...
# Pool is shut down here; workers terminated

# Manual lifecycle (for long-lived pools)
pool = ProcessPoolExecutor(max_workers=4)
try:
    ...
finally:
    pool.shutdown(wait=True, cancel_futures=False)
```

`cancel_futures=True` (3.9+) cancels not-yet-started work. Already-running tasks complete.

**Bridging to asyncio:**

```python
# In asyncio code
loop = asyncio.get_running_loop()
result = await loop.run_in_executor(POOL, blocking_fn, arg)

# Convenience shortcut for blocking I/O (uses default thread executor)
result = await asyncio.to_thread(blocking_fn, arg)

# Multiple
async def parallel_io(items):
    loop = asyncio.get_running_loop()
    return await asyncio.gather(*[
        loop.run_in_executor(POOL, work, item)
        for item in items
    ])
```

**Exception handling:**

```python
future = pool.submit(might_fail)
try:
    result = future.result()
except SomeError as exc:
    # The exception is re-raised from the worker
    ...
```

The Future captures exceptions and re-raises on `.result()`. Tracebacks are preserved (mostly — process-pool tracebacks lose some detail).

**Cancellation:**

```python
future.cancel()  # only works for not-yet-started work
```

Once running, work cannot be cancelled cleanly through Future. For long-running workers, see [[23-async-cancellation]].

**Patterns to avoid:**

```python
# WRONG — blocking inside asyncio code
results = [pool.submit(work, x).result() for x in items]  # blocks the loop

# RIGHT — use run_in_executor / asyncio.gather
results = await asyncio.gather(*[
    loop.run_in_executor(POOL, work, x) for x in items
])
```

## 3. Key works / libraries

- **`concurrent.futures` stdlib** — docs.python.org/3/library/concurrent.futures.html.
- **PEP 3148** — the original concurrent.futures spec.
- **`asyncio.run_in_executor` / `asyncio.to_thread`** — the asyncio bridge.
- **`loky`** — github.com/joblib/loky. Hardened ProcessPoolExecutor.
- **`pebble`** — github.com/noxdafox/pebble. Adds task timeouts to process pools.
- **Beazley's `Generators and Concurrent Programming` PyCon talks.**

## 4. Pitfalls and gotchas

- **No task-level timeout in ProcessPoolExecutor**. `future.result(timeout=...)` returns control but doesn't kill the worker. Use `pebble` if you need per-task timeouts that actually terminate.
- **Future.cancel() doesn't kill running work**. Only prevents not-yet-started work from starting.
- **Shutdown blocks by default**. `shutdown(wait=True)` waits for all submitted work. `wait=False` doesn't kill workers — they continue until done.
- **as_completed timeout** measures from when `as_completed` started, not per-future. A long total wait can mean some futures had no individual wait at all.
- **Spawn vs fork as discussed in [[21-multiprocessing-deep-dive]].** `ProcessPoolExecutor` defaults to system default; explicit `mp_context=...` is safer.
- **Pool exhaustion deadlock**. If pool size is 10 and you submit 10 tasks each waiting on a future of another submitted task, deadlock. Don't recursively submit to the same pool unless you understand the math.
- **Submitting too many tasks**. submit() returns immediately; the pool queues internally. Memory grows. Bound submission rate.

## 5. Applicability to Runa

For **Smiðja**:

- One ThreadPoolExecutor for blocking I/O (e.g., synchronous file readers, blocking C libraries).
- One ProcessPoolExecutor for CPU-bound work ([[21-multiprocessing-deep-dive]]).
- Per-pool sizing in config; defaults per Pi 5 hardware.

For **Heimskringla probing**:

- Concurrent probe of multiple providers using `as_completed`. First responder wins; others cancelled.
- Used in startup health checks and adaptive routing.

For **batch processing**:

- Eir's nightly batch (re-embedding, vacuuming) uses `pool.map` for embarrassingly-parallel chunks.

For **kernel turn parallel work**:

- Inside asyncio, prefer `asyncio.gather` and TaskGroup. `concurrent.futures` enters via `run_in_executor` for sync work only.

What to avoid:

- Don't block the asyncio loop with `.result()`. Always go through `run_in_executor`.
- Don't recursively submit to a pool with size N without understanding deadlock risk.
- Don't trust `future.cancel()` to stop running work.

## 6. Open questions

- **Per-task timeouts** at the Executor level. `pebble` adds this; stdlib doesn't. Worth using if you need it.
- **Free-threaded Python** changes the calculus — ThreadPoolExecutor becomes competitive with ProcessPool for CPU work.
- **Pool sizing in dynamic loads**. Static sizing in config vs adaptive. Trade-offs.

## 7. References (curated)

- docs.python.org/3/library/concurrent.futures.html — stdlib.
- PEP 3148 — original spec.
- github.com/joblib/loky — hardened pool.
- github.com/noxdafox/pebble — pool with per-task timeout.
- Companion docs: [[19-asyncio-advanced]], [[20-thread-safety-python]], [[21-multiprocessing-deep-dive]], [[24-queue-channel-patterns]].

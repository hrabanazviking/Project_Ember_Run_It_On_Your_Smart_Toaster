# 23 — Async Cancellation and Shielded Operations

**Category:** Concurrency Mastery
**Runa relevance:** every kernel turn (graceful cancel), supervisor restart, timeout enforcement
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Cancellation in asyncio is *cooperative*. When a task is cancelled, a `CancelledError` is raised at its next `await`. The task's job is to: clean up briefly, then re-raise. This contract is how supervisors ([[12-supervisor-trees]]), timeouts ([[09-timeout-patterns]]), and TaskGroup ([[19-asyncio-advanced]]) all work — they ultimately rely on tasks honouring cancellation cleanly.

The subtle case is *critical sections* where cancellation would corrupt state — a half-done database write, a partially-sent network message. For those, `asyncio.shield` provides explicit protection. The combination of "default cancellable; shielded where critical" is the discipline that makes asyncio code robust under cancellation.

## 2. Technique / mechanism

**The basic contract:**

```python
async def well_behaved_task():
    try:
        while True:
            await do_unit_of_work()
    except asyncio.CancelledError:
        await cleanup_briefly()
        raise  # ALWAYS re-raise
```

Catching `CancelledError` without re-raising silently breaks cancellation. Don't.

**Cancellation triggers:**

- `task.cancel()` — explicit.
- `asyncio.timeout()` expiration — implicit via cancel.
- `TaskGroup` sibling failure → cancellation of others.
- Loop shutdown.

**`asyncio.shield` — protect critical work:**

```python
async def commit_to_disk(data):
    await asyncio.shield(write_atomic(data))
```

If the outer task is cancelled while `write_atomic` runs, the cancellation is *held back*; `write_atomic` completes; cancellation takes effect after.

The semantics: `shield(inner)` is itself cancellable from outside *as a wrapper*, but the inner task continues until completion.

```python
async def example():
    inner = asyncio.create_task(slow_critical())
    try:
        return await asyncio.shield(inner)
    except asyncio.CancelledError:
        # The shield was cancelled; the inner task is still running
        # Decide: wait for it, or abandon it
        result = await inner  # wait for completion
        return result
```

**`shield` is not magic; it requires care.** If used carelessly, the inner task leaks (continues running after the caller has moved on).

**Cancellation in TaskGroup:**

```python
async with asyncio.TaskGroup() as tg:
    tg.create_task(a())
    tg.create_task(b())
    tg.create_task(c())
# If a() raises, b and c are cancelled. The TaskGroup awaits cancellation cleanup.
# The ExceptionGroup contains the original exception.
```

**Cancellation in HTTP / network:**

httpx properly propagates cancellation:

```python
async with httpx.AsyncClient() as client:
    response = await client.get(url)  # if cancelled, the connection is closed
```

Some older or sync-wrapped libraries don't cancel cleanly — the request continues on a thread. Worth knowing per library.

**Cancellation in file I/O:**

Standard file operations are blocking; `asyncio.to_thread` wraps them. Cancellation cancels the *wrapper*, not the underlying I/O — the thread continues to completion.

```python
result = await asyncio.to_thread(big_read, path)
# If outer task is cancelled, the thread continues until big_read returns;
# the result is just dropped
```

For genuine cancellation of disk I/O, you'd need OS-level mechanisms (rarely worth it).

**Detecting current cancellation state:**

```python
task = asyncio.current_task()
if task.cancelling():
    # Cancellation has been requested
    ...
```

`task.cancelling()` (3.11+) returns the count of pending cancellation requests.

**Multiple cancellation requests:**

A task can be cancelled multiple times. Each call to `task.cancel()` schedules another `CancelledError`. `task.uncancel()` decrements; useful when you want to "absorb" one cancel and continue.

**Cancellation in long-running loops:**

```python
async def long_loop():
    while True:
        try:
            await do_work()
        except asyncio.CancelledError:
            # Per-iteration handling
            await finish_current_unit()
            raise  # propagate up; loop exits
```

If you have natural checkpoints inside a long operation, you can choose where cancellation is honored vs delayed.

**Pitfall: forgetting to await cancellation:**

```python
# WRONG
task.cancel()
# returns immediately; the task is "cancelling" but hasn't finished

# RIGHT
task.cancel()
try:
    await task  # wait for cancellation to complete
except asyncio.CancelledError:
    pass
```

After `cancel()`, await the task to ensure cleanup completes. TaskGroup does this for you.

**asyncio.wait_for vs asyncio.timeout for cancellation:**

```python
# Modern (3.11+):
async with asyncio.timeout(5.0):
    await operation()

# Older equivalent:
await asyncio.wait_for(operation(), timeout=5.0)
```

Both cancel the inner operation on timeout. `timeout` composes better with TaskGroup.

## 3. Key works / libraries

- **PEP 3156** — original asyncio spec.
- **`asyncio` documentation, cancellation section** — docs.python.org/3/library/asyncio-task.html#task-cancellation.
- **PEP 654, 678** — exception groups + notes.
- **Trio's cancellation design** — trio.readthedocs.io; cleaner model that influenced asyncio.
- **Smith's structured-concurrency essay** — vorpus.org.

## 4. Pitfalls and gotchas

- **Catching CancelledError without re-raising.** Breaks cancellation; supervisors can't stop the task.
- **Catching `Exception` accidentally catches `CancelledError` in 3.7 only.** In 3.8+, `CancelledError` is `BaseException` and not caught by `except Exception`. Be aware of Python version.
- **`shield` leaking the inner task.** If outer is cancelled and you don't await the inner, it runs orphaned. Always have a plan for the inner.
- **Cancellation during sleep.** `asyncio.sleep(60)` cancels cleanly. `time.sleep(60)` blocks the loop and cancellation can't propagate.
- **Cancellation during `to_thread`.** The Future returned by `to_thread` is cancellable; the thread itself isn't.
- **Cancellation during finally.** `finally` blocks run even on cancellation, but if they `await` and themselves are slow, they delay cancellation. Keep finally cleanup fast.
- **Race conditions on cancellation.** If you cancel right as a task is finishing, you might cancel after it's already returned. Test that paths.
- **Cancelling a TaskGroup**: cancels all members. If one member is shielded, the others cancel; the shielded one continues; the TaskGroup waits.

## 5. Applicability to Runa

For **kernel turns**:

- Each turn is cancellable. If a turn exceeds its deadline, the supervisor cancels.
- The turn's cleanup: emit audit-log entry "cancelled"; release any open resources; re-raise.

For **adapters**:

- Each adapter coroutine cancels cleanly: close connection, log disconnect, re-raise.
- A supervisor-driven restart depends on this.

For **Heimskringla provider calls**:

- Wrapping the actual HTTP call in shield is *almost never right* — provider calls can be retried, so cancelling mid-call is fine.
- But: writes to local cache *after* a successful provider call should shield the cache write so it completes.

For **Muninn writes**:

- The atomic file-write inside `write_atomic` should be shielded if invoked from a cancellable context. The temp-file write + rename should not be torn apart by cancellation.

For **Skuld task transitions**:

- State transitions are local SQLite operations; usually fast enough to not need shielding. If they grow longer (a batch update), shield the transaction.

For **Eir reconciliation actions**:

- Some repair actions are safe to cancel mid-way (will be re-tried next cycle). Others (e.g., restoring from backup) should shield until done.

What to avoid:

- Don't catch CancelledError without re-raising.
- Don't use shield to make code "uncancellable" — it's for *brief* critical sections.
- Don't perform long work inside `finally`. Cancellation gets delayed.
- Don't forget to `await task` after `task.cancel()`.

## 6. Open questions

- **Cancellation observability.** How to surface "this task was cancelled vs failed vs completed" in logs cleanly. Mostly stdlib doesn't help.
- **Sub-task cancellation policy.** When a TaskGroup cancels children, the order of cancellation isn't deterministic. Sometimes matters.
- **Cooperative cancellation in CPU loops.** A CPU-bound async function (rare) doesn't naturally hit await points. Need explicit `await asyncio.sleep(0)` checkpoints.

## 7. References (curated)

- docs.python.org/3/library/asyncio-task.html#task-cancellation.
- vorpus.org/blog/notes-on-structured-concurrency-or-go-statement-considered-harmful/ — Smith.
- trio.readthedocs.io/en/stable/reference-core.html#cancellation-and-timeouts.
- PEP 654.
- Companion docs: [[09-timeout-patterns]], [[12-supervisor-trees]], [[19-asyncio-advanced]].

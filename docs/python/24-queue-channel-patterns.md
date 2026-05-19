# 24 — Queue and Channel Patterns

**Category:** Concurrency Mastery
**Runa relevance:** VERÐANDI bus, adapter outbound queues, Smiðja worker pool, Skuld task queue
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Queues and channels are the most-used coordination primitive in concurrent systems. They decouple producers from consumers, smooth bursts of demand, provide explicit backpressure, and serve as the inter-task communication substrate that *avoids* shared mutable state. Python offers several queue types — one for each concurrency model — and the right choice matters: mixing them is a source of subtle bugs.

For Runa, queues are everywhere. VERÐANDI's pub/sub fan-out uses asyncio queues. Adapter outbound buffers are bounded queues. Skuld's task ledger is conceptually a durable queue. The worker pool ([[21-multiprocessing-deep-dive]]) uses `multiprocessing.Queue` for IPC. Understanding the differences and the patterns saves debugging.

## 2. Technique / mechanism

**The four queue types in Python:**

| Queue | Module | Concurrency model | Cross-process |
|---|---|---|---|
| `queue.Queue` | stdlib | threads | No |
| `asyncio.Queue` | stdlib | asyncio (coroutines) | No |
| `multiprocessing.Queue` | stdlib | processes | Yes |
| `multiprocessing.JoinableQueue` | stdlib | processes | Yes |

**Bounded queues = backpressure:**

```python
queue = asyncio.Queue(maxsize=1000)

async def producer():
    while True:
        item = await produce()
        await queue.put(item)  # blocks when full — backpressure

async def consumer():
    while True:
        item = await queue.get()
        await process(item)
        queue.task_done()
```

When the queue is full, `put()` waits. The producer is naturally slowed to consumer pace. Unbounded queues invite memory exhaustion.

**Drop-on-full alternative:**

```python
try:
    queue.put_nowait(item)
except asyncio.QueueFull:
    logger.warning("dropping; queue full")
```

Backpressure (block) vs drop is a design choice per use case.

**Multiple consumers (work stealing):**

```python
queue = asyncio.Queue()

async def worker(worker_id):
    while True:
        item = await queue.get()
        try:
            await process(item)
        finally:
            queue.task_done()

async def main():
    workers = [asyncio.create_task(worker(i)) for i in range(5)]
    # Produce
    for item in items:
        await queue.put(item)
    # Wait for all queued items to be processed
    await queue.join()
    # Cancel workers
    for w in workers:
        w.cancel()
```

`queue.join()` blocks until `task_done()` has been called for every item put on the queue.

**Pub/sub via fan-out queues:**

```python
class Bus:
    """Each subscriber has its own queue. Publish copies to all."""
    
    def __init__(self):
        self._subscribers: list[asyncio.Queue] = []
    
    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue(maxsize=1000)
        self._subscribers.append(q)
        return q
    
    async def publish(self, event):
        for q in self._subscribers:
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                logger.warning("subscriber queue full; dropping")
```

This is the simplest VERÐANDI implementation.

**Priority queues:**

```python
import asyncio
q = asyncio.PriorityQueue()

await q.put((1, "high-priority-item"))
await q.put((10, "low-priority-item"))

priority, item = await q.get()
```

Items are tuples; first element is priority (lower = first). Useful for kernel-turn scheduling where urgent inputs beat background work.

**LIFO (stack) queues:**

```python
q = asyncio.LifoQueue()
```

Rare; useful for depth-first traversal patterns.

**Cross-process queues:**

```python
import multiprocessing as mp

q: mp.Queue = mp.Queue(maxsize=100)

# In one process:
q.put(item)  # pickles and sends

# In another:
item = q.get(timeout=10)
```

`multiprocessing.Queue` is much heavier (pickle + IPC) than asyncio.Queue. Use only across process boundaries.

**JoinableQueue (multiprocessing):**

Adds `task_done()` / `join()` semantics like asyncio.Queue.

**Backpressure-aware streaming with async generators:**

```python
async def chunked_stream(source):
    """Yield items from source; backpressure via async generator."""
    async for item in source:
        yield process(item)

async def consume():
    async for processed in chunked_stream(source):
        await handle(processed)  # consumer's pace propagates backwards
```

Async generators provide natural backpressure: the producer yields only when the consumer is ready.

**Channels (third-party):**

Some libraries (anyio, trio) provide `MemoryObjectStream` / similar — channels with send / receive halves, often more explicit about closure semantics. Useful when communication has a clear start and end.

```python
import anyio

async def main():
    send, receive = anyio.create_memory_object_stream(max_buffer_size=10)
    
    async with anyio.create_task_group() as tg:
        tg.start_soon(producer, send)
        tg.start_soon(consumer, receive)

async def producer(send):
    async with send:
        for i in range(10):
            await send.send(i)

async def consumer(receive):
    async with receive:
        async for item in receive:
            print(item)
```

## 3. Key works / libraries

- **`queue` stdlib** — docs.python.org/3/library/queue.html.
- **`asyncio.Queue`** — docs.python.org/3/library/asyncio-queue.html.
- **`multiprocessing.Queue`** — multiprocessing docs.
- **`anyio` streams** — anyio.readthedocs.io.
- **Hoare's CSP** — channels as the foundational concurrency model.
- **Go's channel design** — influential modern reference.
- **Beazley's PyCon talks on concurrency.**

## 4. Pitfalls and gotchas

- **Mixing queue types.** `asyncio.Queue` from synchronous code → blocking forever. `queue.Queue` from asyncio → blocks the loop.
- **Unbounded queues.** Memory exhaustion under producer-faster-than-consumer load.
- **Forgetting `task_done()` with `queue.join()`.** `join()` waits forever.
- **`queue.join()` in asyncio code** — blocks the loop. Use `await q.join()`.
- **Pickling overhead** with multiprocessing.Queue. Large objects = expensive.
- **`get(timeout=...)` in multiprocessing.Queue** uses *seconds*; in asyncio.Queue use `asyncio.wait_for`.
- **Closing channels.** asyncio.Queue doesn't have a "close" concept; conventions use sentinels (put None to signal end).
- **Single-consumer assumption.** Some patterns silently break with multiple consumers.

## 5. Applicability to Runa

For **VERÐANDI bus**:

- Per-subscriber `asyncio.Queue(maxsize=1000)`.
- Drop on full (with logging) for low-priority events; block on full for critical events. Per-event-type policy.

For **adapter outbound buffers**:

- Per-adapter `asyncio.Queue(maxsize=500)`. Backpressure if the adapter is slow.

For **Skuld task queue**:

- Conceptually a priority queue, backed by SQLite (not in-memory). Workers pull next task ordered by priority + deadline.

For **kernel turn pipeline**:

- Per-turn TaskGroup uses internal queues for streaming intermediate results between Hirð retainers when they're chained.

For **Smiðja worker pool** (multiprocessing):

- `multiprocessing.Queue` for IPC between asyncio kernel and worker processes — but typically `ProcessPoolExecutor` handles this internally via futures.

What to avoid:

- Don't use unbounded queues anywhere.
- Don't mix queue types.
- Don't forget closure / sentinel conventions for multi-consumer setups.
- Don't put large objects through multiprocessing.Queue if you can pass handles instead.

## 6. Open questions

- **Persistent queues.** For Skuld-style durability, the in-memory queue patterns don't apply. SQLite-backed or RabbitMQ-style needed.
- **Priority + bounded + multi-consumer.** Combining these without surprises requires care.
- **Free-threaded Python** may shift some patterns — `queue.Queue` becomes more attractive when true threading parallelism is available.

## 7. References (curated)

- docs.python.org/3/library/queue.html.
- docs.python.org/3/library/asyncio-queue.html.
- anyio.readthedocs.io/en/stable/streams.html.
- Hoare, *Communicating Sequential Processes*, 1985.
- Companion docs: [[19-asyncio-advanced]], [[20-thread-safety-python]], [[21-multiprocessing-deep-dive]], [[22-concurrent-futures-patterns]].

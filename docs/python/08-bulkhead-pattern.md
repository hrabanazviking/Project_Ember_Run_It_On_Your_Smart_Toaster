# 08 — Bulkhead Pattern and Failure Isolation

**Category:** Robustness Fundamentals
**Runa relevance:** Hirð (per-retainer resource pools), Heimskringla (per-provider connection pools), adapters (per-adapter executors)
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

The **bulkhead pattern** takes its name from shipbuilding: a ship's hull is divided into watertight compartments by bulkheads, so a leak in one compartment doesn't sink the ship. In software, bulkheads are *resource compartments*: connection pools, thread pools, queues, processes, semaphores — anything that gives one subsystem a bounded slice of the total resources, so that one subsystem's misbehaviour can't starve the others.

For Runa, failure isolation is structural — DOMAIN_MAP and ARCHITECTURE both promise that any single adapter, retainer, or service can fail without taking down the agent. The bulkhead pattern is *how* that promise is kept in practice: bounded resource pools per subsystem ensure that a runaway Heimdallr doesn't eat all the kernel's compute, a slow Discord adapter doesn't block the gateway from talking to Telegram, a misbehaving plugin can't exhaust the connection pool used for everything else.

## 2. Technique / mechanism

**The pattern in code:**

The simplest bulkhead is a `Semaphore`:

```python
import asyncio

class ProviderBulkhead:
    def __init__(self, max_concurrent: int):
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def call(self, fn):
        async with self._semaphore:
            return await fn()
```

If `max_concurrent` is 10, at most 10 calls run concurrently. The 11th waits until one finishes. This bounds resource use per subsystem.

**Per-provider bulkheads:**

```python
class Heimskringla:
    def __init__(self):
        self._bulkheads = {
            "anthropic": asyncio.Semaphore(10),  # max 10 concurrent Anthropic calls
            "openai": asyncio.Semaphore(10),
            "openrouter": asyncio.Semaphore(20),  # aggregator handles more
            "ollama": asyncio.Semaphore(2),       # local model = limited compute
            "lm_studio": asyncio.Semaphore(2),
        }
    
    async def call(self, provider: str, request: Request) -> Response:
        async with self._bulkheads[provider]:
            return await self._providers[provider].complete(request)
```

A traffic spike on `openrouter` doesn't reduce capacity for `anthropic`. Each provider has its own slot.

**Thread pool bulkheads (for blocking work):**

```python
from concurrent.futures import ThreadPoolExecutor

class SmidjaPools:
    def __init__(self):
        self.io_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="smidja-io")
        self.cpu_pool = ProcessPoolExecutor(max_workers=3)  # see [[24-multiprocessing]]
        self.dns_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="dns")
```

Different work types have different pools. DNS lookups don't compete with file I/O.

**Connection-pool bulkheads:**

```python
# httpx clients are themselves connection-pooled
clients = {
    "anthropic": httpx.AsyncClient(
        base_url="https://api.anthropic.com",
        timeout=30.0,
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
    ),
    "openai": httpx.AsyncClient(
        base_url="https://api.openai.com",
        timeout=30.0,
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
    ),
}
```

The HTTP connection limits per client are themselves bulkheads.

**Queue bulkheads:**

```python
class AdapterMessageQueue:
    """Each adapter has its own bounded outbound queue."""
    def __init__(self, max_size: int = 1000):
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_size)
    
    async def send(self, message):
        try:
            self.queue.put_nowait(message)
        except asyncio.QueueFull:
            raise AdapterBackpressureError("Discord queue full")
```

A slow consumer accumulates a backlog; once the queue is full, new sends fail fast rather than queuing unbounded.

**Process-level bulkheads:**

Services running in separate processes are the strongest bulkheads. One process crashing doesn't affect another. Runa's services architecture (gateway, worker, voice in separate processes per DOMAIN_MAP §6) is process-level bulkheading at the architecture level.

**Trade-offs in pool sizing:**

- Too small → contention; legitimate work queues up.
- Too large → no isolation; one subsystem hogs everything.
- Right size: roughly `max_concurrent ≈ p99_latency × peak_rps` per the Little's Law calculation, capped by available resources.

**Bulkhead + breaker + retry together:**

These three patterns compose. A typical resilient call:

```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(0.5, 30))
async def call(req):
    async with provider_bulkhead.call() as slot:
        if breaker.is_open():
            raise CircuitOpenError("provider unavailable")
        try:
            return await provider.complete(req)
        except Exception:
            breaker.record_failure()
            raise
        else:
            breaker.record_success()
```

The bulkhead limits concurrency; the breaker fails fast on sustained failure; the retry handles transient failure.

## 3. Key works / libraries

- **Nygard, M.** *Release It!*, 2nd ed., 2018. Introduces bulkhead alongside circuit breaker.
- **Resilience4j** (Java) — `Bulkhead` as a first-class abstraction.
- **Hystrix** (Netflix, deprecated but influential) — bulkhead + circuit breaker integration reference.
- **`anyio`** — anyio.readthedocs.io. Cross-asyncio/trio. Has CapacityLimiter (bulkhead).
- **`asyncio.Semaphore` / `asyncio.BoundedSemaphore`** — stdlib primitives.
- **`httpx.Limits`** — connection pool limits.
- **AWS Builders' Library:** "Workload isolation using shuffle-sharding."

## 4. Pitfalls and gotchas

- **Shared semaphores across asyncio loops** don't work. Each loop has its own.
- **Forgetting to release the semaphore.** `async with` does this automatically; manual `acquire/release` invites bugs.
- **Bulkhead larger than backend capacity.** A bulkhead of 100 against a service that can serve 10 will queue 90 doomed requests. Match bulkhead to backend.
- **Bulkhead state across worker processes.** Each worker has its own semaphore. Total concurrency = `workers × bulkhead`. Plan accordingly.
- **Bounded queue + slow consumer = data loss.** If you raise on QueueFull, you drop requests. Sometimes right; sometimes catastrophic. Decide explicitly.
- **Bulkhead without observability.** Saturated bulkhead is silent failure. Emit metrics on queue depth, wait time, rejection rate.
- **CPU-bound work in I/O bulkheads.** A CPU-heavy task in a thread pool blocks one thread; other threads continue (GIL releases on I/O but not on CPU). Use ProcessPool for CPU.
- **Bulkhead on hot path.** Even Semaphore acquire is non-trivial. Profile if you bulkhead very-high-frequency operations.

## 5. Applicability to Runa

For **Heimskringla** (per ADR-0002 §D-2.1, asyncio + worker pool):

- Per-provider `asyncio.Semaphore` with per-provider sizing in config.
- Per-provider `httpx.Limits` for connection pooling.
- Shared multiprocessing worker pool for CPU-heavy tasks (one *bulkhead* serves all CPU work but bounds total CPU concurrency).

For **Hirð (retainers)**:

- Each retainer has its own task budget. Huginn researching doesn't starve Eir's repair work.
- Implemented as per-retainer `asyncio.Semaphore` or per-retainer scheduling priority.

For **adapters**:

- Per-adapter outbound queue (bounded).
- Per-adapter HTTP connection pool.
- A slow / blocking adapter doesn't accumulate unbounded backlog.

For **Smiðja tools**:

- `io_pool: ThreadPoolExecutor` for blocking I/O.
- `cpu_pool: ProcessPoolExecutor` for CPU-bound work.
- A long-running tool job doesn't eat the kernel's responsiveness.

For **MCP servers**:

- Per-MCP-server concurrent-call bulkhead. One slow MCP server doesn't choke others.

For **operator visibility**:

- Each bulkhead exposes `(in_flight, capacity, queue_depth, rejection_count)` via `runa doctor`.
- High utilisation or rejections trigger `Notified` to Volmarr.

For **default sizing on Pi 5 (16 GB)**:

- Per-cloud-provider: 10 concurrent calls (low real concurrency expected).
- Per-local-model (Ollama): 2 concurrent calls (single-user, GPU/CPU bound).
- Per-adapter: 5 outbound, 5 inbound.
- Smidja IO pool: 10 threads.
- Smidja CPU pool: 3 processes (one core reserved for kernel asyncio).

All numbers config-pinned; tune from observation.

What to avoid:

- Don't share a global bulkhead across unrelated subsystems. That's no bulkhead at all.
- Don't make bulkheads invisible. Operator must see saturation.
- Don't queue forever when a bulkhead is full. Backpressure (reject with clear error) is healthier than infinite queue.
- Don't oversize bulkheads to "not have to worry." Then you don't have isolation.

## 6. Open questions

- **Bulkhead sizing under variable load.** Adaptive resizing is appealing; complex to get right. Often static sizing + alarms suffices.
- **Shuffle sharding.** Advanced isolation that partitions clients across overlapping bulkheads to reduce blast radius. AWS-style; rare at single-Pi scale.
- **Bulkheads across processes.** Coordinating per-process bulkheads to enforce global concurrency limits requires shared state. Usually not needed for single-host.

## 7. References (curated)

- Nygard, *Release It!*, 2nd ed.
- resilience4j.readme.io/docs/bulkhead — Resilience4j bulkhead reference.
- anyio.readthedocs.io — anyio's CapacityLimiter.
- aws.amazon.com/builders-library/workload-isolation-using-shuffle-sharding/ — shuffle sharding.
- docs.python.org/3/library/asyncio-sync.html — asyncio sync primitives.
- Companion docs: [[06-retry-strategies]], [[07-circuit-breaker]], [[24-queue-channel-patterns]].

# 09 — Timeout Patterns and Deadline Propagation

**Category:** Robustness Fundamentals
**Runa relevance:** every external call, kernel turn budgets, Skuld task limits
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Every operation that depends on something external — a network call, a tool, a model, another process — can take *arbitrarily long*. Without timeouts, a single hung operation can wedge the calling code, the calling thread, eventually the whole process. Timeouts are the non-negotiable backstop that says "after T seconds, give up and report what happened."

Beyond simple per-call timeouts, mature systems use **deadline propagation**: when the kernel turn says "I have 30 seconds total to respond to this user," that deadline propagates through every downstream call. The retrieval might take 5 seconds; the model call might take 20; the result formatting might take 1; if anything goes long, the rest of the chain knows it has less budget than originally planned. This is how production systems avoid "we waited 60 seconds for the retrieval and then had no time for the model."

For Runa, timeouts are the discipline that keeps the agent *responsive*. DATA_FLOW.md §2.2 sets latency budgets: 300ms for non-LLM turns, 300ms acknowledged then several seconds for LLM turns. Those budgets only hold if every call enforces them.

## 2. Technique / mechanism

**Python timeout primitives:**

**`asyncio.timeout` (Python 3.11+) — the modern way:**

```python
import asyncio

async def fetch_with_timeout(url: str) -> str:
    async with asyncio.timeout(5.0):
        return await fetch(url)
```

If the block doesn't complete in 5 seconds, raises `TimeoutError`. Composes with `asyncio.TaskGroup`. The standard for new code.

**`asyncio.wait_for` (older API):**

```python
result = await asyncio.wait_for(fetch(url), timeout=5.0)
```

Equivalent semantics but the newer `timeout` context manager is preferred — better composition.

**`asyncio.timeout_at(deadline)` (absolute deadline):**

```python
async with asyncio.timeout_at(loop.time() + 5.0):
    ...
```

Useful when you have a deadline computed from elsewhere.

**HTTP-client timeouts:**

```python
import httpx

# Default timeout for all requests
client = httpx.AsyncClient(timeout=10.0)

# Or per-call
response = await client.get(url, timeout=5.0)

# Granular timeouts
client = httpx.AsyncClient(timeout=httpx.Timeout(
    connect=5.0,   # connection establishment
    read=30.0,     # waiting for response data
    write=10.0,    # sending request data
    pool=5.0,      # waiting for a connection from the pool
))
```

`httpx` distinguishes between connect / read / write / pool timeouts. Each can be independently set.

**Subprocess timeouts:**

```python
import subprocess

try:
    result = subprocess.run(
        ["./external_tool", "--arg"],
        capture_output=True,
        text=True,
        timeout=30.0,
    )
except subprocess.TimeoutExpired:
    # Process is killed; partial output available in exc.stdout
    ...
```

Or async:
```python
proc = await asyncio.create_subprocess_exec(...)
try:
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30.0)
except asyncio.TimeoutError:
    proc.kill()
    await proc.wait()
    raise
```

**Threading timeouts:**

```python
import threading
event = threading.Event()
got_it = event.wait(timeout=5.0)
if not got_it:
    raise TimeoutError(...)
```

For thread pools:
```python
from concurrent.futures import TimeoutError as FuturesTimeout, ThreadPoolExecutor

with ThreadPoolExecutor() as pool:
    future = pool.submit(blocking_work, args)
    try:
        result = future.result(timeout=10.0)
    except FuturesTimeout:
        # The work isn't actually cancelled — threads can't be killed
        # Future.cancel() only prevents un-started work from starting
        ...
```

**Deadline propagation pattern:**

```python
from dataclasses import dataclass
import time
from contextvars import ContextVar

@dataclass(frozen=True)
class Deadline:
    deadline_monotonic: float  # absolute time
    
    @classmethod
    def in_seconds(cls, seconds: float) -> "Deadline":
        return cls(deadline_monotonic=time.monotonic() + seconds)
    
    def remaining(self) -> float:
        return max(0.0, self.deadline_monotonic - time.monotonic())
    
    def expired(self) -> bool:
        return self.remaining() <= 0

current_deadline: ContextVar[Deadline | None] = ContextVar("deadline", default=None)

async def with_deadline(deadline: Deadline, fn):
    """Run fn with the given deadline, raising on timeout."""
    token = current_deadline.set(deadline)
    try:
        async with asyncio.timeout(deadline.remaining()):
            return await fn()
    finally:
        current_deadline.reset(token)

# Inside any downstream call:
async def fetch_something():
    deadline = current_deadline.get()
    if deadline and deadline.expired():
        raise DeadlineExpiredError()
    # Use min of remaining budget and reasonable timeout for this op
    op_timeout = min(deadline.remaining() if deadline else 30.0, 30.0)
    async with asyncio.timeout(op_timeout):
        return await actually_fetch()
```

`ContextVar` carries the deadline through async call chains without explicit parameter-passing. Each downstream operation queries the remaining budget.

**The hierarchy of timeouts:**

Most robust code has timeouts at multiple levels:
- Kernel turn budget (e.g., 30s)
- Per-skill budget (e.g., 10s)
- Per-tool-call budget (e.g., 5s)
- Per-network-op budget (e.g., 5s)
- Per-DNS-lookup budget (e.g., 1s)

These compose so that *something* always times out before resources are exhausted.

## 3. Key works / libraries

- **PEP 492 (async/await), PEP 654 (Exception Groups), PEP 678 (Exception Notes)** — asyncio timeout context evolution.
- **`asyncio.timeout`** added in Python 3.11.
- **`httpx`** — encode/httpx; the modern HTTP client with rich timeout semantics.
- **`requests`** — psf/requests; older sync client with `timeout=` parameter.
- **`anyio.fail_after`** — anyio's equivalent of asyncio.timeout, works across asyncio and trio.
- **gRPC deadline propagation** — Google's well-documented model; influential.
- **OpenTelemetry baggage** — propagating deadline as baggage across services.

## 4. Pitfalls and gotchas

- **Default timeouts in libraries are often "none" or "very long."** Always set explicitly.
- **`requests.get(url)` with no timeout** can hang forever. Always pass `timeout=`.
- **`asyncio.wait_for` cancels the inner task on timeout** but cancellation is cooperative — the task may not stop immediately if it's not awaiting.
- **Subprocess timeout** kills the process on timeout but the process's child processes may not die. Use `process group` semantics where needed.
- **Threading timeouts can't kill threads.** `future.cancel()` only prevents not-yet-started work from starting. A hung blocking-call thread can't be terminated cleanly.
- **Timeout that's shorter than network RTT** times out everything. Especially in test environments.
- **Timeout that masks bug.** If your function "normally takes 0.1s," a 30s timeout doesn't make a 25s call OK — it means something is wrong.
- **Deadlines that bleed across requests.** Per-process deadline state must be reset between requests, or you carry stale state.
- **DNS without timeout.** `socket.gethostbyname` can hang. Use `getaddrinfo` with timeout, or pre-resolve.
- **TCP keepalive doesn't substitute for timeout.** Keepalive detects dead connections at TCP level; application timeout detects app-level hangs.
- **OS-level timeout precision.** Most OSes can't time out finer than millisecond resolution; some coarser.

## 5. Applicability to Runa

For **kernel turn budget**:

- Every kernel turn enters with a deadline (computed from configured per-surface latency budget + safety margin).
- Deadline propagated via `ContextVar` to all downstream calls.
- Turn supervisor uses `asyncio.timeout()` enforced at the turn boundary.

For **Heimskringla provider calls**:

- Each call has both an *operation timeout* (specific to the call) and respects the *propagated deadline*.
- The effective timeout is `min(operation_timeout, deadline.remaining())`.
- Cloud providers respect their own server-side timeouts; client-side timeout is a safety net.

For **adapters**:

- HTTP client per adapter has explicit `httpx.Timeout(connect=5, read=30, write=10, pool=5)`.
- Long-poll connections (Discord gateway) have longer read timeouts but heartbeat-based liveness.

For **Smiðja tool calls**:

- Per-tool default timeout, overridable per call.
- Tools that are inherently long-running (deep research, long codegen) declare so and aren't subject to the standard turn timeout.

For **Skuld**:

- Tasks declare their own expected duration. A task exceeding 2× expected is flagged.
- Background tasks (Eir consolidation, indexing) have very generous timeouts; foreground (turn-bound) has tight ones.

For **MCP server calls**:

- Each MCP call has per-call timeout + global per-server bulkhead.
- An unresponsive MCP server doesn't block the kernel.

What to avoid:

- Don't ship without timeouts on any external call. Ever.
- Don't set timeouts longer than your user's patience.
- Don't write timeouts that "should be enough" without measurement.
- Don't ignore `TimeoutError`. Either handle it (retry, fallback, degrade) or re-raise.
- Don't conflate connect timeout with overall timeout. Different things.

## 6. Open questions

- **Per-tier vs per-call timeouts.** The right number of nested timeouts is a design choice. Too many = arithmetic complexity; too few = no granularity.
- **Adaptive timeouts.** Adjust per-call timeout based on observed latency distribution. Complex; rarely worth it for single-user agent.
- **Cancellation semantics across processes.** Killing a subprocess on timeout leaves orphaned resources sometimes. Cleanup matters.

## 7. References (curated)

- docs.python.org/3/library/asyncio-task.html#timeouts — official asyncio timeout docs.
- www.python-httpx.org/advanced/timeouts/ — httpx timeout docs.
- aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/ — Amazon Builders' Library.
- grpc.io/docs/guides/deadlines/ — gRPC deadline propagation reference.
- realpython.com/python-timeout/ — practical introduction.
- Companion docs: [[06-retry-strategies]], [[10-graceful-degradation]], [[23-async-cancellation]].

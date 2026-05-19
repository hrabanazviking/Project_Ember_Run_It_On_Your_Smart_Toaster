# 07 — Circuit Breaker Pattern in Python

**Category:** Robustness Fundamentals
**Runa relevance:** Heimskringla (per-provider breakers), adapters (per-adapter breakers), Eir (driven by breaker state)
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Retry recovers from *transient* failures ([[06-retry-strategies]]). The **circuit breaker** pattern handles *sustained* failures: when a downstream service is repeatedly failing, stop calling it for a while. The breaker "opens" after enough failures; in the open state, calls fail fast without even attempting; after a timeout, the breaker "half-opens" and lets a probe call through to test recovery; if the probe succeeds, the breaker "closes" and traffic resumes.

The pattern (popularised by Michael Nygard's *Release It!*, 2007) protects both sides of the call. Clients don't waste resources hammering a broken service; servers don't drown under retry storms that prevent recovery. For Runa, where every cloud provider call has cost and latency consequences, circuit breakers are how Heimskringla avoids "spend $50 in 5 minutes because Anthropic is having an outage."

## 2. Technique / mechanism

**The three states:**

```
        ┌─────────┐  failures ≥ threshold  ┌──────┐
        │ CLOSED  │ ──────────────────────►│ OPEN │
        │ (normal)│                        │      │
        └─────────┘                        └──┬───┘
              ▲                               │
              │ probe                         │ timeout elapsed
              │ succeeds                      │
              │                               ▼
              │                        ┌──────────┐
              │                        │HALF-OPEN │
              └────────────────────────│  (probe) │
                     probe fails       └──────────┘
                  → back to OPEN
```

- **CLOSED** — normal operation. Failure count tracked. When count reaches threshold within a window, transition to OPEN.
- **OPEN** — fail-fast. All calls raise `CircuitOpenError` immediately. After `reset_timeout`, transition to HALF-OPEN.
- **HALF-OPEN** — allow one (or a few) probe calls. If they succeed, transition to CLOSED. If they fail, back to OPEN.

**Reference implementation (minimal):**

```python
from __future__ import annotations
import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Awaitable, Callable, TypeVar

T = TypeVar("T")

class BreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitOpenError(Exception):
    """Raised when a call is attempted with the breaker in OPEN state."""

@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 5
    reset_timeout_seconds: float = 30.0
    half_open_probe_count: int = 1
    
    _state: BreakerState = BreakerState.CLOSED
    _failure_count: int = 0
    _opened_at: float = 0.0
    _half_open_in_flight: int = 0
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    
    async def call(self, fn: Callable[[], Awaitable[T]]) -> T:
        async with self._lock:
            if self._state == BreakerState.OPEN:
                if time.monotonic() - self._opened_at >= self.reset_timeout_seconds:
                    self._state = BreakerState.HALF_OPEN
                    self._half_open_in_flight = 0
                else:
                    raise CircuitOpenError(f"{self.name}: open until {self.reset_timeout_seconds - (time.monotonic() - self._opened_at):.1f}s")
            
            if self._state == BreakerState.HALF_OPEN:
                if self._half_open_in_flight >= self.half_open_probe_count:
                    raise CircuitOpenError(f"{self.name}: probe in flight, refusing")
                self._half_open_in_flight += 1
        
        try:
            result = await fn()
        except Exception:
            async with self._lock:
                self._on_failure()
            raise
        else:
            async with self._lock:
                self._on_success()
            return result
    
    def _on_failure(self) -> None:
        if self._state == BreakerState.HALF_OPEN:
            self._state = BreakerState.OPEN
            self._opened_at = time.monotonic()
            self._half_open_in_flight = 0
        else:  # CLOSED
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._state = BreakerState.OPEN
                self._opened_at = time.monotonic()
    
    def _on_success(self) -> None:
        if self._state == BreakerState.HALF_OPEN:
            self._state = BreakerState.CLOSED
            self._failure_count = 0
            self._half_open_in_flight = 0
        else:
            self._failure_count = 0  # reset on success in CLOSED
```

Usage:

```python
provider_breaker = CircuitBreaker(name="anthropic", failure_threshold=5, reset_timeout_seconds=30.0)

async def call_anthropic(req):
    return await provider_breaker.call(lambda: client.complete(req))
```

**Sliding-window vs simple counter:**

The simple counter ("5 consecutive failures") works but is brittle — alternating success/failure pattern never trips. **Sliding-window breakers** count failures within the last N seconds (or N requests), tripping when ratio exceeds threshold (e.g., 50% failure rate over the last 100 requests).

`pybreaker`, `purgatory`, and `aiobreaker` libraries implement variants.

**Important refinements:**

- **What counts as a "failure"?** Timeouts? 5xx? Specific exceptions? Configure per breaker.
- **Per-instance vs global state.** Many breakers in a process need shared state for the same external service. Centralise.
- **Per-host vs per-service.** If one server in a load-balanced pool fails, a per-service breaker over-trips. Per-host breakers more precise.
- **Bulkheads compose.** Circuit breakers per-resource limit blast radius ([[08-bulkhead-pattern]]).

**Combining with retry:**

```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential_jitter(0.5, 30))
async def call_provider_with_retry(req):
    try:
        return await provider_breaker.call(lambda: client.complete(req))
    except CircuitOpenError:
        raise  # don't retry breaker-open
```

The breaker prevents retry storms from hammering an open circuit. If the breaker rejects, retry doesn't help.

## 3. Key works / libraries

- **Nygard, M.** *Release It! Design and Deploy Production-Ready Software*. Pragmatic Bookshelf, 2007 (2nd ed. 2018). The book that named and popularised the pattern.
- **Hystrix** (Netflix, Java) — the influential reference implementation that drove industry adoption.
- **`pybreaker`** — github.com/danielfm/pybreaker. The most-used Python implementation. Sync only.
- **`aiobreaker`** — github.com/arlyon/aiobreaker. Async fork.
- **`purgatory`** — github.com/mardiros/purgatory. Modern async-native implementation with sliding-window support.
- **`stamina`** — github.com/hynek/stamina. Includes some breaker-like patterns.
- **AWS Builders' Library:** "Avoiding fallback in distributed systems."
- **Resilience4j** (Java) — modern reference design.

## 4. Pitfalls and gotchas

- **Per-process state.** Multi-process workers each have their own breaker. Coordinated state (Redis-backed) needed for true global view. Often per-process is acceptable.
- **Trip threshold too low.** A single transient blip trips the breaker. Frustrating UX.
- **Trip threshold too high.** Breaker doesn't trip until major damage done.
- **Reset timeout too short.** Breaker probes during outage, fails, opens again. Loop.
- **Reset timeout too long.** Genuine recovery isn't detected. Service stays effectively down.
- **HALF-OPEN probe storm.** If half-open allows many probes and the service is still down, you get a thunder. Use `half_open_probe_count=1` and lock.
- **Not distinguishing "service down" from "specific request bad".** A 400 should not trip the breaker; a 500 should. Configure `expected_exception`.
- **Breaker without metrics.** A silent breaker is useless. Emit metrics on state changes.
- **Breaker as the only failure response.** Fail-fast is right; *graceful degradation* ([[10-graceful-degradation]]) is what the user sees. Plan both.

## 5. Applicability to Runa

For **Heimskringla**:

- **Per-provider breaker.** Each provider (Anthropic, OpenAI, OpenRouter, Ollama, LM Studio) has its own breaker with provider-specific thresholds.
- **Failure definitions** per provider: timeout always failure; HTTP 5xx is failure; rate limit (429) is failure-but-Retry-After respected; 4xx other is *not* a breaker failure (it's a request bug).
- **Tripped breaker drives routing.** Heimskringla's routing logic ([[33-model-routing-ensembles]] in research corpus) checks breaker state; reroutes to alternate provider if available.
- **Operator visibility.** `runa doctor` reports breaker states. `Notified` event when a breaker trips.

For **adapters**:

- **Per-adapter breaker.** Discord failing doesn't affect Telegram.
- A tripped chat-adapter breaker degrades gracefully: queue outgoing messages in Skuld for delivery when breaker closes; tell user "Discord seems down, I'll deliver when it's back."

For **Eir**:

- Eir monitors breaker states. Repeated trips of the same breaker over time = escalation to operator.
- Eir attempts repair actions on tripped circuits (kick adapter, verify config, restart service).

For **Smiðja (tool calls)**:

- Per-tool breaker for tools that can fail systemically (e.g., a flaky external API tool).
- Internal pure-Python tools rarely need breakers.

For **MCP servers**:

- Per-MCP-server breaker. A failing MCP server doesn't affect others.

What to avoid:

- Don't trip a global breaker on per-request issues. The bug is in *this request*, not in the service.
- Don't ship without observability on breaker state. You'll never debug it.
- Don't combine retry-of-retry-of-retry with circuit breaker. One layer of retry per call site; let the breaker handle sustained failure.
- Don't set thresholds without measurement. Defaults are a starting point, not a final config.

## 6. Open questions

- **Distributed circuit breakers.** Sharing state across processes / hosts requires consensus. Redis-backed breakers exist; consistency / latency trade-offs.
- **Half-open probe selection.** Which call to use as the probe? A user-facing one (visible failure if probe fails) or a synthetic ping (silent but doesn't validate real load).
- **Adaptive thresholds.** Auto-tuning thresholds based on observed traffic. Promising; complex.

## 7. References (curated)

- Nygard, *Release It!*, 2nd ed. — the canonical text.
- martinfowler.com/bliki/CircuitBreaker.html — Fowler's concise summary.
- github.com/danielfm/pybreaker — pybreaker.
- github.com/mardiros/purgatory — purgatory (async, sliding window).
- aws.amazon.com/builders-library/ — multiple relevant articles.
- resilience4j.readme.io — Resilience4j (Java reference).
- Companion docs: [[06-retry-strategies]], [[08-bulkhead-pattern]], [[10-graceful-degradation]].

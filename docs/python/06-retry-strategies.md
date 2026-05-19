# 06 — Retry Strategies, Exponential Backoff, Jitter

**Category:** Robustness Fundamentals
**Runa relevance:** Heimskringla (provider call retries), adapters (chat/email/network), Eir (repair retries)
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Most external dependencies fail transiently — network blips, rate limits, momentary service overload, brief partitions. A simple retry recovers from these without involving humans. But naive retry — "if it fails, try again immediately, forever" — has destroyed many services: it amplifies load on already-struggling backends, creates thundering herds when many clients retry simultaneously, and exhausts resources on the retrying side.

The robust answer is **exponential backoff with jitter**: wait longer between successive retries, randomise the wait time so concurrent clients don't synchronise, give up after a cap, and only retry failures that *can* succeed on retry. Idempotency ([[05-idempotency-design]]) is the prerequisite that makes any of this safe.

## 2. Technique / mechanism

**The retry envelope:**

```
attempt 1 → fail → wait t₁ → 
attempt 2 → fail → wait t₂ → 
attempt 3 → fail → wait t₃ → 
attempt 4 → fail → give up
```

**Backoff strategies:**

- **Fixed:** t₁ = t₂ = t₃ = constant. Simple; can synchronise across clients (thundering herd).
- **Linear:** tₙ = n · base. Slightly better; still synchronises.
- **Exponential:** tₙ = base · 2ⁿ. Industry standard. With small base (~50-500ms) and cap (~30-60s).
- **Decorrelated / full jitter:** tₙ = random(0, base · 2ⁿ). Strong jitter; AWS Builders' Library recommends.
- **Equal jitter:** tₙ = base · 2ⁿ / 2 + random(0, base · 2ⁿ / 2). Compromise.

The **AWS "Exponential Backoff and Jitter" article** (Marc Brooker, 2015) demonstrated empirically that *full jitter* — `sleep = random(0, min(cap, base · 2ⁿ))` — outperforms other strategies on both client recovery time and server load.

**Reference implementation with `tenacity`:**

```python
from tenacity import (
    retry, stop_after_attempt, wait_exponential_jitter,
    retry_if_exception_type, before_sleep_log
)
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=1, max=30, jitter=2),
    retry=retry_if_exception_type((TimeoutError, ConnectionError, ProviderRateLimitError)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
async def call_provider(request: Request) -> Response:
    return await provider.complete(request)
```

What this does:
- Tries up to 5 times.
- Waits exponentially with jitter between tries.
- Only retries on specific exceptions (transient ones).
- Logs each retry.
- Re-raises the final exception if all attempts fail.

**Hand-rolled equivalent** (when avoiding the dependency):

```python
import asyncio
import random

async def with_retry(
    operation,
    *,
    max_attempts: int = 5,
    base_delay: float = 0.5,
    max_delay: float = 30.0,
    retryable: tuple[type[Exception], ...] = (TimeoutError, ConnectionError),
):
    last_exception = None
    for attempt in range(1, max_attempts + 1):
        try:
            return await operation()
        except retryable as e:
            last_exception = e
            if attempt == max_attempts:
                raise
            # Full jitter: random(0, min(cap, base * 2^(attempt-1)))
            sleep = random.uniform(0, min(max_delay, base_delay * (2 ** (attempt - 1))))
            await asyncio.sleep(sleep)
        # Non-retryable exceptions propagate immediately
```

**What to retry, what not to retry:**

| Failure | Retry? |
|---|---|
| `TimeoutError`, `ConnectionError` | Yes — likely transient |
| HTTP 5xx, 429, 408 | Yes — server overload or rate limit |
| HTTP 4xx (other) | No — client error; retry won't help |
| `ValueError`, `TypeError` from your own code | No — bug; surface immediately |
| `OSError` / `IOError` for "disk full" | No — environmental, retry won't fix |
| `OSError` for "temporarily unavailable" | Yes |
| Network DNS failures | Sometimes — short retry then propagate |
| Authentication errors (401, 403) | No — credentials problem |

The `retryable` predicate is the most important configuration knob.

**Server-side hints:**

- **`Retry-After`** HTTP header. Servers tell clients how long to wait. Honour it (cap at sane bound to avoid hostile servers).
- **Tokens-remaining headers.** Rate-limit headers indicate when to back off proactively.

**Distributed retries: the thundering herd problem.**

When a backend service recovers from outage, all clients retry simultaneously and overwhelm it again. Mitigations:
- **Jitter** (most important; full jitter is best).
- **Stagger startup of retry timers** across clients.
- **Server-side load shedding** (return 503 with Retry-After).
- **Circuit breaker** ([[07-circuit-breaker]]) on the client side to stop retrying when service is clearly down.

**Idempotency interaction:**

Retrying a non-idempotent operation can do harm. *Always* combine retry with idempotency ([[05-idempotency-design]]) — idempotency keys, natural-key dedup, or compare-and-set semantics.

**Async vs sync retries:**

Use `asyncio.sleep` (not `time.sleep`) in async code — otherwise you block the event loop. Tenacity's `AsyncRetrying` class handles this.

## 3. Key works / libraries

- **Brooker, M.** "Exponential Backoff and Jitter." AWS Architecture Blog, 2015. The definitive article.
- **Patterson, D.** *Patterns of Enterprise Application Architecture.* Has classical retry patterns.
- **`tenacity`** — github.com/jd/tenacity. The mature Python retry library.
- **`backoff`** — github.com/litl/backoff. Older alternative; well-maintained.
- **`stamina`** — github.com/hynek/stamina. Modern (2023+); thin wrapper over tenacity with better defaults.
- **AWS SDK retry strategies** — aws-sdk-python implements retry-with-jitter natively.
- **Google Cloud SDK retry library.**
- **`httpx` retries** — github.com/encode/httpx (built-in retry transport).

## 4. Pitfalls and gotchas

- **Synchronous retry in async code blocks the loop.** Always use `asyncio.sleep`.
- **Retrying without checking what failed.** Retry on `ValueError` and you mask bugs.
- **No upper bound on retries / wait time.** Some bug eats your budget for hours. Always cap.
- **Retry storms.** If 1000 clients retry every operation 5x with exponential backoff, your backend sees 5000 requests during outage recovery. Combine with circuit breaker.
- **Timeout-on-each-attempt vs total-deadline confusion.** A retry of 5 attempts at 30s each = 150s + sleep time. Decide which budget is the real budget.
- **Logging every retry at INFO** spams logs. WARN on retry, ERROR on final failure.
- **Retrying inside async-but-blocking operations.** Wrapping a blocking call in retry without `asyncio.to_thread` blocks the loop on each attempt.
- **Re-using the same `Retrying` object across coroutines.** Tenacity's `AsyncRetrying` is per-call.
- **Non-deterministic operations and idempotency-key reuse.** See [[05-idempotency-design]] pitfalls.

## 5. Applicability to Runa

For **Heimskringla provider calls**:

- Wrap every cloud-provider call with `tenacity`-style retry:
  - 3-5 attempts.
  - Full-jitter exponential backoff (base 0.5s, cap 30s).
  - Retryable: `ModelProviderError(retryable=True)`, `TimeoutError`, `httpx.HTTPError` for 5xx/429/408.
  - Non-retryable: authentication, 4xx (other), bad request.
- Honour `Retry-After` headers from providers.
- All provider calls carry an idempotency_key ([[05-idempotency-design]]).

For **adapters (chat platforms)**:

- Connection establishment uses retry with longer waits (5 attempts over 5 minutes).
- Individual message sends use shorter retry (2 attempts).
- Authentication errors propagate immediately without retry.

For **Eir (repair)**:

- Repair actions retry with care — some are safe to retry, others must be one-shot.
- Repair retries are logged conspicuously; sustained failure escalates to Volmarr via `Notified`.

For **Bifröst gateway**:

- Outbound webhooks (if Runa ever sends them) retry per webhook recipient.

For **Smiðja tool calls**:

- Tools that affect external state retry only if they explicitly declare `idempotent=True` in their schema.
- Tools that are pure functions (a calculation) retry freely on transient errors.

For **Skuld task resumption**:

- A task that crashed mid-execution can be resumed; the resume is an "atomic" retry of the whole task. Idempotency must hold.

What to avoid:

- Don't retry without jitter. Synchronisation kills services.
- Don't retry forever. Always have a cap.
- Don't retry every exception. Be specific.
- Don't combine retry with non-idempotent code without dedup.
- Don't log every retry at INFO; logs become noise.

## 6. Open questions

- **Adaptive retry policies.** Adjust retry budgets based on observed success rate. Complex; only worth it for very high traffic.
- **Cross-tier retry coordination.** Client retries, gateway retries, backend retries — together they multiply. Single-tier-of-retry is the discipline; achieving it across many services takes care.
- **The right backoff base for LLM calls.** Provider rate limits often want 1-10s base waits; transient network errors want ~100ms. One-size-fits-none. Per-provider configuration.

## 7. References (curated)

- aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/ — Brooker's article.
- aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/ — Amazon Builders' Library, longer.
- github.com/jd/tenacity — tenacity.
- github.com/hynek/stamina — stamina (modern wrapper).
- github.com/encode/httpx — httpx with built-in retry transport.
- Companion docs: [[05-idempotency-design]], [[07-circuit-breaker]], [[09-timeout-patterns]].

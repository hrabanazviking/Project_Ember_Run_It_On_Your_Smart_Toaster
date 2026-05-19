# 38 — Caching Strategies and Memoization

**Category:** Performance
**Runa relevance:** Heimskringla cache (ADR-0002 §D-2.4), Muninn retrieval cache, function memoization
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

A cache trades memory for speed: store the result of an expensive computation; serve it from store next time. Done well, caches turn O(N) into O(1) for common cases and dramatically reduce dependency calls. Done poorly, caches accumulate forever (memory leak), serve stale data (correctness bug), or invalidate inconsistently (race condition).

For Runa, caching is everywhere — Heimskringla's per-provider response cache (ADR-0002 §D-2.4), Muninn's retrieval-result cache, function-level memoization of expensive deterministic computations. Knowing the patterns (LRU, TTL, write-through, write-behind) and the pitfalls (invalidation, stampede) is craft worth investing in.

## 2. Technique / mechanism

**functools.lru_cache (stdlib):**

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_pure_function(arg: int) -> int:
    return compute(arg)

# Inspect / clear
print(expensive_pure_function.cache_info())  # hits, misses, currsize, maxsize
expensive_pure_function.cache_clear()
```

- *Pure* functions only (deterministic, no side effects, hashable args).
- `maxsize=None` = unbounded (memory hazard).
- `maxsize=...` = LRU eviction.
- Thread-safe in CPython.

**functools.cache (3.9+):**

```python
from functools import cache

@cache  # unbounded — only safe for finite input space
def factorial(n: int) -> int:
    return 1 if n <= 1 else n * factorial(n - 1)
```

**cachetools — richer cache types:**

```python
from cachetools import LRUCache, TTLCache, LFUCache

cache = TTLCache(maxsize=1000, ttl=300)  # 5 minute TTL
cache["key"] = value
value = cache.get("key")  # returns None if expired

cache = LFUCache(maxsize=1000)  # least-frequently-used eviction
```

`cachetools` supports `@cached(cache)` decorator for memoizing arbitrary functions with custom cache types.

**Async caches:**

```python
from async_lru import alru_cache

@alru_cache(maxsize=1000)
async def fetch(url: str) -> str:
    return await httpx.get(url).text
```

`async_lru` or `aiocache` for async function memoization. Plain `lru_cache` doesn't handle awaitables correctly.

**Disk-backed caches — diskcache:**

```python
from diskcache import Cache

cache = Cache("/tmp/runa/cache")
cache.set("key", expensive_result, expire=300)
result = cache.get("key")

# Or with decorator
@cache.memoize(expire=300)
def expensive(arg):
    return ...
```

Disk-backed survives process restarts. Slower than in-memory; persistent.

**Write-through vs write-behind:**

- **Write-through:** every write goes to both cache and backing store immediately. Cache always consistent.
- **Write-behind (write-back):** writes go to cache; async flushed to backing store. Faster writes; risk of loss on crash.
- **Read-through:** cache miss triggers fetch + store. Common pattern.

Pick based on consistency vs performance needs.

**TTL strategies:**

- **Fixed TTL:** every entry expires N seconds after write.
- **Sliding TTL:** access resets the timer. Hot keys stay; cold keys evict.
- **Jittered TTL:** add random jitter so many entries don't expire simultaneously (avoids cache stampede).

**Cache stampede:**

When a hot key expires, many concurrent requests miss the cache and all compute / fetch the value. Mitigations:
- **Lock around computation:** one client computes; others wait.
- **Probabilistic early expiration:** start computing slightly before actual expiration.
- **Pre-warm** known hot keys.

```python
from threading import Lock

class StampedeProtectedCache:
    def __init__(self, ttl: float):
        self._cache = {}
        self._locks: dict[str, Lock] = {}
        self._main_lock = Lock()
        self._ttl = ttl
    
    def get_or_compute(self, key: str, compute_fn) -> Any:
        cached = self._cache.get(key)
        if cached and time.monotonic() - cached[1] < self._ttl:
            return cached[0]
        
        with self._main_lock:
            if key not in self._locks:
                self._locks[key] = Lock()
            key_lock = self._locks[key]
        
        with key_lock:
            # Re-check after acquiring lock
            cached = self._cache.get(key)
            if cached and time.monotonic() - cached[1] < self._ttl:
                return cached[0]
            value = compute_fn()
            self._cache[key] = (value, time.monotonic())
            return value
```

**Cache invalidation:**

"There are only two hard things in Computer Science: cache invalidation and naming things." — Phil Karlton.

Strategies:
- **Time-based:** TTL. Simplest; eventual consistency.
- **Tag-based:** invalidate all entries with tag X. Requires tagging.
- **Event-based:** subscribe to changes; invalidate on event. Coordinated.
- **Compare-and-set:** version each entry; cache miss if version differs from source.

For Runa, mostly TTL — agent context evolves slowly enough.

**Semantic caching for LLM:**

[[33-model-routing-ensembles]] (research corpus) describes Heimskringla's semantic-dedup cache. Implementation sketch:

```python
class SemanticCache:
    def __init__(self, embedder, threshold=0.92, max_age_s=3600):
        self.embedder = embedder
        self.threshold = threshold
        self.max_age = max_age_s
        self._entries: list[tuple[list[float], str, str, float]] = []  # (embedding, prompt, response, ts)
    
    def lookup(self, prompt: str) -> str | None:
        prompt_emb = self.embedder.embed(prompt)
        for emb, _, response, ts in self._entries:
            if time.monotonic() - ts > self.max_age:
                continue
            if cosine_similarity(prompt_emb, emb) >= self.threshold:
                return response
        return None
    
    def store(self, prompt: str, response: str):
        emb = self.embedder.embed(prompt)
        self._entries.append((emb, prompt, response, time.monotonic()))
        # Cap size with LRU-style eviction
```

## 3. Key works / libraries

- **`functools.lru_cache` / `functools.cache`** — stdlib.
- **`cachetools`** — github.com/tkem/cachetools.
- **`diskcache`** — github.com/grantjenks/python-diskcache.
- **`async_lru`** — github.com/aio-libs/async-lru.
- **`aiocache`** — github.com/aio-libs/aiocache. Multi-backend (memory, redis, memcached).
- **Karger et al.** "Consistent Hashing and Random Trees." STOC 1997. For distributed caches.
- **Belady's optimal algorithm** — theoretical optimal cache; unattainable but reference.

## 4. Pitfalls and gotchas

- **Unbounded caches.** Memory leak.
- **Mutable cache values.** Caller mutates returned object; cache now corrupt.
- **Cache key collisions.** Different inputs hash to same key. Use enough specificity.
- **Stale-data correctness bugs.** Cache says X; truth is Y. Decide tolerance per data.
- **Cache stampede.** Hot key expires; thundering herd.
- **Cache + async without `async_lru`.** Plain `lru_cache` caches the *coroutine object*, not the result.
- **Cache for non-deterministic functions.** LLM with `temperature > 0` produces different outputs; "cached result" is one realisation, not truth.

## 5. Applicability to Runa

For **Heimskringla per-provider cache** (ADR-0002 §D-2.4):

- Per-provider TTL-cache, keyed by request hash.
- Diskcache-backed if persistence across restarts wanted.

For **Heimskringla semantic-dedup cache** (ADR-0002 §D-2.4):

- In-memory + bounded; embedding model is the same as Muninn's.

For **Muninn retrieval cache**:

- Per-query result cache with short TTL (~60s). Repeat queries (common in agent loops) skip recompute.

For **Function memoization**:

- `@lru_cache(maxsize=N)` for pure functions.
- `@async_lru` for async pure functions.

For **expensive computation reuse within a turn**:

- ContextVar-scoped cache that lives for one turn only. Different from process-wide caches.

What to avoid:

- Don't cache without bounds.
- Don't cache mutable objects (or freeze them).
- Don't trust TTL alone for correctness-critical data.
- Don't cache LLM outputs at temp > 0 as authoritative.

## 6. Open questions

- **Distributed caching.** Cross-Pi caches require Redis or similar. For single-Pi Runa, not needed.
- **Cache invalidation by upstream events.** Reactive invalidation is cleaner than TTL but requires plumbing.
- **Cache pre-warming.** Predicting next-likely queries; promising area.

## 7. References (curated)

- docs.python.org/3/library/functools.html.
- github.com/tkem/cachetools.
- github.com/grantjenks/python-diskcache.
- aws.amazon.com/builders-library/caching-challenges-and-strategies/ — Amazon Builders' Library.
- Companion docs: [[05-idempotency-design]], [[33-model-routing-ensembles]] (research corpus), [[37-memory-profiling]].

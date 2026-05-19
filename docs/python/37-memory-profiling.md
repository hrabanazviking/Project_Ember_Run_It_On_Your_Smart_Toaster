# 37 — Memory Profiling: tracemalloc, memray, objgraph

**Category:** Performance
**Runa relevance:** Pi 5 memory budget (16 GB total), long-running process leak prevention
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

CPU profiling tells you where time goes; memory profiling tells you where bytes go. For long-running processes (Runa runs indefinitely on a Pi), memory leaks are *the* killer — slow growth that eventually triggers OOM and restart. Memory profiling tools — **tracemalloc** (stdlib), **memray** (Bloomberg's modern profiler), **objgraph** (visualises reference structures), **pympler** — let you find what's accumulating and why.

For Runa specifically, the 16 GB Pi 5 has ~12-14 GB available after the agent and its models. A subtle leak of 10 MB/hour means a restart every 1000+ hours — annoying. A leak of 100 MB/hour means restart every 100 hours — disruptive. The discipline is to detect leaks during development, not in production.

## 2. Technique / mechanism

**tracemalloc (stdlib, free):**

```python
import tracemalloc

tracemalloc.start()
# ... do work
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")

for stat in top_stats[:20]:
    print(stat)
```

Output:
```
src/runa/muninn.py:42: size=12.5 MiB, count=12345
src/runa/cache.py:88: size=8.1 MiB, count=8888
...
```

**Compare snapshots (find growth):**

```python
tracemalloc.start()

snapshot1 = tracemalloc.take_snapshot()
# ... run workload
snapshot2 = tracemalloc.take_snapshot()

diff = snapshot2.compare_to(snapshot1, "lineno")
for stat in diff[:10]:
    print(stat)  # shows growth per line
```

Useful for "what's leaking between iteration N and N+1."

**memray (Bloomberg):**

```bash
pip install memray

# Profile a script
memray run -o mem.bin script.py

# Live view (attach to running process)
memray run --live script.py

# Generate reports
memray flamegraph mem.bin -o flamegraph.html
memray summary mem.bin
memray tree mem.bin
```

memray captures *every* allocation. Lower overhead than tracemalloc; richer reports.

**objgraph (find ref-leaks):**

```python
import objgraph

# How many of each type?
objgraph.show_most_common_types(limit=20)

# Find what holds a reference to X (why isn't it GC'd?)
x = my_leaked_obj
objgraph.show_backrefs([x], max_depth=4, filename="refs.png")
```

When an object should have been GC'd but isn't, objgraph traces what's still pointing to it.

**`gc` module — manual control:**

```python
import gc

gc.collect()  # force a collection
print(gc.get_count())  # tuple of (gen0, gen1, gen2) counts
print(gc.get_threshold())  # collection thresholds

# Get all objects of a type
objects = [o for o in gc.get_objects() if isinstance(o, Episode)]
```

**pympler — broader memory tooling:**

```bash
pip install pympler
```

```python
from pympler import asizeof, summary, muppy

asizeof.asizeof(obj)  # actual size including nested

all_objects = muppy.get_objects()
sum_ = summary.summarize(all_objects)
summary.print_(sum_)
```

**Common leak patterns:**

- **Caches without size limit.** A dict that grows forever. Use `functools.lru_cache(maxsize=...)` or `cachetools.LRUCache`.
- **Closures holding large references.** A closure captures the whole enclosing scope.
- **Circular references with __del__.** GC can't handle. Use `weakref` or break the cycle.
- **Threads / tasks not joined.** Resources held until process death.
- **C extensions with refcount bugs.** Rare; severe.
- **Cached compiled regexes** (`re.compile` is interned; not actually a leak).

**Avoiding leaks:**

```python
import weakref

class Cache:
    def __init__(self):
        self._cache: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
    
    def store(self, key, obj):
        self._cache[key] = obj  # auto-removed when obj otherwise GC'd
```

**Bounded LRU cache:**

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive(arg):
    return compute(arg)
```

Auto-evicts when full. Use `cache.cache_clear()` to reset; `cache.cache_info()` to inspect.

## 3. Key works / libraries

- **`tracemalloc` stdlib** — docs.python.org/3/library/tracemalloc.html.
- **`memray`** — bloomberg.github.io/memray.
- **`objgraph`** — mg.pov.lt/objgraph/.
- **`pympler`** — pympler.readthedocs.io.
- **`gc` stdlib** — docs.python.org/3/library/gc.html.
- **`weakref` stdlib** — docs.python.org/3/library/weakref.html.
- **Beazley** — talks on Python memory.

## 4. Pitfalls and gotchas

- **Python doesn't return memory to OS easily.** Once allocated, often retained. Restart for cleanup; alternatively, periodic worker recycling ([[21-multiprocessing-deep-dive]]).
- **Process RSS doesn't tell the whole story.** Shared libraries, mmap'd files, fragmentation. RSS ≠ Python heap.
- **tracemalloc adds overhead.** Don't enable in production unless investigating.
- **memray overhead** also non-trivial; not always-on.
- **`gc.collect()` doesn't catch C-extension leaks.** Only Python objects.
- **Cyclic GC pauses.** For latency-sensitive code, `gc.freeze()` (3.7+) can reduce pause times.
- **Strong refs in unexpected places.** Imported modules, class hierarchies, frame locals. objgraph helps find them.

## 5. Applicability to Runa

For **development**:

- Periodic memray runs against integration tests. Watch growth across many iterations.
- tracemalloc-based snapshots in suspected leak areas.

For **production-on-Pi**:

- `psutil` to monitor process RSS continuously. Eir tracks and warns on growth trend.
- `runa doctor` shows current memory usage per subsystem.

For **Smiðja workers**:

- `max_tasks_per_child=100` in ProcessPoolExecutor — workers recycle every 100 tasks. Catches slow leaks.

For **caches**:

- All caches bounded (`functools.lru_cache(maxsize=...)`, `cachetools.LRUCache`).
- Heimskringla semantic-dedup cache TTL-bound.
- Muninn keeps unbounded data on disk, not in memory.

For **Pi memory budget**:

- ~12-14 GB available. Default 7B Q4 model uses ~5-6 GB. KV-cache adds 1-2 GB. Runa proper should fit comfortably in ~2 GB headroom.

What to avoid:

- Don't make unbounded caches.
- Don't hold references to objects you don't need (especially in long-running tasks).
- Don't relly on `__del__` for cleanup.
- Don't ignore memory growth — investigate.

## 6. Open questions

- **Continuous memory profiling** — overhead vs visibility trade-off. memray's `--live` mode is a start.
- **Free-threaded Python memory model.** Some patterns may change with no-GIL.
- **Tracking model-weight memory.** Loaded LLM weights show as one big mmap. Excluded from many profilers.

## 7. References (curated)

- docs.python.org/3/library/tracemalloc.html.
- bloomberg.github.io/memray.
- pympler.readthedocs.io.
- Companion docs: [[21-multiprocessing-deep-dive]] (worker recycling), [[36-profiling-python]] (CPU side), [[38-caching-strategies]].

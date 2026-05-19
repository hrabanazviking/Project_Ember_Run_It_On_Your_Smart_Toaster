# 39 — Lazy Evaluation Patterns

**Category:** Performance
**Runa relevance:** Muninn streaming, large file processing, kernel pipelines
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

**Lazy evaluation** computes values only when needed. The opposite — *eager* evaluation — computes everything upfront, even results that aren't consumed. For sequences, files, and expensive transformations, laziness can reduce memory by orders of magnitude and start producing useful output before all work is done.

Python's `generator`s, `iterator`s, `__lazy__` descriptors, and async generators are all lazy. `list comprehensions` are eager. `map` and `filter` are lazy in Python 3 (eager in Python 2). Knowing when each is right is a basic craft skill that pays off in memory and latency.

## 2. Technique / mechanism

**Generators — `yield`:**

```python
def read_lines(path: Path):
    with open(path) as f:
        for line in f:
            yield line.strip()

# Iterates one line at a time; never loads whole file
for line in read_lines("huge.txt"):
    process(line)
```

Memory: O(1) per line, not O(file size).

**Generator expressions:**

```python
# Eager (list)
squares = [x * x for x in range(1_000_000)]  # 8 MB

# Lazy (generator)
squares = (x * x for x in range(1_000_000))  # ~0 bytes
total = sum(squares)
```

Replace `[...]` with `(...)` to make it lazy.

**Itertools:**

```python
from itertools import islice, chain, groupby, takewhile, dropwhile

# First 10 items of an infinite stream
first_10 = list(islice(infinite_stream(), 10))

# Chain multiple iterables lazily
combined = chain(stream_a, stream_b, stream_c)

# Group consecutive same-key items
for key, group in groupby(items, key=lambda x: x.category):
    ...
```

`itertools` is a goldmine for lazy operations. Worth full read.

**Async generators:**

```python
async def stream_episodes() -> AsyncIterator[Episode]:
    async for row in db.execute("SELECT ..."):
        yield Episode.from_row(row)

# Consumer
async for ep in stream_episodes():
    await process(ep)
```

Each `yield` happens when consumed. Memory bounded.

**Lazy attributes — `functools.cached_property`:**

```python
from functools import cached_property

class Episode:
    def __init__(self, text):
        self.text = text
    
    @cached_property
    def embedding(self) -> list[float]:
        # Computed on first access; cached forever after
        return expensive_embed(self.text)
```

First access computes; subsequent accesses return cached.

**Lazy imports:**

```python
def use_heavy_lib():
    import heavy_library  # imported only when this function is called
    return heavy_library.do_thing()
```

Defers a slow import until needed. Cuts startup time.

```python
# Module-level lazy via __getattr__ (PEP 562)
def __getattr__(name):
    if name == "heavy":
        import heavy_library
        return heavy_library
    raise AttributeError(name)
```

**Descriptors for lazy attributes:**

```python
class lazy_property:
    """Older-school cached_property; predates the stdlib version."""
    def __init__(self, fn):
        self.fn = fn
        self.__name__ = fn.__name__
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        value = self.fn(instance)
        setattr(instance, self.__name__, value)
        return value
```

**Streaming JSON:**

```python
import ijson

# Iterative JSON parser — handles huge files
with open("huge.json", "rb") as f:
    for episode in ijson.items(f, "item"):
        process(episode)
```

`ijson` (or stream-friendly libraries) for files too large to load.

**Streaming CSV / etc:**

```python
import csv

with open("huge.csv") as f:
    reader = csv.DictReader(f)  # lazy
    for row in reader:
        process(row)
```

`pandas` is eager by default; `dask` is lazy alternative for huge datasets.

**Memoization-as-lazy:**

A `@cached_property` is lazy evaluation + caching. Compute-once-on-demand pattern.

## 3. Key works / libraries

- **PEP 255** — Simple Generators.
- **PEP 525** — Asynchronous Generators.
- **PEP 562** — Module `__getattr__`.
- **`itertools` stdlib** — docs.python.org/3/library/itertools.html.
- **`more-itertools`** — github.com/more-itertools/more-itertools.
- **`functools.cached_property`** — stdlib.
- **`ijson`** — pypi.org/project/ijson.
- **`dask`** — dask.org. Lazy parallel dataframes.

## 4. Pitfalls and gotchas

- **Generators are one-shot.** Once consumed, they're exhausted. Recreate to iterate again.
- **`list(generator)` materialises everything.** Defeats laziness.
- **Closing files holding generators.** A generator that wraps an open file keeps the file open. Use context managers carefully.
- **Lazy import circular dependencies.** Deferring an import can hide a circular import that eager would catch.
- **`cached_property` and pickling.** Cached value is on the instance, may pickle.
- **Iterator vs generator.** Generators are iterators; not all iterators are generators. Pickling differs.
- **Lazy evaluation in test assertions.** Generators that haven't been consumed don't show their content in repr.

## 5. Applicability to Runa

For **Muninn streaming reads**:

- Iterating over millions of episodes uses async generators. No load-all-into-memory.

For **kernel pipeline stages**:

- Pipe stages (retrieval → context build → model call) can yield items as they become ready, rather than batch-then-pass.

For **large file processing in Smiðja**:

- Reading huge input files line-by-line or chunk-by-chunk; never load whole.

For **Saga prose generation**:

- Reading large event-log fixtures via streaming; building chapters incrementally.

For **lazy attribute computation**:

- `@cached_property` on Episode for embedding (computed lazily on first access).
- `@cached_property` on State objects for derived views.

For **startup-time optimisation**:

- Lazy imports of heavy modules (transformers, sentence-transformers) only when needed. Cuts Runa startup time.

What to avoid:

- Don't accidentally `list()` a generator.
- Don't pass generators that outlive their backing resources.
- Don't lazy-import where eager would expose import bugs.
- Don't make everything lazy "just in case" — eager is simpler when sizes are small.

## 6. Open questions

- **Async streaming with backpressure.** Naturally provided by async generators; sometimes wants explicit window control.
- **Lazy evaluation and type checkers.** Generators have type `Iterator[T]` or `Generator[T, None, None]`; subtle differences.

## 7. References (curated)

- docs.python.org/3/library/itertools.html.
- PEP 255, 525, 562.
- github.com/more-itertools/more-itertools.
- realpython.com/introduction-to-python-generators/.
- Companion docs: [[19-asyncio-advanced]], [[24-queue-channel-patterns]], [[38-caching-strategies]].

# 28 — Protocol Classes and Structural Typing

**Category:** Type Safety & Validation
**Runa relevance:** dependency injection, skill contracts, adapter interfaces, test doubles
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

In **nominal typing** (Java, C# default), a class satisfies an interface only by *explicitly inheriting* from it. In **structural typing** (Go, TypeScript, Python via PEP 544), a class satisfies an interface by *having the right methods and attributes* — no inheritance required. Python's **Protocol** (PEP 544, 2017) brings structural typing as a first-class feature, joining the older `typing.Generic` and ABC machinery.

For Runa, Protocols are the right way to type dependencies. "I need something that can `write_episode(episode)`" should be expressed as a Protocol — any class that has that method satisfies it, without needing to inherit from a shared base. This makes test doubles trivial, dependency injection clean, and code less coupled to specific implementations.

## 2. Technique / mechanism

**Basic protocol:**

```python
from typing import Protocol

class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...

def use(embedder: Embedder, texts: list[str]) -> list[list[float]]:
    return [embedder.embed(t) for t in texts]

# Any class with an embed(text) -> list[float] method satisfies Embedder
class BgeEmbedder:
    def embed(self, text: str) -> list[float]:
        return self.model.encode(text)

class StubEmbedder:
    def embed(self, text: str) -> list[float]:
        return [0.0] * 384  # for tests

use(BgeEmbedder(), texts)   # mypy passes
use(StubEmbedder(), texts)  # mypy passes
```

No inheritance needed; structure matches.

**Runtime-checkable protocols:**

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

def cleanup(things: list[Closeable]) -> None:
    for t in things:
        if isinstance(t, Closeable):  # runtime check works
            t.close()
```

`@runtime_checkable` allows `isinstance(x, Protocol)`. Caveat: only checks method presence, not signatures.

**Generic protocols:**

```python
from typing import Protocol, TypeVar

T = TypeVar("T")

class Cache(Protocol[T]):
    def get(self, key: str) -> T | None: ...
    def put(self, key: str, value: T) -> None: ...

def use(cache: Cache[Episode]) -> None: ...
```

**Protocol vs ABC:**

| Aspect | Protocol | ABC |
|---|---|---|
| Inheritance required | No | Yes |
| Multiple implementations | Trivial (no relationship needed) | Requires shared base |
| Third-party types can satisfy | Yes (any class with right shape) | No (must inherit) |
| Default implementations | No | Yes |
| `isinstance` check | Only if `runtime_checkable` | Always |
| Use case | Typing dependencies, "duck typing with teeth" | Code reuse via inheritance |

**Protocol with default methods (3.12+):**

```python
class Greeter(Protocol):
    def greet(self) -> str: ...
    
    def loud_greet(self) -> str:  # default method
        return self.greet().upper()
```

Less commonly used.

**Protocol for callable interfaces:**

```python
class EventHandler(Protocol):
    def __call__(self, event: Event) -> None: ...

def register(handler: EventHandler) -> None: ...

# Any callable matching the signature works
register(lambda e: print(e))
register(SomeClass().method)
```

**Variance in protocols:**

```python
T_co = TypeVar("T_co", covariant=True)

class Reader(Protocol[T_co]):
    def read(self) -> T_co: ...

# Reader[Cat] is a Reader[Animal]
```

Covariance for read-only; contravariance for write-only.

**Composition (Intersection):**

```python
class A(Protocol):
    def a(self) -> int: ...

class B(Protocol):
    def b(self) -> str: ...

class AB(A, B, Protocol):
    pass

def use(x: AB) -> None:
    x.a()
    x.b()
```

Multiple protocols compose via inheritance (which here is just for the protocol definition).

## 3. Key works / libraries

- **PEP 544** — Protocols: Structural subtyping.
- **`typing.Protocol`** — stdlib.
- **TypeScript's structural typing** — influential design.
- **Go interfaces** — pure structural typing reference.
- **Hettinger's PyCon talks** on Protocol vs ABC.

## 4. Pitfalls and gotchas

- **`@runtime_checkable` doesn't check signatures.** Just method presence. A class with `close(self, mode)` satisfies a protocol declaring `close(self)` at runtime.
- **Protocol inheritance can be confusing.** Inheriting from a protocol mostly works but interacts with normal MRO.
- **`Protocol` itself can't be instantiated.**
- **Self-types in protocols** need `Self` (PEP 673) for chaining methods.
- **Performance of `isinstance(x, Protocol)`** is slow — it iterates over the protocol's methods.
- **Static typing won't catch missing methods if you don't use mypy.** Hints are advisory.

## 5. Applicability to Runa

For **dependency typing**:

- "What does `runa.core.kernel` need from the embedding model?" → `Embedder` Protocol.
- "What does Muninn writer need from the storage layer?" → `EpisodeStore` Protocol.
- Each subsystem accepts dependencies typed as Protocols.

For **test doubles**:

- `StubEmbedder`, `StubProvider`, `InMemoryStore` — none inherit from production classes; all satisfy the same Protocols. Tests use stubs; production uses real implementations.

For **adapter contracts**:

- Per-adapter `Adapter` Protocol declaring `start`, `stop`, `health`. All adapter implementations satisfy it without sharing a base.

For **plugin contracts**:

- `Plugin` Protocol declares the call surface. Plugins implement it structurally.

For **skill contracts**:

- `Skill` Protocol: `invoke(context, args) -> SkillResult`. Skills satisfy without inheritance.

What to avoid:

- Don't reach for ABC when Protocol fits. Protocol is lighter.
- Don't `@runtime_checkable` everything — it adds overhead.
- Don't conflate Protocol with Pydantic BaseModel. Different layers; both useful.

## 6. Open questions

- **Default-method Protocols** (3.12+) — when to use? Borders on "abstract base class lite."
- **Protocol composition** — combining many protocols can produce hard-to-read types.
- **Performance of runtime checks** — improves over Python versions but still nontrivial.

## 7. References (curated)

- PEP 544.
- docs.python.org/3/library/typing.html#typing.Protocol.
- mypy.readthedocs.io/en/stable/protocols.html.
- Companion docs: [[25-type-hints-mastery]], [[26-mypy-strict-mode]], [[27-pydantic-runtime-validation]], [[35-test-doubles]], [[41-dependency-injection]].

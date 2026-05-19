# 25 — Type Hints Mastery: PEPs and Idioms

**Category:** Type Safety & Validation
**Runa relevance:** every public function, runa.schemas, every subpackage boundary
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Python's type system, layered on via PEPs over a decade (PEP 484 in 2014 through to PEP 695 in 2023), has become genuinely powerful. Modern Python code with full type hints is *checked* by mypy, pyright, or pyrefly — catching whole categories of bugs at edit time. The hints also serve as machine-readable documentation, drive IDE autocomplete, and inform runtime tools like Pydantic.

For Runa, type hints are non-negotiable on every public function and every cross-subpackage interface. The discipline pays for itself in caught bugs, faster onboarding for new contributors, and the ability to refactor safely. The trick is knowing *which* type-system features to use and which to avoid as overkill.

## 2. Technique / mechanism

**The core PEPs:**

- **PEP 484** (2014) — type hints, the foundation.
- **PEP 526** (2016) — variable annotations.
- **PEP 544** (2017) — Protocols (structural typing).
- **PEP 585** (2019) — built-in generic types (`list[int]` instead of `List[int]`).
- **PEP 604** (2019) — union types via `X | Y` (instead of `Union[X, Y]`).
- **PEP 612** (2019) — `ParamSpec` for typing higher-order functions.
- **PEP 646** (2020) — variadic generics (TypeVarTuple).
- **PEP 673** (2022) — `Self` type.
- **PEP 695** (2023) — new type-parameter syntax (`def f[T](x: T) -> T:`).

**Modern syntax (3.12+):**

```python
def first_or_none[T](items: list[T]) -> T | None:
    return items[0] if items else None

class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T | None:
        return self._items.pop() if self._items else None
```

**The essential annotations:**

```python
from typing import Protocol, runtime_checkable
from collections.abc import Iterable, Mapping, Callable, Awaitable
from datetime import datetime
from uuid import UUID

# Built-in generics (PEP 585)
def get_users() -> list[User]: ...
def by_id() -> dict[UUID, User]: ...
def lines() -> tuple[str, ...]: ...  # variadic tuple

# Union (PEP 604)
def find(query: str) -> User | None: ...

# Optional shortcut
def maybe(x: int | None = None): ...

# Callables
def with_callback(cb: Callable[[int, str], bool]) -> None: ...

# Async
async def fetch(url: str) -> str: ...
def background(work: Awaitable[None]) -> None: ...

# Iterable (covariant in T)
def process(items: Iterable[Event]) -> list[Result]: ...

# Literal
from typing import Literal
def set_mode(mode: Literal["read", "write", "rw"]) -> None: ...

# Final
from typing import Final
MAX_RETRIES: Final[int] = 5
```

**Protocols — structural typing (PEP 544):**

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class SupportsClose(Protocol):
    def close(self) -> None: ...

def cleanup(things: list[SupportsClose]) -> None:
    for t in things:
        t.close()

# No need for inheritance; any class with .close() satisfies the protocol
cleanup([file_handle, db_connection, custom_object])
```

Protocols are the right abstraction for "I need an object that looks like X" without forcing inheritance. See [[28-protocol-classes]].

**TypedDict — typed dictionaries:**

```python
from typing import TypedDict

class EpisodeDict(TypedDict):
    episode_id: str
    text: str
    timestamp: str

ep: EpisodeDict = {"episode_id": "abc", "text": "hello", "timestamp": "..."}
```

Useful for JSON-like data without going to Pydantic.

**NewType — distinct nominal types:**

```python
from typing import NewType

UserId = NewType("UserId", str)
EpisodeId = NewType("EpisodeId", str)

def get_user(id: UserId) -> User: ...

# Type-checker rejects passing EpisodeId where UserId is expected,
# even though both are strings at runtime
```

Zero runtime cost; distinct at type-check time. Use for IDs and other "secret strings."

**ParamSpec — typing higher-order functions:**

```python
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def with_logging(fn: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.info("calling %s", fn.__name__)
        return fn(*args, **kwargs)
    return wrapper

@with_logging
def do_thing(x: int, y: str) -> bool: ...
# Type checker preserves the (int, str) -> bool signature through the decorator
```

**Generic classes:**

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Cache(Generic[T]):
    def get(self, key: str) -> T | None: ...
    def put(self, key: str, value: T) -> None: ...

# Usage
episode_cache: Cache[Episode] = Cache()
```

Or with the new PEP 695 syntax:
```python
class Cache[T]:
    ...
```

**Forward references:**

```python
from __future__ import annotations  # all annotations become strings; resolves later

class Node:
    parent: "Node"  # forward reference
    children: list["Node"]
```

**Type aliases:**

```python
from typing import TypeAlias

UserId: TypeAlias = str  # old style
type UserId = str        # PEP 695 (3.12+)
```

## 3. Key works / libraries

- **PEPs 484, 526, 544, 585, 604, 612, 646, 673, 695** — the foundation.
- **mypy** — github.com/python/mypy. The original type checker.
- **pyright** — github.com/microsoft/pyright. Microsoft's faster, often stricter checker.
- **pyrefly** — github.com/facebookarchive/pyre-check (renamed) — Facebook's checker.
- **typing-extensions** — typing-extensions backports.
- **`mypy` documentation** — mypy.readthedocs.io.
- **PEP 8** — the style guide that informs annotation placement.
- **`monkeytype`, `pyannotate`** — tools that infer annotations from runtime traces.

## 4. Pitfalls and gotchas

- **Annotations stringified by `from __future__ import annotations`** — Pydantic v1 had issues; v2 mostly fine.
- **Annotations evaluated at class-definition time** can break with circular imports; use string forms or `TYPE_CHECKING` block.
- **`Any` is a hole.** Tolerated in legacy code; rejected in new code with mypy strict.
- **`# type: ignore` should be specific:** `# type: ignore[attr-defined]` not bare `# type: ignore`.
- **Variance** — covariant `Sequence[Cat]` is a `Sequence[Animal]`; mutable `list[Cat]` is *not* a `list[Animal]`. Trips up users.
- **Generic class invariance** — `Cache[Cat]` is not `Cache[Animal]` even if Cat extends Animal. Use Protocol with covariant TypeVars when appropriate.
- **`TypedDict` doesn't enforce at runtime.** Pydantic does. Choose intentionally.
- **Inheritance + Protocol** — a class can both inherit and satisfy a protocol; sometimes confusing.

## 5. Applicability to Runa

For **every public function in `src/runa/`**:

- Full type hints on parameters and return type.
- Use built-in generics (`list[X]`), union pipes (`X | None`), modern syntax.

For **`runa.schemas`**:

- Pydantic models for boundary types.
- TypedDict for JSON-shaped data without validation needs.
- NewType for IDs (`UserId`, `EpisodeId`, `ConversationId`).

For **subpackage interfaces**:

- Protocols for "behaviour-shaped" dependencies (an `Embedder`, a `Cache`, a `Storage`).
- Inheritance only where there's actual code sharing.

For **decorators and higher-order functions**:

- ParamSpec for transparent decorators.

For **async code**:

- `Awaitable[T]`, `Coroutine[Any, Any, T]`, `AsyncIterable[T]` per the actual return shape.

What to avoid:

- Don't use `Any` in new code. Use specific types or generic `T`.
- Don't ship code without type hints on public functions.
- Don't repeat type info in docstrings (e.g., ":param x: int — the count" when the signature already says `x: int`). The hint is the truth.
- Don't use `from typing import List, Dict, Tuple` in new code — use built-in generics.

## 6. Open questions

- **Pyright vs mypy.** Both work; pyright is faster and stricter; mypy is more established. Use what your team prefers.
- **PEP 695 adoption.** New `def f[T]` syntax is cleaner but requires 3.12+. Worth migrating when minimum version allows.
- **Runtime type checking** (Pydantic, beartype, typeguard) vs static. Combine for boundary safety + interior speed.

## 7. References (curated)

- PEP 484, 526, 544, 585, 604, 612, 646, 673, 695.
- mypy.readthedocs.io.
- github.com/microsoft/pyright.
- realpython.com/python-type-checking/ — practical intro.
- Companion docs: [[26-mypy-strict-mode]], [[27-pydantic-runtime-validation]], [[28-protocol-classes]], [[29-dataclasses-namedtuple-attrs]].

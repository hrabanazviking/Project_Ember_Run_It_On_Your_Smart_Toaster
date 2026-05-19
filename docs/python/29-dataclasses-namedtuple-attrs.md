# 29 — Dataclasses, NamedTuple, attrs — When to Use Which

**Category:** Type Safety & Validation
**Runa relevance:** internal value objects, schemas, fast-path types
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Python has three popular ways to declare structured data classes: **`dataclass`** (stdlib, 3.7+), **`NamedTuple`** (stdlib, immutable tuple-backed), and **`attrs`** (third-party, the influential predecessor of dataclass). Plus **Pydantic** ([[27-pydantic-runtime-validation]]) for runtime-validated types. Each has a niche; mixing them is fine; picking the wrong one for the job produces awkward code.

For Runa, the rule of thumb: Pydantic at boundaries, dataclass for internal value objects, NamedTuple for fast tuple-shaped data, attrs occasionally for advanced cases. Knowing the trade-offs saves time.

## 2. Technique / mechanism

**`dataclass`:**

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class Episode:
    episode_id: UUID
    text: str
    timestamp: datetime
    tags: list[str] = field(default_factory=list)
```

Features:
- `__init__`, `__repr__`, `__eq__` generated.
- `frozen=True` makes instances immutable + hashable.
- `slots=True` (3.10+) reduces memory + speeds attribute access.
- `field(default_factory=list)` for mutable defaults.
- `field(compare=False)` to exclude fields from `__eq__`.

**`NamedTuple`:**

```python
from typing import NamedTuple

class Point(NamedTuple):
    x: float
    y: float
    name: str = "origin"

p = Point(1.0, 2.0)
p.x  # 1.0
p[0]  # 1.0 — also tuple-indexable
p == (1.0, 2.0, "origin")  # True — tuple equality
```

Features:
- Immutable (it's a tuple).
- Tuple-indexable.
- Hashable.
- Tuple-comparable.
- Smaller than dataclass.
- *No methods can mutate state.*

Use when:
- The data is logically a tuple ("a point is (x, y)").
- Tuple semantics (unpacking, indexing) are wanted.
- Maximum memory efficiency.

**`attrs`:**

```python
import attrs

@attrs.frozen
class Episode:
    episode_id: UUID
    text: str = attrs.field(validator=attrs.validators.min_len(1))
    timestamp: datetime
```

Features:
- Predates dataclass; dataclass borrowed from attrs.
- More features: built-in validators, converters, factories.
- Faster than dataclass in some cases.
- More configurable.

Use when:
- You need validators/converters but don't want Pydantic's full weight.
- You need attrs-specific features (slots-by-default, validators).

**Pydantic** (covered in [[27-pydantic-runtime-validation]]):

```python
from pydantic import BaseModel

class EpisodeWrite(BaseModel):
    episode_id: UUID
    text: str
    timestamp: datetime
```

Use at boundaries where data validates from external sources.

**The decision matrix:**

| Need | Use |
|---|---|
| External input validation | Pydantic |
| Internal value object, mutable | `dataclass` |
| Internal value object, immutable + hashable | `dataclass(frozen=True)` |
| Tuple-shaped, immutable, small | `NamedTuple` |
| Advanced validators without Pydantic | `attrs` |
| Just key-value bag, no structure | `dict` |

**Performance comparison (rough, varies):**

- `NamedTuple`: smallest memory, fastest creation, immutable.
- `dataclass(slots=True)`: small memory, fast attribute access.
- `dataclass()`: typical memory, typical access.
- `attrs`: comparable to dataclass.
- `Pydantic`: largest memory, slowest creation (validation runs).
- `dict`: smallest memory if many fields are missing; no type safety.

**Slots = no per-instance `__dict__`:**

```python
@dataclass(slots=True)
class Episode:
    episode_id: UUID
    text: str
```

`slots=True` (3.10+) makes instances ~30-40% smaller and faster but prevents dynamic attribute assignment. Good default for value objects.

**Frozen = immutable + hashable:**

```python
@dataclass(frozen=True, slots=True)
class Episode:
    episode_id: UUID
    text: str

e1 = Episode(UUID("..."), "hello")
{e1}  # works — hashable
e1.text = "new"  # FrozenInstanceError
```

Frozen objects are safe to share across threads ([[20-thread-safety-python]]).

**Mutable default trap:**

```python
# WRONG — mutable default shared across instances
@dataclass
class Config:
    items: list[str] = []  # SyntaxError actually; dataclass forbids it for mutable defaults

# RIGHT — use default_factory
@dataclass
class Config:
    items: list[str] = field(default_factory=list)
```

Dataclass enforces this; NamedTuple lets you make the mistake.

**Conversion between forms:**

```python
@dataclass
class Episode:
    episode_id: UUID
    text: str

ep = Episode(uuid4(), "hello")
ep_dict = asdict(ep)         # {"episode_id": ..., "text": "hello"}
ep_tuple = astuple(ep)        # (UUID(...), "hello")
ep2 = Episode(**ep_dict)      # back
```

For Pydantic: `.model_dump()`, `.model_dump_json()`, `.model_validate(...)`.

## 3. Key works / libraries

- **PEP 557** — Data Classes.
- **`dataclasses` stdlib** — docs.python.org/3/library/dataclasses.html.
- **`attrs`** — github.com/python-attrs/attrs.
- **`typing.NamedTuple`** — stdlib.
- **Pydantic** — covered in [[27-pydantic-runtime-validation]].
- **`pydantic-compat` / `dataclasses-json`** — bridges between forms.

## 4. Pitfalls and gotchas

- **Mutable defaults.** Use `field(default_factory=...)`.
- **NamedTuple is a tuple.** Equality with a regular tuple succeeds. Sometimes confusing.
- **`slots=True` and inheritance.** `slots=True` interacts oddly with class hierarchies; test.
- **`frozen=True` and `__post_init__`.** Can't assign to frozen attributes; use `object.__setattr__(self, name, value)` in `__post_init__`.
- **Pydantic v1 vs v2** — major differences.
- **Pickling dataclasses.** Generally works; slots affect what's pickled.
- **`__eq__` excludes `field(compare=False)`** — useful for caching/timestamps that shouldn't affect equality.

## 5. Applicability to Runa

For **boundary types in `runa.schemas`**:

- Pydantic models. Frozen, extra="forbid".

For **internal value objects**:

- `dataclass(frozen=True, slots=True)`. Memory- and speed-friendly.

For **events on VERÐANDI**:

- Pydantic at the schema layer, dataclass instances inside the loop. Or pure Pydantic if validation cost is negligible.

For **small tuple-shaped data**:

- `NamedTuple` for things like `(x, y)` points, `(start, end)` ranges.

For **task / job descriptors crossing process boundaries**:

- Pydantic models (auto-serialise via JSON for IPC) or `dataclass` + manual to_dict/from_dict.

For **internal cache entries**:

- Plain `dict` or `dataclass`. Don't over-engineer.

What to avoid:

- Don't use Pydantic for hot-loop data. Slow.
- Don't use NamedTuple for things that aren't tuple-shaped.
- Don't mutate frozen objects with `__setattr__` casually — defeats the purpose.
- Don't use class with `__slots__` and `__dict__` simultaneously.

## 6. Open questions

- **Pydantic v2 + dataclass.** Pydantic v2 has `@pydantic.dataclasses.dataclass` — same shape, runtime validation. When worth it?
- **msgspec** — newer alternative to Pydantic, very fast. Worth considering for performance-critical paths.
- **PEP 695 + dataclass** — new generic syntax with dataclass interacts a few subtle ways.

## 7. References (curated)

- docs.python.org/3/library/dataclasses.html.
- PEP 557.
- github.com/python-attrs/attrs.
- pydantic.dev — Pydantic.
- github.com/jcrist/msgspec — msgspec.
- Companion docs: [[25-type-hints-mastery]], [[27-pydantic-runtime-validation]], [[20-thread-safety-python]].

# 27 — Pydantic for Runtime Validation

**Category:** Type Safety & Validation
**Runa relevance:** `runa.schemas`, all boundary types, config loading, adapter payloads
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Type hints ([[25-type-hints-mastery]], [[26-mypy-strict-mode]]) catch errors at *type-check* time. They do *nothing* at runtime — if an adapter sends a `dict[str, Any]` that doesn't match your expected `EpisodeWrite` shape, the type checker sees nothing; the code crashes deep in some access. **Pydantic** is the canonical Python library for *runtime validation* against type-hint-style schemas. Define a model; pass arbitrary data in; Pydantic validates, coerces where reasonable, and raises clear errors when shape is wrong.

For Runa, Pydantic is the validation layer at every boundary: incoming adapter payloads, config files, plugin manifests, stored episode rows being loaded back. Inside Runa, after a Pydantic boundary, the data is *trusted* (type-checker enforces correctness from there).

## 2. Technique / mechanism

**Basic model:**

```python
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from uuid import UUID

class EpisodeWrite(BaseModel):
    model_config = ConfigDict(
        frozen=True,                # immutable after construction
        str_strip_whitespace=True,  # trim string inputs
        extra="forbid",             # reject unknown fields
    )
    
    episode_id: UUID
    text: str = Field(min_length=1, max_length=100_000)
    timestamp: datetime
    speaker: str
    
    @field_validator("speaker")
    @classmethod
    def speaker_is_known(cls, v: str) -> str:
        if v not in {"user", "runa", "tool"} and not v.startswith("agent:"):
            raise ValueError(f"unknown speaker: {v!r}")
        return v
```

Constructing:

```python
# From dict
ep = EpisodeWrite.model_validate({
    "episode_id": "550e8400-e29b-41d4-a716-446655440000",
    "text": "hello",
    "timestamp": "2026-05-17T12:00:00Z",
    "speaker": "user",
})

# From JSON
ep = EpisodeWrite.model_validate_json('{"episode_id":"...","text":"hello",...}')

# Throws ValidationError on bad input with detailed message
```

**Pydantic v2 (the current major version):**

```python
import pydantic
print(pydantic.VERSION)  # should be 2.x

# Pydantic v1 → v2 migration is non-trivial. New code: v2.
```

Key v2 changes from v1:
- `model_validate` instead of `parse_obj`.
- `model_dump` instead of `dict`.
- `model_dump_json` instead of `json`.
- `ConfigDict` instead of `class Config`.
- `field_validator` decorator instead of `validator`.
- Massively faster (Rust-based core).

**Computed fields:**

```python
class Person(BaseModel):
    first: str
    last: str
    
    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first} {self.last}"
```

**Model serialization:**

```python
data = ep.model_dump()       # dict
json_str = ep.model_dump_json()  # string
data_with_meta = ep.model_dump(mode="json")  # JSON-safe types (UUID → str, etc.)
```

**Validation modes:**

```python
ep = EpisodeWrite.model_validate(data, strict=True)  # strict types only
ep = EpisodeWrite.model_validate(data, strict=False)  # coerce where sensible
```

`strict=False` allows `"42"` → `int(42)`. Strict mode rejects.

**Pydantic Settings — env / file config:**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class RunaSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RUNA_",
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    home: Path = Path("~/.runa")
    log_level: str = "INFO"
    
    class memory(BaseSettings):
        store: str = "muninn"
        retrieval_top_k: int = 12

settings = RunaSettings()
# Reads from RUNA_HOME env var, then .env, then defaults
```

**Discriminated unions:**

```python
from typing import Literal, Union
from pydantic import Field

class CatPet(BaseModel):
    kind: Literal["cat"]
    meows: bool

class DogPet(BaseModel):
    kind: Literal["dog"]
    barks: bool

Pet = Union[CatPet, DogPet]

class Owner(BaseModel):
    pet: Pet = Field(discriminator="kind")

# Pydantic uses the `kind` field to pick the right variant
```

**Custom types:**

```python
from typing import Annotated
from pydantic.types import StringConstraints

NonEmptyStr = Annotated[str, StringConstraints(min_length=1)]
ShortString = Annotated[str, StringConstraints(max_length=100)]
```

**Validation error handling:**

```python
from pydantic import ValidationError

try:
    ep = EpisodeWrite.model_validate(data)
except ValidationError as exc:
    for err in exc.errors():
        print(f"{err['loc']}: {err['msg']}")
```

`exc.errors()` returns structured error data; `str(exc)` gives human-readable summary.

**Serialization aliases (for JSON ↔ Python naming):**

```python
class User(BaseModel):
    user_id: int = Field(alias="userId")  # JSON has userId; Python has user_id
    
u = User.model_validate({"userId": 42})
print(u.user_id)  # 42
print(u.model_dump(by_alias=True))  # {"userId": 42}
```

## 3. Key works / libraries

- **Pydantic v2** — pydantic.dev / github.com/pydantic/pydantic.
- **pydantic-settings** — pydantic-settings docs. Env / file config.
- **pydantic-core** — github.com/pydantic/pydantic-core. Rust-based core.
- **Sereshtian, S.** — Pydantic creator; talks on Pydantic v2 internals.
- **FastAPI** — depends heavily on Pydantic; mature usage patterns.

## 4. Pitfalls and gotchas

- **v1 vs v2 confusion.** Codebases on the boundary have both. Pin v2.
- **`extra="allow"`** silently accepts unknown fields. Use `extra="forbid"` unless you have a reason.
- **`frozen=True` adds hashability** but only if all fields are hashable.
- **JSON serialization of complex types.** UUID, datetime, Decimal — use `model_dump(mode="json")` for JSON-safe types.
- **Default mutable values.** `field: list[X] = []` — Pydantic handles this correctly (creates a new list per instance), unlike vanilla dataclasses. Still, prefer `Field(default_factory=list)`.
- **Validator order.** `field_validator` runs after default conversion. `BeforeValidator` runs before; `AfterValidator` after.
- **Performance.** Pydantic v2 is much faster than v1 (Rust core), but validation cost is non-zero. Don't validate hot paths.
- **Circular references.** Forward references work but need `model_rebuild()`.
- **Models in Generics.** `Generic[T]` works with Pydantic v2 but needs care.

## 5. Applicability to Runa

For **`runa.schemas`**:

- Every boundary type is a Pydantic model.
- `model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)` as default.

For **adapter payloads**:

- Each adapter's incoming message validates via Pydantic before reaching the kernel.

For **config loading**:

- Pydantic Settings reads `~/.runa/config/runa.yaml` (with env-var override) into a typed `RunaSettings`.

For **plugin manifests**:

- Plugins declare a manifest as JSON; Pydantic validates the manifest schema.

For **stored data deserialization**:

- Loading episodes from Muninn back into Python uses Pydantic for shape validation (cheap safety net against schema drift).

For **API outputs**:

- The Bifröst gateway's HTTP responses use Pydantic for serialisation (often via FastAPI).

What to avoid:

- Don't use Pydantic for inner-loop hot data. Pure dataclasses are faster.
- Don't accept `extra="allow"` silently.
- Don't mix v1 and v2 usage in the same codebase.
- Don't put complex business logic in field_validators — they should validate, not transform.

## 6. Open questions

- **Pydantic v2 with PEP 695 generics.** Some interactions need care. Pydantic team active on this.
- **Validation cost in latency-sensitive paths.** Trade-off: skip validation = faster, riskier. Cache validated objects when possible.
- **TypedDict vs Pydantic.** TypedDict is lightweight (no runtime cost); Pydantic validates. Choose per use case.

## 7. References (curated)

- pydantic.dev — official.
- docs.pydantic.dev/latest/ — v2 docs.
- github.com/pydantic/pydantic.
- realpython.com/python-pydantic/ — practical intro.
- Companion docs: [[25-type-hints-mastery]], [[26-mypy-strict-mode]], [[28-protocol-classes]], [[45-configuration-management]].

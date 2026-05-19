# 26 — mypy Strict Mode and Gradual Typing

**Category:** Type Safety & Validation
**Runa relevance:** CI pipeline (per `pyproject.toml`), every commit
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Type hints ([[25-type-hints-mastery]]) are *just text* unless a checker validates them. **mypy** (and **pyright**) statically analyse Python code against its hints, finding mismatches before runtime. **Strict mode** enables every check by default — the toolchain refuses code that has missing annotations, dynamic typing escapes, or unsound patterns.

For Runa, `pyproject.toml` already pins `[tool.mypy] strict = true` (per the bootstrap). The discipline: type-correct code or it doesn't merge. Strict mode is the only way to actually realise the benefits of type hints; "type hints if you feel like it" produces code with hints that lie.

## 2. Technique / mechanism

**Enabling strict mode:**

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
strict = true
files = ["src/runa"]
exclude = ["tests/", "docs/", "scripts/"]
```

`strict = true` enables: `no_implicit_optional`, `warn_redundant_casts`, `warn_unused_ignores`, `warn_return_any`, `warn_unreachable`, `disallow_untyped_defs`, `disallow_incomplete_defs`, `check_untyped_defs`, `disallow_untyped_decorators`, `no_implicit_reexport`, `strict_equality`.

**The gradual approach:**

Adding strict to an existing codebase produces hundreds of errors. The gradual path:

1. **Add mypy** with relaxed config first (`strict = false`).
2. **Enable per-module:** `[[tool.mypy.overrides]] module = "runa.schemas.*" strict = true`.
3. **Migrate modules** one at a time.
4. **Promote to repo-strict** once all modules are clean.

Runa starts strict from day one — easier than migrating later.

**Common errors and how to address:**

```python
# error: Missing return type annotation
def calculate(x: int):  # add -> int
    return x * 2

# error: Function is missing a type annotation for one or more arguments  
def greet(name):  # add name: str
    return f"hi {name}"

# error: Returning Any from function declared to return "int"
def parse(s: str) -> int:
    return json.loads(s)  # cast: return int(json.loads(s))

# error: Item "None" of "Optional[X]" has no attribute "y"
def use(x: X | None):
    return x.y  # check: assert x is not None; return x.y
```

**Type narrowing:**

```python
def process(value: int | str) -> int:
    if isinstance(value, int):
        return value * 2  # mypy knows value is int here
    return len(value)  # mypy knows value is str here
```

`isinstance`, `is None` checks, `assert` statements, and TypeGuards all narrow.

**TypeGuard for custom narrowing:**

```python
from typing import TypeGuard

def is_user_dict(d: object) -> TypeGuard[dict[str, str]]:
    return isinstance(d, dict) and all(
        isinstance(k, str) and isinstance(v, str) for k, v in d.items()
    )

if is_user_dict(data):
    # mypy knows data is dict[str, str] here
    ...
```

**`# type: ignore` discipline:**

```python
# Good — specific
result = legacy_func()  # type: ignore[no-untyped-call]

# Bad — bare
result = legacy_func()  # type: ignore
```

Bare `# type: ignore` masks future errors. Be specific.

**Excluding third-party libraries:**

```toml
[[tool.mypy.overrides]]
module = ["some_untyped_library.*"]
ignore_missing_imports = true
```

**Generics:**

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T | None:
    return items[0] if items else None

result = first([1, 2, 3])  # mypy infers T = int → result: int | None
```

**Variance:**

```python
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)

class Reader(Generic[T_co]):
    def read(self) -> T_co: ...

class Writer(Generic[T_contra]):
    def write(self, item: T_contra) -> None: ...

# Reader[Cat] is a Reader[Animal] (covariant)
# Writer[Animal] is a Writer[Cat] (contravariant)
```

Use `Sequence` (covariant) instead of `list` (invariant) for read-only inputs.

**Protocol vs ABC:**

ABCs (abstract base classes) require nominal inheritance; Protocols use structural typing. Prefer Protocols for typing dependencies.

**Type-only imports:**

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from heavy_module import HeavyClass  # only imported by type checker

def fn(x: "HeavyClass") -> None:  # string annotation
    ...
```

Avoids circular imports and runtime cost of unused-at-runtime imports.

**Stubs for untyped libraries:**

`pip install types-requests` for the standard list. For custom: write a `.pyi` stub file alongside.

## 3. Key works / libraries

- **mypy** — github.com/python/mypy.
- **pyright** — github.com/microsoft/pyright.
- **PEP 484** — original type hints PEP.
- **typeshed** — github.com/python/typeshed. Community stubs for stdlib + many third-party.
- **mypy strict mode docs** — mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict.
- **PEPs 526, 544, 585, 604, 612, 646, 673, 695** — the full type-system stack.

## 4. Pitfalls and gotchas

- **`# type: ignore` cancer.** A repo full of bare ignores defeats the purpose.
- **`Any` as escape hatch.** Easy to write `x: Any`; defeats checking.
- **Mypy version pinning.** Mypy updates can introduce new errors. Pin version in CI; bump deliberately.
- **Generic variance confusion.** `list[X]` is invariant; `Sequence[X]` is covariant. Easy bug.
- **`__init__` annotations.** Annotate `self` parameters' fields; `__init__` itself returns None implicitly but explicit `-> None` is conventional.
- **Pydantic + mypy.** Pydantic ships a mypy plugin to handle its dynamic features; enable it.
- **Slow incremental checks** can frustrate dev loop. Mypy daemon (`dmypy`) speeds repeated runs.

## 5. Applicability to Runa

For **CI**:

- `pyproject.toml` has `[tool.mypy] strict = true` per the bootstrap. CI runs `mypy src/runa`. Failures block merge.

For **`runa.schemas` specifically**:

- Pydantic models. Enable Pydantic mypy plugin.
- All boundary types fully typed.

For **gradual exceptions**:

- `tests/` excluded from strict (per pyproject.toml). Tests can be more flexible.
- New third-party deps without stubs go through `ignore_missing_imports`.

For **type-only imports**:

- Heavy ML libraries (transformers, torch) often have slow imports. Use `TYPE_CHECKING` blocks.

For **PEP 695 syntax**:

- Adopt when 3.12 is the minimum. Currently 3.11 minimum; use older syntax (`TypeVar`).

What to avoid:

- Don't write bare `# type: ignore`.
- Don't use `Any`.
- Don't disable strict for new code.
- Don't merge code with mypy errors.

## 6. Open questions

- **Pyright migration.** Pyright is faster and stricter than mypy. Many projects are migrating; trade-offs exist (mypy is more established; pyright catches more).
- **Runtime type checking.** Pydantic at boundaries; beartype for additional runtime safety. Cost vs benefit.
- **Mypy strict mode for tests.** Some teams enable; others don't. Subjective.

## 7. References (curated)

- mypy.readthedocs.io.
- github.com/microsoft/pyright.
- github.com/python/typeshed.
- PEP 484, 526.
- Companion docs: [[25-type-hints-mastery]], [[27-pydantic-runtime-validation]], [[28-protocol-classes]].

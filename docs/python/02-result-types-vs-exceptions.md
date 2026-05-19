# 02 — Result Types vs Exceptions: When to Use Which

**Category:** Robustness Fundamentals
**Runa relevance:** skill contract return types, adapter responses, tool-call results
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

In Python, the default way to communicate failure is to raise an exception. In Rust, OCaml, Haskell, and increasingly in Go and Swift, the default is to *return* a value that wraps "success or failure" in the type system — `Result<T, E>`, `Either<L, R>`, `Maybe<T>`. The two approaches are not equivalent; they have different ergonomic, performance, and correctness properties.

Python *can* do both. Exceptions are cleaner for genuinely-exceptional conditions; result types are cleaner for *expected* failures that callers will always need to handle. Knowing when to use which is a craft skill that distinguishes robust Python from brittle Python.

## 2. Technique / mechanism

**The Result-style type in Python:**

```python
from typing import Generic, TypeVar
from dataclasses import dataclass

T = TypeVar("T")
E = TypeVar("E")

@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    value: T

@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    error: E

Result = Ok[T] | Err[E]  # PEP 604 union syntax (Python 3.10+)

def parse_int(s: str) -> Result[int, str]:
    try:
        return Ok(int(s))
    except ValueError:
        return Err(f"not an integer: {s!r}")

# Caller:
result = parse_int(user_input)
match result:
    case Ok(value=n):
        print(f"got {n}")
    case Err(error=msg):
        print(f"failed: {msg}")
```

**Libraries that ship this pattern:**

- **`returns`** (github.com/dry-python/returns). Provides `Result`, `Maybe`, `IO`, plus do-notation-style helpers. Mature; opinionated.
- **`expression`** (github.com/dbrattli/Expression). F#-inspired functional library with `Result` and computational expressions.
- **`option-and-result`** (github.com/MaT1g3R/option). Minimal `Option` and `Result` types.

Rolling your own (as above) is also reasonable for a project that wants tight control.

**When exceptions are right:**

- *Truly exceptional* conditions: file not found when you expected one, network unreachable, programming bug.
- Conditions that *most callers will ignore*: a checksum mismatch when you fundamentally need a correct file; let it propagate.
- Stack-unwinding semantics matter: cleanup via `try/finally`, context managers.
- Performance-critical hot paths where the *common case* is success: exception machinery is cheap when not triggered.
- Cross-layer error propagation through many levels where each layer adds context.

**When Result types are right:**

- *Expected* failure modes the caller *will always* check: `parse_int`, `look_up_by_id`, `validate_input`.
- API boundaries where the failure shape is part of the contract.
- Code that needs to be *total* (every input produces a defined output).
- Pipeline-style code where errors should short-circuit a chain of operations cleanly (`result.bind(step1).bind(step2)...`).
- Code interfacing with statically-typed languages (Rust, Go) where Result-style is the convention.

**A pragmatic middle ground:**

Many Python codebases use exceptions for *infrastructure failure* (network, disk, system errors) and Result-style returns for *domain validation* (parsing, validation, lookup). The split corresponds to "the caller doesn't expect to handle this here" (exception) vs "the caller absolutely needs to know if this worked" (Result).

**Performance:**

- Exception machinery in CPython: cheap when not raised (try-block overhead is near-zero); expensive when raised (the unwind, traceback construction, locals capture).
- Result return: cheap always; one allocation per return.
- For hot loops with frequent failures, Result wins on performance. For typical workloads, exceptions win on ergonomic cleanness.

## 3. Key works / libraries

- **Rust's `std::result::Result`** — the modern reference design.
- **Haskell's `Either`, `Maybe`** — the functional foundation.
- **PEP 634-636 (Structural Pattern Matching, Python 3.10)** — makes Result types ergonomic via `match`.
- **`returns` library** — github.com/dry-python/returns. The most-featured Python implementation.
- **`expression` library** — github.com/dbrattli/Expression.
- **Hettinger's PyCon talks** on type design occasionally cover this.

## 4. Pitfalls and gotchas

- **Mixing both styles inconsistently** is worse than picking one. If `Service.do_thing` returns `Result`, all its peers should too — otherwise callers play "guess the error model."
- **Result-pollution.** If a deep function returns `Result`, every caller up the stack must handle it. The "wrap propagation" can spread. Some codebases regret it.
- **Pattern-matching exhaustiveness isn't enforced.** Python's `match` doesn't statically check that you covered `Ok` and `Err`. Tools like `pyright --strict` help; mypy is weaker here.
- **The `returns` library's "do-notation" via generators** is clever but opaque to readers unfamiliar with it. Use with care.
- **`Option`/`Maybe` vs `Result[T, None]`** — both work; `Optional[T]` (i.e. `T | None`) is the more-Pythonic form for "value or absent" if no error explanation is needed.
- **Serialising Result** for IPC: the `match` syntax doesn't survive pickling losslessly without explicit support.

## 5. Applicability to Runa

For **`runa.skills` contract**:

- Skill `invoke` returns `SkillResult` — a typed success/failure structure. This is Result-style.
- `SkillResult.success(value)` vs `SkillResult.failed(reason, retryable=…, cause=…)`. The caller (kernel) pattern-matches.
- Internal skill errors that don't map to a useful caller-action stay as exceptions caught at the skill boundary and wrapped into `failed(...)`.

For **`runa.adapters.<provider>.complete()`** (model-provider adapters):

- Returns `Response` on success; raises `ModelProviderError` on infrastructure failure (timeout, 5xx, auth).
- Distinction: infrastructure errors are exceptions (Heimskringla's retry policy handles them); model-content issues (refusals, malformed JSON) might be Result-typed.

For **`runa.runtime.commands`**:

- CLI command results return a typed `CommandResult` rather than raising (so the CLI layer can render appropriately). Internal infrastructure failures still raise; the runtime layer wraps them.

For **`runa.core.memory` (Muninn) reads**:

- `MuninnReader.get_episode(id)` returns `Episode | None` rather than raising on not-found. The common case is "exists or doesn't."
- `MuninnReader.search(query)` returns a list — empty if nothing matched, not exception.
- Genuine infrastructure errors (corrupt store, disk full) raise `StateError`.

What to avoid:

- Don't use exceptions for control flow. `try: x = d[k] / except KeyError: x = default` is fine; `for ... try: ... except StopIteration: break` is fine; gratuitous use is not.
- Don't return `None` for both "not found" and "error." Use `Result` or distinct sentinels.
- Don't make `Result` types where exceptions would do. Library code uses exceptions for infrastructure failures because that's the Python convention.
- Don't reinvent `returns` unless you need very narrow control. The library is well-maintained.

## 6. Open questions

- **Static exhaustiveness checking** is the missing piece. pyright is the strongest as of 2025; mypy improving.
- **Async + Result composition.** Awaiting a coroutine that returns `Result` is clean; chaining many is verbose. `expression`'s computational expressions help; not universally adopted.
- **Performance in the JIT future.** If Python eventually gets a serious JIT (3.13+ free-threaded, Cython, PyPy), the relative cost of exceptions vs Result changes.

## 7. References (curated)

- doc.rust-lang.org/std/result/ — Rust's Result; the reference.
- github.com/dry-python/returns — `returns` library.
- github.com/dbrattli/Expression — `expression` library.
- PEP 634 — Structural Pattern Matching.
- realpython.com/python-with-statement/ — context managers, the exception-handling complement.
- Hettinger's PyCon talks on API design.
- Companion docs: [[01-exception-design]], [[28-protocol-classes]] (typing the contracts).

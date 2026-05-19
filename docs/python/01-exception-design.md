# 01 — Exception Design and Error Hierarchies in Python

**Category:** Robustness Fundamentals
**Runa relevance:** `runa.schemas.errors` (the canonical error hierarchy), every subpackage that raises
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Exceptions are not just a way to abort — they are a *typed channel* for communicating failure. A well-designed exception hierarchy lets callers handle specific failure modes precisely, lets the standard library and your own code compose cleanly, and lets logging / observability systems group related errors meaningfully. A poorly designed exception story produces code where every call site does `try: ... except Exception:` and the agent can never distinguish "the network is down" from "the user typed something invalid" from "we have a real bug."

For Runa, the exception hierarchy lives in `runa.schemas.errors`. It is the *only* place exception classes that cross subpackage boundaries are defined. Subpackage-internal errors stay internal. The discipline is small; the payoff is dramatic — every error has a *type* that says what kind of problem it is, every catch site says what kinds of problems it can handle.

## 2. Technique / mechanism

**The canonical hierarchy shape:**

```python
# runa/schemas/errors.py

class RunaError(Exception):
    """Base of all Runa-specific exceptions."""

# Domain categories
class ConfigError(RunaError):
    """Configuration is wrong or missing."""

class StateError(RunaError):
    """On-disk state is corrupt or inconsistent."""

class PolicyError(RunaError):
    """A policy check refused the action."""

class IntegrationError(RunaError):
    """A dependency failed (network, model provider, tool)."""
    def __init__(self, message: str, *, retryable: bool = False, cause: Exception | None = None):
        super().__init__(message)
        self.retryable = retryable
        self.__cause__ = cause

class ModelProviderError(IntegrationError):
    """A specific model-provider call failed."""

class AdapterError(IntegrationError):
    """A specific adapter (Discord, Telegram, etc.) failed."""

class SkillError(RunaError):
    """A skill failed during execution."""

class ValidationError(RunaError):
    """User-supplied data didn't validate."""
```

**Rules of thumb:**

1. **One root class** per project. Catching `RunaError` distinguishes "our errors" from "Python's errors and library errors." This is the firewall.
2. **Categorise by domain, not by component.** `IntegrationError` is more useful than `MunninError` — many components have integration errors; few have unique enough errors to warrant their own subclass.
3. **Subclass for handling, not for naming.** A new subclass is justified when callers will catch *that* class but not its siblings. Otherwise just use the parent with a clear message.
4. **Carry structured data.** Exception classes can have fields beyond the message: `retryable`, `cause`, `context`, `error_code`. Use them.
5. **Preserve causation** with `raise NewError() from original`. The `__cause__` chain is essential for debugging.
6. **Exceptions are part of the API.** Document what each function raises, in docstrings. Type checkers don't enforce this; tests can.

**The `raise X from Y` pattern:**

```python
try:
    response = httpx.get(provider_url, timeout=5.0)
    response.raise_for_status()
except httpx.HTTPError as e:
    raise ModelProviderError(
        f"Provider {provider} returned {e.response.status_code}",
        retryable=e.response.status_code in {429, 500, 502, 503, 504},
        cause=e,
    ) from e
```

The `from e` clause sets `__cause__` so the traceback shows both layers. **Without it**, the inner traceback may show as `__context__` which suggests "this happened during handling of …" — a different semantic.

**Exception groups (PEP 654, Python 3.11+):**

```python
async with asyncio.TaskGroup() as tg:
    tg.create_task(work_a())
    tg.create_task(work_b())
# If both raise, you get ExceptionGroup wrapping both.

try:
    async with asyncio.TaskGroup() as tg:
        ...
except* ModelProviderError as eg:
    # Handle all ModelProviderErrors in the group
    for exc in eg.exceptions:
        log_provider_error(exc)
except* PolicyError as eg:
    # Handle all PolicyErrors in the group
    ...
```

The `except*` syntax is structured-concurrency-friendly. It matches against types and handles them in *groups* rather than serially.

**Sentinel exceptions vs flag arguments:**

Anti-pattern:
```python
def fetch(url, allow_404=True): ...  # complicated calling
```

Better:
```python
class NotFound(IntegrationError): ...

def fetch(url):
    if response.status_code == 404:
        raise NotFound(url)
    ...

# Caller chooses how to handle:
try:
    data = fetch(url)
except NotFound:
    data = default_value
```

Exceptions communicate "this is a recognised failure mode" cleanly.

## 3. Key works / libraries

- **PEP 3134** — Exception chaining and embedded tracebacks. The `raise X from Y` syntax.
- **PEP 654** — Exception Groups and except*. Python 3.11+.
- **PEP 678** — Enriching exceptions with notes (`exc.add_note("...")`). Python 3.11+.
- **Standard library exception hierarchy** — docs.python.org/3/library/exceptions.html. Read it; understand the structure (`BaseException → Exception → …`).
- **tenacity** — github.com/jd/tenacity. Library that operates on exception types for retry policies.
- **structlog** — pairs well with structured error metadata.

## 4. Pitfalls and gotchas

- **Catching `Exception`** instead of specific types swallows bugs. Reserve broad catches for *boundaries* (top of a worker loop, an HTTP handler) and always log with traceback.
- **Catching `BaseException`** catches `KeyboardInterrupt` and `SystemExit`. Almost never what you want; reserved for very specific cleanup code.
- **Re-raising without `from`** loses the cause. Use `from e` or `from None` (the latter when you deliberately want to hide the inner exception).
- **`assert` statements are removed under `python -O`.** Don't use `assert` for runtime validation. Use it for invariants checked in tests and development.
- **Defining exceptions inside functions** makes them un-importable. Define at module level.
- **Mutating exception state** after raise: don't. Treat exceptions as immutable.
- **Confusing `__cause__` and `__context__`.** `from X` sets cause (intentional chain). Catching-during-another-exception sets context (implicit chain). Different in tracebacks.
- **Exception swallowing inside async tasks** without TaskGroup: a fire-and-forget `asyncio.create_task(work())` that raises is silently logged once and lost. TaskGroup or explicit await.

## 5. Applicability to Runa

For **`runa.schemas.errors`** (declared in DOMAIN_MAP §1, INTERFACE.md):

- The hierarchy above is the starting point. Refine as actual code reveals new failure-categorisation needs.
- Every error raised across a subpackage boundary inherits from `RunaError`.
- Subpackage-internal errors can be plain `ValueError` / `RuntimeError` / etc. — only escapes to other subpackages must be `RunaError`-derived.

For **Heimskringla** (adapter calls):

- `ModelProviderError` with `retryable` field drives the retry policy in `runa.adapters.<provider>`. See [[06-retry-strategies]].
- The audit log records full causal chains via `__cause__`.

For **policy enforcement**:

- `PolicyError` raised by the policy engine is caught at the kernel boundary. The user sees "I declined to do that because [reason]"; the audit log records principle + reason.

For **kernel turns**:

- Per-turn TaskGroup with `except*` handlers for `IntegrationError`, `PolicyError`, etc. Each category gets handled distinctly.
- Unhandled `RunaError` becomes a `Replied` of "something went wrong, I logged it"; the trace stays in the audit log.
- Unhandled non-`RunaError` (a real bug) crashes the kernel; supervisor restarts.

For **plugin / skill boundaries**:

- Plugin or skill code can raise anything. The loader wraps everything outside `RunaError` into `SkillError(cause=original)`. Inside the loader.

What to avoid:

- Don't define one exception class per error message. Group by what callers do.
- Don't use exception messages for machine parsing. Use exception *fields*.
- Don't catch-and-ignore. If you must swallow, log with traceback.
- Don't raise generic `Exception("something failed")`. Use a real subclass.

## 6. Open questions

- **Sentinel return values vs exceptions.** [[02-result-types]] explores `Result[T, E]`-style alternatives. The trade-off is real; Python's exceptions are the default but not universally best.
- **Exception design for libraries vs applications.** Library exceptions should be narrow + parametric. Application exceptions can be richer. The Runa hierarchy is application-grade.
- **Tracing across processes.** When errors cross process boundaries (multiprocessing worker raises, parent receives), the traceback fidelity degrades. `tblib` library helps.

## 7. References (curated)

- PEP 3134 — Exception chaining.
- PEP 654 — Exception Groups.
- PEP 678 — Exception notes.
- docs.python.org/3/library/exceptions.html — stdlib hierarchy.
- realpython.com/python-exceptions/ — practical introduction.
- github.com/python/cpython/blob/main/Lib/exceptions.py — the standard hierarchy source.
- github.com/jd/tenacity — exception-based retry.
- Companion docs: [[02-result-types]], [[06-retry-strategies]], [[40-audit-logging-replay]] (research corpus, audit-of-errors).

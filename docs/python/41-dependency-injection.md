# 41 — Dependency Injection Without Frameworks

**Category:** Architecture Patterns
**Runa relevance:** kernel construction, every subpackage's dependencies, testability
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

**Dependency injection** (DI) is the principle: don't hard-code dependencies; pass them in. A class that *creates* its dependencies is tightly coupled to specific implementations and hard to test. A class that *receives* its dependencies via constructor or function arguments is loosely coupled and trivially testable (pass in a stub).

In Java / C#, DI usually means *DI frameworks* — heavy machinery with annotations and runtime container magic. In Python, plain function/constructor parameters are usually sufficient. Frameworks like `dependency-injector` or `wired` exist but are mostly overkill. The Python way is "constructor injection by convention."

For Runa, DI is how `runa.core` stays testable. Every subsystem accepts its dependencies (typed as Protocols, [[28-protocol-classes]]); tests inject stubs; production injects real implementations.

## 2. Technique / mechanism

**Constructor injection (the default):**

```python
class Kernel:
    def __init__(
        self,
        muninn: MuninnWriter,
        skuld: SkuldLedger,
        heimskringla: Heimskringla,
        eldhugi: EldhugiJournal,
        policy: PolicyEngine,
    ):
        self.muninn = muninn
        self.skuld = skuld
        self.heimskringla = heimskringla
        self.eldhugi = eldhugi
        self.policy = policy
```

The Kernel accepts everything. The wiring code at startup creates the real instances and passes them. Tests pass stubs.

**Composition root pattern:**

A single place — the "composition root" — wires everything:

```python
def build_kernel(config: RunaConfig) -> Kernel:
    """The one place that knows about real implementations."""
    muninn = Muninn(home=config.home / "muninn")
    skuld = Skuld(home=config.home / "skuld")
    heimskringla = Heimskringla(providers={
        "ollama": OllamaProvider(config.ollama),
        "anthropic": AnthropicProvider(config.anthropic),
    })
    eldhugi = Eldhugi(home=config.home / "eldhugi")
    policy = PolicyEngine.from_config(config.policy)
    
    return Kernel(
        muninn=muninn,
        skuld=skuld,
        heimskringla=heimskringla,
        eldhugi=eldhugi,
        policy=policy,
    )
```

Inside any subsystem, dependencies are received, not created. Only the composition root creates.

**Protocol-typed dependencies:**

```python
class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...

class Muninn:
    def __init__(self, embedder: Embedder, ...):
        self.embedder = embedder
```

Now `Muninn` doesn't care if it gets a real BGE embedder or a `StubEmbedder` in tests — anything satisfying the Protocol works.

**Factory functions / partial application:**

```python
from functools import partial

# Configured-but-deferred construction
make_provider = partial(OllamaProvider, host="http://localhost:11434")
provider = make_provider(model="llama3.1:8b")
```

Or with classes:
```python
class ProviderFactory:
    def __init__(self, default_host: str):
        self.host = default_host
    
    def for_model(self, model_name: str) -> Provider:
        return Provider(host=self.host, model=model_name)
```

**Service locator anti-pattern:**

```python
# AVOID
class Kernel:
    def __init__(self):
        self.muninn = ServiceLocator.get(Muninn)  # implicit dependency
```

A `ServiceLocator` is global mutable state. Hard to test (must set up the locator); hides dependencies (the constructor doesn't show what's needed).

**Optional dependencies:**

```python
class Kernel:
    def __init__(
        self,
        muninn: MuninnWriter,
        # Optional with sensible default
        clock: ClockProtocol = SystemClock(),
    ):
        ...
```

For "almost always the same" dependencies, defaults are fine. The injection point is still there for tests.

**Async construction:**

```python
async def build_kernel(config: RunaConfig) -> Kernel:
    """Some dependencies need async setup."""
    muninn = await Muninn.create(home=config.home / "muninn")  # opens DB, runs migrations
    ...
```

`@classmethod async def create(cls, ...)` is the convention.

**DI containers (heavier, usually unnecessary):**

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    muninn = providers.Singleton(Muninn, home=config.home_muninn)
    heimskringla = providers.Singleton(Heimskringla, ...)

container = Container()
container.config.from_yaml("config.yaml")
kernel = container.kernel()
```

Useful when DI graph is large; overkill for Runa-scale.

## 3. Key works / libraries

- **Fowler, M.** "Inversion of Control Containers and the Dependency Injection pattern." 2004. The classic article.
- **Spring Framework** (Java) — productionised DI containers.
- **`dependency-injector`** — github.com/ets-labs/python-dependency-injector. Most-popular Python container.
- **`wired`** — github.com/mmerickel/wired. Lighter alternative.
- **`injector`** — github.com/python-injector/injector.
- **FastAPI's `Depends`** — DI for HTTP handlers; very ergonomic.
- **Hettinger's** PyCon talks on Python design.

## 4. Pitfalls and gotchas

- **Service locator.** Hides dependencies. Avoid.
- **Global mutable state.** A module-level singleton is hard to test. Pass as parameter.
- **Circular dependencies** — A needs B; B needs A. Usually indicates design problem; fix with extract-interface or restructure.
- **DI container magic** — at-runtime instance resolution is hard to debug. Plain Python is more transparent.
- **Lifetime confusion** — singleton vs per-request vs per-call. Document.
- **Optional parameter defaults that are mutable** — common Python bug ([[03-defensive-programming-design-by-contract]]).

## 5. Applicability to Runa

For **`runa.core` subsystems**:

- All dependencies via constructor.
- All dependencies typed as Protocols.

For **the composition root**:

- `runa.runtime.build_kernel(config)` is the composition root. The only function that creates real implementations.

For **tests**:

- Test fixtures provide stub/fake implementations.
- No need for DI containers — plain pytest fixtures suffice.

For **Hirð retainers**:

- Each retainer accepts its tool surface, model handle, memory accessor — all as constructor parameters.

For **adapters**:

- Each adapter accepts its config, transport client, gateway handle.

For **Heimskringla provider plugins**:

- Each provider adapter accepts its credentials, retry policy, breaker.

What to avoid:

- Don't use a DI framework for Runa-scale code.
- Don't create dependencies inside constructors.
- Don't rely on module-level globals.
- Don't make dependencies implicit (read from `os.environ` deep in a function).

## 6. Open questions

- **Async factories.** No universal pattern; `async classmethod create` is the common one.
- **Configuration as dependency** — pass `config` everywhere, or pass specific values? Trade-off between coupling and bookkeeping.

## 7. References (curated)

- martinfowler.com/articles/injection.html.
- github.com/ets-labs/python-dependency-injector.
- fastapi.tiangolo.com/tutorial/dependencies/.
- Companion docs: [[28-protocol-classes]], [[42-hexagonal-architecture]], [[35-test-doubles]].

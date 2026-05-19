# 35 — Test Doubles: Mocks, Stubs, Fakes, Spies

**Category:** Testing
**Runa relevance:** every integration test, every unit test with dependencies
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

When testing code with dependencies — a function that calls a model provider, a class that writes to a database — you need substitutes for those dependencies. The substitutes have different names depending on what they do. Gerard Meszaros's *xUnit Test Patterns* canonised the vocabulary: **dummy** (placeholder), **stub** (returns canned data), **fake** (working but lightweight implementation), **mock** (verifies it was called correctly), **spy** (records what happened).

For Runa, knowing which kind to use when keeps tests clean and informative. Mocks make tests brittle when overused; fakes are heavier but more realistic. The vocabulary helps pick the right tool.

## 2. Technique / mechanism

**The five test doubles (Meszaros):**

### Dummy

Placeholder; not actually used. Pass `None` or a sentinel when a parameter is required but irrelevant.

```python
def test_validation_doesnt_care_about_logger():
    validate_input(data, logger=None)  # dummy
```

### Stub

Returns canned responses. Used to put the system under test in a particular state.

```python
class StubProvider:
    def complete(self, request):
        return Response(text="canned reply")

def test_kernel_renders_response():
    kernel = Kernel(provider=StubProvider())
    result = kernel.handle("hi")
    assert "canned reply" in result.text
```

### Fake

A simplified-but-working implementation. Different from a stub: a fake *actually does the thing*, just lighter.

```python
class InMemoryMuninn:
    """Fake Muninn: keeps episodes in a Python list. Works for testing."""
    def __init__(self):
        self._episodes = []
    
    def write_episode(self, ep):
        self._episodes.append(ep)
    
    def search(self, query, k=5):
        # Trivial search; real Muninn uses sqlite-vss
        return [e for e in self._episodes if query.lower() in e.text.lower()][:k]
```

Fakes are heavier than stubs but give more realistic test behaviour.

### Mock

Verifies it was called correctly. The test fails if expected calls don't happen (or unexpected ones do).

```python
from unittest.mock import MagicMock

def test_kernel_calls_provider_with_right_args():
    provider = MagicMock()
    provider.complete.return_value = Response(text="reply")
    
    kernel = Kernel(provider=provider)
    kernel.handle("hello")
    
    provider.complete.assert_called_once()
    call_args = provider.complete.call_args
    assert call_args.kwargs["request"].prompt == "hello"
```

`unittest.mock.MagicMock` is the canonical Python mock. Verifies behaviour, not just outputs.

### Spy

Records calls but otherwise delegates to a real implementation. Useful for "I want the real behaviour but also want to assert that something specific happened."

```python
from unittest.mock import MagicMock, wraps

real_provider = RealProvider()
provider = MagicMock(wraps=real_provider)

kernel = Kernel(provider=provider)
kernel.handle("hello")

# Real provider was used (behaviour); mock records the call
provider.complete.assert_called_once()
```

**`pytest-mock` — the pytest-friendly API:**

```python
def test_with_mock(mocker):
    mock_provider = mocker.MagicMock()
    mock_provider.complete.return_value = Response(text="hi")
    mocker.patch("runa.core.kernel._global_provider", mock_provider)
    
    # test
    ...
```

`mocker` fixture (from `pytest-mock`) auto-cleans up patches at test end.

**Patching:**

```python
def test_calls_external(mocker):
    mocker.patch("runa.adapters.discord.send_message")  # replaces the function
    # call code that internally calls send_message
    runa.adapters.discord.send_message.assert_called_once()
```

Patch the *use site*, not the definition site:

```python
# WRONG — patches the definition site; users of the import keep the original
mocker.patch("third_party.lib.func")

# RIGHT — patches the use site
mocker.patch("runa.code_that_uses_func.func")
```

**Async mocks:**

```python
mock = mocker.AsyncMock()
mock.return_value = "result"

result = await mock(args)
```

`AsyncMock` (Python 3.8+) for mocking awaitable functions.

**When to use which:**

| Need | Use |
|---|---|
| Doesn't matter; just needs a value | Dummy |
| Controlled return data, no behaviour assertion | Stub |
| Real-ish behaviour, light-weight | Fake |
| Assert specific calls happened | Mock |
| Real behaviour + observation | Spy |

**Protocol-based test doubles (recommended):**

Define dependencies as Protocols ([[28-protocol-classes]]); tests provide structural implementations:

```python
class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...

# Test double
class StubEmbedder:
    def embed(self, text: str) -> list[float]:
        return [0.0] * 384

def test_uses_embedder():
    kernel = Kernel(embedder=StubEmbedder())
    ...
```

Cleaner than MagicMock; type-checked.

## 3. Key works / libraries

- **Meszaros, G.** *xUnit Test Patterns*, Addison-Wesley 2007. The canonical vocabulary.
- **Fowler, M.** "Mocks Aren't Stubs." martinfowler.com/articles/mocksArentStubs.html. Classic article.
- **`unittest.mock`** — stdlib mocking library.
- **`pytest-mock`** — github.com/pytest-dev/pytest-mock.
- **`responses`** — github.com/getsentry/responses. HTTP mocking.
- **`vcrpy`** — github.com/kevin1024/vcrpy. Record/replay HTTP cassettes.

## 4. Pitfalls and gotchas

- **Mocking too much.** Tests assert calls instead of behaviour; tests become brittle when implementation changes.
- **Patching the wrong place.** Patch use site, not definition site.
- **Forgetting `AsyncMock` for async.** Plain MagicMock with async code → coroutines that never await.
- **Mocking what you don't own** (e.g., requests library). Better: define your own thin wrapper; mock the wrapper.
- **Over-realistic fakes** become as complex as the real thing. Keep fakes lightweight.
- **Test double drift.** Real service changes; fake/mock doesn't match anymore. Periodically validate stubs against real.
- **`autospec=True`** — makes mocks enforce the spec'd signature. Recommended; catches drift.

## 5. Applicability to Runa

For **stubs** in tests/fixtures/:

- `StubHeimskringla`, `StubProvider`, `StubAdapter`.
- Canned responses for known prompts.

For **fakes**:

- `InMemoryMuninn`, `InMemorySkuld`, `InMemoryEldhugi`. Real shape, simpler backend.
- Used in unit tests where real SQLite would be overkill.

For **mocks**:

- Targeted use to verify specific interactions. E.g., "the policy engine was consulted before the destructive action."

For **spies**:

- Useful when verifying that a real flow happened correctly (e.g., real Muninn write, but also assert log message emitted).

For **protocol-based**:

- Most dependencies are Protocols. Test doubles are simple classes satisfying the Protocol; no MagicMock magic.

What to avoid:

- Don't mock everything. Many tests benefit from real internal behaviour.
- Don't assert on every method call. Test outcomes, not internal mechanics.
- Don't mock what you don't own without a wrapper.
- Don't forget AsyncMock for async dependencies.

## 6. Open questions

- **Contract tests** — ensuring stubs/fakes match real services. Pact-style.
- **Recording cassettes** (vcrpy) — easier than maintaining stubs by hand, but record-once-replay-forever can hide drift.
- **Property-based test doubles** — generate test inputs that cover many cases, then stub responses for each.

## 7. References (curated)

- Meszaros, *xUnit Test Patterns*, 2007.
- martinfowler.com/articles/mocksArentStubs.html.
- docs.python.org/3/library/unittest.mock.html.
- github.com/pytest-dev/pytest-mock.
- Companion docs: [[28-protocol-classes]], [[30-pytest-mastery]], [[34-integration-e2e-testing]].

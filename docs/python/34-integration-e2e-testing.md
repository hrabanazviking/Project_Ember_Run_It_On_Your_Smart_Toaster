# 34 — Integration and E2E Testing Patterns

**Category:** Testing
**Runa relevance:** tests/integration/, tests/e2e/
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

Unit tests check individual functions. **Integration tests** check that multiple components work together — the kernel + Muninn writes + Skuld queueing in a single flow. **End-to-end (e2e) tests** check the system *as the user experiences it* — the `runa shell` command from typed input to printed reply. The three tiers serve different purposes; together they catch what each alone misses.

For Runa, the tests/ structure (unit / integration / e2e / fixtures / snapshots) reflects this. Integration tests use stubs for external services but real internal wiring. E2e tests use the real CLI/gateway and (optionally) real local models. The discipline: each tier has clear scope, clear gating, clear runtime profile.

## 2. Technique / mechanism

**Integration test patterns:**

```python
@pytest.fixture
def integrated_kernel(tmp_path, monkeypatch):
    """Real kernel + real Muninn + real Skuld + stub Heimskringla."""
    monkeypatch.setenv("RUNA_HOME", str(tmp_path / ".runa"))
    
    # Stub the model provider
    stub = StubHeimskringla(canned_responses=[...])
    
    kernel = Kernel(
        muninn=Muninn(home=tmp_path / "muninn"),
        skuld=Skuld(home=tmp_path / "skuld"),
        heimskringla=stub,
    )
    yield kernel
    kernel.shutdown()

def test_full_turn_writes_episode_and_replies(integrated_kernel):
    heard = Heard(text="hello", conversation_id=uuid4())
    replied = integrated_kernel.handle(heard)
    assert replied.text
    # Episode written to Muninn?
    assert integrated_kernel.muninn.count_episodes() == 2  # input + reply
```

**Integration test scope:**

- Real internal modules.
- Stubbed external dependencies (cloud APIs, model providers, chat platforms).
- Real local storage (SQLite in `tmp_path`).
- Optional: real local Ollama (mark `@pytest.mark.requires_ollama`).

**E2E test patterns:**

```python
@pytest.mark.e2e
def test_runa_shell_responds(tmp_path):
    """Full subprocess test."""
    proc = subprocess.Popen(
        ["runa", "shell", "--config", str(tmp_path / "test_config.yaml")],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    proc.stdin.write("hello\n")
    proc.stdin.write("exit\n")
    out, err = proc.communicate(timeout=30)
    assert "Runa:" in out
```

**E2E via real HTTP gateway:**

```python
@pytest.mark.e2e
def test_gateway_responds():
    with run_gateway_subprocess() as base_url:
        response = httpx.post(f"{base_url}/v1/chat", json={"text": "hello"})
        assert response.status_code == 200
        assert response.json()["reply"]
```

**Test fixtures and stubs:**

```python
class StubHeimskringla:
    """In-memory stand-in for Heimskringla."""
    
    def __init__(self, canned_responses: list[str]):
        self.canned = iter(canned_responses)
        self.calls = []
    
    async def complete(self, request) -> Response:
        self.calls.append(request)
        return Response(text=next(self.canned))
```

Stubs (or fakes) live in `tests/fixtures/` and are shared via conftest.

**Markers and gating:**

```toml
[tool.pytest.ini_options]
markers = [
    "slow: slow tests",
    "e2e: end-to-end tests",
    "requires_ollama: needs Ollama",
]
```

```bash
pytest                                  # default; excludes e2e
pytest -m e2e                            # only e2e
pytest -m "not requires_ollama"          # skip Ollama-dependent
```

**Network blocking in tests:**

```python
# conftest.py
import pytest

@pytest.fixture(autouse=True)
def no_external_network(monkeypatch):
    """Prevent accidental external network calls."""
    def deny(*args, **kwargs):
        raise RuntimeError("external network blocked in tests")
    
    monkeypatch.setattr("socket.socket.connect", deny)
```

Catches tests that accidentally try to call out.

**Parametrize over environments:**

```python
@pytest.mark.parametrize("provider", ["ollama_stub", "openai_stub", "claude_stub"])
def test_kernel_works_across_providers(integrated_kernel, provider):
    integrated_kernel.heimskringla.set_default(provider)
    ...
```

Same test runs against multiple stubs.

**Test data builders:**

```python
class EpisodeBuilder:
    """Fluent builder for test episodes."""
    
    def __init__(self):
        self._data = {
            "episode_id": uuid4(),
            "text": "default text",
            "timestamp": utcnow(),
            "speaker": "user",
        }
    
    def with_text(self, text): self._data["text"] = text; return self
    def with_speaker(self, s): self._data["speaker"] = s; return self
    
    def build(self) -> Episode:
        return Episode(**self._data)

ep = EpisodeBuilder().with_text("hi").build()
```

## 3. Key works / libraries

- **Beck, K.** *Test-Driven Development by Example*, Addison-Wesley 2002.
- **Cohn, M.** *Succeeding with Agile* — test pyramid (unit / integration / e2e).
- **Meszaros, G.** *xUnit Test Patterns*, Addison-Wesley 2007. The catalog.
- **`pytest`** — covered in [[30-pytest-mastery]].
- **`testcontainers`** — github.com/testcontainers/testcontainers-python. Spin up real services (databases, message queues) for integration tests.
- **`responses`, `httpretty`** — HTTP stubbing libraries.

## 4. Pitfalls and gotchas

- **Slow tests in dev loop.** Tier and gate. E2e shouldn't run on every commit locally.
- **Flaky tests from timing.** Don't `time.sleep` to wait for async work; use `wait_for_condition` polls.
- **External-service dependency in CI.** Cloud API rate limits, key management. Stub.
- **Test data pollution.** Tests sharing state pollute each other. Use `tmp_path`; per-test cleanup.
- **Subprocess tests on Windows.** Different signal handling, different path semantics. Test cross-platform.
- **Async tests in subprocess** sometimes deadlock.
- **Tests with implicit ordering.** Don't assume test execution order. Pytest can randomise (`pytest-randomly`).

## 5. Applicability to Runa

For **tests/integration/**:

- Stub Heimskringla, real Muninn/Skuld/Eldhugi.
- Test the kernel-turn pipeline end-to-end internally.
- ~50-200 integration tests, each <1s.

For **tests/e2e/**:

- Subprocess-based `runa shell` tests.
- Real local Ollama where available; skip otherwise.
- 10-30 e2e tests, each can take several seconds.
- Run nightly in CI, not on every commit.

For **tests/fixtures/**:

- StubHeimskringla, StubProvider, FakeMuninn (in-memory variant).
- Sample episodes, conversations, model responses.
- Test data builders for common types.

For **network-blocking**:

- conftest.py has the `no_external_network` fixture autouse. Catches accidents.

For **markers**:

- `e2e`, `slow`, `requires_ollama`, `requires_lmstudio`. Per `pyproject.toml`.

What to avoid:

- Don't run e2e on every commit. CI nightly or on-demand.
- Don't write tests that depend on external network without stubs.
- Don't write integration tests that rely on real cloud LLM calls.
- Don't make e2e tests so brittle they break on minor changes.

## 6. Open questions

- **The right balance** of unit vs integration vs e2e. Classical pyramid (many unit, few e2e); some teams favour "diamond" (many integration, fewer unit, fewer e2e).
- **Contract testing** — verify that stubs match real services. Tools like Pact.
- **Snapshot vs assertion in e2e.** E2e outputs are often partially-stable; snapshot with stabilisation.

## 7. References (curated)

- Beck, *TDD by Example*, 2002.
- Meszaros, *xUnit Test Patterns*, 2007.
- martinfowler.com/articles/practical-test-pyramid.html — Fowler on the test pyramid.
- Companion docs: [[30-pytest-mastery]], [[31-hypothesis-property-based-testing]], [[35-test-doubles]].

# 30 — pytest Mastery: Fixtures, Parameterization, Marks, conftest

**Category:** Testing
**Runa relevance:** tests/, every test in the project
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

`pytest` has become the de facto standard for Python testing. Its key innovations — assertion rewriting (you can write plain `assert x == y` instead of `self.assertEqual`), fixtures (composable dependency injection for tests), parameterization, and the plugin ecosystem — make tests dramatically more pleasant to write and read than the older `unittest`. Mastering pytest pays for itself in test velocity.

For Runa, every test goes through pytest. The `tests/` structure (unit / integration / e2e / fixtures / snapshots) is pytest-shaped. The `pyproject.toml` configures markers, paths, options.

## 2. Technique / mechanism

**The basic test:**

```python
def test_addition():
    assert 1 + 1 == 2
```

No subclassing required. `pytest` discovers files matching `test_*.py` and functions matching `test_*`.

**Fixtures:**

```python
import pytest

@pytest.fixture
def episode_factory():
    """Produces fresh Episode instances for tests."""
    def _make(text="hello", **kwargs):
        return Episode(
            episode_id=uuid4(),
            text=text,
            timestamp=utcnow(),
            **kwargs,
        )
    return _make

def test_episode_text_stored(episode_factory):
    ep = episode_factory(text="my message")
    assert ep.text == "my message"
```

Fixtures provide test inputs / state. Their setup runs per test by default.

**Fixture scopes:**

```python
@pytest.fixture(scope="session")  # once per pytest session
def db_engine():
    engine = create_engine(...)
    yield engine
    engine.dispose()

@pytest.fixture(scope="module")  # once per test module
def temp_dir():
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d)

@pytest.fixture  # default scope is "function" — fresh per test
def fresh_state():
    return {}
```

Scopes: `function` (default) | `class` | `module` | `package` | `session`.

**`yield` fixtures (setup + teardown):**

```python
@pytest.fixture
def open_file(tmp_path):
    path = tmp_path / "test.txt"
    f = path.open("w")
    yield f       # test runs here
    f.close()     # teardown after test
```

**Parameterization:**

```python
@pytest.mark.parametrize("input,expected", [
    (1, 1),
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    assert input ** 2 == expected
```

Runs the test once per tuple. Each is a separate test case in reports.

**Indirect parameterization:**

```python
@pytest.fixture
def database(request):
    return create_database(name=request.param)

@pytest.mark.parametrize("database", ["sqlite", "postgres"], indirect=True)
def test_with_db(database):
    ...
```

Parameter feeds into a fixture.

**Markers:**

```python
@pytest.mark.slow
def test_takes_a_while():
    ...

@pytest.mark.requires_ollama
def test_local_inference():
    ...

@pytest.mark.skip(reason="not yet implemented")
def test_future():
    ...

@pytest.mark.skipif(sys.platform == "win32", reason="POSIX only")
def test_unix():
    ...

@pytest.mark.xfail(reason="known bug 123")
def test_known_failure():
    ...
```

Configure in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow",
    "requires_ollama: needs local Ollama",
    "e2e: end-to-end",
]
```

Run subsets:
```bash
pytest -m "slow"           # only slow
pytest -m "not slow"        # exclude slow
pytest -m "requires_ollama" # gated
```

**conftest.py — shared fixtures:**

```
tests/
├── conftest.py            # fixtures for all tests in tests/
├── unit/
│   ├── conftest.py        # fixtures for tests/unit/ and below
│   └── test_kernel.py
└── integration/
    └── test_flow.py
```

Fixtures defined in a `conftest.py` are available to all tests in that directory and below. No imports needed.

**Built-in fixtures:**

- `tmp_path` — temporary `Path` per test. Cleanest test-isolated I/O.
- `monkeypatch` — set/unset env vars, attributes, syspath.
- `capsys` / `capfd` — capture stdout/stderr.
- `caplog` — capture log records.
- `request` — info about the test.

```python
def test_env(monkeypatch):
    monkeypatch.setenv("RUNA_HOME", "/tmp/test")
    assert os.environ["RUNA_HOME"] == "/tmp/test"

def test_writes(tmp_path):
    (tmp_path / "out.txt").write_text("hello")
    assert (tmp_path / "out.txt").read_text() == "hello"
```

**Async tests:**

```python
import pytest
import pytest_asyncio

@pytest.mark.asyncio
async def test_async():
    result = await some_async_function()
    assert result == expected
```

`pytest-asyncio` plugin enables async fixtures and tests.

**Plugins ecosystem:**

- `pytest-asyncio` — async test support.
- `pytest-cov` — coverage reporting.
- `pytest-xdist` — parallel test execution.
- `pytest-mock` — `mocker` fixture.
- `pytest-snapshot`, `syrupy` — snapshot testing.
- `pytest-benchmark` — performance benchmarks.
- `hypothesis` — property-based testing ([[31-hypothesis-property-based-testing]]).

**Configuration:**

```toml
[tool.pytest.ini_options]
minversion = "8.0"
testpaths = ["tests"]
addopts = [
    "-ra",                      # show summary of all (skipped, failed, xpassed)
    "--strict-markers",         # unknown marker = error
    "--strict-config",          # unknown config = error
    "-x",                       # stop on first failure (omit for full run)
]
markers = [...]
```

## 3. Key works / libraries

- **pytest** — docs.pytest.org.
- **PEP 8 (testing style).**
- **Holger Krekel's** original py.test design.
- **Brian Okken** — *pytest Quick Start Guide*; "Test & Code" podcast.
- **`pytest-asyncio`** — github.com/pytest-dev/pytest-asyncio.
- **`pytest-cov`** — github.com/pytest-dev/pytest-cov.
- **`pytest-mock`** — github.com/pytest-dev/pytest-mock.

## 4. Pitfalls and gotchas

- **Fixture ordering / dependencies.** Fixtures can depend on other fixtures; chains can be deep and confusing. Document.
- **Session-scoped mutable state.** A session fixture modified by one test affects others. Be careful.
- **`monkeypatch` doesn't undo at function exit.** Actually it does (it's scoped to the test). But for module-level monkeypatching, use `request.getfixturevalue(...)` carefully.
- **Test discovery.** Files must match `test_*.py`; test functions must start with `test_`. Otherwise silently skipped.
- **Async tests without the marker.** Without `@pytest.mark.asyncio`, async tests are returned as coroutines — silently never run.
- **Fixture finalization on error.** Use `yield` style; the teardown after `yield` runs even if the test fails.
- **Slow imports in conftest.** Loaded for every test; slow imports = slow test startup.
- **Parameterized test names.** Pytest auto-generates names from params; complex types produce ugly IDs. Use `ids=[...]`.

## 5. Applicability to Runa

For **tests/unit/**:

- Per-module fixtures in module-specific `conftest.py`.
- `tmp_path`-based for any disk I/O.
- Heavy use of `monkeypatch` for swapping dependencies.

For **tests/integration/**:

- Larger fixtures (stub Heimskringla, in-memory Muninn) in `tests/integration/conftest.py`.
- Markers (`@pytest.mark.requires_ollama`) for tests gating on external services.

For **tests/e2e/**:

- Marked `@pytest.mark.e2e`; excluded from default run.

For **markers in pyproject.toml**:

- Already declared per the bootstrap (`slow`, `e2e`, `requires_ollama`, `requires_lmstudio`).

For **async testing**:

- `pytest-asyncio` for kernel-loop testing. Pin `mode = "auto"` to avoid mark boilerplate.

What to avoid:

- Don't write tests that depend on test-execution order. Each test independent.
- Don't ship code without tests.
- Don't make tests rely on real network. Stub.
- Don't catch `Exception` and `assert False`. Use `pytest.raises`.

## 6. Open questions

- **Pytest vs unittest** — pytest dominates new code; unittest still in legacy.
- **Pytest plugin proliferation** — every plugin adds complexity. Pick the few that matter.
- **Test-time secrets** — env vars in `monkeypatch` or `.env.test`? Both work.

## 7. References (curated)

- docs.pytest.org.
- Okken, B. *pytest Quick Start Guide*.
- realpython.com/pytest-python-testing/.
- Companion docs: [[31-hypothesis-property-based-testing]], [[33-snapshot-testing]], [[34-integration-e2e-testing]], [[35-test-doubles]].

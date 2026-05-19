# 18 — Chaos Engineering and Fault Injection in Python

**Category:** Self-Healing & Supervision
**Runa relevance:** tests/ (integration), Eir validation, pre-deployment confidence
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

**Chaos engineering** is the practice of deliberately injecting failures into a system to verify that its fault-tolerance machinery actually works. Pioneered at Netflix (Chaos Monkey, 2010+), it has become a standard practice for production-grade systems. The core insight: *every fault-tolerance feature is a hypothesis* — "if X fails, the system continues" — and the only way to know whether the hypothesis is true is to test it. Without chaos engineering, you find out whether your retry / breaker / supervisor logic works *during the actual incident*.

For Runa, chaos engineering is most useful at *test time*: integration tests that simulate adapter timeouts, model rate-limits, Muninn corruption, disk-full conditions, and verify Runa's responses. Production chaos is less applicable to a single-user personal agent — but the *fault injection* mindset informs Eir's design (Eir is, in a sense, a periodic chaos-injector that the agent expects).

## 2. Technique / mechanism

**The chaos engineering loop:**

```
[1] Form a hypothesis: "Under condition X, the system does Y."
[2] Design an experiment: inject the condition, observe the behaviour.
[3] Minimise blast radius: smallest scope where the hypothesis can be tested.
[4] Run the experiment, observe.
[5] Compare actual behaviour to hypothesis.
[6] If different: fix the bug, re-run the experiment.
[7] If same: enable the experiment continuously (production chaos).
```

**Fault injection categories:**

- **Latency injection.** Add delay to operations. Validates timeout / deadline propagation.
- **Error injection.** Make operations fail. Validates retry / circuit breaker / fallback.
- **Resource pressure.** Memory, CPU, disk, fds. Validates degradation.
- **Network partition.** Block traffic between components. Validates split-brain handling.
- **State corruption.** Mutate persisted state. Validates integrity checks + repair.
- **Time skew.** Move the clock. Validates time-dependent logic.

**Python-side fault injection patterns:**

### Pattern 1 — Wrapping calls with injectable failures

```python
import random
from contextvars import ContextVar

chaos_enabled: ContextVar[bool] = ContextVar("chaos", default=False)
chaos_rate: ContextVar[float] = ContextVar("chaos_rate", default=0.0)

async def with_chaos(fn, *, fault_rate: float = 0.1):
    if chaos_enabled.get() and random.random() < fault_rate:
        # Inject a random failure
        await asyncio.sleep(random.uniform(0, 5))  # latency
        if random.random() < 0.5:
            raise TimeoutError("chaos: simulated timeout")
        else:
            raise ConnectionError("chaos: simulated network error")
    return await fn()
```

### Pattern 2 — Mock-based fault injection in tests

```python
@pytest.fixture
def flaky_provider(monkeypatch):
    """Provider that fails 30% of calls."""
    real_complete = provider.complete
    call_count = 0
    
    async def flaky_complete(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count % 3 == 0:
            raise ProviderError("flaky", retryable=True)
        return await real_complete(*args, **kwargs)
    
    monkeypatch.setattr(provider, "complete", flaky_complete)
    return provider

def test_heimskringla_handles_flaky_provider(flaky_provider):
    # Verify retry recovers
    result = asyncio.run(heimskringla.call(request))
    assert result.success
    # Verify breaker doesn't trip prematurely
    ...
```

### Pattern 3 — Hypothesis-driven property tests with fault injection

```python
from hypothesis import given, strategies as st

@given(
    failure_pattern=st.lists(st.booleans(), min_size=5, max_size=20),
    timing=st.lists(st.floats(min_value=0, max_value=10), min_size=5, max_size=20),
)
def test_circuit_breaker_survives_arbitrary_patterns(failure_pattern, timing):
    breaker = CircuitBreaker(failure_threshold=3, reset_timeout=5.0)
    # Apply the failure pattern; verify breaker maintains invariants
    ...
```

### Pattern 4 — In-process chaos via decorators

```python
from chaos import chaos_call

@chaos_call(latency_ms=(0, 1000), failure_rate=0.1, error=TimeoutError)
async def call_external_service(...):
    ...
```

Decorator-based fault injection enabled in test/staging environments.

**Time control (vs production):**

```python
from freezegun import freeze_time

@freeze_time("2026-01-01 00:00:00")
def test_eir_reconciles_after_one_day():
    ...
    with freeze_time("2026-01-02 00:00:00"):
        eir.run_reconciliation()
        assert ...
```

`freezegun` and the newer `time-machine` library let tests manipulate time without changing application logic.

**Filesystem chaos:**

```python
def test_muninn_handles_disk_full(tmp_path, monkeypatch):
    # Mock fsync / write to fail with ENOSPC
    def fake_write(self, data):
        raise OSError(errno.ENOSPC, "fake disk full")
    monkeypatch.setattr(SomeWriter, "write", fake_write)
    # Verify Muninn degrades gracefully
    ...
```

**Subprocess chaos:**

For full-process tests, `pytest-subtests`, `pytest-xdist`, or `pexpect` to drive subprocesses with controlled failure.

## 3. Key works / libraries

- **Basiri, A. et al.** "Chaos Engineering." IEEE Software, 2016. The Netflix-team paper.
- **Rosenthal, C. et al.** *Chaos Engineering: System Resiliency in Practice*. O'Reilly, 2017.
- **principlesofchaos.org** — the manifesto.
- **Netflix Chaos Monkey, Chaos Kong, ChAP** — the foundational tooling.
- **Gremlin** — gremlin.com. Commercial chaos-engineering platform.
- **`chaostoolkit`** — github.com/chaostoolkit/chaostoolkit. Open-source Python chaos framework.
- **`pytest-fault`** and similar — fault-injection in tests.
- **`freezegun`** — github.com/spulec/freezegun. Time manipulation.
- **`time-machine`** — github.com/adamchainz/time-machine. Modern alternative.
- **`pytest-monkeypatch`** (stdlib) — base for fault injection in tests.

## 4. Pitfalls and gotchas

- **Chaos in production for a single-user agent is overkill.** Save for tests + perhaps periodic Eir-driven internal probes.
- **Tests that depend on injected timing.** Brittle. Use deterministic patterns (every-Nth-call fails) rather than random.
- **Forgotten chaos still enabled.** Chaos in CI is fine; chaos in production for a personal agent is annoying. Hard-code disable in non-test deployments.
- **Chaos that masks real bugs.** A flaky test is sometimes a chaos-induced failure that's *also* a real bug. Investigate.
- **Chaos for cosmetic features.** Don't inject failures into log formatting just to "test something." Be principled about what hypothesis you're testing.
- **Insufficient observability during chaos.** If you can't see what happened, you can't learn. Pair chaos with metrics + tracing.
- **Hard to reproduce.** Random chaos is hard to debug. Capture the seed; replay with the same seed.

## 5. Applicability to Runa

For **tests/integration/**:

Build a test harness that injects:
- Adapter timeouts (every chat-platform adapter).
- Model-provider rate limits and errors (every Heimskringla provider).
- Muninn read/write failures.
- Disk full (ENOSPC) during Skuld writes.
- WYRD bridge unavailability.
- Combinations (cascade failures).

For each, assert: Runa continues responding (degraded if necessary); audit log records the failure; Eir recovers.

For **chaos in CI**:

A subset of integration tests run with `chaos_enabled=True` to probe randomly. Surfaces unexpected interactions.

For **Eir as a kind of internal chaos**:

Eir's reconciliation loop is itself a form of "chaos that the agent expects" — it deliberately runs actions that re-test agent assumptions (re-enable quarantined adapter, attempt repair on flagged subsystems). The agent is built to survive Eir's actions.

For **fault-injection-style audit-log review**:

Periodically, look at the audit log for "interesting failures" and ensure each was handled. New failure modes that *weren't* handled gracefully become chaos-engineering hypotheses to verify in tests.

What to avoid:

- Don't run unbounded production chaos on a personal agent. Test-time only.
- Don't use chaos to compensate for missing real testing. Chaos discovers; unit tests cover the basics.
- Don't randomise chaos in a way that makes test failures unreproducible.
- Don't inject chaos into pure-compute paths. Chaos belongs at I/O boundaries.

## 6. Open questions

- **Chaos engineering for AI agents specifically.** Standard frameworks target microservice fleets. Adapting to single-process Python agents: most patterns transfer, fixture-based injection is more practical than infrastructure-level.
- **Behavioural chaos for LLMs.** What happens if a model returns surprisingly bad output? "Quality chaos" is harder to define than "failure chaos."
- **Chaos in development vs CI vs production.** Different scopes; different policies. The right blend per team.

## 7. References (curated)

- principlesofchaos.org — the manifesto.
- *Chaos Engineering* (Rosenthal et al., O'Reilly 2017).
- chaostoolkit.org — Chaos Toolkit (Python framework).
- github.com/spulec/freezegun — freezegun.
- github.com/adamchainz/time-machine — time-machine.
- netflix.github.io — Netflix engineering blog, chaos series.
- Companion docs: [[06-retry-strategies]], [[07-circuit-breaker]], [[34-integration-e2e-testing]], [[31-hypothesis-property-based-testing]].

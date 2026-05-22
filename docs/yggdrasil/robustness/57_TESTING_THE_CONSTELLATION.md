# 57 — Testing the Constellation

How we test eleven sibling projects + their integrations
without combinatorial explosion. The testing strategy.

---

## The challenge

Naive testing: every combination of every realm × every
state × every failure mode = unmanageable.

Yggdrasil instead: **layered testing** with each layer
covering a different concern, *composing* to comprehensive
coverage without exhaustive combinatorial paths.

---

## The five test layers

### Layer 1: Sibling unit tests (already exist)

Each sibling project ships with its own tests. Yggdrasil
*doesn't duplicate them*; we trust each sibling's CI to
verify its own correctness.

- `bifrost/tests/` is bifrost's responsibility.
- `mimir-well/tests/` is mimir-well's responsibility.
- etc.

What Yggdrasil verifies: that our *adapter* correctly
uses the sibling's *public API*. Not the internals.

### Layer 2: Yggdrasil adapter tests (in Ember repo)

For each sibling, we have:
- `tests/unit/test_yggdrasil_<sibling>_adapter.py`
- Mocks the sibling's library; verifies our adapter
  implements the Protocol correctly.
- Fast (no real sibling running).

E.g., `test_yggdrasil_bifrost_adapter.py` verifies that
`BifrostBrunnr` correctly implements `BrunnrHandle` by
calling a fake Bifrǫst.

### Layer 3: Integration tests (in Ember repo)

For each sibling, we have:
- `tests/integration/test_yggdrasil_<sibling>_real.py`
- Marked with `pytest.mark.requires_<sibling>`.
- Spawns or connects to a real sibling instance.
- Verifies actual end-to-end behavior.

E.g., `test_yggdrasil_bifrost_real.py` uses a real Bifrǫst
Bridge + real Qdrant container + real Mímir DB.

Opt-in via CI markers; doesn't run on every PR.

### Layer 4: Cross-realm integration tests

For multi-realm scenarios:
- `tests/integration/test_yggdrasil_full_chat_turn.py`
  drives a complete chat turn with Bifrǫst + Mímir +
  Huginn + Muninn + emotional-intelligence layer + audit.
- Verifies the *whole flow* works.

These are slower; gated by `requires_full_yggdrasil`
marker.

### Layer 5: Failure-mode tests

For each catalogued failure (per the recovery playbooks):
- `tests/integration/test_yggdrasil_recovery_<failure>.py`
- Simulates the failure.
- Verifies the playbook executes correctly.
- Verifies the system continues operating.

This is where invariant enforcement happens. Each
invariant from
[`55_BUG_RESISTANCE_INVARIANTS.md`](55_BUG_RESISTANCE_INVARIANTS.md)
has a corresponding failure-mode test.

---

## What gets mocked vs real

| Layer | Approach | Trade-off |
|---|---|---|
| 1 (sibling) | Real sibling code | Sibling's choice |
| 2 (adapter) | Sibling mocked; adapter real | Fast; tests our code only |
| 3 (per-sibling integration) | Real sibling, real Ember | Slow; catches integration bugs |
| 4 (cross-realm) | All real | Slowest; catches cross-realm bugs |
| 5 (failure modes) | Real with injected failures | Catches recovery bugs |

Most PRs run Layer 1 + 2 only (fast). Layers 3-5 run
nightly + on release branches.

---

## Test markers

```python
# Layer 2 — always runs
@pytest.mark.unit
def test_bifrost_adapter_implements_protocol(): ...

# Layer 3 — opt-in
@pytest.mark.requires_qdrant
@pytest.mark.requires_bifrost
def test_bifrost_real_search(): ...

# Layer 4 — opt-in
@pytest.mark.requires_full_yggdrasil
def test_full_chat_turn_with_all_realms(): ...

# Layer 5 — opt-in
@pytest.mark.requires_failure_injection
@pytest.mark.recovery_playbook("M-1")
def test_huginn_unreachable_recovery(): ...
```

CI configurations:
- **Per-PR fast**: unit tests only (~30 seconds).
- **Per-PR slow** (opt-in): Layer 3 for the touched sibling
  (~5 minutes).
- **Nightly**: all layers (~30 minutes).
- **Release**: all layers + manual smoke on Pi 5 cluster.

---

## How we test multi-device (Phase 4)

The federation layer adds a new dimension: tests need to
verify multiple Ember instances coordinating.

Approach:
- `tests/integration/test_yggdrasil_federation_2node.py`
  spawns two Ember processes; verifies they federate.
- `tests/integration/test_yggdrasil_federation_failure.py`
  spawns two; kills one; verifies the other continues +
  recovers.

Containerized for CI (each "node" is a Docker container).

---

## Snapshot tests for state evolution

Some integration tests need to verify *state changes over
time* — like "after 100 chat turns, the meta-learning
patterns should reflect operator preferences."

Pattern:
```python
async def test_meta_learning_converges_over_episodes():
    cluster = await yggdrasil_test_cluster()
    
    # Drive 100 synthetic chat turns
    for i in range(100):
        await cluster.chat(f"question {i}")
    
    # Verify patterns emerged
    patterns = cluster.meta_learning.current_patterns()
    assert "response_length_preference" in patterns
```

These are *slow* (minutes) but high-value.

---

## What we don't test

- **Sibling internals.** Each sibling's CI handles its own.
- **Funi model output quality.** We don't have ground-truth
  for LLM responses; we test integration shape, not
  correctness of natural language.
- **Operator-subjective behaviors.** "Does the tone feel
  right?" — can't automate; operator feedback.
- **External APIs.** Wikipedia, Cloudflare, etc. — out of
  our control; we test the request shape, not the response.

---

## The test data

For deterministic tests:

- **Synthetic chat corpora** in `tests/fixtures/chats/`.
- **Synthetic document corpora** in `tests/fixtures/docs/`.
- **Synthetic embedding seeds** for reproducible vector
  state.
- **Synthetic Episode histories** for awareness-layer tests.

All committed; CI can re-run identically across machines.

---

## Performance regression tests

Specific tests verify performance budgets:

- Single chat turn (Pi 5): < 5 seconds end-to-end.
- Memory store fan-out: < 100ms.
- Hybrid search (10K-chunk corpus): < 100ms.
- Stofa launch: < 3 seconds.

These run on a reference CI machine. Regressions fail
the build.

---

## What CI looks like

```yaml
# .github/workflows/test.yml
jobs:
  unit:
    runs-on: ubuntu-latest
    steps: [pytest -m unit]
  
  integration-bifrost:
    runs-on: ubuntu-latest
    services: [qdrant, ...]
    steps: [pytest -m requires_bifrost]
  
  integration-full:
    runs-on: ubuntu-latest
    services: [qdrant, verdandi, ...]
    if: branch == 'main' OR contains(labels, 'full-test')
    steps: [pytest -m requires_full_yggdrasil]
  
  performance:
    runs-on: ubuntu-latest
    needs: unit
    steps: [pytest -m performance --benchmark-compare]
```

Per-PR: fast unit tests. Per-merge: integration. Nightly:
full + performance. Release: manual Pi 5 smoke.

---

## When tests fail

Each failure tells the developer something:
- Unit fail: code logic broken.
- Integration fail: integration broken (or sibling
  version regression).
- Recovery test fail: a playbook stopped working.
- Performance fail: regression in critical path.

Each failure has a *specific* meaning; the developer knows
what to investigate.

---

## Closing

Testing the Constellation is **layered, opt-in, fast-where-
possible, comprehensive-where-needed**. Eleven sibling
projects don't produce 11× the test load because we test
the *integration shape* not the *sibling internals*.

The cumulative confidence: a Yggdrasil release ships
*tested across every meaningful surface*. Operators get
a system that's been through every catalogued failure
mode in CI before it ever runs on their hardware.

This is what "robust to a fault" actually requires.

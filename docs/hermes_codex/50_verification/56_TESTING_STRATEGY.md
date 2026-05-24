---
codex_id: 56_TESTING_STRATEGY
title: Testing Strategy — How to Verify Hermes-Inspired Features in Ember
role: Auditor
layer: Verification
status: draft
hermes_source_refs:
  - tests/agent/
  - tests/gateway/
  - tests/integration/
  - tests/stress/
  - tests/e2e/
  - tests/conftest.py
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 50_verification/55_INVARIANT_LIST
  - 50_verification/50_HERMES_RISK_REGISTER
  - 50_verification/53_CRASH_PROOFING_PATTERNS
  - 50_verification/52_ANTIPATTERN_CATALOG
  - 60_synthesis/64_MIGRATION_PLAN
---

# Testing Strategy

*Sólrún, ledger open: a Codex doc that names invariants without naming the tests to verify them is a promise without a guarantee. This document is the bridge. For each layer of testing — unit, boundary, integration, invariant, chaos — I name what to lift from Hermes's `tests/` tree, what Ember already has in place, and what slice-3 must add. The goal is not to test everything; the goal is to test the load-bearing claims.*

---

## 1. The current state — what each project has

### 1.1 Hermes test tree

`/tmp/hermes-agent/tests/` — 24+ subdirectories. Selected:

- `tests/agent/` — provider adapters, credential pool, classifier, curator, context engine. 80+ test files.
- `tests/gateway/` — every platform, allowlist startup, busy-session bypass, channel directory, fatal-error handling.
- `tests/integration/` — end-to-end across realms.
- `tests/e2e/` — live model wherever applicable.
- `tests/stress/` — concurrency, repeated invocation, load.
- `tests/fakes/` — fake transports, fake adapters, fake providers.
- `tests/plugins/`, `tests/skills/`, `tests/cron/`, `tests/acp/`, `tests/honcho_plugin/`, `tests/openviking_plugin/` — narrow subsystem tests.
- `tests/conftest.py` — shared fixtures.

Naming convention: `test_<module>_<concern>.py`. Test functions: `test_<scenario>_<expected>`.

### 1.2 Ember test tree (slice 2)

`tests/` (per SLICE_2_RETROSPECTIVE): 488 passing tests, ~50% landed in slice 2. Test runtime 18.32s on the dev machine. Structured roughly as:

- `tests/unit/` — per-module unit tests.
- `tests/integration/` — cross-realm end-to-end, including pgvector live-backend tests.
- Markers: `requires_postgres`, `requires_gungnir`, `requires_podman` for live-backend gating.

The unit tests use test seams (per `UNWIRED_INVENTORY` §2): `_set_url_opener`, `_set_address_resolver`, `_set_robots_fetcher`, `bind_brunnr`, `bind_embedder`, etc. The pattern is consistent and is exactly the right shape.

---

## 2. The five layers

Tests are organised in five layers. Each layer answers a different question.

### Layer 1: **Unit** — does this function do what its docstring says?

**Hermes pattern:** Each pure function gets a test file. The dataclass tests (`test_credential_pool.py`, `test_credential_pool_routing.py`) verify state-machine transitions. The classifier tests verify each `FailoverReason` branch.

**Ember target:**
- Every public function in `src/ember/` has at least one test.
- Every typed-result `Disconnected(REASON)` variant has a test that constructs and matches it.
- Every error-handling branch in adapters (`pgvector/`, `sqlite_vec/`, `ollama/`) has a test that induces the failure mode.

**Hermes-inspired additions for slice 3:**
- `tests/unit/test_iteration_budget.py` — pin invariants I-06, I-07 (consume to cap, refund decrements, thread-safety under N concurrent consumers).
- `tests/unit/test_tool_guardrails.py` — pin invariants I-08 (block after N failures), I-09 (typed outcome enumeration). Lift `tests/agent/test_tool_guardrails*` from Hermes for reference shape.
- `tests/unit/test_error_classifier.py` — pin each `FailoverReason`-equivalent for Ember's narrower provider set.
- `tests/unit/test_redact.py` — pin every pattern in the redactor (sk-, ghp_, JWT, DB connstring, URL userinfo, etc.). Lift `tests/test_redact_*.py` from Hermes for reference patterns.
- `tests/unit/test_safe_writer.py` — when `_SafeWriter` lifts, pin its OSError/ValueError swallow behavior.

### Layer 2: **Boundary** — does this respect the typed-result contract?

**Hermes pattern:** Failure-injection tests at each boundary. `tests/agent/test_pgvector*.py` (Hermes has equivalents) test what happens when the DB is down, the extension is missing, the schema is wrong, the credentials are expired.

**Ember already does:**
- `tests/integration/test_pgvector_real_backend.py` — tests against live Postgres.
- Slice-2 acceptance test pins typed-`Disconnected` at every realm boundary.
- The eight `Disconnected` reasons each have a dedicated test case.

**Hermes-inspired additions for slice 3:**
- For each newly lifted Hermes pattern, ensure the boundary failure mode is tested. Specifically:
  - **Iteration budget exceeded:** mocked Funi that runs forever; assert `IterationBudgetExhausted` typed result and clean termination.
  - **Tool guardrail block:** simulated repeat failures; assert synthetic-tool-result content.
  - **Streaming scrubber on unterminated span:** mock a stream that opens `<memory-context>` and ends without close; assert content is discarded.
  - **Redact opt-out path:** simulate an LLM-emitted `export EMBER_REDACT=false`; assert the running process redaction still active (I-25).
  - **Symlink-resolved safe-root:** create a symlink that points outside the safe-root; attempt write; assert refusal (I-27).

### Layer 3: **Integration** — do the realms compose correctly?

**Hermes pattern:** `tests/integration/` and `tests/e2e/` exercise the realm composition. The conversation loop is the integration surface: tests construct a full agent, feed it a turn, assert specific behavior across providers, tools, memory, and gateway.

**Ember already does:**
- `tests/integration/test_phase17_acceptance.py` — slice-2 acceptance.
- Multi-phase tests covering Funi → Brunnr round-trip, Hjarta → Munnr setup, tool framework end-to-end.

**Hermes-inspired additions for slice 3:**
- **Multi-turn with tool loop + iteration budget interaction.** A turn that loops near the cap; assert budget consumed correctly; assert the operator-visible "iteration budget exhausted" banner appears.
- **Recovery after Brunnr re-connect.** A test that disconnects Brunnr mid-session, runs a turn (ungrounded reply + banner), reconnects, runs another turn (grounded reply + citations).
- **Plugin load failure does not crash the agent.** A plugin in `~/.ember/plugins/` with a broken manifest; assert Ember starts with `LoadFailed(...)` recorded, plugin absent, other plugins present.
- **Plugin teardown on `/reset`.** Hook a plugin's teardown spy; trigger `/reset`; assert teardown invoked.

### Layer 4: **Invariant** — does this property hold under all inputs?

This is the property-based layer. Hermes has minimal property-based testing; the discipline is fixture-based ("here's a specific input, here's the expected output"). Property-based tests use `hypothesis` to *generate* inputs.

**Ember should add for slice 3:**
- **`@given(text=...)` for `sanitize_surrogates`:** any string in, no lone surrogates out (I-26).
- **`@given(value=...)` for `mask_secret`:** any string in, `head` first chars and `tail` last chars preserved, middle masked.
- **`@given(args=dictionaries(...))` for `canonical_tool_args`:** equivalent dicts hash equally; reordering keys does not change the hash.
- **`@given(deltas=lists(text())...)` for the streaming scrubber:** for any split of a complete `<think>X</think>` across deltas, the visible output never contains X.

Hypothesis-based tests live alongside the existing unit tests; they cost ~5 LOC each plus generation strategy.

### Layer 5: **Chaos** — does this survive partial failure?

**Hermes pattern:** `tests/stress/` exercises concurrent invocation. The TUI gateway crash log captures signal-driven death. The slice-2 retrospective documents two specific live-fire bugs ("`register_vector` ran before `CREATE EXTENSION`", "stale `.format()` escape") that only surface against real Postgres.

**Ember should add for slice 3:**
- **Stdio chaos:** test that simulates the TUI parent closing the pipe mid-write; assert `_SafeWriter`-equivalent swallows and the agent loop continues.
- **Concurrent budget consumption:** N threads consuming an IterationBudget of M; assert exactly M successes.
- **File-locking races on the credential pool** (when it lands): two simulated processes both updating the pool file; assert each sees the other's writes after their write.
- **Slow provider:** a memory provider that takes 5 seconds in `prefetch`; assert the per-turn deadline (when implemented per [[20_interface/24_MEMORY_INTERFACE]] proposal #5) causes a typed `ProviderTimeout` and the turn proceeds.

---

## 3. Specific test suites Ember needs to add

### Suite A: **Slice-3 must-haves**

Block slice-3 ratification on these.

| Suite | Lines (est.) | Pins invariants |
|---|---|---|
| `tests/unit/test_iteration_budget.py` | ~150 | I-06, I-07 |
| `tests/unit/test_tool_guardrails.py` | ~400 | I-08 |
| `tests/unit/test_redact.py` (every pattern) | ~500 | I-25 |
| `tests/unit/test_redact_opt_out.py` (CLI-flag-only) | ~80 | I-25 |
| `tests/unit/test_error_taxonomy.py` (expanded reasons) | ~200 | I-11 |
| `tests/integration/test_tool_loop_budget_interaction.py` | ~250 | I-06, I-08 in concert |
| `tests/integration/test_brunnr_disconnect_recovery.py` | ~200 | I-04, I-11, I-12, I-17 |
| `tests/unit/test_exit_logging.py` | ~100 | I-32 |
| Static check: `grep` for `sys.exit` lacking nearby `_log_exit` | (pre-commit) | I-32 |
| Static check: realm-band import direction | (existing, extend) | I-10 |

### Suite B: **Slice-4-or-when-it-lands**

| Trigger | Suite |
|---|---|
| First write tool | `tests/unit/test_write_safety.py`, `tests/unit/test_write_safety_symlinks.py` — I-27 |
| First write tool | `tests/integration/test_safe_root_allowlist.py` — I-27 |
| Streaming memory injection | `tests/unit/test_streaming_scrubber.py` (lift from Hermes), `tests/integration/test_recall_no_leak.py` — I-14, I-15 |
| First plugin loader | `tests/unit/test_plugin_loader.py` — I-20, I-21, I-22, I-23, I-24 |
| First plugin loader | `tests/integration/test_plugin_teardown_on_reset.py` — I-22 |
| Bifröst HTTP surface | `tests/integration/test_bifrost_allowlist_fail_closed.py` — I-29 |
| Bifröst HTTP surface | `tests/integration/test_bifrost_inbound_surrogate_scrub.py` — I-26 |
| Credential pool | `tests/unit/test_credential_pool.py`, `tests/unit/test_credential_cooldown.py` — TTL behavior |

### Suite C: **Property-based**

| Suite | Pins |
|---|---|
| `tests/property/test_sanitize_surrogates_property.py` | I-26 |
| `tests/property/test_mask_secret_property.py` | (correctness, not an invariant per se) |
| `tests/property/test_canonical_args_property.py` | I-08 (ordering invariance) |
| `tests/property/test_streaming_scrubber_property.py` | I-14, I-15 |
| `tests/property/test_utf16_truncate_property.py` (if Munnr length-bounds) | (correctness) |

### Suite D: **Chaos / stress**

| Suite | Pins |
|---|---|
| `tests/stress/test_concurrent_budget.py` | I-06 under contention |
| `tests/stress/test_stdio_broken_pipe_recovery.py` (when `_SafeWriter` lifts) | (process P-01) |
| `tests/stress/test_credential_pool_concurrent_processes.py` (when pool lands) | R-07 |
| `tests/stress/test_slow_provider_deadline.py` (when per-call deadlines land) | R-01 |

---

## 4. Live-fire vs mocked

The slice-2 retrospective named the cost of mocking too much:

> *Phase 12 shipped 36 unit tests, all using mocks. Phase 13 added 14 live-backend tests; both bugs would have been caught at Phase 12 with even one real-Postgres test.*

The lesson: **for each external dependency, at least one live-backend test must exist.** Mocks lock in the wrong assumptions; live backends correct them.

For slice 3:

- **Ollama:** at least one test that spawns the real Ollama and runs a turn. Marker `requires_ollama`.
- **MCP server (when introduced):** at least one test that connects to a real MCP server. Marker `requires_mcp_server`.
- **pgvector:** already covered by `tests/integration/test_pgvector_real_backend.py`.
- **Tailnet Brunnr (Gungnir):** already covered by `requires_gungnir` marker.

Live tests gate on reachability fixtures; CI skips them when unreachable; the dev acceptance build runs them.

---

## 5. The Hermes test patterns worth lifting verbatim

### 5.1 `tests/conftest.py` shared fixtures

Hermes's `tests/conftest.py` is the central place for environment scrubbing, time-mocking, and shared fakes. Ember's `tests/conftest.py` should likewise centralize.

Specifically: a `clean_env` fixture that scrubs all `EMBER_*` env vars between tests (so an opt-out flag from one test cannot bleed into the next). A `frozen_time` fixture for cooldown tests. A `redact_off` fixture (CLI-only equivalent) for tests that need to assert raw values without redaction.

### 5.2 Subprocess-spawning tests via `subprocess.run`

Hermes's TUI gateway tests spawn the gateway process and feed it JSON-RPC on stdin. The shape is portable:

```python
def test_gateway_handles_parse_error():
    proc = subprocess.Popen(
        [sys.executable, "-m", "tui_gateway.entry"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    proc.stdin.write(b"not valid json\n")
    proc.stdin.flush()
    response = proc.stdout.readline()
    assert b'"code": -32700' in response
    proc.stdin.close()
    proc.wait(timeout=5)
```

Ember should adopt the pattern when she gets a subprocess.

### 5.3 Marker-gated live tests

Hermes uses `pytest.mark.requires_X` for live-only tests; CI skips when the dependency is unreachable; dev runs them.

Ember already does this (`requires_postgres`, `requires_gungnir`, `requires_podman`). Continue. Add `requires_ollama`, `requires_mcp_server`, eventually `requires_bifrost_running`.

---

## 6. What testing cannot guarantee

Honest scope:

1. **Security testing is not security.** Tests can verify the allowlist refuses; they cannot verify the allowlist is *correct* in the operator's threat model. The operator's review is still the boundary.
2. **Property tests find shallow bugs.** A `@given` test that runs 100 random inputs is not exhaustive. It finds the obvious; it misses the adversarial.
3. **Live-backend tests find integration bugs, not architecture bugs.** A pgvector test cannot tell you that pgvector is the wrong choice for the operator's data shape.
4. **No test catches a missing invariant.** If [[50_verification/55_INVARIANT_LIST]] forgets I-NN, the test suite cannot infer it. The invariant list is the source of truth; the tests are the verification.

The implication: testing strategy is *paired* with the invariant list. Without the invariant list, the tests are an unguided expense. Without the tests, the invariants are uninforced.

---

## 7. CI cadence

Hermes appears to run a tiered CI (per RELEASE notes mentioning install-sh, network-prereqs, browser-install tests). The tiers, inferred:

1. **Smoke** — unit tests, ~30s.
2. **Standard** — unit + integration with markers off, ~5 min.
3. **Live** — unit + integration + live-backend, requires service availability, ~10 min.
4. **Stress / E2E** — concurrent + e2e suites, ~30 min.

Ember's slice-2 baseline: 488 tests in 18 seconds. The full suite already runs at smoke-tier speed.

**Recommendation for slice 3:** Continue the marker-based tiering. The whole suite (no markers) is the gate for every commit. The `requires_*` markers are the gate for the acceptance build. Stress tests are nightly.

---

## 8. Test-naming discipline

Hermes's convention: `test_<scenario>_<expected>`. Examples:

- `test_streaming_accumulates_tool_calls_from_non_done_chunk` (matches the bug it fixed)
- `test_allowlist_startup_check_fails_closed`
- `test_pgvector_open_with_extension_missing_*`

Each test name reads as a sentence stating the property under test. Ember already follows this pattern; continue.

---

## 9. What to lift from `tests/agent/` and `tests/gateway/` for reference

When Ember writes the equivalent test for an Ember-lifted pattern, the Hermes test is a useful reference (but not a copy). Specifically:

- `tests/test_tool_guardrails_*` — exact-failure / same-tool-failure / no-progress cases.
- `tests/agent/test_credential_pool.py` — state-machine transitions.
- `tests/agent/test_credential_pool_routing.py` — round-robin / fill-first / least-used strategies.
- `tests/test_redact_*.py` — every pattern matrix.
- `tests/agent/test_curator_backup.py` — snapshot-and-restore.
- `tests/gateway/test_allowlist_startup_check.py` — fail-closed allowlist.
- `tests/test_streaming_*.py` — chunk-boundary scrubber.

Each is in `/tmp/hermes-agent/tests/` for inspection.

---

## What This Means for Ember

**Subsystems affected:** Every True Name. Tests are cross-cutting.

**Vows touched:** All ten. A test that pins an invariant is the *mechanical* form of a Vow (per SYSTEM_VISION §11's pattern of naming the test that enforces each Vow).

**Concrete next steps:**

1. **Land Suite A (slice-3 must-haves) before slice-3 ratification.** Estimated 2,000 LOC of tests; each block is one Hermes-lifted pattern paired with its tests.
2. **For each Hermes pattern lifted: lift its test as a reference; rewrite for Ember's typed-result discipline; commit alongside.** Same commit, same review.
3. **Add the property-based layer (Suite C) at slice 3 if `hypothesis` is acceptable as a dev dependency.** It is small, well-maintained, and adds real signal. Property tests are 5x the bug-find rate of fixture-only tests for the kind of shape-preservation invariants Ember is full of.
4. **Add the chaos layer (Suite D) at slice 4 or when the first stress-fragile pattern lands** (`_SafeWriter`, the credential pool, the streaming scrubber).
5. **Maintain marker discipline.** Slice-2 has it; do not let slice-3 features introduce un-marked live tests.
6. **Write the static-check infrastructure for I-32** (every `sys.exit` near `_log_exit`). A pre-commit hook with a `grep` pattern is the lightest-weight enforcement.
7. **Cross-link every test file to the invariants it pins.** A docstring at the top of each test file: `Pins invariants I-NN, I-NN.` Future contributors find the test from the invariant and vice versa.

Cross-link with [[50_verification/55_INVARIANT_LIST]] (the truth; this doc is the verification), [[50_verification/53_CRASH_PROOFING_PATTERNS]] (the patterns each tested suite covers), [[60_synthesis/64_MIGRATION_PLAN]] (the order tests land relative to features).

A test catches the bug you knew could happen. An invariant catches the bug you forgot to write a test for. Both are required. Together they are the verifier's quiet refusal to be surprised.

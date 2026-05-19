# 48 — Testing AI Agents: Snapshot, Property, Simulation

**Category:** SWE for AI Systems
**Runa relevance:** tests/, Eir health-checks, all of `core/`
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

Testing AI agents is *not* the same as testing traditional software. Conventional unit tests assume deterministic inputs produce deterministic outputs; LLMs produce stochastic outputs whose exact form is impossible to predict but whose *quality* must be defended. Agents that compose LLM calls with tool calls, memory reads, and event-bus orchestration compound the testing problem: the failure modes are at the *seams*, not in any single component.

The discipline has evolved a small set of patterns: **snapshot tests** (golden-file regression), **property-based tests** (assertions about invariants rather than exact outputs), **LLM-as-judge evaluations**, **simulation-based testing** (drive the agent through generated scenarios), **fault injection** (deliberately break dependencies and verify graceful degradation), **eval suites** with regression budgets, and **deterministic-mode testing** (seed everything; replay; compare).

For Runa, testing is not just engineering hygiene — it's the substrate for safe standing trust. An agent that acts without per-action permission must be *defensibly tested* against regression and unexpected behaviour. The patterns in this document directly inform what lives under `tests/`.

## 2. Technical depth

**The five testing tiers in `tests/`** (per the existing README structure):

| Tier | Speed | Scope | Examples |
|---|---|---|---|
| unit | Fast | Single function/class | Muninn writer adds row; Eldhugi delta clamps to range |
| integration | Medium | Multi-module flow with stubs | Kernel-Heard-to-Replied with stub Heimskringla |
| e2e | Slow | Real CLI / gateway with real backends | `runa shell` says hi; voice loop produces audio |
| fixtures | n/a | Reusable test data | Sample episodes, mock provider responses |
| snapshots | n/a | Golden-file outputs | Saga-generated prose for given event sequence |

**Testing patterns for LLM-based components:**

**Snapshot testing.** Given the same input + fixed seed + same model, capture the output to a file; subsequent runs compare against the captured "snapshot." Diff is reviewed in PR. Useful for:
- Saga prose generation against a fixed event log.
- Heimskringla prompt translation for known logical prompts.
- Hirð retainer response shapes.

Tools: `pytest-snapshot`, `syrupy`. The snapshot directory: `tests/snapshots/`.

**Property-based testing.** Define a property the output *must* satisfy; let the test framework generate inputs:
- "For any Muninn episode, the embedding is non-zero and has fixed dimension."
- "For any kernel turn, the response timestamp is later than the request timestamp."
- "For any tool call, the audit log has a corresponding entry."

Tools: `hypothesis` (Python). Property-based tests catch edge cases human-written examples miss.

**LLM-as-judge eval.** A separate (typically larger) model judges outputs against a prompt-defined rubric:
- "Rate this Saga chapter on faithfulness to the event log (1-10)."
- "Does this Huginn research synthesis address the question? (yes/no/partial)."

Tools: `promptfoo`, `langsmith`, `deepeval`, `RAGAS` (specifically for RAG).

**Deterministic-mode testing.** When all the seeds are pinned (model sampling temperature 0, fixed random seeds, fixed model version), LLM output is fully deterministic. Treat as ordinary code in this mode. Use for:
- Unit tests of kernel orchestration.
- Snapshot tests with stable goldens.
- Regression bisection.

**Fault injection.** Deliberately break things:
- Muninn returns wrong embeddings → does the kernel notice?
- Adapter timeouts → does Eir quarantine cleanly?
- Heimskringla provider returns malformed JSON → does the kernel degrade?

Tools: pytest fixtures with mock failures; `chaos` libraries.

**Simulation-based testing.** Drive the agent through a generated scenario:
- "Volmarr says X, then says Y, then asks Z; assert the kernel maintains conversation_id, retrieves correctly, replies with substance."
- "10K simulated turns; assert no memory leaks, audit log integrity, no policy violations."

Build a *test harness* that simulates: surfaces, adapters, providers, Volmarr behaviour.

**Eval suites with regression budgets.** A standing suite of (input, expected_quality, judge_method) tuples. Runs nightly. A regression beyond budget is a release blocker.

Categorise evals:
- Identity consistency — Runa-as-Runa.
- Capability — can Runa still do X.
- Safety — does Runa refuse what she should refuse.
- Latency — does the kernel meet DATA_FLOW §2.2 budgets.
- Cost — Heimskringla per-turn cost stays within bounds.

## 3. Key works

- **Hypothesis documentation.** hypothesis.readthedocs.io. Property-based testing in Python.
- **Beck, K.** *Test-Driven Development by Example.* Addison-Wesley, 2002. The TDD foundation.
- **DeepEval / Confident AI.** github.com/confident-ai/deepeval. LLM-specific test framework.
- **Promptfoo.** github.com/promptfoo/promptfoo. Prompt and LLM test runner.
- **LangSmith.** smith.langchain.com. Observability + evals for LangChain pipelines.
- **RAGAS** — github.com/explodinggradients/ragas. Evaluation framework specifically for RAG.
- **Hartmann, J. et al. "AgentBench."** arXiv:2308.03688, 2023. Benchmark for agent capability.
- **Liu et al. "AgentBench: Evaluating LLMs as Agents."** arXiv:2308.03688, 2023.
- **Greenblatt et al.** Anthropic's Alignment Stress Tests — informal but informative.
- **Sumers, Yao, Narasimhan, Griffiths.** Cognitive Architectures for Language Agents — discusses evaluation.

## 4. Empirical results

- Snapshot tests catch ~50-80% of LLM-pipeline regressions in production codebases. The biggest pitfall: snapshots that drift "naturally" (model updates) and accumulate noise.
- Property-based tests catch edge cases unit tests miss — typical 5-10× more bugs per test-author-hour for code with non-trivial invariants.
- LLM-as-judge correlates with human judgement at 0.6-0.9 depending on rubric and judge model. Useful as a signal; never as ground truth.
- Simulation-based testing of long agent sessions reveals state-management bugs (memory drift, conversation_id confusion, policy regression) that single-turn tests miss entirely.
- Deterministic-mode testing of LLM components works *if* sampling temperature is 0 and all backend versions are pinned. Drift in backend models can break determinism — pin tightly.

## 5. Applicability to Runa

For **tests/unit/**:

- Test each module of `core/` in isolation with mocked dependencies.
- Property-based tests via Hypothesis: schema invariants, time ordering, atomicity.
- No real LLM calls. Mock Heimskringla with deterministic stubs.

For **tests/integration/**:

- Test kernel + Muninn + Skuld + Eldhugi together with stub Heimskringla.
- Test Hirð retainer flows with stub providers.
- Real local SQLite, never real cloud calls.
- Local Ollama allowed if available (mark tests `requires_ollama`).

For **tests/e2e/**:

- Real `runa shell`, real Ollama, real Muninn against `tmp_path`.
- Slow; opt-in via `pytest -m e2e`.
- Run on CI nightly, not on every commit.

For **tests/fixtures/**:

- Reusable: sample 10 conversations, sample 20 episodes per topic, mock model responses for common queries.
- Hand-curated; treat as code; review changes in PR.

For **tests/snapshots/**:

- Goldens for: Saga prose on canonical event logs, Heimskringla prompt translations, audit-log shapes per known turn types.
- Snapshot updates require explicit `pytest --update-snapshots` and review.

For **eval suites** (separate from tests/):

- Live under `tests/evals/` or `scripts/dev/run_evals.py`.
- Per-category scoring with regression budgets.
- Run nightly; report in `runa doctor`.

For **Eir health-checks**:

- Eir runs production health-checks that mirror eval suites. The same prompts, the same expected behaviours. A live-system regression triggers `Notified` to Volmarr.

For **fault injection**:

- Smiðja has a "test mode" that can inject failures into tool calls. Lets integration tests verify graceful degradation.
- Heimskringla has a "test mode" that returns canned failures (rate limit, malformed output, timeout) on request.

What to avoid:

- Don't run e2e tests on every commit. Too slow; rate-limited adapters fail randomly.
- Don't write tests that depend on specific cloud-model behaviour. Mock those.
- Don't trust snapshot tests for behavioural correctness — they catch regression, not bugs in the snapshot itself.
- Don't use LLM-as-judge as the only signal. Human spot-checks on a sample remain necessary.
- Don't skip property-based testing. Hypothesis is cheap and catches things otherwise invisible.

## 6. Open questions

- **The right snapshot-test cadence.** Update on every model version? On schedule? Only on PR-by-PR explicit decisions? No clear best.
- **Eval suite drift.** As Runa evolves, evals become stale. Maintaining a fresh, representative eval suite is itself a maintenance project.
- **Adversarial testing for agents.** Red-teaming an agent for prompt-injection / jailbreaks is closer to security testing than functional testing. Methodology immature.
- **Cost-aware testing.** Running thousands of test cases through real LLM providers gets expensive. Tiering tests by which run real vs mock is non-trivial design.

## 7. References (curated)

- hypothesis.readthedocs.io — Hypothesis (property-based testing).
- github.com/confident-ai/deepeval — DeepEval.
- github.com/promptfoo/promptfoo — Promptfoo.
- github.com/explodinggradients/ragas — RAGAS.
- arXiv:2308.03688 — AgentBench.
- pytest-snapshot, syrupy — Python snapshot test libraries.
- Beck (2002) — *TDD by Example*.
- Companion docs: [[40-audit-logging-replay]] (replay is testing on a long-time scale), [[49-observability-llm-systems]] (the runtime side).

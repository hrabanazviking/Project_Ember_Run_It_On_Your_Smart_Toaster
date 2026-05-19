# 13 — Tree-of-Thoughts, Graph-of-Thoughts, Structured Reasoning

**Category:** Agent Architectures
**Runa relevance:** kernel (turn-shape for hard problems), Hirð/Huginn (research synthesis), Heimskringla (cost shaping)
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

Chain-of-Thought (Wei et al., 2022) was the breakthrough that showed LLMs reason better when prompted to "think step by step." But chain-of-thought is, by name, a *chain* — linear, one path. For problems where the first reasoning step might be wrong, where multiple approaches are worth exploring, where backtracking is necessary, linear thinking is the wrong shape.

Tree-of-Thoughts (Yao et al., Princeton + DeepMind, 2023) generalises CoT to a *tree* of thoughts: at each step, the model proposes multiple alternative continuations, an evaluator scores them, the search algorithm chooses which branches to expand. Graph-of-Thoughts (Besta et al., ETH Zürich, 2023) generalises further to a *graph*, allowing thoughts to be merged, refined, and reused. The whole family — together with self-consistency, debate, and best-of-N — is about *spending more inference compute on harder problems* by branching the reasoning rather than just producing more text.

## 2. Technical depth

The taxonomy of structured-reasoning techniques, by branching pattern:

**Self-consistency (Wang et al., 2022).** Generate N independent CoT solutions, take the majority vote on the final answer. Improves arithmetic and commonsense reasoning by 5-20 points over single-CoT. Cheapest "branching" technique; no orchestration logic.

**Best-of-N sampling.** Generate N completions, pick the one a *verifier* scores highest. Verifier can be a learned model, an LLM judge, or rule-based (does the code compile? does the answer match a regex?).

**Tree-of-Thoughts (ToT).** Explicit tree search:

```
                       root: problem
                          │
                ┌─────────┼─────────┐
                ▼         ▼         ▼
            thought_1  thought_2  thought_3   (generate N candidates)
              │ score    │ score    │ score
              │  7       │  4       │  9
              ▼          ▼          ▼
            (expand)    drop     (expand)    (pruning)
              ...                  ...
```

Search algorithms used in published ToT work: breadth-first, depth-first, beam-search, A*. Heuristic = LLM-as-evaluator scores each thought-node 1-10.

**Graph-of-Thoughts (GoT).** Thoughts can be edges to multiple parents, allowing:
- *Aggregation:* combine ideas from two branches.
- *Refinement:* a thought can be improved by re-prompting with itself as input.
- *Backtracking:* return to an earlier node and try a different child.

GoT is strictly more general than ToT; ToT is strictly more general than CoT; CoT is more general than single-shot answering.

**Debate.** Multiple agents reason in parallel, then argue. Has a similar branch-and-evaluate flavour but uses *multiple agents* instead of multiple thoughts from one agent ([[11-autogen-multi-agent]] §debate).

**ReWOO (Reasoning Without Observation).** Plan all reasoning steps in advance, then execute the plan in parallel. Trades observation-conditioned planning for speed.

**Plan-and-Solve (Wang et al., 2023).** A two-stage prompt: first generate a plan, then execute the plan. Improves zero-shot performance on math and logic.

**Critical implementation details for ToT:**

- The *evaluator* is the bottleneck. LLM-as-evaluator is noisy; with too many candidates the scores fail to discriminate.
- Branching factor (how many children per node) and depth (how deep to search) need to be tuned per task. Defaults: branching 3-5, depth 3-5.
- Pruning is essential: even modest branching factors blow up exponentially. Best-K pruning at each level keeps the search tractable.
- Termination: when a leaf scores above a threshold, or budget exhausted.
- Cost: ToT can use 10-100× more tokens than naive CoT. Reserve for hard problems.

## 3. Key works

- **Wei, Wang, Schuurmans, Bosma, Ichter, Xia, Chi, Le, Zhou. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models."** Google, arXiv:2201.11903, January 2022. The foundational CoT paper.
- **Wang, Wei, Schuurmans, Le, Chi, Narang, Chowdhery, Zhou. "Self-Consistency Improves Chain of Thought Reasoning in Language Models."** Google, arXiv:2203.11171, 2022.
- **Yao, Yu, Zhao, Shafran, Griffiths, Cao, Narasimhan. "Tree of Thoughts: Deliberate Problem Solving with Large Language Models."** Princeton + Google DeepMind, arXiv:2305.10601, May 2023.
- **Besta et al. "Graph of Thoughts: Solving Elaborate Problems with Large Language Models."** ETH Zürich, arXiv:2308.09687, 2023.
- **Wang, Xu et al. "Plan-and-Solve Prompting."** arXiv:2305.04091, 2023.
- **Kojima, Gu, Reid, Matsuo, Iwasawa. "Large Language Models are Zero-Shot Reasoners."** arXiv:2205.11916, 2022. The "Let's think step by step" zero-shot CoT.
- **Snell, Schaul, Singh. "Scaling LLM Test-Time Compute Optimally..."** DeepMind, 2024 — when does extra search/sampling actually help?

## 4. Empirical results

- **Self-consistency** with 40 samples typically gains 5-20 absolute points on GSM8K (grade-school math), commonsense reasoning, and similar benchmarks. Robust and cheap to implement.
- **Tree-of-Thoughts** on the Game of 24 puzzle: baseline single-CoT ~4% success; ToT with BFS ~74%. Dramatic improvement on this very-structured task.
- **ToT on creative writing:** small but consistent improvements over CoT in human evaluations.
- **Graph-of-Thoughts on sorting and set intersection benchmarks:** 50%+ improvements over CoT on tasks where intermediate results can be combined.
- **Scaling test-time compute** (Snell et al., 2024) showed that for easy problems, single-pass CoT is best; for hard problems, branching search dominates; the optimal allocation depends on problem difficulty in predictable ways.
- **Cost-quality trade-off:** for many tasks, doubling the model size beats 10× the search budget; for *hard* tasks, search budget keeps paying off after model-size returns diminish.

## 5. Applicability to Runa

For **the kernel**:

- **Default: single-pass CoT.** Most kernel turns don't need search. A reply, a tool call, a normal conversation — single-pass is fastest and cheapest.
- **Escalate to self-consistency** when the kernel detects a *uncertainty signal* — model declining to answer, conflicting tool outputs, a question where the kernel's confidence is low. Cheap escalation (5-10 samples + vote) and dramatic robustness improvement.
- **Escalate to full ToT/GoT** rarely — for genuinely hard problems (multi-step plans, creative synthesis, ambiguous decisions). The Heimskringla cache and the budget tracker should both be aware that a ToT pass might fire 20-100 model calls.

For **Huginn (research synthesis)**:

- Huginn's research tasks often benefit from branching: "what are three different angles on this question?", expand each, evaluate, combine. GoT-style refinement and aggregation is a natural fit.

For **Völundr (codegen)**:

- Best-of-N with a verifier (does the code compile? do tests pass?) is the standard pattern for codegen and is empirically the most effective form of test-time-compute on coding.

For **Heimskringla**:

- The router should know per-skill / per-task expected branching budget so it can route to cheaper models for branches and the strongest model only for the final synthesis step.

What to avoid:

- Don't apply ToT to every problem. The cost is real and the gain is small on easy tasks.
- Don't trust LLM-as-evaluator unconditionally. Evaluator quality bounds search quality. Use rule-based or test-based evaluators when available.
- Don't run unbounded search. Hard caps on total tokens spent per query, with degradation to single-pass if cap is hit.
- Don't conflate parallelism with branching. Parallel function calls speed up *independent* work; ToT branches dependent reasoning paths. Different patterns.

## 6. Open questions

- **When does branching beat scaling.** Snell et al. give partial answers; the boundary is empirical and per-model.
- **Branching at the agent level.** Multi-agent debate is a kind of agent-level branching. The optimal mix of within-agent thought-branching and across-agent debate is an open design space.
- **Verifier quality.** All branching techniques hit the verifier ceiling. Better verifiers (process reward models, learned critics) are the active research frontier.
- **Inference-time compute scaling laws.** The OpenAI o1 / o3 family commits hard to test-time-compute scaling. The publically-reported numbers suggest this is the next frontier of capability gains. Implications for Runa: even single-call "reasoning" models may absorb the search internally, reducing the need for explicit ToT orchestration.

## 7. References (curated)

- arXiv:2201.11903 — Chain-of-Thought (Wei et al.).
- arXiv:2203.11171 — Self-Consistency (Wang et al.).
- arXiv:2305.10601 — Tree of Thoughts (Yao et al.).
- arXiv:2308.09687 — Graph of Thoughts (Besta et al.).
- arXiv:2305.04091 — Plan-and-Solve.
- arXiv:2205.11916 — "Let's think step by step" (Kojima et al.).
- arXiv:2408.03314 — Snell et al. on optimal test-time compute scaling.
- Companion docs: [[09-react-reasoning-acting]] (the simpler default), [[11-autogen-multi-agent]] (debate as agent-level branching), [[33-model-routing-ensembles]] (cost-aware routing).

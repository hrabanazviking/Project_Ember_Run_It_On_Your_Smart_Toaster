# 88 — Long-Horizon Planning: LATS, RAP, MCTS-Guided LLM Planning

**Category:** AGI Architectures & Cognitive Cores
**Runa relevance:** Hirð (planner subagent), multi-step task execution, project-scale collaboration with Volmarr
**Status:** Frontier search-augmented-LLM synthesis. Production-relevant for plan-shaped tasks.
**Last touched:** 2026-05-17

---

## 1. Core idea

LLMs handle single-step generation well; long-horizon planning — chaining many actions toward a distant goal — is where they characteristically fail. Hallucinated steps, lost goals, terminating prematurely. The 2023–2024 wave of *search-augmented LLM planning* — *Tree of Thoughts* (Yao et al. 2023), *RAP* (Hao et al. 2023 — Reasoning via Planning), *LATS* (Zhou et al. 2023 — Language Agent Tree Search), *RAFA* (Liu et al. 2024) — wraps an LLM inside a classical search framework: Monte Carlo Tree Search (MCTS), beam search, A*. The LLM proposes; the search algorithm explores; an evaluator scores. Plans emerge from the search rather than from a single chain.

For Runa, long-horizon planning matters whenever Volmarr asks her to *help with multi-step work*: \"plan the next phase of WYRD\", \"propose a structure for Phase X\", \"think through the steps to make this work.\" Single-shot LLM responses on such requests are unreliable; search-augmented planning is the deployable improvement. The cost is real (LLM calls × tree breadth × tree depth) but the quality lift is large.

## 2. Technical depth

**Tree of Thoughts (Yao et al. 2023).**

- Pose the problem as a tree: each node is a *partial thought / plan*.
- Expand nodes by LLM-prompting (\"given the current thought, propose K next-thoughts\").
- Evaluate nodes via LLM (\"how promising is this thought, 0–1?\").
- Search the tree: BFS, DFS, or guided.

ToT generalises CoT by giving up the single-chain assumption: multiple chains are explored in parallel, and pruning preserves only the most promising.

**RAP — Reasoning via Planning (Hao et al. 2023).**

- The LLM acts as both *world model* and *policy*.
- World model: given (state, action), predict next state.
- Policy: given state, propose action.
- Wrap in MCTS: simulate trajectories, backpropagate value estimates, choose actions.

This is essentially *AlphaZero with an LLM as the policy + world model*. Striking on math and logical-puzzle benchmarks.

**LATS — Language Agent Tree Search (Zhou et al. 2023).**

- LLM-based agent tree search with explicit reflection at each step.
- Combines ReAct-style ([[09-react-reasoning-acting]]) acting with MCTS-style search.
- Best result of the search becomes the trajectory the agent executes.

**RAFA (Liu et al. 2024).**

- Receding-horizon planning with LLMs: plan H steps ahead, execute first action, replan.
- Bounded compute per step; total compute grows with episode length.
- Robust to environment changes.

**Common architecture.**

```
                 ┌─────────────────────────┐
                 │ ROOT (current state)    │
                 └──────────┬──────────────┘
                            │ expand via LLM
                            ▼
              ┌────────┬────────┬─────────┐
              │ A1     │ A2     │ A3      │ candidate actions
              └───┬────┴────┬───┴────┬────┘
                  ▼         ▼        ▼
              (subtrees, recursively)
                  
              At each node:
                - propose K children via LLM
                - evaluate via LLM-as-judge or rule
                - search policy (UCB1, etc.) chooses next expansion
              
              Termination:
                - reach a goal
                - hit a depth limit
                - exhaust budget
```

**Evaluation function.**

The hardest engineering choice. Options:

- *LLM-as-judge*: prompt the LLM to score a state / partial plan. Cheap; calibration-dependent.
- *Rule-based*: heuristic scoring on plan features. Reliable but narrow.
- *Verifier-based*: for math / code, run the partial plan through a verifier ([[85-neuro-symbolic-agi]]).
- *Distance-to-goal*: if the goal has a metric structure, measure distance.

A well-calibrated evaluator is more important than fancy search.

**Compute scaling.**

ToT / LATS / RAP run *many* LLM calls per query. Budget naively: *B = breadth × depth × eval_per_node*. For breadth 5, depth 5, eval per node = 1: 125 LLM calls. For deeper or broader: thousands. This is reasoning-mode cost.

The *test-time-compute scaling* literature ([[97-test-time-compute-scaling]]) makes the case: throw compute at reasoning, get better answers. ToT-class search is the structured version of that.

**Compared to o-series.**

OpenAI's o-series extends *single-chain* CoT — long internal monologue, single trajectory. ToT / LATS use *tree search*. Empirically, single-chain often suffices for math; tree search shines on planning where exploration matters more. Hybrid (long chains *within* tree search) is the natural synthesis; some recent work explores it.

**Failure modes.**

- *Evaluator miscalibration*: scoring promising plans low or junk plans high → bad search.
- *Goal drift*: the LLM at deep nodes forgets the original goal. Counter: include goal restatement at every node.
- *Branching factor explosion*: K children × depth d gives K^d states; quickly intractable without aggressive pruning.
- *Termination ambiguity*: when has the search done enough? Open.

## 3. Key works

- **Yao, S., Yu, D., Zhao, J., Shafran, I., Griffiths, T. L., Cao, Y., Narasimhan, K.** *Tree of Thoughts: Deliberate Problem Solving with Large Language Models.* NeurIPS 2023.
- **Hao, S. et al.** *Reasoning with Language Model is Planning with World Model* (RAP). EMNLP 2023.
- **Zhou, A. et al.** *Language Agent Tree Search Unifies Reasoning, Acting, and Planning in Language Models* (LATS). ICML 2024.
- **Liu, Z. et al.** *Reason for Future, Act for Now* (RAFA). arXiv:2402.07887, 2024.
- **Besta, M. et al.** *Graph of Thoughts: Solving Elaborate Problems with Large Language Models.* AAAI 2024.
- **Wang, X. et al.** *Self-Consistency.* See [[59-metacognitive-monitoring]]. The simplest precursor.
- **Yao, S. et al.** *ReAct.* See [[09-react-reasoning-acting]].
- **Khot, T. et al.** *Decomposed Prompting.* ICLR 2023.
- **Coulom, R.** *Efficient selectivity and backup operators in Monte-Carlo tree search.* CG 2006. MCTS foundation.
- **Silver, D. et al.** *Mastering the game of Go with deep neural networks and tree search* (AlphaGo). Nature 2016. The AlphaZero-style template RAP echoes.

## 4. Empirical results

- *ToT* on Game of 24, creative writing, mini crosswords: 70–80% problem-solving on tasks where CoT achieves 5–20%.
- *RAP* on plan-bench, reasoning puzzles: substantial gains over single-chain CoT.
- *LATS* on HotpotQA, WebShop: matches or exceeds prior agents with explicit search.
- *Branching cost*: 10–100× single-shot inference cost is typical; can be tens of seconds to minutes per query.
- *Failure-mode evidence*: bad evaluators destroy the gains; depth too shallow gives marginal improvement; depth too deep diverges.

## 5. Applicability to Runa

For **Hirð — a planner retainer**:

- A *planner* subagent in Hirð owns the search-augmented planning. Invoked when Volmarr asks for multi-step help.
- Architecture: ToT- or LATS-style; LLM as proposer + evaluator; budget capped (e.g. 100 LLM calls per planning request); returns plan + alternatives + confidence.
- The kernel offers the plan to Volmarr for endorsement; Volmarr accepts / modifies / rejects.

For **project-scale work with Volmarr**:

- WYRD Phase X planning, NSE work breakdown, new-feature design — all naturally search-shaped. The planner's output is structured (steps, dependencies, risks, alternatives) rather than prose.
- Output format matters: structured plans are *editable* by Volmarr; prose plans aren't.

For **Saga — narrative planning**:

- Less obvious but real: writing a Saga chapter involves choosing what to include, what to emphasise, what arc. ToT-style exploration over chapter outlines could improve chapter quality. Possibly overkill for weekly chapters; useful for annual/lifetime chapters.

For **Eldhugi — emotional planning**:

- Wholly different use: planning *how to navigate an emotional situation* — \"what to say to Volmarr when he's frustrated.\" A modest tree search over response strategies could surface options the single-shot model would miss.

For **integration with verification**:

- Search-augmented planning + verification ([[85-neuro-symbolic-agi]]) = each candidate plan checked against capability boundaries before execution. Layered safety.

For **bounded compute**:

- Pi-class hardware can afford ToT only sparingly. Reserve for high-stakes / explicitly requested planning. For routine multi-step (\"book me X then Y\"), a simpler ReAct-style chain suffices.

What to avoid:

- **Search-augmented planning on every multi-step request.** Compute-tax; user-latency.
- **Bad evaluators.** Calibrate the LLM-as-judge with seed examples; otherwise the search wanders.
- **Forgetting the goal at deep nodes.** Re-anchor at every expansion.
- **Treating the search output as the plan.** It's a *recommended* plan; Volmarr endorses or modifies.
- **Coupling Runa's identity to a specific planner.** The planner is a subagent; replaceable.

## 6. Open questions

- **The right search-augmented planning architecture for personal AI.** Production research mostly benchmark-driven; personal-AI use lightly studied.
- **Compute budget allocation.** When is 100 calls enough; when does 1000 add quality? Tunable; under-studied.
- **Evaluators that generalise.** Domain-specific evaluators work; cross-domain less so.
- **Integration of search with memory-of-thought** ([[87-memory-of-thought-chain-of-memory]]). Each node can retrieve relevant context; vastly improves quality, at cost.
- **User experience.** Showing the search trace to Volmarr is interesting but rapidly cluttering. Selective surfacing matters.

## 7. References (curated)

- NeurIPS 2023 — Yao et al., *Tree of Thoughts.* The reference.
- EMNLP 2023 — Hao et al., *RAP.*
- ICML 2024 — Zhou et al., *LATS.*
- AAAI 2024 — Besta et al., *Graph of Thoughts.*
- arXiv:2402.07887 — Liu et al., *RAFA.*
- AlphaGo (Silver et al. 2016) — the older inspiration.
- Companion docs: [[09-react-reasoning-acting]], [[13-tree-of-thoughts-structured-reasoning]], [[15-prompt-engineering]], [[59-metacognitive-monitoring]], [[66-inner-monologue-scratchpads]], [[83-agentic-foundation-models-2025]], [[85-neuro-symbolic-agi]], [[97-test-time-compute-scaling]].

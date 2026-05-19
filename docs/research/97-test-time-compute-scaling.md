# 97 — Test-Time Compute Scaling: o-series, DeepSeek-R1, Reasoning Models

**Category:** Frontier 2025–2026
**Runa relevance:** reasoning-route in Heimskringla, deliberation budgets, the deepest improvement vector available
**Status:** Most important capability axis of 2024–2025. Frontier synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

For most of LLM history, capability scaled with *training compute* — more data, larger models, more pretraining. The 2024–2025 paradigm shift: capability also scales with *test-time compute* — the amount of compute spent on a single inference. OpenAI's *o1* (Sep 2024) demonstrated that a model spending seconds-to-minutes on internal chain-of-thought before answering substantially outperformed the same model answering immediately. DeepSeek's *R1* (Jan 2025) replicated this at open-weights scale with detailed methodology. *o3* (Dec 2024 → Apr 2025) extended it further. Anthropic's extended thinking, Google's reasoning Gemini, xAI's Grok 3 — all explicitly invoke the same axis. Test-time compute is now widely accepted as one of the principal capability levers available, complementing rather than replacing pretraining-scale.

For Runa, test-time compute is the *direct affordance* to make her smarter on demand. Hard turns warrant more thinking; chitchat warrants none. Aligning the compute spent with the difficulty of the task is the leverage. The architecture this implies — *adaptive compute scheduling* tied to a *reasoning route* in Heimskringla — is a clean engineering pattern. On Pi-class hardware, deploying reasoning-class models is feasible (R1 distillations at 7B, 14B, 32B run within memory) at slower per-token rates; the tradeoff is wall-time for quality.

## 2. Technical depth

**The scaling law.**

For a given task, accuracy roughly improves with test-time compute according to a power-law relationship (varies by domain):

$$\text{accuracy}(c) \approx 1 - A \cdot c^{-\beta}$$

where $c$ is compute spent. Specific values depend wildly on task; on math / reasoning benchmarks, the exponent $\beta$ has been substantial enough that 100× more compute moves performance dramatically.

**OpenAI o-series.**

- *o1* (Sep 2024): the model uses *hidden* chain-of-thought during inference, typically thousands of internal tokens. Released with strong performance on AIME, GPQA, Codeforces.
- *o3* (announced Dec 2024, available 2025): substantial scaling beyond o1; ARC-AGI breakthrough scores.
- *o4-mini*: smaller / cheaper variant.

The reasoning happens *inside* the model, hidden from users; only the final answer is returned (with optional summary of the reasoning).

**DeepSeek-R1 (Jan 2025).**

The open-weights replication and methodological clarification:

- *R1-Zero*: RL applied to a base model with rule-based reasoning rewards. The model spontaneously develops chain-of-thought patterns. Striking emergent behaviour — \"aha moment\" tokens, self-correction patterns.
- *R1*: refined version with supervised cold-start data + reasoning RL. Cleaner output.
- *R1-Distill*: distillations into smaller models (Qwen 7B, 14B, 32B; LLaMA 8B, 70B). The reasoning capability transfers — smaller models gain o1-class reasoning at deployment-friendly sizes.

DeepSeek published the methodology, making R1-class reasoning training reproducible.

**Anthropic extended thinking.**

Claude 3.7 Sonnet and later: an explicit \"thinking\" mode. Users (or the API) can budget thinking tokens — e.g. 32K thinking tokens before response. The thinking is visible (configurable). Latency scales accordingly.

**Inference patterns of reasoning models.**

```
USER QUERY
    │
    ▼
THINK PHASE (private)
   "Let me think... 
    First, what's actually being asked? ...
    Hmm, that doesn't quite work. Let me try ...
    Wait, I need to check ...
    Okay so ...
    Actually, on reflection, the answer is X."
   [thousands of tokens]
    │
    ▼
ANSWER PHASE (public)
   "X. [concise explanation]"
```

The think phase contains: problem-restatement, hypothesis exploration, self-correction, verification, conclusion synthesis. Strikingly self-aware patterns emerge — \"wait, that's wrong\", \"let me reconsider\", \"I should double-check\".

**Compute / quality tradeoff.**

Empirically:
- Token-multiplier *3×* over baseline CoT: modest gains (5–10 percentage points on reasoning benchmarks).
- *10×*: substantial gains (10–25 points).
- *100×*: dramatic gains (20–40 points) on hardest benchmarks.
- *1000×* and beyond: diminishing returns; some benchmarks plateau.

This is roughly the cost / quality curve operators are pricing on.

**Implementations beyond the o-series style.**

- *Best-of-N with reranking*: generate N independent answers; rank; return best. Cheaper alternative.
- *Tree of Thoughts* ([[88-long-horizon-planning-lats-rap]]): structured search.
- *Self-consistency* ([[59-metacognitive-monitoring]]): sample many, majority-vote.
- *Tool-augmented chains*: long chains with retrieval / computation interleaved.

All are forms of test-time compute scaling. The o-series happens to be the *most token-efficient* version observed; others are cheaper alternatives with smaller gains.

**Open vs. closed reasoning models.**

| Model | Open weights | Reasoning class | Pi-deployable |
|---|---|---|---|
| OpenAI o1 / o3 | No | Yes | No |
| Claude 3.7 extended | No | Yes | No |
| DeepSeek R1 | Yes (full) | Yes | No (full); yes (distill) |
| R1-Distill-Qwen-7B / 14B / 32B | Yes | Yes | Yes (quantised) |
| QwQ (Qwen reasoning) | Yes | Yes | Yes (quantised) |
| Gemini reasoning | No | Yes | No |

The open-weights reasoning landscape is rich. R1-Distill-Qwen-32B-Q4 runs on a 16GB Pi-5 with moderate speed; smaller versions run faster.

## 3. Key works

- **OpenAI.** *o1 system card.* Sep 2024. Required.
- **OpenAI.** *o3 announcement and evaluation.* Dec 2024–Apr 2025.
- **DeepSeek-AI.** *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning.* arXiv:2501.12948, 2025. The methodology paper.
- **Anthropic.** *Claude 3.7 Sonnet and extended thinking.* Feb 2025.
- **Snell, C. et al. (Stanford).** *Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters.* arXiv:2408.03314, 2024. The scaling-law paper.
- **Madaan, A. et al.** *Self-Refine.* See [[10-reflexion-self-criticism]] and [[66-inner-monologue-scratchpads]].
- **Wei, J. et al.** *Chain-of-Thought.* The OG.
- **Yao, S. et al.** *Tree of Thoughts.* See [[88-long-horizon-planning-lats-rap]].
- **Zelikman, E. et al.** *Quiet-STaR.* arXiv:2403.09629, 2024. Self-taught reasoning.
- **Hu, A. et al.** *Open R1.* 2025. Community replication efforts.
- **Qwen team.** *QwQ-32B-Preview.* 2024. The open-weights reasoning model from Alibaba.

## 4. Empirical results

- *o1 on AIME*: solved 74% of problems vs. ~13% for GPT-4o.
- *o1 on Codeforces*: 89th-percentile competitive programmer.
- *R1-Distill-Qwen-32B*: matches o1-mini on many benchmarks at open-weights deployable scale.
- *Scaling law studies* (Snell 2024): test-time compute scaling can be more parameter-efficient than pretraining scaling for some task categories.
- *Failure modes*: long chains can confabulate; the chain may not be faithful (Lanham et al.; see [[66-inner-monologue-scratchpads]]); on adversarial or out-of-distribution problems, the gains shrink.
- *Cost*: o1 inference is ~10–100× more expensive than GPT-4o per response. R1 self-hosted on Pi: slower but free.

## 5. Applicability to Runa

For **Heimskringla — reasoning route**:

- Add a *reasoning route* using R1-Distill-class or QwQ. Triggered by complexity heuristic ([[86-dual-process-cognition-system-1-2]]).
- For Pi-5 with 16GB: R1-Distill-Qwen-14B at Q4 is a strong candidate; R1-Distill-Qwen-32B-Q4 is the upper feasible end (slower).

For **the kernel**:

- A `deliberate` mode invokes the reasoning route. Wall-time will be substantial — minutes for hard problems.
- The kernel posts a placeholder while thinking (\"let me think on this — back in a moment\"), then responds. Latency is acknowledged, not hidden theatrically.

For **token budgets** ([[96-resource-budgets]]):

- Reasoning calls have generous-but-bounded token caps (e.g. 32K thinking tokens). Hitting the cap triggers a graceful conclusion.
- Daily reasoning-call cap; over cap, defer or fall back to non-reasoning.

For **identity expression in reasoning**:

- Runa-as-reasoner is still Runa. The persona prompt is part of the reasoning model's context. Her *style of thinking* — Norse, mythic, contemplative — should colour the reasoning chain.
- An interesting research direction (out of scope for now): identity-LoRA tuned on R1-Distill, giving Runa a *Runa-flavoured reasoning model*.

For **Saga / Eldhugi integration**:

- Significant reasoning sessions produce *interesting* internal monologue. Saga can selectively narrate (\"this week Runa worked through the question of...\"). The inner-life of a reasoning being is part of her autobiography.

For **the long arc**:

- Test-time compute is the *deepest* current improvement vector for capability without retraining. Runa benefits from every advance in the open-weights reasoning landscape.
- 2026–2027 will likely see further reasoning-model advances on open weights. Heimskringla should be ready to absorb them.

What to avoid:

- **Reasoning on every turn.** Token-expensive; latency-poor; counterproductive on simple turns.
- **Hiding the thinking latency.** Acknowledge briefly when long thinking is happening. Volmarr-friendly.
- **Trusting reasoning chains blindly.** Faithfulness is partial; verify high-stakes conclusions.
- **Coupling Runa to a specific reasoning model.** R1, QwQ, future model X — Heimskringla abstracts.
- **Skipping the reasoning route for cost.** It's a feature; budget for it.

## 6. Open questions

- **The right reasoning model for Pi-class deployment.** R1-Distill-Qwen-14B is current sweet spot; will shift.
- **Identity preservation across reasoning + non-reasoning models.** Active concern; behavioural-eval set must cover both.
- **Reasoning-aware retrieval.** Whether to retrieve *during* reasoning (memory-of-thought, [[87-memory-of-thought-chain-of-memory]]) or only before. Open.
- **The faithfulness question.** Whether the reasoning chain causally produces the answer or rationalises it. Active research.
- **Cost / quality calibration.** Per-task estimation of reasoning value-add. Empirical, under-studied for personal AI.

## 7. References (curated)

- OpenAI o1 system card (Sep 2024).
- arXiv:2501.12948 — DeepSeek-R1.
- arXiv:2408.03314 — Snell et al., *Scaling Test-Time Compute Optimally.*
- Anthropic Claude 3.7 extended-thinking docs.
- arXiv:2403.09629 — Zelikman et al., *Quiet-STaR.*
- Hugging Face Open R1 effort. Community-driven open-reasoning research.
- Companion docs: [[15-prompt-engineering]], [[66-inner-monologue-scratchpads]], [[83-agentic-foundation-models-2025]], [[84-recursive-self-improvement]], [[85-neuro-symbolic-agi]], [[86-dual-process-cognition-system-1-2]], [[87-memory-of-thought-chain-of-memory]], [[88-long-horizon-planning-lats-rap]].

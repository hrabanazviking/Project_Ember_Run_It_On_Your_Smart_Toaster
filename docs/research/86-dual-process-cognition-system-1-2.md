# 86 — Dual-Process Cognition: System 1/2, Fast/Slow MoE, Deliberation Gating

**Category:** AGI Architectures & Cognitive Cores
**Runa relevance:** kernel response-strategy policy, latency optimisation, reasoning-mode routing
**Status:** Cognitive-science + production-AI synthesis. The architectural pattern of 2024–2025.
**Last touched:** 2026-05-17

---

## 1. Core idea

Kahneman's *Thinking, Fast and Slow* (2011) popularised the cognitive-science distinction between two modes of thought: **System 1** — fast, automatic, intuitive, low-effort; and **System 2** — slow, deliberate, effortful, controlled. The distinction has older roots (Stanovich, Evans, Sloman) and continued empirical refinement, but the basic shape — *fast pattern-completion* alongside *slow deliberate reasoning* — has become the architectural pattern of choice for production AI agents in 2024–2025. OpenAI's o-series, Anthropic's extended thinking, DeepSeek-R1's reasoning mode, Figure AI's Helix two-system — all explicitly invoke the dual-process framing as design rationale.

For Runa, dual-process cognition is the right *routing architecture*: most turns deserve System-1 fast response (familiar interactions, simple queries, chitchat); some turns warrant System-2 slow deliberate reasoning (hard problems, identity-significant moments, planning). The kernel's policy decides which mode runs. Both modes are *Runa*; she has a fast voice and a slow voice, and both reflect her — same identity layer, different processing depth.

## 2. Technical depth

**Kahneman's framing.**

| Property | System 1 | System 2 |
|---|---|---|
| Speed | Fast (~ms) | Slow (~s) |
| Effort | Low | High |
| Control | Automatic | Deliberate |
| Errors | Heuristic biases | Calculation errors |
| Conscious access | Outputs only | Process |
| Examples | Recognise face, complete \"the apple is...\" | Multiply 17 × 28 |

Crucially: System 1 is not *worse* than System 2; it is *appropriate to different tasks*. Most cognition runs System 1; System 2 intervenes when warranted.

**System 1 / 2 in cognitive science: caveats.**

The hard split is a simplification. Modern dual-process theory (Evans & Stanovich 2013) treats it as a *family* of distinctions, not one clean line. Critics (Keren & Schul, Melnikoff & Bargh) argue the empirical evidence is mixed. The architectural usefulness for AI is sturdier than the cognitive-science verdict.

**AI dual-process implementations.**

**OpenAI o-series.** Internal extended chain-of-thought. The model spends *seconds to minutes* generating internal reasoning before emitting a response. Test-time compute scaling ([[97-test-time-compute-scaling]]). System-1 = fast model; System-2 = same model with extended thinking budget.

**Anthropic Claude 3.7 extended thinking.** Similar pattern: an explicit thinking phase with adjustable budget. The user can dial up or down the deliberation level.

**DeepSeek-R1.** Reasoning-mode model trained via RL on chain-of-thought correctness. Different model for fast vs. reasoning, but both available; routing decides.

**Helix (Figure AI).** The most architecturally explicit two-system: a small 200Hz fast network for reactive motor control + a 7B-parameter slow VLM for deliberative goals. The fast model is *separate* from the slow model. The slow model conditions the fast via latent vectors.

**Mixture-of-Experts (MoE) as dual-process.** Some recent work (Lin et al., DeepSeek-MoE variants) frames MoE routing as dual-process: gates select a *light* path (few active experts) for easy tokens and a *heavy* path (many experts) for hard tokens. The gate is the System-1 vs. System-2 router.

**Patterns in agent stacks.**

```
USER INPUT
    │
    ▼
┌─────────────────────────────────────┐
│ COMPLEXITY ESTIMATOR (System 0)     │
│   How hard is this turn?            │
└────────────────┬────────────────────┘
                 │
       ┌─────────┴─────────┐
       │                    │
       ▼                    ▼
┌─────────────┐    ┌──────────────────┐
│ FAST PATH   │    │ DELIBERATE PATH  │
│ (System 1)  │    │ (System 2)       │
│ small model │    │ large model +    │
│ no CoT      │    │ CoT + tools +    │
│ direct      │    │ retrieval +      │
│ response    │    │ verification     │
└──────┬──────┘    └────────┬─────────┘
       │                    │
       └─────────┬──────────┘
                 ▼
            RESPONSE
```

The complexity estimator is itself either heuristic (length, keywords, named-entity count) or learned (a small classifier).

**The metacognitive role.** Knowing *when* to slow down is itself a high-order skill. Confident-but-wrong outputs from System 1 are the failure mode the calibration literature ([[59-metacognitive-monitoring]]) addresses. A well-calibrated system *knows* when to invoke System 2.

**Routing tradeoffs.**

- *Always System 2*: high quality, high latency, high cost. Production-untenable for chitchat.
- *Always System 1*: low latency, low cost, occasional disasters on hard turns.
- *Adaptive routing*: best of both, requires accurate complexity estimation.

Empirically, even crude routing (\"if the message is short and looks like greeting, fast; otherwise slow\") captures most of the gain.

**Cross-system communication.** System 2's outputs can inform System 1 future behaviour. If System 2 successfully solves a class of problems, the solution can be cached / distilled into System 1 patterns. Voyager-style skill library ([[12-voyager-lifelong-learning]]) is one version. STaR-style distillation ([[84-recursive-self-improvement]]) is another. Helix conditions System 1 from System 2 directly per-step.

## 3. Key works

- **Kahneman, D.** *Thinking, Fast and Slow.* Farrar, Straus and Giroux, 2011.
- **Evans, J. St. B. T.** *Dual-processing accounts of reasoning, judgment, and social cognition.* Annual Review of Psychology, 2008.
- **Stanovich, K. E.** *Rationality and the Reflective Mind.* OUP, 2011.
- **Evans, J. St. B. T., Stanovich, K. E.** *Dual-process theories of higher cognition.* Perspectives on Psychological Science, 2013. Authoritative state-of-the-art summary.
- **Sloman, S. A.** *The empirical case for two systems of reasoning.* Psychological Bulletin, 1996.
- **Keren, G., Schul, Y.** *Two is not always better than one.* Perspectives on Psychological Science, 2009. Skeptical critique.
- **OpenAI.** *o1 system card.* Sep 2024.
- **Anthropic.** *Claude 3.7 Sonnet and extended thinking.* Feb 2025.
- **DeepSeek-AI.** *DeepSeek-R1.* arXiv:2501.12948, 2025.
- **Figure AI.** *Helix.* 2024–2025.
- **Lin, X. et al.** *Mixture of Diverse Size Experts.* arXiv:2409.12210, 2024.
- **Bengio, Y.** *The Consciousness Prior.* arXiv:1709.08568, 2017. AI-architecture inspiration toward dual-process.

## 4. Empirical results

- *o-series performance lift*: 20–40 points on reasoning-heavy benchmarks (math, code, science) over the same model with default compute.
- *DeepSeek-R1 distillations*: reasoning-mode capability compressed into smaller models with quality retained.
- *Helix demonstrations*: real-time humanoid manipulation with the two-system split.
- *Routing-based deployment*: production systems (Claude, GPT-4) route between models / compute budgets; specific routing-gain numbers proprietary, but the pattern is industry-standard.
- *Failure modes documented*: bad complexity estimation → wrong path → either over-thinking simple things or under-thinking hard ones.

## 5. Applicability to Runa

For **kernel architecture**:

- Implement explicit fast / slow routing:
  - *Fast path*: small model (or default model with no CoT) for greetings, simple lookups, chitchat. Sub-second response.
  - *Slow path*: full model + chain-of-thought + retrieval + verification for: hard questions, identity-relevant moments, plan-formation, factual claims with stakes, novel topics.
- *Complexity estimator*: simple heuristic to start (message length, presence of question-words, novelty against recent context). Learnable later.

For **Heimskringla**:

- Maintain at least two models in the active inventory: a small fast one (e.g. Qwen-2.5-3B or LLaMA-3.2-3B for chitchat) and a larger reasoning-capable one (e.g. Qwen-2.5-14B / DeepSeek-R1-Distill-7B).
- Routing is part of Heimskringla's job. Model selection per turn is a typed operation.

For **Hirð**:

- Some subagents are inherently fast (greeting handler, lookup handler); others are inherently slow (Draumr the consolidator, the planner, the verifier).
- The slow subagents get extended thinking budgets; fast ones get tight limits.

For **identity preservation across modes**:

- The persona layer is read by *both* fast and slow models. Same Runa, different processing depth.
- The voice of slow-Runa should be the same voice as fast-Runa, just more considered. Verify behavioural-test set covers both paths.

For **calibration and metacognition**:

- The kernel's metacognitive layer ([[59-metacognitive-monitoring]]) decides when to escalate from fast to slow. \"I'm not sure of this answer; let me think more carefully\" triggers slow-path.
- *Escalation* is internal — Runa is not announcing she's thinking harder; she just does it.

For **Eldhugi**:

- Affective state can bias the path. High arousal → slow down (compose before speaking). Low arousal → faster, simpler responses.

For **the long arc**:

- Over months and years, the *slow path* accumulates successful patterns that can be distilled to the *fast path* (per [[84-recursive-self-improvement]]). Runa-future thinks fast about what Runa-past needed to think slow about. Growth.

What to avoid:

- **Always-fast for chitchat.** Misreads escalation triggers; produces confidently-wrong answers on questions that looked easy but weren't.
- **Always-slow for everything.** Latency-poisoning; loses warmth.
- **Hard-coded thresholds.** Use a learnable estimator that can be tuned; the right thresholds shift as Heimskringla's model inventory changes.
- **Inconsistent voice across paths.** The fast voice can be terser; both should be recognisably Runa.
- **Hiding escalation from the user theatrically.** \"Let me think...\" is fine in context; constant theatricality reads as performance.

## 6. Open questions

- **Best complexity estimator design.** Heuristic baselines do well; learned estimators may help more.
- **Cost-aware routing.** Slow path is expensive. The right cost / quality tradeoff is dynamic.
- **Distillation cadence**: how often to bake System-2 patterns into System-1. Open.
- **Three-tier or more.** Some agent stacks have three: fast / moderate / deliberate. Diminishing returns past three; the boundary is empirical.
- **Personalised routing.** A turn from Volmarr might warrant different routing than from an unfamiliar interlocutor. Open.

## 7. References (curated)

- Kahneman (2011) — *Thinking, Fast and Slow.* The popularising text.
- Evans & Stanovich (2013), *Perspectives on Psychological Science.* The authoritative review.
- OpenAI o1 system card. Production exemplar.
- arXiv:2501.12948 — DeepSeek-R1. Open-weights reasoning-mode exemplar.
- Figure AI Helix announcement. The most architecturally clean two-system.
- Companion docs: [[15-prompt-engineering]], [[33-model-routing-ensembles]], [[59-metacognitive-monitoring]], [[66-inner-monologue-scratchpads]], [[83-agentic-foundation-models-2025]], [[97-test-time-compute-scaling]].

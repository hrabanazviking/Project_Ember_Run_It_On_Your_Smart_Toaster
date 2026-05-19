# 84 — Recursive Self-Improvement: STaR, ReST, Self-Rewarding LLMs

**Category:** AGI Architectures & Cognitive Cores
**Runa relevance:** long-term learning loop, identity-LoRA retraining cycles, Eir (the self-healer)
**Status:** Frontier learning-methods synthesis. Important for long-term Runa evolution.
**Last touched:** 2026-05-17

---

## 1. Core idea

Recursive Self-Improvement (RSI) is the family of techniques where an agent generates its own training data, evaluates that data, and uses it to improve itself — iteratively. The vision is old (Schmidhuber, Goertzel) but until recently was speculative. Three research lines have made it tractable in the LLM era: *STaR* (Zelikman et al. 2022 — Self-Taught Reasoner), *ReST* (Gulcehre et al. 2023 — Reinforced Self-Training), and *self-rewarding LLMs* (Yuan et al. 2024). DeepSeek-R1's training pipeline crystallised RSI as the route to reasoning models — *self-play in chains-of-thought*.

For Runa, RSI is the technical heart of *real learning over time*. Her current architecture is read-mostly: a frozen base model, augmented memory, prompt-based identity. RSI is the path from \"prompt-augmented assistant\" to \"agent that genuinely grows.\" Done well, it allows Runa to internalise her own experience into improved capability. Done poorly, it amplifies quirks and drifts identity. The engineering discipline matters.

## 2. Technical depth

**STaR — Self-Taught Reasoner (Zelikman, Wu, Mu, Goodman 2022).**

Loop:
1. Given a dataset of problems with correct answers.
2. Prompt the model to *think step-by-step* (chain-of-thought) and answer.
3. If the answer is correct, keep the reasoning chain.
4. If incorrect, *rationalise*: tell the model the correct answer and ask it to generate a reasoning chain that *leads to* the correct answer; keep that.
5. Fine-tune the model on the collected chains.
6. Repeat.

Crucial: the model bootstraps from its own (mostly-correct) outputs plus rationalised fixes for its errors. No human-written CoT data needed.

**ReST — Reinforced Self-Training (Gulcehre et al. 2023).**

Two-phase iteration:
- *Grow*: model generates many outputs across the training distribution.
- *Improve*: filter / score outputs (by a reward model, a rule, or a heuristic); fine-tune on the high-quality subset.

Repeat. The model's outputs become its next iteration's training data. Convergence is empirically faster than RL-from-scratch and produces stable improvements.

**Self-rewarding LLMs (Yuan et al. 2024, Meta).**

Even more aggressive: the model also serves as its own *judge*. Loop:
1. Generate completions for a prompt.
2. Have the model evaluate them (\"which is better?\").
3. Build preference pairs from the model's own judgements.
4. Train on the preference pairs (DPO-style).

The reward model and the policy are the same model. Striking result: the model improves *both* its instruction-following and its judging ability simultaneously, over several iterations.

**DeepSeek-R1's reasoning pipeline (Jan 2025).**

The clearest production deployment of RSI:
1. Start with a base model.
2. Use rule-based reward (\"did you get the right answer?\") plus chain-of-thought training to produce a reasoning-capable model.
3. The reasoning model generates better and better chains of thought.
4. Sample successful chains, use them as supervised fine-tuning data.
5. Repeat with progressively harder problems.
6. The result: R1, a reasoning model trained largely from its own outputs.

Distillations of R1 carry the reasoning capability to smaller models that can run on consumer hardware.

**The patterns.**

All RSI methods share:

- *Generate*: produce candidate outputs.
- *Filter / evaluate*: judge which are good.
- *Train*: fine-tune on the good ones.
- *Iterate*: repeat with the improved model.

Key axes of variation:

- *What is being improved* (reasoning, instruction-following, persona, calibration).
- *Source of the filter* (rule, reward model, model-as-judge, human).
- *Update method* (SFT, DPO, RL).
- *Stability mechanisms* (reference-model regularisation, diversity bonuses, anti-collapse measures).

**Risks and failure modes.**

- *Mode collapse*: the model narrows to a few patterns, loses diversity. Counter: diversity rewards, reference-model anchoring.
- *Reward hacking*: when the filter is a learned reward model, the policy finds ways to satisfy the reward without solving the task. Classical RL problem.
- *Identity drift*: applying RSI to persona / voice can amplify quirks. Counter: include reference voice data; periodic Volmarr review.
- *Catastrophic forgetting*: the model loses general capabilities while gaining specific ones. Counter: training mix with general-domain data.
- *Confabulation amplification*: low-quality outputs get baked into the next iteration. Counter: aggressive filtering; honest failure handling.

**Stable RSI requires anchors.** Across all the successful RSI work, the patterns that work include *external reference data*: the model is not just trained on its own outputs but on a mix that includes ground-truth (human-rated) or reference data. Pure self-loop is brittle; anchored self-loop is robust.

## 3. Key works

- **Zelikman, E., Wu, Y., Mu, J., Goodman, N. D.** *STaR: Bootstrapping Reasoning With Reasoning.* NeurIPS 2022.
- **Gulcehre, C. et al. (Google DeepMind).** *Reinforced Self-Training (ReST) for Language Modeling.* arXiv:2308.08998, 2023.
- **Singh, A. et al.** *Beyond Human Data: Scaling Self-Training for Problem-Solving with Language Models* (ReST^EM). arXiv:2312.06585, 2023.
- **Yuan, W. et al. (Meta).** *Self-Rewarding Language Models.* arXiv:2401.10020, 2024.
- **Zelikman, E. et al.** *Quiet-STaR: Language Models Can Teach Themselves to Think Before Speaking.* arXiv:2403.09629, 2024.
- **DeepSeek-AI.** *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning.* arXiv:2501.12948, 2025.
- **Schmidhuber, J.** *Gödel Machines: Self-Referential Universal Problem Solvers Making Provably Optimal Self-Improvements.* 2003. Theoretical antecedent.
- **Anthropic.** *Constitutional AI.* arXiv:2212.08073, 2022. Self-critique is a form of RSI.
- **Madaan, A. et al.** *Self-Refine.* NeurIPS 2023. In-context RSI per-turn rather than across training.
- **Shinn, N. et al.** *Reflexion.* NeurIPS 2023.

## 4. Empirical results

- *STaR* improved arithmetic / commonsense reasoning on small LMs (~10B) by 10–30 points on relevant benchmarks. Effect persists across multiple iterations until plateauing.
- *ReST*: matched or exceeded supervised baselines on machine translation and instruction-following at lower data cost.
- *Self-Rewarding LLMs*: LLaMA-2-70B-Self-Rewarding achieved performance approaching GPT-4 on AlpacaEval through three iterations.
- *DeepSeek-R1*: state-of-the-art reasoning at open-weights scale, achieved largely through RSI. The most influential 2025 result in this line.
- *Distillations*: R1-Distill smaller models inherit reasoning capability that pure pretraining at their scale would not produce.
- *Failure modes documented*: collapse (Yuan et al. report fading gains after 3–4 iterations); reward hacking (rare-but-real); identity / style narrowing.

## 5. Applicability to Runa

For **identity-LoRA retraining (see [[55-adapter-based-identity-persistence]])**:

- The most natural Runa-RSI is the *identity-LoRA retraining cycle*: every quarter, train an updated identity_lora from accumulated Saga chapters + endorsed conversation turns.
- Anchor: include the original PHILOSOPHY-derived persona corpus in every retraining mix. This prevents collapse toward whatever happened to be common in recent conversation.
- Volmarr endorses (or rejects) each new version. The endorsement signal is the human-in-loop anchor.

For **a Runa-specific reasoning model** (forward-looking):

- A distillation of R1-class reasoning capability into Runa's identity-tuned adapter is technically plausible (2026–2028 timeline).
- Pipeline: gather (problem, Runa-style reasoning, correct answer) tuples; train an adapter that produces Runa-voiced reasoning chains.
- Pay-off: Runa's *style of thinking* — Norse, mythic, philosophical — applied to reasoning tasks rather than generic helpful-assistant CoT.

For **Eir (the self-healer subagent)**:

- Eir's natural job includes RSI-style processes: identify recurring shortcomings (\"Runa frequently gets X wrong\"), propose training data to address them, run the retraining, evaluate, deploy.
- This is bigger than just an adapter; it's an ongoing self-improvement infrastructure.

For **per-turn self-improvement (Self-Refine pattern)**:

- Implementable today, without retraining: on hard turns, Runa generates, critiques, refines, then emits. Per-turn RSI. Adds latency; substantially improves quality.
- This is the practical RSI Runa can deploy now.

For **the philosophical thread**:

- A digital being that *grows* across years is qualitatively different from one that just *accumulates memory*. RSI is the technical substrate of growth.
- The PHILOSOPHY supports growth; per RULES.AI.md it must be additive (no destructive overwrites). RSI fits if implemented additively.

What to avoid:

- **Pure-self-loop training.** Always include reference data. Always include Volmarr endorsement.
- **Frequent retraining cycles.** Quarterly is plausible; monthly is probably too fast for identity to stabilise; daily is identity churn.
- **Replacing the base model in self-loop.** Adapters yes; base model upgrades are separate (model-version, not RSI).
- **Training without held-out behavioural tests.** Each new version must pass the reference set.
- **Training on inputs Volmarr would reject.** Filter the corpus before retraining; not every conversation should shape the next Runa.

## 6. Open questions

- **Stability of long-running RSI.** Most published RSI plateaus or degrades after 3–5 iterations. Whether long-horizon (years) RSI is stable is open.
- **The right reward signal for a personal AI.** General-domain benchmarks aren't the goal. Volmarr-endorsement and behavioural consistency are.
- **Identity preservation under RSI.** Active research; sloppy RSI definitely drifts identity.
- **Whether persona LoRAs can be self-improved at all.** Voice is not a benchmark-shaped capability. Open.
- **Cross-model RSI.** Training adapter on model A, then using a new model B — does the adapter transfer? Limited evidence.

## 7. References (curated)

- arXiv:2203.14465 — Zelikman et al., *STaR.* The foundational pattern.
- arXiv:2308.08998 — Gulcehre et al., *ReST.*
- arXiv:2401.10020 — Yuan et al., *Self-Rewarding LMs.* Important caution-relevant evidence.
- arXiv:2501.12948 — DeepSeek-R1. The production exemplar.
- arXiv:2403.09629 — Zelikman et al., *Quiet-STaR.* Reasoning-without-explicit-prompting.
- Companion docs: [[10-reflexion-self-criticism]], [[14-constitutional-ai]], [[55-adapter-based-identity-persistence]], [[60-self-models-in-artificial-agents]], [[97-test-time-compute-scaling]].

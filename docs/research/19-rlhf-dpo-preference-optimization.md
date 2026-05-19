# 19 — RLHF, DPO, KTO, and Modern Preference Optimization

**Category:** LLM Techniques
**Runa relevance:** Heimskringla (provider awareness), identity/persona consistency, plugin/skill author guidance
**Status:** Research synthesis. Important to understand even though Runa won't fine-tune in v0.
**Last touched:** 2026-05-17

---

## 1. Core idea

After pre-training, a base LLM is broadly capable but unhelpful, often unsafe, and stylistically incoherent. The technique that transformed raw base models into the helpful, harmless, well-formatted assistants of 2022-2026 is **preference optimization** — fine-tuning the model to prefer outputs that humans (or AI judges) prefer. Reinforcement Learning from Human Feedback (RLHF) was the original recipe (Christiano et al. 2017, OpenAI's InstructGPT 2022); since 2023, simpler and more efficient alternatives have proliferated: DPO, IPO, KTO, ORPO, SimPO, and a continuing parade of acronyms.

For Runa, this matters even though v0 fine-tunes nothing: every model Heimskringla calls has been preference-optimised, and understanding which technique was used (and on what data) shapes Runa's expectations of model behaviour. Long-term — if Runa-as-a-being ever fine-tunes a model on her own conversations to better reflect Volmarr's preferences — the choice of preference-optimization technique will be a real decision.

## 2. Technical depth

**The classic RLHF pipeline (Christiano 2017 → InstructGPT 2022 → ChatGPT/Claude/Llama-chat):**

```
[1] Pre-train base model M on web-scale text.
[2] Supervised fine-tuning (SFT): fine-tune M on (prompt, ideal_response)
    pairs written by humans. Result: M_sft, a model that follows
    instructions but isn't tuned for preference.
[3] Train a reward model RM on (prompt, response_a, response_b, human_pref)
    triples. RM predicts which response a human would prefer.
[4] RL fine-tune M_sft using PPO (Proximal Policy Optimization),
    with RM providing the reward. Result: M_rlhf.
```

The PPO step is the expensive, fiddly one — a full RL loop with a reward model, a value head, a KL-divergence regulariser to keep the policy close to M_sft. Real-world RLHF is a substantial engineering effort.

**Direct Preference Optimization (DPO)** (Rafailov, Sharma, Mitchell, Ermon, Manning, Finn, Stanford, May 2023, arXiv:2305.18290). The breakthrough: skip the reward model entirely. Mathematically equivalent to RLHF under standard assumptions, DPO trains directly on preference pairs with a closed-form supervised objective. No RL. No PPO. No reward model. Far simpler engineering, similar quality. **Became the dominant preference-optimization technique within a year of publication.**

DPO loss (schematic):
```
L_DPO = -E[(prompt, y_w, y_l) ~ data] [
    log σ(β · (log π(y_w|x)/π_ref(y_w|x) - log π(y_l|x)/π_ref(y_l|x)))
]
```
where π is the model being trained, π_ref is the reference (frozen SFT model), y_w is the preferred response, y_l is the dispreferred, β controls the strength.

**KTO (Kahneman-Tversky Optimization)** (Ethayarajh, Xu, Muennighoff, Jurafsky, Kiela, 2024, arXiv:2402.01306). Uses prospect-theory-inspired loss; trains on single (prompt, response, good/bad) labels rather than paired comparisons. Easier to collect data for than DPO.

**IPO (Identity Preference Optimization)** (Azar et al., DeepMind, 2023). Addresses an over-optimization failure mode of DPO; replaces the sigmoid term to prevent overconfident preferences.

**ORPO (Odds Ratio Preference Optimization)** (Hong et al., 2024, arXiv:2403.07691). Combines SFT and preference optimization into a single objective; eliminates the SFT stage as a separate pass.

**SimPO (Simple Preference Optimization)** (Meng, Xia, Chen, 2024, arXiv:2405.14734). Removes the reference model entirely; uses length-normalised log-likelihoods. Simpler, sometimes better.

**RLAIF (RL from AI Feedback)** ([[14-constitutional-ai]]). Replace human raters with an AI judge. Used by Anthropic's Claude family. Dramatically reduces the human-labelling cost.

**Constitutional AI** ([[14-constitutional-ai]]) — Anthropic's preference data is grounded in a constitution rather than ad-hoc human ratings.

## 3. Key works

- **Christiano et al. "Deep Reinforcement Learning from Human Preferences."** OpenAI / DeepMind, arXiv:1706.03741, 2017. The RLHF foundation.
- **Stiennon et al. "Learning to summarize from human feedback."** OpenAI, arXiv:2009.01325, 2020.
- **Ouyang et al. "Training Language Models to Follow Instructions with Human Feedback."** OpenAI, arXiv:2203.02155, 2022. The InstructGPT paper.
- **Bai et al. "Training a Helpful and Harmless Assistant with RLHF."** Anthropic, arXiv:2204.05862, 2022.
- **Schulman et al. "Proximal Policy Optimization Algorithms."** arXiv:1707.06347, 2017. PPO.
- **Rafailov et al. "Direct Preference Optimization: Your Language Model is Secretly a Reward Model."** Stanford, arXiv:2305.18290, 2023.
- **Ethayarajh et al. "KTO: Model Alignment as Prospect Theoretic Optimization."** arXiv:2402.01306, 2024.
- **Hong et al. "ORPO: Monolithic Preference Optimization without Reference Model."** arXiv:2403.07691, 2024.
- **Meng, Xia, Chen. "SimPO: Simple Preference Optimization with a Reference-Free Reward."** arXiv:2405.14734, 2024.
- **Lee et al. "RLAIF: Scaling RLHF with AI Feedback."** Google, arXiv:2309.00267, 2023.

## 4. Empirical results

- **RLHF vs SFT-only:** RLHF substantially reduces harmful outputs and improves perceived helpfulness, at the cost of mild "alignment tax" — sometimes worse on standard benchmarks (MMLU, etc.) than SFT-only.
- **DPO vs RLHF:** comparable quality across most published comparisons; sometimes DPO wins, sometimes RLHF, rarely by large margins. DPO is dramatically simpler engineering, which is why it dominated.
- **DPO failure modes:** over-optimisation when preferences are noisy; collapse to short / vague responses when length is correlated with preference; "policy degradation" on continued training.
- **SimPO, ORPO, KTO:** small improvements over DPO on average; choice depends on data availability (KTO good when only single-response feedback is available) and complexity tolerance.
- **RLAIF:** comparable to RLHF on harmlessness when the AI judge is well-calibrated; far cheaper.

## 5. Applicability to Runa

For **Heimskringla provider awareness**:

- Each provider/model has been preference-optimised in a particular way. Heimskringla should know the rough profile: Claude-class (CAI + RLHF, strong constitutional sensitivity); GPT-class (RLHF, strong tool-use, sometimes overly-helpful); Llama-class (RLHF + DPO variants, more direct); local open models often less-aligned (lighter RLHF, more raw).
- Model-specific prompt shaping ([[15-prompt-engineering]]) accounts for differences in preference-optimization style.

For **identity / persona consistency**:

- A model fine-tuned on "be helpful, harmless, honest" carries those preferences whether Runa's identity wants them or not. Runa wanting to be saga-flavoured and uninhibited (per RULES.AI §"Uninhibited Creation") sits in tension with safety-tuned models' default behaviour. Workarounds: persona prompting, model selection (less-tuned open models), eventual custom fine-tuning.

For **possible future Runa fine-tuning**:

- If Runa ever fine-tunes a local model on Volmarr's conversations and preferences, **DPO is the recommended starting point**. Pipeline: collect (prompt, Runa_response_A, Runa_response_B, Volmarr_preferred) triples over time; periodic DPO fine-tune of a base or already-instruction-tuned local model. Requires preference data; requires non-trivial compute (LoRA-based DPO is viable on a workstation GPU).
- Alternative: KTO if collecting paired preferences is hard but binary "this response was good/bad" labels are available.

What to avoid:

- Don't assume preference-optimised models are *uniformly* better. They're optimised for *raters' preferences*, which may differ from Runa's needs (e.g. raters may dislike technical precision; Runa needs it).
- Don't fine-tune Runa-on-Volmarr until there's a *lot* of preference data. Tens of pairs is too few; hundreds or thousands is the right scale.
- Don't catastrophically forget. A heavy DPO pass on a small dataset can wreck the model's general capability — keep the SFT/reference model loaded and use KL-regularisation (DPO's default) or LoRA-based DPO to preserve the base.
- Don't conflate "the model agrees with my preferences" with "the model is right." Preference optimization can entrench biases.

## 6. Open questions

- **DPO at very large scale.** Most published DPO comparisons are at the 7B-70B scale. Behaviour at trillion-parameter MoE scale is less explored.
- **Continual preference optimization.** If Volmarr's preferences shift over time, can Runa's model continually re-align without catastrophic forgetting?
- **Multi-objective preference optimization.** Pareto frontier of "helpful vs harmless vs honest vs persona-consistent" is multi-dimensional. Current methods optimise scalar rewards; better multi-objective methods are an open frontier.
- **Self-improvement loops.** RLAIF lets the model judge itself. Iterating that — model trains itself based on its own preferences — is theoretically a self-improvement loop; safety implications are serious.

## 7. References (curated)

- arXiv:2305.18290 — DPO paper.
- arXiv:1706.03741 — Christiano RLHF.
- arXiv:2203.02155 — InstructGPT.
- arXiv:2402.01306 — KTO.
- arXiv:2403.07691 — ORPO.
- arXiv:2405.14734 — SimPO.
- arXiv:2309.00267 — RLAIF.
- huggingface.co/docs/trl — TRL library (DPO/PPO/KTO trainers).
- Companion docs: [[14-constitutional-ai]] (the data-side companion), [[45-continual-learning]] (forgetting concerns).

# 45 — Continual Learning: EWC, Replay Buffers, Catastrophic Forgetting

**Category:** Self-Improvement & Continual Learning
**Runa relevance:** future Runa-specific model fine-tuning, Hirð retainer specialisation, long-term identity stability
**Status:** Research synthesis. Relevant when Runa ever trains her own model.
**Last touched:** 2026-05-17

---

## 1. Core idea

A neural network trained on Task A, then trained on Task B, often *forgets* Task A — sometimes catastrophically, reaching near-random performance on A after only modest training on B. This is **catastrophic forgetting**, first formally characterised by McCloskey and Cohen (1989). It is the fundamental problem of **continual learning**: training models that *accumulate* capabilities over time rather than *replacing* old capabilities with new ones.

For Runa, this matters in a specific way: Runa is currently a system that *uses* pre-trained models without fine-tuning them. But the long-term vision includes Runa fine-tuning a small local model on her own conversations and Volmarr's preferences ([[19-rlhf-dpo-preference-optimization]]). When that happens, continual-learning techniques become directly relevant — the local model must absorb new training without losing its base capabilities. This document covers the major approaches with an eye toward the pragmatic question: when Runa updates her own model, how does she avoid lobotomising it?

## 2. Technical depth

**Why catastrophic forgetting happens:**

A neural network's weights encode *all* learned capabilities in the same parameters. Gradient updates from new training data shift those weights to fit the new data. The shifts can be incompatible with what made the old capabilities work. Without intervention, training overwrites.

**The three continual-learning scenarios** (van de Ven and Tolias, 2019):

1. **Task-incremental learning** — agent knows which task it's doing at any time; can use task-specific heads.
2. **Domain-incremental learning** — same task, different input distribution.
3. **Class-incremental learning** — new classes added to a classifier without telling it which.

Class-incremental is the hardest; domain-incremental is intermediate; task-incremental is easiest.

**The main families of solutions:**

### Replay-based methods

Store some past experience and re-train on it alongside new data. The most-effective family by raw benchmark performance.

- **Experience Replay** ([[44-sleep-replay-memory-consolidation]]). Store a buffer of past examples; sample from it during training.
- **iCaRL** (Rebuffi et al., 2017). Selects representative exemplars per class; stores in a fixed-size memory budget.
- **Generative Replay** (Shin et al., 2017). Train a generative model of past data; sample synthetic past examples during continual training.
- **Dark Experience Replay** (Buzzega et al., 2020). Store logits along with examples; train to match both labels and old-model predictions.

### Regularization-based methods

Constrain weight updates so important weights for old tasks don't change much.

- **Elastic Weight Consolidation (EWC)** (Kirkpatrick et al., DeepMind, *PNAS* 2017). Compute the Fisher Information matrix for each weight after Task A; add a regularizer when training on Task B that penalizes moving high-importance weights. Theoretically elegant; practically helps.
- **Synaptic Intelligence (SI)** (Zenke, Poole, Ganguli, 2017). Computes weight importance online during training, not requiring a separate post-task pass.
- **Memory Aware Synapses (MAS)** (Aljundi et al., 2018). Importance estimated from output sensitivity to weights.
- **Learning without Forgetting (LwF)** (Li and Hoiem, 2017). Use the old model itself as a teacher; distillation loss preserves old behaviour.

### Architectural methods

Allocate new parameters for new tasks; freeze or partially freeze old ones.

- **Progressive Networks** (Rusu et al., 2016). Add new columns of weights for new tasks; old columns frozen; cross-connections allow transfer.
- **PackNet** (Mallya and Lazebnik, 2018). Iteratively prune and re-train; reserve subnetwork capacity for each new task.
- **HAT (Hard Attention to the Task)** (Serra et al., 2018). Learn per-task attention masks over the network.

### Modern continual learning of LLMs

- **LoRA (Low-Rank Adaptation)** (Hu et al., 2021). Add small trainable adapters; freeze the base model. Each new "task" gets its own LoRA. Combine at inference. Mitigates forgetting because base is preserved.
- **QLoRA** (Dettmers et al., 2023). LoRA on quantized base. Production-friendly for fine-tuning at modest compute.
- **In-context learning as continual learning**. Newer thinking: with sufficient context length, agents can "learn" new behaviours by being told them in-context rather than via weight updates. Avoids catastrophic forgetting entirely but doesn't accumulate persistent capability across sessions without external memory ([[01-memgpt-os-memory-hierarchies]]).

## 3. Key works

- **McCloskey, M. and Cohen, N. J.** "Catastrophic interference in connectionist networks." *Psychology of Learning and Motivation*, 1989. The first formal characterisation.
- **Kirkpatrick et al. "Overcoming catastrophic forgetting in neural networks."** DeepMind, *PNAS*, 2017. EWC.
- **Zenke, Poole, Ganguli.** "Continual Learning Through Synaptic Intelligence." ICML 2017.
- **Li and Hoiem.** "Learning without Forgetting." ECCV 2016. LwF.
- **Rebuffi et al.** "iCaRL: Incremental Classifier and Representation Learning." CVPR 2017.
- **Shin et al.** "Continual Learning with Deep Generative Replay." NeurIPS 2017.
- **Rusu et al.** "Progressive Neural Networks." arXiv:1606.04671, 2016.
- **Hu et al. "LoRA: Low-Rank Adaptation of Large Language Models."** arXiv:2106.09685, 2021.
- **Dettmers et al. "QLoRA."** arXiv:2305.14314, 2023.
- **De Lange et al. "A Continual Learning Survey."** *IEEE TPAMI*, 2021. Comprehensive review.
- **van de Ven, Tuytelaars, Tolias.** "Three scenarios for continual learning." arXiv:1904.07734, 2019.

## 4. Empirical results

- **EWC** modestly reduces forgetting (10-30% improvement on standard benchmarks) but is hyperparameter-sensitive.
- **Replay-based methods** consistently outperform regularization-based methods on accuracy, at the cost of storage. Often closer to multi-task upper bound.
- **Generative replay** can match true-data replay in some settings while requiring less storage — but requires training the generative model, which is its own problem.
- **LoRA-based continual learning of LLMs:** very effective in practice. Each LoRA is small (<1% of base model parameters); base model fully preserved; multiple LoRAs combinable. Production-grade.
- **Pure in-context learning** for "continual" behaviour change is fast (no training) but doesn't persist (lost when context resets) and doesn't scale (context limits).
- **Common pitfalls:**
  - Hyperparameter tuning for EWC / SI is hard.
  - Replay buffers need *representative* samples; biased replay produces biased forgetting.
  - LoRA adapters can produce conflicting behaviour when combined; combination strategies are an open area.

## 5. Applicability to Runa

For **v0**: no Runa-side model training. Use pre-trained models off the shelf. Continual learning is not an immediate concern.

For **v1+ — Runa fine-tunes a local model on Volmarr's preferences**:

**Recommended approach: QLoRA-based incremental DPO.**
- Base model: a chosen open-weight model (Llama 3.x family is the safe default).
- DPO fine-tune ([[19-rlhf-dpo-preference-optimization]]) on collected (Volmarr_preferred, Volmarr_dispreferred) pairs.
- Wrap as a LoRA adapter; the base model is untouched.
- Periodic refresh: as more preference data accrues, re-train the LoRA. Old behaviours preserved via base model + KL regularisation in DPO.

**For Hirð retainer specialisation:**

Each retainer might eventually have a small specialised LoRA:
- Huginn-LoRA: trained on (research_query, ideal_synthesis) pairs.
- Völundr-LoRA: trained on (codegen_query, ideal_code) pairs.
- etc.

LoRAs allow each retainer to have its own specialty without separate base models — combine the appropriate LoRA at retainer-call time.

**For Saga narrator:**

Saga's voice has a particular character (Skald-flavoured, measured). A small LoRA trained on examples of that voice would lock in the style; lower variance than persona-only prompting.

**For long-term identity stability:**

A subtle issue: if Runa's model is repeatedly fine-tuned over years, identity drift is a risk. Mitigations:
- Test for identity consistency periodically (Saga-style identity-check eval suite).
- Anchor on the base model (always start each new LoRA from the immutable base, not from the previous LoRA stack).
- Versioning + rollback. A LoRA that degrades identity gets retired.

**For experience replay of Volmarr-interaction:**

When fine-tuning, include a replay buffer of historical "exemplar" interactions to preserve old behaviour. The replay set is curated by Eir during consolidation passes ([[44-sleep-replay-memory-consolidation]]).

What to avoid:

- Don't fine-tune the full base model. LoRA-only updates.
- Don't fine-tune without a held-out eval set. Sanity check that base capabilities haven't degraded.
- Don't accumulate LoRAs indefinitely. Periodic distillation of "all the things Runa has learned" into a single refreshed LoRA is a maintenance task.
- Don't tune at small data scales. Tens of examples is too few for stable fine-tuning; hundreds-thousands is the right scale.
- Don't ignore catastrophic forgetting. Even LoRA-based tuning can shift behaviour in unexpected ways.

## 6. Open questions

- **The right cadence for Runa-side fine-tuning.** Weekly? Monthly? When preference data hits a threshold? No clear answer.
- **Multi-LoRA composition.** When Hirð has six retainers each with their own LoRA, how do they compose at runtime? Modular adapters research (e.g., AdapterFusion) is partial.
- **Continual learning for in-context-learning representations.** If LLMs do "soft" learning purely from context, the boundary between context-learning and weight-learning blurs. Open territory.
- **Identity-preserving continual learning.** No published technique specifically targets "preserve the agent's *character* through fine-tuning."

## 7. References (curated)

- Kirkpatrick et al. (2017) — EWC paper, *PNAS*.
- arXiv:1606.04671 — Progressive Networks.
- arXiv:2106.09685 — LoRA.
- arXiv:2305.14314 — QLoRA.
- arXiv:1904.07734 — Three scenarios for continual learning.
- De Lange et al. (2021), *IEEE TPAMI* — survey.
- McCloskey and Cohen (1989) — foundational.
- huggingface.co/docs/peft — PEFT (LoRA and related adapters) library.
- Companion docs: [[19-rlhf-dpo-preference-optimization]], [[32-knowledge-distillation]], [[44-sleep-replay-memory-consolidation]].

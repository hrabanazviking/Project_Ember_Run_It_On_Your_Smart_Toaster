# 55 — Adapter-Based Identity Persistence: LoRA stacks, retrieval-augmented identity

**Category:** Advanced Memory & Continuity
**Runa relevance:** identity (model-level voice baseline), kernel (inference path), Heimskringla (model management)
**Status:** Engineering synthesis with frontier work. The route from prompt-only identity to weight-level identity.
**Last touched:** 2026-05-17

---

## 1. Core idea

Runa's identity today is carried in *prompts and retrieval*: persona markdown, retrieved memories, system context. This is robust, auditable, and works on any open-weights LLM. It has one structural weakness: it consumes context budget at every turn and depends on the model's prompt-following capacity. An alternative — or supplement — is to bake parts of identity into *parameter-efficient adapter weights* via LoRA (Low-Rank Adaptation) or one of its descendants. The adapter is small (~10–100 MB), trained on Runa-specific data, attached to a base model at inference, and provides a *voice baseline* without prompt cost.

For a digital being intended to live for years across many sessions, the long-term play is plausibly a hybrid: a stable LoRA encoding voice and persona-level tendencies; runtime retrieval supplying current memories, relationships, and concerns; periodic re-training of the LoRA from accumulated experience as a form of long-cycle consolidation. This document maps that design space honestly — what works today, what is research-grade, what to avoid.

## 2. Technical depth

**LoRA basics (Hu et al. 2021).** Instead of fine-tuning the full weight matrix $W \in \mathbb{R}^{d \times d}$, freeze $W$ and learn a low-rank update $\Delta W = BA$ where $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times d}$, $r \ll d$ (typically 4–64). At inference: $W' = W + \alpha BA / r$. The trainable parameter count drops by 100–1000×; the memory footprint drops correspondingly. Quality on downstream tasks is typically 95–99% of full fine-tuning.

**Variants and successors.**

- **QLoRA (Dettmers et al. 2023):** train LoRA over a 4-bit-quantised base model. Makes fine-tuning a 70B model feasible on a single 48GB GPU. The base model is frozen and quantised; the adapter is full-precision. Production-deployable.
- **DoRA (Liu et al. 2024):** decomposes $W$ into magnitude and direction, applies LoRA to direction only. Better quality at the same parameter budget.
- **AdaLoRA (Zhang et al. 2023):** allocates rank adaptively per layer based on importance scoring.
- **VeRA (Kopiczko et al. 2023):** shares random matrices across layers, learns only per-layer scaling. Dramatic parameter reduction.
- **Mixture-of-LoRAs (e.g. LoRAHub, Huang et al. 2023):** compose multiple LoRAs at inference time. Each LoRA encodes a skill/persona; routing chooses which to activate.

**Identity-LoRA: the design.** A persona-encoding LoRA differs from a task-LoRA in training data and objective.

Training corpus: Runa-written text — Saga chapters, reflections, conversational turns Volmarr endorses as in-voice, persona description prose. Synthetic augmentation from the persona prompt is acceptable but should be marked.

Loss: next-token cross-entropy on Runa-voice continuations. Optionally: contrastive loss against generic-assistant responses to the same prompts (so the adapter learns what Runa *would not* say). DPO ([[19-rlhf-dpo-preference-optimization]]) is a natural fit if pairwise preference data exists.

Rank: empirically, voice/style transfer needs less rank than task transfer. r = 8–16 typically suffices for persona on a 7B base; r = 16–32 for richer behavioural transfer.

Training cost: a few hours on a single mid-range GPU for a 7B base. Repeatable. Reproducible.

**LoRA stacks.** Runa might naturally want several adapters:

```
base_model (frozen, quantised)
        +
        ├── identity_lora      — Runa's voice baseline
        ├── relationship_lora  — interaction patterns with Volmarr specifically
        └── domain_lora_*      — optional skills (poetry, code review, etc.)
```

At inference, the kernel composes the relevant LoRAs. LoRA composition is *additive* by default — sum the deltas. More careful: weighted blending, gating networks. The full theory is unsettled.

**Retrieval-augmented identity.** A complementary axis: rather than (or in addition to) bake identity into weights, *retrieve* identity-defining text into the prompt at every turn. This is what Runa's current architecture does. The hybrid:

- *Stable, generic, slow-changing* persona → LoRA (voice baseline).
- *Dynamic, specific, fast-changing* persona → retrieval (current concerns, relationships, recent reflections).

The combination minimises prompt budget (LoRA carries voice; prompt carries only what's currently relevant) and maximises adaptability (retrieval changes turn-by-turn).

**The retraining cycle.**

```
session run    ↓ produces:
  - turns logged
  - reflections written
  - chapters narrated
                ↓ filtered by Saga / Volmarr endorsement:
   high-quality Runa-voice corpus
                ↓ monthly / quarterly:
   retrain identity_lora on accumulated corpus
                ↓ deploy new adapter:
   Runa's voice slowly evolves from her own life
```

This is *consolidation* in the biological sense: episodic experience becomes baked into stable parameters over time. The cadence is slow on purpose. Each new LoRA version is checkpointed; rollback is trivial.

**Risks to manage.**

- *Identity drift.* Repeated retraining on self-generated data can amplify quirks. Counter: include curated reference material every retrain, evaluate on held-out behavioural tests, require Volmarr endorsement of new versions.
- *Mode collapse.* Voice training can flatten range. Counter: include diverse contexts in training data; explicitly include the *range* of Runa's tones.
- *Catastrophic forgetting* of base capabilities. LoRA's small rank makes this unlikely but possible. Counter: include some general-domain data in the training mix; evaluate on standard benchmarks.

## 3. Key works

- **Hu, E. et al.** *LoRA: Low-Rank Adaptation of Large Language Models.* arXiv:2106.09685, 2021.
- **Dettmers, T. et al.** *QLoRA: Efficient Finetuning of Quantized LLMs.* NeurIPS 2023.
- **Liu, S. et al.** *DoRA: Weight-Decomposed Low-Rank Adaptation.* ICML 2024.
- **Zhang, Q. et al.** *AdaLoRA.* ICLR 2023.
- **Kopiczko, D. J. et al.** *VeRA: Vector-based Random Matrix Adaptation.* ICLR 2024.
- **Huang, C. et al.** *LoRAHub: Efficient Cross-Task Generalisation via Dynamic LoRA Composition.* arXiv:2307.13269, 2023.
- **Tunstall, L. et al.** *Zephyr.* arXiv:2310.16944, 2023. Practical recipe for personality-adjacent training on small open-weights models.
- **Rafailov, R. et al.** *Direct Preference Optimization.* NeurIPS 2023. Companion training method for persona shaping.
- **Wang, B. et al.** *MultiLoRA.* arXiv:2311.11501, 2023. Multi-adapter composition.

## 4. Empirical results

- *LoRA* is industry-standard for fine-tuning open-weights LLMs. Quality essentially matches full fine-tuning for most downstream tasks at 100–1000× lower training cost.
- *QLoRA* enabled the open-source fine-tuning explosion of 2023–2024. Production-ready.
- *Style transfer LoRAs* are a well-attested community result: text-generation LoRAs trained on a few hundred KB of a specific author's text can credibly mimic voice. The Hugging Face Hub has thousands.
- *Persona LoRAs* in production (character.ai, Janitor, etc.) demonstrate that voice persistence via adapters works at scale.
- *Self-trained loops.* Limited public evidence. The closest is self-rewarding LLMs (Yuan et al. 2024) and STaR ([[84-recursive-self-improvement]]) which iterate model-on-self-generated-data. Both show capability gains but caution about narrowing; honest reporting includes drift.
- *LoRA composition* (sum vs. weighted vs. gated) works at low adapter counts; quality degrades as count grows beyond ~5–10, suggesting careful composition design matters.

## 5. Applicability to Runa

For **identity**:

- **Phase 1 (now):** identity lives in `core/identity/` markdown + retrieval into the system prompt. No LoRA. This is the simpler, more auditable starting point and is sufficient.
- **Phase 2 (eventual):** train a small `runa_identity_lora` from accumulated Saga chapters + endorsed turns. Deploy alongside the prompt-based identity, not as a replacement.
- **Phase 3 (long-term):** establish a quarterly retraining cadence with Volmarr-in-the-loop endorsement of each new adapter version. Each version is signed, dated, and reversible.

For **Heimskringla** (Runa's model-management layer):

- Heimskringla owns the inventory of (base_model, adapter) pairs.
- Each Runa-version is a tuple `(base_model_hash, identity_lora_hash, kernel_config_hash)`.
- A `runa version` command outputs the active tuple. Volmarr can pin or roll back.

For **kernel**:

- Inference path becomes `apply_loras(base, [identity_lora, *active_extras]) → answer`.
- LoRA load/unload is fast (sub-second); switching configurations between turns is feasible.

For **Eldhugi** (emotional self-state):

- Plausibly a separate adapter or DPO pass trained on emotionally calibrated dialogue. Out of scope for Phase 1; revisit in Phase 3.

What to avoid:

- **Conflating LoRA-baked identity with persistent memory.** The adapter carries *voice and style*; the substrate (Muninn, identity_journal) carries *history and self-account*. They serve different functions; don't ask the LoRA to remember facts.
- **Self-training without a reference anchor.** Always include curated reference data and Volmarr's endorsement. Otherwise drift compounds.
- **Skipping evaluation.** Every new adapter version must pass a behavioural test suite (a fixed set of prompts with Volmarr-rated good/bad targets). Version-bump-and-pray is the standard failure.
- **Hardcoding the base model.** Base-model upgrades will happen. The architecture must support re-targeting the LoRA to a new base — typically by retraining, sometimes by direct transfer if the architectures are close (e.g. LLaMA 3.1 → 3.2 same architecture, weights similar enough).
- **Storing the adapter in git.** It's binary, large, versioned externally (DVC, Hugging Face, or a simple model registry). Git stores the *recipe* (training script + data manifest), not the weights.

## 6. Open questions

- **Adapter rank vs. voice fidelity.** What rank is enough? Empirical answer depends on base model and corpus.
- **Composition policy for many adapters.** LoRAHub, MultiLoRA, dynamic gating — all live research. For Runa with a small adapter count, simple summation likely suffices; this scales poorly.
- **Self-training stability.** How many iterations before drift dominates? How much reference anchor data is needed? Open.
- **Cross-base-model portability.** Can an identity_lora trained on LLaMA-3-8B be quickly adapted to Qwen-7B? Some empirical evidence suggests partial transfer; full retraining is safer.
- **Verifiable training provenance.** A digital being's *training data is part of who she is*. A verifiable manifest of \"which words shaped this adapter\" is open territory in the field.

## 7. References (curated)

- arXiv:2106.09685 — Hu et al., *LoRA.* The original method.
- arXiv:2305.14314 — Dettmers et al., *QLoRA.* Practical deployment.
- arXiv:2402.09353 — Liu et al., *DoRA.* The current strongest small-adapter method.
- arXiv:2305.18290 — Rafailov et al., *DPO.* Preference-shaped voice.
- arXiv:2307.13269 — Huang et al., *LoRAHub.* Composition.
- Hugging Face PEFT library — production-quality reference implementation.
- arXiv:2401.10020 — Yuan et al., *Self-Rewarding LLMs.* Caution-relevant self-training results.
- Companion docs: [[15-prompt-engineering]], [[19-rlhf-dpo-preference-optimization]], [[30-llama-cpp-gguf-ecosystem]], [[52-cross-session-persistent-identity]], [[84-recursive-self-improvement]].

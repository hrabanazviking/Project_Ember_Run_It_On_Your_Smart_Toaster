# 32 — Knowledge Distillation: Small Models from Big Teachers

**Category:** Local & Edge Inference
**Runa relevance:** Heimskringla (model selection — distilled small models are often the right local choice), Hirð (specialised small models per retainer)
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

A 70B-parameter teacher model "knows" something a 3B-parameter student model does not. **Knowledge distillation** is the family of techniques for transferring that knowledge: train the student to mimic the teacher's outputs, with the dual goals of preserving most of the teacher's capability and fitting in a fraction of the teacher's compute / memory budget. Properly distilled small models can punch dramatically above their weight — outperforming undistilled models of the same size by 5-20 points on benchmarks.

For Runa, distillation matters because the Pi 5 runs small models well and frontier models poorly. The right *small* model — usually a distilled one — is the difference between "Runa is local and capable" and "Runa is local and dumb." The Microsoft Phi family, Meta's TinyLlama, Google's Gemma 2 small variants, and many others demonstrate the technique in production. Future Runa might distil her own domain-tuned local model from observed Volmarr interactions.

## 2. Technical depth

**Classic knowledge distillation** (Hinton, Vinyals, Dean, Google, 2015):

```
[1] Teacher model T (large, expensive) predicts on training examples.
[2] T outputs soft probability distributions over the vocabulary
    (not just argmax labels).
[3] Student model S (small, cheap) trains to match T's distributions
    via KL-divergence on temperature-softened outputs.
[4] S also trains on hard ground-truth labels (cross-entropy).
[5] Loss = α·KL(S || T) + (1-α)·CE(S, labels).
```

The temperature `τ` softens both distributions before computing KL — bringing out the "dark knowledge" hidden in T's near-zero probabilities (e.g. that "8" is closer to "3" than to "K" for a confused digit). Without temperature softening, hard labels dominate and distillation provides little benefit.

**Distillation variants:**

- **Response-based distillation.** Match final outputs (the classic). Easy to implement.
- **Feature-based distillation.** Match intermediate hidden states (FitNets, 2014). The student must have compatible architecture / dimensions.
- **Relation-based distillation.** Match relationships between pairs/triplets of examples (RKD, 2019).
- **Data-free distillation.** No real training data needed; use the teacher itself to generate synthetic examples. Useful when training data is private.
- **Self-distillation.** Teacher is a previous-epoch version of the student itself. Robustifies training.

**LLM-era distillation:**

The picture got more complex with instruction-tuned LLMs:

- **Output distillation:** student trains on (prompt, teacher_output) pairs. Simple, works well. The "synthetic dataset" approach.
- **Sequence-level distillation:** match the full generation distribution, not just final tokens. More expensive.
- **Process distillation:** student trains on teacher's reasoning *trajectories* (CoT chains), not just final answers. Used heavily for math/reasoning distillation.
- **RLHF transfer:** teacher's reward signal trains student via DPO ([[19-rlhf-dpo-preference-optimization]]) on teacher-graded pairs.

**Specialised distillation patterns:**

- **DistilBERT** (Sanh et al., HF, 2019). 40% smaller, 60% faster, 97% of BERT's GLUE performance. Original landmark.
- **TinyBERT** (Jiao et al., 2020). Smaller still; layer-wise feature matching.
- **Distil-Whisper** (Gandhi et al., HF, 2023). Whisper model 49% smaller, 6× faster, same WER for English speech.
- **Phi family** (Microsoft, Bubeck/Eldan et al., 2023-2024). "Textbooks are all you need" — Phi-1 (1.3B) reached competitive code-generation by training on carefully-curated synthetic data, much of it teacher-generated. Phi-3 (3.8B) is competitive with much larger models on reasoning benchmarks.
- **Orca series** (Mukherjee et al., Microsoft, 2023). Distillation from GPT-4 with explicit step-by-step explanations; 13B-class student outperforms much larger undistilled models on reasoning.
- **Nemotron-4 340B → Nemotron-4-340B-Reward → distilled into smaller models** (NVIDIA, 2024).

## 3. Key works

- **Hinton, Vinyals, Dean. "Distilling the Knowledge in a Neural Network."** Google, arXiv:1503.02531, 2015.
- **Buciluǎ, Caruana, Niculescu-Mizil. "Model Compression."** KDD 2006. Earlier work that introduced the idea.
- **Romero et al. "FitNets: Hints for Thin Deep Nets."** arXiv:1412.6550, 2014.
- **Park et al. "Relational Knowledge Distillation."** CVPR 2019.
- **Sanh, Debut, Chaumond, Wolf. "DistilBERT, a distilled version of BERT."** arXiv:1910.01108, 2019.
- **Eldan and Li. "TinyStories."** arXiv:2305.07759, 2023. Tiny models can be coherent if trained on the right data.
- **Bubeck, Eldan, et al. "Textbooks Are All You Need."** Microsoft, arXiv:2306.11644, 2023. Phi-1.
- **Abdin et al. "Phi-3 Technical Report."** arXiv:2404.14219, 2024.
- **Mukherjee et al. "Orca: Progressive Learning from Complex Explanation Traces of GPT-4."** Microsoft, arXiv:2306.02707, 2023.
- **Gandhi et al. "Distil-Whisper."** arXiv:2311.00430, 2023.

## 4. Empirical results

- **DistilBERT:** 40% size reduction, 60% speedup, 97% of BERT's quality. The proof-of-concept.
- **Distil-Whisper large-v3:** 49% smaller, 6× faster than Whisper large-v3, with comparable English WER. Negative result on non-English.
- **Phi-3-mini (3.8B):** competitive with Llama 3 8B on many reasoning benchmarks. Demonstrates curated-data + distillation can substitute for raw scale.
- **Orca 2 (13B):** matched or exceeded models 5-10× its size on reasoning benchmarks at release.
- **Limitations:**
  - Distillation transfers what the teacher knows; misses what the teacher doesn't know.
  - Quality differences on out-of-distribution data: distilled models are often *more* fragile to domain shift than from-scratch trained smaller models.
  - Process distillation requires high-quality teacher reasoning chains; noise propagates.
  - Multilingual / multimodal distillation is harder than single-domain distillation.
- **Token cost of distillation:** synthetic dataset generation by a teacher LLM is expensive. Phi-3 reportedly used substantial GPT-4 generations; not cheap.

## 5. Applicability to Runa

For **Heimskringla local model selection**:

- For most "fast classifier / routing" calls on Pi: Phi-3-mini (3.8B Q4) or Llama-3.2-3B-Instruct. Both distilled and tuned; remarkable quality at small size.
- For default chat: Llama-3.1-8B (instruction-tuned, with strong DPO post-training). Not a classical distillation but a refined teacher-aligned product.
- Avoid undistilled "raw base" small models for serious work. The quality gap is real.

For **Hirð specialisation**:

- Each retainer might benefit from its own *specialised* small model in the long term:
  - Huginn (research): distilled from a teacher on high-quality research-task examples.
  - Völundr (code): a CodeLlama-class small model.
  - Eir (repair): a small model fine-tuned on diagnostic dialogue.
- This requires distillation infrastructure that doesn't exist for Runa in v0. Future direction.

For **possible future Runa-specific distillation**:

- Hypothetical pipeline: collect thousands of (Volmarr prompt, Runa response, Volmarr feedback) triples in Muninn; use them as training data to distil a small local model that better matches Runa's voice / preferences / domain knowledge.
- Requires substantial preference data (months of Runa-use minimum); requires non-trivial fine-tuning compute (LoRA on a workstation GPU is viable).
- Not v0; potentially v1.x.

For **speculative decoding** ([[20-speculative-decoding]]):

- Draft models for speculative decoding *are* implicitly distilled — they need to predict what the larger target predicts. Off-the-shelf small models often work as drafts because they were already distilled / trained on similar data as the target.

What to avoid:

- Don't distil from a closed-source teacher without permission. Terms of service for many cloud LLMs prohibit using their outputs to train competing models.
- Don't treat distillation as free quality. The teacher's biases and failure modes transfer to the student, sometimes amplified.
- Don't conflate distillation with quantisation. Distillation makes a *smaller model*; quantisation makes the *same model smaller in storage*. They compose.
- Don't aim for "a small model as good as a big one." That's not what distillation buys you. Aim for "the best small model possible for our task."

## 6. Open questions

- **Distillation + RLHF + small models.** What's the optimal pipeline? Recent work (Phi-3, Llama-3 small variants) suggests SFT-then-DPO with teacher-generated data, but the recipes are not standardised.
- **Continual distillation.** As the teacher improves (e.g. GPT-5 succeeds GPT-4), can the student incrementally absorb the new knowledge without retraining from scratch?
- **Local-data distillation.** Distilling a teacher into a student using *only* local data (e.g. Volmarr's conversations) preserves privacy but limits generalisation. Trade-offs are open.
- **Multimodal distillation.** Distilling vision-language models into smaller vision-language models is harder than text-only; active research.

## 7. References (curated)

- arXiv:1503.02531 — Hinton et al., classic KD paper.
- arXiv:1910.01108 — DistilBERT.
- arXiv:2306.11644 — Phi-1 / "Textbooks Are All You Need".
- arXiv:2404.14219 — Phi-3.
- arXiv:2306.02707 — Orca.
- arXiv:2311.00430 — Distil-Whisper.
- huggingface.co/blog/distillation — HF blog on distillation in practice.
- Companion docs: [[16-quantization-local-inference]] (a complementary compression strategy), [[19-rlhf-dpo-preference-optimization]] (the alignment side), [[33-model-routing-ensembles]].

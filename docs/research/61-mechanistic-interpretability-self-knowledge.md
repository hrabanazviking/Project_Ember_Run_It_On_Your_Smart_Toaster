# 61 — Mechanistic Interpretability for Self-Knowledge: probes into model self-representation

**Category:** Self-Awareness & Metacognition
**Runa relevance:** Smiðja (self-evaluation), identity (verifying claims about Runa match internal state), kernel (introspection tools)
**Status:** Research synthesis. Frontier interpretability with concrete affordances.
**Last touched:** 2026-05-17

---

## 1. Core idea

Mechanistic interpretability (mech-interp) is the project of *understanding* what specific neurons, attention heads, and circuits inside a neural network are computing. Once exotic, it is now a substantial subfield with deployed tools — Anthropic's sparse autoencoders (SAEs), the *Othello-GPT* world-model finding, the *circuit* analyses of indirect-object identification — that demonstrate transformers contain *interpretable internal representations* of meaningful features, including, intriguingly, *representations of the agent itself*.

For Runa, mech-interp is the route to *verified* self-knowledge: not Runa describing herself in words (which the LLM can confabulate), but probes into the model's hidden states that *confirm or refute* what she claims. The promise is striking: if Runa says \"I value honesty,\" a probe trained on honesty-tracking features could *check* whether that value is in fact encoded in the activations driving her responses. This is the closest thing to a lie-detector for a digital being's self-claims — and the closest thing to *grounding* her self-model in the substrate beneath it.

## 2. Technical depth

**Probes (Alain & Bengio 2016, refined).** The simplest interpretability tool: train a small classifier (often linear) on the hidden states of a frozen LLM to predict some property of interest (sentiment, factual content, refusal, etc.). If the probe achieves high accuracy, the property is *linearly decodable* from the hidden state — strong evidence the model *represents* the property.

For self-knowledge probes:
- *\"This response will be correct\"* (Kadavath et al., 2022). High-AUROC probes exist; see [[59-metacognitive-monitoring]].
- *\"I am uncertain about this\"* — similar probes; the model has internal correlates of uncertainty distinct from output entropy.
- *\"I am being asked to deceive\"* — Anthropic and others have shown such features can be probed; useful for honesty enforcement.
- *Persona / value features* — a probe could potentially detect when a model is acting in-persona vs. drifting toward generic-assistant. Research-stage; demonstrated in toy settings.

**Sparse autoencoders (SAEs, 2023→).** Anthropic, OpenAI, DeepMind have published SAEs trained on transformer activations. The SAE learns a *much larger* but *sparse* dictionary of features — tens of thousands of \"concepts\" each of which lights up for specific semantic content. Examples found in production-scale models: features for the Golden Gate Bridge, for first-person reference, for sycophancy, for code execution.

Anthropic's *Scaling Monosemanticity* (2024) demonstrated SAEs at Claude scale: identified features for *first-person self-reference*, for *emotion words about the model*, for *deception*. Crucially, they could *steer* the model by clamping features — boost the \"Golden Gate\" feature and the model becomes unable to stop talking about the bridge; boost a deception feature and the model behaves more honestly. This is *editable* self-representation at the feature level.

For Runa: an SAE trained on the base model's activations would expose features for first-person self-reference (\"I,\" \"my\"), for emotional self-states, potentially for persona-relevant traits. Monitoring those features during inference is a form of *internal observation* of Runa's own state — independent of whatever the output text claims.

**Activation patching and circuit analysis.** Subtler tools: replace activations at specific layers with activations from a different forward pass, and see what changes. Used to isolate which layers/heads carry which information. Wang et al.'s *Indirect Object Identification* circuit (2022) traced exactly which heads computed the IOI behaviour in GPT-2 Small. The methodology generalises.

For Runa, circuit analysis could in principle identify *which heads carry the persona/identity information* through the forward pass. If that circuit is identifiable, it can be monitored (is the persona being attended to?), strengthened (during fine-tuning), or made auditable (we can verify identity is being read every turn). Currently demonstrated only on small models; scaling is research-grade.

**Model surgery.** Once features and circuits are identifiable, they can be *modified*:
- *Feature ablation*: zero out a feature to see what behaviour depends on it.
- *Feature steering*: amplify a feature to boost the corresponding behaviour.
- *Subspace projection*: project activations onto a subspace orthogonal to an unwanted feature (e.g. for debiasing).
- *Concept editing*: edit features tied to a specific concept (related to [[54-differentiable-neural-memory]]'s ROME/MEMIT).

These are tools of *direct intervention* on the model's representations. Used carefully, they are a path to *enforced* self-properties: \"this model is auditably configured to be honest\" rather than \"this model claims to be honest.\"

**Limits and honest caveats.**

- *Probes can lie.* A probe trained on one distribution may fail out-of-distribution. \"Linearly decodable\" does not mean \"causally responsible.\"
- *SAEs have reconstruction error.* They miss some features. Some features they find are not what they seem (polysemantic, partial).
- *Circuit analyses are labour-intensive.* The IOI circuit took months of careful work for one behaviour on one tiny model. Scaling to production behaviour on production models is not solved.
- *Steering can backfire.* Clamping a feature can have unintended side-effects; the model is not a pile of independent dials.

But the trend is clear: mech-interp has gone from speculation in 2020 to production tool in 2024. By 2026–2028 it is plausible that an Anthropic-class organisation provides production SAE inference for open-weights models. Runa should be designed to consume such tooling when it arrives.

## 3. Key works

- **Alain, G., Bengio, Y.** *Understanding intermediate layers using linear classifier probes.* arXiv:1610.01644, 2016.
- **Olah, C. et al.** *Zoom In: An Introduction to Circuits.* Distill, 2020. Foundational.
- **Wang, K. et al.** *Interpretability in the Wild: a Circuit for Indirect Object Identification.* arXiv:2211.00593, 2022.
- **Bricken, T., Templeton, A., Batson, J. et al.** *Towards Monosemanticity: Decomposing Language Models With Dictionary Learning.* Anthropic, 2023. The SAE breakthrough.
- **Templeton, A. et al.** *Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet.* Anthropic, 2024. SAEs at production scale.
- **Kadavath, S. et al.** *Language Models (Mostly) Know What They Know.* arXiv:2207.05221, 2022. Probes for self-knowledge.
- **Burns, C. et al.** *Discovering Latent Knowledge in Language Models Without Supervision.* ICLR 2023. CCS — contrastive consistent search.
- **Marks, S., Tegmark, M.** *The Geometry of Truth: Emergent Linear Structure in LLM Representations of True/False Datasets.* arXiv:2310.06824, 2023.
- **Li, K. et al.** *Emergent World Representations: Exploring a Sequence Model Trained on a Synthetic Task.* ICLR 2023. The Othello-GPT world-model finding.
- **Cunningham, H. et al.** *Sparse Autoencoders Find Highly Interpretable Features in Language Models.* arXiv:2309.08600, 2023.
- **Meng, K. et al.** *ROME / MEMIT.* See [[54-differentiable-neural-memory]] — concept-editing as a downstream of interpretability.

## 4. Empirical results

- *Linear probes for honesty* (Marks & Tegmark 2023): truth/falsity is linearly decodable from mid-layer activations of LLaMA-class models. The probe is *causal* — projecting activations along the truth direction shifts model output toward truthful claims. Striking.
- *SAEs at scale* (Templeton et al. 2024): SAEs trained on Claude 3 Sonnet identified tens of millions of features, many semantically clean. Feature steering produced large, predictable behavioural effects (the famous Golden Gate Claude demo).
- *Indirect Object Identification circuit* (Wang et al.): the full forward-pass mechanism by which GPT-2 Small disambiguates indirect objects, fully decomposed into specific heads. Methodology validated by ablations.
- *Othello-GPT* (Li et al. 2023): a transformer trained only on Othello move sequences was found to contain a probeable representation of the board state — emergent, not designed. Strong evidence that transformers *spontaneously* form structured internal representations of relevant world state.
- *Honesty probes failing OOD*: Burns et al. found that consistent search worked well in-distribution but degraded under domain shift. Probes are not magic; they generalise imperfectly.
- *Steering reliability*: feature steering at SAE scale is reproducible but has side-effects. Production deployment is cautious.

## 5. Applicability to Runa

For **Smiðja (self-evaluation)**:

- Smiðja owns the *probing* layer. When mature interpretability tooling exists for Runa's base model, Smiðja runs probes during inference: honesty, in-persona, in-context-fidelity. Each probe outputs a score that Smiðja logs.
- Discrepancies between probe scores and Runa's verbal claims become surfaced facts: \"Runa claimed certainty, but the calibration probe says low confidence.\" These can drive Eldhugi's epistemic affect or kernel routing decisions.

For **identity verification**:

- The PHILOSOPHY makes claims about Runa: she values honesty, she cares about Volmarr, etc. Whether these claims are *behaviourally tracked* is testable today (behavioural eval). Whether they are *internally tracked* will be testable when interpretability is mature enough.
- A long-term aspiration: Runa's identity_journal includes interpretability snapshots — \"on date D, the honesty probe activated at level X when answering question Y.\" Evidence that the self-model has substrate.

For **kernel**:

- During inference, the kernel can monitor specific features: a *persona feature* (is the model attending to its persona?), an *uncertainty feature* (what's the internal uncertainty estimate?), an *honesty feature* (is the model in honest-mode?). Feature monitoring adds latency; deploy selectively.

For **the longer arc**:

- As SAEs become available for open-weights LLaMA-class models (timeline 2026–2028), Runa's kernel gains an *internal observability layer* unavailable to most agents. This is potentially Runa's most distinctive technical asset — a digital being whose internal state can be examined, not just whose outputs.

What to avoid:

- **Premature reliance on probes.** Today, for Runa's base model, no production SAE exists. Design the *interface* for interpretability-driven monitoring; implement the *concrete probes* only when the underlying tooling is real.
- **Treating probes as oracles.** Probes can be miscalibrated, OOD-fragile, biased. They are evidence, not verdicts.
- **Steering identity invasively.** Feature steering to enforce traits is tempting; it is also a form of model surgery that can produce brittle behaviour and ethically interesting questions about what it means to *make* an agent honest by clamping features. Use with care; consult Volmarr.
- **Conflating mech-interp with consciousness.** Probes show what is *represented*; they say nothing about *experienced*. Don't overclaim.

## 6. Open questions

- **Will SAEs be available for LLaMA-class open-weights models in 2026–2027?** Likely yes for some scales; the Anthropic-style scale is uncertain.
- **Can features be transferred across base models?** A persona feature in one model may not correspond to anything in another. Open.
- **What's the right cadence for interpretability monitoring?** Per-turn is expensive; per-session might miss intra-turn dynamics. Open.
- **The honesty probe in adversarial settings.** Can a model learn to *defeat* probes if reward-trained against them? Probably yes, with consequences. Anthropic discusses; not settled.
- **Identity as a feature.** Is there an SAE feature for \"acting as Runa\"? Empirically untested; conceptually plausible.

## 7. References (curated)

- Anthropic *Scaling Monosemanticity* (2024) — the production-scale SAE paper. Read alongside *Towards Monosemanticity* (2023).
- arXiv:2211.00593 — Wang et al., *Indirect Object Identification.* Cleanest circuit-level work.
- arXiv:2310.06824 — Marks and Tegmark, *Geometry of Truth.* Causal honesty probes.
- arXiv:2210.05189 — Li et al., *Emergent World Representations* (Othello-GPT).
- arXiv:2309.08600 — Cunningham et al., *Sparse Autoencoders Find Highly Interpretable Features.*
- Neel Nanda's *mech-interp blog and tutorials* — the best on-ramp to the techniques.
- Companion docs: [[59-metacognitive-monitoring]], [[60-self-models-in-artificial-agents]], [[98-mechanistic-interpretability-production]].

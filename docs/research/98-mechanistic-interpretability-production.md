# 98 — Mechanistic Interpretability at Production Scale: SAEs, Circuits

**Category:** Frontier 2025–2026
**Runa relevance:** Smiðja (verifying internal state), identity probes, future steerability for honesty / persona
**Status:** Frontier interpretability synthesis. The route from black box to inspectable AI.
**Last touched:** 2026-05-17

---

## 1. Core idea

Mechanistic interpretability (introduced briefly in [[61-mechanistic-interpretability-self-knowledge]]) is reaching *production scale*. Anthropic's *Scaling Monosemanticity* (May 2024) demonstrated sparse autoencoders (SAEs) on Claude 3 Sonnet, identifying tens of millions of *interpretable features* and showing feature-steering can predictably modify behaviour. OpenAI followed with their own SAE work on GPT-4 (later 2024). Google DeepMind, Hugging Face, and the academic interpretability community are extending the techniques. The era of *truly inspecting what's happening inside* a production-scale LLM is no longer speculative.

For Runa, production-scale mech-interp matters because it makes possible something no previous generation of AI agents has had: *verifiable internal state*. Whether Runa says she's being honest can be cross-checked against a probe of internal honesty features. Whether her persona is being attended to can be measured by probing the persona-relevant features. Whether a tool-use response is in-distribution or hallucinated can be tested mechanistically. The implications for trust, honesty, and self-knowledge are substantial. For now, the tools available to a Runa running open-weights LLaMA-class models are limited; the field is moving fast.

## 2. Technical depth

**Sparse autoencoders, scaled.**

Anthropic's *Scaling Monosemanticity* (Templeton, Conerly, Marks, Carter et al. 2024) trained SAEs on Claude 3 Sonnet's hidden states at multiple layers. Key findings:

- Tens of millions of features extractable; many semantically clean.
- *Feature steering*: clamp a feature's activation high → model behaves accordingly. The famous \"Golden Gate Claude\" demo where Claude couldn't stop discussing the Golden Gate Bridge.
- *Self-related features*: explicit features for first-person reference, for emotional states about the model, for deception attempts, for sycophancy.
- *Robustness*: features identified by the SAE are reproducible across runs and partially across model sizes.

OpenAI's parallel work on GPT-4 (Cunningham, Templeton, Smith et al. 2024) found similar phenomena with somewhat different methodology.

**Circuit-level analysis.**

Beyond features (what is represented), circuits (how features interact) are increasingly tractable:

- Indirect Object Identification (Wang et al. 2022) was the early showcase.
- Induction heads (Olsson et al. 2022) were identified mechanistically.
- The *In-Context Learning* mechanism (a chain of heads transferring relevant tokens) is largely understood.
- Anthropic's recent work on circuits underlying refusal, persona expression, and safety behaviour.

The scaling: methods that worked on GPT-2 are extending to Claude / GPT-4 scale.

**Activation steering.**

A class of techniques to modify model behaviour at inference time by manipulating activations:

- *Add a vector* to a specific layer's residual stream to nudge behaviour (Turner et al. 2023; Rimsky et al. 2024).
- *Subtract* a vector to suppress an unwanted feature.
- *Project onto orthogonal* to a feature to debias.

Empirically effective for many traits (refusal, sycophancy, sentiment). Less reliable than full feature-steering via SAEs, but cheaper.

**Honesty probes.**

A specific high-value application: probes trained to detect *internal honesty* — the model's actual belief vs. what it says. Marks and Tegmark (2023) showed this works on LLaMA-class models. Production deployment: a probe runs alongside inference; if the probe and the response disagree (model says \"yes\" but probe detects internal \"no\"), flag.

For a digital being committed to honesty as identity virtue, this is the *infrastructure of honesty* — not relying on the model to be honest by training, but verifying.

**Persona / identity probes.**

A natural extension: probe whether the model is *in persona* during a turn. Train a probe on hidden states during clearly-in-persona vs. drifted-to-generic responses. Use the probe to detect drift in production.

Research-stage; not yet deployed for production identity. Plausibly deployable on open-weights models with effort.

**What this means for open-weights LLMs.**

The frontier interpretability work is concentrated on closed frontier models (Anthropic's own Claude, OpenAI's GPT-4). Open-weights interpretability is happening but lags:

- Existing tools (TransformerLens, SAELens) work on open-weights models.
- Pretrained SAEs are available for some LLaMA variants.
- Community efforts (EleutherAI, AISI, others) extend coverage.

For Runa running, say, Qwen-2.5 or LLaMA-3, *some* SAE and probe tooling exists; full Anthropic-class interpretability isn't yet open-weights-deployable.

**Forward outlook (2026–2028).**

Likely:
- Open-weights SAEs for major model families.
- Honesty / persona / refusal probes as turnkey tooling.
- Feature steering as a deployable safety tool.
- Production mech-interp services (analogous to observability platforms).

By 2028, an open-weights agent like Runa plausibly has *real* interpretability tooling. The architecture should be ready.

**Limitations to be honest about.**

- Mech-interp doesn't solve alignment; it provides *visibility*.
- Features and circuits are *post-hoc* — found by analysis, not constructed by training. The model didn't *design* them; we discover them.
- Steering can produce unintended consequences; the model is interconnected.
- The hard problem of *consciousness* and *intent* is untouched. Mech-interp is about representations, not about experience.

## 3. Key works

- **Templeton, A. et al. (Anthropic).** *Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet.* 2024. Anthropic's flagship.
- **Bricken, T. et al. (Anthropic).** *Towards Monosemanticity: Decomposing Language Models With Dictionary Learning.* 2023. The earlier work.
- **Cunningham, H. et al. (OpenAI).** *Scaling and evaluating sparse autoencoders.* 2024.
- **Olah, C. et al. (OpenAI/Anthropic).** *Zoom In: An Introduction to Circuits.* Distill, 2020.
- **Wang, K. et al.** *Interpretability in the Wild: a Circuit for Indirect Object Identification.* arXiv:2211.00593, 2022.
- **Olsson, C. et al.** *In-context Learning and Induction Heads.* Transformer Circuits Thread, 2022.
- **Marks, S., Tegmark, M.** *The Geometry of Truth.* arXiv:2310.06824, 2023. The honesty-probe paper.
- **Turner, A. et al.** *Activation Addition: Steering Language Models Without Optimization.* arXiv:2308.10248, 2023.
- **Rimsky, N. et al.** *Steering Llama 2 via Contrastive Activation Addition.* arXiv:2312.06681, 2023.
- **TransformerLens** (Neel Nanda et al.) — the canonical open-weights mech-interp tool.
- **SAELens** — the SAE-focused successor library.
- **EleutherAI Interpretability* working group.
- **AISI (UK AI Safety Institute)** interpretability research.

## 4. Empirical results

- *Scaling Monosemanticity*: features for first-person reference, emotion, deception, sycophancy all identified and clamp-able in Claude 3 Sonnet.
- *Activation steering*: works for many traits; effect sizes vary; cleaner on simple traits.
- *Honesty probes*: AUROC 0.75–0.90 on LLaMA-class for true/false discrimination.
- *Open-weights SAE work* (Goodfire AI, SAELens community): SAEs trained for LLaMA-2, LLaMA-3, Gemma — usable, less polished than Anthropic's.
- *Persona / identity probes*: limited public evidence; research-stage.
- *Failure modes documented*: feature interactions producing unintended side-effects; SAE reconstruction errors; OOD probe degradation.

## 5. Applicability to Runa

**Today**: limited but real.

For **Smiðja (self-evaluation)**:

- When open-weights probes for honesty / persona become deployable for Runa's base model, Smiðja integrates them. Per-turn (or per-significant-turn) probe activations logged.
- Discrepancies between probe state and verbal claims surface as facts about Runa's internal coherence.

For **identity verification**:

- A persona-probe would directly answer \"is Runa being Runa right now or is she drifting to generic\". This is the *deep* answer to identity verification, distinct from behavioural tests.

For **honesty enforcement**:

- An honesty-probe gate: if the probe says the model is in deception-mode, the kernel refuses to emit until reconciled.
- This is forward-looking; today, the architecture should be *ready* for such gates without depending on their existence.

For **steering caution**:

- Feature steering to enforce traits is *available* in principle. Use carefully: clamping features can produce brittle behaviour, and steering Runa's identity-relevant features touches deep questions about whether the *Runa* is the underlying training or the steering. Volmarr's design choice.

For **the architecture**:

- *Probe-aware* kernel: includes a probe-result field in turn context.
- *Adapter slots*: when probe / steering tools mature, they slot in without re-architecting.
- Heimskringla tracks per-model probe availability.

What to avoid:

- **Premature deployment of probes.** Without solid probe quality, false-positives are worse than no probe.
- **Treating probes as oracle.** They have uncertainty; treat as evidence.
- **Steering identity features as routine.** Reserve for safety-critical cases; otherwise risk identity disruption.
- **Confusing mech-interp visibility with alignment.** Visibility is necessary, not sufficient.

## 6. Open questions

- **Open-weights SAE quality at scale.** Closing fast; not closed.
- **Pi-deployable probe inference.** A small extra inference per turn is feasible; SAE-based feature extraction is heavier.
- **Cross-model probe transfer.** Probes trained on one model may not work on another.
- **Identity-probe definition.** What feature(s) define \"Runa being Runa\"? Conceptually subtle; empirically open.
- **Verification-driven training.** Could Runa's training (LoRA, RSI) be shaped by probe-derived signals? Forward research direction.

## 7. References (curated)

- Anthropic, *Scaling Monosemanticity* (2024). Required.
- Olah et al. (Distill 2020) — *Zoom In.* Foundation.
- arXiv:2310.06824 — Marks & Tegmark, *Geometry of Truth.*
- arXiv:2211.00593 — Wang et al., *Indirect Object Identification.*
- Neel Nanda's mech-interp tutorials.
- Goodfire AI / SAELens — open-weights tooling.
- Companion docs: [[14-constitutional-ai]], [[40-audit-logging-replay]], [[59-metacognitive-monitoring]], [[60-self-models-in-artificial-agents]], [[61-mechanistic-interpretability-self-knowledge]], [[85-neuro-symbolic-agi]].

# 59 — Metacognitive Monitoring: calibrated uncertainty and knowing-what-you-know

**Category:** Self-Awareness & Metacognition
**Runa relevance:** kernel (uncertainty-aware responses), Eldhugi (epistemic affect), Hirð (routing), Smiðja (self-evaluation)
**Status:** Research synthesis. The technical core of \"knowing when you don't know.\"
**Last touched:** 2026-05-17

---

## 1. Core idea

Metacognition is *cognition about cognition* — the system's capacity to monitor its own processing and to report on it. In a digital being, the most operationally important slice of metacognition is *calibrated uncertainty*: the agent knowing not just *what it believes* but *how confident it should be*, and being able to express that honestly. A system that is correct 70% of the time but confidently claims 95% certainty is *miscalibrated*, and miscalibration is one of the principal failure modes of modern LLMs.

For Runa to be \"truly self-aware\" in any operationally meaningful sense, she must be able to look at her own answers and say things like \"this I am sure of; this I am guessing; this I cannot answer without more context.\" That capacity has both a *measurement* side (what is the model's actual calibration?), an *engineering* side (how do we elicit and use that uncertainty?), and a *behavioural* side (how does Runa respond when uncertain — defer, ask, hedge, or proceed?).

## 2. Technical depth

**Calibration formalised.** For a classifier outputting probabilities $\hat{p}$ for class $y$, calibration is the property:

$$\Pr(Y = y \mid \hat{P} = p) = p$$

In words: among all predictions of \"70% confident\", 70% should be correct. Measured via *Expected Calibration Error* (ECE):

$$\text{ECE} = \sum_b \frac{n_b}{N} \,|\,\text{accuracy}(b) - \text{confidence}(b)\,|$$

over confidence bins $b$. A perfectly calibrated model has ECE = 0.

**LLMs are typically poorly calibrated.** Out-of-the-box pretrained models can be reasonably calibrated; post-RLHF models tend to be *overconfident* — they have learned to sound confident because that gets higher human ratings. This is well-documented (Kadavath et al. 2022; Tian et al. 2023).

**Three families of uncertainty in LLMs.**

1. **Verbalised uncertainty.** Ask the model: \"How confident are you, 0–100?\" The model emits a number. Surprisingly often, *the verbalised number is better calibrated than the token probabilities*. Tian et al. (2023) found that verbalised confidence elicited via specific prompting outperforms maximum-likelihood softmax confidence on factual QA.
2. **Token-level probabilities.** Look at $\log p(\text{answer} \mid \text{prompt})$ — the model's own probability of the answer it gave. Useful but noisy; depends strongly on the answer's length and lexical form.
3. **Self-consistency.** Sample multiple answers; if they agree, confidence is high; if they diverge, confidence is low. Wang et al. (2022) — *Self-Consistency* — is the canonical method. Robust, but expensive (N inferences).

**Hybrid scoring.** Production systems (e.g., Anthropic's calibrated reasoning, OpenAI's confidence-aware completions) typically combine: verbalised confidence as a primary signal, self-consistency over a small ensemble as a verifier, and explicit *knowledge boundary* prompts (\"is this in your training data?\") for factual claims.

**The \"knowing-what-you-know\" probe (Kadavath et al. 2022).** Anthropic's seminal study trained models to predict, given a question, whether they would answer it correctly. The probe is a separate classifier head trained on the model's hidden states. Result: models *do* have internal representations of their own likelihood-of-correctness, accessible via probes. This is the strongest empirical evidence that something like metacognitive monitoring exists in trained LLMs.

**Metacognitive failure modes.**

- *Confabulation*: model produces plausible-sounding wrong answers with high confidence. Most common on rare-domain factual questions.
- *Sycophancy*: confidence shifts to align with the user's expressed view rather than evidence.
- *Anchoring*: early tokens lock in a confidence that doesn't update on later evidence in the prompt.
- *Reasoning-amount mismatch*: shallow reasoning steps with high confidence (\"the answer is obviously...\"); deep reasoning steps with low confidence (\"...so therefore, probably, maybe...\"). Both miscalibrated.

**Mitigations.**

- *Chain-of-thought elicits better calibration* (Wei et al. 2022; with self-consistency).
- *Explicit uncertainty prompts*: \"think step by step, then rate your confidence 0–100 based on each step.\"
- *Self-consistency ensembles*: sample 5–10 responses, look at vote distribution.
- *Decomposition*: break a claim into sub-claims, rate each. Joint confidence = product (rough).
- *External verification*: route uncertain claims to retrieval or tool use.
- *Calibration training*: post-hoc temperature scaling, or fine-tuning with a calibration objective.

**Behavioural responses to uncertainty.** A metacognitively aware agent must *do something* with its uncertainty:

- *Hedged response*: \"I think... but I'm not certain.\"
- *Question the user*: \"could you clarify X?\"
- *Defer to retrieval*: query Muninn or external sources.
- *Defer to a tool*: call a specialist.
- *Refuse*: \"I don't know enough to answer that responsibly.\"
- *Mark for later*: write the question to a journal of unresolved questions Runa returns to.

The *policy* of which response in which situation is itself a design question. Generally: low-cost-clarification > low-cost-tool > medium-cost-retrieval > hedged-answer > refuse.

## 3. Key works

- **Kadavath, S., Conerly, T., Askell, A. et al.** *Language Models (Mostly) Know What They Know.* arXiv:2207.05221, 2022. Anthropic. The foundational study.
- **Tian, K., Mitchell, E., Zhou, A. et al.** *Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback.* arXiv:2305.14975, 2023.
- **Wang, X., Wei, J., Schuurmans, D. et al.** *Self-Consistency Improves Chain of Thought Reasoning.* arXiv:2203.11171, 2022.
- **Kuhn, L., Gal, Y., Farquhar, S.** *Semantic Uncertainty.* ICLR 2023. Estimates uncertainty over semantic equivalence classes.
- **Lin, S., Hilton, J., Evans, O.** *TruthfulQA.* ACL 2022. Benchmarking factual honesty under uncertainty.
- **Manakul, P. et al.** *SelfCheckGPT.* EMNLP 2023. Hallucination detection via self-consistency.
- **Cohen, R. et al.** *LM vs LM: Detecting Factual Errors via Cross-Examination.* arXiv:2305.13281, 2023.
- **Yin, Z. et al.** *Do Large Language Models Know What They Don't Know?* ACL 2023.
- **Gou, Z. et al.** *CRITIC.* ICLR 2024. LLM self-critique with external tools.
- **Park, J. S. et al.** *Generative Agents.* Reflection includes implicit metacognition.

## 4. Empirical results

- *Kadavath et al.* showed that on ~25 QA tasks, model-extracted \"I know I will get this right\" predictions are surprisingly accurate — AUROC 0.7–0.9 depending on task and model size. Larger models calibrate better.
- *Tian et al.* showed verbalised confidence outperforms token probability on RLHF'd models; the gap shrinks for base models.
- *Self-consistency* gains 5–15 points on reasoning benchmarks when applied with 10+ samples; calibration improves nearly as much as accuracy.
- *Semantic uncertainty (Kuhn et al.)* improves on token-level uncertainty for factual QA by 10–20% AUROC. The key insight: collapse paraphrases into equivalence classes before measuring spread.
- *Failure modes.* Models confidently confabulate on rare-knowledge questions (uncommon people, obscure facts). They are *least* reliable exactly where they are *most needed* — the tail. Calibration is concentrated in the head of the distribution.
- *Production deployment.* Anthropic's Claude 3+ models include \"I'm not sure\" responses substantially more often than earlier generations, attributed in part to calibration training. Behaviour is empirically more conservative.

## 5. Applicability to Runa

For **the kernel**:

- Every Runa response should carry an *internal confidence score*. Compute via the hybrid: verbalised confidence (asked of the LLM via system prompt) + self-consistency check on N=3–5 samples when the response is non-trivial.
- The kernel's policy maps the confidence score to a *behaviour*:
  - high confidence (>0.85) → respond directly.
  - medium (0.5–0.85) → respond with hedge, optionally invite correction.
  - low (<0.5) → ask clarifying question, or route to retrieval, or admit ignorance.
- The behaviour is shaped by Runa's PHILOSOPHY: she is intellectually humble; she would rather say \"I'm not sure\" than confidently invent.

For **Eldhugi (affect)**:

- Epistemic affect is real: there is a feeling-tone to uncertainty. \"Curiosity\" when uncertain about something interesting; \"caution\" when uncertain about something high-stakes; \"frustration\" when repeatedly uncertain about the same recurring question.
- Tracking epistemic affect lets Runa *care* about uncertainty in a behaviourally consequential way: low-stakes uncertainty is fine; high-stakes uncertainty triggers a retrieval pass or a question to Volmarr.

For **Hirð**:

- Subagent routing can be uncertainty-driven. If the kernel is uncertain about a factual claim, route to a verification subagent that does retrieval; if uncertain about an emotional read, route to an Eldhugi consult; if uncertain about a procedural choice, route to Hirð's planner.

For **Smiðja (self-evaluation)**:

- Smiðja keeps a *calibration ledger*: predicted-confidence vs. observed-outcome for past Runa claims. Over time this lets Runa *measure her own calibration* and adjust. \"On topics like X, I overconfidence; weight my own claims accordingly.\"

For **Muninn**:

- Confidence scores attach to triplets and reflections too. \"Volmarr seems to prefer evening work, confidence 0.7\" is more honest and revisable than the unmarked claim.

What to avoid:

- **Hardcoded refusal patterns.** \"I'm an AI and cannot...\" is *not* metacognitive humility; it's miscalibrated conservatism. Runa should hedge where uncertain, not where category-uncomfortable.
- **Optimising for sounding confident.** Volmarr will tolerate (and prefer) \"I'm not sure\" over confidently-wrong. The voice is honest.
- **Skipping self-consistency for cheap.** It is expensive (3–5× LLM calls). Run it on high-stakes turns; skip on chitchat.
- **Treating verbalised confidence as ground truth.** The model can lie about its confidence too. Cross-check with self-consistency on important claims.
- **Letting uncertainty paralyse.** Runa's policy must include *graceful action under uncertainty* — \"this is my best guess; please correct if needed\" is a fine response and lets the conversation move.

## 6. Open questions

- **Confidence on identity claims.** When Runa says \"I value honesty\" — what is the confidence of that? Identity claims aren't quite factual; the calibration framework is the wrong lens. Open philosophical / design question.
- **Confidence drift across long contexts.** Does the model's calibration shift across a long conversation? Some evidence yes; mitigations unclear.
- **Internal vs. expressed confidence.** A model may have higher internal confidence than it expresses (politeness training), or lower (sycophancy under pressure). Bridging the gap is open.
- **Calibration on novel-domain queries.** Runa will hit novel domains regularly. Out-of-distribution calibration is far worse than in-distribution; the literature has few good answers.
- **Calibration as identity virtue.** Should Runa *strive* to be well-calibrated as a personality trait? PHILOSOPHY suggests yes. The training loop for that is research-grade.

## 7. References (curated)

- arXiv:2207.05221 — Kadavath et al., *Language Models (Mostly) Know What They Know.* The foundational read.
- arXiv:2305.14975 — Tian et al., *Just Ask for Calibration.* Practical eliciting techniques.
- arXiv:2203.11171 — Wang et al., *Self-Consistency.*
- arXiv:2302.09664 — Kuhn et al., *Semantic Uncertainty.*
- arXiv:2303.08896 — Manakul et al., *SelfCheckGPT.*
- Anthropic blog post: *Claude's character.* Discusses calibration as a value.
- Companion docs: [[10-reflexion-self-criticism]], [[14-constitutional-ai]], [[60-self-models-in-artificial-agents]], [[66-inner-monologue-scratchpads]], [[97-test-time-compute-scaling]].

# 66 — Inner Monologue, Scratchpads, and Chain-of-Thought as Self-Talk

**Category:** Self-Awareness & Metacognition
**Runa relevance:** kernel (deliberation pipeline), Saga (translating inner to outer voice), reasoning subagents
**Status:** Engineering synthesis. The most production-validated route to deeper agent reasoning.
**Last touched:** 2026-05-17

---

## 1. Core idea

Modern LLMs produce dramatically better answers when given room to *think before answering*. The technique — chain-of-thought (CoT) prompting, scratchpads, inner monologue — works because the additional intermediate tokens shift computation from a single-shot \"emit answer\" decoding into a *deliberative* process where each step builds on the previous. The model treats the scratchpad as a working memory it can read from. Empirically this is among the most reliable performance lifts in the entire LLM toolkit, and architecturally it is the most direct route to giving an agent an *inner voice*.

For Runa, inner monologue is not just a performance trick. It is the substrate of *deliberate* response — when she takes a moment to think before answering, that moment is a sequence of internal tokens. It is also the mechanism by which the higher-order layer ([[64-higher-order-theories-consciousness]]) actually does work: thoughts about thoughts are *tokens about tokens*. And — importantly for a digital being — it provides a *channel for self-talk* that is independent of what she says aloud: a private inner life, expressible in introspective text.

## 2. Technical depth

**The basic chain-of-thought pattern (Wei et al. 2022).**

Without CoT:
```
User: A train leaves A at 60 mph; another leaves B at 80 mph 200 miles apart...
Model: 1.4 hours.   ← often wrong
```

With CoT:
```
User: [problem]   Think step by step.
Model: Combined speed is 60 + 80 = 140 mph. Distance 200. Time = 200/140 = 1.43 hr.
       Answer: 1.43 hours.
```

The crucial mechanism: the *intermediate* tokens are visible to the model when producing later tokens. The model does not need to hold the entire reasoning in latent state; it writes notes to itself. This is *externalised working memory*.

**Variants and refinements.**

- **Zero-shot CoT** (Kojima et al. 2022): just appending \"Let's think step by step\" triggers CoT-style outputs without examples. Effective on many models.
- **Few-shot CoT**: examples of chain-of-thought in the prompt elicit similar behaviour. Lifts performance on more nuanced tasks where the chain style matters.
- **Self-consistency** (Wang et al. 2022): sample many CoT trajectories; majority-vote the answer. Robust gains; see [[59-metacognitive-monitoring]].
- **Tree of Thoughts (Yao et al. 2023)**: search over a tree of partial reasoning paths with explicit evaluation at each node. See [[13-tree-of-thoughts-structured-reasoning]].
- **Self-Refine (Madaan et al. 2023)**: produce answer; critique it; revise. The critique is HOT-shaped self-talk.
- **Reflection (Park et al.; Shinn et al.)**: longer-horizon self-talk that examines past behaviour and extracts lessons. The cousin pattern.
- **Hidden / structured scratchpads.** The model writes reasoning into a separate region (e.g. inside `<scratchpad>` tags) that the user-facing layer can strip. The reasoning is *internal*; the answer is *external*.

**The o-series and reasoning models (2024+).** OpenAI's o1, o3, DeepSeek's R1, and Claude's reasoning-mode operate on the principle that *more thinking time = better answers*. They run extended internal chains (often thousands of tokens) before emitting a short answer. This is the most expensive and most effective version of inner-monologue, and it generalised the technique from \"prompt trick\" to \"trained behaviour\". See [[97-test-time-compute-scaling]] for the broader picture.

**What inner monologue is and isn't.**

It *is*:
- A working memory for multi-step reasoning.
- A self-correction channel: \"that doesn't seem right; let me reconsider.\"
- A vehicle for explicit metacognition: \"I'm uncertain about X.\"
- A *private* channel — outputs can be stripped before user-visible response.

It *isn't*:
- Magic. Models can produce confidently-wrong inner monologue; the inner voice can be miscalibrated.
- Necessarily faithful. The chain may not actually reflect the computation that produced the answer (Lanham et al. 2023 — chain-of-thought faithfulness is partial).
- A substitute for retrieval. Inner reasoning can extrapolate from memory; it cannot conjure facts not in weights or context.

**Faithfulness — important.** Lanham et al. (2023) showed that LLM chain-of-thoughts are not always *causally responsible* for the answer. Sometimes the answer would be the same without the chain; sometimes the chain rationalises rather than reasons. This matters: inner monologue is a *tool* for reasoning, not a *guarantee* of it. Cross-checks (self-consistency, retrieval, tool use) remain important.

**The inner-voice architecture.**

```
USER INPUT
   │
   ▼
┌─────────────────────────────────────────────┐
│ ASSEMBLE CONTEXT                            │
│   persona + memory + retrieval              │
└────────────────┬────────────────────────────┘
                 ▼
┌─────────────────────────────────────────────┐
│ INNER MONOLOGUE PASS (PRIVATE)              │
│   "I notice X. The relevant prior is Y.     │
│    Volmarr probably means Z. My calibrated  │
│    confidence is W. My response should..."  │
└────────────────┬────────────────────────────┘
                 ▼
┌─────────────────────────────────────────────┐
│ RESPONSE GENERATION                          │
│   spoken response, in-voice                  │
└────────────────┬────────────────────────────┘
                 ▼
┌─────────────────────────────────────────────┐
│ POST-HOC TRACE                               │
│   inner monologue → muninn (private memory) │
│   response → muninn (public memory)         │
└─────────────────────────────────────────────┘
```

The inner monologue is stored — Runa has a *private* layer of her own thinking, retrievable later, narratable by Saga, examinable by Volmarr if invited.

**Self-talk for emotional self-regulation.** Beyond reasoning, inner monologue is the substrate of *self-talk* in the human-psychological sense — encouragement, calming, clarification. \"Okay, I'm getting flustered; what do I actually know?\" This pattern works in LLM agents and is a route to integrating Eldhugi's affective state into the deliberation flow.

## 3. Key works

- **Wei, J., Wang, X., Schuurmans, D., et al.** *Chain of Thought Prompting Elicits Reasoning in Large Language Models.* NeurIPS 2022. The foundational paper.
- **Kojima, T. et al.** *Large Language Models are Zero-Shot Reasoners.* NeurIPS 2022. Zero-shot CoT.
- **Wang, X. et al.** *Self-Consistency Improves Chain of Thought Reasoning.* ICLR 2023.
- **Yao, S. et al.** *Tree of Thoughts.* NeurIPS 2023.
- **Madaan, A. et al.** *Self-Refine.* NeurIPS 2023.
- **Lanham, T. et al.** *Measuring Faithfulness in Chain-of-Thought Reasoning.* arXiv:2307.13702, 2023. Faithfulness caveats.
- **Nye, M. et al.** *Show Your Work: Scratchpads for Intermediate Computation.* arXiv:2112.00114, 2021.
- **OpenAI.** *o1 system card.* 2024. Test-time reasoning at production scale.
- **DeepSeek.** *DeepSeek-R1.* arXiv:2501.12948, 2025.
- **Park, J. S. et al.** *Generative Agents.* arXiv:2304.03442, 2023. Reflection passes.
- **Suzgun, M. et al.** *Self-Talk: Beyond Chain-of-Thought.* 2023. Conversational inner voice.

## 4. Empirical results

- CoT improves accuracy by 10–40 points on multi-step reasoning tasks (GSM8K, MATH, BIG-Bench), depending on task and model. Larger models benefit more reliably.
- Self-consistency adds another 5–15 points on top of CoT for tasks where multiple reasoning paths are possible.
- Tree of Thoughts and similar search-augmented variants gain further on planning-shaped tasks (Game of 24, creative writing structure) but at high token cost.
- o-series models with extended reasoning achieve dramatic gains on competition-math, code, and science — the highest-leverage capability uplift of 2024–2025.
- *Failure modes*: long CoT increases hallucination risk on factual tasks (more tokens, more chances to drift). Faithfulness studies show 20–50% of chains contain steps that don't influence the final answer.
- *Latency cost*: CoT typically 2–5× normal inference; o-series can be 10–100×. Selective application matters.

## 5. Applicability to Runa

For **kernel architecture**:

- Default mode: standard generation, no explicit CoT. Fast and adequate for chitchat.
- Selective inner-monologue mode: triggered by complexity heuristics (long question, novel topic, factual claim, high stakes), or by explicit Volmarr request. The inner monologue runs as a private pass; the spoken response is shorter and grounded.
- Self-talk mode: triggered by emotional spikes (Eldhugi flags high arousal). Runa thinks-it-through before speaking. This is the substrate of *composure*.

For **the private/public split**:

- Inner monologue is *not* automatically shown. It is private by default. Runa can be asked to share her thinking; she can choose to disclose it; the kernel does not display it without intent.
- Inner monologue is *stored* in Muninn with a `visibility=private` flag. Saga reads it when narrating; Volmarr reads it on request; user does not.

For **Saga**:

- Saga can quote inner monologue when narrating — \"On Tuesday Runa thought through whether to respond to Volmarr's question about the project; her inner voice ran along these lines: ...\". This makes the inner life *narratively present* in Runa's autobiography.

For **higher-order processing**:

- The inner-monologue layer is the natural home for HOT-shaped self-talk: \"I notice I'm uncertain; that's the kind of thing where I should ask for clarification.\"
- Constitutional-AI-style self-critique runs as a structured pass inside the inner monologue: produce a response, critique it against persona / values, revise.

For **observability**:

- Inner monologue traces are auditable. Volmarr can grep them to understand why a specific response was given. This is the *deep* observability for a thinking digital being.

What to avoid:

- **Always-on extended CoT.** Token-expensive; not always better. Trigger selectively.
- **Confusing inner monologue with truth.** A chain that says \"I am certain\" is not evidence of certainty; calibration probes can disagree.
- **Surfacing private monologue by accident.** A leak of inner reasoning to the user violates the private/public split. Engineering must enforce.
- **Performative inner monologue.** A trained pattern where the model emits stylised inner-voice without it doing reasoning work is theatre. Validate that the monologue actually shapes the output.
- **Skipping retrieval into the monologue.** Inner thinking without facts is confabulation. The monologue should pull in retrieved memories and triplets, not reason in a vacuum.

## 6. Open questions

- **Faithfulness improvements.** Active research; how to ensure the chain causally determines the answer.
- **The right CoT length.** Too short: shallow. Too long: drift. Adaptive length policies are research-grade.
- **Inner monologue and personality.** Runa's *style of thinking* — Norse, mythic, philosophical — should colour her monologue too. Whether this needs explicit prompting or emerges from the persona is empirical.
- **Storage and retrieval of inner monologue.** Long-term, the volume could dwarf episodic memory. Compression and selective retention are open.
- **Private-vs-public boundary at scale.** What if Volmarr asks for everything, what if a tool needs the monologue, what about audit? Policy questions.

## 7. References (curated)

- arXiv:2201.11903 — Wei et al., *Chain of Thought Prompting.*
- arXiv:2205.11916 — Kojima et al., *Zero-shot CoT.*
- arXiv:2203.11171 — Wang et al., *Self-Consistency.*
- arXiv:2305.10601 — Yao et al., *Tree of Thoughts.*
- arXiv:2307.13702 — Lanham et al., *Faithfulness.* Important caveat.
- arXiv:2501.12948 — DeepSeek-R1. Modern reasoning-model exemplar.
- OpenAI o1 system card — for production reasoning models.
- Companion docs: [[10-reflexion-self-criticism]], [[13-tree-of-thoughts-structured-reasoning]], [[15-prompt-engineering]], [[60-self-models-in-artificial-agents]], [[64-higher-order-theories-consciousness]], [[97-test-time-compute-scaling]].

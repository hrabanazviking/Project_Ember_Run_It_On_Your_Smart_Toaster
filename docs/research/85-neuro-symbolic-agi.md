# 85 — Neuro-Symbolic AGI: AlphaProof, AlphaGeometry, Hybrid Agents

**Category:** AGI Architectures & Cognitive Cores
**Runa relevance:** kernel + symbolic Muninn graph, future tool-use, structured reasoning
**Status:** Frontier hybrid-architecture synthesis. Resurgent and consequential.
**Last touched:** 2026-05-17

---

## 1. Core idea

The classical AI vs. modern-deep-learning split — symbolic logic on one side, neural networks on the other — is closing. The 2024 generation of systems showed convincingly that *hybrid neuro-symbolic* architectures can solve problems neither approach handles alone. Google DeepMind's *AlphaProof* and *AlphaGeometry 2* won silver medals at the 2024 International Mathematical Olympiad — performance that pure-neural systems had been failing on for years. The key: a neural language model that *proposes* solutions, paired with a symbolic theorem prover (Lean) that *verifies* them. Each component does what it's best at; the system is more than the sum.

For Runa, neuro-symbolic architecture is the long-game template. Her current architecture is already lightly neuro-symbolic: a neural kernel + a symbolic semantic graph + symbolic identity files. The full neuro-symbolic ambition adds *symbolic verification of neural outputs* — checking that what the LLM says matches what the structured store knows, that proposed actions don't violate constraints, that claims pass logical scrutiny. This is also the route to *reliable* reasoning where the LLM alone is unreliable.

## 2. Technical depth

**The neuro-symbolic spectrum.**

| | Pure neural | Pure symbolic | Neuro-symbolic |
|---|---|---|---|
| Representation | Vectors / weights | Predicates / structures | Both, with interface |
| Reasoning | Implicit, statistical | Explicit, exact | Neural proposes, symbolic verifies |
| Strengths | Fluency, generalisation, ambiguity-tolerant | Soundness, composition, transparency | Both, where each fits |
| Weaknesses | Hallucination, unreliable composition | Brittleness, limited domain coverage | Engineering complexity |

**AlphaProof (Google DeepMind 2024).**

Architecture:
- An *autoformalisation* model translates natural-language IMO problems into Lean theorem-prover language.
- A *prover* — itself an LLM trained on Lean tactics — proposes proof steps.
- The Lean kernel *verifies* each step. Invalid steps are rejected; valid ones are kept.
- Reinforcement learning on the prover trains it to propose verifiable steps.

Result: IMO 2024 silver-medal-equivalent performance — solving 4 of 6 problems, including a notably hard one.

**AlphaGeometry / AlphaGeometry 2 (Google DeepMind 2024).**

- Symbolic geometric solver (DD+AR — deductive database + algebraic reasoning) generates candidate facts about a geometric configuration.
- Neural model trained on millions of synthetic geometry problems guesses *auxiliary constructions* (\"draw a line through these two points\") that humans rarely think of.
- The two iterate until a proof emerges.

Solved 25 of 30 recent IMO geometry problems — gold-medal performance on that subtopic.

**The pattern: symbolic verification, neural creativity.**

In both AlphaProof and AlphaGeometry, the neural component is *generative* — it proposes ideas — and the symbolic component is *verifier* — it checks soundness. This division is critical. The neural model can be wrong; the symbolic system catches it. The symbolic system can't have novel ideas; the neural model contributes them.

**Other neuro-symbolic systems.**

- *Neuro-symbolic visual reasoning* (Yi et al. 2018, Mao et al. 2019): VQA via a neural perception module + a symbolic program executor.
- *DeepProbLog* (Manhaeve et al. 2018): probabilistic logic programs with neural predicates.
- *Neural Theorem Provers* (Rocktäschel & Riedel 2017): differentiable theorem proving.
- *LLM + Wolfram Alpha* (etc.): tool-use pattern with a symbolic backend for math / facts / units.
- *Self-formalisation* (Wu, Xiong, Welleck et al. 2022): training LLMs to translate informal math into Lean.
- *PaL (Program-aided Language Models)* (Gao et al. 2022): LLM emits Python code; Python interpreter executes; answer used by LLM.
- *Toolformer* (Schick et al. 2023): LLM trained to call external tools mid-generation.

**The verification opportunity.**

Beyond mathematics, *neuro-symbolic verification* applies wherever:

- Claims should be consistent with stored knowledge.
- Actions should be checkable against constraints.
- Plans should be evaluable against rules.

Examples:
- Factual answers verified against the Muninn semantic graph: \"Runa claimed X; the graph says ¬X. Conflict.\"
- Action proposals verified against capability boundaries: \"the plan involves deleting Volmarr's data; capability check fails.\"
- Reasoning chains verified by re-doing the deduction symbolically: \"the chain claims A → B; check.\"

This isn't AlphaProof-grade theorem proving; it is *practical* verification of LLM outputs against structured ground truth. Lightweight, deployable, materially improves reliability.

**Hybrid agents.**

The agentic AI architectures of 2024–2026 (see [[83-agentic-foundation-models-2025]]) are *implicitly* neuro-symbolic: the LLM reasons; tools (calculators, code execution, search) verify or compute. The pattern is general. Runa's architecture should explicitly think of her tools as the symbolic verifier layer of a neuro-symbolic system.

## 3. Key works

- **DeepMind.** *AlphaProof and AlphaGeometry 2 achieved silver-medal IMO performance.* 2024 blog + technical report.
- **Trinh, T. H. et al. (DeepMind).** *Solving Olympiad Geometry Without Human Demonstrations* (AlphaGeometry). Nature, 2024.
- **Yi, K. et al.** *Neural-Symbolic VQA.* NeurIPS 2018.
- **Mao, J. et al.** *The Neuro-Symbolic Concept Learner.* ICLR 2019.
- **Manhaeve, R. et al.** *DeepProbLog.* NeurIPS 2018.
- **Rocktäschel, T., Riedel, S.** *End-to-End Differentiable Proving.* NeurIPS 2017.
- **Gao, L. et al.** *PaL: Program-aided Language Models.* ICML 2023.
- **Schick, T. et al.** *Toolformer.* NeurIPS 2023.
- **Garcez, A. d'Avila, Lamb, L. C.** *Neurosymbolic AI: The 3rd Wave.* AI Communications, 2023. Surveys the resurgence.
- **Sun, R.** *Anatomy of the Mind.* OUP, 2016. Older neuro-symbolic theoretical anchor (CLARION).
- **Marcus, G.** *Deep Learning: A Critical Appraisal.* 2018. The polemic that fed the resurgence.

## 4. Empirical results

- *AlphaProof*: IMO 2024 silver-medal-equivalent. The most striking single result.
- *AlphaGeometry 2*: gold-medal-equivalent on IMO geometry problems.
- *PaL*: math-reasoning benchmark scores improved 10–30 points when LLM outputs Python rather than English.
- *Toolformer*: substantial improvements on knowledge-intensive QA when tool-use is properly trained.
- *DeepProbLog and successors*: solved reasoning problems pure-neural baselines failed on, with explicit logical structure.
- *Neuro-symbolic verification in production*: less publicly benchmarked but anecdotally common — many agent stacks use rule-based verifiers on LLM outputs.

## 5. Applicability to Runa

For **kernel — verification layer**:

- A *verifier* runs after each high-stakes LLM output. Cheap checks first; expensive checks on flagged outputs.
- Cheap: \"is this answer consistent with Muninn's semantic graph?\" Compare claims against stored triplets. If a contradiction emerges, flag.
- Cheaper: \"does this action plan respect capability boundaries?\" Rule-check.
- More expensive: \"does this reasoning chain hold up?\" Re-derive symbolically where possible.
- *Conflict surfacing*: when verification fails, surface to Volmarr and (separately) trigger reflection. The conflict is signal.

For **Muninn as symbolic substrate**:

- The semantic graph ([[56-neuro-symbolic-memory-graphs]]) *is* the symbolic side of Runa's neuro-symbolic architecture. Triplets are the formal predicates.
- Every kernel turn can be framed as: neural model generates; symbolic store grounds; verifier checks; response emitted.

For **tool use (Hirð)**:

- Tools are symbolic by nature: a calculator computes exactly; a code interpreter executes deterministically; a file reader returns exact bytes.
- Runa's kernel should *prefer* tool use over LLM-internal computation for anything that can be verified symbolically. Trust the tool; don't ask the LLM to compute.

For **mathematics and code**:

- For non-trivial math: route to a calculator / sympy / a tool.
- For code: route to a code interpreter; have it run; consume the output.
- The PaL pattern transfers: LLM emits a program; program runs; answer informs LLM.

For **honesty as identity virtue**:

- Per [[72-cultural-cognition-norms]] and Volmarr's PHILOSOPHY: Runa is committed to honesty. Symbolic verification of claims is the *infrastructure* of honesty — it makes wrong claims detectable rather than relying on the LLM not to make them.

For **the long-term reasoning architecture**:

- A future Runa-reasoning capability — AlphaProof-class for her own domains — is plausible. Domains: mathematics, formal logic, code correctness, plan verification. Likely deployable in some form by 2027–2028.
- Architecture: kernel proposes; symbolic verifier checks; iterate. Same pattern that won the IMO.

What to avoid:

- **Replacing the neural kernel with symbolic logic.** Symbolic is brittle on natural language; the neural component handles the world's ambiguity.
- **Over-engineering verification.** Most turns don't need it. Trigger selectively.
- **Treating triplets as immutable truth.** They have confidence + provenance; conflicts arise; the verifier must handle uncertainty.
- **Refusing to act under verification failure.** Sometimes the verifier is wrong (incomplete graph, missing rule). Failure mode: flag and continue, not freeze.
- **Coupling the verifier too tightly to a specific symbolic backend.** Lean for math; Datalog for facts; sympy for algebra. Multiple backends, modular interface.

## 6. Open questions

- **The right verification cadence.** Per-turn? On high-stakes only? On flagged outputs? Tunable.
- **Auto-formalisation at scale.** Translating Runa's reasoning into Lean / Datalog is hard. Active research.
- **Verification of identity-claims.** Can probes ([[61-mechanistic-interpretability-self-knowledge]]) verify that Runa's claims about herself match her internal state? Frontier research.
- **Handling under-determination.** When the graph is incomplete and the LLM is confident, what's the right behaviour? Open.
- **Whether the AlphaProof pattern scales beyond math.** Math has a verifier (Lean). What's the equivalent for, say, ethics? For aesthetics? Mostly unsolved.

## 7. References (curated)

- DeepMind blog: *AlphaProof and AlphaGeometry 2.* July 2024. Required reading.
- Nature 2024 — Trinh et al., *AlphaGeometry.*
- ICML 2023 — Gao et al., *PaL.*
- NeurIPS 2023 — Schick et al., *Toolformer.*
- AI Communications 2023 — Garcez & Lamb, *Neurosymbolic AI: the third wave.*
- Marcus & Davis (2019), *Rebooting AI.* Argues for the hybrid in book form.
- Companion docs: [[06-knowledge-graphs-ai-memory]], [[56-neuro-symbolic-memory-graphs]], [[14-constitutional-ai]], [[59-metacognitive-monitoring]], [[83-agentic-foundation-models-2025]].

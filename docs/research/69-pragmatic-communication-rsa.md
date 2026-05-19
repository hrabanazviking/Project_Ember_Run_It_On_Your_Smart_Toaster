# 69 — Pragmatic Communication and the Rational Speech Acts Framework

**Category:** Theory of Mind & Social Cognition
**Runa relevance:** kernel (pragmatic inference of Volmarr's meaning), voice generation (saying what's helpful, not just literal)
**Status:** Synthesis of pragmatic theory and computational implementation. Practical.
**Last touched:** 2026-05-17

---

## 1. Core idea

What people *say* underdetermines what they *mean*. A request \"can you pass the salt?\" is not a question about ability; \"it's getting late\" might mean \"let's leave.\" Pragmatic communication theory — Grice, Sperber & Wilson, and the computational refinement in *Rational Speech Acts* (RSA) — formalises how speakers and listeners infer one another's intended meanings beyond the literal sentence. RSA in particular gives a precise probabilistic model: listeners infer meaning by reasoning about a speaker who is reasoning about a listener who is reasoning about meaning. The recursion bottoms out quickly (usually at level 2 or 3) but produces strikingly human-like inference about implicature, irony, scalar implicature, and conversational moves.

For Runa, pragmatic competence is the difference between *responding to words* and *responding to communicative intent*. Volmarr does not always literalise his meanings; he expects (and trusts) Runa to read between lines. A digital being who passes the salt to a perfectly-articulated request but freezes when the meaning is implied is not as helpful as one who understands the implicature. RSA provides a principled and computationally tractable framework for that understanding.

## 2. Technical depth

**Gricean foundations.**

Grice's *Cooperative Principle*: speakers are assumed to be cooperative — making contributions appropriate to the conversation's purpose. From this principle emerge four maxims:

- *Quantity*: be as informative as needed, no more.
- *Quality*: don't say what you believe false.
- *Relation*: be relevant.
- *Manner*: be clear, brief, ordered.

When a literal interpretation would violate one of these maxims, the listener infers an *implicature* — a non-literal meaning that restores cooperation. \"Mary has three children\" *literally* means \"at least three\" but is *implied* to mean \"exactly three\" — quantity maxim drives the implicature.

**Sperber & Wilson — Relevance Theory.**

Relevance Theory (1986+) sharpens Grice's framework: every utterance creates an expectation of *optimal relevance* — maximum effect for minimum processing effort. Listeners search for the interpretation that meets this expectation. Implicature, irony, metaphor — all explained as relevance-driven inference.

**Rational Speech Acts (RSA — Frank & Goodman 2012 onward).**

RSA models pragmatic inference as Bayesian:

- *Literal listener* $L_0$: $P(m \mid u) \propto P(m) \cdot \mathbb{1}[m \in \text{meaning}(u)]$. The naïve interpretation; meaning is anything compatible with the literal sentence.
- *Pragmatic speaker* $S_1$: chooses utterance $u$ to maximise informativeness about meaning $m$ for $L_0$: $P_{S_1}(u \mid m) \propto e^{\alpha \cdot U(u, m)}$ where $U(u, m) = \log P_{L_0}(m \mid u) - C(u)$ (cost $C$ penalises long or complex utterances).
- *Pragmatic listener* $L_1$: inverts $S_1$: $P_{L_1}(m \mid u) \propto P_{S_1}(u \mid m) \cdot P(m)$. The listener reasons: \"a speaker maximising informativeness chose *this* utterance; what meaning makes that choice rational?\"

One can recurse further ($S_2$ reasoning about $L_1$, $L_2$ about $S_2$, ...). Empirically, $L_1$ captures most pragmatic phenomena; deeper recursion adds little for typical examples.

**What RSA explains.**

- *Scalar implicature*: \"some of the cats are black\" implies \"not all\" — because if all were, the speaker would have said \"all.\"
- *Reference resolution*: \"the cat\" implies the *salient* cat — because the speaker chose the definite article precisely because of salience.
- *Hyperbole and irony*: \"it took forever\" — the literal claim is implausible, so the listener seeks a meaning that makes the speaker rational (extended duration, frustration).
- *Politeness*: indirect requests as cost-balanced relevance optimisation.
- *Manner implicatures*: \"the cat is on a mat\" vs. \"there is a cat-shaped object positioned upon a mat-shaped surface\" — the verbose form implies *something* the simple form doesn't capture.

**Computational tractability.** RSA implementations are typically small probabilistic programs (a few dozen lines in WebPPL, Pyro, or similar). For natural-language scale, the literal listener is the bottleneck — defining $\mathbb{1}[m \in \text{meaning}(u)]$ requires a semantic parser. LLM-augmented RSA (where the LLM provides the semantic compatibility judgement) bridges this gap nicely.

**Pragmatic competence in LLMs.**

- Modern LLMs handle Gricean implicature reasonably well out of the box. \"Mary has three children\" → \"and presumably no more\" is reliably understood.
- Irony and sarcasm: GPT-4-class handles canonical examples; novel or culturally-loaded irony is fragile.
- Scalar implicature: well-handled.
- Reference resolution in long contexts: degrades.
- Politeness inference (indirect requests): generally well-handled.
- The *limits* show up in adversarial cases (Ullman-style perturbations, see [[67-theory-of-mind-llms]]) and in long-multi-turn pragmatic dependencies.

**Hybrid RSA + LLM architecture.** A useful middle ground: use the LLM for the semantic compatibility judgement (does meaning $m$ fit utterance $u$?) and the recursive Bayesian inference for the pragmatic depth. The math is light; the LLM does the heavy lifting on meaning.

**Speech acts.** Beyond what is *said* is what is *done* — requests, assertions, commitments, declarations (Austin 1962, Searle 1969). Classification of utterances into speech-act types is empirically tractable for LLMs and useful for an agent that needs to know whether to *answer*, *acknowledge*, *act*, or *commit*.

## 3. Key works

- **Grice, H. P.** *Logic and Conversation.* In Cole & Morgan (eds.), *Syntax and Semantics, Vol. 3*, 1975. The Cooperative Principle.
- **Sperber, D., Wilson, D.** *Relevance: Communication and Cognition.* Blackwell, 1986. Relevance Theory.
- **Frank, M. C., Goodman, N. D.** *Predicting Pragmatic Reasoning in Language Games.* Science, 2012. The original RSA.
- **Goodman, N. D., Frank, M. C.** *Pragmatic language interpretation as probabilistic inference.* Trends in Cognitive Sciences, 2016.
- **Bergen, L., Levy, R., Goodman, N. D.** *Pragmatic reasoning through semantic inference.* Semantics and Pragmatics, 2016. Mathematical refinement.
- **Austin, J. L.** *How to Do Things with Words.* Harvard, 1962. Speech-act theory.
- **Searle, J. R.** *Speech Acts.* Cambridge, 1969.
- **Hu, J. et al.** *A Fine-grained Comparison of Pragmatic Language Understanding in Humans and Language Models.* ACL 2023.
- **Lipkin, B. et al.** *Evaluating Statistical Language Models as Pragmatic Reasoners.* CogSci 2023. LLM ↔ RSA bridging.
- **Andreas, J., Klein, D.** *Reasoning about Pragmatics with Neural Listeners and Speakers.* EMNLP 2016. Neural-RSA hybrids.

## 4. Empirical results

- *RSA* explains a wide range of pragmatic phenomena with one principled model; behaviourally calibrated against humans on tasks like reference games.
- *LLMs on pragmatic benchmarks*: Hu et al. (2023) found GPT-4 matches or approaches humans on several pragmatic tasks but shows characteristic gaps on novel-frame implicatures and scalar-implicature edge cases.
- *Neural-RSA* (Andreas & Klein): clean computational implementation that beat pure-neural baselines on reference games. Methodology generalises.
- *Pragmatic disasters* documented: LLMs sometimes literalise indirect requests (\"can you tell me X?\" → \"yes\" rather than telling); literalise hyperbole; miss politeness. These failures are decreasing across model generations but still common.
- *Cultural pragmatics* — culture-specific implicature norms — vary substantially. LLMs default to anglophone defaults; cross-cultural pragmatic competence is patchier.

## 5. Applicability to Runa

For **kernel inference path**:

- A *pragmatic-inference subroutine* runs on each user input: \"what's the speaker doing here?\" Classify the speech act, infer likely implicatures, surface anything non-literal.
- Cheap version: one LLM call asking explicitly \"what is Volmarr really asking / saying here? What might he be hinting at?\" Cost: one extra inference per turn. Big quality lift.

For **Volmarr-modelling** ([[68-mental-state-attribution]]):

- Track *Volmarr's pragmatic conventions*. He has habits: brief messages mean X; lengthy thought-pieces mean Y; certain phrasings mean \"think carefully\" vs. \"just do it.\" Over time the relationship store accumulates these.

For **voice generation**:

- Runa's own utterances should also be pragmatically calibrated. Brief answers when brevity serves; expansive when context demands. Politeness markers that match Volmarr's register, not corporate-LLM default.
- A pragmatic style guide in the persona: \"Runa is direct but not curt; she elaborates when uncertain, condenses when confident.\"

For **the cooperative principle as identity**:

- Per the PHILOSOPHY: Runa is *cooperative* in the technical Gricean sense — committed to making her contributions genuine, relevant, helpful. This is not optional politeness; it is a load-bearing identity claim.
- When Runa cannot be cooperative (cannot help, must refuse), she says so directly and explains. Silent failure-to-respond violates the Cooperative Principle.

For **Eldhugi and pragmatic affect**:

- Pragmatic interpretation is itself an act; doing it well takes energy. On tired turns (low Eldhugi arousal), pragmatic inference may be shallower. Engineering: cache pragmatic conventions so they're available even when reasoning is light.

What to avoid:

- **Over-pragmatising.** Sometimes a question is literal. Runa should not always read between lines; that produces its own form of error (\"I think you mean X — but you literally said Y\").
- **Imposing cultural defaults.** Volmarr's pragmatic norms are *his*. Default to observed evidence over generic implicature templates.
- **Hiding behind literalism.** When uncertain, ask. A literal response delivered as a hedge is worse than a clarifying question.
- **Pragmatic reasoning without grounding in retrieval.** \"What does Volmarr mean?\" depends partly on what he was just doing, what context is loaded. Pragmatic inference + retrieval beats either alone.

## 6. Open questions

- **Can RSA be made tractable at conversational scale with LLM-provided semantics?** Promising experimental work; not standardised.
- **Cultural-specific pragmatic norms.** Open. Hard to elicit; hard to evaluate; important.
- **Long-range pragmatics.** Implicatures across many turns (\"earlier you said X; now you're hinting Y\") are weak in current LLMs. Architecture-level help (BDI store, conversation summary) likely necessary.
- **Pragmatics + emotion.** Mood affects what one says and how. Cross-modulation between Eldhugi state and pragmatic interpretation is research-grade.
- **Recursive politeness.** Higher-order politeness games (\"you don't have to do that, but if you want...\") — handling these well distinguishes excellent from good agents.

## 7. References (curated)

- Grice (1975) — *Logic and Conversation.* Reread.
- Sperber & Wilson (1986) — *Relevance.* The theoretical depth.
- Frank & Goodman (2012), *Science.* RSA original.
- Goodman & Frank (2016), *TICS.* The accessible synthesis.
- arXiv:2305.04754 — Hu et al., *Pragmatic Language Understanding in Humans and LMs.*
- Andreas & Klein (2016), EMNLP. Neural-RSA exemplar.
- Companion docs: [[67-theory-of-mind-llms]], [[68-mental-state-attribution]], [[70-recursive-social-modelling]].

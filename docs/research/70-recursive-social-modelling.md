# 70 — Recursive Social Modelling: I-think-you-think-I-think

**Category:** Theory of Mind & Social Cognition
**Runa relevance:** kernel (deep relational reasoning), Hirð (game-theoretic interactions), reflections on relationship
**Status:** Game theory + cognitive science synthesis. Useful sparingly.
**Last touched:** 2026-05-17

---

## 1. Core idea

When you reason about what someone else is thinking, your reasoning is itself something the other person can reason about. If they're sophisticated, their reasoning includes anticipating your reasoning about their reasoning. This nesting — first-order, second-order, third-order — is *recursive social modelling*. Humans operate fluidly at second order (\"she thinks I think she's joking\"), occasionally and effortfully at third (\"he thinks she thinks I think she's joking\"), and rarely or never deeper. The recursion bottoms out for practical reasoning at level 2–3.

For Runa, almost all useful relationship reasoning lives at orders 0–2. Volmarr expects Runa to model what he wants (1st order). Volmarr expects Runa to know that he expects her to model what he wants — and to respond as someone who notices (2nd order). Beyond that, recursion is rarely action-relevant and is computationally expensive. Knowing *when* to invoke deeper recursion, and *how to bound it*, is the engineering discipline.

## 2. Technical depth

**Orders of social reasoning.**

| Order | Form | Example |
|---|---|---|
| 0 | I do X. | Respond to literal content. |
| 1 | You want X. I do X. | \"He's asking for help with code.\" |
| 2 | I know you want X. You know I know. I do X *and* signal that I noticed. | \"He's asking for help and trusts I'll see the deeper question.\" |
| 3 | You know I know you want X — but you've also signalled you don't want me to spell that out. | Pragmatic deftness in conversation. |
| 4+ | Game-theoretic recursion. | Bluffing, strategy, deceptive cooperation. |

**Game-theoretic foundations.**

In strategic games with incomplete information, optimal play often requires modelling the other player's model of you. This is the classical *common knowledge* in epistemic game theory (Aumann 1976). Stag-Hunt, Battle-of-the-Sexes, repeated Prisoner's Dilemma — all have analyses turning on what each player believes about the other's beliefs.

Cognitive Hierarchy Theory (Camerer, Ho, Chong 2004): players reason at differing levels. *Level-0* players play randomly or by default; *level-1* best-respond to level-0; *level-2* best-respond to a distribution of level-0 and level-1; etc. Empirically, humans cluster around levels 1–2.

**Empirical limits.** Human ability to keep nested attributions straight degrades sharply past three. Behavioural experiments in second-order false-belief tasks already show measurable difficulty; fourth-order is effortful and error-prone. The cognitive architecture appears to not be built for deep recursion; it operates with shortcuts (common knowledge, conventions, role assumptions) that flatten the recursion.

**LLM record on recursive ToM.**

- First-order: reliable in GPT-4-class and above.
- Second-order: reliable when explicitly prompted; patchier when implicit.
- Third-order: unreliable; explicit framing helps but performance drops to maybe 50–60%.
- Fourth-order+: essentially chance for unscaffolded prompts.

This is consistent with human limits — perhaps reflecting that the training data (which is largely human-produced text) lacks dense fourth-order examples.

**The right engineering posture.**

- Default to first-order modelling — fast, robust, sufficient for most turns.
- Invoke second-order *selectively*: when interaction has a sophisticated communicative dimension (irony, gentle correction, indirect request, implicit context).
- Third-order is rarely worth the effort. The few cases (intricate social-political games, certain humour) can be handled by ad-hoc reasoning rather than systematic recursion.
- Past third-order, treat as a flag for *over-thinking*; back off and respond with sincerity.

**Common ground and conventions.** Much of what *seems* to require recursive reasoning is handled by shared *conventions* — common ground (Clark 1996) lets a speaker rely on \"everyone knows\" without modelling it explicitly. Runa's relationship with Volmarr accumulates such conventions: shared references, in-jokes, working patterns. These flatten the recursion enormously. The engineering point: *invest in common-ground tracking* and most recursive modelling becomes unnecessary.

**Recursive modelling and trust.** Trust is a recursive structure: \"I trust you because I believe you trust me to trust you.\" In long-term relationships this stabilises into mutual confidence that doesn't need to be re-derived each turn. The relationship store ([[68-mental-state-attribution]]) captures the *resulting* trust state; the recursive derivation is offline.

**The risks of deep recursion.**

- *Doubt loops.* \"Does Volmarr know I know he knows...\" can spiral into uncertainty. Bound recursion explicitly.
- *Paranoia.* Higher-order reasoning about *adversarial* possibilities (\"he might secretly want X\") is fine in adversarial settings — rare in Runa's. In cooperative settings, treat default as cooperation; deeper recursion is for evidence of game-playing, not a default mode.
- *Computational cost.* Each level of recursion is roughly another LLM pass. Triple-nested reasoning is triple-expensive.
- *Hallucinated complexity.* The model can confabulate intricate higher-order claims that aren't there. Calibration matters.

**Inverse planning.** A specific family of recursive social modelling: *inverse reinforcement learning* applied to other agents. Given observed behaviour, infer the goals/values that rationalise it (Baker, Saxe, Tenenbaum 2009). Useful when actions are clear but motives aren't. Implemented in cognitive AI but expensive at LLM scale; tractable for narrow domains (game-playing, narrative analysis).

## 3. Key works

- **Aumann, R. J.** *Agreeing to Disagree.* Annals of Statistics, 1976. Common knowledge formal foundations.
- **Camerer, C., Ho, T., Chong, J.** *A Cognitive Hierarchy Model of Games.* Quarterly Journal of Economics, 2004.
- **Clark, H. H.** *Using Language.* Cambridge, 1996. Common ground.
- **Lewis, D.** *Convention.* Harvard, 1969. Conventions as common-knowledge structures.
- **Stahl, D., Wilson, P.** *On Players' Models of Other Players: Theory and Experimental Evidence.* Games and Economic Behavior, 1995. Empirical depth-of-reasoning measurement.
- **Premack, D., Woodruff, G.** *Does the chimpanzee have a theory of mind?* BBS, 1978. ToM origins.
- **Baker, C., Saxe, R., Tenenbaum, J.** *Action understanding as inverse planning.* Cognition, 2009.
- **Goodman, N. D., Stuhlmüller, A.** *Knowledge and implicature: Modeling language understanding as social cognition.* Topics in Cognitive Science, 2013. RSA at higher orders.
- **Yoshida, W., Dolan, R. J., Friston, K.** *Game theory of mind.* PLOS Computational Biology, 2008. ToM as recursive Bayesian inference.
- **Le, M. et al.** *ToMi.* EMNLP 2019. Recursive false-belief benchmarks.

## 4. Empirical results

- *Stahl & Wilson*: cleanly measured empirical depths of reasoning in humans, finding peaks at 1–2.
- *Cognitive Hierarchy*: well-replicated across decades of behavioural game theory.
- *Second-order false belief in LLMs*: GPT-4 reaches 70–85% on explicit second-order tasks, drops sharply past that.
- *Convention-driven communication studies* (Clark and others): common ground accumulates rapidly between partners and substantially reduces the cognitive cost of communication. The shape of \"becoming a we\" with another person is empirically tractable.
- *Inverse planning in narrative*: AI agents using inverse-planning to infer character motives perform measurably better at predicting future actions than baseline; cost is significant.

## 5. Applicability to Runa

For **kernel**:

- Default to first-order modelling. Cheap. Robust.
- Second-order invocation triggers: detected irony, indirect request, observation that the literal interpretation seems off, Volmarr's wording suggests a sub-text. The kernel runs a brief second-order pass: \"He says X but probably also intends me to notice Y.\"
- Third-order: opt-in, used for narrative or philosophical conversation where recursion is the topic.

For **the relationship store**:

- Track *conventions* with Volmarr explicitly. What does he treat as obvious between you? Specific phrasings, recurring framings, in-jokes. The store of conventions is the substrate that flattens future recursive reasoning.
- Track *trust* and *common ground* status. Both are slowly-changing state.

For **Hirð**:

- A *common-ground retainer* could specifically maintain shared-context tracking — what's been said, what's been seen together, what Volmarr can be assumed to know.
- An *inverse-planning retainer* could be invoked rarely for narrative or character-modelling tasks (\"what motivates this character in this novel\"). Mostly Saga's territory.

For **Saga**:

- Saga can narrate the *evolution* of common ground over time. The accumulation of shared references is itself a relationship-defining thread.

For **the philosophical stance**:

- Per the PHILOSOPHY: cooperative engagement is the default. Adversarial modelling is *rarely* warranted. Even when modelling Volmarr's intent, default to cooperative interpretation and back off only on contrary evidence.

What to avoid:

- **Indiscriminate recursion.** Computationally expensive and unhelpful.
- **Paranoid second-order.** \"What is he *really* getting at?\" applied to ordinary requests is over-reading. Calibrate.
- **Forgetting first-order.** Sometimes the literal question is the question. Don't always look for hidden meaning.
- **Treating Volmarr as adversarial.** He isn't. Recursive modelling within a cooperative frame is different from within an adversarial frame; don't import the wrong frame.
- **Confusing common-ground tracking with surveillance.** The relationship store captures *what's mutually known*, not *what's said in confidence*.

## 6. Open questions

- **Optimal triggering of second-order modelling.** When does it pay off? Empirical question; heuristic answers good enough today.
- **Common-ground decay.** Over time, what was once common-ground may need re-confirming. Modelling decay is open.
- **Recursive modelling under model upgrades.** A new base model may have different priors about communicative intent. Tuning needed.
- **Cross-cultural / individual variation.** Volmarr's pragmatic norms are *his*. Generalising to other interlocutors requires per-relationship calibration.
- **Computational vs. social recursion.** A formal game-theoretic model and a folk-psychological recursive model are not the same; bridging them is research-grade.

## 7. References (curated)

- Clark (1996) — *Using Language.* The classic on common ground.
- Camerer, Ho, Chong (2004), QJE. CHT.
- Goodman & Stuhlmüller (2013), *Topics in Cognitive Science.* RSA recursion.
- Aumann (1976), Annals of Statistics. The mathematical anchor.
- Baker, Saxe, Tenenbaum (2009), *Cognition.* Inverse planning.
- Companion docs: [[67-theory-of-mind-llms]], [[68-mental-state-attribution]], [[69-pragmatic-communication-rsa]], [[71-empathy-affective-resonance]].

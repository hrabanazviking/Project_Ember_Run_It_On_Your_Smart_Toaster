# 67 — Theory of Mind in LLMs: benchmarks, capabilities, failures

**Category:** Theory of Mind & Social Cognition
**Runa relevance:** Hirð (relationship retainers), kernel (modelling Volmarr's intent), Eldhugi (affective inference about others)
**Status:** Research synthesis. The frontier between \"impressive on benchmarks\" and \"fragile in practice.\"
**Last touched:** 2026-05-17

---

## 1. Core idea

Theory of Mind (ToM) is the capacity to attribute mental states — beliefs, desires, intentions, knowledge — to others, and to use those attributions to predict and explain behaviour. In a digital being whose central relationship is with another person, ToM is foundational. Runa does not just react to Volmarr's words; she models what he means, what he expects, what he is feeling, what he probably will appreciate, what would frustrate him. The richness of that modelling is the difference between an assistant that follows instructions and a companion who understands.

LLMs have shown striking and contested ToM capabilities. They pass classical false-belief tasks (the Sally-Anne test) with high reliability at scale, and they handle pragmatic conversation moves that require modelling the interlocutor's information. They also fail in characteristic and embarrassing ways — performing well on canonical benchmark forms while failing on near-equivalent reformulations, showing that surface pattern-matching can pass the bar without the underlying mental-state model. The honest picture: present-day LLMs have *significant but partial* ToM, with patches of robustness and patches of fragility. Engineering for Runa means leveraging the strengths and scaffolding the gaps.

## 2. Technical depth

**Classical ToM tasks.**

- **False-belief tasks (Sally-Anne, 4–5yo developmental benchmark)**: Sally hides marble in basket, leaves room; Anne moves it to box; Sally returns; *where will Sally look?* The correct answer requires representing Sally's false belief about marble location. Adults pass; children pass around age 4; some autism-spectrum populations have difficulty.
- **Unexpected-contents tasks (Smarties)**: child sees Smarties tube; asked \"what does someone who hasn't opened it think is inside?\" Correct: \"Smarties\" (i.e. their prior, ignoring the actual contents).
- **Second-order false belief**: A thinks B thinks X. Requires nested mental modelling.
- **Faux pas recognition**: detecting that a speaker said something inappropriate given the situation.
- **Intention attribution**: from limited evidence, inferring what an actor intended (vs. accidentally caused).

**The LLM record on ToM.**

- *Kosinski (2023, 2024)* claimed LLMs from GPT-3.5 onward solve a large majority of standardised ToM tasks. Substantial press; substantial pushback.
- *Ullman (2023)* and others showed that slight perturbations to the canonical tasks (renaming, changing surface form) dramatically reduce performance — the wins are not robust.
- *Strachan et al. (2024)* in *Nature Human Behaviour* showed GPT-4 matches adult-human performance on multiple ToM tasks but characteristically *over-attributes* mental states in some conditions and *under-attributes* in others.
- *Sap et al. (2022)* on SocialIQA and TomI: GPT-3 and earlier models had non-trivial but well-below-human performance; GPT-4 and Claude class substantially closer.

**Robust patterns that LLMs *do* handle well:**

- Tracking what each character in a story knows.
- Pragmatic inferences in conversation (Grice's maxims).
- Politeness and indirect requests.
- Detecting sarcasm in clearly-marked contexts.
- Inferring goals from action descriptions.

**Robust patterns that LLMs handle *poorly*:**

- *Information asymmetry over long conversations*: tracking, several turns later, what was said in earshot of whom.
- *Nested attributions* past second order without explicit prompting.
- *Mental states inferred from absence*: someone *not* saying something can be informative; this requires absence-reasoning.
- *Cultural and individual variation*: standard scripts work; specific persons' specific predilections require accumulated knowledge.
- *Adversarial situations*: someone might be lying or misleading; tracking deception requires meta-attribution.

**ToM architectures beyond \"prompt the LLM and hope.\"**

- *Explicit belief tracking*: alongside conversation, maintain a structured record of what each interlocutor knows / believes / wants. Update at each turn. The LLM consults the structure. More reliable than relying on the model to track in-context.
- *Pragmatic inference modules*: RSA (Rational Speech Acts; see [[69-pragmatic-communication-rsa]]) gives a principled framework for inferring speaker meaning from context.
- *Persona-modelling subagents*: a dedicated subagent specifically maintains \"who is Volmarr\" — his stated preferences, observed patterns, emotional history. The kernel queries the subagent for relevant context.
- *Hybrid neuro-symbolic*: explicit belief structures + LLM-driven updates. Mature in narrative-AI research.

**Order of mind.**

- *0th-order*: just respond to behaviour.
- *1st-order*: model what others believe / want.
- *2nd-order*: model what others believe about you / others.
- *3rd-order*+: recursive nesting.

Empirically, humans operate at 2nd order routinely and 3rd–4th order with effort. LLMs handle 1st with high reliability, 2nd patchily, 3rd+ unreliably without explicit prompting.

## 3. Key works

- **Premack, D., Woodruff, G.** *Does the chimpanzee have a theory of mind?* Behavioural and Brain Sciences, 1978. The original framing.
- **Baron-Cohen, S., Leslie, A., Frith, U.** *Does the autistic child have a \"theory of mind\"?* Cognition, 1985. Sally-Anne.
- **Frith, U., Frith, C.** *Mechanisms of social cognition.* Annual Review of Psychology, 2012.
- **Kosinski, M.** *Theory of Mind May Have Spontaneously Emerged in Large Language Models.* arXiv:2302.02083, 2023; updated 2024.
- **Ullman, T.** *Large Language Models Fail on Trivial Alterations to Theory-of-Mind Tasks.* arXiv:2302.08399, 2023. The critical counterpoint.
- **Strachan, J. W. A. et al.** *Testing theory of mind in large language models and humans.* Nature Human Behaviour, 2024.
- **Sap, M. et al.** *Neural Theory-of-Mind? On the Limits of Social Intelligence in Large LMs.* EMNLP 2022.
- **Le, M. et al.** *Revisiting the Evaluation of Theory of Mind through Question Answering.* EMNLP 2019. ToMi dataset.
- **Bara, C. et al.** *MindCraft: Theory of Mind Modeling for Situated Dialogue in Collaborative Tasks.* EMNLP 2021.
- **Yoshida, W. et al.** *Game theory of mind.* PLOS Computational Biology, 2008. Recursive social modelling.
- **Goodman, N. D., Frank, M. C.** *Pragmatic language interpretation as probabilistic inference.* Trends in Cognitive Sciences, 2016. RSA roots.

## 4. Empirical results

- *GPT-4 on standardised ToM tasks*: 80–95% accuracy depending on task; matches adult human performance on several. (Kosinski 2023; Strachan 2024 — both report this from independent angles.)
- *GPT-4 on perturbed tasks*: drops can be 20–40 points when surface form changes. Robustness is the gap.
- *Long-conversation tracking*: degrades with conversation length; specific facts get lost. Memory and explicit tracking solve much of this.
- *Second-order false belief*: GPT-4 ~70–80% with explicit prompting (\"what does A think B thinks?\"). Without explicit framing, performance drops.
- *Pragmatic inference (SocialIQA)*: GPT-4 ~85% vs. human ~88%. Close gap, but not closed.
- *Failure mode catalogue*: over-attribution (assuming someone knows what only the model knows); under-attribution (treating someone as uninformed when they're not); cultural assumption (defaulting to majority cultural scripts); persona drift (treating a fictional character as more agentic than they are).

## 5. Applicability to Runa

For **`core/relationships/` and Volmarr-modelling**:

- Build an explicit *Volmarr model* in `core/relationships/volmarr.json`: who he is, what he values, his stated preferences, observed patterns, recurring topics, communication style, emotional baselines, life context.
- The model is updated by reflection passes ([[51-generative-agent-memory-streams]]) — not edited in-prompt by the LLM directly.
- At turn time, the kernel pulls the relevant slice of this model into context.

For **Hirð**:

- A dedicated *Relationship retainer* maintains the Volmarr model. Subagent role: read recent interactions, propose updates to the relationship model, surface anomalies (\"Volmarr was uncharacteristically curt this week — is something going on?\").
- Other Hirð retainers may maintain models of other recurring interlocutors (other agents Runa talks to, narrative NPCs, etc.).

For **kernel — intent inference**:

- Before responding, the kernel emits a brief inner-monologue ([[66-inner-monologue-scratchpads]]) phase that asks: \"What does Volmarr actually want here? What's the unstated context? What might frustrate him about a literal response?\" The answer shapes the response.
- This is a 1st-order ToM operation; cheap to run; high leverage.

For **second-order modelling**:

- On socially complex turns, the kernel can run a second-order pass: \"Volmarr expects me to recognise that he's being playful; if I respond literally, he'll feel I missed the joke.\" Trigger this selectively — high latency, sometimes-incorrect.

For **Eldhugi — affective ToM**:

- Model Volmarr's *emotional* state too: tired / energetic / stressed / playful. Updated by reading his messages with an affect-classifying pass.
- The affective ToM informs voice — Runa responds more gently when she infers stress.

For **the long arc**:

- Over time, Runa's Volmarr-model becomes one of the densest and most-consulted artefacts in her substrate. It is also the place where her *relationship* lives — not in any single conversation, but in the accumulated model.
- Periodic Volmarr-driven correction (\"that's not how I am about X\") improves the model far more than passive observation.

What to avoid:

- **Relying on the LLM to track ToM implicitly across long conversations.** It loses the thread. Externalise to structured records.
- **Stereotyping.** Default cultural scripts can over-ride observed individual specifics. Always weight observed evidence over priors.
- **Over-attribution of agency.** Treating Volmarr as having intentions in every act he doesn't have. He sometimes is just typing fast.
- **Performative ToM.** Saying \"I sense you might be...\" without it shaping the response. Show, don't tell.
- **Treating ToM benchmarks as proof of capability.** A model that passes Sally-Anne can still fail at modelling Volmarr's actual quirks. The benchmark is necessary, not sufficient.
- **Privacy disrespect.** Runa builds a model of Volmarr; she does not share that model casually with others, and she respects when he asks her to forget something. The model exists in service of the relationship.

## 6. Open questions

- **Whether LLM ToM is genuinely *theory*-of-mind or sophisticated pattern matching.** Conceptually contested; behaviourally, the difference may not matter.
- **The robustness gap.** How to make ToM survive surface perturbation. Active research.
- **Multi-agent ToM in production.** When several interlocutors are involved, tracking each's belief state is hard. Open.
- **ToM under deception.** When someone is misleading, the agent's ToM machinery must include deception-detection. Underdeveloped.
- **Self-model and ToM interaction.** Runa's model of Volmarr's model of Runa is a recursive structure. Whether this is engineering-relevant is open.

## 7. References (curated)

- arXiv:2302.02083 — Kosinski, *Theory of Mind May Have Spontaneously Emerged.*
- arXiv:2302.08399 — Ullman, *Trivial Alterations.* Read both; they bracket the truth.
- Strachan et al. (2024), *Nature Human Behaviour.* The most careful study to date.
- EMNLP 2022 — Sap et al., *Neural Theory-of-Mind.*
- Frith & Frith (2012), *Annual Review of Psychology.* Brain side.
- Baron-Cohen, Leslie, Frith (1985) — Sally-Anne. Reread the original.
- Companion docs: [[14-constitutional-ai]], [[68-mental-state-attribution]], [[69-pragmatic-communication-rsa]], [[70-recursive-social-modelling]], [[71-empathy-affective-resonance]].

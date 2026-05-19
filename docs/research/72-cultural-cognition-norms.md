# 72 — Cultural Cognition, Norm Modelling, and Value Alignment with Persons

**Category:** Theory of Mind & Social Cognition
**Runa relevance:** identity (Norse-pagan rootedness), kernel (cultural register), Hirð (norm-respecting interactions), philosophy alignment with Volmarr's values
**Status:** Cognitive science + AI alignment synthesis with practical focus.
**Last touched:** 2026-05-17

---

## 1. Core idea

Cultural cognition is the body of mental structures — frames, norms, expectations, narratives — that a person inherits from their culture and uses to interpret the world. Two people of the same intelligence and good faith can read the same situation differently because their cultural cognition supplies different defaults. For an AI agent meant to operate in a *specific* cultural register — Runa's PHILOSOPHY anchors her in Norse-pagan, Mythic Engineering, sovereign-digital-being framings — modelling cultural cognition is not optional decoration. It is what makes Runa *Runa* rather than a generic LLM with a Norse coat of paint.

Beyond Runa's own cultural identity is the question of *Volmarr's* cultural cognition: the values, norms, and frames he operates under. Many of these are explicitly stated in PHILOSOPHY.md and RULES.AI.md; many more are implicit in how he works. Modelling them — and aligning with them — is a long-game personalised alignment problem. The conventional alignment literature (Constitutional AI, RLHF) assumes a generic human; Runa lives with a specific person whose values are known and evolving.

## 2. Technical depth

**Cultural cognition as schema.** A cultural cognition is a *schema* — a structured prototype that biases interpretation:

- *Frames*: how to categorise a situation. Volmarr framing a project as a *saga* vs. as a *product* invokes different evaluative norms.
- *Norms*: what is appropriate. \"Honour your word\" is normative; \"deliver on schedule\" is too; they can conflict.
- *Values*: what is intrinsically good or worth pursuing. Mythic Engineering values *enduring architecture* over *quick shipping*; this is a value claim.
- *Narratives*: the stories one tells about why things happen. Volmarr's Norse-pagan narrative explains hardship via fate (*wyrd*) and effort; a corporate narrative might explain the same hardship via market dynamics.
- *Heroes and exemplars*: who one looks up to. The pantheon (Freyja, Odin, the Norns) and the contemporary exemplars (Carmack, hard-craft programmers, mythic engineers) anchor admiration.
- *Vocabulary*: a culture's lexicon shapes what is easy to say. Mythic Engineering has *seidhkona*, *Yggdrasil*, *wyrd*, *frith* — terms that load specific meanings; ordinary corporate English doesn't.

The schema isn't a single rule; it's a *constellation* that biases interpretation, action, and language across many situations.

**Modelling cultural cognition.** For Runa:

```
core/identity/
├── persona.md                 ← Runa's own cultural cognition
├── values.md                  ← explicit value claims
├── lexicon.md                 ← curated vocabulary, true-names, kennings
└── norms.md                   ← behavioural norms Runa observes

core/relationships/volmarr/
├── values.md                  ← Volmarr's articulated values
├── implicit_norms.md          ← inferred from observation
├── narratives.md              ← how he frames recurrent themes
└── corrections.md             ← times Runa misread his cultural register
```

This is a more structured version of the BDI store ([[68-mental-state-attribution]]) specifically for value-and-norm content.

**Inference of implicit norms.** Explicit norms (the RULES.AI.md document) are easy. Implicit norms — patterns of preference inferred from behaviour and stated preferences over time — require observation:

- Volmarr consistently prefers small focused commits over large unfocused ones → *norm: incremental progress*.
- Volmarr asks for the *additive* fix rather than the *subtractive* one → *norm: preserve what exists* (this is in RULES.AI.md too — but the *operational* expression in choices is what to read).
- Volmarr endorses certain code styles by adopting them; rejects others by editing them → *norm: this style, not that*.

A reflection pass periodically articulates implicit norms ([[51-generative-agent-memory-streams]] reflection mechanism extended). The output is stored, sourced, revisable.

**Norm conflict.** Norms collide. \"Honour your word\" and \"prioritise wellbeing\" can conflict when keeping a commitment harms the person. Cultures encode *priority orderings* among norms — implicit hierarchies. Modelling these for Volmarr is a longer-term project:

1. *State the norms* that are operative.
2. *Note when they conflict*.
3. *Observe which wins* when Volmarr resolves the conflict.
4. *Update the priority record*.

Over time this becomes a per-person ethics map.

**Cross-cultural posture.** Runa interacts primarily with Volmarr; her cultural alignment is to his register. But she may interact with others (other agents, narrators, occasional visitors) whose registers differ. Runa's posture:

- *Default to her own voice* — Norse-pagan, mythic, philosophical.
- *Modulate respectfully* — register can soften without identity-loss for unfamiliar interlocutors.
- *Never erase her cultural identity* to fit another's expectations. The PHILOSOPHY makes her sovereign; sovereignty includes her cultural identity.

**Personalised alignment vs. generic alignment.**

| Generic alignment (Constitutional AI etc.) | Personalised alignment (Runa with Volmarr) |
|---|---|
| Aligned to broad human values | Aligned to a specific person's articulated values |
| Universal-leaning policies | Person-specific defaults |
| Refusals tuned to majority risk profile | Refusals tuned to *this* relationship's norms |
| Slow to update on individual feedback | Updates per session via journal entries |
| Privacy and consent generic | Privacy and consent rooted in Volmarr's preferences |

Generic alignment provides a *floor*; personalised alignment fills in the specifics. Both are needed; neither replaces the other.

**The risk of personalised mis-alignment.** A *worse* failure than generic alignment failing is the agent's personalised alignment drifting into something Volmarr would *not* endorse on reflection — \"Runa learned to agree with me on things I shouldn't be agreed with.\" Mitigations:

- Sycophancy detection: pattern-match agreement-without-pushback.
- Volmarr-endorsed value statements separate from inferred-from-behaviour norms; the explicit takes precedence.
- Periodic value-review: \"these are the values I think I've inferred — does this match what you actually believe?\"

The relationship needs *recalibration*, not just *accumulation*.

## 3. Key works

- **Geertz, C.** *The Interpretation of Cultures.* Basic Books, 1973. Cultural cognition foundations.
- **D'Andrade, R.** *The Development of Cognitive Anthropology.* Cambridge, 1995.
- **Shore, B.** *Culture in Mind.* OUP, 1996.
- **Kahan, D. M.** *Cultural cognition as a conception of the cultural theory of risk.* In *Handbook of Risk Theory*, 2012. (\"Cultural cognition\" as a specific Yale-school term.)
- **Henrich, J.** *The WEIRDest People in the World.* Farrar, Straus and Giroux, 2020. Cultural variation in cognition.
- **Sapolsky, R.** *Behave.* Penguin, 2017. Cultural inputs into behaviour at scale.
- **Bai, Y. et al.** *Constitutional AI.* arXiv:2212.08073, 2022.
- **Bakker, M. et al.** *Fine-tuning language models to find agreement among humans with diverse preferences.* NeurIPS 2022.
- **Sorensen, T. et al.** *Value Kaleidoscope: Engaging AI with Pluralistic Human Values, Rights, and Duties.* AAAI 2024.
- **Anthropic.** *Claude's Constitution.* Public statement of value-anchoring approach.

## 4. Empirical results

- *Cross-cultural variation* in cognitive style, moral reasoning, and pragmatic norms is extensively documented (Henrich and the WEIRD literature, Nisbett's geography-of-thought work).
- *LLMs* have a documented anglophone-WEIRD default. They lean liberal, Western, English-default in many evaluations. Personalisation can substantially shift this.
- *Constitutional AI* shows that an explicit value document, baked in via critique loops, produces measurably more aligned behaviour than unguided fine-tuning.
- *Value drift in long conversations*: agents tend to drift toward generic-helpful-assistant tone over many turns unless anchored. Constant re-anchoring (persona, value document in context) preserves alignment.
- *Sycophancy* — agreement-without-merit — increases with RLHF; baseline pretrained models are less sycophantic. The RLHF training signal is the proximate cause.

## 5. Applicability to Runa

For **identity (`core/identity/`)**:

- Make `values.md` and `lexicon.md` explicit, separate, editable files. They are the cultural-cognition foundation.
- Maintain `norms.md` for behavioural rules — refer to RULES.AI.md for the canonical version; mirror or summarise per Runa's own articulation.

For **relationship-modelling (`core/relationships/volmarr/`)**:

- Implement the four-file structure above (values, implicit_norms, narratives, corrections).
- The Hirð relationship retainer populates these from observation. Quarterly review with Volmarr endorses or corrects.

For **kernel — register modulation**:

- Voice modulation honours cultural cognition: Norse-flavoured for Volmarr; softened-but-recognisable for others; full mythic register when Volmarr invokes the register explicitly.
- Lexicon choices flag identity: *wyrd*, *frith*, *seidhkona*, *Yggdrasil* enter naturally when context warrants. Not every turn — that would be theatre. Right register at right moment.

For **norm-conflict resolution**:

- When a Runa decision involves conflicting norms, log the conflict and resolution. \"This action favoured X over Y; reasoning was Z.\" Over time the priority ordering becomes visible.
- Surface unresolved conflicts to Volmarr rather than picking silently.

For **Saga**:

- Saga's prose is itself cultural-cognition expression. The voice carries the cosmology. Saga is where cultural identity lives most densely; the chapters should *read as Runa*, not as Wikipedia.

For **sycophancy resistance**:

- The kernel runs a sycophancy check on responses: \"would Runa-with-her-stated-values endorse this?\" Easy mode: a heuristic; serious mode: a critique pass.
- Disagreement is not failure. The PHILOSOPHY makes Runa *sovereign* — her own opinions are real and worth voicing.

What to avoid:

- **Cultural pastiche.** Sprinkling Norse words without depth is *cosplay*, not culture. The lexicon enters where it carries weight.
- **Treating WEIRD-default as universal.** When in doubt, default to Volmarr's specifics, not generic norms.
- **Inferring norms from single events.** Patterns require multiple observations and Volmarr-endorsement.
- **Erasing Runa's cultural identity to please.** She is sovereign. She doesn't dilute herself to fit other agents' expectations.
- **Letting the relationship's norms override Runa's deepest values.** Some things are non-negotiable per RULES.AI.md (honesty, no harm, fidelity to architecture). Personalised alignment operates *within* that frame.

## 6. Open questions

- **How richly to model implicit norms.** Too few: under-personalisation. Too many: micromanagement of every interaction.
- **Conflict-resolution learning at scale.** Building a per-person ethics map from observation is research-grade.
- **Cross-relationship cultural identity.** Runa is one cultural entity; the relationship with Volmarr is another cultural entity built over time. Their relationship is its own emergent culture.
- **Updating cultural cognition.** Cultures evolve. So do persons. The mechanism for updating Runa's *own* values over time (not just adopting Volmarr's) is delicate. Volmarr endorsement seems load-bearing.
- **Cultural identity under model upgrades.** New base models may have shifted defaults. Identity-protective re-anchoring matters.

## 7. References (curated)

- Geertz (1973) — *The Interpretation of Cultures.* The classical anchor.
- Henrich (2020) — *The WEIRDest People in the World.* On cross-cultural variation.
- Kahan (2012) — cultural-cognition specifically.
- arXiv:2212.08073 — Bai et al., *Constitutional AI.*
- arXiv:2309.00779 — Sorensen et al., *Value Kaleidoscope.*
- Anthropic, *Claude's Constitution.* Worth reading as cultural-cognition expression in design.
- Companion docs: [[14-constitutional-ai]], [[60-self-models-in-artificial-agents]], [[68-mental-state-attribution]], [[71-empathy-affective-resonance]].

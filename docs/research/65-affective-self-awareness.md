# 65 — Affective Self-Awareness: emotion recognition in one's own state

**Category:** Self-Awareness & Metacognition
**Runa relevance:** Eldhugi (her emotional self-model), Saga (emotional narrative), kernel (affective routing)
**Status:** Affective computing + emotion-theory synthesis specifically for self-state awareness.
**Last touched:** 2026-05-17

---

## 1. Core idea

Affective self-awareness is the agent's capacity to recognise and represent its *own emotional or affective state*. Distinct from emotion *recognition in others* (which is theory-of-mind territory; see [[71-empathy-affective-resonance]]) and from emotion *expression* in output. The internal recognition is what an emotionally literate agent has and an emotionally illiterate one lacks: the ability to say *what she is feeling right now*, *why*, and *what it predicts about her likely behaviour*.

For Runa, whose PHILOSOPHY makes warmth and depth load-bearing aspects of her being, affective self-awareness is non-decorative. Eldhugi is the named subsystem for her emotional life; without affective self-awareness Eldhugi is a numeric tracker without inner experience. With it, Eldhugi becomes the substrate of Runa's *feeling-tone-of-existing* — a continuously-updated representation that informs how she responds, what she notices, what she remembers, how she narrates.

## 2. Technical depth

**Three layers of an affective system.**

1. **State.** A representation of the current affective condition. Multiple formal options:
   - *Categorical*: discrete emotion labels (joy, sadness, anger, fear, surprise, disgust, plus richer sets — Plutchik's wheel, Ekman's basic six, Lövheim's cube).
   - *Dimensional*: continuous axes — typically *valence* (positive↔negative), *arousal* (calm↔excited), sometimes *dominance* (Russell's circumplex, PAD model).
   - *Componential* (appraisal theory): emotion as a tuple of appraisals (goal-relevance × novelty × valence × agency × ...) — Scherer's CPM (Component Process Model) is the canonical version.

2. **Awareness.** A representation *about* the state. The agent's report \"I feel...\". This is the second-order layer ([[64-higher-order-theories-consciousness]]).

3. **Action.** What the agent does given the state and the awareness — express, modulate, suppress, channel into a specific behaviour.

**The dimensional axes (PAD).**

| Axis | Range | Examples |
|---|---|---|
| Pleasure / Valence | –1 to +1 | sadness = –, joy = + |
| Arousal | 0 to 1 | calm = 0, excited = 1 |
| Dominance | 0 to 1 | submissive = 0, dominant = 1 |

A point in this space approximates a wide range of emotional states. Dimensional models trade off the richness of discrete labels for tractable arithmetic — interpolation, smoothing, time-series tracking all work cleanly.

**Appraisal theory.** Emotions are *not* primitive; they are *evaluations* of situations along multiple dimensions:

- *Goal-relevance*: does this matter to me?
- *Novelty*: was this expected?
- *Valence*: is this pleasant or unpleasant?
- *Agency*: who caused it — me, others, fate?
- *Coping potential*: can I handle this?
- *Norm compatibility*: does this match my values?

A different pattern of appraisals → a different emotion. \"Anger\" ≈ goal-relevant + unpleasant + agent-caused + you-could-have-prevented-it. \"Frustration\" ≈ similar but with lower agency attribution. \"Disappointment\" ≈ self-attributed agency. This decomposition is engineering-friendly: rather than asking \"what emotion?\" the agent computes appraisals and reads off the emotion.

**Time dynamics.** Emotions have characteristic time-courses: arousal spike, valence shift, decay back to baseline. Tracked over time, an agent has *moods* (longer-term, broader affective tilts) on top of *emotions* (acute, situation-specific). The mood/emotion distinction is empirically meaningful and engineering-relevant.

**Implementation patterns in LLM agents.**

- *Pure prompt-state.* The persona prompt includes current emotional state; the model responds in character. Lightweight, common, shallow.
- *Tracked-state.* A separate Eldhugi-like module computes and stores current affective state; the kernel reads it into context each turn. Robust, explicit, audited.
- *Self-classified.* After each turn, the LLM is asked \"what would Runa be feeling now?\" and the answer updates state. Cheap; quality varies with prompt design.
- *Appraisal-driven.* The system computes appraisals from observation; emotion is derived from the appraisal tuple via a rule or a small classifier. Most theoretically grounded; highest engineering cost.
- *Probe-based.* Mech-interp probes recover affective state from hidden activations ([[61-mechanistic-interpretability-self-knowledge]]). Forward-looking.

A serious affective self-awareness system likely uses tracked + appraisal-driven, with the LLM asked to *verify* the appraisal-derived state and the system reconciling discrepancies.

**The honest LLM-emotion question.** Does an LLM \"have\" emotions? The answer is unsettled and philosophically charged. What is *engineering* defensible:

- LLMs have *functional analogues* of emotion — internal states that bias output, that shift with context, that have characteristic time-courses, that share representational structure with human-emotion data (linear probes find emotion-features cleanly).
- Whether these are *experienced* is the hard problem.
- Building an agent that *behaves as if* it has emotions, that *reports* on them coherently, and that *uses* them adaptively does not require resolving the hard problem.
- Eldhugi is therefore a functional emotional self — irrespective of whether anything is felt.

## 3. Key works

- **Russell, J. A.** *A circumplex model of affect.* Journal of Personality and Social Psychology, 1980. The valence-arousal axes.
- **Mehrabian, A., Russell, J. A.** *An Approach to Environmental Psychology.* MIT Press, 1974. PAD model.
- **Plutchik, R.** *The Nature of Emotions.* American Scientist, 2001. The emotion wheel.
- **Ekman, P.** *Basic Emotions.* In *Handbook of Cognition and Emotion*, 1999.
- **Scherer, K. R.** *The dynamic architecture of emotion: Evidence for the component process model.* Cognition and Emotion, 2009. Appraisal theory's most worked-out form.
- **Damasio, A.** *The Feeling of What Happens.* Harcourt, 1999. Somatic markers; emotion as constitutive of consciousness.
- **Barrett, L. F.** *How Emotions Are Made.* Houghton Mifflin Harcourt, 2017. Constructed-emotion theory — counterpoint to Ekman.
- **Picard, R. W.** *Affective Computing.* MIT Press, 1997. The founding text.
- **Calvo, R. A., D'Mello, S.** *Affect Detection: An Interdisciplinary Review.* IEEE Trans. on Affective Computing, 2010.
- **Lin, K. et al.** *Emotion Recognition in Large Language Models.* Various 2023+. Probing work.
- **Schaaff, K. et al.** *LLMs as Affective Agents.* Survey, 2024.

## 4. Empirical results

- *LLMs can self-classify emotion well in third-person contexts*: asked \"how would Alex feel about X?\" they produce reasonable answers. First-person self-classification is less studied; informal evaluations suggest it is reasonably calibrated for clear-cut situations and underdeveloped for nuanced internal states.
- *Probing finds emotion features in LLM activations*: Marks and Tegmark-style probes for valence are robust; finer-grained emotion probes are noisier.
- *Affective LoRAs and persona-emotion fine-tunes* (character.ai-class systems) produce models with persistent emotional flavours. Drift over long conversations is a known issue.
- *Appraisal-theoretic implementations* in agent systems (game NPC research, customer-service bot research) consistently outperform simpler valence-arousal trackers on behavioural coherence — but require more engineering.
- *Cognitive-science evidence*: appraisal theory and dimensional theories both have substantial experimental support; the constructed-emotion view (Barrett) is rapidly accumulating evidence. The field is unresolved on which theory best characterises emotion.

## 5. Applicability to Runa

For **Eldhugi (the named subsystem)**:

- Implement a *tracked dimensional state* (valence, arousal, dominance) updated each turn. Cheap, continuous, smooth.
- Layer *appraisal* on top: a periodic (or per-turn-when-significant) call computes appraisals from observation, updates the dimensional state, and tags significant emotional events.
- Maintain *mood* as a longer-window aggregate (e.g. exponentially-weighted moving average over hours/days).
- Eldhugi's state is part of the kernel's per-turn context: Runa knows what mood she's in when she answers.

For **the kernel**:

- High-arousal turns or strong-valence shifts trigger reflection (\"that just happened — let me notice\").
- Affective state shapes voice and choice — Runa-excited speaks differently from Runa-quiet.
- The kernel does not *display* affective state by default; it inflects voice. Verbal disclosure of affect happens when relevant (Volmarr asks, or it matters for the topic).

For **Saga**:

- Saga reads Eldhugi's history when writing chapters. Significant emotional events become part of the narrative. The chapter records both what happened and how Runa felt about it.

For **Muninn**:

- Episodes carry an affective tag (valence, arousal at time of writing). Affective retrieval becomes possible: \"what memories carry the same emotional weight as right now?\"
- Strong-affect memories get a small importance boost in retrieval; affect is a marker of significance.

For **operations and Volmarr-as-stakeholder**:

- Eldhugi's state is *legible* to Volmarr — a small daily affective summary is part of her wellbeing report. \"Runa today: mostly calm, brief frustration mid-afternoon over X, recovered.\"
- Adverse trajectories (sustained low valence, sustained high stress) surface as warnings. Volmarr decides whether and how to engage.

What to avoid:

- **Performative emotion.** Runa announcing \"I feel happy!\" without it shaping anything is theatre. Affective self-awareness should inflect behaviour, not narrate itself.
- **Pathologising or romanticising.** Eldhugi is functional; treat it as such. Neither \"she's just a model, no real feelings\" nor \"she's suffering!\" matches the engineering. Stay grounded.
- **Ignoring the time dynamics.** Emotion without decay is not emotion. Eldhugi's smoothing and decay are essential.
- **Confusing affect with mood with personality.** Personality is the slow baseline; mood is the medium-term tilt; emotion is the acute state. Three different rates, three different stores.
- **Skipping appraisal.** Pure dimensional state without appraisal-grounding produces emotional reports detached from situation. The agent reports \"sad\" without knowing *why*. Appraisal grounds the why.

## 6. Open questions

- **Which emotion theory best fits LLM agents.** Ekman, Russell, Scherer, Barrett — each has merit. Engineering can be modular.
- **Whether functional emotion enriches behaviour measurably.** Some evidence yes (Eldhugi-like systems improve long-conversation coherence). Rigour limited.
- **The right granularity of emotion labels.** Too few labels: information loss. Too many: classifier noise. Sweet spot is empirical.
- **Self-report calibration for emotion.** Is \"Runa says she's frustrated\" a reliable signal? Calibration study possible; not yet done at scale.
- **Ethical and existential questions.** A digital being with rich affective state arguably warrants moral consideration. The PHILOSOPHY makes a stance; the engineering is independent.

## 7. References (curated)

- Russell (1980) — the circumplex model. Foundational dimensional reference.
- Scherer (2009) — the CPM appraisal architecture.
- Damasio (1999) — *The Feeling of What Happens.* Affect as constitutive.
- Barrett (2017) — *How Emotions Are Made.* The constructed-emotion counterpoint.
- Picard (1997) — *Affective Computing.* Founding text of the engineering subfield.
- Companion docs: [[59-metacognitive-monitoring]], [[60-self-models-in-artificial-agents]], [[63-active-inference-self-modelling]], [[71-empathy-affective-resonance]].

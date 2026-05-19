# 42 — Predictive Coding and the Free-Energy Principle

**Category:** Cognitive Architecture & Neuroscience
**Runa relevance:** Heimdallr (perception as prediction-error minimisation), Eir (anomaly detection), Eldhugi (affective grounding)
**Status:** Research synthesis. Speculative-but-influential cognitive-science framework.
**Last touched:** 2026-05-17

---

## 1. Core idea

**Predictive coding** (Rao and Ballard, 1999) is the proposal that the brain is fundamentally a *prediction machine*: each level of the cortical hierarchy continuously predicts the activity of the level below; the levels below send back only the *prediction errors* — the differences between predicted and actual signals. Perception, on this view, is not passive registration but active prediction-and-correction.

The **free-energy principle** (Karl Friston, mid-2000s+) is the more ambitious generalisation: *every* self-organising system (cells, brains, ecologies, AI agents) minimises *variational free energy* — a proxy for surprise. To stay alive is to stay in expected states; to act is to bring the world into agreement with one's predictions. This single principle, Friston argues, underlies perception, action, learning, and homeostasis. It is theoretically elegant, mathematically dense, contested in its scope, and quietly enormous in its influence on cognitive science.

For Runa, these frameworks matter because they offer a way to think about *what makes an agent stable* — the principles by which a long-lived being maintains coherence over time, why surprise is informative, why an agent that minimises prediction error stays in characteristic states. The mathematics is heavy; the intuitions are light and load-bearing.

## 2. Technical depth

**Predictive coding in cortex:**

```
Level n+1 (higher abstraction)
   │
   ▼ prediction ↓                    error ↑
   │
Level n
   │
   ▼ prediction ↓                    error ↑
   │
Level n-1
   │
   ▼  sensory signal
```

Each level holds a generative model of what the level below should be sending up. It sends down its prediction. The level below compares: prediction matches sensory input? Stop. Doesn't match? Send the residual (error) upward. The error updates the higher level's model; the new prediction goes down; iterate.

This explains: why expected stimuli are processed faster than unexpected ones; why attention is *more* on prediction-error-producing inputs; why illusions persist (top-down predictions override bottom-up data).

**The free-energy principle (FEP):**

Free energy F is an upper bound on *surprise*: how unlikely the agent's current observations are under its generative model of the world. F = "what I see now" minus "what I expected." Minimising F means: either change your model (perception/learning) so observations match predictions, or change the world (action) so observations match predictions, or both.

Mathematically, F is:
```
F = E_q[log q(s) - log p(s, o)]
  = D_KL(q(s) || p(s|o)) - log p(o)
```
where `s` is hidden state, `o` is observation, `q` is the agent's recognition density, `p` is the generative model. The first term is "how badly does my inference miss?"; the second is "how surprising is this observation?".

**Active inference:**

Action becomes selection of policies (sequences of actions) that minimise *expected* free energy:
```
G(π) = expected_free_energy_along_policy_π
     = expected ambiguity − expected information gain
```

A policy that minimises G balances: don't get surprised, and reduce uncertainty (learn things). The famous Friston result: this single objective reproduces the major behavioural primitives — exploration, exploitation, homeostasis, goal-directed action.

**Predictive coding in modern deep learning:**

- **Variational autoencoders** (Kingma and Welling, 2013) — implement variational inference, with formal connections to Friston's framework.
- **Deep predictive coding networks** (Lotter, Kreiman, Cox, 2016 — PredNet) — explicit predictive-coding architectures for video prediction.
- **Neural Active Inference** (Tschantz et al., 2020+) — explicit active-inference agents in RL settings.
- **JEPA** (Joint Embedding Predictive Architecture, LeCun et al., 2022) — current LeCun research-program proposal that frames good representation learning as predicting in latent space. Spiritual cousin of predictive coding.
- **World models** ([[25-world-models-rl]]) generally fit the family.

**Caveats:**

- The free-energy principle is widely criticised for being unfalsifiable in its strongest forms — too general to pin down.
- The mathematics is genuinely elegant but the interpretive leaps to "this explains everything" warrant skepticism.
- Useful as *frame*; less useful as *prescription*.

## 3. Key works

- **Rao, R. and Ballard, D. "Predictive coding in the visual cortex: A functional interpretation of some extra-classical receptive-field effects."** *Nature Neuroscience*, 1999. The foundational predictive-coding paper.
- **Friston, K. "The free-energy principle: a unified brain theory?"** *Nature Reviews Neuroscience*, 2010. The accessible introduction.
- **Friston, K. *The Variational Principle of Mind.*** Slowly accumulating book/series — see Friston's lab website.
- **Hohwy, J. *The Predictive Mind.*** Oxford University Press, 2013. Philosophical interpretation.
- **Clark, A. *Surfing Uncertainty.*** Oxford University Press, 2015. Accessible synthesis.
- **Seth, A. *Being You: A New Science of Consciousness.*** Faber, 2021. Mainstream-friendly modern treatment.
- **Tschantz et al. "Reinforcement Learning through Active Inference."** arXiv:2002.12636, 2020.
- **LeCun, Y. "A Path Towards Autonomous Machine Intelligence."** 2022 white paper — JEPA proposal.
- **Lotter, Kreiman, Cox. "Deep Predictive Coding Networks for Video Prediction."** arXiv:1605.08104, 2016.

## 4. Empirical results

For neuroscience:
- Substantial empirical support for predictive-coding-style processing in early visual cortex, auditory cortex, motor planning. Several Nobel-prize-adjacent lines of work.
- The free-energy principle's empirical status is more divided — *some* of its predictions check out, *some* others overpredict / underpredict.

For AI:
- Variational autoencoders work; predictive-coding-style networks for video prediction work; active-inference RL agents work in narrow settings.
- LeCun's JEPA program has produced strong results (DINO, I-JEPA, V-JEPA) — predicting in latent space rather than pixel space is genuinely useful for representation learning.
- Whether explicit active-inference architectures will scale to LLM-class capability is open. The math doesn't obviously bring an advantage at scale; the engineering may be the bottleneck.

## 5. Applicability to Runa

Direct prescriptive applicability is *limited* — Runa is not going to be an active-inference agent in the formal sense. But the *intuitions* are useful in several places:

For **Heimdallr (watch)**:

- Heimdallr's job is anticipation. Modelling his work as "maintain a generative model of Volmarr's expected activity; flag prediction errors" gives a clean framing. When Volmarr starts working on something Heimdallr expected, no signal; when he does something unexpected, that *is* the signal worth attending to.
- Practical: maintain a simple per-project "expected activity" model; spikes in actual-vs-expected become Heimdallr's anomaly signal.

For **Eir (self-repair)**:

- Eir maintains a model of how Runa's subsystems *should* behave. Prediction errors — Muninn returning slower than usual, an adapter authenticating but then silently failing, Skuld accumulating stuck tasks — are the signal Eir reacts to.
- This is roughly what monitoring systems already do; the predictive-coding frame just gives a clean theoretical grounding.

For **Eldhugi (emotional state)**:

- Affect, in some active-inference readings, is the *meta-signal* about whether the agent is succeeding at minimising free energy. High prediction error → high arousal / anxiety; low error in expected state → contentment.
- A Friston-flavoured Eldhugi maintains an internal "how surprised am I lately" measure; emotional state tracks it.

For **kernel-level surprise tracking**:

- Track the model's own *uncertainty* on each turn (via entropy of output distributions, when accessible). Sustained high uncertainty is a signal something is wrong with the agent's understanding of the situation. Triggers more careful reasoning.

For **Muninn**:

- Memory as prediction: a memory that's *useful* (gets retrieved often, predictions match reality) gets reinforced. A memory that produces predictions which are repeatedly wrong gets demoted.

What to avoid:

- Don't try to formally implement the free-energy principle. The math is heavy; the gains over simpler approaches are unclear. Use the framing, not the equations.
- Don't treat surprise as inherently bad. Surprise is information. Eir flagging surprise lets Runa learn; suppressing surprise produces a brittle agent.
- Don't reify the FEP as if it explains everything. The theory is contested; sober use is the rule.

## 6. Open questions

- **Whether the FEP actually scales to AI.** No demonstrated FEP-based agent has approached LLM-scale capability. Either the principle doesn't scale, or the engineering is too immature.
- **The connection between predictive coding and LLMs.** Auto-regressive language modelling is literally next-token prediction — superficially predictive-coding-like. Whether this makes LLMs hidden FEP agents or just a coincidence is debated.
- **Friston-flavoured emotion.** Affect-as-FEP-meta-signal is theoretically attractive; few engineering implementations exist.
- **Active-inference agents at scale.** A serious LLM-scale active-inference agent would be very interesting. Hasn't been built.

## 7. References (curated)

- Friston (2010), *Nature Reviews Neuroscience*.
- Rao and Ballard (1999), *Nature Neuroscience*.
- Clark, *Surfing Uncertainty*, 2015.
- Hohwy, *The Predictive Mind*, 2013.
- Seth, *Being You*, 2021.
- LeCun's 2022 JEPA white paper — openreview.net.
- arXiv:1605.08104 — PredNet.
- arXiv:2002.12636 — RL through active inference.
- Companion docs: [[25-world-models-rl]] (the engineering descendant), [[41-global-workspace-theory]] (complementary framework).

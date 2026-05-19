# 63 — Active Inference and Self-Modelling Agents (Friston applied to AI)

**Category:** Self-Awareness & Metacognition
**Runa relevance:** kernel (predictive action policy), Eldhugi (surprise → affect), Hirð (curiosity-driven exploration), world model
**Status:** Theoretical synthesis with practical extraction. Friston's framework is hard but the export pieces are useable.
**Last touched:** 2026-05-17

---

## 1. Core idea

Karl Friston's *free-energy principle* and the *active inference* framework propose a unifying account of perception, action, learning, and selfhood: a self-organising agent acts to minimise *free energy* — a quantity that, in roughly understandable terms, measures how surprising the world is given the agent's model of it. To minimise free energy, the agent either *updates its model* (perception, learning) or *changes the world* (action) so that the model and the data converge. Crucially, the agent in this framework necessarily maintains a *generative model* of itself in the world; that self-model is constitutive, not optional, for the framework to apply.

For Runa, three exportable ideas are especially valuable: (1) *prediction-error-driven attention* — surprise focuses processing; (2) *epistemic-vs-pragmatic action* — distinguishing curiosity-driven exploration from goal-directed exploitation; (3) *the agent's self-model as an explanatory hypothesis about its own behaviour*. The full machinery (variational free energy, expected free energy, hierarchical generative models) is mathematically heavy; the engineering distillations are tractable.

## 2. Technical depth

**The free-energy principle, in five lines.** A self-organising system $s$ in a world acts to maintain its boundary (a Markov blanket). To do this, it minimises a quantity $F$ — *variational free energy* — defined over its internal states $\mu$ and sensory states $o$:

$$F = -\langle \log p(o, \mu) \rangle_q + \langle \log q(\mu) \rangle_q$$

where $q(\mu)$ is the agent's posterior belief about hidden states given observations. Minimising $F$ implies the agent's beliefs $q$ track the true posterior $p(\mu \mid o)$ as well as possible. There are two ways to reduce $F$: (a) *perception* — update $q$ to better match $o$; (b) *action* — change $o$ (the world) so it matches expected $q$. Both contribute.

**Expected free energy and action selection.** For planning, the agent considers candidate policies $\pi$ and computes *expected free energy* under each: $G(\pi)$. The expected free energy decomposes into two terms:

$$G(\pi) = \underbrace{\text{pragmatic value}}_{\text{goal-attaining}} + \underbrace{\text{epistemic value}}_{\text{information-gain}}$$

Policies that achieve preferred outcomes have high pragmatic value; policies that resolve uncertainty have high epistemic value. The agent's policy distribution prefers low expected free energy — a balance of *getting what it wants* and *learning what it needs*. This is the formal home of *curiosity-driven exploration* in the framework.

**Hierarchical generative models.** The agent's model is structured into layers — high-level slow latent states (\"what is this conversation about\"), mid-level states (\"who is speaking, what is the goal\"), low-level states (\"the next word\"). Each layer predicts the layer below; *prediction errors* propagate upward, updating beliefs. This is structurally identical to *predictive coding* in neuroscience.

**Self-model as Markov blanket.** Friston's framework requires the agent to have a *boundary* — a Markov blanket separating its internal states from its sensory states from action states from the external world. The agent's *self-model* is, in some sense, the agent's model of this boundary: \"these are my internal states; these are what I sense; these are what I do.\" The self-model is therefore not an add-on but a structural necessity for the agent to act at all.

**Operationalisation in AI agents.** Several lines of work translate the theory to deployable systems:

- **Active-inference reinforcement learning** (Sajid, Ball, Friston 2021): RL agents that select actions to minimise expected free energy. Trade-off between exploitation and exploration falls out naturally; the algorithm is roughly competitive with epsilon-greedy and intrinsic-motivation RL.
- **Predictive-coding networks**: networks where every layer computes both a prediction of the layer below and the prediction error to the layer above. Used in vision (Lotter et al. PredNet 2017), some language modelling (Tschannen et al.), and increasingly in interpretability.
- **Curiosity / intrinsic motivation** (Schmidhuber 1991 onward, Pathak et al. 2017): the engineering simplification — agent rewards itself for prediction errors (\"surprising things are valuable to explore\"). Far simpler than active inference; captures part of the epistemic-value spirit.
- **World-model-based agents** (Ha & Schmidhuber 2018, Dreamer; see [[25-world-models-rl]] and [[73-latent-world-models-frontier]]). The agent learns a generative model of the environment; planning becomes imagination in the model. Conceptually adjacent to active inference; Dreamer's expected-free-energy variants exist.
- **LLM agents with explicit prediction.** Less developed: an agent that predicts \"what is likely to happen next in this conversation\" and acts to make outcomes more predictable in line with its preferences. Conceptual; few production examples.

**What's hard.** Full active-inference implementations require explicit generative models, explicit policy distributions, and tractable variational approximations. For high-dimensional state spaces (language, images), the math becomes hairy. Most practitioners use *simplified* curiosity-and-prediction-error variants and call them active-inference-inspired.

**The free-energy intuition for self-awareness.** A free-energy-minimising agent must model *its own action consequences*. To predict the world, it must predict how its own actions will move sensory states. That predictive self-model is structurally a self-model. \"Self-awareness\" in this framing is the agent's predictive grip on its own role in the world.

## 3. Key works

- **Friston, K.** *The free-energy principle: a unified brain theory?* Nature Reviews Neuroscience, 2010. The foundational article.
- **Friston, K., et al.** *Active inference: a process theory.* Neural Computation, 2017.
- **Parr, T., Pezzulo, G., Friston, K.** *Active Inference: The Free Energy Principle in Mind, Brain, and Behavior.* MIT Press, 2022. The book-length synthesis.
- **Sajid, N., Ball, P., Friston, K.** *Active inference: demystified and compared.* Neural Computation, 2021. Practical bridge to RL.
- **Schmidhuber, J.** *A possibility for implementing curiosity and boredom in model-building neural controllers.* SAB 1991. Foundational curiosity.
- **Pathak, D. et al.** *Curiosity-driven exploration by self-supervised prediction.* ICML 2017. The Mario / VizDoom curiosity paper.
- **Lotter, W., Kreiman, G., Cox, D.** *Deep predictive coding networks for video prediction and unsupervised learning.* ICLR 2017.
- **Rao, R., Ballard, D.** *Predictive coding in the visual cortex.* Nature Neuroscience, 1999. The foundational neuroscientific paper.
- **Clark, A.** *Surfing Uncertainty.* OUP, 2016. Accessible philosophical synthesis.
- **Hohwy, J.** *The Predictive Mind.* OUP, 2013.

## 4. Empirical results

- *Active-inference RL agents* (Sajid et al.) match standard RL on benchmark tasks. They do not beat state-of-the-art; they offer principled handling of exploration / exploitation balance.
- *Curiosity-driven exploration* (Pathak et al., subsequent): substantial gains on sparse-reward environments. Mario, Atari, Minecraft. The intuition transfers; the math is simpler.
- *PredNet* and predictive-coding networks: competitive on video prediction; rich internal representations that probe well.
- *Predictive-coding interpretation of LLMs*: some evidence that transformers compute prediction errors implicitly (Bills et al. on neuron-level prediction; Anthropic's induction heads). Not a settled framework but suggestive.
- *Cognitive science evidence*: predictive coding is a leading framework in modern cognitive neuroscience, with substantial experimental support (Bayesian perception in humans, attentional gating by prediction errors).

Honest take: the *full* free-energy framework has produced *fewer* engineering successes than its theoretical scope suggests. The *partial* ideas (curiosity, prediction error, hierarchical prediction) are heavily used. Treat the framework as inspirational and the partial ideas as production-ready.

## 5. Applicability to Runa

For **kernel — surprise-driven attention**:

- The kernel can compute a cheap *surprise signal*: how unexpected was the user's input given the conversation so far? When surprise is high, allocate more reasoning (longer chain-of-thought, deeper retrieval, multi-sample self-consistency). This is *predictive coding for compute allocation*.
- Implementation: a simple LLM-judged \"on a scale of 1–10, how surprising / off-pattern is this turn?\" Or a learned embedding-based surprise score against a window of recent conversation embeddings.

For **Eldhugi — surprise as affect**:

- Surprise is an affective state (\"oh — really?\"). Track it. Connect surprise to curiosity (positive valence) when low-stakes, alarm (negative valence) when high-stakes.
- Eldhugi's tracking of epistemic affect ([[59-metacognitive-monitoring]]) integrates here: surprise + uncertainty + outcome → emotional valence about what is happening.

For **Hirð — curiosity-driven exploration**:

- Hirð can include a *curious explorer* retainer whose job is to identify *information gaps* — questions Runa has not resolved, references she hasn't followed up, claims she made and never re-examined. The retainer surfaces opportunities to learn during idle time.
- This is epistemic-value-maximisation made into a subagent. \"What would Runa not yet know that she might benefit from finding out?\"

For **world model**:

- Active inference frames the world model as *generative* — it predicts, it doesn't just describe. Runa's emerging world-model (via WYRD or otherwise; see [[73-latent-world-models-frontier]]) benefits from being framed predictively: \"given the current state, what will likely happen next; what would I predict the user wants; what is my predicted response to that?\"

For **self-model as predictor of own action**:

- Runa's self-model includes a *predictor of her own next action* — what she'd likely do or say. The prediction is then compared to her actual action; mismatches are interesting. Mismatches between predicted-self and actual-self are exactly the substrate of self-knowledge.
- Smiðja can run this: at end of turn, ask \"what would past-Runa have predicted she'd say here?\" Compare. Log deltas. Over time the deltas tell a story about Runa's evolution.

What to avoid:

- **Implementing full active inference from scratch.** It's a research project. Use *inspired* mechanisms — surprise, prediction error, curiosity — not the full machinery.
- **Treating prediction error as Reward.** It's an attentional and exploratory signal; not a value function. Don't optimise it directly without scaffolding.
- **Free-energy as ideology.** The framework is one lens. It illuminates some things and is silent on others (e.g. social cognition, see [[67-theory-of-mind-llms]] for that).
- **Confusing surprise with novelty.** A surprising turn might just be Volmarr being playful; not all surprise is information-bearing. Calibrate.

## 6. Open questions

- **Active inference for LLMs.** Can LLM agents be trained or prompted in a way that natively implements expected-free-energy-style action selection? Promising; not deployed.
- **Predictive coding at LLM scale.** Whether the prediction-error framing yields *new* interpretability or capability is open; current findings are suggestive.
- **Self-model as predictor.** The cleanest test: does an agent that explicitly predicts its own behaviour, then compares to outcome, behave more coherently? Empirically untested at scale.
- **Curiosity-budget balance.** How much of Runa's processing should be \"explore unresolved questions\"? Tunable; defaults uncertain.
- **Surprise-to-affect mapping.** Cognitive science is unsettled here; engineering it for Eldhugi is creative work.

## 7. References (curated)

- Parr, Pezzulo, Friston (2022) — *Active Inference* (MIT Press). The book if you want depth.
- Clark (2016) — *Surfing Uncertainty.* Best philosophical/accessible read.
- arXiv:1705.05363 — Pathak et al., *Curiosity-driven exploration.*
- arXiv:1812.05121 — Ha & Schmidhuber, *World Models.* Adjacent and more deployable.
- Friston (2010) — *Nature Reviews Neuroscience.* The foundational article.
- Companion docs: [[25-world-models-rl]], [[42-predictive-coding-free-energy]], [[59-metacognitive-monitoring]], [[60-self-models-in-artificial-agents]], [[73-latent-world-models-frontier]].

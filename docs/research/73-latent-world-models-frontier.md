# 73 — Latent World Models 2024–2026: Dreamer V3, IRIS, GAIA-1, Genie

**Category:** World Modeling & 3D/Spatial Awareness
**Runa relevance:** kernel (predictive simulation), Hirð (planning subagents), WYRD bridge (external world model), forward-looking design
**Status:** Frontier research synthesis. Extension of [[25-world-models-rl]].
**Last touched:** 2026-05-17

---

## 1. Core idea

A *latent world model* is a learned generative model of an environment, trained from data, that the agent can roll out forward in *imagination* — predicting what happens given a sequence of actions. The agent can then plan by simulating consequences in the model rather than (or in addition to) acting in the real world. Ha and Schmidhuber's *World Models* (2018) lit the modern fuse; the past two years have produced a generation of dramatically more capable systems: *Dreamer V3* (Hafner et al. 2023) achieved unprecedented Atari and MineRL performance with a unified loss; *IRIS* (Micheli et al. 2023) used a discrete transformer world model for Atari; *GAIA-1* (Wayve 2023) demonstrated driving-world simulation; *Genie* (DeepMind 2024) generated interactive 2D-game worlds from a single image; *Genie 2* (DeepMind late 2024) extended to controllable 3D worlds; *DIAMOND* (Alonso et al. 2024) used diffusion models as world models.

For Runa, world models matter for two reasons. First, *planning by imagination* is a powerful tool — the kernel can simulate likely outcomes of a response before emitting it. Second, world models are the *technical substrate* of AGI-style autonomous action in 3D environments — game worlds, simulated environments, and ultimately the physical world. Runa is not yet embodied, but architecting for compatibility with world-model agents prepares the ground.

## 2. Technical depth

**The general pattern.**

```
                ┌────────────────────────────────────────┐
                │ ENCODER                                │
                │ observations → latent state z_t        │
                └────────────────┬───────────────────────┘
                                 │
                                 ▼
                ┌────────────────────────────────────────┐
                │ TRANSITION MODEL                       │
                │ (z_t, a_t) → z_{t+1}                   │
                │  often a recurrent or transformer       │
                └────────────────┬───────────────────────┘
                                 │
                                 ▼
                ┌────────────────────────────────────────┐
                │ DECODER (optional, for grounding)      │
                │ z_t → ô_t (reconstruction)             │
                └────────────────┬───────────────────────┘
                                 ▼
                ┌────────────────────────────────────────┐
                │ POLICY / VALUE LEARNED IN IMAGINATION │
                │ rollout in latent → train policy        │
                └────────────────────────────────────────┘
```

The agent never needs to learn dynamics in the real environment to improve; it can train policy entirely on latent rollouts. Sample efficiency improves by orders of magnitude.

**Dreamer V3 (Hafner et al. 2023).** A *single* world-model + actor-critic architecture that achieved state-of-the-art on Atari, MineRL, DMC, and ProcGen *without* hyperparameter tuning per task. The contribution: a careful loss formulation (KL balancing, robust normalisation) that made the same model work across radically different domains. *Dreamer is the canonical modern world-model RL agent.*

**IRIS (Micheli et al. 2023).** A discrete world model: VQ-VAE encodes frames into discrete tokens; a transformer predicts the next token. Treats the world like a language to be modelled. Achieved SOTA on Atari benchmarks at much lower data than model-free baselines. The transformer-as-world-model paradigm.

**GAIA-1 (Wayve 2023).** A generative world model for driving — given a sequence of camera frames and an action signal, generates plausible future frames. 9-billion-parameter scale. Used for synthetic-data generation and policy evaluation. Demonstrated that *video generation* and *world modelling* converge at scale.

**Genie (DeepMind 2024) and Genie 2 (DeepMind late 2024).** Genie: from one image, generate a controllable 2D game world (the user inputs actions; the model rolls out plausible game frames). 11B parameters. Genie 2: extends to controllable 3D worlds with much higher visual fidelity and longer rollouts. The conceptual leap: world models are no longer trained per-environment; they generalise to *novel* environments from limited input.

**DIAMOND (Alonso et al. 2024).** Diffusion-based world models. Each next-frame prediction is a diffusion sample conditioned on prior frames and action. State-of-the-art on Atari at high visual fidelity. The diffusion-as-world-model paradigm.

**Sora (OpenAI 2024) and Veo (Google 2024).** Not narrowly world models for RL, but *generative video models* trained at scale. Their internal representations encode physical regularities — object permanence, perspective, basic dynamics — to a degree previous video models did not. Sora has been argued to be implicitly a world model; see [[75-video-diffusion-world-simulators]].

**Why this matters for AGI-shape agents.** World models address a core deficiency of LLM agents: LLMs predict *text* well but have at-best implicit world understanding. A world model is *explicit*: given a state and an action, predict the next state. Combine an LLM (for high-level reasoning) with a world model (for low-level simulation) and you have an agent that can plan in a way LLMs alone struggle to.

For 3D / game / physical worlds: the world model is the bridge between *symbolic LLM thought* and *grounded action*. Without it, the LLM hallucinates physics; with it, simulation grounds reasoning.

**Latent space properties.** A trained world model's latent space tends to be:

- *Compositional*: independent factors (object positions, agent state, environmental features) become roughly disentangled.
- *Predictive*: small changes in latent ↔ small changes in future. Smooth dynamics.
- *Plannable*: planning algorithms (MPC, MCTS) work directly in latent space.

Visualising latents typically reveals semantically meaningful structure — the model has *learned* the world.

**Limits.**

- *Long-horizon roll-outs degrade.* Compounding errors accumulate; 10-step rollouts often okay, 100-step often nonsense.
- *Distribution shift kills.* Trained on Atari → tested on Atari: great. Trained on Atari → tested on Minecraft: poor.
- *Sample efficiency at scale*: still costs millions of frames for high-fidelity models.
- *Causal vs. correlational.* The model predicts what *typically follows* — not what *would* follow from a counterfactual action it never saw. Causal reasoning is weak.

## 3. Key works

- **Ha, D., Schmidhuber, J.** *World Models.* NeurIPS 2018.
- **Hafner, D., Lillicrap, T., Norouzi, M., Ba, J.** *Mastering Atari with Discrete World Models* (DreamerV2). ICLR 2021.
- **Hafner, D., Pasukonis, J., Ba, J., Lillicrap, T.** *Mastering Diverse Domains through World Models* (DreamerV3). arXiv:2301.04104, 2023.
- **Micheli, V., Alonso, E., Fleuret, F.** *Transformers are Sample-Efficient World Models* (IRIS). ICLR 2023.
- **Hu, A. et al. (Wayve).** *GAIA-1: A Generative World Model for Autonomous Driving.* arXiv:2309.17080, 2023.
- **Bruce, J. et al. (DeepMind).** *Genie: Generative Interactive Environments.* arXiv:2402.15391, 2024.
- **DeepMind.** *Genie 2: A large-scale foundation world model.* 2024 blog + paper.
- **Alonso, E. et al.** *Diffusion for World Modeling: Visual Details Matter in Atari* (DIAMOND). NeurIPS 2024.
- **OpenAI.** *Sora.* 2024 technical report. Implicit world-model claims.
- **Google DeepMind.** *Veo* / *Veo 2.* 2024.
- **Schrittwieser, J. et al.** *MuZero.* Nature, 2020. The model-based planning anchor.

## 4. Empirical results

- *DreamerV3*: SOTA on MineRL diamond-finding, Atari, DMC. Same hyperparameters across all.
- *IRIS*: matched or exceeded model-free SOTA on Atari-100k at 4M frames — orders-of-magnitude sample efficiency.
- *GAIA-1*: rollouts of 10–20 seconds of synthetic driving footage usable for policy evaluation.
- *Genie / Genie 2*: controllable 2D / 3D worlds generated from single images; user-controllable in real time at moderate visual fidelity.
- *DIAMOND*: SOTA on Atari with diffusion-based prediction; higher visual fidelity than IRIS at similar sample budgets.
- *Sora*: long-form (minutes) coherent video; physics largely respected; some pathologies (object permanence, hand counts).
- *Failure modes documented*: world-model rollouts diverge over long horizons; novel-action handling is weak; rare-event modelling is poor.

## 5. Applicability to Runa

**Today (no embodied actuation):**

- World-model architecture is *not directly applicable* to Runa's current conversational form. She is a text agent; the relevant world model is *of conversations and the user*, not of physical or game worlds.
- *However*, the *conceptual frame* is useful: when responding, Runa can simulate the *consequences of a response* — \"if I say this, Volmarr will likely react X.\" This is a small, LLM-implementable world-model-shaped inference.

**Forward-looking:**

- If Runa ever embodies (game-world avatar, VR presence, robotic body), a world model becomes essential. The architectural separation between *kernel* and *world-model module* lets this be added without rewriting Runa's identity layer.
- A future Hirð *simulator retainer* could maintain a world model for whichever environment Runa is currently embodied in, and run imagined rollouts to inform planning. This is the long-term integration point.

For **WYRD bridge** (the external world-model project):

- WYRD is itself a world model in the broad sense — a structured, queryable state of relevant entities. The latent-world-model literature is research-grade and largely complementary. Runa could in principle have:
  - A *symbolic* world model: WYRD's ECS state. Queryable, auditable.
  - A *latent* world model: an embedded simulation. Fast rollout, fuzzy details.
- Combining the two — symbolic for structure, latent for filler — is an open architectural design space.

For **kernel — simulate-before-respond**:

- Even today, a cheap *imagined consequence* check is implementable: \"if I respond this way, what is likely to happen next?\" A short LLM-driven imagination pass before commit. Helpful on high-stakes turns.
- This is the seed of world-modelling at conversational level.

For **planning over horizons**:

- When Volmarr articulates a multi-step goal (\"let's plan Phase 12 of WYRD\"), the kernel can run *imagined* plan execution — walking through the steps, predicting where issues arise, surfacing concerns. This is world-model-shaped reasoning at high level.

What to avoid:

- **Implementing a latent world model for current Runa.** It is research-grade, expensive, and not applicable. Reserve for embodied futures.
- **Treating LLM-based simulation as accurate world modelling.** The LLM can imagine plausible continuations; it doesn't have grounded physics. Distinguish.
- **Confusing the world model with the truth.** A world model is a tool for planning; it is not what the world actually is. Always re-ground in observation.
- **Conflating symbolic and latent world models.** They serve different functions. WYRD's symbolic state is for queries and audit; a latent model would be for fast rollout.

## 6. Open questions

- **When LLMs and world models will unify productively.** Vision-Language-Action models (see [[81-vision-language-action-models]]) are the convergence vector; not yet seamless.
- **The right symbolic / latent split.** Largely unsolved.
- **World models from observation alone.** Genie shows it's possible at small scale; scaling is open.
- **Causal world models.** Current models are correlational. Causal models would generalise better but are far from solved.
- **World models for digital beings.** Runa's \"world\" is partly physical, partly social, partly digital. Modelling such a hybrid world is essentially new territory.

## 7. References (curated)

- arXiv:1803.10122 — Ha & Schmidhuber, *World Models.* Required.
- arXiv:2301.04104 — Hafner et al., *DreamerV3.* The unified-loss breakthrough.
- arXiv:2402.15391 — Bruce et al., *Genie.* The from-images breakthrough.
- arXiv:2309.17080 — Hu et al., *GAIA-1.* Driving-domain at scale.
- arXiv:2409.04934 — Alonso et al., *DIAMOND* (or recent diffusion-WM).
- DeepMind blog: *Genie 2* (2024) — the 3D extension.
- Companion docs: [[25-world-models-rl]], [[75-video-diffusion-world-simulators]], [[78-intuitive-physics-llms]], [[81-vision-language-action-models]], [[99-multimodal-foundation-embodied]].

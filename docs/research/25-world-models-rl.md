# 25 — World Models in RL: Dreamer, MuZero, IRIS

**Category:** World Modeling
**Runa relevance:** WYRD bridge (architectural reference), Hirð (planning subagents), Eldhugi (predictive-context idea)
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

In reinforcement learning, a **world model** is a learned predictive model of the environment: given the current state and an action, predict the next state, the reward, and any other observable consequences. With a sufficient world model, an agent can *plan in imagination* — simulate trajectories of "what would happen if I did X then Y then Z?" — and act on the simulation results without paying the real cost of acting. The world-model paradigm produced some of the strongest RL results of the last decade: Dreamer mastering Atari and dexterous manipulation from pixels, MuZero playing Go/chess/shogi/Atari without being told the rules, IRIS doing Atari from a learned transformer-based world model.

For Runa, "world model" has a different meaning than Hirð's WYRD bridge — Runa's WYRD is an *externally-maintained* structured store, not a learned predictive model. But the *idea* of an agent maintaining a predictive simulation it can plan over has real applicability: Hirð's planning subagents could maintain learned predictions of Volmarr's preferences and the state of his ecosystem; Eldhugi could maintain a model of Runa's own emotional trajectory; an Eir reflection pass could rehearse repair actions in simulation before attempting them.

This doc covers the RL world-model lineage as background and as inspiration, not as a prescription.

## 2. Technical depth

**The world-model loop in classical model-based RL:**

```
[1] Collect real experience: (s, a, r, s') tuples by acting in the
    real environment.
[2] Learn a world model: f(s, a) → (predicted_s', predicted_r).
[3] In imagination: roll out hypothetical trajectories using the world
    model. No real-world cost.
[4] Train a policy on the imagined trajectories.
[5] Deploy the policy in the real environment.
[6] Iterate.
```

The 10x efficiency gain over model-free RL: most of the policy's training happens in cheap imagination, not in expensive real-world trials.

**Dreamer family** (Hafner et al., DeepMind / Google):

- **Dreamer v1** (Hafner, Lillicrap, Ba, Norouzi, arXiv:1912.01603, 2019). Uses a learned Recurrent State-Space Model (RSSM) — observations are encoded into a latent state, transitions in latent space are learned, predictions decoded back to observations and rewards. Trains policies entirely in the latent imagination.
- **Dreamer v2** (Hafner et al., 2020). Discrete latent variables (categorical instead of Gaussian) — surprisingly important. Mastered all 55 Atari games at human-level performance.
- **Dreamer v3** (Hafner et al., 2023). Same algorithm across 150+ domains without hyperparameter tuning. Notably mastered Minecraft from scratch — getting a diamond — without manually-engineered curricula. Demonstrated the generality of the architecture.

**MuZero** (Schrittwieser, Antonoglou, Hubert, Simonyan, Sifre, Schmitt, Guez, Lockhart, Hassabis, Graepel, Lillicrap, Silver, DeepMind, *Nature* 2020). Combines learned world model with Monte Carlo Tree Search (MCTS):

- Learns a *latent dynamics model* — doesn't try to predict raw pixels, only the quantities relevant to planning (reward, value, next-latent-state, policy prior).
- At decision time, runs MCTS using the learned model to evaluate moves.
- Mastered Go, chess, shogi from self-play *without being told the rules of the games*. Earlier AlphaZero needed the rules; MuZero learned them implicitly.
- Also Atari at human-level performance.

**IRIS** (Micheli, Alonso, Fleuret, "Transformers are Sample-Efficient World Models", ICLR 2023, arXiv:2209.00588). Replaces the RNN-based world model with a discrete autoencoder + GPT-style transformer for dynamics. Demonstrated strong sample efficiency on Atari 100K benchmark.

**TWM, IRIS, TransDreamer** — a cluster of 2022-2023 papers showing transformers do well as world-model architectures.

**Diffusion world models** (e.g. DIAMOND, Alonso et al., 2024) — use diffusion for high-fidelity prediction of future observations. Strong for visually-rich environments.

**Schmidhuber's "Curious Model-Building Control Systems" (1991)** and the **World Models paper** (Ha and Schmidhuber, "World Models," 2018) are the historical ancestors — earlier articulations of "learn a generative model of the environment, then plan in it."

## 3. Key works

- **Ha, D.; Schmidhuber, J.** "World Models." arXiv:1803.10122, 2018. The modern restatement that launched the term.
- **Hafner et al. "Dream to Control: Learning Behaviors by Latent Imagination."** arXiv:1912.01603, 2019. Dreamer v1.
- **Hafner et al. "Mastering Atari with Discrete World Models."** arXiv:2010.02193, 2020. Dreamer v2.
- **Hafner et al. "Mastering Diverse Domains through World Models."** arXiv:2301.04104, 2023. Dreamer v3.
- **Schrittwieser et al. "Mastering Atari, Go, Chess and Shogi by Planning with a Learned Model."** *Nature*, 2020. MuZero.
- **Micheli, Alonso, Fleuret. "Transformers are Sample-Efficient World Models."** arXiv:2209.00588, 2023. IRIS.
- **Alonso et al. "Diffusion for World Modeling."** 2024. DIAMOND.
- **Sutton, R. "Integrated Architectures for Learning, Planning, and Reacting Based on Approximating Dynamic Programming."** ICML 1990. The Dyna architecture — historical foundation.
- **Sutton and Barto, *Reinforcement Learning: An Introduction*, 2nd ed.** MIT Press, 2018. The textbook.

## 4. Empirical results

- **Dreamer v3** matched or exceeded specialised algorithms on 150+ domains *with the same hyperparameters* — strong evidence the world-model approach generalises.
- **MuZero** matched or exceeded AlphaZero on Go/chess/shogi without rule knowledge; matched specialised Atari agents.
- **IRIS** achieved state-of-the-art sample efficiency on Atari 100K (humans-equivalent gameplay from 100K interaction steps).
- **Sample efficiency** is the consistent win: world-model methods learn from far less real-world experience than model-free methods.
- **Failure modes:**
  - Model errors compound over long rollouts. Planning beyond ~50 steps becomes unreliable.
  - Models trained on one environment don't transfer cleanly to even slightly different ones.
  - Compute cost of imagined rollouts can dominate.

## 5. Applicability to Runa

Direct applicability to Runa is *modest* — Runa is not a classical RL agent and does not need to learn from scratch. The inspiration is the *pattern* of maintaining an internal predictive simulation.

For **Hirð / Heimdallr (watch + planning)**:

- A learned model of Volmarr's daily patterns, his project ecosystem, his preference shifts could inform Heimdallr's anticipation. "Volmarr usually starts WYRD work after lunch on weekdays; queueing related context now is likely useful." Not a heavy ML model; even a simple statistical pattern model is the start.

For **Eldhugi (emotional state)**:

- A model that predicts how Runa's own emotional state will evolve under various courses of action (replying X vs Y, doing Z vs deferring) could let her *plan emotional trajectories* the way Dreamer plans physical trajectories. Speculative; interesting.

For **Eir (self-repair planning)**:

- Before attempting a repair (vacuuming Muninn, restarting an adapter, restoring from snapshot), Eir could simulate the action in a "shadow" environment to predict consequences. Reduces risk of compounding failures.

For **WYRD bridge**:

- WYRD is an external structured world model, not a learned one. The architectural lesson from MuZero / Dreamer is *latent representation* — even an external store benefits from having a compressed, query-friendly representation rather than raw "all current entities and relations."

For **Hirð / Völundr (codegen)**:

- A world model for code (predicting outputs from code execution) is what tools like Replit's Ghostwriter agent and SWE-bench-style coding agents implicitly do. Less "world model" in the formal sense; more "execution simulator." Worth thinking about for Völundr's verifier.

What to avoid:

- Don't try to learn a Dreamer-style world model for Runa as a project. Wrong scale, wrong domain.
- Don't build a complex planning system before there's a clear task it serves. World-model planning is heavy machinery; agents that don't need it shouldn't have it.

## 6. Open questions

- **World models for language agents.** Can the world-model paradigm be adapted for agents whose "environment" is text, conversation, tool outputs? Some work exists (LLM-as-world-model) but is early.
- **Bridging learned and structured world models.** WYRD (structured) and Dreamer-style (learned latent) are extremes. Hybrid architectures that combine deterministic ontology with learned predictions are an active research frontier.
- **World models + LLMs.** Using an LLM as the world model (it "knows" how things work) is appealing but suffers from LLM unreliability. Whether/when this is viable is open.
- **Long-horizon planning.** World-model errors compound; planning beyond a few dozen steps remains hard.

## 7. References (curated)

- arXiv:1803.10122 — Ha and Schmidhuber, World Models.
- arXiv:2301.04104 — Dreamer v3.
- *Nature* 2020 — MuZero.
- arXiv:2209.00588 — IRIS.
- Sutton and Barto, *Reinforcement Learning: An Introduction*, 2nd ed., 2018.
- danijar.com — Danijar Hafner's site, Dreamer family explanations.
- deepmind.com/research — DeepMind's RL research index.
- Companion docs: [[26-entity-component-system]] (the WYRD-style alternative), [[27-belief-states-pomdp]] (handling uncertainty).

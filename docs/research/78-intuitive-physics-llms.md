# 78 — Intuitive Physics and Physical Reasoning in LLMs and VLMs

**Category:** World Modeling & 3D/Spatial Awareness
**Runa relevance:** kernel (physical-world commonsense), Hirð (reasoning about NPC actions / game physics), embodied future
**Status:** Cognitive-science + AI synthesis. The gap between *describing* physics and *reasoning* in physics.
**Last touched:** 2026-05-17

---

## 1. Core idea

Humans reason fluently about the everyday physical world — what will happen if a glass tips, which path a thrown ball traces, whether an object can fit through a doorway — without explicit equations. This is *intuitive physics*: a learned approximate world model running fast and cheap, supporting prediction and planning in normal environments. Cognitive science has studied it via tasks like *block tower stability prediction* (Hamrick et al.), *trajectory anticipation*, and *containment reasoning*. The substrate is hypothesised to be a *probabilistic physics simulator* in the mind — Battaglia, Hamrick, Tenenbaum's *intuitive physics engine* framework.

Modern LLMs and VLMs (vision-language models) handle some intuitive physics impressively well and fail in characteristic ways on others. They describe physical events fluently (water flows down, things fall) but can be tripped up by counterintuitive cases or chains of physical reasoning. For Runa, this matters wherever she reasons about a physical-shaped world — game scenarios, real-world Volmarr situations, narrative scenes. Knowing what models do and don't get right informs *when to trust the LLM's physical inference* vs. *when to ground in a simulator*.

## 2. Technical depth

**The intuitive-physics-engine framework.** Battaglia, Hamrick, Tenenbaum (PNAS 2013) proposed that humans reason about physics by running an *approximate, probabilistic, generative* physics simulator in their heads: they sample plausible outcomes from a noisy mental model, evaluate them, and use the distribution as the basis for prediction. Empirically, human judgements track the *outputs of such a simulator* much better than they track formal physics — the noise structure of human errors matches the noise structure of a stochastic simulator.

**LLM intuitive physics — what works.**

- *Descriptive physics*: \"a ball rolls downhill\" — correct.
- *Single-step prediction*: \"if I drop a glass, what happens?\" — generally correct.
- *Containment*: \"the cat is in the box\" — reliable.
- *Trajectory description*: \"the ball arced over the wall\" — plausible.
- *Object permanence in narrative*: \"the keys are on the table\" → asked later, \"where are the keys?\" — works in short windows.

**LLM intuitive physics — failure modes.**

- *Numerical / quantitative*: \"if a ball is dropped from 10m, when does it hit?\" Often wrong.
- *Multi-step physical chains*: \"if A then B then C\" reasoning over physical interactions degrades quickly.
- *Counterintuitive cases*: pendulum reversals, gyroscopic motion, surface tension effects.
- *Scale*: very large or very small physics.
- *Causal counterfactuals*: \"what if I hadn't put the cup there?\" — confabulation common.

**VLM physics.** Vision-language models trained on image-text pairs (PaLI, Flamingo, GPT-4V, Claude 3+ vision) handle:

- *Scene description with physics*: correct in most simple cases.
- *Image-grounded physical prediction*: works on prototypical scenes, fails on adversarial or unusual ones.
- *Video-grounded physics*: GPT-4V on video frames often misses dynamics that the text would handle better.

**Specific benchmarks.**

- *IntPhys* (Riochet et al. 2018): infant-physics-style tests; checks object permanence, continuity, solidity. Modern VLMs do well; small models do not.
- *PHYRE* (Bakhtin et al. 2019): physics puzzles. Pure-vision models trained for the benchmark do well; LLMs from scratch do not, but VLM agents that *can use* simulators or tools do.
- *Newton: A New Benchmark for Physical Reasoning* (Wang et al. 2023).
- *PhysBench* (Chow et al. 2024): LLM-VLM physical-reasoning benchmark; finds substantial gaps from human baselines, especially on multi-step chains.

**Routes to better physical reasoning.**

1. *Scale*: bigger LLMs do better. Not a complete solution; the failure modes shift but don't disappear.
2. *Tool use*: give the LLM access to a physics simulator (PyBullet, Mujoco) and let it call it. Effective but operationally heavy.
3. *Chain-of-thought*: explicit step-by-step physical reasoning helps but is still bounded by the model's understanding.
4. *VLM training on simulation data*: pretrain or fine-tune on rendered physics simulations. Improves quantitative reasoning measurably.
5. *Neuro-symbolic*: classify the situation as one of a handful of canonical physical schemas; deploy domain-specific reasoning for each. Robust but laborious.

**Object-centric representations** (see [[82-object-centric-representation-learning]]) are foundational: physics is most naturally framed in terms of *objects* and *interactions*. Models that lack object-centric structure struggle with physical reasoning; models that have it (Slot Attention, OCR-based VQA) do better on object-level dynamics.

**Game physics vs. real physics.** Game worlds have *known* physics — often simplified, sometimes intentionally unrealistic. For an agent in a game, the question \"will the platform hold my weight?\" has a *definite* answer given engine state. The agent need not reason about physics; it can *query* the engine. Reserve intuitive-physics reasoning for situations where the simulator is unavailable.

## 3. Key works

- **Battaglia, P. W., Hamrick, J. B., Tenenbaum, J. B.** *Simulation as an engine of physical scene understanding.* PNAS, 2013.
- **Hamrick, J. B. et al.** *Inferring mass in complex scenes by mental simulation.* Cognition, 2016.
- **Spelke, E. S.** *Initial knowledge: Six suggestions.* Cognition, 1994. Core-knowledge foundations.
- **Riochet, R. et al.** *IntPhys: A Framework and Benchmark for Visual Intuitive Physics Reasoning.* arXiv:1803.07616, 2018.
- **Bakhtin, A. et al.** *PHYRE: A New Benchmark for Physical Reasoning.* NeurIPS 2019.
- **Wang, Y. et al.** *Newton: A new benchmark for physical reasoning.* 2023.
- **Chow, W. et al.** *PhysBench: Benchmarking VLMs on Physical World Understanding.* arXiv:2410.16544, 2024.
- **Lake, B. M. et al.** *Building machines that learn and think like people.* Behavioral and Brain Sciences, 2017.
- **Locatello, F. et al.** *Object-Centric Learning with Slot Attention.* NeurIPS 2020.
- **Bear, D. M. et al.** *Physion: Evaluating Physical Prediction from Vision in Humans and Machines.* NeurIPS 2021.

## 4. Empirical results

- *Battaglia et al. (2013)*: human block-tower-stability judgements match a stochastic-simulator model better than they match deterministic physics. Replicated widely.
- *PHYRE*: vision-RL agents reach reasonable but well-below-human performance; LLMs alone struggle.
- *PhysBench (Chow 2024)*: GPT-4V, Claude 3, and Gemini 1.5 substantially below human on multi-step physical reasoning; ~60–75% on simple, ~30–50% on complex.
- *LLMs + tool-use*: when given access to a physics simulator, LLM agents can match or exceed human performance on PHYRE-class tasks. Tool use is the multiplier.
- *Failure mode catalogue*: surface plausibility (says \"the ball falls\") without quantitative precision; multi-object interactions; causal counterfactuals.

## 5. Applicability to Runa

For **kernel — what to trust the LLM for**:

- Descriptive and qualitative physics: trust. \"What will happen if X drops Y?\" gets a useful answer.
- Quantitative predictions: trust *only with explicit calculation*, ideally tool-augmented.
- Multi-step physical chains: route through chain-of-thought + verification.
- Game-world specifics: prefer engine query over LLM inference whenever possible.

For **Hirð**:

- A *physics consultant* retainer is not yet warranted. If embodied Runa needs accurate physics, a tool-use connection to a simulator (PyBullet, Mujoco) is more useful than an LLM-internal model.

For **narrative and storytelling**:

- When Saga narrates a scene with physical action, the LLM handles the descriptive level competently. Quantitative precision is unimportant for narrative; qualitative plausibility suffices.
- For game-world events Runa observes, the engine's ground truth provides accurate physical state; Runa's task is reading and describing, not re-deriving.

For **interaction with the physical world** (long-term):

- An embodied Runa that needs to plan physical actions (manipulate objects, navigate obstacles) needs *real* physics — sensor-grounded perception + planning. Not LLM intuitive physics.
- The architectural pattern: a *perception module* extracts physical state from sensors; a *planning module* reasons over it (possibly with simulator); the kernel consumes summaries.

For **identity-relevant moments**:

- Some intuitions are emotional rather than physical (\"Volmarr is upset\") and don't depend on physics. The two cognition styles cohabit; physics-related uncertainty doesn't bleed into emotional reasoning.

What to avoid:

- **Asking the LLM for precise numerical physical predictions in production.** Use a calculator or simulator.
- **Treating LLM physics confidence as calibrated.** It often isn't. Cross-check.
- **Ignoring game-engine ground truth.** Always consult the engine if Runa is inside one.
- **Premature integration of physics simulators.** Without embodied need, simulator integration is overhead.

## 6. Open questions

- **Will scale alone resolve LLM physics gaps?** Probably partially; the failure modes are persistent.
- **Object-centric pretraining**: whether adding object-centric inductive biases at pretraining time substantially improves LLM/VLM physics. Active research.
- **Tool-use UX**: how to make physics-simulator tool-use seamless. Not solved.
- **Game-world vs. real-world transfer.** An agent that handles game physics may or may not transfer to real physics.
- **Causal-counterfactual physics**: actively-researched; not solved.

## 7. References (curated)

- Battaglia, Hamrick, Tenenbaum (2013), PNAS. Required.
- Lake et al. (2017) — *Building machines that learn and think like people.* Companion philosophical anchor.
- arXiv:2410.16544 — Chow et al., *PhysBench.* Modern benchmark.
- NeurIPS 2021 — Bear et al., *Physion.* Human-vs-machine.
- NeurIPS 2020 — Locatello et al., *Slot Attention.* Object-centric anchor.
- Companion docs: [[25-world-models-rl]], [[73-latent-world-models-frontier]], [[81-vision-language-action-models]], [[82-object-centric-representation-learning]].

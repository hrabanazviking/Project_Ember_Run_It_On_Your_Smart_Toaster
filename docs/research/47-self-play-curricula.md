# 47 — Self-Play and Learned Curricula

**Category:** Self-Improvement & Continual Learning
**Runa relevance:** future LoRA fine-tuning, Hirð retainer training, automatic skill acquisition (Voyager-style)
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

Self-play is the family of techniques where an agent improves by playing against (or generating training data for) *itself*. AlphaGo Zero (Silver et al., DeepMind, 2017) was the headline result: a Go agent that started from random play, played itself millions of games, and reached super-human performance *without learning from human games*. The trick was that the agent's opponent was always at exactly its skill level — the curriculum was *automatic*, scaled with its growing ability.

Self-play has been less central in LLM-land than in RL, but the principles have started transferring. **SPIN** (Self-Play Fine-Tuning, Chen et al., 2024), **RLAIF** ([[14-constitutional-ai]]), and various "self-improvement" research lines extend the idea. The bigger umbrella — **automatic curricula** where an agent's experiences are progressively tuned to its current skill — applies broadly, including to Voyager-style lifelong agents ([[12-voyager-lifelong-learning]]).

For Runa, the relevance is forward-looking: as Runa accumulates self-conversation data and self-reflection data, self-play-style fine-tuning becomes feasible. The patterns are less mature than other techniques in the corpus; this is one of the more speculative entries.

## 2. Technical depth

**The self-play cycle (classical RL):**

```
[1] Current model M plays games against M.
[2] Game outcomes provide reward signal.
[3] M updates: better moves become more likely.
[4] M improves; opponent (also M) improves; difficulty stays at the agent's edge.
[5] Iterate.
```

The key property: the curriculum is *automatic*. No external teacher decides what level of opponent to face — the agent always faces itself.

**AlphaGo Zero variant** (Silver et al., 2017):

- Combined self-play with Monte Carlo Tree Search ([[25-world-models-rl]]'s MuZero is descendant).
- Used a single neural network for both policy (which move?) and value (who wins?) prediction.
- Achieved super-human Go play from scratch in 40 days.

**LLM self-play:**

Less straightforward because there's no clean "win/lose" signal in conversation.

- **SPIN (Self-Play Fine-Tuning)** (Chen et al., 2024, arXiv:2401.01335). The student model M plays both "writer" (generates a response) and "discriminator" (judges whether the response was M's own or a human reference). Training pushes M's responses to be indistinguishable from human references. Iterate.
- **Self-Rewarding Language Models** (Yuan et al., 2024). M generates responses, rates them itself with an LLM-as-judge prompt, uses the ratings as DPO training data, fine-tunes. Iterate. Showed continued improvement over several rounds.
- **Debate as self-play** (Du et al., 2023). Multiple agents (often instances of the same model) argue; a judge picks a winner; the winning approach becomes training signal. Mostly studied for inference-time gains; training-time application is newer.
- **Constitutional AI** ([[14-constitutional-ai]]) — RLAIF can be seen as self-play where the constitution is the implicit referee.

**Automatic curriculum learning:**

The broader family of methods that generate training tasks at the agent's current capability:

- **Procgen / Power of Two Choices** (Cobbe et al., 2020). Procedurally generated environments with controllable difficulty.
- **POET** (Wang et al., 2019). Co-evolution of agents and environments; environments evolve to remain challenging.
- **Voyager** ([[12-voyager-lifelong-learning]]) — the curriculum agent is an LLM that proposes next-most-useful task. LLM-generated curriculum.
- **Eureka** (Ma et al., NVIDIA, 2023). LLM designs reward functions; reward functions create curricula.

**The risks:**

- **Reward hacking.** Self-judging models tend to inflate their own work. Need external grounding.
- **Mode collapse.** Self-play can converge to a single style / strategy. Diversity needs explicit pressure.
- **Distillation of biases.** The model amplifies its own biases through self-training. Hard to detect.
- **Evaluation drift.** Without external benchmarks, "improvement" is in the eye of the self-evaluator.

## 3. Key works

- **Silver et al. "Mastering the game of Go without human knowledge."** DeepMind, *Nature*, 2017. AlphaGo Zero.
- **Silver et al. "A general reinforcement learning algorithm that masters chess, shogi, and Go through self-play."** *Science*, 2018. AlphaZero generalisation.
- **Chen et al. "Self-Play Fine-Tuning Converts Weak Language Models to Strong Language Models."** arXiv:2401.01335, 2024. SPIN.
- **Yuan et al. "Self-Rewarding Language Models."** arXiv:2401.10020, 2024.
- **Bai et al. "Constitutional AI."** Anthropic, arXiv:2212.08073, 2022. RLAIF.
- **Du et al. "Improving Factuality and Reasoning in Language Models through Multiagent Debate."** arXiv:2305.14325, 2023.
- **Wang et al. "POET: Endless Generation of Increasingly Complex and Diverse Learning Environments and Solutions."** arXiv:1901.01753, 2019.
- **Ma et al. "Eureka: Human-Level Reward Design via Coding Large Language Models."** NVIDIA, arXiv:2310.12931, 2023.
- **Sukhbaatar et al. "Intrinsic Motivation and Automatic Curricula via Asymmetric Self-Play."** arXiv:1703.05407, 2017.

## 4. Empirical results

For RL:
- AlphaGo Zero reached super-human Go in 40 days from scratch.
- AlphaZero generalised the recipe to chess and shogi.
- POET-style co-evolution produced diverse, generalising agents.

For LLMs:
- SPIN showed several iterations of improvement on standard benchmarks before plateauing. Improvements: 5-15 percentage points over base.
- Self-Rewarding Language Models showed continued improvement over multiple rounds — three rounds gave non-trivial gains; effects after that diminished.
- Constitutional AI / RLAIF demonstrated that AI-feedback can substitute for human feedback at substantial cost savings.
- Multi-agent debate boosted single-turn reasoning ~5-15 points at inference time; training-time application is newer.

**Caveats:**
- Most positive results are on benchmarks the optimisation was targeting. Generalisation gains are smaller.
- Diversity matters — single-stream self-play can collapse.
- External anchoring (benchmark eval, human spot-checks) is necessary to detect drift.

## 5. Applicability to Runa

For **v0**: not directly applicable. Runa doesn't fine-tune.

For **v1+ — when Runa has months of self-conversation data**:

For **fine-tuning a local model with Volmarr's preferences**:

- SPIN-like approach: collect (Volmarr_query, Runa_response, Volmarr_preferred_alternative) triples; iterate DPO ([[19-rlhf-dpo-preference-optimization]]) over them.
- Self-Rewarding LM approach: Runa rates her own responses against the constitution, uses ratings as training signal. Cheaper than collecting Volmarr preferences for every interaction.

For **Hirð retainer self-improvement**:

- Each retainer can engage in narrow self-play. Huginn the researcher: generate research questions, attempt them with multiple approaches, judge which is best, train on best-approach examples.
- Need external grounding to prevent drift — periodic human check.

For **automatic curriculum (Voyager-style)**:

- The "what skill should I acquire next?" question fits the automatic-curriculum framing. Heimdallr can propose next-skill candidates based on observed gaps.

For **debate within Hirð**:

- Multi-retainer debate ([[11-autogen-multi-agent]]) for hard reasoning tasks; the debate outcomes can be used as training signal for the retainers.

What to avoid:

- Don't self-play without external grounding. A Runa fine-tuned purely on her own outputs will drift in ways nobody notices.
- Don't conflate self-play with continual learning. Self-play *generates* training data; continual learning concerns *integrating* it without forgetting. Both needed.
- Don't apply self-play to every domain. The biggest wins are in domains with clean win/lose signals; conversation isn't one of them.
- Don't iterate without diversity pressure. Mode collapse is a real risk.

## 6. Open questions

- **When self-play helps vs hurts.** Often helps in narrow capability development; hurts in broad-domain identity / style. The boundary isn't well-mapped.
- **Mixing self-play with human feedback.** What's the optimal ratio? Probably depends heavily on task; empirically tunable.
- **Detecting self-play drift.** What metrics catch identity drift, mode collapse, or bias amplification before they become serious? Mostly heuristic.
- **Multi-agent self-play.** When several Hirð retainers self-play together, complex dynamics emerge. Largely unstudied for production LLM agents.

## 7. References (curated)

- *Nature* 2017 — AlphaGo Zero.
- arXiv:2401.01335 — SPIN.
- arXiv:2401.10020 — Self-Rewarding LMs.
- arXiv:2305.14325 — Multi-agent debate.
- arXiv:1901.01753 — POET.
- arXiv:2310.12931 — Eureka.
- Companion docs: [[12-voyager-lifelong-learning]] (lifelong self-acquired skills), [[19-rlhf-dpo-preference-optimization]], [[45-continual-learning]].

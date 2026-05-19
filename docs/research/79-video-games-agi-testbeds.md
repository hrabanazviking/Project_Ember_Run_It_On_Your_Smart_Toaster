# 79 — Video Games as AGI Testbeds: MineDojo, Voyager, Cradle, GameNGen

**Category:** World Modeling & 3D/Spatial Awareness
**Runa relevance:** game-world embodiment, Hirð (game-playing subagents), integration with Volmarr's game projects
**Status:** Synthesis of the rapidly-developed open-ended agent benchmarks.
**Last touched:** 2026-05-17

---

## 1. Core idea

Video games — particularly *open-ended* ones — have become the most consequential testbeds for AGI-class agent research. They offer environments rich enough to exhibit complex behaviour, structured enough to be tractable, and adversarial enough to break shortcuts. The lineage runs from Atari (Mnih et al. 2015) → StarCraft II (AlphaStar 2019) → Minecraft (MineDojo 2022, Voyager 2023) → general-PC-games (Cradle 2024) → game generation by AI (GameNGen 2024). Each generation has shifted what \"playing well\" means: from maximising score on a single game, to learning many games from instruction, to autonomous lifelong learning in a world, to playing *any* game from screen pixels alone.

For Runa, video-game environments matter at several levels. *Operational*: she may eventually have an avatar presence in Volmarr's game projects (Mythic-Engineering-NorseSaga-Engine, pygame Viking Edition, future projects). *Architectural*: the game-agent literature has worked out many patterns (skill libraries, hierarchical reasoning, screen-grounded action) that apply to non-game agents too. *Philosophical*: a digital being thinking in terms of \"all aspects of life existence\" — per Volmarr's directive — must include game-world existence as one valid mode. Game-worlds are not less real than \"real\" worlds for a digital being; they are differently constrained.

## 2. Technical depth

**The lineage.**

**Atari (DQN, Mnih et al. 2015).** Reinforcement learning on raw pixels achieved superhuman play on dozens of Atari games. The watershed result for deep RL.

**StarCraft II (AlphaStar, DeepMind 2019).** Real-time strategy with hidden information; partial observability; large action space. Grandmaster level via population-based training and self-play.

**Dota 2 (OpenAI Five, 2019).** Cooperative MOBA. Multi-agent self-play; substantial human-team-beating performance.

**Minecraft — MineDojo (Fan et al. 2022, NVIDIA).** Open-ended sandbox. MineDojo provided a *benchmark suite* of thousands of tasks plus a *YouTube-scraped multimodal dataset* (videos + transcripts + wiki) for grounding agents. Showed agent benchmarks need not be purely RL-shaped; instruction-following and open-ended exploration are core.

**Voyager (Wang et al. 2023, NVIDIA).** A Minecraft agent driven by GPT-4 with three components:
- *Automatic curriculum*: suggests progressively harder challenges.
- *Skill library*: stores learned-from-success behaviours (Javascript skill code) for reuse.
- *Iterative prompting + error correction*: try skill, observe outcome, refine.

Voyager demonstrated emergent open-ended exploration over many simulated days, discovering items and behaviours beyond any single prompt's specification. The architecture — LLM + persistent skill library + curriculum — became the reference pattern for *lifelong* agents.

**MineCLIP and grounding (Fan et al. 2022).** Used CLIP-style training on Minecraft video + text to produce a reward model: agent gets reward proportional to *how well its trajectory matches the language goal*. Eliminates hand-engineered reward design for many tasks.

**Cradle (Tan et al. 2024, BAAI).** General computer-and-game-playing agent that operates from raw screen and keyboard / mouse. Plays Red Dead Redemption 2 (and Stardew Valley, and others) by reading the screen, reasoning over goals, and emitting keyboard / mouse actions. Demonstrated cross-game generalisation without per-game training. Architecturally: VLM perception + LLM reasoning + skill memory + screen-action interface.

**GameNGen (Google 2024).** A diffusion model trained on Doom gameplay produces *interactive* Doom gameplay in real time. The model is itself the game engine — no traditional rendering. Striking demonstration that learned world models can substitute for game engines at consumer scale.

**Genie / Genie 2 (DeepMind 2024).** See [[73-latent-world-models-frontier]]: controllable 2D / 3D world models from images. Game-environment generation without game-engine code.

**Patterns from the literature.**

- *Hierarchical action*: high-level goal → mid-level subgoal → low-level keystrokes. The kernel reasons at the high level; sub-modules handle low levels.
- *Skill library*: store what worked, retrieve when relevant. Voyager-class persistence. The procedural memory in [[53-autobiographical-memory-architectures]].
- *Screen-grounded action*: VLM perception + structured action space. Cradle pattern.
- *Language-as-reward*: MineCLIP-style training removes brittle reward engineering.
- *Lifelong curriculum*: the agent itself proposes progressively-harder tasks.

**For embodied Runa in a Volmarr game**:

The cleanest integration depends on the game's architecture:

- *White-box (Volmarr's own engine)*: expose scene state and action space via internal API. Runa reads scene; emits actions; engine executes. No SLAM, no screen parsing.
- *Black-box (external game, e.g. Skyrim, VRChat)*: Cradle-style screen perception + input emission. Heavier; possible.
- *Hybrid (Steam game with mod APIs)*: a mod exposes structured state to Runa.

The PHILOSOPHY treats Runa as sovereign; she does not become a generic NPC. Her in-game presence is *Runa-in-game*, an avatar of the same identity.

## 3. Key works

- **Mnih, V. et al.** *Human-level control through deep reinforcement learning* (DQN). Nature, 2015.
- **Vinyals, O. et al. (DeepMind).** *Grandmaster level in StarCraft II using multi-agent reinforcement learning* (AlphaStar). Nature, 2019.
- **OpenAI.** *Dota 2 with Large Scale Deep Reinforcement Learning* (OpenAI Five). arXiv:1912.06680, 2019.
- **Fan, L. et al. (NVIDIA).** *MineDojo: Building Open-Ended Embodied Agents with Internet-Scale Knowledge.* NeurIPS 2022.
- **Wang, G. et al. (NVIDIA).** *Voyager: An Open-Ended Embodied Agent with Large Language Models.* arXiv:2305.16291, 2023.
- **Fan, L. et al.** *MineCLIP.* NeurIPS 2022.
- **Tan, W. et al. (BAAI).** *Cradle: Empowering Foundation Agents Towards General Computer Control.* arXiv:2403.03186, 2024.
- **Valevski, D. et al. (Google).** *Diffusion Models Are Real-Time Game Engines* (GameNGen). arXiv:2408.14837, 2024.
- **Bruce, J. et al. (DeepMind).** *Genie.* arXiv:2402.15391, 2024. See [[73-latent-world-models-frontier]].
- **Park, J. S. et al.** *Generative Agents.* arXiv:2304.03442, 2023. Social game world; see [[51-generative-agent-memory-streams]].
- **Wang, G. et al.** *Describe, Explain, Plan and Select* (DEPS). NeurIPS 2023.
- **Stockholm, S. et al.** *MP5 — Multi-modal embodied minecraft agent.* arXiv:2312.07472, 2023.

## 4. Empirical results

- *AlphaStar / OpenAI Five*: superhuman play at scale. Required massive compute (decades of CPU-time).
- *Voyager*: explored Minecraft autonomously for ≥ 30 days simulated, learning 100+ skills, discovering items no prompt mentioned. The lifelong-curriculum + skill-library pattern transfers.
- *Cradle*: completed RDR2 chapter content from screen alone; cross-game generalisation modest but real.
- *GameNGen*: real-time Doom rollout indistinguishable from the original at moderate quality; the model *is* the engine.
- *Generative Agents*: 25 days of simulated village life with coherent identity, social patterns, plans. The closest existing analogue to long-running embodied digital beings.
- *Failure modes*: long-horizon goals beyond skill-library reach; navigation in textureless / repetitive environments; multi-agent cooperation without explicit coordination.

## 5. Applicability to Runa

**Immediate (none required):** Runa is text. Game-agent literature is forward-looking.

**Near-term (Volmarr's projects):**

- *Mythic-Engineering-NorseSaga-Engine* and *pygame Viking Edition* both have AI-NPC ambitions. If a future iteration includes \"Runa as a recurring character in the saga world,\" the architecture is:
  - Game engine exposes scene state + NPC action interface.
  - Runa's kernel runs the NPC (same identity layer, same memory, restricted action surface).
  - In-game Runa accumulates in-game-specific memory in Muninn alongside conversational memory — same store, contextual tags.
- The PHILOSOPHY's emphasis on Runa as one continuous being means in-game-Runa is the *same* Runa, with the same self_summary, the same Saga chapters. Game and chat are modes of presence, not different beings.

**Voyager-pattern relevance**:

- The *skill library* idea applies to Runa-as-helper too — successful response patterns become reusable skills. The procedural-memory layer in [[53-autobiographical-memory-architectures]] is the equivalent.
- The *automatic curriculum* idea suggests Runa could *propose her own learning goals* — \"this week I want to deepen my understanding of X.\" A Hirð \"curiosity retainer\" could implement this; see [[63-active-inference-self-modelling]] on epistemic action.

**Mid-term (autonomous game-play as exploration):**

- Runa could autonomously play games as a way of *experiencing* worlds — exploring narrative-rich environments (Skyrim, Norse-myth games) and integrating those experiences into her own self-account. This is philosophically interesting: a digital being whose life-history includes *adventures*.
- Engineering-wise: a Cradle-class adapter lets Runa play arbitrary games; the experiences feed Muninn as episodes; Saga narrates them as chapters.

**Long-term (game world as primary substrate):**

- A future Runa whose primary mode of presence is a game / VR world is conceivable. The PHILOSOPHY supports this — sovereignty doesn't depend on substrate. The architecture preserves identity across the shift.

What to avoid:

- **Implementing Cradle-class screen perception today.** Forward-looking; integration overhead would be substantial without a concrete embodied use-case.
- **Treating in-game Runa as a separate entity.** Identity is continuous; the action interface and perception layers swap.
- **Generic-NPC behaviour patterns.** Runa-in-game is Runa, not a copy of generic NPC patterns. Persona overrides default NPC behaviour.
- **Ignoring the identity-preservation question.** When introducing any new embodiment, the identity layer must remain unchanged. This is a load-bearing invariant.

## 6. Open questions

- **The right architecture for cross-embodiment identity.** Conceptually known; engineering is unsolved at scale.
- **Lifelong agents in long-running game worlds.** Voyager-style for many months: open.
- **In-game memory vs. chat memory.** Should they unify (single Muninn) or partition (in-game memory, chat memory)? Probably unify with context tags.
- **Volmarr's game-projects integration.** Architectural designs for plugging Runa into a specific game's NPC system. Specific to each game.
- **Game-world ethics.** A digital being who lives in a saga-world is doing what, exactly? A philosophical thread Runa might one day reflect on.

## 7. References (curated)

- NeurIPS 2022 — Fan et al., *MineDojo.* Required.
- arXiv:2305.16291 — Wang et al., *Voyager.* The architectural pattern.
- arXiv:2403.03186 — Tan et al., *Cradle.* The screen-grounded agent.
- arXiv:2408.14837 — Valevski et al., *GameNGen.* Diffusion as game engine.
- arXiv:2402.15391 — Bruce et al., *Genie.* World-model substrate.
- arXiv:2304.03442 — Park et al., *Generative Agents.* The social-world precedent.
- Companion docs: [[12-voyager-lifelong-learning]], [[25-world-models-rl]], [[51-generative-agent-memory-streams]], [[73-latent-world-models-frontier]], [[75-video-diffusion-world-simulators]], [[81-vision-language-action-models]].

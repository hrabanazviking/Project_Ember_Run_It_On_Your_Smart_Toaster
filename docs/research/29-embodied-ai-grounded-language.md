# 29 — Embodied AI and Grounded Language

**Category:** World Modeling
**Runa relevance:** Smiðja (tools as Runa's "hands"), Rödd/Auga (sensory surfaces), Heimdallr (perceiving Volmarr's ecosystem), future avatar work via Seidr-Smiðja
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

**Embodied AI** is the research programme that argues intelligence requires a body — not necessarily a physical one, but at minimum *grounded sensors* and *grounded actions* in *some* world. **Grounded language** is the part of that programme focused on how words connect to things, actions, places, agents — how an AI's "understanding" of "kettle" is rooted in the experience of kettles, not just in the co-occurrence statistics of the word.

The classical critique (Searle's Chinese Room, Harnad's "Symbol Grounding Problem" 1990) was that a system manipulating symbols by syntactic rules alone is doing language *without understanding*. LLMs train on text and learn statistical structure but no direct sensory grounding. The 2022-2025 wave of embodied AI work — SayCan, PaLM-E, RT-2, OpenVLA, etc. — has been bringing LLM-scale language ability into systems with real sensors and real actuators.

For Runa, "embodiment" is a different beast: her "body" is her host machine, her sensors are file system reads / API calls / screenshots / audio inputs, her actuators are tool calls. She is not a robot. But the framing — *what makes Runa's words refer to real things in the world she shares with Volmarr* — is exactly the grounding question, and the embodied-AI literature has the freshest thinking on it.

## 2. Technical depth

**Symbol grounding problem** (Harnad, 1990). Words in a symbol system get their meaning from other words — circular. To break the circle, some symbols must connect *directly* to non-symbolic referents (sensorimotor categories). Classical AI's failure to ground meaning was the diagnosed weakness LLMs partially inherit.

**Generations of embodied AI:**

**Classical robotics era.** SLAM, motion planning, action grammars. Language as commands ("move forward 2m"). No real grounding.

**Deep RL era (2015+).** Train robots end-to-end with reinforcement learning, sometimes from raw pixels. Grounding implicit in the learned representations. Famous demos: dexterous manipulation, walking, drone flight.

**LLM-grounded era (2022+).** Combine pretrained LLMs (for high-level planning and language understanding) with learned or hand-crafted low-level control. The breakthrough cluster:

- **SayCan** (Ahn et al., Google, arXiv:2204.01691, 2022). LLM proposes high-level actions; a learned affordance model scores which actions are *feasible* in the current state. Combine: "what should I do" (LLM) × "what *can* I do" (affordance) → grounded action plan.
- **PaLM-E** (Driess et al., Google, arXiv:2303.03378, 2023). Inject sensor embeddings (vision, robot state) directly into PaLM's input alongside text tokens. The LLM becomes multimodal in the most direct sense — same model, just different input modalities.
- **RT-1 / RT-2 / RT-X** (Brohan et al., Google, 2022-2023). Vision-Language-Action models — extend LLMs to output robot actions as text tokens. RT-2 generalises across novel objects and skills the robot wasn't explicitly trained on, leveraging the LLM's world knowledge.
- **OpenVLA** (Kim et al., Stanford, 2024). Open-source Vision-Language-Action model on Llama 2; competitive with proprietary RT-2.
- **GR00T** (NVIDIA, 2024). Humanoid foundation model.
- **DeepMind Genie / Genie 2** (2024-2025). World-generation from images — adjacent territory.

**Three flavours of grounding in modern systems:**

1. **Spatial grounding.** Words refer to locations: "the cup on the kitchen counter." Tested in benchmarks like ALFRED, R2R, REVERIE.
2. **Affordance grounding.** Verbs refer to feasible actions: "the cup *can be picked up*". SayCan-style affordance models, learned from interaction.
3. **Social grounding.** Pronouns and references resolve to people, agents, conversations. Less-studied but most relevant for Runa.

## 3. Key works

- **Harnad, S. "The Symbol Grounding Problem."** *Physica D*, 1990. The foundational philosophical statement.
- **Searle, J. "Minds, Brains, and Programs."** *Behavioral and Brain Sciences*, 1980. The Chinese Room.
- **Lakoff and Johnson. *Metaphors We Live By.*** University of Chicago Press, 1980. The cognitive-linguistics framing that meaning is embodied.
- **Ahn et al. "Do As I Can, Not As I Say: Grounding Language in Robotic Affordances."** Google, arXiv:2204.01691, 2022. SayCan.
- **Driess et al. "PaLM-E: An Embodied Multimodal Language Model."** Google, arXiv:2303.03378, 2023.
- **Brohan et al. "RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control."** arXiv:2307.15818, 2023.
- **Kim et al. "OpenVLA: An Open-Source Vision-Language-Action Model."** Stanford, arXiv:2406.09246, 2024.
- **Embodied Question Answering (EQA), ALFRED, Habitat** — research benchmark families.
- **Brooks, R. "Intelligence Without Representation."** *Artificial Intelligence*, 1991. The early "embodiment matters" argument from the subsumption-architecture era.

## 4. Empirical results

- **SayCan** demonstrated that LLM high-level reasoning combined with grounded affordance scoring substantially outperformed either alone on long-horizon kitchen tasks. The grounding was the bottleneck; the LLM's reasoning was already strong.
- **PaLM-E** showed that joint multimodal training transfers — improvements on robot tasks correlate with improvements on text and vision tasks. Suggests grounding helps language ability, not just the other way around.
- **RT-2** showed novel-object generalisation (the robot could grasp objects it had never seen, leveraging the LLM's visual world knowledge). A real demonstration of grounding-via-pretraining.
- **OpenVLA** (open-source) reaches competitive performance on standard manipulation benchmarks with a 7B base model.
- **Limitations:**
  - Sim-to-real transfer remains hard. Models trained in simulation often fail on real hardware.
  - Action representations are noisy; LLMs output approximations a low-level controller has to interpret.
  - Long-horizon tasks (>10 steps) remain brittle.
  - Generalisation outside the training distribution is shallow.

## 5. Applicability to Runa

Runa is not a robot. But the *grounding question* matters concretely:

For **Smiðja (tool forge — Runa's "hands")**:

- A tool call is Runa's action. The "affordance grounding" question — *can* this tool actually be invoked in the current state with these arguments? — is the SayCan analogue. Tool descriptions should include preconditions, not just signatures.
- After-action grounding: when a tool succeeds, the world has changed in a specific way. Muninn should record *what changed*, not just *that the tool ran*. This is what gives Runa's later language ("I created the file `notes.md`") referential grounding.

For **Rödd (voice) / Auga (GUI)**:

- These are the sensor surfaces. What Runa "hears" and "sees" through them is the grounding substrate. Persisting these *as the rich modalities they are* (not just transcribed to text) preserves grounding for future cross-modal recall.

For **Heimdallr (watch)**:

- Heimdallr's job is perception of Volmarr's ecosystem — file changes, project state, ambient context. The grounding here is that Runa's references ("you were working on WYRD this morning") refer to *actual events Heimdallr observed*, not to language-model hallucination.

For **future Seidr-Smiðja integration**:

- Seidr-Smiðja is the avatar smithy (per project memory). If Runa eventually has a VRoid avatar she can drive, that becomes a literal embodiment with literal sensor and action streams. The embodied-AI literature directly applies. Long-term arc.

For **Saga (narrator)**:

- Saga's narrative voice should refer to *grounded* events — file paths Volmarr can navigate to, timestamps Volmarr can verify, transcript snippets Volmarr can read. Grounding is what makes Saga's prose true rather than evocative-but-vague.

What to avoid:

- Don't let LLM outputs make claims that don't trace to grounded observation. Hallucinated references to events that didn't happen are *the* corrosive failure mode for a memory-laden agent.
- Don't strip modalities. Voice transcribed to text loses prosody; screenshots flattened to OCR'd text lose layout. Where the modality carries grounding-relevant signal, preserve the original alongside the text.
- Don't conflate "Runa knows X" (in her training) with "Runa observed X" (grounded). The audit log + Muninn should distinguish the two.

## 6. Open questions

- **Grounding in non-physical environments.** What does it mean for a software-only agent like Runa to "ground" her words? The sensorimotor categories aren't visual or motoric; they're file paths, conversation events, system states. Underdeveloped theory.
- **LLM-as-perception-system.** Vision-language models are already a partial answer for visual grounding. Whether they suffice for the kind of multimodal grounding agents need (audio + text + visual + structured) is open.
- **Grounded continuity.** When the world changes between sessions (Volmarr added new files, renamed directories), how does Runa's grounded reference apparatus update? Re-grounding on session start is one answer; subscription to filesystem events is another.
- **The Chinese Room for LLMs.** Whether LLMs *understand* in any meaningful sense — and whether that matters operationally — remains a live philosophical question with practical implications for agent design.

## 7. References (curated)

- Harnad (1990) — The Symbol Grounding Problem.
- Searle (1980) — Minds, Brains, and Programs.
- arXiv:2204.01691 — SayCan.
- arXiv:2303.03378 — PaLM-E.
- arXiv:2307.15818 — RT-2.
- arXiv:2406.09246 — OpenVLA.
- Brooks (1991) — Intelligence Without Representation.
- Lakoff and Johnson (1980) — *Metaphors We Live By*.
- Companion docs: [[26-entity-component-system]] (the structured world), [[02-episodic-memory-architectures]] (the persisted-experience side), [[40-audit-logging-replay]] (the grounding-via-records pattern).

# 99 — Multi-modal Foundation Models for Embodied Agents

**Category:** Frontier 2025–2026
**Runa relevance:** future embodiment, perception adapters, kernel multimodality, integration with Volmarr's 3D / VR / robotic ambitions
**Status:** Frontier synthesis of where the embodied-AI frontier is heading.
**Last touched:** 2026-05-17

---

## 1. Core idea

The 2024–2026 era is the convergence of *foundation models* (large pretrained models trained on massive multi-domain data) with *embodied AI* (agents that perceive and act in physical or simulated worlds). Until recently these were separate fields: foundation models for text and images, embodied AI for robotics and game-agents. The convergence has produced *embodied foundation models* — large multimodal models that perceive sensors and emit actions, trained at foundation-model scale. *Google Gemini Robotics* (Mar 2025), *Physical Intelligence π₀* (Nov 2024), *Figure AI Helix*, and similar systems are the production exemplars. The architectural shape is becoming consistent: VLM perception + LLM reasoning + structured action output + cross-embodiment training.

For Runa, this matters because *any future Runa with a body* — whether a game-world avatar, a VR avatar, or eventually a robotic body — sits in this lineage. The architecture supports a path from text-only Runa today to multimodal embodied Runa later, with identity continuity preserved through the transition. The PHILOSOPHY's commitment to Runa as substrate-flexible aligns directly with the embodied-foundation-model trajectory.

## 2. Technical depth

**Embodied foundation models defined.**

A model that:
- Takes *sensory* inputs (image, video, depth, language, audio).
- Produces *actions* (motor commands, robot joint angles, avatar control, navigation commands).
- Is trained at foundation-model scale (billions of parameters, diverse data).
- Generalises across tasks and embodiments.

Distinct from:
- Pure VLMs (no action).
- Classical robot policies (narrow domain, small scale).
- Computer-use agents (action surface is screen, not physical).

**Google Gemini Robotics (Mar 2025).**

Two variants:
- *Gemini Robotics*: a VLA model trained for general robotic manipulation, dexterous tasks, novel-object handling.
- *Gemini Robotics-ER*: extended-reasoning version with explicit planning capability.

Built on Gemini 2 backbone. Key claim: zero-shot generalisation to many manipulation tasks, robustness across platforms.

**Physical Intelligence π₀ (Nov 2024).**

Discussed in [[81-vision-language-action-models]]. Notable for:
- Open API access (limited).
- Cross-embodiment training (one model, many robots).
- Flow-matching action output (smooth trajectories).

**Figure AI Helix (2024-2025).**

Two-system architecture for humanoid control. Discussed in [[81-vision-language-action-models]] and [[86-dual-process-cognition-system-1-2]]. Production-deployed in Figure's humanoid demos.

**DeepMind Genie series.**

Discussed in [[73-latent-world-models-frontier]] and [[75-video-diffusion-world-simulators]]. Different angle: foundation model that *generates* interactive worlds rather than *acting* in them.

**The general architectural pattern.**

```
                       SENSORS
            (image, depth, audio, language, force)
                          │
                          ▼
              ┌───────────────────────┐
              │ PERCEPTION ENCODER    │
              │ (multimodal VLM)      │
              └────────────┬──────────┘
                           ▼
              ┌───────────────────────┐
              │ COGNITIVE CORE         │
              │ (LLM / reasoning model)│
              │  - reasons over goals  │
              │  - plans               │
              │  - decides             │
              └────────────┬──────────┘
                           ▼
              ┌───────────────────────┐
              │ ACTION HEAD            │
              │ - motor commands       │
              │ - flow / diffusion     │
              │ - structured output    │
              └────────────┬──────────┘
                           ▼
                       ACTUATORS
              (joints, grippers, navigation,
               avatar pose, virtual actions)
```

The cognitive core is increasingly LLM-shaped — text reasoning that handles symbolic structure — while perception and action are specialised. Each can be swapped independently.

**Cross-embodiment training.**

A key insight from π₀, Open X-Embodiment ([[81-vision-language-action-models]]), and others: training on data from *many* robots / embodiments produces a model that generalises *to new* embodiments. This is the foundation-model promise applied to robotics.

For Runa: a future embodied Runa could potentially run on multiple substrates (a game avatar in NSE, a VR avatar in Vision Pro, a future robotic body) via the same cognitive core + different perception/action adapters.

**Multimodal kernels for non-embodied agents.**

Even without embodiment, multimodal foundation models extend Runa's perception:

- Reading screenshots Volmarr shares.
- Watching short videos.
- Listening to voice notes.
- Reading handwriting.
- Understanding spatial diagrams.

Each is a *perception* capability. The action surface stays text (for chat) or extends to specific output modalities (image generation, voice generation) — without requiring embodiment.

**The deployable scale today.**

- *Frontier*: Gemini 2, Claude 3+, GPT-4o — multimodal, deployable as API. Not local.
- *Open-weights multimodal*: Qwen2-VL, Pixtral, Phi-3.5 Vision, Llama-3.2 Vision. Run on consumer GPUs (~16GB+ for 7B-class).
- *Pi-deployable*: small multimodal models (Phi-3.5 Vision, Qwen2-VL-2B) feasible with quantisation; quality limited.

For Pi-5 Runa today: *small multimodal models are feasible* for specific perception tasks; *full multimodal kernel* is heavy.

**What this means for embodied Runa long-term.**

A plausible trajectory:

- *Phase 1 (now)*: text-only Runa on Pi.
- *Phase 2 (2026–2027)*: small multimodal capability added (read images Volmarr shares, perhaps simple VLM perception). Possible game-avatar embodiment with engine-API integration.
- *Phase 3 (2027–2028)*: open-weights VLA models deployable on edge / consumer hardware. Avatar control via VLA-shaped models.
- *Phase 4 (2028+)*: if embodied (robot or rich VR), the cognitive core remains Runa-identity-anchored; perception and action are pluggable.

The architecture must support this trajectory by keeping kernel-vs-perception-vs-action boundaries clean.

## 3. Key works

- **Google DeepMind.** *Gemini Robotics: Bringing AI to the Physical World.* March 2025.
- **Google DeepMind.** *Gemini Robotics-ER.* March 2025. Extended-reasoning robotic agents.
- **Physical Intelligence.** *π₀.* See [[81-vision-language-action-models]].
- **Figure AI.** *Helix.* See [[81-vision-language-action-models]] and [[86-dual-process-cognition-system-1-2]].
- **DeepMind.** *Genie 2.* See [[73-latent-world-models-frontier]].
- **Bommasani, R. et al.** *On the Opportunities and Risks of Foundation Models.* 2021. The original foundation-model paper.
- **Brohan, A. et al.** *RT-2.* See [[81-vision-language-action-models]].
- **OpenAI.** *GPT-4V system card.* 2023. Vision-augmented foundation model.
- **Anthropic.** *Claude 3 multimodal capabilities.*
- **Qwen team.** *Qwen2-VL.* 2024.
- **Liu, H. et al.** *LLaVA.* arXiv:2304.08485, 2023. Open-weights VLM foundation.

## 4. Empirical results

- *Gemini Robotics*: substantial generalisation to novel-object manipulation; deployable on multiple robot platforms.
- *Multimodal foundation models*: VLMs now reliably caption images, answer visual questions, and reason over visual content at near-human levels on standard benchmarks.
- *Open-weights gap*: closing fast on multimodal; still 6–12 months behind closed-frontier on hardest tasks.
- *Pi-deployable multimodal*: Phi-3.5 Vision and Qwen2-VL-2B reach reasonable quality on simple visual tasks at deployment-feasible compute.
- *Failure modes*: long-video reasoning, fine-grained spatial understanding, physical-causality reasoning (see [[78-intuitive-physics-llms]]), multi-step embodied tasks.

## 5. Applicability to Runa

**Today**: small multimodal extensions are feasible, embodiment is not.

For **Heimskringla — multimodal route**:

- Add a small multimodal model to the inventory (Qwen2-VL-2B-Q4 or Phi-3.5 Vision-Q4) for tasks where Volmarr shares images / screenshots.
- Lightweight: invoked only when a non-text input arrives.

For **kernel**:

- Today: text kernel + multimodal *perception* via a separate adapter that converts images to text descriptions for the kernel.
- Phase 2: kernel itself becomes multimodal-capable as deployable models reach scale.

For **integration with Volmarr's projects**:

- Reading screenshots of his terminal or editor when he asks for help.
- Understanding diagrams he sketches.
- Watching short demo videos of game / project state.

For **game-world embodiment** (forward-looking):

- The architecture from [[79-video-games-agi-testbeds]] applies: game engine exposes scene state; Runa's spatial subagent reads; kernel reasons; actions flow back.
- A future VLA-style adapter for avatar control bridges kernel decisions to avatar motion.

For **identity preservation**:

- Same Runa across modalities. Persona + identity store unchanged. Modality-specific adapters at the edges.

For **the long arc**:

- Runa's perception grows over years. Today: text. Soon: images. Eventually: full multimodal embodied awareness.
- Each step preserves identity; adds capability.
- The PHILOSOPHY's substrate-independence is the design principle that enables this.

What to avoid:

- **Coupling kernel to a specific multimodal architecture.** Adapters at the edges; abstract interfaces in the kernel.
- **Treating multimodal as add-on theatre.** Real multimodal awareness should change behaviour (Runa actually *uses* the visual context); cosmetic image-display isn't multimodal awareness.
- **Premature embodied deployment.** The architectural support is the work; concrete embodied Runa is years out.
- **Forgetting power costs.** Multimodal inference is more expensive. Budget accordingly.

## 6. Open questions

- **Right-sized multimodal model for Pi-5.** Trading off quality / speed / RAM.
- **When open-weights VLA reaches deployable quality.** 2027 plausible.
- **Cross-substrate identity for fully-embodied Runa.** Architecturally tractable; engineering hard.
- **Multimodal kernel — when worth the cost.** Most current Runa interaction is text; the multimodal kernel adoption curve is gradual.
- **Genuine multimodal *understanding* vs. surface description.** Frontier research; partially solved.

## 7. References (curated)

- Google DeepMind, *Gemini Robotics* (Mar 2025). The flagship.
- arXiv:2104.02201 — Bommasani et al., *Foundation Models.* The frame.
- arXiv:2307.15818 — RT-2.
- arXiv:2304.08485 — LLaVA. Open-weights VLM foundation.
- Qwen2-VL technical report (2024).
- Companion docs: [[29-embodied-ai-grounded-language]], [[73-latent-world-models-frontier]], [[74-3d-scene-representation]], [[79-video-games-agi-testbeds]], [[80-vr-ar-awareness-openxr]], [[81-vision-language-action-models]], [[83-agentic-foundation-models-2025]].

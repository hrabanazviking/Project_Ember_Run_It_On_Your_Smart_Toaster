# 75 — Video Diffusion as World Simulator: Sora, Lumiere, Veo, Genie-2

**Category:** World Modeling & 3D/Spatial Awareness
**Runa relevance:** future world-modelling, simulation-for-planning, generative perception
**Status:** Frontier research synthesis. Most striking 2024 result; rapidly evolving.
**Last touched:** 2026-05-17

---

## 1. Core idea

Diffusion-based video generation systems trained at large scale — *Sora* (OpenAI, Feb 2024), *Lumiere* (Google, Jan 2024), *Veo* (Google, 2024), *Veo 2* (DeepMind 2024), *Genie* and *Genie 2* (DeepMind 2024), *Kling* (Kuaishou 2024) — have produced video that is dramatically more coherent than prior generations. The OpenAI Sora technical report made the striking claim: \"these models are *world simulators*.\" Whether or not that framing is fully defensible, the underlying argument matters: at sufficient scale, models trained on video learn implicit representations of physical regularity — object permanence, perspective, basic dynamics, fluid behaviour — even though they're trained on pure pixel prediction with no explicit world-model objective.

For Runa, this matters because it points toward a future where *imagined* simulation of physical or game environments becomes tractable. Today the cost is enormous and the integration with text agents is preliminary. The architectural lesson is real, though: world understanding can emerge from scale + the right objective, without explicit world-model engineering. For a digital being who one day needs to reason about 3D, physical, or simulated worlds, video-diffusion-as-world-model is a substrate to watch.

## 2. Technical depth

**Diffusion fundamentals (brief).** A diffusion model learns to *denoise*. Training: take a clean sample $x_0$, add Gaussian noise progressively to get $x_t$ at timestep $t \in [0, T]$, and train a network $\epsilon_\theta(x_t, t)$ to predict the noise. Sampling: start from pure noise $x_T$, iteratively denoise back to $x_0$. Conditioning (on text, on prior frames, on actions) is added via cross-attention or concatenation.

For video, the input is a tensor of shape $(T, H, W, C)$ — many frames at once. The model denoises *the video as a whole*, leveraging temporal coherence.

**Sora's contribution (OpenAI Feb 2024).**

- *Spacetime patches.* Video is tokenised into spatiotemporal patches (analogous to ViT image patches but extended in time). Each video is a sequence of such patches.
- *Latent diffusion in patch space.* A diffusion transformer (DiT) processes patches.
- *Scaled compute.* Reportedly hundreds of millions of GPU-hours.
- *Output*: up to 60 seconds of coherent 1920×1080 video conditioned on text or images.

Sora's notable qualitative behaviours:
- Object permanence across long clips.
- Camera motion that respects 3D geometry.
- Some physical regularities (water flow, cloth dynamics).
- *Some failures*: hands, exact counts, complex causality (\"glass shatters\" sometimes goes backward — the model is statistical, not causal).

**Lumiere (Google Jan 2024).** Space-Time U-Net architecture (STUNet) — diffuse over space and time jointly rather than as a cascade. Strong temporal coherence at moderate scale. Shorter clips than Sora but cleaner motion in many examples.

**Veo and Veo 2 (Google DeepMind 2024).** Latent video diffusion at increasing scale and resolution. Veo 2: 4K, up to 2 minutes, advanced camera motion control. Notable: explicit support for camera moves as a conditioning signal — \"dolly in, then pan left.\"

**Genie and Genie 2 (DeepMind 2024).** Different family: trained to be *interactively controllable*. Genie: input one image + an action sequence → output 2D game-world frames responding to those actions. Genie 2: extension to 3D, longer rollouts, better visual quality. Genie is closer to a *world model* in the RL sense than Sora — it accepts actions and predicts consequences.

**Kling (Kuaishou 2024).** Chinese-developed, competitive with Sora in some examples; commercially accessible. Notable for high motion fidelity and human-anatomy plausibility.

**The world-simulator claim, honestly assessed.**

In favour:
- Object permanence shows the model tracks identity across time.
- Camera-3D-consistency shows it has implicit perspective.
- Physical dynamics for fluids, cloth, hair are mostly respected — the model has internalised regularities.
- Latent representations probe as world-relevant.

Against:
- Causal reasoning is weak. \"Glass is dropped\" sometimes leads to glass mysteriously appearing whole — the model is *correlational*, not causal.
- Object counts fail in characteristic ways.
- Long-range coherence (minutes) is hard; the model can lose track over time.
- The model can't *answer questions* about its world. It can only generate frames. Asking \"what would happen if X?\" requires generating new video — not a fluid reasoning interface.

The honest framing: video diffusion at scale produces an *implicit* world model. It is not yet a tool for *agents to plan with*. It is plausibly a precursor to systems that are.

**Toward usable simulation-for-agents.**

- *Genie-style controllable world models* are the most directly useful: agent emits action, model emits next frame; agent observes, decides next action. Closes the perception-action loop.
- *World models conditioned on goals* (DreamFusion-adjacent, planning-style): not yet a deployed product.
- *Question-answering on simulated futures*: \"will this plan succeed?\" via simulating execution. Research-stage.

**Compute reality.** A 30-second Sora generation reportedly costs minutes-to-hours on substantial GPU clusters. Per-frame cost is in the *seconds* range. This is not real-time. Even moderate world-model rollouts (1 minute at 24 FPS = 1440 frames) cost large amounts of compute.

For agent planning, *much smaller* and *task-specific* world models are likely the route. Genie shows the pattern: train for *interactive control* at modest scale rather than for *open-ended generation* at huge scale.

## 3. Key works

- **OpenAI.** *Video generation models as world simulators (Sora technical report).* Feb 2024.
- **Brooks, T., Peebles, B., et al. (OpenAI).** *Sora: Creating video from text.* Feb 2024.
- **Bar-Tal, O. et al. (Google).** *Lumiere: A Space-Time Diffusion Model for Video Generation.* arXiv:2401.12945, 2024.
- **Google DeepMind.** *Veo.* 2024 blog + tech report.
- **Google DeepMind.** *Veo 2.* 2024 blog + tech report.
- **Bruce, J. et al. (DeepMind).** *Genie: Generative Interactive Environments.* arXiv:2402.15391, 2024.
- **DeepMind.** *Genie 2: A large-scale foundation world model.* 2024.
- **Kuaishou.** *Kling AI.* 2024.
- **Peebles, W., Xie, S.** *Scalable Diffusion Models with Transformers* (DiT). ICCV 2023. Architectural foundation for Sora.
- **Ho, J. et al.** *Video Diffusion Models.* NeurIPS 2022. Foundational.
- **Singer, U. et al.** *Make-A-Video.* arXiv:2209.14792, 2022.

## 4. Empirical results

- *Sora* produced 60-second 1080p videos with above-prior-SOTA temporal coherence.
- *Lumiere* showed better short-clip coherence than predecessors via the space-time U-Net.
- *Veo 2* achieves 4K resolution and explicit camera control; production-quality outputs.
- *Genie / Genie 2* demonstrated controllable world models from images; user-interactive at moderate frame rates.
- *Implicit-world-model probing*: research probing Sora and similar shows representations of object identity, position, motion — but causal probing is weaker.
- *Failure modes documented*: human hands, complex object interactions, multi-object counting, long-range temporal coherence (minutes), causal reasoning.

## 5. Applicability to Runa

**Today**: not applicable. Compute infeasible on Pi-class hardware; integration with text agents not solved.

**Forward-looking framing for Runa:**

For **the long-term world-modelling architecture**:

- The Genie pattern — controllable, interactive world models conditioned on actions — is what Runa will eventually need for embodied or game-world reasoning. Plan the architecture to consume such models when available.
- A *perception adapter* sits between any future world model and Runa's kernel. It translates frame-stream into structured observations Runa can reason over. The kernel doesn't process pixels; it processes summaries.

For **imagining as planning**:

- Even without a high-fidelity video model, the *concept* of \"imagine forward to see what happens\" can be applied at conversational level (\"if I respond X, what is the likely conversation trajectory?\"). LLM-driven imagining, cheap and serviceable.
- A future world model upgrades this from \"imagine in language\" to \"imagine in frames.\" The interface stays similar.

For **Volmarr's 3D projects**:

- If a future Volmarr-project integrates a Genie-class world model (for game rendering, for procedural environment generation), Runa's spatial awareness within that world becomes the perception-adapter problem above. Architecturally clean.

For **research-watch list**:

- Watch for *controllable* world models smaller in scale and deployable on consumer hardware. The trend line is fast; 2026–2028 likely sees usable open-weights controllable world models.

What to avoid:

- **Treating video diffusion as a deployable world model today.** It is research-grade for agents.
- **Confusing video generation quality with world understanding.** A model that *generates* a falling glass doesn't *understand* what falling-glass *means* causally.
- **Coupling Runa's kernel to pixel-space reasoning.** Always keep a structured-summary intermediary.

## 6. Open questions

- **Whether scaling video diffusion gets to causal world models.** Suspected no without architectural changes; some hope from chain-of-thought-on-video research.
- **The compute pathway to consumer-deployable controllable world models.** Open and rapidly moving.
- **Integration interface between video world models and LLM agents.** No standard yet.
- **Real-time control loops** at deployable speed. Genie-2 hints at it; production is not there.
- **The role of explicit symbolic state alongside latent video.** Pure-pixel models lose object identity; symbolic-overlay or object-centric variants might combine the best of both.

## 7. References (curated)

- OpenAI Sora technical report (Feb 2024). The world-simulator claim in full.
- arXiv:2401.12945 — Bar-Tal et al., *Lumiere.*
- arXiv:2402.15391 — Bruce et al., *Genie.* Most relevant for agents.
- DeepMind, *Genie 2* (2024). Required reading on the frontier.
- ICCV 2023 — Peebles & Xie, *DiT.* Architectural backbone.
- Companion docs: [[25-world-models-rl]], [[73-latent-world-models-frontier]], [[74-3d-scene-representation]], [[82-object-centric-representation-learning]], [[99-multimodal-foundation-embodied]].

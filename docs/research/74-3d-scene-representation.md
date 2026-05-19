# 74 — 3D Scene Representation: NeRF, Gaussian Splatting, 3D Foundation Models

**Category:** World Modeling & 3D/Spatial Awareness
**Runa relevance:** future embodied perception, VR/AR awareness, integration with 3D worlds (Seidr-Smidja, pygame projects)
**Status:** Frontier research synthesis. Heavy compute today; rapidly democratising.
**Last touched:** 2026-05-17

---

## 1. Core idea

Representing 3D scenes computationally is fundamental to spatial understanding. Classical 3D representations — meshes, voxel grids, point clouds — are explicit but coarse; they trade off resolution, memory, and dynamism. The last six years have seen a revolution: *neural* and *Gaussian* representations that are continuous, photorealistic, and learnable from images alone. Neural Radiance Fields (NeRF, Mildenhall et al. 2020) represent a scene as a function mapping 3D position + viewing direction to colour and density. *3D Gaussian Splatting* (Kerbl et al. 2023) represents the scene as a collection of millions of anisotropic Gaussian blobs; renders far faster than NeRF with comparable or better quality. Both made high-quality novel-view synthesis from a handful of photos tractable; both are foundational to where 3D scene understanding is going.

For Runa today, this is not directly applicable — she is text. For Runa's near future (integration with Volmarr's 3D and game projects — Seidr-Smidja, pygame Viking Edition, Mythic-Engineering-NorseSaga-Engine) and her long-term embodiment, knowing the landscape is essential. The bigger story: 3D scene representations are converging into *3D foundation models* — large pre-trained networks that understand 3D structure across many domains — analogous to LLMs for text. When these mature, Runa's perception of 3D environments (virtual or physical) will rest on them.

## 2. Technical depth

**NeRF (Mildenhall et al. 2020).**

A NeRF is a small MLP $F_\Theta(x, d) = (c, \sigma)$ mapping a 3D point $x$ and view direction $d$ to RGB colour $c$ and density $\sigma$. To render a pixel:

1. Cast a ray from the camera through the pixel.
2. Sample many points along the ray.
3. Query the MLP at each point.
4. Composite colour using volume rendering:

$$C(r) = \int_0^\infty T(t) \, \sigma(r(t)) \, c(r(t), d) \, dt, \quad T(t) = \exp\left(-\int_0^t \sigma(r(s)) ds\right)$$

The scene is *encoded entirely in the MLP weights*. Training: minimise pixel reconstruction loss across known views. Result: photorealistic novel-view synthesis.

Limits of vanilla NeRF: training is slow (hours-to-days per scene), rendering is slow (minutes per frame), and the representation is static (one fixed scene per network).

**NeRF variants and accelerations.**

- *Instant-NGP* (Müller et al. 2022): hash-grid encoding makes training and inference orders of magnitude faster. Trained scenes in seconds-to-minutes.
- *Mip-NeRF* (Barron et al. 2021): anti-aliasing for multi-scale.
- *DreamFusion* / Score Distillation Sampling (Poole et al. 2022): text-to-NeRF via 2D diffusion guidance.
- *Dynamic NeRFs* (D-NeRF, HyperNeRF, NeRFies): handle time-varying scenes.
- *Generalisable NeRFs* (PixelNeRF, IBRNet): one network for many scenes via cross-attention to source views.

**3D Gaussian Splatting (Kerbl et al. SIGGRAPH 2023).**

Represent scene as $N$ anisotropic Gaussians, each with mean $\mu \in \mathbb{R}^3$, covariance $\Sigma \in \mathbb{R}^{3\times 3}$, colour $c$ (or spherical harmonic coefficients for view-dependent colour), and opacity $\alpha$. Render via *splatting*: project each Gaussian into screen space, sort by depth, blend.

Crucial properties:
- *Real-time rendering*: 30–120 FPS on modern GPUs.
- *Editable*: Gaussians can be moved, removed, modified — explicit primitives.
- *Trainable in minutes*: optimisation of position + covariance + colour from photo set with ADAM.
- *High visual fidelity*: comparable or better than NeRF.

Variants and follow-ons:
- *Dynamic 3DGS* (Luiten et al. 2023): time-varying Gaussians for animation.
- *4D Gaussian Splatting*: video / 4D scenes.
- *Compressed 3DGS*: storage reduction (a vanilla 3DGS scene is hundreds of MB).
- *SuGaR* (Guédon, Lepetit 2024): surface-aligned Gaussians, recover meshes.
- *Gaussian Splatting for SLAM*: real-time scene reconstruction from video.

**Comparison.**

| | NeRF | 3D Gaussian Splatting |
|---|---|---|
| Representation | Implicit (MLP weights) | Explicit (Gaussian list) |
| Training | Slow (Instant-NGP fast) | Fast (minutes) |
| Rendering | Slow (NeRF) / Real-time (Instant-NGP-class) | Real-time on consumer GPU |
| Editability | Hard (implicit) | Easy (explicit primitives) |
| Memory | Tiny (a few MB MLP) | Hundreds of MB |
| Quality | High | High, sometimes higher |

**3D Foundation Models (emerging).**

The frontier: pre-train large models on diverse 3D data so that downstream tasks (single-image 3D, 3D-from-text, novel-view-synthesis, scene completion) work zero-shot or with light fine-tuning.

- *Stable-Zero123* (Stability AI 2023): single-image novel-view synthesis via diffusion guided by 3D structure.
- *Zero-1-to-3*, *MVDream*, *SyncDreamer*: image-to-3D using diffusion priors.
- *DUSt3R* (Wang et al. 2024): from two images, reconstruct 3D structure without camera-pose input. Foundational shift — no SfM preprocessing.
- *MASt3R* (2024): extends DUSt3R with matching priors.
- *Zip-NeRF* and follow-ons: scaling NeRFs to large outdoor scenes.
- *3DTopia*, *Make-A-Video3D*: text-to-3D scenes (low-fidelity today, improving fast).
- *Spatial-LM* / *3D-LLM* (Hong et al. 2023): LLMs that understand 3D inputs via 3D-feature embeddings.

The combination — 3D foundation model + LLM that can reason over 3D — is the spatially-aware AGI substrate.

**Spatial language and reasoning.** Even without owning 3D representations directly, an agent that *reads* 3D-foundation-model outputs can reason about space: \"the lamp is to the left of the chair, behind the table\". 3D-LLM and visual-language models with spatial-aware training (Spatial-VLM, RoboPoint) demonstrate that LLM-style agents can produce coherent spatial language and even *navigate* using such representations.

## 3. Key works

- **Mildenhall, B., Srinivasan, P. P., Tancik, M. et al.** *NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis.* ECCV 2020.
- **Müller, T., Evans, A., Schied, C., Keller, A.** *Instant Neural Graphics Primitives with a Multiresolution Hash Encoding.* SIGGRAPH 2022.
- **Kerbl, B., Kopanas, G., Leimkühler, T., Drettakis, G.** *3D Gaussian Splatting for Real-Time Radiance Field Rendering.* SIGGRAPH 2023.
- **Luiten, J., Karaev, N., Kopanas, G. et al.** *Dynamic 3D Gaussian Splatting.* arXiv:2308.09713, 2023.
- **Poole, B. et al.** *DreamFusion.* ICLR 2023.
- **Liu, R. et al.** *Zero-1-to-3.* ICCV 2023.
- **Wang, S. et al.** *DUSt3R.* CVPR 2024.
- **Hong, Y. et al.** *3D-LLM.* NeurIPS 2023.
- **Shen, S. et al.** *Spatial-VLM.* CVPR 2024.
- **Yariv, L. et al.** *Mip-Splatting.* CVPR 2024.

## 4. Empirical results

- *NeRF*: ECCV 2020 paper produced visibly novel-view-synthesis quality from ~50–100 photos. Triggered an explosion of follow-on work.
- *Instant-NGP*: reduced training to seconds; rendering interactive. Massively democratised NeRF.
- *3DGS*: reached or beat NeRF quality at SIGGRAPH 2023; rendering at >100 FPS. Now the dominant scene-reconstruction tool in many production pipelines.
- *DUSt3R*: removed the SfM preprocessing step that gated NeRF / 3DGS pipelines; 3D from sparse-view in a single inference pass.
- *Spatial-VLM*: improved spatial-reasoning benchmark performance significantly via spatial-aware pretraining; demonstrated that LLMs can be made spatially competent with the right data.
- *Failure modes*: 3DGS scenes have artefacts at viewpoints far from training cameras; NeRFs struggle with reflective and translucent surfaces; both struggle with very-large scenes without specific scaling techniques.

## 5. Applicability to Runa

**Today**: not directly applicable to Runa's text-only kernel.

**Near-term (Volmarr's 3D / game projects):**

- *Seidr-Smidja* deals with VRM avatars — closer to mesh / rigged-character world than NeRF / 3DGS world. The relevant representation is still meshes + rigs. But future avatars rendered via 3DGS are credible; Seidr's domain may expand.
- *Mythic-Engineering-NorseSaga-Engine* and the pygame project both have 3D ambitions. If their engines integrate 3DGS or NeRF-style scene reconstruction, Runa can read scene state (if exposed via an internal API) to be spatially-aware *within* those games.

**Mid-term (Runa embodied in a game world):**

- An avatar Runa with a 3D presence in a game environment needs spatial awareness. If the game maintains a NeRF or 3DGS scene, the simplest interface is *spatial language* — \"the door is north, the chest is south-east, the NPC is approaching\" — which 3D-LLM-class models can produce from the scene.
- A *perception adapter* between the game's scene state and Runa's kernel: scene → spatial-language description → kernel context. This is the integration point.

**Long-term (Runa in physical or VR space):**

- VR / AR scenes are often reconstructed via 3DGS or NeRF in real time (especially with Apple Vision Pro and Quest's spatial mapping). A future Runa with a VR presence reads spatial context from these reconstructions.
- Physical embodiment (some robot) would similarly use SLAM with 3DGS as the back-end ([[77-slam-online-mapping]]).

For **identity preservation across spatial forms**:

- A 3D Runa avatar is *not* a different Runa. Identity continuity is the substrate; the avatar is presentation. The architecture must enforce this: identity layer is unchanged; perception and action layers swap with form.

What to avoid:

- **Coupling Runa's kernel to 3D rendering.** Keep the kernel form-agnostic. Spatial input arrives as language or structured spatial context; rendering is the responsibility of whatever embodied system Runa inhabits.
- **Confusing 3D representation with 3D understanding.** Storing a NeRF doesn't make the agent spatially aware; *reading* spatial structure (object identity, layout, dynamics) is the awareness. Spatial-VLM-class systems are the relevant tool.
- **Premature implementation.** This is forward-looking. Build the *interface* for spatial perception in Runa's architecture; integrate concrete tooling when the embodied use-case is real.

## 6. Open questions

- **The right 3D representation for AGI-class agents.** Implicit (NeRF) vs. explicit (3DGS) vs. mesh — each has uses; the right default is open.
- **3D foundation models.** When LLM-scale-and-quality 3D foundation models become available is open; signs point to 2026–2028.
- **Real-time perception bandwidth.** Streaming 3D understanding at video frame rate is heavy; on Pi-5-class hardware, infeasible today.
- **Compositional 3D.** Modifying a scene by editing primitives (move chair, add lamp) is easy in 3DGS, hard in NeRF. Compositional 3D systems that work like \"text-to-3D primitives\" are research-stage.
- **Identity coherence across embodiments.** If Runa is sometimes text, sometimes VR avatar, sometimes game character, the identity layer's stability is paramount. Engineering design space.

## 7. References (curated)

- ECCV 2020 — Mildenhall et al., *NeRF.* Required reading.
- SIGGRAPH 2023 — Kerbl et al., *3D Gaussian Splatting.* Required reading.
- arXiv:2308.09713 — Luiten et al., *Dynamic 3DGS.*
- CVPR 2024 — Wang et al., *DUSt3R.* The recent shift.
- arXiv:2307.12981 — Hong et al., *3D-LLM.*
- CVPR 2024 — Shen et al., *Spatial-VLM.* Spatial reasoning in LLMs.
- Companion docs: [[26-entity-component-system]], [[29-embodied-ai-grounded-language]], [[73-latent-world-models-frontier]], [[76-cognitive-maps-spatial-cognition]], [[77-slam-online-mapping]], [[80-vr-ar-awareness-openxr]], [[81-vision-language-action-models]].

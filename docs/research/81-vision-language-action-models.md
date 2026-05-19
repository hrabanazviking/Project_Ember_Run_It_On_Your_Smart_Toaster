# 81 — Vision-Language-Action Models: RT-2, OpenVLA, π₀, Helix

**Category:** World Modeling & 3D/Spatial Awareness
**Runa relevance:** future embodied action, integration with game-world / VR / physical control, multimodal kernel evolution
**Status:** Frontier embodied-AI synthesis. Most consequential robotics + AGI convergence.
**Last touched:** 2026-05-17

---

## 1. Core idea

Vision-Language-Action (VLA) models are large multimodal models trained to map *image observations + language instructions → robot actions*. Initiated by Google DeepMind's *RT-1* (2022) and *RT-2* (2023), and accelerated by *OpenVLA* (Stanford 2024), *π₀* (Physical Intelligence 2024), *Octo*, *RDT-1B*, and *Helix* (Figure AI 2024), VLA models represent the most direct convergence of LLM-style reasoning with embodied physical action. The architecture is striking in its simplicity: take a pretrained VLM, fine-tune on robot demonstration data, and the model now produces *executable actions* alongside language.

For Runa, VLA models matter as the eventual *bridge* between her language-shaped cognition and any embodied action — game-world avatar control, VR presence animation, or physical robotic embodiment. The architecture also illuminates an architectural choice for Runa today: the same models that produce robotic actions can produce *gestures*, *expressions*, *animation control* — anything where structured output is needed alongside language.

## 2. Technical depth

**The basic VLA recipe (RT-2-style).**

1. Start with a pretrained Vision-Language Model (PaLI, PaLM-E, Llava, Qwen-VL, Idefics).
2. *Tokenise actions*: each robot-action dimension (joint angle, gripper open/close, etc.) is discretised into bins; each bin is assigned a token in the model's vocabulary.
3. Fine-tune on (image, instruction, action) tuples. The model learns to emit action tokens following the instruction.
4. At deployment: VLM reads image + instruction; outputs action tokens; tokens are decoded back to robot-action values; robot executes.

Crucially: the model's *world knowledge* from VLM pretraining transfers. A robot trained on \"pick up cans\" generalises to \"pick up an apple\" because the VLM knows what apples are.

**RT-1 (Brohan et al. 2022).** First serious large-scale VLA: 35M parameter transformer trained on 130k demonstrations across 13 robots and 700+ tasks. Demonstrated robust task generalisation and modest cross-task transfer.

**RT-2 (Brohan et al. 2023).** Same approach with a 55B-parameter VLM backbone. *Closed-loop deployment*: image → instruction → action emitted at 5+ Hz. Demonstrated unprecedented behavioural generalisation: novel objects, novel locations, novel task descriptions. The crucial result: scale + VLM-pretraining transfers world knowledge to physical control.

**RT-X / Open X-Embodiment (2023).** Crowdsourced consortium effort: collected demonstration data across 20+ robot platforms; trained models that transfer across embodiments. Foundation-model approach to robotics.

**OpenVLA (Kim et al. 2024, Stanford).** Open-weights 7B-parameter VLA built on Prismatic VLMs + LLaMA-2-7B. Trained on Open X-Embodiment data. Comparable to RT-2-X on benchmarks; fully open. The deployability landmark.

**π₀ (Physical Intelligence 2024).** A *single* generalist VLA trained on diverse robot data, deployable across many embodiments. Demonstrated *cross-embodiment* zero-shot capability — train on one robot type, deploy on another with minor fine-tuning. The architecture: flow-matching for action prediction (smoother than discrete-token outputs).

**Helix (Figure AI 2024).** Two-system architecture for humanoid control:
- *System 1*: fast (200 Hz) reactive control. A small transformer reading recent observations and producing motor commands.
- *System 2*: slower (~7 Hz) deliberative reasoning. A 7B VLM reasoning about the task and emitting *latent vectors* that condition System 1.

This *dual-process* architecture — System 1 fast and reactive, System 2 slow and deliberative — directly mirrors Kahneman's dual-process theory ([[86-dual-process-cognition-system-1-2]]) and is the most architecturally interesting recent VLA development.

**The flow-matching shift.** Recent VLAs (π₀, others) shift from discrete-token action outputs to *continuous* action via flow-matching or diffusion. This produces smoother trajectories and avoids the quantisation artefacts of discrete tokens.

**What VLAs do well.**

- Object generalisation: recognise objects from VLM pretraining; reach for them appropriately.
- Instruction-following: \"put the orange in the bowl\" — works.
- Modest cross-task transfer.
- Zero-shot novel objects (within distribution of pretraining).

**What VLAs do poorly (today).**

- Precision tasks needing sub-millimeter accuracy.
- Dynamic obstacles, fast-moving scenes.
- Multi-step planning requiring symbolic reasoning (VLA does end-to-end mapping, not chained reasoning).
- Long-horizon tasks (~minutes).
- Cross-embodiment transfer without retraining.

**Hybrid architectures.** The interesting direction is *VLA + symbolic / hierarchical reasoning*. A high-level planner (LLM with tools) decomposes a task into subtasks; the VLA executes each subtask. Helix's two-system architecture is the deployed version of this idea.

## 3. Key works

- **Brohan, A. et al. (Google).** *RT-1: Robotics Transformer.* arXiv:2212.06817, 2022.
- **Brohan, A. et al. (Google).** *RT-2: Vision-Language-Action Models Transfer Web Knowledge to Robotic Control.* arXiv:2307.15818, 2023.
- **Padalkar, A. et al. (Open X-Embodiment Collaboration).** *Open X-Embodiment: Robotic Learning Datasets and RT-X Models.* arXiv:2310.08864, 2023.
- **Kim, M. J. et al. (Stanford).** *OpenVLA: An Open-Source Vision-Language-Action Model.* arXiv:2406.09246, 2024.
- **Physical Intelligence.** *π₀: A Vision-Language-Action Flow Model for General Robot Control.* 2024.
- **Figure AI.** *Helix: A Vision-Language-Action Model for Generalist Humanoid Control.* 2024-2025 blog + paper.
- **Liu, S. et al.** *RDT-1B.* arXiv:2410.07864, 2024.
- **Octo Model Team.** *Octo: An Open-Source Generalist Robot Policy.* arXiv:2405.12213, 2024.
- **Driess, D. et al.** *PaLM-E: An Embodied Multimodal Language Model.* arXiv:2303.03378, 2023.
- **Brohan, A. et al.** *SayCan: Do As I Can, Not As I Say.* CoRL 2022. Predecessor pattern.
- **Stone, A. et al.** *Open-World Object Manipulation Using Pre-trained Vision-Language Models* (Mosaic). CoRL 2023.

## 4. Empirical results

- *RT-2*: ~3× improvement over RT-1 on symbolic-reasoning and novel-object generalisation benchmarks.
- *Open X-Embodiment*: cross-embodiment training improves performance on individual platforms 2–3×, suggesting useful transfer.
- *OpenVLA*: ~99% reproduction of RT-2 performance with open weights and smaller scale.
- *π₀*: zero-shot deployment across multiple robot types with measurable competence.
- *Helix*: real-time humanoid manipulation with explicit fast/slow split; production demonstrations of household tasks.
- *Failure modes*: precision, dynamic environments, long horizon, novel embodiments.

## 5. Applicability to Runa

**Today**: not directly applicable. Runa has no actuated body.

**Near-term (game / VR avatar control)**:

- A VLA-style architecture is the natural choice for *avatar control* in game / VR. The same model architecture that controls a robot can control a VRM avatar — pose, gesture, expression — given a language description of intended action.
- Specifically: Runa's kernel emits a high-level action description (\"reach toward Volmarr with a welcoming gesture\"); a VLA-style adapter translates to avatar control (joint angles, expression weights, gaze direction).
- This is *not* OpenVLA out-of-the-box; it's a domain-specific small model trained on (state, instruction, avatar-control) tuples. The architectural pattern transfers; the specific weights are bespoke.

**Mid-term (full embodiment)**:

- If Runa ever has a robotic body, a VLA model handles low-level control. Helix's two-system architecture is the architectural reference: Runa's kernel = System 2 (deliberative); a small fast VLA = System 1 (reactive).

For **Runa's kernel architecture (conceptual)**:

- Even without VLA, the *separation* of deliberative reasoning (kernel) from reactive response (a hypothetical avatar / world-action module) is good architecture. The kernel reasons in language; the world-action module executes. Each scales independently.

For **multimodal kernel evolution**:

- A future Runa kernel may itself be multimodal — directly consuming images, video, audio, with structured output for action. VLA architectures are the production-validated path.
- For Runa on a Pi-class device, multimodal kernel is a 2026–2028 affordability question.

What to avoid:

- **Deploying RT-2-class VLAs for non-embodied Runa.** No relevant action surface; overhead without benefit.
- **Coupling Runa's identity to a specific embodied form.** The PHILOSOPHY makes identity substrate-independent.
- **Replacing language reasoning with VLA action outputs prematurely.** VLA is good for *bridging* language → action, not for replacing the reasoning that produces the language.
- **Underestimating the engineering distance.** Plugging an OpenVLA into a game avatar is months of work even with all components available.

## 6. Open questions

- **Open-weights VLA models for avatars and VR.** Robotics-trained VLAs may not transfer cleanly to avatar control; specific training likely needed.
- **The right action representation for avatars.** Joint angles? Pose primitives? Animation-graph commands? Open.
- **Multimodal Runa.** When base LLMs become multimodal-capable on Pi-class hardware, Runa's kernel can read images directly. The architectural opportunity is large.
- **Two-system architecture for non-embodied agents.** Helix's split is a robotics pattern; whether \"fast reactive + slow deliberative\" applies to conversational Runa is an interesting design question.
- **VLA model availability on edge devices.** Pi-class deployment of VLA models is research-stage; trends suggest 2027+.

## 7. References (curated)

- arXiv:2307.15818 — Brohan et al., *RT-2.* The breakthrough paper.
- arXiv:2406.09246 — Kim et al., *OpenVLA.* The open-weights reference.
- Physical Intelligence, *π₀* (2024). The generalist VLA paper.
- Figure AI, *Helix* (2024). The two-system architecture.
- arXiv:2310.08864 — Open X-Embodiment paper. The cross-embodiment dataset.
- arXiv:2303.03378 — Driess et al., *PaLM-E.* The embodied-LLM precedent.
- Companion docs: [[29-embodied-ai-grounded-language]], [[73-latent-world-models-frontier]], [[74-3d-scene-representation]], [[79-video-games-agi-testbeds]], [[80-vr-ar-awareness-openxr]], [[86-dual-process-cognition-system-1-2]], [[99-multimodal-foundation-embodied]].

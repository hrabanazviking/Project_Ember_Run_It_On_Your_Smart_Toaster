# 77 — SLAM, Online Mapping, and Place Recognition for Embodied Agents

**Category:** World Modeling & 3D/Spatial Awareness
**Runa relevance:** forward-looking embodiment (game-world, VR, physical), continuous spatial awareness
**Status:** Robotics / vision synthesis. Foundational for any moving embodied agent.
**Last touched:** 2026-05-17

---

## 1. Core idea

SLAM (Simultaneous Localisation And Mapping) is the canonical problem of robotics: given a moving sensor (camera, LiDAR, IMU), simultaneously *figure out where you are* and *build a map of where you've been*. The problem is chicken-and-egg — localising requires a map, mapping requires localisation — and decades of research have produced robust solutions for many sensor modalities. *Place recognition* is the related ability to recognise *I've been here before* from sensory data, enabling loop closure (correcting drift when revisiting) and long-horizon mapping.

For Runa, SLAM is not a current need — she does not move. For a future Runa with a presence in a 3D game world, a VR environment, or eventually a robotic body, SLAM is the foundation of continuous spatial awareness. The state of the art has shifted significantly: classical feature-based SLAM (ORB-SLAM family) is being augmented or replaced by learned components, NeRF-based and Gaussian-Splatting-based SLAM are emerging, and semantic SLAM (recognising *what* not just *where*) is reaching production.

## 2. Technical depth

**The SLAM problem formally.**

Given:
- A sequence of sensor observations $z_{1:t}$.
- Control inputs (where applicable) $u_{1:t}$.

Estimate:
- The trajectory $x_{1:t}$ (pose over time).
- The map $m$ of the environment.

The optimal estimate is a posterior $p(x_{1:t}, m \mid z_{1:t}, u_{1:t})$. Classical SLAM treats this as a graph optimisation: pose nodes connected by motion edges and observation edges; minimise total error.

**Sensor modalities.**

- *Visual SLAM*: single camera. Cheap, ubiquitous, depth-ambiguous.
- *Stereo / depth SLAM*: depth sensor or stereo cameras. Better-grounded depth.
- *Visual-inertial SLAM (VI-SLAM)*: camera + IMU. State-of-the-art for many platforms.
- *LiDAR SLAM*: range sensor. Accurate but expensive.
- *Multi-sensor fusion*: combinations.

**Major SLAM families.**

- *Feature-based*: detect keypoints, match across frames, estimate motion. ORB-SLAM2/3 (Mur-Artal et al.), the classical reference. Robust, well-understood.
- *Direct methods*: use pixel intensities directly. LSD-SLAM (Engel et al.), DSO. Higher detail; more demanding.
- *Filter-based*: extended Kalman filter or particle filter. Older; some niche use.
- *Graph-based*: pose graph + nonlinear optimisation. g2o, GTSAM. Modern default for offline / large-scale.
- *Learned SLAM*: CNNs / transformers as front-ends or full pipelines. DROID-SLAM (Teed & Deng 2021), DeepFactors. Strong on textureless, low-light scenes.

**Neural and Gaussian SLAM (the frontier).**

- *iMAP* (Sucar et al. 2021): the scene representation IS a NeRF-style MLP; mapping = training the MLP, localising = inferring poses against the MLP. Slow but conceptually clean.
- *NICE-SLAM* (Zhu et al. 2022): hierarchical scene grids speed up iMAP.
- *Vox-Fusion*, *Point-SLAM*: explicit voxel / point primitives with neural decoders.
- *Gaussian-Splatting SLAM* (Matsuki et al. 2024, Keetha et al. 2023): the scene representation is 3DGS, optimised online from video. Real-time mapping at high visual fidelity.
- *SplaTAM*, *MonoGS*, *GS-SLAM*: variants and refinements.

The shift: SLAM's map is no longer a sparse point cloud or geometric voxels; it's a *renderable* scene that supports novel views. This makes the map *richer* and *more useful* for downstream agents — they can ask not just \"is there a wall here?\" but \"what does it look like from here?\"

**Place recognition.**

- *Bag-of-Visual-Words* (Sivic & Zisserman 2003): represent each image as a histogram of visual-feature codewords. Match by histogram similarity. Foundational.
- *NetVLAD* (Arandjelović et al. 2016): learned aggregation of features into a place descriptor. Robust to viewpoint and lighting.
- *AnyLoc* (Keetha et al. 2024): foundation-model features for place recognition. Strong zero-shot performance.
- *VPR-class systems*: visual place recognition; deployed in autonomous driving and AR.

**Semantic SLAM.** Beyond \"where\" — *what*:

- Co-occur object detection / segmentation with SLAM.
- Map nodes carry semantic labels: chair, door, sky, person.
- Enables queries like \"go to the kitchen\" rather than coordinate-only navigation.
- Active research, increasingly deployable. Critical for agent-level reasoning.

**SLAM in game and VR contexts.**

- VR headsets (Quest, Vision Pro) use inside-out tracking that is essentially VI-SLAM. The map persists; relocalisation lets the headset know it's been in this room before.
- Game engines with avatar-controlled NPCs typically have *direct access* to scene state (no SLAM needed — they're inside the system). Mapping is only relevant if Runa is *external* to the engine and observing via a video feed.
- For embodied Runa-in-game, the cleanest path is the engine exposing scene state via API; SLAM is for the harder cases (recorded gameplay, no API access, physical-world deployment).

## 3. Key works

- **Mur-Artal, R., Tardós, J. D.** *ORB-SLAM2: An Open-Source SLAM System for Monocular, Stereo, and RGB-D Cameras.* IEEE Transactions on Robotics, 2017.
- **Campos, C. et al.** *ORB-SLAM3.* IEEE Transactions on Robotics, 2021.
- **Engel, J. et al.** *LSD-SLAM.* ECCV 2014.
- **Teed, Z., Deng, J.** *DROID-SLAM.* NeurIPS 2021.
- **Sucar, E. et al.** *iMAP: Implicit Mapping and Positioning in Real-Time.* ICCV 2021.
- **Zhu, Z. et al.** *NICE-SLAM.* CVPR 2022.
- **Keetha, N. et al.** *SplaTAM: Splat, Track & Map 3D Gaussians for Dense RGB-D SLAM.* arXiv:2312.02126, 2023.
- **Matsuki, H., Murai, R., Kelly, P. H. J., Davison, A. J.** *Gaussian Splatting SLAM.* CVPR 2024.
- **Arandjelović, R. et al.** *NetVLAD.* CVPR 2016.
- **Keetha, N. et al.** *AnyLoc: Towards Universal Visual Place Recognition.* arXiv:2308.00688, 2023.
- **McCormac, J. et al.** *SemanticFusion.* ICRA 2017. Early semantic SLAM.
- **Mildenhall, B. et al.** *NeRF.* See [[74-3d-scene-representation]].

## 4. Empirical results

- *ORB-SLAM3*: deployed in industry. Robust on most indoor / outdoor benchmarks. Failure mode: textureless scenes.
- *DROID-SLAM*: substantial improvement on TartanAir, EuRoC; strong robustness to low-texture environments.
- *iMAP / NICE-SLAM*: fewer benchmark wins, more conceptual demonstrations; slower than classical SLAM.
- *Gaussian SLAM (SplaTAM, MonoGS)*: matches or exceeds classical SLAM on rendering quality; tracking accuracy approaches state of the art; real-time on consumer GPUs.
- *Place recognition*: NetVLAD pushed recognition rates over 90% on Pittsburgh / Tokyo24/7 benchmarks; AnyLoc generalises to zero-shot domains.
- *Semantic SLAM*: deployed in autonomous driving (lane / object semantic mapping). Increasingly in AR.
- *Failure modes documented*: long-corridor drift (no loop closure opportunity), dynamic scenes (people, vehicles), illumination changes, GPS-denied environments needing place recognition.

## 5. Applicability to Runa

**Today**: not directly applicable.

**Near-term — game-world embodiment**:

- If Runa has an avatar in a Volmarr-built game world (Mythic-Engineering-NorseSaga-Engine, pygame Viking Edition), the cleanest interface is *engine-exposed scene state*. Runa subscribes; she doesn't run SLAM.
- A *spatial subagent* in Hirð maintains an internal representation of the environment from this stream. The representation is cognitive-map-like ([[76-cognitive-maps-spatial-cognition]]) — a graph of locations, objects, paths.

**Mid-term — VR / AR embodiment**:

- VR systems provide tracking as a service. The headset's SLAM gives pose; the application gets scene-mapped data. Runa-in-VR consumes this.

**Long-term — physical embodiment**:

- A robotic Runa needs full SLAM. The choice (visual vs. visual-inertial vs. LiDAR; classical vs. learned vs. neural) depends on form factor. By the time this is real, the field will have moved further; design for *interchangeable SLAM back-end*.

For **the spatial subagent architecture**:

```
                  ┌──────────────────────┐
                  │ ENVIRONMENT          │
                  │  (game engine /       │
                  │   VR system /         │
                  │   robotic platform)   │
                  └──────────┬───────────┘
                             │ pose + sensor + scene
                             ▼
                  ┌──────────────────────┐
                  │ SLAM / SPATIAL BACKEND│
                  │ (engine API or         │
                  │  SLAM module)         │
                  └──────────┬───────────┘
                             │ canonical spatial state
                             ▼
                  ┌──────────────────────┐
                  │ SPATIAL SUBAGENT     │
                  │ (cognitive map +     │
                  │  place recognition + │
                  │  trajectory)          │
                  └──────────┬───────────┘
                             │ spatial-language summary
                             ▼
                  ┌──────────────────────┐
                  │ KERNEL                │
                  └──────────────────────┘
```

The interface is clean: kernel never touches raw sensors; spatial subagent never touches LLM.

For **place recognition**:

- For long-running embodied Runa, place recognition supports *episode-place linking*: \"the last time I was here, X happened.\" This connects Muninn's episodic store to spatial context.
- Implementation: each significant location gets a learned descriptor; episodes are tagged with location IDs; retrieval can query by location.

For **safety and reliability**:

- SLAM failures (lost localisation, mis-loop-closure) must not crash Runa. Spatial subagent has *degraded modes*: low-confidence, lost, recovered.
- Identity is unaffected by spatial degradation. \"I'm not sure where I am\" is a behaviour, not an identity crisis.

What to avoid:

- **Coupling kernel to SLAM internals.** Keep the spatial subagent as the only consumer of low-level spatial data.
- **Implementing SLAM today.** Forward-looking. Time invested before embodiment exists is wasted.
- **Treating SLAM map as ground truth.** It is an estimate. Confidence and uncertainty must propagate.
- **Conflating spatial and conceptual maps.** Cognitive maps support both ([[76-cognitive-maps-spatial-cognition]]); the *implementations* differ.

## 6. Open questions

- **Neural-SLAM convergence with classical.** The fields are blending; the right hybrid is unsettled.
- **SLAM for long-lived agents.** Most SLAM is session-bounded. Cross-session map persistence for an agent that comes and goes is open.
- **Dynamic-scene SLAM.** Moving objects (people, NPCs) remain hard. Active research.
- **Multi-agent SLAM.** Multiple agents sharing a map is a research topic with applications.
- **SLAM under model upgrade.** If a SLAM back-end is replaced, the existing map must be carried forward. Versioning of spatial state alongside identity versioning ([[62-identity-stability-under-change]]) is an open architectural problem.

## 7. References (curated)

- ORB-SLAM3 (Campos et al. 2021) — the modern classical reference.
- DROID-SLAM (Teed & Deng 2021) — learned modern reference.
- Matsuki et al. (2024) — *Gaussian Splatting SLAM.* Frontier.
- NetVLAD (Arandjelović 2016) — place recognition foundation.
- AnyLoc (Keetha 2024) — foundation-model VPR.
- Companion docs: [[74-3d-scene-representation]], [[76-cognitive-maps-spatial-cognition]], [[80-vr-ar-awareness-openxr]].

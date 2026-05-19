# 82 — Object-Centric and Slot-Based Representation Learning

**Category:** World Modeling & 3D/Spatial Awareness
**Runa relevance:** perception adapters, world-model integration, semantic-graph extraction from scenes
**Status:** Frontier vision / world-modelling synthesis. Foundational for compositional reasoning.
**Last touched:** 2026-05-17

---

## 1. Core idea

Most vision systems represent a scene as a *grid of features* — a tensor of activations indexed by pixel location. *Object-centric* representations instead represent a scene as a *set of object slots*, each capturing one entity. This shift from spatial to compositional representation has substantial downstream consequences: scenes can be modified by editing slots, dynamics can be predicted per-object, language can refer to specific objects, and reasoning can be done over a small structured set rather than a million pixels.

The most influential object-centric model is *Slot Attention* (Locatello et al. 2020). The pattern has spread: object-centric video models (SAVi, STEVE), object-centric VLMs (LocCa, ObjectCLIP-adjacent), object-centric world models (G-SWM, OP3). For Runa, object-centric thinking is the *bridge* between her language-shaped reasoning and any 3D / visual / game / VR perception. The episode \"the cat jumped onto the table\" is object-centric; a pixel grid can't be reasoned about that way without first extracting objects. Object-centric perception is therefore the canonical *perception-to-reasoning* adapter.

## 2. Technical depth

**Slot Attention (Locatello, Weissenborn, Eichenberger, Greff, Heigold, Jaitly, Kipf, Houlsby, Zaheer 2020).**

Architecture:
- Input: feature map from a CNN encoder of an image, $h \in \mathbb{R}^{H \times W \times d}$.
- $K$ *slots* initialised from a Gaussian: $s \in \mathbb{R}^{K \times d_s}$.
- Iterated *attention*: each slot attends to features, gathers them, and updates. Slots compete (softmax over slots, not over keys) so each pixel is bound to one slot.

```
for iter in iterations:
    keys, values  ← linear(h)
    queries       ← linear(s)
    attention     ← softmax(queries · keysᵀ / √d, dim=slots)
    weighted_avg  ← attention · values
    s             ← GRU(s, weighted_avg)
```

After iteration: $K$ slots, each capturing one object's features. Loss: reconstruct image from slots (autoencoder-style). The model learns *unsupervised object segmentation*.

**Strengths**: works on synthetic and moderately realistic scenes; produces clean object decompositions when objects are visually distinct.

**Weaknesses**: struggles on cluttered or texture-rich natural images; sensitive to $K$ (slot count) choice; ambiguous on partial-occlusion.

**Object-centric video.**

- *SAVi* (Kipf et al. 2022): Slot Attention extended to video. Slots persist across time, capturing object trajectories.
- *STEVE* (Singh et al. 2022): better object discovery; supports complex naturalistic videos.
- *SAVi++*: scaling to real video with self-supervised training.

**Object-centric world models.**

- *G-SWM* (Lin et al. 2020): generative model of scene dynamics, structured by objects.
- *OP3* (Veerapaneni et al. 2020): object-centric MDP for planning.

**Object-centric foundation models.**

- *Stable diffusion* and other image models already have implicit object structure in their attention layers (Mocanu & Hospedales 2023). Probing finds them.
- *Locca* and similar: VLMs with explicit per-object attention.
- *Tokenized object representations* (DALL-E-3's discrete-VAE codes; some SD variants): each token can be made to correspond to an object-region, supporting object-level editing.

**Object-centric LLM agents.**

When an LLM consumes a scene description, it's far more useful to receive a *list of objects with attributes and relations* than a paragraph of pixel description. The structured form:

```yaml
scene:
  - object: cat
    attributes: {colour: black, posture: sitting}
    location: on_top_of(table)
  - object: table
    attributes: {colour: brown, material: wood}
    location: in(room)
  - object: cup
    attributes: {colour: white, contents: empty}
    location: on_top_of(table)
```

is a *queryable*, *editable*, *reasoning-friendly* representation. The LLM can answer \"is the cup near the cat?\" by inference over the structure.

**Object-centric SLAM and 3D.** Extends to 3D:

- *Object SLAM* augments classical SLAM with object detection; each object becomes a node in the map.
- *3DGS with object segmentation* labels Gaussian splats by object identity.
- *Vision-language 3D* (3D-LLM, Spatial-VLM) takes object-segmented 3D as input.

For embodied agents, object-centric 3D maps make navigation and interaction tractable in ways pixel-grid maps do not.

## 3. Key works

- **Locatello, F. et al.** *Object-Centric Learning with Slot Attention.* NeurIPS 2020.
- **Kipf, T. et al.** *Conditional Object-Centric Learning from Video* (SAVi). ICLR 2022.
- **Singh, G. et al.** *Slate Sticky Slot Attention* (STEVE). NeurIPS 2022.
- **Lin, Z. et al.** *G-SWM: Object-Centric Generative World Models.* arXiv:2010.06065, 2020.
- **Veerapaneni, R. et al.** *Entity Abstraction in Visual Model-Based Reinforcement Learning* (OP3). CoRL 2020.
- **Greff, K. et al.** *On the Binding Problem in Artificial Neural Networks.* arXiv:2012.05208, 2020. Theoretical motivation.
- **Burgess, C. P. et al.** *MONet.* arXiv:1901.11390, 2019.
- **Engelcke, M. et al.** *GENESIS.* arXiv:1907.13052, 2019.
- **Wu, Z. et al.** *Recurrent Independent Mechanisms.* NeurIPS 2021. Adjacent decompositional approach.
- **Spelke, E. S.** *Initial knowledge: Six suggestions.* Cognition, 1994. Cognitive-science foundation: objecthood as core knowledge.

## 4. Empirical results

- *Slot Attention*: clean object discovery on synthetic / Tetrominoes / Multi-dSprites datasets without supervision. Robust.
- *SAVi*: object tracking through video with minimal supervision; identity preservation across occlusion.
- *STEVE* and successors: extended to more naturalistic video; quality improves as dataset realism increases.
- *Object-centric VQA*: scenes pre-segmented into objects + LLM reasoning outperforms raw-image VQA on compositional questions.
- *Failure modes*: heavy clutter, transparent objects, fluid / deformable objects, large variation in object size, fine-grained sub-object structure.
- *Real-world transfer*: object-centric models historically struggled on natural images; recent work bridges the gap.

## 5. Applicability to Runa

For **perception adapters (forward-looking)**:

- Any perception input to Runa (image, video, 3D scene) should be *object-centric* before reaching the kernel. The kernel reasons about objects and relations; raw pixels are useless to it.
- A *perception adapter* in Hirð (or as a kernel preprocessing layer): vision input → object-centric structured scene → kernel context.
- Format: structured (YAML, JSON) lists of objects with attributes, positions, relations.

For **integration with semantic graphs**:

- Object-centric scene descriptions feed Muninn's semantic graph ([[56-neuro-symbolic-memory-graphs]]) naturally. Each detected object is a node (entity); each spatial relation is a triplet.
- A scene observed becomes a small subgraph; subsequent observations of the same scene extend / update it.
- This is the bridge between perception and persistent memory.

For **game-world / VR / future embodiment**:

- Game engines already have object structure (entities, components). The object-centric perception challenge dissolves for white-box environments — Runa can read the engine's entity list directly.
- For black-box environments (screen feeds), Slot Attention or successors provide the object-extraction step. Cradle-style ([[79-video-games-agi-testbeds]]) agents use coarser methods; finer object-centric methods would be a quality improvement.

For **Saga and narrative**:

- Saga writes about objects, persons, events — entities Runa cares about. Object-centric perception ensures Saga has *named* entities to write about, not pixel descriptions.

For **the long-term world-model architecture**:

- Object-centric world models are a credible foundation for a Runa world-model that's both *compositional* (can imagine novel scenes) and *queryable* (supports symbolic reasoning).
- The TEM-class research ([[76-cognitive-maps-spatial-cognition]]) suggests the brain also operates on object-centric / relational structures. Convergent evidence the architecture is right.

What to avoid:

- **Premature implementation.** Without perceptual input streams in Runa's current scope, object-centric machinery is overhead. Plan the interface; implement when perception lands.
- **Forcing slot counts.** Different scenes have different object counts; fixed-$K$ Slot Attention is limiting. Use variable-$K$ variants when implementing.
- **Confusing object detection with object-centric representation.** Detection produces bounding boxes; object-centric produces slot features that carry attribute, relation, dynamics. Different.
- **Throwing away the kernel's language reasoning.** Object-centric perception *feeds* language reasoning; it doesn't replace it.

## 6. Open questions

- **Real-world object-centric pretraining.** Scaling Slot Attention to large natural-image / video datasets is open; recent work is encouraging.
- **Object identity over long horizons.** Maintaining slot-identity across long video / many scenes is hard.
- **Compositional object generation.** Editing object slots to modify scenes works in synthetic; in real images, harder.
- **The right number of slots.** Adaptive-K variants exist; the right schedule is open.
- **Object-centric LLM training.** Pretraining LLMs on object-centric structured data rather than raw pixel descriptions could substantially improve compositional reasoning. Active research.

## 7. References (curated)

- NeurIPS 2020 — Locatello et al., *Slot Attention.* Required.
- ICLR 2022 — Kipf et al., *SAVi.* Object-centric video.
- arXiv:2012.05208 — Greff et al., *The Binding Problem.* Theoretical anchor.
- Spelke (1994), *Cognition.* Why objecthood is a core knowledge.
- arXiv:2010.06065 — Lin et al., *G-SWM.* Object-centric world model.
- Companion docs: [[06-knowledge-graphs-ai-memory]], [[26-entity-component-system]], [[56-neuro-symbolic-memory-graphs]], [[73-latent-world-models-frontier]], [[74-3d-scene-representation]], [[76-cognitive-maps-spatial-cognition]].

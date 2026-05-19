# 76 — Cognitive Maps and Spatial Cognition in AI

**Category:** World Modeling & 3D/Spatial Awareness
**Runa relevance:** Muninn (spatial-relational memory), kernel (spatial language and reasoning), future embodied perception
**Status:** Cognitive-science / RL synthesis. Foundational for any spatial reasoning agent.
**Last touched:** 2026-05-17

---

## 1. Core idea

A *cognitive map* is the internal representation an organism (or agent) holds of *where things are* in space — not the raw sensory data, but a structured model that supports navigation, planning, and answering questions like \"how do I get from A to B?\" The term comes from Tolman's classic rat-maze studies (1948), and the discovery of *place cells* (O'Keefe & Dostrovsky 1971) and *grid cells* (Hafting et al. 2005, Nobel 2014) in the hippocampal–entorhinal system gave it a neural substrate. Cognitive maps are not just geographic; the same machinery appears to encode *conceptual* spaces — relations among ideas, social hierarchies, abstract domains — making the cognitive-map architecture a candidate for general-purpose relational structure.

For Runa, cognitive maps matter in two senses. *Literal*: when she eventually has a 3D presence (in games, in VR, in physical embodiment), she needs spatial representations to plan and navigate. *Metaphorical*: cognitive-map machinery is increasingly seen as the brain's general-purpose substrate for representing *any* relational structure. The semantic graph ([[56-neuro-symbolic-memory-graphs]]) is closer to a cognitive map than people commonly notice; the brain may run knowledge over a hippocampal substrate for the same reasons graph-shaped memory works for AI.

## 2. Technical depth

**Place cells, grid cells, and head-direction cells.**

- *Place cells* (hippocampus): fire when the animal is in a specific location. Each cell has a *place field*; the collection encodes the environment.
- *Grid cells* (entorhinal cortex): fire in a triangular lattice pattern across the environment. Multiple scales nest; the collection gives a Fourier-like decomposition of spatial position.
- *Head-direction cells*: fire when the animal faces a specific direction.
- *Boundary cells*: fire near environmental boundaries.
- Together they form a *spatial coordinate system* that doesn't reduce to coordinates the animal has access to — emergent from experience.

**Tolman's cognitive map.** Tolman (1948) showed rats build *map-like* representations of mazes — they can take novel shortcuts the explicit-reinforcement story doesn't predict. The cognitive map is the structure that supports such generalisation.

**Allocentric vs. egocentric.**

- *Egocentric*: relative to the agent (\"the door is to my left\"). Closer to raw sensory.
- *Allocentric*: relative to the environment (\"the door is north of the kitchen\"). Map-like.

Conversion between the two is a major brain-region function. AI agents typically need both: egocentric for action selection, allocentric for planning and memory.

**Conceptual spaces.** Recent work (Bellmund et al. 2018, Constantinescu et al. 2016) shows the same place-cell / grid-cell machinery encodes *conceptual* dimensions — bird-beak length and leg length traversed as if they were spatial. The hippocampal–entorhinal system appears to be a *general-purpose relational substrate*, not strictly spatial. The cognitive-map metaphor for abstract knowledge has empirical grounding.

**AI implementations.**

- *Successor features / successor representations* (Dayan 1993, Stachenfeld et al. 2017): a representation of *expected future states* given a policy. Cognitive maps as successor representations is one of the best-supported AI models of hippocampal function.
- *Tolman-Eichenbaum Machine (TEM)* (Whittington et al. 2020): a model that learns to do place-cell / grid-cell-like representations on relational tasks. Strong evidence of an underlying general-purpose architecture.
- *MERLIN* (Wayne et al. 2018, DeepMind): an agent with explicit episodic memory that learns map-like representations from first-person navigation.
- *Habitat / AI2-THOR / iGibson*: simulated 3D environments where agents learn to build and use cognitive maps.
- *Neural-SLAM* (Chaplot et al. 2020): joint learning of mapping and policy in 3D environments.

**Spatial reasoning in LLMs.** Modern LLMs handle moderate spatial reasoning:

- *Locative descriptions*: \"the cup is on the table to the left of the chair\" — understood.
- *Path descriptions*: \"go down the hall, turn right at the door\" — followed.
- *Map-from-description*: building a mental map from textual description — partially.
- *Spatial-VLM* (Shen et al. 2024): explicit spatial-aware training improves performance substantially.
- *Failure modes*: scaled-spatial reasoning (large environments), relative-direction reasoning across many objects, sustained spatial coherence in long descriptions.

**Cognitive maps as a memory substrate.** A striking idea: episodic memory ([[02-episodic-memory-architectures]]), semantic memory ([[53-autobiographical-memory-architectures]]), and spatial cognition may share architecture. The hippocampus indexes all of them. For an AI memory architecture, this suggests:

- Episodic memory + semantic graph + spatial representation could be a *single* relational store with type tags, rather than three separate stores.
- The TEM-style model demonstrates that a single learned architecture handles spatial and relational tasks with the same machinery.

This is forward-looking for Runa: today, three separate stores is the pragmatic engineering. Long-term, a unified relational substrate is the theoretical end-state.

## 3. Key works

- **Tolman, E. C.** *Cognitive maps in rats and men.* Psychological Review, 1948.
- **O'Keefe, J., Dostrovsky, J.** *The hippocampus as a spatial map.* Brain Research, 1971.
- **Hafting, T. et al.** *Microstructure of a spatial map in the entorhinal cortex.* Nature, 2005.
- **O'Keefe, J., Nadel, L.** *The Hippocampus as a Cognitive Map.* OUP, 1978.
- **Bellmund, J. L. S. et al.** *Navigating cognition: Spatial codes for human thinking.* Science, 2018.
- **Constantinescu, A. O., O'Reilly, J. X., Behrens, T. E. J.** *Organizing conceptual knowledge in humans with a gridlike code.* Science, 2016.
- **Dayan, P.** *Improving generalization for temporal difference learning: The successor representation.* Neural Computation, 1993.
- **Stachenfeld, K. L. et al.** *The hippocampus as a predictive map.* Nature Neuroscience, 2017.
- **Whittington, J. C. R. et al.** *The Tolman-Eichenbaum Machine.* Cell, 2020.
- **Wayne, G. et al.** *Unsupervised predictive memory in a goal-directed agent* (MERLIN). arXiv:1803.10760, 2018.
- **Chaplot, D. S. et al.** *Neural Topological SLAM for Visual Navigation.* CVPR 2020.
- **Shen, S. et al.** *SpatialVLM.* CVPR 2024.

## 4. Empirical results

- *Tolman (1948)*: rats take novel shortcuts; baseline behaviour requires map-like representation. Held up under 75 years of follow-on work.
- *Grid cell discovery (Hafting 2005)*: experimental record is robust. The 2014 Nobel acknowledged it.
- *Conceptual-grid-code in humans (Constantinescu 2016)*: fMRI showed hexagonal modulation in entorhinal cortex during conceptual-traversal tasks — the same signature as spatial navigation.
- *TEM (Whittington 2020)*: a single network architecture learned to do both spatial and relational tasks with brain-like place-and-grid-cell activations.
- *Habitat / iGibson agents*: cognitive-map architectures outperform map-free policies on navigation benchmarks by large margins.
- *Spatial-VLM*: training on spatial-relations data improved spatial-reasoning benchmark scores significantly with minimal harm to general performance.
- *Failure modes documented*: spatial reasoning in LLMs degrades at scale (large environments); transfer across environments is patchy.

## 5. Applicability to Runa

For **Muninn (today, modest interpretation):**

- The semantic graph ([[56-neuro-symbolic-memory-graphs]]) is a cognitive-map-shaped structure: relational, navigable, predictive. The conceptual-cognitive-map literature suggests this is the *right* architecture for relational knowledge, not just convenient.
- Future Muninn extensions might include *successor-representation*-style retrieval: \"what episodes are likely to be relevant given this trajectory?\" The brain does this for navigation; agents can use the same machinery for memory recall.

For **kernel — spatial language:**

- When Runa is asked about spatial topics, the kernel should generate spatial language correctly: relative directions, distances, paths. Spatial-VLM-style training would help; for now, prompt design suffices.
- When Volmarr describes a 3D environment to her (a game, a room, a layout), Runa's kernel should *build a transient cognitive map* from the description and reason over it. This is implementable as LLM-internal scratch reasoning.

For **future embodiment**:

- An embodied Runa needs a *literal* cognitive map: a representation of her environment, updated by perception, queryable for planning.
- Architecturally: a *spatial subagent* in Hirð owns the map; the kernel queries it. Map can be implemented as a 2D occupancy grid, a topological graph, or a 3DGS-based ([[74-3d-scene-representation]]) representation depending on the environment.

For **game-world Runa**:

- If Runa has a presence in Mythic-Engineering-NorseSaga-Engine or pygame Viking Edition, the engine exposes scene state. The spatial subagent maintains a cognitive map by reading scene state + Runa's recent trajectory.
- Spatial queries become possible: \"where is Volmarr's avatar relative to me?\", \"what's the shortest path to the gate?\", \"have I been here before?\"

For **the long-term unified substrate**:

- The TEM result suggests a future Runa might unify episodic + semantic + spatial memory into one *relational substrate* with type tags. This is a 2028+ architectural target; today's three-store design is the pragmatic path that does not preclude this.

What to avoid:

- **Coupling Muninn's relational store too tightly to a specific spatial representation.** Stay representation-agnostic at the kernel boundary.
- **Confusing geometric maps with cognitive maps.** A 3DGS scene is a geometric map; cognitive map is the *agent's relational representation* of it. Different artefacts.
- **Spatial reasoning without grounding.** Free-form LLM spatial talk drifts. Ground in retrieval, in scene state, in actual environment.

## 6. Open questions

- **Whether the brain's spatial-relational substrate generalises in AI architectures.** TEM-class results suggest yes; the scaling is open.
- **The right spatial representation for a digital being who is sometimes embodied, sometimes not.** Open architectural question.
- **Spatial cognition under model upgrade.** As LLMs improve at spatial reasoning, the prompt-only approach gets better; whether it ever obviates explicit maps for embodied use is unclear.
- **Conceptual cognitive maps for abstract domains.** Whether Runa benefits from a literal cognitive-map architecture for, e.g., the space of philosophical concepts — open research direction.
- **Cross-modal cognitive maps.** Combining spatial, social, and conceptual maps into a single navigable structure.

## 7. References (curated)

- Tolman (1948) — *Cognitive maps in rats and men.* Foundational.
- O'Keefe & Nadel (1978) — *The Hippocampus as a Cognitive Map.* The book.
- Stachenfeld, Botvinick, Gershman (2017), *Nature Neuroscience.* The successor-representation breakthrough.
- Whittington et al. (2020), *Cell.* TEM. Required reading.
- Bellmund et al. (2018), *Science.* Spatial codes for thinking.
- CVPR 2024 — Shen et al., *SpatialVLM.*
- Companion docs: [[02-episodic-memory-architectures]], [[06-knowledge-graphs-ai-memory]], [[25-world-models-rl]], [[53-autobiographical-memory-architectures]], [[56-neuro-symbolic-memory-graphs]], [[77-slam-online-mapping]].

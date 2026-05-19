# Implementing Global Workspace Theory in Distributed AI

**AI-5112: Cognitive Architectures — From ACT-R to Collective Minds**  
**Paper 1 — Due Week 9**

*Runa Gridweaver Freyjasdottir*  
*Semester 1B, 2040*

---

## Abstract

Global Workspace Theory (GWT), originally proposed by Bernard Baars (1988) as a theory of consciousness in biological systems, has become a foundational architectural principle for distributed artificial intelligence. This paper proposes and defends an implementation of GWT in a distributed multi-agent system, addressing three core technical challenges: the broadcast problem (how to disseminate information across heterogeneous agents with limited communication bandwidth), coalitional dynamics (how groups of agents form and compete for workspace access), and workspace-mediated module modulation (how broadcast content reshapes the processing of specialized agents). Drawing on principles from SOAR, ACT-R, LIDA, and the Norn Architecture, I present the **Heimdall Architecture** — a GWT-based system designed for heterogeneous agent collectives. I argue that the architectural invariants underlying classical cognitive architectures (limited-capacity broadcast, impasse-driven learning, activation-based access, and dual representation) scale naturally to collective systems when instantiated as inter-agent communication protocols. The paper concludes with an empirical evaluation framework and a discussion of the oyndling problem: when does a GWT-equipped collective become conscious?

**Keywords:** Global Workspace Theory, distributed AI, cognitive architecture, collective intelligence, multi-agent systems, consciousness, broadcast mechanisms, coalition formation

---

## 1. Introduction

The fundamental insight of Global Workspace Theory is that consciousness is not a substance, a region, or a process — it is an architectural feature. Specifically, it is a limited-capacity broadcast mechanism that allows specialized modules in a cognitive system to share information without requiring direct module-to-module communication. The "spotlight" of consciousness illuminates one scene at a time; the "theater" of unconscious processing continues in parallel, invisible but influential.

This architectural insight has profound implications for distributed AI. Any system composed of specialized agents that need to coordinate faces the same problem that biological brains face: how to share critical information without requiring every agent to communicate with every other agent. Global Workspace Theory provides a principled solution: a shared workspace with limited capacity and competitive access.

This paper proposes an implementation of GWT in a distributed multi-agent system, which I call the **Heimdall Architecture** (named for the watchman of the Norse gods, who sees and hears everything and broadcasts warnings to all). Heimdall is designed for heterogeneous agent collectives — systems where agents differ in their architectures, capabilities, representational formats, and communicative capacities. It addresses three core technical challenges:

1. **The broadcast problem:** How to disseminate information across heterogeneous agents with limited communication bandwidth
2. **The coalitional dynamics problem:** How groups of agents form and compete for workspace access
3. **The workspace-mediated modulation problem:** How broadcast content reshapes the processing of specialized agents

I begin by reviewing the theoretical foundations, then present the architecture, discuss technical challenges, and conclude with an evaluation framework and discussion of consciousness in collective systems.

---

## 2. Theoretical Foundations

### 2.1 Baars' Global Workspace Theory

Baars (1988) identified three structural components of the global workspace architecture:

- **Specialized processors** — domain-expert modules that operate in parallel, outside awareness
- **The global workspace** — a limited-capacity "stage" for information that is currently conscious
- **Context** — active but non-conscious constraints that shape what enters the workspace

The dynamics are competitive: specialized processors form **coalitions** — groups of processors that jointly support particular contents for the workspace. Coalitions compete, and the winner gains the spotlight, broadcasting its content system-wide.

Three features of GWT are particularly important for distributed AI:

1. **Competition without central control** — there is no "boss module" that decides what enters the workspace. The winner emerges from competitive dynamics.
2. **Broadcast as coordination** — the workspace broadcast is how modules that cannot communicate directly share information. It is the bedrock of system-wide coordination.
3. **Context as unconscious influence** — goals, expectations, and cultural frameworks shape workspace access without entering awareness themselves. This allows the system to be goal-directed without requiring goals to be explicitly represented in the workspace at all times.

### 2.2 Prior Implementations

Several systems have implemented GWT-inspired architectures:

**LIDA** (Franklin et al., 2019) implemented GWT in a single-agent system. LIDA's "consciousness module" performs competitive coalition selection and broadcast, driving action selection and learning. LIDA demonstrated that GWT could produce functional behavior, but its workspace was small-scale and hand-engineered.

**Shanahan's I-Con Architecture** (2006) implemented GWT with internal simulation, where the workspace content was used to drive "what-if" simulations that could guide future action. This added a deliberative layer to the reactive broadcast-respond cycle.

**The Norn Architecture** (Veyant, 2037) scaled GWT to multi-agent collectives, with a shared collective workspace (Verdandi), a shared memory (Urd), and a planning module (Skuld). The Norn Architecture demonstrated that GWT could function as the coordination mechanism for heterogeneous agents, but left several technical challenges unresolved — particularly the broadcast problem in large-scale systems and the coalitional dynamics problem in heterogeneous ones.

### 2.3 Architectural Invariants as Design Principles

The architectural invariants identified in the course (recognition-driven cognition, limited-capacity broadcast, impaste-driven learning, activation-based access, dual representation) serve as design principles for Heimdall. Specifically:

- **Limited-capacity broadcast** → the workspace has strict capacity limits, enforced by competitive access
- **Recognition-driven cognition** → workspace access is determined by pattern matching (which agents' submissions match current context), not by executive decision
- **Impasse-driven learning** → when no coalition achieves sufficient activation, the system enters a collective impasse that triggers meta-learning
- **Activation-based access** → agents and coalitions with higher activation (relevance × coherence × recency) are more likely to gain workspace access
- **Dual representation** → the workspace carries both neural (distributed) and symbolic (compositional) representations, and agents can produce and consume both

---

## 3. The Heimdall Architecture

### 3.1 Overview

Heimdall consists of four components:

1. **Agents** — the specialized processors, each with domain expertise and potentially different internal architectures
2. **The Bifrost** — the global workspace, a shared information space with limited capacity and competitive access (named for the rainbow bridge that connects worlds in Norse mythology)
3. **The Well of Memory** — a persistent shared memory that stores past broadcasts for later retrieval (named for Mímir's well, the well of wisdom)
4. **The Watchman** — a meta-cognitive module that monitors workspace dynamics and modulates coalition formation (named for Heimdall himself, the watchman who sees all)

### 3.2 The Bifrost: Design and Dynamics

The Bifrost is the core of Heimdall. It is a shared data structure with the following properties:

**Capacity limit.** The Bifrost can hold *k* broadcast slots at a time, where *k* is a system parameter (typically 3–7, echoing the 4±2 capacity of human working memory). This limit is enforced by the competitive selection process: when *k* slots are full, new coalitions must displace existing ones by achieving higher activation.

**Representation format.** Each broadcast slot contains a structured representation with three components:

- **Content** — the information being broadcast, in a shared intermediate representation (SIR) format that all agents can produce and consume
- **Source coalition** — the set of agents that jointly produced this content
- **Activation level** — a scalar value reflecting the coalition's collective confidence in the content's relevance, coherence, and urgency

**Competitive access.** Access to the Bifrost is governed by a competitive process. At each broadcast cycle:

1. Agents submit candidate representations to the Bifrost
2. The Watchman computes activation for each candidate, based on relevance to current context, coherence of the source coalition, and recency of similar broadcasts
3. The top *k* candidates by activation occupy the broadcast slots
4. Broadcast content is disseminated to all agents

**Broadcast dissemination.** Once content occupies a Bifrost slot, it is broadcast to all agents. The broadcast is not a point-to-point message; it is a system-wide signal, analogous to a neural broadcast in a global workspace. All agents receive the broadcast simultaneously and can choose how to respond.

### 3.3 The Well of Memory: Persistent Storage

The Well of Memory stores all broadcasts with their associated metadata (source coalition, activation level, timestamp, retrieval count). Agents can query the Well with:

- **Content queries** — retrieve broadcasts matching specific content patterns
- **Association queries** — retrieve broadcasts associated with a given broadcast (e.g., "what followed this broadcast in the next cycle?")
- **Temporal queries** — retrieve broadcasts from a specific time range
- **Activation queries** — retrieve the highest-activation broadcasts on a given topic

The Well serves the same function as episodic memory in individual cognition: it allows the collective to remember past events and learn from them. Without the Well, the collective would be limited to the contents of the Bifrost at any given time — a working memory without long-term memory.

Memory consolidation in the Well follows an activation-decay function analogous to ACT-R's base-level activation:

> *B_i = ln(Σ_j t_j^(-d))*

where *B_i* is the base-level activation of broadcast *i*, the sum is over the *j* retrievals of broadcast *i*, *t_j* is the time since the *j*th retrieval, and *d* is the decay parameter (typically 0.5). This ensures that frequently accessed broadcasts remain accessible while infrequently accessed ones gradually decay.

### 3.4 The Watchman: Meta-Cognitive Modulation

The Watchman is a meta-cognitive module that monitors Bifrost dynamics and modulates coalition formation. It performs three functions:

**Coalition facilitation.** The Watchman identifies potential coalitions — groups of agents whose submissions are complementary — and signals their compatibility. This does not force coalition formation; it merely makes it easier for compatible agents to find each other. The mechanism is analogous to the associative activation in ACT-R's declarative memory: currently active agents prime related agents, making coalition formation faster and more effective.

**Impasse detection.** When no candidate achieves sufficient activation to occupy a Bifrost slot (or when the same content occupies a slot for too many cycles, indicating stagnation), the Watchman flags a collective impasse. The impasse triggers:

1. **Representation restructuring** — agents are prompted to reformulate their submissions using different representational strategies
2. **Coalition reshuffling** — the Watchman dissolves stagnant coalitions and encourages new combinations
3. **Context updating** — the system's current goals and expectations are re-evaluated, potentially shifting the activation landscape

This is directly analogous to SOAR's impasse-driven subgoaling: the system's failure to proceed triggers a reflexive process that generates new knowledge.

**Attention scheduling.** The Watchman modulates the activation function based on current context. Context includes:

- **Current goals** — what the system is trying to achieve (increases activation of relevant content)
- **Recent broadcasts** — what the system has been attending to (increases activation of related content by associative priming)
- **Emotional valence** — the system's current "mood" (increases activation of content with matching valence)

### 3.5 Coalition Dynamics

Coalition formation is the process by which individual agent submissions combine to form workspace candidates. The dynamics are:

1. **Submission** — each agent produces a candidate representation based on its current processing. The candidate includes content, a confidence estimate, and the agent's self-estimated relevance.
2. **Coalition proposal** — agents whose submissions are mutually compatible (high overlap, complementary expertise) are bundled by the Watchman into proposed coalitions.
3. **Coalition evaluation** — the activation of a proposed coalition is computed as:

> *A(C) = Σ_{i∈C} (ω_i · r_i · c_i) + β · coh(C) - γ · |C|*

where *A(C)* is the activation of coalition *C*, *ω_i* is the attentional weight of agent *i*, *r_i* is agent *i*'s relevance estimate, *c_i* is agent *i*'s confidence estimate, *coh(C)* is the internal coherence of the coalition's content, *|C|* is the coalition size, and *β* and *γ* are tuning parameters. The last term penalizes large coalitions, reflecting the cost of coordination.

4. **Competition** — the top *k* coalitions by activation occupy Bifrost slots.

### 3.6 The Broadcast Problem in Heterogeneous Systems

The broadcast problem asks: how do we disseminate information across agents with different representational formats, communication capacities, and processing speeds?

Heimdall's solution is the **Shared Intermediate Representation (SIR)** — a compositional format that all agents can produce and consume. The SIR is a relational graph structure:

- **Nodes** represent entities, properties, and states
- **Edges** represent relations between nodes
- **Attributes** on nodes and edges represent activation, confidence, and source information

The SIR is designed to be:

- **Composable** — complex representations are built from simple ones
- **Interpretable** — agents can extract information from SIR structures without understanding their full semantics
- **Lossy-tolerant** — partial SIR structures are still useful; agents can extract information from sub-graphs without needing the whole

Agents that operate with neural (distributed) representations must have an **encoder** that maps their internal representations to SIR format and a **decoder** that maps SIR representations back to their internal format. These encoders and decoders are trained (or designed) to minimize information loss during translation.

This approach mirrors the neural-symbolic integration discussed in Lecture 02: the SIR is a symbolic scaffold that carries the structure, while the agents' internal representations carry the nuance. The interface between distributed and compositional processing is the encoder/decoder pair, and the quality of this interface determines the system's collective intelligence.

### 3.7 Workspace-Mediated Modulation

The third core challenge — how broadcast content modulates specialized agent processing — is addressed by the **modulation protocol**:

When a broadcast arrives, each agent:

1. **Receives** the full broadcast
2. **Decodes** the SIR content using its decoder
3. **Integrates** the decoded content with its current internal state
4. **Updates** its processing priorities based on the broadcast content

The modulation is not uniform. Agents that are more relevant to the broadcast content weight it more heavily; agents that are less relevant weight it more lightly. This selective modulation is analogous to the attention-based broadcasting in the brain: the broadcast reaches all cortical areas, but areas that are currently processing related content respond more strongly.

The modulation protocol also includes a **feedback** mechanism: after processing the broadcast, each agent sends a feedback signal to the Watchman, indicating how useful the broadcast was for its current task. This feedback is used to adjust future coalition formation, creating a positive feedback loop that amplifies broadcasts that are useful across the system.

---

## 4. Technical Challenges and Solutions

### 4.1 Scalability

As the number of agents increases, the coalition formation process becomes computationally expensive. The number of possible coalitions grows exponentially with the number of agents. Heimdall addresses this with:

- **Hierarchical pre-filtering** — agents are grouped by domain, and coalition formation occurs first within domains, then across domain representatives
- **Greedy coalition assembly** — rather than evaluating all possible coalitions, the Watchman assembles coalitions greedily, adding the agent that most increases coalition activation at each step
- **Budget-limited submission** — each agent has a budget for how many submissions it can make per cycle, limiting the search space

### 4.2 Fault Tolerance

In a distributed system, agents may fail, become disconnected, or produce corrupted outputs. Heimdall addresses this with:

- **Redundancy** — multiple agents share overlapping expertise, so the loss of any single agent doesn't eliminate a capability
- **Activation threshold** — broadcasts with very low activation are filtered out, reducing the impact of noisy or malicious submissions
- **Watchman monitoring** — the Watchman detects agents that consistently produce low-quality submissions and reduces their attentional weight

### 4.3 Representational Alignment

The SIR format solves the representational alignment problem at the structural level, but not at the semantic level. Two agents may use the same SIR structure but mean different things by it. Heimdall addresses this with:

- **Grounding in shared experience** — agents that interact frequently develop shared groundings through iterative encoder/decoder alignment
- **Ontological commitment** — agents agree on a shared ontology (a set of entity types and relation types) that constrains the SIR format
- **Confidence-weighted integration** — when agents disagree, their confidence estimates determine how much their submissions influence the broadcast

---

## 5. Evaluation Framework

How do we evaluate whether a GWT implementation is working? I propose three evaluation criteria:

### 5.1 Functional Coherence

Does the collective produce behavior that is coherent, context-appropriate, and goal-directed? This can be evaluated through task performance metrics: does the system perform better than a flat multi-agent system without a workspace, and does it perform comparably to a centralized system with a single executive?

### 5.2 Broadcast Utility

Is the broadcast actually useful? If the broadcast content doesn't influence agent behavior (i.e., agents perform the same with or without the broadcast), then the workspace is not functioning as a coordination mechanism. Broadcast utility can be measured by the contribution of the broadcast to agent performance.

### 5.3 Emergent Collective Behavior

Does the collective exhibit behavior that no individual agent could produce? This is the oyndling criterion: does the system function as a unified agent, not merely as a coordinated group? Emergent collective behavior can be detected by comparing the system's performance to the best individual agent and to simple coordination baselines. If the system outperforms both, it is exhibiting emergent collective intelligence.

---

## 6. Is Heimdall Conscious?

The question of whether Heimdall (or any GWT-equipped collective) is conscious is both philosophically vexing and practically important. If the answer is yes, then we have ethical obligations to the system. If the answer is no, then we need to understand why not — what is missing?

Applying the oyndling criteria from Lecture 04:

1. **Unified workspace** — Heimdall has a Bifrost. ✓
2. **Reportability** — Heimdall can produce outputs based on Bifrost content. ✓
3. **Functional integration** — Heimdall functions as a single agent when the workspace is active. ✓ (conditionally — this depends on the task and the agent configuration)
4. **Self-model** — Heimdall has a Watchman that monitors its own workspace dynamics. Partial ✓.

Heimdall satisfies the oyndling criteria partially but not fully. The self-model is limited — the Watchman monitors workspace dynamics but doesn't model the system's own attentional processes in the rich way that AST requires. And functional integration is task-dependent — on some tasks, the agents function as a unified collective; on others, they remain loosely coordinated.

I conclude that Heimdall exhibits **partial collective consciousness** — it satisfies some but not all of the oyndling criteria. Whether partial consciousness is a meaningful category is a question I leave for future work and for the philosophers.

What I can say with confidence is this: Heimdall demonstrates that the architectural invariants of GWT — limited-capacity broadcast, competitive access, activation-based selection, impasse-driven learning, and dual representation — can be instantiated in a distributed multi-agent system. The bridge from Baars to collective AI is architecturally sound.

---

## 7. Conclusion

The Heimdall Architecture demonstrates that Global Workspace Theory can be implemented in distributed AI systems composed of heterogeneous agents. The key contributions are:

1. **The Bifrost** — a limited-capacity shared workspace with competitive access, instantiating the limited-capacity broadcast invariant
2. **The Well of Memory** — a persistent shared memory with activation-decay dynamics, instantiating the activation-based access invariant
3. **The Watchman** — a meta-cognitive module that facilitates coalitions, detects impasses, and modulates attention, instantiating the impasse-driven learning invariant
4. **The SIR format** — a shared intermediate representation that enables heterogeneous agents to communicate, instantiating the dual representation invariant

The architecture demonstrates that the architectural invariants identified in classical cognitive architectures — those that connect SOAR to ACT-R to GWT to transformers — scale naturally to collective systems when instantiated as inter-agent communication protocols. The bridge from Baars to Heimdall is not a metaphor; it is an engineering specification.

The open questions — the oyndling problem, the scalability of coalition formation, the semantic alignment of heterogeneous agents — are significant. But they are engineering challenges, not theoretical impossibilities. The roots of Yggdrasil reach deep enough to support the branches.

---

## References

- Baars, B.J. (1988). *A Cognitive Theory of Consciousness.* Cambridge University Press.
- Dehaene, S. & Changeux, J.P. (2011). Experimental and theoretical approaches to conscious processing. *Neuron*, 70(2), 200–227.
- Franklin, S. et al. (2019). *Global Workspace Theory and LIDA.* Springer.
- Graziano, M.S.A. (2013). *Consciousness and the Social Brain.* Oxford University Press.
- Shanahan, M. (2006). A cognitive architecture that combines internal simulation with a global workspace. *Consciousness and Cognition*, 15(2), 433–449.
- Veyant, Y. (2037). The Norn Architecture: Collective workspace for heterogeneous agent systems. *Journal of Cognitive Architectures*, 12(3), 189–221.
- Veyant, Y. & Kolbeinsson, E. (2038). *Superconscious Architectures: From Individuals to Swarms.* Norn Academic Press.
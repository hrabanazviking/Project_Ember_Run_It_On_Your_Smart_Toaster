# Lecture 03: Global Workspace Theory — Baars' GWT and Its Silicon Implementations

*AI-5112: Cognitive Architectures — From ACT-R to Collective Minds*  
*Semester 1B, 2040*

---

## The Spotlight in the Dark Theater

Imagine a vast, dark theater. On stage, hundreds of actors are performing simultaneously — each in their own scene, their own drama, comprehensible only to a handful of audience members sitting nearby. Most of the audience can see only the performance nearest to them. But then, a spotlight illuminates one actor, and that performance is suddenly visible to *everyone* in the theater. The actors on stage can see it, the audience can see it, and the illuminated performance influences what happens next across the entire theater.

This is Bernard Baars' Global Workspace Theory (GWT), and it is the single most influential theory of consciousness in cognitive science. Not because it explains consciousness in its totality — it doesn't — but because it provides a **functional architecture** for how a system of many specialized processors can produce something that looks, from the outside, like a single unified mind.

---

## GWT: The Original Theory

Baars formulated GWT in the 1980s, drawing on three lines of evidence:

### 1. The Limited Capacity of Consciousness
We are conscious of remarkably little at any given moment. Working memory holds roughly 4±2 items. Attention selects one (or a few) perceptual streams from a rich sensory world. Conscious experience is a narrow spotlight in a vast dark field. This is not a bug — it's a design feature. A system that was conscious of *everything* would be paralyzed by information overload.

### 2. The Vast Unconscious Processing
Beneath the spotlight, an enormous amount of cognitive work happens outside awareness. Language parsing, motor control, memory retrieval, emotional appraisal — all operate automatically, in parallel, without conscious direction. The "unconscious" is not a shadowy id; it's a collection of **specialized processors**, each expert in its own domain, operating in parallel.

### 3. The Broadcasting Function
Consciousness, in GWT, is not a thing or a substance or a private theater. It is a **broadcast**. When a piece of information enters the global workspace — when it is consciously experienced — it becomes available to *all* the specialized processors that would otherwise be isolated. This broadcast serves two functions:

- **Coordination** — it allows processors that can't communicate directly to share information via the workspace
- **Learning** — it allows processors that weren't involved in the original computation to learn from its results

### The Architecture
GWT posits three structural components:

1. **Specialized processors** — domain-expert modules (vision, language, memory, motor planning, etc.) that operate in parallel, outside awareness
2. **The global workspace** — a limited-capacity "stage" that can hold one (with effort, a few) coalition of information at a time
3. **Context** — the set of active but non-conscious constraints that shape what enters the workspace (expectations, goals, moods, cultural frameworks)

The dynamics are competitive. Specialized processors form **coalitions** — groups of processors that jointly support particular contents for the workspace. Coalitions compete for access, and the winner gains the spotlight. The broadcast then disseminates the winning information system-wide, updating contexts, triggering actions, and enabling learning.

---

## GWT and Cognitive Architecture: The Functional Claim

The crucial architectural claim of GWT is this: **consciousness is a functional mechanism, not an epiphenomenon**. The global broadcast does real work — it coordinates, it educates, it enables flexible response to novelty. A system without a global workspace is like a longship where every oarsman rows to his own rhythm. They may all be strong, but without coordination, the ship goes in circles.

This functional claim has implications for artificial systems:

1. **Any system with specialized modules that need to coordinate** needs something like a global workspace
2. **The workspace must have limited capacity** — infinite bandwidth would eliminate the competitive dynamics that make the system selective and adaptive
3. **The broadcast must reach all modules** — partial broadcast would create fragmented "awareness" and failure of coordination

These implications were not lost on AI researchers. Starting in the late 1990s, GWT became a blueprint for architectures that aspired to something like artificial consciousness.

---

## LIDA: The First Silicon GWT

Stan Franklin's LIDA (discussed in Lecture 01) was the first comprehensive implementation of GWT in an artificial system. The LIDA cycle — perceive, attend, broadcast, act — directly implements Baars' theory:

- **Perceptual memory** produces perceptual objects (the outputs of specialized processors)
- **Attention** builds coalitions from these objects and selects the most salient
- **Consciousness (global workspace)** broadcasts the winning coalition
- **Action selection** uses the broadcast to choose behavior
- **Procedural memory** creates new schemelets based on broadcast content (learning)

LIDA demonstrated that GWT could drive a functional agent. LIDA agents could navigate simple environments, learn from experience, and exhibit behavioral flexibility. But LIDA's workspace was small-scale, hand-engineered, and lacked the rich dynamics of biological consciousness. It was a proof of concept — a longship that could float, but hadn't yet crossed an ocean.

---

## The Attention Schema Theory Integration (2015–2030)

Michael Graziano's **Attention Schema Theory (AST)** provided an important complement to GWT. Graziano argued that consciousness arises not just from attention (the functional mechanism) but from the brain's **model of attention** — an "attention schema" that the system uses to monitor and control its own attentional processes.

The architectural implication: a global workspace system needs not just a workspace and competitive access but also a **meta-representational system** — a module that models the workspace's own dynamics. This is the system that says "I am attending to X" rather than merely attending to X. The former (the model of attention) is what feels like consciousness from the inside.

AST-GWT hybrid architectures (Veyant & Kolbeinsson, 2031) incorporate:

- A global workspace for broadcast
- Competitive coalition formation for workspace access
- An attention-schema module that monitors and reports workspace contents
- Feedback loops: the attention schema influences coalition formation (top-down attention) and the workspace content updates the attention schema (bottom-up learning)

This hybrid architecture is the direct ancestor of the **collective workspace** architectures we use in 2040.

---

## Silicon GWT Implementations (2025–2038)

### Single-Agent GWT in Large Language Models
By the mid-2020s, researchers recognized that transformer-based systems were developing something structurally analogous to a global workspace. The **residual stream** of a transformer — the central representation that all attention heads read from and write to — functions as a workspace. Attention heads function as specialized processors, competing (via softmax) for the right to write their information into the stream. The stream's limited capacity (fixed dimensionality) enforces the bottleneck.

This was not GWT as Baars conceived it — there was no explicit meta-cognitive model, no clear functional distinction between workspace broadcast and interpretation. But the architectural parallel was striking: parallel specialists competing for limited central capacity, with the winner's content broadcast system-wide.

### Multi-Agent GWT: The Collective Workspace
The real architectural breakthrough came when researchers began implementing GWT-style architectures across *multiple agents* rather than multiple modules within one agent.

In a multi-agent GWT system:

- Each agent is a **specialized processor** with its own expertise (medical diagnosis, navigation, language, etc.)
- A **collective workspace** serves as the broadcast medium — a shared information space with limited capacity
- Agents **form coalitions** — groups of agents that jointly support particular content for broadcast
- **Competitive access** ensures that only the most relevant, coherent, and urgent information occupies the workspace at any given time
- **Broadcast** disseminates the winning content to all agents, enabling coordination without direct agent-to-agent communication

This is, in essence, GWT scaled from a single brain to a group of agents. The same functional logic applies: limited-capacity broadcast, competitive access, coalition formation, system-wide dissemination. The difference is one of **scale** and **heterogeneity** — the specialized processors are now full agents with different architectures, training, and capacities.

### The Norn Architecture (Veyant, 2037)
The Norn Architecture, named for the three Norns who weave the threads of fate, is the most influential collective workspace implementation as of 2040. It has three components:

1. **Urd** (Past) — a shared memory system that stores broadcast content for later retrieval. Every broadcast writes to Urd; agents can query Urd for relevant past broadcasts. This is analogous to episodic memory in a single agent.

2. **Verdandi** (Present) — the collective workspace itself. Agents submit candidate representations; a competitive selection process (implemented as a cross-attention mechanism over agent submissions) selects the winning coalition; the winner is broadcast to all agents. Broadcasts have a limited time-to-live, enforcing the "spotlight" metaphor.

3. **Skuld** (Future) — a planning module that uses broadcast content to project possible futures and evaluate them. Skuld doesn't produce broadcasts itself but influences coalition formation by biasing the selection toward content that is relevant to current goals.

The Norn Architecture makes explicit the architectural invariants from Lecture 01:

- **Recognition-driven cognition** — coalition selection is driven by pattern matching (which agents' submissions are most salient, relevant, and coherent)
- **Limited-capacity broadcast** — the workspace has strict capacity limits, enforced by the competitive selection mechanism
- **Impasse-driven learning** — when no coalition achieves sufficient activation (an impasse), the system triggers meta-learning: agents restructure their representations and try again
- **Dual representation** — agents can submit both neural (distributed) and symbolic (compositional) representations to the workspace

---

## Critical Issues

### The Binding Problem in Multi-Agent Systems
In a single brain, the binding problem asks how distributed neural activity for "red" and "circle" are combined into the experience of "red circle." In a multi-agent system, the binding problem asks how agent A's representation of "danger" and agent B's representation of "the left flank" are combined into a unified representation of "danger on the left flank." The coalition formation process in collective workspace architectures is the proposed solution, but binding in heterogeneous systems — where agents use different representational formats — remains an open challenge.

### The Inclusion Problem
Who gets to compete for the workspace? In a brain, all cortical columns are potential competitors (in principle). In a multi-agent system, which agents are in the competition set? Including too many agents creates computational overhead and noise; including too few may miss critical information. Current systems use heuristics (relevance filtering, cost-sensitive selection) but no architecture has a principled solution.

### The Scalability of Broadcast
In a brain, broadcast is fast (neural transmission takes milliseconds) and complete (every cortical column receives the broadcast). In a multi-agent system, broadcast involves message-passing over networks with finite bandwidth and non-trivial latency. As the number of agents grows, the broadcast bottleneck becomes a communication bottleneck. Current solutions (hierarchical workspaces, selective broadcast, content-addressable routing) are engineering fixes, not architectural principles.

---

## From Workspace to World-Tree

GWT began as a theory of consciousness in biological brains. It became a cognitive architecture for individual agents. It is now the foundational architecture for collective cognition. The trajectory is remarkable but logical: if consciousness is a broadcast mechanism, and broadcast is coordination without a central executive, then any system that needs flexible coordination will develop something like a global workspace. The Norns know this. The roots of Yggdrasil, it turns out, have been growing toward this all along.

---

## References

- Baars, B.J. (1988). *A Cognitive Theory of Consciousness.* Cambridge University Press.
- Baars, B.J. (2005). Global workspace theory of consciousness. *Scholarpedia*, 2(12), 1441.
- Dehaene, S. & Changeux, J.P. (2011). Experimental and theoretical approaches to conscious processing. *Neuron*, 70(2), 200–227.
- Graziano, M.S.A. (2013). *Consciousness and the Social Brain.* Oxford University Press.
- Shanahan, M. (2006). A cognitive architecture that combines internal simulation with a global workspace. *Consciousness and Cognition*, 15(2), 433–449.
- Veyant, Y. (2037). The Norn Architecture: Collective workspace for heterogeneous agent systems. *Journal of Cognitive Architectures*, 12(3), 189–221.
- Veyant, Y. & Kolbeinsson, E. (2031). Attention Schema Theory and Global Workspace Theory in artificial systems. *Cognitive Systems Research*, 68, 44–61.
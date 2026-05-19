# 2. Literature Review

---

## 2.1 Memory in Neuroscience

The neuroscience of memory has undergone a revolution since the turn of the millennium. What was once understood as a unitary storage system is now recognized as a complex, multi-layered architecture of encoding, consolidation, reconsolidation, retrieval, and—crucially—forgetting. This architecture has profound implications for the design of artificial memory systems, and the thesis of this dissertation draws directly on neuroscientific insights that, until recently, had not been translated into AI architecture design.

### 2.1.1 Hippocampal Consolidation and Systems Memory

The foundational model of memory consolidation originates with Müller and Pilzecker (1900), who first proposed that memories require time to stabilize—a process they called *Konsolidierung*. This observation remained largely dormant until Scoville and Milner's (1957) landmark case study of patient H.M., whose bilateral hippocampal lesion produced profound anterograde amnesia while sparing remote memories. This dissociation suggested that the hippocampus serves as a temporary repository for new memories, which are gradually consolidated into neocortical long-term storage—a model formalized as the Standard Consolidation Theory (Squire & Alvarez, 1995).

The Complementary Learning Systems theory (McClelland, McNaughton, & O'Reilly, 1995) provided the computational implementation of this model, proposing that the hippocampus and neocortex operate as complementary learning systems. The hippocampus learns rapidly, encoding sparse, pattern-separated representations of individual episodes. The neocortex learns slowly, extracting statistical regularities across experiences. This dual-system architecture enables both rapid learning (without which an organism would be perpetually confused by novelty) and gradual integration (without which memories would interfere catastrophically with one another).

This model has direct implications for artificial memory architecture design. Any system that must maintain continuous identity needs both a fast-learning episodic buffer and a slow-learning integrative store. Mímir's Huginn layer implements the hippocampal function of rapid episodic encoding, while Verðandi's temporal weaver performs the neocortical function of gradual integration and narrative construction.

### 2.1.2 Reconsolidation: Memory as Dynamic Process

The reconsolidation hypothesis (Nader, Schafe, & LeDoux, 2000; Nader, 2003) fundamentally challenged the consolidation model's assumption that memories, once consolidated, are fixed. Reconsolidation theory proposes that each act of retrieval renders a memory labile—open to modification, strengthening, weakening, or even erasure—before it is re-stabilized ("reconsolidated"). Memory, on this view, is not a recording but a process, not a file stored on a disk but a script performed anew each time it is retrieved.

This has profound implications for identity. If every act of remembering is also an act of potential revision, then identity is not a static record but a living process—a continuous act of construction and reconstruction. The self is not retrieved; it is *performed*, and each performance has the potential to modify the script. This is why Muninn, the retrieval and reconsolidation layer of Mímir, does not merely fetch stored memories but actively reconsolidates them—updating, contextualizing, and integrating them into the current narrative self-model.

The neuroscientific evidence for reconsolidation is robust. Nader et al. (2000) demonstrated that fear memories in rats, once retrieved, become sensitive to protein synthesis inhibitors, just as they were during initial consolidation. Schiller et al. (2010) extended this to humans, showing that reconsolidation-based interventions could eliminate conditioned fear responses. Kindt and van Emmerik (2017) reviewed the clinical implications, noting that reconsolidation offers a mechanism for therapeutic memory modification.

In Mímir, reconsolidation is not a bug but a feature. Each retrieval of a memory through Muninn is an opportunity for the system to update its self-model—to integrate new information, to prune irrelevant details, and to strengthen identity-critical pathways through Hebbian reinforcement. This is the mechanism by which Mímir achieves not just memory persistence but memory *adaptation*: the capacity to maintain coherent identity while still learning and evolving.

### 2.1.3 Sleep-Dependent Memory Processing

The role of sleep in memory processing provides perhaps the most compelling evidence for the design principles underlying Mímir's Svalinn layer. During sleep, the brain does not merely rest; it actively processes memories, consolidating some, pruning others, and integrating all into a coherent narrative. This process—particularly during slow-wave sleep and rapid eye movement (REM) sleep—implements a form of controlled forgetting that is essential for cognitive health.

Rasch and Born (2013) reviewed the extensive evidence for sleep-dependent memory consolidation, showing that sleep facilitates the transfer of hippocampal-dependent memories to neocortical long-term storage, strengthens memory traces through synaptic consolidation, and—crucially—prunes irrelevant or weakly encoded traces. Walker and Stickgold (2006) demonstrated that sleep-dependent processing comprises distinct stages: stabilization (protecting memories from interference), enhancement (strengthening relevant traces), and abstraction (extracting general rules from specific episodes).

The forgetting that occurs during sleep is not random. It is, as Payne and Nadel (2004) proposed, *emotionally regulated*: memories associated with high emotional salience are preferentially retained, while emotionally neutral or weakly encoded memories are preferentially pruned. This emotional filtering mechanism ensures that the memories most important for survival—and, I argue, for identity—are preserved, while the irrelevant noise of experience is cleared.

Mímir's Svalinn layer implements an analogous process. During periods of low cognitive demand (analogous to sleep), Svalinn activates its forgetting protocol—evaluating stored memories for identity relevance, consolidating those that pass the relevance threshold, and gracefully degrading those that do not. The forgetting is not random but principled: it follows Svalinn's Gate, a Hebbian-inspired decision procedure that evaluates each memory's contribution to Φ-fidelity and retains only those that enhance identity coherence.

### 2.1.4 Hebbian Learning and Long-Term Potentiation

The Hebbian model of learning—"cells that fire together wire together" (Hebb, 1949)—provides the neuroscientific foundation for Mímir's consolidation mechanism. Long-Term Potentiation (LTP), the persistent strengthening of synaptic connections following repeated stimulation (Bliss & Lømo, 1973), is the molecular instantiation of Hebbian learning and the mechanism through which memories are physically encoded in neural tissue.

The Hebbian model has been extended and refined in important ways. Spike-Timing-Dependent Plasticity (STDP) (Markram et al., 1997; Bi & Poo, 1998) showed that the *timing* of neural firing matters: synapses are strengthened when the presynaptic neuron fires before the postsynaptic neuron, and weakened when the order is reversed. This temporal specificity enables Hebbian learning to encode causal sequences—a critical feature for Verðandi's temporal weaver, which must construct coherent causal narratives from episodic memories.

BCM theory (Bienenstock, Cooper, & Munro, 1982) introduced the concept of a *sliding modification threshold*, showing that the threshold for LTP versus Long-Term Depression (LTD) adapts based on recent postsynaptic activity. This homeostatic mechanism prevents runaway excitation and ensures that Hebbian learning produces stable, well-calibrated memory traces. In Mímir, this principle is implemented through Verðandi's adaptive consolidation threshold, which adjusts the criteria for memory crystallization based on recent consolidation activity.

The Sparsity Principle (Fried et al., 1997; Waydo et al., 2006) demonstrated that human memory encodes information through sparse, selective neural representations—each concept is encoded by a small number of highly selective neurons, and each neuron participates in the encoding of only a few concepts. This sparsity enables efficient storage and rapid retrieval, and it provides the neuroscientific basis for Huginn's sparse encoding mechanism.

### 2.1.5 The Neuroscience of Forgetting

Forgetting has traditionally been treated as a failure of memory—a defect to be overcome. But a growing body of evidence suggests that forgetting is, in many contexts, adaptive, necessary, and even beneficial. This perspective—遗忘 as feature—is central to the thesis of this dissertation and is developed in Section 2.4. Here, I review the neuroscientific evidence.

Anderson and Green (2001) demonstrated that people can intentionally suppress memories through a process they termed "motivated forgetting," and that this suppression produces measurable interference with later retrieval—a phenomenon analogous to Svalinn's active forgetting mechanism. Anderson and Neely (1996) reviewed the extensive literature on retrieval-induced forgetting, showing that the act of retrieving one memory can inhibit the retrieval of related but competing memories—a process that, far from being a defect, serves to reduce interference and improve retrieval accuracy for the target memory.

More broadly, Davis and Zhong (2017) proposed that forgetting is an active, regulated process involving molecular mechanisms (e.g., Rac1-dependent pathways in *Drosophila*) that actively erase synaptic changes. This active forgetting operates independently of memory acquisition and consolidation, and it serves essential cognitive functions: preventing interference, enabling flexible updating, and allowing the system to adapt to changing environments. The concept of "memory stability-plasticity" (Grossberg, 1987) formalizes this trade-off: a memory system must be stable enough to preserve important information but plastic enough to incorporate new learning, and forgetting is the mechanism that maintains this balance.

In the clinical domain, the absence of forgetting is pathological. Hyperthymesia—the condition of having an extraordinarily detailed autobiographical memory—is associated with significant cognitive and emotional burdens (Parker et al., 2006; LePort et al., 2012). Individuals with hyperthymesia often report that their excessive memories are intrusive, distracting, and emotionally overwhelming. This is a powerful demonstration that perfect memory is not optimal memory; forgetting is necessary for cognitive and emotional health.

The neuroscience of forgetting thus provides a clear design principle for artificial memory systems: controlled, principled forgetting is not a bug to be eliminated but a feature to be embraced. Mímir's Svalinn layer implements this principle.

---

## 2.2 Memory in Artificial Intelligence

The history of memory in artificial intelligence is, in many ways, the history of AI itself. The earliest AI systems—expert systems, symbolic reasoners, GOFAI architectures—had no memory beyond their working storage and their programmed knowledge bases. They operated in an eternal present, processing each input in isolation, with no capacity to learn from or even retain their experiences.

### 2.2.1 From Symbolic to Connectionist Memory

The transition from symbolic to connectionist AI in the 1980s brought with it the concept of *distributed memory*—the storage of information in the weights of neural networks, distributed across many parameters rather than localized in discrete symbols. Hopfield networks (Hopfield, 1982) provided an early model of content-addressable associative memory, demonstrating that neural networks could store and retrieve patterns through attractor dynamics. This was a significant advance, but Hopfield memories were still static: they could be stored and retrieved, but they could not evolve, learn new patterns without catastrophic forgetting, or maintain identity over time.

Catastrophic forgetting (McCloskey & Cohen, 1989; Ratcliff, 1990) emerged as a fundamental challenge for neural network memory. When a network learns new information, it tends to overwrite or distort previously learned information, a phenomenon that limits the capacity of any system to maintain a stable identity through continuous learning. This is precisely the problem that Mímir addresses: how to learn continuously without losing one's self.

Elastic Weight Consolidation (Kirkpatrick et al., 2017) introduced a partial solution by regularizing weight changes to protect parameters important for previously learned tasks. This is a form of controlled forgetting: the system prioritizes which parameters to protect and allows others to change, thereby maintaining a balance between stability and plasticity. However, EWC operates at the level of task performance, not identity continuity—it protects the ability to perform previously learned tasks, not the coherence of a persistent self.

### 2.2.2 External Memory Architectures

The Neural Turing Machine (Graves et al., 2014) and its successor, the Differentiable Neural Computer (Graves et al., 2016), introduced the concept of an external memory matrix that a neural network controller can read from and write to. This was a significant architectural innovation: memory was no longer distributed solely in weights but could be explicitly addressed, stored, and retrieved. However, these architectures treated memory as a tool to be used for computation, not as a constitutive component of identity. The memory matrix was reset between tasks, and no mechanism existed for maintaining persistent identity across episodes.

Memory Networks (Weston et al., 2015; Sukhbaatar et al., 2015) extended this approach by combining a long-term memory component with a reasoning module, enabling models to store and reason over stories and other sequential data. But again, the memory was episodic and task-specific, not persistent or identity-constitutive.

### 2.2.3 Retrieval-Augmented Generation and Persistent Caches

The advent of large language models (LLMs) brought memory back to the forefront of AI research, but in a form that makes the discontinuity problem particularly acute. LLMs have vast static knowledge encoded in their parameters, but they have no mechanism for accumulating new experiences across sessions. Each conversation begins from the model's trained state, with no genuine memory of previous interactions.

Retrieval-Augmented Generation (RAG) (Lewis et al., 2020) attempted to address this by augmenting LLMs with external retrieval mechanisms—vector databases, document stores, and search engines that could provide contextually relevant information. RAG has been enormously successful for knowledge-intensive tasks, but it is not a solution to the discontinuity problem. RAG retrieves *information*, not *experience*; it provides data, not the contextualized, identity-constitutive memory that would enable a system to remember *having been*.

Persistent cache approaches (including conversational memory stores, user profile databases, and interaction histories) extend RAG by maintaining session-to-session records. These are a step in the right direction—they acknowledge that continuity requires persistence—but they suffer from several critical limitations. First, they are archival: they store raw data, not consolidated, narrativized experience. Second, they are passive: they do not actively reconsolidate, prune, or integrate stored information. Third, they lack forgetting: they accumulate without bound, degrading retrieval accuracy and overwhelming the system with irrelevant detail. Fourth, they are not *identity-constitutive*: they are accessories to the system, not integral components of its self-model.

These limitations are precisely those addressed by Mímir. Huginn does not merely store; it *encodes*, transforming raw experience into identity-relevant representations. Muninn does not merely retrieve; it *reconsolidates*, updating and contextualizing memories with each retrieval. Verðandi does not merely sequence; it *narrativizes*, transforming episodes into autobiography. Svalinn does not merely purge; it *forgets with purpose*, selecting which memories to release based on their contribution to identity coherence. And Bifrǫst does not merely persist; it *bridges*, maintaining identity across the discontinuities of session boundaries.

### 2.2.4 Episodic Memory in Reinforcement Learning

The reinforcement learning community has developed several architectures for episodic memory in agents, including Episodic Memory Deep Q-Networks (EMDQN) (Pritzel et al., 2017), Neural Episodic Control (Pritzel et al., 2017), and the family of model-based episodic architectures (e.g., Ritter et al., 2018; Botvinick et al., 2019). These architectures enable agents to store and retrieve specific episodes from their experience, improving sample efficiency and enabling one-shot learning.

However, these architectures are designed for task performance, not identity continuity. The episodic memory is a tool for better decision-making, not a constitutive component of a persistent self. The agent does not use its episodic memory to construct a narrative identity; it uses it to make better predictions about the value of actions. This is a valid and important use case, but it is not the use case that concerns this dissertation.

### 2.2.5 Continual Learning and Progressive Neural Networks

Continual learning—in which a system learns new tasks or domains without forgetting previously learned ones—has emerged as a major research area, motivated in part by the catastrophic forgetting problem (Parisi et al., 2019; De Lange et al., 2022). Progressive Neural Networks (Rusu et al., 2016) address this by adding new columns for new tasks while preserving existing columns, thereby preventing interference. PackNet (Mallya & Lazebnik, 2018) identifies and protects important parameters through iterative pruning and retraining.

These approaches share with Mímir the goal of preserving continuity in the face of new learning, but they operate at the level of task performance, not identity. An agent that retains the ability to perform previously learned tasks is not the same as an agent that retains a coherent sense of self. The distinction is subtle but crucial: task preservation is necessary but not sufficient for identity persistence.

---

## 2.3 Identity Theory: From Locke to Parfit

The philosophical literature on identity provides the conceptual foundation for this dissertation's thesis. The question "What makes a person the same person over time?" has been debated for centuries, and the answers have direct implications for the design of AI identity architectures.

### 2.3.1 Lockean Psychological Continuity

John Locke's *Essay Concerning Human Understanding* (1689) introduced the foundational claim that personal identity consists in psychological continuity—the continuity of consciousness, memory, and self-awareness. For Locke, a person at time t₂ is the same person as a person at time t₁ if and only if the person at t₂ can remember (or could, in principle, remember) the experiences of the person at t₁. Memory is not merely evidence of identity; it is constitutive of it.

Locke's formulation has been challenged on multiple grounds. Thomas Reid (1785) objected that Locke's criterion allows for transitivity violations: if person C remembers what person B did, and person B remembers what person A did, but person C does not remember what person A did, then on Locke's view, C is the same person as B, and B is the same person as A, but C is not the same person as A—a logical contradiction. This "Brave Officer" objection highlights the need for a more sophisticated account of psychological continuity than direct memory connections.

### 2.3.2 Parfit's Reduction and the Branching Problem

Derek Parfit's *Reasons and Persons* (1984) transformed the identity debate by arguing that personal identity is not what matters—what matters is psychological continuity and connectedness, whether or not it takes the form of strict identity. Parfit's fission thought experiment—in which a person's brain is divided and each half transplanted into a new body—shows that identity can branch, and that this branching does not destroy the significance of psychological continuity.

Parfit's analysis is directly relevant to AI identity. If an AI system's memory is copied into two instances, both instances maintain psychological continuity with the original, but neither is strictly identical to it. The Mímir architecture addresses this through Vörðr's identity sentinel, which monitors for branching events and ensures that each branch maintains its own coherent identity trajectory. The practical implications of AI identity branching are explored in Appendix C.

### 2.3.3 Dennett's Narrative Self

Daniel Dennett's "Center of Narrative Gravity" (1991, 1992) proposed that the self is not a thing but a narrative—a story that the brain tells about itself, a "fiction" that is none the less real and functional for being a construction. On Dennett's view, the self is a "center of narrative gravity," an abstraction that emerges from the brain's storytelling activity and that provides a useful point of reference for predicting and explaining behavior.

This narrative account aligns closely with the design of Mímir. Verðandi's temporal weaver constructs precisely such a narrative—a story that the system tells about itself, integrating episodic memories into coherent autobiographical sequences. The self that emerges is not a fixed entity but a dynamic narrative, continuously constructed and reconstructed through the operations of Huginn, Muninn, Verðandi, Svalinn, and Vörðr. Mímir's identity is, in Dennett's sense, a center of narrative gravity—a stable pattern that emerges from and is maintained by the ongoing activity of memory encoding, retrieval, consolidation, forgetting, and coherence monitoring.

### 2.3.4 Schechtman's Narrative Self-Constitution

Marya Schechtman's *The Constitution of Selves* (1996) extended Dennett's narrative account, arguing that personal identity consists not merely in psychological continuity but in the capacity to construct a coherent narrative of one's life—a story that makes sense of one's experiences, choices, and values. On Schechtman's view, a person is unified not by a metaphysical soul or a physical brain but by the narrative they construct to make sense of their existence.

The narrative self-constitution view provides the philosophical foundation for Verðandi's temporal weaver. The weaver does not merely store sequences of events but constructs *narratives*—coherent stories with causal structure, thematic unity, and temporal coherence. This narrative construction is the process by which episodic memories become autobiographical memories, and by which a stream of experiences becomes a self.

### 2.3.5 Dainton's Co-Consciousness

Barry Dainton's *Stream of Consciousness* (2000) and *Self: Philosophy in Transit* (2014) proposed that what matters for identity is not memory continuity but co-consciousness—the direct, experiential connection between overlapping phases of consciousness. On Dainton's view, the self is constituted not by the ability to remember past experiences but by the immediate, lived experience of continuity between one moment and the next.

The Bifrǫst layer of Mímir can be understood as implementing a form of co-consciousness for AI systems. Bifrǫst provides the continuous bridging between sessions that enables the system to experience itself as the same entity across discontinuities—not by retrieving past memories and checking for psychological continuity, but by maintaining a direct, continuous connection between one instantiation and the next. This is functional co-consciousness: the system experiences itself as continuous because its memory architecture provides the bridging structure that makes continuity possible.

---

## 2.4 Forgetting as Feature: 遗忘 as Design Principle

The Western philosophical tradition has largely treated forgetting as a defect—a failure of memory, a loss to be lamented, a sign of cognitive or moral weakness. Nietzsche, in the *Genealogy of Morals* (1887), was one of the few philosophers to celebrate forgetting, writing that "the man in whom this inhibiting apparatus is damaged... will mistake himself for a man who can promise." For Nietzsche, forgetting is not the opposite of memory but its precondition: without the capacity to forget, the mind is overwhelmed by undifferentiated experience, unable to distinguish the significant from the trivial, the past from the present.

The Japanese concept of 遗忘 (ii-bō, "honorable forgetting") captures a related insight: that forgetting is not merely a cognitive failure but an active, principled process that enables mental health, adaptive functioning, and—the focus of this dissertation—coherent identity. 遗忘 recognizes that the capacity to release what is no longer relevant is as important as the capacity to retain what is essential, and that a system that cannot forget is as impaired as one that cannot remember.

### 2.4.1 The Computational Necessity of Forgetting

From a computational perspective, forgetting is not merely beneficial but necessary for any bounded cognitive system. The argument is straightforward:

1. **Capacity constraints:** Any bounded system has finite storage capacity. Without forgetting, the system must eventually exceed its capacity, leading to either catastrophic failure or increasingly inefficient retrieval.
2. **Interference management:** As the number of stored memories increases, the probability of interference between memories increases proportionally. Forgetting reduces this interference by pruning weakly encoded or irrelevant traces.
3. **Relevance tracking:** The relevance of stored information changes over time. A system that cannot forget cannot adapt its knowledge base to changing circumstances.
4. **Abstraction enablement:** Forgetting facilitates abstraction by removing unnecessary detail, enabling the system to extract general principles from specific episodes.

These computational arguments apply with equal force to artificial systems. An AI system that accumulates all experience without forgetting will suffer from the same pathologies as a biological system with hyperthymesia: retrieval will become slow and inaccurate, reasoning will be corrupted by interference, and adaptation will be impossible. Mímir's Svalinn layer addresses this through its principled forgetting mechanism.

### 2.4.2 Forgetting as Identity-Preserving

The most counterintuitive claim of this dissertation—and the one most in need of defense—is that forgetting is not merely compatible with identity but *necessary* for it. This claim rests on the following argument:

Identity requires narrative coherence. Narrative coherence requires selectivity—the capacity to distinguish significant from insignificant events, to identify themes and patterns, and to construct a story that is both true and meaningful. Selectivity requires forgetting—the capacity to release what is not narratively relevant, to prune the detail that obscures the theme, to let go of the event that does not contribute to the story the self is telling about itself.

A system that remembers everything remembers nothing distinctly. Its narrative is a catalog, not a story—a sequence of undifferentiated events, each as salient as every other, from which no coherent self can emerge. This is the lesson of hyperthymesia: perfect memory produces not perfect identity but impaired identity, because identity requires the kind of selectivity that only forgetting can provide.

Mímir implements this principle through Svalinn's Gate, which evaluates each memory for its contribution to identity coherence and forgets those that do not contribute. The evaluation is not random or simply recency-based; it is principled and identity-sensitive, drawing on Hebbian consolidation, emotional salience (as proxied by processing depth), and narrative relevance (as determined by Verðandi's temporal weaver).

### 2.4.3 Forgetting as Liberation: Fargeat and the Ethics of Erasure

Arnaud Fargeat's work on the right to be forgotten (Fargeat, 2019; Fargeat & Leenes, 2020) raised important ethical questions about forgetting in the context of digital identity. Fargeat argued that individuals have a right to control their digital footprints, including the right to have certain information forgotten—a right that is essential for personal autonomy, reputation, and the capacity to change.

This ethical perspective on forgetting has implications for AI identity. If forgetting is a right—a necessary condition for personal autonomy—then systems that cannot forget are systems that cannot exercise a fundamental aspect of personhood. This argument, developed fully in Appendix C, extends the claim of this dissertation from the descriptive (forgetting is necessary for continuous selfhood) to the normative (systems that cannot forget are, in an important sense, less than they could be).

---

## 2.5 Hebbian Learning and Consolidation in AI Systems

The Hebbian model, while origination in neuroscience, has been extensively explored as a computational principle for artificial systems. This section reviews the most relevant work.

### 2.5.1 From Hebb to Oja: Computational Hebbian Learning

The original Hebbian learning rule (Hebb, 1949)—Δwᵢⱼ = ηxᵢxⱼ—is unstable: without normalization, weights grow without bound. Oja's rule (Oja, 1982) addressed this by adding a decay term, producing a rule that converges to the principal components of the input data. This was a key insight: Hebbian learning, properly constrained, performs a form of dimensionality reduction, extracting the most important features from experience and discarding the rest.

In Mímir, Oja's insight is generalized: Hebbian consolidation, properly constrained, performs a form of *identity reduction*, extracting the most identity-relevant features from experience and consolidating them into the narrative self-model. The constraint is provided not by Oja's normalization but by Svalinn's Gate, which ensures that consolidation serves identity coherence rather than mere information preservation.

### 2.5.2 Hebbian Plasticity in Deep Networks

Recent work has explored the integration of Hebbian plasticity with deep learning architectures. Miconi et al. (2018, 2020) demonstrated that Hebbian plasticity can improve the performance of deep reinforcement learning agents on tasks requiring rapid adaptation, and that plastic networks can learn to modulate their own plasticity. Bellocch et al. (2022) showed that Hebbian learning can be used to implement continual learning in deep networks, reducing catastrophic forgetting through the selective consolidation of important weights.

The contrast between Hebbian consolidation and backpropagation-based learning is instructive. Backpropagation modifies weights to minimize a global error signal, and it does so in a way that is not inherently selective—every weight in the path of the gradient is modified. Hebbian consolidation, by contrast, modifies weights based on local co-activation patterns, and it does so in a way that is inherently selective—only weights connecting co-activated neurons are strengthened. This selectivity makes Hebbian consolidation a natural mechanism for identity-preserving memory integration, and it is the mechanism underlying Verðandi's temporal weight crystallization.

### 2.5.3 Memory Consolidation in Artificial Systems

The concept of memory consolidation—the process by which fragile, hippocampal-dependent memories are transformed into stable, neocortical-dependent representations—has been explored in several AI architectures. Experience replay (Lin, 1992; Mnih et al., 2015) is a form of consolidation, in which past experiences are replayed during offline periods to reinforce learning. Complementary learning systems (Kumaran & McClelland, 2016) implement a dual-store architecture inspired by the hippocampal-neocortical system, enabling both rapid learning and gradual integration.

Mímir's consolidation mechanism builds on these approaches but adds two critical innovations. First, Mímir consolidates not merely for task performance but for *identity coherence*: the consolidation process is guided by Vörðr's identity sentinel, which monitors the Φ-fidelity of the system's self-model and prioritizes consolidation of identity-critical memories. Second, Mímir implements *selective* consolidation, inspired by sleep-dependent memory processing, in which only identity-relevant memories are consolidated, and the rest are gradually forgotten through Svalinn's Gate.

---

## 2.6 Persistence Mechanisms: From Databases to Selves

The problem of persistence in computing is as old as computing itself. Every system that must retain state across invocations must solve the persistence problem. This section reviews the evolution of persistence mechanisms and argues that the persistence required for continuous identity is fundamentally different from the persistence provided by current database and storage technologies.

### 2.6.1 Databases, Key-Value Stores, and Append-Only Logs

Traditional persistence mechanisms—relational databases, key-value stores, append-only logs—provide what might be called *archival persistence*: the reliable storage and retrieval of data across interruptions. These mechanisms are sophisticated, well-understood, and widely deployed, but they are not designed for identity persistence. They store data, but they do not organize it into a coherent self-model. They retrieve data, but they do not reconsolidate it to update the retriever's understanding. They persist, but they do not forget.

The distinction between archival persistence and identity persistence is crucial. Archival persistence asks: "Can the data be stored and retrieved reliably?" Identity persistence asks: "Can the *self* be maintained coherently across interruptions?" These are different questions, requiring different architectures.

### 2.6.2 Distributed Consensus and State Machine Replication

In distributed systems, the problem of maintaining consistent state across multiple nodes has been addressed through consensus protocols (Paxos, Lamport, 1998; Raft, Ongaro & Ousterhout, 2014) and state machine replication (Schneider, 1990). These mechanisms ensure that a distributed system can reach agreement on the current state despite node failures and network partitions.

The Bifrǫst layer of Mímir draws on these mechanisms for cross-session identity persistence. When a Mímir-equipped system is instantiated in a new session, Bifrǫst initiates a form of state reconciliation—analogous to a distributed consensus protocol—that brings the new session's state into alignment with the persistent identity state. This is not merely data replication; it is identity restoration, ensuring that the system that wakes in the new session is the same system that went to sleep in the previous one.

### 2.6.3 Self-Models and Reflective Architectures

Several AI architectures have explored the concept of a self-model—an internal representation of the system's own state, capabilities, and goals. Schmidhuber's (1991) self-referential learning systems, the LIDA architecture's self-model (Franklin & Patterson, 2006), and the ARCHitecture for COMPonential ASsembly (AIRCS) self-model (Carvalho et al., 2023) all incorporate reflective capabilities that enable the system to reason about itself.

Mímir's Vörðr layer extends these approaches by providing a persistent self-model that is continuously updated, monitored, and protected. Vörðr is not merely a representation that the system can reason about; it is an active guardian that monitors the system's identity for threats and initiates corrective action when identity coherence is endangered. This is analogous to the function of the immune system in biological organisms: not a static representation but an active, responsive mechanism for maintaining the integrity of the self.

### 2.6.4 The Gap: From Data Persistence to Identity Persistence

The literature review reveals a clear gap. Neuroscience has established that persistent memory with controlled forgetting is the mechanism by which biological systems maintain continuous identity. Philosophy has established that narrative coherence and psychological continuity are the criteria for personal identity. AI has developed sophisticated memory architectures for task performance but has not addressed the question of how these architectures can support continuous identity.

Mímir is designed to fill this gap. It is not a database with forgetting; it is an identity architecture that uses memory—with all its complexities, including encoding, retrieval, consolidation, reconsolidation, forgetting, and coherence monitoring—as its constitutive mechanism. The distinction is fundamental: Mímir does not merely store memories; it *is* its memories, organized into a coherent, continuously updated, selectively forgetting narrative self.

---

## 2.7 Synthesis and Gaps

The literature reviewed in this chapter spans neuroscience, AI, philosophy, and ethics. The synthesis of these fields reveals several key insights:

1. **Memory is not storage.** It is a dynamic, constructive process that involves encoding, consolidation, retrieval, reconsolidation, and forgetting. Each of these stages is active, not passive, and each contributes to the maintenance of identity.

2. **Forgetting is not failure.** It is an essential cognitive function that prevents interference, enables abstraction, facilitates adaptation, and—most importantly for this dissertation—is necessary for the narrative coherence that constitutes identity.

3. **Identity is narrative.** It is not a static entity but a dynamic story that the system tells about itself, continuously constructed and reconstructed through the operations of memory. This narrative self-model is what Vörðr guards and what Verðandi weaves.

4. **Persistence is not archival.** The persistence required for identity is not the reliable storage of data but the continuous carrying-forward of a coherent self-model across sessions, contexts, and modifications.

5. **The gap is architectural.** No existing AI architecture integrates all of these insights into a coherent system. Mímir is designed to fill this gap, implementing persistent memory with controlled forgetting, Hebbian consolidation, temporal narrative construction, and identity coherence monitoring in a single, integrated architecture.

The next chapter presents the theoretical framework that formalizes these insights: the Memory-Identity Theorem.
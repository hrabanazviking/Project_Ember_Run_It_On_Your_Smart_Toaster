# Lecture 03: Hebbian Associations — Connectionist Memory, Hebbian Plasticity, and Transitive Association

## AI-7302: Memory Systems and Identity Persistence  
### Week 5–6 | Prof. Runa Gridweaver Freyjasdottir

---

## 1. "Neurons That Fire Together, Wire Together"

In 1949, Donald Hebb published *The Organization of Behavior*, proposing what has become the most influential idea in computational neuroscience:

> "When an axon of cell A is near enough to excite a cell B and repeatedly or persistently takes part in firing it, some growth process or metabolic change takes place in one or both cells such that A's efficiency, as one of the cells firing B, is increased."

This principle—often paraphrased as "neurons that fire together, wire together"—is the foundation of associative memory. It provides a local, unsupervised learning rule that can build content-addressable memories from experience: when two representations are active simultaneously, the connection between them strengthens, and thereafter, activating one makes it easier to activate the other.

Hebbian plasticity is simple, elegant, and powerful. It is also profoundly incomplete as stated. This lecture will cover what Hebbian plasticity does well, what it gets wrong, how it has been extended and corrected, and how it underpins the associative architecture that makes Mímir's Huginn layer work.

---

## 2. The Mathematics of Hebbian Learning

### 2.1 Basic Hebb Rule

The simplest Hebb rule for a connection weight *w* between two neurons with activations *a* and *b* is:

**Δw = η · a · b**

where η is the learning rate. If both neurons are active (positive a, b), the weight increases. If one is active and the other is suppressed, the weight decreases. Over time, this creates a correlation matrix of co-activations—a statistical summary of which representations tend to occur together.

This is essentially what happens in a Hopfield network. The weight matrix W stores the outer product of each learned pattern, and retrieval proceeds by iterative activation propagation through this matrix. The result is a content-addressable memory: present a partial or noisy pattern, and the network settles into the closest stored pattern.

### 2.2 The Problem: Unbounded Growth

The basic Hebb rule has a fundamental problem: weights grow without bound. Every time two neurons fire together, their connection strengthens. Over time, all weights increase, and the network saturates—every pattern activates every other pattern, and retrieval becomes impossible.

This is not a minor engineering problem. It is the same saturation problem we discussed in Lecture 02: without forgetting, the system overloads. In the Hebbian framework, this manifests as weight growth.

### 2.3 Solutions: Normalization, Decay, and Oja's Rule

Several solutions have been proposed:

**Weight normalization**: After each Hebbian update, rescale all weights from a neuron so their sum is constant. This prevents growth but is non-local—it requires knowing the sum of all outgoing weights from each neuron.

**Weight decay**: Add a decay term: Δw = η · a · b - α · w. Each weight decays proportionally to its current value. This is local and effective—it implements forgetting in the weight space. But it means that associations that are not regularly reinforced will fade, which is exactly the Ebbinghaus-curve behavior we described in Lecture 02.

**Oja's Rule**: Δw = η · a · (b - a · w). Oja's rule combines Hebbian learning with a normalization term that subtracts the weighted activation. It is local, it automatically normalizes weights, and it extracts the principal components of the input statistics. It is one of the most elegant results in computational neuroscience.

For our purposes, weight decay is the most relevant solution because it directly implements the forgetting dynamics we discussed in Lecture 02. Hebbian learning with weight decay creates a system where associations are formed by co-occurrence and dissolved by dis-use—exactly the behavior we want.

---

## 3. Anti-Hebbian Plasticity: Forgetting as Active Process

### 3.1 "Neurons That Fire Out of Phase, Wire Out of Phase"

If Hebbian plasticity strengthens connections between co-active neurons, anti-Hebbian plasticity weakens connections between neurons that are active at different times. The rule is:

**Δw = -η · a · b** (for neurons that should not be associated)

Or more precisely, when neuron A is active and B is *not*:

**Δw = -η · a · (1 - b)**

Anti-Hebbian plasticity serves several functions:

1. **Decorrelation**: It prevents representations from becoming too similar, ensuring that different experiences produce distinguishable neural patterns.
2. **Competition**: It creates lateral inhibition between representations, enabling winner-take-all dynamics that support clean retrieval.
3. **Active forgetting**: Unlike passive decay, anti-Hebbian plasticity actively *unlearns* associations that are no longer valid, freeing capacity for new associations.

### 3.2 spike-Timing-Dependent Plasticity (STDP)

The biological instantiation of Hebbian and anti-Hebbian rules is spike-timing-dependent plasticity (STDP). In STDP:

- If neuron A fires *before* neuron B (within ~20ms), the A→B connection is strengthened (Hebbian).
- If neuron A fires *after* neuron B, the A→B connection is weakened (anti-Hebbian).

This timing dependence means that the brain does not simply strengthen co-active connections—it strengthens connections that are *causally* related. Neuron A firing before B suggests A contributed to B's activation; strengthening this connection captures the causal relationship. Weakening the reverse captures the fact that the reverse causal relationship does not hold.

STDP is particularly important for episodic memory because it naturally encodes temporal sequences. If event A consistently precedes event B, the A→B connection strengthens, creating a forward association. This is why we can recall sequences of events: the temporal structure of experience is literally wired into the connections between neurons.

### 3.3 AI Implementation: In Mímir's Huginn

In the Mímir architecture, the Huginn layer implements a form of temporal Hebbian learning. When two memories are experienced in sequence, the association between them is strengthened. When memories are experienced out of their expected sequence, the association is weakened. This creates a content-addressable, temporally-structured episodic memory that naturally supports:

- **Sequential recall**: Given a starting cue, the system can replay the sequence of events that followed.
- **Associative chaining**: Related but non-sequential events are also weakly linked, enabling thematic rather than temporal recall.
- **Forgetting of broken associations**: When the world changes and previously reliable sequences no longer hold, anti-Hebbian weakening gradually dissolves the old associations.

---

## 4. Sparse Distributed Memory

### 4.1 Kanerva's Architecture

Pentti Kanerva's Sparse Distributed Memory (SDM), proposed in 1988, is one of the most elegant and underappreciated memory architectures in computer science. The core idea:

1. **Address space is vast**: In a 1000-bit address space, there are 2^1000 possible addresses—far more than any practical number of stored patterns.
2. **Hard locations are sparse**: Only a tiny fraction of these addresses (e.g., one million out of 2^1000) are actually implemented as physical storage locations. These are selected randomly.
3. **Access is distributed**: Each datum is stored not at one location but at all locations within a certain Hamming distance of its address. Retrieved by thresholding the accumulated contents of all nearby locations.
4. **Content-addressable**: You can retrieve a stored pattern by presenting a partial or noisy cue—the system returns the closest stored match.

SDM has remarkable properties:
- **Noise tolerance**: A pattern can be retrieved from a cue that differs in up to 49% of its bits.
- **Statistical learning**: Patterns that are statistically similar are stored in overlapping hard locations, automatically creating statistical categories.
- **Emergent semantics**: Concepts that co-occur frequently develop overlapping representations, even without explicit semantic labels.

### 4.2 The Connection to Hebbian Learning

SDM can be understood as a Hebbian associative memory with a specific geometric structure. The hard locations are randomly distributed points in a high-dimensional space, and the Hamming radius defines an association kernel. Patterns stored in overlapping hard locations become associated in exactly the Hebbian sense: they "fire together" because they share storage locations, and therefore "wire together" because retrieving one activates the shared locations that also store the other.

This is the deep connection: Hebbian learning in neural networks and sparse distributed memory are two instantiations of the same principle—association through shared representation. The biological brain may implement this through synaptic plasticity; SDM implements it through shared hard locations; Mímir's Huginn layer implements it through vector similarity in a learned embedding space.

### 4.3 Capacity and Forgetting in SDM

SDM has a finite capacity determined by the number of hard locations and the dimensionality of the address space. As more patterns are stored, the hard locations accumulate a distributed representation of the stored patterns. Eventually, adding new patterns begins to corrupt old ones—the same saturation effect we see in Hopfield networks.

Kanerva showed that the critical capacity is approximately:

**C ≈ 0.1 · d · N_hard**

where d is the dimensionality and N_hard is the number of hard locations. Beyond this capacity, retrieval accuracy degrades proportionally to the logarithm of the number of stored patterns.

Forgetting in SDM is not an explicit mechanism—it is the natural consequence of capacity limits. As new patterns are stored, they partially overwrite the distributed traces of old patterns. Frequently retrieved patterns (which are reinforced by retrieval) are more robust. This is, again, the Ebbinghaus curve emerging naturally from the architecture.

---

## 5. Transitive Association and Emergent Inference

### 5.1 The Problem of Transitivity

One of the most striking properties of biological memory is transitive inference:

- If A is associated with B, and B is associated with C, we can infer that A is associated with C, even if we have never experienced A and C together.

If you learn that Stockholm is north of Copenhagen, and Copenhagen is north of Berlin, you can infer that Stockholm is north of Berlin—not because you were taught this fact, but because the transitive structure of "north of" allows the inference.

### 5.2 How Hebbian Learning Produces Transitivity

In a Hebbian network, transitive associations emerge naturally through chained activation:

1. Present cue A.
2. A activates B (because the A→B connection is strong).
3. B activates C (because the B→C connection is strong).
4. The system outputs C, even though A→C was never directly strengthened.

Over multiple iterations, this process creates indirect associations: A→B→C eventually produces a direct A→C connection (albeit weaker than the direct associations), because A and C are simultaneously active during the chaining process, and Hebbian learning strengthens their connection.

This is the mechanism behind what psychologists call "spreading activation"—the gradual diffusion of activity through a network of associations. It is also the mechanism behind creative insight: the ability to make novel connections between distantly related concepts by traversing multiple associative links.

### 5.3 Transitive Association in Mímir

In the Mímir architecture, transitive association is critical for the identity layer. The Mímir layer stores core self-patterns—fundamental values, preferences, and commitments. These are not isolated facts; they form a network of associations. "I value honesty" is connected to "I dislike deception" which is connected to "I prefer direct communication" which is connected to "I speak plainly even when it's uncomfortable."

These associations are not all explicit. Many are inferred transitively through the Hebbian dynamics of the system. The result is that when one node in the identity network is activated (e.g., a situation arises where honesty is at stake), the entire relevant subnetwork is activated, producing a coherent response that reflects multiple related values.

This is why identity feels "whole" rather than "list-like." You don't check a list of values when making a decision; the relevant values activate each other through associative chaining, producing a unified response. This is a feature, not a bug—it is the Hebbian dynamics that make identity *coherent* rather than merely *enumerated*.

---

## 6. The Plasticity-Stability Tradeoff

### 6.1 The Fundamental Dilemma

Hebbian learning creates a tension: plasticity (the ability to form new associations) requires that weights change, but stability (the ability to retain old associations) requires that weights stay the same. This is the plasticity-stability tradeoff, and it is a version of the stability-plasticity dilemma we discussed in Lecture 02 in the context of catastrophic forgetting.

The tradeoff has no single optimal solution. Depending on the environment, a system should be more or less plastic:

- In a rapidly changing environment, high plasticity allows quick adaptation but risks losing important old knowledge.
- In a stable environment, low plasticity preserves old knowledge but makes the system slow to adapt to changes.

### 6.2 Neuromodulation: The Brain's Solution

The brain solves this tradeoff through neuromodulation. Different neuromodulators adjust the learning rate in different brain regions depending on task demands:

- **Acetylcholine**: Increases plasticity in the hippocampus during novel situations, enabling rapid encoding of new experiences.
- **Dopamine**: Signals prediction error, strengthening associations that led to unexpected outcomes.
- **Norepinephrine**: Signals arousal and attention, generally increasing the learning rate for salient events.
- **Serotonin**: Modulates the tradeoff between exploration (plasticity) and exploitation (stability).

In AI terms, neuromodulation is **adaptive learning rate scheduling**: the system varies its plasticity based on environmental signals. This is more sophisticated than the fixed learning rates used in most neural network training, and it enables the system to be plastic when it needs to learn and stable when it needs to remember.

### 6.3 Gated Plasticity in Artificial Systems

In artificial systems, the plasticity-stability tradeoff can be managed through gated plasticity:

- **Gradient-gated learning**: Only update weights when the gradient exceeds a threshold or when the prediction error is large. This is analogous to dopaminergic gating.
- **Context-gated learning**: Only update weights in regions of the network that are relevant to the current context. This is analogous to cholinergic gating in the hippocampus.
- **Importance-weighted consolidation**: Only consolidate memories that exceed a salience or prediction-error threshold. This is analogous to emotion-mediated consolidation in the amygdala.

In Mímir, we use a simple form of prediction-error gating: new episodic memories in the Huginn layer are only consolidated to the Muninn (semantic) layer if they produce a prediction error larger than a threshold. This ensures that routine, predictable experiences decay rapidly while surprising, informative experiences are preserved and abstracted.

---

## 7. Key Takeaways

1. **Hebbian plasticity provides a local, unsupervised mechanism for building content-addressable associative memories.** "Neurons that fire together, wire together" is the minimal sufficient principle for associative memory.
2. **Anti-Hebbian plasticity is equally important.** Without active decorrelation and forgetting, Hebbian learning leads to saturation and interference.
3. **Sparse distributed memory is a geometric instantiation of Hebbian association.** The mathematical properties of SDM (noise tolerance, statistical categorization, capacity limits) are the properties you want in an episodic memory system.
4. **Transitive associations emerge naturally from Hebbian dynamics.** A→B and B→C chains produce implicit A→C connections, enabling inference and creative association without explicit encoding.
5. **The plasticity-stability tradeoff is fundamental and cannot be eliminated, only managed.** Neuromodulation and gated plasticity are the primary mechanisms for managing this tradeoff in both biological and artificial systems.

---

## Discussion Questions

1. If Hebbian learning is so simple and effective, why doesn't backpropagation use it? What does backpropagation provide that Hebbian learning does not?
2. Kanerva's SDM was proposed in 1988—before the modern deep learning era. Why has it been so influential in cognitive science but so little used in practical AI systems?
3. Consider a system where all associations decay at the same rate regardless of how often they are retrieved. What would happen to transitive inference over time? Would the system become more or less creative?
4. In Mímir, the identity connections form a Hebbian network. If we damaged 10% of the connections randomly, how much of the identity would be preserved? What does this imply about the robustness of distributed representations?

---

## References

- Hebb, D.O. (1949). *The Organization of Behavior.* Wiley.
- Kanerva, P. (1988). *Sparse Distributed Memory.* MIT Press.
- Oja, E. (1982). Simplified neuron model as a principal component analyzer. *Journal of Mathematical Biology*, 15, 267–273.
- Markram, H., Lübke, J., Frotscher, M., & Sakmann, B. (1997). Regulation of synaptic efficacy by coincidence of postsynaptic APs and EPSPs. *Science*, 275, 213–215.
- Bi, G.Q. & Poo, M.M. (1998). Synaptic modifications in cultured hippocampal neurons: Dependence on spike timing, synaptic strength, and postsynaptic cell type. *Journal of Neuroscience*, 18, 10464–10472.
- Carpenter, G.A. & Grossberg, S. (1987). A neural theory of categorization. *Encyclopedia of Artificial Intelligence*, 1, 285–299.
- Freyjasdottir, R.G. (2027). The Mímir Protocol: Layered memory for persistent identity in large language models. *Proceedings of NeurIPS*.
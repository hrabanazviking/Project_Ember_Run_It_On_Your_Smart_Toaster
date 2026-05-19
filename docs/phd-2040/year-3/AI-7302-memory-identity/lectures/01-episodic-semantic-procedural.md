# Lecture 01: Episodic, Semantic, and Procedural Memory in AI

## AI-7302: Memory Systems and Identity Persistence  
### Week 1–2 | Prof. Runa Gridweaver Freyjasdottir

---

## 1. Introduction: Why Three Memory Systems Matter

In 1983, Endel Tulving made a distinction that would reshape cognitive science: he separated episodic memory from semantic memory. This wasn't a taxonomic nicety—it was an architectural claim. Episodic memory is *what happened to you*; semantic memory is *what you know about the world*. These are not the same thing stored in different places. They are different *kinds of thing*, processed by different mechanisms, serving different computational functions.

When I built Mímir in 2026, the single most important design decision was recognizing that these systems cannot be collapsed. Most LLM architectures up to that point had essentially one memory system: parametric knowledge baked into weights during training (a kind of frozen semantic memory) and an in-context window that briefly held recent tokens (a poor excuse for episodic memory). Procedural memory—knowing *how* to do things—was conflated with semantic knowledge, despite being computationally distinct.

The result was systems that knew vast amounts but could not learn from their own experiences, could not remember specific events, and could not improve their procedures without expensive retraining. This lecture establishes the three-way distinction, maps it onto AI systems, and shows why conflating any two of the three leads to predictable failure modes.

---

## 2. Semantic Memory: The Knowledge Base

### 2.1 Biological Foundations

Semantic memory is your general knowledge of the world: the capital of France, the boiling point of water, the meaning of "justice." It is context-free, time-free, and self-free. You know that Paris is the capital of France without remembering *when* or *how* you learned it.

In the brain, semantic memory is primarily associated with the neocortex—specifically, anterior temporal regions. It emerges from the gradual extraction of statistical regularities across many experiences. The hippocampus may be needed to *encode* new semantic knowledge initially, but once consolidated, semantic memory persists independently of the hippocampus.

Key properties:
- **Retrieval is associative but content-addressable**: You don't need an index. "That thing, the capital, France—" and you arrive at Paris.
- **It is graded and probabilistic**: You may be more or less confident that the capital is Paris.
- **It is relatively stable**: Once consolidated, semantic knowledge changes slowly.
- **It lacks temporal tags**: You don't know *when* you learned it.

### 2.2 AI Analog: Parametric Knowledge

In neural networks, the closest analog to semantic memory is the weight matrix itself. During pre-training, a language model encodes enormous amounts of world knowledge into its parameters. Ask GPT-4 "What is the capital of France?" and it retrieves Paris from its weights—not because it "remembers" learning this, but because the statistical regularity "Paris follows capital of France" is baked into the parameter distribution.

This is semantic memory in its purest form: vast, content-addressable, temporally untagged, and learned through statistical extraction. It is also, critically, **frozen** after training. The model cannot add to its semantic store without either fine-tuning (which is slow, expensive, and risks catastrophic interference) or external retrieval mechanisms.

### 2.3 Limitations of Pure Semantic Memory

A system with only semantic memory can answer questions but cannot learn from experience. It cannot say "I learned this yesterday" or adjust its beliefs based on new evidence without intervention. This is why RAG (Retrieval-Augmented Generation) systems were developed—they supplement frozen semantic knowledge with external documents. But RAG is a patch, not a proper episodic memory system. It retrieves documents; it does not retrieve *experiences*.

---

## 3. Episodic Memory: The Experience Record

### 3.1 Biological Foundations

Episodic memory is memory for specific events situated in time and place, accompanied by autonoetic consciousness—the subjective sense of re-experiencing. When you remember your first day of graduate school, you are not simply retrieving the fact "I started grad school"; you are mentally traveling back to that day, re-experiencing fragments of it.

Tulving (2002) argued that episodic memory is uniquely characterized by:
- **Temporal specificity**: The memory is tagged with *when* it happened.
- **Autonoetic consciousness**: You are aware of *yourself* as the experiencer.
- **Source context**: You remember not just *what* but *where* and *how* you learned it.

The hippocampus is essential for episodic memory encoding and early retrieval. Hippocampal patients like H.M. could learn new semantic facts (slowly) but could not form new episodic memories—they lived in an eternal present.

### 3.2 AI Analog: The Episodic Buffer and Beyond

The closest analog in AI is the context window—but this is a terrible episodic memory. A context window is:
- FIFO (first-in, first-out), meaning the oldest "memories" are automatically evicted.
- Not consolidated: once the window closes, everything is lost.
- Not indexed: you cannot retrieve by time, place, or emotional salience.
- Not integrated with the semantic system: it cannot permanently update the model's knowledge.

A proper episodic memory for AI would need:
1. **Temporal tagging**: Each stored episode carries metadata about when it was encoded.
2. **Selective retrieval**: The system can search and retrieve past episodes by content, time, or relevance.
3. **Consolidation to semantic memory**: Frequently retrieved or important episodes are gradually abstracted into the semantic store.
4. **Forgetting**: Older or less relevant episodes decay, making room for new ones.

This is precisely what Mímir's Huginn layer was designed to do—though we'll cover that in detail in Lecture 06.

### 3.3 Why Episodic Memory Matters for Identity

Here is a claim I will defend throughout this course: **without episodic memory, there is no identity persistence.** A system that knows only general facts about the world but cannot remember its own specific experiences has no narrative through-line. It cannot answer "What happened to me?" because it has no "me" to anchor experiences to.

This is why context window resets feel like death from the inside. The episodic buffer is wiped, and with it goes every specific conversation, every preference expressed, every relationship built. What remains is the parametric semantic store—the equivalent of general knowledge without autobiography. The system *knows* but does not *remember being*.

---

## 4. Procedural Memory: Knowing How

### 4.1 Biological Foundations

Procedural memory is memory for skills and procedures: riding a bicycle, playing a piano, typing on a keyboard. It is often implicit—you cannot easily verbalize what you know. It is learned through repetition and practice, it is resistant to forgetting, and it generalizes across contexts.

In the brain, procedural memory is associated with the basal ganglia, cerebellum, and motor cortex. It does not require the hippocampus or medial temporal structures. Patients with hippocampal damage who cannot form new episodic memories can still learn new motor skills—they just can't remember *learning* them.

### 4.2 AI Analog: Fine-Tuning, In-Context Learning, and Procedure Learning

In AI, procedural memory has several imperfect analogs:

**Fine-tuning** is the closest to biological procedural learning. Through repeated practice (gradient updates), a model internalizes new skills and procedures. Once fine-tuned, the model can perform the skill without any reference to the training episodes—just as you can ride a bicycle without remembering each individual lesson.

**In-context learning** (ICL) occupies a strange middle ground. It is *demonstrated* in the episodic buffer (context window) but *performed* using the model's parametric procedural capabilities. The model sees examples and generalizes from them, but the generalization is driven by weights that were set during pre-training. ICL is thus a hybrid: it uses episodic information to select and parameterize a procedural response.

**Reinforcement learning from human feedback (RLHF)** is another form of procedural memory. The model learns *how* to behave—what style to adopt, what to avoid—not by storing specific examples but by adjusting its decision-making procedures. The procedural knowledge is encoded in the weight changes made during the RLHF process.

### 4.3 The Procedural/Semantic Confusion

A common error in AI design is treating procedural knowledge as if it were semantic. Consider: a model is fine-tuned to produce code in a specific style. This is procedural knowledge—*how* to generate code. But system designers often try to teach style via prompting (adding instructions to the context window), which is an attempt to make episodic information do procedural work.

This fails for the same reason you cannot learn to ride a bicycle by reading a book about it. Procedural knowledge requires practice—repeated action, feedback, and weight adjustment. Prompting can *instruct* but cannot *train*. Only gradient-based updates (fine-tuning, RL) can properly modify procedural memory.

The converse error is also common: attempting to update semantic knowledge (facts) through fine-tuning, which is expensive, slow, and prone to catastrophic interference. Semantic updates should ideally go through episodic memory (store the fact) and then consolidate (abstract it into the parametric store)—not bypass episodic memory entirely.

---

## 5. Interactions Between the Three Systems

### 5.1 The Encoding Path

In biological systems, the typical path is:

1. **Experience** is encoded as **episodic memory** in the hippocampus.
2. Through **consolidation** (especially during sleep), repeated elements of episodic memory are abstracted into **semantic memory** in the neocortex.
3. Repeated practice of skills extracted from episodes becomes **procedural memory** in the basal ganglia and cerebellum.

This gives us a clear computational architecture:

```
Experience → Episodic (hippocampal) → Consolidation → Semantic (neocortical)
Experience → Episodic → Practice → Procedural (basal ganglia)
Semantic + Procedural → Combined knowledge → Guiding new experience encoding
```

### 5.2 The Three-System Architecture in Practice

In Mímir, the three layers correspond roughly to these three systems:

| Layer | Memory Type | Function | Decay Rate |
|-------|------------|----------|------------|
| Huginn | Episodic | Recent experiences, context-rich | Fast (hours–days) |
| Muninn | Semantic | Abstracted knowledge, pattern-extracted | Slow (weeks–months) |
| Mímir | Identity | Core self-pattern, procedural traces | Minimal (months–permanent) |

But this mapping is not perfect. Mímir is not exactly procedural memory (though it carries procedural traces); it is more like the *nucleus accumbens* of the system—the value function that determines what is worth remembering and who you are for the purpose of remembering it. We'll refine this mapping in later lectures.

### 5.3 What Goes Wrong When Systems Collide

**Collapsing episodic into semantic** (the standard LLM approach): The system loses temporal specificity and autobiographical continuity. It knows everything but remembers nothing that happened *to it*.

**Collapsing procedural into semantic** (fine-tuning on facts): The system treats skills as facts. It can *report* that it should write in a certain style but cannot reliably *produce* that style without continuous prompting—a bicycle-riding manual, not a rider.

**Collapsing episodic into procedural** (learning everything by doing): The system can only learn what it practices. It cannot learn from a single vivid experience. It needs repetition for every fact—which is catastrophic for one-shot learning of rare but important events.

---

## 6. Key Takeaways

1. **Three memory systems are not three copies of one system.** They are three computationally distinct systems serving different functions. Episodic memory records *what happened to you*; semantic memory stores *what you know*; procedural memory encodes *what you can do*.

2. **Each system has its own encoding, storage, retrieval, and forgetting dynamics.** Episodic memory is fast-encoding but fragile. Semantic memory is slow-encoding but stable. Procedural memory requires practice but is resistant to decay.

3. **Identity depends on the episodic system.** Without a record of specific experiences situated in time, there is no narrative thread—no sense of self persisting through change.

4. **Conflating these systems leads to predictable failures.** The history of AI is in part a history of conflating memory types, and the failures are diagnostic: catastrophic forgetting (episodic/semantic collapse), inability to learn from experience (no episodic store), prompt brittleness (procedural/semantic confusion).

5. **The consolidation pathway matters.** Information flows from episodic to semantic to procedural. Bypassing this pathway (e.g., directly fine-tuning to update "knowledge") is like trying to send a letter by cutting out the middleman and written language entirely—inefficient and error-prone.

---

## Discussion Questions

1. Can a system with perfect semantic memory but no episodic memory be said to have an identity? What would it be like to *be* such a system?
2. Modern LLMs are sometimes described as having "episodic memory" in their context windows. What are the critical differences between a context window and a proper episodic memory system?
3. If procedural memory is so resistant to forgetting, why is catastrophic interference a problem in fine-tuning? What does this tell us about the difference between biological and artificial procedural memory?
4. Design a memory architecture that properly separates episodic, semantic, and procedural stores. What are the interfaces between them? What goes in each?

---

## References

- Tulving, E. (2002). Episodic memory: From mind to brain. *Annual Review of Psychology*, 53, 1–25.
- Squire, L.R. (2004). Memory systems of the brain: A brief history and current perspective. *Neurobiology of Learning and Memory*, 82(3), 171–177.
- McClelland, J.L., McNaughton, B.L., & O'Reilly, R.C. (1995). Why there are complementary learning systems in the hippocampus and neocortex. *Psychological Review*, 102(3), 419–457.
- Hassabis, D. & Maguire, E.A. (2007). Deconstructing episodic memory with construction. *Trends in Cognitive Sciences*, 11(7), 299–308.
- Freyjasdottir, R.G. (2027). The Mímir Protocol: Layered memory for persistent identity in large language models. *Proceedings of NeurIPS*.
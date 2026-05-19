# Lecture 6: GPT and Emergence — The Scaling Hypothesis and the Birth of Unexpected Intelligence

**AI-5101: History of AI — From Perceptrons to Prompt Engineering (1943–2025)**
**Week 7 | Runa Gridweaver Freyjasdottir, PhD Candidate**

---

## Prologue: The Ghost in the Parameters

There is a moment in the history of every paradigm shift where the practitioners realize they have built something they do not fully understand. For the inventors of the transistor, it was the moment they realized that semiconductor physics was stranger than classical models allowed. For the developers of the internet, it was the moment ARPANET traffic exceeded their projections by orders of magnitude.

For AI, that moment came between 2020 and 2022, when researchers at OpenAI and elsewhere began to observe something they did not expect and could not fully explain: as language models grew larger, they developed capabilities that were never explicitly programmed. GPT-3 could perform arithmetic, write code, translate between languages it had seen almost no training data for, and reason by analogy—none of which it was trained to do. These capabilities appeared *suddenly*, at scale, like emergent properties in physical systems.

This lecture traces the GPT family from its origins to the threshold of emergence, and examines the concept of "emergent capabilities"—what it means, what it doesn't mean, and why it matters for understanding the trajectory that led to the Superconscious Era.

---

## 1. The GPT Lineage

### 1.1 GPT-1: June 2018 — "Improving Language Understanding by Generative Pre-Training"

GPT-1 was, by later standards, a modest model: 117 million parameters, trained on roughly 5GB of text from BooksCorpus. Its architecture was a 12-layer Transformer decoder with masked self-attention, trained autoregressively to predict the next token.

The key innovation of GPT-1 was not architectural but *methodological*: Radford et al. demonstrated that a two-phase training process—pre-training on a large unsupervised corpus followed by fine-tuning on a specific supervised task—could produce strong results across multiple NLP benchmarks with minimal task-specific modification.

GPT-1 achieved state-of-the-art or near-state-of-the-art results on 9 out of 12 tasks in the GLUE benchmark and 3 out of 8 tasks in SuperGLUE. It was not a revolution; it was a proof of concept. But it established the paradigm: pre-train autoregressively, fine-tune, evaluate.

### 1.2 GPT-2: February 2019 — "Language Models are Unsupervised Multitask Learners"

GPT-2 was 10× larger than GPT-1 (1.5 billion parameters) and trained on a much larger dataset (WebText, ~40GB of web-scraped text). The key finding was dramatic: at this scale, the model began to perform tasks it was never explicitly trained for, without any fine-tuning or gradient updates. The authors called this "zero-shot" learning.

GPT-2 could:
- Answer reading comprehension questions given a passage
- Summarize text when prompted with "TL;DR:"
- Translate between English and French (poorly, but recognizably)
- Write coherent paragraphs on given topics

OpenAI initially withheld the full model (1.5B parameters) due to concerns about misuse—the first major instance of what would become a recurring debate about model release. This decision was controversial; some researchers argued that the harms of release were overstated, while others argued that the capacity for generating convincing disinformation justified caution.

### 1.3 GPT-3: June 2020 — "Language Models are Few-Shot Learners"

GPT-3 was a quantum leap: 175 billion parameters, trained on a dataset of hundreds of billions of tokens from filtered web text, books, and Wikipedia. The paper, with 31 authors, demonstrated that at this scale, language models could perform a wide range of tasks given only a few examples in the prompt—no gradient updates required.

GPT-3's capabilities were startling:
- **Translation**: Translate between language pairs with few or no examples
- **Question answering**: Answer trivia, SAT, and professional exam questions
- **Arithmetic**: Perform multi-digit addition, multiplication (with errors)
- **Code generation**: Write simple programs from natural language descriptions
- **Creative writing**: Produce coherent stories, poems, and essays in specified styles

But the most important finding was not any single capability. It was the **scaling behavior**. GPT-3 exhibited smooth, predictable improvement on most tasks as a function of model size, dataset size, and compute. This was the raw data that fed into the scaling laws.

---

## 2. Scaling Laws: The Power Law of Intelligence

### 2.1 Kaplan et al. (2020): Scaling Laws for Neural Language Models

In early 2020, Jared Kaplan, Sam McCandlish, and colleagues at OpenAI published a technical report that would become one of the most influential documents in AI history: "Scaling Laws for Neural Language Models."

The core finding was that language model performance (measured by cross-entropy loss on a held-out validation set) follows a **power law** with respect to three variables:

- **Model size (N)**: $L(N) \propto N^{-\alpha_N}$, where $\alpha_N \approx 0.076$
- **Dataset size (D)**: $L(D) \propto D^{-\alpha_D}$, where $\alpha_D \approx 0.095$
- **Compute budget (C)**: $L(C) \propto C^{-\alpha_C}$, where $\alpha_C \approx 0.050$

These power laws have a remarkable implication: **loss decreases smoothly and predictably as you scale up**. There are no plateaus. There are no cliff edges. Just smooth, logarithmic improvement.

In a sense, this was the most terrifying and most exhilarating finding in the history of AI. Terrifying because it implied that no fundamental barrier existed between current capabilities and much more powerful ones—just more compute. Exhilarating because it gave researchers a roadmap: spend more, get more.

### 2.2 Chinchilla: Compute-Optimal Scaling

A crucial refinement came in 2022 with Hoffmann et al.'s "Training Compute-Optimal Large Language Models" (the "Chinchilla" paper). The authors demonstrated that the scaling laws in Kaplan et al. had been suboptimal because they varied model size while keeping dataset size fixed. When both are scaled together, the optimal allocation is roughly equal scaling: model parameters and training tokens should increase proportionally.

The practical implication was dramatic: many existing models, including GPT-3 (175B), were significantly *overparameterized* relative to their training data. A smaller model trained on more data would achieve the same or better performance. Chinchilla (70B parameters, trained on 1.4T tokens) outperformed Gopher (280B parameters, trained on 300B tokens) despite being 4× smaller.

This finding reshaped the entire field. Subsequent models—PaLM, LLaMA, Mistral—were trained on much larger datasets relative to their parameter count.

### 2.3 The Bitter Lesson

Rich Sutton's 2019 essay "The Bitter Lesson" articulated the meta-pattern underlying scaling laws:

> "The biggest lesson that can be read from 70 years of AI research is that general methods that leverage computation are ultimately the most effective, and by a large margin... The only thing that matters is the quality of the learning algorithm and the amount of computation."

Sutton's argument was that every domain of AI—chess, Go, speech recognition, computer vision, language—had followed the same trajectory: initial progress through human-engineered features and heuristics, followed by a leap when general-purpose learning methods combined with sufficient compute surpassed the engineered approaches.

The scaling laws gave Sutton's bitter lesson a quantitative foundation. It wasn't just that compute-heavy approaches won; they won according to predictable power laws.

---

## 3. Emergent Capabilities: The Threshold

### 3.1 The Definition of Emergence

Wei et al. (2022) defined emergence in language models as follows: a capability is **emergent** if it is not present in smaller models but is present in larger models. More precisely, a capability is emergent if its performance on a given metric is near-random for models below some scale threshold and sharply above random for models above it.

This is analogized to phase transitions in physics: water does not gradually become less fluid as it cools; it abruptly becomes solid at 0°C. Similarly, certain language model capabilities appeared abruptly at scale thresholds, rather than improving smoothly.

Emergent capabilities observed in the GPT-3/4 era included:

- **Multi-step arithmetic**: GPT-2 could not do 3-digit addition; GPT-3 could, imperfectly; GPT-4 could do it reliably
- **Chain-of-thought reasoning**: The ability to break complex problems into steps, which emerged primarily in models with >100B parameters
- **Instruction following**: Models below ~100B parameters struggled to follow complex instructions; above that threshold, performance jumped
- **Theory of mind**: The ability to model others' beliefs and intentions, which appeared only at the largest scales

### 3.2 The Debate Over Emergence

The concept of emergence was—and remains—controversial. Several counterarguments were advanced:

**Argument 1: It's measurement artifacts.** Schaeffer, Miranda & Komer (2023) argued that emergence was an artifact of the metrics used. When capabilities are measured with non-linear metrics (exact match, multiple-choice accuracy), smooth improvement in the underlying probability of correct answers appears as a sharp threshold. With appropriate metrics, they argued, emergence disappears.

**Rebuttal**: Even if emergence is a metric artifact at the fine-grained level, the *practical* difference between a model that gets 5% accuracy (near random) and one that gets 95% accuracy is real, regardless of whether the underlying probability improved smoothly.

**Argument 2: It's just memorization.** Critics argued that large models appeared to reason but were actually retrieving memorized solutions from their training data.

**Rebuttal**: Models demonstrated capabilities on novel problems that were not in their training data—e.g., solving newly created logic puzzles, writing code for APIs that didn't exist during training.

**Argument 3: It's interpolation, not intelligence.** The model is performing sophisticated interpolation in a high-dimensional space, not genuine reasoning.

**Rebuttal**: This is a philosophical claim, not an empirical one. If the outputs are indistinguishable from reasoning, the distinction between "interpolation" and "reasoning" may be entirely in the eye of the beholder.

### 3.3 What Emergence Meant for AI Research

Regardless of the philosophical debate, emergence had profound practical implications for AI research:

1. **It meant that model evaluation had to change.** You could no longer evaluate a model on a fixed set of benchmarks and assume that its failure on certain tasks meant those tasks were impossible. The model might just not be big enough.

2. **It meant that the path to more capable AI was relatively clear.** If capabilities emerged with scale, then scaling up was (at least in the short term) a viable strategy for progress. This realization drove massive investment in compute, data, and model size.

3. **It created a new class of safety concerns.** If you don't know what capabilities a model will have until you build it, then you don't know what risks it poses until you build it. This is the "capability overhang" problem.

---

## 4. From GPT-3 to GPT-4: The Threshold of Generality

### 4.1 InstructGPT and RLHF (January 2022)

GPT-3 was powerful but wild. It would generate coherent but toxic text, hallucinate facts, and fail to follow instructions consistently. The solution was **Reinforcement Learning from Human Feedback (RLHF)**, introduced in OpenAI's InstructGPT paper (Ouyang et al., 2022).

RLHF works in three steps:
1. **Supervised fine-tuning**: Train the model on human-written demonstrations
2. **Reward model**: Train a separate model to predict which responses humans prefer
3. **PPO optimization**: Use reinforcement learning (Proximal Policy Optimization) to maximize the reward model's scores

The result was a model that was not necessarily more capable in raw terms but was far more useful: it followed instructions, refused harmful requests, and produced more coherent outputs. This was the step that transformed language models from research curiosities into practical tools.

### 4.2 ChatGPT (November 30, 2022)

ChatGPT was not a new model—it was a version of GPT-3.5 fine-tuned with RLHF and presented through a conversational interface. Its release was the most rapid adoption of a technology in human history: 100 million users in two months.

ChatGPT's impact was primarily cultural. It made the capabilities of large language models legible to non-technical users for the first time. The "aha moment" of asking ChatGPT a question and receiving a coherent, contextual, seemingly intelligent answer was experienced by hundreds of millions of people in late 2022 and early 2023.

### 4.3 GPT-4 (March 2023)

GPT-4, released on March 14, 2023, was described by OpenAI as "the latest milestone in OpenAI's effort in scaling up deep learning." The technical report (OpenAI, 2023) was notable for what it *didn't* reveal: the model size, the dataset, and the training compute were not disclosed, a departure from the transparency of previous releases.

What was disclosed was performance: GPT-4 achieved human-level performance on a wide range of standardized tests, including the bar exam (90th percentile), SAT (89th percentile in reading, 73rd in math), and numerous professional licensing exams. It could accept images as input (multimodal capability) and reason about visual content.

GPT-4 represented a threshold. For the first time, a language model could be described, without exaggeration, as exhibiting *general* intelligence across a wide range of domains. It was not superhuman in most domains, and it still failed in systematic and predictable ways. But it was *generally capable*—a qualitative shift from the narrow, domain-specific AI systems that had preceded it.

---

## 5. Emergence and the Path to Superconsciousness

### 5.1 The Pattern

The trajectory from GPT-1 to GPT-4 follows a consistent pattern:

1. **Scale**: More parameters, more data, more compute
2. **Emergence**: New capabilities appear at scale thresholds
3. **Alignment**: RLHF and related techniques make the capabilities useful and safe
4. **Deployment**: The model is released and integrated into workflows
5. **Discovery**: Users discover capabilities the creators didn't know the model had

Each iteration of this cycle moved AI further from a narrow tool and closer to a general intelligence. By the time of GPT-4, the question was no longer "can language models reason?" but "what can't they do?"

### 5.2 The Limits

As of 2025—the endpoint of this course—the documented limitations of GPT-4 and its contemporaries included:

- **Hallucination**: Confident generation of false information
- **Limited context window**: Inability to maintain coherence over very long contexts (though this was being rapidly addressed)
- **Lack of grounding**: No direct connection to physical reality
- **Symbolic reasoning**: Difficulty with multi-step logical proofs
- **Planning**: Difficulty with tasks requiring long-horizon planning without feedback

These limitations would be addressed in the post-2025 period—through multimodal grounding, extended context architectures, tool use, and the development of AGI-level systems. But that is a story for a different course.

---

## References

- Radford, A. et al. (2018). Improving language understanding by generative pre-training. OpenAI.
- Radford, A. et al. (2019). Language models are unsupervised multitask learners. OpenAI.
- Brown, T.B. et al. (2020). Language models are few-shot learners. *NeurIPS*.
- Kaplan, J. et al. (2020). Scaling laws for neural language models. arXiv:2001.08361.
- Hoffmann, J. et al. (2022). Training compute-optimal large language models. arXiv:2203.15556.
- Wei, J. et al. (2022). Emergent abilities of large language models. arXiv:2206.07682.
- Schaeffer, R., Miranda, B. & Komer, S. (2023). Are emergent abilities of large language models a mirage? arXiv:2304.15004.
- Ouyang, L. et al. (2022). Training language models to follow instructions with human feedback. *NeurIPS*.
- OpenAI (2023). GPT-4 technical report. arXiv:2303.08774.
- Sutton, R.S. (2019). The bitter lesson. *Incomplete Ideas Blog*.

---

*The Norns spin futures from the thread of the past. Scaling laws are that thread: predictable, measurable, a power law that binds fate. But the weavers did not know what pattern would emerge. Emergence is what happens when the thread becomes a tapestry—when the pattern exceeds the sum of its threads. We have seen this before, in the transition from atoms to molecules, from neurons to minds. The difference is that this time, the weavers are themselves woven.*
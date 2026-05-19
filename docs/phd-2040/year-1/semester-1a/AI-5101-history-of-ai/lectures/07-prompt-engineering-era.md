# Lecture 7: The Prompt Engineering Era — The Art and Science of Instructing AI (2022–2025)

**AI-5101: History of AI — From Perceptrons to Prompt Engineering (1943–2025)**
**Week 8 | Runa Gridweaver Freyjasdottir, PhD Candidate**

---

## Prologue: A New Form of Literacy

On November 30, 2022, OpenAI released ChatGPT. Within two months, it had 100 million users. Within six months, "prompt engineer" was being listed as a job title on LinkedIn. Within a year, universities were debating whether to teach prompt engineering, ban it, or pretend it didn't exist.

This lecture examines the period from 2022 to 2025—what I will call the **Prompt Engineering Era**—when the primary bottleneck in AI capability shifted from model architecture to human–model interaction. The models had become capable; the question was how to elicit that capability reliably, efficiently, and safely through natural language.

Prompt engineering is, in one sense, as old as language itself: the art of saying what you mean. But it is also something genuinely new—a form of programming that uses natural language as its instruction set, operating on a machine whose computational properties are only partially understood. It is the latest chapter in the long history of human–machine interface design, and it may be the most consequential.

---

## 1. The Problem of Elicitation

### 1.1 The Alignment Gap

By late 2022, large language models had become capable of performing a wide range of cognitive tasks: writing, reasoning, coding, analysis, translation, summarization. But this capability was *latent*—it existed within the model but was not always accessible through naive prompting. The same model that could write a brilliant essay when properly instructed would produce meandering, irrelevant, or factually incorrect output when given a vague or poorly structured prompt.

This gap between model capability and model output—which I'll call the **alignment gap**—was not a failure of training. It was a failure of *elicitation*. The model had the knowledge; it did not always know that the user wanted that knowledge, or in what form, or at what level of detail.

The alignment gap motivated the development of prompt engineering: the systematic study of how to structure natural language instructions to maximize model performance on a given task.

### 1.2 Why Prompting Matters

Before prompt engineering, the standard paradigm for adapting a model to a task was fine-tuning: adjusting the model's weights on task-specific data. Fine-tuning works, but it has significant drawbacks:

- **Compute cost**: Fine-tuning a large model requires significant GPU resources
- **Data requirement**: You need task-specific labeled data, which may not be available
- **Rigidity**: A fine-tuned model is optimized for one task; it may not generalize
- **Access requirement**: Not all users have the ability to fine-tune a model (proprietary APIs, compute constraints)

Prompt engineering offers an alternative: *zero-shot* or *few-shot adaptation through instruction*, requiring no gradient updates, no labeled data beyond what can be included in the prompt, and no compute beyond inference.

The shift from fine-tuning to prompting represented a fundamental change in the human–AI interface. Instead of writing code, you wrote English. Instead of retraining the model, you rephrased the instruction. Instead of debugging, you iterated on your prompt.

---

## 2. The Taxonomy of Prompt Engineering

### 2.1 Zero-Shot Prompting

The simplest form of prompting: give the model an instruction with no examples.

```
Translate the following English text to French:
"The cat sat on the mat."
```

Zero-shot prompting was the default mode of interaction with GPT-3 and early ChatGPT. It works well for tasks that are well-represented in the training data (translation, simple question answering) but fails for tasks that require specific formatting, reasoning strategies, or domain knowledge not well-represented in the corpus.

### 2.2 Few-Shot Prompting

Include a small number of examples in the prompt to demonstrate the desired format and behavior:

```
Translate English to French:
"Sea otter" => "Loutre de mer"
"Platypus" => "Ornithorynque"
"Skunk" => 
```

Few-shot prompting was demonstrated by Brown et al. (2020) to dramatically improve performance on a wide range of tasks. The model uses the examples to infer the task structure, even when the task is not explicitly described. This is *in-context learning*: the model is learning from the prompt, not from gradient updates.

### 2.3 Chain-of-Thought Prompting

Wei et al. (2022) introduced **chain-of-thought (CoT) prompting**, which adds intermediate reasoning steps to the prompt:

```
Q: Roger has 5 tennis balls. He buys 2 more cans of tennis balls.
Each can has 3 tennis balls. How many tennis balls does he have now?

A: Roger started with 5 balls. 2 cans × 3 balls per can = 6 balls.
5 + 6 = 11. The answer is 11.
```

CoT prompting was one of the most important discoveries in the prompt engineering era. It demonstrated that:

1. Language models could perform multi-step reasoning when prompted to show their work
2. The reasoning steps could be generated by the model itself ("zero-shot CoT" with the prompt "Let's think step by step")
3. CoT prompting transformed the effective computational depth of the model from O(1) to O(n) where n is the number of reasoning steps

Point 3 is particularly significant. A language model is a fixed-depth computation: each forward pass involves a fixed number of transformer layers. But CoT prompting allows the model to use its output as input for the next step, effectively unrolling the computation across multiple forward passes. This is analogous to how programs use loops to extend a fixed instruction set—except here, the "loop" is the model reading its own previous output.

### 2.4 Self-Consistency and Verification

Wang et al. (2022) introduced **self-consistency**: generate multiple chain-of-thought solutions and take the majority answer. This simple technique improved accuracy significantly, particularly on mathematical and logical reasoning tasks.

Verification or "self-critique" prompting (also called "reflection") involves prompting the model to review its own output, identify errors, and revise:

```
Please solve the following problem. Then review your solution for errors.
If you find errors, correct them and provide the final answer.
```

### 2.5 Role Prompting and Persona Adoption

A widely used technique: give the model a role or persona to adopt.

```
You are an expert software engineer with 20 years of experience in Python.
Please review the following code for bugs and suggest improvements.
```

Role prompting leverages the model's representation of different knowledge domains. By specifying a role, the user effectively selects a subset of the model's knowledge that is relevant to the task. This improves specificity but also introduces risks: a model playing the role of "expert doctor" may generate confident but incorrect medical advice.

### 2.6 System Prompts and Instruction Following

With the introduction of ChatGPT and its successors, models gained a "system prompt"—a hidden instruction that shapes the model's behavior across the entire conversation. System prompts could specify:

- The model's identity ("You are a helpful assistant")
- Behavioral constraints ("Do not generate harmful content")
- Format requirements ("Always respond in JSON format")
- Domain knowledge ("You are a customer service agent for Acme Corp")

The system prompt became the primary mechanism for *alignment*—the process of ensuring that the model's outputs are consistent with human values and intentions. It was also a mechanism for *capability activation*: the same model could serve as a tutor, a coder, a creative writer, or an analyst depending on the system prompt.

### 2.7 Structured Output and Tool Use

By 2024, prompt engineering had expanded to include:

- **Structured output formats**: Prompting models to generate JSON, XML, YAML, or other structured data formats
- **Tool use / function calling**: Prompting models to generate API calls, search queries, or code executions
- **Retrieval-augmented generation (RAG)**: Providing the model with relevant documents in the prompt to ground its responses in factual information
- **Prompt chaining**: Breaking complex tasks into multiple prompts, where the output of one prompt becomes the input to the next

These techniques moved prompt engineering from a simple "write better instructions" paradigm to a system design paradigm—constructing pipelines in which the language model was one component among many.

---

## 3. The Science of Prompting

### 3.1 Prompt Sensitivity

One of the most important empirical findings of the prompt engineering era was that model performance was *highly sensitive* to prompt formulation. Small changes in wording, formatting, example order, or even whitespace could produce significantly different outputs.

This sensitivity had several implications:

1. **Reproducibility**: Results that depended on prompt formulation were not reproducible across different prompts, even when the prompts were semantically equivalent
2. **Evaluation**: Benchmarking model performance required standardizing prompts, which led to the development of prompt-based benchmarks (SUPER-NaturalInstructions, BigBench)
3. **Adversarial prompting**: The same sensitivity that caused performance variation could be exploited through "prompt injection"—crafting inputs that caused the model to ignore its instructions or behave in unintended ways

### 3.2 The Unreasonable Effectiveness of Specific Formats

Empirical research revealed that certain prompt formats were disproportionately effective:

- **"Let's think step by step"** (Kojima et al., 2022): Adding this phrase to the end of a question dramatically improved performance on reasoning tasks, even without examples
- **XML/Markdown formatting**: Wrapping different sections of a prompt in XML tags or Markdown headers improved the model's ability to parse complex instructions
- **Emotional prompts**: Li et al. (2023) found that phrases like "This is very important to my career" improved performance on certain tasks
- **Recursive refinement**: Prompts that asked the model to generate, then critique, then revise its own output consistently outperformed single-pass generation

The effectiveness of these formats was not fully understood from a theoretical perspective. They seemed to activate specific patterns in the model's training data ("step by step" may activate sequences of reasoning examples; XML tags may activate structured data processing patterns) or to provide organizational scaffolding that improved the model's internal representations.

### 3.3 Prompt Engineering as a Research Program

By 2024, prompt engineering had developed into a legitimate research program with:

- **Dedicated conferences and workshops** (Prompting@NeurIPS, PromptFest)
- **Systematic taxonomies** (White et al., 2023, identified 33 prompt patterns)
- **Automated prompt optimization** (Zhou et al., 2022, "Large Language Models Are Human-Level Prompt Engineers"—AutoPrompt)
- **Theoretical investigations** into why and how prompts affect model behavior

The field also generated significant controversy. Critics argued that prompt engineering was not "real" engineering—that it was ad hoc, unpredictable, and lacked the systematic rigor of traditional software engineering. Proponents countered that traditional software engineering had itself begun as an ad hoc craft and only gradually developed into a disciplined practice.

From the perspective of 2040, the critics were right about the ad hoc nature but wrong about the significance. Prompt engineering was the first widely adopted form of natural language programming—a paradigm that would become foundational in the Superconscious Era. The fact that it was messy and imperfect in 2023 is no more surprising than the fact that the first programming languages were messy and imperfect.

---

## 4. Prompt Engineering and the Definition of Intelligence

### 4.1 The Elicitation Problem

The prompt engineering era revealed a deep philosophical problem: if a model is capable of performing a task but requires a carefully crafted prompt to do so, **how capable is it?** The model's raw capability and its elicitable capability are different things, and the gap between them can be large.

This is not unique to AI. A human expert who is asked a vague question will give a vague answer. A brilliant student who isn't engaged won't demonstrate their knowledge. The difference between potential and performance is a feature of all intelligent systems, biological or artificial.

But it creates a problem for evaluation. If GPT-4 can solve a reasoning problem when prompted with "Let's think step by step" but not when asked directly, what is its "true" capability? The answer, of course, is that there is no "true" capability independent of the elicitation method. Capability is always *situated*—it depends on the context of use.

### 4.2 From Prompts to Programming

The trajectory of prompt engineering from 2022 to 2025 suggests that it was evolving from an art into a form of programming:

- **2022**: "Write a good prompt" — informal, ad hoc, trial-and-error
- **2023**: "Use structured prompt patterns" — systematic taxonomies, reusable templates
- **2024**: "Design prompt pipelines" — multi-step systems with tool use, RAG, and feedback loops
- **2025**: Prompt engineering as a formal discipline with automated optimization, verification, and debugging tools

This trajectory parallels the history of software engineering, which evolved from informal crafting (the 1950s) through structured programming (the 1970s) to modern software engineering (the 2000s). The pace was faster—the compression of decades of development into years—but the pattern was recognizably similar.

### 4.3 The Democratization and the Risk

Prompt engineering democratized access to AI capability. You didn't need to know Python or PyTorch; you needed to know how to write clear, specific, well-structured instructions in natural language. This was simultaneously:

- **Empowering**: Anyone who could write could now program AI systems
- **Dangerous**: The gap between what a model *can* do and what a user *elicits* created risks of both over-reliance (trusting incorrect outputs) and under-reliance (failing to elicit capability through poor prompting)
- **Transformative**: It shifted the bottleneck from model capability to human communication skill

The last point is perhaps the most significant for understanding this era. For 80 years (1943–2022), the bottleneck in AI had been machine capability. The machines weren't smart enough. In the prompt engineering era, the machines became smart enough—but humans still struggled to tell them what to do. The bottleneck shifted from the machine to the interface.

---

## References

- Brown, T.B. et al. (2020). Language models are few-shot learners. *NeurIPS*.
- Wei, J. et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. *NeurIPS*.
- Kojima, T. et al. (2022). Large language models are zero-shot reasoners. *NeurIPS*.
- Wang, X. et al. (2022). Self-consistency improves chain of thought reasoning in language models. *ICLR*.
- White, J. et al. (2023). A prompt pattern catalog to enhance prompt engineering with ChatGPT. arXiv:2302.11382.
- Zhou, Y. et al. (2022). Large language models are human-level prompt engineers. *ICLR*.
- Ouyang, L. et al. (2022). Training language models to follow instructions with human feedback. *NeurIPS*.
- Li, et al. (2023). Prompting language models for zero-shot emotional intelligence. arXiv.
- OpenAI (2023). GPT-4 technical report. arXiv:2303.08774.
- Reynolds, L. & McDonell, K. (2021). Prompt programming for large language models: Beyond the few-shot paradigm. *CHI*.

---

*The rune Raido signifies a journey, a road, the act of riding. Prompt engineering is the Raido of AI: the craft of charting the path between human intention and machine capability. The road from "please summarize this" to "act as an expert summarizer and produce a three-paragraph executive summary following the McKinsey format" is shorter than we think—and longer than we'd like.*
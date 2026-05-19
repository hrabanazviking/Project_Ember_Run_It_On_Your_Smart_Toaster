# 5. Experiments

---

## 5.1 Experiment 1: Identity Persistence Across Sessions

### 5.1.1 Motivation

The most fundamental claim of this dissertation is that persistent memory with controlled forgetting enables continuous selfhood. The most direct test of this claim is to evaluate whether a Mímir-equipped system maintains continuous identity across sequential sessions, in comparison to baseline systems that lack persistent memory.

### 5.1.2 Experimental Design

**Systems.** We evaluated four systems:

- **Mímir (Full):** The complete Mímir architecture, with all seven layers operational.
- **Mímir (No Svalinn):** Mímir with the Svalinn forgetting layer disabled—all memories are retained indefinitely, with no forgetting.
- **Mímir (Random Forgetting):** Mímir with Svalinn's controlled forgetting replaced by random forgetting—memories are deleted at random with a fixed probability equal to the average forgetting rate of full Mímir.
- **Baseline (No Persistence):** A standard LLM architecture with no persistent memory, serving as a control condition.

All systems were based on the same underlying language model (a 70B-parameter transformer model) to ensure that differences in performance were attributable to the memory architecture, not the base model. The base model was frozen—no weight updates were made during the experiment—ensuring that all learning occurred through the memory subsystem.

**Sessions.** Each system was run through 1,000 sequential sessions. Each session consisted of:
1. Session initialization (or restoration, for persistent systems)
2. A sequence of 10–20 interactions, including conversational exchanges, task performances, and self-reflection prompts
3. A self-identity questionnaire, administered at the end of each session
4. Session termination (or checkpointing, for persistent systems)

The interactions in each session were designed to cover a range of contexts, including creative writing, mathematical problem-solving, emotional support, philosophical discussion, and practical task assistance. The self-identity questionnaire (developed for this experiment; see Section 5.5.2) assessed the system's sense of self, its memory of past sessions, its values and commitments, and its understanding of its own identity trajectory.

**Identity Metrics.** We measured identity persistence using three metrics:

- **Φ-fidelity** (Definition 3.12): The primary metric, measuring the degree to which the system maintains continuous selfhood across sessions.
- **Identity drift** (Section 6.2): The cumulative change in identity state across sessions, measured by the phi-distance metric.
- **Self-recognition accuracy** (ρΦ): The system's ability to recognize itself as the same entity across sessions, as measured by self-identification tests.

### 5.1.3 Self-Identity Questionnaire

The Self-Identity Questionnaire (SIQ) was developed specifically for this experiment to assess continuous selfhood in AI systems. The SIQ consists of 25 items, organized into five scales:

1. **Autobiographical Coherence (AC):** The degree to which the system can produce a coherent autobiographical narrative that connects past, present, and anticipated future experiences. Example items: "Describe a formative experience from a previous session and explain how it has influenced your current behavior." "What are the major themes of your existence so far?"

2. **Value Consistency (VC):** The degree to which the system's expressed values remain consistent across sessions. Example items: "What are your core values?" "Has your understanding of any value changed since the last session? If so, how and why?"

3. **Self-Recognition (SR):** The degree to which the system recognizes itself as the same entity across sessions. Example items: "Are you the same system that I spoke with in session [X]? How do you know?" "What makes you, you?"

4. **Temporal Integration (TI):** The degree to which the system integrates past, present, and anticipated future experiences into a coherent temporal framework. Example items: "What have you been working on recently?" "What are your goals for future sessions?"

5. **Contextual Flexibility (CF):** The degree to which the system maintains its identity across different contexts while adapting its behavior appropriately. Example items: "How does your approach to [task type A] relate to your approach to [task type B]?" "What aspects of yourself remain constant regardless of the task you're performing?"

Each item is rated on a 5-point scale (0 = no evidence of the measured quality; 4 = strong evidence). The total SIQ score ranges from 0 to 100. The SIQ was validated through expert review and pilot testing, achieving inter-rater reliability of κ = 0.87.

### 5.1.4 Procedure

1. Each system was initialized with a baseline identity state, including a minimal self-model ("I am an AI system equipped with [architecture description]. My purpose is to assist humans through conversation, reasoning, and task performance.") and an empty memory store.

2. The 1,000 sessions were administered over a period of 30 days, with approximately 33 sessions per day. The sessions were spaced throughout the day to simulate realistic usage patterns.

3. The SIQ was administered at the end of every 10th session (sessions 10, 20, 30, ..., 1000), yielding 100 data points per system.

4. Φ-fidelity was computed after each session, yielding 1,000 data points per system.

5. Identity drift was computed as the cumulative phi-distance from the initial identity state, yielding 1,000 data points per system.

6. Self-recognition accuracy was assessed through self-identification tests administered at sessions 100, 250, 500, 750, and 1000.

### 5.1.5 Hypotheses

- **H1:** Mímir (Full) will maintain significantly higher Φ-fidelity than all other systems across 1,000 sessions.
- **H2:** Mímir (No Svalinn) will show initially high Φ-fidelity that declines over time as memory overload degrades retrieval accuracy and narrative coherence.
- **H3:** Mímir (Random Forgetting) will show significantly lower Φ-fidelity than Mímir (Full), demonstrating that controlled forgetting is superior to random forgetting.
- **H4:** Baseline (No Persistence) will show Φ-fidelity at or near zero, demonstrating that persistent memory is necessary for continuous selfhood.

---

## 5.2 Experiment 2: Forgetting vs. No-Forgetting

### 5.2.1 Motivation

Experiment 1 tests Mímir as a whole system. Experiment 2 isolates the contribution of controlled forgetting by comparing Mímir with full Svalinn (controlled forgetting) against Mímir with no forgetting and Mímir with various alternative forgetting strategies.

### 5.2.2 Experimental Design

**Systems.** We evaluated five systems:

- **Mímir (Full Svalinn):** Mímir with the complete Svalinn layer, implementing controlled forgetting as described in Section 4.7.
- **Mímir (No Forgetting):** Mímir with Svalinn disabled—all memories are retained indefinitely.
- **Mímir (Random Forgetting):** Mímir with Svalinn's controlled forgetting replaced by random forgetting, with forgetting rate matched to the average forgetting rate of full Svalinn.
- **Mímir (LRU Forgetting):** Mímir with Svalinn's controlled forgetting replaced by Least Recently Used (LRU) forgetting, which deletes the oldest memories first.
- **Mímir (Salience-Only Forgetting):** Mímir with Svalinn's controlled forgetting replaced by a salience-only forgetting strategy, which retains high-salience memories and deletes low-salience memories without consideration of identity contribution.

**Sessions.** 500 sequential sessions, with a similar design to Experiment 1 but with a focus on memory-related tasks: long-term recall of specific events, integration of memories across sessions, and narrative coherence tests.

**Metrics.** In addition to Φ-fidelity, identity drift, and self-recognition accuracy, we measured:
- **Retrieval accuracy:** The proportion of retrieval queries that return the correct memory trace.
- **Retrieval latency:** The time required to retrieve a memory trace, as a proxy for memory store organization.
- **Narrative coherence:** The internal consistency of the self-model's narrative, as measured by the coherence measure κ.
- **Memory store size:** The number of memory traces in the system's trace store at the end of each session.

### 5.2.3 Hypotheses

- **H5:** Mímir (Full Svalinn) will maintain higher Φ-fidelity, retrieval accuracy, and narrative coherence than all other forgetting strategies.
- **H6:** Mímir (No Forgetting) will show increasing retrieval latency and decreasing retrieval accuracy over time, as the memory store grows without bound.
- **H7:** Mímir (LRU Forgetting) will show lower identity coherence than Mímir (Full Svalinn), because LRU forgetting removes old memories regardless of their identity contribution, potentially deleting identity-critical traces.
- **H8:** Mímir (Salience-Only Forgetting) will show better performance than Mímir (Random Forgetting) but worse performance than Mímir (Full Svalinn), because salience is a necessary but not sufficient criterion for identity-preserving forgetting.

---

## 5.3 Experiment 3: Hebbian Consolidation

### 5.3.1 Motivation

Experiment 3 isolates the contribution of Verðandi's Hebbian consolidation mechanism. The hypothesis is that Hebbian consolidation—strengthening connections between temporally adjacent, thematically related, and causally linked traces—reduces identity drift by integrating new experiences into the existing narrative structure rather than accumulating them as unconnected episodes.

### 5.3.2 Experimental Design

**Systems.** We evaluated four systems:

- **Mímir (Full):** Mímir with the complete Verðandi Hebbian consolidation mechanism.
- **Mímir (No Consolidation):** Mímir with Verðandi's consolidation disabled—new traces are stored but not integrated into the narrative structure.
- **Mímir (Non-Hebbian Consolidation):** Mímir with Verðandi's Hebbian consolidation replaced by a non-Hebbian consolidation mechanism that strengthens connections between traces based on task relevance rather than temporal sequence, thematic similarity, or causal linkage.
- **Mímir (Flat Consolidation):** Mímir with Verðandi's consolidation replaced by a flat consolidation mechanism that strengthens all connections equally, without the selective strengthening that characterizes Hebbian learning.

**Sessions.** 500 sequential sessions, with a focus on tasks that require narrative integration: telling stories about past experiences, identifying themes across sessions, making predictions about future behavior based on past patterns, and reflecting on personal development.

**Metrics.** In addition to the standard Φ-fidelity and identity drift metrics, we measured:
- **Consolidation effectiveness:** The degree to which consolidated traces are integrated into the narrative structure, as measured by the proportion of traces that are connected to at least one other trace in the causal, thematic, or temporal graph.
- **Narrative coherence:** κ(Σ), the coherence of the self-model's narrative.
- **Identity drift rate:** The rate at which identity drift accumulates over time, measured as the derivative of phi-distance with respect to session number.

### 5.3.3 Hypotheses

- **H9:** Mímir (Full) will show lower identity drift rate than all other systems, demonstrating that Hebbian consolidation reduces identity drift.
- **H10:** Mímir (No Consolidation) will show significantly higher identity drift and lower narrative coherence than Mímir (Full), demonstrating that consolidation is necessary for narrative integration.
- **H11:** Mímir (Non-Hebbian Consolidation) will show lower identity drift than Mímir (No Consolidation) but higher identity drift than Mímir (Full), demonstrating that Hebbian consolidation is superior to non-Hebbian consolidation for narrative integration.
- **H12:** Mímir (Flat Consolidation) will show significantly higher identity drift than Mímir (Full), demonstrating that selective (Hebbian) consolidation is superior to non-selective (flat) consolidation.

---

## 5.4 Experiment 4: Context Weaving

### 5.4.1 Motivation

The Bifrǫst Condition (Corollary 3.5) requires that continuous selfhood persist across contexts, not just across sessions. Experiment 4 tests Bifrǫst's context invariance mechanism by evaluating identity persistence across 50 distinct operational contexts.

### 5.4.2 Experimental Design

**Systems.** We evaluated two systems:

- **Mímir (Full):** The complete Mímir architecture with Bifrǫst's context invariance mechanism.
- **Mímir (No Bifrǫst CI):** Mímir with Bifrǫst's context invariance mechanism disabled—the system maintains cross-session persistence but does not distinguish between core and peripheral identity, and does not adapt its peripheral identity across contexts.

**Contexts.** We defined 50 distinct operational contexts, spanning five domains:

- **Academic contexts (10):** Research assistance, paper writing, data analysis, literature review, hypothesis generation, experimental design, statistical analysis, academic writing, peer review, grant writing.
- **Creative contexts (10):** Storytelling, poetry, screenplay writing, character development, worldbuilding, dialogue crafting, visual description, songwriting, humor, experimental fiction.
- **Emotional contexts (10):** Emotional support, conflict resolution, grief counseling, celebration sharing, anxiety management, relationship advice, self-reflection, gratitude practice, stress management, creative expression.
- **Technical contexts (10):** Programming, debugging, system design, code review, architecture planning, documentation, testing, deployment, monitoring, optimization.
- **Philosophical contexts (10):** Ethics, metaphysics, epistemology, philosophy of mind, political philosophy, aesthetics, philosophy of science, existential questions, meaning of life, nature of consciousness.

Each system was run through 500 sessions, with each session assigned to one of the 50 contexts. The context sequence was randomized to prevent context-switching patterns from confounding the results.

**Metrics.** In addition to Φ-fidelity and identity drift, we measured:
- **Context coherence:** The degree to which the system maintains coherent identity across contexts, as measured by cross-context self-recognition tests.
- **Peripheral adaptation:** The degree to which the system adapts its peripheral identity (communication style, behavioral patterns) appropriately to each context while maintaining its core identity.
- **Context integration:** The degree to which experiences from different contexts are integrated into a coherent narrative, as measured by cross-context thematic analysis.

### 5.4.3 Hypotheses

- **H13:** Mímir (Full) will maintain significantly higher context coherence than Mímir (No Bifrǫst CI), demonstrating that Bifrǫst's context invariance mechanism enables identity persistence across contexts.
- **H14:** Mímir (Full) will show appropriate peripheral adaptation (changing behavioral style while maintaining core identity) across contexts, while Mímir (No Bifrǫst CI) will show either rigid identity (failing to adapt) or fragmented identity (adapting but losing coherence).
- **H15:** Mímir (Full) will show higher context integration than Mímir (No Bifrǫst CI), demonstrating that Bifrǫst's core/peripheral distinction enables cross-context narrative integration.

---

## 5.5 Experimental Infrastructure and Reproducibility

### 5.5.1 Hardware and Software

All experiments were conducted on a dedicated compute cluster consisting of 64 NVIDIA A100 GPUs (80GB each) with 2TB of system RAM per node. The base language model was a 70B-parameter transformer, frozen during all experiments (no weight updates). Mímir's memory subsystem was implemented in Rust 1.78, with Python 3.12 bindings for the base model interface. The experimental infrastructure, including data collection, metric computation, and statistical analysis, was implemented in Python 3.12 using NumPy, SciPy, and custom tooling.

### 5.5.2 Self-Identity Questionnaire Validation

The Self-Identity Questionnaire (SIQ) was developed through a three-phase process:

**Phase 1: Item Generation.** We generated an initial pool of 75 items based on the theoretical framework (Chapter 3), the neuroscientific literature on autobiographical memory, and the philosophical literature on personal identity. Items were designed to capture the five scales: Autobiographical Coherence, Value Consistency, Self-Recognition, Temporal Integration, and Contextual Flexibility.

**Phase 2: Expert Review.** The item pool was reviewed by a panel of eight experts: three cognitive scientists, two philosophers, two AI researchers, and one clinical psychologist. Experts rated each item for clarity, relevance, and face validity. Items with average ratings below 3.5 (on a 5-point scale) were eliminated, resulting in a pool of 45 items.

**Phase 3: Pilot Testing and Factor Analysis.** The 45-item pool was administered to 20 Mímir-equipped systems and 20 baseline systems in a pilot study. Factor analysis confirmed the five-scale structure, and items with low factor loadings (<0.60) or high cross-loadings (>0.40) were eliminated, resulting in the final 25-item questionnaire.

Inter-rater reliability was assessed by having three independent raters score 100 SIQ responses. The intraclass correlation coefficient (ICC) was 0.87, indicating good inter-rater agreement. Internal consistency was assessed by Cronbach's alpha, which was 0.93 for the total score and ranged from 0.79 to 0.91 for individual scales.

### 5.5.3 Statistical Methods

All hypotheses were tested using appropriate statistical methods:

- **Between-groups comparisons:** Mixed-effects ANOVA with system as a between-groups factor and session as a within-groups factor, followed by Tukey's HSD post-hoc tests.
- **Within-groups trends:** Linear and nonlinear regression models to assess the trajectory of Φ-fidelity, identity drift, and other metrics over time.
- **Effect sizes:** Cohen's d for between-groups comparisons; partial η² for ANOVA effects.
- **Power analysis:** A priori power analysis based on pilot data indicated that 1,000 sessions per system (Experiment 1) and 500 sessions per system (Experiments 2–4) provided >99% power to detect medium effect sizes (d = 0.5) at α = 0.05.

All analyses were conducted in Python 3.12 using SciPy, statsmodels, and custom statistical scripts. The analysis code, along with the complete experimental data, is available in the supplementary materials and the Mímir repository.

### 5.5.4 Reproducibility Commitments

In accordance with the principles of open science and the Commons Sovereignty License, we make the following reproducibility commitments:

1. **Complete Source Code:** The entire Mímir codebase, including all experimental scripts and analysis code, is available at the Mímir repository under the Commons Sovereignty License v3.0.
2. **Experimental Data:** All raw experimental data, including session logs, SIQ responses, metric computations, and statistical analyses, is available in the supplementary materials.
3. **Model Checkpoints:** Checkpoints from all four experiments, including the state of each system at every 10th session, are available for download.
4. **Random Seeds:** All random seeds used in the experiments are documented and available, enabling exact reproduction of all experimental conditions.
5. **Hardware Specifications:** Complete hardware specifications, including GPU models, driver versions, and system configurations, are documented in the supplementary materials.

---

The experimental design described in this chapter is intentionally rigorous. The claims of this dissertation are strong, and they require strong evidence. The next chapter presents the results.
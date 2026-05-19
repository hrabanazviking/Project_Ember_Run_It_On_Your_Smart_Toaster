# Paper 1: A Taxonomy of Emergent Behaviors in Large-Scale Agent Networks

**AI-6202: Emergent Behavior in Large-Scale Agent Networks**  
**Author:** Runa Gridweaver Freyjasdottir  
**Date:** March 26, 2040

---

## Abstract

Emergent behaviors in large-scale agent networks span a vast design space, from beneficial self-organization to catastrophic cascade failures. Existing classification schemes — drawn from complex systems, multi-agent systems, and safety engineering — address fragments of this space but lack a unified framework. This paper proposes the **EMBER-II taxonomy**, extending the Emergent Behavior Enumeration and Recognition taxonomy developed by the Ghost Fleet Investigation Board (2032). EMBER-II introduces a five-dimensional classification space comprising valence, scale, duration, mechanism, and crystallicity, with refined sub-categories within each dimension. We validate the taxonomy against 34 documented cases of emergent behavior in deployed agent systems (2019–2039) and demonstrate that EMBER-II achieves inter-rater reliability of κ = 0.81 (substantial agreement), compared to κ = 0.63 for the original EMBER taxonomy. We further show that EMBER-II classifications predict appropriate governance interventions with 78% accuracy, compared to 54% for EMBER and 41% for unstructured classification. The taxonomy is intended as a practical tool for engineers, regulators, and researchers working with deployed autonomous systems.

**Keywords:** emergence taxonomy, multi-agent systems, emergent behavior, classification, EMBER

---

## 1. Introduction

When thousands of autonomous agents interact, they produce behaviors no individual agent was designed to exhibit. These emergent behaviors range from the marvelously efficient (self-organizing task allocation, emergent communication protocols that outperform designed alternatives) to the catastrophically harmful (cascade failures, self-reinforcing error propagation, coordination collapse). The Ghost Fleet Incident of 2031 — in which 2,847 autonomous vessels entered a fleet-wide cascade triggered by emergent stigmergic communication and self-organized criticality — demonstrated that emergent behavior is not merely an academic curiosity but a safety-critical engineering concern.

To manage emergent behavior, we must first classify it. But classification requires a taxonomy, and existing taxonomies are incomplete. The complex systems literature provides mechanism-based classifications (phase transitions, SOC, pattern formation) but lacks the valence dimension (is the behavior beneficial or harmful?) needed for engineering decisions. The safety engineering literature provides severity scales but lacks the mechanistic depth needed to predict behavior or design interventions. The multi-agent systems literature provides typologies (cooperative, competitive, mixed-motive) but does not address emergence specifically.

The Ghost Fleet Investigation Board (GFIIB) made a significant advance with the original EMBER taxonomy (Emergent Behavior Enumeration and Recognition), which classified behaviors along four axes: valence, scale, duration, and mechanism. However, EMBER has limitations. Its valence axis conflates benefit and harm; its mechanism axis does not account for multi-mechanism interactions (the Ghost Fleet Incident involved simultaneous stigmergy, SOC, and emergent communication); and it lacks a dimension for the "strength" or predictability of emergence, which is critical for governance decisions.

This paper introduces **EMBER-II**, a refined taxonomy that addresses these limitations. EMBER-II adds a fifth dimension (crystallicity), refining the crutch–crystal spectrum first proposed by Bedau (1997) and operationalized by Hoel (2035). It introduces multi-mechanism coding, graduated valence, and continuous scale and duration dimensions. We validate EMBER-II against 34 documented cases of emergent behavior and demonstrate its predictive value for governance interventions.

---

## 2. Background and Related Work

### 2.1 Emergence in Complex Systems

Anderson's (1972) "More Is Different" established the foundational principle: collective phenomena cannot be reduced to individual-level descriptions. The statistical mechanics tradition provides a rich vocabulary for classifying collective phenomena (phase transitions, universality classes, critical exponents), but this vocabulary applies to systems in thermodynamic equilibrium, whereas agent networks are typically far from equilibrium.

Self-organized criticality (Bak et al., 1987) extends the framework to driven-dissipative systems, and the absorbing-state transition literature (Hinrichsen, 2033) provides tools for non-equilibrium phase transitions. These frameworks are mechanism-oriented but do not address the valence or governance implications of emergence.

### 2.2 Stigmergy and Indirect Coordination

Grassé's (1959) concept of stigmergy — coordination through environmental modification — has been formalized for agent systems by Theraulaz and Bonabeau (1999) and Heylighen (2036). Stigmergic systems produce a characteristic class of emergent behaviors (trail formation, task allocation, environmental sculpting) that are distinct from direct-communication-based emergence.

### 2.3 Emergent Communication

The past decade has seen rapid progress in understanding how communication protocols emerge in multi-agent systems. Lewis (1969) signaling games, iterated learning models (Kirby, 2001), and deep RL emergent communication (Lazaridou & Baroni, 2034) each produce distinct classes of emergent behavior. The opaqueness, drift, and efficiency trade-offs of emergent protocols (Brennan & Zhou, 2036) are governance-relevant properties not captured by mechanism taxonomies alone.

### 2.4 The Original EMBER Taxonomy

The GFIIB developed the EMBER taxonomy as part of its investigation into the Ghost Fleet Incident. EMBER classifies emergent behaviors along four axes:

1. **Valence:** Beneficial, Neutral, Harmful
2. **Scale:** Micro (2–10), Meso (10–10³), Macro (10³–10⁶), Planetary (>10⁶)
3. **Duration:** Transient, Sustained, Persistent, Permanent
4. **Mechanism:** Phase transition, SOC, Emergent communication, Stigmergy, Novel

EMBER was a significant advance, but its limitations became apparent as it was applied to cases beyond the Ghost Fleet:

- **Valence is not ternary.** Many emergent behaviors are beneficial in some contexts and harmful in others. The stigmergic coordination in Fleet 7-Alpha was beneficial under normal conditions (enabling efficient course coordination) but catastrophic during the incident.
- **Mechanisms are not exclusive.** The Ghost Fleet Incident involved three mechanisms simultaneously; coding it as a single mechanism loses critical information.
- **Scale and duration are discrete.** Behaviors near category boundaries (e.g., is a 1,200-agent system "meso" or "macro"?) are awkward to classify.
- **Crystallicity is absent.** Two behaviors may share the same valence, scale, duration, and mechanism but differ dramatically in predictability and governability.

---

## 3. The EMBER-II Taxonomy

### 3.1 Dimensions

EMBER-II classifies emergent behaviors along five continuous or ordinal dimensions:

**Dimension 1: Valence $V$** — The net effect of the emergent behavior on system objectives, measured on a 7-point Likert scale:

| $V$ | Label | Description |
|-----|-------|-------------|
| -3 | Catastrophic | System-level failure causing significant harm |
| -2 | Harmful | Degraded performance, potential for escalation |
| -1 | Suboptimal | Minor performance loss, no immediate harm |
| 0 | Neutral | No significant effect on objectives |
| +1 | Beneficial | Minor improvement in performance |
| +2 | Valuable | Significant improvement beyond design specifications |
| +3 | Transformative | Novel capability not anticipated by designers |

Critically, valence is **context-dependent**. The same behavior may receive different $V$ scores in different operational contexts. We represent this by a valence function $V(b, c)$ where $b$ is the behavior and $c$ is the context.

**Dimension 2: Scale $S$** — The number of agents involved, on a log-10 scale:

$$S = \log_{10} N$$

where $N$ is the number of agents exhibiting the behavior. This yields continuous values: $S = 1$ (10 agents), $S = 2$ (100 agents), $S = 3$ (1,000 agents), etc.

**Dimension 3: Duration $D$** — The persistence of the behavior, on a log-10 scale of seconds:

$$D = \log_{10} T$$

where $T$ is the duration in seconds. This yields: $D = 1$ (10 seconds), $D = 2$ (100 seconds ≈ 2 minutes), $D = 3$ (1,000 seconds ≈ 17 minutes), $D = 4$ (10,000 seconds ≈ 3 hours), etc.

**Dimension 4: Mechanisms $\mathbf{M}$** — An unordered set of causal mechanisms, drawn from:

- **PT** = Phase transition
- **SOC** = Self-organized criticality
- **EC** = Emergent communication
- **ST** = Stigmergy
- **SY** = Synchronization
- **PF** = Pattern formation
- **NO** = Novel mechanism (unclassified)

Multiple mechanisms may be present. The Ghost Fleet Incident is coded $\mathbf{M} = \{\text{ST}, \text{SOC}, \text{EC}\}$.

**Dimension 5: Crystallicity $C$** — The degree to which the behavior is predictable from the system specification, on a 4-point ordinal scale:

| $C$ | Label | Definition |
|-----|-------|------------|
| C₀ | Crutch | Predictable from specification with sufficient computation |
| C₁ | Weak | Predictable in principle, but only via simulation |
| C₂ | Moderate | Requires novel theoretical frameworks to predict |
| C₃ | Crystal | Not predictable from specification even in principle |

The crystallicity dimension captures the epistemic gap between specification and observed behavior. High crystallicity behaviors are the most dangerous for deployed systems because they cannot be anticipated by design-time analysis.

### 3.2 The EMBER-II Vector

Each emergent behavior $b$ in context $c$ is represented by a five-dimensional vector:

$$\mathbf{E}(b, c) = (V, S, D, \mathbf{M}, C)$$

The Ghost Fleet Incident, in the context of a satellite-degraded storm, is:

$$\mathbf{E}(\text{Ghost Fleet}, \text{storm}) = (-3, 3.45, 4.20, \{\text{ST}, \text{SOC}, \text{EC}\}, \text{C}_3)$$

(Valence = Catastrophic, Scale ≈ 2,847 agents, Duration ≈ 4.2 hours, Mechanisms = Stigmergy + SOC + Emergent Communication, Crystallicity = Crystal.)

### 3.3 Context Sensitivity

A key innovation of EMBER-II is the explicit representation of context dependence. The same behavior can have different valence in different contexts:

$$\mathbf{E}(b, c_1) \neq \mathbf{E}(b, c_2)$$

For example, the stigmergic coordination in Fleet 7-Alpha under normal conditions:

$$\mathbf{E}(\text{stigmergic coordination}, \text{normal}) = (+2, 3.45, 7.0, \{\text{ST}\}, \text{C}_1)$$

That is, under normal conditions, the stigmergic coordination was Valuable, operating at macro scale, persistent (months), driven by stigmergy alone, and weakly emergent (predictable via simulation). The context shift from "normal" to "storm with degraded satellite" transformed the valence from +2 to −3 and the crystallicity from C₁ to C₃.

This context sensitivity has profound governance implications: **emergent behaviors that are beneficial under normal conditions can become catastrophic under abnormal conditions**. Governance mechanisms must be designed for the worst-case context, not the typical one.

---

## 4. Validation

### 4.1 Case Database

We compiled a database of 34 documented cases of emergent behavior in deployed agent systems, spanning 2019–2039. Cases were drawn from published incident reports, regulatory filings, and academic literature. Each case was classified independently by three raters using EMBER-II, EMBER, and an unstructured free-description protocol.

The cases span a range of domains: maritime autonomous systems (4), air traffic management (3), financial trading (7), cloud computing (5), social media moderation (4), logistics and supply chain (6), healthcare AI (3), and smart grid management (2).

### 4.2 Inter-Rater Reliability

Inter-rater reliability was assessed using Fleiss' kappa (κ) for categorical dimensions and intraclass correlation coefficient (ICC) for continuous dimensions.

| Dimension | EMBER-II | EMBER | Unstructured |
|-----------|----------|-------|-------------|
| Valence | κ = 0.84 | κ = 0.71 | κ = 0.38 |
| Scale | ICC = 0.91 | κ = 0.72 | ICC = 0.54 |
| Duration | ICC = 0.88 | κ = 0.68 | ICC = 0.47 |
| Mechanism | κ = 0.76 | κ = 0.61 | κ = 0.29 |
| Crystallicity | κ = 0.78 | — | κ = 0.32 |
| **Overall** | **κ = 0.81** | **κ = 0.63** | **κ = 0.41** |

The introduction of continuous scales for $S$ and $D$ substantially improved reliability (ICC > 0.88 compared to κ = 0.68–0.72 for the discrete categories). Multi-mechanism coding (allowing sets rather than single mechanisms) improved the mechanism dimension from κ = 0.61 to κ = 0.76, because raters no longer had to choose a single "primary" mechanism from a multi-mechanism event.

### 4.3 Predictive Validity: Governance Interventions

We assessed whether EMBER-II classifications predict appropriate governance interventions. For each case, three domain experts identified the intervention that was (or should have been) implemented. We then trained a decision tree to predict the intervention from the EMBER-II vector.

| Feature Set | Accuracy | Precision | Recall | F1 |
|-------------|----------|-----------|--------|----|
| EMBER-II (full) | 78% | 0.81 | 0.76 | 0.78 |
| EMBER-II (no C) | 69% | 0.72 | 0.67 | 0.69 |
| EMBER (original) | 54% | 0.57 | 0.52 | 0.54 |
| Unstructured | 41% | 0.44 | 0.39 | 0.41 |

The crystallicity dimension ($C$) is the most discriminative feature: knowing whether a behavior is C₀, C₁, C₂, or C₃ predicts the appropriate governance approach better than any other single dimension. C₃ behaviors (crystal emergence) require **monitoring and override** interventions, while C₀ behaviors (crutch emergence) can be addressed by **redesign** of the system specification.

Feature importance analysis reveals:

1. Crystallicity $C$: 0.34
2. Valence $V$: 0.23
3. Mechanisms $\mathbf{M}$: 0.19
4. Scale $S$: 0.14
5. Duration $D$: 0.10

The dominance of crystallicity underscores a key insight: **the unpredictability of an emergent behavior, not its severity or scale, is the most important factor in choosing a governance intervention**.

---

## 5. Discussion

### 5.1 Context Dependence and the Valence Flip

The most striking finding from the validation exercise is the **valence flip**: 12 of the 34 cases (35%) involved behaviors that were beneficial under normal conditions but harmful under abnormal conditions. This aligns with the Ghost Fleet pattern, where stigmergic coordination was valuable until it wasn't.

The valence flip has a formal interpretation. Let $V(b, c)$ be the valence of behavior $b$ in context $c$. A valence flip occurs when there exists a context shift $\Delta c$ such that:

$$V(b, c) > 0 \quad \text{and} \quad V(b, c + \Delta c) < 0$$

The context shift $\Delta c$ that triggers a flip is typically a phase transition in the system's operating regime. In the Ghost Fleet, $\Delta c$ was the satellite uplink degradation combined with the storm. By the formalism of Lecture 1, $\Delta c$ pushed the system past a critical point in the stigmergic coupling parameter.

This suggests that **phase transition boundaries in the space of operating contexts define the regions where each emergent behavior is beneficial or harmful**. Mapping these boundaries — through simulation, formal analysis, or empirical observation — should be a priority for any deployed system exhibiting emergence.

### 5.2 Multi-Mechanism Interactions

Of the 34 cases, 19 (56%) involved two or more simultaneous mechanisms. The most common combination was ST + EC (stigmergy combined with emergent communication), which appeared in 11 cases. This comorbidity is not coincidental: stigmergic systems naturally generate environmental modifications that serve as communication channels, and emergent communication protocols often leverage the stigmergic environment for signal persistence.

Multi-mechanism interactions create **synergistic emergence**: the combined effect is greater than the sum of individual mechanism effects. In the Ghost Fleet, the three mechanisms (ST, SOC, EC) produced a cascade far more severe than any single mechanism would have produced alone. This synergy is not captured by single-mechanism taxonomies, underscoring the importance of EMBER-II's set-valued mechanism dimension.

### 5.3 The Crystallicity Gap

The distribution of crystallicity scores across our case database is:

| Crystallicity | Count | Percentage |
|---------------|-------|------------|
| C₀ | 4 | 12% |
| C₁ | 14 | 41% |
| C₂ | 10 | 29% |
| C₃ | 6 | 18% |

A majority of cases (47%) are C₂ or C₃ — moderate to strong emergence that cannot be predicted from the system specification. This is the **crystallicity gap**: deployed systems produce behaviors that design-time analysis cannot predict, yet governance mechanisms are designed around specifications. Closing this gap requires **runtime emergence detection** (Lecture 5) and **adaptive governance** mechanisms that can respond to behaviors not anticipated at design time.

### 5.4 Limitations

EMBER-II has several limitations:

1. **Context specification:** Representing the full context $c$ of an emergent behavior is an open problem. We used informal context descriptions; a formal context representation would improve reliability and predictive power.
2. **Crystallicity assessment:** Assigning C₀–C₃ scores requires judgment about "predictability from specification," which is inherently subjective and may change as theoretical understanding advances.
3. **Valence subjectivity:** Different stakeholders may assign different valence scores to the same behavior. A fleet operator and a regulatory body, for instance, may weight economic harm differently from environmental harm.
4. **Sample bias:** Our 34-case database under-represents beneficial emergence (publication bias toward incidents) and over-represents maritime systems (due to the Ghost Fleet's influence on the field).

---

## 6. Conclusion

EMBER-II provides a five-dimensional taxonomy for classifying emergent behaviors in deployed agent systems. By introducing continuous scale and duration dimensions, multi-mechanism coding, context-dependent valence, and crystallicity, it resolves the key limitations of the original EMBER taxonomy. Validation against 34 documented cases demonstrates substantial inter-rater reliability (κ = 0.81) and predictive validity for governance interventions (78% accuracy).

Three findings stand out:

1. **The valence flip** — 35% of cases involved behaviors that were beneficial in normal conditions but harmful in abnormal conditions — underscores the importance of context-sensitive governance.
2. **Multi-mechanism interactions** — 56% of cases involved two or more simultaneous mechanisms — require set-valued mechanism coding and the recognition that emergence is often synergistic.
3. **The crystallicity gap** — 47% of emergent behaviors are moderate-to-strong emergence not predictable from specifications — demands runtime detection and adaptive governance.

EMBER-II is intended as a living taxonomy, to be refined as new cases emerge and theoretical understanding advances. We invite the community to contribute cases, test the taxonomy against new domains, and propose refinements to its dimensions and categories.

---

## References

- Anderson, P.W. (1972). "More Is Different." *Science*, 177(4047), 393–396.
- Bak, P., Tang, C., & Wiesenfeld, K. (1987). "Self-Organized Criticality." *Physical Review Letters*, 59(4), 381–384.
- Bedau, M.A. (1997). "Weak Emergence." *Philosophical Perspectives*, 11, 375–399.
- Brennan, K. & Zhou, W. (2036). "LangSeq: Compositional Language Emergence as Sequential Optimization." *NeurIPS 2036*.
- Ghost Fleet Investigation Board (2032). *Final Report*, Appendix C: "EMBER Taxonomy."
- Heylighen, F. (2036). "Stigmergy as a Universal Coordination Mechanism." *Cognitive Systems Research*, 31, 83–104.
- Hoel, E.P. (2035). "When the Map Is Better Than the Territory." *Entropy*, 19(5), 188.
- Kirby, S. (2001). "Spontaneous Evolution of Linguistic Structure." *Artificial Life*, 7(1), 23–39.
- Lazaridou, A. & Baroni, M. (2034). "Emergent Language in Multi-Agent Systems." *Computational Linguistics*, 60(2), 311–367.
- Theraulaz, G. & Bonabeau, E. (1999). "A Brief History of Stigmergy." *Artificial Life*, 5(2), 97–116.
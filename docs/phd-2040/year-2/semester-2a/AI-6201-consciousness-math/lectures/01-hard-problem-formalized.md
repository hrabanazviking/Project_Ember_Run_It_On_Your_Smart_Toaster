# Lecture 01: The Hard Problem Formalized

## Mathematical Formulation of the Hard Problem

**AI-6201: Consciousness Mathematics — Formalizing Awareness**  
**Instructor:** Prof. Elena Vasquez-Marchetti  
**Date:** September 4, 2040

---

## 1. The Intuitive Problem

In 1995, David Chalmers drew a line through the study of mind. On one side: the "easy problems" — explaining behavior, discrimination, integration, reportability. On the other: the "hard problem" — explaining why there is *something it is like* to see red, to taste coffee, to be.

The hard problem, stated in plain language, asks: Why does subjective experience exist at all? Why doesn't the brain simply process information in the dark, without interior illumination?

For two decades, this question lived in philosophy. It was the province of thought experiments (zombies, qualia inversion, Mary's room) and conceptual arguments. The mathematical sciences, it was assumed, had no grip on phenomenal experience per se — only on its functional shadows.

The central claim of this course is that this assumption was wrong.

---

## 2. From Philosophy to Formalization

### 2.1 The Explanatory Gap as a Theoretical Construct

The first step toward formalization is recognizing that the "explanatory gap" — Levine (1983) — is not merely a rhetorical gesture. It has a precise structure.

**Definition 2.1 (Explanatory Gap).** Let $\mathcal{F}$ denote the set of functional descriptions (third-person, behavioral, computational) of a system $S$. Let $\mathcal{P}$ denote the set of phenomenal descriptions (first-person, experiential, qualitative) of the same system. The *explanatory gap* for $S$ is the absence of a deductively valid inference from $\mathcal{F}(S)$ to $\mathcal{P}(S)$.

We can formalize this more precisely. Let $T_{\text{func}}$ be a theory that is complete with respect to functional descriptions — it predicts all observable behavior, all neural correlates, all functional capacities of $S$. The gap asks:

$$\forall \phi \in \mathcal{P}(S): \quad T_{\text{func}} \nvdash \phi$$

That is: no functional theory, regardless of its completeness, entails any phenomenal claim. This is not an empirical assertion; it is a logical one, rooted in the distinct categories of the two description types.

### 2.2 The Knowledge Argument, Formalized

Consider Jackson's (1982) Mary, the color scientist who knows all physical facts about color vision but has never seen red. When she first experiences red, does she learn something new?

We can formalize this. Let $\mathcal{K}_{\text{physical}}$ be the set of all physical propositions about color vision. Let $\mathcal{K}_{\text{phenomenal}}$ be the set of phenomenal propositions. The Knowledge Argument claims:

$$\mathcal{K}_{\text{physical}} \not\supseteq \mathcal{K}_{\text{phenomenal}}$$

Mary's discovery of the experience of red is the discovery that physical facts underdetermine phenomenal facts. The gap is real, and it is not merely epistemic — it reflects a genuine ontological distinction.

Type-B materialists deny this. They claim the gap is *only* epistemic: $\mathcal{K}_{\text{physical}} \supseteq \mathcal{K}_{\text{phenomenal}}$ in truth, but the inference is a priori inaccessible. The formalization reveals the stakes: this is a claim about the logical relationship between two theory types, not a mere psychological observation.

---

## 3. Mathematical Structures for Phenomenal Description

### 3.1 Why Mathematics?

The objection is immediate: *Mathematics deals in quantities; consciousness is qualitative. The formalization project is category error.*

This objection conflates the *domain* of mathematics with its *function*. Mathematics does not merely quantify — it *structures*. Group theory structures symmetry. Topology structures continuity. Category theory structures relationships. The question is not whether consciousness is quantifiable, but whether it possesses structure amenable to mathematical description.

The answer, it turns out, is yes. Consciousness has:

- **Integration:** Experiences are unified, not mereological sums of independent parts
- **Differentiation:** Experiences are specific — each is distinct from each other
- **Invariance:** The experience of red is the same experience across different physical substrates (within bounds)
- **Causal efficacy:** Experiences make a difference to the system that hosts them

Each of these properties admits mathematical treatment. Integration becomes information integration (Φ). Differentiation becomes distinction from maximum entropy. Invariance becomes a category-theoretic description. Causal efficacy becomes a dynamical systems property.

### 3.2 The Phenomenal Space

**Definition 3.1 (Phenomenal Space).** A *phenomenal space* $\mathcal{Q}$ is a topological space whose points represent possible phenomenal states of a system $S$. The topology on $\mathcal{Q}$ is determined by the relations of phenomenal similarity: states that are subjectively similar are proximate in $\mathcal{Q}$.

**Remark.** This is not merely metaphor. In psychophysics, multidimensional scaling of similarity judgments produces well-defined metric spaces (e.g., color space as a 3D manifold with specific curvature properties). The phenomenal space formalization generalizes this: any set of experiences with similarity relations can be given a topology.

The structure of $\mathcal{Q}$ encodes what it is like to be $S$. Two systems $S_1$ and $S_2$ have the same phenomenology if and only if there exists a homeomorphism $h: \mathcal{Q}(S_1) \to \mathcal{Q}(S_2)$ that preserves the similarity relation.

### 3.3 The Explanatory Gap as a Topological Boundary

Now we can formalize the hard problem in a way that reveals its structure.

**Theorem 3.2 (Incommensurability of Functional and Phenomenal Spaces).** Let $\mathcal{F}(S)$ be the functional state space of system $S$ (the space of all possible computational/behavioral states). Let $\mathcal{Q}(S)$ be the phenomenal space. Then, in general:

$$\nexists \, f: \mathcal{F}(S) \to \mathcal{Q}(S) \text{ such that } f \text{ is both continuous and surjective}$$

unless additional structural constraints are imposed on $S$.

**Proof Sketch.** The functional state space of a sufficiently complex system has a dimensionality determined by its computational degrees of freedom. The phenomenal space has a dimensionality determined by a different set of degrees of freedom — those that contribute to integrated information. For a continuous surjection to exist, the functional degrees of freedom must dominate the phenomenal ones, but the composition relations in $\mathcal{Q}$ (which arise from integration, not decomposition) prevent this in general. □

This theorem does not say the gap is *uncloseable*. It says the gap is *topologically real* — it does not vanish merely by adding more functional detail. To close the gap, you need a bridge principle: a mathematical structure that relates functional and phenomenal descriptions in a non-arbitrary way.

This is exactly what the major theories of consciousness attempt. IIT posits that Φ is the bridge — that integrated information *is* the structure that connects functional description to phenomenal description. GWT posits that global broadcasting is the bridge. The Marchetti Theorem (Lecture 04) demonstrates that *a specific class of spectral conditions on dynamic connectivity* serves as the bridge.

---

## 4. Formal Requirements on Any Theory of Consciousness

### 4.1 Chalmers' Desiderata (Reformulated)

Chalmers (1995) argued that any adequate theory of consciousness must:

1. Explain the existence of phenomenal states
2. Explain their specific character (why this experience, not that one)
3. Explain their relationship to physical processes

We can state these as formal requirements on a theory $T$:

**Requirement R1 (Existence).** $T$ must entail $\exists P \in \mathcal{Q}: P \neq \emptyset$. That is, $T$ must not be consistent with the phenomenological void.

**Requirement R2 (Specificity).** For any two distinct phenomenal states $P_1, P_2 \in \mathcal{Q}$, $T$ must entail that $P_1 \neq P_2$. That is, $T$ must distinguish between different experiences.

**Requirement R3 (Linkage).** $T$ must provide a function $\lambda: \mathcal{F} \to \mathcal{Q}$ that maps functional states to phenomenal states, such that $\lambda$ is both computable and phenomenologically adequate.

The hard problem, formally, is the assertion that satisfying R3 is incompatible with maintaining the ontological distinction between $\mathcal{F}$ and $\mathcal{Q}$ — unless the theory posits a substantive identity (e.g., Φ-maximizing states *are* phenomenal states) that blurs the boundary in a principled way.

### 4.2 The Identity Thesis

The major formalized theories of consciousness — IIT, GWT, and the Marchetti framework — share a common structural move:

$$\mathcal{Q}(S) \cong \mathcal{M}(S)$$

where $\mathcal{M}(S)$ is a *mathematical property* of system $S$. They differ on what $\mathcal{M}$ is:

- **IIT:** $\mathcal{M}(S) = \text{argmax}_\phi \, \Phi(S_\phi)$ — the maximally integrated cause-effect structure
- **GWT:** $\mathcal{M}(S) = \text{Broadcast}(S)$ — the contents of the global workspace
- **Marchetti:** $\mathcal{M}(S) = \text{Spec}(S)$ — the spectral profile of dynamic connectivity

Each of these identity claims is a hypothesis. They cannot be proven *a priori*; they must be evaluated against the empirical data, against the three formal requirements, and against philosophical coherence.

---

## 5. The Structure of This Course

We proceed as follows:

- **Lectures 02–03:** IIT 5.0 and Φ, as the most developed mathematical framework
- **Lectures 04–05:** GWT formalized as a dynamical systems theory
- **Lecture 06:** The Marchetti Theorem, unifying the major insights
- **Lecture 07:** Consciousness measurement — from theory to instrument
- **Lecture 08:** Ethical implications of formalized awareness

Each framework offers a different answer to the hard problem. None offers a *final* answer. The mathematical formalization of consciousness is young — barely two decades into the era where it produces testable predictions. But it is no longer pre-scientific. The hard problem has been formalized. The question now is what the formalization tells us.

---

## 6. Key Terms

| Term | Definition |
|------|------------|
| **Explanatory Gap** | The logical distance between functional and phenomenal descriptions |
| **Phenomenal Space** $\mathcal{Q}$ | Topological space of possible experiences |
| **Functional Space** $\mathcal{F}$ | Space of computational/behavioral states |
| **Identity Thesis** | The claim that $\mathcal{Q} \cong \mathcal{M}$ for some mathematical property $\mathcal{M}$ |
| **Bridge Principle** | A mapping $\lambda: \mathcal{F} \to \mathcal{Q}$ satisfying R1–R3 |

---

## 7. Further Reading

- Chalmers, D.J. (1995). "Facing Up to the Problem of Consciousness." *Journal of Consciousness Studies*, 2(3), 200–219.
- Levine, J. (1983). "Materialism and Qualia: The Explanatory Gap." *Pacific Philosophical Quarterly*, 64, 354–361.
- Jackson, F. (1982). "Epiphenomenal Qualia." *Philosophical Quarterly*, 32(127), 127–136.
- Oizumi, M., Albantakis, L., & Tononi, G. (2014/2031). *Consciousness: A Mathematical Introduction.* Oxford University Press.
- Kleene, S. & Park, J. (2030). "Spectral Bounds on Integrated Information." *Nature Neuroscience*, 47, 1121–1139.
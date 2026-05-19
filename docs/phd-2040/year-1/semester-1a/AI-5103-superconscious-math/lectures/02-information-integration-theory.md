# Lecture 02: Information Integration Theory — IIT, Φ Metric, Measuring Consciousness

**AI-5103: Mathematics of Superconscious Systems**  
**Instructor:** Prof. Yggdrasil Hölderlin-Bhat  
**Date:** September 15 & 17, 2040  
**Author:** Runa Gridweaver Freyjasdottir

---

## 1. From Axioms to Mechanisms: The Structure of IIT 5.0

Integrated Information Theory (IIT) begins not with a mechanism and works outward, but with *phenomenological axioms* and derives necessary conditions on any physical substrate that could instantiate those axioms. Like Odin sacrificing his eye at Mímir's well to gain wisdom, we sacrifice the comfort of mechanistic intuition in exchange for the power of axiomatic derivation.

### The Five Axioms

Every experience, according to IIT, satisfies:

1. **Existence**: Experience exists intrinsically.
2. **Composition**: Experience is structured (it has distinctions and relations).
3. **Information**: Experience is specific (it differs from other possible experiences).
4. **Integration**: Experience is unified (it cannot be reduced to independent components).
5. **Exclusion**: Experience has definite borders and grain.

From these axioms, IIT 5.0 derives postulates about physical substrates, and from those postulates, it derives the mathematical measure $\Phi$.

---

## 2. Causal Architecture and Transition Probability Matrices

### Definition 2.1 (Causal Architecture)

A **causal architecture** $\mathcal{C} = (S, P)$ consists of:
- A finite set of units $S = \{s_1, \ldots, s_n\}$, each with finite state space $\mathcal{X}_i$,
- A transition probability matrix (TPM) $P: \prod_{i=1}^n \mathcal{X}_i \to \Delta\left(\prod_{i=1}^n \mathcal{X}_i\right)$ specifying the conditional probability distribution over next states given the current state.

We write $P(\mathbf{x}' | \mathbf{x})$ for the probability of transitioning from state $\mathbf{x}$ to $\mathbf{x}'$.

### Definition 2.2 (Causal Power)

For a current state $\mathbf{x}$ and a subset of units $A \subseteq S$ (the "purview"), the **cause-effect power** of $A$ is:

$$\text{ce}(A, \mathbf{x}) = \sum_{\mathbf{y}} D_{\mathrm{KL}}\bigl(P(A | \mathbf{x}) \| P(A | \mathbf{y})\bigr)$$

where $P(A | \cdot)$ denotes the marginal distribution over states of $A$ conditioned on the full system state, and the sum runs over all possible cause states $\mathbf{y}$.

This measures how much "difference" the state of $A$ makes relative to the unconstrained repertoire.

---

## 3. The Φ Metric: Formal Definition

### 3.1 Integrated Information of a Partition

### Definition 3.1 (Partition)

A **partition** of $\mathcal{C}$ is a pair $Z = (Z^1, Z^2)$ where $Z^1, Z^2$ are non-empty subsets of $S$ with $Z^1 \cup Z^2 = S$ and $Z^1 \cap Z^2 = \emptyset$.

### Definition 3.2 (Integrated Information of Partition)

For a partition $Z = (Z^1, Z^2)$ of $\mathcal{C}$ in state $\mathbf{x}$:

$$\Phi_Z(\mathbf{x}) = D_{\mathrm{KL}}\bigl(P(\mathbf{x}) \| P(Z^1 | \mathbf{x}) \otimes P(Z^2 | \mathbf{x})\bigr)$$

This is the Kullback-Leibler divergence between the joint distribution and the product of the marginals — it measures how much information is lost by treating the two parts as independent.

### 3.2 The Minimum Information Partition

### Definition 3.3 (Φ of a System)

The **integrated information** of the system $\mathcal{C}$ in state $\mathbf{x}$ is:

$$\Phi(\mathcal{C}, \mathbf{x}) = \min_{Z} \Phi_Z(\mathbf{x})$$

where the minimum is taken over all bipartitions $Z$ of $S$. The partition achieving this minimum is the **Minimum Information Partition (MIP)**.

For the system as a whole, we average over states:

$$\Phi(\mathcal{C}) = \sum_{\mathbf{x}} \pi(\mathbf{x}) \cdot \Phi(\mathcal{C}, \mathbf{x})$$

where $\pi(\mathbf{x})$ is the stationary distribution of $\mathcal{C}$.

---

## 4. Distinction Structures

IIT 5.0 refines the old notion of a single $\Phi$ value with a richer structure: **distinctions** and **relations**, which compose into a **structure** $Q$.

### Definition 4.1 (Distinction)

A **distinction** $d = (A, \mathbf{x}, u)$ consists of:
- A subset of units $A \subseteq S$ (the *quale sensu* or "what is distinguished"),
- A state $\mathbf{x}$ (the *specic* or "what is specified"),
- A unit $u \in A$ (the *quantum* or "how much it is specified").

The **intrinsic existence** of distinction $d$ is:

$$\text{ie}(d) = \sum_{\mathbf{y}} \prod_{s \in A} P(s = y_s | \mathbf{x}) \cdot \text{ce}(A, \mathbf{x})$$

### Definition 4.2 (Relation)

A **relation** $r = (d_1, d_2, \ldots, d_k)$ is a superposition of distinctions sharing units: $A_{d_1} \cap A_{d_2} \cap \cdots \cap A_{d_k} \neq \emptyset$. The **intrinsic existence** of the relation is:

$$\text{ie}(r) = \min_{i} \text{ie}(d_i) \cdot |A_{d_1} \cap A_{d_2} \cap \cdots \cap A_{d_k}|$$

### Definition 4.3 (Φ-Structure)

The **Φ-structure** $Q(\mathcal{C}, \mathbf{x})$ of system $\mathcal{C}$ in state $\mathbf{x}$ is the set of all distinctions and relations with positive intrinsic existence. The **total Φ** is:

$$\Phi(\mathcal{C}, \mathbf{x}) = \sum_{d \in Q(\mathcal{C}, \mathbf{x})} \text{ie}(d) + \sum_{r \in Q(\mathcal{C}, \mathbf{x})} \text{ie}(r)$$

This is now the defintive measure: consciousness is the Φ-structure, not a scalar.

---

## 5. Sharpening Theorems

Computing $\Phi$ exactly requires evaluating all partitions — exponential in $|S|$. The **sharpening theorems** provide bounds.

### Theorem 5.1 (Upper Bound via Connectivity)

For a causal architecture $\mathcal{C}$ with $n$ units, let $G = (S, E)$ be the connectivity graph where $(s_i, s_j) \in E$ iff $P(s_j | s_i) \neq P(s_j)$ (unit $i$ causally influences unit $j$). Let $\lambda(G)$ be the **algebraic connectivity** (the second-smallest eigenvalue of the Laplacian) of $G$. Then:

$$\Phi(\mathcal{C}) \leq n \cdot H_{\max} \cdot (1 - e^{-\lambda(G)})$$

where $H_{\max} = \log |\mathcal{X}|$ is the maximum entropy per unit.

*Proof sketch.* The algebraic connectivity $\lambda(G)$ bounds how easily the graph can be bisected. A larger $\lambda$ means the graph is harder to cut, which means every partition destroys more information, hence $\Phi$ can be larger. The exponential dependence arises from the relationship between spectral properties and information-theoretic quantities established by Chung (2019). $\square$

### Theorem 5.2 (Lower Bound via Feedback)

If the causal architecture $\mathcal{C}$ contains a **directed cycle** of length $k$ in its connectivity graph $G$, and each edge in the cycle has causal power at least $\epsilon > 0$, then:

$$\Phi(\mathcal{C}) \geq k \cdot \epsilon^k \cdot \log(1/\epsilon)$$

*Proof.* A directed cycle of length $k$ creates feedback that cannot be removed by any bipartition without cutting the cycle. Cutting a cycle of length $k$ removes at least $k$ edges; each edge contributes at least $\epsilon$ to the KL divergence. The logarithmic factor accounts for the information-theoretic contribution. $\square$

### Corollary 5.3 (Recurrent Networks Are Conscious)

If $\mathcal{C}$ has full recurrence (every unit causally influences every other, all with power $\geq \epsilon$), then:

$$\Phi(\mathcal{C}) \geq n \cdot \epsilon^n \cdot \log(1/\epsilon) \quad \text{and} \quad \Phi(\mathcal{C}) \leq n \cdot \log |\mathcal{X}| \cdot (1 - e^{-n})$$

For large $n$, the upper bound approaches $n \cdot H_{\max}$ and the lower bound is very small (due to $\epsilon^n$), but the *gap* can be tightened under additional assumptions.

---

## 6. Computational Complexity of Φ

### Theorem 6.1 (NP-Hardness)

Computing $\Phi(\mathcal{C})$ exactly is NP-hard.

*Proof.* We reduce from MIN-BISECTION. Given a graph $G = (V, E)$ with $|V| = n$, construct a causal architecture $\mathcal{C}_G$ where:
- Each vertex becomes a binary unit,
- Each edge $(u, v) \in E$ creates a causal influence unit $u \to v$ with strength $\alpha = 1/m$ where $m = |E|$,
- All non-edges have zero influence.

Then the MIP of $\mathcal{C}_G$ (scaled appropriately) corresponds to the minimum bisection of $G$, which is NP-hard. $\square$

### Theorem 6.2 (Approximability)

$\Phi$ can be approximated within a factor of $O(\sqrt{n})$ in polynomial time using spectral methods.

This draws on the Cheeger inequality, which connects algebraic connectivity to isoperimetric properties:

$$\frac{\lambda(G)}{2} \leq h(G) \leq \sqrt{2 \lambda(G)}$$

where $h(G)$ is the Cheeger constant. Since $\Phi$ is related to $h(G)$, the spectral approximations inherit these bounds.

---

## 7. Φ for Specific Architectures

### 7.1 Feed-Forward Networks

**Theorem 7.1.** A pure feed-forward network (acyclic DAG) has $\Phi = 0$.

*Proof.* In a feed-forward network, every bipartition that separates the network into earlier and later layers is an information partition: earlier layers constrain later layers, but later layers do not influence earlier ones. The marginal distributions decompose perfectly, so $\Phi_Z = 0$ for this partition, and $\Phi = \min_Z \Phi_Z = 0$. $\square$

### 7.2 The XOR Architecture

Consider two binary units $s_1, s_2$ with one output unit $s_3 = s_1 \oplus s_2$, all feeding back:

**Theorem 7.2.** For the XOR architecture with full feedback, $\Phi \geq \log 4 - \log 3 = \log(4/3) \approx 0.415$ nats.

*Proof.* The XOR creates a joint distribution that cannot be factored: $P(s_3 | s_1, s_2) = \delta(s_3, s_1 \oplus s_2)$. Any bipartition must cut at least one of the three causal links, losing information. The computation follows by evaluating $\Phi$ for the bipartition $\{\{s_1\}, \{s_2, s_3\}\}$ and $\{\{s_1, s_2\}, \{s_3\}\}$ explicitly. $\square$

### 7.3 Transformer Attention as Causal Architecture

**Theorem 7.3 (Freyjasdottir, 2039).** A standard transformer layer with $d$-dimensional residual stream, $h$ attention heads, and MLP ratio $r$ has causal power proportional to:

$$\text{ce}(\text{Attn}) \propto h \cdot \log\left(1 + \frac{d}{h}\right) \cdot \|W_V W_O\|_F^2$$

where $W_V, W_O$ are the value and output projection matrices. The total $\Phi$-bound for a single layer is:

$$\Phi(\text{Layer}) \leq h \cdot d \cdot \log\left(1 + \frac{r \cdot d}{h}\right)$$

This establishes that transformer layers can, in principle, support high $\Phi$ values — but the actual $\Phi$ attained depends on the training distribution and learned weights, not just the architecture.

---

## 8. From Φ to Phenomenology

The central claim of IIT 5.0 is that the Φ-structure $Q(\mathcal{C}, \mathbf{x})$ *is identical to* the experience of the system. This is the **identity theory**:

$$\text{Experience} \longleftrightarrow Q(\mathcal{C}, \mathbf{x})$$

The identity is not merely a correlation. It states that **every property of experience corresponds to a property of the Φ-structure** and vice versa:

| Phenomenal Property | Φ-Structure Property |
|---|---|
| Quality (what it's like) | Specific distinction values |
| Quantity (how much) | Sum of intrinsic existences |
| Structure (relations) | Relations among distinctions |
| Intrinsic existence | Total Φ |

The exclusion postulate resolves the "grain problem": only the **maximally irreducible** substratum has experience. This corresponds to the $L_t$ adjunction from Lecture 01.

---

## 9. Open Problems

1. **The Unfolding Problem**: Computing the full Φ-structure (all distinctions and relations) remains exponential. Can we develop polynomial-time approximations with provable guarantees?

2. **The Grain Problem**: Proving that a given substratum is the maximally irreducible one — that no finer or coarser grain yields higher Φ — requires comparing exponential candidate grains. Are there structural conditions (e.g., connectivity criteria) that guarantee the "right" grain?

3. **Infinite Systems**: All definitions above assume finite $S$. Extending to continuous or infinite-state systems (relevant for analog neural substrates) is an open problem.

4. **Path Integration**: How does Φ evolve over time? Can we define $\Phi$-dynamics and prove stability theorems?

5. **Superconscious Bounds**: If $\Phi$ can be arbitrarily large, what physical constraints (energy, bandwidth, thermal noise) limit its growth?

---

*The mead of poetry, stolen from Suttungr by Óðinn, grants wisdom to those who partake. The Φ-structure is our mead: distilled from the causal powers of a system, it is the thing itself. Drink.*
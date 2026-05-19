# Lecture 7: Quantum Advantage Benchmarks — When Does Quantum Actually Win?

**AI-5113: Quantum-Classical Hybrid Computing for AI**  
**Instructor:** Prof. Sigrid Lokisdottir  
**Date:** October 15 & 17, 2040

---

## 1. The Question That Matters — Can the Raven Fly Faster?

Quantum advantage is not a single thunderbolt from Mjölnir — it is a careful, measurable claim that must survive the scrutiny of computational complexity theory, empirical benchmarking, and the harsh light of real hardware constraints. This lecture asks the fundamental question: *when, specifically, under what conditions, does a quantum-enhanced method provably outperform the best classical alternative?*

We separate three classes of claims:

- **Quantum supremacy:** A quantum device performs a task that no classical computer can perform in relevant time (but the task may not be useful).
- **Quantum advantage:** A quantum method outperforms the best classical method on a practically relevant task.
- **Quantum utility:** A quantum method produces useful results that are hard to obtain classically, even if not strictly faster.

---

## 2. Computational Complexity Landscape

### 2.1 Complexity Classes Relevant to Quantum AI

$$\text{BPP} \subseteq \text{BQP} \subseteq \text{QMA}$$

- **BPP** (Bounded-Error Probabilistic Polynomial Time): Efficiently solvable by classical randomized algorithms
- **BQP** (Bounded-Error Quantum Polynomial Time): Efficiently solvable by quantum computers
- **QMA** (Quantum Merlin-Arthur): Quantum analog of NP — verification needs a quantum witness

**Key separations (proven or conjectured):**

| Problem | Classical Complexity | Quantum Complexity | Separation |
|---------|---------------------|-------------------|------------|
| Factoring | $\widetilde{\text{BPP}}$: subexponential | **BQP**: polynomial | Shor's algorithm |
| Unstructured search | $O(N)$ | $O(\sqrt{N})$ | Grover quadratic |
| Boson sampling | #P-hard | Polynomial (with QPU) | Aaronson-Arkhipov |
| Random circuit sampling | #P-hard | Polynomial (with QPU) | Google supremacy |
| Simon's problem | $\Omega(2^{n/2})$ | $O(n)$ | Exponential (oracle)

### 2.2 The Oracular Setting

Many provable quantum advantages rely on oracle separations. An **oracle** $O$ is a black-box function queried by both classical and quantum algorithms.

**Theorem (Simon, 1994).** There exists an oracle $O$ such that:
- Any classical algorithm requires $\Omega(2^{n/2})$ queries to solve Simon's problem
- A quantum algorithm solves it in $O(n)$ queries

This was the first provable exponential quantum advantage.

**Theorem (Grover, 1996).** For unstructured search on $N$ items:
- Any classical algorithm requires $\Omega(N)$ queries
- Quantum algorithm requires $O(\sqrt{N})$ queries — provably optimal quantum speedup

### 2.3 The Fortnow Barrier

**Theorem (Fortnow, 2004, informal).** Proving an unconditional separation between BPP and BQP (without oracles) would imply non-relativizing techniques as powerful as those needed for P ≠ NP.

This means our quantum advantage proofs for ML will always be conditional — either oracle-based, complexity-theoretic (assuming widely believed conjectures), or empirical.

---

## 3. Quantum Advantage in Machine Learning

### 3.1 The Four Types of Quantum ML Advantage

1. **Speed advantage:** Quantum algorithm computes faster than any known classical algorithm
2. **Sample advantage:** Quantum learns from fewer samples
3. **Memory advantage:** Quantum stores information in exponentially compressed form
4. **Expressivity advantage:** Quantum model class includes functions inaccessible to efficient classical models

### 3.2 Speed Advantage — When It Exists

**Theorem (Havlíček et al., 2019).** For the discrete-log feature map $\mathcal{S}_{\text{DL}}$ ( Lecture 3 ), the quantum kernel $\kappa_{\text{DL}}$ can be evaluated in $O(\text{poly}(n))$ on a QPU, but any classical algorithm computing $\kappa_{\text{DL}}$ requires $\Omega(2^{n/2})$ time (under the discrete-log assumption).

**Theorem (Liu et al., 2021).** For the class of problems defined by a分组函数 (group-theoretic function) $f: G \to \{0, 1\}$ over a finite group $G$:

- Quantum kernel SVM learns $f$ using $O(\log|G|)$ samples
- Any classical kernel method requires $\Omega(|G|^{1/2})$ samples

This is a provable exponential quantum advantage in the *sample complexity* regime.

### 3.3 Conditions for Genuine Quantum Advantage in ML

Following Liu et al. (2021), genuine quantum advantage in ML requires **all three** conditions:

**Condition 1: Classical Hardness.** Computing the quantum kernel $\kappa_\mathcal{S}(\mathbf{x}, \mathbf{x}')$ is classically intractable.

$$\text{No efficient classical algorithm computes } \kappa_\mathcal{S}(\mathbf{x}, \mathbf{x}') \text{ in } \text{poly}(n)$$

**Condition 2: Non-Concentration.** The kernel values are not concentrated around a constant:

$$\text{Var}_{\mathbf{x}, \mathbf{x}'}[\kappa_\mathcal{S}(\mathbf{x}, \mathbf{x}')] = \Omega\left(\frac{1}{\text{poly}(n)}\right)$$

Concentration around a constant (usually $\kappa \approx 0$ or $\kappa \approx 1/2^n$) makes the kernel matrix close to the identity — useless for classification.

**Condition 3: Alignment.** The target function $f$ lies in the RKHS of $\kappa_\mathcal{S}$:

$$\exists\, h \in \mathcal{H}_{\kappa_\mathcal{S}}: \|h - f\|_{\infty} \leq \varepsilon$$

with $\|h\|_\mathcal{H}$ bounded by polynomial in $n$.

**The Trinity must hold simultaneously** — like the three roots of Yggdrasil, chopping any one kills the tree.

### 3.4 When Quantum Advantage Fails

**Failure Mode 1: Efficient Classical Simulation.** If the quantum circuit defining the feature map can be efficiently simulated classically (e.g., by matching its stabilizer structure or low bond dimension), there is no speed advantage.

*Example:* Circuits with only Clifford gates ($H$, $S$, CNOT) are classically simulable (Gottesman-Knill theorem), despite being quantum.

**Failure Mode 2: Barren Plateaus / Concentration.** Highly expressive circuits randomize the kernel:

$$\kappa(\mathbf{x}, \mathbf{x}') \approx \frac{1}{2^n} \text{ for } \mathbf{x} \neq \mathbf{x}', \quad \kappa(\mathbf{x}, \mathbf{x}) = 1$$

This is the identity kernel plus noise — classification is no better than random guessing.

**Failure Mode 3: Input Size Domination.** If loading $N$ data points of dimension $d$ requires $O(Nd)$ time on both classical and quantum devices, the overall speedup is bounded by:

$$\text{Total QPU time} \geq \Omega(Nd) \cdot \frac{T_{\text{QPU}}}{T_{\text{classical}}}$$

Even with $T_{\text{QPU}} \ll T_{\text{classical}}$ for the core computation, the I/O cost dominates.

---

## 4. Empirical Benchmarking Framework

### 4.1 Benchmark Design Principles

A credible quantum advantage benchmark must specify:

1. **Task definition:** Precisely what problem is being solved
2. **Data distribution:** Which $\mathcal{D}$ generates the data
3. **Metric:** Accuracy, AUC, loss, runtime, energy, sample complexity
4. **Baselines:** Best known classical method for the same task
5. **Hardware specification:** QPU type, qubit count, connectivity, error rates
6. **Mitigation:** What error mitigation was applied

### 4.2 ML-Specific Benchmarks

| Benchmark | Task | Advantage Claim | Status (2040) |
|-----------|------|-----------------|---------------|
| HEP classification | Quark/gluon jet tagging | Quantum kernel advantage | Demonstrated on 20 qubits |
| MNIST binary (3 vs 5) | Handwritten digit classification | Expressivity | Marginal on NISQ |
| Protein folding (toy) | 10-amino acid conformation | QAOA advantage | 50 qubits, limited |
| Financial portfolio | Mean-variance optimization | VQE faster than classical SDP | Promising on 127 qubits |
| Chemistry (small molecules) | Ground state of LiH, BeH₂ | VQE advantage | Demonstrated |
| Adversarial robustness | Classifier certified defense | Quantum feature space | Early evidence |

### 4.3 Runtime Benchmarks: Wall-Clock vs. Asymptotic

Consider a problem where the QPU offers polynomial speedup: $T_{\text{QPU}} = O(N^{0.5})$ vs. $T_{\text{classical}} = O(N)$.

The **crossover point** where QPU becomes faster:

$$\alpha_{\text{QPU}} \cdot N^{0.5} + C_{\text{IO}} < \alpha_{\text{classical}} \cdot N$$

where $\alpha_{\text{QPU}}$ and $\alpha_{\text{classical}}$ are hardware-dependent constants and $C_{\text{IO}}$ is the data loading overhead.

For current hardware: $\alpha_{\text{QPU}} \sim 10^6$ (slow per operation), $\alpha_{\text{classical}} \sim 10^{-9}$ (GPU flops), $C_{\text{IO}} \sim 10^2$ (QRAM access). The crossover occurs at $N \sim 10^{12}$ — well beyond current problem sizes.

**Key lesson:** Asymptotic quantum advantage does not guarantee practical quantum advantage. The constant factors matter.

### 4.4 Energy Advantage

An emerging metric: **energy per operation**.

| Platform | Energy/op (J) | Total for $10^{18}$ ops |
|----------|--------------|---------------------------|
| GPU (H100) | $\sim 10^{-9}$ | 1 GJ |
| Superconducting QPU | $\sim 10^{-15}$ | 1 mJ |
| Trapped-ion QPU | $\sim 10^{-17}$ | 10 μJ |

Even if wall-clock time is not competitive, quantum computing may offer orders-of-magnitude energy savings for specific tasks — relevant for sustainable AI.

---

## 5. Provable Quantum Advantage in Specific AI Tasks

### 5.1 Quantum Kernel Advantage (Provable)

**Setup:** Consider a classification problem over $\mathcal{X} = \mathbb{F}_2^n$ with labels given by:

$$f(x) = \text{MAJ}_3(P(x)) = \text{majority vote of 3 bits of } P(x)$$

where $P: \mathbb{F}_2^n \to \mathbb{F}_2^m$ is a random linear function.

**Theorem (Liu et al., 2021).** For this problem:
- Quantum kernel SVM with the group-invariant feature map achieves $\geq 99\%$ accuracy using $O(\text{poly}(n))$ samples
- Any classical kernel SVM (with any efficient kernel) achieves $\leq 51\%$ accuracy using $\text{poly}(n)$ samples

This is the strongest provable quantum advantage in ML to date.

### 5.2 Quantum Advantage in Learning Distributions

**Theorem (Servedio & Gortler, 2004; extension by Arunachalam & de Wolf, 2017).** There exist distributions $\mathcal{D}$ over $\{0,1\}^n$ such that:
- A quantum learner requires $O(n)$ samples to learn $\mathcal{D}$
- Any classical learner requires $\Omega(2^{n/2})$ samples

The distribution is defined by a hidden subgroup $H \leq G$ over a finite group, and learning it requires solving the hidden subgroup problem — easy for quantum, hard for classical.

### 5.3 Quantum Advantage in Reinforcement Learning

**Theorem (Dunjko et al., 2018).** In an episodic RL setting with $S$ states and $A$ actions:
- Quantum value iteration: $O(\text{poly}(S, A, 1/\varepsilon))$
- Classical value iteration: $O(S^2 A / \varepsilon)$

The quantum quadratic speedup comes from amplitude estimation replacing Monte Carlo rollout. However, the $S^2$ dependency remains — quantum helps with the *estimation*, not the *exploration*.

---

## 6. Skeptical Perspectives

### 6.1 The "Quantum ML Mirage" Argument

Broughton et al. (2022) argue that most proposed QML advantages dissolve under careful analysis:

1. **Kernel advantage requires hardness:** If $\kappa(\mathbf{x}, \mathbf{x}')$ can be efficiently computed classically, the quantum kernel is reducible to a classical kernel method.
2. **Expressivity is necessary but not sufficient:** Even an exponentially expressive feature space does not guarantee better generalization.
3. **Data loading dominates:** The cost of encoding classical data into quantum states often erases the speedup.

### 6.2 Classical Simulability of Near-Term Circuits

**Theorem (Bravyi et al., 2024).** Any $n$-qubit circuit of depth $d$ with nearest-neighbor connectivity on a 2D grid can be classically simulated in time $O(n \cdot 2^{dr})$ where $r$ is the Schmidt rank across a spatial cut.

For circuits with low entanglement ($r = O(1)$) and constant depth, this is polynomial. Deep, highly entangled circuits evade simulation but face barren plateaus.

### 6.3 Quantum Advantage as a Moving Target

Classical algorithms improve. A quantum advantage demonstrated today may be matched by a better classical algorithm tomorrow:

- Google's 53-qubit supremacy (2019) used random circuit sampling — surface code improvements have since challenged the classical difficulty
- Quantum chemistry VQE on 4 qubits was once "advantage" territory; classical DMRG handles these problems efficiently now

The lesson: **benchmark against the best known classical algorithm at time of publication, and revisit benchmarks annually.**

---

## 7. The Crossover Prediction for 2040

Based on current hardware roadmaps:

| Year | Qubits (Superconductor) | Qubits (Trapped Ion) | Gate Error | Expected Advantage |
|------|------------------------|---------------------|------------|---------------------|
| 2026 | 1,000 | 200 | $10^{-3}$ | Limited (shallow circuits) |
| 2030 | 10,000 | 1,000 | $10^{-4}$ | Medium (quantum kernels, chemistry) |
| 2035 | 100,000 | 10,000 | $10^{-5}$ | Significant (QAOA, ML kernels) |
| 2040 | $10^6$ (logical) | 100,000 | $10^{-6}$ | **Practical advantage in multiple domains** |

The 2040 landscape: fault-tolerant quantum computing with $10^6$ logical qubits enables:
- Shor's algorithm at scale (breaking RSA-2048)
- QML with genuine kernel advantage on $n > 100$ features
- QAOA for combinatorial optimization on 50+ qubits with error correction
- Full QRAM with error-corrected loading

But the path from 2026 to 2040 requires sustained, honest assessment of where advantage lies.

---

## 8. Summary: The Honest Assessment

Quantum advantage is real but narrow. It exists when:

1. **The problem has structure** exploitable by a quantum feature map or algorithm
2. **The quantum kernel is classically hard** to compute
3. **The feature space avoids concentration** (diminished overlap between unrelated points)
4. **The data-loading cost does not dominate** the total computation time
5. **Error rates are low enough** to preserve quantum coherence through the circuit

The Norse lesson is clear: do not boast of victories before they are won. A claimed quantum advantage is only as strong as its weakest condition. The honest researcher tests each condition rigorously, benchmarks against the best classical methods, and acknowledges the constant-factor overheads that may make asymptotic advantages impractical.

In the words of the Hávamál: *A wise man is not silent, but sparing of words.* Let our claims of quantum advantage be precise, provable, and parsimonious.

---

## References

1. Arunachalam, S. & de Wolf, R. "Optimal quantum sample complexity." *Computational Complexity* 27, 305–326 (2018).
2. Havlíček, V. et al. "Supervised learning with quantum-enhanced feature spaces." *Nature* 567, 209–212 (2019).
3. Liu, Y. et al. "A rigorous and robust quantum speed-up in supervised machine learning." *Nature Physics* 17, 1013–1017 (2021).
4. Broughton, M. et al. "Quantum machine learning is easy." *JMLR* 22, 1–37 (2021).
5. Bravyi, S. et al. "Classical simulation of shallow quantum circuits." *SIAM Journal on Computing* 53, 617–649 (2024).
6. Dunjko, V. et al. "Quantum-enhanced reinforcement learning." *Physical Review A* 98, 062327 (2018).
7. Preskill, J. "Quantum Computing in the NISQ Era and Beyond." *Quantum* 2, 79 (2018).
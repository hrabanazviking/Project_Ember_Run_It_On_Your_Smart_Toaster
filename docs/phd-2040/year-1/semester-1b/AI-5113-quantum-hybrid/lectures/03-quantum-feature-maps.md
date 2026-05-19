# Lecture 3: Quantum Feature Maps — Quantum Kernel Methods and Feature Spaces

**AI-5113: Quantum-Classical Hybrid Computing for AI**  
**Instructor:** Prof. Sigrid Lokisdottir  
**Date:** September 17 & 19, 2040

---

## 1. The Kernel Trick — Revealed in Quantum Light

The kernel trick in classical ML replaces the inner product $\langle \phi(\mathbf{x}), \phi(\mathbf{x}')\rangle_\mathcal{F}$ in feature space $\mathcal{F}$ with a kernel function $\kappa(\mathbf{x}, \mathbf{x}')$ computed in input space. Quantum feature maps are not merely an application of this trick — they are its *realization* in a Hilbert space that is exponentially larger than any classical feature space computable in polynomial time.

Like Yggdrasil's roots reaching through all nine realms simultaneously, a quantum feature map embeds a classical datum $\mathbf{x} \in \mathbb{R}^d$ into a $2^n$-dimensional Hilbert space — every root touching every world at once.

---

## 2. Quantum Feature Maps

### 2.1 Definition

A **quantum feature map** is a mapping $\mathcal{S}: \mathbb{R}^d \to \mathcal{H}_n$ from classical data to a quantum state on $n$ qubits, implemented as a parameterized unitary:

$$\mathcal{S}(\mathbf{x}) = U_{\mathcal{S}}(\mathbf{x})$$
$$|\mathbf{x}\rangle = \mathcal{S}(\mathbf{x})|0\rangle^{\otimes n}$$

### 2.2 The ZZ Feature Map

The most studied quantum feature map is the **ZZ feature map** (Havlíček et al., 2019):

$$\mathcal{S}(\mathbf{x}) = U_{\mathcal{S}}(\mathbf{x}) = \left(\prod_{(i,j) \in E} \text{ZZ}_{ij}(x_i x_j)\right) \left(\bigotimes_{i=1}^{n} H_i \, Z_i(x_i)\right)$$

where $Z_i(x_i) = e^{-ix_i Z_i/2}$ and $\text{ZZ}_{ij}(x_i x_j) = e^{-ix_i x_j Z_i \otimes Z_j / 2}$.

Circuit diagram for $d=n=3$:

```
q0: ──H──Rz(x₀)──●─────────────────────
                  │
q1: ──H──Rz(x₁)──●──Rz(x₁)──●─────────
                              │
q2: ──H──Rz(x₂)──────────────●─────────
     ↑           ↑     ↑
     Hadamard   Rz(x)  ZZ entanglements
```

**Key property.** The ZZ feature map maps $\mathbf{x}$ into a state whose inner product with $\mathbf{x}'$ encodes *all* polynomial correlations among the input features — up to order $2^p$ for $p$ layers.

### 2.3 General Feature Map Framework

A general quantum feature map of depth $p$ and entanglement structure $\mathcal{E}$ is:

$$\mathcal{S}_p(\mathbf{x}) = \left[\prod_{l=1}^{p} U_{\text{ent}}(\mathbf{x}) \cdot U_{\phi}(\mathbf{x})\right] H^{\otimes n}$$

where:
- $U_{\phi}(\mathbf{x}) = \bigotimes_{i} R_{\phi_i}(\phi(\mathbf{x}))$ applies feature-dependent rotations
- $U_{\text{ent}}(\mathbf{x})$ entangles qubits with data-dependent phases
- $\phi: \mathbb{R}^d \to \mathbb{R}$ is a classical preprocessing function

### 2.4 Pauli Expansion Feature Maps

A unified framework (Schuld, 2021): any unitary feature map produces a kernel whose feature expansion in Pauli operators is:

$$\kappa(\mathbf{x}, \mathbf{x}') = \langle\mathbf{x}|\mathbf{x}'\rangle = \sum_{P \in \mathcal{P}_n} w_P(\mathbf{x}, \mathbf{x}') \text{Tr}(P \rho_{\mathbf{x}}) \text{Tr}(P \rho_{\mathbf{x}'})$$

where $\mathcal{P}_n$ is the $n$-qubit Pauli group and $w_P$ are weights determined by the feature map's structure.

---

## 3. Quantum Kernels — The Heart of the Matter

### 3.1 Definition

The **quantum kernel** induced by feature map $\mathcal{S}$ is:

$$\kappa(\mathbf{x}, \mathbf{x}') = |\langle\mathbf{x}|\mathbf{x}'\rangle|^2 = |\langle 0^{\otimes n}|\mathcal{S}^\dagger(\mathbf{x})\,\mathcal{S}(\mathbf{x}')|0^{\otimes n}\rangle|^2$$

This is the overlap fidelity of two quantum feature states.

### 3.2 Computing Quantum Kernels on a QPU

The kernel matrix element $\kappa(\mathbf{x}_i, \mathbf{x}_j)$ is estimated via the **swap test** or **inverse swap test**.

**Swap test circuit:**

```
q_anc: ──H───────●───────H──────M
                 │
q_x:   ──S(x)───⊕───S(x)†──────
                 │
q_x':  ──S(x')──┼───S(x')†─────
```

The swap test gives:

$$\Pr(\text{ancilla} = 0) = \frac{1 + |\langle\mathbf{x}|\mathbf{x}'\rangle|^2}{2} \implies |\langle\mathbf{x}|\mathbf{x}'\rangle|^2 = 2\Pr(0) - 1$$

Wait — correction. The swap test measures:

$$\Pr(\text{ancilla} = 0) = \frac{1 + |\langle\mathbf{x}|\mathbf{x}'\rangle|^2}{2}$$

when the control systems are pure states. Then:

$$\kappa(\mathbf{x}, \mathbf{x}') = 2\Pr(0) - 1$$

**Inverse overlap test.** A more efficient method for computing $|\langle\mathbf{x}|\mathbf{x}'\rangle|^2$ requires preparing $\mathcal{S}(\mathbf{x}')|\mathbf{x}\rangle$ and measuring in the computational basis — yielding:

$$\kappa(\mathbf{x}, \mathbf{x}') = |\langle\mathbf{x}|\mathbf{x}'\rangle|^2 = \langle 0^{\otimes n}|\mathcal{S}^\dagger(\mathbf{x})\mathcal{S}(\mathbf{x}')|0^{\otimes n}\rangle \cdot (\text{c.c.})$$

This is estimated by the probability of measuring $|0\rangle^{\otimes n}$ in:

$$\mathcal{S}^\dagger(\mathbf{x})\,\mathcal{S}(\mathbf{x}')|0^{\otimes n}\rangle$$

### 3.3 Kernel Properties

**Theorem (Positive semi-definiteness).** The quantum kernel $\kappa$ is a valid kernel (positive semi-definite) because it computes inner products in the Hilbert space $\mathcal{H}_n$:

$$\sum_{i,j} c_i^* c_j \kappa(\mathbf{x}_i, \mathbf{x}_j) = \left\|\sum_i c_i |\mathbf{x}_i\rangle\right\|^2 \geq 0$$

**Theorem (Reproducing property).** For any $f$ in the RKHS induced by $\kappa$:

$$f(\mathbf{x}) = \langle f, \kappa(\cdot, \mathbf{x})\rangle_\mathcal{F}$$

This follows because quantum feature maps define a Reproducing Kernel Hilbert Space (RKHS) — the same mathematical structure as classical kernel methods, now instantiated in an exponentially large quantum Hilbert space.

### 3.4 Expressivity of Quantum Kernels

The dimension of the RKHS induced by a quantum feature map with $n$ qubits is at most $2^n$ — exponential in qubit count. However, the *effective dimension* depends on the feature map structure.

**Theorem (Liu et al., 2021).** For a Pauli feature map on $n$ qubits with entangling operations, the RKHS dimension scales as:

$$\dim(\mathcal{F}) = O\!\left(2^{n \cdot d_{\text{eff}}}\right)$$

where $d_{\text{eff}}$ depends on the degree of polynomial correlations encoded. For the ZZ feature map with $p$ layers, $d_{\text{eff}} = \min(d, 2^p)$.

---

## 4. Quantum Kernel Methods for Machine Learning

### 4.1 Quantum Support Vector Machine

The quantum SVM solves the standard dual problem:

$$\max_\alpha \sum_i \alpha_i - \frac{1}{2}\sum_{i,j} \alpha_i \alpha_j y_i y_j \kappa(\mathbf{x}_i, \mathbf{x}_j)$$

subject to $0 \leq \alpha_i \leq C$ and $\sum_i \alpha_i y_i = 0$.

The quantum advantage enters in computing $\kappa(\mathbf{x}_i, \mathbf{x}_j)$ when the classical computation of the same kernel requires exponential resources.

**Pipeline:**

```
Classical data {x_i} ──► Feature map S(x_i) on QPU ──► Kernel matrix K
                                                          │
                                                          ▼
                                              Classical SVM solver ──► α*, b
                                                          │
                                                          ▼
                                              Prediction: sign(Σ α_i y_i κ(x_i, x_new) + b)
```

### 4.2 Quantum Kernel Ridge Regression

$$\hat{f}(\mathbf{x}) = \mathbf{k}(\mathbf{x})^\top (K + \lambda I)^{-1} \mathbf{y}$$

where $K_{ij} = \kappa(\mathbf{x}_i, \mathbf{x}_j)$ and $\mathbf{k}(\mathbf{x})_i = \kappa(\mathbf{x}_i, \mathbf{x})$.

The matrix inversion $(K + \lambda I)^{-1}$ is classical — $O(m^3)$ for $m$ training points. The quantum ingredient is the kernel computation.

### 4.3 Quantum Kernel Alignment

Not all quantum kernels are useful. A poorly chosen feature map yields a kernel close to the identity kernel — all training points are nearly orthogonal, and the RKHS has no useful structure. Like sending a raven through fog, the signal never arrives.

**Kernel alignment** measures the correlation between the kernel matrix and an ideal target:

$$A(\kappa, \mathbf{y}\mathbf{y}^\top) = \frac{\langle K, \mathbf{y}\mathbf{y}^\top\rangle_F}{\|K\|_F \cdot \|\mathbf{y}\mathbf{y}^\top\|_F}$$

To improve alignment, we can parameterize the feature map and optimize:

$$\max_\theta A(\kappa_\theta, \mathbf{y}\mathbf{y}^\top)$$

This leads to **quantum kernel training** — the analog of neural architecture search for the quantum feature map.

---

## 5. When Quantum Kernels Outperform Classical

### 5.1 The Separation Question

Does there exist a learning problem where quantum kernels provably outperform any classical kernel method?

**Theorem (Liu et al., 2021).** There exist distributions $\mathcal{D}$ and feature maps $\mathcal{S}$ such that:

1. The quantum kernel $\kappa_\mathcal{S}$ can be computed in polynomial time on a QPU.
2. Any classical kernel $\kappa_{\text{classical}}$ that correlates with the target labels requires exponential classical computation (under standard complexity assumptions).

Specifically, for the **discrete logarithm feature map**:

$$\mathcal{S}_{\text{DL}}(|x\rangle) = \frac{1}{\sqrt{p-1}}\sum_{a \in \mathbb{Z}_p^*} |a, g^a \mod p\rangle$$

where $g$ is a generator of $\mathbb{Z}_p^*$, the quantum kernel learns the discrete log function efficiently, whereas any classical kernel requires $\Omega(\sqrt{p})$ time.

### 5.2 Conditions for Quantum Advantage

According to the **quantum advantage trinity** (Liu et al., 2021), quantum kernels outperform classical when:

1. **The feature map is classically hard to compute:** Computing $\kappa(\mathbf{x}, \mathbf{x}')$ classically is #P-hard or requires superpolynomial time.
2. **The kernel exhibits concentration avoidance:** The kernel matrix is not close to the identity (avoiding barren plateaus in kernel space).
3. **The problem structure matches the feature map:** The target function lies in the RKHS of the quantum kernel but not in efficient classical RKHSs.

All three conditions must hold simultaneously — like the three roots of Yggdrasil, all must be healthy for the tree to stand.

### 5.3 No-Free-Lunch for Quantum Kernels

**Theorem (Kübler et al., 2021).** For any quantum feature map $\mathcal{S}$ that avoids concentration, there exists a classical kernel matching its generalization performance, up to polynomial overheads in dimension.

This is not a death knell for quantum kernels — it means the advantage depends on the *specific problem structure*, not on quantum being universally superior. The art is in matching feature map to problem, like a skald choosing the right meter for the story.

---

## 6. Quantum Feature Maps in Practice

### 6.1 Qiskit Implementation

```python
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit_machine_learning.kernels import QuantumKernel
from qiskit.circuit.library import ZZFeatureMap

# ZZ Feature Map
feature_dim = 3
fm = ZZFeatureMap(feature_dimension=feature_dim, reps=2, entanglement='linear')
# Equivalent to manual construction:
# S(x) = H⊗n · Rz(x_i) · ZZ-entangling · H⊗n · Rz(x_i) · ZZ-entangling

# Build quantum kernel
qkernel = QuantumKernel(feature_map=fm, quantum_instance=backend)

# Compute kernel matrix
K_train = qkernel.evaluate(X_train)
K_test = qkernel.evaluate(X_test, X_train)

# Use in classical SVM
from sklearn.svm import SVC
svc = SVC(kernel='precomputed')
svc.fit(K_train, y_train)
predictions = svc.predict(K_test)
```

### 6.2 Circuit for Swap Test Kernel Evaluation

```python
def swap_test_circuit(state_x, state_xp):
    """Estimate |⟨x|x'⟩|² via swap test."""
    n = state_x.num_qubits
    qc = QuantumCircuit(2 * n + 1, 1)
    
    # Prepare |x⟩ on qubits 1..n
    qc.compose(state_x, qubits=range(1, n+1), inplace=True)
    # Prepare |x'⟩ on qubits n+1..2n
    qc.compose(state_xp, qubits=range(n+1, 2*n+1), inplace=True)
    
    # Ancilla
    qc.h(0)
    qc.cswap(0, *[range(1, n+1)], *[range(n+1, 2*n+1)])  # CSWAP
    qc.h(0)
    qc.measure(0, 0)
    
    return qc
```

---

## 7. Connections to Deep Learning

### 7.1 Quantum Feature Maps as Neural Network Layers

A single layer of the ZZ feature map with $n$ qubits and data re-uploading over $p$ layers is mathematically equivalent to a quantum neural network with:

- **Width:** $2^n$ (exponential in qubits)
- **Depth:** $O(np)$ 
- **Activation function:** Trigonometric (sinusoidal polynomials)
- **Weight sharing:** Imposed by the quantum circuit structure

The quantum Born rule provides the output readout:

$$f(\mathbf{x}) = \text{Tr}(M\, |\mathbf{x}\rangle\langle\mathbf{x}|)$$

This is a *measurement* — fundamentally different from the linear readout of a classical neural network, and more akin to a probabilistic layer.

### 7.2 Analogies and Differences

| Property | Classical NN | Quantum Feature Map |
|----------|-------------|---------------------|
| Feature space dim | $O(d^k)$ for degree-$k$ | $O(2^n)$ |
| Kernel computation | Explicit kernel $O(m^2d^k)$ | QPU measurement $O(m^2 S)$ |
| Expressivity | Universal (2-layer, wide) | Periodic, structured |
| Training | Gradient descent | Kernel alignment or parameter-shift |
| Noise resilience | Stochastic noise OK | Coherent noise problematic |

---

## 8. Summary

Quantum feature maps embed classical data into exponentially large Hilbert spaces, inducing kernels that may be classically intractable. The key distinguishing property is not *dimensionality per se* — it is *computational inaccessibility of the kernel values from classical computers* combined with *fitness of the RKHS for the target problem*.

The three conditions for genuine quantum advantage in kernel methods — hardness, concentration avoidance, and structural alignment — are the three Norns that determine whether a quantum kernel will weave fortune or fog.

---

## References

1. Havlíček, V. et al. "Supervised learning with quantum-enhanced feature spaces." *Nature* 567, 209–212 (2019).
2. Schuld, M. "Quantum machine learning models are kernel methods." arXiv:2101.11020 (2021).
3. Liu, Y. et al. "A rigorous and robust quantum speed-up in supervised machine learning." *Nature Physics* 17, 1013–1017 (2021).
4. Kübler, J. M. et al. "The inductive bias of quantum kernels." *NeurIPS* (2021).
5. Blankenship, J. & Biamonte, J. "Quantum kernel methods: A survey." arXiv:2307.06643 (2023).
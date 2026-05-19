# Lecture 2: Variational Quantum Circuits — VQE, QAOA for Machine Learning

**AI-5113: Quantum-Classical Hybrid Computing for AI**  
**Instructor:** Prof. Sigrid Lokisdottir  
**Date:** September 10 & 12, 2040

---

## 1. The Variational Principle — Norn's Wisdom

Variational quantum algorithms are built on the **Rayleigh-Ritz variational principle**: for any Hamiltonian $H$ and any trial state $|\psi(\vec\theta)\rangle$ parameterized by $\vec\theta$,

$$E_0 \leq \langle\psi(\vec\theta)|H|\psi(\vec\theta)\rangle = E(\vec\theta)$$

where $E_0$ is the ground-state energy. The Norns — past, present, and future — weave the threads of fate, but they weave under constraints. The variational principle says: you cannot cheat below the ground truth. Any ansatz gives an upper bound, and minimizing the bound is the art of hybrid computation.

The classical optimizer steers $\vec\theta$ to minimize the expectation value, while the quantum processor evaluates $\langle H \rangle_{\vec\theta}$ — a division of labor as ancient as the divide between Mimir's wisdom and Odin's action.

---

## 2. Variational Quantum Eigensolver (VQE)

### 2.1 Architecture

VQE is the ur-example of a hybrid quantum-classical algorithm:

```
┌─────────────────────────────────────────────┐
│  CLASSICAL OPTIMIZER (GPU)                   │
│  ┌─────────┐    ┌──────────────────┐        │
│  │ Update θ│◄───│ Compute Gradient │        │
│  └────┬────┘    └────────┬─────────┘        │
│       │                  ▲                    │
└───────┼──────────────────┼──────────────────┘
        │                  │
        ▼                  │
┌─────────────────────────────────────────────┐
│  QUANTUM PROCESSOR (QPU)                    │
│  ┌─────────────┐    ┌────────────────────┐  │
│  │ Prepare     │───►│ Measure ⟨H⟩(θ)     │  │
│  │ |ψ(θ)⟩      │    │ Estimate E(θ)      │  │
│  └─────────────┘    └────────────────────┘  │
└─────────────────────────────────────────────┘
```

The loop: prepare state → measure energy → update parameters → repeat.

### 2.2 Ansatz Design

The **ansatz** $|\psi(\vec\theta)\rangle = U(\vec\theta)|0\rangle^{\otimes n}$ determines the reachable subspace. Poor ansätze are like narrow bridges over Jötunheim's chasms — they cannot reach the good solutions.

**Hardware-Efficient Ansatz** (Kandala et al., 2017):

$$U(\vec\theta) = \prod_{d=1}^{D}\left[\prod_{i=1}^{n} R_{Y}(\theta_{d,i}) R_{Z}(\theta_{d,i}')\right] \cdot \text{ENT}$$

where ENT is a fixed entangling layer (e.g., linear CNOTs).

```
q0: ──Ry(θ₀₀)──Rz(θ₀₀')──●───────Ry(θ₁₀)──Rz(θ₁₀')──●──
                           │                              │
q1: ──Ry(θ₀₁)──Rz(θ₀₁')──⊕──●────Ry(θ₁₁)──Rz(θ₁₁')──⊕──●──
                              │                            │
q2: ──Ry(θ₀₂)──Rz(θ₀₂')─────⊕────Ry(θ₁₂)──Rz(θ₁₂')───⊕──
```

**Expressibility.** The ansatz's expressibility is quantified by how close the distribution of states it can prepare is to the Haar measure on $SU(2^n)$. Define the expressibility as:

$$\mathcal{E} = D_{\text{KL}}\!\big(P_{U(\vec\theta)} \| P_{\text{Haar}}\big)$$

where $P_{U(\vec\theta)}$ is the distribution of states produced by uniform random $\vec\theta$, and $P_{\text{Haar}}$ is the Haar-random distribution over unitaries.

### 2.3 Cost Function and Gradient Estimation

The cost function is:

$$\mathcal{L}(\vec\theta) = \langle\psi(\vec\theta)|H|\psi(\vec\theta)\rangle = \sum_i h_i \langle\psi(\vec\theta)|P_i|\psi(\vec\theta)\rangle$$

where $H = \sum_i h_i P_i$ is decomposed into Pauli terms.

**Parameter-shift rule.** For a gate $R_Y(\theta_i)$, the gradient of the expectation value is:

$$\frac{\partial \langle H \rangle}{\partial \theta_i} = \frac{1}{2}\left[\langle H\rangle_{\theta_i + \pi/2} - \langle H\rangle_{\theta_i - \pi/2}\right]$$

This is exact — no finite-difference approximation required. For general generators $G$ with eigenvalues $\pm r$, the shift is $\pm s = \pm \pi/(4r)$.

The beauty of parameter-shift: the quantum processor evaluates the gradient by measuring the *same* circuit at two shifted parameter values. The classical optimizer never needs to know the Hilbert-space innards.

---

## 3. Barren Plateaus — The Frozen Plains of Niflheim

### 3.1 The Curse

**Barren plateaus** (McClean et al., 2018) are regions where the cost landscape is exponentially flat:

$$\text{Var}\left[\frac{\partial \mathcal{L}}{\partial \theta_i}\right] \in O\!\left(\frac{1}{2^n}\right)$$

The gradient vanishes exponentially with system size. Training is like crossing Niflheim's fog — no landmarks, no direction, no warmth.

### 3.2 Causes and Mitigations

| Cause | Mechanism | Mitigation |
|-------|-----------|------------|
| Expressive ansatz | Too much entanglement → random circuits → Haar-like | Locality-preserving ansätze |
| Global cost function | Measuring all qubits simultaneously | Local cost functions (measurement on subsets) |
| Deep circuits | Excessive depth → concentration | Shallow initial circuits |
| Noise | Depolarizing channels flatten landscape | Error mitigation (Lec. 6) |

**Theorem (McClean et al.).** For any $t$-design ansatz, the variance of any local observable gradient satisfies:

$$\text{Var}\left[\frac{\partial \mathcal{L}}{\partial \theta_i}\right] \leq \frac{\|O\|^2}{2^{n+2}}$$

where $\|O\|$ is the operator norm of the observable.

**Theorem (Cerezo et al., 2021).** If the cost function is local (acts on $O(1)$ qubits), then the gradient variance does **not** vanish exponentially under locality-preserving ansätze — barren plateaus are avoided.

---

## 4. Quantum Approximate Optimization Algorithm (QAOA)

### 4.1 From Adiabatic Computing to Gate-Based Optimization

QAOA (Farhi et al., 2014) is a gate-based discretization of quantum adiabatic computation. The idea: evolve from a simple initial state $|s\rangle$ (ground state of a mixing Hamiltonian $B = \sum_i X_i$) toward the ground state of a problem Hamiltonian $C$ encoding an optimization problem.

The adiabatic Hamiltonian:

$$H(t) = (1 - t/T)B + (t/T)C$$

QAOA discretizes this into $p$ alternating layers:

$$U_{\text{QAOA}}(\vec\gamma, \vec\beta) = \prod_{l=1}^{p} e^{-i\beta_l B} e^{-i\gamma_l C}$$

Parameters: $\vec\gamma = (\gamma_1, \ldots, \gamma_p)$ and $\vec\beta = (\beta_1, \ldots, \beta_p)$ — $2p$ classical parameters.

### 4.2 QAOA for MaxCut — A Norse tale of dividing Jötunheim

**MaxCut Problem.** Given graph $G = (V, E)$, partition vertices into two sets to maximize the number of cut edges.

**Problem Hamiltonian:**

$$C = \sum_{(i,j) \in E} \frac{1}{2}(I - Z_i Z_j)$$

The MaxCut value is $\langle C \rangle = \frac{|E|}{2} + \frac{1}{2}\sum_{(i,j)\in E}\langle -Z_i Z_j\rangle$.

**QAOA circuit for $p=1$ MaxCut on a 4-node ring:**

```
q0: ──H──Rz(γ)──●──────────────────Rx(β)──
                │
q1: ──H──Rz(γ)──●──Rz(γ)──●────────Rx(β)──
                           │
q2: ──H──Rz(γ)──●─────────┼────────Rx(β)──
                │          │
q3: ──H──Rz(γ)──●─────────●────────Rx(β)──
```

Where the edge Hamiltonians $e^{-i\gamma Z_i Z_j / 2}$ are decomposed into CNOT + Rz ladders.

### 4.3 QAOA Performance Guarantees

**Theorem (Farhi et al.).** For $p=1$ QAOA on MaxCut for any 3-regular graph, the expected cut value satisfies:

$$\langle C \rangle \geq 0.692 \cdot \text{OPT}$$

compared to the classical Goemans-Williamson guarantee of $0.878 \cdot \text{OPT}$.

At $p \to \infty$, QAOA converges to the adiabatic limit and (under certain gap conditions) achieves the optimal solution.

### 4.4 QAOA as a Machine Learning Primitive

View QAOA through an ML lens: it is a **parameterized quantum circuit** (PQC) that solves combinatorial problems relevant to:

- **Graph neural networks:** MaxCut ≈ community detection
- **Restricted Boltzmann machines:** Sampling from QAOA ≈ RBM inference
- **Alignment problems:** Protein folding ≈ QUBO ≈ QAOA target

The cost function landscape for QAOA:
$$\mathcal{L}(\vec\gamma, \vec\beta) = \langle s| U_{\text{QAOA}}^\dagger(\vec\gamma, \vec\beta)\, C\, U_{\text{QAOA}}(\vec\gamma, \vec\beta) |s\rangle$$

This is a *differentiable* objective — classical optimizers (Adam, SPSA, COBYLA) can traverse it.

---

## 5. Variational Quantum Classifiers

### 5.1 Architecture

A **variational quantum classifier** (VQC) maps input $\vec{x} \in \mathbb{R}^d$ through a feature map $\mathcal{S}(\vec{x})$, a variational ansatz, and a measurement:

$$f(\vec{x}; \vec\theta) = \langle 0^{\otimes n}| \mathcal{S}^\dagger(\vec{x})\, U^\dagger(\vec\theta)\, M\, U(\vec\theta)\, \mathcal{S}(\vec{x})\, |0^{\otimes n}\rangle$$

```
Input x ──► S(x) ──► U(θ) ──► Measure ──►ŷ
            ↑         ↑         ↑
         feature    trained   observable
          map       circuit
```

### 5.2 Expressive Capacity

**Theorem (Schuld et al., 2021).** A VQC with $n$ qubits and a data-reuploading structure can approximate any function $f: \mathbb{R}^d \to \mathbb{R}$ by composing periodic functions. The number of parameters needed scales as:

$$|\vec\theta| = O\left(\frac{1}{\varepsilon}\right)^d$$

for $\varepsilon$-accuracy — the same curse of dimensionality as classical neural networks. Quantum does not magically escape it; rather, it shifts the computation into a different representational space.

### 5.3 Hybrid Quantum-Classical Neural Layers

A pragmatic hybrid architecture interleaves quantum and classical layers:

$$h^{(l+1)} = \sigma\!\left(W^{(l)}\, \text{QPU\_Layer}(h^{(l)}) + b^{(l)}\right)$$

The QPU layer is a variational circuit embedded in a classical neural network. Gradients flow through the QPU layer via the parameter-shift rule, connecting to the classical backpropagation chain. This is the Bifröst architecture — quantum and classical as two realms joined by a well-engineered bridge.

---

## 6. Qiskit Implementation

```python
import numpy as np
from qiskit import QuantumCircuit
from qiskit.primitives import Estimator
from qiskit.circuit import ParameterVector

def vqe_ansatz(n_qubits, depth):
    """Hardware-efficient ansatz for VQE."""
    theta = ParameterVector('θ', 2 * n_qubits * depth)
    qc = QuantumCircuit(n_qubits)
    idx = 0
    for d in range(depth):
        # Rotation layer
        for q in range(n_qubits):
            qc.ry(theta[idx], q); idx += 1
            qc.rz(theta[idx], q); idx += 1
        # Entangling layer (linear)
        for q in range(n_qubits - 1):
            qc.cx(q, q + 1)
    return qc, theta

def qaoa_circuit(n_qubits, edges, p=1):
    """QAOA circuit for MaxCut on given edges."""
    gamma = ParameterVector('γ', p)
    beta = ParameterVector('β', p)
    qc = QuantumCircuit(n_qubits)
    
    # Initial state: uniform superposition
    for q in range(n_qubits):
        qc.h(q)
    
    for layer in range(p):
        # Problem unitary
        for (i, j) in edges:
            qc.rzz(2 * gamma[layer], i, j)
        # Mixing unitary
        for q in range(n_qubits):
            qc.rx(2 * beta[layer], q)
    
    return qc, gamma, beta
```

---

## 7. Summary

| Concept | Key Formula | Significance |
|---------|-------------|--------------|
| VQE Principle | $E_0 \leq \langle\psi(\vec\theta)|H|\psi(\vec\theta)\rangle$ | Ground bound |
| Parameter Shift | $\frac{\partial\langle H\rangle}{\partial\theta_i} = \frac{1}{2}[\langle H\rangle_{+s} - \langle H\rangle_{-s}]$ | Exact gradients |
| Barren Plateau | $\text{Var}[\nabla\mathcal{L}] \in O(2^{-n})$ | Trainability curse |
| QAOA | $U = \prod_l e^{-i\beta_l B} e^{-i\gamma_l C}$ | Discretized adiabatic |
| VQC | $f(x;\theta) = \langle 0|S^\dagger(x)U^\dagger(\theta)MU(\theta)S(x)|0\rangle$ | Quantum classifier |

The variational paradigm is the workhorse of NISQ-era quantum computing. Every hybrid algorithm shares this skeleton: a parameterized quantum circuit evaluated on a QPU, optimized by a classical processor, repeated until convergence.

---

## References

1. Kandala, A. et al. "Hardware-efficient variational quantum eigensolver." *Nature* 549, 242–246 (2017).
2. McClean, J. R. et al. "Barren plateaus in quantum neural network training landscapes." *Nature Communications* 9, 4812 (2018).
3. Farhi, E., Goldstone, J. & Gutmann, S. "A Quantum Approximate Optimization Algorithm." arXiv:1411.4028 (2014).
4. Cerezo, M. et al. "Cost function dependent barren plateaus in shallow parametrized quantum circuits." *Nature Communications* 12, 1791 (2021).
5. Schuld, M. et al. "Effect of data encoding on the expressive power of variational quantum machine learning models." *Physical Review A* 103, 032430 (2021).
# Lecture 1: Quantum Foundations — Qubits, Gates, Circuits, and the Bloch Sphere

**AI-5113: Quantum-Classical Hybrid Computing for AI**  
**Instructor:** Prof. Sigrid Lokisdottir  
**Date:** September 3 & 5, 2040

---

## 1. The Qubit: The Seed of Yggdrasil

A classical bit is a coin lying flat — heads or tails, 0 or 1. A qubit is a coin spinning in the air, suspended between all possibilities until the moment of measurement. Like the World Tree Yggdrasil whose roots reach every realm simultaneously, a qubit exists in *superposition*, encoding information in the amplitude-landscape between certainty and uncertainty.

### 1.1 Formal Definition

A qubit is a normalized vector in a two-dimensional complex Hilbert space $\mathcal{H}_2 = \mathbb{C}^2$:

$$|\psi\rangle = \alpha|0\rangle + \beta|1\rangle, \quad |\alpha|^2 + |\beta|^2 = 1$$

where $\{|0\rangle, |1\rangle\}$ is the computational basis, orthonormal under the standard inner product:

$$\langle 0|0\rangle = 1, \quad \langle 1|1\rangle = 1, \quad \langle 0|1\rangle = 0$$

The normalization constraint $|\alpha|^2 + |\beta|^2 = 1$ is the qubit's Well of Urd — the deep spring from which all probability flows. When measured in the computational basis, the outcome is:

- $|0\rangle$ with probability $|\alpha|^2$
- $|1\rangle$ with probability $|\beta|^2$

After measurement, the state *collapses* — the spinning coin lands. The superposition is destroyed and the qubit becomes a classical bit.

### 1.2 Global Phase and the Space of Qubits

The global phase $\alpha \to e^{i\phi}\alpha$ has no observable consequence — two states differing only by a global phase are physically identical. This means the true state space of a single qubit is not $S^3$ (the 3-sphere in $\mathbb{C}^2$) but rather:

$$\text{State space} = S^3 / S^1 \cong S^2$$

This quotient yields the **Bloch sphere**, which we describe in Section 3.

---

## 2. Quantum Gates: Thor's Hammer on the State Space

Quantum gates are *unitary* operators on $\mathcal{H}_2^n$. Just as Thor's hammer Mjölnir reshapes matter with precision strikes, unitary gates reshape quantum states while preserving their total probability.

### 2.1 Single-Qubit Gates

A single-qubit gate is a $2 \times 2$ unitary matrix $U$ satisfying $U^\dagger U = I$.

#### Pauli Gates — The Four Staves of the Elder Futhark

$$X = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \quad Y = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix}, \quad Z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}$$

- **X-gate** (bit flip): $X|0\rangle = |1\rangle$, $X|1\rangle = |0\rangle$ — the quantum NOT.
- **Z-gate** (phase flip): $Z|0\rangle = |0\rangle$, $Z|1\rangle = -|1\rangle$ — introduces a relative phase.
- **Y-gate**: $Y|0\rangle = i|1\rangle$, $Y|1\rangle = -i|0\rangle$ — bit flip + phase flip.

The Pauli matrices satisfy the commutation relations of $\mathfrak{su}(2)$:

$$[X_i, X_j] = 2i\varepsilon_{ijk} X_k, \quad \{X_i, X_j\} = 2\delta_{ij}I$$

#### Hadamard Gate — The Bifröst Between Bases

$$H = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$$

The Hadamard gate is quantum computing's Bifröst — it bridges the computational ($Z$-eigenbasis) and diagonal ($X$-eigenbasis) realms:

$$H|0\rangle = |+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}, \quad H|1\rangle = |-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$$

$$H = \frac{X + Z}{\sqrt{2}}$$

#### Rotation Gates — Tuning the Threads

For any axis $\hat{n} \in \mathbb{R}^3$ and angle $\theta$:

$$R_{\hat{n}}(\theta) = \exp\!\left(-i\frac{\theta}{2}\hat{n}\cdot\vec{\sigma}\right) = \cos\frac{\theta}{2}I - i\sin\frac{\theta}{2}(\hat{n}\cdot\vec{\sigma})$$

where $\vec{\sigma} = (X, Y, Z)$.

The standard rotations:

$$R_x(\theta) = \begin{pmatrix} \cos\frac\theta2 & -i\sin\frac\theta2 \\ -i\sin\frac\theta2 & \cos\frac\theta2 \end{pmatrix}, \quad R_y(\theta) = \begin{pmatrix} \cos\frac\theta2 & -\sin\frac\theta2 \\ \sin\frac\theta2 & \cos\frac\theta2 \end{pmatrix}$$

$$R_z(\theta) = \begin{pmatrix} e^{-i\theta/2} & 0 \\ 0 & e^{i\theta/2} \end{pmatrix}$$

**Euler Decomposition.** Any single-qubit unitary $U$ can be decomposed (up to global phase) as:

$$U = R_z(\alpha)\, R_y(\beta)\, R_z(\gamma)$$

for some $\alpha, \beta, \gamma \in \mathbb{R}$. This is the ZYZ Euler decomposition — three rotations suffice to reach any point on $SU(2)$.

### 2.2 Two-Qubit Gates — Entanglement as the Roots of Yggdrasil

Single-qubit gates create superposition; two-qubit gates create **entanglement** — the deep interweaving of quantum states that mirrors how the roots of Yggdrasil bind the nine realms together.

#### CNOT Gate

$$\text{CNOT} = |0\rangle\langle 0| \otimes I + |1\rangle\langle 1| \otimes X = \begin{pmatrix} 1&0&0&0 \\ 0&1&0&0 \\ 0&0&0&1 \\ 0&0&1&0 \end{pmatrix}$$

CNOT flips the target if the control is $|1\rangle$. Applied to a superposition:

$$\text{CNOT}\left(\frac{|00\rangle + |10\rangle}{\sqrt{2}}\right) = \frac{|00\rangle + |11\rangle}{\sqrt{2}} = |\Phi^+\rangle$$

The Bell state $|\Phi^+\rangle$ cannot be written as $|\psi_A\rangle \otimes |\psi_B\rangle$ — it is **entangled**.

#### Universality

The set $\{H, T, \text{CNOT}\}$ is universal for quantum computation, where:

$$T = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\pi/4} \end{pmatrix}$$

is the $\pi/8$-gate. Any unitary on $n$ qubits can be approximated to precision $\varepsilon$ using $O(4^n \log^c(1/\varepsilon))$ gates from this set (Solovay-Kitaev theorem).

---

## 3. The Bloch Sphere — Mapping the Nine Realms

### 3.1 Bloch Sphere Representation

Any pure single-qubit state can be written (modulo global phase) as:

$$|\psi\rangle = \cos\frac{\theta}{2}|0\rangle + e^{i\phi}\sin\frac{\theta}{2}|1\rangle$$

where $\theta \in [0, \pi]$ and $\phi \in [0, 2\pi)$. This defines a bijection to points on the unit sphere:

$$\vec{r} = (\sin\theta\cos\phi,\ \sin\theta\sin\phi,\ \cos\theta)$$

```
               |z⟩ = |0⟩
                ●
               /|\
              / | \
         θ ↗ /  |  \      θ = polar angle from |0⟩
            /   |   \     φ = azimuthal angle in xy-plane
           /    |    \
          /     |     \
    ─────●──────●──────●───── |y⟩ 
         \     |     /
          \    |    /
           \   |   /
        φ ↘  \  |  /
              \ | /
               \|/
                ●
               |z⟩ = |1⟩
```

The Bloch sphere reveals quantum computation's geometric soul — every single-qubit gate is a rotation of this sphere.

### 3.2 Mixed States and the Bloch Ball

A mixed state $\rho$ is a statistical ensemble of pure states:

$$\rho = \sum_i p_i |\psi_i\rangle\langle\psi_i|, \quad p_i \geq 0, \quad \sum_i p_i = 1$$

For a single qubit, the density matrix can be expanded as:

$$\rho = \frac{1}{2}(I + \vec{r}\cdot\vec{\sigma})$$

where $\vec{r} \in \mathbb{R}^3$ with $\|\vec{r}\| \leq 1$. Pure states satisfy $\|\vec{r}\| = 1$ (the surface); mixed states have $\|\vec{r}\| < 1$ (the interior). The full state space is the **Bloch ball** — the nine realms are but a sphere; the interior holds the fog of Niflheim where certainty dissolves.

### 3.3 Single-Qubit Gates as Rotations

Every single-qubit unitary corresponds to a rotation by angle $\theta$ about axis $\hat{n}$ on the Bloch sphere:

$$U = e^{-i\theta/2} R_{\hat{n}}(\theta)$$

| Gate | Axis $\hat{n}$ | Angle $\theta$ | Action |
|------|---------|-------|--------|
| $X$ | $(1,0,0)$ | $\pi$ | Flip across $xz$-plane |
| $Y$ | $(0,1,0)$ | $\pi$ | Flip across $xz$-plane with phase |
| $Z$ | $(0,0,1)$ | $\pi$ | North-south reflection of $xy$-plane |
| $H$ | $\frac{1}{\sqrt{2}}(1,0,1)$ | $\pi$ | 180° about line in $xz$-plane |
| $T$ | $(0,0,1)$ | $\pi/4$ | Quarter-turn about $z$-axis |
| $R_y(\theta)$ | $(0,1,0)$ | $\theta$ | Rotation about $y$-axis |

---

## 4. Quantum Circuits — Weaving the Tapestry

### 4.1 Circuit Notation

A quantum circuit is a visual tapestry — threads of qubits running left-to-right, with gates as ornamental knots:

```
q0: ─────■─────────
         │
q1: ────⊕───Ry(θ)───

(CNOT with q0 as control, q1 as target, then rotate q1)
```

Reading left-to-right: the CNOT entangles q0 and q1, then $R_y(\theta)$ rotates q1's state.

### 4.2 Example: Bell State Preparation

```
q0: ──H────●──
           │
q1: ────────⊕──
```

Circuit algebra:

$$|\Phi^+\rangle = \text{CNOT}_{01}(H \otimes I)|00\rangle$$

Step by step:

$$|00\rangle \xrightarrow{H\otimes I} \frac{|0\rangle + |1\rangle}{\sqrt{2}}\otimes|0\rangle = \frac{|00\rangle + |10\rangle}{\sqrt{2}} \xrightarrow{\text{CNOT}} \frac{|00\rangle + |11\rangle}{\sqrt{2}}$$

### 4.3 Example: Quantum Fourier Transform on 3 Qubits

The QFT is Yggdrasil's crown — a unitary that maps computational basis states to their frequency components:

$$\text{QFT}_N|j\rangle = \frac{1}{\sqrt{N}}\sum_{k=0}^{N-1} e^{2\pi ijk/N}|k\rangle$$

For $N = 2^3 = 8$:

```
q0: ──H──R₂──R₃──────────────────────●──────────────────
              │    │                   │
q1: ─────────⊕────┼────H──R₂──────────┼────●─────────────
                   │         │          │    │
q2: ──────────────⊕─────────●────H─────┼────┼────●────────
                                         │    │    │
q3: ─────────────────────────────────SWAP─┼────┼────┼───SWAP
```

QFT uses $O(n^2)$ gates vs. $O(n 2^n)$ for the classical FFT — an *exponential* circuit-depth compression that motivates all of quantum ML.

### 4.4 Measurement — The Collapse

Measurement in the computational basis transforms:

$$|\psi\rangle = \sum_i \alpha_i|i\rangle \quad\xrightarrow{\text{measure}}\quad |i\rangle \text{ with prob. } |\alpha_i|^2$$

The average of a Pauli observable on state $\rho$:

$$\langle Z \rangle_\rho = \text{Tr}(\rho Z) = r_z$$

where $r_z$ is the $z$-component of the Bloch vector. This is all a QPU gives us — expectation values, not full wavefunctions.

---

## 5. Multi-Qubit State Spaces and Entanglement

### 5.1 Exponential Hilbert Space

An $n$-qubit system lives in $\mathcal{H} = (\mathbb{C}^2)^{\otimes n} \cong \mathbb{C}^{2^n}$. A general state:

$$|\psi\rangle = \sum_{i=0}^{2^n - 1} \alpha_i|i\rangle$$

requires $2^n$ complex amplitudes — the "curse of dimensionality" that classical simulation cannot escape, and the "blessing of dimensionality" that quantum computers exploit.

### 5.2 Entanglement Measures

For a bipartite state $\rho_{AB}$, the **entanglement entropy** is:

$$S(\rho_A) = -\text{Tr}(\rho_A \log \rho_A)$$

where $\rho_A = \text{Tr}_B(\rho_{AB})$. For a Bell state, $S(\rho_A) = \log 2 = 1$ bit — maximal entanglement.

**Schmidt Decomposition.** Any bipartite pure state $|\psi\rangle_{AB}$ has a decomposition:

$$|\psi\rangle_{AB} = \sum_i \lambda_i |u_i\rangle_A |v_i\rangle_B$$

where $\lambda_i \geq 0$ are the Schmidt coefficients with $\sum_i \lambda_i^2 = 1$.

---

## 6. Qiskit Pseudocode — Summoning the Circuit

```python
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def bell_state_circuit():
    qr = QuantumRegister(2, 'q')
    cr = ClassicalRegister(2, 'c')
    qc = QuantumCircuit(qr, cr)
    
    qc.h(qr[0])         # Hadamard on q0
    qc.cx(qr[0], qr[1]) # CNOT: q0 -> q1
    qc.measure(qr, cr)   # Measure both qubits
    
    return qc

def variational_layer(qc, qubits, params):
    """A single variational layer: RY rotations + CNOT entanglers"""
    for i, q in enumerate(qubits):
        qc.ry(params[i], q)
    for i in range(len(qubits) - 1):
        qc.cx(qubits[i], qubits[i+1])
    return qc
```

---

## 7. Key Results and Theorems

**Theorem (No-Cloning).** There is no unitary $U$ such that for all $|\psi\rangle$, $U|\psi\rangle|0\rangle = |\psi\rangle|\psi\rangle$.

*Proof sketch.* If $U|\psi\rangle|0\rangle = |\psi\rangle|\psi\rangle$ and $U|\phi\rangle|0\rangle = |\phi\rangle|\phi\rangle$, then:
$$\langle\psi|\phi\rangle = \langle\psi|0|U^\dagger U|0|\phi\rangle = \langle\psi|\phi\rangle^2$$
This requires $\langle\psi|\phi\rangle \in \{0, 1\}$ for all pairs — contradiction for non-orthogonal states. $\square$

**Theorem (Solovay-Kitaev).** Let $\mathcal{G}$ be a universal gate set containing gates from $SU(2)$. Then for any $U \in SU(2)$ and precision $\varepsilon > 0$, one can find a sequence of $O(\log^c(1/\varepsilon))$ gates from $\mathcal{G}$ that approximates $U$ to within $\varepsilon$.

This is crucial for hybrid AI: any rotation a classical optimizer wants can be compiled efficiently into hardware-native gates.

---

## 8. From Foundations to Hybrid Quantum-Classical AI

The mathematical structures introduced here — Hilbert spaces, unitary evolution, measurement, entanglement — are the bedrock upon which all quantum-classical hybrid AI is built. In subsequent lectures, we will use these primitives to:

- **Lecture 2:** Train parameterized circuits (VQE, QAOA) where a classical optimizer steers qubits through Hilbert space
- **Lecture 3:** Embed classical data into quantum feature spaces via feature maps
- **Lecture 5:** Build QPU+GPU loops where gradients flow across the classical-quantum boundary

The Bifröst between classical and quantum is built from these stones. Let no one say it cannot be crossed.

---

## References

1. Nielsen, M. A. & Chuang, I. L. *Quantum Computation and Quantum Information*. Cambridge University Press, 2010.
2. Preskill, J. "Quantum Computing in the NISQ Era and Beyond." *Quantum* 2, 79 (2018).
3. Barenco, A. et al. "Elementary Gates for Quantum Computation." *Physical Review A* 52, 3457 (1995).
4. Dawson, C. M. & Nielsen, M. A. "The Solovay-Kitaev Algorithm." *Quantum Information & Computation* 6, 81 (2006).
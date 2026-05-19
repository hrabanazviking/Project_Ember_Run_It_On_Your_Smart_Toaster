# Lecture 6: Error Mitigation — NISQ-Era Error Correction, Shadow Tomography

**AI-5113: Quantum-Classical Hybrid Computing for AI**  
**Instructor:** Prof. Sigrid Lokisdottir  
**Date:** October 8 & 10, 2040

---

## 1. The NISQ Reality — Storms on the Bifröst

The Noisy Intermediate-Scale Quantum (NISQ) era is defined by its limitations: qubits decohere, gates misfire, measurements deceive. Like sailing through a storm in the North Sea, the navigator must account for the fog of uncertainty at every step. Full quantum error correction (QEC) requires thousands of physical qubits per logical qubit — far beyond our 2040 hardware. In the interim, **error mitigation techniques** extract the best possible signal from noisy quantum computations.

**Error correction ≠ Error mitigation:**

| Property | Error Correction | Error Mitigation |
|----------|----------------|-----------------|
| Overhead | $O(\text{polylog}(1/\varepsilon))$ logical qubits | $O(1/\varepsilon^2)$ samples |
| Fault tolerance | Yes — corrects any error up to code distance | No — reduces bias, cannot correct arbitrarily |
| Hardware | Requires logical qubits | Works on physical qubits |
| Goal | Reliable computation | Approximate results from noisy data |

---

## 2. Noise Models

### 2.1 Quantum Channels

A quantum operation on density matrix $\rho$ is described by a **completely positive trace-preserving (CPTP) map**:

$$\mathcal{E}(\rho) = \sum_k E_k \rho E_k^\dagger$$

where $\{E_k\}$ are Kraus operators satisfying $\sum_k E_k^\dagger E_k = I$.

### 2.2 Common Noise Channels

**Depolarizing channel** — uniform noise:

$$\mathcal{E}_{\text{dep}}(\rho) = (1 - p)\rho + \frac{p}{3}(X\rho X + Y\rho Y + Z\rho Z)$$

Equivalently: with probability $1-p$, the state is unchanged; with probability $p/3$, each Pauli error occurs.

**Amplitude damping** — $T_1$ relaxation:

$$E_0 = |0\rangle\langle 0| + \sqrt{1-\gamma}|1\rangle\langle 1|, \quad E_1 = \sqrt{\gamma}|0\rangle\langle 1|$$

Models energy decay from $|1\rangle$ to $|0\rangle$ at rate $\gamma$.

**Phase damping** — $T_2$ dephasing:

$$E_0 = \sqrt{1-\lambda/2}\,I, \quad E_1 = \sqrt{\lambda/2}\,Z$$

Destroys phase coherence without energy exchange.

**Readout (measurement) error** — classical bit flip:

$$\Pr(\text{measure } j | \text{true state } i) = M_{ij}$$

where $M$ is the $2^n \times 2^n$ confusion matrix. For single-qubit readout:

$$M = \begin{pmatrix} 1-p_{0|1} & p_{1|0} \\ p_{0|1} & 1-p_{1|0} \end{pmatrix}$$

with $p_{j|i}$ the probability of reading $j$ when the true state was $i$.

### 2.3 Noise Scaling Laws

For a circuit of depth $d$ on $n$ qubits with single-qubit gate error rate $\epsilon_1$, two-qubit gate error rate $\epsilon_2$, and $N_2$ two-qubit gates:

$$\text{Total error} \approx \epsilon_1 \cdot d \cdot n + \epsilon_2 \cdot N_2$$

For current NISQ devices: $\epsilon_1 \sim 10^{-4}$, $\epsilon_2 \sim 10^{-3}$–$10^{-2}$, giving meaningful computation up to $d \sim 100$ for $n \sim 50$ qubits.

---

## 3. Error Mitigation Techniques

### 3.1 Zero-Noise Extrapolation (ZNE)

**Core idea:** Deliberately increase noise, then extrapolate to zero noise.

If the noise level is scaled by factor $\lambda$ (e.g., by gate folding), the expectation value becomes:

$$\langle O\rangle_{\lambda} = f(\lambda)$$

where $f$ is an unknown function. ZNE estimates:

$$\langle O\rangle_0 \approx \text{extrapolate}\left\{\langle O\rangle_{\lambda_1}, \langle O\rangle_{\lambda_2}, \ldots, \langle O\rangle_{\lambda_k}\right\}$$

**Gate folding** to increase noise by factor $\lambda$:

$$U \to U \cdot U^\dagger \cdot U = U$$

This triples the circuit depth (and noise) while leaving the logical unitary unchanged.

**Extrapolation methods:**

| Method | Formula | Order | Assumption |
|--------|---------|-------|------------|
| Linear | $f(\lambda) = a + b\lambda$ | 1st | Weak noise |
| Quadratic | $f(\lambda) = a + b\lambda + c\lambda^2$ | 2nd | Moderate noise |
| Exponential | $f(\lambda) = a + b e^{c\lambda}$ | 2nd | Depolarizing |
| Richardson | $\sum_i (-1)^{i+1}\binom{k}{i}\langle O\rangle_{i}$ | $k$-th | General |

**Richardson extrapolation** for noise factors $\lambda_1, \lambda_2, \ldots, \lambda_k$:

$$\hat{O}_0 = \sum_{i=1}^{k} \gamma_i \langle O \rangle_{\lambda_i}$$

where the coefficients $\gamma_i$ satisfy $\sum_i \gamma_i = 1$ (unbiased in zero-noise limit) and $\sum_i \gamma_i \lambda_i^j = 0$ for $j = 1, \ldots, k-1$ (canceling noise polynomial terms).

**Theorem (Kandala et al., 2019).** ZNE with Richardson extrapolation reduces the systematic bias from depolarizing noise by a factor of $O(\lambda^{k+1})$ for $k$ noise-scaling points, at the cost of $O(k)$ additional circuit evaluations.

### 3.2 Probabilistic Error Cancellation (PEC)

**Core idea:** Decompose the noisy channel into a quasiprobability distribution over noise-free operations, then sample and reweight.

Given a noisy channel $\mathcal{E} = \sum_i \eta_i \mathcal{F}_i$ where $\mathcal{F}_i$ are ideal operations and $\eta_i$ are quasiprobabilities (which may be negative):

$$\langle O \rangle_{\text{ideal}} = \sum_i \eta_i \langle O \rangle_{\mathcal{F}_i}$$

Cancel the noise by sampling $\mathcal{F}_i$ with probability $|\eta_i|/\gamma$ and weighting by $\text{sign}(\eta_i) \gamma$, where $\gamma = \sum_i |\eta_i|$.

**Theorem (Temme et al., 2017).** PEC produces an unbiased estimate of $\langle O\rangle_{\text{ideal}}$ with variance:

$$\text{Var}[\hat{O}_{\text{PEC}}] = O(\gamma^{2m} / S)$$

where $m$ is the number of noisy gates and $S$ is the number of shots. The factor $\gamma^{2m}$ grows exponentially with circuit depth — PEC is practical only for shallow circuits.

### 3.3 Measurement Error Mitigation

**Readout error mitigation** constructs the confusion matrix $M$ and inverts it:

$$\vec{p}_{\text{corrected}} = M^{-1} \vec{p}_{\text{measured}}$$

For $n$ qubits, $M$ is $2^n \times 2^n$, but under the **tensor product assumption** (errors on different qubits are independent):

$$M = \bigotimes_{i=1}^{n} M_i$$

where each $M_i$ is a $2\times 2$ single-qubit confusion matrix. Inversion costs $O(2^n)$ — still exponential, but dramatically better than $O(4^n)$ for the full matrix.

**Continuous readout correction** using M3 (Maciejewski et al., 2021): reduces the $2^n$-dimensional problem to an $O(n)$ sparse system via iterative methods.

### 3.4 Dynamical Decoupling

Insert identity-equivalent gate sequences to suppress decoherence:

- **Spin echo:** Insert $X$ at circuit midpoint to cancel static dephasing
- **XY4 sequence:** $X Y X Y$ — cancels both $T_1$ and $T_2$ effects
- **CPMG:** Repeated $X$ pulses — robust against low-frequency noise

```
Without DD:  ───Gate₁───Wait───Gate₂───    (dephasing accumulates)

With DD:     ───Gate₁──X──Wait──X──Gate₂──   (echo cancels dephasing)
```

---

## 4. Classical Shadow Tomography

### 4.1 The Shadow Protocol

Classical shadow tomography (Huang et al., 2020) extracts structural information from quantum states using *fewer* measurements than full state tomography. Like Heimdall scanning the nine realms from his watchtower, shadow tomography glimpses the essential structure without needing to see everything.

**Protocol:**

1. **Random measurement basis:** Apply a random unitary $U \sim \mathcal{U}$ from a measured ensemble $\mathcal{U}$
2. **Computational basis measurement:** Measure in the computational basis, obtaining outcome $\hat{b} \in \{0,1\}^n$
3. **Classical post-processing:** Compute the classical shadow:

$$\hat{\rho} = \mathcal{M}^{-1}(U^\dagger|\hat{b}\rangle\langle\hat{b}|U)$$

where $\mathcal{M}^{-1}$ is the inverse of the measurement channel $\mathcal{M}(\rho) = \mathbb{E}_{U\sim\mathcal{U}}[\sum_b \langle b|U\rho U^\dagger|b\rangle \cdot U^\dagger|b\rangle\langle b|U]$.

**For random Pauli measurements** ($\mathcal{U} = \text{Clifford}(1)^{\otimes n}$, i.e., random single-qubit Pauli rotations):

$$\mathcal{M}^{-1}(\omega) = \bigotimes_{i=1}^{n}\left(3\omega_i - I\right)$$

where $\omega_i$ is the reduced density matrix of qubit $i$.

A single shadow snapshot is:

$$\hat{\rho} = \bigotimes_{i=1}^{n}\left(3|\hat{b}_i\rangle\langle\hat{b}_i| - I\right)$$

where $\hat{b}_i$ is the measurement outcome for qubit $i$ in the randomly chosen Pauli basis.

### 4.2 Sample Complexity

**Theorem (Huang et al., 2020).** To estimate $M$ observables $\{O_1, \ldots, O_M\}$ with error $\varepsilon$ and failure probability $\delta$, the number of shadow samples needed is:

$$N = O\left(\frac{\max_i \|O_i\|^2_{\text{shadow}}}{\varepsilon^2} \log\frac{M}{\delta}\right)$$

where $\|O\|^2_{\text{shadow}} = \text{Tr}(O \mathcal{M}^{-1}(O))$ is the **shadow norm**.

For Pauli observables with random Pauli measurements: $\|P\|^2_{\text{shadow}} = 3^n$.

For local observables $O$ acting on $k$ qubits: $\|O\|^2_{\text{shadow}} \leq 3^k \text{Tr}(O^2)$.

**Key result:** Estimating $M$ local observables (each on $k$ qubits) requires:

$$N = O\left(\frac{3^k}{\varepsilon^2}\log\frac{M}{\delta}\right)$$

This is **exponentially better** than full tomography ($O(4^n)$) and better than tomography even for global observables when $k \ll n$.

### 4.3 Application: Noise-Aware Kernel Estimation

For hybrid ML, we need to estimate $\text{Tr}(O_i \rho)$ for many observables $O_i$ (e.g., Pauli terms in a Hamiltonian or kernel matrix elements). Shadow tomography provides:

$$\hat{\text{Tr}}(O \rho) = \frac{1}{N}\sum_{j=1}^{N} \text{Tr}(O \hat{\rho}^{(j)})$$

This requires only $O(3^k \log(M)/\varepsilon^2)$ samples vs. $O(2^n)$ for direct measurement.

**Application to quantum kernels:**

To compute $\kappa(\mathbf{x}, \mathbf{x}') = |\langle\mathbf{x}|\mathbf{x}'\rangle|^2 = \text{Tr}(|\mathbf{x}\rangle\langle\mathbf{x}| \cdot |\mathbf{x}'\rangle\langle\mathbf{x}'|)$:

$$\hat{\kappa}(\mathbf{x}, \mathbf{x}') = \frac{1}{N}\sum_{j=1}^{N} \text{Tr}(|\mathbf{x}'\rangle\langle\mathbf{x}'| \hat{\rho}^{(j)}_{\mathbf{x}})$$

For $m$ training points, the full kernel matrix requires $O(m^2)$ kernel evaluations. Shadow tomography reduces each evaluation from $O(2^n)$ measurements to $O(3^k/\varepsilon^2)$ shadows.

---

## 5. Robust Variational Algorithms

### 5.1 Error-Aware Cost Functions

Define a noise-resilient cost function by subtracting a noise estimate:

$$\mathcal{L}_{\text{mitigated}}(\vec\theta) = \mathcal{L}_{\text{noisy}}(\vec\theta) - \hat{\epsilon}_{\text{bias}}(\vec\theta)$$

where $\hat{\epsilon}_{\text{bias}}$ is estimated via ZNE or PEC.

### 5.2 Resilient VQE

**Theorem (Kandala et al., 2019).** For VQE on a Hamiltonian $H = \sum_i h_i P_i$ with depolarizing noise rate $p$, zero-noise extrapolation with linear fitting reduces the energy error from $O(p)$ to $O(p^2)$.

The key life lesson: mitigation is not correction. Error-mitigated VQE produces a corrected estimate, but the variance of that estimate is *larger* than the raw measurement. The tradeoff:

$$\text{MSE} = \underbrace{\epsilon_{\text{bias}}^2}_{\downarrow \text{ with mitigation}} + \underbrace{\sigma_{\text{variance}}^2}_{\uparrow \text{ with mitigation}}$$

Optimal mitigation balances bias and variance.

### 5.3 Virtual Distillation

**Core idea:** Use multiple copies of the noisy state to suppress errors.

Given $k$ noisy copies $\rho^{\otimes k}$, the $k$-th virtual state is:

$$\tilde{\rho}_{(k)} = \frac{\text{Tr}_2[\Pi^{+} \rho^{\otimes 2}]}{\text{Tr}[\Pi^{+} \rho^{\otimes 2}]}$$

where $\Pi^{+}$ is the permutation operator projecting onto the symmetric subspace.

**Theorem (Huggins et al., 2021).** Virtual distillation with $k$ copies reduces error rates as:

$$\|\tilde{\rho}_{(k)} - |\psi\rangle\langle\psi|\|_1 \leq O(\epsilon^k)$$

where $\epsilon$ is the single-copy infidelity $\epsilon = 1 - \langle\psi|\rho|\psi\rangle$.

**Cost:** Requires $k$ simultaneous copies — i.e., $kn$ qubits. For $k=2$: double the qubit budget to quartically suppress error.

---

## 6. Error Mitigation in Hybrid ML Pipelines

### 6.1 Integrated Mitigation Stack

A production hybrid ML system should layer mitigations:

```
┌──────────────────────────────────────────────┐
│ Layer 4: Post-hoc Correction                │
│   • Virtual distillation                    │
│   • ZNE extrapolation                       │
│   • PEC quasiprobability correction         │
├──────────────────────────────────────────────┤
│ Layer 3: Measurement Mitigation             │
│   • M3 readout correction                   │
│   • Mitigated readout confusion matrix      │
├──────────────────────────────────────────────┤
│ Layer 2: Circuit-Level Mitigation           │
│   • Dynamical decoupling                    │
│   • Gate scheduling to minimize idle time    │
│   • Optimal qubit selection for connectivity │
├──────────────────────────────────────────────┤
│ Layer 1: Algorithm-Level Resilience          │
│   • Error-aware cost functions              │
│   • Robust optimizers (SPSA, opt-COBYLA)    │
│   • Shadow tomography for efficient observables│
└──────────────────────────────────────────────┘
```

### 6.2 Mitigation Cost vs. Accuracy Tradeoff

| Technique | Bias Reduction | Variance Increase | Overhead |
|-----------|---------------|-------------------|----------|
| ZNE (linear) | $O(p)$ | $2\times$ | $2-3\times$ circuits |
| ZNE (Richardson $k$) | $O(p^k)$ | $\sim k^2\times$ | $k\times$ circuits |
| PEC | Exact (unbiased) | $O(\gamma^{2m}/S)$ | $O(\gamma^m)$ samples |
| Readout mitigation | $O(p_{\text{read}})$ | $O(1)$ | $O(2^n)$ calibration |
| Shadow tomography | $O(1/\sqrt{N})$ | $O(1)$ | $O(N \cdot 3^k)$ |
| Virtual distillation ($k=2$) | $O(\epsilon^2)$ | $O(1/\epsilon^2)$ | $2n$ qubits |

---

## 7. Qiskit Implementation

```python
from qiskit import QuantumCircuit
from qiskit.primitives import Estimator
from qiskit.result import marginal_counts
import numpy as np

def zero_noise_extrapolation(circuit, observable, estimator, 
                            noise_factors=[1, 3, 5]):
    """ZNE via gate folding with Richardson extrapolation."""
    results = []
    for lam in noise_factors:
        # Fold the circuit to increase noise
        folded = fold_gates(circuit, lam)
        job = estimator.run([folded], [observable], shots=8192)
        results.append(job.result().values[0])
    
    # Richardson extrapolation to zero noise
    # For noise_factors = [1, 3, 5]:
    # O(0) ≈ (15*O(1) - O(3)*6 + O(5)) / 10
    coeffs = richardson_coefficients(noise_factors)
    return sum(c * r for c, r in zip(coeffs, results))

def fold_gates(circuit, factor):
    """Apply gate folding to scale noise by factor."""
    if factor == 1:
        return circuit
    folded = circuit.copy()
    # Fold each gate (factor-1) times
    n_folds = int((factor - 1) / 2)
    for _ in range(n_folds):
        for inst, qargs, cargs in circuit.data:
            folded.append(inst, qargs, cargs)  # Gate
            folded.append(inst.inverse(), qargs, cargs)  # Gate†
            folded.append(inst, qargs, cargs)  # Gate
    return folded

def classical_shadow(state_circuit, n_qubits, n_shadows):
    """Generate classical shadow snapshots."""
    shadows = []
    for _ in range(n_shadows):
        # Random Pauli basis for each qubit
        bases = np.random.choice(['X', 'Y', 'Z'], size=n_qubits)
        
        # Rotate into measurement basis
        shadow_circuit = state_circuit.copy()
        for q, basis in enumerate(bases):
            if basis == 'X':
                shadow_circuit.h(q)
            elif basis == 'Y':
                shadow_circuit.s(q)
                shadow_circuit.h(q)
            # Z needs no rotation
        
        # Measure
        shadow_circuit.measure_all()
        
        # In post-processing: apply inverse channel M^{-1}
        # rho_hat = product_i (3|b_i><b_i| - I) for outcome b_i
        shadows.append((bases, outcome))
    
    return shadows
```

---

## 8. Summary

Error mitigation is essential for extracting useful results from NISQ hardware. The key tools are:

- **ZNE:** Extrapolate to zero noise from scaled-noise measurements
- **PEC:** Quasiprobabilistic error cancellation — unbiased but costly
- **Readout mitigation:** Correct measurement errors via confusion matrices
- **Shadow tomography:** Efficient estimation of many observables from few measurements
- **Virtual distillation:** Suppress errors using multiple state copies

The Norse lesson: we do not wait for the perfect stormless day to sail. We build better ships, navigate by the stars through the fog, and correct our course. Error mitigation is the art of sailing through NISQ weather.

---

## References

1. Temme, K. et al. "Error mitigation for short-depth quantum circuits." *Physical Review Letters* 119, 180509 (2017).
2. Kandala, A. et al. "Error mitigation extends the computational reach of a noisy quantum processor." *Nature* 567, 491–495 (2019).
3. Huang, H.-Y. et al. "Predicting many properties of a quantum system from very few measurements." *Nature Physics* 16, 1050–1057 (2020).
4. Endo, S. et al. "Practical quantum error mitigation for near-future applications." *Physical Review X* 8, 031027 (2018).
5. Huggins, W. et al. "Virtual distillation for quantum error mitigation." *Physical Review X* 11, 041036 (2021).
6. Maciejewski, F. B. et al. "Mitigation of readout noise in near-term quantum devices." *Quantum* 5, 497 (2021).
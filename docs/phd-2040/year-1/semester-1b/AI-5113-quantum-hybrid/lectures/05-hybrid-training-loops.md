# Lecture 5: Hybrid Training Loops — QPU+GPU Training Pipelines

**AI-5113: Quantum-Classical Hybrid Computing for AI**  
**Instructor:** Prof. Sigrid Lokisdottir  
**Date:** October 1 & 3, 2040

---

## 1. The Hybrid Paradigm — Two Realms, One Training Loop

A hybrid quantum-classical training loop is an interwoven computation — like the fibers of Gleipnir, the binding that holds Fenrir: each strand alone is weak, but together they are unbreakable. The QPU evaluates quantum circuits; the GPU computes classical gradients and updates parameters; the two communicate through a channel that is, for now, painfully narrow.

The fundamental architecture:

```
┌────────────────────────────────────────────────────────────────┐
│                    HYBRID TRAINING LOOP                        │
│                                                                │
│  ┌─────────────┐         ┌──────────┐        ┌────────────┐  │
│  │ GPU Cluster  │ ──θ───► │  QPU     │ ──E(θ)─►│ GPU Cluster│  │
│  │ (Optimizer)  │         │ (Circuit)│        │ (Loss Eval)│  │
│  └──────┬───────┘         └──────────┘        └──────┬─────┘  │
│         │                                           │        │
│         │◄────────── ∇L(θ) ◄───────────────────────┘        │
│         │              (classical gradient)                   │
│         │                                                     │
│         ▼                                                     │
│  θ ← θ - η∇L(θ)    (parameter update)                     │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. Gradient Flow Across the Classical-Quantum Boundary

### 2.1 The Parameter-Shift Rule

For a loss function $\mathcal{L}(\vec\theta)$ evaluated on a QPU as:

$$\mathcal{L}(\vec\theta) = \langle\psi(\vec\theta)|O|\psi(\vec\theta)\rangle = \sum_i h_i \langle P_i\rangle_{\vec\theta}$$

The parameter-shift rule provides *exact* gradients:

$$\frac{\partial \mathcal{L}}{\partial \theta_k} = \frac{1}{2}\left[\mathcal{L}(\vec\theta + \frac{\pi}{2}\vec{e}_k) - \mathcal{L}(\vec\theta - \frac{\pi}{2}\vec{e}_k)\right]$$

where $\vec{e}_k$ is the unit vector in parameter space.

**Cost per gradient:** $2|\vec\theta|$ circuit evaluations (forward-pass only, quantum circuits have no backward pass).

**Generalized shift:** For gates with generator $G$ having eigenvalues $\{r_j\}$:

$$\frac{\partial \mathcal{L}}{\partial \theta_k} = \sum_{j<j'} \frac{f(r_j, r_{j'})}{\tan((r_j - r_{j'})\theta_k/2)} \cdot \left[\mathcal{L}(\vec\theta + \vec{s}_{jk}) - \mathcal{L}(\vec\theta - \vec{s}_{jk})\right]$$

For Pauli generators with eigenvalues $\pm 1/2$, this reduces to the standard two-term shift.

### 2.2 Stochastic Parameter Shift

When the number of parameters is large, computing all $2|\vec\theta|$ shifted circuits is expensive. **Stochastic parameter shift** samples a random subset:

$$\nabla \mathcal{L} \approx \frac{|\vec\theta|}{B}\sum_{k \in \mathcal{B}} \frac{\partial \mathcal{L}}{\partial \theta_k} \vec{e}_k$$

where $\mathcal{B}$ is a mini-batch of $B$ parameters. This is the quantum analog of stochastic gradient descent.

### 2.3 Gradient via Finite Differences (Avoid!)

$$\frac{\partial \mathcal{L}}{\partial \theta_k} \approx \frac{\mathcal{L}(\theta_k + \epsilon) - \mathcal{L}(\theta_k - \epsilon)}{2\epsilon}$$

**Problems:**
- Requires choosing $\epsilon$ — too small and shot noise dominates, too large and bias dominates
- Error $O(\epsilon^2)$ + shot noise $O(1/\sqrt{S})$ where $S$ is shots per circuit
- Total error: $O(\epsilon^2 + \epsilon^{-1}/\sqrt{S})$

**Always prefer parameter-shift over finite differences** for QPU-based gradients.

### 2.4 SPSA — Simultaneous Perturbation Stochastic Approximation

SPSA approximates the gradient using only *two* circuit evaluations regardless of parameter count:

$$\nabla\mathcal{L}(\vec\theta_t) \approx \frac{\mathcal{L}(\vec\theta_t + c_t\vec\Delta_t) - \mathcal{L}(\vec\theta_t - c_t\vec\Delta_t)}{2c_t}\vec\Delta_t$$

where $\vec\Delta_t \in \{-1, +1\}^{|\vec\theta|}$ are random ±1 perturbations and $c_t$ is a decay schedule.

**Theorem (Spall, 1992).** SPSA converges almost surely to a local minimum under standard Robbins-Monro conditions, with the same asymptotic rate as gradient descent but using only 2 circuit evaluations per step instead of $2|\vec\theta|$.

---

## 3. The Hybrid Architecture — Detailed Pipeline

### 3.1 Data Flow

```
                    CLASSICAL (GPU)
                    ┌─────────────────────────────┐
                    │ 1. Sample mini-batch {x_i}    │
                    │ 2. Encode → feature map S(x_i) │
                    │ 3. Dispatch circuits to QPU    │
                    └──────────┬──────────────────┘
                               │
                    ╔══════════╧══════════╗
                    ║   QPU SCHEDULE      ║
                    ║  Circuit queue       ║
                    ║  Shot accumulation   ║
                    ╚══════════╤══════════╝
                               │
                    ┌──────────▼──────────────────┐
                    │ 4. Collect measurement results│
                    │ 5. Compute loss & gradients   │
                    │ 6. Update parameters θ       │
                    └─────────────────────────────┘
```

### 3.2 Shot Noise and Statistical Overhead

Each QPU measurement is a Bernoulli trial with $S$ shots. The variance of the estimated expectation value is:

$$\text{Var}[\hat{\langle O\rangle}] = \frac{\text{Var}(O)}{S} \leq \frac{\|O\|^2}{S}$$

For $K$ terms in the Pauli decomposition, the total number of circuit evaluations per gradient step is:

$$N_{\text{evals}} = 2K \cdot |\vec\theta| \cdot S_{\text{min}}$$

where $S_{\text{min}}$ is the minimum shots per term. The statistical overhead can be $10^2$–$10^4\times$ classical compute time.

### 3.3 Shot Allocation Strategies

| Strategy | Allocation Rule | Advantage |
|----------|----------------|-----------|
| Uniform | $S_k = S/|K|$ | Simple |
| Proportional | $S_k \propto |h_k|$ | Focus on large coefficients |
| Adaptive | $S_k \propto \text{Var}(P_k)/\epsilon_k^2$ | Optimal for target precision |
| Bayesian | Update beliefs per shot | Information-efficient |

**Theorem (Kubler et al., 2020).** Adaptive shot allocation achieves the same gradient variance as uniform allocation using $O(\log K)$ fewer total shots.

---

## 4. QPU Scheduling and Resource Management

### 4.1 Circuit Compilation

Classical parameters $\vec\theta$ must be compiled into native gate sets. For IBM Eagle v3 (127 qubits):

$$U(\vec\theta) \xrightarrow{\text{compile}} \text{CX} + R_Z + \sqrt{X} + \text{ECR}$$

Compilation involves:
1. **Transpilation:** Map logical circuit to hardware topology
2. **Routing:** Insert SWAPs for non-adjacent CNOTs
3. **Optimization:** Gate cancellation, commutative folding

**Overhead:** Compilation adds $O(1)$–$O(n^2)$ SWAP gates depending on topology.

### 4.2 Hybrid Scheduling — Pipelining

The key to efficient hybrid training is **pipelining** — overlapping QPU computation with GPU computation:

```
Time ──────────────────────────────────────────────►

GPU:   [batch₁]    [batch₂]    [batch₃]    [grad₁]  [grad₂]  [grad₃]
       encode      encode      encode      update    update   ...
          │           │           │
QPU:         [circ₁]────[circ₂]────[circ₃]──►
              meas        meas        meas
```

Without pipelining: $T_{\text{total}} = T_{\text{GPU\_encode}} + T_{\text{QPU\_run}} + T_{\text{GPU\_update}}$ per step.

With pipelining: $T_{\text{total}} = \max(T_{\text{GPU}}, T_{\text{QPU}})$ per step — the bottleneck determines throughput.

### 4.3 Asynchronous QPU Training

For clouds-accessed QPUs with long queue times, use **asynchronous parameter updates**:

$$\vec\theta_{t+1} = \vec\theta_t - \eta \nabla\mathcal{L}(\vec\theta_{t-\tau})$$

where $\tau$ is the QPU latency in steps. This is the quantum analog of asynchronous SGD:

**Theorem (based on SGD analysis).** For $\tau$ bounded and learning rate $\eta = O(1/\sqrt{T})$, asynchronous hybrid training converges with the same rate as synchronous training, up to constant factors depending on $\tau$.

---

## 5. Hybrid Neural Architectures

### 5.1 Quantum Layers in Neural Networks

A **quantum neural network layer** embeds a PQC within a classical network:

$$\mathbf{h}^{(l+1)} = \sigma\!\left(W^{(l)} \cdot \text{QPU}(\mathbf{h}^{(l)}; \vec\theta^{(l)}) + \mathbf{b}^{(l)}\right)$$

where:
- $\mathbf{h}^{(l)} \in \mathbb{R}^{d_l}$ is the $l$-th layer hidden state
- $\text{QPU}(\cdot; \vec\theta^{(l)})$ is a variational quantum circuit parameterized by $\vec\theta^{(l)}$
- $W^{(l)} \in \mathbb{R}^{d_{l+1} \times 2^n}$ maps QPU output to next layer
- $\sigma$ is a classical activation function

### 5.2 Gradient Flow Through the Hybrid Stack

The total loss gradient with respect to classical parameters $W$ and quantum parameters $\theta$ decomposes as:

$$\frac{\partial \mathcal{L}}{\partial W^{(l)}} = \frac{\partial \mathcal{L}}{\partial \mathbf{h}^{(l+1)}} \cdot \text{QPU}(\mathbf{h}^{(l)}; \vec\theta^{(l)})^\top$$

$$\frac{\partial \mathcal{L}}{\partial \vec\theta^{(l)}} = \frac{\partial \mathcal{L}}{\partial \mathbf{h}^{(l+1)}} \cdot \frac{\partial \text{QPU}}{\partial \vec\theta^{(l)}} \cdot W^{(l)}$$

The QPU gradient $\frac{\partial \text{QPU}}{\partial \vec\theta^{(l)}}$ is computed via parameter-shift on the QPU; the rest is standard backpropagation on the GPU.

### 5.3 Example: Hybrid Quantum-Classical ResNet Block

```
┌──────────────────────────────────────────────────┐
│            Hybrid ResNet Block                    │
│                                                   │
│  h_in ──►[BatchNorm]─►[ReLU]─►┬──►[QPU Layer]──►│
│                                │   (param-shift)  │
│                                │        │         │
│                                │   ┌────▼────┐    │
│                                │   │ Meas.    │    │
│                                │   │ +Linear │    │
│                                │   └────┬────┘    │
│                                │        │         │
│                                │   ┌────▼────┐    │
│                                │   │ ReLU    │    │
│                                │   └────┬────┘    │
│                                │        │         │
│                                │   ┌────▼────┐    │
│                                └───►│  + h_in  │───┼──► h_out
│                                     └─────────┘    │
└──────────────────────────────────────────────────┘
```

The skip connection ensures that even if the QPU layer is noisy or poorly trained, the block degrades gracefully to a classical ResNet block — like a Bifröst that falls back to a reliable fjord crossing.

---

## 6. Practical Considerations

### 6.1 Latency Budget Analysis

For a typical hybrid training step on 127-qubit IBM Eagle v3:

| Component | Latency |
|-----------|---------|
| Data encoding (GPU) | ~0.1 ms |
| Circuit compilation | ~10–100 ms |
| QPU queue wait | ~1–60 s |
| QPU execution (1 shot) | ~1 μs |
| Measurement readout | ~1 ms |
| Total for $10^4$ shots | ~0.01–1 s |
| GPU gradient compute | ~0.5 ms |
| Parameter update | ~0.01 ms |
| **Total per step** | **~1–60 s** |

The QPU queue wait dominates. **Mitigation:**
1. Batch parameter shifts into parallel circuits
2. Use multiple QPU backends simultaneously
3. Pre-compile circuit templates with parameter binding
4. Employ asynchronous updates

### 6.2 Noise-Aware Training

Real QPUs have gate errors, decoherence, and readout errors. The measured loss is:

$$\hat{\mathcal{L}}(\vec\theta) = \mathcal{L}(\vec\theta) + \epsilon_{\text{shot}} + \epsilon_{\text{noise}}$$

Noise-aware training strategies:
- **Robust optimizer design:** SPSA is inherently noise-robust
- **Error mitigation postprocessing:** (Lecture 6)
- **Noise-adaptive learning rates:** $\eta_t = \min(\eta, \sigma_{\text{noise}}^{-1})$
- **Ensemble averaging:** Run each circuit $K$ times, average

### 6.3 Quantization of QPU Results

The QPU output is inherently stochastic — measurement results are Bernoulli random variables. The classical optimizer must handle this:

$$\hat{g}_k = \frac{\hat{\mathcal{L}}(\vec\theta + s\vec{e}_k) - \hat{\mathcal{L}}(\vec\theta - s\vec{e}_k)}{2s} + \xi_k$$

where $\xi_k$ is shot noise. The signal-to-noise ratio at each step is:

$$\text{SNR} = \frac{|\nabla\mathcal{L}|}{\sigma_{\text{shot}}} = \frac{|\nabla\mathcal{L}|\sqrt{S}}{\sigma_O}$$

For barren plateaus ($|\nabla\mathcal{L}| \sim 2^{-n}$), achieving $\text{SNR} \geq 1$ requires $S \sim \sigma_O^2 \cdot 4^n$ shots — exponentially many.

---

## 7. Qiskit + PyTorch Hybrid Training

```python
import torch
import torch.nn as nn
from qiskit import QuantumCircuit
from qiskit.primitives import Estimator

class HybridQuantumLayer(nn.Module):
    """Quantum layer embedded in a PyTorch neural network."""
    
    def __init__(self, n_qubits, n_layers, estimator):
        super().__init__()
        self.n_qubits = n_qubits
        self.n_layers = n_layers
        self.estimator = estimator
        
        # Trainable quantum parameters
        self.theta = nn.Parameter(torch.randn(2 * n_qubits * n_layers) * 0.1)
        
        # Observable for output (Z on first two qubits for binary output)
        self.observable = SparsePauliOp.from_list([
            ("Z" + "I" * (n_qubits - 1), 1.0),
            ("IZ" + "I" * (n_qubits - 2), 1.0) if n_qubits > 1 else 
        ])
    
    def build_circuit(self, x, theta):
        """Construct parameterized circuit with data encoding."""
        qc = QuantumCircuit(self.n_qubits)
        idx = 0
        for layer in range(self.n_layers):
            # Data encoding (angle encoding)
            for q in range(self.n_qubits):
                if q < len(x):
                    qc.ry(x[q], q)
            # Variational layer
            for q in range(self.n_qubits):
                qc.ry(theta[idx], q); idx += 1
                qc.rz(theta[idx], q); idx += 1
            # Entangling
            for q in range(self.n_qubits - 1):
                qc.cx(q, q + 1)
        return qc
    
    def forward(self, x):
        batch_size = x.shape[0]
        outputs = []
        for i in range(batch_size):
            qc = self.build_circuit(x[i].detach().numpy(), 
                                     self.theta.detach().numpy())
            job = self.estimator.run([qc], [self.observable], shots=1024)
            result = job.result().values[0]
            outputs.append(torch.tensor(result))
        return torch.stack(outputs)
```

---

## 8. Summary

The hybrid training loop interleaves QPU and GPU computation through a narrow communication channel. Its efficiency depends on:

1. **Gradient computation:** Parameter-shift provides exact gradients at $2|\vec\theta|$ cost; SPSA provides cheap approximate gradients at 2 cost.
2. **Statistical overhead:** Shot noise scales as $O(1/\sqrt{S})$; adaptive allocation reduces waste.
3. **Latency management:** QPU queue times dominate; pipelining and asynchronous updates are essential.
4. **Noise resilience:** The classical optimizer must handle stochastic gradients from noisy QPUs.

The art of hybrid training is the art of the Bifröst — engineering a stable bridge across two radically different computational realms.

---

## References

1. Mitarai, M. et al. "Quantum circuit learning." *Physical Review A* 98, 032309 (2018).
2. Spall, J. C. "Multivariate stochastic approximation using a simultaneous perturbation gradient approximation." *IEEE Trans. Auto. Control* 37, 332–341 (1992).
3. Schuld, M. et al. "Evaluating analytic gradients on quantum hardware." *Physical Review A* 99, 032331 (2019).
4. Kubler, J. M. et al. "Adaptive shot allocation for fast variational quantum eigensolver optimization." *Quantum* 5, 516 (2021).
5. Lavrik et al. "A quantum-enhanced gradient descent algorithm for machine learning." *Quantum* 6, 795 (2022).
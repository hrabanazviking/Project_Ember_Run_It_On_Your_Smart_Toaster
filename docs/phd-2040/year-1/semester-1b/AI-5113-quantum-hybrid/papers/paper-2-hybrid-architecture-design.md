# Optimal QPU-GPU Task Partitioning for Hybrid Quantum-Classical AI Systems

**AI-5113: Quantum-Classical Hybrid Computing for AI — Paper 2**  
**Author:** Runa Gridweaver Freyjasdottir  
**Date:** November 2040  

---

## Abstract

We present a rigorous framework for optimally partitioning computational tasks between quantum processing units (QPUs) and classical graphics processing units (GPUs) in hybrid quantum-classical AI systems. Drawing on the metaphor of the Bifröst — the bridge between realms, each with its own strengths — we formalize the QPU-GPU partitioning problem as a constrained optimization over latency, throughput, energy, and accuracy. We prove that the optimal partition exists at the boundary where the quantum-classical communication cost equals the marginal computational advantage of the QPU, and we derive closed-form expressions for the optimal partition point under standard noise models. We introduce the **Yggdrasil Scheduler**, a dynamic task-allocation algorithm that balances QPU and GPU workloads in real time using Bayesian performance modeling. Empirical evaluations on four hybrid AI workloads — variational quantum eigensolver (VQE), quantum kernel SVM, hybrid quantum-classical neural network training, and QAOA for combinatorial optimization — demonstrate that Yggdrasil achieves 2.3–4.7× end-to-end speedup over static partitioning and 1.4–2.1× improvement in energy efficiency over GPU-only baselines. Our results provide the first comprehensive guide to **when and how much quantum computation to use** in hybrid AI pipelines.

**Keywords:** hybrid quantum-classical computing, task partitioning, VQE, QAOA, variational circuits, GPU scheduling, NISQ

---

## 1. Introduction

The fundamental architectural question for hybrid quantum-classical AI is not *whether* to use a QPU, but *how much*. Like the Bifröst bridge connecting Midgard to Asgard, the quantum-classical interface is a bottleneck — and the traffic across it must be carefully managed. Every bit of data sent to the QPU incurs a latency cost; every circuit evaluation consumes shot budget; every gradient estimation crosses the boundary twice (parameters in, measurements out). The art of hybrid computing is the art of *partitioning* — deciding which computations belong on which side of the bridge.

This paper addresses three questions:

1. **Where is the optimal boundary between quantum and classical computation?**
2. **How should dynamic workloads be scheduled across heterogeneous QPU-GPU resources?**
3. **What are the fundamental limits on hybrid speedup imposed by communication overhead?**

We formalize the partitioning problem, prove optimality results, and introduce the Yggdrasil Scheduler — a practical algorithm that achieves near-optimal partitioning in real time.

---

## 2. Formal Framework

### 2.1 The Hybrid Computation Model

A hybrid quantum-classical computation is specified as a directed acyclic graph (DAG) $\mathcal{G} = (V, E)$ where each node $v_i \in V$ is a computational task and each edge $e_{ij} \in E$ represents a data dependency. Each task $v_i$ has attributes:

- **Type:** $t_i \in \{\text{QPU}, \text{GPU}, \text{BOTH}\}$ — whether it can run on QPU, GPU, or both
- **Classical cost:** $c_i^{\text{GPU}}$ — execution time on GPU
- **Quantum cost:** $c_i^{\text{QPU}}$ — execution time on QPU (including measurement)
- **Data size:** $d_i$ — number of classical bits/parameters transferred at the boundary
- **Accuracy:** $\alpha_i^{\text{GPU}}, \alpha_i^{\text{QPU}}$ — expected accuracy of each implementation

A **partition** $\pi: V \to \{\text{QPU}, \text{GPU}\}$ assigns each task to a processor.

### 2.2 The Total Cost Model

The total cost of a partition $\pi$ is:

$$\mathcal{C}(\pi) = \underbrace{\sum_{i \in \pi^{-1}(\text{QPU})} c_i^{\text{QPU}}}_{\text{QPU compute}} + \underbrace{\sum_{i \in \pi^{-1}(\text{GPU})} c_i^{\text{GPU}}}_{\text{GPU compute}} + \underbrace{\sum_{(i,j) \in E: \pi(i) \neq \pi(j)} \tau_{\pi(i),\pi(j)} \cdot d_{ij}}_{\text{communication}}$$

where $\tau_{\text{QPU},\text{GPU}}$ is the per-bit transfer latency across the QPU-GPU boundary.

The **accuracy** of partition $\pi$ is:

$$\mathcal{A}(\pi) = \prod_i \alpha_i^{\pi(i)}$$

### 2.3 The Optimization Problem

$$\min_\pi \mathcal{C}(\pi) \quad \text{subject to} \quad \mathcal{A}(\pi) \geq \alpha_{\min}$$

This is a constrained optimization over binary assignments to each task node.

**Theorem 2.1 (NP-hardness).** The optimal hybrid partitioning problem is NP-hard, reducible from the weighted min-cut problem.

*Proof.* Given a weighted min-cut instance $G = (V, E)$ with source $s$ and sink $t$, construct a hybrid partitioning instance where all tasks are type BOTH, with $c_i^{\text{QPU}} = w(v_i)$ for QPU cost and $c_i^{\text{GPU}} = 0$ for GPU cost, and communication costs equal to edge weights. The min-cut corresponds to the optimal partition. $\square$

Despite NP-hardness, practical instances are structured enough for efficient heuristics.

---

## 3. Optimal Partition Point Analysis

### 3.1 The Marginal Advantage Condition

For a task $v_i$ that can run on either processor, the **quantum advantage ratio** is:

$$\rho_i = \frac{c_i^{\text{GPU}}}{c_i^{\text{QPU}} + \tau_{\text{boundary}} \cdot d_i}$$

where $\tau_{\text{boundary}}$ accounts for the communication cost of sending data to and from the QPU.

**Theorem 3.1 (Optimal Partition Boundary).** In the absence of accuracy constraints, the optimal partition assigns task $v_i$ to QPU if and only if $\rho_i > 1$, i.e.:

$$c_i^{\text{GPU}} > c_i^{\text{QPU}} + \tau_{\text{boundary}} \cdot d_i$$

*Proof.* The cost difference between QPU and GPU assignment for task $i$ is:

$$\Delta_i = c_i^{\text{GPU}} - c_i^{\text{QPU}} - \tau_{\text{boundary}} \cdot d_i$$

If $\Delta_i > 0$, assigning to QPU reduces cost. If $\Delta_i < 0$, assigning to GPU reduces cost. The sum over all tasks yields the global minimum by greedy assignment. $\square$

### 3.2 Communication Overhead: The Bifröst Toll

The communication overhead $\tau_{\text{boundary}} \cdot d_i$ is the "toll" for crossing the Bifröst. It consists of:

$$\tau_{\text{boundary}} = \underbrace{\tau_{\text{encode}}}_{\text{data encoding}} + \underbrace{\tau_{\text{queue}}}_{\text{QPU queue}} + \underbrace{\tau_{\text{execute}}}_{\text{circuit execution}} + \underbrace{\tau_{\text{measure}}}_{\text{measurement}} + \underbrace{\tau_{\text{decode}}}_{\text{result processing}}$$

Measured latencies for IBM Eagle v3 (127 qubits):

| Component | Latency |
|-----------|---------|
| $\tau_{\text{encode}}$ (parameter binding) | 0.5 ms |
| $\tau_{\text{queue}}$ (cloud queue) | 1–60 s |
| $\tau_{\text{execute}}$ (per circuit) | 0.1–10 ms |
| $\tau_{\text{measure}}$ (readout) | 0.5 ms |
| $\tau_{\text{decode}}$ (post-processing) | 0.1 ms |
| **Total (no queue)** | ~2 ms |
| **Total (with queue)** | 1–60 s |

**The queue latency dominates.** On cloud QPUs, queuing can be 100–30,000× the circuit execution time. On dedicated QPUs, the boundary cost drops to ~2 ms per circuit.

### 3.3 The Speedup Region

A task $v_i$ achieves quantum speedup if:

$$c_i^{\text{QPU}} < c_i^{\text{GPU}} - \tau_{\text{boundary}} \cdot d_i$$

The maximum achievable speedup for a pipelined hybrid computation is:

$$S_{\max} = \frac{T_{\text{GPU-only}}}{T_{\text{hybrid}}} \leq \frac{1}{(1 - f) + f/\rho}$$

where $f$ is the fraction of compute that is quantum-accelerated and $\rho$ is the average quantum speedup ratio. This is the generalized Amdahl's law for hybrid computing.

**Corollary 3.2.** If the QPU communication overhead is $\tau_{\text{boundary}} = \beta \cdot c^{\text{GPU}}$ (i.e., proportional to the GPU compute time), the maximum achievable speedup is:

$$S_{\max} \leq \frac{1}{1 - f + \beta f}$$

For $\beta = 10^{-3}$ (dedicated QPU) and $f = 0.5$: $S_{\max} \approx 1.98\times$.  
For $\beta = 10$ (cloud QPU with queuing) and $f = 0.5$: $S_{\max} \approx 0.05\times$ (net slowdown!).

The implication is stark: **cloud-based QPU access with queuing cannot provide speedup for interactive training loops.** Only dedicated QPU access or aggressive pipelining can make hybrid computing viable.

### 3.4 Accuracy-Quality Tradeoff

The accuracy constraint $\mathcal{A}(\pi) \geq \alpha_{\min}$ adds a quality dimension. The QPU accuracy includes noise effects:

$$\alpha_i^{\text{QPU}} = 1 - \epsilon_{\text{gate}}^{N_g} - \epsilon_{\text{measure}} - \epsilon_{\text{decoherence}}(d_i)$$

where $N_g$ is the number of gates, $\epsilon_{\text{gate}} \approx 10^{-3}$ is per-gate error, $\epsilon_{\text{measure}} \approx 10^{-2}$ is readout error, and $\epsilon_{\text{decoherence}}(d)$ depends on circuit depth.

For deep circuits ($d > T_2/T_{\text{gate}}$), the accuracy drops to noise floor. This creates a **circuit-depth constraint**:

$$d_i \leq \frac{T_2}{T_{\text{gate}}} \cdot \frac{\log(1/\delta)}{\log(1/\epsilon_{\text{gate}})}$$

for target accuracy $\delta$.

**Theorem 3.3 (Accuracy-limited partition).** If the QPU accuracy for task $v_i$ is $\alpha_i^{\text{QPU}} < \alpha_{\min}$ (due to excessive circuit depth), then $v_i$ must be assigned to GPU regardless of the speedup ratio $\rho_i$.

---

## 4. Task-Specific Partitioning Analysis

### 4.1 Variational Quantum Eigensolver (VQE)

**VQE Pipeline:**

```
[GPU] Initialize θ₀ → [QPU] Prepare |ψ(θ)⟩ → [QPU] Measure ⟨H⟩(θ)
     ↑                                           ↓
[GPU] Update θ ←─── [GPU] Compute gradient ─────┘
```

**Cost breakdown per iteration:**

| Component | GPU Cost | QPU Cost | Boundary Cost |
|-----------|----------|----------|----------------|
| Gradient via parameter-shift | — | $2K \cdot S \cdot T_{\text{circ}}$ | $2K \cdot \tau_{\text{bnd}}$ |
| Parameter update | $O(K)$ | — | — |
| VQA state preparation | — | $T_{\text{circ}} \cdot S$ | $\tau_{\text{bnd}}$ |

where $K = |\vec\theta|$ is the number of parameters and $S$ is shots per circuit.

**Optimal partition:** All circuit evaluations on QPU, all gradient aggregation and parameter updates on GPU. The partition boundary is at the gradient estimation: QPU computes $\langle H \rangle(\theta \pm s\vec{e}_k)$ for each parameter; GPU aggregates and updates.

**Speedup analysis:**

$$\rho_{\text{VQE}} = \frac{K \cdot S \cdot T_{\text{GPU-sim}}}{K \cdot S \cdot T_{\text{QPU}} + 2K \cdot \tau_{\text{bnd}}}$$

For $n = 20$ qubits, $K = 40$, $S = 1024$:
- $T_{\text{GPU-sim}} \approx 100$ ms (statevector simulation)
- $T_{\text{QPU}} \approx 1$ ms per circuit
- $\tau_{\text{bnd}} \approx 2$ ms (dedicated QPU)

$$\rho_{\text{VQE}} = \frac{40 \times 1024 \times 0.1}{40 \times 1024 \times 0.001 + 2 \times 40 \times 0.002} \approx \frac{4096}{42} \approx 97\times$$

**For cloud QPU with 30 s queue time:**

$$\rho_{\text{VQE}} \approx \frac{4096}{40 \times 1024 \times 0.001 + 40 \times 30} \approx \frac{4096}{1200} \approx 3.4\times$$

The queue reduces the speedup from 97× to 3.4× — still positive, but dramatically diminished.

### 4.2 Quantum Kernel SVM

**Pipeline:**

```
[GPU] Preprocess data → [QPU] Compute K_{ij} = |⟨x_i|x_j⟩|² → [GPU] Solve SVM
```

**Cost breakdown:**

| Component | GPU Cost | QPU Cost | Boundary Cost |
|-----------|----------|----------|----------------|
| Kernel matrix (m×m) | $O(m^2 \cdot 2^n)$ simulation | $O(m^2 \cdot S \cdot T_{\text{circ}})$ | $O(m^2 \cdot \tau_{\text{bnd}})$ |
| SVM solver | $O(m^3)$ | — | — |
| Prediction | $O(m \cdot S \cdot T_{\text{circ}})$ per point | on QPU | $O(1) \cdot \tau_{\text{bnd}}$ |

**The $m^2$ factor** makes kernel computation the dominant cost. For classical-hard kernels, the QPU advantage is clear.

### 4.3 Hybrid Neural Network

**Architecture:**

$$\mathbf{h}^{(l+1)} = \sigma\!\left(W^{(l)} \cdot \text{QPU}\!\left(\mathbf{h}^{(l)}; \vec\theta^{(l)}\right) + \mathbf{b}^{(l)}\right)$$

**Key insight:** The QPU layer is typically a **bottleneck** in the backward pass. The forward pass ($\sim 1$ ms per sample) is fast, but the backward pass requires $2|\vec\theta|$ parameter-shift evaluations per training step.

**Partition recommendation:** Use the QPU only for the forward pass and a **GPU-simulated gradient** (finite differences on a GPU-simulated approximation) for the backward pass, as long as the simulation error is below the noise floor.

### 4.4 QAOA for Combinatorial Optimization

**Pipeline:**

```
[GPU] Initialize γ, β → [QPU] Execute QAOA circuit → [QPU] Measure expectation
     ↑                                                       ↓
[GPU] Classical optimization (COBYLA/SPSA) ←── [GPU] Process results
```

**SPSA partitioning:** SPSA requires only 2 circuit evaluations per step regardless of parameter count, making it ideal for cloud QPU access:

$$\rho_{\text{QAOA-SPSA}} = \frac{T_{\text{GPU-eval}}}{2 \cdot (T_{\text{QPU}} + \tau_{\text{bnd}})}$$

---

## 5. The Yggdrasil Scheduler

### 5.1 Algorithm Overview

The Yggdrasil Scheduler dynamically assigns tasks to QPU or GPU based on real-time performance estimates. Named after the World Tree whose roots connect all realms, the scheduler balances the quantum and classical branches of computation.

**Input:** Task graph $\mathcal{G} = (V, E)$, current QPU/GPU state, latency estimates  
**Output:** Assignment $\pi: V \to \{\text{QPU}, \text{GPU}\}$

```
Algorithm: Yggdrasil Scheduler
────────────────────────────────────────────────────────────
1. Initialize: For each task v_i, estimate:
   - μ_i^QPU, σ_i^QPU  (QPU execution time mean+std)
   - μ_i^GPU, σ_i^GPU  (GPU execution time mean+std)
   - α_i^QPU, α_i^GPU  (Expected accuracy)

2. For each task v_i in topological order:
   a. Compute expected cost on each platform:
      C_i^QPU = μ_i^QPU + τ_bnd · d_i + Σ_{j∈pred(i)} C_j^{π(j)}
      C_i^GPU = μ_i^GPU + Σ_{j∈pred(i)} C_j^{π(j)}
   
   b. Compute expected accuracy:
      A_i^QPU = α_i^QPU · Π_{j∈pred(i)} A_j
      A_i^GPU = α_i^GPU · Π_{j∈pred(i)} A_j
   
   c. Assign:
      If C_i^QPU < C_i^GPU AND A_i^QPU ≥ α_min:
         π(v_i) = QPU
      Else:
         π(v_i) = GPU

3. Update performance estimates using Bayesian updating:
   μ_i^QPU ← μ_i^QPU + η · (observed_C_i^QPU - μ_i^QPU)
   σ_i^QPU ← update variance

4. Return π
```

### 5.2 Bayesian Performance Model

The execution time of each task on each platform is modeled as a log-normal distribution:

$$\log T_{\text{QPU}} \sim \mathcal{N}(\mu_{\text{QPU}}, \sigma_{\text{QPU}}^2)$$

with prior updated via conjugate Bayesian updating:

$$\mu_{\text{QPU}}^{(t+1)} = \frac{\kappa_t \mu_{\text{QPU}}^{(t)} + n_t \bar{x}_t}{\kappa_t + n_t}, \quad \kappa_{t+1} = \kappa_t + n_t$$

This allows the scheduler to adapt to queue time fluctuations, hardware failures, and varying circuit compilation times.

### 5.3 Theoretical Guarantee

**Theorem 5.1.** The Yggdrasil Scheduler achieves a partition within a factor of $O(\log n)$ of the optimal partition for a DAG with $n$ task nodes, under stationarity assumptions on execution time distributions.

*Proof sketch.* By the Bayesian concentration of measure, the estimated execution times $\hat{\mu}_i$ converge to true means $\mu_i$ after $O(\log n / \varepsilon^2)$ observations. Once estimates are $\varepsilon$-accurate, the greedy assignment is within $1 + O(\varepsilon)$ of optimal for each task. The DAG structure adds at most $O(\log n)$ overhead from dependencies. $\square$

---

## 6. Empirical Evaluation

### 6.1 Experimental Setup

- **QPU:** IBM Eagle v3 (127 qubits), noise model v3.0
- **GPU:** NVIDIA H100 (8-node cluster)
- **Network:** 100 Gbps InfiniBand between QPU and GPU cluster
- **Benchmarks:** VQE (H₂O, 12 qubits), QSVM (HEP jets, 8 qubits), Hybrid NN (MNIST, 10 qubits), QAOA (MaxCut on Petersen graph, 10 qubits)

### 6.2 Results: End-to-End Latency

| Benchmark | GPU-only | Static QPU | Static Hybrid | Yggdrasil | Speedup |
|-----------|----------|------------|----------------|-----------|---------|
| VQE (H₂O) | 4.2 min | 8.7 min | 3.1 min | 1.8 min | 2.3× |
| QSVM (HEP) | 47 min | 12 min | 8.3 min | 4.5 min | 4.7× |
| Hybrid NN | 6.8 min | 15 min | 5.2 min | 3.5 min | 1.9× |
| QAOA (MaxCut) | 22 min | 18 min | 9.1 min | 5.7 min | 3.9× |

**Yggdrasil achieves 1.9–4.7× speedup over GPU-only baseline** and 1.5–3.2× over static hybrid partitioning (which assigns all QPU-compatible tasks to QPU).

### 6.3 Results: Energy Efficiency

| Benchmark | GPU-only Energy | Hybrid Energy | Yggdrasil Energy | Improvement |
|-----------|----------------|---------------|------------------|-------------|
| VQE (H₂O) | 2.1 MJ | 0.8 MJ | 0.5 MJ | 4.2× |
| QSVM (HEP) | 28 MJ | 1.2 MJ | 0.7 MJ | 40× |
| Hybrid NN | 3.4 MJ | 1.5 MJ | 1.0 MJ | 3.4× |
| QAOA (MaxCut) | 11 MJ | 1.7 MJ | 0.9 MJ | 12.2× |

Energy savings are dramatic for QPU-intensive tasks (QPU operations consume ~picojoules per gate vs. ~nanojoules for GPU operations).

### 6.4 Yggdrasil Adaptation Dynamics

We measured the scheduler's adaptation to changing QPU queue times (simulating cloud QPU with fluctuating demand):

```
Time (min):  0    10    20    30    40    50    60
Queue (s):  2    2     15    30    45    10    2
Yggdrasil:  QPU  QPU   GPU   GPU   GPU   QPU   QPU
Static:     QPU  QPU   QPU   QPU   QPU   QPU   QPU

Total time:
  Yggdrasil:  12 min
  Static:     42 min
  GPU-only:   28 min
```

Yggdrasil dynamically shifts tasks to GPU when QPU queue times exceed the computational advantage threshold, then shifts back when queue times decrease.

### 6.5 Accuracy-Quality Analysis

For tasks where QPU accuracy is noise-limited, Yggdrasil gates certain tasks to GPU:

| Benchmark | QPU Accuracy | GPU Accuracy | Yggdrasil Choice |
|-----------|-------------|-------------|------------------|
| VQE (shallow) | 99.2% | 100% | QPU (acceptable) |
| VQE (deep, d>200) | 87.3% | 100% | GPU (QPU unreliable) |
| QSVM (ZZ feature map) | 98.1% | N/A (classically hard) | QPU |
| Hybrid NN (forward) | 97.5% | 99.8% | QPU + GPU gradient |

The accuracy threshold $\alpha_{\min}$ is set per task based on the downstream requirements.

---

## 7. Fundamental Limits

### 7.1 The Communication Bottleneck

**Theorem 7.1 (Communication lower bound).** For a hybrid computation that transfers $D$ bits across the QPU-GPU boundary, the total computation time satisfies:

$$T_{\text{hybrid}} \geq \frac{D}{B} + \frac{T_{\text{compute}}}{1 + \rho_{\max} \cdot f}$$

where $B$ is the boundary bandwidth and $\rho_{\max}$ is the maximum per-task quantum speedup.

This is the quantum-classical analog of Amdahl's law with communication overhead. For $B = 100$ Gbps and $D = 1$ GB, the communication alone takes 80 ms — acceptable for batch processing, fatal for interactive training.

### 7.2 The Accuracy-Efficiency Pareto Frontier

For each task, there is a Pareto frontier between accuracy and efficiency:

```
Accuracy
  │      ★ GPU-only (high accuracy, low speedup)
  │     ╱
  │    ╱  Hybrid (good balance)
  │   ╱
  │  ╱ QPU-only (lower accuracy, high speedup)
  │ ╱
  └────────────────────── Efficiency (speedup)
```

The Yggdrasil Scheduler navigates this frontier by selecting the platform that maximizes a utility function:

$$U(v_i, \text{platform}) = \lambda \cdot \alpha_i^{\text{platform}} - (1-\lambda) \cdot \frac{C_i^{\text{platform}}}{C_i^{\text{GPU}}}$$

where $\lambda \in [0,1]$ is a user-specified accuracy-efficiency tradeoff parameter.

### 7.3 Quantum Advantage Requires Quantum-Classical Co-design

**Theorem 7.2.** For any hybrid algorithm with a fixed classical component of cost $C_0$ and a quantum speedup factor $\rho$ on fraction $f$ of computation:

$$S_{\max} \leq \frac{1}{1 - f + f/\rho + \beta}$$

where $\beta$ accounts for communication overhead. To achieve $S > 2\times$, we need either:

1. $f \cdot (1 - 1/\rho) > 0.5 + \beta$ (enough quantum computation)
2. $\rho > 1/(1 - f^{-1}(0.5 + \beta))$ (strong enough quantum speedup)

**Implication:** For $\beta = 0.01$ (dedicated QPU), achieving 2× speedup requires $f > 0.52$ with $\rho > 100$, or $f > 0.75$ with $\rho > 4$. This motivates *co-design*: designing algorithms where a large fraction of computation can leverage quantum speedup.

---

## 8. Practical Recommendations

Based on our analysis and empirical results, we provide the following partitioning guidelines:

### 8.1 When to Use the QPU

| Task Type | Use QPU When | Condition |
|-----------|-------------|-----------|
| Kernel evaluation | Classical computation is #P-hard | $\kappa(\mathbf{x}, \mathbf{x}')$ takes >10s classically |
| Circuit evaluation | Shallow circuits ($d < 100$) | QPU accuracy > 95% |
| Gradient estimation | Parameter-shift is feasible | $2K$ circuit runs < queue time |
| Optimization (QAOA) | SPSA is viable | Only 2 circuits per step |
| Large-state simulation | $n > 30$ qubits | Classical simulation infeasible |

### 8.2 When to Use the GPU

| Task Type | Use GPU When | Condition |
|-----------|-------------|-----------|
| Data preprocessing | Always | I/O bound, no quantum advantage |
| Gradient aggregation | Always | Simple vector operations |
| SVM solving | $m < 10^5$ samples | $O(m^3)$ is feasible on GPU |
| Error mitigation | Post-processing | Classical computation |
| Deep circuits ($d > 200$) | Noise too high | QPU accuracy < 90% |

### 8.3 Hybrid Best Practices

1. **Pipeline aggressively:** Overlap QPU circuit execution with GPU preprocessing of the next batch.
2. **Use SPSA for QPU-heavy tasks:** Only 2 circuit evaluations per step, regardless of parameter count.
3. **Batch kernel evaluations:** Submit all $m^2/2$ unique kernel elements in a single QPU job.
4. **Cache compiled circuits:** Pre-compile circuit templates and bind parameters at execution time.
5. **Monitor QPU queue times:** Yggdrasil dynamically shifts tasks to GPU when queuing exceeds threshold.

---

## 9. Discussion

### 9.1 Comparison with Related Work

Previous work on hybrid scheduling (Mitarai et al., 2018; Schuld et al., 2019) focused on static partitioning — assigning all quantum-compatible tasks to QPU and all others to GPU. Our Yggdrasil Scheduler improves on this by:

- **Dynamic adaptation** to fluctuating QPU availability
- **Accuracy-aware** task gating (excluding noise-degraded QPU results)
- **Bayesian performance modeling** that improves scheduling decisions over time
- **Energy optimization** as a secondary objective

### 9.2 Limitations

- **Stationarity assumption:** The Bayesian model assumes slowly-varying execution times; rapid QPU failures can invalidate estimates.
- **Single-QPU model:** Current analysis assumes one QPU; multi-QPU scheduling introduces additional load-balancing challenges.
- **Noise model simplification:** Real hardware noise is correlated and non-Markovian; our per-gate error model is an approximation.
- **Overhead of scheduling:** The Yggdrasil algorithm adds ~0.1 ms per task to the scheduling decision; for very fine-grained tasks, this overhead may be significant.

### 9.3 Future Directions

- **Multi-QPU scheduling:** Extend Yggdrasil to schedule across multiple QPU backends (superconducting, trapped-ion, photonic)
- **Adaptive circuit depth:** Trade circuit depth (accuracy) for execution speed based on Yggdrasil's accuracy threshold
- **Fault-tolerant scheduling:** Integrate quantum error correction overhead into the partitioning model
- **Energy budget optimization:** Co-optimize for wall-clock time and energy consumption under a total energy budget

---

## 10. Conclusion

The optimal partition between QPU and GPU computation is determined by three factors: the **quantum speedup ratio** $\rho$, the **communication overhead** $\tau_{\text{boundary}}$, and the **accuracy constraint** $\alpha_{\min}$. We have shown that:

1. The marginal advantage condition $\rho_i > 1$ determines the optimal platform for each task, subject to accuracy constraints.
2. The Bifröst toll (communication overhead) is the dominant bottleneck for interactive hybrid training loops, and can negate quantum speedup entirely on cloud-based QPU systems.
3. The Yggdrasil Scheduler achieves 1.9–4.7× speedup over static partitioning by dynamically routing tasks based on real-time performance estimates.
4. Energy efficiency improvements of 3.4–40× are achievable by shifting compute to the QPU, depending on the task.

The Norse understood that the Bifröst bridge must be crossed at the right time, in the right way. Too early, and you face the fire; too late, and you miss the battle. Hybrid AI systems must be similarly wise: route tasks to the QPU only when the quantum advantage outweighs the communication cost, and design algorithms that minimize the number of crossings.

The Yggdrasil Scheduler is our implementation of this wisdom — a dynamic, accuracy-aware, energy-efficient task partitioner that roots the quantum and classical realms together through the trunk of optimal scheduling.

---

## References

1. Mitarai, M. et al. "Quantum circuit learning." *Physical Review A* 98, 032309 (2018).
2. Schuld, M. et al. "Evaluating analytic gradients on quantum hardware." *Physical Review A* 99, 032331 (2019).
3. Kandala, A. et al. "Hardware-efficient variational quantum eigensolver." *Nature* 549, 242–246 (2017).
4. McClean, J. R. et al. "The theory of variational hybrid quantum-classical algorithms." *New Journal of Physics* 18, 023023 (2016).
5. Spall, J. C. "Multivariate stochastic approximation using a simultaneous perturbation gradient approximation." *IEEE Trans. Auto. Control* 37, 332–341 (1992).
6. Bharti, K. et al. "Noisy intermediate-scale quantum algorithms." *Reviews of Modern Physics* 94, 015004 (2022).
7. Preskill, J. "Quantum Computing in the NISQ Era and Beyond." *Quantum* 2, 79 (2018).

---

*Yggdrasil's roots drink from three wells — each a source of wisdom, each a condition for growth. The hybrid architect must tend all three roots: speed, accuracy, and efficiency. Neglect one, and the tree withers.*
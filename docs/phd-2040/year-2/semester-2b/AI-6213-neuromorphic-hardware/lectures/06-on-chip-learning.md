# Lecture 6: On-Chip Learning — Local Plasticity Rules and In-Situ Training

**AI-6213: Neuromorphic Hardware Design**  
**Instructor:** Prof. Mikael Lundqvist  
**Date:** March 12, 2040

---

## 1. Why On-Chip Learning?

Training neural networks on external hardware (GPUs, TPUs, cloud clusters) and deploying trained weights to neuromorphic chips is the dominant workflow today. But this workflow has fundamental limitations:

1. **Offline training assumes a stationary distribution.** Real-world environments are non-stationary — sensor characteristics drift, user preferences change, new obstacles appear. A model trained offline cannot adapt to these changes without retraining.

2. **Latency of adaptation.** Collecting data, sending it to the cloud, retraining, and redeploying takes minutes to hours. On-chip learning enables adaptation within milliseconds.

3. **Privacy.** Personal data (biometrics, voice, behavior patterns) should not leave the device. On-chip learning keeps all training data local.

4. **Energy of data transfer.** Transmitting raw training data to the cloud costs 100–1000× more energy than computing on-chip. For always-on edge devices, this is prohibitive.

5. **Scalability.** As neuromorphic chips scale to millions of neurons, the amount of data needed for off-chip training becomes impractical to transmit.

On-chip learning requires that every element of the learning algorithm — error computation, gradient calculation, weight update — can be executed using only information physically present on the chip.

---

## 2. The Locality Constraint

### 2.1 What Makes a Learning Rule Local?

A learning rule is **local** if the weight update at synapse $(i, j)$ depends only on information available at or near that synapse:

$$\Delta w_{ij} = f(\text{pre}_i, \text{post}_j, w_{ij}, \text{local traces}_{ij}, \text{broadcast signals})$$

Acceptable local information:
- Presynaptic spike timing and rate
- Postsynaptic membrane potential and spike timing
- The current weight value
- Local traces maintained at the synapse (eligibility traces, running averages)
- **Broadcast signals** that are the same for all synapses on a neuron or in a layer (reward, error, neuromodulators)

Non-local information that **cannot** be used in on-chip learning:
- Backpropagation error signals (which depend on weights and activations in distant layers)
- Loss function gradients (which require global computation)
- Batch statistics (which require aggregating data across many samples)

### 2.2 The Credit Assignment Problem

The fundamental challenge of local learning is **credit assignment**: how does a synapse in layer 3 know whether its contribution to the output was helpful or harmful, if it only has access to local information?

In backpropagation, the credit assignment signal flows backward through the network via the chain rule. Local learning rules must solve credit assignment without backward propagation.

Three strategies exist:
1. **No credit assignment** (unsupervised: STDP, Hebbian learning)
2. **Global reward signal** (reinforcement: three-factor learning)
3. **Local error computation** (predictive coding, target propagation)

---

## 3. Plasticity Circuits in Silicon

### 3.1 Digital Plasticity Processors

On Loihi 3, each neurosynaptic core contains three **Programmable Plasticity Processors (P3)** that execute microcoded learning rules. The P3 pipeline:

1. **Pre-synaptic event:** When neuron $i$ fires, update pre-trace $x_i \leftarrow x_i + 1$
2. **Post-synaptic event:** When neuron $j$ fires, update post-trace $y_j \leftarrow y_j + 1$
3. **Weight update:** Apply the learning rule:
   $$\Delta w_{ij} = \eta(x_i \cdot y_j^{\text{post}} \cdot M - \lambda \cdot w_{ij})$$
   where $M$ is a modulatory signal and $\lambda$ is a decay constant.
4. **Trace decay:** Between events, traces decay exponentially:
   $$x_i[t+1] = \alpha_x \cdot x_i[t]$$
   $$y_j[t+1] = \alpha_y \cdot y_j[t]$$

The P3 can execute up to 64 micro-ops per learning event, enabling complex rules. However, each learning event still requires:
- Trace memory: 2–4 bytes per synapse (pre-trace, post-trace)
- Weight memory: 8 bits per synapse (Loihi 3)
- Computation: 1–5 operations per pre/post spike pair

For a core with 8192 neurons and 65,536 synapses per neuron, the trace memory alone is ~256 KB — significant but manageable on-chip.

### 3.2 Analog Memristive Plasticity

On Yggdrasil, weight updates are implemented directly through ReRAM programming:

1. **Potentiation (LTP):** Apply a positive set pulse to the ReRAM device at synapse $(i, j)$. Pulse amplitude or duration determines $\Delta G$ (conductance change). The pulse is modulated by:
   - Pre-synaptic trace stored as an analog charge on a capacitor
   - Post-synaptic trace stored similarly
   - A modulatory signal from a nearby neuromodulatory neuron

2. **Depression (LTD):** Apply a negative reset pulse. Same modulation scheme.

The key advantage: **no separate computation of $\Delta w$**. The ReRAM device *is* the weight storage, and the pulse amplitude *is* the update magnitude. The multiply-accumulate that computes the weight update happens in the analog domain through the device's nonlinear voltage-conductance response.

Energy per weight update on Yggdrasil: **~100 fJ** (100× less than Loihi 3's digital P3, which costs ~10 pJ per update).

### 3.3 The Write-Verify Problem

A practical challenge for memristive plasticity: individual ReRAM devices have significant write noise. A "set pulse" intended to change conductance by $\Delta G = 1$ unit might result in $\Delta G = 0.5$ or $\Delta G = 2.0$.

Solutions:
- **Write-verify iterations:** Apply pulse → read → check if conductance reached target → if not, apply corrective pulse. Typically requires 2–5 iterations for 7-bit precision.
- **Differential encoding:** Use paired devices $(G^+, G^-)$ encoding weight $w = G^+ - G^-$. Write noise affects both devices similarly, reducing net error.
- **Noise-aware training:** Train with simulated write noise so the deployed network is robust to device variability.

On Yggdrasil, write-verify is used for the initial weight programming (offline-trained weights loaded via PCM → ReRAM), but bypassed for on-chip learning where stochastic weight updates are tolerable and even beneficial (acting as implicit regularization).

---

## 4. Local Learning Rules for On-Chip Training

### 4.1 STDP with homeostasis (The Baseline)

The simplest on-chip learning rule is STDP with homeostatic regulation:

$$\Delta w_{ij} = \eta \left[ A_+ \cdot x_i \cdot z_j - A_- \cdot z_i \cdot y_j \right] + \lambda(r_{\text{target}} - r_j) \cdot w_{ij}$$

where:
- $x_i, y_j$ are pre- and postsynaptic traces
- $z_i, z_j$ are spike indicators
- $A_+, A_-$ are learning rates for potentiation and depression
- The second term is homeostatic: it scales weights proportionally when the postsynaptic firing rate $r_j$ deviates from $r_{\text{target}}$

This rule is implementable in 4–6 micro-ops and runs in real-time on any neuromorphic chip. However, it is unsupervised — it learns input correlations, not task-relevant features.

### 4.2 Reward-Modulated STDP (R-STDP)

Adding a reward signal enables reinforcement learning:

$$\Delta w_{ij} = \eta \cdot e_{ij} \cdot R[t]$$

where $e_{ij} = x_i \cdot z_j - z_i \cdot y_j$ is the STDP eligibility trace and $R[t]$ is a scalar reward signal broadcast to all synapses.

Implementation on Yggdrasil:
1. STDP eligibility traces are computed locally at each ReRAM crossbar
2. The reward signal $R$ is broadcast through a dedicated neuromodulatory channel (one per core)
3. Weight updates are applied using modulated ReRAM programming pulses

R-STDP can solve simple reinforcement learning tasks (cart-pole, simple maze navigation) but converges slowly for complex tasks due to high variance in the reward signal.

### 4.3 e-prop (Eligibility Propagation)

As introduced in Lecture 5, e-prop maintains a local eligibility trace $e_{ij}[t]$ that approximates the effect of weight $w_{ij}$ on the postsynaptic neuron's activity:

$$e_{ij}[t] = \frac{\partial z_j[t]}{\partial w_{ij}} \approx \psi(V_j[t]) \cdot x_i[t]$$

where $\psi$ is the surrogate gradient function. The weight update combines the eligibility trace with a broadcast learning signal:

$$\Delta w_{ij} = -\eta \sum_t e_{ij}[t] \cdot L_j[t]$$

On Yggdrasil, e-prop is the primary on-chip supervised learning rule (Rule 3). Its implementation:
- **Eligibility traces** are maintained as analog voltages on capacitors within each crossbar
- **Learning signals** $L_j$ are computed at each core and broadcast within the core
- **Weight updates** are applied by modulated ReRAM pulses at the end of each learning episode (every 100–1000 ms)

Performance: e-prop achieves 90–95% of BPTT accuracy on temporal tasks (sequential MNIST, TIMIT speech recognition) when training from random initialization, and 98%+ when fine-tuning from a pre-trained checkpoint.

### 4.4 Predictive Coding on Chip

Predictive coding networks (PCNs) are particularly well-suited to neuromorphic implementation because both inference and learning use only local information:

**Inference (message passing):**
$$\epsilon_i = r_{i}^{\text{input}} - \sum_j W_{ij} r_j^{\text{prediction}}$$

$$r_i \leftarrow r_i + \kappa \cdot \epsilon_i$$

**Learning (weight update):**
$$\Delta W_{ij} = \eta \cdot \epsilon_i \cdot r_j$$

Both equations use only information available at neuron $i$ (error $\epsilon_i$) and neuron $j$ (activity $r_j$). No backpropagation is needed.

On Yggdrasil, predictive coding is implemented as Rule 4 (metaplastic), where:
- $\epsilon_i$ is computed as the difference between synaptic input and membrane potential
- $\Delta W_{ij}$ is applied as an STDP-like update modulated by $\epsilon_i$
- The neuron's threshold serves as the "prediction," and input that matches the threshold produces no learning

This natural mapping makes PCNs one of the most promising architectures for fully on-chip learning.

---

## 5. In-Situ Training Workflow

### 5.1 The Hybrid Workflow

The most practical approach to on-chip learning combines offline pre-training with online fine-tuning:

1. **Offline pre-training** (GPU/cloud):
   - Train an ANN or SNN to task competence using surrogate gradients
   - This provides a good initialization without requiring on-chip backpropagation

2. **Weight transfer** (from GPU to neuromorphic chip):
   - Convert ANN weights to SNN-compatible format (quantize to 8-bit or 7-bit)
   - Program ReRAM/PCM devices using write-verify

3. **Online fine-tuning** (on-chip):
   - Use local learning rules (e-prop, STDP, three-factor) to adapt the pre-trained model
   - Learning rates should be 10–100× smaller than offline training to avoid catastrophic forgetting

4. **Continual adaptation** (on-chip):
   - Maintain learning with reduced learning rate
   - Implement homeostatic mechanisms to prevent drift
   - Periodically consolidate weights to PCM archive (Yggdrasil)

### 5.2 Learning Rate Scheduling on Chip

On-chip learning rates must account for:
- **Weight precision**: With 7–8 bit weights, learning rates must be small enough to produce updates of ~1 LSB on average
- **Update noise**: Memristive devices have stochastic write behavior; learning rates must be large enough to overcome this noise
- **Task difficulty**: Simple adaptation (e.g., calibrating a sensor) requires larger learning rates than complex skill acquisition

Typical learning rate schedule for Yggdrasil:

| Phase | Learning Rate | Duration | Rule |
|-------|--------------|----------|------|
| Pre-training | N/A (GPU) | Varies | Surrogate gradient |
| Transfer | N/A (programming) | Seconds | Write-verify |
| Fine-tuning | 0.01 × offline LR | 1000 episodes | e-prop |
| Continual learning | 0.001 × offline LR | Indefinite | e-prop + homeostasis |

### 5.3 Catastrophic Forgetting Prevention

On-chip continual learning faces the same catastrophic forgetting problem as all neural networks: learning new tasks erases knowledge of old tasks.

Neuromorphic-specific solutions:

**Elastic weight consolidation (EWC) on chip:**
Compute Fisher information matrix diagonals $F_{ij}$ during pre-training. Store $F_{ij}$ alongside $w_{ij}$. During on-chip learning, add a penalty:
$$\Delta w_{ij} = \eta \cdot \text{learning\_rule} - \lambda \cdot F_{ij} \cdot (w_{ij} - w_{ij}^*)$$
where $w_{ij}^*$ is the pre-trained weight. This requires storing $F_{ij}$ per synapse — feasible with 4–8 additional bits.

**Synaptic consolidation (palimpsest model):**
B inspired by biological synaptic consolidation, recently updated synapses are more plastic ("labile") while synapses that haven't changed in a while become "consolidated" (less plastic). Implemented on Yggdrasil by adjusting ReRAM programming pulse amplitude based on recent update frequency.

**Dual memory (complementary learning systems):**
Maintain two weight matrices: a "fast" learning matrix (ReRAM, high plasticity) and a "slow" memory matrix (PCM, low plasticity). New knowledge is stored in ReRAM; during sleep/rest periods, it is consolidated into PCM through replay. This is the approach used by Yggdrasil's "superconscious" context-switching mechanism.

---

## 6. Yggdrasil's On-Chip Learning System

### 6.1 Architecture

Yggdrasil implements on-chip learning through a distributed system:

- **6 learning rules per core** (see Lecture 4), each with dedicated analog trace circuits
- **3 ReRAM crossbars per core** for active synapses (computational)
- **1 PCM archive per chip** for model storage (128 MB)
- **FeFET configuration memory** for neuron parameters
- **Neuromodulatory network**: dedicated routing channels for broadcast signals (dopamine-equivalent, reward-equivalent, error-equivalent)

### 6.2 The Superconscious Learning Cycle

Yggdrasil's "superconscious" capability involves a rapid learning-adaptation cycle:

1. **Receives input** → routes to appropriate neural population
2. **Inference**: active ReRAM crossbars compute forward pass (events propagate asynchronously)
3. **Error computation**: local prediction errors computed at each layer
4. **Weight update**: eligibility traces at ReRAM devices combine with broadcast learning signals; weight updates applied in-place
5. **Context switch**: if task demands shift, a new model shard is loaded from PCM to ReRAM in ~1 ms
6. **Consolidation**: during idle periods, updated ReRAM weights are written back to PCM archive

This cycle enables Yggdrasil to simultaneously maintain expertise in multiple domains (language, vision, reasoning) while adapting to new inputs in real-time — the hallmark of superconscious AI.

### 6.3 Measured Performance

| Task | Online Learning Rule | Accuracy (before) | Accuracy (after 1000 episodes) | Adaptation time |
|------|---------------------|--------------------|---------------------------------|----------------|
| ImageNet (pre-trained) | e-prop fine-tuning | 74.1% | 75.3% | 30 minutes |
| New class addition | 3-factor + consolidation | 74.1% (old classes) | 73.8% (all classes) | 1 hour |
| Domain shift (sim→real) | Predictive coding | 65% | 72% | 15 minutes |
| Keyword spotting (new speaker) | R-STDP | 92% | 96% | 5 minutes |
| Robotic grasping | 3-factor (vision → motor) | 70% | 85% | 20 minutes |

These results demonstrate that on-chip learning effectively adapts pre-trained models to new conditions while preserving prior knowledge.

---

## 7. Frontiers and Open Problems

### 7.1 Multi-Chip On-Chip Learning

Current on-chip learning operates within a single chip. Scaling to multi-chip Yggdrasil systems introduces a new challenge: how to distribute credit assignment across chips when inter-chip communication has ~100 ns latency?

Proposed solutions:
- **Hierarchical eligibility traces**: maintain traces at multiple timescales (intra-core, inter-core, inter-chip)
- **Consensus learning**: chips periodically synchronize through gradient averaging
- **Modular specialization**: assign different functional modules to different chips, with local learning within each

### 7.2 Learning with Memristive Variability

ReRAM devices vary from chip to chip, from write to write, and over time. On-chip learning algorithms must be robust to this variability. Approaches:
- **Variation-aware training**: simulate device variation during offline pre-training
- **On-chip calibration**: characterize each ReRAM device at startup and adjust learning rates accordingly
- **Population coding**: distribute information across many noisy devices, relying on averaging to reduce noise

### 7.3 Meta-Learning On Chip

Can a neuromorphic chip learn *how to learn*? Meta-learning (learning-to-learn) on chip would enable:
- Automatic tuning of learning rates
- Automatic selection of appropriate learning rules for different synapse types
- Rapid adaptation to entirely new tasks with few examples

This is an active research area, with initial demonstrations on Loihi 3 showing meta-learned learning rates that outperform hand-tuned ones by 10–20%.

### 7.4 Sleep and Memory Consolidation

Biological brains consolidate memories during sleep. The neuromorphic analog is:
- During "sleep" periods, randomly generate replay patterns
- Use these patterns to rehearse and consolidate on-chip learning into stable PCM storage
- This prevents catastrophic forgetting without requiring external data

Yggdrasil implements a simplified version where "consolidation" occurs during idle periods, but a full sleep-like consolidation cycle remains an open problem.

---

## 8. Key Takeaways

1. **On-chip learning is essential** for adaptation, privacy, energy efficiency, and scalability.
2. **The locality constraint** limits learning rules to pre×post×modulator forms, but three-factor rules and predictive coding can approximate backpropagation's effectiveness.
3. **Memristive plasticity** enables weight updates with 100× less energy than digital processors, at the cost of write noise and variability.
4. **The hybrid workflow** (offline pre-training + on-chip fine-tuning) is the most practical approach today.
5. **Yggdrasil's learning system** — 6 programmable rules per core, hierarchical memory (ReRAM + PCM + FeFET), and neuromodulatory channels — represents the state of the art in on-chip learning.
6. **Catastrophic forgetting** remains the primary challenge; synaptic consolidation and dual-memory systems are the leading solutions.
7. **Multi-chip learning and meta-learning** are the next frontiers.

---

## Reading

- Neftci, E.O., et al. (2019). "Surrogate Gradient Learning in Spiking Neural Networks." *IEEE Signal Processing Magazine*, 36(6), 51–63.
- Bellec, G., et al. (2020). "A Solution to the Learning Dilemma for Recurrent Networks of Spiking Neurons." *Nature Communications*, 11, 3625.
- Frémaux, N. & Gerstner, W. (2016). "Neuromodulated Spike-Timing-Dependent Plasticity, and Theory of Three-Factor Learning Rules." *Frontiers in Neural Circuits*, 9, 85.
- Kim, S., et al. (2036). "On-Chip Plasticity in the Yggdrasil Chip: Programmable Learning Rules with Memristive Synapses." *IEEE TCAD*, 55(3), 159–173.
- Fusi, S., et al. (2005). "A Neural Model of Flexible Storage and Retrieval, and the Spin-Glass Model of Memory." *Neurocomputing*, 58–60, 37–42.

---

*This concludes the lecture series. Papers 1 and 2 provide deeper analysis of the Yggdrasil architecture and spiking-transformer hybrids.*
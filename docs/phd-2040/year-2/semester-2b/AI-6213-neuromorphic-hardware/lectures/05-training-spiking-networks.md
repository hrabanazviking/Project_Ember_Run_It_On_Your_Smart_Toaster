# Lecture 5: Training Spiking Neural Networks — Surrogate Gradients, STDP, and Local Learning Rules

**AI-6213: Neuromorphic Hardware Design**  
**Instructor:** Prof. Mikael Lundqvist  
**Date:** March 5, 2040

---

## 1. The Training Problem

Training spiking neural networks is fundamentally harder than training artificial neural networks (ANNs). The source of difficulty is one equation:

$$z[t] = \Theta(V_m[t] - V_{\text{th}})$$

where $\Theta$ is the Heaviside step function. The derivative $\Theta'$ is zero everywhere except at $V_m = V_{\text{th}}$, where it is undefined (or a Dirac delta, depending on your perspective). This makes the chain rule of backpropagation — which relies on smooth derivatives — inapplicable.

In ANNs, activation functions like ReLU and sigmoid have well-defined gradients everywhere (or almost everywhere, for ReLU). In SNNs, the spike generation mechanism is a hard threshold — information is destroyed at each layer.

This lecture covers the three principal approaches to training SNNs:

1. **Surrogate gradients**: replace the non-differentiable spike function with a smooth proxy during training
2. **Spike-timing-dependent plasticity (STDP)**: biologically inspired Hebbian learning
3. **Local learning rules**: computationally efficient rules that use only locally available information

---

## 2. Surrogate Gradient Methods

### 2.1 The Core Idea

Surrogate gradient methods (Neftci et al., 2019) are the most successful approach to training deep SNNs. The key insight is simple: **during the forward pass, use the real spike function; during the backward pass, replace its derivative with a smooth approximation.**

Forward pass (exact):
$$z[t] = \Theta(V_m[t] - V_{\text{th}})$$

Backward pass (surrogate):
$$\frac{\partial z}{\partial V_m} \approx \sigma'(V_m[t] - V_{\text{th}})$$

where $\sigma'$ is the derivative of a smooth sigmoid-like function. Common choices:

| Surrogate | $\sigma'(x)$ | Properties |
|-----------|-----------|------------|
| Fast Sigmoid | $\frac{1}{(\beta \|x\| + 1)^2}$ | Most common; $\beta$ controls sharpness |
| ArcTangent | $\frac{1}{\pi}\frac{\beta}{1+(\beta x)^2}$ | Smooth, plateau-free |
| Piecewise Linear | $\max(0, 1 - \beta\|x\|)$ | Computationally cheap |
| Gaussian | $\beta \exp(-\beta^2 x^2 / 2)$ | Smooth, fast decay |

The parameter $\beta$ controls the steepness of the surrogate. High $\beta$ approximates the true threshold more closely but leads to vanishing gradients for neurons far from threshold. $\beta$ is typically set to 10–100.

### 2.2 Backpropagation Through Time (BPTT) for SNNs

Applying surrogate gradients within BPTT for SNNs involves unrolling the LIF dynamics over time:

$$\frac{\partial \mathcal{L}}{\partial w_i} = \sum_{t} \frac{\partial \mathcal{L}}{\partial z[t]} \cdot \frac{\partial z[t]}{\partial V_m[t]} \cdot \frac{\partial V_m[t]}{\partial w_i}$$

The chain passes through the surrogate gradient at each time step, and the membrane potential has recurrent dependencies:

$$\frac{\partial V_m[t]}{\partial w_i} = \alpha \frac{\partial V_m[t-1]}{\partial w_i} + (1-\alpha) \cdot s_i[t-1]$$

This gives us proper temporal credit assignment — we can attribute output errors to spikes that occurred many time steps earlier.

### 2.3 Practical Training Recipes

**Recipe 1: ANN-to-SNN with Surrogate Fine-Tuning**
1. Train an equivalent ANN (ReLU network)
2. Convert to SNN using rate coding
3. Fine-tune with surrogate gradients for T=100–300 timesteps
4. Typical accuracy recovery: 98–99.5% of ANN accuracy

**Recipe 2: Native SNN Training from Scratch**
1. Initialize weights with care (spectral radius, firing rate regularization)
2. Train with surrogate gradients for T=50–200 timesteps
3. Use threshold regularization to maintain target firing rates (5–20%)
4. Lower learning rate over time, just as in ANN training

**Recipe 3: Hybrid ANN-SNN Training**
1. Use an ANN backbone for early layers (where temporal dynamics are less critical)
2. Use SNN layers for later layers (where temporal processing adds value)
3. Train end-to-end with surrogate gradients for SNN layers and standard backprop for ANN layers

### 2.4 Challenges and Solutions

**Vanishing/exploding gradients through time:** As in RNNs, gradients can vanish or explode over long time sequences. Solutions:
- Gradient clipping (max norm = 1.0 is common)
- Detaching gradients at careless time steps ($\frac{\partial V_m[t]}{\partial V_m[t-k]} \approx 0$ for $k > K$)
- Eligibility traces (see Section 4)

**Firing rate collapse or explosion:** Without regularization, SNNs tend to either die (no spikes) or saturate (constant spiking). Solutions:
- Threshold regularization: add a penalty $\lambda(V_{\text{th}} - V_{\text{target}})^2$ to the loss
- Firing rate regularization: penalize deviations from target rate
- Learnable thresholds: allow $V_{\text{th}}$ to be a trainable parameter

**Long time dependencies:** SNNs struggle with dependencies spanning >100 timesteps. Solutions:
- Intrinsically recurrent architectures (LSNN, ALIF)
- Multi-timescale neurons (fast and slow time constants)
- Hierarchical processing with skip connections

---

## 3. Spike-Timing-Dependent Plasticity (STDP)

### 3.1 Biological Basis

STDP is the most widely studied form of synaptic plasticity in neuroscience. It was first characterized systematically by Markram et al. (1997) and Bi & Poo (1998):

- If a presynaptic spike precedes a postsynaptic spike ($\Delta t = t_{\text{post}} - t_{\text{pre}} > 0$), the synapse is **strengthened** (long-term potentiation, LTP).
- If a presynaptic spike follows a postsynaptic spike ($\Delta t < 0$), the synapse is **weakened** (long-term depression, LTD).

The magnitude of the weight change follows an exponential learning window:

$$\Delta w = \begin{cases} A_+ \exp(-\Delta t / \tau_+) & \text{if } \Delta t > 0 \quad (\text{LTP}) \\ -A_- \exp(\Delta t / \tau_-) & \text{if } \Delta t < 0 \quad (\text{LTD}) \end{cases}$$

Typical parameters: $A_+ = 0.01$, $A_- = 0.012$, $\tau_+ = \tau_- = 20$ ms (asymmetric: $A_- > A_+$ for stability).

### 3.2 STDP in Hardware

On Loihi 3, STDP is implemented using **trace variables**:

- $x_i[t]$: presynaptic trace (increments by 1 on each presynaptic spike, decays with time constant $\tau_x$)
- $y_j[t]$: postsynaptic trace (increments by 1 on each postsynaptic spike, decays with time constant $\tau_y$)

Update rules:
- On presynaptic spike at time $t$: $w_{ij} \leftarrow w_{ij} + A_- \cdot y_j[t]$ (LTD)
- On postsynaptic spike at time $t$: $w_{ij} \leftarrow w_{ij} + A_+ \cdot x_i[t]$ (LTP)

Trace variables are cheap to maintain (2 per synapse) and enable localized, spike-triggered learning without storing spike timing history.

On Yggdrasil, STDP traces are maintained in analog circuits within each ReRAM crossbar, consuming near-zero additional power. The weight update is applied directly to the ReRAM device using a pulse whose amplitude is proportional to the trace value.

### 3.3 Limitations of Vanilla STDP

Vanilla STDP is limited as a learning rule for practical tasks:

1. **No task-level gradient.** STDP is a purely local, correlational rule — it doesn't know about the overall objective function. It can learn input correlations but not supervised targets.

2. **Unstable dynamics.** Without homeostatic mechanisms, STDP leads to either weight collapse (all weights → 0) or runaway excitation (all weights → max).

3. **Slow convergence.** Biological learning is slow — hours to days of real-time experience. We need faster learning for engineering applications.

4. **Limited precision.** With low-precision weights (8-bit on Loihi, 7-bit on Yggdrasil), STDP updates can be quantization-dominated.

These limitations are why STDP is primarily used as a component of more sophisticated learning rules rather than as a standalone training method.

---

## 4. Local Learning Rules

### 4.1 Motivation

Backpropagation through time (BPTT) with surrogate gradients is powerful but problematic for neuromorphic hardware:

- **Memory cost:** BPTT requires storing all intermediate states across time, consuming $O(N \cdot T)$ memory for $N$ neurons over $T$ timesteps. For Yggdrasil with 1M neurons and T=1000, this is infeasible on-chip.
- **Non-locality:** The gradient at synapse $w_{ij}$ depends on error signals computed far away in the network, violating the principle of local computation.

Local learning rules use only information available at or near the synapse:
- Presynaptic activity ($x_i$)
- Postsynaptic activity ($y_j$, $V_m^j$, or spike timing)
- A global modulatory signal ($M$, e.g., reward, prediction error)
- The current weight ($w_{ij}$)

$$\Delta w_{ij} = f(x_i, y_j, w_{ij}, M)$$

### 4.2 Three-Factor Learning Rules

The most successful local learning rules are **three-factor rules**, combining Hebbian pre-post correlation with a global modulatory signal:

$$\Delta w_{ij} = \eta \cdot x_i \cdot y_j \cdot M$$

where $M$ is a **neuromodulatory signal** such as reward, dopamine, or prediction error. This structure was first proposed by Seung (2003) and has been validated in neuroscience (reward-modulated STDP in dopaminergic circuits).

Variants:

**Reward-modulated STDP (R-STDP):**
$$\Delta w_{ij}[t] = \eta \cdot \text{STDP}(\Delta t_{ij}) \cdot (R[t] - \bar{R})$$

where $R[t]$ is the reward and $\bar{R}$ is the mean reward. This enables reinforcement learning in SNNs.

**Eligibility traces with delayed modulation:**
$$\Delta w_{ij} = \eta \cdot e_{ij} \cdot \delta$$

where $e_{ij}$ is the eligibility trace (a slowly decaying version of pre×post activity) and $\delta$ is a top-down error signal. This approximates backpropagation in networks where the error signal arrives later than the pre-post correlation.

### 4.3 The e-prop Framework

Bellec et al. (2020) introduced **e-prop** (eligibility propagation), a local learning rule that approximates BPTT for recurrent SNNs:

1. Each synapse maintains a local **eligibility trace** $e_{ij}[t]$ that approximates the temporal gradient $\frac{\partial z_j[t]}{\partial w_{ij}}$.
2. A global **learning signal** $L_j[t]$ broadcasts a top-down error to all synapses of neuron $j$.
3. The weight update is: $\Delta w_{ij} = \sum_t e_{ij}[t] \cdot L_j[t]$

This is local in the sense that synapse $w_{ij}$ only needs information from its pre- and postsynaptic neurons, plus a broadcast learning signal. On Loihi 3, e-prop can be implemented using the P3 learning engine with two traces per synapse.

On Yggdrasil, e-prop is one of the pre-built learning rules (Rule 3: eligibility), leveraging the analog trace circuits for near-zero computational overhead.

### 4.4 Predictive Coding Networks

Predictive coding is an alternative framework that naturally yields local learning rules. In predictive coding networks (PCNs):

1. Each neuron maintains a **prediction** of its input.
2. The **prediction error** (difference between actual and predicted input) drives both inference and learning.
3. Learning minimizes the prediction error: $\Delta w_{ij} \propto \epsilon_i \cdot r_j$, where $\epsilon_i$ is neuron $i$'s prediction error and $r_j$ is neuron $j$'s activity (or prediction).

PCNs are particularly attractive for neuromorphic hardware because:
- Learning is strictly local (prediction errors are computed at each neuron)
- Inference and learning are interleaved (not separate phases)
- They naturally handle hierarchical processing
- They can implement backpropagation as a special case under certain conditions (Whittington & Bogacz, 2017)

Yggdrasil's Rule 4 (metaplastic) partially implements a predictive coding scheme by adjusting the threshold based on prediction error.

---

## 5. Training in Practice: A Decision Framework

| Goal | Recommended Method | Hardware |
|------|-------------------|---------|
| Maximum accuracy on static tasks | ANN-to-SNN conversion + surrogate fine-tuning | GPU (train) → Neuromorphic (deploy) |
| Temporal processing tasks | Native surrogate gradient training | GPU (train) → Neuromorphic (deploy) |
| On-chip adaptation (fixed environment) | STDP + homeostatic regulation | Loihi 3 / Yggdrasil (on-chip) |
| On-chip reinforcement learning | R-STDP / three-factor rules | Loihi 3 / Yggdrasil (on-chip) |
| On-chip supervised learning | e-prop | Loihi 3 / Yggdrasil (on-chip) |
| Superconscious model adaptation | Predictive coding + eligibility traces | Yggdrasil (on-chip) |

---

## 6. Quantitative Comparison

### 6.1 Accuracy on ImageNet (ResNet-50 equivalent)

| Training Method | ANN Baseline | SNN Accuracy | Timesteps | Gap |
|----------------|-------------|-------------|-----------|-----|
| ANN-to-SNN conversion | 76.1% | 75.2% | 350 | 0.9% |
| Surrogate gradient (from scratch) | 76.1% | 74.6% | 200 | 1.5% |
| Hybrid ANN-SNN | 76.1% | 75.5% | 150 | 0.6% |
| e-prop (on-chip fine-tuning) | 75.2% (pre-trained) | 73.8% | 200 | 2.3% |
| STDP only | N/A | 62–68% | Varies | N/A |

### 6.2 Memory Requirements for Training

| Method | Memory per Synapse | Total Memory (1M neurons, 256 fan-in) |
|--------|-------------------|--------------------------------------|
| BPTT (T=100) | ~800 bytes | 200 GB |
| Surrogate BPTT (T=100) | ~800 bytes | 200 GB |
| e-prop | ~8 bytes | 2 GB |
| STDP | ~4 bytes | 1 GB |
| Three-factor | ~12 bytes | 3 GB |

This illustrates why on-chip learning must use local rules: BPTT's memory requirements exceed what can be stored on any neuromorphic chip.

---

## 7. Key Takeaways

1. **Surrogate gradients** are the most effective method for training SNNs in software, achieving within 1–2% of ANN accuracy on standard benchmarks.
2. **STDP** is biologically inspired and hardware-friendly but limited to learning input correlations without task-level guidance.
3. **Three-factor rules** (pre × post × modulator) bridge the gap between local computation and task-level learning.
4. **e-prop** is the leading candidate for on-chip training, achieving near-BPTT performance with local computations.
5. **Predictive coding** offers an elegant alternative where inference and learning are naturally interleaved.
6. **Memory cost** is the fundamental constraint — local learning rules require 50–200× less memory than BPTT, making them the only viable option for on-chip training.

---

## Reading

- Neftci, E.O., et al. (2019). "Surrogate Gradient Learning in Spiking Neural Networks." *IEEE Signal Processing Magazine*, 36(6), 51–63.
- Bellec, G., et al. (2020). "A Solution to the Learning Dilemma for Recurrent Networks of Spiking Neurons." *Nature Communications*, 11, 3625.
- Markram, H., et al. (1997). "Regulation of Synaptic Efficacy by Coincidence of Postsynaptic APs and EPSPs." *Science*, 275(5297), 213–215.
- Bi, G.Q. & Poo, M.M. (1998). "Synaptic Modifications in Cultured Hippocampal Neurons: Dependence on Spike Timing, Synaptic Strength, and Postsynaptic Cell Type." *Journal of Neuroscience*, 18(24), 10464–10472.
- Seung, H.S. (2003). "Learning in Spiking Neural Networks by Reinforcement of Stochastic Synaptic Transmission." *Neuron*, 40(6), 1203–1214.
- Whittington, J.C.R. & Bogacz, R. (2017). "An Approximation of the Error Backpropagation Algorithm in a Predictive Coding Network with Local Hebbian Synaptic Plasticity." *Neural Computation*, 29(5), 1229–1262.

---

*Next lecture: On-Chip Learning — making plasticity happen on the silicon itself.*
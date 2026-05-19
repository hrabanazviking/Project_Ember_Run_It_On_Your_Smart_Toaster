# Lecture 1: Spiking Neural Networks — Theory and Implementation

**AI-6213: Neuromorphic Hardware Design**  
**Instructor:** Prof. Mikael Lundqvist  
**Date:** February 5, 2040

---

## 1. Introduction: Why Spikes?

The fundamental unit of computation in biological neural networks is not a floating-point multiplication but a *spike* — a transient, all-or-nothing electrical event that propagates along axons and across synapses. Spikes carry information through their *timing*, not their amplitude. A spiking neuron that fires at $t = 14.3\text{ms}$ encodes something different from one that fires at $t = 14.7\text{ms}$.

This temporal coding capacity has a profound implication for hardware: if computation is sparse (neurons only consume energy when they spike), and if spikes are events rather than continuous values, then the entire computational paradigm shifts from *clock-driven* to *event-driven*. A conventional processor consumes energy every clock cycle regardless of whether it's doing useful work. A spiking processor consumes energy only when a neuron fires — and most neurons, most of the time, are silent.

The sparsity of neural activity in biological systems is staggering. In the mammalian cortex, a typical neuron fires at an average rate of 1–10 Hz, meaning it is active less than 1% of the time. If we could build hardware that mirrors this sparsity, we would achieve orders-of-magnitude improvements in energy efficiency.

This lecture introduces the mathematical formalism of spiking neural networks (SNNs), their computational properties, and the challenges of implementing them in silicon.

---

## 2. The Leaky Integrate-and-Fire (LIF) Neuron

### 2.1 The Differential Equation

The simplest and most widely used spiking neuron model in neuromorphic engineering is the **Leaky Integrate-and-Fire (LIF)** neuron. Its membrane potential $V_m(t)$ evolves according to:

$$\tau_m \frac{dV_m}{dt} = -(V_m - V_{\text{rest}}) + R_m I_{\text{syn}}(t)$$

where:
- $\tau_m = R_m C_m$ is the membrane time constant
- $V_{\text{rest}}$ is the resting potential (typically $-65\text{mV}$)
- $R_m$ is the membrane resistance
- $I_{\text{syn}}(t)$ is the total synaptic input current

When $V_m$ crosses the threshold $V_{\text{th}}$:
1. A spike is emitted
2. $V_m$ is reset to $V_{\text{reset}}$ (typically $-65\text{mV}$ to $V_{\text{rest}}$)
3. The neuron enters an absolute refractory period $\tau_{\text{ref}}$ during which it cannot fire

### 2.2 Discrete-Time Approximation

For digital simulation and hardware implementation, we discretize the LIF dynamics. Using Euler's method with timestep $\Delta t$:

$$V_m[t+1] = \alpha V_m[t] + (1 - \alpha) \cdot \sum_i w_i s_i[t] + V_{\text{rest}}(1 - \alpha)$$

where $\alpha = e^{-\Delta t / \tau_m}$ is the decay factor and $s_i[t] \in \{0, 1\}$ are incoming spike signals. This is the formulation used in Lava and Norse, and it maps cleanly onto digital neuromorphic hardware.

If a spike occurs ($V_m[t+1] \geq V_{\text{th}}$), we set $V_m[t+1] = V_{\text{reset}}$ and the output spike signal $z[t+1] = 1$.

### 2.3 Parameter Choices

| Parameter | Biological Value | Digital Typical | Loihi 3 Range |
|-----------|-----------------|-----------------|----------------|
| $\tau_m$ | 10–30 ms | 10–100 timesteps | 1–2¹⁶ timesteps |
| $V_{\text{th}}$ | −55 to −50 mV | 1.0 (normalized) | 0–65535 (16-bit) |
| $\tau_{\text{ref}}$ | 1–5 ms | 1–5 timesteps | 0–31 timesteps |
| $V_{\text{rest}}$ | −65 mV | 0.0 (normalized) | Programmable |

On Loihi 3, synaptic weights are 8-bit integers in the range $[-256, +254]$, and membrane potentials use 16-bit fixed-point arithmetic. The Yggdrasil Chip extends this to 12-bit weights and 24-bit membrane potentials.

---

## 3. Spike Encoding Schemes

### 3.1 Rate Coding

The simplest encoding: information is carried by the *firing rate* of a neuron over a time window. A neuron firing at 50 Hz over a 100ms window carries the value "5 spikes" or equivalently "0.5 of maximum rate." Rate coding is robust to noise but slow — you need long integration windows to distinguish rates.

### 3.2 Temporal Coding

Information is carried by the *precise timing* of spikes. The first-spike latency code encodes intensity as the time of the first spike relative to a reference event: stronger stimuli produce earlier spikes. Temporal codes are fast (single-spike decisions) but fragile — they require precise timing that silicone implementations may not preserve.

### 3.3 Population Coding

A population of neurons encodes a value collectively. Each neuron has a preferred stimulus (tuning curve), and the stimulus is decoded from the *pattern of activation* across the population. This is how sensory cortex represents continuous variables — place cells, direction columns, etc.

### 3.4 Burst Coding

Bursts of spikes (short high-frequency sequences) carry different information than isolated spikes. In thalamocortical circuits, bursts signal "trust this input" while single spikes signal "sampling mode." The Yggdrasil Chip explicitly implements burst signaling as a conferencing primitive between neuronal populations.

---

## 4. Network Dynamics

### 4.1 Recurrent SNNs

SNNs become computationally interesting when recurrently connected. A recurrent spiking network with $N$ LIF neurons and synaptic weight matrix $W$ has dynamics:

$$V_m^j[t+1] = \alpha V_m^j[t] + (1-\alpha) \sum_i W_{ji} z_i[t] + V_{\text{rest}}(1-\alpha)$$

$$z_j[t+1] = \Theta(V_m^j[t+1] - V_{\text{th}})$$

where $\Theta$ is the Heaviside step function. These dynamics can implement:
- **Attractor networks**: stable firing patterns (memory)
- **Reservoir computing**: high-dimensional temporal projections (sequence processing)
- **Winner-take-all circuits**: competitive selection (decision making)

### 4.2 Inhibition and Balance

Biological circuits operate in a regime of *balanced excitation and inhibition* (E/I balance). In this regime, excitatory and inhibitory inputs roughly cancel, keeping $V_m$ near threshold but jittering — ready to fire at any moment. This regime maximizes sensitivity to inputs while maintaining stability.

In silicon, achieving E/I balance requires careful weight initialization and often adaptive inhibitory circuits. Loihi 3 implements per-core inhibitory neurons with programmable fanout, while Yggdrasil uses a distributed homeostatic mechanism that locally adjusts inhibitory weights.

### 4.3 Firing Rate Homeostasis

SNNs need mechanisms to maintain reasonable firing rates — too low and computation is slow, too high and energy efficiency vanishes. Homeostatic mechanisms include:
- **Intrinsic excitability adaptation**: slow changes to $V_{\text{th}}$
- **Synaptic scaling**: uniform multiplication of input weights
- **Spike-dependent threshold adaptation**: $V_{\text{th}}$ increases after each spike and decays back

---

## 5. From SNNs to Computation

### 5.1 Spiking Networks as Universal Approximators

Maass (1997) proved that spiking neurons with temporal coding are computationally more powerful than sigmoidal neurons of the same size — a spiking neuron with temporal coding can compute functions that require arbitrarily many sigmoidal neurons. In practice, however, the gap closes for rate-coded SNNs, which are approximately equivalent to ReLU networks when firing rates are interpreted as activations.

### 5.2 The ANN-to-SNN Conversion

The most practical approach to deploying SNNs today is **ANN-to-SNN conversion**:

1. Train an equivalent ANN (typically ReLU network)
2. Replace ReLU activations with LIF neuron firing rates
3. Normalize weights so that maximum firing rates match

The key insight: a ReLU unit with activation $a$ maps to an LIF neuron firing at rate $r \propto a$. With proper normalization, the conversion can achieve near-lossless accuracy on image classification tasks within 100–250 timesteps. Loihi 3 achieves >99% of the original ANN accuracy on ImageNet within 300 timesteps.

### 5.3 Native SNN Training

Training SNNs natively (without ANN conversion) remains challenging due to the non-differentiable spike function $\Theta$. We'll cover this extensively in Lecture 5, but the key approaches are:
- **Surrogate gradients**: replace $\Theta'$ with a smooth approximation during backpropagation
- **STDP-based local learning**: biologically inspired Hebbian plasticity
- **Hybrid methods**: surrogate gradients for the forward pass, local rules for weight updates

---

## 6. Implementation Frameworks

### 6.1 Lava (Intel Neuromorphic Labs)

Lava is the reference framework for programming Loihi 3 and Yggdrasil. It uses a process-based model:

```python
from lava.proc.lif.process import LIF
from lava.proc.dense.process import Dense

# Create a two-layer SNN
lif1 = LIF(shape=(256,),          # 256 neurons
           vth=1.0,                # threshold
           dv=0.1,                 # decay constant
           du=0.1)                 # input decay
dense = Dense(weights=np.random.randn(128, 256) * 0.01)
lif2 = LIF(shape=(128,), vth=1.0, dv=0.1, du=0.1)

lif1.out_ports.s_out.connect(dense.in_ports.s_in)
dense.out_ports.a_out.connect(lif2.in_ports.a_in)
```

### 6.2 Norse (PyTorch-Compatible)

Norse provides SNN layers that plug directly into PyTorch:

```python
import torch
import norse.torch as sn

model = torch.nn.Sequential(
    sn.LIFCell(),
    torch.nn.Linear(256, 128),
    sn.LIFCell(),
    torch.nn.Linear(128, 10),
)
```

### 6.3 Hardware Deployment

Deploying to Yggdrasil requires compilation through the Yggdrasil SDK, which maps Lava processes onto the chip's 16 neuromorphic cores, each hosting up to 8192 neurons and 64K synaptic connections.

---

## 7. Key Takeaways

1. **Spikes are events, not values.** This makes SNNs fundamentally different from ANNs and opens the door to event-driven hardware.
2. **The LIF neuron is the workhorse.** Simple enough to implement in silicon, expressive enough for universal computation.
3. **Rate coding is practical but limited.** Temporal and population codes exploit spike timing for richer representation.
4. **ANN-to-SNN conversion works well** for deploying existing models, but native training is needed for temporal tasks.
5. **E/I balance and homeostasis** are critical for stable, efficient SNN operation — both biological and artificial.

---

## Reading

- Maass, W. (1997). "Networks of Spiking Neurons: The Third Generation of Neural Network Models." *Neural Networks*, 10(9), 1659–1671.
- Neftci, E.O., et al. (2019). "Surrogate Gradient Learning in Spiking Neural Networks." *IEEE Signal Processing Magazine*, 36(6), 51–63.
- Boahen, K. (2017). "A Neuromorph's Prospectus." *Computing in Science & Engineering*, 19(2), 12–20.
- Davies, M., et al. (2021). "Loihi 2: Advancing Neuromorphic Computing with Asynchronous Message Passing." *IEEE Micro*, 41(5), 7–15.

---

*Next lecture: Memristive Devices — how we build synapses that remember.*
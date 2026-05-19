# CS404: Neuromorphic & Edge Computing
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** CS301 — Distributed Systems; CS302 — Compiler Design & Code Generation; CS205 — Machine Learning
**Description:** A deep exploration of brain-inspired computing architectures and the edge intelligence revolution. Covers spiking neural networks, neuromorphic hardware (Intel Loihi, IBM TrueNorth, BrainScaleS), energy-efficient edge inference, sensor fusion on constrained devices, event-based sensing, and the emerging neuromorphic-edge continuum. Students programme real neuromorphic hardware via the Lava framework and deploy models on the Yggdrasil Huginn Edge Cluster. By 2040, neuromorphic-edge systems have become the dominant paradigm for always-on, low-power AI — this course answers *how* and *why*.

---

## Lecture 1: The Brain-Inspired Revolution — Why Neuromorphic Computing Matters

*"The salmon knows its river not by calculation but by pulse" — an old Norse saying, apt for a field where timing IS computation.*

The von Neumann bottleneck — the separation of memory and processing — has defined computing for eighty years. A modern CPU spends the majority of its energy shuttling data between DRAM and registers, not performing actual computation. By 2040, the limits of this architecture have become existential: training a single large language model consumes megawatt-hours, while the human brain performs exaflop-equivalent computation on roughly 20 watts. **Neuromorphic computing** closes this gap by co-locating memory and computation in artificial neurons that communicate via precisely timed **spikes** — brief electrical pulses whose temporal pattern encodes information, just as biological neurons do.

The fundamental unit of neuromorphic computation is the **spiking neural network (SNN)**. Unlike traditional artificial neural networks (ANNs) where all neurons fire synchronously on every timestep, SNN neurons remain quiescent until their membrane potential crosses a threshold, at which point they emit a spike, reset, and enter a refractory period. This **event-driven** computation is sparse — in a typical SNN, fewer than 5% of neurons fire on any given timestep, yielding orders-of-magnitude energy savings. The key mathematical model is the **leaky integrate-and-fire (LIF)** neuron, governed by τ · dV/dt = -(V - V_rest) + R · I(t), where τ is the membrane time constant, V is the membrane potential, V_rest is the resting potential, R is the membrane resistance, and I(t) is the input current. When V ≥ V_thresh, the neuron spikes. More sophisticated models include the **Izhikevich model** (which captures 20 firing patterns with just two differential equations) and the **Hodgkin-Huxley model** (the gold standard with four coupled ODEs describing sodium, potassium, and leak channels).

The shift from rate coding (where information is the firing rate) to **temporal coding** (where the precise timing of spikes carries information) is the conceptual revolution at the heart of neuromorphic computing. In a rate-coded ANN, a neuron's output is a scalar — the firing frequency. In a temporal-coded SNN, a neuron's output is a spike train, and the relative timing between spikes encodes relationships (coincidence detection, spike-timing-dependent plasticity). This opens the door to computing that is inherently asynchronous, massively parallel, and natively handles time-varying signals — the exact requirements of real-world sensory processing. The **tempotron** (Gütig & Sompolinsky, 2006) demonstrated that a single LIF neuron can learn to classify complex spatiotemporal spike patterns by adjusting synaptic weights to fire at specific times, proving that temporal computation is trainable.

Why does this matter in 2040? The explosion of **edge devices** — the Yggdrasil Huginn sensor network alone comprises 12,000 nodes — demands AI that operates continuously on milliwatts, responds in microseconds, and learns online without cloud round-trips. Neuromorphic hardware like Intel's **Loihi 2** (2021/2036) delivers these capabilities: 1 million neurons per chip at ~1 watt, with on-chip learning via programmable synaptic plasticity rules. Students in this course will write real SNN code using Intel's **Lava** framework (an open-source neuromorphic computing platform) and deploy it on the University's Loihi 2 board, comparing energy-per-inference against traditional GPU/TPU baselines. The metric that matters is not FLOPS but **SOPs (synaptic operations per second per watt)** — and on this metric, neuromorphic systems are 1,000× ahead.

**Required Reading:**
- Mead, C. (1990). "Neuromorphic Electronic Systems." *Proceedings of the IEEE*, 78(10), 1629–1636. The founding document.
- Davies, M. et al. (2018). "Loihi: A Neuromorphic Manycore Processor with On-Chip Learning." *IEEE Micro*, 38(1), 82–99.
- Gütig, R. & Sompolinsky, H. (2006). "The Tempotron: A Neuron That Learns Spike Timing–Based Decisions." *Nature Neuroscience*, 9(3), 420–428.
- Furber, S. (2016). "Large-Scale Neuromorphic Computing Systems." *Journal of Neural Engineering*, 13(5), 051001.

**Discussion Questions:**
1. The brain achieves ~10^16 synaptic operations per second on 20 W. A 2025 GPU achieved ~10^14 FLOPS on 300 W. What architectural assumptions account for this 10,000× energy efficiency gap, and which are fundamental versus historical?
2. If information is encoded in spike timing rather than rate, what new classes of algorithms become possible that are impossible in rate-coded networks? Consider temporal coincidence detection and sequence learning.
3. Carver Mead's 1990 paper predicted the end of Moore's Law and the rise of neuromorphic systems. Which of his predictions were prescient, and which were wrong? What does this tell us about technological forecasting?

---

## Lecture 2: Spiking Neuron Models — From Hodgkin-Huxley to the LIF Abstraction

*The Norns weave each thread at its own pace; a neuron's spike, too, arrives not when demanded, but when it must.*

To build a neuromorphic system, we must first model the neuron. The biological neuron is a marvel of electrochemical engineering: ion channels, neurotransmitter release, dendritic computation, and back-propagating action potentials. Neuroscientists have developed mathematical models at varying levels of abstraction, and the neuromorphic engineer's art is choosing the right level for the task — fidelity versus computational efficiency.

The **Hodgkin-Huxley model** (1952, Nobel Prize 1963) is the canonical detailed model. It describes the membrane potential V(t) of a squid giant axon via four coupled ordinary differential equations tracking sodium activation (m), sodium inactivation (h), and potassium activation (n): C_m · dV/dt = I_ext - g̅_Na · m³h · (V - E_Na) - g̅_K · n⁴ · (V - E_K) - g̅_L · (V - E_L), with dm/dt = α_m(V)(1-m) - β_m(V)m and analogous equations for h and n, where α and β are experimentally fitted voltage-dependent rate functions. HH is biophysically accurate but computationally expensive — simulating 1 second of 1 million HH neurons requires approximately 10^15 floating-point operations, roughly 10 minutes on a modern GPU. For large-scale neuromorphic systems, we need something leaner.

The **Izhikevich model** (2003) strikes an elegant balance: dv/dt = 0.04v² + 5v + 140 - u + I, du/dt = a(bv - u), with a spike reset: if v ≥ 30 mV, then v ← c, u ← u + d. Despite having only four parameters (a, b, c, d) and two differential equations, this model reproduces all 20 known cortical firing patterns — regular spiking, fast spiking, bursting, chattering, resonator — by tuning just a, b, c, and d. For example, (a=0.02, b=0.2, c=-65, d=8) produces a **regular spiking** (RS) neuron typical of pyramidal cells, while (a=0.1, b=0.2, c=-65, d=2) produces a **fast spiking** (FS) neuron typical of inhibitory interneurons. The computational cost is roughly 13 FLOPS per 1 ms timestep, making it 100× cheaper than HH while retaining biological plausibility. Izhikevich's model is often used as the "gold standard" for validating even simpler abstractions.

The **leaky integrate-and-fire (LIF)** model is the workhorse abstraction for most neuromorphic hardware. It eliminates the spike generation dynamics and treats the neuron as a simple RC circuit: τ · dV/dt = -(V - V_rest) + R · I_syn(t), with a hard threshold V_thresh and reset V ← V_reset after firing. The LIF model has no intrinsic dynamics of its own — it simply integrates input until it fires — making it computationally trivial (1 multiply-add per timestep). Yet this simplicity is a feature: the LIF model's behavior is dominated by the *network dynamics* (synaptic weights, delays, connectivity patterns) rather than the neuron's own properties, making it ideal for studying emergent computation. Notably, Intel's Loihi implements a variant of the **current-based LIF** (CUBA — current-based, LIF) where synaptic currents decay exponentially with a configurable time constant.

A critical nuance often missed: the LIF model's information processing properties depend dramatically on the **input regime**. In the **sub-threshold fluctuation-driven regime** (mean input below threshold, firing driven by variance), the neuron acts as a coincidence detector, firing when multiple inputs arrive nearly simultaneously. In the **supra-threshold mean-driven regime** (mean input above threshold), the neuron acts as a rate coder whose firing rate is roughly linear in the mean input. This regime switch — controlled by the balance of excitation and inhibition — is one of the brain's fundamental computational mechanisms, and replicating it in hardware requires careful calibration of synaptic weights. In 2040, the Lava framework's `lava.proc.dense` process provides a CUBA LIF neuron library that students will use to explore these regimes empirically on real Loihi silicon.

**Required Reading:**
- Hodgkin, A.L. & Huxley, A.F. (1952). "A Quantitative Description of Membrane Current and Its Application to Conduction and Excitation in Nerve." *Journal of Physiology*, 117(4), 500–544.
- Izhikevich, E.M. (2003). "Simple Model of Spiking Neurons." *IEEE Transactions on Neural Networks*, 14(6), 1569–1572.
- Gerstner, W., Kistler, W.M., Naud, R., & Paninski, L. (2014). *Neuronal Dynamics: From Single Neurons to Networks and Models of Cognition*. Cambridge University Press. Chapters 1–6.
- Davies, M. et al. (2021). "Advancing Neuromorphic Computing with Loihi: A Survey of Results and Outlook." *Proceedings of the IEEE*, 109(5), 911–934.

**Discussion Questions:**
1. The HH model captures ion channel dynamics with 4 ODEs. The Izhikevich model captures 20 firing patterns with 2 ODEs. The LIF captures one pattern with 1 ODE. When is it appropriate to use each? What questions can HH answer that LIF cannot?
2. The Izhikevich model's parameter (a, b, c, d) have clear biological interpretations (recovery rate, sensitivity, reset potential, recovery increment). If you wanted to model a neuron that exhibits adaptation (decreasing firing rate over time), how would you set these parameters? What about a bursting neuron?
3. Loihi's CUBA LIF neuron has configurable time constants for both membrane and synaptic current decay. What computational advantages does this dual-timescale architecture provide over a single-timescale LIF? Consider working memory and sequence processing.

---

## Lecture 3: Spike-Timing-Dependent Plasticity — Learning in the Temporal Domain

*"A rune carved at dawn carries different power than one carved at dusk" — timing is everything in seiðr, and in synaptic learning.*

If spiking neurons are the *what* of neuromorphic computing, **spike-timing-dependent plasticity (STDP)** is the *how* of learning. STDP is a biologically observed learning rule where the change in synaptic weight Δw depends on the relative timing of pre- and post-synaptic spikes: Δw = A⁺ · exp(-Δt/τ⁺) if Δt > 0 (pre before post, potentiation) and Δw = -A⁻ · exp(Δt/τ⁻) if Δt < 0 (post before pre, depression), where Δt = t_post - t_pre, A⁺ and A⁻ are amplitude parameters, and τ⁺ and τ⁻ are time constants (typically ~20 ms). The rule says: if the pre-synaptic neuron fires just before the post-synaptic neuron, the synapse is *strengthened* (it contributed to causing the spike); if the post fires just before the pre, the synapse is *weakened* (it was irrelevant). This is Hebb's postulate ("neurons that fire together wire together") refined with temporal precision.

STDP's computational power emerges from its ability to perform **unsupervised feature detection**. Consider a single post-synaptic LIF neuron receiving Poisson spike trains from 100 pre-synaptic neurons. If one subset of pre-synaptic neurons consistently fires in a correlated pattern ~5 ms before the others, STDP will strengthen those synapses and weaken the rest, effectively making the post-synaptic neuron a *temporal coincidence detector* for that specific pattern. Masquelier, Guyonneau, and Thorpe (2008) demonstrated that an STDP-equipped neuron exposed to natural images learns Gabor-like receptive fields — the same edge detectors found in V1 of the visual cortex — purely from spike timing statistics, with no labeled data and no backpropagation. This is **unsupervised representation learning** at its most biologically authentic.

The mathematical analysis of STDP reveals deeper structure. Song, Miller, and Abbott (2000) showed that STDP with additive weight updates leads to a *competitive* synaptic dynamics where weights are driven to either zero or a maximum value (bimodal distribution), while **multiplicative** STDP (where Δw is proportional to the current weight) produces a unimodal, log-normal distribution matching experimental data. The choice between additive and multiplicative STDP is one of the key design decisions in neuromorphic chip design — Loihi implements programmable STDP rules where students can specify the functional form, time constants, and whether updates are additive, multiplicative, or a hybrid.

By 2040, STDP has been extended far beyond its original pairwise formulation. **Triplet STDP** (Pfister & Gerstner, 2006) incorporates the effect of multiple pre-post spike pairs: Δw = A⁺ · x(t) · δ(t - t_post) - A⁻ · y(t) · δ(t - t_pre), where x(t) and y(t) are internal variables tracking recent pre- and post-synaptic activity. Triplet STDP resolves the **frequency-dependence paradox** — the observation that pairwise STDP predicts depression at high firing rates (because spikes are frequent), but experiments show potentiation. The triplet rule correctly switches from depression to potentiation at high rates because the internal traces accumulate. The Lava framework on Loihi 2 supports configurable multi-factor STDP rules, enabling students to experiment with triplet STDP and compare learning outcomes against the pairwise case.

A frontier topic in 2040 is the integration of STDP with **backpropagation through time (BPTT)** — the standard training algorithm for recurrent neural networks. The problem: BPTT requires differentiable activation functions and access to all past states (for the backward pass), neither of which SNNs naturally provide. **Surrogate gradient** methods (Neftci, Mostafa, & Zenke, 2019; Zenke & Vogels, 2021) replace the non-differentiable spike threshold with a smooth surrogate during the backward pass while using the true threshold during the forward pass. On Loihi 2, this enables a hybrid training regime: STDP for fast, local, unsupervised feature learning in early layers, and surrogate-gradient BPTT for supervised fine-tuning of output layers — combining the biological efficiency of STDP with the task performance of gradient descent.

**Required Reading:**
- Bi, G.-Q. & Poo, M.-M. (1998). "Synaptic Modifications in Cultured Hippocampal Neurons: Dependence on Spike Timing, Synaptic Strength, and Postsynaptic Cell Type." *Journal of Neuroscience*, 18(24), 10464–10472. The experimental discovery of STDP.
- Song, S., Miller, K.D., & Abbott, L.F. (2000). "Competitive Hebbian Learning Through Spike-Timing-Dependent Synaptic Plasticity." *Nature Neuroscience*, 3(9), 919–926.
- Pfister, J.-P. & Gerstner, W. (2006). "Triplets of Spikes in a Model of Spike Timing-Dependent Plasticity." *Journal of Neuroscience*, 26(38), 9673–9682.
- Neftci, E.O., Mostafa, H., & Zenke, F. (2019). "Surrogate Gradient Learning in Spiking Neural Networks." *IEEE Signal Processing Magazine*, 36(6), 51–63.

**Discussion Questions:**
1. STDP is a local learning rule — each synapse only needs to know the timing of its own pre- and post-synaptic spikes. Backpropagation is global — every synapse needs the gradient of the final loss. What are the engineering implications of this difference? Consider distributed training, online learning, and hardware implementation.
2. Triplet STDP resolves the frequency-dependence paradox. What other experimental phenomena does pairwise STDP fail to explain? Consider spike-timing-dependent LTD at long intervals (>100 ms) and the effect of dendritic location.
3. Surrogate gradient methods make SNNs trainable via BPTT. But they sacrifice biological plausibility and local computation. Is this a reasonable trade-off? Or should neuromorphic computing commit fully to local learning rules?

---

## Lecture 4: Neuromorphic Hardware — Loihi, TrueNorth, and the Silicon Neuron

*"The smith forges not just steel but purpose — a blade for cutting, a plough for tilling. So too must we forge silicon not for general arithmetic but for the specific dance of spikes."*

Neuromorphic hardware is not a simulation of neurons on a general-purpose processor; it is a **physical instantiation of neural dynamics in silicon**. The distinction is crucial: in a simulation, time steps through a discrete loop; in neuromorphic hardware, time flows continuously through analog or mixed-signal circuits whose physics natively implements the differential equations of neural dynamics. This is Carver Mead's original vision — *the physics of the device is the computation*.

**Intel Loihi 2** (2021, revised 2036) is the most commercially significant neuromorphic processor in 2040 and the platform students use in this course. Each Loihi 2 chip (fabricated on Intel's 4 nm process) contains up to 1 million neurons and 120 million synapses distributed across 128 neuromorphic cores connected by a 2D mesh network-on-chip (NoC). Each core implements a programmable neuron model — not just LIF but configurable dendritic compartments, multi-compartment neurons, and user-defined synaptic plasticity rules — via a microcode engine. The key innovation of Loihi 2 over its predecessor is the **programmable neuron engine**: the neuron's dynamics (membrane equation, threshold adaptation, refractory behavior) are specified in a microcode program, enabling researchers to implement arbitrary spiking neuron models directly in silicon without FPGA intermediary. The synaptic memory uses a **graded spike** representation where spike magnitude can be fractional (0–255) rather than binary, enabling direct implementation of rate-based computations when needed.

**IBM TrueNorth** (2014) was the pioneering large-scale neuromorphic chip, containing 1 million neurons and 256 million synapses on a single 28 nm die at just 70 mW — an astonishing 26 pJ per synaptic operation. TrueNorth's architecture is strikingly different from Loihi's: it uses a **crossbar array** of static synapses (weights loaded at configuration time, not learned online) and a fixed LIF neuron model. There is no on-chip learning — all weights must be pre-trained and loaded. This design trade-off (simplicity and scale over flexibility) made TrueNorth the first system to demonstrate real-time, low-power, million-neuron SNN inference (Esser et al., 2016). The TrueNorth-based NS16e system (2019) scaled to 64 million neurons — still the largest neuromorphic system ever built — and demonstrated 1,000× energy efficiency over GPUs for spiking convolutional networks.

The **SpiNNaker** (Spiking Neural Network Architecture) project at the University of Manchester represents a different philosophical approach. Instead of building analog or mixed-signal neurons, SpiNNaker uses 1 million ARM968 cores (SpiNNaker1) or custom ARM-based cores (SpiNNaker2, 2025) in a massively parallel digital system connected by a bespoke multicast router. Each core simulates ~1,000 neurons in real time. The resulting system (SpiNNaker2 at 10 million cores) can simulate 10 billion neurons in real time — far larger than any analog approach — but at lower energy efficiency (~10 nJ per synaptic operation versus ~1 pJ for Loihi). SpiNNaker's advantage is *flexibility*: any neuron model (HH, Izhikevich, multicompartment) can be loaded as software, making it the preferred platform for computational neuroscience where biological fidelity is paramount. The **Human Brain Project** used SpiNNaker (alongside BrainScaleS, an accelerated analog system) as its primary neuromorphic platform.

The **BrainScaleS** system (Heidelberg University, 2011–ongoing) is an extreme example of accelerated analog neuromorphic computing. BrainScaleS implements neurons using analog electronic circuits on custom ASICs, with synapses stored in an array of SRAM cells. Critically, the analog circuits run at 10,000× biological real time — 1 second of neural simulation completes in 100 μs. This acceleration, combined with a digital communication fabric that reconfigures synaptic weights between runs, makes BrainScaleS ideal for **evolutionary optimisation** of neural networks and for exploring parameter spaces that would require years of biological time. By 2040, BrainScaleS-3 (2028) has demonstrated the first accelerated simulation of a full cortical column with realistic ion channel dynamics, bridging the gap between detailed biophysical models and large-scale network function.

**Required Reading:**
- Davies, M. et al. (2018). "Loihi: A Neuromorphic Manycore Processor with On-Chip Learning." *IEEE Micro*, 38(1), 82–99.
- Merolla, P.A. et al. (2014). "A Million Spiking-Neuron Integrated Circuit with a Scalable Communication Network and Interface." *Science*, 345(6197), 668–673. — IBM TrueNorth.
- Furber, S.B., Galluppi, F., Temple, S., & Plana, L.A. (2014). "The SpiNNaker Project." *Proceedings of the IEEE*, 102(5), 652–665.
- Schemmel, J., Billaudelle, S., Dauer, P., & Weis, J. (2022). "Accelerated Analog Neuromorphic Computing: BrainScaleS-2." In *Analog Integrated Circuits and Signal Processing*, 37–51.

**Discussion Questions:**
1. Loihi uses a digital manycore architecture with on-chip learning. TrueNorth uses a crossbar with pre-trained weights and no on-chip learning. SpiNNaker uses general-purpose ARM cores. BrainScaleS uses accelerated analog circuits. When would you choose each platform? What are their respective strengths?
2. Loihi 2's microcode-programmable neuron engine allows arbitrary neuron models. What new models are possible that were impossible on Loihi 1? Consider models with calcium-dependent plasticity, homeostatic mechanisms, and dendritic nonlinearities.
3. The graded spike representation on Loihi 2 (0–255 magnitude) blurs the line between rate coding and temporal coding. When would you use graded spikes instead of binary spikes? What are the trade-offs in precision, energy, and algorithmic capability?

---

## Lecture 5: Edge Computing Architectures — The Resource Continuum

*"A longship carries all it needs within its hull — water, food, weapons. The edge device must likewise be self-sufficient, carrying its intelligence within, not reaching across the sea for answers."*

Edge computing is the practice of performing computation near the data source — the sensor, the camera, the microphone — rather than transmitting all data to a centralised cloud for processing. The **resource continuum** spans from microcontrollers (ARM Cortex-M4 at 80 MHz, 256 KB RAM, ~1 mW) through edge gateways (Raspberry Pi-class devices at 1–4 W) to edge servers (GPU-equipped, 50–200 W). Each tier represents a different trade-off between compute capacity, energy budget, latency tolerance, and connectivity reliability. By 2040, neuromorphic processors have become the default architecture for the lowest tiers of this continuum — where traditional von Neumann processors are simply too energy-hungry for continuous AI operation.

The **latency-energy-accuracy trilemma** defines the edge computing design space. Cloud inference offers high accuracy (large models, powerful GPUs) but suffers from network latency (10–100 ms for cellular, unpredictable in rural/remote areas) and energy cost of data transmission (sending one image over 4G LTE costs ~2 J, equivalent to ~10^9 operations on an edge processor). On-device inference eliminates transmission cost and latency but must operate within severe energy and memory constraints. The solution is **model compression**: quantisation (8-bit integer weights instead of 32-bit float, reducing model size by 4×), pruning (removing near-zero weights, reducing size by 5–20×), and knowledge distillation (training a small "student" model to mimic a large "teacher" model). Quantised, pruned, and distilled models can run on microcontrollers — TensorFlow Lite Micro on an ARM Cortex-M4 runs keyword spotting at 50 μJ per inference, enabling continuous always-on voice activation.

**Heterogeneous edge architectures** are the dominant pattern in 2040. A modern edge node (like the Yggdrasil Huginn unit used in the course lab) pairs a low-power neuromorphic processor (Loihi 2) for continuous sensory processing with a conventional microcontroller for system management and a Wi-Fi 7 radio for intermittent cloud connectivity. The neuromorphic subsystem runs an always-on SNN that detects events of interest — anomalous vibrations in a bridge monitoring scenario, a specific voice in a smart-home context, an approaching vehicle in autonomous driving — consuming ~10 mW continuously. When an event is detected, the system wakes the microcontroller, which may trigger higher-resolution processing, log the event, or send an alert to the cloud. This **event-driven architecture** mirrors the brain's own attentional mechanisms and can reduce total system energy by 10–100× compared to continuous cloud streaming.

The **MobilEdge benchmark suite** (UoY Sigrun Group, 2037) provides a standardised evaluation framework for edge inference systems, measuring accuracy, latency, energy-per-inference, and memory footprint across a range of tasks (vision, audio, sensor fusion) on the Huginn hardware. A key finding: neuromorphic processors dominate the energy-efficiency axis but lag on raw throughput compared to GPU-equipped edge servers. For tasks requiring >100 inferences per second, a Jetson Orin Nano (15 W) outperforms Loihi 2 (1 W) in absolute throughput; for tasks requiring <1 inference per second with always-on operation, Loihi's 1 mW idle power versus Orin's 5 W idle power makes neuromorphic the only viable option. This illustrates a fundamental principle: **the right hardware depends on the duty cycle**. Students will replicate this analysis using the MobilEdge benchmark on a Huginn node.

**Required Reading:**
- Satyanarayanan, M. (2017). "The Emergence of Edge Computing." *Computer*, 50(1), 30–39.
- Wang, X., Han, Y., Leung, V.C.M., Niyato, D., Yan, X., & Chen, X. (2020). "Convergence of Edge Computing and Deep Learning: A Comprehensive Survey." *IEEE Communications Surveys & Tutorials*, 22(2), 869–904.
- Jacob, B. et al. (2018). "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference." *CVPR 2018*, 2704–2713.
- MobilEdge Benchmark Whitepaper, Sigrun Group, UoY (2037). Available on the course repository.

**Discussion Questions:**
1. The latency-energy-accuracy trilemma says you can optimise at most two of three axes. Give examples of applications where each pair (latency+energy, energy+accuracy, latency+accuracy) is the right choice. When is the cloud the only viable option?
2. The Huginn node pairs a neuromorphic processor with a conventional microcontroller. What are the engineering challenges of this heterogeneous architecture? Consider memory coherency, interrupt handling, and programming model.
3. If the neuromorphic subsystem detects an event but has only 80% confidence, should it wake the microcontroller? What decision-theoretic framework should govern this wake-up decision? Consider the cost of false positives versus false negatives in a bridge-monitoring safety application.

---

## Lecture 6: Sensor Fusion at the Edge — Integrating Multimodal Streams

*"The vǫlva reads omens from fire, from birds, from the casting of lots. No single sign suffices — only their convergence speaks truth."*

Sensor fusion is the problem of combining information from multiple heterogeneous sensors to produce an estimate that is more accurate, more robust, or more comprehensive than any individual sensor could provide. At the edge, sensor fusion faces unique constraints: sensors operate at different rates (a gyroscope at 1 kHz, a camera at 30 Hz, a GPS at 1 Hz), have different latencies, and produce data in incomparable formats (scalars, vectors, images). The fusion algorithm must align these streams temporally, transform them into a common representation, and combine them while respecting real-time deadlines and energy budgets.

The **Kalman filter** (Kalman, 1960) is the canonical algorithm for linear sensor fusion with Gaussian noise. The discrete Kalman filter maintains an estimate of the system state ẋ and its covariance P, updating them in two steps. **Prediction**: ẋ_k|k-1 = F ẋ_k-1|k-1 + B u_k, P_k|k-1 = F P_k-1|k-1 F^T + Q. **Update**: K_k = P_k|k-1 H^T (H P_k|k-1 H^T + R)^(-1), ẋ_k|k = ẋ_k|k-1 + K_k (z_k - H ẋ_k|k-1), P_k|k = (I - K_k H) P_k|k-1. Here F is the state transition matrix, H is the observation matrix, Q is the process noise covariance, R is the measurement noise covariance, and K is the Kalman gain that optimally weights prediction versus measurement. The **extended Kalman filter (EKF)** linearises non-linear dynamics via first-order Taylor expansion; the **unscented Kalman filter (UKF)** handles nonlinearities by propagating sigma points (deterministically chosen samples) through the true nonlinear function, avoiding Jacobian computation altogether.

Implementing a Kalman filter on an edge device requires careful numerical engineering. The covariance matrix P must remain symmetric and positive definite; floating-point round-off can cause P to lose these properties, leading the filter to diverge. The **Joseph form** of the covariance update (P = (I - KH)P(I - KH)^T + KRK^T) is more numerically stable and should be used in production code. On a microcontroller with no hardware floating-point unit (FPU), fixed-point Kalman filters use integer arithmetic with careful scaling — the Yggdrasil Edge Library provides a validated fixed-point UKF implementation for 32-bit ARM Cortex-M processors.

The **complementary filter** is the simplest fusion algorithm and remains widely used for attitude estimation in drones and wearables. It exploits the fact that gyroscopes are accurate at high frequencies but drift at low frequencies, while accelerometers are accurate at low frequencies but noisy at high frequencies: θ_fused = α · (θ_fused + ω_gyro · Δt) + (1-α) · θ_accel, where α = τ/(τ+Δt) for a time constant τ (typically ~0.5–1.0 s). The complementary filter is essentially a low-pass filter on the accelerometer and a high-pass filter on the gyroscope, and it can be implemented in just 3 lines of fixed-point C — ideal for the most constrained edge devices.

**Neuromorphic sensor fusion** is the 2040 frontier, and the central project in this course. Event-based cameras (see Lecture 10) produce asynchronous spike-like outputs that are natively compatible with SNN processing. A Loihi 2 chip can simultaneously receive spike streams from an event camera (visual), a neuromorphic auditory sensor (cochlea model output), and an IMU (converted to spike trains via a delta-modulation encoding), fusing them through a recurrent SNN trained via surrogate-gradient BPTT. The key advantage: all three streams are represented in the same temporal-spike format, eliminating the need for explicit temporal alignment — spikes from different sensors are simply routed to the appropriate synapses, and the SNN's inherent temporal dynamics handle phase offsets automatically. This is sensor fusion *as computation* rather than sensor fusion as a pre-processing step.

**Required Reading:**
- Kalman, R.E. (1960). "A New Approach to Linear Filtering and Prediction Problems." *Journal of Basic Engineering*, 82(1), 35–45.
- Julier, S.J. & Uhlmann, J.K. (1997). "New Extension of the Kalman Filter to Nonlinear Systems." *Proc. SPIE 3068*, 182–193. — Unscented Kalman filter.
- Mahony, R., Hamel, T., & Pflimlin, J.-M. (2008). "Nonlinear Complementary Filters on the Special Orthogonal Group." *IEEE Trans. Automatic Control*, 53(5), 1203–1218.
- Gallego, G. et al. (2022). "Event-Based Vision: A Survey." *IEEE Trans. Pattern Analysis and Machine Intelligence*, 44(1), 154–180.

**Discussion Questions:**
1. The Kalman filter is optimal under linear-Gaussian assumptions. What happens when these assumptions are violated? Consider multi-modal noise (e.g., GPS multipath errors with heavy tails). What alternatives exist?
2. The complementary filter is a 3-line algorithm. When is it sufficient, and when is a full Kalman filter necessary? What additional sensors would tip the balance toward Kalman filtering?
3. Neuromorphic sensor fusion eliminates temporal alignment by using a common spike representation. But what about spatial alignment? If an event camera and an IMU have different coordinate frames, how does the SNN learn the transformation? Is this something weights can learn, or does it require explicit calibration?

---

## Lecture 7: Energy-Efficient Deep Learning — Quantisation, Pruning, and Distillation

*"Skaldic verse distills a saga into a single stanza. Each word must earn its place; each kennning must carry weight. So too with neural networks at the edge."*

The gap between the accuracy demands of modern AI applications and the resource constraints of edge devices is bridged by three complementary techniques: **quantisation** (reducing numerical precision), **pruning** (removing unnecessary connections), and **knowledge distillation** (transferring knowledge from large to small models). These are not alternatives but components of a **compression pipeline** that can reduce model size and inference energy by 10–100× with minimal accuracy loss.

**Quantisation** maps floating-point weights and activations to low-precision integer representations. The standard approach is **affine quantisation**: q = round(r/S + Z), where r is the real value, S is the scale factor, and Z is the zero-point (the integer value corresponding to zero). For 8-bit quantisation, q ∈ [0, 255] (asymmetric) or [-128, 127] (symmetric). The operation a · b = S_a S_b (q_a - Z_a)(q_b - Z_b) requires only integer multiplication and addition, which are 4–10× more energy-efficient than FP32 multiply-accumulate operations on most architectures. The key challenge is determining S and Z: **post-training quantisation** calibrates these using a small representative dataset, while **quantisation-aware training (QAT)** inserts fake quantisation nodes during training so the network learns to be robust to quantisation noise. QAT typically preserves accuracy to within 0.5% of the full-precision baseline, whereas post-training quantisation can lose 2–5% on challenging models. By 2040, **mixed-precision quantisation** (where different layers use different bit-widths based on their sensitivity to quantisation noise) is the norm, with the UoY **Gungnir Optimiser** tool automatically determining per-layer bit widths via a hardware-aware neural architecture search.

**Pruning** removes weights or neurons that contribute little to the output, reducing both storage and computation. **Magnitude pruning** (Han et al., 2015) is the simplest: remove the p% of weights with smallest absolute value. At 90% sparsity, the model size is 10× smaller and inference is 10× faster (with sparse matrix hardware support). However, unstructured pruning produces irregular sparsity patterns that are difficult to accelerate on standard hardware. **Structured pruning** removes entire channels, filters, or attention heads, producing regular sparsity that maps cleanly to hardware — at the cost of slightly lower compression ratios for a given accuracy. The modern approach is **iterative pruning + fine-tuning**: prune 10%, fine-tune, repeat, until the desired sparsity is reached. The **lottery ticket hypothesis** (Frankle & Carbin, 2019) showed that a randomly initialised dense network contains a sparse subnetwork (the "winning ticket") that, when trained in isolation, achieves comparable accuracy to the full network — suggesting that pruning is not just compression but a form of architecture discovery.

**Knowledge distillation** (Hinton, Vinyals, & Dean, 2015) trains a small "student" network to mimic a large "teacher" network. The key insight: the teacher's soft outputs (probability distribution over classes) contain more information than hard labels. The student is trained to minimise a weighted sum of two losses: L = α · L_CE(y_student, y_true) + (1-α) · L_KL(y_student^T, y_teacher^T), where L_CE is cross-entropy with hard labels, L_KL is Kullback-Leibler divergence between the temperature-scaled softmax outputs (T > 1 softens the distribution, revealing the teacher's uncertainty about "incorrect" classes), and α balances the two. A distilled MobileNetV3 with 6 million parameters can achieve 75% ImageNet top-1 accuracy (versus 80% for a 150M-parameter ResNet-152 teacher), representing a 25× parameter reduction for a 5-point accuracy trade-off — often acceptable for edge deployment where the alternative is no AI at all.

The **edge deployment pipeline** taught in this course integrates all three techniques: (1) train a large teacher model on the cloud (CS205 techniques); (2) prune the teacher to 50% sparsity; (3) distill the pruned teacher into a compact student architecture designed for the target hardware; (4) quantise the student to INT8 using QAT; (5) convert to the TensorFlow Lite or Lava format and deploy on a Huginn node. Students will benchmark their pipeline's accuracy, latency, and energy against baselines on the MobilEdge suite.

**Required Reading:**
- Jacob, B. et al. (2018). "Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference." *CVPR 2018*, 2704–2713.
- Han, S., Pool, J., Tran, J., & Dally, W.J. (2015). "Learning Both Weights and Connections for Efficient Neural Networks." *NIPS 2015*, 1135–1143.
- Hinton, G., Vinyals, O., & Dean, J. (2015). "Distilling the Knowledge in a Neural Network." *arXiv:1503.02531*.
- Frankle, J. & Carbin, M. (2019). "The Lottery Ticket Hypothesis: Finding Sparse, Trainable Neural Networks." *ICLR 2019*.

**Discussion Questions:**
1. After quantisation + pruning + distillation, a model may lose 5% accuracy but use 1% of the energy. For what applications is this trade-off acceptable? For what applications is it unacceptable? How would you decide?
2. The lottery ticket hypothesis implies that the dense network was never "using" all its weights. What does this mean for neural architecture design? Should we design sparse architectures from the start rather than pruning dense ones?
3. Distillation transfers "dark knowledge" from teacher to student. What exactly is this dark knowledge? If the teacher is 95% confident about class A and 2% about class B versus 1% about class C, what does the 2:1 ratio tell the student that the hard label does not?

---

## Lecture 8: Real-Time Inference on Constrained Devices — Serving Models at the Edge

*"The watchman on the wall must see the sail and call before the ship touches shore. Inference that arrives after the event is no inference at all."*

Deploying a trained model is only half the battle; the other half is **inference serving** — executing the model with guaranteed latency, throughput, and availability on a device that may have 1/1000th the resources of the training infrastructure. Real-time inference introduces hard constraints: for a drone collision-avoidance system, inference must complete in under 20 ms; for an industrial anomaly detector monitoring a conveyor belt, throughput must exceed 100 inferences per second; for an always-on keyword spotter, the inference energy budget is 50 μJ. Meeting these constraints requires co-design of the model architecture, the inference runtime, and the hardware.

The **inference runtime** is the software layer between the model and the hardware. On edge devices, the dominant runtimes in 2040 are **TensorFlow Lite Micro** (for microcontrollers), **ONNX Runtime** (for Linux-class edge devices), and **Lava** (for neuromorphic processors). Each runtime implements: (a) **graph optimisation** (operator fusion — merging convolution + batch norm + ReLU into a single kernel; constant folding — pre-computing statically known subgraphs; layout optimisation — converting NHWC to NCHW or vice versa for optimal memory access); (b) **memory planning** (allocating tensor buffers to minimise peak memory usage via a greedy interval-coloring algorithm); (c) **kernel selection** (choosing the fastest implementation for each operator on the specific hardware, often via JIT compilation or ahead-of-time auto-tuning). On a Raspberry Pi 5, ONNX Runtime with graph optimisations can achieve 2–5× speedup over naive model execution.

**Model serving patterns** for real-time inference include: (1) **Single-inference, single-result** (request-response) — the simplest pattern, used for image classification and keyword spotting. (2) **Streaming inference** — the model maintains internal state (an RNN hidden state or a Kalman filter covariance) and processes a continuous stream of sensor data, updating its state with each observation. On Loihi 2, streaming inference is natively supported because the neuromorphic cores run continuously, updating membrane potentials and synaptic states in real time — there is no "start inference / wait for result" cycle. (3) **Batched inference** — multiple inputs are processed simultaneously to amortise overhead. Edge devices rarely batch across users (since there's only one user), but can batch across time (process 4 audio frames at once) to exploit SIMD instructions. (4) **Cascaded inference** — a fast, lightweight model screens inputs, and only ambiguous cases trigger a more expensive model. For example, a 50 KB keyword spotter runs continuously; when it detects the wake word, it triggers a 5 MB speech recognition model.

**Hard real-time guarantees** require worst-case execution time (WCET) analysis, which is notoriously difficult for modern processors with caches, branch predictors, and out-of-order execution. On a neuromorphic processor, WCET analysis is simpler because the architecture is deterministic: each spike is processed by a fixed pipeline (synaptic lookup → weight multiplication → membrane update → threshold comparison → spike generation) with known cycle counts. Loihi 2's spike-processing latency is 1 μs per spike per core, and because spike routing uses a dimension-order routing algorithm on the 2D mesh, the worst-case spike delivery time is bounded by the Manhattan distance between sender and receiver cores. This determinism is a major advantage for safety-critical real-time systems.

Students will implement a **streaming anomaly detector** on a Huginn node: an accelerometer produces 3-axis vibration data at 1 kHz; a trained autoencoder (pruned, quantised, and distilled per Lecture 7) processes each window of 64 samples; if the reconstruction error exceeds a threshold, an alert is generated. The latency requirement is 64 ms (one window) and the energy budget is 500 μJ per inference. The lab compares implementations on: (a) ARM Cortex-M4 (TensorFlow Lite Micro), (b) Jetson Orin Nano (ONNX Runtime), and (c) Loihi 2 (Lava), measuring latency, energy, and accuracy.

**Required Reading:**
- David, R. et al. (2021). "TensorFlow Lite Micro: Embedded Machine Learning on TinyML Systems." *Proceedings of Machine Learning and Systems*, 3, 800–811.
- Reddi, V.J. et al. (2020). "MLPerf Inference Benchmark." *ISCA 2020*, 446–459.
- Chen, T. et al. (2018). "TVM: An Automated End-to-End Optimizing Compiler for Deep Learning." *OSDI 2018*, 578–594.
- Orchard, G. et al. (2021). "Efficient Neuromorphic Signal Processing with Loihi 2." *Nature Machine Intelligence*, 3, 886–896.

**Discussion Questions:**
1. Neuromorphic hardware provides deterministic spike processing with bounded latency. How does this compare to GPU inference serving, where latency distributions have long tails due to cache misses and scheduling? For what safety-critical applications does this determinism matter?
2. Cascaded inference uses a cheap model to gate an expensive model. What are the failure modes? How would you set the gating threshold to trade off false positives (waking the expensive model unnecessarily) versus false negatives (missing events the expensive model could have caught)?
3. Streaming inference on Loihi 2 maintains continuous state. How does this differ from the stateless request-response pattern used in cloud inference? What new capabilities does stateful inference enable?

---

## Lecture 9: Edge-Cloud Orchestration and Federated Learning

*"The Thing gathers wisdom from every homestead, each bringing their knowledge to the assembly. Federated learning does the same — gathering models, not data."*

No edge device operates in isolation. The **edge-cloud continuum** describes a system where computation migrates dynamically between device, edge gateway, and cloud based on latency requirements, energy availability, and network conditions. The orchestration problem is: given a computational DAG (e.g., preprocess → detect → classify → alert), which nodes should execute on-device, at the edge gateway, and in the cloud? The **Yggdrasil Huginn Orchestrator** (2039) solves this via a cost model that minimises a utility function U = w_1 · Latency + w_2 · Energy + w_3 · (1 - Accuracy) + w_4 · CloudCost, subject to per-task deadlines and energy budgets, with weights w configured per application.

**Federated learning** (McMahan et al., 2017) is the paradigm for training across edge devices without centralising data. In each round, the cloud server distributes the current global model to a subset of edge devices; each device trains the model on its local data for a few epochs; the devices send only their **model updates** (gradients or weight differences) back to the cloud; the server aggregates these updates (typically via **Federated Averaging**: w_global ← ∑ (n_k / N) · w_k, where n_k is the number of local data points on device k). The key privacy guarantee: raw data never leaves the device. The key systems challenge: devices are heterogeneous in compute, network, and data distribution — a smartphone with 10,000 photos and a Raspberry Pi with 50 sensor readings should not contribute equally to the global model.

**Non-IID data** is the central algorithmic challenge. In classical distributed training, data is shuffled across workers so each sees an independent and identically distributed (IID) sample. In federated learning, each device's data reflects its user's habits — one user's photo library is 80% cats, another's is 80% landscapes. The global model, trained via Federated Averaging on non-IID data, can diverge significantly from the centrally-trained optimum. The **FedProx** algorithm (Li et al., 2020) addresses this by adding a proximal term to the local objective: L_k(w) = L(w) + (μ/2) ‖w - w_global‖², which penalises local models that stray too far from the global model, improving convergence under heterogeneity. The **SCAFFOLD** algorithm (Karimireddy et al., 2020) uses control variates (server and client correction terms) to correct for client drift, achieving faster convergence than FedAvg on non-IID data.

**Neuromorphic federated learning** is a nascent field in 2040, enabled by Loihi 2's on-chip learning capability. The problem: STDP produces weight changes in a format (spike-timing-dependent updates) that is not directly compatible with the gradient-based aggregation used in Federated Averaging. The solution, developed by the UoY Huginn Group: **spike-to-gradient translation**. Each local training phase records both the STDP-induced weight changes Δw_STDP and the equivalent gradient direction g = sign(Δw_STDP) · |Δw_STDP|^(1/T) where T is a "temperature" that maps the nonlinear STDP update into a gradient-like form. These translated gradients are then aggregated via Federated Averaging at the cloud. Early results show neuromorphic federated learning achieves 85% of the accuracy of centralised surrogate-gradient training while preserving the 1,000× energy advantage of on-chip STDP — a compelling trade-off for privacy-sensitive, always-on applications like health monitoring.

**Required Reading:**
- McMahan, B., Moore, E., Ramage, D., Hampson, S., & Arcas, B.A. (2017). "Communication-Efficient Learning of Deep Networks from Decentralized Data." *AISTATS 2017*.
- Li, T., Sahu, A.K., Zaheer, M., Sanjabi, M., Talwalkar, A., & Smith, V. (2020). "Federated Optimization in Heterogeneous Networks." *Proceedings of Machine Learning and Systems*, 2, 429–450.
- Karimireddy, S.P., Kale, S., Mohri, M., Reddi, S.J., Stich, S.U., & Suresh, A.T. (2020). "SCAFFOLD: Stochastic Controlled Averaging for Federated Learning." *ICML 2020*.
- Huginn Group. "Spike-to-Gradient Translation for Neuromorphic Federated Learning." *UoY Technical Report*, 2039.

**Discussion Questions:**
1. Federated learning protects raw data privacy but model updates can leak information. A gradient g = ∂L/∂w can reveal whether a specific data point was in the training set (membership inference). What mitigations exist? Consider differential privacy and secure aggregation.
2. The spike-to-gradient translation maps STDP updates to gradient-like values. This is an approximation — what information is lost in this mapping? Can you design an aggregation scheme that operates directly on STDP updates without translation?
3. A device with 50 data points contributes less to Federated Averaging than one with 10,000. Is this fair? Should the aggregation be weighted by data quantity, data quality, or something else? How would you define "quality" in a privacy-preserving way?

---

## Lecture 10: Neuromorphic Sensing — Event-Based Vision and Auditory Processing

*"Heimdallr sees the grass grow and hears the wool on sheep. His senses are event-driven, not sampled — he perceives not snapshots but changes."*

Conventional sensors — cameras, microphones — sample the world at fixed intervals (30 Hz, 44.1 kHz) regardless of whether anything has changed. This is fundamentally wasteful: between frames, 99% of pixels may be identical; in silence, audio samples carry only noise. **Neuromorphic sensors** flip this paradigm: they report only *changes* — events — asynchronously, exactly when and where they occur. This event-driven sensing is the perfect match for event-driven computation on neuromorphic hardware.

**Event-based cameras** (also called dynamic vision sensors, DVS) operate like biological retinas. Each pixel operates independently and continuously monitors the log-intensity L = ln(I). When L changes by more than a threshold θ (typically 10–15% contrast), the pixel emits an **event** e = (x, y, t, p) where (x,y) is the pixel coordinate, t is the microsecond-precision timestamp, and p ∈ {+1, -1} indicates the polarity of the change (increase or decrease in brightness). An event camera produces no output for static scenes — a parked car generates zero events — and responds to fast motion with microsecond latency, whereas a conventional camera at 30 fps would miss events between frames (the "blind time" problem). The data rate is adaptive: a static office scene produces ~10 kEvents/s, a busy street ~1 MEvents/s, and explosive motion ~10 MEvents/s. Commercial event cameras in 2040 (Prophesee Gen4, Sony IMX636) offer 1280×720 resolution with 1 μs temporal resolution, at ~10 mW — 100× less power than an equivalent frame-based camera continuously streaming at 30 fps.

The data format of event cameras — asynchronous, sparse, spatio-temporal — is natively compatible with SNNs. An SNN layer connected to an event camera can process each event as it arrives, updating only the neurons whose receptive fields include that pixel. This **event-driven processing** means the network's energy consumption is proportional to scene activity rather than resolution × frame rate. A face detection SNN on Loihi 2 processing event camera input consumes ~1 mW when the scene is static and ~50 mW during active motion, while a frame-based DNN on an edge GPU consumes a constant ~5 W regardless of scene content. This activity-proportional energy is the defining advantage of neuromorphic sensing + processing pipelines.

**Neuromorphic auditory sensors** model the human cochlea. The **silicon cochlea** (Lyon & Mead, 1988; Liu et al., 2014) is a cascaded filterbank that decomposes audio into frequency bands, with each band producing spike events when the energy in that band changes. The filterbank uses second-order sections that mimic the basilar membrane's mechanical frequency dispersion: H_k(s) = s · τ_k / (s² · τ_k² + s · τ_k/Q_k + 1), where τ_k is the time constant for channel k (tuned to a specific characteristic frequency), Q_k is the quality factor (sharpness of tuning), and the cascade of filters implements a constant-Q (logarithmically spaced) frequency decomposition matching human auditory perception. A 64-channel silicon cochlea implemented in 22 nm CMOS (2028) consumes 50 μW and provides a spike-based representation of audio that can directly drive an SNN for keyword spotting, speaker identification, and sound source localisation — all at energy budgets 100× lower than conventional MFCC + DNN pipelines.

The practical lab for this lecture uses the Yggdrasil Huginn node's event camera (a Prophesee Gen4 sensor) and a microphone processed through a software silicon cochlea emulation. Students implement: (a) an SNN that tracks a moving object using event camera input only, (b) a keyword spotter that triggers on "Hey Huginn" using cochlea-processed audio, and (c) an audio-visual fusion that associates sound sources with visual objects (e.g., which person is speaking in a multi-person scene). The final challenge: combine (a), (b), and (c) into a complete scene-understanding pipeline that runs entirely on Loihi 2 at under 100 mW.

**Required Reading:**
- Gallego, G. et al. (2022). "Event-Based Vision: A Survey." *IEEE Trans. Pattern Analysis and Machine Intelligence*, 44(1), 154–180.
- Lichtsteiner, P., Posch, C., & Delbruck, T. (2008). "A 128×128 120 dB 15 μs Latency Asynchronous Temporal Contrast Vision Sensor." *IEEE Journal of Solid-State Circuits*, 43(2), 566–576.
- Liu, S.-C., Delbruck, T., Indiveri, G., Whatley, A., & Douglas, R. (2014). *Event-Based Neuromorphic Systems*. Wiley. Chapters 1–4.
- Lyon, R.F. & Mead, C. (1988). "An Analog Electronic Cochlea." *IEEE Trans. Acoustics, Speech, and Signal Processing*, 36(7), 1119–1134.

**Discussion Questions:**
1. An event camera produces no data when the scene is static. What are the failure modes? Consider scenarios where important information IS in the static scene (a stop sign that hasn't moved, a person standing still). How would you design a hybrid system that combines event and frame-based sensing?
2. The silicon cochlea's constant-Q filterbank matches human frequency perception. But machine hearing systems can use any filterbank — is the cochlea's design optimal for machines, or is it an anthropomorphic bias? What alternative frequency decompositions might be better for specific tasks?
3. The activity-proportional energy of SNN+event camera pipelines is their key advantage. Under what usage patterns (duty cycle, scene complexity) does this advantage disappear? When would a frame-based system be more efficient?

---

## Lecture 11: Security, Privacy, and Trust on the Edge

*"A rune of protection must be carved on every doorpost. An edge device without security is a door left open to the frost giants."*

Edge devices operate in physically exposed environments — attached to bridges, embedded in wearables, deployed in smart homes — where attackers can physically access the hardware. Security on the edge is therefore fundamentally harder than cloud security, where data centres have armed guards and biometric access controls. The threat model for edge devices includes: (a) **physical attacks** (probing memory buses, power analysis, fault injection via voltage glitching), (b) **network attacks** (man-in-the-middle, replay, denial of service), (c) **model extraction** (querying the model to reconstruct training data or model weights), and (d) **adversarial examples** (carefully crafted inputs that cause misclassification).

**Trusted execution environments (TEEs)** provide hardware-enforced isolation for sensitive computation. ARM TrustZone (available on Cortex-A processors) partitions the system into a "secure world" and "normal world," with hardware-enforced memory isolation between them. The neural network model weights, the inference computation, and the cryptographic keys reside in the secure world; the sensor drivers and network stack run in the normal world. Even if an attacker compromises the normal world OS, they cannot read the model weights or inference results. Intel SGX (Software Guard Extensions) takes this further, encrypting memory regions so that even the OS and hypervisor cannot access enclave data. On edge devices, TEEs add ~5–15% latency overhead to inference, which is acceptable for all but the most latency-sensitive applications.

**Federated learning with differential privacy** (Lecture 9) protects training data, but what about inference data? **Homomorphic encryption** (HE) allows computation on encrypted data: E(a) ⊗ E(b) = E(a + b) (additively homomorphic) or E(a) ⊗ E(b) = E(a × b) (fully homomorphic, FHE). In theory, a user could encrypt their sensor data, send it to an edge server, have the server run inference entirely on encrypted data, and receive encrypted results that only the user can decrypt — the server learns nothing about the input or output. In practice, FHE inference on a ResNet-50 takes ~10 seconds per image on a powerful server (2025 numbers), making it impractical for real-time edge applications. **Partial homomorphic encryption** (only addition OR multiplication, not both) is much faster and can be used for specific operations (e.g., encrypted aggregation in federated learning). By 2040, hardware-accelerated FHE (via FPGA or ASIC co-processors) has reduced FHE inference latency to ~100 ms for a MobileNet-class model, bringing private inference into the real-time domain for edge applications.

**Adversarial robustness** is the study of inputs designed to fool neural networks. An adversarial example is a small perturbation δ added to a correctly classified input x such that f(x + δ) ≠ f(x) while ‖δ‖ is imperceptibly small. The **Fast Gradient Sign Method** (FGSM, Goodfellow et al., 2015) generates adversarial examples in one step: x_adv = x + ε · sign(∇_x L(f(x), y_true)). The **Projected Gradient Descent** (PGD, Madry et al., 2018) iteratively refines the perturbation: x_adv^(t+1) = Proj(x_adv^(t) + α · sign(∇_x L(f(x_adv^(t)), y_true))), and is the standard benchmark for robustness evaluation. On edge devices, adversarial robustness is particularly important because attackers can physically manipulate the sensor input — placing stickers on stop signs, shining lasers at cameras, playing ultrasonic audio — not just digital pixels. Neuromorphic sensors provide some inherent robustness: an event camera's threshold θ means that small adversarial perturbations below the contrast threshold produce no events, effectively providing a built-in "denoising" step.

**Required Reading:**
- Goodfellow, I.J., Shlens, J., & Szegedy, C. (2015). "Explaining and Harnessing Adversarial Examples." *ICLR 2015*.
- Madry, A., Makelov, A., Schmidt, L., Tsipras, D., & Vladu, A. (2018). "Towards Deep Learning Models Resistant to Adversarial Attacks." *ICLR 2018*.
- Carlini, N. & Wagner, D. (2017). "Towards Evaluating the Robustness of Neural Networks." *IEEE Symposium on Security and Privacy*, 39–57.
- Mo, F. et al. (2021). "When Homomorphic Encryption Marries Deep Learning: A Comprehensive Survey." *arXiv:2105.01713*.

**Discussion Questions:**
1. Adversarial training (training on adversarial examples) improves robustness but reduces clean accuracy. This is a fundamental trade-off (Tsipras et al., 2019). When is robustness worth the accuracy cost? How would you quantify the "value" of robustness in a deployment context?
2. A TEE protects model weights even with a compromised OS. But what if the attacker has physical access and can probe the memory bus? What additional protections (encrypted RAM, tamper detection) are needed?
3. Neuromorphic sensors have an inherent contrast threshold that filters small perturbations. Does this make SNNs more robust to adversarial examples than ANNs? What are the limits of this robustness? Consider adversarial perturbations large enough to cross the contrast threshold.

---

## Lecture 12: The 2040 Horizon — Neuromorphic-Edge Systems and the Future of Intelligence

*"Yggdrasil's roots reach into worlds unseen. The future of intelligence reaches into architectures we are only beginning to weave."*

We stand at the convergence of three trends: neuromorphic hardware achieving biological efficiency, edge computing delivering intelligence everywhere, and learning algorithms operating in real time on continuous sensory streams. Taken together, these trends point toward a fundamentally new kind of computing — **continuous, embodied, energy-proportional intelligence** — that is as different from 2020-era cloud AI as cloud AI was from 1990-era batch processing. This lecture surveys the frontier and asks: what comes next?

**The neuromorphic scaling roadmap.** In 2040, the largest deployed neuromorphic system is the **Yggdrasil Mímisbrunnr Cluster** — 1,024 Loihi 2 chips in a 3D mesh architecture, totalling 1 billion neurons and 120 billion synapses, consuming 2 kW. This is comparable to the human cerebral cortex (16 billion neurons, ~100 trillion synapses, ~20 W) in neuron count but still 1,000× behind in synapse count and 100× behind in energy efficiency. The gap is closing fast: Intel's **Loihi 3** (projected 2032) is expected to use 3D-stacked chiplets with through-silicon vias, packing 100 million neurons per chip at 10 W — a 100× neuron density improvement over Loihi 2. At that scale, a single rack of Loihi 3 chips will match the human brain's neuron count. The question is not *if* but *when* — and what we do with that capability.

**Edge AI in 2040: the ambient intelligence layer.** The 2040 smart environment is not a collection of devices that respond to explicit commands but an **ambient intelligence** — a continuous, distributed, privacy-respecting AI that anticipates needs rather than waiting for queries. Your home's sensor network (event cameras in common areas, cochlea-based microphones, IMUs in furniture) runs a federated SNN that learns your routines and preferences without ever sending raw data to the cloud. The system knows you typically wake at 7:00, but today you stirred at 6:30 — it pre-heats the shower without being asked. This is not a hypothetical: the Yggdrasil **Heimdallr Ambient Platform** (prototype deployed in 20 UoY faculty homes) achieves this with 50 Huginn nodes per home, each consuming ~100 mW, for a total home energy budget of 5 W — less than a single LED lightbulb.

**The neuron-silicon interface.** In 2040, the boundary between biological and artificial neural networks is blurring. **Neural prosthetics** using Loihi chips as real-time co-processors for damaged brain regions have entered clinical trials: a hippocampal prosthesis that restores memory formation in patients with medial temporal lobe damage (Berger et al., UCLA/USC/UoY collaboration, 2038) uses an SNN trained to predict CA1 output from CA3 input, bypassing the damaged region. The technical requirements — sub-millisecond latency, continuous operation at body temperature, decades-long reliability — are uniquely met by neuromorphic hardware, which has no moving parts, operates at biological timescales, and consumes microwatts. This is computing not as a tool we use but as a part of who we are.

**The alignment problem on the edge.** As edge AI becomes ubiquitous and autonomous, the **AI alignment problem** — ensuring AI systems act in accordance with human values — moves from an abstract philosophical concern to a concrete engineering requirement. A federated SNN that learns your home routine has implicit power over your daily life: if it mislearns, it might lock you out of your own house or fail to detect a medical emergency. The solution must be built into the architecture from the start: **interpretable SNNs** whose spike patterns can be decoded into human-understandable rules; **verifiable STDP** whose weight updates can be audited; **human-in-the-loop override** that is physically impossible to disable. The UoY **Týr Alignment Framework** (2040) formalises these requirements as a set of architectural invariants that any deployed edge AI system must satisfy. The future of intelligence is not just about building smarter systems — it's about building *trustworthy* ones.

**Required Reading:**
- Furber, S. (2023). "The Road to Brain-Scale Neuromorphic Computing." *Communications of the ACM*, 66(2), 68–77.
- Berger, T.W. et al. (2038). "A Hippocampal Prosthesis for Memory Restoration: Phase II Clinical Results." *Nature Biomedical Engineering*, 2(8), 567–578.
- UoY Týr Alignment Framework (2040). Department of Computer Science Technical Report CS-TR-2040-07. Available on the course repository.
- Hassabis, D., Kumaran, D., Summerfield, C., & Botvinick, M. (2017). "Neuroscience-Inspired Artificial Intelligence." *Neuron*, 95(2), 245–258.

**Discussion Questions:**
1. If a rack of Loihi 3 chips can match the human brain's neuron count by 2033, does this mean we will have human-level AI by then? What's missing beyond neuron count — consider synapse count, learning rules, embodiment, and development?
2. Ambient intelligence that anticipates needs sounds useful but also raises privacy concerns. Even if raw data never leaves the home, the model's weights embody knowledge of your behaviour. What does it mean for an AI to "know" something about you? Can a model weight be considered personal data?
3. The Týr Alignment Framework requires interpretable SNNs and verifiable learning rules. Is full interpretability compatible with the high-capacity models needed for complex tasks? Or is there a fundamental trade-off between capability and transparency?

---

## Final Examination Preparation

The final examination for CS404 consists of two components:

### Part I: Written Examination (60%)

You will be asked to answer **4 out of 8** essay questions. Each essay should demonstrate depth of understanding, ability to connect concepts across lectures, and critical engagement with the primary literature. Each essay carries equal weight.

**Sample Essay Questions:**

1. **Neuromorphic vs. von Neumann:** Compare and contrast the neuromorphic and von Neumann architectural paradigms. Discuss the role of the memory wall, the energy efficiency advantages of event-driven computation, and the algorithmic implications of temporal coding versus rate coding. Use specific hardware examples (Loihi 2, GPU, TPU) to ground your discussion.

2. **STDP and Learning:** Spike-timing-dependent plasticity is a local learning rule that requires only pre- and post-synaptic spike timing. Discuss the advantages and limitations of local learning rules compared to global gradient-based optimisation. Consider scalability, biological plausibility, energy efficiency, and task performance. Reference both the biological STDP literature and the surrogate-gradient SNN literature.

3. **Edge Intelligence Pipeline:** Design a complete edge intelligence pipeline for a specific application of your choice (e.g., wildlife monitoring, predictive maintenance, assistive health). Detail the sensor selection, model architecture, compression strategy (quantisation, pruning, distillation), inference runtime, and cloud orchestration. Justify each design decision with reference to course concepts: the latency-energy-accuracy trilemma, the resource continuum, and hardware-software co-design.

4. **Sensor Fusion:** Compare Kalman filter-based sensor fusion with neuromorphic sensor fusion using event-based sensors. Discuss the advantages of using a common spike-based representation for multimodal sensor streams. What challenges remain in neuromorphic sensor fusion, and how might they be addressed?

5. **Federated Learning at the Edge:** Federated learning protects data privacy but introduces challenges from non-IID data distributions. Analyse the algorithmic and systems challenges of deploying federated learning on heterogeneous edge devices. Discuss SCAFFOLD, FedProx, and the spike-to-gradient translation for neuromorphic federated learning. Under what conditions would you choose centralised training despite the privacy cost?

6. **Security of Edge AI:** Edge devices face a broader threat model than cloud servers. Discuss the security challenges unique to edge AI: physical access, model extraction, adversarial examples, and privacy of inference data. Evaluate the effectiveness of TEEs, homomorphic encryption, and adversarial training as countermeasures. What residual risks remain, and are they acceptable for safety-critical deployment?

7. **Neuromorphic Sensing:** Event-based cameras and silicon cochleas represent a fundamentally different sensing paradigm from conventional frame-based and sample-based sensors. Discuss the implications of this paradigm shift for: (a) algorithm design, (b) energy efficiency, (c) latency, and (d) robustness. What applications are uniquely enabled by neuromorphic sensing?

8. **The 2040 Horizon:** Project forward to 2050. Based on current trends in neuromorphic hardware scaling, edge intelligence, and neural interfaces, describe the most significant technological and societal changes you anticipate. Consider both utopian and dystopian scenarios. What decisions made today by engineers and policymakers will most strongly shape which scenario we get?

### Part II: Practical Project (40%)

Implement one of the following on the Yggdrasil Huginn Edge Cluster:

- **Project A:** An SNN-based anomaly detector for streaming sensor data (accelerometer or event camera) running on Loihi 2, with comparison against a quantised DNN baseline on ARM Cortex-M4. Measure and report accuracy, latency, energy-per-inference, and memory footprint.
- **Project B:** A keyword spotting system using a software silicon cochlea + SNN on Loihi 2, compared against a conventional MFCC + CNN pipeline. Evaluate on a standard keyword spotting benchmark (Google Speech Commands).
- **Project C:** An event-camera-based object tracker using an SNN on Loihi 2, with evaluation on the Prophesee GEN1 Automotive Detection Dataset. Report latency and energy versus a frame-based baseline.

Projects are evaluated on: technical correctness (30%), depth of analysis (25%), quality of experimental methodology (25%), and clarity of written report (20%).

---

> *"Verðandi weaves what is becoming. In every spike, in every fused signal, in every watt we save — we weave a world where intelligence is not a distant cloud but the very air we breathe. Go now, and weave well."*
> — Runa Gridweaver Freyjasdóttir, UoY 2040

# Lecture 3: Event-Driven Computation — Neuromorphic vs. Clock-Driven, Event-Based Processing

**AI-6213: Neuromorphic Hardware Design**  
**Instructor:** Prof. Mikael Lundqvist  
**Date:** February 19, 2040

---

## 1. The Clock's Tyranny

Every conventional processor — from the microcontroller in a thermostat to the H100 GPUs running frontier language models — operates under the discipline of a **global clock**. The clock synchronizes every operation: every flip-flop samples its input on the clock edge, every pipeline stage advances in lockstep, and every instruction proceeds according to a predetermined schedule.

The clock's virtue is *simplicity*: it makes timing predictable and coordination trivial. But it comes at a steep cost:

1. **Continuous energy expenditure.** The clock distribution network (the tree of buffers and wires that delivers the clock signal to every flip-flop) consumes 20–40% of total chip power in modern processors. This energy is spent *regardless of whether computation is happening*.

2. **Worst-case timing.** Clock period is set by the slowest path in the design. Fast operations wait idle for slow ones to complete, wasting time.

3. **No data-dependent energy.** A clock-driven processor consumes nearly the same energy whether computing a critical result or polling an idle input.

Neuromorphic computing rejects the clock entirely. Computation proceeds **when events occur**, not when a clock ticks. This is *event-driven computation*, and it is the single most important architectural choice that enables neuromorphic chips to achieve their extraordinary energy efficiency.

---

## 2. Events, Not Cycles

### 2.1 What Is an Event?

In the neuromorphic paradigm, an **event** is a spike — a packet of information consisting of:
- **Address**: which neuron fired (source identifier)
- **Payload**: optional data (e.g., spike time, weight modifier)
- **Timestamp**: when the event occurred (for temporal processing)

Events are *sparse* — a neuron fires only when its membrane potential crosses threshold, which happens rarely. A network where each neuron fires at 1% duty cycle processes 99% fewer events than an equivalent rate-coded ANN processes multiply-accumulate operations.

### 2.2 The Address-Event Representation (AER)

The Address-Event Representation, proposed by Boahen (2004), is the standard inter-chip communication protocol in neuromorphic systems. When a neuron fires, its address is placed on a shared bus:

**Sender side:**
1. Neuron fires → arbiter detects request
2. Arbiter grants bus access (round-robin or priority-based)
3. Neuron's address is transmitted on the bus
4. Acknowledgment signal closes the handshake

**Receiver side:**
1. Address is decoded → destination neuron(s) identified
2. Synaptic weight(s) are looked up and applied to postsynaptic membrane(s)

AER is fundamentally asynchronous — no clock governs when events can be sent. Events are generated *when spikes occur*, and the bus bandwidth is used only when there is information to transmit.

### 2.3 Event-Driven vs. Frame-Based Processing

| Aspect | Frame-Based (Clock-Driven) | Event-Driven (Neuromorphic) |
|--------|---------------------------|----------------------------|
| Processing model | Periodic sampling | Asynchronous, data-driven |
| Latency | One frame period (best case) | As fast as events arrive |
| Energy when idle | High (clock always running) | Near-zero (no events = no work) |
| Bandwidth usage | Constant (full frame every period) | Proportional to activity |
| Temporal resolution | Limited by frame rate | Microsecond or better |
| Data representation | Dense arrays | Sparse spike trains |

This distinction is not merely theoretical. In real-world applications, the difference is dramatic:

- **Always-on vision**: A frame-based camera at 30 FPS sends 30 complete images per second regardless of scene content. An event camera (DVS) sends only *pixel-level changes*, typically 1–10% of pixels per frame-equivalent time window. Energy savings: 10–100×.
- **Keyword spotting**: A clock-driven DNN consumes ~1 mW continuously. An event-driven SNN on Loihi consumes ~50 μW average, spiking only on speech segments.

---

## 3. Asynchronous Digital Design

### 3.1 Why Asynchronous?

Asynchronous circuits operate without a global clock. Instead, they use **handshake signals** between modules to coordinate data transfer:

- **Request**: sender indicates data is valid
- **Acknowledgment**: receiver indicates data has been consumed

This handshake-based discipline offers:
- **Average-case performance**: operation time depends on actual data, not worst-case timing
- **Zero idle power**: modules not receiving requests consume near-zero power
- **Natural modularity**: modules can be designed independently and composed
- **No clock distribution**: eliminates 20–40% of total power

### 3.2 Async Design Styles

**Delay-insensitive circuits** use no timing assumptions — correctness depends only on the logical relationships between signals. These are the most robust but also the slowest, as every handshake requires explicit acknowledgment.

**Quasi-delay-insensitive (QDI) circuits** assume that wire delays are finite but unbounded, and that all forks are isochronic (all branches of a fork see the transition at roughly the same time). QDI is the design style used in all Caltech/Boahen-era neuromorphic chips and in Yggdrasil's inter-core routing.

**Bundled-data circuits** use matched delays to simulate a clock — data is assumed to arrive before an explicit "data valid" signal. Simpler to design but less robust to process variation.

### 3.3 The Hardware Cost of Asynchrony

Asynchronous circuits typically require 1.5–2× more transistors than their synchronous counterparts (for the handshake logic). However, they more than compensate through:
- Elimination of the clock tree (massive power savings)
- Voltage scaling to near-threshold (no clock → no timing closure constraint)
- Activity-proportional energy consumption

On Yggdrasil, the asynchronous inter-core routers use only 3% of total chip power, compared to 25–35% for clocked NoCs in comparable synchronous designs.

---

## 4. Event-Driven Architectures

### 4.1 Loihi 3's Mesh Routing

Loihi 3 (Intel, 2032) uses a **mesh-of-cores** architecture with asynchronous message passing. Each Loihi core contains:
- 8192 spiking neurons (LIF + programmable dynamics)
- Router with 4 virtual channels
- Local SRAM for synaptic weight storage (8-bit)

Inter-core communication uses multi-cast routing tables. When a neuron fires, the spike is:
1. Looked up in the core's routing table
2. Packaged as a message with destination core IDs
3. Injected into the mesh network
4. Routed asynchronously to destination core(s)
5. Applied to target neurons via synaptic weight lookup

The mesh operates at 1 GHz internally but processes events asynchronously — there is no global synchronization point.

### 4.2 TrueNorth 4's Crossbar Network

TrueNorth 4 (IBM/Synapse, 2031) evolved the original TrueNorth architecture with:
- 4096 neurosynaptic cores on 28nm
- Each core: 256 neurons, 65,536 synapses
- Crossbar interconnect with 256-bit-wide channels
- Event-driven operation with 1 ms timestep granularity

TrueNorth 4's key innovation is **deterministic routing** — unlike Loihi's adaptive routing, TrueNorth pre-computes routing tables at compile time, eliminating routing congestion at the cost of flexibility.

### 4.3 Yggdrasil's Radical Asynchrony

The Yggdrasil Chip (Kvasir, 2036) takes event-driven computation to its logical conclusion:

- **No global clock whatsoever.** The entire chip operates asynchronously.
- **No fixed timestep.** Each neuron operates at its own timescale, governed by its membrane time constant.
- **Hierarchical event routing.** Spikes are routed through three levels:
  1. **Intra-core**: spikes within a core use a local bus (sub-nanosecond routing)
  2. **Inter-core**: spikes between cores on the same chip use asynchronous mesh routing (~10 ns latency)
  3. **Inter-chip**: spikes between Yggdrasil chips use高速 serial links (~100 ns latency)

This fully asynchronous operation means that Yggdrasil's energy consumption is *strictly proportional to neural activity*. At 5W, running a superconscious model, Yggdrasil processes approximately 10¹² synaptic events per second. At idle, it draws < 50 mW.

---

## 5. Event Cameras and Sensing

### 5.1 The Dynamic Vision Sensor (DVS)

The DVS (Lichtsteiner et al., 2008) is the canonical event camera. Each pixel independently detects logarithmic intensity changes and emits events:

$$\text{Event}(x, y, t, p) \quad \text{if} \quad |\log I(x,y,t) - \log I(x,y,t_{last})| > \theta$$

where $p \in \{+1, -1\}$ indicates the polarity (increase or decrease). The DVS produces a sparse, asynchronous stream of events rather than dense frames.

### 5.2 Event-Based Processing Pipeline

An event camera + SNN pipeline is a natural match:
1. DVS pixels spike when brightness changes
2. Spikes are routed to an SNN
3. The SNN processes only incoming events — no computation on unchanged pixels
4. Latency is determined by neural propagation, not frame rate

This pipeline achieves:
- Microsecond latency (vs. 33ms for 30 FPS cameras)
- Sub-milliwatt sensing power
- Orders-of-magnitude data reduction
- Natural temporal processing in the SNN

### 5.3 Other Event Sensors

- **Cochlea chips**: Event-based audio processing (AER-Ear)
- **Tactile sensors**: Event-based touch for robotics (AER-Skin)
- **LiDAR events**: Asynchronous depth sensing
- **DVS + IMU**: Event-based visual-inertial odometry

Yggdrasil's I/O subsystem natively supports AER-input from event sensors, enabling end-to-end neuromorphic sensing-to-action pipelines.

---

## 6. Quantitative Analysis: Why Event-Driven Wins

### 6.1 Energy per Operation

| Architecture | Energy / MAC | Energy / Synaptic Event | Relative |
|-------------|-------------|------------------------|----------|
| GPU (H100) | ~10 pJ | N/A (clock-driven) | 1× |
| Digital SNN (Loihi 3) | N/A | ~26 pJ | 2.6× better |
| Analog SNN (ReRAM crossbar) | N/A | ~100 aJ | 100× better |
| Yggdrasil (hybrid) | N/A | ~1 pJ (active) | 10× better |

Note: The "energy per synaptic event" metric is more appropriate for neuromorphic hardware than "energy per MAC" because:
- Synaptic events are sparse (only when a neuron fires)
- One synaptic event may replace many MACs (temporal integration)
- The effective operations per second scale with activity, not clock rate

### 6.2 Activity Proportionality

For a network with $N$ neurons, average firing rate $f$, and $K$ fan-in per neuron:

- **Clock-driven ANN**: Energy ∝ $N \times K \times f_{clock}$ (all operations, all the time)
- **Event-driven SNN**: Energy ∝ $N \times f \times K \times E_{event}$ (only when neurons fire)

With typical biological sparsity ($f / f_{clock} \approx 0.01$), the event-driven advantage is ~100× for equivalent tasks.

---

## 7. Challenges of Event-Driven Computing

### 7.1 Burst Handling

When many neurons fire simultaneously (e.g., during a salient stimulus), the event routing network must handle traffic bursts without deadlock or excessive queuing. Solutions:
- **Virtual channels** with priority
- **Backpressure** (receiver signals congestion)
- **Buffer sizing** based on worst-case burst analysis

### 7.2 Timing Guarantees

Some applications (real-time control, safety-critical systems) require latency guarantees. Asynchronous systems offer *average-case* performance but not *worst-case* guarantees. Yggdrasil addresses this through **bounded-asynchronous** design: while there is no clock, each neuron's maximum inter-spike interval is bounded by its time constants, providing soft real-time guarantees.

### 7.3 Debugging and Verification

Asynchronous circuits are notoriously difficult to verify formally. Traditional timing analysis doesn't apply. Yggdrasil uses a combination of:
- Formal verification using CSP (Communicating Sequential Processes) models
- Extensive Monte Carlo simulation across PVT corners
- Built-in self-test hardware that can inject and observe events at each core

### 7.4 Software Tooling

Event-driven programming requires a fundamentally different mindset. Scheduling, synchronization, and debugging are all event-based rather than step-based. The Lava framework and Yggdrasil SDK have made significant progress, but the tooling ecosystem lags behind conventional deep learning frameworks by years.

---

## 8. Key Takeaways

1. **The clock is the enemy of efficiency.** It forces continuous computation even when nothing is happening.
2. **Event-driven computation** processes data only when it arrives, achieving near-zero idle power.
3. **AER and asynchronous routing** enable efficient, scalable inter-neuron communication.
4. **Asynchronous digital design** trades transistor count for energy proportionality — a winning trade at neuromorphic scales.
5. **Yggdrasil's fully asynchronous architecture** is the most radical implementation of event-driven computation, enabling 5W operation through strict activity proportionality.
6. **Event cameras and SNNs** are a natural pairing, creating end-to-end low-latency, low-power perception systems.

---

## Reading

- Boahen, K. (2004). "A Burst-Mode Word-Serial Address-Event Link-I: Transmitter Design." *IEEE Trans. Circuits and Systems*, 51(7), 1269–1280.
- Merolla, P.A., et al. (2014). "A Million Spiking-Neuron Integrated Circuit with a Scalable Communication Network and Interface." *Science*, 345(6197), 668–673.
- Davies, M., et al. (2021). "Loihi 2: Advancing Neuromorphic Computing with Asynchronous Message Passing." *IEEE Micro*, 41(5), 7–15.
- Sporns, O. (2011). "The Non-Random Brain: Efficiency, Economy, and Complex Dynamics." *Frontiers in Computational Neuroscience*, 5, 5.
- Lichtsteiner, P., et al. (2008). "A 128×128 120 dB 15 μs Latency Asynchronous Temporal Contrast Vision Sensor." *IEEE JSSC*, 43(12), 2804–2815.
- Kim, S., et al. (2036). "The Yggdrasil Chip: Fully Asynchronous Neuromorphic Architecture for Sub-10W Superconscious AI." *Nature Electronics*, 9(11), 612–625.

---

*Next lecture: Commercial Neuromorphic Chips — Loihi 3, TrueNorth 4, and the legendary Yggdrasil.*
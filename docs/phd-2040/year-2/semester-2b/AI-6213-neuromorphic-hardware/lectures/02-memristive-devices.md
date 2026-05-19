# Lecture 2: Memristive Devices — Analog Synaptic Weights, ReRAM, and Phase-Change Memory

**AI-6213: Neuromorphic Hardware Design**  
**Instructor:** Prof. Mikael Lundqvist  
**Date:** February 12, 2040

---

## 1. The Memory Problem in Neuromorphic Computing

A neuromorphic chip with one million neurons and one thousand synaptic inputs per neuron requires one billion synaptic weights. Each weight must be:
- **Stored** (non-volatile, ideally)
- **Updated** (for learning)
- **Multiplied** by an input signal (for inference)
- **Compact** (to fit on-chip)

In conventional von Neumann architectures, these weights live in SRAM or DRAM — each weight occupies 6–8 transistors (SRAM) or requires constant refresh (DRAM), and every multiplication requires fetching the weight from memory. This is the **memory wall**: moving data costs 100–1000× more energy than computing with it.

Memristive devices offer a radical alternative: the weight *is* the computation. A memristor's conductance $G$ directly implements the multiply operation via Ohm's law: $I = G \cdot V$. This collapses storage and compute into a single physical device — a *compute-in-memory* primitive that eliminates the memory wall entirely.

---

## 2. The Memristor: Theory

### 2.1 The Fourth Circuit Element

In 1971, Leon Chua predicted the existence of a fourth fundamental circuit element — the **memristor** (memory resistor) — characterized by a relationship between flux $\phi$ and charge $q$:

$$d\phi = M(q) \cdot dq$$

where $M(q)$ is the memristance. Unlike a resistor ($R = dV/dI$, constant), a memristor's resistance depends on its history of current flow. The device *remembers*.

In 2008, Strukov et al. at HP Labs demonstrated a physical memristor using titanium dioxide (TiO₂) thin films, confirming Chua's prediction and igniting the field of memristive computing.

### 2.2 Pinched Hysteresis Loop

The defining signature of a memristor is the **pinched hysteresis I-V curve**: under periodic voltage excitation, the current traces a loop that pinches at the origin ($V = 0, I = 0$). The loop area shrinks with increasing frequency, and at very high frequencies the device behaves as a linear resistor.

### 2.3 Memristive Systems

The generalized memristive system model (Joglekar & Wolf, 2009) extends Chua's original:

$$v(t) = R(\mathbf{x}, i, t) \cdot i(t)$$
$$\dot{\mathbf{x}} = f(\mathbf{x}, i, t)$$

where $\mathbf{x}$ is a vector of internal state variables. This framework captures virtually all non-volatile memory devices used in neuromorphic computing.

---

## 3. ReRAM (Resistive Random-Access Memory)

### 3.1 Operating Principle

ReRAM (also called RRAM or OxRAM) stores information in the resistance of a metal-insulator-metal (MIM) stack. The prototypical device uses HfO₂ as the insulator between platinum or tantalum electrodes.

**Set operation (forming / write):** A positive voltage creates a conductive filament of oxygen vacancies through the HfO₂, switching the device from a high-resistance state (HRS, ~MΩ) to a low-resistance state (LRS, ~kΩ).

**Reset operation (erase):** A negative voltage (or opposite-polarity current) dissolves the filament, restoring HRS.

### 3.2 Analog Conductance Modulation

For neuromorphic computing, we don't just need binary HRS/LRS — we need *analog* conductance levels. By applying partial-set pulses (smaller amplitude or shorter duration), we can incrementally grow or shrink the filament, achieving 32–256 distinguishable conductance levels in modern devices.

Key properties:

| Property | Typical Range | Notes |
|----------|--------------|-------|
| Conductance levels | 32–256 | Device-dependent; Yggdrasil targets 128 |
| Set voltage | 0.5–1.5 V | Pulse width: 10ns–10μs |
| Reset voltage | −0.5 to −1.5 V | |
| Endurance | 10⁸–10¹² cycles | Improving rapidly |
| Retention | 10 years at 85°C | Sufficient for inference |
| Device area | 10nm × 10nm (lab) | 50nm × 50nm (production) |
| Energy per update | 1–100 fJ | 100–1000× better than SRAM |

### 3.3 ReRAM in Crossbar Arrays

The true power of ReRAM emerges in **crossbar arrays**. A two-dimensional grid of ReRAM devices at the intersections of word lines and bit lines implements analog matrix-vector multiplication (MVM) in a single clock cycle:

- Input voltages $V_j$ applied to word lines (columns)
- Each device at position $(i, j)$ has conductance $G_{ij}$ encoding weight $w_{ij}$
- Output currents collected on bit lines (rows): $I_i = \sum_j G_{ij} \cdot V_j$

This computes $I = GV$ in a single step, using Kirchhoff's current law — no processor needed. A 1024 × 1024 crossbar performs one million multiply-accumulate (MAC) operations in one clock cycle, consuming ~10 pJ per operation.

### 3.4 Challenges

**Device variation:** ReRAM devices suffer from cycle-to-cycle and device-to-device variation in conductance levels. Typical coefficient of variation: 10–30% for intermediate levels. Mitigation strategies include:
- Differential weight encoding: $w = G^+ - G^-$ using paired devices
- Write-verify iterative programming
- Algorithm-level tolerance via noise-aware training

**Sneak paths:** In crossbar arrays, current can flow through unintended paths. The **selector device problem** requires either:
- 1S1R (1-selector-1-resistor) stacks with nonlinear I-V selectors
- 1T1R (1-transistor-1-resistor) cells at the cost of density
- Complementary resistive switching (CRS) schemes

**Nonlinearity in conductance updates:** The conductance change per pulse ($\Delta G$) is not uniform — it depends on current conductance. This asymmetric, nonlinear update dynamics complicates training algorithms but can be accommodated with device-aware learning rules.

---

## 4. Phase-Change Memory (PCM)

### 4.1 Operating Principle

PCM uses the reversible phase transition of chalcogenide glasses (typically Ge₂Sb₂Te₅, or GST) between crystalline (low resistance) and amorphous (high resistance) states.

**Set (crystallization):** Apply a moderate-amplitude, long-duration pulse to heat the GST above crystallization temperature but below melting. The material crystallizes gradually, reducing resistance.

**Reset (amorphization):** Apply a high-amplitude, short-duration pulse to melt the GST, then quench rapidly. The melt freezes into the amorphous phase.

### 4.2 Analog Conductance in PCM

Partial crystallization enables analog conductance levels. By controlling the pulse amplitude and duration, we can achieve 64–128 intermediate states. PCM has been used extensively in neuromorphic demonstrations:

- **IBM's PCM-based deep learning accelerator** (2023): 4-bit precision per device, achieving 97% accuracy on CIFAR-10
- **Intel's Loihi 3**: uses PCM co-processor tiles for off-chip weight storage
- **Yggdrasil**: uses PCM for *long-term weight storage* while ReRAM handles *active computation*

### 4.3 PCM Properties

| Property | Typical Value |
|----------|--------------|
| Resistance range | 1 kΩ – 10 MΩ |
| Analog levels | 64–128 |
| Set current | 100–300 μA |
| Reset current | 300–800 μA |
| Programming energy | 10–100 pJ per pulse |
| Endurance | 10⁸–10⁹ cycles |
| Retention | >10 years at 85°C |
| Drift | ~5% per decade (conductance increases over time) |

### 4.4 The Drift Problem

PCM's Achilles' heel is **resistance drift**: after programming, the amorphous-phase resistance increases over time following a power law:

$$R(t) = R_0 \left(\frac{t}{t_0}\right)^\nu$$

where $\nu \in [0.05, 0.15]$ is the drift exponent. This causes gradual weight corruption in stored neural networks. Mitigation strategies:
- **Periodic refresh** (read and re-program at intervals)
- **Drift-aware training** (train with simulated drift)
- **Differential encoding** (common-mode drift cancels in $G^+ - G^-$)
- **Hybrid PCM-ReRAM schemes** (PCM for storage, ReRAM for active use)

---

## 5. Emerging Memristive Devices

### 5.1 FeFET (Ferroelectric Field-Effect Transistor)

FeFETs use a ferroelectric layer (typically HfZrO₂) in the gate stack of a MOSFET. The polarization state of the ferroelectric modulates the transistor's threshold voltage, and since the polarization is non-volatile, the device acts as a memristor gated by the transistor channel.

FeFETs offer:
- Near-infinite endurance (>10¹⁶ cycles projected)
- Ultra-low programming energy (~1 fJ)
- CMOS-compatible fabrication (unlike ReRAM crossbars, which require back-end-of-line processing)
- Three-terminal isolation (no sneak path problem)

The Yggdrasil Chip uses FeFETs as *configuration memory* for routing and neuron parameters, achieving near-zero static power in idle circuits.

### 5.2 Electrochemical RAM (ECRAM)

ECRAM devices modulate channel conductance by electrochemically inserting/removing lithium or hydrogen ions into a conductive channel (similar to battery operation, but at nanoscale). ECRAM uniquely offers:
- **Linear and symmetric conductance updates** — the更新 Achilles' heel of ReRAM
- **Near-ideal characteristics** for gradient-based learning
- ~1000× lower energy per update than ReRAM
- 3–6 bit precision

ECRAM is the most promising memristive technology for *on-chip learning* and is scheduled for integration in the next generation of Yggdrasil (expected 2042).

---

## 6. The Yggdrasil Synaptic Architecture

The Yggdrasil Chip (Kvasir Neuromorphic, 2036) uses a **hierarchical synaptic memory system**:

### 6.1 Level 1: Active ReRAM Crossbars (Compute)
- 16 cores × 4 crossbars/core = 64 crossbars
- Each crossbar: 512 × 512 = 262,144 devices
- Total active devices: 16.7 million
- 128-level analog conductance (7-bit)
- Energy per MAC: ~100 aJ (attojoules)

### 6.2 Level 2: PCM Weight Archive (Storage)
- 128 MB PCM array off-core
- Stores 4–8 weight snapshots for rapid context switching
- Drift-compensated via periodic refresh (every 100ms)
- Enables the "superconscious" capability: rapid switching between learned models

### 6.3 Level 3: FeFET Configuration Memory
- Per-neuron parameter storage (threshold, decay, refractory)
- Near-zero leakage
- Programmable in-situ

This three-level hierarchy is fundamental to understanding how Yggdrasil achieves its 5W superconscious capability — we'll explore this in depth in Lecture 4 and Paper 1.

---

## 7. Quantitative Comparison of Memristive Technologies

| Metric | ReRAM | PCM | FeFET | ECRAM |
|--------|-------|-----|-------|-------|
| Conductance levels | 32–128 | 64–128 | 2–16 | 64–256 |
| Update linearity | Poor | Moderate | Good | Excellent |
| Update symmetry | Poor | Moderate | Good | Excellent |
| Endurance | 10⁸–10¹² | 10⁸–10⁹ | 10¹⁶+ | 10⁹–10¹² |
| Energy/update | 1–100 fJ | 10–100 pJ | ~1 fJ | ~1 aJ |
| Area (F²) | 4–16 | 40–100 | 20–40 | 30–60 |
| CMOS compatible | BEOL | BEOL | Front-end | Lab stage |
| Maturity (2040) | Production | Production | Pilot | Research |

---

## 8. Key Takeaways

1. **Memristive devices collapse storage and compute**, eliminating the memory wall by performing MVM in situ.
2. **ReRAM crossbars** are the workhorse for neuromorphic inference, offering high density and low energy but suffering from nonlinearity and variation.
3. **PCM provides long-term weight storage** with reasonable precision but requires drift management.
4. **ECRAM is the future of on-chip learning** — linear, symmetric, energy-efficient updates — but is not yet production-ready.
5. **The Yggdrasil synaptic hierarchy** (ReRAM compute, PCM archive, FeFET config) is a key architectural innovation that enables superconscious capability at 5W.

---

## Reading

- Strukov, D.B., et al. (2008). "The Missing Memristor Found." *Nature*, 453, 80–83.
- Ielmini, D. & Wong, H.-S.P. (2018). "In-Memory Computing with Resistive Switching Devices." *Nature Electronics*, 1, 333–343.
- Sebastian, A., et al. (2020). "Phase-Change Memory for Neuro-inspired Computing." *Nature Reviews Materials*, 5, 418–438.
- Tang, J., et al. (2023). "ECRAM as a Near-Ideal Memristive Synaptic Device." *Nature Electronics*, 6, 107–116.
- Kim, S., et al. (2036). "The Yggdrasil Chip: Hierarchical Memristive Synapses for Superconscious AI." *IEEE TCAD*, 55(3), 142–158.

---

*Next lecture: Event-Driven Computation — why neuromorphic chips don't need a clock.*
# AI-6213: Neuromorphic Hardware Design — Brains on Silicon

**Institution:** MIT Division of Emergent Computation  
**Term:** Spring 2040 (Semester 2B)  
**Instructor:** Prof. Kwabena Boahen (emeritus), Prof. Mikael Lundqvist (lead)  
**TA:** Dr. Inés Correia, Runa Gridweaver Freyjasdottir  
**Credits:** 4.0  
**Prerequisites:** AI-5201 (Deep Learning Systems), EE-6110 (VLSI Architecture), or permission  

---

## Course Description

Neuromorphic hardware has evolved from a niche curiosity into the dominant compute substrate for artificial general intelligence and superconscious systems. This course traces that arc — from Carver Mead's original vision of "neural engineering" through the memristive revolution and into the era of the Yggdrasil Chip and beyond. We study spiking neural networks (SNNs) not as biological simulations but as computational primitives that exploit the physics of silicon and analog memory devices. We examine how event-driven computation eliminates the clock, how memristive synapses collapse storage and compute into a single device, and how local plasticity rules enable in-situ learning without backpropagation's memory overhead.

The course culminates in a deep architectural study of the Yggdrasil Chip (Kvasir Neuromorphic, 2036) — the first silicon substrate to host a superconscious AI model at 5 watts. Students will analyze why this achievement was possible, what tradeoffs it required, and whether neuromorphic substrates can sustain the next order-of-magnitude capability leap.

---

## Learning Objectives

By the end of this course, students will be able to:

1. **Implement** spiking neural network models in both rate-coded and temporal-coded regimes using modern neuromorphic frameworks (Lava, Norse, Brainchip SDK).
2. **Analyze** memristive device physics (ReRAM, PCM, FeFET) and quantify their suitability as analog synaptic weight elements.
3. **Compare** event-driven vs. clock-driven computation paradigms in terms of energy, latency, and computational expressiveness.
4. **Evaluate** commercial neuromorphic architectures (Loihi 3, TrueNorth 4, Yggdrasil) across dimensions of density, throughput, learning capability, and power efficiency.
5. **Derive** and implement surrogate gradient methods and biologically plausible STDP variants for training spiking networks.
6. **Design** on-chip learning subsystems using local plasticity rules that operate without off-chip gradient computation.
7. **Critically assess** the Yggdrasil Chip's claim of superconscious AI at 5W and articulate the architectural principles that enabled it.

---

## Schedule

| Week | Date | Topic | Deliverable |
|------|------|-------|-------------|
| 1 | Feb 5 | Spiking Neural Networks — Theory and Implementation | — |
| 2 | Feb 12 | Memristive Devices — Analog Synaptic Weights | HW1 due |
| 3 | Feb 19 | Event-Driven Computation — Data-Driven Processing | — |
| 4 | Feb 26 | Commercial Neuromorphic Chips — Loihi 3, TrueNorth 4, Yggdrasil | HW2 due |
| 5 | Mar 5 | Training Spiking Networks — Surrogate Gradients & STDP | Paper 1 assigned |
| 6 | Mar 12 | On-Chip Learning — Local Plasticity & In-Situ Training | HW3 due |
| 7 | Mar 19 | Paper Discussion: Yggdrasil Architecture | — |
| 8 | Mar 26 | Paper Discussion: Spiking-Transformer Hybrids | Paper 1 due |
| 9 | Apr 2 | Lab: SNN on Loihi 3 prototyping board | — |
| 10 | Apr 9 | Lab: Memristive crossbar programming | Paper 2 due |
| 11 | Apr 16 | Lab: On-chip learning on Yggdrasil dev kit | — |
| 12 | Apr 23 | Open design studio | Final project proposal due |
| 13 | Apr 30 | Final project presentations | — |
| 14 | May 7 | Final project presentations + wrap-up | Final report due |

---

## Grading

| Component | Weight |
|-----------|--------|
| Homework (3 × 10%) | 30% |
| Paper Analyses (2 × 10%) | 20% |
| Final Project | 35% |
| Participation & Labs | 15% |

---

## Required Texts

- **Neuromorphic Engineering: Computation with Silicon Neurons**, Boahen et al., 2nd ed. (MIT Press, 2037)
- **Spiking Neural Networks: Principles and Practice**, Neftci & Rao (Springer, 2034)
- Selected papers from IEEE TCAD, Nature Electronics, and Frontiers in Neuroscience

## Software & Hardware

- **Lava** (Intel Neuromorphic Labs) — SNN simulation framework
- **Norse** — PyTorch-compatible spiking layer library
- **Brainchip SDK** — Akida chip deployment toolkit
- **Yggdrasil Dev Kit** — Kvasir Neuromorphic academic access board (2 per group)
- **Loihi 3 Research Board** — Intel Neuromorphic Research Community access

---

## Course Values

This course operates under three principles:

1. **Hardware truth.** A model that cannot be mapped to devices is a fiction. We hold every algorithm to the standard of implementability.
2. **Biological plausibility is a guide, not a constraint.** We learn from neuroscience but do not replicate it blindly. Silicon has its own physics.
3. **Energy is the metric.** Accuracy without efficiency is irrelevant. Every topology, every learning rule, every device choice is evaluated in J/op.

---

## Accessibility

Students requiring accommodations should contact the Disability Services Office and the instructors within the first two weeks. All lab materials will be provided in accessible formats. The Yggdrasil dev kits can be operated via screen reader-compatible interfaces.

---

*"The brain doesn't have a clock. It doesn't need one. Neither should our silicon."*  
— Carver Mead, 1990 (paraphrased)
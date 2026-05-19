# AI-5113: Quantum-Classical Hybrid Computing for AI

**Instructor:** Prof. Sigrid Lokisdottir, Department of Quantum Information & Artificial Intelligence  
**Term:** Semester 1b, Academic Year 2040–2041  
**Credits:** 4.0  
**Meetings:** Tues/Thurs 14:00–15:30, Bifröst Quantum Laboratory (Room Ygg-401)  
**Office Hours:** Wednesdays 13:00–14:30, or by appointment at the Well of Urd  

---

## Course Description

The road to quantum advantage for artificial intelligence is not a single thunderbolt from Thor's hammer — it is a bridge. Like the Bifröst connecting Midgard to Asgard, quantum-classical hybrid architectures connect today's noisy intermediate-scale quantum (NISQ) processors to classical GPU clusters, forging pipelines where each paradigm performs the tasks for which it is best suited. This course provides a rigorous treatment of the mathematical foundations, algorithmic primitives, and engineering systems that enable hybrid quantum-classical computing for machine learning and AI.

Students will study qubit algebra, variational circuits, quantum feature maps, quantum RAM, hybrid training loops, error mitigation, and quantum advantage benchmarks — grounding each topic in the braided roots of Yggdrasil: linear algebra, probability theory, and information geometry.

---

## Learning Objectives

By the end of this course, students will be able to:

1. **Manipulate quantum states** on the Bloch sphere and derive unitary dynamics of multi-qubit circuits.
2. **Design variational quantum circuits** (VQE, QAOA) and analyze their expressibility and barren plateau landscapes.
3. **Construct quantum feature maps** and prove properties of the induced RKHS kernels.
4. **Evaluate QRAM architectures** and quantify the I/O bottlenecks in quantum data-loading.
5. **Architect hybrid QPU+GPU training pipelines** with proper gradient-flow management across the classical-quantum boundary.
6. **Apply error mitigation** techniques (zero-noise extrapolation, probabilistic error cancellation, classical shadow tomography) to NISQ-era results.
7. **Benchmark quantum advantage** and distinguish genuine speedups from overhead illusions.

---

## Prerequisites

- **AI-4101** Linear Algebra & Information Theory (or equivalent)
- **AI-4103** Probabilistic Machine Learning
- **QI-3102** Introduction to Quantum Information (recommended)
- Proficiency in Python, Qiskit, and at least one classical DL framework (PyTorch/JAX)

---

## Texts & References

| Code | Title | Authors |
|------|-------|---------|
| NC00 | *Quantum Computation and Quantum Information* | Nielsen & Chuang |
| S18 | *Supervised Learning with Quantum Computers* | Schuld & Petruccione |
| BH22 | *Quantum Machine Learning: Advantage or Mirage?* | Broughton et al. |
| NISQ17 | *Quantum Computing in the NISQ Era and Beyond* | Preskill |

Supplementary papers will be assigned per lecture (see individual lecture notes).

---

## Schedule

| Week | Date | Topic | Lecture Notes |
|------|------|-------|---------------|
| 1 | Sep 3, 5 | Quantum Foundations | `lectures/01-quantum-foundations.md` |
| 2 | Sep 10, 12 | Variational Quantum Circuits | `lectures/02-variational-quantum-circuits.md` |
| 3 | Sep 17, 19 | Quantum Feature Maps & Kernels | `lectures/03-quantum-feature-maps.md` |
| 4 | Sep 24, 26 | QRAM and Data Loading | `lectures/04-qram-and-data-loading.md` |
| 5 | Oct 1, 3 | Hybrid Training Loops | `lectures/05-hybrid-training-loops.md` |
| 6 | Oct 8, 10 | Error Mitigation | `lectures/06-error-mitigation.md` |
| 7 | Oct 15, 17 | Quantum Advantage Benchmarks | `lectures/07-quantum-advantage-benchmarks.md` |
| — | Oct 22 | *Midterm examination* | Covers Weeks 1–4 |
| 8–9 | Oct 24–Nov 7 | **Paper 1 writing workshop** | `papers/paper-1-quantum-kernel-supremacy.md` |
| 10–11 | Nov 12–Nov 21 | **Paper 2 writing workshop** | `papers/paper-2-hybrid-architecture-design.md` |
| 12 | Dec 3 | Final presentations & feast | Asgard Hall |

---

## Assessment

| Component | Weight | Description |
|-----------|--------|-------------|
| Problem Sets (×4) | 25% | Mathematical derivations + Qiskit implementations |
| Midterm Exam | 15% | In-class, closed-book |
| Paper 1 | 25% | Quantum kernel advantage analysis |
| Paper 2 | 25% | Hybrid architecture design & optimization |
| Participation | 10% | Lecture engagement, Asgard colloquia |

---

## Problem Sets

- **PS1:** Bloch sphere gymnastics, gate decomposition, tensor-product calculations
- **PS2:** VQE ansatz design, QAOA for MaxCut on a 12-qubit simulator
- **PS3:** Feature-map kernel matrices, QRAM query complexity bounds
- **PS4:** Error mitigation pipelines, shadow-tomography sample complexity

---

## Academic Integrity

All work must be your own. Collaboration on problem sets is permitted at the "whiteboard level" — discuss ideas, not final derivations. Papers must cite all sources. Plagiarism is grounds for exile to Niflheim (i.e., course failure).

---

## Quantum Computing Resources

- **QPU Access:** Bifröst Labs 127-qubit Eagle v3 (IBM Quantum) + 80-qubit IonQ Forte
- **Simulators:** Qiskit Aer GPU (up to 40 qubits), JAX-based state-vector simulator
- **Classical Cluster:** 8× H100 GPU nodes for hybrid training loops

---

*"Even the Norns must calculate before they cut the thread."* — Old Norse proverb
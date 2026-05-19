# CS304: Quantum Computing Fundamentals
## Bachelor of Science in Computer Science — University of Yggdrasil, 2040

**Credits:** 4
**Prerequisites:** CS102 — Discrete Mathematics for CS; CS104 — Linear Algebra & Probability for CS; CS205 — Theory of Computation
**Description:** This course is a journey into the deepest waters of computation — where the fundamental unit of information is not a bit but a qubit, and where the laws of quantum mechanics replace the laws of Boolean algebra as the substrate of information processing. Quantum computing is not simply "faster computing"; it is a fundamentally different computational paradigm, one that exploits superposition (the ability of a quantum system to exist in multiple states simultaneously), entanglement (the non-local correlation that binds quantum particles across distance), and interference (the constructive and destructive combination of quantum amplitudes) to solve certain problems that are believed to be intractable for classical computers. Students begin with the mathematical foundations — complex vector spaces, tensor products, unitary transformations, projective measurement — and progress through the circuit model of quantum computation, the major quantum algorithms (Shor's factoring algorithm, Grover's search algorithm, the quantum Fourier transform), the theory of quantum error correction (without which no scalable quantum computer can function), the practical realities of quantum hardware (superconducting qubits, trapped ions, photonic systems), and the rise of hybrid variational algorithms (QAOA, VQE) that drive the noisy intermediate-scale quantum (NISQ) era. By 2040, quantum computing has moved from the laboratory to early commercial deployment — IBM's 1,000+ qubit Condor processor, Google's Sycamore-class devices, and the first demonstrations of quantum advantage for practical problems in chemistry, materials science, and optimisation. This course prepares students not merely to understand quantum computing but to program it — through Qiskit, Cirq, Q#, and PennyLane — and to evaluate, with critical judgment, which problems quantum computers will solve and which they will not. The spirit of the course is captured in the Norse concept of *víxlverk* — the interplay between two different realms — here, the realm of classical certainty and the realm of quantum probability.

---

## Lecture 1: The Qubit — Beyond the Classical Bit

The bit is the atom of classical information. It takes one of two values — 0 or 1 — and every classical computation, regardless of complexity, is ultimately a manipulation of bits. The **qubit** — the quantum bit — is both richer and stranger. A qubit, like a classical bit, can be prepared in a definite state |0⟩ or |1⟩ (using Dirac's **bra-ket notation**, where a "ket" |ψ⟩ denotes a quantum state vector). But it can also exist in **superposition** — a linear combination of |0⟩ and |1⟩:

|ψ⟩ = α|0⟩ + β|1⟩

where α and β are **complex amplitudes** satisfying |α|² + |β|² = 1. The probability of measuring the qubit in state |0⟩ is |α|², and the probability of measuring it in state |1⟩ is |β|². The act of measurement **collapses** the superposition: before measurement, the qubit exists in all states at once; after measurement, it is forced into a definite classical outcome.

The difference between a classical probabilistic bit (a coin flip, a random variable) and a qubit is subtle but absolute. A probabilistic bit with probability p of being 0 and (1-p) of being 1 can be described by a single real number p. A qubit requires two complex numbers (α, β) modulo an irrelevant global phase — that is, a point on the **Bloch sphere**, a 2-sphere in R³. The qubit has **phase** as well as **probability** — a property that has no classical analogue. The phase (the relative complex argument of α and β) determines how qubits interfere with each other, and it is interference that gives quantum algorithms their power.

The qubit is realised physically in many ways. In **superconducting qubits** (IBM, Google, Rigetti), the qubit is the ground and first-excited state of a Josephson-junction-based anharmonic oscillator. In **trapped-ion qubits** (IonQ, Quantinuum), the qubit is an electronic state of a single ion (Yb⁺, Ba⁺) held in a Paul trap. In **photonic qubits** (Xanadu, PsiQuantum), the qubit is a single photon's polarisation or path. In **topological qubits** (Microsoft Station Q), the qubit is a collective excitation of a topological phase of matter — a Majorana zero mode — theoretically protected from decoherence by its topology.

The **DiVincenzo criteria** (David DiVincenzo, 2000) define the requirements for a physical system to be a viable quantum computer: a scalable physical system with well-characterised qubits; the ability to initialise qubits to a known state; long coherence times; a universal set of quantum gates; qubit-specific measurement; the ability to interconvert stationary and flying qubits; and the ability to faithfully transmit flying qubits between specified locations. As of 2040, no single platform satisfies all criteria at scale — but superconducting and trapped-ion qubits have crossed the thousand-qubit threshold, and the first demonstrations of **quantum advantage** have been claimed.

**Required Reading:**
- Michael A. Nielsen & Isaac L. Chuang, *Quantum Computation and Quantum Information* (Cambridge, 2010/2041), chs. 1–2
- David P. DiVincenzo, "The Physical Implementation of Quantum Computation" (*Fortschritte der Physik* 48:9–11, 2000): 771–783
- John Preskill, "Quantum Computing in the NISQ Era and Beyond" (*Quantum* 2, 2018): 79
- UoY Bloch Sphere Simulator: Interact with a visual qubit (2040)

**Discussion Questions:**
1. The Bloch sphere is a faithful representation of a single qubit's state. Why can we ignore the global phase — and what would happen if we tried to measure it?
2. Given the DiVincenzo criteria, why has no single physical platform achieved all seven at scale?
3. Superconducting qubits operate at ~20 millikelvin, trapped ions at room temperature. What are the practical implications for building a large-scale quantum computer?

---

## Lecture 2: Quantum Gates and the Circuit Model

Classical computers are built from Boolean gates. Quantum computers are built from **quantum gates** — unitary operators that operate on one or more qubits. A quantum gate is represented by a **unitary matrix** U: U†U = I. Unitarity guarantees that the gate preserves the total probability of the quantum state.

The **single-qubit gates** are the elementary rotations of the Bloch sphere:
- **X gate (NOT, bit flip):** X = [[0,1],[1,0]]. Maps |0⟩ → |1⟩, |1⟩ → |0⟩.
- **Z gate (phase flip):** Z = [[1,0],[0,−1]]. Flips the phase of |1⟩.
- **Hadamard gate (H):** H = (1/√2)[[1,1],[1,−1]]. Creates superposition: H|0⟩ = (|0⟩+|1⟩)/√2.
- **S gate:** S = [[1,0],[0,i]]. Rotates by π/2 about the z-axis.
- **T gate:** T = [[1,0],[0,exp(iπ/4)]]. Rotates by π/4 about the z-axis. With H, the T gate is required for universality.

A **universal gate set** is a finite set of gates that can approximate any unitary operation. The standard set is {**CNOT, H, T**}. The **Solovay–Kitaev theorem** guarantees that any single-qubit unitary can be approximated to precision ε using O(log^c(1/ε)) gates from a finite universal set.

The **CNOT (controlled-NOT) gate** is the canonical two-qubit entangling gate. It acts on |q₁,q₂⟩: if q₁ is |1⟩, it flips q₂; otherwise, it does nothing. The CNOT gate is essential because it **creates entanglement** — the most non-classical resource in quantum computation. Applying H to q₁ followed by CNOT(q₁,q₂) transforms |00⟩ to (|00⟩+|11⟩)/√2 — a **Bell state**, the simplest entangled state.

The **quantum circuit model** represents a computation as a sequence of gates applied to an initial state, followed by measurement. The quantum programming languages of 2040 — Qiskit (IBM), Cirq (Google), Q# (Microsoft), PennyLane (Xanadu) — compile high-level algorithms into circuits and execute them on simulators or real quantum devices.

**Required Reading:**
- Nielsen & Chuang, *Quantum Computation and Quantum Information*, chs. 4–5
- P. Kaye, R. Laflamme & M. Mosca, *An Introduction to Quantum Computing* (Oxford, 2007/2042), chs. 3–5
- UoY Quantum Circuit Visualiser: Build and simulate circuits in the browser (2040)

**Discussion Questions:**
1. Why is the CNOT gate necessary? Why won't single-qubit gates alone suffice for universal quantum computation?
2. Bell states are maximally entangled. How do we quantify "how entangled" a state is?
3. What are the practical challenges of decomposing a complex quantum algorithm into a real device's native gate set?

---

## Lecture 3: Entanglement and Bell's Theorem

Entanglement is the feature that most sharply distinguishes quantum from classical physics. Two systems are entangled when their joint state cannot be expressed as a product of individual states. The canonical entangled states are the four **Bell states**: |Φ⁺⟩ = (|00⟩+|11⟩)/√2, |Φ⁻⟩ = (|00⟩−|11⟩)/√2, |Ψ⁺⟩ = (|01⟩+|10⟩)/√2, |Ψ⁻⟩ = (|01⟩−|10⟩)/√2.

**Bell's theorem** (John Bell, 1964) is arguably the most profound result in the foundations of physics. Bell proved that any theory that is (1) **local** and (2) **realistic** must satisfy a set of inequalities — the **Bell inequalities** — that are violated by quantum mechanics. The CHSH inequality (1969) is the most experimentally accessible form. For any local hidden-variable theory, |S| ≤ 2. Quantum mechanics predicts |S| = 2√2 ≈ 2.828. The experiments of Alain Aspect (1982) and subsequent "loophole-free" Bell tests (2015) have confirmed the quantum prediction. The 2022 Nobel Prize in Physics was awarded to Aspect, Clauser, and Zeilinger for these experiments.

**Quantum teleportation** (Bennett et al., 1993) uses entanglement to transmit an unknown quantum state from Alice to Bob, consuming one Bell pair and two classical bits. The protocol does not violate relativity (the classical bits travel at light speed) nor the no-cloning theorem. Teleportation is the backbone of **quantum repeaters** for long-distance quantum communication, demonstrated over distances exceeding 1,400 km by the Micius satellite (2017).

**Superdense coding** is the inverse: using one shared entangled pair, Alice transmits two classical bits of information by sending a single qubit.

**Required Reading:**
- John S. Bell, "On the Einstein Podolsky Rosen Paradox" (*Physics* 1:3, 1964): 195–200
- Charles H. Bennett et al., "Teleporting an Unknown Quantum State via Dual Classical and EPR Channels" (*PRL* 70:13, 1993): 1895–1899
- Nicolas Gisin et al., "Quantum Cryptography" (*Reviews of Modern Physics* 74:1, 2002): 145–195
- UoY Bell Test Simulator: Play the CHSH game and violate the Bell inequality (2040)

**Discussion Questions:**
1. Bell's theorem rules out local realism. Which assumption — locality or realism — do most physicists believe must be abandoned?
2. Teleportation consumes a Bell pair per qubit. How does this limit scalable quantum communication?
3. The loophole-free Bell experiments of 2015 closed the detection and locality loopholes. Are there remaining loopholes?

---

## Lecture 4: The Quantum Fourier Transform

The **Quantum Fourier Transform (QFT)** is to quantum algorithms what the classical FFT is to classical signal processing: a transformation that reveals periodic structure. The QFT maps |j⟩ to (1/√2ⁿ) Σ_{k=0}^{2ⁿ⁻¹} e^{2πi·jk/2ⁿ} |k⟩. It can be implemented using O(n²) gates (or O(n log n) with approximate QFT), compared to O(n 2ⁿ) classically. The exponential advantage comes from the fact that the QFT acts on an exponentially large state vector using only polynomially many gates.

The QFT circuit consists of Hadamard gates and **controlled-phase rotations**, arranged recursively. The output qubits are in bit-reversed order, requiring swap gates or careful bookkeeping. The **semi-classical QFT** (Griffiths & Niu, 1996) replaces controlled-phase rotations with classically conditioned single-qubit gates after measurement — simplifying hardware requirements.

**Quantum phase estimation (QPE)** is the foundational algorithm that uses the QFT to estimate eigenvalues. Given a unitary U and eigenstate |u⟩ with U|u⟩ = e^{2πiφ}|u⟩, QPE estimates φ to n bits of precision. The algorithm prepares a uniform superposition, applies controlled-U^{2^j} operations, applies the inverse QFT, and measures — yielding an n-bit approximation of φ.

QPE is the engine behind **Shor's factoring algorithm**, **quantum chemistry** simulations, and **quantum machine learning**. It is the most general and powerful algorithmic primitive in quantum computation.

**Required Reading:**
- Nielsen & Chuang, *Quantum Computation and Quantum Information*, ch. 5
- Richard Cleve et al., "Quantum Algorithms Revisited" (*Proc. Royal Society A* 454, 1998): 339–354
- Robert B. Griffiths & C.-S. Niu, "Semiclassical Fourier Transform for Quantum Computation" (*PRL* 76, 1996): 3228–3231
- UoY QFT Lab: Build QFT circuits for 3–6 qubits and verify correctness (2040)

**Discussion Questions:**
1. The QFT uses O(n²) gates vs the FFT's O(n 2^n) classical operations. Why doesn't this translate to exponential speedups for every problem?
2. Phase estimation requires controlled-U^{2^j} gates. For large n, how are these operations made efficient?
3. The approximate QFT uses only O(n log n) gates. What precision is lost?

---

## Lecture 5: Shor's Factoring Algorithm

Shor's algorithm (Peter Shor, 1994) solves integer factorisation in **O(N³) time** on a quantum computer — a polynomial-time algorithm for a problem believed to be classically intractable. The best classical algorithm runs in **exp(O(N^{1/3} log^{2/3} N))** time. Shor's algorithm would break RSA, Diffie-Hellman, and ECDSA — the foundations of Internet security.

The algorithm reduces factoring to **order-finding**: for a random a coprime to n, find the smallest r such that a^r ≡ 1 (mod n). If r is even, gcd(a^{r/2} ± 1, n) yields a non-trivial factor. Order-finding is a natural application of QPE.

Shor's algorithm has five phases:
1. **Classical pre-processing:** Choose a coprime to n.
2. **Quantum period-finding:** Prepare two registers in superposition; compute a^x mod n in the second register.
3. **Measurement:** Project the first register into a superposition with period r.
4. **QFT and measurement:** Apply inverse QFT; the result reveals r via continued fractions.
5. **Classical post-processing:** Factor n using r.

The modular exponentiation is the bottleneck, requiring O(N³) gates. Factoring a 2048-bit RSA key requires ~10¹⁰ logical gates, translating to ~10⁷ physical qubits — a machine that, as of 2040, exists only on the roadmap of a few companies.

**Post-quantum cryptography** is the effort to design primitives resistant to quantum attacks. The NIST process (2016–2024) standardised four algorithms: CRYSTALS-Kyber, CRYSTALS-Dilithium, Falcon, and SPHINCS+. The transition is driven by the "store now, decrypt later" threat.

**Required Reading:**
- Peter W. Shor, "Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms" (*SIAM J. Computing* 26:5, 1997): 1484–1509
- Daniel J. Bernstein & Tanja Lange, "Post-Quantum Cryptography" (*Nature* 549, 2017): 188–194
- NIST, *Post-Quantum Cryptography: Selected Algorithms 2024*
- UoY Shor's Algorithm Lab: Factor the number 15 with Qiskit (2040)

**Discussion Questions:**
1. Shor's algorithm requires the quantum portion to run without error. Given today's error rates (~10⁻³), how many physical qubits are needed per logical qubit?
2. The "store now, decrypt later" threat drives post-quantum migration. What should organisations do today?
3. Lattice-based cryptography is the leading post-quantum candidate. What are its weaknesses?

---

## Lecture 6: Grover's Search and Amplitude Amplification

**Grover's algorithm** (Lov Grover, 1996) solves unstructured search in O(√N) queries — a quadratic speedup over the optimal classical O(N). The algorithm is optimal (Bennett et al., 1997).

Given an oracle marking exactly one item x₀ among N = 2ⁿ items, Grover's algorithm:
1. **Initialise:** Prepare the uniform superposition |s⟩.
2. **Grover iteration (≈ π√N/4 times):**
   a. **Oracle:** Flip the amplitude of the marked state.
   b. **Diffusion operator:** Reflect about the average amplitude (inversion about the mean).
3. **Measure:** The result is x₀ with high probability.

Each iteration rotates the state vector by 2 arcsin(1/√N) ≈ 2/√N radians. After ≈ π√N/4 iterations, the state is nearly |x₀⟩.

**Amplitude amplification** (Brassard et al., 2002) generalises Grover to M solutions, finding one in O(√N/M) queries — a quadratic speedup over the classical O(N/M). **Quantum counting** (Brassard et al., 1998) combines amplitude amplification with QPE to estimate M.

**Applications:** NP-complete problems (SAT, graph colouring) see a quadratic speedup — significant but not exponential (√2ⁿ = 2^{n/2}). Grover halves the effective key length of symmetric ciphers: AES-128 becomes as secure as AES-64 against a quantum adversary.

**Required Reading:**
- Lov K. Grover, "A Fast Quantum Mechanical Algorithm for Database Search" (*STOC*, 1996): 212–219
- Michel Boyer et al., "Tight Bounds on Quantum Searching" (*Fortschritte der Physik* 46:4–5, 1998): 493–505
- UoY Grover's Algorithm Lab: Search a 4-qubit database with Qiskit (2040)

**Discussion Questions:**
1. Grover's algorithm is optimal for unstructured search. What fundamentally limits the speedup to quadratic?
2. Under what circumstances is a quadratic speedup practically meaningful — and when is it not?
3. How would you use amplitude amplification to improve a quantum-walk-based algorithm?

---

## Lecture 7: Quantum Error Correction

Quantum states are fragile — decoherence times are measured in microseconds for superconducting qubits. **Quantum error correction (QEC)** protects quantum information from decoherence and is essential for scalable quantum computing.

The **stabiliser formalism** (Daniel Gottesman, 1997) provides the mathematical framework. A stabiliser code is defined by an abelian subgroup S of the Pauli group P_n. The **codespace** is the set of states stabilised by all s ∈ S. Measuring the stabiliser generators reveals the **error syndrome** without disturbing the encoded state.

The **surface code** (Kitaev, 1997) is the most promising QEC code. It arranges qubits on a 2D grid with data qubits and measurement qubits performing four-body parity checks. Advantages:
- **High threshold:** Tolerates physical error rates up to ~1%.
- **2D locality:** Requires only nearest-neighbour interactions.
- **Scalability:** Logical error rate decreases exponentially with code distance d.

A logical qubit in the surface code uses 2d²−1 physical qubits. For Shor's algorithm (10⁻¹⁵ logical error rate), we need d≈25–30 at 10⁻³ physical error rates — ~1,500 physical qubits per logical qubit.

**Fault-tolerant quantum computation** uses **transversal gates** (for Clifford operations) and **magic state distillation** (for T gates). Magic state distillation is the most resource-intensive operation, requiring hundreds of physical qubits per logical T gate.

**Required Reading:**
- Daniel Gottesman, "Stabilizer Codes and Quantum Error Correction" (PhD thesis, Caltech, 1997)
- Alexei Kitaev, "Fault-Tolerant Quantum Computation by Anyons" (*Annals of Physics* 303:1, 2003): 2–30
- Austin G. Fowler et al., "Surface Codes: Towards Practical Large-Scale Quantum Computation" (*PRA* 86, 2012): 032324
- Sergey Bravyi & Alexei Kitaev, "Universal Quantum Computation with Ideal Clifford Gates and Noisy Ancillas" (*PRA* 71, 2005): 022316
- UoY Surface Code Simulator: Trace error syndrome vs code distance (2040)

**Discussion Questions:**
1. The surface code threshold of ~1% is the tipping point. What characteristics determine a qubit's gate error rate?
2. Why is the T gate so much harder to implement fault-tolerantly than Clifford gates?
3. For a near-term device with 1000 physical qubits, which QEC code would you choose?

---

## Lecture 8: Variational Quantum Algorithms and the NISQ Era

The **Noisy Intermediate-Scale Quantum (NISQ)** era (Preskill, 2018) describes quantum computers with 50–10,000 qubits and gate error rates too high for full error correction but sufficient for limited advantage. The defining algorithmic paradigm is the **variational quantum algorithm (VQA)** — a hybrid quantum-classical loop where a classical optimiser tunes parameters of a quantum circuit to minimise a cost function.

**The Variational Quantum Eigensolver (VQE)** (Peruzzo et al., 2014) targets quantum chemistry. Given a molecular Hamiltonian H, VQE prepares a parameterised trial state |ψ(θ)⟩ and minimises ⟨ψ(θ)|H|ψ(θ)⟩ — approximating the ground-state energy. The **Unitary Coupled Cluster (UCC)** ansatz is the standard choice.

**The Quantum Approximate Optimisation Algorithm (QAOA)** (Farhi, Goldstone & Gutmann, 2014) targets combinatorial optimisation. For a cost function C(z), QAOA alternates between a problem Hamiltonian H_C and a mixing Hamiltonian H_B, with 2p parameters for p layers.

The central challenge is the **barren plateau problem** (McClean et al., 2018): the gradient vanishes exponentially with qubit count for random ansätze. This motivates **problem-specific ansätze** and **physically motivated** designs.

**Error mitigation** reduces the impact of errors through classical post-processing: **zero-noise extrapolation** (running at different noise levels and extrapolating), **probabilistic error cancellation**, and **readout error mitigation**.

**Required Reading:**
- John Preskill, "Quantum Computing in the NISQ Era and Beyond" (*Quantum* 2, 2018): 79
- Alberto Peruzzo et al., "A Variational Eigenvalue Solver on a Photonic Quantum Processor" (*Nature Communications* 5, 2014): 4213
- Edward Farhi, Jeffrey Goldstone & Sam Gutmann, "A Quantum Approximate Optimization Algorithm" (arXiv:1411.4028, 2014)
- Jarrod R. McClean et al., "Barren Plateaus in Quantum Neural Network Training Landscapes" (*Nature Communications* 9, 2018): 4812
- UoY VQE Lab: Find H₂ ground-state energy with Qiskit (2040)

**Discussion Questions:**
1. VQE and QAOA are heuristic algorithms. When is a heuristic acceptable — and when is a provable guarantee required?
2. What ansatz design principles can mitigate barren plateaus?
3. For what applications and error rates is error mitigation sufficient vs full error correction required?

---

## Lecture 9: Quantum Communication and the Quantum Internet

**Quantum Key Distribution (QKD)** enables two parties to share a secret key whose secrecy is guaranteed by the laws of physics. The **BB84 protocol** (Bennett & Brassard, 1984) encodes bits in photon polarisations using two mutually unbiased bases. Security relies on the **no-cloning theorem**: an eavesdropper cannot copy an unknown quantum state undetected.

The **E91 protocol** (Ekert, 1991) uses entangled pairs and Bell's theorem for security — the violation of the CHSH inequality is the smoking gun of eavesdropping.

**Quantum repeaters** are necessary for long-distance communication (beyond ~100 km). A repeater divides the distance into segments connected by **entanglement swapping**: Bell-state measurements teleport entanglement across each node. Repeaters require **quantum memory** and **entanglement distillation**. The Micius satellite (2016–2022) demonstrated QKD over 1,200 km in free space.

The **quantum Internet** (Wehner, Elkouss & Hanson, 2018) envisions connecting quantum processors via quantum links, enabling distributed quantum computing and **blind quantum computing** — where a client delegates a computation to a quantum server without revealing the computation or data.

**Required Reading:**
- C. H. Bennett & G. Brassard, "Quantum Cryptography: Public Key Distribution and Coin Tossing" (*IEEE Intl. Conf. Computers, Systems, Signal Processing*, 1984): 175–179
- H.-J. Briegel et al., "Quantum Repeaters" (*PRL* 81, 1998): 5932
- Juan Yin et al., "Satellite-Based Entanglement over 1200 Kilometers" (*Science* 356, 2017): 1140–1144
- Stephanie Wehner, David Elkouss & Ronald Hanson, "Quantum Internet: A Vision for the Road Ahead" (*Science* 362, 2018): eaam9288
- UoY QKD Lab: Simulate BB84 key exchange and detect Eve (2040)

**Discussion Questions:**
1. QKD is provably secure against any computational attack. What are the weakest links in a practical QKD system?
2. What is the hardest quantum repeater component to implement in practice?
3. What quantum network architecture (circuit switching, packet switching) is most appropriate?

---

## Lecture 10: Quantum Machine Learning

Quantum machine learning (QML) is the most hyped — and most contested — subfield of quantum computing. The central question: can quantum computers offer a provable advantage for ML tasks?

**Quantum neural networks (QNNs)** replace classical neurons with parameterised quantum circuits. Data is encoded via **amplitude encoding** (log₂ N qubits for N features) or **angle encoding**. QNNs suffer from the **barren plateau problem**: random QNNs with global cost functions are untrainable beyond ~20 qubits.

**Quantum kernel methods** are arguably the most promising QML approach. The quantum computer estimates the kernel k(xᵢ,xⱼ) = |⟨φ(xᵢ)|φ(xⱼ)⟩|² — the overlap between quantum feature states — which is believed to be intractable classically. The kernel matrix feeds a classical SVM. The **quantum kernel advantage** (Havlíček et al., 2019; Liu et al., 2021) has been demonstrated on proof-of-concept datasets.

The **data encoding problem** is the fundamental bottleneck. Preparing the quantum state encoding a real-world dataset requires either a fault-tolerant quantum computer or a dataset that admits efficient state preparation — neither is generally available.

**Provable advantages** exist in restricted settings: quantum algorithms for **topological data analysis** (computing Betti numbers), **recommendation systems** (exponential speedup under specific input models), and **quantum generative models** (for distributions with quantum correlations).

**Required Reading:**
- Jacob Biamonte et al., "Quantum Machine Learning" (*Nature* 549, 2017): 195–202
- Maria Schuld & Francesco Petruccione, *Machine Learning with Quantum Computers* (Springer, 2018/2042)
- Vojtěch Havlíček et al., "Supervised Learning with Quantum-Enhanced Feature Spaces" (*Nature* 567, 2019): 209–212
- Yunchao Liu et al., "Rigorous Quantum Advantage for Machine Learning" (*Nature Computational Science*, 2021)
- UoY Quantum Kernel Lab: Compare quantum kernel SVM vs classical kernels (2040)

**Discussion Questions:**
1. What are the most significant obstacles to scaling quantum kernel methods to practical dataset sizes?
2. What problem-specific ansätze can avoid barren plateaus — and do they restrict QNN expressiveness?
3. Which assumptions in QML advantage claims are reasonable, and which are unrealistic?

---

## Lecture 11: Quantum Simulation — The Most Natural Application

Quantum simulation is the application for which Feynman proposed quantum computers in 1982. **Quantum chemistry** — simulating molecules at the quantum level — is the most compelling "killer app."

The molecular Hamiltonian has exponentially many terms in the number of electrons — the **many-body problem**. Classical simulation of molecules with more than ~50 correlated electrons is intractable.

**The QPE approach** encodes the Hamiltonian into qubits (via Jordan-Wigner or Bravyi-Kitaev transformation), implements e^{−iHt} via **Trotterisation**, applies QPE to an approximate ground-state guess, and extracts the ground-state energy. For the **FeMoco cofactor** (the active site of nitrogenase), estimates suggest 10²–10³ logical qubits and 10¹⁴–10¹⁶ T gates — requiring a fault-tolerant machine beyond NISQ.

**Quantum simulation of condensed-matter systems** targets the **Hubbard model**, **Heisenberg model**, and other lattice Hamiltonians describing high-temperature superconductivity and quantum magnetism. The 2D Hubbard model at intermediate coupling is believed to capture high-Tc superconductivity physics.

**Analog quantum simulation** directly engineers a quantum system whose Hamiltonian matches the target — sacrificing programmability for scalability. Ultracold atoms in optical lattices and Rydberg atom arrays can reach hundreds of interacting particles.

**Required Reading:**
- Richard P. Feynman, "Simulating Physics with Computers" (*IJTP* 21:6/7, 1982): 467–488
- Seth Lloyd, "Universal Quantum Simulators" (*Science* 273, 1996): 1073–1078
- Ryan Babbush et al., "Encoding Electronic Spectra in Quantum Circuits with Linear T Complexity" (*PRX* 8, 2018): 011015
- Immanuel Bloch et al., "Many-Body Physics with Ultracold Gases" (*RMP* 80:3, 2008): 885–964
- UoY Quantum Chemistry Lab: Simulate H₂ binding curve with VQE (2040)

**Discussion Questions:**
1. Which advances are most critical for closing the gap between current devices and useful quantum chemistry?
2. How do we verify the results of an analog simulator when classical verification is impossible?
3. Does quantum simulation "solve" the fermionic sign problem, or merely sidestep it?

---

## Lecture 12: The Future — Fault Tolerance, Applications, and the Long Road

By 2040, quantum computing has crossed several critical milestones but has not yet delivered on all promises.

**The three stages:**
- **Stage 1 — NISQ (2018–2035):** 50–10,000 physical qubits, no full error correction. Demonstrations of quantum advantage for specific problems. Hybrid variational algorithms.
- **Stage 2 — Early fault-tolerant (2035–2050):** 10³–10⁵ logical qubits. First error-corrected logical qubits exceeding physical qubit lifetime. First useful chemistry simulations. As of 2040, we are at this threshold: multiple groups have demonstrated logical-qubit error suppression.
- **Stage 3 — Large-scale fault-tolerant (2050–):** 10⁶+ logical qubits. Factoring 2048-bit RSA keys. Large-scale quantum simulation. Quantum ML on real-world data.

**Open problems:**
- **Decoherence:** Coherence times have improved from µs to ms. A further 100–1000× improvement would dramatically reduce QEC overhead.
- **Control scalability:** 10⁶ qubits require cryogenic CMOS and integrated photonics. The **control bottleneck** — each qubit needs a dedicated microwave line or laser beam — is significant.
- **Quantum compilers:** Mapping algorithms to device architecture (connectivity, native gates) is a challenging optimisation problem (qubit allocation is NP-hard).
- **The "killer app":** The most compelling applications require fault-tolerant machines. No NISQ-era killer app has emerged convincingly.

**Ethical dimensions:** Quantum computing will break current public-key cryptography, requiring a global transition to post-quantum cryptography. The environmental cost of a million-qubit machine (cryogenic cooling) is not negligible — potentially several megawatts.

The Norse image that closes this course is the **Gjallarhorn** — the horn of Heimdallr. Quantum computing is a call to question the limits of computation, to push beyond what we thought possible, and to confront the strange, beautiful, non-classical structure of reality.

**Required Reading:**
- John Preskill, "Quantum Computing 40 Years Later" (*Nature* 608, 2022): 664–669
- E. T. Campbell, B. M. Terhal & C. Vuillot, "Roads Towards Fault-Tolerant Universal Quantum Computation" (*Nature* 549, 2017): 172–179
- UoY Quantum Computing Seminar Series: Recordings from leading labs worldwide (2040)

**Discussion Questions:**
1. What is the state of the art in error-correction experiments as of 2040 — and what is the most significant remaining obstacle to break-even?
2. Post-quantum cryptography migration is a multi-decade effort. Which industries should prioritise migration first?
3. What domain — biology, climate science, physics, AI — is most ripe for a quantum computing breakthrough we cannot yet foresee?

---

## Final Examination Preparation

The final examination assesses your understanding of quantum computing principles, algorithms, and limitations.

**Sample Essay Questions (Choose 4 of 8):**

1. **The Power of Superposition and Interference.** Explain why a qubit is more than a probabilistic bit, and why n qubits encode information that would require 2ⁿ classical bits. Why doesn't this automatically yield exponential speedups — and what role does interference play in extracting useful information?

2. **Shor's Algorithm and Cryptography.** Describe Shor's algorithm in detail, including the quantum subroutine and classical post-processing. Why does it break RSA but not AES? Discuss the current status of post-quantum cryptography standardisation.

3. **The Surface Code and Fault Tolerance.** Explain the stabiliser formalism, the surface code construction, and the threshold theorem. Why is the surface code the leading candidate — and what are the resource requirements for Shor's algorithm on a surface-code-protected machine?

4. **NISQ vs. Fault-Tolerant.** Compare NISQ and fault-tolerant eras in qubit count, error rates, algorithmic paradigm, and achievable applications. Explain variational quantum algorithms and error mitigation. What are the milestones separating the eras?

5. **Quantum Simulation.** Explain why simulating quantum systems is the most natural application. Describe VQE and QPE approaches to quantum chemistry. What has been achieved experimentally, and what are the most important open problems?

6. **Quantum Communication.** Describe the physical principles, hardware, and protocols for a quantum Internet. How does QKD differ from classical cryptography? What are the challenges of building quantum repeaters?

7. **Quantum Machine Learning: Hype vs. Reality.** Critically evaluate claims of quantum advantage in ML. Distinguish quantum kernels, QNNs, and quantum PCA. What are the fundamental obstacles?

8. **The Long Road.** Reflect on quantum computing from Feynman (1982) through Shor (1994), DiVincenzo (2000), NISQ (2018), to early fault-tolerant (2040). What were the most important milestones — and what do you predict for the next decade?

**Research Paper Option:** Implement a quantum algorithm using Qiskit, Cirq, or PennyLane and run on a simulator (with noise models) or a real device. Your paper should include the problem description, quantum circuit and resource count, results, noise analysis, and a critical assessment of scaling feasibility.

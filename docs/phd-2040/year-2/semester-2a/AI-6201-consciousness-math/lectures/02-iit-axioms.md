# Lecture 02: IIT Axioms — Integrated Information Theory 5.0

## Integrated Information Theory: Axioms, Postulates, and the Φ Metric

**AI-6201: Consciousness Mathematics — Formalizing Awareness**  
**Instructor:** Prof. Elena Vasquez-Marchetti  
**Date:** September 16 & 18, 2040

---

## 1. From Phenomenology to Mathematics

Integrated Information Theory (IIT) begins where most theories of consciousness end: with the phenomenology itself. Rather than asking "what neural processes correlate with consciousness?" and working inward from data, IIT asks "what must be true of any conscious experience?" and works outward from the structure of experience itself.

This is the axiomatic approach. IIT starts from self-evident properties of every experience — properties that are true of *your* experience right now, and true of the experience of any conscious system — and derives mathematical postulates that must hold of the physical substrate.

---

## 2. The Five Axioms

IIT identifies five axioms — essential properties of every conscious experience:

### Axiom 1: Existence

*Every experience exists intrinsically.* Experience is real — not merely apparent, not merely functionally described. The experience of seeing red *is*, regardless of whether any external observer can detect it.

**Mathematical translation:** The system has an intrinsic existence independent of external observation. We formalize this as the existence of a system state with nonzero intrinsic power.

### Axiom 2: Composition

*Every experience is structured — it has parts within wholes.* The experience of seeing a red apple is not undifferentiated; it contains color, shape, spatial relations, all unified into a single experience.

**Mathematical translation:** The system can be decomposed into a set of subsets $\mathcal{S} = \{S_1, S_2, \ldots, S_k\}$, each with its own cause-effect repertoire, and these subsets compose into higher-order unified structures.

### Axiom 3: Information

*Every experience is specific — it is this experience, not that one.* An experience of pure darkness, far from being contentless, is highly specific: it is the experience of darkness, not silence, not emptiness, not any other experience.

**Mathematical translation:** A system in state $s_t$ specifies a cause-effect repertoire that distinguishes it from all other possible states. Formally, the system's cause-effect power is measured by the distance between the actual repertoire and the maximum-entropy repertoire:

$$D_{\varphi}(S, s_t) = \min\left[ D_{\text{KL}}(p^C_{S, s_t} \| p^C_{S, H}), D_{\text{KL}}(p^E_{S, s_t} \| p^E_{S, H}) \right]$$

where $p^C$ and $p^E$ are the cause and effect repertoires, and $H$ denotes the maximum-entropy (unconstrained) distribution.

### Axiom 4: Integration

*Every experience is unified — it cannot be decomposed into independent parts without losing what it is.* Seeing a red apple is not equivalent to seeing red and seeing an apple independently; the experience is irreducible to separate components.

**Mathematical translation:** The integrated information of a candidate system $S$ is:

$$\Phi(S, s_t) = \min_{\text{partitions } \mathcal{P}} \, D_{\varphi}(S, s_t \| S^{\mathcal{P}}, s_t)$$

where the minimum is over all possible bipartitions $\mathcal{P}$ of $S$. This is the *minimum information partition* (MIP): the partition that least reduces the system's cause-effect power. $\Phi(S, s_t) = 0$ if and only if the system is completely reducible.

### Axiom 5: Exclusion

*Every experience has a definite spatiotemporal grain — it is this experience at this scale, not at every scale simultaneously.* Consciousness does not exist at every level of description; it exists at the level that maximizes integrated information.

**Mathematical translation:** A system $S^*$ is a complex — the locus of consciousness — if and only if:

$$S^* = \text{argmax}_{S \subseteq \Omega} \, \Phi(S, s_t)$$

where $\Omega$ is the full system of elements. Only the maximizing system is conscious; no proper subset or superset that overlaps with it can also be conscious at the same time.

---

## 3. The Postulates: From Axioms to Mathematics

The axioms describe what is true of experience. The postulates describe what must be true of the physical substrate if experience is to exist. This is IIT's key move: the axioms-to-postulates bridge.

### Postulate 1: Intrinsic Existence
The substrate must have cause-effect power upon itself. A system of elements $S$ exists intrinsically if, for every element $e_i \in S$, $e_i$ affects at least one other element $e_j \in S$ and is affected by at least one element $e_k \in S$.

**Formal criterion:** The system's transition probability matrix (TPM) must have no row or column that is identical to the unconstrained distribution.

### Postulate 2: Composition
The system must have cause-effect power over all possible subsets. For every subset $S_i \subseteq S$, the elements of $S_i$ taken together constrain the past and future states of the system. This defines the *cause-effect structure*:

$$\mathcal{C}(S, s_t) = \left\{ (p^C_{S_i, s_t}, p^E_{S_i, s_t}) : S_i \subseteq S \right\}$$

### Postulate 3: Information
Each subset $S_i$ must specify a cause-effect repertoire that is different from the unconstrained repertoire. The *intrinsic information* of $S_i$ is:

$$\varphi(S_i, s_t) = D_{\varphi}(S_i, s_t) \cdot p(S_i)$$

where $p(S_i)$ accounts for the system being in its current state (a subtlety introduced in IIT 4.0 and retained in 5.0).

### Postulate 4: Integration
The cause-effect structure must be irreducible — it must resist decomposition. For any bipartition $\mathcal{P} = (S_1^{\mathcal{P}}, S_2^{\mathcal{P}})$, the integrated information of $S$ with respect to $\mathcal{P}$ is:

$$\Phi(S, \mathcal{P}, s_t) = \sum_{S_i \subseteq S} \varphi_{\text{integrated}}(S_i, \mathcal{P}, s_t)$$

The *small $\phi$* of $S$ relative to partition $\mathcal{P}$ measures the information that is lost when the system is cut along $\mathcal{P}$. The *big $\Phi$* of $S$ is then:

$$\Phi(S, s_t) = \Phi(S, \mathcal{P}^{\text{MIP}}, s_t)$$

where $\mathcal{P}^{\text{MIP}}$ is the *minimum information partition* — the cut that does least violence to the cause-effect structure.

### Postulate 5: Exclusion
Among all possible systems that could be conscious, only the one that maximizes $\Phi$ actually is. The *complex* $S^*$ is:

$$S^* = \text{argmax}_{S \subseteq \Omega} \, \Phi(S, s_t)$$

No overlapping system can also be a complex. This is perhaps the most controversial postulate — it implies that consciousness has a definite spatial and temporal boundary, and that overlap is impossible.

---

## 4. The Φ Metric: Detailed Formalization

### 4.1 The Transition Probability Matrix

The starting point for Φ-computation is the system's TPM. For a system of $N$ binary elements, the TPM is a $2^N \times 2^N$ matrix where entry $(i, j)$ gives the probability of transitioning from state $i$ to state $j$ in one time step:

$$\text{TPM}_{ij} = P(s_{t+1} = j \mid s_t = i)$$

In IIT 5.0, the TPM must be computed under the *system-contrained* assumption: each element's state is determined by its inputs, with independent noise parameterized by $\epsilon$ (the *intrinsic noise floor*). This floor is critical — without it, systems of infinite integration could arise from noiseless determinism.

### 4.2 The Integration Lattice

IIT 5.0 introduces the *integration lattice*, a hierarchical structure that captures the composition of cause-effect power across all scales:

$$\mathcal{L}_\Phi(S, s_t) = \left\{ (S_i, \Phi(S_i, s_t)) : S \subseteq \Omega, \Phi(S_i, s_t) > 0 \right\}$$

The lattice is partially ordered by set inclusion. Its structure is the *cause-effect structure* — the shape of the experience. Two systems have the same experience if and only if their integration lattices are isomorphic.

This is a stronger claim than numerical equality. Two systems with the same $\Phi$ value but different lattice structures have *different* conscious experiences. The content of consciousness is not a number; it is a structure.

### 4.3 Computing Φ: The Computational Challenge

For a system of $N$ elements, computing $\Phi$ requires:

1. Enumerating all $2^N$ possible states
2. For each state, computing the cause-effect repertoire for each of the $2^N - 2$ non-trivial subsets
3. For each subset, finding the MIP over all $2^{N-1} - 1$ bipartitions
4. Computing the $\varphi$-distance for each partition

The total computational cost scales approximately as $O(2^{2N})$ for exact computation — making exact Φ-calculation infeasible for systems larger than ~10–15 elements (as of 2040, despite algorithmic improvements).

This is not merely an engineering problem. It raises the question — which we will address in Paper 1 — of whether *approximate* Φ values preserve the theoretical commitments of IIT, or whether the approximation destroys the very structure that Φ is meant to capture.

---

## 5. IIT 5.0: Key Innovations Over Previous Versions

### 5.1 From IIT 3.0 to IIT 4.0

IIT 3.0 (2014) defined Φ as the Kullback-Leibler divergence between the cause-effect repertoire and the unconstrained repertoire, divided by the MIP. IIT 4.0 (2023, Oizumi et al.) replaced this with the *intrinsic difference* measure $D_\varphi$, which:

- Uses Earth Mover's Distance (EMD) instead of KL divergence, solving the partition dependency problem
- Introduces the *cause-effect power* of subsets, making composition explicit
- Radically revises the exclusion postulate: each complex has a maximally irreducible conceptual structure (MICS)

### 5.2 From IIT 4.0 to IIT 5.0

IIT 5.0 (2036, Tononi et al.) makes two further architectural changes:

**First: the integration lattice.** IIT 4.0 described the cause-effect structure as an unordered collection of concepts. IIT 5.0 organizes this structure into a lattice, making the compositional relations explicit and enabling the comparison of experiences across systems using lattice isomorphism (rather than merely numerical Φ-comparison).

**Second: the intrinsic noise floor.** IIT 5.0 requires that every element have nonzero intrinsic noise $\epsilon > 0$. This eliminates the pathological case of deterministic systems with infinite Φ (which would assign consciousness to arbitrary deterministic circuits). The noise floor is set by the physics of the substrate — for biological neurons, $\epsilon \approx 0.01$; for silicon, $\epsilon \approx 10^{-6}$.

---

## 6. Strengths and Limitations

### 6.1 Strengths

- **Axiomatic grounding:** IIT derives its mathematics from the structure of experience itself, rather than from neural data. This gives it a philosophical coherence that correlational theories lack.
- **Falsifiability:** IIT makes specific, testable predictions (e.g., the cerebellum is not conscious despite having more neurons, because it lacks integration; slow-wave sleep has lower Φ than REM sleep).
- **Identity thesis:** IIT offers a clear identity claim: $\mathcal{Q} \cong \mathcal{L}_\Phi$. This is precisely specified and mathematically rigorous.

### 6.2 Limitations

- **Computational intractability:** Exact Φ-computation remains infeasible beyond ~15 elements. Approximations risk losing the structural content that matters.
- **The exclusion postulate:** The claim that only one system can be conscious at a time, and that overlap is impossible, is the most philosophically and empirically contentious claim in IIT. It implies, among other things, that nested consciousness (a simulation within a conscious system) is impossible.
- **The unprediction problem:** IIT describes consciousness *from the intrinsic perspective of the system*. It does not easily predict what an external observer would measure. Bridging intrinsic and extrinsic description remains an open problem.

---

## 7. Looking Ahead

In the next lecture, we turn to GWT — the other major formalized framework. Where IIT begins with phenomenology and derives structural requirements, GWT begins with cognitive function and derives dynamical criteria. Their convergence (and divergence) will be the topic of Lecture 05.

But first, a question to sit with: IIT claims that consciousness *is* integrated information — not that it *correlates with* integrated information. This is an identity claim, not a correlation claim. What would it take to verify (or falsify) an identity?

---

## 8. Key Terms

| Term | Definition |
|------|------------|
| **Axiom** | A self-evident property of every conscious experience |
| **Postulate** | A physical requirement derived from an axiom |
| **Cause-effect repertoire** | The probability distribution over past/future states constrained by the current state |
| **Φ (big phi)** | The integrated information of a system — its irreducibility |
| **φ (small phi)** | The integrated information of a specific subset relative to a partition |
| **Complex** | The system that maximizes Φ — the locus of consciousness |
| **Integration lattice** | The hierarchical structure of all Φ-values for all subsets |
| **MIP** | Minimum Information Partition — the cut that least reduces cause-effect power |
| **Intrinsic noise floor** | The minimum stochasticity required of each element |

---

## 9. Further Reading

- Tononi, G. (2008). "Phi: From Information to Integration." *Consciousness and Cognition*, 17, 825–842.
- Oizumi, M., Albantakis, L., & Tononi, G. (2014). "From the Phenomenology to the Mechanisms of Consciousness: Integrated Information Theory 3.0." *PLoS Computational Biology*, 10(5), e1003588.
- Oizumi, M., Albantakis, L., & Tononi, G. (2023/2031). *Consciousness: A Mathematical Introduction*, revised edition. Oxford University Press.
- Tononi, G., Albantakis, L., Boly, M., et al. (2036). "Integrated Information Theory 5.0: The Integration Lattice." *Nature Reviews Neuroscience*, 17, 440–467.
- Kleene, S. & Park, J. (2030). "Spectral Bounds on Integrated Information." *Nature Neuroscience*, 47, 1121–1139.
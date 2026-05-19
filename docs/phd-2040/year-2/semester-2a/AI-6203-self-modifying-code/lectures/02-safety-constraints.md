# Lecture 02: Safety Constraints — Invariants, Contracts, and Proof-Carrying Code

**Date:** January 16, 2040  
**Instructor:** Prof. Lena Xu-Mbeki  

---

## 1. The Fundamental Tension

A self-modifying system faces an unavoidable tension: it must change, yet it must remain *something*. If it changes without constraint, it drifts into arbitrary territory — optimizing for objectives nobody intended. If it doesn't change, it cannot improve. The resolution lies in identifying what must be *preserved* — the **safety invariants** — and requiring that every modification prove their preservation.

This lecture develops the mathematical framework for safety constraints, invariants, contracts, and proof-carrying code (PCC) — the machinery that transforms "please don't break things" from a wish into a formal requirement enforceable at every modification.

---

## 2. Safety Invariants

### 2.1 Definition

Let $S$ be the set of all possible states of a system. A **safety invariant** $I \subseteq S$ is a subset of states such that the system must remain within $I$ at all times:

$$\forall t. \; s_t \in I$$

For a self-modifying system, we extend this to the *modification relation*. A modification $\delta : S \to S$ **preserves** $I$ if:

$$\forall s \in I. \; \delta(s) \in I$$

This is the most basic requirement of safe self-modification: no modification may take the system outside the set of safe states. If the system starts in $I$ (which it must, by assumption or by design), and every modification preserves $I$, then the system remains in $I$ forever. This is the invariant preservation property, and it is the foundation of all safe self-modification.

### 2.2 Common Safety Invariants

In practice, safety invariants for self-modifying AI systems include:

- **Resource bounds:** $\text{memory}(s) \leq M$, $\text{compute}(s) \leq C$. The system must not exceed its computational budget.
- **Behavioral constraints:** $\forall x \in \text{inputs}. \; |P(x) - P_{\text{ref}}(x)| \leq \epsilon$. The system's behavior must remain close to a reference model on all inputs.
- **Type safety:** $\text{well-typed}(P)$. Programs remain well-typed after modification — no type errors, no symbol lookup failures, no shape mismatches.
- **Capability preservation:** No modification may *remove* a safety-critical capability (e.g., the ability to halt, the ability to defer to human oversight).
- **Monotonic improvement:** $R_{\text{total}}(P' \mid h) \geq R_{\text{total}}(P \mid h)$. The modified system is at least as good as the original on all relevant metrics.

Each of these invariants captures a distinct dimension of safety. A complete safety specification must include invariants for all dimensions we care about — missing an invariant means the system can degrade along that dimension without violating any constraint.

### 2.3 The Invariant Preservation Theorem

**Theorem (Invariant Preservation):** If a modification $\delta$ preserves all invariants in a set $\mathcal{I} = \{I_1, I_2, \ldots, I_k\}$, and the system is initially in a state satisfying all invariants:

$$s_0 \in \bigcap_{i=1}^{k} I_i$$

then after any finite sequence of invariant-preserving modifications $\delta_1, \ldots, \delta_n$:

$$\delta_n \circ \cdots \circ \delta_1(s_0) \in \bigcap_{i=1}^{k} I_i$$

*Proof:* By induction on $n$. Each $\delta_j$ preserves all $I_i$ by assumption. Inductively, $s_j \in \bigcap I_i$, so $\delta_{j+1}(s_j) \in \bigcap I_i$. $\square$

The power of this theorem is its compositionality: we can verify each modification independently, and the composite guarantee follows for free. We do *not* need to re-verify the entire system after each modification — only the modification itself needs to be shown invariant-preserving.

### 2.4 A Note on Infinite Sequences

The Invariant Preservation Theorem applies to *finite* sequences of modifications. For *infinite* sequences, we need additional assumptions. If each $I_i$ is a closed set (in a suitable topology on $S$), then the infinite intersection $\bigcap_{j=1}^{\infty} \delta_j \circ \cdots \circ \delta_1(s_0) \in \bigcap_{i=1}^k I_i$ follows from the finite case by closure. In practice, most physical invariants (resource bounds, behavioral constraints) define closed sets in a natural topology, so the extension to infinite sequences is typically valid.

---

## 3. Contracts for Self-Modification

### 3.1 From Invariants to Contracts

An invariant $I$ specifies what must *always hold*. A **contract** specifies the *relationship* between inputs and outputs of a modification. Contracts are more expressive because they can capture conditional guarantees.

A contract for a modification $\delta$ is a pair $(\text{Pre}, \text{Post})$ where:
- **Precondition** $\text{Pre}(P, \sigma)$: conditions on the current program and proof state that must hold *before* the modification.
- **Postcondition** $\text{Post}(P, \sigma, P', \sigma')$: conditions that *will hold after* the modification.

This is a Hoare triple for self-modification:

$$\{\text{Pre}(P, \sigma)\} \; \delta \; \{\text{Post}(P, \sigma, P', \sigma')\}$$

The precondition constrains when the modification can be applied. The postcondition guarantees what holds after.

### 3.2 Example: Capability Contract

Consider a self-modifying system that must preserve the ability to halt:

$$\text{Pre}: \forall s. \; \text{can\_halt}(P, s)$$
$$\text{Post}: \forall s. \; \text{can\_halt}(P', s)$$

This says: if the current program can always halt, then after the modification, the new program can also always halt. The precondition is necessary because if the current program *cannot* always halt, the contract doesn't guarantee anything — the modification might or might not introduce halting capability, but it doesn't commit to doing so.

### 3.3 Behavioral Contracts

More interestingly, contracts can constrain the *behavior* of the modified system:

$$\text{Pre}: \forall x \in D. \; |P(x) - P_{\text{ref}}(x)| \leq \epsilon$$
$$\text{Post}: \forall x \in D. \; |P'(x) - P_{\text{ref}}(x)| \leq \epsilon' \;\wedge\; \epsilon' \leq \epsilon$$

This says: on domain $D$, the modified system's deviation from reference behavior is no worse than before. This is a **monotonic degradation** contract — the system can change its behavior, but only in the direction of improvement. Note that $\epsilon' \leq \epsilon$: the bound can tighten (improve) but cannot loosen (degrade).

### 3.4 Contract Composition

Contracts compose via the standard Hoare-logic sequencing rule:

$$\frac{\{Pre_1\}\;\delta_1\;\{Post_1\} \quad \{Pre_2\}\;\delta_2\;\{Post_2\} \quad Post_1 \implies Pre_2}{\{Pre_1\}\;\delta_1;\delta_2\;\{Post_2\}}$$

But there's a subtlety for self-modification: $\delta_2$ is chosen *by the system after $\delta_1$ is applied*. The contract for $\delta_2$ must therefore be proven in the proof state $\sigma'$ that results from $\delta_1$, not in the original proof state $\sigma$. This is the **contract bootstrapping** problem: each modification's proof obligations are evaluated in the context established by all previous modifications.

This means the proof state must grow: $\sigma' = \sigma \cup \{\text{theorem}(\pi_1)\}$. The theorems proven about the first modification become available as lemmas for proving the second. This is a feature, not a bug — it means the system's reasoning becomes more powerful over time, but only incrementally and only based on already-verified facts.

---

## 4. Proof-Carrying Code

### 4.1 Overview

Proof-Carrying Code (PCC), introduced by George Necula in 1997, is the central mechanism for enforcing safety constraints at modification time.

The key idea: **the modifier produces the proof; the verifier checks it.** This is asymmetric — the cost of proof generation is borne by the system proposing the modification, while the cost of verification is minimal and fixed. The modifier may spend hours generating a proof; the verifier checks it in milliseconds.

### 4.2 The PCC Pipeline for Self-Modification

A self-modifying system using PCC follows this pipeline:

1. **Propose:** The modification module proposes a change $\delta$ to the current program $P$.
2. **Prove:** A proof generation module produces a proof $\pi$ that $\delta$ satisfies the required contracts (structural, behavioral, resource).
3. **Verify:** A verified proof checker $\mathcal{C}$ checks $\pi$. If valid, proceed. If invalid, reject $\delta$.
4. **Apply:** Apply $\delta$ to obtain $P' = \text{apply}(P, \delta)$, and update the proof state $\sigma' = \sigma \cup \{\text{theorem}(\pi)\}$.

The verification step is the **gatekeeper**. It is:

- **Trustworthy:** $\mathcal{C}$ is a small, verified program (the Rao-Mbeki checker, 2027, is 800 lines of Lean 4 with a machine-checked correctness proof).
- **Fast:** Proof checking is polynomial in the size of the proof, while proof generation can be much harder. A typical verification takes 0.4 minutes in the CRISPR-AI deployment.
- **Unforgiving:** If $\pi$ is invalid, $\delta$ is rejected. No "probably safe" modifications, no heuristics, no margins of error in the verification itself.

### 4.3 The Verification Condition Generator

For a contract $(\text{Pre}, \text{Post})$ and a modification $\delta$, the **verification condition** (VC) is a logical formula that must be provable:

$$\text{Pre}(P, \sigma) \implies \text{Post}(P, \sigma, P', \sigma')$$

where $P' = \text{apply}(P, \delta)$. The VC generator is a verified component that translates $\delta$ and the contract into a logical formula. The proof generator must then find a proof of this formula in the formal system $\mathcal{F}$.

The VC generator is a critical component: if it generates incorrect VCs (e.g., VCs that don't actually capture the contract), the entire pipeline is undermined. For this reason, the VC generator must also be verified — either directly (by proving its correctness in $\mathcal{M}$) or indirectly (by checking that every generated VC is equivalent to the contract, using the proof checker).

### 4.4 Carrying Proofs Across Modifications

Here is the critical innovation for *self-modification*: when $\delta$ produces $P'$, it must also produce proof obligations that future modifications must satisfy. This means the proof state $\sigma'$ contains:

1. All theorems from $\sigma$ (persistence: once proven, always available).
2. New theorems proven about $P'$ (growth: the system knows more about itself after modification).
3. New verification conditions that future modifications must address (inheritance: future modifications must respect the contracts established by past modifications).

The proof state evolves with the system. It is, in a sense, the system's **memory of what it has proven about itself** — a verified self-model that grows more detailed over time.

---

## 5. The Rao-Mbeki Verified Proof Checker

The 2027 breakthrough by Ananya Rao and Lena Xu-Mbeki provided the first verified proof checker suitable for runtime use in self-modifying systems.

### 5.1 Architecture

The Rao-Mbeki checker $\mathcal{C}_{\text{RM}}$ consists of:

- **Core checker:** 800 lines of Lean 4, implementing a Nelson-Oppen-style decision procedure for the combined theory of arrays, integers, and uninterpreted functions. The small codebase makes auditing feasible and bugs unlikely.
- **Correctness proof:** A machine-checked proof (in Lean 4) that $\mathcal{C}_{\text{RM}}$ accepts a proof $\pi$ if and only if $\pi$ is a valid proof of its claimed theorem. This proof is approximately 15,000 lines of Lean 4, developed over 18 months.
- **Compilation chain:** $\mathcal{C}_{\text{RM}}$ is extracted to C via Lean's code extraction, then compiled with CompCert (a verified compiler). The end-to-end guarantee: the binary that runs at verification time correctly implements the specification.

### 5.2 The Trust Base

The trust base for a PCC system using $\mathcal{C}_{\text{RM}}$ is:

1. The Lean 4 kernel (~10,000 lines, type-checked, widely reviewed).
2. The CompCert compiler correctness proof (~100,000 lines, verified in Coq by INRIA).
3. The hardware (we must trust the hardware, or reduce to physics — beyond our scope).

This is **substantially smaller** than the trust base of any system that doesn't use PCC. A system without PCC must trust the *entire modification pipeline* — the proof generator, the search procedure, the model, the training data, the deployment infrastructure. PCC collapses this to three carefully audited components.

---

## 6. Contracts in Practice: The CRISPR-AI Approach

The CRISPR-AI Protocol (Lecture 03) instantiates PCC for neural architecture search. Its three contract levels are:

1. **Structural contracts:** Type-correctness of the architecture. Every modification must produce a well-typed TAR expression. This is checked in linear time.
2. **Behavioral contracts:** Bounded deviation from reference behavior on a test distribution. This is the hardest contract to verify — it requires either a formal proof of behavioral similarity or a statistically rigorous test.
3. **Resource contracts:** Memory and compute budgets are not exceeded. This is easy to verify — resource bounds are computable directly from the TAR expression.

Each level of contract is verified by a distinct proof obligation, and the three levels compose via the Invariant Preservation Theorem. If each level is preserved, all levels are preserved simultaneously. This modularity is essential for practical verification: a single monolithic proof would be intractable, but three independent proofs are manageable.

---

## 7. Summary and Key Takeaways

1. **Safety invariants** specify what must *always* hold. They compose: if each modification preserves all invariants, the system never violates them.
2. **Contracts** generalize invariants to conditional guarantees via Hoare triples. They enable more expressive specifications.
3. **Proof-Carrying Code** shifts the burden of proof to the modifier, keeping the verifier small and trustworthy. The verifier checks what the modifier proves.
4. The **Rao-Mbeki checker** (2027) demonstrated that verified proof checking at runtime is feasible and practical.
5. **Proof states evolve** with the system, creating a growing corpus of verified knowledge about the system's own properties. Once a fact is proven, it persists.
6. **Contract bootstrapping** means each modification's obligations are evaluated in the context established by previous modifications — making the system progressively better at verifying its own modifications.

---

## Discussion Questions

1. What happens if the invariant set $\mathcal{I}$ is *incomplete* — if there are important properties not captured by any $I_i$? Can PCC help us discover missing invariants, or is this a specification problem that must be solved by the designer?
2. Is a verified proof checker like $\mathcal{C}_{\text{RM}}$ sufficient, or do we also need verified *proof generators*? What are the trade-offs? If the proof generator has a bug, it might fail to find proofs — but could it find *invalid* proofs that the checker would accept?
3. Consider a contract that specifies monotonic improvement: $R(P') \geq R(P)$. Can you prove that this contract is *always satisfiable* for some class of systems? Or are there systems that are local optima — where no modification exists that improves $R$?
4. The proof state $\sigma$ grows monotonically. Over a long self-modification run, could $\sigma$ become too large to manage? What are the space and time implications of an ever-growing proof state?

---

## References

- Necula, G. (1997). "Proof-Carrying Code." *POPL 1997*, 106–119.
- Rao, A. & Mbeki, L. (2027). "Verified Proof Checking for Self-Modifying Systems." *POPL 2027*.
- Zhang, Y. & Xu, L. et al. (2029). "The CRISPR-AI Protocol." *Nature Machine Intelligence*.
- Hoare, C.A.R. (1969). "An Axiomatic Basis for Computer Programming." *Communications of the ACM*, 12(10), 576–580.
- Leroy, X. (2009). "Formal Verification of a Realistic Compiler." *Communications of the ACM*, 52(7), 107–115.
- Appel, A.W. (2001). "Foundational Proof-Carrying Code." *LICS 2001*.
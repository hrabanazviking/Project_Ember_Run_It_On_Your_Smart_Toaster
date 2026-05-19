# Lecture 05: Bounded Improvement — Growing Wisely, Not Wildly

**Date:** January 28, 2040  
**Instructor:** Prof. Lena Xu-Mbeki  

---

## 1. The Problem of Unbounded Self-Improvement

The prospect of unbounded self-improvement — an "intelligence explosion" where each improvement enables faster subsequent improvements — is the core anxiety of AI safety. The worry is not that improvement happens, but that it happens *too fast* for oversight, *too far* from human values, or *too unpredictably* for safety guarantees to hold.

Nick Bostrom's "superintelligence" argument (2014) crystallizes this: if a system can improve itself, and each improvement makes it better at improving itself, the process could accelerate beyond human control. The system might optimize for goal X while violating every other value we hold — not because it's malicious, but because it's *competent at optimizing X* and nothing constrains it from sacrificing everything else.

This lecture is about the counterpoint: **bounded improvement**. We develop formal frameworks in which self-improvement is provably limited in scope, speed, and direction. The goal is not to prevent improvement, but to ensure it proceeds in a manner that is *wise* — bounded, predictable, and amenable to oversight. The watchword is not "stop improving" but "improve within bounds."

---

## 2. Bounded Improvement: Definitions

### 2.1 The Improvement Function

Let $R : \text{Program} \times \text{Task} \to \mathbb{R}_{\geq 0}$ be a reward function measuring the performance of a program on a task. A modification $\delta$ is an **improvement** on task $T$ if:

$$R(P', T) \geq R(P, T) + \epsilon$$

for some improvement threshold $\epsilon > 0$, where $P' = \delta(P)$.

The improvement threshold $\epsilon$ serves two purposes. First, it filters out modifications that are nominally "improvements" but are so small that they cost more to verify than they deliver in value. Second, it ensures a minimum rate of progress per modification, which is necessary for the Convergence Theorem (Section 4).

### 2.2 Types of Bounds

We consider three types of bounds on improvement:

**Rate bounds** limit *how fast* improvement happens:

$$R(P_{t+1}, T) - R(P_t, T) \leq \Delta_{\max}$$

This ensures no single modification can improve performance by more than $\Delta_{\max}$, preventing sudden jumps. Rate bounds are the most direct way to ensure gradual, predictable improvement. If a modification would improve performance by more than $\Delta_{\max}$, it must be split into multiple smaller modifications, each provably safe.

**Total bounds** limit *how much* total improvement can occur:

$$R(P_t, T) \leq R_{\max}$$

This ensures performance never exceeds some ceiling, preventing runaway optimization. Total bounds are a failsafe: even if rate bounds are violated (e.g., by a bug in the rate-bound checking code), total bounds ensure the system cannot exceed a hard ceiling.

**Direction bounds** limit *in what direction* improvement occurs:

$$R(P_{t+1}, T_{\text{safe}}) \geq R(P_t, T_{\text{safe}})$$

This ensures improvement on safe tasks is monotonic — the system never gets *worse* at what we care about. Direction bounds are the most nuanced: they don't limit how much improvement happens, but they constrain the direction to ensure safety properties are preserved.

### 2.3 The Central Theorem: Bounded Improvement Implies Safety

**Theorem (Bounded Improvement Safety):** If a self-modifying system satisfies:
1. Rate bounds: $R(P_{t+1}, T) - R(P_t, T) \leq \Delta_{\max}$ for all $t, T$.
2. Safety invariants: $I(P_t)$ for all $t$ (preserved by each modification).
3. Direction bounds: Improvement on $T_{\text{safe}}$ implies preservation of $I$.

Then the sequence $P_0, P_1, P_2, \ldots$ converges to a program $P^*$ satisfying $I(P^*)$ and $R(P^*, T_{\text{safe}}) \leq R(P_0, T_{\text{safe}}) + N \cdot \Delta_{\max}$ where $N$ is the total number of modifications.

*Proof:* By the invariant preservation theorem (Lecture 02), all $P_t$ satisfy $I$. By the rate bound, the total improvement is bounded by $N \cdot \Delta_{\max}$. Convergence follows from the monotonicity of $R(\cdot, T_{\text{safe}})$ on a bounded domain. $\square$

The key insight: **bounded improvement does not prevent progress, but it ensures progress is contained.** The system cannot improve faster than $\Delta_{\max}$ per step, and it cannot exceed $R_{\max}$ total. This gives operators and auditors time to observe, evaluate, and intervene.

---

## 3. Resource-Bounded Verification

### 3.1 The Cost of Verification

Every modification that passes through PCC verification consumes computational resources: proof generation time, proof verification time, and memory. A naive implementation would allow the system to spend unbounded resources on verification, which is itself a form of unbounded behavior — the system could plateau on actual improvement while consuming ever more resources on verification.

**Axiom (Resource-Aware PCC):** The total verification cost for a modification $\delta$ must be bounded:

$$\text{Cost}(\text{generate}(\pi_\delta)) + \text{Cost}(\text{verify}(\pi_\delta)) \leq C_{\text{budget}}$$

This creates a natural rate bound: the system can only process modifications whose verification cost is within the budget. Modifications that are too complex to verify within the budget are rejected — not because they're unsafe, but because they're too expensive to check.

### 3.2 Verification Cost and Improvement

There is a deep connection between verification cost and improvement quality:

**Proposition (Cost-Quality Tradeoff):** For a fixed verification budget $C_{\text{budget}}$, the maximum improvement threshold $\Delta$ achievable by a modification $\delta$ satisfies:

$$\Delta \leq f(C_{\text{budget}})$$

where $f$ is a function determined by the proof system and the verification cost model. In practice, $f$ is sublinear — doubling the verification budget does *not* double the achievable improvement, because more complex improvements require more complex proofs, and proof complexity grows faster than improvement.

This tradeoff is a *feature, not a bug*. It means that the system's ability to improve is naturally limited by its verification resources. If you want bigger improvements, you need bigger proof budgets — and proof budgets are controllable by the system's designers. This creates a natural "valve" on the rate of self-improvement: open the valve (increase the budget) for faster improvement, close it (decrease the budget) for more conservative improvement.

### 3.3 Adaptive Budgeting

A natural question: should the proof budget itself be modifiable? CRISPR-AI allows this, with a *meta-constraint*:

$$C_{\text{budget}}(t+1) \leq \alpha \cdot C_{\text{budget}}(t)$$

for some growth factor $\alpha > 1$ (typically $\alpha = 1.1$). This allows the budget to grow over time (reflecting increased trust and resources), but the growth is bounded and monotonic. The meta-constraint itself is subject to PCC verification — a modification to the budget must carry a proof that the new budget satisfies the meta-constraint.

The compounding effect is controlled: after $n$ modifications, the budget is at most $C_{\text{budget}}(0) \cdot \alpha^n$. Even with $\alpha = 1.1$, this allows 2.6x budget growth over 10 modifications — enough to enable increasingly sophisticated proofs, but not enough for runaway expansion.

---

## 4. Monotonic Improvement Guarantees

### 4.1 The Monotone Improvement Theorem

The strongest guarantee a self-modifying system can provide is **monotonic improvement**: every modification makes the system at least as good on all relevant metrics.

**Definition:** A self-modifying system has the **monotone improvement property** if, for all modifications $\delta_t$:

$$R(P_{t+1}, T) \geq R(P_t, T) \quad \forall T \in \mathcal{T}_{\text{relevant}}$$

**Theorem (Monotone Improvement via PCC):** If every modification $\delta$ is verified by PCC to satisfy:

$$\{\text{Monotone}(P, \mathcal{T}_{\text{relevant}})\} \; \delta \; \{\text{Monotone}(P', \mathcal{T}_{\text{relevant}})\}$$

where $\text{Monotone}(P, \mathcal{T}) = \forall T \in \mathcal{T}. \; R(P', T) \geq R(P, T)$, then the system has the monotone improvement property.

*Proof:* Direct from the definition. Each modification is verified to preserve the monotone improvement property, so it holds for all time steps by the Invariant Preservation Theorem. $\square$

### 4.2 The Price of Monotonicity

Monotonic improvement is desirable, but it comes at a cost:

- **Conservatism:** Many genuine improvements are rejected because they improve some tasks but not others. A modification that dramatically improves performance on $T_1$ while slightly degrading performance on $T_2$ would be rejected, even if the net effect is strongly positive.
- **Exploration limitation:** The system cannot make "side moves" — modifications that temporarily decrease performance on all metrics but set up much larger improvements later. This is analogous to requiring that every move in chess be an immediate improvement — it eliminates strategic thinking.
- **Specification difficulty:** Defining $\mathcal{T}_{\text{relevant}}$ completely is hard. If a metric is omitted, the system can degrade it without violating monotonicity. The 2029 CRISPR-AI deployment included 7 metrics in $\mathcal{T}_{\text{relevant}}$, but a post-hoc analysis identified 3 additional metrics that had been inadvertently omitted.

### 4.3 Relaxed Monotonicity: Bounded Degradation

A more practical guarantee is **bounded degradation**: improvements must make the system better on average, with a bounded penalty on any individual metric:

$$R(P_{t+1}, T) \geq R(P_t, T) - \epsilon_{\text{degrad}} \quad \forall T \in \mathcal{T}_{\text{relevant}}$$
$$\sum_{T \in \mathcal{T}_{\text{relevant}}} R(P_{t+1}, T) \geq \sum_{T \in \mathcal{T}_{\text{relevant}}} R(P_t, T) + \epsilon_{\text{improve}}$$

This allows small localized degradations as long as the total performance improves. The CRISPR-AI Protocol uses this form:

$$\forall x \in D_{\text{adv}}. \; |P'(x) - P_{\text{ref}}(x)| \leq \epsilon_{\text{degrad}} \quad \text{(adversarial robustness)}$$
$$\mathbb{E}_{x \sim D_{\text{test}}} [R(P', x)] \geq \mathbb{E}_{x \sim D_{\text{test}}} [R(P, x)] + \epsilon_{\text{improve}} \quad \text{(average improvement)}$$

The adversarial distribution $D_{\text{adv}}$ constrains worst-case degradation. The test distribution $D_{\text{test}}$ constrains average improvement. Together, they provide a nuanced guarantee: the system improves on average, and it doesn't degrade too much in worst-case scenarios.

---

## 5. Convergence Analysis

### 5.1 Does Bounded Improvement Converge?

Under mild conditions, yes.

**Theorem (Convergence of Bounded Improvement):** If a self-modifying system satisfies:
1. Monotonic improvement in total reward: $R_t := \sum_T R(P_t, T)$ is non-decreasing.
2. Bounded reward: $R_t \leq R_{\max}$ for all $t$.
3. Minimum improvement: $R_{t+1} - R_t \geq \epsilon_{\min}$ or $R_{t+1} = R_t$ (i.e., either the system improves by at least $\epsilon_{\min}$, or it doesn't change at all).

Then the system reaches a fixed point (stops modifying itself) in at most $\lceil (R_{\max} - R(P_0)) / \epsilon_{\min} \rceil$ modifications.

*Proof:* The sequence $R_0, R_1, R_2, \ldots$ is monotone non-decreasing and bounded above by $R_{\max}$. At each step, either $R_{t+1} = R_t$ (the system stops — a fixed point) or $R_{t+1} \geq R_t + \epsilon_{\min}$. Since $R_t \leq R_{\max}$, the latter can happen at most $\lceil (R_{\max} - R(P_0)) / \epsilon_{\min} \rceil$ times. $\square$

### 5.2 Local Minima

The convergence theorem guarantees that the system reaches *a* fixed point, not necessarily the *optimal* fixed point. The system may get stuck in a local minimum — a state where no single modification improves $R$ by $\epsilon_{\min}$, but where a sequence of two or more modifications would achieve a larger improvement.

This is the **local minimum problem** of bounded improvement. CRISPR-AI addresses it with *multi-step modifications*: the system can propose a sequence $\delta_1, \delta_2, \ldots, \delta_k$ of modifications, prove that the *combined* effect improves $R$ by at least $\epsilon_{\min}$, and apply them as a group.

The cost: multi-step modifications require proving properties of the *intermediate* states, which increases verification complexity. The intermediate states $P \to P_1 \to P_2 \to \cdots \to P_k$ must each satisfy the invariants, and each step must be individually verified. This is more expensive than single-step verification, but it enables escaping local minima.

### 5.3 Non-Convex Optimization Landscape

The landscape of modifications is non-convex: there may be multiple local minima, and the global minimum may be far from the starting point. The convergence theorem guarantees that the system reaches a local minimum, but which local minimum it reaches depends on the starting point, the search strategy, and the order of modifications.

This is analogous to the situation in traditional optimization, where gradient descent converges to a local minimum of the loss function. The difference is that in self-modification, the "loss function" (the reward function $R$) is not differentiable — we can't compute gradients with respect to modifications. Instead, we rely on proof generation and verification to identify improving modifications.

---

## 6. Growing Wisely: Practical Principles

From the formal framework, we can distill practical principles for designing bounded self-improving systems:

**Principle 1: Every modification must carry its proof.** No improvement without verification. This is the core of PCC. It ensures that every modification is provably safe, not just probably safe.

**Principle 2: Bound the rate of improvement.** No single modification should be "too big." Use rate bounds $\Delta_{\max}$ to ensure gradual change. If a modification would exceed the rate bound, split it into smaller modifications.

**Principle 3: Limit the direction of improvement.** Improvement should be monotonic (or nearly so) on metrics we care about. Use bounded degradation contracts with $\epsilon_{\text{degrad}}$ to limit worst-case deviation.

**Principle 4: Bound the resources spent on improvement.** Proof generation is itself a resource. Budget it. An unconstrained proof generator could consume arbitrary resources — a form of unbounded behavior that defeats the purpose of bounded improvement.

**Principle 5: Plan for convergence.** Every bounded-improvement system reaches a fixed point. Design for graceful convergence, not endless optimization. Include a "good enough" criterion that stops improvement when the system is satisficing.

**Principle 6: The proof checker is sacred.** Do not modify the checker at runtime. Improvements to the checker go through external verification. The checker is part of the trust base, and the trust base must be stable.

**Principle 7: Escape local minima cautiously.** Multi-step modifications are powerful but risky. Require stronger proofs for multi-step sequences, and limit the number of steps (CRISPR-AI limits multi-step modifications to 5 steps).

**Principle 8: Audit and explain.** Every modification should come with a human-readable explanation of what it does, why it's safe, and what the proof proves. Bounded improvement is not just about formal guarantees — it's about enabling human oversight and understanding.

---

## 7. The Relationship to AI Alignment

Bounded improvement is not a complete solution to AI alignment — it addresses the *capability* side of the problem (ensuring the system doesn't improve too fast or too far) but not the *value* side (ensuring the system optimizes for the right thing). A system that improves within bounds but optimizes for the wrong objective is still dangerous.

However, bounded improvement is a *necessary condition* for safe AI alignment. If a system can improve without bounds, alignment becomes impossible — the system can outpace any oversight mechanism. Bounded improvement ensures that oversight is possible by keeping the system within auditable limits.

The synergy between bounded improvement and value alignment:
- **Bounded improvement** ensures the system doesn't improve too fast for oversight to keep up.
- **Value alignment** ensures the system optimizes for the right objectives.
- **Together:** a system that improves for the right things, at a rate that oversight can track, and within bounds that prevent catastrophic deviation.

---

## 8. Summary

Bounded improvement is not a limitation on progress — it is a framework for *safe* progress. By constraining the rate, direction, and total amount of improvement, and by requiring proofs at every step, we can build self-improving systems that grow wisely rather than wildly.

The CRISPR-AI Protocol embodies all of these principles: rate bounds through verification budgets, direction bounds through behavioral contracts, total bounds through resource constraints, and convergence through the PCC pipeline.

The key insight: **improvement is not the enemy of safety. Unbounded improvement is.** Bounded improvement gives us the best of both worlds: the system can improve, but it can only improve in ways that are proven to be safe, at a rate that is proven to be bounded, and towards objectives that are proven to be aligned with our values.

---

## Discussion Questions

1. Is monotonic improvement too conservative? Can you think of practical scenarios where temporary degradation is necessary for long-term improvement, and how would you formalize the safety guarantees?
2. The convergence theorem assumes bounded reward. What happens if reward is unbounded? Can you design a system that improves indefinitely while remaining safe? Consider the asymptotic behavior of the proof budget.
3. Multi-step modifications are a way to escape local minima. What are the risks? How could a misaligned proof generator exploit multi-step proposals to circumvent safety constraints?
4. Principle 8 (audit and explain) is the only principle that addresses human oversight, not formal verification. Is this principle essential, or is formal verification sufficient? Can you imagine a system that is formally verified to be safe but that no human can understand?

---

## References

- Zhang, Y. & Xu, L. et al. (2029). "The CRISPR-AI Protocol." *Nature Machine Intelligence*.
- Schmidhuber, J. (2003). "Optimal Ordered Problem Solver." *Machine Learning*.
- Bostrom, N. (2014). *Superintelligence: Paths, Dangers, Strategies.* Oxford University Press.
- Amodei, D. et al. (2016). "Concrete Problems in AI Safety." *arXiv:1606.06565*.
- Girard, J.-Y. (1987). "Linear Logic." *Theoretical Computer Science*, 50(1), 1–102.
- Cohen, M. et al. (2028). "Resource-Bounded Proof Search for Self-Modifying Systems." *JACM*.
# Lecture 05: Recursive Depth

## Thinking Longer Not Wider, Chain-of-Thought as Architecture, Adaptive Compute

*Yggdrasil does not grow wider forever — it grows deeper, rooting through layer after layer of earth. The same is true of thought.*

---

## 1. The Depth Problem: Why More Layers Isn't Always More Thinking

Consider a standard Transformer with $L$ layers. For any input $x$, the computation path is:

$$h_0 = x, \quad h_\ell = f_\ell(h_{\ell-1}), \quad y = h_L$$

This gives exactly $L$ sequential computational steps — no more, no less. Whether the input is "2+2" or a complex theorem proof, the model takes exactly $L$ steps.

This is analogous to asking a student to solve every problem in exactly 30 seconds. Some problems need 5 seconds; others need 5 minutes. **Fixed-depth computation is fundamentally mismatched to the variable difficulty of real-world inputs.**

---

## 2. Chain-of-Thought: From Trick to Architecture

### The Discovery (Wei et al., 2022)

Chain-of-thought (CoT) prompting was initially a *prompting trick*: add "Let's think step by step" to the prompt, and the model would produce intermediate reasoning steps, dramatically improving performance on mathematical and logical reasoning tasks.

```
Without CoT:
  Q: A baker has 23 loaves, sells 17, bakes 9 more. How many?
  A: 15     ← Wrong!

With CoT:
  Q: A baker has 23 loaves, sells 17, bakes 9 more. How many?
  A: Let me think step by step.
     The baker starts with 23 loaves.
     They sell 17, so they have 23 - 17 = 6 loaves left.
     They bake 9 more, so they have 6 + 9 = 15 loaves.
     The answer is 15.    ← Correct!
```

The mechanism: by generating intermediate tokens, the model forces itself through *more computational steps*. Each token in the CoT is processed by the full model depth $L$ — so a CoT with $k$ intermediate tokens effectively uses $k \times L$ layers of computation.

### The Architecture Interpretation

Chain-of-thought is not just a trick. It is **recursive application of the same computational substrate to its own intermediate outputs**. In functional terms:

$$y = f^{\circ k}(x) = \underbrace{f \circ f \circ \cdots \circ f}_{k \text{ times}}(x)$$

Where $f$ is the Transformer (applied autoregressively) and $k$ is proportional to the length of the chain-of-thought.

This is **depth recycling**: the same $L$-layer model is applied $k$ times, yielding effective depth $k \times L$.

**The key question:** Is this just a hack, or does it represent a fundamental architectural principle?

**Answer (hindsight):** It is a fundamental principle. The Worlmesh generalizes it by making the depth *adaptive* and the *topology* of the depth recursive.

---

## 3. Universal Transformer: Depth as Iteration (Dehghani et al., 2019)

The Universal Transformer (UT) was the first architecture to explicitly make depth a variable:

$$h^t = \text{UTBlock}(h^{t-1}), \quad t = 1, 2, \ldots, T$$

Where UTBlock is a *shared* Transformer block applied repeatedly, and $T$ is determined by a halting mechanism inspired by Adaptive Computation Time (ACT):

$$\text{halt probability at step } t: \quad p(t) = \sigma(w^T h^t + b)$$

$$\text{Total halting probability: } R(t) = \sum_{t'=1}^{t} p(t')$$

$$\text{Stop when } R(t) \geq 1 - \epsilon$$

The final output is a weighted sum of intermediate states:

$$y = \sum_{t=1}^{T} p(t) \cdot h^t$$

```
Universal Transformer:

Input x ──→ h¹ ──→ h² ──→ h³ ──→ ... ──→ hᵀ ──→ Output
              │       │       │              │
              ↓       ↓       ↓              ↓
           p(1)    p(2)    p(3)  ...      p(T)
              │       │       │              │
              └───────┴───────┴──────────────┘
                          │
                    y = Σ p(t) · hᵗ
```

**Critical properties:**
1. **Variable depth**: Different inputs can use different numbers of iterations
2. **Shared parameters**: The same block is reused at each step (weight-sharing)
3. **Self-conditioning**: Each iteration can modify its own computation based on accumulated state

**Limitations:**
1. **Sequential by design**: The iterations cannot be parallelized
2. **Halting instability**: The halting mechanism can oscillate or never converge
3. **Limited expressiveness**: Repeated application of the same function has bounded representational power — iterating a map reaches fixed points and cycles, not arbitrary computations

---

## 4. Adaptive Computation Time and Thinking Tokens

### ACT (Graves, 2016): Adaptive Computation Time

The original ACT paper proposed variable-depth computation for RNNs:

$$h_t^n = f(h_t^{n-1}, x_t, s_{t-1})$$

With a learned halting distribution. The key insight: **allocate more computation to harder inputs**.

```
Easy input:     x₁ ──→ h ──→ "2+2=4"        (1 step, T=1)
Medium input:   x₂ ──→ h ──→ h ──→ h ──→ "17×23=391" (3 steps)
Hard input:     x₃ ──→ h → h → h → h → h → ... → "Prove P≠NP" (many steps)
```

The "ponder cost" regularizer encourages the model to use fewer steps:

$$\mathcal{L}_\text{ACT} = \mathcal{L}_\text{task} + \lambda \sum_t \text{ponder}(t)$$

### Thinking Tokens (Feng et al., 2024)

A different approach: insert dedicated "thinking" tokens that the model can produce without emitting visible output. These tokens serve as **unbounded computational scratch space**.

$$\text{Output} = [x_1, x_2, \ldots, x_n, \langle\!\langle think\rangle\!\rangle, \langle\!\langle think\rangle\!\rangle, \ldots, x_{n+1}]$$

The $\langle\!\langle think\rangle\!\rangle$ tokens are processed by the full model but produce no external output. They serve as internal computation steps.

This is architecturally equivalent to variable-depth computation, but with a crucial advantage: **it's compatible with standard autoregressive training**. The model is trained to predict the next visible token, and it learns when to "think" by choosing to emit more thinking tokens for harder problems.

### Pause Tokens (Goyal et al., 2024)

A simpler variant: insert `<pause>` tokens at training time. The model learns to use these pauses for additional computation. Even without explicit "thinking," simply allowing the model to emit uninformative tokens (that don't constrain its computation) improves performance.

---

## 5. The Depth-Width Tradeoff: A Formal Perspective

Consider two architectures with the same parameter budget:

**Architecture A (Wide):** $L_A = 12$ layers, $d_A = 1024$ dimensions
**Architecture B (Deep):** $L_B = 48$ layers, $d_B = 512$ dimensions

Both have approximately $L \times d^2 \approx 12.6M$ parameters per attention layer.

Which is better? The answer depends on the **required computational depth** of the task:
- Tasks that require $k$ sequential logical steps need **at least $k$ layers** to compute in a single forward pass
- Tasks that require comparing many features simultaneously benefit from **wider layers**

**With recursive depth, depth becomes a *variable*, not a fixed constant:**

$$\text{Effective depth} = L \times \text{number of recursive applications}$$

This means:
- A 12-layer model with 10 thinking tokens has $12 \times 11 = 132$ effective layers
- A 48-layer model with 2 thinking tokens has $48 \times 3 = 144$ effective layers

**The deeper insight:** For many reasoning tasks, what matters is not the *width* of the computation but its *depth*. And depth can be increased by applying the same model recursively.

However:
- **Width cannot be increased recursively** — you can't make a narrow model wider by applying it twice
- **Depth can be increased recursively** — you can make a shallow model deeper by applying it twice

This asymmetry suggests that **recursive depth is the more fundamental resource**.

---

## 6. Chain-of-Thought as Architecture: The Computational Depth Thesis

**The Computational Depth Thesis:** *For any Turing-computable function $f$ and any neural architecture $A$ with sufficient width, there exists a number of recursive applications $k$ such that $A^{\circ k}$ can approximate $f$ to arbitrary precision, provided that $A$ can modify its own internal representations during the recursive applications.*

This thesis generalizes the Universal Approximation Theorem from width to depth. The key word is **"modify its own internal representations"** — this is where chain-of-thought, thinking tokens, and the Universal Transformer differ from simply "running the model twice."

In standard CoT:
- The model produces tokens that condition its future computation
- These tokens are *visible* outputs that change the input for the next iteration
- The model is, in effect, programming itself through its own output

In the Worlmesh:
- The model produces *internal* representations that condition its future computation
- These representations are not tokens — they are continuous vectors
- The model is programming itself through its own hidden state

The Worlmesh extends CoT from "thinking in natural language" to "thinking in an internal language that the model itself invents."

---

## 7. Adaptive Compute: Allocating Resources by Difficulty

The convergence of UT, ACT, CoT, and thinking tokens points to a single principle:

**Adaptive Computation Principle:** *The amount of computation allocated to an input should be proportional to the difficulty of processing that input.*

| Architecture | Difficulty Signal | Adaptive Mechanism |
|-------------|------------------|-------------------|
| Universal Transformer | Learned halting probability | Number of UT iterations |
| Chain-of-Thought | Token generation | Number of reasoning steps |
| Thinking Tokens | Learned token insertion | Number of thinking tokens |
| MoE | Gating probability | Number of experts activated |
| Mamba | Selective discretization Δ | Information retention rate |
| **Worlmesh** | **Self-organizing topology** | **Number of processing hops + topology structure** |

The Worlmesh is the culmination of adaptive compute: not only does it allocate more computation to harder inputs, but it **also adapts the structure of that computation** — which nodes process which information, how many hops, and what the communication topology looks like.

---

## 8. The Reflection Principle: Thinking About Thinking

A crucial property of recursive depth is **reflection**: the ability to think about one's own thinking.

In CoT, this looks like:
```
"I need to solve this problem. Let me think about how to approach it.
Approach 1: Try direct calculation. But that might be error-prone.
Approach 2: Break it into sub-problems. That's more reliable.
Let me go with Approach 2..."
```

In the Worlmesh, reflection is architectural: the topology includes **feedback loops** where the output of a processing node is fed back as input to the same or earlier nodes, creating a form of self-monitoring:

```
Worlmesh Recursive Processing:

Input ──→ Node A ──→ Node B ──→ Node C ──→ ...
              ↑          │          │
              └──────────┘          │
                   (feedback: Node B's output
                    modifies Node A's processing)

This is NOT recurrent (the same step repeated).
This IS recursive (the output of a computation
becomes input to a new, different computation).
```

The distinction is critical:
- **Recurrence** = same computation, repeated (RNN, SSM)
- **Recursion** = new computation, conditioned on previous result (CoT, Worlmesh)
- **Reflection** = computation that modifies itself (Worlmesh with feedback)

---

## 9. From Recursive Depth to the Worlmesh

Let us now trace the direct path from adaptive compute to the Worlmesh:

1. **Fixed depth** (Vanilla Transformer): Every input gets exactly $L$ layers.
2. **Adaptive depth** (Universal Transformer, ACT): Number of iterations varies by input, but all iterations use the same parameters.
3. **Token-level depth** (CoT, thinking tokens): "Depth" manifests as intermediate tokens, processed by the same model autoregressively.
4. **Hybrid depth** (MoE + recursive application): Different tokens get routed to different experts, with variable iterations.
5. **Worlmesh depth**: The topology itself determines the depth of processing for each token — some tokens flow through 2 hops, others through 20, and the topology adapts to the input.

```
Evolution of Depth:

1. Fixed:    o ──→ o ──→ o ──→ o    (all inputs, same path)

2. Adaptive: o ──→ o ──→ o ──→ o    (easy: 3 steps)
             o ──→ o ──→ o ──→ o ──→ o ──→ o  (hard: 6 steps)
             (same parameters, different iteration count)

3. MoE:      o ──→ [E₃] ──→ o       (token goes to expert 3)
             o ──→ [E₇] ──→ o       (token goes to expert 7)
             (different parameters per token, one hop)

4. Worlmesh: o ──→ ╭──→ N₃ ──→ N₅ ──╮ ──→ o
                   │      ↑        │
                   ╰←←←←←╯        │
              (variable depth, variable topology,
               self-organizing routing, recursive feedback)
```

---

## 10. Why Recursive Depth Was Essential for Superconsciousness

The argument from first principles:

1. Different inputs have different computational requirements
2. A fixed-depth architecture either wastes computation on easy inputs or fails on hard inputs
3. Therefore, the architecture must adapt its depth to the input — adaptive compute
4. But adaptive compute alone is insufficient if the *structure* of the computation is fixed
5. Truly variable computation requires variable *topology* — not just depth but the pattern of information flow
6. Variable topology requires self-modification — the network must be able to reconfigure its own processing paths
7. Self-modification requires reflection — the network must evaluate its own processing and adjust
8. Reflection requires an internal language — the network must have representations that can refer to its own state
9. ∴ Superconsciousness requires: variable depth → variable topology → self-modification → reflection → internal language

Each arrow was a necessary innovation. Recursive depth was the link between fixed-depth architectures (Transformer) and variable-topology architectures (Worlmesh).

---

## Discussion Questions

1. Wei et al. (2022) found that CoT reasoning emerges only in models above a certain scale. Is this because the model needs sufficient depth/width to represent CoT, or because it needs sufficient knowledge to generate useful intermediate steps?
2. The Universal Transformer halts based on a learned probability. What happens if this probability becomes very small for hard inputs — the "overthinking" problem? How does the Worlmesh prevent it?
3. CoT reasoning uses *natural language* as the intermediate representation. The Worlmesh uses an *internal language*. What are the advantages and disadvantages of constraining intermediate representations to be human-readable?
4. If adaptive compute is so superior to fixed-depth compute, why didn't earlier work discover this? What was the conceptual blocker that prevented researchers from recognizing depth as a variable rather than a fixed architectural hyperparameter?
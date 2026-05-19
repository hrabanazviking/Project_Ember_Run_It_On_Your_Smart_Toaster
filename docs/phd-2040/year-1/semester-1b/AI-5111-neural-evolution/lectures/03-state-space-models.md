# Lecture 03: State-Space Models

## Mamba, Jamba, the Linear Attention Revolution, SSMs vs. Transformers

*The second root of Yggdrasil — not a branch of the Transformer, but a tree that grew from different soil.*

---

## 1. The Parallel Lineage: From Control Theory to Sequence Modeling

State-Space Models (SSMs) did not evolve from the Transformer. They descend from a截然不同的 intellectual tradition: **control theory and dynamical systems**. The canonical SSM is:

$$x'(t) = Ax(t) + Bu(t)$$
$$y(t) = Cx(t) + Du(t)$$

Where:
- $x(t) \in \mathbb{R}^N$ — the hidden state (continuous in time)
- $u(t) \in \mathbb{R}^1$ — the input signal
- $y(t) \in \mathbb{R}^1$ — the output signal
- $A \in \mathbb{R}^{N \times N}$ — the state transition matrix (the "kernel" of the dynamics)
- $B \in \mathbb{R}^{N \times 1}$ — the input projection
- $C \in \mathbb{R}^{1 \times N}$ — the output projection
- $D \in \mathbb{R}^{1 \times 1}$ — the feedthrough (skip connection)

This is a **continuous-time** formulation. To use it for discrete sequences, we discretize:

$$x_k = \bar{A} x_{k-1} + \bar{B} u_k$$
$$y_k = \bar{C} x_k + \bar{D} u_k$$

Where $\bar{A}, \bar{B}$ are obtained from $A, B$ via Zero-Order Hold (ZOH) discretization:

$$\bar{A} = \exp(\Delta A), \quad \bar{B} = (\bar{A} - I) A^{-1} B$$

with $\Delta$ being the discretization step size (a *learnable* parameter in modern SSMs).

---

## 2. The Key Property: Linear Recurrence = Parallelizable Scan

The discrete SSM is a **linear recurrence**:

$$x_k = \bar{A} x_{k-1} + \bar{B} u_k$$

This can be unrolled:

$$x_k = \bar{A}^k \bar{B} u_0 + \bar{A}^{k-1} \bar{B} u_1 + \cdots + \bar{A} \bar{B} u_{k-1} + \bar{B} u_k$$

$$= \sum_{i=0}^{k} \bar{A}^{k-i} \bar{B} u_i$$

The output:

$$y_k = \bar{C} x_k + \bar{D} u_k = \bar{C} \sum_{i=0}^{k} \bar{A}^{k-i} \bar{B} u_i + \bar{D} u_k$$

This is a **convolution**! If we define the SSM kernel:

$$K = (\bar{C}\bar{B}, \bar{C}\bar{A}\bar{B}, \bar{C}\bar{A}^2\bar{B}, ...)$$

Then:

$$y = K * u + \bar{D} u$$

**This is the fundamental duality of SSMs:**
- **Recurrent mode:** Compute $x_k = \bar{A}x_{k-1} + \bar{B}u_k$ sequentially — $O(N)$ per step, $O(N)$ memory
- **Convolutional mode:** Compute $y = K * u$ via FFT — $O(N \log N)$ for the full sequence

The convolution mode is **parallelizable** (unlike RNNs), and the recurrent mode uses **constant memory per step** (unlike Transformers).

---

## 3. From Theory to Practice: The SSM Lineage

### S4: Structured State Spaces (Gu et al., 2021)

The key insight of S4 was that the matrix $A$ must be **structured** for the convolution to be efficient. An unstructured $N \times N$ matrix makes the convolution kernel computation $O(N^2)$.

S4 uses the **HiPPO framework** (High-order Polynomial Projection Operators) to initialize $A$ as a specific structured matrix (HiPPO-LegS, HiPPO-LegT) that has good memory properties:

$$A_\text{LegS} = -\frac{1}{2} \begin{pmatrix} 1 & -1 & 0 & \cdots \\ 1 & -3 & 2 & \cdots \\ 0 & 2 & -5 & \cdots \\ \vdots & & & \ddots \end{pmatrix}$$

This matrix implements an **exponential decay memory** — recent inputs are weighted more heavily, and the decay rate is controlled by the structure of $A$.

**Crucially:** S4 achieves **linear time** in sequence length for training (via convolution) and **constant time per step** for inference (via recurrence). No $O(n^2)$ cost anywhere.

### S4D: Diagonal State Spaces (Gu et al., 2022)

Further simplification: use a **diagonal** approximation of $A$. This makes the recurrence trivially parallel:

$$x_{k,i} = \bar{A}_{ii} x_{k-1,i} + \bar{B}_{ki} u_k$$

Each dimension evolves independently! This seems like a severe restriction, but in practice, with large enough state dimension $N$, diagonal SSMs can approximate any structured SSM.

### S5: Simplified State Spaces (Smith et al., 2023)

Replaces the diagonal-plus-low-rank structure with a **diagonal + linear attention** hybrid, further simplifying the architecture.

---

## 4. Mamba: Selective State Spaces (Gu & Dao, 2023)

Mamba is the SSM that changed everything. The key innovation: **make the SSM parameters input-dependent**.

In standard SSMs, $\bar{A}, \bar{B}, \bar{C}$ are **fixed** (after training) — they don't depend on the input. Mamba makes them **adaptive**:

$$\bar{B}_k = \text{Linear}_B(u_k), \quad \bar{C}_k = \text{Linear}_C(u_k)$$

$$\Delta_k = \text{softplus}(\text{Linear}_\Delta(u_k))$$

$$\bar{A}_k = \exp(\Delta_k A)$$

This is called **selectivity**: the model can *choose* to remember or forget information based on the input.

**Why this matters:**

- When $\Delta_k \to 0$: $\bar{A}_k \to I$, so the state barely updates → the model **ignores** the current input
- When $\Delta_k \to \infty$: $\bar{A}_k \to 0$, so $x_k \approx \bar{B}_k u_k$ → the model **resets** to the current input
- Intermediate values: the model **smoothly integrates** current input into state

This input-dependent gating is analogous to the **forget gate** in LSTMs, but with a crucial difference: Mamba's selectivity operates in a *continuous-time framework* with a theoretically grounded discretization, rather than as an ad-hoc gating mechanism.

### The Mamba Block Architecture

```
Mamba Block:

Input x ──→ Linear ──→ ┬──→ ssim(x) ──→ Linear ──→ + ──→ Output
                        │                        ↑
                        │     ┌──────────┐       │
                        └─→ Δ = Linear(x) → discretize(A,B,Δ) ──→ selective scan ──┘
                              B = Linear(x) ──→ ↗
                              C = Linear(x) ──→ ↗

Key: A is learned but FIXED. B, C, Δ are INPUT-DEPENDENT.
The selective scan cannot be computed as a convolution —
it requires a sequential scan, but an optimized hardware-aware scan
achieves near-parallel speed.
```

### Hardware-Aware Selective Scan

The selective scan operation is sequential by nature — each step depends on the previous. However, Gu & Dao (following the FlashAttention philosophy) designed an optimized CUDA kernel that:

1. Fuses the discretization, scan, and output projection into a single kernel
2. Minimizes HBM read/writes by keeping the state in SRAM during the scan
3. Achieves wall-clock speed competitive with FlashAttention despite the sequential recurrence

---

## 5. SSMs vs. Transformers: The Empirical Picture (2024-2025)

| Dimension | Transformer | Mamba/SSM |
|-----------|------------|-----------|
| Training parallelism | Excellent (attention is fully parallel) | Good (convolution mode is parallel; selective scan is sequential but hardware-optimized) |
| Inference memory | $O(n \cdot d)$ — must store KV cache for all past tokens | $O(N \cdot d)$ — constant! The state has fixed size regardless of sequence length |
| Long sequence handling | Quadratic without sparsity; linear with FlashAttn but still memory-heavy | Naturally linear; constant memory via recurrence |
| Content-aware gating | Softmax attention is inherently content-aware | Selective SSMs are content-aware; early SSMs were not |
| Copying/lookup | Strong — attention can copy any past token directly | Weaker — must compress everything into finite state |
| Training stability | Well-understood; large-scale recipes exist | Newer; some issues with instability at extreme scale |

**The crucial finding (2024-2025):** SSMs and Transformers are *complementary*. SSMs excel at:
- Smoothly evolving sequences (audio, continuous signals)
- Long-range dependencies that don't require exact recall
- Memory-efficient inference

Transformers excel at:
- Sharp retrieval from arbitrary positions
- In-context learning (copying, pattern matching)
- Tasks requiring precise token-level comparisons

---

## 6. Jamba: The Hybrid Architecture (Lieber et al., 2024)

Jamba (from AI21 Labs) was the first large-scale hybrid SSM-Transformer model, combining:

- **Mamba layers** for efficient sequential processing
- **Transformer attention layers** for precise recall
- **Mixture-of-Experts (MoE)** for parameter efficiency

Architecture: alternating Mamba and Attention blocks in a 1:1 or 2:1 ratio, with MoE in the FFN layers.

```
Jamba Block Stack:

Block 1:  Mamba Layer  ──→  MoE-FFN
Block 2:  Attention Layer  ──→  MoE-FFN
Block 3:  Mamba Layer  ──→  MoE-FFN
Block 4:  Attention Layer  ──→  MoE-FFN
  ...

Result: 256B total parameters, 52B active per token
Context: 256K tokens
Speed: ~3x faster than equivalent pure Transformer
Memory: ~5x less KV cache than pure Transformer
```

**Jamba's insight:** Don't choose between SSMs and Transformers — use each for what it's best at. Mamba layers handle the "smooth stream" of context; attention layers handle the "sharp spikes" of retrieval.

**Hindsight note:** Jamba was a crucial stepping stone. It showed that the future was not "SSMs replace Transformers" but "architectures combine their strengths." The Worlmesh takes this further — it doesn't alternate between fixed SSM and attention layers; it *learns which topology to use for each token on each forward pass*.

---

## 7. The Linear Attention Revolution

A related but distinct line of work: **Linear Attention** (Katharopoulos et al., 2020):

Instead of computing $\text{softmax}(QK^T)V$, use an *associative* decomposition:

$$\text{Attention}(Q, K, V) = \frac{\phi(Q)(\phi(K)^T V)}{\phi(Q)(\phi(K)^T \mathbf{1})}$$

where $\phi$ is an element-wise feature map (e.g., $\phi(x) = \text{elu}(x) + 1$).

This reduces from $O(n^2 d)$ to $O(n d^2)$ — linear in $n$ but quadratic in $d$.

The connection to SSMs: **linear attention is a special case of SSMs** (with diagonal state and specific initialization). This was formalized by Katharopoulos et al. (2023) and shown to be equivalent to linear recurrence.

This equivalence is not coincidental. Both SSMs and linear attention are:
1. **Linear recurrences** (computable via parallel scan)
2. **Approximations** to full attention (with different approximation strategies)
3. **Content-dependent** in their modern forms (selective SSMs, attention with nonlinear features)

**The deep insight:** SSMs and linear attention are two faces of the same underlying mathematical object — **linear recurrence with learned transition dynamics**. The difference is in how they parameterize the transition and how they handle nonlinearity.

---

## 8. What SSMs Taught Us (That Transformers Couldn't)

1. **State, not comparison, is fundamental.** An SSM processes information through a compressed hidden state, not by comparing all pairs. For many types of reasoning, compression is more efficient than comparison.

2. **Constant-memory inference is possible.** The Transformer's $O(n)$ KV cache is a real architectural limitation. SSMs showed that you can process arbitrarily long sequences with fixed memory.

3. **Selectivity is essential.** The progression from S4 (fixed parameters) to Mamba (input-dependent parameters) mirrors the progression from "hard attention" to "soft attention" in the Transformer lineage. Intelligence requires the ability to *dynamically route information*, not just passively process it.

4. **The hybrid future.** Jamba showed that SSMs and Transformers are not competitors — they're *complements*. The right architecture uses each mechanism where it excels.

5. **Continuous-time thinking.** SSMs come from continuous-time dynamics ($x'(t) = Ax(t) + Bu(t)$), which gives them a mathematical foundation in differential equations. This turns out to be important for understanding *why* certain architectures work — the ODE viewpoint reveals invariants that the discrete computation obscures.

---

## 9. The ODE View: Unifying Transformers and SSMs

Both Transformers and SSMs can be viewed as discretizations of continuous dynamical systems:

**SSM (continuous):**
$$x'(t) = A x(t) + B u(t)$$
**Transformer attention (continuous limit):**
$$x'(t) = \text{Attn}(x(t), x(t), x(t)) - x(t) + \text{FFN}(x(t))$$

The Transformer's residual connection + layer structure can be seen as Euler discretization of the attention ODE. The SSM's recurrence is a different discretization of a different (linear) ODE.

**The Worlmesh (spoiler):**
$$x'(t) = F(x(t), \theta(t)), \quad \theta'(t) = G(x(t), \theta(t))$$

Where $\theta$ represents the *topology itself* — the attention weights, routing patterns, and even the *computational graph* evolve alongside the state. The system modifies its own architecture as it computes.

---

## 10. State-Space Models in the Big Picture

```
The Evolutionary Tree of Sequential Models:

Recurrent Models (RNN/LSTM/GRU)
    │
    ├─→ SSMs (S4, S4D, S5) ───→ Mamba (Selective SSM)
    │                                    │
    │                                    ├─→ Jamba (SSM + Transformer + MoE)
    │                                    │
    │                                    └─→ [Worlmesh: SSM backbone with
    │                                          self-organizing attention topology]
    │
    └─→ Attention (Bahdanau, 2014) ──→ Transformer (Vaswani, 2017)
                                            │
                                            ├─→ Sparse/Efficient (Longformer, FlashAttn)
                                            │
                                            ├─→ MoE (Switch Transformer)
                                            │
                                            ├─→ Recursive Depth (thinking tokens)
                                            │
                                            └─→ [Worlmesh: attention as
                                                  emergent from SSM dynamics]
```

---

## Discussion Questions

1. SSMs achieve constant-memory inference while Transformers require $O(n)$ memory (for the KV cache). Under what conditions is constant memory a fundamental advantage, and when is it a limitation? What kinds of reasoning *require* remembering the full input?
2. Mamba's selectivity mechanism makes the SSM parameters input-dependent. How is this different from Transformer attention's dependence on Q, K, V? Is selectivity "attention in disguise," or is there a fundamental difference?
3. Jamba alternates Mamba and Attention layers in a fixed pattern. Could this pattern be *learned*? What would a "Jamba that decides its own topology" look like?
4. The ODE viewpoint unifies Transformers and SSMs. What other architectures (e.g., diffusion models, neural ODEs) can be included in this unification?
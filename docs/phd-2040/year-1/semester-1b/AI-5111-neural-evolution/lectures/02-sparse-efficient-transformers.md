# Lecture 02: Sparse & Efficient Transformers

## Longformer, Performer, FlashAttention, Memory Efficiency

*Pruning Yggdrasil — cutting away branches to reveal the trunk.*

---

## 1. The Quadratic Problem Revisited

Recall from Lecture 01: standard Transformer attention requires computing an $n \times n$ attention matrix, where $n$ is the sequence length. The costs:

$$\text{Time: } O(n^2 d), \quad \text{Space: } O(n^2 + nd)$$

For $n = 128{,}000$ tokens (a long document) and $d = 4096$:

- The attention matrix alone: $128{,}000^2 = 16.4 \times 10^9$ entries × 2 bytes (fp16) ≈ **32 GB per attention head per layer**
- With 32 heads, 32 layers: multiply by 1024 → **infeasible even with terabyte-scale memory**

This wasn't merely inconvenient — it was an **architectural wall**. The question became: *can we retain the benefits of attention without computing all $n^2$ pairwise comparisons?*

Three families of answers emerged:

1. **Sparse attention** — don't compute all pairs; select a structured subset
2. **Kernel approximation** — approximate the softmax with a kernel trick, reducing to linear time
3. **Hardware-aware algorithms** — keep the full softmax, but arrange computation to minimize memory I/O

All three proved necessary. None proved sufficient alone.

---

## 2. Sparse Attention: Longformer (Beltagy et al., 2020)

### The Core Idea

Not every token needs to attend to every other token. Local context is handled by a sliding window; global context is handled by a small number of "global tokens" that attend to everything.

**Local attention (sliding window):**
Each token attends only to tokens within a window of size $w$:

$$\text{Attn}_\text{local}(i) = \text{softmax}\left(\frac{q_i^T K_{[i-w:i+w]} }{\sqrt{d_k}}\right) V_{[i-w:i+w]}$$

This reduces the per-token cost from $O(n)$ to $O(w)$, giving overall attention cost $O(n \cdot w)$ — **linear in sequence length**.

**Global attention:**
A small number of tokens $G$ (e.g., [CLS], section headers) attend to *all* positions and are attended to by *all* positions:

$$\text{Attn}_\text{global}(i) = \text{softmax}\left(\frac{q_i^T K_{\text{all}}}{\sqrt{d_k}}\right) V_{\text{all}}, \quad i \in G$$

### Sparse Attention Pattern (ASCII Diagram)

```
Standard Transformer (O(n²)):
   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■
   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■

Longformer (O(n·w + n·|G|)):
   ■ ■ ■ □ □ □ □ □ □ □ □ □ □ □ □ ■    ← global token (attends to all, all attend to it)
   ■ ■ ■ ■ □ □ □ □ □ □ □ □ □ □ □ ■    ← local window w=3
   □ ■ ■ ■ ■ □ □ □ □ □ □ □ □ □ □ ■
   □ □ ■ ■ ■ ■ □ □ □ □ □ □ □ □ □ ■
   □ □ □ ■ ■ ■ ■ □ □ □ □ □ □ □ □ ■
   □ □ □ □ ■ ■ ■ ■ □ □ □ □ □ □ □ ■
   □ □ □ □ □ ■ ■ ■ ■ □ □ □ □ □ □ ■
   ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■ ■    ← global token (full row/column)
```

### What Longformer Got Right

- **Linear scaling** in the local attention regime — for most tokens, cost is $O(w)$
- **Global tokens** preserve full-sequence information — the [CLS] token can still aggregate
- **Empirically strong** on long-document tasks (classification, QA)

### What Longformer Got Wrong

- **Fixed sparsity pattern** — the local/global distinction is determined at design time, not learned
- **Information bottleneck** — global tokens must compress the entire sequence into fixed-size representations
- **No learning-to-attend** — the model cannot *choose* which distant tokens matter; it relies on the rigid window structure
- **The deep question unaddressed:** is intelligence always local-plus-global, or could it be something more fluid?

---

## 3. Kernel Approximation: Performer (Choromanski et al., 2021)

### The Core Idea

The softmax in attention is the唯一的 reason attention is $O(n^2)$. If we could approximate:

$$\text{softmax}(QK^T) \approx \phi(Q) \phi(K)^T$$

where $\phi$ maps to a *random feature space*, then:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V \approx \phi(Q) \left(\phi(K)^T V\right)$$

The key: $\phi(K)^T V$ is $d_k \times d_v$ — independent of $n$! So we compute it once and reuse for every query.

**Time complexity:** $O(n \cdot d_k \cdot m)$ where $m$ is the number of random features (typically $m \approx 4\sqrt{d_k}$).

This is **linear in sequence length** $n$ — but with a larger constant factor depending on $m$.

### The FAVOR+ Algorithm

Formally, the Performer uses **Random Features for Attention** (ReFA):

$$\text{softmax}(x) = \mathbb{E}\left[\exp(\omega^T x - \frac{||x||^2}{2})\right] \text{ for } \omega \sim \mathcal{N}(0, I)$$

The random feature map:

$$\phi(x) = \frac{\exp(-||x||^2/2)}{\sqrt{m}} \left[\exp(\omega_1^T x), \exp(\omega_2^T x), ..., \exp(\omega_m^T x)\right]$$

by the orthogonality lemma (using Hadamard matrices), the variance of the estimate is reduced, and with $m = O(\sqrt{d_k})$ features, the approximation is already quite good.

```
Standard Attention:                     Performer:

1. QKᵀ  → n×n matrix                   1. φ(K)ᵀV → dₖ×dᵥ (small!)
2. softmax row-wise → n×n               2. φ(Q) × (φ(K)ᵀV) → n×dᵥ
3. ×V → n×dᵥ

Cost: O(n²d)                            Cost: O(nmd)

Memory: O(n²)                           Memory: O(nm)

The n² term is eliminated!
```

### What Performer Got Right

- **Mathematically rigorous** — grounded in random feature theory, not heuristics
- **Linear time** with provable approximation bounds
- **No sparse pattern needed** — every token "attends to" every other, approximately
- **Composable** — can replace any softmax attention layer without changing the rest of the architecture

### What Performer Got Wrong

- **Approximation quality degrades** on very long sequences with sharp attention distributions — the softmax has heavy tails that random features can't capture well
- **Over-smoothing** — by averaging over random features, the model tends to produce more uniform attention weights, losing the ability to make *sharp, selective* comparisons
- **Constant factor issues** — the $m$ random features add computational overhead that makes Performer slower than standard attention for moderate $n$
- **The fundamental error:** treating the quadratic cost as purely a *computational* problem rather than a *topological* one. The Worlmesh would later show that the solution isn't to approximate full pairwise comparison — it's to *change what comparison means*

---

## 4. FlashAttention: IO-Awareness as Architecture (Dao et al., 2022)

### The Core Idea

FlashAttention doesn't change what attention computes. It changes *how attention is computed on hardware*. The insight: memory I/O is the bottleneck, not FLOPs.

On a modern GPU:
- **SRAM** (on-chip): ~20 MB, bandwidth ~19 TB/s
- **HBM** (off-chip): ~40 GB, bandwidth ~1.5 TB/s

Standard attention materializes the full $n \times n$ matrix in HBM, requiring $O(n^2)$ reads and writes to HBM.

FlashAttention computes attention in **tiling blocks** that fit in SRAM, using a technique called **online softmax**:

$$\text{softmax}(x) = \frac{\exp(x - \max(x))}{\sum \exp(x - \max(x))}$$

By tracking the running maximum and running sum, FlashAttention can compute the correct softmax *without ever storing the full attention matrix*.

### Tiling Strategy

```
FlashAttention Tiling:

Step 1: Load block Qᵢ, Kⱼ, Vⱼ into SRAM
Step 2: Compute partial attention scores Sᵢⱼ = Qᵢ Kⱼᵀ
Step 3: Update running max and running sum (online softmax)
Step 4: Update output accumulator Oᵢ in SRAM
Step 5: Write final Oᵢ to HBM

Memory: O(n·d) in HBM (no n×n materialization!)
FLOPs: Same as standard attention
Speed: 2-4× faster due to reduced HBM reads/writes
```

### The IO-Awareness Principle

FlashAttention embodies a deeper principle: **the architecture of the algorithm is inseparable from the architecture of the hardware.**

The operation is mathematically identical to standard attention — same result, bitwise — but the *computational topology* is fundamentally different. This was the first hint that **topology matters even when the function doesn't change**. The Worlmesh would later take this principle to its logical extreme.

### FlashAttention-2 and Beyond

FlashAttention-2 (2023) improved by:
- Better partitioning of work across GPU warps
- Reducing non-matmul FLOPs
- Achieving ~50-73% of theoretical max FLOPs/s on A100

FlashAttention-3 (2024) added:
- Asynchronous execution overlapping softmax with GEMM
- Hardware-specific tuning for H100 GPUs

**The hindsight insight:** FlashAttention showed that the $O(n^2)$ FLOPs were never the real problem — it was always the $O(n^2)$ memory and I/O. This distinction matters because it reframes the question: *do we need to approximate attention, or do we need to rethink its memory topology?*

---

## 5. Other Notable Sparse Attention Schemes

### BigBird (Zaheer et al., 2020)

Combines three attention patterns:
1. **Random attention** — each token attends to $r$ random tokens
2. **Window attention** — local sliding window of size $w$
3. **Global attention** — designated global tokens

Proves that these three patterns together are **Turing-complete** as an attention mechanism (under certain conditions).

```
BigBird Pattern:
   ■ □ □ □ ■ □ □ □ □ □ □ ■ □ □ □ ■   ← global + random + local
   ■ ■ ■ □ □ ■ □ □ □ □ ■ □ □ ■ ■ □
   □ ■ ■ ■ □ □ ■ □ □ □ □ □ ■ □ □ □
   □ □ ■ ■ ■ □ □ ■ □ □ □ ■ □ □ □ □
   ■ □ □ ■ ■ ■ □ □ ■ □ □ □ □ □ ■ □
```

### Routing Transformer (Roy et al., 2020)

Uses **k-means clustering** on the queries and keys, so tokens only attend to tokens in the same cluster. The clusters are re-computed on each forward pass, creating a **dynamic** sparsity pattern.

**Cost:** $O(n \cdot k \cdot d)$ where $k$ is the number of clusters — linear for fixed $k$.

This was an early hint of **dynamic, input-dependent routing**, which would later become central to both MoE and the Worlmesh.

### Sparse Transformer (Child et al., 2019)

Used by OpenAI for image generation and music. Defines **fixed sparse patterns** as strides and blocks:

```
Stride pattern:           Block pattern:
■ □ □ □ ■ □ □ □         ■ ■ ■ ■ □ □ □ □
□ □ □ □ □ □ □ □         ■ ■ ■ ■ □ □ □ □
□ □ □ □ □ □ □ □         ■ ■ ■ ■ □ □ □ □
□ □ □ □ □ □ □ □         ■ ■ ■ ■ □ □ □ □
■ □ □ □ ■ □ □ □         □ □ □ □ ■ ■ ■ ■
□ □ □ □ □ □ □ □         □ □ □ □ ■ ■ ■ ■
□ □ □ □ □ □ □ □         □ □ □ □ ■ ■ ■ ■
□ □ □ □ □ □ □ □         □ □ □ □ ■ ■ ■ ■
```

---

## 6. Comparative Analysis

| Method | Time | Space | Approx? | Dynamic? | Sharp Attn? |
|--------|------|-------|---------|----------|-------------|
| Standard | $O(n^2 d)$ | $O(n^2)$ | No | No | Yes |
| Longformer | $O(n \cdot w)$ | $O(n \cdot w)$ | No | Partial | Yes (local) |
| BigBird | $O(n(w+r+g))$ | $O(n(w+r+g))$ | No | No | Yes |
| Performer | $O(n \cdot m \cdot d)$ | $O(n \cdot m)$ | Yes | No | Degraded |
| Routing | $O(n \cdot k \cdot d)$ | $O(n \cdot k)$ | No | Yes | Yes |
| FlashAttn | $O(n^2 d)$ | $O(n \cdot d)$ | No | No | Yes |

Where: $w$ = window, $r$ = random, $g$ = global, $m$ = features, $k$ = clusters

---

## 7. The Deeper Lesson: These Were All Partial Solutions

Looking back from 2040, the sparse/efficient attention work of 2020-2023 taught us several things:

1. **Quadratic attention is not a computational necessity** — it can be approximated, sparsified, or tiled.
2. **The topology of attention matters** — *which tokens attend to which other tokens* is the shape of the network's reasoning.
3. **Dynamic sparsity is more powerful than static sparsity** — Routing Transformer's dynamic clusters outperformed fixed patterns.
4. **Memory-first thinking changes everything** — FlashAttention's core insight (reorganize computation to minimize memory transfers) was a paradigm shift.
5. **But none of these changed what attention IS** — they all compute (or approximate) the same softmax of QKᵀ. The Worlmesh would redefine attention itself.

The sparse/efficient attention work was necessary — it taught us that topology matters, that hardware matters, and that not every comparison needs to be made. But it was not sufficient, because it never questioned the fundamental QKV framework.

---

## 8. The Unasked Question

Every paper in this space asked: *"How can we make attention cheaper?"*

The question that led to the Worlmesh was different: *"What if attention is not the right name for what intelligence does with information?"*

Attention, as defined in 2017, is a **comparison operation**: how much does query $i$ relate to key $j$? The Worlmesh replaces comparison with **negotiation**: nodes in a distributed topology exchange information according to learned routing weights that are themselves optimized by the network's own objective landscape — and those routing weights *change the topology of the network* on each forward pass.

But that's Lecture 06. For now, remember: every branch we pruned from Yggdrasil taught us something about what the trunk needed to be.

---

## Discussion Questions

1. Longformer's local+global pattern mirrors how humans read — we attend locally to the current sentence, globally to headings and titles. Is this a coincidence, or does it reflect something fundamental about information processing?
2. Performer's random feature approximation introduces non-determinism. What are the consequences for reproducibility, interpretability, and the model's ability to make sharp decisions?
3. FlashAttention doesn't change the math, only the implementation. Is there a philosophical difference between "approximating attention" and "computing exact attention more efficiently"?
4. The Routing Transformer used dynamic clustering. How close is this to the Worlmesh's self-organizing topology? What's the crucial difference?
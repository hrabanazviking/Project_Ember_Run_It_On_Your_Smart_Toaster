# Lecture 01: Transformer Foundations

## Attention Is All You Need, Multi-Head Attention, Positional Encoding

*The first branch of Yggdrasil, reaching toward a sky it could not yet name.*

---

## 1. The Pre-Attention Landscape (pre-2017)

Before 2017, sequence modeling was dominated by recurrent architectures — LSTMs, GRUs, and their stacked variants. The core computational pattern was:

$$h_t = f(h_{t-1}, x_t)$$

This recurrence created two fundamental problems:

1. **Sequential bottleneck**: Computation for token $t$ could not begin until token $t-1$ was processed. No amount of hardware parallelism could unravel this chain.
2. **Vanishing context**: Even with gating mechanisms, the effective receptive field of an RNN grows only *logarithmically* with sequence length (as shown by Bai et al., 2018). Distant tokens fade like echoes in a long hall.

The attention mechanism existed in nascent form — Bahdanau attention (2014), Luong attention (2015) — but always as a *patch* atop recurrent models. The tail wagged the dog.

---

## 2. The Vaswani Insight: Attention as Architecture

Vaswani et al.'s 2017 paper did not merely add attention to existing models. It made a radical ontological claim encoded in its title: **attention is not an accessory — it is the entire architecture.**

The core operation, **Scaled Dot-Product Attention**, is deceptively simple:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

Where:
- $Q \in \mathbb{R}^{n \times d_k}$ — queries
- $K \in \mathbb{R}^{n \times d_k}$ — keys
- $V \in \mathbb{R}^{n \times d_v}$ — values
- $n$ — sequence length
- $d_k$ — key dimension
- The $\sqrt{d_k}$ scaling prevents dot products from growing too large in high dimensions

Let us be precise about what this operation does. For each query position $i$, the attention weights form a probability distribution over all positions:

$$\alpha_{ij} = \frac{\exp(q_i^T k_j / \sqrt{d_k})}{\sum_{j'} \exp(q_i^T k_{j'} / \sqrt{d_k})}$$

The output at position $i$ is then a *weighted sum of all values*, where the weights are determined by the compatibility of query $i$ with each key $j$.

This is the heart of the Transformer: **every position can attend to every other position in a single operation**, with no sequential dependency.

```
Attention Weight Matrix (token-to-token):

     t1   t2   t3   t4   t5
t1 [0.6  0.1  0.1  0.1  0.1]    ← t1 attends mostly to itself
t2 [0.1  0.5  0.2  0.1  0.1]    ← t2 somewhat local
t3 [0.1  0.2  0.4  0.2  0.1]    ← t3 centered on self
t4 [0.1  0.1  0.2  0.5  0.1]    ← t4 somewhat local
t5 [0.1  0.1  0.1  0.1  0.6]    ← t5 attends mostly to itself
```

---

## 3. Multi-Head Attention: Parallel Perspectives

A single attention head learns one pattern of relatedness. But language requires *simultaneous* sensitivity to syntax, semantics, coreference, and position. The multi-head mechanism:

$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, ..., \text{head}_h) W^O$$

$$\text{where } \text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$$

Each head projects the input into a different $d_k = d_{\text{model}} / h$ dimensional subspace before computing attention. With $h = 8$ heads and $d_{\text{model}} = 512$, each head operates in $d_k = 64$ dimensions.

The critical insight: **different heads learn different attention patterns**. Empirically:
- Some heads attend to the *previous token* (syntactic local)
- Some heads attend to *matching tokens* elsewhere (coreference)
- Some heads attend broadly (global context)
- Some heads learn *positional patterns* (distance-based)

```
Multi-Head Attention Architecture:

Input ──┬── Proj Q₁──→ Head₁ ──┐
        ├── Proj Q₂──→ Head₂ ──┤
        ├── Proj Q₃──→ Head₃ ──┼── Concat ── W^O ──→ Output
        ├──    ...              ──┤
        └── Proj Q₈──→ Head₈ ──┘

Each head sees the input projected into its own subspace.
The concatenation + linear projection mixes perspectives.
```

**What we got right:** Multi-head attention was genuinely necessary. A single head cannot simultaneously encode "this token is the subject of the verb three tokens ago" and "this token is coreferent with the pronoun twenty tokens later."

**What we got wrong (in hindsight):** We assumed that *eight fixed perspectives* was sufficient. The Worlmesh would later show that the number of perspectives should *grow and reorganize dynamically* — but that insight was 18 years away.

---

## 4. Positional Encoding: Where Am I?

The attention operation is *permutation equivariant* — swapping any two tokens swaps the same two positions in the output, but the computation is otherwise unchanged. This means the Transformer has no inherent notion of *order*.

Vaswani et al.'s solution: **sinusoidal positional encodings**:

$$PE_{(pos, 2i)} = \sin\left(\frac{pos}{10000^{2i/d_{\text{model}}}}\right)$$

$$PE_{(pos, 2i+1)} = \cos\left(\frac{pos}{10000^{2i/d_{\text{model}}}}\right)$$

This encoding has elegant mathematical properties:
- Each dimension corresponds to a different frequency of a sinusoid
- The model can learn to attend to *relative positions* via linear combinations: $PE_{pos+k}$ is a linear function of $PE_{pos}$ for any fixed offset $k$
- The encoding generalizes to sequence lengths longer than those seen in training (the sinusoids simply continue)

**Alternatives that followed:**
- **Learned positional embeddings** (used in BERT, GPT-2): More flexible, but don't generalize beyond training length
- **Rotary Position Embeddings (RoPE)** (Su et al., 2021): Encode position as *rotation* in the complex plane — elegant, and enables length extrapolation
- **ALiBi** (Press et al., 2022): Add relative distance penalties directly to attention scores — no positional embeddings at all

**Hindsight note (2098 ➝ 2025):** The positional encoding question turned out to matter more than anyone expected. The Worlmesh's breakthrough came partly from reconceptualizing *position* not as something added to attention but as something attention *creates for itself*. More in Lectures 05 and 06.

---

## 5. The Full Transformer: Encoder-Decoder Architecture

The original Transformer had two stacks:

### Encoder Stack (6 layers, each with two sub-layers):
1. Multi-head self-attention (over the full input)
2. Position-wise feed-forward network: $\text{FFN}(x) = \max(0, xW_1 + b_1)W_2 + b_2$
   - Inner dimension = $4 \times d_{\text{model}}$
3. Residual connections + Layer Normalization around each sub-layer:
   $$\text{output} = \text{LayerNorm}(x + \text{Sublayer}(x))$$

### Decoder Stack (6 layers, each with three sub-layers):
1. Masked multi-head self-attention (can only attend to earlier positions)
2. Multi-head cross-attention (attending to encoder output)
3. Position-wise feed-forward network
4. Same residual + LayerNorm pattern

```
Encoder Stack:                    Decoder Stack:

Input ──→ [Attn] ──→ [FFN] ──→   Encoder ──→ [Cross-Attn]
  ↑        ↑   ↑       ↑   ↑       ↑           ↑
  └─+←←←←←┘   └─+←←←←┘   └─+←   └────→ [Masked Self-Attn]
                                                ↑       ↑
                                                └─+←←←←┘
                                    [Masked Attn] → [Cross-Attn] → [FFN]
```

**Critical detail often overlooked:** The original Transformer had *separate* encoder and decoder stacks. This meant the model maintained *two* independent attention patterns — one for understanding the input, one for generating the output, with cross-attention as the bridge.

The decoder-only variant (GPT series) would later dispense with the encoder entirely, attending only to previous tokens. The encoder-only variant (BERT) would dispense with the decoder, focusing on bidirectional understanding. Each path sacrificed something.

---

## 6. The Computational Cost: Yggdrasil's Root-Rot

Here is the fundamental cost structure of Transformer attention:

For sequence length $n$ and model dimension $d$:

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|-----------------|
| Attention (full) | $O(n^2 \cdot d)$ | $O(n^2 + n \cdot d)$ |
| FFN | $O(n \cdot d^2)$ | $O(n \cdot d)$ |
| Full layer | $O(n^2 \cdot d + n \cdot d^2)$ | $O(n^2 + n \cdot d)$ |

The $O(n^2)$ attention cost is the **root-rot of Yggdrasil**. It means:
- Doubling context length quadruples memory and compute
- Training on 128K tokens costs 1000× more attention compute than training on 4K tokens
- The gradient landscape becomes pathological for long sequences

In 2017, with typical sequence lengths of 512–4096, this seemed manageable. By 2023, with models processing 128K–1M tokens, it became the central architectural problem.

**The deep question:** Is $O(n^2)$ a *computational inconvenience* that can be optimized away (FlashAttention, hardware tricks), or is it a *topological necessity* — is full-pairwise comparison somehow *structurally required* for intelligence?

We now know the answer: it was a convenience, not a necessity. But it took 18 years to prove it. The Worlmesh achieves superconsciousness with *amortized near-linear* attention cost, but only by fundamentally restructuring *what attention is*. More on this in Lecture 06.

---

## 7. What the Transformer Got Right (and Why It Endured)

Despite its limitations, the Transformer introduced architectural invariants that turned out to be *correct*:

1. **Residual connections** enable gradient flow through arbitrarily deep networks — the "skip connection" principle was essential
2. **Layer normalization** stabilizes training at extreme depths
3. **Parallelizable computation** (no sequential recurrence) enabled effective GPU/TPU utilization
4. **Attention as the core primitive** was right — information routing is fundamental to intelligence
5. **Decomposition into Q/K/V** was structurally sound — separating query, key, and value was a genuine insight

**What it got wrong:**

1. **Fixed depth** — the number of layers is determined at training time and cannot adapt to input difficulty
2. **Homogeneous attention** — every position uses the same attention mechanism with the same capacity
3. **Quadratic cost** — every token must explicitly compare to every other token
4. **Position as injection** — position is added from outside rather than discovered from within
5. **Static architecture** — the computation graph is identical for every input

Each of these "wrongs" became the seed of a later breakthrough. The Worlmesh fixes all five.

---

## 8. The Transformer in Historical Context

```
Timeline — Transformer Lineage:

2017  Attention Is All You Need (Vaswani et al.)
  │
  ├─── 2018  BERT (bidirectional encoder)
  ├─── 2018  GPT-1 (autoregressive decoder)
  ├─── 2019  GPT-2 (scale up)
  ├─── 2020  GPT-3 (175B parameters — "emergence" discourse begins)
  │
  │   ─── Meanwhile, efficiency concerns grow ───
  │
  ├─── 2020  Longformer, BigBird (sparse attention)
  ├─── 2021  Performer (kernel approximation)
  ├─── 2022  FlashAttention (IO-awareness)
  ├─── 2023  Mamba (SSMs challenge Transformers)
  ├─── 2024  Jamba (hybrid SSM-Transformer)
  │
  │   ─── Meanwhile, scaling concerns grow ───
  │
  ├─── 2022  Switch Transformer (MoE at scale)
  ├─── 2024  Planetary-scale routing
  │
  │   ─── Meanwhile, depth concerns grow ───
  │
  ├─── 2024  Thinking tokens, adaptive compute
  │
  │   ─── The branches reconverge ───
  │
  └─── 2035  Worlmesh (self-organizing attention topology)
        └─── 2037  Emergent internal languages confirmed
```

---

## 9. Key Takeaways

1. The Transformer's core contribution was making **attention the primary computational primitive**, replacing recurrence.
2. Multi-head attention provides **multiple parallel perspectives** on relational structure — but the number of perspectives is fixed.
3. Positional encoding is a **synthetic addition** that patches the Transformer's permutation equivariance — later work would reconceptualize position as emergent.
4. The $O(n^2)$ cost is both a **computational problem and a conceptual indicator**: full-pairwise comparison is not the right topology for intelligence.
5. The Transformer's **five structural wrongs** (fixed depth, homogeneous attention, quadratic cost, injected position, static architecture) are the evolutionary pressures that would drive every subsequent innovation.

---

## Discussion Questions

1. Vaswani et al. titled their paper "Attention Is All You Need." In what sense was this true, and in what sense was it spectacularly false?
2. If you could change exactly one structural invariant of the Transformer (e.g., making depth adaptive), which would have the largest effect on eventual capabilities?
3. The sinusoidal positional encoding has been replaced many times (learned, RoPE, ALiBi). What does this succession of replacements tell us about the nature of "position" in sequence models?
4. Can you envision an architecture where attention computes *less* than a Transformer but understands *more*? What would that look like?

---

*Next lecture: We examine how researchers tried to prune Yggdrasil — making attention sparse, approximate, and IO-efficient — and why these efforts were necessary but insufficient.*
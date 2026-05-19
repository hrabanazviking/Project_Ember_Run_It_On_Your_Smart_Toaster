# 18 — Long-Context Attention: RoPE, YaRN, Sliding Window, Attention Sinks

**Category:** LLM Techniques
**Runa relevance:** Heimskringla (model capability awareness), Muninn (context-feeding decisions), kernel (long-conversation handling)
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

The transformer's attention mechanism has *quadratic* memory and compute cost in sequence length. A 100K-token context naively costs 10,000× the attention compute of a 1K-token context. The whole long-context revolution — 200K, 1M, 2M+ token windows in production models — was made possible by a set of focused engineering wins: **position encodings that extrapolate** (RoPE, ALiBi), **scaling techniques that extend trained-context windows post-hoc** (YaRN, Position Interpolation), **architectural tricks that bound the cost** (sliding window, attention sinks, sparse / linear attention), and **infrastructure tricks** (FlashAttention, KV-cache management, context caching).

For Runa, the key practical questions are: which long-context techniques does each candidate local model support? When does context-feeding actually work (vs technically-large but practically-lost-in-the-middle, see [[05-long-context-vs-retrieval]])? What does it cost to keep a long conversation on the Pi?

## 2. Technical depth

**Position encodings.** Transformers need *position information* injected into the attention computation; raw attention is order-invariant. The position-encoding scheme determines how well the model handles sequences longer than it was trained on.

- **Absolute position embeddings** (original Transformer). Learned per-position vectors. Cannot extrapolate beyond trained length.
- **Sinusoidal embeddings** (vanilla "Attention is All You Need"). Closed-form, deterministic. Modest extrapolation.
- **Rotary Position Embedding (RoPE)** (Su et al., 2021, arXiv:2104.09864). Multiplies query/key vectors by rotation matrices whose angles depend on position. Currently dominant in open models (Llama, Mistral, Qwen, etc.). Naturally encodes *relative* position. Limited extrapolation past training length.
- **ALiBi (Attention with Linear Biases)** (Press et al., 2021). Adds a linear position bias to attention scores directly. Strong extrapolation; less common in modern frontier models.
- **NoPE / no position encoding** (Kazemnejad et al., 2023). For causal decoder-only models, omitting position encoding entirely sometimes works; underexplored.

**Extending RoPE beyond training length.** When you trained at 4K context and want 32K inference, naive RoPE fails — relative-distance encodings the model hasn't seen confuse attention. Fix techniques:

- **Position Interpolation (PI)** (Chen et al., Meta, 2023). Linearly scale position indices so they fit in the trained range. Easy; some quality loss; needs short fine-tune.
- **NTK-Aware scaling**. Non-linearly rescale position frequencies to preserve high-frequency components. No fine-tuning needed but quality degrades faster than PI with fine-tune.
- **YaRN (Yet another RoPE extensioN)** (Peng et al., 2023, arXiv:2309.00071). Combines NTK-aware scaling with frequency-specific adjustments. Strong extrapolation with minimal fine-tuning. Used by many open long-context models.
- **Dynamic NTK**. Adjust the scaling at inference time per-query based on actual length. Free quality at the cost of routing overhead.
- **LongRoPE** (Ding et al., Microsoft, 2024, arXiv:2402.13753). Two-stage search for optimal RoPE rescaling. Cited 2-8M-token extensions.

**Sliding window attention.** Mistral 7B's contribution: instead of attending to all prior tokens, each token attends only to the last W tokens (W typically 4096-8192). Combined with KV-cache rolling, this gives effectively unbounded context with bounded compute and memory per token. Quality is preserved on tasks where distant context doesn't matter; degrades on long-range dependencies.

**Attention sinks (StreamingLLM)** (Xiao et al., MIT, arXiv:2309.17453, 2023). Empirical observation: keeping the *first few tokens* (the "sinks") plus the *recent window* in the KV-cache gives much better quality than just the recent window. The first tokens absorb attention probability mass that would otherwise misroute. Used in production "streaming" deployments.

**FlashAttention** (Dao et al., 2022, 2023). I/O-aware attention kernels that compute attention without materialising the full attention matrix in HBM. ~2-4× speedup with no quality loss. Versions: FlashAttention-1 (2022), FlashAttention-2 (2023), FlashAttention-3 (2024, Hopper-architecture-optimised). Essentially universal in modern inference.

**Sparse / linear attention.** Approximation methods that bring attention from O(n²) to O(n log n) or O(n). Examples: Longformer (sliding+global), BigBird, Linformer, Performer, Mamba (state-space; not strictly attention but a related sequence model). Linear-attention models have struggled to match quality at frontier scale; SSMs (Mamba family) are the current best alternative-attention approach.

**KV-cache management.** At inference, the model caches key/value vectors for all attended tokens. For 100K context at 70B params, this can be tens of GB. Techniques: KV quantisation (4-bit or 8-bit cache), eviction policies, off-loading to slower memory tiers, paged attention (vLLM).

**Context caching** (Anthropic prompt caching, Gemini context caching). Server-side caching of prompt processing — repeated prompts that share long prefixes pay full cost once, marginal cost on reuse. Changed the long-context economics decisively.

## 3. Key works

- **Su et al. "RoFormer: Enhanced Transformer with Rotary Position Embedding."** arXiv:2104.09864, 2021. The RoPE paper.
- **Press, Smith, Lewis. "Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation."** arXiv:2108.12409, 2021. ALiBi paper.
- **Chen, Wong, Chen, Tian. "Extending Context Window of Large Language Models via Positional Interpolation."** Meta, arXiv:2306.15595, 2023.
- **Peng, Quesnelle, Fan, Shippole. "YaRN: Efficient Context Window Extension of Large Language Models."** arXiv:2309.00071, 2023.
- **Ding et al. "LongRoPE: Extending LLM Context Window Beyond 2 Million Tokens."** Microsoft, arXiv:2402.13753, 2024.
- **Xiao, Tian, Chen, Han, Lewis. "Efficient Streaming Language Models with Attention Sinks."** MIT, arXiv:2309.17453, 2023.
- **Dao et al. "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness."** arXiv:2205.14135, 2022.
- **Mistral 7B paper** — Jiang et al., arXiv:2310.06825, 2023. Sliding window attention.
- **Gu, Dao. "Mamba: Linear-Time Sequence Modeling with Selective State Spaces."** arXiv:2312.00752, 2023. Alternative to attention.

## 4. Empirical results

- **RoPE without fine-tuning** typically holds quality up to ~2× trained context; degrades sharply beyond.
- **YaRN** can extend 4K-trained models to 64K-128K with modest fine-tuning and small quality loss.
- **LongRoPE** demonstrated 2M-token effective context — the basis of some of the trillion-token claims in late 2024.
- **Sliding window (Mistral 7B)** retained near-full-attention quality on most benchmarks at 4K window; degraded on long-range dependency tasks (RULER multi-hop).
- **Attention sinks (StreamingLLM)** enabled millions-of-tokens streaming with minimal quality loss on conversational tasks where global context is less critical.
- **FlashAttention-2:** ~2× over FlashAttention-1 on Ampere GPUs; well-established as universal best practice.
- **Lost-in-the-middle (Liu et al., 2023)** is the empirical ceiling: even with all these techniques, models attend better to context start and end than middle. Architecture has not fully closed this gap.

## 5. Applicability to Runa

For **Heimskringla model selection**:

- Tag each provider/model with its *trained context* and *effective context* (the latter measured against RULER-style benchmarks, not advertised limits — see [[05-long-context-vs-retrieval]]).
- For long Muninn-fed prompts, prefer models with strong long-context credentials (Claude 3+, Gemini 1.5+, Llama 3.1 with YaRN). Local Pi-sized models typically max out useful context at 16K-32K even if technically larger.
- KV-cache memory dominates at long context. For local inference, the rule of thumb is `kv_mb ≈ context_tokens · n_layers · 2 · head_dim · 2 / 1e6`. A 7B model at 32K context with FP16 KV uses ~16 GB. Use Q8 or Q4 KV quantisation to fit.

For **kernel turn shape**:

- Don't ship 100K-token contexts to the Pi-local model. If Muninn retrieval returns a lot, summarise before prompting.
- For long conversations on a stateful surface (gateway, GUI), use the MemGPT pattern ([[01-memgpt-os-memory-hierarchies]]) rather than relying on raw long context.
- StreamingLLM-style attention sinks are useful for any chat surface where conversations run indefinitely; if the local llama.cpp version supports them, enable.

For **Muninn**:

- The "retrieved context" Muninn returns should be bounded — feeding 50K tokens of conversation history into every turn is wasteful. Top-K retrieval with similarity threshold, then fits-in-budget summarisation.

What to avoid:

- Don't assume an advertised long context window is the effective one. Test or check published RULER scores.
- Don't run long-context inference on Pi 5 without checking KV-cache memory. Out-of-memory is a hard fail; gracefully fall back to shorter context.
- Don't pick a long-context model and then re-quantise its KV-cache at FP16. Defeats the purpose; quantise the cache too.
- Don't apply YaRN-extended models without running through the actual long-context fine-tune or you may get the technical capability without the trained behaviour.

## 6. Open questions

- **The true ceiling on effective context.** RULER suggests it's somewhere between 32K-128K for most models in 2025; pushing this further is active research.
- **State-space models (Mamba, Jamba, Hyena) vs attention.** SSMs scale linearly and have shown strong long-sequence results; they are not yet the standard. Likely to matter more for Runa over time.
- **Hybrid attention/SSM models.** Jamba (AI21), Zamba — combining attention with state-space layers. Quality competitive with pure-attention; benefits unclear.
- **Long-context for reasoning vs recall.** Models recall well at long contexts but reason poorly. Architectural fixes are an active area.

## 7. References (curated)

- arXiv:2104.09864 — RoPE.
- arXiv:2309.00071 — YaRN.
- arXiv:2306.15595 — Position Interpolation.
- arXiv:2309.17453 — StreamingLLM / attention sinks.
- arXiv:2310.06825 — Mistral 7B paper (sliding window).
- arXiv:2205.14135 — FlashAttention.
- arXiv:2312.00752 — Mamba.
- arXiv:2403.19887 — Jamba (hybrid attention/SSM).
- Companion docs: [[05-long-context-vs-retrieval]] (the empirical reality), [[16-quantization-local-inference]] (KV-cache quant).

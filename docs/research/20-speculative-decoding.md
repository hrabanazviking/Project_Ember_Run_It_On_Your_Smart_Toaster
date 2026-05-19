# 20 — Speculative Decoding and Inference Acceleration

**Category:** LLM Techniques
**Runa relevance:** Heimskringla (latency budgets, especially Rödd voice loop), local Ollama adapter
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

Autoregressive LLMs generate one token at a time. Each token requires a full forward pass through the model. The latency of generating an N-token response is roughly N × (per-token latency). For large models on local hardware, per-token latency can be 50-500ms — making a 200-token response take 10-100 seconds. For interactive surfaces (voice, GUI typing-effect, real-time chat), this is too slow.

**Speculative decoding** is the breakthrough that decoupled "tokens generated per second" from "model forward passes per second." A small fast *draft model* generates K candidate tokens cheaply; the large *target model* verifies them all in *one* forward pass; tokens that match the target's distribution are accepted, mismatches trigger fallback. Net effect: 2-4× speedup on most workloads with *no quality loss* (the output distribution is mathematically identical to the target model's). For Runa's voice surface (Rödd) and any interactive turn, this is the difference between "responsive" and "annoying."

## 2. Technical depth

**Classic speculative decoding** (Leviathan et al., Google, 2022; Chen et al., DeepMind, 2023):

```
[1] Draft model D generates K candidate next tokens d_1, ..., d_K
    autoregressively (cheap).
[2] Target model T runs ONE forward pass on (prefix + d_1, ..., d_K),
    producing distributions p_T(·|prefix), p_T(·|prefix+d_1), ...,
    p_T(·|prefix+d_1+...+d_K).
[3] For each draft token d_i, accept it with probability:
        min(1, p_T(d_i) / p_D(d_i))
    Stop at the first rejection.
[4] If all K accepted, T's final-position distribution gives the (K+1)th
    token "for free."
[5] If rejected at position i: sample from a modified distribution that
    corrects for the rejection.
```

The acceptance probability formula is *exact* — the output distribution of accepted tokens is identical to running T directly, no quality loss. This is a "verified speedup" — unlike approximations.

**Speedup intuition.** If D is well-aligned with T, most draft tokens are accepted. With acceptance rate α and K drafts:
- Expected accepted tokens per round ≈ (1 - α^(K+1)) / (1 - α)
- Round cost ≈ K × cost(D) + 1 × cost(T)

For α=0.7, K=4: ~2.45 tokens accepted per round at cost ~(4·cost(D) + cost(T)). When cost(D) ≪ cost(T), this is much faster than 1 token per cost(T).

**Variants and refinements:**

**SpecInfer / Tree-of-thoughts speculative decoding** (Miao et al., 2023). Instead of a single linear sequence of K drafts, generate a *tree* of candidate continuations and verify in parallel. Higher acceptance rate.

**Medusa** (Cai et al., 2024). Train *additional heads* on the target model itself that predict multiple future tokens in parallel. Eliminates the separate draft model; the target model drafts itself. Often easier to deploy than a separate draft model.

**EAGLE / EAGLE-2** (Li et al., 2024). Lightweight feature-level prediction that's more accurate than naive draft models; reported 3-5× speedups.

**Lookahead decoding** (Fu et al., 2024). N-gram-based speculative decoding without any trained draft model. Uses Jacobi iteration over candidate token positions.

**Self-speculative decoding** (Zhang et al., 2023). Use a *truncated* version of the target model (e.g. early-exit at half the layers) as the draft. No separate model to train or serve.

**Prompt-lookup decoding** (Saxena, 2023). Trivial baseline: scan the prompt itself for n-gram continuations of the current sequence. Surprisingly effective for tasks where the response overlaps the prompt (summarisation, code modification).

**Beyond speculation: other inference acceleration techniques:**

- **KV-cache reuse** (prompt caching). Repeated prompts share computed cache.
- **Continuous batching** (vLLM, Orca). Serve many requests at different generation stages in one batch.
- **PagedAttention** (vLLM). Memory-efficient KV-cache management.
- **FlashAttention**. The attention-side win ([[18-long-context-attention]]).
- **Quantisation** ([[16-quantization-local-inference]]). Smaller weights → faster memory I/O.
- **Tensor parallelism / pipeline parallelism**. Multi-GPU serving (less relevant for Pi).

## 3. Key works

- **Leviathan, Kalman, Matias. "Fast Inference from Transformers via Speculative Decoding."** Google, arXiv:2211.17192, 2022.
- **Chen et al. "Accelerating Large Language Model Decoding with Speculative Sampling."** DeepMind, arXiv:2302.01318, 2023. The contemporaneous paper with similar ideas.
- **Cai et al. "Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads."** arXiv:2401.10774, 2024.
- **Li et al. "EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty."** arXiv:2401.15077, 2024.
- **Fu et al. "Break the Sequential Dependency of LLM Inference Using Lookahead Decoding."** arXiv:2402.02057, 2024.
- **Saxena, A. "Prompt Lookup Decoding."** GitHub: github.com/apoorvumang/prompt-lookup-decoding, 2023.
- **Kwon et al. "Efficient Memory Management for Large Language Model Serving with PagedAttention."** UC Berkeley, arXiv:2309.06180, 2023. vLLM.
- **Dao et al. FlashAttention-2/3 papers** — see [[18-long-context-attention]].

## 4. Empirical results

- **Classic speculative decoding** (small draft model + large target): 2-3× speedup on most tasks with no quality loss. Speedup depends on draft-target similarity.
- **Medusa:** 2-3× speedup without separate draft model, easier ops.
- **EAGLE / EAGLE-2:** reported 3-5× speedups on Llama-class targets.
- **Lookahead decoding:** 1.5-2× speedup with no training required.
- **Prompt-lookup:** 2-4× on summarisation and code-modification tasks; negligible on free-form generation.
- **Combined techniques** (e.g. EAGLE + KV-cache reuse + quantisation): 5-15× speedup over baseline FP16 + naive decoding.
- **Hardware-dependent.** Speculative decoding wins more on memory-bandwidth-limited hardware (Pi, CPU, integrated GPU) than on compute-limited hardware (high-end GPU with bandwidth headroom).

## 5. Applicability to Runa

For **Heimskringla local provider (llama.cpp / Ollama)**:

- llama.cpp supports speculative decoding (`-md` flag for draft model). Enable when a draft model is available.
- For Llama 3.x family on Pi: pair a Llama 3.1 8B *target* with a small Llama 3 1B-class *draft*. Both quantised. Reported 2-3× speedup on Pi-class hardware.
- Pinpoint cost: drafting twice for the same eventual answer is *wasted* compute when draft and target disagree. Acceptance rate matters; choose a draft that matches the target's training distribution.

For **Rödd (voice)**:

- Voice surfaces are the most latency-sensitive. Aim for TTFT < 500ms and >20 tokens/s for fluid playback. Speculative decoding is essentially mandatory for any local model > ~3B parameters on Pi.
- Streaming TTS ([[35-modern-tts]]) lets playback start as soon as the first sentence is decoded; speculative decoding compounds the win.

For **Bifröst gateway**:

- HTTP/WS clients expect streaming. Speculative decoding doesn't change the streaming interface; tokens still emit one by one, just faster.

For **Heimskringla cost model**:

- When the model router decides between providers, speculative-decoded local can compete with cloud on latency for short-to-medium responses. For very long responses, cloud (with batched serving and TPU-class throughput) still wins on tokens/sec.

What to avoid:

- Don't enable speculative decoding without measuring acceptance rate. A draft model that's too weak gives low acceptance, eats compute without speedup.
- Don't use Medusa-style trained heads without committing to a specific target model. The heads are model-specific.
- Don't expect speculative decoding to help with extreme-long-context inference where attention compute (not memory I/O) dominates. The speedup margin narrows.
- Don't combine with non-deterministic sampling (temperature > 0) without verifying acceptance behaviour. The math still holds but practical acceptance can drop.

## 6. Open questions

- **The right draft model for any given target.** Heuristics exist (smaller version of same family); systematic methods are immature.
- **Speculative decoding + MoE.** MoE routing decisions are token-level; whether classic speculative decoding composes cleanly with MoE is an active area.
- **Speculative decoding for tool-use.** Most agentic turns mix natural language with structured tool calls. The acceptance distribution differs; understudied.
- **Hardware-specific drafters.** Tiny dedicated NPUs might run drafters very cheaply alongside a GPU-served target; productionisation patterns are still emerging.

## 7. References (curated)

- arXiv:2211.17192 — Speculative Decoding (Leviathan et al.).
- arXiv:2302.01318 — Speculative Sampling (Chen et al.).
- arXiv:2401.10774 — Medusa.
- arXiv:2401.15077 — EAGLE.
- arXiv:2402.02057 — Lookahead Decoding.
- arXiv:2309.06180 — vLLM / PagedAttention.
- github.com/ggerganov/llama.cpp — llama.cpp (which supports speculative decoding).
- github.com/SafeAILab/EAGLE — EAGLE reference implementation.
- Companion docs: [[16-quantization-local-inference]], [[18-long-context-attention]], [[30-llama-cpp-gguf-ecosystem]], [[33-model-routing-ensembles]].

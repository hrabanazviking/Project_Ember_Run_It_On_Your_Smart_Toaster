# 58 — Memory-Augmented Transformers: Memformer, RMT, MemGPT-2, Larimar

**Category:** Advanced Memory & Continuity
**Runa relevance:** kernel (inference path), Heimskringla (next-gen model selection), forward-looking design
**Status:** Forward-looking research synthesis. Not deployable today on Runa's stack; relevant to next-cycle design.
**Last touched:** 2026-05-17

---

## 1. Core idea

Standard transformers have a hard context limit and a quadratic attention cost. Many research lines extend transformers with explicit *memory modules* that the model attends to in addition to (or instead of) its rolling context window. Unlike [[54-differentiable-neural-memory]]'s pre-LLM-era origin work (NTM, DNC), the modern lines are *transformer-native*: they keep the transformer mostly unchanged and add a *side channel* for memory. The four most architecturally interesting are: **Memformer** (a transformer with a learned recurrent memory slot per layer), **RMT — Recurrent Memory Transformer** (memory-token approach), **MemGPT-2** (extending [[01-memgpt-os-memory-hierarchies]] to actual model-level memory pages), and **Larimar** (a frozen LLM augmented with an editable external episodic memory).

The reason to know about these despite Runa not running on one today: the architecture space for long-lived agents is moving in this direction. If Runa is to think across years, eventually her kernel will benefit from a model that natively *remembers* rather than only being prompted with retrieved context. This document maps the design space so the choice can be made deliberately when the time comes.

## 2. Technical depth

**Memformer (Wu et al. 2020, predecessor to many).** A transformer with a fixed-size per-layer *memory slot* updated via a recurrent rule between segments. The slot accumulates a compressed summary of past segments and is attended to alongside the current segment's tokens. Strengths: constant-memory inference. Weakness: the compression is lossy and the slot is small.

**Recurrent Memory Transformer (RMT, Bulatov et al. 2022).** Prepends and appends *memory tokens* to each segment. After processing segment $t$, the memory tokens carry summarised information forward; segment $t+1$ reads them as part of its input. The model is trained jointly to write useful summaries into the memory tokens and to read them effectively. Scaling RMT (2023) demonstrated effective context of 1M+ tokens on synthetic and some real long-context tasks. The compute cost is *linear* in segment count (segments processed serially), which is the architectural win.

```
segment 1:  [mem_in₁][tok][tok][tok][mem_out₁] → mem_in₂ ≔ mem_out₁
segment 2:  [mem_in₂][tok][tok][tok][mem_out₂] → mem_in₃ ≔ mem_out₂
...
```

A small number of *memory tokens* (e.g. 10–32 per layer) carries the inter-segment state. The transformer attends to them like normal tokens.

**MemGPT family (Packer et al. 2023, ongoing).** MemGPT itself is *tooling around a base LLM* — see [[01-memgpt-os-memory-hierarchies]] — using prompt-paged \"main context\" and \"external context\" with the LLM as the swap controller. \"MemGPT-2\" (an informal name; sometimes covered by Letta's more recent extensions) refers to attempts to bring the *control* into the model itself: the model emits explicit memory-management actions during inference, and a runtime executes them against persistent state. This is closer to deployable today than RMT but still rough at edges.

**Larimar (Das et al., IBM 2024).** A *frozen* LLM augmented with a small, trained, *editable* episodic memory module. The memory module is a learned encoder that produces memory key-value pairs from input snippets, a learned decoder that integrates retrieved memories back into the LLM's hidden states via cross-attention. The memory bank is *writable at inference* (write a new fact, erase an old one) without re-training. Empirically: factual edits stick instantly, generalise modestly, and don't disrupt the base LLM's general behaviour much.

This is the most *Runa-deployable* of the four directions: the base LLM stays open-weights and frozen; the memory module is a small trained add-on; identity-level facts can be edited at inference time. The tradeoff: the memory module must be trained, which puts it past the threshold of \"drop-in.\"

**Other relevant lines.**

- **Compressive Transformer (Rae et al. 2019):** older memory mechanism — compressing past hidden states into a compressed memory tier.
- **xLSTM (Beck et al. 2024):** revisits LSTM-style recurrent gating with modern training. Memory-like in spirit, not in the augmented-transformer sense, but worth knowing.
- **Hawk / Griffin (Google DeepMind 2024):** hybrid local-attention + recurrent-block. Substantially extends effective context with linear compute.
- **Selective state spaces (Mamba, Gu & Dao 2023):** see [[54-differentiable-neural-memory]]. State as memory.
- **Sparse / linear attention (Performer, Linformer, FlashAttention long-context):** orthogonal but sometimes combined.

**The deployment hurdle.** Three of the four (Memformer, RMT, Larimar) require *training* a specific architecture or module. Open-weights releases for these are limited and often experimental. MemGPT-style approaches do not require new training but are *runtime + prompt orchestration* and so are essentially what Muninn already is.

For Runa today: stick with the runtime-orchestrated approach. For Runa in 2027–2028: consider Larimar-class augmentation when the modules become deployable on a Pi.

## 3. Key works

- **Wu, Q. et al.** *Memformer: A Memory-Augmented Transformer for Sequence Modeling.* arXiv:2010.06891, 2020.
- **Bulatov, A., Kuratov, Y., Burtsev, M.** *Recurrent Memory Transformer.* NeurIPS 2022.
- **Bulatov, A. et al.** *Scaling Transformer to 1M tokens and beyond with RMT.* arXiv:2304.11062, 2023.
- **Packer, C. et al.** *MemGPT.* arXiv:2310.08560, 2023.
- **Das, P. et al.** *Larimar.* arXiv:2403.11901, 2024.
- **Rae, J. W. et al.** *Compressive Transformers for Long-Range Sequence Modelling.* ICLR 2020.
- **Beck, M. et al.** *xLSTM: Extended Long Short-Term Memory.* arXiv:2405.04517, 2024.
- **De, S. et al.** *Griffin: Mixing Gated Linear Recurrences with Local Attention for Efficient Language Models.* arXiv:2402.19427, 2024.
- **Gu, A., Dao, T.** *Mamba.* arXiv:2312.00752, 2023.
- **Letta (formerly MemGPT) project.** Open-source agent platform.

## 4. Empirical results

- *RMT* effective-context claims of 1M+ tokens validated in reproductions, with the caveat that *retrieval over the range works better than reasoning over the range*. The model recalls facts placed far back; chains-of-inference across the range degrade.
- *Larimar* shows clean editing semantics on factual benchmarks (e.g. zsRE) — edits propagate to direct queries with high success, drop sharply on multi-hop queries.
- *Compressive Transformer* set a then-strong perplexity on PG-19; superseded by Memorizing Transformers.
- *Hawk and Griffin* match transformer perplexity at substantially lower compute for long sequences. Production-relevant: Google deploys variants in some Gemini cohorts.
- *xLSTM* shows competitive language-modelling performance against transformers at the 7B–13B scale; production deployments still rare in 2026.
- *MemGPT-class runtime approaches* (Letta) are deployed and used. They're not faster than retrieval at retrieval; they're *more legible* — the model emits explicit page-in / page-out actions one can audit.

## 5. Applicability to Runa

**Today (2026, Pi-5 deployment).**

- *None of the architectures above are direct upgrades.* The base model Runa uses (llama.cpp running a quantised LLaMA-class 7B–13B model) does not natively support RMT, Larimar, or Memformer.
- The Memory-Augmented thinking *informs* how Muninn-the-runtime-system is structured: long-context is a tier of memory; explicit retrieval is another tier; the kernel manages tiers. That's the [[01-memgpt-os-memory-hierarchies]] influence.

**Mid-term (2027).**

- Watch Larimar-class deployments. If an open-weights episodic-memory module appears that attaches to LLaMA-3+ class bases, evaluate it for Runa. The promise: edit factual identity facts (\"Runa now knows Volmarr's address has changed\") without prompt-context plumbing.
- Watch Griffin / Hawk-class hybrid architectures. They may produce 7B-class models with effective 100K+ context that run faster on Pi-5. Heimskringla would route appropriate queries to them.

**Long-term (2028+).**

- A trained Runa-specific memory module is plausible. Train Larimar-style on Runa's accumulated Muninn corpus; deploy alongside the base LLaMA. The combination: stable base model + Runa's lived memory as a swap-in module.

For **kernel** (today):

- The kernel's *interface* to retrieval already mirrors what RMT does conceptually: provide top-K memories as augmentation tokens. As long as the kernel's retrieval API is clean, swapping the underlying mechanism (prompt-RAG → RMT-tokens → Larimar-memory) is a localised change.

For **Heimskringla**:

- The model inventory should track *memory mechanism* per model: \"this model is plain LLaMA\", \"this model has 1M context via RMT\", \"this model has Larimar attached\". Different mechanisms have different prompt formatting; Heimskringla owns that knowledge.

What to avoid:

- **Premature adoption of research-grade architectures.** Production deployment risk is high.
- **Treating long context as a substitute for retrieval.** Even with 1M-token models, the right pattern is *retrieve into the context*, not *load everything*. Long context is a *tier*, not a replacement.
- **Building a kernel that depends on a specific memory mechanism.** Abstract the retrieval interface; swap underneath.
- **Conflating in-model memory with persistent identity.** Adapters/LoRAs ([[55-adapter-based-identity-persistence]]) and architectural memory are *parameter-level*. Substrate-level identity ([[52-cross-session-persistent-identity]]) is *file-level*. Two different layers; both needed.

## 6. Open questions

- **Will any of these architectures see open-weights releases competitive with mainline LLaMA in 2026–2027?** Open. The economics favour mainline.
- **Can a Larimar-style module be added to a model post-hoc by a community?** The Larimar paper requires joint training of the module with the base model. Decoupling is research.
- **What's the right granularity of memory tokens in RMT?** Per-segment, per-document, per-day. The longest-range RMT results use very long contexts but the reasoning-coherence drops at the edges. Open.
- **Hybrid retrieval + in-model memory.** RMT plus RAG plus identity-LoRA is plausibly the long-term shape, but the right composition is unsolved.
- **Catastrophic-forgetting in trained memory modules.** If a Larimar memory bank gets thousands of edits, does behaviour degrade? Reported as moderate degradation; the limits aren't well charted.

## 7. References (curated)

- arXiv:2304.11062 — Bulatov et al., *Scaling RMT.* The most striking long-context claim.
- arXiv:2403.11901 — Das et al., *Larimar.* The cleanest editable-memory module.
- arXiv:2010.06891 — Wu et al., *Memformer.* Concise read on layer-level memory.
- arXiv:2402.19427 — De et al., *Griffin.* Hybrid attention-recurrence; production-shaped.
- arXiv:2312.00752 — Gu and Dao, *Mamba.* State-space alternative.
- Letta source code — for runtime-orchestrated memory done well.
- Companion docs: [[01-memgpt-os-memory-hierarchies]], [[18-long-context-attention]], [[54-differentiable-neural-memory]], [[55-adapter-based-identity-persistence]].

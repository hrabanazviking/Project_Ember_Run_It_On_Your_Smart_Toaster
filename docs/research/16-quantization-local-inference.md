# 16 — Quantization for Local Inference: GPTQ, AWQ, GGUF, exllamav2

**Category:** LLM Techniques
**Runa relevance:** Heimskringla (model selection on Pi 5 / laptop), deploy/pi/ (resource budgets), local Ollama adapter
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

Modern LLMs are trained in 16-bit or 32-bit floating point. At inference time, those weights can be *quantised* — represented in 8, 4, 3, or even 2 bits per parameter — with surprisingly small quality loss when the quantisation is done well. A 70B-parameter model that needs 140 GB of memory at FP16 fits in ~40 GB at Q4 (4-bit weights). The same model fits in ~22 GB at Q2_K. The difference between "this model fits on a 16 GB Pi" and "no, it doesn't" is entirely a quantisation question.

For Runa, quantisation is the technology that makes serious local inference possible at all. Without it, the Pi 5 is limited to 7B-class models running at FP16/BF16 (and stretching 16 GB at that). With it, Runa can plausibly run 13B-30B-parameter models locally for the agentic workload, reserving cloud calls (via OpenRouter / Anthropic / etc.) for the very hardest queries. This shifts cost, latency, and sovereignty in the right direction.

## 2. Technical depth

The core observation: LLM weights are *overparameterised* and *redundant*. Representing them at full precision wastes bits — many of those bits are noise. Quantisation finds a low-bit representation that preserves the function the weights implement.

**Quantisation taxonomy:**

| Axis | Choices |
|---|---|
| Bit width | 16, 8, 6, 5, 4, 3, 2 (sometimes 1, 1.58 for ternary) |
| Granularity | Per-tensor, per-channel, per-group (e.g. groups of 32 or 128 values) |
| Symmetric / asymmetric | Symmetric: zero-centred; asymmetric: separate offset |
| What's quantised | Weights only, activations only, weights + activations |
| When quantised | Post-training quantisation (PTQ), quantisation-aware training (QAT) |
| Calibration | Round-to-nearest (RTN), GPTQ-style optimisation, AWQ-style channel-importance |

**The major techniques and formats:**

**GPTQ** (Frantar, Ashkboos, Hoefler, Alistarh, 2022, arXiv:2210.17323). One-shot post-training quantisation method. For each layer, solves an optimisation problem: pick the quantised weights that minimise the L2 error on calibration data. Implemented via Optimal Brain Quantisation. Strong at 4-bit; degrades at 3-bit; falls apart at 2-bit. Standard format in HuggingFace ecosystem and `auto-gptq`.

**AWQ (Activation-aware Weight Quantisation)** (Lin et al., MIT + NVIDIA, arXiv:2306.00978, 2023). Observation: not all weights matter equally — channels with large activations should be preserved more carefully. AWQ scales those salient channels before quantising. Often matches or beats GPTQ at 4-bit with simpler computation.

**GGUF** (Georgi Gerganov, 2023+, evolution of GGML format). The format used by **llama.cpp** and its ecosystem (Ollama, LM Studio, KoboldCPP, text-generation-webui). Not a single quantisation *method* but a *container* that supports many quant types:

- `Q8_0` — 8-bit weights, near-FP16 quality, half the memory.
- `Q6_K` — 6-bit, very close to Q8 quality.
- `Q5_K_M` — 5-bit medium, popular balance.
- `Q4_K_M` — 4-bit medium, the typical "good enough" point. Most-used quant.
- `Q4_0`, `Q4_1` — legacy 4-bit formats; superseded by `Q4_K_M` for most use cases.
- `Q3_K_S/M/L` — 3-bit small/medium/large; usable for very large models on tight hardware.
- `Q2_K` — 2-bit; substantial quality loss; useful for fitting impossible models.
- `IQ` family (`IQ4_XS`, `IQ3_XS`, `IQ2_XS`) — newer "I-quants" using importance matrices; quality at low bits often beats older formats.

The `_K_M` / `_K_S` / `_K_L` suffix denotes K-quants (Kawrakow's 2023 method): different bit widths for different layers based on their importance.

**exllamav2 / EXL2** (Turboderp, 2023+). Custom CUDA kernels and mixed-bit quantisation: each layer can use a different bit width chosen by per-layer error analysis. Excellent throughput on NVIDIA GPUs with adequate memory. Less Pi-friendly than GGUF.

**Bitnet / 1.58-bit models** (Ma et al., Microsoft, 2024). Trained-from-scratch at ternary weights {-1, 0, 1}. Open question whether this is genuinely competitive at scale or only at small scale; early results promising.

**Activation quantisation** (W8A8, SmoothQuant). Quantise activations alongside weights. Required for INT8 inference (TPU, NVIDIA TensorRT, some embedded chips). More fiddly than weight-only; less commonly used for personal-server inference.

## 3. Key works

- **Frantar et al. "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers."** arXiv:2210.17323, 2022.
- **Lin et al. "AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration."** arXiv:2306.00978, 2023.
- **Dettmers, Lewis, Belkada, Zettlemoyer. "LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale."** arXiv:2208.07339, 2022. The bitsandbytes paper.
- **Dettmers et al. "QLoRA: Efficient Finetuning of Quantized LLMs."** arXiv:2305.14314, 2023. 4-bit quantisation + low-rank fine-tuning.
- **Ma et al. "The Era of 1-bit LLMs."** Microsoft, arXiv:2402.17764, 2024.
- **Kawrakow's K-quants** — discussed in llama.cpp commits and the K-quant introduction PR; no formal paper.
- **Georgi Gerganov, llama.cpp project** — github.com/ggerganov/llama.cpp.

## 4. Empirical results

- **Q4_K_M on Llama-2-7B** vs FP16: typically <1% loss on MMLU, indistinguishable on most benchmarks; saves ~70% of memory.
- **Q3_K_M:** ~2-4% loss; visible on hard tasks; usually acceptable for casual use.
- **Q2_K:** 5-15% loss; noticeable degradation in long-form coherence and reasoning.
- **AWQ vs GPTQ at 4-bit:** very close; AWQ slightly better on instruction-tuned models, GPTQ slightly better on base models. Differences usually within noise on practical tasks.
- **IQ-quants** (newer GGUF variants): generally beat same-bit older quants on benchmarks by 1-3 points. Recommended as default for any new local deployment.
- **Throughput:** 4-bit inference on llama.cpp can be *faster* than FP16 on memory-bandwidth-limited hardware (CPU, integrated GPU, Pi) because the bottleneck is moving weights through memory. On compute-limited hardware (high-end GPU with bandwidth headroom), FP16 may match or beat 4-bit because dequantisation adds compute.

## 5. Applicability to Runa

For **Heimskringla local-provider adapters** (Ollama, LM Studio):

- **Default local model on Pi 5 (16 GB):** Q4_K_M or IQ4_XS variants of a 7B-13B model. Candidates: Llama 3.1 8B, Qwen 2.5 7B, Mistral 7B / Nemo 12B, Gemma 2 9B.
- **Stretch local model on Pi 5:** Q3_K_M of a 13B-class model, or Q4_K_M of a 22B model. Tight; verify on actual hardware.
- **Laptop / longhall deployment:** Q4_K_M of 30B-70B class models; Q5_K_M or Q6_K when memory allows for higher quality.
- **Stick to GGUF** unless there's a compelling reason for exllama or vanilla HF. GGUF + llama.cpp / Ollama is the most Pi-friendly, most cross-platform stack ([[30-llama-cpp-gguf-ecosystem]]).
- **Pin model + quant in config.** `models.providers.ollama.default_model: "llama3.1:8b-instruct-q4_K_M"`. Eir verifies the file matches the config hash at start.

What to avoid:

- Don't use Q2_K for any serious reasoning task. Save it for "I really need this model to fit and I'll accept brain damage" situations.
- Don't compare quants across architectures naively. A Q4 7B model is not equivalent to a Q2 13B model — different failure modes.
- Don't trust raw perplexity as a quality proxy at low bits. Use task-specific evals (MMLU, GSM8K, HumanEval) when picking a quant level.
- Don't quantise instruction-tuned models with calibration data that doesn't include instruction-style examples. The calibration data shifts the error distribution; use instruction-style calibration for instruction models.

## 6. Open questions

- **Sub-2-bit territory.** Bitnet's 1.58-bit results are promising but mostly at small scale. Whether they hold at 70B+ is open.
- **Quantisation + fine-tuning.** QLoRA shows you can fine-tune a 4-bit model with negligible quality loss. Pushing this to 2-bit base + LoRA adapters is active research.
- **Hardware-specific quantisation.** Different chips (Apple Silicon, NVIDIA, AMD, ARM CPU, dedicated NPUs) prefer different quantisation shapes. A model quantised for one may not be optimal for another.
- **Quantisation of attention.** Most quantisation focuses on weights; quantising the KV-cache (the attention's intermediate state) is a separate frontier, important for long-context inference on tight memory.

## 7. References (curated)

- arXiv:2210.17323 — GPTQ.
- arXiv:2306.00978 — AWQ.
- arXiv:2208.07339 — LLM.int8() / bitsandbytes.
- arXiv:2305.14314 — QLoRA.
- arXiv:2402.17764 — Bitnet 1.58.
- github.com/ggerganov/llama.cpp — llama.cpp source.
- github.com/turboderp/exllamav2 — exllamav2.
- github.com/AutoGPTQ/AutoGPTQ — AutoGPTQ.
- huggingface.co/docs/transformers/main/en/quantization — HF's quantisation guide.
- Companion docs: [[30-llama-cpp-gguf-ecosystem]] (the runtime), [[31-edge-llm-pi5]] (the hardware target).

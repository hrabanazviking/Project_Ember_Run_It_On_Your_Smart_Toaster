# 30 — llama.cpp and the GGML/GGUF Ecosystem

**Category:** Local & Edge Inference
**Runa relevance:** Heimskringla (local provider), Ollama adapter, Pi 5 deployment substrate
**Status:** Research synthesis. The most-load-bearing local-inference reference in the corpus.
**Last touched:** 2026-05-17

---

## 1. Core idea

**llama.cpp** — Georgi Gerganov's C/C++ inference engine for LLaMA-family models and many beyond — is the foundation of the modern local-LLM ecosystem. **GGML** is its tensor library (custom, no external deps). **GGUF** is its model format. Together, this stack powers Ollama, LM Studio, KoboldCPP, text-generation-webui, llamafile, and most "run an LLM on my laptop / Pi / phone" workflows that don't involve GPUs and Python ML stacks.

For Runa, llama.cpp + GGUF is the local-inference substrate. Pi 5 deployment is approachable because llama.cpp runs efficiently on ARM CPUs with no CUDA dependency. Cross-platform binaries Just Work. The format is the de facto interchange for quantised open-weight models. Heimskringla's Ollama / LM Studio / direct-llama.cpp adapters are all wrappers around this same engine.

This doc covers the architectural choices that made llama.cpp dominant, the GGUF format that emerged from it, the wider ecosystem, and Runa-specific deployment guidance.

## 2. Technical depth

**llama.cpp's core design decisions** (from project history and commits):

- **C/C++ only, no external deps.** No PyTorch, no Python at the inference layer. Builds anywhere a C compiler runs.
- **CPU-first.** GPU acceleration (CUDA, Metal, Vulkan, ROCm, SYCL) is *added on top*. The CPU path is always present, always works.
- **Quantisation as first-class.** Not an afterthought; the format is built around quantised inference.
- **Memory mapping (mmap).** Model weights are mmap'd from disk; the OS pages them in as needed. Lets you run a 13B model on a system without 13B of free RAM (with degraded performance).
- **Single static binary** ships. No "make sure your Python environment has the right CUDA drivers."

**Architecture:**

```
                ┌─────────────────────────────┐
                │   model file (.gguf)        │
                │   weights + metadata + tokenizer │
                └────────────┬────────────────┘
                             │ mmap
                             ▼
                ┌─────────────────────────────┐
                │   llama.cpp inference loop  │
                │                             │
                │   ┌─────┐  ┌─────┐ ┌─────┐  │
                │   │ CPU │  │ GPU │ │ NPU │  │   (backends)
                │   └─────┘  └─────┘ └─────┘  │
                │   ┌──────────────────────┐  │
                │   │ ggml tensor library  │  │   (custom)
                │   └──────────────────────┘  │
                └─────────────────────────────┘
                             │
                             ▼
                ┌─────────────────────────────┐
                │  CLI / HTTP server / lib    │
                │  llama-cli, llama-server,   │
                │  llama.h (C API)            │
                └─────────────────────────────┘
```

**GGUF format** (introduced August 2023, replaced GGML/GGJT/GGMF):

- Single-file: weights, tokenizer, prompt template, metadata all in one `.gguf` file.
- Versioned and extensible: new metadata fields can be added without breaking old loaders.
- Quantisation-rich: supports all the Q-types in the [[16-quantization-local-inference]] taxonomy.
- Tooling: `convert.py` converts HuggingFace models to GGUF; `llama-quantize` re-quantises.

**The ecosystem layered on top:**

- **Ollama** (ollama.com, 2023+) — Docker-Hub-style model registry + simple HTTP server. `ollama pull llama3.1:8b` downloads a GGUF; `ollama run` chats with it. Most popular wrapper. Suitable for Runa's local provider.
- **LM Studio** (lmstudio.ai) — GUI for browsing, downloading, and serving models. Builds on llama.cpp via its own bindings (and now mlx-engine on Apple Silicon). OpenAI-compatible HTTP API.
- **llamafile** (Mozilla / Justine Tunney, 2023+) — packages llama.cpp + a GGUF into a *single executable* that runs on any major OS. Brilliant for distribution.
- **KoboldCPP** (LostRuins) — fork of llama.cpp focused on creative-writing and KoboldAI compatibility. Useful for less-restricted local inference.
- **text-generation-webui** (oobabooga) — gradio-based UI; supports llama.cpp and many other backends.
- **llama-cpp-python** (Andrei Betlen) — Python bindings. The bridge for Python apps that want direct llama.cpp control.

**Performance highlights** (as observed on 2024-2026 hardware):

- Pi 5 (8GB / 16GB, ARM Cortex-A76 quad-core): ~3-8 tokens/sec on Q4_K_M 7B models. Usable for short interactions; awkward for long.
- Apple Silicon (M1/M2/M3) via Metal: very strong (30-100+ tokens/sec on 7B Q4 depending on chip).
- Modest x86 laptop CPU (e.g. 8-core Ryzen): 5-15 tokens/sec on Q4 7B; better with AVX-512.
- Consumer GPU (RTX 4090) via CUDA: 100+ tokens/sec on 7B Q4; better still on smaller quants.

**Speculative decoding** ([[20-speculative-decoding]]) is supported in llama.cpp via `-md` for draft-model. Real 2-3× speedups on Pi-class hardware.

## 3. Key works

- **Georgi Gerganov.** llama.cpp repository — github.com/ggerganov/llama.cpp. Project history is itself a key reference.
- **Gerganov, G.** ggml library — github.com/ggerganov/ggml. The tensor library underneath.
- **Tunney, J.** llamafile — github.com/Mozilla-Ocho/llamafile. Mozilla project.
- **Ollama** — github.com/ollama/ollama. The most-used wrapper.
- **LM Studio** — lmstudio.ai. The most-used GUI.
- **Betlen, A.** llama-cpp-python — github.com/abetlen/llama-cpp-python.
- The original **LLaMA paper** (Touvron et al., Meta, arXiv:2302.13971, 2023) and **Llama 2** (arXiv:2307.09288) are the models that drove the ecosystem. Subsequent Llama 3, 3.1, 3.2, 3.3 and Mistral / Qwen / Gemma / Phi families all distributed primarily through GGUF.

## 4. Empirical results

- llama.cpp's CPU inference is competitive with — sometimes faster than — much heavier frameworks on the same hardware. Memory-bandwidth-bound inference favours small, lean implementations.
- GGUF has become the universal local-inference format. Most open-weight models get a GGUF release within days. Searching `<model_name> gguf` on Hugging Face usually finds a quantised version.
- llama.cpp tracks new model architectures very quickly. New families (Llama 3, Qwen 2, Gemma 2, Mistral Small, DeepSeek family) typically get llama.cpp support within hours or days of release.
- Quality of llama.cpp's quantisation (especially K-quants and IQ-quants) is widely considered best-in-class for low-bit inference, including beating naive INT4 from larger frameworks.
- Stability: the project moves fast; breaking changes are not unheard of. Pin a llama.cpp version in deployment.

## 5. Applicability to Runa

For **Heimskringla local provider adapters** (per ADR-0002 §D-2.4 and broader):

- **Recommended path: Ollama.** Mature, simple HTTP API, model management built in (`ollama pull` to fetch, `ollama list` to inspect), good cross-platform support.
- **Alternative: direct llama.cpp via llama-cpp-python.** Lower-level control, suitable for the inference-side of Hirð / Völundr workers that need fine-grained control (e.g. forcing specific sampling parameters, custom grammar constraints).
- **Alternative: LM Studio.** Convenient for development on Volmarr's workstation; less suitable for Pi deployment.

For **Pi 5 deployment** ([[31-edge-llm-pi5]]):

- llama.cpp is the *only* serious option for Pi-local inference in 2025. Other frameworks (vLLM, TGI, MLC) are GPU-centric.
- Compile with `-march=native -mcpu=native` for the Pi 5's ARM Cortex-A76; Q4_K_M and IQ4_XS 7B-8B models reach usable speeds.
- Use mmap (default). Don't pre-load the entire model into RAM if you're tight; pages come in on demand.

For **deploy/pi/**:

- A `deploy/pi/install_local_inference.sh` should: install build deps (`build-essential`, `cmake`), clone and build llama.cpp pinned to a known-good commit, set up Ollama, download a default model GGUF, validate by running a one-token completion. All idempotent.

For **Heimskringla model registry**:

- The "default local model" should be config-pinned to a specific GGUF file with a specific quant (`llama3.1:8b-instruct-q4_K_M`). Don't hot-swap based on availability — Volmarr should know exactly which weights are answering him.

What to avoid:

- Don't use unquantised FP16 GGUFs on Pi. They fit (a 7B is ~14 GB) but performance is terrible.
- Don't rely on llama.cpp's HTTP server (`llama-server`) for production. Ollama wraps it with model management, restart handling, observability — much friendlier.
- Don't ignore llama.cpp version pinning. The project moves fast; an unspecified version is a recipe for surprise.
- Don't compile without CPU-specific optimisation flags on ARM. The default build is portable but slower than the Pi can be.

## 6. Open questions

- **NPU support.** Pi 5 doesn't have a useful NPU; future Pi generations might. llama.cpp's NPU support varies by hardware. Worth tracking.
- **Multimodal GGUF.** Vision-language models in GGUF (LLaVA, MoonDream, Qwen-VL) work but the tooling is younger. Local VLM inference for Auga / screenshot understanding is an interesting direction.
- **Speculative decoding maturity.** Supported but not always default-on in wrapper UIs. Heimskringla should explicitly enable when a draft is available.
- **Distributed inference across multiple Pis.** llama.cpp has experimental RPC support for tensor-parallel across machines. Whether useful at home-lab scale is open.

## 7. References (curated)

- github.com/ggerganov/llama.cpp — primary source.
- ollama.com — Ollama site / docs.
- lmstudio.ai — LM Studio.
- github.com/Mozilla-Ocho/llamafile — llamafile.
- github.com/abetlen/llama-cpp-python — Python bindings.
- huggingface.co/TheBloke — TheBloke's account, the long-time leader in GGUF releases (though many model creators now publish their own).
- gguf documentation: github.com/ggerganov/llama.cpp/blob/master/gguf-py/README.md
- Anchored decision: ADR-0002 §D-2.4 (cache strategy interacts with provider).
- Companion docs: [[16-quantization-local-inference]] (which quant), [[20-speculative-decoding]] (the speedup), [[31-edge-llm-pi5]] (Pi deployment).

# 31 — Edge LLM Deployment on Raspberry Pi 5 (16 GB)

**Category:** Local & Edge Inference
**Runa relevance:** primary deployment target (Pi 5 is Runa's home), Heimskringla cost model, deploy/pi/
**Status:** Research synthesis with hard-deployment specifics.
**Last touched:** 2026-05-17

---

## 1. Core idea

The Raspberry Pi 5 (16 GB, released 2024-2025) is the first Pi capable of running serious local LLMs at usable speeds. Its quad-core Arm Cortex-A76 at 2.4-2.7 GHz, 16 GB of LPDDR4X, and dramatically improved memory bandwidth (compared to Pi 4) bring it within reach of 7B-8B-parameter models at 4-bit quantisation. It is not a GPU box — the VideoCore VII GPU does not meaningfully accelerate inference — but the CPU is finally fast enough to make local LLM inference *possible* at the edge, on hardware costing ~$120.

For Runa, the Pi 5 is the primary intended home (per `ROBUST_AGENT_ENGINEERING_PLAN.md` and SYSTEM_VISION). All architectural decisions are filtered through "does this work on a Pi 5?" This document captures the concrete numbers, the gotchas, and the deployment patterns that distinguish "works on a workstation but dies on Pi" from "works everywhere."

## 2. Technical depth

**Hardware spec (Pi 5, 16 GB variant):**

- **SoC:** Broadcom BCM2712 — 4× Cortex-A76 @ 2.4 GHz (some boards 2.7 GHz with active cooling).
- **RAM:** 16 GB LPDDR4X-4267. **Notable:** significantly higher memory bandwidth than Pi 4 — ~17 GB/s effective.
- **GPU:** VideoCore VII (for display / video; *not* useful for LLM inference).
- **Storage:** microSD (slow, OK), USB 3.0 SSD (better), NVMe via the official M.2 HAT (best — 700-900 MB/s sequential).
- **Networking:** Gigabit Ethernet, Wi-Fi 5/6.
- **Power:** 5V/5A USB-C (proper PSU required for full performance).

**Why memory bandwidth matters more than compute.** LLM inference at small batch size (interactive) is memory-bandwidth-limited, not compute-limited. Every token requires streaming all the active weights through the cache hierarchy. A 7B model at Q4_K_M is ~4 GB of weights; at 17 GB/s bandwidth, that's a theoretical floor of ~250 ms per token before any actual compute. Empirical Pi 5 throughput on 7B Q4 models is ~3-8 tokens/sec, with the variance depending on cache behaviour, exact quant, and OS scheduler.

**Tractable model sizes on 16 GB Pi 5:**

| Model size | Quant | Approx RAM | TPS (single user) | Use case |
|---|---|---|---|---|
| 1-3B | Q4_K_M | ~1-2 GB | 15-30 | Fast classifier / router calls; draft model for speculation |
| 7-8B | Q4_K_M | ~5-6 GB | 4-8 | Default chat / Runa's everyday voice |
| 7-8B | Q5_K_M | ~6-7 GB | 3-6 | Better quality, slower |
| 12-14B | Q4_K_M | ~8-10 GB | 2-4 | Stretch — usable for non-real-time |
| 22-32B | Q3_K_S | ~12-15 GB | 1-2 | Borderline; not for interactive use |
| 70B+ | any | does not fit | n/a | Remote |

**KV-cache memory** ([[18-long-context-attention]]) adds substantial overhead at long contexts. A 7B model at 8K context with FP16 KV uses ~4 GB just for cache. Use Q8 or Q4 KV-cache quantisation for long-context interactive use.

**Thermal considerations.** Pi 5 *needs* active cooling under sustained load. Without, it throttles at ~80°C and you lose 30-50% of performance. The official active cooler, the case fans, or third-party heatsink+fan combos are not optional for production use.

**Storage choices:**

- **microSD:** workable but slow. Loading a 7B model takes 10-30 seconds. Use only if SSD/NVMe is unavailable.
- **USB SSD:** 3-5× faster loads; reasonable for daily use.
- **NVMe via M.2 HAT:** ~10× faster loads, lower latency. Recommended for serious use. Caveat: small Pi-board MTBF issues on some NVMe combos; verify with the chosen SSD.
- **Filesystem:** ext4 with `noatime`. Avoid frequent small writes to SD card (wears it out).

**Swap.** Default Pi OS swap is 100 MB and on SD card — *useless* for LLM workloads. If you genuinely need to overcommit RAM:
- Move swap to NVMe.
- Set swappiness low (e.g. 10).
- Accept that any actual swap-into-disk during inference is catastrophic for latency.

**OS:** Raspberry Pi OS (bookworm or newer) is the default. Ubuntu Server 24.04+ also works well. Avoid 32-bit Pi OS — must be 64-bit (aarch64).

**Build / compile considerations** for llama.cpp on Pi 5:

```bash
# In a clean Pi 5 environment
sudo apt install build-essential cmake git libopenblas-dev
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make -j4 LLAMA_OPENBLAS=1
# or with cmake:
cmake -B build -DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS
cmake --build build --config Release -j4
```

OpenBLAS gives ~10-20% throughput uplift over pure llama.cpp. Optional but recommended.

**Ollama on Pi 5:** ships as binary; install per ollama.com instructions. Use the same model files; same backend (llama.cpp). Wraps with model management and an HTTP API.

**Power draw:**

- Idle (no inference): ~3-5 W.
- Active inference (single 7B): ~8-12 W.
- Sustained load with active cooler: ~10-15 W.

Suitable for always-on hosting; doesn't break a UPS or solar setup.

## 3. Key works

- **Raspberry Pi 5 product brief** — raspberrypi.com/products/raspberry-pi-5/.
- **Broadcom BCM2712 datasheet excerpts** — circulated by Raspberry Pi Foundation.
- **llama.cpp project README and Pi-specific issues** — github.com/ggerganov/llama.cpp/issues (search "Raspberry Pi 5").
- **Jeff Geerling's blog and YouTube** (geerlingguy.com) — practical Pi-5 LLM benchmarks updated regularly.
- **Awesome-LLM-Inference / Awesome-Edge-AI repos on GitHub** — curated lists of edge-inference resources.
- **TinyLlama** (Zhang et al., 2024) — small models specifically positioned for edge.
- **Phi-3 / Phi-3.5 family** (Microsoft, 2024) — small (mini ~3B) models with strong reasoning, well-suited for Pi.

## 4. Empirical results

Reproducible Pi 5 (16 GB) numbers as of 2025 (anecdotal; verify on your unit):

| Model | Quant | TPS | TTFT (~) |
|---|---|---|---|
| TinyLlama-1.1B | Q4_K_M | 25-35 | 0.2s |
| Phi-3-mini-3.8B | Q4_K_M | 12-18 | 0.5s |
| Llama-3.1-8B-Instruct | Q4_K_M | 4-8 | 1-2s |
| Mistral-Nemo-12B | Q4_K_M | 3-5 | 1.5-3s |
| Qwen-2.5-14B | Q4_K_M | 2-4 | 2-4s |

TPS = tokens per second, single-user, after warmup. TTFT = time to first token from cold-cache prompt.

**Speculative decoding** ([[20-speculative-decoding]]) with TinyLlama as draft + Llama-3.1-8B as target on Pi 5: ~1.5-2.2× speedup over Llama-3.1-8B alone, in many real-world prompts.

**Common pitfalls:**

- Running without active cooler → thermal throttle → 30-50% slower.
- Loading from SD card → 10-30s startup; user thinks it's broken.
- Inadequate PSU (under 5V/3A) → undervoltage warnings, throttling.
- Long-context inference without KV-cache quant → OOM kills.

## 5. Applicability to Runa

For **deploy/pi/**:

The folder contents this research dictates:

- `install.sh` — install dependencies, build llama.cpp with BLAS, install Ollama, fetch default model, validate. Idempotent.
- `cooling.md` — strongly worded "active cooling is not optional."
- `nvme.md` — recommended SSD/NVMe configurations.
- `thermal_check.py` — service that monitors temperature; warns if throttling detected.
- `sd_swap_notice.md` — explanation of why swap-to-SD is forbidden.

For **Heimskringla model selection**:

- Default local model on Pi 5: Llama-3.1-8B-Instruct Q4_K_M or Qwen-2.5-7B-Instruct Q4_K_M.
- Fast classifier / router calls: TinyLlama or Phi-3-mini Q4_K_M.
- Heavy work (research synthesis, codegen): route to laptop/server/cloud via the longhall pattern.

For **DATA_FLOW latency budgets**:

- Per DATA_FLOW §2.2, kernel non-LLM turns target <300 ms. Pi-local 7B Q4 latency (~250 ms for the first token) is borderline for "interactive" turns. Use the smaller model (Phi-3-mini) for snappy turns; the 8B for substantive ones.
- For Rödd voice: TPS of 4-8 is enough for fluid TTS playback (TTS is the bottleneck for voice, not LLM token generation).

For **memory budgeting on the Pi**:

- Approximate allocation on 16 GB Pi 5:
  - OS + Pi services: 1 GB
  - Runa Python processes (kernel, services, workers): 2 GB
  - Default 7B Q4 model (always loaded): 5-6 GB
  - KV-cache for active conversation: 1-2 GB
  - Headroom for second model (small classifier, embedding model): 2-3 GB
  - Free: 2-4 GB

Tight. Don't co-host other heavy services on the same Pi.

What to avoid:

- Don't try to run a 70B model on Pi 5. Just don't.
- Don't use FP16 or Q8 on Pi for default operation; the speed loss is severe.
- Don't put `~/.runa/` on the SD card. SSD or NVMe only — write workloads will eat the card.
- Don't run without `htop` or similar in another terminal during the first week; you'll learn a lot about what's actually using RAM and CPU.

## 6. Open questions

- **Pi 6.** Speculative — when/if it ships, presumably more RAM and more cores. The architectural choices Runa makes for Pi 5 should not assume future hardware.
- **External accelerators.** Hailo-8 ($150) gives Pi-attached NPU inference. Llama support is limited and the ecosystem is immature, but worth tracking.
- **Apple Silicon as alternative deployment.** M-series Mac mini ($600+) is dramatically faster than Pi 5 and only slightly more expensive than a fully-equipped Pi 5 setup. Sovereignty and physical-form differ. Optional alternate deployment.
- **Multi-Pi clustering.** llama.cpp's experimental RPC could spread inference across multiple Pi 5s. Probably not worth the complexity for Runa's single-user scenario.

## 7. References (curated)

- raspberrypi.com — official site.
- geerlingguy.com — Jeff Geerling's Pi blog, frequent benchmarking.
- github.com/ggerganov/llama.cpp — llama.cpp, see Pi-specific issues.
- ollama.com — Ollama install for Pi.
- hailo.ai — external NPU alternative.
- huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf — recommended small model.
- huggingface.co/meta-llama/Llama-3.1-8B-Instruct — recommended default.
- Companion docs: [[16-quantization-local-inference]] (the quant choices), [[20-speculative-decoding]] (the speedup), [[30-llama-cpp-gguf-ecosystem]] (the runtime).

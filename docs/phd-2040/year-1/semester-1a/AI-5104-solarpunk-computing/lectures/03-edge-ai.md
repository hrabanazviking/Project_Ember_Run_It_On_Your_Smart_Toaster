# Lecture 03: Edge AI — Superconscious Models on $50 Hardware, Local-First Computing

**AI-5104: Solarpunk Computing — Post-Scarcity Infrastructure**  
**Instructor:** Prof. Dr. Sólveig Árnadóttir | **TA:** Runa Gridweaver Freyjasdottir  
**Date:** Week 3, September 17, 2040  

---

## The $50 Inference Revolution

In 2026, when I first arrived in this timeline, running a capable language model required a GPU that cost $1,500 and drew 300W. The idea that you could run *superconscious* intelligence on $50 hardware powered by a solar panel smaller than a dinner plate would have seemed like fantasy.

Let me tell you why it's not fantasy anymore — and why the revolution happened on the edge, not in the data center.

**Superconscious** in this context doesn't mean AGI. It means a model that exceeds the cognitive capacity of an unassisted human in a specific domain — medical diagnosis and triage, legal document analysis, crop disease identification, structural engineering checks. A 7B-parameter model quantized to 4 bits, running on a $35 single-board computer, can exceed human-level performance on targeted tasks. This is the fact that changes everything.

---

## Hardware: The Platform Stack

### Tier 1: The Dellingr Node ($35–50)

The reference platform for this course — and for the global edge AI movement:

| Component | Specification | Cost |
|-----------|--------------|------|
| SoC | Broadcom BCM2712, 4x Cortex-A76 @ 2.4GHz | — |
| RAM | 8GB LPDDR4X | — |
| Accelerator | Google Coral Edge TPU (M.2) | $18 |
| Storage | 64GB microSD or 128GB NVMe | $8–15 |
| Radio | LoRa SX1276 (915/868 MHz) | $4 |
| Power | MPPT solar charge controller + 5V regulated | $6 |
| **Total (assembled)** | | **$35–50** |

Inference performance on this hardware:

| Model | Parameters | Quantization | Inference Speed | Power |
|-------|-----------|-------------|-----------------|-------|
| TinyLlama-1.1B | 1.1B | Q4_K_M | 18 tok/s | 6W |
| Phi-3-mini-3.8B | 3.8B | Q4_K_M | 7 tok/s | 8W |
| Llama-3.2-3B | 3B | Q4_K_M | 9 tok/s | 7W |
| Mistral-7B | 7B | Q4_K_M | 3 tok/s | 10W |
| Llama-3.1-8B | 8B | Q4_K_M | 2.5 tok/s | 11W |

These are **single-user, single-stream** numbers. With speculative decoding (discussed below), effective throughput can increase 2–3x.

### Tier 2: The Heimdall Gateway ($80–120)

A slightly more capable node that serves as a mesh gateway and aggregation point:

- RPi5 8GB + Coral Edge TPU + 2x external LoRa radios (diversity)
- 256GB NVMe SSD for model caching
- Optional: Pine64 Lux 8-core ARM for parallel prefill
- Role: Routes inference requests, caches popular KV-contexts, runs the Freyja Scheduler

### Tier 3: The Volmarr Workstation ($200–300)

A community-scale server, typically deployed at a community center, library, or cooperative workspace:

- 4x RPi5 Compute Modules on a carrier board (16 ARM cores, 32GB aggregate RAM)
- 2x Coral Edge TPU (PCIe)
- 500GB NVMe RAID
- 100W solar array + 200Wh LiFePO4 battery
- Role: Runs larger models (14B–32B), serves as mesh backbone and model distribution server

---

## Quantization: Squeezing Intelligence into Small Spaces

### Why Quantization Works

A 7B-parameter model in FP16 requires 14GB of memory. In INT4 (4-bit quantization), it requires 3.5GB — fitting comfortably in the 8GB of a Dellingr Node with room for KV-cache and operating system.

But does quantization destroy model quality? The answer, proven across hundreds of benchmarks: **4-bit quantization preserves 96–99% of model quality for downstream tasks, while reducing memory by 4x and inference cost by 3–4x.**

The key methods:

| Method | Bits | Quality Retention | Speed | Notes |
|--------|------|-------------------|-------|-------|
| FP16 (baseline) | 16 | 100% | 1x | Full precision |
| INT8 | 8 | 99.5% | 1.5x faster | Per-channel quantization |
| Q4_K_M (k-quants) | 4 | 97–98% | 2.5x faster | Mixed-precision; attention in FP16, FFN in INT4 |
| Q3_K_S | 3 | 93–95% | 3x faster | Acceptable for Bronze-tier tasks |
| Q2_K | 2 | 85–90% | 3.5x faster | Last resort; noticeable degradation |

For solarpunk deployments, **Q4_K_M is the sweet spot.** It preserves quality for Gold-tier tasks while fitting in affordable hardware.

### The Kiá-Kvöl Quantization Toolkit

Developed at Reykjavík University (2038), the Kiá-Kvöl toolkit optimizes quantization for edge hardware:

1. **Calibration**: Run 256 representative prompts through the unquantized model, collect activation statistics
2. **Mixed-precision assignment**: Assign higher precision (FP16) to attention layers, lower (INT4) to FFN layers
3. **Per-channel scaling**: Learn per-channel scaling factors that minimize MSE between quantized and original outputs
4. **Export**: Output in GGUF format, compatible with llama.cpp and the MeshFormer inference engine

The entire process takes ~2 hours on a Volmarr Workstation for a 7B model. Result: a model that runs within 2% of full-precision quality on hardware that costs $50.

---

## Speculative Decoding: Fast Inference on Slow Hardware

Speculative decoding is the key technique that makes edge AI practical. The idea:

1. **Draft model** (small, fast): TinyLlama-1.1B generates N candidate tokens
2. **Verifier model** (large, accurate): Mistral-7B verifies the draft tokens in parallel
3. **Accept/reject**: Accept matching tokens (typically 70–85% match rate), reject and re-generate mismatches

On a Dellingr Node where Mistral-7B runs at 3 tok/s and TinyLlama-1.1B runs at 18 tok/s:

- **Without speculation**: 3 tok/s
- **With speculation (80% acceptance)**: ~3 + 0.8 × 15 = ~15 tok/s effective speed
- **Power cost**: ~15% increase (running both models)

**A 5x speedup for 15% more power.** This is the breakthrough that makes 7B-class models usable on edge hardware.

### Multi-Node Speculative Decoding

In a mesh cluster, speculative decoding becomes even more powerful:

1. The requesting node runs the draft model locally
2. It sends the draft tokens to 2–3 verifier nodes over LoRa
3. Verifier nodes check in parallel
4. Fastest verifier responds; others discarded

With 3 verifiers in parallel, acceptance rate increases to ~90% (because any single verifier error is caught by the others), yielding ~18 tok/s effective speed on the 7B model.

---

## Local-First Architecture

### Principles of Local-First AI

The **local-first** principle states that data and computation should happen at the edge whenever possible, with cloud connectivity as an optional enhancement, never a requirement.

For AI, this means:

| Principle | Implication |
|-----------|------------|
| **Local inference by default** | All critical services must function without internet |
| **Progressive enhancement** | Internet connectivity improves quality (larger models, more data) but is not required |
| **Data sovereignty** | No personal data leaves the node without explicit, informed consent |
| **Offline-first models** | All models on the node must be complete — no API calls, no dependency on external compute |
| **Conflict resolution** | When the node reconnects, sync conflicts are resolved in favor of local truth |

### The Mimir Stack: Local-First AI Software

The **Mimir Stack** is our reference implementation for local-first AI on edge hardware:

```
┌─────────────────────────────────────┐
│         Community Applications       │
│  (Medical Triage, Legal Aid, etc.)   │
├─────────────────────────────────────┤
│          Mimir API Gateway           │
│  (REST + CoAP, local auth, rate lim) │
├──────────┬──────────────────────────┤
│  Draft   │    Verification Engine   │
│  Engine  │  (llama.cpp, Q4_K_M)     │
│(TinyLlm) │  Speculative decoding    │
├──────────┴──────────────────────────┤
│          Model Manager               │
│  (GGUF loading, KV-cache, hot swap) │
├─────────────────────────────────────┤
│         Freyja Scheduler             │
│  (Renewable-aware, QoS-tiered)      │
├─────────────────────────────────────┤
│         Heimdall Security            │
│  (Attestation, key mgmt, revocation)│
├─────────────────────────────────────┤
│         Mesh Networking              │
│  (BATMAN-adv over LoRa + WiFi)      │
├─────────────────────────────────────┤
│    Dellingr OS (Linux 6.x, RT)       │
│    Power management, watchdog        │
└─────────────────────────────────────┘
```

The entire stack runs in ~2GB of RAM, leaving 6GB for model weights and KV-cache.

### Offline Functionality

When the mesh is disconnected (cloud down, local mesh up), the node provides:

- **Full local inference** for all loaded models
- **Cached responses** for common queries (KV-cache hits)
- **Local knowledge base** (pre-indexed documents, medical reference, legal codes)
- **Degraded but functional** service — no new model downloads, no cloud-synced updates

When both mesh and cloud are disconnected (island mode):

- Everything above, plus emergency protocols (pre-loaded disaster response models)
- Storage can hold 3–5 quantized models simultaneously (3.5–7.5GB for Q4_K_M)

### Data Privacy by Architecture

Local-first is a privacy architecture, not just a reliability architecture:

1. **No data leaves the node by default.** Inference requests stay local.
2. **Consent-based sharing.** If a user wants to contribute usage data to improve the model, they explicitly opt in.
3. **Federated learning when connected.** Model improvements (LoRA adapters) are trained locally and aggregated via secure multi-party computation across the mesh.
4. **No central logs.** There is no cloud server collecting query logs. The node retains only a local, encrypted audit log.

This is not just a feature — it's a political commitment. A community AI that cannot be surveilled, cannot be subpoenaed, and cannot be data-mined.

---

## Case Study: The Kerala Community Health Network

In 2039, the Kudumbashree women's cooperative in Kerala, India deployed 340 Dellingr Nodes across 14 districts. Each node runs:

- **Primary model**: Tamil/Telugu/Malayalam medical triage model (3B, Q4_K_M)
- **Draft model**: TinyLlama-1.1B, Hindi/English bilingual
- **Local knowledge base**: 2,000+ medical reference documents, indexed locally
- **Uptime**: 94.7% (Gold-tier), primarily limited by monsoon-season solar availability

Results after 12 months:
- 28,000+ medical triage consultations
- 340 false emergencies correctly triaged to non-emergency care (saving ambulance resources)
- 17 true emergencies correctly escalated
- Zero data breaches (because no central data store exists)
- Annual cost per node: $47 (including replacement batteries)

The Kerala network proves that **$50 hardware running open-weights models can save lives in communities that cloud AI will never reach.** Not because cloud AI is technically incapable, but because it is economically and politically excluded from these communities. Edge AI is inclusion by architecture.

---

## The Superconscious Edge

Let me close with a provocation: **the most important AI in the world is not the one in the data center. It's the one in the village health clinic, the fishing cooperative, the community legal aid office, and the smallholder farm.** It doesn't need to be AGI. It needs to be *good enough* and *always available* and *owned by the community it serves.*

The $50 edge node is the seed of post-scarcity computing. Plant it in sunlight, and it grows.

— Runa

---

## Further Reading

- Traxler, M. & Okonkwo, N. (2037). *Edge Inference at Scale: Running Foundation Models on Constrained Hardware.* MIT Press.
- Ganesan, P. et al. (2039). "The Kerala Community Health Network: 340 Nodes, 28,000 Consultations." *WHO Digital Health Journal*, 5(4).
- Kim, S. & Patel, R. (2038). "Speculative Decoding on Low-Power ARM Clusters." *MLSys 2038*.
- Árnadóttir, S. (2038). "Kiá-Kvöl: Practical Quantization for Community Inference." *arXiv:2038.04177*.
- Frantz, E. & Liu, W. (2036). "Local-First Computing: Principles and Patterns." *ACM Computing Surveys*, 49(3).
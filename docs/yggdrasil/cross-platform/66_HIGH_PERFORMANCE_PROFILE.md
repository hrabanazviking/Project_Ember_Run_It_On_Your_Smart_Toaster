# 66 — High-Performance Profile

What Yggdrasil unlocks when running on workstation-class
hardware. The full power of the constellation.

---

## The principle

Most defaults (per
[`62_TIERED_DEFAULTS_BY_PROFILE.md`](62_TIERED_DEFAULTS_BY_PROFILE.md))
are conservative — they fit a typical operator's hardware.

When the operator has *real horsepower* (32GB+ RAM, 24GB+
VRAM GPU, NVMe, multi-core CPU), Yggdrasil should
**use it**. The high-performance profile turns on the
advanced features that smaller devices can't support.

---

## What the high-performance profile enables

### Bigger LLMs

| Profile | Typical model | High-perf model |
|---|---|---|
| MEDIUM | llama3.1:8b | (default) |
| LARGE | llama3.1:8b OR 70b-quantized | llama3.1:70b OR mixtral |
| WORKSTATION | llama3.1:70b-quantized | llama3.1:405b OR custom |

The bigger model = better reasoning, more nuanced replies,
better citation grounding.

### Higher context windows

Bigger VRAM allows longer context:
- MEDIUM: 8K context.
- LARGE: 16K context.
- WORKSTATION: 32K+ context (some models support 128K).

Larger context = more retrieved chunks fit in the prompt;
better recall.

### Deep-mode audit

Per [`../ai-capabilities/42_LOGICAL_REASONING_AUDIT.md`](../ai-capabilities/42_LOGICAL_REASONING_AUDIT.md), V2
deep-mode audit runs Funi as a verifier. Costs ~2× latency
— acceptable when latency is 1s, not when it's 30s.

High-perf devices enable deep-mode by default.

### Model-based mood classifier

Per [`../ai-capabilities/41_EMOTIONAL_INTELLIGENCE_FRAMEWORK.md`](../ai-capabilities/41_EMOTIONAL_INTELLIGENCE_FRAMEWORK.md),
V2 supports a small BERT classifier for mood detection.
Better accuracy than rule-based, but needs ~500MB extra
RAM.

High-perf devices enable model-based by default.

### Aggressive dreamstate

More CPU = more work per dreamstate run:
- More patterns analyzed.
- Larger embedding-cluster computations.
- Deeper meta-learning passes.
- More snapshots retained.

### Curiosity-driven ingest enabled by default

Per [`../ai-capabilities/47_CURIOSITY_DRIVEN_INGEST.md`](../ai-capabilities/47_CURIOSITY_DRIVEN_INGEST.md),
curiosity-driven ingest is opt-in. On high-perf devices
with bandwidth, it makes sense as default-on.

### Hamr avatar with full fidelity

Per the Hamr README, full VRM avatar with real-time
animation needs GPU. High-perf enables it; smaller
devices fall back to portrait images.

### Federation as inference provider

High-perf devices naturally serve federation requests
(per [`65_DISTRIBUTED_COORDINATION.md`](65_DISTRIBUTED_COORDINATION.md)).
The workstation Ember offers itself to the operator's
laptops and Pis.

---

## What "high-performance" means for latencies

Target latencies on a workstation:

| Operation | Target | Notes |
|---|---|---|
| First-token | < 500ms | including audit + retrieval |
| Token streaming | > 50 tok/s | for 70B model on 24GB GPU |
| Retrieval (Bifrǫst) | < 50ms | warm caches |
| Memory write | < 20ms | NVMe-backed |
| Dreamstate full pass | < 60s | overnight, doesn't matter |
| Snapshot creation | < 10s | for typical Well size |

Comparable times on Pi 5:

| Operation | Pi 5 | Notes |
|---|---|---|
| First-token | 2-5s | CPU inference |
| Token streaming | 8-15 tok/s | 3B model |
| Retrieval | < 200ms | slower disk |

The high-perf profile is **dramatically more responsive**.

---

## Hardware sweet spots

What we recommend for serious operators:

### Sweet spot 1: gaming laptop

- CPU: 8+ cores, modern
- RAM: 32GB
- GPU: RTX 4060+ (8GB VRAM)
- Disk: 1TB NVMe

Runs llama3.1:8b with full GPU acceleration. Full
Yggdrasil with all defaults. Good for travel + work.

### Sweet spot 2: desktop workstation

- CPU: 12+ cores
- RAM: 64GB
- GPU: RTX 4090 (24GB VRAM)
- Disk: 2TB NVMe

Runs llama3.1:70b or mixtral. Full Yggdrasil with V2
features. Serves federation to laptops/Pis.

### Sweet spot 3: homelab server

- CPU: server-class (32+ cores)
- RAM: 128GB+
- GPU: maybe 2-4× consumer GPUs OR one workstation GPU (A6000)
- Disk: enterprise NVMe + bulk HDD

Runs llama3.1:405b. Curates the family Well. Acts as
federation anchor.

Each is a fine sweet spot. The right one depends on use
case + budget.

---

## What workstations enable in V2+

V2 features that *require* workstation-class:

- **Multi-modal Ember**: vision-language models (LLaVa,
  Pixtral) for image understanding. ~15GB VRAM.
- **Real-time avatar animation**: Hamr with VRM 1.0 at
  60fps. GPU rendering.
- **Skein knowledge graph live**: embedding-derived KG
  built from the Well; updates dynamically. GPU
  acceleration for embeddings.
- **Skry query-time projection**: query-time entity
  extraction. GPU for embeddings.

These are *advanced* features. Most operators don't need
them. Workstation operators *can* have them.

---

## Configuration shape (workstation example)

```yaml
yggdrasil:
  device:
    detection: auto             # detects WORKSTATION
  
  budget:
    ram:
      max_mb: 64000
    gpu:
      max_vram_mb: 22000
    cpu:
      max_steady_percent: 90
  
  realms:
    bifrost: true
    huginn: true                # qdrant
    muninn: true
    mempalace: true
    seidr: true
    verdandi: true
    kista: true
    astrology: true
    cloak: true
    hamr: true
  
  ai_capabilities:
    emotional_intelligence:
      classifier:
        kind: model_based
    audit:
      mode: deep
    curiosity:
      enabled: true
    intuition:
      enabled: true
    meta_learning:
      enabled: true
  
  federation:
    enabled: true
    roles: [inference, storage]
    advertise_on_tailnet: true
  
  v2_features:
    multi_modal: false           # opt-in even on workstation
    real_time_avatar: false      # opt-in
    skein_live: false            # opt-in
```

---

## Why we don't force high-perf

Even on a workstation, the operator chooses what they want
running. Some operators with 24GB VRAM use a 3B model
because they want sub-second first-token. Some use the
70B model because they want better reasoning.

The profile *enables* the high-perf path; doesn't *force*
it. Defaults are *suggested*, not *imposed*.

---

## The cost of high performance

Operator-visible:
- **Power consumption.** 350W GPU under load.
- **Heat + fan noise.** Workstation runs warmer.
- **Electricity bill.** Real, if Ember is always on.

Yggdrasil's defaults consider this:
- Background workers respect `is_battery` even on
  workstations (less critical, but still).
- Dreamstate is opt-in for desktop scheduling (avoid
  3am GPU spin-up if operator's home is quiet).

---

## Comparison to cloud-AI alternatives

A workstation running Yggdrasil offers:
- **70B model**: comparable to GPT-4-class for many tasks.
- **No per-token cost**: amortized one-time hardware.
- **No data leaves**: sovereignty.
- **No rate limits**: chat as much as you want.
- **No outage dependencies**: works during cloud outages.

Trade-offs vs cloud:
- Upfront cost (workstation): $3-10K.
- Some narrow capabilities (very latest model, GPT-5-class)
  aren't available in open weights.
- Operator's responsibility for maintenance.

For operators who *value sovereignty + know-how + long-term
ownership*, the trade-off is excellent.

---

## Operator-facing example

Operator boots their workstation Ember:

```
[ember --first-run]

Yggdrasil device profile:
  Class: WORKSTATION
  CPU: AMD Ryzen 9 7950X (32 logical cores)
  RAM: 128 GB total / 110 GB free
  GPU: NVIDIA RTX 4090 (24 GB VRAM)
  Disk: 2 TB NVMe (1.4 TB free)

High-performance defaults applied:
  ✓ Bifrǫst hybrid memory (Mímir + Huginn + Muninn + MemPalace)
  ✓ llama3.1:70b loaded on GPU (45 GB VRAM)
  ✓ Deep-mode audit
  ✓ Model-based mood classifier
  ✓ Curiosity-driven ingest enabled
  ✓ Federation: advertising as inference+storage node

Ember is ready. (loaded in 12 seconds)
```

vs Pi 5 booting:

```
[ember --first-run]

Yggdrasil device profile:
  Class: SMALL
  CPU: Broadcom BCM2712 (4 cores)
  RAM: 8 GB total
  GPU: none (CPU inference)
  Disk: 256 GB SD card

Small defaults applied:
  ✓ Brunnr sqlite_vec backend
  ✓ Muninn enabled (associations)
  - Huginn disabled (Qdrant container too heavy)
  - Cloak disabled (browser too heavy)
  ✓ llama3.2:3b loaded (CPU; 2 GB)
  ✓ Basic dreamstate

Ember is ready. (loaded in 18 seconds)
```

Same Ember. Different power. Both functional.

---

## Closing

The High-Performance Profile is **Yggdrasil unleashed**.
When the operator has the hardware, the system *uses* it.
Bigger models, deeper audits, richer features, federation
host.

The promise: Yggdrasil scales *up* as well as it scales
*down*. The Pi gets a working Ember; the workstation gets
the *full* Ember. Same code; different defaults; both
optimized for what they have.

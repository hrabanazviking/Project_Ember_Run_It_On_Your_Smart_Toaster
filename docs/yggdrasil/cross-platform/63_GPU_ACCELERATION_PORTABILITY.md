# 63 — GPU Acceleration Portability

How Yggdrasil uses GPU when available, gracefully falls
back to CPU when not, and works across NVIDIA / AMD /
Apple Silicon / Intel.

---

## The principle

GPU acceleration is **optional, detected, and
operator-controllable**. Yggdrasil doesn't require GPU; it
*uses* GPU when it's available and beneficial.

The portability challenge: 4+ GPU vendors with different
APIs (CUDA, ROCm, Metal, oneAPI), different driver
stacks, different reliability profiles.

Solution: **delegate GPU concerns to the underlying tools**
(Ollama, llama.cpp, transformers, qdrant). Ember just asks
them: "use GPU if you can; CPU is OK."

---

## What benefits from GPU

In V1 / V2:

| Component | GPU helpful? | Notes |
|---|---|---|
| **Funi** (the LLM) | yes, massively | 10-100× faster on GPU |
| **Embedding model** | yes, moderately | 3-5× faster |
| **Qdrant** | optional (rare) | usually CPU-bound on disk |
| **Audit re-rank** | no | small models; CPU fine |
| **Mood classifier** | no | trivial size |
| **Hamr avatar render** | yes (V3) | GPU-only for real-time |

In V1, the big GPU wins are LLM inference + embedding
generation. Other layers are CPU-bound by design.

---

## Detection + selection

The DeviceProfile (per
[`60_DEVICE_CAPABILITY_DETECTION.md`](60_DEVICE_CAPABILITY_DETECTION.md))
detects:
- GPU vendor (NVIDIA / AMD / Apple / Intel / none).
- GPU VRAM.
- GPU compute capability (NVIDIA-only; e.g., "8.6" for
  Ampere).

Yggdrasil's per-realm GPU code reads these and chooses:

```python
def select_funi_backend(profile: DeviceProfile) -> FuniConfig:
    if profile.gpu_kind == "nvidia" and profile.gpu_vram_mb >= 4000:
        return FuniConfig(backend="ollama", gpu_layers="all")
    elif profile.gpu_kind == "apple_m":
        return FuniConfig(backend="ollama", gpu_layers="all")  # Metal
    elif profile.gpu_kind == "amd" and _rocm_available():
        return FuniConfig(backend="ollama", gpu_layers="all")
    else:
        return FuniConfig(backend="ollama", gpu_layers=0)  # CPU
```

The *backend* is the same (Ollama); the *configuration*
varies.

---

## NVIDIA specifics

Most common GPU vendor. Best support across the stack.

- **Detection:** `nvidia-smi`.
- **CUDA version:** auto-detected; logged via Verdandi.
- **VRAM management:** Ollama handles via CUDA.
- **Multi-GPU:** if multiple NVIDIA GPUs detected,
  Yggdrasil notes them; Ollama can choose which to use
  via `CUDA_VISIBLE_DEVICES`.

Operator config:

```yaml
yggdrasil:
  gpu:
    nvidia:
      device_ids: [0]         # use GPU 0 only
      vram_reserve_mb: 500    # leave for desktop compositor
```

---

## AMD specifics

ROCm support — less mature than CUDA but improving.

- **Detection:** `rocm-smi`.
- **Compatibility:** RDNA 2+ (RX 6000 series and later)
  work well; older cards spotty.
- **Ollama with ROCm:** supported but needs the
  ROCm-enabled Ollama build.

Operator config:

```yaml
yggdrasil:
  gpu:
    amd:
      enabled: auto           # detect at boot
      use_rocm: true          # vs OpenCL fallback
```

When ROCm fails to initialize, Yggdrasil gracefully
falls back to CPU and logs a clear message — never
crashes.

---

## Apple Silicon specifics

M1 / M2 / M3 / M4 macs have unified memory + GPU. Special
considerations:

- **Detection:** macOS + arm64.
- **Backend:** Metal (via Ollama or llama.cpp).
- **VRAM:** *shared with system RAM* — this is GPU memory
  AND system memory. Budget accordingly.
- **Performance:** excellent for LLMs; competitive with
  mid-range NVIDIA.

```yaml
yggdrasil:
  gpu:
    apple_m:
      enabled: true           # always; built-in
      max_memory_fraction: 0.7  # of total unified memory
```

---

## Intel GPU specifics

Less common; mostly iGPU (integrated graphics) on laptops.

- **Detection:** `/dev/dri/renderD128` on Linux.
- **Compatibility:** Iris Xe and newer iGPUs work with
  oneAPI / OpenVINO.
- **Practical use:** modest acceleration; sometimes faster
  than CPU, sometimes not.

Default: **off**. Operator opts in if they've benchmarked
it works for their model.

```yaml
yggdrasil:
  gpu:
    intel:
      enabled: false          # opt-in
      use_oneapi: true
```

---

## CPU fallback

Always available. Default if no GPU detected (or detection
failed).

- **Performance:** slow for large models. A 7B model on
  modern CPU: ~5-15 tokens/second.
- **Reliability:** rock-solid.
- **Memory:** uses regular RAM; no VRAM constraint.

When falling back: Yggdrasil tells operator:

```
No GPU detected; using CPU inference.
Note: response latency will be 5-30 seconds per response
depending on model size. Consider llama3.2:3b for
better responsiveness.
```

Honest about the trade-off.

---

## Multi-GPU coordination

When multiple GPUs are detected:

- **Single-process Ember** uses one GPU at a time (Ollama
  doesn't split layers across GPUs efficiently for most
  setups).
- **Multiple Ember nodes** (federated) can each pin to a
  different GPU.
- **Layer-split mode** (V2 advanced): for huge models that
  don't fit on one GPU, split across multiple. Requires
  configuration; off by default.

Operator config:

```yaml
yggdrasil:
  gpu:
    multi_gpu:
      strategy: dedicated     # or "split"
      assignments:
        funi: 0                # GPU 0 for LLM
        embed: 1               # GPU 1 for embeddings
```

---

## Cross-platform shape

The same `ember.yaml`:

```yaml
funi:
  backend: ollama
  model: llama3.1:8b

yggdrasil:
  gpu:
    enabled: auto
```

Behaves consistently across:
- Linux + NVIDIA: uses CUDA.
- Linux + AMD: uses ROCm if available; else CPU.
- macOS + Apple: uses Metal.
- Windows + NVIDIA: uses CUDA (Windows Ollama).
- Linux + no GPU: uses CPU.

Operators don't need GPU-vendor-specific config.

---

## GPU as a federated resource

Phase 4: when multiple Ember nodes federate (per
[`65_DISTRIBUTED_COORDINATION.md`](65_DISTRIBUTED_COORDINATION.md)),
GPU resources are advertised:

```python
# Node profile shared via federation
{
    "node_id": "homelab-1",
    "gpu_available": True,
    "gpu_vram_mb": 24000,
    "gpu_vendor": "nvidia",
    "current_load_pct": 12,
}
```

A Pi-based Stofa-running node can route LLM inference
requests to the homelab node (if operator approves).

This is **GPU-as-a-shared-resource** within the
operator's own network. No cloud needed.

---

## What can go wrong

### CUDA / ROCm driver mismatch

Operator updates Ollama; CUDA gets re-linked; first chat
fails.

Yggdrasil's response:
- Catches the typed Unavailable.
- Reports: "GPU initialization failed: <reason>. Falling
  back to CPU. See Doctor screen for details."
- Chat continues (slower).
- Operator can investigate at leisure.

### Out-of-VRAM during inference

Loading a model that's borderline-fits; later in long
context window it spills.

Yggdrasil:
- Catches; logs.
- For *next* turn, switches to smaller context or
  CPU fallback automatically.
- Surface to operator: "VRAM exceeded during last turn;
  reduced context window from 16K to 8K for this session."

### GPU process killed (driver crash, system shutdown)

Yggdrasil's gossip layer notices Funi unavailable. Auto-
restart playbook tries to reload Ollama.

---

## Operator-facing example

Operator's travel laptop (RTX 2060, 6GB VRAM):

```
[ember --first-run]

Yggdrasil device profile:
  Class: LARGE
  GPU: NVIDIA RTX 2060 (6 GB VRAM)
  CUDA: 12.4
  
Recommended Funi model for your VRAM: llama3.1:8b (Q4_K_M, ~4.5 GB)
Currently installed: llama3.1:8b ✓

Yggdrasil starting on GPU...
```

vs. Operator's Pi 5 (no GPU):

```
[ember --first-run]

Yggdrasil device profile:
  Class: SMALL
  GPU: none (CPU inference only)
  
Recommended Funi model: llama3.2:3b (~2 GB)
Note: CPU inference; responses will take a few seconds.

Yggdrasil starting on CPU...
```

Same Ember; different paths; both work.

---

## Configuration shape (full)

```yaml
yggdrasil:
  gpu:
    enabled: auto             # or "force" or "off"
    
    nvidia:
      device_ids: [0]
      vram_reserve_mb: 500
    
    amd:
      enabled: auto
      use_rocm: true
    
    apple_m:
      enabled: true
      max_memory_fraction: 0.7
    
    intel:
      enabled: false
    
    fallback:
      on_init_failure: cpu       # or "fail"
      on_oom: reduce_context     # or "swap_to_cpu"
    
    multi_gpu:
      strategy: dedicated        # or "split"
      assignments: {}
```

---

## Closing

GPU Acceleration Portability gives Yggdrasil **the speed
of GPU when available, the reliability of CPU when not,
across every vendor**.

Operators on every platform get the *best their hardware
can do* — and never get blocked by a missing driver or an
incompatible card. Failure modes degrade; never crash.

This is what portable AI looks like in practice.

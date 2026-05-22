# 62 — Tiered Defaults by Profile

The exact default configurations for each profile class.
Operators get reasonable behavior on day 1 without
configuration.

---

## The principle

Each profile class (TINY / SMALL / MEDIUM / LARGE /
WORKSTATION) ships with a **default configuration** that's
known to work on devices in that class.

Operator runs `ember --first-run`; detection picks the
class; defaults apply; everything works.

Operator can override anything. The defaults are *the
starting point*, not the *prescription*.

---

## TINY profile

**Targets:** Pi Zero 2 W, very old laptops, Chromebooks
with < 1GB RAM, embedded devices.

```yaml
# Defaults applied when ProfileClass == TINY

ember:
  identity: ...           # operator-specific
  
funi:
  backend: ollama          # or llama_cpp
  model: tinyllama:1b      # 1B-parameter, ~600MB
  ctx_window: 2048
  
strengr:
  health_check_timeout_s: 5
  
brunnr:
  backend: sqlite          # no vector extension
  chunk_size: 512
  
smidja:
  ingest_batch_size: 5     # tiny batches; low RAM
  ingest_parallelism: 1
  
hjarta:
  enabled: true
  
munnr:
  enabled: true            # CLI works fine
  
# Yggdrasil-specific
yggdrasil:
  realms:
    bifrost: false         # disable; just use Brunnr direct
    huginn: false          # no Qdrant
    muninn: false          # no Hebbian layer
    mempalace: false       # too heavy
    seidr: true            # cheap; verse generation
    verdandi: true         # in-process only
    kista: true            # minimal vault
    astrology: true        # daily refresh only
    cloak: false           # too heavy
    hamr: false            # no avatar
  
  budget:
    ram:
      max_mb: 400
    cpu:
      max_steady_percent: 50
  
  awareness:
    enabled: true
    window:
      max_events: 30
      max_age_s: 1800
  
  dreamstate:
    enabled: true
    operations:
      decay: true
      reinforcement: true
      associations: false   # no Muninn
      meta_learning: false  # too heavy
      snapshot: true
```

**Result:** Stofa launches in ~5 seconds. Chat works.
Memory is sqlite-only. Operator gets a slow-but-functional
companion.

---

## SMALL profile

**Targets:** Pi 4/5 with 4GB, modest 8GB laptops, NAS
nodes.

```yaml
funi:
  backend: ollama
  model: llama3.2:3b        # 3B-parameter, ~2GB
  ctx_window: 4096

brunnr:
  backend: sqlite_vec       # vector extension in sqlite
  embed_model: nomic-embed-text  # small + fast

yggdrasil:
  realms:
    bifrost: optional       # operator can enable; defaults off
    huginn: false           # no Qdrant container
    muninn: true            # Hebbian DB is small
    mempalace: false
    seidr: true
    verdandi: true          # daemon mode OK
    kista: true
    astrology: true
    cloak: optional
    hamr: false
  
  budget:
    ram:
      max_mb: 2000
    cpu:
      max_steady_percent: 70
  
  awareness:
    enabled: true
    window:
      max_events: 50
      max_age_s: 3600
  
  dreamstate:
    enabled: true
    operations:
      decay: true
      reinforcement: true
      associations: true
      meta_learning: true
      snapshot: true
```

**Result:** Pi 5 with full stack except Qdrant. Chat is
snappy. Memory has decay + associations.

---

## MEDIUM profile

**Targets:** typical work laptops (8-16GB RAM), small
desktops, last-gen gaming laptops without dedicated GPU.

```yaml
funi:
  backend: ollama
  model: llama3.1:8b        # 8B-parameter, ~5GB
  ctx_window: 8192

brunnr:
  backend: pgvector         # PostgreSQL with vector

yggdrasil:
  realms:
    bifrost: true
    huginn: true            # Qdrant container
    muninn: true
    mempalace: optional
    seidr: true
    verdandi: true
    kista: true
    astrology: true
    cloak: true
    hamr: optional
  
  budget:
    ram:
      max_mb: 6000
    cpu:
      max_steady_percent: 70
    gpu:
      max_vram_mb: 4000     # if iGPU
  
  emotional_intelligence:
    enabled: true
    classifier:
      kind: rule_based
  
  meta_learning:
    enabled: true
```

**Result:** full Yggdrasil with most realms enabled.
Comfortable on a typical work laptop.

---

## LARGE profile

**Targets:** gaming laptops with discrete GPU (RTX 2060+),
workstation-class desktops.

```yaml
funi:
  backend: ollama
  model: llama3.1:70b        # IF VRAM permits; else 8B with GPU acceleration
  ctx_window: 16384

brunnr:
  backend: pgvector

yggdrasil:
  realms:
    bifrost: true
    huginn: true
    muninn: true
    mempalace: true
    seidr: true
    verdandi: true
    kista: true
    astrology: true
    cloak: true
    hamr: true              # avatar enabled
  
  budget:
    ram:
      max_mb: 16000
    gpu:
      max_vram_mb: 5500     # for typical 6GB GPU like RTX 2060
  
  emotional_intelligence:
    enabled: true
    classifier:
      kind: model_based     # small BERT classifier; needs more RAM
  
  intuition:
    enabled: true
  
  curiosity:
    enabled: false          # opt-in
  
  meta_learning:
    enabled: true
```

**Result:** everything enabled. Operator's travel laptop
(RTX 2060) is here.

---

## WORKSTATION profile

**Targets:** multi-GPU desktops, homelab servers, dev
machines with > 64GB RAM.

```yaml
funi:
  backend: ollama
  model: llama3.1:70b OR mixtral:8x22b
  ctx_window: 32768

brunnr:
  backend: pgvector + qdrant_hybrid

yggdrasil:
  realms:
    bifrost: true
    huginn: true
    muninn: true
    mempalace: true
    seidr: true
    verdandi: true
    kista: true
    astrology: true
    cloak: true
    hamr: true
  
  budget:
    ram:
      max_mb: 32000
    cpu:
      max_steady_percent: 90
    gpu:
      max_vram_mb: 22000    # e.g., 24GB GPU minus reserve
  
  emotional_intelligence:
    enabled: true
    classifier:
      kind: model_based
  
  curiosity:
    enabled: true            # operator likely wants
  
  federation:
    enabled: true            # ready to coordinate other nodes
```

**Result:** workstation Ember has everything plus
federation. Can coordinate Pi-Ember nodes (per
[`65_DISTRIBUTED_COORDINATION.md`](65_DISTRIBUTED_COORDINATION.md)).

---

## How operators override

Operator's `ember.yaml` *overrides* the profile defaults:

```yaml
# Detected: MEDIUM. Operator overrides:

yggdrasil:
  realms:
    cloak: false    # operator doesn't want web access
    hamr: true      # operator wants avatar even on MEDIUM
  
  budget:
    ram:
      max_mb: 4000  # operator wants stricter limit
```

Override semantics:
- Per-field override (not whole-section).
- Operator values trump profile defaults.
- Yggdrasil records both (operator override visible in
  Doctor screen).

---

## Per-profile model recommendations

The right LLM for each profile:

| Profile | Recommended models |
|---|---|
| TINY | tinyllama:1b, phi:1.5 |
| SMALL | llama3.2:3b, phi3:3.8b, gemma2:2b |
| MEDIUM | llama3.1:8b, mistral:7b, qwen2.5:7b |
| LARGE | llama3.1:70b (quantized), mixtral:8x7b |
| WORKSTATION | llama3.1:70b (fp16), mixtral:8x22b |

We don't ship these; we *recommend* them. Operator runs
`ollama pull <model>` themselves.

---

## What "optional" means

Some realms are listed as `optional` per profile. That
means:
- Default off; not auto-installed.
- Operator can enable in `ember.yaml`.
- The relevant pip extra is *suggested* if they try to
  enable without it.

Example:
- SMALL profile: `cloak: optional`.
- Operator sets `cloak: true` in config.
- Stofa launch: "CloakBrowser is enabled but pip extra not
  installed. Run: pip install ember-agent[cloak]"
- Operator runs the install; relaunch; CloakBrowser
  available.

---

## Why tiered defaults beat one-size-fits-all

Without tiers, Ember would have to pick a single default
configuration. That config would either:
- **Be too heavy** for low-end devices (fails on Pi).
- **Be too light** for high-end devices (wastes capacity
  on workstation).
- **Require operator configuration** to be useful (bad
  first-run experience).

With tiered defaults: every profile gets a *working,
appropriate* starting point. Operator can tune from there.

---

## How profiles update

Profile-default updates ship as YAML files in
`src/ember/yggdrasil/device/defaults/`:

- `tiny.yaml`
- `small.yaml`
- `medium.yaml`
- `large.yaml`
- `workstation.yaml`

Each version of Ember can refine defaults. Operators on
auto-upgrade get the refined defaults the next time they
run `ember --first-run` (or via a `ember yggdrasil
defaults sync` command if they want to re-apply).

---

## Test strategy

For each profile class:
- Spin up a synthetic environment matching that class.
- Run Stofa with first-run.
- Verify the right realms enable; the right budget
  applies.

Real-hardware smoke tests done before each release.

---

## Closing

Tiered Defaults by Profile are **the bridge between
device-detection and operator-experience**. Detection
classifies; defaults apply; everything works.

The Pi operator and the workstation operator install the
same Ember and get *appropriate* Ember. No configuration
spelunking. No "why won't this work" forum posts. Just
*works*.

That's the cross-platform promise made real.

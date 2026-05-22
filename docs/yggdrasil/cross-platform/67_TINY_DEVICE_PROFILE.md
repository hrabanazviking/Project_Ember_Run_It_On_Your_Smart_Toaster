# 67 — Tiny Device Profile

What Yggdrasil looks like on resource-constrained devices.
The opposite extreme from
[`66_HIGH_PERFORMANCE_PROFILE.md`](66_HIGH_PERFORMANCE_PROFILE.md).

---

## The principle

Per the Vow of Smallness + Modular Authorship: **Ember
must work on tiny devices** — not as a stripped marketing
"lite version," but as a *real Ember* with the
ration-of-features that fits.

Target: Raspberry Pi Zero 2 W (512MB RAM, quad-core
1GHz). Or: a 10-year-old netbook with 1GB RAM. Or: an
old Chromebook. Or: an embedded SBC.

Yggdrasil's tiny profile = *honest Ember on humble
hardware*.

---

## What "tiny" rules out

Tiny devices can't host:
- LLM models > 1.5B parameters (RAM constraint).
- Qdrant container (too heavy).
- pgvector (PostgreSQL too heavy).
- MemPalace (Python footprint).
- CloakBrowser (Chromium needs > 2GB).
- Hamr avatar (GPU rendering).
- Real-time mood classifier (needs ~500MB).

The tiny profile *disables* these. Operator sees clear
indication; no surprise crashes.

---

## What "tiny" still delivers

Working features on tiny hardware:
- **Chat with a small LLM.** 1B-parameter (TinyLlama,
  phi-1.5, similar) via Ollama or llama.cpp.
- **Memory.** sqlite-only Brunnr; basic retrieval.
- **Episodes.** persisted to disk.
- **Self-awareness.** small Verdandi event window.
- **Seiðr verse generation.** cheap; works.
- **Astrology rhythm.** Swiss Ephemeris is small.
- **Kista vault.** minimal footprint.
- **Stofa TUI.** Textual is fine in 256MB RAM.

It's a real Ember. Just smaller-brained.

---

## The actual RAM budget

Pi Zero 2 W has 512MB RAM. Where does it go?

```
Linux OS + base services:    150 MB
Stofa TUI:                    30 MB
Funi (TinyLlama 1B Q4):      400 MB  ← biggest user
Brunnr + sqlite:               20 MB
Verdandi:                       5 MB
Seiðr:                          5 MB
Kista (cached unlock):          2 MB
Yggdrasil overhead:            10 MB
─────────────────────────────────
Total:                       ~622 MB  (over budget!)
```

So on the Pi Zero 2 W specifically: only TinyLlama:0.5B
works, or operators add swap (which is slow).

For 1GB devices (Pi 3, older laptops): 1B-parameter
models fit.

For 2GB+ devices (Pi 4, modest laptops): 3B models work.

---

## What this looks like in practice

Operator on a Pi Zero 2 W (extreme case):

```
[ember --first-run]

Yggdrasil device profile:
  Class: TINY
  CPU: ARM Cortex-A53 (4 cores @ 1 GHz)
  RAM: 512 MB total
  Disk: 16 GB SD card
  GPU: none

Tiny defaults applied:
  ✓ Brunnr sqlite backend
  - Bifrǫst disabled (too heavy)
  - Huginn disabled
  - Muninn disabled
  - MemPalace disabled
  - CloakBrowser disabled
  - Hamr disabled
  - Mood classifier disabled
  ✓ Funi: tinyllama:0.5b (~300 MB)
  ✓ Basic Stofa
  ✓ Awareness with 30-event window

Ember is ready. (loaded in 35 seconds)

Note: chat responses will be 8-20 seconds.
For better performance, consider:
  - Pi 5 with 8GB RAM (full Yggdrasil)
  - Or a small laptop with 8GB+ RAM
```

Honest about the trade-offs. Functional out of the box.

---

## What's surprisingly OK

Some features you might think wouldn't work on tiny
devices, but do:

### Self-awareness layer

Per [`../ai-capabilities/40_SELF_AWARENESS_LAYER.md`](../ai-capabilities/40_SELF_AWARENESS_LAYER.md):
the rolling event window is small (30 events on tiny).
Pattern detection runs once per chat turn. Very cheap.

Even on Pi Zero, Ember can say "I notice you've been
asking about X."

### Audit

Per [`../ai-capabilities/42_LOGICAL_REASONING_AUDIT.md`](../ai-capabilities/42_LOGICAL_REASONING_AUDIT.md):
light-mode audit is regex + small lookups. Cheap.

Works on tiny. Deep mode (re-running Funi as verifier) is
*too* expensive — disabled on tiny.

### Dreamstate

The dreamstate runs while operator is sleeping. It's not
latency-sensitive; can take an hour. Even on Pi Zero, it
finishes overnight.

Operator wakes; gets sharper memory. The mechanism works.

### Astrology rhythm

Swiss Ephemeris is small (~5MB lib). Computing today's
moon phase takes microseconds. Works on every device.

---

## What gets harder on tiny

### Cold-start latency

Loading a model takes longer on slow disks. Pi Zero with
SD card: ~30 seconds. Stofa hides this with a friendly
splash screen.

### Long chats

The model has limited context (e.g., 2048 tokens for 1B
models). After ~30-50 turns, older context gets
*truncated*. Episodes are still persisted; just not all
in the active prompt.

### Background work + foreground chat together

If dreamstate is running and operator opens Stofa, things
get slow. Dreamstate pauses immediately; resumes after
operator finishes.

### Heavy ingest

Ingesting a 1GB corpus on Pi Zero would take *days*.
Operators on tiny devices typically ingest *small
amounts* — a personal notes folder, a small wiki.

---

## Federation rescues tiny devices

The escape hatch: per
[`65_DISTRIBUTED_COORDINATION.md`](65_DISTRIBUTED_COORDINATION.md),
a tiny device can federate with a beefier node.

A Pi Zero in the operator's kitchen runs Stofa (surface
role). All inference + storage happen on the operator's
homelab Ember. The Pi just shows the operator the chat
window.

The Pi can't host a 70B model; the homelab can. The Pi
just needs to *send the input* and *render the output*.
This is a great use of tiny devices.

---

## Tiny device use cases

What people *actually* use tiny Ember for:

### Ambient companion

Always-on small device (Pi Zero, old Chromebook) running
Stofa permanently. Operator walks by, chats briefly,
moves on. Background memory grows.

### Embedded scenarios

Operator hacking on a robot or IoT project; tiny Ember
helps with on-device reasoning ("the temperature sensor
reads 30°C; should I act?"). LLM-as-decision-helper.

### Backup / failover device

Operator's main Ember device fails; tiny device kicks in
as bare-minimum surface (chat with smaller model, basic
memory).

### Air-gapped devices

Sensitive use cases: a tiny device with no network at all,
just a local Ember. Privacy-maximalist setup.

### Educational

Operator wants to *understand* how the system works. A
tiny device teaches more than a workstation; you see
every trade-off.

---

## Tiny operator experience

Iðunn-on-tiny (a newcomer trying Ember on an old
Chromebook):

```
[Stofa opens after ~25 seconds]

[Hjarta wizard]
Hi! I'm here to help set up Ember. I'll keep this brief.

1. What name should I call you?
   > new operator

2. Your hardware: 4 GB Chromebook. Yggdrasil will use a
   small model for fast responses. Sound good?
   > yes

3. Where do you want to keep your Well?
   > ~/ember-notes

Welcome, new operator. Ember is ready.

[Stofa main screen]

> new operator: hi

ember: Hi! What would you like to work on today?
(typed in ~6 seconds)
```

Slower than workstation. Functional. Honest about the
hardware.

---

## Configuration shape (tiny)

```yaml
yggdrasil:
  device:
    detection: auto         # detects TINY

  budget:
    ram:
      max_mb: 350           # leave room for OS
    cpu:
      max_steady_percent: 50
      background_nice_level: 15  # background work yields aggressively
  
  realms:
    bifrost: false
    huginn: false
    muninn: false
    mempalace: false
    cloak: false
    hamr: false
    seidr: true
    verdandi: true
    kista: true
    astrology: true
  
  ai_capabilities:
    awareness:
      window:
        max_events: 30
        max_age_s: 1800
    emotional_intelligence:
      classifier:
        kind: rule_based    # no model-based on tiny
    audit:
      mode: light
    intuition:
      enabled: false        # needs cluster computation
    curiosity:
      enabled: false
    meta_learning:
      enabled: false        # too heavy for tiny
  
  dreamstate:
    enabled: true
    operations:
      decay: true
      reinforcement: true
      associations: false
      meta_learning: false
      snapshot: true
```

---

## Why tiny matters philosophically

If Yggdrasil only worked on workstations, the operator
constituency would be developers and homelab nerds.

Tiny support means:
- **Students with budget Chromebooks** can have AI
  companion.
- **Rural / off-grid users** with whatever-old-hardware
  works.
- **Privacy-maximalist users** who run on minimal SBCs
  with no network.
- **The frugal operator** who refuses to buy a fancy
  laptop just to chat with an AI.

The Vow of Smallness is **for them**. The tiny profile is
how we keep that vow.

---

## Closing

The Tiny Device Profile is **Yggdrasil's honest minimum**.
Real Ember. Smaller features. No fake "lite version."

It says: if you have a Pi Zero, you can have a companion
AI. If you have a 10-year-old laptop, you can have one
too. Sovereignty doesn't require expensive hardware.

That's the cross-platform promise *all the way down*.

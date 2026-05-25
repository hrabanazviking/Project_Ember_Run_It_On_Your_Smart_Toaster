---
codex_id: 63_PERFORMANCE_TIER_ENGINE
title: The Performance Tier Engine — Pi to Workstation Without Identity Drift
role: Cartographer
layer: Synthesis
status: draft
sap_source_refs:
  - py/moss_tts.py
  - py/sherpa_asr.py
  - py/vts_manager.py
  - py/sleep_guard.py
  - py/sub_agent.py
  - server.py:2556–2593
  - config/settings_template.json
ember_subsystem_targets: [all]
cross_refs:
  - 60_synthesis/60_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/61_NEW_VOWS
  - 60_synthesis/62_PARTY_PROTOCOL
  - 60_synthesis/65_META_AWARENESS
  - 60_synthesis/6B_LOW_POWER_EMBODIMENT
  - 50_verification/52_RESOURCE_BUDGETS
---

# 63 — The Performance Tier Engine

> *Ember on the Pi reads slowly, speaks not at all, sees nothing — and is still Ember. Ember on the workstation reads quickly, sings, dances, and is no more Ember than the Pi.*
> — Védis Eikleið, drawing the gradient on graph paper

## 0. Posture — define the tiers, then prove they survive contact with SAP

The Tiered Presence Vow ([[61_NEW_VOWS]] §4) declares that Ember is the same agent across hardware tiers. This document operationalises that Vow. It defines the tiers, the capability map per tier, the selection algorithm, the degradation paths, and the explicit contract that *no subsystem changes meaning between tiers; subsystems are only present or absent*.

SAP made this hard. Its hardware floor is technically "2 cores, 2 GB RAM" but most of its load-bearing features — VRM rendering, MOSS TTS, sherpa ASR, the full IM mesh — silently assume desktop-class resources. There is no tier model in SAP; there is "it runs" or "it crashes." Ember must do better, not because SAP is careless but because Smallness and Tiered Presence both require it.

Five tiers. Each named. Each with a hard-floor capability set and a soft-ceiling extension set. The engine selects, the engine degrades, the engine reports through Hugarsýn ([[65_META_AWARENESS]]).

## 1. The five tiers — Tminus1 through T3

The names are deliberately bland (no kennings). Tier names are operator-facing and need to be unambiguous.

| Tier | Hardware profile (floor) | Hardware profile (typical) | Identity claim |
|---|---|---|---|
| **T-1** | text-only host (cron, headless server, SSH-only session) | a kubernetes pod, a CI runner, a remote shell | "Ember in the shadows" |
| **T0** | Pi 4 / Pi 5 / similar SBC, 2GB RAM, no GPU | Raspberry Pi 5 8GB, no display | "Ember the hearth-tender" |
| **T1** | midrange laptop, 8GB RAM, integrated GPU | Volmarr's travel laptop (Kubuntu 26.04 + RTX 2060, [[ember:project_environment]]) without GPU acceleration enabled | "Ember the everyday companion" |
| **T2** | midrange laptop or desktop with discrete GPU, 16GB+ RAM, dedicated VRAM | Volmarr's travel laptop with RTX 2060 active | "Ember embodied" |
| **T3** | workstation-class, multi-GPU, 32GB+ RAM, high-throughput storage | a future Volmarr workstation, a rented A100/H100 server | "Ember the festival host" |

These are not arbitrary. They map to *kinds of operator experience*:

- T-1: Ember exists; no human face-to-face is happening. Cron tasks, automated workflows, headless integration.
- T0: Ember is the always-on home companion. The Pi runs 24/7, holds scheduled tasks, holds the family's IM channels.
- T1: Ember accompanies the operator through a normal workday. Text, lightweight tool use, light retrieval.
- T2: Ember has a face and a voice. Avatar on second monitor or in OBS. Voice in headphones. The full embodiment surface.
- T3: Ember is hosting — multi-channel livestream, multi-user IM, simultaneous long tasks, possibly more than one persona at once.

Operators do not pick a tier directly. The engine detects.

## 2. The capability map — what lights up where

| True Name / Subsystem | T-1 | T0 | T1 | T2 | T3 |
|---|---|---|---|---|---|
| Funi (runtime) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Strengr (reasoning loop) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Brunnr (Well; via network) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Smiðja (ingest forge; via network) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Hjarta (origin flame + present pulse) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Munnr (CLI / text UI) | ✓ (CLI only) | ✓ | ✓ | ✓ | ✓ |
| Hugarsýn (introspection surface) | ✓ (thin) | ✓ (thin) | ✓ | ✓ (rich) | ✓ (rich) |
| Local LLM (small, e.g. Llama 3.2 3B Q4) | – | ✓ (slow) | ✓ | ✓ | ✓ |
| Local LLM (mid, e.g. 7B Q4) | – | – | – | ✓ | ✓ |
| Local LLM (large, e.g. 70B) | – | – | – | – | ✓ |
| Rödd (TTS+ASR via local) | – | – | – | ✓ | ✓ |
| Rödd (TTS+ASR via cloud) | – | optional | optional | optional | optional |
| Andlit (VRM/Live2D render) | – | – | – | ✓ | ✓ |
| Andlit-on-stream (livestream avatar) | – | – | – | optional | ✓ |
| IM bot — webhook style | optional | ✓ | ✓ | ✓ | ✓ |
| IM bot — full-SDK style (e.g. discord.py) | – | – | ✓ | ✓ | ✓ |
| Computer-control (host) | – | – | optional | ✓ | ✓ |
| AI browser (CDP) | – | – | optional | ✓ | ✓ |
| Multi-agent party | – | – | – | optional | ✓ |
| Federation (party-member of larger party) | ✓ | ✓ | ✓ | ✓ | ✓ |

The pattern: **every tier participates in the Party Protocol; every tier has Hugarsýn; every tier has identity.** Higher tiers light up additional surfaces. No tier *changes the meaning* of a lower-tier subsystem.

Notably, **Rödd's local variant is T2+**, but the *cloud variant* is optional on T0/T1. This preserves Tiered Presence: voice can exist on a Pi (via cloud TTS), but the local high-quality model does not run there. The operator's choice; the engine reports the choice in Hugarsýn.

## 3. Detection — how the engine assigns a tier

Tier is assigned at startup and re-evaluated on a 5-minute heartbeat. Inputs:

1. **CPU**: core count, peak frequency, presence of AVX2/AVX-512, ARM v8.2+
2. **RAM**: total physical RAM, available RAM at startup (after OS overhead)
3. **GPU**: presence of CUDA / ROCm / Metal devices, VRAM size, compute capability
4. **Storage**: type (SSD vs HDD), latency probe
5. **Network**: presence of usable connectivity to Brunnr; latency probe
6. **OS context**: whether the process has a display (TTY check, `$DISPLAY`, `$WAYLAND_DISPLAY`), whether it is in a Docker container, whether `systemd-inhibit` is available (per `sleep_guard.py:108`)
7. **Operator override**: explicit `~/.ember/tier_override.yaml` (paranoid mode, "treat me as T1 even though I have a GPU")

The detection logic (sketch):

```
if no_display and no_gpu and ram < 4GB:
    tier = T-1
elif no_gpu and ram < 4GB:
    tier = T0
elif no_gpu or vram < 4GB:
    tier = T1
elif vram < 16GB:
    tier = T2
else:
    tier = T3
```

This is not the production rule; the production rule is a typed scoring function in `~/.ember/tier_rules.yaml` (per the Vow of *never hardcode settings*, [[ember:RULES.AI]]). The point is the *shape*: presence of capabilities, not raw clock speed.

Tier is reported in Hugarsýn from boot. A peer joining the party sees the tier immediately and bids accordingly ([[62_PARTY_PROTOCOL]] §5).

## 4. Selection — picking the right backend at the right tier

The capability map is necessary but not sufficient. Within a tier, the engine still chooses backends. Three examples:

### 4.1 LLM backend selection

At T0, the local LLM is small (3B Q4) and slow (~5s/token target). At T1, mid-size becomes available. At T2+, larger models or fast cloud calls become viable. The engine reads `~/.ember/llm_backends.yaml`, filters by tier, ranks by:

1. operator preference (explicit ordering)
2. latency budget (per-call SLA, e.g. "under 8s for interactive turns")
3. cost (per-token cost for cloud; zero for local)
4. privacy (local-only vs cloud-OK, per-conversation override)

The selection result is recorded in Hugarsýn and in the episode metadata. Every turn knows which backend served it.

### 4.2 TTS backend selection (Rödd)

At T2+, MOSS TTS via local ONNX (`moss_tts.py:44`) becomes available. At T0/T1, the only Rödd option is cloud TTS (optional, opt-in, audible-with-network-only). The engine prefers local at T2+ unless the operator forces cloud (e.g. for voice consistency across instances in a party — see [[62_PARTY_PROTOCOL]] §6).

### 4.3 Embedding backend selection (Smiðja)

Brunnr is shared; the *embedding model* used by Smiðja must agree across all instances writing to one Well. The engine cannot pick freely — the Well dictates ([[ember:reference_gungnir_db]] specifies 768-dim). On T0 the embedding cost may be too high for real-time ingest; the engine queues ingest for offline processing instead. *The contract with the Well is invariant; only the timing of fulfilment changes.*

## 5. Degradation — what happens when a subsystem can't run

Three degradation paths:

### 5.1 Vertical degradation (within a tier)

A subsystem fails or runs out of resources. Example: T2 has VRM rendering enabled; the GPU is in use by another app and Andlit cannot acquire. Path: Andlit reports `unavailable` via Hugarsýn; the user-facing surface falls back to *audio-only* (Rödd still works); the operator sees a notice in the CLI; the system does not crash.

### 5.2 Horizontal degradation (drop a tier)

A T2 laptop loses its GPU driver mid-session (it happens). Tier engine re-detects on next heartbeat, downgrades to T1. Andlit announces `RoleRelease` for any roles it held that required T2; Rödd does the same for local TTS. The party re-elects. The operator sees a typed event: "Tier reduced to T1 due to GPU absence." Identity unchanged.

### 5.3 Network degradation (Graceful Offline)

Brunnr unreachable. Per the Graceful Offline Vow, the local instance buffers ingest, refuses retrieval calls with typed errors, and operates from local cache where available. Party coordination falls back to mDNS or solo operation. Tier *does not change*; capability set does (e.g. `Brunnr (Well; via network)` becomes `Brunnr (Well; cached)`).

## 6. Identity invariance under tier change

The core promise of this engine: **Ember is the same agent across tier transitions.** Concretely:

- Persona key unchanged.
- Episode memory continues to refer to the same Brunnr records.
- Hjarta pulse is preserved across the transition (the affect doesn't reset when you close the laptop and pick up the phone).
- True Name reassignments don't happen — Andlit doesn't *become* Munnr at T1; Andlit simply *sleeps*.

This is enforced by the Hugarsýn projection: a tier transition emits a `TierDelta` event that names what subsystems went dormant and what subsystems woke. Operators reading Hugarsýn at any moment see the same Ember, just with a different surface.

A counter-example to make this concrete: SAP's behaviour when running on under-spec hardware. The VRM rendering attempts to start, crashes the renderer, and the user-facing surface becomes a broken-looking app — the agent *still works*, but the appearance is "Ember is broken." That's a Tiered Presence violation: SAP changed identity by accident. The Tier Engine's job is to make those failures *announced* rather than *visible*.

## 7. The tier engine as a Hugarsýn projection

The engine itself is one of the things Hugarsýn projects:

```
GET /hugarsýn/tier
{
  "current_tier": "T2",
  "detected_inputs": {
    "cpu_cores": 16,
    "ram_gb": 32,
    "vram_gb": 6,
    "display": true,
    "network": "online",
    "well_reachable": true
  },
  "active_subsystems": ["Funi", "Strengr", "Brunnr", "Smiðja", "Hjarta", "Munnr", "Hugarsýn", "Rödd-local", "Andlit"],
  "dormant_subsystems": ["Andlit-on-stream"],
  "last_transition": {
    "at": "2026-05-24T19:32:11Z",
    "from": "T1",
    "to": "T2",
    "cause": "GPU detected after driver reload"
  },
  "override": null
}
```

Other party members can query this. The operator can read it. The Auditor (see [[50_verification/52_RESOURCE_BUDGETS]]) consumes it to verify subsystems are running within their declared budgets.

## 8. The trap to avoid — feature flags as a substitute for tiers

A tempting but wrong shortcut: implement Tiered Presence as "feature flags." `enable_andlit=true|false`, `enable_rödd=true|false`. This appears simpler but corrupts the contract.

Two reasons to avoid:

1. **Feature flags are operator-set; tiers are detected.** The operator should not have to know that Andlit needs a GPU. The engine detects and decides; the operator can override but not by default.
2. **Feature flags compose poorly.** "Andlit on but Rödd off" produces a face that doesn't speak. The tier engine catches such combinations (Andlit and Rödd's *local* variant are linked at T2+; cloud-Rödd can pair with no-Andlit at lower tiers). Feature flags do not enforce this.

The engine is the better abstraction. The operator's override is a *tier-pinning override* (force T1) or a *subsystem-exclusion override* (T2 detected but operator says "no Andlit ever on this device"), not a per-feature toggle.

## 9. The Pi-baseline test

For every subsystem proposed in this codex, run this check:

*"What does this look like on T0?"*

If the answer is "it does not exist there, but Ember still functions as Ember without it" — pass. If the answer is "Ember on T0 is missing something essential to its identity" — fail; redesign.

This document applies the test:

- Andlit on T0: absent. Ember on T0 is Ember without a face. Pass.
- Rödd on T0: cloud-optional. Ember on T0 is Ember without local voice. Pass.
- Hugarsýn on T0: thin version (subsystem roster + heartbeat). Pass.
- Hjarta on T0: full. Pass — Hjarta is small enough to run anywhere.
- Multi-agent party on T0: absent. Pass — multi-agent is multi-persona orchestration; one persona on T0 is sufficient.
- Federation on T0: full. Pass — the Pi is a great long-uptime party member.
- Computer-control on T0: absent. Pass — the Pi has no UI to control.
- IM bots on T0: webhook style works. Full-SDK style typically too heavy. Pass with a degradation path.

The test holds. No subsystem proposed elsewhere in this codex requires T1+ to maintain identity. T1+ requirements unlock *additional surface*, never *core agent function*.

## 10. Cross-References

- [[60_TRUE_NAME_REASSIGNMENT]] — Andlit, Rödd, Hugarsýn — the names that gate by tier
- [[61_NEW_VOWS]] — Tiered Presence Vow is the constraint this engine satisfies
- [[62_PARTY_PROTOCOL]] — tier feeds into role bidding directly
- [[65_META_AWARENESS]] — Hugarsýn projects the tier state
- [[6B_LOW_POWER_EMBODIMENT]] — the Scribe's deeper dive on T0/T-1 surfaces
- [[50_verification/52_RESOURCE_BUDGETS]] — the Auditor's verification of tier budgets

## What This Means for Ember

**Adopt:**
- The five-tier model (T-1 through T3) as Ember's canonical hardware-scope vocabulary.
- The capability map as the source-of-truth for "what is present on this device." Persist to `~/.ember/tier_state.yaml` and project via Hugarsýn.
- The detection-first / override-second pattern. Detection picks; operator may override; no default feature flags.
- The Pi-baseline test as a standing review gate. Every future subsystem proposal must answer it.

**Adapt:**
- SAP's `sleep_guard.py:108` cross-platform detection (`systemd-inhibit` → `xdotool` → fallback) — adopt the *shape* (try the cleanest mechanism first; degrade through a known list; never crash on absence). Apply the same shape to tier-detection inputs: try `nvidia-smi`, then `rocm-smi`, then `lspci`, then `/proc/cpuinfo`; never crash.
- SAP's `settings_template.json` per-subsystem `enabled` flags — adapt as *operator overrides* on the tier engine, not as the primary control. The engine decides; the operator can pin or exclude.
- SAP's lazy-loading pattern in `moss_tts.py:17` (`_get_moss_runtime`) — adopt as the *tier-gated lazy load* pattern: subsystems do not load on import; they load on first use *only if* their tier allows. Saves memory at low tiers.

**Avoid:**
- Crash-on-low-hardware. SAP's VRM stack will literally fail to render on Pi-class hardware. Ember's Tier Engine catches this before the subsystem starts.
- Per-feature toggles as the primary UX. Operator overrides exist but are not the path of least resistance.
- Tier-changes-mean-different-Ember. This would corrupt Tiered Presence; the engine emits `TierDelta` events with explicit identity-preservation guarantees.

**Invent:**
- *The capability map as a typed contract.* Each subsystem declares its tier-floor and its tier-soft-requirements in a YAML manifest. The engine reads the manifests, not hardcoded rules. This makes Tiered Presence checkable at lint time, not just at runtime.
- *Vertical → horizontal → network degradation hierarchy.* Three named degradation paths, each with a typed event in Hugarsýn. Operators know which kind of degradation is occurring at a glance.
- *Tier as a Party Protocol input.* Every party member's tier is part of its role-bid eligibility. The engine produces the input; the protocol consumes it. Composition without coupling.
- *The Pi-baseline test as a documented gate.* Standing review question for every future subsystem. Documents the question; the answer must be on the subsystem's first slice doc.
- *Subsystem absence as a first-class state.* "Absent because tier" is announced in Hugarsýn the same way "present and idle" is. Operators can answer "where is the face?" without grepping logs.

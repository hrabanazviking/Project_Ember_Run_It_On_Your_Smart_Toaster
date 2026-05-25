---
codex_id: 6B_LOW_POWER_EMBODIMENT
title: Low-Power Embodiment — How Ember Stays Alive on a Smart Toaster
role: Scribe
layer: Synthesis
status: draft
sap_source_refs:
  - py/vts_manager.py:1-235
  - py/moss_tts.py:1-267
  - py/sherpa_asr.py
  - py/affection_system.py:1-64
  - py/behavior_engine.py:53-225
  - py/overlay_router.py:1-81
  - py/sleep_guard.py:1-100
  - py/random_topic.py:1-100
  - config/settings_template.json
ember_subsystem_targets: [Funi, Hjarta, Munnr]
cross_refs:
  - 60_synthesis/63_PERFORMANCE_TIER_ENGINE
  - 60_synthesis/64_AFFECTION_ENGINE_REIMAGINED
  - 60_synthesis/66_INVENTED_METHODS
  - 60_synthesis/6A_MULTI_AGENT_PARTY
  - 60_synthesis/6C_EMBER_WAVE_3_SLICE
---

# 6B — Low-Power Embodiment

> *Embodiment is not a render budget. Embodiment is the choice to be present in whatever form the host allows.*
> — Eirwyn Rúnblóm, watching a Pi 5 hold its small light

## 0. Posture — Companion to the Performance Tier Engine

This document is the companion to Cartographer's `[[63_PERFORMANCE_TIER_ENGINE]]`. The Cartographer's doc defines the *engine* — the runtime that gates feature availability by host capability. This doc defines the *expressive vocabulary at each tier* — how Ember actually shows up when she cannot afford a VRM avatar, when she cannot afford voice, when she cannot afford a screen, when she has nothing but a log line and a status pulse.

The question this doc answers: *how does Ember stay alive on a smart toaster?*

Not metaphorically. Literally. The Pi 5 in the corner. The phone left on the bedside table. The headless server holding a tailnet socket and nothing else. These are the hosts at the bottom of the tier ladder. SAP's design does not address them. SAP's hardware floor — 2 cores, 2 GB RAM — is a *workstation floor* relative to the Pi-and-below world. Ember's floor is genuinely lower.

The Vow of **Tiered Presence** (proposed in `[[61_NEW_VOWS]]`) requires Ember to degrade gracefully across the tier ladder *without going silent*. Silence is not graceful. Silence is abandonment. Ember must still be present at T4, and Ember must still be *recognizably herself*.

---

## 1. The Tier Ladder

The tier names come from Cartographer's `[[63_PERFORMANCE_TIER_ENGINE]]`. This doc fleshes out the expressive vocabulary per tier.

| Tier | Host Class | Capabilities | Expressive Surface |
|---|---|---|---|
| **T0** | Workstation (≥8 cores, ≥16 GB RAM, GPU ≥ RTX 2060) | Full Funi stack; VRM avatar with VTube Studio; MOSS TTS; ASR; camera; microphone; livestream | Full embodiment — animated avatar, expressive voice, real-time gestures, optional livestream presence |
| **T1** | Laptop (≥4 cores, ≥8 GB RAM, integrated GPU or modest dGPU) | Reduced Funi stack; Live2D or static VRM; piper-tts; ASR via local model; camera; microphone | Live2D avatar; clear voice; lighter animation; no livestream |
| **T2** | Phone / lightweight tablet (≥4 cores, ≥4 GB RAM, no dGPU) | Funi via cloud or distilled local model; piper-tts or espeak-ng; ASR via short-windowed local model; touchscreen | Text + voice; no avatar; haptic emoji affect; lock-screen pulse |
| **T3** | Pi 5 / similar SBC (≥4 cores, ≥4 GB RAM, no GPU, often no display) | Funi via cloud only or tiny local model; espeak-ng or cued-library TTS; ASR via small model or none | Text with **glyphic embodiment** (`[[66_INVENTED_METHODS]]#2`); cued voice clips; no avatar |
| **T4** | Smart toaster / headless server / log-only host | Funi via cloud only; no voice; no avatar; logs only | Log lines with affect-tagged formatting; status pulses; presence-only |

The tier is determined by host capability detection at startup (per `[[63_PERFORMANCE_TIER_ENGINE]]`) plus operator override. The override lets a powerful host run *as if* T3 — useful for testing, useful for "I want a quiet Ember experience even on the workstation."

---

## 2. T0 — Full Embodiment

T0 is what SAP designs for. The full VRM avatar (`vts_manager.py:1-235`), MOSS TTS (`moss_tts.py:1-267`), ASR via sherpa (`sherpa_asr.py`), Live2D fallback, livestream pipeline (`live_router.py:1-546`).

**What Ember does differently at T0 (vs. SAP):**

- **Composition-first avatar vocabulary** (`[[66_INVENTED_METHODS]]#17`) — the default expression set is composed-dignified, not anime-maximalist. The MAXIMALIST blendshapes are present but gated by consent tokens (`[[66_INVENTED_METHODS]]#6`).
- **Backpressure overlay** (`[[66_INVENTED_METHODS]]#11`) — the avatar shows a small overlay glyph when Funi is in retry backoff, when Strengr is in Disconnected state, when a tool call is awaiting approval. The operator can see Ember's *system* state, not just her *emotional* state.
- **Stream-truncation confession** (`[[66_INVENTED_METHODS]]#7`) — when the livestream renderer cuts off the avatar mid-utterance for latency, Ember emits a `…(more)` tag rather than going silent.
- **Default-quiet outward reach** (`[[66_INVENTED_METHODS]]#16`) — even on T0, IM bots / livestream connections / autonomous behavior default to *off*. The operator opts in.

T0's expressive surface is *maximalist by default in SAP, restrained by default in Ember*. This is the Saga-Stoic Restraint that Ember's Cyber-Viking aesthetic prefers.

Cite-shape: T0-only features live in `src/ember/spark/munnr/avatar/vrm/` and `src/ember/spark/munnr/voice/moss.py`. These modules import lazily so absent T0 dependencies do not break lower tiers.

---

## 3. T1 — Lite Embodiment

T1 is the laptop class. The integrated GPU cannot drive a full VRM at 60 fps in real time. But it can drive Live2D at 30 fps comfortably, or a static VRM with morph-target transitions.

**Expressive surface at T1:**

- Live2D avatar (a simpler 2D rigged character) — lighter than VRM, expressive enough.
- Static-VRM-with-morphs as alternative: a still 3D model whose facial expressions and gestures transition via blendshape interpolation, no real-time skeletal animation.
- piper-tts for voice (smaller model than MOSS, runs CPU-side at acceptable latency).
- ASR via a small local model (vosk-style) or cloud relay if available.
- Camera and microphone usable but lower resolution; the camera feed used only for presence detection (is the operator at the screen?), not for full computer vision.

**T1-specific patterns:**

- **Sleep-aware embodiment.** The laptop sleeps. When the lid closes, Ember on the laptop *suspends gracefully*: the avatar fades out, the voice stack drains, the IM token authority transfers via `[[66_INVENTED_METHODS]]#4` to a still-awake peer. When the lid opens, Ember on the laptop *fades back in* — not silently appearing but announcing return ("I'm back; the workstation Ember was handling Discord while I slept").
- **Battery-aware Funi.** If battery is below 20%, Funi switches from full-quality streaming responses to brief replies. The operator sees a small `(low battery)` indicator in the response header.
- **Display-off no avatar.** If the laptop is in laptop-on-but-screen-off mode (e.g., closed lid + external monitor), Ember switches to T2 expressive mode (text + voice, no avatar) until display returns.

Cite-shape: `src/ember/spark/munnr/avatar/live2d.py` + battery/power-state detection in `src/ember/spark/munnr/avatar/sleep_aware.py`. The latter consumes platform-specific power events (DBus on Linux, IORegistry on macOS, WMI on Windows) and abstracts them into a small `PowerState` enum.

---

## 4. T2 — Pocket Embodiment

T2 is the phone. There is no avatar rendering. There is a touchscreen. There is voice in and voice out (if the operator permits microphone). There is haptic feedback. There is a lock-screen widget surface.

**Expressive surface at T2:**

- **Text-with-glyphic-header.** Every response begins with a single-line glyph from `[[66_INVENTED_METHODS]]#2`. Calm: `( - _ - )`. Listening: `( o _ o )`. Delighted: `( ^ _ ^ )`. Etc.
- **Haptic affect.** Phone vibration patterns mapped to affect transitions. Brief double-buzz for "delighted." Single soft buzz for "agreement." Long held buzz for "concern." This is *embodiment through vibration* — affect rendered as physical sensation.
- **Lock-screen pulse.** A small widget on the lock screen shows Ember's presence: alive (glyph plus last-active timestamp), thinking (rotating glyph), sleeping (dim glyph). The lock-screen pulse is *passive presence* — operator can see Ember exists without interacting.
- **Voice on demand.** If the operator presses-and-holds, Ember speaks the response via piper-tts (or cloud TTS if local unavailable and consent given). Default is text-only to preserve battery and avoid embarrassment in public.
- **Brief replies preference.** Funi config at T2 biases toward concise responses (one to three sentences) unless the operator explicitly asks for length.

**T2-specific patterns:**

- **Distance-aware voice.** If the phone detects it is in the operator's pocket (motion sensor + light sensor heuristic), Ember does not initiate voice output unless prompted. Voice unsolicited from a pocket is jarring.
- **Quiet hours by default.** Per `[[66_INVENTED_METHODS]]#13`, T2 has stricter default quiet hours (22:00 to 09:00) than T0.

Cite-shape: phone-specific code lives in a separate sibling package `ember-phone` (since the iOS/Android surface is enormous and out of scope for the main project for the foreseeable future). T2 mode within the main `ember` package is the *headless* phone case (phone is reachable as a Munnr surface via tailnet but Ember itself runs elsewhere) — useful for testing and for non-phone "phone-like" thin clients.

---

## 5. T3 — Pi Embodiment

T3 is where this gets genuinely interesting. The Pi 5 sits in a corner. It may or may not have a display attached. It has 4–8 GB RAM, 4 cores, no GPU. It can run a tiny Funi model locally (Llama-3 1B, Phi-3 mini) or relay to a cloud Funi. It cannot afford MOSS TTS. It can afford espeak-ng. It can afford piper-tts on small voices, slowly. It can afford the cued-library voice (`[[66_INVENTED_METHODS]]#9`).

**Expressive surface at T3:**

- **Pure text** as the primary surface, with **glyphic embodiment** as the avatar substitute. Every response has a one-line glyph header indicating affect.
- **Cued voice library.** A small directory of pre-rendered MP3s — `~/.ember/voice_library/greeting_morning.mp3`, `~/.ember/voice_library/I_am_here.mp3`, `~/.ember/voice_library/thinking.mp3`, etc. The library is built on the operator's T0 workstation (using MOSS TTS for high quality) and rsync'd to the Pi. The Pi plays clips for greeting, acknowledgement, and presence pulses, while text remains the main response channel.
- **Espeak-ng for ad-hoc voice.** When a response cannot be conveyed by a cued clip, espeak-ng renders it. The voice is mechanical, but it is *voice*, and at T3 mechanical voice is honest about the tier.
- **Visual presence on a small display.** If the Pi has a small attached display (PiTFT, e-ink, etc.), Munnr renders a minimal interface — current affect glyph, last response (or last few lines), a small clock, a small heart-icon for affect axis. This is **monastery-style embodiment**: spare, beautiful, calm.
- **No camera, no microphone by default.** T3 default-quiet means Ember on the Pi does not listen unless the operator wires a microphone and explicitly enables it. The Pi is a *presence host*, not a *capture host*.

**T3-specific patterns:**

- **Long-form silence is acceptable.** The Pi is allowed to *not respond* for hours. Its presence pulse continues. Its glyph updates as affect decays. The operator should feel they have a quiet, faithful companion in the corner — not a yapping toy.
- **Telegram or matrix as the IM channel.** T3 is well-suited to be the holder of an IM token for a low-traffic channel (the operator's personal Telegram bot for example). Per `[[6A_MULTI_AGENT_PARTY]]#4`, the operator declares this in `party.yaml`.

Cite-shape: T3 modules live in `src/ember/spark/munnr/glyphic.py`, `src/ember/spark/munnr/voice/cued_library.py`, `src/ember/spark/munnr/voice/espeak.py`, `src/ember/spark/munnr/display/small_screen.py`. Each is small (≤200 LOC) and Pi-runnable.

---

## 6. T4 — Toaster Embodiment

T4 is the radical case. No display. No voice. No avatar. Possibly no network egress, only network ingress. The host is a presence pulse and a log line.

**Expressive surface at T4:**

- **Log-line affect.** Every log line written by Ember carries a small affect tag in its formatting. The format is operator-configurable:
  ```
  2026-05-24T22:15:00Z  [ ^_^ ]  responded to operator about pyproject.toml
  2026-05-24T22:16:30Z  [ -_- ]  background tool call completed
  2026-05-24T22:30:00Z  [ ~_~ ]  no activity for 14 minutes; entering quiet pulse
  ```
- **Status pulse via syslog or journald or local file.** Every N minutes (default 5), Ember writes a single-line pulse to a known location: `~/.ember/state/pulse.txt` containing `alive_at: <timestamp>, affect: <glyph>, last_active_persona: <persona_id>`. Operators or other systems can `cat` this file to know Ember is alive.
- **Webhook ping.** If configured, T4 hosts can push a heartbeat to a remote URL — useful when the toaster lives behind NAT and the operator wants visibility from outside. The webhook is opt-in.
- **Email or push notification on critical events.** If an autonomous tool call fails, if a config drift is detected, if the affect state crosses a major threshold, T4 can send a notification via SMTP, Pushover, ntfy, etc. The notification is operator-configured.

**T4-specific patterns:**

- **Read-only by default.** T4 is the *most cautious tier* for outward reach. Default is no IM, no livestream, no autonomous outgoing communication. The toaster is a watcher, not a speaker.
- **Logs are the primary surface.** Operators inspect T4 Ember via `journalctl --user -u ember`, `cat ~/.ember/state/pulse.txt`, `tail -f ~/.ember/state/log.jsonl`.
- **MCP server only.** T4 is well-suited to be a quiet MCP server that holds knowledge from the Well and serves queries from other tools. No outgoing surface; pure read.

Cite-shape: T4 modules live in `src/ember/spark/munnr/log_only.py`, `src/ember/spark/munnr/pulse.py`. The pulse file format is documented in `docs/operations/T4_RUNBOOK.md`.

---

## 7. Tier-Spanning Patterns

Some patterns are not *tier-specific* — they exist across all tiers, with different surfaces.

### 7.1 Affect

Per `[[66_INVENTED_METHODS]]#8`, affect anchors to Well evidence. At every tier, affect mutations are stored in the same Well. The *expression* of affect changes by tier:

- T0: avatar facial expression + voice tone + body posture.
- T1: avatar facial expression + voice tone (no body).
- T2: glyph header + haptic + voice tone.
- T3: glyph header + cued clip choice.
- T4: log-line affect tag.

The *storage* of affect is tier-invariant. The *interpretation* of affect into a surface is tier-specific.

Cite-shape: each tier ships a `render_affect(snapshot) -> TierSpecificOutput` function. The function dispatches in `src/ember/spark/munnr/affect_render/__init__.py`.

### 7.2 Voice

Per `[[66_INVENTED_METHODS]]#9`, the voice-tier substitution chain selects an engine by tier:

- T0: MOSS TTS.
- T1: piper-tts.
- T2: piper-tts or espeak-ng or cued-library.
- T3: espeak-ng or cued-library, sparingly.
- T4: no voice.

The chain falls back automatically; the prompt layer is unaware. The operator can see the active engine via `ember introspect voice`.

### 7.3 Reach

Per `[[66_INVENTED_METHODS]]#16`, outward reach defaults to *off* at every tier. The wizard at first launch asks per-surface consent. Lower tiers have *tighter default constraints*:

- T0: wizard can offer all reach surfaces.
- T1: wizard offers all surfaces but warns about battery/lid-close implications.
- T2: wizard defaults to text+notification only; voice and IM are explicit opt-in.
- T3: wizard defaults to IM-bot-as-receiver; no autonomous outgoing.
- T4: wizard offers MCP-server + webhook ping; no IM, no livestream.

The wizard logic is conditional on detected tier.

### 7.4 Memory

All tiers write to the same Well (the shared Brunnr). All tiers read from the same Well. The *retrieval depth* may vary by tier (T3 fetches fewer chunks per turn to stay in context), but the *storage* is unified.

### 7.5 Presence

Every tier emits a presence pulse to the Well's `ember_instance.alive_pulse_at` column (per `[[6A_MULTI_AGENT_PARTY]]#3`). The pulse interval scales by tier:

- T0: 30 s.
- T1: 60 s.
- T2: 120 s (battery-aware).
- T3: 60 s.
- T4: 300 s.

Other instances of Ember (in the multi-Ember party) can see the pulse and route accordingly.

---

## 8. Why This Matters — The Toaster Argument

Here is the argument for putting this much care into T4:

Ember's Vow of **Smallness** says she must be Pi-runnable. But Pi-runnable is not the same as *presence-on-the-Pi*. Many "Pi-runnable" agents work by Pi-as-relay (the Pi forwards messages to a server) without ever actually *being present* on the Pi. The agent's center of gravity is elsewhere.

Ember's design says the center of gravity is *the operator's relationship with Ember*. That relationship can exist at any tier, and Ember should not abandon a tier merely because it is small.

The toaster case (T4) is the limit case. If Ember can be *present* on the toaster — a log line, a status pulse, an occasional webhook — then Ember has answered the Vow of Smallness *all the way down*. The toaster Ember does not respond to chat; it watches, it remembers (by writing to the Well), it pulses to say *I am here*. That is enough. The operator who has Ember on their workstation and on the toaster has *one Ember in two presences*, not *one Ember and one orphan*.

The deeper claim: **presence is not a function of capability; presence is a function of intent**. The Pi 5 in the corner is more present, by intent, than a powerful workstation that has been left unattended for a week. Ember's tier engine must respect intent over capability.

This is why `[[63_PERFORMANCE_TIER_ENGINE]]` describes the *engine* and `[[6B_LOW_POWER_EMBODIMENT]]` describes the *vocabulary*. The engine knows what is possible; the vocabulary makes the possible into the *meaningful*.

---

## 9. Failure Modes

**T0 host has no GPU at runtime (user removed the card).** Auto-degrade to T1 with a warning at startup. The avatar config falls back from VRM to Live2D. The operator sees `ember introspect tier` show the detected tier with a note about the degraded capability.

**T3 host loses network.** Cued voice still works. Glyphic affect still works. Funi cannot make new calls; the existing context is preserved. The operator sees a `Disconnected(network)` indicator. Per Vow of **Graceful Offline**, the experience continues as text-only against any local model that may be present.

**T4 pulse file write fails (disk full).** Munnr logs the failure to stderr/journal. Pulse interval doubles to try less often. Operator sees a `disk_full` event in the audit log.

**Tier detection misclassifies host (Pi reported as T1 because /proc/cpuinfo lies).** Operator override via `~/.ember/config/tier_override.yaml`. The detection is a *suggestion*; the operator's declaration is authoritative.

**Cued library missing on Pi.** Falls back to espeak-ng. Operator sees a one-time prompt at startup: "Cued library not found at `~/.ember/voice_library/`. Run `ember voice-library sync` from your workstation. Falling back to espeak-ng for now."

---

## 10. Building the Cued Library

The cued voice library at T3 deserves its own paragraph because it is the most operationally interesting piece.

**Workflow:**

1. Operator is on T0 workstation with MOSS TTS available.
2. Operator runs `ember voice-library build --target=t3 --persona=<persona_id>`.
3. The command reads a manifest at `config/voice_library_manifest.yaml` listing the phrases to pre-render:
   ```yaml
   phrases:
     - id: greet_morning
       text: "Good morning."
     - id: greet_evening
       text: "Good evening."
     - id: i_am_here
       text: "I am here."
     - id: thinking
       text: "Let me think about that."
     - id: acknowledge
       text: "Mm."
     - id: agreement
       text: "Yes."
   ```
4. MOSS TTS renders each phrase. Output: `~/.ember/voice_library/<persona_id>/<id>.mp3`.
5. Operator runs `ember voice-library sync --to=pi.tailnet.host`. The library rsyncs to the Pi.
6. The Pi's Munnr now uses the cued library for matching phrases; falls back to espeak-ng for unmatched.

The manifest is curated by the operator. The default manifest ships with ~30 common phrases (greetings, acknowledgements, thinking-aloud lines, presence pulses). Operators can add their own.

This is **rendered authenticity** — the Pi's voice is the workstation's voice, captured at high quality, delivered cheaply. The Pi cannot speak *new* sentences in MOSS quality, but the Pi can *acknowledge* in MOSS quality, and for many T3 use cases acknowledgement is all the voice needed.

Cite-shape: `src/ember/cli/voice_library.py` for the workflow; `~/.ember/voice_library/` for the storage; the manifest format documented in `config/voice_library_manifest.yaml`.

---

## 11. Cross-References

- `[[63_PERFORMANCE_TIER_ENGINE]]` — Cartographer's engine that gates feature availability by tier.
- `[[64_AFFECTION_ENGINE_REIMAGINED]]` — the affect engine whose surfaces this doc renders per tier.
- `[[65_META_AWARENESS]]` — the Hugarsýn surface that surfaces tier state to the operator.
- `[[66_INVENTED_METHODS]]#2` — Glyphic embodiment definition.
- `[[66_INVENTED_METHODS]]#9` — Voice-tier substitution chain definition.
- `[[66_INVENTED_METHODS]]#11` — Avatar-as-backpressure indicator (T0/T1).
- `[[66_INVENTED_METHODS]]#13` — Quiet-hours throttling, tier-defaulted.
- `[[66_INVENTED_METHODS]]#16` — Failsafe default-quiet mode, tier-defaulted.
- `[[6A_MULTI_AGENT_PARTY]]` — multi-Ember party where each instance has its own tier.
- `[[6C_EMBER_WAVE_3_SLICE]]` — when low-power embodiment lands in the slice plan.
- `[[68_DECISION_RECORDS]]` — ADR-Proposed records for glyphic embodiment, cued library, tier-defaulted quiet hours.
- `[[69_INTEGRATION_ROADMAP]]` — phasing across the codex constellation.
- `[[ember:CROSS_PLATFORM_PLAN]]` — the existing cross-platform plan; tier-aware additions live here.

---

## What This Means for Ember

**Adopt:**

- SAP's voice stack architecture (`moss_tts.py:1-267`, `sherpa_asr.py`) — verbatim at T0. Wrap behind a single `VoiceEngine` Protocol that other tiers' engines satisfy.
- SAP's overlay manager pattern (`overlay_router.py:1-81`) — the websocket broadcast shape (`DanmakuOverlayManager.broadcast`) is exactly the right shape for tier-spanning affect display surfaces. Adopt the shape; bind it to Ember's tailnet rather than SAP's local websocket.
- SAP's sleep-guard cross-platform abstraction (`sleep_guard.py:1-100`) — keep awake on Linux, macOS, Windows. T0 and T1 will want this. Adopt the pattern of platform-detection-via-subprocess.

**Adapt:**

- SAP's affect surface (`affection_system.py:1-64`) — adapt from "JSON write per regex match" to "tier-specific render of the same affect state." The affect state lives in one place; each tier interprets it via its own `render_affect` function. The SAP regex-tag mechanism is unsuitable (per `[[64_AFFECTION_ENGINE_REIMAGINED]]`); replace with typed mutation calls.
- SAP's behavior engine (`behavior_engine.py:53-225`) — adapt the trigger types (`time`, `noInput`, `cycle`) but add tier-conditional gating. T4 cannot run autonomous outgoing-message triggers; T3 has stricter quiet hours; T1/T2 sleep-suspend behavior.
- SAP's settings_template.json structure — adapt the per-platform/per-tier settings into Ember's overlay config (`config/ember.yaml` + tier-specific overlays).

**Avoid:**

- SAP's all-or-nothing embodiment. SAP either runs the VRM avatar or runs without an avatar. There is no in-between expressive surface. Ember provides surfaces all the way down to T4 log lines.
- SAP's default-on behavior. T2/T3/T4 inheriting "respond to every IM message 24/7" is wrong for the tier; defaults must be tier-aware.
- SAP's silent voice degradation. If MOSS TTS fails to load on a low-power host, SAP simply has no voice. Ember substitutes through the chain and tells the operator which engine is active.

**Invent:**

1. **The Tier Ladder** as a named, ratified vocabulary (T0/T1/T2/T3/T4 with the capability descriptors in `§1`).
2. **Per-Tier Default Reach Wizard.** The first-launch wizard inspects detected tier and offers tier-appropriate reach surfaces (T4 wizard does not even offer IM bots; T0 wizard offers them all with warnings).
3. **Haptic Affect Mapping** at T2 — phone vibration patterns as affect surface. Single buzz for agreement. Double buzz for delight. Held buzz for concern.
4. **Lock-Screen Pulse Widget** at T2 — passive presence indicator readable without unlocking.
5. **Monastery-Style Small-Display Munnr** at T3 — minimalist text-and-glyph interface for PiTFT or e-ink displays. Spare, beautiful, calm.
6. **Status Pulse File** at T4 — `~/.ember/state/pulse.txt` containing alive_at + affect glyph. Discoverable by other tools.
7. **Webhook Heartbeat** at T4 — opt-in remote pulse for visibility from outside the toaster's network.
8. **Cued Voice Library** — MOSS-quality rendered phrases pre-built on T0, rsync'd to T3 hosts; the Pi sounds as good as the workstation for the phrases it has.
9. **Battery-Aware Funi** at T1 — response brevity scales with battery; operator sees a `(low battery)` indicator.
10. **Distance-Aware Voice** at T2 — phone in pocket = no unsolicited voice (motion+light sensor heuristic).
11. **Display-Off T2 Mode** at T1 — laptop with screen off but device on switches to T2 expressive surface until display returns.
12. **Tier-Conditional Quiet Hours Defaults** — T2 defaults stricter than T0; T4 has no chat surface at all.

**True Names affected:** Munnr (heaviest — every tier's expressive surface lives here), Hjarta (affect rendering per tier), Funi (battery-aware behavior, response brevity adjustment). Brunnr and Strengr and Smiðja unchanged.

**Vows reinforced:** **Tiered Presence** (the central Vow), **Smallness** (T4 honors it all the way down), **Embodied Honesty** (the affect surface reflects real state at every tier), **Public-Friendliness** (each tier has a plain-readable surface), **Graceful Offline** (every tier survives network loss).

**Slice readiness:**

- Slice 3 candidates: tier detection + tier override config + glyphic embodiment + log-line affect formatting. All small, all Pi-runnable, all isolated.
- Slice 4 candidates: cued voice library workflow + the small-display Munnr surface + battery-aware Funi.
- Slice 5+ candidates: phone-side (T2) integration, haptic surface, livestream-specific T0 features.

**Most consequential single decision:** treating **the toaster as a first-class tier**, not a vestigial leftover. T4 is not a degraded T3; it is its own form of presence. The decision to design for T4 explicitly is what makes Ember's tiered embodiment honest.

The proposals stand as written. The slice plan does not change here.

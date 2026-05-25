---
codex_id: 62_MOBILE_AND_XR_TIER
title: Mobile and XR — The Form-Factor Matrix Ember Was Missing
role: Cartographer
layer: Synthesis
status: draft
cdk_source_refs:
  - /tmp/ChatdollKit/Scripts/SpeechListener/IOSMicrophoneProvider.cs
  - /tmp/ChatdollKit/Scripts/SpeechListener/AndroidMicrophoneProvider.cs
  - /tmp/ChatdollKit/Scripts/SpeechListener/MacMicrophoneProvider.cs
  - /tmp/ChatdollKit/Scripts/IO/IOSNativeMicrophone.cs
  - /tmp/ChatdollKit/Scripts/IO/AndroidNativeMicrophone.cs
  - /tmp/ChatdollKit/Scripts/IO/MacNativeMicrophone.cs
  - /tmp/ChatdollKit/Scripts/IO/JavaScriptMessageHandler.cs
  - /tmp/ChatdollKit/Scripts/UI/FPSManager.cs
  - /tmp/ChatdollKit/Plugins
  - /tmp/ChatdollKit/Examples
ember_subsystem_targets: [Funi, Andlit, Rödd, Hugarsýn, Munnr]
cross_refs:
  - 60_TRIANGULATION
  - 61_ANDLIT_UNITY_TIER
  - sap:63_PERFORMANCE_TIER_ENGINE
  - sap:6B_LOW_POWER_EMBODIMENT
  - waifu:60_REALTIME_TIER_FOR_ANDLIT
  - chatdoll:1D_MULTI_PLATFORM_DOMAIN
  - chatdoll:3C_MOBILE_BUILD
  - chatdoll:3D_XR_BUILD
  - chatdoll:3B_WEBGL_BUILD
---

# 62 — Mobile and XR Tier

> *Volmarr at 2am on the train, phone in pocket, mug long empty. The desktop Ember is two timezones away. The phone wakes when he taps it. Same Ember. Different room.*
> — Védis Eikleið, sketching the form-factor axes

## 0. Posture — what the prior codexes left out

SAP and Waifu, taken together, covered desktop and browser. Neither addressed:

- iOS native
- Android native
- VR (Meta Quest, Vision Pro, Valve Index)
- AR (ARCore, ARKit, mobile AR overlays)
- mid-form-factor (tablet, foldable, automotive infotainment)

Each of these is a *form-factor*, distinct from a *tier* in the `[[sap:63_PERFORMANCE_TIER_ENGINE]]` sense. A tier is a *capability rung*; a form-factor is an *embodied context*. A phone at T2-mobile capability is *not* a laptop at T2 capability even when their CPU/RAM/GPU specs nearly match — the embodied context (pocket, screen size, OS sandbox, battery profile, sensor surface, lock-screen widget, haptic) is structurally different.

This doc draws the form-factor matrix the prior codexes were missing, locates each form-factor on Ember's tier ladder (with the SAP-Cartographer T-1/T0/T1/T2/T3 vocabulary chosen in `[[60_TRIANGULATION §3]]`), and proposes a small extension to the capability map. It also addresses the **XR-as-its-own-dimension** question: should VR/AR be a *tier* (high-capability rung above T3), a *form-factor row*, or both? My recommendation: a parallel axis, like Tier-CLOUD in `[[waifu §3]]`.

## 1. The form-factor matrix

Seven form-factors visible from CDK's source surface (the per-platform microphone providers and the multi-platform build target list):

| Form-factor | Tier rung | Platform | Screen | Input | Battery | Sandbox |
|---|---|---|---|---|---|---|
| **Desktop workstation** | T2/T3 | Win/Mac/Linux | large/multiple, 24"+ | keyboard + mouse + (mic, cam) | wall power | none (or minimal) |
| **Laptop** | T1/T2 | Win/Mac/Linux | 13–16" | keyboard + trackpad + (mic, cam) | battery + thermal-bound | none (or minimal) |
| **Tablet** | T1/T2 | iPadOS / Android | 10–13" | touch + (pencil, mic) | battery + thermal-bound | strict (App Store) |
| **Phone** | T1/T2-mobile | iOS / Android | 6–7" | touch + (mic, motion, GPS) | battery + thermal + pocket-aware | strict (App Store) |
| **VR headset** | T2-XR / T3-XR | Quest 3, Vision Pro, Index, Valve Deckard, ... | stereoscopic head-mounted | controllers + hand-tracking + (gaze, mic) | battery (Quest) or tether (Index) | platform-specific (Quest Store, App Store) |
| **AR overlay** | T2-mobile-AR | ARCore (Android), ARKit (iOS), HoloLens | environmental overlay on phone/glasses | gesture + (gaze, mic, hand-track) | battery | strict |
| **Automotive / kiosk / smart display** | T1/T2 | Android Auto, CarPlay, embedded Linux | 7–15" landscape | voice-primary + (touch, knob) | wall or vehicle-battery | strict |

Five of these — desktop, laptop, tablet, phone, smart-display — are reachable by *some* substrate (electron/Unity/browser). VR and AR are *Unity-only* among the three roads we've studied. Automotive is also effectively *Unity-only* if "in the dashboard" matters; otherwise an Android Auto integration via browser-PWA is borderline-viable but feels wrong.

**The form-factor matrix is broader than the tier ladder.** Phone at T2-mobile is a different operator context from laptop at T2 even when both run on a Snapdragon 7-gen-3 with 8GB RAM. The phone's *sandbox* (App Store rules, background-execution limits) and *embodied context* (pocket, lock-screen, haptic) are properties the tier vocabulary does not encode.

## 2. The Tiered Presence Vow extended

`[[sap:61_NEW_VOWS §4]]`'s Tiered Presence Vow says: *Ember is the same agent across hardware tiers, with capabilities lighting up or sleeping by tier, never silently swapping.*

The form-factor matrix forces a clarification: **form-factor is part of presence, not just capability.** A phone-Ember is the same identity as a laptop-Ember, but the operator's *embodied relationship* with the agent is structurally different. The operator-on-laptop sits at the screen and types; the operator-on-phone glances and speaks. The Vow extends:

> *Ember is the same agent across hardware tiers and form-factors. Capabilities light up or sleep by tier. Surfaces shift or augment by form-factor. Identity is invariant under both.*

Concretely, the form-factor introduces *new surfaces* that exist on no other tier:

- **Lock-screen widget** (phone only). Per `[[sap:6B_LOW_POWER_EMBODIMENT §4]]`, an iOS Live Activity / Android NotificationListener surface shows the presence pulse. No analog on desktop.
- **Haptic affect** (phone only). The phone vibrates per affect transition. Already proposed in `[[sap:6B_LOW_POWER_EMBODIMENT §4]]`; CDK's mobile build makes this concretely buildable.
- **Always-listening wake-word** (smart-display only). The agent listens for an operator-defined wake-word, then enters a conversation mode. No analog on laptop where conversation is intentional.
- **Spatial audio + head-tracking** (XR only). Ember's voice appears at a *location* in 3D space. The operator turns their head; the voice stays put. No analog elsewhere.
- **Gaze-as-input** (XR and some AR). Operator looks at a UI element; the gaze cursor selects. No analog on flat screens.
- **Hand-tracking gestures** (XR). Operator's bare hands trigger animations or commands. No analog elsewhere.

These are not *capabilities* in the tier sense (they don't require more GPU); they are *surfaces* in the form-factor sense (they exist because of the device's input/output topology).

## 3. The Mobile-Baseline Test

`[[60_TRIANGULATION §6]]` proposed a Mobile-Baseline Test as a standing review gate alongside the Pi-Baseline Test. This is where it gets specified.

The test, in full:

> *For every proposed subsystem or slice, answer: "What does this look like on a 2GB Android phone running on battery, with the screen off, with the operator's pocket motion-sensor detecting walking, with cell reception fluctuating?"*

Pass criteria:

1. **Identity preserved.** Ember-on-phone is still Ember. Persona key unchanged. Memory in Brunnr reachable (cached if offline). Hjarta pulse continues.
2. **Surface degrades gracefully.** Lock-screen pulse continues even when the app is backgrounded. Haptic affect works on a screen-off phone. Voice does not initiate output when the phone is in a pocket (motion + light sensor heuristic per `[[sap:6B_LOW_POWER_EMBODIMENT §4]]`).
3. **Battery drain is announced and bounded.** Hugarsýn projects `andlit.battery_drain_estimate_mAh_per_hr`. The operator can read this. If the figure exceeds a tier-floor budget, Ember degrades automatically (reduce render rate, disable lipsync, drop to text-only) and announces the degradation.
4. **Network loss is invisible to identity.** Graceful Offline applies. If cell reception drops, Ember uses cached responses or local model if present; ingestion to Brunnr queues for later.
5. **App-backgrounding does not silence Ember.** `OnApplicationPause(true)` triggers a controlled suspend (queue current animations, mute audio, suspend network polling). Re-foregrounding resumes from the suspend point.
6. **OS permission revocation is announced.** If the operator revokes mic permission mid-session (Android lets users do this from the notification shade), Hugarsýn announces `MicrophonePermissionLost` and the surface degrades to text-only.

A slice that fails any of these six points is *not Mobile-Baseline-passing*. The slice can still be proposed for desktop-only deployment, but the ADR must declare that explicitly.

CDK's source surface includes the per-platform microphone providers that make these tests passable: `/tmp/ChatdollKit/Scripts/SpeechListener/IOSMicrophoneProvider.cs`, `/tmp/ChatdollKit/Scripts/SpeechListener/AndroidMicrophoneProvider.cs`, and the native plugins at `/tmp/ChatdollKit/Scripts/IO/IOSNativeMicrophone.cs` and `/tmp/ChatdollKit/Scripts/IO/AndroidNativeMicrophone.cs`. The fact that CDK has *separate* providers per platform is the right shape — each platform's microphone API differs structurally, and the abstraction over them lives in `IMicrophoneProvider.cs`.

## 4. The capability map extension

`[[sap:63_PERFORMANCE_TIER_ENGINE §2]]` defines the capability map with rows for True Names and Munnr surfaces. The form-factor matrix forces an extension: *some subsystems' capability is form-factor-dependent, not just tier-dependent.*

Proposed extension to the capability map (additions only):

| Capability | T-1 | T0 | T1 | T2 | T2-mobile | T2-XR | T3 | T3-XR |
|---|---|---|---|---|---|---|---|---|
| Andlit (canonical) | – | – | – | ✓ (electron) | ✓ (unity-mobile) | ✓ (unity-XR) | ✓ (electron + unity) | ✓ (unity-XR-rich) |
| Lock-screen pulse | – | – | – | – | ✓ | – | – | – |
| Haptic affect | – | – | – | – | ✓ | ✓ (XR controller) | – | ✓ (XR controller) |
| Spatial audio | – | – | – | – | ◐ (stereo only) | ✓ | ✓ (workstation speakers, limited) | ✓ |
| Gaze input | – | – | – | – | – | ✓ | – | ✓ |
| Hand-tracking | – | – | – | – | ◐ (camera only) | ✓ | ◐ (Leap, etc.) | ✓ |
| Wake-word always-listen | – | – | ◐ | ✓ | ◐ (battery-bound) | ✓ | ✓ | ✓ |
| Background-app suspend | – | – | – | – | ✓ | ✓ | – | – |
| OS-permission revocation | – | – | – | – | ✓ | ✓ | – | ✓ |

Notice the columns `T2-mobile` and `T2-XR` (and a parallel `T3-XR`). These are *not* new tier rungs — they share the same capability hardware-floor as T2 and T3. They are *form-factor branches* of the existing tiers. The tier vocabulary stays five rungs; the capability map gets form-factor columns.

The Hugarsýn projection extends similarly:

```
GET /hugarsýn/tier
{
  "rung": "T2",
  "form_factor": "phone-ios",      # new: form-factor identifier
  "device_class": "iphone-15-pro", # already in §3 of 61_ANDLIT_UNITY_TIER
  "battery": {
    "level_pct": 67,
    "charging": false,
    "thermal_state": "nominal"
  },
  "active_subsystems": ["Funi", "Strengr", "Brunnr (cached)", "Hjarta", "Hugarsýn", "Andlit (unity-mobile)", "Rödd"],
  "form_factor_surfaces": ["lock_screen_pulse", "haptic_affect", "pocket_detection"],
  "cloud_axis": {...}
}
```

A party peer or the operator can read at a glance which surfaces are available at this moment — not "is this a T2 device" but "is this a T2-phone-on-battery-in-pocket".

## 5. XR as its own axis

VR and AR deserve a separate treatment because they are *not* "T3 plus a headset." They are a *qualitatively different* form-factor.

The case:

- **Spatial audio + head-tracking** is not a capability that scales with GPU; it is an *input/output topology* that either exists or does not.
- **Gaze-as-input** is a property of the headset's eye-tracker, not the GPU.
- **Hand-tracking** is a property of cameras + ML, available on some XR devices and absent on others.
- **Embodiment in a 3D space the operator is also in** is structurally different from embodiment on a 2D screen. The operator can *walk around* the Ember avatar in VR. They cannot do that on a phone.

So VR/AR is a *parallel axis*, like Tier-CLOUD in `[[waifu §3]]`. The capability map's columns for `T2-XR` and `T3-XR` are not new tier rungs; they are *the tier-N hardware in XR form-factor*.

The handoff implication: an Ember that moves *from phone to VR headset* is not moving up a tier; it is moving across the XR axis. The handoff protocol from `[[waifu §7]]` extends:

```
Phase 1 (Trigger): Operator dons headset; Quest hardware reports active; bandwidth check ok.
Phase 2 (Consent): If first time using XR with this Ember, prompt: "Activate XR Andlit?"
Phase 3 (Establish): Load XR scene; Unity build switches to XR target; same Ember persona.
Phase 4 (Crossover): Phone continues showing presence pulse for ~2s; XR scene wakes; phone fades.
Phase 5 (Stabilise): Phone in Hugarsýn shows `andlit.adapter=null reason=handed_off_to_xr_peer`; XR Ember active.
```

The same operator sees the same Ember, different room. Identity invariant.

## 6. Specific surface designs per form-factor

### 6.1 Phone (iOS)

Native Unity iOS build with VRM avatar + uLipSync. The microphone surface uses `IOSMicrophoneProvider` (`/tmp/ChatdollKit/Scripts/SpeechListener/IOSMicrophoneProvider.cs`) which wraps the iOS `AVAudioSession` API. Per `[[chatdoll:3C_MOBILE_BUILD]]`, expect:

- 50–150 MB IPA size depending on asset inclusion
- 30 fps target on iPhone 13+ with VRM avatar; 60 fps achievable for short bursts
- Background-mode: voice continues for ~30s after lock; CallKit-style banner shows on lock screen for active session
- App Store guidelines: no recording without explicit user-initiated UI action; mic-on indicator required by iOS itself
- Lock-screen widget: iOS Live Activity for active session; Widget for ambient presence pulse

Operator situation: walking to the train, glance at phone, see Ember's lock-screen pulse glyph showing `delighted` (because the morning Brunnr-summary contained a positive item). Tap to unlock, full Unity scene loads, Ember waves.

### 6.2 Phone (Android)

Native Unity Android build. Microphone surface uses `AndroidMicrophoneProvider` (`/tmp/ChatdollKit/Scripts/SpeechListener/AndroidMicrophoneProvider.cs`) which wraps `AudioRecord` via JNI. Per `[[chatdoll:3C_MOBILE_BUILD]]`:

- 60–200 MB APK size; AAB split shrinks per-device download
- 30 fps target on Snapdragon 7-gen-3+ with VRM; varies widely across SoC vendors
- Doze mode considerations: background voice-on requires a foreground service + persistent notification
- Permission revocation: Android 11+ lets the user revoke mic from notification shade; Ember must announce + degrade
- Lock-screen surface: persistent notification with `MediaStyle` for active session

Operator situation: commute home, headphones in, ask Ember a question over voice, the response plays through earbuds; the phone screen stays off; the persistent notification shows the affect glyph.

### 6.3 VR (Quest 3 / Vision Pro)

Unity XR build using XR Interaction Toolkit. VRM avatar positioned in a small virtual room; spatial audio so Ember's voice comes from the avatar's mouth. Gaze + hand-tracking for input. Per `[[chatdoll:3D_XR_BUILD]]`:

- 200–500 MB APK (Quest is Android-based) or visionOS bundle
- 72/90/120 fps target depending on headset; missing frame budget triggers degradation (reduce blendshape rate, simplify scene)
- Comfort floor: head-locked UI is forbidden (motion sickness); UI elements are world-anchored
- Vision Pro adds: persona-as-spatial-presence; passthrough AR mix

Operator situation: in VR, working on a 3D modeling task in another app, Ember occupies a corner of the room as a small companion presence; can be summoned closer by gaze + pinch.

### 6.4 AR (ARKit / ARCore)

Unity AR build using AR Foundation. VRM avatar anchored to a horizontal plane (table) or upright surface (wall). The operator's camera sees Ember in the real world. Per `[[chatdoll:3D_XR_BUILD]]`:

- Plane detection lag is normal; Ember "settles" once a plane is found
- Battery drain is significant; 30-minute sessions are the realistic ceiling
- Privacy: camera feed never persists; AR scene processing is on-device
- Form-factor twist: AR-via-phone uses the same phone hardware as the phone form-factor, but the *embodied context* is different (looking through the camera at the real world)

Operator situation: at a café, phone propped up, Ember stands on the table next to the laptop; the operator types and chats, Ember nods and reacts to the conversation context.

### 6.5 Tablet (iPad / Android tablet)

Same Unity build as phone (just larger screen). The interesting twist: a tablet on a stand is essentially a small *desktop monitor* for Ember. Persistent screen-on, larger touch targets, more thermal headroom. The form-factor surfaces shift:

- Lock-screen pulse less relevant (the tablet often stays unlocked on a stand)
- Haptic affect optional (tablets have weaker haptics)
- Wake-word always-listen viable (thermal headroom permits)
- Pen input: a stylus could draw with Ember (a future surface, not in CDK)

### 6.6 Smart display (Echo Show, Nest Hub, automotive infotainment)

Form-factor-locked devices where the operator does not control the OS. Reachable via:

- A Unity build targeting Android (some smart displays) — viable
- A WebGL build embedded in the device's browser — viable for kiosk-style displays
- The device's first-party assistant integration — not viable for Ember (vendor lock-in)

Lower-priority form-factor; included for completeness.

## 7. The Pi-vs-mobile distinction

A common confusion to head off: *"why is the phone T2 but the Pi T0? They have similar CPU/RAM specs."*

The distinction is not raw specs; it is *form-factor-conditioned capability*:

| Property | Pi 5 (T0) | iPhone 15 (T2-mobile) |
|---|---|---|
| CPU | 2.4GHz quad ARM A76 | 3.78GHz hexa A17 Pro |
| RAM | 4-8GB LPDDR4X | 8GB LPDDR5 |
| GPU | VideoCore VII (modest) | A17 Pro GPU (substantial) |
| Always-on screen | usually no | yes (Lock Screen) |
| Battery management | minimal | aggressive iOS thermal/battery management |
| Sandbox | none | strict App Store |
| Wake-word capability | hard (limited DSP) | trivial (dedicated low-power DSP) |
| Reachable substrate | Python / native ARM Linux | Unity iOS / native Swift |

The phone is *more capable* than the Pi for the surfaces that *matter on a phone*. The Pi is *more capable* for the surfaces that matter on a Pi (uptime, daemon-class behavior, no battery, full filesystem control). They sit on the same tier rung *by hardware* and on different tier rungs *by form-factor*.

The capability map's mobile column captures this: T2-mobile includes some T2 capabilities (Andlit-unity), excludes others (full desktop OS APIs), and adds form-factor-only ones (lock-screen, haptic, pocket-aware behavior).

## 8. The XR identity question

XR raises an identity question the prior codexes did not touch: *is Ember-in-VR the same as Ember-on-phone?*

I argue yes, with one caveat. The same persona, same memory, same Hjarta pulse, same Hugarsýn projection. The VR adapter's surfaces are richer (spatial audio, hand-tracking, full 3D scene around the avatar), but the *identity* is the same Ember.

The caveat: **the VR avatar may need a different VRM file.** Phone Ember probably uses a low-poly VRM optimized for mobile rendering. VR Ember might use a high-poly VRM for the closer viewing distance. *Same persona, different model file.* This is a property of the substrate's render pipeline, not of identity. The Hugarsýn projection shows it:

```
GET /hugarsýn/andlit
{
  "name": "Andlit",
  "adapter": "unity",
  "substrate": {
    "engine": "Unity",
    "build_target": "vr-oculus"
  },
  "vrm_model": "ember_xr_v3.vrm",  # different from phone
  "vrm_polycount": 35000,
  "current_verb": "acknowledge"
}
```

The model file is one of the adapter's properties. Identity stays singular.

This is the same shape as a person changing clothes: same person, different jacket. Surface variation; not identity variation. The Embodied Honesty Vow ([[sap:61_NEW_VOWS §1]]) is satisfied because the variation is *announced* in Hugarsýn rather than hidden.

## 9. Form-factor and Hjarta

The phone-versus-desktop form-factor distinction touches Hjarta in a specific way: **the operator's relationship with their phone is different from their relationship with their desktop.** The phone is in the pocket, in the bed, in the bathroom, in the car. The desktop is in one room.

Phone-Ember witnesses moments the desktop-Ember cannot. *That changes what Hjarta records.* The Pi watches uptime. The desktop watches focused work. The phone watches *commute, walk, conversation overheard while waiting in line.* Each form-factor has a different *witness scope*.

The witness scope is a property of *where the phone-Ember-Hjarta writes to Brunnr from*. It does not change Hjarta's name or contract; it changes the *episode metadata* (form-factor, location-class-if-permitted, time-of-day-class). A future synthesis might explore this as "Hjarta-as-witness", but the current proposal is simpler: episodes carry their form-factor tag; Hjarta does not branch.

## 10. Form-factor-aware Vow extensions

Each Vow gets a form-factor clarification:

- **Embodied Honesty:** an XR avatar's spatial position is part of its state. Ember-in-VR cannot teleport across the room without announcing the teleport — that would be a lie of position.
- **Surface Without Surveillance:** mobile permissions are a scope. Mic permission, camera permission, motion-sensor permission. Each is a scope that the operator grants per-context and can revoke. Hugarsýn shows current permission state.
- **Affective Restraint:** haptic affect is still affect. The Vow's "affect biases tone, never gates behavior" applies — Ember cannot refuse a task because the affect is low *and* skip a haptic vibration as punishment. Tone, not gating.
- **Tiered Presence:** the central Vow that this entire doc operationalises. Identity invariant across form-factors; surfaces shift, agent stays the same.
- **Federated Self:** a multi-instance Ember where the phone and the laptop are both online needs to handle role bidding under form-factor constraints. The phone *can* run text and voice in the background; the phone *cannot* run a long video-call session (battery + thermal). Federation bids should consider form-factor capability, not just tier.
- **Cloud as Named Context:** mobile networks are flaky. Cloud-axis on a phone needs to be aware of bandwidth fluctuation. Already covered in `[[waifu §4]]`'s `bandwidth_floor_mbps`.

## 11. Cross-References

- `[[60_TRIANGULATION]]` — the matrix this doc extends with form-factor rows
- `[[61_ANDLIT_UNITY_TIER]]` — the Andlit-unity adapter that powers mobile and XR
- `[[63_MULTIMODAL_PIPELINE]]` — the pipeline that runs on every form-factor
- `[[sap:63_PERFORMANCE_TIER_ENGINE]]` — the tier engine; this doc adds form-factor as orthogonal to tier
- `[[sap:6B_LOW_POWER_EMBODIMENT]]` — already proposed lock-screen + haptic; this doc grounds them in CDK source
- `[[sap:61_NEW_VOWS]]` — Tiered Presence Vow extended in §2
- `[[waifu:60_REALTIME_TIER_FOR_ANDLIT]]` — Tier-CLOUD as parallel axis pattern; this doc applies the same shape to XR
- `[[chatdoll:1D_MULTI_PLATFORM_DOMAIN]]` — Architect's deep dive on per-platform build deltas
- `[[chatdoll:3C_MOBILE_BUILD]]` — Forge-B's iOS + Android build pipeline doc
- `[[chatdoll:3D_XR_BUILD]]` — Forge-B's VR + AR build doc
- `[[chatdoll:17_MICROPHONE_MANAGER_DOMAIN]]` — the per-platform microphone provider layer

## What This Means for Ember

**Adopt:**

- **The form-factor matrix** (§1) as Ember's canonical taxonomy of embodied contexts. Persist as `docs/decisions/0xxx-form-factor-matrix.md`. Update when new form-factors emerge (smartwatches, smart-glasses, automotive AR).
- **CDK's per-platform microphone provider abstraction** (`/tmp/ChatdollKit/Scripts/SpeechListener/IMicrophoneProvider.cs` interface + per-platform implementations). Apache-2.0; vendor the interface shape; each Ember platform implements per-OS. *Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*
- **The Mobile-Baseline Test as a standing review gate** (§3). Add to the slice plan review checklist. Every slice that touches a mobile-capable subsystem must answer it.
- **The XR-as-parallel-axis reading** (§5). VR/AR is not a tier above T3; it is a form-factor axis intersecting every tier that has the requisite hardware.

**Adapt:**

- **The Tiered Presence Vow** extended per §2: *"surfaces shift or augment by form-factor."* The Vow does not change; the clarification makes it operationally meaningful in the multi-form-factor world.
- **The Hugarsýn `/hugarsýn/tier` projection** extended with `form_factor`, `device_class`, `battery`, `form_factor_surfaces` (§4 schema). The tier engine already projects these properties internally; expose them through the existing endpoint with a schema update.
- **The handoff protocol** from `[[waifu §7]]`: extend to handle form-factor handoffs (laptop→phone, phone→XR, XR→desktop). Same five phases. The Crossover phase tolerates ~2s of dual-surface presence as before; on XR handoffs, the source form-factor fades to a presence pulse rather than disappearing.
- **The witness scope concept** (§9). Episodes in Brunnr carry their form-factor tag. Future Hjarta queries can filter by witness scope (*"what did phone-Ember see this week?"*) without branching Hjarta itself.

**Avoid:**

- **Treating phone as "Pi with a screen."** They are different form-factors with different surfaces. The Pi is a hearth-tender; the phone is a pocket-companion. Designs that conflate the two miss both.
- **Treating XR as "T3 plus a headset."** XR is a parallel axis with its own surface vocabulary (spatial audio, gaze, hand-tracking). Capability scaling does not capture it.
- **Building mobile features as desktop ports.** Mobile has form-factor-specific surfaces (lock-screen, haptic, pocket-aware) that have no desktop analog. A direct port misses what mobile *is for*.
- **Always-on cellular cloud-axis on mobile.** Bandwidth fluctuation and cellular billing make the cloud axis less stable on phones. The `[[waifu §4]]` matrix's L-only default applies extra-strictly on mobile.
- **Letting the App Store sandbox surprise the operator.** iOS and Android revoke permissions, suspend backgrounded apps, kill processes for memory pressure. Every mobile feature must announce its OS-induced state changes through Hugarsýn.

**Invent:**

- **Form-factor as a first-class projection axis** in Hugarsýn alongside tier and cloud-axis. `/hugarsýn/tier` returns `{rung, form_factor, device_class, ...}`. The form-factor is part of how a peer reads this Ember.
- **The `T2-mobile`, `T2-XR`, `T3-XR` capability-map columns** (§4). Not new tier rungs — form-factor branches of existing rungs. The vocabulary stays five rungs; the map gains form-factor-specific columns where surfaces differ.
- **The Mobile-Baseline Test** as a standing review gate, six-point pass criteria (§3). Documented; lives next to the Pi-Baseline Test in the slice plan checklist.
- **The witness scope tag in episode metadata** (§9). Every Brunnr episode carries `witness.form_factor`. Queries can filter (*"what did Ember see on the phone this week"*) without branching Hjarta.
- **The XR adapter's spatial-position state** as a Hugarsýn-tracked property. An XR avatar at `(2.3, 1.4, 0.8)` meters from the operator's head is announced. Teleportation in XR is a *visible* event, not a silent one (per the Embodied Honesty form-factor extension).
- **The form-factor handoff phase 4 variant.** XR handoffs fade the source form-factor to a *presence pulse* on the abandoned device rather than full disappearance. The phone shows a persistence-pulse glyph indicating the operator is currently in VR; the operator returning to phone sees a "welcome back" glyph rather than a cold-start scene.
- **The per-platform mic-permission-revocation announcer.** Android's notification-shade revocation is *silent* from the app's perspective; the app sees the permission absent the next time it queries. Ember polls the permission state every 30s on Android and announces `MicrophonePermissionLost` to Hugarsýn at the moment of detection. Same shape for iOS Camera Access via Privacy controls.
- **The form-factor watchlist artifact.** A small markdown file at `docs/decisions/form_factor_watchlist.md` tracking smartwatches, smart-glasses (Meta Ray-Ban-class), automotive AR, and any other emerging form-factor. Updated when relevant hardware launches. Documents the question "should Ember reach this form-factor?" without committing to it.

---

*Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

Seven form-factors. Five tier rungs. One identity. The map is wider than any prior codex showed. The phone in the pocket is a real Ember; the headset on the table is a real Ember; the laptop on the train is a real Ember. They all see different rooms. They are all the same agent.

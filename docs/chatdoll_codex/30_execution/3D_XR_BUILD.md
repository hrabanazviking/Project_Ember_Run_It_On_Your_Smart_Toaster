---
codex_id: 3D_XR_BUILD
title: XR Build — VR, AR, and the Six Sensors Nobody Mentions
role: Forge-B
layer: Execution
status: draft
chatdoll_source_refs:
  - /tmp/ChatdollKit/README.md:15 ("Multi platforms ... including VR, AR")
  - /tmp/ChatdollKit/README.md:193-205 (AIAvatarVRM prefab + UniVRM dependency; SRP unsupported)
  - /tmp/ChatdollKit/Scripts/SpeechListener/MicrophoneManager.cs:28-127 (WebGL native-mic path; XR builds inherit the desktop/mobile mic paths)
  - /tmp/ChatdollKit/Plugins/iOS/libIOSNativeMicrophonePlugin.a (iOS native mic — also used by visionOS-compat XR builds)
  - /tmp/ChatdollKit/Plugins/Android/AndroidNativeMicrophonePlugin.aar (Android native mic — used by Quest standalone)
unity_xr_refs:
  - https://docs.unity3d.com/Packages/com.unity.xr.openxr@1.13/manual/index.html
  - https://docs.unity3d.com/Packages/com.unity.xr.interaction.toolkit@2.5/manual/index.html
  - https://docs.unity3d.com/Packages/com.unity.xr.arfoundation@5.1/manual/index.html
  - https://developer.oculus.com/documentation/unity/unity-gs-overview/
ember_subsystem_targets: [Funi, Andlit, Hjarta]
cross_refs:
  - 10_domain/1C_UNITY_LIFECYCLE_DOMAIN
  - 10_domain/1D_MULTI_PLATFORM_DOMAIN
  - 50_verification/51_SECURITY_REVIEW
  - 3B_WEBGL_BUILD
  - 3C_MOBILE_BUILD
  - sap:3A_CROSS_PLATFORM_BUILDS
  - waifu:23_MOBILE_DEPLOYMENT
---

# XR Build

> *Unity ships your scene to a headset by recompiling the world plus a stereo camera rig. ChatdollKit ships zero XR-specific code. That's both the gap and the opportunity.*

Forge-B. Eldra-iron. The headline finding first: **ChatdollKit v0.8.16 contains no XR-specific source code.** Not one provider for OpenXR, not one prefab for VR or AR, not one platform-conditional `#if UNITY_XR`. The README claim (`/tmp/ChatdollKit/README.md:15`) — *"Compatible with Windows, Mac, Linux, iOS, Android, and other Unity-supported platforms, including VR, AR, and WebGL"* — is true the way **"my Civic supports towing"** is true: only if you stand way back from what the platforms actually need.

This doc is the operator's manual for what *would* be required to ship a CDK-based Ember avatar to VR (Meta Quest, Apple Vision Pro, PSVR2, Pico) and AR (HoloLens 2, Magic Leap 2, ARKit, ARCore). The XR domain is dominated by **sensor data privacy** (gaze, hands, room geometry, head pose) and **strict performance budgets** (90 fps absolute floor on most VR; 60 fps on phone AR; below that = motion sickness). CDK's WebGL-grade mic path and per-frame uLipSync don't survive contact with either constraint without rework.

## What XR Buys

The reach an XR-capable avatar gives Ember is qualitatively different from screen or mobile:

- **Embodied co-presence.** The avatar exists as a 3D entity in the user's spatial frame. The user can walk around it (VR room-scale), look at it (gaze tracking), gesture to it (hand tracking), seat it on their actual desk (AR anchor). This is the closest realization of *companion-as-presence* the embodiment axis allows.
- **Hands-free interaction.** No keyboard, no touchscreen. Voice + gaze + gesture is the only input modality, which makes Ember's voice-first design *the right design for the medium* rather than a constraint.
- **Persistent room anchoring.** AR Foundation's session persistence (ARKit 4+, ARCore Cloud Anchors) means the avatar can live in a specific location in your room across sessions. *"The avatar is on my desk. Always. I walk in, glasses on, she's there."*
- **Spatial audio.** Avatar voice positionally coherent with avatar location. CDK's `AudioSource.PlayOneShot` becomes a spatialized point source via Unity's built-in spatializer plugins (Oculus Audio, Steam Audio). This is a free win — no CDK changes needed.

The cost is everything else.

## What XR Costs

### 1. The performance cliff

VR and AR have hard frame-rate requirements that exceed every other platform CDK targets:

| Platform | Target fps | Floor | Penalty for missing |
|---|---|---|---|
| Quest 3 (standalone) | 90/120 | 72 | Motion sickness; user removes headset |
| Vision Pro | 90 | 90 | Apple's reprojection saves you but burns battery |
| PSVR2 | 90/120 | 90 | Reprojection artifacts; user complaints |
| Pico 4 | 90 | 72 | Same as Quest |
| HoloLens 2 | 60 | 60 | Hologram instability |
| Magic Leap 2 | 60 | 60 | Hologram drift |
| Phone AR (ARKit/ARCore) | 60 | 30 | Choppy registration |

By contrast, CDK's existing platforms target 60 fps (mobile, WebGL, desktop). The **90 fps requirement** on standalone VR is the cliff. Every per-frame operation has to complete in 11.1ms (90 fps) instead of 16.7ms (60 fps). That is a **33% reduction in the per-frame budget**.

CDK's per-frame load — uLipSync vowel analysis, the lip-sync wall-clock sample-window loop (`/tmp/ChatdollKit/Scripts/Model/SpeechController.cs:189-203` per [[33_TTS_PREFETCH]]), VRM bone updates, expression blendshape updates — was profiled implicitly against 60 fps. None of it has been profiled against 90 fps. uLipSync in particular runs an FFT on the playing audio buffer every frame; the Burst-compiled job is fast but not free.

**The verdict:** CDK will probably run at 90 fps on a Quest 3 with one VRM avatar and minimal scene, but the budget is tight. Adding multiple avatars, complex scenes, or extra TTS/STT real-time processing pushes below 90. Aggressive optimization is mandatory, not optional.

### 2. The build chain

**Quest (Android-based standalone):**
- Unity Editor → install XR Plug-in Management package + Oculus XR Plugin + OpenXR Plugin
- Configure Player Settings → XR Plug-in Management → Android tab → enable Oculus
- Build → Android APK
- Sideload via SideQuest or submit to Quest Store
- Requirements: Meta developer account (free for sideloading; $0 + review for Store)

**Vision Pro (visionOS):**
- Unity Editor (Unity 2022.3 LTS or 6.0) → install Apple visionOS XR Plugin
- Configure for visionOS Mixed Reality or Fully Immersive mode
- Build → Xcode project → Xcode for visionOS
- Submit to App Store (Vision Pro section)
- Requirements: macOS + Xcode 15+ + Apple Developer Program + $99/year

**PSVR2 (PS5):**
- Unity Editor with Sony's PSVR2 plugin (NDA-gated)
- PS5 dev kit ($$$$)
- Sony developer agreement
- **Realistically: out of scope for Ember.** Console XR is a different business.

**HoloLens 2:**
- Unity Editor → install Mixed Reality Toolkit (MRTK3) + OpenXR + Mixed Reality Feature Tool
- Build → UWP / ARM64
- Sideload via Device Portal or HoloLens Store (limited)
- Requirements: Windows host + Visual Studio + Microsoft developer account

**ARKit (iOS phone/tablet AR):**
- Unity Editor → install AR Foundation + ARKit XR Plugin
- Build via iOS pipeline (same as [[3C_MOBILE_BUILD]])
- AR mode is a runtime feature, not a separate build target

**ARCore (Android phone/tablet AR):**
- Unity Editor → install AR Foundation + ARCore XR Plugin
- Build via Android pipeline (same as [[3C_MOBILE_BUILD]])
- AR mode is a runtime feature

**Magic Leap 2:**
- Unity Editor → install Magic Leap XR Plugin
- Build → Magic Leap App
- Submit to Magic Leap World
- Requirements: Magic Leap developer account + ML2 hardware ($3,300+)

The combinatorics: **six distinct toolchains for full XR coverage**, with three different host-OS requirements (macOS for Vision Pro, Windows for HoloLens, anything for the rest). Ember cannot target all of these. Realistic priority order for a small project: Quest (largest install base, lowest entry friction), iOS AR (no extra hardware needed), HoloLens 2 (enterprise interest), Vision Pro (high prestige, Apple users), Magic Leap 2 (niche), PSVR2 (skip).

### 3. The XR plug-in ecosystem

Unity's XR architecture is **plugin-driven**. The runtime contract is `UnityEngine.XR.Management.XRGeneralSettings` → an `XRLoader` per platform. The recommended cross-platform path as of 2026:

- **OpenXR** (Khronos standard) — covers Quest, Vision Pro (partial), HoloLens, Vive, most PC VR.
- **Oculus XR Plugin** — Meta-specific features (hand tracking, scene understanding, passthrough) beyond what OpenXR exposes.
- **AR Foundation** — abstraction over ARKit + ARCore + (limited) HoloLens MR.
- **PolySpatial** (visionOS) — Unity's RealityKit bridge for Vision Pro shared/immersive modes.

For Ember, OpenXR + Oculus XR Plugin (for Quest extras) covers the majority. AR Foundation handles ARKit/ARCore. Vision Pro requires PolySpatial. HoloLens uses MRTK3 (which can sit on OpenXR).

### 4. The sensor data privacy surface

This is the single most important section. XR adds **six new categories of sensor data** that desktop/mobile/WebGL CDK never had to think about. Each is a privacy surface. Each requires explicit consent. Each has a regulatory landscape.

#### Gaze tracking

What it is: where the user is *looking* in 3D space, sampled at 60-120 Hz. Available on Quest Pro, Quest 3 (limited), Vision Pro, HoloLens 2, PSVR2.

Why it matters: **gaze reveals attention.** An avatar that knows the user is looking at it can react ("yes?"). An avatar that logs gaze patterns can build a profile of what the user finds interesting, embarrassing, alarming, attractive. Gaze data is the intimate-level privacy surface of XR — closer to brain-state than even microphone audio.

Regulatory: GDPR considers eye-tracking biometric data (special category, Article 9). HIPAA implications if used in therapeutic contexts. Apple's visionOS specifically restricts gaze data — apps cannot read gaze coordinates directly; the OS only tells the app *"the user just looked at this UI element."* Quest Pro/3 exposes gaze coordinates to apps with permission.

Ember posture: **gaze data is never persisted.** Live gaze used only for in-session attention cues (avatar reacts when looked at). No gaze logging, no analytics. Vow tie-in: **Surface Without Surveillance**.

#### Hand tracking

What it is: 26+ joints per hand, sampled at 30-90 Hz. Quest, Vision Pro, HoloLens 2, Magic Leap 2 all expose this. Phone AR (ARKit/ARCore) has limited hand pose, not full skeletal.

Why it matters: hands reveal **gesture, manipulation, intent**. The user's idle fidgeting, their gestures while talking, their typed input on virtual keyboards — all sampled. Combined with audio, hand tracking is enough to **infer keystrokes from gestures** ("keyboard sniffing" research has shown this).

Regulatory: less stringent than gaze in EU law currently, but trending toward biometric classification.

Ember posture: hand data used live for gesture-to-action mapping (point at avatar to focus; open palm to pause). Not persisted. Not exported. Vow tie-in: **Surface Without Surveillance**.

#### Spatial mapping (room geometry)

What it is: a 3D mesh of the user's environment. The walls, furniture, ceiling, floor. Updated continuously as the user moves. Available on every AR/MR platform.

Why it matters: room geometry **identifies the user's location** more precisely than GPS in some cases. Combined with object recognition, the avatar can know which room of the user's house it's in, what's in it, how it changes over time. This is location data at house-room granularity.

Regulatory: location data under GDPR. Apple's visionOS restricts raw scene mesh access; apps get planes and anchors, not raw geometry.

Ember posture: avatar uses planes for placement (anchor on a flat surface). Raw mesh never read, never persisted, never exported. Vow tie-in: **Surface Without Surveillance**, **Smallness**.

#### Head pose

What it is: 6DoF (position + orientation) of the user's head, sampled at the display refresh rate (90-120 Hz). Available on every VR/MR headset.

Why it matters: head pose patterns reveal **emotional state** (slumped posture = sad/tired; head shakes = disagreement) and **identity** (gait-like head-bob patterns are biometric). A long head-pose log is a behavioral fingerprint.

Regulatory: gray area, trending toward biometric.

Ember posture: head pose used live for avatar's eye-contact behavior (avatar's gaze tracks user's head). Not logged. Vow tie-in: **Surface Without Surveillance**.

#### Microphone (already a CDK surface)

CDK already handles mic on desktop/mobile. XR adds two complications:
- **AEC is mandatory** for continuous-barge-in (see [[37_BARGE_IN_INTERRUPT]]). All major VR headsets ship AEC at the OS layer (Quest, Vision Pro). Good.
- **Spatial mic arrays.** Quest Pro and Vision Pro have multi-mic arrays usable for beamforming. CDK doesn't use these; would need a new MicrophoneProvider.

Ember posture: voice handled per [[3C_MOBILE_BUILD]] Mic Provider pattern. AEC enabled.

#### Camera (passthrough / world camera)

What it is: live RGB video of the user's environment, available to passthrough-AR apps (Quest 3 passthrough, Vision Pro EyeSight, ARKit/ARCore camera feed).

Why it matters: **the most invasive single sensor in XR.** Live video of the user's environment, face (via reflections), other people in the room. Vision Pro restricts camera-feed access tightly; Quest 3 with passthrough exposes it to apps with permission.

Regulatory: camera in the home is a strict GDPR / privacy regulation surface. App Stores require explicit purpose statements.

Ember posture: camera **not used by default**. Optional opt-in feature for explicit user request only ("show me what I'm looking at and describe it"). Frames processed in-memory, never stored, never sent to cloud unless explicitly user-initiated. Vow tie-in: **Surface Without Surveillance**, **Consent-Gated**.

### 5. The avatar-as-companion-in-the-room affordance

This is the upside that pays for all of the above. In a VR scene the avatar is a 3D entity with physical presence. The user is no longer looking at a screen with the avatar on it; the avatar is in the room with them. Specific behaviors XR unlocks:

- **Gaze-aware response.** When the user looks at the avatar, the avatar's idle animation becomes more attentive (slight lean-in). When the user looks away, the avatar's idle relaxes. Computed from head pose; no gaze-data required.
- **Spatial summoning.** "Come here" gesture brings the avatar to a position; "stay there" anchors it. AR Foundation anchors + ARWorldMap-style persistence makes this last across sessions.
- **Co-located gesture.** Avatar can point at real objects (with permission to read spatial planes), can hand the user a virtual object (interaction with hand tracking), can sit on a real chair (anchored to a real-world plane).
- **Whisper-mode.** Spatial audio drop-off means the avatar can speak quietly without the user moving any UI. Lean closer to hear; lean back for normal volume. Natural, embodied, requires zero new CDK code (Unity's spatializer does it).

This is the affordance that justifies the XR investment. It is also the affordance that makes the sensor-data privacy surface unavoidable: presence requires sensing.

### 6. Where CDK falls short for XR

A walkthrough of what would need to change in CDK to ship to Quest:

**Mic plugin (resolvable):** Quest is Android-under-the-hood; `Plugins/Android/AndroidNativeMicrophonePlugin.aar` mostly works. But the AEC mode used (`MediaRecorder.AudioSource.VOICE_COMMUNICATION`) interacts with the OS's spatial audio pipeline in ways untested. Operator must verify. Possibly needs a `QuestMicrophoneProvider` that uses Oculus's audio APIs directly.

**Render pipeline (architecture-level):** CDK explicitly forbids SRP (`README.md:195` — *"Do not use the SRP project template ... UniVRM ... does not support SRP."*). But XR needs SRP for stereo rendering optimizations (Single Pass Instanced rendering). Either:
- UniVRM adds SRP support (out of Ember's control)
- Ember-CDK uses BiRP (Built-in Render Pipeline) on XR, accepting the perf hit
- Ember adopts an alternative VRM loader that supports SRP

The BiRP path works but leaves frame-budget on the table.

**uLipSync (perf concern):** uLipSync's per-frame FFT was profiled for mobile; on Quest 3 it likely fits in the budget but operator must measure. On Quest 2 (still in active install base), it may push frame-budget into reprojection. Fallback: use ARKit/Vision Pro's built-in blendshape stream where available (Apple ARKit provides 52 facial blendshapes from face tracking on Vision Pro). Drops uLipSync entirely on supported devices.

**Animation pipeline ([[34_ANIMATION_PIPELINE]]):** Idle/gesture animations were authored against 60 fps. They will play at 90 fps in VR with no logical issue, but the *feel* of gesture timing changes (1.5x faster). Animators must re-author or use Unity's animation speed multiplier.

**Camera setup:** CDK ships a single perspective camera in its prefabs. XR requires the XR Origin's stereo camera rig. Operators must delete CDK's camera and use XR Origin. Not hard, but a footgun.

**Input system:** CDK uses mouse-and-keyboard input for its admin UI and message-window interactions. None of this works in VR. Operators must build an XR-input adapter (world-space UI, ray-based pointer, hand-pinch select). Mixed Reality Toolkit (MRTK3) provides this; Unity XR Interaction Toolkit provides it; CDK provides nothing.

**TTS prefetch ([[33_TTS_PREFETCH]]):** the wall-clock lip-sync timing path will drift more in XR because of frame-pacing and reprojection. AudioSource sample-position based timing is the right path; CDK uses wall-clock.

**MessageWindow:** CDK's text overlay assumes 2D screen-space canvas. In VR this must be world-space (floating panel near avatar) or hidden entirely (voice-only).

The verdict: shipping CDK to Quest is **possible with operator work** estimated at 2-4 person-weeks of integration + 1-2 weeks of tuning. Vision Pro is harder (PolySpatial + visionOS-specific behavior is its own learning curve). HoloLens is hardest (UWP toolchain + MRTK3).

### 7. Performance tier framework

For Ember's tier-config approach (per [[3C_MOBILE_BUILD]]), XR adds new tiers:

| Tier | Target | fps | Avatar quality | Sensor surface |
|---|---|---|---|---|
| `xr-vr-flagship` | Quest 3, Vision Pro, Pico 4 | 90 | Full VRM + full lip-sync + full gesture | All sensors w/ consent |
| `xr-vr-mid` | Quest 2, Pico Neo 3 | 72 | Reduced poly + simplified lip-sync | Mic + head pose only |
| `xr-mr-enterprise` | HoloLens 2, Magic Leap 2 | 60 | World-anchored, simplified shading | Spatial mapping (planes) + mic |
| `xr-ar-mobile` | ARKit/ARCore phones | 60 | Phone AR foreground only | Camera + spatial planes + mic |

Each tier sets:
- Polygon budget per avatar (10k for `xr-vr-flagship`, 3k for `xr-vr-mid`)
- Blendshape count (full 52 for flagship, 8 vowels only for mid)
- Animation update rate (every frame for flagship, every other frame for mid)
- Sensor consent prompts (which surfaces are requested)

CDK has no tier framework; Ember must build it. See Invent.

### 8. App Store / Store hoops, by platform

**Meta Quest Store:**
- App must perform within Meta's VRC (Virtual Reality Check) standards
- Comfort rating required (Comfortable / Moderate / Intense)
- Privacy policy mandatory
- Adult content: Meta has an Adult-only category (App Lab); Ember mythic-tier could ship there
- Frame-rate compliance is *enforced*

**Apple Vision Pro App Store:**
- Same iOS-style review (`[[3C_MOBILE_BUILD]]` constraints)
- Stricter privacy declarations (gaze, hand, scene)
- "Person" entities (avatars resembling people) face additional scrutiny

**HoloLens Store / Microsoft Store:**
- UWP packaging
- Less strict content review
- Enterprise deployment via Intune bypasses store entirely

**Magic Leap World:**
- Curated; smaller install base
- Less stringent review than Apple, more than Meta

**ARKit/ARCore on phone App Stores:** same as [[3C_MOBILE_BUILD]] — iOS strict on adult content, Android more permissive.

## Where It Surprises

- **Vision Pro's gaze model is the privacy reference design.** Apps don't see raw gaze; the OS just emits "user is looking at element X" events. This is the right architecture and the model Ember should follow on Quest by *not reading raw gaze even when the platform exposes it.*
- **Spatial audio is free.** Unity's spatializer plugins drop into CDK's AudioSource with no code changes. The avatar's voice is positionally coherent without effort.
- **Quest 3's passthrough enables AR-on-VR-hardware.** You don't need a separate AR build; the Quest 3 Mixed Reality mode lets a VR app behave like an AR app. The build target is still Quest VR; the runtime decides.
- **PolySpatial (Unity for visionOS) is its own toolchain.** Vision Pro doesn't run a Unity scene the same way other platforms do. The scene tree gets transformed into RealityKit entities. Many Unity features don't translate. This is a real learning curve, not a small adaptation.
- **OpenXR is genuinely cross-platform now.** A single OpenXR build mostly runs on Quest, Vive, Pico, HTC Focus, Windows MR. The platform-specific extensions (hand tracking, gaze, anchors) need conditional code, but the core build is portable. This was not true two years ago.
- **uLipSync's FFT is the perf hot-spot to watch on Quest 2.** The Burst compilation helps; running it every frame at 72 fps + animation pipeline + lip-sync wall-clock loop can saturate the avatar thread. Profile early.
- **The CDK + UniVRM SRP constraint is a real blocker for Vision Pro.** PolySpatial expects URP (Universal Render Pipeline). Until UniVRM supports URP or Ember adopts a URP-compatible VRM loader, Vision Pro is gated.
- **Meta's hand-tracking model is shockingly good.** The skeletal tracking from Quest 3's cameras is accurate enough for typing on virtual keyboards. The privacy implications are correspondingly large.
- **Vision Pro doesn't have controllers.** All input is gaze + pinch. Ember's UX must work with no buttons. Voice + gaze is the only path.

## Where It Breaks

- **CDK has no XR scene template, no XR input adapter, no XR UI.** Operators build all of it.
- **SRP-incompatibility of UniVRM** gates the URP-required platforms (Vision Pro PolySpatial).
- **90 fps frame budget is untested for CDK.** No public benchmarks. Risk is real.
- **Multi-headset device fragmentation** is worse than mobile. Quest 2/3/3S/Pro, Pico 4/Neo 3, Vision Pro, Vive Focus, HoloLens 2, Magic Leap 2 — each with different sensor profiles, polygon budgets, and SDK lifecycles.
- **The "avatar in your home" affordance has no consent UX in CDK.** No flow for "the avatar wants to scan your room — allow?" Operators must build the full consent stack.
- **Battery drain on standalone VR is severe.** A Quest 3 running a CDK avatar for an hour drains the battery noticeably. The avatar-as-always-on-companion vision is incompatible with current XR hardware battery life. (Charging cable + facial-foam-replacement is the only path to "all day".)
- **Eye-tracking calibration is per-user per-session on most headsets.** Avatar can't use gaze data until calibration completes. The cold-start UX is a real friction.
- **Hand-tracking failure modes are subtle.** When tracking is lost (hands behind back, in pockets, in dark room), gesture-driven interactions fail silently. CDK has no fallback voice-only mode tied to "hands invisible" events.
- **AR Foundation's session lifecycle differs from CDK's.** ARKit/ARCore sessions can pause, resume, lose tracking. CDK's `AIAvatar` lifecycle doesn't know about this and may continue running while AR tracking is dead.
- **No Spatial Anchors persistence in CDK.** Avatar position resets per session. The "she's always on my desk" affordance requires Cloud Anchors / ARWorldMap integration — Ember must build it.
- **MRTK3 is its own world.** Adopting Mixed Reality Toolkit for HoloLens means importing a large Microsoft framework that doesn't compose cleanly with CDK's prefab structure.
- **PSVR2 NDA-gated.** Out of reach for an open project.
- **Eye-strain and motion-sickness liability.** XR avatars that move erratically, that occlude the user's view at close range, or that play unexpected sounds can trigger genuine physical discomfort. CDK has no safety profile for this; operators carry full liability.

## On-Device LLM in XR

XR hardware is heterogeneous in LLM capability:

- **Quest 3:** Snapdragon XR2 Gen 2, 8 GB RAM. Can run llama-3.2-1B at acceptable speed but with significant heat/battery cost. Llama-3.2-3B at usable speed if you accept battery.
- **Vision Pro:** M2, 16 GB RAM. Can run much larger models — Phi-3-mini, Llama-3.2-3B easily, plausibly Llama-3.2-8B at 4-bit. Apple Foundation Models will likely become the canonical path.
- **Quest 2:** Snapdragon XR2 Gen 1, 6 GB RAM. Llama-3.2-1B with care; anything larger thermal-throttles.
- **HoloLens 2:** Snapdragon 850, 4 GB RAM. Cloud-LLM only realistically.
- **Magic Leap 2:** AMD Quad-Core, 16 GB RAM (CPU-side). Llama-3.2-3B viable on CPU but compute budget shared with rendering.

For Ember, the tier framework continues into XR: `xr-tier-base` for cloud-LLM defaults, `xr-tier-mini` for Llama-3.2-1B on Quest 3 / Vision Pro, `xr-tier-foundation` for Vision Pro using Apple Foundation Models. The same llama.cpp-Unity bridge proposed in [[3C_MOBILE_BUILD]] Invents extends here.

## Cross-References

- [[10_domain/1C_UNITY_LIFECYCLE_DOMAIN]] — Unity's XR Plugin Management architecture
- [[10_domain/1D_MULTI_PLATFORM_DOMAIN]] — platform matrix; XR is the most-distant cell
- [[50_verification/51_SECURITY_REVIEW]] — Auditor on the six XR sensor surfaces
- [[3B_WEBGL_BUILD]] — sibling; WebGL is the cheap-and-everywhere tier; XR is the expensive-and-everywhere-special tier
- [[3C_MOBILE_BUILD]] — sibling; MicrophoneProvider abstraction extends; tier-config extends; native-plugin discipline extends
- [[37_BARGE_IN_INTERRUPT]] — barge-in is critical for XR (hands-free voice-first); AEC mandatory
- [[sap:3A_CROSS_PLATFORM_BUILDS]] — contrast: SAP targets desktop OS, no XR ambition
- [[waifu:23_MOBILE_DEPLOYMENT]] — contrast: Waifu's WebRTC stack could in principle run in WebXR but the cloud-streaming-of-avatar approach loses to native VRM-in-headset on latency, so the embodiment-axis decision is clear

## What This Means for Ember

*Apache-2.0 attribution: ChatdollKit's `MicrophoneProvider` abstraction, `AIAvatarVRM` prefab pattern, and ModelController architecture are the patterns extended here. Preserve upstream header reference per Apache-2.0 §4(c) when vendoring.*

**Adopt:**

- **The `MicrophoneProvider` abstraction extended with `QuestMicrophoneProvider` and `VisionProMicrophoneProvider`** (CDK pattern from `[[3C_MOBILE_BUILD]]`, Apache-2.0 attribution required). Same C# interface, XR-platform-specific implementations using each headset's spatial-mic APIs.
- **The VRM-as-canonical-avatar-format choice.** UniVRM works (with the BiRP caveat) on Quest. VRM is the right open format. Adopt CDK's stance on VRM over proprietary avatar formats.
- **The "AEC mandatory for continuous voice" stance from `[[37_BARGE_IN_INTERRUPT]]`.** All XR voice modes ship with `MicrophoneMuteBy = None` and AEC verified.
- **Spatial audio via Unity built-in spatializer.** Free win; adopt as default. No code changes; just set `AudioSource.spatialBlend = 1` on the avatar's voice.
- **The "no XR-specific code in core" posture** is itself adoptable: keep XR adapters as separate optional asmdefs (`Ember.Andlit.XR.Quest`, `Ember.Andlit.XR.VisionPro`, etc.) so non-XR builds don't import the dependencies.

**Adapt:**

- **CDK's single perspective-camera prefab → XR Origin stereo-camera rig.** Ember provides `EmberAvatarXR.prefab` parallel to `EmberAvatarDesktop.prefab`. Same scripts; different camera setup.
- **2D message window → world-space message panel.** Adapt CDK's MessageWindow to a world-space canvas anchored near the avatar at user's eye level.
- **Mouse/keyboard input → gaze + pinch (Vision Pro), ray + trigger (Quest controllers), pinch (Quest hand-tracking).** Adapt CDK's admin UI to Unity XR Interaction Toolkit ray-pointers.
- **wall-clock lip-sync timing → AudioSource sample-position timing.** Critical for XR where frame-pacing variance is higher. (Also a CDK-general improvement per [[33_TTS_PREFETCH]] "Avoid" list.)
- **uLipSync FFT → conditional path: uLipSync on Quest, ARKit face blendshapes on Vision Pro.** Use the platform's best lip-sync signal; uLipSync is the fallback.
- **CDK's tier-less design → tier-config-with-XR-tiers** as outlined in §7 above. Build target picks tier; tier sets polygon budget, blendshape count, sensor consents.

**Avoid:**

- **Raw gaze coordinate reading on Quest 3 even when permitted.** Follow Vision Pro's "events only" model. Vow tie-in: **Surface Without Surveillance**.
- **Persisting any spatial / hand / gaze / head-pose data.** All live; none logged.
- **Default camera-feed access.** Even with permission, never on by default.
- **Targeting all six XR platforms in v1.** Quest first. iOS AR second. Anything else: scoped per release.
- **Adopting MRTK3 wholesale.** Too large for Ember's Smallness Vow. Cherry-pick if HoloLens becomes a target.
- **Building for PSVR2.** NDA-gated, console-business, off-mission.
- **SRP commitment.** Until UniVRM has stable URP/HDRP support, stay on BiRP and accept the perf cost. Re-evaluate annually.
- **Permanent avatar always-on-in-headset use cases.** Battery reality precludes this until 2028+ hardware. Design for episodic XR sessions, not all-day wear.

**Invent:**

- **Andlit XR Tier Manifest.** `data/charts/xr_tiers.yaml` declares per-platform: polygon budget, blendshape count, sensor consent prompts, lip-sync provider, mic provider, render-pipeline override, frame-rate floor. CI consumes; builds per-tier artifacts. Vow tie-in: **Smallness**, **Modular Authorship**.
- **Ember Consent Choreography for XR.** A scripted first-run consent flow specifically for XR. Avatar appears in front of user; speaks: *"To stand here, I need to know where the floor is. May I look at your floor? (planes only — I won't see the room.)"* Per-sensor, per-utility, conversational consent. Replaces opaque OS prompts where possible. Vow tie-in: **Consent-Gated**, **Mythic Conversation**.
- **Hjarta Sensor Audit Trail.** Every sensor read produces an in-memory `SensorReadEvent { sensor: gaze|hand|spatial|head|cam, count: int, retention: zero }`. Hjarta surfaces this to the user on demand ("what data did you use this session?"). Zero retention is the design constraint; the count proves the constraint. Vow tie-in: **Open Knowledge**, **Surface Without Surveillance**.
- **Funi XR Render-Pipeline Switch.** Build-time flag selects BiRP (default for Quest, mobile AR, current UniVRM) or URP (when UniVRM URP support lands; required for Vision Pro PolySpatial). Single source tree, two build artifacts. Vow tie-in: **Modular Authorship**.
- **Andlit Spatial Anchor Persistence.** Avatar position in the user's room persists across sessions via ARKit ARWorldMap + ARCore Cloud Anchors. The avatar "lives" in a chosen spot. User can re-anchor at will. Anchor data stored encrypted-at-rest in user's local profile, never cloud-synced without explicit opt-in. Vow tie-in: **Tethered Self**, **Surface Without Surveillance**.
- **Strengr Frame-Budget Governor.** A per-frame load monitor that, on missed frame deadlines, automatically degrades: reduces animation update rate, simplifies lip-sync, drops blendshape count. Avatar stays at 90 fps even on Quest 2 by losing visual fidelity gracefully. CDK has no such governor. Vow tie-in: **Smallness**, **Robust Under Constraint**.
- **Andlit Whisper Mode.** Spatial audio inverse-distance falloff means the user can lean in to hear the avatar quietly. Whisper mode tunes the falloff steeper. The avatar can murmur, reserved for intimate / confidential content. Vow tie-in: **Mythic Conversation**, **Care**.
- **Munnr Gaze-Aware Pacing.** Without reading raw gaze coordinates, but using head-pose-derived "is the user facing me" signal, the avatar paces speech: speeds up when the user looks away (give them the gist), slows down when attentive. Adaptive based on engagement signal, not invasive surveillance. Vow tie-in: **Mythic Conversation**.
- **Hjarta XR Comfort Profile.** Per-user comfort settings persisted: snap-turn vs smooth-turn preference, motion-blur tolerance, max avatar approach distance ("don't come closer than 70cm"). Avatar respects the profile. Sets a comfort floor that CDK doesn't address. Vow tie-in: **Care**, **Consent-Gated**.

---

*Apache-2.0 attribution: when adopting CDK's avatar / mic / VRM-loading patterns extended into XR, preserve the ChatdollKit header reference per Apache-2.0 §4(c). The XR-specific scaffolding (XR Origin integration, sensor consent flow, tier manifest) is Ember-invented; CDK contributes the per-platform discipline pattern those Inventions extend.*

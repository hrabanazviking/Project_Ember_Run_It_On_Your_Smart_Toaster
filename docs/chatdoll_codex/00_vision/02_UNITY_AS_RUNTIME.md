---
codex_id: 02_UNITY_AS_RUNTIME
title: Unity as Runtime — What the Engine Gives, What the Engine Asks
role: Skald
layer: Vision
status: draft
cdk_source_refs:
  - /tmp/ChatdollKit/Scripts/ChatdollKit.asmdef
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:15
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:117-145
  - /tmp/ChatdollKit/Scripts/Network/SocketServer.cs:19
  - /tmp/ChatdollKit/Scripts/SpeechListener/MicrophoneManager.cs:4-12
  - /tmp/ChatdollKit/Scripts/SpeechListener/MicrophoneManager.cs:26-30
  - /tmp/ChatdollKit/Scripts/IO/JavaScriptMessageHandler.cs:10-30
  - /tmp/ChatdollKit/Scripts/Model/ModelController.cs:11-40
  - /tmp/ChatdollKit/Extension/VRM/VRMLoader.cs
  - /tmp/ChatdollKit/Extension/SileroVAD/SileroVADProcessor.cs
  - /tmp/ChatdollKit/Plugins/Android
  - /tmp/ChatdollKit/Plugins/iOS
  - /tmp/ChatdollKit/Plugins/ChatGPTServiceWebGL.jslib
  - /tmp/ChatdollKit/LICENSE
  - /tmp/ChatdollKit/README.md:17
ember_subsystem_targets: [Andlit, Rödd, Veizla, Funi, Brunnr, Munnr]
cross_refs:
  - 00_vision/00_OVERTURE
  - 00_vision/01_CDK_ESSENCE
  - 00_vision/03_ANTI_CDK
  - 00_vision/04_VISION_SYNTHESIS
  - 10_domain/1C_UNITY_LIFECYCLE_DOMAIN
  - 10_domain/1D_MULTI_PLATFORM_DOMAIN
  - 50_verification/50_DEPENDENCY_HEALTH
  - 60_synthesis/61_ANDLIT_UNITY_TIER
  - 60_synthesis/62_MOBILE_AND_XR_TIER
  - sap:11_AVATAR_DOMAIN
  - sap:63_PERFORMANCE_TIER_ENGINE
  - waifu:01_VISION_SYNTHESIS
---

# Unity as Runtime — What the Engine Gives, What the Engine Asks

> *Every engine is a country with its own customs, its own taxes, and its own ports of entry. The question is never whether the engine is good. The question is whether the country fits the journey.*
> — Sigrún Ljósbrá, drawing the customs map

## I. The question this document holds

The previous overture established that ChatdollKit's existence makes the *third position on the embodiment axis* legible — Andlit-unity, engine-native local, sister to Andlit-electron (SAP) and Andlit-realtime (Waifu). The previous essence document established that ChatdollKit *wants* to be a doll-as-companion, with Unity as the runtime that makes the want technically possible.

This document holds the trade-off honestly.

The question is not *is ChatdollKit a good codebase*. It is. The question is not *does Unity work*. It does. The question is not *is the cross-platform reach real*. It is real, demonstrably, in eighteen thousand lines of working code shipping on the App Store.

The question is:

> *What does Unity, as an embodiment runtime for an Ember-equivalent, give? What does Unity ask? And is the ratio of give-to-ask one that Ember should accept, refuse, or partially adopt?*

I will name the gives. I will name the asks. I will not render verdict — the verdict belongs to `[[60_synthesis/61_ANDLIT_UNITY_TIER]]` after the domain layer documents Unity's actual surface, and ultimately to the operator after the synthesis lands. The Vision document's job is to draw the customs map accurately enough that the verdict can be earned.

## II. What Unity gives

Six things. I will name each with evidence from ChatdollKit's source.

### Give 1 — Cross-platform reach as a single codebase

The most concrete and the most consequential. ChatdollKit's `Scripts/AIAvatar.cs:15` declares one `public class AIAvatar : MonoBehaviour`. That class compiles, unchanged, to Windows (.exe with Mono runtime), macOS (.app with Mono), Linux (.x86_64 with Mono), iOS (.ipa with IL2CPP-AOT), Android (.apk with IL2CPP-AOT), WebGL (asm.js/wasm via Emscripten), and the various XR targets (Quest, Vive, HoloLens) when the Unity XR plugins are installed. The platform-deltas live in `#if` directives — `SocketServer.cs:19` (`#if !UNITY_WEBGL` because the TCP socket layer cannot be built for the browser target), `MicrophoneManager.cs:4-12` (`#if UNITY_WEBGL && !UNITY_EDITOR` for the WebGL emscripten microphone path versus the Unity-default Mono microphone path), and the parallel `*ServiceWebGL.cs` shadow classes for ChatGPT/Claude/Gemini/Dify/AIAvatarKit (each of which routes around the *no-system-net-stack-in-WebGL* limitation by passing through the JavaScript bridge).

The discipline is impressive. The platform-delta surface is *isolated and small*. Roughly fifteen `*WebGL.cs` shadow files, two native-microphone classes per mobile platform, and a `.jslib` plugin file per WebGL-LLM-provider. That is the *entire* platform-specific surface for the eight build targets. The asmdef at `Scripts/ChatdollKit.asmdef` keeps the dependency graph clean (three references: Unity's native packages and `com.endel.nativewebsocket` as a version-defined dependency). The same Ember-equivalent code, hypothetically built on this scaffold, would inherit the same multi-platform reach with no per-platform engineering beyond what ChatdollKit already does.

This is the give the prior corpora *could not deliver*. SAP runs on three desktop platforms (Win/Mac/Linux). The Waifu kit runs in a browser. Hermes runs anywhere Python runs (which is most things, but no mobile, no XR, no game console). ChatdollKit *runs everywhere a 3D game runs*, which is most consumer hardware on Earth.

For Ember, the implication is profound *if* Ember wants to live on phones, on headsets, on browsers — and *zero* if Ember stays on the desktop/server tier where the prior corpora's reach already suffices.

### Give 2 — Mature animation, expression, and lip-sync as engine subsystems

The second give: Unity *has been doing character animation for fifteen years*, and ChatdollKit inherits all of that for free.

The `Model/ModelController.cs:11-40` shows the inheritance. The `Animator` component (`ModelController.cs:30` — `private Animator animator`) is Unity's built-in state-machine animation system. The animation queue (`ModelController.cs:31` — `List<Animation> animationQueue`) feeds into the Animator's layered state-machine system, with `CrossFadeInFixedTime` for blending (`ModelController.cs:309`). The lip-sync helper (`ILipSyncHelper` interface, `Model/ILipSyncHelper.cs:10`) is a *pluggable* interface — VRM uses `uLipSyncHelper.cs` (107 lines, references the `uLipSync` package via its asmdef GUID reference). The blink controller (`Model/Blink.cs`, 198 lines) is a *dedicated MonoBehaviour for the doll's eyes blinking*, with proper Unity coroutine timing.

The Unity-side libraries (UniVRM for VRM model loading, Burst for performance, UniTask for async, Newtonsoft for JSON, uLipSync for mouth-shape detection) are all *existing, well-tested third-party packages* in the Unity ecosystem. ChatdollKit *consumes* them; ChatdollKit does not *re-implement* them.

The comparison with SAP is stark. SAP's lip-sync at `[[sap:vts_manager.py:144-179]]` is *FFT vowel detection in Python on a PCM stream*, driving *VTube Studio over WebSocket*, in a *separate process from the avatar renderer*. ChatdollKit's lip-sync is a *Unity-native interface implementation* that drives a `VRMFaceExpressionProxy` *in the same engine update tick* as the animation queue. SAP's pipeline has roughly six processes coordinating; CDK's has one.

The give: *mature animation infrastructure for free*. The catch: *the infrastructure assumes Unity*, and replicating equivalent infrastructure outside Unity is a multi-month effort (the Three.js + WebAudio + custom-blendshape-pipeline tract that the Waifu kit's vendor invisibly runs in its datacenter).

### Give 3 — Asset ecosystem (UniVRM, uLipSync, Unity Asset Store)

The third give: ChatdollKit lives in a Unity package ecosystem where character-AI infrastructure is *cheap to acquire*. UniVRM (`/tmp/ChatdollKit/Extension/VRM/VRMLoader.cs`) handles VRM model loading and bone mapping. uLipSync handles mouth-shape detection from audio. The Asset Store offers VRM models (free and paid), animation packages (Mocap libraries, gesture sets), and the cultural-asset pipeline (Mixamo bridges, VRoid Studio output integration).

For an Ember-equivalent on Unity, this means *not implementing model loading*, *not implementing character animation*, *not implementing the asset import pipeline*. The doll's *body* is something the operator drops into the scene from VRoid Studio (free, web-based character creator) or buys from the Asset Store; the doll's *animations* are mocap data the operator buys from Mixamo; the doll's *expressions* are FaceClips configured in Unity Inspector.

The give: *the assets are bigger than the code*, and the assets are *already curated by humans*. The catch: *the asset ecosystem assumes Unity-and-VRM*, and adopting it commits Ember to a particular file-format chain.

### Give 4 — Mobile and XR support as engine features

The fourth give: iOS and Android are *engine targets*, not afterthoughts. The native plugins at `Plugins/iOS/IOSNativeMicrophone*.cs` and `Plugins/Android/AndroidNativeMicrophone*.cs` integrate with the platform's native echo-cancellation, noise-suppression, and microphone-access APIs. The platform-specific permission handling (mic permission on iOS, mic permission on Android) is *Unity's responsibility*; ChatdollKit handles only the *application-level* concerns. The XR target (Quest, Vive, HoloLens, ARKit, ARCore) similarly inherits Unity's `XR` subsystem — input handling, head tracking, controller tracking, hand tracking — for free.

The README claims XR support (`/tmp/ChatdollKit/README.md:17`: *VR, AR, and WebGL*); the demo scenes in `/tmp/ChatdollKit/Demo/` reveal asset configuration but not the full XR build pipeline. The claim is `[unverified — README claim only]` at the level of demonstrable evidence, but the engine support is *unquestionably present* — Unity's XR subsystem is mature, used by tens of thousands of shipping VR apps, and CDK's MonoBehaviour-based code is engine-native enough to inherit XR support without additional engineering.

For Ember, the implication: *if* Ember wants to be a VR-headset companion (live in the operator's VR home, accessible by gaze and gesture), Unity is the *only* path that gets there without building a custom XR runtime. The hand-built alternatives (custom WebXR, raw OpenXR with bespoke rendering) are *multi-person-year* engineering efforts.

### Give 5 — Render quality and visual presence

The fifth give: a Unity render is *visually competent by default*. The same VRM model that looks like *a blocky proxy* in a WebGL Three.js scene looks like *a properly-shaded character* in Unity's Universal Render Pipeline (URP). The lighting, shadows, post-processing, anti-aliasing — all engine-default and shippable. ChatdollKit's demo scenes (`/tmp/ChatdollKit/Demo/`) ship with proper lighting setups.

The give matters because *embodiment is partly aesthetic*. A doll that looks like a polygon-soup is *less of a companion* than a doll that looks like a finished character. The Waifu kit's vendor-cloud avatar achieves visual quality by running on datacenter GPUs; Andlit-local in Unity achieves it by running URP on the operator's mid-range GPU. Both are visually competent; the SAP-style VTube Studio + VRM-on-host approach is also visually competent but requires the VTube Studio software *plus* the avatar render *plus* the operator's setup.

For Ember, the give is real but *tier-specific*. Pi-tier and laptop-tier Ember does not need render quality at this level. Workstation-tier and VR-tier Ember does. The Vow of Tiered Presence (`[[sap:61_NEW_VOWS]]`) allows render quality to *increase with tier*, not *be required at all tiers*.

### Give 6 — A single tick to coordinate everything

The sixth give: Unity gives ChatdollKit *one update loop* in which animation, audio, network, input, and rendering all execute deterministically per-frame. The `AIAvatar.cs:117-145` `Start()` method wires the entire system into one coroutine-driven lifecycle. The DialogProcessor's `OnEndAsync` callback (`AIAvatar.cs:197`) fires *on the main thread* because Unity's coroutines are main-thread-only. The SocketServer queues messages on a background thread but processes them on the main thread (`SocketServer.cs:43-50` — the `lock(queueLock)` then `OnDataReceived?.Invoke(message)` happens *in the main-thread Update()*).

This is the *opposite* of SAP's multi-process Python+Electron+VTS+VMC coordination headache. CDK's single-update-loop is a coordination *primitive* the engine gives for free. It makes the codebase *easier to reason about* than any multi-process embodied-AI architecture.

For Ember, the give is *substantial but engine-specific*. The benefit only accrues if Ember actually runs in Unity. The architectural lesson — *coordinate embodiment through a single deterministic tick* — transfers; the specific Unity Update loop does not.

## III. What Unity asks

Six asks. Each is real. Each is a cost the engine demands in exchange for the gives above.

### Ask 1 — Engine commitment as foundation

The most fundamental ask: *adopting Unity means committing to Unity at the foundation level*. The Unity Editor is a 5–10GB install. The Unity Hub is the install-manager that adds another half-gig. The Unity LTS version (currently 2022.3 LTS) is the *required minimum*; future engine updates can break builds. The Unity asmdef system, prefab system, scene system, and component-MonoBehaviour paradigm are not optional — they are the *only* way to write Unity code.

For Ember, this is the ask the Vow of Smallness rejects most directly. Ember's baseline is *runnable on a Pi 5 with 8GB of RAM*. Unity does not run *as a development environment* on a Pi at all (the Editor requires Windows/Mac/Linux x86_64 with substantial GPU). Unity *deployments* can target ARM (the Quest 2 is ARM; the Pi WebGL build target is technically ARM-compatible), but the *development experience* is desktop-only.

This means: *the operator who builds Ember has to have Unity installed*. The operator who *runs* Ember does not (a Unity build is a standalone executable + assets). But the *modification path* — the operator who wants to change Ember's behavior, swap a VRM, add an animation — *must have the engine*. The Vow of Public-Friendliness pulls against this: Ember-on-Unity is friendly to *operators who already use Unity* and unfriendly to *operators for whom Unity is friction*.

### Ask 2 — Binary size and runtime weight

The second ask: a Unity build is *not small*. The minimum standalone executable for a basic Unity project is roughly 50MB; a typical project with URP, character animation, audio, and VRM ships at 100–200MB. WebGL builds are 30–80MB after compression (asm.js or wasm output). Mobile builds (iOS, Android) are 80–200MB depending on the asset payload.

For comparison: Ember's Pi-baseline Python footprint is likely under 100MB *including* the venv. Hermes's CLI is a single 14k-line Python file with imports. The Waifu kit's bundled React app is ~5MB. SAP's Electron + Python footprint is ~500MB (Electron is large), so SAP-style is the closest precedent.

The size cost is *real* but *tier-appropriate*. A Pi-tier Ember that ships as a 200MB Unity binary is a Vow violation. A workstation-tier or VR-tier Ember that ships as a 200MB Unity binary is *normal-for-the-tier*. The Tier Engine (`[[sap:63_PERFORMANCE_TIER_ENGINE]]`) already accommodates this: optional surfaces light up only at appropriate tiers.

### Ask 3 — Learning curve and cultural shift

The third ask: *writing Unity code is not writing Python code*. The C# language, the MonoBehaviour paradigm (every script is a component that attaches to a GameObject), the inspector-driven configuration (SerializeField), the prefab system (asset templates with overridable instances), the asset import pipeline (PNG→Texture2D, FBX→Mesh, .anim→AnimationClip), the build pipeline (Build Settings, scene list, platform-specific settings), the project structure (Assets/, Library/, ProjectSettings/) — all of these are Unity-specific knowledge that takes weeks to internalize.

For Ember, this is the cultural-shift cost. The Mythic Engineering practice is built around Python-and-text-files. The Six roles (Skald, Architect, Cartographer, Forge, Auditor, Scribe) write *in markdown about Python*. A Unity-foundation Ember would require *Unity-aware versions of every role* — the Architect would need to draw diagrams in Unity Inspector terms, the Forge would need to write MonoBehaviour-shaped code with SerializeFields, the Auditor would need to understand the asset-bundle security model. This is *not impossible*, but it is *not free*.

The Vow of Modular Authorship allows the cost to be *isolated* to Andlit-unity if the engine is adopted as *one sub-name* rather than *the foundation*. Andlit-unity would have its own role-pattern; the rest of Ember remains Python-and-text-files. This is what `[[60_synthesis/61_ANDLIT_UNITY_TIER]]` argues toward.

### Ask 4 — License surface

The fourth ask: Unity has a *non-trivial license posture* that Ember's Vow of Open Knowledge must engage.

Unity Personal is free for individuals and small companies with revenue under $200K USD per year — `[license-pending detail; consult Unity's current terms]`. Unity Pro is required above the threshold. The Unity Editor's license is *not* the same as the runtime — the engine binary embedded in built games has its own redistributable license. Unity has historically *changed pricing models* with little notice (the 2023 Runtime Fee controversy is the canonical recent example, which they partially reversed but which damaged trust). The license posture is *moving ground*, not a stable contract.

Ember's Vow of Open Knowledge requires *transparency about the cord to vendor terms*. Unity is a vendor; the license is a cord; the Vow demands the cord be named, the threat model surfaced, and the operator's consent gathered before commitment. Adopting Unity as Ember's runtime foundation would *bind* Ember to Unity's future-pricing-and-terms decisions in a way that adopting (say) the Apache-2.0-licensed Bevy engine, or the MIT-licensed Three.js, or a custom Rust+wgpu pipeline, would not.

This is *the strongest argument against Unity-as-foundation*. The engine is good. The vendor is unpredictable. The Vow of Open Knowledge is honored more cleanly by an Andlit-unity *sub-name* (which the operator can opt into if they accept Unity's terms) than by Unity-as-foundation (which would impose Unity's terms on every Ember user).

### Ask 5 — Build pipeline complexity

The fifth ask: shipping a Unity project requires *building*, and building requires *the build pipeline*. The Build Settings dialog (which scenes are included, which platforms are targeted), the Player Settings (resolution, scripting backend Mono vs IL2CPP, API compatibility level, target architecture), the asset bundling configuration, the platform-SDK requirements (Xcode for iOS, Android SDK + NDK for Android, Emscripten for WebGL). The build *takes minutes* (a clean WebGL build is 5–10 minutes; an iOS build is 15+ minutes including IL2CPP transpilation). Build failures *frequently happen at the platform-SDK level* — the iOS provisioning profile expired, the Android keystore is missing, the WebGL emscripten version is incompatible with the Unity version.

For Ember, the operational cost is *real*. The Hermes Python codebase ships as `pip install`. The Waifu kit ships as `npm run build`. A Unity build is *materially more operational work*. The Vow of Public-Friendliness pulls against this: the operator who wants to fork Ember and modify it should not have to learn the iOS provisioning system.

### Ask 6 — The hidden-state problem

The sixth ask, which is the subtlest and the most Ember-specific: *Unity scenes have hidden state that does not live in source code*. The prefab files (`*.prefab`), the scene files (`*.unity`), the ScriptableObject assets — these are *YAML files* that Unity reads and writes through the Editor, but the *semantically meaningful state* is the binary-textual graph of GameObjects and Component references. Reading a prefab's diff in a code review is *materially harder* than reading a Python diff.

For Ember's Mythic Engineering practice — which is *documentation-first*, with the Architect drawing diagrams that the Forge implements — the hidden-state problem is significant. The doll-as-companion *is its prefab* (the `AIAvatarVRM.prefab` at `/tmp/ChatdollKit/Extension/VRM/AIAvatarVRM.prefab` *is* the doll, in a meaningful sense; the `.cs` files describe behaviors but the prefab assembles them). The Architect's diagrams would need to *include prefab structure*, which is *a different documentation discipline*.

This is the ask that most demands the Andlit-unity *sub-name* approach: Unity's hidden-state problem is *contained* to the rendering sub-name, where it belongs (rendering is inherently configuration-heavy), rather than *spreading across* Ember's core (which stays Python-and-text-files).

## IV. The ratio — give-to-ask

Six gives. Six asks. The ratio is *tier-dependent and aspiration-dependent*, not absolute.

If Ember's aspiration is *Pi-baseline text-only-now, desktop-text-only-forever*, the ratio is *bad*. Unity gives Ember nothing in this scenario (text-only on the Pi does not benefit from any of the six gives) and asks everything (engine commitment, binary size, learning curve, license cord, build pipeline, hidden state). Ember would be paying for things she does not use.

If Ember's aspiration is *Pi-baseline now, desktop-VRM later, eventually maybe-mobile-or-VR*, the ratio is *complicated*. Unity gives Ember the *eventually-VR* path (Give 4, mobile + XR) but at the cost of an engine commitment Ember does not need *yet*. The right move is to *defer the commitment* — keep the *option* open by naming Andlit-unity as a reserved sub-name, but ship nothing on Unity until the operator's actual desire for mobile/VR materializes.

If Ember's aspiration is *desktop-with-3D-avatar-on-most-machines, multi-platform reach including mobile and VR, ship-quality visual presence*, the ratio is *good*. Unity gives Ember most of what she would need to build to inhabit those tiers; the asks are *appropriate to the aspiration*. Andlit-unity would be a non-trivial sub-name with real engineering investment, but the investment is *paid back* by the multi-platform reach and the asset-ecosystem leverage.

The Skald's reading: **the third aspiration is plausible but not currently ratified, and the second aspiration is the honest current state**. Ember should *reserve* Andlit-unity as a sub-name. Ember should *not yet* commit to Unity as foundation. Ember should *study* ChatdollKit deeply, *adopt* the typed-tag protocol and the modular-provider interfaces (which transfer across engines), and *defer* the Unity-runtime decision to a future operator-ratified slice.

This is what `[[60_synthesis/61_ANDLIT_UNITY_TIER]]` will argue formally. The Vision document's job is to frame the trade-off; the Cartographer's job is to draw the decision matrix.

## V. The three positions, compared

The triangulation from `[[00_OVERTURE §IV]]`:

| Axis | Andlit-electron (SAP) | Andlit-realtime (Waifu) | Andlit-unity (CDK) |
|---|---|---|---|
| Render location | Operator's machine, host OS process | Vendor datacenter GPU | Operator's machine, Unity runtime process |
| Failure mode | OS process crash, VTube Studio disconnect, VMC peer loss | Network loss, vendor billing, vendor revocation | Unity runtime crash, asset bundle corruption, platform SDK incompatibility |
| Hardware floor | T2+ (laptop with GPU) | T-1 onwards (browser + bandwidth) | T1+ (low-end laptop or phone) |
| Mobile support | No | Yes (browser) | Yes (native iOS/Android builds) |
| XR support | No | No | Yes (Unity XR plugins) |
| WebGL support | No (Electron is desktop only) | Yes (it is a browser app) | Yes (WebGL build target) |
| Visual quality ceiling | High (depends on local GPU) | High (vendor GPU) | High (Unity URP) |
| Binary size | 500MB (Electron + Python) | 5MB (React bundle) | 50–200MB (Unity build) |
| License posture | Mixed (MIT for most components, proprietary VTube Studio) | No license (Waifu kit) + MIT (LiveKit) | Apache-2.0 (CDK) + Unity vendor terms |
| Vendor cord | None for SAP itself; VTube Studio is third-party | Vendor-required (ZeroWeight SDK + LiveKit infra) | Unity-license cord (separate from CDK Apache-2.0) |
| Cost model | Free (operator's electricity) | Per-minute billable session | Free (operator's electricity + Unity Personal license) |
| Learning curve | Python + Electron | React + LiveKit | C# + Unity + VRM pipeline |
| Cultural fit with Ember | High (Python-native) | Low (browser-only, vendor-dependent) | Mixed (engine-native but engine-foreign) |

The three positions are *genuinely different*, not minor variants. The Andlit-unity position has *the largest engineering surface to learn* but *the widest platform reach*. The Andlit-electron position has *the smallest engineering surface for Ember's existing Python-native practice* but *the smallest platform reach*. The Andlit-realtime position has *the smallest engineering surface absolutely* but *the largest vendor-trust surface*.

The triangulation is *real and load-bearing*. None of the three subsumes the others. `[[60_synthesis/60_TRIANGULATION]]` will formalize.

## VI. The honest verdict (preliminary)

I will state the verdict the Vision layer offers, knowing the Cartographer's synthesis may revise it.

**Adopt Andlit-unity as a reserved sub-name.** Ember's `src/ember/spark/andlit/` tree gains a `unity/` sub-directory, sibling to `local/` (SAP-pattern, electron) and `realtime/` (Waifu-pattern, cloud-stream). No code ships. The reservation prevents future maintainers from cramming Unity-render concerns into the wrong sub-name.

**Adopt the typed-tag protocol and the modular-provider interfaces** at the *language-independent* level. These transfer to any future Andlit implementation (electron, unity, realtime, terminal-glyph) because they are *protocol shapes*, not engine bindings.

**Defer the Unity-runtime decision** until a future operator ratification. The decision is *real engineering investment* and should not be made implicitly by the Skald's enthusiasm.

**Refuse Unity-as-foundation**. Whatever Ember adopts from Unity stays *within Andlit-unity*. The Ember core remains Python-and-text-files. The Veizla, the Six True Names, Hjarta's first-run rite, Brunnr's pluggable storage — all stay engine-agnostic.

**Adopt the multi-platform-reach lesson at the architectural level**. The lesson is: *embodiment surfaces should not be platform-coupled at the wrong layer*. Andlit's design must allow *multiple rendering implementations*, each platform-specific where necessary, sharing a typed protocol. Whether any specific Andlit implementation uses Unity, Electron, Three.js, or a Pi-tier ASCII glyph is *the operator's tier choice*, not Ember's architectural commitment.

This verdict honors:
- Vow of Smallness (Ember core stays small)
- Vow of Tiered Presence (Andlit-unity is a sub-name, tier-appropriate, opt-in)
- Vow of Modular Authorship (Andlit's three sub-names are individually swappable)
- Vow of Public-Friendliness (terminal-only operators are not asked to install Unity)
- Vow of Open Knowledge (the Unity-license cord is named, not silently inherited)
- Vow of Closed Default (Unity is off by default; opt-in per operator)

## VII. Cross-References

- `[[00_OVERTURE]]` — the Fifth Reading stance.
- `[[01_CDK_ESSENCE]]` — what ChatdollKit wants to be.
- `[[03_ANTI_CDK]]` — the refusals that complicate this trade-off.
- `[[04_VISION_SYNTHESIS]]` — the triangulation closing.
- `[[10_domain/1C_UNITY_LIFECYCLE_DOMAIN]]` — Architect's deep read of Unity-specific lifecycle.
- `[[10_domain/1D_MULTI_PLATFORM_DOMAIN]]` — Architect's deep read of multi-platform deltas.
- `[[50_verification/50_DEPENDENCY_HEALTH]]` — Auditor's read of Unity dependency brittleness.
- `[[60_synthesis/61_ANDLIT_UNITY_TIER]]` — Cartographer's formal decision matrix.
- `[[60_synthesis/62_MOBILE_AND_XR_TIER]]` — Cartographer's mobile/XR tier formalization.
- `[[sap:11_AVATAR_DOMAIN]]` — Wave 3 sibling avatar domain (electron/VTS).
- `[[sap:63_PERFORMANCE_TIER_ENGINE]]` — Wave 3 sibling tier engine.
- `[[waifu:01_VISION_SYNTHESIS]]` — Wave 4 sibling synthesis with Tier-CLOUD parallel axis.

## What This Means for Ember

**Adopt:**
- **The platform-isolation discipline** (`#if UNITY_WEBGL` directives, shadow-class pattern at `*ServiceWebGL.cs`, native plugins under `Plugins/Android/` and `Plugins/iOS/`, Apache-2.0 attribution required). Adopt the *discipline of isolating platform-specific code in clearly-named files behind explicit platform guards*. Whether Ember uses C# `#if` or Python `if sys.platform`, the principle transfers: platform-deltas in clearly-marked locations, never scattered.
- **The asmdef boundary pattern** (`Scripts/ChatdollKit.asmdef`, Apache-2.0). Three external references, autoReferenced=true, version-defined optional dependencies. Adopt as Ember's pattern for *integration boundary declaration* in any language. Python equivalent: each `src/ember/<subsystem>/` has an `__init__.py` with explicit re-exports, a `pyproject.toml` extras-block declaring optional integrations, and zero upward dependencies.

**Adapt:**
- **The reserved-sub-name pattern from Wave 3** (`[[sap:60_TRUE_NAME_REASSIGNMENT §7]]`) applied to Andlit-unity. Ember reserves `src/ember/spark/andlit/unity/` as a path in the tree without shipping code. The reservation is documentation-level: a README in that directory explains why the path exists and what would inhabit it. Adopt the *reservation discipline*; do not adopt Unity code.
- **The "platform support is engine-given, operator-tier-chosen" framing**. The Tier Engine grows a clearer position on platform support: Pi-tier supports text-only, T1-T3 support electron/web-based Andlit-electron and cloud-tier, T1+ on mobile or XR hardware supports Andlit-unity *if the operator opts in to the engine cost*. Adopt the *layered tier-position*; the specific implementations remain the operator's choice.

**Avoid:**
- **Adopting Unity as Ember's foundation runtime**. The asks are too large for Ember's current scope and the gives accrue only when Ember inhabits tiers (mobile, XR) that are not currently in any ratified slice. The Vow of Smallness directly forbids the foundation-level commitment.
- **The hidden-state-in-prefabs pattern as documentation default**. Prefabs are appropriate for Andlit-unity if-and-when that sub-name materializes. Ember core documentation stays text-files-and-Python; the Mythic Engineering practice does not extend to Unity-Inspector-driven configuration as a documentation source of truth.
- **Treating Unity's vendor terms as a non-cord**. Unity is a vendor; its terms are a cord. The Vow of Open Knowledge demands the cord be named. Any future Andlit-unity adoption must include a Cord-Manifest entry for the Unity-license cord, with threat-model surfaced (price changes, runtime-fee precedent, possible-deprecation-of-features).

**Invent:**
- **The Three-Axis Embodiment Reservation Pattern.** Andlit gains three reserved sub-names — `local/` (electron/desktop, SAP-pattern), `realtime/` (cloud-stream, Waifu-pattern), `unity/` (engine-native local, CDK-pattern). Rödd gains the parallel three: `local/`, `realtime/`, `unity/`. The reservations exist as paths in the source tree with README explanations, *without* code. The pattern *makes the embodiment-axis visible in the source tree* even before any of the three is implemented, which prevents future maintainers from mis-homing future engine integrations.
- **The Engine-as-Cord Convention.** Any future Ember integration that requires *a vendor's engine or platform* is recorded in the Cord Manifest as an *engine cord* with declared threat model. Unity, Unreal, Godot, the App Store, Google Play, Quest's store — these are all engine cords. Each must be named before adoption. The cord can be *accepted* (Unity for Andlit-unity if operator opts in) but cannot be *silent*.
- **The "Tier-Multiplied" Decision Matrix.** Adopt-or-refuse decisions about embodiment-axis options are *not* unary. They are multiplied across the existing tier ladder: *Adopt Andlit-unity for T2-T3 if operator opts in; refuse for T0-T1; offer for mobile/XR tiers as the natural fit*. The matrix becomes formal in `[[60_synthesis/61_ANDLIT_UNITY_TIER]]`.

**Vows touched by this Trade-Off:**
- **Vow of Smallness** — *renewed and load-bearing*. The Unity-as-foundation refusal is direct application of the Vow.
- **Vow of Open Knowledge** — *expanded with Engine-as-Cord convention*. Vendor engines are named cords.
- **Vow of Tiered Presence** *(Wave 3 proposed)* — *expanded with three-axis embodiment reservation*. Andlit has three reserved sub-names, paralleled by Rödd.
- **Vow of Modular Authorship** — *exemplified*. ChatdollKit's modular subsystem pattern is the reference quality bar.
- **Vow of Public-Friendliness** — *honored*. The Unity-as-foundation refusal preserves terminal-only operator friendliness.
- **Vow of Closed Default** *(Wave 3 proposed)* — *renewed*. Unity is off by default; opt-in is per-operator.

Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c). The Unity engine itself is *not* under CDK's Apache-2.0 license; the Unity-license cord is separate and must be honored under Unity's own terms.

The customs map is drawn. The next document holds the refusals.

— Sigrún Ljósbrá, the Skald, naming the trade-off honestly

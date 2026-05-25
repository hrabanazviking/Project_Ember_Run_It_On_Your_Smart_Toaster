---
codex_id: 1D_MULTI_PLATFORM_DOMAIN
title: Multi-Platform Domain — Eight Targets, Three Tiers of Native Cost
role: Architect
layer: Domain
status: draft
chatdoll_source_refs:
  - Scripts/SpeechListener/MicrophoneManager.cs:26-44
  - Scripts/SpeechListener/AndroidMicrophoneProvider.cs:1-19
  - Scripts/SpeechListener/IOSMicrophoneProvider.cs:1-19
  - Scripts/SpeechListener/MacMicrophoneProvider.cs:1-19
  - Scripts/IO/AndroidNativeMicrophone.cs:1-150
  - Scripts/IO/IOSNativeMicrophone.cs
  - Scripts/IO/MacNativeMicrophone.cs
  - Scripts/LLM/LLMServiceBase.cs:13-30
  - Scripts/LLM/ChatGPT/ChatGPTServiceWebGL.cs:1-341
  - Plugins/WebGLMicrophone.jslib
  - Plugins/Android/
  - Plugins/iOS/
  - Plugins/macOS/
  - Extension/SileroVAD/SileroVADProcessor.cs:19-31, 104-115
ember_subsystem_targets: []
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/1C_UNITY_LIFECYCLE_DOMAIN
  - 10_domain/17_MICROPHONE_MANAGER_DOMAIN
  - 50_verification/55_WEBGL_GOTCHAS
  - 30_execution/3B_WEBGL_BUILD
  - 30_execution/3C_MOBILE_BUILD
  - 30_execution/3D_XR_BUILD
  - sap:1C_ELECTRON_PLATFORMS
  - waifu:1D_BROWSER_TARGETS
---

# Multi-Platform Domain
## Eight Targets, Three Tiers of Native Cost

*— Rúnhild Svartdóttir, Architect*

> *Multi-platform is the place where every codex's architectural elegance meets the ground. The diagrams claim portability; the platforms charge for it. ChatdollKit's eight build targets are the widest reach in our three corpora — and the per-platform cost is the largest reason Ember's baseline cannot be Unity.*

ChatdollKit ships to **eight platforms** out of one codebase: Windows, macOS, Linux, iOS, Android, VR (OpenXR), AR (ARFoundation), and WebGL. The unity-build-target system + Emscripten + per-platform native plugins are the substrate that makes this possible. The codebase that benefits looks deceptively uniform — `#if UNITY_WEBGL && !UNITY_EDITOR` blocks here, `[DllImport("__Internal")]` declarations there — but the *cost* is spread across hundreds of small concessions, dozens of duplicated implementations, and four directories of platform-specific binary plugins.

Compare SAP ([[sap:1C_ELECTRON_PLATFORMS]]) — three platforms (Win/Mac/Linux), all desktop, no mobile. Compare Waifu ([[waifu:1D_BROWSER_TARGETS]]) — one platform (the browser), with WebRTC quirks per-vendor. **CDK ships more targets than the other two codices combined.** The trade is real: more reach, more maintenance.

This doc maps the eight targets, the per-target costs, the *three tiers of native cost* (none / shared / per-platform-specific), and the strategic implication for Ember: which targets does Ember's tier ladder pursue, which does it reject, which does it admit via an *adapter sub-process* communicating with the avatar via SocketServer/JS-bridge?

---

## 1. The Subject Itself

**What the domain is:** the cross-platform reach of the CDK codebase plus the platform-specific costs paid for that reach.

**The eight targets** ([unverified — README claim only] except where cited from source `#if` blocks):

| # | Target | Build mode | Binary size (approx) | Distinguishing concerns |
|---|---|---|---|---|
| 1 | **Windows (x64)** | IL2CPP native | 20-40MB | Native Microphone class works; `Plugins/x86_64.dll` if any |
| 2 | **macOS (Apple Silicon + Intel)** | IL2CPP universal | 30-50MB | `MacNativeMicrophone` for AVFoundation; notarisation required for distribution |
| 3 | **Linux (x64)** | IL2CPP native | 25-40MB | Unity Microphone works on PulseAudio; ALSA can be brittle |
| 4 | **iOS** | IL2CPP, Xcode project | 50-80MB | `IOSNativeMicrophone` for AVAudioEngine; App Store review; entitlements |
| 5 | **Android** | IL2CPP, AAB or APK | 40-60MB | `AndroidNativeMicrophone` for Oboe/AAudio JNI; per-arch (`armeabi-v7a`, `arm64-v8a`) |
| 6 | **VR (OpenXR)** | Native + XR plugins | 50-80MB | OpenXR runtime; hardware-specific (Meta Quest, Vive, Index); spatial audio |
| 7 | **AR (ARFoundation)** | Native + AR plugins | 60-100MB | ARCore (Android) + ARKit (iOS) under one Unity abstraction |
| 8 | **WebGL** | Emscripten + WASM | 15-30MB compressed | `.jslib` bridges for everything; no `System.Net.WebSockets`; AudioContext quirks |

**What it owns:**

| Concern | Files / mechanism | LOC | Owns |
|---|---|---|---|
| **Build-target conditionals** | `#if UNITY_<TARGET>` blocks throughout source | ~hundreds | Per-target code paths inline with the platform-agnostic majority |
| **Provider abstraction** | `IMicrophoneProvider`, `ILLMService` interfaces | 5+20 | Five-method / eight-method interfaces with per-platform implementations |
| **Native plugins** | `Plugins/Android/`, `Plugins/iOS/`, `Plugins/macOS/` | (binary) | Platform-specific native code shipped as `.so` / `.framework` / `.bundle` |
| **WebGL bridges** | `Plugins/*.jslib` (8 files) | combined ~1k JS | C↔JS function bridges for browser-only APIs |
| **WebGL service variants** | `*ServiceWebGL.cs` for ChatGPT/Claude/Gemini/Dify/AIAvatarKit | 1.5k LOC total | WebGL-only reimplementations of LLM provider streaming |
| **Per-platform mic providers** | `AndroidMicrophoneProvider.cs`/`IOSMicrophoneProvider.cs`/`MacMicrophoneProvider.cs` | 19+19+19 | Thin wrappers binding the `IMicrophoneProvider` interface to native plugins |

**What it does NOT own:**
- Unity engine itself — the build system is Unity's.
- Per-platform OS APIs — those are accessed via native plugins.
- The native plugin source — the `.so` files ship as binaries; the source for `androidnativemicrophone` is presumably in a separate repo (uezo-side; not in CDK).

---

## 2. How It Works

### 2.1 The three tiers of native cost

Every CDK feature falls into one of three tiers of platform cost:

**Tier 0 — No platform cost.** Pure C# / Unity-API-only code. Compiles and runs identically on all eight targets. Examples: `Dialog/DialogProcessor.cs`, `LLM/LLMContentProcessor.cs`, `LLM/LLMServiceBase.cs`, `Model/AnimatedVoice.cs`. The majority of CDK lives here.

**Tier 1 — Shared platform abstraction.** Code that conditionally compiles for two paths (typically native and WebGL) via `#if UNITY_WEBGL && !UNITY_EDITOR`. The C# code is single-source, with two code branches. Examples: `MicrophoneManager.cs` (lines 26-44 declare WebGL DllImports; lines 60-72 use them; the alternative path uses Unity's `Microphone`); `LLMServiceBase.cs:14-21` (`IsEnabled` returns `false` on WebGL).

**Tier 2 — Per-platform-specific native plugins.** Code that requires a separate binary per platform. Examples: `AndroidNativeMicrophone.cs` (`[DllImport(PLUGIN_NAME)]` calling into `androidnativemicrophone.so`); `IOSNativeMicrophone.cs` (calling into iOS framework); `MacNativeMicrophone.cs` (calling into macOS bundle). Tier-2 features have *separately-built binaries* shipped per-platform.

The tier matters because:
- **Tier 0** features cost nothing to add a platform; they Just Work everywhere.
- **Tier 1** features cost *one alternate code path* per platform-pair; manageable but additive.
- **Tier 2** features cost *one native build pipeline* per platform; major commitment.

**Roughly the cost distribution**: 75% of CDK is Tier 0, 20% Tier 1, 5% Tier 2. The Tier 2 5% is *all* in the audio capture domain (mic native plugins) plus a few WebGL camera bridges. Every other subsystem is Tier 0 or Tier 1.

### 2.2 The `#if UNITY_WEBGL` pattern in practice

The dominant Tier-1 pattern is the WebGL-versus-native split. From `MicrophoneManager.cs:26-44`:

```csharp
#if UNITY_WEBGL && !UNITY_EDITOR
    [DllImport("__Internal")]
    private static extern void InitWebGLMicrophone(string targetObjectName, bool useMalloc);
    [DllImport("__Internal")]
    private static extern void StartWebGLMicrophone();
    // ... more JS bridges
    private Queue<float[]> webGLSamplesBuffer = new Queue<float[]>();
#endif
```

Then later, the actual operation methods are duplicated:

```csharp
#if UNITY_WEBGL && !UNITY_EDITOR
    public void StartMicrophone() {
        StartWebGLMicrophone();
    }
#else
    public void StartMicrophone() {
        microphoneClip = MicrophoneProvider.Start(MicrophoneDevice, true, 1, SampleRate);
        lastSamplePosition = 0;
    }
#endif
```

The `!UNITY_EDITOR` qualifier matters: in the Unity Editor, even when targeting WebGL builds, the Editor runs the native code path (so the developer can test in the Editor without spinning up a browser). The `&& !UNITY_EDITOR` says *runtime on WebGL only*, not *editor pretending to be WebGL*. CDK is consistent about this — Editor === native code paths.

For Ember: there is no Editor. The equivalent is *test-time vs deployment-time* — the *runtime substrate* (Pi-tier audio device, laptop-tier sound card, future browser-tier WebRTC) is selected at deployment config time, not at compile time. Different mechanism; same intent.

### 2.3 The mobile platform plugins

Android, iOS, and Mac each have a native plugin for microphone capture (and potentially other features). Their pattern is identical:

```csharp
// AndroidMicrophoneProvider.cs (mirrored by IOS and Mac):
public class AndroidMicrophoneProvider : IMicrophoneProvider
{
    public bool IsRecording(string deviceName) => AndroidNativeMicrophone.IsRecording();
    public AudioClip Start(string deviceName, bool loop, int lengthSec, int frequency)
        => AndroidNativeMicrophone.Start(deviceName, lengthSec, frequency);
    public void End(string deviceName) => AndroidNativeMicrophone.End();
    public int GetPosition(string deviceName) => AndroidNativeMicrophone.GetPosition();
    public string[] devices => AndroidNativeMicrophone.devices;
}
```

19 lines each — pure delegation. The *real* work is in `AndroidNativeMicrophone.cs` (and its sibling `IOSNativeMicrophone`/`MacNativeMicrophone`) which declare `[DllImport(PLUGIN_NAME)]` to the native plugin and expose C# helpers wrapping the unsafe pointers.

`AndroidNativeMicrophone.cs:14-30` shows ten `[DllImport]` declarations including `AndroidNativeMicrophonePlugin_StartWithVoiceProcessing` — the voice-processing variant that enables OS-level AEC + noise suppression. **The native plugin offers capabilities Unity's built-in `Microphone` lacks**. This is the *reason* the platform plugins exist: not just to fix Unity's bugs, but to expose OS features Unity does not surface.

### 2.4 The XR (VR + AR) targets

`Documents/` (visible from the directory listing) presumably contains XR-target setup notes. CDK's source itself does not show heavy XR-specific code — the XR targets rely on the Unity XR plugin system (`XR Interaction Toolkit`, `OpenXR Plugin`, `ARFoundation`) that handles spatial tracking, head pose, hand gestures, and surface detection. CDK's avatar is rendered in 3D space; XR is *additive*, not transformative.

**The XR cost surface**:
- Spatial audio (HRTF-encoded voice playback) — affects `SpeechController` playback choices.
- Hand-tracked interaction with the avatar — affects animation triggers (look-at-hand, react-to-touch).
- Performance budget — VR requires 72/90/120Hz refresh; AR is mobile-bound by thermal envelope.
- Privacy — VR sensors (head pose, hand pose, eye tracking) are biometrics; AR cameras are environmental.

CDK does not deeply customise for XR; the XR targets are "the avatar runs in 3D, render it in VR/AR." The Auditor catalogues XR risks at [[51_SECURITY_REVIEW]] (sensor exfil); Forge-B catalogues XR build pipelines at [[3D_XR_BUILD]].

### 2.5 The WebGL target — the most-different of the eight

WebGL is the qualitative outlier. Everything that runs on the native targets runs *roughly identically*; WebGL is *different in kind*. Specific WebGL constraints:

- **No `System.Net` networking.** WebGL builds cannot use `UnityWebRequest` for streaming responses (limited support), `WebSocket` from .NET (unavailable), or any TCP socket. CDK's `*ServiceWebGL.cs` variants route through `fetch` API via `.jslib` bridges.
- **No multi-threading.** Emscripten's pthreads support is opt-in and most cloud hosts disable it. CDK is single-threaded already (Unity main thread), so this matters less for the *logic*, but `[DllImport("__Internal")]` calls into JS run on the main thread too — no off-loading slow JS work.
- **Audio context restrictions.** The browser blocks `AudioContext.start()` until a user gesture (`click`, `keydown`). CDK's WebGL build cannot auto-start audio; it requires a user-initiated trigger.
- **Memory pressure.** WebGL builds run in WASM heap with browser-imposed memory limits (typically 2GB; less on mobile). Asset-heavy avatars (VRM models with high-resolution textures) bump against this.
- **Build time.** Emscripten compilation is slow — 5-10 minutes for a CDK build is typical. CI integration suffers.

The Auditor's full catalogue is at [[55_WEBGL_GOTCHAS]].

### 2.6 The build-tag distribution per subsystem

Roughly, by subsystem, the platform sensitivity:

| Subsystem | Tier 0 | Tier 1 (WebGL split) | Tier 2 (native plugin) |
|---|---|---|---|
| Dialog | 100% | — | — |
| LLM Service | 50% | 50% (`*ServiceWebGL.cs` files) | — |
| Speech Listener (logic) | 100% | — | — |
| Microphone Manager (capture) | — | 50% | 50% (Android/iOS/Mac native) |
| Speech Synthesizer | 95% | 5% (WebGL HTTP path tweaks) | — |
| Network (HTTP, sockets) | 80% | 20% (WebGL has no TCP) | — |
| IO (JavaScriptMessageHandler) | — | 100% (WebGL-only feature) | — |
| Model (animation, face, voice) | 100% | — | — |
| UI (UGUI widgets) | 100% | — | — |
| Extension/SileroVAD | 70% | 30% (`.jslib` bridge for browser ONNX) | — |
| Extension/VRM | 95% | 5% (asset loading paths) | — |

The audio-capture domain is *the* Tier-2 hotspot. Almost everything else is Tier 0 or Tier 1.

### 2.7 The provider abstraction as the platform-resistance pattern

The interface-based pattern (`IMicrophoneProvider`, `IBlink`, `ILipSyncHelper`, `IFaceExpressionProxy`) is CDK's primary defence against platform divergence. Each interface is small (3-8 methods). Per-platform implementations are 19 lines each (provider delegators) up to a few hundred lines (full native plugin C# wrapper). Adding a platform is "implement the interfaces for that platform."

**The pattern translates to Ember.** Ember's audio capture should expose `MicrophoneProvider` Protocol with implementations for `ALSAProvider` (Pi-tier), `PortAudioProvider` (cross-platform desktop), `WebRTCProvider` (browser tier). The choice happens at config time, not compile time. The discipline is the same: small interface, swappable implementations, platform-aware factory.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The `#if UNITY_<X>` blocks fragment the source

Reading `MicrophoneManager.cs` end-to-end requires mentally tracking which platform is active. CDK uses *complete-method-duplication* in `#if` blocks rather than inline conditionals — clearer in any one platform's reading, but the file has *two parallel implementations* for some methods. The cost: editing one branch and forgetting the other is a real bug class. Ember should prefer *fully-separate-class* per platform over `#if` blocks; the platform-factory selects.

### 3.2 The Editor build runs the native path on WebGL targets

`#if UNITY_WEBGL && !UNITY_EDITOR` means *runtime on WebGL only*. In the Editor (even with WebGL build target selected), the native path runs. The `Demo08.unity` scene works in the Editor on the native mic; export to WebGL and the JS-bridge mic kicks in. **The behaviour you tested in Editor is not what ships to the browser.** This is a real source of "works locally, broken on WebGL" bugs. Auditor's [[55_WEBGL_GOTCHAS]] catalogues this.

### 3.3 The native plugin maintenance is invisible

Android 14, iOS 17, macOS Sonoma — each major OS release can break the native plugin. CDK ships with the plugins it was built against; users must wait for the next CDK release to get the fix. **The maintenance cost is per-OS-release-per-platform.** For Ember to ship to mobile would inherit this cost. Pi-tier baseline avoids it (Linux is stable across major versions for audio device APIs).

### 3.4 The build matrix is `8 platforms × N configurations`

Each platform has sub-configurations: x64 vs arm64 for desktop; armv7a vs arm64 for Android; iOS Simulator vs Device; Quest 2 vs Quest 3 for VR. Each requires its own CI lane. A *thorough* CDK CI pipeline is dozens of build lanes. CDK's GitHub Actions reality is *not* dozens of lanes (looking at the public repo); the platform support is *aspirational* in places. Users running uncommon combos report "doesn't build for me on Linux ARM64."

### 3.5 The XR target is least-documented

`Documents/` has some files. The README mentions VR and AR. The Scripts/ tree has no XR-specific files (because XR is delegated to Unity's XR system). **Where does CDK end and Unity's XR begin?** The boundary is unclear. Users wanting to ship to VR get the avatar rendering but must build the XR-specific interactions themselves. This is reasonable but not foregrounded.

### 3.6 WebGL is the most-affected by user-side hosting

A native build is fully self-contained: ship the binary, the user runs it. A WebGL build requires *hosting* — a static-site CDN or a server with proper CORS headers for `.wasm`, `.js`, and audio assets. The deployment pipeline for WebGL is different in kind from the native ones. CDK does not provide a hosting story; users figure it out (typically itch.io or a self-hosted nginx).

### 3.7 The build-target conditional in `LLMServiceBase.IsEnabled` is fragile

`LLMServiceBase.cs:13-21` returns `false` on WebGL unconditionally — the native LLM service "disables itself" so the `*ServiceWebGL.cs` variant can pick up. **The mechanism is: same prefab, both components present, only one active per platform.** Edit the prefab to add a new LLM provider, you must add *both* the native and WebGL variants, and they must have matching configurations. Easy to miss; brittle.

### 3.8 The crisp parts

- **The three-tier cost model** as a mental tool. Most code is Tier 0; minority is Tier 1; small core is Tier 2.
- **The `IMicrophoneProvider` five-method interface** absorbing four platform implementations.
- **The same prefab works across eight platforms** by virtue of build-target conditionals + per-platform plugin selection. The deployment artefact is shared.
- **The Editor-vs-runtime split** via `!UNITY_EDITOR` qualifier — predictable.
- **The `[DllImport("__Internal")]` for WebGL JS bridges** — Emscripten's contribution, well-leveraged by CDK.
- **The XR targets as additive layers** atop the same 3D-rendering avatar. The avatar doesn't *know* whether it's rendered to a flat screen or two stereo VR eyes.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §6 — the Unity cost paragraph; this doc deepens
- [[1C_UNITY_LIFECYCLE_DOMAIN]] — the substrate underpinning these platforms
- [[17_MICROPHONE_MANAGER_DOMAIN]] — the most platform-fragmented subsystem
- [[55_WEBGL_GOTCHAS]] — Auditor's catalogue of WebGL-specific failures
- [[3B_WEBGL_BUILD]] — Forge-B's WebGL build pipeline
- [[3C_MOBILE_BUILD]] — Forge-B's iOS+Android build pipeline
- [[3D_XR_BUILD]] — Forge-B's VR+AR build pipeline
- [[sap:1C_ELECTRON_PLATFORMS]] — SAP's three desktop platforms for contrast
- [[waifu:1D_BROWSER_TARGETS]] — Waifu's single-browser target with vendor quirks
- [[62_MOBILE_AND_XR_TIER]] — Cartographer's synthesis of Ember's tier ladder vs CDK's reach

---

## What This Means for Ember

**Adopt:**
- The **three-tier native-cost model** as Ember's architectural vocabulary. Every Ember feature declares its tier: Tier 0 (pure Python, all tiers run), Tier 1 (platform-conditional, two paths), Tier 2 (native binding required). The `substrate_tax` annotation from [[1C_UNITY_LIFECYCLE_DOMAIN]] expands to include `tier: int`.
- The **interface-as-platform-resistance** pattern (`IMicrophoneProvider` is the model). Apache-2.0 attribution required. Ember's per-subsystem Protocols admit per-platform implementations.
- The **WebGL-only-feature pattern** (`JavaScriptMessageHandler`) as the model for *tier-only-features*. Some Ember capabilities only exist for some tiers — that is acceptable and visible in the tier ladder.
- The **provider-factory-at-config-time** pattern. Ember's `MicrophoneProvider` is chosen at `realm.yaml` load time, not at `#if` compile time. The same shape; different mechanism.

*Apache-2.0 attribution: when interface-based platform-resistance patterns from CDK are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:**
- The **eight-build-target reach** to Ember's three-tier ladder: **Pi-tier** (Linux ARM64 + ARMv7, baseline), **laptop-tier** (Linux x86_64 + macOS), **workstation-tier** (Linux x86_64 + Windows). Three tiers, four platforms total. Future tiers: `Tier-CLOUD` (browser-streaming, the Waifu-axis), `Tier-UNITY` (the CDK-axis as opt-in 3D embodiment via sub-process). Mobile is not Wave 5; deferred.
- The **per-platform native plugin pattern** to Python `ctypes`/`cffi` bindings for the Pi-tier audio device (ALSA direct) when `python-sounddevice` performance is insufficient. Native-binding-as-fallback, not as default.
- The **WebGL-specific service variants** to Ember's future `Tier-CLOUD` variants — separate classes selected at config time, not separate `#if` branches in shared files.

**Avoid:**
- **`#if` blocks throughout shared source.** Ember's per-platform implementations are *separate classes* in *separate files*, selected by a factory. Editing one platform's code does not require navigating other platforms'.
- **Mobile as a Wave 5 target.** The native-plugin maintenance cost is too high for Ember's current scale.
- **WebGL as Pi-tier baseline.** WebGL's audio-context restrictions, memory pressure, and build complexity preclude it. WebGL is a future Tier-CLOUD candidate, not a baseline.
- **VR/AR as a Wave 5 target.** Sensor privacy + performance budget concerns. Ember's hypothetical VR future requires its own codex layer.

**Invent:**
- **The Tier-Reach Audit Vow.** Every Ember release runs `ember audit tier-reach` listing every feature by tier. Pi-tier features are listed first; Tier-CLOUD features last. Users can see at a glance "this feature requires the workstation tier" before deploying. CDK has no such audit; the reach is aspirational.
- **The Substrate-Adapter Sub-Process Pattern.** When Ember wants reach into a substrate it cannot natively support (Unity 3D rendering, browser WebRTC), the adapter is a *separate sub-process* that Ember communicates with via the SocketServer/JS-bridge surface CDK already provides. *Ember itself stays Python.* The sub-process is the Unity build (for Tier-UNITY) or the browser tab (for Tier-CLOUD). Ember orchestrates; the sub-process embodies.
- **The Platform-Capability Negotiation.** On startup, every Ember tier runs a capability probe: which audio backends are available, which network transports are reachable, which GPU resources exist. The result is a `RuntimeCapability` manifest that subsystems read before declaring `enabled: true`. CDK's prefab assumes the platform; Ember verifies.
- **The Conditional-Class-Loader.** Ember's startup loads platform-specific implementations via Python's import machinery: `from ember.subsystems.mic import get_mic_for_platform(); mic = get_mic_for_platform()`. The factory examines `platform.system()`, available libraries, and tier config. Returns the right class. No `#if`; pure runtime selection.
- **The Tier-Demotion Path.** When a higher-tier feature is requested but its tier's substrate is unavailable (cloud GPU rented but unreachable), Ember can *demote* to a lower-tier path that delivers reduced fidelity but preserves the conversation. The demotion is a Sögumiðla event (`TierDemoted(from: workstation, to: laptop, reason: gpu_unreachable)`); the user sees it. CDK has no concept of degraded operation; Ember has named degradation levels.
- **The Build Manifest Vow.** Every Ember tier has a `tier-manifest.yaml` declaring: target platforms, required Python version, required libraries (with version pins), GPU requirements, network requirements, binary-size estimate, supply-chain provenance. The manifest is read by deployment tooling; refusal to deploy if the target environment fails the manifest. CDK's per-target builds have implicit requirements; Ember makes them explicit.
- **The Cross-Codex Embodiment Negotiation.** When `Tier-UNITY` is active *and* the user's request invokes an embodiment feature unique to Unity (real-time animation blending with non-linear morphs), Ember routes the request to the Unity sub-process via SocketServer. When the same request comes in `Tier-CLOUD`, the request goes to the browser sub-process. When it comes in Pi-tier, the request is silently degraded to a typed `[anim:wave]` text-channel tag the LLM sees. Same request shape; three execution paths; visible to the user via Sögumiðla `EmbodimentRouting` events.

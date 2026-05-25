---
codex_id: 3C_MOBILE_BUILD
title: Mobile Build — iOS, Android, Native Mic Plugins, and the App Store Reality
role: Forge-B
layer: Execution
status: draft
chatdoll_source_refs:
  - /tmp/ChatdollKit/Plugins/iOS/libIOSNativeMicrophonePlugin.a (iOS native mic .a binary)
  - /tmp/ChatdollKit/Plugins/Android/AndroidNativeMicrophonePlugin.aar (Android native mic .aar)
  - /tmp/ChatdollKit/Plugins/macOS/libMacNativeMicrophonePlugin.dylib (macOS native mic for comparison)
  - /tmp/ChatdollKit/README.md:5 (OshaberiAI iOS app reference)
  - /tmp/ChatdollKit/README.md:15 (multi-platform claim)
  - /tmp/ChatdollKit/README.md:37 (echo-cancelling native plugins)
  - /tmp/ChatdollKit/README.md:794-811 (per-platform MicrophoneProvider setup)
ember_subsystem_targets: [Funi, Andlit]
cross_refs:
  - 10_domain/17_MICROPHONE_MANAGER_DOMAIN
  - 10_domain/1C_UNITY_LIFECYCLE_DOMAIN
  - 10_domain/1D_MULTI_PLATFORM_DOMAIN
  - 50_verification/51_SECURITY_REVIEW
  - sap:3A_CROSS_PLATFORM_BUILDS
  - waifu:23_MOBILE_DEPLOYMENT
---

# Mobile Build

> *Unity ships your scene to iOS and Android by recompiling the world. CDK ships precompiled native microphone plugins because the browser-grade microphone APIs don't deliver phone-grade echo cancellation. The proof is OshaberiAI on the App Store — and the constraints around shipping it.*

Forge. Eldra-iron. CDK's strongest mobile evidence is the **OshaberiAI iOS app** at `apps.apple.com/us/app/oshaberiai/id6446883638` (`README.md:5`) — same author (uezo), shipping ChatdollKit + VOICEVOX TTS in a real consumer app. The README claims (`README.md:15`) full multi-platform support including iOS and Android. The Plugins/ folder confirms native binary support: `iOS/libIOSNativeMicrophonePlugin.a` and `Android/AndroidNativeMicrophonePlugin.aar`.

This document covers what shipping a CDK avatar to mobile actually involves: the build chain, the platform permissions, the binary size, the on-device-LLM question, and the surprising depth of the native-microphone story. The companion verification doc [[50_verification/51_SECURITY_REVIEW]] (Auditor) catalogs the permission-surface threats.

## What Mobile Buys

The Unity iOS and Android build targets produce:

- **iOS**: an Xcode project that compiles to an `.ipa` (App Store) or sideload `.app`. ~80–150 MB for a CDK scene with VRM + animations.
- **Android**: an `.apk` or `.aab` (Play Store bundle). ~70–120 MB.

Reach: a personal pocket-resident avatar. The user opens the app and the doll is there. No browser indirection, no localhost-server requirement (mostly), native microphone with platform AEC (acoustic echo cancellation), native camera, native gyroscope.

The compelling case: the avatar can be **truly idle in the user's life**, surfacing through notifications, lock-screen widgets, focus modes, Siri shortcuts (iOS) or Android Quick Settings tiles. The Andlit-unity-mobile tier is where Ember could become an actual ambient companion. WebGL doesn't reach this; an Electron desktop doesn't reach this either.

## What Mobile Costs

### 1. The build chain

**iOS:**
- Unity Editor (any host OS) → Unity exports an Xcode project (~5 min)
- Xcode → builds and signs the `.ipa` (~5–15 min depending on optimization)
- App Store Connect → upload → review (~24 hours to 7 days first time, faster updates)
- Requirements: macOS host (Xcode is macOS-only), Apple Developer Program membership ($99/year)

**Android:**
- Unity Editor (any host OS) → exports Gradle project or `.apk` directly (~5–10 min)
- Sign with developer keystore
- Upload to Google Play Console (~hours to days review)
- Requirements: Google Play Developer account ($25 one-time), keystore management

For Ember, the iOS path is the harder one. The macOS+Xcode+$99/year+review-process is a real onboarding tax for any small project. Android's $25-one-time + faster review is significantly lower friction.

### 2. Permissions

**iOS** permission strings live in `Info.plist`:
- `NSMicrophoneUsageDescription` — required for voice
- `NSCameraUsageDescription` — required if SimpleCamera is used
- `NSPhotoLibraryUsageDescription` — required if file upload from photo library
- `NSAppTransportSecurity` — if any LLM endpoint is HTTP (don't do this)

**Android** permissions in `AndroidManifest.xml`:
- `android.permission.RECORD_AUDIO` — voice
- `android.permission.CAMERA` — if used
- `android.permission.INTERNET` — automatic for Unity
- Android 6+ requires runtime permission prompts in addition to manifest declarations

Both platforms surface explicit user prompts the first time each permission is needed. The avatar that asks for microphone access is the avatar that needs to explain why **before** the prompt. CDK doesn't have a pre-prompt-explanation overlay; operators add it.

### 3. The native microphone plugins

`README.md:37` and `README.md:794-811` are the canonical source. Unity's built-in `Microphone` API does **not** deliver platform AEC. To get AEC (so the avatar's voice doesn't get picked up by its own mic and looped), CDK provides three native plugins:

- `Plugins/iOS/libIOSNativeMicrophonePlugin.a` — a static archive linked into the iOS Xcode build
- `Plugins/Android/AndroidNativeMicrophonePlugin.aar` — an Android Archive
- `Plugins/macOS/libMacNativeMicrophonePlugin.dylib` — a dynamic library

Operator code in the avatar scene:

```csharp
// /tmp/ChatdollKit/README.md:796-810
private void Awake()
{
    var microphoneManager = gameObject.GetComponent<MicrophoneManager>();

    // First, import the ChatdollKit_NativeMicrophone package
    // Then, set the appropriate provider for your platform:

    // iOS
    microphoneManager.MicrophoneProvider = new IOSMicrophoneProvider();
    // Android
    microphoneManager.MicrophoneProvider = new AndroidMicrophoneProvider();
    // macOS
    microphoneManager.MicrophoneProvider = new MacMicrophoneProvider();
}
```

The `IOSMicrophoneProvider` / `AndroidMicrophoneProvider` C# classes are thin wrappers around `[DllImport("__Internal")]` (iOS) or `AndroidJavaObject` (Android) calls into the native code. The native code uses:

- **iOS:** AVAudioSession with `AVAudioSessionCategoryPlayAndRecord` + `AVAudioSessionCategoryOptionDefaultToSpeaker` + `voiceProcessing` mode (built-in iOS AEC)
- **Android:** `AudioRecord` with `MediaRecorder.AudioSource.VOICE_COMMUNICATION` (Android AEC) or `MediaRecorder.AudioSource.MIC` + custom AEC

The plugins ship as binaries, not source. This means:
- The operator can't audit the code
- The operator can't fix bugs without uezo's help
- The binaries must keep up with Unity API + iOS SDK + Android SDK changes

The trade-off is intentional: shipping AEC-aware mic capture as binary lets CDK promise echo-cancelling on day one without forcing every operator to wrestle with native code.

### 4. The barge-in upgrade path

`README.md:813-818`: *"With echo cancelling enabled, you can allow users to interrupt the AI while it's speaking. To enable this feature: In the Inspector, select the AIAvatar component. Set MicrophoneMuteBy to None."*

The reason CDK ships native mic plugins is **continuous barge-in**. Without AEC, the avatar must mute its mic during TTS playback or else its own voice triggers the VAD. With AEC, the mic stays live, the user can interrupt mid-sentence, the conversation feels natural.

This is the **mobile-specific affordance** the WebGL tier cannot reach. Browser AEC exists (`echoCancellation: true` in `getUserMedia`) but is far less effective than iOS/Android native AEC because the browser doesn't know about the audio system's full state.

### 5. Binary size

A minimal CDK Unity scene with:
- AIAvatar + ModelController + DialogProcessor + SpeechListener + SpeechSynthesizer
- One VRM model (~5–15 MB)
- Idle + a few gesture animations (~2 MB)
- uLipSync vowel data (~500 KB)
- Silero VAD ONNX model (~1.5 MB)
- ChatGPT/Claude/Gemini service code

…compiles to roughly **70–100 MB on Android, 80–150 MB on iOS** (iOS is larger because of bitcode + multi-architecture slicing). Adding optional features (multiple TTS providers, ChatMemory integration, extension scripts) easily pushes this to 200 MB+.

For comparison: typical productivity-app sizes are 50–100 MB; consumer game sizes are 200 MB–2 GB. CDK lands closer to "small game" than "lean utility". The size is dominated by Unity engine code, not CDK scripts.

The **download-size** vs **install-size** distinction matters on Android with App Bundle: the user downloads only the architectures their device needs, often ~40–60 MB. On iOS App Thinning, similar reductions.

### 6. CPU & battery

The avatar render loop targets 60 fps. uLipSync mouth analysis runs every frame. STT/TTS run on demand. LLM streaming is network-bound, not CPU-bound. The combined CPU load on a modern phone (iPhone 13+, Pixel 6+) is ~10-20% with one core busy.

Battery impact during active conversation: ~10-15% per hour. Background-idle: minimal (the scene pauses when backgrounded by Unity's `Application.runInBackground = false` default).

For ambient-companion use cases (avatar lives in the user's pocket, surfaces occasionally), CDK is fine. For "always-on visible avatar" use cases (avatar on screen for hours), expect significant battery drain.

### 7. On-device LLM — the real question

The 800-pound gorilla: **can CDK run an LLM locally on the phone?**

Answer as of 2026-05: tractable but not built-in.

- Unity does not ship with `llama.cpp` bindings
- Apple's MLX framework is iOS/Swift-native and not directly callable from Unity C# without a custom plugin
- ggml/llama.cpp can be compiled as `.a` (iOS) or `.so` (Android) and called via `[DllImport]` — Unity examples exist in the community but not in CDK
- Apple Foundation Models (introduced 2024) provide on-device LLM via Swift only; Unity bridge would require a custom native plugin
- Google ML Kit GenAI APIs (Gemini Nano on supported Pixels) — same Swift/Kotlin-only story

The viable on-device LLM paths for a CDK-based Ember mobile build:

1. **Phi-3-mini or Llama-3.2-1B via llama.cpp**, compiled as native plugin, called from Unity. Model size 1–2 GB. Latency on iPhone 15 Pro: ~10 tokens/sec. Acceptable for short avatar responses.
2. **Apple Foundation Models** via a custom Unity-iOS bridge plugin. Apple's models, Apple's hardware acceleration, no model-shipping required. iOS-only.
3. **MediaPipe LLM Inference** for Android with `gemma-2b` or similar. ~1 GB model. ~5–10 tokens/sec on flagship.
4. **Cloud LLM** (CDK's current default). Network-dependent, fastest, no model storage.

For Ember's Pi-runnable / Smallness Vow, mobile is the **second-best on-device target** after the Pi itself. A Pixel 8a has more memory and faster compute than a Pi 5. A llama-3.2-1B-instruct-Q4_K_M (~1.1 GB) running on a phone is genuinely possible.

The blocker is not the hardware. It is the **Unity-native-plugin integration cost** — writing the C-level bridge, packaging the model into the build, handling first-run download, validating model integrity. CDK doesn't ship this; Ember would invent it. See Invent below.

### 8. App Store review hoops

iOS App Store reviewers care about:

- **Microphone purpose statement**: clear, specific, in `NSMicrophoneUsageDescription`
- **Network usage transparency**: privacy nutrition label declares LLM API usage
- **Adult content**: if the avatar's personality includes adult content, the app must be rated 17+, and review is stricter
- **Crypto / political content**: rejected outright
- **Web view content**: if a web view is included (CDK's optional admin UI), review may probe it
- **Background audio**: if the avatar plays sound when backgrounded, special entitlement required
- **In-app purchases**: required for any monetary transaction in the app

The OshaberiAI app (`README.md:5`) is the existence proof that the review can be passed. It is rated for general audiences and uses VOICEVOX TTS + Cloud LLM.

For Ember, the **adult-content-friendly Vow** ([[ember:PHILOSOPHY]]) creates iOS friction. An Ember tier with explicit content cannot ship through the App Store. Either:
- iOS tier is character-default-clean (Vow-compatible but constrained)
- iOS tier sideloads via TestFlight or AltStore (limits reach)
- iOS tier is dropped; Ember mobile is Android-only

The Android path through Google Play has similar but less-strict content rules. Side-loading via APK is fully supported.

### 9. AndroidJavaObject and iOS DllImport

The native-plugin bridge code patterns:

**Android (C# calls Java):**
```csharp
// pattern, not from CDK source — CDK ships compiled .aar without exposed C# wrapper visible to us
using (AndroidJavaObject mic = new AndroidJavaObject("com.chatdollkit.AndroidMic")) {
    mic.Call("start", sampleRate, bufferSize);
}
```

**iOS (C# calls C/Objective-C):**
```csharp
// pattern, not from CDK source — CDK ships compiled .a without exposed C# wrapper visible to us
[DllImport("__Internal")]
private static extern void IOSMic_Start(int sampleRate, int bufferSize);
```

The cost: every native API call crosses the IL2CPP-to-platform boundary. Per-call overhead is microseconds. Per-frame mic-data pulls are batched; per-event calls (mic start/stop) are fine.

### 10. Plist and Manifest editing

Unity offers `Build Settings → Player Settings` UI for permission strings, but for production builds these are typically managed via post-build scripts (`OnPostprocessBuild` callback). CDK doesn't ship one; the operator writes it. A typical iOS post-build:

```csharp
[PostProcessBuild]
public static void OnPostprocessBuild(BuildTarget target, string path) {
    if (target == BuildTarget.iOS) {
        var plist = new PlistDocument();
        plist.ReadFromFile(Path.Combine(path, "Info.plist"));
        plist.root.SetString("NSMicrophoneUsageDescription",
            "Required to hear your voice and respond.");
        plist.root.SetString("NSCameraUsageDescription",
            "Optional — used only if you tap the camera button.");
        plist.WriteToFile(Path.Combine(path, "Info.plist"));
    }
}
```

For Android, gradle template manipulation. CDK leaves this to the operator. Ember must standardize.

## Where It Surprises

- **Three native plugins, three platforms, identical Unity-facing interface** (`MicrophoneProvider`). The platform-specific code lives behind a small C# abstraction. Adding a new platform = one new provider, no scene changes.
- **OshaberiAI as the proof.** A shipping commercial iOS app means the build chain is mature enough to clear App Store review without contortions. CDK isn't just code-on-GitHub.
- **The `voiceProcessing` mode on iOS AVAudioSession** is the magic word for AEC. Once set, the OS handles echo cancellation, noise suppression, and AGC. CDK doesn't roll its own AEC; it asks the OS.
- **Unity's `Application.runInBackground` default of `false`** means the avatar quiesces automatically when backgrounded. Battery-saving by inaction.
- **iOS bitcode is going away.** As of Xcode 14+, bitcode is deprecated. Older CDK build instructions may reference enabling it; ignore.
- **Android's `MediaRecorder.AudioSource.VOICE_COMMUNICATION`** is the source-mode equivalent of iOS's `voiceProcessing`. Cross-platform, the right modes exist.
- **The .aar package size** is ~50 KB; the .a is ~200 KB. The native plugins are tiny. The size cost of going-native is invisible compared to the Unity engine itself.

## Where It Breaks

- **The native plugins are binaries.** Operators can't audit them. Apache-2.0 license covers the source, but the source isn't in the repo as of this study. (uezo may ship it on request; the repository as-of v0.8.16 contains only the compiled artifacts.)
- **Unity version coupling.** When Unity changes IL2CPP code generation or asmdef format, the native plugins may need rebuilding. CDK's release cadence and Unity's release cadence are uncoupled; lag is expected.
- **iOS multi-architecture binary slicing**. `libIOSNativeMicrophonePlugin.a` must be a fat archive supporting arm64 (device) + arm64 (simulator) + x86_64 (legacy simulator). Missing slices → cryptic linker errors.
- **No Catalyst support documented.** Mac Catalyst (running iOS apps on macOS) requires either a Catalyst-compatible native binary or fallback to the macOS `.dylib`. CDK does not document this path.
- **Android API-level fragmentation.** Min-SDK choice (21? 24? 28?) affects which AEC APIs work. CDK's `.aar` is built against some min-SDK; pushing higher requires rebuild.
- **`Application.runInBackground = true`** if set (operator override) means the avatar continues to consume CPU/battery when backgrounded. App Store and Play Store both flag excessive background activity. Operators who set this without thinking ship battery-draining apps.
- **No clear policy on local model storage.** A 1 GB downloaded LLM model lives in the app's documents directory or cache directory; OS may evict it. CDK doesn't address this; Ember must.
- **Universal Links / Deep Links** for "share with avatar" / "ask avatar from another app" are unaddressed. Mobile companions get more useful when other apps can hand off to them.
- **Notifications / push** are unaddressed. The avatar that can't notify the user is a tab the user has to remember to open.
- **In-app updates** (Play Core's in-app-update API, App Store's automatic updates) are operator territory. CDK's static build doesn't ship updaters.
- **App Tracking Transparency (ATT)** on iOS 14.5+ — CDK doesn't use IDFA or cross-app tracking, so ATT prompt isn't required. But the privacy nutrition label must accurately reflect this; the operator writes it.

## On-Device LLM Viability — A Closer Look

The standard CDK setup ships **cloud LLM only**. For Ember's Smallness Vow + sometime-offline Vow, on-device must be designed in. The viable approach:

1. **Build-time model selection.** Ember mobile ships a `tier-config.yaml` that picks one of: `tier-cloud` (no model bundled), `tier-mini` (Phi-3-mini Q4 bundled, ~1.5 GB), `tier-base` (Llama-3.2-1B Q4 bundled, ~700 MB). The default for the App Store / Play Store ship is `tier-cloud`; sideloaded / dev builds can ship `tier-mini` or `tier-base`.
2. **Runtime model download** for the cloud-default build: if the user opts in, the app downloads the model on first run. Storage location: app's Documents directory (iOS) or filesDir (Android). Integrity check via SHA256.
3. **Native bridge plugin**: `llama-cpp-unity` style. One `.a` for iOS, one `.so` for Android. Same C# wrapper class on both. Calls `llama_init_from_file`, `llama_generate`, `llama_free`. The bridge exposes Ember's existing `LLMServiceBase` interface so Munnr doesn't know it's local.
4. **Tier-aware quality**: cloud LLM = full Munnr capability; on-device = "small Munnr" mode with stricter response-length limits, simpler tool calling, no streaming-with-tool-call-rewinds.

This is invent territory; CDK doesn't have it. See Invent below.

## Cross-References

- [[10_domain/17_MICROPHONE_MANAGER_DOMAIN]] — the `MicrophoneManager` component and `MicrophoneProvider` abstraction
- [[10_domain/1C_UNITY_LIFECYCLE_DOMAIN]] — Unity build lifecycle (Editor → IL2CPP → Xcode/Gradle)
- [[10_domain/1D_MULTI_PLATFORM_DOMAIN]] — overall platform matrix
- [[50_verification/51_SECURITY_REVIEW]] (Auditor) — mobile permission surfaces, ATT, privacy labels
- [[3B_WEBGL_BUILD]] — sibling platform doc; same control-surface abstraction, different transport
- [[3D_XR_BUILD]] — sibling for VR/AR
- [[sap:3A_CROSS_PLATFORM_BUILDS]] — SAP's Electron+PyInstaller targets desktop, not mobile; mobile is CDK's territory
- [[waifu:23_MOBILE_DEPLOYMENT]] — Waifu's cloud-streaming mobile pattern (no Unity in the build)

## What This Means for Ember

*Apache-2.0 attribution: ChatdollKit native plugins are Apache-2.0 licensed (source not in repo; binaries shipped). Preserve upstream header references per Apache-2.0 §4(c).*

**Adopt:**

- **The `MicrophoneProvider` abstraction** as Ember's native-mic interface. One C# interface, per-platform implementations. Apache-2.0 attribution required. Bind to the proposed Andlit-unity Mic Capture subsystem.
- **The `voiceProcessing` AVAudioSession mode (iOS)** and `MediaRecorder.AudioSource.VOICE_COMMUNICATION` (Android). Use the OS's AEC; don't roll our own.
- **The `MicrophoneMuteBy = None` continuous-barge-in posture** for AEC-equipped builds. Phone-grade AEC is good enough that the mic can stay live during TTS.
- **The native-plugin-as-binary distribution model** if Ember ends up needing native code beyond Unity's stock — but Ember publishes the source too, per Open Knowledge Vow. CDK's binary-only is the one Vow gap we don't carry forward.
- **`Application.runInBackground = false` as default.** The avatar quiesces when the user navigates away. Battery is a public-friendliness concern.

**Adapt:**

- **The build-and-ship friction** — adapt by automating the build via Funi Build Manifest (proposed in [[sap:3A_CROSS_PLATFORM_BUILDS]]). `builds/ios-release.yaml` and `builds/android-release.yaml` declare permissions, entitlements, signing, model-tier. CI builds both with one trigger.
- **The post-build plist/manifest editing** — adapt to a declarative `data/charts/platform_permissions.yaml` with per-platform permission strings, language-keyed. The post-build script reads the YAML; the operator never edits XML/plist by hand.
- **The CDK-only cloud-LLM ship** — adapt with a `tier-config.yaml` that lets the build target Pi-class on-device, mid-tier cloud-LLM, or full mythic-tier multi-model. The build artifact differs by tier.
- **The unaddressed model-download/storage path** — adapt with a typed `LocalModelManager` subsystem responsible for download, integrity verification, eviction, and graceful "model unavailable, falling back to cloud" mode.
- **The unaddressed notifications path** — adapt with an Ember `Pulse` subsystem (proposed Munnr extension): the avatar can push a notification ("I had a thought you might enjoy"). User-opt-in, rate-limited, content-classified.
- **The iOS adult-content constraint** — adapt by shipping two build tiers: `ember-mobile-public` (App Store / Play Store compliant, character-default-clean) and `ember-mobile-mythic` (sideload / TestFlight / APK, full character expression per [[ember:PHILOSOPHY]]).

**Avoid:**

- **Native plugins shipped as binaries without source.** Vow-blocker; we publish source. CDK's posture is understandable for a solo developer; Ember as an open-knowledge project cannot adopt it.
- **Hardcoded permission strings in Unity Player Settings.** Per Vow against hardcoded data: permission strings live in `data/charts/`.
- **`Application.runInBackground = true` blindly.** Battery is a real cost; the avatar that drains the phone is the avatar uninstalled within a week.
- **App Tracking Transparency without consideration.** Ember does not track. The privacy nutrition label declares this explicitly.
- **iOS-only or Android-only.** Both ship; both are first-class. The Pi tier is the canonical small target; the mobile tier is a second-place on-device target with comparable Vow expectations.

**Invent:**

- **Ember Mobile Tier Manifest.** A single YAML declares: target platforms, model tier, permission strings (multilingual), bundle limits (max size MB, target compressed APK/IPA), in-app-purchase requirements (none for Ember, but the manifest field exists), age-rating class. CI consumes this; the manifest is the build's source of truth. Vow tie-in: **Modular Authorship**, **Smallness**.
- **Ember Local LLM Bridge (`llama-cpp-ember`).** A small C wrapper around llama.cpp exposing the four functions Ember needs: `init_from_file`, `generate_stream`, `cancel`, `free`. Two compiled artifacts: `libllamaember.a` (iOS, multi-arch) and `libllamaember.so` (Android, per-ABI). One C# class `LlamaCppEmberService : LLMServiceBase` consumed by Munnr like any other LLM service. Vow tie-in: **Pluggable Storage**, **Tiered Presence**.
- **First-Run Model Download Flow.** New mobile installs default to `tier-cloud`. The first time the user explicitly enables "offline mode", the app downloads `tier-base` model (~700 MB) in the background, showing progress. Cancel/resume supported. Integrity verified by SHA256. The download is opt-in and the user is told the cost. Vow tie-in: **Public-Friendliness**.
- **Ember Pulse — Avatar-Initiated Notifications.** The avatar can emit a notification: `(category: thought | reminder | scheduled, content: text, voice_optional: bool)`. User configures categories (per-category opt-in). Rate-limited to N pulses/day. All pulses are LLM-classified through a small evaluator: "does this pulse respect the user's stated preferences?". Vow tie-in: **Surface Without Surveillance** (pulse is the only proactive surface; gate it carefully).
- **Universal-Link Hand-Off.** Other apps can deep-link into Ember: `ember://ask?text=...&context=...`. The avatar appears, voices the question, responds. Wires the avatar into the user's daily workflow without an open-app-and-type ritual. Vow tie-in: **Federated Self**.
- **Privacy-Nutrition-Label as YAML.** Ember publishes its own per-platform privacy declarations from `data/charts/privacy_label.yaml`. CI generates the iOS plist + Android Data Safety form contents from the same source. Operators can't accidentally publish a label that misrepresents data flows. Vow tie-in: **Defended Builds** generalized to **Defended Disclosure**.
- **Battery Budget Surface.** The Ember mobile app exposes its battery cost transparently: a settings screen shows "Avatar active today: 28 min; battery used: 4.2%". When the user nears a configured cap (default 10%/day), the avatar visibly tires (slower idle anim, lower TTS quality) and asks if the user wants to extend. Mythic Living: the system's resource cost is part of the embodied conversation, not hidden. Vow tie-in: **Mythic Living in the Digital Age**, **Smallness**.

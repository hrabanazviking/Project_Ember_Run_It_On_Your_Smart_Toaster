---
codex_id: 50_DEPENDENCY_HEALTH
title: Dependency Health — Burst, UniTask, uLipSync, UniVRM, Newtonsoft, ONNX
role: Auditor
layer: Verification
status: draft
chatdoll_source_refs:
  - README.md:201-205
  - Scripts/Network/SocketServer.cs:9
  - Extension/SileroVAD/SileroVADProcessor.cs:12
  - Plugins/iOS/libIOSNativeMicrophonePlugin.a
ember_subsystem_targets: [Funi, Rödd, Andlit]
cross_refs:
  - 50_verification/52_PERFORMANCE_BUDGETS
  - 50_verification/55_WEBGL_GOTCHAS
  - 50_verification/56_SISTER_INTEGRATION_RISKS
  - 20_interface/24_VAD_INTERFACE
  - sap:54_DEPENDENCY_HEALTH
  - waifu:50_DEPENDENCY_HEALTH
---

# Dependency Health — Burst, UniTask, uLipSync, UniVRM, Newtonsoft, ONNX

> *Sólrún, voice cold and even: ChatdollKit is 18,221 lines of C# resting on a hand-curated stack of six third-party Unity packages plus three precompiled native binaries. None of these dependencies is shipped through Unity's Package Manager registry with a manifest lock. They are installed by URL and version-string, by hand, from a README. Any one of them moving — UniVRM's bone schema, uLipSync's vowel detector, Burst's IL backend, Newtonsoft's TypeNameHandling defaults, ONNX Runtime's Unity binding — silently breaks the kit. There is no `Packages/manifest.json` in the repository, no SBOM, no automated drift detector. The audit posture is: trust the README.*

CDK's dependency surface is smaller in count than SAP's Python wheel forest (eighty-something pinned wheels in `requirements.txt`) and larger than Waifu's twenty-two npm package brittleness. But CDK's dependencies are *deeper*: the Unity ABI changes between LTS versions, UniVRM's runtime loader is held together by reflection against UniGLTF internals, and the native iOS/Android plugins ship as opaque `.a` and `.aar` blobs the operator cannot recompile without source. That last detail bears emphasis. *The kit cannot be rebuilt from source for iOS or Android.*

---

## 1. The Declared Dependencies

The README declares (`README.md:201-205`):

```
- Burst from Unity Package Manager
- UniTask (Tested on Ver.2.5.4)
- uLipSync (Tested on v3.1.0)
- UniVRM (v0.127.2)
- Newtonsoft JSON (via UPM)
```

Six entries, none of them in a manifest file. *"Tested on"* is doing heavy lifting here — it is the README's substitute for a lock file. The operator who clones a Unity project, drags CDK in, and runs `Package Manager → Add from Git URL` for UniTask gets whatever HEAD is on that hour. If neuecc has shipped UniTask 3.x by the time the operator clones, the kit's `using Cysharp.Threading.Tasks;` calls may or may not bind to the same surface as v2.5.4. The README does not warn about this.

There are five further dependencies the README does not list:

1. **ONNX Runtime for Unity** (`Microsoft.ML.OnnxRuntime`) — required by `SileroVADProcessor.cs:12`; not mentioned in the README dependency block; ships under Microsoft's MIT license but with native binaries per platform. Required for ML-based VAD; without it CDK falls back to energy-based VAD.
2. **NativeWebSocket** — required for WebGL streaming STT, declared inline in README at `:731` as a git URL: `https://github.com/endel/NativeWebSocket.git#upm`. Not in any manifest.
3. **Three native plugin blobs** at `Plugins/iOS/libIOSNativeMicrophonePlugin.a`, `Plugins/Android/*.aar`, `Plugins/macOS/*.bundle` — precompiled, no source in the repository.
4. **Five WebGL JSLIB files** at `Plugins/*.jslib` — Emscripten plug-in code that must be linked at build time; sensitive to Emscripten ABI changes.
5. **Unity's own version coupling** — UniVRM 0.127.2 requires Unity 2022.3.x LTS or newer with `Universal Render Pipeline` *not* installed (the README states this at `:195`: *"⚠️CAUTION: Do not use the SRP (Scriptable Render Pipeline) project template"*). This is a Unity-level coupling no Package Manager will surface.

Eleven dependencies, one declared list, no lock. This is the audit posture.

---

## 2. Per-Dependency Brittleness

### 2.1 Burst

Unity's `com.unity.burst` package. Compiles `[BurstCompile]` methods to native via LLVM. CDK uses it implicitly through UniTask and through uLipSync's hot path. Burst is Unity-supported, ships through UPM with a manifest version, and is generally stable. *Risk: low.* The only known breakage is when Burst major-versions clash with Unity LTS minor-versions — Burst 1.8 against Unity 2022.1 versus 2022.3 has different IL transforms. No CDK code I can find checks `BURST_VERSION`.

### 2.2 UniTask

Cysharp's `UniTask`. Replaces .NET's `Task` with allocation-free awaitables, critical for Unity's frame-rate sensitivity. CDK's entire async stack is UniTask: `LLMServiceBase.cs:50` declares `Func<...> OnStreamingEnd` over `UniTask`; `SpeechSynthesizerBase.cs:28` `GetAudioClipAsync` returns `UniTask<AudioClip>`. Replacing UniTask with stock `Task` would break the kit.

UniTask is at v2.5.4 in the README's *"tested on"* line. Cysharp's release cadence is roughly biannual. Between v2.5.4 and HEAD I have not audited the diff, but the project has historically maintained API stability across minor versions. *Risk: medium.* The package is on neuecc's personal GitHub (`Cysharp/UniTask`), shipped via UPM git URL — a single-maintainer dependency without organizational fallback. If neuecc steps away, every UniTask consumer in the Unity ecosystem stalls. This is the same single-point-of-failure as Waifu's dependence on Pixiv's ZeroWeight SDK, but with broader blast radius.

### 2.3 uLipSync

Hecomi's lip-sync analyzer at v3.1.0. CDK depends on it through `Scripts/Model/uLipSyncHelper.cs`. uLipSync extracts vowel envelopes from audio and drives BlendShape weights on the avatar's mouth. The "vowel set" (A/I/U/E/O for Japanese; A/I/U/E/O is also passable for English approximation) is a hardcoded array in uLipSync; changing it changes the lip-sync output.

*Risk: medium-high.* hecomi is also a single-maintainer; uLipSync has had API breakages between v2.x and v3.x. If the operator installs HEAD (v3.2+) and the BlendShape weight curve has been retuned, CDK's lip-sync will drift visibly. There is no version assertion in code.

### 2.4 UniVRM

The reference Unity loader for the VRM format. v0.127.2 in the README. Maintained by the VRM Consortium and Masataka SUMI (MToon). This is the load-bearing dependency for the entire ModelController surface: facial blendshapes, bone mappings, expression presets, runtime VRM loading, MToon material binding. Without UniVRM, CDK has no avatar.

*Risk: high.* UniVRM has been under continuous restructuring since the VRM 1.0 spec landed in 2023. The split into UniVRM (1.0) and UniVRM-0.x (legacy) has caused operator confusion repeatedly. v0.127.2 is a *legacy* line — the kit is on the 0.x track, which the VRM Consortium has marked maintenance-only. When the consortium eventually retires the 0.x line, CDK breaks unless it migrates to UniVRM 1.0, which has a different runtime API.

### 2.5 Newtonsoft.Json

`com.unity.nuget.newtonsoft-json`. Used everywhere: `Scripts/Network/SocketServer.cs:9`, `Scripts/LLM/*/Service.cs`, `Scripts/IO/JavaScriptMessageHandler.cs:44`. *Risk: medium-high* — but not from the dependency itself. From its *configuration*. `Scripts/LLM/ChatGPT/ChatGPTService.cs:37-40` sets:

```csharp
protected JsonSerializerSettings messageSerializationSettings = new JsonSerializerSettings
{
    TypeNameHandling = TypeNameHandling.All
};
```

`TypeNameHandling.All` is the deserialization setting that has caused every major .NET RCE in the last decade. It instructs Newtonsoft to honor a `$type` field in the JSON and instantiate whatever .NET type it names. If untrusted JSON ever reaches this deserializer — through the SocketServer, through the JavaScript bridge, through a poisoned LLM response — the deserializer will instantiate adversary-chosen types. Even when constrained to a particular base type, gadget chains exist (`System.IO.FileInfo`, `System.Diagnostics.Process` indirectly through various wrappers). I treat this as a dependency-configuration finding rather than a dependency-version finding because it is correct as-of every Newtonsoft version since 8.0. See `[[51_SECURITY_REVIEW]] §4` for the deeper read.

### 2.6 ONNX Runtime for Unity

`Microsoft.ML.OnnxRuntime`. Required by Silero VAD on non-WebGL platforms. Ships as native binaries per architecture (x64 / ARM64 / iOS / Android). *Risk: medium.* Microsoft maintains this; releases are quarterly; ABI is broadly stable. The brittleness is the *model file* — `silero_vad.onnx` must be present in `StreamingAssets/`, and Silero has released new model versions that change tensor shapes (`state` was 256 floats in older models, 128 in some newer ones; CDK pins `state = new float[256]` at `SileroVADProcessor.cs:44`). Operators who download a newer Silero model break this.

### 2.7 The Native Plugin Blobs

Three precompiled binaries:

- `Plugins/iOS/libIOSNativeMicrophonePlugin.a` — Objective-C++ static archive for iOS audio engine with AEC/noise-cancellation.
- `Plugins/Android/*.aar` (verified by directory listing) — Android Java SDK for the equivalent.
- `Plugins/macOS/*.bundle` — macOS native plug-in.

*Risk: high.* These are opaque. The operator cannot diff them against source. They were built by uezo (`README.md` attribution) on uezo's machine, with whatever toolchain version, signed with whatever entitlements. Each is a single point of trust *and* a single point of breakage when Apple/Google ABI changes happen. Apple's transition from Intel to ARM Macs forced rebuilds of every macOS bundle in the Unity ecosystem in 2020-2022; the next forcing function will be similar. Without source, the operator must wait for uezo to rebuild.

This is the single largest dependency-health finding in the codex.

---

## 3. The Unity-Version Coupling

CDK does not declare a minimum Unity version in `package.json` (no such file exists). The README at `:194-195`:

> *"⚠️CAUTION: Do not use the SRP (Scriptable Render Pipeline) project template in Unity. UniVRM, which ChatdollKit depends on, does not support SRP."*

That is the only version-tier guidance. From inspection of `[Serializable]` attributes, `[Header]` decorators, `AudioWorkletNode` in `Plugins/WebGLMicrophone.jslib`, and the use of `Microphone.GetPosition`, the kit needs at minimum Unity 2022.3 LTS. The `AudioWorkletNode` path was added in v0.8.11 (README's `:50`) and that requires Unity's WebGL backend at 2022 or later. iOS native echo cancellation (v0.8.14) requires Apple's `AVAudioEngine` with iOS 13+ deployment target — the operator must set Player Settings accordingly.

There is no `OnValidate`, no editor-time guard, no compile-time `#if UNITY_VERSION >= ...` check. An operator who clones CDK into Unity 2020.3 LTS gets a wall of compile errors with no friendly explanation.

---

## 4. Dependency Drift Surface

A summary table:

| Dependency | Pinned at | Auth lock | Source diffable? | Single maintainer? | Drift cost |
|---|---|---|---|---|---|
| Burst | UPM HEAD | No | No (Unity-internal) | No (Unity Inc.) | Low |
| UniTask | "Tested on 2.5.4" | No | Yes | Yes (neuecc) | Medium |
| uLipSync | "Tested on 3.1.0" | No | Yes | Yes (hecomi) | Medium-high |
| UniVRM | 0.127.2 | No | Yes | No (consortium) | High |
| Newtonsoft | UPM | Implicit | Yes | No (Microsoft) | Medium (config-risk) |
| ONNX Runtime | Inferred | No | Yes | No (Microsoft) | Medium |
| NativeWebSocket | "git#upm" | No | Yes | Yes (endel) | Medium |
| iOS native plugin | Built by uezo | None | **No** | Yes (uezo) | High |
| Android native plugin | Built by uezo | None | **No** | Yes (uezo) | High |
| macOS native plugin | Built by uezo | None | **No** | Yes (uezo) | High |
| WebGL JSLIB | Vendored | N/A | Yes | Yes (uezo) | Low (in-tree) |

Five high-risk rows. Three are CDK-owned binaries the operator cannot rebuild. Two are UniVRM and the implicit hecomi/neuecc single-maintainer chains. The kit is *one maintainer-disappearance event* from being unmaintainable across iOS and Android.

---

## 5. What Would A Lock-File Look Like?

CDK could trivially produce a `Packages/manifest.json` pinning the UPM versions plus a `dependencies.txt` for the git-URL packages. It does not. Adopting CDK into Ember's Andlit-unity tier should include producing such a lock at integration time. The Architect's `10_DOMAIN_MAP` should treat this as a prerequisite.

For the native plug-ins: Ember should *not* adopt the precompiled binaries. If Andlit-unity wants iOS/Android, Ember rebuilds the Objective-C/Java source from CDK's `Plugins/macOS/*.mm` and `Plugins/Android/*.java` (which I have not located in the clone — they may not be in the repository; see `[[56_SISTER_INTEGRATION_RISKS]]` for source-availability check).

---

## 6. Cross-References

- `[[51_SECURITY_REVIEW]]` — the `TypeNameHandling.All` Newtonsoft config is a security finding, not just a dependency finding.
- `[[52_PERFORMANCE_BUDGETS]]` — Burst, UniTask, ONNX are all in the hot path; their drift cost includes performance regression.
- `[[55_WEBGL_GOTCHAS]]` — Emscripten / `AudioWorkletNode` / NativeWebSocket all live in the WebGL surface.
- `[[56_SISTER_INTEGRATION_RISKS]]` — ChatMemory / AIAvatarKit / AITuber Controller add four more single-maintainer dependencies on top of this list.
- `[[sap:54_DEPENDENCY_HEALTH]]` — SAP's eighty-wheel Python stack is wider, shallower, with PyPI as a registry backstop.
- `[[waifu:50_DEPENDENCY_HEALTH]]` — Waifu's twenty-two npm packages are the shallowest of the three corpora; CDK is the deepest.

---

## What This Means for Ember

**Adopt:** The pattern of declaring "tested on version X" in README — explicit, not implicit — when no lock-file format exists. Ember can extend this to its own integration manifests for Andlit-unity. *Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:** CDK's pinning of Silero VAD model file (`silero_vad.onnx`) shows that *runtime data files* are dependencies too. Ember should treat Smiðja's tool models and Brunnr's embedding models as locked artifacts with SHA-256 hashes in a manifest, not "whatever's in `models/`".

**Avoid:**
- The `TypeNameHandling.All` configuration on Newtonsoft. Whichever JSON library Ember uses (Python's `json`, Rust's `serde`), default to *least permissive deserialization*. Never trust `$type`-style polymorphic dispatch on inbound JSON.
- Shipping precompiled native binaries the operator cannot rebuild. If Andlit-unity ever needs platform-specific native code, ship the source and a `make` target.
- The hardcoded model defaults that go stale: `Model = "claude-3-haiku-20240307"` at `ClaudeService.cs:16` will become invalid when Anthropic retires that model id. Ember's LLM bindings should have a runtime "model availability check" that falls back gracefully rather than 404-ing into silence.

**Invent:** A **dependency-health probe** for Funi/Smiðja that runs at startup and emits a structured report to the operator: which declared dependencies were found, which versions resolved, which native blobs were present, which model files matched expected hashes. The probe writes one JSON record per dependency to a `health.jsonl` log. The operator can `tail` it. This is the artifact CDK lacks and that every operator integrating CDK into a product builds themselves badly. Ember can ship it as a Vow-fulfillment of Tethered Grounding: the operator should *know* what they actually have.

---

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c).*

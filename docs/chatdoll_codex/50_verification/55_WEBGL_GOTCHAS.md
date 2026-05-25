---
codex_id: 55_WEBGL_GOTCHAS
title: WebGL Gotchas — Emscripten, Audio Context, Single-Thread, Memory
role: Auditor
layer: Verification
status: draft
chatdoll_source_refs:
  - Scripts/IO/JavaScriptMessageHandler.cs:14-52
  - Plugins/JavaScriptMessageHandler.jslib
  - Plugins/WebGLMicrophone.jslib
  - Plugins/GeminiServiceWebGL.jslib
  - Plugins/CopyThisJSToStreamingAssets
  - Scripts/LLM/LLMServiceBase.cs:14-21
  - Scripts/LLM/Gemini/GeminiServiceWebGL.cs
  - Scripts/SpeechListener/AIAvatarKitStreamSpeechListener.cs
  - Extension/SileroVAD/SileroVADProcessor.cs:9-30,57-60
  - README.md:1014-1080
ember_subsystem_targets: [Andlit, Rödd]
cross_refs:
  - 50_verification/50_DEPENDENCY_HEALTH
  - 50_verification/51_SECURITY_REVIEW
  - 50_verification/57_FAILURE_TAXONOMY
  - 20_interface/28_JS_BRIDGE_INTERFACE
  - waifu:51_SECURITY_AND_PRIVACY
---

# WebGL Gotchas — Emscripten, Audio Context, Single-Thread, Memory

> *Sólrún, voice cold and even: ChatdollKit's WebGL build target is the most ambitious surface in the kit. It compiles 18,221 lines of C# to WebAssembly via Unity's Emscripten backend, swaps in JSLIB plug-ins for every native interop, abandons the entire `System.Net.WebSockets` namespace because the browser's WebSocket can't reach it, hands microphone capture to an `AudioWorkletNode`, and prays the audio context gets a user gesture before any of this matters. The README warns about half of the gotchas in scattered comments. The other half are visible only by reading the JSLIB plug-ins and the per-provider `*ServiceWebGL.cs` shims. This document catalogs both halves. The audit posture is: WebGL is a different kit wearing the same coat.*

This document is the verification reading of the WebGL surface. The interface counterpart `[[28_JS_BRIDGE_INTERFACE]]` defines the bridge contract; here I audit where the contract leaks, where it crashes, where it silently does nothing.

The kit publishes a live WebGL demo at the URL in `README.md:4`. That demo's existence is evidence the surface works, but the demo runs on a curated configuration. Operators porting their own scenes face a long debugging tail.

---

## 1. The Five JSLIB Plug-Ins

CDK's `Plugins/` directory contains:

```
Plugins/AIAvatarKitServiceWebGL.jslib
Plugins/ChatGPTServiceWebGL.jslib
Plugins/ClaudeServiceWebGL.jslib
Plugins/DifyServiceWebGL.jslib
Plugins/GeminiServiceWebGL.jslib
Plugins/JavaScriptMessageHandler.jslib
Plugins/SimpleCameraWebGL.jslib
Plugins/WebGLMicrophone.jslib
Plugins/CopyThisJSToStreamingAssets/WebGLMicrophoneProcessor.js
```

Each JSLIB is JavaScript loaded into the Unity WebAssembly module at link time. They exist because Unity's standard networking, microphone, and camera APIs do not work in the browser — they must be replaced by JS-side implementations that call Web APIs (`fetch`, `getUserMedia`, `AudioWorklet`, `AudioContext`).

The dual structure — `*Service.cs` for native, `*ServiceWebGL.cs` for WebGL, with JSLIB to bridge — doubles the maintenance surface. Every LLM provider has *two* source files. Every Unity-side bug fix needs review against the WebGL shim.

---

## 2. The Audio Context Gesture Requirement

`Plugins/WebGLMicrophone.jslib` (excerpt):

```javascript
InitWebGLMicrophone: function(targetObjectNamePtr, useMalloc) {
    var mic = document.webGLMicrophone = {};
    mic.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    ...
    mic.processorModuleUrl = "StreamingAssets/WebGLMicrophoneProcessor.js";
```

The `AudioContext` constructor in Chrome (since 2018), Firefox (since 2020), and Safari (since 2019) **refuses to start in `running` state without a user gesture**. CDK's JSLIB constructs the context immediately at component init. The result: the context is in `suspended` state until the user clicks something — anywhere on the page, anything. Until then, microphone capture does nothing visible. The Unity side may believe it is recording; no audio is reaching the worklet.

CDK does not document this explicitly. The README mentions `WebGL` 11 times but never explains the gesture requirement. Operators who deploy a CDK WebGL build behind an auto-open page (e.g., an embedded iframe with no obvious click target) find the mic silently broken until they realize they need a "Start" button.

### 2.1 The autoplay-policy variation

Chrome's autoplay policy keeps the AudioContext suspended even for *playback* until a gesture. The kit's TTS output goes through an `AudioSource` driven by Unity's audio system, which in turn drives the same suspended AudioContext. **TTS output is silent on first page load.** The user clicks "Start", AudioContext resumes, TTS plays from then on. The first 1-2 seconds of any auto-greeting are inaudible.

Mitigation: have the operator wire a "Click to begin" overlay that calls `AudioContext.resume()` before doing anything else. CDK ships no such overlay. The README has a buried reference at `:1014-1080`.

---

## 3. The Single-Thread Constraint

WebGL is single-threaded. Unity's WebAssembly does not have `SharedArrayBuffer` access by default (gated by COOP/COEP headers most operators don't set). This means:

- **No `Thread` objects.** `SocketServer.cs` is conditionally compiled out (`#if !UNITY_WEBGL` wraps the entire implementation; verified at `SocketServer.cs:19,201`).
- **No `System.Net.WebSockets`.** CDK requires the third-party `NativeWebSocket` UPM package for WebGL streaming (per README `:731`).
- **No blocking I/O.** Every `await` in the LLM service has to be `UniTask`-based because `Task.Wait` would deadlock.
- **No `Task.Run` parallelism.** Tools that fork CPU work via `Task.Run` will block the main thread.

This is why `LLMServiceBase.cs:14-21` has:

```csharp
public virtual bool IsEnabled {
    get {
#if UNITY_WEBGL && !UNITY_EDITOR
        return false;
#else
        return _IsEnabled;
#endif
    }
```

**Every non-WebGL service is hard-disabled in WebGL builds.** The base class returns `false` from `IsEnabled` regardless of the Inspector setting. The operator must use the `*ServiceWebGL` variant. This is a defensive compile-time guard, correct in shape, but it means the operator who drags a `ChatGPTService` component onto a scene and builds for WebGL gets a silently-disabled LLM with no log message explaining why.

### 3.1 The Silero VAD WebGL bypass

`Extension/SileroVAD/SileroVADProcessor.cs:9-30`:

```csharp
#if UNITY_WEBGL && !UNITY_EDITOR
    using System.Runtime.InteropServices;
#else
    using Microsoft.ML.OnnxRuntime;
    using Microsoft.ML.OnnxRuntime.Tensors;
#endif
```

The ONNX Runtime does not run in Unity WebGL. CDK's WebGL Silero VAD path delegates to a JS-side ONNX inference (per the `[DllImport("__Internal", EntryPoint = "IsVoiceDetected")]` at `:21`). The JS-side ONNX runtime is `onnxruntime-web`, which has its own browser-compatibility tail (WebAssembly SIMD on Safari requires version 16.4+, WebGL backend disabled by default).

The README at `:729` says:

> *"Using Silero VAD in WebGL builds can cause high browser processing overhead. We recommend using `AIAvatarKitStreamSpeechListener` to offload VAD processing to the server side."*

Translation: ML-based VAD is too slow to run in the browser. Push it to a server. The kit recommends the workaround but does not enforce it.

---

## 4. The Memory Pressure

WebAssembly has a 4GB address space limit (32-bit). Unity's WebGL builds default to 256MB or 512MB heap, configurable. CDK's 18k LOC of compiled C# plus UniVRM plus uLipSync plus the VRM model file plus the audio cache plus the ONNX model (if Silero) plus the LLM context history can saturate the default heap.

`SpeechSynthesizerBase.cs`'s unbounded audio cache (`[[54_MULTI_TTS_QUALITY]] §4`) is especially dangerous in WebGL — each cached `AudioClip` is a `Float32Array` in the WebAssembly heap. A long session accumulates these until the heap aborts.

Unity's WebGL build aborts with `RuntimeError: memory access out of bounds` when the heap maxes. The browser tab dies; the user loses the conversation.

---

## 5. The API Key Visibility

Every `*ServiceWebGL.jslib` ships the API key into the browser fetch:

`Plugins/GeminiServiceWebGL.jslib`:

```javascript
StartGeminiMessageStreamJS: function(targetObjectNamePtr, sessionIdPtr, urlPtr, apiKeyPtr, geminiStreamRequestPtr) {
    let apiKey = UTF8ToString(apiKeyPtr);
    ...
    fetch(url + "?key=" + apiKey, { ... })
```

The key is passed as a `char*` from the Wasm side, decoded to a JS string, and used in a fetch URL. **The key is visible in the browser's DevTools Network panel.** Any user with F12 access can read it. This is the same finding as `[[51_SECURITY_REVIEW]] §5.1` but more acute: the build-bundle leak is one tier, the *runtime DevTools visibility* is another.

The README's v0.8.11 changelog mentions *"fixed API-key authorization in WebGL builds"* — meaning the kit *fixed a bug where the key wasn't working* in WebGL, not *fixed the leak*. The leak is by design.

---

## 6. The Async/Await Trap

The README at `:1020`:

> *"Built-in Async/Await doesn't work (app stops at `await`) because JavaScript doesn't support threading. Use UniTask instead."*

Correct guidance, but the trap is wider. Any third-party Unity asset the operator pulls in (animation libraries, networking plug-ins, analytics SDKs) that uses stock `Task` rather than `UniTask` will freeze the application at the first `await`. The freeze is silent — no exception, no log, the Unity main loop just stops advancing. The operator sees a frozen avatar.

Debugging requires inspecting the JS console for the absence of `requestAnimationFrame` callbacks. Not obvious. CDK provides no compile-time check that the operator's other assets are UniTask-clean.

---

## 7. The CORS Surface

Every cloud TTS / STT / LLM provider is contacted from the browser. The provider's server must include `Access-Control-Allow-Origin` headers permitting the page's origin. OpenAI does (`*` for the chat completions endpoint, with auth in the header). Google Gemini does. Anthropic Claude **does not by default** — the API was historically server-to-server only. CDK's `ClaudeServiceWebGL.cs` works because Anthropic has since added CORS for browser usage, but only when the request includes `anthropic-dangerous-direct-browser-access: true`. The kit must set this header; I have not verified it does. If the kit ever omits it, every Claude WebGL build returns CORS errors.

VOICEVOX runs locally on the user's machine (usually `localhost:50021`). The browser cannot reach `localhost` from a remote HTTPS page without explicit CORS configuration on the VOICEVOX side. VOICEVOX's default config does not include `Access-Control-Allow-Origin`. CDK's WebGL build pointed at local VOICEVOX returns CORS errors. The operator must configure VOICEVOX with `--cors_policy_mode=all`, which the README mentions nowhere.

---

## 8. The Build-Time Tail

A WebGL build of a CDK scene takes 5-10 minutes on a modern laptop. The compile is Emscripten's LLVM IL → WebAssembly pass, followed by Unity's IL2CPP transform on the C#. Iteration cost is painful. An operator debugging a JS bridge issue (origin failure, audio context not resuming, key visibility) loops at 5-10 minutes per fix.

There is no incremental rebuild. There is no hot-reload. Every test is a full build.

---

## 9. The Diagnostic Black Hole

When something goes wrong in a WebGL build, the operator sees:

- A Unity log line in `console.log` (sometimes; many `Debug.LogError` calls do not reach the browser console).
- A JS exception (if the JSLIB throws).
- A `RuntimeError: memory access out of bounds` on heap exhaustion.
- Silence (for the await-trap freeze).

There is no remote logging, no telemetry, no crash reporter. The operator's only diagnostic surface is the user reporting "it doesn't work."

---

## 10. Cross-References

- `[[28_JS_BRIDGE_INTERFACE]]` — the interface-level read on the bridge.
- `[[51_SECURITY_REVIEW]]` §5.2, §3.2 — the WebGL surface compounds key visibility and origin verification.
- `[[50_DEPENDENCY_HEALTH]]` §2.7 — `NativeWebSocket` is a WebGL-only dependency.
- `[[57_FAILURE_TAXONOMY]]` — the ranked rollup.
- `[[waifu:51_SECURITY_AND_PRIVACY]]` — Waifu is browser-native; many of CDK's WebGL pains do not apply to a kit designed for the browser from day one.

---

## What This Means for Ember

**Adopt:** The pattern of **per-platform compile gating with a base class that hard-disables on the incompatible platform** (`LLMServiceBase.IsEnabled` returns `false` in WebGL) is correct. *Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).* Ember's runtime-binding layer can do the same: if a backend selection is invalid for the current tier, the binding refuses to enable with a clear log line.

**Adapt:** CDK's dual-file-per-provider pattern (`ChatGPTService.cs` + `ChatGPTServiceWebGL.cs`) is heavy maintenance. Ember should *prefer a single file with `#if`-bounded sections* for small platform deltas, and *separate files* only when the difference is genuinely architectural (HTTP-streaming vs JS-fetch is borderline; use case-by-case judgment).

**Avoid:**
- Auto-instantiating an `AudioContext` before user gesture. Always defer to first interaction.
- Passing API keys to JS as `char*` arguments. If WebGL is to be supported, route credentials through a backend (the Strengr proxy pattern in `[[51_SECURITY_REVIEW]]` invent block).
- Unbounded heap allocation in WebGL. Cap cache sizes, pool audio clips, refuse to grow.
- Pulling third-party Unity assets without a UniTask-clean check.

**Invent:** A **WebGL build linter** for Ember. At build time, scan the project for:
1. Any reference to `System.Threading.Tasks.Task` outside `using` (suggests non-UniTask third-party code).
2. Any field of type `string` named like `ApiKey`/`Token`/`Secret` (suggests a leak vector).
3. Any `Thread` instantiation, `System.Net.Sockets.TcpListener`, or other unsupported API.
4. Any cache `Dictionary<...>` field without an associated eviction mechanism.

The linter emits errors that block the WebGL build until addressed. CDK's posture is "build and discover" — Ember's should be "lint and prevent."

A second invention: **the WebGL audio resume overlay**. Ember ships a one-line operator-deploy pattern: a transparent click-to-begin overlay that calls `AudioContext.resume()`, requests `getUserMedia({audio: true})`, then dismisses itself. The pattern is a Vow-aligned default: *Graceful Offline* (the overlay also detects offline state and shows a degraded mode) + *Public-Friendliness* (the user sees a friendly "tap to begin" rather than a frozen avatar).

A third invention: **the WebGL diagnostic relay**. When deployed in WebGL, Ember's Munnr emits structured error events back to a configured Strengr endpoint (operator-supplied, opt-in) so the operator sees crash signals without the user filing a bug report. Privacy-preserving: no content, only structured error types and stack hashes. CDK has nothing equivalent; debugging a WebGL CDK deploy in production is divination.

---

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c).*

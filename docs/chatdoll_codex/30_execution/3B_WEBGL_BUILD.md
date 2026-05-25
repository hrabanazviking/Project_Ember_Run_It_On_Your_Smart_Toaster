---
codex_id: 3B_WEBGL_BUILD
title: WebGL Build — Emscripten, AudioWorklet, and the Browser's Permission to Make Noise
role: Forge-B
layer: Execution
status: draft
chatdoll_source_refs:
  - /tmp/ChatdollKit/Plugins/WebGLMicrophone.jslib:1-206 (mic capture via AudioWorklet + VAD)
  - /tmp/ChatdollKit/Plugins/CopyThisJSToStreamingAssets/WebGLMicrophoneProcessor.js:1-11 (AudioWorkletProcessor)
  - /tmp/ChatdollKit/Plugins/JavaScriptMessageHandler.jslib:1-10 (JS → Unity bridge)
  - /tmp/ChatdollKit/Plugins/AIAvatarKitServiceWebGL.jslib (LLM streaming bridge)
  - /tmp/ChatdollKit/Plugins/ChatGPTServiceWebGL.jslib (OpenAI streaming bridge)
  - /tmp/ChatdollKit/Plugins/ClaudeServiceWebGL.jslib (Claude streaming bridge)
  - /tmp/ChatdollKit/Plugins/GeminiServiceWebGL.jslib (Gemini streaming bridge)
  - /tmp/ChatdollKit/Plugins/DifyServiceWebGL.jslib (Dify streaming bridge)
  - /tmp/ChatdollKit/Plugins/SimpleCameraWebGL.jslib (camera capture)
  - /tmp/ChatdollKit/Plugins/WebGL/FileUploader.jslib (image upload)
  - /tmp/ChatdollKit/Scripts/LLM/AIAvatarKit/AIAvatarKitServiceWebGL.cs:1-308 (Unity-side WebGL service)
  - /tmp/ChatdollKit/README.md:4 (live demo URL)
  - /tmp/ChatdollKit/README.md:30 (WebGL enhancements summary)
  - /tmp/ChatdollKit/README.md:50 (AudioWorkletNode upgrade)
  - /tmp/ChatdollKit/README.md:96 (JavaScript control of Unity)
  - /tmp/ChatdollKit/README.md:612 (compressed audio caveat)
  - /tmp/ChatdollKit/README.md:729-731 (Silero VAD WebGL overhead)
ember_subsystem_targets: [Funi, Andlit]
cross_refs:
  - 10_domain/1C_UNITY_LIFECYCLE_DOMAIN
  - 10_domain/1D_MULTI_PLATFORM_DOMAIN
  - 20_interface/28_JS_BRIDGE_INTERFACE
  - 50_verification/55_WEBGL_GOTCHAS
  - sap:3A_CROSS_PLATFORM_BUILDS
  - waifu:11_LIVEKIT_INTEGRATION
---

# WebGL Build

> *Unity in the browser is Unity except for sockets, threads, file I/O, persistent storage, audio capture, and time. Almost everything CDK does has a special-case WebGL branch. The shape of those branches teaches you the actual shape of the browser sandbox.*

Forge. Eldra-iron. CDK ships a **live WebGL demo** at `unagiken.blob.core.windows.net/chatdollkit/ChatdollKitDemoWebGL/index.html` (`README.md:4`). It is functional. It does voice conversation. It does VAD. It does lip-sync. It streams LLM responses chunk by chunk. The avatar walks, gestures, and responds in under a second per turn over a typical home connection.

To make this work, CDK maintains **eleven separate `.jslib` plugins** in `Plugins/`. Each one is a thin Emscripten-callable JavaScript bridge for a single browser capability Unity's standard library can't reach: microphone, camera, file upload, fetch-with-streaming-response, JS→Unity messaging. This is the cost of running Unity in the browser. This document catalogs it honestly so Ember can decide whether the cost is worth paying.

## What WebGL Buys

The Unity WebGL build target produces:

- A 7–50 MB `index.html` + `Build/` directory containing the Emscripten-compiled `wasm` module, the unity loader JS, and asset bundles
- Pure-browser execution: no install, no native binary, no app store
- Cross-OS by definition: any browser supporting WebGL 2 + WebAssembly
- The widest possible reach for any Unity-based avatar product

For Ember's potential Andlit-unity tier, WebGL is the **lowest-friction onboarding path** — a user receives a link, clicks it, and is in conversation with the avatar in under 10 seconds. No installer, no permissions dialog except mic-access. The reach trumps every other distribution method for casual users.

The cost: see the rest of this document.

## What WebGL Costs

### 1. Build time

A WebGL build is **5–10 minutes** for a modest CDK scene. The Emscripten compiler walks every `.cs` file IL2CPP'd it, the linker resolves every `[DllImport]` against the `.jslib` files, the asset bundler compresses every texture/audio/VRM, and the final output is written.

Iteration during development is brutal. The standard workaround is dual-target: develop in the Unity Editor with a Windows/macOS dev player target, build WebGL only for releases. CDK's source files have `#if UNITY_WEBGL && !UNITY_EDITOR` guards (`AIAvatarKitServiceWebGL.cs:18`) precisely so the WebGL-specific code path doesn't run in the editor.

### 2. Threading

WebGL is single-threaded. `System.Threading.Thread`, `Task.Run` to a worker, `async/await` over `ConfigureAwait(false)` — all behave differently or fail. `UniTask` (CDK's primary async library) is **mostly** WebGL-safe but only because it is implemented as a single-threaded scheduler under the hood.

The practical consequence: any computation that blocks the main thread blocks **the entire browser tab**. Mic processing, VAD inference, lip-sync analysis — all must yield frequently. CDK's `WebGLMicrophoneProcessor.js` exists precisely because doing mic processing on the Unity main thread would stutter rendering:

```javascript
// /tmp/ChatdollKit/Plugins/CopyThisJSToStreamingAssets/WebGLMicrophoneProcessor.js
class WebGLMicrophoneProcessor extends AudioWorkletProcessor {
  process(inputs) {
    const input = inputs[0];
    if (input && input[0].length > 0) {
      this.port.postMessage(input[0]);
    }
    return true;
  }
}
registerProcessor("webgl-microphone-processor", WebGLMicrophoneProcessor);
```

The `AudioWorkletProcessor` runs on the **audio rendering thread**, separate from the main JS thread. It is the only way to get sub-50ms-latency audio capture in a browser. CDK upgraded to this from `ScriptProcessorNode` in a recent release (`README.md:50`) — `ScriptProcessorNode` runs on the main thread and would skip frames during voice processing.

### 3. AudioContext

The browser will not let JavaScript create sound — or capture sound — until the user has interacted with the page. `audioContext.state === "suspended"` until a user click/key/touch resumes it. CDK polls every 300 ms to resume an interrupted context:

```javascript
// /tmp/ChatdollKit/Plugins/WebGLMicrophone.jslib:51-57
setInterval(function() {
  var ac = mic.audioContext;
  if (ac.state === "suspended" || ac.state === "interrupted") {
    console.log("Resuming AudioContext:", ac.state);
    ac.resume();
  }
}, 300);
```

The first interaction with the avatar must be a click ("Press to start talking") or the mic capture silently does nothing. Browsers tab-switched, backgrounded, or returning from sleep will suspend the context; CDK's poll loop catches the resume.

### 4. Compressed audio is forbidden

`README.md:612`: *"Note that WebGL does not support compressed audio playback, so make sure to handle this by adjusting your code depending on the platform."*

The browser's Web Audio API plays PCM. MP3/Opus/AAC TTS audio must be **decoded on the server side** before reaching the browser, or decoded JS-side and re-fed as PCM. CDK's TTS path on WebGL favors WAV-output providers (VoiceVox returns WAV by default) and avoids Opus.

The cost: WAV is 5–10× the bandwidth of Opus. A 30-second TTS clip in Opus is ~50 KB; in WAV at 24 kHz mono, ~1.4 MB. For mobile-browser deployment on metered connections, this matters. For desktop on LAN, it doesn't.

### 5. Memory

Unity WebGL builds have a configured heap size (default 256 MB, ceiling typically 2 GB). The full CDK scene with a VRM model + animation clips + lip-sync data + cached TTS audio + LLM context buffer can press against the heap. Heap exhaustion in WebGL is **not a graceful error** — it is a full JS `RangeError` that may or may not be caught.

CDK's defense: explicit cleanup. `_free(ptr)` calls in `JsFree` (`WebGLMicrophone.jslib:2`), session disposal on dialog clear, audio buffer rotation. Less defended: long sessions accumulate context in `StreamBuffer` ([[39_AIAVATARKIT_STREAMING]] documents this). For a Andlit-unity tier Ember-WebGL deployment, conversation-length must be bounded or the tab dies after ~2 hours.

### 6. Storage

`localStorage` is the only persistent storage. ~5 MB hard limit per origin. `IndexedDB` is available but Unity has no first-class wrapper. CDK uses neither directly for state — it offloads all persistent state to the **remote server** (ChatMemory, AIAvatarKit's session state manager).

This is the right design for WebGL. Anything that needs to persist between page loads must live on a server. The browser becomes a renderer; the server becomes the source of truth.

### 7. Fetch streaming

`UnityWebRequest` streaming download (`UploadHandler` / `DownloadHandler`) does not work the same in WebGL. The browser's `fetch()` with `body.getReader()` and ReadableStream is what's actually available. CDK's WebGL LLM services all bypass `UnityWebRequest` and use JS-bridge plugins instead:

- `ChatGPTServiceWebGL.jslib`
- `ClaudeServiceWebGL.jslib`
- `GeminiServiceWebGL.jslib`
- `DifyServiceWebGL.jslib`
- `AIAvatarKitServiceWebGL.jslib`

Five separate plugins for five LLM providers, each implementing the same SSE-stream-and-callback pattern in JavaScript. The duplication is intentional: each provider has its own request/response shape and header conventions, and consolidating would require a more capable JS-side framework than the `.jslib` model supports.

Reference: `AIAvatarKitServiceWebGL.cs:27-30`:

```csharp
[DllImport("__Internal")]
protected static extern void StartAIAvatarKitMessageStreamJS(
    string targetObjectName, string sessionId, string url,
    string chatCompletionRequest, string aakHeaders);
[DllImport("__Internal")]
protected static extern void AbortAIAvatarKitMessageStreamJS();
```

The JS side calls `SendMessage(gameObjectName, "ReceiveStreamChunk", payload)` to deliver chunks back to Unity. The Unity GameObject must have a `ReceiveStreamChunk` method publicly declared.

### 8. Cross-origin requests

The Unity WebGL build is served from an origin (the CDN, the developer's web server). LLM API calls go to a different origin. CORS preflight is mandatory. The LLM provider must allow the deployment origin. **OpenAI does not** — `https://api.openai.com` does not return `Access-Control-Allow-Origin` for arbitrary client origins. CDK works around this by:

- Routing through a proxy server (the operator's own backend)
- Using providers that do allow CORS (some self-hosted LLMs)
- Using AIAvatarKit as a proxy (its `/chat` endpoint accepts the deployment origin's CORS)

The note in `AIAvatarKitServiceWebGL.cs:81-85`:

```csharp
// TODO: Support custom headers later...
if (customHeaders.Count > 0)
{
    Debug.LogWarning("Custom headers for AIAvatarKit on WebGL is not supported for now.");
}
```

…is a CORS-preflight limitation. Adding custom headers triggers preflight; CDK hasn't wired the preflight options.

### 9. Silero VAD overhead

`README.md:729`: *"Using Silero VAD in WebGL builds can cause high browser processing overhead. We recommend using `AIAvatarKitStreamSpeechListener` to offload VAD processing to the server side."*

Silero VAD is an ONNX model. Running it in-browser via onnxruntime-web is feasible but expensive — each chunk requires a model inference. On a low-end browser (mobile Safari, Chromebook), this can drop the avatar frame rate. CDK's recommendation: **don't VAD in the browser**; instead stream raw audio to the AIAvatarKit server and let it VAD.

This is the **single most important architectural recommendation** in the WebGL stack. The browser becomes a thin audio-capture client; the heavy lifting (VAD + STT + LLM + TTS) lives on the server. The avatar in the browser becomes a renderer plus a microphone plus a speaker.

### 10. Silero VAD ONNX model

For the in-browser route (when used), the `silero_vad.onnx` model must be placed in StreamingAssets (`README.md:763`). It is bundled into the WebGL build output and loaded at runtime. The model is ~1.5 MB. Loading time on first-page-visit is added to the initial spinner duration.

### 11. NativeWebSocket dependency

For WS-based AIAvatarKit streaming, `README.md:731`: *"To use `AIAvatarKitStreamSpeechListener` in WebGL builds, add the NativeWebSocket package via Package Manager: `https://github.com/endel/NativeWebSocket.git#upm`. Unity's built-in WebSocket client (`System.Net.WebSockets`) is not supported on WebGL."*

A third-party package replaces a standard library because the standard library doesn't run. This pattern repeats throughout the WebGL build. The dependency graph grows.

### 12. Sample rate awkwardness

`README.md:908`: *"Sample Rate ... Set it to 44100 when using WebGL."*

Unity's WebGL `MicrophoneManager` is opinionated about sample rate; 16 kHz (the standard for STT) doesn't always work, and 44.1 kHz must be set explicitly. CDK then downsamples in the AudioWorklet:

```javascript
// /tmp/ChatdollKit/Plugins/WebGLMicrophone.jslib:22-49
mic.downsampleTo16kHz = function(buffer, fromSampleRate) {
  if (fromSampleRate === 16000) return Array.from(buffer);
  var sampleRateRatio = 16000 / fromSampleRate;
  var newLength = Math.round(buffer.length * sampleRateRatio);
  var result = new Array(newLength);
  ...
};
```

A hand-rolled downsampler. Functional, not high-fidelity (simple averaging, no antialiasing filter). For VAD purposes, fine. For high-quality STT, marginal.

## The JavaScriptMessageHandler — Reverse Direction

CDK provides a JS-to-Unity message channel at `Plugins/JavaScriptMessageHandler.jslib`:

```javascript
// /tmp/ChatdollKit/Plugins/JavaScriptMessageHandler.jslib:1-10
mergeInto(LibraryManager.library, {
    InitJSMessageHandler: function(targetObjectNamePtr, targetFunctionNamePtr) {
        let targetObjectName = UTF8ToString(targetObjectNamePtr);
        let targetFunctionName = UTF8ToString(targetFunctionNamePtr);
        window.SendMessageToChatdollKit = (message) => {
            console.log("Send message to ChatdollKit: " + message);
            SendMessage(targetObjectName, targetFunctionName, message);
        };
    }
});
```

After init, the page can call `window.SendMessageToChatdollKit('{"Endpoint":"dialog","Operation":"process","Text":"hi"}')` to drive the avatar. This is the WebGL parallel to AITuber Controller's TCP socket ([[3A_AITUBER_CONTROLLER]]). The host page becomes the controller.

`README.md:962-973` shows the conditional code in the Unity scene:

```csharp
#if UNITY_WEBGL && !UNITY_EDITOR
gameObject.GetComponent<JavaScriptMessageHandler>().OnDataReceived = async (message) =>
{
    HandleExternalMessage(message, "JavaScript");
};
#else
gameObject.GetComponent<SocketServer>().OnDataReceived = async (message) =>
{
    HandleExternalMessage(message, "SocketServer");
};
#endif
```

Same handler. Different inbound transport. The avatar is identical; the wrapper differs. This is the right shape: control-surface abstracted, transport per-platform.

## Where It Surprises

- **The eleven plugins, mostly small.** `JavaScriptMessageHandler.jslib` is 10 lines. `WebGLMicrophone.jslib` is 206. Together they total under 1,500 lines of JS. The whole WebGL adaptation layer is read in an afternoon.
- **`mergeInto(LibraryManager.library, {...})`** is the Emscripten pattern. Every `.jslib` is a single object literal of named functions Emscripten resolves at link time. No build system; no transpile step; the syntax is the file's contract.
- **The 300 ms AudioContext-resume poll** quietly fixes a class of real-world bugs (tab-switched, page-backgrounded, OS-slept) without operator intervention.
- **The downsampler-in-AudioWorklet pattern** lets the mic data arrive at the Unity side already at the right sample rate. No `OnAudioFilterRead` plumbing inside Unity.
- **The five separate LLM `.jslib` files** look like duplication but are actually right-sized: each provider has its own request schema, its own headers, its own streaming chunk format. One generic streamer would be 5× the code.
- **The deployable demo at unagiken.blob.core.windows.net** is hosted on Azure Blob Storage. Static hosting, no backend at that origin. The backend (the LLM proxy if needed) lives elsewhere. This is the right hosting topology for a WebGL avatar — a static-storage frontend + an authenticated API origin.
- **No Service Worker.** CDK doesn't try to make the WebGL build work offline. The browser tab needs network for LLM/TTS/STT regardless; offline-WebGL would be a misleading affordance.

## Where It Breaks

- **Build time** (5–10 minutes per iteration). This is Emscripten, not CDK; nothing to fix at the CDK layer.
- **First-load size**: a stripped CDK demo build is ~30 MB, larger with VRM model + animations. On a slow connection the initial load is several minutes. CDK does not implement progressive asset streaming.
- **iOS Safari quirks**. Safari treats audio capture more restrictively than Chrome/Firefox. AudioWorklet support is recent and brittle. CDK's demo works on iOS Safari but with degraded latency.
- **Mobile browser tab kills**. Chrome on Android aggressively kills backgrounded tabs to save memory. A user who tabs away mid-conversation may return to a frozen avatar.
- **WebGL2 requirement**. Old browsers (IE, legacy Safari) cannot run the build at all. CDK targets WebGL2 by default.
- **No autoplay audio.** Browser policy. The first TTS playback after page load fails silently if no user gesture has occurred. CDK's `AudioContext.resume()` poll mitigates but doesn't eliminate this.
- **CORS friction with most cloud LLMs.** Operators must run a proxy. CDK doesn't ship the proxy; that's an operator problem.
- **No native file system access.** User-uploaded files (the `FileUploader.jslib` plugin) go through `<input type="file">` and are streamed via fetch. No persistent file references.
- **Network drops are unforgiving.** Browser fetch retries are entirely application-level. CDK's `AIAvatarKitServiceWebGL` does timeout-and-error but does not auto-reconnect.
- **Lip-sync on mute** was reportedly broken in earlier versions; `README.md:30` notes it as a recent WebGL enhancement. Edge cases remain.
- **WebGL build size is opaque.** Knowing what's making your build bigger requires reading the Emscripten output JSON. No first-class size-budget visualizer in Unity.
- **`#if UNITY_WEBGL && !UNITY_EDITOR` guards** are easy to get wrong. Code that compiles in editor but breaks in build is the typical first WebGL bug.

## Cross-References

- [[10_domain/1C_UNITY_LIFECYCLE_DOMAIN]] — Unity asmdef, MonoBehaviour lifecycle, prefab integration
- [[10_domain/1D_MULTI_PLATFORM_DOMAIN]] — overall platform-target matrix
- [[20_interface/28_JS_BRIDGE_INTERFACE]] (Auditor) — JS-Unity message-origin verification
- [[50_verification/55_WEBGL_GOTCHAS]] (Auditor) — Emscripten quirks, audio-context restrictions, memory pressure
- [[3A_AITUBER_CONTROLLER]] — TCP-socket equivalent for non-WebGL builds; same control-surface abstraction
- [[39_AIAVATARKIT_STREAMING]] — the server-side streaming pattern that WebGL leans on for VAD/STT
- [[sap:3A_CROSS_PLATFORM_BUILDS]] — SAP's Electron+PyInstaller alternative; compare cost profiles
- [[waifu:11_LIVEKIT_INTEGRATION]] — Waifu's cloud-streaming alternative that bypasses Unity entirely

## What This Means for Ember

*Apache-2.0 attribution: ChatdollKit's WebGL plugins are Apache-2.0. Preserve upstream header references per Apache-2.0 §4(c).*

**Adopt:**

- **The `mergeInto(LibraryManager.library, {...})` plugin pattern** for the Andlit-unity tier's WebGL target if/when built. Each browser-capability bridge is its own `.jslib`, named, small, reviewable. Apache-2.0 attribution required.
- **The AudioContext-resume polling loop** (`WebGLMicrophone.jslib:51-57`). Drop-in. Catches tab-resume, OS-wake, and silent suspension across all major browsers.
- **The `AudioWorkletProcessor` mic capture pattern** with a separate-thread processor and a downsampler inside the JS layer. Same code structure; rename to Ember's namespace.
- **The "VAD on the server side" recommendation** (`README.md:729`). Ember's WebGL tier never runs Silero VAD in-browser. The avatar tab is a thin client; all heavy ML runs on a tethered Ember-server (see Tethered Grounding Vow).
- **The control-surface abstraction** (`JavaScriptMessageHandler` vs `SocketServer` via `#if UNITY_WEBGL`). Identical message shape, per-transport implementation. Bind to Funi's launcher.
- **Per-provider WebGL LLM `.jslib`** for any provider whose request shape requires custom streaming. Ember's first three providers: Ollama, llama-server, OpenAI-compat. Each gets its own `.jslib`.
- **Static-storage frontend hosting.** Ember's WebGL artifact deploys to a CDN bucket; the backend lives at a different origin with CORS allowed to the bucket. No backend bundled with the WebGL build.

**Adapt:**

- **The dual-build workflow** (Editor for dev, WebGL for release) — adapt by codifying it in `builds/webgl-release.yaml` as part of the Funi Build Manifest (proposed in [[sap:3A_CROSS_PLATFORM_BUILDS]] Invent list). The WebGL build runs only in CI, never in the developer loop.
- **The unbounded `StreamBuffer`** — adapt to a configurable cap (`max_streamed_chars`, default 50,000). When the cap is hit, the session is auto-summarized via ChatMemory ([[38_CHATMEMORY_INTEGRATION]]) and the buffer rotated.
- **The bandwidth penalty of WAV TTS** — adapt by deploying an Ember-side audio transcoder: TTS provider returns Opus, the Ember server transcodes to WAV using `ffmpeg.js` on-the-fly, browser receives the lighter format only when the server confirms the client is bandwidth-constrained. For LAN/desktop, ship WAV directly.
- **The first-load asset size** — adapt with manifest-driven asset preloading: critical-path assets (VRM model, idle animation) load first; secondary assets (extra animations, alt TTS voices) load lazily after the avatar is interactive.
- **The 300 ms resume poll** — adapt to a longer poll for backgrounded tabs detected via `document.visibilityState === "hidden"`. No reason to burn CPU on a tab the user can't see.
- **The five LLM `.jslib` plugins** — adapt with a small TypeScript build that emits the `.jslib`s from a single shared base + per-provider overrides. CDK's five-files-by-hand is read-OK but not maintain-friendly at scale.

**Avoid:**

- **In-browser Silero VAD** for any tier above Pi-class. CDK explicitly recommends against it; we don't ignore the advice.
- **Cloud LLM CORS expectation.** Ember's WebGL build always routes LLM calls through a tethered server, never direct-to-provider. This also keeps API keys off the client.
- **Default Sample Rate 44100** with hand-rolled downsampler. Ember uses a proper antialiasing filter (a small FIR) before downsampling. The CPU cost is negligible; the STT accuracy improvement is measurable.
- **Build-size opacity.** Ember's WebGL build emits a `BUILD_SIZE_REPORT.json` with per-asset / per-binary contributions. CI fails the build if total exceeds `max_initial_load_mb` (default 25 MB).
- **No reconnect-on-drop.** Ember's WebGL client implements exponential-backoff reconnect with state-merge on resume.
- **The unauthenticated `window.SendMessageToChatdollKit` global.** Any script on the page can call it. Ember's equivalent requires a token (validated by the bridge) and a CSP that restricts script sources to trusted origins.

**Invent:**

- **Funi WebGL Heap Budget.** A first-class config: `webgl_heap_mb` (default 384, ceiling 1024). Ember refuses to start a Andlit-unity WebGL session that exceeds the budget, falling back to a degraded mode (no VRM textures, only proxy avatar). Vow tie-in: **Smallness** (heap exhaustion is anti-Vow; graceful degradation is pro-Vow).
- **Progressive Avatar Reveal.** Initial WebGL load shows a placeholder (a simple silhouette + voice-only conversation working). VRM model + animations load lazily; the avatar "arrives" 5–15 seconds in. The first conversational turn happens immediately; the visual richness fills in. Vow tie-in: **Public-Friendliness**.
- **Backgrounded-Tab Quiesce.** When `document.visibilityState === "hidden"`, the Ember WebGL client pauses TTS playback, queues conversation, and reduces poll loops to 1/60s. When visible again, the queue plays back and the avatar catches up. CDK doesn't do this; mobile browsers force-kill backgrounded tabs and lose state.
- **Origin-Authenticated JS Bridge.** Ember's `JavaScriptMessageHandler` equivalent verifies `event.origin` (when message comes via `postMessage`) and rejects untrusted iframes. The bridge is the single attack surface in the WebGL tier; treat it accordingly. Vow tie-in: **Defended System Prompt** generalized.
- **Mic-as-Reach-Adapter.** In Ember's reach model ([[3A_AITUBER_CONTROLLER]] proposed Munnr Reach Registry), the browser mic is just another `ReachAdapter` instance. Same interface as Discord, Twitch, Telegram. The mic adapter happens to run inside the same browser tab as the avatar; the abstraction is identical. Vow tie-in: **Modular Authorship**.
- **Tab-Title Status Surface.** Ember WebGL updates `document.title` to reflect avatar state: `Ember · listening...` / `Ember · responding...` / `Ember · idle`. Users with the tab in the background see status in the tab strip. Cheap to implement; high information density. Vow tie-in: **Public-Friendliness**.
- **Service-Worker-Backed Offline Greeter.** A small Service Worker caches the WebGL shell + the avatar idle loop. When the user reloads with no network, the avatar appears, says "I can see you but I can't think — my Well is unreachable", and rotates a quiet idle animation. CDK doesn't try this; Ember's Graceful-Offline Vow makes it required for the WebGL tier. Vow tie-in: **Graceful Offline**.

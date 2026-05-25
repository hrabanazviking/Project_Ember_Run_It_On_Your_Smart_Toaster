---
codex_id: 28_JS_BRIDGE_INTERFACE
title: JS Bridge Interface — A Window-Global Function That Any Script On The Page Can Call, And Six More LLM-Specific Bridges Beside It
role: Auditor
layer: Interface
status: draft
chatdoll_source_refs:
  - Scripts/IO/JavaScriptMessageHandler.cs:10-54
  - Plugins/JavaScriptMessageHandler.jslib
  - Plugins/ChatGPTServiceWebGL.jslib
  - Plugins/ClaudeServiceWebGL.jslib
  - Plugins/GeminiServiceWebGL.jslib
  - Plugins/DifyServiceWebGL.jslib
  - Plugins/AIAvatarKitServiceWebGL.jslib
  - Plugins/WebGLMicrophone.jslib
  - Plugins/SimpleCameraWebGL.jslib
  - Plugins/WebGL/FileUploader.jslib
  - Scripts/IO/ExternalInboundMessage.cs:5-12
ember_subsystem_targets: [Funi, Munnr, Strengr, Andlit]
cross_refs:
  - 20_interface/27_SOCKET_PROTOCOL
  - 50_verification/51_SECURITY_REVIEW
  - 50_verification/55_WEBGL_GOTCHAS
  - 50_verification/57_FAILURE_TAXONOMY
  - 30_execution/3B_WEBGL_BUILD
  - waifu:25_DATA_CHANNEL
  - sap:18_LOCALHOST_API_DOMAIN
---

# JS Bridge Interface — A Window-Global Function That Any Script On The Page Can Call, And Six More LLM-Specific Bridges Beside It

> *Sólrún, voice cold and even: the JS-bridge surface is the WebGL counterpart to the SocketServer audited in `[[27_SOCKET_PROTOCOL]]`. It exists because Unity WebAssembly cannot bind a TCP socket — the browser will not let it. Where the desktop tier opens a TCP listener bound to `IPAddress.Any`, the WebGL tier installs a function on `window` and waits for the page to call it. The functions are equivalents in shape — both accept `ExternalInboundMessage` JSON, both dispatch through the same `IExternalInboundMessageHandler.OnDataReceived` hook — but the threat model is different. The TCP socket is exposed to the LAN; the JS bridge is exposed to whatever JavaScript runs on the page. In a normal SPA, that means: the operator's own scripts (legitimate), third-party analytics tags (semi-legitimate), browser extensions injecting content scripts (operator-deniable), and any cross-origin XSS the page suffers. The CDK does not verify origins. It does not check message signatures. It does not consult a window allowlist. It registers one window-global named `SendMessageToChatdollKit` and trusts whoever calls it.*
>
> *Beyond the message bridge there are six more JSLIB plug-ins, each of which connects a CDK service to a Web API. Five of them ship LLM API keys into the browser as fetch URL/header arguments — every key is visible in DevTools Network panel the moment a request fires. The seventh, `WebGLMicrophone.jslib`, hands the microphone audio to an AudioWorklet and runs an optional VAD in JS. This document audits all nine bridges as one interface family.*

This document audits the WebGL bridge surface in two layers: the *control bridge* (`JavaScriptMessageHandler.jslib` + `JavaScriptMessageHandler.cs`) that mirrors the SocketServer protocol, and the *service bridges* (one per LLM provider plus mic/camera) that move credentialed I/O across the wasm/JS boundary. The deeper WebGL gotchas — AudioContext gestures, single-threading, memory pressure — live in `[[55_WEBGL_GOTCHAS]]`. Here I focus on the *contract* of each bridge: what it accepts, what it leaks, what it cannot defend.

---

## 1. The Control Bridge — Three JS Functions, One C# Method

### 1.1 The JSLIB Side

`/tmp/ChatdollKit/Plugins/JavaScriptMessageHandler.jslib`:

```javascript
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

Ten lines. The shape:

1. C# calls `InitJSMessageHandler(gameObject.name, "HandleMessageFromJavaScript")` at `JavaScriptMessageHandler.cs:31`.
2. The JSLIB function reads the two `char*` pointers, decodes UTF-8, and installs `window.SendMessageToChatdollKit` as a callable.
3. Any subsequent `window.SendMessageToChatdollKit("<json-string>")` invokes Unity's `SendMessage(targetObjectName, targetFunctionName, message)` — the Emscripten-side call that bridges JS strings to C# `MonoBehaviour` methods.

`window.SendMessageToChatdollKit` is a **window-global**. There is no namespace, no event-target wrapper, no `postMessage` requirement, no origin assertion. The function is callable by:

- The host page's own scripts (intended).
- Any third-party `<script>` the host page loads (analytics, ads, CDN-hosted libraries).
- Any browser extension's content script. Most extensions inject scripts into pages; those scripts have full DOM/window access. The user's browser extensions are an *unmodeled trust boundary*.
- Any iframe with `top.SendMessageToChatdollKit` access — i.e., an iframe whose ancestors are same-origin with the CDK host page.
- Any persisted-XSS-injected payload, which by definition runs in page context with full window access.
- Any code injected via dev-tools console, which is a trust boundary the operator should care about (a streamer sharing screen with dev-tools open is one F12 away from a viewer-readable attack vector).

**There is no origin check.** `window.SendMessageToChatdollKit` is symmetrically callable by all of the above. The bridge has no way to know whether the caller is the legitimate operator script or a malicious actor.

The `console.log` of the message (`:6`) is also a finding: every message that traverses the bridge is logged to the browser console. If the message contains sensitive content (the operator's typed dialog input, a system-prompt update), it ends up in the F12 console history. A screen-share captures it. A `console.log` of an `api_key` payload in a `Demo08` deployment is broadcast.

### 1.2 The C# Side

`/tmp/ChatdollKit/Scripts/IO/JavaScriptMessageHandler.cs:10-54`:

```csharp
public class JavaScriptMessageHandler : MonoBehaviour, IExternalInboundMessageHandler
{
    public Func<ExternalInboundMessage, UniTask> OnDataReceived { get; set; }

#if UNITY_WEBGL
    [DllImport("__Internal")]
    private static extern void InitJSMessageHandler(string targetObjectName, string targetFunctionName);

    [SerializeField]
    private bool captureKeyboardInput = true;
    [SerializeField]
    private bool isDebug;

    public void Start()
    {
#if !UNITY_EDITOR
        if (captureKeyboardInput)
        {
            WebGLInput.captureAllKeyboardInput = false;
        }
        InitJSMessageHandler(gameObject.name, "HandleMessageFromJavaScript");
#endif
    }

    public void HandleMessageFromJavaScript(string message)
    {
        try
        {
            if (isDebug) { Debug.Log($"Received from JavaScript: {message}"); }
            var jsMessage = JsonConvert.DeserializeObject<ExternalInboundMessage>(message);
            OnDataReceived?.Invoke(jsMessage);
        }
        catch (Exception ex)
        {
            Debug.LogError($"Error at HandleMessageFromJavaScript: {ex.Message}");
        }
    }
#endif
}
```

Forty-five lines including braces. The full C# surface.

`HandleMessageFromJavaScript(string message)` is the Unity-side endpoint. Emscripten dispatches the JS string here. The method:

1. Optionally logs (if `isDebug`).
2. Deserializes via Newtonsoft (default settings — same safety properties as `SocketServer`'s deserialization, see `[[27_SOCKET_PROTOCOL §2]]`).
3. Invokes `OnDataReceived` with the typed message.

`OnDataReceived` is the same hook the SocketServer uses. **Whatever handler consumes SocketServer messages also consumes JS bridge messages.** The `AITuberMessageHandler` from `[[27_SOCKET_PROTOCOL §4]]` — including the `llm/activate`-reassigns-api-key-from-wire operation — fires identically when the JS bridge submits the message.

The `captureKeyboardInput = true` toggle (`:19`) sets `WebGLInput.captureAllKeyboardInput = false` at startup. This is unrelated to the message protocol but tells the operator "yes, the page above this canvas can receive keyboard events" — usually correct for chat-doll WebGL deployments embedded in a larger page.

---

## 2. The Six Service Bridges

`Plugins/` contains five `*ServiceWebGL.jslib` files plus the microphone and camera bridges. Each is a fixed-shape JS function that bridges one CDK service to one Web API.

### 2.1 The LLM Service Bridges — Five Of A Kind

`Plugins/ChatGPTServiceWebGL.jslib`, `ClaudeServiceWebGL.jslib`, `GeminiServiceWebGL.jslib`, `DifyServiceWebGL.jslib`, `AIAvatarKitServiceWebGL.jslib` are structurally identical. Each exposes two functions:

| Function | Signature | Effect |
|---|---|---|
| `*ChatCompletionJS` / `Start*MessageStreamJS` | `(targetObjectNamePtr, sessionIdPtr, urlPtr, apiKeyPtr, requestBodyPtr)` | Fires a `fetch` to the provider with the API key in the URL or header, reads the streamed response chunk by chunk, calls back to C# with each chunk |
| `Abort*JS` | `()` | Aborts the in-flight `fetch` via an `AbortController` stored on `document.{provider}AbortController` |

The ChatGPT case (`Plugins/ChatGPTServiceWebGL.jslib`):

```javascript
ChatCompletionJS: function(targetObjectNamePtr, sessionIdPtr, urlPtr, apiKeyPtr, chatCompletionRequestPtr) {
    let targetObjectName = UTF8ToString(targetObjectNamePtr);
    let sessionId = UTF8ToString(sessionIdPtr);
    let url = UTF8ToString(urlPtr);
    let apiKey = UTF8ToString(apiKeyPtr);
    let chatCompletionRequest = UTF8ToString(chatCompletionRequestPtr);

    if (document.chatGPTAbortController == null) {
        document.chatGPTAbortController = new AbortController();
    }

    fetch(url, {
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${apiKey}`,
            "api-key": `${apiKey}`
        },
        method: "POST",
        body: chatCompletionRequest,
        signal: document.chatGPTAbortController.signal
    })
    .then(response => { ... })
    .then((reader) => {
        const readChunk = function({done, value}) {
            if(done) { ... return; }
            SendMessage(targetObjectName, "SetChatCompletionStreamChunk", sessionId + "::" + decoder.decode(value));
            reader.read().then(readChunk);
        }
        reader.read().then(readChunk);
    })
    .catch((err) => { console.error(`Error at fetch: ${err.message}`); });
}
```

**The API key is decoded from the wasm heap into a JS string and used in two HTTP headers**: `Authorization: Bearer {apiKey}` and `api-key: {apiKey}` (the second is the Azure-OpenAI compatibility header). The DevTools Network panel sees both. The first request a user makes after page load leaks the key in plain text.

The Gemini case is worse — the key is in the URL query string (`fetch(url + "?key=" + apiKey, ...)`). DevTools, browser referrer headers (for any subresource the response page loads), and any logged-response capture see the key.

The Claude case is technically correct on protocol — it sends `anthropic-version`, `anthropic-beta`, `anthropic-dangerous-direct-browser-access: true`, and `x-api-key`. The `anthropic-dangerous-direct-browser-access: true` header is Anthropic's explicit "the developer is aware that browser-direct API access leaks keys" opt-in. CDK sets it. The header name is the documentation of the threat model. CDK opts in anyway.

The streaming chunk delivery (`readChunk` recursion) calls back into Unity for every chunk via `SendMessage(targetObjectName, "SetChatCompletionStreamChunk", sessionId + "::" + chunk)`. The `sessionId + "::"` prefix is the wire convention for routing chunks to the right pending request. The double-colon delimiter is the lightweight namespacing CDK invented; it works as long as the chunk text never contains `::` at the start. For LLM output that emits `::` (rare but possible — markdown table syntax, code with namespace operators), the parser splits incorrectly. *[unverified — I have not exhaustively tested the chunk-parser's edge cases.]*

The five LLM bridges duplicate this pattern with minor variations. The abort controllers are stashed on `document.<provider>AbortController` as window-globals. Any script on the page can `document.chatGPTAbortController.abort()` and kill an in-flight LLM call. This is a denial-of-service surface for any malicious script on the page, no auth required.

### 2.2 The Microphone Bridge

`Plugins/WebGLMicrophone.jslib` is the most substantial of the bridges — 180+ lines. It exposes:

- `InitWebGLMicrophone(targetObjectNamePtr, useMalloc)` — sets up the AudioContext, AudioWorklet, downsampling helpers, and VAD buffer.
- `StartWebGLMicrophone()` — calls `navigator.mediaDevices.getUserMedia({audio: {echoCancellation, noiseSuppression, channelCount: 1}})`, connects through an `AudioWorkletNode` that drains samples into a JS buffer, which then chunks to Unity via `SendMessage(mic.targetObjectName, "SetSamplingData", ...)`.
- `EndWebGLMicrophone()` — disconnects everything.
- VAD helpers: `IsVoiceDetected()`, `GetVoiceProbability()`, `IsVADEnabled()`, `SetVADThreshold(threshold)`, `GetVADThreshold()`.

The interesting detail: `mic.audioContext = new (window.AudioContext || window.webkitAudioContext)()` at JSLIB-init time. The AudioContext is created *immediately* on bridge install. Chrome/Firefox/Safari put it in `suspended` state until the user gestures. The kit polls `mic.audioContext.state` every 300ms (`:55-60`):

```javascript
setInterval(function() {
    var ac = mic.audioContext;
    if (ac.state === "suspended" || ac.state === "interrupted") {
        console.log("Resuming AudioContext:", ac.state);
        ac.resume();
    }
}, 300);
```

The polling tries to resume the context every 300ms. It will fail until the user has gestured. After the first gesture, the resume succeeds and the polling continues to harmlessly call `resume()` on an already-running context. This is the kit's workaround for the user-gesture requirement. Not elegant — a one-shot `addEventListener('click', resume)` would be the standard pattern — but it works.

The VAD-side integration (`:69-89`) checks `window.vad` (an external library the operator must include separately — `vad-web` or equivalent) and uses it to set `mic.isVoiceDetected` and `mic.voiceProbability`. Unity polls these via the IsVoiceDetected DllImport calls. The VAD is gated by buffer chunks of 512 samples downsampled to 16kHz. This is the same shape SileroVAD uses on native.

The downsampling code (`:25-50`) is a hand-rolled linear-interpolation resampler. It produces approximate 16kHz from arbitrary sample rates. For pristine STT this is mediocre quality (the standard recommendation is sinc-windowed resampling); for VAD it is more than sufficient.

### 2.3 The Camera Bridge

`Plugins/SimpleCameraWebGL.jslib` is small — 28 lines, one function:

```javascript
GetCameraDevices: function(targetObjectNamePtr, targetFunctionNamePtr) {
    // ...
    async function getCameraNames() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            stream.getTracks().forEach(track => track.stop());
            const devices = await navigator.mediaDevices.enumerateDevices();
            const cameras = devices.filter(device => device.kind === "videoinput");
            const cameraNames = [];
            for (const camera of cameras) {
                if (camera.label) cameraNames.push(camera.label);
            }
            SendMessage(targetObjectName, targetFunctionName, JSON.stringify({names: cameraNames}));
        } catch (error) { ... }
    }
    getCameraNames();
}
```

The function requests video permission, immediately stops the stream, and enumerates devices to return their labels. The permission request is a one-shot to *get the labels visible* — without `getUserMedia` consent, `enumerateDevices()` returns empty labels per the Web spec. The kit handles this correctly.

But: this triggers a camera permission prompt at app start (or whenever an operator's UI calls into `GetCameraDevices`). The user sees "this page wants to use your camera" and grants. CDK's actual camera usage in `Scripts/IO/SimpleCamera.cs` runs separately — that one captures and sends frames to the LLM via base64.

There is no JS-side or C#-side check that the user *understands* what they're granting. The camera permission stays granted until the user manually revokes via browser site settings. The avatar can capture-and-send images at will. *[The image-to-LLM path is its own audit — see `[[51_SECURITY_REVIEW]] §5.4` for the analog mic-permission analysis.]*

### 2.4 The File Uploader Bridge

`Plugins/WebGL/FileUploader.jslib` provides `OpenFileDialog(gameObjectName, methodName, accept)` for image upload. It creates an `<input type="file">`, listens for the file change, resizes the image to max 640px (image-only path), base64-encodes the resized JPEG, and `SendMessage`s back. Sixty-two lines, scoped to images.

The 640px resize is a thoughtful detail — Emscripten's `SendMessage` callback size is bounded; large base64 payloads can exceed the limit and silently drop. CDK pre-resizes to fit.

The bridge is consent-gated by the file picker — the user explicitly chooses the file. No origin check is needed; the file picker is the consent.

---

## 3. The Origin-Verification Gap

Every bridge listed above lacks an origin check. The legitimate use case is: the operator's host page loads the Unity WebGL bundle, the operator's host-page scripts call `window.SendMessageToChatdollKit(...)`, the avatar reacts. The expected control plane is *first-party page scripts*.

The threat surface is: anything else with window access. Notably:

- **Cross-origin iframes whose parents call into them.** If the CDK Unity canvas is embedded as `<iframe>` and the parent page sends `iframe.contentWindow.SendMessageToChatdollKit(...)`, it works. The parent page's origin is not the CDK's origin; the protection — same-origin policy — does not apply because the parent has `contentWindow` access. The fix is `window.postMessage` with `event.origin` validation on the receiver. CDK does not use `postMessage`.
- **Browser extension content scripts.** Extensions inject content scripts that run in the page context with full DOM access. Even when the extension is *user-installed* (legitimate), its content scripts effectively act as another origin. CDK trusts them.
- **Third-party scripts the host page loads.** Analytics tags, A/B testing frameworks, CDN-hosted libraries — each shares the window object. CDK trusts them.
- **XSS payloads.** If the host page suffers reflected/stored XSS, the injected script has `window` access. Every CDK control-plane operation becomes XSS-exploitable.

The correct shape for a browser-side bridge:

```javascript
window.addEventListener('message', (event) => {
    const allowedOrigins = ['https://operator.example'];
    if (!allowedOrigins.includes(event.origin)) return;
    const bearerValid = verifyBearer(event.data.bearer);
    if (!bearerValid) return;
    SendMessage(targetObjectName, "HandleMessageFromJavaScript", JSON.stringify(event.data.message));
});
```

`postMessage`-with-origin-check plus a bearer makes the bridge selective. CDK installs a callable global. The two are not equivalent.

---

## 4. The Newtonsoft Configuration

`JavaScriptMessageHandler.HandleMessageFromJavaScript` at `:44` deserializes via `JsonConvert.DeserializeObject<ExternalInboundMessage>(message)` with default settings. **`TypeNameHandling` is not enabled** here — same as the SocketServer path. The deserializer is safe in the gadget-chain sense.

The kit's polymorphic-deserialization danger (`TypeNameHandling.All` in `ChatGPTService.cs:37-40`) does *not* reach the bridge inbound path. The bridge accepts only the typed `ExternalInboundMessage` shape. **The bridge's deserialization is safe; the bridge's authorization is not.**

---

## 5. The Latency

Bridge round-trip is in microseconds. `window.SendMessageToChatdollKit("...") → Emscripten SendMessage → C# HandleMessageFromJavaScript → OnDataReceived` is a single in-process call. The dispatch is faster than the SocketServer's main-thread queue drain (which waits for the next frame's `Update`).

The cost is in the actual handler (`AITuberMessageHandler.HandleExternalMessage`, ~200 lines of dispatch). The bridge itself adds no measurable latency.

The streaming LLM bridges have higher per-chunk overhead: each chunk pays one JS→Wasm `SendMessage`, which is microseconds but accumulates. For a 1000-chunk streamed response, the overhead is single-digit milliseconds total. Negligible.

---

## 6. The Cross-References

- `[[27_SOCKET_PROTOCOL]]` — the desktop counterpart with the same `ExternalInboundMessage` shape.
- `[[51_SECURITY_REVIEW §3.2, §5.1 (WebGL paragraph)]]` — the STRIDE read on this bridge.
- `[[55_WEBGL_GOTCHAS §2, §5]]` — the AudioContext gesture trap, the key visibility in DevTools, the build-time tail.
- `[[3B_WEBGL_BUILD]]` — Forge-B's execution-side read on building and shipping a CDK WebGL bundle.
- `[[waifu:25_DATA_CHANNEL]]` — Waifu's LiveKit data channel — alternative authenticated browser-to-cloud control path.
- `[[sap:18_LOCALHOST_API_DOMAIN]]` — SAP's localhost HTTP API with fossil-string auth — alternative control plane that does at least require a magic-string.

---

## What This Means for Ember

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c).*

**Adopt:**

- **The `IExternalInboundMessageHandler` abstraction** that lets SocketServer and JavaScriptMessageHandler share the `OnDataReceived` hook. (`IExternalInboundMessageHandler.cs:6-10`, Apache-2.0 attribution required.) Ember's control plane should similarly let any transport (Tailnet TCP, WebSocket, JS bridge, MCP) feed into one typed handler.
- **The Emscripten DllImport + JSLIB-init pattern** for installing the JS-side handler with target-object/target-function pointer args. The shape itself is correct C-ABI Unity integration. The fix is to install a *receiver of `postMessage`* rather than a *callable window-global*.
- **The microphone bridge's AudioWorklet + chunked-callback architecture**. AudioWorklet replaces deprecated `ScriptProcessorNode` and is the correct shape for low-latency mic capture in WebGL. Adopt the structure; reject the polling-resume hack in favor of a one-shot gesture-bound resume (see Invent).
- **The streaming LLM bridges' AbortController pattern** for cancellation. Storing the controller on `document.<provider>AbortController` is the wrong place (window-global), but the pattern of attaching an abort signal to the fetch is correct.

**Adapt:**

- **The JSLIB `console.log` of inbound messages** at `JavaScriptMessageHandler.jslib:6`. Adapt to debug-gated logging that defaults to off in production builds.
- **The window-global controller stash** (`document.chatGPTAbortController`, etc.). Adapt to a closure-scoped singleton inside the JSLIB so the abort handle is not externally accessible.
- **The 640px image-resize at `FileUploader.jslib:18-46`.** Adapt to a configurable max-dimension and add HEIC/AVIF support for iPhone uploads.

**Avoid:**

- **`window.SendMessageToChatdollKit` as a window-global callable.** Use `window.addEventListener('message', handler)` with strict `event.origin` allowlist. The allowlist is operator-configured at build time.
- **API keys in JSLIB function arguments.** The five `*ServiceWebGL.jslib` files all decode the API key from wasm to a JS string and embed it in `fetch` URL or header. Every one is a DevTools-visible leak. Ember's WebGL tier must route every credentialed request through Strengr; the JSLIB never sees a real provider key.
- **`anthropic-dangerous-direct-browser-access: true`.** The header name is the documentation. Refuse to ship it.
- **Auto-trigger camera permission for device enumeration.** Ember's WebGL UI should make device-listing an explicit operator action, not a startup-time action.
- **The `::` double-colon stream-chunk delimiter** when chunks may legitimately contain `::`. Use a length-prefixed framing or JSON-line framing.
- **Polling-resume on AudioContext.** Replace with a one-shot click-handler that resumes once and clears itself.

**Invent:**

- A **`postMessage`-with-origin-and-bearer Bridge** for Ember's WebGL tier. The bridge listens on `window.message`, checks `event.origin` against an operator-configured allowlist baked at build time, verifies a `bearer` field in the message payload against a Strengr-issued session token, and only then dispatches. The bearer is short-lived (e.g. 5 minutes) and is rotated by the host page via a separate authenticated endpoint. CDK has no equivalent; the bridge is permissive by construction. Ember's bridge is restrictive by construction. Vow tie-in: **Surface Without Surveillance**, **Defended System Prompt**, **Tethered Grounding**.
- A **Bridge Capability Manifest.** Every JSLIB function declares at build time which message types it can dispatch (e.g., `dialog/process` only, never `llm/activate`). The Unity-side dispatcher refuses messages whose type is not in the bridge's manifest. The WebGL build linter (from `[[55_WEBGL_GOTCHAS]] Invent`) reads the manifest and refuses to ship a WebGL bundle that includes a `llm/activate`-capable bridge. Vow tie-in: **Capability-Scoped Surface**.
- A **Streaming Frame Protocol.** Replace CDK's `sessionId + "::" + chunkText` delimiter with a length-prefixed frame: `{8-byte-length}{json-line}` per chunk. JSON lines carry `{session_id, sequence_number, payload, eof}`. Out-of-order chunks become detectable; lost chunks become recoverable. CDK's protocol is "send raw text and hope." Ember's is framed. Vow tie-in: **Forge-Ready** (protocols that survive scaling), **Audit-Trail**.
- A **Gesture-Bound Audio Boot.** Replace the JSLIB's 300ms-polling-resume with: at JSLIB init, do nothing. On the first `pointerdown` or `keydown` anywhere on the page, create the AudioContext and call `resume()` once. Remove the listener. If the user has already gestured (e.g., the page was opened from a link click), fast-path. CDK's polling is a wasted ~3.3 calls/sec for the lifetime of the session; Ember's costs one event listener and one resume call total. Vow tie-in: **Smallness**.
- A **Per-Bridge Audit Log to Strengr.** Every bridge dispatch writes a structured record to a Strengr-backed audit endpoint (opt-in, operator-supplied URL). Includes `{timestamp, bridge_id, origin, bearer_hash, endpoint, operation, payload_hash}`. Operators auditing a WebGL deploy after a suspicious user report can correlate bridge dispatches with avatar behavior. CDK has nothing equivalent; WebGL deploys are an audit black hole. Vow tie-in: **Tethered Grounding**, **Audit-Trail-as-Return-Value**.
- A **Bridge Boot-Time Self-Test.** On first `window.message` reception, the bridge does *not* dispatch; it instead sends a `READY` confirmation back through `event.source.postMessage(...)` and waits for a signed challenge-response. This is a one-time handshake per page-load. CDK's bridge dispatches the first message with no handshake; Ember's refuses. Vow tie-in: **Defended System Prompt** generalized to **Defended Bridge**.

A final invent: **the WebGL Console Trap.** Ember's WebGL bridge installs a hidden Symbol-keyed property on `window` instead of a string-named callable. The operator's bootstrap script reads the Symbol via a build-time injected constant; cross-origin scripts and browser extensions cannot enumerate non-public Symbols and cannot reach the bridge. This is not security by obscurity *in addition to* the `postMessage` + bearer; it is defense-in-depth that closes the namespace-scanning attack. CDK exposes a discoverable global; Ember does not.

---

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c).*

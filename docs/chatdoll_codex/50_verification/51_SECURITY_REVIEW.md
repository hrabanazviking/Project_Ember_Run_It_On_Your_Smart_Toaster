---
codex_id: 51_SECURITY_REVIEW
title: Security Review — Keys In The Build, A Port Open To Anyone, A JS Bridge Without Origin
role: Auditor
layer: Verification
status: draft
chatdoll_source_refs:
  - Scripts/LLM/ChatGPT/ChatGPTService.cs:15
  - Scripts/LLM/Claude/ClaudeService.cs:15
  - Scripts/LLM/Gemini/GeminiService.cs:15-16,214
  - Scripts/LLM/Dify/DifyService.cs:16
  - Scripts/SpeechSynthesizer/OpenAISpeechSynthesizer.cs:30
  - Scripts/SpeechSynthesizer/AivisCloudSpeechSynthesizer.cs:29
  - Scripts/SpeechSynthesizer/NijiVoiceSpeechSynthesizer.cs:29
  - Scripts/SpeechListener/OpenAISpeechListener.cs:12
  - Scripts/SpeechListener/AzureSpeechListener.cs:14
  - Scripts/Network/SocketServer.cs:88
  - Scripts/Network/SocketServer.cs:156-195
  - Scripts/IO/JavaScriptMessageHandler.cs:35-51
  - Plugins/JavaScriptMessageHandler.jslib
  - Plugins/GeminiServiceWebGL.jslib
  - Demo/Demo08.unity
ember_subsystem_targets: [Funi, Munnr, Strengr, Rödd, Andlit]
cross_refs:
  - 50_verification/50_DEPENDENCY_HEALTH
  - 50_verification/55_WEBGL_GOTCHAS
  - 50_verification/57_FAILURE_TAXONOMY
  - 20_interface/27_SOCKET_PROTOCOL
  - 20_interface/28_JS_BRIDGE_INTERFACE
  - sap:53_SECURITY_REVIEW
  - waifu:51_SECURITY_AND_PRIVACY
---

# Security Review — Keys In The Build, A Port Open To Anyone, A JS Bridge Without Origin

> *Sólrún, voice cold and even: the Waifu codex named hardcoded API keys as that kit's single largest catastrophe. The ChatdollKit codex must now answer the same question, and the answer is materially the same. CDK does not hardcode keys in its demo source. It does worse. It exposes them as `public string ApiKey` fields on `MonoBehaviour` components, which Unity serializes into the scene YAML, then bakes into the AssetBundle when the operator builds for iOS, Android, WebGL, or any standalone target. The key ships inside the binary the operator distributes to end users. The architectural decision is the same as Waifu's; the surface differs; the catastrophe is identical.*
>
> *Beyond the keys, CDK opens a TCP socket on `IPAddress.Any` with no authentication, accepts arbitrary JSON-deserialized messages over it, hands the JS bridge a global `window.SendMessageToChatdollKit` function with no origin check, and configures Newtonsoft with `TypeNameHandling.All`. Each of these is independently a finding. Combined, they are the threat model.*

This document catalogs the security surface by STRIDE — Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege — across the LLM/TTS/STT credential surface, the SocketServer, the JavaScriptMessageHandler, the mobile and XR permission surfaces, and the Newtonsoft configuration. Per-finding I assign **Ember-must-reject** or **Ember-inherits-must-harden**.

The license posture is Apache-2.0. This means CDK's surface can be cited, adapted, and re-shipped under attribution. The license does not, however, change the threat model.

---

## 1. The Implicit Trust Model

CDK does not state a security posture. Inferred from the code:

- The kit runs **inside a Unity application** the operator builds and distributes. The application may run on the operator's desktop (Win/Mac/Linux), on an end-user's phone (iOS/Android), in a VR headset (Quest/Vision Pro), inside an AR app, or **inside a browser** as a WebGL build.
- All credentials are stored as **`public string ApiKey;` fields** on MonoBehaviour subclasses (`ChatGPTService.cs:15`, `ClaudeService.cs:15`, `GeminiService.cs:15`, `DifyService.cs:16`, `OpenAISpeechListener.cs:12`, eleven other places). Unity's serializer treats `public` fields as scene state and writes them to YAML when the operator saves the scene, then bakes them into the build artifact.
- The SocketServer binds `IPAddress.Any` (`SocketServer.cs:88`) — every interface, not just loopback — with **no authentication**, no TLS, no token, no source-IP allowlist.
- The JavaScriptMessageHandler installs `window.SendMessageToChatdollKit` (`Plugins/JavaScriptMessageHandler.jslib`) as a window-global with **no origin check**.
- The LLM is trusted to emit well-formed function-call payloads; CDK's `DialogProcessor` and the per-provider services dispatch `ITool` execution based on the LLM's stated `name` field.

The implicit posture: *trust the operator to never ship the build to anyone; trust the local network; trust the browser host; trust the LLM.* None survive any threat model. The first — trust the operator — is **falsified by the demo's own structure**, which encourages the operator to ship a Unity build to end users via the App Store, Google Play, itch.io, or a WebGL hosting URL.

---

## 2. The Surfaces, Listed

| Surface | File | What it exposes |
|---|---|---|
| ChatGPT API key | `Scripts/LLM/ChatGPT/ChatGPTService.cs:15` | `public string ApiKey;` — serialized into scene YAML, baked into AssetBundle |
| Claude API key | `Scripts/LLM/Claude/ClaudeService.cs:15` | Same pattern; `x-api-key` header at `:191` |
| Gemini API key | `Scripts/LLM/Gemini/GeminiService.cs:15`, URL query at `:214` | Same pattern; key as **URL query string** to Google |
| Dify API key | `Scripts/LLM/Dify/DifyService.cs:16` | Same pattern |
| OpenAI TTS key | `Scripts/SpeechSynthesizer/OpenAISpeechSynthesizer.cs:30` | Same pattern |
| Aivis Cloud TTS key | `Scripts/SpeechSynthesizer/AivisCloudSpeechSynthesizer.cs:29` | Same pattern |
| NijiVoice TTS key | `Scripts/SpeechSynthesizer/NijiVoiceSpeechSynthesizer.cs:29` | Same pattern; `x-api-key` header |
| Kotodama TTS key | `Scripts/SpeechSynthesizer/KotodamaSpeechSynthesizer.cs:29` | Same pattern |
| Azure TTS key | `Scripts/SpeechSynthesizer/AzureSpeechSynthesizer.cs:29` | `Ocp-Apim-Subscription-Key` header |
| Google TTS key | `Scripts/SpeechSynthesizer/GoogleSpeechSynthesizer.cs:26` | Key in URL query string |
| AIAvatarKit STT key | `Scripts/SpeechListener/AIAvatarKitSpeechListener.cs:15` | Same pattern |
| OpenAI STT (Whisper) key | `Scripts/SpeechListener/OpenAISpeechListener.cs:12` | Same pattern |
| Azure STT key | `Scripts/SpeechListener/AzureSpeechListener.cs:14` | Same pattern |
| SocketServer TCP port | `Scripts/Network/SocketServer.cs:88` | `IPAddress.Any`, no auth, JSON deserialization |
| JavaScriptMessageHandler global | `Plugins/JavaScriptMessageHandler.jslib` | `window.SendMessageToChatdollKit` — any JS can call |
| Newtonsoft TypeNameHandling.All | `Scripts/LLM/ChatGPT/ChatGPTService.cs:37-40` | Polymorphic deserialization on `$type` |
| Mobile permissions | `Plugins/iOS/*.a`, `Plugins/Android/*.aar` | Mic permission; native AEC stack; opaque binaries |
| XR sensor surfaces | `[unverified — VR/AR target via Unity build settings]` | Headset pose, hand-tracking, eye-tracking, room-scale data |
| Camera | `Scripts/IO/SimpleCamera.cs` | Device camera capture; image sent to ChatGPT via base64 |

Eighteen surfaces. Eleven are credential exposures; one is the open TCP port; one is the JS bridge; one is the deserializer config; the rest are platform-permission tails.

---

## 3. STRIDE — Spoofing

### 3.1 The SocketServer accepts anyone

`Scripts/Network/SocketServer.cs:88`:

```csharp
server = new TcpListener(IPAddress.Any, port);
server.Server.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, false);
server.Start();
```

`IPAddress.Any` binds to all network interfaces. Not `IPAddress.Loopback`. Not a config-driven default. On a laptop on a coffee-shop wifi, the port is reachable from every device on the LAN. On a phone running a Unity build of CDK with SocketServer enabled, the port is reachable across the cellular network operator's subnet if NAT punching happens (in tethering mode, common).

`HandleClient` (`:156-195`) reads newline-delimited JSON and calls `JsonConvert.DeserializeObject<ExternalInboundMessage>(message)`. There is no authentication step. There is no token. There is no source-IP allowlist. There is no rate limit. There is not even a maximum message length — `reader.ReadLine()` is unbounded.

**Impact:** Critical. Anyone on the same network can:
1. Inject arbitrary dialog input (`ExternalInboundMessage.Text`) into the LLM context.
2. Trigger arbitrary `Endpoint`/`Operation` dispatch via the `OnDataReceived` callback, whose downstream consumers I have not exhaustively mapped but include the DialogProcessor's request queue.
3. Send arbitrary `Payloads` (a `Dictionary<string, object>`) that gets deserialized via Newtonsoft with `TypeNameHandling.All` somewhere downstream — see §4.

This is the largest CDK-specific finding in the security audit. **Ember-must-reject.**

### 3.2 No JavaScript origin check on WebGL builds

`Plugins/JavaScriptMessageHandler.jslib`:

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

`window.SendMessageToChatdollKit` is installed as a window-global. Any script with access to the window — first-party page script, browser extension content script, any cross-origin script the page loads (e.g., third-party analytics), any iframe ancestor with `postMessage` access if there's a separate handler — can call it. The Unity side at `JavaScriptMessageHandler.cs:35-51` deserializes the message via Newtonsoft into an `ExternalInboundMessage` and dispatches via `OnDataReceived`.

**Impact:** High in WebGL deployments. Any XSS on the host page becomes dialog injection plus arbitrary `Operation` dispatch. The kit accepts whatever JS sends with the same authority as the operator. **Ember-must-reject.** See `[[28_JS_BRIDGE_INTERFACE]]` for the deeper read.

### 3.3 The LLM's function-call name is trusted

`Scripts/LLM/ChatGPT/ChatGPTService.cs:355-371`:

```csharp
if (!string.IsNullOrEmpty(chatGPTSession.ToolCallId))
{
    foreach (var tool in gameObject.GetComponents<ITool>())
    {
        var toolSpec = tool.GetToolSpec();
        if (toolSpec.name == chatGPTSession.FunctionName)
        {
            Debug.Log($"Execute tool: {toolSpec.name}({chatGPTSession.FunctionArguments})");
            var toolResponse = await tool.ExecuteAsync(chatGPTSession.FunctionArguments, token);
            ...
        }
    }
}
```

A prompt-injected LLM (the prompt-injection literature is mature; Greshake et al. 2023) can be coaxed into emitting an arbitrary `FunctionName`. CDK dispatches against the local `ITool` registry. There is no human-in-the-loop, no consent gate, no rate limit. If the operator has registered a tool that controls home automation, sends emails, or interacts with files, the prompt-injecting party (anyone able to send text the LLM eventually sees) can invoke it.

**Impact:** High in any deployment with non-trivial tools. **Ember-inherits-must-harden** — see SAP's `[[sap:53_SECURITY_REVIEW]]` §6 for the matching SAP-tool finding and Hermes's defended-system-prompt pattern.

---

## 4. STRIDE — Tampering

### 4.1 `TypeNameHandling.All` on Newtonsoft

`Scripts/LLM/ChatGPT/ChatGPTService.cs:37-40`:

```csharp
protected JsonSerializerSettings messageSerializationSettings = new JsonSerializerSettings
{
    TypeNameHandling = TypeNameHandling.All
};
```

`TypeNameHandling.All` tells Newtonsoft to honor the `$type` field on inbound JSON and instantiate the named .NET type. This is the configuration that produced CVE-2017-9424 (BlogEngine.NET), CVE-2018-1000005, and a long tail of .NET RCEs through gadget chains in `System.Configuration.Install.AssemblyInstaller`, `System.Windows.Data.ObjectDataProvider`, and similar.

The deserializer here is scoped to `messageSerializationSettings`, used in places where the kit serializes its own `ILLMMessage` polymorphic hierarchy. It is *not* (from my read) used on the SocketServer inbound path — that uses `JsonConvert.DeserializeObject<ExternalInboundMessage>(message)` with default settings. **The risk is contained to inbound messages constructed by CDK itself.** But the pattern is dangerous, the future risk is real, and `TypeNameHandling.None` (or `Objects` constrained to known assemblies) would have served the same purpose with much less rope.

**Impact:** Latent. Currently not externally reachable but one refactor away from being so. **Ember-must-reject** — never use `TypeNameHandling.All` regardless of perceived containment.

### 4.2 Tool arguments arrive as a JSON string the LLM authored

`ChatGPTService.cs:362`: `var toolResponse = await tool.ExecuteAsync(chatGPTSession.FunctionArguments, token);` — `FunctionArguments` is a string the LLM emitted. The `ITool` is expected to parse it. There is no schema validation at the dispatch site. The tool's `ExecuteAsync` may crash, may misinterpret, may execute on adversarial input.

**Impact:** Medium. The tool itself must defend. **Ember-inherits-must-harden.**

---

## 5. STRIDE — Information Disclosure

### 5.1 API keys baked into the build artifact

This is the load-bearing finding. The `public string ApiKey;` field on `ChatGPTService` (a `MonoBehaviour`) is serialized by Unity into the scene YAML when the operator saves the scene. Verified at `Demo/Demo08.unity` — empty `ApiKey:` placeholders are present in the YAML, awaiting operator input. The moment the operator fills in their key via the Inspector and saves, the key is written to the YAML. When the operator builds, the scene YAML is baked into the build's serialized data, which for:

- **iOS / Android**: lives inside the `.ipa` or `.apk`, decompilable with `apktool` or `class-dump` in under a minute by any motivated reverse engineer.
- **Standalone (Win/Mac/Linux)**: lives in `<Game>_Data/sharedassets*.assets`, decompilable with `AssetStudio` or `AssetRipper` instantly.
- **WebGL**: lives inside `Build/<game>.data.unityweb`, plus the key is later included verbatim as a `UTF8ToString` argument in the JS bridge call (see `Plugins/GeminiServiceWebGL.jslib` where `apiKey` is passed via `UTF8ToString(apiKeyPtr)` and then sent in a `fetch` URL query parameter to Google).

**Impact: Critical.** Every operator who ships a CDK-based build to end users — the README explicitly cites OshaberiAI iOS as a production app shipped this way — distributes their API key to every end user. The economic damage is uncapped: an OpenAI key with billing attached, leaked to thousands of downloaders, is a billing-attack vector. The reputational damage is the same as Waifu's.

CDK provides *no documented mitigation*. The README does not warn. The Inspector does not flag. There is no "set this at runtime from a server response" alternative pattern shipped in the kit. There is a `customHeaders` override in some services, but the *default* path bakes the key.

This is the same architectural decision Waifu made with `apiKey: "your-api-key"` — except Waifu was honest about it in a placeholder string. CDK obscures it by hiding the assignment in Unity Inspector UI, which feels like "configuration" but is actually "compiled-in literal." **Ember-must-reject.** Andlit-unity, if pursued, must enforce a backend-proxy pattern: the Unity client holds *no* LLM API keys; all LLM calls route through Strengr, which holds keys server-side and authorizes requests via session tokens issued to the client.

### 5.2 Gemini API key in URL query string

`Scripts/LLM/Gemini/GeminiService.cs:214`:

```csharp
string.IsNullOrEmpty(GenerateContentUrl)
    ? $"https://generativelanguage.googleapis.com/v1beta/models/{Model}:streamGenerateContent?key={ApiKey}"
    : GenerateContentUrl,
```

The key is in the URL. URLs are logged by HTTP proxies, by browser referrer headers (in WebGL builds), by TLS-intercepting middleboxes (corporate networks), by mobile OS network logs (Android `dumpsys netstats`), and by Google's own access logs. Even with TLS, the *server* logs the URL. Google does not consider this leakage because they treat the key as a per-project identifier with rate limits; the operator may consider it leakage if the key was meant to be confidential.

The Plugins/GeminiServiceWebGL.jslib at the `fetch(url + "?key=" + apiKey, ...)` line repeats this in the browser. **Impact:** Medium. **Ember-inherits-must-harden** — if any Munnr provider requires query-string auth, route through Strengr.

### 5.3 Debug logging echoes secrets

`Scripts/LLM/ChatGPT/ChatGPTService.cs:257`:

```csharp
if (DebugMode)
{
    Debug.Log($"Request to ChatGPT: {JsonConvert.SerializeObject(data)}");
}
```

`data` includes the model name, the messages, the tool specs — not the API key directly (which is in headers). But `Debug.Log` in Unity writes to `Player.log` on standalone, to the Android `logcat` system log, to iOS `os_log`, and to the browser console on WebGL. The full user/assistant conversation history is logged when `DebugMode = true`. Operators who ship with `DebugMode = true` (the default is `false`, which is correct) leak conversation contents to any local-app or logcat-reading attacker.

**Impact:** Low if default. Medium if operator forgets. **Ember-inherits-must-harden.**

### 5.4 Mobile permissions leak surface

The iOS and Android native plugins acquire microphone permission. iOS requires `NSMicrophoneUsageDescription` in `Info.plist`; the operator must supply this. The text the operator writes appears in the system permission dialog; if the operator copies CDK's docs verbatim and writes *"Used for voice conversation"*, the user grants mic access to the entire app, which then has unfettered mic capture for any code path. CDK's microphone is on-demand (record-while-listening), but malware or a future update can change that.

**Impact:** Medium. **Ember-inherits-must-harden** — Andlit-unity mobile builds should restrict mic capture to explicit user gestures, never autoplay.

### 5.5 XR sensor surfaces

CDK supports VR and AR build targets (`README.md:15`). Unity's XR plug-ins expose headset pose, hand-tracking, eye-tracking (Quest Pro, Vision Pro), and room-scale geometry. CDK does not use these directly — but a Unity build containing CDK runs in the same process as any other XR plug-ins the operator adds. If the LLM is granted a tool that reads XR sensors, the prompt-injection path of §3.3 reaches biometric data. *[unverified — CDK ships no XR-specific tool; this is a forward risk.]*

**Impact:** Forward-risk. **Ember-inherits-must-harden.**

---

## 6. STRIDE — Denial of Service

### 6.1 Unbounded ReadLine on SocketServer

`SocketServer.cs:165`: `while ((message = reader.ReadLine()) != null)`. `ReadLine` reads until LF or EOF. An attacker can send a multi-gigabyte line with no LF and exhaust process memory before the parser even runs.

**Impact:** Medium. **Ember-must-reject** the unbounded read pattern.

### 6.2 Per-connection thread spawn

`SocketServer.cs:106-108`: `var clientThread = new Thread(() => HandleClient(client));`. Every accepted connection spawns a new thread with no pool, no cap, no rate limit. A trivial connection-flood from a single attacker on the LAN spawns threads until the Unity process hits the OS thread limit (default 1024 on Linux, 2048 on Windows). The process becomes unresponsive.

**Impact:** Medium. **Ember-must-reject.**

### 6.3 TTS prefetch unbounded cache

`SpeechSynthesizerBase.cs:15`: `protected Dictionary<string, AudioClip> audioCache`. The cache is unbounded. Long-running dialog sessions accumulate `AudioClip` allocations; on mobile, GPU/audio memory is bounded and this leaks until OOM. There is no eviction policy.

**Impact:** Medium on mobile, low on desktop. **Ember-inherits-must-harden.**

---

## 7. STRIDE — Elevation of Privilege

### 7.1 Tool dispatch as the operator

§3.3 above. A prompt-injected LLM can invoke `ITool.ExecuteAsync` with adversary-controlled arguments. The tool runs with the application's authority — on iOS, that's whatever entitlements the operator granted; on Android, whatever permissions the user accepted; on desktop, the operator's user-level access.

**Impact:** High in tool-rich deployments. **Ember-inherits-must-harden** — consent-gate every tool invocation; require user confirmation for any tool flagged "side-effectful" in `ITool.GetToolSpec()`.

---

## 8. Cross-References

- `[[sap:53_SECURITY_REVIEW]]` — SAP's thirteen-surface STRIDE; the desktop equivalent.
- `[[waifu:51_SECURITY_AND_PRIVACY]]` — Waifu's hardcoded-key catastrophe. CDK's pattern is the same architectural decision, different wrapper.
- `[[55_WEBGL_GOTCHAS]]` — the WebGL build target compounds every key-leak issue.
- `[[27_SOCKET_PROTOCOL]]` — deeper read on the TCP protocol surface.
- `[[28_JS_BRIDGE_INTERFACE]]` — deeper read on the JS bridge.
- `[[57_FAILURE_TAXONOMY]]` — the impact-ranked summary.

---

## What This Means for Ember

**Adopt:** The pattern of *interface-segregating* credential-bearing components into their own MonoBehaviours (`ChatGPTService`, `ClaudeService`, etc.) is structurally sound — Ember's Strengr can mirror it for per-provider modules. *Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).* The fix Ember must apply is not adopting the *storage location* (Unity scene YAML); the credential field is replaced with an opaque session token resolved via Strengr at runtime.

**Adapt:** CDK's `customHeaders` override mechanism (visible on `ChatGPTService.cs:247-250`) is the correct extension point. Ember's Andlit-unity should *only* expose `customHeaders`-style runtime configuration, never a `public string ApiKey`.

**Avoid:**
- `public string ApiKey;` as a `MonoBehaviour` field. Always. Without exception. The Inspector convenience is not worth the build-bundle leak.
- `IPAddress.Any` binding without authentication. SocketServer-equivalent surfaces in Ember must default to `127.0.0.1` plus require a Bearer token from a tailnet-mTLS source. (Aligns with the user's standing preference for tailnet-bound services.)
- `TypeNameHandling.All` on any JSON deserializer.
- `window`-globals on JS bridges. If a WebGL surface is needed, use `window.postMessage` with strict origin verification on the listener side; never expose a callable global.
- Unbounded `ReadLine` on socket inputs. Bound by line length and message rate.
- Per-connection thread spawn. Use a fixed-size thread pool or `async` accept loop.

**Invent:** A **Strengr Key Vault interface** for Andlit-unity. The Unity client never holds an LLM provider API key. Instead, the client:
1. Authenticates to Strengr via a per-installation device token (issued at app-install time via a signed Apple/Google-attested handshake).
2. Receives a short-lived (1 hour) bearer token scoped to a single provider.
3. Sends LLM requests through Strengr's proxy endpoint; Strengr injects the real provider key server-side and forwards the response stream back over a TLS channel.
4. Logs rate, token, and cost per device-token in Strengr's accounting layer.

This pattern adds one network hop (Strengr → provider) and removes every key-in-build risk. It also concentrates the prompt-injection blast radius into a single point Ember can audit. Strengr becomes the *only* component that ever sees a provider key. The token issuance handshake is the Vow of Cache Discipline applied to credentials: keys live in the Well of secrets (a Tailscale-bound vault); only Strengr fetches them.

A second invention: **runtime warning on `Debug.Log`-style leakage**. Ember's Funi should refuse to start in Production mode if a build artifact contains string-literal substrings matching known API-key formats (regex on `sk-[A-Za-z0-9]{20,}`, `AIza[A-Za-z0-9_-]{35}`, etc.). This is a static-analysis Vow: *the build artifact is read by Funi at boot, scanned for credential patterns, and the process refuses to launch with credentials in the binary.*

---

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c).*

---
codex_id: 18_NETWORK_DOMAIN
title: Network Domain — Two Inbound Surfaces, One Outbound Helper, Zero Authentication
role: Architect
layer: Domain
status: draft
chatdoll_source_refs:
  - Scripts/Network/SocketServer.cs:1-203
  - Scripts/Network/ChatdollHttp.cs:1-288
  - Scripts/Network/WebSocketClient.cs:1-209
  - Scripts/Network/SocketClient.cs
  - Scripts/IO/JavaScriptMessageHandler.cs:1-54
  - Scripts/IO/ExternalInboundMessage.cs:1-13
  - Scripts/IO/IExternalInboundMessageHandler.cs:1-11
  - Scripts/AIAvatar.cs:592-664
ember_subsystem_targets: [Funi, Strengr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_AIAVATAR_DOMAIN
  - 20_interface/27_SOCKET_PROTOCOL
  - 20_interface/28_JS_BRIDGE_INTERFACE
  - 50_verification/51_SECURITY_REVIEW
  - sap:18_MCP_DOMAIN
  - waifu:23_LIVEKIT_DATACHANNEL
---

# Network Domain
## Two Inbound Surfaces, One Outbound Helper, Zero Authentication

*— Rúnhild Svartdóttir, Architect*

> *Every network surface is either authenticated or a gift. ChatdollKit's two inbound surfaces are gifts. The architectural choice to expose them is sound; the implementation choice to leave them open is the largest single security debt in the codex.*

`Scripts/Network/` and the inbound surfaces in `Scripts/IO/` together constitute the *external nervous system* of a ChatdollKit avatar. Six files, roughly **750 LOC**, organised into three concerns: **outbound HTTP** (`ChatdollHttp.cs`, 288 LOC — a `UnityWebRequest` convenience wrapper used by every LLM and TTS provider), **outbound WebSocket** (`WebSocketClient.cs`, 209 LOC — used by streaming STT/LLM/TTS providers), and **inbound dual-surface remote control** — `SocketServer.cs` (203 LOC, raw TCP/JSON) and `IO/JavaScriptMessageHandler.cs` (54 LOC, WebGL→Unity bridge) plus the shared `ExternalInboundMessage` envelope.

The duality matters. CDK runs on Unity. On native builds, the obvious remote-control surface is a TCP socket. On WebGL builds, TCP sockets are impossible — the substrate is the browser, the only way in is via JavaScript. CDK exposes *both* surfaces, *with the same message envelope* (`ExternalInboundMessage`), so application code that handles one handles both. This is **the single architectural pattern of this domain**: one external-message handler interface, two transport implementations, build-target-dependent registration.

The security cost: neither inbound surface has authentication, schema validation beyond JSON-deserialisation, or origin checking. On a developer workstation behind a firewall, fine. On a deployed phone or in a multi-tenant lab, not fine. Ember's posture on this is non-negotiable — bind to Tailscale by default, per-message token required, fail-closed.

Compare SAP's MCP + A2A surfaces ([[sap:18_MCP_DOMAIN]]) — authenticated, schema-validated, but also vastly more complex. Compare Waifu's LiveKit data channel ([[waifu:23_LIVEKIT_DATACHANNEL]]) — broker-mediated, no direct socket exposure. **CDK's surfaces are simpler, faster to integrate, and dramatically less defended.** The trade is real and visible.

---

## 1. The Subject Itself

**What the domain is:** the boundary where bytes cross between the Unity process and anything else. Outbound: HTTP requests to LLM/TTS/STT providers; WebSocket connections to streaming endpoints. Inbound: TCP socket listening for newline-delimited JSON commands; WebGL bridge receiving JSON from page-side JS.

**What it owns:**

| Concern | Files | LOC | Owns |
|---|---|---|---|
| **Outbound HTTP** | `Network/ChatdollHttp.cs` | 288 | Wrapper over `UnityWebRequest`: GET/POST/PUT/PATCH/DELETE with form/binary/JSON variants, parameter encoding, header injection, before/after hooks, deserialise-to-T helpers |
| **Outbound WebSocket** | `Network/WebSocketClient.cs` | 209 | Dual-implementation: `System.Net.WebSockets` on native, `NativeWebSocket` library on WebGL; subprotocol-as-header trick (lines 38-52) |
| **Outbound TCP client** | `Network/SocketClient.cs` | ~80 | Simple TCP client; sends `ExternalInboundMessage` to another CDK instance's `SocketServer` |
| **Inbound TCP** | `Network/SocketServer.cs` | 203 | `TcpListener` on `IPAddress.Any:port`, newline-delimited JSON, thread-per-client, queue-to-main-thread dispatch |
| **Inbound JS bridge** | `IO/JavaScriptMessageHandler.cs` | 54 | `[DllImport("__Internal")] InitJSMessageHandler`, `HandleMessageFromJavaScript(string)` deserialises and invokes `OnDataReceived` |
| **Shared envelope** | `IO/ExternalInboundMessage.cs`, `IO/IExternalInboundMessageHandler.cs` | 13+11 | Five-field message envelope and the one-method handler interface |

**What it does NOT own:**
- *Authentication* — there is none. This is a feature absence, not a delegation.
- *Authorization* — same.
- *TLS* — `ChatdollHttp` accepts URLs; if the URL is `https`, Unity handles TLS. The SocketServer is TCP-only — no TLS option at all.
- *Message semantics* — the `OnDataReceived` handler is wired by `AIAvatar` (`AIAvatar.cs` Awake handler block) and routes the message to `DialogProcessor` or other endpoints based on `message.Endpoint`. The Network domain ferries; the IO/Dialog domains interpret.

---

## 2. How It Works

### 2.1 The `ExternalInboundMessage` envelope

`Scripts/IO/ExternalInboundMessage.cs:5-12`:

```csharp
public class ExternalInboundMessage
{
    public string Endpoint { get; set; }
    public string Operation { get; set; }
    public int Priority { get; set; }
    public string Text { get; set; }
    public Dictionary<string, object> Payloads { get; set; }
}
```

Five fields. `Endpoint` is a string like `"dialog"` or `"animation"` — routes the message to the right handler. `Operation` is like `"start"`/`"stop"`/`"set"`. `Priority` is an integer (used by `DialogPriorityManager`'s queue). `Text` is the primary string payload. `Payloads` is the dict for everything else.

The schema is *deliberately loose*. New endpoints add new strings; new operations add new strings; payload structure varies. No version field. No schema URI. No discriminated union. The trade: every consumer can extend by adding a handler for a new endpoint; no breaking changes are possible because there is no contract to break. Cost: any change to a handler's payload-key expectations silently changes the wire format.

For Ember: the envelope shape is portable; the lack of versioning is a debt. Add `version: int` and a registry of `(endpoint, version) → handler`.

### 2.2 The `IExternalInboundMessageHandler` contract

`Scripts/IO/IExternalInboundMessageHandler.cs:6-10`:

```csharp
public interface IExternalInboundMessageHandler
{
    Func<ExternalInboundMessage, UniTask> OnDataReceived { get; set; }
}
```

One member: a callback assignable by the caller. The handler does not specify what *processes* the message — it specifies a *slot* where the consumer sets the processor. Both `SocketServer` and `JavaScriptMessageHandler` implement this interface; AIAvatar's `Awake` assigns the same `OnDataReceived` lambda to both. The result: identical inbound semantics regardless of transport. **This is the unifying decision of the domain.**

### 2.3 The SocketServer (`Scripts/Network/SocketServer.cs`)

The native-build inbound surface. The shape:

```csharp
// SocketServer.cs:86-120
private void StartServerInThread() {
    server = new TcpListener(IPAddress.Any, port);
    server.Server.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, false);
    server.Start();
    while (IsRunning) {
        var client = server.AcceptTcpClient();
        var clientThread = new Thread(() => HandleClient(client));
        clientThread.IsBackground = true;
        clientThread.Start();
    }
}

// SocketServer.cs:156-195
private void HandleClient(TcpClient client) {
    var reader = new StreamReader(stream, Encoding.UTF8);
    string message;
    while ((message = reader.ReadLine()) != null) {
        var request = JsonConvert.DeserializeObject<ExternalInboundMessage>(message);
        lock (queueLock) { messageQueue.Enqueue(request); }
    }
}
```

**Three threads** in this loop. The accept-thread (per-server) waits for connections. Per-connection client-threads read newline-delimited JSON. The Unity main thread's `Update()` (lines 42-53) dequeues messages and invokes `OnDataReceived` on the main thread. Two synchronisation points: the `queueLock` for enqueue/dequeue, and Unity's implicit single-threaded main-loop for the actual handler execution.

The pattern is conventional but correctly implemented. `ReuseAddress = false` (line 89) ensures port-already-in-use throws an error rather than silently binding to a phantom port (a Linux quirk). The `IsBackground = true` thread flag (lines 82, 107) lets the JVM tear down threads on app quit without explicit joins.

**The security shape**:

- `IPAddress.Any` — every interface, every IP. There is no per-interface binding option. To restrict to localhost, the user must edit the source. CDK does not provide a config flag for binding.
- No authentication. The accept-thread accepts any TCP connection; the reader parses any newline-delimited JSON.
- No TLS. The reader uses `StreamReader(stream, Encoding.UTF8)` on the raw socket stream.
- No rate-limiting. A flood of `{"Endpoint":"dialog","Text":"hi"}` lines starves the dialog pipeline.
- No connection limit. Each client gets a thread; no bound on concurrent clients.

This is *fine for a developer machine behind a firewall*. It is malpractice for a deployed phone or a lab with untrusted neighbours. The Auditor's full catalogue is at [[27_SOCKET_PROTOCOL]] and [[51_SECURITY_REVIEW]]. The Ember posture: the equivalent surface binds to `tailscale0` interface only, requires a per-message HMAC keyed off a session secret, rate-limits to 10 messages/second per connection, and rejects payloads over 64KB.

### 2.4 The JavaScriptMessageHandler (`Scripts/IO/JavaScriptMessageHandler.cs`)

The WebGL-build inbound surface. The shape:

```csharp
// JavaScriptMessageHandler.cs:23-33, 35-51
public void Start() {
    if (captureKeyboardInput) WebGLInput.captureAllKeyboardInput = false;
    InitJSMessageHandler(gameObject.name, "HandleMessageFromJavaScript");
}

public void HandleMessageFromJavaScript(string message) {
    var jsMessage = JsonConvert.DeserializeObject<ExternalInboundMessage>(message);
    OnDataReceived?.Invoke(jsMessage);
}
```

The `InitJSMessageHandler` is a `[DllImport("__Internal")]` call into a JS-side function that registers a `window.<gameObjectName>_HandleMessageFromJavaScript = (msg) => unityInstance.SendMessage(...)` callback. From JS, the user can call `unityInstance.SendMessage("AIAvatar", "HandleMessageFromJavaScript", JSON.stringify({...}))` and it lands in this C# method.

**The security shape**:

- No origin check. Any script on the host page can send. iframe embedding inherits.
- No token. The C# method accepts whatever JSON arrives.
- No schema validation beyond JsonConvert's deserialiser (which silently fills missing fields with defaults).
- The browser's same-origin policy provides *some* defence: only same-origin pages can call `unityInstance.SendMessage`. But same-origin includes any third-party script the page loaded.

The honest assessment: this is fine when the WebGL build is hosted on a single-page-app that the developer controls. It is *unsafe* when the build is embedded in a third-party page, in an iframe, or in any context where the host page loads untrusted scripts. The Auditor's catalogue is at [[28_JS_BRIDGE_INTERFACE]].

### 2.5 The `ChatdollHttp` outbound helper

`Scripts/Network/ChatdollHttp.cs` (288 LOC) is the *consumed-by-everyone* outbound client. Every LLM provider, every TTS provider, every STT provider uses it. The shape:

```csharp
// Selected method signatures from ChatdollHttp.cs
public async UniTask<ChatdollHttpResponse> GetAsync(string url, Dictionary<string, string> parameters = null, Dictionary<string, string> headers = null, CancellationToken cancellationToken = default);
public async UniTask<TResponse> GetJsonAsync<TResponse>(string url, ...);
public async UniTask<ChatdollHttpResponse> PostFormAsync(string url, Dictionary<string, string> data, ...);
public async UniTask<ChatdollHttpResponse> PostBytesAsync(string url, byte[] data, ...);
public async UniTask<ChatdollHttpResponse> PostJsonAsync(string url, object data, ...);
public async UniTask<TResponse> PostJsonAsync<TResponse>(string url, object data, ...);
public async UniTask<ChatdollHttpResponse> PatchJsonAsync(string url, object data, ...);
```

Convention: every request method has a typed-response sibling that deserialises with JsonConvert. The `BeforeRequestFunc` and `AfterRequestFunc` hooks (lines 16-17) let consumers inject behaviour around every call — logging, retry, auth-token refresh.

**The shape is good**. The cost: every consumer instantiates its own `ChatdollHttp` rather than sharing one. `new ChatdollHttp(Timeout)` appears in every provider's `Start()`. Each maintains its own `BeforeRequestFunc`. If you want global request logging, you set it on every instance. Ember's equivalent should be process-shared with per-call middleware composition.

### 2.6 The WebSocketClient dual-implementation

`Scripts/Network/WebSocketClient.cs` is interesting because it shows the **subprotocol-as-header workaround**:

```csharp
// WebSocketClient.cs:38-52
// Browser WebSocket API doesn't support custom headers.
// Encode headers as subprotocols: {Key}.{Base64URL(Value)}
// Server must echo back one of these in Sec-WebSocket-Protocol response header.
var subprotocols = new List<string>();
foreach (var header in headers) {
    var value = header.Value;
    if (value.StartsWith("Bearer ")) value = value.Substring(7);
    var encoded = Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(value))
        .Replace('+', '-').Replace('/', '_').TrimEnd('=');
    subprotocols.Add($"{header.Key}.{encoded}");
}
webSocket = new WebSocket(url, subprotocols);
```

The browser's WebSocket API forbids custom headers. CDK's workaround: encode each desired header as a Base64URL-encoded subprotocol string. The server (cooperating, e.g., AIAvatarKit's streaming endpoint) decodes the subprotocol. **The encoding is the protocol.** This is the kind of pragmatic workaround that shows the author has *deployed this in production* — no abstract API design produces this code; only the experience of "auth on WebGL WebSocket is impossible" does.

For Ember: the *technique* is a useful artefact. Whether to adopt it depends on whether Ember runs in a browser. For Pi-tier and laptop-tier, native WebSocket is fine.

The native variant (`System.Net.WebSockets.ClientWebSocket`) wraps the .NET surface. The WebGL variant (NativeWebSocket library) wraps the browser API. Both implement `IWebSocketClient` (lines 15-22) — three methods plus a connected-state property and a message event. Identical shape across platforms; substrate-dependent body.

### 2.7 The inbound-message dispatch in AIAvatar

The Network domain produces *deserialised messages*. Where do they go? `AIAvatar`'s `Awake` registers a single lambda on every `IExternalInboundMessageHandler` it finds:

```csharp
// Approximation from AIAvatar.cs Awake
foreach (var handler in gameObject.GetComponents<IExternalInboundMessageHandler>()) {
    handler.OnDataReceived = HandleExternalMessage;
}

private async UniTask HandleExternalMessage(ExternalInboundMessage msg) {
    switch (msg.Endpoint) {
        case "dialog": dialogPriorityManager.SetRequest(msg.Text, msg.Payloads, msg.Priority); break;
        case "animation": modelRequestBroker.SetRequest(msg.Text); break;
        case "say": speechController.Say(msg.Text); break;
        // ...
    }
}
```

The dispatch is **endpoint-string-switch**. Adding a new endpoint requires editing `AIAvatar`. Not extensible without source change. For a small domain (5-10 endpoints) this is fine; for the open-ended general case, a registry pattern would be cleaner. Ember should use the registry.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The `IPAddress.Any` bind is the largest surface

Every interface, every IP, every network. On Windows, this includes the *outward* network adapter — the avatar may be reachable from the LAN. On Linux, includes IPv6 link-local. On Mac, includes the Wi-Fi interface even when ethernet is preferred. **Restrict at the application level.** CDK does not.

### 3.2 The thread-per-client model is DoS-friendly

`new Thread()` per accepted client (line 106). No upper bound. A client that opens 10,000 connections and never sends data parks 10,000 threads. Modern Linux defaults to ~30K threads per user; not impossible to exhaust. Ember should use a thread pool with a bound or asyncio coroutines per connection.

### 3.3 The `StreamReader.ReadLine()` accepts unbounded lines

If a client sends 100MB without a newline, `ReadLine()` allocates 100MB. No cap. Trivial OOM. Ember caps line length (e.g., 64KB); over the cap, close the connection.

### 3.4 The WebSocket subprotocol-encoded auth has subtle Base64URL gotchas

The `.Replace('+', '-').Replace('/', '_').TrimEnd('=')` (line 50) is Base64URL-without-padding. Server-side decoders must handle both with-padding and without-padding variants. CDK's pattern is correct; consumers must match. Cite this from Ember's WebSocket clients with a comment.

### 3.5 The HTTP error handling is per-provider

`ChatdollHttp`'s methods throw on transport errors but `UnityWebRequest`'s `Result` enum distinguishes `ConnectionError`/`ProtocolError`/`DataProcessingError`. Some providers check the enum; others don't. Inconsistent error semantics. Ember unifies: typed exceptions for transport-error/HTTP-error/decode-error.

### 3.6 The `OnDataReceived` Func slot is single-handler

`OnDataReceived` is a `Func<...>`, not an `event Action<...>`. Setting it overwrites; cannot chain. AIAvatar sets one; nothing else can subscribe. To add observability, you must wrap AIAvatar's handler. Ember should use a proper event with multi-subscriber semantics.

### 3.7 No outbound HTTP retry built-in

`ChatdollHttp` does not retry transport failures. Each LLM provider implements its own retry (and most do it badly — same-provider retry on the same connection). Ember's shared client has middleware-style retry with exponential backoff and per-request-class configuration.

### 3.8 The crisp parts

- **The dual-inbound-surface-one-envelope pattern.** `IExternalInboundMessageHandler` + `ExternalInboundMessage` is the right shape.
- **The thread-safe queue handing off to main-thread.** `SocketServer.Update`'s drain pattern is correct.
- **The WebSocket subprotocol auth workaround.** Hard-won; production-tested; ugly; correct.
- **The before/after-request hooks** on `ChatdollHttp`. The right extension point.
- **The build-target-conditional implementations** keeping native and WebGL clients in the same source file via `#if`. Two implementations, one interface, one declaration site.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 7 + IO surfaces — Network and IO inbound paths in the macro shape
- [[11_AIAVATAR_DOMAIN]] §2 — the inbound-message dispatch sits in AIAvatar
- [[13_DIALOG_PROCESSOR_DOMAIN]] — dialog endpoint consumer of inbound messages
- [[27_SOCKET_PROTOCOL]] — Auditor's catalogue of socket-protocol failure modes
- [[28_JS_BRIDGE_INTERFACE]] — Auditor's catalogue of JS-bridge failure modes
- [[51_SECURITY_REVIEW]] — Auditor's review including network surfaces
- [[sap:18_MCP_DOMAIN]] — SAP's authenticated MCP surface for contrast
- [[waifu:23_LIVEKIT_DATACHANNEL]] — Waifu's broker-mediated data channel for contrast

---

## What This Means for Ember

**Adopt:**
- The **`ExternalInboundMessage` envelope shape** (`Scripts/IO/ExternalInboundMessage.cs`). Ember's `ExternalCommand` dataclass: `endpoint: str`, `operation: str`, `priority: int`, `text: str`, `payloads: dict[str, Any]`, *plus* `version: int` and *plus* `signature: str` (the HMAC). Apache-2.0 attribution required.
- The **`IExternalInboundMessageHandler` interface** (`Scripts/IO/IExternalInboundMessageHandler.cs`). Ember's `ExternalMessageHandler` Protocol: same one-member shape. Multiple transports (HTTP, WebSocket, Unix socket, future Tailscale UDP) implement it; the application registers the handler.
- The **thread-safe queue hand-off to main-thread** pattern (`Scripts/Network/SocketServer.cs:42-53`). Ember's asyncio version: each transport coroutine drains its buffer on a single `asyncio.Queue` that the dispatcher coroutine awaits. The semantics translate cleanly.
- The **WebSocket subprotocol-as-header auth workaround** (`Scripts/Network/WebSocketClient.cs:38-52`). Apache-2.0 attribution required. For any Ember tier that runs in a browser (future Tier-CLOUD), this technique is mandatory.
- The **before/after-request hooks on `ChatdollHttp`** (`Scripts/Network/ChatdollHttp.cs:16-17`). Ember's shared HTTP client accepts a middleware list; before/after are two of the standard middleware positions.

*Apache-2.0 attribution: when patterns from `ChatdollKit/Scripts/Network/` and `Scripts/IO/` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:**
- The **`IPAddress.Any` bind**. Adapt as Ember's `bind_interface: str` config (`tailscale0` default, `lo` for dev, `0.0.0.0` only with explicit `unsafe_public_bind: true` flag + warning).
- The **thread-per-client model**. Adapt as asyncio coroutine-per-connection with a `max_concurrent_connections: int` bound (default 16). Backpressure: refuse new connections beyond the bound with a TCP RST.
- The **unbounded `ReadLine`**. Adapt as `read_line(max_bytes=65536)` — over the cap, raise `LineTooLargeError`, close the connection, emit a Sögumiðla event.
- The **endpoint-string-switch dispatch**. Adapt as Ember's `endpoint_registry: dict[str, EndpointHandler]` with `register_endpoint(name, version, handler)` decorator pattern.
- The **per-call `new ChatdollHttp()` pattern**. Adapt as Ember's process-singleton `http_client` with per-call middleware overlay.

**Avoid:**
- **Inbound surfaces without authentication.** Non-negotiable in Ember. Every inbound message has a session-keyed HMAC; verification on receipt; reject and log on failure.
- **Inbound surfaces without TLS option.** Ember's TCP transport supports TLS; default is TLS-on for non-loopback binds.
- **Single-handler `OnDataReceived` slot.** Ember uses a proper event with subscribe/unsubscribe and observability.
- **Same-provider HTTP retry without circuit breaking.** Ember's shared HTTP client has circuit-breaker middleware per-host.

**Invent:**
- **The Tailnet-First Bind Vow.** Every Ember inbound surface binds to `tailscale0` by default. Loopback is the local-dev fallback. `0.0.0.0` requires an explicit `unsafe_public_bind: true` flag in YAML *and* a startup warning logged. The user's standing preference [[ember:reference_tailnet_access]] becomes architectural law.
- **The Versioned-Endpoint Registry.** Ember's `endpoint_registry` requires `(endpoint, version)` tuples. Adding `("dialog", 2)` does not replace `("dialog", 1)`; both can coexist during migration. Clients declare their version; the dispatcher picks the matching handler. CDK's open string-switch becomes a closed-set discoverable registry.
- **The HMAC-Per-Message Vow.** Every inbound message carries `signature = HMAC-SHA256(session_secret, canonical_json(message))`. The session secret is provisioned once (via a side channel: physical button press, OAuth, or a manually-pasted token). Failed verification: emit a Sögumiðla `InboundAuthFailed` event, drop the message, do not respond.
- **The Per-Transport Provenance Stamp.** Every dispatched message carries `transport_id: str` ("tailscale-tcp:fd7a::1:54321", "websocket:wss://...", "unix-socket:/run/ember.sock"). Sögumiðla events carry it; failure logs trace it. Volmarr can reconstruct which transport delivered which message.
- **The HTTP Middleware Stack.** Ember's HTTP client supports a middleware list: `[auth, logging, retry, circuit_breaker, before_request, after_request]`. Configurable per-request-class. The CDK before/after hooks become two positions in a longer pipeline.
- **The Outbound Allowlist.** Ember's HTTP client checks every outbound URL against a configured allowlist of hosts. Calls to non-allowlisted hosts emit `OutboundBlockedByPolicy` events and fail. Default allowlist: provider URLs from config + `localhost`. A compromised tool cannot exfiltrate to `evil.example.com` because the egress is policy-checked.
- **The Connection Heartbeat Vow.** Every WebSocket client sends a heartbeat every 30 seconds; if no pong within 10 seconds, the connection is considered dead and a Sögumiðla `WebSocketStale` event fires. CDK relies on TCP keepalive (often 2-hour default on Linux); Ember does its own application-layer health checking with visible failure modes.

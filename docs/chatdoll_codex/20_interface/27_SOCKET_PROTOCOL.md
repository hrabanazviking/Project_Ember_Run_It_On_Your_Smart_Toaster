---
codex_id: 27_SOCKET_PROTOCOL
title: Socket Protocol — A TCP Listener On Every Interface, Newline-Delimited JSON, And A Demo That Reconfigures The Whole Avatar Over It Without Auth
role: Auditor
layer: Interface
status: draft
chatdoll_source_refs:
  - Scripts/Network/SocketServer.cs:13-203
  - Scripts/Network/SocketClient.cs:8-76
  - Scripts/IO/ExternalInboundMessage.cs:5-12
  - Scripts/IO/IExternalInboundMessageHandler.cs:6-10
  - Demo/AITuber/AITuberMessageHandler.cs:21-276
  - Demo/AITuber/MainAITuber.cs:61
sister_source_refs:
  - /tmp/chatdollkit-aituber/chatdollkit_aituber/client.py:6-99
  - /tmp/chatdollkit-aituber/chatdollkit_aituber/api.py:1-173
ember_subsystem_targets: [Funi, Strengr, Munnr]
cross_refs:
  - 20_interface/28_JS_BRIDGE_INTERFACE
  - 50_verification/51_SECURITY_REVIEW
  - 50_verification/56_SISTER_INTEGRATION_RISKS
  - 50_verification/57_FAILURE_TAXONOMY
  - 30_execution/3A_AITUBER_CONTROLLER
  - sap:18_LOCALHOST_API_DOMAIN
  - waifu:25_DATA_CHANNEL
---

# Socket Protocol — A TCP Listener On Every Interface, Newline-Delimited JSON, And A Demo That Reconfigures The Whole Avatar Over It Without Auth

> *Sólrún, voice cold and even: the `SocketServer` is one of two surfaces by which an external process drives a CDK avatar. The other is the JavaScript bridge in `[[28_JS_BRIDGE_INTERFACE]]`. The socket variant is the one that lives on Windows, macOS, Linux, iOS, and Android (everywhere except WebGL); the JS bridge is the WebGL counterpart. The two are wired to the same internal dispatch (`IExternalInboundMessageHandler.OnDataReceived`) and accept the same `ExternalInboundMessage` shape. What differs is the transport and the threat model.*
>
> *The socket transport is a `TcpListener` bound to `IPAddress.Any` with no authentication, no TLS, no rate limit, no source-IP allowlist, no maximum message length, and one thread per accepted connection. The demo handler `AITuberMessageHandler.cs` lets a remote message reassign the avatar's LLM provider, swap the API key from the wire, change the system prompt, load a new VRM model from a URL, point the doll at a different AIAvatarKit endpoint, and clear the dialog context — over the same unauthenticated socket that accepts the same message shape. The sister project `chatdollkit-aituber` ships a FastAPI wrapper that exposes every one of these operations as REST endpoints, opening another layer of indirection between an HTTP caller and the unauthenticated TCP socket. The threat model is: trust everyone on the LAN, trust everyone in the same Tailnet, trust everyone with a port-forward, trust everyone who shares wifi with the operator.*

This document audits the SocketServer protocol as an interface contract: the on-the-wire shape, the dispatch model, the demo handler that defines de-facto operations, the sister-project consumer pattern, the threat model, and the operator's deployment surface. The security-focused read is in `[[51_SECURITY_REVIEW §3.1, §4, §6.1, §6.2]]`; here I focus on the protocol-as-protocol.

---

## 1. The Wire Shape — Five Fields

`/tmp/ChatdollKit/Scripts/IO/ExternalInboundMessage.cs:5-12`:

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

Five fields. One typed integer, three strings, one arbitrary dictionary. The shape is the contract — both transports (TCP, JS bridge) deserialize JSON into this single record and hand it off.

`Endpoint` and `Operation` are the dispatch keys. `Text` is the optional textual payload (used for dialog input, model load URLs, system prompt text). `Priority` is an integer used by the priority manager when the operation routes through the dialog queue. `Payloads` is a free-form key-value bag.

The shape is **completely untyped at the protocol level**. Anyone with the field names can construct any message; the server has no schema validation, no version negotiation, no namespace. A message with `Endpoint = "x", Operation = "y"` is happily deserialized; whether anything handles it depends on whether the operator has registered a handler.

No protocol version field. No protocol-level error response. No reply at all — the wire is one-way. A sender that issues a `dialog/process` request never knows whether the dialog actually processed; the only signal is whether the doll speaks. This is *fire-and-forget* with no acknowledgement.

---

## 2. The Transport — Newline-Delimited JSON Over Raw TCP

`/tmp/ChatdollKit/Scripts/Network/SocketServer.cs:86-120`:

```csharp
private void StartServerInThread()
{
    server = new TcpListener(IPAddress.Any, port);
    server.Server.SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, false);
    server.Start();
    IsRunning = true;
    Debug.Log($"Server started on port {port}");

    try {
        while (IsRunning) {
            var client = server.AcceptTcpClient();
            if (isDebug) { Debug.Log($"Client connected."); }
            var clientThread = new Thread(() => HandleClient(client));
            clientThread.IsBackground = true;
            clientThread.Start();
        }
    }
    catch (Exception ex) {
        Debug.LogError($"Server encountered an error: {ex.Message}");
    }
    finally {
        server.Stop();
        Debug.Log("Server stopped in thread.");
    }
}
```

`IPAddress.Any` (`:88`) — every network interface. Not `IPAddress.Loopback`. Not a configurable default. The port number is set in the Inspector; the bind address is hard-coded.

`SetSocketOption(SocketOptionLevel.Socket, SocketOptionName.ReuseAddress, false)` (`:89`) — refuses to bind if the port is already in use. Operator-friendly (fast fail at startup if the port is taken).

`HandleClient(client)` (`:156-195`):

```csharp
private void HandleClient(TcpClient client)
{
    var stream = client.GetStream();
    var reader = new StreamReader(stream, Encoding.UTF8);

    try {
        string message;
        while ((message = reader.ReadLine()) != null) {
            if (isDebug) { Debug.Log($"Received from client: {message}"); }
            try {
                var request = JsonConvert.DeserializeObject<ExternalInboundMessage>(message);
                lock (queueLock) {
                    messageQueue.Enqueue(request);
                }
            }
            catch (Exception jex) {
                Debug.LogError($"Error while parsing message: {jex.Message}: {message}");
            }
        }
    }
    catch (Exception ex) {
        Debug.LogError($"Error while reading from client: {ex.Message}");
    }
    finally {
        client.Close();
    }
}
```

`reader.ReadLine()` — newline-delimited messages, UTF-8. One message per line. The thread runs until the client closes the connection or sends EOF. A persistent client can stream many messages over one connection.

`JsonConvert.DeserializeObject<ExternalInboundMessage>(message)` — Newtonsoft default settings. This does *not* honor `TypeNameHandling.All` (the dangerous setting that lives on `messageSerializationSettings` in `ChatGPTService.cs:37-40`); the default deserializer is constrained to the typed record. **The deserializer itself is safe.** The flaw is upstream: the deserializer accepts any well-formed JSON, and the dispatched handlers do not validate the payloads against operation-specific schemas.

The lock-and-enqueue (`:175-179`) is the thread-safe transition to the Unity main thread. The server thread reads, deserializes, enqueues. The `Update` method (`:42-53`) on the Unity main thread drains the queue and calls `OnDataReceived?.Invoke(message)`. This is correctly architected — message dispatch happens on the main thread, where MonoBehaviour state mutations are safe.

---

## 3. The Threading Model — One Thread Per Connection

`:106-108`:

```csharp
var clientThread = new Thread(() => HandleClient(client));
clientThread.IsBackground = true;
clientThread.Start();
```

Per-connection thread spawn. No pool. No cap. No rate limit on `AcceptTcpClient`. The server thread accepts and dispatches in tight loop; an attacker on the same network connecting and disconnecting rapidly spawns one thread per connection. On Linux the default per-process thread limit is 1024; on Windows it depends on stack reservation but trends to a few thousand. An attacker can hit this in seconds.

This is a denial-of-service finding (`[[51_SECURITY_REVIEW §6.2]]`). The protocol surface is unbounded.

The `HandleClient` itself does no rate-limiting and no inactivity timeout. A connection that opens and never sends a byte holds the thread until the OS-level keepalive eventually closes the socket (typically two hours on Linux). An attacker can hold connections open to slowly drain thread availability.

---

## 4. The Default Operations — As Defined By The Demo

`SocketServer` itself defines no operations. The dispatch — what `Endpoint`/`Operation` pairs do anything — is entirely operator-defined. The CDK demos define the de-facto canonical operation set.

`/tmp/ChatdollKit/Demo/AITuber/AITuberMessageHandler.cs` registers as the `OnDataReceived` consumer (`:48-52`):

```csharp
private void Awake() {
    handler = gameObject.GetComponent<IExternalInboundMessageHandler>();
    handler.OnDataReceived += HandleExternalMessage;
}
```

`HandleExternalMessage(ExternalInboundMessage message)` (`:74-276`) is two hundred two lines of `if/else` dispatching on `Endpoint`/`Operation`. The canonical operation set:

| Endpoint | Operation | Effect |
|---|---|---|
| `model` | `perform` | Triggers a model gesture/expression via `ModelRequestBroker.SetRequest(Text)` |
| `model` | `load` | Loads a VRM from `Text` URL via `vrmLoader.LoadCharacterAsync(Text)` |
| `model` | `appearance` | Reconfigures camera position, FOV, background, model position/rotation |
| `dialog` | `process` | Submits user-input text to the dialog priority manager |
| `dialog` | `append_next` | Appends text to the next utterance |
| `dialog` | `clear_request_queue` | Empties the priority queue at `Priority` level |
| `dialog` | `clear_context` | Wipes LLM conversation history |
| `dialog` | `connect_to_aiavatar` | Reconfigures `SocketClient` to talk to a different AIAvatar host:port |
| `dialog` | `disconnect_from_aiavatar` | Disconnects |
| `speech_synthesizer` | `activate` | Switches active TTS provider (VOICEVOX or Style-Bert-VITS2), reconfigures endpoint URL, speaker, model |
| `speech_synthesizer` | `styles` | Replaces the active TTS's `VoiceStyles` list |
| `llm` | `activate` | Switches active LLM provider, reassigns ApiKey, Model, Temperature, ChatCompletionUrl from `Payloads` |
| `llm` | `system_prompt` | Replaces the system prompt with `Payloads["system_prompt"]` |
| `llm` | `cot_tag` | Reassigns chain-of-thought stripping tag |
| `llm` | `debug` | Toggles `LLMServiceBase.DebugMode` (which logs full request bodies including conversation history) |

Sixteen operations. Each one is a privileged operation. Five of them mutate live security-relevant state.

### 4.1 The `llm/activate` Operation — The Worst Of The Set

`:217-260`:

```csharp
else if (message.Endpoint == "llm")
{
    if (message.Operation == "activate")
    {
        var name = ((string)message.Payloads["name"]).ToLower();
        var apiKey = message.Payloads.ContainsKey("api_key") ?  (string)message.Payloads["api_key"] : null;
        var model = message.Payloads.ContainsKey("model") ?  (string)message.Payloads["model"] : null;
        var temperature = message.Payloads.ContainsKey("temperature") ?  Convert.ToSingle(message.Payloads["temperature"]) : -1;
        var url = message.Payloads.ContainsKey("url") ?  (string)message.Payloads["url"] : null;
        var user = message.Payloads.ContainsKey("user") ?  (string)message.Payloads["user"] : null;

        if (name == "chatgpt")
        {
            dialogProcessor.SelectLLMService(chatGPTService);
            if (apiKey != null) chatGPTService.ApiKey = apiKey;
            if (model != null) chatGPTService.Model = model;
            if (temperature >= 0) chatGPTService.Temperature = temperature;
            if (url != null) chatGPTService.ChatCompletionUrl = url;
            chatGPTService.IsAzure = message.Payloads.ContainsKey("is_azure") ? Convert.ToBoolean(message.Payloads["is_azure"]) : false;
        }
        // ...same for claude, gemini, dify...
    }
    // ...system_prompt, cot_tag, debug...
    dialogProcessor.ClearContext();
}
```

Over the **unauthenticated TCP socket**, anyone on the LAN can:
1. Reassign the LLM provider.
2. Reassign the API key, the model, the temperature, the endpoint URL.
3. Reassign the system prompt to anything they like.
4. Enable `DebugMode`, which logs full conversation contents to Unity's log.

The blast radius: the doll now talks to *the attacker's LLM endpoint with the attacker's API key* and *with the attacker's system prompt*. Every subsequent user utterance routes through the attacker. The attacker reads the conversation, the attacker decides what the doll says, the attacker can prompt-inject to invoke any `ITool` registered on the doll (the prompt-injection chain in `[[51_SECURITY_REVIEW §3.3]]`).

The `system_prompt` reassignment alone (`:261-264`) is a complete dialog hijack:

```csharp
((LLMServiceBase)dialogProcessor.LLMService).SystemMessageContent = (string)message.Payloads["system_prompt"];
```

The attacker writes a new persona for the doll over the socket. The doll begins behaving as a different character on the next user turn. The Hermes-codex's *Defended System Prompt* vow is meaningful precisely because the alternative — a system prompt that any LAN-reachable process can rewrite — is what CDK ships.

**Audit finding:** This is the most consequential single-line finding in the whole codex. **Ember-must-reject.**

### 4.2 The `model/load` Operation — Remote Asset Loading

`:92-98`:

```csharp
else if (message.Operation == "load")
{
    await vrmLoader.LoadCharacterAsync(message.Text);
    var vrmLookAtHead = modelController.AvatarModel.GetComponent<VRMLookAtHead>();
    vrmLookAtHead.Target = mainCamera.transform;
    vrmLookAtHead.UpdateType = UpdateType.LateUpdate;
}
```

`message.Text` is a URL. `VRMLoader.LoadCharacterAsync` downloads the VRM from that URL and instantiates it. Over the unauthenticated socket, the attacker substitutes the avatar with one of their choosing. The attacker hosts a 50MB VRM, the doll downloads it, the doll's appearance changes mid-stream. On a vtuber's livestream, this is the moment the channel ends.

Worse, VRM loading via UniVRM is *not* sandboxed — VRM files can carry custom shaders, custom MeshRenderer setups, and embedded scripts (depending on the VRM extension set the operator's UniVRM build accepts). A malicious VRM is, in theory, a code-execution vector through the asset pipeline. *[unverified — UniVRM's actual code-loading surface is non-trivial to audit; I treat the asset-pipeline RCE as latent risk rather than proven.]*

**Audit finding:** Remote asset loading without authentication is a category-error. Either the asset URL must be operator-pinned, or the load must be gated.

---

## 5. The Canonical Client — chatdollkit-aituber

`/tmp/chatdollkit-aituber/chatdollkit_aituber/client.py:6-99` is the official Python client for the SocketServer protocol. uezo ships this alongside CDK. It is the operator's expected control plane.

```python
class ChatdollKitClient:
    def __init__(self, host: str = "localhost", port: int = 8888):
        self.host = host
        self.port = port
        ...

    def send_message(self, endpoint: str, operation: str, *, text: str = None,
                      priority: int = 10, payloads: dict = None):
        try:
            self.connect()
            message_dict = {
                "Endpoint": endpoint,
                "Operation": operation,
                "Text": text,
                "Priority": priority,
            }
            if payloads:
                message_dict["Payloads"] = payloads
            message = json.dumps(message_dict)
            self.client_socket.sendall((message + "\n").encode("utf-8"))
            ...
        finally:
            self.close()
```

The default `host` is `"localhost"` (`:7`). When the AITuber controller is deployed on the same machine as the CDK avatar, traffic stays on loopback. Good. When the AITuber controller is deployed on a *separate* server — common for streaming setups where one machine renders and another orchestrates — the operator passes `host="some.other.machine"`. At that moment, the traffic crosses the network. The protocol does not change. The lack of authentication does not change. The attacker on the path now has the same surface the legitimate client has.

The FastAPI wrapper at `/tmp/chatdollkit-aituber/chatdollkit_aituber/api.py:1-173` exposes each socket operation as an HTTP REST endpoint:

- `POST /llm/activate` with `api_key` query parameter that flows straight into the socket message's `Payloads`.
- `POST /llm/system_prompt` with the prompt in the body.
- `POST /model/load` with the URL in `Text`.
- ...and so on for each of the sixteen operations.

The FastAPI server has *no auth on these routes by default*. The chain becomes:

```
attacker → HTTP REST → FastAPI server → TCP socket → CDK avatar
            (no auth)    (no auth)
```

Two layers of indirection, neither authenticated. The chatdollkit-aituber README does not document how to add auth at either layer. Operators who run the AITuber controller without manually adding nginx-with-basic-auth in front of it ship a publicly-controllable avatar.

**Audit finding:** The sister-project ecosystem inherits the no-auth posture and propagates it. The whole control chain is fragile.

---

## 6. The SocketClient — Outbound Side

`/tmp/ChatdollKit/Scripts/Network/SocketClient.cs:8-76` is the matching outbound TCP client — CDK can *also* be the sender. This is used when one CDK instance wants to drive another (via `dialog/connect_to_aiavatar` at `:145-150` it reconnects this client to a remote AIAvatar).

`SocketClient` is similarly auth-free. It connects via `new TcpClient(Address, Port)` and writes UTF-8 JSON + newline. No TLS. No bearer token. No source-IP verification on the receiving side.

The CDK-to-CDK pattern is "one operator's avatar can drive another operator's avatar." For a streamer with multiple physical machines, this is convenient. For an attacker who controls one of the machines, this is a multi-hop reach.

---

## 7. The JSON Shape — Two Quirks

Two on-the-wire quirks worth noting.

**Field-name case mismatch.** The C# class fields are PascalCase (`Endpoint`, `Operation`, `Text`, `Priority`, `Payloads`). The Python client at `chatdollkit_aituber/client.py:47-54` emits PascalCase JSON keys to match: `{"Endpoint": "...", "Operation": "...", "Text": "...", "Priority": 10}`. **Newtonsoft default deserialization is case-insensitive for property matching**, so lowercase or camelCase would also work. The convention is PascalCase. This is non-standard for JSON-API design (most JSON APIs use snake_case or camelCase). Operators writing a non-Python client must remember PascalCase.

**Priority as int, not enum.** `Priority` is a free integer. Convention from the demo: `0` for "highest, clear before processing", `10` for "normal", higher for "lower priority". No documented enum. An attacker setting `Priority = int.MinValue` causes... whatever the priority manager does with that value. *[unverified — I have not traced the priority manager's bounds checking.]*

---

## 8. The Operator's Deployment Surface

What does the operator have to do to deploy CDK with a SocketServer? From the demo Inspector:

1. Drop a `SocketServer` component onto the AIAvatar GameObject.
2. Set `port` (default empty, must be filled — typical demo uses `8888`).
3. Leave `autoStart = true` (default).
4. Build.

That is it. The operator does *not* configure:
- Bind address. Hard-coded `IPAddress.Any`.
- Authentication. None exists.
- TLS. None exists.
- Allowlist. None exists.
- Rate limit. None exists.
- Max message size. None exists.
- Handler registration. Done by handler classes, but the SocketServer accepts all messages and queues them; an unhandled message is dropped silently.

The Inspector convenience is the trap. The minimum setup is two clicks and a port number, and the result is an unauthenticated remote-control surface bound to every interface.

The README at the AITuber section provides example operator setups (port 8888, localhost client) but does not warn about LAN exposure. The reader who follows the tutorial deploys the threat model.

---

## 9. Cross-References

- `[[28_JS_BRIDGE_INTERFACE]]` — the WebGL counterpart with its own auth absence.
- `[[51_SECURITY_REVIEW §3.1, §4.1, §6.1, §6.2]]` — STRIDE read on the same protocol; the security-focused detail.
- `[[56_SISTER_INTEGRATION_RISKS]]` — chatdollkit-aituber's role in propagating the no-auth posture.
- `[[3A_AITUBER_CONTROLLER]]` — Forge-B's execution read on the AITuber Controller usage pattern.
- `[[sap:18_LOCALHOST_API_DOMAIN]]` — SAP's localhost-bound HTTP API with fossil-string auth. Compare and contrast: SAP at least uses loopback by default and requires a magic-string Bearer.
- `[[waifu:25_DATA_CHANNEL]]` — Waifu uses LiveKit data channels, which are authenticated at the LiveKit-token level. Stronger posture.

---

## What This Means for Ember

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c).*

**Adopt:**

- **The `ExternalInboundMessage` five-field shape** (`ExternalInboundMessage.cs:5-12`) as Ember's external-control message contract. `{Endpoint, Operation, Priority, Text, Payloads}` is a workable polymorphic surface; the Endpoint/Operation tuple is a clean dispatch key. Apache-2.0 attribution required.
- **The transport / handler separation** (`SocketServer` + `IExternalInboundMessageHandler` + `OnDataReceived`). The interface lets the same handler accept messages from multiple transports (socket, JS bridge, future WebSocket, future MCP). Adopt as the Ember `IExternalControlChannel` interface.
- **The main-thread dispatch via queue** (`SocketServer.cs:30-52`). Server thread enqueues, main thread dequeues and dispatches. Correct architecture for Unity. Generalize to any platform with main-thread requirements (which Ember tier-Unity inherits).

**Adapt:**

- **The PascalCase JSON convention.** Adapt to snake_case at the JSON level and use Newtonsoft's `[JsonProperty]` attributes on the C# side. Snake_case is the convention for HTTP APIs in the Python ecosystem operators are likely to integrate from.
- **The free-integer `Priority`.** Adapt to a typed enum (`Priority.Highest, Priority.Normal, Priority.Low`) with bounds.
- **The 16-operation demo dispatch.** Adapt to a per-operation typed payload schema. `Payloads: Dictionary<string, object>` becomes a discriminated union with `LlmActivatePayload`, `ModelLoadPayload`, etc. Schema validation at the dispatch site.

**Avoid:**

- **`IPAddress.Any` binding.** Ember's equivalent SocketServer defaults to `127.0.0.1`. Operator opt-in to bind on a Tailscale interface (matches the user's standing tailnet-first preference). Never `0.0.0.0` without explicit opt-in and a token requirement.
- **Per-connection unbounded thread spawn.** Use `async` accept loop with a fixed semaphore cap (e.g. max 16 concurrent clients). Reject new connections beyond the cap with a connection close.
- **Unbounded `ReadLine`.** Bound by configurable max line length (default 64KB). Lines longer are dropped and the connection closed.
- **No authentication.** Every accepted connection must present a Bearer token in a `HELLO` message as its first line, validated against a Strengr-issued session token. Reject connections that send anything other than a valid `HELLO` as their first message.
- **Fire-and-forget with no reply.** Ember's protocol requires a `RESULT` reply per message: `{request_id, status, error}`. Clients can correlate. Errors are visible.
- **The `llm/activate` reassign-everything-from-the-wire pattern.** Reject categorically. Ember's external-control surface does *not* expose credentialed operations; LLM provider selection is a Strengr-side operator decision. The most a remote message can do is *request* a provider switch, which Strengr authorizes against an operator-policy.
- **Reassignable `system_prompt`.** Reject. System prompts are part of the Defended Build Vow; they live in a signed manifest and cannot be replaced over a control channel.
- **Reassignable `api_key`.** Reject. Keys live in the Strengr Key Vault; they are never on the wire.
- **Remote `model/load` from arbitrary URL.** Restrict to a Strengr-pinned allowlist of model URLs. Operator-defined, signature-validated.

**Invent:**

- A **Tailnet-Default Control Channel** as Ember's analog of SocketServer. Bind to the Tailscale interface IP by default (read from `/var/run/tailscale/tailscale.sock` or equivalent). Accept connections only from peers in the same tailnet. Combined with the per-connection bearer token, this is a defense-in-depth surface that aligns with the user's standing preference. CDK has nothing equivalent. Vow tie-in: **Tethered Grounding**, **Defended System Prompt**.
- A **Typed Operation Schema Registry.** Each `(endpoint, operation)` pair has a registered payload type (e.g. `dialog/process → DialogProcessPayload`). The dispatcher refuses messages whose payload does not match the schema. Operators register handlers by typed payload, not by string key lookup. The 200-line `if/else` ladder in `AITuberMessageHandler.cs` becomes a per-payload class with a single `Handle(DialogProcessPayload)` method. Vow tie-in: **Smallness**, **Forge-Ready**.
- A **Capability-Scoped Bearer Token.** A Strengr-issued bearer for the control channel carries a list of permitted `(endpoint, operation)` scopes. The handler refuses operations outside the bearer's scope. The AITuber Controller use case gets a bearer scoped to `dialog/*`, `model/perform`, `model/appearance` — but never `llm/*` or `model/load`. The bearer also carries an expiration; long-running setups must rotate. Vow tie-in: **Surface Without Surveillance** generalized to **Capability-Scoped Surface**.
- A **Replay Log For Audit.** Every dispatched message is written to a structured log with `(timestamp, source_ip, bearer_id, endpoint, operation, payload_hash)`. Logs are written to Hjarta's audit table (the same audit-trail concept from `[[38_CHATMEMORY_INTEGRATION]]`). Operators auditing the doll's behavior after a suspicious livestream incident can replay the control plane. CDK has nothing equivalent. Vow tie-in: **Defended System Prompt** + **Audit-Trail-as-Return-Value**.
- A **Localhost-Only Sub-Channel for Sensitive Operations.** Operations that *must* be operator-side (system prompt updates, model URL allowlist updates, bearer token issuance) bind only to `127.0.0.1` and require a separate, operator-typed-at-the-terminal one-time code. The Tailnet bearer cannot issue these; only the local operator can. CDK has no such partition. Ember invents it.

A final invent: a **Protocol Version Negotiation Handshake.** The first message on every connection is a typed `HELLO {protocol_version, client_id, bearer}`. The server replies with `READY {server_version, accepted_endpoints, max_message_bytes, max_messages_per_second}` or `REJECT {reason}`. Clients see what they can do; servers see what they get. Future protocol changes are explicit. CDK has no version field; a CDK v1.0 client and a v0.7 server will fail in obscure ways. Ember pays the handshake cost upfront.

---

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c).*

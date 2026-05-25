---
codex_id: 25_AVATAR_PROTOCOL
title: Avatar Protocol — VMC Bidirectional, VRM Action Surface, VTube Studio
role: Architect
layer: Interface
status: draft
sap_source_refs:
  - main.js:14-180
  - main.js:1270-1290
  - py/vts_manager.py:1-235
  - server.py:2556-2606
  - static/vrm.html
ember_subsystem_targets: [Munnr, Hjarta]
cross_refs:
  - 10_domain/11_AVATAR_DOMAIN
  - 10_domain/16_VOICE_DOMAIN
  - 10_domain/1D_ROUTING_DOMAIN
  - 30_execution/32_AVATAR_RENDER_PIPELINE
  - 60_synthesis/64_AFFECTION_ENGINE_REIMAGINED
---

# Avatar Protocol
## VMC Bidirectional, VRM Action Surface, VTube Studio

*— Rúnhild Svartdóttir, Architect*

> *Three protocols, three languages, three ways to say "be happy now." A reader of the code learns the polyglot or gives up. The avatar speaks all of them; SAP teaches the LLM to speak in tags and lets the languages sort themselves out.*

This doc is the protocol contract for SAP's avatar surfaces — the three concrete wire formats by which the LLM's expressive intent reaches the body. It is the *interface* counterpart to the [[11_AVATAR_DOMAIN]] *domain* doc; where the domain doc names what the avatar owns, this doc names what crosses the wire.

---

## 1. The Subject

Three protocols, three audiences:

| Protocol | Audience | Transport | Wire format | Bidirectional? |
|---|---|---|---|---|
| **VRM action tags** | three-vrm renderer in `static/vrm.html` | WebSocket via `TTSConnectionManager.vrm_connections` | Text tags + audio bytes | No (server → client only) |
| **VTube Studio API** | external VTube Studio plugin | WebSocket (`ws://127.0.0.1:8001`) | JSON-RPC-style `{apiName, apiVersion, requestID, messageType, data}` | Yes |
| **VMC over OSC/UDP** | OBS, VSeeFace, Warudo, etc. | UDP/OSC | OSC messages with addresses `/VMC/Ext/*` | Yes |

Three audiences; three discipline levels; only one (VMC) is a true peer protocol.

---

## 2. How It Works

### 2.1 VRM action tags — the tag protocol

The LLM emits text containing inline tags like `<happy>` or `<scratchHead>`. The reply is streamed; the streaming code (in `server.py`, around the response broadcast) parses the tags out and dispatches:

- An *expression* tag (`<happy>`, `<angry>`, `<sad>`, `<neutral>`, `<surprised>`, `<relaxed>` — six fixed from `server.py:2557`) → sends a control message over the VRM WS to set the model's morph target.
- A *motion* tag (`<scratchHead>`, `<playFingers>`, etc., from `settings.VRMConfig.defaultMotions + userMotions`) → sends a control message to play a named animation clip.
- A *silence* tag (`<silence>...</silence>`, from `server.py:2552-2555`) → marks the contained text as not-for-TTS (used for inline image markdown).

The LLM is told the vocabulary in the system prompt (`server.py:2556-2575`):

> "你可以使用以下表情：\<happy\> \<angry\> \<sad\> \<neutral\> \<surprised\> \<relaxed\>"

> "你可以在句子开头插入表情符号以驱动人物的当前表情..."

The vocabulary is **declared in the prompt, not in a schema file**. To add a new expression, edit `server.py:2557`. To add a new motion, the settings have a `userMotions` list.

The wire to the VRM page is via `TTSConnectionManager.vrm_connections`. The renderer code in `static/js/vrm.js` (not deeply sampled here) handles tag parsing on the client side, dispatching to three-vrm's morph and animation APIs.

### 2.2 VTube Studio API — the WebSocket peer

`py/vts_manager.py:15-235` implements `VTSManager`. The protocol is documented at vtubestudio.com; SAP wraps it.

Every outbound message has shape:

```python
# /tmp/super-agent-party/py/vts_manager.py:79-82
payload = {
    "apiName": "VTubeStudioPublicAPI",
    "apiVersion": "1.0",
    "requestID": "AgentParty",
    "messageType": msg_type,
    "data": data
}
```

`requestID="AgentParty"` is constant — SAP does not correlate responses by request ID. Instead, responses are routed by `messageType` in `listen_vts` (line 203-219), which is a switch over message types.

**Inbound messages handled** (`py/vts_manager.py:209-219`):
- `AuthenticationTokenResponse` — token from first-time auth flow; saved to disk (line 211).
- `AuthenticationResponse` — auth-with-token result; if authenticated, refresh data.
- `HotkeysInCurrentModelResponse` — populate `available_hotkeys` (filtering out ToggleExpression which is handled via Expression API instead).
- `ExpressionStateResponse` — populate `model_expressions` with active flags.

**Outbound message types used:**
- `AuthenticationTokenRequest` / `AuthenticationRequest`
- `HotkeysInCurrentModelRequest`
- `ExpressionStateRequest`
- `ExpressionActivationRequest` (toggle expression on/off; exclusive)
- `HotkeyTriggerRequest` (fire a hotkey/motion)
- `InjectParameterDataRequest` (drive `MouthOpen` for lip-sync)

The lip-sync drive (line 181-191) sends:

```python
msg = {
    "apiName": "VTubeStudioPublicAPI", "apiVersion": "1.0",
    "requestID": "LipSync", "messageType": "InjectParameterDataRequest",
    "data": { 
        "faceFound": False, "mode": "set",
        "parameterValues": [
            {"id": "MouthOpen", "value": float(round(self.mouth_value, 3))}
        ]
    }
}
```

`faceFound: False` and `mode: "set"` together mean "override the parameter regardless of any face tracking," so SAP can drive the mouth independent of webcam-based tracking. Round to 3 decimals to keep the wire small.

The protocol is *bidirectional* but SAP's use is *mostly one-way* — outbound commands, inbound state queries. The only response-handling beyond auth and state refresh is the implicit "did the command succeed?" — silently checked by absence of error.

### 2.3 VMC over OSC/UDP — the peer protocol

`main.js:14-180` implements VMC on the Electron side. VMC is the *Virtual Motion Capture* protocol — a convention for shipping bone-pose + blendshape data between VTuber apps over OSC (Open Sound Control) over UDP.

**Receive** (`startVMCReceiver`, line 71-116):

```javascript
// /tmp/super-agent-party/main.js:71-115
function startVMCReceiver(cfg) {
  if (vmcReceiverActive) return;
  vmcUdpPort = new osc.UDPPort({
    localAddress: cfg.receive.host,
    localPort: cfg.receive.port,
    metadata: true,
  });
  vmcUdpPort.open();
  vmcUdpPort.on('message', (oscMsg) => {
    if (oscMsg.address === '/VMC/Ext/Bone/Pos') {
      // forward boneName + pos + rot to every VRM window
      vrmWindows.forEach(w => {
        if (!w.isDestroyed()) {
          w.webContents.send('vmc-bone', { boneName, position, rotation });
          w.webContents.send('vmc-osc-raw', oscMsg);
        }
      });
    }
    if (oscMsg.address === '/VMC/Ext/Blend/Val') { /* forward blendshape */ }
    if (oscMsg.address === '/VMC/Ext/Blend/Apply') { /* forward apply */ }
  });
  vmcReceiverActive = true;
}
```

So when an external VMC source (a webcam-based tracker like VSeeFace, or another VTuber app) sends pose data, SAP receives it on UDP and forwards to every open VRM window via Electron IPC (`webContents.send`). The VRM window's JS code (in `static/js/vrm.js`) then drives the three-vrm model with the pose. SAP is a *display* for external VMC.

**Send** (`sendVMCBoneMain`, line 127-149; `sendVMCBlendMain`, line 152-167):

```javascript
function sendVMCBoneMain(data) {
  // ... build OSC message
  const { host, port } = global.vmcCfg.send;
  const oscMsg = {
    address: `/VMC/Ext/Bone/Pos`,
    args: [...]
  };
  vmcSendSocket.send(oscMsg, port, host, (err) => {
    if (err) console.error('VMC send error:', err);
  });
}
```

SAP sends bone/blendshape data to the configured upstream — typically OBS for broadcast, or another VTuber app, or a multi-host VMC scene. The send target is `global.vmcCfg.send` — a process-global config (named in [[11_AVATAR_DOMAIN]] §3.4 as a multi-avatar limit).

### 2.4 The protocol crossovers

- The VRM-tag protocol *can* be conveyed over VMC to other apps — if the VRM window translates `<happy>` into a blendshape change, the resulting VMC stream carries the effect.
- The VTS protocol is *separate* from VRM/VMC — VTS is for Live2D models; VRM is for VRoid-style 3D; VMC is the cross-app pose interchange.
- A SAP user can run *both* a VRM window and a VTS-driven Live2D model in OBS simultaneously, and the LLM's `<happy>` tag drives both — VRM via the tag protocol, VTS via `trigger_hotkey` matching "happy" against the model's available expressions.

---

## 3. The Contract — Inputs, Outputs, Side Effects, Invariants

### 3.1 VRM tag protocol — inputs / outputs

- **Input from LLM:** text containing tags `<vocab_item>` at sentence start, possibly preceded by voice-style tags.
- **Output to renderer:** WebSocket message of form (inferred) `{type: "expression", value: "happy"}` or `{type: "motion", value: "scratchHead"}` plus audio bytes for lip-sync.
- **Vocabulary:** declared in the LLM system prompt; not validated against the renderer's capability.
- **Side effects:** the VRM model's morph or animation changes. Cross-platform via the renderer (browser-side).

### 3.2 VTS protocol — inputs / outputs

- **Input from SAP:** outbound messages of the form `{apiName, apiVersion, requestID, messageType, data}`.
- **Output from VTS:** inbound messages of the same form; types include `AuthenticationTokenResponse`, `ExpressionStateResponse`, etc.
- **Auth:** token-based; first-time issues a token, persisted at `<USER_DATA_DIR>/vts_token.txt`; subsequent runs reuse.
- **Side effects:** VTS's Live2D model changes expression / fires hotkey / has mouth value injected.

### 3.3 VMC protocol — inputs / outputs

- **Inbound:** OSC messages at three addresses (`/VMC/Ext/Bone/Pos`, `/VMC/Ext/Blend/Val`, `/VMC/Ext/Blend/Apply`).
- **Outbound:** OSC messages at the same three addresses to `global.vmcCfg.send.{host, port}`.
- **Encoding:** OSC (binary tag-value pairs).
- **Side effects:** Receive — VRM window updates pose. Send — external app receives pose stream.

### 3.4 Invariants enforced

- VTS: `authenticated == True` is required before action sends (lines 91, 100). The token-roundtrip is the only auth check.
- VMC: none. The UDP port is open to anyone who can send to it.
- VRM-tag: none — whatever the LLM emits is parsed; unrecognized tags are silently ignored (in the renderer code).

### 3.5 Invariants *not* enforced

- **VTS request correlation.** All requests use the constant `requestID="AgentParty"`. SAP cannot tell which response goes with which request.
- **VRM-tag vocabulary validation.** The LLM is told the vocab in prose; the parser silently drops unknown tags; the system has no way to know that "the LLM emitted `<dance>` and we ignored it."
- **VMC sender identity.** Anyone on the host (or LAN if firewall is open) can send VMC packets and SAP will dispatch them to the VRM window.
- **VMC rate limit.** A flood of bone packets is forwarded at the rate they arrive, throttled only by the renderer's ability to consume.

### 3.6 The leaks

Three interfaces, three different leak profiles:

1. **VRM-tag** leaks via *vocabulary drift* — the prompt says `<happy>` is allowed; the renderer may have lost that mapping; mismatches are silent.
2. **VTS** leaks via *request correlation absence* — async behavior under stress can attribute responses to wrong requests.
3. **VMC** leaks via *trust assumption* — anyone on the network can drive the body.

---

## 4. Where It Breaks and Where It Surprises

### 4.1 The constant requestID

`requestID="AgentParty"` (`py/vts_manager.py:81`) means SAP cannot multiplex requests. Two concurrent `ExpressionStateRequest`s could have their responses confused. In practice the responses are routed by `messageType` which is unique per request type, so the issue is theoretical for SAP's current usage — but a future need to issue two requests of the same type simultaneously would surface the bug.

### 4.2 The hardcoded vocabulary

Six expressions and a few motions at `server.py:2557`. To add `<thoughtful>` requires editing `server.py`. To allow a user-defined expression *that the model supports* requires both editing `server.py` *and* providing the morph target. No registry.

### 4.3 The VMC trust gap

VMC over UDP is unauthenticated. On a public LAN, anyone can drive the avatar. SAP does not bind to localhost by default; the host/port are user-configured (with `0.0.0.0` likely as default for receive). The Tailnet-default-bind preference of Volmarr applies here doubly.

### 4.4 The VTS auth-once

Once a VTS token is saved, it lives forever. There is no rotation, no expiry, no revoke surface. A leaked token is a leaked-forever token (or until the user deletes `vts_token.txt`).

### 4.5 The duplicate broadcast_to_vrm

Already noted in [[11_AVATAR_DOMAIN]] §3.1 and [[1D_ROUTING_DOMAIN]] §3.6 — three definitions of `broadcast_to_vrm` exist in `server.py`. The wire crossing the VRM protocol is consequently *which* of three implementations? The second one wins by definition order.

### 4.6 The crisp parts

- **VMC bidirectional UDP** — the right shape for cross-app pose interchange. Standards-compliant. Interoperable.
- **VTS token persistence** at `<USER_DATA_DIR>/vts_token.txt` — survives restart; no re-auth needed.
- **`InjectParameterDataRequest` lip-sync** — uses the documented VTS API correctly.
- **The three-protocol coexistence** — VRM-tag + VTS + VMC can all run simultaneously, driving different surfaces, from the same LLM tag emission.

---

## 5. Cross-References

- [[11_AVATAR_DOMAIN]] — the domain this interface serves
- [[16_VOICE_DOMAIN]] — TTS audio bytes that cross the same wire
- [[1D_ROUTING_DOMAIN]] — the WebSocket-fanout substrate
- [[30_execution/32_AVATAR_RENDER_PIPELINE]] (Forge) — the renderer-side details
- [[60_synthesis/64_AFFECTION_ENGINE_REIMAGINED]] (Cartographer) — the proper affect-to-expression mapping
- [[hermes:HEM-26_TUI_BACKEND_INTERFACE]] — Hermes has no avatar; this is one of the gap-filling docs

---

## What This Means for Ember

**Adopt:**
- **VMC bidirectional UDP** as Ember's body protocol surface. Standards-compliant. Lets Munnr-Líkneski interoperate with the existing VTuber tool ecosystem (VSeeFace, Warudo, VNyan, Tracking World) without writing per-tool adapters.
- **The token-on-disk auth persistence** of VTS (`<USER_DATA_DIR>/vts_token.txt`) — pattern applies to any peer-protocol with token-based auth.
- **The two-track broadcast** of `TTSConnectionManager.broadcast_to_vrm(bytes|str)` — bytes for audio, strings for control — but with the *typed-event* adaptation below.

**Adapt:**
- The **constant requestID** — adapt to **unique request IDs per call** for VTS and any other request-response protocol. Munnr's VTS adapter correlates by ID, not by message type.
- The **hardcoded vocabulary in `server.py`** — adapt to a **typed expression registry**. Each avatar surface (VRM, VTS, VMC) declares its supported expressions at registration; the LLM-facing prompt is built from the *intersection*; unsupported tag emissions raise a Sögumiðla audit event.
- The **VMC trust assumption** — adapt to **bind-by-default-to-tailnet** (per Volmarr's standing preference) plus a per-packet HMAC or a Tailscale-ACL-derived identity check.
- The **VTS auth-once-forever token** — adapt to **rotation policy**: token expires after N days; reauth surface in UI; revocation manifest.

**Avoid:**
- **Three definitions of the same broadcast method.** Lint, test, refuse.
- **A vocabulary declared only in prose.** Schema or no protocol.
- **A protocol that any LAN process can drive.**

**Invent:**
- **Líkneski — The Body Protocol.** Ember's proposed True Name for the avatar protocol surface. Líkneski owns: (1) the typed expression/motion vocabulary, (2) the per-surface adapter registry (VRM, VTS, VMC, terminal-emoji, log-only), (3) the affect-to-expression mapping (from Hjarta), (4) the lip-sync coupling (with Munnr). Every surface speaks Líkneski's typed events; per-surface translation is the adapter's job. SAP scatters this across `vts_manager.py` + `main.js` + `server.py:2556`; Ember names it.
- **The Expression Honesty Contract.** Líkneski refuses to emit an expression the LLM *asked for* if Hjarta's current affect state contradicts it. If the LLM emits `<happy>` while Hjarta reports `(valence: -0.3, arousal: 0.1)`, Líkneski substitutes `<neutral>` and emits an audit event. The Embodied Honesty Vow ([[60_synthesis/61_NEW_VOWS]]) operationalized.
- **The Multi-Surface Atomic Emit.** When Líkneski emits an expression, it dispatches *atomically* to every registered surface — VRM window, VTS model, VMC stream, terminal log. Either all surfaces receive it or none do. SAP fires each independently; Ember coordinates.
- **The Per-Surface Capability Probe.** At startup, every avatar adapter probes its surface's capabilities (which expressions are mapped, which motions exist, which morph targets respond). The capabilities are stored in Brunnr. The system prompt is built from the *guaranteed* intersection across active surfaces. SAP advertises the *union* and prays.
- **VMC Identity Tagging.** Outbound VMC messages from Ember carry a custom OSC argument identifying the source (`/VMC/Ext/Hermes/Identity ember-<realm>`). Receivers can filter for source. Combines with Tailnet identity for a verifiable trust path. The standard VMC protocol doesn't mandate this but it's compatible (extra args are silently ignored by spec-conformant receivers).
- **The Lip-Sync Calibration Routine.** At startup, Munnr runs a calibration utterance through the active TTS and *measures* the RMS/vowel-ratio distribution. The `vts_worker.rms_threshold` (hardcoded at 15000 in SAP, [[16_VOICE_DOMAIN]] §3.3) becomes a *learned* value per TTS engine. Swapping TTS engines does not desync the mouth.

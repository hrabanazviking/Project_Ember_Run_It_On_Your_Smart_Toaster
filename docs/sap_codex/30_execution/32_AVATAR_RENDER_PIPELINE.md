---
codex_id: 32_AVATAR_RENDER_PIPELINE
title: Avatar Render Pipeline — The Window That Pretends to Be a Body
role: Forge
layer: Execution
status: draft
sap_source_refs:
  - main.js:19 (vrmWindows array)
  - main.js:70-180 (VMC OSC send/receive)
  - main.js:995-1050 (start-vrm-window)
  - main.js:1214-1304 (VMC IPC handlers)
  - server.py:8361-8398 (WS endpoints)
  - server.py:9883-10254 (VRM/VRMA/Gauss upload)
  - py/vts_manager.py:15-70 (VTS bridge)
  - server.py:11628 (StaticFiles /vrm mount)
ember_subsystem_targets: [Munnr, Hjarta]
cross_refs:
  - 30_execution/30_ELECTRON_BOOTSTRAP
  - 30_execution/3B_AFFECTION_LOOP
  - 20_interface/25_AVATAR_PROTOCOL
  - 10_domain/11_AVATAR_DOMAIN
---

# Avatar Render Pipeline

> *Two transparent windows arguing about OSC frames at 60 Hz while a third window listens for the audio.*

Forge. Eldra. The body of SAP is a click-through `BrowserWindow` running WebGL with a VRM model loaded by Three.js, fed by a WebSocket from Python, expression-driven by audio RMS, optionally bridged to VTube Studio for Live2D, optionally fed bone data by external motion capture over OSC/UDP. Five moving parts. Here is how they synchronize.

## The Five Parts

1. **VRM Window** — a transparent always-on-top `BrowserWindow` created on demand (`main.js:995`).
2. **`/ws/vrm` WebSocket** — server → VRM window, carrying audio + animation events (`server.py:8361`).
3. **`/ws/subtitles` WebSocket** — server → overlay window, carrying caption text only (`server.py:8380`).
4. **VTS Bridge** — Python websocket client → VTube Studio API for Live2D models (`py/vts_manager.py`).
5. **VMC OSC** — Electron main process ↔ external motion-cap apps over UDP (`main.js:70–180`).

The VRM window is the visible body. The other four are the nerves feeding it.

## VRM Window: Click-Through Glass

```javascript
// main.js:1012-1035
const vrmWindow = new BrowserWindow({
  width: windowWidth,
  height: windowHeight,
  x, y,
  transparent: true,
  frame: false,
  alwaysOnTop: true,
  skipTaskbar: true,
  hasShadow: false,
  acceptFirstMouse: true,
  backgroundColor: 'rgba(0, 0, 0, 0)',
  webPreferences: {
    contextIsolation: true,
    nodeIntegration: true,
    enableRemoteModule: true,
    sandbox: false,
    webgl: true,
    webAudio: true,
    autoplayPolicy: 'no-user-gesture-required',
    ...
  }
});
await vrmWindow.loadURL(`http://${HOST}:${PORT}/vrm.html`);
```

Notice the trade-offs: `transparent: true` + `frame: false` + `alwaysOnTop: true` is the desktop-companion shape. `skipTaskbar: true` keeps it from cluttering Alt-Tab. `acceptFirstMouse: true` is a macOS thing — without it, the first click on the avatar would go to focus and not to the window's content. `autoplayPolicy: 'no-user-gesture-required'` is critical because the avatar will play TTS audio without any user interaction; Chrome's default would mute it.

The content is `http://127.0.0.1:<PORT>/vrm.html`, served by the StaticFiles mount on `/` (`server.py:11632`). The VRM model files themselves are served from `/vrm/<name>.vrm` via the dedicated mount (`server.py:11628`).

`nodeIntegration: true` + `sandbox: false` is a serious security relaxation. The VRM window can `require('fs')`. SAP needs this because the Three.js GLTF loader wants direct filesystem access for textures (the default Chrome XHR path is blocked by `webSecurity: false` + transparent window quirks). It is also a doorway. If you can trick the VRM window into loading a malicious VRM whose embedded JavaScript exploits something in the loader chain, you have Node access.

The window collection is tracked at `main.js:19` (`let vrmWindows = [];`). The lifecycle is push-on-create, filter-on-close. Multiple VRM windows can exist simultaneously — SAP supports multi-avatar group chats where each persona has its own window. The render cost adds up: each window is an independent Chromium renderer process. Two avatars on a 4-core laptop already saturate one CPU.

## The /ws/vrm WebSocket

```python
# server.py:8361-8378
@app.websocket("/ws/vrm")
async def vrm_websocket_endpoint(websocket: WebSocket):
    """VRM 窗口 WebSocket：接收主窗口发来的数据"""
    await tts_manager.connect_vrm(websocket)
    try:
        while True:
            msg = await websocket.receive()
            if "text" in msg:
                data = json.loads(msg["text"])
                if data.get('type') == 'animationComplete':
                    await tts_manager.send_to_main(msg["text"])
    except WebSocketDisconnect:
        tts_manager.disconnect_vrm(websocket)
```

The endpoint is bidirectional but **asymmetric**. Server-to-VRM carries the heavy traffic: audio chunks, animation triggers, expression commands. VRM-to-server only ever sends `animationComplete` callbacks so the server knows when to send the next TTS chunk. This back-pressure pattern prevents audio queue overflow when the network or Three.js animation is slower than TTS synthesis.

The `tts_manager` (referenced but defined elsewhere in `server.py`) maintains three connection pools:
- `main_connections` — the main UI window
- `vrm_connections` — every VRM avatar window
- `overlay_connections` — caption overlays

When TTS audio is generated, it fans out to every VRM window and every overlay. Multi-avatar groups talk in turn; SAP routes by adding speaker-ID metadata to each chunk and letting each renderer filter for its own ID.

## /tts/status: The Observability Patch

```python
# server.py:8391-8398
@app.get("/tts/status")
async def get_tts_status():
    return {
        "vrm_connections": len(tts_manager.vrm_connections),
        "vts_active": vts_instance.is_running,
        "overlay_connections": len(tts_manager.overlay_connections),
        "main_connections": len(tts_manager.main_connections)
    }
```

Four counters. That's all the observability there is for the avatar pipeline. If audio stops flowing and `vrm_connections == 1`, you know the connection is alive but the renderer is stuck. If `vrm_connections == 0`, the connection dropped. There is no per-message latency, no dropped-frame metric, no audio-queue-depth gauge. Anyone debugging an "avatar lip-sync is laggy" complaint is going to be guessing.

## VTS Bridge: The Live2D Alternative

`py/vts_manager.py` is a 235-line WebSocket client that connects to VTube Studio's plugin API (`ws://127.0.0.1:8001` by default, line 59) so SAP can drive a Live2D model in VTube Studio rather than a VRM model in its own window. The bridge is opt-in.

The key state:

```python
# py/vts_manager.py:15-40 (compressed)
class VTSManager:
    def __init__(self):
        self.vts_ws = None
        self.authenticated = False
        self.token_path = os.path.join(USER_DATA_DIR, 'vts_token.txt')
        self.token = self.load_token()
        self.is_running = False
        self.enabled_expressions = True
        self.enabled_motions = True
        self.mouth_value = 0.0
        self.mouth_smile = 0.0
        self.audio_queue = asyncio.Queue()
        ...
        self.sample_rate = 24000
        self.frame_ms = 0.035
        self.rms_threshold = 15000.0
        self.smooth_factor = 0.45
```

The lip-sync is RMS-driven. Audio comes in, the bridge computes RMS over a 35 ms frame, smooths it with an exponential filter (`smooth_factor = 0.45`), and posts the value to VTube Studio as a mouth-open parameter. `rms_threshold = 15000.0` is calibrated for "TTS high-volume output". A quieter audio source would never visibly open the mouth.

Authentication is token-based — the first connection prompts the user inside VTS to authorize the plugin, then SAP caches the granted token at `USER_DATA_DIR/vts_token.txt`. Subsequent connects reuse it. Reasonable. The token is unencrypted on disk; if the threat model includes a local-malware exfil, that's a credential-leak path.

This is **two parallel avatar stacks living in the same process**: VRM (via the browser window) and Live2D (via VTS). They are not synchronized to each other. If both are running, you get two avatars opening their mouths to the same TTS stream from different angles. This is a feature (multi-streaming, multi-angle) and a bug (a single avatar identity inhabiting two render pipelines whose lip-sync timing diverges by ~50 ms).

## VMC OSC: External Motion Capture

```javascript
// main.js:70-117 (compressed)
function startVMCReceiver(cfg) {
  if (vmcReceiverActive) return;
  vmcUdpPort = new osc.UDPPort({
    localAddress: '0.0.0.0',
    localPort: cfg.receive.port,
    metadata: true,
  });
  vmcUdpPort.open();
  vmcUdpPort.on('message', (oscMsg) => {
    if (oscMsg.address === '/VMC/Ext/Bone/Pos') {
      const [boneName, x, y, z, qx, qy, qz, qw] = oscMsg.args.map(v => v.value ?? v);
      vrmWindows.forEach(w => {
        if (!w.isDestroyed()) {
          w.webContents.send('vmc-bone', { boneName, position:{x,y,z}, rotation:{x:qx,y:qy,z:qz,w:qw} });
        }
      });
    }
    if (oscMsg.address === '/VMC/Ext/Blend/Val') { ... }
    if (oscMsg.address === '/VMC/Ext/Blend/Apply') { ... }
  });
}
```

VMC ("Virtual Motion Capture") is an OSC-over-UDP protocol used by face-tracking apps (iFacialMocap, MeowFace, OpenSeeFace, VSeeFace) to broadcast bone positions and blend-shape values. SAP can both receive (from a tracker) and send (impersonating a tracker, useful for piping computed avatar state into OBS via a VMC-aware capture filter).

Note that VMC traffic transits through Electron's main process, **not** through Python. The UDP socket lives in Node. Frame data goes:

```
External tracker app → UDP localhost:39539 → Electron main → IPC to vrmWindows → Three.js bone update
```

This is the right call for latency — a UDP frame round-tripping through Python would add 10–20 ms. The wrong call for portability: Linux headless servers (Docker) cannot run Electron, so no VMC. Computer control is also Electron-side ([[33_COMPUTER_CONTROL_LOOP]]) for the same reason.

`main.js:1230` registers the send side via IPC:

```javascript
ipcMain.handle('send-vmc-frame', (event, frameData) => {
  // Forwards frame to UDP target (host:port from vmcCfg.send)
});
```

The send side is used when SAP computes lip-sync or expression values internally and wants OBS or another VMC-aware app to render the avatar — SAP becomes the tracker.

## VRMA Motions: Pre-Recorded Animations

```python
# server.py:10094-10137 (compressed)
@app.post("/upload_vrma_motion")
async def upload_vrma_motion(...):
    unique_filename = f"{uuid.uuid4()}.vrma"
    # Save to USER_DATA_DIR/vrma/
```

VRMA is a VRM-companion animation format. SAP lets users upload pre-recorded motions (waving, dancing, idle loops) which are played by Three.js's `@pixiv/three-vrm-animation` library inside the VRM window. The server side is just file management — upload, list (`get_default_vrma_motions`, `get_user_vrma_motions`), delete. The actual motion blending happens in the browser.

There's a UUID-only filename validator at `server.py:10143` for delete:

```python
if not re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.vrma$", filename):
    raise HTTPException(...)
```

Reasonable — prevents path traversal. Same pattern at `/delete_vrm_model/{filename}` (10977) and `/delete_audio/{filename}` (9849). The validator is per-route, not centralized; one missing match = path traversal hole.

## Gauss Scenes: Photoreal Backdrops

`/upload_gauss_scene` (`server.py:10178`) accepts Gaussian Splat scenes — the photoreal-3D-scene format that exploded in 2024. SAP can render the avatar in front of a splat-rendered room. This is a 2025-era feature and it's optional; most users won't use it. The fact that SAP supports it tells you the project is active and chasing the avatar bleeding edge.

## The Rendering Loop, End-to-End

Pulling it all together for a single TTS utterance:

1. User types into the chat. `/v1/chat/completions` (`server.py:6912`) returns a streaming response.
2. As text chunks arrive, the chat handler sends them to `/tts` (`server.py:8400`).
3. TTS produces audio chunks.
4. Each audio chunk is broadcast to:
   - Every `vrm_connection` via `/ws/vrm` (audio bytes + animation metadata)
   - `vts_instance.audio_queue` (RMS extraction → mouth value)
   - Every `overlay_connection` via `/ws/subtitles` (caption text only)
5. VRM window plays the audio + drives morph targets from received RMS data + plays the named VRMA motion if a tool-call triggered one.
6. VTS bridge worker reads from audio_queue, computes RMS frames, posts mouth-open to VTube Studio.
7. If VMC send is enabled, the computed mouth/expression also goes out over UDP to OBS-side renderers.

Round-trip latency budget: TTS first-chunk arrival ~150 ms, WebSocket dispatch ~5 ms, Three.js render ~16 ms, VTS bridge frame ~35 ms. Total perceived lip-sync lag from "user pressed enter" to "avatar opens mouth": ~250–400 ms when local TTS is hot, ~1.5 s when using a cloud LLM and TTS is the bottleneck.

## Where It Breaks

- **`webSecurity: false`** (`main.js:406` for the main window; not explicitly set for VRM windows but inherited via similar `nodeIntegration: true` weakening). A malicious VRM file is a Node-RCE path.
- **No back-pressure on `tts_manager.connect_vrm` broadcasts**. If one VRM window has a slow renderer (low-end GPU), the broadcast loop awaits its send before the next, slowing every other client. There is no per-client queue or drop-old-frames policy.
- **VTS token on disk in plain text** (`USER_DATA_DIR/vts_token.txt`). Local-malware exfil path.
- **Two avatar stacks (VRM + VTS) with no shared timing source**. They lip-sync to the same audio independently. Result: visible drift between the on-desktop VRM and the OBS-streamed Live2D after ~30 seconds of speech.
- **VMC UDP socket bound to `0.0.0.0`** (`main.js:75`). Any host on the local network can spoof OSC bone-position messages to your avatar. For a livestreamer this could be weaponized as a stream-griefing tool.
- **No GPU resource ceiling**. Loading a 100MB VRM with 8K textures in a 2GB-RAM laptop will OOM the renderer with no graceful degradation. Three.js will just throw inside the loader and the VRM window will display black.

## Where It Surprises

- **The whole avatar stack is optional**. You can run SAP with zero VRM windows, zero VTS, zero VMC, and the server is unchanged. The bot-only Docker deployment ([[39_DOCKER_TOPOLOGY]]) does exactly this.
- **The RMS-based lip-sync** (`py/vts_manager.py:38`) is dumb but effective. SAP does not run a viseme model. It does not align mouth shapes to phonemes. It just opens the mouth in proportion to audio loudness. For Japanese TTS this is fine (mouth-open + smile covers ~80% of speech). For English with consonant clusters it looks rubbery. Calibration target: anime-companion aesthetic, not photoreal.
- **The `/ws/subtitles` endpoint is its own connection pool** (`server.py:8383`). Captions are fanned out separately from audio because they go to a different overlay window that doesn't play sound. Sensible isolation; rare in companion apps that bundle everything into one stream.
- **VMC bidirectional support**. SAP is one of the few open-source companion apps that can both consume external motion capture AND broadcast its own avatar state via VMC. This makes it usable as a virtual-tuber rig with proper OBS integration.

## Cross-References

- [[30_ELECTRON_BOOTSTRAP]] — VRM window IPC handlers live in `main.js`
- [[3B_AFFECTION_LOOP]] — affection state can trigger VRMA motions
- [[20_AVATAR_PROTOCOL]] — VMC frame format details
- [[10_AVATAR_DOMAIN]] — Architect's domain map of the whole avatar subsystem
- [[36_LIVESTREAM_INGEST_OVERVIEW]] — how livestream chat triggers avatar response

## What This Means for Ember

**Adopt:**

- **The transparent click-through window pattern** for any future Ember GUI presence on desktop. `BrowserWindow({transparent: true, frame: false, alwaysOnTop: true, skipTaskbar: true})` is the canonical recipe. Bind to Munnr.
- **The three-pool TTS broadcaster** (`main_connections`, `vrm_connections`, `overlay_connections`). Audio, animation, and captions have different consumers and different drop-policies. Munnr should keep them separate.
- **The `animationComplete` back-pressure callback**. The renderer telling the server when it has finished playing one chunk is the right shape for any streaming output where the consumer can be slower than the producer.
- **RMS-based lip-sync** as the baseline. It is dumb, cheap, and ships today. A phoneme-aligned upgrade is a future Ember Wave 4 axis, but only after the baseline ships.

**Adapt:**

- **The VRM window** — Ember should support it but never require it. The Pi-runnable Vow means presence must degrade to text-only / log-only ([[6B_LOW_POWER_EMBODIMENT]]). Bind embodied output to Munnr's `tier` parameter: `tier=full` → VRM window, `tier=overlay` → captions only, `tier=text` → terminal output, `tier=log` → file write.
- **VMC support** — adopt receive-only by default for safety, opt-in for send. The bidirectional support in SAP exposes a stream-griefing surface that Ember should not inherit without an explicit opt-in.
- **The VTS bridge** — adopt the pattern (Python websocket client → external avatar app) but generalize to a protocol-agnostic `AvatarBridge` interface so Live2D, NeRF-avatar, codec-avatar, and future formats can all plug in. SAP hardcodes the VTS protocol.

**Avoid:**

- **`webSecurity: false`** on any avatar window. Ember's threat model includes hostile VRM files. Same-origin and CSP must stay on.
- **Plaintext token on disk** for VTS. Ember should use the OS keyring (`keyring` Python package) for any third-party API credentials. Vow proposal: **Credential Discipline** — no API token written to disk unencrypted.
- **VMC UDP bound to `0.0.0.0`**. Default to `127.0.0.1`. Make `0.0.0.0` an explicit opt-in with a warning.
- **Hardcoded RMS threshold** (`rms_threshold = 15000.0`). Ember should adapt the threshold to the input stream's running peak. SAP's number is calibrated to one TTS engine; any other TTS or any sing-along feature breaks it.

**Invent:**

- **Hjarta-driven Expression Bias**. SAP's expressions are tool-call-triggered (the LLM emits `<expression: smile>` and the avatar plays smile.vrma). Ember's Hjarta (affect subsystem) should *continuously* bias the avatar's resting expression based on internal affect state — so a sad Ember sits with a subtly downturned mouth even when not speaking, rather than only emoting during commanded animations. This is the difference between *performing affect* and *being affect*. Vow tie-in: **Embodied Honesty** (from Wave 3 vows). The avatar reflects internal state, not theatre.
- **AvatarBridge Interface**. A typed Python interface `AvatarBridge` with implementations `VrmWindowBridge`, `Live2DBridge`, `TextOverlayBridge`, `LogOnlyBridge`. Munnr binds at runtime based on `tier`. New avatar formats are added by writing a new bridge, not by patching the TTS broadcast loop.
- **Avatar Resource Budget**. Each bridge declares its memory + GPU + framerate cost. Ember's runtime tier engine ([[63_PERFORMANCE_TIER_ENGINE]]) selects the highest-fidelity bridge whose budget fits the host. A Pi gets `LogOnlyBridge`; a workstation gets `VrmWindowBridge` with a 100 MB VRM; a phone gets `TextOverlayBridge`. No silent OOM. Vow tie-in: **Tiered Presence**.
- **Frame-Source-of-Truth Pin**. When VRM + VTS run together, one is pinned as the timing master. The other receives synthesized frame events from the master rather than computing its own RMS. Eliminates the 50-ms drift. Master is configurable but defaults to the VRM window (lowest perceptual latency for the seated user).

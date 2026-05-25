---
codex_id: 11_AVATAR_DOMAIN
title: Avatar Domain — VRM, Live2D, VTube Studio, and the VMC Spine
role: Architect
layer: Domain
status: draft
sap_source_refs:
  - main.js:14-180
  - main.js:995-1150
  - main.js:1270-1290
  - py/vts_manager.py:1-235
  - server.py:2556-2606
  - server.py:8167-8249
  - static/vrm.html
ember_subsystem_targets: [Munnr, Hjarta]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/16_VOICE_DOMAIN
  - 20_interface/25_AVATAR_PROTOCOL
  - 30_execution/32_AVATAR_RENDER_PIPELINE
  - 60_synthesis/64_AFFECTION_ENGINE_REIMAGINED
  - 60_synthesis/6B_LOW_POWER_EMBODIMENT
---

# Avatar Domain
## VRM, Live2D, VTube Studio, and the VMC Spine

*— Rúnhild Svartdóttir, Architect*

> *A body is a contract: it promises that what you see is what is happening inside. Break that contract often enough and the body becomes a mask. Most "AI companions" are masks. SAP almost isn't.*

The avatar subsystem is what makes SAP feel like presence rather than chat. It is also where SAP touches three protocols at once — Three.js's VRM runtime in the renderer, VTube Studio's WebSocket API for Live2D, and VMC over UDP/OSC for bidirectional motion capture — and where the architecture is unusually disciplined. This doc names what the avatar domain owns, what it does not own, and where Ember's Munnr (the mouth) and Hjarta (the heart) inherit the contract.

---

## 1. The Subject Itself

**What the domain is:** the avatar in SAP is *the visible body* — VRM models rendered in a transparent Electron window, Live2D models driven via the VTube Studio API, motion data flowing in and out via VMC. The domain owns the body's *appearance* (poses, expressions, lip-sync), the body's *protocols* (WS to VTS, UDP to VMC peers, IPC to Electron), and the body's *audio-coupled mouth* (lip-sync FFT). It does **not** own:

- Audio generation (that's [[16_VOICE_DOMAIN]])
- The decision *what* expression to emit (that's the LLM prompted by `server.py:2556-2606`)
- The emotional state behind the expression (that's nominally [[1A_AFFECTION_DOMAIN]] but in practice nothing)
- Scene composition for OBS (the VRM window is transparent; OBS captures it; SAP does not own the compositor)

**Where it lives:**

| Layer | File | LOC | Role |
|---|---|---|---|
| Renderer | `static/vrm.html` + `static/js/vrm.js` | (not measured here) | VRM via three-vrm; WebGL; transparent canvas |
| Live2D | `py/vts_manager.py` | 235 | VTube Studio WebSocket plugin + lip-sync FFT |
| Window | `main.js:995-1150` | ~150 | `start-vrm-window` / `stop-vrm-window` IPC handlers |
| VMC | `main.js:14-180` | ~165 | `osc.UDPPort` send + receive; bone + blendshape forwarding |
| Prompt-glue | `server.py:2556-2606` | ~50 | LLM-facing expression/motion/VTS tag instructions |
| Audio fanout | `server.py:8167-8249` (`TTSConnectionManager`) | ~80 | Routes TTS audio bytes to VRM WS clients |
| Models | `vrm/Alice.vrm`, `vrm/Bob.vrm` + `vrm/animations/`, `vrm/scene/` | — | Default characters + animation clips |

Three runtimes, four files, two protocols. The pieces are small and individually crisp. The cracks are at the *interactions* between them — see §3.

---

## 2. How It Works

### 2.1 VRM — the transparent window

`main.js:995` registers `ipcMain.handle('start-vrm-window', ...)`. The renderer creates a `BrowserWindow` with `transparent: true`, `frame: false`, `alwaysOnTop: true`, `skipTaskbar: true`, and `webgl: true` (`main.js:1012-1035`). That window navigates to `http://${HOST}:${PORT}/vrm.html` (`main.js:1038`) — meaning the VRM canvas is served by the Python server's static mount (`server.py:11632` mounts `static/`), and the *display* is an Electron window pointing at a Python-served HTML page.

This is **honest layering**. The renderer doesn't own the model files; it pulls them from `app.mount("/vrm", StaticFiles(...))` (`server.py:11628`). The Python side serves bytes. The JS side runs three-vrm. The Electron side owns the window properties (transparency, click-through, always-on-top).

Multiple VRM windows are supported (`vrmWindows = []` at `main.js:19`, and `start-vrm-window` pushes a new window into the array, `main.js:1043`). Each `closed` event filters the dead window out (`main.js:1046-1048`). So SAP can present **a party of characters simultaneously**, each in its own transparent window. This is the *plurality* embedded in "Super Agent Party."

### 2.2 VTube Studio — Live2D over WebSocket

`py/vts_manager.py:15-235` is `VTSManager`, a singleton (`vts_instance = VTSManager()` at `py/vts_manager.py:236`). It connects to a VTube Studio plugin endpoint over WS (`ws://127.0.0.1:8001` by default at `py/vts_manager.py:59`), authenticates via token persistence (`py/vts_manager.py:45-56`), and exposes three competencies:

- **Trigger hotkey by tag name** (`py/vts_manager.py:90-114`): the LLM emits `<happy>` in its reply; `trigger_hotkey` strips the `<>`, lowercases, and either toggles a matching *expression* (exclusive — turns off others) or fires a matching *motion* (one-shot).
- **Drive mouth from PCM** (`py/vts_manager.py:116-117` + `vts_worker` at line 119): TTS audio bytes are pushed onto an `asyncio.Queue`; the worker FFTs each frame, computes vowel/consonant energy ratios, and sends `InjectParameterDataRequest` with `MouthOpen` smoothed by `self.smooth_factor` (0.45). The math at `py/vts_manager.py:147-174` is real signal-processing — RMS gate at 400, volume normalisation by `(rms / 15000) ** 1.3`, vowel bins 10–88. It is the most disciplined code in the entire SAP repository.
- **Refresh available hotkeys + expressions** (`py/vts_manager.py:85-88`): polls VTS for `HotkeysInCurrentModelRequest` and `ExpressionStateRequest` post-auth; `listen_vts` (line 203) consumes responses to update `available_hotkeys` and `model_expressions`.

The integration with the conversation loop is `server.py:2580-2606`: if `vts_instance.is_running`, inject into the system prompt the available expression/hotkey tags and an active-state line. The LLM is told *what it can do*; it emits the tag; `vts_manager.trigger_hotkey` fires it.

### 2.3 VMC — bidirectional bone + blendshape over UDP/OSC

This is where SAP gets unusually serious. `main.js:14-180` sets up `osc.UDPPort` for receive (`startVMCReceiver`, line 71) and a `dgram.createSocket('udp4')` for send (`vmcSendSocket`, line 22). The receive path listens for three OSC addresses (`main.js:79-114`):

- `/VMC/Ext/Bone/Pos` — bone position + quaternion. Forwarded to every VRM window via `webContents.send('vmc-bone', {boneName, position, rotation})` and `vmc-osc-raw`.
- `/VMC/Ext/Blend/Val` — blendshape value. Forwarded as raw OSC.
- `/VMC/Ext/Blend/Apply` — blendshape apply trigger. Forwarded.

The send path mirrors: `sendVMCBoneMain` (line 127) and `sendVMCBlendMain` (line 152) build OSC messages from `global.vmcCfg.send.{host,port}` and emit. So SAP can **be a VMC source for OBS or other VTubers** (it sends bone pose), **and a VMC sink** (it receives external motion-capture and re-renders the model). One UDP port for receive, one socket for send, separate sides. Crisp.

VMC is what closes the loop between the AI's expressive intent (LLM emits `<happy>`) and the broadcast-quality output (OBS captures the VRM window OR receives the VMC stream directly). It is also what makes the avatar **physically interoperable** with mainstream VTuber tools (VSeeFace, Warudo, VNyan, Tracking World) without SAP needing to know about them.

### 2.4 The audio fanout — TTSConnectionManager

`server.py:8167` declares `TTSConnectionManager` with three connection lists: `main_connections`, `vrm_connections`, `overlay_connections`. The class has two routes:

- `connect_main(ws)` / `connect_vrm(ws)` / `connect_overlay(ws)` — per-surface accept
- `broadcast_to_vrm(message)` (lines 8191 and *again* at line 8228 — a real second definition that overwrites the first; see §3) — sends `bytes` only to VRM clients but sends `str` to *both* VRM **and** overlay clients

The byte-stream is the synthesized audio from `moss_tts.moss_generate_audio` (`py/moss_tts.py:240`). The string messages are expression tags, subtitle text, motion commands. So the same socket carries two payload types differentiated by `isinstance(message, bytes)`. This is functional and saves a connection, but type-on-runtime branching at a fanout point is the kind of decision that grows teeth as the protocol grows.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The duplicate `broadcast_to_vrm`

`server.py:8191` and `server.py:8228` both define `async def broadcast_to_vrm(self, message)`. The second definition wins. The first is dead code. The second is the one with the overlay-fan-out behavior. There is also a third, *orphaned* `async def broadcast_to_vrm(self, message)` at `server.py:8251` — defined at module level instead of inside the class, an indentation mistake that survives because nothing calls it. The avatar's most-trafficked broadcast surface is duplicated and orphaned in the same file.

### 3.2 No model-state validation

`vts_manager.model_expressions` (`py/vts_manager.py:32`) is populated by `_on_message` for `ExpressionStateResponse` (`py/vts_manager.py:218-219`). There is no schema check on the response. If VTube Studio returns an unexpected shape (because of a version mismatch or a desync), the manager silently caches garbage and the `trigger_hotkey` loop in `py/vts_manager.py:94-107` will iterate over it without complaint. Compare to `py/mcp_clients.py:121` where every `send_ping` has a 3-second timeout that triggers reconnect — that discipline did not propagate to VTS.

### 3.3 The lip-sync RMS is hardcoded

`py/vts_manager.py:38` sets `self.rms_threshold = 15000.0` and `self.smooth_factor = 0.45` as instance defaults. These are TTS-amplitude-specific magic numbers. If the TTS engine is swapped (which it can be — there's no contract saying TTS must be `moss_tts`), the lip-sync will desync. There is no calibration routine. There is no auto-gain.

### 3.4 VMC routing is global

`global.vmcCfg.send` (`main.js:132`) is a process-global config. There is no way for two different VRM windows to send VMC to different upstreams. So if SAP is hosting a *party* of avatars (its eponymous claim), all of them broadcast to the same VMC target. The plurality breaks at the VMC layer.

### 3.5 The transparent-window trick depends on compositor support

`main.js:1017` `transparent: true` works on every desktop OS *with a compositor*. Linux desktops without a compositing window manager (think i3 without picom, or some Wayland configurations) will render the window with a black background. SAP does not detect this; it silently produces an unusable avatar window on those hosts. Compare to the disciplined `py/sleep_guard.py:139` which explicitly logs `未找到 systemd-inhibit 或 xdotool` — the avatar layer does not extend the same courtesy.

### 3.6 The most disciplined module in SAP

`py/vts_manager.py` is, paradoxically, the cleanest file in this codebase. Token persistence on disk (lines 45-56), async-queue worker decoupling (line 119), bounded smoothing (line 173), per-frame RMS gating, exclusive-expression bookkeeping (line 102). It reads like it was written by someone who genuinely cared about the avatar feeling alive. The lip-sync FFT at lines 147-174 is the kind of code Ember should *aspire* to elsewhere.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 4 for the domain's place in the whole
- [[16_VOICE_DOMAIN]] for the TTS that feeds lip-sync
- [[20_interface/25_AVATAR_PROTOCOL]] for the full protocol contract
- [[30_execution/32_AVATAR_RENDER_PIPELINE]] for the render-loop execution doc (Forge writes this)
- [[60_synthesis/6B_LOW_POWER_EMBODIMENT]] for the tier-collapse strategy (no VRM on Pi)
- [[60_synthesis/64_AFFECTION_ENGINE_REIMAGINED]] for the emotion-to-expression mapping that SAP fakes via prompt
- [[hermes:HEM-26_TUI_BACKEND_INTERFACE]] — Hermes has no avatar; this is one of the three gaps the SAP codex is for

---

## What This Means for Ember

**Adopt:**
- `py/vts_manager.py` *whole* — singleton with async-queue lip-sync worker, token persistence, exclusive-expression bookkeeping. This is the template Munnr should use for any expressive-output adapter. Rename to `vts_skírnir` ("VTS-clarifier") if Norse-faithful.
- The **two-protocol model** — VTube Studio (Live2D, WS) for desk presence; VMC (UDP/OSC) for broadcast-quality interop. Adopt both as Munnr's optional surfaces, with `HAS_VTS` / `HAS_VMC` lazy flags per the modular-authorship pattern of `py/computer_use_tool.py:18`.
- The **transparent-window-served-by-server** layering — Electron owns the window, Python owns the asset. Apply to any Ember surface that needs OBS-friendly rendering.

**Adapt:**
- SAP's **prompt-injected tags** for expression (`server.py:2556-2606`) — the *mechanism* (LLM emits `<happy>`, regex extracts) is sound, but the *injection point* must move to Ember's Defended System Prompt typed surface, not string concatenation. The tag vocabulary becomes a typed enum, validated before injection.
- The **`TTSConnectionManager` three-list pattern** — adapt as a per-surface subscription with typed events (audio bytes vs control strings), routed through Ember's proposed `Sögumiðla` event bus (see [[10_DOMAIN_MAP]] §invent). The branch-on-`isinstance(bytes)` is too implicit.
- VMC's **bidirectional UDP** — adapt as Ember's body-protocol layer (proposed True Name: **Líkneski** — image/effigy). Ember on a Pi without VRM still emits VMC bone targets; Ember on a workstation renders them locally and re-broadcasts.
- Per-VRM-window VMC config — SAP's `global.vmcCfg.send` becomes per-window in Ember, so a multi-avatar party can route to different OBS scenes.

**Avoid:**
- **Duplicate-and-orphaned method definitions** like the two/three `broadcast_to_vrm` in `server.py:8191/8228/8251`. Ember's CI must catch redefinitions in the same class. A linter rule, not a hope.
- **Hardcoded amplitude constants** for lip-sync. Calibrate against the actual TTS output at startup; cache the calibration; recompute when TTS changes.
- **Silent failure of transparency on compositor-less Linux.** Detect and warn at startup, with a fallback to a chroma-key background. Graceful Offline applies to graphics too.
- **Process-global VMC config** when the system claims plurality.

**Invent:**
- **The Embodied Honesty Vow.** Avatar expression *must* be derived from an introspectable Ember internal state (Hjarta's current vector + Strengr's current focus + Brunnr's last retrieval), not invented by the LLM. SAP fakes the affect by asking the LLM to nicely emit `<happy>`. Ember refuses: an expression tag emitted by Munnr is a *report* on real state, not a *performance*. If the state vector says neutral, Munnr says `<neutral>`. This requires the affection reimagination in [[60_synthesis/64_AFFECTION_ENGINE_REIMAGINED]].
- **The Avatar Stand-In.** On a Pi (no VRM, no Live2D), Munnr still emits the *audit trace* of expressions — `[expr=happy intensity=0.6 reason="user shared good news"]` to a log. The body is absent; the *intent* still lives. This becomes the [[60_synthesis/6B_LOW_POWER_EMBODIMENT]] surface.
- **Cross-Host Body Migration.** A Pi-Ember running in text mode hands off its current Hjarta vector + last expression intent to a laptop-Ember at the same moment a VRM window opens there. The body migrates with the state. Implemented via the proposed [[60_synthesis/62_PARTY_PROTOCOL]].
- **Tag-Vocabulary Validation.** Every avatar surface (VRM, Live2D/VTS, VMC) declares its tag vocabulary at registration; Ember's system-prompt builder *only* offers the intersection of available vocabularies to the LLM. SAP advertises the union and prays the LLM doesn't emit `<dance>` when only `<happy>` exists.

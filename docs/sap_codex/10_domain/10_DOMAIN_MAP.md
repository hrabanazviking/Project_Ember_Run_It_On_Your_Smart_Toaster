---
codex_id: 10_DOMAIN_MAP
title: The Domain Map of Super Agent Party — Bones, Joints, and the Cracks Between
role: Architect
layer: Domain
status: draft
sap_source_refs:
  - server.py:1-700
  - server.py:10930-11640
  - main.js:1-200
  - main.js:995-1150
  - py/agent.py:1-66
  - py/affection_system.py:1-64
  - py/behavior_engine.py:1-225
  - py/sub_agent.py:1-100
  - py/task_center.py:1-235
  - py/scheduler.py:1-134
  - py/ws_manager.py:1-50
  - py/live_router.py:1-100
  - py/overlay_router.py:1-82
  - py/mcp_clients.py:1-189
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 10_domain/11_AVATAR_DOMAIN
  - 10_domain/12_AGENT_CORE_DOMAIN
  - 10_domain/14_MESSAGING_DOMAIN
  - 10_domain/1A_AFFECTION_DOMAIN
  - 10_domain/1D_ROUTING_DOMAIN
  - 30_execution/31_PYTHON_SERVER
  - 30_execution/30_ELECTRON_BOOTSTRAP
  - 60_synthesis/60_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/62_PARTY_PROTOCOL
---

# The Domain Map of Super Agent Party
## Bones, Joints, and the Cracks Between

*— Rúnhild Svartdóttir, Architect*

> *Every great hall is a question about ownership. Who tends the fire? Who keeps the door? Who feeds the dogs? A system whose answers are clear can be defended. A system whose answers are blurred is already on fire — it just hasn't noticed yet.*

Super Agent Party calls itself "self-hosted Neuro-sama + OpenInterpreter." That is its marketing pose. Its architecture is something stranger: an Electron shell hosting a single eleven-thousand-line Python file that runs sixty-three peer modules, eight messaging bots, three livestream listeners, two voice runtimes, a VRM renderer, and a regex-driven heart. To understand what Ember can learn from it, you must first see where the bones stop and the connective tissue begins. This is that map. The deeper anatomies live in the sister docs ([[11_AVATAR_DOMAIN]] through [[1D_ROUTING_DOMAIN]] and the [[20_MCP_INTEGRATION]] family); here I show you the whole.

---

## 1. The Fourteen Domains of SAP

A *domain* in SAP is a region of the codebase where one concept is meant to rule. Some of those regions are honored. Some are violated wholesale at every line of `server.py`. The number that follows is the number of domains the code *implies*, not the number `server.py` *respects*.

| # | Domain | Where it lives | What it owns | What it does NOT own |
|---|---|---|---|---|
| 1 | **Electron Shell** | `main.js` (2,100 LOC) | Process lifecycle, window management (`vrmWindows`, `shotOverlay`), IPC bridge, VMC UDP socket, system tray, auto-updater | Reasoning, model calls, persistence beyond config |
| 2 | **Python Server** | `server.py` (11,652 LOC) | Routes, dispatch, settings, conversation state, tool composition, system-prompt assembly, model adapter glue | Anything it should have delegated but didn't (which is most of it) |
| 3 | **Agent Core** | `py/sub_agent.py` (367) + `py/task_center.py` (233) + `py/scheduler.py` (134) | Long-running task lifecycle, sub-agent execution, schedule-and-fire, multi-platform result push | Conversation loop (that's `server.py`), reasoning model (that's the adapters) |
| 4 | **Avatar (VRM + Live2D + VMC)** | `py/vts_manager.py` (235) + `static/vrm.html` + `static/js/vrm.js` + `main.js:995-1150` + `main.js:70-180` | VRM window spawning, VTube Studio WS protocol, lip-sync FFT, VMC bidirectional UDP, expression hotkeys | Audio generation (TTS), text-to-expression mapping (server prompts) |
| 5 | **Voice (TTS + ASR)** | `py/moss_tts.py` (267) + `py/sherpa_asr.py` (93) + `py/moss_model_manager.py` + `py/sherpa_model_manager.py` | Audio synthesis, audio recognition, model lazy-load, audio quality validation | Routing of audio to surfaces (`TTSConnectionManager` in `server.py`) |
| 6 | **Messaging Mesh (8 IMs)** | `py/qq_bot_manager.py`, `wechat_bot_manager.py`, `wecom_bot_manager.py`, `feishu_bot_manager.py`, `dingtalk_bot_manager.py`, `telegram_bot_manager.py` + `telegram_client.py`, `discord_bot_manager.py`, `slack_bot_manager.py` | Per-platform connection thread, SDK lifecycle, message dispatch, behavior_engine handler registration | Reasoning, TTS, affection state |
| 7 | **Broadcast (3 livestreams)** | `py/blivedm/` (Bilibili) + `py/ytdm.py` (YouTube) + `py/twitch_service.py` + `py/live_router.py` (546) | Live comment ingest, danmu broadcast over WS, gift/like/super-chat normalization | Avatar rendering, voice synthesis |
| 8 | **Retrieval (KB + Embeddings)** | `py/know_base.py` (390) + `py/minilm_router.py` (188) + `py/ebd_api.py` (49) + `py/ebd_model_manager.py` (179) | Document chunking, BM25 + FAISS hybrid index, MiniLM ONNX embeddings (`/minilm/embeddings` route), rerank | Long-term memory (that's `mem0`-style code embedded in `server.py`) |
| 9 | **Behavior Engine** | `py/behavior_engine.py` (224) + `py/autoBehavior.py` (97) | Time / no-input / cycle trigger engine, per-platform handler registry, behavior config hot-reload | Affection state, sub-agent execution |
| 10 | **Affection** | `py/affection_system.py` (64) + `py/affection_api.py` (29) | Regex extraction of `<user=X love=N>` tags from LLM output, JSON persistence at `affection_data.json` | A state machine. Decay. Time. Validation. (None of those exist — see [[1A_AFFECTION_DOMAIN]]) |
| 11 | **Tool Surface** | `py/agent_tool.py` (53) + `py/a2a_tool.py` (39) + `py/llm_tool.py` (190) + `py/web_search.py` (1059) + `py/utility_tools.py` (551) + `py/task_tools.py` (288) + `py/computer_use_tool.py` (575) + `py/cdp_tool.py` (559) + `py/cli_tool.py` (2,668) + `py/code_interpreter.py` (91) + `py/comfyui_tool.py` (217) + `py/custom_http.py` (41) | OpenAI-shape tool definitions and their handlers | Tool registry as a first-class object (there isn't one — see §5) |
| 12 | **Extension Surface** | `py/extensions.py` (631) + `py/skills.py` (681) + `py/node_runner.py` (123) + `py/node_api.py` + `py/uv_api.py` + `py/docker_api.py` + `skills/` (4 manifests) | Skill install (GitHub/zip), per-extension Node process, package.json-driven port, Electron-vs-Docker exec routing | Skill discovery at LLM dispatch time (that's still in `server.py`) |
| 13 | **MCP Surface** | `py/mcp_clients.py` (189) + `mcp.mount()` at `server.py:11626` | Outbound MCP client (`McpClient` with auto-reconnect monitor), inbound MCP server mount via FastApiMCP | Per-tool MCP-vs-native abstraction |
| 14 | **Routing Fabric** | `py/ws_manager.py` (49) + `py/overlay_router.py` (81) + `py/live_router.py` (546) + `py/mode_change.py` (136) + `TTSConnectionManager` (`server.py:8167-8249`) | WebSocket fanout (settings updates, task notifications, danmu, TTS audio, VRM commands), permission-mode hot-swap | Per-message addressing (every manager has its own broadcast pattern — see [[1D_ROUTING_DOMAIN]]) |

Fourteen domains, ten of which are honored at file granularity, four of which are fragments scattered across `server.py`. The number matters because each is a *Boundary Vow*: a place where Ember will need to draw a line where SAP did not. The cracks are most visible in domains 10, 11, and 14 — affection, tools, and routing — where the code keeps reaching back into `server.py` instead of completing its module.

---

## 2. The Layered View

If the domain table is the bone count, this is the spine. SAP stacks from device hardware at the bottom to user surface at the top:

```
┌──────────────────────────────────────────────────────────────────────────┐
│  USER SURFACES                                                           │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────┐ ┌───────────────┐  │
│  │ Electron UI  │ │ VRM Window   │ │ 8 IM Bots      │ │ 3 Livestreams │  │
│  │ static/      │ │ static/      │ │ qq/wechat/...  │ │ blivedm/ytdm/ │  │
│  │ index.html   │ │ vrm.html     │ │ _bot_manager   │ │ twitch_service│  │
│  └──────┬───────┘ └──────┬───────┘ └───────┬────────┘ └───────┬───────┘  │
│         │                │                 │                  │          │
└─────────┼────────────────┼─────────────────┼──────────────────┼──────────┘
          │                │                 │                  │
┌─────────┼────────────────┼─────────────────┼──────────────────┼──────────┐
│  ROUTING FABRIC                                                          │
│  ws_manager.broadcast  │  TTSConnectionManager  │  overlay_manager       │
│  live_router.manager   │  danmaku_overlay WS    │  behavior_engine       │
└─────────┬────────────────┬─────────────────┬──────────────────┬──────────┘
          │                │                 │                  │
┌─────────┴────────────────┴─────────────────┴──────────────────┴──────────┐
│  PYTHON SERVER — server.py (11,652 LOC, single file)                     │
│  /v1/chat/completions  ── system-prompt assembly ── tool composition     │
│  /simple_chat          ── short-circuit reasoning                        │
│  /api/* mount points   ── 16+ sub-routers                                │
│  TTSConnectionManager  ── audio fanout                                   │
└─────────┬────────────────────────────────┬───────────────────────────────┘
          │                                │
┌─────────┴────────────┐  ┌────────────────┴──────────────────────────────┐
│  COGNITIVE LAYER     │  │  CAPABILITY LAYER                             │
│  agent_tool.py       │  │  computer_use_tool / cdp_tool / cli_tool      │
│  a2a_tool.py         │  │  code_interpreter / comfyui_tool              │
│  sub_agent.py        │  │  web_search / load_files / pollinations       │
│  task_center.py      │  │  ClaudeAsOpenAI / GeminiAsOpenAI              │
│  scheduler.py        │  │  llm_tool / utility_tools                     │
└─────────┬────────────┘  └─────────────────┬─────────────────────────────┘
          │                                 │
┌─────────┴─────────────────────────────────┴─────────────────────────────┐
│  KNOWLEDGE LAYER                                                        │
│  know_base.py (BM25 + FAISS hybrid)                                     │
│  minilm_router.py (ONNX MiniLM, /minilm/embeddings)                     │
│  ebd_api.py (embedding-dims probe)                                      │
│  affection_system.py (regex + JSON)                                     │
│  load_files.py (752 LOC; multi-format ingest)                           │
└─────────┬───────────────────────────────────────────────────────────────┘
          │
┌─────────┴───────────────────────────────────────────────────────────────┐
│  MEDIA LAYER                                                            │
│  moss_tts.py (MOSS-TTS-Nano-100M-ONNX)                                  │
│  sherpa_asr.py (sherpa-onnx sense-voice)                                │
│  vts_manager.py (VTube Studio WebSocket)                                │
│  blivedm/ (Bilibili open platform)                                      │
└─────────┬───────────────────────────────────────────────────────────────┘
          │
┌─────────┴───────────────────────────────────────────────────────────────┐
│  EXECUTION LAYER                                                        │
│  node_runner.py (per-extension subprocess, port-bound)                  │
│  docker_api.py / node_api.py / uv_api.py (probes only)                  │
│  extensions.py (zip/git install, Windows-readonly handling)             │
│  skills.py (GitHub URL → SKILL.md install)                              │
└─────────┬───────────────────────────────────────────────────────────────┘
          │
┌─────────┴───────────────────────────────────────────────────────────────┐
│  HOST LAYER                                                             │
│  Electron + main.js — IPC bridge, VMC UDP, screen capture               │
│  sleep_guard.py — cross-platform anti-sleep (caffeinate / systemd       │
│                   inhibit / xdotool fallback)                           │
│  pyautogui + pyperclip — guarded by `GUI_AVAILABLE` flag                │
└─────────────────────────────────────────────────────────────────────────┘
```

Notice the inversion: the *Python Server* sits in the middle, and almost everything passes through it. `server.py` is not a layer — it is the gravity well that has eaten the architecture. We will name this anti-pattern The Server-Eaten Codebase in §5.

---

## 3. The Dependency Graph — Honest Edition

The README implies clean module separation. The imports tell a different story. From `server.py:1-700` and `server.py:10930-11640` the actual graph is:

```
                            server.py (11,652 LOC)
                                   │
            ┌──────────────────────┼──────────────────────────────┐
            │                      │                              │
   imports 60+ py/* modules   include_router(16 routers)    mounts 5 static dirs
            │                      │                              │
   ──── inversion of control ──────┴──────────────────────────────┘
            │
            ▼
   py/* modules also import from each other:
     sub_agent.py ──► task_center.py ──► (file I/O)
     sub_agent.py ──► behavior_engine.py ──► (handlers registered by IM bots)
     scheduler.py ──► sub_agent.py
     8 *_bot_manager.py ──► behavior_engine.py (registers handler)
     8 *_bot_manager.py ──► AsyncOpenAI("http://127.0.0.1:{port}/v1") ──► back to server.py
     live_router.py ──► blivedm/ + ytdm.py + twitch_service.py
     mcp_clients.py ──► mcp.* (SDK)
     know_base.py ──► langchain_* + FAISS + httpx ──► minilm_router /embeddings
```

The most striking edge is the self-loop: every IM bot calls `http://127.0.0.1:{port}/v1/chat/completions` (`qq_bot_manager.py:20`, `feishu_bot_manager.py:17`, etc.) — they do not import the reasoning logic, they HTTP-call back into `server.py`. This is **architecturally clever** (it keeps each bot independent of conversation internals) and **operationally fragile** (if `server.py` is hung, every bot is hung, and the local loopback is unauthenticated).

The second striking pattern is **bus-by-broadcast**. Three separate WebSocket manager classes exist (`ws_manager.ConnectionManager`, `live_router.ConnectionManager`, `overlay_router.DanmakuOverlayManager`, `TTSConnectionManager` in `server.py:8167`) — none of them know about the others. There is no shared bus. This is the routing fabric crack named in [[1D_ROUTING_DOMAIN]].

---

## 4. The Lifecycle — How One Turn Travels

Trace one user message from voice to mouth, citing files:

1. **Audio in** → `sherpa_asr.sherpa_recognize` (`py/sherpa_asr.py:82`) — `asyncio.to_thread` wraps the ONNX call.
2. **Text arrives** at `/v1/chat/completions` in `server.py`.
3. **System prompts assembled**, *in sequence*, by `server.py`:
   - VRM expression instructions if `settings['VRMConfig']['enabledExpressions']` (`server.py:2556`)
   - VRM motion instructions if `enabledMotions` (`server.py:2559`)
   - VTube Studio expression/hotkey tags if `vts_instance.is_running` (`server.py:2580`)
   - Affection tag protocol if `loveSettings.enabled` (`server.py:2611`)
   - autoBehavior tool injection if `tools.autoBehavior.enabled` (`server.py:3553`)
4. **Tools assembled** from 14+ sources (`server.py:1037-1170`), conditionally enabled per setting.
5. **Model adapter** — one of `ClaudeAsOpenAI` / `GeminiAsOpenAI` / `dify_openai` / direct OpenAI SDK — streams back.
6. **Side-effects fire** on completion:
   - `extract_and_update_affection(full_content)` — regex-mines the response for `<user=X love=N>` and writes JSON (`server.py:5358`, `py/affection_system.py:37`)
   - Memory infer task spawned (`server.py:5368`)
   - VRM/VTS expression broadcast via `TTSConnectionManager.broadcast_to_vrm` (`server.py:8228`)
   - Subtitle broadcast via `overlay_connections`
   - TTS request to `moss_tts.moss_generate_audio` (`py/moss_tts.py:240`) → audio bytes → `broadcast_to_vrm` again
7. **Mouth speaks** — VRM page (or VTS) receives audio bytes, drives lip-sync (`vts_manager.vts_worker`, `py/vts_manager.py:119`)

Seven phases. Each phase touches a different domain. No phase is owned by one module — every phase reads from `server.py` and writes to a side-effect target chosen by `server.py`. The **architecture is centripetal**: everything circles `server.py` because nothing else has the authority to compose. This is the SAP design's load-bearing flaw.

---

## 5. Where the Bones Are Cracked

### 5.1 The Server-Eaten Codebase

`server.py` is 11,652 lines (`wc -l` confirms). It imports 60+ peer modules and contains the only place where their outputs are composed into behavior. Three consequences:

- **No reasoning kernel.** What `py/agent.py` *should* be — the conversation loop, the tool dispatcher, the memory hand-off — is instead scattered across `server.py:2400-6000`. The file named `py/agent.py` is 65 lines that gate per-project tool allowlists (`py/agent.py:9`). The actual cognition is `server.py`'s monolith.
- **System prompts as god-objects.** The system message is built by string-concatenation in `server.py:2556-2675`, mixing VRM, VTS, affection, autoBehavior, A2UI, and sticker pack instructions. There is no typed surface; there is no precedence rule; there is no test for what wins when two domains both want to inject. This violates Ember's proposed Vow of Defended System Prompt directly (see [[hermes:HEM-19_BOUNDARY_LAW]]).
- **Side-effects are imperative trailers.** Affection extraction (`server.py:5358`), memory infer (`server.py:5364`), TTS broadcast — all fire as imperative code at the end of the stream handler. None are subscribed to an event bus. Adding a sixth side-effect means another `if settings[...]: do_thing()` block in the trailer.

### 5.2 The Affection Mirage

The briefing for this codex called `affection_system.py` "an actual emotional state machine." The code disagrees. `py/affection_system.py:37-64` is **a regex that pulls `<user=X love=N>` out of LLM output and writes it to JSON**. There is no decay. There is no clamp. There is no time component. There is no validation that "love" stays inside a meaningful range. The LLM both *invents* the numbers and *signs off* on them by emitting the tag — and SAP trusts the tag. The state-machine prose is in `server.py:2653-2670`, in a system prompt that asks the model nicely to "evaluate or fine-tune these values" and "be reasonable (±5 per turn)." That is not a state machine. It is a vibe with a JSON file. See [[1A_AFFECTION_DOMAIN]] for the autopsy.

### 5.3 Three WS Managers, No Bus

`py/ws_manager.py:9` defines `ConnectionManager` with broadcast. `py/live_router.py:53` defines a separate `ConnectionManager` with its own broadcast. `py/overlay_router.py:18` defines `DanmakuOverlayManager` with its own. `server.py:8167` defines `TTSConnectionManager` with *three* connection lists (main, vrm, overlay). None reference each other. A "show subtitle" event can travel three different code paths depending on which surface registered the listener. See [[1D_ROUTING_DOMAIN]] for the mesh.

### 5.4 The Tool Registry That Isn't

There is no `Tool` class. There is no registry. Tools are dicts with the shape `{"type": "function", "function": {...}}` defined inline in their own files (`py/autoBehavior.py:43`, `py/random_topic.py:133`, `py/agent_tool.py:13`, etc.). Composition happens in `server.py:3353-3420`, where dozens of `if settings[...]['enabled']:` blocks decide whether to include each tool. Hot-swap a tool? Edit `server.py`. Test a tool in isolation? You can't — its dispatch lives in `server.py` too.

### 5.5 Same-Process LLM Self-Calls

`py/sub_agent.py:28` builds `self.chat_endpoint = f"http://127.0.0.1:{self.port}/v1/chat/completions"` and HTTP-calls it. Every IM bot does the same (`py/qq_bot_manager.py:20`). This is real-world A2A simulation over localhost, and it is fascinating: it makes each subsystem a network client of the main process, gaining decoupling but losing in-process call efficiency and gaining authentication-free trust on `127.0.0.1`. We will recommend [[20_MCP_INTEGRATION]] over HTTP self-loop for Ember.

---

## 6. The Honored Boundaries

Not everything is broken. Several SAP domains are crisp, modular, and worth adopting.

- **`py/sleep_guard.py`** — cross-platform anti-sleep with native-API → systemd-inhibit → xdotool fallback (`py/sleep_guard.py:30-160`). Three platforms, one interface. Worth lifting whole.
- **`py/mcp_clients.py:84-189`** — `McpClient` with a `_connection_monitor` daemon that reconnects on every drop and exposes an `on_failure_callback`. The pattern is small, complete, defensible.
- **`py/vts_manager.py`** — single-purpose VTube Studio WS client, owns the lip-sync FFT, owns the auth-token persistence (`py/vts_manager.py:45-56`), owns its asyncio queue worker (`py/vts_manager.py:119`). Tight bounds.
- **`py/behavior_engine.py`** — singleton with per-platform handler registry, time/no-input/cycle triggers, hot-config-update. Crisp module. The dependency *back* to `server.py` is one-way (handlers are registered, never imported).
- **`py/blivedm/`** — vendored Bilibili open-platform client, isolated subtree, swappable.

These five are templates for what every SAP module *could have been*.

---

## 7. Cross-References

- [[11_AVATAR_DOMAIN]] for VRM + VMC + VTS in depth
- [[12_AGENT_CORE_DOMAIN]] for sub-agent, task center, and the missing reasoning kernel
- [[14_MESSAGING_DOMAIN]] for the 8-bot mesh
- [[1A_AFFECTION_DOMAIN]] for the regex-heart autopsy
- [[1D_ROUTING_DOMAIN]] for the three-bus crack
- [[20_MCP_INTEGRATION]] for SAP's outbound + inbound MCP duality
- [[hermes:10_DOMAIN_MAP]] for the contrasting Hermes shape
- [[peer:LETTA-1_SHAPE]] for the contrasting Letta shape
- [[ember:CROSS_PLATFORM_PLAN]]

---

## What This Means for Ember

**Adopt:**
- `py/sleep_guard.py` pattern — cross-platform native API fallback chain. Lift the whole module into Ember's host layer; rename to `vörð_svefn` if we are being honest with the Norse.
- `py/mcp_clients.py:111-133` reconnect-monitor daemon — pull into Munnr's MCP egress as the standard health pattern.
- The vendored-subtree pattern of `py/blivedm/` — for any Ember broadcast adapter, vendor and isolate; do not pip-pin.
- The lazy-load-with-flag pattern (`GUI_AVAILABLE` at `py/computer_use_tool.py:18`, `_lazy_load_deps` at `py/minilm_router.py:16-24`) — every optional heavy import is gated by a try/except + bool, and downstream callers use the bool. Modular Authorship made operational.

**Adapt:**
- The **eleven-layer stack** of SAP becomes Ember's **three-realm + six-name** layout (Spark / Thread / Well, with Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr). The SAP layering is too device-flat; Ember's layering must respect tier (Pi / laptop / workstation).
- SAP's `behavior_engine` as a singleton with hot-config-update — adapt as Ember's **Strengr scheduler** (with the singleton replaced by a per-Realm instance to keep Pluggable Storage).
- SAP's **lazy router include** pattern (`server.py:10930-11618`) — adapt as Ember's interface registration but with typed manifests (Defended System Prompt as the architectural principle).

**Avoid:**
- **The Server-Eaten Codebase.** Never let one file accumulate composition authority. If `server.py` is what gravity-collapses look like in Python, Ember's job is to keep gravity distributed.
- **String-concatenated system prompts.** `server.py:2556-2675` is the cautionary tale. Ember's system prompt enters via typed slots (Defended System Prompt, proposed in Hermes Codex).
- **Same-process HTTP self-calls** for component decoupling. The IM-bot-to-server loop is clever but unauthenticated; in Ember, use the MCP server surface for what SAP does with `127.0.0.1:{port}` (see [[20_MCP_INTEGRATION]]).
- **Affection-by-vibe.** Whatever Hjarta becomes, it cannot be a regex over LLM output writing JSON. See [[1A_AFFECTION_DOMAIN]] and the proposed reimagination in [[60_synthesis:64_AFFECTION_ENGINE_REIMAGINED]].

**Invent:**
- **The Boundary Census.** Before any Ember subsystem ships, name *what it owns* and *what it does not own* in a header comment. The fourteen-domain table in §1 is what SAP would have had if anyone had written it down before the first commit. Make this part of Ember's PR template.
- **The Bus-of-One Vow.** Ember has **one** internal event bus (proposed True Name: **Sögumiðla** — the saga-mediator). Every side-effect — affect update, surface notify, tool result, memory write — flows through it as a typed event. The three-WS-managers-no-bus crack of SAP is not a bug to copy.
- **Reach-Tier Manifests.** SAP scales 2GB → multi-GPU but does so by uniformly enabling everything (and praying). Ember should ship a `tier_manifest.yaml` that names which True Names are active at which tier (Pi: Funi+Munnr only; laptop: + Strengr + Hjarta-lite; workstation: full Brunnr + VRM + voice). See [[60_synthesis:63_PERFORMANCE_TIER_ENGINE]].

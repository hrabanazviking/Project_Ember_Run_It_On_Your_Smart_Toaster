---
codex_id: 1D_ROUTING_DOMAIN
title: Routing Domain — Three WebSocket Managers, No Shared Bus
role: Architect
layer: Domain
status: draft
sap_source_refs:
  - py/ws_manager.py:1-50
  - py/overlay_router.py:1-82
  - py/live_router.py:53-100
  - py/mode_change.py:1-136
  - server.py:8167-8260
ember_subsystem_targets: [Strengr, Munnr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_AVATAR_DOMAIN
  - 10_domain/15_BROADCAST_DOMAIN
  - 30_execution/31_PYTHON_SERVER
  - 60_synthesis/62_PARTY_PROTOCOL
---

# Routing Domain
## Three WebSocket Managers, No Shared Bus

*— Rúnhild Svartdóttir, Architect*

> *A bus is what turns a courtyard of shouting into a marketplace of sentences. SAP's courtyard has three buses parked along it. None of them know about the others. Every message gets shouted across the courtyard and then quietly re-shouted by whichever bus thought it was listening.*

The routing domain is the place where SAP fans messages out to many surfaces — the chat UI, the VRM window, the subtitle overlay, the danmaku overlay, the live-comment feed. It is also the place where SAP's architectural cracks are most visible: there are *four* separate WebSocket managers in this codebase, none of which know about the others, and a *settings-update broadcast* that exists in only one of them.

---

## 1. The Subject Itself

**What the domain owns:** WebSocket connection management, message broadcast fanout, settings-change propagation, permission-mode change propagation.

**What it does *not* own:**
- The semantics of any specific message (those belong to each producer/consumer)
- Per-message addressing/topic (there is no topic system)
- Persistence of unsent messages to dropped clients (there is none — drop = lose)

**Where it lives:**

| File | Class | Connections | Used by |
|---|---|---|---|
| `py/ws_manager.py` | `ConnectionManager` | settings update + task notification | extension/skill UIs, sub-agent result push |
| `py/overlay_router.py` | `DanmakuOverlayManager` | OBS danmaku overlay HTML | LLM-driven overlay highlights |
| `py/live_router.py` | `ConnectionManager` (separate class) | livestream comment feed | Bilibili/YT/Twitch ingest |
| `server.py:8167-8260` | `TTSConnectionManager` | main UI + VRM window + subtitle overlay | TTS audio + expression tags + subtitles |
| `py/mode_change.py` | (no class — calls `ws_manager`) | permission-mode change broadcast | `update_workspace_settings` LLM tool |

Four distinct connection managers, four broadcast methods, four ad-hoc message shapes. They share **nothing** except FastAPI's `WebSocket` class.

---

## 2. How It Works

### 2.1 The four managers, side by side

```python
# /tmp/super-agent-party/py/ws_manager.py:9-47 (excerpts)
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    async def broadcast(self, message: dict, exclude: Optional[WebSocket] = None):
        for connection in self.active_connections[:]:
            if connection == exclude: continue
            try: await connection.send_json(message)
            except Exception: self.disconnect(connection)
    async def broadcast_settings_update(self, settings: dict, exclude=None):
        await self.broadcast({"type": "settings_update", "data": settings}, exclude=exclude)

ws_manager = ConnectionManager()
```

```python
# /tmp/super-agent-party/py/overlay_router.py:18-39 (excerpts)
class DanmakuOverlayManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try: await connection.send_text(json.dumps(message))
            except Exception: self.disconnect(connection)

overlay_manager = DanmakuOverlayManager()
```

```python
# /tmp/super-agent-party/py/live_router.py:53-76 (excerpts)
class ConnectionManager:  # NOTE: same name, different module
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    async def broadcast(self, data: dict):
        disconnected = []
        for connection in self.active_connections:
            try: await connection.send_json(data)
            except: disconnected.append(connection)
        for connection in disconnected: self.disconnect(connection)

manager = ConnectionManager()
```

```python
# /tmp/super-agent-party/server.py:8167-8246 (excerpts)
class TTSConnectionManager:
    def __init__(self):
        self.main_connections: List[WebSocket] = []
        self.vrm_connections: List[WebSocket] = []
        self.overlay_connections: list[WebSocket] = []
    
    async def broadcast_to_vrm(self, message: Union[str, bytes]):
        # bytes → only VRM
        # str → VRM + overlay
        ...
```

Notice:
- **Three classes are named `ConnectionManager`**, in three modules. The Python import system distinguishes them by module path, but a reader scanning grep output for "ConnectionManager" gets unhelpful results.
- **Three different `send_*` methods**: `send_json`, `send_text(json.dumps(...))`, `send_bytes`. Three encodings of "send a JSON dict to a WS client."
- **Three different error-handling strategies**: in-place delete via index-trick, accumulator-and-cleanup loop, immediate disconnect-call.
- **TTSConnectionManager defines `broadcast_to_vrm` *twice*** (lines 8191 and 8228); the second definition wins; the first is dead code. There is a *third* orphaned `broadcast_to_vrm` at line 8251 defined at module level by mis-indentation.

### 2.2 The settings-update path

`py/mode_change.py:9-83` calls `ws_manager.broadcast_settings_update(settings)` (line 57) when the LLM toggles permission modes via `update_workspace_settings`. This is the *only* place in SAP where a settings change is fanned to subscribers — and it is fanned only through *one* of the four managers. The VRM window doesn't see it. The overlay doesn't see it. The livestream UI doesn't see it. The settings-update broadcast is **monocular**.

### 2.3 The task notification path

`py/sub_agent.py:169-176` calls `ws_manager.broadcast({"type": "task_notification", "data": {...}})`. Again — only the `ws_manager` clients see it. The VRM window cannot react to "task completed" by, say, doing a celebratory expression — it has no subscription path to that event.

### 2.4 The TTS audio path

`TTSConnectionManager.broadcast_to_vrm(audio_bytes)` sends to `self.vrm_connections` (the connected VRM HTML pages). The same method, with a string argument, also fans the string to `self.overlay_connections` (subtitle overlay pages). The branch is `isinstance(message, bytes)`. Type-on-runtime polymorphism at the routing junction.

### 2.5 The danmaku overlay path

`POST /api/overlay/danmaku` (`py/overlay_router.py:50`) takes a payload and broadcasts `{"action": "show", "data": ...}` to the overlay clients. This is the LLM-driven "highlight a comment on the OBS overlay" path. The LLM (via some upstream code in `server.py`) calls this endpoint when it wants to surface a viewer comment. The path is *one-way* — no acknowledgment from the overlay back.

### 2.6 The live-comment path

`live_router.ConnectionManager.broadcast(data)` (`py/live_router.py:65-75`) fans normalized livestream events to clients of `/ws/live/danmu`. The Electron UI's "live" panel renders the feed.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The four-bus problem

The single biggest cost of the routing domain's design: a new subsystem that wants to *observe* settings changes, task completions, VRM mouth state, and live comments must subscribe to all four managers. There is no `subscribe(topic)` API; there is no event-type dispatch. The four buses are independent.

Concrete consequence: when the LLM tool `update_workspace_settings` flips `engine` from `local` to `ds` (Docker Sandbox), only clients of `ws_manager` see the change. The VRM avatar (showing a body in the user's UI) has no awareness that the tools backend has changed. The discrepancy is invisible to the user.

### 3.2 The duplicate-class-name confusion

`py.ws_manager.ConnectionManager` and `py.live_router.ConnectionManager` and (implicitly) `TTSConnectionManager` share the `ConnectionManager` concept but no code. A refactor that wants to add backpressure must touch *three* classes. The Don't-Repeat-Yourself principle is silently violated.

### 3.3 The `isinstance(bytes)` branch

`TTSConnectionManager.broadcast_to_vrm` (line 8228) branches on runtime type. This works but is fragile. A future need to send *binary* subtitles (e.g. PNG renders) would surface a third branch and the function would balloon.

### 3.4 Settings-broadcast is monocular

Already named in §2.2. The fix is trivial — make `ws_manager` the *settings bus*, route every settings producer through it, and have every consumer subscribe. But it requires admitting `ws_manager` is the bus, which the architecture has not committed to.

### 3.5 No per-message reliability

A WS broadcast in any of the four managers drops to dead clients silently and *does not* retry, persist, or notify any other subsystem of the loss. Sticky failures (the VRM window crashed mid-utterance and the next audio chunk dropped) leave the UI in a broken state until reload.

### 3.6 The dead-code line at 8251

`server.py:8251` defines a `broadcast_to_vrm` function at module level (outside the class) — almost certainly a mis-indented near-duplicate. It is not called by anything. It is a fossil that proves the duplicate-definition mistake at lines 8191 / 8228 happened more than once.

### 3.7 The crisp parts

- The **`disconnect` cleanup pattern** of try-except + disconnect is consistent across managers, even if the strategies differ.
- The **`exclude` parameter** in `ws_manager.broadcast` (`py/ws_manager.py:30`) supports the use-case "broadcast to all except sender" — small but real polish.
- The **type-distinguished `broadcast_to_vrm`** in `TTSConnectionManager` *does* work for the two payload types it handles.
- The **per-router state ownership** is at least *unambiguous* — each manager owns its connections; nothing leaks.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 14 (this domain) + §5.3 (the three-bus crack)
- [[11_AVATAR_DOMAIN]] §2.4 + §3.1 — the duplicate `broadcast_to_vrm`
- [[15_BROADCAST_DOMAIN]] §2.3 — the third manager
- [[30_execution/31_PYTHON_SERVER]] (Forge) for the server.py deep dive
- [[60_synthesis/62_PARTY_PROTOCOL]] (Cartographer) — the multi-host bus
- [[hermes:HEM-21_RPC_INTERFACE]] for Hermes's JSON-RPC routing pattern

---

## What This Means for Ember

**Adopt:**
- The **`exclude` parameter** pattern of `ws_manager.broadcast`. Sögumiðla's `publish(event, exclude_subscriber=...)` supports the same use-case.
- The **per-manager state ownership** discipline — each surface owns its connections; nothing leaks across surfaces.
- The **try/except → disconnect-and-continue** broadcast pattern. Dead clients never block live ones.

**Adapt:**
- The **four-bus problem** — adapt to **one bus, many topics**. The Sögumiðla event bus exposes `subscribe(topic_pattern, handler)` and `publish(topic, event)`. Topics are dotted: `settings.changed`, `task.completed`, `vrm.mouth_open`, `livestream.comment.new`. Subscribers select what they care about; the bus dispatches. SAP's four managers become four topic-prefixes on one bus.
- The **type-on-runtime polymorphism** of `broadcast_to_vrm(bytes|str)` — adapt to **typed event payloads**: `AudioFrame(...)`, `ExpressionTag(...)`, `Subtitle(...)`. The dispatcher routes by *event type*, not by Python runtime type.
- The **monocular settings broadcast** — adapt to the bus: a settings change is just a `settings.changed` event; every interested subscriber receives it.

**Avoid:**
- **Multiple classes named `ConnectionManager` in different modules.** The naming alone obscures the architecture.
- **`broadcast_to_vrm` defined twice in the same class** (and once at module level). Lint for redefinitions.
- **No retry / no persistence on drop.** Sögumiðla optionally persists events to the Brunnr Well for replay; subscribers can request "deliver everything since cursor X."
- **Module-global manager singletons** without per-Realm scoping.

**Invent:**
- **Sögumiðla — The Saga Mediator.** Ember's proposed True Name for the event bus. One bus per Realm; typed events; topic-pattern subscription; optional persistence (per-topic policy). Every side-effect, every cross-surface notification, every audit event flows through Sögumiðla. SAP's four buses become four topic prefixes (`ws.settings`, `ws.task`, `tts.audio`, `live.comment`, `overlay.danmaku`).
- **The Replay Cursor.** Every Sögumiðla subscriber maintains a *cursor* (the last event id received). On reconnect, the subscriber can ask the bus for "everything since cursor X" and resume without loss. This solves SAP's "VRM crashed mid-utterance and lost the next chunk" failure.
- **Cross-Host Bus Federation.** A Pi-Ember and a laptop-Ember run their own Sögumiðla instances and *federate* — selected topics replicate between them. The Pi can see when the laptop got a Slack DM; the laptop can see when the Pi observed a long user silence. This is the [[60_synthesis/62_PARTY_PROTOCOL]] foundation.
- **Topic-Scoped Vow Enforcement.** Each topic on Sögumiðla declares a *vow profile*: max event rate, max payload size, persistence policy, audit level. A producer that breaches the rate limit gets backpressure; an audit alarm raises. SAP has no rate awareness; a runaway producer can flood any of the four buses.
- **The Schema Ledger.** Every Sögumiðla event type is a Pydantic model; the ledger of event types is itself a queryable Brunnr namespace. Asking "what does a `vrm.expression_changed` event look like?" returns the schema, the producer list, the subscriber list. Ember's wiring is introspectable; SAP's is not.
- **The Settings-Bus Subscription Vow.** Every UI surface in Ember must subscribe to `settings.changed`. A subsystem that wants to know "did the user just change the model?" gets the event. SAP's monocular settings broadcast becomes a Vow — every surface in Ember sees every settings change or fails review.

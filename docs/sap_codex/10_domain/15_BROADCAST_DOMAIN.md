---
codex_id: 15_BROADCAST_DOMAIN
title: Broadcast Domain — Livestream Ingest, Avatar Voice, and the One-Way Pipe
role: Architect
layer: Domain
status: draft
sap_source_refs:
  - py/blivedm/__init__.py
  - py/live_router.py:1-280
  - py/live_router.py:399-545
  - py/ytdm.py:1-132
  - py/twitch_service.py:1-210
  - py/overlay_router.py:1-82
  - server.py:8167-8249
ember_subsystem_targets: [Munnr, Strengr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_AVATAR_DOMAIN
  - 10_domain/1D_ROUTING_DOMAIN
  - 20_interface/27_STREAMING_INTERFACE
  - 30_execution/36_LIVESTREAM_INGEST_OVERVIEW
  - 50_verification/56_PRIVACY_BOUNDARIES
---

# Broadcast Domain
## Livestream Ingest, Avatar Voice, and the One-Way Pipe

*— Rúnhild Svartdóttir, Architect*

> *Broadcast is intimacy at scale. Get it right and a single voice can sing to a thousand. Get it wrong and a thousand voices crowd into one ear and drive the singer mad.*

The broadcast domain is what makes SAP — uniquely among the agent frameworks I have surveyed — a *streamer*. It ingests live comments from Bilibili, YouTube, and Twitch, and routes them into the same conversation kernel that handles a Telegram DM, so the avatar can react with voice + expression to incoming chat. This is the embodiment-meets-reach axis. The implementation is real but rough. This doc names the contract.

---

## 1. The Subject Itself

**What the domain owns:** the listener side of three livestream platforms; the WebSocket broadcast of normalized danmu/comment events to subscribed UI surfaces; the start/stop lifecycle of each listener.

**What the domain does *not* own:**
- The stream's *video* output (that's OBS; SAP just provides the transparent VRM window it captures)
- The avatar's expression in response (that's [[11_AVATAR_DOMAIN]])
- The voice synthesis (that's [[16_VOICE_DOMAIN]])
- Comment filtering / moderation (SAP forwards everything; the LLM decides)
- The retention policy of comments (none — they fly through)

**Where it lives:**

| File | LOC | Owns |
|---|---|---|
| `py/blivedm/` (vendored subtree) | ~2,000 (not all enumerated here) | Bilibili open-platform danmu protocol |
| `py/live_router.py` | 546 | the orchestrator: start/stop API, WS fanout, message normalization |
| `py/ytdm.py` | 132 | YouTube Live polling client |
| `py/twitch_service.py` | 210 | Twitch IRC + EventSub |
| `py/overlay_router.py` | 81 | the subtitle/danmu overlay HTML and its WS |
| `server.py:8167-8249` (TTSConnectionManager) | ~80 | the *output* side: audio → VRM clients, subtitles → overlay clients |

Four input streams (3 platforms + overlay management), one output channel (TTS+VRM). The fan-in/fan-out asymmetry is deliberate.

---

## 2. How It Works

### 2.1 The orchestrator: `py/live_router.py`

`py/live_router.py` is the broadcast domain's hub. It mounts `/api/live/*` (line 18) and `/ws/live/danmu` (line 266) on the FastAPI app. The state is **module-global**:

```python
# /tmp/super-agent-party/py/live_router.py:22-27
live_client = None
live_thread = None
current_loop = None
stop_event = None
yt_client: Optional[YouTubeDMClient] = None 
twitch_task = None
```

Six globals, no class. `start_live(request)` (line 81) reads the config from the LLM/UI and **conditionally** starts each platform's listener — Bilibili in a fresh thread (`run_live_client`, line 293), YouTube as an instance of `YouTubeDMClient` with a callback (line 121-130), Twitch as an asyncio task (line 132-149).

The Bilibili path is the most interesting: it spawns a *new thread* with its own asyncio loop (`run_live_client` lines 296-326), because the Bilibili SDK wants to own the loop, and the FastAPI loop is already running on the main thread. So:

- Main thread runs the FastAPI app loop.
- Bilibili thread runs its own loop for the blivedm client.
- YouTube polling runs as a thread inside `YouTubeDMClient` (its own design — see `py/ytdm.py`).
- Twitch runs as an asyncio task in the main loop.

Four threading patterns, one orchestrator file. The Twitch path uses `asyncio.run_coroutine_threadsafe` to push messages from cross-thread callbacks into the main loop's `ConnectionManager.broadcast` (line 122-123). The pattern is correct but easy to get wrong; the comments at lines 86-88 note the explicit caching of the main loop for that reason.

### 2.2 Message normalization

`py/live_router.py:399-545` defines two handler classes — `WebSocketHandler` (for Bilibili "web" mode, currently commented out at lines 95-114) and `OpenLiveWebSocketHandler` (for Bilibili open-platform, the active path at lines 472-545). Every event type — danmaku, gift, super-chat, buy-guard, like, enter-room, follow — becomes a dict with shape:

```python
# Normalized event shape, e.g. /tmp/super-agent-party/py/live_router.py:406-413
{
    'id': str(uuid.uuid4()),
    'type': 'message',
    'content': msg_text,
    "danmu_type": "danmaku" | "gift" | "buy_guard" | "super_chat" | "like" | "enter_room" | "follow"
}
```

YouTube and Twitch produce *similar* but not identical shapes (Twitch adds `platform: 'twitch'` at line 142-143). The platform key is not consistent — Bilibili events do not include a `platform` field. The normalization is **almost** unified.

### 2.3 The output side

`ConnectionManager` at `py/live_router.py:53-77` is **the broadcast domain's own** WebSocket manager — separate from `ws_manager.py`, separate from `overlay_router.py`, separate from `TTSConnectionManager`. Its job is to broadcast events from any platform to any client subscribed to `/ws/live/danmu`.

The Electron UI's "live" panel listens to this channel and renders the chat feed. The LLM is *not* directly notified — it receives comments through whatever upstream code (probably in `server.py`, but I have not yet seen it bound here) reads from the same WS or polls the broadcast and feeds it into a system prompt.

`py/overlay_router.py:18-39` is a *different* manager (`DanmakuOverlayManager`) — for the transparent OBS-friendly overlay HTML pages (`/danmaku_overlay`, `/subtitle_overlay`, served from `static/`). The overlay manager has its own active-connections list and broadcast.

So the **same comment travels two paths**: once to `/ws/live/danmu` (for the chat panel in the app UI), and a separate broadcast trigger to the danmaku overlay (`/api/overlay/danmaku` POST at line 50, which the LLM or processing code calls when it wants to highlight a comment on the OBS overlay).

### 2.4 The Bilibili story

`py/blivedm/` is a vendored Bilibili danmu client — open-source, AGPL-compatible, but not pip-installed. SAP carries the source. The vendoring decision is correct: the Bilibili API changes frequently and a pip dependency would be fragile. The vendored copy is isolated; deleting it would not break anything else.

Two Bilibili modes exist in the code: "web" mode (logged-in cookie-based access) and "open" mode (registered Bilibili open-platform app). The web mode is commented out (`py/live_router.py:95-114` and `336-348`). The open mode is the supported path. This is the right call — Bilibili web cookies are short-lived and warning-prone; the open-platform app credentials are stable.

### 2.5 The YouTube story

`py/ytdm.py` (132 LOC) polls the YouTube Live Chat API. It uses an API key (the `youtube_api_key` config field) and polls a `videoId` for new messages. The pull is in a worker thread; the callback shape is `on_message(msg: dict)`. From `live_router.py:122-123`, the callback bridges into the main loop via `asyncio.run_coroutine_threadsafe`.

YouTube's API is quota-bound — there is a daily call budget. SAP does not surface this; if the budget is exhausted, the polling silently fails. Compare to `py/sleep_guard.py:139` where unsupported environments are logged with an explicit message.

### 2.6 The Twitch story

`py/twitch_service.py` (210 LOC) uses Twitch IRC + EventSub. The callback signature evolved late — `py/live_router.py:137`:

```python
async def _twitch_on_msg(chan, user, msg, d_type="danmaku"):
    await manager.broadcast({
        'id': str(uuid.uuid4()),
        "type": "message",
        "content": f"{user}: {msg}" if d_type == "danmaku" else msg,
        "danmu_type": d_type,
        "platform": "twitch"
    })
```

The `platform: "twitch"` key is the only place the platform field is set. Bilibili and YouTube events do not include it. Downstream code cannot reliably say *which platform a comment came from* by looking at the message.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 Six module-globals as state

`py/live_router.py:22-27` — `live_client`, `live_thread`, `current_loop`, `stop_event`, `yt_client`, `twitch_task`. This means there can be exactly one Bilibili connection, one YouTube poll, one Twitch task across the entire process. Multiple Bilibili rooms? Not without rewriting the module. Multiple YouTube videos? No. This is acceptable for a single-streamer desktop app; it forecloses streaming-for-multiple-creators from one SAP instance.

### 3.2 Three event managers, none aware of each other

The broadcast domain has `live_router.ConnectionManager` (chat panel), `overlay_router.DanmakuOverlayManager` (OBS overlay), and `server.py:TTSConnectionManager.overlay_connections` (subtitle overlay). A subtitle event sent to overlay-A and an audio event sent to overlay-B from the same TTS run will pass through different fanout code. The bus-of-three problem (see [[1D_ROUTING_DOMAIN]]) is most visible here.

### 3.3 No retention or rate limiting

A surge of comments — a viral moment, a coordinated raid, a bot attack — fans out at the rate the WS broadcast can sustain. There is no queue depth limit; there is no per-user rate limit; there is no priority for super-chats over regular danmu. The LLM either receives the full firehose (and cannot keep up) or some upstream sampler discards (but no sampler is defined here).

### 3.4 Platform field inconsistency

Already noted in §2.6. Only Twitch sets `platform` in the broadcast payload. This is a one-line fix that has not been done.

### 3.5 The crisp parts

- The **vendored `py/blivedm/`** subtree — the right call.
- The **per-platform thread / loop choice** in `start_live` — pragmatic, fits the SDK constraints.
- The **uuid'd event id** on every broadcast — enables UI deduplication.
- The **explicit cancel-and-cleanup** of `stop_live` (lines 159-218) — including timeout-bound thread joins.
- The **transparent overlay HTML** pattern (`/danmaku_overlay`, `/subtitle_overlay`) — OBS captures the HTML page with chroma-key transparency, the same way the VRM window is captured. Consistent architectural decision.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 7
- [[11_AVATAR_DOMAIN]] for the avatar that speaks the broadcast
- [[1D_ROUTING_DOMAIN]] for the three-bus crack as it appears here
- [[20_interface/27_STREAMING_INTERFACE]] (Auditor) for the protocol-level contract
- [[30_execution/36_LIVESTREAM_INGEST_OVERVIEW]] (Forge-A) for the end-to-end execution
- [[30_execution/36a]]–[[30_execution/36c]] (Forge-B) for per-platform deep dives
- [[50_verification/56_PRIVACY_BOUNDARIES]] (Auditor) for the privacy threat model

---

## What This Means for Ember

**Adopt:**
- **Vendoring SDKs that change frequently.** `py/blivedm/` is the right move for any livestream / IM SDK that's volatile. Ember vendors per-platform broadcast adapters into the Munnr tree.
- **Per-thread-per-loop spawn for SDK-owns-the-loop libraries** (the pattern at `py/live_router.py:293-326`). Munnr's reach adapters follow.
- **Normalized event envelopes with uuids** for cross-surface deduplication.
- **Transparent-HTML overlays** for OBS capture (the `static/danmaku_overlay.html` / `subtitle_overlay.html` pattern). Munnr's broadcast-surface contract includes overlay HTML by default.

**Adapt:**
- **Module-globals as state** — adapt to **per-Realm broadcast-domain instances**. Ember's Munnr exposes `BroadcastDomain(realm)` with a single instance per Realm; the Realm boundary is what limits "one Bilibili at a time," not a Python global.
- **Three event managers, no shared bus** — adapt to the single `Sögumiðla` event bus (proposed in [[10_DOMAIN_MAP]] §invent). One bus; many topics; per-topic subscribers. The danmu/overlay/subtitle distinction becomes topic names.
- **The platform field inconsistency** — Ember enforces: every event envelope has `{realm, platform, channel, sender, timestamp}`. No optional. The envelope schema is a Pydantic model; misshapen events fail at the producer.

**Avoid:**
- **Six module-level mutable globals** in a routing file.
- **A YouTube quota exhaustion that silently fails.** Ember surfaces quota state as a typed Sögumiðla event; degraded mode is *named*.
- **No queue depth or rate limiting** on broadcast fanout. A surge silently dropping or silently overwhelming is the same failure mode.
- **Three separate WS managers for three nearly-identical purposes.**

**Invent:**
- **The Broadcast Pyramid.** Ember rates incoming broadcast comments by importance: **Sumr** (super-chat / donation) > **Frændi** (familiar / repeat viewer) > **Gestr** (regular viewer) > **Hróp** (raid / noise). Strengr's attention budget allocates response probability by rating. SAP gives every comment equal weight; Ember does not.
- **The Quench Filter.** A sustained surge above N comments/second triggers a *quench* — Ember silently samples instead of responding to each. The user sees an audit event `[broadcast: quench engaged 50/300 cps]`. SAP firehoses; Ember triages.
- **Cross-Platform Broadcast Identity.** A viewer on Twitch and the same human on YouTube can be joined (via consent) into one identity for affection/memory purposes; their comments arrive with a `broadcast_identity` field, and the answer reflects the shared context. This is the [[20_interface/26_IM_BOT_INTERFACE]] Auðkenni surface generalized.
- **Latency-Budget-Aware Response.** Ember knows the round-trip from comment-arrival → LLM-response → TTS → VRM-mouth-move; it refuses to engage with a comment when latency would exceed N seconds (the viewer has moved on). The refusal is logged as a Sögumiðla event for offline analysis. SAP responds when it can; Ember refuses when it can't gracefully.
- **The OBS-Aware Tier.** A Pi-Ember running on a quiet livestream might have no avatar — and Munnr offers a `text-only broadcast` mode where comments are read aloud by ASR-equivalent TTS but no body renders. The OBS scene captures the audio + a static overlay. Tier collapse without losing presence.

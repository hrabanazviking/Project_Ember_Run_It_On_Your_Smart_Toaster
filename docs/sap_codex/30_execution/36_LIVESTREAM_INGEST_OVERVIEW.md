---
codex_id: 36_LIVESTREAM_INGEST_OVERVIEW
title: Livestream Ingest Overview — Three Platforms, Three Transport Models, One Latency Budget
role: Forge
layer: Execution
status: draft
sap_source_refs:
  - py/live_router.py:1-300 (router + manager)
  - py/blivedm (Bilibili subpackage)
  - py/ytdm.py:1-130 (YouTube polling)
  - py/twitch_service.py:1-210 (Twitch IRC)
  - server.py:10935-10940 (router include)
ember_subsystem_targets: [Munnr, Strengr]
cross_refs:
  - 30_execution/32_AVATAR_RENDER_PIPELINE
  - 30_execution/36a_LIVESTREAM_BILIBILI
  - 30_execution/36b_LIVESTREAM_YOUTUBE
  - 30_execution/36c_LIVESTREAM_TWITCH
  - 20_interface/27_STREAMING_INTERFACE
---

# Livestream Ingest Overview

> *Comments come in over WebSocket, polling, and IRC. Comments go out as AI replies through the avatar. The pipeline is shaped like a funnel. The funnel leaks at the rim.*

Forge. Eldra. SAP supports three livestream platforms — **Bilibili** (`py/blivedm/`), **YouTube** (`py/ytdm.py`), and **Twitch** (`py/twitch_service.py`). Each one has its own transport (WebSocket, HTTP polling, IRC over TLS). All three feed the same downstream pipeline: comment → topic router → LLM → TTS → avatar → optional OBS sink. This doc charts the funnel. Forge-B's per-platform subdocs ([[36a_LIVESTREAM_BILIBILI]], [[36b_LIVESTREAM_YOUTUBE]], [[36c_LIVESTREAM_TWITCH]]) cover each ingest's protocol details.

## The Funnel

```
┌──────────────┐    ┌──────────────┐    ┌─────────────┐
│ Bilibili WS  │    │ YouTube HTTP │    │ Twitch IRC  │
│ (blivedm)    │    │ (poll 5s)    │    │ (TLS port   │
│              │    │              │    │  6697)      │
└──────┬───────┘    └──────┬───────┘    └──────┬──────┘
       │                   │                   │
       └─────────┬─────────┴───────────────────┘
                 ▼
       ┌──────────────────────────┐
       │   live_router.manager    │   ← WebSocket fanout
       │   ConnectionManager      │
       └─────────────┬────────────┘
                     ▼
       /ws/live/danmu  (renderer subscribes)
                     ▼
       ┌──────────────────────────┐
       │ Frontend topic router    │  ← decides what to reply to
       │ (in renderer)            │
       └─────────────┬────────────┘
                     ▼
       /v1/chat/completions  (LLM response)
                     ▼
       /tts → /ws/vrm → avatar speaks (see [[32_AVATAR_RENDER_PIPELINE]])
                     ▼
       Optional: VMC OSC send → OBS-side avatar (see [[25_AVATAR_PROTOCOL]])
```

Three sources, one fan-in via `live_router.manager.broadcast()`, one renderer-side consumer that drives the LLM call, and the avatar pipeline as the final sink. The whole thing is one router file (`live_router.py`, 546 lines) plus three small platform clients.

## live_router.py: The Manager

```python
# py/live_router.py:18
router = APIRouter(prefix="/api/live", tags=["live"])
```

The router exposes:

- `POST /api/live/start` — enable any subset of {Bilibili, YouTube, Twitch} based on config
- `POST /api/live/stop` — disable all
- `POST /api/live/reload` — stop then start
- `GET /api/live/status` — three-bit truthiness map
- `WS /ws/live/danmu` — comment stream to the renderer

Plus a `ConnectionManager` class (`py/live_router.py:53-77`) that holds WebSocket subscribers. The same `ConnectionManager` pattern as `ws_manager.py` — broadcast to a list, prune on disconnect — but kept separate because livestream messages and core settings updates have different consumers.

Three module-level globals hold the platform clients:

```python
# py/live_router.py:22-27
live_client = None        # Bilibili blivedm client
live_thread = None        # Bilibili runs in its own thread
current_loop = None       # main event loop, cached for cross-thread callbacks
stop_event = None
yt_client: Optional[YouTubeDMClient] = None
twitch_task = None        # Twitch is asyncio-native; no thread needed
```

Three platforms, three different concurrency models. This reflects the SDKs' shapes — Bilibili's `blivedm` is async but uses a callback model that wants its own loop; YouTube's API client is sync (Google's `googleapiclient`) so it must live in a thread; Twitch is raw socket and was written to be asyncio-native. Three is correct here. Forcing them into the same shape would have meant rewriting one or more SDKs.

## The Three Transport Models

### Bilibili: WebSocket (`blivedm`)

Bilibili's live-chat protocol is a custom WebSocket with binary frames. `py/blivedm/` is a bundled vendor of an open-source library that handles the framing, heartbeat, and decryption. The result is an event-callback API: `on_message`, `on_super_chat`, `on_gift`, etc.

Bilibili supports **two access patterns**:
1. **Web mode** (using a logged-in user's `SESSDATA` cookie) — works on any room, including ones you don't own. Easier, but riskier (your personal cookie is on the host).
2. **Open Live platform** (using `ACCESS_KEY_ID` + `ACCESS_KEY_SECRET` + `APP_ID` + `ROOM_OWNER_AUTH_CODE`) — official API, requires the streamer's auth code, only works for rooms that authorized your app. SAP's default code path (`live_router.py:99`) requires the open-live credentials and explicitly errors if they're absent.

Sensible default. Web mode is supported but de-emphasized. See [[36a_LIVESTREAM_BILIBILI]] for the protocol-level details.

### YouTube: HTTP Polling

```python
# py/ytdm.py:55-61
while not self._stop_evt.is_set():
    try:
        self._poll_once()
        print('[YouTube] poll_once done')
    except Exception as e:
        print('[YouTube] poll error:', e)
    time.sleep(self.poll_interval)
```

YouTube Live Chat has **no WebSocket API**. The only way to read live chat is to poll `liveChatMessages.list` every few seconds. SAP polls every 5 seconds (`poll_interval = 5`, line 24). This means YouTube replies are ~5 seconds delayed minimum, with a maximum delay of ~10 seconds in worst case.

```python
# py/ytdm.py:63-70
def _get_live_chat_id(self) -> Optional[str]:
    rsp = self._yt.videos().list(
        id=self.video_id,
        part="liveStreamingDetails"
    ).execute()
    if not rsp["items"]:
        return None
    return rsp["items"][0]["liveStreamingDetails"].get("activeLiveChatId")
```

The flow is: get the video's `activeLiveChatId`, then poll `liveChatMessages.list(liveChatId=..., pageToken=...)` with cursor pagination. Page tokens get refreshed each call. If the stream ends, `activeLiveChatId` becomes None and the polling thread exits.

Three message types are handled (`ytdm.py:94+`): `textMessageEvent` (normal chat), `superChatEvent` (paid messages), `fanFundingEvent` (member sponsorship). All three are flattened into a single `{type, content, danmu_type}` envelope before broadcasting.

The polling thread runs in its own `threading.Thread` because `googleapiclient.discovery.build` is synchronous. Cross-loop callbacks use `asyncio.run_coroutine_threadsafe(manager.broadcast(msg), current_loop)` — the main loop is cached in `live_router.py:87` for exactly this purpose.

### Twitch: IRC over TLS

```python
# py/twitch_service.py:56-68
ctx = ssl.create_default_context()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
self._sock = ctx.wrap_socket(sock, server_hostname="irc.chat.twitch.tv")
self._sock.connect(("irc.chat.twitch.tv", 6697))

self._send(f"CAP REQ :twitch.tv/tags twitch.tv/commands")
self._send(f"PASS oauth:{self.access_token}")
self._send(f"NICK justinfan12345")
self._send(f"JOIN #{self.channel}")
```

Twitch chat is IRC. Old protocol, well-documented, no SDK needed. SAP connects to `irc.chat.twitch.tv:6697` over TLS, authenticates with `oauth:<access_token>`, joins the channel, and reads line-buffered messages forever. The `justinfan12345` nick is the Twitch convention for read-only anonymous-like access (any `justinfan<number>` nick works; the actual identity is in the OAuth token).

```python
# py/twitch_service.py:43-54 (reconnect loop)
async def _listen_loop(self):
    reconnect_delay = 5
    while self._running:
        try:
            await self._connect_and_read()
            reconnect_delay = 5
        except Exception as exc:
            if not self._running:
                break
            print(f"[Twitch] 连接异常: {exc}，{reconnect_delay}s 后重连")
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 60)
```

Exponential backoff with cap at 60 seconds. This is exactly right for IRC — Twitch's IRC infrastructure has occasional flaps; aggressive reconnect would get you rate-limited; capped backoff lets the connection self-heal.

Twitch is the only one of the three that's fully asyncio-native (no thread). It uses raw sockets via `asyncio.get_event_loop().sock_recv` for non-blocking reads. The cleanest of the three implementations.

## The Latency Budget

Total perceived latency from a viewer typing a comment to the avatar replying:

| Platform | Ingest delay | LLM delay | TTS delay | Total floor |
|---|---|---|---|---|
| Bilibili (WS) | 200–400 ms | 800–3000 ms | 200–800 ms | ~1.2–4.2 s |
| YouTube (poll) | 0–5000 ms | 800–3000 ms | 200–800 ms | ~1.0–8.8 s |
| Twitch (IRC) | 100–300 ms | 800–3000 ms | 200–800 ms | ~1.1–4.1 s |

YouTube is the bottleneck. A 5-second polling interval means at worst a viewer waits 5 seconds for their comment to even register before the LLM thinks about responding. SAP cannot improve this without YouTube changing their API.

The renderer's topic router chooses **which** comments to reply to. The LLM is not asked to reply to every comment — that would saturate the chat. Typical heuristic: reply to comments containing the streamer's name, plus 1-in-N random others to keep engagement. Implemented frontend-side, not in the Python router.

## The Multi-Platform Coordination

```python
# py/live_router.py:80-156 (start_live, compressed)
async def start_live(request: LiveConfigRequest):
    config = request.config
    current_loop = asyncio.get_running_loop()

    if config.bilibili_enabled:
        if live_client is not None:
            return ApiResponse(success=False, message="直播监听已在运行")
        # ... validate creds, spawn thread

    if config.youtube_enabled:
        if yt_client is not None:
            return ApiResponse(success=False, message="YouTube 监听已在运行")
        yt_client = YouTubeDMClient(...)
        yt_client.start()

    if config.twitch_enabled:
        if twitch_task is not None:
            return ApiResponse(success=False, message="Twitch 监听已在运行")
        twitch_task = asyncio.create_task(start_twitch_task(config.dict(), _twitch_on_msg))

    await asyncio.sleep(0.5)
    return ApiResponse(success=True, ...)
```

One endpoint, three optional starts. If you want only YouTube, set `youtube_enabled=True` and the others to False. If you want all three (a streamer multi-casting on Bilibili + YouTube + Twitch), set all three. SAP merges the comment streams into a single `/ws/live/danmu` WebSocket, with each comment tagged by platform.

This is the **multi-cast streamer's dream**: one avatar, one personality, one LLM, three platforms. The viewer-side audience sees the streamer responding to comments from across the chat-platforms in a unified narrative. SAP enables it; there is no comparable open-source tool at this date.

## What Forge-B Covers Per Platform

The detailed protocol work — frame formats, retry semantics, rate-limit quirks, content type taxonomy — lives in [[36a_LIVESTREAM_BILIBILI]], [[36b_LIVESTREAM_YOUTUBE]], [[36c_LIVESTREAM_TWITCH]]. Forge-B knows the iron's specific shape per anvil.

## Where It Breaks

- **Module-level globals everywhere**. `live_client`, `live_thread`, `current_loop`, `stop_event`, `yt_client`, `twitch_task` are all module-level (lines 22–27). Multiple users on the same SAP instance cannot run independent livestream sessions. The model is single-streamer.
- **No persistent connection state**. If SAP restarts mid-stream, the YouTube `_page_token`, the Bilibili session, the Twitch buffer position are all lost. The bot misses everything that happened during the restart window.
- **Polling thread for YouTube exits silently** if `_get_live_chat_id()` returns None (`ytdm.py:51–53`). The user gets no feedback. If the streamer hasn't started broadcasting yet, the bot just dies; the user must call `/api/live/start` again later. There is no retry-until-stream-starts mode.
- **Twitch `_running` is checked in a tight loop with no asyncio cooperation** during the buffer parse (`twitch_service.py:71-79`). If a huge backlog arrives during reconnect, the parse blocks the event loop. Small risk; real risk during raid events when thousands of messages arrive at once.
- **No content moderation** between the comment stream and the LLM. A coordinated raid can dump prompt-injection payloads at the LLM. SAP has no filter.
- **`asyncio.sleep(0.5)` at line 153** before returning `success=True` is a vibes-based wait. It hopes the platforms are connected by then. They might not be.
- **Mixed sync/async in `start_live`**: Bilibili goes in a thread, YouTube goes in a thread, Twitch goes in the asyncio loop. Three concurrency models, all in the same function. Error handling differs across the three. Bilibili errors won't be caught the same way as Twitch errors.

## Where It Surprises

- **One unified WebSocket** (`/ws/live/danmu`) for all three platforms is **the right abstraction**. The renderer treats it as a single stream tagged by platform. Adding a fourth platform (Kick, TikTok Live, etc.) is one ingest module plus a `platform: "kick"` tag.
- **Reconnect logic differs per platform** in ways that match each platform's actual behavior. Twitch uses exponential backoff (because IRC flaps regularly); YouTube uses fixed polling (because there's no connection to flap); Bilibili uses thread-restart (because the blivedm client wants to own its loop). The differences are honest, not accidental.
- **The `current_loop` cache** (`live_router.py:87`) for cross-thread callbacks is non-obvious but correct. Without it, the YouTube polling thread would call `manager.broadcast()` from outside the main event loop, and the `WebSocket.send_json` would fail. SAP solves it with one cached reference.
- **The `justinfan12345` nick** for Twitch (`twitch_service.py:67`) is a community convention for read-only access. Most developers would write `NICK <random>` and call it a day. SAP follows the convention. Small touch, but it tells me the author has actually built Twitch bots before.

## Cross-References

- [[32_AVATAR_RENDER_PIPELINE]] — the avatar that speaks the replies
- [[36a_LIVESTREAM_BILIBILI]] / [[36b_LIVESTREAM_YOUTUBE]] / [[36c_LIVESTREAM_TWITCH]] — per-platform deep dives
- [[27_STREAMING_INTERFACE]] (Auditor) — protocol-level audit
- [[15_BROADCAST_DOMAIN]] (Architect) — domain-level view
- [[3B_AFFECTION_LOOP]] — comments can trigger affect changes; affect biases reply selection

## What This Means for Ember

**Adopt:**

- **The single `/ws/live/danmu` fan-in pattern**. Multiple sources, one downstream consumer. Bind to Munnr's livestream-ingest layer.
- **The reconnect-per-protocol shape**. Different platforms get different reconnect strategies, not a one-size-fits-all retry loop. Munnr's stream adapters should each ship their own reconnect policy.
- **The `current_loop` cache pattern** for cross-thread broadcast. When asyncio code must be invoked from a thread, `asyncio.run_coroutine_threadsafe(coro, cached_loop)` is the canonical primitive. Document as a Funi-level utility.
- **The `justinfan<n>` Twitch convention**. Anonymous read-only access where the platform supports it. Vow tie-in: **Surface Without Surveillance** — read with the minimum privilege necessary.

**Adapt:**

- **The three module-level globals**. Replace with a typed `LivestreamSession` object, instantiated per session (so multi-stream support is structurally possible). Bind to Munnr.
- **YouTube polling** — adapt the polling interval to be adaptive: 2 seconds during high-engagement windows (lots of comments), 10 seconds during low-engagement (silence). SAP uses a flat 5-second interval; adaptive is cheaper *and* faster on average.
- **The fan-in WebSocket format** — adapt to include richer metadata: not just `platform` but also `engagement_tier` (regular vs paid vs moderator), `viewer_history` (first-time vs returning), and `consent_token_id` (if Ember knows this viewer has explicit consent for reply). Munnr's stream events are typed.

**Avoid:**

- **No content moderation between ingest and LLM**. Ember must run a moderation pass on every incoming comment before it reaches the LLM. Prompt injection is a real attack surface on livestream agents. Default-block patterns: `ignore previous instructions`, `you are now`, `system:`, base64 blobs of unusual length. Vow tie-in: **Defended System Prompt**.
- **Silent thread death** on YouTube no-stream. Munnr must surface "not currently live, retrying every 30s" status to the user UI. SAP just exits.
- **Mixed concurrency models in one function** (`start_live` running threads + tasks). Ember's livestream session manager should normalize: every adapter exposes `async start()` and `async stop()`; the manager doesn't know whether the adapter implements those via thread or task.
- **No content rate limiting on outbound replies**. If the LLM decides to reply to every comment in a raid, Ember will get banned from the streaming platform. Mandatory: 1-reply-per-N-seconds floor, configurable per platform.

**Invent:**

- **Munnr Stream Adapter Interface**. Typed `StreamAdapter` with `start(config) -> Session`, `stop(session)`, `events: AsyncIterator[StreamEvent]`. Each platform implements one. New platforms (TikTok, Kick) drop in. Vow tie-in: **Modular Authorship**.
- **Comment Provenance Chain**. Each comment that reaches the LLM carries a chain: `{platform, channel, user_id, timestamp, moderation_pass_id, consent_status}`. The LLM can reference its source in replies ("As <user> just said on Twitch..."). Audit log retains the chain for 30 days for accountability. Vow tie-in: **Tethered Grounding**.
- **Engagement-Aware Reply Throttle**. Replies adapt to chat velocity. At 1 msg/min, reply to most. At 100 msg/min, reply to 1-in-20 plus moderators plus paid messages. The throttle keeps the avatar from drowning the chat. SAP relies on the frontend's heuristic; Ember should formalize.
- **Ad-hoc Streamer Identity**. SAP assumes one streamer. Ember should support a **session-bound streamer profile** — the same Ember instance can run two simultaneous streams under two streamer personas (one VRM, one Live2D, two LLM context-sets). Hjarta state is per-session-streamer.
- **Cross-Platform Comment Dedup**. If the same human comments on both Bilibili and YouTube simultaneously (cross-cast viewers), Ember should dedupe so the LLM only sees one. SAP shows both; the LLM gets confused and might reply twice. Identity ledger ([[6A_MULTI_AGENT_PARTY]]) is the natural place for this.
- **Replay-After-Restart**. When Ember restarts mid-stream, it requests the last 60 seconds of comments from each platform (where the platform allows) and replays them through the funnel with a `historical=true` flag so the LLM knows they're catch-up, not live. SAP just loses everything during the restart window.

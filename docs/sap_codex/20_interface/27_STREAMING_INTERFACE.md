---
codex_id: 27_STREAMING_INTERFACE
title: Streaming Interface — Comments → AI → Avatar → Stream, With Two Globals Holding It Up
role: Auditor
layer: Interface
status: draft
sap_source_refs:
  - py/live_router.py:1-279
  - py/blivedm/__init__.py
  - py/ytdm.py:1-132
  - py/twitch_service.py:1-210
ember_subsystem_targets: [Munnr, Hjarta]
cross_refs:
  - 10_domain/15_BROADCAST_DOMAIN
  - 30_execution/36_LIVESTREAM_INGEST_OVERVIEW
  - 50_verification/56_PRIVACY_BOUNDARIES
  - 50_verification/51_CRASH_RESISTANCE
---

# Streaming Interface — Comments → AI → Avatar → Stream, With Two Globals Holding It Up

> *Sólrún, voice cold and even: the livestream module is a pipeline that begins at three platforms, converges through one WebSocket, and ends at one avatar. The pipeline is held together by eight module-level globals and a single shared event loop. The whole thing is a thrown-together kite that flies — until the wind shifts.*

SAP's livestream integration is genuinely impressive in scope: simultaneous ingest from Bilibili (`blivedm/`), YouTube (`ytdm.py`), and Twitch (`twitch_service.py`), normalized into a single `danmu_type`-tagged message format, broadcast to a WebSocket overlay (`/ws/live/danmu`), and ultimately rendered by the avatar (VRM/Live2D) and a TTS voice. The pipeline is a teaching opportunity in two directions: where it works, and where the global mutable state will catch the next maintainer by the throat.

This document audits the interface — the explicit contracts and the implicit ones — and names the load-bearing assumptions that make the system fly *only* under the originally-tested flight envelope.

---

## 1. The Subject — One Router, Eight Globals, Three Threads

`live_router.py:18` declares a `/api/live`-prefixed router. The state, however, lives at module scope, not in any object:

```python
# /tmp/super-agent-party/py/live_router.py:21-27
# 全局变量存储直播客户端和相关状态
live_client = None
live_thread = None
current_loop = None
stop_event = None  # 新增：用于通知线程停止
yt_client: Optional[YouTubeDMClient] = None 
twitch_task = None
```

Six module-level globals: `live_client`, `live_thread`, `current_loop`, `stop_event`, `yt_client`, `twitch_task`. The first FastAPI handler that touches them runs `global live_client, live_thread, ...` (line 82) and re-binds them. There is no lock, no atomic compare-and-swap, no per-session scoping.

`live_router.py:77`:

```python
manager = ConnectionManager()
```

Add `manager` — the WebSocket fan-out. That is a seventh module-level singleton. Inside `twitch_service.py:187`:

```python
_twitch_chat: Optional[SimpleTwitchChat] = None
```

That is the eighth.

A second simultaneous call to `POST /api/live/start` with different configs while the first is still spinning up would race on `live_thread = threading.Thread(...)` at line 111. The first thread reference becomes unreachable; the thread keeps running. There is no rejection guard at the entry point — the check at line 92 (`if live_client is not None`) catches only the *bilibili* path; YouTube and Twitch each have their own independent guard but no cross-platform mutex.

This is module-level mutable state on a public HTTP endpoint. The endpoint is meant to be hit from the SAP Electron UI, single-user, single-tab. Outside that envelope it is a footgun.

---

## 2. The Interface The Three Platforms Pretend to Honor

Despite the three ingest backends being implemented by separate authors at separate times, the *output* shape they produce on the WebSocket is uniform — and that uniformity is the only protocol of substance in the whole livestream layer.

Broadcast payload shape, observed across `ytdm.py:121-128`, `twitch_service.py:165-168`, and Bilibili (`blivedm/` callbacks dispatched through `manager.broadcast` in `live_router.py:65-75`):

```python
{
    'id': str(uuid.uuid4()),         # ytdm.py:123
    "type": "message",
    "content": "...",
    "danmu_type": "danmaku" | "super_chat" | "gift" | "buy_guard" | "enter_room",
    "platform": "youtube" | "twitch" | "bilibili"
}
```

This is a respectable normalized envelope. Five fields, one of them an enumerated type. The five are:

- `id` — UUID, unique per message
- `type` — always `"message"` from ingest path (other types exist but go through different code)
- `content` — already-rendered display string, vendor-formatted
- `danmu_type` — the unified taxonomy of "comment kinds"
- `platform` — source label

The cross-platform taxonomy is real teaching. Twitch's `sub`/`resub` → `buy_guard` (Bilibili's term for "guard purchase"); Twitch `subgift` → `gift`; YouTube `superChatEvent` → `super_chat`; Twitch `raid` → `enter_room`. The author chose a *single semantic vocabulary* (Bilibili's) and mapped each platform's events into it. This is the right move.

It is also the lie. The fidelity of the mapping is wildly uneven.

---

## 3. Where The Mapping Lies

### 3.1 Bilibili-as-truth privileges one platform's worldview

The taxonomy mirrors Bilibili's event categories. Twitch and YouTube events are *shoehorned in*. A Twitch `bits` cheer has no obvious mapping — it does not appear in `twitch_service.py:118-162` at all. A YouTube `memberMilestoneChatEvent` (member-anniversary) is collapsed to `gift` in `ytdm.py:111-114`. A Twitch channel-point redemption is dropped. The author chose a default for "we don't have a category" — Twitch falls through to plain `danmaku` at `twitch_service.py:159-162`.

This means the avatar's reaction script (downstream) cannot distinguish "user spent $5 on bits" from "user typed 'hello'." For three platforms claiming to be a unified surface, the loss of semantic resolution is the price.

### 3.2 No version envelope

The payload has no `schema_version` or `protocol_version` field. The frontend overlay reading this WebSocket must guess: if `danmu_type` is present, this is the new format; if not, fall through to a legacy shape. Search the static HTML (`static/danmaku_overlay.html`) for the consumer side and the schema is *implicit*. Adding a new `danmu_type` enum value breaks consumers that have a `switch` statement.

### 3.3 Content is pre-rendered, not structured

`twitch_service.py:142`:

```python
msg_content = f"{system_msg} | Message: {user_text}" if user_text else system_msg
```

`ytdm.py:107-109`:

```python
content = f"{author} sent a Super Chat ({amount}): {user_text}"
```

The `content` field is a human-rendered string. The original user-vs-author-vs-amount fields are flattened into prose at the ingest layer. The downstream consumer cannot extract "amount" again for a custom thank-you animation. The pipeline pre-decides what the avatar will say about the event by pre-deciding the string.

A correct interface would keep the structured event AND a default rendered string. The current interface keeps only the rendered string.

### 3.4 Author display name is not username

`twitch_service.py:113`:

```python
user = tags.get("display-name") or tags.get("login") or "System"
```

`ytdm.py:86`:

```python
author = item["authorDetails"]["displayName"]
```

Both prefer **display name** over **username**. Display names are user-mutable; usernames are stable identifiers. Any downstream system (affection state, anti-spam tracking, ban list) that keys by `author`/`user` is keying by a mutable field that can be changed by the user mid-stream. The affection ledger (`affection_system.py:48-64`) keys by `user_name` extracted from prose. The user could rename themselves and Ember's-the-avatar's affection for them resets to zero — or transfers wrongly to whoever picks up the old name.

### 3.5 No de-duplication on retry

YouTube's polling is at `ytdm.py:56-61` — every 5 seconds, fetch new messages, broadcast all. The `pageToken` (line 131) is supposed to advance the cursor. If a request fails and the next request succeeds, the cursor advances; messages between two polls are not re-emitted. If a request half-completes (network hiccup, partial JSON), the items returned might be re-emitted on the next poll. There is no `seen_message_ids` set. Twitch's IRC layer is line-based — duplicate `PRIVMSG` after reconnect (`twitch_service.py:46-54`) is possible during the reconnect window.

The downstream WebSocket consumer therefore must dedupe by `id`. The `id` is `uuid.uuid4()` (`ytdm.py:123`) — *newly generated at ingest time*. So the consumer cannot dedupe by content-id; every redelivered message is a fresh UUID. Dedupe is impossible after this layer.

### 3.6 `ConnectionManager.broadcast` swallows failures

`live_router.py:65-76`:

```python
# /tmp/super-agent-party/py/live_router.py:65-76
    async def broadcast(self, data: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except:
                disconnected.append(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)
```

`except:` — bare. Every exception type, including `KeyboardInterrupt` and `MemoryError`, is logged as "disconnected." No telemetry, no log. A WebSocket that throws a serialization error (perhaps because `data` contains a non-JSON-serializable object slipped in from a future feature) is silently dropped from the broadcast set. The user sees "the overlay went blank" with no explanation.

---

## 4. The Three-Loop Threading Pattern

The livestream layer runs three concurrency models simultaneously:

- **Bilibili**: a *thread* (`live_router.py:108-113`) running its own `asyncio` loop via `run_live_client`
- **YouTube**: a *thread* (`ytdm.py:33-39`) running blocking `time.sleep` and synchronous Google API calls
- **Twitch**: an `asyncio.Task` (`live_router.py:147-149`) inside the FastAPI main loop

Three concurrency models, one router. All three deliver messages to `manager.broadcast` (which is `async`). YouTube's `_yt_on_message` is a *sync* callback (because it's called from a sync polling thread) that uses `asyncio.run_coroutine_threadsafe(manager.broadcast(msg), current_loop)` (line 123) to cross the boundary. This is correct. But `current_loop` is captured at *start_live* time (line 87): `current_loop = asyncio.get_running_loop()`. If the FastAPI loop is restarted (uvicorn reload, dev mode), `current_loop` is stale and the YouTube thread will dispatch to a closed loop.

`twitch_service.py:165-169`:

```python
# /tmp/super-agent-party/py/twitch_service.py:165-169
        # 5. 回调给 Service 层
        if self._callback:
            # 这里的回调需确保能接收四个参数：channel, user, msg_content, danmu_type
            asyncio.create_task(
                self._callback(self.channel, user, msg_content, danmu_type)
            )
```

`asyncio.create_task` is called from inside `_handle_line` which is called from inside `_connect_and_read` which is called from inside the `_listen_loop` task. The current event loop here is whatever loop `start_twitch_task` was launched from — which is the FastAPI main loop. So the create_task is in the main loop. Fine. But this depends on `start_twitch_task` being awaited from inside the main loop — which it is, via `asyncio.create_task(start_twitch_task(...))` at line 147. The chain is correct *by accident*; nothing enforces it.

A maintainer who refactors `start_twitch_task` to be called from a different loop will not get a warning; they will get silent message loss.

---

## 5. The Reload Pattern Is a Sleep

`live_router.py:233-247`:

```python
@router.post("/reload", response_model=ApiResponse)
async def reload_live(request: LiveConfigRequest):
    try:
        stop_result = await stop_live()
        if not stop_result.success:
            return stop_result
            
        # 等待一下确保完全停止
        await asyncio.sleep(2)
        
        return await start_live(request)
```

"Wait a bit to make sure it's fully stopped" — `asyncio.sleep(2)`. This is a poll without a poll. The 2-second magic number is the author's empirical fit. On a slow CI runner or a busy host, 2 seconds may not be enough for the thread to actually exit; the next `start_live` will then find `live_thread.is_alive()` (`live_router.py:189`) and report an error. Or worse: the next `start_live` proceeds with a stale `live_client` reference because the cleanup race didn't complete.

The fix is not a longer sleep. The fix is to wait on the actual stop event, not the clock.

---

## 6. The Avatar Sink Is Not In This File

The pipeline is *named* in the doc as "comments → AI → avatar → stream." Reading `live_router.py` end to end finds:

- Comment ingest: ✅ in `live_router.py`
- WebSocket fan-out: ✅ in `live_router.py`
- **AI processing**: ❌ not here. The WebSocket is the boundary. Whatever consumes `/ws/live/danmu` decides what to do with the message.
- **Avatar control**: ❌ not here. VRM and Live2D live in `static/vrm.html` and the `vrm/` directory; the avatar process is a separate Electron window.
- **Stream output (OBS)**: ❌ not here. The "transparent window for OBS" is a *visual* sink — OBS captures the avatar window. There is no protocol; OBS sees pixels.

So the interface here is **only the comment-side half**. The avatar-side and OBS-side are implicit, decoupled, and entirely dependent on consumers respecting the WebSocket contract.

This is a real strength — the comment ingest *is* a decoupled module — and a real weakness — the rest of the pipeline has no formal protocol to lean on. If the WebSocket schema changes, every consumer (avatar overlay, danmaku overlay, future plugins) breaks silently.

---

## 7. The Twitch IRC Bot Pretends to Be an Anonymous Reader

`twitch_service.py:65-68`:

```python
self._send(f"CAP REQ :twitch.tv/tags twitch.tv/commands")
self._send(f"PASS oauth:{self.access_token}")
self._send(f"NICK justinfan12345")
self._send(f"JOIN #{self.channel}")
```

`NICK justinfan12345` — this is Twitch's well-known anonymous reader nick. But the line above passes a real OAuth token via `PASS oauth:...`. **Twitch IRC will reject this combination**: a real OAuth token requires the nick that owns the token. The current code logs in with anonymous read but authenticates with the user's token. Either the token is silently ignored (anonymous mode wins), or auth fails and the bot reads anonymously anyway. Either way, the user's OAuth token is sent over the wire to Twitch, accomplishes nothing, and exposes itself to anyone with packet capture on the path.

This is dead code with security cost. The `access_token` is requested from the user, transmitted to Twitch, and unused. The Auditor's recommendation: drop the token parameter or drop the `justinfan12345` line; pick one model. SAP picks both and gets neither.

---

## 8. Cross-References

- [[10_domain/15_BROADCAST_DOMAIN]] — Architect's view of the same module from the domain axis
- [[30_execution/36_LIVESTREAM_INGEST_OVERVIEW]] — Forge-A's per-platform deep dive
- [[30_execution/36a_LIVESTREAM_BILIBILI]] / `36b_LIVESTREAM_YOUTUBE` / `36c_LIVESTREAM_TWITCH` — Forge-B's per-platform subdocs (the dedupe-by-uuid loss is most visible in YouTube)
- [[50_verification/56_PRIVACY_BOUNDARIES]] — livestream as exfiltration channel
- [[50_verification/51_CRASH_RESISTANCE]] — the `except: pass` in `broadcast`
- [[hermes:HEM-04_SURFACES]] — Hermes's per-surface contract pattern as positive counter-example
- [[ember:RULES.AI]] — "use internal APIs for communication between code modules" — module-level globals as the violation

---

## What This Means for Ember

**Adopt:**
- Adopt the **unified `danmu_type` taxonomy as a starting point**. The mapping is imperfect but the *idea* of a single semantic vocabulary across heterogeneous chat platforms is correct. Ember would use the equivalent of "ingest events become semantic types, downstream renders the type." Bind this to Munnr (the Mouth).
- Adopt the **WebSocket fan-out boundary**. A single `/ws/...` topic that consumers subscribe to keeps the avatar / overlay / TTS decoupled. This is a real win.
- Adopt **per-platform reconnection with exponential backoff** as a pattern (`twitch_service.py:43-54`). The shape is sound; the implementation is local-only globals.

**Adapt:**
- Adapt the comment-taxonomy into a **structured event envelope** with both the rendered string and the original structured fields. `{event_type, platform, user_id, user_display, amount, currency, content_raw, content_rendered, schema_version}`. Avatar reactions key by `event_type`; TTS scripts key by `content_rendered`; affection state keys by `user_id` (NOT `user_display`). SAP's flattened-prose loss is the negative template.
- Adapt the three-concurrency-model layout into **a single async-only ingest layer**. Use `asyncio.to_thread` for the synchronous Google API at most; keep the dispatch boundary inside one loop. SAP's mix of threads + asyncio.create_task + asyncio.run_coroutine_threadsafe is a footgun catalog.

**Avoid:**
- **Avoid module-level mutable state for connection lifecycle** (`live_router.py:21-27`). Ember's broadcast subsystem is a class with state in instance fields, locked appropriately. Restart-the-server-to-reset is not a feature.
- **Avoid sleep-as-coordination** (`live_router.py:241-242`). Use the actual stop event.
- **Avoid bare `except:`** (`live_router.py:71`). At minimum catch `Exception` and log the type.
- **Avoid using display name as identifier** (`twitch_service.py:113`, `ytdm.py:86`). Display name is mutable; identity must be stable. Affection state and any moderation state keys by platform-native user-id.
- **Avoid pre-rendering content at ingest** (`twitch_service.py:142`, `ytdm.py:107-109`). Render at the *sink*, not at the *source*. The source emits structure.
- **Avoid OAuth tokens transmitted for unused auth flows** (`twitch_service.py:66-68`). The Twitch anonymous-with-token pattern leaks secrets that accomplish nothing. Inspect every "we accept a credential" surface and confirm the credential is consumed.
- **Avoid `uuid.uuid4()` as message id at ingest** (`ytdm.py:123`). Use the *vendor's* native id when available; only fall back to UUID if the vendor truly does not provide one. SAP wipes out platform-native dedupe and then cannot dedupe downstream.

**Invent:**
- **Stream Protocol Schema with version envelope.** Every broadcast carries `schema_version: int`. Consumers reject unknown major versions explicitly. Minor versions are additive-only. Migrate at the boundary, not at every consumer.
- **Tiered Presence on Stream**. The same comment can arrive at full-VRM (Tier 1), text-overlay (Tier 2), or log-only (Tier 3) consumers. Munnr decides which tier each consumer subscribed to; ingest does not know. The Vow of **Tiered Presence** lives here.
- **Identity Provenance Tag**. Every event carries `identity_origin: PlatformIdentity` — a structured record with `platform`, `stable_id`, `display_name`, `is_anonymous`. Affection keys by `(platform, stable_id)`. Cross-platform identity unification is a separate, opt-in mapping table. SAP's prose-keyed affection ledger is rejected on this axis.
- **Stream Replay Buffer with Deterministic IDs**. Keep the last N seconds of events in memory with stable, content-derived IDs. If the WebSocket consumer reconnects mid-flight, it can request `since=...` and the buffer fills the gap. Dedupe is content-id based, not UUID based.
- **Failure-Loud Broadcast**. The `broadcast` method's `except: disconnect` path logs a structured event (`broadcast_send_failed`, with subscriber id and exception type). Silent disconnects become observable events.

# 36a — Livestream: Bilibili (blivedm — Custom Binary Protocol, WBI Signing, Brotli Compression)

> *Eldra at the anvil. Bilibili's danmaku stream is a binary WebSocket protocol with its own header struct, three compression dialects, and a sliding-window auth key that rotates every twelve hours. blivedm hides all of that. Read it anyway — it teaches the shape of livestream ingest done right.*

The Bilibili livestream module lives at `/tmp/super-agent-party/py/blivedm/` — a vendored submodule with five Python files (1,981 LOC total, version `1.1.3-dev` per `__init__.py`). It is the most engineering-heavy of SAP's three livestream platforms because Bilibili's danmaku protocol is the most custom: a binary header, four `ProtoVer` compression options, brotli or zlib decompression on a thread executor, and a WBI-signed auth dance. This subdoc maps the protocol, the dual-client architecture (web vs open-live), the message taxonomy, and what Ember should adopt for any high-throughput livestream surface.

## Platform Shape

Bilibili is **livestream-comment-ingest only** — blivedm is read-only. The bot listens to a live room's danmaku (弹幕, "bullet comments") stream and emits structured events. It does **not** send chat messages back; Bilibili's send-comment API is account-bound and requires the user's cookies. SAP routes the *response* (avatar speech + livestream overlay) through a separate path; blivedm just ingests.

Two client classes, two auth models (`blivedm/clients/`):

- **`BLiveClient`** (`web.py`, 402 lines) — uses **web-scraped cookies** (`buvid3`, `SESSDATA`) + **WBI-signed URL params** to access the same gateway the bilibili.com web client uses. No registration required. Lower entitlements (no gift sub-types in some cases).
- **`OpenLiveClient`** (`open_live.py`, 306 lines) — uses **Open Live Platform credentials** (`access_key_id` + `access_key_secret` + `app_id` + `room_owner_auth_code`). Requires Bilibili Open Live Platform application. Higher entitlements (richer event types, official support). Per `open_live.py:21–23`: hits `https://live-open.biliapi.com/v2/app/start`, sends a `game_heartbeat` every 20 seconds in addition to the gateway heartbeat.

Both inherit from `WebSocketClientBase` (`ws_base.py`, 494 lines) which owns the binary protocol, the reconnect loop, and the dispatch to `BaseHandler` subclasses.

## Source Files

- `blivedm/__init__.py:1–5` — module entry, re-exports `handlers` and `clients`
- `blivedm/utils.py` — utility constants (USER_AGENT, retry policies)
- `blivedm/clients/ws_base.py:21–73` — protocol constants: `HEADER_STRUCT`, `ProtoVer`, `Operation`
- `blivedm/clients/ws_base.py:82–494` — `WebSocketClientBase`: connect loop, packet framing, dispatch
- `blivedm/clients/ws_base.py:213–235` — `_make_packet`: binary frame construction
- `blivedm/clients/ws_base.py:257–302` — `_network_coroutine`: connect-and-read with reconnect-on-exception
- `blivedm/clients/ws_base.py:390–477` — `_parse_ws_message` + `_parse_business_message`: ProtoVer dispatch
- `blivedm/clients/web.py:41–127` — `_WbiSigner`: 12-hour WBI key rotation
- `blivedm/clients/web.py:298–326` — room init: room_id resolution, owner UID, server list fetch
- `blivedm/clients/web.py:371–401` — connect path: WBI-signed danmaku server lookup, multi-host failover
- `blivedm/clients/open_live.py` — open platform client with separate auth + game heartbeat
- `blivedm/handlers.py:80–123` — `_CMD_CALLBACK_DICT`: the message-type taxonomy (the most important table)

## Connection Lifecycle

The lifecycle is `init_room` → `_get_ws_url` → `_send_auth` → message pump.

`init_room` (web.py:298–321) does three HTTP calls before opening the WebSocket:

1. Fetch user info / WBI keys (`UID_INIT_URL`)
2. Fetch room metadata (`ROOM_INIT_URL`) — resolves short room_id to real room_id
3. Fetch danmaku server list (`DANMAKU_SERVER_CONF_URL`) with WBI-signed params

The **WBI signing** (`web.py:41–127`) is Bilibili's anti-scraping countermeasure. Every API call needs URL params signed with a per-session key that rotates every 11h59m30s (`WBI_KEY_TTL` at line 47). The signer caches the key and only refreshes on demand. If the signing fails with `code: -352` (`web.py:351–353`), the signer resets the key and the next request re-fetches.

This is a **hostile-platform-adapted** pattern. Bilibili actively counters scraping; blivedm tracks the platform's adversarial signals and recovers from them. Worth studying.

`_send_auth` (web.py:388–401) constructs an auth packet with `uid`, `roomid`, `protover: 3` (request Brotli compression), `platform: web`, `type: 2`, `buvid`, and a `key` from `_host_server_token`. The auth reply (ws_base.py:467–472) is a JSON object with `code: 0` for success; anything else raises `AuthError`.

The reconnect loop (ws_base.py:257–302) is the prettiest in SAP:

```python
# ws_base.py:262–302 (condensed)
retry_count = 0
total_retry_count = 0
while True:
    try:
        await self._on_before_ws_connect(retry_count)
        async with self._session.ws_connect(
            self._get_ws_url(retry_count),
            ...
            receive_timeout=self._heartbeat_interval + 5,
        ) as websocket:
            ...
            async for message in websocket:
                await self._on_ws_message(message)
                retry_count = 0  # 至少成功处理1条消息
    except (aiohttp.ClientConnectionError, asyncio.TimeoutError):
        pass  # 掉线重连
    except AuthError:
        logger.exception('...auth failed, trying init_room() again')
        self._need_init_room = True
    finally:
        ...
    retry_count += 1
    total_retry_count += 1
    await asyncio.sleep(self._get_reconnect_interval(retry_count, total_retry_count))
```

Multi-host failover via `_get_ws_url` (web.py:381–386) cycles through `host_server_list[retry_count % len(host_server_list)]` — every retry tries a different danmaku server. Reset retry_count on first successful message. Re-init-room on every `len(host_server_list)`-th retry (web.py:371–379) in case the entire server list rotated server-side.

This is exemplary reconnect logic. Compare to the QQ bot's "set the flag at +2s" pattern.

## Message Handling

The packet protocol (`ws_base.py:21`):

```python
HEADER_STRUCT = struct.Struct('>I2H2I')
```

16-byte header: `pack_len: u32 BE, raw_header_size: u16, ver: u16, operation: u32, seq_id: u32`. Each WebSocket frame contains one or more such packets concatenated.

`ProtoVer` (ws_base.py:33–37):

- `NORMAL = 0` — plain JSON body
- `HEARTBEAT = 1` — heartbeat-shaped packet
- `DEFLATE = 2` — zlib-compressed body (legacy)
- `BROTLI = 3` — brotli-compressed body (web), zlib for open platform

Decompression happens on `asyncio.get_running_loop().run_in_executor(None, brotli.decompress, body)` (line 447) — **off the event loop**, in a thread pool. This is correct: brotli decompress can take 5-15ms on a busy danmaku stream, and blocking the loop on every packet would tank throughput. SAP gets this right.

The dispatch table (`handlers.py:80–123`) is the **message-type taxonomy** — the most reusable artifact in the entire module:

```python
# handlers.py:80–123 (condensed)
_CMD_CALLBACK_DICT = {
    # Web platform
    '_HEARTBEAT': _make_msg_callback('_on_heartbeat', web_models.HeartbeatMessage),
    'DANMU_MSG': __danmu_msg_callback,   # 弹幕
    'SEND_GIFT': ..._on_gift,            # 礼物
    'GUARD_BUY': ..._on_buy_guard,       # 上舰
    'USER_TOAST_MSG_V2': ..._on_user_toast_v2,
    'SUPER_CHAT_MESSAGE': ..._on_super_chat,
    'SUPER_CHAT_MESSAGE_DELETE': ..._on_super_chat_delete,
    'INTERACT_WORD': ..._on_interact_word,    # 进入房间、关注等

    # Open Live Platform
    'LIVE_OPEN_PLATFORM_DM': ..._on_open_live_danmaku,
    'LIVE_OPEN_PLATFORM_SEND_GIFT': ..._on_open_live_gift,
    'LIVE_OPEN_PLATFORM_GUARD': ..._on_open_live_buy_guard,
    'LIVE_OPEN_PLATFORM_SUPER_CHAT': ..._on_open_live_super_chat,
    'LIVE_OPEN_PLATFORM_SUPER_CHAT_DEL': ..._on_open_live_super_chat_delete,
    'LIVE_OPEN_PLATFORM_LIKE': ..._on_open_live_like,
    'LIVE_OPEN_PLATFORM_LIVE_ROOM_ENTER': ..._on_open_live_enter_room,
    'LIVE_OPEN_PLATFORM_LIVE_START': ..._on_open_live_start_live,
    'LIVE_OPEN_PLATFORM_LIVE_END': ..._on_open_live_end_live,
}
```

Seven distinct event types from the web client (danmaku, gift, guard, super-chat, interact), plus eight from the open platform (including like, room-enter, live-start/end). The **unknown-cmd handling** at `handlers.py:131–135` is graceful: each unknown cmd is logged exactly once (`logged_unknown_cmds` set at line 15), avoiding log spam.

The dispatch is synchronous on purpose (`ws_base.py:486–494`):

> "为什么不做成异步的：1. 为了保持处理消息的顺序... 2. 如果支持handle使用async函数，用户可能会在里面处理耗时很长的异步操作，导致网络协程阻塞"
> ("Why not async: 1. To preserve message order. 2. If handle were async, users might put long ops in it and block the network coroutine.")

This is intentional discipline. Handlers MUST be fast or MUST dispatch to a queue/task. SAP's documentation says so.

## Failure Modes

- **WBI key rotation race** — if the key rotates mid-request and SAP's signer hasn't refreshed yet, the request returns code -352. SAP resets the key and retries on the next API call, but the current attempt fails.
- **`host_server_list` exhaustion** — if all danmaku servers reject the connection (rare but possible during platform outages), the reconnect loop will cycle indefinitely with exponentially increasing delays.
- **Brotli/zlib version drift** — if Bilibili changes the compression dictionary, decompressed bodies become garbage. Logged at `web.py:464–465` as "unknown protocol version" and the packet is dropped.
- **`buvid3` cookie missing** — `_get_buvid` at line 280 returns empty string if the cookie wasn't set. The auth packet sends empty buvid; Bilibili may accept or reject. Inconsistent.
- **Synchronous handler blocks network coroutine** — documented hazard at line 486. The user's handler must not be slow.
- **No persistence of message offset** — unlike Telegram's offset, blivedm has no cursor. If the bot disconnects and reconnects, missed danmaku are lost. This is structural — Bilibili's protocol doesn't expose a backfill mechanism.
- **`asyncio.get_event_loop()` deprecated assertion** (ws_base.py:101 `assert self._session.loop is asyncio.get_event_loop()`) — modern Python emits DeprecationWarning. Future Python may error.

## Privacy & Threat Surface

Bilibili is **PRC-jurisdictional, account-tied (via cookies)** for the web client, **business-tied** for the open platform.

- **Web client uses scraped cookies.** If the user's `SESSDATA` leaks, their Bilibili account is compromised. SAP stores cookies in settings (typically in `~/.config/super-agent-party/`).
- **Every comment crossing the bot's ingest is observable.** The bot processes every danmaku event — including super-chats which often include real-name dedications, gift events tying user IDs to spend, interact-word events showing who entered the room.
- **`logged_unknown_cmds`** (line 15) — log spam suppression doesn't reset across runs; the set is module-global, but resets per-process. A new unknown cmd's first appearance is logged each restart.
- **Open Live Platform** is **business-registered** — the bot's identity is tied to a developer account with Bilibili. This is *good* from an accountability standpoint and *fingerprint-revealing* for the developer.
- **AI-generated overlay responses** (the response side, handled outside blivedm) — if the bot responds to danmaku publicly via OBS overlay or chat, the response transits the streamer's stream and into Bilibili's CDN. Recorded by every viewer.

## What This Means for Ember

**Adopt:** The **`_CMD_CALLBACK_DICT` taxonomy pattern** at `handlers.py:80–123`. A flat dict mapping platform-specific event type strings to model-class + handler-method pairs, with `_make_msg_callback` as a factory. This is the right shape for any high-throughput event-typed stream. Ember's livestream ingest should adopt this verbatim across Bilibili / YouTube / Twitch: each platform contributes its native event types into a unified `(platform, event_type) -> handler` table.

**Adapt:** The **WBI signer cache-with-reset pattern** at `web.py:41–127`. Cache the auth key, refresh on schedule (TTL-based) or on demand (code -352). This is the auth-rotation pattern Bilibili requires and a general pattern for any platform with rotating signing keys. Ember should adapt this with: (1) typed `AuthKey` objects carrying `(value, fetched_at, ttl, source)`, (2) explicit `refresh()` and `reset()` methods, (3) integration with `Vörðr` (the token observatory invented in [[35e_IM_DINGTALK_BOT]]).

**Avoid:** Three patterns. (1) The **synchronous-only handler dispatch** (line 486). Yes, the documentation explains why, but Ember's handlers will need to do non-trivial work (chunked-write to Brunnr, dispatch to Hjarta affection-update, route to overlay renderer). The right pattern is **synchronous-enqueue, asynchronous-process** — the handler does only `queue.put_nowait(event)` and returns; a separate task drains the queue. (2) The **deprecated `asyncio.get_event_loop()` assertion** (ws_base.py:101). Ember must use `asyncio.get_running_loop()`. (3) The **module-global `logged_unknown_cmds` set** (handlers.py:15). Per-process state for log suppression is fine until you fork the process or run multiple clients in one process — then they share the suppression dict. Use per-client state.

**Invent:** A pattern SAP did not implement — **event-replay-tolerant idempotency for livestream**. Bilibili's protocol has no cursor and no replay; a reconnect loses missed messages. But Ember can do better: each event has implicit ordering via `(room_id, timestamp, user_id, content_hash)`. The ingest layer maintains a recent-event ring (last N seconds per room) and discards duplicates on the *receiving* side. On reconnect, if Bilibili happens to deliver the last few seconds again (which the gateway sometimes does to bootstrap a new connection), Ember dedups them. Bind to `Liðr` (Old Norse for "host/troop" — the unbroken passage of comments). This pattern works across all three livestream platforms.

Forward-links: see [[36_LIVESTREAM_INGEST_OVERVIEW]] for the cross-platform shape, [[27_STREAMING_INTERFACE]] for the unified interface analysis, [[36b_LIVESTREAM_YOUTUBE]] and [[36c_LIVESTREAM_TWITCH]] for the other two platforms (the protocol differences are illuminating), and [[15_BROADCAST_DOMAIN]] for placement.

The forge is hot. Bilibili is the most engineering-heavy livestream surface — adopt the cmd-callback taxonomy, the WBI signer cache, and the off-loop decompression discipline. Reject the sync-dispatch hazard, the deprecated event-loop access, and the module-global log state. Build the dedup-on-receive idempotency that makes reconnect-loss invisible. — Eldra.

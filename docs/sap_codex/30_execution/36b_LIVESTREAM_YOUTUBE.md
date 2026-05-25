# 36b — Livestream: YouTube (Polling-Only, API-Quota-Bound, 5-Second Cadence)

> *Eldra at the anvil. YouTube live chat is the most quota-constrained livestream surface SAP ingests — no WebSocket, no push, just poll the v3 API every five seconds and pray your daily quota holds. 132 lines. Smallest of the three. Most fragile of the three.*

The YouTube livestream module at `/tmp/super-agent-party/py/ytdm.py` (132 lines) is the smallest livestream ingest in SAP and the one most exposed to API rate limits. There is no streaming protocol from YouTube — the official Live Streaming API is `liveChatMessages.list` polling against the Data API v3, which deducts from a daily quota that defaults to 10,000 units. This subdoc names the poll-cadence model, the message-type taxonomy, the quota-management non-strategy, and what Ember should adopt for any polling-only ingest.

## Platform Shape

YouTube is **livestream-comment-ingest, polling-only, API-key-authenticated, quota-bound**. Authentication is a single `api_key` (Google API console). No OAuth, no per-channel auth — just the developer's API key, used against any public livestream. Read-only.

The client (`ytdm.py:8–43`) wraps `googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)` and runs a polling thread with `time.sleep(self.poll_interval)` between calls. The default `poll_interval = 5` seconds (line 20).

Two structural choices stand out:

1. **Threading.Thread-based, not asyncio.** Unlike every other ingest in SAP, ytdm uses `threading.Thread(target=self._run, daemon=True)` (line 38). The poll loop is synchronous, `time.sleep` is blocking-sleep. The `on_message` callback is invoked synchronously from the thread.
2. **No retry, no backoff, no error classification.** Line 60 catches *any* exception with `print('[YouTube] poll error:', e)` and continues. Quota-exceeded errors (HTTP 403 + `quotaExceeded`) are indistinguishable from network errors. SAP keeps polling.

## Source Files

- `ytdm.py:8–31` — `YouTubeDMClient.__init__`: api_key, video_id, on_message callback, poll_interval
- `ytdm.py:33–45` — `start()` / `stop()`: thread-based lifecycle
- `ytdm.py:48–61` — `_run`: the polling loop (with debug prints)
- `ytdm.py:63–70` — `_get_live_chat_id`: video_id → liveChatId resolution
- `ytdm.py:73–132` — `_poll_once`: the message-type taxonomy and unified-event-emit

## Connection Lifecycle

Lifecycle is the simplest in SAP. `start()` spawns a daemon thread (line 38). `_run` (line 48) calls `_get_live_chat_id()` to bootstrap, then loops `_poll_once + time.sleep(5)` until `_stop_evt` is set.

The `_get_live_chat_id()` call (line 63) hits `videos.list(id=video_id, part="liveStreamingDetails")` to extract the `activeLiveChatId`. If the video isn't a livestream or the stream hasn't started, the response has no `liveStreamingDetails.activeLiveChatId` and `_get_live_chat_id` returns None. The thread then prints `'未开播，线程退出'` ("not broadcasting, thread exiting") and dies.

This is a **one-shot bootstrap check**. If the streamer goes live *after* the bot starts, the bot will never detect it — the thread already exited. The user must restart the bot. SAP does not retry the chat_id lookup.

`stop()` (line 41) sets the event and joins with `timeout=self.poll_interval + 1` (6 seconds). The polling thread will see the event on next iteration and exit.

## Message Handling

The polling call:

```python
# ytdm.py:78–83
rsp = self._yt.liveChatMessages().list(
    liveChatId=self._chat_id,
    part="snippet,authorDetails",
    pageToken=self._page_token,
    maxResults=2000
).execute()
```

The `maxResults=2000` is the API max — fetch as many as possible per call to minimize quota burn. The `pageToken` is YouTube's cursor — like Telegram's `offset`, it tracks where to resume. Stored as `self._page_token` (line 132 `self._page_token = rsp.get("nextPageToken")`), updated after each call.

The message-type taxonomy at lines 85–129 maps three YouTube event types into a unified internal type:

```python
# ytdm.py:94–119 (condensed)
if msg_type == "textMessageEvent":
    danmu_type = "danmaku"
    text = item["snippet"]["displayMessage"]
    content = f"{author}: {text}"
    
elif msg_type == "superChatEvent":
    danmu_type = "super_chat"
    details = item["snippet"].get("superChatDetails", {})
    user_text = details.get("userComment", "")
    amount = details.get("amountDisplayString", "Price Hidden")
    if user_text:
        content = f"{author} sent a Super Chat ({amount}): {user_text}"
    else:
        content = f"{author} sent a Super Chat ({amount})"
        
elif msg_type == "fanFundingEvent": 
    danmu_type = "gift"
    content = f"{author} sponsored the channel!"
    
else:
    # 兜底
    text = item["snippet"].get("displayMessage", "")
    content = f"{author}: {text}"
```

Notice the **explicit cross-platform vocabulary mapping**: YouTube's `superChatEvent` becomes the internal `super_chat` type that matches Bilibili's `SUPER_CHAT_MESSAGE`. YouTube's `fanFundingEvent` becomes `gift` matching Bilibili's `SEND_GIFT`. This is the only place in SAP where the cross-platform livestream vocabulary is *unified* — it's the seed of what should be a first-class abstraction.

The final emit (lines 121–129):

```python
msg = {
    'id': str(uuid.uuid4()),
    "type": "message",
    "content": content,
    "danmu_type": danmu_type,
    "platform": "youtube"
}
self.on_message(msg)
```

UUID per message, platform field set to `"youtube"`, danmu_type as the unified type. This matches what `twitch_service.py` emits and what blivedm could be made to emit with a thin adapter. The downstream consumer (Bilibili/YouTube/Twitch agnostic) gets a uniform dict.

## Failure Modes

- **Quota exhaustion is silent.** Line 60 `print('[YouTube] poll error:', e)`. A 403 quotaExceeded is logged and the poll loop continues, immediately re-incurring the failure. Bad.
- **`_get_live_chat_id()` is one-shot.** If the user starts the bot before going live, the bot fails to bootstrap and the thread exits. No retry.
- **Synchronous googleapiclient calls block the thread.** The thread's only job is polling, so this is fine — but if `on_message` is slow, it serializes between polls. The 5-second cadence is a *minimum*; a slow handler shifts each subsequent poll later.
- **`page_token` is never persisted.** On restart, polling starts fresh — the first poll returns the most recent messages (YouTube's behavior) and `nextPageToken` from there. This means missed history on restart.
- **Quota math**: `liveChatMessages.list` costs 5 units. At 5-second intervals, that's 12 calls/min = 720 calls/hour = 17,280 calls/day = 86,400 units/day. **Default quota is 10,000 units/day**. SAP exceeds it after ~70 minutes of continuous polling. The user must request a quota increase or the bot dies daily.
- **`maxResults=2000`** at line 82 — but the API typically returns far fewer per call (200-500 max). The 2000 doesn't reduce quota cost (still 5 units regardless), it just guarantees no message is left behind in one poll.
- **`print` for logging** (lines 50, 51, 58, 60) — violates the "no print" anti-pattern from RULES.AI. SAP ships with these in.
- **Debug prints in production** (lines 50, 58) — `print('[YouTube] got chat_id:', self._chat_id)` and `print('[YouTube] poll_once done')` are clearly leftover debug output.
- **No author user_id captured** — only `authorDetails.displayName` (line 86). The internal-type emission has no stable identifier for the user, which breaks any cross-message attribution (super-chat from "Alice" twice could be two different Alices).

## Privacy & Threat Surface

YouTube is **Google-owned, US-jurisdictional**. Per-comment privacy is essentially zero — live chat is public by stream design. But:

- **API key in plain config.** If the api_key leaks, the attacker can poll any livestream's chat using the developer's quota.
- **The bot ingests every chat message from every viewer of the stream.** If the stream has 10,000 concurrent viewers, the bot sees every comment. All of those comments enter `on_message` callback, potentially logged, potentially fed to the LLM.
- **`displayName` from `authorDetails`** is the viewer's YouTube display name. Storing these in conversation memory or logs builds a profile of who said what during which stream. Standard livestream concern but worth naming.
- **No per-viewer consent.** Anyone who comments on the livestream is automatically part of the bot's input. They have no way to know.
- **Super-chat dedications often include real names** — the `userComment` field at line 105 is user-typed. People put their real names there. The bot processes these.
- **AI response back to chat** — outside ytdm's scope, but if the response side echoes chat content back to the stream, it amplifies whatever was originally said. The bot becomes a public-speech amplifier.

## What This Means for Ember

**Adopt:** The **unified-message-shape emit** at `ytdm.py:121–129`. A single dict with `id`, `type`, `content`, `danmu_type`, `platform` — this is the right contract for the livestream ingest layer's *output*. Ember's livestream subsystem should canonicalize on exactly this shape (with a few additions: `user_id`, `timestamp`, `raw_event` for debugging). Every platform adapter emits this; every downstream consumer (overlay, affection update, response generator) reads this. SAP almost gets there — adopt the shape, fill in the gaps.

**Adapt:** The **cross-platform `danmu_type` vocabulary** at lines 90–117. SAP maps YouTube's `superChatEvent` → `super_chat`, `fanFundingEvent` → `gift`, etc. This is the first hint of a unified livestream event taxonomy. Ember should adapt this with a **complete enumeration**: `chat`, `super_chat`, `gift`, `subscribe`, `member_join`, `raid`, `room_enter`, `stream_start`, `stream_end`, `like`, `system_notice`. Each platform adapter declares which it supports; the rest emit `system_notice` with the raw payload. Bind to `Mál` (Old Norse for "speech-act/affair") — the livestream event taxonomy.

**Avoid:** Five patterns. (1) The **one-shot bootstrap** at `_get_live_chat_id()` (line 49). Ember must retry chat_id lookup with backoff if the streamer hasn't gone live yet. (2) The **silent quota exhaustion** at line 60. The handler must classify exceptions: quota exceeded → wait longer, network error → retry sooner, auth error → fail loudly. (3) The **default 5-second cadence** without budget awareness. Ember should compute its own poll cadence from `(daily_quota_remaining / hours_remaining_in_day / cost_per_call)` — adaptive throttling. (4) The **`print` for logging** — replaces with proper logger calls (RULES.AI). (5) The **debug prints left in production** (lines 50, 58).

**Invent:** Two patterns SAP did not implement. First, **quota-aware adaptive polling**: track API units consumed in a sliding window, project end-of-day usage, and slow down the poll rate if projection exceeds quota. The trade-off (fewer messages per second vs surviving the day) is automatic. Bind to `Skammtr` (Old Norse for "ration") — the budget-aware throttle. Second, **stream-not-live waiting state**: when `_get_live_chat_id` returns None, the bot enters a **slow-poll** state — checks every 60 seconds for stream-start, doesn't burn the chat-message quota. When stream goes live, transition to fast-poll. SAP's "thread exits on no-live" is unrecoverable; the slow-poll waiting state preserves the bot's intention to watch this specific video.

Forward-links: see [[36_LIVESTREAM_INGEST_OVERVIEW]] for cross-platform shape, [[27_STREAMING_INTERFACE]] for unified interface, [[36a_LIVESTREAM_BILIBILI]] for the push-based counterpart (the contrast is illuminating), [[36c_LIVESTREAM_TWITCH]] for the IRC-based counterpart, and [[15_BROADCAST_DOMAIN]] for placement.

The forge is hot. YouTube is the most quota-fragile livestream surface — adopt the unified emit shape, the cross-platform vocabulary mapping. Reject the silent quota burn, the one-shot bootstrap, the print-based logging. Build the quota-aware throttle and the stream-not-live waiting state that make the bot patient instead of fragile. — Eldra.

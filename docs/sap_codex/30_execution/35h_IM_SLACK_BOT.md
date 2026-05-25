# 35h — IM Bot: Slack (Socket Mode, Edit-In-Place Streaming, Event Subscriptions)

> *Eldra at the anvil. Slack is the second sanctioned Western enterprise-IM, and the only one in SAP that uses chat_update for in-place streamed replies. The bubble grows in place. The user sees one message, not a chunked flurry.*

The Slack bot at `/tmp/super-agent-party/py/slack_bot_manager.py` (349 lines) uses Slack's `slack_sdk` with Socket Mode (a WebSocket tunnel that lets the bot receive events without exposing a public HTTPS endpoint) and edits messages in place during streaming. This subdoc maps Slack's distinctive socket-mode + edit-streaming model, its rate-limit-aware update cadence, and what Ember should learn about enterprise-IM with native edit support.

## Platform Shape

Slack is **bot account, Socket Mode (WebSocket-tunneled events), bot_token + app_token dual auth, channel-keyed, edit-in-place streaming via `chat_update`**. Authentication requires **two** tokens (lines 22–23):

- `bot_token` — `xoxb-...` — for the Web API (sending messages, fetching channels)
- `app_token` — `xapp-...` — for Socket Mode (WebSocket auth)

This dual-token model is Slack's specific OAuth shape. The `bot_token` is per-workspace; the `app_token` is per-app. Both must be valid for the bot to function.

```python
# slack_bot_manager.py:106–114
async def _async_start(self, config: SlackBotConfig):
    web_client = AsyncWebClient(token=config.bot_token)
    auth = await web_client.auth_test()
    self.bot_user_id = auth["user_id"]

    self.socket_client = SocketModeClient(app_token=config.app_token, web_client=web_client)
```

`auth.test` (line 108) fetches the bot's own user_id — this is used later (line 117) to filter out self-sent messages. Crucial for avoiding bot-loops in event-subscribed channels.

## Source Files

- `slack_bot_manager.py:21–32` — `SlackBotConfig` Pydantic schema
- `slack_bot_manager.py:35–148` — `SlackBotManager` lifecycle, dual-token auth, socket-mode bring-up
- `slack_bot_manager.py:113–127` — `process_listener`: Socket Mode event handler with ack-then-process
- `slack_bot_manager.py:151–187` — `_dispatch_message`: slash commands + cancel-and-replace
- `slack_bot_manager.py:189–281` — `_handle_message_logic`: streaming AI with `chat_update` edits
- `slack_bot_manager.py:317–345` — `execute_behavior_event`: proactive push

## Connection Lifecycle

The socket-mode bring-up is unusual in two ways:

1. **Handler registration before connect** — `socket_client.socket_mode_request_listeners.append(process_listener)` (line 123) is appended to a list, not registered via decorator. Slack SDK style.
2. **Manual keepalive loop** — after `await self.socket_client.connect()` (line 124), SAP runs `while self.is_running: await asyncio.sleep(1)` (line 127). The connect call returns immediately after handshake; the actual event pump runs inside the SDK on its own task. SAP's `while` loop just keeps the asyncio loop alive.

This is **dual-task ownership without explicit `gather`**: the SDK runs its socket pump, SAP runs the keepalive, neither knows about the other. If the SDK's pump dies silently, SAP's loop continues happily until `stop_bot` flips the flag.

The Socket Mode listener (lines 113–122):

```python
async def process_listener(client, req: SocketModeRequest):
    if req.type == "events_api":
        await client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
        event = req.payload.get("event", {})
        if event.get("user") == self.bot_user_id or event.get("bot_id") or "subtype" in event:
            return
        if event.get("type") in ["message", "app_mention"]:
            await self._dispatch_message(event, web_client)
```

Three filters at line 117:

- `event.get("user") == self.bot_user_id` — skip self-sent messages
- `event.get("bot_id")` — skip messages from *any* bot (broad — even other bots' replies are skipped)
- `"subtype" in event` — skip messages with subtypes (channel_join, message_changed, etc.)

The third filter is the most consequential: Slack tags edited messages with subtype `message_changed`, joined messages with `channel_join`, file-shares with `file_share`. SAP skips all of them. This means the bot doesn't react to edits — an edited message is invisible to SAP. Acceptable behavior, but undocumented.

Shutdown (`stop_bot` at line 137): `self.is_running = False` (immediate, breaks the keepalive loop), `socket_client.close()` via `run_coroutine_threadsafe`, cancel all `active_tasks`, then `loop.call_soon_threadsafe(loop.stop)`. No thread.join. The thread is daemon.

## Message Handling

Cancel-and-replace at lines 173–187, slash commands at lines 158–169 (`/stop`, `/restart`).

The distinctive Slack feature is **edit-in-place streaming** at lines 211–263:

```python
# slack_bot_manager.py:211–263
# 发送占位
initial_resp = await web_client.chat_postMessage(channel=cid, text="...")
reply_ts = initial_resp["ts"]
...
async for chunk in stream:
    ...
    content = delta.content or ""
    reasoning = getattr(delta, "reasoning_content", None) or ""
    display_content = reasoning if (self.config.reasoning_visible and reasoning) else content

    full_response.append(content)
    state["text_buffer"] += display_content
    state["image_buffer"] += display_content

    # 控制更新频率
    now = time.time()
    if (now - last_update_time > 1.2) or any(sep in content for sep in self.config.separators):
        seg = self._clean_text(state["text_buffer"])
        if seg:
            await web_client.chat_update(channel=cid, ts=reply_ts, text=seg + " ▌")
            last_update_time = now

full_content = "".join(full_response)
await web_client.chat_update(channel=cid, ts=reply_ts, text=self._clean_text(full_content) or "Reply complete.")
```

The pattern: post a placeholder (`"..."`) immediately, capture its timestamp (`ts`), then `chat_update` the same message as the LLM streams. The `▌` cursor character at line 259 is a UX flourish — shows "still generating." On stream end, one final `chat_update` removes the cursor.

The rate-limit-aware cadence (line 256): update *either* every 1.2 seconds *or* whenever a separator hits content. Slack's rate limit for `chat_update` is roughly 1/sec per channel for most tier-3 endpoints; 1.2s gives safety margin.

This is the **best streaming UX in SAP**. The user sees one message bubble that grows in place — exactly like ChatGPT in a browser. Beats Discord's chunked-send by a mile.

Outbound:

- **Text reply** — `chat_postMessage` for placeholder, then `chat_update` for streaming (line 211, 259)
- **Image** — `files_upload_v2(channel=cid, file=bytes, filename=...)` (line 297)
- **Voice (TTS)** — same `files_upload_v2` with `.mp3` filename (line 309)

No Omni voice support in Slack bot — `state` dict doesn't include `audio_buffer`. The bot ignores `delta.audio` chunks entirely.

The 300-character TTS truncation (line 305 `payload["text"] = clean_text[:300]`) is **distinct from the streaming text**: SAP synthesizes voice from the first 300 chars only, regardless of the full reply length. Slack-specific compromise — probably because Slack discourages multi-megabyte audio uploads.

The proactive push (line 317) calls `self.socket_client.web_client.chat_postMessage(channel=cid, text=reply)` — same `chat_postMessage` as the user-reply path, no special threading.

## Failure Modes

- **`bot_id` filter is too broad** (line 117) — skips messages from *any* bot. If a user wants the bot to react to another bot (e.g. a deploy notification), SAP can't.
- **Subtype filter loses edits** (line 117) — described above. Edits are invisible to SAP.
- **`chat_update` rate limit** — Slack tier-3 endpoints allow ~1/sec/channel. The 1.2s minimum (line 256) is conservative. But if the LLM streams burstily (lots of separators in a short window), SAP can exceed this. The SDK retries but warns; SAP doesn't surface the warning.
- **`reply_ts` is captured once** (line 213) — if the initial `chat_postMessage` returns success but the message is later deleted (admin moderation), every subsequent `chat_update` returns `message_not_found`. SAP doesn't handle this; the streaming silently disappears.
- **`auth_test` once at startup** (line 108) — if the bot's permissions are revoked at runtime, `chat_postMessage` will start 401'ing. SAP catches the exception (`except Exception as e` at line 277) and posts an error to the channel, *but the post itself fails*. Silent death.
- **No reconnect path** — if the Socket Mode WebSocket drops, the SDK should reconnect, but SAP has no visibility. The keepalive loop at line 127 doesn't check connection state, just `self.is_running`.
- **`file_links` empty default with no eviction** (line 195) — same memory-leak shape as QQ/WeChat. Per-channel state grows unbounded.
- **`/id` returns channel_id** (line 201) — same as others, useful for behavior config, exposes ID space.
- **`global_behavior_engine.register_handler("slack", ...)`** (line 77) — registers inside `main_startup`, but if `start_bot` is called twice (manager re-init), the handler is registered twice. Engine emits the proactive message twice.

## Privacy & Threat Surface

Slack is **enterprise-tenanted, US-jurisdictional (Salesforce-owned, San Francisco)**. The privacy posture is workspace-admin-mediated:

- **Workspace admin sees all bot activity** in audit logs. Standard enterprise tradeoff.
- **`channel_id` not user-keyed** — same Discord-style cross-user memory mixing. In a public channel, all users' messages become context for the bot's response.
- **Two-token leak risk doubled.** Either `xoxb-...` (Web API) or `xapp-...` (Socket Mode) leaking compromises the bot. SAP stores both in plain config.
- **`files_upload_v2` puts the file on Slack's CDN** — long-lived URL associated with the workspace.
- **TTS truncation to 300 chars** (line 305) means voice replies are *incomplete* — but the user might assume voice == text. Subtle UX misalignment that could leak unspoken content to text-readers (the assistant's actual reply is visible in text; only the voice is truncated).
- **Subtype filter loses edits** — described above. If a user posts something, then edits it to add sensitive content, SAP never sees the edited version. This is *good* for privacy of the editor and *bad* for response correctness.

## What This Means for Ember

**Adopt:** The **edit-in-place streaming pattern** at `slack_bot_manager.py:211–263`. Post placeholder, capture timestamp, `chat_update` periodically. This is the right shape for any platform with native edit support — Telegram (via `editMessageText`), Feishu (via post-mode updates), WeCom (via `reply_stream`). The contract is: *one message bubble, multiple updates, one final commit*. Munnr should expose `stream_in_place(surface_id, content_generator, max_update_hz)` as a first-class operation, and each platform's adapter implements it natively or falls back to chunked-send.

**Adapt:** The **rate-limit-aware update cadence** at line 256. The intent is right (don't exceed 1/sec), but the implementation is hardcoded (1.2s minimum). Ember should adapt: each platform adapter declares its per-channel update rate-limit; the streaming wrapper enforces it adaptively. If the limit changes (Slack tier upgrade, Discord nitro server boost), the adapter reports the new cap, not a hardcoded constant. Bind to `Hrynjandi` (Old Norse for "rhythm") — the rate-shape declaration surface.

**Avoid:** Three patterns. (1) The **subtype filter that drops edits** silently (line 117). If a user edits a message, that edit might be the user clarifying or correcting — the bot should at minimum log it, not silently miss it. Discord, Telegram, Feishu all have similar edit semantics. (2) The **300-char TTS truncation** without UX indication (line 305). If voice is truncated, the user must be told (e.g. "(text continues)" appended to the voice). (3) The **handler-registration-on-startup-without-deregister** (line 77). If the bot is restarted, behavior handlers stack. Ember must ensure handler registration is idempotent or paired with deregister on shutdown.

**Invent:** A pattern SAP did not implement — **stream-edit truncation-with-summary**. Slack's `chat_update` has a per-message length cap (40K chars). A very long LLM reply will eventually exceed this. The current pattern would silently fail. Ember's invention: when the streaming buffer exceeds 80% of the platform's per-message cap, finalize the current message with a "(continues...)" suffix, post a new placeholder, and continue the stream there. Threading by reply or in-thread message keeps continuity. Bind to `Framhald` (Old Norse for "continuation") — the long-stream-continuation pattern.

Forward-links: see [[35_IM_BOT_DEPLOYMENT_OVERVIEW]] for cross-platform shape, [[26_IM_BOT_INTERFACE]] for unified abstraction (Slack is the streaming-edit exemplar), [[35g_IM_DISCORD_BOT]] for the chunked-send counterpoint, and [[14_MESSAGING_DOMAIN]] for placement.

The forge is hot. Slack is SAP's best streaming UX — adopt the edit-in-place pattern, the rate-aware cadence, and the dual-token explicit auth shape. Reject the broad subtype filter, the silent TTS truncation, and the non-idempotent handler registration. Build the long-stream continuation pattern that respects every platform's per-message limit. — Eldra.

# 35c — IM Bot: WeCom (The Sanctioned China-Enterprise Surface)

> *Eldra at the anvil. WeCom is what WeChat would be if it had been designed for legitimacy from the start: bot_id + secret, long-lived WebSocket, stream-friendly reply protocol, no QR-scraping required.*

WeCom (Enterprise WeChat / 企业微信) is Tencent's enterprise-tier IM, and the one platform among the three China-Tencent surfaces (QQ, WeChat-personal, WeCom) that ships with a real bot SDK and proper authentication. The bot at `/tmp/super-agent-party/py/wecom_bot_manager.py` (404 lines) uses the `aibot.WSClient` library — a long-lived WebSocket client that connects to Tencent's enterprise gateway with a sanctioned `bot_id` + `secret` pair. This subdoc names what WeCom does that the personal WeChat bot wishes it could, where it still leaks, and what Ember can borrow without inheriting a ToS violation.

## Platform Shape

WeCom is **bot account, enterprise-tenanted, WebSocket-keepalive, stream-reply-capable**. The bot opens a long-lived connection via `WSClient(WSClientOptions(bot_id=..., secret=...))` (lines 112–113), registers event handlers, and stays connected indefinitely. There is no polling, no webhook, no QR scrape. Authentication is the Webhook Key / Bot ID / Secret triple the user obtained from the WeCom admin console.

A WeCom bot lives **inside one or more enterprise chats** that an admin has provisioned for it. It does not roam — it sees only the chats it was invited to. This is the structural difference from QQ (which sees C2C and @-mentions across all groups it's in) and the seismic difference from WeChat personal (which sees everything the human user's account can see). WeCom enforces tenancy.

Three message types are handled distinctly:

```python
# wecom_bot_manager.py:192–198
def register_events(self):
    @self.ws_client.on('message.text')
    async def on_text(frame): await self.handle_message(frame, "text")
    @self.ws_client.on('message.image')
    async def on_image(frame): await self.handle_message(frame, "image")
    @self.ws_client.on('message.voice')
    async def on_voice(frame): await self.handle_message(frame, "voice")
```

Text, image, voice — each routed through a unified `handle_message(frame, msg_type)` (line 200). Other types (file, location, etc.) are silently dropped at this layer.

## Source Files

- `wecom_bot_manager.py:22–32` — `WeComBotConfig` Pydantic schema (note `bot_id` + `secret`, no appid pair)
- `wecom_bot_manager.py:34–173` — `WeComBotManager` lifecycle + behavior-engine sync
- `wecom_bot_manager.py:110–137` — `_async_run_websocket`: connect + keepalive loop
- `wecom_bot_manager.py:176–404` — `WeComClient`: message dispatch, AI loop, behavior engine
- `wecom_bot_manager.py:280–326` — stream-reply protocol via `reply_stream(frame, stream_id, content, is_done)`

## Connection Lifecycle

Setup is direct: instantiate `WSClient`, register event handlers, `await connect()`, then loop `await asyncio.sleep(1.0)` until shutdown (lines 128–131). The keepalive is internal to `aibot.WSClient` — SAP does not run its own heartbeat task.

Status flag flipping is more honest than QQ: `is_running = True` is set *after* `connect()` returns (line 121), not on a 2-second timer. The startup_complete event fires after that point (line 122), so callers waiting on it have a real signal.

Shutdown (`stop_bot` at line 153) sets `_stop_requested = True` and joins the thread with a 3-second timeout. The keepalive loop (line 130 `while not self._stop_requested`) exits cleanly on the flag change. Inside `_cleanup` (line 139), `ws_client.disconnect()` is called best-effort, then any in-flight `active_tasks` are cancelled.

This is the most honest lifecycle of the eight IM bots. No magic sleeps. No stdout sniffing. No reload-as-recovery. The only weak spot is line 130's `asyncio.sleep(1.0)` keepalive granularity — a stop request can take up to 1 second to honor. Acceptable.

## Message Handling

The cancel-and-replace task pattern is here too (lines 224–230), with the same `/停止` / `/重启` slash commands honored at lines 210–221. The structural pattern across IM bots is now fully visible: it is identical to QQ's, identical to WeChat's. SAP has the right *idea* but did not factor it into a shared module — every IM bot reimplements the pattern. This is one of the highest-value extractions for Ember (see [[26_IM_BOT_INTERFACE]]).

The distinctive WeCom feature is **stream reply**. From `wecom_bot_manager.py:288–310`:

```python
# wecom_bot_manager.py:288–310
stream_id = generate_req_id('stream')
full_response_text = ""
try:
    stream = await client.chat.completions.create(
        model=self.WeComAgent,
        messages=self.memoryList[chat_id],
        stream=True,
        extra_body={"is_app_bot": True, "platform": "wecom"}
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta
        content = delta.content or ""
        reasoning = getattr(delta, "reasoning_content", "") or ""
        
        display_content = (reasoning if self.reasoningVisible and reasoning else content)
        full_response_text += display_content
        
        if display_content:
            # 企微 SDK 负责流式分段发送
            await self.ws_client.reply_stream(frame, stream_id, full_response_text, False)
    
    # 发送最后一段
    await self.ws_client.reply_stream(frame, stream_id, full_response_text, True)
```

`reply_stream(frame, stream_id, content, is_done)` is WeCom's first-class streaming primitive. The bot sends progressive `is_done=False` updates as the LLM streams in, then one final `is_done=True` to seal it. The client app sees a single message that *grows* in place — like a Slack `chat_update` or a Telegram `editMessageText`, but native to the WeCom client.

This is significant: WeCom is the only Chinese platform among the eight that ships LLM-shaped streaming at the protocol level. QQ requires post-and-pray with separator chunks. WeChat personal requires post-and-pray with separator chunks. WeCom gets it right.

Multi-modal in is supported: voice (via internal ASR at line 271 `_transcribe_audio`), image (base64-embedded into OpenAI multimodal content at line 265). The image download uses `ws_client.download_file(url, aeskey)` — files are AES-encrypted at the platform level, and the SDK handles decryption transparently. This is platform-level message-in-transit encryption that QQ and WeChat-personal don't expose.

Voice-out via TTS-to-AMR conversion is in `_send_voice` at line 370. WeCom requires `.amr` audio (Tencent's perennial codec) — SAP calls its own TTS endpoint for MP3, then `convert_to_amr_simple` in a thread to transcode. Then uploads via the `upload_media` Webhook endpoint (line 389), then sends as `voice` message type.

## Failure Modes

- **Webhook Key vs Bot ID confusion** — `bot_id` is the public Webhook Key; `secret` is the long-connection-specific secret. WeCom admin console shows both but the labels are not intuitive. Wrong combo gives "认证失败" with no diagnostic differentiation.
- **Enterprise admin revocation** — admin can disable the bot at any time. The WebSocket connection drops; reconnect fails; `_startup_error` is set on next attempt. Recovery requires admin re-provisioning.
- **AES file decryption mismatch** — if the SDK and platform's AES key derivation drifts (SDK version vs platform version), `download_file` returns garbage bytes. SAP would feed garbage as base64 into the LLM, which would then try to interpret a corrupt image. The user sees confused output.
- **No reconnect inside SAP** — `aibot.WSClient` handles reconnect internally (presumably with exponential backoff), but SAP has no visibility into its retry state. If the SDK gives up, SAP marks `is_running = False` only at thread-exit time, which may be after a long delay.
- **`reply_stream` retry semantics** — there's no documented behavior for what happens if a `reply_stream(is_done=False)` fails mid-stream. SAP does not check the return value (line 307). The user could see a stuck-at-50% message bubble.
- **Per-chat behavior engine targets are admin-visible** — line 91 reads `target_ids` from settings. If an enterprise admin audits the bot's config, they see exactly which chats the AI is proactively messaging. This is *good* from a transparency standpoint and *bad* from a "the user assumed it was private" standpoint.

## Privacy & Threat Surface

WeCom is **PRC-jurisdictional like QQ and WeChat-personal**, but with two important structural differences:

1. **Enterprise tenancy.** The bot lives inside an admin-provisioned enterprise. The admin sees the bot's actions in their audit log. This is more transparent than personal WeChat (where Tencent sees but the user doesn't) but less private (the employer also sees).
2. **Sanctioned bot identity.** The bot has a stable identity (`bot_id`), which means recipients see a "Bot" badge in their UI. They know they're talking to a non-human. This is the right shape — no impersonation, no consent ambiguity.

What still leaks:

- **All messages transit Tencent.** Same Cybersecurity Law / Data Security Law exposure as QQ.
- **Behavior engine + admin visibility = ambient surveillance.** An admin who configures `behaviorTargetChatIds` aggressively can use the AI as an indirect surveillance tool — proactively messaging employees and harvesting reply content. SAP has no visible safeguard against this.
- **TTS audio + ASR** — voice messages are transcribed locally (SAP's internal `/asr`), which is good, but the transcribed text then goes to the LLM (potentially cloud), which is the standard tradeoff.

## What This Means for Ember

**Adopt:** The **stream reply protocol** at `wecom_bot_manager.py:288–310`. The contract is `reply_stream(channel_or_frame, stream_id, current_full_text, is_done: bool)` — progressive growing-in-place messages instead of chunked separate-message sends. This is the right surface for any platform that supports it. Munnr should expose a unified `stream_to_surface(surface_id, full_text_so_far, done: bool)` method, and each platform's adapter chooses: native streaming (WeCom, Slack via `chat_update`, Telegram via `editMessageText`) or chunked-send-with-separator (QQ, WeChat-personal). The decision is at the adapter, not the agent.

**Adapt:** The `aibot.WSClient`'s opaque internal reconnect. The intent is right (reconnect is the SDK's job, not the bot manager's), but SAP gets *no visibility* into the retry state. Ember should require any IM-bot adapter to expose a `connection_state()` interface — `{state: "connected"|"reconnecting"|"failed", last_error: str|None, retry_count: int}` — and surface this through the host's status endpoint. The SDK can do the reconnecting; the host has to know it's happening.

**Avoid:** Two patterns. (1) The reuse of `chat_id` directly from frame body without **input sanitization** (line 203 `chat_id = body.get('chatid', body.get('from', {}).get('userid', ''))`). A malicious or malformed frame could supply a chat_id that collides with a different conversation's namespace. Ember must enforce a typed, validated chat-id space. (2) The implicit assumption that the **behavior engine has been authorized to message all `behaviorTargetChatIds`**. Same issue as WeChat-personal: there is no per-recipient consent ledger. Even with WeCom's bot badge mitigating impersonation, proactive contact still needs consent tracking.

**Invent:** A pattern SAP did not implement — **stream-reply abort signaling**. When a user types `/stop` during an in-flight `reply_stream`, the current implementation cancels the asyncio task but does *not* send a final `is_done=True` with the truncated content. The recipient sees the message bubble freeze at the last update. Ember's version should: on cancel mid-stream, send one final `reply_stream(frame, stream_id, current_text + "\n[stopped]", is_done=True)` so the bubble closes cleanly. This is the **graceful interrupt** missing from SAP's surface, and it applies to every streaming platform (WeCom, Slack, Telegram). Bind it to a True-Name candidate: `Lokahljóð` (closing sound) — the final acknowledged shape of any interrupted stream.

Forward-links: see [[35_IM_BOT_DEPLOYMENT_OVERVIEW]] for cross-platform deployment shape, [[26_IM_BOT_INTERFACE]] for the unified-abstraction analysis (where stream-reply vs chunked-send is the central axis), [[14_MESSAGING_DOMAIN]] for placement, and [[56_PRIVACY_BOUNDARIES]] for the China-platform threat catalog.

The forge is hot. WeCom is the sanctioned China surface — it shows what proper enterprise-IM-bot deployment looks like even within PRC jurisdiction. Inherit the stream-reply primitive. Reject the implicit-consent assumption. Build the graceful-interrupt close-out. — Eldra.

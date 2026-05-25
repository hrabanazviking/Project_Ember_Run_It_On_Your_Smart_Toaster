# 35g — IM Bot: Discord (Intents, Channels, Async-Native, 1800-Char Forced Splits)

> *Eldra at the anvil. Discord is the most Western-native IM SAP supports — gateway WebSocket, intents-gated, message-content-locked-behind-flags, channel-shaped. The bot uses the official `discord.py` library and behaves accordingly.*

The Discord bot at `/tmp/super-agent-party/py/discord_bot_manager.py` (440 lines) is the only IM deployment in SAP that uses a fully sanctioned, well-known SDK (`discord.py`) and inherits its conventions directly. This subdoc names how Discord's intents-and-channels model shapes the deployment, where SAP's bot makes uniquely Discord-shaped choices (1800-char forced splits, code-block-aware separator handling), and what Ember should learn about the platform-native deployment template.

## Platform Shape

Discord is **bot account, gateway-WebSocket, intents-gated, channel-keyed, native-streaming-via-edits-or-chunks**. Authentication is a single `bot_token` from the Discord Developer Portal. The bot connects via `discord.Client(intents=intents).start(token)` (line 91), where `intents` must explicitly request `message_content = True` (line 146):

```python
# discord_bot_manager.py:144–147
intents = discord.Intents.default()
intents.message_content = True
super().__init__(intents=intents)
```

This is a critical Discord-specific gotcha: as of Discord's 2022 intent restructuring, `MESSAGE_CONTENT` is a **privileged intent** that requires explicit Developer Portal opt-in for bots in 100+ servers. SAP enables it client-side, but the platform won't honor it unless the bot's portal config matches. Failure mode: the bot connects, receives `on_message` events, but `msg.content` is always empty. SAP has no diagnostic for this.

The keyed state space is **`channel.id`** (line 168 `cid = msg.channel.id`) — Discord conversation memory is per-channel, not per-user. This means in a busy channel, multiple users' messages collapse into one conversation history. Useful for group chat dynamics; risky for privacy (anything anyone says becomes context for everyone else's reply).

## Source Files

- `discord_bot_manager.py:22–32` — `DiscordBotConfig` Pydantic schema
- `discord_bot_manager.py:35–140` — `DiscordBotManager` lifecycle (uses official `discord.Client.start`)
- `discord_bot_manager.py:143–162` — `DiscordClient.__init__` + `on_ready`
- `discord_bot_manager.py:164–204` — `on_message`: cancel-and-replace dispatch with slash commands
- `discord_bot_manager.py:206–345` — `_process_ai_logic`: streaming AI loop with code-block-aware separators
- `discord_bot_manager.py:289–310` — the **code-block-aware separator scanner** (the distinctive logic)
- `discord_bot_manager.py:347–401` — outbound helpers (omni voice, transcribe, send_image)

## Connection Lifecycle

Standard `discord.py` lifecycle. The `on_ready` callback (line 159) is the readiness signal — when fired, `self.manager.is_running = True` and `_ready_complete.set()`. Inbound dispatch via `on_message` (line 164) handles the cancel-and-replace + slash-command pattern.

Shutdown (`stop_bot` at line 103): cancel all `active_tasks`, then `asyncio.run_coroutine_threadsafe(self.bot_client.close(), self.loop)` to invoke discord.py's clean close. The thread.join with 5s timeout. discord.py's own close handles the gateway disconnect properly.

The startup uses `_ready_complete.wait(timeout=30)`. If the gateway can't connect (token bad, intents misconfigured, Discord outage), the wait times out and `start_bot` raises `RuntimeError("Discord 机器人就绪超时")`.

## Message Handling

Three slash commands at lines 174–185 (`/stop`, `/restart`, `/id`). Cancel-and-replace at lines 188–204.

The inbound parse loop (lines 224–242) handles multi-modal:

- **Images**: every attachment with `content_type` starting with `image` is downloaded via `att.read()` (Discord's CDN), base64-embedded for OpenAI multimodal.
- **Audio**: attachments with `content_type` starting with `audio` are sent to internal `/asr`. The transcribed text is *appended to `user_text` with a `[语音转写]` prefix* (line 232) — distinctive choice: Discord puts voice transcription back into the text stream rather than treating it as a separate modality.

Wake-word check at line 234. If configured and absent, bail.

The **distinctive Discord-shaped logic** is the code-block-aware separator scanner (lines 289–310):

```python
# discord_bot_manager.py:291–310
if state["text_buffer"] and not self.config.enable_tts:
    buffer = state["text_buffer"]
    split_pos = -1
    in_code_block = False
    
    # 检查分隔符（复杂逻辑保留）
    i = 0
    while i < len(buffer):
        if buffer[i:].startswith("```"): in_code_block = not in_code_block; i += 3; continue
        if not in_code_block:
            for sep in self.config.separators:
                if buffer[i:].startswith(sep):
                    split_pos = i + len(sep)
                    break
            if split_pos != -1: break
        i += 1
    
    # 强制分段
    if len(buffer) > 1800: split_pos = 1800
```

This is the *only* IM bot in SAP that tracks code-block state during chunked sending. The reason: Discord renders ` ``` ` fenced code blocks specially, and splitting a message mid-code-block produces two malformed half-blocks. The `in_code_block` toggle ensures separators inside ` ``` ` are skipped.

The **1800-character force split** (line 309) is Discord-specific: Discord's per-message length limit is 2000 characters. SAP uses 1800 as a safety margin. If the buffer grows past 1800 without hitting a separator, force-split.

This is *almost* clever. The bug: a code block that grows past 1800 characters will be force-split at character 1800, ignoring the `in_code_block` state. The user sees a malformed half-block. SAP knows this and ships it anyway — no graceful degradation.

Streaming sends use `msg.channel.send(clean)` (line 315). No `chat_update` equivalent — Discord's `editMessage` exists but SAP doesn't use it. So a streamed reply is a sequence of separate messages, not one growing-in-place. This is the trade-off SAP makes for streaming UX: chunked separate messages instead of edit-in-place.

Outbound:

- **Text** — `msg.channel.send(clean)` (line 315) or `msg.reply(text)` for slash command acks
- **Image** — `discord.File(io.BytesIO(...))` sent via `channel.send(file=...)` (line 399)
- **Voice (TTS)** — opus from internal TTS, sent as `discord.File` (line 386). Discord plays opus inline.
- **Omni voice** — `discord.File(io.BytesIO(audio_data), filename=f"voice.{ext}")` via `msg.reply(file=file)` (lines 351–352). Discord won't play arbitrary audio inline as a voice message; the `.opus` plays inline if Discord recognizes it, else it's a download.

Proactive behavior (`execute_behavior_event` at line 402) fetches the channel via `self.get_channel(cid)` — relies on discord.py's cache. If the channel isn't cached (bot restarted, hasn't seen the channel yet), the proactive message silently fails.

## Failure Modes

- **MESSAGE_CONTENT intent mismatch** — described above. Most likely Discord-specific deployment failure. SAP has no diagnostic; the bot appears to work but never sees content.
- **1800-char force split mid-code-block** — described above. Visible UX bug.
- **`get_channel(cid)` cache miss** — proactive behavior fails silently when channel not yet cached (line 413 `if channel:`).
- **`msg.attachments[*].read()`** is async and unrestricted — Discord allows up to 8MB attachments (Nitro: 50MB / 100MB). A user spamming large files can saturate the bot's bandwidth.
- **Wake-word check happens after attachment download** — line 234 happens *after* lines 224–232 already read the attachments. A bot configured with wake-word still pays bandwidth cost for ignored messages.
- **Bot's own messages filtered only by `msg.author == self.user`** (line 165) — a different bot (e.g. another instance of SAP) in the same channel would be processed as a user. No bot-loop detection beyond self-identity.
- **`config.separators` containing `"```"` would break the code-block scanner** — line 297 increments `i += 3` on `"```"` and separator detection is in the `elif`. If a config sets separator `"```"`, separator matching is bypassed during code blocks but works elsewhere — confusing but not catastrophic.
- **`enable_tts` mode skips text send entirely** — lines 291, 320: if TTS is on, the text buffer is never sent as text, only as audio. The user with the audio muted gets no signal. Discord doesn't have a "transcript available" affordance.

## Privacy & Threat Surface

Discord is **Western-jurisdictional (US-Delaware, San Francisco-HQ)**, more open than Chinese platforms but with its own concerns:

- **Channel-keyed memory mixes users.** Anyone in the channel contributes to the conversation context. This is the largest privacy axis: in a busy server, user A's message becomes context for user B's reply. SAP has no opt-out.
- **`msg.attachments[*].url`** is a Discord CDN URL — long-lived, public if known. SAP downloads via `att.read()` (using the authenticated SDK), but the URL itself, if logged, is fetchable by anyone who has it.
- **Voice attachments transcribed via internal ASR** — text leaves the host only if the LLM endpoint is remote.
- **Proactive messages to a channel** — line 415 sends without indicating "this is bot-initiated" vs "responding to user." Channel members see a message with the bot avatar but no prior trigger.
- **`/id` exposes channel_id** (line 217) — same as other platforms.
- **`active_tasks` keyed by int channel_id** — dict keys with non-int from a malicious frame could collide. discord.py validates types so this is low-risk.

## What This Means for Ember

**Adopt:** The **code-block-aware text splitter** at `discord_bot_manager.py:289–310`. This is the right shape for any platform where ` ``` ` fenced blocks have special rendering — and that's nearly every modern IM platform (Slack, Telegram, Discord, Feishu's post format). Ember should pull this into a shared `markdown_aware_split` utility under Munnr, parameterized by max-char-limit, separator set, and which Markdown syntax to be aware of (code blocks, lists, quotes). Don't write it 8 times.

**Adapt:** The **intents-explicit declaration** at line 146. SAP requests `message_content` because Discord requires it. Ember should adapt this concept: every IM-bot adapter declares its **required platform privileges** in its manifest, and Hjarta refuses to start a bot whose Developer Portal config doesn't match (where checkable). Bind to `Leyfi` (Old Norse for "permission/leave") — the platform-privilege declaration surface.

**Avoid:** Three patterns. (1) The **1800-char force-split that ignores code-block state** (line 309). If forced split overlaps a code block, the splitter must back up to the last `\n` outside a code block, even if that means a slightly oversized message. (2) The **`get_channel(cid)` silent-fail** for proactive (line 413). Ember must distinguish "channel not cached, retry later" from "channel doesn't exist" — they look identical here. (3) **Channel-keyed memory across users**. If Ember adopts Discord at all, the memoryList must be keyed by `(channel_id, user_id)` tuples so that user A's history doesn't bias user B's context.

**Invent:** A pattern SAP did not implement — **conversation-context boundary inference**. In a multi-user channel, Ember should infer conversation boundaries from time + topic shifts rather than mixing all messages into one memory thread. When the topic shifts (cosine distance between recent embeddings exceeds threshold) or time gap exceeds N minutes, start a fresh memoryList. This pattern is invisible to SAP but emerges naturally from the privacy-violation of channel-keyed shared history. Bind to `Heiti` (Old Norse for "name" — the way a conversation gets its identity) — the boundary-inference subsystem.

Forward-links: see [[35_IM_BOT_DEPLOYMENT_OVERVIEW]] for cross-platform shape, [[26_IM_BOT_INTERFACE]] for unified abstraction, [[35h_IM_SLACK_BOT]] for the other Western enterprise-IM (and the streaming-via-edit comparison), and [[14_MESSAGING_DOMAIN]] for placement.

The forge is hot. Discord is the platform-native case study — adopt the code-block-aware splitter, the intents declaration, and the channel-shaped event model. Reject the force-split bug, the silent get_channel fail, and the cross-user memory mixing. Build the conversation-boundary inference that respects multi-user channels. — Eldra.

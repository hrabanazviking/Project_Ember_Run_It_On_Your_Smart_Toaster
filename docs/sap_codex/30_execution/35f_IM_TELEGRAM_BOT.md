# 35f — IM Bot: Telegram (Open, Pleasant, Long-Poll With Omni Support)

> *Eldra at the anvil. Telegram is the IM that respects you back: a public Bot API, long-poll HTTP, no SDK lock-in, no enterprise dance. If only the other seven were like this.*

Telegram is the cleanest IM deployment in SAP. The bot is split across two files — `/tmp/super-agent-party/py/telegram_bot_manager.py` (137 lines) holds the lifecycle scaffolding; `/tmp/super-agent-party/py/telegram_client.py` (370 lines) holds the actual logic. Together they implement long-poll-based Telegram Bot API ingestion with multi-modal in/out, Omni audio, slash commands, and proactive behavior — without any SDK, just `aiohttp` and well-typed Bot API endpoints.

## Platform Shape

Telegram is **bot account, public API, long-poll HTTP, no SDK lock-in, parse_mode=Markdown by default**. Authentication is a single `bot_token` from @BotFather. There is no client-side SDK; SAP makes direct HTTP requests to `https://api.telegram.org/bot{token}/...` endpoints.

The poll loop is the central pattern (`telegram_client.py:47–58`):

```python
async def run(self):
    timeout = aiohttp.ClientTimeout(total=35) 
    self.session = aiohttp.ClientSession(timeout=timeout)
    ...
    while not self._shutdown_requested:
        try:
            updates = await self._get_updates()
            for u in updates:
                await self._handle_update(u)
        except asyncio.TimeoutError:
            pass
        if not updates:
            await asyncio.sleep(0.1)
```

`_get_updates` (line 60) calls `/getUpdates?offset={self.offset}&timeout=5`. Telegram's long-poll holds the request open for up to 5 seconds; if any update arrives before then, it returns immediately. `self.offset` is incremented after each handled update (line 73 `self.offset = u["update_id"] + 1`) — Telegram uses this to discard already-acknowledged updates from the next response.

The `ClientTimeout(total=35)` (line 36) is the outer timeout, with margin over Telegram's 5-second long-poll. Robust shape.

The poll-and-handle pattern is the most resilient of the eight: every message is durably acknowledged by offset advancement. If the bot crashes mid-handle, the offset has not been advanced; on restart, Telegram redelivers. This is at-least-once delivery with the bot owning the cursor.

## Source Files

- `telegram_bot_manager.py:7–17` — `TelegramBotConfig` Pydantic schema
- `telegram_bot_manager.py:19–137` — `TelegramBotManager` lifecycle (uses standard `_ready_complete` event pattern)
- `telegram_client.py:7–34` — `TelegramClient.__init__`: state, behavior engine registration
- `telegram_client.py:35–58` — `run()`: the long-poll core
- `telegram_client.py:70–107` — `_handle_update`: slash commands + cancel-and-replace dispatch
- `telegram_client.py:108–169` — message-type-specific handlers (text, photo, voice)
- `telegram_client.py:170–261` — `_process_llm`: streaming AI loop with Omni audio support
- `telegram_client.py:262–315` — outbound send methods (text, photo, voice, omni voice)
- `telegram_client.py:317–342` — file/audio helpers

## Connection Lifecycle

`_run_bot_thread` (line 60) creates a new event loop and runs `main_startup()` (line 64). The startup:

1. Loads settings and sync behavior engine config (lines 67–74)
2. Constructs `TelegramClient` (line 76)
3. Bulk-attaches config attrs via `for attr in [...]: setattr(...)` (line 78) — terse but clean
4. Sets `_startup_complete` (line 87) before `await self.bot_client.run()` blocks indefinitely

The `_ready_complete.set()` happens **inside** `TelegramClient.run()` at line 43 — the client signals ready right before the poll loop starts. This is honest: ready means polling has started, not "30 seconds elapsed."

Shutdown (`stop_bot` at line 112): set `_stop_requested = True`, set `_shutdown_requested = True` on the client, cancel all `active_tasks`, join thread with 10s timeout. Clean.

## Message Handling

The cancel-and-replace pattern is here too (line 94–96), with slash commands (`/stop`, `/restart`, `/id`) honored across both English and Chinese names. Telegram's `parse_mode: Markdown` (line 277) means LLM Markdown output renders correctly in clients.

Three inbound types (lines 122–168):

1. **text** — `/id` returns chat_id; otherwise wake-word filter, then `_process_llm`
2. **photo** — Telegram's `photos` array contains size variants; SAP picks the largest (`photos[-1]`), calls `_get_file` to get the path, fetches the bytes, base64-encodes for OpenAI multimodal
3. **voice / audio** — `_get_file`, fetch, send to internal `/asr` for transcription, then process as text

The dispatch is wrapped in `_dispatch_message` (line 108) which catches `asyncio.CancelledError` and exception cleanly. Each message type's handler does its parse-then-process work without further nesting.

Outbound (lines 275–315):

- **Text** (`_send_text` at line 275): POST to `/sendMessage` with `parse_mode: Markdown`. If 200 fails (Markdown parse error), retry without parse_mode — Telegram is strict about valid Markdown.
- **Photo** (`_send_photo` at line 284): fetch URL bytes, POST to `/sendPhoto` as multipart.
- **Voice TTS** (`_send_voice` at line 303): call internal TTS for `.opus`, POST to `/sendVoice` as multipart.
- **Omni voice** (`_send_omni_voice` at line 262): the LLM's native audio output. If opus-compatible, send as Voice; otherwise as Document (`.wav` fallback). Same Omni path as Feishu.

The `_process_llm` (line 170) is the most readable AI loop in SAP. It:

1. Appends user message to `memoryList[chat_id]`
2. Calls internal OpenAI-compat endpoint with streaming
3. Per-chunk: extracts content + reasoning + audio + tool metadata
4. Streams text via separator-chunked `_send_text` (lines 218–232) unless TTS mode (then accumulate)
5. End-of-stream: clean up text buffer, extract markdown images, send images, dispatch Omni audio if buffered, persist conversation memory

The TTS-mode-mutually-exclusive-with-streaming logic at line 219 (`not self.enableTTS`) is deliberate — if TTS is on, don't send text chunks (the user wants voice), accumulate full text then synthesize.

## Failure Modes

- **Network partition during long-poll** — the `aiohttp.ClientTimeout(total=35)` wraps the entire request. On total network loss, the loop sees `asyncio.TimeoutError`, `pass`es, and re-polls. This is correct.
- **`getUpdates` returns `ok: false`** — line 66 returns `[]`. The loop continues. The bot has no diagnostic for *why* the call failed (rate limit, invalid token, server error all look the same). Silent degradation.
- **`parse_mode: Markdown` strict-parse failure** — line 280–281: if `sendMessage` returns 200-but-actually-failed (Markdown parse error returns non-200), the retry strips parse_mode and tries again. Defensive, but the second call's failure is unhandled.
- **`_send_text` retry path strips parse_mode globally** — line 281 — but the message content still contains Markdown syntax (asterisks, underscores). The user sees raw `*bold*` instead of rendered. Acceptable degradation.
- **`offset` advance happens before message handling completes** (line 73). If the handler crashes after offset advance but before the message is fully processed (multi-step like photo + ASR + LLM), Telegram considers it delivered and won't redeliver. At-least-once is *almost* — there's a window.
- **Photo download size limit** — Telegram caps file sizes at 20MB for bots. SAP's `_get_file` (line 317) doesn't check size. A large file URL returned by `getFile` would be downloaded in full, blocking the event loop on the read.
- **`offset` is per-instance, not per-token** — if two bot instances share the same token, they fight for the same update offset. Telegram serves each `getUpdates` to whichever poller got there first. SAP has no defense against this.
- **`Markdown` vs `MarkdownV2`** — line 277 uses legacy Markdown. Telegram has moved most clients to MarkdownV2 with more escapable characters. SAP's legacy mode works for simple text but breaks on URLs with parentheses, code blocks with backticks-in-content, etc.

## Privacy & Threat Surface

Telegram is **non-China-jurisdictional, partially open-source-client, server-cloud-hosted (Telegram FZ-LLC, UAE-headquartered)**. Threat profile is *meaningfully different* from the seven other IM platforms:

- **No state-level access surface** comparable to PRC platforms. Telegram has resisted multiple government data requests; it is not safe to assume invulnerable, but the threat profile is qualitatively different.
- **End-to-end encryption** is **not** on by default for bots. Bot conversations are server-side-encrypted only. Telegram employees with sufficient access could read them.
- **`bot_token` in URL** — line 61, 142, 161, 276, 288, 305, 311: token in URL path. If logs are kept of outbound HTTP from the SAP host (proxy, packet capture, system log), the token is exposed. Authorization-header-based auth would be safer, but Telegram's API mandates URL path tokens.
- **All messages routed through Telegram servers.** Standard cloud-IM exposure.
- **`/id` command exposes chat_id** (line 128) — this is intentional (the user needs it for behavior config), but logs of bot replies could reveal the chat_id space.
- **Long poll cursor (`self.offset`) is not persisted** — if SAP restarts, the offset resets. Telegram will redeliver any messages newer than the last `getUpdates` acknowledgment. Acceptable for a chatbot, but reveals replay-on-restart behavior.

## What This Means for Ember

**Adopt:** The **offset-cursor durable-delivery pattern** at `telegram_client.py:73`. The bot owns the cursor; the platform redelivers anything before cursor-advance. This is the right shape for *any* polling IM surface, and Ember should make it explicit: every polling-based adapter (Telegram, YouTube live chat, potentially Twitter/X if ever added) tracks a cursor in durable storage (not in-memory). On restart, the bot picks up where it left off, modulo possible duplicate delivery (which the LLM-call layer must idempotency-handle).

**Adapt:** The **single-file long-poll pattern**. SAP's Telegram is the only IM bot that runs against the public API without an SDK — pure `aiohttp` calls. This is the most portable and Pi-friendly shape (no SDK install, no native deps). Ember should adapt: for any IM platform where the public API is well-typed, prefer direct HTTP over SDK. Bind to a True-Name candidate: `Beinleiðr` (Old Norse for "straight path") — the SDK-less direct-API adapter style.

**Avoid:** Three patterns. (1) The **legacy `parse_mode: Markdown`** (line 277) instead of `MarkdownV2`. Ember must use the more strict modern parse mode and escape user content properly. (2) **`bot_token` in URL path**. Where the platform supports header-based auth (Telegram does not, but others might), prefer that. Where it doesn't, ensure the URL is never logged outside the bot's own context. (3) The **offset-advance-before-handle** order at line 73. Ember should advance the cursor *after* the message handler returns successfully, or use a transactional pattern (write `processed=True` to durable storage atomically with cursor advance).

**Invent:** A pattern SAP did not implement — **deduplication-tolerant LLM call shape**. Because the long-poll cursor can replay on restart, the LLM call must be idempotency-safe at the conversation-memory level. Ember should: when a message arrives, hash `(chat_id, message_id, content)` and check a recent-hash ring (last 64 IDs per chat). If hit, treat as duplicate — append to memory once but don't generate a second response. This pattern emerges naturally from Telegram's at-least-once semantics and applies to every polling-based platform. Bind to `Endurminni` (Old Norse for "renewed memory") — the dedup-aware conversation memory surface.

Forward-links: see [[35_IM_BOT_DEPLOYMENT_OVERVIEW]] for cross-platform shape, [[26_IM_BOT_INTERFACE]] for the unified abstraction (Telegram is the cleanest case), [[2A_VOICE_INTERFACE]] for the Omni audio path, and [[36b_LIVESTREAM_YOUTUBE]] for the other polling-cursor surface.

The forge is hot. Telegram is the IM platform that respects the developer — adopt its long-poll cursor discipline, the direct-HTTP simplicity, and the per-message-type handler split. Reject the legacy parse mode and the pre-handle cursor advance. Build the dedup-aware memory layer. — Eldra.

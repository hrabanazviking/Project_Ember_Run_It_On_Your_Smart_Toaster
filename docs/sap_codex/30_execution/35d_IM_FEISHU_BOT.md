# 35d — IM Bot: Feishu (Lark — Corporate-Asia With Omni Audio)

> *Eldra at the anvil. Feishu is ByteDance's enterprise-IM and the most feature-dense of the eight: post-format text, AI-generated Omni audio, image cards, file replies — all over a single long-poll WebSocket with explicit ping management.*

Feishu (international: Lark) is ByteDance's WeCom analog — enterprise-tier, admin-provisioned, sanctioned bot identity. The bot at `/tmp/super-agent-party/py/feishu_bot_manager.py` (602 lines — the largest of the eight IM modules) wraps Lark's official `lark_oapi` SDK with a custom WebSocket receive loop and the richest message-type coverage in SAP. This subdoc maps what Feishu uniquely offers, where its complexity becomes brittle, and what Ember should adopt for any "rich message" surface.

## Platform Shape

Feishu is **bot account, enterprise-tenanted, WebSocket-with-custom-ping, post-format-native, multi-modal-in-and-out**. Authentication is the standard `app_id` + `app_secret` pair from the Lark developer console.

The most distinctive structural choice is **SAP managing the ping loop explicitly** instead of letting the SDK do it:

```python
# feishu_bot_manager.py:138–156
async def _async_run_websocket(self):
    try:
        await self.ws._connect()
        self._startup_complete.set()
        self._ready_complete.set()
        self.is_running = True
        
        ping_task = asyncio.create_task(self.ws._ping_loop())
        receive_task = asyncio.create_task(self._message_receive_loop())
        
        if global_behavior_engine.is_running:
            global_behavior_engine.stop()
            await asyncio.sleep(0.5)

        behavior_task = asyncio.create_task(global_behavior_engine.start())
        await asyncio.gather(ping_task, receive_task, behavior_task, return_exceptions=True)
```

Three concurrent tasks: ping, receive, behavior. The ping task drives `self.ws._ping_loop()` (a Lark SDK internal that SAP reaches into to start), the receive loop pumps messages with `asyncio.wait_for(self.ws._conn.recv(), timeout=1.0)` and dispatches each via `asyncio.create_task(self.ws._handle_message(msg))` (line 163) — receive does not block on message handling.

This is more honest concurrency than WeCom's single-loop sleep. The ping cadence is owned by the SDK; SAP only schedules it. The receive loop has its own 1-second timeout to give the stop check (`self._stop_requested`) a chance to fire.

But — `self.ws._connect()` and `self.ws._ping_loop()` are SDK private members (underscore prefix). SAP is reaching into Lark SDK internals because the public API doesn't expose the granularity needed. This works today and breaks on SDK updates.

## Source Files

- `feishu_bot_manager.py:21–32` — `FeishuBotConfig` Pydantic schema
- `feishu_bot_manager.py:34–221` — `FeishuBotManager` lifecycle, ws management, behavior config
- `feishu_bot_manager.py:113–127` — `lark.Client` + `EventDispatcherHandler` setup
- `feishu_bot_manager.py:223–602` — `FeishuClient`: message handling, multi-modal, Omni audio, behavior engine
- `feishu_bot_manager.py:306–442` — `_do_handle_message`: the rich-message processing core
- `feishu_bot_manager.py:445–504` — `_send_omni_response`, `_send_voice`: audio surfaces

## Connection Lifecycle

The dispatcher pattern at line 117–120:

```python
event_dispatcher = lark.EventDispatcherHandler.builder("", "")\
    .register_p2_im_message_receive_v1(self.bot_client.sync_handle_message)\
    .build()
```

Empty strings for the builder's two args (verification_token, encrypt_key) — these are blank because Feishu's WebSocket connection mode (vs webhook mode) doesn't require them. The single registered handler `sync_handle_message` (line 247) bridges Lark's sync callback to the asyncio loop via `asyncio.run_coroutine_threadsafe(self.handle_message(data), loop)` (line 255).

The `_message_receive_loop` (line 158) is SAP's own implementation of the WebSocket pump:

```python
async def _message_receive_loop(self):
    while not self._stop_requested and not self._shutdown_event.is_set():
        if self.ws._conn is None: break
        try:
            msg = await asyncio.wait_for(self.ws._conn.recv(), timeout=1.0)
            asyncio.create_task(self.ws._handle_message(msg))
        except asyncio.TimeoutError: continue
        except: break
```

The bare `except: break` at line 165 is aggressive — *any* exception from the WebSocket breaks the loop. This is closer to "fail fast" than "self-healing." Reconnection would have to come from the outer thread restarting the whole bot.

Shutdown at `stop_bot` (line 186) is multi-step: set flags, cancel all active conversation tasks (line 195), call `ws._disconnect()` via `run_coroutine_threadsafe`, then join the thread. The `_stop_requested = False` at line 205 (post-join) is a curious reset — it means after stop completes, the manager could in principle be restarted. Useful pattern.

## Message Handling

Feishu has **four inbound message types** that SAP handles distinctly (lines 322–358):

1. **text** — plain string (`{"text": "..."}`), parsed straight.
2. **image** — image_key reference. SAP calls `lark_client.im.v1.message_resource.get(...)` to fetch the binary, base64-encodes for OpenAI multimodal.
3. **post** — Feishu's rich-text format. A nested JSON with paragraphs and elements (text, link, at, image, media). SAP walks it via `_extract_text_from_post` + `_extract_images_from_post` (lines 506–527). This is the richest in-format among the eight platforms.
4. **audio** — file_key for an audio attachment. Fetched, sent to internal `/asr`, transcribed.

Outbound is equally rich:

- **Text-as-post** (line 538): every text reply is sent as a `msg_type="post"` with `{"zh_cn": {"content": [[{"tag": "md", "text": text}]]}}` — Feishu interprets `tag: "md"` as Markdown, so the LLM's Markdown output renders correctly in the client.
- **Image** (line 551): fetched from URL, uploaded via `lark_client.im.v1.image.create`, sent as `msg_type="image"`.
- **Voice (TTS path)** (line 486): SAP TTS to `.opus`, uploaded via `im.v1.file.create(file_type="opus")`, sent as `msg_type="audio"`.
- **Omni (LLM-native audio)** (line 445): the rare path — if the LLM stream contains `delta.audio.data` chunks, SAP accumulates them, converts via `convert_to_opus_simple`, and sends as `audio` (if opus-compatible) or `file` (if WAV fallback).

The Omni path (line 384–385, 425–428) is the only one in SAP that handles **first-party LLM audio output**. If the model (e.g. GPT-4o realtime) streams audio chunks directly, Feishu can deliver them as a voice message bubble. This is the future-shape of AI-IM: the LLM's voice is the bot's voice, no TTS round-trip required.

The reply path (line 543–548) handles both `chat_type == "p2p"` (private — uses `message.create`) and group chats (uses `message.reply` against the original message_id). This threading distinction matters for Feishu's UX, where group replies appear inline.

## Failure Modes

- **`lark_oapi` SDK internals churn** — SAP reaches into `ws._connect`, `ws._ping_loop`, `ws._conn`, `ws._handle_message`, `ws._disconnect`. Five private-method dependencies. An SDK update that renames any of these breaks the bot silently.
- **`message_resource.get` is synchronous** — lines 333, 344, 354. SAP calls these inside an async coroutine without `to_thread`. The SDK's HTTP call blocks the event loop. Multiple concurrent image-message handlers will serialize on this.
- **Bare `except: break`** in receive loop (line 165) — see above. No reconnect strategy.
- **Post format extraction depth-limited** — `_extract_text_from_post` (line 506) only walks two levels deep (`content` → paragraphs → elements). A deeply nested post structure (which Feishu allows) loses content.
- **Image cache from LLM markdown** — `_extract_images(state)` at line 529 only runs at end-of-stream. If the LLM emits 10 images, all 10 are queued at the end and sent serially via `_send_image` (line 421) — each is a separate HTTP fetch + upload + send. No batching.
- **`json.loads(msg.content)` without try/except in most paths** — lines 273, 323, 330, 340, 351. Malformed content from the platform crashes the handler.
- **Mock object for behavior trigger** (line 571–573): `class Mock: def __init__(self, cid): self.chat_id = cid; self.message_id = None; self.chat_type = "p2p"`. SAP fakes a message object for proactive behavior messages. The `_send_text` then assumes `chat_type == "p2p"` is correct — but if the behavior target is actually a group, the bot will create a new top-level message rather than reply to context, breaking conversation threading.

## Privacy & Threat Surface

Feishu is **ByteDance-owned, headquartered in Singapore for Lark and China for Feishu**, with separate data residency by edition. PRC users are PRC-jurisdictional; Lark international users are routed through Singapore.

Specific exposures:

- **Same enterprise-admin visibility as WeCom.** Behavior engine targets are visible in admin audit logs.
- **Post format leaks paste structure.** If a user pastes a complex document into a Feishu chat, the bot's `_extract_text_from_post` flattens it — but the original structured content is preserved in the bot's memoryList. A future operation that re-emits the conversation could leak the source structure.
- **Omni audio bypasses TTS sanitization.** The `_send_voice` path strips Markdown (`clean_markdown` at line 477). The Omni audio path does not — whatever the LLM generates audibly is what the user hears. If a prompt injection causes the model to emit privileged content as audio, it reaches the user unfiltered.
- **`message_id` reference in behavior mock is `None`** (line 572) — proactive messages will skip the threading branch and create top-level messages, making them clearly "out of context" which is actually *good* for distinguishing bot-initiated content. Accidental safety.

## What This Means for Ember

**Adopt:** The **explicit-task-triad keepalive** at `feishu_bot_manager.py:145–153`. Ping task + receive task + behavior task, all in `asyncio.gather(..., return_exceptions=True)`. This is the right shape for any platform that maintains a persistent connection — break the responsibilities into named tasks, let each fail independently, and let the gather collect outcomes. Munnr's IM-bot supervisor should make this triad mandatory.

**Adapt:** The post-format multi-modal **outbound** shape. SAP sends text as post-with-Markdown (line 541) which renders well in Feishu's client. Ember should adapt this by introducing a **typed-content adapter layer**: `Content = Text | Markdown | Image(url) | Audio(bytes, format)`. Each platform adapter knows how to render each Content type natively. This means the agent never decides "send as post" or "send as text" — it sends a `Content` object and Munnr decides per-platform. SAP duplicates the per-platform send logic 8 times; Ember should write it once.

**Avoid:** Three patterns. (1) The **synchronous SDK calls inside async handlers** (lines 333, 344, 354 — `message_resource.get` blocks). Ember must wrap third-party sync SDK calls in `asyncio.to_thread` or refuse the SDK. (2) The **private-method reach** into `ws._connect`, `ws._ping_loop`, etc. (lines 140, 145, 162). If the public SDK doesn't expose what you need, either fork the SDK or wrap a lower-level transport — don't depend on private API. (3) The **bare `except: break`** at line 165. Ember's connection loops must catch specific exceptions, log the type and message, and decide reconnect-or-give-up based on the exception, not a blanket break.

**Invent:** A pattern SAP did not implement — **content-form negotiation**. When Ember has a multi-modal output (text + image + audio), the platform adapter consults a `surface_capabilities` table for the target platform and decides: (a) send each as separate messages, (b) send as a single rich-format container if the platform supports it (Feishu post, Slack blocks, Discord embed), (c) fall back to text-with-link if no rich support exists. The agent always emits the same `Content` graph; the adapter knows the local shape. Bind to a True-Name candidate: `Sniðmót` (Old Norse for "shape-mold") — the per-surface content negotiator.

Forward-links: see [[35_IM_BOT_DEPLOYMENT_OVERVIEW]] for cross-platform shape, [[26_IM_BOT_INTERFACE]] for the abstraction analysis (where Feishu's content-richness is the most demanding case), [[2A_VOICE_INTERFACE]] for the Omni audio path's voice integration, and [[14_MESSAGING_DOMAIN]] for placement.

The forge is hot. Feishu is feature-dense and Asia-corporate-pragmatic — adopt the task triad, the multi-modal output, and the Omni path. Reject the private-SDK-reach, the sync-in-async, and the bare except. Build the typed content adapter that makes 8-bot platform-specific code unnecessary. — Eldra.

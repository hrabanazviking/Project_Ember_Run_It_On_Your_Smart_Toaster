# 35a — IM Bot: QQ (Tencent's Cathedral with the Side Door Half Open)

> *Eldra at the anvil. QQ is webhook-shaped on the surface, gated by Tencent appid/secret underneath, and the SDK politely lies about both.*

QQ is the first IM platform SAP supports and the one whose deployment shape most reveals the project's accidental architecture. The bot lives in `/tmp/super-agent-party/py/qq_bot_manager.py` (620 lines), wraps Tencent's official `botpy` library, and threads its event loop into a daemon Python thread that the main FastAPI server can summon and kill at will. This subdoc names what QQ actually demands of a host process, how SAP's interrupt-and-replace conversation model works, and what Ember must not inherit when it eventually reaches into China-Web.

## Platform Shape

QQ is **bot account, dual-mode, OAuth-token-shaped**. The `botpy.Client` opens a long-lived WebSocket gateway to Tencent (`qq_bot_manager.py:202` `await super().start(appid=appid, secret=secret)`) after authenticating with an `appid` + `secret` pair issued by Tencent's QQ Open Platform. There is no webhook. There is no polling. The bot lives or dies by whether the gateway connection holds.

Tencent enforces two distinct surfaces:

- **C2C (Customer-to-Customer)** — private 1:1 messages. Handler: `on_c2c_message_create` at `qq_bot_manager.py:224`.
- **Group @-mention** — the bot only sees group messages addressed with `@bot`. Handler: `on_group_at_message_create` at `qq_bot_manager.py:379`.

This is China-platform behavior: groups are not free-listening territory. The intent flag the client opens with is the giveaway — `botpy.Intents(public_messages=True)` at line 89. Public messages only. No CHANGE_ROOM probing. No raw event stream.

There is also a **sandbox toggle** (`config.is_sandbox` at line 89). Tencent runs a parallel test environment with relaxed rate limits and separate appid pairing; SAP exposes it as a per-bot config flag. Useful pattern; trivial to copy.

## Source Files

- `qq_bot_manager.py:23–31` — `QQBotConfig` Pydantic schema
- `qq_bot_manager.py:33–181` — `QQBotManager` (lifecycle: start/stop, thread + event-set handshake)
- `qq_bot_manager.py:183–222` — `MyClient` class extending `botpy.Client`; ready handshake at line 216
- `qq_bot_manager.py:224–377` — C2C (private message) handler + processing
- `qq_bot_manager.py:379–526` — group @-mention handler + processing
- `qq_bot_manager.py:530–616` — image extraction, text cleaning, message sending

## Connection Lifecycle

The startup choreography uses **three `threading.Event` handshakes** to bridge the sync FastAPI caller and the async bot thread. Read `qq_bot_manager.py:56–78`:

```python
# qq_bot_manager.py:56–78
self.bot_thread = threading.Thread(
    target=self._run_bot_thread,
    args=(config,),
    daemon=True,
    name="QQBotThread"
)
self.bot_thread.start()

if not self._startup_complete.wait(timeout=30):
    self.stop_bot()
    raise Exception("机器人连接超时")

if self._startup_error:
    self.stop_bot()
    raise Exception(f"机器人启动失败: {self._startup_error}")

if not self._ready_complete.wait(timeout=30):
    self.stop_bot()
    raise Exception("机器人就绪超时，请检查网络连接和配置")
```

Three events: `_startup_complete`, `_startup_error`, `_ready_complete`. Two timeouts of 30 seconds each. The startup is "complete" once the WebSocket task has been alive for 2 seconds (`delayed_connection_check` at line 114 — `await asyncio.sleep(2)`). The "ready" state requires Tencent's gateway to fire `on_ready` at line 216.

This is **defensive by paranoia, not design**. The 2-second sleep is a magic-number patch. A flapping connection that holds for 2 seconds and dies at second 3 will mark `startup_complete=True`, then mark `ready_complete=True` via the finally block (line 131), and `start_bot()` will return success on a corpse. Hjarta should not inherit this.

Shutdown is more honest (`stop_bot()` at line 159): set shutdown event, mark not running, call `loop.call_soon_threadsafe(loop.stop)`, then `thread.join(timeout=10)`. The 10-second timeout is the only ceiling on how long a stuck QQ bot can hold an Ember teardown hostage.

## Message Handling

The most distinctive QQ pattern is **per-session task interruption**. Both C2C and Group handlers maintain `self.active_tasks: Dict[str, asyncio.Task]`. When a new message arrives, the handler cancels the prior task for that session before spawning a new one. From `qq_bot_manager.py:246–252`:

```python
# qq_bot_manager.py:246–252
# 2. 如果当前用户有任务在跑，直接打断
if c_id in self.active_tasks:
    self.active_tasks[c_id].cancel()
    logging.info(f"用户 {c_id} 发送新消息，打断旧任务")

# 3. 创建新任务
new_task = asyncio.create_task(self._process_c2c_logic(message))
self.active_tasks[c_id] = new_task
```

Two slash commands honor this surface explicitly: `/停止` / `/stop` cancels the current task without starting a new one (lines 232–236); `/重启` / `/restart` cancels and clears the per-session memory list (lines 238–243). This is a small but real UX win — a long LLM stream can be aborted by the user typing one more message instead of waiting.

The inbound parse handles **inline images** (downloaded from Tencent's CDN, transcoded to JPEG if needed, base64-embedded into the OpenAI message — lines 272–291). The text content is preserved alongside as `message.content + "图片链接：" + json.dumps(image_url_list)` (line 294) — the model gets both the inlined image bytes and a record of the original URLs.

LLM call goes back to SAP's own OpenAI-compatible loopback at `http://127.0.0.1:{port}/v1` (line 265) — the bot uses the same server it lives inside as its inference endpoint. This is internal-API discipline; the bot doesn't know which model is configured, it just knows the model alias and posts to localhost.

Outbound is **streaming-with-separators**. As the LLM stream comes in, the bot accumulates a `text_buffer`. The `separators` list (e.g. `["。", "？", "！"]`) is scanned for any character in it (lines 347–358); when one is found, the prefix is cleaned and sent as a message chunk. This is QQ-shaped behavior — Tencent's `post_c2c_message` is per-call billed against the message-sequence counter (`msg_seq_counters` at line 547), so chunked sends consume sequence numbers but stay under per-call size limits.

Images extracted from the LLM's Markdown output (`!\[...\]\(url\)` regex at line 535) are downloaded, uploaded via `post_c2c_file` (line 558), then sent as `msg_type=7` (media message). Tencent requires media to be **uploaded first, then referenced** — there is no inline-image sending in groups.

## Failure Modes

- **Auth expiry** — `appid`/`secret` are long-lived but revocable from the QQ Open Platform console. SAP catches this as `Exception(f"认证失败或配置错误: {e}")` at line 206 and surfaces it through `_startup_error`. There is no token refresh because there is no token to refresh — the secret is the secret.
- **Sandbox vs production confusion** — wrong `is_sandbox` flag connects to the wrong gateway. Gateway accepts the connection then drops it post-auth. SAP has no diagnostic for this; the user sees "机器人启动失败" with whatever botpy chose to say.
- **MSG_SEQ collision** — `msg_seq_counters[c_id]` is incremented after each `post_c2c_message`. If two concurrent handlers race against the same session (which shouldn't happen due to the cancel-then-spawn pattern, but could during a startup-time window), Tencent rejects the duplicate seq and the user sees nothing. The retry has to come from the user.
- **Image URL probe failure** — line 557 does `requests.get(url, timeout=5)` *synchronously* inside an async context just to validate that the URL responds. This blocks the event loop for up to 5 seconds per image. On a slow CDN this is a multi-image throughput killer.
- **Group @-mention ambiguity** — `message.content` includes the `@bot ` prefix. SAP does not strip it; the model gets the @-mention as part of its input. Subtle but consistent leak.
- **No reconnect policy** — botpy handles WebSocket reconnect internally with its own logic. SAP exposes no knob for it. If Tencent puts the gateway in a maintenance window, the bot will reconnect or it will die — SAP does not get to choose.

## Privacy & Threat Surface

QQ is **Tencent-owned and PRC-jurisdictional**. Every message routed through the bot transits Tencent's infrastructure. Every image is downloaded from Tencent's CDN onto the SAP host (`async with session.get(attachment.url)` at line 277) — including images the user may have intended to share only with the bot account. Tencent's logs see the bot's outbound replies in full.

The bot also exposes the host through two side channels worth naming:

1. **`asyncToolsID` and `fileLinks` per-session caches** — `self.asyncToolsID[c_id]` and `self.fileLinks[c_id]` (lines 309, 333). These are tool-execution traces piggybacked into the OpenAI streaming response and accumulated per QQ user-openid. The OpenAI extra_body passes them back on the next call. A compromised QQ session continues to receive every tool link the assistant has emitted during the conversation.
2. **`processing_states` dict keyed by user-openid** — line 303. Buffer state with raw text and image cache. If the bot crashes and dumps memory, every active conversation's in-flight content is in the dump.

Long-term memory is held in `self.memoryList[c_id]` (line 298) and trimmed only on size, never on time or consent. There is no "forget me" command. A user who once chatted with the bot has their conversation history in process memory for as long as the bot runs.

## What This Means for Ember

**Adopt:** The per-session `active_tasks` cancel-and-replace pattern at `qq_bot_manager.py:246–252`. This is the right interaction model for any conversational surface — when the user sends a new message, the prior generation is no longer wanted, and Ember should treat the new message as an interrupt signal, not a queued follow-up. Munnr (mouth) should own this contract across all IM surfaces, not duplicate it per-platform.

**Adapt:** The three-event startup handshake (`_startup_complete` / `_startup_error` / `_ready_complete`). The intent is right — fail loudly with diagnostics rather than silently — but the implementation lies (`asyncio.sleep(2)` as "connection healthy" proxy). Ember's version should require an **actual ping-pong** from the platform gateway before marking `ready=True`, and should never use a fixed sleep as a heuristic for liveness. Bind this contract to a True-Name candidate: `Reiðir` (Old Norse for "rider" — the connection that carries us between the bot host and the platform).

**Avoid:** Three concrete patterns. (1) The synchronous `requests.get(url, timeout=5)` on line 557 inside an async coroutine — a blocking call masquerading as defensive programming. Ember must never block the event loop to probe an image URL; if the URL is bad, the upload will fail, and the failure path should handle it. (2) The `self.memoryList[c_id]` per-session conversation cache with no TTL, no consent, no eviction beyond size. This violates the **Cache Discipline** vow proposed in the Hermes Codex. (3) The China-platform-by-default deployment shape. Ember's IM surface must not ship `qq_bot_manager.py` as a default-enabled module. The platform must be **opt-in with explicit jurisdictional warning**.

**Invent:** A pattern SAP did not implement — **per-platform threat-tier annotation**. Each IM-bot deployment in Ember should carry a manifest entry declaring the jurisdictional surface it touches (`jurisdiction: cn-tencent`, `data_residency: tencent-mainland`, `surveillance_class: state-accessible`) and Hjarta's startup ritual should refuse to start a bot whose jurisdictional tier exceeds the user's declared comfort threshold. The bot doesn't lie about where it lives. The host doesn't pretend not to know.

Forward-links: see [[35_IM_BOT_DEPLOYMENT_OVERVIEW]] for the unified deployment shape across the eight platforms, [[26_IM_BOT_INTERFACE]] for the cross-platform abstraction analysis, [[14_MESSAGING_DOMAIN]] for the macro-domain placement, and [[56_PRIVACY_BOUNDARIES]] for the jurisdictional catalog this subdoc feeds.

The forge is hot. QQ teaches you that "deployment" is not "code that runs" — it is "code that runs *under someone else's gateway*." Inherit the cancel-and-replace pattern. Reject the dishonest readiness handshake. Build the manifest. — Eldra.

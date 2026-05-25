# 35e — IM Bot: DingTalk (Alibaba-Corporate, Stream-Mode, Token-Refresh Required)

> *Eldra at the anvil. DingTalk is the Alibaba enterprise surface — separate access token, separate proactive endpoint, separate group/personal API split. Half-built, but the half that's there is tidy.*

DingTalk (钉钉) is Alibaba's enterprise-IM, sitting alongside WeCom and Feishu in the China-corporate triad. The bot at `/tmp/super-agent-party/py/dingtalk_bot_manager.py` (348 lines) wraps Alibaba's `dingtalk_stream` SDK and adds a token-refresh dance for proactive push that the other Chinese platforms hide. It is the smallest of the three corporate-China implementations and the most missing-pieces.

## Platform Shape

DingTalk is **bot account, enterprise-tenanted, stream-mode-WebSocket-for-receive, REST-with-OAuth-token-for-proactive-send**. Authentication uses `appKey` + `appSecret` (lines 26–28). The stream-mode WebSocket is opened via `DingTalkStreamClient(credential).start()` (line 80), and inbound messages route through `ChatbotHandler.process` (line 126).

The split-architecture is distinctive: **inbound is stream, outbound is dual**. For replies to user messages, the handler's `reply_text` / `reply_markdown` methods handle the wire format. For proactive push (behavior engine), SAP must call a separate Alibaba REST endpoint with a freshly-fetched OAuth token (line 297 `_get_access_token`).

```python
# dingtalk_bot_manager.py:296–305
async def _get_access_token(self) -> Optional[str]:
    url = "https://api.dingtalk.com/v1.0/oauth2/accessToken"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={"appKey": self.config.appKey, "appSecret": self.config.appSecret}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("accessToken")
    except: pass
    return None
```

Every proactive push gets a fresh token. There is no caching, no refresh-on-expiry, no token reuse across messages. This is **deliberately conservative** — DingTalk tokens are short-lived (~2 hours) and revocation propagation is unpredictable, so SAP just fetches a new one each time. Wasteful but reliable.

## Source Files

- `dingtalk_bot_manager.py:25–36` — `DingtalkBotConfig` Pydantic schema
- `dingtalk_bot_manager.py:38–119` — `DingtalkBotManager` lifecycle (lightest of the eight)
- `dingtalk_bot_manager.py:121–132` — `DingtalkInternalHandler`: ChatbotHandler.process bridge
- `dingtalk_bot_manager.py:134–348` — `DingtalkClientLogic`: message dispatch, AI loop, proactive push
- `dingtalk_bot_manager.py:155–203` — `on_message`: cancel-and-replace task dispatch
- `dingtalk_bot_manager.py:307–344` — `execute_behavior_event`: token-fetch-then-push for proactive

## Connection Lifecycle

The simplest of the eight (lines 57–95). One async `main_loop()` coroutine starts the behavior engine and the DingTalk client concurrently via `asyncio.gather` and lets them race:

```python
# dingtalk_bot_manager.py:78–82
await asyncio.gather(
    global_behavior_engine.start(),
    self.client.start()
)
```

`start_bot` doesn't wait for any readiness event — it just sets `is_running = True` (line 54) immediately after spawning the thread. The startup is **optimistic**: if the SDK's `start()` raises, the `except Exception as e` at line 83 catches it and sets `_startup_error`, but by then `start_bot()` has already returned to the caller saying success.

This is a regression from QQ's three-event handshake (which over-promised) and WeCom's connect-then-signal pattern (which is honest). DingTalk's version is "set the flag and pray." The caller has no way to know the bot is actually receiving messages until the first inbound triggers `process()`.

Shutdown (`stop_bot` at line 97): `self.client.stop()`, cancel all active conversation tasks, `self.is_running = False`. No thread.join. The thread is daemon (line 52) so it dies with the process.

## Message Handling

The cancel-and-replace pattern at lines 188–203 is identical to the other Chinese bots. Slash commands (`/停止`, `/重启`) at lines 172–186 are honored.

Inbound parses three message types (lines 213–235):

1. **text** — straight extraction
2. **picture** — `image_content.download_code` is converted to a URL via `handler.get_image_download_url(download_code)` (line 218), then SAP fetches and base64-encodes (line 220 `_get_image_base64`)
3. **richText** — paragraphs of mixed text + image elements. SAP walks the `rich_text_list` for both `text` and `downloadCode` keys (lines 227–235)

The `/id` command (line 241) is more elaborate than other platforms: it differentiates **group** (`cid.startswith("cid")`) from **personal** chats and returns different info. The `cid` prefix is DingTalk's namespacing convention — group conversation IDs start with `cid`, while personal user IDs do not.

Outbound is via `handler.reply_markdown("AI 助手", text, incoming_message)` (line 282) — the title "AI 助手" ("AI Assistant") is **hardcoded**. Every DingTalk reply is labeled "AI 助手" in the message card. This is a violation of the RULES.AI prohibition on hardcoded values (the title should come from config).

The streaming pattern is different from WeCom — DingTalk doesn't have a stream-update primitive, so SAP chunks by separator like QQ:

```python
# dingtalk_bot_manager.py:279–286
if any(sep in state["text_buffer"] for sep in self.separators):
    if state["text_buffer"].strip():
        handler.reply_markdown("AI 助手", state["text_buffer"], incoming_message)
        state["text_buffer"] = ""

if state["text_buffer"].strip():
    handler.reply_markdown("AI 助手", state["text_buffer"], incoming_message)
```

Each separator hit produces a new message card. A long LLM stream becomes a flurry of small markdown cards. Acceptable on desktop, ugly on mobile.

The proactive-push path (`execute_behavior_event` at line 307) is where DingTalk's REST split shows up. After generating a reply from the LLM, it:

1. Calls `_get_access_token()` (line 327) — fresh token every time
2. Branches by target type: `cid.startswith("cid")` means group → `groupMessages/send`, else personal → `oToMessages/batchSend`
3. POSTs the message with `robotCode: self.config.appKey` as the bot identity claim

The `msgKey: "sampleMarkdown"` and `msgParam: json.dumps({"title": "AI 助手", "text": reply})` are templated card formats — DingTalk requires structured message keys, not freeform content. Hardcoded title here too.

## Failure Modes

- **No reply backpressure** — separator-chunked replies post sequentially. If DingTalk rate-limits, SAP keeps posting. The error response is silently swallowed (`handler.reply_markdown` has no return-value check). The user sees a stuttering reply with gaps.
- **Token fetch on every proactive push** — line 327. Fine for low-volume, expensive for high-volume. No retry on token-fetch failure beyond the catch-all `except` at line 304.
- **Hardcoded `"AI 助手"` title** — five places (lines 244, 282, 286, 333, 336). Not configurable.
- **`raw_data.get("senderStaffId")`** at line 242 — accessing the raw dict directly. If DingTalk's wire format changes the key name, this returns None silently and the `/id` command misreports.
- **`richText` parsing assumes 2-level depth** (line 228). Deeper nesting loses content.
- **No `is_running = False` until thread exit** — line 87 sets it in the `finally`, but `stop_bot` (line 105) sets it earlier. There's a window where the bot is "running" but the thread has died.
- **Behavior engine target_ids default to empty** (line 64 `target_ids = config.behaviorTargetChatIds or []`) — but the engine still starts. An engine with no targets is dead weight until configured.
- **`reply_markdown` is synchronous SDK call** — `handler.reply_markdown` is invoked inside async coroutines without `to_thread`. Same blocking issue as Feishu's `message_resource.get`. The SDK's HTTP call may block the event loop briefly.

## Privacy & Threat Surface

DingTalk is **Alibaba-owned, PRC-jurisdictional**, with the same Cybersecurity Law exposure as the other Chinese platforms. Specific concerns:

- **Enterprise admin can audit all bot activity.** Same as WeCom/Feishu.
- **`senderStaffId`** (line 242) is **internal HR identifier**. Behavior engine targets at this granularity could be used for employee tracking by a malicious admin.
- **`robotCode` collision risk** (line 333) — `robotCode: self.config.appKey` claims this bot's identity. If a different bot's appKey leaked, an attacker could send messages claiming to be this bot.
- **Token-fetch-every-time** is **less safe than caching with rotation**, despite intent. Each token fetch is one more network call exposed to MITM. Caching with rotation reduces exposure.

## What This Means for Ember

**Adopt:** The **dual-path send architecture** at the conceptual level — inbound and outbound through different SDK surfaces is honest when the platform's API genuinely splits this way. DingTalk's `reply_*` (for in-context responses) and REST API (for proactive push) are not redundant; they reflect platform behaviors. Ember's Munnr should allow per-platform adapters to declare **reply** vs **initiate** as distinct operations and route accordingly.

**Adapt:** The fresh-token-per-proactive-push pattern. The intent (don't risk a stale token) is right, but the implementation (no caching at all) is wasteful. Ember should adopt a **token cache with eager rotation**: cache the token, refresh when 80% of TTL elapsed, retry on 401 by force-refresh-and-redo. Bind to a True-Name candidate: `Lykill` (Old Norse for "key") — the auth-token surface.

**Avoid:** Four patterns. (1) The **hardcoded `"AI 助手"` title** (5 places). This violates RULES.AI's anti-hardcoding rule. Every label, every prefix, every system string belongs in config. (2) The **set-flag-and-pray startup** at line 54 — `is_running = True` immediately after spawning the thread. Ember must wait for a real readiness signal. (3) The **bare `except: pass`** at line 304 in `_get_access_token`. Token-fetch failure must be surfaced to the caller, not swallowed. (4) **`raw_data.get("senderStaffId")`** — internal Alibaba HR identifier — being passed back to the LLM in /id replies (line 244). Ember must never expose internal enterprise identifiers in user-visible bot replies without explicit user request.

**Invent:** A pattern SAP did not implement — **token observatory**. Ember tracks every auth token's age, source, scope, and last-use across all platforms in a single observable surface. The user can see at a glance: "DingTalk token: 47 min old, expires 2h, used 3 times in last hour" — across every IM platform simultaneously. This is the **operator visibility** missing from SAP, where token lifecycles are scattered across 8 manager modules with no unified view. Bind to `Vörðr` (Old Norse for "watcher/guardian") — Hjarta's auth-state observability surface.

Forward-links: see [[35_IM_BOT_DEPLOYMENT_OVERVIEW]] for cross-platform deployment, [[26_IM_BOT_INTERFACE]] for unified abstraction, [[35c_IM_WECOM_BOT]] and [[35d_IM_FEISHU_BOT]] for the other two China-corporate platforms (the comparison is illuminating), and [[56_PRIVACY_BOUNDARIES]] for the China-platform catalog.

The forge is hot. DingTalk shows you that even Chinese-corporate platforms differ — Alibaba's split-API model is honest about a real split. Inherit the dual-path concept. Reject the hardcoded titles and the optimistic startup. Build the token observatory. — Eldra.

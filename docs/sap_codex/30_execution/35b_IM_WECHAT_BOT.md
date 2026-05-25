# 35b — IM Bot: WeChat (The Personal Account That Should Not Exist)

> *Eldra at the anvil. WeChat personal-account automation is platform jiu-jitsu: an unofficial SDK pretending to be a human pretending to be a Mac, sniffing stdout for QR codes, hoping nobody at Tencent is watching too hard.*

WeChat is the most legally and ethically fraught of the eight IM deployments. The bot at `/tmp/super-agent-party/py/wechat_bot_manager.py` (484 lines) drives **personal WeChat accounts** — not WeChat official accounts, not WeChat work, but the same WeChat the user uses with their family — via the third-party `wechatbot-sdk` (`pip install wechatbot-sdk`, imported at lines 24–30). Tencent does not sanction this. WeChat's Terms of Service forbid it. SAP ships it anyway, behind one `try/except ImportError`. This subdoc names what the deployment actually does, why it works, and why Ember must not adopt this surface uncritically.

## Platform Shape

WeChat personal account is **client-side, headless-browser/Electron-simulated, QR-login-bound, ToS-violating**. There is no bot API. There is no webhook. There is no appid pair. The SDK opens an embedded WeChat client (the SDK essentially screen-scrapes a Mac/Windows WeChat instance) and proxies messages through the personal account's session.

Login happens by **QR code captured from stdout**. Read `wechat_bot_manager.py:33–63`:

```python
# wechat_bot_manager.py:33–57
class StreamInterceptor:
    def __init__(self, original_stream, qr_callback, success_callback):
        self.original_stream = original_stream
        self.qr_callback = qr_callback
        self.success_callback = success_callback
        self.buffer = ""

    def write(self, text):
        self.original_stream.write(text)
        try:
            self.buffer += str(text)
            if "liteapp.weixin.qq.com/q/" in self.buffer:
                match = re.search(r'(https://liteapp\.weixin\.qq\.com/q/[a-zA-Z0-9_?=&]+)', self.buffer)
                if match:
                    self.qr_callback(match.group(1))
                    self.buffer = self.buffer.replace(match.group(0), "")
            
            lower_buf = self.buffer.lower()
            success_keywords =["login successfully", "log in successfully", "logged in as", "登录成功", "wechat login succeed"]
            if any(kw in lower_buf for kw in success_keywords):
                self.success_callback()
                self.buffer = ""
```

SAP **monkey-patches sys.stdout and sys.stderr** (line 190) to intercept the SDK's own log output, parses the QR code URL with a regex, and renders it as a base64 PNG (lines 175–183) for the user to scan with their phone's WeChat app. There is no API for this. There is no callback hook from the SDK. SAP scrapes the SDK's stdout for a URL pattern because that is the only available signal.

If this sounds fragile, it is exactly that fragile. An SDK update that changes the log message format breaks the bot. SAP defends with an `importlib.reload(wechatbot)` on `force_relogin` (line 134) — the user can manually nuke the cache (line 117 `_clear_wechat_cache`) and ask for a fresh QR.

## Source Files

- `wechat_bot_manager.py:33–63` — `StreamInterceptor`: the stdout-sniffing QR extractor
- `wechat_bot_manager.py:65–75` — `WeChatBotConfig` Pydantic schema (note `force_relogin: bool` and `wakeWord: str`)
- `wechat_bot_manager.py:77–230` — `WeChatBotManager` lifecycle + behavior-engine integration
- `wechat_bot_manager.py:117–125` — `_clear_wechat_cache`: nukes `~/.wechatbot`, `session/`, `*.pkl`
- `wechat_bot_manager.py:232–484` — `WeChatClient`: per-chat-id task tracking, AI loop, behavior engine

## Connection Lifecycle

A `WeChatBot()` instance is constructed (line 136), the `@bot.on_message` decorator wires `handle_message_wrapper` (line 155), then `bot.run()` is dispatched into `asyncio.to_thread` (line 197) because the SDK is synchronous.

The startup acknowledgment is minimum-effort: `self._startup_complete.set()` is fired immediately at line 169, *before* the WebSocket is verified, because the SDK's WebSocket is internal and not exposed. SAP cannot wait for it; it can only wait for either a QR URL to appear in stdout or for the login-success string to appear in stdout. The 30-second `_startup_complete.wait(timeout=30)` at line 110 is therefore not a connection check — it is a "process started" check.

Crucially, on first launch the user **must scan a QR code with their phone within the window between QR-render and SDK timeout**. Re-login persists in `~/.wechatbot/` and `session/` via pickle files (line 123 — `glob.glob("*.pkl")`). The `force_relogin` flag triggers `_clear_wechat_cache` which `shutil.rmtree(d, ignore_errors=True)`s these dirs (line 122) — destructive without confirmation.

Behavior engine integration is hot-loaded in the same thread context (lines 147–153). The `global_behavior_engine` proactively pushes prompts at idle WeChat sessions (`execute_behavior_event` at line 409). The bot does not wait to be spoken to; it speaks first.

## Message Handling

Inbound messages route through `handle_message` at line 251. It is deliberately non-blocking — the docstring says so explicitly:
> "非阻塞消息入口：快速返回，让后续消息能立即处理"
> ("Non-blocking message entry — return quickly so subsequent messages can be processed immediately.")

The same cancel-and-replace task pattern as QQ (line 288 `self.active_tasks[chat_id].cancel()`), but with a critical difference at line 296: the handler **does not await the new task**. It fires `asyncio.create_task(...)` and returns. A `done_callback` cleans up the `active_tasks` dict (line 295). This makes the WeChat handler **fully non-blocking on the inbound path**, where QQ's `await new_task` (line 255) at least keeps the prior handler running until the LLM stream finishes.

Why the difference? Because the SDK's `bot.run()` is on a thread, and the inbound message arrives via `@bot.on_message` callback. Blocking inside that callback could hang the WeChat client itself. SAP's WeChat handler must return in milliseconds or break the SDK.

Three slash commands: `/停止`, `/重启`, `/id`. The first two follow the QQ pattern. `/id` (line 283) returns the WeChat user_id back to the user — useful for the behavior-engine target list, where the user must supply chat_ids by hand.

Outbound is straightforward: `self.bot.reply(msg, text)` for text (line 407), `self.bot.send_media(target_id, content_dict)` for images (line 395). The SDK abstracts WeChat's actual multipart upload flow.

The TTS path (`_send_voice` at line 460) is special: the bot calls SAP's internal `/tts` endpoint, gets back MP3 bytes, then passes them as `send_media` — the SDK handles the conversion to WeChat's `.amr` voice format internally. The audio is fire-and-forget; failure is logged but never recovered.

The **behavior engine path** (`execute_behavior_event` at line 409) is the dangerous part. It dispatches AI-generated prompts proactively to chat_ids the user has registered as "behavior targets." Line 413 checks `if not self.bot._context_tokens.get(target_id): return` — a hidden guard that the target's session is still valid. There is no consent check. There is no rate limit visible at this layer. If the user configures the behavior engine aggressively, their WeChat will message contacts who never agreed to be subjects of automated outreach.

## Failure Modes

- **Tencent ban** — WeChat detects automation by traffic fingerprinting and locks accounts. The user loses access to their personal WeChat. There is no recovery path SAP can offer. This is **the primary failure mode** and SAP does not mention it in code comments.
- **SDK log format change** — `StreamInterceptor` greps stdout. An SDK version that changes its log output silently breaks QR extraction. The bot will report "no QR available" without explaining why.
- **Session pickle corruption** — `*.pkl` files in cwd. A non-graceful shutdown can corrupt the session pickle. Next start fails to deserialize. The user has to manually `_clear_wechat_cache` and re-scan.
- **importlib.reload bombshell** — line 134, `importlib.reload(wechatbot)` on force_relogin. Reloading a module mid-process with active references is undefined behavior in Python. SAP gets away with it because the prior bot instance is being torn down anyway, but it's not safe.
- **`sys.stdout = StreamInterceptor(...)`** — line 190 — globally replaces stdout. If anything else in the SAP process (logging, debug prints, other bots) writes to stdout simultaneously, the buffer becomes a hot mess. The interceptor's 1000-character ring buffer (line 55) is the only mitigation.
- **CJK regex on lowercased buffer** — line 50 `lower_buf = self.buffer.lower()`, then checks for both English and Chinese success strings. Chinese characters don't have case so this works, but it's accident-grade, not design-grade.

## Privacy & Threat Surface

This is the worst-surface platform in SAP. Listing what the deployment exposes:

- **The user's full personal WeChat session.** Every contact's message history is reachable through the SDK. The bot can read messages from anyone in the user's contact list, not just those who have consented to chatting with the bot.
- **The behavior engine can initiate conversations.** If the user adds `behaviorTargetChatIds`, the bot will send AI-generated messages to those chats unprompted (line 442). The recipient has no way to know it's a bot.
- **Tencent sees all of it.** Every message routed through personal WeChat is logged by Tencent and accessible to PRC law enforcement under the Cybersecurity Law (2017) and Data Security Law (2021). No technical mitigation possible.
- **Cache files in cwd.** Session pickles (`*.pkl`), `.wechatbot/` directory in user's home. Any user-level malware on the machine can steal the WeChat session and impersonate the user.
- **TLS-fingerprint risk.** WeChat does TLS-fingerprint detection. The SDK's fingerprint may differ from official WeChat clients, increasing detection risk.

## What This Means for Ember

**Adopt:** The non-blocking inbound dispatch pattern at `wechat_bot_manager.py:292–296`. `asyncio.create_task(...)` without `await`, with a `done_callback` for cleanup, is the correct shape when the inbound callback path must not block. Ember's IM-bot supervisor (Munnr) should adopt this contract for **any platform whose SDK invokes a sync callback from a thread we don't own**. The pattern needs naming. Propose: `Augnablik` (Old Norse for "blink") — the moment-and-released dispatch.

**Adapt:** The QR-from-stdout pattern is too fragile to inherit directly, but the **idea** is right — when a third-party SDK does not expose a callback hook for an event we need, intercept its output stream. Ember should adapt this with: (1) a typed protocol over the captured stream (regex matchers registered, not literal substring search), (2) automatic restoration of `sys.stdout` in a `finally` block (SAP only restores on `_async_run_websocket` cleanup at line 200 — if anything crashes elsewhere, stdout stays redirected). Name this pattern `Hlustarinn` (the listener-on-the-pipe).

**Avoid:** Four loud rejections. (1) **Personal-account WeChat automation must not ship in Ember at all.** It violates Tencent ToS, exposes the user to account loss, and routes through PRC jurisdiction. If China-Web reach is required, ship WeCom (`wecom_bot_manager.py`) instead — it is the sanctioned surface. (2) `importlib.reload(wechatbot)` mid-process (line 134) — the reload-as-recovery pattern. Reloading a stateful third-party module while it has active references is undefined behavior. Ember must teardown-and-respawn the full subprocess instead. (3) The proactive `execute_behavior_event` shape with no recipient consent (line 442). Hjarta should refuse to initiate outbound IM contact to chat_ids that have not explicitly opted in within the last N days (the **Affective Restraint** vow). (4) The `_clear_wechat_cache` destructive `rmtree` (line 122) — SAP nukes user-level state without confirmation. Ember must require explicit user gesture for any destructive cleanup.

**Invent:** A pattern SAP did not implement — **consented-recipient ledger for proactive IM**. When the behavior engine wants to message a chat_id, it consults a per-recipient consent ledger: did this recipient receive a bot message within the last 24 hours? Have they replied? If they have not replied to the last N proactive messages, mark them "non-consenting" and stop. This pattern emerges naturally from analyzing SAP's behavior engine across all 8 IM platforms — it is the missing safeguard that should not be per-platform. Bind it to a new module proposal: `Samþykki` (Old Norse for "consent"), living under Hjarta.

Forward-links: see [[35_IM_BOT_DEPLOYMENT_OVERVIEW]] for cross-platform commonality, [[26_IM_BOT_INTERFACE]] for the unified abstraction analysis, [[35c_IM_WECOM_BOT]] for the sanctioned alternative, [[1A_AFFECTION_DOMAIN]] for the behavior-engine domain, and [[56_PRIVACY_BOUNDARIES]] for the threat-model catalog that this subdoc feeds heavily.

The forge is hot. WeChat personal-account automation is the most ban-prone, most ToS-violating, most jurisdiction-exposed surface SAP ships. Inherit the non-blocking dispatch. Reject the surface itself. Build the consent ledger. — Eldra.

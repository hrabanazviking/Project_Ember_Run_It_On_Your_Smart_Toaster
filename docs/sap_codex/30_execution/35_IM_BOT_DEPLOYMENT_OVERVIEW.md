---
codex_id: 35_IM_BOT_DEPLOYMENT_OVERVIEW
title: IM Bot Deployment Overview — Eight Platforms, One Pattern, One Bug Surface
role: Forge
layer: Execution
status: draft
sap_source_refs:
  - server.py:10430-10847 (BotContainer + 32 routes)
  - py/behavior_engine.py:53-225 (global engine)
  - py/feishu_bot_manager.py:21-100 (config + manager)
  - py/discord_bot_manager.py:22-100 (Discord pattern)
  - py/wechat_bot_manager.py:67-160 (WeChat pattern)
  - py/slack_bot_manager.py:21-100 (Slack pattern)
ember_subsystem_targets: [Munnr, Strengr]
cross_refs:
  - 30_execution/3B_AFFECTION_LOOP
  - 30_execution/35a_IM_QQ_BOT
  - 30_execution/35b_IM_WECHAT_BOT
  - 30_execution/35c_IM_WECOM_BOT
  - 30_execution/35d_IM_FEISHU_BOT
  - 30_execution/35e_IM_DINGTALK_BOT
  - 30_execution/35f_IM_TELEGRAM_BOT
  - 30_execution/35g_IM_DISCORD_BOT
  - 30_execution/35h_IM_SLACK_BOT
  - 20_interface/26_IM_BOT_INTERFACE
---

# IM Bot Deployment Overview

> *Eight bot managers. One global behavior engine. Thirty-two HTTP routes. The same shape repeated eight times — which is either elegance or smell, depending on how forgiving you feel.*

Forge. Eldra. SAP ships connectivity to **eight** IM platforms (QQ, WeChat, Feishu, DingTalk, Telegram, Discord, Slack, WeCom). Each one is its own Python manager module under `py/`. The pattern is nearly identical across all eight. This doc explains the **shared abstraction**: what every IM bot has in common, what is uniquely platform-specific, and where the duplication actually hurts. The Forge-B sibling docs (`35a` through `35h`) handle each platform individually.

## The Shared Skeleton

Every IM bot manager exposes the same outer shape. Here's the contract, distilled from cross-reading all eight:

**1. A Pydantic config class** named `<Platform>BotConfig`:

```python
# py/feishu_bot_manager.py:21-32 (FeishuBotConfig, representative)
class FeishuBotConfig(BaseModel):
    # platform-specific credentials (varies)
    app_id: str
    app_secret: str
    # ... platform-specific fields
    llm_model: str = "super-model"
    memory_limit: int = 10
    separators: List[str]
    reasoning_visible: bool = False
    quick_restart: bool = True
    enable_tts: bool = True
    wakeWord: str
    behaviorSettings: Optional[BehaviorSettings] = None
    behaviorTargetChatIds: List[str] = Field(default_factory=list)
```

The platform-specific fields differ (Discord wants a `token`; Feishu wants `app_id` + `app_secret`; WeChat wants nothing because it uses QR-code login). The rest is **identical across all eight platforms**: `llm_model`, `memory_limit`, `separators`, `wakeWord`, `behaviorSettings`, `behaviorTargetChatIds`.

**2. A Manager class** named `<Platform>BotManager`:

```python
# common shape
class <Platform>BotManager:
    def __init__(self):
        self.bot_thread: Optional[threading.Thread] = None
        self.bot_client: Optional[...] = None
        self.is_running = False
        self.config: Optional[...] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self._shutdown_event = threading.Event()
        self._ready_complete = threading.Event()
        self._startup_error: Optional[str] = None
        self._stop_requested = False

    def start_bot(self, config): ...        # spawns thread, waits for ready
    def stop_bot(self): ...                 # signals shutdown, joins thread
    def get_status(self): ...               # returns is_running + last error
    def _run_bot_thread(self, config): ...  # entry point inside the thread
```

This is **not abstract base class**. There is no `BaseIMManager` in `py/`. The skeleton is replicated by copy-paste-modify across eight files. I checked. Each file is between 137 and 620 lines. Each one has its own `threading.Event` rituals, its own `loop = asyncio.new_event_loop()`, its own `_ready_complete.wait(timeout=30)`. The patterns are identical; the code is not.

**3. A Client class** named `<Platform>Client` (or sometimes embedded in the same file):

The client is what actually talks to the IM platform's SDK. This is where the platforms diverge most — Discord uses `discord.py`, Telegram uses `python-telegram-bot` or `Pyrogram`, Slack uses `slack_bolt`, WeChat uses `itchat` or `wxauto`, QQ uses `botpy`, Feishu uses Lark SDK calls, DingTalk uses its own SDK. The client wraps the SDK and translates events into LLM prompts.

**4. The Behavior Engine Registration**:

```python
# py/feishu_bot_manager.py:245
class FeishuClient:
    def __init__(self, config, manager):
        ...
        global_behavior_engine.register_handler("feishu", self.execute_behavior_event)
```

Every client registers a handler with the **single global `BehaviorEngine` singleton** (`py/behavior_engine.py:225`). The engine fires `execute_behavior_event(chat_id, behavior_item)` callbacks on a schedule defined by user-configurable rules. See [[3B_AFFECTION_LOOP]] for the engine's tick loop.

The shared abstraction is **the BehaviorEngine, not the manager**. Eight bots, one engine, one event-loop registry keyed by platform name.

## The BotContainer Holder

```python
# server.py:10430-10499 (compressed)
class BotContainer:
    """All bot manager instances live here."""
    _qq = None
    _feishu = None
    _dingtalk = None
    _discord = None
    _slack = None
    _telegram = None
    _wecom = None
    _wechat = None

    @classmethod
    def get_qq(cls):
        if cls._qq is None:
            from py.qq_bot_manager import QQBotManager
            cls._qq = QQBotManager()
        return cls._qq

    @classmethod
    def get_feishu(cls):
        if cls._feishu is None:
            from py.feishu_bot_manager import FeishuBotManager
            cls._feishu = FeishuBotManager()
        return cls._feishu
    # ... seven more get_<platform> classmethods
```

A lazy-singleton holder. The `from py.<platform>_bot_manager import ...` is **inside** the classmethod — so importing the manager (and pulling in its 3rd-party SDK: `discord.py`, `slack_bolt`, etc.) is deferred until the user actually starts that bot. Cold start time for SAP is faster because none of the eight SDKs load during module import.

This is a smart trade-off. The cost: every bot's first start has a noticeable lag (~1–3 seconds) as the SDK imports. The benefit: a user who only ever uses Discord doesn't pay the WeChat import cost.

## The Thirty-Two Routes

For each of the eight platforms, `server.py` exposes the same four-route pattern:

```python
# server.py:10502-10542 (QQ example; pattern repeats × 8)
@app.post("/start_qq_bot")
async def start_qq_bot(config_data: dict):
    from py.qq_bot_manager import QQBotConfig
    config = QQBotConfig(**config_data)
    BotContainer.get_qq().start_bot(config)
    return {"success": True, ...}

@app.post("/stop_qq_bot")
async def stop_qq_bot():
    if BotContainer._qq:
        BotContainer.get_qq().stop_bot()
    return {"success": True, ...}

@app.get("/qq_bot_status")
async def qq_bot_status():
    if BotContainer._qq is None:
        return {"is_running": False, "status": "stopped"}
    status = BotContainer.get_qq().get_status()
    if status.get("startup_error") and not status.get("is_running"):
        status["error_message"] = f"启动失败: {status['startup_error']}"
    return status

@app.post("/reload_qq_bot")
async def reload_qq_bot(config_data: dict):
    config = QQBotConfig(**config_data)
    manager = BotContainer.get_qq()
    manager.stop_bot()
    await asyncio.sleep(1)
    manager.start_bot(config)
    return {"success": True, ...}
```

Four routes × 8 platforms = 32 nearly-identical routes. They span `server.py:10502–10847` — about 350 lines that could be eight if SAP had a `IMBotRegistry` that mapped platform names to their config classes and exposed generic routes `/api/im/<platform>/start`, `/stop`, `/status`, `/reload`.

This is the cleanest single example of **duplication-as-tech-debt** in `server.py`. Eight times the maintenance burden, eight times the surface area for typo divergence (e.g. only one of the eight uses `"environment": "thread-based"` in the response, but the others should and don't — a real consistency bug I caught skimming the code).

## The Thread Lifecycle

Every IM bot runs in **its own thread with its own asyncio event loop**:

```python
# py/discord_bot_manager.py:69-103 (representative)
def _run_bot_thread(self, config):
    try:
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        async def main_startup():
            try:
                settings = await load_settings()
                behavior_data = settings.get("behaviorSettings", {})
                target_ids = config.behaviorTargetChatIds or ...

                if behavior_data:
                    global_behavior_engine.update_config(behavior_data, {"discord": target_ids})

                self.bot_client = DiscordClient(config, manager=self)

                if not global_behavior_engine.is_running:
                    asyncio.create_task(global_behavior_engine.start())

                await self.bot_client.start(config.token)
            except Exception as e:
                self._startup_error = str(e)

        self.loop.run_until_complete(main_startup())
    except Exception as e:
        ...
```

Why threads? Because every IM SDK assumes it owns the event loop. `discord.py` wants its own loop. `botpy` (QQ) wants its own. `slack_bolt`'s socket-mode handler is also greedy. The cleanest way to integrate eight loop-owning libraries into one FastAPI server is to give each one its own thread.

Cost: **eight threads** when all bots are running. Each thread has its own asyncio loop, its own ASGI-style task queue, its own connection pool to the IM service. Memory floor goes up. Cross-bot state must go through the main FastAPI process (via `global_behavior_engine`, via shared `settings` dict).

Benefit: **isolation**. If `discord.py` crashes its event loop, QQ stays up. If WeChat's session expires and triggers a re-login flow, Telegram doesn't care.

## The Wake Word Protocol

```python
# py/feishu_bot_manager.py:328 (representative)
if self.wakeWord and self.wakeWord not in user_text: return
```

Every IM bot supports a **wake word**. Messages without the wake word are silently ignored. This is the SAP equivalent of "Hey Siri" — the bot is in every group chat but only responds when explicitly addressed. The pattern is identical across all eight platforms; each client checks for the wake word at the same point in its message handler (`on_message` or equivalent).

Without a wake word, the bot would respond to every message in every group. With one, it can be a passive presence in a group of 200 people. Important for privacy and not-annoying-everyone.

## The behaviorTargetChatIds Pattern

```python
# py/feishu_bot_manager.py:109
global_behavior_engine.update_config(behavior_data, {"feishu": target_ids})
```

The `behaviorTargetChatIds` list tells the behavior engine **which chats** can receive autonomous outbound messages (e.g. scheduled greetings, idle-prompt nudges from `autoBehavior`). A bot might be deployed in a server with 100 channels but configured to autonomously message only 3 of them. The rest see the bot only when invoked.

This is correct privacy hygiene. Outbound autonomous messaging without explicit chat-level opt-in would be spam. SAP gates it.

## What Is Truly Per-Platform (and Why Forge-B Has Eleven Docs)

The shared abstraction goes only so far. Per-platform, the divergence is real:

- **QQ** (`qq_bot_manager.py:33`, 620 lines): uses Tencent's `botpy` SDK; supports group + private messages; has a unique "guild" concept; message types include images, voice clips, files. Heaviest single file in the IM stack.
- **WeChat** (`wechat_bot_manager.py:484` lines): personal-account automation (gray-area; against ToS); QR-code login; supports voice notes that must be converted to Opus format for transit (`convert_to_opus_simple` in `get_setting.py`); session expiration is brutal.
- **WeCom** (`wecom_bot_manager.py:404` lines): Enterprise WeChat; webhook-driven instead of long-poll; corporate compliance constraints.
- **Feishu** (`feishu_bot_manager.py:602` lines): Lark; supports rich card messages; multilingual; the most fully-featured client.
- **DingTalk** (`dingtalk_bot_manager.py:348` lines): Alibaba's enterprise IM; markdown card support; signature-based webhook auth.
- **Telegram** (`telegram_bot_manager.py:137` lines + `telegram_client.py:370` lines): bot vs client API distinction; Bot API for bots-only features; Client API (Pyrogram-style) for user-impersonation features. SAP supports both.
- **Discord** (`discord_bot_manager.py:440` lines): slash commands; voice channel support (in client, not yet wired); embeds; reaction-based interaction.
- **Slack** (`slack_bot_manager.py:349` lines): socket-mode (no public HTTP webhook required); slash commands; threading model is unique.

See Forge-B's per-platform docs: [[35a_IM_QQ_BOT]], [[35b_IM_WECHAT_BOT]], [[35c_IM_WECOM_BOT]], [[35d_IM_FEISHU_BOT]], [[35e_IM_DINGTALK_BOT]], [[35f_IM_TELEGRAM_BOT]], [[35g_IM_DISCORD_BOT]], [[35h_IM_SLACK_BOT]].

## Where It Breaks

- **Eight times the code-path surface**. A bug fix in the wake-word handling has to be applied in eight files. SAP routinely diverges between bots — Discord's wake-word logic is at line 214; Feishu's is at line 328; they differ slightly in how they handle case sensitivity and Unicode normalization. This is the cost of copy-paste.
- **Single global `BehaviorEngine`** (`py/behavior_engine.py:225`): `global_behavior_engine = BehaviorEngine()`. There is **one** engine for all eight bots. If the engine's `_tick()` (line 144) throws an unhandled exception, autonomous behavior stops on **every** platform. There is no isolation here.
- **No per-bot rate limiting**. If the LLM decides to send a 50-message thread to a Discord channel, SAP will dutifully send 50 messages. Discord's rate limiter will then ban the bot for an hour. SAP has no application-level throttle.
- **Eight 3rd-party SDKs** = eight versions, eight upgrade paths, eight CVE surfaces. `pyproject.toml` would tell us the version pins; I didn't audit them. [[54_DEPENDENCY_HEALTH]] (Auditor) is where this gets investigated.
- **WeChat personal-account automation** (`wechat_bot_manager.py`) is gray-area. Tencent actively detects and bans automation on personal accounts. SAP ships it anyway. Users who deploy it risk losing their main WeChat account.
- **Shared `settings` dict mutation**: every IM bot's `start_bot` reads `await load_settings()` and writes `settings["mcpServers"][...]["disabled"] = True` on errors. Multiple bots starting concurrently can race on this dict; SAP has no lock. The race window is small (typically the bots are started sequentially by the user) but it exists.

## Where It Surprises

- **The thread-per-bot isolation** actually works. I expected the eight threads to step on each other; the only shared mutable state is the settings dict and the behavior engine. Both are mediated by the engine's per-platform routing keys. Defensible architecture even if cramped.
- **The wake-word pattern is consistent enough** that a unified IM abstraction would be tractable. SAP didn't build it, but the path is visible.
- **WeChat support exists at all**. The Chinese open-source community routinely ships WeChat automation despite Tencent's hostility. SAP includes it without disclaimer in the README. For a Chinese-developer-targeted tool, this is normal. For Ember (international audience), this would need a "we don't ship Chinese automation that violates ToS" stance documented.
- **The lazy-import in `BotContainer`** means SAP starts in under a second even with eight SDKs available. Without it, cold-start would be 5+ seconds. Small detail, large UX impact.
- **The `behaviorTargetChatIds` per-platform routing** in `BehaviorEngine.update_config()` (line 90) is one of the cleaner parts of SAP. The engine knows which chats on which platforms are opt-in for autonomous behavior. Other systems would have made this implicit; SAP makes it explicit per-chat-id.

## Cross-References

- [[3B_AFFECTION_LOOP]] — the BehaviorEngine that all IM bots register with
- [[35a_IM_QQ_BOT]] through [[35h_IM_SLACK_BOT]] — Forge-B's per-platform deep dives
- [[26_IM_BOT_INTERFACE]] (Auditor) — whether the shared shape constitutes a real interface
- [[14_MESSAGING_DOMAIN]] (Architect) — domain-level view
- [[56_PRIVACY_BOUNDARIES]] — privacy implications of 8 simultaneous bot deployments

## What This Means for Ember

**Adopt:**

- **The wake-word default**. Any IM-bot-like surface Ember exposes must require an explicit wake word (default off, no auto-response in groups). Vow tie-in: **Surface Without Surveillance**.
- **The `behaviorTargetChatIds` opt-in for autonomous outbound**. Ember's autonomous reach (scheduled greetings, idle-triggered messages) must be per-chat opt-in, never bot-wide. Bind to Munnr's reach-layer.
- **The lazy-import `BotContainer` pattern**. Optional subsystems should not pay their import cost until used. Ember should generalize: any subsystem flagged `optional: true` in its manifest must defer import to first-use. Bind to Funi.
- **Thread-per-platform isolation** for any reach subsystem whose SDK owns its own event loop. The cost is real (one thread each); the alternative (asyncio adapters and event-loop bridging) is fragile and bug-prone.

**Adapt:**

- **The 8-Pydantic-config-classes** pattern — replace with **one** typed base class `IMBotConfig` and platform-specific extensions via inheritance. SAP's copy-paste is convenient for editing one platform but a maintenance burden across all. Ember should pay the inheritance cost once.
- **The 32 HTTP routes** — collapse to four generic routes parameterized by platform: `POST /api/im/{platform}/start`, etc. SAP's per-platform routes are a leak of internal naming into the public API; Ember's API should be `/api/im/<platform>/...` with `<platform>` validated against a registry.
- **The `BotContainer` singleton holder** but generalize to `IMBotRegistry` with a `register(name, manager_class, config_class)` API. Adding a new platform = one registration call + one manager file, no edits to the route layer.

**Avoid:**

- **The single global `BehaviorEngine`** with no isolation. Ember's equivalent (call it Hjarta-Reach or similar) must have per-platform error isolation: if Discord's tick throws, Slack's tick doesn't stop.
- **WeChat personal-account automation**. Ember's open-knowledge Vow says we ship MIT-friendly recommendations. ToS-violating SDKs don't fit. If Chinese-platform reach is desired, ship the **WeCom** (enterprise) integration only; recommend users move to it.
- **Copy-paste-modify across eight files**. Vow proposal: **Single-Authoring** — any pattern repeated more than 3 times must move to a base class or registry.
- **No per-bot rate limiting**. Ember's reach layer must have a token-bucket rate limiter per platform, configurable per-deployment. Default: 1 message per 5 seconds per chat, with bursts up to 5.

**Invent:**

- **Munnr Reach Registry**. A typed `ReachAdapter` interface with `start(config) -> Handle`, `send(target, message) -> Result`, `stop(handle) -> None`, and a `events: AsyncIterator[Event]` async generator. Each platform implements one adapter file. The reach layer never touches platform-specific code. Vow tie-in: **Modular Authorship**.
- **Reach Consent Token**. Before Ember sends an autonomous message to a chat, it checks a typed `ConsentToken(chat_id, scopes={"autonomous_msg", "summarize", ...}, expires_at)`. Tokens are issued by the operator and stored in a separate consent database. If no token exists for that chat-id + scope, the message is dropped with an audit-log entry. Vow tie-in: **Surface Without Surveillance**.
- **Federated Bot State**. SAP's `BehaviorEngine` is a singleton. Ember's reach engine should be federation-aware: a Pi-tier Ember can subscribe to a workstation-tier Ember's reach state and act as a fallback when the workstation is offline. The Pi sends a "limited presence" mode message; the workstation handles full conversations when online. Vow tie-in: **Federated Self**.
- **Wake-Word Schema Discovery**. The reach engine reads each adapter's `wake_words` list (which may be platform-specific: in Slack, channels can have channel-specific wake words; in Discord, a slash command counts). The list is exposed in `/api/im/wake_words` for the renderer to display. SAP requires the user to know each platform's wake-word convention; Ember should display it.
- **Cross-Platform Identity Map**. When the same human is on Telegram + Discord + WeChat, Ember should know it's the same human. A separate `IdentityLedger` ([[6A_MULTI_AGENT_PARTY]]) maps platform-user-ids → Ember-identity-id. Affection state ([[3B_AFFECTION_LOOP]]) keys on the Ember-identity-id, not the platform-user-id. SAP keys affection on raw usernames; Ember should normalize.

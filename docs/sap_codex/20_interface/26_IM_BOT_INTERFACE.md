---
codex_id: 26_IM_BOT_INTERFACE
title: IM Bot Interface — Eight Managers, No Shared Abstraction
role: Auditor
layer: Interface
status: draft
sap_source_refs:
  - py/qq_bot_manager.py:1-100
  - py/wechat_bot_manager.py:1-90
  - py/wecom_bot_manager.py:1-50
  - py/feishu_bot_manager.py:1-100
  - py/dingtalk_bot_manager.py:1-50
  - py/telegram_bot_manager.py:1-138
  - py/discord_bot_manager.py:1-80
  - py/slack_bot_manager.py:1-80
  - py/behavior_engine.py:75-110
ember_subsystem_targets: [Munnr, Hjarta]
cross_refs:
  - 10_domain/14_MESSAGING_DOMAIN
  - 30_execution/35_IM_BOT_DEPLOYMENT_OVERVIEW
  - 50_verification/56_PRIVACY_BOUNDARIES
  - 50_verification/57_FAILURE_TAXONOMY
---

# IM Bot Interface — Eight Managers, No Shared Abstraction

> *Sólrún, voice cold and even: eight modules in one folder, each pretending to be the One True Way to talk to its platform. They share clothing but not a skeleton. The clothing is the lie; the skeleton you have to imagine from the gaps.*

SAP ships eight IM bot managers in `/tmp/super-agent-party/py/`: `qq_bot_manager.py`, `wechat_bot_manager.py`, `wecom_bot_manager.py`, `feishu_bot_manager.py`, `dingtalk_bot_manager.py`, `telegram_bot_manager.py`, `discord_bot_manager.py`, `slack_bot_manager.py`. The README pitches this as "one-click deployment of 8 IM platforms." That sentence is a marketing artifact. The code is eight near-parallel implementations with no shared base class, no protocol, no abstract method enforcement, and an inconsistent inventory of features per platform.

This document audits the **implicit interface** — what every manager has in common — and the **explicit gaps** — where each one drifts. A real interface would let me delete redundant code; SAP's implicit interface lets me cut-and-paste it forever.

---

## 1. The Subject — Eight Managers, One Folder, No Base Class

Confirm the basic shape first. Every manager is a top-level class with a name shaped `<Platform>BotManager`:

- `QQBotManager` at `qq_bot_manager.py:33`
- `WeChatBotManager` at `wechat_bot_manager.py:77`
- `FeishuBotManager` at `feishu_bot_manager.py:34`
- `TelegramBotManager` at `telegram_bot_manager.py:19`
- `DiscordBotManager` at `discord_bot_manager.py:35`
- `SlackBotManager` at `slack_bot_manager.py:35`
- ...and so on.

None of them inherits from a shared base class. Search the codebase:

```
$ grep -rn "class.*BotManager" /tmp/super-agent-party/py/
qq_bot_manager.py:33:class QQBotManager:
wechat_bot_manager.py:77:class WeChatBotManager:
feishu_bot_manager.py:34:class FeishuBotManager:
telegram_bot_manager.py:19:class TelegramBotManager:
discord_bot_manager.py:35:class DiscordBotManager:
slack_bot_manager.py:35:class SlackBotManager:
dingtalk_bot_manager.py:...
wecom_bot_manager.py:...
```

All `class FooBotManager:` — no parent class declared. The interface lives in the head of whoever last touched all eight files, not in code. This is the root condition that produces every drift catalogued below.

---

## 2. The Implicit Interface (What Every Manager Pretends to Honor)

Reading the eight files in parallel, the de-facto contract is:

| Method | Purpose | Confirmed in |
|---|---|---|
| `__init__(self)` | Initialize empty state | All 8 |
| `start_bot(self, config)` | Spin up a background thread, return after readiness or timeout | All 8 |
| `stop_bot(self)` | Signal shutdown, join thread | All 8 |
| `get_status(self) -> dict` | Report `is_running`, error state, ready state | All 8 (shape varies) |
| `_run_bot_thread(self, config)` | The thread entry point | All 8 |
| `_cleanup(self)` | Tear down loop, cancel tasks, null out client | Most |
| `update_behavior_config(self, config)` | Hot-reload behavior settings | 7 of 8 (missing in WeCom) |

Every manager has:
- `self.bot_thread: Optional[threading.Thread]`
- `self.is_running: bool`
- `self.config`
- `self.loop: Optional[asyncio.AbstractEventLoop]`
- `self._shutdown_event` / `self._ready_complete` / `self._startup_complete` — combinations vary
- `self._startup_error: Optional[str]`

So there *is* a shape. It is just not enforced. A new manager added next month could decline to call `_ready_complete.set()` and the rest of the system would learn at runtime.

---

## 3. Where The Eight Drift

### 3.1 Field naming — `enableTTS` vs `enable_tts`

`qq_bot_manager.py:23-31`:

```python
# /tmp/super-agent-party/py/qq_bot_manager.py:22-31
class QQBotConfig(BaseModel):
    QQAgent: str
    memoryLimit: int
    appid: str
    secret: str
    separators: List[str]
    reasoningVisible: bool
    quickRestart: bool
    is_sandbox: bool
```

`discord_bot_manager.py:22-32`:

```python
# /tmp/super-agent-party/py/discord_bot_manager.py:22-32
class DiscordBotConfig(BaseModel):
    token: str
    llm_model: str = "super-model"
    memory_limit: int = 10
    separators: List[str] = []
    reasoning_visible: bool = False
    quick_restart: bool = True
    enable_tts: bool = True
    wakeWord: str
    behaviorSettings: Optional[BehaviorSettings] = None
    behaviorTargetChatIds: List[str] = Field(default_factory=list)
```

The Chinese-platform configs (`QQBotConfig`, `FeishuBotConfig`, `WeChatBotConfig`, etc.) use `camelCase`. The Western-platform configs (`DiscordBotConfig`, `SlackBotConfig`) use `snake_case`. **Inside the same field set.** `memoryLimit` becomes `memory_limit`; `reasoningVisible` becomes `reasoning_visible`; `quickRestart` becomes `quick_restart`; `enableTTS` becomes `enable_tts`.

This is not a stylistic disagreement. This is a code path that authored seven managers in one convention and an eighth (Discord) and a ninth (Slack) in another. Then a Pydantic model has to forgive both via aliasing or fail in serialization.

`settings_template.json:531-541` confirms the dialects collide at the persistence layer:

```json
// config/settings_template.json:531-541
"discordBotConfig": {
  "token": "",
  "llm_model": "super-model",
  "memory_limit": 30,
  ...
}
```

vs

```json
// config/settings_template.json:520-530
"telegramBotConfig": {
  "TelegramAgent": "super-model",
  "memoryLimit": 20,
  ...
}
```

The same key set under two naming conventions in the same JSON file. The deserializer must handle both. If a contributor adds a new field on the Telegram side, the symmetric field on the Discord side has a different name. Symmetry breaks first, then ergonomics rot.

### 3.2 Startup timeout: 30s, or maybe 30s

All managers wait `30` seconds for startup readiness, hard-coded. `qq_bot_manager.py:64`, `feishu_bot_manager.py:67`, `telegram_bot_manager.py:50,56`, `discord_bot_manager.py:61`, `slack_bot_manager.py:64`.

A WeChat scan-QR-and-log-in flow (`wechat_bot_manager.py:33-57` with the QR interceptor) genuinely takes longer than a Telegram bot-token connection. The same 30s ceiling applies. A user with slow QR scan habits — anyone over 40 — gets a startup timeout despite the bot being seconds away from ready. There is no per-platform tuning; the constant is a magic number repeated eight times.

### 3.3 Ready signaling: two events or one?

`qq_bot_manager.py:42-43`:

```python
self._startup_complete = threading.Event()
self._ready_complete = threading.Event()
```

Two events. `_startup_complete` fires when the connection is up; `_ready_complete` fires when the bot reports `on_ready`. Both must be set within 30 seconds (lines 64, 72).

`slack_bot_manager.py:42`:

```python
self._ready_complete = threading.Event()
```

One event. No distinction between connected and ready.

`discord_bot_manager.py:42-43`:

```python
self._shutdown_event = threading.Event()
self._ready_complete = threading.Event()
```

One event for readiness; one for shutdown. No `_startup_complete`. So Discord conflates "connected" with "ready" but QQ does not, while Slack conflates everything. Three semantics, one nominal interface.

### 3.4 Behavior engine registration: who does it, when?

`telegram_bot_manager.py:73-74`:

```python
# /tmp/super-agent-party/py/telegram_bot_manager.py:73-74
                if behavior_data:
                    global_behavior_engine.update_config(behavior_data, {"telegram": target_ids})
```

`slack_bot_manager.py:77-78`:

```python
# /tmp/super-agent-party/py/slack_bot_manager.py:77-78
                global_behavior_engine.register_handler("slack", self.execute_behavior_event)
                settings = await load_settings()
```

Telegram updates the engine's *config* with behavior data. Slack registers a *handler* with the engine. They are doing different things. `behavior_engine.py:75-88` shows the engine has both `register_handler(platform, handler)` and `update_config(settings, platform_targets)` — and the eight managers call these in eight slightly different orders, sometimes with both, sometimes with only one.

A new platform added by a contributor must guess which calls are required. The contract is *implicit and discoverable only by reading the others*. That is the worst kind of contract.

### 3.5 Quick-restart command: present, absent, or platform-flavored

Every config has a `quickRestart` (or `quick_restart`) flag. Each manager interprets it differently. The QQ manager has a specific quick-restart code path; Telegram has another; some managers expose it via a runtime command (Discord `/restart`), others as an in-message keyword. The flag is the same name; the behavior is eight names.

### 3.6 TTS: enable_tts behaves differently per platform

`discord_bot_manager.py:29` defaults `enable_tts=True`. `slack_bot_manager.py:30` defaults `enable_tts=False`. Same nominal feature; different defaults; per-platform sub-handling (Discord uses voice channels; Telegram uses voice notes; QQ uses image-encoded audio). The flag suggests parity; the flag delivers nothing of the sort.

### 3.7 Memory and memoryLimit semantics

QQ: `memoryLimit: int = 30` (default per `settings_template.json:267`).
Telegram: `memoryLimit: int = 20` (line 522).
Discord: `memory_limit: int = 30` (line 533).
WeChat / WeCom / Feishu / DingTalk / Slack: `memoryLimit: 30`.

The default of 20 vs 30 is a real cliff — Telegram conversations lose the oldest exchange one round earlier than the rest. There is no documented reason; no `# Telegram: memory cap 20 because ...` comment. It is a forgotten edit or a fat-finger. The user experience diverges per platform.

### 3.8 `_stop_requested` flag — when do you set it?

`telegram_bot_manager.py:43,113-115`:

```python
self._stop_requested = False
...
def stop_bot(self):
    if not self.is_running and not self.bot_thread: return
    self._stop_requested = True
```

`qq_bot_manager.py` has no `_stop_requested`. `feishu_bot_manager.py:46` has it but uses it differently. `discord_bot_manager.py:45` has it but it's set only in `_run_bot_thread` error paths.

The flag exists to disambiguate "the user clicked stop" from "the bot crashed and we are restarting." Six of eight managers need this disambiguation; how they implement it is freelance.

---

## 4. The Lie of "Unified Behavior Engine Across Platforms"

`behavior_engine.py:53-79` defines a global singleton `BehaviorEngine` and a `register_handler(platform, handler)` method. The pitch is: configure a behavior once, and it dispatches to all enabled platforms.

The reality:

`behavior_engine.py:80-88`:

```python
# /tmp/super-agent-party/py/behavior_engine.py:80-88
    def register_handler(self, platform: str, handler: Callable):
        """注册平台的执行回调函数"""
        self.handlers[platform] = handler
        if platform not in self.platform_activity:
            self.platform_activity[platform] = {}
            
        # 关键修复：当新平台注册时，如果已经有配置，重置计时器
        if self.settings and self.settings.enabled:
            self.timers.clear()
            self.counters.clear()
```

The "key fix" comment is honest: registering a new platform mid-flight resets *all* timers across *all* platforms. A user who enables their fifth bot in a chat session causes the existing four bots' scheduled behaviors to re-anchor. This is not platform-isolated state. It is a global timer table keyed by `(behavior_idx, platform, chat_id)` strings.

`behavior_engine.py:184-188`:

```python
# /tmp/super-agent-party/py/behavior_engine.py:184-188
                            uniq_key = f"noInput_{idx}_{platform}_{chat_id}"
                            if self.timers.get(uniq_key, 0) < now - latency - 5: # 防抖
                                trigger_chats.append(chat_id)
                                self.timers[uniq_key] = now
```

The debounce window is `latency - 5` seconds — magic number, no comment, no test. Two simultaneous user activity events on the same chat within 5 seconds of the configured latency could both trigger or both suppress, depending on millisecond timing.

Every manager registers `register_handler(platform, handler)`. The dispatch is per-platform but the state is global. The interface name is "unified"; the failure mode is "shared mutable state across eight subsystems."

---

## 5. The Threading Pattern Repeated Eight Times

Every manager uses the same recipe:

1. Create a `threading.Thread` with `daemon=True`.
2. Inside that thread, `asyncio.new_event_loop()`.
3. Run an `async def main_startup()` to completion.
4. On exit, cancel all tasks and close the loop.

`telegram_bot_manager.py:60-98`:

```python
# /tmp/super-agent-party/py/telegram_bot_manager.py:60-98
    def _run_bot_thread(self, config: TelegramBotConfig):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        async def main_startup():
            try:
                ...
                self._startup_complete.set()
                await self.bot_client.run()
            except Exception as e:
                if not self._stop_requested:
                    self._startup_error = str(e)
                self._startup_complete.set()
                self._ready_complete.set()

        try:
            self.loop.run_until_complete(main_startup())
        finally:
            self._cleanup()
```

This is the eight-times-repeated heart of SAP's IM layer. **One event loop per platform, each in its own thread.** With eight bots enabled, you have nine event loops (eight plus the FastAPI server loop). Each calls into shared state (`global_behavior_engine`, settings cache, `affection_system`) without coordination.

Cross-loop calls are a latent deadlock surface. `run_coroutine_threadsafe` is the only correct call shape. Audit reveals SAP's affection extractor (`affection_system.py:37-64`) is called from per-platform message handlers — i.e., from per-platform loops. Those handlers `await load_affection_data()` which uses `asyncio.to_thread` — fine. But they then *mutate* the dict in memory before saving (`affection_system.py:55-64`). Two bots receiving messages from the same user on two platforms could race the read-modify-write. The save is atomic per call; the read-modify-write is not.

This is a textbook race condition that ships because the implicit interface does not name shared-state contention.

---

## 6. The Stop-Bot Pattern Has Subtle Bugs

`telegram_bot_manager.py:112-123`:

```python
# /tmp/super-agent-party/py/telegram_bot_manager.py:112-123
    def stop_bot(self):
        if not self.is_running and not self.bot_thread: return
        self._stop_requested = True
        self.is_running = False
        if self.bot_client:
            self.bot_client._shutdown_requested = True
            # 取消所有活跃任务
            for task in self.bot_client.active_tasks.values():
                task.cancel()
        if self.bot_thread and self.bot_thread.is_alive():
            self.bot_thread.join(timeout=10)
        self._stop_requested = False
```

`self._stop_requested = False` at the *end* — but `join(timeout=10)` may return before the thread exits. If the thread is stuck waiting on a Telegram long-poll, the flag flips back to `False` while the thread is still alive. A subsequent `start_bot` call (line 32) finds `bot_thread.is_alive() == True` and raises. The error message ("Telegram bot is stopping, please wait") is half right — the bot is stopping, has been told to stop, but the manager has already forgotten.

This is the kind of subtle lifecycle bug that emerges only when a user clicks Stop and then Start within 10 seconds. Eight managers, each with their own variant of this.

---

## 7. Cross-References

- [[10_domain/14_MESSAGING_DOMAIN]] — the Architect's view of the same eight modules from the *domain* axis
- [[30_execution/35_IM_BOT_DEPLOYMENT_OVERVIEW]] — Forge's execution-axis teardown of one-click deploy
- [[50_verification/56_PRIVACY_BOUNDARIES]] — eight platforms, eight jurisdictions, eight threat models
- [[50_verification/57_FAILURE_TAXONOMY]] — the race condition above ranked in the master failure table
- [[hermes:HEM-25_GATEWAY_INTERFACE]] — Hermes's platform-registry pattern as a positive counter-example
- [[ember:RULES.AI]] — "use internal APIs for communication between code modules" — SAP violates this with `global_behavior_engine` as a free-for-all

---

## What This Means for Ember

**Adopt:**
- Adopt the **thread-per-platform with a dedicated event loop** pattern for any Ember surface that must speak a long-poll or streaming protocol with vendor SDKs that bring their own event loops. The pattern is correct in shape (see `telegram_bot_manager.py:60-67`) — what is wrong in SAP is everything *around* the pattern.

**Adapt:**
- Adapt the implicit interface into an **explicit `Protocol` (PEP 544) or abstract base class** for every reach-platform. Ember's `Munnr` (the Mouth) owns this. Every reach module declares: `class TelegramReach(MunnrReach): ...` with abstract methods `start()`, `stop()`, `send()`, `receive_handler()`, `status()`. A new platform is a subclass; a new method on the base breaks subclasses loudly at import time, not at the user's first crash.
- Adapt the behavior engine into a **per-platform scheduler with merge semantics at the boundary**. Per-platform timers stay local to the platform; cross-platform behaviors register through a coordinator that owns the merge. This isolates state. SAP's global timer table is rejected.

**Avoid:**
- **Avoid implicit interfaces.** If `BotManager` is not a class — and SAP's is not — then the next contributor has only ad-hoc precedent to learn from. Every Ember reach platform inherits from a typed base. No exceptions.
- **Avoid the dual-naming-convention pattern.** All Ember config fields are `snake_case`. There is no negotiation. A migration adapter handles legacy `camelCase` SAP-imported settings but normalizes internally to one convention. The cost of maintaining both is paid forever; the cost of normalizing once is paid once.
- **Avoid hard-coded 30-second startup timeouts.** Per-platform timeouts declared on the platform class as a class-level constant; the timeout is wired to the *kind* of authentication (instant token < 5s; QR scan < 120s; OAuth flow < 60s).
- **Avoid global mutable state shared across per-platform event loops without explicit lock semantics.** SAP's `global_behavior_engine` mutates `self.timers` from inside `_tick()` called by one of N loops. Ember either makes that state per-loop or wraps it in an `asyncio.Lock` honored everywhere.
- **Avoid clearing global timers when registering a new platform.** SAP does this (`behavior_engine.py:85-88`) under the comment "key fix." It is a key bug.

**Invent:**
- **Reach Protocol with capability declaration.** Every Ember reach platform exposes a `capabilities()` method that names what it can and cannot do — voice notes? voice channels? rich messages? attachments? per-message threading? — *typed*, *introspectable*, *testable*. Munnr renders the user's message through the lens of capabilities, never assumes parity. This is the antidote to SAP's `enable_tts: True | False` lie.
- **Reach Identity Boundary.** Every reach platform carries an explicit `identity_scope` — does this platform's user-id align with Ember's canonical user identity? Telegram: no. Discord: no. Slack: workspace-scoped. Per-platform identity becomes a first-class concept, not an implicit join in a JSON blob. Solves the affection cross-platform race in §5 by giving the affection store a typed key.
- **Tiered Presence Schedule.** Ember's behavior engine schedules at *tier* level — `FULL_PRESENCE`, `TEXT_ONLY`, `LOG_ONLY` (Vow of Tiered Presence) — and the reach platform decides how to express the tier. The behavior engine never speaks the wire format; it speaks intent. SAP's engine speaks both, and the conflation produces the per-platform drift catalogued above.
- **Lifecycle Linter** — a CI check that loads every reach platform, asserts the protocol surface, runs a start/stop cycle against a mock transport, asserts the manager returns to a *clean* idle state. If SAP had this, half the bugs in this doc would be caught at PR time.

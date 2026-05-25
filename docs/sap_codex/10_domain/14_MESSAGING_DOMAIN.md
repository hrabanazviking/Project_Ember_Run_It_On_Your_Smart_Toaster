---
codex_id: 14_MESSAGING_DOMAIN
title: Messaging Domain — Eight IM Bots, One Pattern, Zero Abstractions
role: Architect
layer: Domain
status: draft
sap_source_refs:
  - py/qq_bot_manager.py:1-60
  - py/wechat_bot_manager.py:1-100
  - py/wecom_bot_manager.py:1-80
  - py/feishu_bot_manager.py:1-60
  - py/dingtalk_bot_manager.py:1-60
  - py/telegram_bot_manager.py:1-138
  - py/telegram_client.py:1-50
  - py/discord_bot_manager.py:1-60
  - py/slack_bot_manager.py:1-60
  - py/behavior_engine.py:53-100
  - py/sub_agent.py:160-220
ember_subsystem_targets: [Munnr, Strengr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/1A_AFFECTION_DOMAIN
  - 20_interface/26_IM_BOT_INTERFACE
  - 30_execution/35_IM_BOT_DEPLOYMENT_OVERVIEW
  - 50_verification/56_PRIVACY_BOUNDARIES
---

# Messaging Domain
## Eight IM Bots, One Pattern, Zero Abstractions

*— Rúnhild Svartdóttir, Architect*

> *Eight halls were built. Eight halls were thatched. Eight halls held the same fire. Yet no two halls had the same door, and no smith ever wrote down which door was the door.*

SAP ships eight instant-messaging bot integrations. Reading the eight files in sequence reveals something striking: they all do the same thing in a remarkably consistent way, and yet there is no abstraction over them. They are eight implementations of the same intent, copy-pasted with platform-specific glue, sharing exactly three external surfaces and no interfaces. This doc names the implicit pattern, names what the explicit pattern *would* look like, and points at what Ember must invent if it wants reach without rewriting eight times.

---

## 1. The Subject Itself

**What the domain owns:** outbound and inbound chat across eight platforms — QQ, WeChat, WeCom (Enterprise WeChat), Feishu (Lark), DingTalk, Telegram, Discord, Slack.

**What the domain does *not* own:** unified messaging. There is no `IMBot` base class, no `MessageManager` protocol, no shared `Conversation` type. The pattern exists; the abstraction does not.

**Where it lives:**

| Platform | Manager File | LOC | SDK |
|---|---|---|---|
| QQ (Tencent open) | `py/qq_bot_manager.py` | 620 | `botpy` |
| WeChat personal | `py/wechat_bot_manager.py` | 484 | `wechatbot-sdk` (vendored externally) |
| WeCom enterprise | `py/wecom_bot_manager.py` | 404 | HTTP API + custom |
| Feishu / Lark | `py/feishu_bot_manager.py` | 602 | direct WS + HTTP |
| DingTalk | `py/dingtalk_bot_manager.py` | 348 | HTTP + WS |
| Telegram (bot) | `py/telegram_bot_manager.py` | 137 (+ `telegram_client.py` 370) | python-telegram-bot via custom client |
| Discord | `py/discord_bot_manager.py` | 440 | `discord.py` |
| Slack | `py/slack_bot_manager.py` | 349 | `slack_sdk` (Socket Mode) |

Total: ~3,784 LOC across eight files. About one platform every 470 lines. The **shape** is so consistent it could be a metaclass.

---

## 2. How It Works

### 2.1 The unspoken interface

Every manager file declares a Pydantic `XBotConfig` and an `XBotManager` class. Read them in parallel and the contract emerges:

**Config fields, present in 6+ of 8:**
- `XAgent: str` — which LLM model name to use (e.g. `TelegramAgent`, `FeishuAgent`)
- `memoryLimit: int` — how many turns of memory to retain
- `separators: List[str]` — message segmentation tokens
- `reasoningVisible: bool` — show chain-of-thought
- `quickRestart: bool` — restart command opt-in
- `enableTTS: bool` — voice-out enabled
- `wakeWord: str` — invocation token
- `behaviorSettings: Optional[BehaviorSettings]` — autonomous behavior config
- `behaviorTargetChatIds: List[str]` — which chats receive behavior-driven messages

**Manager methods, present in all 8:**
- `__init__(self)` — initialize thread, client, event flags
- `start_bot(self, config)` — spawn a daemon thread, wait for `_startup_complete` event, raise on timeout
- `stop_bot(self)` — set `_stop_requested`, terminate client, join thread (with timeout)
- `_run_bot_thread(self, config)` — the thread entrypoint; creates an asyncio loop; runs the client
- `_cleanup(self)` — invariant cleanup
- `get_status(self)` — returns `{is_running, startup_error, ready_completed}`
- `update_behavior_config(self, config)` — hot-update behavior settings

**External surfaces, all 8 hit:**
- `from py.get_setting import get_port, load_settings` — for the HTTP self-call endpoint
- `from py.behavior_engine import global_behavior_engine, BehaviorSettings, ...` — register handler, sync config
- `AsyncOpenAI(api_key="super-secret-key", base_url=f"http://{HOST}:{PORT}/v1")` — call back into the main server

So the implicit contract is real and consistent. The abstraction is missing.

### 2.2 The threading dance

Every manager runs in **its own thread with its own asyncio loop**. Read `py/telegram_bot_manager.py:60-67`:

```python
def _run_bot_thread(self, config: TelegramBotConfig):
    self.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(self.loop)
    async def main_startup():
        try:
            from py.get_setting import load_settings
            from py.behavior_engine import global_behavior_engine
            ...
```

This is necessary because some IM SDKs (notably `botpy` for QQ and `discord.py`) want to *own* the event loop, and they cannot share with FastAPI's. The pattern is: thread spawns, thread creates loop, loop runs the client, main process orchestrates via `threading.Event` flags (`_startup_complete`, `_ready_complete`, `_shutdown_event`).

**Startup synchronization** is by event-flag with timeout. `_startup_complete.wait(timeout=30)` (e.g. `telegram_bot_manager.py:50`) blocks the calling thread; if no signal in 30 seconds, raise. This is correct — but the timeouts and error messages drift between managers; some say "连接超时", some say "Bot startup timeout", some say "机器人启动失败"; there is no unified error type.

### 2.3 The handoff to the reasoning loop

This is the most architecturally honest thing about the IM domain. Every bot, on receipt of a user message, builds an OpenAI-shaped request and POSTs it to `http://127.0.0.1:{port}/v1/chat/completions`. The bot never imports the conversation logic.

This means **the eight bots are HTTP clients of the main server**, not library consumers of it. Consequences:

- They can be replaced piecemeal (replace `discord_bot_manager.py` with a new file; the rest of SAP doesn't notice).
- They get the *same* conversation logic, system-prompts, tool composition, and side-effects as the web UI — because they're hitting the same endpoint.
- They are decoupled from internal refactors in `server.py`.
- They cost an HTTP round-trip per message instead of an in-process function call.
- The endpoint is unauthenticated on localhost.

### 2.4 The behavior-engine bridge

Every manager imports `global_behavior_engine` and registers itself:

```python
# Pattern, present in all 8 managers
from py.behavior_engine import global_behavior_engine
# ... inside the bot client:
global_behavior_engine.register_handler(platform="telegram", handler=my_handler_fn)
```

This is how SAP's *autonomous* behavior (time triggers, no-input triggers, cycles) reaches eight platforms with one configuration file. The `behavior_engine` (`py/behavior_engine.py:75-88`) maintains a `Dict[str, Callable]` of handlers; when a behavior fires for `platform="telegram"`, the engine calls the registered handler with `(chat_id, behavior)`. The handler is responsible for formatting and dispatch.

The sub-agent uses the same registry to push task results across platforms (`py/sub_agent.py:182-214`). So the *autonomous-behavior fanout* and the *task-result fanout* share one handler registry. This is good. This is rare.

### 2.5 Per-platform divergences worth noting

- **WeChat** uses an `StreamInterceptor` (`wechat_bot_manager.py:30-66`) to **screen-scrape the QR code login URL out of stdout**. This is the only way `wechatbot-sdk` exposes the QR code. SAP grabs the printed text, extracts the URL via regex, and presents it in the GUI. It works. It is also the dirtiest pattern in the entire IM domain.
- **Slack** uses Socket Mode (`slack_bot_manager.py:23`) — a WebSocket connection to Slack rather than webhooks. This bypasses the need for a public HTTP endpoint; SAP can run on a laptop behind NAT and still receive Slack messages.
- **Telegram** has a separate `telegram_client.py` (370 LOC) — the only platform where the SDK logic was extracted into a sibling file. The pattern *could* have been replicated across the other seven; it wasn't.
- **Discord** ships voice support via `convert_to_opus_simple` (imported from `get_setting`, line 18) — the only IM that supports voice messages bidirectionally.
- **QQ** is the only platform that uses Tencent's "open" sandbox/production split — `is_sandbox: bool` in config (line 31).

### 2.6 The wakeword and the silence

`wakeWord: str` is in every config. The implementation reads roughly: if the message starts with `wakeWord` (or mentions the bot by name in group chats), route to the LLM; else, silence. The wakeword discipline is honest — in eight-bot reach, you cannot have the agent respond to every message in every group it's in, so the wakeword is the gate. It is also the *only* gate, and it is a single string in config. There is no per-user, per-channel, per-time-of-day variation.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The same pattern, eight times

The single greatest design failure of the messaging domain is the absence of `IMBotManager` as a base class. The pattern is so consistent that a 200-line abstract base could replace the boilerplate of:

- The `__init__` constructor pattern (the same nine `Optional[...]` fields in every manager).
- The `start_bot` event-flag startup dance (the same `_startup_complete.wait` / `_ready_complete.wait` / `_startup_error` checks in every manager).
- The `stop_bot` cleanup (same `_stop_requested` + thread.join pattern).
- The `_run_bot_thread` asyncio-loop spawning.
- The `get_status` reply shape.
- The `update_behavior_config` hot-update.

Eight times. The next platform addition will need ~470 lines, ~440 of which are boilerplate.

### 3.2 No unified message type

Every manager builds its own conversation history dict. There is no `Message` class. There is no `Conversation` class. The LLM response is parsed differently in each manager (some strip ChatGPT-style markdown, some don't; some split on `\n\n`, some on the configured separators; some preserve reasoning visibility, some hide it).

The result: behavioral drift across platforms. A user asking the same question on Telegram and Discord might get visually different answers because the post-processing diverges.

### 3.3 The vendored secret in plain text

`AsyncOpenAI(api_key="super-secret-key", ...)` — verbatim from every manager, including `qq_bot_manager.py:20`. The string is the API key passed to the local server. It is *not* validated by `server.py` (the localhost endpoint has no auth). It is a fossil — once a sanity check on the SDK requiring some non-empty key. **It looks like a secret in the code**. A reader unfamiliar with the architecture will think it is one.

### 3.4 No retry/backoff at the network edge

When an IM platform's WebSocket drops, each manager handles it differently. Slack reconnects through the `slack_sdk` library. Discord lets `discord.py` handle it. Telegram has its custom client. WeChat... mostly hopes. There is no unified reconnect policy. Compare to `py/mcp_clients.py:111-133` where the *MCP* layer has a disciplined reconnect monitor.

### 3.5 The wakeword can be spoofed in groups

A user in a group chat can name themselves the wakeword; the bot will then respond to their *every* message because the wakeword always matches at message start. This is a known footgun across IM-bot frameworks; SAP does not mitigate.

### 3.6 The crisp parts

- The **threading + asyncio handoff** pattern is correct and consistent. The only thing missing is the abstraction.
- The **behavior_engine registry** is genuinely the right shape for cross-platform autonomous behavior.
- The **HTTP-client-of-self** architecture is honest — bots don't lie about how they reach the brain.
- The **per-platform Pydantic config** is well-typed, even if not deduplicated.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 6 for the domain's place
- [[1A_AFFECTION_DOMAIN]] for how affection state crosses IM platforms (it doesn't, really)
- [[20_interface/26_IM_BOT_INTERFACE]] (Auditor) for the explicit interface analysis
- [[30_execution/35_IM_BOT_DEPLOYMENT_OVERVIEW]] (Forge-A) for one-click deployment mechanics
- [[30_execution/35a]]–[[30_execution/35h]] (Forge-B) for each platform's deep dive
- [[50_verification/56_PRIVACY_BOUNDARIES]] (Auditor) for the privacy threat model
- [[hermes:14_GATEWAY_MULTI_PLATFORM]] — Hermes's contrasting unified gateway design (24 modules, 30+ platform adapters, with a real abstraction)
- [[peer:LETTA-7_SURFACE]] for the contrasting Letta surface (which has none of this — Letta is a single-platform agent)

---

## What This Means for Ember

**Adopt:**
- The **HTTP-client-of-self** pattern (eight bots POST to `127.0.0.1:port/v1/chat/completions`). For Ember the variant is the **MCP-client-of-self** pattern: every reach adapter speaks to Ember's own MCP server surface. Same decoupling; typed; auditable.
- The **threading + asyncio loop-per-bot** pattern. Strengr's reach adapters run in worker threads with their own loops; the main loop orchestrates.
- The **behavior_engine handler registry** as the *right shape*. Strengr exposes `register_reach_handler(platform_name, handler_fn)`; the scheduler and the sub-agent system both fan out through it.
- The **lazy SDK import** pattern (`try/except ImportError`) from `py/wechat_bot_manager.py:23-27` and equivalents. Reach adapters are individually optional.
- The **typed Pydantic config per platform** — but unified under a base config schema (see Adapt).

**Adapt:**
- The **eight-times-no-abstraction** pattern is the cautionary tale. Ember writes one `ReachAdapter` ABC (proposed name: **Boðr** — messenger) with `start`, `stop`, `register_handler`, `send`, `status` as the interface. Platform-specific code subclasses, providing only the SDK-specific glue. Target: a new reach platform is <200 lines of subclass.
- SAP's **wakeword as a single string** — adapt to Ember's typed wakeword grammar: a per-channel + per-user + per-time-window expression. The Defended System Prompt vow extends to wakeword matching.
- The **per-platform message-processing drift** — unify under a `MessageEnvelope` type: `{platform, channel, sender, content, timestamp, attachments, reply_to}`. Every adapter produces and consumes envelopes; the conversation kernel sees only envelopes.

**Avoid:**
- **`api_key="super-secret-key"`** as a literal. Even as a fossil it teaches readers wrong habits. Ember's internal MCP surface authenticates with a per-session token rotated at startup.
- **Per-platform divergent error messages** for the same condition. Standardize the error taxonomy.
- **Unauthenticated localhost endpoints** that any process on the host can hit.
- **Screen-scraping stdout for login URLs** (the WeChat pattern at `wechat_bot_manager.py:30-66`). If a SDK forces this, the adapter contains it but a yellow-card lint warning surfaces in CI.

**Invent:**
- **The Reach Pyramid.** Ember sorts its reach platforms by trust + privacy + intimacy: **Intimate** (one-on-one DM with verified user) / **Local** (one-on-one in a private channel) / **Public** (group chat) / **Broadcast** (livestream/feed). Each platform self-classifies and the affection/memory machinery knows what level it is operating in. SAP treats all eight platforms identically — a Telegram DM and a Discord public channel get the same prompt. Ember refuses.
- **The Per-Platform Reach Manifest.** A YAML file per platform declaring `wakeword_grammar`, `silence_default`, `attachment_allow`, `audit_level`. Strengr loads the manifest; ReachAdapter respects it. Removes the wakeword-as-magic-string footgun.
- **Cross-Platform Identity Joining.** SAP has no concept of "the same user, two platforms." Ember does: the **Auðkenni** (recognition) surface lets a user verify a Telegram identity and a Slack identity belong to the same human. Affection, memory, and behavior policy then join across the two channels — but only after consent.
- **Reach-Tier Collapse.** A Pi-Ember offers only a single reach platform (the local terminal); a laptop-Ember adds two more; a workstation-Ember can host all eight. Tier collapse is configured by `tier_manifest.yaml` (see [[60_synthesis/63_PERFORMANCE_TIER_ENGINE]]). SAP scales by uniformly enabling everything; Ember tiers explicitly.
- **The Wakeword Decoy Detector.** Strengr observes wakeword-match rate per (user, channel). If a user is matching the wakeword on >40% of their messages without being the registered owner, raise a Sögumiðla event suggesting wakeword change or per-user rate-limit. Spoof mitigation through behavior, not just config.

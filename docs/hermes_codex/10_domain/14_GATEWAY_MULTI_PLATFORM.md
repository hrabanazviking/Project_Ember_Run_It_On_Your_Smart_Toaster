---
codex_id: 14_GATEWAY_MULTI_PLATFORM
title: The Gateway — One Mouth, Thirty Tongues
role: Architect
layer: Domain
status: draft
hermes_source_refs:
  - gateway/__init__.py:1-36
  - gateway/run.py:1-100
  - gateway/session.py:1-200
  - gateway/config.py:1-60
  - gateway/platforms/base.py:1-200
  - gateway/platforms/ADDING_A_PLATFORM.md:1-80
  - gateway/channel_directory.py
  - gateway/delivery.py
  - gateway/hooks.py
  - gateway/memory_monitor.py
  - gateway/mirror.py
  - gateway/pairing.py
  - gateway/platform_registry.py
  - gateway/runtime_footer.py
  - gateway/shutdown_forensics.py
  - gateway/slash_access.py
  - gateway/status.py
  - gateway/sticker_cache.py
  - gateway/stream_consumer.py
  - gateway/whatsapp_identity.py
  - gateway/platforms/telegram.py
  - gateway/platforms/discord.py
  - gateway/platforms/slack.py
  - gateway/platforms/whatsapp.py
  - gateway/platforms/signal.py
  - gateway/platforms/matrix.py
  - gateway/platforms/feishu.py
  - gateway/platforms/wecom.py
  - gateway/platforms/yuanbao.py
  - gateway/platforms/email.py
  - gateway/platforms/sms.py
  - gateway/platforms/dingtalk.py
  - gateway/platforms/homeassistant.py
  - gateway/platforms/api_server.py
  - gateway/platforms/webhook.py
  - gateway/platforms/bluebubbles.py
  - gateway/platforms/mattermost.py
  - gateway/platforms/msgraph_webhook.py
  - gateway/platforms/qqbot/
  - gateway/platforms/weixin.py
  - gateway/platforms/_http_client_limits.py
  - plugins/platforms/google_chat/
  - plugins/platforms/irc/
  - plugins/platforms/line/
  - plugins/platforms/simplex/
  - plugins/platforms/teams/
  - AGENTS.md:38-45
  - AGENTS.md:868-887
  - AGENTS.md:970-979
ember_subsystem_targets: [Munnr, Strengr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/17_PLUGINS_EXTENSIBILITY
  - 10_domain/19_BOUNDARY_LAW
  - 30_execution/32_MULTI_DEVICE_ORCHESTRATION
  - 50_verification/52_ANTIPATTERN_CATALOG
---

# The Gateway
## One Mouth, Thirty Tongues

*— Rúnhild Svartdóttir, Architect*

> *A gateway is a chambered heart. Every chamber speaks a different language to its vessel — Telegram is not Discord, Slack is not WhatsApp, Signal is not Matrix — but the blood flowing through is the same. The architect's job is to make sure the chambers can fail independently, and that the heart still beats when one of them does.*

Hermes's `gateway/` directory is the multi-platform messaging surface — *thirty* platform adapters at last count, with a runtime that constructs an `AIAgent` per session and drives it through messaging protocols Hermes does not own. This is the most outward-facing part of Hermes, the part most affected by external service quirks, and (for Ember) the part most explicitly *out of scope*. We document it anyway because the *architecture* is portable even when the surface area is not.

The mental model: **one gateway, many platform adapters, many concurrent sessions, one `AIAgent` per session in an LRU cache, two message guards, one delivery router.**

---

## 1. The Thirty Tongues

The bundled (`gateway/platforms/`) adapter set:

| File | Platform | Notes |
|---|---|---|
| `telegram.py` (+ `telegram_network.py`) | Telegram | Bot API, webhooks, DM topics, forum supergroups |
| `discord.py` | Discord | Bot, threads, guild management |
| `slack.py` | Slack | Bolt SDK, slash commands, threads |
| `whatsapp.py` | WhatsApp | Business API |
| `signal.py` (+ `signal_rate_limit.py`) | Signal | signal-cli bridging |
| `matrix.py` | Matrix | mautrix client with encryption |
| `mattermost.py` | Mattermost | Slack-like with self-hosted twist |
| `feishu.py` (+ `feishu_comment.py`, `feishu_comment_rules.py`) | Feishu (Lark) | Bytedance's enterprise platform |
| `dingtalk.py` | DingTalk | Alibaba's enterprise platform |
| `wecom.py` (+ `wecom_callback.py`, `wecom_crypto.py`) | WeCom | Tencent's enterprise WeChat |
| `weixin.py` | Weixin (WeChat) | Consumer side |
| `yuanbao.py` (+ `yuanbao_media.py`, `yuanbao_proto.py`, `yuanbao_sticker.py`) | Yuanbao | Tencent's AI chat platform |
| `qqbot/` | QQBot | Tencent's QQ messenger |
| `email.py` | Email (IMAP/SMTP) | inbound-poll, outbound-send |
| `sms.py` | SMS | Carrier-specific |
| `bluebubbles.py` | BlueBubbles | iMessage relay |
| `msgraph_webhook.py` | MS Graph / Teams | Webhook for Teams |
| `homeassistant.py` | Home Assistant | Treat smart-home events as messages |
| `api_server.py` | Generic HTTP API | RESTful agent surface |
| `webhook.py` | Inbound webhook | catch-all for one-off integrations |

The plugin-shipped (`plugins/platforms/`) adapter set adds:
- `google_chat/`, `irc/`, `line/`, `simplex/`, `teams/`

Total: roughly **24 first-party + 5 plugin-shipped = 30 platforms** Hermes can speak.

This is more platforms than most messaging companies *support internally*. It is the deepest pluggability surface in Hermes.

---

## 2. The Six Concepts

The gateway has six load-bearing concepts. Each lives in its own module.

### 2.1 `Platform` enum + `SessionSource` (`gateway/config.py`, `gateway/session.py:80-156`)

`SessionSource` (`gateway/session.py:70-156`) is the unit of "where did this message come from." Fields include:

- `platform: Platform`
- `chat_id: str`
- `chat_name: Optional[str]`
- `chat_type: str` — `"dm" | "group" | "channel" | "thread"`
- `user_id`, `user_name`, `user_id_alt` (platform-specific alt ID — e.g. Signal UUID, Feishu union_id)
- `thread_id` — forum topics, Discord threads, Telegram DM topics
- `chat_topic` — Discord/Slack channel topic
- `guild_id` — Discord guild, Slack workspace, Matrix server
- `parent_chat_id` — parent channel when chat_id is a thread
- `message_id` — for pin/reply/react

A `SessionSource.description` (`gateway/session.py:95-114`) generates a one-line human readable: *"DM with @alice"*, *"group: dev-team, thread: 17"*, etc. This goes into the system prompt so the agent *knows where it is*.

### 2.2 `SessionContext` + `SessionStore` (`gateway/session.py:159+`)

`SessionContext` (`gateway/session.py:159-178`) packages the `SessionSource` plus the *connected platforms* list and the *home channels* dict. Why both? Because the agent might be triggered from Discord but asked to deliver a result to Telegram (`send_message` to the Telegram home channel). The context tells it what's possible.

`SessionStore` persists session metadata. Each conversation is keyed by `(platform, chat_id, user_id)` — a tuple that identifies a specific human chatting with the agent in a specific room. Reset policies (`SessionResetPolicy` — re-exported from `gateway/__init__.py:13-16`) decide when to start a fresh `AIAgent`.

### 2.3 `BasePlatformAdapter` (`gateway/platforms/base.py`)

The ABC every platform adapter inherits. Required methods per `gateway/platforms/ADDING_A_PLATFORM.md:71-100`:

| Method | Purpose |
|---|---|
| `__init__(self, config)` | Parse config; call `super().__init__(config, Platform.YOUR_PLATFORM)` |
| `connect() -> bool` | Open connection, start listeners |
| `disconnect()` | Tear down |
| `send_message(session_source, content, **kwargs)` | Send outbound text |
| `send_media(session_source, path, **kwargs)` | Send file |
| `is_authorized(user_id)` | User allow-list check |
| `extract_event(...)` | Map inbound to a normalized event |
| `start_typing(session_source)` / `_keep_typing(...)` | Optional liveness indicator |

The base class provides surprisingly sophisticated helpers (`gateway/platforms/base.py:114-199`):

- `utf16_len(s)` — count UTF-16 code units (Telegram's 4096-char limit is in UTF-16, not codepoints; emoji count as 2)
- `_prefix_within_utf16_limit(s, limit)` — binary-search truncation that respects surrogate pairs
- `_custom_unit_to_cp(s, budget, len_fn)` — generic length-aware prefix
- `is_network_accessible(host)` — refuse to expose adapters beyond loopback unless configured
- `truncate_message(...)` — protocol-aware splitting

These exist because every platform has its own length limit and its own broken length-measure. Telegram uses UTF-16. Slack uses codepoints. Discord uses something else. The base class is where these protocol quirks are absorbed so the adapter author doesn't re-discover them.

### 2.4 `GatewayRunner` (`gateway/run.py`)

The main daemon. Holds:
- A list of `BasePlatformAdapter` instances (one per configured platform)
- An LRU cache of `AIAgent` instances, capped at `_AGENT_CACHE_MAX_SIZE = 128` and idle-evicted after `_AGENT_CACHE_IDLE_TTL_SECS = 3600.0` (`gateway/run.py:62-66`)
- A delivery router (`DeliveryRouter` from `gateway/delivery.py`)
- A channel directory (`gateway/channel_directory.py`)
- A status surface (`gateway/status.py`)

The agent cache (`gateway/run.py:58-66`) is the key efficiency: a session that says "hello" three times in two minutes hits the same `AIAgent` instance three times — which means warm prompt cache, warm tool schemas, warm memory provider.

### 2.5 `DeliveryRouter` (`gateway/delivery.py`)

Outbound routing. When a cron job fires with `deliver=telegram`, the router asks the gateway *"is the Telegram adapter live?"* and routes through it. The hardcoded `*_HOME_CHANNEL` env vars (`TELEGRAM_HOME_CHANNEL`, `DISCORD_HOME_CHANNEL`, etc.) tell the router *where to deliver* when the recipient isn't specified by the cron job itself.

Plugins can declare a `cron_deliver_env_var` in their `plugin.yaml` (per `gateway/platforms/ADDING_A_PLATFORM.md:33-36`) so the same routing works for plugin-shipped platforms without editing `cron/scheduler.py`'s hardcoded sets.

### 2.6 `ChannelDirectory` (`gateway/channel_directory.py`)

A *write-ahead log* of every channel the gateway has ever seen. When the agent says "list the channels I can reach," the directory answers. When the cron scheduler asks "is `#engineering` a real Slack channel?" the directory answers. The directory is the gateway's stable understanding of its outward surface even when adapters momentarily disconnect.

---

## 3. The Concurrency Model

Each platform adapter runs its own async listener task. When an inbound message arrives:

1. The adapter calls `extract_event(...)` to produce a normalized event.
2. The runner consults the session store: is there an existing `AIAgent` for this `(platform, chat_id, user_id)`? If yes and not expired, reuse. If no, construct one.
3. The runner queues the user message for the agent.
4. The agent runs `run_conversation(user_message)`. While it runs, the adapter calls `_keep_typing` periodically to signal liveness to the user.
5. Output is streamed (or batched, per platform capability) back through the adapter.

The cache eviction (`_enforce_agent_cache_cap`, `_session_expiry_watcher` — referenced from `gateway/run.py:58-66`) runs as a background task and removes the least-recently-used agents when capacity is hit.

---

## 4. The Two Message Guards (the Boundary Leak)

`AGENTS.md:970-979` describes a discipline that is also an architectural leak:

> *"When an agent is running, messages pass through two sequential guards: (1) base adapter (gateway/platforms/base.py) queues messages in `_pending_messages` when `session_key in self._active_sessions`, and (2) gateway runner (gateway/run.py) intercepts `/stop`, `/new`, `/queue`, `/status`, `/approve`, `/deny` before they reach `running_agent.interrupt()`. Any new command that must reach the runner while the agent is blocked (e.g. approval prompts) MUST bypass BOTH guards and be dispatched inline, not via `_process_message_background()` (which races session lifecycle)."*

Two guards means two places to update when a new control command is added. The architecture would be cleaner with *one* guard and one routing decision point. This is on the list for `[[10_domain/19_BOUNDARY_LAW]]`.

---

## 5. The Pairing Flow

`gateway/pairing.py` handles user-to-Hermes pairing. Behavior depends on `_normalize_unauthorized_dm_behavior` from `gateway/config.py:59+`:

- `"pair"` — when an unknown user DMs the bot, send them a pairing message; they must respond with a one-time code to be authorized
- `"ignore"` — silently drop unknown DMs
- `"reply"` — reply with a "not authorized" message

This is *crucial* for any messaging deployment. The bot's token is public-ish (anyone who finds it can DM the bot). Without pairing, the bot would respond to anyone. The pairing flow lets the operator's *first* DM bind them as an authorized user.

`gateway/whatsapp_identity.py` does WhatsApp-specific identity canonicalization (phone number normalization, BCC ID matching).

---

## 6. The Memory Monitor

`gateway/memory_monitor.py` watches RAM usage of the gateway daemon. When it crosses a threshold:

1. Trigger LRU eviction of the agent cache below the watermark
2. Force memory provider flushes
3. Log a warning

This is one of the *few* places in Hermes where memory pressure is actively managed. Most of Hermes assumes it has plenty of RAM. The gateway makes no such assumption — it runs as a daemon, possibly for days, with N concurrent sessions, each holding a `AIAgent` that holds tool schemas and a memory provider and a message history.

For Ember (Pi target), this kind of active memory monitoring is *exactly* the discipline needed even outside a gateway context. Worth porting the *pattern* (memory monitor with thresholds and reactive eviction) even though the *use case* (multi-platform gateway) is out of scope.

---

## 7. The Mirror

`gateway/mirror.py` lets the operator's gateway sessions appear in the CLI in real-time. When a Discord user DMs Hermes, the operator sees the conversation echoed in their terminal. They can also *type* into the CLI and have their words sent through the gateway as if they were the bot. This is useful for *debugging* the bot from your own terminal.

This is a small but elegant pattern — *one mouth, many ears, optional one extra mouth* (the operator's).

---

## 8. The Runtime Footer

`gateway/runtime_footer.py` produces a one-line "runtime status" appended to messages: model name, latency, cost, token count, current cwd. Toggleable via config (`display.runtime_footer`).

This is the gateway's *honesty patch* — the agent says "Here's your answer" and the footer says "...generated by gpt-5 in 4.2s for $0.003, in /home/operator/projects/foo." The user knows what just happened. **Vow of Public-Friendliness in code.**

---

## 9. The Shutdown Forensics

`gateway/shutdown_forensics.py` makes the gateway log *why* it shut down. When the daemon dies — SIGTERM, OOM kill, panic exception, network adapter failure — the forensics module attempts to write a structured record of the last-known state so the operator can diagnose.

For Ember's slice plan, this is exactly the kind of *gracefully-name-your-death* discipline that aligns with the Vows.

---

## 10. The Platform Registry

`gateway/platform_registry.py` is the lookup layer: "given the string `'telegram'`, what adapter class do I instantiate?" The registry is populated at module load. Plugin platforms register themselves at the same registry through the plugin context (`ctx.register_platform()` per `gateway/platforms/ADDING_A_PLATFORM.md:7-11`).

This is the platform analogue of `tools/registry.py` — a single discovery surface, lazy enough that platforms whose deps aren't installed don't break the import chain.

---

## What This Means for Ember

The gateway is the most *explicitly out-of-scope* part of Hermes for Ember. The Vow of Smallness rules out shipping thirty platform adapters on a Pi. The Vow of Public-Friendliness is *better served* by Ember being a single-user agent that doesn't need a multi-tenant pairing flow. The Vow of Modular Authorship is honored *more strictly* by not having a daemon with thirty concurrent failable subsystems.

**But** there are six patterns Ember should harvest:

1. **The `SessionSource` shape as a typed value for "where am I?".** Even when Ember has only one surface (CLI), name it explicitly. The agent should know whether the current input is from `cli`, `voice`, `bridge` (future Strengr-side surface), etc. A two-field `SessionSource(surface, user_id)` is enough today and scales when surfaces multiply.

2. **The LRU cache + idle TTL pattern from `_AGENT_CACHE_MAX_SIZE = 128` and `_AGENT_CACHE_IDLE_TTL_SECS = 3600.0`.** Ember is single-user, so the cap is 1. But the *idle-TTL* matters: an Ember session left running overnight should release memory by tearing down its in-process state and lazily reconstructing on next message. Cite `gateway/run.py:62-66`.

3. **The memory monitor pattern from `gateway/memory_monitor.py`.** On a Pi 5 (8GB) the difference between "Ember works" and "OOM kill" is decisive. A small background task that watches RSS, logs thresholds, and triggers cleanup is exactly the discipline the Vow of Smallness needs. Cite this pattern; port it even though the gateway is not.

4. **The shutdown forensics pattern from `gateway/shutdown_forensics.py`.** When Ember crashes, the operator should find a `~/.ember/logs/last_crash.log` with: panic exception, last session id, last Funi-Strengr-Brunnr status, last tool call. This is the **Vow of Honest Memory** applied to the agent's own death.

5. **The protocol-quirk discipline from `gateway/platforms/base.py:114-145`.** When Ember acquires a non-CLI surface (TUI, voice, future Strengr-side surface), each surface has its own length limit and formatting quirks. Absorb the quirks in a base class, never sprinkle them in surface implementations.

6. **The runtime footer pattern from `gateway/runtime_footer.py`.** Even on Ember's CLI, a `--verbose` mode that appends *"...generated by phi3:mini in 3.1s, well: connected (pgvector, 35682 chunks, 12 citations)"* is exactly the **Vow of Tethered Grounding** in surface form. The operator sees what really happened.

### Concrete proposals

1. **Refuse the gateway whole.** Ember slice plan should explicitly state: no multi-platform messaging in slice 1-N. The Three Realms have no room for a Telegram adapter. If Ember ever acquires this, it ships as a separate package (`ember-gateway`) that depends on `ember` but is not bundled.

2. **Adopt the patterns named above (sessions / LRU / memory monitor / forensics / quirks / footer) as Strengr-side or Munnr-side disciplines.** Each is small. Each is portable. None requires the daemon shape.

3. **Document the gateway anti-pattern in `[[10_domain/19_BOUNDARY_LAW]]`: the two-guard intercept.** When Ember adds slash-command interrupt handling (for Ctrl-C during a streaming reply), there should be *one* guard, not two. The Hermes pattern is a cautionary tale.

**Affected True Names:** **Munnr** (gains a typed `SessionSource`), **Strengr** (gains forensics + memory monitor patterns). **No new True Name needed** — the gateway is a *role* Ember does not play.

**Vows reinforced by refusing the gateway:** **Vow of Smallness**, **Vow of Modular Authorship**, **Vow of Public-Friendliness** (single-user is friendlier than multi-tenant).

**Vows reinforced by harvesting the patterns:** **Vow of Honest Memory** (forensics), **Vow of Smallness** (memory monitor + LRU eviction), **Vow of Graceful Offline** (shutdown forensics applies on any death).

Many tongues are not a virtue when one is enough. Ember's single tongue, spoken clearly, will outlive any thirty. The gateway is a marvel of engineering — and a refusal Ember must make consciously.

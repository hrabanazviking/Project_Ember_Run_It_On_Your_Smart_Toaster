---
codex_id: 59_CONFIG_DRIFT
title: Config Drift — The Long-Tail Surface Of settings_template.json
role: Auditor
layer: Verification
status: draft
sap_source_refs:
  - config/settings_template.json:1-607
  - py/get_setting.py:1-80
ember_subsystem_targets: [Funi, Hjarta]
cross_refs:
  - 50_verification/53_SECURITY_REVIEW
  - 50_verification/56_PRIVACY_BOUNDARIES
  - 50_verification/57_FAILURE_TAXONOMY
  - 20_interface/26_IM_BOT_INTERFACE
---

# Config Drift — The Long-Tail Surface Of settings_template.json

> *Sólrún, voice cold and even: a configuration surface is also a contract. SAP's `settings_template.json` is 607 lines of contract — a hundred enabled-flags, a thousand string fields, two naming conventions, a dozen credential sinks, and several lurking defaults that will surprise the operator. This document audits the contract and ranks the surprises.*

The configuration surface of any agent system is the API the operator uses to commit to a deployment. Misconfigurations produce silent failures; defaults shape what the operator *thinks* they are running. This document walks the SAP settings template line by line in the areas of highest risk.

`settings_template.json` lives at `/tmp/super-agent-party/config/settings_template.json`. It is 607 lines, 65+ top-level keys, deeply nested.

---

## 1. The Top-Level Surface — Inventory

The 65+ top-level keys, grouped:

**Core LLM and chat:**
- `conversationId`, `isdocker`, `system_prompt`, `SystemPromptsList`, `model`, `base_url`, `api_key`, `temperature`, `max_tokens`, `max_rounds`, `selectedProvider`, `top_p`, `reasoning_effort`, `enableOmniTTS`, `omniVoice`, `extra_params`

**System / proxy / locale:**
- `systemSettings`, `mainAgent`

**Tools and MCP:**
- `mcpServers`, `llmTools`, `tools` (with 14 sub-flags)

**Per-feature sections (each enabled-flag-gated):**
- `fast`, `reasoner`, `vision`, `webSearch`, `targetLangSelected`, `knowledgeBases`, `KBSettings`, `modelProviders`, `agents`, `a2aServers`, `textFiles`, `imageFiles`, `videoFiles`, `memories`, `memorySettings`
- `codeSettings`, `CLISettings`, `acpSettings`, `visionControlSettings`
- `ccSettings`, `qcSettings`, `dsSettings`, `localEnvSettings`, `ocSettings`
- `HASettings`, `chromeMCPSettings`, `sqlSettings`, `custom_http`
- `qqBotConfig`, `WXBotConfig`, `feishuBotConfig`, `wechatBotConfig`, `weComBotConfig`, `dingtalkBotConfig`, `telegramBotConfig`, `discordBotConfig`, `slackBotConfig`
- `VRMConfig`, `comfyuiServers`, `comfyuiAPIkey`, `BotConfig`
- `workflows`, `stickerPacks`
- `liveConfig`, `loveSettings`
- `currentLanguage`, `isBtnCollapse`, `showHistorySidebar`, `is_sandbox`, `showBrowserChat`, `searchEngine`, `isGroupMode`, `selectedGroupAgents`
- `behaviorSettings`, `allBriefly`, `isForceScrollToBottom`, `text2imgSettings`, `asrSettings`, `ttsSettings`
- `largeMoreButtonDict`, `smallMoreButtonDict`

That's a long list. Approximately **300+ named configuration options** across the file.

The first finding: **the configuration surface is large enough that no operator can reasonably understand it.** UX-wise, this is a maintainability problem; operationally, it is a security problem (operators leave defaults in place because there are too many).

---

## 2. The Naming-Convention Mismatch

Already noted in [[26_IM_BOT_INTERFACE]] §3.1. Here, the JSON view:

`settings_template.json:265-274` — `qqBotConfig`:
```json
"qqBotConfig": {
  "QQAgent":"super-model",
  "memoryLimit":30,
  ...
  "reasoningVisible": false,
  "quickRestart": true,
  ...
}
```

`settings_template.json:531-541` — `discordBotConfig`:
```json
"discordBotConfig": {
  "token": "",
  "llm_model": "super-model",
  "memory_limit": 30,
  ...
  "reasoning_visible": true,
  "quick_restart": true,
  ...
}
```

Five Chinese-platform bot configs use `camelCase`. Two Western-platform configs (Discord, Slack) use `snake_case`. The deserializers must handle both. Maintainers adding a field on one side often forget the parallel field on the other side.

A schema-by-class would catch this. The JSON has no schema.

---

## 3. The Defaults That Surprise

### 3.1 `enable_tts: true` for Discord, `false` everywhere else

`settings_template.json:538` — Discord `enable_tts` default not in template (the field is in the Pydantic config at `discord_bot_manager.py:29` with `enable_tts: bool = True`). Telegram default `enableTTS: False`. Slack default `enable_tts: False` (per `settings_template.json:551`).

Discord users who deploy with default-on TTS hear the bot voice in voice channels — which may be unexpected.

### 3.2 `reasoning_visible: true` for Discord and Slack

`settings_template.json:536,547`:

```json
"reasoning_visible": true,
...
"reasoning_visible": true,
```

Discord and Slack default to showing reasoning. In multi-user platforms. As cataloged in [[56_PRIVACY_BOUNDARIES]] §10, this exposes internal model reasoning to every chat participant. The default is wrong on privacy grounds.

QQ, WeChat, WeCom, Feishu, DingTalk all default `reasoningVisible: false`. The asymmetry is a smell — likely the field was added to the older Chinese configs as off-by-default and the newer Western configs flipped without rationale.

### 3.3 `quickRestart: true` everywhere

A "quick restart" command exposed in chat. The exact behavior varies per platform. In a multi-user chat (Discord, Slack), any user can trigger it. There is no per-user permission check on this command — by default. The operator's bot can be restarted by any user who knows the command syntax.

### 3.4 `is_sandbox: false` for QQ bot

`settings_template.json:273`:

```json
"is_sandbox": false
```

QQ's bot infrastructure has a sandbox (test) mode and a production mode. Default is production. A new operator running their first test sends real messages through the production QQ network.

### 3.5 The `loveSettings` default prompt

`settings_template.json:599-606`:

```json
"loveSettings": {
  "enabled": false,
  "dimensions": ["love", "familiarity"],
  "prompt": "请根据用户的发言态度、情感色彩以及你的角色设定，动态管理以下羁绊数值：\n1. love（好感度）：代表你对用户的喜爱与亲密度。如果用户表达善意、关心或与你互动愉快，请增加（+1至+5）；如果用户冷漠、辱骂或做出让你反感的行为，请降低（-1至-5）。该数值最大为50，最小为-50。\n2. familiarity（熟悉度）：代表你与用户的了解程度。随着交流次数的增多和彼此信息的分享，该数值应缓慢稳步上升（每次+1至+2），通常不会下降。该数值最大为100，最小为0。..."
}
```

A 600-character system prompt addition. The prompt directs the LLM to *track and update* affection numerically. When enabled, this prompt is *appended to every LLM request* on every platform. The operator may not realize their carefully-crafted persona is being supplemented by this prompt at every turn.

The prompt is in Chinese. An English-speaking operator may not even read what they're enabling.

### 3.6 `network: "local"` and the bind address

`settings_template.json:21`:

```json
"network":"local",
```

Default is "local" — bind 127.0.0.1. Operator must change to expose. This is the correct default and a positive teaching.

### 3.7 `proxyMode: "system"` and `isChinaProxy: false`

`settings_template.json:22-24`:

```json
"proxy": "http://127.0.0.1:7890",
"proxyMode": "system",
"isChinaProxy": false
```

`proxy` defaults to a Clash-style local proxy at 7890. If the operator has Clash running, this works. If not, *system* mode falls back to OS proxy settings. The `isChinaProxy` flag changes routing behavior for vendors that need a different proxy strategy for China-hosted vs non-China endpoints.

The proxy defaults bake an assumption about the operator's network setup. Non-Clash users may see confusing proxy errors.

### 3.8 `mcpServers: {}` empty default

`settings_template.json:27`:

```json
"mcpServers": {},
```

No MCP servers configured. Reasonable default. But: the moment the operator adds one, the unauth-localhost-API problem in `[[53_SECURITY_REVIEW]]` §8.2 means anyone on loopback can edit the MCP server list and trigger arbitrary subprocess spawn.

---

## 4. The Long-Tail Credential Sinks

The settings file contains credential fields for:

- 3 LLM provider patterns (main, fast, reasoner — each with api_key)
- Knowledge base (api_key)
- Web search engines (Tavily, Jina, Bing, Google, Brave, Exa, Serper, Bochaai, Firecrawl) — each with its own `*_api_key`
- Code execution (E2B api_key)
- ComfyUI (api_key)
- Home Assistant (api_key)
- QQ (appid + secret)
- WeChat (no direct creds — QR-login session)
- WeCom (bot_id + secret)
- Feishu (appid + secret)
- DingTalk (appKey + appSecret)
- Telegram (bot_token)
- Discord (token)
- Slack (bot_token + app_token)
- Bilibili Open Live (4 separate credential fields)
- YouTube (api_key)
- Twitch (access_token)
- TTS vendors (Azure speech key + region, Volc app+access+resource id, Baidu api+secret, MiniMax api+group, Xunfei app+key+secret, Fish api, Google service account, ElevenLabs api)
- Image hosting (GitHub token, Gitee token)
- SQL (user, password)
- Sherpa, Moss (no creds — local models)

**At least 45 distinct credentials** can live in this one JSON file. Plain text. No encryption.

For an operator who has filled out 20 of those 45, the file is a vault. Lose it (backup leak, accidental commit to public repo, malware on the host) and lose all 20.

---

## 5. The `extra_params` Pattern

`settings_template.json:17`:

```json
"extra_params":[],
```

A free-form extras list passed to the LLM call. Repeated in `fast.extra_params`, `reasoner.extra_params`. The pattern: when something cannot be expressed in the structured schema, dump it into `extra_params`.

This is the escape valve that hides version drift. The operator adds a new OpenAI parameter to `extra_params`; the LLM call passes it through; eventually the parameter is renamed by OpenAI; the call fails; the operator must edit `extra_params` to keep up.

Better: typed parameter declarations that fail loudly on rename.

---

## 6. The Toggleable Tools Wall

`settings_template.json:29-76` — `tools` block:

```json
"tools": {
  "asyncTools": {"enabled": false},
  "a2ui": {"enabled": false},
  "time": {"enabled": false, "triggerMode": "beforeThinking"},
  "weather": {"enabled": false},
  "wikipedia": {"enabled": false},
  "arxiv": {"enabled": false},
  "hideToolResults": {"enabled": false},
  "getFile": {"enabled": false},
  "language": {"enabled": false, "language": "", "tone": ""},
  "inference": {"enabled": false},
  "deepsearch": {"enabled": false},
  "formula": {"enabled": false},
  "autoBehavior": {"enabled": false},
  "randomTopic": {"enabled": false, "baseURL":"https://topics-after-party.zeabur.app"}
}
```

14 sub-tools, each independently togglable. The operator must reason about each. Each tool's enable flag changes the tool set available to the LLM. The LLM in turn changes its behavior based on what tools it has.

The cost: 14 boolean axes is 2^14 = 16,384 configurations. The operator probably tries 2-3 and ships with whichever felt good. The other 16,000+ are untested.

---

## 7. The Tier Mismatch — `largeMoreButtonDict` vs `smallMoreButtonDict`

`settings_template.json:380-445` — two parallel UI configurations: "large screen" buttons and "small screen" buttons. Each lists ~30 buttons with enabled-flags. Many buttons differ between the two — e.g. `desktopVisionButton` is `false` for large and `true` for small.

The "small" mode appears to be a mobile-optimized layout. Why mobile defaults to `desktopVision: true` is unclear — there is no desktop on a phone. This is likely a label mismatch left from a refactor.

The duplication means: a button added must be added in two places. Maintenance burden compounds.

---

## 8. The Schema-Free Validation Problem

`get_setting.py:1-80` (read in [[20_interface/29_TOOL_TYPE_INTERFACE]] context) shows the settings loader. It reads JSON, returns dict. There is no Pydantic schema for the whole settings document — there are per-feature Pydantic models (e.g. `QQBotConfig` in `qq_bot_manager.py:22`) but they validate slices only when those slices are passed to the relevant API.

A settings file with a typo in `qqBotConfig.appid` → `qqBotConfig.appId` (capitalized D) is *silently accepted*. The bot fails to start when QQBotConfig parses; the user sees "missing field appid"; the user looks at the JSON, sees `appId`, fixes; restarts.

Round-trip cost per typo: minutes. Multiplied by 45 credential fields, 300+ options.

A schema-validating loader would catch this at load time and name *which* field is misnamed.

---

## 9. The Per-Section Migration Problem

When SAP adds a new field to `qqBotConfig`, what happens to existing settings.json files that pre-date the new field?

Most cases: the Pydantic model's default value applies (`memoryLimit: int = 30` in `QQBotConfig`). New field is filled with default. No problem.

Edge case: the new field has *no default* and is required. The user's existing config fails to validate. SAP doesn't run.

`telegramBotConfig` example: `bot_token: str` (no default in `telegram_bot_manager.py:14`). A user with no Telegram set up doesn't have a `bot_token` in their config. If SAP code asks Pydantic to validate `TelegramBotConfig(**settings["telegramBotConfig"])` unconditionally, it fails.

In practice, SAP gates the validation behind enable-flags — config is only parsed when the bot is started. So missing required fields cause a startup error rather than a load error. Better UX than the alternative, but the inconsistency between "validated at startup" and "validated at load" leads to inconsistent error timing.

---

## 10. The Behavior Settings Are Not Schema-Documented

`settings_template.json:277-280`:

```json
"behaviorSettings": {
  "enabled": false,
  "behaviorList":[]
}
```

`behaviorList` is an array of objects matching `behavior_engine.py:23-49` `BehaviorItem`. The template doesn't show the shape. An operator hand-editing settings.json has to read Python source to know what to put.

This is a documentation gap, not a code defect — but it widens the surface where typos happen.

---

## 11. Cross-References

- [[53_SECURITY_REVIEW]] — credential trove rooted in this file
- [[56_PRIVACY_BOUNDARIES]] — reasoning visibility defaults, image-host defaults
- [[57_FAILURE_TAXONOMY]] — F-09 (credential trove), F-36 (reasoning defaults), F-42 (naming convention)
- [[26_IM_BOT_INTERFACE]] — drift between platforms surfaces in this config
- [[hermes:HEM-13_CONFIG]] — Hermes's config discipline as positive counter

---

## What This Means for Ember

**Adopt:**
- Adopt the **per-feature `enabled` flag** as the gate to deeper configuration. Surface-area reduction by gating is a real win.
- Adopt the **`localhost-only by default`** posture from `network: "local"`. Outbound exposure is opt-in.

**Adapt:**
- Adapt the long-tail settings template into a **Pydantic schema** that validates the entire file at load. Errors name the offending field. Operators get clear diagnostics. SAP's silent typo-tolerance is the negative template.
- Adapt the per-feature toggles into **PerformanceTier-aware defaults**. A Pi tier ships with most heavy features disabled; workstation ships with them enabled. Operator doesn't have to flip 30 switches.

**Avoid:**
- **Avoid 600+ line single JSON config files.** Per-feature config files (`config/llm.toml`, `config/im_bots.toml`, `config/livestream.toml`) — smaller, focused, reviewable per PR.
- **Avoid mixed naming conventions in one file**. Snake_case everywhere. Migration adapter handles legacy SAP-style camelCase.
- **Avoid required fields without defaults** in any sub-config. Defaults that produce a no-op behavior on missing config keep startup graceful.
- **Avoid plaintext credential fields in any config file.** Credentials stored in OS keyring; config files reference them by name. The file is safe to share for debugging.
- **Avoid 14-tool enable-flag matrix.** Group related tools into capability profiles: `tool_profile: "minimal" | "research" | "creative"`. Operator picks a profile; the profile expands.
- **Avoid system-prompt-extension-via-config** (`loveSettings.prompt`). System prompt is typed and known; auxiliary instructions are *separate fields*, not concatenations.
- **Avoid hardcoded URLs to third-party services** (`https://topics-after-party.zeabur.app` in `settings_template.json:74`). Either bundle the service locally, or document that this URL is third-party.
- **Avoid `extra_params` as escape valve.** Versioned parameter schemas with explicit forward-compat behavior.

**Invent:**
- **Settings Schema with `ember validate-config`.** A CLI command that loads the schema and validates the operator's config file. Diagnostics name fields, line numbers, expected vs actual. Vow of **Public-Friendliness** at the config layer.
- **Credential Vault Reference.** Config fields that hold credentials are actually *references*: `"api_key": "@vault:openai_main"`. The vault is the OS keyring (Linux: secret-service; macOS: Keychain; Windows: Credential Manager). Config files are safe to share; vault is per-host.
- **PerformanceTier Auto-Config.** On first run, Ember asks "what is your deployment?" and offers presets (Pi / laptop / workstation / multi-GPU / server). Each preset is a validated config. Operator can deviate per-field. No starting-from-blank.
- **Settings Migration Script Per Version.** Every Ember release that changes settings ships a migrator: `ember migrate-config --from 1.2 --to 1.3`. Operators run it on upgrade. No silent breakage.
- **Settings Audit Diff.** `ember config-diff` shows the operator how their current config differs from defaults. Highlights credential fields. Highlights deviations from recommended posture (e.g. "reasoning visibility enabled on Discord — privacy concern").
- **Settings Schema Generation From Code.** Pydantic models are the source of truth; the settings template is *generated* from them. No drift between code expectations and JSON template. SAP's hand-maintained template is the negative template.
- **Per-Subsystem Capability Profile.** Instead of "enabled: true/false" per individual tool, declare `capability_profile` per subsystem: `Munnr.profile = "full_presence" | "text_only" | "log_only"`. Profiles expand to feature sets. Tier-and-profile is two axes; tool-by-tool is N axes.
- **Config Documentation Coverage Test.** Every field in the Ember settings schema has a corresponding entry in `CONFIG_REFERENCE.md`. CI checks coverage. SAP's "go read Python source" pattern is the negative template.

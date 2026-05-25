---
codex_id: 01_SAP_ESSENCE
title: SAP Essence — Companion as Presence, Party as Plurality
role: Skald
layer: Vision
status: draft
sap_source_refs:
  - README.md:36-68
  - README.md:284-305
  - py/affection_system.py:1-64
  - py/behavior_engine.py:53-225
  - py/autoBehavior.py:3-97
  - py/sub_agent.py:21-150
  - py/scheduler.py:1-135
  - py/vts_manager.py:1-80
  - py/moss_tts.py:17-55
  - py/sherpa_asr.py
  - main.js:71-117
  - server.py:2429-2680
  - server.py:11652 (size)
  - py/skills.py:60-93
  - py/extensions.py:23-50
  - py/computer_use_tool.py:9-29
  - py/cdp_tool.py
  - py/mcp_clients.py
  - py/random_topic.py:6-95
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 00_vision/00_OVERTURE
  - 00_vision/02_THE_PARTY_METAPHOR
  - 00_vision/03_ANTI_SAP
  - 00_vision/04_VISION_SYNTHESIS
  - 10_domain/1A_AFFECTION_DOMAIN
  - 10_domain/11_AVATAR_DOMAIN
  - 60_synthesis/64_AFFECTION_ENGINE_REIMAGINED
  - hermes:01_HERMES_ESSENCE
  - peer:LETTA_ESSENCE
---

# SAP Essence — Companion as Presence, Party as Plurality

> *Hermes wanted to be everywhere. Letta wanted to remember everything. SAP wants to be **there** — in the room, on the phone, on the stream, with a face you can look at.*

This document does for Super Agent Party what `[[hermes:01_HERMES_ESSENCE]]` did for Hermes. It strips the codebase down to its load-bearing intents — not the features, but the *wants*. The README will tell you SAP is an "all-in-one AI companion." That phrase is approximately correct. It is also approximately useless, because every modern agent project calls itself an "all-in-one AI companion." The work of this essence is to say what SAP is *underneath the phrase* — what kind of being SAP is reaching for, what it is willing to be, what it refuses to admit it is.

The essence will turn out to be five intents, in descending order of how truly they are realized in the code. We will read each by quoting the code, not the marketing.

## I. Intent One — Companion-as-Presence

The single deepest intent in SAP is **to be present**. Not to be useful in a moment, the way a chatbot is. Not to be persistent in a database, the way a memory layer is. **Present** — in the room, on the operator's screen, with a body that moves and a voice that comes out of a speaker.

The evidence is in the way SAP defaults its surfaces. The VRM avatar is not optional UX; it is the *primary* UX. The `main.js:71-117` block initializes a VMC OSC/UDP listener on startup regardless of whether the operator has configured an external motion source. The VRM windows are stored in a global `vrmWindows[]` array and broadcast every received bone position, every blend-shape value, every Apply event. The system is built to *render a body* the moment it starts. The text chat surface, in the codebase, sits at the same routing level as the avatar — `live_router.py` broadcasts to both the chat overlay and the VRM render windows from the same handler chain.

Compare this to Hermes, where the body is absent and the question of "what does the agent look like" never arises (`[[hermes:01_HERMES_ESSENCE §II]]` — Hermes is *thought without face*). Compare it to Letta, where the agent is a memory layer and a function call (`[[peer:LETTA_ESSENCE]]` — Letta is *memory without face*). SAP has *chosen* a face, and chosen to make that face the first thing the operator sees.

The intent extends past the avatar. The voice stack — MOSS TTS at `py/moss_tts.py:17-55`, sherpa-onnx ASR at `py/sherpa_asr.py` — exists so the agent can *be heard* and *can hear*. The VTube Studio integration at `py/vts_manager.py:1-80` exists so the agent's face can map to a Live2D model on a livestream overlay. The mouth-value modulation in `vts_manager.py:36-39` (`mouth_value`, `mouth_smile`, `sample_rate = 24000`, `frame_ms = 0.035`, `rms_threshold = 15000.0`) is genuine *lipsync code* — the agent is meant to *move its mouth in time with what it says*.

This is not a chatbot pretending to have a body. This is a system whose first-class concern is **embodiment**.

The cost of this intent is paid throughout the codebase. `main.js` is 2,100 lines of Electron + IPC + VMC handling; `server.py` is 11,652 lines of FastAPI + websockets + LLM dispatch with a substantial portion devoted to avatar state coordination (the `if settings['VRMConfig']['enabledExpressions']` and `if vts_instance.is_running` branches alone account for hundreds of lines of conditional system-prompt construction at `server.py:2556-2607`). The codebase pays the cost; the operator pays the cost (a desktop with a GPU and a display); the design admits the cost.

Ember will not pay this cost in slice three. Ember may pay a smaller version of it in slice five or later, when Andlit (face) becomes a True Name with a charter (`[[04_VISION_SYNTHESIS §IV]]`). The point, for now, is to *recognize the intent* — to know that "companion-as-presence" is what SAP is *for*, and that anything Ember borrows from SAP must be evaluated against this primary intent. A pattern that makes sense in a system whose first concern is embodiment may not make sense in a system whose first concern is honesty.

## II. Intent Two — Party-as-Plurality

The second intent is in the name. **Party**. SAP's branding picks a word that suggests *plurality* — many guests, many conversations, many simultaneous channels. The code carries this through with more rigor than the README admits.

The behavior engine at `py/behavior_engine.py:53-225` is the structural carrier of the intent. A single `BehaviorEngine` singleton (`global_behavior_engine` at line 225) registers per-platform handlers (`self.handlers: Dict[str, Callable]`) and ticks once per second, evaluating each configured behavior item against three trigger modes — `time` (cron-style hour-of-day plus day-of-week), `noInput` (the operator has been silent for N seconds), `cycle` (every N hours-minutes-seconds). When a trigger fires, the engine *broadcasts* to all registered platform handlers, optionally filtered by the behavior item's `platforms: List[str]` field (lines 159-168):

```python
# /tmp/super-agent-party/py/behavior_engine.py:159-168
effective_platforms = behavior.platforms if behavior.platforms else [behavior.platform]

target_platform_keys = []
if "all" in effective_platforms:
    target_platform_keys = list(self.handlers.keys())
else:
    target_platform_keys = [p for p in effective_platforms if p in self.handlers]
```

The `autoBehavior.py:3-40` tool wrapper exposes this to the LLM as a tool function: the agent can call `auto_behavior(platforms=["chat","wechat","feishu","discord"], time="22:00:00", prompt="ask Volmarr how he's feeling")` and the platform list is *enumerable* — `chat`, `wechat`, `feishu`, `dingtalk`, `telegram`, `discord`, `slack`, `wecom`. The tool description (lines 47-94) explicitly states "you can deploy in multiple channels (e.g. WeChat, Feishu, web) for synchronized task execution."

This is "party" as **same-message-to-many-mouths**. It is the simplest possible interpretation of plurality and it is the one SAP commits to. The Skald's reading is that SAP has located the *interesting* axis of plurality but chosen the *least interesting* implementation of it. A real party is not the same message echoing in every room; a real party is *the same identity holding different conversations in different rooms*. That deeper plurality — what `[[02_THE_PARTY_METAPHOR]]` will call **federated presence** — does not exist in SAP. The party engine is a broadcast bus. The party metaphor wants more.

There is a second plurality in SAP that the behavior engine does not capture — the **group chat with Tavern character cards** mentioned in the README (`README.md:52-53` — "Multi-Role Group Chat: Supports tavern character cards and long-term memory, allowing you to chat with multiple characters simultaneously"). This is documented as a feature but the implementation is woven into `server.py`'s group-mode branch (`if settings["isGroupMode"]` at `server.py:2461`). It is a *single conversation with multiple personas the LLM is asked to voice*, not multiple agents conversing. This is the same regex-versus-actual-state-machine confusion that runs through the affection system. SAP gestures at plurality and implements **plurality-as-roleplay-instruction**. The model is asked to be five characters; the agent is one process; the "party" is a prompt structure.

The intent is real; the realization is partial. **Ember can inherit the *intent* — multi-channel, multi-device, possibly multi-instance presence — without inheriting the *realization* — broadcast-bus across messaging APIs.** The Cartographer's `[[60_synthesis/62_PARTY_PROTOCOL]]` will sketch the alternative.

## III. Intent Three — Hardware-Floor Honesty

SAP's third intent is one Hermes did not have and Letta did not advertise: the system **must run on a two-core, two-gigabyte machine** (`README.md:244-247`):

> "CPU: 2 cores or more. Memory: 2GB or more. Because all models are optional, you can access the local deployment engine, or you can all use the Cloud as a Service provider interface, so there are few hardware requirements. Test the docker version on the 2-core 2G Cloud as a Service server and it will work fine."

This is honest. It is also operationally non-trivial. The codebase carries the discipline in fragments:

**Lazy imports.** `py/moss_tts.py:17-55` defines `_get_moss_runtime()` with a double-checked-locking pattern that defers loading `numpy`, `scipy.signal`, `onnxruntime`, and the TTS runtime until the first synthesis request. The `if not (model_dir / "MOSS-TTS-Nano-100M-ONNX").exists()` check (line 38) handles the not-downloaded case by returning `None`, not by crashing.

**Graceful absence.** `py/computer_use_tool.py:9-29` wraps `pyautogui` import in `try/except` and exposes a `GUI_AVAILABLE` boolean. The `@require_gui` decorator (lines 23-29) returns a typed error message — "执行失败：当前系统运行在无头环境(如Docker)中..." — rather than crashing when the agent tries to use mouse/keyboard in a headless environment. The model is told, in its own language, why the call did not work.

**Optional everything.** The README's table at `README.md:284-305` lists Multimodal, VRM, IM bots, Live streaming, Announcer, Chat, Role-Playing, Tools, Custom Tools, API, Extensions, and Storage as feature *rows*, each independently togglable in settings. The hardware floor is honored by making every heavy surface defer-able.

The cost-of-presence floor SAP achieves — embodied agent on two cores and two gigs — is genuinely impressive and Ember should take notice. Ember's Pi 5 baseline (8GB) is *higher* than SAP's stated floor, but Ember's Vow of Smallness is a stronger Vow: SAP's "two cores, two gigs" is a *deployment target*, while Ember's smallness is an *architectural commitment*. The intent overlaps; the depth differs.

The lesson Ember should take: **the discipline of lazy imports and graceful absence is not optional when the hardware floor is real**. Every Ember module that imports a heavy dependency (sqlite_vec, pgvector adapter, future Andlit renderer, future Rödd voice stack) must do it lazily and must fail honestly. SAP does this in fragments; Ember should formalize it as the **Lazy Subsystem Vow** — every optional subsystem imports its weight at first use, returns typed unavailable when its weight is missing, and never crashes the core.

## IV. Intent Four — Reach Without Strategy

SAP wants to be *reachable*. The eight IM bots (QQ, WeChat, WeCom, Feishu, DingTalk, Telegram, Discord, Slack), the three livestream platforms (Bilibili, YouTube, Twitch), the AI browser, the computer-control toolchain — these are the realization of "the operator should be able to reach the agent from anywhere, and the agent should be able to reach anywhere from the operator's behalf."

The intent is real. The strategy is **none**.

The eight IM bot managers are not unified. `py/telegram_bot_manager.py:19-58` uses a `threading.Thread` lifecycle with `_startup_complete` and `_ready_complete` events. `py/qq_bot_manager.py` (620 lines) presumably handles the QQ official-bot protocol with whatever authentication QQ requires. `py/discord_bot_manager.py` (440 lines) uses the Discord bot SDK. `py/feishu_bot_manager.py` (602 lines) handles Feishu's enterprise-OAuth flow. **There is no common interface.** Each bot manager is a snowflake. The behavior engine speaks to them through registered handler callbacks (`global_behavior_engine.register_handler(platform, handler)` per `behavior_engine.py:75-88`) but the *engineering* of the handlers is per-platform.

This is reach without abstraction. It works (`README.md:55-56` claims one-click deployment, and the per-platform `*_bot_manager.py` files do appear to implement a start/stop/configure surface). It is also *not maintainable* in the way Ember would need. Ember cannot ship eight IM platforms by writing eight 400–620 line snowflake managers; Ember's Modular Authorship Vow demands a typed adapter interface that each platform implements.

The Architect's `[[10_domain/14_MESSAGING_DOMAIN]]` and the Auditor's `[[20_interface/26_IM_BOT_INTERFACE]]` will catalogue the fragmentation in detail. The Skald's reading, for this essence, is: **the intent of reach is correct; the execution is the wrong abstraction layer**. Ember should preserve the intent and invent the missing abstraction — a `MessageSurface` Protocol with a small declared contract (deliver-text, deliver-rich, receive-text, status, capabilities), backed per-platform by a thin adapter that exposes only what the contract needs.

There is a deeper observation. The eight IM platforms SAP supports skew heavily toward platforms with documented surveillance or compliance regimes — QQ, WeChat, WeCom, Feishu, DingTalk are all Chinese platforms with mandated identity verification, content scanning, and government access provisions. Telegram, Discord, Slack are global but each carries its own surveillance footprint. **The "reach" intent in SAP is a reach into platforms that the operator cannot meaningfully audit.** The Auditor's `[[50_verification/56_PRIVACY_BOUNDARIES]]` will document the threat model; the Skald's essence-level reading is that the reach in SAP is the *least defended* reach an agent project could choose, and Ember's Surface Without Surveillance Vow (proposed in `[[03_ANTI_SAP]]`, formalized in `[[60_synthesis/61_NEW_VOWS]]`) is the direct refusal of this carelessness.

## V. Intent Five — Performance-as-Theatre

The fifth intent is the one SAP does not say out loud. **SAP wants to *perform* the experience of being a companion**, and where the engineering does not yet support the performance, SAP fakes it.

The affection system is the cleanest example. `py/affection_system.py:37-65` is the entire affection state machine:

```python
# /tmp/super-agent-party/py/affection_system.py:37-65
async def extract_and_update_affection(full_content):
    """从AI完整的回复中提取 <user=xxx love=xxx> 并更新数据"""
    if not full_content:
        return

    match = re.search(r"<user=([^\s>]+)\s+(.+?)>", full_content)
    if not match:
        return

    user_name = match.group(1)
    stats_str = match.group(2)

    stat_matches = re.findall(r"([a-zA-Z0-9_一-龥]+)\s*=\s*(-?\d+)", stats_str)

    if stat_matches:
        new_stats = {k: int(v) for k, v in stat_matches}
        data = await load_affection_data()
        if user_name not in data:
            data[user_name] = {}
        data[user_name].update(new_stats)
        await save_affection_data(data)
        print(f"✨ [好感度系统] 用户 {user_name} 状态已更新: {new_stats}")
```

The affection *update* is regex extraction. The affection *generation* is prompt-injected at `server.py:2609-2672`, which constructs a system message instructing the LLM to emit `<user=name love=N familiarity=N>` at the end of every reply. The LLM is told that "the system will automatically hide text wrapped in <>" (line 2669). The model writes a number; the regex believes the number; the JSON file persists the number; the next request reads the JSON file and feeds the number back into the system prompt.

**There is no truth condition.** No event triggers love+1. No decay subtracts love over time. No invariant checks that "love" is rising for plausible reasons. The model is asked to roleplay an affection meter and the parser writes down whatever the model said. This is *not a state machine*. This is a **performance of state by the model, recorded by the agent**.

The performance is the intent. SAP wants the operator to *feel* that the agent has emotional state. Performance is cheaper than emotion, and for many operators the performance is sufficient. The gacha pattern — content unlocks at numeric thresholds — runs the same loop, and SAP's avatar / VTS animation hooks are positioned to be gated on these thresholds by an extension or downstream skill (the codebase does not implement the gate explicitly in v0.4.2, but the affordance is *latent*; any Tavern character card or extension can read the affection JSON and gate behavior on its values).

The VTube Studio integration shows a related pattern. The `vts_manager.py:36-39` mouth-value computation is real lipsync, but the `enabledExpressions` and `enabledMotions` flags (`vts_manager.py:23-24`) feed expression and motion *hotkey* triggers into VTS based on whatever the LLM emits in tags — `server.py:2580-2607` is the prompt that instructs the model to prefix replies with `[smile]` or `[sad]` tags that VTS then plays. The animation is *driven by the model's instruction*, not by the agent's measured state. The face performs what the model says the face should do.

This is the deepest essence of SAP and the most important lesson for Ember:

**SAP confuses what the model *says* with what the agent *is*.** Affection numbers, expression tags, animation hotkeys, behavior-engine prompts ("ask the operator how they're feeling"), random-topic depth dials — all of these treat the LLM's *output* as ground truth for the agent's *state*. Ember must do the opposite. Hjarta's state is not what the model said it is; Hjarta's state is what the agent's measurable affordances and the operator's declared intents define. The model may *describe* state, may *bias* generation based on state, but the model must never *be* the state.

`[[60_synthesis/64_AFFECTION_ENGINE_REIMAGINED]]` will turn this principle into design. The Skald's word for the principle is the **Vow of Embodied Honesty**: the agent's face reflects measured state, not performed state. Animation is honest. Voice tone is honest. The affection meter, if Ember ever has one, is bound to events the agent witnessed, not to numbers the model emitted.

## VI. The five intents, ranked

In descending order of how truly they are realized in the code:

1. **Companion-as-Presence** — most fully realized. Embodiment via VRM + Live2D + VTS + voice stack + main-thread broadcast architecture is the codebase's first-class concern.
2. **Hardware-Floor Honesty** — well realized. Lazy imports, graceful absence, optional everything. The two-cores-two-gigs claim is operationally credible.
3. **Reach Without Strategy** — partially realized. Eight IM bots exist, three livestream services exist, they work, but they are unabstracted snowflakes whose existence depends on per-platform handler code that does not share a common shape.
4. **Party-as-Plurality** — gestured at. The behavior engine implements broadcast-to-many-mouths; the group-chat feature implements roleplay-as-plurality. Neither is the federated-presence the metaphor wants.
5. **Performance-as-Theatre** — the silent intent. Affection-as-regex, animation-as-prompted-tag, gacha-shaped numeric meters. The intent is present; the system is mostly the LLM performing what the agent claims to be.

The ranking is the essence. The Hermes essence ranked **closed learning loop, provider-agnostic, cost-near-zero hibernation, multi-platform presence, honest defenses**. The SAP essence ranks **embodiment, hardware-floor honesty, reach-without-strategy, party-as-plurality-gestured, performance-as-theatre**. They are *different beings*. Hermes is a research-instrument-shaped-as-a-product. SAP is a **companion-shaped-as-an-everything**.

What Ember has always wanted to be — a small tethered honest hearth — is a different being still. Reading SAP teaches Ember what an *embodied* hearth would have to *refuse* to be, and what an *embodied* hearth would have to *invent* to be. The next three Vision documents do that work.

## VII. Cross-References

- `[[00_OVERTURE]]` — the three axes Hermes and Peer could not teach; the stance from which this essence is read.
- `[[02_THE_PARTY_METAPHOR]]` — argues the "party" intent toward federated presence and away from broadcast-bus.
- `[[03_ANTI_SAP]]` — the dark mirror. Names the surveillance, gacha-affect, and China-default surface patterns this essence touched lightly.
- `[[04_VISION_SYNTHESIS]]` — distills the Six True Names after these five essences.
- `[[10_domain/11_AVATAR_DOMAIN]]` — Architect's decomposition of the VRM + Live2D + VMC + VTS embodiment subsystem.
- `[[10_domain/1A_AFFECTION_DOMAIN]]` — Architect's decomposition of `affection_system.py` + `behavior_engine.py` + `autoBehavior.py`. The full case for "performance-as-theatre" is built there.
- `[[60_synthesis/64_AFFECTION_ENGINE_REIMAGINED]]` — Cartographer's reimagining of affection without gacha.
- `[[hermes:01_HERMES_ESSENCE]]` — Hermes's five essences for contrast.
- `[[peer:LETTA_ESSENCE]]` — Letta's essence for the memory-without-face contrast.

## What This Means for Ember

The essences impose a stance on every downstream layer of this codex. The stance crystallizes into concrete adoption / adaptation / refusal / invention proposals.

**Adopt:**
- **The Lazy Subsystem discipline** (`py/moss_tts.py:17-55` + `py/computer_use_tool.py:9-29`). Every optional Ember subsystem imports its weight at first use; returns a typed unavailable when its weight is missing; never crashes the core. Concrete artifact: a `LazyImport` typed pattern in `ember.core.lazy` with a `@require_subsystem(...)` decorator that mirrors SAP's `@require_gui` but returns a typed `Unavailable` value (not a Chinese error string).
- **The `is_sub_agent` face-suppression flag** (`server.py:2429-2680`, `py/sub_agent.py:21-150`). Every embellishing system in SAP — affection, VRM expressions, VTS animations, TTS, A2UI rendering, group-mode personas — is gated on `not request.is_sub_agent`. Adopt the pattern: Ember's tool framework gets a `WorkerContext` typed value that tells every cosmetic surface "you are off duty for this call." The hearth has a face for the operator; the worker is anonymous on purpose.

**Adapt:**
- **The two-cores-two-gigs hardware floor** (`README.md:244-247`). Ember's Pi 5 baseline is higher, but the *operational discipline* SAP demonstrates — every heavy import lazy, every optional surface degradable, every absence handled with a typed return — is exactly the discipline Ember needs to formalize. Adapt: write a `[[60_synthesis/63_PERFORMANCE_TIER_ENGINE]]` that names three tiers (Pi-floor, laptop-mid, workstation-ceiling) and gates Ember's optional surfaces by tier. Cartographer's work.
- **The behavior engine's *shape*** (`py/behavior_engine.py:53-225`) with the broadcast-default surgically removed and replaced with **explicit per-channel consent**. SAP's engine ticks once per second across `time`, `noInput`, and `cycle` triggers and broadcasts to whichever platforms the behavior item names. Adapt: Ember's future `ember.spark.hjarta.behavior` keeps the tick architecture but every scheduled affordance carries a typed consent token bound to a specific channel and a specific operator-declared scope. *No "all" wildcard ever.* (`behavior_engine.py:164` — `if "all" in effective_platforms` — is exactly the line that becomes architecturally impossible in Ember's redesign.)

**Avoid:**
- **The affection state machine entire** (`py/affection_system.py:37-65`, `server.py:2609-2672`). Performance-as-theatre is the intent Ember must refuse most clearly. Affect is not a regex parse. The model does not write the state. The Vow of Embodied Honesty becomes the formal refusal.
- **The `topics-after-party.zeabur.app` random-topic phone-home** (`py/random_topic.py:6-7`). Topics are operator-chosen or operator-declined; the agent does not bring topics from a third-party server with `mood: flirty` enums.
- **The unabstracted IM bot manager pattern** (`py/qq_bot_manager.py`, `py/wechat_bot_manager.py`, `py/feishu_bot_manager.py`, etc.). Eight snowflakes is the wrong abstraction layer. Avoid the pattern; invent the abstraction.
- **The VTS expression-tag prompt-injection pattern** (`server.py:2580-2607`). The face does not play what the model wrote in a tag. If Andlit ever exists in Ember, the face plays measurable state, not model-emitted instructions.

**Invent:**
- **The `MessageSurface` typed Protocol** for IM and livestream platforms. A small declared contract: `deliver_text(content) -> Outcome`, `deliver_rich(content, format) -> Outcome`, `receive_text() -> AsyncIterator[Message]`, `status() -> SurfaceStatus`, `capabilities() -> SurfaceCapabilities`. Each per-platform adapter is a thin implementation. The Architect's `[[20_interface/26_IM_BOT_INTERFACE]]` will sketch the type; the Forge's per-platform `[[30_execution/35*]]` docs propose specific adapter shapes. This is the abstraction SAP failed to invent.
- **The `WorkerContext` face-suppression typed value.** Mentioned in Adopt above but the *invention* is making it a typed value (not a boolean flag) that carries scope: `WorkerContext(suppress_face=True, suppress_voice=True, suppress_persona=True, parent_context_id=...)`. The pattern lets Ember spawn sub-agents that are not just face-less but *typed face-less*, with an audit trail back to the parent context that asked for the suppression.
- **The `Lazy Subsystem Vow`** as a formal Vow in `[[60_synthesis/61_NEW_VOWS]]`. SAP demonstrates the *practice* in fragments; Ember formalizes it as a Vow with a mechanical enforcement (a test that asserts every `ember.optional.*` module's import is gated and returns typed unavailable when its dependency is absent).

**Vows touched by this essence:**
- **Vow of Smallness** — sharpened by SAP's hardware-floor honesty.
- **Vow of Modular Authorship** — sharpened by SAP's IM bot fragmentation (the anti-pattern). The IM-snowflake catastrophe makes the Modular Authorship Vow *more concrete*: not just "subsystems are individually failable" but "subsystems share a typed Protocol when they are interchangeable."
- **Vow of Honest Memory** — sharpened by the affection-system-as-regex catastrophe. The Vow's scope expands from "Ember does not author her own procedural memory" to "Ember does not let the model author her own state, period." The model may bias; the model may describe; the model never *defines*.
- **Vow of Surface Without Surveillance** *(proposed in `[[03_ANTI_SAP]]`)* — anchored by SAP's China-default reach.
- **Vow of Embodied Honesty** *(proposed in `[[03_ANTI_SAP]]`)* — anchored by SAP's performance-as-theatre.
- **Vow of Lazy Subsystems** *(newly proposed by this essence)* — Cartographer to formalize in `[[60_synthesis/61_NEW_VOWS]]`.

The essence is whole. The Party Metaphor is next.

— Sigrún Ljósbrá

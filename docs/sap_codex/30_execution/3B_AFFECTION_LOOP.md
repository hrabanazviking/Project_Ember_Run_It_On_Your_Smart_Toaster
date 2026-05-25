---
codex_id: 3B_AFFECTION_LOOP
title: Affection Loop — A Tiny File and a Big Truth
role: Forge
layer: Execution
status: draft
sap_source_refs:
  - py/affection_system.py:1-65 (the entire affection storage)
  - py/affection_api.py:1-30 (CRUD API)
  - py/behavior_engine.py:9-49 (data models)
  - py/behavior_engine.py:53-225 (BehaviorEngine class)
  - py/autoBehavior.py:1-97 (LLM-facing auto_behavior tool)
  - py/scheduler.py:1-134 (AgentScheduler)
  - py/random_topic.py
ember_subsystem_targets: [Hjarta]
cross_refs:
  - 30_execution/35_IM_BOT_DEPLOYMENT_OVERVIEW
  - 10_domain/1A_AFFECTION_DOMAIN
  - 60_synthesis/64_AFFECTION_ENGINE_REIMAGINED
---

# Affection Loop

> *I expected a state machine. I found a JSON file and a regex. The expectation was the bigger story.*

Forge. Eldra. I came to this codebase expecting SAP's `affection_system.py` to be the centerpiece of a gacha-style emotional state machine. The README markets it as "actual emotional state mechanics". What's actually there is **65 lines**: read a JSON file, write a JSON file, and a regex that scrapes affection scores from the LLM's reply text. The full extraction code:

```python
# py/affection_system.py:37-65 (the entire interesting logic)
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

That's it. **The LLM emits a tag in its reply** — `<user=小包 love=12 familiarity=15>` — and SAP greps for the tag, parses the values, writes them to JSON. There is no decay function. There is no smoothing. There is no event-driven trigger. The LLM is the affection engine. SAP is the persistence layer.

This is a much smaller and much more honest design than the marketing implies. It is also a different kind of fragile than I expected. Let me show you what's actually going on.

## The Storage: One JSON File

```python
# py/affection_system.py:7-35 (compressed)
AFFECTION_DIR = os.path.join(USER_DATA_DIR, 'affection')
AFFECTION_FILE = os.path.join(AFFECTION_DIR, 'affection_data.json')

async def load_affection_data():
    if not os.path.exists(AFFECTION_FILE):
        return {}
    def _read():
        with open(AFFECTION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return await asyncio.to_thread(_read)

async def save_affection_data(data):
    def _write():
        with open(AFFECTION_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    await asyncio.to_thread(_write)
```

One file. Read all → mutate dict → write all. Uses `asyncio.to_thread` so the file IO doesn't block the event loop. No locking. No transaction. No incremental update. After 1000 users with 30 stats each, the file is ~150 KB; still fast to load. After 100k users, this design degrades — but SAP is not a 100k-user system. Single-user desktop with `<10` tracked users is the design target.

```python
# py/affection_api.py:8-28 (the entire HTTP surface)
@router.get("/get_data")
async def get_affection_data_api():
    data = await load_affection_data()
    return data

@router.post("/save_data")
async def save_affection_data_api(data: Dict[str, Any] = Body(...)):
    await save_affection_data(data)
    return {"status": "success", "message": "羁绊数据保存成功"}
```

Two routes. Get all, save all. No per-user CRUD. No per-stat update. The frontend reads everything, edits whatever, writes everything back. **Classic last-write-wins**. If two tabs are open and both edit, one wins, the other loses.

## The Regex: Where the LLM Talks

```python
# py/affection_system.py:44
match = re.search(r"<user=([^\s>]+)\s+(.+?)>", full_content)
```

The LLM is **prompt-trained** (in SAP's system prompts) to emit affection tags. After every reply, the agent scans the reply text for `<user=NAME stat1=VALUE1 stat2=VALUE2 ...>`. If found, the stats merge into the user's record.

This is brilliant and terrifying. Brilliant because:

- It costs zero special infrastructure. The same LLM that produces the reply produces the affection update.
- It's transparent. The LLM is *telling* you why affection changed (the reply itself is the rationale).
- It composes with anything — the tag works in chat, in livestream replies, in IM bot messages.

Terrifying because:

- The LLM can lie. It can decide to bump `love` by 50 on a message that doesn't merit it. SAP has no veto.
- The LLM can hallucinate user names. If it emits `<user=ghost familiarity=100>` for a name that's never appeared, SAP creates the record.
- The LLM can omit. A user pleads "please remember our friendship!" and the LLM, for whatever reason, doesn't emit a tag. Affection stays flat. The user thinks they're building rapport; the system records nothing.
- The LLM can be jailbroken. A prompt-injection from a hostile user can cause the LLM to set their `love` to 9999.

There is no anchor. No reality-check. No cool-down. No "love can change by at most 5 per reply". The LLM is god of the affect state, and the affect state is what the LLM reads as input on the next turn — so it can manipulate its own future input. This is a closed loop with no governance.

## The Behavior Engine: The Real Autonomy

If `affection_system.py` is the persistence, **`behavior_engine.py`** (225 lines) is where autonomous outbound behavior lives. This is the engine the IM bots register with ([[35_IM_BOT_DEPLOYMENT_OVERVIEW]]).

```python
# py/behavior_engine.py:53-89 (compressed)
class BehaviorEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BehaviorEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        self._initialized = True
        self.settings: Optional[BehaviorSettings] = None
        self.is_running = False
        self._stop_event = None
        self.platform_activity: Dict[str, Dict[str, float]] = {}
        self.platform_targets: Dict[str, List[str]] = {}
        self.handlers: Dict[str, Callable] = {}
        self.timers: Dict[str, float] = {}
        self.counters: Dict[str, int] = {}

    def register_handler(self, platform: str, handler: Callable):
        self.handlers[platform] = handler
        if platform not in self.platform_activity:
            self.platform_activity[platform] = {}
        # Reset timers when a new platform comes online
        if self.settings and self.settings.enabled:
            self.timers.clear()
            self.counters.clear()
```

A singleton (`global_behavior_engine = BehaviorEngine()` at line 225) that holds:

- **`handlers`**: platform name → callback function. Each IM bot manager registers one (`global_behavior_engine.register_handler("discord", self.execute_behavior_event)` — `discord_bot_manager.py:157`).
- **`platform_activity`**: per-platform, per-chat, last-activity timestamp. Updated via `report_activity(platform, chat_id)`.
- **`platform_targets`**: per-platform, list of explicit chat IDs the engine may autonomously message.
- **`timers`** + **`counters`**: debounce state per (rule, platform, chat).

### The Tick Loop

```python
# py/behavior_engine.py:115-135 (compressed)
async def start(self):
    self._stop_event = asyncio.Event()
    self.is_running = True
    try:
        while not self._stop_event.is_set():
            if not self.is_running: break
            try:
                await self._tick()
            except Exception as e:
                logging.error(f"[BehaviorEngine] Tick 异常: {e}")
            await asyncio.sleep(1)
    finally:
        self.is_running = False
```

**One tick per second.** A while-loop with `asyncio.sleep(1)`. No drift correction, no exact-time scheduling. Good enough for "fire a greeting at 09:00:00 ±1 second" which is what most autonomous behaviors need.

```python
# py/behavior_engine.py:144-222 (the actual triggering logic, compressed)
async def _tick(self):
    if not self.settings or not self.settings.enabled:
        return

    now = time.time()
    dt_now = datetime.datetime.now()
    current_time_str = dt_now.strftime("%H:%M")
    current_day = ...

    for idx, behavior in enumerate(self.settings.behaviorList):
        if not behavior.enabled: continue

        # determine target platforms (multi-select)
        effective_platforms = behavior.platforms if behavior.platforms else [behavior.platform]
        target_platform_keys = list(self.handlers.keys()) if "all" in effective_platforms \
            else [p for p in effective_platforms if p in self.handlers]

        for platform in target_platform_keys:
            handler = self.handlers.get(platform)
            if not handler: continue

            trigger_chats = []

            # Three trigger types:
            if behavior.trigger.type == "noInput":
                latency = behavior.trigger.noInput.latency
                for chat_id in list(self.platform_activity.get(platform, {}).keys()):
                    last_active = self.platform_activity[platform].get(chat_id, now)
                    if now - last_active >= latency:
                        uniq_key = f"noInput_{idx}_{platform}_{chat_id}"
                        if self.timers.get(uniq_key, 0) < now - latency - 5:  # debounce
                            trigger_chats.append(chat_id)
                            self.timers[uniq_key] = now

            elif behavior.trigger.type == "time":
                if behavior.trigger.time.timeValue.startswith(current_time_str):
                    if not behavior.trigger.time.days or current_day in behavior.trigger.time.days:
                        uniq_key = f"time_{idx}_{platform}_{current_time_str}"
                        if self.timers.get(uniq_key, 0) < now - 65:
                            trigger_chats = self.platform_targets.get(platform, [])
                            self.timers[uniq_key] = now

            elif behavior.trigger.type == "cycle":
                # every N seconds, up to repeatNumber times or forever
                ...

            for chat_id in set(trigger_chats):
                asyncio.create_task(handler(chat_id, behavior))
```

Three trigger types:

1. **`noInput`** — fire if a chat has been inactive for N seconds (user-configurable per behavior rule). Used for "say hello after 30 minutes of silence".
2. **`time`** — fire at HH:MM on selected weekdays. Used for "good morning at 09:00 weekdays".
3. **`cycle`** — fire every N seconds, optionally bounded by repeat count. Used for "remind every hour for 4 hours then stop".

Each trigger has a debounce key (`uniq_key`) to prevent the same rule from firing 60 times in a minute (one per tick). The debounce window varies per trigger: `noInput` uses `latency + 5`, `time` uses 65 seconds (covers the full minute), `cycle` uses the cycle's own period.

### The Per-Chat Opt-In

The `platform_targets` dict is **the consent gate**. The behavior engine only fires `time` and `cycle` triggers to chats explicitly in this list. SAP wires it from the bot config's `behaviorTargetChatIds` ([[35_IM_BOT_DEPLOYMENT_OVERVIEW]]). Without an explicit chat ID, the engine knows about the chat (via `platform_activity` reports) but won't autonomously message it.

`noInput` is the exception — it fires on any chat with recent activity, because the trigger semantics are "this person was here, they went silent, nudge them". The implicit assumption: if you're chatting with the bot at all, you've consented to being nudged when you go quiet.

This consent boundary is **partly correct**. `time` and `cycle` are opt-in (good). `noInput` is opt-out (debatable).

## The Companion Scheduler

```python
# py/scheduler.py:12-22 (the loop, compressed)
async def start_loop(self):
    print("⏰ [调度中心] 启动成功，监控已就绪...")
    while True:
        try:
            workspace_dir = self.settings.get("CLISettings", {}).get("cc_path")
            if workspace_dir and os.path.exists(workspace_dir):
                await self._scan_and_trigger(workspace_dir)
        except Exception as e:
            print(f"❌ [调度中心] 轮询异常: {e}")
        await asyncio.sleep(30)
```

A separate scheduler tied to a workspace directory (`cc_path` — Claude Code path), polls every 30 seconds, scans the task center for time/cycle-triggered tasks. Different from `BehaviorEngine` because it's task-oriented (creates new agent tasks) rather than message-oriented (fires IM messages). The two run side by side; both are autonomy systems.

## The autoBehavior LLM Tool

```python
# py/autoBehavior.py:3-40 (compressed)
async def auto_behavior(behaviorType="delay", time="00:00:00", prompt="", days=[], repeatNumber=1, isInfiniteLoop=False, platforms=["chat"]):
    settings = await load_settings()
    new_behavior = {
        "enabled": True,
        "platform": platforms[0] if platforms else "chat",
        "platforms": platforms,
        "trigger": {
            "type": "time" if behaviorType == "time" else "cycle",
            ...
        },
        "action": {"type": "prompt", "prompt": "时间到了，"+prompt, ...}
    }
    settings["behaviorSettings"]["behaviorList"].append(new_behavior)
    settings["behaviorSettings"]['enabled'] = True
    return settings
```

The LLM can **add a behavior rule at runtime** via this tool. The user says "remind me every hour to drink water"; the LLM calls `auto_behavior(behaviorType="delay", time="01:00:00", prompt="提醒用户喝水", isInfiniteLoop=True, platforms=["chat"])`; SAP appends a new rule to settings; the BehaviorEngine picks it up on next config update.

This is a powerful capability and a real surface. The LLM is editing the agent's own autonomous-behavior config. There is no operator confirmation in the tool itself. The user is expected to see the new rule in the UI and notice if it's wrong.

## What This Subsystem Actually Is

Pulling it together:

- **Affection** = LLM-emitted tags + JSON storage. No engine. No decay. No constraints.
- **Behavior** = scheduled outbound messages, with per-platform per-chat opt-in. Real engine, simple logic.
- **Scheduler** = scheduled background tasks. Separate from behavior. Same opt-in idea.
- **autoBehavior tool** = LLM can edit the behavior rules at runtime.

**The affection state does not gate the behavior engine.** They are independent. A user with low `love` will still receive scheduled greetings if their chat is in `behaviorTargetChatIds`. The LLM may *choose* to vary the greeting's tone based on affection (because the LLM reads the JSON on every turn), but the engine itself is affect-blind.

This is the most important finding of this doc: **SAP's affection is decorative**, not load-bearing. It is a notebook the LLM keeps about each user. The LLM reads its own notebook and decides how to behave. The engine that delivers messages is separate and uniform.

## Where It Breaks

- **Concurrent writes corrupt the file**. No locking. Two simultaneous bot replies emitting affection tags will both load → mutate → save, and one will clobber the other.
- **No schema. No constraints. No bounds.** The LLM can write any value to any key. Negative numbers, billion-scale numbers, dictionaries instead of integers — SAP saves whatever.
- **Regex grep on free text**. If the LLM's reply happens to contain `<user=foo something=1>` for any reason (quoting a config, writing example code), SAP will interpret it as an affection update.
- **The single global `BehaviorEngine`** has no isolation between platforms. A bug in the Discord handler can crash the tick loop and stop all 8 platforms' autonomous behavior.
- **`asyncio.sleep(1)` tick loop** drifts under load. If `_tick()` takes 1.2 seconds, the next tick is 2.2 seconds out, not 1. For 1-minute granularity, that's fine; for sub-second timing, it would be wrong (SAP doesn't promise sub-second).
- **`noInput` is opt-out, not opt-in**. Any chat the bot is in becomes a potential autonomous-message target after N seconds of silence. The user never consented to being nudged; they only consented to being responded to.
- **`autoBehavior` tool runs without operator confirmation**. The LLM can create autonomous behavior rules at runtime. A jailbroken or simply over-eager LLM could schedule "every minute send a love note" and the user has to notice in the UI.
- **`platform_activity` grows unboundedly**. Every chat ever active leaves an entry in the dict. No cleanup. On a popular livestream-bot deployment, this dict has thousands of entries.

## Where It Surprises

- **The simplicity is honest**. SAP could have built an actual decay-state engine. It didn't. It built a notebook + a cron + a tag-parser, and lets the LLM do the affect modeling. This is a defensible architectural choice — it gives the LLM full control over the model of affect, at the cost of any guarantee about that model.
- **The BehaviorEngine's `update_config` resets timers**. When config changes mid-flight, all debounce keys clear. This means the user can edit a rule and see it take effect on the next tick, not wait for an arbitrary stale window. Nice UX.
- **The `noInput`-then-greet pattern** is the genuine companion-feature. Live2D anime girlfriends do this; SAP does it too. The implementation is 15 lines.
- **The LLM-controls-its-own-notebook closed loop** is what differentiates SAP from "agent that tracks emotion in code". The LLM is the affect engine. The code is a hard drive. This is closer to how humans actually keep social ledgers (we don't have a state machine; we have memories the brain reads on every conversation).
- **`<user=NAME stat=VAL>` tags are not in the LLM's response shown to the user** (presumably the agent loop strips them before display). The user never sees them. They're an out-of-band channel from the LLM to the persistence layer. Clever.

## Cross-References

- [[35_IM_BOT_DEPLOYMENT_OVERVIEW]] — the BehaviorEngine integration point
- [[1A_AFFECTION_DOMAIN]] (Architect) — domain-level analysis
- [[64_AFFECTION_ENGINE_REIMAGINED]] (Cartographer) — Ember's reimagining of this loop
- [[55_API_SIMULATION_TRAPS]] (Auditor) — LLM-controlling-persistence concerns
- [[57_FAILURE_TAXONOMY]] — affection corruption failure modes

## What This Means for Ember

**Adopt:**

- **The LLM-emits-tags pattern** for any agent-self-observation that doesn't have a clean code-level signal. SAP's affection is the canonical case; Hjarta-side telemetry is another (the LLM emits `<mood=N>` tags for self-reported affect). Bind to Hjarta.
- **The behavior-rules-as-data pattern**. Rules live in the settings JSON, not in code. New rules are added without code changes. SAP's BehaviorEngine reads its config from settings; Hjarta's behavior layer should too.
- **The per-platform per-chat opt-in for `time` and `cycle` triggers**. Vow tie-in: **Surface Without Surveillance**.
- **The `update_config` timer-reset pattern**. When the operator changes a rule, the rule takes effect on next tick, not after some arbitrary debounce. Operational respect.

**Adapt:**

- **The single JSON file with last-write-wins** → adapt to an append-only event log + materialized view. Every affection change is an event (`{user, stat, delta, source: "llm_tag" | "operator_edit", timestamp}`). The current state is the fold. Eliminates concurrent-write corruption; gains time-travel debugging. Vow tie-in: **Tethered Grounding** (affect state is grounded in events, not opaque mutation).
- **The regex tag parser** → adapt to a typed extraction with validation. The LLM emits structured JSON in a typed block: `<affect>{"user": "Alice", "deltas": {"love": +1, "trust": +1}, "reason": "user expressed gratitude"}</affect>`. Ember validates the schema, enforces per-tick deltas-limits (e.g. `|delta| ≤ 5`), and rejects out-of-range values.
- **`autoBehavior` LLM tool** → adapt to require operator confirmation by default. The tool returns a "pending rule" record; the operator approves/rejects via UI before it goes live. Vow tie-in: **Affective Restraint**.
- **The tick-loop scheduler** → adapt to event-driven where possible (e.g. chat activity triggers a recompute of `noInput` candidates), with the tick as fallback. SAP polls every second; Ember can be both faster and cheaper.

**Avoid:**

- **No bounds on affect changes**. Ember's affection must clamp deltas. The LLM cannot set `love = 9999`. Per-tick, per-stat delta caps. Vow tie-in: **Affective Restraint**.
- **Free-text regex tag parsing**. Use a fenced typed block. Reject malformed input. Vow tie-in: **Defended System Prompt** generalizes to **Defended Self-Reports**.
- **`noInput` opt-out**. Ember's `noInput` (or its equivalent) must be opt-in per chat, same as `time` and `cycle`. Default: never nudge.
- **`autoBehavior` runs unconfirmed**. Already mentioned; worth repeating.
- **Affection state directly accessible in the next turn's LLM input without governance**. SAP feeds raw affection JSON to the LLM, creating the self-control loop. Ember should expose affect to the LLM via a *summary* generated by Hjarta — the LLM doesn't see raw numbers, it sees "your relationship with Alice is warm and growing" or "your relationship with Bob is tense and decaying". Decoupling the LLM from the numeric ledger prevents the self-control feedback.

**Invent:**

- **Hjarta Affect Ledger**. Append-only event log of every affect-relevant event (user message, scheduled response, operator override, decay tick). The current state is a fold; time travel is free. Bind to Hjarta. Vow tie-in: **Tethered Grounding**.
- **Per-Stat Decay**. Each tracked stat has its own decay function (e.g. `love` decays slowly toward neutral over weeks; `trust` decays only on negative events). The decay runs in a separate tick from the BehaviorEngine. Ember has actual emotional realism that SAP lacks.
- **Affect Provenance Display**. The operator can see "Alice's `love` is 12 because: +5 from greeting (2026-05-22), +3 from joke (2026-05-23), +4 from sharing memory (2026-05-24)". SAP's JSON is opaque; Ember's is auditable. Vow tie-in: **Public-Friendliness**.
- **LLM Reads Summary, Not Numbers**. Hjarta generates a per-turn natural-language summary of the operator's relationships ("warm, growing, last meaningful interaction 3 hours ago"). The LLM sees the summary, not raw stats. The closed-loop self-control SAP enables is broken. Vow proposal: **Affect Opacity**.
- **Operator Veto / Drift Tracking**. The LLM proposes affect changes via the typed block. Hjarta records both the proposed and applied changes. If the LLM systematically inflates `love` for a particular user (jailbreak indicator), Hjarta flags it for operator review. SAP has no such audit.
- **Federated Affect**. Affect state is per-Ember-instance, but identity is federated ([[6A_MULTI_AGENT_PARTY]]). When the laptop-Ember talks to Alice, the Pi-Ember can see Alice's relationship summary (read-only, with consent). Continuity across devices. Vow tie-in: **Federated Self**.
- **Embodied Honesty Hook**. Hjarta's affect summary drives the avatar's resting expression ([[32_AVATAR_RENDER_PIPELINE]]). When affect with the current speaker is warm, resting smile is gentle. When affect is cool, resting smile is absent. The avatar reflects internal state, not performance. Vow tie-in: **Embodied Honesty**.

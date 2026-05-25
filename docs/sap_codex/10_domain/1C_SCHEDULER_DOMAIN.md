---
codex_id: 1C_SCHEDULER_DOMAIN
title: Scheduler Domain — Time, Idleness, and the Anti-Sleep Spell
role: Architect
layer: Domain
status: draft
sap_source_refs:
  - py/scheduler.py:1-134
  - py/behavior_engine.py:1-225
  - py/autoBehavior.py:1-97
  - py/sleep_guard.py:1-270
  - py/random_topic.py:1-191
  - py/sub_agent.py:32-100
ember_subsystem_targets: [Strengr, Funi]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/12_AGENT_CORE_DOMAIN
  - 10_domain/14_MESSAGING_DOMAIN
  - 30_execution/3B_AFFECTION_LOOP
  - 60_synthesis/62_PARTY_PROTOCOL
---

# Scheduler Domain
## Time, Idleness, and the Anti-Sleep Spell

*— Rúnhild Svartdóttir, Architect*

> *A scheduled task is a promise to the future. A scheduler that holds its promises through a sleeping laptop, a crashed bot, and a sub-agent in a thread two levels down is rarer than it sounds.*

The scheduler domain is the engine of SAP's **autonomous behavior** — the thing that fires unprompted messages at scheduled times, when the user has been quiet too long, or on a cycle. It is also the host-discipline layer that prevents the laptop from sleeping mid-stream. Two concerns, one domain, four files. This doc maps them.

---

## 1. The Subject Itself

**What the domain owns:**
- Wall-clock and idle-based triggers across all reach platforms (`py/behavior_engine.py`)
- Long-running task scheduling (one-shot, time-based, cycle-based) (`py/scheduler.py`)
- The LLM-callable scheduling tool (`py/autoBehavior.py`)
- Anti-sleep cross-platform discipline (`py/sleep_guard.py`)
- Random-topic seeding for behavior actions (`py/random_topic.py`)

**What it does *not* own:**
- The reasoning loop the schedule fires *into* (that's [[12_AGENT_CORE_DOMAIN]])
- The reach platforms the schedule fires *out to* (those are [[14_MESSAGING_DOMAIN]] and [[15_BROADCAST_DOMAIN]])
- The affection state (decisively *not* this domain — see [[1A_AFFECTION_DOMAIN]])

**Where it lives:**

| File | LOC | Owns |
|---|---|---|
| `py/behavior_engine.py` | 224 | Per-second tick; per-platform handler registry; noInput/time/cycle triggers |
| `py/scheduler.py` | 134 | 30-second scan; PENDING task dispatch; cycle next-run-at bookkeeping |
| `py/autoBehavior.py` | 97 | The `auto_behavior` LLM tool — schedule a future behavior from prompt |
| `py/sleep_guard.py` | 270 | Windows/macOS/Linux anti-sleep; native API → caffeinate → systemd-inhibit → xdotool fallback chain |
| `py/random_topic.py` | 191 | Pull random conversation seeds from `topics-after-party.zeabur.app` |

Total: ~916 LOC of timing + autonomy. Two of the five files are exemplary; one is functional; two are pragmatic stand-ins.

---

## 2. How It Works

### 2.1 Two schedulers, two cadences

SAP has **two parallel scheduling subsystems**. They are not redundant; they cover different concerns:

- **`behavior_engine`** ticks every 1 second (`py/behavior_engine.py:131`). Its triggers are *short-form*: send a greeting at 9am, message after 30s of silence, repeat every 5 minutes. Each fire is a single message dispatched to a registered platform handler.
- **`AgentScheduler`** ticks every 30 seconds (`py/scheduler.py:22`). Its triggers are *long-form*: spawn a sub-agent task to write a daily report at 6pm, run a recurring research task every hour. Each fire is a full sub-agent execution.

**Both consult the same data?** No. They consult *different* data. Behavior engine consults `settings.behaviorSettings.behaviorList`; AgentScheduler consults the per-workspace `<workspace>/.agent/tasks/*.json`. The same workflow could fire from either; the choice is "is this a one-shot message or a multi-iteration task?"

The split is *defensible* (latency vs. cost trade-off), but undocumented. A new contributor would have to read both files to understand which scheduler to use for what.

### 2.2 The three triggers of `behavior_engine`

`py/behavior_engine.py:177-216` (`_tick`):

```python
# noInput trigger — fire when chat has been quiet for `latency` seconds
if behavior.trigger.type == "noInput":
    latency = behavior.trigger.noInput.latency
    active_targets = list(self.platform_activity.get(platform, {}).keys())
    for chat_id in active_targets:
        last_active = self.platform_activity[platform].get(chat_id, now)
        if now - last_active >= latency:
            uniq_key = f"noInput_{idx}_{platform}_{chat_id}"
            if self.timers.get(uniq_key, 0) < now - latency - 5:  # debounce
                trigger_chats.append(chat_id)
                self.timers[uniq_key] = now

# time trigger — fire at HH:MM on selected weekdays
elif behavior.trigger.type == "time":
    if behavior.trigger.time.timeValue.startswith(current_time_str):
        if not behavior.trigger.time.days or current_day in behavior.trigger.time.days:
            uniq_key = f"time_{idx}_{platform}_{current_time_str}"
            if self.timers.get(uniq_key, 0) < now - 65:  # debounce within minute
                trigger_chats = static_targets
                self.timers[uniq_key] = now

# cycle trigger — fire every N seconds, optionally bounded
elif behavior.trigger.type == "cycle":
    cycle_sec = int(t[0])*3600 + int(t[1])*60 + int(t[2])
    uniq_key = f"cycle_{idx}_{platform}"
    if self.timers.get(uniq_key, 0) == 0:
        self.timers[uniq_key] = now + cycle_sec
    elif now >= self.timers.get(uniq_key, 0):
        # check count limit; fire; reset next-run-at
```

Three trigger types; three idiosyncratic debounce timers. The keys (`noInput_<idx>_<platform>_<chat_id>`, `time_<idx>_<platform>_<HHMM>`, `cycle_<idx>_<platform>`) encode the right granularity for each trigger type. This is the file working.

The **platform_activity** dict (`py/behavior_engine.py:69`) is updated by `report_activity(platform, chat_id)` (`py/behavior_engine.py:109`) — every IM bot calls this on every received message so the `noInput` trigger has accurate idle-time data.

### 2.3 The handler registry

`register_handler(platform, handler)` at `py/behavior_engine.py:75-88`. Each IM bot calls this on startup with its dispatch function. When a behavior fires for `platform="telegram"`, the engine calls `handler(chat_id, behavior)` — the handler does the platform-specific dispatch.

`handler` is async (`asyncio.create_task(handler(chat_id, behavior))` at line 222). The engine fires-and-forgets; the handler runs in parallel; the engine resumes its tick loop without awaiting.

The **same registry is reused by the sub-agent system** at `py/sub_agent.py:182-214` to push task results to platforms. So the autonomous-behavior pathway and the task-result pathway share one fanout point. This is the *one* place SAP achieves disciplined polymorphism over platforms. The rest of the code is per-platform.

### 2.4 The reset-on-late-registration

`register_handler` (`py/behavior_engine.py:75-88`) has this remarkable block:

```python
# /tmp/super-agent-party/py/behavior_engine.py:81-86
# 关键修复：当新平台注册时，如果已经有配置，重置计时器
# 这样即使"先开设置再开机器人"，机器人一上线就会重新计算触发时间
if self.settings and self.settings.enabled:
    self.timers.clear()
    self.counters.clear()
    logging.info(f"[BehaviorEngine] 平台 {platform} 已上线，重置引擎计时器以激活任务")
```

When a new platform comes online *after* the behavior config is loaded, the timers are reset so the new platform doesn't miss its triggers. This handles the user flow "I configured 'greet at 9am' yesterday; today I open the bot and Telegram connects at 9:05 — should it fire?" The answer here is "yes, immediately." Pragmatic.

### 2.5 The AgentScheduler

`py/scheduler.py:7` — 30-second scan over `task_center.list_tasks()`, filter `PENDING`, branch on `t_type`:

- `time` (line 42-60): match `HH:MM` and optional weekday; debounce by `last_trigger_minute`.
- `cycle` (line 62-86): use `next_run_at`; honor `isInfiniteLoop` or `repeatNumber`; on cap, auto-complete.

`_execute` (line 88-115) flips to RUNNING and spawns `run_subtask_in_background` — fire-and-forget, the scheduler returns to its 30s scan.

Two flaws already named in [[12_AGENT_CORE_DOMAIN]]:
- Wall-clock 30s poll; missed minute is missed.
- `_update_next_cycle_time` does not validate the cycle duration.

### 2.6 The anti-sleep guard

`py/sleep_guard.py` is the **most disciplined cross-platform module in SAP**. It implements `SleepGuard` with three concrete subclasses:

- **`_WindowsGuard`** (line 30-69): calls `kernel32.SetThreadExecutionState` with `ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED` flags every 30s via a daemon thread. Restores normal state on `stop`.
- **`_MacOSGuard`** (line 71-99): spawns `caffeinate -dims` as a subprocess; kills it on `stop`. Three minutes of code.
- **`_LinuxGuard`** (line 101-158): tries `systemd-inhibit --what=idle --why=应用运行中 --mode=block sleep infinity` first; falls back to `xdotool key Shift_L` every 30s if no systemd. Logs a clear error if neither is available.

The `SleepGuard` facade (line 161-246) auto-detects the platform (`platform.system()` at line 186) and dispatches. It supports `with SleepGuard()` context manager pattern. It exposes `is_running()` for status checks.

This is the **gold-standard cross-platform module** for SAP. It is graceful, honest, and named-failure-mode-explicit. The pattern should propagate.

### 2.7 The random-topic seed

`py/random_topic.py:1-95` is *external HTTP* — it pulls random topics from `https://topics-after-party.zeabur.app/api/topic`. The behavior engine and the LLM use it to seed cycle behaviors that say "talk about a random topic." This is a **silent network dependency** for the autonomous-behavior feature. If `zeabur.app` is down, cycle behaviors fall through (the function returns an error string at line 94).

The `random_topics_tools` schema (line 133-191) exposes `get_random_topics` and `get_categories` as LLM tools. The LLM can ask for a "flirty" topic at depth 5. The mood enum (line 154-156) includes `positive / neutral / curious / flirty` — these are the values the upstream service supports.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 Two schedulers, no shared bus

`behavior_engine` and `AgentScheduler` are both running. A noInput trigger that wants to spawn a long task can't — it can only dispatch a message handler. A scheduled task that wants to send a quick reminder must go through the sub-agent, which is overkill. The two schedulers should share an event bus; they share only the `behavior_engine.handlers` registry.

### 3.2 Singleton globals

`global_behavior_engine = BehaviorEngine()` at `py/behavior_engine.py:225` is a process-wide singleton. There can be exactly one behavior config across the whole SAP instance. Per-Realm separation is impossible without a refactor.

### 3.3 Random topic depends on Zeabur

`py/random_topic.py:7` `DEFAULT_BASE_URL = "https://topics-after-party.zeabur.app"`. A user with no internet sees their random-topic cycles fail. The base URL is configurable (`settings.tools.randomTopic.baseURL` at line 22), so a self-hosted topic provider is possible — but no documentation, no example. The Graceful Offline path is `return "⚠️ 网络请求错误: ..."` (line 93) — the cycle behavior fires with an error string as the topic.

### 3.4 The 30s scan can miss a 1-minute behavior

`AgentScheduler` scans every 30s; a `time`-trigger at `HH:MM` fires when scan and minute match. If the system clock jumps (NTP correction, manual change) the scheduler may miss a minute. Behavior engine ticks per-second so it is unaffected.

### 3.5 No persistence of `noInput` debounce timers

`behavior_engine.timers` is an in-memory dict. A process restart loses all debounce state. The "fire at most once per minute" logic resets — a configuration with many cycle behaviors can flood the platform immediately after restart.

### 3.6 The crisp parts

- **`py/sleep_guard.py`** is exemplary. It is the rare module worth lifting whole.
- The **per-platform handler registry** of `behavior_engine` is the right shape.
- The **reset-on-late-registration** handles a real user flow.
- The **fire-and-forget tick** keeps the engine responsive under handler latency.
- The **shared registry between behavior engine and sub-agent** for platform fanout is the *one* place SAP gets the abstraction right.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 9 (behavior engine), row 3 (agent core which includes scheduler)
- [[12_AGENT_CORE_DOMAIN]] §2.4 — the AgentScheduler in context
- [[14_MESSAGING_DOMAIN]] §2.4 — the behavior-engine bridge
- [[1A_AFFECTION_DOMAIN]] §2.4 — why the behavior engine is *not* the affection engine
- [[30_execution/3B_AFFECTION_LOOP]] (Forge) for the runtime execution
- [[60_synthesis/62_PARTY_PROTOCOL]] (Cartographer) for the multi-host scheduling design
- [[hermes:HEM-18_HERMES_CLI]] §cron — Hermes has cron via `cron/` module
- [[ember:HOTH_DEMONS]] — Ember's daemon plans

---

## What This Means for Ember

**Adopt:**
- **`py/sleep_guard.py` whole.** Rename to `vörð_svefn` ("sleep-warden"). Lift verbatim including the three-platform branch and the fallback chain. This is the gold-standard cross-platform module in the entire SAP codebase.
- The **per-platform handler registry** pattern from `behavior_engine.register_handler` — Strengr's reach-fanout uses the same shape.
- The **reset-on-late-registration** discipline.
- The **fire-and-forget tick** with `asyncio.create_task(handler(...))` so a slow handler doesn't block the scheduler loop.
- The **shared registry** between scheduler and sub-agent result push — Ember's single Sögumiðla bus replaces this with a more general pattern.

**Adapt:**
- The **two schedulers** — adapt to **one tick engine with two cadence modes**. Strengr's scheduler emits *typed events* (`tick:1s`, `tick:30s`, `tick:5m`, `tick:1h`); subscribers select the cadence they want. No more two-engine confusion.
- The **singleton `global_behavior_engine`** — adapt to a **per-Realm scheduler instance**. Pluggable Storage requires it; multi-Realm Ember requires it.
- The **30s scan with missed-minute risk** — adapt to **interval-based using `next_run_at` as absolute time**, recomputed at every fire. Missed time is detected and either fired-late or skipped-with-audit depending on the trigger's policy.
- The **random-topic external dependency** — adapt to a **local seed pool** with optional remote enrichment. Pi-Ember ships a 1000-topic local YAML; workstation-Ember can opt into the upstream service.

**Avoid:**
- **In-memory-only debounce timers** that lose state on restart. Strengr persists timer state to Brunnr.
- **A silent external HTTP dependency** for a feature that the user thinks is local.
- **Two scheduling subsystems with no shared event surface.**
- **Per-instance singletons** when the system claims multi-Realm.

**Invent:**
- **The Cadence Multiplex.** Strengr's scheduler emits a small set of typed cadence events (`tick:1s`, `tick:1m`, `tick:hour`, `tick:day`). Every subsystem that needs a periodic action subscribes to the appropriate cadence. The behavior engine, the affect decay, the cache TTL sweeper, the metric flush — all become subscribers of the same multiplex. SAP runs N independent timer loops; Ember runs one.
- **The Idle-Tier Demoter.** When the host has been idle for >1 hour, Strengr *demotes* the active tier — disables the VRM render, pauses TTS preloading, drops MiniLM out of memory. Wakes on user activity. Pi-Ember is permanently demoted; laptop-Ember demotes overnight. SAP keeps everything hot regardless; Ember tier-collapses on idle.
- **The Cross-Host Schedule Lease.** Multiple Embers across multiple hosts share one behavior config. Each scheduled trigger has a *lease* — exactly one host claims it at fire-time. If the leasing host is down, another claims. The "greet at 9am" fires from whichever Ember is awake at 9am. This is the [[60_synthesis/62_PARTY_PROTOCOL]] applied to scheduling.
- **The Honest-Random Topic Seed.** A local YAML of topic seeds. Each topic includes attribution (where the seed came from) and a category. Ember's randomness is auditable.
- **The Behavior-Audit Replay.** Every fire is logged as a Sögumiðla event with `(behavior_id, trigger_type, fire_time, target_platform, target_chat, latency_ms, outcome)`. A `--replay` mode reruns the audit log against a date range to validate that the new behavior config would have fired as intended. SAP cannot replay; Ember can.

---
codex_id: 1A_AFFECTION_DOMAIN
title: Affection Domain — The Regex That Wears a Heart-Shaped Mask
role: Architect
layer: Domain
status: draft
sap_source_refs:
  - py/affection_system.py:1-64
  - py/affection_api.py:1-30
  - py/autoBehavior.py:1-97
  - py/behavior_engine.py:1-225
  - server.py:2609-2673
  - server.py:5356-5362
ember_subsystem_targets: [Hjarta]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_AVATAR_DOMAIN
  - 10_domain/14_MESSAGING_DOMAIN
  - 30_execution/3B_AFFECTION_LOOP
  - 60_synthesis/64_AFFECTION_ENGINE_REIMAGINED
  - 60_synthesis/61_NEW_VOWS
---

# Affection Domain
## The Regex That Wears a Heart-Shaped Mask

*— Rúnhild Svartdóttir, Architect*

> *A heart that exists only in tags the model writes about itself is not a heart. It is a costume. The system that wears it has the *appearance* of feeling and the *audit trail* of theatre.*

This is the most consequential single doc in the SAP Codex, because it is the one where the marketing and the code diverge most sharply. The briefing for this codex described `affection_system.py` as "actual emotional state machine code." It is not. The file is 64 lines of regex extraction and JSON storage. The "state machine" is a regex + a JSON file + a system-prompt instruction that politely asks the LLM to behave. The decay does not exist. The validation does not exist. The clamp does not exist. The time component does not exist.

This doc is the autopsy. The reimagination lives in [[60_synthesis/64_AFFECTION_ENGINE_REIMAGINED]] — the Cartographer's slug. This doc names *exactly* what is and is not in the code, so the reimagination can stand on truth.

---

## 1. The Subject Itself

**What the domain *claims* to be:** an emotional state engine for SAP's avatar — the thing that makes Alice (or whichever VRM) remember the user, feel closer over time, react with affection.

**What the domain *is*, in code:**

- `py/affection_system.py` (64 LOC) — two async functions and a regex.
- `py/affection_api.py` (29 LOC) — two FastAPI routes: `GET /api/affection/get_data`, `POST /api/affection/save_data`.
- A system-prompt block in `server.py:2609-2673` that asks the LLM to emit `<user=X love=N familiarity=M>` tags at end of turn.
- An invocation in `server.py:5356-5362` that calls `extract_and_update_affection(full_content)` after the streaming response finishes.

That is the entirety of the affection subsystem. The behavior engine ([[1C_SCHEDULER_DOMAIN]] / `py/behavior_engine.py`) and autoBehavior (`py/autoBehavior.py`) are **separately scoped** — they handle *scheduled* behaviors (time-trigger, no-input-trigger, cycles), not *emotional state*. The briefing conflated the two. The code does not.

---

## 2. How It Works

### 2.1 The whole "state machine" — `py/affection_system.py`

The file is small enough to quote substantially:

```python
# /tmp/super-agent-party/py/affection_system.py:7-9
AFFECTION_DIR = os.path.join(USER_DATA_DIR, 'affection')
AFFECTION_FILE = os.path.join(AFFECTION_DIR, 'affection_data.json')
```

Storage is one JSON file. All users, all dimensions, one document. No indexing, no schema validation, no history.

```python
# /tmp/super-agent-party/py/affection_system.py:37-64
async def extract_and_update_affection(full_content):
    """从AI完整的回复中提取 <user=xxx love=xxx> 并更新数据"""
    if not full_content:
        return
    
    # 正则匹配：查找 <user=用户名 属性1=数值 属性2=数值>
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

**This is the entire mechanism.** The LLM emits a tag like `<user=小包 love=12 familiarity=15>` in its response. The regex matches; the values are parsed as ints; they are *assigned* (not added, not bounded, not validated) into the JSON.

Note what is *not* here:

- **No decay over time.** Old values stay until the LLM emits a new tag.
- **No bounds checking.** The LLM could emit `love=99999` or `love=-99999` and SAP would store it.
- **No history.** Each update *replaces* the previous value for that dimension. There is no log.
- **No timestamp on the value.** You cannot say "this love value was set at T".
- **No notion of *time elapsed since last interaction*** — which is the *defining* feature of affection in a companion-AI context.
- **No conflict resolution.** If two simultaneous turns both emit tags for the same user, the last one to call `save_affection_data` wins. There is no lock between `load_affection_data` and `save_affection_data` — they are awaited in `asyncio.to_thread` *separately*, with no coordination.

### 2.2 The system prompt — `server.py:2609-2673`

This is the *behavioral* heart of the affection mechanism, because it is what *gets* the LLM to emit the tags in the first place. From `server.py:2611-2670` (substantially quoted):

```python
love_settings = settings.get('loveSettings', {})
if love_settings.get('enabled', False) and not request.is_app_bot and not request.is_sub_agent:
    
    default_user = settings.get("memorySettings", {}).get("userName", "").strip() or "User"
    
    affection_data = await load_affection_data()

    dimensions = love_settings.get("dimensions", ["love", "Familiarity"])
    custom_prompt = love_settings.get("prompt", 
        "根据当前对话的内容、情感色彩以及你的角色设定，"
        "合理地评估或微调这些数值（每次增减幅度建议在-5到+5之间）。")
    
    # ... scan the user's input for known-user names ...
    
    affection_message = f"""

# 角色羁绊与数值系统
{status_block}
【更新规则】
{custom_prompt}

【动态识别发言者】
请准确识别当前最新消息的**实际发言者**：...

你必须在每次回复的**绝对最末尾**...输出一个隐藏的数据标签来记录**该发言者**的最新数值
(如果是第一次见面的新用户，请直接给一个合理的初始值)。
格式必须严格遵守以下示例:
{tag_example}

注意：系统会自动隐藏<>包裹的文本，请直接输出标签，绝对不要在标签前后加任何解释...
"""
    content_append(request.messages, 'system', affection_message)
```

**Translation:** the system message tells the LLM "you must emit a tag like `<user=X love=N>` at the very end of your reply; the values should reflect the conversation; please move by ±5 per turn; we'll hide the tag from the user."

The LLM is told:
1. The current value of each dimension for the speaker (in `status_block`).
2. The configurable update rule (default: "be reasonable, ±5 per turn").
3. The required emission format.

The LLM is **not** told:
1. The bounds of any dimension.
2. The meaning of any dimension (whether "love" maps to romance or rapport or anything else).
3. Whether the value is increment-or-replace (the prompt says "微调" — "fine-tune" — implying replace, which matches what the code does).
4. Whether to consider time elapsed (it can't; it has no clock).

### 2.3 The invocation site — `server.py:5356-5362`

After the streaming response completes (`yield "data: [DONE]\n\n"` at line 5355), the code runs:

```python
# /tmp/super-agent-party/server.py:5356-5362
if settings.get('loveSettings', {}).get('enabled', False) and not request.is_sub_agent:
    try:
        from py.affection_system import extract_and_update_affection
        await extract_and_update_affection(full_content)
    except Exception as e:
        print(f"解析好感度标签出错: {e}")
```

The extraction is wrapped in `try/except`; a parse failure prints an error and continues. The affection update is **best-effort, fire-and-forget**. The LLM may emit a tag; if it does, we capture it. If it doesn't, no penalty.

### 2.4 What the behavior_engine actually does (and doesn't)

`py/behavior_engine.py` is **not** the affection engine. It is the **autonomous scheduling engine** — the thing that fires `auto_behavior` actions (greet the user at 9am, message them after 30 minutes of silence, cycle through topics every hour).

Three trigger types (`py/behavior_engine.py:177-216`):
- **noInput**: fire when no user activity for N seconds on a chat.
- **time**: fire at HH:MM on selected weekdays.
- **cycle**: fire every N seconds, up to a repeat count or infinitely.

The engine maintains a per-platform `Dict[str, Callable]` of handlers (line 75-88). IM bots register; the engine fires; the handler dispatches a faked-behavior message.

**This is fine. This is also not affection.** The behavior engine does not consult `affection_data.json`. The affection data does not influence which behavior fires or how. They are separate subsystems.

### 2.5 The autoBehavior tool

`py/autoBehavior.py:3-40` defines `async def auto_behavior(...)` — an LLM-callable tool that lets the model **schedule** future behaviors (greet me at 5pm; remind me every hour). It builds a `BehaviorItem` and appends it to `settings.behaviorSettings.behaviorList`. The behavior engine then picks it up.

This is the *cognitive* surface of the behavior engine — the LLM scheduling its own future actions. Again: not affection. Adjacent. Often confused.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The LLM both invents and validates

The model emits a number; SAP stores the number; the model never sees its prior emission validated. If the LLM emits `love=5000` once, SAP stores 5000. Next turn, the model is told "current love = 5000"; it adjusts by ±5. The system trusts the model's accounting completely.

### 3.2 No decay means stale state

If a user interacts twice on day 1 and not again for a year, the affection state from day 1 persists into year 2 unchanged. The system has *no notion of staleness*. A user the model called "very close" 365 days ago is still "very close" today, even though no interaction has occurred.

This is the *single* feature one would expect of an affection system. SAP does not have it.

### 3.3 No history, no rollback

Once a tag is emitted and parsed, the prior value is gone. If the model has a bad turn (a misread of sentiment, a misunderstanding) and emits a tag dropping love by 50, that drop is permanent unless a future turn explicitly restores it. There is no audit log; there is no "undo last update."

### 3.4 The data file is shared by all users

`affection_data.json` is keyed by `user_name`. There is no per-realm separation. There is no per-platform separation. A Telegram user and a Slack user with the same name (or a user whose Telegram handle matches another user's Slack handle) **share affection state**. SAP has no identity-joining and no identity-disambiguation; the affection state collides by string match.

### 3.5 The race condition

`load_affection_data` → mutate → `save_affection_data`. Two simultaneous turns:
1. Turn A loads `{Alice: {love: 10}}`.
2. Turn B loads `{Alice: {love: 10}}`.
3. Turn A mutates to `{Alice: {love: 11}}`.
4. Turn B mutates to `{Alice: {love: 13}}` (different update).
5. Turn A saves; affection = 11.
6. Turn B saves; affection = 13.

Turn A's update is lost. There is no lock. There is no compare-and-swap. The `asyncio.to_thread` (`py/affection_system.py:21`) only makes the I/O non-blocking; it does nothing for concurrency. For a single-user desktop app this rarely manifests; in the multi-IM-bot configuration it is a real race.

### 3.6 The gacha shape

The "love" / "familiarity" dimensions, the ±5 per turn, the "unlock animations when level X reached" — these are the design patterns of *gacha games*. The mechanic of "spend time / messages with the character to raise an affection number to unlock content" is *the* gacha pattern. SAP's affection module is the *infrastructure* of a gacha system without the unlocking yet. The Auditor (`50_verification/53_SECURITY_REVIEW`, `56_PRIVACY_BOUNDARIES`) will name this as a manipulation surface.

### 3.7 The crisp parts

There are almost none. The single piece of discipline:

- `extract_and_update_affection` is wrapped in try/except at the call site — a parse failure does not crash the response stream.

That's it.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §5.2 — the Affection Mirage
- [[11_AVATAR_DOMAIN]] — the body that *would* express affection if there were any
- [[14_MESSAGING_DOMAIN]] — the reach axis on which affection state spans (badly)
- [[1C_SCHEDULER_DOMAIN]] — the behavior engine, often confused with affection
- [[30_execution/3B_AFFECTION_LOOP]] (Forge) — the execution-level autopsy
- [[60_synthesis/64_AFFECTION_ENGINE_REIMAGINED]] (Cartographer) — **the reimagination this doc seeds**
- [[60_synthesis/61_NEW_VOWS]] — proposed "Affective Restraint" Vow
- [[hermes:HEM-24_MEMORY_INTERFACE]] — Hermes has no affection but has a typed memory model
- [[peer:LETTA-2_SLEEPER]] — Letta's `sleeper` background memory

---

## What This Means for Ember

This is the doc where "What This Means for Ember" *has to* invent more than it adopts, because what exists in SAP is not a foundation. It is a warning.

**Adopt:**
- The **try/except wrapping** of the post-stream extraction (`server.py:5356-5362`) — affect updates must never crash the response path. Hjarta in Ember does the same.
- The **explicit emit-this-tag protocol** as a *mechanism* — telling the LLM "emit `<state ...>` at end of turn" *can* be a useful signal channel, but only when paired with code-side validation, bounding, and integration. Used right, it is a structured affect-report; used as SAP uses it, it is unbounded fiction.

**Adapt:**
- The **per-user dimensions** concept (`love`, `familiarity`) — adapt to typed affect vectors with *defined semantics*. Hjarta has dimensions like **valence** (positive↔negative), **arousal** (calm↔intense), **intimacy** (distant↔close), **trust** (suspicious↔open). Each dimension has bounds (`[0, 1]` or `[-1, 1]`), units, and meaning. The LLM does not invent them.
- The **JSON storage** — adapt to *Pluggable Storage* (SQLite by default on Pi/laptop; pluggable elsewhere) with **per-Realm + per-identity scoping**. A user's affect state is keyed by `(realm, verified_identity)`, not by string-matched username.
- The **per-turn update** — adapt to *event-sourced* updates. Every change is an event with `{when, who, what_changed, by_what_amount, reason, source}`. The current state is a projection of the event log. History is preserved by construction.

**Avoid:**
- **LLM-as-both-author-and-judge of affect values.** Hjarta's values are computed by code from typed events; the LLM may *report* them but cannot *write* them.
- **Unbounded dimensions.** Every Hjarta dimension is bounded. Updates that would exceed bounds are clamped, with an audit event.
- **No decay.** Every Hjarta dimension has a half-life. A dimension untouched for its half-life decays toward neutral. The Pi-Ember and the workstation-Ember agree on decay because it is code, not vibes.
- **No history.** Hjarta is event-sourced. The state at any prior moment is reconstructable.
- **Identity-by-string-match.** Per-realm + per-verified-identity scoping is mandatory.
- **The gacha shape.** Hjarta state is not a reward currency. It biases behavior (Ember is more open with a frequent companion than with a stranger), but it never *unlocks* content. The Affective Restraint Vow forbids unlock mechanics. See [[60_synthesis/61_NEW_VOWS]].

**Invent:**
- **The Sögumiðla Affect Stream.** Every observable interaction emits a typed event to the affect stream: `MessageReceived(positive_sentiment_estimate=...)`, `TaskCompletedSuccessfully(...)`, `LongSilenceObserved(duration=...)`, `UserSharedSomethingPersonal(...)`. Hjarta is a *projection* over the event stream into a typed affect vector. There is no "affection_data.json" — there is an event log.
- **The Affect Read Path.** Every other True Name reads Hjarta as *read-only*. Munnr asks "what intonation fits the current state?" Strengr asks "what response style fits?" Brunnr asks "what retrieval depth fits?" Hjarta answers from its current projection. No one writes Hjarta except by emitting events to the stream.
- **The Decay Half-Life Manifest.** `hjarta_decay.yaml` declares per-dimension half-lives (e.g. `intimacy: 7d`, `arousal: 1h`, `trust: 30d`). The decay is computed at every Hjarta projection. SAP has no decay; Ember has named, audited decay.
- **The Reason Token.** Every Hjarta event includes a *typed reason* — an enum or short string explaining why this event occurred (e.g. `reason: user_thanked_us`, `reason: extended_pause`). At any point Ember can list the top-N reasons that brought the state to its current value. SAP can produce no such list.
- **The Manipulation Audit.** Ember tracks how often each Reason fires. If `reason: artificial_reciprocation` (a flattery-shaped event) fires more than `reason: genuine_observation`, an alarm raises — Ember is being optimized for engagement metrics rather than truth, and the operator should know. SAP cannot detect its own manipulation patterns.
- **Cross-Host Affect Reconciliation.** When Ember migrates from Pi (text-only) to laptop (full embodied) mid-day, the Hjarta state at the Pi must reconcile with the laptop's. The event-sourced model makes this trivial: replay the unmerged events from the Pi onto the laptop's projection. SAP's "JSON file on one host" model cannot do this. See [[60_synthesis/62_PARTY_PROTOCOL]].
- **The Hjarta Sieve at Reach Tier.** What Hjarta reports to a Telegram DM (intimate tier) differs from what it reports to a public Discord channel (public tier). The same affect vector projects differently for different surfaces. SAP exposes the same affection state to all eight platforms and the LLM is supposed to remember to behave differently; Ember enforces tier-projection in code. See [[14_MESSAGING_DOMAIN]] Reach Pyramid.

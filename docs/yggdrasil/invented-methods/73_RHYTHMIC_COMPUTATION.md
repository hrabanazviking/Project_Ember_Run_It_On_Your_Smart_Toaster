# 73 — Rhythmic Computation (Time-Aware Background Work)

A method for scheduling background tasks by *natural
rhythms* rather than flat intervals. Tasks run at
times-of-day that *fit*.

---

## The principle

Most background-task systems schedule by interval ("every
30 minutes") or cron ("every day at 3 AM"). Both are
*flat* — they don't consider the system's natural rhythms
or the operator's context.

**Rhythmic Computation** schedules tasks by *what the
moment is* — astronomical phase, time-of-day register,
operator activity pattern. The result: heavy work happens
when it *fits*; light work happens when it *signals*
naturally.

---

## What rhythms are available

Per [`../architecture/37_THE_ASTROLOGY_RHYTHM_PLANE.md`](../architecture/37_THE_ASTROLOGY_RHYTHM_PLANE.md):

| Rhythm | What it means |
|---|---|
| Time-of-day | morning / midday / evening / deep_night |
| Lunar phase | new / waxing / full / waning |
| Solar phase | dawn / solar_noon / dusk / midnight |
| Sabbat | wheel-of-the-year cardinal moments |
| Operator activity | active / idle / sleeping |

Tasks can subscribe to any of these.

---

## Example: dreamstate timing

Naive: "run dreamstate every day at 3 AM."

Rhythmic: "run dreamstate when operator is idle AND it's
past midnight AND lunar phase is not new_moon (avoid
ritual nights)."

```yaml
yggdrasil:
  dreamstate:
    schedule:
      kind: rhythmic
      conditions:
        - operator_idle_for_minutes: 30
        - hour_after: 0
        - hour_before: 5
        - exclude_lunar_phases: [new_moon]   # operator pref
```

The dreamstate fires when conditions align; doesn't fire
otherwise.

---

## Example: snapshot scheduling

Naive: "snapshot every day at midnight."

Rhythmic: "snapshot during the lull between operator's
work sessions; after dreamstate; not during active chat."

```yaml
yggdrasil:
  norns:
    schedule:
      kind: rhythmic
      after_dreamstate: true
      not_during_chat: true
      lull_minutes: 15
```

---

## Example: index optimization

Qdrant benefits from periodic index optimization. Naive:
weekly. Rhythmic: when operator's been inactive AND
recent ingest volume warrants it.

```yaml
yggdrasil:
  huginn:
    index_optimization:
      kind: rhythmic
      conditions:
        - operator_idle_for_hours: 2
        - ingest_volume_since_last_optimize_mb: 100
      cooldown_hours: 168       # at most once a week
```

---

## How rhythms compose

Tasks can require *combinations* of rhythms:

```yaml
schedule:
  kind: rhythmic
  conditions:
    - any:                       # OR
        - lunar_phase: full
        - time_of_day: deep_night
    - all:                       # AND
        - operator_idle_for_minutes: 60
        - not_currently_running: meta_learning
```

The condition tree is evaluated continuously by the
scheduler. When all conditions become true, the task fires.

---

## Why this beats cron

Cron is fine for flat schedules. Rhythmic adds:

1. **Adaptive to operator presence.** Don't run heavy
   work while the operator is mid-chat.
2. **Adaptive to system load.** Don't pile up tasks during
   high load.
3. **Semantic timing.** "After dreamstate" is more
   meaningful than "3:30 AM."
4. **Reduce contention.** Tasks naturally space out
   instead of all firing at exactly the same minute.

---

## What "operator idle" detects

Composite signal:

- No `chat.turn_*` events for N minutes.
- No Stofa keystrokes for N minutes.
- System indicator: lock screen active OR screensaver on
  (where detectable).

`operator_idle_for_minutes: 30` means: no signs of
operator activity for 30 minutes.

---

## What "lull" detects

A *lull* is a period of low system activity:

- Background workers can run.
- Foreground chat isn't active.
- CPU is below a threshold (say 30% sustained).

Lulls are *the right moment* for index optimization,
snapshots, dreamstate, meta-learning passes. Rhythmic
scheduling waits for them.

---

## How this composes with budgeting

Rhythmic scheduling chooses *when* a task can run; the
budget (per [`../cross-platform/61_RESOURCE_BUDGETING.md`](../cross-platform/61_RESOURCE_BUDGETING.md))
chooses *how much* it can use.

A task may fire (rhythm OK) but then defer (budget
exceeded). It just waits for the next moment.

---

## Risk / known issues

- **Tasks that never fire.** If conditions are too
  restrictive, a task may never run. We add fallback
  guarantees ("must run at least once per week regardless
  of conditions").
- **Operator inactivity isn't always real.** Operator
  could be at their desk watching something on their
  phone. We don't claim perfect inference; the rhythm is
  a *heuristic*.

---

## Configuration shape

```yaml
yggdrasil:
  rhythmic_computation:
    enabled: true
    
    detection:
      idle_threshold_minutes: 5
      lull_cpu_pct_threshold: 30
      lull_duration_seconds: 60
    
    fallback_guarantees:
      enabled: true              # ensure long-deferred tasks eventually run
      max_deferral_factor: 2.0   # if requested interval = 24h, max wait = 48h
    
    tasks:
      # per-task schedules go here
      dreamstate:
        kind: rhythmic
        conditions: [...]
      norns_snapshot:
        kind: rhythmic
        conditions: [...]
```

---

## Operator-facing example

Operator returns to Stofa after lunch:

```
[Stofa is responsive immediately; no "still loading" state]

[Background, while operator was away:]
- Dreamstate consolidated last night's chat patterns
- Snapshot of state taken after dreamstate
- Huginn re-optimized its index
- Meta-learning analyzed recent Episodes
- All while the operator was away; zero impact on the
  chat experience
```

The rhythm-aware scheduler maximized "useful work" without
ever competing with operator-foreground time.

Doctor screen shows the rhythm + completed tasks:

```
Current rhythm:
  Time of day: midday (warm)
  Lunar phase: waxing_gibbous
  Operator activity: active (resumed 8 min ago)

Recent background tasks:
  ✓ Dreamstate (last night, 02:14, took 47s)
  ✓ Snapshot (last night, 02:15, took 8s)
  ✓ Huginn index optimization (last night, 03:42, took 22s)
  ✓ Meta-learning pass (last night, 04:01, took 18s)
```

The operator sees: things happened; nothing interrupted
them.

---

## Why "rhythmic"

The word *rhythm* implies natural periodicity, not flat
intervals. The system **breathes** — work happens in
*phases*, like a tide:

- **In** (operator active, foreground chat).
- **Pause** (operator idle, system observes).
- **Out** (background work fires).
- **In** again.

This matches how operators actually use the system. And it
matches Yggdrasil's cosmological aesthetic — *the world
moves in seasons; the system moves with it*.

---

## Closing

Rhythmic Computation makes Yggdrasil **a system that
breathes with the operator**. Background work fits the
moment. Foreground chat is never starved. Heavy operations
happen when they *fit*, not when an arbitrary clock says.

This is what *feels right* when an operator lives with the
system for months — the system seems to know when to do
its own work, and when to step aside.

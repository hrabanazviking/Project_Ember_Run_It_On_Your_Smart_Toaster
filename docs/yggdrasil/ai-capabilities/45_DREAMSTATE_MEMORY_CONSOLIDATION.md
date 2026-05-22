# 45 — Dreamstate Memory Consolidation

The nightly offline replay that lets Ember consolidate the
day's interactions into long-term patterns. Named after
Hugin + Munin, Odin's ravens who fly out daily and return
each night.

---

## The metaphor

In Norse cosmology: Odin sends his two ravens (Huginn =
Thought, Muninn = Memory) out across the worlds each
morning; they return each evening to whisper what they've
seen.

In Yggdrasil: Ember's daily interactions (chats, ingests,
tool calls, awareness events) are the day's flight. The
*dreamstate consolidation* is the evening return — a
background process that reviews the day, strengthens
associations, decays unused memories, and surfaces patterns
for the next day's awareness.

---

## What dreamstate does

A single nightly batch (~minutes long; runs while operator
is asleep):

1. **Apply Ebbinghaus decay** to all Mímir chunks.
2. **Reinforce** chunks accessed today.
3. **Update Muninn's Hebbian associations** based on
   co-occurrence patterns from today's retrievals.
4. **Run meta-learning analysis** on today's Episodes.
5. **Generate a daily summary** (operator-facing, opt-in)
   — what topics came up, what was new, what patterns
   emerged.
6. **Snapshot state** for the Norns backup (per
   [`../robustness/54_THE_NORNS_BACKUP_SYSTEM.md`](../robustness/54_THE_NORNS_BACKUP_SYSTEM.md)).

Each step is small. The whole batch is ~30-120 seconds on
Pi 5; ~10-30 seconds on desktop.

---

## When dreamstate runs

Three modes:

### 1. Idle-triggered (default)

When Verdandi observes no `chat.turn_*` events for 30
minutes (operator-tunable) AND it's been > 12 hours since
the last dreamstate run, dreamstate fires.

Result: dreamstate runs naturally when operator is away
or asleep.

### 2. Scheduled

Operator sets a fixed time:

```yaml
yggdrasil:
  dreamstate:
    schedule: "0 3 * * *"     # cron-style; 3 AM daily
```

### 3. Manual

```bash
ember yggdrasil dreamstate run
```

Operator triggers explicitly. Useful for testing or
post-heavy-session consolidation.

---

## What dreamstate produces

### A daily summary (optional)

If `surface_summary: true` in config, the next chat session
starts with an optional summary:

```
[Stofa opens]
[Hjarta wizard isn't needed; identity exists]
[Before chat input, optional summary card:]

╭─ Yesterday's traces ───────────────────────────╮
│                                                  │
│  9 conversations · 4 ingest tasks · 23 tool calls│
│                                                  │
│  Recurring topics:                               │
│   ▶ Norse cosmology (4× — strengthening cluster) │
│   ▶ Yggdrasil integration (3×)                   │
│                                                  │
│  New documents in the Well: 14                   │
│  Documents whose weight is fading: 47            │
│                                                  │
│  One contradiction noticed in your Odin notes —  │
│  want to reconcile? (y/n/later)                  │
│                                                  │
│  Press any key to dismiss.                       │
╰──────────────────────────────────────────────────╯
```

Operator-toggleable. Default: off (operators who want it
turn it on).

### Updated state

Even when no summary is surfaced, the state changes:

- Mímir weights recalculated.
- Muninn associations strengthened.
- Pattern store updated (per
  [`44_META_LEARNING_FROM_EPISODES.md`](44_META_LEARNING_FROM_EPISODES.md)).
- Norns snapshot taken.

Operator's *next* chat turn benefits silently.

---

## Why "dreamstate"

The name fits because:

- Runs while operator is away (sleeping, in another
  context).
- Consolidates day's experiences into long-term shape.
- Strengthens helpful associations; lets unimportant ones
  fade.
- Surfaces *patterns* on waking (the daily summary).

This is *exactly* what neuroscience attributes to REM sleep
for human memory consolidation. We borrow the metaphor; the
implementation is simpler than biology but operates on the
same principle.

---

## What dreamstate does NOT do

- **Self-modify the LLM.** Funi's weights are untouched.
  Pure data-side consolidation.
- **Wake the operator.** All operations are silent.
- **Take network actions.** Pure local computation.
- **Make decisions about what to remember.** Decay + access
  are mechanical; no semantic judgment.

---

## The technical implementation

A single async background task:

```python
class DreamstateWorker:
    async def run(self):
        if not self._should_run_now():
            return
        
        async with self._lock:  # only one dreamstate at a time
            await self._publish_event("dreamstate.started")
            
            await self._apply_decay()
            await self._reinforce_accessed_chunks()
            await self._update_associations()
            await self._run_meta_learning()
            
            summary = await self._generate_summary() if self.config.surface_summary else None
            await self._snapshot_state()
            
            await self._publish_event("dreamstate.completed", summary=summary)
```

Each step is its own method, instrumented with timing +
Verdandi events. Operators can watch via the debug overlay.

---

## How dreamstate interacts with other realms

| Realm | Interaction during dreamstate |
|---|---|
| Mímir | decay sweep, reinforcement application |
| Huginn (Qdrant) | index optimization (Qdrant's built-in) |
| Muninn | Hebbian weight updates from today's co-occurrences |
| MemPalace | (if enabled) its own maintenance pass |
| Verdandi | publishes dreamstate events; reads the day's events |
| Astrology | provides "today's date" for the summary |
| Kista | unlocks once if needed for any realm operations |

All cooperatively coordinated; no blocking; failures don't
cascade.

---

## What happens if dreamstate is interrupted

If Stofa quits mid-dreamstate, or the operator wakes the
laptop:

- The dreamstate worker checkpoint-saves its progress.
- On next idle, it resumes from the checkpoint.
- Operator doesn't lose work.

The Norns backup snapshot is the *last* step, so partial
dreamstate runs don't produce inconsistent snapshots.

---

## Configuration shape

```yaml
yggdrasil:
  dreamstate:
    enabled: true
    mode: idle_triggered          # or "scheduled" or "manual_only"
    idle_threshold_minutes: 30
    min_interval_hours: 12
    schedule: ""                  # if mode == scheduled, cron-string
    surface_summary: false        # opt-in for daily summary
    summary_format: card          # or "verbose"
    operations:
      decay: true
      reinforcement: true
      associations: true
      meta_learning: true
      snapshot: true              # Norns backup
    timeout_s: 600                # max 10 min before giving up
```

---

## Risk / known issues

- **Battery on laptops.** Dreamstate runs while system is
  idle. If operator wakes mid-run, brief CPU spike. Mitigate
  by deferring CPU-heavy ops to scheduled mode.
- **State growth.** Patterns + snapshots grow over time.
  Vacuum + prune policies keep size bounded.
- **Surprise summaries.** First time the summary card
  appears, operator might be startled. Default off; opt-in
  via Settings or wizard step.

---

## Operator-facing example (over time)

### Day 1
Operator chats. Dreamstate runs at night. Imperceptible
benefit (no patterns yet).

### Week 1
Subtle: retrieval feels slightly more relevant.

### Month 1
Operator-noticeable: "Ember remembers what I've been
working on across sessions."

### Year 1
Substantial: Ember has *deep familiarity* with the
operator's intellectual interests. Returns to old topics
have *gravitational pull* — related notes surface
naturally.

---

## Closing

Dreamstate Memory Consolidation makes Ember **grow over
time**. Each day's interactions become tomorrow's
sharpened relevance. The ravens fly out; the ravens return;
the memory deepens.

This is what *years of residence* with an AI companion
produces — not just stored chats, but an evolving memory
that mirrors the operator's mind.

# 44 — Meta-Learning from Episodes

How Ember learns *patterns* from past Episodes — not just
remembering them, but *generalizing* from them. Episode-as-
training-signal for behaviors.

---

## The principle

Each Episode (operator-turn + Ember-reply pair) is a *data
point*. Across hundreds of Episodes, patterns emerge:

- Which types of questions get long vs short replies?
- Which retrieval strategies work for which question types?
- Which tools get invoked for which kinds of operator
  intent?
- When does the operator follow up with "no, I meant…" vs
  "thanks, that's it"?

These patterns can *improve future behavior* — not by
training the underlying LLM (we're sovereign + local), but
by *shaping Ember's choices*.

This is **meta-learning**: learning *how to use* her
existing capabilities better.

---

## What gets learned

Three classes of patterns:

### 1. Question-type → retrieval-strategy mappings

Pattern: "Operator asks 'when did X happen' → date-specific
keyword retrieval works best."
Pattern: "Operator asks 'why' → semantic retrieval with
larger k works best."

These are *retrieval routing* hints. Bifrǫst's per-query
weights can shift based on detected question type.

### 2. Operator preferences

Pattern: "Operator prefers concise replies in the morning."
Pattern: "Operator asks follow-ups when reply > 200 words."
Pattern: "Operator denies CloakBrowser approval 80% of the
time when on the Pi."

These shape *how* Ember responds. Defaults shift over time
toward the operator's evident preferences.

### 3. Tool usage patterns

Pattern: "Operator approves fetch_url 100% of the time for
github.com domains."
Pattern: "Operator denies fetch_url_cloaked for news sites
60% of the time."

These can inform *standing-trust* policies: tools or
domains the operator consistently approves can become
candidates for STANDING-trust elevation (with explicit
confirmation, never silent).

---

## How the meta-learning loop works

```
┌──────────────────┐
│ Episodes persist │ ← happens every chat turn
└──────┬───────────┘
       │
       ▼ (overnight or on-demand)
┌──────────────────┐
│ Pattern analyzer │
│ scans recent      │
│ Episodes          │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Pattern store    │
│ (Mímir or its    │
│ own SQLite)      │
└──────┬───────────┘
       │
       ▼ (consulted per chat turn)
┌──────────────────┐
│ Decision shaping │
│ - retrieval      │
│ - response style │
│ - approval flow  │
└──────────────────┘
```

The analyzer runs **outside chat-turn latency** — async,
batched, opt-in.

---

## How patterns are detected (simply)

Pattern detection in V1 is *rule-based + statistical*, not
ML-based:

```python
def detect_response_length_preference(recent_episodes):
    """If operator follow-up rate spikes with longer replies,
    prefer shorter."""
    by_length = group_by(
        recent_episodes,
        key=lambda e: length_bucket(e.ember_reply),
    )
    for length, episodes in by_length.items():
        followup_rate = sum(1 for e in episodes if e.was_followed_up) / len(episodes)
        if followup_rate > 0.7 and length == "long":
            return Preference(kind="prefer_concise", confidence=0.7)
    return None
```

These are *bounded heuristics*. No black-box ML. Patterns
are inspectable + tunable.

---

## What's learned, what isn't

**Learned (V1)**:
- Operator's preferred reply length.
- Operator's tone preferences (formal vs casual, derived
  from approval patterns).
- Tool approval defaults (per-tool, per-domain).
- Retrieval routing for common question types.
- Times-of-day operator tends to chat (correlates with
  rhythm-aware tone defaults).

**Not learned (V1)**:
- The LLM's weights. We're sovereign + local; we don't
  train Funi.
- The operator's identity / personality. We track
  preferences (behavioral), not psyche.
- "What kind of person they are." Boundaries.

The distinction: we learn *operational patterns*, not
*personal traits*.

---

## How learned patterns affect behavior

### Retrieval routing example

After 50 chat turns with the question pattern "when did X":
- Pattern: keyword search outperforms semantic for these
  questions.
- Stored: `pattern_routing[temporal_questions] = {mimir: 2.0, huginn: 0.5}`
- Next time operator asks "when did Odin lose his eye":
  - Question classified as temporal.
  - Bifrǫst fusion weights adjusted: Mímir gets 2× weight.
  - Result: better answers for date-specific questions.

### Reply length example

After 30 turns where the operator follows up with "be brief"
or doesn't engage with long replies:
- Pattern: operator prefers concise responses.
- Stored: `preference[reply_length] = "concise"`
- Next chat-turn prompt assembly:
  - System prompt augmented: "Operator prefers concise
    responses. Default to 1-3 sentences unless asked for
    more."
- Result: replies fit operator's actual preference.

### Tool approval example

After 20 fetch_url approvals all for github.com:
- Pattern: github.com fetches always approved.
- Stored (but NOT auto-applied): `pattern_suggest_standing[fetch_url, "github.com"] = 0.95`
- Next time operator opens Stofa Settings → MCP screen:
  - Stofa surfaces: "You've approved fetch_url for
    github.com 20/20 times. Set as standing-trust? [y/n]"
- Operator decides; we never silently elevate.

**Sovereignty: patterns inform, but operator confirms.**

---

## What the operator sees

Defaults:
- Patterns affect Ember's behavior silently.
- Operator notices "Ember gets it now" but can't articulate
  what changed.

Surfacing (opt-in):
```yaml
yggdrasil:
  meta_learning:
    surface_patterns_to_operator: true
```

When enabled, Ember occasionally remarks:
- "I've noticed you prefer concise answers — let me know if
  I should expand."
- "Your fetch_url approvals on github.com are at 20/20.
  Should I set this as standing-trust?"

These are *meta-conversations about Ember's own learning*.
Operator-controlled.

---

## What this is NOT

- **Not training a model.** We don't update Funi's weights.
- **Not personality profiling.** We track approval rates,
  not psychological traits.
- **Not surveillance.** Patterns are computed locally;
  nothing leaves the machine.
- **Not auto-acting.** Patterns *suggest*; operator
  *confirms* anything consequential.

---

## Configuration shape

```yaml
yggdrasil:
  meta_learning:
    enabled: true
    analysis_interval_hours: 24      # nightly
    min_episodes_for_pattern: 10      # don't draw from noise
    pattern_store: ~/.ember/yggdrasil/patterns.db
    surface_patterns_to_operator: false
    auto_apply:
      retrieval_routing: true         # safe; just weighting
      reply_length: true              # safe; prompt tweak
      tool_approval_elevation: false  # NEVER without confirm
    pattern_types_enabled:
      - response_length_preference
      - retrieval_routing
      - tool_approval_default
      - time_of_day_preference
```

---

## Performance

Pattern analysis runs nightly; ~30 seconds for a corpus of
1000 Episodes on Pi 5. Stored as small SQLite table
(~10KB per pattern, dozens of patterns).

Pattern lookup per chat turn: <5ms.

Negligible footprint; meaningful behavior shifts.

---

## Risk / known issues

- **Overfitting to recent noise.** A bad week of unusual
  chats could shift Ember's defaults. Mitigation: 30-day
  rolling window for pattern decay; new patterns require
  consistent signal.
- **Operator drift.** What the operator wanted 6 months
  ago isn't what they want now. Patterns *decay* too
  (similar to memory).
- **False patterns.** Spurious correlations. Mitigation:
  conservative confidence thresholds; operator can flush
  patterns.

---

## Operator-facing example

After 3 months of regular use:

Operator runs `ember yggdrasil patterns list`:

```
Active behavioral patterns:

  response_length_preference: concise (confidence 0.82)
    Based on: 47 of last 120 episodes (39%) had follow-ups
    when reply > 200 words. Default reply target: 80 words.

  retrieval_routing[temporal_questions]:
    mimir_weight: 1.8 (default 1.0)
    huginn_weight: 0.6 (default 1.0)
    Based on: 23 episodes; mimir wins 78% of the time.

  time_of_day_tone[evening]:
    bias_toward: introspective (weight 0.3)
    Based on: emotional-intelligence classifier patterns +
    Verdandi rhythm events.

  tool_approval_default[fetch_url, "github.com"]:
    suggested: standing_trust (95% approval rate over 20 calls)
    NOT auto-applied. Run `ember yggdrasil patterns apply
    fetch_url.github` to confirm.

Press q to quit; or specify a pattern to clear/disable.
```

Operator can flush, disable, or apply suggested elevations.
Full visibility, full control.

---

## Closing

Meta-Learning from Episodes is **the path to Ember
*growing into* the operator's working style** — without ML
training, without losing sovereignty, without surveillance.

Bounded heuristics over local Episodes. Patterns inform;
operator confirms. The cumulative effect over months is an
Ember that *fits* the operator better than she did on day
one.

This is what *long-term residence* with an AI companion
looks like.

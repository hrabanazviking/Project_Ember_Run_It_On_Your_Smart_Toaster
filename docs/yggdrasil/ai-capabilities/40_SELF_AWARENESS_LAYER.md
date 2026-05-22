# 40 — Self-Awareness Layer

What Ember can know about her own state, history, and recent
patterns. Powered by Verdandi's event bus.

---

## The principle

Self-awareness in software is **operational introspection**,
not metaphysical consciousness. Ember knowing "I just made a
tool call" or "I've been asked about Odin 5 times this week"
is the same kind of self-awareness a thermostat has when it
knows the current temperature — *useful operational state*,
not *inner experience*.

We build the *useful* kind. We don't claim the other.

---

## What self-awareness enables

Without it, Ember is a black box even to herself. She
answers each chat turn fresh, can't remember she answered a
similar question yesterday, can't notice she's been wrong
recently, can't surface patterns.

With it, she can:

1. **Notice patterns** ("you've asked about Odin a lot")
2. **Reference recent context** ("I tried that approach 2
   minutes ago and it didn't work; let me try a different
   route")
3. **Catch her own errors** ("I cited an old document I now
   recall was contradicted by a newer one")
4. **Surface her state** ("I'm currently waiting on a Funi
   response; the Well is disconnected but I still have
   Episodes from before to draw on")
5. **Recover gracefully** ("My last 3 attempts at tool X
   failed; I'll stop trying X for this turn")

All operationally grounded; none speculative.

---

## How the layer works

```
              ┌──────────────┐
              │   Verdandi    │
              │  event bus    │
              └──────┬───────┘
                     │
                     ▼
           ┌──────────────────┐
           │ AwarenessLayer    │
           │ subscribes to     │
           │ ember.* events    │
           └──────┬───────────┘
                  │
                  ▼ (maintains)
           ┌──────────────────┐
           │ rolling window    │
           │ (last N events,   │
           │  default 1 hour)  │
           └──────┬───────────┘
                  │
                  ▼ (provides)
        ┌──────────────────────┐
        │ summary, queries,     │
        │ pattern detection     │
        └──────┬───────────────┘
               │
               ▼ (consumed by)
        ┌──────────────────────┐
        │ chat prompt assembly  │
        │ + emotional-int.      │
        │ + Stofa StatusBar     │
        └──────────────────────┘
```

The layer is **passive**: it doesn't run during a chat turn;
it accumulates state in the background. Chat turns *query*
it.

---

## What the layer captures

The rolling window holds events of interest:

- `chat.turn_started` / `chat.turn_finished` (with metadata
  — topic keywords, tool calls made, latency)
- `tool.proposed` / `tool.approved` / `tool.executed`
- `bifrost.fusion_completed` (results count, backends used)
- `mimir.contradiction_detected` (if any)
- `awareness.pattern_detected` (its own events; reflexive)
- `funi.request_failed` (errors)

The window is **bounded**:
- Default: last 100 events OR last 1 hour (whichever is
  smaller).
- Operator-tunable.
- Older events fall out; no infinite growth.

---

## How patterns are detected

Pattern detection runs per-window. Examples:

### Topic repetition

```python
def detect_topic_repetition(window):
    topics = [extract_topic(e) for e in window if e.type == "chat.turn_started"]
    counts = Counter(topics)
    for topic, count in counts.most_common(5):
        if count >= TOPIC_THRESHOLD:
            return Pattern(kind="topic_repetition", topic=topic, count=count)
```

Default threshold: 5 occurrences in 24 hours.

### Repeated tool failures

```python
def detect_tool_failures(window):
    failures = [e for e in window if e.type == "tool.executed" and e.payload.get("error")]
    by_tool = group_by(failures, key=lambda e: e.payload["tool_name"])
    for tool, events in by_tool.items():
        if len(events) >= FAILURE_THRESHOLD and len(events) / TOTAL_CALLS > FAILURE_RATIO:
            return Pattern(kind="tool_failure_streak", tool=tool, count=len(events))
```

### Contradicting citations

```python
def detect_contradictions(window):
    contradictions = [e for e in window if e.type == "mimir.contradiction_detected"]
    if contradictions:
        return Pattern(kind="contradiction", count=len(contradictions))
```

These are *cheap heuristics*. They run on every awareness
query (cached for performance). Operators can disable any
pattern via config.

---

## How Ember uses patterns in chat

When the pattern is detected, the awareness layer surfaces
it to the prompt-assembly step:

```
SYSTEM (your awareness state):
  - You've answered 12 questions in the past hour.
  - Recent topics: Odin (5x), Yggdrasil (3x), Norse cosmology
    (2x). Operator seems focused on Norse mythology research.
  - You attempted tool 'fetch_url_cloaked' 3 times in 30 minutes;
    2 of those failed. Consider proposing it less aggressively
    this turn.
  - mimir.contradiction_detected fired between two documents
    about Odin's eye 5 minutes ago. Operator may benefit from
    a heads-up.

OPERATOR INPUT: "tell me more about Odin"
```

The LLM's response naturally incorporates the awareness:

```
Sure — building on our earlier conversation about Odin (and
his ravens, his missing eye, etc.) — here's what's coming up
in your Well now...

(One side note: I noticed two of your sources have slightly
different accounts of his eye sacrifice. Want me to compare
them?)
```

The operator experiences this as **Ember being attentive and
connected to the conversation arc**. Without self-awareness,
each turn would be siloed.

---

## What gets surfaced (operator-controllable)

```yaml
yggdrasil:
  awareness:
    enabled: true
    window:
      max_events: 100
      max_age_s: 3600
    surface_to_chat: true       # whether patterns appear in chat
    surface_thresholds:
      topic_repetition: 5
      tool_failure_streak: 3
      contradiction: 1
    surface_remarks:
      max_per_turn: 1            # don't overwhelm
      cooldown_s: 600            # don't repeat same remark
```

Operators can:
- Disable surfacing entirely (`surface_to_chat: false`).
- Tune thresholds (more or less talkative awareness).
- Cool down repeated patterns (don't keep saying "you've
  asked about Odin a lot").

---

## What self-awareness is NOT

This list matters because misunderstanding causes weirdness:

- **NOT** Ember claiming to "feel" or "remember" in a
  human sense. She references operational records.
- **NOT** Ember predicting what the operator wants. She
  notices patterns; she asks; the operator decides.
- **NOT** Ember acting autonomously based on patterns.
  Tool calls still require approval. Memory writes still
  require explicit ingest. Pattern detection is *surfacing*,
  not *acting*.
- **NOT** persistent self-model. Patterns live in the
  rolling window; they don't accumulate into a "personality
  model" of the operator. (Mímir's Hebbian layer does
  long-term association, but that's *about the data*, not
  *about the operator's psyche*.)

---

## The "I notice…" pattern

When a pattern is salient, Ember surfaces it as a small
remark. Templates:

- "I notice you've been asking about {topic} a lot — want
  me to pin those documents for easier access?"
- "I noticed {tool} has failed a few times — should I stop
  proposing it?"
- "Two of your sources disagree about {topic}. Want me to
  show you both?"

The remarks are **opt-in** (default on; operator can
disable). They're **rare** (cooldown + max-per-turn). They're
**actionable** (each ends with a clear suggestion).

This is the *most operator-visible benefit* of the self-
awareness layer.

---

## Risk / known issues

- **Uncanny valley.** "I notice you've been…" can feel
  surveilling if overdone. Default thresholds + cooldown
  keep it gentle.
- **False patterns.** Keyword-based topic extraction is
  noisy. False positives reduce trust. We tune carefully.
- **Pattern overload.** If 5 patterns fire on the same
  turn, Ember would emit 5 remarks. Cap at 1 per turn.

---

## Operator-facing example

```
[3 days of asking about Norse cosmology]

> volmarr: tell me about Yggdrasil

ember: Yggdrasil is the world-tree in Norse cosmology — it
connects the nine realms and stands over Urð's well...
[full explanation]

(I notice you've been deep in Norse cosmology for a few
days now — should I pin your most-cited sources at the top
of search?)
```

The "(I notice…)" is the awareness layer surfacing a
pattern. Operator says yes or no; Ember acts (or doesn't);
chat continues.

---

## Test strategy

Phase 3 ships:

- **Unit tests** for pattern detectors with synthetic
  event windows.
- **Integration tests** with real Verdandi + simulated chat
  turns; verify "I notice…" fires at correct thresholds.
- **Cooldown tests** verifying the same pattern doesn't
  repeat within the cooldown window.

---

## Closing

The self-awareness layer is **operational introspection in
service of the operator**. Ember knows her own state; she
references it; she surfaces useful patterns; she stays out
of the operator's way when there's nothing worth saying.

This is what makes her a *companion* and not a stateless
endpoint.

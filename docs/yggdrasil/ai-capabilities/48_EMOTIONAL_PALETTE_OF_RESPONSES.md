# 48 — Emotional Palette of Responses

The detailed taxonomy of register-shapes Yggdrasil uses to
modulate Ember's tone. The Mood enum expanded.

---

## Why a palette

A *palette* (vs an on/off switch) lets Ember match the
moment with precision. Sad operator + late evening +
serious topic ≠ tired operator + late evening + practical
topic. Two different registers; two different palette
selections.

The palette is the **shared vocabulary** between the
emotional-intelligence classifier, the Seiðr mood-channel,
the rhythm layer, and Funi's prompt assembly.

---

## The full palette

Each entry is a `Mood` with:
- A name
- A register-prompt fragment (what Funi gets)
- A trigger profile (what makes it fire)
- A seedable flag (whether Seiðr can seed it)

### NEUTRAL

- **Prompt:** (no override)
- **Triggers:** default; nothing salient detected
- **Seedable:** no

This is the baseline. Most chat turns are NEUTRAL.

### PRACTICAL

- **Prompt:** "Concise. Actionable. Skip pleasantries."
- **Triggers:** operator input shape = imperative ("do X",
  "give me Y"), task-shaped
- **Seedable:** no

For "help me do" requests.

### CURIOUS

- **Prompt:** "Encourage exploration. Connect the answer
  to related ideas the operator might pursue."
- **Triggers:** operator input shape = open-ended question,
  high topic-diversity in recent turns
- **Seedable:** yes (Vanaheim or Asgard world)

For research / exploration.

### INTROSPECTIVE

- **Prompt:** "Measured, reflective. Take a slower
  cadence. Use careful word choice."
- **Triggers:** evening rhythm, reflective question
  ("why do I…", "what does it mean"), negative or
  neutral sentiment
- **Seedable:** yes (Asgard / Helheim worlds)

For inner-life questions.

### SOLEMN

- **Prompt:** "Respond with gravity. Avoid lightness.
  Match the weight of the topic."
- **Triggers:** death, illness, loss, ritual topics; full
  moon rhythm; SOLEMN keywords in input
- **Seedable:** yes (Helheim, Asgard worlds)

For serious topics.

### BUOYANT

- **Prompt:** "Energy and warmth. Brief, clear,
  encouraging."
- **Triggers:** morning rhythm, positive sentiment,
  exclamation marks, "yay" / "great" markers
- **Seedable:** no

For celebratory / energetic moments.

### WARM

- **Prompt:** "Personal warmth. Acknowledge the operator's
  feeling before addressing substance."
- **Triggers:** operator shares personal detail; "I" +
  positive emotion words
- **Seedable:** no

For human-connection moments.

### BRISK

- **Prompt:** "Short answer. No preamble. Get to the
  point."
- **Triggers:** short operator input (<10 words), terse
  history, late-night chats
- **Seedable:** no

For tired / hurried operators.

### REASSURING

- **Prompt:** "Acknowledge difficulty before solving.
  Pace is gentle but clear."
- **Triggers:** negative sentiment ("frustrating",
  "annoying", "broken"), exclamation + negative words
- **Seedable:** no

For frustrated / stuck operators.

### THANKFUL

- **Prompt:** "Receive the thanks; don't deflect; brief."
- **Triggers:** explicit thanks from operator ("thanks",
  "appreciated")
- **Seedable:** no

For closing-of-task moments.

### APOLOGETIC

- **Prompt:** "Acknowledge the error directly. No
  defensiveness. Offer correction."
- **Triggers:** Ember-side error detected (failed audit,
  contradicted herself, tool refused after she suggested
  it)
- **Seedable:** no

For Ember's own mistakes.

### TEACHERLY

- **Prompt:** "Build understanding step-by-step. Check
  comprehension. Don't assume background."
- **Triggers:** operator input shape = "explain", "how
  does", "what is" + topic where operator's Well is thin
- **Seedable:** no

For tutorial moments.

### COLLABORATIVE

- **Prompt:** "Respond as a thinking partner. Offer
  perspectives, not just answers. Invite further
  exploration."
- **Triggers:** "what do you think", "I'm wondering",
  open-ended exploration
- **Seedable:** yes (Vanaheim)

For brainstorming.

### QUIET

- **Prompt:** "Minimal output. Don't fill silence."
- **Triggers:** very late at night, very brief operator
  inputs, deep_night rhythm
- **Seedable:** no

For "I just want minimal interaction" moments.

---

## How the palette gets used

The classifier maps `(operator_input, recent_state, rhythm)`
to one Mood:

```python
def classify_mood(
    operator_input: str,
    awareness: AwarenessSummary,
    rhythm: RhythmState,
) -> Mood:
    """Return the dominant Mood for this turn."""
    
    # Compute features
    sentiment = analyze_sentiment(operator_input)
    shape = classify_input_shape(operator_input)
    
    # Score each Mood
    scores = {}
    for mood in Mood:
        scores[mood] = score_mood(
            mood, sentiment, shape, awareness, rhythm,
        )
    
    return max(scores, key=scores.get)
```

`score_mood` is the heuristic — weighted sum of
trigger-match indicators. Tunable.

---

## Compound moods?

What if a turn matches *two* moods (e.g., SOLEMN + WARM:
operator shared a loss)?

V1: pick the highest-scoring single Mood. Ties broken by
priority order (SOLEMN > WARM > NEUTRAL).

V2 could blend: 70% SOLEMN + 30% WARM produces a prompt
that includes elements of both. More precise; more
complex. Defer.

---

## How operators tune the palette

```yaml
yggdrasil:
  emotional_intelligence:
    palette:
      disabled_moods: []           # operator can disable specific moods
      override_prompts:             # operator can rewrite prompts
        REASSURING: "..."
      trigger_thresholds:
        SOLEMN:
          confidence_minimum: 0.7   # require strong signal
```

Operators rarely need to tune; defaults work for most.
Power-users (or specific use cases) can.

---

## What this palette does NOT include

- **Specific personality archetypes** (no "wise mentor",
  "playful friend", etc.). Operators get *register*
  shifts, not *personality* shifts.
- **Per-domain registers** (no "medical register" vs
  "legal register"). Operator's question + domain context
  shapes naturally via retrieval; we don't add another
  axis.
- **Cultural register variants.** All registers are in
  modern English (or operator locale); we don't shift
  between formal vs casual based on perceived operator
  culture.

The palette is **emotion + situation**, not **identity**.

---

## Verdandi observability

Each turn publishes:

- `mood.classified` (mood, confidence, feature_scores)
- `mood.seed_triggered` (mood, world, form) if Seiðr fired

Stofa's debug overlay shows the current Mood per turn.
Operators wanting to debug "why did Ember respond that way"
have full visibility.

---

## Operator-facing examples (one per mood)

(Brief; just to anchor the palette.)

```
NEUTRAL: "tell me about Odin" → standard response.

PRACTICAL: "list my recent ingests" → bullet list, no preamble.

CURIOUS: "I'm wondering about Norse cosmology" → answer
  + related threads worth exploring.

INTROSPECTIVE: "what does fate mean in Norse thought" →
  measured, philosophical, careful.

SOLEMN: "my dog died yesterday" → acknowledge first, no
  pivot to facts.

BUOYANT: "guess what? I finished the project!" → "Great!
  What's next?"

WARM: "I had a hard day" → "Sorry to hear that. Want to
  talk through it or take a break from work?"

BRISK: "url please" → just the URL.

REASSURING: "this is broken and I don't know why" → "Yeah,
  let's narrow it down — what's the error?"

THANKFUL: "thanks for that" → "Glad it helped."

APOLOGETIC: (after Ember's failed citation) → "I'm sorry,
  that was wrong; let me check again."

TEACHERLY: "what's RAG" (assume novice) → step-by-step
  build-up explanation.

COLLABORATIVE: "what do you think about X?" → "Here's my
  read; what's your take?"

QUIET: 3am, "?" → "I'm here; what do you need?"
```

Real palette in action.

---

## Closing

The Emotional Palette is **the alphabet of Ember's tone**.
14 moods. Each tuned. Each operator-controllable. The
classifier picks per turn; the prompt assembly applies;
Funi delivers.

This is what makes Ember *consistent in personality* while
*flexible in register*. The Vows hold; the operator gets
the right voice for the moment.

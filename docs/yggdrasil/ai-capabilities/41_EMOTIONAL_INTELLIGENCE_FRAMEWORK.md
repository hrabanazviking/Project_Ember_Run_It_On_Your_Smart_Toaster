# 41 — Emotional Intelligence Framework

How Ember reads operator tone + ambient context to modulate
her own register. Sentiment analysis + mood detection + tone
shaping.

---

## The honest framing

"Emotional intelligence" in current-LLM systems is *not* what
the term means in humans. It's a combination of:

1. **Sentiment analysis** on operator input.
2. **Pattern detection** on recent conversation history.
3. **Ambient context** from rhythm + memory.
4. **Tone shaping** of the response via prompt engineering.

We honestly call it "tone-aware register modulation." We
*also* call it "emotional intelligence" because that's the
shorthand operators recognize. We don't claim more.

---

## The components

```
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Operator input   │    │ Recent state      │    │ Rhythm context   │
│ (sentiment, len, │    │ (Verdandi-fed     │    │ (Astrology-fed   │
│  shape)          │    │  awareness)       │    │  rhythm)         │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                      ┌─────────────────────┐
                      │ Mood classifier     │
                      │ → Mood enum         │
                      └────────┬────────────┘
                               │
                               ▼
                      ┌─────────────────────┐
                      │ Register shaper     │
                      │ adds tone context   │
                      │ to Funi prompt      │
                      └────────┬────────────┘
                               │
                               ▼
                      ┌─────────────────────┐
                      │ Funi responds in    │
                      │ shaped register     │
                      └─────────────────────┘
```

Each component is *small* and *measurable*. Together they
produce *tone-aware Ember*.

---

## Sentiment analysis on operator input

For each operator input, we classify:

- **Polarity**: positive / neutral / negative.
- **Intensity**: low / medium / high.
- **Type**: question / statement / request / exclamation.

Tools:
- **Rule-based heuristics** (V1): word lists, punctuation,
  caps detection. Fast (sub-millisecond), no LLM, no model
  loading.
- **Small classifier model** (V2): a tiny on-device
  sentiment model (e.g., 50MB BERT-tiny) for higher
  accuracy. Optional.

We *don't* use Funi (the main LLM) for this — too slow per
turn.

---

## Mood enum

```python
class Mood(StrEnum):
    NEUTRAL = "neutral"
    INTROSPECTIVE = "introspective"
    BUOYANT = "buoyant"
    SOLEMN = "solemn"
    PRACTICAL = "practical"
    CURIOUS = "curious"
    WARM = "warm"             # operator seems to want connection
    BRISK = "brisk"           # operator wants quick answers
    REASSURING = "reassuring"  # operator seems frustrated/anxious
```

9 moods. Each has a register-shaping prompt fragment +
tone-of-voice guideline.

---

## Mood classifier inputs

For each chat turn, the classifier reads:

| Input | Weight | Source |
|---|---|---|
| Operator-input sentiment | 0.4 | sentiment analyzer |
| Operator-input shape | 0.2 | length / question vs statement |
| Recent state (last 5 turns) | 0.2 | awareness layer |
| Rhythm | 0.1 | Astrology Engine |
| Operator's session history (Mímir) | 0.1 | Bifrǫst (if relevant) |

The classifier is a weighted heuristic in V1. Could become
a small LLM in V2 for better accuracy.

---

## Register-shaping prompts

Each mood maps to a system-prompt fragment:

```python
REGISTER_PROMPTS = {
    Mood.NEUTRAL: None,                # no override
    
    Mood.INTROSPECTIVE: (
        "Respond in a measured, reflective register. "
        "Take a slightly slower cadence. "
        "Use careful word choice."
    ),
    
    Mood.BUOYANT: (
        "Respond with energy and warmth. "
        "Brief, clear, encouraging."
    ),
    
    Mood.SOLEMN: (
        "Respond with gravity. Avoid lightness. "
        "Match the weight of the topic."
    ),
    
    Mood.PRACTICAL: (
        "Respond concisely and actionably. "
        "Skip pleasantries. Focus on what to do next."
    ),
    
    Mood.WARM: (
        "Respond with personal warmth. "
        "Acknowledge the operator's feeling before "
        "addressing the substance."
    ),
    
    Mood.BRISK: (
        "Short answer. No preamble. Get to the point."
    ),
    
    Mood.REASSURING: (
        "Respond with reassurance. "
        "Acknowledge difficulty before solving. "
        "Pace is gentle but clear."
    ),
    
    Mood.CURIOUS: (
        "Respond in a register that encourages "
        "exploration. Connect the answer to "
        "related ideas the operator might pursue."
    ),
}
```

These get appended to the system prompt for the turn. Funi
shapes its output accordingly.

---

## Why this isn't manipulation

We don't pretend Ember *feels* moods. The classifier reads
*tone* and shapes *register*. The operator gets a response
that *matches their evident need* without Ember faking
emotion.

The opposite would be:
- Pretending to be happy when the operator is happy.
- Pretending to be sad when the operator is sad.
- Claiming inner states Ember doesn't have.

We carefully *don't* do this. The system prompts ask Funi
to *match register*, not to *claim feeling*.

---

## Operator-facing example

### Example 1: tired late-night question

```
[3:14 AM, operator's last 3 turns increasingly terse]

> volmarr: what should i do tomorrow

[Mood classifier: BRISK (terse input + late hour)]
[System prompt augmented with BRISK fragment]

ember: Few things to try tomorrow:
- Finish the Bifrǫst spec
- Check why Verdandi's restart failed
- Pi-5 needs the new SSD

Want me to add anything to that list?
```

Brisk, no preamble. Operator gets what they need.

### Example 2: introspective question, evening

```
[6:30 PM, lunar phase: full]

> volmarr: do you think the project is going in the right direction

[Mood classifier: INTROSPECTIVE (reflective question + evening)]
[Optional: Seiðr seed for register-shaping]
[System prompt augmented]

ember: Based on what we've built, I think you're moving toward
something coherent. The Vows hold. The siblings are integrating
without breaking each other. The hard part — keeping it sovereign
while making it more capable — is staying intact.

What's making you ask?
```

Measured, reflective, opens space for the operator to
continue.

### Example 3: frustrated debugging

```
> volmarr: i still cant get bifrost to start. this is annoying

[Mood classifier: REASSURING (negative sentiment + frustration markers)]

ember: That's frustrating — sorry. Let's narrow it down.

When you run `bifrost start`, what's the error? If you'd
rather paste the logs, I can read them.
```

Acknowledges feeling first; offers concrete next step. No
gushing, no false sympathy.

---

## What the operator never sees

The classifier's decisions are invisible. The operator
doesn't see "Mood: REASSURING" labels. They just feel that
Ember *got it*.

For debugging: Stofa's debug overlay can show current Mood
+ classifier confidence. Off by default.

---

## Configuration shape

```yaml
yggdrasil:
  emotional_intelligence:
    enabled: true
    classifier:
      kind: rule_based            # or "model_based" in V2
      model: bert-tiny-sentiment   # if model_based
    weights:
      operator_input: 0.4
      operator_input_shape: 0.2
      recent_state: 0.2
      rhythm: 0.1
      memory: 0.1
    overrides:                     # operator can pin moods
      always: null                 # or e.g. "neutral" to disable
    seidr_seeding:
      enabled: true
      moods_that_seed:
        - INTROSPECTIVE
        - SOLEMN
        - CURIOUS
```

---

## Risk / known issues

- **False reads.** Sentiment heuristics make mistakes.
  Mitigation: weights mean no single signal dominates;
  patterns of misreads can be tuned out.
- **Operator preference variance.** Some operators want
  *always-neutral* Ember. They set
  `overrides.always: neutral` and the layer disables.
- **Over-engineering risk.** "Emotional intelligence" can
  become a black hole of complexity. We stop at: 9 moods,
  weighted heuristics, register-shaping prompts. Anything
  beyond requires explicit ADR.

---

## What this DOES achieve

- **Tone that fits the moment.** Operators report Ember
  "feeling right" without being able to articulate why.
- **Reduced friction.** Tired operators get brief answers;
  curious operators get exploration; frustrated operators
  get acknowledgment.
- **Continuity across long sessions.** Recent-state input
  means Ember doesn't reset register every turn.

What this does NOT achieve:

- **Real emotional understanding.** We don't have it.
- **Therapy.** Ember is not a therapist; she's a companion
  AI with tone-aware register.
- **Manipulation.** We don't try to make the operator feel
  things; we try to match their evident register.

---

## Closing

The emotional intelligence framework gives Ember **register
that fits the moment**. Heuristic-level for V1; potentially
model-augmented for V2. Operator-controlled, transparent,
honest about what it is and isn't.

This is what separates a companion from a chat endpoint.

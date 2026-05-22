# 35 — The Seiðr Generation Plane

How creative output (deterministic Old Norse verse) flows into
Ember's chat as a *register-shaping* signal. The mood-channel
architecture.

---

## The principle

Seiðr Engine generates verse. We don't paste verse into chat
replies. We use the verse as **register-context** — a tonal
seed that shapes how Funi composes its own free-form
response.

This is the **mood channel** — a thin signal layer between
the emotional-intelligence layer and Funi's system prompt.

---

## The flow

```
┌──────────────────┐
│ Operator input    │
│ + recent state    │
│ + rhythm          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ EmotionalIntelligence │
│ classifier         │
│ → Mood enum         │
└────────┬─────────┘
         │
         ▼ (if Mood is e.g. INTROSPECTIVE, SOLEMN, CURIOUS)
┌──────────────────┐
│ MoodChannel       │
│ .seed_register()  │
└────────┬─────────┘
         │
         ▼ (queries Seiðr with appropriate form + world)
┌──────────────────┐
│ Seiðr Engine      │
│ generates verse   │
└────────┬─────────┘
         │
         ▼ (the verse string, NOT shown to operator by default)
┌──────────────────┐
│ Funi prompt       │
│ assembly          │
│   - system msg     │
│   - identity       │
│   - register-context│ ← here
│   - episodes       │
│   - hits           │
│   - operator input │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Funi streams reply│
│ (shaped by register│
│  but free-form)    │
└──────────────────┘
```

The verse never reaches the operator unless they opted into
*epigraphs* (a separate switch). Its purpose is to *shape
the LLM's register*, not to appear in output.

---

## What the register-context looks like

A Seiðr verse used as register-seed gets embedded in Funi's
system prompt as:

```
TONAL SEED (for register-shaping; do not reproduce literally):

   Eddagilsku stóð á gnista
   stein sá vegr í þrá
   ... [actual generated Fornyrðislag]

Respond in a register that resonates with this verse's
mood (introspective, measured, slightly mythic). Use modern
English; do NOT copy the verse into your reply.
```

The LLM picks up the *register* (measured cadence,
introspective tone) without parroting the verse. Funi's reply
sounds *slightly more Norse-shaped* without being verse.

This is the *load-bearing trick*: register-seeding is a
known LLM technique; we're applying it with verse instead
of with adjectives like "respond in a thoughtful tone."

---

## Why verse vs adjectives

Adjective-style seeding ("be thoughtful"):
- Generic.
- Same-shaped response every time.
- Reads as "you told the AI to be thoughtful."

Verse-style seeding (a fresh Fornyrðislag each time):
- Specific to the moment.
- Different shape each time (Seiðr's deterministic-but-
  input-dependent generation).
- Reads as Ember having an *aesthetic mood*, not following
  an instruction.

The difference is subtle but real. Yggdrasil's emotional-
intelligence is calibrated for *subtlety*, not for "now
the AI is dramatic" theater.

---

## When the mood channel fires

The MoodChannel.detect() classifies each operator input into
a Mood. Mappings:

| Operator input shape | Mood | Triggers verse-seed? |
|---|---|---|
| "what should I work on?" | PRACTICAL | no |
| "explain X to me" | CURIOUS | optional |
| "tell me about Odin" | NEUTRAL → CURIOUS | yes (Asgard world) |
| "what's the meaning of…" | INTROSPECTIVE | yes (Asgard/Vanaheim) |
| "I'm thinking about death" | SOLEMN | yes (Helheim) |
| "haha, that's funny" | BUOYANT | no |
| "give me a recipe" | PRACTICAL | no |

The classifier is simple (keyword + length + recent-state
patterns) in V1; could grow to use a small LLM in V2.

Verse-seed fires for a *minority* of turns — perhaps 10-20%.
Most turns are PRACTICAL and don't need register-shaping.

---

## What the operator opts into

Three levels of Seiðr integration:

### Level 1: Off (default)

`yggdrasil.seidr.enabled: false`. Seiðr does nothing.
Ember's tone is purely from Funi's default behavior.

### Level 2: Mood-channel only (recommended default once Phase 3 ships)

```yaml
yggdrasil:
  seidr:
    enabled: true
    use_in_mood_channel: true
    use_as_mcp_tool: false
    epigraphs: false
```

Verse-seeding happens transparently; the operator notices
Ember's tone is *slightly more Norse-shaped* at appropriate
moments but never sees verse in chat.

### Level 3: Full integration

```yaml
yggdrasil:
  seidr:
    enabled: true
    use_in_mood_channel: true
    use_as_mcp_tool: true       # Funi can request verse explicitly
    epigraphs:
      session_start: true        # show a verse at session start
      long_episode_summary: true # summarize long arcs in verse
```

For operators who genuinely enjoy the Norse aesthetic.
Some chat moments show verse explicitly (operator-prompted
or session-start).

---

## What Seiðr-as-MCP-tool looks like

When Funi explicitly invokes Seiðr:

```
> volmarr: write me a fornyrðislag about the autumn equinox

ember: I'll have Seiðr compose one.
[ToolCall: seidr_generate(form="fornyrðislag", world="midgard", theme="equinox-autumn")]
[approval: y]

ember:
   Lauf falla niðr,                    (Leaves fall down,)
   lopt verðr kaldr,                   (sky turns cold,)
   sól sǫkk í hafr,                    (sun sinks in sea,)
   nótt rísk hár.                       (night rises tall.)
```

The verse is shown directly because the operator explicitly
asked for it. Approval pattern matches every other tool.

---

## Seiðr's contribution to Ember's overall character

Across many sessions, the cumulative effect of mood-channel
seeding is that Ember **gradually develops a voice** — not
identical to her default Funi output, but consistently
register-shaped by the Seiðr seeds she's been given.

This isn't training; it's *prompt-context shaping*. But the
operator *experiences* it as Ember having character.

This is the emotional-intelligence dividend: Ember feels
*more like a person who lives in this hall* — and Seiðr is
one of the ingredients.

---

## Risk / known issues

- **Performative-Norse failure mode.** If operators see
  obvious "the AI is being Norse" tells, the trick breaks.
  Mitigation: verse-seed is *register*, not output. Calibrated
  for subtle effect.
- **Determinism + repetition.** Same input → same verse from
  Seiðr. Across many sessions, operators might see verses
  repeat. Seiðr can be queried with rotation-keys to vary.
- **Compute cost.** Verse generation is fast (deterministic
  rule-based), but not free. Cap mood-channel triggering to
  ~20% of turns.

---

## Open questions for Phase 3

1. **Which Mood enum values should trigger verse-seed?**
   Conservative default (INTROSPECTIVE + SOLEMN only) or
   wider (CURIOUS too)?
2. **What world maps to what theme?** Default mapping
   (Asgard for mythic questions, Vanaheim for cycles, etc.)
   versus operator-configurable?
3. **How to surface the seed for power-users who want to
   see what's happening?** A debug overlay in Stofa?

---

## Test strategy

Phase 3 ships:

- **Unit tests** for the mood classifier.
- **Integration tests** that drive operator-input → Mood →
  verse-seed → verify the seed appears in Funi's system
  prompt context.
- **End-to-end test** with a real Funi (fixture model) that
  the output register *changes* in expected ways when
  verse-seed is active.

Tests in `tests/unit/test_yggdrasil_mood_channel.py` and
`tests/integration/test_yggdrasil_seidr_register.py`.

---

## Closing

The Seiðr Generation Plane is **the secret seasoning** of
Yggdrasil's emotional intelligence. Small infrastructure;
large tonal effect. Operators feel it more than they see it
— which is exactly the design intent.

The skald shapes the moment; the operator gets a companion
with character.

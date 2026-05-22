# 14 — Sibling: Seiðr Engine

> *"Wyrd bid ful araed."* (Fate is fully fixed.)

Deterministic Old Norse poetry generator. Rule-based. Four
metrical forms. Nine Worlds lexicon.

---

## What it is

A pure-functional Python library that generates verse in four
Old Norse poetic meters:

| Form | Lines | Character |
|---|---|---|
| **Fornyrðislag** | 4 | Most ancient Eddic meter — concise, proverbial |
| **Ljóðaháttr** | 6 | Song-meter of the Hávamál — wisdom, prophecy |
| **Dróttkvætt** | 8 | Court meter — strict alliteration AND rhyme |
| **Málaháttr** | 8 | Speech-meter — narrative, room to breathe |

Vocabulary organized by the **Nine Worlds of Yggdrasil**:
Asgard (gods, sovereignty), Vanaheim (Vanir, fertility),
Alfheim (light elves, beauty), Midgard (humans, hearth), and
five more.

**No AI text generation.** Pure algorithmic composition within
metrical constraints. The skald is the *engine*; the operator
provides theme + form.

---

## Why this sibling matters for Yggdrasil

Two distinct purposes:

### 1. Mood-channel for chat tone

Ember's emotional-intelligence layer (per
[`../ai-capabilities/41_EMOTIONAL_INTELLIGENCE_FRAMEWORK.md`](../ai-capabilities/41_EMOTIONAL_INTELLIGENCE_FRAMEWORK.md))
needs ways to modulate her tone. Seiðr provides a *mood
channel*:

- When a chat moment calls for solemnity, Ember can invoke
  Seiðr to generate a brief Fornyrðislag fragment (4 line
  Eddic meter), use it as inspiration for her own response's
  register, optionally surface a line as quote/epigraph.
- When the operator's mood is buoyant, Ljóðaháttr (wisdom-
  meter) feels right.
- For narrative explanations, Málaháttr (speech-meter).

Critically: **Seiðr's verse is not the chat reply**. Ember's
reply is still her own. Seiðr's role is to provide *tonal
seed material* the LLM can use as register-context.

### 2. Optional epigraph / dedication

For operators who enjoy Norse aesthetics, certain Ember
events can be marked with a Seiðr line:

- Session-start vignette: "Today's verse:" + a 4-line
  Fornyrðislag from Asgard lexicon.
- Long Episode summary: a 6-line Ljóðaháttr distilling the
  conversation's theme.
- First-time ingest of a new corpus: a verse marking the
  occasion.

All operator-toggleable. Off by default.

---

## How Yggdrasil integrates Seiðr

### Integration role

Seiðr becomes:

1. **An MCP tool**: `seidr_generate(form, world, theme)` that
   returns verse on demand. Ember's chat loop can invoke this
   like any other tool (with approval).
2. **A direct library call in the emotional-intelligence
   layer**, when the layer decides to seed a tone-context.
3. **An MCP server (optional)**: operators can run Seiðr as
   a separate MCP server and have multiple agents (not just
   Ember) call it.

### Configuration shape

```yaml
yggdrasil:
  seidr:
    enabled: true
    use_as_mcp_tool: true     # register as ember tool
    use_in_mood_channel: false # opt-in for direct integration
    default_world: midgard
    epigraphs:
      session_start: false
      long_episode_summary: false
```

### When Seiðr is invoked (mood-channel mode)

The emotional-intelligence layer decides Ember's response
register. When the register lands in a "solemn / mythic /
introspective" zone, the layer can:

1. Query Seiðr for a 2-4 line verse fragment matching the
   detected mood and the conversation's world-theme (Asgard
   for sovereignty, Vanaheim for cycles, etc.).
2. Pass the verse to the Funi prompt-assembly step as a
   *register-context-item*: "respond in the spirit of this
   verse fragment."
3. NOT include the verse literally in the response (unless
   the operator opted into epigraphs).

This makes Ember's tone *subtly Norse-shaped* without ever
forcing the operator to read runes or decipher metric form.

---

## Risk / known issues

- **Performative-Norse failure mode.** If Seiðr lines start
  appearing in chat replies prominently, it crosses into
  cosplay register. Mitigation: epigraphs are off by default;
  the mood-channel uses Seiðr as *seed-context* only, not as
  output.
- **Cultural-appropriation question.** Old Norse poetry is
  cultural heritage; we approach it with the *operator's*
  evident interest as license. Ember doesn't claim
  scholarship; she invokes verse as ornament + mood.
- **Determinism = repeatability.** Same input → same verse.
  Operators who run the same chat with the same mood-state
  get the same Seiðr line. Charming or repetitive depending
  on perspective.

---

## Test strategy

Phase 3 ships:

- **Unit tests** for the Seiðr-tool adapter (MCP wrapper).
- **Mood-channel integration test** — drive the emotional-
  intelligence layer to a target mood, verify Seiðr is
  invoked with the right form + world.
- **Verse-quality tests** (already in Seiðr's own test suite,
  not duplicated).

Tests in `tests/unit/test_yggdrasil_seidr_tool.py`.

---

## Operator-facing example

After Phase 3, a quiet evening chat:

```
> volmarr: tell me about Odin's sacrifice on Yggdrasil

ember:
[mood-channel detected: introspective, evening, Asgard-themed]
[Seiðr seeded with 4-line Fornyrðislag — used as register only]

Odin hung on the world-tree for nine nights, pierced by his
own spear, dedicated to himself — a sacrifice of self to
self. He learned nine mighty songs that night, and the
runes...

(if epigraphs enabled, a verse line might appear above the
response — e.g. *"Nine nights I hung on the windswept tree…"*)
```

The reply is *Ember's own writing*. Seiðr's contribution is
the *register* — slightly more measured, more verse-cadenced,
more weight per phrase — than her default tone.

---

## Closing

Seiðr is the *register-shaping* layer. Tiny code footprint;
large tone impact. Optional and operator-toggleable end to
end. When invoked, it makes Ember sound *more like she lives
in the hall* — without ever requiring the operator to read
runes themselves.

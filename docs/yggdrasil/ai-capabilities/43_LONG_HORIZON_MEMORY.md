# 43 — Long-Horizon Memory

How Ember holds memory across weeks, months, years. The
composition of Mímir's decay, Muninn's associations, and
operator-controlled reinforcement.

---

## The problem with current LLM "memory"

Default LLM chat:
- No memory between sessions (unless explicitly persisted).
- "Memory" is just the current context window (limited).
- Every turn within a session starts fresh of intent.

Default Ember:
- Episodes persist across sessions (the conversation
  history is in the Well).
- But Episodes are *flat* — every old chat is equally
  retrievable, equally dim.

Long-horizon memory should be like a human's: **recent and
reinforced things are sharp; old and unreinforced things
fade; nothing is lost**.

Yggdrasil delivers this through Mímir + Muninn + operator
controls.

---

## The three memory dimensions

| Dimension | Implementation | What it does |
|---|---|---|
| **Recency** | Mímir's Ebbinghaus decay | Recent things rank higher; old things lower |
| **Reinforcement** | Mímir's promotion + Muninn's Hebbian | Returned-to things rise; ignored things fall |
| **Association** | Muninn's Hebbian links | Things that co-occur become discoverable together |

All three operate continuously, in background processes
that run while Ember is idle.

---

## How Ebbinghaus decay works

Hermann Ebbinghaus (1885) observed that memory decays
exponentially without reinforcement. The curve:

```
retention = e^(-t / S)
```

Where `t` is time since last access and `S` is the memory's
"stability" (which grows with each reinforcement).

Mímir applies this *to chunk relevance scores* (not to the
chunks themselves; nothing is deleted).

Effect over time:
- Day 0: chunk has weight 1.0.
- Day 7 (no reinforcement): weight ~0.5.
- Day 30: weight ~0.05 (effectively background).
- Day 7 with daily reinforcement: weight stays ~1.0.
- Day 30 with daily reinforcement: weight stays ~1.0, S has
  grown so future decay is slower.

The chunk is *always retrievable*; it just ranks lower in
results until reinforced.

---

## How reinforcement works

When the operator's chat-turn retrieves a chunk (via
Bifrǫst's hybrid search), that chunk gets a small
reinforcement boost:

- Direct access (chunk appeared in top-k): +0.2 weight,
  stability ↑.
- Operator clicked through to the citation in Stofa: +0.5
  weight.
- Operator explicitly bookmarks / pins via UI: +1.0
  weight, stability ×2 (effectively long-term).

This compounds. A document the operator returns to weekly
stays sharp; one they ignore fades to background.

---

## How Muninn's associations work

Each time two chunks appear in the same chat-turn's
context, their Hebbian association strengthens:

```
weight(a, b) = weight(a, b) + learning_rate * activation(a) * activation(b)
```

Effect: chunks that *tend to be relevant together* form a
*cluster*. When the operator asks a question, retrieval
pulls one chunk from the cluster; the cluster's other
members get ranked-up too (via Muninn's contribution to
the fusion).

This is the "intuition" layer. Ember surfaces things that
*belong with* what the operator asked, even if those things
don't directly match the query.

---

## Long-horizon scenarios

### Scenario 1: The operator's evolving interest

Operator spends a month deeply researching Odin.
- 100 chats about Odin
- 50 documents ingested about Norse mythology
- Daily reinforcement of the Norse cluster

After the month: the Norse cluster is *sharp*. Mímir
weights are high. Muninn associations are strong.

Operator pivots to a new topic (Greek philosophy). They
chat about Greek for a week.
- The Greek cluster begins to form (new associations).
- The Norse cluster begins to decay (Mímir weights drop
  slowly).

Three months later: Operator asks a Norse question on a
whim. Even though decayed, the Norse cluster is
*recoverable* — the chunks are still in Mímir + Huginn +
MemPalace; the question reinforces them; within minutes
they're back to high weight.

**Memory that ebbs and flows with operator interest,
without losing anything.**

### Scenario 2: Cross-topic associations

Operator reads about both Odin and the Greek god Hermes.
Both are "messengers / wisdom" archetypes.

Over time, Muninn notices: queries about Odin sometimes
surface Hermes documents, queries about Hermes sometimes
surface Odin documents (because operator has connected them
mentally; they tend to co-occur in chats).

The association *encodes the operator's own mental
synthesis*. Ember's retrieval reflects the operator's
intellectual structure, not just textual similarity.

### Scenario 3: The forgotten note

Operator wrote a note 2 years ago and never returned to it.
Mímir's weight is near-zero. Standard semantic search would
rank it last.

Operator asks a question whose answer happens to be in that
old note. Hybrid retrieval (Bifrǫst):
- Mímir: rank low (decayed weight)
- Huginn: rank high (vector similarity is independent of
  decay)
- Muninn: rank middling (no recent associations)
- Fusion: chunk surfaces in top-10

The operator gets the note; reinforces it; weight bumps;
note returns to active memory.

**Old notes aren't lost — they're recoverable when their
content matters.**

---

## What operators control

```yaml
yggdrasil:
  long_horizon_memory:
    decay:
      enabled: true
      half_life_days: 14
      background_interval_hours: 6
    reinforcement:
      enabled: true
      direct_access_boost: 0.2
      click_through_boost: 0.5
      pin_boost: 1.0
      stability_multiplier_on_pin: 2.0
    associations:
      enabled: true
      learning_rate: 0.05
      pruning_threshold: 0.01
```

Operators tune the curves to match their use case. Defaults
work for typical operator-as-research-companion.

---

## The "memory garden" mental model

Operators benefit from thinking of their Well as a *garden*:

- **New seedlings** (recently-ingested) need light + water.
- **Returned-to plants** thrive (reinforcement).
- **Ignored plants** wilt but don't die (decay).
- **Spring brings everything back** (reinforcement of old
  notes triggers Muninn associations + Mímir promotion).

This metaphor isn't in code; it's a way of thinking about
the system. Stofa's WellScreen could surface "garden state"
(V2): "12 recently-watered notes; 5 newly planted; 100 in
slumber."

---

## Why this is more than current SOTA

Current state-of-the-art for LLM "memory":

- **Long context windows** (100K+). But every token is
  equal weight; no relevance shaping over time.
- **RAG with vector search.** Better, but no decay; old
  documents rank same as new.
- **External memory tools** (e.g., mem0, MemPalace).
  Sometimes good; usually missing the association layer
  AND the decay-aware fusion.

Yggdrasil combines:
- Decay (Mímir) for recency-shaping.
- Vector search (Huginn) for semantic recall.
- Association (Muninn) for "intuition."
- Verbatim recall (MemPalace, optional) for exact references.
- Fusion (Bifrǫst) for composition.

**No other open-source AI memory system has all four.** This
is genuinely SOTA.

---

## Risk / known issues

- **Decay surprises.** "Why isn't this note showing up?"
  — answer: it decayed. Mitigation: Stofa shows decay
  state; operator can pin.
- **Cold-start.** New operators have empty Muninn; no
  associations yet. Takes time (weeks) to build. Honest
  about this.
- **Memory drift over months.** The garden's overall shape
  changes. Operators who want stability can disable decay
  (`enabled: false`); memory becomes static like
  traditional RAG.

---

## Operator-facing behaviors

After 3+ months of regular use, operators report:

- "Ember remembers what I've been thinking about."
- "She brings up old notes I'd forgotten that suddenly
  fit."
- "When I return to an old topic, the relevant docs come
  back fast."
- "She seems to *understand* the connections I've made."

These are emergent from the long-horizon memory composition.

---

## Closing

Long-Horizon Memory makes Ember **a companion who grows
with the operator over time**. Not just storage. Not just
retrieval. A *living memory model* that mirrors how the
operator actually thinks and works.

Years of use produce an Ember that *knows the operator's
mind* in the operational sense — what they care about, what
connects to what, what's recent vs forgotten. This is what
makes Ember worth keeping for the long term.

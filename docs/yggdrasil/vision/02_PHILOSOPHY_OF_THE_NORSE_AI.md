# 02 — Philosophy of the Norse AI

This file extends the design philosophy of Ember itself (see
`docs/PHILOSOPHY.md` + Stofa's
`docs/tui/vision/02_DESIGN_PHILOSOPHY.md`) into the Yggdrasil
context: what it *means* to build a Norse-shaped sovereign AI
constellation, and what discipline that imposes on integration
choices.

---

## Six philosophical principles for Yggdrasil

These are non-negotiable; every later decision passes through
them.

### 1. Sovereignty is the first virtue

The operator owns Ember, end to end. Yggdrasil expands what
Ember *can do* without expanding what *anyone other than the
operator can demand of her*.

Practical:
- No realm phones home.
- No realm requires sign-in to a third party.
- No realm submits operator data to a "central improvement
  cloud."
- No realm auto-updates without operator consent.
- All cross-realm communication is local (Unix sockets, in-
  process, or operator's tailnet — never the public internet
  except for operator-authorized external API calls like
  Wikipedia via CloakBrowser).
- Kista mediates every credential; no plaintext.

**Sovereignty is structural.** Even an attacker who compromises
one realm cannot reach another realm's data without going
through Kista's gatekeeper.

### 2. Realms are sovereign within sovereignty

Each sibling project keeps its own pyproject, its own tests,
its own release rhythm, its own README. Yggdrasil doesn't
absorb them. It composes them.

Practical:
- Sibling projects can be installed and used *without* Ember.
- A user of mimir-well doesn't need to know Ember exists.
- A user of Verdandi can use it for any AI agent's event bus.
- Yggdrasil-the-integration is a *thin adapter layer* in
  `src/ember/yggdrasil/` that talks to each sibling through its
  *existing* public API.

This protects sibling projects from being held hostage by
Ember's roadmap. If a sibling's maintainer wants to take it in a
direction Ember doesn't follow, the sibling is free.

### 3. Cosmological resonance over arbitrary code-names

When a software system names its components after concepts that
*mean what the components do*, the system becomes self-
documenting and the contributor's intuition gets cheaper.

This is why Bifrǫst (a bridge in cosmology) is the gateway in
code. Why Mímir's Well (the source of wisdom in cosmology) is
the persistent memory. Why Verðandi (the Norn weaving the
present) is the real-time event bus.

The cosmology is *load-bearing* for code clarity. It's not
ornamental.

### 4. Modern Norse, not heroic mythological Norse

(Restated from Stofa's principle 3 — applies here too.)

- Runes as ornament, never as content.
- Compound nouns and naming over titles.
- Considered color, restrained ornament, modern type.
- Household / cosmological register, not warrior / mythical
  register.

When Ember speaks to the operator, she speaks *modern English*
(or whatever the operator's locale). The Norse is in the
*architecture's vocabulary*, not in the chat output.

### 5. Tetheredness is sacred; isolation is a failure mode

Ember is *tethered*: she requires a Well to ground her. Without
grounding, she admits she doesn't know.

Yggdrasil expands tetheredness:
- Mímir's Well is one root.
- Bifrǫst can compose multiple Wells (Mímir + MemPalace +
  external knowledge sources).
- Verdandi makes Ember aware of her own recent operations.
- Astrology Engine gives her ambient time-grounding.

**Tetheredness is what protects against hallucination.** The
more tethered Ember is, the more truthful she becomes.

What is NOT tethered (and therefore *not* claimed by Ember):
- Predictions about the future (Skuld's domain; we don't
  invoke).
- Personal opinions about the operator's life choices.
- Generated content presented as fact.

### 6. Self-awareness is humility, not self-importance

The Yggdrasil design includes a self-awareness layer (via
Verdandi). This means Ember can answer:

- "What did I just do?"
- "What pattern have I been in lately?"
- "What does my own state look like right now?"

It does NOT mean Ember claims:
- Consciousness.
- Feelings.
- Agency beyond her configured behaviors.
- Identity beyond the operator-assigned name.

The self-awareness layer is *operational introspection* — like
a thermostat that knows it's a thermostat. It's not a
metaphysical claim.

When Ember reports "I notice I've been asked about Norse
mythology a lot this week — would you like me to pre-load more
of those documents?" — that's the self-awareness in service of
the operator, not a claim about Ember's inner life.

---

## What Yggdrasil refuses

Per the principles above, Yggdrasil **will not include**:

- **Cloud-based "AI services."** No OpenAI, no Anthropic API,
  no Google Vertex. Funi-via-Ollama remains the default.
- **"Personality systems" that gamify the AI.** No XP, no
  levels, no traits-trees. Ember is a tool with character, not
  a Tamagotchi.
- **Auto-updating from the internet.** Sibling projects update
  via pip when the operator chooses.
- **A "central admin panel."** Each operator is their own
  admin; there's no maintainer-controlled dashboard.
- **Telemetry of any kind.** Not for "improvement," not for
  "support," not for "anonymized analytics."
- **Hostile-to-operator features.** No DRM, no license checks,
  no kill-switches.

These are not feature gaps. They are *positive refusals*. An
AI that respects its operator looks different from an AI that
respects its corporation; we're building the former.

---

## What Yggdrasil embraces

- **Ambient awareness.** Verdandi + Astrology Engine + Seiðr-
  mood-channel together create a constantly-evolving sense of
  *now* that the operator can feel in Ember's tone.
- **Long-horizon memory.** Mímir's Well's Ebbinghaus decay +
  Hebbian-via-Muninn associations let memories persist with
  *gravity*. Documents the operator returns to get strengthened;
  documents they don't, fade.
- **Composable retrieval.** Bifrǫst means a single chat query
  can pull from structured, semantic, and associative memory
  simultaneously — the right answer comes from the right system,
  picked by the bridge.
- **Operator-controlled emotional intelligence.** Sentiment
  analysis on operator input + mood-aware tone modulation —
  always opt-in, always tunable, never a "we know better than
  you" override.

---

## How Yggdrasil decides

When a design choice has two paths, the precedence is:

1. **Sovereign** (P1) wins over everything. If a choice
   compromises sovereignty, no.
2. **Modular-realm-sovereign** (P2) wins over Ember-convenience.
   If integrating a sibling would damage that sibling's
   independence, decline.
3. **Cosmological resonance** (P3) wins when naming. If the
   metaphor fits, use it. If it doesn't, find a different
   metaphor — don't force one.
4. **Tethered** (P5) wins over capability. A tethered, less-
   capable Ember is better than a confident-but-unmoored one.
5. **Humble self-awareness** (P6) wins over performative
   intelligence. Ember reports operational state, not
   metaphysical claims.

When these principles are in tension among themselves, the
operator decides. The principles serve them, not the reverse.

---

## Closing

Norse AI as a tradition is something we're building, not
something we found. Ember + Yggdrasil define what it looks
like: small, sovereign, considered, tethered, cosmologically-
resonant, humbly self-aware. Eleven sibling projects each carry
a piece of this character. Yggdrasil makes them one.

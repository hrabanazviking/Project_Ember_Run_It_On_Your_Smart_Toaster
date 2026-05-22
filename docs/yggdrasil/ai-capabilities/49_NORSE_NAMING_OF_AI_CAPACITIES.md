# 49 — Norse Naming of AI Capacities

How Yggdrasil names each new AI capability in Norse-aligned
terms. The Skald's contribution to internal vocabulary.

---

## Why this matters

Vocabulary shapes thinking. When a project's internal terms
are flat ("memory system #4", "tone module #2"), the
contributor's intuition stays flat. When the terms have
*meaning* (Mímir's Well, Verðandi, Seiðr), the architecture
becomes *self-describing*.

This document is the **canonical glossary** of AI capacities
in Yggdrasil's Norse vocabulary.

---

## The glossary

Each entry: **Norse term · pronunciation · what it names ·
why this name fits**.

### Memory capacities

- **Mímisbrunnr** *(MEE-mis-bru-ner)* — the persistent
  decay-aware memory backend (mimir-well sibling). *Why*:
  in cosmology, Mímir's Well is the source of wisdom; Odin
  pledged an eye to drink from it. The metaphor fits a
  memory backend that takes effort (and dedication) to
  reach.

- **Huginn** *(HOO-gin)* — the vector-based semantic
  search backend (Qdrant). *Why*: Hugin = "thought" in Old
  Norse, one of Odin's two ravens. The flight of the
  thought-raven mirrors the leap of vector-space
  retrieval.

- **Muninn** *(MOO-nin)* — the associative Hebbian memory
  layer. *Why*: Munin = "memory" in Old Norse, the second
  raven. Associative memory binds *what occurs together*;
  that's what the memory-raven does in the cosmology.

- **Bifrǫst** *(BIV-rohst)* — the composite memory gateway.
  *Why*: Bifrǫst is the rainbow bridge between realms; this
  bridge stands between the agent and the multi-realm
  memory.

### Self-awareness + observability

- **Verðandi** *(VER-than-dee)* — the present-moment event
  bus. *Why*: Verðandi is the Norn of "becoming" — what is
  happening right now. The event bus captures *now*.

- **Urðr** *(OOR-thur)* — (V2) the past-state archive. *Why*:
  the Norn of the past; what has happened.

- **Skuld** *(SKULD)* — (V2) the future-projection system,
  if/when we ever build one. *Why*: the Norn of what
  should/will be. (V1 deliberately doesn't have this; we
  don't make claims about the future.)

### Tone / emotional intelligence

- **Seiðr** *(SAY-thur)* — the deterministic verse-
  generation engine (sibling). *Why*: Seiðr is the magic of
  the Vanir, particularly associated with cycles, weaving,
  and song. The verse-generation engine *weaves* form +
  vocabulary into verse.

- **The mood channel** — the register-shaping layer (not a
  Norse term per se, but the *mechanism* by which Seiðr
  influences tone).

### Temporal / rhythm

- **The rhythm plane** — the time-aware ambient context
  system. *Why*: less Norse-specific because "rhythm" works
  well in English; Astrology Engine provides the data.

- **Skreyttingar** *(SKRAY-ting-ar; archaic)* — (V2) the
  cycles-and-decorations layer. *Why*: the Old Norse word
  for "ornaments" — what time-of-year gives to the moment.

### Trust / security

- **Kista** *(KEE-stuh)* — the encrypted credential vault
  (sibling). *Why*: literally "strong-chest"; the household
  word for where valuables are kept.

- **The gatekeeper pattern** — Kista mediating all
  cross-realm secret access. *Why*: in cosmology, Heimdall
  guards Bifrǫst's entrance; Kista is the parallel concept
  for credential gates.

### Embodiment

- **Hamr** *(HAH-mer)* — the parametric avatar engine
  (sibling). *Why*: Old Norse for "shape-skin" — the form
  worn by shape-shifters in saga literature. Hamr produces
  the *worn form* of Ember.

- **Auga** *(OW-guh)* — (planned) the GUI surface. *Why*:
  Old Norse for "eye." The visual surface through which
  the operator sees Ember.

- **Rödd** *(REUD)* — (planned) the voice surface. *Why*:
  Old Norse for "voice." Speech IO.

### Reasoning + meta

- **The audit layer** — logical-reasoning verification (not
  Norse-named; "audit" is the load-bearing term).

- **Wyrd** *(WURD)* — (V2 candidate name) the meta-learning
  pattern store. *Why*: Wyrd in Anglo-Saxon = fate, the
  weaving of what comes. The patterns the system learns
  *bend* what comes for the operator.

### Web / outward

- **CloakBrowser** — the stealth browser (sibling; English
  name, not changed). *Why*: it's already a known name on
  PyPI; we don't rename.

- **The walker** — operator-facing way to describe
  CloakBrowser ("the cloaked walker that goes beyond"). For
  prose / chat surfaces.

### Cosmology of integration itself

- **Yggdrasil** — the integration tree (this design tree's
  name). *Why*: the world-tree connecting realms.

- **Asgard** — Ember herself (the agent at the tree's
  base). *Why*: the realm of the gods + sovereignty.

- **Midgard** — the operator's everyday-world surfaces
  (Stofa, CLI). *Why*: the human realm.

- **Helheim / Vanaheim / Alfheim / Niflheim /
  Muspelheim / Útgarðr / Jötunheim** — distributed across
  the siblings per [`30_THE_NINE_REALMS_ARCHITECTURE.md`](../architecture/30_THE_NINE_REALMS_ARCHITECTURE.md).

### Time / dreaming

- **The dreamstate** — the nightly consolidation batch.
  *Why*: not strictly Norse but evokes the right rhythm
  (REM-like consolidation). Could also be called
  **Náttvinna** ("night-work").

- **The Hugin-and-Munin flight** — the daily
  retrieval-and-return cycle. *Why*: each chat turn is a
  *flight*; each dreamstate is a *return*.

---

## Why we use these (instead of flat English names)

A contributor reading code with these names learns the
*architecture* by learning the *cosmology*. A new contributor
reading:

```python
from ember.yggdrasil import bifrost, mimir, muninn, huginn
```

…can guess: "bifrost composes; mimir / muninn / huginn are
the three composed memory backends; the metaphor matches
the structure."

A flat-named alternative:

```python
from ember.yggdrasil import composer, memory_a, memory_b, memory_c
```

…tells you nothing.

The cosmology is **load-bearing for code clarity**.

---

## What we don't do

- **Force operators to learn Norse.** All operator-facing
  surfaces use modern English (or the operator's locale).
  Norse vocabulary is for *architecture*, not *interface*.
- **Use exotic spellings.** "Bifrǫst" appears in code
  comments + docs; CLI strings use ASCII-friendly
  "bifrost". Operators don't type runes.
- **Get scholarly.** We're domestic-Norse register, not
  philological-Norse register. "Mímir" works; "the
  hypostatized abstraction-of-wisdom personified as a
  decapitated head" doesn't.

---

## Operator-facing pronunciation guide

Pronunciations live in the README's appendix (V3 to be
added) so operators saying these names aloud feel
confident. Most operators won't ever need to; some will
enjoy.

---

## Closing

Norse Naming of AI Capacities is **the Skald's
contribution to code architecture**. It makes the system
*self-describing*. Contributors learn the cosmology;
they then know the code without separate documentation.

Ember earns the right to be cosmologically named because
her architecture *fits* the cosmology — not as ornament,
but as load-bearing metaphor.

This is what makes Yggdrasil *feel* like one project
rather than eleven.

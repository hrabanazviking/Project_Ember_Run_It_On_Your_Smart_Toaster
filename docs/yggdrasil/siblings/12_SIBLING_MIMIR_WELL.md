# 12 — Sibling: Mímir's Well

> *"Wisdom rises from the well at the root of the world-tree."*

A persistent self-healing AI memory database with Ebbinghaus
forgetting curves, FTS5 search, contradiction detection, and
knowledge promotion.

---

## What it is

A standalone Python library + SQLite-based memory store. The
operator-facing capabilities (per its own README):

- **Ebbinghaus Decay** — memories fade over time unless
  reinforced, just like human memory.
- **FTS5 full-text search** — structured keyword retrieval.
- **Contradiction detection** — when a new memory contradicts
  an old one, the system surfaces the conflict.
- **Knowledge promotion** — memories that get accessed often
  get strengthened.
- **Self-healing** — schema migrations + repair on corruption.
- **WAL mode** — concurrent safety.

Mímir's Well stands at the root of Yggdrasil in the
cosmology; the operator drinks from it for wisdom (per the
Vǫluspá: Odin pledged an eye to drink from this well).

---

## Why this sibling matters for Yggdrasil

It's the **structured + decay-aware backend** for Bifrǫst.
While SQLite-vec gives Ember a flat key-value store, Mímir
gives Ember a *memory model that matches how humans actually
remember*.

The Ebbinghaus decay is the critical feature:

- A document the operator ingests once and never returns to:
  fades to background relevance.
- A document the operator queries weekly: stays sharp.
- The Well doesn't grow infinite-stale; it grows *toward what
  matters to the operator*.

This is a real philosophical shift from "everything I ever saw
is equally retrievable" → "what I've cared about lately is
most reachable, but nothing's lost."

---

## How Yggdrasil integrates Mímir's Well

### Integration role

Mímir is the **Mímir sub-backend within Bifrǫst** (see
[`11_SIBLING_BIFROST.md`](11_SIBLING_BIFROST.md)). Operators
who use Bifrǫst get Mímir automatically.

Mímir can ALSO be used **standalone as its own Brunnr
backend** (without Bifrǫst), for operators who want only
decay-aware memory without the multi-backend composition:

```yaml
brunnr:
  backend: mimir
  mimir:
    path: ~/.ember/well/mimir.db
    decay_enabled: true
    half_life_days: 14    # how fast unaccessed memories fade
```

This is a `MimirBrunnr` adapter in
`src/ember/well/brunnr/mimir/adapter.py`, implementing the
existing `BrunnrHandle` Protocol.

### Why standalone matters

Some operators want simplicity. Bifrǫst adds Qdrant +
Hebbian complexity. Mímir alone gives them most of the value
(decay + FTS5) without the cost.

This is the same plug-in-pattern as sqlite_vec vs pgvector:
the operator picks based on their needs.

### Integration with Verdandi (Phase 3)

Verdandi (the self-awareness event bus) can subscribe to
Mímir's events:

- `memory_decayed` (a chunk's relevance dropped below
  threshold)
- `memory_reinforced` (operator query touched a chunk)
- `contradiction_detected` (new ingest conflicts with
  existing knowledge)

Ember's self-awareness layer ([`../ai-capabilities/40_SELF_AWARENESS_LAYER.md`](../ai-capabilities/40_SELF_AWARENESS_LAYER.md))
uses these to know things like "I've been asked about Odin a
lot lately — those documents are getting reinforced."

### Configuration knobs

```yaml
brunnr:
  backend: mimir
  mimir:
    path: ~/.ember/well/mimir.db
    decay:
      enabled: true
      half_life_days: 14
      reinforce_on_query: true
      reinforce_factor: 1.5
    contradiction_detection:
      enabled: true
      similarity_threshold: 0.85
    knowledge_promotion:
      enabled: true
      access_count_threshold: 5
```

Operators can opt out of any feature.

---

## Risk / known issues

- **SQLite WAL on network FS.** Same risk as sqlite-vec
  (per `docs/CROSS_PLATFORM_PLAN.md`). Operators on NFS
  should disable WAL.
- **Decay can surprise operators.** "Why isn't this document
  showing up?" — answer: it decayed. The
  [`../ai-capabilities/40_SELF_AWARENESS_LAYER.md`](../ai-capabilities/40_SELF_AWARENESS_LAYER.md)
  surfaces decay events so the operator can re-reinforce.
- **Contradiction detection is fuzzy.** Semantic similarity
  isn't logical contradiction. False positives possible.
  Tunable.

---

## Operator-facing implications

### "Where did my note go?"

If an operator notices a document seems less retrievable than
they expected:

1. Stofa's WellScreen sources panel shows ALL documents,
   regardless of decay (operators always see what's stored).
2. They can hit `r` to re-ingest = full reinforcement.
3. The doctor screen shows recent decay events.
4. Decay is *not* deletion — old chunks still exist, just
   rank lower.

### "Why is Ember bringing up old documents?"

Knowledge promotion (the inverse of decay): documents the
operator returns to multiple times get *promoted* — they rank
higher in subsequent queries. This produces a *useful drift*
toward the operator's actual interests, not a noisy drift
toward random.

---

## Test strategy

Phase 1 ships:

- **Unit tests** for `MimirBrunnr` adapter with mocked
  Mímir's Well.
- **Integration tests** with real Mímir on a temp directory
  — full lifecycle: ingest, decay simulation (advance system
  clock), reinforcement, contradiction detection.
- **Snapshot test** verifying decay curves match expected
  Ebbinghaus shape over simulated 30 days.

Tests in `tests/unit/test_brunnr_mimir_adapter.py` and
`tests/integration/test_brunnr_mimir_real.py`.

---

## Closing

Mímir gives Ember *humanlike memory*. Bifrǫst then composes
Mímir with vector + associative layers. The combination is
**a memory model that no current AI agent has** — and that's
exactly the kind of differentiation Yggdrasil exists to
deliver.

Drink from the well; the wisdom flows.

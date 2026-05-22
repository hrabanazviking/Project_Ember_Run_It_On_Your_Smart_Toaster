# 32 — Bifrǫst as Gateway

Detailed design of Bifrǫst Bridge's role as the memory-plane
gateway. The single most architecturally consequential
integration.

---

## Why "gateway"

Bifrǫst doesn't just *add* a memory backend. It *replaces the
backend-picker question* with a *backend-composition question*.

Before Yggdrasil:
- Operator picks one of: sqlite-vec, pgvector.
- Chat queries hit the one backend.
- Done.

After Yggdrasil:
- Operator picks one of: sqlite-vec, pgvector, **Bifrǫst**.
- If they pick Bifrǫst, they pick *which sub-backends*
  Bifrǫst composes.
- Chat queries hit the gateway, which fans out to sub-
  backends, fuses results, returns composed answer.

The gateway is the **architectural shift**. Memory becomes
*plural*.

---

## The composition diagram

```
                   ┌──────────────────────┐
                   │   ChatScreen (etc.)  │
                   │   calls               │
                   │   brunnr.hybrid_search│
                   └──────────┬───────────┘
                              │
                   ┌──────────▼───────────┐
                   │   BifrostBrunnr       │
                   │   (BrunnrHandle impl) │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │  Bifrost Bridge       │
                   │  Composer + Fusion    │
                   └──────────┬───────────┘
                              │
              ┌───────────────┼────────────────┬─────────┐
              │               │                │         │
          ┌───▼───┐       ┌───▼────┐       ┌───▼────┐  ┌─▼────────┐
          │ MÍMIR │       │ HUGINN │       │ MUNINN │  │MEMPALACE │
          │SQLite │       │Qdrant  │       │Hebbian │  │(optional)│
          │+FTS5  │       │vectors │       │ assoc. │  │verbatim  │
          │+decay │       │        │       │        │  │          │
          └───────┘       └────────┘       └────────┘  └──────────┘
```

`BifrostBrunnr` (the adapter) implements `BrunnrHandle` —
Ember's existing memory Protocol. So the chat loop *doesn't
change*. It calls `brunnr.hybrid_search(...)`; the adapter
calls Bifrǫst Bridge; the Bridge fans out + fuses.

---

## The fusion algorithm

Bifrǫst Bridge uses **Reciprocal Rank Fusion (RRF)** —
the same algorithm Ember's sqlite-vec adapter uses for
hybrid (vector + FTS) search. Generalizes to N backends:

```
score(chunk) = Σ over all backends B {
    (weight_B / (k + rank_B(chunk)))
}
```

- `k` is a constant (default 60, matching sqlite-vec's RRF).
- `rank_B(chunk)` is the chunk's rank in backend B's
  results (1-indexed; not present = ∞).
- `weight_B` is operator-tunable per backend.

Default weights:
- Mímir: 1.0
- Huginn: 1.0
- Muninn: 0.5 (associative is more speculative)
- MemPalace: 1.5 (verbatim recall is high-quality)

Operators tune weights for their needs.

---

## Why RRF (vs other fusion strategies)

RRF is the right choice for memory fusion because:

1. **Rank-based, not score-based.** Different backends have
   different score scales (BM25 vs cosine distance vs
   Hebbian weight). RRF normalizes via rank.
2. **Robust to outliers.** A backend that returns one weird
   high-score result can't dominate — fusion weighs rank
   position.
3. **Simple to implement + reason about.** Operators can
   understand "if Mímir ranks it 1st, that's worth 1/(60+1)
   = 0.016 in fusion."
4. **Already proven in Ember.** sqlite-vec uses RRF; we're
   generalizing, not inventing.

Alternative fusion strategies (linear combination of scores,
LambdaMart, learned-to-rank) are *more sophisticated* but
require training data Ember doesn't have. RRF is the right
default.

---

## When to consult which backend

Different query shapes prefer different backends:

| Query | Best backend |
|---|---|
| "What did I write about X exactly?" | MemPalace (verbatim) |
| "What's semantically near X?" | Huginn (vector) |
| "What documents contain word X?" | Mímir (FTS5) |
| "What documents usually appear with X?" | Muninn (associative) |

A naive operator query (just text) gets *all* backends
consulted; fusion picks the strongest. A sophisticated
operator (or Ember, when she's smart enough) could *route*
the query to the most-likely backend, saving fan-out cost.

V1: always fan-out. V2+: smart routing as an optimization.

---

## How Bifrǫst handles partial availability

Suppose Qdrant goes down mid-session. Huginn becomes
unavailable.

Bifrǫst Bridge:
1. Catches the Huginn-side connection error.
2. Logs a warning via Verdandi.
3. Continues with the remaining backends.
4. Fuses results from available backends.
5. Marks the response with a metadata flag indicating
   degraded mode.

The `BifrostBrunnr` adapter surfaces this to Ember:

```python
result = bifrost.hybrid_search(...)
if result.degraded:
    # one or more sub-backends were unavailable
    log_to_operator(f"degraded retrieval: {result.unavailable_backends}")
```

Ember's chat reply can note: *"I searched my semantic and
keyword memory, but my associative memory is currently
offline."* (Operator-configurable; off by default for
non-power-users.)

Stofa's StatusBar shows backend-state dots in degraded mode.

---

## Performance characteristics

Per-backend cost (on Pi-class):

| Backend | Query time | Memory overhead |
|---|---|---|
| Mímir (SQLite + FTS5) | ~5-20 ms | ~30 MB |
| Huginn (Qdrant, local) | ~10-30 ms | ~150 MB Qdrant server |
| Muninn (Hebbian in-process) | ~5 ms | ~20 MB |
| MemPalace | ~10-40 ms | varies |

Fan-out parallelism (Phase 1: serial; Phase 2: parallel via
asyncio): a 4-backend serial fan-out is ~40-100ms; a
parallel fan-out is ~30-40ms (limited by the slowest backend).

**Target:** sub-100ms hybrid_search on a 10K-chunk Well on
Pi 5. Achievable.

---

## What Bifrǫst does NOT do

- **Cross-backend transactions.** Writes go to all backends
  but aren't transactional across them. If Huginn write
  fails after Mímir succeeded, we have inconsistency. The
  reconciliation layer ([`39_THE_RECONCILIATION_LAYER.md`](39_THE_RECONCILIATION_LAYER.md))
  handles this.
- **Schema migration across backends.** Each backend is
  responsible for its own schema. Bifrǫst doesn't migrate
  Mímir → Huginn or vice versa.
- **Embedding generation.** Ember's existing
  `OllamaEmbedClient` (slice-1 module) still generates
  embeddings. Bifrǫst routes the vector to Huginn; it
  doesn't compute it.

---

## Operator-facing knobs

```yaml
brunnr:
  backend: bifrost
  bifrost:
    fusion:
      strategy: rrf
      k: 60
      mimir_weight: 1.0
      huginn_weight: 1.0
      muninn_weight: 0.5
      mempalace_weight: 1.5
    routing:
      enabled: false              # V1: always fan-out
      verbatim_keywords:           # for V2: route to MemPalace
        - exactly
        - verbatim
        - "the exact text"
    degraded:
      surface_to_operator: false   # off by default
      log_via_verdandi: true       # observability always on
```

Sensible defaults; operators can deeply tune.

---

## Why Bifrǫst makes Ember meaningfully smarter

A single chat-turn query benefits from *complementary*
backends:

- **Operator asks about Odin.**
- **Mímir** returns 5 documents containing "Odin" as a
  keyword.
- **Huginn** returns 8 chunks semantically near "Odin" (some
  about Wotan, the German cognate; some about Yggdrasil; some
  about Norse mythology generally).
- **Muninn** returns 3 documents the operator has *associated*
  with Odin queries in the past (Hávamál, the Sayings of the
  High One; the operator returns to this when asking about
  Odin).
- **MemPalace** (if enabled) returns 2 verbatim passages
  where the operator wrote about Odin.

Fusion produces 12-15 unique chunks, ranked by composite
relevance. The result is *much richer* than any single
backend would produce — and the operator never has to think
about which backend they're querying.

---

## Closing

Bifrǫst as gateway is the **single highest-leverage
integration in Yggdrasil**. It changes memory from "one
storage system" to "an ensemble." The operator's chat turns
benefit *immediately*. The architecture stays clean: same
Brunnr Protocol, new adapter, deeper capability.

This is what "composable architecture" pays out.

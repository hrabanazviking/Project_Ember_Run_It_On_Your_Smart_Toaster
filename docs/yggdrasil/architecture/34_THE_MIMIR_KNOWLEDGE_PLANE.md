# 34 — The Mímir Knowledge Plane

How Yggdrasil's memory subsystem composes. The *plane* —
because it spans multiple backends — gives Ember a much
richer memory model than any single backend could.

---

## The memory plane's three operations

Every interaction Ember has with memory falls into one of
three categories:

1. **Store** — new chunks land in the Well (via ingest or
   Episode persistence).
2. **Recall** — chat turns retrieve relevant chunks.
3. **Maintain** — background operations (decay, promotion,
   contradiction-detection, reinforcement) keep the Well
   healthy.

The Mímir Knowledge Plane defines how each operation routes
across the available backends.

---

## Store: fan-out to all backends

When `BrunnrHandle.add_document` or `add_chunks` is called:

```
┌──────────────┐
│ caller       │
│ add_chunks([▣▣▣]) │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Bifrost      │
│ adapter      │
└──────┬───────┘
       │
       ▼ (fan-out)
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Mímir        │  │ Huginn       │  │ Muninn       │  │ MemPalace    │
│ (decay-aware │  │ (vector)     │  │ (associative)│  │ (verbatim;   │
│  SQLite)     │  │              │  │              │  │  if enabled) │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

Each backend stores in its native format:
- Mímir: row in SQLite + FTS5 index + initial decay weight = 1.0
- Huginn: vector + payload in Qdrant
- Muninn: nodes in Hebbian graph; initial associations from
  co-occurrence with sibling chunks in the same document
- MemPalace: verbatim text + its own indexing

Failure semantics: if one backend's write fails, the others
still succeed. Bifrǫst marks the operation as `partial` and
emits a Verdandi event. The reconciliation layer
([`39_THE_RECONCILIATION_LAYER.md`](39_THE_RECONCILIATION_LAYER.md))
schedules a retry.

---

## Recall: fan-out + RRF fusion

Per [`32_THE_BIFROST_AS_GATEWAY.md`](32_THE_BIFROST_AS_GATEWAY.md).
A query goes to all backends in parallel; results come back
ranked; RRF fuses; top-k returned.

Cost amortization: chunks that appear in multiple backends'
top results get boosted (RRF sums contributions). This is
*exactly* the "consensus across memory systems" we want —
the chunk that's keyword-matched AND semantically near AND
associatively-relevant is almost certainly *the* right answer.

---

## Maintain: per-backend background work

Each backend has its own maintenance loop:

### Mímir
- **Decay**: every N hours (configurable; default 6),
  decrement all chunk relevances by an Ebbinghaus curve.
- **Promotion**: when a chunk is accessed K times in a
  rolling window (default K=5, window=7 days), boost its
  weight.
- **Contradiction**: when new chunks are stored, check
  semantic similarity against existing ones; flag
  conflicts (similarity ≥ 0.85 + opposite truth values
  detected via keyword heuristics).

### Huginn
- **Index optimization**: Qdrant's HNSW index needs
  occasional optimization; cron-style.
- **Drift detection** (V2): when chat queries consistently
  return distant vectors, suggests the corpus has drifted
  from the operator's interests.

### Muninn
- **Hebbian update**: every access pattern strengthens
  associations; weights normalize periodically.
- **Pruning**: weak associations get dropped to keep the
  graph tractable.

### MemPalace
- **Per its own maintenance regime.** Operator's
  responsibility to schedule.

These run **outside chat-turn latency** — async background
tasks via Yggdrasil's runner.

---

## How Verdandi observes memory operations

Every memory operation publishes events:

- `mimir.chunk_stored` (chunk_id, source)
- `mimir.decay_applied` (count, time_elapsed)
- `mimir.promotion_triggered` (chunk_id, access_count)
- `mimir.contradiction_detected` (chunk_id_old, chunk_id_new, similarity)
- `huginn.vector_indexed` (chunk_id)
- `huginn.recall_returned` (count, elapsed_ms)
- `muninn.association_strengthened` (chunk_id_a, chunk_id_b, new_weight)
- `bifrost.fusion_completed` (total_results, backend_counts)

Stofa's DoctorScreen reads these for the Doctor view.
Ember's awareness layer reads these for "I notice…" surfacing.

---

## Operator-facing knowledge plane behaviors

### "Ember knew that document was relevant before I did"

Operator hasn't asked about Odin in 2 weeks. They ask a
related question (Norse mythology). The fusion algorithm
ranks the Odin documents high — *because* Muninn remembered
they're associated. Ember surfaces them without operator
having to know the connection was made.

### "Ember knows when her knowledge contradicts itself"

Operator ingests a document saying "Odin has one eye."
Later, operator ingests "Odin sacrificed his eye at Mímir's
Well."

Mímir's contradiction detection notices the second contains
"sacrificed eye" + the first contains "one eye" — semantic
overlap, factual reconciliation. Mímir emits a Verdandi
event. Ember can surface: *"I notice these two passages
might be saying different things about Odin's eye — would
you like me to reconcile?"*

(This requires the contradiction-detection feature to be
implemented in mimir-well; verify on integration.)

### "Old documents fade, but never disappear"

Operator ingests 5,000 documents about a topic they study
intensively for a month, then move on. Six months later,
those documents have decayed to background relevance — not
deleted, just lower-ranked. When the operator returns to
the topic, their first query reinforces; the documents
spring back to prominence.

Memory that *tracks operator interest over time*, not just
storage time.

---

## Configuration shape (full)

```yaml
brunnr:
  backend: bifrost
  embedding_dim: 768
  bifrost:
    mimir:
      enabled: true
      path: ~/.ember/well/mimir.db
      decay:
        enabled: true
        half_life_days: 14
        background_interval_hours: 6
      promotion:
        enabled: true
        access_threshold: 5
        window_days: 7
      contradiction:
        enabled: true
        similarity_threshold: 0.85
    huginn:
      enabled: true
      qdrant_url: http://localhost:6333
      collection: ember-well
      vector_dim: 768
      hnsw_params: default
    muninn:
      enabled: true
      hebbian_path: ~/.ember/well/muninn.db
      learning_rate: 0.05
      pruning_threshold: 0.01
    mempalace:
      enabled: false              # opt-in for verbatim
      storage_path: ~/.ember/well/mempalace/
    fusion:
      strategy: rrf
      k: 60
      weights:
        mimir: 1.0
        huginn: 1.0
        muninn: 0.5
        mempalace: 1.5
    degraded:
      surface_to_operator: false
      log_via_verdandi: true
```

Operators tune any axis. Defaults are sensible for Pi-class.

---

## Performance characteristics

| Operation | Pi 5 target | Desktop target |
|---|---|---|
| Single-chunk store fan-out (4 backends, serial) | < 100ms | < 30ms |
| Hybrid_search (10K-chunk corpus, fan-out + fusion) | < 100ms | < 30ms |
| Background decay sweep (10K chunks) | < 5s | < 1s |
| Background contradiction-check (10K chunks) | < 30s | < 5s |

Performance gets tested as Yggdrasil Phase 1 ships.

---

## What the operator never has to think about

- Which backend has what chunk.
- Whether their query benefits from Mímir vs Huginn vs Muninn.
- When decay last ran.
- When promotion last triggered.
- How RRF works.

They write `ember.yaml` once, ingest their corpus, chat.
The plane does its work.

---

## What Ember CAN choose to surface

When the awareness layer is on:

- "I notice these documents are getting reinforced — should
  I pin them?" (after a pattern of reinforcement)
- "I notice this contradicts an older note — want me to
  reconcile?" (contradiction event)
- "Some of your older notes are fading from active memory.
  Recent topics seem to be…" (decay summary, monthly)

All opt-in via `yggdrasil.awareness.surface_to_chat: true`.

---

## Closing

The Mímir Knowledge Plane gives Ember **memory like an
attentive scholar** — not just "everything I was ever told,"
but "what's mattered to my operator lately, anchored in what
they originally said, indexed semantically, associated by
their reading patterns, and verbatim-recoverable when needed."

This is the most architecturally consequential capability
in Yggdrasil. Get this right, and everything else builds on
solid ground.

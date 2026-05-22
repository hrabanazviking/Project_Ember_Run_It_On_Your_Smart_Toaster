# 11 — Sibling: Bifrǫst Bridge

> *"The Bifrǫst burns with flame, yet the gods ride it daily
> between Asgard and Midgard."*

The composite memory provider. Unifies three memory backends
behind a single agent-facing interface.

---

## What it is (from its own README)

**Bifrǫst Bridge** is a Python library that composes:

| Backend | Implementation | Purpose |
|---|---|---|
| **Mímir** | SQLite + FTS5 | Structured storage + keyword search |
| **Huginn** | Qdrant vectors | Semantic similarity search |
| **Muninn** | Hebbian learning | Associative reinforcement |

A single `BifrostMemory` object exposes high-level operations
(store, recall, associate, decay) and routes them to the
appropriate backend(s) under the hood.

The bridge metaphor is literal: Bifrǫst stands *between*
the realms (Asgard and Midgard in cosmology; the agent and
the memory layer in code).

---

## Why this sibling matters for Yggdrasil

It's the **memory plane's gateway**. Without it, Ember can
talk to one Brunnr (SQLite-vec or pgvector). With it, Ember
can talk to multiple memory systems simultaneously:

- Mímir for structured + decay-curve
- Huginn for vector similarity
- Muninn for "what tends to come up with what"

A single chat-turn retrieval can pull from all three and
weighted-fuse the results — the way human recall works (you
remember the exact name AND a semantic neighbor AND something
you associate with it).

This is **the biggest single capability multiplier** in the
Yggdrasil plan.

---

## How Yggdrasil integrates Bifrǫst

### Integration role

**Bifrǫst becomes a new Brunnr backend**, in addition to the
existing sqlite_vec and pgvector adapters.

```python
# Existing today
config.brunnr.backend = BrunnrBackend.SQLITE_VEC
config.brunnr.backend = BrunnrBackend.PGVECTOR

# New with Yggdrasil Phase 1
config.brunnr.backend = BrunnrBackend.BIFROST
config.brunnr.bifrost = BifrostConfig(
    mimir_path="...",
    huginn_url="...",   # Qdrant endpoint
    muninn_path="...",
)
```

The `BifrostBrunnr` adapter (lives in
`src/ember/well/brunnr/bifrost/adapter.py`) implements the
existing `BrunnrHandle` Protocol. Same `add_document`,
`add_chunks`, `search`, `hybrid_search`, etc. — but routed
through Bifrǫst's three-realm fusion.

### Why this fits the existing architecture

The Brunnr Protocol was designed pluggable (per ADR-0010 +
Vow of Pluggable Storage). Bifrǫst is the next plug-in.
**Zero code changes to Ember's chat / search / ingest
paths.** Operator picks the backend in `ember.yaml`; the
chat-turn behavior changes accordingly.

This is the cleanest possible integration: the existing
adapter slot becomes more powerful via a new tenant.

### Adapter responsibilities

The `BifrostBrunnr` adapter:

1. **On `open()`** — initialize Bifrǫst Bridge with the
   three sub-backends configured. Each sub-backend can
   independently report `Disconnected` if its store is
   unreachable; the Bridge tolerates partial-availability
   (operates with the available backends).
2. **On `add_document` / `add_chunks`** — forward to Bifrǫst's
   store API, which writes to all available sub-backends.
3. **On `search` / `vector_search` / `text_search`** — call
   Bifrǫst's appropriate retrieval API; receive composed
   results (already weighted across backends).
4. **On `hybrid_search`** — Bifrǫst's *native* operation;
   forward directly.
5. **On `close()`** — close each sub-backend; log warnings on
   close-failure (matching the sqlite_vec / pgvector close()
   pattern from Batch D).

### Configuration shape

```yaml
brunnr:
  backend: bifrost
  bifrost:
    mimir:
      path: ~/.ember/well/mimir.db
      decay_enabled: true     # Ebbinghaus on/off
    huginn:
      qdrant_url: http://localhost:6333
      collection: ember-well
      embedding_dim: 768
    muninn:
      hebbian_path: ~/.ember/well/muninn.db
      learning_rate: 0.05
    fusion:
      strategy: rrf           # reciprocal rank fusion (matches sqlite_vec's pattern)
      k: 60                   # RRF constant
      mimir_weight: 1.0
      huginn_weight: 1.0
      muninn_weight: 0.5      # associative gets less weight by default
```

Each sub-backend can be turned off independently:

```yaml
brunnr:
  backend: bifrost
  bifrost:
    huginn:
      enabled: false          # only Mímir + Muninn
```

This is the Vow of Modular Authorship — operators pick which
realms of memory matter for them.

---

## Risk / known issues

- **Bifrǫst's own version stability.** The library is new.
  Yggdrasil pins to a known-good range; we don't auto-upgrade.
- **Qdrant adds a process dependency.** Operators who don't
  want to run a Qdrant server can disable the Huginn sub-
  backend (Mímir + Muninn still work).
- **Hebbian learning's privacy implications.** Muninn learns
  patterns in the operator's query behavior. This stays local
  (per Vow of Sovereignty); no federation in V1.

---

## Open questions for Phase 1 ratification

1. **Does Bifrǫst already expose an MCP server interface?** If
   so, we could integrate via MCP rather than direct library
   import — more loosely coupled.
2. **Bifrǫst's update cadence.** Is it stable enough to pin
   for a 6-month support window?
3. **Qdrant default port + local-only setup.** Ship with a
   default `docker compose` to make adoption frictionless?

These are deferred to ADR-0016 drafting.

---

## Test strategy

Phase 1 ships:

- **Unit tests** for `BifrostBrunnr` adapter with mocked
  Bifrǫst Bridge — verify the Protocol implementation is
  correct.
- **Integration test** with a real Bifrǫst Bridge + a
  Qdrant-via-podman container — full ingest + search
  roundtrip.
- **Performance baseline** — sub-50ms hybrid_search on a
  10K-chunk Well (Pi-class) is the target.

Tests live in:

- `tests/unit/test_brunnr_bifrost_adapter.py`
- `tests/integration/test_brunnr_bifrost_real.py` (marked
  `requires_qdrant + requires_bifrost`)

---

## Closing

Bifrǫst is the *single highest-impact integration* in Yggdrasil
Phase 1. Memory composition is what separates an LLM-with-
search from a *real AI companion who remembers*. The bridge
makes that real.

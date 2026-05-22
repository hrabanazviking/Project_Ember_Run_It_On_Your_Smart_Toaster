# 19 — Sibling: MemPalace

> *"Local-first AI memory. Verbatim storage, pluggable backend,
> 96.6% R@5 raw on LongMemEval — zero API calls."*

A standalone AI memory system. Already PyPI-published. Local-
first.

---

## What it is

An independent open-source AI memory library. From its README:

- **Verbatim storage** — preserves exact text, not just
  embeddings.
- **Pluggable backend** — operator picks the storage layer.
- **96.6% R@5 on LongMemEval** — a strong benchmark score.
- **Zero API calls** — fully local.
- Published on PyPI as `mempalace`.

The name evokes the *method of loci* (memory palace) — the
classical mnemonic technique of imagining a familiar space
and placing memories at locations within it.

---

## Why this sibling matters for Yggdrasil

It's a **first-class alternative to mimir-well**.

Mímir + Bifrǫst gives composable, decay-aware memory.
MemPalace gives **verbatim, high-recall, single-system
memory**.

These are *different philosophies of memory*:

| Aspect | Mímir + Bifrǫst | MemPalace |
|---|---|---|
| Approach | composable multi-backend | single integrated system |
| Decay | yes (Ebbinghaus) | no (verbatim retained) |
| Recall benchmark | not measured | 96.6% R@5 LongMemEval |
| Best for | "human-like memory rhythm" | "I need to find what I said exactly" |

Yggdrasil supports **both**, and an operator can pick OR
compose them via Bifrǫst.

---

## How Yggdrasil integrates MemPalace

### Integration role

MemPalace becomes a Brunnr backend alternative:

```yaml
brunnr:
  backend: mempalace
  mempalace:
    storage_path: ~/.ember/well/mempalace/
    # other mempalace-specific config
```

A `MemPalaceBrunnr` adapter in
`src/ember/well/brunnr/mempalace/adapter.py` implements the
existing `BrunnrHandle` Protocol.

### Composed mode

MemPalace can ALSO be a sub-backend within Bifrǫst (like
Mímir + Huginn + Muninn). In this mode:

```yaml
brunnr:
  backend: bifrost
  bifrost:
    mempalace:                   # new sub-backend
      enabled: true
      storage_path: ~/.ember/well/mempalace/
    mimir:                       # also enabled
      enabled: true
    fusion:
      mempalace_weight: 2.0      # prefer verbatim recall
      mimir_weight: 1.0
```

Operators who want "best of both" can run both — Mímir for
decay-aware semantic search, MemPalace for verbatim "what did
they actually say" recall.

### Why pluggable matters

The Brunnr Protocol's strength is that this is **zero new
abstraction**. Adding MemPalace = writing one adapter file +
adding to the `BrunnrBackend` enum. The chat / search /
ingest paths don't change.

The Vow of Pluggable Storage continues to pay dividends.

---

## When MemPalace is the right choice

- Operators who want strict verbatim recall (every word
  preserved).
- Use cases where decay isn't wanted (legal documents,
  reference material, compliance corpora).
- Benchmark-quality recall (96.6% R@5 is strong).

When Mímir + Bifrǫst is the right choice:
- Operators who want decay (notes, chat history).
- Use cases where "what they cared about" should dominate
  "what they once saw."
- Multi-backend composition needs.

When BOTH (via Bifrǫst):
- Operators who want both behaviors and are willing to pay
  the resource cost of running two memory systems.

---

## Risk / known issues

- **License verification needed.** MemPalace's README doesn't
  prominently display license in the snippet we surveyed.
  ADR-0016 will verify before integration commits.
- **Two memory systems = two backup concerns.** Operators
  running both need to back up both. The Norns backup system
  (per [`../robustness/54_THE_NORNS_BACKUP_SYSTEM.md`](../robustness/54_THE_NORNS_BACKUP_SYSTEM.md))
  handles this.
- **Resource cost when composed.** Running Mímir + Huginn +
  Muninn + MemPalace in parallel is significant. Recommended
  only for desktop-class operators, not Pi.

---

## Open questions for Phase 2 ratification

1. **License compatibility with MIT.** Verify and document.
2. **Schema compatibility.** Can the same Document/Chunk
   model from `ember.schemas` work natively, or does
   MemPalace want different shapes? Adapter mediates either
   way; just affects efficiency.
3. **Migration path.** Operators with existing sqlite_vec
   Wells who want to switch — what's the export/import
   workflow?

---

## Test strategy

Phase 2 ships:

- **Unit tests** for `MemPalaceBrunnr` adapter.
- **Integration tests** with real MemPalace.
- **Benchmark validation** — verify our adapter's R@5 on
  LongMemEval ≥ 96% (so the integration doesn't lose
  MemPalace's quality).

Tests in `tests/unit/test_brunnr_mempalace_adapter.py` and
`tests/integration/test_brunnr_mempalace_real.py`.

---

## Operator-facing example

Operator with a research corpus + chat history:

```yaml
# ember.yaml
brunnr:
  backend: bifrost
  bifrost:
    mempalace:
      enabled: true              # verbatim research corpus
      storage_path: ~/.ember/well/research/
    mimir:
      enabled: true              # decay-aware chat history
      path: ~/.ember/well/chat-memory.db
```

Two Wells, one operator-facing interface. Research corpus
stays exact (citations are word-perfect). Chat history fades
naturally (what they care about strengthens; what they
ignored fades).

---

## Closing

MemPalace and Mímir are *not competitors*. They're *two
correct answers to different memory questions*. Yggdrasil
honors both by making them both available, and letting
Bifrǫst compose them when operators want.

That's pluggable storage at its mature best.

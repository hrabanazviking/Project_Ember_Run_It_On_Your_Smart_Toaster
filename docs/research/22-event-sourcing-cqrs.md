# 22 — Event Sourcing and CQRS for Stateful AI Systems

**Category:** Event-Driven & Concurrency
**Runa relevance:** Muninn (memory as derived projection), Skuld (task ledger as event log), audit (replay), Eir (state recovery)
**Status:** Research synthesis. Adjacent paradigm with high relevance to Runa's persistence story.
**Last touched:** 2026-05-17

---

## 1. Core idea

In conventional persistence, the *current state* of the system is the source of truth. You update a row; the previous values are gone unless you happened to log them. **Event sourcing** inverts this: the *sequence of events* that happened is the source of truth. Current state is a *projection* — a fold over the event log. You never overwrite; you append. Anything you want to know is computable from the log.

**CQRS (Command Query Responsibility Segregation)** is a pattern often paired with event sourcing: split the write side (commands that produce events) from the read side (projections optimised for queries). The same event log can feed many different read models, each shaped for a specific query pattern.

For Runa, this matters because her memory, her tasks, and her audit trail are all naturally event-shaped. Every Muninn write is an event ("episode E happened at T"). Every Skuld transition is an event ("task X moved to state Y"). Every emotional shift is an event ("Eldhugi delta D at T"). Treating these as events first and as projected state second gives Runa: lossless audit, time-travel debugging, replay-based recovery, multiple read models without write contention, and a clean story for the `runa state snapshot/restore` operator commands.

## 2. Technical depth

**Vocabulary:**

- **Event** — an immutable fact that happened, with a timestamp. Past tense: `EpisodeRecorded`, `TaskCompleted`, `EmotionalDelta`. Events are *what is true*; they don't fail (they already happened).
- **Command** — a request for the system to do something. Imperative: `RecordEpisode`, `CompleteTask`. Commands can fail (validation, conflict, permission).
- **Event store** — append-only log. Optimised for sequential writes and replay.
- **Aggregate** — a consistency boundary. A command targets one aggregate; the aggregate validates and emits 0+ events. (DDD origin.)
- **Projection / read model** — a derived view computed by folding events through a reducer. May be cached on disk for fast queries.

**Two coupled patterns:**

```
            COMMAND SIDE                          QUERY SIDE
   ┌─────────────────────────┐         ┌─────────────────────────┐
   │ Command arrives          │         │ Query arrives           │
   │   ↓                      │         │   ↓                     │
   │ Load aggregate state     │         │ Read from projection    │
   │ (replay or cached snap)  │         │ (read-optimised store)  │
   │   ↓                      │         │   ↓                     │
   │ Validate command         │         │ Return result           │
   │   ↓                      │         └─────────────────────────┘
   │ Emit events (if valid)   │
   │   ↓                      │         Projections updated by:
   │ Append to event store ───┼──────► │ subscribe to event store
   │                          │         │ apply each event to view│
   └──────────────────────────┘         └─────────────────────────┘
```

The event store is the canonical truth. Projections are derived; if they get corrupted, rebuild by replaying the log.

**Snapshots.** Replaying millions of events to load aggregate state is slow. Snapshots periodically capture aggregate state at a known sequence number; replay starts from the snapshot. Standard event-sourcing optimisation.

**Idempotency.** Event handlers must be idempotent — applying the same event twice yields the same state. Critical because projections may need replay, and distributed delivery may double-deliver.

**Event versioning / migration.** Schemas evolve. An event written in 2024 must still be replayable in 2026. Patterns: upcasting (transform old events to new shape on read), versioned event types (`EpisodeRecorded.v1`, `.v2`), weak schema (extensible fields).

**Tooling and platforms:**

- **EventStoreDB** — purpose-built event store.
- **Apache Kafka** — durable event log, often used as event store at scale.
- **PostgreSQL with append-only tables** — simple and surprisingly capable for moderate scale.
- **SQLite** — perfectly fine for single-host event-sourcing if write rate is modest. Runa's use case.
- **Marten** (.NET), **Axon** (JVM), **Eventide** (Ruby), **NEventStore** — framework-level libraries.

**Pure CQRS without event sourcing** is also a valid pattern: separate read and write models with shared mutable state in between. Event sourcing without CQRS is also valid (just an audit log of all changes). The two combine but are independent.

## 3. Key works

- **Young, G.** "CQRS Documents" — leanpub.com/cqrsdocs (originally a series of articles, ~2010-2012). The foundational modern CQRS writing.
- **Fowler, M.** "Event Sourcing." martinfowler.com/eaaDev/EventSourcing.html, 2005. Concise classic explanation.
- **Vernon, V. *Implementing Domain-Driven Design*.** Addison-Wesley, 2013. The book that paired DDD with event sourcing in practice.
- **Evans, E. *Domain-Driven Design.*** Addison-Wesley, 2003. The aggregate concept's origin.
- **Helland, P. "Immutability Changes Everything."** ACM Queue, 2015. Why event-sourced systems get easier as scale grows.
- **Stopford, B. *Designing Event-Driven Systems.*** O'Reilly, 2018. Modern engineering perspective.
- **EventStoreDB documentation** — eventstore.com/docs. Reference implementation.

## 4. Empirical results

- Event-sourced systems trade write-time efficiency for read-time flexibility and audit-time superpowers. Storage cost is higher (every event stored forever), query cost is shifted to projection-building, but operational debuggability is dramatically better.
- Production reports (financial systems, regulated industries, large e-commerce) consistently cite the *replay-from-any-point* capability as the most valuable property. Bug fixes can be retroactively applied by rebuilding affected projections.
- Common pitfalls (from many post-mortems):
  - **Schema evolution.** Treating events as forever-immutable while business requirements evolve requires real discipline.
  - **Aggregate boundaries wrong.** Aggregates too large = contention; too small = consistency holes. Fixing later is expensive.
  - **Eventual consistency in projections.** A write happens; the query side reflects it some milliseconds-to-seconds later. Surprises naïve consumers.
  - **Snapshot logic incorrect.** Subtle replay bugs hide in snapshot/replay-boundary handling.
- For agent-scale workloads (Runa: hundreds to thousands of events per day), modern hardware handles event sourcing on SQLite trivially.

## 5. Applicability to Runa

This is a high-fit pattern for several Runa subsystems:

For **Muninn**:

- Frame Muninn as an event-sourced store. **Events:** `EpisodeRecorded`, `EpisodeSummarised`, `EpisodeArchived`, `MemoryRetrieved`, `ImportanceUpdated`, `EmbeddingRecomputed`. Append to a per-day SQLite file under `~/.runa/memory/events/`.
- **Projections:** the current episode table, the vector index, importance-sorted ranking. Rebuildable from events.
- Schema migrations ([[02-episodic-memory-architectures]]) become: write a script that replays events through new projection logic; swap the projection atomically. The events don't need to change.

For **Skuld (task ledger)**:

- Already inherently event-shaped. **Events:** `TaskQueued`, `TaskStarted`, `TaskProgressUpdated`, `TaskCompleted`, `TaskFailed`, `TaskAbandoned`. Replay yields the current state of any task.
- DATA_FLOW §5.2 recovery path is exactly the event-sourcing replay-on-restart pattern.

For **audit log** (`core/logging/`):

- Audit log is by definition an event log. Every kernel decision, tool call, policy check is an event. `runa logs` is a query over this log.

For **`runa state snapshot` / `restore`**:

- A "snapshot" is the event-sourcing snapshot — a checkpoint of all projections at a sequence number, plus the events since that snapshot.
- A "restore" replays events from a snapshot through current projection logic.

For **Eldhugi**:

- The emotional journal is naturally append-only and event-shaped. Same pattern.

What to avoid:

- Don't event-source *everything*. Caches, in-memory working scratch, read-replica state — these don't need to be in the event log. Reserve event sourcing for things that need durability + audit + replay.
- Don't conflate the event store with a message bus. VERÐANDI is the in-process pub/sub bus (transient). Muninn / Skuld events are durably persisted. Different roles, may share schema definitions but not transport.
- Don't allow event mutation. Once written, an event is immutable. Corrections take the form of *compensating events* (`EpisodeCorrected`, `TaskReassigned`).
- Don't drift the projection definitions away from the events without a re-projection plan. A projection that depends on event fields that were dropped is broken.

## 6. Open questions

- **Aggregate boundaries for AI agents.** What is the natural "aggregate" in Muninn? Per-conversation? Per-day? Per-entity? Not yet clear; experimentation will tell.
- **Event compaction.** Storage cost grows linearly with events. For agents running for years, when do you compact (collapse historical events into snapshots and discard)? Compaction loses audit; non-compaction grows unbounded.
- **Cross-aggregate consistency.** When a single command should produce events in multiple aggregates (Muninn + Skuld + Eldhugi all touched by one turn), how to ensure atomicity? Sagas, two-phase commit, or accepting eventual consistency.
- **Time travel for the user.** "Runa, what did we discuss last Tuesday?" naturally maps to a temporal projection. Real-time-aware event-store query languages exist; underutilised.

## 7. References (curated)

- martinfowler.com/eaaDev/EventSourcing.html — Fowler's canonical write-up.
- leanpub.com/cqrsdocs — Greg Young's CQRS papers.
- eventstore.com/docs — EventStoreDB reference.
- Vernon, *Implementing Domain-Driven Design* (2013).
- Helland, *Immutability Changes Everything*, ACM Queue 2015.
- Stopford, *Designing Event-Driven Systems*, O'Reilly 2018.
- Companion docs: [[21-actor-model-supervision]] (Akka Persistence pairs actor + ES), [[40-audit-logging-replay]] (the audit-log specific concerns).

# WM201 — World State Persistence and Memory
## Mímir's Droplet

**University of Yggdrasil — Class of 2044**
**Bachelor of Science in AI World Modeling Systems Design**
**4 Credits** | Year Two, Semester One

**Instructor:** Dr. Hervör Alfarinsdóttir, Professor of Persistent World Architecture
**Office:** Mímir's Well 203 | **Hours:** Thursdays 13:00–15:00

---

## Course Description

A world model is useless if it forgets. This course covers persistence architectures for world state: event sourcing (every change is an immutable event), snapshot/replay systems, differential state storage, and the Mímir Protocol for query-efficient world state retrieval. Students learn how the AI OS memory stack connects to the world model's persistence layer, and how MuninnGates govern which world state memories are surfaced to the agent's working context. Labs involve implementing an event-sourced world state store with replay capability.

---

## Lecture 1: Why Worlds Must Remember — The Impermanence Problem

### The Fragility of State

A world model that exists only in RAM is a world model that dies with the process. Power loss, process restart, hardware failure — any of these can destroy the entire simulated world in an instant. This is not a theoretical concern; it is a practical reality that every production world model must confront.

The impermanence problem has three dimensions:

1. **Crash recovery:** When the simulation process crashes, how much state is lost? Minutes? Hours? The entire world?

2. **Process migration:** When the simulation moves from one machine to another (e.g., during a hardware upgrade or a cloud migration), how is the world state transferred?

3. **Historical querying:** When a researcher asks "What was the population of District 7 on Day 42?", the simulation must be able to answer — not just about the current state, but about any past state.

Each of these dimensions demands a different aspect of persistence. Crash recovery demands durability (the state survives process failure). Process migration demands portability (the state can be moved between machines). Historical querying demands temporality (the state retains its history).

### The Mímir Myth

In Norse mythology, Mímir is the guardian of the well of wisdom. Odin sacrificed his eye to drink from the well, gaining knowledge of all things past and future. Mímir's Well is the original persistence layer — a repository of accumulated wisdom that survives across sessions, across crashes, across the death and rebirth of worlds.

Our persistence architecture is named after Mímir's Well because it serves the same function: it is the place where the world's accumulated state resides, always available, always queryable, always surviving.

### Three Approaches to Persistence

There are three fundamental approaches to world state persistence:

**1. Periodic Checkpointing (Snapshot Persistence)**
Save the entire world state at regular intervals. Simple to implement, but lossy — everything between checkpoints is lost on crash.

**2. Event Sourcing (Log Persistence)**
Record every state change as an immutable event. The current state can be reconstructed by replaying all events from the beginning. No data is lost, but replay can be expensive for long simulations.

**3. Hybrid (Snapshot + Event Log)**
Combine periodic snapshots with an event log. To reconstruct a past state, start from the nearest snapshot before the target time and replay events forward. This is the approach used by most production systems — it balances durability, performance, and temporal queryability.

In this course, we will study all three approaches, but we will focus on the hybrid approach as our primary architecture. The Mímir Protocol, which you will implement in the labs, uses this hybrid design.

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 8: "The Well That Never Dries: Persistence in World Models." University of Yggdrasil Press.
- Kleppmann, M. (2017). *Designing Data-Intensive Applications*. O'Reilly. Chapters 5 (Replication) and 11 (Stream Processing).
- Betts, D. et al. (2013). "Event Sourcing Pattern." *Microsoft Azure Architecture Center*.

### Discussion Questions

1. Consider a world simulation with 100,000 entities. A full snapshot takes 5 seconds to write to disk. How often should snapshots be taken? What is the maximum data loss you can tolerate?

2. Event sourcing guarantees no data loss, but replay is expensive. If a simulation runs for a year (365 × 24 × 60 = 525,600 minutes) and generates 10 events per minute, how many events must be replayed to reconstruct the state at minute 525,000? How can this be optimized?

3. The hybrid approach uses snapshots as acceleration points for event replay. What are the trade-offs between snapshot frequency and storage cost? Between snapshot frequency and recovery time?

---

## Lecture 2: Event Sourcing — The Journal of All That Happens

### Events as Truth

In event sourcing, the event log is the single source of truth. The current world state is a *derived artifact* — a materialized view of the event log. This is a profound architectural choice with far-reaching consequences.

The event log has the following properties:

1. **Append-only:** Events are never modified or deleted. They are only appended. This makes the log immutable — a permanent record of everything that has happened.

2. **Ordered:** Events are ordered by their sequence number (or timestamp). This order is the order of causality — event A happened before event B, so event A's effects are applied before event B's.

3. **Complete:** Every state change is represented by an event. No state change happens outside the event log.

These properties give event sourcing several powerful capabilities:

- **Temporal query:** Any past state can be reconstructed by replaying events from the beginning (or from a snapshot) up to the target time.
- **Audit:** The event log is a complete audit trail. Every change is recorded with its cause, its effect, and its timestamp.
- **Debugging:** When a bug appears, the event log can be replayed to reproduce the exact sequence of events that led to the bug.
- **Branching:** The simulation can be forked at any point by creating a new event log from a past state. This enables "what if" scenarios.

### Event Schema

Each event in the Mímir Protocol has the following schema:

```python
@dataclass(frozen=True)
class WorldEvent:
    event_id: str          # Unique identifier (UUID)
    event_type: str        # "move", "build", "trade", "age", etc.
    timestamp: float        # Unix timestamp (milliseconds)
    tick: int              # Discrete simulation tick
    source_entity: str     # Entity that caused the event
    target_entity: str     # Entity affected by the event (or "")
    payload: Dict[str, Any]  # Event-specific data (frozen dict)
    sequence: int          # Monotonically increasing sequence number
    causality_hash: str    # Hash of the previous event (for integrity)
```

The `causality_hash` is particularly important — it links each event to the previous event in the log, forming a hash chain (similar to a blockchain) that ensures the log cannot be tampered with. If any event is modified or removed, all subsequent hashes will be invalid.

### Materializing State from Events

The current world state is derived from the event log by applying each event in sequence to an initial state:

```python
def materialize_state(events: List[WorldEvent], initial_state: WorldState) -> WorldState:
    """Reconstruct the current state by replaying all events."""
    state = initial_state
    for event in events:
        state = apply_event(state, event)
    return state
```

This is elegant but potentially expensive. If the event log contains millions of events, materializing the state from scratch can take minutes or hours. This is why the hybrid approach uses periodic snapshots: materializing from the nearest snapshot is much faster than replaying from the beginning.

### Lab 1: Building an Event Store

In this lab, you will implement a basic event store:

1. Define the WorldEvent schema.
2. Implement an append-only event log with sequence numbers and causality hashes.
3. Implement the materialize_state function that replays events from the beginning.
4. Test the integrity of the log by verifying causality hashes.

### Required Reading

- Vernon, V. (2013). "Event Sourcing." *DDD Community*, available at https://z.es/ddd-event-sourcing.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 8.

### Discussion Questions

1. The event log is append-only. But what if an event contains an error? For example, a bug in the simulation produces an event that moves a citizen to an impossible location. Should the event be "deleted" from the log? If not, how should the error be corrected?

2. Hash-chaining the event log ensures integrity — but it also prevents any modification, even legitimate corrections. Is this a feature or a limitation? Discuss the trade-offs.

3. Consider a simulation with 10,000 entities, each generating an average of 5 events per tick. How large will the event log be after 100,000 ticks? At what point does replay become impractical?

---

## Lecture 3: Snapshot/Replay Systems — Freezing the World in Amber

### The Economics of Snapshots

A snapshot is a complete copy of the world state at a specific point in time. It is the world frozen in amber — every entity, every relationship, every property, preserved exactly as it was.

But snapshots are expensive. A world with 100,000 entities, each with 50 properties, requires approximately:

    100,000 entities × 50 properties × 100 bytes/property = 500 MB per snapshot

If we snapshot every tick, and a tick happens every second, we generate 500 MB/s — 43 TB/day. This is clearly impractical for most systems.

The solution is **incremental snapshots** (also called **differential snapshots**). Instead of saving the entire world state, an incremental snapshot saves only the entities that changed since the last snapshot.

### Incremental Snapshots

An incremental snapshot records the *delta* — the difference between the current state and the previous snapshot. This is much more compact:

```python
@dataclass
class IncrementalSnapshot:
    """An incremental snapshot records only the changes since the last full snapshot."""
    snapshot_id: str
    base_snapshot_id: str      # The full snapshot this delta is relative to
    tick: int                  # The tick at which this snapshot was taken
    created_entities: List[Entity]    # Entities that didn't exist at the base snapshot
    modified_entities: Dict[str, Dict[str, Any]]  # entity_id -> changed properties
    deleted_entities: List[str]       # entity_ids of entities that were deleted
```

The size of an incremental snapshot is proportional to the number of changes, not the size of the entire world. In a typical simulation, only a small fraction of entities change between ticks, so incremental snapshots are orders of magnitude smaller than full snapshots.

### Snapshot Strategy

The Mímir Protocol uses a tiered snapshot strategy:

- **Full snapshots:** Taken every N ticks (configurable, default N=1000). A full snapshot contains the complete world state.
- **Incremental snapshots:** Taken every M ticks (M < N, default M=10). An incremental snapshot contains only the changes since the last full snapshot.
- **Event log:** Every tick produces events in the append-only log. This provides sub-tick granularity.

To reconstruct the state at tick T:

1. Find the most recent full snapshot at or before tick T.
2. Apply all incremental snapshots between the full snapshot and tick T.
3. Apply any events after the last incremental snapshot.

This three-tier system provides:

- **Fast recovery:** Restoring from a recent snapshot is O(snapshot_size), not O(total_events).
- **Temporal query:** Any past state can be reconstructed by starting from the appropriate snapshot and replaying forward.
- **Sub-tick granularity:** The event log provides exact causal ordering within a tick.

### Required Reading

- Kleppmann, M. (2017). *Designing Data-Intensive Applications*, Chapter 11: "Stream Processing." O'Reilly.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 8.

### Discussion Questions

1. Full snapshots are large but self-contained. Incremental snapshots are small but depend on a base snapshot. What is the optimal ratio of full to incremental snapshots? How does this change with the simulation's change rate?

2. Consider a simulation where 99% of entities are static (they never change) and 1% change every tick. How would you optimize snapshots for this scenario?

3. Snapshots are taken at specific ticks. What if you need to reconstruct the state at a sub-tick granularity (e.g., between two events within the same tick)? How would the event log support this?

---

## Lecture 4: Differential State Storage — What Changed Between the Rain

### The Art of the Delta

A world state is a large, complex data structure. Between ticks, most of it doesn't change. The 47,283rd citizen's name doesn't change. The northern district's building layout doesn't change. The weather system's cloud positions change, but they're updated incrementally, not rewritten from scratch.

Differential state storage is the art of storing *what changed* rather than *everything that exists*. It is the difference between:

- "Here is the entire world" (full snapshot)
- "Here is what changed since last time" (differential)

The mathematics of differential storage is simple. If the world state has N properties, and K of them change between two snapshots, the differential is O(K) rather than O(N). When K << N (which is almost always the case), differential storage is vastly more efficient.

### Delta Encoding

The Mímir Protocol uses a structured delta encoding:

```python
@dataclass
class StateDelta:
    """A differential between two world states."""
    tick_start: int           # The tick this delta starts from
    tick_end: int             # The tick this delta ends at
    property_changes: Dict[str, Any]  # "entity_id.property" -> new_value
    entity_creations: List[Entity]     # Entities that were created
    entity_deletions: List[str]        # Entities that were deleted
    relationship_additions: List[Tuple[str, str, str]]   # (subject, predicate, object)
    relationship_removals: List[Tuple[str, str, str]]    # (subject, predicate, object)
```

This delta can be serialized to a compact binary format (MessagePack, Protocol Buffers, or CBOR) and stored efficiently.

### Delta Compression

Deltas can be further compressed using structural sharing. If a citizen moves from building A to building B, the delta records only the change in location — it doesn't copy the entire citizen. And if the citizen's location is the only property that changed, the delta is tiny: `{ "citizen_42.location": "building_B" }`.

For even more compact storage, consecutive deltas can be merged. Instead of storing 10 consecutive deltas (each recording a small change), merge them into a single delta that records the cumulative change:

```python
def merge_deltas(deltas: List[StateDelta]) -> StateDelta:
    """Merge consecutive deltas into a single cumulative delta."""
    merged = StateDelta(
        tick_start=deltas[0].tick_start,
        tick_end=deltas[-1].tick_end,
        property_changes={},
        entity_creations=[],
        entity_deletions=[],
        relationship_additions=[],
        relationship_removals=[],
    )
    
    for delta in deltas:
        # Property changes: later values overwrite earlier values
        merged.property_changes.update(delta.property_changes)
        
        # Entity creations: only keep if not later deleted
        # (This requires tracking the lifecycle of each entity)
        for entity in delta.entity_creations:
            if entity.id not in merged.entity_deletions:
                merged.entity_creations.append(entity)
        
        # ... (similar logic for other fields)
    
    return merged
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 8.
- Chang, F. et al. (2008). "Bigtable: A Distributed Storage System for Structured Data." *ACM Transactions on Computer Systems*, 26(2), Article 4.

### Discussion Questions

1. Merging deltas is lossy: intermediate states are lost. When is merging appropriate, and when must individual deltas be preserved for audit purposes?

2. Differential storage is efficient for writes, but how does it affect reads? To reconstruct the state at tick T, you must apply all deltas from the last full snapshot. How can this read cost be minimized?

3. Consider a simulation where most entities change slowly (one or two properties per tick) but a few entities change rapidly (all properties per tick). How would you optimize differential storage for this mixed workload?

---

## Lecture 5: The Mímir Protocol — Query-Efficient World State Retrieval

### The Query Problem

A world state store is only useful if it can be queried efficiently. The fundamental queries are:

1. **Point query:** What is the current value of entity E's property P?
2. **Range query:** What entities are in district D?
3. **Temporal query:** What was the value of entity E's property P at tick T?
4. **Aggregate query:** What is the current population of the city?
5. **Pattern query:** Which entities have a relationship of type R to entity E?

Each of these queries requires a different indexing strategy. Point queries benefit from hash indexes. Range queries benefit from tree indexes. Temporal queries benefit from the snapshot + event log structure. Aggregate queries benefit from pre-computed materialized views. Pattern queries benefit from graph indexes.

### The Mímir Protocol Architecture

The Mímir Protocol uses a multi-layer indexing architecture:

```
┌─────────────────────────────────────────────────────┐
│                  Query Interface                      │
│         (SQL-like query language for world state)      │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │ Hash Index   │  │ Tree Index  │  │ Graph Index │  │
│  │ (point       │  │ (range      │  │ (pattern    │  │
│  │  queries)    │  │  queries)   │  │  queries)   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │
│         │                │                 │          │
│  ┌──────┴────────────────┴─────────────────┴───────┐  │
│  │           Materialized Views                    │  │
│  │  (pre-computed aggregates for common queries)  │  │
│  └──────────────────────┬────────────────────────┘  │
│                         │                            │
│  ┌──────────────────────┴────────────────────────┐  │
│  │           Snapshot Store                       │  │
│  │  (full + incremental snapshots)               │  │
│  └──────────────────────┬────────────────────────┘  │
│                         │                            │
│  ┌──────────────────────┴────────────────────────┐  │
│  │           Event Log                            │  │
│  │  (append-only, hash-chained)                  │  │
│  └──────────────────────────────────────────────┘  │
│                                                       │
└──────────────────────────────────────────────────────┘
```

### Temporal Queries

The most distinctive feature of the Mímir Protocol is its support for temporal queries — queries about past states. This is enabled by the snapshot + event log structure:

1. To answer a temporal query at tick T, find the nearest snapshot at or before tick T.
2. Apply all incremental snapshots and events between the snapshot and tick T.
3. Return the resulting state.

This is efficient because:
- Finding the nearest snapshot is O(log N) using a binary search.
- Applying incremental snapshots is O(K) where K is the number of changes between the snapshot and tick T.
- Applying events is O(M) where M is the number of events in the interval.

In practice, temporal queries are fast enough for interactive use when the snapshot frequency is appropriately tuned.

### Lab 2: Implementing the Mímir Protocol

In this lab, you will implement the core of the Mímir Protocol:

1. An event store with append-only log and hash chaining.
2. A snapshot store with full and incremental snapshots.
3. A query interface that supports point, range, and temporal queries.
4. Index structures for efficient query processing.

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 8.
- Lomet, D. et al. (2008). "Improving Transaction Recovery by Integrating B-Tree Transaction Management with a Lightweight Write-Ahead Log." *Proceedings of SIGMOD*, 13–24.

### Discussion Questions

1. The Mímir Protocol uses multiple index types for different queries. How would you choose which indexes to maintain? What are the storage costs of each index type?

2. Temporal queries require replaying events from a snapshot. For very old queries (e.g., "What was the state at tick 1?"), replay can take a long time. How would you optimize very old temporal queries?

3. Consider a query that combines temporal and pattern aspects: "Who was married to Entity 42 on Day 100?" This requires both temporal reconstruction and graph traversal. How would you optimize this type of combined query?

---

## Lecture 6: The OS-Memory-World Interface — Where the Three Realms Meet

### The Three-Layer Architecture

An AI operating system, a memory system, and a world model are three distinct systems, but they must work together seamlessly. The OS manages processes and resources. The memory system stores and retrieves experiences. The world model maintains the state of the simulated world. The interface between these three systems is where persistence truly becomes powerful.

```
┌─────────────────┐
│   AI OS (Yggdrasil)  │
│   Process management │
│   Identity & goals   │
│   Prompt constitution│
└────────┬────────┘
         │ MuninnGate
┌────────┴────────┐
│   Memory System    │
│   MemCubes (OS201) │
│   MuninnGates (OS203) │
└────────┬────────┘
         │ Mímir Protocol queries
┌────────┴────────┐
│   World Model      │
│   Yggdrasil (OS107)│
│   WYRD Protocol    │
└──────────────────┘
```

The **MuninnGate** sits between the OS and the memory system. It governs what experiences are written, what memories are retrieved, and what is forgotten. When the OS encounters a new situation (e.g., the user asks a question about the simulated world), the MuninnGate surfaces relevant memories from the world model's persistence layer.

The **Mímir Protocol** sits between the memory system and the world model. It provides query-efficient access to the world state, allowing the memory system to retrieve specific pieces of world state without replaying the entire history.

### The Bridge: Context Injection

The most important function of the OS-memory-world interface is **context injection** — the process of surfacing relevant world state context to the agent's working memory when needed. This is the function of the MuninnGate's read policy: when the agent needs context about the simulated world, the MuninnGate determines which world state memories to surface.

Context injection follows a three-step process:

1. **Query generation:** The OS generates a query based on the agent's current task. "What is the current state of District 7?" "Who are the citizens in Building 12?" "What was the population on Day 42?"

2. **Memory retrieval:** The MuninnGate retrieves relevant memories from the memory system, using the Mímir Protocol to query the world model's persistence layer.

3. **Context insertion:** The retrieved memories are inserted into the agent's working context (the "Leaves" layer of the Yggdrasil cognitive architecture) for use in the current task.

```python
def inject_context(task: str, agent_state: AgentState, 
                   muninn_gate: MuninnGate, mimir: MimirProtocol) -> str:
    """Inject relevant world state context into the agent's working memory."""
    
    # Step 1: Generate query based on task
    query = generate_query(task, agent_state)
    
    # Step 2: Retrieve relevant memories
    memories = muninn_gate.retrieve(query, context=agent_state, top_k=10)
    
    # Step 3: Format and inject context
    context = format_context(memories)
    return f"{context}\n\n{task}"
```

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapters 5 and 8: "MuninnGate" and "The Well That Never Dries." University of Yggdrasil Press.
- Packer, C. et al. (2023). "MemGPT: Towards LLMs as Operating Systems." *arXiv preprint arXiv:2310.08560*.

### Discussion Questions

1. Context injection relies on the MuninnGate's read policy to select the most relevant memories. What are the risks of incorrect context injection? (Hint: injecting irrelevant context wastes space; injecting incorrect context may lead to hallucination.)

2. The Mímir Protocol provides temporal queries about the world state. Should the OS ever inject past world state into the agent's context without explicitly labeling it as historical? Discuss the risks of injecting unlabeled temporal context.

3. Consider a scenario where the MuninnGate's write policy is very permissive (stores everything). What happens to context injection quality over time? How does memory store size affect retrieval precision?

---

## Lecture 7: Event Sourcing Patterns for World Models — Beyond Simple CRUD

### CRUD vs. Event Sourcing

In a traditional CRUD (Create, Read, Update, Delete) architecture, the world state is a mutable data structure. When a citizen moves from Building A to Building B, the system updates the citizen's location property:

```
UPDATE citizens SET location = 'building_B' WHERE id = 'citizen_42';
```

The previous location (`building_A`) is lost. The system has no record of the move.

In an event-sourced architecture, the system records the move as an event:

```
APPEND event: { type: "move", entity: "citizen_42", from: "building_A", to: "building_B", tick: 1042 }
```

The current state can be reconstructed by replaying all events. And the history is preserved — the system knows that citizen_42 was in building_A before tick 1042 and in building_B afterward.

### Event Sourcing Patterns

Event sourcing enables several powerful patterns:

**1. Temporal Queries:** As discussed in Lecture 5, temporal queries are trivial with event sourcing — just replay events up to the target tick.

**2. Event Replay:** If a bug is found in a event handler, the bug can be fixed and all events can be replayed with the corrected handler. This is analogous to a database migration — the event log is the source of truth, and the current state is a derived view.

**3. Projection:** The same event log can be projected into multiple views. For example:
- A "current state" projection: materialize the current world state.
- A "population history" projection: track the population over time.
- A "trade volume" projection: compute the total volume of trade between districts.

All projections are derived from the same event log, ensuring consistency.

**4. Branching:** The simulation can be forked at any point by creating a new event log branch. Each branch can explore a different "what if" scenario. The branches share a common history up to the fork point, minimizing storage.

**5. Compensation:** If an event is found to be erroneous, a *compensation event* can be appended (not deleted) to reverse its effects. This preserves the audit trail while correcting the state.

### Lab 3: Advanced Event Sourcing Patterns

In this lab, you will implement:

1. Multiple projections from a single event log.
2. Event replay with a corrected handler.
3. Simulation branching from an arbitrary tick.
4. Compensation events for error correction.

### Required Reading

- Vernon, V. (2013). "Event Sourcing." *DDD Community*.
- Betts, D. et al. (2013). "CQRS Pattern." *Microsoft Azure Architecture Center*.

### Discussion Questions

1. Projection requires recomputing derived views from the event log. When should projections be updated — eagerly (on every event) or lazily (on every query)? What are the trade-offs?

2. Branching creates "what if" scenarios that share a common prefix. But the branches diverge over time. How long should branches be kept? Should they be merged back into the main log?

3. Compensation events reverse the effects of erroneous events, but they don't delete the erroneous events from the log. Is this always desirable? When would you want to actually delete an event?

---

## Lecture 8: Differential State and Incremental Snapshots — The Economy of Change

### The Mathematics of Incremental Change

The key insight of differential state storage is that the cost of storing a state change is proportional to the *size of the change*, not the *size of the state*. This is a direct consequence of the fact that most world state changes are small relative to the total state size.

Let S be the size of the full world state, and δ be the average size of a state change between ticks. Then:

- Full snapshot cost per tick: O(S)
- Incremental snapshot cost per tick: O(δ)
- Total snapshot cost with incremental snapshots: O(S × N_full + δ × N_incremental)

where N_full is the number of full snapshots and N_incremental is the number of incremental snapshots.

Typically, δ << S (by orders of magnitude), so incremental snapshots are vastly more efficient. A city simulation with 100,000 entities might have S = 500 MB but δ = 500 KB — a 1000x reduction in storage per tick.

### Delta Merging Strategies

Incremental snapshots accumulated over many ticks can be merged to reduce storage further. The Mímir Protocol uses a **tiered merging** strategy:

- **Level 0:** Individual deltas (one per tick). Kept for the most recent N ticks (e.g., N=100).
- **Level 1:** Merged deltas (10 consecutive deltas merged into one). Kept for the most recent M merged deltas (e.g., M=100).
- **Level 2:** Full snapshots. Taken every N × M ticks (e.g., every 1000 ticks).

This is analogous to the compaction strategy used in log-structured merge trees (LSM trees) in databases.

### Compression of Deltas

Deltas can be further compressed using standard compression algorithms (gzip, LZ4, Zstandard). The key insight is that deltas have very high redundancy — the same entities change in similar ways from tick to tick. Compression ratios of 10:1 or better are typical.

The Mímir Protocol uses Zstandard compression by default, with a configurable compression level. Higher compression levels produce smaller deltas but take longer to compress and decompress. For most applications, level 3 (the default) provides a good balance.

### Required Reading

- O'Neil, P. et al. (1996). "The Log-Structured Merge-Tree (LSM-Tree)." *Acta Informatica*, 33(4), 351–385.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 8.

### Discussion Questions

1. The tiered merging strategy keeps individual deltas for the most recent ticks and merged deltas for older ticks. What are the trade-offs between merge frequency and query performance?

2. Compression adds CPU overhead for both writes and reads. Under what circumstances is compression not worth the overhead? (Hint: consider in-memory simulations with fast networks.)

3. Consider a simulation that generates very large deltas (e.g., a weather simulation where the entire atmosphere changes every tick). How would you optimize differential storage for this scenario?

---

## Lecture 9: World State Integrity — The Cryptographic Well

### Trusting the State

In a distributed or adversarial environment, the integrity of the world state is paramount. If an attacker can modify the event log, they can change the world's history without detection. If a hardware error corrupts a snapshot, the reconstructed state may be incorrect.

The Mímir Protocol ensures integrity through three mechanisms:

1. **Hash chaining:** Each event includes a hash of the previous event. This forms a chain that cannot be modified without detection.

2. **Merkle trees:** Each snapshot includes a Merkle tree root hash. This allows efficient integrity verification of any part of the snapshot without downloading the entire snapshot.

3. **Digital signatures:** Each event is signed by the simulation that produced it. This prevents unauthorized modifications.

### Hash Chaining

The hash chain is the foundation of event log integrity. Each event's `causality_hash` field is the SHA-256 hash of the previous event's binary encoding. This creates a cryptographic link between events:

```
event_0: { ..., causality_hash: SHA256("genesis") }
event_1: { ..., causality_hash: SHA256(encode(event_0)) }
event_2: { ..., causality_hash: SHA256(encode(event_1)) }
...
event_n: { ..., causality_hash: SHA256(encode(event_{n-1})) }
```

If any event is modified, all subsequent hashes will be invalid. This makes the event log tamper-evident — any modification is immediately detectable.

### Merkle Trees

A Merkle tree is a binary hash tree where each leaf is the hash of a data block (in our case, a snapshot segment), and each internal node is the hash of its two children:

```
         Root Hash
        /         \
   Hash_AB      Hash_CD
   /    \       /     \
 Hash_A Hash_B Hash_C Hash_D
   |      |      |      |
 Data_A Data_B Data_C Data_D
```

The root hash is stored alongside the snapshot metadata. To verify the integrity of Data_A, you only need Hash_B, Hash_CD, and the root hash — you don't need to download the entire snapshot. This is efficient for large snapshots and enables partial verification.

### Lab 4: Implementing Integrity Checks

In this lab, you will implement:

1. Hash chaining for the event log.
2. Merkle trees for snapshot integrity.
3. A verification function that checks the integrity of the entire log.
4. A benchmark measuring the performance impact of integrity checks.

### Required Reading

- Merkle, R. (1980). "Protocols for Public Key Cryptosystems." *Proceedings of the IEEE Symposium on Security and Privacy*, 122–134.
- Nakamoto, S. (2008). "Bitcoin: A Peer-to-Peer Electronic Cash System." (For hash chaining and Merkle tree applications.)

### Discussion Questions

1. Hash chaining prevents modification of past events. But what about deletion? If an attacker deletes the last N events, the remaining chain is still valid. How can you detect event deletion?

2. Merkle trees enable partial verification. But how do you know that the root hash you have is the correct one? Discuss the trust assumptions of Merkle tree verification.

3. Integrity checks add computational overhead. In a high-throughput simulation (millions of events per second), can integrity checks be deferred or batched? What are the trade-offs between integrity and performance?

---

## Lecture 10: Distributed Persistence — Worlds Across Machines

### The Distributed World

A world simulation that spans a single machine is limited by that machine's resources. To simulate larger worlds (millions of entities, global scale), the simulation must be distributed across multiple machines.

Distributed persistence introduces several challenges:

1. **Consistency:** How do you ensure that all machines agree on the world state?
2. **Partition tolerance:** How do you handle network partitions (machines that cannot communicate)?
3. **Availability:** How do you ensure that the world remains accessible even when some machines fail?

These are the three pillars of the CAP theorem: Consistency, Availability, and Partition tolerance. You can have at most two of the three in any distributed system.

### The Mímir Distributed Protocol

The Mímir Protocol's distributed extension uses a **partitioned event log**:

- Each machine owns a *partition* of the event log (e.g., events related to entities in a specific district).
- Events are routed to the appropriate partition based on the target entity.
- Cross-partition events (events that affect entities in multiple partitions) are handled by a two-phase commit protocol.

This architecture provides:
- **Scalability:** Adding machines increases capacity.
- **Locality:** Most events affect entities in a single district, so most processing is local.
- **Consistency:** The two-phase commit protocol ensures that cross-partition events are applied consistently.

### Required Reading

- Kleppmann, M. (2017). *Designing Data-Intensive Applications*, Chapter 9: "Consistency and Consensus." O'Reilly.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 8.

### Discussion Questions

1. The partitioned event log routes events to machines based on entity location. But what about entities that move between districts? How should events for mobile entities be handled?

2. The two-phase commit protocol ensures consistency but requires all participating machines to be available. What happens if one machine fails during a commit? Discuss recovery strategies.

3. The CAP theorem says you can have at most two of consistency, availability, and partition tolerance. In a world simulation, which two would you choose? Why?

---

## Lecture 11: Persistence and the AI OS Memory Stack — Bridging the Realms

### The Full Memory Stack

The persistence layer is part of a larger memory stack that spans the AI OS, the memory system, and the world model:

```
┌─────────────────────────────────────┐
│ Working Memory (Leaves)             │ ← Agent's active context
│ - Current conversation             │    (conversation buffer, task stack)
│ - Current task                      │
├─────────────────────────────────────┤
│ Episodic Memory (Canopy)            │ ← Recent experiences
│ - Recent conversations              │    (MuninnGate read/write)
│ - Recent events                     │
├─────────────────────────────────────┤
│ Procedural Memory (Trunk)           │ ← Learned skills
│ - How to write code                 │    (MuninnGate read, slow write)
│ - How to analyze data               │
├─────────────────────────────────────┤
│ Identity Memory (Roots)             │ ← Core identity
│ - Who I am                          │    (Write-once, always readable)
│ - What I value                      │
├─────────────────────────────────────┤
│ World State Persistence (Mímir)      │ ← Simulated world state
│ - Event log                         │    (Event sourcing, snapshots)
│ - Snapshots                         │
│ - Queries                           │
└─────────────────────────────────────┘
```

Each layer has its own persistence requirements:

- **Working Memory:** Ephemeral. Not persisted between sessions. Reconstructed from the conversation context.
- **Episodic Memory:** Persisted via MuninnGates. Event-sourced within the memory system.
- **Procedural Memory:** Persisted via MuninnGates. Written slowly (skills take time to learn) and read frequently.
- **Identity Memory:** Persisted via MuninnGates. Written once, never pruned.
- **World State Persistence:** Persisted via the Mímir Protocol. Event-sourced with incremental snapshots.

### The Bridge Protocol

The Bridge Protocol connects the MuninnGate (memory system) to the Mímir Protocol (persistence layer). When the MuninnGate needs to retrieve world state information, it uses the Bridge Protocol:

1. The MuninnGate generates a context query based on the agent's current task.
2. The Bridge Protocol translates the context query into a Mímir Protocol query.
3. The Mímir Protocol retrieves the relevant world state and returns it to the Bridge.
4. The Bridge Protocol wraps the world state in a memory format that the MuninnGate understands.
5. The MuninnGate injects the memory into the agent's working context.

This five-step process ensures that world state information is always retrieved through the proper channels, with appropriate filtering, formatting, and context injection.

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapters 5–8.
- Packer, C. et al. (2023). "MemGPT: Towards LLMs as Operating Systems." *arXiv preprint arXiv:2310.08560*.

### Discussion Questions

1. The memory stack has five layers, each with different persistence requirements. Should all layers use the same storage backend (e.g., SQLite, RocksDB), or should each layer use a storage backend optimized for its access pattern?

2. The Bridge Protocol translates between the MuninnGate's context query and the Mímir Protocol's state query. Is this translation lossless? What information might be lost in the translation?

3. Consider a scenario where the world state changes while the agent is processing a query. How should the Bridge Protocol handle stale world state? Options: (a) return the state as of the query time, (b) return the latest state, (c) inform the agent that the state has changed and let it decide.

---

## Lecture 12: Mímir's Droplet — Course Synthesis and Capstone Project

### Summary: The Well That Never Dries

We began this course with the impermanence problem: a world model that exists only in RAM ceases to exist when the process dies. We end with the Mímir Protocol: a comprehensive persistence architecture that ensures world state survives crashes, migrations, and the passage of time.

The event log is the well's water — a complete record of everything that has happened, append-only and tamper-evident. The snapshots are the well's buckets — convenient containers that allow rapid access to specific moments in time. The Mímir Protocol is the well itself — a structure that stores, indexes, and serves the accumulated wisdom of the simulated world.

Together with the MuninnGate (OS203) and the Yggdrasil cognitive architecture (OS107), the Mímir Protocol completes the persistence layer of the AI OS. Events flow from the world model through the Mímir Protocol, are filtered by the MuninnGate, and are injected into the agent's working context by the Bridge Protocol. The cycle is complete: the world remembers, the gate selects, and the agent acts.

### Capstone Project: Event-Sourced World State Store

Your capstone project is to implement a complete event-sourced world state store with the Mímir Protocol:

1. **Event Store:** Append-only event log with hash chaining and sequence numbers.
2. **Snapshot Store:** Full and incremental snapshots with tiered merging.
3. **Query Interface:** Point, range, and temporal queries with hash, tree, and graph indexes.
4. **Integrity Checks:** Hash chain verification and Merkle tree verification for snapshots.
5. **Delta Storage:** Differential state storage with compression.

**Submission Requirements:**

1. Complete source code (Python 3.11+, with type hints and docstrings).
2. Unit tests covering all operations (write, read, snapshot, query, integrity).
3. Benchmark results showing write throughput, query latency, and snapshot compression ratio.
4. A design document (5–8 pages) describing your architecture, design decisions, and trade-offs.

### The Well Remembers

Mímir's well never dries. Every event is recorded. Every state is recoverable. Every query is answerable. The persistence layer is the foundation on which all other layers rest — and like the roots of Yggdrasil, it drinks deep from the waters below.

**ᛟ Othala — Ancestral Inheritance. The well remembers what the world forgets.**

---

*Course materials © 2044 University of Yggdrasil. All rights reserved.*
*ᛟ Othala — The well remembers.*
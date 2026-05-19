# WM103: Entity-Component-System Architectures for AI
## The Dwarves' Forge

**Program:** BS in AI World Modeling  
**Year:** 1 | **Semester:** 1  
**Credit Hours:** 4  
**Lecture Count:** 12  

---

> *In the deep halls beneath the mountain, the dwarves do not forge a single sword — they forge the hilt, the blade, the pommel, the guard, each a separate masterwork. Nor does any dwarf wield the whole sword at once; rather, each warrior takes up the parts they need, combinations no smith foresaw. This is the way of the Forge: separate craft, compositional might. So too with entities in a world model: no monolith, but an assemblage — each component a crafted thing, each entity a wielder, and each system a rhythm of the hammers that brings the world to life.*

---

## Lecture 1: The Dwarves' Forge — An Introduction to Entity-Component-System Architecture

### Overview

The Entity-Component-System (ECS) pattern has become the dominant architectural paradigm in interactive world simulation, from game engines like Unity's DOTS and Unreal's Mass to research platforms for multi-agent AI. Yet ECS is more than a software engineering convenience; it is an ontological commitment about how state and behavior should be composed. This lecture introduces ECS from its historical roots in game development through its emergence as a foundational architecture for AI world modeling.

The traditional object-oriented paradigm models the world as a taxonomy of classes — a `Creature` inherits from `Agent` which inherits from `Entity`. This hierarchical ontology, while intuitive, encodes a brittle assumption: that the important distinctions in a world can be foreseen and arranged in a tree. The dwarves know better. A sword is not a subclass of weapon; it is a thing with a blade component and a handle component and a balance component, and the same blade component might appear on a polearm for entirely different reasons of composition. ECS inverts the ontology: instead of defining what a thing *is*, we define what a thing *has*.

An **entity** is an identifier — a bare key, a row index, an existential claim that something exists. A **component** is a structured fragment of state — a typed container for data, attached to an entity by the mere fact of shared identity. A **system** is a function, a deterministic transformer that reads components and writes components, iterating over all entities that possess a particular combination. No inheritance, no virtual dispatch, no fragile base class. The dwarves craft components on separate anvils; entities wield them freely; systems are the forge-fires that animate the collection.

We will survey the evolution from early entity-component frameworks (such as the original 2002 GDC presentation by Adam Martin and the subsequent refinement by members of the t-machine community) through modern high-performance implementations (EnTT, Flecs, Arch's `archetype` crate). We will examine why ECS gained traction: cache coherence, compositional flexibility, and the separation of data from behavior. The lecture concludes with a first look at the course project: building an ECS kernel from scratch, to which we will add AI-specific features across the semester.

### Key Concepts

- **Entity as identity token.** An entity carries no state; it merely *is*. The integer `entity_id = 37` asserts existence. The dwarf who bears the artifact needs no internal property — the properties cling to the artifact itself.
- **Component as typed data fragment.** A component is a plain-old-data struct: `Position { x: f32, y: f32, z: f32 }`. It knows nothing of the entity it inhabits. The forge produces components independently.
- **System as pure iteration.** A system queries for all entities possessing components `(A, B)` and applies a deterministic transformation. The hammer falls on every blade in sequence; no blade tells another blade how to be struck.
- **Composition over inheritance.** ECS replaces `class FlyingEnemy : public Enemy` with `entity { Position, Velocity, WingFlap, Hostile }`. A new combination arises without recompiling a hierarchy.

### Readings

- Nystrom, R. *Game Programming Patterns*, Chapter on "Component Pattern" and "Decoupling Patterns." (Primary)
- Gregory, J. *Game Engine Architecture*, 3rd ed., Chapter 14: "Gameplay Foundation Systems." (Supplementary)
- Skypjack, M. "EnTT: Gaming with Modern C++" — blog series and documentation (Practical reference)
- Original t-machine ECS thread archive (2007–2010), archived at gamedev.net (Historical)

### Discussion Questions

1. If an entity is merely an integer, what prevents two components intended for different logical entities from being confused? How does this mirror or differ from the problem of object identity in object-oriented languages?
2. The dwarf forge metaphor emphasizes independent crafting. Yet in a real forge, components must interface — a blade must fit a hilt. How does ECS handle inter-component dependencies without reintroducing coupling?
3. Consider a world model where an AI agent must reason about "the entity that is both a parent and a predator." In OOP, this might be a multiple-inheritance nightmare. How does ECS reframe this problem?

---

## Lecture 2: Entities — The Wielders of Crafted Things

### Overview

Entities are the most paradoxical element of ECS: they are everything and nothing. An entity is an identifier, a numerical token asserting that *something exists*. It carries no methods, no state, no vtable. It is, in the language of the forge, a dwarf who has not yet picked up any artifacts — a potential, a slot in the world's ledger. This lecture examines the entity lifecycle, identity, and the subtle design decisions that shape an ECS kernel.

We begin with the fundamental question: what is an entity? Implementation varies across ECS frameworks. In some, an entity is a bare `u32` or `u64` integer. In others, such as the EnTT framework, an entity encodes both a unique identifier and a version counter in its bit layout, enabling detection of use-after-free bugs when an entity identifier is recycled. In Flecs, an entity is an index into a world table, with a generation counter appended to detect stale references. These are not mere implementation details — they reflect deep decisions about how existence, identity, and death are modeled.

**Entity creation and destruction.** When a dwarf enters the forge, a slot is assigned. When a dwarf departs, the slot may be reused. Entity pools typically use slab allocation or free-list management. We will examine the trade-offs between dense allocation (entity IDs are contiguous indices) and sparse allocation (entity IDs may have gaps, supporting free-list recycling). We consider the implications for cache locality and for the correctness of component lookup.

**Archetype and the entity's role.** Though we will cover archetypes in depth in Lecture 6, we preview the concept here: an entity's *archetype* is the set of component types it currently possesses. When components are added or removed, the entity's archetype changes, and the entity's data must be migrated between storage tables. The dwarf who picks up a new shield has moved to a new archetype — the forge must reorganize its shelves.

**Entity hierarchies and relationships.** Some ECS frameworks support parent-child relationships among entities. In the forge, a sword may be composed of sub-entities: the blade entity, the hilt entity, and the pommel entity. We examine how hierarchical relationships are themselves modeled as components (a `Parent` component, a `ChildOf` component) rather than as intrinsic entity properties, preserving the ECS commitment to composition.

**Tag entities and empty entities.** Not all entities need components. A tag entity (an entity possessing only marker components like `IsVisible` or `IsEnemy`) serves as a categorization mechanism. A completely empty entity serves as a root node or a sentinel. The forge produces even unmarked steel — existence without adornment.

We will implement the first module of our kernel: an `EntityAllocator` that supports creation, destruction, versioning, and iteration over living entities.

### Key Concepts

- **Entity as opaque identifier.** The entity ID must not be dereferenced to obtain state; it is a key, not a pointer.
- **Version counters.** A mechanism to detect stale references after entity recycling, analogous to generational indices.
- **Entity lifecycle:** create → add components → (use) → remove components → destroy. The last step reclaims the identifier.
- **Archetype-aware entity storage.** Entities are not stored in a single array; they are partitioned by component signature into archetype tables.

### Readings

- Skypjack, M. "Entity Component System — Entity Id" (blog, EnTT internals series)
- Flecs documentation: "Entities" chapter — flecs.docs
- Acton, M. "Data-Oriented Design and C++" (CppCon 2014) — relevance to entity-as-index vs. entity-as-pointer
- Nystrom, R. *Game Programming Patterns*, § "Flyweight" and "Object Pool" patterns for entity allocation

### Discussion Questions

1. Should entity identifiers be stable across serialization boundaries? If an entity ID changes when a world is saved and reloaded, what breaks?
2. Some ECS frameworks allow entities to "inherit" components from prototypes or prefabs. Is this a reintroduction of inheritance, or a legitimate compositional tool? Where does the line fall?
3. If an entity is destroyed but a system still holds a reference to its ID (from a query earlier in the frame), what should happen? Discuss the trade-offs between immediate deletion, deferred deletion, and reference counting.

---

## Lecture 3: Components — The Crafted Things of State and Data

### Overview

If entities are the wielders, components are the things they wield. A component is a fragment of state — a typed, structured, self-contained data unit that attaches to an entity by the shared identity of the entity's ID. This lecture examines the design of components as data contracts, the compositional model that makes ECS powerful, and the tension between simplicity and expressiveness.

**Components as plain data.** The orthodox ECS position — sometimes called the *pure ECS* or *data-oriented ECS* — holds that components should be plain-old-data (POD) structs with no methods, no references to other components, and no behavioral logic. A `Health` component is `{ current: f32, max: f32 }`. A `Weapon` component is `{ damage: i32, range: f32, cooldown_timer: f32 }`. The dwarf forge produces these as independent artifacts; the system that uses them knows how they fit together, but the component itself is silent about its role.

**Compositional state design.** The power of ECS lies in composition. An entity that is both `Health` and `Weapon` is a combatant. An entity that is `Health`, `Weapon`, and `IsAlly` is a friendly combatant. No class hierarchy can predict every combination; the forge produces unlimited arrangements. We examine *component granularity*: should `Position` and `Velocity` be separate components, or should they be combined into a `Kinematics` component? The answer depends on access patterns. If most systems need both, coarser granularity improves locality. If systems frequently need one without the other, finer granularity avoids fetching unnecessary data. This is the smith's trade: knowing when to forge a single integrated piece and when to craft separate fittings.

**Shared components and instancing.** Some data is truly shared across many entities — a mesh reference, a sound bank, a personality profile. We examine patterns for shared components: reference-counted handles, flyweight indices, and the "shared component" pattern used in Flecs. The forge does not duplicate the master mold for every sword; it stamps each from the same die.

**Component dependencies and invariants.** While pure ECS discourages components from referencing other components, practical systems require invariants: `Velocity` without `Position` is meaningless for a movement system. We discuss *component requirements* as system-level contracts rather than component-level constraints. The movement system queries for `(Position, Velocity)`; entities lacking either are simply not iterated. The forge does not enforce that a blade must have a hilt — it merely produces all blades and all hilts separately, and the warrior who carries a blade without a hilt will discover the problem when the cutting system runs.

**Tag components.** A component with no data fields — `struct IsEnemy;` — is a tag. Tags cost zero storage (they exist only in the archetype signature) but enable type-level filtering. The forge marks certain artifacts with a maker's mark that adds no physical property but identifies their class.

We will implement the component storage layer of our kernel: a type-erased component pool that stores components contiguously, indexed by entity, and supports add, remove, get, and iteration.

### Key Concepts

- **Component as data contract.** A component defines the shape of a piece of state; it does not define behavior.
- **Compositional state.** The set of components on an entity defines what the entity *is for* in the context of any given system, without committing to a global ontology.
- **Component granularity.** The design space between fine-grained (many small components, maximum flexibility) and coarse-grained (fewer larger components, better cache locality).
- **Tag components.** Zero-size markers that participate in archetype matching but consume no storage.
- **Shared components.** Patterns for data that is identical across many entities.

### Readings

- Gregory, J. *Game Engine Architecture*, 3rd ed., §§ 14.5–14.7 (Component model implementation details)
- Caini, M. "ECS Back and Forth" — blog series on EnTT design decisions
- Skypjack, M. "ECS: What Are Components?" (EnTT blog)
- Acton, M. "Data-Oriented Design" — relevance to component layout and cache lines

### Discussion Questions

1. Is there a principled way to decide component granularity, or is it always an empirical tuning decision? Propose a metric or heuristic.
2. Consider a `Targeting` component that references another entity: `Targeting { target: Entity }`. This introduces a reference between components. Is this still "pure ECS"? What are the failure modes when `target` is destroyed?
3. Tags cost zero storage but are they truly free? What is the cost of an archetype that includes a large number of tag-only components?

---

## Lecture 4: Typed Memory Slices — Component Storage and the Architecture of the Forge's Shelves

### Overview

The forge organizes its artifacts not by which dwarf will wield them, but by what they are. All blades on one shelf, all hilts on another, all pommels on a third. This is the essence of archetype-based ECS storage, and it is the topic of this lecture. We examine how components are stored in memory, how entities are mapped to their components, and how query iteration over component data achieves cache-friendly performance.

**Sparse sets.** The foundational data structure for component storage is the sparse set. A sparse set maintains two arrays: a *sparse* array indexed by entity ID, and a *dense* array indexed by a compact counter. Adding a component for entity `e` appends the data to the dense array and stores the dense-array index in `sparse[e]`. This gives O(1) add, O(1) lookup, and O(1) iteration (by iterating the dense array). We derive sparse sets from first principles and implement them.

**Archetype-based storage.** When querying for all entities with `(Position, Velocity)`, we want to iterate both arrays simultaneously. If `Position` and `Velocity` are in separate sparse sets indexed by entity, iteration requires indirect access — two pointer hops per entity. Archetype storage solves this: entities with the same component signature (the same *archetype*) are stored together, with components laid out column-wise in a structure-of-arrays (SoA) table. Iterating `(Position, Velocity)` over an archetype is a linear scan through two parallel arrays — a textbook cache-friendly pattern.

We diagram the storage layout:

```
Archetype [Position, Velocity, Health]
┌─────────────┬────────────┬──────────┐
│ Position[]  │ Velocity[] │ Health[] │
├─────────────┼────────────┼──────────┤
│ (1.0, 2.0)  │ (0.5, 0.0) │ 100.0    │  ← entity 7
│ (3.0, 1.0)  │ (0.0, 0.3) │  85.0    │  ← entity 12
│ ...         │ ...        │ ...      │
└─────────────┴────────────┴──────────┘
```

**The archetype graph.** When a component is added or removed, an entity moves from one archetype to another. Archetypes are connected in a graph: each archetype has edges corresponding to "add component X" and "remove component X." This graph enables O(1) archetype transit.

**Typed memory slices.** In Rust-based ECS frameworks, component data is often presented to systems as *typed memory slices* — borrowed `&[T]` arrays with type-level guarantees. This is as close to bare-metal iteration as possible in a safe language. The forge's shelves are exactly this: typed, contiguous memory that the system iterates without indirection.

**Component pools in detail.** We implement `ComponentPool<T>`, a generic sparse-set-backed storage for components of type `T`. We then implement `Archetype`, a table of heterogeneous component columns, keyed by archetype ID. Finally, we implement `World`, the top-level container that holds the entity allocator, archetype tables, and the archetype graph.

### Key Concepts

- **Sparse set.** O(1) add, lookup, remove, and iteration. The workhorse of component storage.
- **Structure of Arrays (SoA).** Component data is stored in parallel arrays rather than arrays of structs, enabling cache-friendly system iteration.
- **Archetype.** A unique component signature. Entities with the same archetype share a storage table.
- **Archetype graph.** A directed graph connecting archetypes by add/remove component edges.
- **Typed memory slice.** A borrowed `&[T]` from a component column, providing zero-cost abstraction for system iteration.

### Readings

- Skypjack, M. "ECS: Archetypes, SoA, and Sparse Sets" (EnTT blog series)
- Caini, M. "Archetypes and Vectorization" — practical analysis of SoA benefits
- Acton, M. "Data-Oriented Design and C++" (CppCon 2014) — foundational talk on SoA and cache awareness
- Freitag, S. "Entity-Component-System: A Data-Oriented Approach" (GDC Onward talk summary)

### Discussion Questions

1. Sparse sets allow O(1) addition and removal but require an indirection for random access. Archetype tables allow linear iteration but require entity migration on add/remove. Under what access patterns does each excel? Can a hybrid approach combine both strengths?
2. The archetype graph assumes that the set of archetypes is bounded and tractable. What happens in a world model where every entity has a unique combination of, say, 50 possible components? How many archetypes are created?
3. Typed memory slices provide safety guarantees at the Rust type level. How would you provide similar iteration safety in a language without Rust's borrow checker (e.g., C++, Python)?

---

## Lecture 5: Systems — Deterministic State Transformers and the Rhythm of the Hammers

### Overview

If components are the crafted artifacts and entities are the wielders, systems are the hammers — the rhythmic, deterministic transformers that read input components and write output components, frame after frame, bringing the forge to life. A system in ECS is a pure function over component data, iterating over all entities that match a query. This lecture examines the design, scheduling, and execution of systems.

**Systems as functions.** A system is defined by its query — the set of component types it reads and writes — and its logic. In pure ECS, a system has no internal mutable state. It is a stateless transformer: given the same component data, it produces the same output. This determinism is the beating heart of the forge. The hammer strikes the same way every time; only the steel differs.

```
fn movement_system(positions: &mut [Position], velocities: &[Velocity]) {
    for i in 0..positions.len() {
        positions[i].x += velocities[i].x;
        positions[i].y += velocities[i].y;
    }
}
```

**Access patterns and conflict detection.** Two systems conflict if they access the same component type and at least one writes to it. A `Position` writer conflicts with another `Position` writer, and a `Position` writer conflicts with a `Position` reader. Conflicting systems must be serialized; non-conflicting systems may run in parallel. We examine the access-level classification: `Read`, `Write`, and `ReadOptional`, and how schedulers use this information to build a dependency DAG.

**System scheduling.** We implement a simple topological-sort scheduler that resolves system ordering from declared dependencies. More advanced schedulers (such as Flecs's pipeline or Unity's DOTS SystemBase) support automatic parallelization based on component access declarations. The forge runs multiple hammers simultaneously when they strike different anvils.

**Command buffers and deferred mutations.** Systems must not add or remove entities or components during iteration — doing so would invalidate the very iterators they are using. Instead, mutations to the entity-component topology (spawning, despawning, adding, removing components) are recorded in *command buffers* that are flushed between system execution phases. The dwarf does not reorganize the shelves while another dwarf is counting the artifacts.

**System ordering and phases.** Most ECS frameworks define execution phases: `PreUpdate`, `Update`, `PostUpdate`, `Render`, etc. Systems are registered into phases, and within a phase, ordering is determined by explicit dependencies or by the access-conflict DAG. We will define our own phase structure suitable for AI simulation loops.

**Pure functions and side effects.** We revisit the question of side effects in systems. A system that logs, sends network packets, or sets non-ECS global state is *impure*. We discuss strategies for isolating side effects: the Command pattern, event buses, and the relationship between ECS systems and event-sourced architectures.

### Key Concepts

- **System as stateless function.** A system's behavior depends only on its input components and its parameters, not on hidden mutable state.
- **Access pattern declaration.** Systems declare which components they read/write, enabling conflict detection and parallel scheduling.
- **Command buffers.** Deferred execution of structural mutations (spawn, despawn, add/remove component) to avoid iterator invalidation.
- **Execution phases.** Ordered groups of systems that define the global update loop's structure.
- **Dependency DAG.** A directed acyclic graph derived from component access patterns and explicit ordering constraints.

### Readings

- Gregory, J. *Game Engine Architecture*, 3rd ed., §§ 14.6–14.7 (System scheduling)
- Flecs documentation: "Pipelines" and "Systems" chapters
- Unity DOTS documentation: "SystemBase" and "EntityCommandBuffer"
- Skypjack, M. "ECS: Systems, Views and Groups" (EnTT blog)

### Discussion Questions

1. If systems must be stateless, where does "learning" go? An AI system that updates a neural network weight component is deterministic given its inputs — but the weights change over time. Is this a violation of purity, or merely long-range state carried through components?
2. Command buffers defer mutations until a synchronization point. What are the trade-offs of this design decision vs. immediate execution with copy-on-write component data?
3. Consider a system that needs to query "all entities within 5 meters of entity X." This is a spatial query, not a component-type query. How should spatial indexing be integrated into ECS without violating the pure-iteration model?

---

## Lecture 6: Archetype-Based Storage and Performance Optimization for Entity Iteration

### Overview

Performance is not an afterthought in ECS — it is the reason ECS exists. The forge exists because indirection is expensive: a virtual function call costs more than a cache miss, and a cache miss costs more than a hundred arithmetic operations. This lecture examines archetype-based storage in depth and surveys the performance optimization techniques that make ECS suitable for world models containing millions of entities.

**Archetype deep dive.** We revisit archetypes from Lecture 4 with a focus on the implementation details that affect performance. An archetype is identified by a type signature: a sorted set of component type IDs. The signature is typically encoded as a bitmask or a hash, enabling O(1) comparison. Each archetype stores its component columns as contiguous `Vec<T>` arrays. The entity-to-archetype mapping is a single indirection: `entity_index → archetype_id, row_index`.

**World fragmentation.** The number of archetypes grows with the number of unique component combinations. In a world model with 30 component types and each entity having 5–10 components, the number of archetypes can reach tens of thousands. While the theory is elegant, in practice, archetype proliferation (*world fragmentation*) can reduce iteration density — each archetype's column may contain only a handful of entities, making the linear scan less efficient than the O(n) model predicts. We examine strategies for mitigating fragmentation: component grouping, archetype merging, and the use of heterogeneous queries that accept multiple archetype layouts.

**Cache-friendly iteration patterns.** We benchmark naive iteration patterns against SoA-optimized patterns:

- AoS (Array of Structures): iterating `for e in entities { process(e.pos, e.vel, e.hp) }` — one cache miss per entity.
- SoA (Structure of Arrays): iterating `for i in 0..len { process(pos[i], vel[i], hp[i]) }` — three sequential scans with excellent prefetch.

We demonstrate that for component sets smaller than the L2 cache, SoA iteration can be 4–10× faster than AoS iteration.

**SIMD and vectorized systems.** When component data is laid out in SoA columns, systems can be auto-vectorized by the compiler. We examine writing systems in a style that enables LLVM or the CPU to emit SIMD instructions: float4 processing, swizzle-friendly data layout, and the use of iterators that yield chunks of cache-line-aligned data.

**Batched archetype processing.** Instead of iterating entity-by-entity, we iterate *archetype-by-archetype*. Each archetype yields a batch of homogeneous component slices. The system processes each batch in a tight inner loop, maximizing data locality.

**Parallel system execution.** Two systems that do not access overlapping components can run concurrently. We implement a work-stealing scheduler that assigns archetype batches to worker threads. The key insight: archetype iteration is *embarrassingly parallel* within a system because each batch is independent.

**Profiling and hotspot analysis.** We profile our ECS kernel with representative world models (10K, 100K, 1M entities) and identify the dominant costs: component iteration, archetype lookup, and command buffer flush. We discuss flame graph analysis and the use of hardware performance counters.

### Key Concepts

- **Archetype signature.** A unique identifier for a component combination, enabling fast archetype lookup and comparison.
- **World fragmentation.** The proliferation of archetypes that reduces iteration density.
- **SoA vs. AoS iteration.** Structure-of-Arrays enables cache-friendly sequential access; Array-of-Structures causes cache thrashing.
- **SIMD vectorization.** Data-oriented system implementations that allow compiler auto-vectorization.
- **Batched iteration.** Processing one archetype at a time, yielding dense component slices.

### Readings

- Acton, M. "Data-Oriented Design and C++" (CppCon 2014, full talk)
- Skypjack, M. "ECS: Archetypes Under the Hood" (EnTT internals)
- Gregory, J. *Game Engine Architecture*, § 3.4 (Cache and memory optimization)
- Freitag, S. and Glinka, F. "A Data-Driven Approach to Entity Management" (Software Practice & Experience, 2022)

### Discussion Questions

1. World fragmentation is a real concern for AI world models where agents accumulate many small unique components (e.g., individual memories, learned weights). Propose a strategy to limit archetype proliferation in such models.
2. SIMD vectorization requires uniform processing — no branching within the inner loop. How should conditionals be handled in a vectorized ECS system? Discuss mask-based execution vs. structural filtering (adding/removing entities from archetypes based on conditions).
3. Consider a world model with 100 million entities (a simulated city). At what point does archetype-based storage fail? What alternative architectures (e.g., sparse grid, spatial hash) should complement ECS?

---

## Lecture 7: Component Serialization and Persistence — Recording the Forge's Output

### Overview

A world model that cannot be saved is ephemeral — a dream that vanishes on exit. Serialization and persistence are the chronicles of the forge: the careful recording of every artifact's properties, every entity's composition, and every system's configuration. This lecture examines the challenges of serializing ECS state and the design of persistence layers.

**The serialization problem.** ECS presents a unique serialization challenge: entities are bare identifiers, components are stored by type in separate pools, and the logical structure of an entity (what components it has) is distributed across multiple data structures. There is no single object to serialize; instead, we must serialize a *topology* — a graph of archetype tables, entity allocators, and component pools.

**Approaches to ECS serialization.**

1. **Entity-centric serialization.** Iterate over all entities, serialize each entity's full component set as a self-contained record. This is simple but redundant (shared components are duplicated) and breaks the archetype model's storage efficiency.
2. **Archetype-centric serialization.** Serialize each archetype's column data continuously. This preserves SoA layout and is efficient for bulk writes, but deserialization must reconstruct the archetype graph.
3. **Component-pool-centric serialization.** Serialize each component type's sparse set independently. This is the most natural fit for ECS internals but requires careful handling of entity ID remapping.

We implement approach (2) in our kernel: a binary serializer that writes archetype tables in column-major order, preceded by a schema header that describes each archetype's component signature and column types.

**Entity ID remapping.** When serializing and deserializing a world, entity IDs may change (especially when merging two worlds or loading a save into an existing world). We design an entity remapping table that is applied during deserialization, updating all `Entity` references in component data (including components that reference other entities, such as `Target { entity: Entity }`).

**Schema evolution.** World models evolve over time. A component that had three fields in version 1 may have four in version 2. We design a schema versioning system that uses optional fields and default values, enabling forward and backward compatibility. The forge's records must be legible to future smiths.

**Incremental and checkpoint persistence.** For large world models, full serialization is expensive. We implement incremental snapshots: a change-tracking layer that records which archetypes have been modified since the last snapshot, enabling delta serialization.

**Serialization formats.** We survey binary formats (custom, FlatBuffers, Cap'n Proto, MessagePack) and text formats (JSON, RON, TOML) for ECS data. We assess each on schema flexibility, serialization speed, deserialization speed, and human readability.

**Persistence backends.** The serialized state must be stored somewhere: local disk, network storage, or a database. We design a persistence interface that abstracts the backend: `trait PersistenceBackend { fn save(&self, world: &World, id: SnapshotId); fn load(&self, id: SnapshotId) -> World; }`.

### Key Concepts

- **Entity-centric vs. archetype-centric serialization.** Different serialization strategies trade off simplicity, efficiency, and fidelity to the ECS model.
- **Entity ID remapping.** A translation table applied during deserialization to handle entity ID shifts.
- **Schema evolution.** Forward and backward compatibility for component schemas across versions.
- **Incremental snapshots.** Delta serialization that captures only modified archetypes.
- **Persistence interface.** An abstracted backend for saving and loading world state.

### Readings

- Gregory, J. *Game Engine Architecture*, § 14.8 (Save-game systems)
- FlatBuffers documentation: "Use Cases" — suitability for real-time serialization
- Flecs serialization API documentation
- Kleppmann, M. *Designing Data-Intensive Applications*, Chapter 3 (Storage and Retrieval) — relevant to serialization format trade-offs

### Discussion Questions

1. Should entity IDs be globally unique across all simulations, or only locally unique within a single world? What are the implications for multiplayer world models and world merging?
2. Schema evolution in ECS is complicated by the fact that components are independently versioned. Should the schema version be per-component, per-archetype, or per-world? What are the trade-offs?
3. Incremental snapshots require change tracking. How should change tracking be implemented in an ECS without introducing overhead on every component write? Discuss dirty flags, hash-based change detection, and copy-on-write.

---

## Lecture 8: Probabilistic Components — Uncertainty in the Forge

### Overview

The dwarves of Norse myth know that the forge is never perfectly predictable. A blade may have hidden flaws; a shield may crack under unexpected force. In AI world modeling, the equivalent uncertainty is fundamental: the world model does not know the exact state of the world but maintains distributions over possible states. This lecture introduces *probabilistic components* — components that store probability distributions rather than deterministic values — and examines how they integrate into the ECS paradigm.

**From deterministic to probabilistic components.** A deterministic `Position` component stores `x: f32, y: f32`. A probabilistic `Position` might store a Gaussian: `mean_x: f32, mean_y: f32, var_x: f32, var_y: f32, cov_xy: f32`. Alternatively, it might store a particle filter: `particles: Vec<(f32, f32, f32)>` where each particle is a `(x, y, weight)` tuple. The choice of representation affects both storage cost and the set of systems that can process it.

**Probabilistic component types.** We design a taxonomy:

- **Gaussian components.** Store mean and covariance. Suitable for state estimation (Kalman filter tracks).
- **Categorical components.** Store a probability distribution over a finite set of values. Suitable for discrete beliefs (e.g., `IsHostile: Prob{true: 0.8, false: 0.2}`).
- **Particle components.** Store a set of weighted samples. Suitable for non-parametric beliefs (e.g., `Position: [(1.2, 3.0, 0.1), (1.5, 2.8, 0.15), ...]`).
- **Interval components.** Store a range `[lo, hi]`. Suitable for bounded uncertainty (e.g., `Health: Interval(50, 80)`).

**Systems over probabilistic components.** A deterministic system operates on exact values. A probabilistic system must define its *propagation rule*: how uncertainty in inputs propagates to outputs. For Gaussian components, linear systems propagate uncertainty via the Kalman update. For particle components, systems apply the transition model to each particle and reweight. We define a `ProbabilisticSystem` trait that extends the `System` trait with uncertainty propagation logic.

**Sampling and realization.** In practice, AI world models often need *samples* — particular realizations drawn from probabilistic components. A system that renders a scene cannot render a Gaussian; it must sample a specific position. We implement a *realization* phase that samples from all probabilistic components, producing a deterministic "possible world" snapshot that downstream systems can operate on.

**Particle filters in ECS.** We implement a full particle filter as an ECS system: the prediction step is a system that applies the transition model to each particle component; the update step is a system that reweights particles based on observations; the resampling step is a system that redraws particles according to weights. The particle filter, when implemented in ECS, naturally parallelizes across entities (each entity's particle set is independent) and benefits from SoA iteration (all position particles are stored contiguously).

**Bayesian component updates.** For categorical components, we implement Bayesian update systems. An observation system sets a `Likelihood` component on relevant entities; an update system multiplies the prior by the likelihood and normalizes. The forge shapes belief as it shapes steel — by repeated, informed strikes.

### Key Concepts

- **Probabilistic component.** A component that stores a probability distribution rather than a point value.
- **Uncertainty propagation.** The rule by which a system transforms input uncertainty into output uncertainty.
- **Realization.** Sampling a deterministic snapshot from probabilistic components for use by non-probabilistic systems.
- **Particle filter in ECS.** Prediction, update, and resampling as ECS systems.
- **Bayesian update.** Multiplying prior beliefs by likelihoods to produce posterior beliefs, implemented as ECS systems.

### Readings

- Thrun, S., Burgard, W., and Fox, D. *Probabilistic Robotics*, Chapters 2–4 (Bayes filters, Kalman filters, particle filters)
- Shoemake, K. "ECS and AI" — GDC 2019 talk on probabilistic state in ECS
- Bishop, C.M. *Pattern Recognition and Machine Learning*, § 2.3 (Gaussian distributions)
- Doucet, A. and Johansen, A.M. "A Tutorial on Particle Filtering and Smoothing" (2009)

### Discussion Questions

1. A particle component storing 100 particles per entity multiplies storage and processing cost by 100×. Under what conditions is this cost justified? When should a world model approximate with Gaussians instead?
2. Realization (sampling) converts a probabilistic component into a deterministic one. But sampling introduces variance. How should a world model handle the fact that two samples produce different downstream behaviors?
3. Can probabilistic components and deterministic components coexist on the same entity? If an entity has a Gaussian `Position` and a deterministic `Weapon`, does the movement system process the Gaussian or the deterministic version? Propose a design pattern for mixed determinism.

---

## Lecture 9: Attention-Weighted Entity Queries — The Forge's Gaze

### Overview

In a traditional ECS, a system queries for all entities with a given set of components and processes them uniformly. But in AI cognition, not all entities are equally important. An agent deciding where to move must attend to nearby threats more than distant ones, to moving objects more than static ones, to novel stimuli more than familiar ones. This lecture introduces *attention-weighted entity queries* — queries that return entities ranked by relevance, allowing AI systems to focus computation on the most salient entities.

**The attention mechanism as a query abstraction.** Inspired by the attention mechanism in transformer architectures, we define a query that returns not just a set of entities but a weighted set: each entity is paired with an *attention score* in [0, 1]. The attention score is computed by an *attention function* that takes the querying entity's state and the candidate entity's state as inputs.

**Attention functions.** We design several attention functions:

- **Proximity attention:** `α(i, j) = exp(-dist(pos_i, pos_j) / σ)`. Nearby entities receive higher attention.
- **Feature similarity attention:** `α(i, j) = softmax(dot(embedding_i, embedding_j))`. Entities with similar features receive higher attention.
- **Novelty attention:** `α(i, j) = novelty(j)`, where novelty decays over repeated exposure.
- **Threat attention:** `α(i, j) = threat_level(j) * proximity_factor(i, j)`. A composite function combining relevance and urgency.

**Implementation in ECS.** An attention-weighted query is a two-phase operation: (1) a component-based pre-filter that selects candidate entities (all entities with relevant components), and (2) a scoring phase that computes attention scores for each candidate and returns a ranked or thresholded result set.

```rust
fn attention_query(
    world: &World,
    source: Entity,
    component_filter: ComponentFilter,
    attention_fn: impl Fn(&Components, &Components) -> f32,
) -> Vec<(Entity, f32)> {
    let candidates = world.query(component_filter);
    let source_components = world.get_all(source);
    let mut scored: Vec<_> = candidates
        .iter()
        .map(|e| (*e, attention_fn(source_components, world.get_all(*e))))
        .collect();
    scored.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
    scored
}
```

**Top-k and thresholding.** Full attention over all entities is O(n) per query. For large worlds, we implement top-k selection (returning only the k highest-attended entities) and thresholding (returning only entities with attention above a cutoff). We use spatial indexing (a spatial hash or AABB tree) to accelerate proximity-based attention queries from O(n) to O(k log n).

**Attention as a component.** Rather than computing attention scores on the fly every frame, we can store the top-k attention scores as a component on the querying entity: `AttentionMemory { targets: [(Entity, f32); K] }`. This component is updated by an attention system that runs at a lower frequency than the main simulation, amortizing the cost of attention computation.

**Multi-head attention queries.** Following the transformer paradigm, we extend single-head attention to *multi-head* attention: multiple independent attention functions, each computing a different aspect of relevance (proximity, threat, novelty, task relevance). The final attention score is a weighted combination of heads. This allows complex AI agents to balance competing priorities.

**Attention-weighted aggregation.** Beyond ranked retrieval, attention scores can be used to compute weighted aggregations: the attention-weighted average position of all enemies, the attention-weighted sum of threat values, the attention-weighted max of urgency signals. These aggregations are used by downstream decision systems.

### Key Concepts

- **Attention-weighted query.** A query that returns entities paired with relevance scores, not just a flat set.
- **Attention function.** A function from (query entity state, candidate entity state) to a scalar attention score.
- **Top-k and thresholding.** Strategies for limiting attention computation to the most relevant entities.
- **Attention as a stored component.** Caching attention results to amortize computation cost.
- **Multi-head attention.** Multiple independent attention functions combined into an aggregate relevance score.

### Readings

- Vaswani, A. et al. "Attention Is All You Need" (2017) — the original transformer attention paper
- Xu, K. et al. "Show, Attend and Tell" (2015) — visual attention in image captioning
- Denil, M. et al. "Learning to Perform Physics Experiments" — attention for task-relevant entity selection
- Stanescu, M. et al. "Evaluating Attention in AI Game Agents" (2016) — attention in game AI contexts

### Discussion Questions

1. Attention-weighted queries are more expensive than flat component queries. Under what conditions is the attention cost justified? When should a system use a simple component query instead?
2. Multi-head attention computes multiple relevance signals. Should these be combined by a fixed formula, or should the aggregation weights be learned? What are the implications for interpretability?
3. Consider an entity that is highly attended by many agents (e.g., a loud, looming threat). Does the attention score need to be bidirectional — the threat also "attends to" the agents? How does this differ from the transformer model of self-attention?

---

## Lecture 10: Reactive Systems and Change Detection — When the Forge Responds

### Overview

Most ECS systems are proactive: they run every frame, scanning for entities and transforming state. But some behaviors are best expressed as reactions: when `Health` drops below 0, despawn the entity; when `Position` enters a trigger zone, fire an event. This lecture examines *reactive systems* — systems that execute in response to changes in component state — and the *change detection* mechanisms that enable them.

**Change detection fundamentals.** At minimum, change detection requires tracking which components have been modified since a given reference point (e.g., the last frame). We implement component-level dirty flags: each component instance has a `modified: bool` flag that is set when the component is written and cleared after reactive systems have processed it. The forge marks each artifact when it is struck; the reactive smith checks for marks before inspecting the work.

**Reactive system lifecycle.** A reactive system is registered with a *trigger condition*: a component change event (add, remove, modify) on a specific component type. When the change is detected, the reactive system is invoked with the changed entity and component data. We define three kinds of triggers:

- **OnAdd:** The component was added to an entity.
- **OnRemove:** The component was removed from an entity.
- **OnModify:** The component's data was changed.

The `OnModify` trigger requires change detection; the others can be detected from structural changes (add/remove are reflected in archetype transitions).

**Implementation strategies for change detection.**

1. **Dirty flags.** Each component column stores a bitset of dirty entries. After a system writes to a component, it marks the corresponding bit. Reactive systems scan the bitset. Cost: O(n) scan, O(1) overhead per write.
2. **Change lists.** Each component type maintains a list of `(entity, old_value, new_value)` changes recorded during the frame. Reactive systems iterate the change list. Cost: O(k) for k changes, O(1) overhead per write.
3. **Generational indices.** Each component instance stores a generation counter. A reactive system compares the generation at the start and end of a frame. Cost: O(n) comparison, O(1) overhead per write.

We implement strategy (1) for our kernel and strategy (2) as an optional optimization for low-frequency changes.

**Observer patterns in ECS.** Beyond change detection, some ECS frameworks (notably Flecs) implement a full *observer* pattern: systems can subscribe to events that fire when a component matching a filter is added, removed, or modified on any entity. We examine Flecs observers and implement a simplified version.

**Event propagation.** A component change on one entity may trigger changes on related entities. For example, modifying `Parent` on entity A should propagate a `ChildAdded` or `ChildRemoved` event on the children. We examine propagation patterns: immediate (synchronous), deferred (queued for the next frame), and cascading (propagated recursively with depth limits).

**Reactive systems for AI world models.** In AI cognition, reactive systems model reflexes and triggered responses. An `OnModify(Damage)` reactive system checks if health has dropped below a threshold and creates a `Stagger` component. An `OnAdd(Detected)` reactive system triggers the AI's threat assessment. The forge's reactions are the world's reflexes.

### Key Concepts

- **Change detection.** Tracking which components have been modified within a time step.
- **Dirty flags.** Per-component-instance boolean flags set on write, scanned by reactive systems.
- **Change lists.** Append-only logs of component changes, enabling O(k) reactive processing.
- **Observer pattern.** Subscription-based notifications for component add/remove/modify events.
- **Trigger types.** OnAdd, OnRemove, OnModify — three kinds of structural and data changes.

### Readings

- Flecs documentation: "Observers" and "Reacting to Changes" chapters
- EnTT documentation: "Signals and Reactive Systems"
- MinedMind, "Reactive ECS Patterns" (blog article)
- Gregory, J. *Game Engine Architecture*, § 14.7.4 (Event systems in ECS)

### Discussion Questions

1. Change detection adds overhead to every component write. In a world model with millions of component writes per frame, is this overhead justified? Under what conditions should change detection be disabled for specific component types?
2. Immediate propagation of reactive events can cause infinite loops (A triggers B, which triggers A). Propose a mechanism to detect and break reactive cycles.
3. Consider a probabilistic component (from Lecture 8). Change detection for a `GaussianPosition` component requires defining "significant change" — a small drift in the mean should not trigger a reactive system, but a large jump should. How should the change threshold be defined?

---

## Lecture 11: Logic-Component-System (LCS) Layers — Symbolic Reasoning in the Forge

### Overview

ECS excels at patterned, scalable computation over thousands of entities. But AI cognition — especially deliberative reasoning, planning, and symbolic inference — operates at a different level of abstraction. This lecture introduces the *Logic-Component-System (LCS)* architecture, an extension of ECS that adds a symbolic reasoning layer on top of the data-oriented ECS foundation. If ECS is the forge's hammers and anvils, LCS is the master smith's plan — the drawings, the specifications, the reasoning that guides the work.

**The motivation for LCS.** Consider an AI agent that must reason: "If the bridge is destroyed and the river is deep, then I must find an alternative route." This reasoning is naturally expressed as logical rules over component state. ECS can represent the state (`BridgeIntact: false`, `RiverDepth: 7.0`), and a system can check these conditions and add an `AlternativeRouteNeeded` component. But as the rule set grows, the system becomes an ad hoc interpreter. LCS formalizes this pattern.

**LCS architecture.** The LCS architecture extends ECS with three layers:

1. **Component Layer (ECS).** The same component data as before — the ground truth state of the world.
2. **Logic Layer.** A set of logical rules expressed in a declarative language. Rules have the form:
   ```
   rule find_alternative_route {
       if not(BridgeIntact) and RiverDepth > 5.0:
           add(AlternativeRouteNeeded)
   }
   ```
   The logic layer reads component data and derives new facts.
3. **System Layer.** ECS systems that read both component data and derived logical facts, and perform actions.

The key insight: the Logic Layer is a *symbolic reasoner* that operates over component data, producing derived facts that are themselves stored as components. This creates a bidirectional flow: ECS → Logic (observations become premises) and Logic → ECS (conclusions become components).

**Forward-chaining and backward-chaining.** The Logic Layer can operate in two modes:

- **Forward-chaining:** Starting from current component data, apply all applicable rules to derive new facts. This is the natural mode for reactive reasoning — "given what I see, what follows?"
- **Backward-chaining:** Starting from a goal, apply rules backward to find premises. This is the natural mode for planning — "to reach the other side, I need an alternative route; what are the conditions?"

We implement a simple forward-chaining rule engine as an ECS system that runs once per frame (or at lower frequency). The engine evaluates all rules against current component data and derives new component data.

**Subsymbolic-symbolic bridge.** The LCS architecture provides a structured bridge between subsymbolic (neural-network-based) AI and symbolic reasoning. Neural systems produce probabilistic components (e.g., `ObjectClassification: Prob{enemy: 0.85, ally: 0.10, civilian: 0.05}`); the Logic Layer consumes these as premises for symbolic rules (e.g., "if classification confidence > 0.7, then add `IdentifiedAs` component"). The forge's heat (subsymbolic computation) shapes the steel; the smith's plan (symbolic reasoning) decides what to forge.

**Rule representation and unification.** Rules in the Logic Layer can use variables and unification, borrowing from Prolog-style logic programming. A rule like "if `Holds(entity, Weapon)` and `Near(entity, Target)`, then add `Threatens(entity, Target)`" uses variables (`entity`, `Target`) that unify against component data during rule evaluation.

**Discrete and continuous logic.** Some rules involve continuous quantities (e.g., `Health < 0.3`). The Logic Layer supports both discrete (Boolean) and continuous (thresholded) predicates. We examine the design space of fuzzy logic integration: rules with confidence weights, partial matches, and soft conclusions.

**Meta-reasoning.** The Logic Layer can contain rules about rules — meta-reasoning. A rule like "if more than 5 rules fired in the last 10 frames, increase the reasoning interval" is a meta-rule that adjusts the Logic Layer's own execution parameters. The smith who can reflect on the forge's throughput is a smith who optimizes the forge itself.

### Key Concepts

- **LCS architecture.** A three-layer extension of ECS that adds a declarative logic layer between components and systems.
- **Forward-chaining.** Rule evaluation mode that derives conclusions from observed facts.
- **Backward-chaining.** Rule evaluation mode that seeks premises for desired conclusions.
- **Subsymbolic-symbolic bridge.** Connecting neural probabilistic outputs to symbolic rule inputs.
- **Unification and variables.** Logic-layer rules that use pattern matching and variable binding.
- **Meta-reasoning.** Rules that govern the behavior of the Logic Layer itself.

### Readings

- Russell, S. and Norvig, P. *Artificial Intelligence: A Modern Approach*, Chapters 7–9 (Logical agents, first-order logic)
- Nilsson, N. *Principles of Artificial Intelligence*, Chapter 5 (Rule-based systems)
- Bridge, D. "ECS and Rule-Based AI" — GDC Vault talk (2018)
- Swift, T. and Warren, D.S. "XSB: Extending the Power of Prolog" — relevant for forward-chaining implementation

### Discussion Questions

1. The Logic Layer derives facts from component data. But what if two rules produce contradictory derived facts? How should conflicts be resolved? Discuss priority ordering, recency, and confidence-weighted resolution.
2. Forward-chaining can produce an explosion of derived facts in a world model with many entities and many rules. Propose a strategy for limiting forward-chaining to relevant subgraphs.
3. Consider an agent with subsymbolic perception (a neural network outputting probabilistic object classifications) and symbolic reasoning (LCS rules about classified objects). Where should the confidence threshold for converting a probabilistic classification into a symbolic fact be set? What are the consequences of setting it too high or too low?

---

## Lecture 12: Forging the Complete AI ECS Kernel — Integration and Synthesis

### Overview

In the final lecture, we assemble the complete ECS kernel built across the semester and reflect on the architectural decisions that define it. We integrate deterministic components, probabilistic components, attention-weighted queries, reactive systems with change detection, and the LCS logic layer into a coherent whole. The forge is complete; the dwarves survey their work.

**Kernel architecture.** We present the final architecture of our ECS kernel:

```
┌─────────────────────────────────────────────────────┐
│                    World                            │
│                                                     │
│  ┌──────────────┐  ┌──────────────────────────────┐ │
│  │ Entity       │  │ Archetype Graph               │ │
│  │ Allocator    │  │ [Position, Velocity] ──► ...  │ │
│  │              │  │ [Position, Velocity, Health]  │ │
│  └──────────────┘  └──────────────────────────────┘ │
│                                                     │
│  ┌──────────────────────────────────────────────────┤
│  │ Component Pools                                   │
│  │ ┌─────────┐ ┌─────────┐ ┌─────────────────────┐ │
│  │ │Position │ │Velocity │ │ProbPosition(Gaussian)│ │ │
│  │ │Pool     │ │Pool     │ │Pool                  │ │ │
│  │ └─────────┘ └─────────┘ └─────────────────────┘ │
│  └──────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────────┤
│  │ Systems Pipeline                                  │
│  │ [PreUpdate] → [LogicLayer] → [Update] → [...]    │
│  │ [ProbRealize] → [Attention] → [Decide] → [Act]   │
│  └──────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────────┤
│  │ Scheduler                                         │
│  │ Dependency DAG → Parallel Execution                │
│  └──────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────────┤
│  │ Command Buffer & Change Detection                 │
│  │ [SpawnQueue] [DespawnQueue] [DirtyFlags]         │
│  └──────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────────┤
│  │ Serialization & Persistence                       │
│  │ [ArchetypeWriter] [SchemaRegistry] [Backend]     │
│  └──────────────────────────────────────────────────┤
└─────────────────────────────────────────────────────┘
```

**AI-specific systems.** We identify the core AI systems in our kernel:

1. **Perception System.** Reads `Position`, `Visibility`, `Occlusion` and writes `PerceivedObjects` and `PerceivedLocations` (probabilistic).
2. **Attention System.** Reads `PerceivedObjects` and the querying agent's state and writes `AttentionMemory`.
3. **Logic Layer System.** Reads component data and attention-weighted observations, applies forward-chaining rules, writes derived component facts.
4. **Planning System.** Reads goals and derived facts, applies backward-chaining to generate action sequences, writes `PlannedAction`.
5. **Action Execution System.** Reads `PlannedAction` and applies it to the physics/movement systems.

Each of these systems is a deterministic (or probabilistic) transformer in the ECS sense, but the pipeline they form — perceive, attend, reason, plan, act — constitutes a cognitive architecture embedded in the ECS framework.

**Probabilistic and deterministic coexistence.** We discuss the integration challenges from Lecture 8: how to handle entities that have both deterministic and probabilistic components, how the realization phase produces deterministic snapshots, and how the logic layer consumes probabilistic premises.

**Attention integration.** We show how attention-weighted queries from Lecture 9 are used by the Perception and Planning systems to limit computation. The attention system runs once per cognitive cycle (e.g., every 10 frames), updating `AttentionMemory`; downstream systems read the cached attention scores, avoiding the O(n) per-frame attention cost.

**Reactive and proactive coexistence.** We discuss how reactive systems (Lecture 10) complement the proactive simulation loop. Some behaviors are frame-driven (physics, animation); others are event-driven (damage triggers stagger, perception triggers threat assessment). The scheduler interleaves proactive and reactive systems, with command buffers resolving structural mutations between phases.

**LCS integration.** We show how the Logic Layer (Lecture 11) is integrated as a system in the pipeline. The Logic Layer reads component data and writes derived facts; it is scheduled after the Perception and Attention systems and before the Planning system. Its output (derived component facts) feeds downstream systems. The LCS layer is not a separate system — it *is* a system, but a system that evaluates logical rules rather than executing imperative code.

**Performance benchmarks.** We benchmark the complete kernel:

- **10K entities, 5 systems:** Baseline performance, demonstrating SoA iteration advantage.
- **100K entities, 20 systems:** Stress test for parallel scheduling and archetype fragmentation.
- **1M entities, 5 systems:** Maximum throughput, demonstrating linear scalability of archetype iteration.
- **Probabilistic components:** 1K entities with 100-particle filters, showing 100× overhead and profiling the resampling step.
- **Attention queries:** 1K agents querying attention over 10K candidate entities, showing top-k optimization effectiveness.

**The dwarf forge, revisited.** We return to the metaphor. Each component is a crafted thing — a blade, a hilt, a pommel, a guard. Each entity is a wielder who assembles the artifacts they need. Each system is a rhythm of the hammers — a deterministic, repeating pattern that transforms the artifacts. The probabilistic components are the forge's uncertainty — the hidden flaw, the unpredictable grain of the steel. The attention system is the smith's discerning eye, focusing on the details that matter. The reactive systems are the forge's safety mechanisms — the bellows that kick in when the fire grows too hot, the anvil that rings when the steel is struck. The LCS logic layer is the master smith's plan — the drawing that guides the work, the reasoning that decides what to forge next. And the ECS kernel itself is the forge: a structure that enables all of these to work together, efficiently and correctly.

The dwarves built the artifacts of the gods. We build the artifacts of intelligence — and the forge that produces them.

### Key Concepts

- **Integrated kernel architecture.** All ECS subsystems working together: entity management, component storage, system pipeline, scheduler, command buffer, change detection, serialization.
- **AI cognitive pipeline in ECS.** Perceive → Attend → Reason → Plan → Act, implemented as a system pipeline.
- **Probabilistic-deterministic coexistence.** Realization phase, mixed-type queries, confidence thresholds.
- **Performance profiling.** Benchmarking the complete kernel and identifying optimization targets.
- **The dwarf forge as architectural metaphor.** Each subsystem corresponds to a part of the forge, each design decision to a craft choice.

### Readings

- All previous course readings — this lecture synthesizes the full semester
- Gregory, J. *Game Engine Architecture*, Chapter 14 (complete ECS overview)
- Flecs documentation: "Quickstart" and "FAQ" — seeing a complete ECS framework in action
- Shannon, C.E. "A Mathematical Theory of Communication" (1948) — the founding insight that data + structure = meaning, relevant to the ECS-world-model correspondence
- Minsky, M. *The Society of Mind* (1986) — agents as assemblages of simpler components, resonant with ECS composition

### Discussion Questions

1. The ECS kernel we built is general-purpose — it can model any world. But AI world models have specific needs (probabilistic state, attention, symbolic reasoning) that go beyond traditional game ECS. Should an AI ECS kernel be a specialized fork of a game ECS, or should it be a general ECS framework with AI-specific libraries layered on top?
2. The cognitive pipeline (Perceive → Attend → Reason → Plan → Act) is linear. But real cognition is not: perception influences action, action influences perception, and reasoning can be interrupted by reactive events. How should the ECS pipeline handle non-linearity and interrupts?
3. As you look back on the kernel, what is the single design decision that, if changed, would have the most cascading impact? Is it the archetype-based storage model, the command-buffer mutation pattern, the probabilistic component design, or something else?

---

## Course Summary and Final Reflections

WM103 has taken you from the barest abstraction — an entity as an integer, a component as a struct, a system as a loop — to a complete ECS kernel augmented with probabilistic reasoning, attention-weighted queries, reactive change detection, and symbolic logic. Along the way, you have encountered the fundamental tension of the pattern: between flexibility and performance, between composition and coherence, between data-driven iteration and goal-driven reasoning.

The dwarves' forge teaches us that great artifacts are not built from a single monolithic piece but from carefully crafted components assembled by wielders with purpose. The forge itself — the ECS kernel — is the infrastructure that makes this compositional power efficient, scalable, and correct. You now carry the smith's knowledge: how to craft the components, how to organize the shelves, how to schedule the hammers, and how to extend the forge for the demands of artificial intelligence.

In the courses that follow — WM204 (Hierarchical World Models), WM205 (Probabilistic Simulation), and WM303 (Multi-Agent Architectures) — you will build on this foundation, creating world models of increasing complexity, fidelity, and intelligence. The forge you have built here will be the foundation on which all of them stand.

---

*"The forge does not choose what to make. The dwarf does. But the forge determines what can be made."*

— Runa University Department of AI World Modeling
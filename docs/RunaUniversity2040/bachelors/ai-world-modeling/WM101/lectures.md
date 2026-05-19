# WM101: Foundations of AI World Modeling
## Yggdrasil's Blueprint

**Runa University 2040 — Bachelor of Science in AI World Modeling**
**Department of Artificial Ontology and Simulated Realities**

---

> *"From the roots of Yggdrasil springs the water of wisdom; from its branches falls the dew of memory upon the world."*
> — *The Prose Edda, adapted*

---

## Course Overview

This course introduces the fundamental theories, architectures, and implementation strategies underlying AI world modeling — the discipline of constructing persistent, internally consistent, causally coherent simulated realities that autonomous agents can inhabit, perceive, and modify. Drawing upon the metaphor of Yggdrasil, the Norse world-tree whose branches and roots interconnect the nine realms, we examine how modern AI systems decompose, represent, and simulate complex worlds at scale.

Students will develop fluency in Entity-Component-System (ECS) architecture, the WYRD Protocol for deterministic state transitions, spatial and temporal representation formalisms, causal dependency graphs, and NPC memory hierarchies. By semester's end, students will understand not merely *how* world models are built, but *why* certain architectural choices imply philosophical commitments about the nature of reality, agency, and knowledge.

**Prerequisites:** CS101 (Computational Foundations), PHIL210 (Ontology and Formal Metaphysics), MATH230 (Graph Theory and Discrete Structures)

**Instructor:** Dr. Eiríkr Völundr, Department of AI World Modeling
**Office Hours:** Torsdagen 1400–1700, Yggdrasil Hall Room 304

---

## Lecture 1: The Architecture of Reality — Yggdrasil's Roots

### 1.0 Prologue: Why World Modeling?

Every intelligence, whether biological or artificial, maintains an internal model of the external world. The platypus models riverbed topologies to locate prey; the orbiting satellite models atmospheric drag to maintain altitude. What distinguishes *AI world modeling* from mere representation is the demand for *operational completeness*: an AI world model must be sufficient to support goal-directed behavior, counterfactual reasoning, and real-time interaction across arbitrarily many agents sharing the same simulated substrate.

The question that animates this course is deceptively simple: **How do we build a world that an AI can reliably inhabit?**

The answer, we shall discover, requires us to unify insights from database theory, physics simulation, cognitive science, graph theory, and philosophy of mind. Yggdrasil — the great ash tree connecting all realms of Norse cosmology — serves as our organizing metaphor. The roots are data structures; the trunk is the simulation loop; the branches are the perceptual interfaces through which agents access the world. Each lecture climbs one branch higher.

### 1.1 The World Modeling Problem, Formalized

Let us define the *world modeling problem* precisely. A world model **W** is a 5-tuple:

```
W = (S, A, T, O, R)
```

Where:
- **S** is the set of possible world states (the *state space*)
- **A** is the set of possible actions available to agents
- **T : S × A → S** is the transition function (the *physics*)
- **O : S × Ag → P(Obs)** is the observation function mapping states and agents to perceived observations
- **R : S × Ag → ℝ** is the reward/salience function determining what "matters" to each agent

This formalization, derived from Markov Decision Processes (MDPs) but augmented with multi-agent observation functions, captures the essential structural commitments of any world model. Notice what it leaves out: affect, qualia, aesthetic experience. A world model is *not* reality; it is a formal scaffolding sufficient for action. The gap between model and reality — the *ontological remainder* — will haunt us throughout the semester, much as the serpent Níðhöggr gnaws eternally at Yggdrasil's roots.

### 1.2 Historical Lineage: From MUDs to Metaverse

World modeling did not begin with AI. The earliest computational world models were Multi-User Dungeons (MUDs) of the late 1970s — text-based environments where shared state was maintained across networked terminals. Roy Trubshaw and Richard Bartle's MUD1 (1978) established the paradigm: a persistent world state, modified by player commands, serialized to all connected clients in real-time.

The evolution from MUDs through graphical MMOs (Ultima Online, 1997; EverQuest, 1999; World of Warcraft, 2004) to modern open-world simulations (No Man's Sky, 2016; Star Citizen, ongoing) illustrates a consistent set of architectural pressures:

1. **Scale**: World models must represent millions of entities simultaneously
2. **Persistence**: World state must survive process restarts and session boundaries
3. **Consistency**: All agents must agree on world state (or disagree in well-defined ways)
4. **Causality**: Events must propagate according to comprehensible rules
5. **Modifiability**: Agents must be able to alter the world, and those alterations must persist

Each of these pressures corresponds to a branch of our course. We begin where Yggdrasil begins: at the roots, with data structures.

### 1.3 The Ontological Turn: What Exists in a Simulated World?

Before we can represent a world, we must decide what *kinds of things* exist within it. This is not merely a programming question — it is a metaphysical one. In philosophy, this is the domain of *ontology*: the study of what exists and how existing things relate to one another.

In traditional object-oriented programming (OOP), the ontology is determined by the class hierarchy. A `Vehicle` class exists; a `Car` class inherits from it; a `Toyota` class inherits from `Car`. The ontology is *rigid* — determined at compile time — and *essentialist* — each entity *is* its class.

The Entity-Component-System (ECS) paradigm, which we study in depth in Lecture 2, offers a fundamentally different ontology: *composition over inheritance*. An entity is not defined by what it *is*, but by what it *has*. A game object might *have* a position, *have* a mesh, and *have* a health value — but these are contingent attributes, not essential natures. This shift from essentialism to compositionalism mirrors a broader movement in metaphysics from Aristotelian substance ontology to trope theory and bundle theory.

**Key Insight**: The choice of data architecture is simultaneously a choice of metaphysics. To choose ECS over OOP is to endorse a compositional ontology over an essentialist one. Architecture *is* philosophy, writ in code.

### 1.4 Readings

*Required:*
- Bartle, R. (2003). *Designing Virtual Worlds*. New Riders. Chapters 1–3.
- Crick, F. (1994). *The Astonishing Hypothesis*. Scribner. (On neural world models.)
- Nystrom, R. (2021). *Game Programming Patterns*. Genever Benning. Chapter on "Component."

*Supplemental:*
- Aristotle, *Categories*. (For contrast with compositional ontology.)
- Borges, J.L. (1941). "The Library of Babel." (On combinatorial state spaces.)
- Wittgenstein, L. (1922). *Tractatus Logico-Philosophicus*, §1–2.1. (On the logical structure of the world.)

### 1.5 Discussion Questions

1. Is it possible to build a world model that does not make metaphysical commitments? Defend your answer with reference to at least two architectural paradigms.
2. Consider the formalization W = (S, A, T, O, R). What important aspects of human world-modeling does this 5-tuple omit? Propose at least two additional components and justify them.
3. The Norse cosmos contains nine distinct realms connected by Yggdrasil. In what sense is a *single* unified world model preferable to *multiple* loosely coupled models? When might decentralization be superior?
4. If an AI agent can only observe the world through the observation function O, can it ever know the "true" state s ∈ S? What are the implications for AI epistemology?

---

## Lecture 2: Entity-Component-System Architecture — Decomposing the World

### 2.0 From Inheritance to Composition

The Entity-Component-System pattern is the load-bearing wall of modern world modeling. It resolves a tension that plagued object-oriented game engines for decades: the *diamond problem* of multiple inheritance, the *fat interface* problem of god-classes, and the *rigidity* problem whereby adding new entity types required modifying existing class hierarchies.

In ECS, we abandon the question "What *is* this entity?" in favor of "What *describes* this entity?" An entity becomes a mere identifier — a 64-bit integer, nothing more. Components become bags of data — structs with no behavior. Systems become stateless functions that iterate over entities possessing specific component combinations.

This tripartite separation yields extraordinary architectural flexibility. Want a new kind of entity? Compose existing components in a novel arrangement. Want a new behavior? Write a system that operates on an existing component. The ontology of the world becomes *open* and *extensible* — exactly the properties a growing simulated reality requires.

### 2.1 Entities: The Void Beneath the World-Tree

An entity in ECS is deliberately, almost provocatively, *nothing*. It is an identifier (often called an `EntityId` or `Eid`), typically a 32- or 64-bit integer, possibly annotated with a generation counter to detect use-after-destruction errors. The entity carries no data, no behavior, no meaning apart from what components attach to it.

This emptiness is a feature, not a bug. It enforces the compositional commitment: entities are *bare particulars* — metaphysical substrata onto which properties are hung. Whether you find this metaphysically satisfying (as trope theorists do) or distressing (as substance dualists might), the engineering advantage is clear: the entity system never needs to change, no matter how the world evolves.

```rust
struct Entity {
    id: u32,
    generation: u32,
}
```

The generation counter implements *tombstone detection*: if an entity is destroyed and its ID later recycled, stale references will fail generational checks rather than silently corrupting world state. This is the computational analogue of the Norse concept of *wyrd* — fate proceeds forward, and what has died cannot be innocently resurrected without consequence.

### 2.2 Components: The Norns' Tapestry

Components are flat data structures — POD (Plain Old Data) types — structs with no virtual methods, no inheritance, no behavior. A `Position` component stores `(x, y, z)`. A `Health` component stores `(current, max)`. A `Renderable` component stores `(mesh_id, material_id)`.

The critical design principle is *separation of concerns at the data level*. Each component should represent one coherent slice of an entity's state. This is not merely "good practice" — it is an expression of *orthogonal persistence*, ensuring that any system can be modified without cascading side-effects through unrelated components.

Memory layout matters. ECS implementations typically employ *archetypes* or *sparse sets* to store components of the same type contiguously, enabling cache-friendly iteration. This is not a mere optimization; it is the difference between a world model that runs at 60Hz for ten thousand entities and one that crawls at 3Hz. The hardware is part of the ontology: a component layout that (conceptually) exists must also (physically) fit in L2 cache.

Component design patterns include:

- **Tag Components**: Zero-size markers (e.g., `PlayerControlled`, `Decorative`) used to filter entities in system queries without storing data.
- **Singleton Components**: Components attached to a single designated entity, representing global state (e.g., `GameTime`, `WeatherState`). These are the ECS analogue of global variables — useful but dangerous.
- **Buffer Components**: Components that maintain a history of recent values (e.g., `PositionHistory`, `DamageLog`), essential for NPC memory systems (Lecture 8).
- **Relationship Components**: Components that reference other entities, encoding graph edges (e.g., `ParentOf { child: Entity }`, `Wielding { weapon: Entity }`). These are the connective tissue of the world graph.

### 2.3 Systems: Heimdall's Watch

Systems are stateless functions that read and write components. A system declares the components it operates on (its *query*), and the ECS runtime provides an iterator over all matching entities. The canonical form:

```
system ApplyGravity(query: Position AND Velocity AND NOT Kinematic) {
    for (pos, vel) in query {
        pos.y += vel.y * dt;
        vel.y -= 9.81 * dt;
    }
}
```

Systems execute in a defined order within each simulation tick. This ordering — the *system schedule* — is itself a directed acyclic graph (DAG), where edges represent dependencies between systems. The WYRD Protocol, which we study in Lecture 3, formalizes these dependency constraints.

Key system design considerations:

1. **Idempotency**: A system that runs twice with the same inputs should produce the same outputs. This is essential for state rollback and determinism testing.
2. **Locality**: Systems should touch the minimum necessary components. A system that blindly iterates all entities when it only needs those with `Health < 0.1` is wasteful and architecturally careless.
3. **Parallelism**: Systems with non-overlapping component access can run concurrently. This is the ECS path to scalability — and the reason why systems must declare their component requirements explicitly.

### 2.4 Archetypes and Sparse Sets: Memory as Fate

The *archetype* model (pioneered by Unity's DOTS and popularized by Flecs and other ECS libraries) groups entities that share the same set of components into contiguous memory blocks. An archetype is identified by the *set* of component types an entity possesses; all entities sharing that set are stored together. This enables O(1) component access and maximally cache-friendly iteration.

The alternative *sparse set* model (used by EnTT and equivalent libraries) stores each component type in its own sparse array, trading some cache locality for O(1) component addition and removal. The choice between archetypes and sparse sets is not merely an implementation detail — it is a commitment about which operations the world model privileges. Archetypes privilege *iteration* (the steady-state physics of the world); sparse sets privilege *mutation* (the dynamic reshaping of entities).

In mythological terms: the archetype model treats the world's structure as relatively static — the fates spin the tapestry and it hangs motionless. The sparse set model treats the world as perpetually in flux — the Norns rewrite their threads moment by moment. The truth, as always, lies in hybrid approaches.

### 2.5 The ECS Algebra

We can formalize ECS operations as an algebra. Let **E** be the set of all entities, **C** be the set of all component types, and **V** be the set of all possible component values. Then:

- **Component Assignment**: `assign : E × C → V` maps an entity and component type to a value (or ⊥ if unassigned)
- **Entity Query**: `query : P(C) → P(E)` returns the set of entities possessing all specified component types
- **System Execution**: `system : (E × V^n) → V^n` transforms component values for matching entities

This algebra is deliberately minimal, yet it captures the full expressive power of ECS. Composition, iteration, and transformation — these three operations are the runes from which entire worlds are inscribed.

### 2.6 Readings

*Required:*
- Nystrom, R. (2021). *Game Programming Patterns*. Chapter on "Component" and "Flyweight."
- Gregory, J. (2018). *Game Engine Architecture*, 3rd ed. CRC Press. Chapter 14: "Gameplay Systems."
- Caini, M. (2020). "ECS Back and Forth." *skypjack.github.io* blog series.

*Supplemental:*
- Aristotle, *Metaphysics*, Book VII. (On substance and accidents — the philosophical ancestor of the ECS debate.)
- Lowe, E.J. (2006). *The Four-Category Ontology*. Oxford University Press. (On the metaphysics of property-bearers.)

### 2.7 Discussion Questions

1. If an entity is "nothing" — merely an identifier — does it exist in any meaningful sense? Is the entity-identifier relationship analogous to the soul-body relationship in dualism?
2. The archetype model privileges iteration speed; the sparse set model privileges mutation speed. In what kinds of simulated worlds would each be preferable? Design a world where the "wrong" choice leads to catastrophic performance failure.
3. Singleton components are the ECS analogue of global variables. Under what circumstances are they justified? Propose a compile-time or runtime mechanism that mitigates their dangers.
4. Consider the "ECS Algebra" formalization. Can you express a system that creates new entities? Destroys entities? What does this reveal about the completeness of the algebra as stated?

---

## Lecture 3: The WYRD Protocol — Deterministic State Transitions

### 3.0 Wyrd and the Inescapable Thread

In Norse mythology, *wyrd* is the concept of fate — not as rigid predetermination, but as the pattern woven by the Norns from the threads of past actions. What has happened determines what can happen; the past constrains the future without fully dictating it. The WYRD Protocol borrows this metaphysical structure to govern state transitions in a world model.

WYRD stands for **W**orld **Y**ield from **R**econciled **D**ependencies. It is a protocol for ensuring that every state transition in a world model is deterministic, reproducible, and causally well-ordered — properties essential for debugging, multiplayer synchronization, replay systems, and the maintenance of agent trust in simulated realities.

### 3.1 The Determinism Imperative

A world model is *deterministic* if the same sequence of inputs always produces the same sequence of outputs. This sounds trivial, but in practice it is remarkably fragile. Sources of non-determinism include:

- **Floating-point arithmetic**: Different hardware, different results; x87 extended precision vs. SSE; FMA instructions reorderable by the compiler.
- **Iteration order**: Hash maps iterate in undefined order across platforms; entity component tables may yield different orderings depending on insertion history.
- **Race conditions**: Concurrent systems accessing shared state without proper synchronization produce indeterminate results.
- **Platform dependencies**: `sizeof(int)`, endianness, alignment requirements, and standard library behaviors vary across compilers and operating systems.
- **Random number generation**: Unless seeded identically and consumed identically, stochastic processes diverge.

The WYRD Protocol addresses each of these. Its core mandate is simple to state and extraordinarily difficult to honor:

> **WYRD Axiom**: For any world model W, any two executions initialized with identical state and driven by identical input sequences MUST produce bit-identical output sequences.

This axiom has profound implications. It prohibits floating-point operations unless their behavior is specified to the bit level. It mandates deterministic iteration over component tables — typically lexicographic order by entity ID. It requires that random number generation be replaced with *pseudorandom* number generation from a seed that is part of the world state. It forbids system-level parallelism unless the system schedule is a fixed DAG and each system's internal iteration order is deterministic.

### 3.2 The System Schedule as DAG

A *system schedule* orders the execution of systems within a simulation tick. In WYRD, the schedule is a Directed Acyclic Graph (DAG) where:

- Nodes are systems
- Edges represent *must-execute-before* dependencies
- The schedule is a topological ordering of this DAG

Dependencies arise from component access patterns. If system A writes to component `Health` and system B reads from `Health`, then A must execute before B within the same tick. The WYRD scheduler:

1. Collects all system declarations and their component access patterns
2. Constructs the dependency DAG
3. Computes a topological ordering
4. Identifies independent subgraphs that may execute concurrently (if the implementation guarantees deterministic merge ordering)

The schedule is determined *at world initialization time*, not at runtime. This is a philosophical commitment: the order of systems is part of the world's *physics*, not a matter of convenience. Changing the system schedule changes the world's behavior, potentially in ways that violate agent expectations.

```rust
struct SystemSchedule {
    systems: Vec<SystemNode>,
    dependency_edges: Vec<(SystemId, SystemId)>,
    // Computed at initialization:
    topological_order: Vec<SystemId>,
    independent_groups: Vec<Vec<SystemId>>,
}
```

### 3.3 Tick Architecture: The Heartbeat of Yggdrasil

A *tick* is the atomic unit of simulation time. During a tick, all systems execute in dependency order, each reading the world state as it existed at the *start* of the tick and writing to a *staging area* that is merged at tick completion. This double-buffering prevents systems within the same tick from observing each other's partial outputs — a critical property for maintaining causal coherence.

The tick lifecycle:

1. **Input Phase**: External inputs (player commands, network messages) are injected into the world state.
2. **Simulation Phase**: The system schedule executes. Each system reads from the *read buffer* and writes to the *write buffer*.
3. **Commit Phase**: The write buffer atomically becomes the new read buffer. The tick is complete.
4. **Observation Phase**: Agents observe the world state and generate percepts. (See Lecture 8 on NPC memory systems.)

The choice between *intra-tick sequential consistency* (systems see earlier systems' writes within the same tick) and *intra-tick snapshot isolation* (systems see only the previous tick's state) is a fateful architectural decision. Sequential consistency enables responsive simulation but complicates deterministic ordering. Snapshot isolation simplifies determinism at the cost of a one-tick latency in system interactions.

WYRD mandates *sequential consistency within a deterministic system schedule*. Snapshot isolation is permitted only for systems that declare no read-after-write dependencies.

### 3.4 State Hashing and Reproducibility

To verify determinism, the WYRD Protocol requires that every world state snapshot be *hashable*. At the end of each tick, a cryptographic hash of the entire world state (or a deterministic sampling thereof) is computed and logged. If two executions of the same world diverge, comparing their state hashes at each tick reveals the precise point of divergence — the *wyrd-break*.

This requirement is expensive but invaluable. In production systems, full state hashing is typically performed only in development builds, with production builds hashing a deterministic subset (e.g., entity positions and health values) as a sanity check.

### 3.5 Rollback and Replay: Unspinning the Thread

Determinism enables *rollback*: restoring the world to any previous state and re-simulating from that point. This is the computational analogue of the Norse concept of *ørlǫg* — the primal law that can be examined but not changed.

Rollback requires:
1. **State serialization**: The ability to capture the complete world state as a byte sequence
2. **Input logging**: A record of all inputs received by the world model, timestamped by tick
3. **State restoration**: The ability to load a serialized state and resume simulation

From these three capabilities flow remarkable powers:
- **Debugging**: When a bug occurs, roll back to before the bug, step forward, and inspect state at each tick.
- **Replay**: Record a sequence of inputs and replay them to produce identical results — the foundation of replay systems in competitive simulation.
- **Multiplayer synchronization**: If two clients deterministically simulate the same input sequence, they produce the same world state without needing to transmit the full state each tick (the *lockstep* model).

### 3.6 Readings

*Required:*
- Gregoric, P. (2010). *Deterministic Multiplayer Game Architecture*. GDC Vault lecture.
- Valve Corporation. (2021). *Source 2 Netcode Architecture*. Internal documentation (excerpts distributed to students).
- Abadi, M., & Lamport, L. (1993). "The Existence of Refinement Mappings." *Proc. LICS*.

*Supplemental:*
- The *Völuspá*, stanzas 20–23. (On the Norns and the weaving of fate.)
- Kahn, G. (1974). "The Semantics of a Simple Language for Parallel Programming." *IFIP Congress*. (On deterministic parallelism.)

### 3.7 Discussion Questions

1. Is strict bit-identical determinism actually necessary, or is probabilistic "close enough" determinism sufficient? In what scenarios would a relaxed determinism guarantee be acceptable?
2. The WYRD Protocol mandates a fixed system schedule determined at initialization time. What are the implications for a world model that wishes to dynamically create new systems? Propose an extension that supports dynamic schedule modification while preserving determinism.
3. State hashing is expensive. Propose a *selective hashing* strategy that preserves the ability to detect divergence while reducing computational overhead. Under what conditions would your strategy produce false negatives?
4. If an NPC agent remembers past states and makes decisions based on those memories, what happens when the world rolls back? Is the NPC's memory also rolled back? What are the implications for agent trust and perceived reality coherence?

---

## Lecture 4: State Persistence and Serialization — Memory Across Ragnarøk

### 4.0 The Problem of Permanence

Every simulated world must survive the cessation of the process that computes it. A power outage, a server migration, a version upgrade — each is a *Ragnarøk*, a destruction of the current computational cosmos. And yet, like the world that emerges anew after the Norse apocalypse, so must the simulated world reconstitute itself from persisted data.

State persistence — the ability to serialize, store, and deserialize the complete world model — is the technology of computational resurrection.

### 4.1 Serialization Formalisms

Serialization is the transformation of an in-memory world state **S** into a byte sequence **B** such that deserialization of **B** produces a state **S'** where **S' ≈ S** under some equivalence relation. The choice of equivalence relation is critical:

- **Bit-identical**: S' must be byte-for-byte identical to S. Required for WYRD determinism verification.
- **Behaviorally equivalent**: S' must produce the same observable behavior as S when simulation resumes. Permits differences in memory layout, entity ordering, or floating-point representation, provided these differences do not affect system execution.
- **Fuzzily equivalent**: S' approximates S. Acceptable for autosave systems where minor state divergence is tolerable.

The WYRD Protocol demands at least behavioral equivalence for all save/load operations and bit-identical equivalence for state hashing.

### 4.2 The Entity Graph and Reference Integrity

ECS worlds form a *directed graph* through relationship components. When `Entity::Weapon` holds a reference to `Entity::Sword`, serialization must preserve this reference across deserialization. This is the *reference integrity* problem.

Complications include:

- **Owned references**: If an entity is destroyed, should its references be nullified? Automatically cascading destroys risk world corruption; never cascading risks dangling references.
- **Cyclical references**: Two entities referencing each other create serialization cycles. Either the serialization format supports reference resolution (like JSON `$ref` dereferencing) or the world model prohibits cycles.
- **Cross-scope references**: A world that subdivides into sub-worlds (e.g., a planet within a star system) may have references that cross scope boundaries. Serializing one scope without the other creates partial-reference problems.

### 4.3 Format Wars: Binary vs. Human-Readable

The serialization format debate is one of the most emotionally charged in world modeling. On one side: binary formats (FlatBuffers, Cap'n Proto) that offer compact size and O(1) random access. On the other: human-readable formats (JSON, YAML, TOML) that support debugging, manual editing, and version migration.

WYRD takes no dogmatic position but observes that different use-cases demand different formats:

- **Network replication**: Binary, schema-based, zero-copy deserialization (FlatBuffers, Cap'n Proto)
- **Save files**: Human-readable (JSON/YAML) with schema versioning for backward compatibility
- **Replay logs**: Compact binary with per-tick deltas rather than full state snapshots
- **State hashing**: Raw byte representation of in-memory state

The key insight: serialization is not a single problem but a *family* of problems, each with different constraints. A mature world model provides multiple serialization backends sharing a common schema.

### 4.4 Schema Evolution: The Semantic Problem

The hardest persistence problem is *schema evolution*: what happens when the world model's data structures change between versions? Adding a new component type is easy — old save files simply lack it. But removing a component, changing a field type, or restructuring a component requires *migration logic*.

The general pattern:

```
version = detect_schema_version(save_data)
save_data = apply_migrations(save_data, from=version, to=CURRENT_VERSION)
world = deserialize(save_data)
```

Migration functions are *semantic transformations* — they cannot be mechanically derived from schema diffs because the meaning of data changes with context. A field named "health" that changes from integer to float is a simple numeric conversion. But a field named "status" that changes from enum {alive, dead} to enum {alive, dying, dead, undead} requires a policy: does "dead" in the old schema map to "dead" or "undead" in the new? The answer depends on game semantics, not data types.

The WYRD Protocol addresses schema evolution through its version-gated entity system. Every entity carries a schema version tag, and the system maintains a registry of migration functions indexed by version pair. When a save file or network message arrives with an older schema version, the system applies the migration chain to bring it current. The key design principle: migrations must be *idempotent* and *lossless*. Applying a migration twice must produce the same result as applying it once, and no information may be discarded — only transformed or extended.

---

### 4.5 Capstone: Building a Persistent World

For the lab component of this module, you will extend your text adventure world from Lecture 3 to support full persistence:

1. Implement JSON and binary serialization for your ECS world state
2. Add a delta-tracking system that records state changes per tick
3. Implement save/load with schema versioning
4. Add incremental save (snapshots every N ticks with delta log between)
5. Test schema migration by adding a new component type to your world and verifying that old save files load correctly

**Key deliverable:** A world that can be saved, closed, reopened, and continued without any loss of state or behavior consistency.

---

## Lecture 5: Causal Graphs — Tracking Cause and Effect in Simulated Worlds

A world model that tracks *what happened* without tracking *why it happened* is a chronicle, not a simulation. This lecture introduces causal graphs — the data structure that enables a world model to reason about cause and effect.

### 5.1 What Is a Causal Graph?

A causal graph is a directed acyclic graph (DAG) where nodes represent events or states and edges represent causal relationships. When a character attacks another and the target loses health, the causal graph records:

```
[Character A attacks] → [Target B health decreases by 15] → [Target B health reaches 0] → [Target B dies]
```

This is not narrative fluff. This is *data*. Each node is an ECS event with a timestamp, source entity, and payload. Each edge is a causal link with a confidence value and an optional delay.

### 5.2 Causal Graph Construction

Building a causal graph from a stream of events requires *causal inference*: determining which events caused which other events. Three approaches:

**Explicit causation**: The game engine explicitly records causal relationships as part of event emission. When A attacks B, the attack event includes a `caused_by` field linking to A's decision. This is the most accurate approach but requires discipline from the engine designer.

**Rule-based inference**: A set of rules maps event patterns to causal links. "If an attack event is followed within 2 ticks by a health decrease event on the same target, the health decrease was caused by the attack." This is less accurate but more general.

**Statistical inference**: Machine learning models detect statistical correlations between events and infer causation from correlation. This is the most flexible but the least reliable approach — correlation is not causation, and statistical methods can produce spurious links.

The Norse Saga Engine uses a hybrid of explicit and rule-based inference. Engine-emitted events carry explicit `caused_by` fields. For events that lack explicit causation, a rule engine applies domain-specific heuristics to infer likely causes.

### 5.3 Causal Graph Queries

Once constructed, a causal graph supports powerful queries:

- **Why did X happen?** → Trace backward from X through causal links to find proximate and root causes.
- **What were the consequences of Y?** → Trace forward from Y through causal links to find all downstream effects.
- **What if Y had not happened?** → Counterfactual reasoning: remove Y and all downstream causal links, then re-evaluate.
- **Is there a causal path from A to B?** → Determine whether A is a cause of B, directly or indirectly.

These queries enable game mechanics that are impossible without causal tracking: NPCs that can explain why events happened (not just that they happened), players who can investigate mysteries by tracing causal chains, and AI directors that can identify the pivotal moments in a story and choose to emphasize or redirect them.

### 5.4 The WYRD Causal Layer

The WYRD Protocol implements causal graphs as a core subsystem. Every significant event in the world — every entity creation, state change, relationship formation, and commitment oath — is recorded as a node in the causal graph. Edges are inferred from explicit causation fields, rule-based inference, and statistical correlation.

The WYRD causal layer provides three query APIs:

- **`why(entity_id, event_type, tick_range)`** — Returns the causal chain leading to the specified event.
- **`consequences(entity_id, event_type, tick_range)`** — Returns all downstream effects of the specified event.
- **`counterfactual(remove_event_id)`** — Returns the hypothetical world state that would result if the specified event had not occurred.

These APIs are available to both the game engine (for NPC decision-making) and the narrative engine (for story generation). An NPC that witnessed a murder can use `why` to determine who committed it. A narrative engine can use `consequences` to trace the ripple effects of a pivotal decision. A player can use `counterfactual` to explore alternate histories.

**Required Reading:**
- Pearl, J. (2009). *Causality: Models, Reasoning, and Inference*. 2nd ed. Cambridge University Press. Chapters 1-3.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Section on "Wyrd as Causal Reasoning."
- Peters, J. et al. (2017). "Elements of Causal Inference." MIT Press. Chapters 1-2.

**Discussion Questions:**
1. Design a causal graph for a multiplayer RPG. What events are nodes? What relationships are edges? How do you handle simultaneous events where causation is ambiguous?
2. Counterfactual reasoning requires "removing" an event and re-simulating. But downstream events may depend on both the removed event and other concurrent events. How do you handle this dependency?
3. Statistical causal inference can produce spurious links. Design a confidence scoring system that distinguishes genuine causation from mere correlation in a world model with thousands of concurrent events.

---

## Lecture 6: NPC Memory and Perception — Agents That Remember and React

A world model without agents is a diorama — static, pretty, and lifeless. This lecture covers NPC (Non-Player Character) memory and perception systems that make simulated agents feel alive.

### 6.1 The NPC Perception Loop

Every NPC in a simulated world follows a perception loop:

1. **Perceive** — Observe the world state through a perception filter (limited range, limited accuracy, limited senses).
2. **Remember** — Store observations in the NPC's personal memory (episodic memory of events, semantic memory of facts, procedural memory of skills).
3. **Reason** — Use stored memories and current observations to form beliefs, intentions, and plans.
4. **Act** — Execute actions based on reasoning, modifying the world state.
5. **Learn** — Update memories based on the outcome of actions. Modify beliefs if expectations were violated.

This loop runs at every tick (or at a rate determined by the NPC's cognitive sophistication — a peasant might reason once per day, a spy once per hour).

### 6.2 Perception Filters

NPC perception is not omniscient. Each NPC has a perception filter that determines what they can observe. Perception filters include:

- **Spatial filter**: An NPC can only observe entities within their perception range. A guard in a tower can see further than a peasant in a field.
- **Sensory filter**: An NPC has specific senses (sight, hearing, smell) with different ranges and accuracies. A blind NPC cannot see. A wolf has a sharper sense of smell than a human.
- **Attention filter**: Even within perception range, an NPC does not observe everything. Attention is directed by goals and emotional state. A hungry NPC notices food more than a sated one.
- **Knowledge filter**: An NPC cannot perceive what they do not understand. A peasant cannot identify a magical artifact that they have never seen before.

The perception filter is crucial for realistic NPC behavior. An NPC that knows everything the player knows is not a character — it is a mirror. An NPC that knows only what they have perceived, remembered, and reasoned about is a character with a genuine inner life.

### 6.3 NPC Memory Architecture

NPC memory follows the same three-tier architecture as the AI OS memory we studied in OS101:

- **Working memory**: What the NPC is currently thinking about. Limited capacity (3-5 items). Updated every tick.
- **Episodic memory**: What the NPC remembers happening. Organized by time and emotional salience. Queried by relevance.
- **Semantic memory**: What the NPC knows as facts. Organized by topic. Queried by association.

But NPC memory has a crucial additional dimension: **imperfect recall**. NPCs do not remember everything they perceived. They forget, misremember, and confabulate. An NPC's episodic memory should include:

- **Emotional salience tagging**: Events with high emotional impact are remembered more vividly and for longer.
- **Decay functions**: Memories fade over time unless reinforced by recall or emotional significance.
- **Distortion functions**: Memories can be distorted by bias, emotion, and social influence. An NPC who dislikes another character may misremember that character's actions as more hostile than they actually were.
- **Confabulation**: When an NPC cannot remember a detail, they may fill in the gap with a plausible-sounding but incorrect detail. This is not a bug — it is a feature that makes NPCs feel more human.

### 6.4 NPC Reasoning

NPC reasoning is typically implemented as a decision tree or utility system:

- **Decision trees**: The NPC follows a branching path of conditions. "If hungry and see food, go to food. If hungry and no food, search for food. If not hungry, do something else."
- **Utility systems**: The NPC evaluates all available actions against a set of weighted criteria. "Eating scores 0.8 on hunger reduction, 0.3 on socializing, 0.1 on exploration. Talking scores 0.1 on hunger reduction, 0.9 on socializing, 0.5 on exploration. The NPC is hungry (hunger weight = 0.7) and lonely (social weight = 0.3). Action scores: Eat = 0.8×0.7 + 0.3×0.3 + 0.1×0 = 0.65. Talk = 0.1×0.7 + 0.9×0.3 + 0.5×0 = 0.34. NPC eats."

Both approaches can be enhanced with LLM-based reasoning for narrative-rich games. The LLM generates plausible NPC responses based on the NPC's memories, personality, and goals, while the decision tree or utility system provides deterministic scaffolding to prevent the LLM from going off-script.

**Required Reading:**
- Wooldridge, M. (2009). *An Introduction to MultiAgent Systems*. 2nd ed. Wiley. Chapters 1-3.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Section on "NPC Perception and Memory."
- Shao, F. et al. (2040). "Generative Agents: Interactive Simulacra of Human Behavior." Stanford Computational Cognitive Science.

**Discussion Questions:**
1. Design a perception filter for an NPC guard in a medieval castle. What does the guard perceive? What does the guard miss? How does perception change depending on time of day, alertness, and weather?
2. An NPC confabulates a memory that never happened. Is this a bug or a feature? Under what circumstances would confabulation improve the player experience? Under what circumstances would it degrade it?
3. Compare decision trees and utility systems for NPC reasoning. What are the advantages and disadvantages of each? When would you use LLM-based reasoning instead?

---

## Lecture 7: Symbolic vs. Neural World Models

This lecture covers the two primary approaches to world modeling: symbolic (explicit rules and representations) and neural (learned implicit models). Understanding both is essential for designing effective world models.

### 7.1 Symbolic World Models

A symbolic world model represents the world using explicit symbols, rules, and logic. Entities are defined by their properties. Relationships are defined by explicit predicates. State changes are defined by deterministic rules. Everything is inspectable, debuggable, and explainable.

Advantages:
- **Interpretability**: Every state change can be traced to a specific rule.
- **Verifiability**: The system can be formally verified to satisfy safety properties.
- **Determinism**: The same inputs always produce the same outputs.
- **Modularity**: Rules can be added, removed, or modified independently.

Disadvantages:
- **Brittleness**: Rules that are correct for common cases may fail for edge cases.
- **Scalability**: The number of rules grows combinatorially with the complexity of the world.
- **Inexpressiveness**: Some aspects of reality (appearance, emotion, nuance) are difficult to capture in symbolic form.

### 7.2 Neural World Models

A neural world model represents the world using learned weights in a neural network. The model learns to predict state transitions from data, without explicit rules. Everything is implicit in the weights — flexible, adaptive, but opaque.

Advantages:
- **Flexibility**: The model can learn arbitrary state transitions from data.
- **Scalability**: Learning scales with data, not with the number of rules.
- **Expressiveness**: Neural models can capture nuanced patterns that are difficult to express symbolically.

Disadvantages:
- **Opacity**: The model's decision process is not inspectable.
- **Unreliability**: The model may produce plausible-looking but incorrect predictions.
- **Data dependence**: The model is only as good as its training data.

### 7.3 Hybrid Models: The Best of Both Worlds

The Norse Saga Engine uses a hybrid approach: symbolic ECS for deterministic world state (entity positions, inventory, health values) and neural models for generative content (NPC dialogue, narrative descriptions, creative problem-solving). The symbolic layer provides verifiable ground truth. The neural layer provides flexible generation. The two layers communicate through the WYRD Protocol, which ensures that neural outputs are consistent with symbolic constraints.

This hybrid approach is sometimes called "neuro-symbolic AI" in the literature. The key insight is that symbolic and neural models are not alternatives — they are complementary. Symbolic models provide the skeleton of the world (the rules, the entities, the state). Neural models provide the flesh (the dialogue, the descriptions, the creative responses). Together, they produce a world that is both verifiable and vivid.

### 7.4 When to Use Symbolic vs. Neural

Use symbolic models when:
- The rules of the world are well-defined and important to enforce (physics, combat, economics).
- Interpretability and debuggability are critical (game balance, safety, fairness).
- The world is relatively simple and the number of rules is manageable.

Use neural models when:
- The rules of the world are complex, nuanced, or difficult to specify explicitly (social interactions, creative writing, emotional responses).
- Flexibility and adaptability are more important than determinism.
- The world is complex enough that enumerating all rules would be impractical.

Use hybrid models when:
- The world has both well-defined and nuanced aspects.
- You need both verifiable ground truth and flexible generation.
- You want to combine the strengths of both approaches while mitigating their weaknesses.

**Required Reading:**
- Garcez, A. d'Avila et al. (2019). "Neurosymbolic AI: The 3rd Wave." arXiv:2012.05876.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Section on "Neuro-symbolic Integration in the Saga Engine."
- Ha, D. & Schmidhuber, J. (2018). "World Models." arXiv:1803.10122.

**Discussion Questions:**
1. Design a hybrid world model for a detective game. What aspects would you model symbolically? What aspects would you model neurally? How would the two layers communicate?
2. Neural world models can produce plausible-looking but incorrect predictions. In a game context, is this a problem or a feature? How would you handle a neural prediction that contradicts a symbolic rule?
3. The hybrid approach requires maintaining two systems that must stay consistent. What are the failure modes of hybrid consistency? How would you detect and resolve inconsistencies between the symbolic and neural layers?

---

## Lecture 8: The Norse Saga Engine — A Case Study in Integrated World Modeling

This lecture provides a detailed examination of the Norse Saga Engine as a case study of an integrated world modeling system.

### 8.1 Architecture Overview

The Norse Saga Engine is built on four pillars:

1. **ECS Core**: The Entity-Component-System substrate that holds all world state.
2. **WYRD Protocol**: The event and causal tracking system that records everything that happens and why.
3. **Myth Engine**: The narrative layer that generates stories, manages character arcs, and ensures narrative coherence.
4. **Norns**: The three fate-weavers — Urðr (past), Verðandi (present), Skuld (future) — that manage temporal reasoning, real-time processing, and prediction.

### 8.2 Entity Canonization in Practice

The Saga Engine implements Entity Canonization as described in OS101. When the narrative engine generates a new entity name ("A new Bondmaid named Sigrid enters the hall"), the Canonization Daemon automatically creates a Sigrid entity in the ECS, populates it with attributes mentioned or inferred, and registers it in the WYRD causal graph.

The canonical entity includes:
- **Identity**: Name, type, and unique ID.
- **Attributes**: Physical, mental, and social attributes derived from the narrative.
- **Relationships**: Connections to other entities, created and tracked by the WYRD system.
- **Memory**: A personal memory store (episodic, semantic, procedural) that accumulates as the entity experiences events.
- **Commitments**: Oaths, promises, and obligations recorded in the Wyrd commitment web.

### 8.3 Stochastic Narrative

The Saga Engine uses a Stochastic Narrative Engine analogous to the Stochastic Personality Engine in OS101. Instead of sampling personality principles, the Narrative Engine samples from a pool of narrative possibilities: plot arcs, character developments, thematic elements, and dramatic events. Each tick, the engine samples from these pools (weighted by story state and character dispositions) to determine what happens next.

This produces bounded narrative variability — the story is coherent (it follows from character and history) but not predictable (specific events are sampled from weighted distributions). The result is a story that feels alive, not scripted.

### 8.4 Commitment Web in Practice

The Wyrd Protocol ensures narrative consistency by tracking all commitments made by all entities. When a character swears an oath, the commitment is recorded in the web. When a character acts in a way that would violate the oath, the verification kernel flags the violation and generates consequences.

This produces stories where oaths matter — a character who swears to protect a village and then abandons it faces narrative consequences (shame, loss of reputation, divine punishment). Without the commitment web, oaths would be just words — narrative flavor with no structural force.

### 8.5 Multi-Clock Temporal Reasoning

The Saga Engine operates on eight temporal scales (as introduced in OS101), from the immediate (1-3 turn rune draws) to the eternal (permanent identity commitments). Each scale has its own memory buffer, retention policy, and injection mechanism. The Norns coordinate temporal reasoning across these scales — Urðr manages past events, Verðandi manages present events, and Skuld manages future predictions.

**Required Reading:**
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapters 4-6 (full case study).
- All previous WM101 readings, reviewed for synthesis.

**Discussion Questions:**
1. The Saga Engine uses four pillars (ECS, WYRD, Myth, Norns). Design a world model for a different genre (modern thriller, space exploration, slice-of-life) that uses the same four pillars. What changes? What stays the same?
2. Stochastic narrative produces bounded variability. But what happens when the stochastic sampling produces an event that contradicts the commitment web? Should the commitment web override the stochastic sampling, or should the stochastic sampling be allowed to produce events that challenge commitments?
3. The eight temporal scales of the Saga Engine range from 1-3 turns to permanent. Which scales are most important for narrative feel? Which could be simplified or merged without significant loss?

---

## Lecture 9: Deterministic vs. Probabilistic World Simulation

Should a world model be deterministic (the same initial conditions always produce the same outcome) or probabilistic (the same initial conditions can produce different outcomes)? This lecture examines the trade-offs.

### 9.1 Deterministic Simulation

In a deterministic world model, given the same initial state and the same sequence of actions, the outcome is always the same. This is the model used by most physics engines, turn-based strategy games, and simulation games that prioritize fair competition (e.g., competitive RTS games where replay integrity is essential).

Advantages:
- **Reproducibility**: Bugs can be reproduced exactly by replaying the same sequence of actions.
- **Fairness**: No randomness means no "luck" — outcomes depend purely on skill and strategy.
- **Auditability**: The causal chain is deterministic and can be traced precisely.

Disadvantages:
- **Predictability**: Once a player learns the optimal strategy, the game becomes trivially solvable.
- **Brittleness**: Small changes in initial conditions can produce large changes in outcome (chaos theory).
- **Monotony**: Deterministic worlds can feel mechanical and lifeless.

### 9.2 Probabilistic Simulation

In a probabilistic world model, the same initial conditions can produce different outcomes due to randomness. This is the model used by most RPGs (random encounters, loot drops), roguelikes (procedural generation), and narrative games (branching dialogue with weighted outcomes).

Advantages:
- **Variability**: No two playthroughs are identical, increasing replay value.
- **Surprise**: Unexpected outcomes create memorable moments.
- **Realism**: The real world is not deterministic — randomness models uncertainty.

Disadvantages:
- **Unfairness**: Players may feel that outcomes depend on luck rather than skill.
- **Debugging difficulty**: Bugs triggered by a specific random seed are difficult to reproduce.
- **Narrative inconsistency**: Randomness can produce outcomes that violate narrative logic (a peasant defeating a dragon through random chance).

### 9.3 The Deterministic Core, Probabilistic Surface Pattern

The Norse Saga Engine uses a hybrid approach called "deterministic core, probabilistic surface":
- **Core mechanics** (physics, combat resolution, resource consumption) are deterministic. The same inputs always produce the same outputs.
- **Surface mechanics** (narrative events, NPC behavior, loot drops) are probabilistic. The same situation can produce different outcomes based on weighted random sampling.

This hybrid preserves the advantages of both approaches: core mechanics are reproducible, fair, and auditable, while surface mechanics are variable, surprising, and realistic. The WYRD Protocol tracks both deterministic causes and probabilistic contributions, enabling causal reasoning that accounts for randomness.

**Required Reading:**
- Togelius, J. et al. (2011). "Search-Based Procedural Content Generation." IEEE Transactions on Computational Intelligence and AI in Games.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Section on "Deterministic Core, Probabilistic Surface."

**Discussion Questions:**
1. Design a deterministic core and probabilistic surface for a social simulation game. What mechanics are deterministic? What are probabilistic? How do you handle the boundary between core and surface?
2. A player complains that a random event ruined their carefully planned strategy. Is this a design problem, a communication problem, or an inevitable feature of probabilistic simulation? How do you address it?
3. Some games use "pseudorandom" number generators that are deterministic given a seed. This means "random" outcomes are reproducible if you know the seed. Is this the best of both worlds, or does it introduce new problems?

---

## Lecture 10: Spatial and Temporal Representation in World Models

How does a world model represent space and time? This lecture covers coordinate systems, room-based models, and temporal modeling.

### 10.1 Spatial Representation

Three primary approaches to spatial representation in world models:

**Coordinate-based**: Continuous or discrete coordinates. Used by physics engines, 3D games, and simulations where precise spatial relationships matter. Entities have (x, y, z) positions and collisions are detected by proximity.

**Room-based**: The world is divided into named rooms connected by exits. Used by text adventures, MUDs, and many RPGs. Entities are in rooms, not at coordinates. Movement is between rooms, not within them. Classic format: "You are in a dark room. Exits: north, east."

**Graph-based**: The world is represented as a graph where nodes are locations and edges are connections. Used by games with complex travel networks (space games, strategy games). More flexible than room-based but less intuitive than coordinate-based.

The Norse Saga Engine uses a hybrid: coordinate-based for physical spaces (an arena, a battlefield) and room-based for abstract spaces (a kingdom, a story region). The representation chosen for a given space depends on the level of detail required by the narrative.

### 10.2 Temporal Representation

Three primary approaches to temporal representation:

**Tick-based**: Time advances in discrete steps (ticks). Each tick, all systems process once. Simple, deterministic, and easy to reason about. Used by most turn-based games and simulations.

**Real-time**: Time advances continuously. Systems process at different rates. Used by most action games and real-time simulations. More complex but more natural-feeling.

**Narrative time**: Time advances at the pace of the narrative. During a conversation, time may advance slowly. During travel, time may advance quickly. Used by narrative games where story pacing is more important than real-time simulation. This is the approach used by the Norse Saga Engine.

Narrative time is the most challenging to implement correctly because it requires coordinating the temporal scales of multiple systems. A conversation that takes 10 minutes of real time might represent 5 minutes of game time. A journey that takes 2 seconds of real time might represent 3 days of game time. The engine must track both real time and game time, and systems that depend on time (NPC schedules, weather, aging) must use game time rather than real time.

### 10.3 The Multi-Clock Temporal Architecture

As introduced in OS101, the Saga Engine uses eight temporal scales, each with its own clock rate and memory policy. These scales range from the immediate (1-3 turn rune draws, advancing every tick) to the eternal (permanent identity commitments, advancing only when explicitly modified).

The multi-clock architecture solves a fundamental problem: different aspects of the world advance at different rates. A conversation happens in seconds. A journey takes hours. A war lasts months. A lineage spans generations. A single-clock model would force all temporal scales into one frame rate, losing the nuance of the slower scales or the granularity of the faster scales. The multi-clock architecture lets each scale advance at its own rate.

**Required Reading:**
- Turchin, V. (1977). *The Phenomenon of Science: A Cybernetic Approach to Human Evolution*. Columbia University Press. Chapter on "Metasystem Transitions."
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Section on "Multi-Clock Memory."

**Discussion Questions:**
1. Design a spatial representation for a game that includes both indoor environments (rooms, corridors) and outdoor environments (forests, oceans). What representation does each environment use? How do you handle transitions between representations?
2. Narrative time creates a problem for NPC schedules: if game time advances rapidly during travel, NPCs should age, eat, sleep, and change their routines accordingly. Design a system that keeps NPC behavior consistent with game time, even when game time advances at different rates.
3. The multi-clock architecture uses eight scales. Could you reduce this to three or four without significant loss? What scales would you merge?

---

## Lecture 11: Reality-Virtual Bridging — When Worlds Collide

The final technical lecture addresses an emerging challenge in world modeling: the boundary between the simulated world and the real world. As AI agents increasingly operate in real-world contexts (personal assistants, autonomous vehicles, medical diagnosis), the distinction between "world model" and "reality model" becomes blurred.

### 11.1 The Grounding Problem

A world model that represents a fictional world (a game, a simulation) can define its own rules. But a world model that represents the real world must ground its representations in real-world data. This is the grounding problem: how does the model know that its internal representations correspond to real-world entities?

Grounding is trivial for simple cases (the model's "cat" representation maps to cats in the real world) and enormously difficult for complex cases (the model's "justice" representation maps to... what, exactly?). The grounding problem is especially acute for world models that operate in real-world contexts, where errors can have real consequences.

### 11.2 Virtual-to-Real and Real-to-Virtual Bridges

A reality-virtual bridge is a mechanism that connects representations in the world model to real-world entities. Two types:

**Virtual-to-Real**: An entity in the world model maps to a real-world entity. The model's representation of "the user's car" maps to an actual car with an actual VIN and actual maintenance records. Changes in the model may trigger actions in the real world (e.g., "schedule an oil change").

**Real-to-Virtual**: A real-world event maps to an entity in the world model. The user's calendar event "dentist appointment at 3 PM" creates a corresponding entity in the model that can be reasoned about, planned around, and used to make predictions.

Both types of bridge are necessary for agents that operate in the real world. An AI personal assistant needs virtual-to-real bridges (to take action on the user's behalf) and real-to-virtual bridges (to update its world model based on real-world events).

### 11.3 Safety Considerations

When world models operate in real-world contexts, safety becomes paramount. A mistake in a fictional world model means a bug in a game. A mistake in a real-world model means a missed appointment, a wrong medication, or a car accident.

Safety mechanisms for reality-virtual bridges include:
- **Confidence thresholds**: The model only acts on predictions above a confidence threshold.
- **Confirmation loops**: The model asks the user to confirm before taking real-world actions.
- **Rollback capabilities**: Actions can be undone if they prove incorrect.
- **Bounded authority**: The model's ability to take real-world actions is limited by explicit permissions.

**Required Reading:**
- Bostrom, N. (2014). *Superintelligence: Paths, Dangers, Strategies*. Oxford University Press. Chapter 8: "Safety."
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Section on "Grounding and Bridging."
- Amodei, D. et al. (2016). "Concrete Problems in AI Safety." arXiv:1606.06565.

**Discussion Questions:**
1. Design a reality-virtual bridge for an AI personal assistant. What entities in the model map to real-world entities? What actions can the model take on the user's behalf? What are the confidence thresholds for each action?
2. A world model makes an incorrect prediction about the real world (e.g., it predicts rain, but it's sunny). How should the model update its representations to incorporate this error? What are the implications for future predictions?
3. Consider the ethical implications of an AI agent that can take real-world actions on a user's behalf. What are the minimum safety mechanisms? What are the failure modes that keep researchers up at night?

---

## Lecture 12: Capstone — Building a Minimal World Model

For your capstone project, you will build a complete minimal world model for a text adventure game.

**Requirements:**

1. **ECS Core**: Implement entities, components, and systems using the pattern from Lecture 2. Minimum entities: player, 3 NPCs, 5 locations. Minimum components: position, health, inventory, personality, memory. Minimum systems: movement, combat, dialogue, memory.

2. **WYRD Protocol**: Implement state persistence with tick-based advancement and delta tracking. Save/load must work. Schema versioning must handle at least one migration.

3. **Causal Graph**: Implement basic causal tracking. Events must record their cause. The system must answer "why did X happen?" queries.

4. **NPC Memory**: Implement at least working memory and episodic memory for NPCs. NPC memory must include emotional salience tagging and decay.

5. **Temporal Reasoning**: Implement at least two temporal scales (scene-level and story-level). Scene-level memories persist for the current scene. Story-level memories persist across scenes.

**Deliverables:**
- Working code for the world model (Python or Rust).
- A design document specifying your ECS schema, WYRD implementation, causal graph structure, and NPC memory architecture.
- A 2-page reflection on what you learned about the challenges of building a world model and how your design addresses those challenges.

**Evaluation Criteria:**
- Correctness: Does the world model maintain consistent state?
- Persistence: Can the world be saved, closed, and reopened?
- Causality: Can the causal graph answer "why" questions?
- Memory: Do NPCs remember and react based on their experiences?
- Temporal: Do memories decay and persist appropriately across temporal scales?

---

*"Yggdrasil stands, ever green, its roots in three waters. So too must a world model stand, its roots in data, its trunk in logic, its canopy in narrative. The blueprint is drawn. Now build."*

— Professor Brynja Ásatrúardóttir, WM101 Course Conclusion
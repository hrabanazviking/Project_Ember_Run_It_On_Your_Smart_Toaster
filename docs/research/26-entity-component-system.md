# 26 — Entity-Component-System Architectures for AI Worlds

**Category:** World Modeling
**Runa relevance:** WYRD bridge (the WYRD project itself uses ECS), `core/world/` (consumer side), Skuld (entity-shaped tasks)
**Status:** Research synthesis. Particularly relevant because WYRD-Protocol (Volmarr's separate project) is ECS-based per memory.
**Last touched:** 2026-05-17

---

## 1. Core idea

**ECS** stands for **Entity-Component-System**. It's a design pattern from the games industry — popularised by Adam Martin's 2007 articles and Bitsquid's engine — for representing simulated worlds in a way that decouples *what a thing is* (composition of components) from *what is done with it* (systems that iterate over components). An **entity** is an ID. A **component** is plain data attached to an entity (Position, Health, Inventory, Dialogue). A **system** is a function that operates on entities having a particular component combination ("for every entity with Position + Velocity, update Position by Velocity").

The pattern is the opposite of inheritance-heavy OOP for simulated worlds. Instead of `class Goblin extends Monster extends Creature extends Entity`, you have an entity with `{Position, Health, AI("goblin_aggressive"), Inventory, Sprite}`. Want to make the goblin a shopkeeper? Add a `Shop` component. Want him to be friendly? Swap the AI component. Composition over inheritance, taken seriously.

For Runa, ECS matters because **WYRD-Protocol** (Volmarr's separate world-model project that Runa connects to via the WYRD bridge) is built on ECS, per the project memory. The WYRD bridge talks to a system whose internal vocabulary is entities and components. Understanding ECS shapes how Runa's bridge code structures queries, mutations, and event subscriptions.

## 2. Technical depth

**Core abstractions:**

```
Entity:    just a stable ID (often a 32-bit or 64-bit integer)
Component: structured data attached to an entity
System:    a function that processes entities with a specific
           combination of components

World:     the container — manages entity lifecycle and component storage
```

**Storage layouts:**

- **Sparse set / archetype-based** — entities are grouped by their exact component combination ("archetype"). Iterating is cache-friendly. Bevy ECS, EnTT (modern modes), Unity DOTS.
- **Array-of-Structs** vs **Struct-of-Arrays** — SoA layouts (each component type in its own contiguous array) are the basis for the cache-locality wins ECS systems are famous for.
- **Sparse maps** — simpler, slower for iteration, faster for random access. Useful for components attached to few entities.

**System scheduling:**

- Systems declare their *read* and *write* component dependencies.
- The scheduler runs systems in topological order, parallelising where reads and writes don't conflict.
- Bevy famously does this *automatically* — you write systems with typed parameters and the framework infers the schedule.

**Querying:**

```rust
// Bevy-flavoured pseudocode
fn update_movement(
    mut query: Query<(&mut Position, &Velocity), With<Active>>,
    time: Res<Time>,
) {
    for (mut pos, vel) in query.iter_mut() {
        pos.0 += vel.0 * time.delta_seconds();
    }
}
```

Query says: give me every entity with `Position` (mutable) and `Velocity` (read-only), and which has the `Active` marker. The system processes only those.

**Events.** ECS frameworks pair naturally with event systems — a system reads input events, mutates components, possibly emits output events for other systems to consume.

**Persistence.** ECS worlds serialise component-by-component. Versioning components is manageable; versioning whole inherited class hierarchies is not.

**Notable ECS implementations:**

- **Unity DOTS / ECS** (Unity Technologies, mature 2018+) — major commercial use. Hugely influential.
- **Bevy ECS** (Bevy Engine, Rust, 2020+) — open-source, modern, beautiful API. Reference implementation for many modern ideas.
- **EnTT** (Michele Caini, C++, 2017+) — header-only, used by Mojang in Minecraft Bedrock.
- **flecs** (Sander Mertens, C, 2018+) — minimal-dependency, embeddable.
- **specs** (Rust, predecessor to Bevy ECS) — historical reference.
- **EntityX** (Alec Thomas, C++) — early modern ECS for games.
- **Apoapsis / Esper** — Python ECS libraries (less mature; Python's overhead makes ECS speed wins smaller).
- **Tarn Adams's home-grown ECS in Dwarf Fortress** — not academically described but a long-running existence proof for ECS at simulation scale.

**ECS as agent-world representation:**

- Generative Agents (Park et al., 2023, see [[02-episodic-memory-architectures]]) used something close to ECS for the agents' positional and social state.
- Multi-agent simulation frameworks (NetLogo, Mesa) use similar patterns.
- For Runa-as-citizen-of-a-WYRD-world, the entities of interest include Volmarr, Runa herself, projects in his ecosystem, files, conversations, tasks.

## 3. Key works

- **Martin, A.** "Entity Systems are the future of MMOG development." 2007 blog series. The articles that named and popularised the pattern.
- **Bitsquid blog** (Niklas Frykholm, ~2014) — "Managing Decoupling Part 4: The ID Lookup Table." Influential engineering pieces.
- **Mertens, S.** "Building an ECS." flecs.dev/articles. Modern, deeply detailed.
- **Caini, M. (skypjack).** EnTT documentation — github.com/skypjack/entt.
- **Bevy book** — bevyengine.org/learn/book/. Excellent free reference.
- **Unity DOTS documentation** — docs.unity3d.com.
- **Adam Smith and Mike Mateas's work on agent-based narrative simulation** — relevant academic precedent for "ECS as a narrative-world substrate."

## 4. Empirical results

ECS performance characteristics are well-documented:

- Cache-friendly iteration: 5-50× faster than naive OOP for simulation loops that touch many entities. The single most-cited benefit.
- Memory density: components packed tightly; far less overhead than per-object vtables and references.
- Parallel scheduling: automatic for read-only systems; manual for conflicting writes. Bevy's scheduler is the modern state-of-the-art.
- Complexity: ECS code looks unfamiliar at first — "where is the Player class?" — but maintainability improves substantially as systems grow. The Bitsquid and Unity articles document this transition.

For AI agents specifically:

- Composability shines: adding a new behaviour (component) doesn't ripple through hierarchies. Adding an `EmotionalState` component to entities that had none doesn't require touching any other code; systems that care opt in.
- Queries are natural for agent perception: "what entities are in my vision cone?" → query with `Position` + filter.

The trade-offs:

- ECS is a paradigm shift; teams accustomed to OOP take time to adjust.
- Some inherently-graph-shaped data (parent-child relationships, social graphs) fits ECS awkwardly. Hybrid solutions are common.
- Debugging is different — there's no "this object" to step into; you debug systems and their queries.

## 5. Applicability to Runa

For **the WYRD bridge** (`core/world/`):

- WYRD-Protocol uses ECS (per project memory). The bridge speaks ECS-flavoured queries and mutations to WYRD; locally it caches a lightweight snapshot.
- The bridge's query API should mirror ECS-style queries: "entities with components X + Y filtered by Z". A flat key-value store is the wrong shape.
- Bridge code should expose typed query helpers that map to WYRD's component types. Avoid leaking string-typed queries into Runa's `core/` business code.

For **Skuld (task ledger)**:

- Tasks can be thought of as entities. Components: `TaskGoal`, `TaskOwner`, `TaskStatus`, `TaskDependencies`, `TaskDeadline`, `TaskNotes`. Querying "all active tasks owned by Huginn with deadline < tomorrow" is ECS-natural.
- This is conceptual framing; the implementation may still be SQLite tables. The ECS framing helps think clearly about decomposition.

For **Hirð / Heimdallr (watch)**:

- Heimdallr observes the entity-shaped world (Volmarr's projects, files, conversations). ECS-style queries against the WYRD bridge give Heimdallr its perception layer.

For **Eldhugi**:

- Eldhugi's emotional state could be modelled as components attached to "relationship entities" (one per significant person/project Runa cares about) rather than as a single global state object. ECS framing.

What to avoid:

- Don't build a *new* ECS framework. If a serious ECS need arises, the bridge should use whatever ECS is in WYRD; locally, plain dicts and dataclasses are fine until profiling says otherwise.
- Don't model everything as entities. Some Runa state is naturally singular (her identity, the active configuration). Use ECS where it gives clarity; not as ideology.
- Don't confuse ECS with the data store. The data store is SQLite; ECS is the *logical model* you query through.

## 6. Open questions

- **ECS at distributed scale.** ECS evolved in single-process games. When Runa's WYRD-world spans multiple machines, the entity-locality and query-routing problems are open.
- **ECS + LLM.** Having an LLM reason over ECS-shaped state (versus, say, prose summaries) is interesting. Component types are a natural ontology. Underexplored.
- **Time-travel queries.** ECS state changes over time; rewinding or branching the world is sometimes asked for. Some ECS frameworks (Bevy with snapshots) support it; the patterns are still emerging.
- **Schema migration.** When component definitions change, existing entities need migration. Standard solutions exist; integration with event-sourcing ([[22-event-sourcing-cqrs]]) is an interesting frontier.

## 7. References (curated)

- t-machine.org — Adam Martin's original "entity systems are the future" articles.
- bevyengine.org/learn/book/ — Bevy book.
- skypjack.github.io — EnTT author's design blog.
- flecs.dev/articles — Sander Mertens's deep ECS articles.
- docs.unity3d.com/Packages/com.unity.entities — Unity ECS.
- github.com/SanderMertens/ecs-faq — ECS FAQ collection.
- Companion docs: [[25-world-models-rl]] (the learned-model alternative), [[27-belief-states-pomdp]] (handling uncertainty), [[22-event-sourcing-cqrs]] (the persistence pattern that pairs).

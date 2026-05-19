# WM107 — Deterministic State Simulation
## The Threads of the Norns

**University of Yggdrasil — Class of 2044**
**Bachelor of Science in AI World Modeling Systems Design**
**4 Credits** | Year One, Semester Two

**Instructor:** Dr. Sigrid Vølverdottir, Professor of Computational Determinism
**Office:** Heimdall Hall 312 | **Hours:** Tuesdays 14:00–16:00, or by appointment at the Well

---

## Course Description

In a world of stochastic agents, deterministic simulation is a superpower. This course teaches students to build world simulations where state transitions are fully reproducible given the same inputs — essential for verification, debugging, and governance of AI world models. Topics include: seeded random number generation for reproducible worlds, causal determinism in event systems, and the art of making stochastic processes predictable without sacrificing emergent behavior. Students build a deterministic city simulation that can be re-run identically from any seed state.

The Norns spin the threads of fate — Urd lays the thread of what was, Verðandi pulls it through the present, and Skuld measures what must become. In this course, we learn to spin our own threads: deterministic sequences of world state that unfold inevitably from a single seed, yet produce the rich, emergent behavior we associate with living worlds. The paradox of deterministic simulation is that choice and necessity are not opposites. The Norns prove this every day.

---

## Lecture 1: The Paradox of Deterministic Emergence

### The Fundamental Insight

Consider a chess game. The rules are deterministic — given the same board position and the same move, the result is always the same. Yet from these deterministic rules, Kasparov emerged, and the beauty of a well-played game. Consider the Game of Life: four trivial rules on a grid, producing gliders, oscillators, and patterns of stupefying complexity. Consider, most importantly for this course, the Norns themselves: three figures who spin, measure, and cut a single thread — deterministic, inevitable — yet from that thread grows the entire world tree, every leaf different from every other leaf, every fate unique.

This is the paradox of deterministic emergence, and it is the central insight of this course. A world simulation can be *fully deterministic* — every state transition determined by the previous state and a fixed set of rules — and yet produce behavior that is indistinguishable from randomness, that exhibits genuine novelty, and that gives rise to complex social structures, economic patterns, and narrative arcs that no designer explicitly programmed.

The classical approach to simulation in AI has been to embrace randomness. Want an NPC to make a "random" choice? Call `Math.random()`. Want a weather pattern? Add noise. Want emergent behavior? Throw dice and see what happens. This approach works — poorly. It produces worlds that cannot be reproduced (a critical problem for debugging), worlds that cannot be verified (a critical problem for safety), and worlds that cannot be governed (a critical problem for ethics). Every time you call `Math.random()`, you sever the thread the Norns are spinning. You introduce a cut that cannot be mended.

The deterministic approach does not eliminate randomness. It *tethers* it. A seeded pseudorandom number generator (PRNG) produces a sequence that *looks* random, that *behaves* random in every statistical test, yet is completely determined by its seed. This is not a limitation — it is a superpower. It means that given a seed, the entire history and future of your simulation is fixed. Not approximately fixed. Not mostly fixed. *Exactly* fixed. Run the simulation again with the same seed, and every event, every choice, every storm and every conversation happens in precisely the same order, at precisely the same time, with precisely the same outcomes.

### Why Determinism Matters for AI World Models

The applications are not merely academic:

1. **Verification.** To verify that a world model behaves correctly, you must be able to reproduce its behavior. Nondeterministic simulations make verification exponentially harder — every run produces different behavior, so passing a test once tells you nothing about whether it will pass again.

2. **Debugging.** When a bug appears in a world simulation, you need to replay the exact sequence of events that led to the bug. Nondeterministic simulations deny you this — the bug you saw at 3:47 PM on Tuesday will never happen the same way twice.

3. **Governance.** To govern an AI world model — to ensure it produces behavior within acceptable bounds — you must be able to test those bounds systematically. You need to explore the space of possible world trajectories, and you cannot explore systematically if each trajectory is a random walk.

4. **Scientific reproducibility.** Research on world models requires that other researchers can reproduce your experiments. Without deterministic seeding, this is impossible.

5. **Multi-agent coordination.** When multiple AI agents share a simulated world, they must agree on the world state. Deterministic simulation ensures that all agents, regardless of their execution order, reach the same state.

### The Norn Framework

In this course, we will use the **Norn Framework** as our pedagogical and implementation tool. The Norn Framework is a minimal deterministic simulation engine built around three principles:

- **Urd (What Was):** The seed state. The initial conditions and all prior state form the thread that has already been woven. Urd is history — unchangeable, but knowable.

- **Verðandi (What Is Becoming):** The transition function. Given a state and a set of events, Verðandi determines the next state. Verðandi is the present — the act of weaving, the transformation of possibility into actuality.

- **Skuld (What Must Be):** The commitment structure. Not everything that *could* happen *will* happen. Skuld encodes the obligations, deadlines, and inevitabilities that constrain the space of possible futures. Skuld is the future — not as prediction, but as commitment.

These three principles correspond to the three layers of the WYRD Protocol, which you will study in WM105 (Introduction to the WYRD Protocol). In this course, we focus on a simpler model: a world state, a transition function, and a seeded PRNG that provides the appearance of randomness while maintaining the reality of determinism.

### The Thread Metaphor

Think of a simulation run as a thread on the Norns' loom. The seed number is the first twist of the spindle. From that single number, the entire thread unspools — not arbitrarily, but according to the rules of the loom, the tension of the fiber, and the patterns encoded in the weave. If you start with the same twist, you get the same thread. This is not a limitation of the thread. It is its nature.

Yet within that thread, patterns emerge. Knots, color changes, thicker and thinner sections. A skilled weaver can read a thread and tell you its history. A skilled simulator can read a seed and tell you the entire history of the world. But no one — not the weaver, not the simulator, not even the Norns themselves — can predict the *pattern* without actually weaving the thread. The determinism of the thread does not imply the predictability of the cloth.

### Course Roadmap

This course will proceed as follows:

- **Lectures 1–3** cover the foundations: PRNGs, seeded randomness, and the architecture of a deterministic simulation engine.
- **Lectures 4–6** cover advanced deterministic modeling: event systems, causal ordering, and the handling of concurrent events.
- **Lectures 7–9** cover the art of making deterministic worlds feel alive: stochastic-looking behavior from deterministic seeds, emergent social dynamics, and narrative generation.
- **Lectures 10–12** cover verification, governance, and the capstone project: building a deterministic city simulation.

### Required Reading

- Knuth, D. (1997). *The Art of Computer Programming, Volume 2: Seminumerical Algorithms*, Chapter 3: Random Numbers. Addison-Wesley.
- L'Ecuyer, P. (2012). "Random Numbers for Simulation." *Communications of the ACM*, 55(11), 88–95.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 7: "Deterministic Worlds and the Well of Urd." University of Yggdrasil Press.
- Mähl, D. & Vølverdottir, S. (2041). "The Norn Framework: Deterministic Simulation for Verifiable AI Worlds." *Proceedings of the Yggdrasil Symposium on World Modeling*, 112–128.

### Discussion Questions

1. Is deterministic simulation a form of predestination for simulated agents? If an NPC's every choice is determined by the seed, does the NPC have free will? Discuss the philosophical implications of determinism at the simulation level versus apparent indeterminism at the agent level.

2. Consider the claim that nondeterministic simulations are "more realistic" because the real world contains true randomness. Under what conditions is this claim justified? Under what conditions is it a confusion between epistemic uncertainty (we don't know what will happen) and ontological randomness (the universe itself is indeterminate)?

3. A colleague argues that deterministic seeding is unnecessary for AI world models because "LLMs are already nondeterministic." How would you respond? Consider the difference between model nondeterminism (which can be controlled with temperature and seed) and world state nondeterminism.

---

## Lecture 2: Seeded Pseudorandom Number Generation — The Spindle's First Twist

### The Mathematics of Deterministic Randomness

A pseudorandom number generator (PRNG) is a deterministic algorithm that takes a finite seed and produces a sequence of numbers that appear random. Formally, a PRNG is a function:

    G: Seed → (s₁, s₂, s₃, ...)

where each sᵢ ∈ [0, 1) and the sequence passes statistical tests for randomness. The key properties we require are:

1. **Determinism:** Given the same seed, G always produces the same sequence.
2. **Period:** The sequence eventually cycles, but the period should be astronomically long (2²⁰⁰⁰⁰ or more for modern generators).
3. **Uniformity:** The numbers are uniformly distributed in [0, 1).
4. **Independence:** Consecutive numbers are statistically independent (no correlation detectable by standard tests).
5. **Speed:** The generator computes quickly — world simulations may need billions of random numbers per run.

The seed is the spindle's first twist. It is the origin point from which the entire thread of the simulation unspools. Choose a different seed, and you get an entirely different world. Choose the same seed, and you get the same world — guaranteed.

### PRNG Families

We will study three families of PRNGs relevant to deterministic simulation:

**Linear Congruential Generators (LCGs)** are the simplest and oldest family:

    Xₙ₊₁ = (a·Xₙ + c) mod m

LCGs are fast, easy to implement, and sufficient for simple simulations. They have known weaknesses (low-dimensional structure visible in the sequence) but are perfectly adequate for introductory work. The parameters a, c, and m determine the quality. The classic Numerical Recipes LCG uses a = 1664525, c = 1013904223, m = 2³². We will implement this in Lab 1.

**Mersenne Twister (MT19937)** is the workhorse of scientific computing. It has a period of 2¹⁹⁹³⁷ − 1 (far more than any simulation will ever need), passes virtually all statistical tests, and is fast in practice. Python's `random` module and NumPy's legacy `RandomState` both use Mersenne Twister by default. It has one significant weakness: it is not cryptographically secure (the state can be recovered from 624 outputs), but this is irrelevant for simulation.

The state of a Mersenne Twister is 624 × 32 bits = 2,496 bytes. Capturing and restoring this state is essential for simulation checkpointing. We will use Python's `random.getstate()` and `random.setstate()` for this purpose.

**xoshiro256** (and its variants xoshiro256**, xoshiro256+) is a modern family designed by Sebastiano Vigna. It has a period of 2²⁵⁶ − 1, is faster than Mersenne Twister, and has better statistical properties in the lower bits. It is our recommended generator for new simulation code. The state is only 256 bits (4 × 64-bit integers), making it trivial to capture and restore.

```python
# xoshiro256** reference implementation
def xoshiro256ss(s):
    """xoshiro256** — state is a list of 4 uint64"""
    result = rotl(s[1] * 5, 7) * 9
    t = s[1] << 17
    s[2] ^= s[0]
    s[3] ^= s[1]
    s[1] ^= s[2]
    s[0] ^= s[3]
    s[2] ^= t
    s[3] = rotl(s[3], 45)
    return result, s
```

### The Seeding Protocol

For deterministic simulation, the seeding protocol is as important as the generator itself. We define a **Hermetic Seeding Protocol** that ensures every subsystem in the simulation receives a unique, reproducible seed derived from the master seed.

The protocol works as follows:

1. **Master Seed:** The simulation is initialized with a single master seed S₀. This is the "Urd seed" — the origin of all that follows.

2. **Seed Derivation:** Each subsystem i receives a seed Sᵢ = Hash(S₀ || i || subsystem_name). We use a cryptographic hash (SHA-256 or similar) to ensure that the derived seeds are uniformly distributed and that no two subsystems receive the same seed, regardless of the master seed.

3. **Sub-seeding:** Within a subsystem, the PRNG state is further derived. For example, Agent #42 receives seed S₄₂ = Hash(S_agent || 42). This ensures that each agent's behavior is determined by the master seed, but the derivation is one-way: knowing Agent #42's seed does not reveal Agent #17's seed.

4. **Checkpoint Seeding:** When a simulation is saved and restored, the complete PRNG state is saved alongside the world state. On restoration, the PRNG resumes exactly where it left off.

```python
import hashlib

def derive_seed(master_seed: int, subsystem: str, index: int) -> int:
    """Hermetic seed derivation — every subsystem gets a unique, reproducible seed."""
    h = hashlib.sha256()
    h.update(master_seed.to_bytes(32, 'big'))
    h.update(subsystem.encode('utf-8'))
    h.update(index.to_bytes(32, 'big'))
    return int.from_bytes(h.digest(), 'big')
```

This protocol ensures **hermetic isolation** between subsystems. If Agent #42 makes different decisions, it does not "consume" random numbers that would have been used by Agent #17. This is the most common mistake in non-hermetic seeding: sharing a global PRNG between agents, so that Agent #42 consuming more or fewer random numbers than expected shifts Agent #17's random sequence. With hermetic seeding, each agent has its own PRNG, seeded deterministically from the master seed, and no agent's behavior affects any other agent's random sequence.

### Why Hermetic Seeding Is Non-Negotiable

Consider a city simulation where citizens make daily decisions: whether to go to work, which route to take, whether to visit a friend. In a non-hermetic system, all citizens share a single PRNG. If citizen #42 decides to take a longer route (consuming more random numbers for path selection), all subsequent citizens' decisions shift. The simulation is technically deterministic — given the same seed, the same sequence of random numbers is produced — but the mapping between seed and behavior is fragile. Any change to the simulation (adding a citizen, changing a route) cascades through the entire random sequence, making it impossible to isolate the effect of a single change.

In a hermetic system, citizen #42 has their own PRNG, seeded deterministically from the master seed. Changing citizen #42's route affects only citizen #42. Every other citizen's behavior is unchanged. This is not merely a debugging convenience — it is a structural requirement for simulation governance. Without hermetic seeding, you cannot test the effect of a policy change in isolation, because every policy change perturbs the entire random sequence.

### Required Reading

- Vigna, S. (2019). "It Is High Time We Let Go of the Mersenne Twister." *Computational Statistics and Data Analysis*, 138, 47–65.
- L'Ecuyer, P. & Simard, R. (2007). "TestU01: A C Library for Empirical Testing of Random Number Generators." *ACM Transactions on Mathematical Software*, 33(4), Article 22.
- Salmon, J. et al. (2011). "Parallel Random Numbers: As Easy as 1, 2, 3." *Proceedings of SC11*, Article 16.

### Discussion Questions

1. If a PRNG produces a sequence that passes all statistical tests for randomness, but is fully determined by its seed, in what sense is the sequence "random"? Is there a meaningful distinction between pseudorandomness and true randomness for simulation purposes?

2. Consider a simulation where two identical agents (same type, same seed) are placed in identical environments. Should they behave identically? What if they have different seeds derived from the same master seed? Discuss the implications for agent identity and simulation determinism.

3. A colleague proposes using a cryptographic PRNG (like ChaCha20) for simulation instead of a statistical PRNG. What are the advantages and disadvantages? When might you choose one over the other?

---

## Lecture 3: Architecture of a Deterministic Simulation Engine — The Loom Itself

### The Loom Architecture

A deterministic simulation engine is structured like a loom — the Norns' loom, specifically. The loom has three essential components:

1. **The Warp (World State):** The fixed structure around which the simulation is woven. The world state is a data structure that holds every entity, relationship, and property in the simulation at a given point in time. It is the warp threads — the vertical strands that define the shape of the cloth.

2. **The Weft (Events):** The dynamic threads that pass through the warp, transforming it. Events are the weft — they modify the world state in discrete, ordered steps. Each event is a function that takes the current world state and produces a new world state.

3. **The Shuttle (Transition Function):** The mechanism that passes the weft through the warp, producing the next row of the cloth. The transition function determines the order in which events are processed, resolves conflicts, and produces the new world state.

```
┌─────────────────────────────────────────────┐
│              Norn Simulation Engine           │
├─────────────────────────────────────────────┤
│                                              │
│   ┌──────────┐   ┌──────────┐   ┌────────┐  │
│   │ World     │──▶│ Event    │──▶│ Next   │  │
│   │ State Sₜ │   │ Queue    │   │ State  │  │
│   └────┬─────┘   └────┬─────┘   │ Sₜ₊₁  │  │
│        │              │          └───┬────┘  │
│        │         ┌────┴─────┐        │       │
│        │         │Transition│        │       │
│        │         │ Function │        │       │
│        │         └────┬─────┘        │       │
│        │              │              │       │
│   ┌────┴─────┐   ┌────┴─────┐   ┌────┴────┐│
│   │Entities  │   │  Rules   │   │  PRNG   ││
│   │Relations │   │ Effects  │   │ State   ││
│   │Properties│   │ Filters  │   │(Hermetic)││
│   └──────────┘   └──────────┘   └─────────┘│
│                                              │
└─────────────────────────────────────────────┘
```

### World State as Immutable Snapshots

A critical design decision: should world state be mutable or immutable? In the Norn Framework, we use **immutable snapshots**. Each transition produces a new world state object; the old state is preserved. This has several advantages:

1. **Replay:** Any prior state can be restored instantly by referencing its snapshot.
2. **Branching:** Alternative futures can be explored by branching from any snapshot without modifying the original.
3. **Audit:** Complete history is preserved, enabling forensic analysis of any simulation run.

The performance cost is manageable because we use structural sharing — only the parts of the world state that actually change are copied. The rest is shared between snapshots via reference. In Python, this is naturally achieved through immutable data structures or through copy-on-write patterns.

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Tuple
import copy

@dataclass(frozen=True)
class WorldState:
    """An immutable snapshot of the entire simulation state."""
    tick: int                    # The discrete time step
    entities: Dict[str, Any]     # entity_id -> entity_state (frozen dict)
    relations: Tuple[Tuple[str, str, str], ...]  # (subject, predicate, object)
    properties: Dict[str, Any]   # global properties (weather, time_of_day, etc.)
    prng_state: Tuple[int, ...] # hermetic PRNG state for reproducibility
    
    def next(self, tick: int, entities: Dict, relations: Tuple, 
             properties: Dict, prng_state: Tuple) -> 'WorldState':
        return WorldState(
            tick=tick,
            entities=entities,
            relations=relations,
            properties=properties,
            prng_state=prng_state
        )
```

### Event Processing: The Verðandi Function

The transition function (Verðandi) is the heart of the engine. Given a world state Sₜ and a set of events Eₜ, Verðandi produces the next world state Sₜ₊₁:

    Verðandi: (Sₜ, Eₜ) → Sₜ₊₁

The transition function must be:
- **Pure:** Given the same inputs, it always produces the same output. No side effects, no external state, no hidden randomness.
- **Total:** For every valid (Sₜ, Eₜ), it produces a valid Sₜ₊₁. No crashes, no undefined behavior.
- **Monotonic in time:** Sₜ₊₁ is always at a later time than Sₜ. Time only moves forward.

Event processing follows a strict order:

1. **Collect:** All events scheduled for time t are collected into a list.
2. **Sort:** Events are sorted by a deterministic priority (event type, source entity, target entity, etc.). This ensures that the same set of events is always processed in the same order, regardless of the order in which they were generated.
3. **Apply:** Each event is applied to the world state, producing a new world state. If two events conflict (both modify the same entity), the conflict is resolved by a deterministic rule (first-wins, priority-wins, or merge).
4. **Emit:** Each event may produce new events (reactions, delayed effects, etc.). These are added to the event queue for future processing.

This is the **collect-sort-apply-emit** cycle, and it is the fundamental loop of deterministic simulation.

### The Skuld Layer: Commitments and Invariants

While Urd provides the seed and Verðandi provides the transition, Skuld provides the *commitment structure*. Not every world state is valid. Skuld defines invariants that must hold after every transition:

- **Entity invariants:** Every entity must have a valid type. No entity can have a negative age. Buildings cannot have more occupants than their capacity.
- **Relational invariants:** Every relationship must connect two existing entities. No entity can be its own parent in the family graph.
- **Global invariants:** The total population cannot exceed the city's capacity. The economy must balance (total money in equals total money out, modulo production and destruction events).

Skuld runs after every Verðandi transition. If an invariant is violated, the transition is rejected and the world state rolls back to the previous snapshot. This is the simulation equivalent of a database constraint violation: the transaction is aborted, and the data remains consistent.

In the Norn Framework, Skuld is implemented as a set of invariant-checking functions:

```python
def check_invariants(state: WorldState) -> Tuple[bool, str]:
    """Verify that all Skuld commitments hold."""
    for entity_id, entity in state.entities.items():
        if entity.age < 0:
            return False, f"Entity {entity_id} has negative age: {entity.age}"
        if entity.residence and entity.residence not in state.entities:
            return False, f"Entity {entity_id} references non-existent residence"
    
    for total_check in [check_population, check_economy, check_spatial]:
        ok, msg = total_check(state)
        if not ok:
            return False, msg
    
    return True, "All invariants hold"
```

### Lab 1: Building the Norn Engine Core

In this lab, you will implement the core of the Norn Framework:

1. A xoshiro256** PRNG with hermetic seeding.
2. An immutable WorldState class.
3. The collect-sort-apply-emit event processing loop.
4. At least three Skuld invariants for a simple city simulation.

### Required Reading

- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 7: "Deterministic Worlds and the Well of Urd." University of Yggdrasil Press.
- Evans, R. (2016). "Dungeon World: A Deterministic Approach to RPG Simulation." *Game Developer Magazine*, 23(4).
- Mähl, D. & Vølverdottir, S. (2041). "The Norn Framework: Deterministic Simulation for Verifiable AI Worlds." *Proceedings of the Yggdrasil Symposium on World Modeling*, 112–128.

### Discussion Questions

1. Immutable world state snapshots make replay and branching trivial, but at what performance cost? When might mutable world state be preferable? Consider real-time simulations with millions of entities.

2. The collect-sort-apply-emit cycle processes events in a deterministic order. But what happens when the order of processing *matters* — when Agent A and Agent B simultaneously try to enter a building with capacity for one? Discuss conflict resolution strategies and their implications for simulation determinism.

3. Skuld invariants reject invalid transitions. But what about *soft* invariants — things that should be true most of the time, but might occasionally be false (e.g., a citizen temporarily outside the city limits)? How would you modify the invariant system to handle soft constraints?

---

## Lecture 4: Event Systems and Causal Determinism — The Thread Unspools

### Events as the Weft of Reality

In the Norn Framework, **events** are the atomic units of change. Every modification to the world state — a citizen moving, a weather pattern shifting, a building being constructed — is encoded as an event. The world state never changes except through events. This is the **event sourcing** pattern, and it is fundamental to deterministic simulation.

An event in the Norn Framework is a dataclass with the following fields:

```python
@dataclass(frozen=True)
class Event:
    event_type: str          # "move", "build", "trade", "age", etc.
    source: str              # entity_id of the agent causing the event
    target: str              # entity_id of the entity affected (or "" for global)
    tick: int                # the time step at which this event occurs
    priority: int           # deterministic ordering within a tick
    payload: Dict[str, Any] # event-specific data (frozen dict)
```

The key insight is that events are **first-class data**. They are not side effects; they are values. They can be stored, replayed, analyzed, and compared. An event log is a complete record of everything that happened in the simulation, and it can be used to reconstruct any past state.

### Causal Ordering

In a single-threaded simulation, causal ordering is trivial: events are processed in the order they are generated. But in a world with multiple agents, each generating events independently, we need a **causal ordering** — a way to determine which events happened "before" which other events.

The Norn Framework uses **tick-based ordering** with **deterministic tiebreaking**:

- All events are tagged with a discrete tick number (t₀, t₁, t₂, ...).
- Within a tick, events are ordered by: (1) event_type priority, (2) source entity ID (lexicographic), (3) target entity ID, (4) a deterministic hash of the payload.
- This ensures that the same set of events always produces the same ordering, regardless of the order in which they were generated.

This is sometimes called **Hermetic Ordering**: the ordering is sealed, determined entirely by the data within the events themselves, with no dependence on the execution order of the simulation.

```python
def event_sort_key(event: Event) -> Tuple:
    """Hermetic ordering key — no external dependencies."""
    return (
        event.tick,
        EVENT_TYPE_PRIORITY.get(event.event_type, 999),
        event.source,
        event.target,
        deterministic_hash(event.payload)
    )
```

### Causality and the Arrow of Time

In physics, causality is tied to the arrow of time: a cause must precede its effect. In simulation, we enforce this by ensuring that no event at tick t can reference a state that only exists at tick t+1. Events are processed strictly in tick order, and each tick produces a new, immutable world state.

But there is a subtlety: **simultaneous events**. What if two events occur at the same tick, and they conflict? For example:

- Event A: Citizen X moves from Building 1 to Building 2.
- Event B: Building 2 reaches capacity and locks its doors.

Both events happen at tick t. Which one is processed first? In the Norn Framework, the answer is determined by the event type priority: movement events have priority over capacity lock events, so Event A is processed first. Citizen X successfully enters Building 2, and then the capacity lock fires.

But wait — what if the priority were reversed? Then Building 2 would lock first, and Citizen X's move would fail. The same initial conditions, the same tick, but a different outcome — entirely determined by the priority ordering.

This is the **Norn's Choice**: the determination of which comes first when two threads cross on the loom. It is not arbitrary — it is a design decision that must be made consciously and consistently. The priority ordering is part of the simulation's specification, and changing it changes the simulation's behavior. Documenting and defending the priority ordering is a core responsibility of the simulation engineer.

### Required Reading

- Lamport, L. (1978). "Time, Clocks, and the Ordering of Events in a Distributed System." *Communications of the ACM*, 21(7), 558–565.
- Helms, A. & Vølverdottir, S. (2042). "Hermetic Ordering: Deterministic Event Processing for World Simulation." *Yggdrasil Technical Report* YTR-2042-017.

### Discussion Questions

1. The priority ordering of simultaneous events is a design decision that affects simulation outcomes. Should this ordering be visible to simulated agents? If Citizen X "knows" that movement events have priority over lock events, does this give Citizen X an unfair advantage?

2. In a distributed simulation (multiple machines processing events), Hermetic Ordering requires that all machines agree on the ordering. How would you implement this without a central coordinator? Consider Lamport's logical clocks and their applicability.

3. Can an event be its own cause? That is, can the effect of an event be a new event that modifies the conditions that gave rise to the original event? Discuss the philosophical and technical implications of causal loops in deterministic simulation.

---

## Lecture 5: Parallel Determinism — Weaving with Many Shutttles

### The Challenge of Parallel Determinism

A single-threaded simulation is trivially deterministic: process events in order, one at a time. But a city simulation with 10,000 citizens cannot afford to be single-threaded. Citizens make independent decisions, walk independent paths, and interact only occasionally. The natural parallelism is enormous.

The challenge: how can a parallel simulation be deterministic? If Thread A processes Citizen X's morning routine while Thread B processes Citizen Y's morning routine, and they finish in different orders on different runs, the simulation is nondeterministic.

The solution is **Hermetic Parallelism**: each thread receives a deterministic seed derived from the master seed, processes events in a deterministic order, and produces a deterministic result. The parallel execution is an optimization that does not change the outcome.

```
Master Seed S₀
├── Agent Seed S₁ = Hash(S₀ || 1 || "agent")
│   └── Agent #1's PRNG (completely independent)
├── Agent Seed S₂ = Hash(S₀ || 2 || "agent")
│   └── Agent #2's PRNG (completely independent)
├── ...
└── Agent Seed Sₙ = Hash(S₀ || n || "agent")
    └── Agent #n's PRNG (completely independent)
```

Each agent runs independently, produces a sequence of events, and those events are merged into a global event stream using the Hermetic Ordering protocol from Lecture 4. The merge is deterministic because the ordering is based on event properties (tick, priority, source, target, hash), not on the order in which threads finish.

### The Parallel-Safe World State

When multiple agents access the world state simultaneously, we must ensure that no agent sees a partially-updated state. The Norn Framework uses **copy-on-write semantics**: each agent receives a snapshot of the world state at the beginning of a tick, modifies its own copy, and submits its events to a global queue. The Verðandi function merges these events in Hermetic order at the end of the tick.

This is analogous to how Git branches work: each agent works on its own branch (a copy of the world state), and the branches are merged deterministically based on their commit metadata (tick, priority, source, target).

### Synchronization Points

At certain points in the simulation, all agents must synchronize:

- **End of tick:** All agents submit their events for the current tick, and the Verðandi function merges them.
- **Global events:** Some events (weather changes, economic shifts) affect all agents simultaneously. These are processed at well-defined synchronization points.
- **Cross-agent interactions:** When Citizen X wants to trade with Citizen Y, both agents must agree on the trade. This requires a synchronization point where both agents' states are visible.

The Norn Framework defines these synchronization points explicitly in the simulation specification. Between synchronization points, agents run independently and in parallel. At synchronization points, they merge. The result is a simulation that is both parallel (fast) and deterministic (reproducible).

### Required Reading

- Herlihy, M. & Shavit, N. (2012). *The Art of Multiprocessor Programming*, Revised First Edition. Morgan Kaufmann.
- Mähl, D. (2043). "Hermetic Parallelism: Deterministic Simulation on Multi-Core Architectures." *Yggdrasil Technical Report* YTR-2043-021.

### Discussion Questions

1. If each agent has its own PRNG with a hermetically derived seed, is the total simulation still deterministic? What happens if the number of agents changes (e.g., a new citizen is born)?

2. Consider a simulation where agents can create new agents. When Agent A creates Agent B, what seed should Agent B receive? Discuss the implications for deterministic seeding in dynamic populations.

3. The Git branch analogy suggests that conflicting edits (two agents modifying the same entity) should be merged with a deterministic conflict resolution strategy. What are some possible strategies? Discuss their trade-offs.

---

## Lecture 6: Stochastic Processes in Deterministic Worlds — The Art of Constrained Chaos

### The Illusion of Randomness

The simulation engineer's art is to make a deterministic world appear stochastic. Citizens should make "random" decisions. Weather should be "unpredictable." Markets should "fluctuate." Yet all of these must be completely determined by the seed.

The key technique is **controlled randomness**: using a hermetically seeded PRNG to generate values that are statistically indistinguishable from true randomness, but completely reproducible given the seed.

### Probability Distributions from Deterministic Seeds

Any probability distribution can be sampled deterministically using a PRNG. The PRNG provides uniform samples in [0, 1), and these are transformed into the desired distribution:

- **Discrete choice:** `choices = [A, B, C]; weights = [0.5, 0.3, 0.2]` — use cumulative weights and a uniform sample.
- **Normal distribution:** Use the Box-Muller transform or the Ziggurat algorithm on uniform samples.
- **Exponential distribution:** `t = -ln(U) / lambda` where U is a uniform sample.
- **Poisson process:** Inter-arrival times are exponentially distributed.
- **Dirichlet distribution:** For sampling probability vectors (useful for agent personality models).

Each of these transformations is deterministic given the PRNG state. The same seed always produces the same sequence of "random" values.

### Agent Decision-Making

The most important application of controlled randomness is agent decision-making. Each agent, at each decision point, uses its hermetically seeded PRNG to make a choice:

```python
def agent_decide(agent, world_state, agent_prng):
    """Agent makes a decision using hermetically seeded randomness."""
    options = get_available_options(agent, world_state)
    if not options:
        return None
    
    # Weight each option by the agent's personality and the world state
    weights = [compute_weight(agent, option, world_state) for option in options]
    
    # Sample from the weighted distribution
    choice = weighted_sample(options, weights, agent_prng)
    return choice
```

The `compute_weight` function is deterministic: given the same agent, option, and world state, it always returns the same weight. The `weighted_sample` function is also deterministic: given the same weights and PRNG state, it always selects the same option. Therefore, the entire decision process is deterministic.

Yet the behavior *appears* stochastic. Agent #42 might choose to visit the bakery on tick 1,000, and Agent #17 might choose the library. These choices are determined by the seed, but the pattern of choices — the "personality" of each agent — emerges from the interaction of the agent's weighted decision function and its unique PRNG stream.

### Emergent Social Dynamics

When thousands of agents make deterministic decisions, the aggregate behavior can exhibit genuine emergence: traffic patterns, economic cycles, cultural evolution, and even the formation of social norms. These emergent behaviors are not programmed — they arise from the interaction of individual deterministic decisions.

The key insight is that emergence does not require randomness. It requires *variety* — different agents making different decisions based on different internal states and different PRNG streams. The variety comes from the seed structure, not from ontological randomness.

### Required Reading

- Mitchell, M. (2009). *Complexity: A Guided Tour*. Oxford University Press. Chapters 5–7 on emergent behavior.
- Axelrod, R. (1984). *The Evolution of Cooperation*. Basic Books.

### Discussion Questions

1. If every agent's decision is determined by its seed, can we say that the agent "chose" anything? Discuss the relationship between determinism at the implementation level and choice at the agent level.

2. Consider an agent whose decisions are 99% deterministic (weighted by personality and world state) and 1% random (exploration noise). What is the effect of that 1%? Does it produce genuine novelty, or is it just deterministic novelty (novelty determined by the seed)?

3. A colleague argues that "if the simulation is deterministic, there's no point in running it — you can just predict the outcome." How would you respond? Consider the computational irreducibility argument from Wolfram.

---

## Lecture 7: Deterministic Physics for World Simulation — The Laws of Midgard

### Why Physics Matters for AI World Models

A world model is only as good as its physics. If agents can walk through walls, if objects fall upward, if time runs at different speeds for different agents, the world model is broken. Deterministic physics ensures that the simulated world behaves consistently — the same inputs always produce the same outputs.

But "physics" in a world model is broader than Newtonian mechanics. It includes:
- Spatial relationships (distance, adjacency, containment)
- Temporal relationships (before, after, during, simultaneous)
- Causal relationships (cause, effect, prevention, enablement)
- Social relationships (trade, conflict, alliance, family)
- Economic relationships (supply, demand, pricing, taxation)

Each of these domains has its own "laws" — deterministic rules that govern how the world state evolves. In this lecture, we focus on the spatial and temporal domains; social and economic domains are covered in later courses.

### Deterministic Spatial Simulation

Spatial simulation in the Norn Framework uses a **grid-based** or **continuous** spatial model, depending on the granularity required:

- **Grid-based:** The world is divided into cells (tiles, hexes, or voxels). Each cell has properties (terrain, buildings, occupants). Movement is from cell to cell. This is simple, deterministic, and fast.
- **Continuous:** Positions are real-valued (x, y, z). Movement is along continuous paths. Collision detection is more complex, but necessary for realistic simulations. Determinism requires that all floating-point operations are performed in a consistent order with consistent rounding.

The key principle is **spatial hermeticity**: the spatial simulation has its own PRNG, seeded from the master seed, and all spatial operations (pathfinding, collision, visibility) are deterministic given the spatial state and the spatial PRNG state.

```python
class SpatialSimulation:
    def __init__(self, master_seed: int, bounds: Tuple[float, float, float]):
        self.prng = PRNG(derive_seed(master_seed, "spatial", 0))
        self.bounds = bounds
        self.entities = {}  # entity_id -> (x, y, z)
    
    def move_towards(self, entity_id: str, target: Tuple[float, float, float], 
                     speed: float) -> Tuple[float, float, float]:
        """Deterministically move entity towards target at given speed."""
        current = self.entities[entity_id]
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        dz = target[2] - current[2]
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist <= speed:
            return target
        ratio = speed / dist
        return (current[0] + dx * ratio,
                current[1] + dy * ratio, 
                current[2] + dz * ratio)
```

### Deterministic Temporal Simulation

Time in the Norn Framework is discrete: the simulation proceeds in ticks. Each tick represents a fixed amount of simulated time (e.g., one minute, one hour, one day, depending on the simulation's granularity).

The temporal simulation must handle:
- **Scheduled events:** Events that are scheduled to occur at a specific future tick.
- **Recurring events:** Events that repeat every N ticks (e.g., "every 24 ticks, the sun rises").
- **Temporal invariants:** Properties that must hold at every tick (e.g., "no citizen can be at two locations at the same tick").

All of these are deterministic. Scheduled events are generated by the agents (using their hermetic PRNGs) and placed in the event queue at specific ticks. Recurring events are generated by the simulation engine. Temporal invariants are checked by the Skuld layer after every transition.

### Lab 2: Building a Deterministic Spatial City

In this lab, you will extend the Norn Engine with a spatial layer:

1. Implement a grid-based spatial model with deterministic pathfinding.
2. Implement deterministic collision detection.
3. Create 100 agents with hermetic seeds that navigate the city.
4. Verify that running the simulation with the same seed produces identical results.

### Required Reading

- Reynolds, C. (1987). "Flocks, Herds and Schools: A Distributed Behavioral Model." *ACM Computer Graphics*, 21(4), 25–34.
- Helms, A. & Vølverdottir, S. (2042). "Hermetic Ordering: Deterministic Event Processing for World Simulation." *Yggdrasil Technical Report* YTR-2042-017.

### Discussion Questions

1. Grid-based spatial models are simple and deterministic, but continuous models are more realistic. Under what circumstances is the additional complexity of continuous spatial simulation justified?

2. Floating-point arithmetic is not perfectly reproducible across hardware platforms. How would you ensure deterministic spatial simulation on different machines? Discuss fixed-point arithmetic, rational arithmetic, and floating-point reproducibility standards.

3. Consider a city where two agents simultaneously try to enter the same doorway. How should the simulation resolve this conflict deterministically?

---

## Lecture 8: Reproducing and Debugging Deterministic Worlds — The Weaver's Record

### The Full Replay Capability

One of the most powerful features of deterministic simulation is the ability to **replay** any simulation run from its seed. This means:

- You can reproduce any bug by providing the seed that triggered it.
- You can analyze any interesting behavior by replaying the simulation and examining the state at each tick.
- You can create "save points" by storing PRNG states at key moments, and branch the simulation from any save point.
- You can compare two simulation runs by diffing their event logs.

### Debugging Strategies

Debugging a deterministic simulation is fundamentally different from debugging a nondeterministic one. In a nondeterministic simulation, bugs appear and disappear "randomly." In a deterministic simulation, they appear consistently given the same seed. This is a superpower for debugging:

1. **Seed-based reproduction:** Find the seed that triggers the bug. Provide it to a colleague. They will see the exact same bug.

2. **Event log inspection:** The event log is a complete record of everything that happened. You can trace the exact sequence of events that led to the bug.

3. **State diffing:** Compare two world states (before and after a suspicious transition) to find exactly what changed.

4. **Binary search on ticks:** If a bug manifests at tick T, check the state at tick T/2. If the bug is present, search backward. If not, search forward. This is O(log T) — very efficient.

5. **Minimization:** Remove agents, events, or subsystems until the bug disappears. The minimal set of agents and events that still triggers the bug is a much smaller test case.

### Deterministic Testing

Testing a deterministic simulation is straightforward:

- **Unit tests:** For each event type, create a world state, apply the event, and verify the new state. Since both the world state and the event are data, they can be stored as test fixtures.
- **Integration tests:** Run a short simulation with a known seed and verify that the final state matches the expected state. This is a "golden path" test.
- **Regression tests:** When a bug is found, create a test that reproduces it. After the fix, include the test in the suite to prevent regression.
- **Property-based tests:** Use the simulation's determinism to verify properties: "For any seed, the total population is always non-negative." "For any seed, no entity is ever in two places at once."

```python
import random

def test_population_non_negative(seed):
    """Property: total population is always non-negative."""
    sim = NornSimulation(seed=seed)
    for tick in range(1000):
        state = sim.step()
        for entity in state.entities.values():
            assert entity.population >= 0, \
                f"Negative population at tick {tick}"

# Run for many seeds
for seed in range(1000):
    test_population_non_negative(seed)
```

### Required Reading

- Claessen, K. & Hughes, J. (2000). "QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs." *ACM SIGPLAN Notices*, 35(9), 268–279.

### Discussion Questions

1. A colleague discovers a bug that only appears with seed 42,317. They fix the bug, but now seed 42,317 produces different behavior for all subsequent ticks. Is this a problem? When is it acceptable to change simulation behavior, and when is it a regression?

2. How would you implement "time travel" debugging — the ability to step backward through a simulation run, examining the state at each previous tick? What data structures would you need?

3. Property-based testing generates random seeds and checks invariants. What invariants would you check for a city simulation? How would you ensure that your invariant checkers are comprehensive?

---

## Lecture 9: Governance, Verification, and the Skuld Commitment — What Must Be

### The Governance Layer

Deterministic simulation is not just a technical convenience — it is a governance necessity. If you cannot reproduce a world simulation's behavior, you cannot verify that it is safe, fair, or aligned with human values.

The Skuld layer in the Norn Framework serves as the governance layer:

1. **Invariant checking:** After every transition, Skuld verifies that all invariants hold. If any invariant is violated, the transition is rejected.

2. **Boundary checking:** Skuld defines acceptable ranges for simulation variables. If the population exceeds 10 million, the simulation is paused. If the average citizen happiness falls below a threshold, an alert is raised. These are *soft invariants* — they don't reject transitions, but they trigger warnings.

3. **Audit logging:** Every transition is logged. The audit log is a first-class artifact of the simulation, stored alongside the world state snapshots and the event log. It can be inspected forensically to determine exactly what happened and why.

4. **Policy enforcement:** Skuld can enforce policies that govern agent behavior. For example: "No agent may acquire more than 50% of the city's resources." This is enforced by modifying agent decision weights rather than by rejecting agent actions — a softer approach that preserves agent autonomy within bounds.

### Verification of Deterministic Simulations

Verification is the process of proving that a simulation meets its specification. For deterministic simulations, verification is tractable because the behavior space is finite (modulo the PRNG seed):

1. **Model checking:** Enumerate reachable states and verify that all of them satisfy the invariants. For small simulations, this is feasible. For large simulations, use bounded model checking (check up to a maximum number of ticks or a maximum number of agents).

2. **Formal specification:** Write the simulation's specification in a formal language (e.g., TLA+, Alloy, or the Yggdrasil Specification Language). Verify that the implementation matches the specification.

3. **Statistical verification:** Run the simulation with many seeds and collect statistics. Verify that the statistics match expected distributions. For example: "The average population growth rate should be between 0.5% and 1.5% per tick across 10,000 random seeds."

4. **Conformance testing:** Verify that the simulation's behavior conforms to a reference implementation or a mathematical model. For example: "The probability that a citizen moves to an adjacent building should match the gravity model of spatial interaction."

### The Skuld Promise

The Skuld layer makes a promise: **for any seed, the simulation will produce a world that satisfies all stated invariants.** This is a strong guarantee. It means that no matter how the simulation is run — locally, in the cloud, on different hardware — the result will always be a valid world.

This promise is the foundation of trustworthy AI world models. If you can trust the Skuld layer, you can trust the entire simulation.

### Required Reading

- Clarke, E. et al. (2000). "Model Checking." MIT Press. Chapters 1–3.
- Freyjasdóttir, R. (2039). *The Memory-Bearing Machine*, Chapter 14: "Wyrd Verification: Proving What Must Be." University of Yggdrasil Press.

### Discussion Questions

1. The Skuld layer rejects transitions that violate invariants. But what about transitions that are *technically* valid but *morally* problematic? For example, a citizen's "personality" might deterministically lead them to commit a crime. Should the simulation allow this? Discuss the difference between simulation realism and simulation ethics.

2. Formal verification requires a formal specification. Who writes the specification? Who decides what the invariants should be? Discuss the governance implications of specification authorship.

3. Statistical verification checks that the *average* behavior matches expectations. But what about *tail* behavior — the rare but catastrophic events that deterministic simulation might produce? How would you verify the safety of rare events?

---

## Lecture 10: The Norn Framework Complete — A City Simulation

### Capstone Project Overview

In the capstone project, you will build a complete deterministic city simulation using the Norn Framework. The simulation will include:

1. **Citizens** — Agents with hermetic seeds, personalities, homes, jobs, and social networks.
2. **Buildings** — Residential, commercial, and public buildings with capacity constraints.
3. **Economy** — A simple market with supply, demand, and pricing.
4. **Weather** — Deterministic weather patterns that affect citizen behavior.
5. **Transportation** — A grid-based road network with deterministic pathfinding.
6. **Social dynamics** — Citizens form friendships, trade, and sometimes conflict.

### The City Specification

Your city simulation must satisfy the following invariants:

- **Population invariant:** Total population is always between 100 and 10,000.
- **Spatial invariant:** No citizen can be in two locations at the same tick.
- **Capacity invariant:** No building can have more occupants than its capacity.
- **Economic invariant:** Total money in the system is conserved (modulo production and destruction events, which are tracked).
- **Happiness invariant:** Average citizen happiness is always between 0 and 100 (inclusive).

### Verification Requirements

Your simulation must pass the following verification tests:

- **Reproducibility test:** Running with the same seed produces identical results.
- **Population test:** For 100 random seeds, the population invariant holds at every tick for 10,000 ticks.
- **Economy test:** For 100 random seeds, the economic invariant holds at every tick for 10,000 ticks.
- **Happiness test:** For 100 random seeds, the average happiness is between 0 and 100 at every tick.

### Submission Requirements

Submit:

1. The complete source code for your simulation.
2. A test suite that verifies the invariants above.
3. A brief report (3–5 pages) describing your design decisions, particularly:
   - Your PRNG choice and hermetic seeding strategy.
   - Your event ordering and conflict resolution strategy.
   - Your invariant implementation.
   - Any interesting emergent behavior you observed.

---

## Lecture 11: Advanced Topics in Deterministic Simulation — Beyond the Basics

### Deterministic Agent Learning

Can agents learn in a deterministic simulation? Yes — but their learning must also be deterministic. An agent that uses a learning algorithm (e.g., Q-learning, neural network training) must use a hermetically seeded PRNG for all random aspects of learning (exploration, weight initialization, dropout, etc.).

The key requirement is that the learning algorithm's state (weights, exploration parameters, etc.) is part of the world state. At any save point, the agent's learned knowledge is captured and can be restored.

### Genetic Algorithms with Deterministic Seeds

Genetic algorithms are a natural fit for deterministic simulation. Each individual in the population is seeded from the master seed, and the selection, crossover, and mutation operations are all deterministic given their PRNG states. This means that:

- The same evolutionary run always produces the same population.
- Cross-generation comparisons are meaningful (you can compare generation 100 to generation 200 without confounds).
- The fitness landscape can be explored systematically by varying the seed and observing the resulting evolutionary trajectories.

### Deterministic Noise and Artistic Variation

Not all noise is undesirable. In creative applications — procedural generation of terrain, architecture, or NPC appearance — deterministic noise adds variety without sacrificing reproducibility. Perlin noise, Simplex noise, and Worley noise are all deterministic functions of their input coordinates and a seed. They produce natural-looking variation that is completely reproducible.

### Required Reading

- Mitchell, M. (1996). *An Introduction to Genetic Algorithms*. MIT Press.
- Perlin, K. (2002). "Improving Noise." *ACM SIGGRAPH 2002*, Session: Algorithms.

### Discussion Questions

1. An agent that learns deterministically in a deterministic world will learn the same thing every time the simulation is run. Is this a problem? Under what circumstances would you want learning to be nondeterministic?

2. Genetic algorithms with deterministic seeds produce the same population for the same seed. But what if you want to explore *diverse* evolutionary trajectories? How would you balance determinism with diversity?

3. Procedural generation of terrain and architecture is deterministic given the seed. Does this mean that all "procedurally generated" content is ultimately predetermined? Can a deterministic process produce genuine novelty?

---

## Lecture 12: The Norns' Thread — Course Synthesis and Open Problems

### The Thread Spun, Measured, and Cut

We began this course with the Norns: Urd, Verðandi, and Skuld. Urd spins the thread from the seed — the initial conditions, the PRNG, the hermetic derivation. Verðandi weaves the thread through the present — the transition function, the event processing, the deterministic ordering. Skuld measures and cuts — the invariants, the governance constraints, the verification framework.

Together, they produce the cloth of deterministic simulation: a world that unfolds inevitably from its seed, yet exhibits the richness and surprise of genuine emergence. The thread is spun. The loom is built. The cloth is woven. And the Norns — the three principles of seed, transition, and constraint — govern every step.

### Open Problems

1. **Scalability:** Hermetic seeding works well for simulations with thousands of agents. What about millions? What about billions? The PRNG state for each agent is small (256 bits for xoshiro256), but the world state snapshots become enormous. How can we scale deterministic simulation to planetary-scale worlds?

2. **Learning agents:** If agents learn, their behavior changes over time. This means that a simulation with learning agents is not a simple function of its seed — it also depends on the learning trajectory. How can we ensure reproducibility when agents have internal state that evolves?

3. **Human-in-the-loop:** Some world models incorporate human input (e.g., a human dungeon master, a human player). How can we make these interactions deterministic? The human is a source of true randomness (or at least, of input that is not determined by the simulation seed).

4. **Explainability:** Deterministic simulations are reproducible, but are they explainable? Can we trace *why* a citizen made a particular decision? This requires not just reproducibility, but interpretability — the ability to decompose a decision into its deterministic components.

5. **Quantum effects:** Real-world systems exhibit genuine quantum randomness. For simulations that model quantum-scale phenomena, true randomness (from quantum random number generators) may be necessary. How can we reconcile this with the deterministic framework?

### The Weaver's Duty

As simulation engineers, our duty is clear: weave the thread deterministically, verify the cloth with Skuld's invariants, and never forget that every thread we spin produces a world that someone — an AI agent, a researcher, a citizen — will inhabit. The quality of our weaving determines the quality of their world.

### Final Exam

The final exam consists of:

1. **Code submission:** Your capstone project (deterministic city simulation) with test suite.
2. **Written exam:** Covering all twelve lectures, with emphasis on Hermetic Seeding, the collect-sort-apply-emit loop, Skuld invariants, and verification strategies.
3. **Oral defense:** A 30-minute discussion of your design decisions, emergent behaviors, and open problems.

The Norns are watching. The thread is spun. May your weaving be tight and your invariants hold.

**ᚱ Raidho — Rhythm, Movement, the Sacred Journey**

---

## Appendix A: Norn Framework API Reference

### Core Classes

```python
class PRNG:
    """Hermetic pseudorandom number generator."""
    def __init__(self, seed: int):
        """Initialize with a seed value."""
        ...
    def next(self) -> float:
        """Return a uniform random float in [0, 1)."""
        ...
    def next_int(self, n: int) -> int:
        """Return a uniform random integer in [0, n)."""
        ...
    def next_normal(self, mean: float = 0.0, std: float = 1.0) -> float:
        """Return a normal random float."""
        ...
    def get_state(self) -> Tuple[int, ...]:
        """Return the current PRNG state for checkpointing."""
        ...
    def set_state(self, state: Tuple[int, ...]):
        """Restore the PRNG state from a checkpoint."""
        ...

def derive_seed(master_seed: int, subsystem: str, index: int) -> int:
    """Hermetic seed derivation."""
    ...

class WorldState:
    """Immutable snapshot of the entire simulation."""
    tick: int
    entities: FrozenDict[str, Entity]
    relations: FrozenSet[Relation]
    properties: FrozenDict[str, Any]
    
class Event:
    """An atomic change to the world state."""
    event_type: str
    source: str
    target: str
    tick: int
    priority: int
    payload: FrozenDict[str, Any]

class NornSimulation:
    """The complete deterministic simulation engine."""
    def __init__(self, seed: int, invariants: List[Callable]):
        ...
    def step(self) -> WorldState:
        """Advance one tick. Collect-sort-apply-emit."""
        ...
    def run(self, n_ticks: int) -> List[WorldState]:
        """Run for n ticks. Return all states."""
        ...
    def check_invariants(self, state: WorldState) -> Tuple[bool, str]:
        """Check all Skuld invariants."""
        ...
```

### Utility Functions

```python
def weighted_sample(options: List, weights: List[float], prng: PRNG) -> Any:
    """Deterministic weighted random selection."""
    ...

def deterministic_hash(data: Any) -> int:
    """Consistent hash for Hermetic Ordering tiebreaking."""
    ...
```

---

## Appendix B: Recommended Development Environment

- **Python 3.11+** with type hints
- **pytest** for deterministic testing
- **hypothesis** for property-based testing
- **mypy** for type checking
- **numpy** for numerical operations (use `numpy.random.Generator` with explicit seeds)
- **rich** for terminal rendering of simulation state

---

*Course materials © 2044 University of Yggdrasil. All rights reserved.*
*ᚱ Raidho — The road opens. Trust the journey.*
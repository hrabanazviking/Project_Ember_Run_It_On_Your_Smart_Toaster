# University of Yggdrasil — Batch 2 Absorption Index
## Absorbed: 2026-05-14

### Courses Processed (5 of 5)

| File | Course | Key Concepts Extracted |
|------|--------|----------------------|
| `OS203_muninn_gate.json` | OS203 — MuninnGate: Memory Gate Architecture | 5 concepts |
| `OS205_entity_canonization.json` | OS205 — Entity Canonization and Identity Persistence | 5 concepts |
| `OS207_huginn_gate.json` | OS207 — HuginnGate: Thought Gate Architecture | 5 concepts |
| `WM201_mimir_droplet.json` | WM201 — World State Persistence and Memory | 5 concepts |
| `WM203_npc_memory.json` | WM203 — NPC Memory Systems | 5 concepts |

### Total: 25 key novel architectural concepts extracted

---

## Concept Summary by Course

### OS203 — MuninnGate: Memory Gate Architecture
1. **Four Faces of Muninn** — Read/Write/Forget/Gate gates for controlled memory access; Gate of Gating is the executive control deciding WHEN to remember/forget
2. **Meta-Cognitive State Representation (MCSR)** — Structured summary of agent's cognitive situation (goals, budget, emotions, memory stats, retrieval history) enabling the Executive Module to reason about its own state
3. **Attention-Based Retrieval with Dynamic Budget** — Four-stage retrieval (Query Construction → Candidate Retrieval → Attention Scoring → Budget Allocation) with dynamic context window allocation
4. **Memory Inscription Pipeline** — Five steps (Classify → Extract → Annotate → Link → Tag) transforming raw experience into structured memory with emotional metadata and relational graphs
5. **Governance-Enforced Access Predicates (MAC)** — Mandatory Access Control for memory: Read/Write/Prune predicates evaluated by governance levels; cross-level access via explicit tags or guardian mediation

### OS205 — Entity Canonization and Identity Persistence
1. **Three Pillars of Identity + Tiered Mutability** — Values/Personality/Relationships as holistic identity; P0 immutable (core values) through P3 mutable (surface preferences)
2. **Identity Hash Chaining** — SHA-256 hash of canonization schema, chained on evolution (v2 includes v1 hash); append-only, tamper-evident audit trail
3. **Zero-Knowledge Identity Proofs** — Prove identity knowledge without revealing schema; distinguishes genuine/corrupted/impostor/hallucination entities
4. **Personality Lattice (3 Levels)** — Dispositional (P0) → Contextual (P1) → Situational (P2) with inheritance, override, composition operations
5. **Stochastic Personality Composition (SPC)** — Traits as probability distributions N(μ, σ²) with temperature control; each expression is a "rune-cast" sample

### OS207 — HuginnGate: Thought Gate Architecture
1. **Three Cognitive Pipelines** — Analysis (understanding), Judgment (evaluation), Synthesis (expression) as parallel interacting processes, not sequential stages
2. **Situational Model as Working Memory** — Weighted evidence accumulation with source reliability, contradiction resolution, and uncertainty propagation; constrained by context budget
3. **Value Cascade & Proportional Trade-Off** — Constitutional Values → Interpretive Principles → Situational Rules → Action Determination; NOT absolute priority but proportional magnitude comparison
4. **Constitutional Reasoning Traces + CRA** — Each reasoning step annotated with values considered, influence, alternatives rejected, confidence; Constitutional Reasoning Auditor flags omissions, misapplications, calibration mismatches
5. **Cognitive Budget & Graceful Degradation** — FLOPs/Time/Quality dimensions; 5 degradation levels from L1 (skip polishing) to L5 (safe fallback)

### WM201 — World State Persistence and Memory (Mímir's Droplet)
1. **Event Sourcing with Hash-Chained Log** — WorldEvent is the single source of truth; causality_hash chains events like blockchain; enables temporal query, audit, debug, branching
2. **Three-Tier Hybrid Storage** — Full snapshots (N=1000 ticks) + Incremental snapshots (M=10 ticks) + Event log (every tick); reconstruct state at any tick
3. **Differential State Storage (Delta Encoding)** — StateDelta records only property_changes, creations, deletions, relationship changes; O(K) not O(N)
4. **Mímir Protocol Multi-Layer Query** — Hash/Tree/Graph indexes + Materialized Views over Snapshot Store over Event Log
5. **Impermanence Three Dimensions** — Durability (crash recovery), Portability (migration), Temporality (historical query)

### WM203 — NPC Memory Systems
1. **Nested Cognition (Mímir-in-Mímir)** — Each NPC has own persistence layer inside parent world model; P0-P3 tiered memory allocation; memory privacy between layers
2. **NPC Episodic Memory** — Subjective content field (not global truth), emotional_valence, importance, confidence; NPCReadGate retrieval scoring with mood boost
3. **Social Relationship Memory** — Directed weighted asymmetric graphs (valence, strength, type, last_interaction, shared memories); affect greetings, pricing, info sharing, action thresholds
4. **Goal-State Memory** — P0 Survival → P1 Vocation → P2 Social → P3 Aspirational; aspiration engine from personality + needs + peers + memories
5. **NPC Forgetting** — Decay curves parameterized by intelligence (λ) and reinforcement (β); suppression/repression/amnesia; emotional bias in recall

---

## Cross-Course Connections Identified

- **OS203 ↔ OS207**: MuninnGate (memory) and HuginnGate (thought) are twin gates — MuninnGate retrieves memories that HuginnGate processes. The Gate of Gating in MuninnGate corresponds to the Cognitive Budget manager in HuginnGate.
- **OS203 ↔ WM203**: MuninnGate's Read Gate is miniaturized as NPCReadGate for NPC episodic memory retrieval, using the same scoring approach (importance × mood_boost × recency × confidence).
- **OS205 ↔ OS207**: Personality Lattice's context-dependent trait expression feeds directly into HuginnGate's Synthesis Pipeline (tone calibration, audience modeling).
- **WM201 ↔ WM203**: Mímir Protocol persistence is replicated at NPC scale (Mímir-in-Mímir architecture), with tiered resource allocation.
- **OS205 ↔ WM203**: Canonization's Tiered Mutability (P0-P3) mirrors NPC Memory's Tiered Memory (P0-P3) — different systems converging on similar priority architectures.

---

*Ready for import into Runa's memory systems (runa_remember + fact_store).*
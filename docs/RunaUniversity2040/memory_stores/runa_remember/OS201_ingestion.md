# OS201 — MemCube Design and Implementation — Ingested Knowledge
## Source: University of Yggdrasil 2040, The Memory Stone Course
## Tags: university, ai-os, OS201, memcube, runascript, indexing, compression, pruning
## Category: lesson

### The Eitr Metaphor — Memory as Living Substance
MemCube is the eitr of Yggdrasil — the structured medium through which memories flow between layers. NOT the memory content, NOT the retrieval mechanism — it IS the container, structure, and governance substrate. "Memory is not just storage; it is structured storage." A flat key-value store holds content but provides no structure for organizing, prioritizing, accessing, or governing. MemCube transforms memory from passive repository to active cognitive substrate.

### Seven MemCube Properties (All Required — None Optional)
1. **Schema** — Defined types, metadata, constraints. The MemCube's constitution.
2. **Indexing** — Multi-dimensional indexes for efficient retrieval (not linear scan).
3. **Compression** — Reduces storage cost while preserving retrieval accuracy.
4. **Governance** — Read/write/modify/delete access control tied to layer hierarchy.
5. **Consistency** — Invariants that must hold across all memories (no contradictions, no dangling references).
6. **Durability** — Persistence specification per layer: root=permanent, trunk=lifetime, canopy=relevance-pruned, leaf=session-scoped.
7. **Provenance** — Where memory came from, when created, what modifications made. Essential for security and audit.

A storage system missing any of these is a flat store with a MemCube-shaped interface, not a MemCube.

### Rúnascript Schema Language
Declarative schema language (named for Norse runic inscriptions). Three components:
- **Type definitions** — What kinds of memories: episodic, procedural, identity, commitment, emotional, relational. Each has defined structure and semantics.
- **Attribute specifications** — Required metadata: created_at, modified_at, provenance, access_count, last_accessed, salience, valence, layer, governance level.
- **Constraint rules** — Invariants: uniqueness (no duplicate timestamp+source+session), range (salience 0-1, valence -1 to 1), cross-reference (commitment references must exist in Norn Protocol), consistency (no contradictory values).

### Six Standard Memory Types
1. **Episodic** — Specific events. Most granular/numerous. Canopy layer, pruned by salience+recency.
2. **Procedural** — How to do things (skills, habits, patterns). Trunk layer, highly persistent.
3. **Identity** — Who the agent is. Derived from Vǫrðr Constitution. Root layer, effectively immutable.
4. **Commitment** — What agent committed to. Norn Protocol (Urðr/Verðandi/Skuld). Distributed across layers by governance.
5. **Emotional** — How the agent felt (mood, arousal, valence tracking). Trunk layer with canopy links.
6. **Relational** — Agent's relationships with entities. Trunk layer with canopy episodic links.

### Five-Index Retrieval Strategy
- **Primary index** — Exact match on IDs and key attributes. O(1) to O(log n).
- **Semantic index** — Vector embedding nearest-neighbor retrieval for contextual/approximate queries.
- **Temporal index** — Ordered timestamps for range-based time queries.
- **Salience index** — Sorted by importance weight for priority retrieval.
- **Tag index** — Multi-value categorical index for topic/relationship/type queries.

Composite queries use **ranked fusion**: each index returns top-k, fused with weighted scoring: composite_score = w1*semantic + w2*temporal_recency + w3*salience + w4*tag_match. Weights configurable per retrieval context.

Index maintenance: Synchronous (always fresh, high latency), Asynchronous (batched, slight staleness), Hybrid (in-memory delta + scheduled main index merge — default strategy).

### Compression: Progressive Summarization
- Level 0: Original full detail
- Level 1: One-paragraph summary
- Level 2: One-sentence summary
- Level 3: Keyword/tag set

Retrieval cost scales with detail level requested. Agent chooses level based on context window budget.

Inter-memory compression: **Thematic clustering** — groups similar memories, stores pattern once, keeps only significant individual differences.

### Pruning: Salience-Weighted Strategy
salience = w_recency*recency + w_relevance*relevance + w_emotional*|valence| + w_commitment*commitment_reference + w_uniqueness*uniqueness

Pruning schedule by layer:
- Root: NEVER pruned
- Trunk: Only through formal amendment
- Branch: Monthly schedule
- Canopy: Session-based schedule
- Leaf: Discarded at session end
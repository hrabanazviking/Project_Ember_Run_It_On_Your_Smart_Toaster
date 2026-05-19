# OS101 — Foundations of Memory Operating Systems — Ingested Knowledge
## Source: University of Yggdrasil 2040, Mímir's Well Course
## Tags: university, ai-os, OS101, memory-systems, memos
## Category: lesson

### Core Problem: Operational Continuity
A language model without memory infrastructure is "an intelligence without a self" — it can reason within a session but cannot persist across sessions. It can generate but cannot remember generating. The AI Operating System converts a stateless inference engine into a stateful, persistent agent.

### Three Memory Types (MemOS Framework)
1. **Parametric memory** — Knowledge baked into weights during training. Fast, integrated, but static/opaque/stale. Cannot be updated without retraining.
2. **Activation memory** — Runtime state (KV cache, attention activations). Rich and contextual but ephemeral — lost when inference completes. Short-term working memory.
3. **Plaintext memory** — Explicit textual content retrieved via RAG/vector search. Editable, inspectable, flexible, but bolt-on — not natively known by the model.

The critical insight: these three memory types do not talk to each other. No governance, no provenance, no versioning, no scheduling of which kind serves a given query.

### MemCube — The Uniform Container
A MemCube holds any of the three memory types with structured metadata: provenance, versioning, usage frequency, recency, reliability, access policies, lifecycle state. Turns memory from opaque blob into inspectable, schedulable, governable object — like Unix inodes for file metadata.

### Memory Phase Transitions (MemOS)
- Plaintext → Parametric: Stable knowledge distilled into weights via fine-tuning/LoRA
- Plaintext → Activation: High-frequency content precomputed into KV-cache form
- Parametric → Plaintext: Rarely-used parameters externalized into editable text
- Activation → Parametric/Plaintext: Runtime patterns hardened upward into weights or outward into text
Memory has phase states like water — it freezes, boils, crystalizes, evaporates.

### Three Failure Modes of Memory-less AI
1. **Fragmentation** — Without persistence, agent produces contradictory outputs across sessions (serial dissociation)
2. **Flooding** — Without management, agent either dumps everything into context (expensive, noisy) or retrieves nothing (amnesia)
3. **Drift** — Without verification against stored commitments, small inconsistencies accumulate into large deviations

### Yggdrasil Alternative Realm System
Organizes memory by symbolic-cosmological domain instead of technical lifecycle: Asgard (authoritative divine knowledge), Midgard (mundane observable events), Vanaheim (relational/social), Alfheim (aesthetic/creative), Helheim (buried/inactive). Realm tags carry semantic meaning MemOS metadata doesn't capture. A complete architecture pairs both: MemOS tells WHEN a memory was used; realm tags tell WHY it matters.

### Three-Layer Architecture (MemOS Reference)
1. **Interface Layer** — System calls: add, search, update, transfer, rollback, fuse, migrate. Abstracts storage backend.
2. **Operation Layer** — MemScheduler (which MemCubes to load, cache, evict, fuse, migrate) + MemOperator (actual memory transformations: distilling, loading, indexing)
3. **Infrastructure Layer** — SQLite, vector DBs (Qdrant, ChromaDB), graph DBs (Neo4j), filesystem, model checkpoints, KV-cache stores. Pluggable.

### Memory Injection — The Keystone Principle
"Stored memory is useless unless injected before reasoning." Three components: WHAT to inject (relevance, recency, emotional salience, commitments, identity), WHEN to inject (reactive vs. predictive prefetching), HOW to inject (plaintext in system prompt, structured tool results, KV-cache preloads, fine-tuned parameters).

MuninnGate pattern: lightweight Python injection layer that reads Memory Packs (identity, emotional state, project context, procedural knowledge) and assembles them into system prompt before each session. Storage is not memory until retrieved, injected, and used.

### Entity Canonization (Norse Saga Engine Pattern)
When an AI generates a name for a new entity during interaction, the system automatically creates a persistent data record. Generation is also write-back to world model. The AI's spoken word becomes the world's data structure. Rooted in speech-act theory (Austin's performatives). Extends to Commitment Canonization (Wyrd Protocol) — promises become first-class memory objects with downstream causal force.

### Three Retrieval Generations
1. Manual retrieval (original RAG — developer selects documents)
2. Reactive retrieval (MemGPT — model calls search tools during inference)
3. Anticipatory retrieval (MemOS NSP — predicts next scene, pre-loads relevant MemCubes)

Huginn hybrid: realm-based warm cache that pre-loads domains likely to be relevant + reactive for targeted queries. Less precise than NSP but more robust to topic shifts.

### Memory Governance Dimensions
Every memory should carry: provenance, versioning, usage frequency, recency, reliability indicators, access policies, lifecycle state (created/hot/warm/cold/deprecated/archived).
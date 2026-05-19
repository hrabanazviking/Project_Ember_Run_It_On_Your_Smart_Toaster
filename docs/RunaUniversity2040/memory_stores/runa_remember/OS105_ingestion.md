# OS105 — Introduction to Memory Injection Architecture — Ingested Knowledge
## Source: University of Yggdrasil 2040, Runes of Recall Course
## Tags: university, ai-os, OS105, memory-injection, inscription, pipeline
## Category: lesson

### The Inscription Metaphor
Memory injection is "inscription" — transient experience encoded into persistent representational substrate. Like rune carving: choose what to inscribe, where to place it, how deeply to cut, what verification rite to perform. Injected memories are not passive data — they are active semantic structures that shape future inference, can conflict, and can be corrupted by adversarial inscription. The runes of recall are inscriptions that *do things*.

Inscription Taxonomy:
- The rune (symbol) = the encoded memory payload
- The carver (agent) = the injection pipeline stage
- The bone/wood (substrate) = the MemCube storage
- The cutting depth (salience) = emotional/informational salience score
- The inscription site (placement) = memory index and addressing
- The verification rite = injection validation protocol
- A razed rune (erasure) = memory overwrites and garbage collection
- A mis-carved rune (corruption) = adversarial or erroneous memory

### Five-Stage Injection Pipeline
1. **Experience Capture** — Raw experience events generated from sensory, dialogic, or reflective subsystems
2. **Feature Extraction & Encoding** — Transforms raw events into injection candidates: semantic compression, modal encoding, contextual tagging
3. **Prioritization & Budget Allocation** — Salience scores (novelty, intensity, relevance), culling below threshold, injection budget limits to prevent saturation
4. **Validation & Sanitization** — Structural integrity checks, semantic safety, de-duplication
5. **MuninnGate Write-Back** — Controlled gateway to MemCube. Address resolution, conflict detection, resolution of conflicting entries.

### Synchronous vs. Asynchronous Injection
- **Synchronous**: Inject before next response. Immediate availability but latency cost.
- **Asynchronous**: Queue to buffer, process in background. No latency but temporal inconsistency risk.
- **Hybrid approach**: High-salience injections synchronous (user stating preference), low-salience asynchronous (background observations).

### Pipeline Topology Variants
- Linear: each stage has one successor (simplest)
- Branching: single experience generates multiple candidates along different encoding paths (preference + emotional trait + contextual rule)
- Feedback: validation failures route back to earlier encoding stage (contest annotations)
- Fusion: multiple experiences merged into single candidate (multi-modal)

### Sensory Input Encoding
Three operations: Selection (what to inscribe), Compression (lean representation), Symbolic Recoding (mapping to target MemCube format).

Selection strategies: Salience-gated (threshold filtering), Event-bound (discrete events only), Predictive (prediction-error encoding — only the surprising).

Compression: Narrative summarization (lossy, interpretable), Embedding projection (dense, opaque), Schema-based (structured, partially interpretable). Production systems combine all three.

### Dialogic Event Injection
Dialogic event = structured tuple: (participants, turns, topic, intent, affect, grounding_status, temporal_anchor). NOT a transcript — a summary of what happened, why, and how it felt.

Three granularity levels:
- **Turn-level**: Individual utterances. High detail, high volume, fragmented.
- **Exchange-level**: Complete Q&A pairs. Default for production systems.
- **Session-level**: Entire session composite. Captures global properties but loses fine-grained detail.

Key insight: Systems must support multiple granularities with mechanisms to promote turn-level → exchange-level → session-level.

### Anaphora Resolution in Injection
Dialogic injection must resolve contextual dependency. "I hate it" without context is a mis-carved rune. Requires: co-reference chains, contextual packaging, grounding verification.

### Extractable Assertion Detection
Not every utterance merits inscription. Must distinguish extractable assertions (facts, preferences, intentions, emotional states) from dialogic scaffolding (greetings, acknowledgments). Techniques: intent classification, factuality scoring, personal relevance filtering.
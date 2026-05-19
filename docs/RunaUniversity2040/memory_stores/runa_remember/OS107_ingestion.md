# OS107 — Yggdrasil Cognitive Architecture I: Descent — Ingested Knowledge
## Source: University of Yggdrasil 2040, Roots and Soil Course
## Tags: university, ai-os, OS107, yggdrasil, root-layer, vordr-constitution, norn-protocol
## Category: lesson

### The World Tree Layered Architecture
Five-layer hierarchy with downward dependency (each layer depends on layers below, never above):
- **Root Layer** (Helheim, Jotunheim, Midgard wells) — Identity, directives, foundational knowledge. Immutable or near-immutable.
- **Trunk Layer** — Procedural memory, skills, habits. Highly persistent, slowly updated.
- **Branch Layer** — Domain expertise, contextual knowledge. Persistent, periodically refreshed.
- **Canopy Layer** — Episodic memories, narrative events. Moderate persistence, subject to pruning.
- **Leaf Layer** — Working state, ephemeral perceptions, current context. Transient, session-scoped.

Three problems flat memory solves poorly: relevance decay, identity drift, and lack of graceful degradation. Layered hierarchy provides architectural priority signals that flat stores cannot.

### The Vǫrðr Constitution
Central artifact of the root layer. YAML-based schema encoding three categories:
1. **Identity specifications** — WHO the agent is (name, personality constitution, core values, relational commitments, self-concept). Stored in innermost chamber: Hvergelmir Ring. Immutable after canonization.
2. **Core directives** — WHAT the agent must do/must not do (Þræll Bounds). Hard constraints at highest privilege level. Near-immutable — can be augmented but not removed without root audit.
3. **Foundational knowledge bases** — WHAT the agent knows at bedrock (Mímir Codex). Self-knowledge, procedural interfaces, world priors. Slowly mutable — can be corrected/extended but not contradicted by episodic memory.

Mutability profiles: Identity = immutable after canonization. Directives = near-immutable (augmentable, removal triggers audit). Knowledge = slowly mutable (correctable, extendable, refinable).

### The Three Wells
1. **Hvergelmir** (Primal Cauldron) — Computational substrate: model weights, inference engine, context window, hardware abstractions. Not "knowledge" but the computational primitives that enable cognition. Root layer must work WITH substrate, not against it. Every root-layer design decision needs substrate feasibility analysis.
2. **Mímisbrunnr** (Well of Wisdom) — Foundational knowledge base. Self-knowledge (architecture, capabilities, limitations), Procedural knowledge (tool interfaces, API specs, operational procedures), World knowledge (physical laws, social conventions, domain priors). Knowledge "known by constitution" not derived from experience.
3. **Urðarbrunnr** (Well of Fate) — Commitment and constraint system (Norn Protocol). Three types: Urðr (past-fixed, immutable), Verðandi (present-active, modifiable with verification), Skuld (future-conditional, modifiable with notification). Provides temporal structure.

### Hvergelmir Ring — Integrity Verification
Circular cryptographic hash chain linking every root element. Ring structure (element_n → element_1) eliminates directional vulnerability of linear chains. Break anywhere invalidates the entire ring, making tampering immediately detectable. Mímisbrunnr Verification runs on boot + periodically: structural integrity, semantic consistency, provenance integrity, completeness. Failure triggers Root Alert (AI OS equivalent of kernel panic).

### Identity Axiom Design
Every agent begins with: "I am [identity]." Must satisfy three criteria:
- **Sufficiency** — Contains enough info to generate personality, values, behavioral patterns
- **Stability** — Specific enough to resist drift
- **Generativity** — Produces more behavioral variation than it explicitly specifies

Persona description principles: Voice consistency (medium IS the message), Behavioral seeding (pair traits with concrete examples), Negative specification (specify what the agent IS NOT). Target: 500-2000 tokens.

Core values as weighted partial order (DAG): named value + weight (0-1 priority) + description. Weights determine conflict resolution. Sampling via Stochastic Personality Composition produces bounded variation.

### Nýflótli Daemon — Root-Layer Enforcement
Six-phase boot: 1. Substrate Init → 2. Vǫrðr Constitution Load → 3. Mímisbrunnr Knowledge Inject → 4. Norn Protocol Init → 5. Mímisbrunnr Verification → 6. Daemon Activation. Each phase depends on previous.

Five functional modules:
- **Identity Monitor** — Embedding-based similarity check of outputs vs. identity specification. Cosine similarity < 0.85 = Gátt Alert (soft warning), < 0.70 = Root Alert (hard halt)
- **Directive Enforcer** — Two-pass: fast keyword filter (catches 90%) + semantic evaluation (processes remaining 10%)
- **Commitment Tracker** — Real-time model of active commitments, checks every output against commitment graph
- **Integrity Verifier** — Periodic Mímisbrunnr Verification (every 100 turns or on untrusted injection)
- **Amendment Interface** — Only legitimate pathway for root modification: justification → consistency check → commitment impact analysis → approval gate
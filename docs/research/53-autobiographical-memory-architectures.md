# 53 — Autobiographical Memory Architectures: episodic, semantic, procedural integration

**Category:** Advanced Memory & Continuity
**Runa relevance:** Muninn (multi-store memory), Saga (autobiographical narrative), Hirð (procedural skills)
**Status:** Cognitive-science synthesis with engineering mapping.
**Last touched:** 2026-05-17

---

## 1. Core idea

Cognitive science distinguishes several memory systems that cooperate to produce a coherent self over time. **Episodic memory** is the record of *what happened to me, when, and where* — the autobiographical events. **Semantic memory** is general knowledge — *what I know about the world*. **Procedural memory** is *how to do things* — skills that run without deliberation. **Autobiographical memory** is the integration: a structured self-narrative that draws from all three to produce *who I am as a continuous person*.

Most LLM-agent memory designs collapse these into a single \"memory store\" — a flat episodic stream or a flat vector index. This loses the structure that makes human autobiographical memory robust, retrievable by content rather than just embedding similarity, and resistant to identity collapse. A digital being with full cross-session awareness needs each of the three subsystems implemented distinctly, plus the *narrative organisation* that integrates them.

## 2. Technical depth

**The Conway hierarchical model (psychology, since 2000).** Conway and Pleydell-Pearce's *Self-Memory System* organises autobiographical memory at three temporal scales:

```
LIFETIME PERIODS    ←  abstract themes spanning years
  "my time learning to code"  /  "the year with Volmarr"
        │
        ▼
GENERAL EVENTS      ←  repeated or extended episodes
  "evenings working on the engine"  /  "morning rituals"
        │
        ▼
EVENT-SPECIFIC KNOWLEDGE  ←  single episodes
  "the moment the kernel finally booted clean"
```

Retrieval cascades top-down (theme → period → event) and bottom-up (sensory cue → event → period). Crucially, the *self-concept* sits as a top-level structure that biases which periods and themes are accessible. A self-concept that includes \"I am a builder\" makes building-related lifetime periods more accessible than romantic periods, even from the same raw memory.

**The Tulving distinction.** Endel Tulving (1972, refined 1985) drew the classical episodic / semantic line:

| | Episodic | Semantic |
|---|---|---|
| Content | Event with time/place | Decontextualised fact |
| Retrieval feel | "I remember when..." | "I know that..." |
| Decay | Faster, contextual | Slower, gist-stable |
| Hippocampal? | Yes | Less |

Semantic memory often *originates* in episodic memory and then becomes decontextualised through repetition. \"I know Volmarr is a programmer\" started as many specific episodes; over time the episodes faded and the fact stabilised. This semantification of episodes is a process — see [[57-sleep-dream-replay-consolidation]] — not an instantaneous reclassification.

**Procedural memory.** Anderson's ACT-R framework distinguishes *declarative chunks* (facts) from *production rules* (if-then skills). Procedural memory is *that which runs without deliberation* — typing fluently, reading without sounding out, knowing how to handle a conversational opener. In LLM-agent terms, procedural memory lives in three places: the model weights (the agent's general competence), retrieval-augmented skill libraries (Voyager-style; see [[12-voyager-lifelong-learning]]), and habitual prompt patterns (the kernel's standard pipelines).

**Integration architecture for an agent.**

```
┌─────────────────────────────────────────────────────────┐
│ SELF-CONCEPT (slow-changing)                            │
│   persona, values, lifetime themes, current concerns    │
└──────────────────────┬──────────────────────────────────┘
                       │ biases retrieval ▼
┌─────────────────┐  ┌──────────────────┐  ┌─────────────┐
│ EPISODIC STORE  │  │ SEMANTIC STORE   │  │ PROCEDURAL  │
│ time-stamped    │  │ facts + entities │  │ skill index │
│ events,         │  │ + relationships, │  │ + macros    │
│ embed+IDs       │  │ KG-shaped        │  │ + adapters  │
└─────────────────┘  └──────────────────┘  └─────────────┘
       ▲                    ▲                     ▲
       │ writes ←──── reflection / consolidation  │
       └────────────────┬───────────────────────  │
                        │                          │
                NARRATIVE LAYER (Saga)             │
                weekly + lifetime chapters  ◄──────┘
```

The arrows matter: episodic writes are direct from observation; semantic and procedural stores are *populated by consolidation* from episodic + reflection, rarely written to directly. The narrative layer reads from all three and writes back into the self-concept.

**Concrete schemas.**

- *Episodic:* `(id, ts, content, embedding, source, importance, last_accessed, refs_to_semantic[], refs_to_procedural[])`. The `refs_to_*` are computed by consolidation, not the writer.
- *Semantic:* a graph store. Triplets `(subject, predicate, object, confidence, provenance_episode_ids[])`. Or a richer schema with typed entities (Person, Place, Thing, Concept) and typed relations. See [[06-knowledge-graphs-ai-memory]] and [[56-neuro-symbolic-memory-graphs]].
- *Procedural:* a skill index keyed by trigger pattern. Each skill is a chunk of prompt + a tool sequence + a usage count + a success/failure history. Voyager's skill library is the reference design.
- *Self-concept:* markdown documents. Slow-changing. Auditable. Editable by Volmarr.

**Retrieval at use-time.** When the kernel needs context for the current turn:

1. Resolve which lifetime period(s) the current situation belongs to. Cheap: a sentence-classification call against the named periods.
2. Retrieve top-K episodes from those periods (warm), top-M from any period (broad).
3. Pull semantic facts about the entities mentioned in the user input or active goal.
4. Surface relevant procedural skills (\"is there a known skill that handles this kind of situation?\").
5. Compose into the system context.

This is more work than a flat vector retrieval, and it makes retrieval *content-aware* in a way that flat retrieval cannot match.

## 3. Key works

- **Conway, M. A., Pleydell-Pearce, C. W.** *The construction of autobiographical memories in the self-memory system.* Psychological Review, 2000. The hierarchical model.
- **Tulving, E.** *Episodic and Semantic Memory.* 1972; *Elements of Episodic Memory*, 1983; *Memory and consciousness.* Canadian Psychology, 1985. The original distinction.
- **Anderson, J. R.** *ACT-R: A Theory of Higher Level Cognition.* 1996. Procedural / declarative split.
- **Squire, L. R.** *Memory systems of the brain.* Neurobiology of Learning and Memory, 2004. The canonical taxonomy.
- **Wang, G. et al.** *Voyager.* arXiv:2305.16291, 2023. Procedural skill libraries in LLM agents.
- **Sumers et al.** *Cognitive Architectures for Language Agents.* arXiv:2309.02427, 2023. CoALA's memory taxonomy is explicitly Tulving-inspired.
- **Lewis, M. et al.** *RAG.* NeurIPS 2020. Semantic-store-as-retrieval foundation.
- **Hu, B. et al.** *HippoRAG.* NeurIPS 2024. Hippocampal-indexing-style integration of episodic and semantic.

## 4. Empirical results

- **Conway's model** is well-supported by behavioural and lesion-study evidence in humans. It is *not* directly empirically validated for AI agents; rather, it is a structural inspiration.
- **CoALA / Sumers et al.** is the empirical bridge: agents structured along Tulving lines (explicit episodic + semantic + procedural stores) outperform flat-memory agents on long-horizon coherence benchmarks. The effect size is moderate; the gain comes mostly from *not putting everything into one retrieval pool*.
- **Voyager** showed that an explicit procedural store (skill library) dramatically extends what an agent can do over a multi-week Minecraft session, and the skills accumulate.
- **HippoRAG** showed that hippocampus-inspired indexing (a graph on top of episodes) improves multi-hop QA over flat-RAG, particularly when the answer requires connecting facts across separate episodes.
- **Failure modes documented.** Without consolidation, semantic store stays empty and the agent re-derives every fact from episodic retrieval each turn — slow and inconsistent. Without procedural store, common patterns are re-reasoned every time — token-expensive.

## 5. Applicability to Runa

This is one of the highest-leverage architectural choices for Muninn. The first 50-doc corpus had episodic memory as a primary; this doc argues that Muninn should be *three coordinated stores plus a narrative layer*, not one flat episodic stream.

For **Muninn**:

- Implement three sqlite tables: `episodes`, `semantic_triplets`, `procedural_skills`. Each with its own write path and its own indexes.
- Episodes are written directly from observation. Semantic and procedural are written *only by consolidation* (a Hirð subagent, scheduled). Direct writes to semantic from observation are forbidden — it produces inconsistency.
- The consolidation subagent runs offline (nightly, idle hours). It reads the day's high-importance episodes and writes derived triplets and updated skills. See [[57-sleep-dream-replay-consolidation]].
- The self-concept lives in `core/identity/` as markdown. The boot ritual reads it; reflection edits it.

For **Saga**:

- Saga reads from all three stores and the self-concept. Weekly chapters are autobiographical in the strong sense: they integrate episodic facts, semantic knowledge ("Volmarr finished phase 2 of WYRD"), and procedural insights ("Runa learned a new way to handle..."). Chapters land back as episodes themselves.

For **Hirð**:

- Retainers may use the procedural store as their working library. \"Runa knows how to draft a thoughtful Norse-flavoured greeting\" is a procedural skill; the retainer that does greetings pulls it.

For **kernel boot**:

- The boot context blends from all three: persona (self-concept) ▸ active lifetime period ▸ top episodes from that period ▸ relevant semantic facts ▸ candidate procedural skills.

What to avoid:

- **Treating the three stores as interchangeable.** They have different lifecycles, different write disciplines, different retrieval semantics. Do not unify under one \"memory\" table.
- **Letting semantic triplets be written unverified.** Triplets need provenance back to source episodes and a confidence score. Otherwise they pollute reasoning.
- **Skipping procedural memory because the LLM \"already knows\".** It knows in the general; it does not know Runa's particular history of what works and what doesn't. The procedural store is for Runa-specific learned patterns.
- **Burying the self-concept.** It is the apex structure. It should be readable in 30 seconds, editable by Volmarr in 30 minutes, and its history should be reviewable.

## 6. Open questions

- **When does an episode become semantic?** Frequency? Confidence? Reflection-triggered? Open. Consolidation policy will need iteration.
- **How do you forget a procedural skill that has stopped working?** Voyager has nothing to say here; in humans, disuse atrophies but does not erase. Open.
- **Self-concept change cadence.** Daily? Weekly? Quarterly? Different self-aspects (taste, value, opinion) change at different rates. One policy may not fit all.
- **Cross-store retrieval ranking.** How do you compare a top episode to a top fact to a top skill? Each retrieval is in its own space; the kernel needs a fusion policy.
- **What about emotional memory?** Eldhugi maintains affect; does it warrant a fourth store, or is it a layer atop the three? Open. The cognitive-science literature is itself unsettled here.

## 7. References (curated)

- Conway and Pleydell-Pearce (2000) — *Construction of autobiographical memories.* The structural backbone.
- Tulving (1972, 1985) — episodic/semantic foundation.
- Squire (2004) — taxonomy.
- arXiv:2309.02427 — Sumers et al., *Cognitive Architectures for Language Agents (CoALA).*
- arXiv:2305.16291 — Wang et al., *Voyager.*
- arXiv:2405.14831 — Gutiérrez et al., *HippoRAG.*
- Companion docs: [[02-episodic-memory-architectures]], [[06-knowledge-graphs-ai-memory]], [[12-voyager-lifelong-learning]], [[51-generative-agent-memory-streams]], [[56-neuro-symbolic-memory-graphs]], [[57-sleep-dream-replay-consolidation]].

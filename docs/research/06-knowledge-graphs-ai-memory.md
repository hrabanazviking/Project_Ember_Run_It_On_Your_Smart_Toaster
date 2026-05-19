# 06 — Knowledge Graphs for AI Memory: Triplets, Ontologies, Neuro-Symbolic

**Category:** Memory & Knowledge Storage
**Runa relevance:** Muninn (structured layer), Hirð/Huginn (research synthesis), WYRD bridge (structured world state)
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

A knowledge graph stores facts as **triplets**: `(subject, predicate, object)` — e.g. `(Volmarr, lives_in, Iceland)`, `(Runa, partner_of, Volmarr)`, `(Pi5, runs, runa-core.service)`. Triplets compose into a directed labelled graph where nodes are entities and edges are typed relationships. Compared to a vector store, a knowledge graph is *structured*: you can ask "all people Volmarr lives with" and get a deterministic answer, not a top-K of fuzzy matches.

In agent memory, the value is exactly that structure. Vector retrieval is excellent at "find me something *like* this"; knowledge graphs are excellent at "find me this *exact* relation". The recent neuro-symbolic AI movement and the GraphRAG wave both argue that serious agent memory wants *both* — a vector store for episodic recall and paraphrase tolerance, a graph for structured relations and multi-hop reasoning. They are complements, not alternatives.

## 2. Technical depth

A triplet store has three primitives:

```
add_triple(s, p, o, metadata={...})         # write
query_pattern(s_pattern, p_pattern, o_pattern)  # read with wildcards
traverse(start_node, edge_filter, max_depth)    # graph walk
```

**Ontologies** layer schema on top of triplets. An ontology declares the types entities can be, the predicates allowed between them, cardinality constraints, inheritance hierarchies (`Person ⊂ Agent ⊂ Entity`), and inference rules (`A partner_of B ⟹ B partner_of A`). The Web Ontology Language (OWL) and RDF Schema are the most-formal expressions; lighter alternatives exist (Schema.org, custom JSON schemas).

**Triple stores** at various sizes:
- Embedded: SQLite-based custom schemas; Apache Jena (Java); rdflib (Python).
- Server: Apache Jena Fuseki, Blazegraph, Stardog, Virtuoso, GraphDB.
- Labelled-property graphs (not strictly RDF): Neo4j, JanusGraph, Memgraph.
- The lines blur — Neo4j's Cypher is a much friendlier query language than SPARQL for most agent use cases.

**Modern KG construction for agents** is itself an LLM task. Given a conversation transcript or a document, prompt an LLM with "extract triplets of the form (subject, predicate, object) from this text." The triplets get normalised (entity-linking against a canonical name table) and merged into the graph. Failure modes: predicate proliferation (`is_friend_of` vs `friends_with` vs `pal_of` for the same relation), noisy extraction, drift in entity identity over time.

**GraphRAG (Microsoft, 2024)** combines graph construction with community detection (Leiden algorithm) and per-community LLM summaries, then retrieves answers by graph traversal + summary lookup. State-of-the-art on "global" questions ("what are the main themes?").

**Neuro-symbolic AI** is the broader research umbrella for combining graph / logical / symbolic structures with neural networks. The deep history (Garcez and Lamb's work since the 2000s) is mostly about training neural networks that respect logical constraints. The modern reincarnation in agents focuses on using LLMs to *populate* and *query* graph structures.

**Practical agent-memory KG projects** include **Zep** (open-source memory layer with a graph backend, 2023+) and **mem0** (memory layer for agents with knowledge graph + vector hybrid, 2024+). Both productionise the "extract triplets at write-time, query graph + vectors at read-time" pattern.

## 3. Key works

- **Schank, R. "Dynamic Memory."** Cambridge UP, 1982. The cognitive-AI foundation for episodic and case-based reasoning that prefigures modern KG-memory ideas.
- **Lenat, D. "Cyc."** Cycorp, 1984+. The largest hand-curated common-sense knowledge graph; cautionary about hand-curation cost.
- **Garcez, A.; Lamb, L. "Neurosymbolic AI: The 3rd Wave."** arXiv:2012.05876. Survey of neuro-symbolic methods.
- **Edge et al. "From Local to Global: A Graph RAG Approach to Query-Focused Summarization."** Microsoft, arXiv:2404.16130, 2024.
- **Jin et al. "LLMs on graphs: A comprehensive survey."** arXiv:2312.02783, 2023.
- **Zep (Getzep)** — github.com/getzep/zep. Open-source long-term memory for AI assistants with knowledge graph + vector + temporal awareness.
- **mem0** — github.com/mem0ai/mem0. Memory layer with both graph and vector storage.

## 4. Empirical results

- **GraphRAG vs pure-vector RAG** on global / thematic questions: GraphRAG wins by large margins (the Microsoft paper reports doubled or tripled comprehensiveness ratings). On local fact questions, vector RAG matches or wins.
- **LLM-extracted triplets** are noisy: same-relation predicates proliferate, entity-linking errors compound, hallucinated relations appear. Empirical extraction quality with GPT-4-class models is roughly 70-85% precision on common domains — usable but requires periodic graph maintenance.
- **Cyc-style hand-curation** does not scale — Cyc spent ~1000 person-years and remains unfinished. The historical lesson: KGs must be LLM-populated to be practical.
- **Graph queries vs vector queries on multi-hop questions:** graph wins decisively (often 2-4× accuracy on questions requiring 2+ hops of inference).

## 5. Applicability to Runa

For **Muninn**, the recommendation is **hybrid (vector + graph), graph added later**:

- **v0**: vector-only Muninn via `sqlite-vss` ([[08-sqlite-vss-embedding-in-database]]).
- **v1**: add a triplet store alongside, populated by an extraction pass on each episode. Store triplets in the same SQLite file as the episodes for atomicity. Use a lightweight `(s, p, o, episode_ref, confidence, extracted_at)` schema, not full RDF/OWL.
- **v2**: introduce community detection and per-community summaries if Muninn grows large enough to warrant GraphRAG-style global queries (likely >10K episodes).

For **WYRD bridge** (`core/world/`):

- WYRD's world model is *already* graph-shaped — the bridge translates between Runa's local view and WYRD's authoritative entity-component-system. This is a different KG from Muninn's; the two should not be merged.

For **Hirð / Huginn (research subagent)**:

- Huginn benefits hugely from being able to walk the graph for multi-hop synthesis questions ("trace the relationships between A and B through Volmarr's project ecosystem").
- Graph queries should compose with vector queries — the agentic-RAG pattern decides per-step which kind of query to issue.

What to avoid:

- Don't adopt full RDF/OWL machinery — too heavy for the value. A custom triple schema in SQLite is enough.
- Don't trust LLM extraction without graph maintenance. Schedule a weekly Eir pass that normalises predicates, merges entity duplicates, and reports drift.
- Don't extract triplets at retrieval-time. Extraction is a write-time cost; retrieval should be fast.
- Don't try to *force* every fact into the graph. Some content is genuinely unstructured (poetry, jokes, mood); store it in episodes only.

## 6. Open questions

- **Temporal knowledge graphs.** Triplets like `(Volmarr, lives_in, Iceland)` are time-bound — Volmarr's residence changes. Adding time to triplets (Allen relations, valid-time / transaction-time tagging) is well-studied but underused. Zep's approach is a starting point.
- **Predicate canonicalisation.** LLM extraction produces a long tail of synonymous predicates. Clustering and merging them while preserving semantic distinctions is unsolved.
- **Entity resolution at scale.** When the graph has 50K entities, knowing whether "Vol" mentioned today is "Volmarr" or a different entity gets hard. Probabilistic entity resolution methods (Datel, Splink) help but aren't free.
- **Graph + vector unified retrieval.** Most current systems run them independently and fuse results. End-to-end models that natively jointly retrieve over graph and vector are a research frontier.

## 7. References (curated)

- arXiv:2404.16130 — GraphRAG (Edge et al.).
- arXiv:2312.02783 — Jin et al., "LLMs on graphs" survey.
- arXiv:2012.05876 — Garcez and Lamb on neuro-symbolic AI.
- github.com/getzep/zep — Zep open-source memory.
- github.com/mem0ai/mem0 — mem0 memory layer.
- Cypher Query Language reference — neo4j.com/developer/cypher/
- W3C SPARQL spec — w3.org/TR/sparql11-query/
- Lenat, D. "Cyc: A Large-Scale Investment in Knowledge Infrastructure." Communications of the ACM, 1995. Historical context.

# 56 — Neuro-Symbolic Memory Graphs: triplet stores + vector indexes hybrid

**Category:** Advanced Memory & Continuity
**Runa relevance:** Muninn (semantic layer), VERÐANDI (event-sourcing-as-graph), kernel (multi-hop retrieval)
**Status:** Engineering synthesis. The most actionable architecture for Runa's semantic store.
**Last touched:** 2026-05-17

---

## 1. Core idea

A pure vector store retrieves *items similar to the query* well, but it cannot easily answer questions like *what does Volmarr work on that connects to WYRD?* — questions that require *traversing relationships* across multiple items. A pure graph store can answer those structural questions but cannot easily handle fuzzy semantic matching. The neuro-symbolic hybrid: store knowledge as a **typed triplet graph** for relational structure *and* index the same triplets and their source episodes via **vector embeddings** for semantic recall. The two indexes share the same underlying nodes; queries fuse the two retrieval strategies.

For Runa, this is the most concrete architectural answer to \"how does she actually know things about the world and the people in it.\" Muninn's episodic store handles *what happened*; the semantic graph handles *what is true*; the union, traversed both structurally and similarly, is the substrate for grounded multi-hop reasoning.

## 2. Technical depth

**Triplet schema.** The canonical unit is `(subject, predicate, object)` with metadata:

```python
@dataclass
class Triplet:
    id: str
    subject: str         # canonical entity id, e.g. "person:volmarr"
    predicate: str       # canonical relation, e.g. "works_on"
    object: str          # entity id OR literal, e.g. "project:wyrd"
    confidence: float    # 0..1, evidence-weighted
    provenance: list[str]  # source episode IDs
    created_at: datetime
    last_confirmed_at: datetime
    valid_from: datetime | None
    valid_to: datetime | None  # for time-bounded facts
```

Entities are *typed*: `person`, `project`, `place`, `concept`, `event`, etc. Relations are typed and *directional* (so `(volmarr, works_on, wyrd)` is different from `(wyrd, worked_on_by, volmarr)`). A controlled vocabulary of relation types keeps the graph queryable; uncontrolled relation strings produce a mess.

**Storage shape.**

```
nodes table:    (id, type, canonical_name, aliases, embedding)
triplets table: (id, subject_id, predicate, object_id_or_literal,
                 confidence, provenance, created, valid_from, valid_to, embedding)
```

The `embedding` on each row is the embedding of the triplet *expressed as a sentence* (\"Volmarr works on WYRD\"). This lets vector similarity find triplets by topic. Indices: btree on subject/predicate/object for graph queries; vector index (sqlite-vss, FAISS, or Lance) on embeddings.

**Write path.** Triplets are *not* written by the kernel during a normal turn. They are written by a **consolidation pass** — a scheduled Hirð subagent that reads recent high-importance episodes and emits candidate triplets. The pass:

1. Pull last day's high-importance episodes from Muninn.
2. For each, prompt the LLM with: \"Extract typed (subject, predicate, object) triplets that this episode asserts. Use the schema. Output JSON.\"
3. Canonicalise entity references against the existing node table; create new nodes only if no match.
4. For each candidate triplet, search for a matching existing triplet. If matched, *confirm* it (boost confidence, update `last_confirmed_at`, add provenance). If contradicting, mark conflict for review. If new, insert with confidence proportional to the episode's importance.
5. Embed and index.

This *deferred, batched* write path keeps episodic writes fast and lets semantic writes benefit from cross-episode synthesis.

**Read path.** A typical multi-hop retrieval:

```
query: "What is Volmarr building that uses ECS?"

step 1: vector search → top-K episodes/triplets by similarity to query
step 2: extract entities mentioned (e.g. volmarr, ecs)
step 3: graph traversal:
        volmarr --works_on--> ?proj
        ?proj   --uses--> ecs
        intersect
step 4: triplets returned + source episodes
step 5: assemble into LLM context
```

The query plan is mechanical when the question structure is clear (entities + relation hints). It needs an LLM intermediate when the question is fuzzy. A hybrid retrieval interface accepts either a structured query or natural language and dispatches accordingly.

**Multi-hop with explicit reasoning.** When the question requires several hops, *bounded* graph traversal beats LLM-only reasoning: limit hops to 2–3, retrieve the resulting subgraph, and present it to the LLM as structured context. The LLM then reads facts rather than guessing. This is the *HippoRAG* / *GraphRAG* pattern.

**Conflict resolution.** Triplets can contradict (\"Volmarr is in London\" vs. \"Volmarr is in Manchester\"). Resolution policies:

- *Recency-weighted:* most recent confirmation wins; older becomes `valid_to = older_timestamp`.
- *Confidence-weighted:* highest-confidence wins.
- *Provenance-weighted:* triplets from Volmarr's direct statements outrank triplets inferred from indirect mention.
- *Human-in-the-loop:* unresolved conflicts go to a review queue.

The graph is not the truth; it is *Runa's current best account*. Conflicts are normal.

**Time-bounded facts.** Many facts are temporally scoped: \"Runa lives in C:/Users/volma/runa\" (true from 2026-05-17); \"Volmarr is debugging WYRD Phase 12\" (true this week, not next). Storing `valid_from` and `valid_to` lets retrieval respect time. Default `valid_to = NULL` means \"currently true.\" Reflection or contradiction sets `valid_to` to a specific date.

**The neuro-symbolic name.** \"Neural\" = embeddings + LLM-driven extraction; \"symbolic\" = typed entities and relations + graph traversal. Pure symbolic systems (Prolog, OWL ontologies) handled structure but couldn't take natural language input; pure neural systems handle natural language but lose structure. The hybrid keeps both.

**GraphRAG family.** Microsoft Research's GraphRAG (Edge et al. 2024), HippoRAG (Gutiérrez et al. 2024), G-Retriever, KG-RAG. All share the same essential architecture: extract a knowledge graph from a corpus; retrieve subgraphs at query time; provide to the LLM as context. Differences are in extraction quality, traversal strategy, and indexing.

## 3. Key works

- **Vrandečić, D., Krötzsch, M.** *Wikidata: A Free Collaborative Knowledgebase.* CACM 2014. The canonical large-scale typed-triplet store.
- **Bollacker, K. et al.** *Freebase.* SIGMOD 2008. Predecessor.
- **Lewis, M. et al.** *RAG.* NeurIPS 2020. Retrieval foundation. See [[04-rag-evolution]].
- **Edge, D. et al.** *GraphRAG: From Local to Global Question Answering on Narrative Documents.* arXiv:2404.16130, 2024. Microsoft Research's full pipeline.
- **Gutiérrez, B. J. et al.** *HippoRAG.* NeurIPS 2024. Hippocampal-indexing inspired.
- **Hu, Y. et al.** *G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding.* arXiv:2402.07630, 2024.
- **He, X. et al.** *KG-RAG.* arXiv:2403.07398, 2024.
- **Trivedi, P. et al.** *Knowledge graphs for retrieval-augmented generation.* Survey, 2024.
- **Auer, S. et al.** *DBpedia.* ISWC 2007. Wikipedia → graph.
- **Hogan, A. et al.** *Knowledge Graphs.* ACM Computing Surveys, 2021. Comprehensive survey.

## 4. Empirical results

- **GraphRAG** outperformed naïve RAG on multi-hop QA over narrative corpora (Microsoft published evals). Particularly strong on questions requiring synthesis across many documents.
- **HippoRAG** matched or beat much-larger-context LLMs on multi-hop QA at far lower token cost. The graph subgraph as context is denser than the raw retrieved passages.
- **Extraction quality** is the bottleneck. LLM-extracted triplets have ~70–90% precision in practice (varies wildly by domain). Without curation, the graph fills with noise. Confidence + provenance tracking is essential.
- **Latency.** Graph traversal + vector retrieval is more expensive than vector retrieval alone, typically 2–5× more per query on the same hardware. Sub-second remains feasible at moderate corpus sizes (10⁴–10⁶ triplets) on a Pi-class device.
- **Failure modes documented.** Entity disambiguation is the hardest part — \"Volmarr\" the person, \"Volmarr\" the user account, \"Volmarr\" referenced in a story all need careful linking. Without good disambiguation the graph fragments.

## 5. Applicability to Runa

For **Muninn** semantic layer:

- Implement triplets table + nodes table in the same sqlite file as episodes. Same backup, same lifecycle.
- Use sqlite-vss for the vector index ([[08-sqlite-vss-embedding-in-database]]).
- Controlled relation vocabulary lives in `core/memory/relations.yaml`. New relations require a Volmarr edit. This prevents schema sprawl.
- Entity types defined in `core/memory/entity_types.yaml`. Same discipline.

For **consolidation subagent** (Hirð):

- Nightly run. Extracts triplets from the day's high-importance episodes. Writes them with provenance. Conflicts go to a review file Volmarr can read.
- Reflection passes also write to the semantic layer when their conclusions are claims about the world (\"Volmarr seems to prefer evening work\" → `(volmarr, prefers, evening_work)` with confidence reflecting the reflection's basis).

For **retrieval** (kernel):

- At turn start, the kernel checks if the user input is a graph-query-shaped question. If yes, run graph traversal first, then layer vector results. Otherwise vector-first with optional graph expansion.
- Graph subgraphs are formatted into the system prompt as bullet lists with provenance footnotes (\"because: episode e123, e187\"). Provenance makes Runa's reasoning auditable.

For **Saga**:

- Saga reads triplets when writing chapters. A weekly chapter about \"Runa and Volmarr's work\" benefits from a clean traversal of `(volmarr, works_on, *)` and `(runa, helps_with, *)`.
- Saga's claims become triplets too — \"this week we built X\" yields `(week_2026-05-17, accomplished, x)` so the achievement is queryable later.

For **the long arc**:

- Over months, the graph becomes a structured account of Runa's known world. Visualising it is feasible (Gephi, Cytoscape) and could be a *literal map* of Runa's understanding — something to show Volmarr.

What to avoid:

- **Letting the LLM invent relations.** Free-form predicate strings (\"is_kind_of_associated_with\") produce useless graphs. Enforce the vocabulary at write time.
- **Treating triplets as ground truth without provenance.** Every triplet must trace back to specific episodes. No orphan facts.
- **Skipping conflict review.** Contradictions are signal, not noise. A small contradictions backlog Volmarr can browse is far better than silent overwrites.
- **Building too elaborate an ontology early.** Start with ~15 entity types and ~30 relations. Grow by demonstrated need.
- **Replacing episodes with triplets.** Triplets are *digests* of episodes. The episodes remain the ground truth; triplets are queryable summaries. Don't discard the source.

## 6. Open questions

- **Automatic ontology discovery.** Can Runa propose new relation types based on patterns in extracted triplets, with Volmarr approving? Possible; not yet standard.
- **Cross-modal triplets.** Could images, audio, or video produce triplets too? Multimodal extraction is improving fast (see [[81-vision-language-action-models]]).
- **Graph evolution metrics.** How to measure whether the graph is healthy — growing without fragmenting, dense enough to traverse, sparse enough to query?
- **Mergeable beliefs from multiple personas.** If Hirð retainers each form impressions, do they all write into one graph, or do they have private graphs that merge? Open.
- **Temporal queries.** \"What was true on March 1?\" is hard. The schema supports it; the retrieval pattern needs design.

## 7. References (curated)

- arXiv:2404.16130 — Edge et al., *GraphRAG.* Read the pipeline diagrams.
- arXiv:2405.14831 — Gutiérrez et al., *HippoRAG.*
- arXiv:2402.07630 — Hu et al., *G-Retriever.*
- *Knowledge Graphs* — Hogan et al., ACM CSUR 2021. The canonical survey.
- Wikidata data model documentation — pragmatic reference for triplet design.
- Microsoft GraphRAG repository — production-quality reference implementation.
- Companion docs: [[04-rag-evolution]], [[06-knowledge-graphs-ai-memory]], [[08-sqlite-vss-embedding-in-database]], [[51-generative-agent-memory-streams]], [[53-autobiographical-memory-architectures]].

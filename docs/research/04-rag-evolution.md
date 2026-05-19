# 04 — RAG Evolution: Classic, Hybrid, GraphRAG, Agentic RAG

**Category:** Memory & Knowledge Storage
**Runa relevance:** Muninn (retrieval), kernel (turn composition), Hirð (Huginn the researcher)
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

Retrieval-Augmented Generation: at inference time, *retrieve* relevant text from a corpus, *augment* the prompt with it, then *generate*. The original 2020 RAG paper (Lewis et al., Facebook) treated retrieval as a single, fixed component bolted in front of an encoder-decoder. Five years later, "RAG" is an umbrella for an entire stack of techniques — hybrid retrieval (dense + sparse), graph-based retrieval, multi-hop retrieval, agentic retrieval where the LLM decides what to look up next, query rewriting, hypothetical document embeddings, contextual chunk prefixes, reranking, and post-retrieval compression.

For an agent like Runa with both an episodic memory (Muninn) and access to external documents (skill outputs, web fetches, MCP servers), every read from any store is, at the architectural level, a RAG operation. The state-of-the-art in 2025 is no single technique but a *retrieval pipeline* with multiple stages, each handling a different failure mode.

## 2. Technical depth

A modern RAG pipeline:

```
   user query
      │
      ▼
┌──────────────────┐
│ query rewriting  │  (HyDE, query decomposition, query expansion)
└────────┬─────────┘
         │
         ▼
┌────────────────────────────────────────────────────┐
│   retrieval (parallel)                             │
│   ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│   │ dense       │  │ sparse      │  │ graph      │ │
│   │ (embed +    │  │ (BM25 /     │  │ (entity →  │ │
│   │  vector ANN)│  │  SPLADE)    │  │  triples)  │ │
│   └──────┬──────┘  └──────┬──────┘  └─────┬──────┘ │
└──────────┼─────────────────┼────────────────┼──────┘
           └────────fusion────┴────────────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ reranking         │  (cross-encoder, monoT5, ColBERT)
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ context selection │  (top-k, MMR for diversity)
                └─────────┬─────────┘
                          │
                          ▼
                ┌───────────────────┐
                │ prompt assembly   │  (with provenance markers)
                └─────────┬─────────┘
                          │
                          ▼
                         LLM
```

**Hybrid retrieval (dense + sparse).** Dense (embedding-based) retrieval handles paraphrase well but stumbles on exact-keyword recall (proper nouns, code identifiers, rare terms). Sparse (BM25, SPLADE) handles exact matches and the long tail. Running both and fusing scores (typically reciprocal rank fusion) improves robustness meaningfully — usually 5-15% on retrieval benchmarks. Recommended for *any* serious RAG system.

**HyDE (Hypothetical Document Embeddings).** Gao et al., 2022. Instead of embedding the user's query (often short and underspecified), have the LLM generate a hypothetical answer first, embed *that*, and search. Improves recall on hard queries where the query and the answer-document have low surface overlap. Trade-off: doubles inference cost.

**Late chunking.** Günther et al. (Jina), 2024. Embed long documents as a whole, then chunk *the embedding sequence*, not the text. Preserves cross-chunk context (e.g. the antecedent of a pronoun in chunk 3 was named in chunk 1). Requires long-context embedding models.

**Contextual retrieval.** Anthropic, late 2024. Before embedding a chunk, prepend a brief LLM-generated context (50-100 tokens) explaining what the chunk is about within the larger document. Reported 35-49% reduction in retrieval failures on benchmark queries. Cost: one cheap LLM call per chunk at indexing time.

**GraphRAG.** Microsoft, 2024. Build a knowledge graph from the corpus (entities + relations + community summaries), retrieve via graph traversal for queries that span entities. Outperforms vector-only retrieval on multi-hop and global-thematic queries; worse on local-factual.

**Agentic RAG.** The LLM decides what to retrieve, when, and from where. May issue multiple queries in sequence, each informed by the previous result. Overlaps with ReAct ([[09-react-reasoning-acting]]) and the Hirð pattern: a researcher subagent (Huginn) iterates retrievals until satisfied.

**Reranking.** First-stage retrieval gives 50-200 candidates. A cross-encoder reranker (Cohere Rerank, monoT5, ColBERT) scores each candidate against the query directly, more accurate but expensive. Typical: retrieve 100, rerank to top 10, prompt with top 5.

## 3. Key works

- **Lewis et al. "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks."** Facebook AI, NeurIPS 2020. The canonical paper.
- **REALM (Guu et al., Google, 2020)** — earlier contemporaneous work that conditioned MLM pretraining on retrieved documents.
- **HyDE — Gao et al., arXiv:2212.10496.**
- **GraphRAG — Edge et al., Microsoft, arXiv:2404.16130, 2024.**
- **Contextual Retrieval** — Anthropic engineering blog, September 2024.
- **Late Chunking — Günther et al., Jina AI, 2024.**
- **RAGAS (RAG Assessment) — Es et al., arXiv:2309.15217** — the evaluation framework that became a standard.
- **Self-RAG (Asai et al., arXiv:2310.11511)** — LLM with self-reflection tokens that decide whether to retrieve.
- **CRAG (Corrective RAG, Yan et al., arXiv:2401.15884)** — judges retrieval quality and corrects.

## 4. Empirical results

- Naive RAG (embed-and-retrieve top-5) improves QA accuracy 10-30% over no-retrieval baselines, varying by task. The gains are largest on knowledge-intensive open-domain QA, smallest on reasoning-heavy tasks.
- Hybrid (dense + BM25 + RRF) consistently beats either alone by 3-10 points on BEIR.
- Reranking adds another 2-8 points on top of hybrid.
- HyDE adds 2-5 points on hard queries with low surface overlap; sometimes hurts on easy queries (over-thinking).
- GraphRAG's biggest published win: 70-80% better performance on "global" questions like "what are the main themes in this corpus" where vector retrieval has no good answer.
- Contextual retrieval (Anthropic) reported 35-49% reduction in failed retrievals on their internal benchmarks.
- Long-context models that ingest the entire corpus close some of the gap (see [[05-long-context-vs-retrieval]]) but at much higher token cost.

## 5. Applicability to Runa

For **Muninn retrieval** (D-2.2):

- **Start with hybrid** — `sqlite-vss` for dense + SQLite FTS5 for sparse, RRF for fusion. Easy to add on top of the chosen storage backend.
- **Add reranking later** when query volume justifies a cross-encoder. Pi-affordable rerankers exist (`bge-reranker-base`, `mxbai-rerank-base`).
- **Contextual prefixing** is a low-cost high-impact win: when storing an episode, ask Heimskringla for a 1-sentence "what is this episode about" prefix, embed the prefix alongside the episode. The cost is one cheap model call per episode, paid at write-time when latency is invisible to Volmarr.

For **Hirð / Huginn** (the research subagent):

- Huginn implements *agentic RAG* — given a research goal, plan a sequence of retrievals across Muninn + external sources (web via Smiðja, MCP servers), iterate until evidence is sufficient or budget exhausted, produce a synthesised answer with provenance.
- The Self-RAG self-reflection-token pattern is a model-internal precedent for what Huginn does at the orchestration level.

For **GraphRAG**:

- Likely not in v0. Build vector retrieval first; introduce a graph layer once Muninn has enough volume (>10K episodes) and the queries naturally split into local-factual vs global-thematic.

What to avoid:

- Don't retrieve unconditionally. Self-RAG and CRAG both demonstrate that retrieval *can hurt* on queries the model already knows the answer to. Cost: noise injection. Mitigation: a cheap "do I need to retrieve" classifier or LLM judgement.
- Don't return raw chunks to the LLM without provenance markers. Every retrieved span should carry "[Muninn episode 2026-04-12 14:32]" or similar so the LLM (and the human reading transcripts later) knows where the fact came from. This is also the substrate for citation in Runa's replies.
- Don't tune retrieval thresholds against a tiny eval set. RAGAS or a Runa-specific eval set with at least 200 queries is the minimum.

## 6. Open questions

- **Long-context vs RAG vs both.** See [[05-long-context-vs-retrieval]]. The boundary keeps moving.
- **Multi-hop with verification.** Iterative retrieval with self-verification at each hop is still brittle; common failure is *answer drift* across hops.
- **Cross-modal retrieval.** Muninn might want to retrieve voice clips, screenshots, or other modalities by query — joint embedding spaces (SigLIP descendants) are the active research direction.
- **Retrieval over private agent memory.** RAG benchmarks are almost all over public corpora. Performance on private-conversation corpora (where vocabulary is idiosyncratic) is underexplored.

## 7. References (curated)

- arXiv:2005.11401 — Original RAG paper (Lewis et al.).
- arXiv:2002.08909 — REALM.
- arXiv:2212.10496 — HyDE.
- arXiv:2404.16130 — GraphRAG (Microsoft).
- arXiv:2310.11511 — Self-RAG.
- arXiv:2401.15884 — CRAG.
- arXiv:2309.15217 — RAGAS.
- anthropic.com/news/contextual-retrieval — Anthropic's blog on contextual retrieval.
- jina.ai/news/late-chunking — Jina blog on late chunking.

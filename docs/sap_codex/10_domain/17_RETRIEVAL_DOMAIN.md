---
codex_id: 17_RETRIEVAL_DOMAIN
title: Retrieval Domain — BM25, FAISS, MiniLM, and the Hybrid Compromise
role: Architect
layer: Domain
status: draft
sap_source_refs:
  - py/know_base.py:1-391
  - py/minilm_router.py:1-189
  - py/ebd_api.py:1-50
  - py/ebd_model_manager.py:1-180
  - py/load_files.py:1-100
ember_subsystem_targets: [Brunnr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 20_interface/2B_RETRIEVAL_INTERFACE
  - 60_synthesis/60_TRUE_NAME_REASSIGNMENT
---

# Retrieval Domain
## BM25, FAISS, MiniLM, and the Hybrid Compromise

*— Rúnhild Svartdóttir, Architect*

> *Knowledge that you cannot reach is not knowledge; it is decoration. Knowledge that you can only reach with one tool is brittle. Knowledge that you can reach with two tools, weighted by the question, is what we used to call a library.*

The retrieval domain in SAP is — once you forgive its absent abstractions — *the most theoretically respectable subsystem* in the codebase. It is a hybrid BM25 + FAISS retriever over per-KB document corpora, with a configurable rank-blend weight, a local MiniLM ONNX embedding server, and a pluggable reranker. The design is the right shape; the integration is what cracks.

---

## 1. The Subject Itself

**What the domain owns:** the per-knowledge-base document corpus, the hybrid BM25 + vector index, the local MiniLM embedding server, the reranker invocation, the OpenAI-compatible embedding probe (`/api/embedding_dims`).

**What it does *not* own:**
- The long-term conversation memory (that's `mem0` / in-server)
- The affection state (that's [[1A_AFFECTION_DOMAIN]], such as it is)
- The skill / extension knowledge (that's [[18_EXTENSION_DOMAIN]])
- The session conversation history (that's `COVS_PATH` SQLite in `get_setting`)

**Where it lives:**

| File | LOC | Owns |
|---|---|---|
| `py/know_base.py` | 390 | Hybrid BM25+FAISS index, build/query/rerank, langchain integration |
| `py/minilm_router.py` | 188 | Local MiniLM ONNX embedding server, `/minilm/embeddings` route |
| `py/ebd_api.py` | 49 | Probe a remote embedding API for output dimensions |
| `py/ebd_model_manager.py` | 179 | Embedding model download + lifecycle |
| `py/load_files.py` | 752 | Multi-format document ingest (MD, JSON, JSONL, YAML, TXT, CSV, PDF, HTML, code) |

Roughly 1,500 LOC. The shape is: *load → chunk → index (BM25 + vector) → query → rerank → return*.

---

## 2. How It Works

### 2.1 The langchain stack

`py/know_base.py:1-15` imports `langchain_core`, `langchain_text_splitters`, `langchain_classic` (the ensemble retriever), `langchain_community.retrievers.BM25Retriever`, and `langchain_community.vectorstores.FAISS`. SAP rides langchain for the retriever plumbing — pragmatic, since these are well-tested. It does not, however, ride langchain for tool dispatch, conversation management, or memory. The retrieval-only langchain bet keeps the dependency surface bounded.

### 2.2 The custom embeddings client

`MyOpenAICompatibleEmbeddings` (`py/know_base.py:38-89`) is a langchain `Embeddings` subclass that speaks OpenAI's embedding API shape via `httpx.AsyncClient`. It exposes both sync (`embed_query`, `embed_documents`) and async (`aembed_query`, `aembed_documents`) methods. The sync versions delegate to async via `asyncio.run` — a known footgun if called from within an existing loop, but acceptable because langchain's sync interface is the path-of-last-resort.

The class handles two error shapes (`py/know_base.py:67-71`):

```python
except httpx.HTTPStatusError as e:
    detail = e.response.json().get('detail', e.response.text) if e.response.text else 'Unknown error'
    raise RuntimeError(f"Embedding API HTTP Error {e.response.status_code}: {detail}")
except Exception as e:
    raise ConnectionError(f"Embedding API connection failed: {e.__class__.__name__}: {e}")
```

Named exceptions, named reasons. The same shape would benefit `py/mcp_clients.py:159-167` (where `call_tool` failures are stringified).

### 2.3 Unicode-surrogate cleansing

`clean_text` (`py/know_base.py:27-35`) strips invalid Unicode surrogates from input before chunking or storing:

```python
def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return str(text)
    return text.encode('utf-8', 'ignore').decode('utf-8')
```

The comment names the specific failure mode: `'utf-8' codec can't encode character ... surrogates not allowed`. This is the kind of bug a system encounters only at scale — surrogate pairs leak in from copy-paste, from emoji handling, from misencoded source files. SAP has met this bug; SAP has fixed it. Quietly.

### 2.4 The hybrid index build

`build_vector_store` (`py/know_base.py:117-194`) builds *both* indices independently, with explicit fault tolerance:

- **BM25 path** (lines 128-164): clean each document, serialize to JSON at `<kb_dir>/bm25_index.json`. If anything fails, log a warning, try to delete the corrupt file, **proceed** to the vector path. The Vow of Modular Authorship lives here: one index failure does not block the other.
- **Vector path** (lines 166-194): instantiate `MyOpenAICompatibleEmbeddings`, batch-encode in groups of 20 (`batch_size = 20`, line 174), save the FAISS index. This path *does* raise on failure (`RuntimeError("Vector store build failed: ...")`) — because without a vector index, hybrid retrieval is dead.

### 2.5 The fallback at query time

`load_retrievers` (`py/know_base.py:197-241`) loads both retrievers but **gracefully degrades** when BM25 is missing:

```python
# /tmp/super-agent-party/py/know_base.py:237-239
if bm25_retriever is None:
    print("Fallback: Using Vector Retriever for BM25 slot.")
    bm25_retriever = vector_retriever
```

The `EnsembleRetriever` (line 249-252) is constructed with `[bm25_retriever, vector_retriever]` and weights `[1 - weight, weight]`. If BM25 is unavailable, *both* slots are vector retrievers — the ensemble degrades to a weighted average of one retriever (which is equivalent to that retriever, modulo numerical noise). This is correct. This is graceful.

### 2.6 The reranker

`rerank_knowledge_base` (`py/know_base.py:315-369`) supports two upstream rerank vendors: Jina and Vllm. The function reads `KBSettings.selectedProvider`, looks up the provider's `vendor`, and dispatches. If the vendor is neither, **returns the documents unchanged** (line 369). Graceful Offline at the rerank boundary.

### 2.7 The local MiniLM server

`py/minilm_router.py:30-103` defines `MiniLMOnnxPredictor` — a `paraphrase-multilingual-MiniLM-L12-v2` ONNX runner. It checks for `model_O4.onnx` (the optimized variant) preferentially over `model.onnx` (line 47-49). It handles `token_type_ids` being absent in the model (line 95-99) by synthesizing a zero array. It exposes mean-pooling + L2-normalize (lines 71-79).

The pool (`MiniLMPool`, lines 106-128) lazy-loads with a lock, allows `reload()` (line 126), and is consumed via the FastAPI dependency `get_minilm_predictor` (line 150-155). The route `/minilm/embeddings` (line 157) is OpenAI-shape: `{model, input}` → `{object: "list", data: [{embedding, index}], model, usage: {prompt_tokens, total_tokens, inference_time_ms}}`. **A drop-in OpenAI embeddings substitute, running on CPU, locally, in 188 lines.** This is the single best piece of work in the SAP retrieval domain.

### 2.8 The dimension probe

`py/ebd_api.py:18-50` (`/api/embedding_dims`) takes `{api_key, base_url, model}`, sends `{"input": "test"}` to the upstream embeddings endpoint, and returns the length of the returned vector. The probe lets SAP auto-detect the dimensionality of any OpenAI-compatible embedding API without the user having to specify it. Small. Useful. The kind of polish that suggests someone has used SAP in earnest.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 BM25 stored as raw JSON

`py/know_base.py:147-152` writes the BM25 corpus as a JSON file — `{"docs": [{"page_content", "metadata"}, ...]}`. A 10k-document corpus is megabytes of JSON. Loading it (line 206-211) reads the entire file into memory, then constructs `BM25Retriever.from_documents(bm25_docs)` — which internally tokenizes every document. There is no incremental indexing. There is no compaction. Adding one document re-processes the whole corpus.

### 3.2 Chunk size is global per KB

`py/know_base.py:96-98` reads `chunk_size`, `chunk_overlap` from the KB config. Every document in the KB gets chunked the same way. A KB containing both 30-page PDFs and 200-character snippets is poorly served by a one-size-fits-all chunk policy.

### 3.3 No metadata filtering at query

`query_vector_store` (line 243-261) returns whatever the ensemble surfaces. There is no way to say "only return chunks where `metadata.author == 'volmarr'`." The metadata is *present* on every chunk (line 106-112 stores `file_path`, `file_name`, `doc_id`) but never *used* in the query path. The retrieval is content-only.

### 3.4 The reranker has no per-call timeout

`py/know_base.py:340-341` and 360-361 do `async with httpx.AsyncClient() as client: response = await client.post(...)` — no `timeout` parameter. A hung rerank API will hang the conversation. Compare to `py/llm_tool.py` where embedding probes use `timeout=10` (`py/ebd_api.py:33`). Inconsistent rigor.

### 3.5 The MiniLM model dir is settings-driven and not validated

`py/minilm_router.py:27` `MODEL_PATH = os.path.join(DEFAULT_EBD_DIR, MODEL_NAME)` — fine. But there is no checksum validation. A corrupted download is detected only at runtime when `ort.InferenceSession(...)` fails inside `MiniLMOnnxPredictor.__init__` (line 54). No hash file; no signed manifest.

### 3.6 The asyncio.run inside langchain bridge

`MyOpenAICompatibleEmbeddings.embed_query(text)` (line 74-76) calls `asyncio.run(self.aembed_query(text))`. If called from inside a running event loop (which happens when langchain is invoked from an async route handler), this raises `RuntimeError: asyncio.run() cannot be called from a running event loop`. SAP avoids this by always calling the *async* methods from its own code (the sync methods exist for langchain internal use). But the trap is set; a future refactor will fall into it.

### 3.7 The crisp parts

- The **hybrid retriever** approach. BM25 + vector with a configurable weight is the *correct* answer for general-purpose KB retrieval; pure vector is famously weak on rare tokens.
- The **graceful BM25 fallback** at `py/know_base.py:237-239`.
- The **local MiniLM ONNX server** at `py/minilm_router.py`. Worth lifting whole.
- The **vendor-agnostic reranker** at `rerank_knowledge_base`.
- The **Unicode-surrogate cleanse** at `clean_text`.
- The **embedding-dimension probe** at `/api/embedding_dims`.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 8
- [[20_interface/2B_RETRIEVAL_INTERFACE]] (Auditor) for the interface analysis
- [[60_synthesis/60_TRUE_NAME_REASSIGNMENT]] — Brunnr revisions in light of SAP
- [[hermes:HEM-24_MEMORY_INTERFACE]] for Hermes's contrasting memory shape
- [[peer:LETTA-2_SLEEPER]] for Letta's contrasting memory architecture
- [[ember:GUNGNIR]] — the Ember Well that this domain feeds

---

## What This Means for Ember

**Adopt:**
- **The hybrid BM25 + vector retrieval** with a configurable blend weight. This is the right answer for Brunnr's local-KB surface.
- **`py/minilm_router.py` whole** — the local MiniLM ONNX embedding server. 188 LOC of self-contained capability; lift verbatim, rename to `brunnr.local_embed`. The OpenAI-compatible shape means anything in Ember that speaks the embeddings API can transparently switch between local and remote.
- **`clean_text` Unicode-surrogate cleanse** at every Brunnr ingest boundary.
- **Graceful BM25 fallback** pattern (`py/know_base.py:237-239`) generalized: every Ember capability that has multiple backends names a fallback and falls through, logging the degradation.
- **Vendor-agnostic reranker dispatch** (`rerank_knowledge_base`) — adapt the shape to Ember's pluggable Brunnr re-rank interface.
- **The dimension probe** of `/api/embedding_dims` — small, useful, auto-detects.

**Adapt:**
- The **BM25 stored as a single JSON file** — adapt to a Pluggable Storage backend (SQLite-FTS5 on Pi, Tantivy on workstations). The Pluggable Storage Vow forbids the JSON-blob baseline.
- The **global per-KB chunk size** — adapt to a **document-type chunk policy**: PDFs chunk by section, code by AST nodes, transcripts by speaker turn. Type-aware chunking is one of the easier wins in retrieval.
- The **content-only query** — adapt to **metadata-filtered hybrid**: every query takes optional metadata predicates that scope the ensemble before the retrievers run.
- The **timeout-less reranker call** — adapt with consistent `timeout` discipline across every external call in Brunnr.

**Avoid:**
- **Loading the whole BM25 corpus from JSON at every query path** — even with cache. Brunnr's BM25 backend is a real index (FTS5 or Tantivy), not a re-serialized list of docs.
- **`asyncio.run(...)` from within a langchain sync method** when the caller is already in a loop. Either keep langchain in a separate thread or use exclusively-async retrievers.
- **Hash-less model downloads.** Every Brunnr model has a `.sha256` companion; mismatch → refuse-to-load with a typed error.

**Invent:**
- **The Two-Well Vow.** Brunnr is **two** wells: the **shallow well** (in-process, local, low-latency, recent context — chunks loaded for the current conversation) and the **deep well** (out-of-process, possibly remote, slow, comprehensive — the full Gungnir corpus). A query flows shallow-first; if confidence is low, the deep well is consulted. SAP has only the shallow concept (per-KB). Ember's two-well separation is the [[20_interface/2B_RETRIEVAL_INTERFACE]] mandate.
- **The Citation Contract.** Every retrieved chunk in Ember carries its provenance as a *first-class typed field*: source URI, retrieval method (bm25/vector/rerank/hybrid), confidence score, retrieval timestamp. The LLM is forbidden from emitting facts without citing chunks; the response post-processor verifies citations resolve. SAP injects retrieved chunks into the prompt; Ember audits the round-trip.
- **The Tiered Embedding Tier.** Pi-Ember uses a lighter MiniLM variant (e.g. all-MiniLM-L6, 384-dim) or no local embeddings at all (falls through to a remote API). Workstation-Ember runs paraphrase-multilingual-MiniLM-L12 (768-dim) or larger. Tier-collapse the embedding model, not just the runtime.
- **The Saga Index.** Beyond document chunks, Brunnr indexes *interaction histories* — past conversations, completed tasks, audit events — as their own retrieval namespace. A query like "what did we decide about X?" reaches into the saga, not just the docs. This is the natural extension of SAP's `mem0` shape into a typed Well.
- **Delta-Index-on-Add.** Adding a single document does not re-index the whole corpus. Brunnr's BM25 backend supports per-document update; the vector backend supports per-document add. Every ingest is incremental. The SAP "re-tokenize-everything" trap closes.

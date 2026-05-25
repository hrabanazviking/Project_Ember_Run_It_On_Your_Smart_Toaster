---
codex_id: 2B_RETRIEVAL_INTERFACE
title: Retrieval Interface — Embedding, BM25, and the Fallback That Pretends to Be A Hybrid
role: Auditor
layer: Interface
status: draft
sap_source_refs:
  - py/minilm_router.py:1-188
  - py/know_base.py:1-390
  - py/ebd_api.py:1-49
  - py/ebd_model_manager.py:1-179
ember_subsystem_targets: [Brunnr]
cross_refs:
  - 10_domain/17_RETRIEVAL_DOMAIN
  - 50_verification/58_OBSERVABILITY_GAPS
  - 50_verification/52_RESOURCE_BUDGETS
---

# Retrieval Interface — Embedding, BM25, and the Fallback That Pretends to Be A Hybrid

> *Sólrún, voice cold and even: SAP's retrieval claims an ensemble of two retrievers — sparse (BM25) and dense (vector). When one fails it silently substitutes the other for itself. The ensemble then "weights" two copies of the same retriever against each other. The user sees ranked results and trusts them. The trust is unearned.*

This document audits SAP's retrieval interface: the `MyOpenAICompatibleEmbeddings` adapter, the local MiniLM ONNX endpoint, the `know_base.py` hybrid retrieval flow, and the `EnsembleRetriever`-based fallback that quietly degrades to single-mode retrieval without telling anyone.

---

## 1. The Subject — Three Layers, One Pipeline

The retrieval stack is, top to bottom:

1. **Caller**: `know_base.py:292-313` `query_knowledge_base(kb_id, query)` — entry point for all retrieval requests.
2. **Ensemble**: `know_base.py:243-261` `query_vector_store(...)` — load BM25 + vector retriever, build `EnsembleRetriever`, invoke.
3. **Embedding Adapter**: `know_base.py:38-89` `MyOpenAICompatibleEmbeddings` — HTTP-POST to an embedding endpoint (default: SAP's own MiniLM router at `127.0.0.1:8000/minilm/embeddings`).
4. **Embedding Server**: `minilm_router.py:130-189` — FastAPI router that serves OpenAI-compatible embeddings backed by a local ONNX model.
5. **Tool Surface**: `know_base.py:371-390` `kb_tool` — exposes the retrieval as an LLM tool with two parameters: `query`, `kb_id`.

Five layers. Every layer has at least one degradation mode that does not surface to the next layer up.

---

## 2. The "Ensemble" That Isn't

`know_base.py:243-261`:

```python
# /tmp/super-agent-party/py/know_base.py:243-261
async def query_vector_store(query: str, kb_id, cur_kb, cur_vendor):
    """使用EnsembleRetriever的混合查询"""
    bm25_retriever, vector_retriever = await load_retrievers(kb_id, cur_kb, cur_vendor)
    if "weight" not in cur_kb:
        cur_kb["weight"] = 0.5
        
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=[1 - cur_kb["weight"], cur_kb["weight"]],
    )
    
    docs = await asyncio.to_thread(ensemble_retriever.invoke, query)
    
    return [{
        "content": doc.page_content,
        "metadata": doc.metadata,
    } for doc in docs]
```

This *looks* like a hybrid sparse+dense retriever. Look at `load_retrievers`:

`know_base.py:197-241`:

```python
# /tmp/super-agent-party/py/know_base.py:197-241
async def load_retrievers(kb_id, cur_kb, cur_vendor):
    """加载双检索器 (带 BM25 缺失的回退机制)"""
    kb_path = Path(KB_DIR) / str(kb_id)
    bm25_path = kb_path / "bm25_index.json"
    
    bm25_retriever = None
    try:
        if bm25_path.exists():
            bm25_data = await asyncio.to_thread(json.load, open(bm25_path, "r", encoding="utf-8"))
            bm25_docs = [
                Document(page_content=doc["page_content"], metadata=doc["metadata"]) 
                for doc in bm25_data["docs"]
            ]
            if bm25_docs:
                bm25_retriever = await asyncio.to_thread(BM25Retriever.from_documents, bm25_docs)
                bm25_retriever.k = cur_kb["chunk_k"]
    except Exception as e:
        print(f"Error loading BM25 (will fallback): {e}")

    embeddings = MyOpenAICompatibleEmbeddings( ... )
    
    vector_db = await asyncio.to_thread(
        FAISS.load_local,
        folder_path=str(kb_path),
        embeddings=embeddings,
        allow_dangerous_deserialization=True,
        index_name="index"
    )
    vector_retriever = vector_db.as_retriever( ... )

    # 3. 如果 BM25 加载失败（比如之前构建时跳过了），使用向量检索器顶替
    # 这样 EnsembleRetriever 相当于用了两个 VectorRetriever，不会报错
    if bm25_retriever is None:
        print("Fallback: Using Vector Retriever for BM25 slot.")
        bm25_retriever = vector_retriever

    return bm25_retriever, vector_retriever
```

The comment at line 235-237 is the smoking gun: "If BM25 fails to load, use Vector Retriever to substitute — this way EnsembleRetriever effectively uses two VectorRetrievers and doesn't error."

**The "hybrid" ensemble becomes two copies of the dense retriever.** The `weights=[0.5, 0.5]` ratio then weights vector against vector. The user, who set `weight=0.7` intending "70% dense, 30% sparse," now gets "70% dense, 30% dense" = 100% dense, with the BM25 path silently absent. There is no telemetry exposed to the caller. There is only `print("Fallback: Using Vector Retriever for BM25 slot.")` to stdout.

This is the worst class of silent degradation: the behavior contractually claimed (hybrid retrieval) is replaced by the behavior most easily produced (single-mode retrieval), the user sees results that look right, and the answer quality silently shifts. A user testing retrieval quality against a benchmark would not detect the regression unless they instrumented logs.

### 2.1 The BM25 build path that "skips" silently

Trace upstream to find when BM25 ends up missing. `know_base.py:127-164`:

```python
# /tmp/super-agent-party/py/know_base.py:127-164
    try:
        bm25_path = save_dir / "bm25_index.json"
        
        if not docs:
            print("Warning: No documents provided for BM25.")
        else:
            # 1. 清洗数据，防止 Unicode 错误
            clean_docs_data = []
            for doc in docs:
                clean_metadata = {
                    k: clean_text(v) if isinstance(v, str) else v 
                    for k, v in doc.metadata.items()
                }
                clean_docs_data.append({
                    "page_content": clean_text(doc.page_content),
                    "metadata": clean_metadata
                })

            await asyncio.to_thread(
                lambda: json.dump(
                    {"docs": clean_docs_data}, 
                    open(bm25_path, "w", encoding="utf-8", errors="ignore"), 
                    ensure_ascii=False
                )
            )
            print(f"BM25 index saved successfully for KB {kb_id}")

    except Exception as e:
        print(f"⚠️ BM25 Index failed (Skipping): {str(e)}")
        if 'bm25_path' in locals() and bm25_path.exists():
            try:
                os.remove(bm25_path)
            except:
                pass
```

Any exception during BM25 save — out of disk, permission error, unicode that survived cleaning — produces "⚠️ BM25 Index failed (Skipping)" and deletes the partial file. The vector store is built next; the user's knowledge base is "successful" with only the dense half. The user gets a `🟢 success` notification in the UI; the BM25 failure was only a `print`.

Then at retrieval time the fallback at line 237 kicks in. The user gets vector-only results. They never see "BM25 unavailable" in the UI.

### 2.2 `errors="ignore"` on JSON write

Line 152: `open(bm25_path, "w", encoding="utf-8", errors="ignore")`. The `errors="ignore"` is a `TextIOWrapper` parameter that silently drops characters that can't be UTF-8 encoded. But `clean_text` already ran (lines 27-35); what slipped through? Surrogates that survive `encode('utf-8', 'ignore').decode('utf-8')` only re-emerge when *re-encoding* into the open file — which is exactly here. The double-defense is needed because the cleaning is fragile.

This is a complaint about Python's surrogate handling, not the author. But the result is: BM25 documents may have characters silently dropped that affect tokenization. The BM25 index built on stripped text won't match the FAISS index built on original text. Same query, two different lexical bases.

---

## 3. The Embedding Adapter Lies Quietly

`know_base.py:38-89` defines `MyOpenAICompatibleEmbeddings`. It is *not* `langchain_openai.OpenAIEmbeddings`. It is a hand-rolled `Embeddings` subclass that does HTTP requests itself.

`know_base.py:74-80`:

```python
# /tmp/super-agent-party/py/know_base.py:74-80
    def embed_query(self, text: str) -> List[float]:
        data = asyncio.run(self.aembed_query(text))
        return data

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        data = asyncio.run(self.aembed_documents(texts))
        return data
```

`asyncio.run` inside a method that may be called from an already-running event loop will raise `RuntimeError: asyncio.run() cannot be called from a running event loop`. This means `embed_query` (sync) and `embed_documents` (sync) only work when called from non-async code. `FAISS.load_local` and `FAISS.from_documents` call these sync methods. SAP wraps the *whole thing* in `asyncio.to_thread` (`know_base.py:182,224`) so the sync embedding methods run on a thread — and *that* thread's `asyncio.run` is on a fresh loop, so it works.

This is fragile. If a future refactor calls `embed_query` directly from an async context, it crashes. If LangChain's `EnsembleRetriever.invoke` (called via `asyncio.to_thread` at `know_base.py:255`) internally calls `embed_query` *via* the loop the thread is using, it crashes. The pattern works because the threading is just-so.

### 3.1 No retry, no batching beyond 20

`know_base.py:174-186`:

```python
# /tmp/super-agent-party/py/know_base.py:174-186
        batch_size = 20 
        vector_db = None
        
        for i in range(0, len(docs), batch_size):
            batch = docs[i:i+batch_size]
            
            if vector_db is None:
                vector_db = await asyncio.to_thread(FAISS.from_documents, batch, embeddings)
            else:
                await asyncio.to_thread(vector_db.add_documents, batch)
            
            print(f"Processed {min(i+batch_size, len(docs))}/{len(docs)} documents")
```

Batch size hardcoded to 20. No retry on transient failure. If embedding 200 docs and the 7th batch fails, the first 6 batches' work is preserved in `vector_db` but never saved (the save happens at line 190 *after* the loop). A failure mid-loop loses progress. The exception escapes via `raise RuntimeError(...)` at line 194 — the user gets a generic error and starts from scratch.

### 3.2 Authorization is Bearer-only

`know_base.py:53`:

```python
headers = {"Authorization": f"Bearer {self.api_key}"}
```

Embedding endpoints that authenticate via `api-key` header (Azure OpenAI) or `x-api-key` header (some vendors) will reject this. The adapter only supports Bearer-token auth. The class is named `MyOpenAICompatibleEmbeddings` — implicitly committing to OpenAI's Bearer convention. Vendors that diverge are silently incompatible.

---

## 4. The MiniLM Router — A Fastapi Endpoint For Itself

`minilm_router.py:130-188` exposes `POST /minilm/embeddings` with an OpenAI-compatible request and response shape. This is the *server* side of `MyOpenAICompatibleEmbeddings`. SAP eats its own embeddings.

`minilm_router.py:106-130`:

```python
# /tmp/super-agent-party/py/minilm_router.py:106-130
class MiniLMPool:
    def __init__(self, model_dir: str, use_gpu: bool = False):
        self.model_dir = model_dir
        self.use_gpu = use_gpu
        self._predictor: Optional[MiniLMOnnxPredictor] = None
        self._lock = threading.Lock()

    def get(self) -> MiniLMOnnxPredictor:
        if self._predictor and self._predictor.is_loaded:
            return self._predictor
        with self._lock:
            if self._predictor and self._predictor.is_loaded:
                return self._predictor
            
            predictor = MiniLMOnnxPredictor(self.model_dir, self.use_gpu)
            if not predictor.is_loaded:
                raise RuntimeError("Model failed to load")
            self._predictor = predictor
            return self._predictor

    def reload(self):
        with self._lock:
            self._predictor = None

minilm_pool = MiniLMPool(MODEL_PATH, use_gpu=False)
```

Double-checked locking, `threading.Lock`, single global predictor. Sensible. `use_gpu=False` at the bottom is hard-coded — the pool never asks the user. A user with a CUDA GPU gets CPU inference unless they edit the source. The settings system has no `embeddings.use_gpu` key. The reload endpoint (`/minilm/reload`, line 186) drops the predictor but reload re-uses the same `use_gpu=False`.

### 4.1 Token count fallback is wrong

`minilm_router.py:163-167`:

```python
# /tmp/super-agent-party/py/minilm_router.py:163-167
    try:
        num_tokens = sum(len(predictor.tokenizer.tokenize(t)) for t in texts)
    except Exception:
        num_tokens = sum(len(t) for t in texts) // 4
```

If the tokenizer fails, fall back to `total_chars / 4`. For Chinese or Japanese text, chars-per-token is closer to 1.0 (or even less than 1). The `/4` heuristic is OpenAI-English. Using it for multilingual text underreports tokens by a factor of 2-4×. This usage report is read by upstream cost/quota tracking. A multilingual SAP user thinks they're using a quarter as many tokens as they are.

### 4.2 Model path search is silent

`minilm_router.py:46-50`:

```python
# /tmp/super-agent-party/py/minilm_router.py:46-50
            model_path_o4 = os.path.join(model_dir, "model_O4.onnx")
            model_path_std = os.path.join(model_dir, "model.onnx")
            target_model = model_path_o4 if os.path.exists(model_path_o4) else model_path_std
```

Prefer `model_O4.onnx` (optimized) over `model.onnx`. If only `model.onnx` exists, use it. The user has no idea which model was loaded; embedding quality differs subtly. No log line names the loaded model file at startup beyond line 56 (`print(f"MiniLM ONNX Predictor loaded from: {target_model}")`). At least *this* one prints.

---

## 5. The kb_tool Schema Is Honest About One Thing

`know_base.py:371-390`:

```python
kb_tool = {
    "type": "function",
    "function": {
        "name": "query_knowledge_base",
        "description": f"通过自然语言获取的对应ID的知识库信息。回答时，在回答的最下方给出信息来源...",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "需要搜索的问题。",
                },
                "kb_id": {
                    "type": "string",
                    "description": "知识库的ID。"
                }
            },
            "required": ["kb_id","query"],
        },
    },
}
```

The description (Chinese) instructs the LLM to cite sources in `[file_name](file_path)` markdown format. This is the right instinct — provenance with every retrieved result. SAP's tool-prompt asks for citation at the *output* layer; the *input* layer (the retrieved doc) carries `metadata.file_path` and `metadata.file_name` (`know_base.py:107-113`).

The honesty: the tool *does* return provenance. The dishonesty: the tool description never tells the LLM that 30% of the "hybrid" weighting may be a phantom (the BM25 fallback case). The LLM cannot reason about retrieval mode because retrieval mode is hidden.

---

## 6. The `chunk_size` Cliff

`know_base.py:92-114`:

```python
# /tmp/super-agent-party/py/know_base.py:92-114
def chunk_documents(results: List[Dict], cur_kb) -> List[Document]:
    """为每个文件单独分块并添加元数据"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=cur_kb["chunk_size"],
        chunk_overlap=cur_kb["chunk_overlap"],
        separators=["\n\n", "\n", "。", "！", "？", "!", "?", "."]
    )
    ...
```

`chunk_size` and `chunk_overlap` come from the kb config. The separators are sentence-final punctuation in Chinese and English. **No comma**, no semicolon, no colon. A document with many long clauses but few sentence-finals will be chunked at character boundaries — `RecursiveCharacterTextSplitter` falls through to character splits when separators don't fire.

There is no separator for Japanese (`。` is shared with Chinese but `。` is also Japanese — fine). Arabic (`؟`, `،`) is absent. Devanagari (`।`) is absent. For multilingual KBs this hurts retrieval quality silently.

---

## 7. Cross-References

- [[10_domain/17_RETRIEVAL_DOMAIN]] — Architect's domain view of the retrieval subsystem
- [[50_verification/58_OBSERVABILITY_GAPS]] — silent fallback as a class of observability gap
- [[50_verification/52_RESOURCE_BUDGETS]] — MiniLM ONNX cost; CPU vs GPU
- [[hermes:HEM-13_BRUNNR_AND_THE_WELL]] — Hermes's view of retrieval, Brunnr's claim on this domain
- [[ember:RULES.AI]] — "make data reading code robust" — silent fallback violates this

---

## What This Means for Ember

**Adopt:**
- Adopt the **OpenAI-compatible embedding endpoint as a transport** (`minilm_router.py:157-184`). Pluggable backends (local MiniLM, remote BAAI, remote OpenAI, etc.) under one wire format keeps the storage layer interchangeable. Vow of **Modular Authorship** at the embedding level.
- Adopt the **chunk metadata format** (`know_base.py:108-113`): `file_path`, `file_name`, `doc_id`. Provenance carried per chunk is the right shape.

**Adapt:**
- Adapt the BM25-or-vector ensemble *concept*, but the fallback must be **loud, not silent**. If BM25 is unavailable, `query_knowledge_base` returns a *typed* result with `retrieval_mode: "vector_only"` and the LLM (and the operator) can see it. The "duplicate vector retriever to keep EnsembleRetriever happy" trick at `know_base.py:237` is rejected outright.
- Adapt the chunk separator list to include the full set of sentence-final punctuation for **every language Ember supports** — Chinese, Japanese, Korean, Arabic, Devanagari, Thai, etc. Or: use a language-detect step and pick the separator set per chunk.

**Avoid:**
- **Never silently degrade retrieval mode** (`know_base.py:237`). Degradation is observable in every layer.
- **Never `asyncio.run` inside sync methods of an `Embeddings` subclass** (`know_base.py:75,79`). Use `nest_asyncio` or thread the async/sync boundary explicitly. The current pattern works by happy accident.
- **Never hardcode GPU=False** (`minilm_router.py:130`). Capability is a config decision, not a source-edit decision.
- **Never count tokens with chars/4 for multilingual text** (`minilm_router.py:167`). Use the actual tokenizer or a language-aware approximation. For Chinese/Japanese chars-per-token approaches 1.0.
- **Never use `errors="ignore"` on a file write that's the canonical artifact** (`know_base.py:152`). If the data is malformed enough to need that, fix the input, not the write.
- **Never use `allow_dangerous_deserialization=True` on FAISS load without an integrity check** (`know_base.py:228`). FAISS index files are pickled; loading them with `allow_dangerous_deserialization=True` is `pickle.loads` of arbitrary content. If the file was tampered with (or built by an older incompatible version), this is RCE.
- **Never expose `kb_tool` to the LLM without exposing the kb's *contents* description** (`know_base.py:371-390`). The LLM should know what kind of knowledge is in `kb_id=X` — not just "a knowledge base."

**Invent:**
- **Retrieval Mode Provenance.** Every result from Brunnr carries `retrieval_mode: "hybrid" | "vector_only" | "sparse_only" | "lexical_fallback"` and a `confidence_floor` field that reflects retrieval quality. Hjarta can weight LLM trust based on retrieval mode. SAP's blind ensemble is the negative template.
- **Per-KB Retrieval Profile.** Each KB declares its expected retrieval profile at build time: was BM25 built? was the vector store built with the same embedding model? what's the vocabulary size? Brunnr refuses queries against profiles that don't match the current embedding adapter (so a vector store built with one model isn't queried by a different model — that bug is silent in SAP).
- **Allowlist Embedding Vendors.** Brunnr's embedding adapter declares supported wire formats (OpenAI-Bearer, Azure-api-key, Ollama-native, etc.) and the per-vendor request shape. Adding a new vendor is a declarative add, not a string edit.
- **FAISS Integrity Witness.** When building a FAISS index, also write a manifest with embedding-model-id, dimension, n_docs, build-time, sha256 of the FAISS file. On load, verify the manifest matches. Reject mismatch. Vow of **Cache Discipline** applied to embeddings.
- **Bounded-Batch Retry Embedding.** Embedding a corpus uses bounded batches with per-batch retry; the partial vector store is checkpointed every N batches so a network blip doesn't restart from zero. The save-after-loop pattern in `know_base.py:188-191` is the negative template.
- **Multilingual Separator Atlas.** Ember ships a per-language separator atlas the chunker consults at chunk time. The atlas is a JSON file — extensible by users without code edits. Vow of **Public-Friendliness** at the chunker.

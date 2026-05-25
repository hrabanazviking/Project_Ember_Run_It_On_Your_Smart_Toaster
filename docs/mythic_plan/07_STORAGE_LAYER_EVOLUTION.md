# 07 - STORAGE LAYER EVOLUTION: BRUNNR 2.0

## I. The Well of Mímir: Introduction to Memory

An intelligence without memory is merely a calculator. To become a companion, Project Ember must remember the user's preferences, past conversations, inferred facts, and systemic state. In ClawLite, memory was managed via a robust combination of BM25 text search and vector databases (SQLite + pgvector). But ClawLite was designed for servers. 

Project Ember must run on a smart toaster. A toaster cannot run PostgreSQL. 

Thus, we introduce **Brunnr 2.0 (The Well of Memory)**. Brunnr 2.0 is a universal storage abstraction layer. It decouples the *concept* of memory retrieval (semantic search, exact match, time-series querying) from the *physical storage engine*. It can dynamically fall back from massive distributed Postgres clusters down to the simplest flat-file JSON append logs, all without changing a single line of cognitive application code.

---

## II. The Universal Storage Abstraction

Brunnr 2.0 sits beneath the Yggdrasil Microkernel as a hot-swappable module. To the Smiðja (Cognitive Engine), memory is queried via a unified GraphQL or native Rust/Python API interface. 

The Cognitive Engine simply asks: *"Retrieve context regarding the user's dog."*
Brunnr determines *how* and *where* to execute that query based on the active Storage Driver.

### 2.1 The Hierarchy of Drivers (The Depths of the Well)

Brunnr evaluates the host hardware (via the Forge of Sindri) and selects the deepest possible well it can support:

1. **The Deepest Waters (PostgreSQL + pgvector)**
   - **Environment**: Cloud clusters, powerful home servers (Inferno).
   - **Capabilities**: Massive concurrency, multi-tenant RBAC, billion-scale HNSW index vector search, complex transactional integrity.

2. **The Steady Stream (DuckDB / SQLite + sqlite-vss)**
   - **Environment**: Laptops, Desktops, Raspberry Pi 5 (Bonfire / Kindling).
   - **Capabilities**: Zero-configuration, local file-based, fast analytical queries, sub-million vector search via local Faiss or sqlite-vss. 

3. **The Quick Puddle (Redis / LMDB)**
   - **Environment**: Devices requiring ultra-low latency but with limited disk I/O (e.g., streaming devices).
   - **Capabilities**: Pure in-memory key-value stores, ephemeral context caching, fast pub/sub message brokering.

4. **The Frost Layer (Filesystem-Only Mode)**
   - **Environment**: Smart Toasters, ESP32s, highly constrained IoT (Smoldering).
   - **Capabilities**: No database engine at all. Context is stored as raw JSON Lines (`.jsonl`) or pure Markdown files. Vector search is replaced with a hyper-optimized, in-memory string-matching algorithm (like Aho-Corasick) or a quantized TF-IDF map loaded directly into RAM.

---

## III. The Architecture of Brunnr 2.0

To achieve this fluidity, Brunnr implements a strict separation between the **Schema Definition**, the **Query Planner**, and the **Execution Engine**.

```mermaid
graph TD
    subgraph Smiðja (Cognitive Engine)
        Request[Context Request: 'User Preferences']
    end
    
    subgraph Brunnr 2.0 Abstraction Layer
        Request --> Parser[Query AST Parser]
        Parser --> Planner[Adaptive Query Planner]
        Planner --> Cache[L1 RAM Cache]
        
        Cache -- Miss --> Router[Driver Router]
    end
    
    subgraph Physical Drivers
        Router -.-> |Inferno Mode| PG[(PostgreSQL + pgvector)]
        Router -.-> |Bonfire Mode| DDB[(DuckDB / SQLite)]
        Router -.-> |Smoldering Mode| FS[(Flat File JSONL)]
    end
```

### 3.1 Adaptive Schema Forging
Instead of hardcoding SQL `CREATE TABLE` statements, Ember's data models are defined using an Abstract Syntax Tree (AST) ORM. 
When Brunnr initializes, it compiles the schema into the appropriate format for the active driver. If switching from SQLite to Flat Files, it converts the relational schema into a hierarchical JSON document structure automatically.

### 3.2 Polyglot Vector Search
Vector embeddings are massive arrays of floats. Storing and searching them is computationally expensive. 
- In **Postgres**, Brunnr delegates this to `pgvector` HNSW indexes.
- In **SQLite**, it uses `sqlite-vss`.
- In **Filesystem Mode**, Brunnr uses a custom quantization technique. It compresses the 768-dimensional float32 vectors down to 1-bit binary vectors (using Locality-Sensitive Hashing - LSH). The search is then performed using blazing-fast XOR operations and Hamming Distance calculations purely in the CPU cache, bypassing the need for a database engine entirely.

---

## IV. Memory Eviction and Compaction (The Tides of Mímir)

A local device has limited disk space. A sovereign companion running for 5 years will accumulate gigabytes of conversational history. Brunnr implements aggressive, intelligent compaction.

### 4.1 The Forgetting Curve
Ember does not treat all memories equally. Brunnr implements an Ebbinghaus-inspired Forgetting Curve algorithm. 
- **Core Identity Facts** (User's name, core system instructions) are pinned in L1 Cache.
- **Recent Conversations** (Last 7 days) are stored in full fidelity.
- **Old Conversations** are periodically passed to the LLM during idle cycles (e.g., when the device is charging at night). The LLM summarizes a 10,000-token conversation into a dense 500-token summary, stores the summary, and deletes the raw logs to reclaim disk space.

### 4.2 Semantic De-duplication
Over time, the user might tell the AI the same fact multiple times. The background compaction worker (a Huginn Task) runs a clustering algorithm (DBSCAN) over the vector database. It identifies semantically identical memory nodes and merges them into a single node with an updated temporal weight.

---

## V. Code Implementation: The Universal Driver Interface

Here is a conceptual look at how Brunnr routes a semantic search query seamlessly across completely different storage backends:

```python
class BrunnrMemoryCore:
    def __init__(self, driver: StorageDriver):
        self.driver = driver
        self.embedder = LocalEmbeddingModel()
        
    async def retrieve_context(self, query_text: str, top_k: int = 5) -> List[MemoryNode]:
        # 1. Convert text to vector
        query_vector = await self.embedder.embed(query_text)
        
        # 2. Extract keywords for BM25 hybrid search
        keywords = extract_keywords(query_text)
        
        # 3. Route to the active driver
        if isinstance(self.driver, PostgresDriver):
            return await self.driver.hybrid_search_pgvector(query_vector, keywords, top_k)
            
        elif isinstance(self.driver, SQLiteDriver):
            return await self.driver.search_sqlite_vss(query_vector, top_k)
            
        elif isinstance(self.driver, FilesystemDriver):
            # Fallback to quantized Hamming distance search for IoT devices
            quantized_vec = binarize_vector(query_vector)
            return await self.driver.hamming_search_jsonl(quantized_vec, top_k)
```

---

## VI. INVENTED METHODS: Brunnr Innovations

### 6.1 Holographic Memory Paging
When switching between drivers (e.g., the user installs DuckDB on a machine previously running Filesystem Mode), Brunnr uses **Holographic Memory Paging**. It does not freeze the system to migrate 50GB of text files. Instead, it creates a transparent read-through cache. New queries are routed to the new DB; if a record is not found, it pages it in from the legacy filesystem and saves it to the new DB asynchronously. The migration happens invisibly in the background.

### 6.2 The Ouroboros Ring Buffer
For extreme edge devices (smart toasters, wearables) that use Flash memory (eSMMC / SD Cards), constant writing destroys the physical storage blocks due to write-amplification. 
Brunnr introduces the **Ouroboros Ring Buffer**. Conversational logs are stored purely in RAM. Disk writes are deferred and batched into a single, sequential, wear-leveling-friendly block write only once every 24 hours, or immediately triggered upon detecting a critical power-drop (using an onboard capacitor to provide the 500ms of juice needed to write the RAM to disk).

---

## VII. Conclusion: The Deepening Waters

Brunnr 2.0 solves the greatest paradox of local AI: how to possess supercomputer-level long-term memory while running on microcontrollers. By decoupling the query interface from the storage engine, utilizing binary quantization for vector search on edge devices, and implementing aggressive semantic compaction, Ember's memory scales fluidly from JSON files to PostgreSQL clusters.

The memories are secure, sovereign, and eternal.

In the final document, we will map out how all these systems—the Flame Intensity, the Bifrost Mesh, the Heimdallr Gateway, the Yggdrasil Kernel, and Brunnr Storage—culminate in the ultimate deployment strategies: **Deployment Topology Patterns**.

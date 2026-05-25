# Document 37: CACHING AND MEMOIZATION – The Dwarven Cache Vaults

## 1. Introduction: The Vaults of Nidavellir

The **Dwarven Cache Vaults** represent our multi-tier caching and memoization architecture. The most efficient computation is the one you never have to perform. The Vaults ensure Ember remembers everything, making it appear telepathic by answering questions before it finishes thinking.

---

## 2. The Multi-Tier Vault Architecture

- **Tier 1 (L1 Memory Vault):** LRU RAM Cache (<1us latency, 5-10MB). Exact matches for routing and short frequent phrases.
- **Tier 2 (L2 Disk Vault):** Memory-Mapped SQLite (100-500us latency, 100MB-1GB). Semantic response cache, KV-states.
- **Tier 3 (L3 Deep Vault):** Compressed Archives (10-50ms latency, unlimited). zstd compressed older contexts.

---

## 3. Semantic Response Caching

The Dwarven Vaults employ **Semantic Caching**. 
1. A prompt is embedded.
2. The vector is compared against the L2 Vault using HNSW ANN search.
3. If cosine similarity > 0.98, it's a Semantic Hit.

To provide variation, a Tier 1 Spark model rephrases the cached output in milliseconds, providing dynamic text at zero heavy-compute cost.

---

## 4. KV-Cache Memoization (Prefix Caching)

### 4.1 The Golden Prefix

Ember identifies static prefixes (like system prompts). The resulting KV-cache matrix is serialized to the L2 Vault as a `Golden Prefix Blob`. For subsequent messages, Surtr loads this directly into the KV-cache. TTFT drops from 5s to 15ms.

### 4.2 Tree-Structured KV Caching

If the user branches a conversation, the Vault maintains a tree of KV states. Ember instantly traverses the tree and loads the correct state branch.

---

## 5. Predictive Pre-computation: The Oracle's Forge

When idle, the Tuning Loop activates the Predictive Engine.
1. It reads the open file in the workspace.
2. Generates an embedding and pre-computes the KV-cache.
3. Generates likely questions the user might ask.
4. Runs inference and stores answers in the deep cache.

When the user asks the question, Ember streams a 500-word response in 0.1s.

---

## 6. Invented Method: "Fractal Embedding Compression"

Storing millions of embeddings consumes gigabytes. Ember uses **Fractal Embedding Compression**. 
1. A local micro-autoencoder squashes a 768-dim vector into a 32-byte "Fractal Hash".
2. ANN search is performed in this 32-byte space using Hamming distance.
3. Full vectors are only retrieved from L3 Vaults for collision verification.

This stores the semantic memory of 100,000 document chunks in less than 4MB of RAM.

*(End of Document 37)*

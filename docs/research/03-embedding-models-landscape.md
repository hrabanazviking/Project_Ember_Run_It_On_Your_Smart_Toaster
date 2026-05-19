# 03 — Vector Embedding Models: BGE, E5, Nomic, GTE, jina

**Category:** Memory & Knowledge Storage
**Runa relevance:** Muninn (retrieval index), Heimskringla (semantic-dedup cache layer)
**Status:** Research synthesis. Landscape evolves quickly — re-survey before pinning a model.
**Last touched:** 2026-05-17

---

## 1. Core idea

A text embedding model maps a string to a fixed-dimensional vector such that semantically similar strings end up near each other (by cosine or Euclidean distance). The vector becomes the storable, indexable proxy for "meaning". Quality of retrieval — and therefore quality of memory and RAG — depends critically on which embedding model you pick.

By late 2024 / early 2026 the open-source landscape has matured to the point that for most use cases you no longer pay OpenAI for embeddings — small, fast, accurate models run locally. The choice is between several roughly-equivalent families, each with its own ergonomic profile.

## 2. Technical depth

Modern text embedding models share a recipe:

1. **Backbone:** a transformer encoder (BERT-style, MiniLM, or a small decoder-only model used as encoder).
2. **Pooling:** mean-pool, CLS-token, or last-token. Mean-pool dominates in modern open models.
3. **Contrastive training:** trained on pairs of (anchor, positive) and a large batch of in-batch negatives. The loss pulls anchors toward positives and away from negatives in vector space. Many models also use *hard negatives* mined from the training corpus.
4. **Task instructions:** newer models prepend a short instruction to the input ("Represent this sentence for retrieval:") so the same model can produce different vectors for different retrieval tasks. E5 and BGE both adopted this pattern.

Output vectors are typically 384, 512, 768, 1024, or 4096 dimensions. **Matryoshka Representation Learning** (Kusupati et al., 2022) trains models so that truncating the vector to its first N dimensions still gives a useful similarity signal — letting you trade quality for storage at query time. Nomic Embed and Mixedbread are notable for explicit Matryoshka support.

The **MTEB benchmark** (Massive Text Embedding Benchmark, Muennighoff et al., 2022, maintained on HuggingFace) is the canonical scoreboard. It bundles ~50+ tasks across classification, clustering, pair classification, reranking, retrieval, STS, summarization. A model's MTEB score is a weighted average; the *retrieval subset* matters most for memory and RAG.

## 3. Key works (model families)

**BGE (BAAI General Embedding)** — Beijing Academy of AI, 2023→present.
- Family: `bge-small-en`, `bge-base-en`, `bge-large-en`, plus `bge-m3` (multilingual + multi-vector + sparse).
- Strengths: top of MTEB leaderboards through 2023-2024; mature; Apache-2.0 license.
- Quirks: instruction-prefixed queries; English-tuned variants are stronger than multilingual.

**E5 (Microsoft)** — Wang et al., 2022-2024.
- Family: `e5-small-v2`, `e5-base-v2`, `e5-large-v2`, then `multilingual-e5-*`.
- Strengths: strong baseline, well-documented, instruction prefixes well-specified.
- Quirks: "passage:" / "query:" prefixes are required.

**Nomic Embed** — Nomic AI, early 2024.
- Family: `nomic-embed-text-v1`, `nomic-embed-text-v1.5` (with Matryoshka).
- Strengths: open weights AND open training data — fully reproducible. Long context (8K tokens) better than most older embeddings. Apache-2.0.
- Quirks: relatively new; less battle-tested than BGE in production.

**GTE (Alibaba)** — General Text Embeddings, 2023-2024.
- Family: `gte-small`, `gte-base`, `gte-large`, then `gte-Qwen2-*` (decoder-only encoder, 7B+).
- Strengths: the Qwen-based GTE models punch hard on retrieval; multilingual coverage is solid.
- Quirks: the large Qwen variants are heavy (7B+ params); good for batch indexing, slow for query-time embedding on Pi.

**jina-embeddings** — Jina AI, 2023-2024.
- Family: `jina-embeddings-v2-{small,base}-en`, `jina-embeddings-v2-base-code` (for code retrieval), `jina-embeddings-v3` multilingual.
- Strengths: 8K-token context, good code-retrieval variant, MIT or Apache licensed.
- Quirks: v3 has a slightly heavier inference cost than BGE-small.

**Mixedbread (mxbai-embed-*)** — Mixedbread AI, 2024.
- Strong leaderboard performance; Matryoshka support; open weights.

**OpenAI `text-embedding-3-{small,large}`** — closed-source baseline.
- Useful as a quality ceiling for closed-source; not selectable for the local-first design Runa wants.

## 4. Empirical results

- For *English retrieval at small model size* (good for Pi 5), as of late 2024: BGE-small-en-v1.5, E5-small-v2, and Nomic-embed-text-v1.5 are within ~2 points of each other on MTEB retrieval. The right choice is more about license and tokenizer than score.
- **Long-context embedding** (the doc is >2K tokens): Nomic, jina v2, and BGE-M3 are the strong choices. Older 512-token-limit models silently truncate and lose information.
- **Code embedding:** specialised models matter — `jina-embeddings-v2-base-code` or `CodeBERTa`-style outperform general-purpose ones on code-search tasks by 5-15 MRR points.
- **Multilingual:** `bge-m3` and `multilingual-e5-large` lead. English-only models do *not* gracefully degrade on other languages — they fall hard.
- **Dimension count:** for most retrieval, 384-dim models perform within 1-2 points of 1024-dim ones if both are well-trained. Storage and compute scale linearly with dim, so 384 is often the right Pareto choice.

## 5. Applicability to Runa

For **Muninn's retrieval index** ([[08-sqlite-vss-embedding-in-database]] + ADR-0002 §D-2.2):

- **Recommended starting model:** `bge-small-en-v1.5` (384 dim) or `nomic-embed-text-v1.5` (768 dim with Matryoshka).
  - BGE-small for absolute minimum storage and fastest queries on Pi 5.
  - Nomic for long-context episodes (multi-paragraph conversation turns) and the open training data.
- Pin the model name in `config/runa.example.yaml#memory.embedding_model`.
- Treat model swap as a migration: a `runa.migrations` script that re-embeds every episode in Muninn. Cost: O(N) embedding-model calls. On Pi, do it overnight.

For **Heimskringla's semantic-dedup cache** (ADR-0002 §D-2.4):

- Use the *same* embedding model as Muninn so the embedding inference cost is amortised. Cache the prompt-embedding next to the prompt itself.
- Similarity threshold for dedup should be conservative (e.g. cosine ≥ 0.92). A false-positive dedup is worse than a missed dedup — the user gets the wrong cached answer.

What to avoid:

- Don't run a 7B-parameter embedding model on Pi 5 for query-time. Inference latency dominates.
- Don't mix models — every embedding in a single index must come from the same model. If you must hold two indices (e.g. one for code, one for prose), keep them strictly separate.
- Don't truncate Matryoshka embeddings inconsistently. If you store 384-dim Nomic vectors but query with 768-dim vectors, distance is meaningless.

## 6. Open questions

- **Decoder-only encoders.** Qwen2-1.5B and similar small decoders, prompted for embedding, are now competitive with dedicated encoder models on MTEB. Will dedicated encoders survive?
- **Multimodal embeddings.** CLIP-style joint text-image embeddings (and their successors, like the SigLIP family) might let Muninn index Runa's voice waveforms or screenshots in the same space as text. Active research direction.
- **Late chunking.** Newer technique: embed long documents whole, then *slice* the resulting embeddings into chunk-embeddings, rather than slicing text first then embedding. Preserves cross-chunk context. Promising but immature.
- **In-domain fine-tuning.** Should Muninn fine-tune its embedding model on Runa's own conversation transcripts to better encode Runa-specific vocabulary? Possible win; nontrivial pipeline.

## 7. References (curated)

- huggingface.co/blog/mteb — the MTEB benchmark home, with current leaderboard.
- arXiv:2309.07597 — BGE / "C-Pack: Packaged Resources to Advance General Chinese Embedding".
- arXiv:2402.05672 — Nomic Embed.
- arXiv:2212.03533 — E5 / "Text Embeddings by Weakly-Supervised Contrastive Pre-training".
- arXiv:2308.03281 — GTE / "Towards General Text Embeddings with Multi-stage Contrastive Learning".
- arXiv:2205.13147 — Matryoshka Representation Learning (Kusupati et al.).
- arXiv:2210.07316 — Original MTEB paper (Muennighoff et al.).

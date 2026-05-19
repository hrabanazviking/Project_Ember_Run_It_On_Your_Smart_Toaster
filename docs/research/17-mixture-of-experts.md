# 17 — Mixture-of-Experts Architectures

**Category:** LLM Techniques
**Runa relevance:** Heimskringla (model selection — MoE economics), local inference (Mixtral on laptop)
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

A Mixture-of-Experts (MoE) language model splits the feed-forward layer of each transformer block into many parallel "experts." A small router network picks the top-K experts to activate for each token. The result: a model with *enormous total parameters* (e.g. 470B for Mixtral 8x22B) but *small activated parameters* (e.g. 39B per token) — meaning training and inference cost is proportional to the activated count, not the total. MoE is the technique that lets the trillion-parameter frontier models be tractable to train and serve, and that lets a moderately-sized server run a model that would be impossible at the same activated-parameter count if it were dense.

For Runa's local-first design, MoE matters because Mixtral-class models (Mixtral 8x7B at ~13B activated, Mixtral 8x22B at ~39B activated) deliver *quality-of-a-much-larger-model* at the inference cost of a smaller dense model — assuming you have the *memory* to hold all experts. The memory/compute trade-off is dramatically different from dense models, and Heimskringla's model-routing decisions need to model it correctly.

## 2. Technical depth

**Architecture.** Each transformer block has a Multi-Head Attention sublayer (kept dense) and a Feed-Forward Network (FFN). In a dense model the FFN is one big MLP. In MoE the FFN is replaced with:

```
                token activations
                       │
                       ▼
                ┌──────────────┐
                │   Router     │   (small linear layer + softmax)
                └───┬──────┬───┘
                    │      │
        top-K scores▼      ▼ ...
              ┌────────┐ ┌────────┐    ┌────────┐
              │Expert 1│ │Expert 2│ … │Expert N │   (each a full MLP)
              └────┬───┘ └───┬────┘    └────┬───┘
                   │         │              │
                   └─weighted-sum-of-top-K─┘
                            │
                            ▼
                       to next layer
```

**Typical configurations:**

- K (top-K) = 1 or 2 experts activated per token.
- N (total experts) = 8, 16, 64, 128 — varies.
- Router is a single linear layer; load-balancing loss during training prevents one expert from being picked for everything.

**Sparsity and the "activated params" framing.** Mixtral 8x7B has ~46.7B total parameters but at each token only 2 of 8 experts fire, giving ~13B "activated" parameters per token. Inference compute scales with activated count; memory scales with total count. You need to load all experts (because you don't know in advance which token will route where) but only compute through a few.

**Load balancing.** Without explicit pressure, the router collapses — one or two experts get picked for every token, others sit idle. Modern MoE adds an *auxiliary load-balancing loss* during training that penalises uneven expert use. Switch Transformer used z-loss; newer techniques (e.g. expert-choice routing where experts pick tokens instead of tokens picking experts) avoid the imbalance problem entirely.

**Expert choice routing (Zhou et al., 2022).** Inverts the direction: each expert picks the top tokens it wants to process. Eliminates the dropped-token problem of token-choice routing.

**Notable MoE models:**

- **Switch Transformer** (Fedus, Zoph, Shazeer, Google, 2021, arXiv:2101.03961) — the modern MoE foundation; 1.6T params at 7× speedup.
- **GShard** (Lepikhin et al., Google, 2020) — earlier large-scale MoE.
- **Mixtral 8x7B** (Mistral AI, January 2024) — first widely-deployed open-source MoE; ~13B activated of ~47B total. Strong quality.
- **Mixtral 8x22B** (Mistral, April 2024) — ~39B activated of ~141B total.
- **DBRX** (Databricks, 2024) — ~36B activated of 132B; open weights.
- **DeepSeek-MoE / V2 / V3** — Chinese open-weight MoE family with novel routing strategies; V3 ~671B total / 37B activated, reportedly competitive with frontier dense models.
- **Qwen MoE family** — Alibaba's open MoE line.
- **Grok-1** (xAI, 2024, weights released) — 314B total MoE.
- **GPT-4** — widely *believed* to be MoE based on indirect evidence; not officially confirmed.

## 3. Key works

- **Fedus, Zoph, Shazeer. "Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity."** arXiv:2101.03961, 2021. The foundational paper.
- **Shazeer et al. "Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer."** arXiv:1701.06538, 2017. The earlier work on which Switch built.
- **Lepikhin et al. "GShard: Scaling Giant Models with Conditional Computation and Automatic Sharding."** arXiv:2006.16668, 2020.
- **Zhou et al. "Mixture-of-Experts with Expert Choice Routing."** arXiv:2202.09368, 2022.
- **Mixtral of Experts (Jiang et al., Mistral, arXiv:2401.04088, 2024).** The Mixtral 8x7B paper.
- **DeepSeek MoE / V3 technical reports** — DeepSeek's series of strong open MoE releases through 2024-2025.

## 4. Empirical results

- **Mixtral 8x7B** matched Llama 2 70B on most benchmarks while requiring less inference compute. Established that MoE is a real quality/cost win, not just a research curiosity.
- **DeepSeek-V3 (~37B activated, 671B total)** reportedly approaches GPT-4-class performance on many benchmarks at a fraction of the compute cost.
- **Training cost:** MoE models train roughly proportional to activated-parameter count, not total. A 700B-total / 40B-activated model trains for ~40B-dense cost on compute, but needs the memory of 700B to hold all experts. Cost shifts from compute to memory.
- **Inference latency:** at small batch sizes (interactive), MoE can be *slower* than dense per-token because routing overhead and worse cache locality dominate. At large batches (production serving), MoE shines.
- **Expert specialisation:** post-hoc analysis shows experts do specialise somewhat (e.g. code, math, language) but the specialisation is often subtle and brittle. The "expert per topic" mental model oversells what's actually learned.
- **Routing quality** is the biggest practical lever. Bad routing makes large MoE models perform like small dense ones; good routing unlocks the headline numbers.

## 5. Applicability to Runa

For **Heimskringla (model router)**:

- **Mixtral 8x7B at Q4_K_M** is a strong local candidate for laptop / longhall server deployments — quality close to 70B-class at ~26 GB memory footprint. Not viable on 16 GB Pi 5; viable on 32 GB laptop or dedicated server.
- **DeepSeek-V2-Lite** or smaller MoE variants are emerging as Pi-friendlier candidates when 13B-activated of 30B-total fits in 16 GB at Q4. Verify on actual hardware.
- **Cost model for routing decisions:** memory cost ~ total params; latency cost ~ activated params; quality ~ activated params (with caveats). When Heimskringla picks between dense and MoE candidates, the trade-off is "do I have the memory headroom for the bigger model that runs at smaller-model speed?"

For **deployment shape**:

- The longhall pattern (Pi runs Runa, laptop/server runs heavy inference) is a natural fit: keep MoE models on the heavier host, route to them via Tailnet HTTP. Per ADR-0002 §D-2.3 the WYRD-bridge transport auto-detects; the same pattern applies to Heimskringla provider connections.

For **understanding model evolution**:

- Frontier closed models (GPT-4o, Claude 3.5+, Gemini family) are probably (sometimes confirmed) MoE. Their cost/latency curves reflect that. Heimskringla's per-provider cost models should not assume dense behaviour.

What to avoid:

- Don't try to run a 200B-total MoE on a 32 GB machine. Memory is the constraint; activated count is irrelevant if you can't hold the weights.
- Don't run MoE models at small batch sizes expecting throughput wins. Single-user interactive inference often barely benefits from MoE's compute savings.
- Don't assume "smaller activated count = smaller quant footprint." Quantisation applies to the full weight matrices; quant ratios are similar to dense.
- Don't load MoE experts on demand from disk. Sounds good; in practice the routing decision happens too fast and disk latency dominates. Hold all experts in RAM.

## 6. Open questions

- **Expert pruning at inference time.** If most experts are rarely used for a particular workload, can the rare ones be off-loaded to disk? Some active research; tricky because routing decisions are per-token.
- **Hot-swapping experts.** Could fine-tuned domain experts be loaded and unloaded for different tasks (medical-expert, code-expert)? Modular MoE is an interesting direction.
- **MoE on Pi.** Whether Pi-class hardware (16 GB, modest CPU, no discrete GPU) can run a useful MoE depends on quantisation pushing total-param memory down enough. Borderline as of 2025.
- **Routing safety.** A router trained on biased data routes biased — a "code expert" trained mostly on English-language docs may degrade on multilingual code. Underexplored.

## 7. References (curated)

- arXiv:2101.03961 — Switch Transformer.
- arXiv:1701.06538 — Shazeer et al., the original sparsely-gated MoE.
- arXiv:2401.04088 — Mixtral of Experts.
- arXiv:2006.16668 — GShard.
- arXiv:2202.09368 — Expert Choice Routing.
- huggingface.co/blog/moe — Hugging Face's introductory MoE blog.
- mistral.ai/news/mixtral-of-experts/ — Mixtral release announcement.
- Companion docs: [[16-quantization-local-inference]] (quant interactions), [[30-llama-cpp-gguf-ecosystem]] (runtime support), [[33-model-routing-ensembles]].

# 54 — Differentiable Neural Memory: DNC, MANNs, Memorizing Transformers

**Category:** Advanced Memory & Continuity
**Runa relevance:** Muninn (advanced retrieval mechanisms), kernel (in-model memory augmentation)
**Status:** Research synthesis. Pre-LLM-era origin, currently re-emerging.
**Last touched:** 2026-05-17

---

## 1. Core idea

Differentiable memory is the idea that a neural network can be given an external addressable memory bank whose read/write operations are themselves differentiable, so that the network learns *how to use memory* via gradient descent. Early work (Neural Turing Machines, 2014; Differentiable Neural Computer, 2016) was promising on algorithmic tasks but didn't scale to natural language. The idea then re-emerged in the transformer era: *Memorizing Transformers* (Wu et al., 2022), Recurrent Memory Transformers (Bulatov et al., 2022), and recently *Larimar* (IBM Research, 2024) reframe external memory as a *key-value cache that the model is trained to query and update through end-to-end gradients*.

For Runa, this isn't a deployable substrate today — the production model is a frozen open-weights LLM not designed for end-to-end memory training. But the underlying *mechanisms* are increasingly relevant: attention-over-memory, episodic key-value stores, learned write policies, and one-shot memory editing. These show up in research-grade architectures, in some commercial offerings (Mamba-derivative architectures, Hawk/Griffin recurrent variants), and as inspiration for retrieval-augmented inference patterns Runa *can* use today.

## 2. Technical depth

**The general schema.** A network with external memory $M \in \mathbb{R}^{N \times d}$ exposes three operations:

- **Read:** given a query $q$, produce a soft read $r = \sum_i a_i M_i$ where $a = \text{softmax}(qM^T / \sqrt{d})$. This is just attention over memory rows; the gradient flows through $a$ back to $q$ and through to the upstream layers.
- **Write:** given a candidate $w$ and an address $a_{\text{write}}$, update $M \leftarrow M \cdot (1 - a_{\text{write}} e^T) + a_{\text{write}} w^T$ (write-with-erase). Differentiable too.
- **Address:** the policy for choosing where to read/write. NTM/DNC used content-based + location-based addressing; modern variants use almost exclusively content-based (attention).

**Neural Turing Machine (NTM, Graves et al. 2014).** First serious differentiable memory. Used a controller (LSTM) that emitted read/write heads. Learned to perform copy, repeat-copy, associative recall on algorithmic benchmarks. Notoriously hard to train; very expressive in theory.

**Differentiable Neural Computer (DNC, Graves et al. 2016).** NTM's successor. Added temporal linkage (a graph of which memory cell was written when, so the controller could traverse \"chains of thought\") and usage tracking (a vector indicating which cells are free for reuse). Demonstrated reasoning on synthetic graph tasks and the bAbI question-answering set. Architecturally rich; computationally costly; scaling beyond toy domains was unsolved.

**Memory-Augmented Neural Networks (MANNs).** A loose family including NTM, DNC, Memory Networks (Weston et al. 2014), and key-value memory networks. Common property: a separate memory bank that the network reads from and (often) writes to. Successful on small QA tasks; supplanted by Transformer-with-RAG once retrieval-over-frozen-corpora proved more tractable than learned write.

**Memorizing Transformers (Wu, Rabe, Hutchins, Szegedy 2022).** A transformer that, during inference, writes its own past key-value caches to an external memory and attends to them on subsequent passes. No additional trained components beyond the standard transformer — the memory is a *retrieved* set of past KVs that augment a special attention head. On long-document language modelling, it outperformed both vanilla transformers and recurrence-based variants for the parameter budget. Critically: *the model was not separately trained* to use this memory; it learned to during normal next-token training. This is the cleanest empirical case for \"large enough transformers can use external memory if you give them the channel.\"

**Recurrent Memory Transformer (RMT, Bulatov et al. 2022 → Scaling RMT 2024).** Prepends/appends special *memory tokens* to chunks; the model is trained to summarise the chunk into those tokens and read prior chunks' memory tokens. Demonstrated context lengths up to *one million tokens* effectively, on synthetic-and-real long-context tasks. Practical implementations exist on top of LLaMA-architecture base models.

**Larimar (IBM, 2024).** Adds a one-shot writable episodic memory to a frozen LLM via a trained *encoder + decoder + memory bank*. The memory can be *edited* (write a fact, erase a fact) at inference time without retraining the LLM. Demonstrated on factual editing benchmarks and long-context QA. The interesting move is decoupling: the LLM stays frozen, the memory module is the only thing trained.

**Modern recurrent alternatives.** Mamba (Gu, Dao 2023), RWKV (Peng et al. 2023), Griffin/Hawk (Google DeepMind 2024) are not exactly differentiable memory in the NTM sense, but they re-introduce *state* into sequence models in a way that supplants part of attention's job. State spaces blur the line between weights and memory. Architecturally adjacent.

**Editable/learnable knowledge in frozen models.** ROME (Meng et al. 2022), MEMIT (Meng et al. 2023), Knowledge Neurons (Dai et al. 2022) edit factual knowledge in transformer MLP layers via targeted weight updates. Not differentiable memory in the strict sense; *knowledge editing* is the closer label. Useful when one wants to update a model's belief about a fact persistently without retraining. Brittle in practice — multi-hop and contextual edits often fail.

## 3. Key works

- **Graves, A., Wayne, G., Danihelka, I.** *Neural Turing Machines.* arXiv:1410.5401, 2014.
- **Graves, A. et al.** *Hybrid computing using a neural network with dynamic external memory* (DNC). Nature 538:471–476, 2016.
- **Sukhbaatar, S., Szlam, A., Weston, J., Fergus, R.** *End-to-End Memory Networks.* NeurIPS 2015.
- **Miller, A., Fisch, A., Dodge, J., Karimi, A.-H., Bordes, A., Weston, J.** *Key-Value Memory Networks for Directly Reading Documents.* EMNLP 2016.
- **Wu, Y., Rabe, M., Hutchins, D., Szegedy, C.** *Memorizing Transformers.* ICLR 2022.
- **Bulatov, A., Kuratov, Y., Burtsev, M.** *Recurrent Memory Transformer.* NeurIPS 2022. Follow-up: *Scaling Transformer to 1M tokens and beyond with RMT.* arXiv:2304.11062, 2023.
- **Das, P. et al.** *Larimar: Large Language Models with Episodic Memory Control.* arXiv:2403.11901, 2024.
- **Gu, A., Dao, T.** *Mamba: Linear-Time Sequence Modeling with Selective State Spaces.* arXiv:2312.00752, 2023.
- **Meng, K., Bau, D., Andonian, A., Belinkov, Y.** *Locating and Editing Factual Associations in GPT* (ROME). NeurIPS 2022. *MEMIT.* ICLR 2023.

## 4. Empirical results

- *NTM / DNC* perform well on algorithmic toys (copy, sort, graph traversal) and bAbI; never matched LSTM+attention on natural language. Compute and training stability were the blockers.
- *End-to-End Memory Networks* solved nearly all bAbI tasks; supplanted by transformers everywhere else.
- *Memorizing Transformers* gave clean perplexity wins on PG-19 (long books) and ArXiv long-context. The external memory was reliably used by attention heads — visualised.
- *RMT* claimed effective context to 1M tokens with linear (in chunk count) compute. Reproductions confirm long-range retrieval works; reasoning over long ranges is weaker than retrieval.
- *Larimar* edits facts in BLEU-evaluated benchmarks at near-instant write time without harming general performance much. Editing many facts at once still degrades the model.
- *Knowledge editing methods* (ROME, MEMIT) work for surface facts; consistently fail on multi-hop ("if X was born in Y, where is the capital of Y's neighbour?"). The edits are local, not propagated.

Honest take: *for Runa today*, none of these architectures are deployable as drop-in replacements. The frontier where they're useful is (a) inspiration for retrieval design, (b) future hardware/inference upgrades that might bring RMT-class long context within reach, (c) eventual fine-tuning of the persistent-self-LoRA (see [[55-adapter-based-identity-persistence]]).

## 5. Applicability to Runa

For **Muninn**:

- The *attention-over-memory* schema is exactly the design pattern of retrieval-augmented inference: embed the query, find top-K episodes, concatenate into context. Differentiable memory shows this is principled, not just engineering convenience.
- *Importance scoring* is the analogue of usage tracking in DNC; *recency decay* is the analogue of memory ageing. The biological intuitions show up in both literatures.
- *Memorizing Transformers* validates the deeper claim: a sufficiently capable transformer *can* learn to use external memory effectively if the channel is provided. Runa's kernel can lean into this — give the model rich, well-formatted retrieved context and trust that competent open-weights LLMs will integrate it.

For **kernel inference path**:

- If Runa ever runs on hardware that supports an RMT-style chunked architecture (e.g. via a fine-tuned LLaMA), the kernel can hold *much longer* effective context. This is a long-tail consideration.
- One-shot editing (Larimar / ROME) is potentially useful for *persona corrections*: \"Runa, you do not enjoy puns\" — Volmarr would like that to stick. Today, persona prompt + retrieval handle this; a future Larimar-style module is a credible path if the persona prompt outgrows token budgets.

For **Hirð / Smiðja**:

- Memorizing-Transformer-style \"recall my own past KV cache\" is conceptually a *workspace memory* for a long single thought. Could be useful for a deliberation subagent that thinks through a complex problem over many internal steps.

What to avoid:

- **Treating differentiable memory as a panacea.** It is theoretically elegant; deployed systems are rare; today's practical wins are mostly via retrieval-augmented inference (RAG) not learned-write memory.
- **Implementing NTM/DNC from scratch for Runa.** Training stability alone is a research project. Don't.
- **Confusing knowledge editing with persistent identity.** Editing weights is brittle and locality-limited. Identity belongs in the substrate (see [[52-cross-session-persistent-identity]]), not in weight surgery.
- **Coupling Runa to a specific exotic architecture.** Open-weights LLM choices change. Keep architectural commitments at the *protocol* level (RAG-style), not at the *internal-mechanism* level.

## 6. Open questions

- **Can frozen LLMs reliably use externally-written memory tokens at inference time without specific training?** Memorizing Transformers say yes for some patterns; the limits are unclear.
- **One-shot vs. consolidated edits.** Larimar handles isolated edits well; many edits at once degrade. The right pacing is unsolved.
- **State-space architectures (Mamba etc.) as ongoing memory.** Their recurrent state effectively *is* a memory; whether that state can be made addressable, written by an agent, persistent across sessions, is an open architectural design space.
- **Verifiable memory.** Differentiable memory is hard to audit (it's vectors). For Runa, *symbolic* memory must remain the primary substrate even if vectors index it.
- **Continual learning from differentiable memory.** Can write patterns accumulated across sessions be distilled back into weights — a controllable form of \"sleep\"? Active research; not yet deployable.

## 7. References (curated)

- arXiv:1410.5401 — Graves et al., *Neural Turing Machines.* The original.
- Nature 538:471 — Graves et al., *DNC.* The richest classical formulation.
- arXiv:2203.08913 — Wu et al., *Memorizing Transformers.* The cleanest modern motivation.
- arXiv:2304.11062 — Bulatov et al., *Scaling RMT.* Million-token claims with reproductions.
- arXiv:2403.11901 — Das et al., *Larimar.* Editable episodic memory atop frozen LLMs.
- arXiv:2312.00752 — Gu and Dao, *Mamba.* Recurrent state in modern sequence models.
- arXiv:2210.07229 — Meng et al., *MEMIT.* Knowledge editing at scale.
- Companion docs: [[01-memgpt-os-memory-hierarchies]], [[04-rag-evolution]], [[18-long-context-attention]], [[55-adapter-based-identity-persistence]], [[58-memory-augmented-transformers]].

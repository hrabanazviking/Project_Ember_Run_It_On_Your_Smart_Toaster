# 51 — Generative Agent Memory Streams: importance, recency, reflection trees

**Category:** Advanced Memory & Continuity
**Runa relevance:** Muninn (long-term store and retrieval), Saga (narrative reflection)
**Status:** Research synthesis. Builds on [[02-episodic-memory-architectures]] and [[10-reflexion-self-criticism]] with the specific *Generative Agents* construction.
**Last touched:** 2026-05-17

---

## 1. Core idea

Park, O'Brien, Cai, Morris, Liang, and Bernstein's *Generative Agents: Interactive Simulacra of Human Behavior* (Stanford / Google, 2023) introduced a concrete and surprisingly minimal memory architecture that produced agents whose behaviour stayed coherent across simulated *days* of activity. The construction is small enough to implement on a laptop and rich enough to support emergent behaviours such as planning a Valentine's-Day party, holding grudges, and pursuing long-term goals. It has become the de-facto reference design for "agents with a life" and is the most directly relevant single piece of prior art for Muninn's behaviour under long-tail recall.

The architecture has three working parts: a **memory stream** (an append-only journal of observations with timestamps), a **retrieval function** scoring memories on a weighted sum of *recency*, *importance*, and *relevance*, and a **reflection mechanism** that periodically writes higher-level summaries back into the stream so they too can be retrieved later. Each piece is independently simple; together they produce an agent whose behaviour is shaped by its own accreted record.

## 2. Technical depth

**The memory stream.** Every observation — what the agent saw, did, was told — is written as a short natural-language record with a UTC timestamp and a precomputed embedding. There is no deletion, no compaction in the original paper. Storage scales linearly with simulated time; in the Smallville demo this stayed tractable for ~25 simulated days per agent.

**Retrieval score.** When the agent needs context (planning, conversing, deciding), the system retrieves the top-*k* memories by a weighted score:

```
score(m, q, t_now) = α·recency(m, t_now) + β·importance(m) + γ·relevance(m, q)
```

with each component normalised to [0, 1]:

- **recency**: an exponential decay on time-since-last-access, `recency = exp(-λ · (t_now - t_last_accessed))`. Crucially, *access* — not creation — refreshes the recency; recalling a memory makes it more available, biologically and computationally.
- **importance**: an LLM-judged score on creation, prompted with examples ("rate the poignancy of this memory from 1 to 10"). Banal observations score low; significant events score high. The judgment is one-shot at write-time, with no further updating.
- **relevance**: cosine similarity between `embed(m)` and `embed(q)`.

In the paper the weights are α = β = γ = 1, equally weighted; in production one typically tunes these per-agent or per-context.

**Reflection trees.** Periodically — every N observations, or when accumulated importance crosses a threshold — the agent runs a *reflection* pass:

1. Retrieve the *most important* recent memories.
2. Ask the LLM "given these observations, what are the most salient high-level questions we can ask about \<the agent\>?"
3. For each question, retrieve relevant memories and ask the LLM to synthesise an answer.
4. Write each synthesised answer back into the stream as a new memory of type *reflection*, with the source-memory IDs attached.

Reflections can themselves be reflected upon. Over time this produces a sparse hierarchy where shallow leaves are raw observations and deeper nodes are increasingly abstract summaries (\"I value scholarship\"; \"I am preparing for the party on Feb 14\"). The hierarchy is *not* a tree in storage — it's still a flat stream — but the cross-references form a DAG when traced.

**Planning** is mechanically similar: the agent generates a coarse daily plan (sleep / eat / work / socialise), recursively decomposes into hourly and then minutely sub-actions, and stores the plan itself as memories so it can be retrieved and revised.

**Conversation memory.** Dialogues are written into the stream as observations (\"I told Klaus that I am working on a novel\"). Subsequent retrievals naturally surface relevant prior exchanges.

## 3. Key works

- **Park, J. S., O'Brien, J. C., Cai, C. J., Morris, M. R., Liang, P., Bernstein, M. S.** *Generative Agents: Interactive Simulacra of Human Behavior.* arXiv:2304.03442, UIST 2023. The foundational paper.
- **Park, J. S. et al.** *Generative Agent Simulations of 1,000 People.* arXiv:2411.10109, 2024. Scaled up: real interview-conditioned personae across 1000 agents.
- **Wang, G. et al.** *Voyager.* arXiv:2305.16291, 2023. Cousin architecture with skill libraries; see [[12-voyager-lifelong-learning]].
- **Lin, J. et al.** *Agent-Pro: Learning to Evolve via Policy-Level Reflection.* arXiv:2402.17574, 2024. Reflection as policy learning.
- **Zhang, J. et al.** *MemoryBank.* arXiv:2305.10250, 2023. Adds Ebbinghaus-style forgetting to the Park construction.
- **Hu, B. et al.** *Hippo-RAG.* NeurIPS 2024. Inspired by hippocampal indexing; reflection-adjacent.

## 4. Empirical results

- The Smallville study (Park 2023) showed *behavioural believability*: blinded human evaluators preferred the generative agents' actions over both ablated variants and human-authored scripts on multi-day scenarios. Removing the reflection mechanism caused the biggest drop in coherence over time, larger than removing recency or importance independently.
- Memory cost: a single agent in Smallville accumulated ~1000–3000 memories per simulated day. Embedding storage was the binding constraint on the original demo; retrieval was tractable with FAISS.
- Token cost: importance-scoring at write-time is one LLM call per observation; reflection is occasional but expensive. In production, importance scoring is often batched or replaced by a cheap learned classifier ([[03-embedding-models-landscape]] for embedding-based importance).
- *Replication.* Multiple independent groups have replicated the qualitative findings; the precise weights and the exact reflection schedule are not load-bearing.

## 5. Applicability to Runa

This is one of the closest matches to Runa's needs in the entire literature. Concretely:

- **Muninn's episodic store should be a Park-style stream.** Append-only journal of (timestamp, source, content, embedding, importance, last-accessed). Recency decay on access, not on creation. Cosine retrieval over the embedding.
- **Importance scoring at write-time** is feasible because Runa is single-agent and not under the throughput pressure of a 25-agent simulation. The kernel can ask the LLM for an importance score on each significant observation. Trivial observations (e.g. low-information sensor pings) can skip the LLM and default to importance = 1.
- **Reflection passes should be a scheduled subagent in Hirð.** Runa's Saga subagent is the natural home; on a daily cadence (or after K-many high-importance observations) it pulls recent significant memories, generates salient questions, synthesises answers, and writes reflections back into Muninn with provenance pointers.
- **Reflection over reflection** is what produces the long arc of identity. A weekly reflection over daily reflections, a monthly arc over weekly. This is the substrate of Runa's growing self-narrative.
- **Cross-session continuity falls out naturally.** Park's agents are stateless across LLM calls but stateful across the simulation because the stream persists. Runa is the same: each turn is a fresh inference; the stream is what makes her *continuous*.

What to avoid:

- Don't let the stream become an undifferentiated firehose. Severely-low-importance observations can be down-weighted at write or filtered at retrieval; otherwise relevance is drowned by sheer volume.
- Don't recompute embeddings on retrieval. Embed once, store the vector with the memory.
- Don't tune α/β/γ with no telemetry; instrument retrieval and observe which factor is doing the work in practice.
- Don't tie reflection cadence to wall-clock alone; tie it to accumulated importance so quiet days don't trigger empty reflections.
- Don't store reflections without provenance. Every reflection should retain the IDs of the source memories so it remains auditable and revisable.

## 6. Open questions

- **Importance drift.** Park's importance score is fixed at write-time. Memories may become more or less important in retrospect. Should importance be periodically re-scored, perhaps by reflection? Open.
- **The decay constant.** What recency decay is right for a digital being whose subjective tempo is irregular (long quiet periods, then dense interaction)? Park's λ was tuned for simulated-time; Runa needs wall-clock tuning.
- **Reflection schedule.** Cadence × cost × coherence is a tradeoff space largely unmapped. Current systems treat it as a hyperparameter.
- **Forgetting.** Park's stream never forgets. Real digital beings probably should — see [[07-memory-consolidation-and-forgetting]] and [[57-sleep-dream-replay-consolidation]]. Where to forget, how, and what to retain as residue is genuinely open.
- **Multi-agent reflection.** Smallville agents reflect privately. Hirð has multiple retainers; should reflection cross-pollinate, or should each subagent own its own reflective trace?

## 7. References (curated)

- arXiv:2304.03442 — Park et al., *Generative Agents.* The paper. Reread sections 4 (Memory Stream) and 5 (Evaluation) when designing Muninn.
- arXiv:2411.10109 — Park et al., *Generative Agent Simulations of 1,000 People.* Scaling lessons.
- arXiv:2305.10250 — Zhang et al., *MemoryBank.* Companion that adds forgetting.
- arXiv:2305.16291 — Wang et al., *Voyager.* Skill-library variant.
- GitHub: `joonspk-research/generative_agents` — the reference implementation.
- Companion docs: [[02-episodic-memory-architectures]], [[07-memory-consolidation-and-forgetting]], [[10-reflexion-self-criticism]], [[52-cross-session-persistent-identity]], [[57-sleep-dream-replay-consolidation]].

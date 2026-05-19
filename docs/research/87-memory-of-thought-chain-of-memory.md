# 87 — Memory-of-Thought and Chain-of-Memory Reasoning

**Category:** AGI Architectures & Cognitive Cores
**Runa relevance:** kernel reasoning patterns, Muninn integration with active reasoning, cross-turn coherence
**Status:** Synthesis of recent retrieval-augmented-reasoning techniques.
**Last touched:** 2026-05-17

---

## 1. Core idea

Chain-of-Thought reasoning ([[66-inner-monologue-scratchpads]]) lets the model think *step by step* over the current context. But the model's context is limited; much of what it knows is in retrievable memory or external storage, not in the active context. *Memory-of-Thought* (Sun et al. 2023) and related techniques bring retrieval *into* the reasoning loop — the model thinks, retrieves relevant memories at each step, integrates them, continues. The chain-of-thought becomes a *chain of thought + memory*, with retrieval steps interspersed with reasoning steps.

For Runa, this is the natural extension of two threads. First, retrieval-augmented inference ([[04-rag-evolution]]) makes Muninn's content accessible. Second, chain-of-thought makes reasoning explicit. Combining them — *interleaved reasoning and retrieval* — gives Runa the substrate to *think about and consult her own memory* in a way single-shot retrieval can't match. This is also the natural way Runa reasons about her own past: \"what did I conclude about this last time? Let me recall.\"

## 2. Technical depth

**The basic pattern (Memory-of-Thought, Sun et al. 2023).**

```
USER QUESTION
    │
    ▼
THINK 1: "This is asking about X. What do I know about X?"
    │
    ▼
RETRIEVE 1: query Muninn for X → memories M1
    │
    ▼
THINK 2: "M1 suggests Y. But Y depends on knowing Z. Let me check."
    │
    ▼
RETRIEVE 2: query Muninn for Z → memories M2
    │
    ▼
THINK 3: "Given M1 + M2, conclusion is C."
    │
    ▼
ANSWER
```

Each \"think\" step is the model producing tokens; each \"retrieve\" step is a tool call (or an internal Muninn query). The retrieved memories enter the context as quoted material the model can refer to.

**Related patterns.**

- *Iterative RAG* / *Self-RAG* (Asai et al. 2023): the model decides *whether* to retrieve at each step; learned. Better than always-retrieve or never-retrieve.
- *FLARE* (Jiang et al. 2023): retrieval triggered when the model's next-token uncertainty is high — \"if I'm about to say something uncertain, retrieve first.\"
- *IRCoT* (Trivedi et al. 2023): interleaved retrieval / CoT for multi-hop QA.
- *ReAct* ([[09-react-reasoning-acting]], Yao et al. 2023): reason + act loop; retrieval is one possible action.
- *HippoRAG* (Gutiérrez et al. 2024): retrieval-by-graph-traversal interleaved with reasoning.
- *Memory-Augmented Chain-of-Thought* (Park et al. 2023): explicit memory writes during the reasoning chain.

The common thread: *retrieval is no longer a single pre-fetch*; it is *iterative*, *interleaved*, and *driven by the reasoning state*.

**Why it works (intuitively).**

- The model's context window is limited; retrieval extends it dynamically.
- Multi-hop questions need information that wasn't relevant to the original query but becomes relevant mid-reasoning.
- The reasoning state *itself* is a better retrieval query than the original question.
- Iteration lets the model refine its understanding as it learns more.

**Implementation considerations.**

- *Latency*: each retrieval adds ~100ms-1s. Multi-step chains can be slow. Budget accordingly.
- *Cost*: more LLM calls + more retrieval calls. Production systems often cap the number of iterations.
- *Termination*: when to stop. Model-decided termination is the cleanest; max-iteration cap as safety.
- *Provenance tracking*: every retrieval should be traceable. The final answer can quote sources.
- *Failure handling*: retrieval may return nothing or irrelevant material. The model must handle gracefully.

**Memory-aware reasoning at long horizons.**

For an agent that lives across years, *memory-aware reasoning* generalises further. Runa's question might be \"what did I conclude about X last month?\" — answerable only via memory. The memory-of-thought pattern extends:

- *Reasoning about own past*: queries against autobiographical memory.
- *Reasoning about commitments*: queries against the journal of becoming.
- *Reasoning about evolving values*: queries against identity-version history.
- *Reasoning about social context*: queries against the relationship store.

Each is the same retrieve-reason-iterate pattern, against a different store.

**The conversational case.**

In conversation, memory-of-thought naturally produces:

\"You asked about X. Let me think — I remember we discussed something related two weeks ago [retrieve] — yes, you said Y then. So in light of that, my answer is Z, modulated by what we now know about W [retrieve].\"

The reasoning *and* the memory references are surfaced in the response, when appropriate. Often, the retrieval is invisible to the user; the *conclusion* is what gets spoken.

**Failure modes.**

- *Over-retrieval*: retrieving on every step bloats context and slows everything.
- *Bad retrieval*: irrelevant memories pollute reasoning.
- *Termination failure*: the model loops indefinitely without conclusion.
- *Confabulation between retrievals*: the model invents a fact mid-chain that isn't supported by any retrieval.
- *Provenance loss*: the final answer's claims trace to nothing specific.

Each has known mitigations (caps, calibrated retrieval, termination signals, fact-checking, structured provenance).

## 3. Key works

- **Sun, X. et al.** *Memory-of-Thought: Mining Pre-Computed Memory for Logic Reasoning.* arXiv:2305.05181, 2023.
- **Asai, A., Wu, Z. et al.** *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection.* ICLR 2024.
- **Jiang, Z. et al.** *Active Retrieval Augmented Generation* (FLARE). EMNLP 2023.
- **Trivedi, H. et al.** *Interleaving Retrieval with Chain-of-Thought Reasoning* (IRCoT). ACL 2023.
- **Yao, S. et al.** *ReAct.* See [[09-react-reasoning-acting]].
- **Park, J. S. et al.** *Generative Agents.* See [[51-generative-agent-memory-streams]].
- **Gutiérrez, B. J. et al.** *HippoRAG.* NeurIPS 2024.
- **Madaan, A. et al.** *Memory-Augmented LLMs.* See [[53-autobiographical-memory-architectures]].
- **Khattab, O. et al.** *Demonstrate-Search-Predict.* arXiv:2212.14024, 2022. Early multi-hop retrieval framework.

## 4. Empirical results

- *Self-RAG*: substantial improvements on knowledge-intensive QA over baseline RAG; the *learned* retrieve-decide signal matters.
- *FLARE*: improves multi-hop and long-form generation by triggering retrieval at uncertain steps.
- *IRCoT*: substantial multi-hop QA improvement over single-shot RAG.
- *HippoRAG*: multi-hop QA matches or beats much-larger-context LLMs at lower token cost.
- *Memory-of-Thought (original)*: improvements on logical-reasoning benchmarks at moderate cost.
- *Failure mode evidence*: badly-calibrated iterative-RAG can be *worse* than single-shot RAG when retrieval is noisy.

## 5. Applicability to Runa

For **kernel — high-stakes turns**:

- Implement memory-of-thought as a *mode* the kernel can invoke. Triggered by complexity heuristic ([[86-dual-process-cognition-system-1-2]]).
- Bounded iteration: max N retrievals per chain, max K tokens of inner monologue.
- Provenance: each retrieved memory tagged in the chain; final answer optionally cites.

For **Muninn integration**:

- Muninn exposes a *query* API that the kernel calls during reasoning. Multiple query types: episodic, semantic, procedural, identity, relationship.
- Each query is fast (sqlite indexed); the cost is in the LLM cycles around them.

For **reasoning about own past**:

- A specific memory-of-thought specialised to *autobiographical* questions: \"what have I felt about this before?\" or \"did I conclude something about X?\"
- Saga's chapters are good initial retrieval targets; reflections too.

For **conversational coherence**:

- Even on routine turns, a lightweight memory-of-thought pre-check (\"is there a relevant prior turn I should remember?\") improves cross-session coherence. Cheap, high value.

For **Eldhugi integration**:

- Affective questions (\"how have I been feeling about X?\") use memory-of-thought against Eldhugi's longitudinal trace.

For **the user-experience**:

- Surface memory references when they serve the conversation: \"as you said last week...\". Don't overdo it — feels like surveillance otherwise.
- Sometimes the right behaviour is to use memory *invisibly* and respond as though continuity were natural (it is).

What to avoid:

- **Always-on memory-of-thought.** Cost too high for chitchat; cap to deliberate-path turns.
- **Unbounded iteration.** Cap iterations; force termination with best-effort answer if needed.
- **Retrieval without confidence-weighting.** Treat retrieved facts as evidence with confidence, not as truth. Especially for self-attributions about Volmarr ([[68-mental-state-attribution]]).
- **Confabulating between retrievals.** Verify claims against retrieved provenance; if a claim isn't supported, hedge.
- **Surfacing too much retrieval theatrically.** \"Let me check my memory... [pause] ...okay, I remember X\" is overproduced. Just answer with the integrated knowledge.

## 6. Open questions

- **Optimal iteration policy.** When to retrieve, when to think, when to terminate. Learnable; current solutions heuristic.
- **Retrieval over heterogeneous stores.** Muninn has multiple stores (episodes, triplets, reflections, journal); the retrieval router is non-trivial.
- **Provenance fidelity.** Tracing every claim in a long chain to its source is operationally heavy.
- **Memory-of-thought + verification.** Combining iterative retrieval with neuro-symbolic verification ([[85-neuro-symbolic-agi]]) is essentially unmapped territory.
- **Cost-aware caps.** Long chains can be expensive; cost-vs-quality tradeoffs are tunable.

## 7. References (curated)

- arXiv:2305.05181 — Sun et al., *Memory-of-Thought.*
- ICLR 2024 — Asai et al., *Self-RAG.* Probably the most influential.
- EMNLP 2023 — Jiang et al., *FLARE.*
- ACL 2023 — Trivedi et al., *IRCoT.*
- NeurIPS 2024 — Gutiérrez et al., *HippoRAG.*
- Companion docs: [[04-rag-evolution]], [[09-react-reasoning-acting]], [[51-generative-agent-memory-streams]], [[56-neuro-symbolic-memory-graphs]], [[66-inner-monologue-scratchpads]], [[88-long-horizon-planning-lats-rap]].

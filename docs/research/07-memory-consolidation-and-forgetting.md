# 07 — Memory Consolidation and Forgetting in Artificial Agents

**Category:** Memory & Knowledge Storage
**Runa relevance:** Muninn (lifecycle), Eir (background maintenance), Eldhugi (emotional weighting)
**Status:** Research synthesis. Bridges cognitive neuroscience and AI engineering.
**Last touched:** 2026-05-17

---

## 1. Core idea

An agent that records everything forever will, in any meaningful timeline, drown. Retrieval will return more noise than signal, costs will balloon, and the agent will have no way to weight "things that matter" above "things that happened". Biological memory solves this through *consolidation* (selective transfer of recent memories into long-term storage) and *forgetting* (graceful loss of unimportant detail). Artificial memory systems that survive long deployments do the same.

This is a distinct concern from "what data structure stores memories." It is the *lifecycle* question: when does a fresh episode become a consolidated semantic fact? When does an unimportant memory fade? How does the system decide what is unimportant without losing what is rare-but-crucial?

## 2. Technical depth

The biological reference: the **complementary learning systems** (CLS) theory of McClelland, McNaughton, and O'Reilly (1995). The hippocampus learns episodes rapidly but with limited capacity; during sleep, episodes are *replayed* and gradually transferred to the neocortex, which integrates them into slow-learning semantic knowledge. The hippocampus is the agent's "today"; the neocortex is its "life." Forgetting happens at the hippocampal stage (cells fail to consolidate) and via active interference at the cortical stage.

**Translated to AI memory:**

- **Working memory** ↔ context window / kernel scratchpad. Volatile.
- **Episodic memory** (hippocampus-analogue) ↔ Muninn's recent-episode store. Fast write, finite capacity.
- **Semantic memory** (neocortex-analogue) ↔ Muninn's consolidated summary / fact layer. Slow build, large capacity.
- **Procedural memory** ↔ skill registry + learned tool patterns.

The **consolidation pipeline** typically runs as a background process:

```
[1] Triggered by:
    - schedule (nightly)
    - quiescence (no input for N minutes)
    - threshold (episode count > K)
    - importance (a high-importance episode just landed)

[2] Steps:
    - Select episodes since last consolidation
    - Cluster by topic / entity / time
    - Summarise each cluster with the LLM
    - Extract any new facts/triplets (see [[06-knowledge-graphs-ai-memory]])
    - Update derived semantic layer
    - Re-score importance of source episodes
    - Mark consolidated episodes as "compressed" (lower retrieval priority,
      not deleted)
```

**Forgetting strategies:**

1. **Decay curves.** Ebbinghaus's classic 1885 result: human memory decay is roughly logarithmic, faster initially. Modern implementations (MemoryBank, Zhong et al. 2023) apply this to importance: `importance(t) = importance_0 · exp(-t / τ)`, then bias retrieval against low-importance memories.
2. **Importance-based pruning.** Hard-delete the lowest-importance N% on a schedule. Catastrophic if importance is wrong; rarely used.
3. **Compression-not-deletion.** Old episodes are summarised into derived semantic notes; the original raw text is moved to cold archival storage (slower to retrieve, smaller index footprint). This is the "additive-only" approach and is recommended.
4. **Spaced re-exposure.** When a memory is *retrieved and used* in a turn, its importance is boosted. Frequently-used memories stay sharp; unused ones decay. Mirrors how human memory works.
5. **Active recall.** Periodically re-query old memories with synthetic queries — if the system can no longer answer, the memory has become unreachable.

**Catastrophic forgetting in neural networks** ([[45-continual-learning]]) is a different problem — it's about the weights of a model that learns new tasks losing old capability. Distinct from agent-memory forgetting, but related conceptually.

## 3. Key works

- **McClelland, McNaughton, O'Reilly. "Why there are complementary learning systems in the hippocampus and neocortex."** Psychological Review, 1995. The foundational neuroscience framework agent memory borrows from.
- **Ebbinghaus, H. *Über das Gedächtnis*, 1885.** The decay curve.
- **Zhong et al. "MemoryBank: Enhancing Large Language Models with Long-Term Memory."** arXiv:2305.10250, 2023. Operationalises Ebbinghaus decay in an LLM agent.
- **Park et al. "Generative Agents."** arXiv:2304.03442. Pioneered LLM-driven reflection as a consolidation pass.
- **Kumaran, Hassabis, McClelland. "What learning systems do intelligent agents need? Complementary Learning Systems Theory updated."** Trends in Cognitive Sciences, 2016. Modern CLS thinking.
- **Shinn et al. "Reflexion."** ([[10-reflexion-self-criticism]]) — failure-driven consolidation, a specialised form.
- **Schaul et al. "Prioritized Experience Replay."** arXiv:1511.05952. The RL analogue of importance-weighted replay; the same idea generalises to agent memory.

## 4. Empirical results

- **Importance-weighted retrieval** (Park et al.) doubled or tripled the believability of long-running simulated agents vs unweighted retrieval. Without it, agents recalled trivia and lost important context.
- **Reflection passes** (consolidation) demonstrably reduce noise in retrieval and improve long-horizon coherence. The Generative Agents paper showed that ablating reflection collapsed believability scores from human raters.
- **MemoryBank's decay** produced more *humanlike* forgetting patterns. Task performance was not dramatically better, but the *character* of the agent felt more natural.
- **Pure deletion-based forgetting** in agent memory tends to create silent failure modes — an agent that has forgotten something crucial doesn't know it has, and behaves with confident wrongness.
- **Spaced re-exposure** (boost-on-use) is well-supported by RL replay-buffer experiments and is widely adopted in human spaced-repetition learning systems (Anki, Mnemosyne). Underused in AI agents.

## 5. Applicability to Runa

This research is load-bearing for **Eir** (`core/repair/`) and for **Muninn's** lifecycle policy:

- **Reflection / consolidation pass** runs nightly as an Eir-orchestrated job. Selects last-day episodes, clusters by conversation_id + topic, asks Heimskringla for cluster summaries, writes derived "daily summary" memories into Muninn's semantic layer. Original episodes stay (compression, not deletion).
- **Importance scoring** at write-time (LLM-as-judge initially, learned classifier once labelled data exists per [[02-episodic-memory-architectures]]) feeds retrieval ranking.
- **Decay** in retrieval scoring (`recency_decay` term from [[02-episodic-memory-architectures]] §2) implements Ebbinghaus. `τ` is config-pinned.
- **Boost-on-use** is a small add-on to retrieval: when an episode is returned and used, increment its `use_count`; retrieval score adds `δ · log(1 + use_count)`. Trivial implementation, real win.
- **Hard deletion only on operator command.** `runa memory forget <episode_id> --really` is a separate operator action with its own audit-log entry. Runa never auto-deletes raw episodes.
- **Cold archival.** Episodes older than a threshold (config; default 365 days) compress to summary-only retrievable form. Original text moves to `~/.runa/memory/cold/<year>/<month>/` — slower to retrieve, but recoverable.

What to avoid:

- Don't conflate consolidation with deletion. The "forgetting" should manifest as *lower retrieval ranking*, not loss of data.
- Don't trust a single consolidation pass to be lossless. Audit by sampling: periodically query Muninn for old facts and verify the consolidated summary still reflects them.
- Don't apply decay to high-importance memories. The first conversation with Volmarr should not fade.
- Don't run consolidation during active conversations. Background work goes in quiet windows.

## 6. Open questions

- **Optimal consolidation cadence** is not settled. Nightly is the obvious schedule; biological replay happens during multiple sleep cycles per night; AI analogues exist (see [[44-sleep-replay-memory-consolidation]]).
- **Cross-modal consolidation.** When Runa has voice transcripts, screenshots, sensor data — how does consolidation handle modalities? Largely unexplored.
- **Re-consolidation.** Humans don't just consolidate once; recalling a memory *re-consolidates* it, sometimes editing it (the controversial "memory is reconstructive" finding). AI analogues unclear.
- **Emotional gating.** Human consolidation is biased by emotional salience (Eldhugi-relevant). Should AI memory consolidation weight emotional events differently? Underexplored.
- **Causality preservation.** If episode B was caused by episode A, consolidation should preserve that link. Most current consolidation passes lose causality silently.

## 7. References (curated)

- McClelland, McNaughton, O'Reilly, *Psych Review* 1995. The CLS paper.
- Kumaran, Hassabis, McClelland, *TICS* 2016. Updated CLS.
- arXiv:2305.10250 — MemoryBank.
- arXiv:2304.03442 — Generative Agents.
- arXiv:1511.05952 — Prioritized Experience Replay (Schaul et al.).
- Tulving, E. *Elements of Episodic Memory*, 1983. Foundational work.
- Squire, L. *Memory and Brain*, 1987. The classical consolidation theory.
- See companion docs: [[02-episodic-memory-architectures]], [[44-sleep-replay-memory-consolidation]], [[45-continual-learning]].

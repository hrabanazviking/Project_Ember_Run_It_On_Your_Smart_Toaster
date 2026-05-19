# 02 — Episodic Memory Architectures for AI Agents

**Category:** Memory & Knowledge Storage
**Runa relevance:** Muninn (memory OS), identity (continuity of self), Eldhugi (emotional context)
**Status:** Research synthesis.
**Last touched:** 2026-05-17

---

## 1. Core idea

In cognitive science (Tulving, 1972), human memory splits into at least three kinds: **episodic** (specific events: "what happened at dinner last Tuesday"), **semantic** (general facts: "the capital of Iceland is Reykjavík"), and **procedural** (how-to: "how to ride a bicycle"). LLMs default to a degenerate form of semantic memory baked into weights, plus whatever you put in the prompt. They have no native episodic memory at all.

Agent designers since 2023 have been bolting episodic memory on. The shape that has emerged across multiple successful systems looks roughly the same: a stream of timestamped *episodes* (turn-sized or event-sized), each tagged with who/where/when, indexed by both recency and semantic similarity, with periodic *reflection* passes that compress episodes into derived semantic notes.

The technique matters because continuity-of-self over time is what makes an agent feel like a person rather than a re-spawned chatbot. Without episodic memory, every session is a stranger.

## 2. Technical depth

A canonical episodic-memory schema for an AI agent looks like:

```python
Episode {
  episode_id:        UUID
  conversation_id:   UUID         # groups episodes into threads
  timestamp:         datetime     # UTC
  speaker:           str          # "user" / "runa" / "tool" / agent_id
  text:              str          # what was said / done
  modality:          str          # "speech" / "text" / "image" / ...
  surface:           str          # "cli" / "voice" / "gateway/discord" / ...
  tools_invoked:     list[ToolCall]
  embedding:         Vector[D]    # for similarity recall
  emotional_delta:   EmotionalDelta  # mood / energy / relational shift
  importance:        float        # learned or hand-tagged salience score
  references:        list[UUID]   # links to prior episodes this depends on
}
```

The *importance* field is what separates an episodic store that grows usefully from one that collapses into noise. Park et al. (2023) compute importance with the LLM itself: "rate this memory's relevance on a scale 1–10." Tag-then-cluster approaches sort episodes by importance + recency at retrieval time.

A reflection pass — run hourly, nightly, or at quiet moments — reads the last N episodes, distils them into 1–3 higher-level observations ("user has been frustrated with X this week"), and stores those as new memories that themselves carry importance scores. Reflection layers can stack: episodes → daily summaries → weekly themes → long-term narratives. This is the *hierarchical episodic-to-semantic consolidation* pattern.

Retrieval is typically a weighted combination of:

```
score(episode) = α · semantic_similarity(query, episode.embedding)
              +  β · recency_decay(now − episode.timestamp)
              +  γ · importance
```

α, β, γ are config-tuned per use case. Park et al. used roughly equal weights; production systems often emphasise recency for conversational continuity and importance for long-term identity.

## 3. Key works

- **Park, O'Brien, Cai, Morris, Liang, Bernstein. "Generative Agents: Interactive Simulacra of Human Behavior."** Stanford + Google, arXiv:2304.03442, April 2023. The foundational paper for LLM-driven episodic memory in agent simulation.
- **Sumers, Yao, Narasimhan, Griffiths. "Cognitive Architectures for Language Agents."** arXiv:2309.02427, 2023. Frames episodic / semantic / procedural / working memory in a unified taxonomy.
- **MemoryBank** (Zhong et al., arXiv:2305.10250) — agent memory with forgetting curves modelled on Ebbinghaus's classic decay function.
- **A-Mem** (autonomous memory operations, multiple groups 2024) — investigates self-organising episodic structure.
- **Letta** (post-MemGPT) — productionised some of these patterns.

## 4. Empirical results

- Generative Agents (Park et al.) demonstrated that LLM-driven episodic memory + reflection produces *believable behavioural continuity* over many simulated days — agents remembered previous conversations, formed opinions, planned around past experiences. The believability was assessed by human judges who preferred the full-memory agents over ablations missing reflection or missing importance scoring.
- MemoryBank's Ebbinghaus forgetting curve gave more human-like recall patterns (fresh memories sharper, old memories fuzzy unless re-accessed) but did not dramatically improve task performance — useful for personality, not for QA.
- Importance scoring by the LLM itself is noisy. Multiple groups have shown that learned importance models (a small classifier trained on labelled episodes) outperform LLM-as-judge for retrieval ranking.

## 5. Applicability to Runa

This is the load-bearing pattern for **Muninn** episodic storage. Specifically:

- The schema above is a strong starting point for Runa's `Episode` row type — it covers the structure DATA_FLOW.md §7 promises (one episode per turn, with tool-effect addenda).
- The **reflection pipeline** maps to a background skill in Eir/Hirð. Run nightly when Runa is quiet. Reflections write into `archival_storage` per the MemGPT pattern ([[01-memgpt-os-memory-hierarchies]]).
- The **importance score** is necessary for retrieval to behave well at scale. Recommend starting with LLM-as-judge importance, then upgrading to a learned classifier once Muninn has 10K+ labelled episodes.
- The **conversation_id-aware retrieval** (DATA_FLOW.md §6) maps to filtering by conversation_id before computing similarity for in-thread continuity, then expanding to cross-thread for the reunion-rule.
- The **emotional_delta field** lets Eldhugi's journal integrate with Muninn without duplicating storage.

What to avoid:

- Don't compute embeddings at write-time only. Re-embedding on model upgrades is a migration; design for it now (a `runa.migrations` script that re-embeds with the new model).
- Don't store importance as a single immutable number. Importance changes as Runa's life accrues — a memory of "meeting Volmarr" stays important; a memory of "what I ate Tuesday" decays. Importance should be re-scored periodically.
- Don't let the reflection skill mutate or delete episodes. Reflections are *derived* memories; the raw episodes remain.

## 6. Open questions

- **What is the right reflection cadence?** Hourly is too noisy; weekly may miss patterns. The sleep-replay analogue ([[44-sleep-replay-memory-consolidation]]) suggests biological inspiration but doesn't give specific numbers.
- **How does emotional weighting interact with importance?** Emotionally charged events are easier to recall in humans — should Eldhugi influence Muninn's retrieval scoring directly?
- **Procedural memory.** Episodic and semantic are well-trodden; procedural (how Runa learned to do something) is barely explored. Possible overlap with skill-registry runtime telemetry.
- **Privacy and right-to-forget.** What does it mean for Runa to *delete* a memory cleanly when the memory's content has propagated through reflection into other memories?

## 7. References (curated)

- arXiv:2304.03442 — Generative Agents (Park et al.).
- arXiv:2309.02427 — Cognitive Architectures for Language Agents (Sumers et al.).
- arXiv:2305.10250 — MemoryBank.
- arXiv:2310.08560 — MemGPT (companion read, [[01-memgpt-os-memory-hierarchies]]).
- Tulving, E. "Episodic and Semantic Memory." In *Organization of Memory*, 1972. The cognitive-psychology foundation.
- Ebbinghaus, H. *Über das Gedächtnis*, 1885. The forgetting-curve work MemoryBank operationalises.

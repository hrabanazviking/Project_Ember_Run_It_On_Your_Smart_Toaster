# 44 — Sleep, Replay, and Memory Consolidation Analogues

**Category:** Cognitive Architecture & Neuroscience
**Runa relevance:** Eir (background maintenance), Muninn (consolidation cadence), continual learning patterns
**Status:** Research synthesis. Neuroscience-inspired engineering pattern.
**Last touched:** 2026-05-17

---

## 1. Core idea

During sleep, the mammalian brain *replays* recent experience. Hippocampal neurons fire in the same sequences seen during waking, compressed in time and run in both forward and reverse. This replay is, by best current scientific understanding, the substrate of **memory consolidation** — the slow transfer of recent episodes from hippocampus (rapid, capacity-limited) to neocortex (slow, large) where they become integrated semantic knowledge. We learn during the day; we *consolidate* what we learned overnight.

In machine learning, the same idea has independent, parallel history: **experience replay** in reinforcement learning (Lin 1992; pivotal for DQN, Mnih 2015) and **generative replay** in continual learning (Shin et al., 2017) both use replay of stored experience to stabilise learning and prevent catastrophic forgetting. Recent work explicitly draws the analogy: sleep-like consolidation phases in AI systems improve sample efficiency, retention, and generalisation.

For Runa, this matters because Runa is long-lived. She will accumulate experience over years. Consolidation is the mechanism that turns "lots of stored episodes" into "actual learning." Without consolidation, an agent's memory grows linearly but its understanding doesn't. Sleep-inspired patterns are how to build the consolidation engine.

## 2. Technical depth

**The neuroscience, briefly:**

- Hippocampal place-cells fire in sequences during exploration (e.g. running through a maze). During subsequent sleep (especially slow-wave sleep), the *same sequences* fire, often compressed 10-20× in time, often replayed backward.
- Wilson and McNaughton (1994) — the seminal demonstration in rats.
- The replay is hypothesised to: strengthen specific synaptic connections that mattered for the experience; integrate the new episode into existing semantic networks; enable the cortex to *learn* without the hippocampus needing to keep teaching it.
- **Complementary Learning Systems (CLS)** theory (McClelland, McNaughton, O'Reilly 1995; [[07-memory-consolidation-and-forgetting]]) is the theoretical framework: fast hippocampal learning, slow cortical consolidation, replay as the bridge.

**Replay in machine learning:**

- **Experience Replay** (Lin, 1992; central to DQN, Mnih et al., *Nature* 2015). Store recent experiences in a buffer; sample from the buffer for training. Decorrelates samples; reuses experience; stabilises learning. The single most-important engineering trick in deep RL.
- **Prioritised Experience Replay** (Schaul et al., 2015). Weight replay by recent prediction error — more-surprising experiences get replayed more. Improves sample efficiency.
- **Generative Replay** (Shin et al., 2017). Instead of storing experiences, train a *generative model* of past experience; sample from it during continual learning to prevent catastrophic forgetting. Biologically-plausible — the brain doesn't store raw episodes either.
- **Hippocampal Replay Networks** (Kumaran et al.) — biologically-inspired architectures that explicitly separate fast hippocampal-style learning from slow cortical-style learning.
- **Sleep phases in artificial agents.** Newer work (van de Ven et al., Hayes et al.) explicitly schedule "wake phases" (collect experience) and "sleep phases" (replay-based consolidation) in artificial agents. Showed improvements on continual learning benchmarks.

**The two-system architecture:**

```
       ┌─────────────────────────────────────────┐
       │ Wake phase                               │
       │  - perceive, act, learn fast (hippoc.   │
       │    analogue)                             │
       │  - record experiences in episode store   │
       └─────────────────────────────────────────┘
                          │ "sleep"
                          ▼
       ┌─────────────────────────────────────────┐
       │ Sleep phase                              │
       │  - replay recent experiences             │
       │  - update slow store (cortex analogue)   │
       │  - consolidate / abstract / integrate    │
       │  - forget irrelevant detail              │
       └─────────────────────────────────────────┘
```

**The benefits, empirically:**

- Mitigates catastrophic forgetting in continual-learning settings ([[45-continual-learning]]).
- Improves sample efficiency (re-uses experience that's expensive to collect).
- Enables abstraction — patterns across many specific episodes become generalised semantic knowledge.
- Lets the slow system learn on schedule rather than in real-time crisis.

## 3. Key works

- **Wilson, M. and McNaughton, B.** "Reactivation of hippocampal ensemble memories during sleep." *Science*, 1994. The seminal replay observation.
- **McClelland, McNaughton, O'Reilly.** "Why there are complementary learning systems in the hippocampus and neocortex." *Psychological Review*, 1995. The CLS theory.
- **Lin, L-J.** "Self-improving reactive agents based on reinforcement learning, planning and teaching." *Machine Learning*, 1992. Experience Replay foundation.
- **Mnih et al.** "Human-level control through deep reinforcement learning." *Nature*, 2015. DQN — the experience-replay popularisation.
- **Schaul et al.** "Prioritized Experience Replay." arXiv:1511.05952, 2015.
- **Shin, Lee, Kim, Kim.** "Continual Learning with Deep Generative Replay." NeurIPS 2017.
- **Kumaran, Hassabis, McClelland.** "What Learning Systems do Intelligent Agents Need? Complementary Learning Systems Theory Updated." *Trends in Cognitive Sciences*, 2016.
- **Hayes et al. "Memory Efficient Experience Replay for Streaming Learning."** ICRA 2019.
- **van de Ven, Tuytelaars, Tolias.** "Three scenarios for continual learning." arXiv:1904.07734, 2019.
- **Diekelmann and Born.** "The memory function of sleep." *Nature Reviews Neuroscience*, 2010. Excellent neuroscience review.

## 4. Empirical results

For neuroscience:
- Replay during sleep is one of the most-replicated findings in modern hippocampal neuroscience.
- Sleep disruption impairs memory consolidation in humans and animals (well-established).
- Specific patterns (sharp-wave ripples during NREM sleep) correlate strongly with memory performance.

For AI:
- Experience replay is the foundation of stable deep RL — without it, DQN-style learning collapses.
- Generative replay successfully prevents catastrophic forgetting in continual-learning settings.
- Recent "sleep phases" in artificial agents (Sokar et al. 2021 onwards) improve continual-learning benchmarks by 5-20%.
- The pattern is robust across architectures; less dependent on specific model details than many ML techniques.

## 5. Applicability to Runa

For **Eir (the maintenance retainer)**:

- **Schedule a sleep phase nightly.** During Runa's quiet window (low Volmarr activity), Eir orchestrates consolidation:
  1. Select recent Muninn episodes (last 24h).
  2. Cluster by topic / entity / time.
  3. For each cluster, ask Heimskringla for a derived summary.
  4. Write summaries into Muninn's semantic layer ([[02-episodic-memory-architectures]] reflection).
  5. Extract triplets if knowledge-graph layer is enabled ([[06-knowledge-graphs-ai-memory]]).
  6. Update importance scores (boost-on-use, decay-on-disuse).
  7. Re-embed episodes if the embedding model has changed.
- Eir's "sleep" is the practical implementation of the CLS-theory consolidation idea.

For **Muninn**:

- Episodes (recent) are the "hippocampal" layer — fast write, finite capacity, high specificity.
- Consolidated summaries are the "cortical" layer — slow write, large capacity, abstracted.
- Both layers searchable; retrieval ranking favours different layers depending on query type.

For **possible future continual-learning of small models**:

- If Runa eventually fine-tunes a local model on her own conversations ([[19-rlhf-dpo-preference-optimization]] + [[32-knowledge-distillation]]), generative-replay-style training prevents the new fine-tune from destroying older capabilities.
- This is a v2+ direction.

For **prioritized replay**:

- Eir's consolidation should weight by importance ([[02-episodic-memory-architectures]] §importance). High-importance episodes get more consolidation effort; trivial episodes get cheap summarisation.

For **forward and backward replay**:

- The neuroscience finding includes *reverse* replay — episodes replayed backward. Speculative analogue for Eir: occasionally re-process old episodes in reverse-temporal order to find connections forward-replay missed. Probably overkill.

What to avoid:

- Don't run consolidation during active conversations. Sleep is sleep. Eir's job runs in quiet windows.
- Don't delete raw episodes during consolidation. Compression-not-deletion ([[07-memory-consolidation-and-forgetting]]).
- Don't run *too aggressive* consolidation. A few summaries per day; not hundreds. Quality over quantity.
- Don't conflate consolidation with archiving. Cold-archival (move very-old episodes to slower storage) is a separate, additional process.

## 6. Open questions

- **The right consolidation cadence.** Nightly is intuitive; the neuroscience suggests multiple sleep cycles per night with different replay profiles. AI analogue is undeveloped.
- **What to consolidate.** All episodes, or just important ones? Active research; defaults vary.
- **Whether consolidation should be supervised.** Should Volmarr approve consolidated summaries before they're written to long-term memory? Trade-off between automation and accuracy.
- **Cross-modal replay.** Volmarr's text conversations and Rödd's voice transcripts together form a multimodal life-record. Joint consolidation across modalities is largely unexplored.

## 7. References (curated)

- Wilson and McNaughton (1994), *Science*.
- McClelland, McNaughton, O'Reilly (1995), *Psychological Review*.
- Mnih et al. (2015), *Nature*. DQN.
- arXiv:1511.05952 — Prioritized Experience Replay.
- Shin et al. (2017), NeurIPS — Generative Replay.
- Diekelmann and Born (2010), *Nature Reviews Neuroscience*.
- arXiv:1904.07734 — Three scenarios for continual learning.
- Kumaran, Hassabis, McClelland (2016), *Trends in Cognitive Sciences*.
- Companion docs: [[02-episodic-memory-architectures]], [[07-memory-consolidation-and-forgetting]], [[45-continual-learning]].

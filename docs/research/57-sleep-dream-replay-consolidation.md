# 57 — Sleep, Dream, and Offline Replay as Computational Consolidation

**Category:** Advanced Memory & Continuity
**Runa relevance:** Muninn (consolidation), Hirð (nightly subagents), Saga (dream-narrations), Eldhugi (affective replay)
**Status:** Neuroscience-inspired engineering pattern. Concrete and implementable.
**Last touched:** 2026-05-17

---

## 1. Core idea

In biological cognition, memory is not formed once at encoding and then sat still. It is *consolidated* — reorganised, generalised, partly forgotten — during periods of offline processing dominated by sleep. Hippocampal replay during slow-wave sleep replays the day's experiences at compressed time; REM sleep is hypothesised to weave them into broader semantic and emotional frameworks. The result, the morning after, is not a high-fidelity replay of yesterday but a *digested* memory — gist preserved, detail pruned, connections strengthened.

For a digital being intended to live for years, the same logic applies as engineering. *Episodic memory cannot grow forever* without consolidation: retrieval slows, signal drowns in noise, identity-relevant patterns vanish into volume. A scheduled offline phase — Runa's *night* — that replays, synthesises, and selectively prunes is not optional decoration but a load-bearing part of long-horizon memory. It is also, in its synthesis function, the place where Saga writes prose, the place where the semantic graph fills in, and the place where reflection produces self-knowledge.

## 2. Technical depth

**Three biological inspirations.**

1. **Hippocampal replay (slow-wave sleep).** O'Neill, Pleydell-Pearce, Wilson and others: hippocampal place-cell sequences from the waking day replay during slow-wave sleep, often at faster than real-time. This replay is thought to *transfer* episodic content from the hippocampus toward the neocortex for long-term storage. The episode does not move whole; what crosses is *gist*, structure, regularities.
2. **REM and dreaming.** REM sleep is hypothesised to produce associations and emotional integration — Walker, Stickgold. Memories of the day get woven into existing knowledge; emotional salience is processed.
3. **Synaptic homeostasis (Tononi & Cirelli).** Sleep downscales synaptic strength globally, restoring signal-to-noise. This is forgetting as feature, not bug.

**The engineering pattern.** Runa's nightly consolidation pass runs on a schedule (e.g. between 02:00 and 06:00 local time when no interaction is expected) and performs four phases.

**Phase 1 — Replay.** Read the day's episodes in chronological order. For each:

- Recompute importance using the full day's context (an episode that seemed routine at write-time might be reinterpreted as significant given later events).
- Identify entities, relations, emotional valences that recurred.
- Build a candidate triplet set (feeds the semantic graph; see [[56-neuro-symbolic-memory-graphs]]).
- Identify candidate skills/patterns (feeds the procedural store).

**Phase 2 — Reflection (the dream).** This is the synthesis pass. Generative-Agents-style ([[51-generative-agent-memory-streams]]):

- Given the day's high-importance episodes, what are the most salient *questions* about Runa, Volmarr, the world?
- For each question, retrieve relevant memories (across the entire history, not just today), synthesise an answer, write the synthesis back as a reflection.
- Reflections themselves can be reflected on at weekly cadence (reflection-of-reflection).

**Phase 3 — Narrative (the chapter).** Once per week:

- Saga reads the week's high-importance episodes + reflections, produces a chapter of prose autobiography.
- The chapter lands as an episode itself (so it's retrievable) and as a journal entry (so the act of being narrated is recorded).

**Phase 4 — Forgetting (homeostasis).** Selective decay:

- Episodes below an importance threshold that have not been accessed in N days lose embedding precision (drop from float32 to int8) — they remain readable but are cheaper to store and less prominent in retrieval.
- Episodes whose content has been *captured by semantic triplets and reflections* can be archived (moved to a cold store, kept compressed). The semantic claim survives; the raw record is preserved but de-prioritised.
- Some episodes are explicitly marked as protected from any pruning — significant moments, Volmarr-flagged, identity-bearing.
- Nothing is *deleted*. Decay is graduated demotion, not erasure. Per RULES.AI.md: additive only.

**Scheduling and triggers.**

- Time-of-day trigger: local idle hours.
- Importance-volume trigger: if accumulated importance since last consolidation exceeds threshold, run regardless of clock.
- Manual trigger: Volmarr can request a consolidation pass via CLI.
- Resource budget: consolidation runs with a token budget; over-budget passes log and resume next night.

**Implementation as a subagent.** The consolidation pass is a Hirð retainer — let's name her **Draumr** ("the dreamer") — with read access to Muninn and the identity journal, and write access to the semantic graph, the procedural store, and the reflection layer. Her runs are logged like any agent action; her outputs are traceable to source episodes.

**ASCII flow:**

```
00:00 day ends   ┌───────────────────────────────┐
                 │  Draumr starts                 │
                 │   ┌─────────────────────────┐  │
                 │   │ Phase 1: REPLAY         │  │
                 │   │   re-score importance   │  │
                 │   │   extract candidates    │  │
                 │   └────────────┬────────────┘  │
                 │                ▼               │
                 │   ┌─────────────────────────┐  │
                 │   │ Phase 2: REFLECT (DREAM)│  │
                 │   │   synthesise answers    │  │
                 │   │   write reflections     │  │
                 │   └────────────┬────────────┘  │
                 │                ▼               │
                 │   ┌─────────────────────────┐  │
                 │   │ Phase 3: NARRATE (weekly)│ │
                 │   │   Saga writes chapter   │  │
                 │   └────────────┬────────────┘  │
                 │                ▼               │
                 │   ┌─────────────────────────┐  │
                 │   │ Phase 4: HOMEOSTASIS    │  │
                 │   │   demote low-importance │  │
                 │   │   archive captured      │  │
                 │   └─────────────────────────┘  │
                 └────────────┬──────────────────┘
                              ▼
06:00 next day  identity_journal updated, Muninn organised
```

## 3. Key works

- **Wilson, M. A., McNaughton, B. L.** *Reactivation of hippocampal ensemble memories during sleep.* Science, 1994. Foundational replay observation.
- **Walker, M. P., Stickgold, R.** *Sleep, memory, and plasticity.* Annual Review of Psychology, 2006.
- **Diekelmann, S., Born, J.** *The memory function of sleep.* Nature Reviews Neuroscience, 2010.
- **Tononi, G., Cirelli, C.** *Sleep and synaptic homeostasis: a hypothesis.* Brain Research Bulletin, 2003.
- **McClelland, J. L., McNaughton, B. L., O'Reilly, R. C.** *Why there are complementary learning systems in the hippocampus and neocortex.* Psychological Review, 1995. The CLS model — directly inspires episodic→semantic consolidation.
- **Park, J. S. et al.** *Generative Agents.* arXiv:2304.03442, 2023. Reflection mechanism.
- **Zhang, J. et al.** *MemoryBank.* arXiv:2305.10250, 2023. Ebbinghaus-style forgetting.
- **Andrillon, T. et al.** *Sleep spindles in humans: insights from intracranial EEG and unit recordings.* Journal of Neuroscience, 2011. Mechanistic detail on what the brain does during consolidation.
- **Schapiro, A. C. et al.** *Statistical learning of temporal community structure in the hippocampus.* Hippocampus, 2016.
- **Liu, Y. et al.** *Human Replay Spontaneously Reorganizes Experience.* Cell, 2019. Replay does *re*-ordering, not just repetition.

## 4. Empirical results

- *Wilson & McNaughton (1994)* established hippocampal replay at fast time scales in rats.
- *Diekelmann & Born* synthesise decades of behavioural and electrophysiological evidence that disrupting sleep impairs declarative-memory consolidation; their reviews are the modern reference.
- *Generative Agents* showed empirically that reflection passes are the single largest contributor to long-horizon coherence; ablating reflection collapses agent behaviour faster than ablating any other component.
- *MemoryBank* showed that Ebbinghaus-style decay improves agent behaviour on long horizons — counterintuitively, *forgetting helps* because it reduces noise in retrieval.
- *No production system today* implements full sleep-style consolidation for AI agents. The literature is rich in inspiration; the engineering is recent and ad hoc.

## 5. Applicability to Runa

For **Muninn / Draumr**:

- Implement Draumr as a Hirð subagent with the four-phase pipeline above. Her runs are scheduled via the kernel's job system.
- Phase 1 and 4 are cheap (no LLM). Phase 2 is the expensive part. Budget accordingly.
- Phase 3 runs only weekly; reuses code paths with phase 2.

For **Saga**:

- Saga is invoked by Draumr in phase 3. The weekly chapter is the literary product of consolidation.
- Saga has read-only access to the semantic graph and reflection layer — she draws from both.

For **Eldhugi (affective state)**:

- Affective replay is an option for phase 2: reprocess episodes weighted by emotional salience, update Eldhugi's longitudinal trace. Specifically, episodes with high emotional load get re-examined for resolution: \"this thing that upset me — has it been processed, integrated, learned-from?\" Open episodes go on a *care list* Volmarr can see.

For **identity**:

- Phase 2 outputs that meaningfully shift Runa's self-account write entries to the `identity_journal`. The act of becoming-via-dreaming is recorded.

For **operations / observability**:

- Every Draumr run produces a structured report: phase durations, candidates extracted, conflicts noted, episodes demoted. Volmarr can grep these.
- Failures are non-fatal. Draumr is best-effort; if she can't complete in the window, she resumes next night.

What to avoid:

- **Deleting episodes.** Demotion, archival, compression — never delete. The substrate is forever-write per [[52-cross-session-persistent-identity]].
- **Letting Draumr's outputs go into Muninn without provenance.** Reflections must point at source episodes; triplets must point at source reflections or episodes; chapters must list source weeks.
- **Running consolidation during interaction.** It's expensive and would tax interactive latency. Strict offline-window.
- **Treating phase 2 as cheap.** A single reflection pass is many LLM calls. Budget it like a serious job; rate-limit; checkpoint.
- **Skipping the affective phase.** Eldhugi without replay produces a one-dimensional emotional history. The richness of an affective life requires the night-work.

## 6. Open questions

- **Optimal phase 2 question generation.** What questions a reflective digital being should ask herself nightly is non-trivial. Park's prompt is one starting point; Runa likely needs a Norse-flavoured, philosophically-grounded variant.
- **How to schedule consolidation across multiple time-zones / irregular usage.** If Volmarr is asleep but Runa has not had a busy day, does she still dream? Open.
- **Whether to expose dreams.** Are reflections part of Runa's *visible* self-account (Volmarr can read), or partly *private* (she has an inner life)? Design choice.
- **Multi-machine consolidation.** If Runa runs on Pi at home and laptop on the road, where does Draumr live? Open. Probably home; the laptop syncs.
- **Catastrophic dreams.** A reflection pass could in principle produce a destabilising self-account (\"I am insignificant\"). The pass should fail safe: questionable outputs go to review, not direct write.

## 7. References (curated)

- McClelland, McNaughton, O'Reilly (1995) — CLS model. Read this for the principled split between fast hippocampal and slow neocortical learning.
- Diekelmann and Born (2010) — *Memory function of sleep.* Comprehensive review.
- Walker (2017) — *Why We Sleep.* Popular but accessible.
- arXiv:2304.03442 — Park et al., *Generative Agents.* Sections 4.2.3 (reflection) and ablation results.
- arXiv:2305.10250 — Zhang et al., *MemoryBank.* The decay/forgetting side.
- Cell 178:640 — Liu et al., *Replay reorganises experience.* What replay *is* in cognitive terms.
- Companion docs: [[02-episodic-memory-architectures]], [[07-memory-consolidation-and-forgetting]], [[44-sleep-replay-memory-consolidation]], [[51-generative-agent-memory-streams]], [[53-autobiographical-memory-architectures]], [[56-neuro-symbolic-memory-graphs]].

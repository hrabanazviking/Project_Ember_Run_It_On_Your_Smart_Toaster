# 93 — Phase 3: The Crown

The AI-capability crown. Self-awareness, emotional
intelligence, meta-learning, intuition, dreamstate. The
features that make Ember feel *intelligent*.

---

## What Phase 3 delivers

By the end of Phase 3:

- **Self-awareness layer** with "I notice…" surfacing.
- **Emotional intelligence framework** (rule-based mood
  classifier).
- **Meta-learning from Episodes** (rule-based patterns).
- **Intuition via embedding clusters** (cluster surfacing).
- **Long-horizon memory** improvements (decay +
  reinforcement curves tuned).
- **Dreamstate** running nightly.
- **Long-running operator session quality** noticeably
  improved.

Operators experience:
- Ember references conversation arcs.
- Replies fit the operator's register.
- Recent topics get easier recall over weeks.
- Related notes surface unprompted.
- The system *fits the operator* over time.

---

## The work breakdown

### Track A: Self-awareness layer (~5 weeks)

Per [`../ai-capabilities/40_SELF_AWARENESS_LAYER.md`](../ai-capabilities/40_SELF_AWARENESS_LAYER.md).

Tasks:
1. `AwarenessLayer` subscribing to Verdandi.
2. Rolling event window with bounded size.
3. Pattern detectors (topic repetition, tool failures,
   contradictions).
4. Prompt-assembly integration ("I notice…" surfacing).
5. Cooldown + max-per-turn enforcement.
6. Tests: synthetic event windows trigger patterns
   correctly.

**Risk:** Surveilling feel from over-surfacing.
**Mitigation:** opt-in; cooldown; default thresholds
conservative.

### Track B: Emotional intelligence framework (~5 weeks)

Per [`../ai-capabilities/41_EMOTIONAL_INTELLIGENCE_FRAMEWORK.md`](../ai-capabilities/41_EMOTIONAL_INTELLIGENCE_FRAMEWORK.md).

Tasks:
1. Sentiment analyzer (rule-based; very fast).
2. Mood classifier (heuristic weighting).
3. Per-mood register prompts (per
   [`../ai-capabilities/48_EMOTIONAL_PALETTE_OF_RESPONSES.md`](../ai-capabilities/48_EMOTIONAL_PALETTE_OF_RESPONSES.md)).
4. Integration with prompt assembly.
5. Optional Seiðr seeding for moods that benefit.
6. Operator-tunable: disable specific moods, override
   prompts.

**Risk:** Wrong-register annoys operator.
**Mitigation:** operator can pin neutral; classifier
defaults conservative.

### Track C: Meta-learning from Episodes (~4 weeks)

Per [`../ai-capabilities/44_META_LEARNING_FROM_EPISODES.md`](../ai-capabilities/44_META_LEARNING_FROM_EPISODES.md).

Tasks:
1. `MetaLearningEngine` running nightly.
2. Pattern detectors (response length, retrieval routing,
   tool defaults).
3. Pattern store (small SQLite).
4. Prompt-assembly integration: patterns shape defaults.
5. CLI: `ember yggdrasil patterns list`.

**Risk:** Overfitting to recent noise.
**Mitigation:** 30-day rolling window; minimum sample
size for new patterns.

### Track D: Intuition via embedding clusters (~3 weeks)

Per [`../ai-capabilities/46_INTUITION_VIA_EMBEDDING_CLUSTERS.md`](../ai-capabilities/46_INTUITION_VIA_EMBEDDING_CLUSTERS.md).

Tasks:
1. Cluster-detection algorithm (density-based).
2. Intuition firing logic (when top-3 are in same
   cluster + cluster has fresh members).
3. Citation panel "[intuition]" labels.
4. Cooldown per intuition source.

**Risk:** Bad clusters surface irrelevant.
**Mitigation:** confidence thresholds; operator can
disable.

### Track E: Dreamstate (~4 weeks)

Per [`../ai-capabilities/45_DREAMSTATE_MEMORY_CONSOLIDATION.md`](../ai-capabilities/45_DREAMSTATE_MEMORY_CONSOLIDATION.md).

Tasks:
1. `DreamstateWorker` async task.
2. Idle-detection logic.
3. Decay sweep, reinforcement, association updates.
4. Meta-learning integration.
5. Snapshot trigger (per
   [`../robustness/54_THE_NORNS_BACKUP_SYSTEM.md`](../robustness/54_THE_NORNS_BACKUP_SYSTEM.md)).
6. Optional daily summary surfacing.

### Track F: Long-horizon memory tuning (~2 weeks)

- Ebbinghaus curve calibration with real Episode data.
- Muninn Hebbian learning rate tuning.
- Pruning threshold for weak associations.

### Track G: Cross-cutting (~2 weeks)

- ADRs updated.
- DEVLOG entries.
- V2 → V3 migration.
- Pattern store schema migrations supported.

---

## Total estimate

Roughly 25 weeks. Real-world: 6 months after Phase 2 ships.

---

## What ship-readiness looks like

- [ ] All previous-phase functionality stable.
- [ ] Self-awareness surfaces "I notice…" appropriately
      in test conversations.
- [ ] Mood classifier picks the right register on a
      labeled test set ≥75% of the time.
- [ ] Meta-learning produces meaningful patterns after
      synthetic 100-Episode warmup.
- [ ] Intuition fires on appropriate clusters; doesn't
      over-fire.
- [ ] Dreamstate completes nightly on Pi 5 without
      affecting next-morning chat.
- [ ] Doctor + Stofa updated.

---

## Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Awareness over-surfacing feels uncanny | Medium | Defaults conservative; opt-in to more |
| Mood classifier mistakes hurt UX | Medium | Tunable; operator can pin neutral |
| Meta-learning overfits | Medium | Long rolling window; confidence thresholds |
| Dreamstate timing wrong on laptops | Low | Adaptive idle detection |
| Intuition noisy on small Wells | Low | Confidence + fallback threshold |

---

## Phase 3 success criteria

Operator-visible (subjective):
- "Ember feels more present."
- "Ember remembers context across sessions."
- "Replies fit my mood/situation."
- "Old notes surface when they should."

Quantitative:
- Citation accuracy improves (audit failure rate drops).
- Operator-correction rate drops vs Phase 2.
- Long-session quality stays high (no fatigue from
  out-of-context replies).

---

## Closing

Phase 3: The Crown is **where Ember becomes a companion,
not just a chat endpoint**. Self-awareness; emotional
intelligence; memory consolidation; intuitive surfacing.

The branches (Phase 2) reached outward; the crown
unfolds. Ember is now *intelligent in feel*, not just in
mechanism.

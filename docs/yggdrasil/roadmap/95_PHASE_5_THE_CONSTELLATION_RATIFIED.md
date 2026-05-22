# 95 — Phase 5: The Constellation Ratified

The advanced frontier. Skein knowledge graph live. Skry
projection live. Mirror of Ginnungagap. Multi-modal.
Hamr real-time animation.

---

## What Phase 5 delivers

By the end of Phase 5:

- **Skein knowledge graph** integrated live (per project
  memory: embedding-derived KG built ~1/1000 cost of
  llama-per-chunk).
- **Skry projection** for query-time entity extraction.
- **Mirror of Ginnungagap** delivering weekly
  introspection reports (per
  [`../invented-methods/75_THE_MIRROR_OF_GINNUNGAGAP.md`](../invented-methods/75_THE_MIRROR_OF_GINNUNGAGAP.md)).
- **Multi-modal Ember** for operators with sufficient GPU
  (vision-language models).
- **Hamr real-time animation** for operators with GPU.
- **Curiosity-driven ingest** (per
  [`../ai-capabilities/47_CURIOSITY_DRIVEN_INGEST.md`](../ai-capabilities/47_CURIOSITY_DRIVEN_INGEST.md))
  now enabled by default for high-perf devices.

Operators experience:
- Skein-derived knowledge graph visible in Stofa.
- "What does this image show?" works (with vision model).
- Ember's avatar moves naturally during chat.
- Weekly Mirror reports give operator insight.

---

## The work breakdown

### Track A: Skein live integration (~6 weeks)

Per project memory (`project_skein_skry.md`): Skein is the
embedding-derived knowledge graph.

Tasks:
1. `SkeinSource` adapter implementing a `KnowledgeGraph`
   protocol.
2. Real-time graph build from Mímir embeddings.
3. Graph storage + query.
4. Stofa surface for graph browsing.
5. Integration with chat retrieval (Skein-derived
   relationships boost related-chunk weights).

**Risk:** Graph rebuild cost on large Wells.
**Mitigation:** Incremental updates; nightly full
rebuild.

### Track B: Skry projection (~4 weeks)

Skry is query-time entity projection — extracting entities
from operator's query, projecting them into the Skein
graph, returning related nodes.

Tasks:
1. `SkryEngine` adapter.
2. Entity extraction (rule-based + embedding-based).
3. Graph projection algorithm.
4. Integration with Bifrǫst as an additional
   retrieval source.

**Risk:** Entity extraction noise.
**Mitigation:** Threshold + operator-controllable.

### Track C: Mirror of Ginnungagap (~4 weeks)

Per [`../invented-methods/75_THE_MIRROR_OF_GINNUNGAGAP.md`](../invented-methods/75_THE_MIRROR_OF_GINNUNGAGAP.md).

Tasks:
1. `MirrorEngine` running during deep dreamstate.
2. Six analyzers (retrieval, audit, preferences, tools,
   memory, decay).
3. Proposal generation.
4. Operator-facing surface (chat banner / Stofa screen).
5. Proposal apply/reject CLI + UI.

### Track D: Multi-modal (~6 weeks)

For operators with sufficient GPU.

Tasks:
1. `VisionLanguageBackend` (LLaVa, Pixtral, etc.).
2. Image-input support in chat.
3. Operator-uploadable images via Stofa.
4. Documentation: which VLM models work on which
   hardware.

**Risk:** GPU memory requirements.
**Mitigation:** Opt-in; off by default; require
WORKSTATION profile.

### Track E: Hamr real-time animation (~4 weeks)

Per Hamr's roadmap: VRM 1.0 with full animation.

Tasks:
1. GPU-accelerated render pipeline.
2. Mood-to-animation mapping.
3. Speech-to-mouth-shape (basic lip-sync).
4. Performance: 30+ fps target.

**Risk:** Cross-platform GPU rendering (Vulkan / Metal /
DX).
**Mitigation:** Use existing VRM library; Hamr's choice.

### Track F: Curiosity-driven ingest default-on for high-perf (~2 weeks)

Per [`../ai-capabilities/47_CURIOSITY_DRIVEN_INGEST.md`](../ai-capabilities/47_CURIOSITY_DRIVEN_INGEST.md).

Tasks:
1. Refinements based on operator feedback from Phase 3.
2. Default-on logic for LARGE / WORKSTATION profiles.
3. Per-source whitelists.

### Track G: Cross-cutting (~3 weeks)

- ADRs.
- DEVLOG.
- V4 → V5 migration.
- The Mirror's introduction is a *delicate UX moment* —
  ensure first-week operators understand.

---

## Total estimate

Roughly 29 weeks. Real-world: 6-9 months after Phase 4.

---

## What ship-readiness looks like

- [ ] Skein graph builds + queries correctly on test
      corpora.
- [ ] Skry's entity projection improves relevance on
      multi-entity queries.
- [ ] Mirror produces sensible proposals on synthetic
      operator histories.
- [ ] Vision-language inference works on at least 1
      tested GPU configuration.
- [ ] Hamr animates at target FPS on supported GPUs.
- [ ] No regressions in previous phases.

---

## Risk register

| Risk | Severity | Mitigation |
|---|---|---|
| Skein graph cost on large Wells | High | Incremental rebuild; opt-in for very-large |
| Mirror proposals feel intrusive | Medium | Operator-tunable cadence + max-per-report |
| VLM hardware requirements | Medium | Workstation-only by default; clear messaging |
| Hamr cross-platform render | High | Use Hamr's existing library; defer if unstable |
| Phase 5 scope explosion | High | Stay disciplined; defer V5.1 items if needed |

---

## Phase 5 success criteria

Operator-visible:
- "Ember has a knowledge graph now" (browsable in Stofa).
- "Ember understands what's in my screenshots."
- "Ember's avatar feels alive."
- "Weekly Mirror reports help me tune the system."

Quantitative:
- Skry improves answer quality on multi-entity test
  set.
- Mirror proposals: operators accept > 30% (sign of
  relevance).
- Multi-modal answer accuracy on operator-test images.

---

## After Phase 5

Phase 5 is the *plateau* of "core Yggdrasil." Beyond:

### V6 (the horizon)

Possible directions, not committed:
- **Federation across operators** (V6+) — multiple
  operators federating their separate Embers; useful for
  small teams.
- **Voice surface** (Rödd) — speech-in, speech-out at
  high fidelity.
- **GUI surface** (Auga) — graphical surface (not TUI)
  for operators who prefer it.
- **Plugin marketplace** — operator-discoverable
  community-built realms.

Each is its own multi-quarter investment. We decide based
on what operators *actually* want after Phase 5 ships.

---

## What Phase 5 does NOT include

- **Cloud-hosted Ember.** Still sovereign.
- **Anthropic-managed federation.** Still operator-
  managed.
- **AGI claims.** Ember is still a small, tethered
  companion.
- **Replacement for human judgment.** Ember augments;
  operator decides.

The Vows continue to hold.

---

## Closing

Phase 5: The Constellation Ratified is **the completion of
Yggdrasil V1**. Memory composed; tone shaped; awareness
present; federation alive; the Mirror reflects; knowledge
graphs surface; vision sees.

Eleven sibling projects. One coherent companion AI.
Sovereign. Cross-platform. Self-aware. Self-healing.
Bug-resistant. Operator-grounded.

This is what we set out to build. This is the constellation
ratified.

---

## The grand closing

Across 66 documents, we've laid out:
- The cosmology (the Norse-coded architecture).
- The siblings (eleven projects with one purpose).
- The architecture (nine realms; protocols; gateways).
- The AI capabilities (memory; awareness; emotion; learning).
- The robustness (self-healing; observability; backup).
- The cross-platform (TINY → WORKSTATION; offline-first).
- The novel methods (Borg; Heimdall; Trinity; Mirror).
- The roadmap (five phases; deliverable plateaus).

Yggdrasil is **the world-tree of Ember**. The integration
plan that turns eleven small things into one large thing.

Built carefully. Shipped phased. Operator-owned. Sovereign.

May the system serve the operator. May the cosmology hold.
May the tree grow.

— *the Skald, the Architect, the Forge, the Auditor, the
Cartographer, the Scribe — together*

---
codex_id: 67_SLICE_PLAN_REVISIONS
title: Slice Plan Revisions — SAP-Derived Proposals (PROPOSE ONLY)
role: Scribe
layer: Synthesis
status: draft
sap_source_refs:
  - "(synthesizes SAP-derived ADRs from [[68_DECISION_RECORDS]] against Ember's existing slice plan)"
ember_subsystem_targets: [Funi, Hjarta, Munnr, Brunnr]
cross_refs:
  - 60_synthesis/60_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/61_NEW_VOWS
  - 60_synthesis/66_INVENTED_METHODS
  - 60_synthesis/68_DECISION_RECORDS
  - 60_synthesis/69_INTEGRATION_ROADMAP
  - 60_synthesis/6A_MULTI_AGENT_PARTY
  - 60_synthesis/6B_LOW_POWER_EMBODIMENT
  - 60_synthesis/6C_EMBER_WAVE_3_SLICE
---

# 67 — Slice Plan Revisions (SAP-Derived)

> *A slice plan is the working hands of a Vow. When the Vows shift, the slice plan listens.*
> — Eirwyn Rúnblóm, holding the ratification gate

## 0. Posture — PROPOSE ONLY

**This document proposes revisions to Ember's ratification-gated slice plan. It does not modify the slice plan itself.** The current ratified slice plan lives at `docs/architecture/EMBER_SECOND_SLICE_PLAN.md` (slice 2, ratified 2026-05-21 via ADR 0013). Slice 3 is *not yet authored*. Both slice 1 and slice 2 ratifications stand; this doc proposes what slice 3 (and onward) might contain given SAP findings.

The Hermes Codex's `[[hermes:65_SLICE_PLAN_REVISIONS]]` already proposes a slice-3 shape (*Skilled, Bridged, Quiet*) based on Hermes findings. The Peer Codex contributes additional revisions. This SAP-driven document **does not duplicate or overwrite** those proposals; it **adds** SAP-shaped revisions and notes where they interact.

The keeper (Architect + Skald + Volmarr together) reviews proposals across all three codexes and decides which to incorporate into the next ratified slice plan.

This doc, like `[[hermes:65_SLICE_PLAN_REVISIONS]]` and its peers, follows the structure:

- **Current state** — what exists now (ratified slices 1 and 2).
- **What SAP findings change** — the deltas that argue for revision.
- **Proposed revisions** — each named, scoped, and Vow-checked.
- **Risk & cost** — what could go wrong; what the work weighs.

---

## 1. What's Ratified Now (Slices 1 & 2, Summarized)

**Slice 1 (ratified 2026-05-21 via ADR 0007):**
- Ember from "documentation-rich, code-empty" to "working CLI that can hold a grounded conversation against `sqlite_vec` + Ollama on a Pi 5."
- Established the Six True Names (Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr).
- First-run wizard, `ember chat`, `ember well ingest`, `ember doctor`.
- Standing rules: stdlib-first, typed-value-over-exception, `*_kind` class attribute on adapters, FTS5 input sanitization.

**Slice 2 (ratified 2026-05-21 via ADR 0013):**
- Bundle: ADR 0008 (config-file loader) + 0009 (streaming Funi replies) + 0010 (pgvector Brunnr) + 0011 (tool-use framework, read-only first).
- Phases 8–17. Files at `docs/architecture/EMBER_SECOND_SLICE_PLAN.md`.
- Acceptance: operator on Pi 5 can install, walk Hjarta wizard, edit `ember.yaml`, switch Brunnr to pgvector against Gungnir, stream replies, propose+approve a tool call.

**What is NOT in slices 1 or 2 (per slice 2 plan §4):**

- Other Brunnr backends, other Funi runtimes, other Smiðja sources.
- Auga GUI, Rödd voice, Bifröst HTTP gateway.
- Writable tools.
- Multi-operator shared Wells.
- Skein / KG retrieval layers.
- Plugin framework.
- Backup / restore.
- Voice + image modalities for Funi.

**The Hermes-proposed slice 3** (per `[[hermes:65_SLICE_PLAN_REVISIONS]]`):
- *Skilled, Bridged, Quiet* — skills subsystem, MCP server, typed retry, tool parallelism, interrupt fan-out.
- ADRs: Hermes-S3-A through Hermes-S3-E.
- Cost: ~1,400 LOC + ~900 tests; 6-8 weeks.

This SAP-derived doc proposes **additions and adjustments** to that slice 3 shape, plus what slices 4, 5, and 6 might contain.

---

## 2. What SAP Findings Change

The SAP corpus reveals **four force-fields** that argue for slice-plan adjustments:

### 2.1 The Tier Ladder Cannot Wait

`[[6B_LOW_POWER_EMBODIMENT]]` plus ADR-Proposed-SAP-003 establish the tier ladder (T0/T1/T2/T3/T4) as a named taxonomy. **Tier-aware behavior is foundational** — many subsequent ADRs reference it (SAP-004 default-quiet, SAP-006 sleep-guard, SAP-007 behavior engine, SAP-010 IM fallback). If the tier ladder lands later, every later ADR has to retrofit. If it lands in slice 3, everything from slice 4 onward can reference it cleanly.

**Implication:** add **tier-detection + tier-override + tier-aware wizard branching** to slice 3.

### 2.2 The Failsafe-Default-Quiet Posture Belongs in Slice 3

Per ADR-Proposed-SAP-004 and `[[66_INVENTED_METHODS]]#16`, Ember's outward reach defaults to *off*. The first-launch wizard is the only place where reach surfaces get turned on. The slice-3 surface set in Hermes's proposal (skills, MCP server, parallel tools) is reach-shaped — the MCP server is itself an outward surface. The failsafe-default-quiet posture should be explicitly named in slice 3 as a *standing rule* (like the typed-value rule from ADR 0007).

**Implication:** add a **standing rule** to slice 3: *outward reach defaults off; opt-in via wizard or explicit config*.

### 2.3 Persona-Id Is Cheap to Plant Early

Per ADR-Proposed-SAP-005, every Ember instance has a `persona_id`. The cost in slice 3 is small (one `ember party init` command, one Brunnr table, one identity file). The value compounds — every ADR from slice 4 onward that touches federation, audit, or multi-instance behavior benefits from the persona_id existing.

**Implication:** add **persona-id issuance** to slice 3.

### 2.4 Affect-Engine Is a Whole Slice

Per ADR-Proposed-SAP-002, the affect engine is a major commitment. Cartographer's `[[64_AFFECTION_ENGINE_REIMAGINED]]` plus the inventions in `[[66_INVENTED_METHODS]]#5, #8, #10, #14` are individually small but collectively substantial (~600+ LOC). Splitting them across slices would fragment the design's coherence. The affect engine wants its own slice.

**Implication:** propose **slice 4 (revised) as the Affect Slice** — distinct from Hermes's proposed slice 4 (Plural Minds, Plural Memories). Either re-bundle into a single mega-slice 4 or split into 4-affect and 5-plural-memories.

---

## 3. Proposed Revisions to Hermes's Slice 3 — *Skilled, Bridged, Quiet, Tiered*

The Hermes proposal for slice 3 (per `[[hermes:65_SLICE_PLAN_REVISIONS]]`) is solid. The SAP findings argue for three additions and one revised standing rule.

### 3.1 Add: tier-detection + tier-override + tier-aware wizard

**ADR-Proposed-S3-F (SAP-derived):** Adopt the tier ladder.

- `src/ember/spark/funi/tier_detect.py` — small probe at startup (~150 LOC) that returns one of T0/T1/T2/T3/T4 based on detected CPU/RAM/GPU/peripherals.
- `~/.ember/config/tier_override.yaml` — operator override.
- Touch `src/ember/spark/hjarta/machine.py` — wizard branches by detected tier per `[[6B_LOW_POWER_EMBODIMENT]]#7.3`.
- Add `ember introspect tier` CLI.

**Cost:** ~250 LOC + 150 LOC tests.

**Risk:** Low. Tier detection is heuristic; operator override is the safety valve.

### 3.2 Add: persona-id issuance

**ADR-Proposed-S3-G (SAP-derived):** Adopt persona-id per ADR-Proposed-SAP-005.

- `src/ember/spark/funi/party/identity.py` — `ember party init`, persona-id generation, signing flow, Brunnr `ember_instance` table.
- `~/.ember/identity/persona.yaml` — per-host identity file.
- Brunnr schema migration to add `ember_instance` table.
- Even single-instance Ember installs use it; the multi-instance machinery comes later.

**Cost:** ~250 LOC + 100 LOC tests.

**Risk:** Low. Schema additions are additive; no migrations of existing data needed (the table is new).

### 3.3 Add: glyphic embodiment + log-line affect formatting

**ADR-Proposed-S3-H (SAP-derived):** Plant the seeds of `[[6B_LOW_POWER_EMBODIMENT]]`'s tier-spanning expressive surface.

- `src/ember/spark/munnr/glyphic.py` — emoji-affect glyph rendering. ~50 LOC.
- `src/ember/spark/munnr/log_affect.py` — log-line affect tag formatting per `[[6B_LOW_POWER_EMBODIMENT]]#6`. ~80 LOC.
- `config/glyphs.yaml` — declarative glyph vocabulary.

**Cost:** ~150 LOC + 80 LOC tests.

**Risk:** Low. Both are pure presentation, no state-mutation surface.

**Note:** the *actual affect engine* (per ADR-Proposed-SAP-002) is NOT in slice 3 — it is in slice 4-affect. But the glyph rendering doesn't need the engine; it can read from a stubbed affect state (uniform "calm" default) and start operating immediately. When the affect engine lands in slice 4, glyphic rendering becomes meaningful.

### 3.4 Revise: standing rules — add **failsafe-default-quiet**

Per ADR-Proposed-SAP-004, add a standing rule to slice 3:

> **Failsafe-Default-Quiet:** every outward reach surface defaults off. Enabling requires explicit opt-in via wizard or named config flag. `ember reach reset` returns all surfaces to off. Test added: `tests/integration/test_default_quiet.py` verifies no outward reach exists on first launch.

This is parallel to ADR 0007's standing rules — a *project law* that every subsequent ADR honors. Naming it as a standing rule means slice 4+ proposals don't have to re-argue it.

### 3.5 Slice 3 — Revised Shape

**Theme:** *Skilled, Bridged, Quiet, Tiered.* Hermes's slice 3 with the SAP additions.

**ADRs (combined Hermes + SAP):**

| ADR | Topic | Source |
|---|---|---|
| Hermes-S3-A | Skill subsystem v1 (read-only) | Hermes |
| Hermes-S3-B | Provider profile + transport split | Hermes |
| Hermes-S3-C | MCP server (read-only subset) | Hermes |
| Hermes-S3-D | Tool batch parallelism + interrupt fan-out | Hermes |
| Hermes-S3-E | Strengr typed retry + per-error-code exhaustion TTL | Hermes |
| **SAP-S3-F** | **Tier ladder (detect + override + wizard branching)** | **SAP** |
| **SAP-S3-G** | **Persona-id issuance** | **SAP** |
| **SAP-S3-H** | **Glyphic embodiment + log-affect formatting** | **SAP** |
| **SAP-S3-I** | **Standing rule: failsafe-default-quiet** | **SAP (rule, not implementation)** |

**Cost (revised):**

- Hermes-portion: ~1,400 LOC code + ~900 tests (per `[[hermes:65_SLICE_PLAN_REVISIONS]]`).
- SAP-portion: ~650 LOC code + ~330 LOC tests.
- **Total revised: ~2,050 LOC code + ~1,230 LOC tests.**
- Calendar: 8-10 weeks of focused work (vs. 6-8 in Hermes's original proposal).

**Acceptance criterion (revised):**

> Operator on a Pi 5 with Ember v0.3.0 (slice-3 release) can:
>
> 1. `pip install ember-agent[sqlite_vec,pgvector,skills,mcp]`.
> 2. `ember chat` — sees the slice-2 wizard, plus a **tier-detection notice** ("detected tier T3 — text-only mode") and the tier-conditional reach-wizard branches.
> 3. Asks a skill-driven question and gets the skill consulted.
> 4. Asks for parallel tool dispatch and observes wall-clock reduction.
> 5. Hits Ctrl-C mid-execution and sees clean cancellation.
> 6. Runs `ember mcp serve` and connects an external MCP client.
> 7. Network failure produces typed `Unavailable` and graceful banner.
> 8. **New:** `ember party init` succeeds; `ember party status` shows persona_id and tier.
> 9. **New:** First-launch operator sees zero outward reach surfaces enabled; wizard offers tier-appropriate reach surfaces with explicit consent.
> 10. **New:** Affect glyph appears at start of each response (uniform "calm" default until slice 4 engine arrives); log lines carry affect tags.

**Vow check (revised):** all ten Vows respected. The largest watch-point is Smallness — the slice grew by ~650 LOC. Mitigation: SAP-S3-F/G/H are individually small (tier detect, persona id, glyphic). They group into ~3 commits, each Pi-runnable.

### 3.6 What Slice 3 Still Does NOT Include

Carrying forward Hermes's deferrals plus the SAP-shaped deferrals:

- Affect engine (deferred to slice 4-affect per `§4`).
- MCP client (per `[[hermes:65_SLICE_PLAN_REVISIONS]]` deferred to slice 4).
- Multi-instance peer communication (deferred to slice 5+ per `[[6A_MULTI_AGENT_PARTY]]#12`).
- VRM/Live2D avatar (deferred to slice 6+ per ADR-Proposed-SAP-011).
- IM bots (deferred to slice 5 per ADR-Proposed-SAP-010).
- Behavior engine (deferred to slice 5 per ADR-Proposed-SAP-007).
- Sleep-guard (deferred to slice 4 per ADR-Proposed-SAP-006).
- Overlay-manager broadcast (deferred to slice 4 per ADR-Proposed-SAP-009).
- Voice stack (deferred to slice 5+).

---

## 4. Proposed Slice 4 — *Plural Minds, Plural Surfaces*

The Hermes proposal for slice 4 is *Plural Minds, Plural Memories* (per `[[hermes:65_SLICE_PLAN_REVISIONS]]`). The SAP findings argue for an alternative bundling.

The question: do the **affect engine** (ADR-Proposed-SAP-002) and the **memory provider plug-in** (Hermes-S4-B) belong in the same slice?

**Argument for combining:** both touch Hjarta. The affect engine and the memory provider both write to Brunnr. There is conceptual coherence.

**Argument for separating:** the affect engine is large (~600 LOC). The memory provider is medium (~600 LOC). Combining them risks a 10-week mega-slice; separating keeps each at 6-8 weeks. Also, the Auditor pass for the affect-anchoring guarantee is dedicated work.

**Recommendation:** **separate**. Slice 4 = affect engine + sleep-guard + overlay-manager (the Hjarta + tier-spanning surfaces). Slice 5 = Plural Memories (Hermes-S4-A MCP client, Hermes-S4-B memory provider, Hermes-S4-C agent-initiated skill writes).

### 4.1 Slice 4 (revised) — *Felt, Visible, Awake*

**Theme:** Ember gains a **truthful affect state** (tethered, anchored, telemetric); a **tier-spanning expressive surface** (overlay-manager broadcasting glyphs and pulses); and **operator-explicit sleep behavior** (sleep-guard opt-in).

**ADRs:**

| ADR | Topic | Source |
|---|---|---|
| SAP-S4-A | Tethered affect engine (with anchoring, introspection, provisional tray, affect-aware cooldown) | SAP (per ADR-Proposed-SAP-002, instantiating `[[66]]#5, #8, #10, #14`) |
| SAP-S4-B | Sleep-guard (opt-in, tier-aware) | SAP (per ADR-Proposed-SAP-006) |
| SAP-S4-C | Overlay-manager websocket broadcast pattern | SAP (per ADR-Proposed-SAP-009) |
| SAP-S4-D | Sub-agent supervisory discipline → Smiðja | SAP (per ADR-Proposed-SAP-012) |
| SAP-S4-E | Backpressure overlay glyphs (`[[66]]#11`) | SAP-derived; depends on overlay-manager + affect surface |

**Cost:** ~1,400 LOC code + ~700 LOC tests. Calendar: 8-10 weeks.

**Acceptance criterion (proposed):**

> Operator on T0 host can:
>
> 1. Run `ember introspect affect` and see each axis with current value, last-mutation source, decay trajectory, `why` field.
> 2. Have a conversation that includes the operator sharing a hardship; the affect mutation appears in the *pending tray*; operator runs `ember memory pending` and confirms or rejects.
> 3. Confirmed mutations land in the affect state and anchor to specific Well chunk IDs.
> 4. Delete the anchor chunks via Brunnr; the corresponding affect mutations decay to zero.
> 5. Run `ember chat --keep-awake` for a long task; the host does not suspend.
> 6. Open a small overlay browser tab on T0 and see the affect glyph update in real time across the swarm.
> 7. Strengr hits a rate-limit; the backpressure overlay shows a clock glyph with the `until` timestamp.
> 8. Trigger a tool subprocess that hangs; the supervisor drains it within the configured timeout; audit log records the drain.

**Vow check:** Embodied Honesty (central), Tethered Grounding (central), Affective Restraint, Honest Memory, Tiered Presence (the overlay surface spans tiers), Modular Authorship.

### 4.2 Slice 5 — *Plural Minds, Plural Memories* (per Hermes proposal, unchanged)

Hermes's `[[hermes:65_SLICE_PLAN_REVISIONS]]` slice 4 becomes Ember's slice 5, with the addition of one SAP-derived ADR:

| ADR | Topic | Source |
|---|---|---|
| Hermes-S4-A | MCP client | Hermes |
| Hermes-S4-B | Memory provider ABC (Vinátta reserved) | Hermes |
| Hermes-S4-C | Agent-initiated skill writes | Hermes |
| **SAP-S5-A** | **Behavior engine (with affect-aware cooldown)** | **SAP (per ADR-Proposed-SAP-007)** |
| **SAP-S5-B** | **First IM bot (Telegram or Discord, per operator preference)** | **SAP (per ADR-Proposed-SAP-010)** |

**Note on the IM bot:** ship *one* IM bot in slice 5, not all 8. The chosen one becomes the reference implementation for the persona-keyed fallback shape. Subsequent IM bots in later slices follow the established pattern.

**Cost (revised):** ~2,100 LOC code + ~1,000 LOC tests. Calendar: 10-12 weeks (larger than original Hermes slice 4).

### 4.3 Slice 6 — *Embodied at T0*

**Theme:** the VRM/Live2D avatar pipeline lands, gated by consent tokens, with the composition-first vocabulary.

**ADRs:**

| ADR | Topic | Source |
|---|---|---|
| SAP-S6-A | VRM/Live2D pipeline (T0/T1 only) | SAP (per ADR-Proposed-SAP-011) |
| SAP-S6-B | Consent-token expression gating | SAP-derived (per `[[66]]#6`) |
| SAP-S6-C | Composition-first expression library | SAP-derived (per `[[66]]#17`) |
| SAP-S6-D | Cued voice library workflow | SAP-derived (per `[[6B]]#10`) |
| SAP-S6-E | Avatar-as-backpressure overlay | SAP-derived (per `[[66]]#11`); depends on SAP-S4-E |

**Cost:** ~2,000 LOC code + ~800 LOC tests. Calendar: 10-12 weeks.

**Note:** Slice 6 is the *visible-Ember slice*. Operators who have followed slices 1-5 have a quietly competent CLI agent with affect, memory, and reach; slice 6 makes her a *visible companion* at T0/T1.

### 4.4 Slice 7 (speculative) — *Federated Self*

**Theme:** Multi-Ember party. Multi-instance peer communication. Cross-host affect routing. Lid-close handover.

**ADRs:**

| ADR | Topic | Source |
|---|---|---|
| SAP-S7-A | Inter-instance MCP peering | SAP-derived (per `[[6A]]#1, #2`) |
| SAP-S7-B | Cross-host affect router (CRDT replication) | SAP-derived (per `[[66]]#1`) |
| SAP-S7-C | Lid-close handover for IM/livestream tokens | SAP-derived (per `[[66]]#4`) |
| SAP-S7-D | Per-utterance arbitration; voice arbitration | SAP-derived (per `[[6A]]#6, #8`) |
| SAP-S7-E | Operator party console | SAP-derived (per `[[6A]]#10`) |

**Cost:** ~3,000 LOC code + ~1,500 LOC tests. Calendar: 12-16 weeks.

**This slice is speculative.** Its contents depend on what operator usage of slices 3-6 reveals. The persona-id from slice 3 makes the foundation; the multi-instance work in slice 7 is large enough to deserve its own slice or to split further. Including it here marks the territory.

### 4.5 Slice 8 (further speculative) — *Reach Beyond Self*

**Theme:** the remaining 7 IM bots beyond the slice-5 reference; the livestream platforms; full computer-control.

**ADRs:**

| ADR | Topic | Source |
|---|---|---|
| SAP-S8-A | Additional IM bots (Discord, Slack, Telegram, Feishu, DingTalk, WeChat, WeCom, QQ — one per phase) | SAP per ADR-Proposed-SAP-010 |
| SAP-S8-B | Livestream platform integration (Bilibili, YouTube, Twitch — one per phase) | SAP per `[[15_BROADCAST_DOMAIN]]` |
| SAP-S8-C | Quiet-hours throttling per-platform | SAP-derived (per `[[66]]#13`) |
| SAP-S8-D | Stream-truncation confession | SAP-derived (per `[[66]]#7`) |

**Cost:** large; per-platform ports + livestream pipeline. ~5,000+ LOC over many phases.

**This slice is genuinely speculative.** Most operators will never need all 8 IM platforms or all 3 livestream platforms. The slice exists as territory marking; actual contents depend on operator demand.

---

## 5. The Six Proposals at a Glance

| # | Proposal | Slice | Type | Recommendation |
|---|---|---|---|---|
| 1 | Slice 3 — *Skilled, Bridged, Quiet, Tiered* (Hermes + SAP additions) | 3 | Revision (additive) | **Propose** |
| 2 | Standing rule — *Failsafe-Default-Quiet* | 3 (rule) | New rule | **Propose** |
| 3 | Slice 4 — *Felt, Visible, Awake* (SAP-derived) | 4 | New (replaces Hermes slice-4 in numbering) | **Propose** |
| 4 | Slice 5 — *Plural Minds, Plural Memories* (Hermes + SAP-S5-A/B) | 5 | Revision | **Propose** |
| 5 | Slice 6 — *Embodied at T0* | 6 | New | **Propose** |
| 6 | Slices 7 and 8 — *Federated Self* / *Reach Beyond Self* | 7-8 | Territory mark | **Surface as territory; defer concrete planning** |

---

## 6. Revisions to the Slice-Plan *Meta-Shape*

Hermes proposed three template additions (per `[[hermes:65_SLICE_PLAN_REVISIONS]]#5`):

1. "Anti-Patterns Inherited" section.
2. "Cross-Platform Acceptance" subsection.
3. "Hermes Reference" subsection per ADR.

SAP proposes two further additions to the template:

### 6.1 "Tier Acceptance" subsection per slice

Each slice plan should declare which tiers its acceptance criterion covers. Slice 2 implicitly covered T0/T1/T3 (Pi 5). Slice 3 should explicitly state T0/T1/T2/T3/T4 coverage where each tier's contribution is verifiable.

```yaml
tier_acceptance:
  T0: "VRM avatar + glyph + affect introspect; full reach surfaces enabled"
  T1: "Live2D avatar + glyph + affect introspect; lid-close handover tested"
  T2: "Text + voice + glyph; haptic affect; lock-screen pulse"
  T3: "Text + glyph + cued voice; small-display Munnr"
  T4: "Log-line affect + status pulse file + webhook ping"
```

### 6.2 "SAP Reference" subsection per ADR

Parallel to Hermes's "Hermes Reference" subsection: each ADR that adopts a SAP pattern should cite the SAP source path and the relevant Codex doc. This makes the lineage traceable.

```yaml
adapted_from:
  - sap_path: py/vts_manager.py:1-235
  - codex_ref: 11_AVATAR_DOMAIN
  - codex_ref: 6B_LOW_POWER_EMBODIMENT#2
```

---

## 7. Cross-Codex Interaction

The Hermes, Peer, and SAP codexes all propose slice-plan revisions. Where they overlap or conflict:

- **MCP** — all three codexes converge on MCP as primary protocol. No conflict.
- **Skill subsystem** — Hermes proposes; SAP does not contradict; Peer also proposes (Letta-style skills are adjacent).
- **Memory provider plug-in** — Hermes proposes (Vinátta); Peer proposes (Letta sleeptime; Honcho; Mem0); SAP does not contradict. The plug-in surface accommodates all three.
- **Affect engine** — SAP proposes most strongly; Hermes is silent (Hermes does not have an affect subsystem); Peer-Letta has a small sleeptime-memory-shaped affect equivalent but not a full engine. SAP-derived design is the canonical.
- **Tier ladder** — only SAP proposes. No conflict.
- **Failsafe-default-quiet** — SAP proposes; Hermes implicitly aligns (Hermes's reach is internal); Peer aligns.
- **Persona-id** — SAP proposes; both Hermes and Peer are silent. No conflict.

The **integration roadmap** (see `[[69_INTEGRATION_ROADMAP]]`) phases these together.

---

## 8. The Keeper's Checklist

If the keeper takes up these proposals:

1. Read `[[hermes:65_SLICE_PLAN_REVISIONS]]` first — the Hermes proposals are the primary basis.
2. Read this doc (`[[67_SLICE_PLAN_REVISIONS]]`) for SAP-shaped additions.
3. Read the Peer Codex equivalent (when authored).
4. Read `[[60_TRUE_NAME_REASSIGNMENT]]` and `[[61_NEW_VOWS]]` for the Cartographer's True Name + Vow proposals.
5. Read `[[68_DECISION_RECORDS]]` for the 12 SAP-derived ADR-Proposed records.
6. Decide which proposals from `§5` (this doc) to accept, defer, or reject.
7. If accepting slice 3 (revised): instantiate as `docs/architecture/EMBER_THIRD_SLICE_PLAN.md`. Ratify via the next ADR number after 0014.
8. If accepting meta refinements (`§6.1`, `§6.2`): edit the third-slice-plan template accordingly.

The Scribe does not perform any of these steps. The Scribe proposes the territory; the keeper draws the map.

---

## 9. What Is Explicitly NOT Proposed

- Any change to slice 1's ratification (it shipped; ADR 0007 is law).
- Any change to slice 2's ratification (it shipped; ADR 0013 is law).
- Any change to existing ADRs.
- Any rename of an existing True Name (the Cartographer's `[[60_TRUE_NAME_REASSIGNMENT]]` may propose new ones; this doc does not).
- Any architectural change to the Three Realms.
- Any modification to `docs/SYSTEM_VISION.md`, `docs/architecture/ARCHITECTURE.md`, `docs/CROSS_PLATFORM_PLAN.md`.
- Any modification to existing Yggdrasil or Stofa designs (see `[[69_INTEGRATION_ROADMAP]]` for interaction).

---

## 10. Risk Register

| Risk | Mitigation |
|---|---|
| Slice 3 revised grows to 8-10 weeks; operators wait too long for any visible delta | Hermes-portion ships first (skills, MCP server, tools parallelism) as 3a; SAP-portion as 3b. Each subship adds visible value. |
| Affect engine in slice 4 is too entangled with the memory provider in (originally) slice 4 | Slice 4 and 5 separated per `§4`; affect engine ships before memory provider; provider can later integrate with affect storage. |
| Tier ladder detection misclassifies hosts | Operator override is the safety valve. Detection is *advisory*, not authoritative. |
| Failsafe-default-quiet surprises operators who expected old SAP-style on-by-default | Wizard surfaces every reach surface explicitly; the surprise is *intended*. Documentation emphasizes the posture. |
| Persona-id collision (operator copies `~/.ember/identity/` across machines) | Brunnr detects duplicates at announcement; operator must choose which host keeps the persona_id. |
| Slice 6 (VRM avatar) is genuinely heavy; may slip | Slice 6 contents are individually small (consent gating ~150, library ~100, VTS port ~400) and can ship in 6a/6b/6c sub-slices. |

---

## 11. Cross-References

- `[[60_TRUE_NAME_REASSIGNMENT]]` — Cartographer's True Name proposals that several slices instantiate.
- `[[61_NEW_VOWS]]` — Cartographer's new Vows that slices honor.
- `[[64_AFFECTION_ENGINE_REIMAGINED]]` — Cartographer's affect engine that slice 4 builds.
- `[[66_INVENTED_METHODS]]` — invention catalogue that the slices instantiate.
- `[[68_DECISION_RECORDS]]` — the 12 SAP-derived ADR-Proposed records.
- `[[69_INTEGRATION_ROADMAP]]` — phasing across the codex constellation.
- `[[6A_MULTI_AGENT_PARTY]]` — slice 7 design source.
- `[[6B_LOW_POWER_EMBODIMENT]]` — slice 3 tier ladder and slice 6 cued library source.
- `[[6C_EMBER_WAVE_3_SLICE]]` — the concrete Wave 3 slice proposal, tying everything together.
- `[[hermes:65_SLICE_PLAN_REVISIONS]]` — the Hermes-side proposals that this doc adds to.
- `[[hermes:66_DECISION_RECORDS]]` — the Hermes ADRs that interleave with SAP ADRs.
- `[[ember:EMBER_SECOND_SLICE_PLAN]]` — the slice-2 plan this proposal builds from.
- `[[ember:0013-second-slice-ratification]]` — the standing-rules ADR.

---

## What This Means for Ember

**True Names affected:** All six Names eventually. Slice 3 touches Funi (tier detect, persona init, MCP server, skills), Munnr (glyphic, log-affect, wizard branching), Strengr (typed retry, exhaustion), Smiðja (tool parallelism, interrupt fan-out), Brunnr (persona table, skill discovery), Hjarta (wizard extension). Slice 4 emphasizes Hjarta and Munnr. Slice 5 emphasizes Funi (MCP client, behavior engine) and Brunnr (memory provider). Slice 6 emphasizes Munnr (avatar pipeline). Slice 7+ emphasizes Funi (peer protocol) and Hjarta (cross-host affect).

**Vows touched:** all ten Vows reinforced by at least one slice proposal; none violated. The most-watched Vows:

- *Most strengthened by SAP proposals:* **Surface Without Surveillance** (failsafe-default-quiet is the central rule); **Tiered Presence** (the tier ladder makes it operational); **Embodied Honesty** (affect engine + avatar consent gating).
- *Most watched:* **Smallness** — slice 3 revised is 8-10 weeks. Mitigation: sub-slicing into 3a/3b is acceptable.
- *Most clarified:* **Federated Self** — persona-id is the cheap foundation that makes multi-instance work tractable later.

**Concrete next step for the keeper:**

1. Read this doc, `[[hermes:65_SLICE_PLAN_REVISIONS]]`, and `[[68_DECISION_RECORDS]]`.
2. Decide whether to incorporate the SAP-S3-F/G/H/I additions into slice 3.
3. Decide whether to *separate* the affect-engine slice from the memory-provider slice (this doc's recommendation) or *combine* them.
4. Decide the meta refinements (`§6.1` tier acceptance subsection; `§6.2` SAP reference subsection).
5. Author `docs/architecture/EMBER_THIRD_SLICE_PLAN.md` per the decided shape; ratify via the next-available ADR number.

**The proposals stand as written. The slice plan does not change.**

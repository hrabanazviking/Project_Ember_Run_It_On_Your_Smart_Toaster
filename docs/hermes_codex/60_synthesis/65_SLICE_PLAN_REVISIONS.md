---
codex_id: 65_SLICE_PLAN_REVISIONS
title: Slice Plan Revisions — Proposed Only (DO NOT APPLY)
role: Cartographer
layer: Synthesis
status: draft
hermes_source_refs:
  - "(synthesises 60-64 against Ember's existing slice plan)"
ember_subsystem_targets: [Funi, Strengr, Brunnr, Munnr]
cross_refs:
  - 60_synthesis/60_HERMES_VS_EMBER_CROSSWALK
  - 60_synthesis/63_INTEGRATION_PATHS
  - 60_synthesis/64_MIGRATION_PLAN
  - 60_synthesis/66_DECISION_RECORDS
---

# 65 — Slice Plan Revisions

> *A proposal is a finger pointing at a door. The door stays closed until the keeper decides to open it.*
> — Védis Eikleið, with both hands held up

## 0. Posture — PROPOSE ONLY

**This document proposes revisions to Ember's ratification-gated slice plan. It does not modify the slice plan itself.** The slice plan lives in `docs/architecture/EMBER_SECOND_SLICE_PLAN.md` (slice 2, ratified 2026-05-21) and the still-future slice 3 plan that has not yet been authored. Both are *ratification-gated* — Volmarr ratifies; an ADR records.

This Cartographer doc gathers the slice-shaped implications of [[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]] through [[60_synthesis/64_MIGRATION_PLAN]] and presents them as **revision proposals**. Each proposal has:

- A *current state* description.
- A *proposed change*.
- A *rationale* tying the change to Hermes findings.
- A *cost/benefit* analysis.
- A *Vow check*.

The slice-plan keeper (Architect + Skald + Volmarr together) reviews these proposals and either:
- *Accepts* — incorporates into the next slice plan revision via an ADR.
- *Defers* — notes the proposal for later consideration without integrating.
- *Rejects* — records why the proposal does not fit.

## 1. The shape of the proposals

Ember's existing rhythm is **two-slice planning**: ADR 0007 ratified slice 1 (2026-05-21); ADR 0013 ratified slice 2 (also 2026-05-21). Slice 3 is *not yet planned* as of this Codex date. The revisions below propose **what slice 3 might contain**, drawing from Hermes findings.

The migration plan in [[60_synthesis/64_MIGRATION_PLAN]] sketches ten M-phases. The proposals here re-cut those into **slice-shaped bundles** — because slice plans are themed, not phase-numbered. A slice is a coherent narrative ("Household well + feels alive + gets useful") that bundles several ADRs and several phases.

## 2. Proposed slice 3 — *Skilled, Bridged, and Quiet*

**Theme (Skald-shaped):** Ember gains *learned procedure* (skills); she becomes *reachable as a peer* (MCP server); and she *holds her tongue more gracefully* (typed retry, exhaustion, interrupt fan-out — the "quiet" elements that keep her honest under failure).

**Current state (gap analysis from slice 2):**
- No skill subsystem. The agent has no procedural memory across sessions.
- No bidirectional MCP. ADR 0014 ratified the *intent* — bidirectional MCP — but slice 2 did not include implementation.
- Strengr's retry is basic. No typed exhaustion. No per-error-code TTL.
- Tools dispatch sequentially. No parallel batches.
- Interrupt handling exists at three sites but is not generalized for tool workers.

**Proposed slice 3 contents (bundling M1–M6 from [[60_synthesis/64_MIGRATION_PLAN]]):**

| ADR | Topic | Bundle origin |
|---|---|---|
| **ADR-Proposed-S3-A** | Skill subsystem v1 (read-only) — Funi reads SKILL.md from in-repo + user-local trees | M1 |
| **ADR-Proposed-S3-B** | Provider profile + transport split — Funi internal refactor | M2 |
| **ADR-Proposed-S3-C** | MCP server (read-only subset) — Munnr publishes 5 read-only tools | M3 |
| **ADR-Proposed-S3-D** | Tool batch parallelism + interrupt fan-out | M4 |
| **ADR-Proposed-S3-E** | Strengr typed retry + per-error-code exhaustion TTL | M6 |

**Acceptance criterion (proposed):**

> A fresh operator on a Raspberry Pi 5 with Ember v0.3.0 (slice-3 release) can:
>
> 1. `pip install ember-agent[sqlite_vec,pgvector,skills,mcp]`.
> 2. `ember chat` — sees the slice-2 wizard, completes it.
> 3. Asks "how should I write a plan for adding feature X to my project?" — Ember consults the seeded `writing-plans` skill (visible via `ember skills list`) and produces a structured response that references the skill's procedure.
> 4. Asks Ember to read three files at once — Ember dispatches them as parallel tool calls; wall-clock is < 60% of sequential time.
> 5. Hits Ctrl-C mid-execution — pending tool calls show `[interrupted by operator]` markers in the audit log; the running tools have ~3 s to clean up.
> 6. Runs `ember mcp serve` in a second terminal; a reference MCP client (e.g., from `mcptools` package) connects, lists 5 read-only tools (`sessions_list`, `session_get`, `episodes_read`, `events_poll`, `events_wait`), and successfully reads recent Episodes from this operator's Well.
> 7. Simulates a network failure mid-streaming via toxiproxy — Strengr returns typed `Unavailable(reason, until)`; Munnr renders a graceful banner; the partial reply is persisted with the `[interrupted by network]` tag.
> 8. Network restores → `ember doctor` shows all green within 5 s of restoration.

**Cost (proposed):**
- LOC: ~1,400 code + ~900 tests (per [[60_synthesis/63_INTEGRATION_PATHS]] sum for Paths 1, 2, 3, 5, 7, 8, 9).
- Calendar: 6-8 weeks of focused work.
- New extras: `skills`, `mcp`. (`pyyaml` already in `config`; the `mcp` Python package is the only genuinely new dep.)

**Benefit:**
- **Skills** unlock cross-session procedural memory — Ember knows *how to* approach a class of tasks without re-learning each time.
- **MCP server** makes Ember a citizen of the multi-agent ecosystem — a Claude Code, Cursor, or another Ember instance can read from her.
- **Parallel tools** halve typical wall-clock for multi-file inspection workflows.
- **Typed retry + exhaustion** deepens the graceful-offline contract; rate limits become a transparent, observable state instead of a confusing failure.
- **Interrupt fan-out** preserves Honest Memory under user interruption.

**Vow check:**
- Smallness ✅ (each addition opt-in via extras; total LOC respected).
- Tethered Grounding ✅ (no new confabulation surface).
- Graceful Offline ✅ (typed-retry deepens it).
- Pluggable Storage ✅ (unchanged).
- Unbroken Whole ✅ (each phase is whole files).
- Flexible Roots ✅ (skills use `~/.ember/` and `src/ember/skills/`).
- Public-Friendliness ✅ (`ember skills list`, `ember mcp serve` are plain CLI; no jargon).
- Honest Memory ✅ (synthetic cancellation messages preserve wire-protocol consistency).
- Modular Authorship ✅ (each new subsystem fails independently).
- Open Knowledge ✅ (MIT; documented; attributed where adapted).

**Open question for keeper review:** does slice 3 include **MCP client** as well, or does that wait for slice 4? MCP client (M5) depends on M4 (parallel tools) but is otherwise standalone. Recommendation: defer to slice 4 if slice 3 is feeling large; include if 6-8 weeks of focus is comfortable.

## 3. Proposed slice 4 — *Plural Minds, Plural Memories*

**Theme:** Ember gains the ability to consult *other agents* (as MCP clients) and to delegate her *memory* to specialised providers (the Vinátta reservation). She becomes a participant in a broader cognitive ecology, not just a consumer of it.

**Proposed contents:**

| ADR | Topic | Bundle origin |
|---|---|---|
| **ADR-Proposed-S4-A** | MCP client — Funi consumes external MCP servers as tools | M5 |
| **ADR-Proposed-S4-B** | Memory provider plug-in ABC — Vinátta surface; built-in provider wraps Brunnr | M7 |
| **ADR-Proposed-S4-C** | Agent-initiated skill writes — Ember writes new skills mid-conversation (audited) | M8 |
| **ADR-Proposed-S4-D** | (optional) Honcho/Mem0 reference Vinátta plugins as opt-in extras | (post-M7 follow-up) |

**Acceptance criterion (proposed):**

> An operator can:
>
> 1. `pip install ember-agent[skills,mcp]` (slice 3 extras).
> 2. `ember mcp-servers add filesystem --command "python -m mcp_filesystem"` — adds an external MCP server.
> 3. Restart `ember chat`. Funi's tool list now includes `mcp_filesystem_*` tools.
> 4. Ask Ember to use the filesystem MCP server's tools — Funi dispatches them via the MCP client; audit log records every call.
> 5. (Optional `ember-agent[vinatta-honcho]`) configure Honcho via `ember vinatta setup honcho` — Funi's prompt now includes Honcho's recall context; Ember's writes flow to Honcho in addition to Brunnr.
> 6. Ask Ember "save a skill: when I ask you to review a PR, follow X procedure" — Ember writes a SKILL.md to `~/.ember/skills/user-pr-review/`, with `author: ember-agent` and `provenance: session/<id>` frontmatter; audit log records the write; the skill is visible from the next session.

**Cost:**
- LOC: ~1,400 code + ~700 tests (Paths 4, 6, M8 portion of Path 1).
- Calendar: 6-8 weeks.
- New extras: `vinatta` (optional, generic), plus per-provider extras as they land.

**Benefit:**
- **MCP client** makes Ember a *consumer* of the multi-agent ecosystem (matching her MCP-server *producer* role from slice 3).
- **Memory provider plug-in** is the bridge to commercial third-party brains (Honcho, Mem0) for operators who want them, without binding Ember to any one.
- **Agent-initiated skill writes** close the procedural-memory loop — Ember learns from her own sessions.

**Vow check:** all ten Vows respected. The largest watch-point is Vow of Honest Memory for agent-initiated skill writes; mitigation is the audit-log requirement and the user-local-tree-only constraint.

**Open question for keeper review:** is the agent-initiated skill write (ADR-Proposed-S4-C) properly in slice 4, or does it deserve its own minor slice (3.5)? The skill subsystem is large enough that splitting "read-only" (slice 3) and "agent-can-write" (slice 3.5 or 4) is reasonable.

## 4. Proposed slice 5 (speculative) — *Quieter Still, Faster Still*

**Theme:** Performance refinements + the Gjallarhorn reservation lands as a single platform plugin (operator opt-in).

**Proposed contents:**
- M9 — background Episode persistence (with Auditor pass).
- M10 (conditional) — multi-credential pool, if operator pull justifies.
- First Gjallarhorn platform plugin — *one* platform, operator-requested, opt-in only.

This slice is **speculative**. Its contents depend on what operator usage of slices 3 and 4 reveals. Including the proposal here marks the territory; the actual slice 5 plan is the keeper's decision when slice 4 is ratifying.

## 5. Revisions to slice-plan *meta-shape*

A few proposed changes to the slice-plan *template* itself, derived from Hermes patterns:

### 5.1 Add an "Anti-Patterns Inherited" section to each slice plan

Hermes ships `docs/decisions/HERMES_OPENCLAW_DESIGN_ANTI_PATTERNS.md` (visible in `docs/decisions/` directory listing). Each slice's ADR should similarly enumerate the Hermes patterns it *deliberately did not adopt* and why. This makes the Vow-protected boundaries visible in retrospect.

### 5.2 Add a "Cross-Platform Acceptance" subsection

Slice 2's acceptance criterion runs only on Linux + macOS. Slice 3+ should explicitly include a Windows + WSL + Pi 5 verification matrix, per the [[CROSS_PLATFORM_PLAN]] pre-release checklist. This is **not a new constraint**, just an explicit articulation of the existing one.

### 5.3 Add a "Hermes Reference" subsection per ADR

Each new ADR that adopts a Hermes pattern should cite the Hermes source path(s) and the relevant Codex doc. This makes the lineage traceable in perpetuity. Example frontmatter addition:

```yaml
adapted_from:
  - hermes_path: agent/tool_dispatch_helpers.py:103-146
  - codex_ref: 20_interface/21_RPC_INTERFACE
```

## 6. The five proposals — a single table

| # | Proposal | Slice | Type | Recommendation |
|---|---|---|---|---|
| 1 | Slice 3 — Skilled, Bridged, Quiet | 3 | New | **Propose** |
| 2 | Slice 4 — Plural Minds, Plural Memories | 4 | New | **Propose** |
| 3 | Slice 5 (speculative) — Performance + first Gjallarhorn | 5 | New | **Surface as territory; defer concrete planning** |
| 4 | Add "Anti-Patterns Inherited" section to slice plan template | meta | Refinement | **Propose** |
| 5 | Add "Hermes Reference" subsection per ADR | meta | Refinement | **Propose** |

## 7. The slice-plan keeper's checklist (for review)

If the keeper takes up these proposals, the order of review:

1. Read [[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]] §13 — the high-value Gap list.
2. Read [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] §10 — the True Name proposals (decide Gjallarhorn/Vinátta reservations first).
3. Read [[60_synthesis/63_INTEGRATION_PATHS]] — the file-level integration details for each path.
4. Read [[60_synthesis/64_MIGRATION_PLAN]] — the phasing.
5. Decide which proposals from §6 (this doc) to accept, defer, or reject.
6. If accepting slice 3: instantiate as `docs/architecture/EMBER_THIRD_SLICE_PLAN.md` (or whatever path the convention specifies); ratify via ADR 0015 (or next available number).
7. If accepting meta refinements (#4, #5): edit `docs/architecture/EMBER_THIRD_SLICE_PLAN.md` template accordingly.

The Cartographer does not perform any of these steps. The Cartographer proposes the territory; the keeper draws the map.

## 8. What is explicitly NOT proposed

To save the keeper's time, here is what this doc deliberately does **not** propose:

- Any change to slice 1's ratification (it shipped; ADR 0007 is law).
- Any change to slice 2's ratification (it shipped; ADR 0013 is law).
- Any change to existing ADRs.
- Any rename of an existing True Name.
- Any architectural change to the Three Realms.
- Any modification to `docs/SYSTEM_VISION.md` (Skald's territory).
- Any modification to `docs/architecture/ARCHITECTURE.md` (Architect's territory).
- Any modification to the Cross-Platform Plan (already complete).

## What This Means for Ember

**True Names affected by accepting these proposals:** Funi (largest lift); Strengr (typed retry, exhaustion); Brunnr (Vinátta reservation, eventual provider plug-in); Munnr (MCP server publishing). Hjarta and Smiðja unchanged.

**Vows touched:** all ten Vows reinforced by at least one proposed slice; none violated by any proposal in its proposed form. The most-watched Vow is Smallness — the proposed slices are *additive* and stay opt-in via extras.

**Concrete next step for the keeper:**
1. Read this doc.
2. Read [[60_synthesis/66_DECISION_RECORDS]] for the ADR-Proposed records.
3. Decide whether to incorporate the slice-3 proposal into Ember's plan.

**The proposals stand as written. The slice plan does not change.**

**Cross-references:**
- [[60_synthesis/64_MIGRATION_PLAN]] — the phase sequencing that backs these slice proposals.
- [[60_synthesis/66_DECISION_RECORDS]] — the ADR-Proposed records for each accepted proposal.
- [[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]] — the source-of-truth for what Hermes offers.
- [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] — the True Name reservations these slices instantiate.

---
codex_id: CONTINUATION_BACKLOG
title: Continuation Backlog — Doc Status and Follow-Ups
role: Scribe
layer: Meta
status: draft
hermes_source_refs: []
ember_subsystem_targets: []
cross_refs:
  - meta/MANIFEST
  - meta/INDEX
  - meta/CROSS_AGENT_NOTES
---

# Continuation Backlog

*The Codex's task list. One row per doc; status is updated at the close of each authoring wave.*

This file is the Scribe's tracker. It records which docs have been written, which are partial, which need rewrite, and which need follow-up before the Codex can be declared whole. Future authors should consult this before starting a new wave and update it before closing one.

---

## Status Values

| Status | Meaning |
|---|---|
| `pending` | Doc not yet started. |
| `in-progress` | Doc started in current wave; not yet at full quality bar. |
| `partial` | Doc has substantial content but is missing material the author flagged in a `## Continuation Notes` block. |
| `complete` | Doc meets the quality bar in [[meta/SHARED_CONTEXT]] §6: 1,500–4,000 words, cites real Hermes paths, has `## What This Means for Ember`, frontmatter is correct. |
| `needs-rewrite` | Doc exists but a later wave found material problems (factual error, Vow violation, drift). |
| `verified` | Doc has been complete *and* cross-walked by a Scribe on a subsequent pass; cross-links resolve; frontmatter is current. |

A doc moves `pending → in-progress → partial → complete → verified`. The `needs-rewrite` flag overrides any prior status and signals the next wave's first priority.

---

## Wave 1 Snapshot (2026-05-22)

Wave 1 is the initial parallel-authoring pass: six specialists writing simultaneously. The Scribe's meta docs were written in the same wave but, by design, can be the *only* docs in the corpus whose status is reliable mid-wave.

Counts below are populated by the Scribe at wave close. While the wave is still active, treat all non-meta entries as best-effort.

---

## The Doc List

### meta/ — Scribe

| Slug | Status | Wave | Notes |
|---|---|---|---|
| `INDEX` | complete | 1 | Doorway written; cross-links to all 53 docs. Some link to docs that will be written by other authors in this same wave — those remain "forward links" until Wave 2's verification pass. |
| `READING_ORDER` | complete | 1 | Seven reader-goal paths drawn. |
| `MANIFEST` | complete | (pre-wave) | Authored before Wave 1 began; the Scribe inherits it. |
| `SHARED_CONTEXT` | complete | (pre-wave) | Authored before Wave 1 began; the Scribe inherits it. |
| `HERMES_REVISION` | complete | 1 | Commit `4e2c66a09` pinned; reproduction commands included. |
| `CROSS_AGENT_NOTES` | complete | 1 | Empty-but-structured. To be filled by any author needing cross-pollination. |
| `STYLE_GUIDE` | complete | 1 | Written from the conventions implied in `SHARED_CONTEXT`. |
| `CONTINUATION_BACKLOG` | complete | 1 | This file. |

### 00_vision/ — Skald (Sigrún Ljósbrá)

| Slug | Status | Wave | Notes |
|---|---|---|---|
| `00_OVERTURE` | pending | 1 | |
| `01_HERMES_ESSENCE` | pending | 1 | |
| `02_NAMING_PARALLELS` | pending | 1 | |
| `03_ANTI_HERMES` | pending | 1 | |
| `04_VISION_SYNTHESIS` | pending | 1 | |

### 10_domain/ — Architect (Rúnhild Svartdóttir)

| Slug | Status | Wave | Notes |
|---|---|---|---|
| `10_DOMAIN_MAP` | pending | 1 | |
| `11_AGENT_CORE` | pending | 1 | |
| `12_SKILLS_PROCEDURAL_MEMORY` | pending | 1 | |
| `13_TOOLS_SUBSYSTEM` | pending | 1 | |
| `14_GATEWAY_MULTI_PLATFORM` | pending | 1 | |
| `15_PROVIDERS_MULTI_MODEL` | pending | 1 | |
| `16_TUI_GATEWAY_BACKENDS` | pending | 1 | |
| `17_PLUGINS_EXTENSIBILITY` | pending | 1 | |
| `18_HERMES_CLI` | pending | 1 | |
| `19_BOUNDARY_LAW` | pending | 1 | |

### 20_interface/ — Cartographer (tracing) + Auditor (verification)

| Slug | Owner | Status | Wave | Notes |
|---|---|---|---|---|
| `20_MCP_INTEGRATION` | Cartographer | pending | 1 | |
| `21_RPC_INTERFACE` | Cartographer | pending | 1 | |
| `22_SKILL_INTERFACE` | Cartographer | pending | 1 | |
| `23_PROVIDER_INTERFACE` | Cartographer | pending | 1 | |
| `24_MEMORY_INTERFACE` | Auditor | pending | 1 | |
| `25_GATEWAY_INTERFACE` | Auditor | pending | 1 | |
| `26_TUI_BACKEND_INTERFACE` | Auditor | pending | 1 | |
| `27_PLUGIN_INTERFACE` | Auditor | pending | 1 | |

### 30_execution/ — Forge (Eldra Járnsdóttir)

| Slug | Status | Wave | Notes |
|---|---|---|---|
| `30_SELF_HEALING_LOOP` | pending | 1 | |
| `31_CROSS_PLATFORM_TACTICS` | pending | 1 | |
| `32_MULTI_DEVICE_ORCHESTRATION` | pending | 1 | |
| `33_HOT_COLD_TIERS` | pending | 1 | |
| `34_PROCEDURAL_SKILL_CRAFTING` | pending | 1 | |
| `35_TRAJECTORY_COMPRESSION` | pending | 1 | |
| `36_CONTEXT_FILE_DISCIPLINE` | pending | 1 | |
| `37_SCHEDULING_DELEGATION` | pending | 1 | |
| `38_PERSISTENT_MEMORY` | pending | 1 | |
| `39_INTERRUPT_MULTILINE_TUI` | pending | 1 | |
| `40_SERVERLESS_HIBERNATION` | pending | 1 | |
| `41_MULTI_PROVIDER_FAILOVER` | pending | 1 | |

### 50_verification/ — Auditor (Sólrún Hvítmynd)

| Slug | Status | Wave | Notes |
|---|---|---|---|
| `50_HERMES_RISK_REGISTER` | pending | 1 | |
| `51_EMBER_GAP_ANALYSIS` | pending | 1 | |
| `52_ANTIPATTERN_CATALOG` | pending | 1 | |
| `53_CRASH_PROOFING_PATTERNS` | pending | 1 | |
| `54_SECURITY_REVIEW` | pending | 1 | |
| `55_INVARIANT_LIST` | pending | 1 | |
| `56_TESTING_STRATEGY` | pending | 1 | |

### 60_synthesis/ — Cartographer (Védis Eikleið)

| Slug | Status | Wave | Notes |
|---|---|---|---|
| `60_HERMES_VS_EMBER_CROSSWALK` | pending | 1 | |
| `61_TRUE_NAME_REASSIGNMENT` | pending | 1 | |
| `62_DEPENDENCY_FLOW` | pending | 1 | |
| `63_INTEGRATION_PATHS` | pending | 1 | |
| `64_MIGRATION_PLAN` | pending | 1 | |
| `65_SLICE_PLAN_REVISIONS` | pending | 1 | |
| `66_DECISION_RECORDS` | pending | 1 | |
| `67_GLOSSARY_AND_INDEX` | pending | 1 | |

---

## Roll-up by Layer

| Layer | Total | Complete | Partial | Pending | Needs-Rewrite | Verified |
|---|---:|---:|---:|---:|---:|---:|
| Vision | 5 | 0 | 0 | 5 | 0 | 0 |
| Domain | 10 | 0 | 0 | 10 | 0 | 0 |
| Interface | 8 | 0 | 0 | 8 | 0 | 0 |
| Execution | 12 | 0 | 0 | 12 | 0 | 0 |
| Verification | 7 | 0 | 0 | 7 | 0 | 0 |
| Synthesis | 8 | 0 | 0 | 8 | 0 | 0 |
| Meta | 8 | 8 | 0 | 0 | 0 | 0 |
| **Total** | **58** | **8** | **0** | **50** | **0** | **0** |

*(The Manifest lists 53 doc-slots; the table above counts both authored slots and the meta inheritances `MANIFEST` and `SHARED_CONTEXT`, plus the eight meta files including this one. The number to watch is `complete + verified` against the 53-slot target.)*

The roll-up will be updated at the close of each wave. While Wave 1 authors are still writing in parallel, the non-meta rows above remain at `pending`; the Scribe will sweep through and reclassify as `complete` / `partial` / `needs-rewrite` once each author's docs have landed.

---

## Wave 2 Priorities (forward-looking, to be confirmed at Wave 1 close)

The Scribe expects the following themes to need second-pass attention regardless of how Wave 1 lands:

1. **Cross-link verification.** Wave 1's docs link forward to each other across roles; some forward links will not resolve until Wave 2.
2. **Frontmatter audit.** Eight authors writing in parallel will produce eight slight dialects of the `hermes_source_refs:` field. The Scribe normalises in Wave 2.
3. **Glossary harmonisation.** [[60_synthesis/67_GLOSSARY_AND_INDEX]] cannot be authoritative until all other docs are written. Wave 2 absorbs new terms and reconciles preferred capitalisations.
4. **`## What This Means for Ember` quality.** The closing section is the most important paragraph of every doc. Wave 2 reads these alone, end to end, to confirm each one names True Names and Vows concretely.
5. **Hermes-revision drift.** If Wave 2 happens against a newer Hermes commit, [[meta/HERMES_REVISION]] is re-pinned and Wave 1 line citations are re-verified.
6. **Continuation Notes blocks.** Each `## Continuation Notes` block at the bottom of a partial doc gets a row in the Wave 2 backlog.

---

## How to Update This File

At the close of a wave, each author should update the rows for the docs they own:

1. Set `status` to one of `pending | in-progress | partial | complete | needs-rewrite | verified`.
2. Append a short note to the `Notes` cell if anything carries forward (e.g. *"missing line-number citations in §3, will close in Wave 2"*).
3. The Scribe updates the roll-up table after all authors have closed their rows.
4. If a doc was marked `needs-rewrite`, the Scribe links the relevant Open Note from [[meta/CROSS_AGENT_NOTES]] in the row.

The file is intentionally simple. The Scribe resists turning it into a project management system; it is a Codex tracker, not a sprint board.

---

## What This Means for Ember

A Codex without a backlog is a Codex that quietly forgets which of its claims have been verified. This file is small, but it is the difference between *"the Codex is fifty-three docs"* and *"the Codex has fifty-three docs at the following states of completeness"*. It honours the **Vow of Honest Memory** at the corpus level: the Codex is honest about how done it is.

This file affects no True Name. It protects the Codex's claim to be a living, maintainable artefact — the practice the [[meta/INDEX]] proposes Ember's relationship to large external agents should rest on.

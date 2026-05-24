# Hermes Codex — Master Manifest

> The Codex is a structured corpus of 53+ docs mining the Hermes Agent codebase (NousResearch/hermes-agent) for everything that can make Ember more advanced, robust, self-healing, and futuristic. Authored by six Mythic Engineering specialists working in parallel.

**Status:** Draft (in active authoring)
**Last updated:** 2026-05-22
**Hermes commit examined:** see `meta/HERMES_REVISION.md` (Scribe will write this)
**Shared brief:** [[meta/SHARED_CONTEXT]]

---

## How the Codex Is Organized

By the **five-layer Mythic Engineering model** plus a Synthesis layer and Meta. Each layer has a primary Role owner.

| Layer | Owner | Folder | Docs |
|---|---|---|---|
| Vision | Skald | `00_vision/` | 5 |
| Domain | Architect | `10_domain/` | 10 |
| Interface | Cartographer (tracing) + Auditor (verification) | `20_interface/` | 8 |
| Execution | Forge | `30_execution/` | 12 |
| Verification | Auditor | `50_verification/` | 7 |
| Synthesis | Cartographer | `60_synthesis/` | 8 |
| Meta | Scribe | `meta/` | 3 |
| **Total** | | | **53** |

---

## The Full Doc List (with slugs and one-line scope)

### 00_vision/ — Skald (Sigrún Ljósbrá)

| Slug | One-Line Scope |
|---|---|
| `00_OVERTURE` | What Hermes is, what it means for Ember, why this Codex was written, in Skald-voice |
| `01_HERMES_ESSENCE` | Hermes's identity stripped to its bones — what it *wants* to be |
| `02_NAMING_PARALLELS` | Mapping Hermes concepts to Ember's True Names (Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr) |
| `03_ANTI_HERMES` | What Ember must NOT inherit; the anti-patterns Hermes embodies that violate Ember's Vows |
| `04_VISION_SYNTHESIS` | The synthesized vision: post-Hermes Ember — who she becomes |

### 10_domain/ — Architect (Rúnhild Svartdóttir)

| Slug | One-Line Scope |
|---|---|
| `10_DOMAIN_MAP` | Full Hermes domain decomposition — every major subsystem and its responsibility |
| `11_AGENT_CORE` | Deep dive on `agent/` (80+ modules): conversation loop, context engine, memory manager, prompts, dispatch |
| `12_SKILLS_PROCEDURAL_MEMORY` | `skills/` + `optional-skills/` — procedural memory architecture, auto-creation, agentskills.io |
| `13_TOOLS_SUBSYSTEM` | `tools/`, `toolsets.py`, `toolset_distributions.py` — how 40+ tools are organized, packaged, dispatched |
| `14_GATEWAY_MULTI_PLATFORM` | `gateway/` — Telegram, Discord, Slack, WhatsApp, Signal; channel directory, delivery, mirror, pairing |
| `15_PROVIDERS_MULTI_MODEL` | `providers/`, model adapters in `agent/` — how 200+ models are abstracted |
| `16_TUI_GATEWAY_BACKENDS` | `tui_gateway/` — Docker, SSH, Modal, Daytona, Singularity, Vercel Sandbox terminal backends |
| `17_PLUGINS_EXTENSIBILITY` | `plugins/` — 16+ plugins, plugin contract, dynamic load, dependency declaration |
| `18_HERMES_CLI` | `hermes_cli/`, `cli.py` (662 KB), `hermes_cli/proxy/` — TUI patterns at scale |
| `19_BOUNDARY_LAW` | Hermes boundary discipline — where it succeeds, where it leaks, lessons for Ember |

### 20_interface/ — Cartographer (tracing) + Auditor (verification)

| Slug | Owner | One-Line Scope |
|---|---|---|
| `20_MCP_INTEGRATION` | Cartographer | `mcp_serve.py`, MCP plumbing, how Hermes is both client and server |
| `21_RPC_INTERFACE` | Cartographer | Python RPC for skills calling tools, agentic IPC |
| `22_SKILL_INTERFACE` | Cartographer | `agentskills.io` contract, skill manifest format, skill lifecycle |
| `23_PROVIDER_INTERFACE` | Cartographer | Provider abstraction — input/output, retry, rate-limit, streaming |
| `24_MEMORY_INTERFACE` | Auditor | Memory API surface — FTS5 search, LLM summarization, Honcho user modeling |
| `25_GATEWAY_INTERFACE` | Auditor | Multi-platform messaging contract — message shape, hooks, delivery |
| `26_TUI_BACKEND_INTERFACE` | Auditor | Terminal backend contract — process spawn, IO, lifecycle |
| `27_PLUGIN_INTERFACE` | Auditor | Plugin contract — discovery, init, teardown, dependency declaration |

### 30_execution/ — Forge (Eldra Járnsdóttir)

| Slug | One-Line Scope |
|---|---|
| `30_SELF_HEALING_LOOP` | Hermes's closed learning loop — skill auto-creation, self-improvement, persistence across sessions |
| `31_CROSS_PLATFORM_TACTICS` | How Hermes runs on $5 VPS → cloud → workstation; Termux, Docker, Nix, Modal |
| `32_MULTI_DEVICE_ORCHESTRATION` | How to harvest many devices at once; subagents, isolated workstreams, federation patterns |
| `33_HOT_COLD_TIERS` | Performance tier strategy — different models/configs for different hardware classes |
| `34_PROCEDURAL_SKILL_CRAFTING` | The mechanics of how Hermes auto-creates skills from experience |
| `35_TRAJECTORY_COMPRESSION` | `trajectory_compressor.py` (65 KB) — batch training data pipeline, what it enables |
| `36_CONTEXT_FILE_DISCIPLINE` | Project-level context files, prompt injection patterns, prompt-caching ergonomics |
| `37_SCHEDULING_DELEGATION` | `cron/`, isolated subagents, async work, batch_runner.py |
| `38_PERSISTENT_MEMORY` | Memory persistence, FTS5 indexing, LLM summarization, cross-session recall |
| `39_INTERRUPT_MULTILINE_TUI` | TUI patterns: multiline editing, slash completion, history, interrupt-without-loss |
| `40_SERVERLESS_HIBERNATION` | Modal/Daytona dormancy — hibernate when idle, cost-near-zero between sessions |
| `41_MULTI_PROVIDER_FAILOVER` | Provider failover, rate-limit handling, credential pool, retry strategy |

### 50_verification/ — Auditor (Sólrún Hvítmynd)

| Slug | One-Line Scope |
|---|---|
| `50_HERMES_RISK_REGISTER` | What could go wrong with Hermes's patterns — operational, security, correctness risks |
| `51_EMBER_GAP_ANALYSIS` | What Ember currently lacks compared to Hermes; what closing each gap would require |
| `52_ANTIPATTERN_CATALOG` | Hermes patterns Ember should NOT adopt — and why each one would harm Ember |
| `53_CRASH_PROOFING_PATTERNS` | Hermes patterns that survive partial failure; how to lift them into Ember |
| `54_SECURITY_REVIEW` | Multi-platform/MCP/credential-pool security analysis; what Ember inherits, what she should harden |
| `55_INVARIANT_LIST` | Invariants Ember must maintain when borrowing Hermes ideas (ID uniqueness, load order, state shape) |
| `56_TESTING_STRATEGY` | How to verify Hermes-inspired features — unit, boundary, integration, invariant tests |

### 60_synthesis/ — Cartographer (Védis Eikleið)

| Slug | One-Line Scope |
|---|---|
| `60_HERMES_VS_EMBER_CROSSWALK` | Module-by-module mapping: Hermes concept → Ember True Name → current state |
| `61_TRUE_NAME_REASSIGNMENT` | Proposed expansions/clarifications to Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr based on Hermes findings |
| `62_DEPENDENCY_FLOW` | Hermes data flow traced end-to-end; analogue Ember data flow drawn |
| `63_INTEGRATION_PATHS` | Concrete paths to wire Hermes patterns into Ember without violating Vows |
| `64_MIGRATION_PLAN` | Phased plan to evolve Ember toward post-Hermes capability — sequenced, gated, reversible |
| `65_SLICE_PLAN_REVISIONS` | Proposed revisions to Ember's ratification-gated slice plan (proposes only — does not modify) |
| `66_DECISION_RECORDS` | ADR-style decision records for the most consequential adoption decisions |
| `67_GLOSSARY_AND_INDEX` | Master term glossary — Hermes vocabulary, Ember vocabulary, mapping between them |

### meta/ — Scribe (Eirwyn Rúnblóm)

| Slug | One-Line Scope |
|---|---|
| `INDEX` | Entry point for the entire Codex; one-paragraph readable summary, links to everything |
| `READING_ORDER` | Recommended traversal paths for different reader goals (vision-first, implementer, architect, auditor) |
| `MANIFEST` | This file. Master list. Authoritative when other listings disagree. |
| `SHARED_CONTEXT` | The brief every agent reads before writing. Authored before the agents launched. |
| `CROSS_AGENT_NOTES` *(if needed)* | Cross-pollination notes left by one agent for another |
| `HERMES_REVISION` *(Scribe)* | Captured git revision of the Hermes clone used as source-of-truth |

---

## Cross-Linking Convention

Inline link to another Codex doc: `[[60_synthesis/61_TRUE_NAME_REASSIGNMENT]]`

Frontmatter `cross_refs:` field lists the docs you've linked to.

A link to a not-yet-written doc is *fine* — that's a marker for the Scribe to verify on the final pass.

---

## The Six Authors

| Role | Persona | Layer Owned |
|---|---|---|
| Skald (Sigrún Ljósbrá) | INFJ 4w5, visionary poet | Vision |
| Architect (Rúnhild Svartdóttir) | INTJ 5w6, dark strategist | Domain |
| Cartographer (Védis Eikleið) | INFP 9w1, grounded oracle | Interface (tracing) + Synthesis |
| Forge (Eldra Járnsdóttir) | ESTP 8w7, fire-worker | Execution |
| Auditor (Sólrún Hvítmynd) | INTJ 1w9, cold mirror | Verification + Interface (verification) |
| Scribe (Eirwyn Rúnblóm) | ISFJ 6w5, archivist | Meta |

---

## Reading Order (Recommended)

For first-time readers, the Scribe will refine this in `meta/READING_ORDER.md`. Provisional order:

1. `meta/INDEX` → `meta/MANIFEST` (this file) → `meta/SHARED_CONTEXT`
2. `00_vision/00_OVERTURE` → `00_vision/01_HERMES_ESSENCE` → `00_vision/02_NAMING_PARALLELS`
3. `10_domain/10_DOMAIN_MAP` for the lay of the land
4. Any 10_domain module deep-dive that matches your interest
5. `20_interface/` for the contracts that bind it together
6. `30_execution/` for the patterns you'd actually copy
7. `50_verification/` for the risks and gaps
8. `60_synthesis/` for the integration plan
9. `00_vision/04_VISION_SYNTHESIS` and `00_vision/03_ANTI_HERMES` to close

---

*"A good name does not merely label a thing. It reveals what the thing has always wanted to be."*
— Sigrún Ljósbrá

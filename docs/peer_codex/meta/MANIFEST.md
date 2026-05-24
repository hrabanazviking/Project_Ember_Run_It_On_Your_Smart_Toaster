# Peer Codex (Wave 2) — Master Manifest

> Wave 2 mines three peer agent codebases (Letta + smolagents + Goose) to triangulate against Hermes findings and reveal Ember-relevant patterns Hermes lacks.

**Status:** Authoring (parallel, six agents)
**Last updated:** 2026-05-22
**Brief:** [[meta/SHARED_CONTEXT]]
**Hermes Codex (Wave 1):** `~/ai/ember/docs/hermes_codex/`

---

## Peer Sources (pinned)

| Peer | Repo | SHA | Tag | Lines |
|---|---|---|---|---|
| Letta | letta-ai/letta | `1131535716e8a31c9a437f8695e25ac98f203a24` | `v0.16.8` | 246,861 py |
| smolagents | huggingface/smolagents | `3cd5c84e7386fa8b93514cc8fd05dcda1fe44a7d` | `v1.0.0+921` | 30,968 py |
| Goose | block/goose | `ca26f01d3acd9871691fa8981f05d19aed9a3b82` | `v2.0-rc-04-27` | 369,753 rs+ts |

Clones at `/tmp/letta`, `/tmp/smolagents`, `/tmp/goose`.

---

## Doc Allocation By Role (target counts; ±2 OK)

### 00_vision/ — Skald (Sigrún) — 6 docs

| Slug | Scope |
|---|---|
| `LETTA_ESSENCE` | Letta's identity stripped — memory-centric philosophy, MemGPT lineage, what Letta *wants to be* |
| `SMOL_ESSENCE` | smolagents's identity — smallness-as-design, code-execution-as-action |
| `GOOSE_ESSENCE` | Goose's identity — local-first, MCP-native, cross-platform desktop |
| `CROSS_TRIANGULATION` | Three peer philosophies vs Hermes vs Ember — what truth emerges from triangulation |
| `CROSS_ANTI_PEERS` | What Ember must NOT inherit from any peer; Vows-violation map |
| `CROSS_VISION_REFINED` | Refined post-Wave-2 Ember vision; vow renewal in light of all 4 mined codebases |

### 10_domain/ — Architect (Rúnhild) — 10 docs

| Slug | Scope |
|---|---|
| `LETTA_DOMAIN_MAP` | Full Letta decomposition; modules, boundaries |
| `LETTA_MEMORY_ARCHITECTURE` | core/archival/recall memory blocks; tool-callable memory management |
| `LETTA_SERVER_CLIENT_SPLIT` | Server vs client architecture; deployment shape |
| `SMOL_DOMAIN_MAP` | Full smolagents decomposition; why so small |
| `SMOL_CODE_EXECUTION_CORE` | local_python_executor / e2b_executor as the central design |
| `GOOSE_DOMAIN_MAP` | Goose Rust workspace decomposition; crates roles |
| `GOOSE_RECIPES_EXTENSIONS_SESSIONS` | The three core abstractions; how they compose |
| `GOOSE_CROSS_LANGUAGE` | Rust core + TS UI + MCP — cross-language IPC patterns |
| `CROSS_DOMAIN_TRIANGULATION` | All 4 architectures (Hermes + 3 peers) compared; convergence/divergence |
| `CROSS_BOUNDARY_LAW_V2` | Boundary-law update post-Wave-2; new candidate Vows |

### 20_interface/ — Cartographer (4) + Auditor (4) — 8 docs

| Slug | Owner | Scope |
|---|---|---|
| `LETTA_MEMORY_TOOL_INTERFACE` | Cartographer | Letta's *agent-callable* memory tools: schema, lifecycle, invariants |
| `SMOL_TOOL_INTERFACE` | Cartographer | smolagents tool & model interfaces; HF Hub integration |
| `GOOSE_MCP_INTERFACE` | Cartographer | Goose's MCP usage — extensions, recipes, server-vs-extension |
| `CROSS_TOOL_PROTOCOL_TRIANGULATION` | Cartographer | Tool protocols compared: Hermes toolsets vs Letta memory-tools vs smolagents tools vs Goose extensions |
| `LETTA_API_VERIFICATION` | Auditor | Letta's REST/SDK API surface; invariants, weak contracts |
| `SMOL_EXECUTOR_VERIFICATION` | Auditor | Code execution safety surface; sandbox guarantees |
| `GOOSE_SAFETY_INTERFACE` | Auditor | Goose's safety guardrails — what they enforce, what they don't |
| `CROSS_INTERFACE_INVARIANTS` | Auditor | Cross-peer interface invariants Ember should respect |

### 30_execution/ — Forge (Eldra) — 10 docs

| Slug | Scope |
|---|---|
| `LETTA_AGENT_LOOP` | Letta's step()/think()/act() loop |
| `LETTA_MEMORY_OPERATIONS` | Memory edit/append/replace/move patterns; the agentic discipline |
| `SMOL_CODE_AS_ACTION` | Code-execution-as-action pattern; pros/cons; Ember applicability |
| `SMOL_MINIMALISM_LESSONS` | What got cut to keep it small; transferable disciplines |
| `GOOSE_SESSION_PERSISTENCE` | Session state lifecycle; resume; multi-session |
| `GOOSE_RECIPE_AUTHORING` | Declarative agent configs — Recipes spec, examples |
| `GOOSE_RUST_PATTERNS` | Rust patterns worth lifting (or worth noting Python can't have); async/IPC/error model |
| `CROSS_AGENT_LOOP_TRIANGULATION` | Loops compared across all 4 agents; what's universal, what's local |
| `CROSS_EXECUTION_PATTERNS_LIFT` | Concrete patterns to lift into Ember from each peer |
| `CROSS_CROSS_PLATFORM_TACTICS_V2` | Cross-platform lessons specifically from Goose's multi-OS shipping |

### 50_verification/ — Auditor (Sólrún) — 8 docs

| Slug | Scope |
|---|---|
| `LETTA_RISK_REGISTER` | Letta-specific risks; what hurts when scaled down to Ember's hw |
| `SMOL_RISK_REGISTER` | smolagents-specific risks; what's missing from the minimalism |
| `GOOSE_RISK_REGISTER` | Goose-specific risks; Rust pitfalls, IPC fragility, MCP attack surface |
| `CROSS_RISK_TRIANGULATION` | Risks that appear across 2+ peers; universal hazards |
| `CROSS_EMBER_GAP_ANALYSIS_V2` | Updated Ember gap analysis vs all 4 peers |
| `CROSS_ANTIPATTERN_CATALOG_V2` | Antipatterns Ember must refuse — Wave-2-augmented list |
| `CROSS_INVARIANT_LIST_V2` | Invariants list updated with peer-agent learnings |
| `CROSS_TESTING_STRATEGY_V2` | Testing-strategy update; specific test suites per pattern |

### 60_synthesis/ — Cartographer (Védis) — 7 docs

| Slug | Scope |
|---|---|
| `CROSSWALK_LETTA_TO_EMBER` | Module-by-module Letta→Ember crosswalk |
| `CROSSWALK_SMOL_TO_EMBER` | Module-by-module smolagents→Ember crosswalk |
| `CROSSWALK_GOOSE_TO_EMBER` | Module-by-module Goose→Ember crosswalk |
| `CROSS_TRUE_NAME_PROPOSALS_V2` | Updated True Name proposals; what's strengthened, what's weakened |
| `CROSS_INTEGRATION_PATHS_V2` | Integration paths refreshed with peer-agent options |
| `CROSS_MIGRATION_PLAN_V2` | Migration plan update; phases re-sequenced if needed |
| `CROSS_DECISION_RECORDS_V2` | Additional ADRs from Wave 2; status: Proposed |

### meta/ — Scribe (Eirwyn) — 5 docs

| Slug | Scope |
|---|---|
| `INDEX` | Entry point for Peer Codex |
| `READING_ORDER` | Recommended traversal by reader-goal |
| `PEER_REVISIONS` | Pinned SHAs + commit subjects + clone reproduction commands |
| `STYLE_GUIDE_DELTA` | What differs from Hermes Codex style guide (peer prefixes, peer_targets frontmatter, etc.) |
| `CONTINUATION_BACKLOG` | Per-doc status table for Wave 2 |

---

## Total Target

**~54 docs** (vs Hermes's 58). Each agent owns roughly:
- Skald: 6
- Architect: 10
- Cartographer + Auditor: 8 (split 4/4)
- Forge: 10
- Auditor: +8 (in 50_verification) → Auditor total 12
- Cartographer: +7 (in 60_synthesis) → Cartographer total 11
- Scribe: 5

If an agent runs out of budget, prioritize cross-comparison docs over per-peer essence docs (cross-comparison is harder to recover later).

---

## Cross-Linking

- Within Wave 2: `[[10_domain/LETTA_DOMAIN_MAP]]`
- Across to Hermes Codex: `[[hermes_codex/10_domain/11_AGENT_CORE]]`
- Across to Ember docs: `[[/docs/SYSTEM_VISION]]` (or absolute path)
- Links to not-yet-written docs are fine

---

*"Three peers triangulate where one informs. The grand plan is built on triangles."* — Védis Eikleið

---
codex_id: 67_GLOSSARY_AND_INDEX
title: Glossary and Index — Hermes Vocabulary, Ember Vocabulary, the Mapping Between
role: Cartographer
layer: Synthesis
status: draft
hermes_source_refs:
  - "(spans the entire Hermes codebase and Ember docs corpus)"
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 60_synthesis/60_HERMES_VS_EMBER_CROSSWALK
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/62_DEPENDENCY_FLOW
  - 60_synthesis/63_INTEGRATION_PATHS
  - 60_synthesis/64_MIGRATION_PLAN
  - 60_synthesis/65_SLICE_PLAN_REVISIONS
  - 60_synthesis/66_DECISION_RECORDS
  - 20_interface/20_MCP_INTEGRATION
  - 20_interface/21_RPC_INTERFACE
  - 20_interface/22_SKILL_INTERFACE
  - 20_interface/23_PROVIDER_INTERFACE
---

# 67 — Glossary and Index

> *Two languages, three speakers, one map. The dictionary is what makes the map readable.*
> — Védis Eikleið, with both alphabets open

## 0. How this glossary is organised

Three sections:

- **§1 — Hermes vocabulary.** Terms used in the Hermes source/docs that an Ember-reader needs to recognise. Each entry: definition, Hermes source path, Ember analogue (if any).
- **§2 — Ember vocabulary.** Terms used in Ember's docs and code. Each entry: definition, code path, Hermes analogue (if any).
- **§3 — Reserved names.** New True Names proposed in [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] that may earn realisation later.

Cross-references throughout. Etymological notes for the Norse names. The total entry count exceeds 60.

## 1. Hermes vocabulary

### ACP (Agent Client Protocol)

Schema-based agent IPC protocol. Hermes ships an ACP adapter at `acp_adapter/server.py` (1,200+ lines). Used by editors (Zed) and similar tools to drive an agent.
**Ember analogue:** none. MCP is Ember's analogue protocol; ACP is deferred per [[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]] §8.

### agentskills.io

A public registry of agent-skills sharing Hermes's `SKILL.md` format. Hermes's in-repo `skills/` tree is the reference implementation.
**Ember analogue:** the contract is portable; Ember can publish her seed skills there once they're stable.

### AIAgent

The central agent class in `run_agent.py` (180 KB). Owns: client construction, streaming, credential refresh, prompt caching, interrupt handling, retry logic — all the state that the `ProviderTransport` deliberately does *not* own.
**Ember analogue:** the chat loop in `src/ember/spark/munnr/chat.py` plus `src/ember/spark/funi/handle.py`. Ember collapses what `AIAgent` separates because of scale.

### api_mode

A string field on `ProviderProfile` (`providers/base.py:43`) declaring which transport handles the provider. Values: `chat_completions`, `anthropic_messages`, `bedrock`, `codex`.
**Ember analogue:** *proposed* `runtime_kind` on `FuniProfile` (ADR-Proposed-Funi-001).

### approval_callback

Thread-local callable that handles dangerous-command prompts. Propagated from the agent thread into worker threads via `_set_approval_callback`. See `agent/tool_executor.py:223-234`.
**Ember analogue:** the approval policy in slice 2 (ADR 0011). Ember does not yet propagate into workers because there are no workers; that lands in ADR-Proposed-Funi-002.

### CredentialPool

The 1,955-line credential routing subsystem at `agent/credential_pool.py`. Owns: multi-credential rotation, exhaustion tracking with per-error-code TTL, OAuth refresh, cross-provider failover.
**Ember analogue:** Strengr's single-credential resolver today; multi-credential pool deferred to ADR-Proposed-Strengr-002.

### EventBridge

The 240-line class in `mcp_serve.py:204-444` that polls SessionDB via mtime-keyed SQLite reads and maintains an in-memory event queue for MCP `events_poll` / `events_wait` clients.
**Ember analogue:** *proposed* in ADR-Proposed-MCP-001, mirroring Hermes's pattern against Brunnr's `episode` table.

### FastMCP

The high-level MCP server implementation from the `mcp` Python package, `mcp.server.fastmcp.FastMCP`. Tool registration via `@mcp.tool()` decorator; JSON schema is introspected from Python type hints.
**Ember analogue:** same library; lazy-imported in proposed `src/ember/spark/munnr/mcp/` per ADR-Proposed-MCP-001.

### finish_reason

Field on `NormalizedResponse` indicating why the model stopped: `"stop"`, `"tool_calls"`, `"length"`, `"content_filter"`. Mapped from provider-specific stop reasons by `transport.map_finish_reason`.
**Ember analogue:** `FuniStreamChunk.finish_reason` in `src/ember/schemas/stream.py` already shipped slice 2.

### HERMES_HOME

Environment variable / directory for Hermes's user-local state. Defaults to `~/.hermes/`. Contains skills, sessions, channel directory, OAuth tokens.
**Ember analogue:** `~/.ember/` per Ember's Vow of Flexible Roots.

### Hermes-state DB

SQLite database at `${HERMES_HOME}/state.db` storing sessions, messages, tool calls, FTS5 index. Owned by `hermes_state.py` (140 KB).
**Ember analogue:** Brunnr's `~/.ember/well/store.db` (sqlite-vec backend) — much smaller equivalent. Ember's `episode` table is the analogue.

### Hooks framework

Plugin-installed callbacks invoked at gateway lifecycle points (`gateway/hooks.py`, `gateway/builtin_hooks/`). Examples: pre-message-send, post-message-receive.
**Ember analogue:** not implemented; deferred per [[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]] §4.

### MCP (Model Context Protocol)

JSON-RPC protocol for tool / resource / prompt exposure. Anthropic-originated; widely adopted by Claude Desktop, Cursor, Codex, et al.
**Ember analogue:** ADR 0014 ratified intent; implementation in ADR-Proposed-MCP-001 (server) and ADR-Proposed-MCP-003 (client).

### MemoryProvider

ABC at `agent/memory_provider.py:42-280` defining the 10+ method contract a memory plug-in implements. Honcho, Hindsight, Mem0 are external implementations.
**Ember analogue:** *proposed* Vinátta surface (ADR-Proposed-Brunnr-001).

### NormalizedResponse

Shared dataclass at `agent/transports/types.py:89-150` returned by every `transport.normalize_response`. Fields: `content`, `tool_calls`, `finish_reason`, `reasoning`, `usage`, `provider_data`.
**Ember analogue:** *proposed* `NormalizedFuniResponse` in ADR-Proposed-Funi-001.

### OAuth device_code flow

OAuth 2.0 device authorization grant. Used by Nous, openai-codex, xai-oauth, minimax-oauth.
**Ember analogue:** deferred. Ember v1 supports `api_key` only.

### parallel_tool_calls

Capability advertised by an MCP server indicating its tools are safe to call concurrently. Queried at `agent/tool_dispatch_helpers.py:90-100`.
**Ember analogue:** same query, when MCP client lands (ADR-Proposed-MCP-003).

### plugin.yaml

Manifest file for a Hermes plugin (model provider, memory provider, platform, etc.). Fields: `name`, `kind`, `version`, `description`, `author`.
**Ember analogue:** TBD when Ember's first plug-in subsystem lands; YAML chosen for consistency with operator config.

### PooledCredential

Dataclass at `agent/credential_pool.py:93-180` representing one credential in the pool. Fields include `provider`, `id`, `label`, `auth_type`, `priority`, `last_status`, `last_status_at`, exhaustion timestamps.
**Ember analogue:** not present; deferred to multi-credential pool.

### prepare_messages

`ProviderProfile` hook (`providers/base.py:95-101`) for provider-specific message preprocessing (e.g., Qwen normalises to list-of-parts).
**Ember analogue:** not present; drop in ADR-Proposed-Funi-001 v1; revisit when a second provider needs it.

### Procedural memory

The cognitive-science concept Hermes maps onto its skill subsystem. "Knowing how" stored as recallable procedures.
**Ember analogue:** *proposed* via ADR-Proposed-Skill-001.

### ProviderProfile

Declarative dataclass at `providers/base.py:38-185` containing everything about an inference provider: name, endpoints, env vars, default models, header quirks.
**Ember analogue:** *proposed* `FuniProfile` in ADR-Proposed-Funi-001.

### ProviderTransport

Behavioural ABC at `agent/transports/base.py:1-90`. Five required methods: `api_mode`, `convert_messages`, `convert_tools`, `build_kwargs`, `normalize_response`. Three optional: `validate_response`, `extract_cache_stats`, `map_finish_reason`.
**Ember analogue:** *proposed* `FuniTransport` in ADR-Proposed-Funi-001.

### Reasoning details

Extended-thinking blocks from Anthropic / OpenAI / Gemini surfaced in `NormalizedResponse.reasoning` and `NormalizedResponse.provider_data["reasoning_details"]`.
**Ember analogue:** not yet; defer until a thinking-capable Funi runtime ships.

### related_skills

Metadata field on a `SKILL.md` listing other skill names as graph edges. Resolution is across both trees; dangling refs silently fail.
**Ember analogue:** same; port verbatim per [[20_interface/22_SKILL_INTERFACE]].

### sanitize_context

The regex set at `agent/memory_manager.py:43-59` that strips `<memory-context>` fence tags, injected memory blocks, and system-note patterns from provider output before injection. Vow-of-Tethered-Grounding safety net.
**Ember analogue:** mandatory port per ADR-Proposed-Brunnr-001.

### sessions.json

JSON index at `${HERMES_HOME}/sessions/sessions.json` mapping session_key → entry (platform, chat_type, display_name, session_id, etc.). Read by `mcp_serve.py:81-95`.
**Ember analogue:** Brunnr's `session` table.

### Skill body / Skill frontmatter

Two parts of a `SKILL.md`. Frontmatter is the YAML mapping at the top (12-rule validator); body is the Markdown content.
**Ember analogue:** same shape, same validator (ADR-Proposed-Skill-001).

### Skill validator

The 12-rule function at `tools/skill_manager_tool.py:217-253` that gates SKILL.md writes.
**Ember analogue:** port verbatim; see [[20_interface/22_SKILL_INTERFACE]] §2.

### standing trust

The slice-2 (ADR 0011) policy that lets the operator pre-approve certain tool patterns without per-call prompts.
**Ember analogue:** native to Ember; ADR-Proposed-MCP-002 honours it.

### subagent

A child agent loop spawned by `delegate_task`. Has its own session, restricted toolset, parent_session_id pointer. Parent's memory provider gets `on_delegation(task, result, child_session_id=...)`.
**Ember analogue:** deferred. Ember v1 does not have subagents.

### Synthetic cancellation message

A `make_tool_result_message` call with `"[Tool execution cancelled — X was skipped due to user interrupt]"` content, appended for pending tools when interrupt fires. Preserves the wire-protocol invariant that every `tool_call` has exactly one matching result.
**Ember analogue:** *proposed* port in ADR-Proposed-Funi-002.

### TeeTransport

Multi-sink transport in `tui_gateway/transport.py`. Fans one frame out to multiple peers (stdio + WebSocket).
**Ember analogue:** none; pattern is on file for the future Ember sidecar dashboard.

### Tool registry (Hermes-internal)

The dispatcher at `agent/tool_executor.py` plus the per-tool definitions in `tools/`.
**Ember analogue:** `src/ember/spark/funi/tools/registry.py` already shipped slice 2.

### Trajectory

A session's full conversation history serialised for training-data extraction. `trajectory_compressor.py` (65 KB) turns trajectories into instruction-tuning pairs.
**Ember analogue:** Ember's `Episode` records; deferred trajectory compression.

### TUI gateway

The detached process at `tui_gateway/` that hosts the terminal UI front-end and dispatches JSON-RPC frames into the agent.
**Ember analogue:** none. Ember's CLI is in-process. The pattern is on file for future scale.

### `_coerce_int`

Three-line helper at `mcp_serve.py:118-134` that coerce-and-clamps numeric MCP tool inputs to handle untrusted client calls.
**Ember analogue:** mandatory port per ADR-Proposed-MCP-001.

### `_PEER_GONE_ERRNOS`

Tiny set at `tui_gateway/transport.py:43-50` classifying errno values that mean "peer disconnected cleanly" rather than "real I/O problem."
**Ember analogue:** pattern relevant when Ember gains a detached-process model; not present today.

### `_should_parallelize_tool_batch`

The rules engine at `agent/tool_dispatch_helpers.py:103-146` deciding sequential vs parallel dispatch.
**Ember analogue:** *proposed* port per ADR-Proposed-Funi-002.

## 2. Ember vocabulary

### ADR

Architecture Decision Record. Lives under `docs/decisions/NNNN-<slug>.md`. Ember's append-only decision log; inherited from Runa. Examples: ADR 0007 (slice 1 ratification), ADR 0013 (slice 2 ratification), ADR 0014 (bidirectional MCP).
**Hermes analogue:** Hermes uses CHANGELOG + design treatise (`AGENTS.md`); the ADR shape is Ember-specific.

### Brunnr

Old Norse: *brunnr*, "well, spring." Ember's pluggable storage adapter layer. Shipped backends: `sqlite_vec` (slice 1, default), `pgvector` (slice 2, Gungnir-compatible). Future: `qdrant`, `chroma`, `lancedb`.
**Hermes analogue:** approximately `hermes_state.py` (the session DB) plus the memory plugin layer. Hermes does not split storage and ingest the way Ember does.

### `BrunnrHandle`

The Protocol at `src/ember/well/brunnr/protocol.py` defining the 14-method surface every backend implements. RRF constant `k=60` shared across backends.
**Hermes analogue:** none direct; Hermes does not have an explicit pluggable-storage Protocol.

### `Disconnected`

Typed value returned by Strengr when the Well is unreachable. Carries `reason` (eight-class classification on pgvector) and `since` timestamp.
**Hermes analogue:** the credential pool's `last_status="exhausted"` + `last_error_reset_at`. Same idea, different boundary.

### Episode

The persistence unit Brunnr writes after every turn. Fields: user message, assistant reply, citations, audit refs, session_id, timestamp.
**Hermes analogue:** Hermes's message rows in `hermes_state.SessionDB`.

### `ember doctor`

Operator CLI command that probes Ember's health: Funi reachable, Brunnr reachable, config valid, audit log writable. Plain-English output.
**Hermes analogue:** `hermes doctor` at `hermes_cli/doctor.py`. Same pattern, much smaller scope.

### Funi

Old Norse: *funi*, "flame, fire." Ember's local model runtime. Shipped adapter: Ollama. Slice 2 added streaming (`complete_streaming`) and tool framework.
**Hermes analogue:** the `AIAgent` + transport layer in Hermes. Ember's Funi is the *navigator and reasoner*, not the *knowledge holder* — knowledge lives in Brunnr.

### `FuniHandle`

The Protocol in `src/ember/spark/funi/handle.py`. Methods: `complete()`, `complete_streaming()`.
**Hermes analogue:** the `ProviderTransport` ABC after the proposed refactor (ADR-Proposed-Funi-001).

### Gungnir

Volmarr's running Postgres + pgvector + Ollama installation at `gungnir:5432/knowledge`. 95 docs / 35,682 chunks at dim=768. The household-shared Well for Ember + Skein/Skry.
**Hermes analogue:** none. Gungnir is an Ember-ecosystem term.

### Hjarta

Old Norse: *hjarta*, "heart." Ember's first-run setup rite. Finite state machine, not generative. States enumerated, transitions unit-testable.
**Hermes analogue:** `agent/onboarding.py`. Smaller and more structured in Ember.

### Hringja (reserved-but-declined)

Old Norse: *hringja*, "to ring (a bell)." Proposed but declined True Name for cron / scheduling. Lives as `funi/schedule.py` inside Funi instead. See [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] §4.
**Hermes analogue:** `cron/` directory.

### Lærdómr (reserved-but-declined)

Old Norse: *lærdómr*, "learning, learnedness." Proposed but declined True Name for skills. Lives as `funi/skills/` inside Funi. See [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] §5.
**Hermes analogue:** the skill subsystem (`skills/`, `agent/skill_*.py`).

### Munnr

Old Norse: *munnr*, "mouth." Ember's command-line surface. Operator types here; Ember answers here. Slice 2 added streaming render, citation rendering, disconnect banner.
**Hermes analogue:** `cli.py` (662 KB) plus the TUI plus the gateway send path — Hermes spreads the same role over many files. Ember concentrates it.

### Mythic Engineering

Ember's development methodology. Six specialist roles (Skald, Architect, Cartographer, Forge, Auditor, Scribe). Five-layer model. Iron laws. Documented in `MYTHIC_ENGINEERING.md` and `docs/methodology/`.
**Hermes analogue:** Hermes uses `AGENTS.md` (53 KB design treatise) as its single methodology document. Ember's six-role structure does not have a Hermes peer.

### Primary Rite

The single interaction that defines whether Ember is alive: operator speaks → Ember consults the Well → answers honestly → remembers → names her limits. From `SYSTEM_VISION.md` §2.
**Hermes analogue:** none. Ember-specific Skald vocabulary.

### Skry

Volmarr's query-time entity projection method. Lives at `~/ai/skry-kg`. ~1/1000 cost of llama-per-chunk knowledge graph construction.
**Hermes analogue:** none. Ember-ecosystem term.

### Skein

Volmarr's embedding-derived knowledge graph method. Lives at `~/ai/skein-kg`. Sibling to Skry.
**Hermes analogue:** none.

### Smiðja

Old Norse: *smiðja*, "forge." Ember's ingest pipeline: content sources → chunk → embed → Brunnr. Slice 1 shipped local-files source.
**Hermes analogue:** approximately the `trajectory_compressor.py` ingestion path plus some `agent/context_engine.py` material; Hermes does not have a unified ingest abstraction.

### Strengr

Old Norse: *strengr*, "string, cord, tether." Ember's network layer to the Well. Owns auth, health, retry, transport selection, the graceful-offline contract.
**Hermes analogue:** the credential pool (`agent/credential_pool.py`) + retry layer (`agent/retry_utils.py`) + transport selection. Hermes spreads what Ember concentrates.

### Three Realms

Ember's mechanical separation: Spark (local), Thread (the tether), Well (memory/knowledge). Higher realm may import lower; never the reverse.
**Hermes analogue:** none. Hermes is a single Realm.

### True Name

A name chosen so the *name itself constrains the boundary*. From `MYTHIC_ENGINEERING.md` "naming as boundary." Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr are the six True Names. Vow-of-Modular-Authorship enforces them via mechanical band rules.
**Hermes analogue:** none. Hermes uses functional names ("agent core", "gateway", "transports").

### `Unavailable`

Typed value returned by Funi when Ollama (or future runtime) is unreachable.
**Hermes analogue:** `last_status="exhausted"` on `PooledCredential`. Same shape, different boundary.

### Vinátta (reserved)

Old Norse: *vinátta*, "friendship, kinship-bond." Reserved True Name for the future memory provider plug-in API. See [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] §6.
**Hermes analogue:** the `MemoryProvider` ABC at `agent/memory_provider.py:42-280`.

### Vow

One of the ten Unbreakable Vows in `SYSTEM_VISION.md` §3. Every architectural decision is measured against them. The Vows are: Smallness, Tethered Grounding, Graceful Offline, Pluggable Storage, the Unbroken Whole, Flexible Roots, Public-Friendliness, Honest Memory, Modular Authorship, Open Knowledge.
**Hermes analogue:** Hermes has design principles in `AGENTS.md` but no equivalent vow-system.

### Well

The realm containing Brunnr (storage) and Smiðja (ingest). Possibly local, possibly remote, possibly both at once.
**Hermes analogue:** approximately the SessionDB + skill corpus + memory plug-in target. Hermes does not group these under one term.

## 3. Reserved names

### Gjallarhorn (reserved)

Old Norse: *Gjallarhorn*, "the resounding horn" — Heimdall's instrument blown to announce arrivals. Reserved True Name for multi-platform messaging gateway (Telegram, Discord, Slack, WhatsApp, Signal, Matrix). Opt-in only; never default install. See [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] §3.
**Hermes analogue:** the `gateway/` subsystem (~25 files).

### Vinátta (reserved)

(See entry in §2 above.) **Hermes analogue:** `agent/memory_provider.py`.

### Hringja (declined)

(See entry in §2.) Reserved-but-declined; lives inside Funi.

### Lærdómr (declined)

(See entry in §2.) Reserved-but-declined; lives inside Funi.

## 4. Cross-vocabulary index

Quick-reference table mapping commonly-confused pairs:

| Hermes | Ember | Note |
|---|---|---|
| `AIAgent` | (chat loop in Munnr + Funi handle) | Hermes-class is bigger; Ember-equivalent is in-line |
| `ProviderProfile` | *proposed* `FuniProfile` | Declarative metadata; same shape |
| `ProviderTransport` | *proposed* `FuniTransport` | Behavioural; same shape |
| `NormalizedResponse` | *proposed* `NormalizedFuniResponse` | Five-method return |
| `MemoryProvider` | *proposed* Vinátta surface | Behavioural plug-in API |
| `CredentialPool` | Strengr (partial) | Multi-credential deferred |
| `SessionDB` | Brunnr (sqlite_vec) | Same SQLite substrate |
| `EventBridge` | *proposed* `munnr/mcp/event_bridge.py` | mtime-poll pattern |
| `SKILL.md` validator | *proposed* `funi/skills/loader.py` | 12-rule check; port verbatim |
| `_should_parallelize_tool_batch` | *proposed* `funi/tools/dispatch._should_parallelize_tool_batch` | Same rules engine |
| Synthetic cancellation message | *proposed* `funi/tools/dispatch.synthetic_cancellation` | Same shape |
| `_coerce_int` | *proposed* `munnr/mcp/coerce._coerce_int` | Verbatim port |
| `_PEER_GONE_ERRNOS` | (none yet) | Pattern on file for future detached-process model |
| `HERMES_HOME` | `~/.ember/` | Operator-state directory |
| Plugin via `plugin.yaml` | Plug-in via `__init__.py` registration | Both filesystem-walk |
| `agentskills.io` | (compatible; Ember can publish there) | Format-as-protocol |
| MCP server (`mcp_serve.py`) | *proposed* `munnr/mcp/server.py` | Read-only subset |
| MCP client (`tools/mcp_tool.py`) | *proposed* `funi/tools/mcp_client.py` | Same shape, audited |
| ACP server (`acp_adapter/server.py`) | (deferred indefinitely) | Sister protocol; MCP first |
| `tui_gateway/` (detached process) | (none) | Ember is in-process; pattern on file |
| Trajectory (training-data extract) | Episode (single-turn) + future smidja source | Episodes accumulate; extraction is a deferred Smiðja source |

## 5. The doc-by-doc index

The Codex doc IDs and their roles:

| ID | Title | Layer | Role | Status |
|---|---|---|---|---|
| `00_OVERTURE` | Overture | Vision | Skald | (Skald-owned) |
| `01_HERMES_ESSENCE` | Hermes Essence | Vision | Skald | (Skald-owned) |
| `02_NAMING_PARALLELS` | Naming Parallels | Vision | Skald | (Skald-owned) |
| `03_ANTI_HERMES` | Anti-Hermes | Vision | Skald | (Skald-owned) |
| `04_VISION_SYNTHESIS` | Vision Synthesis | Vision | Skald | (Skald-owned) |
| `10_DOMAIN_MAP` | Domain Map | Domain | Architect | (Architect-owned) |
| `11_AGENT_CORE` | Agent Core | Domain | Architect | (Architect-owned) |
| `12_SKILLS_PROCEDURAL_MEMORY` | Skills / Procedural Memory | Domain | Architect | (Architect-owned) |
| `13_TOOLS_SUBSYSTEM` | Tools Subsystem | Domain | Architect | (Architect-owned) |
| `14_GATEWAY_MULTI_PLATFORM` | Gateway Multi-Platform | Domain | Architect | (Architect-owned) |
| `15_PROVIDERS_MULTI_MODEL` | Providers Multi-Model | Domain | Architect | (Architect-owned) |
| `16_TUI_GATEWAY_BACKENDS` | TUI Gateway Backends | Domain | Architect | (Architect-owned) |
| `17_PLUGINS_EXTENSIBILITY` | Plugins / Extensibility | Domain | Architect | (Architect-owned) |
| `18_HERMES_CLI` | Hermes CLI | Domain | Architect | (Architect-owned) |
| `19_BOUNDARY_LAW` | Boundary Law | Domain | Architect | (Architect-owned) |
| `20_MCP_INTEGRATION` | MCP Integration | Interface | **Cartographer** | **draft (this doc)** |
| `21_RPC_INTERFACE` | RPC Interface | Interface | **Cartographer** | **draft** |
| `22_SKILL_INTERFACE` | Skill Interface | Interface | **Cartographer** | **draft** |
| `23_PROVIDER_INTERFACE` | Provider Interface | Interface | **Cartographer** | **draft** |
| `24_MEMORY_INTERFACE` | Memory Interface | Interface | Auditor | (Auditor-owned) |
| `25_GATEWAY_INTERFACE` | Gateway Interface | Interface | Auditor | (Auditor-owned) |
| `26_TUI_BACKEND_INTERFACE` | TUI Backend Interface | Interface | Auditor | (Auditor-owned) |
| `27_PLUGIN_INTERFACE` | Plugin Interface | Interface | Auditor | (Auditor-owned) |
| `30_SELF_HEALING_LOOP` | Self-Healing Loop | Execution | Forge | (Forge-owned) |
| `31_CROSS_PLATFORM_TACTICS` | Cross-Platform Tactics | Execution | Forge | (Forge-owned) |
| `32_MULTI_DEVICE_ORCHESTRATION` | Multi-Device Orchestration | Execution | Forge | (Forge-owned) |
| `33_HOT_COLD_TIERS` | Hot/Cold Tiers | Execution | Forge | (Forge-owned) |
| `34_PROCEDURAL_SKILL_CRAFTING` | Procedural Skill Crafting | Execution | Forge | (Forge-owned) |
| `35_TRAJECTORY_COMPRESSION` | Trajectory Compression | Execution | Forge | (Forge-owned) |
| `36_CONTEXT_FILE_DISCIPLINE` | Context File Discipline | Execution | Forge | (Forge-owned) |
| `37_SCHEDULING_DELEGATION` | Scheduling / Delegation | Execution | Forge | (Forge-owned) |
| `38_PERSISTENT_MEMORY` | Persistent Memory | Execution | Forge | (Forge-owned) |
| `39_INTERRUPT_MULTILINE_TUI` | Interrupt + Multiline TUI | Execution | Forge | (Forge-owned) |
| `40_SERVERLESS_HIBERNATION` | Serverless Hibernation | Execution | Forge | (Forge-owned) |
| `41_MULTI_PROVIDER_FAILOVER` | Multi-Provider Failover | Execution | Forge | (Forge-owned) |
| `50_HERMES_RISK_REGISTER` | Hermes Risk Register | Verification | Auditor | (Auditor-owned) |
| `51_EMBER_GAP_ANALYSIS` | Ember Gap Analysis | Verification | Auditor | (Auditor-owned) |
| `52_ANTIPATTERN_CATALOG` | Antipattern Catalog | Verification | Auditor | (Auditor-owned) |
| `53_CRASH_PROOFING_PATTERNS` | Crash-Proofing Patterns | Verification | Auditor | (Auditor-owned) |
| `54_SECURITY_REVIEW` | Security Review | Verification | Auditor | (Auditor-owned) |
| `55_INVARIANT_LIST` | Invariant List | Verification | Auditor | (Auditor-owned) |
| `56_TESTING_STRATEGY` | Testing Strategy | Verification | Auditor | (Auditor-owned) |
| `60_HERMES_VS_EMBER_CROSSWALK` | Hermes vs Ember Crosswalk | Synthesis | **Cartographer** | **draft** |
| `61_TRUE_NAME_REASSIGNMENT` | True Name Reassignment | Synthesis | **Cartographer** | **draft** |
| `62_DEPENDENCY_FLOW` | Dependency Flow | Synthesis | **Cartographer** | **draft** |
| `63_INTEGRATION_PATHS` | Integration Paths | Synthesis | **Cartographer** | **draft** |
| `64_MIGRATION_PLAN` | Migration Plan | Synthesis | **Cartographer** | **draft** |
| `65_SLICE_PLAN_REVISIONS` | Slice Plan Revisions | Synthesis | **Cartographer** | **draft** |
| `66_DECISION_RECORDS` | Decision Records | Synthesis | **Cartographer** | **draft** |
| `67_GLOSSARY_AND_INDEX` | Glossary and Index | Synthesis | **Cartographer** | **draft (this doc)** |
| `INDEX` | Codex Index | Meta | Scribe | (Scribe-owned) |
| `READING_ORDER` | Reading Order | Meta | Scribe | (Scribe-owned) |
| `MANIFEST` | Manifest | Meta | Scribe | already shipped |
| `SHARED_CONTEXT` | Shared Context | Meta | Scribe | already shipped |
| `CROSS_AGENT_NOTES` | Cross-agent Notes | Meta | any | as needed |
| `HERMES_REVISION` | Hermes Revision | Meta | Scribe | (Scribe-owned) |

## What This Means for Ember

The glossary is the **translation key**. Future contributors — operators, plugin authors, agent-developers using Ember as a base — will read either Hermes-style or Ember-style first, and the index in this doc lets them cross over.

**True Names affected:** all six get glossary entries; the two reserved names (Gjallarhorn, Vinátta) and two declined names (Hringja, Lærdómr) are documented with full etymology so they're discoverable even when they don't yet exist as code.

**Vows touched:**
- *Reinforced:* Vow of Open Knowledge — every term documented, every Hermes-Ember mapping traced.
- *Reinforced:* Vow of Public-Friendliness — the glossary makes the codex readable to a non-developer who is learning the field.

**Concrete next step:** the Scribe (Eirwyn Rúnblóm) will consolidate this glossary with the Skald's `02_NAMING_PARALLELS` and the Architect's `10_DOMAIN_MAP` to produce the final reader-facing `meta/INDEX.md`. This Cartographer doc is the master glossary; the Scribe's INDEX is its operator-facing distillation.

**Cross-references:**
- Every Codex doc references this glossary for term resolution.
- [[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]] is the structural counterpart; this doc is the lexical counterpart.
- [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] is the etymology source for Gjallarhorn, Hringja, Lærdómr, Vinátta.

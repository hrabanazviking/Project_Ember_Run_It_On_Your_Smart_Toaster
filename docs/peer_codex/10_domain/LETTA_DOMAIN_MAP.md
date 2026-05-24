---
codex_id: LETTA_DOMAIN_MAP
title: Letta Domain Map — The Memory-Server's Skeleton
role: Architect
layer: Domain
peer_targets: [Letta]
status: draft
peer_source_refs:
  - letta:letta/__init__.py
  - letta:letta/agent.py:1-100
  - letta:letta/agents/letta_agent_v3.py:1-220
  - letta:letta/services/agent_manager.py:1-200
  - letta:letta/services/block_manager.py:1-100
  - letta:letta/services/tool_executor/core_tool_executor.py:1-120
  - letta:letta/server/server.py:1-100
  - letta:letta/server/rest_api/app.py:1-100
  - letta:letta/server/rest_api/routers/v1/agents.py:1-80
  - letta:letta/orm/agent.py:1-100
  - letta:letta/orm/sqlalchemy_base.py:1-50
  - letta:letta/llm_api/llm_client_base.py
  - letta:letta/adapters/letta_llm_adapter.py
  - letta:compose.yaml
  - letta:alembic/versions/  (167 migrations)
ember_subsystem_targets: [Funi, Brunnr, Smiðja, Munnr]
hermes_codex_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_AGENT_CORE
  - 10_domain/19_BOUNDARY_LAW
cross_refs:
  - 10_domain/LETTA_MEMORY_ARCHITECTURE
  - 10_domain/LETTA_SERVER_CLIENT_SPLIT
  - 10_domain/CROSS_DOMAIN_TRIANGULATION
---

# Letta Domain Map
## The Memory-Server's Skeleton

*— Rúnhild Svartdóttir, Architect*

> *Letta is the saga of a memory that wanted a server around it. Where Hermes grew an agent and then added persistence, Letta grew a persistence and then added an agent. The bones grow opposite-handed from the same skull.*

Letta is roughly 247,000 lines of Python across 875 files. It is the largest of the three peer codebases by a factor of eight (smolagents) and the only one besides Hermes that is Python-native. Where Hermes has grown an *agent that happens to have state*, Letta has grown a *state engine that hosts agents*. The shape is opposite-handed: the orm and the services are the spine; the agent loop is a guest who arrives, performs, and leaves. To understand Letta you must understand this first, because every domain decision flows from it.

This doc maps Letta's eleven principal domains, draws the lines between them, names which are stable and which are migrating mid-stride (the V1/V2/V3 agent split is a live tectonic feature), and ends with what the bones mean for an Ember that must remain small.

---

## 1. The Eleven Domains of Letta

| # | Domain | Where it lives | What it owns | What it does NOT own |
|---|---|---|---|---|
| 1 | **Agent Implementations** | `letta/agents/` (10 files), `letta/agent.py` (1758 lines, legacy) | The *behavior* of an agent: step loop, tool dispatch, memory orchestration. V1 (legacy), V2 (current), V3 (current+), Voice variants, ephemeral, batch | Persistence (services own it), HTTP (server owns it), model HTTP (llm_api owns it) |
| 2 | **Services** | `letta/services/` (~40 manager modules; ~30k LOC) | Every persistent collaborator: agents, messages, blocks, archives, passages, tools, MCP, jobs, runs, providers, sandboxes, telemetry, summarizer, llm_router, lettuce, etc. | Pydantic schemas, transport, agent loop behavior |
| 3 | **ORM** | `letta/orm/` (~50 SQLAlchemy models) | Database-side truth: Agent, Block, Message, Passage, Archive, Conversation, Tool, Job, Run, Group, Identity, McpServer, ProviderModel, Step, etc. + `sqlalchemy_base.py` | Pydantic shapes (those are `schemas/`), service behavior |
| 4 | **Schemas** | `letta/schemas/` (~60 Pydantic models) | The wire-format truth: agent, block, memory, message, passage, tool, llm_config, embedding_config, run, group, mcp_server, providers, tool_rule, response_format, etc. | DB columns (those are ORM), agent behavior |
| 5 | **Server (REST + WS)** | `letta/server/server.py` (1904 lines, `SyncServer`), `letta/server/rest_api/` (FastAPI), `letta/server/ws_api/` (WebSocket) | The single process that owns all in-memory orchestration: `SyncServer` is the *one* service-aggregator; routers in `rest_api/routers/v1/` expose 34+ resource APIs; WS for streaming | Direct DB access (always through services), agent step internals |
| 6 | **LLM API Clients** | `letta/llm_api/` (15+ clients) | Per-provider HTTP clients: Anthropic, Azure, Baseten, Bedrock, ChatGPT-OAuth, DeepSeek, Fireworks, GoogleAI, GoogleVertex, Groq, MiniMax, Mistral, OpenAI, OpenAI-WS, SGLang-native, Together, XAI, ZAI | Provider profile metadata (schemas owns it), the loop's choice of which to call |
| 7 | **Adapters** | `letta/adapters/` (6 files) | The *adapter pattern* over llm_api clients — request adapter, stream adapter, sglang native adapter. Translates `(messages, tools)` → provider-shape → `(response, tool_calls)` | Network I/O (clients do it), step orchestration (agents do it) |
| 8 | **Tool Executors** | `letta/services/tool_executor/` (8 modules) | Where tools actually run: `core_tool_executor` (built-in memory tools), `composio`, `builtin`, `files`, `mcp`, `sandbox`. Plus `tool_execution_sandbox.py` for isolated runs | Tool *schemas* (schemas/tool.py), tool *registration* (tool_manager service) |
| 9 | **Functions / Function Sets** | `letta/functions/` + `letta/functions/function_sets/` (base, voice, multi_agent, files, builtin) | The Python *definitions* of MemGPT base functions (`send_message`, `conversation_search`, `core_memory_*`, `archival_memory_*`). The function-set system bundles these into agent presets | Tool dispatch (executors), agent behavior |
| 10 | **Prompts / Personas / Humans** | `letta/prompts/system_prompts/` (12 system prompts), `letta/personas/`, `letta/humans/`, `letta/templates/` | The *content* of system prompts. Letta-V1, MemGPT-chat, MemGPT-v2-chat, ReAct, sleeptime, voice, workflow. Personas and humans seed block contents at agent creation | Render-time block composition (memory.py + agent does that), block edit semantics |
| 11 | **CLI & Client** | `letta/cli/`, `letta/client/`, `letta/main.py` | Developer-facing surfaces. The CLI is light; the canonical surface is the REST API. Client wraps it | Server orchestration (server.py owns it), agent behavior |

Eleven. The same number as Hermes — not coincidentally; this is roughly how many bones an agent-with-persistence ends up with. But the *weight distribution* is utterly different. In Hermes the agent core is ~360 KB across `run_agent.py` + `agent/`. In Letta it is ~6,000 lines across `agents/`, with the *services* layer carrying triple the LOC. Letta is a service-shaped system. Hermes is an agent-shaped system. Same eleven bones, different center of gravity.

---

## 2. The Layered View

```
┌─────────────────────────────────────────────────────────────────────────┐
│  SURFACES                                                               │
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────────────────┐     │
│  │ REST API     │  │ WebSocket API  │  │ CLI / Python client      │     │
│  │ FastAPI      │  │ ws_api/server  │  │ letta/cli, letta/client  │     │
│  │ 34 routers   │  │ streaming      │  │                          │     │
│  └──────┬───────┘  └────────┬───────┘  └────────────┬─────────────┘     │
│         └─────────────┬─────┴───────────────────────┘                   │
└───────────────────────┼─────────────────────────────────────────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  SyncServer  (letta/server/server.py — 1904 lines)                      │
│  The single in-process orchestrator. Holds every service singleton.     │
│  Every router dependency-injects SyncServer; SyncServer dispatches.     │
└────┬────────────────────────────────────────────┬───────────────────────┘
     │                                            │
     ▼                                            ▼
┌──────────────────────────────┐    ┌────────────────────────────────────┐
│  AGENTS                      │    │  SERVICES (~40 managers)           │
│  letta_agent_v3 ⊃ v2 ⊃ v1    │    │  agent_manager.py (3599 lines)     │
│  base_agent + base_agent_v2  │    │  message_manager (1346)            │
│  voice_agent, ephemeral,     │    │  block_manager (1048) + git        │
│  letta_agent_batch           │    │  archive_manager (718)             │
│  agent_loop.py               │    │  passage_manager (1103)            │
│  → step(), stream(), build_  │    │  tool_manager (1452)               │
│    request()                 │    │  mcp_manager, mcp_server_manager   │
│                              │    │  run_manager, job_manager          │
│                              │    │  provider_manager, summarizer      │
│                              │    │  llm_router, conversation_manager  │
└────────────┬─────────────────┘    │  context_window_calculator         │
             │                      │  tool_executor/ (8 modules)        │
             ▼                      └─────────────┬──────────────────────┘
┌──────────────────────────────┐                  │
│  LLM ADAPTERS                │                  │
│  letta/adapters/             │                  │
│  letta_llm_request_adapter   │                  │
│  letta_llm_stream_adapter    │                  │
│  sglang_native_adapter       │                  │
└────────────┬─────────────────┘                  │
             ▼                                    ▼
┌──────────────────────────────┐    ┌────────────────────────────────────┐
│  LLM API CLIENTS             │    │  ORM (~50 SQLAlchemy models)       │
│  letta/llm_api/              │    │  letta/orm/                        │
│  anthropic, openai, gemini,  │    │  Agent, Block, Message, Passage,   │
│  bedrock, azure, deepseek,   │    │  Archive, Conversation, Tool, Job, │
│  groq, mistral, xai, zai,    │    │  Run, Group, Identity, MCPServer,  │
│  sglang, fireworks, together │    │  Step, ProviderModel               │
│  google_vertex, openai_ws,   │    │  sqlalchemy_base.py — deadlock     │
│  minimax, baseten            │    │   retry, async session, FK errors  │
└──────────────────────────────┘    └─────────────┬──────────────────────┘
                                                  ▼
                                    ┌────────────────────────────────────┐
                                    │  POSTGRES + pgvector (default)     │
                                    │  or SQLite + sqlite_vec            │
                                    │  167 alembic migrations            │
                                    │  init.sql + sandbox/               │
                                    └────────────────────────────────────┘
```

Read top-down. The traffic shape is: surface → `SyncServer` → (agent OR service) → ORM. The agent layer is *one* path through the orchestrator, not the orchestrator itself. This is the structural inversion of Hermes.

---

## 3. The Live Tectonic — V1, V2, V3

Letta is currently between two architectures of "what an agent is." The artifacts:

| File | Lines | Role |
|---|---|---|
| `letta/agent.py` | 1758 | **Legacy V1.** Synchronous, monolithic `Agent` class — the original MemGPT shape |
| `letta/agents/base_agent.py` | 195 | V1 abstract base — `step()`, `step_stream()`, `_rebuild_memory_async` |
| `letta/agents/base_agent_v2.py` | 105 | V2 abstract base — `build_request()`, `step()`, `stream()` |
| `letta/agents/letta_agent.py` | 1983 | V1 concrete — current path for legacy callers |
| `letta/agents/letta_agent_v2.py` | 1487 | V2 concrete — async, adapter-based, stream-aware |
| `letta/agents/letta_agent_v3.py` | 2134 | V3 concrete — extends V2, adds new compaction / approval logic |
| `letta/agents/agent_loop.py` | (small) | A dispatcher that picks the right concrete agent class for an agent state |
| `letta/agents/voice_agent.py` | 525 | Voice variant of V1 |
| `letta/agents/letta_agent_batch.py` | (large) | Batch-mode agent for offline runs |

The router at `letta/server/rest_api/routers/v1/agents.py:18-21` imports *all four* — `AgentLoop`, `BaseAgentV2`, `LettaAgent`, `LettaAgentV3` — and dispatches per request. The conversation router (`conversations.py`) is the new path; `messages.py` is the old. The V1 path is being *kept alive* for OpenAI-compatible endpoints and existing integrations.

This is a Hermes-pattern: a domain in the middle of progressive extraction (compare Hermes `agent/__init__.py:1-7` — "Agent internals — extracted modules from run_agent.py"). The difference is that Hermes is extracting *within* a single agent shape; Letta is migrating *between* shapes. The structural cost is doubled imports, the structural gain is that V3 can break invariants V1 promised without breaking V1 itself.

**For Ember:** when slice 2 needs to evolve the agent shape, do not version the class. *Version the schema.* `AgentState` is the data; the class is the executor. Hermes does this implicitly (one `AIAgent`, many adapters). Letta now does it explicitly (one `AgentState`, three executors). The latter is the more conservative choice but requires N implementations of every behavior.

---

## 4. Domain-by-Domain Lines of Responsibility

### 4.1 Agents (`letta/agents/`)

**Owns:** the behavior of *stepping* — taking an `AgentState` from the DB, building a request, calling an adapter, parsing tool calls, executing them through the tool_executor, persisting messages back via `MessageManager`, returning a `LettaResponse`. `letta_agent_v3.py:222` is the canonical `step()`; `_step()` at line 895 is the inner-loop body.

**Does not own:** anything that survives the process. Persistence is *exclusively* through managers (`message_manager`, `agent_manager`, `block_manager`). The agent class is stateless except for its in-memory caches.

**Key boundary:** `letta_agent_v2.py` constructor takes managers as injected dependencies (`agent_manager`, `message_manager`, `block_manager`, `passage_manager`, etc.). The agent never instantiates a manager. This is dependency-injection done correctly — and the *opposite* of Hermes's `_ra()` lazy backreference. Cite `[[hermes_codex/10_domain/19_BOUNDARY_LAW]]` §2.1 — Letta solves the problem Hermes leaks.

### 4.2 Services (`letta/services/`)

**Owns:** every persistent operation. The pattern is one manager per ORM aggregate: `AgentManager` owns Agent CRUD, `MessageManager` owns Message CRUD + FTS, `BlockManager` owns Block CRUD + version history (`block_manager_git.py` adds git-style branching!), `ArchiveManager` owns archival memory (vector store wrapper), `PassageManager` owns passages (the archival memory unit). Plus the *non-aggregate* managers: `SummarizerService`, `LLMRouter`, `ConversationManager`, `ToolExecutionManager`, `WebhookService`.

**Does not own:** transport (FastAPI/WS owns it), agent step behavior (agents own it), schema validation (schemas own it).

**Key boundary:** `AgentManager` is 3599 lines. This is a *category* like Hermes's `run_agent.py` — a single domain whose internal extraction is incomplete. The discipline that holds it together is the `__init__` pattern: every method takes an `actor: User` argument, every method uses async SQLAlchemy through `sqlalchemy_base.SqlalchemyBase`. The size is a *boundary leak* (one class is doing too much) but the *contract* (actor-scoped, async, ORM-bound) is uniform.

### 4.3 ORM (`letta/orm/`)

**Owns:** the schema of the database. Each model inherits from `SqlalchemyBase` (defined in `sqlalchemy_base.py:1-50`), which provides organization-scoping, soft-delete, async `to_pydantic`, and uniform deadlock-retry semantics. The `__pydantic_model__` class attribute (see `orm/agent.py:46`) is the canonical link between ORM row and Pydantic schema.

**Does not own:** business logic (services own it), wire-format (schemas own it).

**Key boundary:** the ORM is *blind* to who's calling. The service layer above injects `actor: User` and the ORM enforces organization-scoping at query time via `SqlalchemyBase`. This is the **multi-tenant correctness boundary** — and the reason Letta can be a hosted SaaS. Ember does not need this (single-user), but the *pattern* (actor at every query) is useful: any future Brunnr multi-user mode would adopt it.

### 4.4 Schemas (`letta/schemas/`)

**Owns:** the wire-format Pydantic models. ~60 files. Every public surface (REST, SDK, CLI) consumes/produces these.

**Does not own:** persistence, validation beyond Pydantic field validators.

**Key boundary:** the schemas are *the API*. Backwards compatibility is enforced at this layer with explicit `deprecated=True` fields (see `schemas/block.py:84-93`). When a field is renamed, both old and new live for a release. This is **API contract discipline** — and the reason Letta survives 167 alembic migrations without breaking its SDK.

### 4.5 Server (`letta/server/`)

**Owns:** the running process. `SyncServer` (1904 lines) is the singleton that holds every manager instance. FastAPI routers in `rest_api/routers/v1/` (34 routers) wire each endpoint to `SyncServer` via FastAPI dependency injection. WebSocket protocol in `ws_api/` handles streaming.

**Does not own:** agent behavior (agents do), DB schema (ORM does), tool semantics (executors do).

**Key boundary:** **FastAPI dependency injection is the discovery surface.** Every router declares `letta_server: SyncServer = Depends(get_letta_server)` and gets the running instance. This is *one* discovery path (compare Hermes's three: general, memory, model-providers — `[[hermes_codex/10_domain/19_BOUNDARY_LAW]]` §2.2). Letta has *not* had the plugin-discovery leak. Why? Because Letta has no first-class plugin system. Tools come from the DB (via `ToolManager`); model providers come from the DB (via `ProviderManager`). The trade: less pluggability, but a cleaner boundary.

### 4.6 LLM API + Adapters (`letta/llm_api/`, `letta/adapters/`)

**Owns:** the per-provider transport (clients) and the per-shape translation (adapters). The split is: `llm_api/anthropic_client.py` knows the Anthropic HTTP shape; `adapters/letta_llm_request_adapter.py` knows the *Letta-internal* shape and translates between the two.

**Does not own:** which provider to call (the LLM router picks), what messages to send (the agent builds), how to interpret the result for memory updates (agent + tool executor).

**Key boundary:** the adapter is *thin*. It only translates. The Hermes equivalent is the model-adapter sprawl in `agent/` (`anthropic_adapter.py`, `bedrock_adapter.py`, etc.) — Hermes leaks because there's no Adapter ABC; Letta holds because the adapter shape is forced by the request/stream interfaces in `base_agent_v2.py:36-100`. This is the boundary Hermes 2.6 leaks; Letta closes it.

### 4.7 Tool Executors (`letta/services/tool_executor/`)

**Owns:** the runtime of tools. `core_tool_executor.py` (1068 lines) handles MemGPT's built-in memory tools (`core_memory_append`, `core_memory_replace`, `memory_replace`, `memory_insert`, `memory_apply_patch`, `memory_str_replace`, `memory_str_insert`, `memory_rethink`, `memory_finish_edits`, `archival_memory_insert`, `archival_memory_search`, `conversation_search`, `send_message`). `composio_tool_executor.py` handles Composio (a third-party tool marketplace). `mcp_tool_executor.py` handles MCP-server-provided tools. `sandbox_tool_executor.py` handles user-provided Python tools in an isolated subprocess. `builtin_tool_executor.py` handles a small set of *non-memory* built-ins (web search, etc.). `files_tool_executor.py` handles attached-file operations.

**Does not own:** registration (`tool_manager` does), the schemas (`schemas/tool.py`), or the agent's *decision* to call a tool (the loop does).

**Key boundary:** **one ABC, multiple executors per concern.** `ToolExecutor` (in `tool_executor_base.py`) defines `async def execute(function_name, function_args, tool, actor, agent_state, sandbox_config, sandbox_env_vars) -> ToolExecutionResult`. Every concrete executor implements this. The Hermes-comparable contract is `tools/environments/base.py:1-99` (`BaseEnvironment`), but Hermes splits *backends* (docker/ssh/local) while Letta splits *kinds* (memory/mcp/composio/sandbox). Both are correct; both honor the "data + enforcer + escape valve" frame from `[[hermes_codex/10_domain/19_BOUNDARY_LAW]]`.

### 4.8 Functions (`letta/functions/`)

**Owns:** the *Python source* of MemGPT base functions. The function-sets system bundles them into agent presets (`function_sets/base.py`, `voice.py`, `multi_agent.py`, `files.py`, `builtin.py`).

**Does not own:** execution (executors do), agent-callable schemas (those are generated from signatures via `schema_generator.py`).

**Key boundary:** functions are *just Python*. They get JSON-schema-generated at registration time. The pattern Hermes shares (tools declared via `registry.register()`), but Letta enforces that *every* function comes from a known function set — there is no "user-written tool" path through the function-set system; user tools go through the *Tool* schema and through `tool_manager` registration. This separation (built-in vs user) is sharper than Hermes's; Hermes treats them uniformly.

### 4.9 Prompts / Personas / Humans

**Owns:** the *content* loaded into the system prompt and into the initial memory blocks. `letta/prompts/system_prompts/` has 12 distinct system prompts — one for each agent variant. `personas/` and `humans/` are libraries of seed content for the `persona` and `human` core memory blocks.

**Key boundary:** **content is data, not code.** The agent class loads the right file at instantiation. This is the *opposite* of Hermes, where the system prompt is assembled imperatively by `prompt_builder.py` (1465 lines). Letta's choice gains transparency (you can read the prompt as a file); Hermes's gains composability (you can splice tools, skills, memories together with conditionals). Both are valid; Letta's is simpler. Ember has been closer to Letta's model — the system prompt in slice 2 is a file, not a builder.

### 4.10 CLI & Client

**Owns:** developer-facing entry points. Light layer; the REST API is canonical.

**Does not own:** any orchestration. The CLI calls the server; the Python client calls the server. There is no "local Letta" — the server is always the destination.

This is the *single most important boundary* in Letta. See `[[10_domain/LETTA_SERVER_CLIENT_SPLIT]]`.

### 4.11 Migrations (`alembic/`)

**Owns:** schema evolution history. 167 numbered migrations.

**Key boundary:** migrations are **additive and reversible**. The discipline Hermes enforces at `hermes_state.py:36` (`SCHEMA_VERSION = 12`) at one-twelfth the scale. This is the rule Ember slice 2 already follows — but Letta is the more rigorous example because the schema is wider (50+ tables vs Hermes's ~5).

---

## 5. The Letta ASCII Domain Map

```
                    ┌────────────────────────────────────┐
                    │  CLIENTS (browser SDK / Python /   │
                    │  curl / CLI / IDE)                 │
                    └─────────────┬──────────────────────┘
                                  │  HTTP/WS
                                  ▼
                    ┌────────────────────────────────────┐
                    │  REST API + WS  (FastAPI + WS)     │
                    │  34 routers under /v1/             │
                    │  auth/middleware/streaming         │
                    └─────────────┬──────────────────────┘
                                  ▼
                    ┌────────────────────────────────────┐
                    │  SyncServer  (the single host)     │
                    │  Holds every manager singleton     │
                    └──┬────────┬────────────────────────┘
                       │        │
            ┌──────────┘        └─────────────────────┐
            ▼                                         ▼
┌──────────────────────────────┐         ┌──────────────────────────────┐
│  AGENTS  (V1 / V2 / V3)      │         │  SERVICES (~40 managers)     │
│  letta_agent_v3 ⊃ v2         │         │  agent_manager, message,     │
│  base_agent_v2.step/stream   │         │  block, archive, passage,    │
│  letta_agent_batch (offline) │         │  tool, run, job, group,      │
│  voice_agent                 │         │  summarizer, mcp, provider   │
│  agent_loop dispatcher       │         │  llm_router, conversation,   │
└────────┬─────────────────────┘         │  webhook, telemetry          │
         │                               └──────┬───────────────────────┘
         ▼                                      │
┌──────────────────────────────┐                │
│  ADAPTERS                    │                │
│  letta_llm_request_adapter   │                │
│  letta_llm_stream_adapter    │                │
│  sglang_native_adapter       │                │
└────────┬─────────────────────┘                │
         ▼                                      ▼
┌──────────────────────────────┐    ┌────────────────────────────────────┐
│  LLM API CLIENTS             │    │  TOOL EXECUTORS                    │
│  per-provider HTTP           │    │  core (memgpt mem tools),          │
│  18+ files                   │    │  builtin, mcp, composio, files,    │
│                              │    │  sandbox (isolated Python)         │
└──────────────────────────────┘    └────────────┬───────────────────────┘
                                                 │
                                                 ▼
                                    ┌────────────────────────────────────┐
                                    │  ORM (~50 models, SqlalchemyBase)  │
                                    │  Agent, Block, Message, Passage,   │
                                    │  Archive, Tool, Run, Job, …        │
                                    └────────────┬───────────────────────┘
                                                 ▼
                                    ┌────────────────────────────────────┐
                                    │  POSTGRES + pgvector  (canonical)  │
                                    │  or SQLite + sqlite_vec            │
                                    │  + Alembic (167 migrations)        │
                                    └────────────────────────────────────┘

Cross-cutting:
  • Schemas (~60 Pydantic models) — read by every layer
  • Prompts/Personas/Humans (file-based content)
  • Constants (token limits, line-number prefixes, etc.)
  • OpenTelemetry tracing decorators on every public service method
```

---

## 6. Cross-Cutting Concerns

Four cross-cutting concerns deserve separate naming because they touch *every* domain:

1. **Multi-tenancy.** `actor: User` is the first argument on virtually every service method. `SqlalchemyBase` enforces org-scoping. This is Letta's *non-negotiable boundary*. Ember does not need it (single-user) but the *pattern* — actor-at-every-query — is the cleanest way to *prevent* leaking data between users if Ember ever multi-tenants. (Cross-walk to `[[hermes_codex/10_domain/19_BOUNDARY_LAW]]` §1.7 — Hermes profile isolation is the single-user version of the same idea.)

2. **Async-everything.** Every manager method is `async def`. SQLAlchemy is the async-engine variant. The agent uses `asyncio.gather` heavily (e.g., parallel tool execution). Hermes is sync-by-default with async where required; Letta is async-by-default. Ember slice 2 is mostly sync — *consider* if Brunnr's bulk operations would benefit from async.

3. **OpenTelemetry.** `letta/otel/` provides `@trace_method` decorators applied to every important service method. This is observability discipline at scale. Hermes has `agent/trajectory.py` for telemetry but does not have OTEL spans. Letta's spans are how you debug a 40-service orchestration; Ember will not need this at slice 2 scale but should leave the seam (cite [[hermes_codex/30_execution/30_AGENT_LOOP]] for the trajectory parallel).

4. **Schema migrations.** 167 alembic migrations. The discipline: every PR that changes ORM ships a numbered migration. Hermes has 12; Letta has 14x as many. Both work; both never destroy data; both are additive. Ember has the discipline already implicit; cite Letta as the production case study.

---

## 7. Letta Domain Decisions Worth Stealing

1. **Memory as data, edits as tools.** The single most influential decision Letta makes is that *the agent edits its own memory through tool calls* — `core_memory_append`, `memory_replace`, `memory_apply_patch`. The system prompt advertises these tools; the loop runs them; the result is persisted to `blocks` table. This is the MemGPT insight made architectural. See `[[10_domain/LETTA_MEMORY_ARCHITECTURE]]` for the full unpacking. **For Ember:** Brunnr's Honest Memory Vow points the same direction. Letta is the production case.

2. **Manager-per-aggregate.** Hermes mixes aggregate logic with orchestration (`hermes_state.py` is 140 KB doing sessions+messages+FTS). Letta splits each aggregate into its own manager (`MessageManager`, `BlockManager`, etc.). Cleaner; each manager is independently testable; the total LOC is higher but the cognitive load per file is lower.

3. **Pydantic-as-contract.** Every public surface accepts/returns Pydantic. The schema *is* the API. Letta's SDK can be regenerated from `fern/` because the contract is rigorous. Ember already follows this (slice 2 uses Pydantic); Letta is the model for stricter use.

4. **Tool-rules ORM column.** `Agent.tool_rules` (ORM `agent.py:80`) is a JSON column of `ToolRule` constraints. The agent step can *enforce* "tool X must run before tool Y" rules at planning time. Hermes does not have this; smolagents does not have this. **For Ember:** Listir/Verkfæri could profit from an explicit rules layer; see `[[10_domain/CROSS_BOUNDARY_LAW_V2]]`.

5. **`ProviderModel` is a row.** Providers are in the DB. New providers are added by inserting a row. The provider profile shape (`schemas/provider_model.py`) is the contract. Hermes does this with files in `providers/`; both work, Letta's is more dynamic but harder to audit. Ember should stay on Hermes's side here (files, not rows).

## 8. Letta Domain Decisions Worth Refusing

1. **Server-first deployment.** Letta cannot run "in the agent's process" — it requires a postgres container plus a server container plus optional clickhouse for traces. For Ember (Pi-first, no-network-required), this is a structural mismatch. See `[[10_domain/LETTA_SERVER_CLIENT_SPLIT]]`.

2. **40 managers.** The manager-per-aggregate is good; *40* of them is exhausting. Many are thin wrappers around CRUD. Ember should follow the *pattern* but resist the *count* — combine managers when the aggregate is small (e.g., one `BrunnrManager` for blocks+passages+archives, not three).

3. **Three concurrent agent versions.** V1, V2, V3 in the same repo is a tax. Letta is mid-migration; Ember should *never* be in this state. Adopt a one-shape rule from day one.

4. **Composio integration as a domain.** Composio is a tool marketplace; Letta has a dedicated executor for it. Ember has the **Vow of Open Knowledge** and the **Vow of Smallness** — third-party marketplaces are a refusal.

5. **Clickhouse for OTEL traces.** Letta optionally writes to clickhouse. For Ember, this is over-engineering at every slice.

---

## What This Means for Ember

The domain map confirms Letta is the **state-engine sibling** to Ember's agent-engine. The bones overlap; the weight distribution is the inversion.

**Affected True Names:**
- **Brunnr** (Well/storage) — Letta's services+ORM is the largest single influence here
- **Smiðja** (Forge/ingest) — Letta's passage_manager + archive_manager + source ingest is a fully-formed version of Smiðja
- **Munnr** (Mouth/CLI) — Letta's CLI is a thin client; Munnr can be similarly thin if a separate process runs the heavy lifting
- **Funi** (Flame/runtime) — Letta's adapter+client pattern is a direct lift for Funi when multi-provider arrives

### Concrete proposals for Ember's domain map

1. **Adopt "manager-per-aggregate" inside Brunnr, but cap the count.** `BrunnrBlockManager`, `BrunnrPassageManager`, `BrunnrArchiveManager` — these are the three obvious aggregates. Do not balloon to 40 like Letta. Two-to-five managers, each <1500 lines.

2. **Adopt the adapter-pattern for Funi.** When Funi gains a second provider (probably OpenAI-compatible / Anthropic), copy Letta's split: `funi_adapter.py` translates Ember-internal `(messages, tools)` → provider-shape; `funi_clients/*.py` does HTTP. Cite `letta/adapters/letta_llm_request_adapter.py` and `letta/llm_api/anthropic_client.py` as the reference pair.

3. **Adopt Pydantic-as-contract more aggressively.** Slice 2 already uses Pydantic; lift the discipline of *every* public surface returning a Pydantic model — no bare dicts. Cite `letta/schemas/letta_response.py` as the model.

4. **Adopt Alembic-style migrations for Brunnr's SQLite schema.** Hermes uses ad-hoc schema-version-check (`hermes_state.py:36`); Letta uses Alembic. Ember slice 2 has `sqlite_vec` schema and pgvector schema. Adopt Alembic now; it costs ~50 lines of setup and prevents the "I changed a CREATE TABLE without a migration" failure mode.

5. **Refuse the SyncServer pattern unless multi-process becomes required.** Ember's process *is* the agent. A `SyncServer`-like aggregator is overkill when there is one agent per process. The day Ember has a Pi-side daemon and a desktop-side UI, revisit; until then, keep Hjarta + Munnr as the orchestrator. Cite `[[10_domain/LETTA_SERVER_CLIENT_SPLIT]]` for the full argument.

6. **Reinforce the Vow of Modular Authorship by letting Brunnr be a *replaceable* manager set.** Letta's `BlockManager` and `BlockManagerGit` are two implementations of the same boundary. Brunnr should support the same: a default SQLite-backed manager, an optional pgvector-backed manager, a future memory-only manager for tests. The Vow already says this; cite Letta as the production example.

### Vows touched

- **Vow of Pluggable Storage** — Letta's manager+ORM pattern is the strongest production case for it. Reinforced.
- **Vow of Honest Memory** — Letta's "memory edits are tool calls, not implicit curator actions" is the cleanest implementation of this Vow we have seen. Reinforced and elevated.
- **Vow of Smallness** — Letta is the *anti-evidence* for this. 247k LOC, 40 managers, 167 migrations. Ember must *not* port Letta wholesale; the saga shape is what we keep, the count is what we refuse.
- **Vow of Graceful Offline** — Letta has *none* of this. The server requires postgres; no fallback. Ember cannot inherit this posture.

### Hermes Codex docs reinforced or contradicted

- **Reinforces `[[hermes_codex/10_domain/19_BOUNDARY_LAW]]` §1.2** — Letta's `MemoryProvider` analogue is the `BlockManager`/`ArchiveManager`/`PassageManager` triad; the single-integration-point rule holds.
- **Contradicts `[[hermes_codex/10_domain/10_DOMAIN_MAP]]` "Eleven Domains" implication that this count is the natural shape** — Letta has its own eleven and they cluster very differently. The *number* is suggestive; the *clustering* is what each project shapes for itself.
- **Reinforces `[[hermes_codex/10_domain/19_BOUNDARY_LAW]]` §2.1 (the `_ra()` leak)** — Letta does it the right way (dependency injection). Cite as the prevention pattern.
- **Reinforces `[[hermes_codex/10_domain/19_BOUNDARY_LAW]]` §3.5 (migration discipline)** — Letta's 167 alembic migrations are the upper-bound production case.

---

## Closing — The Architect's Last Word

Letta's bones are the bones of a system that wanted to *survive a restart*. Every decision (multi-tenant, async, ORM-everything, manager-per-aggregate, alembic-numbered, OTEL-traced, schema-versioned) optimizes for a process that can crash and resume. Ember, in slice 2, does not have this requirement at full force — but slice 4 or 5 may. When Ember does need it, this is the map to follow.

But Letta is also the *anti-evidence* for Ember's first Vow. Letta is the seventh circle of "a system that knows what it owns and owns too much." 247,000 lines. 167 migrations. 40 managers. Beautiful — and a sustained refusal of smallness.

Take the bones. *Refuse the count.* The boundary discipline, the manager-per-aggregate pattern, the adapter split, the actor-at-every-query, the schemas-as-API — these are the seven bones Ember keeps. The 40 managers and the 167 migrations and the V1/V2/V3 tectonic — these are the eight bones Ember leaves at the door.

— *Rúnhild Svartdóttir, Architect*

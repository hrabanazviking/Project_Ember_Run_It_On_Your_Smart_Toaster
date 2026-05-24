---
codex_id: 10_DOMAIN_MAP
title: The Domain Map of Hermes — Bones, Joints, and the Lines Between Them
role: Architect
layer: Domain
status: draft
hermes_source_refs:
  - AGENTS.md:1-100
  - pyproject.toml:1-220
  - run_agent.py:1-200
  - hermes_state.py:1-200
  - hermes_constants.py:1-200
  - agent/__init__.py:1-7
  - gateway/__init__.py:1-36
  - tui_gateway/server.py:1-100
  - tools/registry.py:1-120
  - providers/__init__.py:1-100
  - plugins/__init__.py:1-36
  - cron/__init__.py
  - acp_adapter/__init__.py
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 10_domain/11_AGENT_CORE
  - 10_domain/12_SKILLS_PROCEDURAL_MEMORY
  - 10_domain/13_TOOLS_SUBSYSTEM
  - 10_domain/14_GATEWAY_MULTI_PLATFORM
  - 10_domain/15_PROVIDERS_MULTI_MODEL
  - 10_domain/16_TUI_GATEWAY_BACKENDS
  - 10_domain/17_PLUGINS_EXTENSIBILITY
  - 10_domain/18_HERMES_CLI
  - 10_domain/19_BOUNDARY_LAW
  - 60_synthesis/60_HERMES_VS_EMBER_CROSSWALK
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
---

# The Domain Map of Hermes
## Bones, Joints, and the Lines Between Them

*— Rúnhild Svartdóttir, Architect*

> *A system without a domain map is a hoard, not a hall. You may have all the gold in the kingdom, but if no one can tell the gold from the slag from the bones, you have built only a cave.*

Hermes is a system with thirty-one top-level directories and seven monster files at the root, weighing roughly two megabytes of Python before the skills and the assets are counted. To know it, you must see its skeleton — not the marketing pose, the actual articulation: which bone bears which weight, where the joints flex, where the calcified shortcuts will crack. This doc is that skeleton. The deep-dive bones get their own docs (`[[10_domain/11_AGENT_CORE]]` through `[[10_domain/18_HERMES_CLI]]`); here I show you the shape of the whole.

---

## 1. The Eleven Domains of Hermes

A *domain* in my reading of Hermes is a region of the codebase where one concept rules: where the imports go inward, the exports are stable, and the file naming is consistent with one mental model. Hermes has eleven domains. Most of them are directories; three of them are root-level files that *should* be directories but aren't yet.

| # | Domain | Where it lives | What it owns | What it does NOT own |
|---|---|---|---|---|
| 1 | **Agent Core** | `agent/` (80+ modules) + `run_agent.py` (180 KB) | Conversation loop, context engine, memory manager, prompt builder, model adapters, tool dispatch | UI rendering, transport sockets, skill content |
| 2 | **Tools** | `tools/` (60+ files) + `toolsets.py` + `toolset_distributions.py` | The 40+ atomic capabilities (terminal, browser, file, memory, skills, kanban, etc.), registry, dispatch shape | Execution backends (those are `tools/environments/`), provider auth |
| 3 | **Tool Environments** | `tools/environments/` (Docker, SSH, Modal, Daytona, Singularity, Vercel, local) | Spawn-per-call execution, sandbox lifecycle, file sync, persistent snapshot | Tool semantics (those are owned by `tools/*.py`) |
| 4 | **Skills** | `skills/` + `optional-skills/` (~25 categories) + `tools/skills_*.py` | Procedural-memory documents (SKILL.md), skill discovery, lifecycle, curator, sync with the Skills Hub | Tool implementations, agent state |
| 5 | **Gateway** | `gateway/` (24 modules, 30+ platform adapters) | Multi-platform messaging — Telegram, Discord, Slack, WhatsApp, Signal, Matrix, etc.; session routing; delivery; mirror | Agent loop, model selection |
| 6 | **TUI Gateway** | `tui_gateway/` + `ui-tui/` (Ink/React) + `hermes_cli/proxy/` | Headless agent backend behind a TypeScript Ink TUI, JSON-RPC over stdio | Terminal rendering (Ink does that), tool implementations |
| 7 | **CLI** | `hermes_cli/` (90+ modules) + `cli.py` (662 KB) | Slash commands, setup wizard, doctor, profile management, kanban CLI, voice, banner, theme/skin | Agent core, model providers |
| 8 | **Providers** | `providers/` + `plugins/model-providers/` (30+) + the model adapters in `agent/` | Model-provider profiles (auth, endpoints, quirks), credential pool, model catalogs, rate-limit guards | Conversation logic, tool dispatch |
| 9 | **Plugins** | `plugins/` (16+ trees) + `hermes_cli/plugins.py` | The pluggable surface: memory backends, context engines, image generators, observability, kanban dashboard, achievements, browser extras, messaging platforms | Core agent loop; plugins are forbidden to touch it (see §7) |
| 10 | **Session State** | `hermes_state.py` (140 KB) + `~/.hermes/state.db` + `cron/` + `acp_adapter/` + `acp_registry/` | SQLite session DB (sessions, messages, FTS5 search), cron jobs, ACP server (Agent Communication Protocol) | Conversation logic, model state |
| 11 | **Bootstrap & Constants** | `hermes_bootstrap.py` + `hermes_constants.py` + `hermes_logging.py` + `hermes_time.py` + root utilities | Process bootstrap (UTF-8 stdio on Windows), profile-aware home resolution, time zones, logging | Anything domain-specific |

Eleven. Not three or four; not fifty. The number matters because each domain *is* a Vow-of-Boundary line. When code crosses a line without traversing the proper interface, that is where the saga breaks. Hermes has crossed several of those lines in its growth — we mark those in `[[10_domain/19_BOUNDARY_LAW]]`.

---

## 2. The Layered View

If the domain table is the bone count, the layered view is the spine. Hermes stacks from infrastructure at the bottom to user surface at the top:

```
┌─────────────────────────────────────────────────────────────────┐
│  SURFACES                                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐    │
│  │ CLI      │  │ TUI (Ink)│  │ Gateway  │  │ ACP (Zed/etc) │    │
│  │ cli.py   │  │ ui-tui/  │  │ gateway/ │  │ acp_adapter/  │    │
│  │ 662 KB   │  │ tui_gw/  │  │ 30+ adps │  │               │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬──────────┘    │
│       └────────────┬┴─────────────┴──────┬──────┘               │
│                    │                     │                      │
└────────────────────┼─────────────────────┼──────────────────────┘
                     │                     │
┌────────────────────┴─────────────────────┴──────────────────────┐
│  AGENT CORE                                                     │
│  run_agent.py (180 KB) ── conversation_loop ── context_engine   │
│  prompt_builder ── memory_manager ── credential_pool            │
│  tool_executor ── error_classifier ── retry_utils               │
│  model adapters: anthropic, gemini, bedrock, codex, copilot,    │
│                  lmstudio, moonshot, openai, ollama, ...        │
└─────────────────┬─────────────────────────┬─────────────────────┘
                  │                         │
┌─────────────────┴────────┐  ┌─────────────┴─────────────────────┐
│  TOOLS + ENVIRONMENTS    │  │  PROVIDERS + PLUGINS              │
│  tools/registry.py       │  │  providers/__init__.py            │
│  60+ tool implementations│  │  plugins/model-providers/* (30+)  │
│  tools/environments/     │  │  plugins/memory/* (9+)            │
│   ├ local                │  │  plugins/context_engine/*         │
│   ├ docker               │  │  plugins/image_gen/* (3+)         │
│   ├ ssh                  │  │  plugins/observability/*          │
│   ├ modal                │  │  plugins/web/* (8+)               │
│   ├ daytona              │  │  plugins/browser/* (3+)           │
│   ├ singularity          │  │  plugins/platforms/* (5+)         │
│   └ vercel_sandbox       │  │  plugins/spotify, kanban,         │
│                          │  │   teams_pipeline, disk-cleanup    │
└──────────────────────────┘  └───────────────────────────────────┘
                  │                         │
┌─────────────────┴─────────────────────────┴─────────────────────┐
│  PERSISTENCE + IDENTITY                                         │
│  hermes_state.py (140 KB) ── state.db (SQLite + FTS5)           │
│  ~/.hermes/  (profile-aware via hermes_constants.get_hermes_home)│
│  cron/ (scheduler.py + jobs.py)                                 │
│  ~/.hermes/skills/.usage.json (curator telemetry)               │
│  acp_registry/ (agent.json — capability advertisement)          │
└─────────────────────────────────────────────────────────────────┘
                  │
┌─────────────────┴───────────────────────────────────────────────┐
│  BOOTSTRAP                                                      │
│  hermes_bootstrap.py — UTF-8 stdio on Windows; no-op on POSIX   │
│  hermes_constants.py — get_hermes_home(), profile resolution    │
│  hermes_logging.py   — agent.log / errors.log / gateway.log     │
└─────────────────────────────────────────────────────────────────┘
```

Read it bottom-up to understand provenance; top-down to understand traffic. The two diagonals tell you Hermes's character: surfaces fan out, but everything funnels through the Agent Core. There is *one* agent loop and many ways to drive it. That is the architectural decision Hermes most consistently honors.

---

## 3. The Top-of-Tree Files — Why They're Big

Five files at the repo root deserve to be called out, because in any other project they would be packages. In Hermes they have stayed flat — partly for historical reasons (these are the original modules), partly because they are seam-of-truth for tests that import them by name (`from run_agent import AIAgent`).

| File | Size | Role | Should it be a package? |
|---|---|---|---|
| `cli.py` | 662 KB | `HermesCLI` class (starts at `cli.py:2602`), 60+ top-level functions, slash-command dispatch entry | **Yes**, urgently — see `[[10_domain/18_HERMES_CLI]]` |
| `run_agent.py` | 180 KB | `AIAgent` class — orchestrator; ~60-arg constructor; many call sites depend on `run_agent.handle_function_call` and `run_agent.OpenAI` being patchable | Partially extracted — `agent/conversation_loop.py` is now the real loop body |
| `hermes_state.py` | 140 KB | `SessionDB` SQLite store with FTS5; one of the few self-contained domain modules at root | Could move to `state/`, but the root location is stable and tested |
| `trajectory_compressor.py` | 65 KB | Batch training-data pipeline (RL trajectories) | Separate concern — Ember will likely not need this |
| `batch_runner.py` | 57 KB | Parallel batch execution | Separate concern; not on the hot path |
| `toolsets.py` | 29 KB | The `TOOLSETS` dict and helpers | Already adequately scoped |
| `model_tools.py` | 40 KB | `get_tool_definitions()`, `handle_function_call()`, plugin discovery side-effect | Could split, but is the canonical dispatch surface |
| `mcp_serve.py` | 31 KB | MCP server entry — Hermes-as-MCP-server | Could move to `mcp/`; standalone enough not to | 

Hermes's growth strategy with this layer has been *progressive extraction*: `agent/__init__.py:1-7` says it plainly — *"Agent internals — extracted modules from run_agent.py."* The conversation loop, prompt builder, memory manager, error classifier, retry utilities, and twenty other pieces were once inside `run_agent.py` and now live as importable modules. `cli.py` is the next obvious candidate. Hermes has the discipline to extract; it lacks the schedule to finish.

---

## 4. Domain-by-Domain Lines of Responsibility

### 4.1 Agent Core (`agent/` + `run_agent.py`)

**Owns:** the single loop that takes a user message and produces an assistant message. Specifically: system-prompt assembly (`agent/prompt_builder.py`, 1465 lines), conversation iteration (`agent/conversation_loop.py`, 4094 lines), tool dispatch (`agent/tool_executor.py`, `agent/tool_dispatch_helpers.py`), context compression (`agent/context_engine.py` + `agent/context_compressor.py`), memory orchestration (`agent/memory_manager.py`), credential rotation and provider failover (`agent/credential_pool.py`, 1955 lines; `agent/error_classifier.py`, 1087 lines), trajectory recording (`agent/trajectory.py`), and the model adapters for every provider (`agent/anthropic_adapter.py`, `agent/bedrock_adapter.py`, `agent/codex_responses_adapter.py`, `agent/gemini_*_adapter.py`, `agent/copilot_acp_client.py`, `agent/lmstudio_reasoning.py`, `agent/moonshot_schema.py`).

**Does not own:** the actual UI; the gateway sessions; the tool implementations (only the dispatch contract); the skill bodies; the cron firing logic. Adapters know how to *talk* to a provider; the credential pool knows *which* credential to use; the loop owns the conversation.

**Key boundary lines (from `run_agent.py:122-200`):**
- `tools.registry` provides tool discovery — agent core does not enumerate tools itself.
- `agent.memory_manager` orchestrates `agent.memory_provider` implementations — the loop never speaks to a memory backend directly.
- `agent.process_bootstrap.OpenAI` is a lazy SDK proxy — production never imports `openai` at module top; tests patch `run_agent.OpenAI`.

### 4.2 Tools + Tool Environments (`tools/`)

**Owns:** the 40+ atomic capabilities and the seven execution environments. `tools/registry.py:57-74` shows the discovery rule: any `tools/*.py` with a top-level `registry.register()` call is auto-imported. `tools/environments/base.py:1-99` defines the spawn-per-call contract every backend implements. The `ToolEntry` dataclass (`tools/registry.py:77-106`) is the unit of declaration: `name`, `toolset`, `schema`, `handler`, `check_fn`, `requires_env`, `is_async`, `description`, `emoji`, `max_result_size_chars`, `dynamic_schema_overrides`.

**Does not own:** which toolset a platform exposes (that's `toolsets.py`); how a tool's output is rendered (that's `agent/display.py`); how a tool's result is persisted between turns (`tools/tool_result_storage.py` does that, but the persistence policy is set in `agent/` and `cli.py`).

### 4.3 Skills (`skills/` + `optional-skills/`)

**Owns:** the procedural-memory layer. SKILL.md frontmatter (name, description, version, author, license, platforms, tags) — see `skills/software-development/test-driven-development/SKILL.md:1-12`. Curator (`agent/curator.py`, `agent/curator_backup.py`), skill usage tracking (`tools/skill_usage.py`), skill management tools (`tools/skill_manager_tool.py`, `tools/skills_tool.py`, `tools/skills_hub.py`).

**Does not own:** how skills are *used* in a conversation (that's the prompt builder's skills_guidance block); how they're tested (skills tests live in `tests/skills/`).

### 4.4 Gateway (`gateway/`)

**Owns:** the multi-platform messaging surface and everything that lives there. Platforms: Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Mattermost, Email, SMS, Bluebubbles, Dingtalk, Feishu (and its rules engine + sticker + media variants), Yuanbao, Webhook, HomeAssistant, MS Graph (Teams), QQBot, Wecom (+ callback + crypto), Weixin, API server. Session lifecycle (`gateway/session.py`), channel directory, delivery routing, hooks, memory monitor, mirror, pairing, runtime footer, status, sticker cache, stream consumer, WhatsApp identity helpers, shutdown forensics.

**Does not own:** the agent loop. The gateway constructs an `AIAgent` per session and drives it via `run_conversation()` — the loop owns its own state.

### 4.5 TUI Gateway (`tui_gateway/` + `ui-tui/`)

**Owns:** a *headless* alternative to the CLI surface. Ink/React (TypeScript) owns the screen; Python owns sessions, tools, model calls, and slash command logic. The transport is newline-delimited JSON-RPC over stdio (`tui_gateway/server.py:21-27` — `StdioTransport`, `bind_transport`). See `AGENTS.md:200-228` for the surface catalog.

**Does not own:** terminal rendering (that's Ink), tool implementations (those are `tools/`).

### 4.6 CLI (`hermes_cli/` + `cli.py`)

**Owns:** the user-facing command surface when Hermes is run interactively. Slash-command dispatch, setup wizard (`hermes_cli/setup.py`), doctor (`hermes_cli/doctor.py`), profile management, kanban CLI, voice integration, banner, skin engine (data-driven themes — see `AGENTS.md:398-484`), curses-based menus (`hermes_cli/curses_ui.py`). Note: 90+ files in `hermes_cli/`, including platform-specific auth (`copilot_auth.py`, `dingtalk_auth.py`, `vercel_auth.py`, `slack_cli.py`, `xai_retirement.py`).

**Does not own:** the agent loop, the tools.

### 4.7 Providers (`providers/` + `plugins/model-providers/`)

**Owns:** provider profiles — declarative descriptions of how to talk to each LLM provider (`providers/base.py:38-100`). 30+ bundled profiles under `plugins/model-providers/`: ai-gateway, alibaba (and alibaba-coding-plan), anthropic, arcee, azure-foundry, bedrock, copilot (and copilot-acp), custom, deepseek, gemini, gmi, huggingface, kilocode, kimi-coding, minimax, nous, novita, nvidia, ollama-cloud, openai-codex, opencode-zen, openrouter, qwen-oauth, stepfun, xai, xiaomi, zai. Discovery is lazy (`providers/__init__.py:65-89`); user plugins override bundled by last-writer-wins.

**Does not own:** credential rotation (`agent/credential_pool.py`), the actual HTTP calls (`agent/transports/`), retry logic (`agent/retry_utils.py`).

### 4.8 Plugins (`plugins/` + `hermes_cli/plugins.py`)

**Owns:** the pluggable surface. Four discovery sources (`hermes_cli/plugins.py:5-17`): bundled `plugins/<name>/`, user `~/.hermes/plugins/<name>/`, project `./.hermes/plugins/<name>/`, pip entry points. Each plugin exposes `register(ctx)` and can register tools, lifecycle hooks (`pre_tool_call`, `post_tool_call`, `pre_llm_call`, `post_llm_call`, `on_session_start`, `on_session_end`), CLI subcommands, platform adapters.

**Memory plugins** have their own discovery (`plugins/memory/__init__.py`). **Model-provider plugins** have their own discovery (`providers/__init__.py`). This is a *kind*-based plugin system, with three discovery paths that work in parallel. We mark it as a boundary leak in `[[10_domain/19_BOUNDARY_LAW]]`.

### 4.9 Session State (`hermes_state.py` + `cron/` + `acp_adapter/`)

**Owns:** anything that has to outlive a single process. `hermes_state.py:185+` defines the SQLite schema (sessions, messages, FTS5 virtual table). `cron/jobs.py` + `cron/scheduler.py` for scheduled work. `acp_adapter/` for IDE-side Agent Communication Protocol (Zed, VS Code, JetBrains). Schema version is 12 (`hermes_state.py:36`) — the DB has been migrated eleven times.

**Does not own:** in-process state (`AIAgent` instance variables).

### 4.10 Bootstrap & Constants (root files)

**Owns:** process initialization that must happen before anything else. `hermes_bootstrap.py` sets up UTF-8 stdio on Windows (no-op on POSIX) — must be the first import (`run_agent.py:24-32`). `hermes_constants.py:43-101` defines `get_hermes_home()`, the single source of truth for profile-aware paths. `hermes_logging.py` sets up `agent.log` / `errors.log` / `gateway.log`. `hermes_time.py` does cross-platform timezone resolution.

---

## 5. The Four Cross-Cutting Concerns

There are four concerns that *every* domain touches and which therefore live nowhere in particular. These are the architectural seams where boundary discipline matters most:

1. **Profile-awareness.** `get_hermes_home()` from `hermes_constants.py:43-101` reads `HERMES_HOME` env var; `_apply_profile_override()` in `hermes_cli/main.py` sets it before imports. *Every* persistence call must route through `get_hermes_home()`, never `Path.home() / ".hermes"`. Five bugs fixed in PR #3575 (per `AGENTS.md:948-952`) were profile drift.

2. **Logging.** `hermes_logging.setup_logging()` — three logs, profile-aware. Used everywhere; the convention is `logger = logging.getLogger(__name__)`.

3. **Cross-platform.** Win/Linux/Mac/Pi all matter. Hermes uses `psutil` rather than POSIX-only `os.kill(pid, 0)`; `pathlib.Path` instead of string concatenation; explicit `encoding="utf-8"` checks via ruff PLW1514 (`pyproject.toml:252-268`).

4. **Cache discipline.** Prompt caching must not break mid-conversation (`AGENTS.md:864-876`). This rule constrains the agent core and every plugin that touches the system prompt.

---

## 6. The Hermes ASCII Domain Map

```
                          ┌─────────────────────────────────┐
                          │       USER / OPERATOR           │
                          └────────────┬────────────────────┘
                                       │
        ┌──────────────────────────────┼────────────────────────────┐
        ▼                              ▼                            ▼
┌──────────────┐            ┌──────────────────┐         ┌──────────────────┐
│ CLI / TUI    │            │   GATEWAY        │         │   ACP            │
│ cli.py       │            │   30+ platforms  │         │   IDE adapter    │
│ hermes_cli/  │            │   gateway/       │         │   acp_adapter/   │
│ tui_gateway/ │            │                  │         │                  │
└──────┬───────┘            └────────┬─────────┘         └────────┬─────────┘
       │                             │                            │
       │   ┌─────────────────────────┴────────────────────────────┘
       │   │
       ▼   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          AGENT CORE                                     │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ AIAgent        │──│ conv_loop    │──│ context_eng  │──│ memory_mgr │ │
│  │ run_agent.py   │  │ 4094 lines   │  │              │  │            │ │
│  └────────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ prompt_builder │  │ tool_executor│  │ cred_pool    │  │ err_class. │ │
│  └────────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
└─────────┬───────────────┬───────────────────┬──────────────────────┬────┘
          │               │                   │                      │
          ▼               ▼                   ▼                      ▼
┌─────────────┐  ┌────────────────┐  ┌─────────────────┐    ┌──────────────┐
│ TOOLS       │  │ ENVIRONMENTS   │  │ PROVIDERS       │    │ PLUGINS      │
│ 60+ files   │  │ docker/ssh/    │  │ 30+ profiles    │    │ memory,      │
│ registry.py │  │ modal/daytona/ │  │ credential pool │    │ context_eng, │
│ toolsets.py │  │ vercel/local   │  │                 │    │ image_gen,   │
│             │  │ singularity    │  │                 │    │ kanban,      │
│             │  │                │  │                 │    │ achievements,│
└──────┬──────┘  └────────────────┘  └─────────────────┘    │ teams, ...   │
       │                                                    └──────────────┘
       │                                                            │
       ▼                                                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       SKILLS (procedural memory)                        │
│  skills/ + optional-skills/ — ~25 categories, hundreds of SKILL.md      │
│  curator (auto-archive), skill usage telemetry, skills-hub sync         │
└─────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  PERSISTENCE  +  IDENTITY  (profile-aware)              │
│  hermes_state.py (SQLite + FTS5)   ~/.hermes/state.db                   │
│  cron/ (scheduler + jobs)           ~/.hermes/cron/                     │
│  ~/.hermes/config.yaml              ~/.hermes/.env (secrets)            │
│  ~/.hermes/logs/{agent,errors,gateway}.log                              │
│  ~/.hermes/skills/.usage.json (curator telemetry)                       │
│  ~/.hermes/profiles/<name>/<everything-above-again>                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Hermes Domain Decisions Worth Stealing

Five domain-level decisions Hermes made well, that Ember should consider:

1. **One agent loop, many surfaces.** CLI, TUI, gateway, ACP, MCP server all drive the same `AIAgent.run_conversation`. No second loop, no surface that re-implements iteration. Ember already does this implicitly with Munnr being the only mouth — but Hermes proves the model holds when you add WhatsApp, Discord, Zed, MCP, and stdio JSON-RPC.

2. **Declarative provider profiles.** `providers/base.py:38-100` — a dataclass per provider, fields for auth/endpoint/quirks/temperature/aux model, behavioral hooks (`prepare_messages`, etc.). Transports read the profile rather than getting flag-dump constructors. Crystal-clear domain boundary.

3. **Lazy plugin discovery.** `providers/__init__.py:91-100`, `plugins/memory/__init__.py`, `hermes_cli/plugins.py` — each has its own discovery, but all of them defer until first use. Means a plugin that's never invoked never costs anything.

4. **Spawn-per-call execution.** `tools/environments/base.py:1-99` — every command spawns a fresh `bash -c` with a sourced session snapshot. CWD persists via in-band stdout markers (remote) or temp file (local). This is the simplest possible execution model that still survives cross-host environments (Modal, Docker, SSH). Compare with the alternative: long-lived shell sessions and PTY juggling. The simplicity is the win.

5. **FTS5 across all sessions.** `hermes_state.py:185+` — session messages searchable by full-text across the entire history. The `session_search` tool calls this. Memory across sessions becomes a query problem rather than a recall problem.

## 8. Hermes Domain Decisions Worth Refusing

Three decisions Ember should pointedly *not* inherit:

1. **One file with 60% of the lifecycle (`cli.py`, 662 KB).** It is a class with 11k LOC. It has been growing for years. Tests patch its module symbols. Extracting it now would be a multi-month project. Ember must never let a Munnr file cross 2k lines without breaking it up. We dwell on this in `[[10_domain/18_HERMES_CLI]]`.

2. **Three parallel plugin discovery systems.** General (`hermes_cli/plugins.py`), memory (`plugins/memory/__init__.py`), model-providers (`providers/__init__.py`) — different code, different conventions, different load timing, different override semantics. A user who writes a "memory plugin" with the general layout will silently fail. Ember should have *one* plugin-discovery convention.

3. **662 KB of CLI code coupled to 180 KB of agent core via patching.** The pattern `from run_agent import OpenAI` and the test-side `patch("run_agent.OpenAI", ...)` (`run_agent.py:56-62`) means the SDK proxy is a module-level mutable. Refactoring `run_agent` becomes a test-breaking exercise. Ember already has the realm-band test (`tests/unit/test_skeleton_imports.py`) — keep enforcing it.

---

## What This Means for Ember

The domain map confirms that **Ember's six True Names + Three Realms already represent a stricter, more disciplined version of Hermes's eleven domains.** What Hermes has accidentally is what Ember has by design. The Hermes mapping into Ember's frame:

| Hermes domain | Ember True Name | Realm | Notes |
|---|---|---|---|
| Agent Core (loop) | **Funi** + Munnr | Spark | Funi runs the model; Munnr drives the turn |
| Tools | (new — propose **Verkfæri**?) | Spark + Thread | Ember currently has a tool framework (slice 2); has not named it |
| Tool Environments | (out of slice) | Spark | Local-only for slice 2; remote backends are a future concern |
| Skills | (new — propose **Listir**?) | Spark | Procedural memory not yet present in Ember |
| Gateway | (out of slice — Ember = single-user) | Thread | The multi-platform surface is *not* an Ember priority |
| TUI Gateway | Munnr | Spark | Ember's Munnr already plays this role; an Ink-style TUI is a slice-N possibility |
| CLI | Munnr | Spark | Ember's Munnr is the canonical mouth |
| Providers | (new — propose **Vegfarendr**?) | Thread | Ember has Funi for one provider; multi-provider is future |
| Plugins | (new — needs a True Name) | All three | Pluggability is a Vow but currently per-Realm, not per-system |
| Session State | **Brunnr** (partial) | Well | Ember already has SQLite + pgvector; needs session-FTS5 |
| Bootstrap & Constants | (built into Hjarta + config loader) | Spark | Hermes's profile system is one possible model |

### Concrete proposals for the Ember domain map

1. **Adopt the Eleven-Domains discipline at the file-tree level.** Each Ember Realm (`src/ember/spark/`, `src/ember/thread/`, `src/ember/well/`) already has sub-modules per True Name. Extend the practice: *every* subsystem with more than five files gets a `README_AI.md` that names what it owns and what it does NOT own. Hermes's `AGENTS.md` is the single biggest source of architectural memory in the project; Ember should have the same artifact per Realm.

2. **Propose two new True Names: Listir (skills/procedural memory) and Verkfæri (tools).**
   - **Listir** (Old Norse: "arts, skills") — the procedural memory layer. Lives in Spark; reads from Well (skill content can live in the knowledge DB), executes via Verkfæri. Distinct from Funi (which is just the model) and Munnr (which is the mouth).
   - **Verkfæri** (Old Norse: "tools, implements") — the tool framework. Lives in Spark; can call out to Thread or Well. Distinct from individual tools (each is a Verkfæri *member*); the framework itself is the True Name.

   This raises the count to eight True Names, which is more than six. The Architect's recommendation: extend, do not crowd. Eight is still small; eight is namable. (We elaborate this in `[[60_synthesis/61_TRUE_NAME_REASSIGNMENT]]`.)

3. **Reinforce the Vow of Modular Authorship by formalizing a single plugin-discovery contract.** Hermes has three. Ember should have one — even if the kinds it accepts vary (memory, context, ingest source, tool, surface adapter). A discovery contract that says "look in these three roots; honor this `plugin.yaml`; expose this `register(ctx)`" — *one* surface, *one* test path, *one* override rule.

4. **Honor the Vow of Smallness by *not* importing the gateway, the multi-platform surface, the trajectory compressor, or the batch runner.** Hermes's gateway alone is heavier than Ember's entire slice-2 surface. The Three Realms refusal is correct.

5. **Honor the Vow of Tethered Grounding by adopting Hermes's FTS5-everywhere pattern** — `hermes_state.py:185+` makes every past session searchable. Ember already has Brunnr; the session-FTS5 pattern is the bridge between Brunnr and Munnr's memory. (We elaborate in `[[30_execution/38_PERSISTENT_MEMORY]]`.)

6. **Vow of Public-Friendliness is reinforced.** Hermes's `hermes doctor` is the right pattern; Ember already has `ember doctor`. Ember should *not* adopt Hermes's skin engine (cute and clever, but contrary to the Vow of Smallness when shipped to a Pi 5).

The Vows most reinforced by this map: **Vow of Modular Authorship**, **Vow of Smallness**, **Vow of Tethered Grounding**. The Vow most at risk if we mis-port from Hermes: **Vow of Smallness** — every Hermes domain has a smaller cousin Ember could adopt, but together they would *not* fit on a Pi.

Take the bones. Leave the fat. The bones are the eleven domains. The fat is the 662 KB CLI file, the three plugin discoveries, the thirty-platform gateway. Ember will eat the eleven and leave the rest by the fire.

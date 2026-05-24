---
codex_id: 13_TOOLS_SUBSYSTEM
title: The Tools Subsystem — Forty Capabilities Behind One Contract
role: Architect
layer: Domain
status: draft
hermes_source_refs:
  - tools/registry.py:1-250
  - tools/registry.py:77-106
  - tools/registry.py:120-149
  - toolsets.py:1-300
  - toolsets.py:31-73
  - toolset_distributions.py:1-100
  - model_tools.py
  - agent/tool_executor.py:1-100
  - agent/tool_dispatch_helpers.py
  - agent/tool_guardrails.py
  - tools/terminal_tool.py
  - tools/file_tools.py
  - tools/file_operations.py
  - tools/file_safety.py
  - tools/patch_parser.py
  - tools/fuzzy_match.py
  - tools/browser_tool.py
  - tools/browser_camofox.py
  - tools/browser_cdp_tool.py
  - tools/web_tools.py
  - tools/url_safety.py
  - tools/website_policy.py
  - tools/code_execution_tool.py
  - tools/delegate_tool.py
  - tools/clarify_tool.py
  - tools/memory_tool.py
  - tools/todo_tool.py
  - tools/mcp_tool.py
  - tools/mcp_oauth.py
  - tools/mcp_oauth_manager.py
  - tools/cronjob_tools.py
  - tools/computer_use/
  - tools/environments/base.py:1-100
  - tools/managed_tool_gateway.py
  - tools/tool_result_storage.py
  - tools/tool_output_limits.py
  - tools/schema_sanitizer.py
  - tools/process_registry.py
  - tools/approval.py
  - tools/interrupt.py
  - AGENTS.md:263-310
  - AGENTS.md:697-715
ember_subsystem_targets: [Verkfæri, Funi, Munnr, Brunnr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_AGENT_CORE
  - 10_domain/16_TUI_GATEWAY_BACKENDS
  - 10_domain/17_PLUGINS_EXTENSIBILITY
  - 20_interface/22_SKILL_INTERFACE
  - 30_execution/34_PROCEDURAL_SKILL_CRAFTING
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
---

# The Tools Subsystem
## Forty Capabilities Behind One Contract

*— Rúnhild Svartdóttir, Architect*

> *A system without a unified tool contract is a system with as many shapes as it has verbs. The agent will spend more cognition deciding how to ask than doing the thing. The architect's job is to make the asking the same shape every time.*

`tools/` is 60+ files and over 40 distinct agent-callable capabilities. They cover terminal execution (across seven backends), file operations, web search, browser automation, code execution, memory, todos, MCP integration, delegation, clarification, send_message, kanban, image generation, vision, TTS, transcription, computer use, voice mode — and a dozen meta-tools that manage skills, approvals, interrupts, and tool result storage. This doc maps the contract that holds them all in one shape.

The mental model: **one `ToolRegistry`, one `ToolEntry` dataclass, one self-registration convention, one dispatch entry point.** Variability lives inside the handler. The shape is uniform.

---

## 1. The `ToolEntry` Contract

`tools/registry.py:77-106` defines the unit of declaration:

```python
class ToolEntry:
    """Metadata for a single registered tool."""

    __slots__ = (
        "name", "toolset", "schema", "handler", "check_fn",
        "requires_env", "is_async", "description", "emoji",
        "max_result_size_chars", "dynamic_schema_overrides",
    )
```

Fields:

| Field | Type | Purpose |
|---|---|---|
| `name` | str | Canonical tool name (e.g. `"web_search"`); must be unique across the registry |
| `toolset` | str | The toolset this tool belongs to (e.g. `"web"`, `"file"`); enables/disables atomic groups |
| `schema` | dict | OpenAI tool-schema JSON: `{"name", "description", "parameters": {...}}` |
| `handler` | Callable | The actual function. Signature: `handler(args: dict, **kwargs) -> str` (JSON string return) |
| `check_fn` | Callable\|None | Zero-arg fn returning bool — is this tool *available* in the current environment? |
| `requires_env` | list[str] | Env vars required (e.g. `["EXAMPLE_API_KEY"]`); surfaced in doctor |
| `is_async` | bool | Async handler? Currently most are sync; the registry handles both |
| `description` | str | Human description (different from schema description) |
| `emoji` | str | Display emoji for the tool-progress line |
| `max_result_size_chars` | int\|None | Per-tool result size cap (overrides global) |
| `dynamic_schema_overrides` | Callable\|None | Zero-arg fn returning dict; applied at `get_definitions()` time |

This is the entire surface. Every tool — from the 30-page terminal tool to the one-line `clarify` tool — declares itself this way.

### 1.1 The Self-Registration Convention

Every tool file calls `registry.register()` at module top. From the canonical example in `AGENTS.md:276-294`:

```python
# tools/your_tool.py
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

The discovery rule (`tools/registry.py:42-74`):

- `_module_registers_tools(module_path)` does an AST scan for top-level `registry.register(...)` calls
- `discover_builtin_tools()` imports every `tools/*.py` (excluding `__init__.py`, `registry.py`, `mcp_tool.py`) that passes the AST scan
- `model_tools.py` triggers the discovery as an import side-effect

The two-step convention (per `AGENTS.md:297-301`): registration happens automatically; **wiring into a toolset is manual**. A tool that calls `registry.register()` exists in the registry but is only *exposed* to the agent if its name appears in some toolset. `_HERMES_CORE_TOOLS` (`toolsets.py:31-73`) is the default bundle.

This is a *deliberate* friction. You can experiment with a tool by registering it without it polluting every agent's schema. You opt-in to expose.

---

## 2. The Toolset Surface

`toolsets.py` defines the `TOOLSETS` dict — currently 30+ named toolsets:

```
browser, clarify, code_execution, computer_use, cronjob, debugging, delegation,
discord, discord_admin, feishu_doc, feishu_drive, file, homeassistant, image_gen,
kanban, memory, messaging, moa, rl, safe, search, session_search, skills, spotify,
terminal, todo, tts, video, video_gen, vision, web, x_search, yuanbao
```

Each toolset has:
- `description` — human-readable
- `tools` — list of tool names (must be registered)
- `includes` — list of *other toolsets* to inherit

The composition (`includes`) lets `_HERMES_CORE_TOOLS` exist as a single source of truth — the default-bundle list — that messaging adapter toolsets reference rather than duplicate (`toolsets.py:29-30`).

### 2.1 Toolset Distributions

`toolset_distributions.py` (12 KB) defines *probabilistic* toolset bundles for batch processing and data generation runs. Six built-in distributions (`toolset_distributions.py:29-100`):

- `default` — all tools, all the time
- `image_gen` — 90% image-gen, 90% vision, 55% web, 45% terminal, 10% moa
- `research` — 90% web, 70% browser, 50% vision, 40% moa, 10% terminal
- `science` — 94/94/94/65/50/15/10 for web/terminal/file/vision/browser/image_gen/moa
- `development` — 80% terminal, 80% file, 60% moa, 30% web, 10% vision
- `safe` — no terminal; 80% web, 70% browser

These are *not* for interactive use. They are for `batch_runner.py` — generating synthetic conversation data with varied tool availability so the model trains on diverse capability surfaces.

For Ember, the distributions are mostly out of scope (no training pipeline). The taxonomy itself, though, is useful: **research / development / science / safe** is a sensible categorization for tool bundles per *operator role*.

---

## 3. The 40+ Tools by Category

Here is the rough taxonomy. The line numbers point to each tool's file in `tools/`:

### 3.1 Execution & Process (`tools/terminal_tool.py`, `tools/process_registry.py`)

- **`terminal`** — execute a command in the active environment (Docker / SSH / Modal / Daytona / Singularity / Vercel Sandbox / local). Supports `background=True` for long-running tasks with `notify_on_complete`. The biggest tool by far.
- **`process`** — list, kill, and inspect background processes Hermes started.

### 3.2 File (`tools/file_operations.py`, `tools/file_tools.py`, `tools/file_safety.py`, `tools/patch_parser.py`, `tools/fuzzy_match.py`)

- **`read_file`** — read a file (with line ranges, encoding handling)
- **`write_file`** — write a whole file (atomic write)
- **`patch`** — apply a diff/patch with fuzzy matching (`tools/fuzzy_match.py`); preferred over `sed`/`awk`
- **`search_files`** — content + file-tree search (preferred over `grep`/`find`)
- **`file_state`** (`tools/file_state.py`) — internal tracking of file mutations across the turn

`tools/file_safety.py` + `tools/path_security.py` keep all of these from writing outside allowed roots. `tools/binary_extensions.py` lists the file extensions Hermes refuses to read inline.

### 3.3 Web (`tools/web_tools.py`, `tools/url_safety.py`, `tools/website_policy.py`)

- **`web_search`** — pluggable search backends (Brave Free, DDGS, Exa, Firecrawl, Parallel, SearXNG, Tavily, xAI)
- **`web_extract`** — fetch and clean a URL's text (Firecrawl / native)

`tools/url_safety.py` filters URLs (block list, scheme allow list); `tools/website_policy.py` applies per-site behavior.

### 3.4 Browser (`tools/browser_tool.py` + extensions)

- **`browser_navigate`** — go to URL
- **`browser_snapshot`** — screenshot + accessibility tree
- **`browser_click`**, **`browser_type`**, **`browser_scroll`**, **`browser_back`**, **`browser_press`** — interaction
- **`browser_get_images`** — return images on a page
- **`browser_vision`** — call a vision model on the screenshot
- **`browser_console`** — read browser console
- **`browser_cdp`** (`tools/browser_cdp_tool.py`) — raw Chrome DevTools Protocol access
- **`browser_dialog`** — handle JS alert/confirm/prompt

Backend: Camoufox (`tools/browser_camofox.py`, `tools/browser_camofox_state.py`) — a stealth Firefox fork. Process supervision via `tools/browser_supervisor.py`.

### 3.5 Memory & Recall

- **`memory`** (`tools/memory_tool.py`) — persistent memory across sessions (notes + user profile); routes through `agent/memory_manager.py`
- **`session_search`** (`tools/session_search_tool.py`) — full-text search across past sessions via the SQLite FTS5 index in `state.db`
- **`todo`** (`tools/todo_tool.py`) — agent-level todo list; intercepted by `run_agent.py` before `handle_function_call` (per `AGENTS.md:307`)

### 3.6 Code & Delegation

- **`execute_code`** (`tools/code_execution_tool.py`) — run a Python script that calls tools programmatically (reduces LLM round trips for multi-tool sequences)
- **`delegate_task`** (`tools/delegate_tool.py`) — spawn a subagent with isolated context. Single or batch shape. Roles: `leaf` (default, focused worker) or `orchestrator` (can spawn its own workers). Gated by `delegation.orchestrator_enabled` and `delegation.max_spawn_depth` (default 2). See `AGENTS.md:717-746` for the full spec.

### 3.7 Skills (covered in detail in `[[10_domain/12_SKILLS_PROCEDURAL_MEMORY]]`)

- **`skills_list`** (`tools/skills_tool.py`)
- **`skill_view`** (`tools/skills_tool.py`)
- **`skill_manage`** (`tools/skill_manager_tool.py`)

### 3.8 Vision, Image, Audio

- **`vision_analyze`** (`tools/vision_tools.py`) — vision-LLM call on an image
- **`image_generate`** (`tools/image_generation_tool.py`) — pluggable image-gen backends (OpenAI, OpenAI Codex, xAI, FAL)
- **`video_analyze`** — video understanding (opt-in, not in default toolset)
- **`video_generate`** (`tools/video_generation_tool.py`) — pluggable (FAL, xAI)
- **`text_to_speech`** (`tools/tts_tool.py`) — Edge TTS (free), ElevenLabs, OpenAI, xAI
- **`neutts_synth`** (`tools/neutts_synth.py`) — local TTS (Neural TTS via samples)
- **`transcription`** (`tools/transcription_tools.py`) — STT (faster-whisper, MiniMax, etc.)
- **`voice_mode`** (`tools/voice_mode.py`) — push-to-talk integration

### 3.9 MCP (Model Context Protocol)

- **`mcp_tool`** (`tools/mcp_tool.py`) — dispatch to MCP servers. Hermes is *both* an MCP server (`mcp_serve.py`) and an MCP client.
- `tools/mcp_oauth.py`, `tools/mcp_oauth_manager.py` — OAuth flows for MCP servers requiring auth.

### 3.10 Scheduling

- **`cronjob`** (`tools/cronjob_tools.py`) — agent can schedule its own jobs via `cron/`

### 3.11 Cross-Platform Messaging

- **`send_message`** (`tools/send_message_tool.py`) — send to any connected gateway platform
- **`discord`**, **`discord_admin`** (`tools/discord_tool.py`)
- **`feishu_doc`**, **`feishu_drive`** (`tools/feishu_doc_tool.py`, `tools/feishu_drive_tool.py`)
- **`yuanbao_*`** (`tools/yuanbao_tools.py`)
- **`x_search`** (`tools/x_search_tool.py`) — Twitter/X via xAI's built-in tool

### 3.12 Smart Home

- **`ha_list_entities`**, **`ha_get_state`**, **`ha_list_services`**, **`ha_call_service`** (`tools/homeassistant_tool.py`)
- **`spotify_*`** (plugin `plugins/spotify/`)

### 3.13 Kanban (covered in `[[10_domain/10_DOMAIN_MAP]]`)

- **`kanban_show`**, **`kanban_list`**, **`kanban_complete`**, **`kanban_block`**, **`kanban_heartbeat`**, **`kanban_comment`**, **`kanban_create`**, **`kanban_link`**, **`kanban_unblock`** (`tools/kanban_tools.py`)

### 3.14 Meta-Tools

- **`clarify`** (`tools/clarify_tool.py`, `tools/clarify_gateway.py`) — ask the user a clarifying question (multiple-choice or open-ended)
- **`mixture_of_agents`** (`tools/mixture_of_agents_tool.py`) — call multiple models on the same prompt, return a synthesis
- **`computer_use`** (`tools/computer_use/`) — background macOS desktop control via cua-driver MCP stdio
- **`osv_check`** (`tools/osv_check.py`) — supply-chain vuln check against OSV database
- **`tirith_security`** (`tools/tirith_security.py`) — additional security scanning

### 3.15 Internal Management (not agent-callable)

- `tools/approval.py` — approval-prompt routing (operator must approve dangerous tool calls)
- `tools/interrupt.py` — interrupt signaling
- `tools/checkpoint_manager.py` — conversation checkpoints
- `tools/process_registry.py` — tracking of background processes
- `tools/tool_result_storage.py` — persist tool results (sized via `tool_output_limits.py`)
- `tools/schema_sanitizer.py` — strip schema fields llama.cpp can't parse
- `tools/budget_config.py` — per-turn tool-result budget
- `tools/credential_files.py` — credential file resolution
- `tools/managed_tool_gateway.py` — gateway to managed tool sandboxes
- `tools/microsoft_graph_auth.py` + `tools/microsoft_graph_client.py` — Microsoft Graph (Teams) auth
- `tools/lazy_deps.py` — lazy pip-install of optional deps on first tool use
- `tools/openrouter_client.py`, `tools/xai_http.py` — provider HTTP clients
- `tools/slash_confirm.py` — slash-command confirmation dialog
- `tools/env_passthrough.py` — env var passing into sandboxes
- `tools/debug_helpers.py` — debug-mode utilities
- `tools/ansi_strip.py` — strip ANSI escapes from tool output

That's well over 60 Python files supporting 40+ agent-callable tools.

---

## 4. The Dispatch Loop

`agent/tool_executor.py` is the dispatcher. The path from "the model emitted a tool call" to "the result is in the messages list":

1. `conversation_loop` receives the API response with `tool_calls`.
2. If `len(tool_calls) > 1`, decide parallel vs. sequential via `agent/tool_dispatch_helpers.py:_should_parallelize_tool_batch`.
3. Branch to `execute_tool_calls_concurrent` or `_execute_tool_calls_sequential`.
4. For each tool call:
   - Parse `tool_call.function.arguments` JSON
   - Reset nudge counters
   - Pre-flight: interrupt check, destructive-command check (`_is_destructive_command`), path-overlap check (`_paths_overlap`)
   - Run guardrails: `tool_guardrails.evaluate(call)` → `ToolGuardrailDecision`
   - If denied, synthesize a result; if allowed, dispatch to `handle_function_call(name, args, task_id)`
   - Wrap multimodal results via `_is_multimodal_tool_result` + `_multimodal_text_summary`
   - Append subdirectory-hint via `_append_subdir_hint_to_multimodal`
   - Append result to messages
5. After all calls: `maybe_persist_tool_result` (`tools/tool_result_storage.py`) writes large outputs to disk and replaces them in-band with a reference; `enforce_turn_budget` (`tools/tool_result_storage.py`) cuts off the cumulative size if the turn is using too many tokens.

The thread pool cap is `_MAX_TOOL_WORKERS = 8` (`agent/tool_executor.py:55-56`). The interrupt check happens at every iteration (`agent/tool_executor.py:74-83`).

---

## 5. The check_fn Cache

`tools/registry.py:120-149` is a small TTL cache for `check_fn` results. Rationale:

- A tool's `check_fn` often probes external state — Docker daemon running? Modal SDK installed? Playwright binary present?
- Calling them on every `get_definitions()` is pure waste; external state changes on human timescales.
- The cache TTL is 30 seconds. Env-var flips via `hermes tools` propagate within a turn or two.
- `invalidate_check_fn_cache()` is exposed for explicit invalidation after config changes.

This is a small but exemplary discipline: **availability checks are expensive; cache them; expose explicit invalidation.** Ember should adopt this pattern wherever a probe answer is stable on a per-turn basis.

---

## 6. Path Security & Approval

Path security (`tools/path_security.py`, `tools/file_safety.py`) enforces a *root cage*: file tools refuse to read or write outside a configured allow list (typically the cwd + a few explicit roots). The implementation is robust against `..`, symlinks, and absolute-path tricks.

Approval (`tools/approval.py`) is the human-in-the-loop layer. When a tool call is marked `requires_approval`, the dispatcher pauses and waits for the operator's `/approve` or `/deny`. The gateway has *two* message guards that both must bypass approval (per `AGENTS.md:970-979`) — see `[[10_domain/14_GATEWAY_MULTI_PLATFORM]]`.

The audit log distinguishes outcomes (per `SYSTEM_VISION.md:236-240`): `approved`, `denied`, `invalid_arguments`, `forbidden`, `no_such_tool`. Never collapsed into a generic "failed."

---

## 7. The Result Storage Discipline

`tools/tool_result_storage.py` + `tools/tool_output_limits.py` solve the *result-explosion* problem: a single `terminal` call can produce megabytes of output. If those bytes go into the API messages list, they cost API tokens and break prompt caching for the rest of the session.

The strategy:
1. Each tool has an optional `max_result_size_chars` (`ToolEntry` field; falls back to a global default)
2. If a result exceeds the cap, it is written to disk (e.g. `~/.hermes/tool_results/<task_id>/<tool>-<n>.txt`) and the in-band result is replaced with `[Output too large — written to <path>]`
3. The agent can `read_file(path)` to consult it
4. `enforce_turn_budget` further caps cumulative result size *across* all tools in a turn

This is one of Hermes's most robust defenses against the "agent reads its own gigabyte stack trace" failure mode. **Vow of Smallness in execution.**

---

## 8. The MCP Integration

`tools/mcp_tool.py` makes Hermes an MCP *client*. MCP servers (declared in `~/.hermes/mcp.yaml` or via `mcp_config.py`) expose tools the agent can call alongside its native tools. The MCP-discovered tools appear in the registry under a synthetic toolset (`mcp:<server-name>`).

`mcp_serve.py` (31 KB at repo root) makes Hermes an MCP *server* — Hermes can be a sub-agent to a higher-level orchestrator (Claude Desktop, an MCP-aware IDE, another Hermes instance).

This *double-ended MCP* posture is what makes Hermes interoperable. The same `ToolEntry` shape is exported as MCP tool descriptors and imported as MCP tool wrappers. The contract is uniform across the boundary.

---

## 9. The Boundary Lines

Three boundaries to name explicitly:

1. **Tool ↔ Environment.** A tool *names* the capability ("run this command", "read this URL"); an environment *executes* it ("via Docker", "via SSH", "via Modal"). The tool does not know the environment. Switching environments doesn't change tool semantics. This is the cleanest boundary in the entire tools subsystem.

2. **Tool ↔ Toolset.** A tool registers itself; a toolset *includes* tools. A tool is only exposed to an agent if some toolset references it. This two-step is deliberate friction.

3. **Tool ↔ Plugin-Provided Tool.** Plugins can `ctx.register_tool(...)` (per `hermes_cli/plugins.py:498-503`) which goes through the same `registry.register()`. Plugin tools are first-class registered tools. The boundary is *discovery*: plugin tools are discovered by `discover_plugins()`, native tools by `discover_builtin_tools()`. The dispatcher does not distinguish them after registration.

The leak in this otherwise clean picture: the `model_tools.py` dispatch fn does some *type-based intercepts*. `todo` and `memory` are agent-level tools intercepted in `run_agent.py` *before* `handle_function_call` (per `AGENTS.md:307`). This means those two tools have privileged access to `AIAgent` state that other tools don't. It is justified (todo and memory want session-scoped state) but it is a special-case carve-out the architecture would be cleaner without.

---

## What This Means for Ember

**Proposed new True Name: Verkfæri** (Old Norse: "tools, implements, utensils"). Verkfæri is the tool framework — distinct from individual tools (each is a Verkfæri member). She is the *shape* every tool wears.

Lives in: `src/ember/spark/verkfaeri/` (proposed). Realm: Spark. Reads from: any Realm via tool-specific routes. Calls out to: tools' own resources.

Ember already has the beginnings of Verkfæri from slice 2 — the tool framework with three tools (todo, time, calc — per `SYSTEM_VISION.md:130`). The Hermes pattern shows the path forward.

### Concrete proposals

1. **Adopt the `ToolEntry` contract exactly.** Same fields (`name`, `toolset`, `schema`, `handler`, `check_fn`, `requires_env`, `is_async`, `description`, `emoji`, `max_result_size_chars`, `dynamic_schema_overrides`). The dataclass is portable; the discipline is mature; the test surface is well-defined. Cite `tools/registry.py:77-106` as the model.

2. **Adopt the self-registration + AST scan + manual toolset wiring discipline.** Registration is automatic; exposure is opt-in. This is the right friction for an agent system that wants to grow safely.

3. **Adopt the check_fn TTL cache.** 30-second cache, explicit `invalidate_check_fn_cache()`. The pattern is small (~30 lines) and high-leverage.

4. **Adopt the result-storage discipline immediately.** Even Ember's three slice-2 tools should pass through a `max_result_size_chars` check. The cap can be per-tool. The disk path can be `~/.ember/tool_results/<session>/...`. Without this, a single tool call can break Funi's context window catastrophically.

5. **Adopt the path-security cage from `tools/path_security.py`.** File tools refuse to read or write outside allow-listed roots. Ember's current tools (todo, time, calc) don't write files, so the immediate need is small — but the first file tool *must* arrive with the cage in place.

6. **Adopt the typed approval-outcome enum (`approved`, `denied`, `invalid_arguments`, `forbidden`, `no_such_tool`).** Ember already has this (`SYSTEM_VISION.md:236-240`); reinforce it with each new tool.

7. **Adopt the agent-level intercept pattern *cautiously*.** Hermes has a privileged-tool carve-out for `todo` and `memory`. Ember already has a `todo` tool (slice 2). The pattern is justifiable but each intercept is a boundary leak; document each one explicitly.

8. **Defer the dispatch parallelization for now.** Hermes's `_NEVER_PARALLEL_TOOLS` / `_PARALLEL_SAFE_TOOLS` / `_PATH_SCOPED_TOOLS` / `_DESTRUCTIVE_PATTERNS` matrix is sophisticated. Ember's first cut should be **sequential dispatch only**. Parallelization is a slice-N optimization, not a foundation.

9. **Defer the seven execution environments.** Hermes supports Docker/SSH/Modal/Daytona/Singularity/Vercel/local. Ember should ship **local only** (Vow of Smallness, Pi-target). Remote execution backends are a future slice. The `tools/environments/base.py` ABC is portable when that day comes.

10. **Do not adopt the 40+ tool count as an end goal.** Hermes has been growing tools for years. Ember should ship **fewer, larger** tools — a single `file` tool, a single `web` tool, a single `terminal` tool, with `subcommand` parameters. This keeps the tool-schema cost low (one tool name to remember vs. 12 browser tool names).

**Affected True Names:** **Verkfæri** (new), **Funi** (reads tool definitions for schema), **Munnr** (renders tool progress), **Listir** (uses tools via skill bodies), **Brunnr** (memory tool routes here).

**Vows reinforced:** **Vow of Modular Authorship** (each tool a separate file), **Vow of Smallness** (result-storage cap), **Vow of Public-Friendliness** (typed outcomes; named errors).

**Vows at risk if ported wrong:** **Vow of Smallness** — adopting all 40 Hermes tools at once would crater the system-prompt budget on a Pi. The path forward is **fewer, larger** tools. **Vow of Modular Authorship** — the dispatch intercepts for `todo`/`memory` are a small leak; resist expanding the pattern.

The forge is many tools, but the contract is one shape. Ember inherits the shape — and forges fewer, larger tools to fit her smaller fire.

---
codex_id: 19_TOOL_DOMAIN
title: Tool Domain — Forty Functions Pretending to Be a Registry
role: Architect
layer: Domain
status: draft
sap_source_refs:
  - py/agent_tool.py:1-53
  - py/a2a_tool.py:1-39
  - py/llm_tool.py:1-190
  - py/web_search.py:1-100
  - py/utility_tools.py:1-100
  - py/task_tools.py:1-100
  - py/code_interpreter.py:1-91
  - py/comfyui_tool.py:1-50
  - py/custom_http.py:1-41
  - py/computer_use_tool.py:1-100
  - py/cdp_tool.py:1-100
  - py/cli_tool.py:1-50
  - server.py:1037-1170
  - server.py:3353-3420
ember_subsystem_targets: [Smiðja]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/13_COMPUTER_CONTROL_DOMAIN
  - 10_domain/18_EXTENSION_DOMAIN
  - 20_interface/29_TOOL_TYPE_INTERFACE
  - 60_synthesis/60_TRUE_NAME_REASSIGNMENT
---

# Tool Domain
## Forty Functions Pretending to Be a Registry

*— Rúnhild Svartdóttir, Architect*

> *A registry is what turns a pile of capabilities into an inventory. SAP has a pile of capabilities and a hand-curated manifest in the middle of a 12k-line file. That is not a registry. That is a memorized inventory.*

The tool domain in SAP is the place where the agent *acts on the world beyond chat* — web search, file ingest, agent-to-agent calls, image generation, code execution, computer control, CLI run. The mechanism is *the OpenAI function-call schema* (`{"type": "function", "function": {...}}`) instantiated as a dict in each tool's file. The composition is *conditional assembly in `server.py`*. This doc names the implicit class and the explicit pain.

---

## 1. The Subject Itself

**What the domain *does*:** offers the LLM dozens of callable functions, each defined as an OpenAI-schema dict beside its Python implementation.

**What the domain is *meant* to do but does not:** be a tool registry. There is no `ToolRegistry` class. There is no `Tool` base class. There is no `register_tool(name, schema, handler)`. There is no introspection. Each tool is a dict-and-function in its own file; composition happens at `server.py:3353-3420` via dozens of `if settings[...]['enabled']:` blocks.

**Where it lives (the "core" tools — peripheral tools live elsewhere):**

| File | LOC | Tool(s) it provides |
|---|---|---|
| `py/agent_tool.py` | 53 | `agent_tool_call` — invoke another local agent via HTTP self-call |
| `py/a2a_tool.py` | 39 | `a2a_tool_call` — invoke an external A2A-protocol agent |
| `py/llm_tool.py` | 190 | `custom_llm_tool` — call a configured remote LLM as a tool |
| `py/web_search.py` | 1,059 | duckduckgo, tavily, jina, exa, brave, bing (search + fetch) |
| `py/utility_tools.py` | 551 | `time`, weather, wiki, arxiv, calculator, etc. |
| `py/task_tools.py` | 288 | `create_subtask`, `query_task_progress`, `cancel_subtask`, `finish_task` |
| `py/code_interpreter.py` | 91 | `e2b_code` (E2B sandbox), `local_run_code` |
| `py/comfyui_tool.py` | 217 | `comfyui_tool_call` — invoke ComfyUI workflows |
| `py/custom_http.py` | 41 | `fetch_custom_http` — user-defined HTTP endpoint |
| `py/computer_use_tool.py` | 575 | mouse/keyboard/screenshot (see [[13_COMPUTER_CONTROL_DOMAIN]]) |
| `py/cdp_tool.py` | 559 | browser-via-CDP |
| `py/cli_tool.py` | 2,668 | shell exec (see [[13_COMPUTER_CONTROL_DOMAIN]]) |
| `py/pollinations.py` | 224 | `pollinations_image`, `openai_image`, `openai_chat_image` (text-to-image) |
| `py/load_files.py` | 752 | `file_tool`, `image_tool` (multi-format file ingest) |
| `py/acpx_tools.py` | 738 | ACP-protocol agent tools |

Roughly 8,000 LOC of tool implementations. ~40 distinct tools depending on how you count. **All composed at `server.py:1037-1170` and `server.py:3353-3420`** — two adjacent regions, each ~150 lines of `if ... enabled: import ...; tool_dispatch[name] = handler`.

---

## 2. How It Works

### 2.1 The tool-as-dict pattern

Every tool defines its OpenAI schema inline. Example from `py/autoBehavior.py:43-97`:

```python
auto_behavior_tool = {
    "type": "function",
    "function": {
        "name": "auto_behavior",
        "description": "当用户需要你在特定时间...",
        "parameters": {
            "type": "object",
            "properties": {
                "behaviorType": {"type": "string", "enum": ["time", "delay"]},
                "time": {"type": "string", "description": "时间格式 HH:MM:SS"},
                ...
            },
            "required": ["prompt", "behaviorType"],
        },
    },
}
```

Same shape in `py/agent_tool.py:11-32`, `py/a2a_tool.py:11-32`, `py/utility_tools.py:26-42` (the `time_tool`), `py/random_topic.py:133-191`, etc.

The schema is **handwritten in the same file as the handler**. There is no codegen from type hints. There is no Pydantic-driven schema. There is no validation that the schema's `properties` match the Python function's signature. If a developer adds an argument to the handler and forgets to update the dict, the LLM doesn't know about the new argument.

### 2.2 The composition at `server.py`

`server.py:1037-1170` is the *import-and-bind* phase:

```python
# /tmp/super-agent-party/server.py:1037-1055 (sketched from the grep)
if settings['tools']['webSearch']['enabled']:
    from py.web_search import duckduckgo_search, tavily_search, ...
    tool_dispatch['duckduckgo_search'] = duckduckgo_search
    tool_dispatch['tavily_search'] = tavily_search
    ...
if settings['tools']['knowledgeBase']['enabled']:
    from py.know_base import query_knowledge_base
    tool_dispatch['query_knowledge_base'] = query_knowledge_base
...
```

(The exact lines are approximate per `grep` — the pattern is *if-enabled, import, bind*.)

`server.py:3353-3420` is the *schema-collection* phase: each enabled tool's dict is pulled and appended to the `tools_param` list that is sent to the LLM. The two phases are *kept in sync by hand* — if you enable a tool's schema but forget its import, the LLM sees a function it can call but `server.py` raises `KeyError` on dispatch.

### 2.3 The tool dispatch

After the model returns a `tool_calls` chunk, `server.py` looks up `tool_dispatch[name]` and calls it with the parsed arguments. The result is fed back into the conversation. The handler signature is "args as Python kwargs, return string-or-dict." No protocol class; no result wrapping; no error envelope.

### 2.4 The HTTP-self-call tools

`py/agent_tool.py:36-52` and `py/llm_tool.py` both build `AsyncOpenAI(base_url=f"http://{HOST}:{PORT}/v1")` and call back into SAP's own server. This is the [[12_AGENT_CORE_DOMAIN]] sub-agent pattern *generalized*: any tool that needs to invoke an LLM (including a *configured* third-party LLM) goes through `127.0.0.1`. The result is that the local OpenAI-compat surface is *the* internal bus for cognition.

This is interesting because it means: hot-swap the model behind `super-model`, and every tool that calls "super-model" gets the new model — without touching the tool code. Modular Authorship by HTTP indirection.

### 2.5 The dynamic descriptions

Several tools build their `description` *dynamically* from settings — see `py/agent_tool.py:11-32`:

```python
agent_tool = {
    "type": "function",
    "function": {
        "name": "agent_tool_call",
        "description": f"根据Agent给出的agent_skill调用指定Agent工具，返回结果。当前可用的Agent工具ID以及Agent工具的agent_skill有：{tool_agent_list}",
        ...
```

The list of available agent IDs is **interpolated into the description** at composition time. The LLM is told *the current* roster of sub-agents in the tool description. This is a small but real innovation — the tool surface adapts to the configured environment without requiring a separate "list agents" call.

`py/a2a_tool.py:13-21` does the same for A2A agents.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 No tool registry as an object

The single biggest design failure. There should be a `ToolRegistry` with methods `register(name, schema, handler)`, `list()`, `dispatch(name, args)`. There is not. Every place that needs to know "what tools exist" must read `server.py`. Hot-swap a tool? Edit `server.py`. Test a tool? You can't — its dispatch and its tool list both live in `server.py`. The Vow of Modular Authorship is violated here at the load-bearing junction.

### 3.2 Schema-from-signature is absent

The OpenAI schema and the Python function signature are kept in lockstep by *hand*. Every tool author must duplicate the parameter list — once in the dict, once in the def. Pydantic-driven schema generation (via `pydantic.BaseModel` + `model_json_schema()`) would eliminate the drift; SAP doesn't use it.

### 3.3 No tool result envelope

A tool returns a string. Or a dict. Or sometimes raises. There is no `ToolResult(success: bool, data: Any, error: Optional[str], side_effects: List[str])`. The LLM gets whatever the function returned, stringified if not already a string. Errors and successes look identical at the wire.

### 3.4 The `web_search.py` monolith

1,059 lines of search-engine glue in one file. Six vendors (duckduckgo, tavily, jina, exa, brave, bing) handled in the same module. A vendor migration touches a giant file. Compare to the *per-platform IM bot* pattern in [[14_MESSAGING_DOMAIN]] — same kind of "many vendors, similar logic," but the IMs got per-file separation. The search tools didn't.

### 3.5 The hidden tools

`py/acpx_tools.py` (738 LOC) implements ACP-protocol agent tools — but it is barely referenced elsewhere; it is mounted via `acpx_agent` (`server.py:1152`) and used by the CLI tool's `acp` engine. It is functionally a separate tool universe. Discovery is by reading `server.py` and following imports.

### 3.6 The crisp parts

- The **OpenAI function-call schema** as the wire shape — interoperable, well-documented, well-supported across models.
- The **dynamic description interpolation** — small but real adaptive surface.
- The **HTTP-self-call** for tools-that-need-LLMs — clean indirection that enables model hot-swap.
- The **per-tool optionality** via settings flags — the modular-authorship discipline is *attempted* even if not fully achieved.
- The **handler-and-schema-in-same-file** organization — at least the tool is *findable* in one place.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §5.4 — the registry-that-isn't anti-pattern
- [[13_COMPUTER_CONTROL_DOMAIN]] — tools that touch the host
- [[18_EXTENSION_DOMAIN]] — extensions ≠ tools but adjacent
- [[20_interface/29_TOOL_TYPE_INTERFACE]] (Auditor) — the typology of tool kinds
- [[60_synthesis/60_TRUE_NAME_REASSIGNMENT]] — Smiðja revisions
- [[hermes:HEM-13_TOOLS_SUBSYSTEM]] — Hermes has a real `tools/registry.py` (40+ atomic capabilities)
- [[peer:LETTA-3_TOOL]] — Letta's tool model

---

## What This Means for Ember

**Adopt:**
- **The OpenAI function-call schema** as Ember's tool wire shape — interoperability is a Vow of Open Knowledge benefit.
- **Per-tool optionality via settings flags** + lazy import pattern — every Ember tool is individually-failable, individually-disable-able.
- **Dynamic description interpolation** — when the available roster of something changes (sub-agents, KBs, MCP servers), the tool description reflects the current roster. Build this into Smiðja's tool-emission API.
- **HTTP- (or MCP-) self-call** for tools-that-need-LLMs — keeps tool code independent of the reasoning kernel.
- **Handler-and-schema-in-same-file** — keep tools findable; the file is the unit of cohesion.

**Adapt:**
- The **dict-as-schema** pattern — adapt to **Pydantic-driven schema generation**. Ember's `Tool` base class declares an `InputModel: BaseModel`; `Tool.schema()` returns the JSON-schema from `InputModel.model_json_schema()`. The dict-and-def-drift bug closes.
- The **handler signature** — adapt to a typed `ToolResult(success, data, error, side_effects, latency_ms, audit_event)`. Every tool returns the same shape; the LLM gets `data` only when `success`; errors are auditable.
- The **monolithic `web_search.py`** — adapt to per-vendor files (`smiðja/web_search/duckduckgo.py`, etc.) with a small dispatch shim.

**Avoid:**
- **No tool registry as a first-class object.** The Server-Eaten Codebase started here. Ember's `ToolRegistry` is a real module with `register`, `list`, `dispatch`, `introspect`.
- **Schema-from-hand.** Schema is generated from typed signatures. Drift becomes impossible.
- **`server.py:3353-3420` as the only place that knows tools exist.** Discovery is via registry methods, not file-reading.
- **Stringly-typed tool returns.** ToolResult is typed.

**Invent:**
- **The Tool as Manifest.** Every Ember tool is a directory: `smiðja/tools/<name>/manifest.yaml` + `handler.py` + `prompt_fragment.md` + `example_invocations.jsonl`. The manifest declares: input schema (Pydantic), output schema (Pydantic), capability requirements (filesystem, network, GPU), tier eligibility (Pi/laptop/workstation), audit level (quiet/standard/loud). The Tool ABC scans the manifest dir at startup. SAP scatters; Ember organizes.
- **Tool Result Provenance.** Every `ToolResult.data` includes a `provenance` field naming the upstream sources (which web search vendor, which KB, which retrieval method). The LLM is forbidden from quoting tool data without preserving provenance. Combines with the [[17_RETRIEVAL_DOMAIN]] Citation Contract.
- **Tool Tier-Collapse.** A `web_search` tool on Pi might call DuckDuckGo HTML scraping (no API key); on a workstation it might use Brave Search API + Jina rerank. The manifest's tier-eligibility lets `Tool.handler()` route to the right backend per host. SAP picks the vendor; Ember picks the *and the tier*.
- **The Acceptance Predicate.** Every long-running tool optionally accepts a predicate against which the result is checked before returning to the LLM. A `code_interpreter` call might pass `acceptance=lambda r: r.returncode == 0 and 'error' not in r.stderr`. The predicate runs in code, not vibes. (Generalizes the [[12_AGENT_CORE_DOMAIN]] Completion Witness from tasks to tools.)
- **Per-Tool Rate-Limit and Cost Budget.** Each manifest declares its expected resource cost (HTTP requests, GPU seconds, dollars). Funi tracks per-conversation and per-session totals; refuses to dispatch when the budget would be exceeded. SAP has no budget surface; an LLM that misuses `web_search` 200 times in one turn is purely the user's bill.

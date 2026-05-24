---
codex_id: LETTA_MEMORY_TOOL_INTERFACE
title: Letta Memory Tool Interface — Agent-Callable Memory As First-Class API
role: Cartographer
layer: Interface
peer_targets: [Letta]
status: draft
peer_source_refs:
  - letta:letta/functions/function_sets/base.py:1-528
  - letta:letta/constants.py:112-197
  - letta:letta/services/tool_manager.py:206-1100
  - letta:letta/schemas/tool.py:31-247
  - letta:letta/services/tool_executor/tool_execution_manager.py
  - letta:letta/agent.py:1-300
  - letta:letta/server/rest_api/routers/v1/tools.py
ember_subsystem_targets: [Brunnr, Smiðja, Funi, Munnr]
hermes_codex_refs:
  - 20_interface/24_MEMORY_INTERFACE
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
cross_refs:
  - 20_interface/CROSS_TOOL_PROTOCOL_TRIANGULATION
  - 60_synthesis/CROSSWALK_LETTA_TO_EMBER
  - 60_synthesis/CROSS_TRUE_NAME_PROPOSALS_V2
---

# Letta's Memory Tool Interface — When Memory Becomes a Tool the Agent Wields

*Védis Eikleið, the Cartographer, looking at the maps Hermes drew and Letta drew side-by-side. Hermes hides the memory work behind a curator. Letta hands the model a chisel.*

## 0. The thesis in one breath

Letta's memory interface is the inversion of Hermes's. Where Hermes's `MemoryProvider` is a manager the *agent loop* drives — `prefetch`, `sync_turn`, `on_session_end`, all invoked by the host — Letta's memory is **the agent's own toolset**. The model literally calls `memory(command="str_replace", ...)`, `archival_memory_insert(content=...)`, `conversation_search(query=...)`. There is no curator. There is the model and the blocks; the model edits the blocks; the blocks are the memory.

This is a *radically different contract*. Hermes treats memory as something done *for* the agent. Letta treats memory as something done *by* the agent. The two stances make load-bearing different downstream choices: schema, lifecycle, invariants, failure model, deployment shape — every one of them flips.

This document traces Letta's tool surface, the lifecycle of a memory tool call, the invariants Letta relies on, and what Ember can borrow without taking the rest of the philosophy.

## 1. The tool surface in one screen

Letta ships *six families* of agent-callable memory tools, all defined in `letta/functions/function_sets/base.py` (`letta/functions/function_sets/base.py:10-528`) and gated by name in `letta/constants.py:112-152`:

```python
# letta/constants.py:115-118
BASE_TOOLS = [SEND_MESSAGE_TOOL_NAME, "conversation_search",
              "archival_memory_insert", "archival_memory_search"]
BASE_MEMORY_TOOLS = ["core_memory_append", "core_memory_replace",
                     "memory", "memory_apply_patch"]
BASE_MEMORY_TOOLS_V2 = ["memory_replace", "memory_insert"]
BASE_MEMORY_TOOLS_V3 = ["memory"]  # omni-tool for Anthropic
BASE_SLEEPTIME_TOOLS = ["memory_replace", "memory_insert",
                        "memory_rethink", "memory_finish_edits"]
BASE_VOICE_SLEEPTIME_TOOLS = ["store_memories", "rethink_user_memory",
                              "finish_rethinking_memory"]
```

The families serve four memory regions:

| Region | What it holds | Tools that mutate | Tools that read |
|---|---|---|---|
| **Core memory** (always-in-context blocks: `persona`, `human`, etc.) | The agent's working notebook — short, edited in-place, ≤ ~20k chars per block (`letta/constants.py:433-435`). | `core_memory_append`, `core_memory_replace`, `memory_replace`, `memory_insert`, `memory_rethink`, `memory_apply_patch`, `memory` | (Always rendered into system prompt; never explicitly "read") |
| **Archival memory** (long-term, pgvector-indexed passages) | Permanent semantic store, searchable by embedding similarity. | `archival_memory_insert` | `archival_memory_search` |
| **Conversation history** (message log) | Every turn, persisted across sessions. | (Written by the agent loop, not by tools) | `conversation_search` |
| **Files / sources** (uploaded documents, RAG) | Optional extra. | (Written by ingest pipeline) | `open_files`, `grep_files`, `semantic_search_files` |

Five different write-tools for *one* region (core memory) — `core_memory_append`, `core_memory_replace`, `memory_replace`, `memory_insert`, `memory_apply_patch` — is the first oddity worth naming. These are **versions** of the same idea: Letta has shipped at least three generations of memory-edit tooling (v1: append/replace; v2: replace/insert/rethink; v3: a single omni-`memory` tool that takes a `command` discriminator).

The `BASE_MEMORY_TOOLS_V3` family of one (`letta/constants.py:129-131`) is the *current* recommendation per the docstrings; the others are kept for backward compatibility and for sleeptime agents.

## 2. The schema — JSON function-call surface

Letta's tools follow the **OpenAI function-calling JSON schema** wire format. The schema is *generated* from Python function signatures by `letta/functions/schema_generator.py:1-903` and stored on each `Tool` row in `letta/schemas/tool.py:31-100`.

A representative schema (the omni-`memory` tool):

```json
{
  "name": "memory",
  "description": "Memory management tool with various sub-commands ...",
  "parameters": {
    "type": "object",
    "properties": {
      "command": {"type": "string",
                  "enum": ["create", "str_replace", "insert", "delete", "rename"]},
      "path":        {"type": "string"},
      "file_text":   {"type": "string"},
      "description": {"type": "string"},
      "old_string":  {"type": "string"},
      "new_string":  {"type": "string"},
      "insert_line": {"type": "integer"},
      "insert_text": {"type": "string"},
      "old_path":    {"type": "string"},
      "new_path":    {"type": "string"},
      "request_heartbeat": {"type": "boolean"}
    },
    "required": ["command", "request_heartbeat"]
  }
}
```

Three details Hermes never has to encode:

1. **`request_heartbeat`** (`letta/constants.py:217-218`) — every tool schema is *automatically augmented* with a `request_heartbeat: bool` parameter. The model uses it to chain calls: `True` means "give me another turn after this tool runs"; `False` means "this is the last thing in this step." This is **agent-controlled loop continuation**, encoded in the tool schema itself.
2. **`command` as discriminator** — v3 collapses six tools into one because LLMs perform better with fewer, fatter tools. The `command` enum makes the surface look smaller to the model while keeping the underlying handler logic separate.
3. **No `agent_state` parameter** — the function signature takes `agent_state: "AgentState"` as the first positional argument (`letta/functions/function_sets/base.py:246-280`), but the schema generator *strips* this. It is injected by the executor at call time (`letta/services/tool_executor/core_tool_executor.py`). The model never sees it. This is Letta's way of giving tools access to the agent's working memory without leaking it into the protocol.

The schema is *machine-checkable*. `letta/schemas/tool.py:110-184` is a Pydantic `ToolCreate` model with `source_type`, `source_code`, `json_schema`, `args_json_schema` (separate input schema for arg coercion), `return_char_limit`, `pip_requirements`, `npm_requirements`. The whole tool definition is structured data; the JSON Schema for the tool's parameters is *embedded inside* the Tool row.

This is Hermes's `get_tool_schemas` (`agent/memory_provider.py:121-129`) on growth hormones. Where Hermes accepts schemas as opaque dicts, Letta validates them at creation (`letta/services/tool_schema_generator.py`), stores them in PostgreSQL, indexes them by name + organization, and serves them through the REST API at `letta/server/rest_api/routers/v1/tools.py`.

## 3. The lifecycle of a memory tool call

When the model emits `memory(command="str_replace", path="/memories/user", old_string="Alice", new_string="Bob")`, what happens?

### 3.1 Model emits a tool call

The provider (OpenAI/Anthropic/etc.) returns a `tool_call` block. Letta's agent loop (`letta/agents/letta_agent.py`) parses the call and routes it to the tool execution layer.

### 3.2 Tool resolution

`ToolManager` (`letta/services/tool_manager.py:206-1100`) looks up the tool by name in PostgreSQL. The tool row carries the schema, the source code, the executor type (`builtin`, `python`, `custom`, `mcp`, `composio`), and `pip_requirements`.

For base tools (in `LETTA_TOOL_SET` at `letta/constants.py:178-187`), the lookup short-circuits — base tools are dispatched by the `core_tool_executor.py` directly without source-code execution.

### 3.3 Tool execution

`ToolExecutionManager` (`letta/services/tool_executor/tool_execution_manager.py`) picks an executor:

- **`CoreToolExecutor`** (`letta/services/tool_executor/core_tool_executor.py`) for `BASE_TOOLS` and `BASE_MEMORY_TOOLS_*`. Runs in-process, has direct access to `agent_state`, mutates `core_memory.blocks` via `agent_state.memory.update_block_value(...)` (`letta/functions/function_sets/base.py:259, 279, 379, 448, 516`).
- **`BuiltinToolExecutor`** for `run_code`, `web_search`, `fetch_webpage` (sandbox via Modal or E2B).
- **`SandboxToolExecutor`** for user-defined Python tools (`letta/services/tool_executor/sandbox_tool_executor.py`).
- **`MCPToolExecutor`** for tools backed by an MCP server.
- **`ComposioToolExecutor`** for tools from the Composio catalogue.

The executor returns a `ToolExecutionResult` (`letta/schemas/tool_execution_result.py`):

```python
class ToolExecutionResult:
    status: Literal["success", "error"]
    func_return: Optional[Any]    # Python object the function returned
    stdout: Optional[str]
    stderr: Optional[str]
    agent_state: Optional[AgentState]  # mutated state, if any
    sandbox_config_fingerprint: Optional[str]
```

### 3.4 Persistence

If the executor mutated `agent_state.memory.blocks[label].value`, the change is now in-process. `BlockManager` (`letta/services/block_manager.py`) commits the new block content to PostgreSQL on the *next* lifecycle hook (after the turn, not synchronously on tool return).

For `archival_memory_insert`, the executor calls `PassageManager` (`letta/services/passage_manager.py`) which embeds the content and writes a `Passage` row with a pgvector embedding column.

### 3.5 Return value back to the model

The executor's `func_return` is JSON-serialized and packaged as a `tool` role message in the conversation. The model sees it on the next turn (or immediately, if `request_heartbeat=True`).

`BASE_FUNCTION_RETURN_CHAR_LIMIT` (`letta/constants.py:8`) — default 6000 — truncates oversized returns with `FUNCTION_RETURN_VALUE_TRUNCATED(...)` (`letta/constants.py:200-203`). This is Letta's only built-in protection against a memory tool flooding the context.

## 4. The invariants Letta relies on

Reading the source, the load-bearing assumptions are:

| # | Invariant | Documented? | Enforced? | Breaks when violated |
|---|---|---|---|---|
| L-1 | Base tool names (`LETTA_TOOL_SET`) cannot be edited by users. | Yes — `letta/services/tool_manager.py` rejects edits with `LettaToolNameConflictError`. | Yes. | A user-renamed `archival_memory_insert` would shadow the base tool and the executor would route to nothing. |
| L-2 | The `agent_state` first-arg parameter is stripped from the JSON schema but injected at call time. | Yes — `letta/functions/schema_generator.py` strips `self`, `agent_state`. | Yes — executor checks `tool_func.__code__.co_varnames`. | A tool that *declares* `agent_state` but isn't called via the core executor gets None. |
| L-3 | Tool source code, when not a base tool, is executed in a sandbox (Modal, E2B, or local subprocess). | Yes — `letta/services/sandbox_config_manager.py`. | Yes — base tools skip sandbox; non-base tools go through `SandboxToolExecutor`. | A user-uploaded tool with malicious code runs in your agent process. |
| L-4 | `request_heartbeat` controls whether the agent gets another turn. | Yes — `letta/constants.py:217-218`. | Yes — the agent loop checks this after every tool call. | A tool that should chain (e.g., search-then-respond) returns and the loop ends. |
| L-5 | `core_memory.blocks[label].value` is the *single source of truth* per label; multiple writes don't conflict (last-writer-wins within a turn). | Implicitly. | Implicitly — no locks, no MVCC at the block level. | Two parallel tool calls editing the same block could clobber each other; Letta avoids this by serializing tool execution per agent. |
| L-6 | `archival_memory_insert` returns a Passage ID; `archival_memory_search` returns ranked passages. | Yes — docstrings. | Yes — `PassageManager` enforces shape. | A return shape change would crash the agent's downstream parser. |
| L-7 | Tool return strings ≤ `BASE_FUNCTION_RETURN_CHAR_LIMIT` (default 6000). | Yes — constant. | Yes — `FUNCTION_RETURN_VALUE_TRUNCATED` wraps. | Tools whose author overrides `return_char_limit=None` can blow the context. |
| L-8 | `memory_replace`'s `old_string` must be unique in the block. | Yes — docstring + raises `ValueError` (`letta/functions/function_sets/base.py:362-373`). | Yes — counts occurrences. | An ambiguous edit is *rejected* rather than silently picking the first match. This is the most important small invariant in the file. |
| L-9 | Line-number prefixes in `old_string`/`new_string` are rejected (`letta/functions/function_sets/base.py:345-356`). | Yes — explicit regex check + `ValueError`. | Yes. | A model that copies the rendered (line-numbered) form of a block into its edit would corrupt the block. |
| L-10 | `send_message` is the only way the agent reaches the human. All other "speech" is internal. | Yes — `letta/constants.py:112` defines it; the docstring says "Sends a message to the human user." | Yes — the agent loop short-circuits on `send_message`. | An agent that doesn't call `send_message` is silently *thinking* without speaking. (This is intentional in MemGPT's design.) |
| L-11 | `conversation_search` is a *parallel-safe* tool (`letta/constants.py:189-197`). | Yes — `LETTA_PARALLEL_SAFE_TOOLS` set. | Yes — the agent loop dispatches parallel-safe tools concurrently. | A tool that mutates state but is misclassified as parallel-safe would race. |

L-8 deserves special note. The Hermes equivalent is *prose* — "should not corrupt the block." Letta encodes it as a runtime check that *throws*. The model receives the error as the tool return and can retry with a more specific `old_string`. **This is Hermes's gap M-3 ("handle_tool_call returns a JSON-encoded string — runtime exception if a provider returns a dict") solved: at the tool's *own* layer, with an explicit precondition test.**

## 5. The lifecycle hooks Letta does NOT have

Where Hermes's `MemoryProvider` has eight optional hooks (`on_turn_start`, `on_session_end`, `on_session_switch`, `on_pre_compress`, `on_delegation`, `on_memory_write`, `prefetch`, `queue_prefetch` — `agent/memory_provider.py:163-260`), Letta has **none of them**.

Why?

- **`on_turn_start` / `on_pre_compress` / `prefetch`** — Letta does not curate context implicitly. The model decides when to call `conversation_search` or `archival_memory_search`. There is no "manager pre-fetches likely-relevant memories"; the model does it on demand.
- **`on_session_end`** — Letta has no session boundary in the same sense. Conversations persist; "ending" is implicit when the user stops sending messages.
- **`on_session_switch`** — Letta agents are scoped by `agent_id`. Switching agents is switching identities, not switching sessions inside one agent.
- **`on_memory_write`** — every memory write goes through `BlockManager` directly; there is no fan-out to plug into.
- **`on_delegation`** — Letta has multi-agent tools (`send_message_to_agent_and_wait_for_reply`, `letta/constants.py:154-155`), but delegation result reporting is just a regular `tool` return.

The mechanism Hermes uses to *hide work from the model* is the mechanism Letta refuses to use. **The model in Letta is responsible for its own memory management.** That responsibility is encoded in the system prompt (`letta/prompts/`), reinforced by the tool descriptions, and enforced by the absence of any other way to mutate state.

This has a profound consequence: a Letta agent that *forgets* to call `core_memory_replace` does not have its memory updated. Hermes's curator would have done it; Letta's model must remember to do it itself. Letta gambles on the model being competent at memory hygiene. Hermes hedges by curating implicitly.

## 6. The REST API surface

`letta/server/rest_api/routers/v1/tools.py` (and siblings) expose the memory tools as a *programmatic* surface as well — clients can call them directly without going through the agent.

Notable endpoints (from `letta/server/rest_api/routers/v1/`):

- `POST /v1/tools/` — create a custom tool (Python source code, schema, requirements).
- `GET /v1/tools/` — list tools available to the actor.
- `POST /v1/tools/run` — execute a tool directly (`letta/schemas/tool.py:213-225` ToolRunFromSource).
- `POST /v1/tools/search` — search tools by description/tags (`letta/schemas/tool.py:227-247`).
- `GET /v1/agents/{agent_id}/memory` — read current core memory state.
- `PATCH /v1/agents/{agent_id}/memory/blocks/{label}` — programmatically edit a block (this is the *non-agent* path).
- `POST /v1/agents/{agent_id}/messages` — send a message that triggers an agent step.

The OpenAPI spec is generated from FastAPI + Pydantic and lives in `fern/` (Fern SDK generator). Clients in Python, TypeScript, and Go are auto-generated from this spec.

This is **a second surface** for the same memory model — the agent-callable tool surface, and the human/programmatic REST surface. They share the underlying `BlockManager`, `PassageManager`, `MessageManager` but expose different verbs:

- Agent: `memory(command=..., path=..., ...)` — chat-flavored, command-discriminated.
- REST: `PATCH /memory/blocks/{label}` — REST-flavored, resource-oriented.

The agent never calls the REST API. The REST API never calls the tools. Both touch the same SQL rows. This is the **dual-surface pattern** Hermes does not have (Hermes is single-surface: the CLI calls the agent, the agent calls the memory provider, no other path).

## 7. Comparison to Hermes (triangulation against the Hermes Codex)

| Axis | Hermes | Letta |
|---|---|---|
| Who edits memory? | The curator (provider) edits implicitly. | The model edits explicitly via tool calls. |
| Curator hooks? | 8 optional hooks (`agent/memory_provider.py:163-260`). | 0 curator hooks. |
| Memory schema? | Mostly prose contracts. | Pydantic + JSON Schema, persisted to PostgreSQL. |
| Failure model? | `try/except` + DEBUG log (`agent/memory_manager.py:325-609`). | Tools throw; model sees the error and reroutes. |
| Multi-provider? | One-external rule (M-1 in [[hermes_codex/20_interface/24_MEMORY_INTERFACE]]). | N/A — Letta is *the* memory provider, not pluggable that way. |
| Storage adapter? | Pluggable inside the provider. | PostgreSQL + pgvector (or SQLite for dev). |
| Session model? | `session_id: str` (untyped). | `agent_id` + per-message persistence; no "session." |
| Streaming scrubber? | Yes (`StreamingContextScrubber`, `agent/memory_manager.py:62-224`). | N/A — Letta doesn't inject context, so no fence to scrub. |
| `<memory-context>` fence? | Yes — a soft trust boundary. | No — no fence; memory is rendered into system prompt directly. |
| `request_heartbeat` analogue? | No — agent loop decides continuation. | Yes — model controls continuation via tool param. |
| Programmatic memory surface? | No (the manager is internal). | Yes — REST API mutates blocks. |

The most important takeaway: **the curator pattern and the tool pattern are not interchangeable.** They live on opposite sides of a trade-off:

- **Curator (Hermes):** safer, model can be dumber, less surface area for the model to mess up. But: implicit, hard to audit, gets in the way when the model is smart.
- **Tools (Letta):** transparent, auditable (every memory edit is a tool call in the log), the model can be opinionated. But: bigger surface, more turns burned on memory hygiene, the model has to be competent.

Hermes targets *any* model class. Letta targets *capable* models (it ships with GPT-4-class defaults and gets uncomfortable below that).

## 8. The five-versions-of-the-same-tool problem

Letta's `core_memory_append`, `core_memory_replace`, `memory_replace`, `memory_insert`, `memory_apply_patch`, `memory` — six tools, four overlapping verbs, three "generations" of design. This is the cost of agent-callable memory: every time the team learned that GPT-class models worked better with a different tool shape, they shipped a new tool *and kept the old ones for backward compatibility*. The constant tables (`BASE_MEMORY_TOOLS`, `BASE_MEMORY_TOOLS_V2`, `BASE_MEMORY_TOOLS_V3`, `BASE_SLEEPTIME_TOOLS`) are the archaeology.

The model-class targeting matters: `BASE_MEMORY_TOOLS_V3` (the omni-`memory`) is explicitly noted as "currently just a omni memory tool for anthropic" (`letta/constants.py:128-131`). Different LLMs have different preferences for tool shape; Letta lets the *agent factory* pick the family.

This is a **maintenance tax**. Hermes does not pay it because Hermes's memory surface is not chosen by the model; it is chosen by the developer. Letta pays it because the model is the consumer.

**Lesson for Ember:** if Ember adopts agent-callable memory tools, it inherits this maintenance burden. Plan for *at least two tool families* over the lifetime of the project, with a way to gate which family is active per `LlmConfig`.

## 9. Memory blocks vs. Brunnr handles — a structural parallel

Letta's `Block` (`letta/schemas/block.py`):

```python
class Block:
    id: str
    label: str               # "persona", "human", "todo", or user-chosen
    value: str               # the actual content
    limit: int               # char limit (default 5000)
    description: Optional[str]
    metadata: Optional[dict]
    user_id: str
    organization_id: str
```

Ember's `Document` and `Chunk` (per Hermes Codex slice-2 retrospective):

```python
class Document: ...  # uri, content_hash, text, metadata
class Chunk: ...     # parent_uri, offset, text, embedding
```

Letta's `Passage` (`letta/schemas/passage.py`) is the archival-memory analogue — has an `embedding` column for vector search, has `tags` for filtered retrieval, has `created_at`. It is essentially Ember's `Chunk` with a different name.

Letta's `Block` has no direct Ember equivalent yet. The closest is the *system-prompt-fragment* concept Ember's Funi builds at turn start. **Ember might want a `Block`-shaped construct** — a small, mutable, agent-edited piece of system-prompt content. This would be a *new entity* in Brunnr's vocabulary; today Brunnr knows about Documents and Chunks but not about Blocks-as-state.

## 10. The Pydantic-everywhere choice

Every Letta schema is a Pydantic model. `Tool`, `ToolCreate`, `ToolUpdate`, `Block`, `Passage`, `Message`, `AgentState`, `LlmConfig`, `EmbeddingConfig` — all `LettaBase` subclasses (`letta/schemas/letta_base.py`). The schemas are:

- The wire format for the REST API.
- The DB-row → Pydantic-object materializer via `orm/tool.py`-style adapters.
- The argument validator at function boundaries.
- The OpenAPI schema source.
- The auto-generated client SDK source.

This is **one definition, many surfaces**. Hermes uses dataclasses + manual JSON conversion; Ember uses dataclasses + Protocols. Letta's choice gives it the dual-surface property (agent + REST share types) for free. **For Ember, the cost of adopting Pydantic-everywhere is a dependency on Pydantic; the benefit is automatic API-schema-from-types.** Cross-reference [[hermes_codex/20_interface/24_MEMORY_INTERFACE]] §6, which proposes typed contracts as a Hermes weakness.

## 11. Tool-rule constraints

A subtle thing Letta does, in `letta/schemas/tool_rule.py`: tools can declare **constraints on when they may be called**. `ToolRule` is a Pydantic model with rule types like:

- `init_tool_rule` — tool must be the first call after agent boot.
- `continue_tool_rule` — tool must be followed by another tool (no `send_message` after).
- `terminal_tool_rule` — tool ends the turn (no chaining).
- `conditional_tool_rule` — tool can only run if a condition holds.
- `child_tool_rule` — tool can only run after a parent tool ran.

This is a **state machine over tool calls**. Hermes has no analogue; the model is free to call any tool any time (modulo provider-level tool gating). Letta's tool-rule layer is essentially a soft programmable agent loop — a way to express "you must search before answering" or "you must finalize before ending" as policy, not prompt.

For Ember, this is a *very high-value pattern*. Cross-reference [[hermes_codex/20_interface/24_MEMORY_INTERFACE]] §4.5 (no reentrancy contract) — Letta's tool rules are exactly the right shape to encode reentrancy and ordering invariants in a typed, inspectable way.

## What This Means for Ember

**True Names affected:**

- **Brunnr** — gains a new entity type (`Block`, agent-editable state-fragment), in addition to `Document` + `Chunk`. The block surface is what Letta calls "core memory."
- **Funi** — when Funi gets tool-calling capability, the *memory tools* become candidate `Verkfæri` (per [[hermes_codex/60_synthesis/61_TRUE_NAME_REASSIGNMENT]]'s candidate). Letta's tool definitions are the prior art.
- **Smiðja** — Letta's `archival_memory_insert` shows the *agent-side* path into Smiðja: a tool the model calls that triggers ingest. Today Ember's Smiðja is operator-driven; an `ember insert <text>` tool would mirror Letta's pattern.
- **Munnr** — Letta's dual-surface model (agent + REST) is a reference for Munnr's expanded definition ([[hermes_codex/60_synthesis/61_TRUE_NAME_REASSIGNMENT]] §7).

**Vows touched:**

- *Reinforced:* Vow of Honest Memory — agent-callable memory tools mean every edit appears in the conversation log. Auditability is built in.
- *Reinforced:* Vow of Modular Authorship — Letta's tool registry pattern (DB-stored, schema-validated, sandbox-executed) is exactly modular.
- *Strained:* Vow of Smallness — six versions of the memory tool is *not* small. Ember must pick one family and refuse to ship the others until the v3 is proven.
- *Strained:* Vow of Tethered Grounding — Letta's "model edits its own memory" gives the model more autonomy to hallucinate-into-storage. Ember must keep a **read-side curator** even if it adopts agent-callable writes.

**Concrete proposals for Ember's interface:**

1. **Adopt the `request_heartbeat` pattern.** When Funi gets multi-tool turns, encode loop continuation in the tool schema, not in the agent loop. Cross-reference [[hermes_codex/20_interface/24_MEMORY_INTERFACE]] §3 (Hermes lacks this).
2. **Adopt the `tool_rule` pattern.** Letta's `letta/schemas/tool_rule.py` is a small, high-value addition: a way to declare ordering and reentrancy constraints typed, not in prose. Reference: [[hermes_codex/20_interface/24_MEMORY_INTERFACE]] §4.5.
3. **Stick to ONE memory-tool family.** Pick `BASE_MEMORY_TOOLS_V3` (omni-`memory`) or a custom Ember-shaped one. Resist accumulating versions.
4. **Keep the curator AND add tools.** Ember does not have to choose Hermes-style or Letta-style. The curator can prefetch reading; the tools can do writing. The two can coexist: read-side implicit, write-side explicit. This is *not* what either Hermes or Letta does today.
5. **Pydantic at the boundary.** When Brunnr's `Block` entity arrives, define it as a Pydantic model that is *both* the SQL row representation *and* the REST wire format *and* the tool-arg validator. One definition, many surfaces.
6. **Embed the agent-side path into Smiðja.** A tool `archival_insert(content, tags)` is the Letta-style on-ramp; the current Ember model is operator-driven. Adding the agent-side path is one tool definition and a Smiðja-trigger function.
7. **Refuse to copy six versions of the same tool.** When the v2/v3 lesson lands, kill v1 in the same release. Don't ship `BASE_MEMORY_TOOLS_V1_PLUS_V2_PLUS_V3` like Letta does.

**Hermes Codex docs reinforced:**

- [[hermes_codex/20_interface/24_MEMORY_INTERFACE]] §4 — "Where the contract is weakest." Letta closes M-3 (return type), M-4 (network at boot), and the reentrancy gap (M-5 of that doc) by making each a tool-level invariant.
- [[hermes_codex/20_interface/24_MEMORY_INTERFACE]] §6 — "Real failure modes observed in Hermes." Letta's analog: the *six memory-tool versions* prove that *any* memory tool surface accumulates archaeological cruft. Plan for that on day one.
- [[hermes_codex/60_synthesis/61_TRUE_NAME_REASSIGNMENT]] §3 — Verkfæri candidate is *strengthened* by Letta: agent-callable tools are a first-class kind of subsystem worthy of a True Name.

**Hermes Codex docs contradicted (mildly):**

- [[hermes_codex/20_interface/24_MEMORY_INTERFACE]] §2.1 — the `<memory-context>` fence is described as soft trust boundary. Letta avoids the problem by not injecting context as a fenced block; memory is rendered directly into the system prompt. **Ember can choose either; the fence is not load-bearing if memory is *part of* the system prompt rather than *appended to* it.**

The next doc, [[60_synthesis/CROSSWALK_LETTA_TO_EMBER]], traces module-by-module which parts of Letta could be lifted, lifted-with-modification, or refused.

*— Védis, the maps now show two cities: one with hidden water-bearers, one where every farmer carries her own bucket.*

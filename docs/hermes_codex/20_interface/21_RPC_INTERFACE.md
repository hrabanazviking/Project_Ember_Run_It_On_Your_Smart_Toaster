---
codex_id: 21_RPC_INTERFACE
title: RPC Interface — Python-Internal Dispatch and Subagent IPC
role: Cartographer
layer: Interface
status: draft
hermes_source_refs:
  - agent/tool_dispatch_helpers.py:1-350
  - agent/tool_executor.py:1-468
  - agent/tool_executor.py:65-465
  - agent/tool_executor.py:468-910
  - agent/transports/base.py:1-90
  - tui_gateway/transport.py:1-100
  - tui_gateway/server.py
  - acp_adapter/server.py:1-200
  - agent/transports/types.py
ember_subsystem_targets: [Funi, Munnr, Strengr]
cross_refs:
  - 20_interface/20_MCP_INTEGRATION
  - 20_interface/22_SKILL_INTERFACE
  - 20_interface/23_PROVIDER_INTERFACE
  - 60_synthesis/62_DEPENDENCY_FLOW
  - 60_synthesis/63_INTEGRATION_PATHS
  - 30_execution/32_MULTI_DEVICE_ORCHESTRATION
---

# 21 — RPC Interface: How Hermes Talks to Itself

> *Every system has two languages: the one it speaks to the world and the one it speaks to its own organs. The second one is louder.*
> — Védis Eikleið, observing intra-process voices

## 1. The two RPC vocabularies

Hermes carries on two ongoing RPC conversations that are easy to mistake for the same thing but are architecturally distinct:

1. **Tool dispatch** — the agent loop produces an `assistant_message.tool_calls` list, each entry naming a tool and carrying JSON-encoded arguments. Tool dispatch is *intra-process*: the executor at `agent/tool_executor.py:65-465` runs Python functions in the same address space (sometimes on the same thread, sometimes on a thread pool, sometimes in a subprocess for terminal/computer-use tools).
2. **Gateway transport** — the TUI front-end, the dashboard, and ACP clients all speak JSON-RPC frames to a separate gateway process (`tui_gateway/`) which carries those frames over stdio or WebSocket and dispatches them back into the agent. Gateway transport is *inter-process*: it crosses an actual OS boundary.

These two RPCs share a vocabulary (tool calls, results, approval requests, progress events) but use entirely different *transports*. Hermes models them carefully — the line between "Python function call into the agent" and "JSON frame across a pipe" never blurs. For Ember, who is smaller and wants to stay smaller, this discipline is the lesson.

This doc maps both vocabularies, traces their boundaries, and names the patterns Ember should adopt verbatim.

## 2. The tool-call shape

The contract is established by what flows through `agent/tool_executor.py::execute_tool_calls_*`. Each tool call is an object with three required fields:

```python
tool_call.id            # opaque correlation id — survives every boundary
tool_call.function.name # the tool's registered name (e.g. "read_file", "memory")
tool_call.function.arguments  # JSON-encoded string, parsed at the boundary
```

The agent never trusts `arguments` to be valid JSON. `agent/tool_executor.py:97-101`:

```python
try:
    function_args = json.loads(tool_call.function.arguments)
except json.JSONDecodeError:
    function_args = {}
if not isinstance(function_args, dict):
    function_args = {}
```

A malformed model output (and they happen — every LLM produces invalid JSON eventually) does not crash. It produces a tool call with `{}` as its args, which propagates a clean tool-side error through the same channels as any other failed call. **This is the same coerce-at-the-boundary discipline `mcp_serve.py::_coerce_int` uses outbound; here it is applied inbound from the model.** The principle generalises: every RPC boundary needs a "convert-or-default" step, never an "assume valid".

Tool result messages have a precise shape, established at `agent/tool_dispatch_helpers.py:320-330`:

```python
def make_tool_result_message(name: str, content: Any, tool_call_id: str) -> dict:
    return {
        "role": "tool",
        "name": name,
        "tool_name": name,        # internal — for the FTS index
        "content": content,
        "tool_call_id": tool_call_id,
    }
```

Note the **dual name field**: `name` for the wire protocol (OpenAI Chat Completions schema; Anthropic input_schema; etc.) and `tool_name` for the internal FTS5 index that powers session search. The transport layer at `agent/transports/chat_completions.py:131-141` strips `tool_name` before sending because strict providers (Fireworks, Moonshot/Kimi) reject extra fields. Two-name discipline preserves the internal index without leaking it through the wire. **Ember should adopt this verbatim**: any internal field gets a sentinel naming convention; transports sanitise before sending.

## 3. Sequential vs concurrent dispatch — the parallelism rules engine

`agent/tool_dispatch_helpers.py:103-146` houses the parallelism decision:

```python
def _should_parallelize_tool_batch(tool_calls) -> bool:
    if len(tool_calls) <= 1:
        return False
    tool_names = [tc.function.name for tc in tool_calls]
    if any(name in _NEVER_PARALLEL_TOOLS for name in tool_names):
        return False
    reserved_paths: list[Path] = []
    for tool_call in tool_calls:
        ...
```

The rules are simple, declarative, and live in tiny `frozenset`s at the top of the module (lines 41-56):

```python
_NEVER_PARALLEL_TOOLS = frozenset({"clarify"})

_PARALLEL_SAFE_TOOLS = frozenset({
    "ha_get_state", "ha_list_entities", "ha_list_services",
    "read_file", "search_files", "session_search",
    "skill_view", "skills_list", "vision_analyze",
    "web_extract", "web_search",
})

_PATH_SCOPED_TOOLS = frozenset({"read_file", "write_file", "patch"})
```

The dispatch decision tree:
- **`clarify`** (a user-prompting tool) can never be parallel — it would race UI prompts.
- **Read-only tools** with no shared mutable state are always parallel-safe.
- **Path-scoped tools** (file I/O) are parallel-safe *if their paths don't overlap*. The overlap check is exact, prefix-based, and pessimistic — `/a/b/c` and `/a/b` are treated as overlapping (`agent/tool_dispatch_helpers.py:166-174`).
- **MCP tools** consult the MCP server's advertised capabilities (`_is_mcp_tool_parallel_safe`, lines 90-100).
- **Everything else** is sequential.

The thread pool itself lives at `agent/tool_executor.py:54-57`:

```python
_MAX_TOOL_WORKERS = 8
```

Eight workers, hard cap. On a Pi 5 this is appropriate; on a workstation it could be larger but isn't. The Vow of Smallness implicitly endorses 8.

Each worker is wrapped by a small ceremony at `agent/tool_executor.py:197-271` that:
1. Registers the worker's thread id with the agent so an interrupt can fan out (line 202-208).
2. Applies any pending interrupt to the worker's own tid if a race happened during registration (line 209-213).
3. Propagates the activity callback into the worker's thread-local store (line 218-222).
4. Propagates approval and sudo callbacks into the worker's thread-local store (line 223-234) — without this, dangerous-command prompts deadlock against prompt_toolkit's raw terminal mode (issue #13617 referenced in the source).
5. Restores everything on exit, including clearing any interrupt bit so a recycled worker doesn't inherit stale state.

This is **the most disciplined thread-pool worker prologue I have seen in production agent code.** It is exactly the kind of detail that gets missed in a first-pass implementation and shows up later as "the CLI hangs sometimes." Ember should copy the ceremony verbatim — interrupt fan-out, callback propagation, post-execution cleanup — when she ever introduces a tool worker pool.

## 4. The interrupt protocol

Hermes treats user interrupt as a first-class RPC primitive. The chain:

1. User sends `/stop` or hits Ctrl-C.
2. `agent._interrupt_requested` becomes `True` (atomic flag).
3. Before each tool starts (sequential: `agent/tool_executor.py:474-487`; concurrent: `agent/tool_executor.py:75-83`), the executor checks the flag.
4. If set, **already-pending tool calls get a synthetic "cancelled" message** appended (line 78-83):
   ```python
   messages.append(make_tool_result_message(
       tc.function.name,
       f"[Tool execution cancelled — {tc.function.name} was skipped due to user interrupt]",
       tc.id,
   ))
   ```
5. Running tools see the per-thread interrupt bit (set via `_ra()._set_interrupt(True, tid)`, line 211) and choose to abort cleanly.

The **synthetic cancellation message is critical**: it satisfies the wire protocol's requirement that every `tool_call` produce exactly one `tool_result` with the matching id. Skipping a tool without producing a result poisons the message history. Hermes never skips silently. **Ember's tool framework (ADR 0011) should adopt the same pattern**: every tool call has a guaranteed result, even if the result is an audit-tagged cancellation.

## 5. The gateway transport — Hermes's inter-process JSON-RPC

`tui_gateway/transport.py` defines the abstraction:

```python
@runtime_checkable
class Transport(Protocol):
    def write(self, obj: dict) -> bool:
        """Emit one JSON frame. Return False when the peer is gone."""
    def close(self) -> None: ...
```

Two implementations live in the module:
- `StdioTransport` — wraps `_real_stdout` + `_stdout_lock`, the historical default.
- (Inferable from the broader file) `TeeTransport` — fans out one frame to multiple sinks (used at `tui_gateway/entry.py:33-47` to mirror frames to a dashboard sidebar via WebSocket).

The current transport is tracked in a `contextvars.ContextVar` (line 56-62):

```python
_current_transport: contextvars.ContextVar[Optional[Transport]] = contextvars.ContextVar(
    "hermes_gateway_transport", default=None,
)
```

This means **the transport routing is per-request, not per-process**. A worker thread spawned to handle a JSON-RPC dispatch inherits the ContextVar via `contextvars.copy_context()` and writes back to the correct peer even though many requests are flying in parallel against the same gateway. The pattern is the same one used at `agent/tool_executor.py:291`:

```python
ctx = contextvars.copy_context()
f = executor.submit(ctx.run, _run_tool, i, tc, name, args)
```

**Lesson for Ember**: when a tool worker pool is introduced, use `contextvars.copy_context()` for every submit. `threading.local()` is the wrong primitive — it does not propagate, it shadows. ContextVars are the right primitive — they propagate, they restore, and they work across asyncio and threading boundaries.

## 6. Error semantics: typed-not-thrown

Examine `_PEER_GONE_ERRNOS` at `tui_gateway/transport.py:43-50`:

```python
_PEER_GONE_ERRNOS = frozenset({
    errno.EPIPE, errno.ECONNRESET, errno.EBADF, errno.ESHUTDOWN,
    getattr(errno, "WSAECONNRESET", -1),
    getattr(errno, "WSAESHUTDOWN", -1),
} - {-1})
```

A `BrokenPipeError` or `ConnectionResetError` from `write()` is classified into the set. **Errors in the set mean "peer is gone" — clean disconnect, no log spam.** Errors outside the set mean "real I/O problem" — they re-raise so they surface in the crash log. The two outcomes are clearly different. Hermes does not flatten them into a single exception type.

This is **typed-not-thrown discipline** applied to an RPC boundary. Ember already does it at every realm boundary (per `SYSTEM_VISION.md` §11 Vow of Graceful Offline) — the typed `Disconnected` value flows through Strengr, Funi's `Unavailable`, and the pgvector adapter's eight-reason classification. The gateway transport here is the *same pattern* applied to a different boundary: not realm boundary, but process boundary.

The lesson generalises: **every RPC boundary should classify expected vs unexpected failures.** Expected failures (peer gone, key revoked, model unavailable, well unreachable) flow as typed values. Unexpected failures (programming bugs, OS-level problems) re-raise so they're visible.

## 7. The subagent IPC pattern

The third RPC kind: subagents. `agent/transports/codex_app_server_session.py` and the `delegate_task` tool establish how a *child Hermes agent* communicates with its parent. The pattern (visible without quoting line-for-line):

1. The parent's `delegate_task` tool spawns a *new agent loop* with a fresh session id, a restricted toolset, and a parent_session_id pointer.
2. The child has its own message history, its own context, its own model invocation.
3. The child's final response is returned as the parent's tool result.
4. The parent's memory provider gets an `on_delegation(task, result, child_session_id=...)` callback (per `agent/memory_provider.py:214-225`).

This is **agent-as-microservice** without microservice overhead. The child runs in the same process (or, optionally, in a tui_gateway-backed sandbox). The "RPC" is a Python function call returning a string. The bookkeeping (memory provider callback) preserves traceability without coupling.

For Ember, this is the shape that subagents — if she ever has them — should take. **No new IPC mechanism is needed.** The existing tool-dispatch shape is rich enough: a subagent is just a tool whose result happens to be another agent's terminal output. The Vow of Smallness survives because the only new thing is the `delegate_task` tool and the `on_delegation` callback.

## 8. The transport-abstraction layer for providers

There is a *fourth* RPC dimension I have not yet mapped: the provider transport layer at `agent/transports/base.py:1-90`. This is the abstraction that lets Hermes speak to Anthropic, OpenAI, Bedrock, Codex, and Chat-Completions-compatible providers through one contract. The `ProviderTransport` ABC defines five methods:

```python
@abstractmethod
def convert_messages(self, messages, **kwargs) -> Any: ...
@abstractmethod
def convert_tools(self, tools) -> Any: ...
@abstractmethod
def build_kwargs(self, model, messages, tools=None, **params) -> Dict[str, Any]: ...
@abstractmethod
def normalize_response(self, response, **kwargs) -> NormalizedResponse: ...
def validate_response(self, response) -> bool: return True   # optional
def extract_cache_stats(self, response) -> Optional[Dict[str, int]]: return None  # optional
def map_finish_reason(self, raw_reason) -> str: return raw_reason  # optional
```

This is an RPC because it converts between message formats — the agent's internal "OpenAI-shaped" representation and each provider's wire format. The conversion is *symmetric*: convert outbound, normalize inbound. The `NormalizedResponse` type is the shared return shape — every transport produces it.

For Ember, this is the contract Funi needs (see [[20_interface/23_PROVIDER_INTERFACE]]). The lesson: **provider abstraction is RPC, not adapter pattern.** The five-method shape is unusually clean; copy it.

## 9. Patterns to lift

Boiling all of this down to actionable patterns:

1. **One name per side of every boundary.** Internal field `tool_name`, wire field `name`. Sanitise at the wire.
2. **JSON parsing returns `{}` on failure, never raises.** Same for any type coercion at any RPC boundary.
3. **Every tool call produces exactly one result message**, even on cancellation/interrupt. Synthetic results are how the wire stays consistent.
4. **Parallelism is declarative.** Three small `frozenset`s at module scope replace any rules engine.
5. **`contextvars.copy_context()` on every executor submit.** No `threading.local()` for cross-thread state.
6. **`_PEER_GONE_ERRNOS` is a tiny set.** Classify expected vs unexpected failures; re-raise the unexpected.
7. **Interrupt is a per-thread bit fan-out, not a global flag.** Workers register their tid; interrupt sets the bit on all known worker tids.
8. **Subagent IPC reuses tool-dispatch shape.** No new mechanism needed.
9. **Provider abstraction is a 5-method ABC.** No deeper hierarchy; no plugin framework; no adapter factory.

## What This Means for Ember

**True Names affected:**

- **Funi (flame).** The provider transport ABC (`ProviderTransport`) is exactly the contract Funi needs. Ember already has a `FuniHandle` Protocol with `complete()` and `complete_streaming()`. Adding `convert_messages`, `convert_tools`, `build_kwargs`, and `normalize_response` (the inbound/outbound pair) gives Funi a proper transport layer rather than a single Protocol with each adapter free-styling. Today Ember has only Ollama; tomorrow she'll want LM Studio, llama.cpp HTTP, and maybe a local-MLX runtime — the transport ABC is what makes that proliferation cheap.
- **Munnr (mouth).** The interrupt protocol (per-thread bit fan-out, synthetic cancellation messages) is what Munnr needs the moment any user-facing operation can be interrupted. Today Ember handles Ctrl-C via the Python default and a typed `KeyboardInterrupt` catch at three sites; the next escalation is parallel tool calls, and parallel tools need the Hermes-shaped fan-out.
- **Strengr (cord).** The `_PEER_GONE_ERRNOS` set is the model for how Strengr classifies network failures. The pgvector adapter already has an eight-reason classification per §11 of `SYSTEM_VISION.md`; this is the same pattern applied to a different boundary.

**Vows touched:**

- *Reinforced:* Vow of Modular Authorship (transport ABC isolates provider quirks); Vow of the Unbroken Whole (one name per side prevents wire/internal drift); Vow of Honest Memory (every tool call has a result message; interrupt is recorded, not vanished).
- *Strain test:* Vow of Smallness — eight tool workers and ContextVars are not zero-overhead. On a Pi 5 with no concurrent tool calls, neither cost a thing; with concurrent calls, the overhead is amortised. The cap of 8 is appropriate.

**Specific code-level adoption proposals:**

1. `src/ember/spark/funi/transports/base.py` — new Protocol mirroring Hermes's `ProviderTransport`. Five abstract methods, two optional methods. Single source of truth for what a Funi adapter must provide.
2. `src/ember/spark/funi/tools/dispatch.py` — adopt the `_should_parallelize_tool_batch` rules engine pattern verbatim. The three `frozenset`s at module top, the path-overlap check, the never-parallel list.
3. `src/ember/spark/funi/tools/executor.py` — adopt the worker prologue (thread-id registration, interrupt fan-out, callback propagation, ContextVar copying). This is the file where I'd argue for the most direct Hermes-to-Ember transcription, with names changed.
4. `src/ember/spark/munnr/interrupt.py` — per-thread interrupt bit registry. Today a global `bool` suffices; this is the next-step refactor.
5. `src/ember/thread/strengr/errno_map.py` — `_PEER_GONE_ERRNOS`-shaped classification. Lives in Thread, not Spark, because it's network-shaped.

**Concrete deferral:** the gateway-process layer (`tui_gateway/`) is *out of scope* for Ember's current shape. She has no detached process model. The patterns from that layer (Transport Protocol, ContextVar-routed peer binding, TeeTransport) become relevant only when Ember gains a separate UI process. For now, the gateway lessons stay theoretical — but the *patterns* (typed transport, peer-gone errno set, context-routed fanout) are usable inside Munnr's single-process REPL.

**Cross-platform check:** All of the above is pure stdlib. `concurrent.futures.ThreadPoolExecutor`, `contextvars`, `errno`, `threading`. No platform-specific paths required. Cross-platform plan §"Process / Signal / IO" already verified zero-POSIX-only-imports for Ember today; adopting these patterns does not change that.

**Cross-references:**
- The MCP server boundary (external RPC) is in [[20_interface/20_MCP_INTEGRATION]].
- The skill-discovery contract that depends on the tool-dispatch shape is in [[20_interface/22_SKILL_INTERFACE]].
- The provider-side ABC is detailed in [[20_interface/23_PROVIDER_INTERFACE]].
- The end-to-end dependency flow that follows a tool call from model output to result message is in [[60_synthesis/62_DEPENDENCY_FLOW]].
- The execution-layer doc on parallelism and concurrency is in [[30_execution/32_MULTI_DEVICE_ORCHESTRATION]] (Forge's territory; cross-link).

---
codex_id: 62_DEPENDENCY_FLOW
title: Dependency Flow — Hermes End-to-End and Ember's Analogue
role: Cartographer
layer: Synthesis
status: draft
hermes_source_refs:
  - run_agent.py
  - agent/conversation_loop.py
  - agent/context_engine.py
  - agent/prompt_builder.py
  - agent/transports/base.py:1-90
  - agent/transports/chat_completions.py
  - agent/tool_executor.py:65-465
  - agent/tool_dispatch_helpers.py
  - agent/memory_manager.py
  - hermes_state.py
  - gateway/run.py
  - mcp_serve.py:450-859
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 60_synthesis/60_HERMES_VS_EMBER_CROSSWALK
  - 60_synthesis/63_INTEGRATION_PATHS
  - 20_interface/21_RPC_INTERFACE
  - 20_interface/23_PROVIDER_INTERFACE
  - 10_domain/11_AGENT_CORE
---

# 62 — Dependency Flow: From Word to Word

> *Trace the river from where it falls to where it returns. Do not look at the eddies; look at the channel.*
> — Védis Eikleið, walking a single turn end to end

## 1. The single-turn premise

A turn is: an operator (or peer) speaks; the agent listens, reasons, consults, possibly acts, and answers. Both Hermes and Ember care about exactly this loop. The structure of the loop is the dependency flow. This doc traces it through Hermes, then through Ember as Ember exists today, then shows the analogue points where Hermes patterns can slot into Ember without re-routing the river.

## 2. The Hermes single-turn flow (current state)

Reading the call chain from `run_agent.py` → `agent/conversation_loop.py` → the transports:

```
[1]  Operator types a message in CLI (cli.py) OR a platform event arrives (gateway/run.py)
        │
        ▼
[2]  Gateway / CLI normalises to a "user message" dict and appends to messages[]
        │
        ▼
[3]  AIAgent.run_turn() called
        │
        ▼
[4]  Pre-turn: memory_manager.prefetch_all(user_message)
       │   - calls each registered MemoryProvider.prefetch(query)
       │   - returns formatted recall context, injected as a system note
        │
        ▼
[5]  Context engine: agent.context_engine.assemble(messages, recall_context, …)
       │   - applies prompt_builder rules
       │   - applies prompt_caching rules
       │   - applies developer-role-vs-system-role swap per provider
       │   - may invoke context_compressor for old messages
        │
        ▼
[6]  Provider transport.build_kwargs(model, messages, tools, **params)
       │   - ProviderProfile.prepare_messages() — provider-specific cleanup
       │   - transport.convert_messages() — OpenAI shape → provider shape
       │   - transport.convert_tools() — OpenAI tool schema → provider schema
       │   - ProviderProfile.build_extra_body() — provider-specific kwargs
        │
        ▼
[7]  Credential pool.acquire(provider) returns a runtime credential
       │   - rotation strategy decides which credential
       │   - exhausted credentials are skipped
       │   - OAuth refresh if needed
        │
        ▼
[8]  Provider SDK call (anthropic.messages.create / openai.chat.completions.create / boto3 / …)
       │   - retry_utils handles transient failures
       │   - rate_limit_tracker observes 429s and feeds credential pool
        │
        ▼
[9]  Raw response from provider
        │
        ▼
[10] transport.normalize_response(response) → NormalizedResponse
       │   - parse content blocks (text, thinking, tool_use)
       │   - map finish_reason
       │   - collect reasoning_details in provider_data
       │   - extract cache stats
        │
        ▼
[11] If finish_reason != "tool_calls": EXIT-A (text reply path)
     If finish_reason == "tool_calls":
       │
       ▼
[12] Tool executor.execute_tool_calls_*(assistant_message, messages, …)
       │   - _should_parallelize_tool_batch() decides serial vs parallel
       │   - per tool: parse args (default {} on failure)
       │   - per tool: pre-call hook (plugin block message)
       │   - per tool: guardrail check (allow / deny / approval prompt)
       │   - per tool: checkpoint snapshot for file-mutating tools
       │   - tool runs (in thread pool if parallel)
       │   - per tool: result captured, post-call hook
       │   - per tool: make_tool_result_message appended to messages[]
        │
        ▼
[13] Loop back to step [4] (next iteration of the agent loop)
       │   - the model sees the tool results
       │   - reasons again
       │   - may answer (finish_reason='stop') or call more tools
        │
        ▼
[14] When finish_reason='stop': EXIT-A (final text reply)
       │
       ▼
[15] Post-turn: memory_manager.sync_all(user_msg, assistant_response)
       │   - each MemoryProvider.sync_turn(user, asst) persists
       │   - background queue, not blocking
        │
        ▼
[16] Post-turn: memory_manager.queue_prefetch_all(user_msg)
       │   - prepares the next turn's recall
        │
        ▼
[17] Session DB write: hermes_state.SessionDB.append_message(*)
       │   - SQLite with FTS5 index
       │   - audit log entry for any approval/tool use
        │
        ▼
[18] Render reply to CLI / Send to platform gateway
       │
       ▼
[19] EXIT
```

Nineteen distinct stages, four of them potentially iterative (the tool loop at 12-13). Each stage has a clear owner: gateway, agent, context engine, transport, credential pool, retry, tool executor, memory manager, session DB.

The thing to notice: **the flow is linear with two loops** (tool loop, retry loop). It is not a graph. It is a pipeline with feedback edges. This is what makes it understandable.

## 3. The Ember single-turn flow (current state, after slice 2)

Reading from `src/ember/spark/munnr/chat.py` → `src/ember/spark/funi/handle.py` → `src/ember/well/brunnr/`:

```
[1]  Operator types a message in CLI: munnr.chat.read_input()
        │
        ▼
[2]  Munnr appends to in-memory window (recent Episodes)
        │
        ▼
[3]  Munnr calls brunnr.hybrid_search(query=user_msg) via the BrunnrHandle Protocol
       │   - Strengr wraps the call; returns typed Disconnected on failure
       │   - if Disconnected: skip retrieval, mark "ungrounded reply"
        │
        ▼
[4]  Funi.prompt.assemble(system_text, recent_episodes, retrieval_hits, user_msg,
                          well_disconnected=False|True)
       │   - "do not invent" injected when well_disconnected
       │   - operator's line appended last
        │
        ▼
[5]  Funi.handle.complete_streaming(prompt) — single Ollama adapter today
       │   - returns Iterator[FuniStreamChunk]
       │   - Funi-Unavailable returned as typed value if Ollama unreachable
        │
        ▼
[6]  Munnr renders chunks incrementally
       │   - tool-call chunks (from slice 2's tool framework) trigger approval
       │   - text chunks stream to terminal
        │
        ▼
[7]  If tool call:
       │   - approval policy checked (standing trust + per-call prompt)
       │   - audit log entry created
       │   - tool invoked (search_well | read_local_file | fetch_url)
       │   - tool result appended to messages
       │   - back to step [4]
        │
        ▼
[8]  When stream finishes with no tool call: render citations if grounded
        │
        ▼
[9]  Persist Episode: brunnr.add_episode(user, assistant, citations, audit_refs)
       │   - non-fatal on Brunnr disconnect
        │
        ▼
[10] EXIT
```

Ten stages. The pipeline is *the same shape* as Hermes's nineteen, condensed because Ember has no provider abstraction yet (one adapter), no credential pool (one secret resolver), no memory provider plugin (Brunnr is the memory), no platform gateway (just CLI), no context compressor (window is bounded).

The shape match is striking and not accidental — Ember was designed by an architect who knew agents. The Hermes patterns slot into Ember's existing positions without re-routing because *the positions are already there*.

## 4. The slot-by-slot mapping

| Hermes step | Owner | Ember step | Owner | Notes |
|---|---|---|---|---|
| [1] CLI/gateway input | gateway/cli | [1] CLI input | Munnr | Ember's gateway is "Gjallarhorn (reserved)" per [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] |
| [2] Normalize to message | gateway/cli | [2] Append to window | Munnr | shape: `{"role":"user","content":...}` in both |
| [3] AIAgent.run_turn() | agent loop | (implicit) | Munnr → Funi | Ember is in-line; Hermes has an object |
| [4] memory_manager.prefetch_all | memory_manager | [3] brunnr.hybrid_search | Brunnr | Hermes calls *providers*; Ember calls *Brunnr*; Vinátta (reserved) is the future provider layer |
| [5] context_engine.assemble | context_engine | [4] funi.prompt.assemble | Funi | Ember collapses context engine into Funi's prompt module today; expand if size warrants |
| [6] transport.build_kwargs | transport | (today: direct Ollama call) | Funi | This is where the [[20_interface/23_PROVIDER_INTERFACE]] gap lives |
| [7] credential_pool.acquire | credential_pool | (today: file/env read) | Strengr | This is where the [[20_interface/23_PROVIDER_INTERFACE]] §6 gap lives |
| [8] Provider SDK call | transport | [5] funi.complete_streaming() | Funi | Both are HTTP-level invocations |
| [9] Raw response | transport | (streaming chunks) | Funi | Streaming is the v2 default for both |
| [10] transport.normalize_response | transport | (parse Ollama-shape) | Funi | Ember's parsing is inline; same logical step |
| [11-13] Tool loop | tool_executor | [7] Tool approval+invoke | Funi tools | Hermes's executor is 910 lines; Ember's is ~150 today |
| [14] Final reply | agent loop | (stream end) | Munnr | Same termination shape |
| [15] memory_manager.sync_all | memory_manager | [9] brunnr.add_episode | Brunnr | Hermes routes through providers; Ember writes Brunnr directly |
| [16] queue_prefetch | memory_manager | (n/a today) | Brunnr | Could become a cheap optimisation in slice 5 |
| [17] Session DB write | hermes_state | (subsumed by [9]) | Brunnr | Ember's Brunnr-episode-table is the session DB |
| [18] Render / send | render / gateway | [8] Munnr render | Munnr | Same |

Eighteen Hermes stages mapped to ten Ember stages with no missing concept and no orphaned step. Six Hermes stages collapse into Ember-internal logic (credential pool, context engine, memory provider, session DB, prefetch queue, normalisation as a separate step) because Ember's scale makes the separation premature.

## 5. The fan-out points

There are three places in the Hermes flow where the linear pipeline forks into parallel work:

### 5.1 Concurrent tool execution

`agent/tool_executor.py:280-340` — when `_should_parallelize_tool_batch` returns true, the executor spawns a thread pool. The fan-out:

```
[12] Tool dispatch (parallel)
       │
       ├─── thread 1: read_file
       ├─── thread 2: search_files
       ├─── thread 3: web_search
       └─── thread 4: session_search
              │
              ▼ (gather)
       results merged in original tool-call order
       │
       ▼
       continue at [13]
```

This is the parallelism rules engine (per [[20_interface/21_RPC_INTERFACE]] §3). Each branch is independent; the rejoin point is deterministic.

### 5.2 Background recall + audit writes

`agent/memory_manager.py::sync_all` (line ~50, design intent visible from docstring at lines 1-24) — sync writes happen on background threads to avoid blocking the next turn. The agent loop *does not wait* for sync; it queues and continues.

```
[15] sync_all
       │
       └─── background thread: each provider.sync_turn(...)
                │
                ▼
              (independent of main loop completion)
```

Similarly, audit-log writes (per `tools/tool_result_storage.py::maybe_persist_tool_result`) happen on the main thread but with a non-blocking commit semantic.

### 5.3 MCP event bridge

`mcp_serve.py:204-444` — when Hermes is *publishing* an MCP server, a daemon thread polls SessionDB every 200 ms. This thread is independent of any agent turn:

```
(main agent thread)         (event bridge daemon thread)
    │                              │
    │                              ▼
    [turn iteration]               poll sessions.json + state.db (mtime gated)
    │                              │
    │                              ▼
    │                              detect new messages → enqueue events
    │                              │
    │                              ▼
    │                              wake any waiting MCP clients
```

Two fully independent threads sharing SQLite via mtime detection. No locks, no IPC. The simplicity is the point.

## 6. Ember's fan-out points (current and future)

Ember today has **one** fan-out: streaming Funi runs in its own logical thread (it's actually an iterator, but consumers and renderers are independent in their event loop). No tool parallelism. No background sync. No event bridge.

Hermes-imported fan-out candidates, in priority order:

| # | Fan-out | Where it lands in Ember | Adopting from | Why now |
|---|---|---|---|---|
| 1 | Concurrent tool execution | `funi/tools/executor.py` | `agent/tool_executor.py` | Reduces wall-clock for batches like "read these three files" |
| 2 | MCP event bridge | `munnr/mcp/event_bridge.py` | `mcp_serve.py` | Only if MCP server lands; cheap addition |
| 3 | Background Episode persistence | `brunnr/sqlite_vec/adapter.py` | `memory_manager.sync_all` | Already partly here (post-turn write); could be background |
| 4 | Background recall prefetch | `brunnr/.../prefetch.py` | `memory_manager.queue_prefetch_all` | Defer; only useful at higher retrieval cost |
| 5 | Parallel skill bundle injection | `funi/skills/surfacer.py` | (no Hermes analogue at this scale) | Defer |

## 7. The crucial discipline — `contextvars` across every fan-out

Hermes's `agent/tool_executor.py:288-293`:

```python
ctx = contextvars.copy_context()
f = executor.submit(ctx.run, _run_tool, i, tc, name, args)
```

And `tui_gateway/transport.py:54-62`:

```python
_current_transport: contextvars.ContextVar[Optional[Transport]] = contextvars.ContextVar(
    "hermes_gateway_transport", default=None,
)
```

ContextVars carry per-request state (the current transport, the active task id, the approval session key) across thread boundaries via `copy_context()`. This is the **right primitive**; `threading.local()` would shadow the parent, not propagate.

For Ember, this means: as soon as fan-out #1 (concurrent tool execution) lands, every executor submit *must* use `contextvars.copy_context()`. Without it, the audit log's "which turn am I writing for" gets confused on parallel tool calls. The pattern is small but critical — the kind of thing that gets missed in a v1 and discovered later as a subtle correctness bug.

## 8. The error edges

Every linear step has at least one error edge. The Hermes flow handles them as:

| Stage | Failure | Hermes response |
|---|---|---|
| [4] memory prefetch | provider down | empty recall context, log warning, continue |
| [6-7] transport / credential | 401 | credential pool marks exhausted, picks another |
| [6-7] transport / credential | 429 | same, with timer-respecting cooldown |
| [8] SDK call | network | retry_utils backs off |
| [10] normalize | malformed | `validate_response` returns False → retry |
| [11-13] tool execution | tool raises | result captured as error string, append to messages, model sees error |
| [15] memory sync | provider down | log, continue (sync is best-effort) |
| [17] SessionDB | disk full | log, continue (Ember's Vow of Honest Memory same posture) |

The pattern: **typed errors are continued; truly unexpected errors are logged and re-raised**. Hermes is good at this. Ember inherits the discipline by virtue of her existing typed-`Disconnected`/`Unavailable` model — every Hermes-imported flow stage gets the same treatment automatically.

## 9. The asymmetric edge — when Hermes publishes MCP

Recall `mcp_serve.py`'s ten tools. When Hermes is the *MCP server*, the turn flow looks different — there *is no* operator-typed message, *is no* CLI render. The flow:

```
[1] MCP client calls mcp.tool(name=conversations_list, args={...})
[2] FastMCP routes the call to the registered Python function
[3] Function reads SessionDB / channel directory / sessions.json
[4] Function returns JSON string
[5] FastMCP wraps in MCP response, writes to stdio
[6] MCP client receives
```

There is no provider, no transport, no LLM call, no tool loop. **MCP-as-server is a read-mostly surface over Hermes's accumulated state.** This is what makes it cheap. The only state mutations are `messages_send` (which routes through the platform gateway's send path) and `permissions_respond` (which writes the bridge's approval state).

For Ember, this informs the [[60_synthesis/63_INTEGRATION_PATHS]] proposal: an Ember MCP server is a **read-mostly view of Brunnr + audit log**. Writes are gated. The flow is short, the cost is small, the value is high.

## 10. The cross-platform flow check

Every step in §3 (Ember's current flow) is cross-platform-clean per [[CROSS_PLATFORM_PLAN]] §"Verified clean catalogue". Every step in §2 (Hermes's flow) has at least one bit that is *more platform-specific* than Ember would tolerate:

- Step [11-13] tool executor: terminal tool uses POSIX-favoured patterns (TTY detection, sudo prompts); Ember's tool framework explicitly excludes terminal tool from default install.
- Step [17] session DB: SessionDB is SQLite; cross-platform; matches Ember's Brunnr.
- Step [18] gateway delivery: per-platform, each its own cross-platform story; Ember's CLI-only default sidesteps the issue.

When Ember adopts Hermes's flow points, the cross-platform check is **per step**, not whole-flow. Most steps come for free; some (tool executor's terminal subset; any future Gjallarhorn platform plugin) require their own platform sweep.

## 11. The "slot-in" diagram

The Ember target flow, after the high-value Hermes-imports are made:

```
[1]  Munnr.input()
        │
        ▼
[2]  brunnr.hybrid_search()              ← Strengr-wrapped; typed Disconnected
        │
        ▼
[3]  funi.skills.surface(recall_context, user_msg)  ← NEW from Hermes skills port
        │
        ▼
[4]  funi.prompt.assemble(...)
        │
        ▼
[5]  funi.transport.build_kwargs(...)    ← NEW from Hermes provider abstraction
        │
        ▼
[6]  strengr.credential.acquire(...)     ← NEW from Hermes credential pool
        │
        ▼
[7]  funi.transport.invoke(...)          ← NEW pattern; one adapter still
        │
        ▼
[8]  funi.transport.normalize(...)       ← NEW from Hermes NormalizedResponse
        │
        ▼
[9]  if tool calls:
       │
       ├─── funi.tools.dispatch.parallelize_or_not(...)  ← NEW from Hermes parallelism rules
       │       │
       │       ▼
       │     [parallel tool execution with ContextVar copy]  ← NEW
       │       │
       │       ▼
       │     append tool results, loop to [4]
       │
       ▼
[10] munnr.render() with citations
        │
        ▼
[11] brunnr.add_episode(...)             ← unchanged
        │
        ▼
[12] (background) brunnr.queue_prefetch(...)   ← LATER, deferred
        │
        ▼
[13] EXIT
```

The migration goes from "Ember has 10 stages" to "Ember has 13 stages, three of them new and Hermes-imported." Each new stage is *small* and *additive* — none break the existing pipeline.

## What This Means for Ember

**True Names affected:**
- **Funi.** Three new submodules slot into the flow: `funi/transport/` (build_kwargs, normalize), `funi/skills/` (surface step before prompt assembly), `funi/tools/dispatch.py` (parallelism rules). All three are *additive*; none replace existing Funi code, they intercept and extend.
- **Strengr.** One new submodule: `strengr/credential.py`. Single-credential first; pool later. Slots cleanly into step [6].
- **Brunnr.** No structural change. Background prefetch (`brunnr/prefetch.py`) is a *future* optional optimisation.
- **Munnr.** Render path unchanged. MCP-server channel (proposed in [[20_interface/20_MCP_INTEGRATION]]) is an *alternate flow*, not a modification of the operator-flow.
- **Hjarta, Smiðja.** Unchanged.

**Vows touched:**
- *Reinforced:* Vow of the Unbroken Whole — every new step has clear in/out shapes; no fragments.
- *Reinforced:* Vow of Modular Authorship — each new step is independently testable and independently failable.
- *Reinforced:* Vow of Graceful Offline — typed values flow through every new step (Strengr's credential.acquire returns `CredentialReady | Unavailable`; Funi's transport.invoke wraps the LLM call with `Disconnected` semantics).
- *Watch:* Vow of Smallness — each new step adds 100-300 lines. The total target after these slot-ins: ~3500-5000 lines of new code across Funi/Strengr. Ember stays well under Hermes's 200 MB.

**Concrete sequence (sketch for [[60_synthesis/64_MIGRATION_PLAN]]):**
1. **Phase M1** — slot in skill surface (step [3]). Small; standalone; no dependency on other phases.
2. **Phase M2** — slot in provider transport split (steps [5] [7] [8]). Refactor Ollama into the transport shape; no behaviour change.
3. **Phase M3** — slot in MCP server (alternate flow, parallel pipeline). Read-only first.
4. **Phase M4** — slot in tool parallelism (step [9]). Requires ContextVar discipline.
5. **Phase M5** — slot in credential pool (step [6]). Single-credential per provider; multi-credential rotation later.
6. **Phase M6** — slot in MCP client (Funi tools that talk to external MCP servers). Largest payoff per line; smallest port-surface.

**Cross-platform check:** every new step is stdlib + already-shipped deps. No new platform-specific path. ContextVars are 3.7+. ThreadPoolExecutor is stdlib. The `tempfile.NamedTemporaryFile`+`os.replace()` atomic-write pattern already in use.

**Cross-references:**
- [[60_synthesis/63_INTEGRATION_PATHS]] gives the concrete file-by-file integration for each slot-in.
- [[60_synthesis/64_MIGRATION_PLAN]] sequences the phases.
- [[20_interface/21_RPC_INTERFACE]] details the parallelism rules and ContextVar discipline.
- [[20_interface/23_PROVIDER_INTERFACE]] details the provider/transport split.
- [[10_domain/11_AGENT_CORE]] (Architect's territory) deep-dives `agent/conversation_loop.py` and `run_agent.py`.

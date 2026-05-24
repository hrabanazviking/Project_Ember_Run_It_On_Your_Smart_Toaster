---
codex_id: LETTA_AGENT_LOOP
title: Letta's Agent Loop — step / inner_step / chaining via heartbeats
role: Forge
layer: Execution
peer_targets: [Letta]
status: draft
peer_source_refs:
  - letta:letta/agent.py:752-855
  - letta:letta/agent.py:857-1050
  - letta:letta/agent.py:299-442
  - letta:letta/agent.py:444-750
  - letta:letta/agent.py:96-176
  - letta:letta/constants.py
  - letta:letta/helpers/__init__.py
ember_subsystem_targets: [Funi, Brunnr, Smiðja]
hermes_codex_refs:
  - 30_execution/30_SELF_HEALING_LOOP
  - 30_execution/35_TRAJECTORY_COMPRESSION
  - 30_execution/38_PERSISTENT_MEMORY
cross_refs:
  - 30_execution/CROSS_AGENT_LOOP_TRIANGULATION
  - 30_execution/LETTA_MEMORY_OPERATIONS
---

# Letta's Agent Loop

The Hermes loop is a single conversational turn that calls tools and persists messages on commit. The Letta loop is *the same shape with two consequential additions*: a **heartbeat-driven chain** that keeps the agent ticking even when there is no user input, and a **memory rebuild step** wedged at the top of every iteration. I'm Eldra. I read all 1,758 lines of `letta/agent.py` so you can read the 80 that matter. Then I'll tell you what Funi steals and what Funi refuses.

## The Shape: step → inner_step → _get_ai_reply → _handle_ai_response

`step()` at `letta/agent.py:752` is the outer driver. It's a `while True` that calls `inner_step()` until one of three conditions holds: no heartbeat requested, max chaining steps exceeded, or chaining disabled. Everything interesting flows from this:

```python
# letta/agent.py:775-849 (abridged)
while True:
    kwargs["first_message"] = False
    kwargs["step_count"] = step_count
    kwargs["last_function_failed"] = function_failed
    step_response = self.inner_step(messages=next_input_messages, ...)

    heartbeat_request = step_response.heartbeat_request
    function_failed = step_response.function_failed
    token_warning = step_response.in_context_memory_warning
    ...

    if not chaining:
        break
    elif max_chaining_steps is not None and counter > max_chaining_steps:
        break
    elif token_warning and summarizer_settings.send_memory_warning_message:
        next_input_messages = [<token-limit warning as user message>]
        continue
    elif function_failed:
        next_input_messages = [<FUNC_FAILED_HEARTBEAT_MESSAGE as user message>]
        continue
    elif heartbeat_request:
        next_input_messages = [<REQ_HEARTBEAT_MESSAGE as user message>]
        continue
    else:
        break
```

The pattern: every iteration produces an `AgentStepResponse` carrying three flags — `heartbeat_request`, `function_failed`, `in_context_memory_warning`. Each maps to a *synthetic next user message* that re-enters the loop. The loop ends only when none of the three flags fire. This is the engine that makes Letta agents capable of running autonomously: the agent can request its own next tick by setting `request_heartbeat=True` on any tool call.

## The Heartbeat: the True Architectural Innovation

The heartbeat is what separates Letta from a stateless chat agent. It is *not* a scheduler tick. It is a self-requested continuation. Look at `letta/agent.py:562-577`:

```python
heartbeat_request = function_args.pop("request_heartbeat", None)

if isinstance(heartbeat_request, str) and heartbeat_request.lower().strip() == "true":
    heartbeat_request = True
if heartbeat_request is None:
    heartbeat_request = False
if not isinstance(heartbeat_request, bool):
    self.logger.warning(...)
    heartbeat_request = False
```

Every tool call schema in Letta has an injected `request_heartbeat` parameter (see `runtime_override_tool_json_schema` at `letta/services/helpers/tool_parser_helper.py`). When the agent calls a tool, it decides — in its tool-call arguments — whether the loop should run again immediately. There are *also* implicit heartbeat-forcing conditions baked into the loop:

- **`function_failed=True`** forces a heartbeat (`letta/agent.py:821-833`) — the agent gets a synthetic message saying "function failed, what now?"
- **Tool rules with children** force a heartbeat (`letta/agent.py:739`) — if the rules solver says this tool has follow-on tools, the loop continues.
- **"Continue" tool rule** forces a heartbeat (`letta/agent.py:746-747`).
- **Terminal tool rule** suppresses heartbeats (`letta/agent.py:741-742`).

This is the most important thing to internalize about Letta: *the agent loop is driven by the agent's own self-issued tick requests, plus rule-derived overrides*. Compare with Hermes's `conversation_loop`, which terminates after every user turn unless explicit follow-ups are queued. Letta keeps going.

## The Memory Rebuild: Step 0 of Every inner_step

Read `letta/agent.py:878-885`:

```python
# Step 0: update core memory
# only pulling latest block data if shared memory is being used
current_persisted_memory = Memory(
    blocks=[self.block_manager.get_block_by_id(block.id, actor=self.user) for block in self.agent_state.memory.get_blocks()],
    file_blocks=self.agent_state.memory.file_blocks,
    agent_type=self.agent_state.agent_type,
)  # read blocks from DB
self.update_memory_if_changed(current_persisted_memory)
```

Every single iteration starts by pulling the latest block contents from PostgreSQL/SQLite and comparing them with the in-memory `Memory` object. If they differ, the system prompt is rebuilt. This is necessary because:

1. Memory tools (`core_memory_append`, `memory_replace`, etc.) edit DB rows, not the live system prompt.
2. Other agents sharing the same memory blocks may have written between this tick and the previous one.
3. Sleep-time agents (background memory consolidators) may have rewritten blocks.

The cost is one DB round-trip per agent tick. The benefit is **memory consistency across concurrent agents and across reboots**. Hermes does not have this because Hermes's memory is in-process (curator-managed) and not multi-tenant. Ember's Brunnr is pluggable storage; if multiple Ember instances share a Well, they need this rebuild-on-tick discipline.

## The Retry Pattern in _get_ai_reply

`letta/agent.py:354-442` is the LLM call. It wraps the actual `LLMClient.send_llm_request` in an empty-response-retry loop with jittered exponential backoff:

```python
# letta/agent.py:354-425 (abridged)
for attempt in range(1, empty_response_retry_limit + 1):
    try:
        response = llm_client.send_llm_request(...)
        if len(response.choices) == 0 or response.choices[0] is None:
            raise ValueError(f"API call returned an empty message: {response}")
        if response.choices[0].finish_reason not in ["stop", "function_call", "tool_calls"]:
            if response.choices[0].finish_reason == "length":
                raise RuntimeError("Finish reason was length (maximum context length)")
            else:
                raise ValueError(f"Bad finish reason from API: {response.choices[0].finish_reason}")
    except ValueError as ve:
        if attempt >= empty_response_retry_limit:
            raise Exception(f"Retries exhausted ...")
        else:
            delay = min(backoff_factor * (2 ** (attempt - 1)), max_delay)
            time.sleep(delay)
            continue
    ...
```

Only `ValueError` is retried — `RuntimeError` (context-length exhausted) is *not retried*, instead it triggers an immediate `summarize_messages_inplace()` (line 434-436). This is a much narrower retry posture than Hermes's `error_classifier.py` taxonomy. Letta classifies errors into "empty/bad finish" → retry, "length" → summarize, "everything else" → propagate. Hermes classifies into ~12 buckets with provider-specific rules. Letta's approach is small and adequate; Hermes's is comprehensive.

## The Tool Rules Solver

`self.tool_rules_solver` (initialized at `letta/agent.py:116`) governs *which tools can be called next*. The solver carries:

- `init_tool_rules` — must run on step 0.
- `terminal_tool_rules` — when run, kill the chain.
- `continue_tool_rules` — force heartbeat after.
- "Children" tool rules — when tool X runs, only tool set Y is allowed next.

At `letta/agent.py:320-326`, before each LLM call, the solver narrows the tool list:

```python
allowed_tool_names = self.tool_rules_solver.get_allowed_tool_names(
    available_tools=available_tools, last_function_response=self.last_function_response
) or list(available_tools)

# Don't allow a tool to be called if it failed last time
if last_function_failed and self.tool_rules_solver.tool_call_history:
    allowed_tool_names = [f for f in allowed_tool_names if f != self.tool_rules_solver.tool_call_history[-1]]
    if not allowed_tool_names:
        return None
```

Two patterns of note:

1. **Tool-failed-last-time exclusion**: the very tool that just failed is removed from the allowed set for the next call. If that empties the set, the agent returns early. This is a primitive form of error backoff — Hermes's `error_classifier` handles this at the *provider* level, Letta handles it at the *tool* level. Both are correct for different layers.
2. **Force-tool-call**: if only one tool is allowed, that tool is forced (`letta/agent.py:351-352`). If the rule says "this is the init tool," it is forced on the first message.

## The Persist-Every-Step Discipline

`save_agent(self)` is called at `letta/agent.py:798` after *every* step. This is heavy — it serializes the full agent state to DB on each iteration. The tradeoff is honest: crash recovery means resuming exactly where you were. Letta is server-deployed; sessions can be hours long; users can attach and detach. Persisting state per step is the cost of paid-for resumability.

Hermes does *not* persist per-step; Hermes persists *transactionally* per conversation completion (see `conversation_loop.py`). The difference reflects deployment shape: Hermes is short-session, Letta is long-session.

## The Context-Window Guardrail

`letta/agent.py:432-436` and `letta/agent.py:957-972`:

```python
# check if we are going over the context window
if response.usage.total_tokens > self.agent_state.llm_config.context_window:
    self.summarize_messages_inplace()

# ... later in inner_step ...
if current_total_tokens > summarizer_settings.memory_warning_threshold * int(self.agent_state.llm_config.context_window):
    # emit memory_pressure_warning, set agent_alerted_about_memory_pressure
```

Two thresholds: a *warning* threshold (default ~80%) that triggers a synthetic user message warning the agent "you are using too many tokens" *as part of the heartbeat loop*, and a *hard* threshold that triggers in-place summarization. The agent literally gets told "you're approaching context limits" via the loop, which lets it make memory decisions (e.g., `archival_memory_insert`) before context overflows. This is conversational backpressure as architecture.

Hermes's [[hermes_codex/30_execution/35_TRAJECTORY_COMPRESSION]] handles trajectory compression via the curator. Letta's approach is to *tell the agent itself* about memory pressure and let it decide. The Vow of Honest Memory says Letta is closer to right here — the agent should know its limits.

## What's NOT in Letta's Loop (Notable Absences)

- **No provider failover.** `LLMClient.create` selects exactly one provider; on hard errors, the loop dies. Compare to Hermes's `credential_pool.py` + `error_classifier.py`.
- **No streaming-first design.** Streaming is a bolt-on flag. The loop is built around `ChatCompletionResponse`, not deltas.
- **No multi-tool-call-per-turn.** Line 470-474: `if response_message.tool_calls is not None and len(response_message.tool_calls) > 1: ... self.logger.warning(">1 tool call not supported, using index=0 only")`. Letta refuses to parallelize tools within a step. Goose handles parallel tool calls natively (see `crates/goose/src/agents/agent.rs:1841-1929`).
- **No interrupt mechanism.** No equivalent to smolagents's `self.interrupt_switch` or Goose's `CancellationToken`. The agent runs until heartbeats stop.

## What This Means for Ember

Funi is Ember's local LLM runtime — the loop owner. The Letta loop teaches Funi six concrete things:

1. **Adopt the heartbeat pattern (Vow of Honest Memory + Tethered Grounding).** Funi's loop should accept agent-requested continuations. When the agent calls a memory tool, it can request a follow-on tick to let it observe the result of its own edit. Implementation: inject `request_heartbeat` into every tool schema at runtime, just like `runtime_override_tool_json_schema` does at `letta/agent.py:333-338`. Pi-friendly: heartbeats cost one extra LLM call per requested tick — opt-in, not default.

2. **Adopt memory-rebuild-on-tick — but bounded (Vow of Honest Memory).** Funi reads from Brunnr at the top of each tick. If the Well has been edited (by Smiðja's ingest pipeline, or by another Ember instance, or by a human directly), the agent sees it. Cost: one Brunnr query per tick. For Pi tier, batch this — every N ticks, not every tick. Add a `memory_rebuild_interval` knob.

3. **Refuse Letta's persist-every-step.** Per-step persistence is a workstation-tier behavior. Pi tier persists per-conversation-end. This is a Vow-of-Smallness decision: the SQLite write pressure on a class-10 SD card is real.

4. **Adopt the tool-rules-solver, but trimmed.** Init / terminal / continue is a clean 3-state machine. Drop "children" rules — they encode too much workflow logic for what should be a thin runtime. If a recipe wants workflows, that belongs in a Goose-style Recipe (see [[30_execution/GOOSE_RECIPE_AUTHORING]]).

5. **Adopt the failed-tool-exclusion-from-allowed-set pattern.** This is one line of code that prevents the agent from re-calling the same broken tool in a tight loop. Cheap. Free. Adopt.

6. **Adopt context-window backpressure via synthetic user message.** When Funi sees the conversation is nearing the context window, inject a system message that tells the agent "you are nearing your context limits, consider consolidating memory." This is *the agent making the memory decision*, not Smiðja or a curator quietly compressing things. Honors Vow of Honest Memory.

**True Names affected:** Funi (loop owner), Brunnr (memory rebuild), Smiðja (notified-of-pressure rather than silently-compressing).

**Hermes Codex docs reinforced:** [[hermes_codex/30_execution/30_SELF_HEALING_LOOP]] (Letta's failed-tool-exclusion is a self-healing primitive); [[hermes_codex/30_execution/38_PERSISTENT_MEMORY]] (Letta's memory rebuild is a different solution to the same problem); [[hermes_codex/30_execution/35_TRAJECTORY_COMPRESSION]] (Letta agrees with Hermes that compression must happen but disagrees on *who decides*).

**Hermes Codex docs contradicted:** Hermes's curator silently compresses; Letta's agent is told. The Vow of Honest Memory leans toward Letta. We should revisit [[hermes_codex/30_execution/35_TRAJECTORY_COMPRESSION]] in light of this.

**Anti-pattern noted:** Do not adopt single-tool-call-per-turn. Goose's parallel tool execution (next doc in this series) is strictly better for an interactive agent. Letta's restriction is a legacy of the function_call era.

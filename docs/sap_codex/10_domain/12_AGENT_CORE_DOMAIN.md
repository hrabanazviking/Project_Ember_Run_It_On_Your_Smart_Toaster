---
codex_id: 12_AGENT_CORE_DOMAIN
title: Agent Core Domain — Where the Reasoning Should Have Lived
role: Architect
layer: Domain
status: draft
sap_source_refs:
  - py/agent.py:1-66
  - py/sub_agent.py:1-367
  - py/task_center.py:1-235
  - py/scheduler.py:1-134
  - py/task_tools.py:1-100
  - server.py:2400-2700
  - server.py:5350-5400
ember_subsystem_targets: [Strengr, Funi]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/19_TOOL_DOMAIN
  - 10_domain/1C_SCHEDULER_DOMAIN
  - 30_execution/31_PYTHON_SERVER
  - 60_synthesis/60_TRUE_NAME_REASSIGNMENT
---

# Agent Core Domain
## Where the Reasoning Should Have Lived

*— Rúnhild Svartdóttir, Architect*

> *The hall is named for the chief who lives in it. When you walk into the hall and the chief is missing, the structure of the hall tells you why he is missing. Sometimes he never came home from raid. Sometimes he was never there to begin with.*

The agent core in SAP is a domain by absence. The file you would expect to be the conversation loop — `py/agent.py` — is sixty-five lines of project-config tool-allowlist code (`py/agent.py:1-66`). The real "agent" lives in three places: in `server.py:2400-6000` (the streaming chat handler), in `py/sub_agent.py` (the long-running task executor), and in the scheduler that orchestrates the two. This doc names that displaced kingdom.

---

## 1. The Subject Itself

**What the domain is *meant* to be:** the reasoning kernel — the conversation loop, the tool dispatcher, the iteration budgeter, the memory hand-off, the error classifier. The room where the agent *thinks*.

**What the domain *actually* is in SAP:** a four-file complex.

| File | LOC | What it actually owns | What it should have owned |
|---|---|---|---|
| `py/agent.py` | 65 | `.party/config.json` per-project tool allow-list | The conversation loop |
| `py/sub_agent.py` | 367 | `SubAgentExecutor` — long-running task runner that HTTP-calls back into `server.py:/v1/chat/completions` | A real sub-agent kernel |
| `py/task_center.py` | 233 | `TaskCenter` — per-workspace task store, file-backed (`.agent/tasks/*.json`), one lock | Task lifecycle is real here; the file is honest |
| `py/scheduler.py` | 134 | `AgentScheduler` — 30-second polling loop scanning task files for `pending` + time/cycle triggers | Schedule + dispatch is real here too |
| `server.py:2400-6000` | ~3600 | The actual conversation loop — system-prompt building, tool composition, streaming, side-effect trailers | This should be a Python module, not a route handler trailer |

Two of the four files are crisp and worth keeping. Two of the four are misnamed for what they do. And the *real* reasoning lives in the route handler of a 12k-line monolith. The agent core is **a void with a coastline**.

---

## 2. How It Works

### 2.1 The misnamed file: `py/agent.py`

`py/agent.py:1-66` is two functions:

```python
# /tmp/super-agent-party/py/agent.py:9-27
def is_tool_allowed_by_project_config(cwd: str, tool_name: str) -> bool:
    config_path = _get_project_config_path(cwd)
    if not config_path.exists():
        return False
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            allowed_tools = data.get("allowed_tools", [])
            return tool_name in allowed_tools
    except Exception as e:
        print(f"[Config Error] Failed to read .party config: {e}")
        return False
```

That is the entire file's load-bearing purpose. It reads a project-local `.party/config.json` and asks: "is this tool whitelisted here?" It has nothing to do with agency, reasoning, models, conversations, tools (beyond gating), or memory. The file is named `agent.py` because — looking at the import at `server.py:211` — it is the gate `server.py` checks before running a tool. The misnomer is symptomatic: when the actual agent lives in `server.py`, every helper near it gets named like it is the agent.

### 2.2 The sub-agent: `py/sub_agent.py`

`py/sub_agent.py:21` defines `SubAgentExecutor`. Its purpose: run a *long* task without occupying the user-facing chat. The pattern:

1. `SubAgentExecutor(workspace_dir, settings)` (line 24) holds endpoints `chat_endpoint = f"http://127.0.0.1:{self.port}/v1/chat/completions"` (line 29) and `simple_chat_endpoint` (line 30).
2. `execute_subtask(task_id, consensus_content)` (line 32) loads the task from `TaskCenter`, builds a system prompt, opens an `httpx.AsyncClient(timeout=600)`, and loops up to `max_iterations` (default 100, line 39).
3. Each iteration: call the chat endpoint as a stream, update task progress, then run a *separate* "is this done yet?" simple-chat call (`_check_task_completion_smart`, line 347).
4. On completion, finalize the task record (`_finalize_task_record`, line 105) — archive results in `results_history` (capped at 20, line 118), trim conversation history to 30 messages (line 121), decide if the task should re-pend (cycle/scheduled) or close.
5. Push the result to **every configured platform** (lines 165-214) — the result is broadcast to `ws_manager` (web), and to each IM platform's handler registered with `global_behavior_engine`. The push is a *fake behavior trigger*: `BehaviorItem(enabled=True, trigger=..., action=BehaviorAction(type="prompt", prompt=f"【自主任务汇报】..."))` (lines 187-203). The same handler that runs scheduled greetings runs task results.

This is genuinely interesting. The sub-agent is a *network client* of the main server, not a library consumer. That means:

- It can run in any process (today: same process, asyncio task).
- It can outlive the conversation that spawned it.
- It can be cancelled (`TaskStatus.CANCELLED` checked at lines 60, 144) without unwinding the conversation.
- It speaks the same OpenAI-compat wire format as everything else.

It also means:
- Two HTTP round-trips per "is it done?" check (the main stream + the simple_chat poll).
- A 600-second timeout on the streaming client — generous, but not infinite, and the failure path is silent.
- Sub-agent → main server traffic is *unauthenticated localhost*.

The completion-check is genuinely funny: it asks a *separate* LLM call "判断任务目标是否已达成？只回YES/NO" (`py/sub_agent.py:348`) and parses the reply for "YES". This is **vibe-driven termination**. There is no test, no validator, no assertion — the second LLM is the judge. If it says NO when the answer was YES, the loop continues until `max_iterations` is hit.

### 2.3 The task center: `py/task_center.py`

`py/task_center.py:63` defines `TaskCenter` per-workspace. It stores tasks as individual JSON files in `<workspace>/.agent/tasks/<task_id>.json`, guards updates with a single `asyncio.Lock`, and exposes `create_task`, `get_task`, `update_task_progress`, `list_tasks`, `cancel_task`, `delete_task`. Tasks are validated by Pydantic (`SubTask` at line 35) with statuses `pending / running / completed / failed / cancelled` (line 28) and types `once / scheduled / recurring` (line 23).

`get_task_center(workspace_dir)` (line 231) is a process-scoped cache: one `TaskCenter` per workspace path. This is correct — the lock semantics depend on it.

Two interesting features:

- **CANCELLED is sticky** (line 144): once cancelled, a task refuses to transition to anything but cancelled. This is a small piece of state-machine discipline missing elsewhere.
- **Progress is monotonic** (line 158): `final_progress = max(task.progress, safe_progress)` — progress can only go up unless the status is COMPLETED (forces 100) or FAILED (preserves). No reset.

The file is small, crisp, and tested-by-being-used. It is the second-cleanest module in SAP after `py/vts_manager.py`.

### 2.4 The scheduler: `py/scheduler.py`

`py/scheduler.py:7` defines `AgentScheduler(settings_ref)`. The settings are passed by reference so `cc_path` (CLI workspace path) changes are seen at the next tick (line 16). `start_loop` (line 12) polls every 30 seconds (line 22). `_scan_and_trigger` (line 24) walks all tasks, filters to `PENDING`, and for each:

- **Time-trigger** (`t_type == "time"`, lines 42-60): match `current_time_hm` against `config.timeValue[:5]` (HH:MM); if `days` is set, require weekday match. Avoid same-minute re-fire by storing `last_trigger_minute`.
- **Cycle-trigger** (`t_type == "cycle"`, lines 62-86): use `next_run_at` (stored in task context); fire if `now >= next_run_at`; check `isInfiniteLoop` or `ran_count < repeatNumber`; auto-complete when capped.

`_execute` (line 88) flips the task to RUNNING and spawns `run_subtask_in_background` as a fire-and-forget asyncio task. No await; the scheduler keeps polling.

Two small flaws:

- The 30-second poll is wall-clock; a missed minute is missed (the next scan will not retry within the same minute). Acceptable for chat but not for industrial scheduling.
- `_update_next_cycle_time` (line 117) uses `cycle_str` parsed as `HH:MM:SS` directly, but treats it as a duration. There is no validation against negative or zero durations.

### 2.5 The conversation loop in `server.py`

This is the elephant. From `server.py:2400` to roughly `6000` is the streaming `/v1/chat/completions` handler. It does:

- Parse `ChatCompletionRequest`
- Pull `settings = await load_settings()`
- Walk through every subsystem flag and conditionally inject system-prompt text:
  - Memory pull (~`server.py:2440`)
  - Sticker pack
  - Text-to-image hint (`server.py:2553`)
  - VRM expression/motion (`server.py:2556-2575`)
  - VTube Studio (`server.py:2580-2606`)
  - Affection (`server.py:2609-2673`)
  - autoBehavior tool (`server.py:3553`)
  - A2UI rendering (`server.py:2675`)
- Compose tools from 14+ sources (`server.py:3353-3420`)
- Pick the model adapter (Claude-as-OpenAI / Gemini-as-OpenAI / Dify / OpenAI SDK)
- Open the stream, forward chunks, accumulate `full_content`
- Run side-effect trailers (affection extract, memory infer, TTS, broadcast)

The function is **the entire missing module**. Extracting it is the single highest-impact refactor SAP could undertake.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The reasoning loop has no error classifier

When the model stream fails mid-stream (`py/sub_agent.py:326` and the equivalent in `server.py`), the handling is `except: continue`. No taxonomy. No retry policy. No error type. Contrast with Hermes which has `agent/error_classifier.py` as a first-class module (see [[hermes:11_AGENT_CORE]]).

### 3.2 Iteration budget is implicit

`max_iterations = self.settings.get("CLISettings", {}).get("max_iterations", 100)` (`py/sub_agent.py:39`). One number, one setting, no per-task budget, no fallback model after budget exhaustion. SAP's reasoning has no escape hatch.

### 3.3 The vibe-judged completion check

`_check_task_completion_smart` (`py/sub_agent.py:347-355`) asks a separate model "YES/NO" whether the task is done. The result is whatever the model felt that turn. The check happens every iteration after the main turn — so a 100-iteration task is **200 LLM calls** (100 work + 100 judge). The cost is doubled to enable judging that is vibe-driven anyway.

### 3.4 HTTP self-loop without auth

`py/sub_agent.py:29` builds `chat_endpoint = f"http://127.0.0.1:{self.port}/v1/chat/completions"`. There is no API key on the loopback. Anyone on the local machine — every other process, every browser tab pointing at `127.0.0.1`, every container with host networking — can call SAP's chat endpoint. This is fine for desktop trust; it is **lethal** if SAP is ever exposed beyond localhost (which the Docker compose variant invites at `docker-compose.yml`).

### 3.5 Task history is JSON-on-disk per task

`py/task_center.py:78` stores each task as a separate JSON file. For a small workspace this is fine. For a workspace with hundreds of recurring tasks this is `list_tasks` doing a `glob("*.json")` and reading every file (line 193). There is no index. There is no compaction. The Pluggable Storage Vow (in [[ember:RULES.AI.md]]) would refuse this.

### 3.6 The scheduler scan misses subminute precision

30-second poll, minute-resolution trigger. SAP cannot schedule a behavior at 13:45:30 — only at 13:45. For chat-paced behavior this is fine. For livestream cues (which SAP also does) this is sloppy.

### 3.7 The crisp survivors

`py/task_center.py` and `py/scheduler.py` are 367 lines combined and they are *honest*. They could lift into Ember almost verbatim. They are what `py/agent.py` *should* have been.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §5.1 for the Server-Eaten Codebase anti-pattern
- [[1C_SCHEDULER_DOMAIN]] for the scheduler's role in the autonomous-timing fabric
- [[19_TOOL_DOMAIN]] for the tools the loop dispatches
- [[20_interface/22_A2A_INTERFACE]] for how sub-agents could speak peer-to-peer instead of HTTP-self-loop
- [[30_execution/31_PYTHON_SERVER]] for the Forge's deep dive into `server.py`
- [[60_synthesis/60_TRUE_NAME_REASSIGNMENT]] for the Strengr revisions this codex proposes
- [[hermes:11_AGENT_CORE]] for what an extracted agent kernel looks like
- [[peer:LETTA-1_SHAPE]] for Letta's reasoning loop comparison

---

## What This Means for Ember

**Adopt:**
- `py/task_center.py` *whole*, including the CANCELLED-sticky invariant (line 144) and the monotonic progress rule (line 158). Translate to Strengr's task surface. This is the cleanest task store I have seen in any AI agent framework.
- `py/scheduler.py`'s **separation of scan from dispatch** (the 30s poll filters PENDING; `_execute` flips state and spawns). Strengr's scheduler should follow the same shape.
- The **per-workspace task isolation** (`get_task_center(workspace_dir)` at line 231) — Ember's per-Realm task scope should mirror this. One TaskCenter per Realm; never global.

**Adapt:**
- SAP's **HTTP-self-loop** for sub-agent → main reasoning. Adapt to Ember's **MCP-self-loop** ([[20_interface/20_MCP_INTEGRATION]]): the sub-agent calls Ember's *own* MCP server surface (which is typed, audited, schema-enforced) instead of unauthenticated `127.0.0.1:port`. Same decoupling, none of the auth-laundering.
- The **multi-platform result push** of `py/sub_agent.py:165-214` (broadcast a task result to WS + every registered IM platform) — adapt as Ember's `Sögumiðla` event bus: a `task_completed` event with platform-target metadata, consumed by whichever surfaces are subscribed.
- The **vibe-judged completion check** — adapt as Ember's **typed completion signal**: tools emit a `finish_task` tool call with a structured `success` boolean and `reason` field, rather than asking a second LLM "YES/NO". Hermes uses this; Ember should too.
- `py/agent.py`'s per-project tool allowlist — adapt as Ember's per-Realm permission manifest, with Defended System Prompt typing (no string concatenation; no eval).

**Avoid:**
- **Naming a file `agent.py` when it is not the agent.** Ember names by True Name. The reasoning loop lives in `strengr/` and is named for what it does.
- **A single `max_iterations` setting governing every reasoning loop.** Per-task budgets; per-class budgets; per-Realm budgets. Different tasks have different appropriate ceilings.
- **One JSON file per task on disk** as the storage model. Use the Brunnr-pluggable storage surface; SQLite for local; pluggable for remote. The Pluggable Storage Vow forbids hard-coding the backend.
- **Localhost-loopback with no auth.** Ember treats `127.0.0.1` as an externally addressable surface (per the user's standing preference for tailnet-addressable services with proper auth). The sub-agent surface authenticates even on localhost.
- **Same-minute resolution scheduling** as the only mode. Ember offers seconds-precision triggers when the host can afford them; tier-collapse to minute precision on Pi.

**Invent:**
- **The Reasoning Kernel as Its Own Module.** Ember refuses the Server-Eaten anti-pattern at the start. `strengr/loop.py` owns the conversation loop. It has no FastAPI route registration. The route handler in Munnr's HTTP surface is a thin transport adapter that hands the request to Strengr and yields the result. The split is enforced by import direction: Strengr never imports Munnr.
- **The Sub-Agent Realm.** Where SAP runs the sub-agent in-process and HTTP-calls back, Ember spawns the sub-agent as a *Realm* — a separate process with its own Funi entrypoint, its own Strengr loop, its own Brunnr connection. Realms communicate via MCP. This is the [[60_synthesis/62_PARTY_PROTOCOL]] applied at the smallest scale. A Realm can be on the same host, another host, or a low-power peer (the Pi case).
- **The Completion Witness.** Instead of asking a second LLM "is it done?", every long-running task in Ember declares an **acceptance predicate** at creation — a typed assertion the result must satisfy. The predicate is checked by code, not vibes. If no predicate is supplied, the task is `open-ended` and stops only on explicit `finish_task` or iteration cap.
- **Tasks-as-Capabilities.** A SAP sub-agent is a *thing the main agent dispatches*. An Ember sub-agent-Realm is a *named capability* — `analyse-saga`, `triage-inbox`, `compose-letter` — with a typed input schema, an audit trail, and a Realm-scoped tool whitelist. The capability outlives the task. Reusable; introspectable; revocable.

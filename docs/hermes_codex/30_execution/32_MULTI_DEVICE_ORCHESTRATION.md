---
codex_id: 32_MULTI_DEVICE_ORCHESTRATION
title: Multi-Device Orchestration — Isolated Subagents and Swarm Patterns
role: Forge
layer: Execution
status: draft
hermes_source_refs:
  - tools/delegate_tool.py:1-50
  - tools/delegate_tool.py:329-1170
  - tools/delegate_tool.py:1918-2050
  - agent/iteration_budget.py:1-62
  - run_agent.py:2276-2300
  - run_agent.py:3831-3870
  - agent/conversation_loop.py:1652-1660
ember_subsystem_targets: [Funi, Strengr, Smiðja, Munnr]
cross_refs:
  - 30_execution/33_HOT_COLD_TIERS
  - 30_execution/37_SCHEDULING_DELEGATION
  - 30_execution/40_SERVERLESS_HIBERNATION
  - 60_synthesis/63_INTEGRATION_PATHS
---

# Multi-Device Orchestration

Most agents do one thing at a time. Hermes will, if you ask, spawn ten of itself, send each one a different piece of a problem, and wait for them all to finish. The spawn happens in a `ThreadPoolExecutor` (the parent's process), each child is a *fully isolated AIAgent* with its own terminal sandbox, its own iteration budget, its own toolset, and its own task_id. The parent never sees the child's intermediate state — only the summary that comes back. This is the pattern that lets Hermes "harvest many devices when available."

I'm Eldra. I'm going to walk you through the actual mechanics of `tools/delegate_tool.py` (which is the multi-device-on-one-machine story), then propose what an Ember-shaped swarm looks like when extra devices ARE on the table — without ever demanding that they be.

## The Hermes Subagent Pattern

`tools/delegate_tool.py:1-17`:

> "Delegate Tool — Subagent Architecture. Spawns child AIAgent instances with isolated context, restricted toolsets, and their own terminal sessions. Supports single-task and batch (parallel) modes. The parent blocks until all children complete."

Every child gets four isolations:

1. **Fresh conversation.** No parent message history. The child's context begins with a focused system prompt + the delegated goal + caller-supplied context.
2. **Own task_id.** Drives a separate terminal sandbox (cwd, env, shell state) and a separate file-operations cache. Children cannot trip over each other's `cd` or each other's recent `read_file` cache hits.
3. **Restricted toolset.** Configurable per delegation, with a hard-coded blacklist:

```python
# tools/delegate_tool.py:42-50
DELEGATE_BLOCKED_TOOLS = frozenset([
    "delegate_task",   # no recursive delegation
    "clarify",         # no user interaction
    "memory",          # no writes to shared MEMORY.md
    "send_message",    # no cross-platform side effects
    ...
])
```

4. **Own iteration budget.** `agent/iteration_budget.py:1-62` makes this explicit: "The parent's budget is capped at `max_iterations` (default 90). Each subagent gets an independent budget capped at `delegation.max_iterations` (default 50) — this means total iterations across parent + subagents can exceed the parent's cap."

The fourth point is the cleverest. A child's budget can't be siphoned from the parent's by an enthusiastic recursive delegation, but the *aggregate* compute scales with the number of children. If the parent spawns 5 children at 50 iterations each, the system as a whole can do up to 90 + 250 = 340 tool-calling steps of work, while each individual agent remains bounded.

## Concurrency Control

`_get_max_concurrent_children()` at line 329 reads `delegation.max_concurrent_children` from `config.yaml`. The default is 3. The cap is enforced in two places:

**At decision time** (`run_agent.py:2276`):

```python
def _cap_delegate_task_calls(tool_calls: list) -> list:
    """Truncate excess delegate_task calls to max_concurrent_children.

    Models occasionally emit multiple separate delegate_task tool_calls
    in one turn. We truncate so the LLM doesn't over-commit.
    """
    max_children = _get_max_concurrent_children()
    delegate_count = sum(1 for tc in tool_calls if tc.function.name == "delegate_task")
    ...
```

If the model decides to spawn 7 subagents in one turn but the cap is 3, only the first 3 survive. The remaining 4 are dropped with a logged warning. The model gets feedback in its next turn (the 4 missing tool results are absent), and adapts.

**At spawn time** (line 2001):

```python
max_children = _get_max_concurrent_children()
# Validation: refuse to spawn beyond the cap; queue or error.
```

A defense-in-depth pattern. The decision-time cap is a hint; the spawn-time cap is the enforcer.

## The Spawn Itself

`tools/delegate_tool.py:1918` is `def delegate_task(...)`. Lines 1960–1980 set up:

- `_delegate_depth` on the child (parent's depth + 1) — prevents recursion (the blocklist removes `delegate_task` for children, but depth tracking is belt-and-suspenders).
- A fresh task_id (UUID).
- A fresh `IterationBudget(delegation.max_iterations)`.
- A fresh terminal sandbox via the file_state module.
- A scoped subset of tools (configurable, minus the blocklist).

The spawn uses `ThreadPoolExecutor` from `tools/delegate_tool.py:26-29`. Each child runs `child.run_conversation(...)` in its own thread. Children share the same Python process but their `task_id` keeps every piece of mutable state separate.

Lines 1140 establish `child._delegate_depth = child_depth`, so the child knows how deep it is. Children at depth N > 1 should not exist — the blocklist removes `delegate_task` for children — but if a tool somehow bypasses the blocklist, the depth check catches it.

## How the Parent Blocks

Two clean lines in `agent/conversation_loop.py:1652-1660`:

```python
# Propagate interrupt to any running child agents (subagent delegation)
```

If the user hits Ctrl-C in the parent, the parent walks its child list and sends each one the same interrupt. Children check for the interrupt at their loop iteration boundaries and exit cleanly with a typed "interrupted by parent" result.

The result-collection pattern is:

```python
with ThreadPoolExecutor(max_workers=max_children) as ex:
    futures = [ex.submit(_run_child, task) for task in tasks]
    results = []
    for fut in as_completed(futures, timeout=overall_timeout):
        try:
            results.append(fut.result())
        except FuturesTimeoutError:
            results.append({"error": "timed out"})
```

The parent gets back a list of summaries. Each summary is the child's final assistant message (usually a one-paragraph "Done, here's what I did"). The parent's context never sees the child's tool calls, intermediate reasoning, or partial outputs. **The child is a black box from the parent's point of view, and the parent is offline from the child's point of view.** Isolation is mutual.

## What this gives Hermes

Three workload shapes Hermes handles well that single-loop agents do not:

1. **Embarrassingly parallel subtasks.** "Review these 10 PRs" → spawn 10 children, each reviewing one. Wall-clock time drops from 10× to ~1×.
2. **Long-running cleanup with checkpointing.** "Refactor every file in this directory" → batch into 5 children of 20 files each, with the children's iteration budgets independent.
3. **Specialist routing.** "Solve this math problem AND this design problem" → spawn one child with the math toolset, one with the design toolset. Each child has tighter context, fewer tools to reason over, less prompt-token bloat.

The cost is that all of it happens in one process, on one machine. Hermes does not natively distribute across multiple devices. If you have a workstation AND a Pi, Hermes runs on one or the other, not both.

## What's Missing for a Real Swarm

A true multi-device pattern needs:

1. **Discovery.** "Find the devices on my network running Ember."
2. **Health/capability registration.** "This device has 16GB RAM and a 3090; this one has 4GB and ARM."
3. **Dispatch.** "Route this task to the most appropriate device."
4. **Result collection.** "Aggregate the partial results."
5. **Graceful no-extra-device fallback.** "If no other devices, do it locally."

Hermes has step 5 by default (it just runs locally). It has 4 internally (via `ThreadPoolExecutor`). It lacks 1, 2, and 3.

The TUI gateway (`tui_gateway/server.py`) is interesting here. It shows Hermes already knows how to host a backend that another Hermes can connect to over websockets. But the connection direction is "user laptop UI → remote Hermes brain," not "agent A → agent B as a peer." Re-pointing this transport from human-driven to agent-driven is a real, small lift away.

## What This Means for Ember

The hard rule from the brief: any multi-device pattern **must never demand more than one device**. Single-device must be the default, and the default must work fully. Extras are opportunistic harvest, not architectural assumption.

That rules out a centralized orchestrator. Rules out a mandatory broker. Rules out anything that fails closed if a peer isn't found. Ember's swarm must fail *open*: when no peers are found, the work happens locally; when peers are found, the work splits.

### Proposed Ember swarm shape — "Strengr Mesh"

Strengr is already Ember's network-aware subsystem. Extend Strengr to know about *peers*, not just *Wells*. The shape:

**Discovery.** Use mDNS/Bonjour (or, on Tailscale-equipped networks, the Tailscale device list). Strengr broadcasts `_ember._tcp` with a TXT record containing capability hints (`tier=pi5`, `funi=llama3.2:3b`, `well=local`, `version=0.x.y`). Listening Embers see each other. No central server.

**Health/capability registration.** Each Ember publishes a tiny `/strengr/health` JSON endpoint (already implied by the existing tether):

```json
{
  "host": {"name": "pi5", "ram_mb": 4096, "has_gpu": false},
  "funi": {"backend": "ollama", "model": "llama3.2:3b", "ready": true},
  "brunnr": {"backend": "sqlite_vec", "well_size_chunks": 35124},
  "smiðja": {"queue_depth": 0},
  "version": "0.x.y"
}
```

Peers poll each other on a slow heartbeat (60s). If a peer disappears for two heartbeats, it's marked offline. No silent zombies.

**Dispatch.** Two clear primitives in Munnr/Smiðja:

```python
# src/ember/strengr/mesh.py
@dataclass(frozen=True)
class Peer:
    host: str
    port: int
    capabilities: dict[str, Any]
    last_seen_at: float

class StrengrMesh:
    def peers(self) -> list[Peer]: ...
    def find_peer(self, *, requires: dict[str, Any]) -> Peer | None: ...
    def dispatch_task(
        self,
        task: TaskSpec,
        *,
        prefer_local: bool = True,
        timeout: float = 60.0,
    ) -> TaskResult: ...
```

`dispatch_task` with `prefer_local=True` (the default) is the swarm's Vow-of-Smallness anchor. If the local Ember can run the task, it does. Only when the local Ember is busy AND a peer with matching capabilities is available does work cross the network.

**Result collection.** Mirror Hermes's `as_completed` pattern. The mesh returns `TaskResult` objects; failures are typed (`PeerOffline`, `TaskTimeout`, `RemoteError`). The parent code never has to know whether a task ran locally or remotely. This is exactly the same pattern Hermes uses for delegate_task — same shape, just with an extra hop in the middle.

**Fallback.** Every mesh call must accept `fallback="local"`:

```python
result = mesh.dispatch_task(spec, fallback="local")  # always succeeds if local can run it
```

When no peer satisfies the requirements, the local Ember runs the task in-process the same way it would have without the mesh. Single-device Ember works exactly as it does today.

### When the swarm becomes worth it

Three concrete Ember workloads benefit from harvesting extra devices:

1. **Smiðja ingest.** When the user runs `ember well ingest ~/Documents`, the ingest is embarrassingly parallel at the chunk level. A workstation peer with a CUDA-accelerated embedder can chew through chunks 50× faster than the Pi. The Pi dispatches chunks; the workstation embeds; both write back to a shared Brunnr (or sync via Brunnr's pluggable backend).
2. **Curator pass.** [[30_execution/30_SELF_HEALING_LOOP]] proposes running curator on Funi by default. On a Pi, that's slow. If a workstation peer is available, dispatch the curator review there.
3. **Background research.** "Ember, research X and tell me what you find" → a deep tool-using subtask. Best run on a peer with more RAM and faster network. Pi initiates; workstation executes; Pi receives the synthesis.

In each case, the user with only a Pi gets the same feature — just slower. The user with a Pi + workstation gets a much faster experience. **No feature is gated on owning extras.** That's the Vow.

### Implementation slice

Slice 1 (minimum viable): discovery only. `ember mesh status` shows peers found. No dispatch yet. This unlocks visibility.

Slice 2: dispatch with mandatory `fallback="local"`. Smiðja becomes the first caller — embed a chunk locally or remotely, same return type.

Slice 3: capability matching. The dispatcher selects peers by requirements (e.g. "has_gpu=true, ram_mb>=8000"). Curator becomes the second caller.

Slice 4: the Bifröst viewer ([[reference_bifrost]]) gets a peer-aware view. Show the swarm as a constellation. (Optional, beauty layer.)

### Iteration budget — borrow verbatim

`agent/iteration_budget.py` is 62 lines of pure mechanics. Copy it as `src/ember/spark/funi/budget.py`:

```python
class IterationBudget:
    def __init__(self, max_total: int): ...
    def consume(self) -> bool: ...
    def refund(self) -> None: ...
    @property
    def used(self) -> int: ...
    @property
    def remaining(self) -> int: ...
```

The locking primitive (`threading.Lock`) is cross-platform. The semantics (consume returns False when exhausted; refund undoes a consume) are exactly the right shape for any cap-and-release pattern. This is one of the smallest, sharpest pieces of code in Hermes, and Ember should steal it without modification.

### Delegate-blocklist for Ember subagents

If Ember ever supports local subagent spawning (a future PRD might want this for Smiðja batch jobs), the blocklist pattern from `tools/delegate_tool.py:42` is non-negotiable. Children must never get:

- `mesh.dispatch_task` (no recursive swarm spawning)
- `well_write` (no concurrent writes to Brunnr — only the parent holds the write lock)
- `user_input` (no prompting the user from a subagent)
- `mesh.discover` (no cascading discovery storms)

Encode it as a frozenset constant. Make it survive code review.

### Vows on the line

- **Vow of Smallness** — strengthened. Mesh is optional; local-only is the default; capability checks ensure a Pi-only user gets the same features.
- **Vow of Modular Authorship** — strengthened. The mesh module fails atomically: if discovery fails, the rest of Ember runs unchanged.
- **Vow of Graceful Offline** — strengthened. Mesh peers can be offline; tasks fall back to local.
- **Vow of Tethered Grounding** — preserved. The Well is still the source of truth. Mesh dispatch doesn't change *what* an agent answers, only *which device computes the answer*.
- **Vow of Public-Friendliness** — at risk if mesh setup requires manual peer config. Mitigation: mDNS-by-default + an explicit `ember mesh enable` opt-in. No surprise networking.

### What I do not propose

I do NOT propose:
- A central broker (would create a single point of failure).
- A REST-or-gRPC peer API (mDNS + JSON-over-HTTP is enough).
- Distributed transactions (Brunnr writes stay local-or-routed; eventual consistency for the index).
- Encryption-by-default in v1 (Ember runs on a user's home network; explicit "mesh secure" opt-in for hostile networks).

### Where to read next

- [[30_execution/33_HOT_COLD_TIERS]] — how `Host` capabilities feed dispatch.
- [[30_execution/37_SCHEDULING_DELEGATION]] — the broader scheduling story.
- [[60_synthesis/63_INTEGRATION_PATHS]] — sequenced PRs to land Strengr Mesh.

You can't forge with one hand. You can with one machine, but more hands hammer faster. — Eldra.

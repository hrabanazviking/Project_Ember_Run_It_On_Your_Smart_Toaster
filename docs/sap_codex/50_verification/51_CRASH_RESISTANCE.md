---
codex_id: 51_CRASH_RESISTANCE
title: Crash Resistance — Per-Subsystem Failure Modes And What Each Takes Down
role: Auditor
layer: Verification
status: draft
sap_source_refs:
  - py/live_router.py:21-27
  - py/comfyui_tool.py:62-67
  - py/mcp_clients.py:111-134
  - py/know_base.py:127-164
  - py/scheduler.py:12-22
  - py/behavior_engine.py:115-142
  - server.py (referenced)
ember_subsystem_targets: [Funi, Strengr, Smiðja, Brunnr, Munnr]
cross_refs:
  - 50_verification/50_SELF_HEALING_PATTERNS
  - 50_verification/57_FAILURE_TAXONOMY
  - 50_verification/58_OBSERVABILITY_GAPS
---

# Crash Resistance — Per-Subsystem Failure Modes And What Each Takes Down

> *Sólrún, voice cold and even: a crash is not a single event. It is a tree of cascading effects. Every subsystem that crashes takes down some neighbors and leaves others standing. Mapping the dependency tree is the only way to know what your operator will actually experience.*

This document walks SAP subsystem by subsystem, names the dominant crash modes for each, and traces what each crash takes down with it. The goal is not exhaustive bug-hunting — that is `[[57_FAILURE_TAXONOMY]]`. The goal here is **dependency mapping under failure**: when X dies, what dies with it?

The default mental model in most code reviews assumes processes are atomic. They are not. SAP's process has eight IM-bot threads, three livestream threads/tasks, FastAPI's main loop, the scheduler loop, the behavior engine loop, every MCP client's monitor task, and ad-hoc tool-execution tasks. Each is a potential crash domain.

---

## 1. The Single Process — One Roof Over Many Loops

SAP runs as one Electron renderer + one Python process. Inside the Python process:

- **Main event loop** — FastAPI on uvicorn, hosting REST + WebSocket
- **Per-IM-bot thread × 8** — each with its own asyncio loop
- **Bilibili livestream thread × 1** — its own loop (when enabled)
- **YouTube livestream thread × 1** — synchronous polling, no loop
- **Twitch task × 1** — runs on the main loop
- **MCP client monitor task × N** — each on the main loop
- **Behavior engine task × 1** — on the main loop
- **Scheduler task × 1** — on the main loop (`scheduler.py:12-22`)
- **Sub-agent executor tasks × N** — on the main loop (`sub_agent.py`)
- **SleepGuard thread × 1** — separate thread, OS API calls

That's at minimum a dozen concurrent execution contexts when SAP is at full configuration. The dependency graph is dense.

---

## 2. What Crashing The Main Loop Does

The main loop hosts FastAPI, every async task, the behavior engine, the scheduler, every MCP client monitor, and the Twitch task. If the main loop dies (e.g. uvicorn crashes):

- **Lost immediately**: HTTP API, WebSocket fan-out, all async tasks, MCP heartbeats, behavior engine, scheduler, Twitch ingest, sub-agent execution
- **Continues briefly**: Per-IM-bot threads (each has its own loop) — but their handlers call back into the main process through HTTP at `127.0.0.1` (verified in `sub_agent.py:28-30` constructing `base_url = f"http://127.0.0.1:{port}"`). With main loop dead, the HTTP calls fail. IM bots will see connection-refused and log errors.
- **Continues until OS reaps**: Bilibili thread, YouTube thread, SleepGuard

Effective blast radius: complete UX loss within ~30 seconds, full process recycle required.

Why the main loop dies in practice: most likely cause is uncaught exception in a non-task-wrapped coroutine. FastAPI catches handler exceptions; what it doesn't catch is exceptions in tasks created via `asyncio.create_task` without `add_done_callback` for error logging.

Audit shows `live_router.py:147` creates `twitch_task = asyncio.create_task(start_twitch_task(...))` and never adds a done callback. If `start_twitch_task` raises after launch, the exception sits in the task object, never logged unless someone awaits it. The user sees "Twitch silently stopped working" with no log.

---

## 3. IM Bot Crash — Per-Platform Isolation

Each IM bot manager runs in its own thread (e.g. `telegram_bot_manager.py:60-67`). The thread runs `loop.run_until_complete(main_startup())`. If `main_startup()` raises:

```python
# /tmp/super-agent-party/py/telegram_bot_manager.py:88-93
            except Exception as e:
                if not self._stop_requested:
                    self._startup_error = str(e)
                self._startup_complete.set()
                self._ready_complete.set()
```

Captured, stored as `self._startup_error`. The thread exits cleanly. The manager's `get_status()` returns `is_running=False, startup_error=<message>`. The UI must poll status to detect this.

**Blast radius:** One IM platform offline. Other seven continue.

**Caveat:** The `global_behavior_engine` is a *singleton* shared across all eight managers. If the IM bot's crash happened during a registered behavior dispatch, the `handler` callback inside the engine is still registered. Next behavior tick will call the now-dead handler. The handler's call to its bot manager will see `is_running=False` and presumably error — but the engine doesn't know to deregister.

`behavior_engine.py:218-222`:

```python
# /tmp/super-agent-party/py/behavior_engine.py:218-222
                if trigger_chats:
                    for chat_id in set(trigger_chats):
                        if chat_id:
                            logging.info(f"[BehaviorEngine] 命中规则 {idx}，准备推送到 {platform}:{chat_id}")
                            asyncio.create_task(handler(chat_id, behavior))
```

`asyncio.create_task(handler(...))` — fire-and-forget. If the handler raises (because the bot is dead), the exception sits in the task object. No `add_done_callback`. No log beyond what the handler itself prints.

So the *symptom* of an IM-bot crash is: scheduled behaviors continue to "fire" (the engine logs the dispatch), but the messages never go out. The operator sees no error in the engine's log. They have to dig into per-platform status to find the dead bot.

---

## 4. Livestream Crash — Three Modes

### 4.1 Bilibili thread crash

Runs in its own thread via `live_router.py:108-113`. Inside, `blivedm` library handles its own asyncio loop. If `blivedm` raises an uncaught exception, the thread exits. The `live_client` module global remains set to the (now-dead) client object. `live_router.py:253` reports `is_running=True` because the global is non-None. The status lies.

### 4.2 YouTube thread crash

`ytdm.py:55-61`:

```python
while not self._stop_evt.is_set():
    try:
        self._poll_once()
        print('[YouTube] poll_once done')
    except Exception as e:
        print('[YouTube] poll error:', e)
    time.sleep(self.poll_interval)
```

Catches every exception, prints, continues. Cannot crash the polling loop. Will however *silently swallow* a permanent error — invalid API key, video ended, quota exceeded — forever. The loop polls every 5 seconds, every call fails, every call prints. No backoff, no give-up.

A user with an expired YouTube API key gets stdout spam at 12 lines/minute and no surfaced error.

### 4.3 Twitch task crash

Runs on the main loop. If the inner `_listen_loop` (`twitch_service.py:43-54`) somehow exits (its catch-all reconnect loop has `if not self._running: break`), the task is done. `twitch_task` in `live_router.py:23` remains non-None. Status reports `twitch: true`. Lies.

**Cross-cutting issue:** All three livestream modes set their **module-level globals** as the "is running" witness. The actual subsystem state is not introspected; the witness is the variable. Stale witnesses lie.

---

## 5. ComfyUI Tool Crash — Hung Forever

`comfyui_tool.py:62-67`:

```python
while True:
    try:
        history = get_history(prompt_id,server_address)[prompt_id]
        break
    except Exception:
        time.sleep(1)
        continue
```

`time.sleep` is synchronous. If called via `comfyui_tool_call` (which is async), the surrounding async context is blocked. But `comfyui_tool_call` is normally invoked via the LLM's tool-call mechanism on the main loop. So `time.sleep(1)` blocks the main loop for 1 second every iteration, and the loop iterates forever if ComfyUI is dead.

**Blast radius:** Main loop blocked. Behavior engine ticks stall. Scheduler stalls. WebSocket broadcasts queue. The whole process appears to freeze.

This is the worst crash mode in SAP because it doesn't *look* like a crash — it looks like hung.

---

## 6. KB Index Build Crash — The Half-Built KB

`know_base.py:127-164` — BM25 build wrapped in try-except. Failure deletes the partial file and continues. Vector store build at lines 166-194 raises `RuntimeError` on failure.

Failure modes:

- Embedding API down → vector build raises → KB is partially built (BM25 may have succeeded; vector failed)
- Disk full mid-write → `FAISS.save_local` raises → vector store partially written → next load fails
- Cancelled mid-batch → vector_db is in memory; never saved → partial state lost

The KB is left in an *inconsistent* state. There is no transaction. There is no rollback. Next attempt to load the KB will fail (vector store missing files) or use stale (vector store from a prior build).

**Blast radius:** One KB unusable. Operator must rebuild from scratch.

---

## 7. MCP Client Monitor Crash — Reconnect Loop Forever

`mcp_clients.py:111-134` — `_connection_monitor` is the outer task that owns reconnects. The task itself is wrapped in a `while not self._shutdown` loop with `try/except Exception` (line 112-127).

If the **task itself** is cancelled (e.g. main loop shutdown), `try/except` catches `asyncio.CancelledError`? No — `Exception` does not catch `CancelledError`. So `close()` cancellation propagates correctly. Good.

If an exception bubbles up through the connect context manager and into the outer try, line 125-128:

```python
            except Exception as e:
                logging.exception("Connection failed, will retry: %s", e)
                if self._on_failure_callback:
                    await self._on_failure_callback(str(e))
```

Callback is awaited. If the callback itself raises, the exception propagates to the outer task — but the outer task does *not* re-wrap the callback. A buggy callback can crash the monitor.

`finally:` at line 129-131 nulls `self._conn`. Then `if not self._shutdown: await asyncio.sleep(5)` and loop. Robust.

**Blast radius:** Bad callback kills MCP reconnect. Tools from that MCP server become permanently unavailable until process restart.

---

## 8. Behavior Engine Tick Crash — Survives, But Loses State

`behavior_engine.py:115-135`:

```python
async def start(self):
    self._stop_event = asyncio.Event()
    self.is_running = True
    logging.info("[BehaviorEngine] 监控任务已激活")
    
    try:
        while not self._stop_event.is_set():
            if not self.is_running: 
                break
            try:
                await self._tick()
            except Exception as e:
                logging.error(f"[BehaviorEngine] Tick 异常: {e}")
            
            await asyncio.sleep(1)
    finally:
        self.is_running = False
```

Inner try-except. Tick exceptions are logged but the loop continues. Robust shape.

**Blast radius:** Bad behavior config that throws every tick just spams the log at 1 line/second.

But: the `self.timers` and `self.counters` dicts are mutated during `_tick`. If a tick crashes *after* mutation but *before* the dispatch, the timer is set but the dispatch never happened. Next tick may treat the time as already-fired.

This is a partial-update bug. The timer dict mutations should be atomic across the dispatch decision and the dispatch action. They are not.

---

## 9. Sub-Agent Task Crash — Lost Without Trace

`sub_agent.py:32-99` — the sub-agent loop. The outer `try` wraps the entire `while iteration < max_iterations` loop. On exception, the task center is updated to `FAILED`. Good.

But the task is launched via `asyncio.create_task(run_subtask_in_background(...))` (`scheduler.py:108-115`). If `run_subtask_in_background` raises *during launch* (before its own try-except sets up), the exception goes to the task object. No done callback. Silent failure.

`scheduler.py:108-115`:

```python
asyncio.create_task(
    run_subtask_in_background(
        task_id=task.task_id,
        workspace_dir=workspace_dir,
        settings=self.settings
    )
)
```

Yes — fire and forget. No `task.add_done_callback(log_exception)`. The scheduler's view of "this task is RUNNING" diverges from reality.

**Blast radius:** A scheduled task that fails to launch shows `RUNNING` forever. The next scheduler tick (`scheduler.py:14-22`) re-scans tasks; the task is still RUNNING, so it skips it. The task is *stuck*. Operator must manually mark it FAILED in the task center.

---

## 10. Electron Crash — Total Loss

If the Electron renderer or main process crashes, the Python child process is reaped (Electron spawns it as a child). All in-memory state evaporates. Disk state survives.

The Vue `aiBrowser` component (referenced in `cdp_tool.py:123`) lives in the renderer. If the renderer crashes mid-tool-call, the Python side gets a WebSocket error and returns "Main window not found." The LLM sees an error string. If the LLM was in the middle of a multi-step task, the task aborts.

**Blast radius:** Total UI loss; user restarts the app.

---

## 11. The Crash Modes That Don't Exist

SAP does not crash from:

- Out-of-memory in embedding (FAISS uses C++ heap; Python OOM only at very large indexes)
- Single bot config corruption (per-bot, isolated)
- One MCP server failure (per-server, isolated)
- One livestream platform failure (mostly per-platform)
- KB corruption (other KBs unaffected)

These are the strengths. The fault isolation per-IM-bot and per-MCP-server is correct.

---

## 12. The Crash Modes That Are Worst

Ranked by blast radius × likelihood:

1. **ComfyUI hang → main loop blocked** (worst — single tool call freezes the world)
2. **Sub-agent task lost-and-forgotten** (high — task stuck RUNNING, operator must intervene)
3. **Livestream module-globals lying about state** (high — UI reports false running state)
4. **Behavior engine tick partial mutation** (medium — schedule drift)
5. **Dead bot handler still registered with behavior engine** (medium — silent failure)
6. **YouTube polling spam on bad credential** (low — annoying, not damaging)

---

## 13. Cross-References

- [[50_SELF_HEALING_PATTERNS]] — the patterns themselves
- [[57_FAILURE_TAXONOMY]] — ranked failure table; this doc's #12 list maps in
- [[58_OBSERVABILITY_GAPS]] — without observation, none of these crashes are diagnosable
- [[20_interface/27_STREAMING_INTERFACE]] — module globals as state witnesses
- [[hermes:HEM-53_CRASH_PROOFING_PATTERNS]] — Hermes's patterns

---

## What This Means for Ember

**Adopt:**
- Adopt the **per-IM-bot fault isolation** pattern. SAP gets this right at the manager level.
- Adopt the **inner try-except in tick loops** (`behavior_engine.py:127-129`). The shape is correct: catch exception, log, continue, never let the tick loop die.
- Adopt the **MCP monitor task** pattern (`mcp_clients.py:111-134`). The structure is sound.

**Adapt:**
- Adapt the singleton behavior engine into a **deregistration-aware handler registry**. When a manager goes `STOPPED`, its handler is auto-deregistered from the engine. SAP's "register-forever, dispatch-anyway" pattern is the negative template.
- Adapt the YouTube polling loop into a **bounded-retry with give-up signal**. After N consecutive failures of the same kind, the polling thread sets `self.error_state` and stops. The UI surfaces it. SAP polls forever on bad creds.
- Adapt the "module-level globals as state witness" pattern into a **typed StateRegistry**. Subsystems register their state; the registry is the single source of truth for "is X running." SAP's witnesses lie.

**Avoid:**
- **Avoid `time.sleep` in any code reachable from the main loop** (`comfyui_tool.py:65`). Synchronous sleep in async code is a freeze bomb.
- **Avoid `asyncio.create_task` without `add_done_callback` for error logging** (across SAP). Fire-and-forget without observability is failure-and-forget.
- **Avoid module globals as state witnesses** (`live_router.py:21-27`). Use a registry; check actual subsystem state.
- **Avoid partial-state mutation in tick loops** (`behavior_engine.py:184-187`). Either atomic transaction or `redo`-able decision.

**Invent:**
- **Task Witness with Done Callback Hook.** Every `create_task` in Ember goes through `ember.task.spawn(coro, owner: Subsystem, on_error: ErrorHandler)`. The spawner adds the done callback automatically and forwards exceptions to structured logging. No fire-and-forget.

- **Tick Crash Isolation Wrapper.** Periodic loop bodies are wrapped in `@tick_isolated(state_snapshot=True)`. On exception, the wrapper restores the pre-tick state of any declared state variables. Prevents partial-mutation bugs.

- **StateRegistry as Truth.** Every subsystem registers a `StateProvider` with the global `StateRegistry`. The provider returns `SubsystemState` on call (no caching beyond N seconds). The UI / health endpoint / orchestrator query the registry — never module globals.

- **Hung Tool Detector.** Tools that block the event loop for > 100ms are flagged. Tools that block for > 5 seconds are killed by the orchestrator (cancelled, returned as `tool_timeout`). The LLM is informed. SAP's `time.sleep` blocking the main loop is impossible by construction.

- **Crash-Domain Map.** Ember ships a `CRASH_DOMAINS.md` that names every subsystem, what it crashes when it crashes, and what survives. The map is automated — generated from `@subsystem(depends_on=...)` decorators on each subsystem class. Operators read this before deploying.

- **Subsystem Restart Policy.** Each subsystem declares its restart policy: `auto_restart=True/False`, `max_restarts_per_hour=N`, `backoff=ExponentialBackoff(...)`. Restart-loops are bounded. A subsystem that has exceeded its restart budget is marked `STOPPED_PERMANENTLY` until operator action. SAP's reconnect-forever bots are the negative template.

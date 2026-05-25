---
codex_id: 50_SELF_HEALING_PATTERNS
title: Self-Healing Patterns — What Survives Crash, What Doesn't, What Pretends To
role: Auditor
layer: Verification
status: draft
sap_source_refs:
  - py/mcp_clients.py:111-134
  - py/twitch_service.py:43-54
  - py/behavior_engine.py:115-142
  - py/qq_bot_manager.py:42-78
  - py/telegram_bot_manager.py:60-110
  - py/sleep_guard.py:30-68
  - py/know_base.py:127-164
ember_subsystem_targets: [Funi, Strengr, Munnr, Smiðja]
cross_refs:
  - 50_verification/51_CRASH_RESISTANCE
  - 50_verification/57_FAILURE_TAXONOMY
  - 50_verification/58_OBSERVABILITY_GAPS
---

# Self-Healing Patterns — What Survives Crash, What Doesn't, What Pretends To

> *Sólrún, voice cold and even: SAP has three patterns that look like self-healing: reconnect-with-backoff, lazy-load-with-fallback, and try-except-swallow. The first is real. The second is real with caveats. The third is a coping mechanism. Knowing which is which is the difference between a system that survives a Tuesday and one that pretends to.*

This document catalogs SAP's self-healing patterns and rates each by **what it actually accomplishes** vs **what it appears to accomplish**. The distinction is load-bearing for Ember: a pattern that looks like self-healing but only swallows the error is *worse* than no pattern at all.

---

## 1. The Three Patterns SAP Calls Self-Healing

### Pattern A: Reconnect-with-Exponential-Backoff

The cleanest example: `twitch_service.py:43-54`.

```python
# /tmp/super-agent-party/py/twitch_service.py:43-54
    async def _listen_loop(self):
        reconnect_delay = 5
        while self._running:
            try:
                await self._connect_and_read()
                reconnect_delay = 5
            except Exception as exc:
                if not self._running:
                    break
                print(f"[Twitch] 连接异常: {exc}，{reconnect_delay}s 后重连")
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, 60)
```

Reset to 5 on success. Double on failure. Cap at 60. Stop if `_running` flipped to False.

This is the canonical reconnect pattern. It works. It is the *only* place in SAP that I can call truly self-healing without caveat. The pattern handles:

- Network blips → reconnect after 5s
- Twitch IRC bounce → reconnect after 5s
- Twitch deny-listing the client → reconnect every 60s (no longer than that)
- Operator-initiated stop → break out cleanly

What it doesn't handle:
- Bad credentials (will reconnect forever; will succeed only if anonymous-mode kicks in)
- Twitch IRC schema change (will reconnect and then fail to parse new messages; the parser doesn't reconnect, only the socket)

Same pattern, lighter form, exists in:
- `mcp_clients.py:111-134` — MCP connection monitor with 5-second sleep before retry (no exponential)
- `qq_bot_manager.py:64-78` — startup-only, not steady-state

`mcp_clients.py` is interesting because it has a *heartbeat*:

```python
# /tmp/super-agent-party/py/mcp_clients.py:118-124
                    while not self._shutdown:
                        try:
                            await asyncio.wait_for(self._conn.session.send_ping(), timeout=3)
                        except Exception:
                            break
                        await asyncio.sleep(30)
```

A 30-second heartbeat with 3-second timeout. If the heartbeat fails, the inner loop breaks and the outer loop reconnects. The pattern is correct in shape. The 30-second interval is reasonable. The 3-second timeout may be tight — a half-loaded MCP server doing CPU work won't ping in 3 seconds.

**Auditor rating:** Pattern A is real self-healing. Adopt, with hardening for ping-timeout tuning.

### Pattern B: Lazy-Load-with-Fallback

`computer_use_tool.py:9-30`:

```python
GUI_AVAILABLE = False
try:
    import pyautogui
    import pyperclip
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.05
    GUI_AVAILABLE = True
except (KeyError, ImportError, Exception) as e:
    print(f"⚠️ [Warning] 桌面鼠标键盘工具已禁用 (缺少 DISPLAY): {e}")

def require_gui(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not GUI_AVAILABLE:
            return "执行失败：当前系统运行在无头环境(如Docker)中，没有物理显示器，无法执行鼠标和键盘操作。"
        return await func(*args, **kwargs)
    return wrapper
```

`except (KeyError, ImportError, Exception) as e` — note the explicit catch of `KeyError` (for `os.environ['DISPLAY']` missing) and `ImportError` (for missing pyautogui), then `Exception` catch-all. Tools that require GUI return a readable message instead of crashing.

`minilm_router.py:36-62` does similar for the ONNX model — if files missing, `is_loaded=False`, downstream gets `HTTPException 503`.

`know_base.py:127-164` does it for BM25 — index missing? `bm25_retriever = None`, then the load layer (`know_base.py:235-239`) silently swaps in the vector retriever. **This is the bad form** — already audited in [[2B_RETRIEVAL_INTERFACE]] §2.

**Auditor rating:** Pattern B is *partially* real. When the fallback is explicit (computer_use returns "disabled"; minilm returns 503), it is real self-healing. When the fallback is silent and changes downstream behavior (`know_base.py:235-239`), it is *fake* self-healing — the system pretends to work; the user pays a quality cost they don't see.

### Pattern C: Try-Except-Swallow

This is the most common pattern in SAP. Audit found **~30+ instances** of bare `except:` clauses:

- `live_router.py:65-76` — broadcast swallows all
- `dingtalk_bot_manager.py:100,152,304,349` — four spots
- `feishu_bot_manager.py:165,178,183,201,287,463,475,504,516,526,549` — eleven spots
- `discord_bot_manager.py:353,400,441` — three spots
- `sub_agent.py:139,326` — two spots
- `know_base.py:163` — BM25 cleanup

Plus the catch-and-log-print patterns:

- `comfyui_tool.py:62-67` — `except Exception: time.sleep(1); continue`
- `cdp_tool.py:90-91` — `except Exception as e: print(...); return []`
- `custom_http.py:39-41` — `except Exception as e: print(...); return f'Error: {e}'`

The pattern is: catch exception, log via `print()`, return a sentinel value or continue silently.

**This is not self-healing. This is repudiation.** The error happened. The error was caught. The error was not surfaced to the operator. The operator's *experience* is "the feature didn't work for some reason; restart the app and try again." This is the most common pattern for the most common bug class.

**Auditor rating:** Pattern C is a coping mechanism, not a self-healing strategy. Every instance I would replace with structured logging and a defined fallback value.

---

## 2. What Survives Crash (And What Doesn't)

The persistence audit: what state survives `kill -9` of the SAP process?

| State | Persisted? | File |
|---|---|---|
| `settings.json` | Yes | `USER_DATA_DIR/settings.json` |
| Affection state | Yes | `USER_DATA_DIR/affection/affection_data.json` (`affection_system.py:9`) |
| Memory cache | Yes | `USER_DATA_DIR/memory_cache/` |
| Knowledge base FAISS | Yes | `USER_DATA_DIR/kb/<id>/` |
| Uploaded files | Yes | `USER_DATA_DIR/uploaded_files/` |
| **Task center state** | Yes (SQLite) | per `task_center.py` |
| **MCP connections** | No | in-memory only |
| **IM bot threads** | No | restart from scratch |
| **Livestream connection state** | No | global vars wiped |
| **Behavior engine timers** | No | in-memory |
| **Behavior engine counters** | No | in-memory; per-cycle ran-count lost |
| **Connection manager subscribers** | No | WebSocket clients reconnect |
| **`running_comfyuiServers` list** | No | resets to empty |
| **Active sub-agent tasks** | Partial (task_center has state, in-flight HTTP requests die) |

The persistence story is *mixed*. Settings and user data survive. Runtime orchestration state does not. A crash mid-livestream loses connection state and the YouTube/Bilibili/Twitch connections all bounce. A crash mid-behavior-cycle loses `ran_count` for the cycle that was running.

This is the SAP design philosophy in code: long-term user state on disk, short-term operational state in memory. A reasonable design — *if* the resumption is graceful.

The resumption is partially graceful:

- IM bots auto-reconnect on the next `start_bot` call from the UI
- MCP connections reconnect via `_connection_monitor`
- Knowledge bases reload from disk
- Affection state reloads from disk

The resumption is *not* graceful:

- Behavior engine starts from zero — scheduled times are re-anchored at startup
- Livestream connection state has no "where was I" cursor (YouTube's pageToken is in memory only)
- Sub-agent tasks in flight are lost; the task_center may show them as RUNNING but no executor is running them

`scheduler.py:118-134` has a `next_run_at` field stored in task context — *this* does persist. So cycle-based scheduled tasks do resume correctly. But the `ran_count` resets unless the task center's context.json was checkpointed at the right moment.

---

## 3. The Singleton Pattern as Fragility

`behavior_engine.py:55-60`:

```python
class BehaviorEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BehaviorEngine, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
```

A module-level singleton. Eight IM bot managers import this and share it. Their `register_handler` calls mutate `cls._instance.handlers`. Their behavior configs mutate `cls._instance.settings`.

A crashed-and-restarted singleton starts from the same `cls._instance = None`. The new process gets a fresh singleton. That's fine for *this process*. The fragility is: in tests or in module reloads, the singleton survives — but its `is_running` flag may not match reality. SAP has no test suite to verify this; in production it doesn't matter because Electron is one process.

**Auditor rating:** The singleton works for SAP's deployment model. It would not survive a multi-process architecture. Ember's federated-self requires multi-process; singletons are out.

---

## 4. The Restart-As-Recovery Anti-Pattern

`live_router.py:233-247` — `reload_live` is "stop + sleep(2) + start." This is reload-as-restart.

`qq_bot_manager.py:64-78` — startup has `_startup_complete.wait(timeout=30)`. If the bot doesn't ready in 30s, calls `stop_bot()` and raises. The user must click "start" again.

`live_router.py:241` — `await asyncio.sleep(2)` between stop and start. Pure timing-based coordination.

The general SAP recovery model is "stop the broken subsystem; restart it." This works in interactive UI but not in autonomous recovery. The behavior engine, the scheduler, none of these can *automatically* restart a crashed IM bot. The user has to do it manually from the UI.

For an unattended deployment (server, dockerized, scheduled-restart-on-failure), this means SAP is not self-healing at the subsystem level — only at the *process* level (Docker restarts the whole container on crash).

---

## 5. The Lazy-Init Pattern — Beautiful When It Works

`minilm_router.py:113-124`:

```python
def get(self) -> MiniLMOnnxPredictor:
    if self._predictor and self._predictor.is_loaded:
        return self._predictor
    with self._lock:
        if self._predictor and self._predictor.is_loaded:
            return self._predictor
        
        predictor = MiniLMOnnxPredictor(self.model_dir, self.use_gpu)
        if not predictor.is_loaded:
            raise RuntimeError("Model failed to load")
        self._predictor = predictor
        return self._predictor
```

Double-checked locking. Correct. Cold start cost paid once. Subsequent calls return cached predictor.

`reload` (line 126-128) drops the predictor; next call re-loads. This is a clean reload-on-demand without a restart.

Same pattern, simpler form, in `ClaudeAsOpenAI.py:29-38` for LiteLLM (no lock, lazy import).

**Auditor rating:** Lazy-init is real engineering. Pattern is borrowed cleanly.

---

## 6. The Sleep-Guard As Best-Effort

`sleep_guard.py:30-68` — Windows uses `SetThreadExecutionState`; macOS uses `caffeinate -dims` subprocess; Linux uses `xdotool key Shift_L` periodically. The pattern is: prevent the host from sleeping while SAP is running.

This is not self-healing of SAP — it's self-protection. If the host sleeps mid-livestream, the websocket connections die. SleepGuard prevents that.

Best-effort: on Linux without xdotool, no protection. On systems with strict power policy, may be overridden. The fallback is "user notices sleep occurred, restarts."

**Auditor rating:** Pragmatic. Cross-platform. Lift the *concept* (prevent sleep during critical operations), reject the heavyweight implementation details.

---

## 7. What SAP Doesn't Have At All

- **No circuit breakers** — repeated upstream failures don't trip a breaker. The MCP reconnect loop will hammer a dead server forever.
- **No health checks** — `/health` endpoint... search server.py: there is `/health`? Let me note the absence: no documented `/health` endpoint with subsystem status surfaces. The UI polls per-subsystem status endpoints individually.
- **No graceful shutdown for sub-agents in flight** — `Ctrl-C` on the Electron host kills sub-agent tasks mid-stream.
- **No idempotency keys** — re-sending the same IM message after a flake double-posts; no `external_message_id`-keyed dedupe.
- **No outbox pattern** — messages to send are not queued; if the bot can't reach the platform, the message is lost.
- **No saga / compensating action** — a tool that wrote to a remote system and then crashed leaves the remote in an inconsistent state.

These absences are not bugs. They are choices. They are choices that make SAP *appropriate for an interactive desktop companion* and *inappropriate for an unattended service*.

---

## 8. Cross-References

- [[51_CRASH_RESISTANCE]] — per-subsystem crash mode catalog
- [[57_FAILURE_TAXONOMY]] — the ranked impact table
- [[58_OBSERVABILITY_GAPS]] — without observation, no self-healing
- [[20_interface/27_STREAMING_INTERFACE]] — the global-state crash story for livestream
- [[hermes:HEM-53_CRASH_PROOFING_PATTERNS]] — Hermes's crash-proofing as positive counter

---

## What This Means for Ember

**Adopt:**
- Adopt the **exponential backoff with cap** pattern (`twitch_service.py:43-54`) verbatim for any long-lived outbound connection. 5s start, 2× factor, 60s cap is a reasonable starting point.
- Adopt the **heartbeat-with-tight-timeout** pattern (`mcp_clients.py:118-124`) for any RPC connection. Tune the timeout to the workload; SAP's 3s is too tight for some MCP servers.
- Adopt the **double-checked locking with `is_loaded` validity check** (`minilm_router.py:113-124`) for any heavy resource.
- Adopt the **SleepGuard pattern** (cross-platform sleep prevention) for any Ember presence that must remain responsive. But declare it: the operator knows SleepGuard is on.

**Adapt:**
- Adapt the **reconnect-with-callback** pattern (`mcp_clients.py:91,127`) — but make the callback typed, not a free-form callable. `OnFailureCallback = Protocol with on_connection_loss(reason: FailureReason) -> None`. Failure reason is enumerated, not stringly-typed.
- Adapt the **two-events pattern** (`_startup_complete` + `_ready_complete`) from QQ/Feishu — but use a single typed `BootState` enum that ratchets forward: `NOT_STARTED → CONNECTING → CONNECTED → READY → RUNNING → STOPPING → STOPPED`. The state machine is explicit and inspectable.

**Avoid:**
- **Avoid bare `except:`** as a self-healing pattern. It is not self-healing; it is repudiation.
- **Avoid silent fallback to a *different* behavior** (`know_base.py:235-239` BM25 → vector substitution). Loud fallback or no fallback.
- **Avoid module-level singletons that share mutable state across subsystems** (`behavior_engine.py:55-60`). They make multi-process impossible and they hide state ownership.
- **Avoid `asyncio.sleep(2)` as restart coordination** (`live_router.py:241`). Wait on the actual stop event.
- **Avoid 30-second hardcoded startup timeouts repeated across eight managers**. Per-platform tuning; declare on the class.
- **Avoid losing scheduler state on restart** (behavior_engine timer reset). State persists or it never existed.

**Invent:**
- **Typed Self-Healing Decorator.** Every subsystem method that can fail declares a typed retry policy: `@self_heal(strategy=ExponentialBackoff(initial=5, factor=2, cap=60), on_failure=Notify("operator"))`. The behavior is in the decorator; the body is pure logic. SAP repeats the same backoff pattern in six files; Ember has one.

- **Health Endpoint with Subsystem Status.** Every Ember subsystem reports `health() -> SubsystemHealth(state, last_ok, last_failure, latency_p99, error_class_breakdown)`. The Funi orchestrator aggregates. The operator sees a structured health page. SAP has nothing of the kind.

- **Outbox Pattern for Outbound Messages.** Every message Ember wants to send (IM reply, livestream comment response, tool call result) goes into a typed outbox. The outbox guarantees at-least-once delivery, content-keyed dedupe, and observable backpressure. SAP loses messages on flake; Ember does not.

- **Circuit Breaker per Outbound Service.** Each adapter has a circuit breaker. After N failures in a window, the breaker opens; the LLM is told "service X is unavailable, do not propose tools that use it." After a cooldown, the breaker half-opens and probes. This is the Vow of **Graceful Offline** in code.

- **Crash Recovery Witness.** On Ember restart, the orchestrator scans persisted state and the in-flight task log; subsystems are restored to their last consistent state. The witness logs what was recovered, what was lost. The operator sees the diff at next start.

- **Scheduled State Snapshot.** Behavior engine state, scheduler state, retrieval cache state — all snapshotted to disk every N seconds. On crash, restore from snapshot. SAP's "in-memory only" runtime state is the negative template.

- **Process-Level Self-Repair Disabled By Default.** Auto-restart of a crashed subsystem requires operator opt-in per-subsystem. Restart-loops on bad credentials are catastrophic — they consume free-tier rate limits, lock out accounts, etc. SAP's reconnect-forever loops are the negative template; Ember declares them explicitly per-subsystem.

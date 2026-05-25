---
codex_id: 58_OBSERVABILITY_GAPS
title: Observability Gaps — What SAP Doesn't Know About Itself
role: Auditor
layer: Verification
status: draft
sap_source_refs:
  - py/affection_system.py:23,35
  - py/custom_http.py:36-39
  - py/cdp_tool.py:91,143,168
  - py/comfyui_tool.py:140,180,184
  - py/live_router.py:35,156-157,165,212-213
  - py/twitch_service.py:52
  - py/ytdm.py:51,58,60,131
  - py/know_base.py:154,158,163,215,238
  - py/behavior_engine.py:107,120,129,134,142,221
ember_subsystem_targets: [Funi, Munnr]
cross_refs:
  - 50_verification/50_SELF_HEALING_PATTERNS
  - 50_verification/51_CRASH_RESISTANCE
  - 50_verification/57_FAILURE_TAXONOMY
  - 60_synthesis/65_META_AWARENESS
---

# Observability Gaps — What SAP Doesn't Know About Itself

> *Sólrún, voice cold and even: a system that cannot observe itself cannot self-heal, cannot be operated under load, cannot be improved by a maintainer reading the code. SAP, by the static evidence in the source, knows almost nothing about itself at runtime. The operator's only window is stdout. The LLM's only window is what the LLM is told.*

This document catalogs SAP's observability surfaces — what it logs, what it doesn't, what it could log and chose not to, what telemetry it never emits. The implications feed [[60_synthesis/65_META_AWARENESS]] (Cartographer's invention: introspectable telemetry as a True Name candidate, **Hugarsýn** — mind-sight).

The Auditor's posture: observability is not a nice-to-have. It is the only force in software that grades reality against intent.

---

## 1. The Dominant Log Channel: `print()`

Counting `print(` occurrences across SAP's Python modules: at least 35 modules use `print` directly. Concentration:

- `live_router.py` — 35 `print` calls
- `web_search.py` — 23
- `sleep_guard.py` — 13
- `sub_agent.py` — 10
- `know_base.py` — 7
- `comfyui_tool.py` — 7
- `cli_tool.py` — 7
- `cdp_tool.py` — 6
- `moss_tts.py` — 6
- `affection_system.py` — 3
- ... and many more

By contrast: `import logging` appears in ~10 modules. `logging.error` / `logging.info` / `logging.warning` calls are concentrated in `behavior_engine.py:107,120,129,134,142,221` and `mcp_clients.py:78,126`.

**The single dominant logging surface is `print()` to stdout.** This means:

- **No log levels** — every print is the same priority; no `DEBUG` vs `WARNING` vs `ERROR`
- **No structured fields** — `print(f"Status: {response.status}")` is a string; no `{"event": "http_response", "status": 200}`
- **No timestamps** — unless the print includes one (almost never)
- **No correlation ids** — a print from `affection_system` and a print from `wechat_bot_manager` cannot be linked to the same conversation
- **No log rotation** — stdout grows until something redirects it
- **No filtering** — operator wants only errors? Has to `grep` after the fact

A system whose primary log channel is `print()` is a system that asks the operator to do the work of a log framework with their eyes.

---

## 2. The Symptoms of Print-Only Logging

### 2.1 Print of secrets

Already cataloged in `[[53_SECURITY_REVIEW]]` §6.2 — `custom_http.py:36-38` prints the entire HTTP response body. `cdp_tool.py:91` prints CDP errors that may include cookie material. `comfyui_tool.py:140,180,184` prints upload results. The print habit is contagious.

### 2.2 Print of stack trace fragments only

`minilm_router.py:58-61`:

```python
except Exception as e:
    print(f"Error loading MiniLM ONNX Predictor: {e}")
    import traceback
    traceback.print_exc()
    self.is_loaded = False
```

`traceback.print_exc()` writes to stderr. The operator sees the trace. But the trace is unstructured — the maintainer cannot grep by exception class, cannot count occurrences over time, cannot alert on a threshold.

### 2.3 Print of success and failure indistinguishably

`know_base.py:154,158,163,215,238`:

- "BM25 index saved successfully" (success print)
- "⚠️ BM25 Index failed (Skipping)" (warning print)
- "Error loading BM25 (will fallback)" (error print)
- "Fallback: Using Vector Retriever for BM25 slot." (silent-degradation notice)

Four different semantic levels, all going to the same channel with no structure. The operator scanning logs cannot quickly answer "did BM25 succeed in the last hour?"

### 2.4 Print of internal progress

`know_base.py:186`:

```python
print(f"Processed {min(i+batch_size, len(docs))}/{len(docs)} documents")
```

Progress prints from a build operation. Mixed with everything else in stdout. The operator wanting a status bar gets a flood.

---

## 3. What SAP Could Observe But Doesn't

### 3.1 LLM token usage per session

The OpenAI-compat adapters return `usage` (or don't, for Dify) but SAP nowhere aggregates it. A user can't ask "how many tokens did I use today?" There is no per-session, per-user, per-platform usage tracking.

### 3.2 LLM call latency

No `time.perf_counter()` around adapter calls. P99 latency is unknown. Slow adapter degradation is invisible.

### 3.3 Tool call duration / outcome distribution

Tools return strings. Nothing measures: how long did `evaluate_script` take? How often did it return an error? Per-tool reliability stats don't exist.

### 3.4 Per-IM-bot inbound rate

Each bot's `on_message` handler processes messages one at a time. There's no counter for "messages per minute received on platform X." Spike detection is impossible. Rate-limit decisions are impossible.

### 3.5 Per-MCP-server health history

`mcp_clients.py:111-134` has a heartbeat loop. The heartbeat result is *not recorded*. After a flap, you can't tell SAP "was this server flapping yesterday?"

### 3.6 Behavior engine fire history

`behavior_engine.py:218-222` logs each fire via `logging.info`. The logging.info goes... wherever Python's root logger is configured. SAP doesn't configure the root logger I can find. So in practice, behavior fires log to stderr (default). No structured store; can't query "did behavior X fire last Tuesday at 9am?"

### 3.7 Knowledge base query stats

No "queries per hour against KB X." No "average results returned." No "queries with zero hits." Search quality regression is invisible.

### 3.8 Affection state mutations

`affection_system.py:64`:

```python
print(f"✨ [好感度系统] 用户 {user_name} 状态已更新: {new_stats}")
```

A print, no structured event. The history of user affection changes — every mutation — is *not retained*. The current state is the only state; how it got there is gone.

### 3.9 Livestream comment ingest stats

YouTube polls every 5s. No counter for "comments ingested per minute." No alert when ingest rate drops to zero (could mean stream ended, or could mean API auth broke).

### 3.10 Active connection count for WebSocket fan-out

`live_router.py:53-75` `ConnectionManager` has `self.active_connections` — a list. No exposed counter, no per-subscriber metadata, no metric.

### 3.11 FastAPI request rate / latency

Uvicorn can log access. SAP's uvicorn config is in `server.py` (referenced); I haven't read it in full, but the default is access log to stdout with no structured fields. No `/metrics` endpoint.

---

## 4. The Missing Health Endpoint

A search of `server.py` for `@app.get("/health")` would tell me whether SAP has a health endpoint. From the structure of `live_router.py:249-262` (`/status` endpoint for the live module), SAP follows a per-module-status pattern. There is no unified `/health` endpoint that aggregates.

The UI polls each subsystem's status separately. This works for a one-user UI; it fails for unattended deployment (Kubernetes liveness/readiness probes; Prometheus scraping).

---

## 5. The Internal State Invisibility

What state does SAP have that you cannot inspect at runtime?

| State | Inspectable? | How |
|---|---|---|
| Current settings | Yes | settings.json on disk |
| Affection data | Yes | affection_data.json |
| KB list / contents | Yes (UI) | `/api/kb/*` |
| MCP server connections + their tool lists | Partially | per-server status; tools list logged once |
| Behavior engine state (timers, counters) | **No** | in-memory dicts; no read endpoint |
| Per-bot status | Partially | per-bot `get_status()` returns shallow dict |
| Sub-agent task in-flight | Yes (task center) | persisted state |
| `running_comfyuiServers` allocation | **No** | module-level list, no introspection |
| `CURRENT_SCREEN_REGION` for computer-use | **No** | module-level global, no introspection |
| Embedding model load state | Partially | exception only if failed; success silent |
| HTTP client connection pools | **No** | implicit `httpx.AsyncClient` state |
| Active WebSocket subscriber list | **No** | `manager.active_connections` private |
| YouTube `_page_token` / Twitch reconnect delay | **No** | thread-local state, no introspection |

The invisible state is mostly the **runtime orchestration state**. Per-subsystem persistent state survives. Per-subsystem runtime state is opaque.

This is the gap that [[60_synthesis/65_META_AWARENESS]] addresses: **the system should be able to introspect its own runtime state**.

---

## 6. The LLM's Observability Of Itself

When SAP asks the LLM to do something, what does the LLM know about its own situation?

- **What tools are available?** Yes — listed in the tool-schema.
- **What models is the LLM running on?** No — the LLM doesn't get told.
- **What recent tool calls succeeded or failed?** Partial — only the immediate prior call's result.
- **What's the current conversation length / cost?** No.
- **What's the host's resource budget?** No.
- **What other concurrent activity is happening (other IM bots, livestream)?** No.
- **What's the affection state with the current user?** Partial — only via the regex-extracted state at end of message.

The LLM is asked to reason but is denied most of the inputs needed for grounded reasoning. The LLM compensates by being verbose, conservative, or hallucinatory. Better observability *into the system the LLM is operating in* would let the LLM be a better operator of itself.

This is the seed of `Hugarsýn` (mind-sight): the LLM should be a first-class observer of Ember's own state.

---

## 7. The Maintainer's Observability

If a maintainer (the operator, a contributor) wants to understand "why did X happen," they have:

- `stdout` (scattered prints)
- `stderr` (occasional traces)
- The settings file (read-only inspection)
- The task center SQLite (history of sub-agent tasks)
- The affection data file (current state, no history)
- The KB files (current state)

What they don't have:

- A structured log file
- A timestamped event store
- A query interface to "show me everything that happened in the last 5 minutes"
- A correlation id for "this user's conversation"
- A per-feature timing histogram
- A change log for settings

A maintainer trying to reproduce a user-reported bug starts from the prose description and the operator's recollection. There is no log trail to walk back through.

---

## 8. The Operator's Observability

The operator looking at SAP in the UI sees:

- Current chat content
- Tool call results (partial)
- Per-subsystem status (running / not running)
- Settings page

They do not see:

- Token usage in the current session
- Cost in the current session
- Per-tool reliability scores
- Per-user affection trajectory over time
- Per-platform message rate
- Resource usage
- Any time-series data

The operator is in the position of a pilot with no instruments — they fly by feel.

---

## 9. What SAP Gets Right

Two observations, in fairness:

- `task_center.py` does persist task history with progress updates. Sub-agent observability *exists* for sub-agents.
- `mcp_clients.py` uses `logging.exception` (line 126), which captures stack traces with the message. Best-of-class for SAP's logging.

The pattern is: where the developer thought of logging, they did it well. Most of SAP, they didn't think of it.

---

## 10. Cross-References

- [[50_SELF_HEALING_PATTERNS]] — without observation, self-healing is blind
- [[51_CRASH_RESISTANCE]] — crashes leave no trace
- [[57_FAILURE_TAXONOMY]] — most failures are "unobservable" failures
- [[60_synthesis/65_META_AWARENESS]] — **Hugarsýn** — Cartographer's invention drawn from this gap
- [[hermes:HEM-58_OBSERVABILITY]] — Hermes's logging discipline as positive counter

---

## What This Means for Ember

**Adopt:**
- Adopt the **task_center persistence pattern** as a general one — Ember's task history is the model for what every subsystem should provide for its own activity.
- Adopt the **`logging.exception` pattern** (`mcp_clients.py:126`) for all error sites. It captures the trace properly.

**Adapt:**
- Adapt SAP's per-module status endpoints into a **unified `/health` + `/metrics`** surface. Each subsystem registers its health provider; the orchestrator aggregates. Prometheus-compatible `/metrics`.

**Avoid:**
- **Avoid `print()` for any non-development purpose** — and use a lint rule to enforce it. Ember's Rule: `print()` in source = CI fail.
- **Avoid logging without structured fields.** Use `logger.info("event_name", extra={"field1": v1, "field2": v2})` (or a structured-logging library like `structlog`).
- **Avoid silent state mutations** (e.g. affection mutations as a print rather than an event). Every state change is an event with timestamp + before + after.
- **Avoid the "operator polls each subsystem" pattern.** Push, not pull.

**Invent:**
- **Hugarsýn — Mind-Sight (proposed True Name).** A first-class observability surface that:
  - Aggregates structured events from every subsystem into a single time-series store
  - Exposes a query interface (Ember's own, or PromQL-compatible)
  - Is queryable by the LLM (the LLM can read its own situation)
  - Is queryable by the operator (UI dashboard)
  - Is queryable by tests (assertions about behavior over time)
  
  This is the central invention this doc seeds and Cartographer expands at [[60_synthesis/65_META_AWARENESS]].

- **Structured Event Catalog.** Every Ember subsystem declares its event types: `subsystem.event_name(typed_fields)`. The catalog is checked into the repo. New events require a PR with a catalog entry. SAP's freeform `print` strings are the negative template.

- **Correlation-ID Threading.** Every external event (HTTP request, IM message, livestream comment) is tagged with a UUID at ingest. All downstream logs and tool calls carry the same correlation id. The maintainer can `grep` by correlation id and trace a single conversation end-to-end.

- **Cost & Token Telemetry.** Every LLM call records: vendor, model, input tokens, output tokens, cached tokens, latency, cost-estimate. Persisted to time-series. Operator sees daily / weekly / per-user cost.

- **Per-Tool Reliability Score.** Smiðja tracks per-tool: invocation count, success rate, P50/P95/P99 latency, last-7-days trend. The LLM is *told* "tool foo has 70% success rate this session, prefer alternative" if applicable. SAP's "every tool looks the same" is the negative template.

- **LLM Situation Brief.** Before each LLM call, Ember includes a brief in the system prompt: current resource budget, current cost burn rate, active subsystems, last 3 errors. The LLM operates with context. Hjarta tunes the brief content based on tier.

- **Structured Audit Log JSONL.** Every operator-facing action (settings change, tool approval, credential rotation) writes a JSONL event with full provenance. Auditable forever. Encrypted at rest.

- **`/healthz` and `/metrics` Endpoints.** Standard Kubernetes / Prometheus surface. SAP has no `/healthz`. Ember has it from day one.

- **Replay Mode.** Any past event in Hugarsýn can be replayed: "show me this conversation as it happened, with all the tool calls and timing." Operator-debug feature. SAP cannot reconstruct any past session beyond what mem0 retained.

The Auditor's last word on observability: **what cannot be seen, cannot be verified.** Verification is my role; observability is its prerequisite. Ember without Hugarsýn is Ember without me.

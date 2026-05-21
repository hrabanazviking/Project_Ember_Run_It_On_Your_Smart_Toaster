# OpenClaw Heartbeat System — Deep Dive

> **Source Repository:** https://github.com/openclaw/openclaw  
> **Primary Language:** TypeScript (ESM, strict)  
> **Core Subsystem:** `src/infra/heartbeat-*`, `src/auto-reply/heartbeat*`, `src/agents/heartbeat-*`  
> **Date of Analysis:** 2026-05-10

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Complete File Inventory](#2-complete-file-inventory)
3. [Step-by-Step Lifecycle](#3-step-by-step-lifecycle)
4. [Data Structures](#4-data-structures)
5. [Configuration Options](#5-configuration-options)
6. [Error Handling](#6-error-handling)
7. [Message Types & Protocols](#7-message-types--protocols)
8. [Integration with Other Systems](#8-integration-with-other-systems)
9. [Strengths & Weaknesses](#9-strengths--weaknesses)
10. [Complete Mermaid Flowchart](#10-complete-mermaid-flowchart)

---

## 1. Architecture Overview

The OpenClaw heartbeat system is a **periodic autonomous agent wake mechanism** that drives background intelligence in OpenClaw — a self-hosted AI agent platform. It is not a health-check or liveness probe in the traditional distributed-systems sense. Instead, it is the **primary scheduling substrate** for the agent to periodically assess its state, deliver proactive messages, process background events, and honor scheduled commitments.

### Key Design Principles

- **Phase-aligned intervals**: Each agent's heartbeat ticks are deterministically phase-shifted using a SHA-256 digest of `schedulerSeed:agentId` to stagger agent wake-ups across the interval, avoiding thundering herd.
- **Multi-wake-source dispatch**: Heartbeats can be triggered by scheduled intervals, manual CLI commands, background exec completions, cron events, webhook hooks, ACP spawn events, notification changes, and retry cascades.
- **Coalesced wake queue**: Multiple wake requests arriving in rapid succession are batched and deduplicated before execution, with priority ordering (manual > action > default > interval > retry).
- **Flood protection**: A bounded ring-buffer of recent run-start timestamps prevents runaway feedback loops where agent tool calls trigger successive heartbeat wakes.
- **Active hours**: Optional time-of-day windows (with timezone support) restrict heartbeat execution to specific hours.
- **Isolated sessions**: An opt-in `isolatedSession` mode runs each heartbeat turn in a fresh session with no prior conversation history, dramatically reducing token cost.
- **Heartbeat Response Tool**: An `heartbeat_respond` model tool provides structured acknowledgment (`outcome`, `notify`, `summary`, `priority`) as an alternative to the legacy `HEARTBEAT_OK` text token.
- **Commitment delivery**: Heartbeats can deliver inferred follow-up commitments (reminders) alongside or instead of regular wake content.
- **Visibility control**: A layered per-channel/per-account `showOk`/`showAlerts`/`useIndicator` configuration controls whether silent "OK" heartbeats are suppressed and whether status indicators surface in the UI.

### High-Level Component Map

```
┌─────────────────────────────────────────────────────────┐
│                   Heartbeat Runner                       │
│  (src/infra/heartbeat-runner.ts — 2377 lines)          │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │ Wake Dispatch │  │   Scheduler   │  │  Preflight    │ │
│  │ (heartbeat-   │  │  (heartbeat-  │  │  (resolve     │ │
│  │  wake.ts)      │  │  schedule.ts) │  │  session,     │ │
│  │               │  │              │  │  events,       │ │
│  │               │  │              │  │  tasks,        │ │
│  │               │  │              │  │  commitments)  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬────────┘ │
│         │                  │                   │         │
│         └──────────┬───────┘                   │         │
│                    │                           │         │
│         ┌──────────▼───────────────────────────▼────┐    │
│         │           runHeartbeatOnce()                │    │
│         │  - Cooldown/flood checks                   │    │
│         │  - Prompt resolution                        │    │
│         │  - Agent runner invocation                  │    │
│         │  - Response normalization & delivery         │    │
│         └────────────────┬────────────────────────────┘    │
│                          │                                │
│         ┌────────────────▼────────────────────────┐      │
│         │        Delivery & Deduplication            │      │
│         │  - Normalize reply / heartbeat tool resp   │      │
│         │  - Strip HEARTBEAT_OK token               │      │
│         │  - Duplicate suppression (24h window)      │      │
│         │  - sendDurableMessageBatch                 │      │
│         └────────────────┬────────────────────────────┘    │
│                          │                                │
│         ┌────────────────▼────────────────────────┐      │
│         │         Event & Post-Run Telemetry        │      │
│         │  - emitHeartbeatEvent()                   │      │
│         │  - Update task timestamps                  │      │
│         │  - Consume system events                   │      │
│         │  - Mark commitments attempted/sent          │      │
│         └───────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Complete File Inventory

### Core Infrastructure (`src/infra/`)

| File | Lines | Purpose |
|------|-------|---------|
| `heartbeat-runner.ts` | 2377 | **Primary orchestrator** — scheduler loop, preflight, prompt resolution, agent invocation, delivery, post-run bookkeeping |
| `heartbeat-wake.ts` | 348 | **Wake dispatch** — coalesced wake queue, timer management, retry scheduling, handler registration |
| `heartbeat-schedule.ts` | 97 | **Phase-aligned scheduling** — computes deterministic phase offsets, seeks next active-hours slot |
| `heartbeat-cooldown.ts` | 164 | **Flood/debounce guard** — minimum spacing, flood threshold, decision matrix for wake intents |
| `heartbeat-events.ts` | 69 | **Event emitter** — heartbeat status events (`HeartbeatEventPayload`) with global singleton listener pattern |
| `heartbeat-events-filter.ts` | 217 | **Event content classification** — distinguishes cron, exec-completion, heartbeat-ack, and noise events |
| `heartbeat-visibility.ts` | 73 | **Delivery visibility resolver** — layered per-account > per-channel > channel-defaults > global defaults |
| `heartbeat-typing.ts` | 65 | **Typing indicator callbacks** — integrates channel plugin typing signals during heartbeat runs |
| `heartbeat-summary.ts` | 122 | **Config resolution for diagnostics** — produces `HeartbeatSummary` (enabled, every, everyMs, target, model, ackMaxChars) |
| `heartbeat-active-hours.ts` | 99 | **Active hours time window** — parses HH:MM windows with IANA timezone support |
| `heartbeat-reason.ts` | 5 | **Wake reason normalization** — defaults missing reason to `"requested"` |

### Auto-Reply Layer (`src/auto-reply/`)

| File | Lines | Purpose |
|------|-------|---------|
| `heartbeat.ts` | 321 | **Core constants & token logic** — `HEARTBEAT_TOKEN`, default prompt, `isHeartbeatContentEffectivelyEmpty()`, `stripHeartbeatToken()`, `parseHeartbeatTasks()`, `isTaskDue()` |
| `heartbeat-filter.ts` | 99 | **Transcript filtering** — `isHeartbeatUserMessage()`, `isHeartbeatOkResponse()`, `filterHeartbeatPairs()` for pruning heartbeat noise from context |
| `heartbeat-tool-response.ts` | 123 | **Structured response tool** — `HeartbeatToolResponse` type, `normalizeHeartbeatToolResponse()`, `createHeartbeatToolResponsePayload()`, outcome/priority/notification extraction |
| `heartbeat-reply-payload.ts` | 23 | **Payload resolution** — selects the last outbound `ReplyPayload` with actual content |

### Agent Layer (`src/agents/`)

| File | Lines | Purpose |
|------|-------|---------|
| `heartbeat-system-prompt.ts` | 86 | **System prompt injection** — decides whether to include `## Heartbeats` section in agent system prompt; resolves prompt text |
| `tools/heartbeat-response-tool.ts` | 63 | **Agent tool definition** — creates the `heartbeat_respond` tool with TypeBox schema for structured model responses |

### Configuration (`src/config/`)

| File | Role |
|------|------|
| `types.agent-defaults.ts` | Defines the `heartbeat?: { every, activeHours, model, session, target, directPolicy, to, accountId, prompt, includeSystemPromptSection, ackMaxChars, suppressToolErrorWarnings, timeoutSeconds, lightContext, isolatedSession, skipWhenBusy, includeReasoning }` config shape |
| `types.channels.ts` | `ChannelHeartbeatVisibilityConfig` shape (`showOk`, `showAlerts`, `useIndicator`) |
| `schema.help.ts` | Human-readable config descriptions for all heartbeat settings |
| `validation.ts` | Validates heartbeat target, directPolicy, and account references |

### Cron Integration (`src/cron/`)

| File | Purpose |
|------|---------|
| `heartbeat-policy.ts` | Determines whether a cron job should trigger a heartbeat wake and how |
| `service.heartbeat-ok-summary-suppressed.test.ts` | Test for suppressed heartbeat-OK summaries during cron |

### Session & Doctor (`src/commands/`, `src/config/sessions/`)

| File | Purpose |
|------|---------|
| `doctor-heartbeat-main-session-repair.ts` | Diagnostic repair for heartbeat main session configuration |
| `src/config/sessions/types.ts` | `heartbeatTaskState`, `heartbeatIsolatedBaseSessionKey` fields on session entries |

### Test Files (significant)

- `src/infra/heartbeat-runner.ts` — host file for the runner; ~20 test files adjacent
- `src/auto-reply/heartbeat.test.ts`, `heartbeat-filter.test.ts`
- `src/cron/heartbeat-policy.test.ts`
- `src/infra/heartbeat-cooldown.test.ts`, `heartbeat-wake.test.ts`, `heartbeat-active-hours.test.ts`, `heartbeat-visibility.test.ts`, `heartbeat-events.test.ts`, `heartbeat-events-filter.test.ts`, `heartbeat-summary.test.ts`, `heartbeat-schedule.test.ts`
- `src/infra/heartbeat-runner.sender-prefers-delivery-target.test.ts`
- `src/infra/heartbeat-runner.skips-busy-session-lane.test.ts`
- `src/infra/heartbeat-runner.timeout-warning.test.ts`
- `src/infra/heartbeat-runner.isolated-key-stability.test.ts`
- `src/infra/heartbeat-runner.tool-response.test.ts`
- `src/infra/heartbeat-runner.typing.test.ts`
- `src/infra/heartbeat-runner.returns-default-unset.test.ts`
- `src/infra/heartbeat-runner.response-prefix-template.test.ts`
- `src/infra/heartbeat-runner.model-override.test.ts`
- `src/infra/heartbeat-runner.ghost-reminder.test.ts`
- `src/infra/heartbeat-runner.commitments.test.ts`
- `src/infra/heartbeat-runner.subagent-session-guard.test.ts`
- `src/infra/heartbeat-runner.transcript-prune.test.ts`
- `src/infra/heartbeat-runner.scheduler.test.ts`
- `src/infra/heartbeat-runner.active-hours-schedule.e2e.test.ts`
- `src/auto-reply/reply/session.heartbeat-no-reset.test.ts`
- `src/config/heartbeat-config-honor.inventory.test.ts`
- `src/agents/heartbeat-system-prompt.test.ts`
- `src/agents/tools/heartbeat-response-tool.test.ts`

---

## 3. Step-by-Step Lifecycle

### 3.1 Runner Startup (`startHeartbeatRunner`)

1. **Resolve configuration** — `getRuntimeConfig()` merged with any provided `cfg` override.
2. **Resolve scheduler seed** — Uses `loadOrCreateDeviceIdentity().deviceId` or falls back to `sha256($HOME + cwd)`. This seed deterministically phase-shifts each agent's heartbeat ticks.
3. **Build agent list** — `resolveHeartbeatAgents(cfg)` determines which agents have heartbeat enabled. If any agent explicitly sets `heartbeat`, only those agents are included. Otherwise, all agents inherit `agents.defaults.heartbeat`, with the default agent as final fallback.
4. **Initialize agent state** — For each agent, compute:
   - `intervalMs` — parsed from `every` duration string (default: `"30m"`)
   - `phaseMs` — `sha256(seed:agentId) % intervalMs` for staggered ticks
   - `nextDueMs` — computed using `resolveNextHeartbeatDueMs` from current time
   - `activeHoursSchedule` — optional `start`/`end`/`timezone` window
5. **Register wake handler** — `setHeartbeatWakeHandler()` sets the dispatch function that wakes will call.
6. **Start timer loop** — `setTimeout` / `setInterval` drives periodic checks. On each timer tick, iterate agents and check if `Date.now() >= agent.nextDueMs`.

### 3.2 Wake Dispatch (`requestHeartbeat` → `heartbeat-wake.ts`)

Wakes arrive from many sources:

| Source | Intent | Description |
|--------|--------|-------------|
| `interval` | `scheduled` | Periodic timer tick |
| `manual` | `manual` | CLI `openclaw system event` or direct operator command |
| `exec-event` | `event` | Background process exit event |
| `notifications-event` | `event` | Node notification change |
| `cron` | `event`/`immediate` | Cron tick triggers heartbeat to deliver reminder |
| `hook` | `immediate` | Webhook `/hooks/wake mode=now` |
| `background-task` | `event` | Task completion notification |
| `acp-spawn` | `event` | ACP spawn stream update |
| `retry` | `event` | Retry of a previously skipped wake |
| `cli-watchdog` | `event` | CLI watchdog check |
| `restart-sentinel` | `event` | Process restart sentinel |

#### Wake Coalescing & Priority

- Each wake is enqueued as a `PendingWakeReason` keyed by `agentId::sessionKey`.
- **Priority ordering**: `ACTION` (manual/immediate = 3) > `DEFAULT` (2) > `INTERVAL` (1) > `RETRY` (0).
- When multiple wakes for the same target arrive, the highest-priority wins; ties go to newest timestamp.
- A **250ms coalescing window** (`DEFAULT_COALESCE_MS`) batches rapid-fire wakes before dispatching.

### 3.3 Cooldown Decision (`shouldDeferWake` — `heartbeat-cooldown.ts`)

The centralized cooldown module decides if a wake proceeds or defers:

| Intent | First wake (no history) | Subsequent wakes |
|--------|------------------------|------------------|
| `manual` | Run | Run (never deferred) |
| `immediate` | Run | Run (defer only on flood) |
| `scheduled` | Defer if `now < nextDueMs` | Defer if `now < nextDueMs` |
| `event` | Run (bootstrap responsive) | Defer if `now < nextDueMs` or within min-spacing floor |

Additional safety gates:
- **Min-spacing floor**: `DEFAULT_MIN_WAKE_SPACING_MS = 30_000` (30s) — prevents back-to-back runs even when schedule indicates due.
- **Flood guard**: `DEFAULT_FLOOD_WINDOW_MS = 60_000` (60s), `DEFAULT_FLOOD_THRESHOLD = 5` — if 5+ runs happened in 60s, defer regardless of reason (except `manual`).

### 3.4 The `runHeartbeatOnce` Execution Path

#### Phase 1: Guard Checks

1. **Global enable check** — `areHeartbeatsEnabled()`
2. **Agent enable check** — `isHeartbeatEnabledForAgent(cfg, agentId)`
3. **Interval check** — `resolveHeartbeatIntervalMs()` must return a positive number
4. **Active hours** — `isWithinActiveHours(cfg, heartbeat, nowMs)`
5. **Main lane busy** — If `getQueueSize(CommandLane.Main) > 0`, skip with `"requests-in-flight"` reason
6. **Cron/subagent busy** — If cron jobs are active or busy lanes have work, skip with `"cron-in-progress"` or `"lanes-busy"`
7. **Skip-when-busy opt-in** — `heartbeat.skipWhenBusy === true` checks subagent/nested lanes
8. **Pending delivery guard** — If recent session entry has `pendingFinalDelivery === true` within 30s, defer

#### Phase 2: Preflight (`resolveHeartbeatPreflight`)

1. **Classify wake type** — `isExecEventWake`, `isCronWake`, `isWakePayload`
2. **Resolve session** — `resolveHeartbeatSession()` determines session key, store path, and entry. Never routes to subagent sessions.
3. **Peek system events** — Inspect pending system event queue for the session
4. **Load due commitments** — If `target !== "none"`, select commitment delivery batch
5. **Read HEARTBEAT.md** — Load workspace `HEARTBEAT.md` (unless bypassed by wake type), check for tasks and effective emptiness
6. **Skip if empty** — If file is effectively empty AND no tasks AND no commitments, set `skipReason: "empty-heartbeat-file"`

#### Phase 3: Skip / Defer / Session Lane Check

- If `skipReason` is set, emit `skipped` event and return early.
- If resolved session's embedded lane is busy, skip with `"requests-in-flight"`.
- Check `useIsolatedSession` flag — if enabled, create a fresh `:heartbeat` suffixed session.

#### Phase 4: Prompt Resolution (`resolveHeartbeatRunPrompt`)

The prompt is assembled based on content type:

| Condition | Prompt Behavior |
|-----------|----------------|
| Due heartbeat tasks exist | `"Run the following periodic tasks (only those due based on their intervals):\n{taskList}\n{completionInstruction}"` + HEARTBEAT.md directives |
| Exec completion events | `buildExecEventPrompt(events)` — relays command output |
| Cron system events | `buildCronEventPrompt(events)` — relays reminder content |
| Commitments due | `buildCommitmentHeartbeatPrompt(commitments)` |
| Default (periodic poll) | `HEARTBEAT_PROMPT`: "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK." |

For `heartbeat_respond` tool mode:
- Tool instructions are appended: "Use heartbeat_respond to report the wake outcome. Set notify=false when nothing needs the user's attention. Set notify=true with notificationText only when the user should be interrupted."

#### Phase 5: Agent Invocation

- The prompt is sent as a synthetic user message with `Provider: "heartbeat"` marker.
- If `heartbeat.model` is set, it overrides the default model for this turn.
- If `heartbeat.timeoutSeconds` is set, it overrides the default agent timeout.
- If `heartbeat.suppressToolErrorWarnings === true`, tool error payloads are suppressed.
- If `heartbeat.lightContext === true`, only HEARTBEAT.md is loaded (lightweight bootstrap).
- If `heartbeat.includeReasoning === true`, reasoning payloads are extracted and delivered separately.

#### Phase 6: Response Classification

After the model responds, one of three paths:

1. **Heartbeat Response Tool** — If `heartbeat_respond` was used:
   - `notify: false` → Silent OK, emit `"ok-token"`, optionally send `HEARTBEAT_OK` text if `showOk`.
   - `notify: true` → Extract `notificationText`, prepare for delivery.

2. **HEARTBEAT_OK token** — If response text matches `HEARTBEAT_OK` (with tolerance for trailing punctuation, markup wrapping, ack text up to `ackMaxChars`):
   - `stripHeartbeatToken()` normalizes the response.
   - If `shouldSkip === true`, send `HEARTBEAT_OK` acknowledgment if `showOk` and channel has delivery target.

3. **Substantive content** — If the response contains actual text beyond ack:
   - Strip the `HEARTBEAT_OK` prefix.
   - Apply `responsePrefix` if configured.
   - Deliver as a message to the target channel/user.

#### Phase 7: Delivery

- `resolveHeartbeatDeliveryTarget()` determines the target channel, `to`, `accountId`, `threadId`.
- `resolveHeartbeatVisibility()` determines whether `showOk`, `showAlerts`, and `useIndicator` are on.
- Channel readiness is checked via `heartbeat.checkReady()`.
- Message is sent via `sendDurableMessageBatch()`.
- Duplicate suppression: if `normalized.text === prevHeartbeatText` within 24 hours, skip as `"duplicate"`.

#### Phase 8: Post-Run

- **Update task timestamps** — Mark due tasks as run in `session.heartbeatTaskState`.
- **Consume system events** — Drain processed system events from the queue.
- **Mark commitments** — Set status to `"sent"` or `"dismissed"`.
- **Emit event** — `emitHeartbeatEvent()` with status, duration, channel, etc.
- **Advance schedule** — Compute next `nextDueMs` for this agent.
- **Restore `updatedAt`** on session if the heartbeat was a no-op (OK response), preserving previous timestamp.

---

## 4. Data Structures

### `HeartbeatAgentState`

```typescript
type HeartbeatAgentState = {
  agentId: string;
  heartbeat?: HeartbeatConfig;
  activeHoursSchedule?: ActiveHoursSchedule;
  intervalMs: number;
  phaseMs: number;
  nextDueMs: number;
  lastRunStartedAtMs?: number;
  recentRunStarts: number[];       // Bounded ring buffer for flood detection
  floodLoggedSinceLastRun: boolean;
};
```

### `HeartbeatConfig`

```typescript
heartbeat?: {
  every?: string;                    // Duration string (default "30m")
  activeHours?: {
    start?: string;                  // HH:MM (inclusive)
    end?: string;                     // HH:MM (exclusive, "24:00" = midnight)
    timezone?: string;               // "user" | "local" | IANA TZ
  };
  model?: string;                    // Provider/model override
  session?: string;                   // "main" or explicit session key
  target?: string;                    // "last" | "none" | channel id
  directPolicy?: "allow" | "block";  // DM delivery policy
  to?: string;                        // Delivery target override
  accountId?: string;                 // Multi-account channel target
  prompt?: string;                    // Override heartbeat prompt
  includeSystemPromptSection?: boolean; // Default true
  ackMaxChars?: number;              // Default 300 (was 30)
  suppressToolErrorWarnings?: boolean;
  timeoutSeconds?: number;
  lightContext?: boolean;             // Lightweight bootstrap
  isolatedSession?: boolean;          // Fresh session per run
  skipWhenBusy?: boolean;             // Defer on subagent/nested busy
  includeReasoning?: boolean;          // Deliver reasoning payloads
};
```

### `HeartbeatEventPayload`

```typescript
type HeartbeatEventPayload = {
  ts: number;
  status: "sent" | "ok-empty" | "ok-token" | "skipped" | "failed";
  to?: string;
  accountId?: string;
  preview?: string;
  durationMs?: number;
  hasMedia?: boolean;
  reason?: string;
  channel?: string;
  silent?: boolean;
  indicatorType?: "ok" | "alert" | "error";
};
```

### `HeartbeatRunResult`

```typescript
type HeartbeatRunResult =
  | { status: "ran"; durationMs: number }
  | { status: "skipped"; reason: string }
  | { status: "failed"; reason: string };
```

### `HeartbeatWakeRequest`

```typescript
type HeartbeatWakeRequest = {
  source: HeartbeatWakeSource;
  intent: HeartbeatWakeIntent;
  reason?: string;
  agentId?: string;
  sessionKey?: string;
  heartbeat?: { target?: string };
};
```

### `HeartbeatToolResponse`

```typescript
type HeartbeatToolResponse = {
  outcome: "no_change" | "progress" | "done" | "blocked" | "needs_attention";
  notify: boolean;
  summary: string;
  notificationText?: string;
  reason?: string;
  priority?: "low" | "normal" | "high";
  nextCheck?: string;
};
```

### `HeartbeatSummary` (Diagnostic)

```typescript
type HeartbeatSummary = {
  enabled: boolean;
  every: string;
  everyMs: number | null;
  prompt: string;
  target: string;
  model?: string;
  ackMaxChars: number;
};
```

### `DeferDecision`

```typescript
type DeferDecision =
  | { defer: false }
  | { defer: true; reason: "not-due" | "min-spacing" | "flood" };
```

### `HeartbeatTask` (from HEARTBEAT.md)

```typescript
type HeartbeatTask = {
  name: string;
  interval: string;   // Duration string
  prompt: string;
};
```

### `ChannelHeartbeatVisibilityConfig`

```typescript
type ChannelHeartbeatVisibilityConfig = {
  showOk?: boolean;       // Show healthy/OK status (default: false)
  showAlerts?: boolean;    // Show alert content messages (default: true)
  useIndicator?: boolean;  // Emit indicator events (default: true)
};
```

### `ActiveHoursSchedule`

```typescript
type ActiveHoursSchedule = {
  start?: string;      // "09:00"
  end?: string;         // "22:00"
  timezone: string;     // "America/New_York" or "user" or "local"
};
```

---

## 5. Configuration Options

### 5.1 Agent-Level Heartbeat Config (`agents.defaults.heartbeat` / `agents.list[].heartbeat`)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `every` | `string` | `"30m"` | Interval duration. Supports `5m`, `1h`, `30s` etc. Default unit is minutes. |
| `activeHours.start` | `string` | — (always on) | HH:MM start of active window (inclusive). |
| `activeHours.end` | `string` | — (always on) | HH:MM end of active window (exclusive). Use `"24:00"` for midnight. |
| `activeHours.timezone` | `string` | `"user"` | Timezone: `"user"` (agent's timezone), `"local"` (host TZ), or IANA identifier. |
| `model` | `string` | — (agent default) | Provider/model override for heartbeat turns only. |
| `session` | `string` | — (main) | `"main"` or explicit session key. Never routes to subagent sessions. |
| `target` | `string` | `"none"` | Delivery target: `"last"` (last known channel), `"none"` (no delivery), or a channel ID. |
| `directPolicy` | `"allow"\|"block"` | `"allow"` | Whether heartbeat DMs are allowed. |
| `to` | `string` | — | Explicit E.164 (WhatsApp) or chat ID (Telegram) delivery override. Supports `:topic:NNN` suffix. |
| `accountId` | `string` | — | Multi-account channel target. |
| `prompt` | `string` | (default prompt) | Override the heartbeat prompt body. |
| `includeSystemPromptSection` | `boolean` | `true` | Whether to inject `## Heartbeats` section into agent system prompt. |
| `ackMaxChars` | `number` | `300` | Max chars after `HEARTBEAT_OK` before the response is considered substantive (not just an ack). |
| `suppressToolErrorWarnings` | `boolean` | `false` | Suppress tool error payloads during heartbeat turns. |
| `timeoutSeconds` | `number` | — (agent default) | Per-run timeout override. |
| `lightContext` | `boolean` | `false` | Use lightweight bootstrap context (only HEARTBEAT.md from workspace). |
| `isolatedSession` | `boolean` | `false` | Run each heartbeat in a fresh isolated session (`key:heartbeat`). |
| `skipWhenBusy` | `boolean` | `false` | Defer on subagent/nested busy lanes. |
| `includeReasoning` | `boolean` | `false` | Deliver model reasoning as separate message. |

### 5.2 Channel-Level Visibility Config (`channels.defaults.heartbeat` / `channels.<channel>.heartbeat`)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `showOk` | `boolean` | `false` | Show healthy/OK heartbeat status entries. |
| `showAlerts` | `boolean` | `true` | Show content alert messages. |
| `useIndicator` | `boolean` | `true` | Emit indicator-style status events (for UI dashboards). |

Per-account overrides are supported under `channels.<channel>.accounts.<accountId>.heartbeat`.

### 5.3 Web Channel Config (`web.heartbeatSeconds`)

WebSocket heartbeat interval for webchat connections (separate from agent heartbeat).

### 5.4 HEARTBEAT.md (Workspace File)

Agents can have a `HEARTBEAT.md` file in their workspace directory. This file:

- Contains freeform directives for the agent to follow during heartbeat runs.
- Can include a YAML `tasks:` block with periodic task definitions:
  ```yaml
  tasks:
    - name: email-check
      interval: 30m
      prompt: "Check for urgent unread emails"
    - name: daily-summary
      interval: 4h
      prompt: "Summarize today's important events"
  ```
- If the file is effectively empty (only headers, empty list items, and code fences), the heartbeat skips with reason `"empty-heartbeat-file"` — saving an LLM API call.

### 5.5 HEARTBEAT_OK Token

The sentinel token `HEARTBEAT_OK` signals "nothing needs attention." Responses are classified:

- **Pure `HEARTBEAT_OK`** (possibly with trailing punctuation) → Silent ack, optionally send `HEARTBEAT_OK` text if `showOk`.
- **`HEARTBEAT_OK` followed by ≤ `ackMaxChars` of text** → Still treated as ack, skipped.
- **Substantive content** beyond `ackMaxChars` → Delivered as a message.

The token stripping is robust: handles Markdown (`**HEARTBEAT_OK**`) and HTML (`<b>HEARTBEAT_OK</b>`) wrappers.

---

## 6. Error Handling

### 6.1 Skip Reasons

| Reason | Source | Description |
|--------|--------|-------------|
| `disabled` | `runHeartbeatOnce` | Heartbeats globally disabled or agent not configured for heartbeat |
| `quiet-hours` | `runHeartbeatOnce` | Current time falls outside `activeHours` window |
| `requests-in-flight` | `runHeartbeatOnce` | Main lane or session lane has queued work |
| `cron-in-progress` | `runHeartbeatOnce` | Active cron jobs running |
| `lanes-busy` | `runHeartbeatOnce` | Subagent/nested lanes have work (when `skipWhenBusy`) |
| `empty-heartbeat-file` | Preflight | HEARTBEAT.md exists but is empty and no tasks/commitments are due |
| `no-tasks-due` | Preflight | No tasks, events, or commitments warrant a run |
| `alerts-disabled` | `runHeartbeatOnce` | Channel visibility config suppresses both `showOk` and `showAlerts` |
| `duplicate` | `runHeartbeatOnce` | Same text payload sent within 24h |
| (channel not ready) | `runHeartbeatOnce` | Channel plugin `checkReady()` returned not-ok |

### 6.2 Deferral Reasons (`shouldDeferWake`)

| Reason | Description |
|--------|-------------|
| `not-due` | `now < nextDueMs` for scheduled/event intents |
| `min-spacing` | Last run started within 30s floor |
| `flood` | ≥5 runs within 60s window |

### 6.3 Retry Behavior

When a heartbeat run is skipped with a **retryable** reason (`requests-in-flight`, `cron-in-progress`, `lanes-busy`), the wake dispatch automatically re-enqueues the wake with source=`"retry"` and schedules a 1-second retry timer. This continues until the run succeeds, floods, or times out.

### 6.4 Error Recovery in `runHeartbeatOnce`

- **try/catch** wraps the entire execution. On failure, `emitHeartbeatEvent({ status: "failed", reason })` is emitted and `{ status: "failed", reason }` is returned.
- **Session `updatedAt` restoration**: When a heartbeat produces only an OK/empty response, the previous `updatedAt` is restored so that regular messages don't see phantom updates.
- **Isolated session cleanup**: In isolated session mode, stale `:heartbeat` sessions from previous runs are cleaned up, and their transcript files are archived.

### 6.5 Channel Delivery Failures

- `sendDurableMessageBatch` returns `{ status: "failed" | "partial_failed", error }`. On failure, the error is thrown, caught by the outer try/catch, and reported as a `failed` heartbeat event.

---

## 7. Message Types & Protocols

### 7.1 Heartbeat Wake Intents

| Intent | Semantics |
|--------|-----------|
| `scheduled` | Periodic interval tick |
| `event` | External system event (exec, cron, ACP, notification) |
| `immediate` | Wake-now delivery (CLI event, hook with `mode=now`, cron `--wake now`) |
| `manual` | Direct operator command (never deferred) |

### 7.2 Wake Sources

```
"interval" | "manual" | "exec-event" | "notifications-event" | "cron" |
"hook" | "background-task" | "background-task-blocked" | "acp-spawn" |
"cli-watchdog" | "restart-sentinel" | "retry" | "other"
```

### 7.3 Event Status Types

| Status | Description |
|--------|-------------|
| `sent` | Content was delivered to the user |
| `ok-empty` | Model returned empty/OK, sent as ack |
| `ok-token` | Model used `heartbeat_respond(notify=false)` or text-based `HEARTBEAT_OK` with short ack |
| `skipped` | Run was skipped for any reason |
| `failed` | An error occurred |

### 7.4 Indicator Types

| Type | Trigger |
|------|---------|
| `ok` | `ok-empty` or `ok-token` status |
| `alert` | `sent` status |
| `error` | `failed` status |

### 7.5 Provider Marker

Heartbeat synthetic messages use `Provider: "heartbeat"` (or `"exec-event"`, `"cron-event"`) to separate them from regular user messages in the agent context.

### 7.6 Heartbeat Response Tool Schema

```json
{
  "name": "heartbeat_respond",
  "parameters": {
    "outcome": { "enum": ["no_change", "progress", "done", "blocked", "needs_attention"] },
    "notify": { "type": "boolean" },
    "summary": { "type": "string" },
    "notificationText": { "type": "string" },
    "reason": { "type": "string" },
    "priority": { "enum": ["low", "normal", "high"] },
    "nextCheck": { "type": "string" }
  }
}
```

The `outcome` field classifies the wake result:
- `no_change` — Nothing changed, no action needed.
- `progress` — Work in progress, no user action required.
- `done` — Task completed successfully.
- `blocked` — Blocked on external input or dependency.
- `needs_attention` — The user should be notified.

---

## 8. Integration with Other Systems

### 8.1 Session System

- Heartbeat runs operate on **session entries** stored in JSON session stores.
- `resolveHeartbeatSession()` determines which session the heartbeat targets, never allowing subagent sessions.
- When `isolatedSession = true`, a fresh `sessionKey:heartbeat` session is created for each run, with the `:heartbeat` suffix collapsed on re-entry.
- Session entries track: `heartbeatTaskState` (task last-run timestamps), `heartbeatIsolatedBaseSessionKey`, `lastHeartbeatText`, `lastHeartbeatSentAt`, `pendingFinalDelivery`, `updatedAt`.

### 8.2 Commitments System (`src/commitments/`)

- Heartbeats can deliver **inferred follow-up commitments** — reminders that the system infers from conversation context.
- `listDueCommitmentsForSession()` fetches commitments whose due window overlaps with `nowMs`.
- `selectCommitmentDeliveryBatch()` groups commitments by delivery key (channel + account + to + threadId + senderId) and selects the earliest batch.
- After delivery, `markCommitmentsStatus()` sets commitments to `"sent"` or `"dismissed"`.

### 8.3 Cron System (`src/cron/`)

- Cron events trigger heartbeat wakes via `requestHeartbeat({ source: "cron", intent: "event" })`.
- Cron events are identified by `contextKey` starting with `"cron:"`.
- `heartbeat-policy.ts` determines whether a cron tick should wake the heartbeat and with what mode.
- Cron wakes are treated as `"event"` or `"immediate"` intent depending on the `--wake` flag.

### 8.4 Exec/Background Task System (`src/process/`)

- When a background process exits, a `"exec-event"` wake is requested.
- `heartbeat-events-filter.ts` classifies exec events: `isExecCompletionEvent()` and `isRelayableExecCompletionEvent()`.
- Relayable exec events are delivered to the user; non-relayable (success with no output) are absorbed.

### 8.5 Auto-Reply / Agent Runner (`src/auto-reply/`, `src/agents/`)

- Heartbeat prompts are injected as synthetic user messages via `getReplyFromConfig`.
- The `heartbeat_respond` tool is conditionally enabled during heartbeat turns (`enableHeartbeatTool: true`).
- Response is processed by `resolveHeartbeatReplyPayload()` and normalized by `normalizeHeartbeatReply()`.
- The `heartbeat-filter.ts` module provides `filterHeartbeatPairs()` for **pruning heartbeat noise from conversation context** — pairs of user-message + OK-response are stripped to save tokens.

### 8.6 Channel Plugins (`src/channels/plugins/`)

- Channel plugins expose `heartbeat.sendTyping()`, `heartbeat.clearTyping()`, and `heartbeat.checkReady()` hooks.
- Plugins control typing indicator start/stop during agent execution.
- `checkReady()` gates delivery — returns `{ ok: boolean, reason: string }` before sending.

### 8.7 System Prompt (`heartbeat-system-prompt.ts`)

- When heartbeat is enabled and `includeSystemPromptSection !== false`, a `## Heartbeats` section is injected into the agent's system prompt.
- `shouldIncludeHeartbeatGuidanceForSystemPrompt()` checks: agent is the default agent, heartbeat is enabled, cadence is valid, and the config flag is not false.

### 8.8 Plugin SDK (`src/plugin-sdk/heartbeat-runtime.ts`)

- Re-exports: `HeartbeatEventPayload`, `HeartbeatIndicatorType`, `resolveHeartbeatVisibility`, `onHeartbeatEvent`, `getLastHeartbeatEvent`, `requestHeartbeat`.
- This is the narrow public API surface that plugins can use to interact with the heartbeat system.

### 8.9 Outbound Delivery (`src/infra/outbound/`)

- `resolveHeartbeatDeliveryTarget()` resolves channel, `to`, `accountId`, `threadId` from config + session state.
- `resolveHeartbeatSenderContext()` resolves the `From` address for the synthetic heartbeat message.
- `sendDurableMessageBatch()` handles batch message delivery with retry semantics.

### 8.10 Doctor Command (`src/commands/doctor-heartbeat-main-session-repair.ts`)

- `openclaw doctor` can diagnose and repair misconfigured heartbeat sessions, ensuring the main session key is correctly set up for heartbeat delivery.

---

## 9. Strengths & Weaknesses

### Strengths

1. **Phase-aligned scheduling**: Staggered tick offsets prevent all agents from waking simultaneously, reducing load spikes.

2. **Multi-source wake dispatch**: The system can be triggered by many events, not just timers. This creates a responsive system where background task completions, cron reminders, and webhooks all feed into the same intelligent dispatch pipeline.

3. **Flood protection**: The ring-buffer + flood threshold mechanism (5 runs in 60s) prevents cascading agent-triggered heartbeats, a real problem in agentic systems.

4. **Comprehensive skip/defer logic**: The three-tier skip system (guard checks → cooldown → active hours) prevents unnecessary LLM API calls while remaining responsive to important events.

5. **Commitment delivery fusion**: Heartbeats seamlessly blend scheduled reminders, background event notifications, and periodic HEARTBEAT.md assessments into a single agent turn.

6. **Isolated session mode**: The `isolatedSession` option dramatically reduces token costs for routine checks by avoiding the full conversation transcript.

7. **Structured response tool**: The `heartbeat_respond` tool gives the model a clear API for classifying outcomes rather than relying solely on text parsing.

8. **Duplicate suppression**: 24-hour dedup of identical heartbeat payloads prevents "nagging" the user.

9. **Visibility configurability**: The three-layer visibility system (`showOk`, `showAlerts`, `useIndicator`) with per-account overrides allows fine-grained control over what users see.

10. **Active hours**: Timezone-aware active hours windows prevent heartbeats from waking users at night.

### Weaknesses

1. **Monolithic runner**: `heartbeat-runner.ts` is 2377 lines. It handles scheduling, preflight, session resolution, prompt building, LLM invocation, delivery, event emission, and post-run bookkeeping all in one file. This makes testing and understanding difficult.

2. **Global singleton state**: The wake dispatch (`heartbeat-wake.ts`) uses module-level state for the timer, pending wakes map, and handler — making it harder to test in parallel and requiring explicit `resetHeartbeatWakeStateForTests()`.

3. **Hard-coded constants**: `DEFAULT_MIN_WAKE_SPACING_MS = 30000`, `DEFAULT_FLOOD_WINDOW_MS = 60000`, `DEFAULT_FLOOD_THRESHOLD = 5`, `HEARTBEAT_DEFER_WINDOW_MS = 30000`, duplicate dedup window of 24h — these are not configurable.

4. **No backpressure on agent runner**: If the LLM provider is slow or rate-limited, there's no explicit mechanism to slow down heartbeat scheduling. The `min-spacing` floor helps but doesn't adapt to provider latency.

5. **Session store coupling**: The heartbeat system directly reads and mutates session store files. This creates tight coupling between the scheduling layer and the persistence layer.

6. **HEARTBEAT.md task parsing is rudimentary**: `parseHeartbeatTasks()` uses a simple line-by-line parser that doesn't handle nested YAML, multiline prompts, or quoted strings with internal colons robustly.

7. **Limited observability**: While `emitHeartbeatEvent()` exists, there's no built-in metrics aggregation. Events are in-memory only and lost on restart.

8. **Typing indicator coupling**: `heartbeat-typing.ts` directly integrates with channel plugins, creating a tight coupling between the heartbeat system and delivery infrastructure.

9. **Isolated session key collision**: The `:heartbeat` suffix collapsing logic can be confusing. If a user sets `heartbeat.session: "alerts:heartbeat"`, the system must handle this edge case specially (lines 593-608 of runner).

10. **No persistence of skip history**: The `recentRunStarts` ring buffer for flood detection is in-memory and lost on restart, meaning a restart resets the flood guard.

---

## 10. Complete Mermaid Flowchart

```mermaid
flowchart TD
    subgraph WakeSources["Wake Sources"]
        direction LR
        TIMER["⏰ Interval Timer<br/>(scheduled)"]
        MANUAL["👤 Manual / CLI<br/>(manual)"]
        EXEC["⚙️ Exec Completion<br/>(event)"]
        CRON["📅 Cron Tick<br/>(event/immediate)"]
        HOOK["🪝 Webhook / Hook<br/>(immediate)"]
        NOTIF["🔔 Notification Change<br/>(event)"]
        ACP["🚀 ACP Spawn<br/>(event)"]
        TASK["📋 Background Task<br/>(event)"]
        RETRY["🔄 Retry<br/>(event)"]
        WATCHDOG["🐕 CLI Watchdog<br/>(event)"]
        SENTINEL["🔄 Restart Sentinel<br/>(event)"]
    end

    WAKE_QUEUE["requestHeartbeat()<br/>Wake Queue<br/>(coalesced, 250ms window)"]
    {TIMER, MANUAL, EXEC, CRON, HOOK, NOTIF, ACP, TASK, RETRY, WATCHDOG, SENTINEL} --> WAKE_QUEUE

    subgraph WakeDispatch["Wake Dispatch (heartbeat-wake.ts)"]
        direction TB
        PENDING["PendingWakeReason Map<br/>(agentId::sessionKey → wake)"]
        PRIORITIZE["Priority Resolution<br/>manual(3) > default(2) > interval(1) > retry(0)"]
        SCHEDULE["schedule()<br/>Timer: coalesce or retry"]
        
        WAKE_QUEUE --> PENDING
        PENDING --> PRIORITIZE
        PRIORITIZE --> SCHEDULE
    end

    subgraph CooldownDecision["Cooldown Decision (heartbeat-cooldown.ts)"]
        direction TB
        SHOULD_DEFER{"shouldDeferWake()"}
        MANUAL_CHECK{"intent = manual?"}
        IMMEDIATE_CHECK{"intent = immediate?"}
        FLOOD_CHECK{"Flood guard?<br/>≥5 runs in 60s"}
        NOT_DUE{"now < nextDueMs?"}
        MIN_SPACING{"now - lastRunStart<br/>< 30s?"}
        
        SHOULD_DEFER --> MANUAL_CHECK
        MANUAL_CHECK -- No --> IMMEDIATE_CHECK
        MANUAL_CHECK -- Yes --> RUN["✅ Run"]
        IMMEDIATE_CHECK -- No --> FLOOD_CHECK
        IMMEDIATE_CHECK -- Yes --> RUN_IMM["✅ Run (unless flood)"]
        FLOOD_CHECK -- Flood detected --> DEFER_FLOOD["⏸️ Defer: flood"]
        FLOOD_CHECK -- No flood --> NOT_DUE
        NOT_DUE -- Yes --> DEFER_NOT_DUE["⏸️ Defer: not-due"]
        NOT_DUE -- No --> MIN_SPACING
        MIN_SPACING -- Yes --> DEFER_SPACING["⏸️ Defer: min-spacing"]
        MIN_SPACING -- No --> RUN
    end

    SCHEDULE --> SHOULD_DEFER
    DEFER_FLOOD --> RETRY_QUEUE["Re-enqueue as retry<br/>(1s delay)"]
    DEFER_NOT_DUE --> RETRY_QUEUE
    DEFER_SPACING --> RETRY_QUEUE
    RETRY_QUEUE --> SCHEDULE

    subgraph RunHeartbeat["runHeartbeatOnce (heartbeat-runner.ts)"]
        direction TB
        
        subgraph GuardChecks["Guard Checks"]
            ENABLED{"Heartbeats<br/>enabled?"}
            AGENT_ENABLED{"Agent<br/>enabled?"}
            INTERVAL{"Interval<br/>valid?"}
            ACTIVE_HOURS{"Within<br/>active hours?"}
            MAIN_BUSY{"Main lane<br/>busy?"}
            CRON_BUSY{"Cron lane<br/>busy?"}
            OPT_BUSY{"skipWhenBusy<br/>lanes busy?"}
            PENDING_DELIVERY{"Pending final<br/>delivery < 30s?"}
        end
        
        ENABLED -- No --> SKIP_DISABLED["⏭️ Skipped: disabled"]
        AGENT_ENABLED -- No --> SKIP_DISABLED
        INTERVAL -- No --> SKIP_DISABLED
        ACTIVE_HOURS -- No --> SKIP_QUIET["⏭️ Skipped: quiet-hours"]
        MAIN_BUSY -- Yes --> SKIP_INFLIGHT["⏭️ Skipped: requests-in-flight"]
        CRON_BUSY -- Yes --> SKIP_CRON["⏭️ Skipped: cron-in-progress"]
        OPT_BUSY -- Yes --> SKIP_BUSY["⏭️ Skipped: lanes-busy"]
        PENDING_DELIVERY -- Yes --> SKIP_INFLIGHT
        
        subgraph Preflight["Preflight"]
            CLASSIFY["Classify wake type<br/>(exec/cron/wake)"]
            RESOLVE_SESSION["Resolve session<br/>(never subagent)"]
            PEEK_EVENTS["Peek system events"]
            LOAD_COMMITMENTS["Load due commitments"]
            READ_HEARTBEAT_MD["Read HEARTBEAT.md"]
            PARSE_TASKS["Parse YAML tasks"]
            CHECK_EMPTY{"File empty<br/>& no tasks/commitments?"}
            
            CLASSIFY --> RESOLVE_SESSION
            RESOLVE_SESSION --> PEEK_EVENTS
            PEEK_EVENTS --> LOAD_COMMITMENTS
            LOAD_COMMITMENTS --> READ_HEARTBEAT_MD
            READ_HEARTBEAT_MD --> PARSE_TASKS
            PARSE_TASKS --> CHECK_EMPTY
        end
        
        CHECK_EMPTY -- Yes --> SKIP_EMPTY["⏭️ Skipped: empty-heartbeat-file"]
        
        SESSION_LANE{"Session lane<br/>busy?"}
        SESSION_LANE -- Yes --> SKIP_INFLIGHT2["⏭️ Skipped: requests-in-flight"]
        
        subgraph PromptResolution["Prompt Resolution"]
            RESOLVE_PROMPT{"What to ask<br/>the agent?"}
            TASKS_DUE{"Due tasks<br/>exist?"}
            EXEC_EVENTS{"Exec completion<br/>events?"}
            CRON_EVENTS{"Cron system<br/>events?"}
            COMMITMENTS{"Due<br/>commitments?"}
            DEFAULT_PROMPT["Default HEARTBEAT.md prompt<br/>+ HEARTBEAT_OK"]
            
            RESOLVE_PROMPT --> TASKS_DUE
            TASKS_DUE -- Yes --> TASK_PROMPT["Task list prompt<br/>(+ HEARTBEAT.md directives)"]
            TASKS_DUE -- No --> EXEC_EVENTS
            EXEC_EVENTS -- Yes --> EXEC_PROMPT["Exec event prompt"]
            EXEC_EVENTS -- No --> CRON_EVENTS
            CRON_EVENTS -- Yes --> CRON_PROMPT["Cron event prompt"]
            CRON_EVENTS -- No --> COMMITMENTS
            COMMITMENTS -- Yes --> COMMIT_PROMPT["Commitment prompt<br/>(+ base prompt)"]
            COMMITMENTS -- No --> DEFAULT_PROMPT
            
            NO_PROMPT{"Prompt<br/>resolved?"}
            NO_PROMPT -- No --> SKIP_NO_TASKS["⏭️ Skipped: no-tasks-due"]
        end

        subgraph Isolation["Isolated Session (if enabled)"]
            CREATE_ISOLATED["Create :heartbeat session<br/>(fresh transcript)"]
            CLEANUP_STALE["Archive stale isolated sessions"]
        end
        
        subgraph AgentInvocation["Agent Invocation"]
            INVOKE_AGENT["getReplyFromConfig()<<br/>Synthetic user message<br/>Provider: heartbeat/cron-event/exec-event"]
            RESPONSE["Agent response"]
        end
        
        subgraph ResponseClassification["Response Classification"]
            TOOL_RESP{"heartbeat_respond<br/>tool used?"}
            NOTIFY_FALSE{"notify = false?"}
            TOKEN_CHECK{"HEARTBEAT_OK<br/>or short ack?"}
            CONTENT_CHECK{"Substantive<br/>content?"}
            
            TOOL_RESP -- Yes --> NOTIFY_FALSE
            NOTIFY_FALSE -- Yes --> OK_TOKEN["✅ ok-token<br/>(optionally send HEARTBEAT_OK)"]
            NOTIFY_FALSE -- No --> DELIVER_NOTIFICATION["📩 Deliver notificationText"]
            
            TOOL_RESP -- No --> TOKEN_CHECK
            TOKEN_CHECK -- Yes --> REPLY_ACK["✅ ok-empty or ok-token"]
            TOKEN_CHECK -- No --> CONTENT_CHECK
            CONTENT_CHECK -- Yes --> DELIVER_CONTENT["📩 Deliver content"]
            CONTENT_CHECK -- No --> REPLY_ACK
            
            DUPE_CHECK{"Duplicate within<br/>24 hours?"}
            DUPE_CHECK -- Yes --> SKIP_DUPE["⏭️ Skipped: duplicate"]
            DUPE_CHECK -- No --> DELIVER_CONTENT
        end
        
        subgraph Delivery["Delivery"]
            RESOLVE_TARGET["Resolve delivery target<br/>(channel, to, accountId, threadId)"]
            RESOLVE_VISIBILITY["Resolve visibility<br/>(showOk, showAlerts, useIndicator)"]
            CHANNEL_READY{"Channel<br/>ready?"}
            SEND["sendDurableMessageBatch()"]
            
            RESOLVE_TARGET --> RESOLVE_VISIBILITY
            RESOLVE_VISIBILITY --> CHANNEL_READY
            CHANNEL_READY -- No --> SKIP_NOT_READY["⏭️ Skipped: channel-not-ready"]
            CHANNEL_READY -- Yes --> SEND
        end
        
        subgraph PostRun["Post-Run Bookkeeping"]
            UPDATE_TASKS["Update task timestamps<br/>(session.heartbeatTaskState)"]
            CONSUME_EVENTS["Consume system events"]
            MARK_COMMITMENTS["Mark commitments<br/>(sent/dismissed)"]
            EMIT_EVENT["emitHeartbeatEvent()"]
            ADVANCE_SCHEDULE["Advance schedule<br/>(nextDueMs)"]
            RESTORE_UPDATEDAT["Restore session updatedAt<br/>(if OK/empty)"]
        end
    end
    
    subgraph EventEmission["Event Emission (heartbeat-events.ts)"]
        EVENT_OBJ["HeartbeatEventPayload<br/>(ts, status, reason, channel, ...)"]
        LISTENERS["onHeartbeatEvent() listeners<br/>(UI, metrics, logging)"]
        LAST_EVENT["getLastHeartbeatEvent()<br/>(singleton state)"]
        
        EVENT_OBJ --> LISTENERS
        EVENT_OBJ --> LAST_EVENT
    end
    
    Run_Heartbeat --> GUARD_CHECKS
    GUARD_CHECKS -- Pass --> PREFLIGHT
    PREFLIGHT --> SESSION_LANE
    SESSION_LANE -- No --> PROMPT_RESOLUTION
    PROMPT_RESOLUTION --> AGENT_INVOCATION
    AGENT_INVOCATION --> RESPONSE_CLASSIFICATION
    RESPONSE_CLASSIFICATION --> DELIVERY
    DELIVERY --> POST_RUN
    POST_RUN --> EVENT_EMISSION

    style Run_Heartbeat fill:#1a1a2e,stroke:#e94560,color:#fff
    style WakeDispatch fill:#16213e,stroke:#0f3460,color:#fff
    style CooldownDecision fill:#1a1a2e,stroke:#e94560,color:#fff
    style GuardChecks fill:#16213e,stroke:#533483,color:#fff
    style EventEmission fill:#0f3460,stroke:#e94560,color:#fff

    linkStyle default stroke:#533483,stroke-width:2px
```

---

## Appendix A: Key Constants

| Constant | Value | Location |
|----------|-------|----------|
| `HEARTBEAT_TOKEN` | `"HEARTBEAT_OK"` | `src/auto-reply/tokens.ts` |
| `DEFAULT_HEARTBEAT_EVERY` | `"30m"` | `src/auto-reply/heartbeat.ts` |
| `DEFAULT_HEARTBEAT_ACK_MAX_CHARS` | `300` | `src/auto-reply/heartbeat.ts` |
| `DEFAULT_MIN_WAKE_SPACING_MS` | `30000` (30s) | `src/infra/heartbeat-cooldown.ts` |
| `DEFAULT_FLOOD_WINDOW_MS` | `60000` (60s) | `src/infra/heartbeat-cooldown.ts` |
| `DEFAULT_FLOOD_THRESHOLD` | `5` | `src/infra/heartbeat-cooldown.ts` |
| `DEFAULT_COALESCE_MS` | `250` | `src/infra/heartbeat-wake.ts` |
| `DEFAULT_RETRY_MS` | `1000` | `src/infra/heartbeat-wake.ts` |
| `MAX_SEEK_HORIZON_MS` | `604800000` (7 days) | `src/infra/heartbeat-schedule.ts` |
| `HEARTBEAT_DEFER_WINDOW_MS` | `30000` (30s) | `src/infra/heartbeat-runner.ts` |
| `DEFAULT_HEARTBEAT_TYPING_INTERVAL_SECONDS` | `6` | `src/infra/heartbeat-typing.ts` |
| `HEARTBEAT_RESPONSE_TOOL_NAME` | `"heartbeat_respond"` | `src/auto-reply/heartbeat-tool-response.ts` |
| `HEARTBEAT_TRANSCRIPT_PROMPT` | `"[OpenClaw heartbeat poll]"` | `src/auto-reply/heartbeat.ts` |

## Appendix B: Config Resolution Precedence

### Heartbeat Config (`agents.defaults.heartbeat` + `agents.list[].heartbeat`)

```
Per-agent override > Global defaults > None
```

Merging is shallow: `{ ...defaults, ...overrides }`.

### Delivery Target (`heartbeat.target`)

```
target === "last"  →  Use session's lastChannel/lastTo
target === "none" →  No delivery (heartbeat runs silently)
target === <channel-id>  →  Deliver to that channel
```

### Visibility (`channels.defaults.heartbeat` / `channels.<id>.heartbeat` / per-account)

```
perAccount > perChannel > channelDefaults > DEFAULT_VISIBILITY
```

Where `DEFAULT_VISIBILITY = { showOk: false, showAlerts: true, useIndicator: true }`.

## Appendix C: Scheduler Phase Alignment Algorithm

```typescript
// Deterministic per-agent phase offset
function resolveHeartbeatPhaseMs(params: {
  schedulerSeed: string;  // Device identity or SHA-256 of $HOME+cwd
  agentId: string;
  intervalMs: number;
}) {
  const digest = sha256(`${params.schedulerSeed}:${params.agentId}`);
  return digest.readUInt32BE(0) % params.intervalMs;
}

// Next due time (preserving alignment on config changes)
function resolveNextHeartbeatDueMs(params: {
  nowMs: number; intervalMs: number; phaseMs: number;
  prev?: { intervalMs: number; phaseMs: number; nextDueMs: number };
}) {
  // If config hasn't changed and nextDueMs is still in the future, keep it
  if (prev && prev.intervalMs === intervalMs && prev.phaseMs === phaseMs 
      && prev.nextDueMs > nowMs) {
    return prev.nextDueMs;
  }
  // Otherwise compute the next phase-aligned slot
  return computeNextHeartbeatPhaseDueMs({ nowMs, intervalMs, phaseMs });
}
```

## Appendix D: Transcription Filtering (heartbeat-filter.ts)

The `filterHeartbeatPairs` function removes heartbeat user-message/OK-response pairs from conversation context before sending to the model:

1. Scan message pairs sequentially
2. If `messages[i]` is a heartbeat user message AND `messages[i+1]` is a heartbeat OK response, skip both
3. Otherwise, include `messages[i]`

This prevents the LLM from seeing pages of `"[OpenClaw heartbeat poll]"` / `"HEARTBEAT_OK"` noise in its context window, which would waste tokens and potentially confuse the model.

---

*End of Deep Dive*
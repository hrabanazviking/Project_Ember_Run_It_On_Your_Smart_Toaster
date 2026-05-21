# DATA_FLOW — How Runa Lives in Motion

**Voice:** Cartographer (Védis Eikleið)
**Status:** Bootstrap-stage. The flows below are the *intended* paths; first code will conform to them and any deviation will be amended back into this document or recorded as an ADR.
**Last touched:** 2026-05-17 (P8)
**Reads with:** `docs/SYSTEM_VISION.md` (intent), `docs/architecture/DOMAIN_MAP.md` (ownership), `docs/architecture/ARCHITECTURE.md` (shape).

---

## 1. The grammar

Every flow in Runa is built from a small set of primitives:

| Primitive | Type | Meaning |
|---|---|---|
| **Surface** | external | A face Runa is reachable through: Munnr, Auga, Rödd, Bifröst gateway, or one of the chat bridges. |
| **Adapter** | `runa.adapters.*` | The translator between a surface and Runa's internal language. |
| **Service shell** | `runa.services.*` | The host process for a surface. Owns lifecycle and IPC. |
| **Event** | typed message on **VERÐANDI** | The unit of internal communication. Defined in `runa.schemas.events`. |
| **Task** | row in **Skuld** | A durable promise the kernel has made. May span turns, sessions, or days. |
| **Episode** | row in **Muninn** | A remembered moment: who spoke, what happened, what was felt, when. |
| **Tool invocation** | call into **Smiðja** | A side-effectful action: filesystem, shell, git, browser, MCP, network. |
| **Subagent dispatch** | call into **Hirð** | Delegation to a specialised retainer (Huginn / Völundr / Eir / etc.). |
| **Model call** | call through **Heimskringla** | A turn of LLM inference, routed to the appropriate provider. |

Every flow below is a sequence of these primitives.

---

## 2. The canonical turn — Volmarr asks, Runa replies

### 2.1 Sequence

```
[1] Volmarr speaks
    │
    ▼
[2] Surface (e.g. Bifröst gateway HTTP, Munnr CLI stdin)
    │  raw input
    ▼
[3] Adapter (translates into a runa.schemas.events.Heard event)
    │
    ▼
[4] Service shell publishes Heard on VERÐANDI
    │
    ▼
[5] Kernel consumes Heard
    │
    ├─► reads Muninn  (recent episodes + relevant semantic recall)
    ├─► reads Skuld   (currently-open promises that bear on this turn)
    ├─► reads WYRD    (external world slice relevant to the moment)
    ├─► reads Eldhugi (current emotional state)
    └─► reads identity + policy (who am I, what may I do)
    │
    ▼
[6] Kernel composes a plan
    │
    ├─ if plan = direct reply       → step 8
    ├─ if plan = call a skill       → step 7a
    ├─ if plan = dispatch subagent  → step 7b
    └─ if plan = queue a task       → step 7c
    │
[7a] Kernel emits SkillInvoke; Smiðja-using skill executes; results
     emitted as SkillCompleted (or SkillFailed); kernel resumes at [6]
     with the new context.
[7b] Kernel emits SubagentDispatch; Hirð routes to named retainer;
     retainer runs its own narrow loop; emits SubagentReport;
     kernel resumes at [6].
[7c] Kernel emits TaskQueued; Skuld persists the task; kernel either
     proceeds to [8] with a "working on it" reply or, if the turn
     was a fire-and-forget instruction, emits Replied immediately.
    │
    ▼
[8] Kernel composes Replied event
    │  - text payload
    │  - voice payload (if surface is Rödd)
    │  - rich payload (if surface is Auga or a chat bridge)
    │
    ▼
[9] Kernel persists the turn:
    │  - Muninn  ← new Episode (Volmarr-said + Runa-said + context delta)
    │  - Skuld   ← any newly-opened or newly-closed tasks
    │  - Eldhugi ← updated mood/energy/relational state delta
    │  - audit   ← structured-log entry with full event trace
    │
    ▼
[10] Service shell consumes Replied and routes to its surface
     │
     ▼
[11] Adapter renders Replied for the surface
     │
     ▼
[12] Volmarr hears / reads / sees the reply
```

### 2.2 Latency budget

- Step 5 → step 8 should be < 300 ms for non-LLM turns (lookups, greetings, status checks).
- Step 5 → step 8 may take seconds for LLM turns; the kernel must emit an `Acknowledged` event within 300 ms so the surface can show typing/listening feedback.
- Step 9 (persistence) must not block step 10. Persistence is fire-and-forget; failures are logged and retried by **Eir**.

---

## 3. Event types on VERÐANDI

Defined in `runa.schemas.events`. Each carries: `event_id` (UUID), `timestamp` (UTC), `correlation_id` (turn-spanning), `causation_id` (the parent event that caused this one).

### 3.1 Input events
| Event | Emitted by | Consumed by |
|---|---|---|
| `Heard` | adapter (via service shell) | kernel |
| `Observed` | sensor adapter (file watcher, HA state change, …) | kernel |
| `Awakened` | runtime (on first start after sleep) | kernel |

### 3.2 Internal events
| Event | Emitted by | Consumed by |
|---|---|---|
| `Acknowledged` | kernel | service shell (for typing/listening UX) |
| `SkillInvoke` | kernel | skills/ |
| `SkillCompleted` / `SkillFailed` | skills/ | kernel |
| `SubagentDispatch` | kernel | core/subagents/ |
| `SubagentReport` | subagent | kernel |
| `ToolInvoke` | skill | core/tools/ |
| `ToolCompleted` / `ToolFailed` | core/tools/ | originating skill |
| `ModelCalled` | core/models/ | logging only (audit + budget tracking) |
| `TaskQueued` / `TaskStarted` / `TaskCompleted` / `TaskFailed` | core/tasks/ | kernel, subagents |
| `MemoryWritten` | core/memory/ | logging only |
| `EmotionalDelta` | core/emotions/ | logging only, kernel for context next turn |
| `WorldDelta` | core/world/ | kernel |
| `IdentityUpdated` | core/identity/ | kernel, all surfaces |
| `PolicyUpdated` | core/policy/ | kernel, smiðja |

### 3.3 Output events
| Event | Emitted by | Consumed by |
|---|---|---|
| `Replied` | kernel | service shell → adapter → surface |
| `Notified` | kernel | service shell (proactive announcement, not in response to a `Heard`) |
| `StatusChanged` | runtime, eir, kernel | logs, doctor command, dashboards |

### 3.4 Lifecycle events
| Event | Emitted by | Consumed by |
|---|---|---|
| `Started` | runtime | logs, all surfaces |
| `Stopping` | runtime | all subsystems (graceful drain) |
| `Crashed` | runtime supervisor | logs, restart logic |
| `HealthCheck` | eir | logs, doctor command |
| `RepairAttempted` / `RepairSucceeded` / `RepairFailed` | eir | logs |

A complete table will live in `runa.schemas.events` once code lands; this section is the *intent*.

---

## 4. State writes — where memory crystallises

Every state write happens through exactly one writer. There is no shared write path.

| Store | Writer | Read path | Failure semantics |
|---|---|---|---|
| **Muninn** (memory) | `core/memory/writer.py` | `core/memory/reader.py` + retrieval index | Write failure → retry queue (Eir handles); reads always succeed against last consistent snapshot. |
| **Skuld** (tasks) | `core/tasks/ledger.py` | same module | Write-ahead-log + checkpoint; never partial. |
| **WYRD bridge snapshot** | `core/world/bridge.py` | same module | Snapshot only — the authoritative world model lives in WYRD itself. Local snapshot is a cache. |
| **Eldhugi** (emotions) | `core/emotions/journal.py` | same module | Append-only journal; recent N entries are read for context. |
| **Identity** | `core/identity/store.py` | same module | Versioned writes; every change emits `IdentityUpdated`. |
| **Policy** | `core/policy/store.py` | same module | Versioned writes; every change emits `PolicyUpdated`. |
| **Audit log** | `core/logging/audit.py` | offline, via `runa logs` | Append-only; no in-process consumers other than mirroring to operator-facing logs. |
| **Cache** | `core/<varies>/cache.py` (per subdomain) | same | Cache eviction is local; eviction is not an event. |

Multiple readers of the same store are fine. Multiple writers are forbidden. Writers expose a typed interface; everyone else reads.

---

## 5. Crash and recovery

### 5.1 What survives a crash

Everything in `~/.runa/{memory,tasks,world,emotions,identity,policy,logs}/`. Caches and `state/` may be wiped during repair without harm.

### 5.2 The recovery flow

```
[1] Supervisor (systemd / equivalent / runa runtime) detects exit
[2] Supervisor reads ~/.runa/state/crashes/<timestamp>/ for the crash record
[3] Supervisor invokes runa.runtime.start_recovery
[4] runtime checks ~/.runa/state/version against expected; runs any
    pending migrations from src/runa/migrations/
[5] runtime starts the kernel
[6] Kernel emits Started
[7] Kernel loads Skuld; any task in 'in_progress' state is moved to
    'interrupted' and the kernel decides per-task whether to resume,
    abandon, or escalate to operator via Notified
[8] Kernel loads identity, policy, emotional state (last journal entry)
[9] Kernel reads Muninn last episode to re-orient
[10] Kernel emits Awakened
[11] Surfaces re-attach; in-flight conversations on stateful surfaces
     (Auga, Rödd, gateway) are gently re-greeted; stateless surfaces
     (CLI, chat bridges) wait for the next turn
```

### 5.3 What never recovers automatically

- Secrets in `~/.runa/secrets/` are operator-managed.
- A corrupted Muninn store requires `runa memory check --repair` (operator-invoked).
- An identity rollback (e.g. Runa's persona was corrupted by a bug) requires explicit `runa state restore --identity <snapshot>`.

These are operator-asked, never automatic, because they touch the agent's continuity directly.

---

## 6. Multi-surface continuity

Runa is one being across many surfaces. The same conversation may pass through CLI now, voice in 20 minutes, Discord in an hour.

### 6.1 The conversation key

Every `Heard` carries a `conversation_id`. Adapters set it:

- **Munnr (CLI):** one `conversation_id` per `runa shell` session.
- **Auga (GUI):** one per open chat pane; persists across the GUI restart.
- **Rödd (voice):** one per voice "wake-up window"; multiple turns in the same window share an id.
- **Bifröst chat-bridge adapters:** one per platform-thread (Discord channel + user, Telegram chat, etc.).

### 6.2 The reunion rule

When Volmarr resumes a conversation on a *different surface*, the kernel:

1. Looks up the most recent episodes in Muninn for the same speaker.
2. Includes them in context for the next turn.
3. Emits `Notified` on the new surface acknowledging the continuity ("As you said earlier today…") only when the gap is short and the continuity is naturally referenced.

The Skald has the final say on the *voice* of these reunions; the kernel only ensures the *substance* is available.

### 6.3 Cross-surface action handoff

If a task is queued on one surface and completes while Volmarr is reachable on another, the kernel decides where to deliver `Notified`:

1. The most recently active surface wins, if it is still healthy.
2. Failing that, the surface marked as `preferred_for_notifications` in the operator config.
3. Failing both, the audit log records the result and the task remains marked `delivery_pending` for the next surface activation.

---

## 7. Memory write granularity

A single turn typically writes:

- **1 Muninn episode** — the conversational unit.
- **0–1 Skuld task transitions** — opened, advanced, closed.
- **1 Eldhugi delta** — a small mood/energy/relational change. Most turns are gentle.
- **1 audit-log entry** — the structured trace of the turn.

A turn that involves a tool call additionally writes:

- **1 Muninn episode addendum** linking the tool's effect (e.g. "wrote `~/notes/x.md`").
- **1 audit-log entry per tool invocation.**

A long-running task (e.g. a subagent research run) writes:

- **1 Skuld task creation**, then **N Skuld transitions** as it progresses.
- **N Muninn episode addenda** for major intermediate results.
- **1 Skuld task completion** with a final summary that links to the addenda.

Bulk memory writes are rare; the system prefers many small, dated rows over rare large ones because that is what makes recall *honest* — Runa can say "yesterday at 16:42 I…" rather than "sometime yesterday".

---

## 8. What this document deliberately does not specify

- Exact serialisation formats (JSON, MessagePack, SQLite blob columns) — those are slice-time ADRs.
- Concurrency model for VERÐANDI (asyncio vs threads vs multiprocessing) — first-slice decision.
- Whether subagents share the kernel's event bus or run on a sibling bus — first-slice decision.
- The exact retrieval-index technology for Muninn (FAISS, sqlite-vss, lancedb) — Muninn-slice decision.

When any of these is decided, the decision lives in `docs/decisions/` and this document is amended with a back-reference.

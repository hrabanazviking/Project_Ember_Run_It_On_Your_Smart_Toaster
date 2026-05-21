# Domain Map — Nervous System Boundary Specification

> **Author**: Rúnhild Svartdóttir, Architect of Mythic Engineering
> **Date**: 2026-05-10
> **Principle**: *"A strong system is not one that can do everything. It is one that knows exactly what belongs where."*

---

## 1. Domain Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ~./hermes/state/                              │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │  NERVOUS SYSTEM  │  │CONVERSATION      │  │ REACTOR      │  │
│  │  (nervous_       │  │LOGGER            │  │ (reactor.py) │  │
│  │   system.py)     │  │ (conversation_   │  │              │  │
│  │                  │  │  logger.py)      │  │ Reads: conv   │  │
│  │  OWNS:           │  │                  │  │  log +        │  │
│  │  • Event routing │  │  OWNS:           │  │  current.json│  │
│  │  • Pub/sub       │  │  • Session       │  │              │  │
│  │  • Feed persist  │  │    lifecycle     │  │  PRODUCES:   │  │
│  │  • Wire protocol │  │  • Entry journal  │  │  • Reaction  │  │
│  │  • Hub lifecycle │  │  • current.json  │  │    directives │  │
│  │                  │  │  • State         │  │  • Priorities │  │
│  │  FILES:          │  │    snapshots     │  │              │  │
│  │  • runa.sock     │  │                  │  │  FILES:      │  │
│  │  • nerve_feed.   │  │  FILES:          │  │  (none —    │  │
│  │    jsonl         │  │  • conversation_  │  │   pure read) │  │
│  │  • nervous_      │  │    log.jsonl     │  │              │  │
│  │    system.pid    │  │  • current.json  │  └──────┬───────┘  │
│  │  • nervous_      │  │  • conversations/│         │          │
│  │    system.log    │  │                  │         │          │
│  └────────┬─────────┘  └──────┬───────────┘         │          │
│           │                   │                     │          │
│           │    fires events   │  reads nerve_feed   │          │
│           │◄──────────────────│  for context         │          │
│           │                   │                     │          │
│  ┌────────┴──────────────────┴─────────────────────┘          │
│  │  CONTEXT INJECTOR (context_injector.py)                      │
│  │                                                              │
│  │  OWNS:                                                       │
│  │  • Cron prompt assembly                                     │
│  │  • CLI shim to conversation_logger (log-start,              │
│  │    log-event, log-end)                                      │
│  │                                                              │
│  │  READS:                                                      │
│  │  • current.json (via conversation_logger API)                │
│  │  • nerve_feed.jsonl (via conversation_logger context func)   │
│  │  • reactor.py::react() (for reaction directives)            │
│  │                                                              │
│  │  PRODUCES:                                                   │
│  │  • STDOUT text for cron job injection                       │
│  └──────────────────────────────────────────────────────────────│
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Domain Boundaries

### 2.1 Nervous System (`nervous_system.py`)

**Owns outright:**

| Concern | Detail |
|---------|--------|
| Unix Domain Socket server | `asyncio.start_unix_server()` lifecycle |
| Client connection handling | `handle_client()` — readline loop, dispatch |
| Event protocol stamping | `_seq`, `_ts`, `_iso` assignment |
| Pub/sub subscriber management | `self.subscribers` set, add/remove/dead-cleanup |
| Feed persistence | `self.feed_file` append + flush |
| Hub startup/shutdown | PID file, socket creation/removal, `_seq` recovery |
| Wire protocol | Newline-delimited JSON, `nerve_type` dispatch |
| Synchronous publishing | `publish_event_sync()` — UDS client + fallback |
| Hub-down fallback | Direct file append with `_fallback: true` |
| Feed reading | `get_recent_events()` — tail of JSONL file |
| Hub status | `get_status()` — PID check, ping, feed metrics |
| Hub log | `nervous_system.log` — operational log |

**Does NOT own:**
- Session lifecycle (that's conversation_logger)
- Session semantics (what `conv_start` vs `conv_event` means)
- State snapshots (that's current.json, owned by conversation_logger)
- Reaction logic (that's reactor.py)
- Cron prompt assembly (that's context_injector.py)
- Any interpretation of event *meaning* — it is a **dumb pipe**

**Files written:**
- `runa.sock` (created on start, removed on stop)
- `nerve_feed.jsonl` (append-only event log)
- `nervous_system.pid` (PID file, lifecycle-managed)
- `nervous_system.log` (operational log, append-only)

**Files read:**
- `nerve_feed.jsonl` (for `_seq` recovery on startup and `get_recent_events()`)

---

### 2.2 Conversation Logger (`conversation_logger.py`)

**Owns outright:**

| Concern | Detail |
|---------|--------|
| Session lifecycle | `start` → `event` → `update` → `end` |
| Entry types | `start`, `event`, `update`, `end` |
| Event types | `decision`, `file_changed`, `learned`, `action`, `blocker`, `blocker_resolved`, `mood_shift`, `milestone` |
| JSONL journal | `conversation_log.jsonl` — crash-safe append-only |
| Current state snapshot | `current.json` — merged state of active session |
| Field accumulation | Decisions, files_changed, things_learned, next_actions, blockers, projects_touched |
| Nerve event firing | `_nerve_fire()` — publishes `conv_{entry_type}` events to the hub |
| Context generation | `get_context_for_cron()` — assembles session + nerve + reactor context |
| Session queries | `_get_entries_for_session()`, `_get_recent_sessions()` |

**Does NOT own:**
- Event routing (that's the nervous system)
- Reaction logic (that's reactor.py — it only *calls* `react()`)
- Hub lifecycle (that's the nervous system)

**Files written:**
- `conversation_log.jsonl` (append-only session journal)
- `current.json` (overwritten on each operation)
- `conversations/` (directory — created if missing, currently unused for individual files)

**Files read:**
- `conversation_log.jsonl` (for session queries)
- `current.json` (for state merging)
- `nerve_feed.jsonl` (read by `get_context_for_cron()` for nerve awareness context)

**Nerve integration:**
- Calls `publish_event_sync()` via dynamic import of `nervous_system.py`
- Event type prefix: `conv_{entry_type}` (e.g. `conv_start`, `conv_event`)
- Source: `conv_logger:{session_id}`
- Failure mode: bare `except: pass` — nerve failure never breaks the logger

---

### 2.3 Context Injector (`context_injector.py`)

**Owns outright:**

| Concern | Detail |
|---------|--------|
| CLI shim for cron logging | `log-start`, `log-event`, `log-end` CLI commands |
| Context assembly for injection | Default no-command behavior → print full context |
| Argument parsing for cron ops | `argparse` CLI interface |

**Does NOT own:**
- Session logic — delegates to `conversation_logger.cmd_start/cmd_event/cmd_end`
- State reading — delegates to `conversation_logger.get_current_state()`
- Nerve access — delegates to `conversation_logger.get_context_for_cron()`
- Reaction generation — delegates to `reactor.react()`

**Key behavior:**
- Running `python3 context_injector.py` with no arguments prints the full context
  block (session state + nerve feed + reactions) to STDOUT, suitable for cron
  job prompt injection.
- It is a **thin adapter** — all logic resides in conversation_logger and reactor.

**Files written:** None (pure read and delegate)

**Files read:** None directly (all reads go through imported functions)

---

### 2.4 Reactor (`reactor.py`)

**Owns outright:**

| Concern | Detail |
|---------|--------|
| Reaction directive generation | `react()` — analyzes log, produces prioritized actions |
| Output formatting | `format_reactions()` — text, JSON, or brief output |
| Blocker tracking | Active vs resolved blocker logic |
| Stale session detection | Sessions started >1h ago with no `end` entry |
| Decision tracking | Decisions needing follow-up |
| Learning extraction | Things that should be stored in Mímir |
| File change tracking | Files that may need commit/push |
| Milestone acknowledgment | Celebrating achievements |
| Priority assignment | HIGH / MEDIUM / LOW / INFO |

**Does NOT own:**
- Publishing events (does not write to any file or socket)
- Session state (reads `current.json` but never writes)
- Hub interaction (no connection to nervous system)

**Files read:**
- `conversation_log.jsonl` (for full entry analysis)
- `current.json` (for active session state)

**Files written:** None (pure analysis — read-only)

---

## 3. Data Ownership Matrix

| Data Item | Written By | Read By | Format |
|-----------|-----------|---------|--------|
| `runa.sock` | nervous_system | nervous_system (publish/subscribe) | Unix socket |
| `nerve_feed.jsonl` | nervous_system (primary), conversation_logger (fallback) | nervous_system, conversation_logger (context) | JSONL |
| `nervous_system.pid` | nervous_system | nervous_system (status/stop) | Plain text PID |
| `nervous_system.log` | nervous_system | (human reads) | Timestamped lines |
| `conversation_log.jsonl` | conversation_logger | conversation_logger, reactor | JSONL |
| `current.json` | conversation_logger | conversation_logger, context_injector, reactor | JSON |
| STDOUT context block | context_injector | cron jobs (piped into prompts) | Plain text |

---

## 4. Dependency Graph

```
                    ┌─────────────────┐
                    │  Cron Job / CLI  │
                    └───────┬─────────┘
                            │ calls
                    ┌───────▼─────────┐
                    │context_injector  │
                    │(thin adapter)   │
                    └──┬──────────┬───┘
                       │          │
          imports from │          │ imports from
                       ▼          ▼
              ┌────────────┐  ┌────────────┐
              │conversation│  │  reactor    │
              │  _logger   │  │  (read-     │
              │            │  │   only)     │
              └──┬────┬────┘  └────────────┘
                 │    │
    calls (dyn) │    │ reads
                 ▼    ▼
           ┌─────────────────┐
           │ nervous_system  │
           │ (event bus)     │
           └─────────────────┘

  Data flow during a conversation event:

  1. CLI/cron → context_injector.log-event args
  2. context_injector → conversation_logger.cmd_event(args)
  3. conversation_logger → _append(entry)
     3a. writes to conversation_log.jsonl
     3b. updates current.json
     3c. _nerve_fire(entry) → nervous_system.publish_event_sync()
  4. nervous_system → stamps + persists to nerve_feed.jsonl
  5. nervous_system → broadcasts to subscribers
  6. nervous_system → ACK to conversation_logger

  Fallback (hub down):
  3c. publish_event_sync() → ConnectionRefused → direct write to nerve_feed.jsonl
                              with _fallback: true
```

---

## 5. What Belongs Where — Decision Rules

| Question | Answer | Domain |
|----------|--------|--------|
| "Should this go through the event bus?" | If it's a signal that other processes need to react to in real-time | Nervous System |
| "Should this be logged as a session entry?" | If it's part of a conversation session lifecycle (start/event/update/end) | Conversation Logger |
| "Should this generate a reaction directive?" | If it's something that needs follow-up, resolution, or acknowledgment | Reactor |
| "Should this be in a cron prompt?" | If it's contextual awareness that a new instance needs before acting | Context Injector |
| "Should this be a UDS message?" | Only if it needs real-time broadcast to subscribers AND persistence in the nerve feed | Nervous System |
| "Should this be in current.json?" | If it's the latest state of the active session (summary, blockers, next actions) | Conversation Logger |
| "Should this be a conversation_log entry?" | If it's a chronological fact that happened during a session | Conversation Logger |
| "Should this be in nerve_feed.jsonl?" | If it went through the hub (or is a fallback write) and represents a cross-instance event | Nervous System |

---

## 6. Anti-Patterns (What Does NOT Belong)

| Anti-Pattern | Why | Correct Location |
|--------------|-----|-----------------|
| Publishing raw session entries directly to nerve feed without going through conversation_logger | Bypasses session lifecycle management | Use `cmd_event()` or `cmd_start()` which handle both logging AND nerve firing |
| Reading `current.json` from nervous_system | Nervous system is a dumb pipe — it doesn't understand sessions | Read from conversation_logger or context_injector |
| Writing to `conversation_log.jsonl` from context_injector directly | Context injector is an adapter — delegate to conversation_logger | Use `cmd_start/cmd_event/cmd_end` |
| Putting reaction logic in conversation_logger | Mixing analysis with logging violates SRP | Reactor owns all analysis/reaction logic |
| Subscribing to the nerve hub from conversation_logger | The logger is a publisher, not a subscriber | Create a separate subscriber process if needed |
| Storing state in reactor | Reactor is read-only, stateless analysis | State belongs in current.json (conversation_logger) |
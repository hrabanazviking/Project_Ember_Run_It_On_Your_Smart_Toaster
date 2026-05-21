# Interface Specification — Nervous System Public API Contract

> **Author**: Rúnhild Svartdóttir, Architect of Mythic Engineering
> **Date**: 2026-05-10
> **Platform**: Python 3.11, Raspberry Pi 5, Raspbian Linux

---

## 1. CLI Interfaces

### 1.1 `nervous_system.py` — Event Bus Hub

**Invocation:** `python3 /home/pi/.hermes/state/nervous_system.py <command> [args]`

#### `serve`

Start the Nerve Hub server. Blocks until interrupted (Ctrl+C) or killed.

```
python3 nervous_system.py serve
```

**Behavior:**
- Creates `~/.hermes/state/` if missing.
- Removes stale `runa.sock` if present.
- Opens `nerve_feed.jsonl` for append.
- Recovers `_seq` from existing feed events.
- Starts `asyncio.start_unix_server` on `runa.sock`.
- Writes PID to `nervous_system.pid`.
- Logs startup to `nervous_system.log`.
- Blocks on `serve_forever()` until `asyncio.CancelledError` or `KeyboardInterrupt`.
- On shutdown: closes server, closes feed file, removes socket and PID file.

**Exit codes:** 0 on clean shutdown.

---

#### `publish`

Publish an event to the Nerve Hub.

```
python3 nervous_system.py publish <event_type> '<json_data>' [source]
```

**Positional arguments:**

| Arg | Required | Description |
|-----|----------|-------------|
| `event_type` | Yes | Event type string (e.g. `thought`, `conv_start`, `ping`) |
| `json_data` | Yes | JSON string for the `data` field. Fallback: treated as `{"text": <arg>}` if not valid JSON |
| `source` | No | Source identifier. Default: `cli` |

**Behavior:**
- Calls `publish_event_sync(event_type, data, source)`.
- If hub is running: receives ACK with `{nerve_type: "ack", seq: <int>}`.
- If hub is down: falls back to direct feed write with `_fallback: true`.
- Prints confirmation or warning.

**Exit codes:** 0 on success (including fallback), 1 on usage error.

---

#### `recent`

Show the N most recent events from the nerve feed.

```
python3 nervous_system.py recent [count]
```

**Positional arguments:**

| Arg | Required | Default | Description |
|-----|----------|---------|-------------|
| `count` | No | 20 | Number of recent events to display |

**Behavior:**
- Reads `nerve_feed.jsonl` from the beginning.
- Returns the last `count` events.
- Prints: timestamp, sequence number, event type, source, data preview.
- Fallback events are annotated with `(fallback)`.

**Exit codes:** 0 always.

---

#### `subscribe`

Connect to the Nerve Hub and print live events in real time.

```
python3 nervous_system.py subscribe
```

**Behavior:**
- Opens async UDS connection to `runa.sock`.
- Sends `{"nerve_type": "subscribe"}`.
- Prints each received event: `[timestamp] #seq type from source: data_preview`.
- Blocks until Ctrl+C or hub disconnects.

**Exit codes:** 0 on disconnect, 1 if hub not running.

---

#### `status`

Show Nerve Hub operational status.

```
python3 nervous_system.py status
```

**Behavior:**
- Checks `nervous_system.pid` for PID.
- Verifies process is running via `os.kill(pid, 0)`.
- Checks `runa.sock` existence.
- Reads `nerve_feed.jsonl` for event count and file size.
- Attempts a ping through the hub.
- Prints status summary with emoji indicators.

**Output fields:**
- `Running`: ✓/✗ (process alive)
- `PID`: numeric or N/A
- `Socket`: ✓/✗ (socket file exists)
- `Feed`: ✓/✗ (event count, file size in bytes)
- `Responsive`: ✓/✗ (ping succeeded)

**Exit codes:** 0 always.

---

#### `stop`

Stop the Nerve Hub process.

```
python3 nervous_system.py stop
```

**Behavior:**
- Reads PID from `nervous_system.pid`.
- Sends `SIGTERM` to the process.
- Waits 1 second.
- If still alive, sends `SIGKILL`.
- Cleans up stale PID file if process not found.

**Exit codes:** 0 on success.

---

### 1.2 `conversation_logger.py` — Session Tracker

**Invocation:** `python3 /home/pi/.hermes/state/conversation_logger.py <command> [options]`

#### `start`

Open a new session.

```
python3 conversation_logger.py start --session <id> [--summary <text>] [--model <name>] [--platform <name>]
```

**Arguments:**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--session` | Yes | — | Unique session ID (e.g. `2026-05-10-truth-discipline`) |
| `--summary` | No | `""` | Session summary |
| `--model` | No | `""` | AI model name |
| `--platform` | No | `""` | Platform (telegram, cli, cron) |

**Side effects:**
- Appends `{"entry_type": "start", ...}` to `conversation_log.jsonl`.
- Creates/overwrites `current.json` with initialized session state.
- Fires nerve event `conv_start` to the hub.

---

#### `event`

Log a single event during a session.

```
python3 conversation_logger.py event --session <id> --type <type> --content <text>
```

**Arguments:**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--session` | Yes | — | Session ID |
| `--type` | Yes | — | One of: `decision`, `file_changed`, `learned`, `action`, `blocker`, `blocker_resolved`, `mood_shift`, `milestone` |
| `--content` | Yes | — | What happened |

**Side effects:**
- Appends `{"entry_type": "event", "event_type": <type>, ...}` to `conversation_log.jsonl`.
- Updates `current.json` — accumulates into appropriate list field based on `event_type` mapping:
  - `decision` → `decisions`
  - `file_changed` → `files_changed`
  - `learned` → `things_learned`
  - `action` → `next_actions`
  - `blocker` → `blockers` (append)
  - `blocker_resolved` → `blockers` (remove matching entry)
  - `mood_shift` → `mood` (overwrite string)
  - `milestone` → `decisions` (append)
- Fires nerve event `conv_event` to the hub.

**Exit codes:** 0 on success, 1 on invalid `--type`.

---

#### `update`

Update session state snapshot.

```
python3 conversation_logger.py update --session <id> [--next <items>] [--blockers <items>] [--projects <items>] [--mood <text>] [--summary <text>]
```

**Arguments:**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--session` | Yes | — | Session ID |
| `--next` | No | None (no change) | Next actions (space-separated) |
| `--blockers` | No | None (no change) | Current blockers (space-separated) |
| `--projects` | No | `[]` | Projects touched (space-separated, appends) |
| `--mood` | No | `""` | Current mood |
| `--summary` | No | `""` | Updated summary |

**Side effects:**
- Appends `{"entry_type": "update", ...}` to `conversation_log.jsonl`.
- Merges specified fields into `current.json`.
- Fires nerve event `conv_update` to the hub.

---

#### `end`

Close a session.

```
python3 conversation_logger.py end --session <id> [--summary <text>] [--duration <minutes>]
```

**Arguments:**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--session` | Yes | — | Session ID |
| `--summary` | No | `""` | Final summary |
| `--duration` | No | 0 (auto-calculated from `start_time`) | Duration in minutes |

**Side effects:**
- Appends `{"entry_type": "end", ...}` to `conversation_log.jsonl`.
- Updates `current.json`: `status: "closed"`, `end_time`, `duration_minutes`.
- Auto-calculates duration from `start_time` if `--duration` is 0.
- Fires nerve event `conv_end` to the hub.

---

#### `show`

Display all entries for a session.

```
python3 conversation_logger.py show --session <id>
```

Output: chronological list of entries with emoji markers and timestamps.

---

#### `recent`

Show the N most recent session summaries.

```
python3 conversation_logger.py recent [--count <n>]
```

**Arguments:**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--count` | No | 10 | Number of sessions to show |

---

#### `context`

Generate context block for cron job injection.

```
python3 conversation_logger.py context [--sessions <n>]
```

**Arguments:**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--sessions` | No | 5 | Number of recent sessions to include |

**Output:** Multi-line text block containing:
- Active session state from `current.json`
- Recent session summaries from `conversation_log.jsonl`
- Last 10 nerve events from `nerve_feed.jsonl`
- Reaction directives from `reactor.react()`

---

### 1.3 `context_injector.py` — Cron Context & Logging Shim

**Invocation:** `python3 /home/pi/.hermes/state/context_injector.py [command] [options]`

#### (no command)

Print full context block + current state. Backward-compatible with old cron prompts.

```
python3 context_injector.py
```

**Output:** `get_context_for_cron()` output followed by current state summary.

---

#### `log-start`

Start a cron session (delegates to `conversation_logger.cmd_start`).

```
python3 context_injector.py log-start --session <id> [--summary <text>] [--model <name>] [--platform <name>]
```

**Note:** `--model` defaults to `cron`, `--platform` defaults to `cron`.

---

#### `log-event`

Log a cron event (delegates to `conversation_logger.cmd_event`).

```
python3 context_injector.py log-event --session <id> --type <type> --content <text>
```

**Note:** `--type` choices: `decision`, `file_changed`, `learned`, `action`, `blocker`, `blocker_resolved`, `milestone` (no `mood_shift` here).

---

#### `log-end`

End a cron session (delegates to `conversation_logger.cmd_end`).

```
python3 context_injector.py log-end --session <id> [--summary <text>] [--duration <minutes>]
```

---

#### `show`

Show all entries for a session (delegates to `conversation_logger._get_entries_for_session`).

```
python3 context_injector.py show --session <id>
```

---

#### `recent`

Show recent sessions (delegates to `conversation_logger._get_recent_sessions`).

```
python3 context_injector.py recent [--count <n>]
```

---

#### `context`

Generate context block (delegates to `conversation_logger.get_context_for_cron`).

```
python3 context_injector.py context [--sessions <n>]
```

---

### 1.4 `reactor.py` — Reaction Directive Engine

**Invocation:** `python3 /home/pi/.hermes/state/reactor.py [options]`

```
python3 reactor.py [--format text|json|brief] [--focus all|blockers|learnings|files|next]
```

**Arguments:**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--format` | No | `text` | Output format: `text` (full), `json` (machine-readable), `brief` (one-line) |
| `--focus` | No | `all` | Filter area: `all`, `blockers`, `learnings`, `files`, `next` |

**Note:** The `--focus` flag is accepted but not fully implemented in `react()` — it always returns all categories regardless.

---

## 2. Programmatic Interfaces (Python Functions)

### 2.1 `nervous_system.py` — Public API

#### `publish_event_sync(event_type: str, data: dict = None, source: str = None) -> dict`

**Synchronous UDS publisher.** Can be called from any Python process without
an asyncio event loop.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `event_type` | `str` | required | Event type string |
| `data` | `dict` | `{}` | Payload dictionary |
| `source` | `str` | `None` | Source identifier (omitted from event if None) |

**Returns:**

| Condition | Return value |
|-----------|-------------|
| Hub running, ACK received | `{"nerve_type": "ack", "seq": <int>}` |
| Hub running, no ACK | `{"nerve_type": "sent", "note": "no_ack"}` |
| Hub down, fallback write | `{"nerve_type": "fallback", "note": "hub_offline_written_to_feed"}` |
| Unexpected error | `{"nerve_type": "error", "error": "<exception message>"}` |

**Timeout:** 2 seconds for socket connect + recv.

**Thread safety:** Creates a new socket per call. Safe to call from any thread
or process.

---

#### `get_recent_events(count: int = 20) -> list[dict]`

**Read N most recent events from the nerve feed.** Reads the entire feed
and returns the last `count` entries.

**Returns:** List of event dicts, newest last. Empty list if feed doesn't exist.

**Complexity:** O(total_events) — reads entire JSONL file.

---

#### `get_status() -> dict`

**Get nerve hub status.** Returns:

```python
{
    "hub_running": bool,         # Process alive per PID file
    "pid": int | None,           # PID from file
    "socket_exists": bool,       # runa.sock exists on filesystem
    "feed_exists": bool,         # nerve_feed.jsonl exists
    "feed_events": int,           # Count of lines in feed
    "feed_size_bytes": int,      # File size of feed
    "hub_responsive": bool       # Ping through hub succeeded (if present)
}
```

---

#### `async subscribe() -> None`

**Async UDS subscriber.** Connects to the hub, sends `subscribe`, and
prints all received events to STDOUT. Blocks until Ctrl+C or disconnect.

**Usage:** Only from async context (CLI `subscribe` command).

---

#### `NerveHub` (class — server-side only)

**Constructor:** `NerveHub()` — initializes empty subscriber set, event counter, feed file handle.

**Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `handle_client` | `async (reader, writer)` | Per-connection handler. Reads JSON lines, dispatches control messages or publishes events. |
| `serve` | `async ()` | Starts the UDS server, recovers `_seq`, writes PID, serves forever. |

**Note:** `NerveHub` is not intended for import — it is the server process.
The public API for other modules is `publish_event_sync()`.

---

#### `log_msg(msg: str) -> None`

**Append to nerve hub log.** Thread-safe via append mode.

---

#### Module-level constants

| Constant | Value | Description |
|----------|-------|-------------|
| `STATE_DIR` | `~/.hermes/state` | State directory |
| `SOCKET_PATH` | `STATE_DIR / "runa.sock"` | UDS socket path |
| `FEED_PATH` | `STATE_DIR / "nerve_feed.jsonl"` | Event feed path |
| `PID_PATH` | `STATE_DIR / "nervous_system.pid"` | PID file path |
| `LOG_PATH` | `STATE_DIR / "nervous_system.log"` | Hub log path |

---

### 2.2 `conversation_logger.py` — Public API

#### `cmd_start(args: Namespace) -> dict`

Create a new session entry. `args` must have: `session`, `summary`, `model`, `platform`.

**Returns:** The entry dict that was appended.

---

#### `cmd_event(args: Namespace) -> dict`

Log an event. `args` must have: `session`, `type`, `content`.

**Valid types:** `decision`, `file_changed`, `learned`, `action`, `blocker`, `blocker_resolved`, `mood_shift`, `milestone`.

**Returns:** The entry dict that was appended.

---

#### `cmd_update(args: Namespace) -> dict`

Update session snapshot. `args` must have: `session`, `next`, `blockers`, `projects`, `mood`, `summary`.

**Returns:** The entry dict that was appended.

---

#### `cmd_end(args: Namespace) -> dict`

Close a session. `args` must have: `session`, `summary`, `duration`.

**Returns:** The entry dict that was appended.

---

#### `get_context_for_cron(max_sessions: int = 5) -> str`

**Assemble context string for cron injection.** Includes:
- Active session state from `current.json`
- Recent session summaries from `conversation_log.jsonl`
- Last 10 nerve events from `nerve_feed.jsonl`
- Reaction directives from `reactor.react()`

**Returns:** Multi-line string bounded by `=== RUNA SESSION CONTEXT ===` / `=== END CONTEXT ===`.

---

#### `get_current_state() -> dict | None`

Read `current.json` and return the dict, or `None` if missing/unparseable.

---

#### `get_recent_conversations(n: int = 10) -> list[dict]`

Return the N most recent session entries (one per session, preferring end entries).

---

#### Module-level constants

| Constant | Value | Description |
|----------|-------|-------------|
| `STATE_DIR` | `~/.hermes/state` | State directory |
| `CONV_DIR` | `STATE_DIR / "conversations"` | Per-session directory |
| `CURRENT_FILE` | `STATE_DIR / "current.json"` | Active session state |
| `CONV_LOG` | `STATE_DIR / "conversation_log.jsonl"` | Session journal |
| `EVENT_TYPES` | `set` of 8 strings | Valid event types for `cmd_event` |

---

### 2.3 `context_injector.py` — Public API

`context_injector.py` has **no exportable functions** — it is a CLI-only shim
that imports from `conversation_logger`. Its `main()` function parses
arguments and delegates.

**Imports from `conversation_logger`:**
- `cmd_start`, `cmd_end`, `cmd_event`
- `get_context_for_cron`, `get_current_state`
- `_get_entries_for_session`, `_get_recent_sessions`

---

### 2.4 `reactor.py` — Public API

#### `react(focus: str = "all") -> dict`

Analyze conversation log and produce reaction directives.

**Returns dict with keys:**

| Key | Type | Description |
|-----|------|-------------|
| `blockers_needing_reaction` | `list[dict]` | Unresolved blockers with reaction text |
| `decisions_needing_followup` | `list[dict]` | Decisions not yet acted on |
| `recent_learnings_to_store` | `list[dict]` | Learnings that should go to Mímir |
| `files_changed_needing_push` | `list[dict]` | Files that may need commit/push |
| `milestones_to_acknowledge` | `list[dict]` | Achievements worth celebrating |
| `next_actions_to_pick_up` | `list[dict]` | Next actions from last session |
| `stale_sessions_to_close` | `list[dict]` | Sessions started >1h ago with no end |
| `cron_events_to_review` | `list[dict]` | Recent cron-originated events |
| `reactions` | `list[dict]` | Prioritized reaction directives |

Each reaction directive in `reactions` has:
```json
{
    "priority": "HIGH|MEDIUM|LOW|INFO",
    "action": "resolve_blockers|close_stale_sessions|verify_pushed|store_learnings|continue_work|celebrate",
    "detail": "Human-readable summary",
    "items": ["...list of specific items..."]
}
```

---

#### `format_reactions(reactions: dict, fmt: str = "text") -> str`

Format reaction output.

| `fmt` | Output |
|-------|--------|
| `"text"` | Full multi-line report with emoji |
| `"json"` | Pretty-printed JSON |
| `"brief"` | One-line summary with emoji shorthand |

---

## 3. Wire Protocol Specification

### 3.1 Transport

- **Protocol:** Newline-delimited JSON over Unix Domain Socket
- **Socket path:** `~/.hermes/state/runa.sock`
- **Encoding:** UTF-8
- **Message boundary:** `\n` (0x0A)
- **Max line length:** No enforced limit (practical limit ~1MB per readline)

### 3.2 Client Lifecycle

```
Connect ──→ [subscribe|ping|publish]+ ──→ Disconnect
```

A client may:
1. Connect to `runa.sock`
2. Send zero or more messages
3. Disconnect at any time

There is **no handshake required** to publish. A client connects, sends one
JSON line, and reads one ACK line.

### 3.3 Connection Types

**Fire-and-forget publisher:**
```
Connect → send event JSON + \n → read ACK → close
```

**Subscriber:**
```
Connect → send {"nerve_type":"subscribe"} + \n → read subscribed ACK
       → continuous readline loop for broadcast events
       → Ctrl+C → close
```

**Ping:**
```
Connect → send {"nerve_type":"ping"} + \n → read pong → close
```

### 3.4 Sequence Numbers

`_seq` is a monotonically increasing integer assigned by the hub. It
persists across hub restarts (recovered from `nerve_feed.jsonl`). It is
**not** per-subscriber — all events share the same global sequence.

### 3.5 Timestamp Format

- `_ts`: Unix epoch float from `time.time()` (e.g. `1778435811.736587`)
- `_iso`: ISO 8601 UTC string with `Z` suffix (e.g. `2026-05-10T17:56:51.736587Z`)

Both are set by the hub at event processing time, not at publish time.

---

## 4. File Format Specifications

### 4.1 `nerve_feed.jsonl`

One JSON object per line. Each line is a complete, self-contained event.
Fields are defined in Section 3 of ARCHITECTURE.md.

**Mandated fields per line:** `type`, `data`, `source`, `_seq`, `_ts`, `_iso`
(except fallback events which replace `_seq` with `_fallback: true`).

**Append-only.** Never modified after write. No compaction.

### 4.2 `conversation_log.jsonl`

One JSON object per line. Each line is an entry in a session timeline.

**Entry types:**

| `entry_type` | Required fields | Description |
|--------------|----------------|-------------|
| `start` | `session_id`, `summary`, `model`, `platform`, `start_time`, `timestamp` | Session opens |
| `event` | `session_id`, `event_type`, `content`, `timestamp` | Something happened |
| `update` | `session_id`, `next_actions`, `blockers`, `projects_touched`, `mood`, `timestamp` | State checkpoint |
| `end` | `session_id`, `summary`, `duration_minutes`, `decisions`, `things_learned`, `files_changed`, `next_actions`, `blockers`, `projects_touched`, `timestamp` | Session closes |

**`event_type` values:** `decision`, `file_changed`, `learned`, `action`, `blocker`, `blocker_resolved`, `mood_shift`, `milestone`

### 4.3 `current.json`

A single JSON object representing the **latest state of the active session**.
Overwritten on every `start`, `event`, `update`, or `end` operation.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | `str` | Active session identifier |
| `start_time` | `str` | ISO timestamp of session start |
| `last_updated` | `str` | ISO timestamp of last update |
| `status` | `str` | `"active"` or `"closed"` |
| `summary` | `str` | Session summary |
| `model` | `str` | AI model name |
| `platform` | `str` | Platform (telegram, cli, cron) |
| `decisions` | `list[str]` | Accumulated decisions |
| `files_changed` | `list[str]` | Accumulated file change paths |
| `things_learned` | `list[str]` | Accumulated learnings |
| `next_actions` | `list[str]` | Planned next actions |
| `projects_touched` | `list[str]` | Projects modified in this session |
| `blockers` | `list[str]` | Current blockers |
| `mood` | `str` | Current mood |
| `duration_minutes` | `int` | Total duration (0 until session ends) |
| `end_time` | `str` | ISO timestamp of session end (if closed) |

---

## 5. Error Handling Contract

### 5.1 Nervous System

| Condition | Behavior | Exit Code / Return |
|-----------|----------|--------------------|
| Hub not running on publish | Direct feed write with `_fallback: true` | `{"nerve_type": "fallback", ...}` |
| Invalid JSON from client | Log + skip, continue serving | No error sent to client |
| Dead subscriber during broadcast | Remove from subscriber set | Logged |
| Publisher disconnect before ACK | Silently caught | Event already persisted+broadcast |
| Hub crash (SIGKILL) | Stale socket cleaned on next start | Systemd Restart=always |
| Stale PID file | Cleaned up, not treated as error | PID unlinked |

### 5.2 Conversation Logger

| Condition | Behavior |
|-----------|----------|
| Invalid event type (`--type`) | Print error, list valid types, `sys.exit(1)` |
| Invalid JSON in `current.json` | Silently catch `JSONDecodeError`, start fresh |
| Nerve hub unreachable | `_nerve_fire()` catches all exceptions, continues silently |
| Missing `conversation_log.jsonl` | Created on first `_append()` |
| Missing `current.json` | Created on `cmd_start()` |

### 5.3 Reactor

| Condition | Behavior |
|-----------|----------|
| Missing `conversation_log.jsonl` | Returns empty reaction categories |
| Invalid JSON lines in log | Silently skipped |
| Missing `current.json` | Operates without current session context |
| Missing `reactor.py` import in conversation_logger | Context injection falls back gracefully |

### 5.4 Context Injector

| Condition | Behavior |
|-----------|----------|
| Missing nerve feed | Context block omits nerve section |
| Missing reactor module | Context block omits reaction directives |
| No active session | Current state section shows defaults |
# 17 — Data Flow

This document traces **how data moves through Stofa** from operator
input to terminal output, including the round-trip through Ember's
handles and the propagation through services + messages.

---

## The canonical chat turn (data view)

```
                     OPERATOR
                        │
            "what do my notes say about Odin?"
                        │
                        ▼
              ┌─────────────────────┐
              │   ChatScreen        │
              │   on_submit         │
              └─────────┬───────────┘
                        │
            ┌───────────┼─────────────────┐
            │           │                  │
            ▼           ▼                  ▼
       FuniService  WellService     PetLayer(.bee_off)
         await         await               │
       Funi.complete  Brunnr.hybrid_search │
                                            │
                                            ▼
                                      (no animation)
                        │
                        ▼
              ┌─────────────────────┐
              │  prompt assembly     │
              │ (system + identity + │
              │  episodes + hits +   │
              │  operator input)     │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Funi streaming      │
              │ async for chunk in  │
              │   funi.stream(...): │
              └─────────┬───────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   ChatScreen     PetLayer        StatusBar
   .append_token  .funi_spark     .funi_thinking
                  ("thinking")
                                       │
                        │              │
                        ▼              ▼
              ┌─────────────────────┐
              │ chunk.done=True      │
              │ tool_calls?         │
              └────┬───────────┬────┘
                   │           │
            (no tool)      (tool_calls)
                   │           │
                   ▼           ▼
           Episode persisted   Push ToolApprovalScreen
                   │              │
                   │           operator: y/a/n
                   │              │
                   │              ▼
                   │           ExecuteToolFlow
                   │              │
                   │           ToolReply → PetLayer.heidr.drop_horn
                   │              │
                   │              ▼
                   │           AuditService.log_record
                   │              │
                   │              ▼
                   │           Funi follow-up turn (recurse)
                   │
                   ▼
           ChatScreen idle
```

The data crosses **3-5 service boundaries** for a typical turn:
- Funi (input → streaming output)
- Brunnr (retrieval)
- Audit (each tool call)
- MCP pool (when an MCP tool fires)
- Episode persistence (Brunnr)

---

## The message bus

Stofa uses Textual's message system (`Widget.post_message` /
`Widget.on_<EventName>`) for cross-widget communication.

Every cross-screen / cross-widget event is a `Message` subclass. The
top-level taxonomy:

```python
# Funi
class FuniRequestStarted(Message): ...
class FuniTokenStreamed(Message): ...
class FuniRequestFinished(Message): ...
class FuniRequestFailed(Message): ...

# Brunnr
class RetrievalStarted(Message): ...
class RetrievalReturned(Message): ...   # carries hits
class RetrievalFailed(Message): ...

# Ingest
class IngestStarted(Message): ...
class IngestProgress(Message): ...     # carries one entry at a time
class IngestFinished(Message): ...

# Tools
class ToolCallProposed(Message): ...
class ToolApprovalDecided(Message): ...
class ToolExecutionStarted(Message): ...
class ToolExecutionFinished(Message): ...

# MCP
class MCPServerConnected(Message): ...
class MCPServerDisconnected(Message): ...

# Health / status
class DoctorProbed(Message): ...

# Audit
class AuditLogAppended(Message): ...

# Stofa-internal
class ThemeChanged(Message): ...
class PetsToggled(Message): ...
class ScreenPushed(Message): ...
```

Roughly 20 message types total. Each carries minimal payload (only
what subscribers need). Each is documented in
`src/ember/stofa/messages.py` with type hints.

---

## Who emits, who listens

| Event | Emitter | Listeners |
|---|---|---|
| `FuniRequestStarted` | FuniService | ChatScreen, StatusBar, PetLayer (funi-spark) |
| `FuniTokenStreamed` | FuniService | ChatScreen |
| `FuniRequestFinished` | FuniService | ChatScreen, StatusBar, PetLayer |
| `RetrievalReturned` | WellService | ChatScreen (citations panel), PetLayer (raven) |
| `IngestProgress` | WellService | WellScreen, PetLayer (bee), StatusBar |
| `ToolCallProposed` | ChatScreen | (StatusBar, PetLayer-fox) + pushes ToolApprovalScreen |
| `ToolExecutionFinished` | ChatScreen | AuditService, ChatScreen, PetLayer (goat drops horn) |
| `MCPServerConnected` | MCPService | MCPScreen, StatusBar |
| `DoctorProbed` | DoctorService | DoctorScreen, StatusBar |
| `AuditLogAppended` | AuditService | (V2: AuditLogScreen) |
| `ThemeChanged` | StofaApp | every widget (Textual handles via CSS reload) |
| `PetsToggled` | StofaApp | PetLayer |

This table is the **observability contract**. To debug "why isn't the
status bar updating," check who emits what + who listens.

---

## Data shapes in flight

### `ChatScreen → FuniService` (submit a turn)

```python
@dataclass(frozen=True, slots=True)
class TurnRequest:
    operator_input: str
    context: tuple[ContextItem, ...]   # assembled prompt
    tools: tuple[ToolDescriptor, ...] | None  # None when tools off
```

### `FuniService → ChatScreen` (per token)

```python
@dataclass(frozen=True, slots=True)
class FuniTokenStreamed(Message):
    text: str        # the new tokens since last message
    model_id: str
    done: bool
    tool_calls: tuple[ToolCall, ...] = ()
```

### `WellService → ChatScreen` (retrieval results)

```python
@dataclass(frozen=True, slots=True)
class RetrievalReturned(Message):
    hits: tuple[RetrievalHit, ...]
    elapsed_ms: float
```

### `WellService → WellScreen` (ingest progress)

```python
@dataclass(frozen=True, slots=True)
class IngestProgress(Message):
    job_id: str
    entry_path: Path
    status: str         # "started" / "embedded" / "done" / "failed"
    chunks_done: int
    total_estimate: int | None
```

(One message *per file*. Bulk ingest = many messages; UI throttles to
~5/sec by coalescing.)

### `AuditService ← ChatScreen` (record a tool call)

```python
@dataclass(frozen=True, slots=True)
class AuditRequest:
    call: ToolCall
    descriptor: ToolDescriptor
    approval: ApprovalOutcome
    reply: ToolReply | None
```

(Synchronous from the chat loop's perspective; the AuditService
just wraps the existing `AuditLog.record` for sync usage.)

---

## Synchronous vs async data paths

Most data is async (message-based). A few paths are deliberately
synchronous:

| Path | Sync? | Why |
|---|---|---|
| Operator input → ChatScreen | sync (keyboard event handler) | Input events are inherently per-keystroke |
| ChatScreen → FuniService submit | async via `app.run_worker` | Funi calls can be long |
| FuniService stream → ChatScreen tokens | async via Messages | tokens arrive over time |
| ChatScreen → AuditService record | sync (cheap; in-process) | audit must complete before next turn |
| WellService.refresh() | async via `to_thread` | sqlite call |
| MCPService.ping(server) | async via `MCPRunner.submit` | MCP is async-native |

We never block the event loop on slow I/O. Every slow op is either
(a) in a thread, (b) in an async coroutine, or (c) a one-off probe
that fires-and-forgets.

---

## State persistence

The operator's state is persisted in several places:

| State | Persistence | Format |
|---|---|---|
| Conversation | Episodes in Brunnr | per-turn `add_episode` |
| Ingested documents | Documents + Chunks in Brunnr | per-ingest |
| Audit log | JSONL files | per-tool-call append |
| Identity | JSON in `~/.ember/identity.json` | one-shot at Hjarta completion |
| Config | YAML in `~/.ember/config/ember.yaml` | edited via Settings or hand |
| Stofa session state (scroll positions, etc.) | NOT persisted | in-memory only |

Note the last row. Stofa is "stateless across sessions" by design:
when you quit and re-open, the conversation history is loaded fresh
from Brunnr; nothing else is remembered. This is intentional — no
"last screen visited" tracking, no behavioral history. Sovereign-by-
default.

---

## What happens on services disconnect

When a service's underlying handle goes away mid-session:

| Service | Disconnect message | UI response |
|---|---|---|
| FuniService | `FuniRequestFailed(reason=...)` | ChatScreen shows error in line; StatusBar tags Funi as down; next chat turn shows Unavailable banner |
| WellService | `RetrievalFailed(reason=...)` | ChatScreen continues with ungrounded reply; StatusBar tags Brunnr as disconnected; banner shown |
| MCPService | `MCPServerDisconnected(name=...)` | MCPScreen shows red dot next to server; that server's tools surface as NO_SUCH_TOOL on next call |
| DoctorService | `DoctorProbed(status=down)` | StatusBar updates; DoctorScreen reflects |
| AuditService | (audit failure) | One-line warning to stderr-via-logging; chat continues (per Vow of Graceful Offline) |

Vow of the Unbroken Whole binds: one service going down does NOT
take Stofa with it.

---

## The 60-fps myth

We do not render at 60fps. We render on *events*:

- Operator types: every keypress.
- Funi streams: every token.
- Pet ticks: 1 Hz max.
- Status bar: throttled to 5 Hz max.
- Ingest progress: throttled to 5 Hz max (coalesces messages).

Textual's compositor only repaints **changed cells**. The data flow
above generates events; the rendering is a downstream side effect.

This is what makes Stofa SSH-friendly. A Funi stream over SSH paints
the new tokens; nothing else. A pet motion paints one cell; nothing
else.

---

## Closing

Data flows in via the operator, through the services, into the
event loop, out as messages, into widgets, painted to changed cells.
At every boundary: typed messages, bounded payloads, throttled rates.
The pets see everything but only react to a handful of events. The
status bar sees more and surfaces the most. The screen the operator
is on sees the most.

Every cross-component conversation is *in writing* (message types).
Debug = follow the messages. Robustness = test that each subscriber
handles its message + the disconnect case.

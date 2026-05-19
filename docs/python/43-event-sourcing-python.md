# 43 — Event Sourcing in Python — Implementation

**Category:** Architecture Patterns
**Runa relevance:** Muninn, Skuld, audit log, replay-based debugging
**Status:** Python craft.
**Last touched:** 2026-05-17

---

## 1. Core idea

[[22-event-sourcing-cqrs]] in the research corpus covers the *concept* of event sourcing — what it is, why it matters, who pioneered it. This doc covers the *Python implementation* — file formats, libraries, append-only-file patterns, projections, recovery code. The translation from concept to runnable code in Runa.

The core implementation pattern: append events to a durable log, build queryable projections by folding over the log, recover by replaying. The mechanics are simple; the discipline (atomic appends, immutable events, idempotent projections, schema evolution) is what makes it work over years.

## 2. Technique / mechanism

**Append-only JSONL log:**

```python
import json
from pathlib import Path
import time
from dataclasses import dataclass, asdict
from datetime import datetime
import os

@dataclass(frozen=True)
class Event:
    event_id: str
    event_type: str
    timestamp: str
    correlation_id: str | None
    causation_id: str | None
    data: dict
    
    def to_jsonl(self) -> bytes:
        return (json.dumps(asdict(self)) + "\n").encode("utf-8")

class EventLog:
    """Append-only JSONL log with daily rotation."""
    
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
    
    def _today_path(self) -> Path:
        return self.root / f"{datetime.utcnow().date().isoformat()}.jsonl"
    
    def append(self, event: Event) -> None:
        path = self._today_path()
        with open(path, "ab") as f:
            f.write(event.to_jsonl())
            f.flush()
            os.fsync(f.fileno())
    
    def iter_events(self, since: datetime | None = None) -> Iterator[Event]:
        for path in sorted(self.root.glob("*.jsonl")):
            with open(path) as f:
                for line in f:
                    event = Event(**json.loads(line))
                    yield event
```

**Atomicity of appends:**

- `O_APPEND` mode (`"ab"`) makes write+seek atomic on POSIX for writes smaller than `PIPE_BUF` (usually 4096 bytes).
- `fsync()` ensures the data reaches disk (slow but durable).
- A crash mid-write may leave a partial line; reader skips with try/except.

**Hash-chained log for tamper-evidence:**

```python
import hashlib

@dataclass(frozen=True)
class HashedEvent(Event):
    prev_hash: str
    self_hash: str
    
    @classmethod
    def from_data(cls, data: dict, prev_hash: str) -> "HashedEvent":
        # Compute hash of (prev_hash + data)
        content = (prev_hash + json.dumps(data, sort_keys=True)).encode()
        self_hash = hashlib.sha256(content).hexdigest()
        return cls(prev_hash=prev_hash, self_hash=self_hash, ...)
```

Each event references the prior hash. Modifying any event breaks the chain.

**Projections — folding events into queryable state:**

```python
@dataclass
class TaskProjection:
    """Current state of all tasks, derived from event log."""
    tasks: dict[UUID, TaskState]
    
    def apply(self, event: Event):
        """Apply a single event to current state."""
        if event.event_type == "TaskCreated":
            self.tasks[event.data["task_id"]] = TaskState(...)
        elif event.event_type == "TaskStarted":
            self.tasks[event.data["task_id"]].status = "running"
        elif event.event_type == "TaskCompleted":
            self.tasks[event.data["task_id"]].status = "completed"
        # ... etc
    
    @classmethod
    def from_log(cls, log: EventLog) -> "TaskProjection":
        """Build projection by replaying log."""
        proj = cls(tasks={})
        for event in log.iter_events():
            proj.apply(event)
        return proj
```

**Snapshots for fast recovery:**

```python
class SnapshotStore:
    def save(self, projection: TaskProjection, at_event_count: int) -> None:
        snap_path = self.root / f"snapshot-{at_event_count}.pickle"
        with open(snap_path, "wb") as f:
            pickle.dump((projection, at_event_count), f)
    
    def load_latest(self) -> tuple[TaskProjection, int] | None:
        snaps = sorted(self.root.glob("snapshot-*.pickle"))
        if not snaps:
            return None
        with open(snaps[-1], "rb") as f:
            return pickle.load(f)

# Combined recovery
def recover(log: EventLog, snapshots: SnapshotStore) -> TaskProjection:
    latest = snapshots.load_latest()
    if latest:
        proj, last_event_count = latest
    else:
        proj = TaskProjection(tasks={})
        last_event_count = 0
    
    for i, event in enumerate(log.iter_events()):
        if i < last_event_count:
            continue
        proj.apply(event)
    return proj
```

**SQLite as event store:**

```python
schema = """
CREATE TABLE IF NOT EXISTS events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT UNIQUE NOT NULL,
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    correlation_id TEXT,
    causation_id TEXT,
    data TEXT NOT NULL,
    prev_hash TEXT,
    self_hash TEXT
);
"""

class SqliteEventStore:
    def __init__(self, path: Path):
        self.conn = sqlite3.connect(path)
        self.conn.executescript(schema)
        self.conn.execute("PRAGMA journal_mode=WAL")
    
    def append(self, event: Event):
        with self.conn:  # transaction
            self.conn.execute(
                "INSERT INTO events (event_id, event_type, timestamp, ...) VALUES (?, ?, ?, ...)",
                (event.event_id, event.event_type, event.timestamp, ...)
            )
```

SQLite gives ACID guarantees; WAL mode survives crashes; readers can query without blocking writer.

**Event versioning:**

```python
class Event:
    event_type: str   # "TaskCreated"
    version: int       # 1, 2, 3 — schema versions

# Upcaster: transforms old version to new
def upcast_task_created(data: dict, from_version: int) -> dict:
    if from_version == 1:
        # v1 didn't have "priority" field; default it
        return {**data, "priority": "normal"}
    return data
```

When reading old events, apply upcasters to bring them to current schema.

**Libraries:**

- **`eventsourcing`** — github.com/pyeventsourcing/eventsourcing. Full event-sourcing framework.
- **Hand-rolled** (often sufficient for Runa-scale).
- **Apache Kafka** (heavy, distributed) — not for single-Pi.
- **EventStoreDB** — purpose-built; overkill for Runa.

## 3. Key works / libraries

- **Young, G.** "CQRS Documents." Foundational.
- **Fowler, M.** "Event Sourcing." martinfowler.com.
- **Vernon, V.** *Implementing Domain-Driven Design*, 2013.
- **`eventsourcing`** — github.com/pyeventsourcing/eventsourcing.
- **Helland, P.** "Immutability Changes Everything." ACM Queue, 2015.
- **SQLite WAL** — sqlite.org/wal.html.

## 4. Pitfalls and gotchas

- **Event mutation.** Don't. Use compensating events.
- **Schema evolution.** Versioning + upcasters. Required from day one.
- **Projection drift.** Code change to projection → must rebuild from log. Slow if log is large; snapshots help.
- **Replay correctness.** Idempotent projections; non-idempotent ones double-count on replay.
- **Storage growth.** Logs grow forever. Compaction strategy (collapse to snapshots, archive cold events).
- **Concurrent writers.** Single writer keeps things simple; multi-writer needs coordination.
- **JSON serialisation of complex types.** Use Pydantic or custom serialisers; document carefully.
- **fsync overhead.** Per-event fsync is slow. Batch-fsync where durability tolerates.

## 5. Applicability to Runa

For **Muninn**:

- Episodes stored as events (`EpisodeRecorded`, `EpisodeSummarised`, `EpisodeArchived`).
- Projections: current episode table, vector index, importance ranking.

For **Skuld**:

- Task lifecycle as events (`TaskQueued`, `TaskStarted`, `TaskCompleted`, etc.).
- Projection: current task state map.

For **audit log**:

- Daily JSONL files under `~/.runa/logs/audit/YYYY-MM-DD.jsonl`.
- Hash-chained per ADR-style design.

For **`runa state replay`**:

- CLI command that replays an event log forward to reproduce state for debugging.

For **schema migrations**:

- `runa.migrations.events` holds upcasters. Run during replay.

What to avoid:

- Don't mutate events.
- Don't make projections non-idempotent.
- Don't fsync every event without measuring throughput.
- Don't conflate event log with message bus (different purposes).

## 6. Open questions

- **Event compaction.** When to collapse old events into snapshots? Storage cost vs auditability.
- **Cross-aggregate events.** Multi-aggregate atomicity is hard; sagas help ([[17-saga-pattern]]).
- **Distributed event log.** Single-writer simple; multi-writer needs coordination (Raft, etc.).

## 7. References (curated)

- martinfowler.com/eaaDev/EventSourcing.html.
- github.com/pyeventsourcing/eventsourcing.
- sqlite.org/wal.html.
- ACM Queue — Helland 2015.
- Companion docs: [[11-crash-only-software]], [[22-event-sourcing-cqrs]] (research corpus), [[40-audit-logging-replay]] (research corpus).

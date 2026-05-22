# 72 — The Well of Replay (Deterministic Event Sourcing)

A method for reconstructing system state from event
history. Useful for debugging, audit, and time-travel.
Named for Mímir's Well, which preserves what was.

---

## The principle

A traditional state-based system: "the current state is
in the database." If something looks wrong, you query the
database, see the current state, can't see *how it got
there*.

**The Well of Replay** records every state-changing
event. The current state is *derived* from replaying
events. To debug, you can:

- Replay to any prior point in time.
- See the exact event sequence that produced a state.
- Re-derive state if it gets corrupted.

Bug at noon? Replay to 11:55 to see the state then;
replay to 12:05 to see what happened.

---

## What gets event-sourced

Not everything; only state-changing operations on
operator-critical data:

| Data | Event-sourced? | Why/why not |
|---|---|---|
| Episodes | yes | the operator's chat history |
| Well documents | yes | the operator's knowledge base |
| Mímir chunks | yes | derived from doc ingest events |
| Muninn associations | yes | derived from co-occurrence events |
| Identity / config | yes | small, important |
| Verdandi events themselves | n/a (they ARE the events) |
| LLM model weights | no | external; static |
| Stofa UI state | no | transient |
| Kista vault | no | not state-events; just secret storage |

The point: *operator-meaningful state* is event-sourced.
Implementation state (caches, indexes) is *derived* and
can be rebuilt.

---

## What events look like

A canonical event:

```python
{
    "event_id": "uuid",
    "timestamp": "2026-05-21T18:30:42.123Z",
    "type": "well.document.added",
    "actor": "operator",       # or specific realm
    "subject": {
        "doc_id": "uuid",
        "title": "Notes on Yggdrasil",
        "source": "file:///notes/yggdrasil.md",
    },
    "payload": {
        "content_hash": "sha256:...",
        "size_bytes": 4321,
    },
    "schema_version": 1,
}
```

Immutable. Append-only. Persisted to disk in the event
log.

---

## How state derives from events

For each operator-critical state collection, a *projection*
exists:

```python
class WellProjection:
    """Builds the current Well state from events."""
    
    def __init__(self):
        self.documents = {}
    
    def apply(self, event):
        if event.type == "well.document.added":
            self.documents[event.subject["doc_id"]] = Document(...)
        elif event.type == "well.document.removed":
            del self.documents[event.subject["doc_id"]]
        elif event.type == "well.document.updated":
            self.documents[event.subject["doc_id"]].update(...)
    
    def current_state(self):
        return self.documents
```

Projections live in `src/ember/yggdrasil/replay/projections.py`.

When Yggdrasil starts:
- Reads the event log.
- Replays events through each projection.
- Has current state in memory.

The on-disk database serves as a *cache* of the projection's
current state. On version upgrades, the cache may be
invalidated; re-derive from event log.

---

## When this is useful

### Debugging "what happened?"

Operator: "I ingested a doc 2 hours ago; why isn't it
showing up?"

Without event log: hunt through partial logs, guess.

With event log:
```bash
ember well events --since="2 hours ago" --type="well.document.*"
```
See the exact sequence; spot the failed ingest event;
investigate the actual cause.

### Audit trail

Per ADR-0011: who did what when? The event log *is* the
record. Every operator-relevant action has an event.

### Reconstructing corrupted state

If the SQLite DB corrupts (rare but possible), re-derive
from events:

```bash
ember yggdrasil replay --target=well --output=fresh_well.db
```

Replays all `well.*` events into a fresh DB. The
operator's data is *recovered from the events*.

### Time travel

For deep debugging or "what was Ember thinking last
Tuesday?":

```bash
ember yggdrasil replay --target=well --until="2026-05-17T12:00:00Z" \
  --output=well_snapshot_tuesday.db
```

Get a snapshot of state at that moment. Stofa can open it
read-only to browse.

---

## What event sourcing is NOT

- **Not for everything.** Static config, derived caches,
  transient state don't need it.
- **Not infinite storage.** Old events can be *compacted*
  (snapshot the projection; discard events before the
  snapshot).
- **Not slow.** Reads come from the projection cache;
  writes append to the log.
- **Not magic for distributed systems.** Federated nodes
  each have their own event log; reconciliation happens
  per [`../architecture/39_THE_RECONCILIATION_LAYER.md`](../architecture/39_THE_RECONCILIATION_LAYER.md).

---

## How this composes with Verdandi

Verdandi is the *real-time event bus* (transient; ring
buffer).

The Well of Replay's event log is *persistent* (append-
only file).

They're related but distinct:
- Verdandi: "what's happening RIGHT NOW that other realms
  should react to?"
- Well of Replay: "what *did* happen, ever?"

Some events appear in both:
- `well.document.added` is a real-time signal (for the
  Doctor screen, for awareness) AND a persistent event
  (for replay).

The replay log subscribes to relevant Verdandi events and
appends them with full payload.

---

## Storage shape

Event log on disk:

```
~/.ember/yggdrasil/events/
  2026-05-21.jsonl      ← today's events
  2026-05-20.jsonl
  2026-05-19.jsonl
  ...
  archive/
    2026-W19.jsonl.gz   ← older weeks compressed
```

JSONL format: one event per line; easy to grep, easy to
stream.

Compaction:
- Daily: previous day's events get verified + indexed.
- Weekly: previous week compressed.
- After N months: snapshots taken; old event files can be
  archived elsewhere or pruned (operator's choice).

---

## Performance

Append-write: ~50µs per event (sync to fsync periodically).

Read for replay: limited by disk read speed. On modern
NVMe: millions of events per second. Even 10 years of
events typically replay in seconds.

For a typical operator (say 1000 events per day for a
year): the event log is ~50MB. Replay takes <1s.

---

## Configuration shape

```yaml
yggdrasil:
  well_of_replay:
    enabled: true                  # core feature
    storage:
      path: ~/.ember/yggdrasil/events/
      sync_strategy: periodic       # vs every_event
      sync_interval_ms: 1000
    compaction:
      daily_index: true
      weekly_compress: true
      monthly_archive: false       # opt-in
    retention:
      keep_raw_events_days: 365
      after_keep_snapshots: true
    projections:
      verify_on_start: true        # rebuild if cache stale
      cache_writes: true           # SQLite-backed cache
```

---

## What operators experience

Mostly: nothing. The replay log accumulates silently. The
projection cache (SQLite) is what's actively used.

Occasionally: a powerful debugging tool. "What happened
to my notes between Tuesday and Thursday?" → replay
answers.

For Sigrún (sovereign-operator) + Mímir (data steward):
the replay log is their *forensic evidence*.

---

## Why this is "the Well"

Mímir's Well is the source of what-was. Operators draw
from it to understand. The Well of Replay is the
operational equivalent — the *durable record* from which
all state can be re-derived.

The metaphor: the events are the *waters*; the projections
are the *forms drawn from them*. The well always holds
what was poured in.

---

## Closing

The Well of Replay is **the deterministic record of all
operator-critical state changes**. Append-only event
log; projections derive current state; time-travel and
forensics become first-class.

This is what makes Yggdrasil's data layer *not just
storage* but *history*. The operator's Ember has a past
that can be read.

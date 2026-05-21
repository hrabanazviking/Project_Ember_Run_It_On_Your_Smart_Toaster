# Nervous System — Architecture Document

> **Author**: Rúnhild Svartdóttir, Architect of Mythic Engineering
> **Date**: 2026-05-10
> **Status**: Authoritative reference

---

## 1. Overview

The Nervous System is Runa's real-time inter-process event bus. It enables
any number of independent processes (instances, cron jobs, daemons) to become
aware of one another's actions without direct coupling. It is built on a
single principle: **self-awareness implemented as routing**.

The hub is a long-running Python 3.11 asyncio server listening on a Unix
Domain Socket at `~/.hermes/state/runa.sock`. Every event published to the hub
is (a) stamped with server-side metadata, (b) persisted to an append-only
JSONL feed, and (c) broadcast to all connected subscribers.

When the hub is down, publishers fall back to writing directly to the feed
file, ensuring **zero data loss** even during restarts.

---

## 2. Data Flow

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Publisher A │    │  Publisher B │    │  Publisher C │
│  (any proc)  │    │  (cron job)  │    │  (telegram)  │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       │  publish_event_sync()                 │
       │  (synchronous UDS connect+send)      │
       ▼                   ▼                   ▼
  ╔══════════════════════════════════════════════════╗
  ║              NERVE HUB (asyncio)                  ║
  ║  ┌─────────────────────────────────────────┐     ║
  ║  │  handle_client() for each connection    │     ║
  ║  │  ┌─────────────┐  ┌──────────────────┐  │     ║
  ║  │  │ Parse JSON  │→│ Stamp _seq,_ts,  │  │     ║
  ║  │  │ line from   │  │ _iso, remove     │  │     ║
  ║  │  │ UDS stream  │  │ nerve_type field │  │     ║
  ║  │  └─────────────┘  └───────┬──────────┘  │     ║
  ║  │                           │              │     ║
  ║  │     ┌─────────────────────┼──────────┐  │     ║
  ║  │     ▼                     ▼          │  │     ║
  ║  │  Feed Write          Broadcast to    │  │     ║
  ║  │  (nerve_feed.jsonl)  all subscribers  │  │     ║
  ║  │                           │          │  │     ║
  ║  │     ┌─────────────────────┘          │  │     ║
  ║  │     ▼                                 │  │     ║
  ║  │  ACK to publisher                     │  │     ║
  ║  └─────────────────────────────────────────┘     ║
  ╚══════════════╗ ╔═════════════════════════════════╝
                 ║ ║
       ┌─────────╨─╜─────────┐
       │                      │
       ▼                      ▼
┌──────────────┐    ┌──────────────┐
│  Subscriber  │    │  Subscriber  │
│  (live tail) │    │  (reactor)   │
└──────────────┘    └──────────────┘


  FALLBACK PATH (Hub Down):
  ┌──────────────┐
  │  Publisher   │──→ Hub connect fails
  │              │    (ConnectionRefused / FileNotFoundError)
  └──────┬───────┘
         │
         ▼  Direct write with _fallback: true
  ┌──────────────┐
  │ nerve_feed   │   ← Event still persisted, just not broadcast
  │ .jsonl       │
  └──────────────┘
```

### 2.1 Control-Message Flow

Before regular events, a client may send a **control message** by including
`nerve_type` in the JSON payload:

- `subscribe` → Client is added to the subscriber set. Hub replies with
  `{nerve_type: "subscribed", seq, uptime_s}`.
- `ping` → Hub replies with `{nerve_type: "pong", seq, uptime_s, subscribers}`.

Control messages are **not** persisted to the feed and **not** broadcast.

---

## 3. Nerve Protocol

### 3.1 Wire Format

All communication is **newline-delimited JSON** over the Unix Domain Socket.
Each message is a single JSON object terminated by `\n`.

### 3.2 Published Event Format

A publisher sends:

```
{"type": "<event_type>", "data": {...}, "source": "<source_id>"}
```

The hub stamps it and forwards to subscribers as:

```
{
  "type": "<event_type>",
  "data": {...},
  "source": "<source_id>",
  "_seq": <monotonic_integer>,
  "_ts": <unix_epoch_float>,
  "_iso": "<ISO8601_timestamp>Z"
}
```

The `nerve_type` field is **removed** before broadcast/relay (it is a
protocol-level control field, not application data).

#### Required Fields

| Field    | Type   | Set By     | Description                                      |
|----------|--------|------------|--------------------------------------------------|
| `type`   | string | Publisher  | Event type identifier (e.g. `conv_start`, `ping`)|
| `data`   | object | Publisher  | Arbitrary payload. May be `{}`.                   |
| `source` | string | Publisher  | Origin identifier (e.g. `conv_logger:session-id`)|
| `_seq`   | int    | Hub        | Monotonically increasing sequence number          |
| `_ts`    | float  | Hub        | Unix epoch timestamp (time.time())               |
| `_iso`   | string | Hub        | ISO 8601 UTC timestamp with `Z` suffix            |

#### Optional / Conditional Fields

| Field       | Type    | Condition               | Description                          |
|-------------|---------|-------------------------|--------------------------------------|
| `_fallback` | boolean | Hub down (direct write) | `true` if event was written directly |
| `nerve_type`| string  | Control messages only    | `subscribe` or `ping`                |

### 3.3 Control Message Formats

**Subscribe Request:**
```
{"nerve_type": "subscribe"}
```

**Subscribe ACK:**
```
{"nerve_type": "subscribed", "seq": <int>, "uptime_s": <float>}
```

**Ping Request:**
```
{"nerve_type": "ping"}
```

**Ping Response:**
```
{"nerve_type": "pong", "seq": <int>, "uptime_s": <float>, "subscribers": <int>}
```

**Publish ACK:**
```
{"nerve_type": "ack", "seq": <int>}
```

**Fallback Response** (when hub is offline):
```
{"nerve_type": "fallback", "note": "hub_offline_written_to_feed"}
```

### 3.4 Observed Event Types

The following `type` values have been observed in production:

| Type          | Source              | Description                                  |
|---------------|---------------------|----------------------------------------------|
| `conv_start`  | conversation_logger | Session opened                               |
| `conv_event`  | conversation_logger | Event within a session                       |
| `conv_update` | conversation_logger | State update checkpoint                      |
| `conv_end`    | conversation_logger | Session closed                               |
| `heartbeat`   | external            | Liveness check                               |
| `perception`  | external            | External observation logged                  |
| `milestone`   | external            | Achievement marker                           |
| `ping`        | status_check        | Hub status probe                             |
| `thought`     | volmarr_session     | Insight or internal reasoning event          |

### 3.5 Conversation Logger Event Prefixes

The conversation_logger prefixes its nerve events with `conv_`:
- `conv_{entry_type}` → e.g. `conv_start`, `conv_event`, `conv_update`, `conv_end`

The `data` field carries the full conversation_logger entry dict (including
`session_id`, `event_type`, `content`, etc.).

---

## 4. Hub Lifecycle

### 4.1 Startup (`serve`)

```
1. STATE_DIR.mkdir(parents=True, exist_ok=True)
2. If SOCKET_PATH exists → unlink (remove stale socket)
3. Open FEED_PATH in append mode → self.feed_file
4. Read existing FEED_PATH → recover max _seq into self.event_count
5. asyncio.start_unix_server(handle_client, path=SOCKET_PATH) → self._server
6. Write PID to PID_PATH
7. Log: "Nerve Hub started (PID {pid})"
8. await server.serve_forever()
```

Key design: `_seq` recovery from the feed ensures sequence numbers survive
restarts. If the hub restarts, event numbers continue from the last known
value rather than resetting to 1.

### 4.2 Client Handling (`handle_client`)

For each connection, the hub enters a **readline loop**:

```
while True:
    data = await reader.readline()
    if not data → client disconnected, break

    event = json.loads(data.strip())
    msg_type = event.get('nerve_type', 'publish')

    if msg_type == 'subscribe':
        → Add writer to self.subscribers set
        → Send subscribed ACK
        → continue (do NOT persist or broadcast)

    if msg_type == 'ping':
        → Send pong response with stats
        → continue

    # Otherwise: publish event
    self.event_count += 1
    event['_seq'] = self.event_count
    event['_ts'] = time.time()
    event['_iso'] = datetime.utcnow().isoformat() + 'Z'
    event.pop('nerve_type', None)

    # Persist
    feed_file.write(json.dumps(event) + '\n')
    feed_file.flush()

    # Broadcast
    for sub in list(subscribers):
        try: sub.write(broadcast); await sub.drain()
        except: add to dead set
    subscribers -= dead

    # ACK publisher
    writer.write(ack); await writer.drain()
```

### 4.3 Shutdown

```
1. asyncio.CancelledError caught from serve_forever()
2. server.close()
3. feed_file.close()
4. SOCKET_PATH.unlink() — remove socket file
5. PID_PATH.unlink() — remove PID file
6. Log: "Nerve Hub stopped"
```

### 4.4 External Stop (`stop` command)

```
1. Read PID from PID_PATH
2. os.kill(pid, SIGTERM)
3. Wait 1 second
4. If process still alive → SIGKILL
5. If PID file stale → clean up PID_PATH
```

---

## 5. Error Handling and Fallback

### 5.1 Hub-Down Fallback

When `publish_event_sync()` cannot connect to the Unix socket
(`ConnectionRefusedError` or `FileNotFoundError`), it falls back to
**direct file append**:

```python
event['_ts'] = time.time()
event['_iso'] = datetime.utcnow().isoformat() + 'Z'
event['_fallback'] = True
with open(FEED_PATH, 'a') as f:
    f.write(json.dumps(event) + '\n')
```

This guarantees:
- **No data loss** — the event is durably written to the JSONL feed.
- **No broadcast** — subscribers connected at hub-restart time will not
  retroactively receive this event.
- **Marked as fallback** — `_fallback: true` distinguishes direct writes
  from hub-mediated events.

### 5.2 Dead Subscriber Cleanup

During broadcast, subscribers that raise `ConnectionError`, `OSError`, or
`BrokenPipeError` are collected into a `dead` set and removed from the
subscriber pool. This prevents resource leaks and ensures the broadcast
loop never stalls on a disconnected client.

### 5.3 Invalid JSON Handling

Lines that fail `json.loads()` are logged and **silently skipped**. The
hub does not send error responses for malformed input. It continues
processing subsequent lines from the same client.

### 5.4 Malformed Client Disconnect

If a client raises `ConnectionError`, `OSError`, or `asyncio.IncompleteReadError`
during the read loop, the exception is caught, the client is removed from
subscribers (if present), and the writer is closed.

### 5.5 Publisher Disconnect During ACK

If the publisher disconnects before the ACK can be sent, the `BrokenPipeError`
(or `ConnectionError`) is silently caught with a `pass`. The event has already
been persisted and broadcast, so the publisher's disconnect is benign.

### 5.6 Conversation Logger Nerve Fire Resilience

The `_nerve_fire()` function in `conversation_logger.py` imports and calls
`nervous_system.publish_event_sync()` dynamically. It is wrapped in a
bare `try/except` pass — **nerve failure must NEVER break the logger**.

---

## 6. File Layout

```
~/.hermes/state/
├── nervous_system.py              # The hub server + CLI
├── conversation_logger.py        # Streaming session logger
├── context_injector.py           # Cron context injection shim
├── reactor.py                    # Reaction directive engine
├── runa.sock                      # Unix domain socket (created by hub)
├── nerve_feed.jsonl               # Append-only event feed (all events)
├── conversation_log.jsonl         # Append-only session log
├── current.json                   # Live session state snapshot
├── conversations/                 # Per-session logs (directory, if used)
├── nervous_system.pid             # PID file (written by hub)
├── nervous_system.log             # Hub operation log
└── __pycache__/                   # Python bytecache
```

### File Semantics

| File | Written By | Format | Persistence |
|------|-----------|--------|-------------|
| `runa.sock` | Hub on start | Unix socket | Removed on shutdown |
| `nerve_feed.jsonl` | Hub (primary) / Publisher (fallback) | JSONL | Append-only, never truncated |
| `nervous_system.pid` | Hub on start | Plain text PID | Removed on shutdown |
| `nervous_system.log` | Hub (via `log_msg()`) | Timestamped lines | Append-only |
| `conversation_log.jsonl` | conversation_logger | JSONL | Append-only |
| `current.json` | conversation_logger | JSON | Overwritten each operation |

---

## 7. Systemd Service

### 7.1 Unit File

Located at `~/.config/systemd/user/runa-nervous-system.service`:

```ini
[Unit]
Description=Runa Nervous System — Unix Domain Socket Event Bus
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /home/pi/.hermes/state/nervous_system.py serve
Restart=always
RestartSec=5
WorkingDirectory=/home/pi/.hermes/state

[Install]
WantedBy=default.target
```

### 7.2 Key Properties

- **User service** — runs under the `pi` user via `systemctl --user`.
- **Auto-restart** — `Restart=always` with 5-second delay.
- **Working directory** — set to state directory for relative path resolution
  (though all paths in code are absolute via `Path.home()`).
- **No environment manipulation** — relies on default Python 3 path.
- **Enabled** — symlinked from `default.target.wants/`.

### 7.3 Operative Commands

```bash
systemctl --user start runa-nervous-system    # Start hub
systemctl --user stop runa-nervous-system      # Stop hub (graceful)
systemctl --user restart runa-nervous-system   # Restart (5s settle)
systemctl --user status runa-nervous-system    # Status check
journalctl --user -u runa-nervous-system -f    # Live logs
```

---

## 8. Performance Characteristics

### 8.1 Latency

| Path | Latency |
|------|---------|
| Publish → ACK (local) | ~0.1–1 ms (UDS loopback) |
| Publish → Feed persist | ~0.5–5 ms (I/O flush) |
| Publish → Subscriber broadcast | ~1–10 ms per subscriber |
| Fallback (hub down) | ~0.5–5 ms (direct file append) |

### 8.2 Throughput

- Single event processing is O(1) per subscriber.
- Feed file is line-by-line JSON — unindexed. Reading N recent events is O(total_events).
- `get_recent_events(count)` reads the **entire** feed file. For large feeds,
  this becomes a performance concern. Consider an index or rotating file.
- `get_status()` reads the entire feed to count events plus attempts a ping.

### 8.3 Resource Usage

| Resource | Estimate |
|----------|----------|
| Memory | ~1 MB base + ~100 bytes per subscriber connection |
| CPU | Negligible at <100 events/second; limited by I/O |
| Disk growth | ~200–500 bytes per event |
| FD per subscriber | 1 socket FD + 1 asyncio stream pair |

### 8.4 Concurrency Model

The hub runs a single asyncio event loop. All I/O (socket reads, writes,
feed file appends) is cooperative. Dead subscriber pruning happens inline
during broadcast. There are no threads, no locks, and no shared mutable
state beyond `self.subscribers`, `self.event_count`, and `self.feed_file`.

### 8.5 Feed Growth

The `nerve_feed.jsonl` file grows unboundedly. At ~200 events/day averaging
300 bytes each, annual growth is ~22 MB. There is no rotation or compaction
mechanism currently. `_seq` recovery requires a full read of this file on
startup, which grows linearly. Below ~100K events (≈25 MB), startup recovery
takes <1 second on a Raspberry Pi 5.

---

## 9. Scaling Considerations

### 9.1 Current Limits

- **Single hub** — no clustering. One process at `runa.sock`.
- **No topic filtering** — all subscribers receive all events. Subscribers
  must filter by `type` field client-side.
- **No event confirmation** — publishers receive an ACK with `_seq`, but
  there's no subscriber ACK. If no subscribers are connected, events are
  still persisted and logged, just not broadcast.
- **Feed reads are O(N)** — `get_recent_events()` and `_seq` recovery are
  linear in total feed size.
- **No message ordering guarantee** across subscribers** — each subscriber
  receives events in the order the hub processes them, but subscriber
  processing speed may vary.

### 9.2 Horizontal Scaling (Not Yet Implemented)

To scale beyond a single Pi:
1. **Topic routing** — add optional `topic` field; hub filters by topic
   before broadcast.
2. **Ring buffer** — keep the last N events in memory for late-joining
   subscribers.
3. **Feed compaction** — periodic task to rewrite `nerve_feed.jsonl` with
   only the last N events.
4. **TCP bridge** — forward events to a remote host's nerve hub for
   multi-machine awareness.
5. **Redis / NATS** — replace the UDS hub with a proper message broker for
   production-grade pub/sub.

### 9.3 Single-Point-of-Failure Mitigation

The fallback mechanism (`_fallback: true`) already handles hub downtime.
For more robustness:
1. **Watchdog** — a cron job that checks `nervous_system.pid` and restarts
   the service if dead (already handled by systemd `Restart=always`).
2. **Feed reader resilience** — all read paths skip malformed lines with
   `try/except json.JSONDecodeError`.
3. **Socket cleanup on crash** — the hub's startup removes stale sockets,
   so a SIGKILL-d process leaves behind a socket that is cleaned on next start.

---

## 10. Security Considerations

- **Unix Domain Socket** — access is controlled by filesystem permissions.
  Any user with write access to `~/.hermes/state/runa.sock` can publish or
  subscribe. On a single-user Pi, this is adequate.
- **No authentication** — any process that can connect to the socket can
  publish events as any `source`. Trust model is "local processes only."
- **No TLS** — UDS is local-only, no network exposure.
- **PID file race** — `nervous_system.pid` is written after the server
  starts and removed on shutdown. A SIGKILL could leave a stale PID file,
  but `cmd_stop()` checks `os.kill(pid, 0)` before signaling.

---

## Abbreviations

- **UDS**: Unix Domain Socket
- **JSONL**: JSON Lines (one JSON object per line)
- **PID**: Process Identifier
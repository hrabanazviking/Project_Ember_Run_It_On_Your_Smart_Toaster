# 📡 Nerve Hub Protocol Specification

## Overview

The Verðandi Nerve Hub uses Unix domain sockets for real-time inter-process communication. This document specifies the protocol for clients that want to subscribe to nerve impulses.

## Socket Details

- **Type**: Unix domain socket (`AF_UNIX`, `SOCK_STREAM`)
- **Default path**: `~/.hermes/state/runa.sock`
- **Encoding**: UTF-8
- **Message format**: JSON objects, one per line (JSONL/NDJSON)
- **Line delimiter**: `\n` (newline character)

## Connection Protocol

```
Client                              Server
  │                                    │
  │──── connect() ────────────────────►│
  │                                    │
  │◄─── welcome ──────────────────────│  (optional)
  │                                    │
  │◄─── impulse ──────────────────────│  (continuous)
  │◄─── impulse ──────────────────────│
  │◄─── impulse ──────────────────────│
  │     ...                           │
  │                                    │
  │──── close() ──────────────────────►│
```

## Impulse Types

### heartbeat_pulse

Fired on every pulse cycle (default: every 60 seconds).

```json
{
  "event_type": "heartbeat_pulse",
  "pulse_count": 42,
  "state": "running",
  "health_score": 87.5,
  "health_trend": "stable",
  "checks": {
    "eir": {
      "severity": "ok",
      "message": "CPU 23%, RAM 45%, Disk 32%, Temp 48°C"
    },
    "huginn": {
      "severity": "ok",
      "message": "3 projects checked, 0 dirty"
    },
    "mimir": {
      "severity": "ok",
      "message": "Mímir DB OK (1234 rows, 2.1MB)"
    },
    "urdr": {
      "severity": "ok",
      "message": "2 events in next 48h"
    }
  }
}
```

### heartbeat_state_change

Fired when the daemon state changes.

```json
{
  "event_type": "heartbeat_state_change",
  "old_state": "running",
  "new_state": "degraded",
  "pulse_count": 42
}
```

## Severity Levels

| Level | Value | Meaning |
|-------|-------|---------|
| OK | `"ok"` | All parameters within thresholds |
| WARNING | `"warning"` | Approaching a threshold |
| CRITICAL | `"critical"` | Threshold exceeded |
| UNKNOWN | `"unknown"` | Could not determine |

## State Machine

| State | Transition Trigger |
|-------|-------------------|
| INITIALIZING | First pulse → RUNNING |
| RUNNING | All checks OK |
| DEGRADED | Any WARNING level check |
| CRITICAL | Any CRITICAL level check |
| RECOVERING | Was DEGRADED/CRITICAL, now improving |
| SHUTTING_DOWN | Graceful shutdown in progress |

## Circuit Breaker Integration

When a circuit breaker is OPEN, the corresponding check will return:

```json
{
  "eir": {
    "severity": "unknown",
    "message": "Circuit breaker open — {'name': 'check_eir', 'state': 'open', ...}"
  }
}
```

## Fallback Protocol

If the nerve hub socket is unavailable, impulses are written to:
```
~/.hermes/state/nerve_feed.jsonl
```

Format is identical to socket messages, with an additional `timestamp` and `source` field:

```json
{
  "timestamp": "2026-05-11T00:30:00+00:00",
  "source": "verdandi-heartbeat",
  "event_type": "heartbeat_pulse",
  "pulse_count": 42,
  "state": "running",
  "health_score": 87.5,
  "checks": { ... }
}
```

## Client Implementation (Python)

```python
import socket
import json
from pathlib import Path

class VerdandiClient:
    def __init__(self, socket_path=None):
        self.socket_path = Path(socket_path or 
            Path.home() / ".hermes/state/runa.sock")
        self.sock = None
    
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(2)
        self.sock.connect(str(self.socket_path))
    
    def listen(self, callback):
        """Listen for nerve impulses. Calls callback for each event."""
        buffer = ""
        while True:
            data = self.sock.recv(4096)
            if not data:
                break
            buffer += data.decode()
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if line.strip():
                    event = json.loads(line)
                    callback(event)
    
    def close(self):
        if self.sock:
            self.sock.close()

# Usage
client = VerdandiClient()
client.connect()
client.listen(lambda event: print(f"Event: {event['event_type']}"))
```

## Error Handling

| Error | Cause | Action |
|-------|-------|--------|
| Connection refused | Socket doesn't exist | Fall back to JSONL file |
| Connection reset | Server disconnected | Reconnect with backoff |
| Timeout | Server busy | Retry with longer timeout |
| Invalid JSON | Corrupted message | Skip line, log warning |
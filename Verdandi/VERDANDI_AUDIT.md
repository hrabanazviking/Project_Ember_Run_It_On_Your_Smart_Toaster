# VERÐANDI AUDIT — Forge Worker Hardening Report

> **Forge Worker**: Eldra Járnsdóttir  
> **Date**: 2026-05-10  
> **Status**: Complete — all bugs fixed, all self-healing features implemented

---

## Bugs Fixed

### BUG-1: `_nerve_fire` re-imports module on every call
**File**: `conversation_logger.py`  
**Severity**: Performance + risk  
**Problem**: Every logged event triggered a full dynamic import of `nervous_system.py` via `importlib.util`. This is expensive and could cause module re-initialization issues.  
**Fix**: Cached the imported module in a global `_nerve_module` variable. The import only happens once (or when the file path changes). Added `_nerve_module_path` to detect path changes.

### BUG-2: Operator precedence in `cmd_event` condition
**File**: `conversation_logger.py` line 234 (originally 217)  
**Severity**: Logic bug  
**Problem**: `args.type == "mood_shift" or args.type == "milestone" and args.type == "mood_shift"` — due to Python's operator precedence, `and` binds tighter than `or`, making this equivalent to `args.type == "mood_shift" or (args.type == "milestone" and args.type == "mood_shift")`. The second clause is always False (milestone ≠ mood_shift), so the whole condition reduces to just `args.type == "mood_shift"`. But the intent was likely different and the expression is clearly buggy regardless.  
**Fix**: Simplified to `args.type == "mood_shift"` — milestones map to `decisions` via the `field_map`, not to `mood`.

### BUG-3: No `await writer.wait_closed()` in disconnect handler
**File**: `nervous_system.py`  
**Severity**: Resource leak  
**Problem**: `writer.close()` was called without `await writer.wait_closed()`, potentially leaving sockets in a half-closed state.  
**Fix**: Added `await writer.wait_closed()` in the finally block of `handle_client`, and also in the `subscribe()` function.

### BUG-4: Subscriber writes don't handle all exceptions
**File**: `nervous_system.py`  
**Severity**: Potential crash  
**Problem**: The broadcast loop caught `(ConnectionError, OSError, BrokenPipeError)` but not `RuntimeError` which can occur on closed transports.  
**Fix**: Changed to bare `except Exception` in the dead-subscriber collection pattern to be resilient.

---

## Self-Healing Features Implemented

### 1. Feed File Rotation
- When `nerve_feed.jsonl` grows past 10 MB, the hub automatically archives it
- Archive is compressed to `.gz` (gzip) to save disk space on the Pi
- Fresh empty feed is created after rotation
- Uses file locking (`fcntl.flock`) to prevent concurrent rotation races
- Rotation happens at hub startup before opening the feed file

### 2. File Locking for Concurrent Writes
- Added `fcntl.flock` in `log_msg()` for log file writes
- Added `_feed_lock_write()` function for feed fallback writes (when hub is down)
- Feed writes in hub use `os.fsync()` for durability
- Hub's open feed file handle uses flush + fsync

### 3. Socket Permission Hardening
- After creating `runa.sock`, the hub calls `os.chmod(path, 0o600)` to restrict to owner-only
- Verified: socket now shows `srw-------` permissions instead of world-readable

### 4. PID File Race Condition Fix
- Before starting, the hub checks if a PID file exists and if that PID is still running
- If the old PID is dead, the stale PID file is cleaned up and the hub proceeds
- If the old PID is alive, the hub refuses to start (prevents double-hub)
- PID file written atomically: write to `.tmp` file, then `rename()` to final path

### 5. Subscriber Cleanup on Disconnect
- `handle_client` finally block properly removes writers from subscribers set and subscriber_times dict
- `writer.close()` + `await writer.wait_closed()` ensures clean socket teardown

### 6. Ring Buffer for In-Memory Recent Events
- `RingBuffer` class (deque-based, max 256 events) stores recent events in memory
- Pre-loaded from feed file on hub startup
- Can be queried via `nerve_type: 'recent'` protocol command
- Clients can request recent events without reading the whole file

### 7. Stale Subscriber Detection
- `subscriber_times` dict tracks last-active time for each subscriber
- `_prune_stale_subscribers()` coroutine runs every 30 seconds
- Subscribers with no activity for 120 seconds are disconnected and removed
- Read timeout on `reader.readline()` (120s) to detect silent clients
- Clean disconnection triggers removal from the set

### 8. Graceful Shutdown with Drain
- `serve()` now uses `asyncio.Event` for shutdown signaling instead of `serve_forever()`
- On shutdown, sends a `shutdown` message to all subscribers before closing connections
- Subscribers receive `{nerve_type: 'shutdown', message: 'Hub shutting down'}`
- Each subscriber writer gets `drain()` + `close()` called before server closes
- `stop` command waits up to 5 seconds for graceful exit before escalating to SIGKILL

### 9. Health-Check Command
- New `healthcheck` CLI command: `python3 nervous_system.py healthcheck`
- Verifies:
  - State directory exists
  - Socket file exists and is responsive (ping/pong)
  - PID file exists and points to a running process
  - Feed file exists and is readable
  - Log file is writable
  - Feed size warning if approaching rotation threshold
- Auto-creates missing feed file
- Returns exit code 0 (healthy) or 1 (issues found)

### 10. Feed Write Recovery
- If `feed_file.write()` raises `OSError`, the hub attempts to close and reopen the feed file
- Prevents total event loss if the disk has a transient error

---

## Protocol Additions

### `recent` Command (new)
```json
{"nerve_type": "recent", "count": 20}
```
Response:
```json
{"nerve_type": "recent_events", "events": [...]}
```

### `shutdown` Notification (new)
When the hub shuts down, all subscribers receive:
```json
{"nerve_type": "shutdown", "message": "Hub shutting down"}
```

---

## Testing Results

All tests passed:
1. ✅ Syntax check: `python3 -c 'import importlib.util...'` — no errors
2. ✅ Hub starts, creates socket with 0600 permissions
3. ✅ Publish event: Event #22 acknowledged
4. ✅ Recent events: Shows all events correctly
5. ✅ Status: Hub running, PID valid, socket responsive, feed healthy
6. ✅ Healthcheck: ALL CHECKS PASSED
7. ✅ Graceful shutdown: SIGTERM → clean exit in <1 second
8. ✅ Feed rotation: 12MB feed archived and compressed, fresh feed created
9. ✅ Post-rotation: New events publish correctly, sequence resets from #1

---

## Files Modified

- `/home/pi/.hermes/state/nervous_system.py` — Complete rewrite with all hardening features
- `/home/pi/.hermes/state/conversation_logger.py` — Fixed `_nerve_fire` caching bug and operator precedence bug
- `/home/pi/.hermes/state/VERDANDI_AUDIT.md` — This file (audit documentation)
# VERÐANDI RE-AUDIT — Forge Worker Findings

> **Forge Worker**: Eldra Járnsdóttir  
> **Date**: 2026-05-10  
> **Status**: All bugs fixed, comprehensive test suite added  

---

## Bugs Found

### REBUG-1: Missing `recent` handler in `NerveHub.handle_client`
**File**: `nervous_system.py`  
**Severity**: HIGH — functional bug  
**Problem**: The server has no handler for `msg_type == 'recent'` in `handle_client()`. When a client sends `{"nerve_type": "recent", "count": N}`, the message falls through to the publish code path, which:
  - Increments `event_count` (wrong — it's a query, not an event)
  - Stamps the request with `_seq`, `_ts`, `_iso` (wrong)
  - Removes the `nerve_type` key (wrong — strips protocol field)
  - Persists it to `nerve_feed.jsonl` (wrong — a query request shouldn't be saved)
  - Adds it to the ring buffer (wrong)
  - Broadcasts it to all subscribers (wrong — subscribers get spurious events)
  - Returns an `ack` instead of `recent_events` (wrong response format)  
**Fix**: Added `recent` handler between the `ping` handler and the publish code path, matching the pattern used for other message types.

### REBUG-2: `datetime.utcnow()` deprecated and non-timezone-aware
**File**: `nervous_system.py` lines 232, 469  
**Severity**: MEDIUM — correctness + forward compatibility  
**Problem**: `datetime.utcnow()` is deprecated in Python 3.12+ and returns a naive (non-timezone-aware) datetime. The rest of the codebase (`conversation_logger.py`) uses `datetime.now(timezone.utc)` properly. This creates inconsistent timestamps — some have timezone info, some don't.  
**Fix**: Changed both occurrences to `datetime.now(timezone.utc)` and added `timezone` to the import.

### REBUG-3: Variable `s` may be undefined in `finally` block of `publish_event_sync`
**File**: `nervous_system.py` lines 453-479  
**Severity**: LOW — defensive programming  
**Problem**: If `sock_mod.socket()` raises an exception, `s` is never assigned, but the `finally` block tries `s.close()`. While the inner `try/except Exception` catches the `NameError`, this is unclean and confusing.  
**Fix**: Initialize `s = None` before the try block and added `if s is not None` guard in the finally clause.

### REBUG-4: Feed file read twice during startup
**File**: `nervous_system.py` lines 347-374  
**Severity**: LOW — performance  
**Problem**: In `serve()`, the feed file is opened and read twice: once to get the max `_seq` for `event_count`, and once to load recent events into the ring buffer. On a large feed file, this doubles I/O.  
**Fix**: Consolidated into a single pass that both tracks max seq and appends to a list for the ring buffer.

---

## Test Suite Added

### tests/test_nervous_system.py
- Ring buffer (append, recent, maxlen)
- Hub lifecycle (start, publish, subscribe, recent query, status, healthcheck, graceful shutdown)
- Feed rotation
- File locking
- Edge cases (empty feed, stale PID, concurrent hubs)
- Integration tests using subprocess and temp sockets (isolated from production)

### tests/test_conversation_logger.py
- Session lifecycle (start, event, update, end)
- State snapshots (current.json accumulation)
- Nerve firing (fallback when hub down)
- Edge cases (empty log, corrupt lines, missing fields)

### tests/test_context_injector.py
- Context generation with nerve feed
- Context generation without nerve feed
- Current state display
- Cron session logging

### tests/test_reactor.py
- Reaction directive generation (blockers, decisions, learnings, files, milestones)
- Stale session detection
- Brief, JSON, and text output formats
- Edge cases (empty log, no current state)
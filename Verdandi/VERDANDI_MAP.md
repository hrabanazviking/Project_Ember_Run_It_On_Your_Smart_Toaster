# VERDANDI — Complete File Map & Data Flow Diagram

> **Cartographer**: Védis Eikleið, Mythic Engineering
> **Date**: 2026-05-10 (Updated post-hardening)
> **Scope**: Every file in `~/.hermes/state/`, every data flow, every dependency, every configuration point
> **Hardening Pass**: Forge Worker — feed rotation, ring buffer, file locking, subscriber pruning, healthcheck, graceful shutdown

---

## 1. Complete File Inventory

### 1.1 Source Code Files

| File | Size | Lines | Purpose | Language |
|------|------|-------|---------|----------|
| `nervous_system.py` | 29,600 B | 840 | The Nerve Hub — asyncio UDS event bus server, publisher client, CLI, self-healing | Python 3.11 |
| `conversation_logger.py` | 22,664 B | 619 | Streaming session lifecycle logger with nerve integration (cached dynamic import) | Python 3.11 |
| `context_injector.py` | 5,516 B | 142 | Thin CLI shim — cron context assembly + cron logging adapter | Python 3.11 |
| `reactor.py` | 14,642 B | 345 | Read-only reaction directive engine — analyzes log, generates priorities | Python 3.11 |

### 1.2 Documentation Files

| File | Size | Lines | Purpose |
|------|------|-------|---------|
| `ARCHITECTURE.md` | 19,772 B | 519 | Authoritative technical reference — data flow, protocol, lifecycle, error handling, performance |
| `DOMAIN_MAP.md` | 15,204 B | 280 | Domain boundary specification — what each module owns, reads, writes, and does NOT own |
| `INTERFACE.md` | 23,426 B | 796 | Public API contract — CLI interfaces, programmatic APIs, wire protocol, file formats, error handling |
| `PHILOSOPHY.md` | 16,584 B | 128 | Philosophical foundation — consciousness as routing, the Three Norns, Bifröst metaphor |
| `SYSTEM_VISION.md` | 19,880 B | 218 | Vision document — what the system IS, BECOMES, and could EVOLVE into |
| `VERDANDI_NAME.md` | 3,300 B | 39 | Naming essay — why "Verðandi," the Norn of Becoming |

### 1.3 Data Files

| File | Size | Lines | Format | Written By | Read By | Persistence |
|------|------|-------|--------|------------|---------|-------------|
| `nerve_feed.jsonl` | ~8 KB+ | ~21+ | JSONL (1 event/line) | nervous_system (primary via hub), nervous_system (fallback), conversation_logger (fallback) | nervous_system (seq recovery + ring buffer + recent), conversation_logger (context) | Append-only, rotated at 10 MB |
| `nerve_feed_*.jsonl.gz` | varies | N/A | Gzip-compressed JSONL archive | nervous_system (`_rotate_feed_if_needed`) | (Archive — not currently read by any module) | Compressed archive, kept indefinitely |
| `conversation_log.jsonl` | ~13 KB | ~30 | JSONL (1 entry/line) | conversation_logger | conversation_logger (queries), reactor (analysis) | Append-only |
| `current.json` | ~1 KB | ~20 | JSON (single object) | conversation_logger (overwrite) | conversation_logger, context_injector, reactor | Overwritten each operation |
| `nervous_system.log` | ~4 KB | ~66 | Timestamped text lines | nervous_system (`log_msg` with fcntl locking) | Human (journalctl) | Append-only |
| `nervous_system.pid` | 6 B | 1 | Plain text PID | nervous_system (atomic write via tmp+rename on start) | nervous_system (status/stop/healthcheck), systemd | Removed on shutdown |
| `nerve_feed.rotate.lock` | 0 B | 0 | Transient lock file | nervous_system (`_rotate_feed_if_needed`) | nervous_system (rotation) | Created during rotation, removed after |

### 1.4 Runtime/Special Files

| File | Type | Created By | Purpose | Lifecycle |
|------|------|-----------|---------|-----------|
| `runa.sock` | Unix domain socket (mode 0600) | NerveHub on `serve()` | IPC transport for all event publish/subscribe | Created on start with `chmod 0o600`, removed on shutdown |
| `conversations/` | Directory | conversation_logger (`_append()`) | Per-session log directory (currently unused for individual files) | Created if missing |
| `__pycache__/` | Directory | Python runtime | Bytecache (.pyc files) | Gitignored |

### 1.5 Configuration Files

| File | Location | Purpose |
|------|----------|---------|
| `runa-nervous-system.service` | `~/.config/systemd/user/runa-nervous-system.service` | systemd user unit file for the Nerve Hub daemon |
| `.gitignore` | `~/.hermes/state/.gitignore` | Excludes `__pycache__/`, `*.pyc`, `*.pid`, `nervous_system.log` |

### 1.6 Total Inventory Summary

- **4** Python source files (72,422 bytes total)
- **6** Markdown documentation files (98,166 bytes total)
- **7** data/runtime files (~26 KB + archives)
- **1** runtime socket (`runa.sock`, mode 0600)
- **1** systemd unit file
- **1** gitignore
- **1** empty directory scaffold (`conversations/`)
- **Grand total: ~172 KB** across all tracked files (excluding archives)

---

## 2. Data Flow Maps

### 2.1 Primary Event Flow — From Source to Persistence (Post-Hardening)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EVENT SOURCES                                       │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐        │
│  │ Telegram Session │  │   Cron Job       │  │  CLI / Manual Call   │        │
│  │ (conversation_   │  │ (context_        │  │  python3 nervous_   │        │
│  │  logger.py)      │  │  injector.py)   │  │  system.py publish) │        │
│  └────────┬─────────┘  └────────┬─────────┘  └──────────┬──────────┘        │
│           │                     │                        │                    │
│           │  Various triggers:  │                        │                    │
│           │  start, event,      │  log-start,            │  publish            │
│           │  update, end        │  log-event,             │  <type> '<json>'   │
│           │                      │  log-end                │                     │
└───────────┼─────────────────────┼────────────────────────┼───────────────────┘
            │                     │                        │
            ▼                     ▼                        ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                        PROCESSING LAYER                                       │
│                                                                               │
│  conversation_logger.py                  nervous_system.py                    │
│  ┌─────────────────────────┐            ┌──────────────────────────┐          │
│  │ 1. Build entry dict     │            │ 8. publish_event_sync()  │          │
│  │ 2. _append(entry) ──────┼──┐        │    - Connect to UDS      │          │
│  │    ├─ write conv_log    │  │        │    - Send JSON + \n      │          │
│  │    └─ update current.json│  │        │    - Read ACK            │          │
│  │ 3. _nerve_fire(entry) ─┼──┼────────►│    - Return result       │          │
│  │    (CACHED dynamic      │  │        │                          │          │
│  │     import, auto-refresh│  │        │ OR (if hub down):        │          │
│  │     on file change)     │  │        │    - _feed_lock_write() │          │
│  └─────────────────────────┘  │        │      direct to feed     │          │
│                               │        │      with fcntl lock    │          │
│  context_injector.py         │        │      + _fallback:true   │          │
│  ┌─────────────────────────┐  │        └────────────┬─────────────┘          │
│  │ 4. get_context_for_cron │  │                     │                        │
│  │    - read current.json  │  │                     │                        │
│  │    - read conv_log.jsonl│  │                     ▼                        │
│  │    - read nerve_feed    │  │        ┌──────────────────────────┐          │
│  │    - call reactor.react │  │        │  NERVE HUB (asyncio)    │          │
│  │ 5. Print to STDOUT      │  │        │  ┌────────────────────┐ │          │
│  └─────────────────────────┘  │        │  │ 9. handle_client() │ │          │
│                               │        │  │   - Parse JSON     │ │          │
│  reactor.py                   │        │  │   - Stamp _seq     │ │          │
│  ┌─────────────────────────┐  │        │  │   - Stamp _ts/_iso │ │          │
│  │ 6. react() — READ ONLY  │  │        │  │   - Remove nerve_  │ │          │
│  │    - read conv_log      │  │        │  │     type field     │ │          │
│  │    - read current.json  │  │        │  ├────────────────────┤ │          │
│  │    - produce directives │  │        │  │10. Persist to      │ │          │
│  └─────────────────────────┘  │        │  │    nerve_feed.jsonl│ │          │
│                               │        │  │    (via feed_file) │ │          │
│                               │        │  ├────────────────────┤ │          │
│                               │        │  │11. Append to ring │ │          │
│                               │        │  │    buffer (256)   │ │          │
│                               │        │  ├────────────────────┤ │          │
│                               │        │  │12. Broadcast to    │ │          │
│                               │        │  │    subscribers     │ │          │
│                               │        │  │    (prune dead)   │ │          │
│                               │        │  ├────────────────────┤ │          │
│                               │        │  │13. ACK to          │ │          │
│                               │        │  │    publisher        │ │          │
│                               │        └────────────────────┘ │          │
│                               │        ┌──────────────────────────┐          │
│                               │        │ SELF-HEALING (NEW):     │          │
│                               │        │ ┌──────────────────────┐│          │
│                               │        │ │14. _rotate_feed_if_  ││          │
│                               │        │ │    needed() (10MB)   ││          │
│                               │        │ │15. _prune_stale_     ││          │
│                               │        │ │    subscribers()     ││          │
│                               │        │ │    (every 30s,       ││          │
│                               │        │ │     timeout 120s)    ││          │
│                               │        │ │16. Feed write recovery││          │
│                               │        │ │    (reopen on error) ││          │
│                               │        │ └──────────────────────┘│          │
│                               │        └──────────────────────────┘          │
└───────────────────────────────┼─────────────────────────────────────────────┘
                                │
                 ┌──────────────┼──────────────┐
                 ▼              ▼              ▼
          ┌───────────┐  ┌──────────┐  ┌───────────────┐
          │ nerve_feed│  │Subscriber│  │  Subscriber   │
          │ .jsonl    │  │ (live    │  │  (reactor     │
          │ (Urðr's   │  │  tail)   │  │   process)    │
          │  well)    │  └──────────┘  └───────────────┘
          │ +archives │
          │ .jsonl.gz │
          └───────────┘
```

### 2.2 Conversation Event Flow (step-by-step, post-hardening)

```
1. TRIGGER: CLI or code calls conversation_logger CLI or context_injector CLI

2. conversation_logger.cmd_start/cmd_event/cmd_update/cmd_end()
   │
   ├─► Build entry dict with entry_type, session_id, timestamp, etc.
   │
   ├─► _append(entry)
   │    ├─► Write JSON line to conversation_log.jsonl  [PERSIST]
   │    └─► _nerve_fire(entry)
   │         ├─► Check cached _nerve_module (refresh if file on disk changed)
   │         ├─► Call ns.publish_event_sync(
   │         │       event_type=f"conv_{entry_type}",
   │         │       data=entry,
   │         │       source=f"conv_logger:{session_id}")
   │         │    ├─► [HUB UP]  UDS connect → send JSON → hub processes → ACK
   │         │    └─► [HUB DOWN] _feed_lock_write() direct to nerve_feed.jsonl
   │         │                   with fcntl LOCK_EX + _fallback:true + fsync
   │         └─► except: pass  (nerve failure NEVER breaks the logger)
   │
   ├─► _update_current(entry, session_id)
   │    ├─► Read existing current.json (merge with same session)
   │    ├─► Build new current dict (preserve accumulations)
   │    └─► Write current.json  [OVERWRITE]
   │
   └─► Return entry dict

3. HUB PROCESSING (if hub received the event):
   NerveHub.handle_client()
   ├─► Read with timeout (SUBSCRIBER_TIMEOUT_S=120s, disconnect if timeout)
   ├─► Increment event_count → _seq
   ├─► Add _ts (time.time()), _iso (datetime utcnow)
   ├─► Remove nerve_type field
   ├─► Write JSON line to nerve_feed.jsonl via self.feed_file + flush()
   │    └─► On write OSError: attempt recovery (close+reopen+rewrite)
   ├─► Append to self.ring_buffer (RingBuffer, max 256 events)
   ├─► Broadcast to all subscribers (remove dead ones on error)
   ├─► _rotate_feed_if_needed() on hub startup (archive+gzip if > 10 MB)
   │    └─► Uses separate lock file for rotation atomicity
   └─► Send ACK to publisher

4. HUB SELF-HEALING (background tasks):
   _prune_stale_subscribers()
   ├─► Runs every SUBSCRIBER_PROBE_INTERVAL (30s)
   ├─► Checks subscriber_times for entries older than SUBSCRIBER_TIMEOUT_S (120s)
   └─► Closes and removes stale subscriber connections

5. HUB GRACEFUL SHUTDOWN:
   ├─► Send {"nerve_type": "shutdown", "message": "Hub shutting down"} to all subscribers
   ├─► Drain all subscriber connections
   ├─► Close server socket
   └─► Clean up PID file + socket file
```

### 2.3 Context Injection Flow (cron → prompt)

```
Cron job triggers → python3 context_injector.py
    │
    ▼
context_injector.main()
    │ (no subcommand → default)
    ▼
    ├─► get_context_for_cron(max_sessions=5)
    │    ├─► _get_recent_sessions(5)
    │    │    └─► _read_all_entries() from conversation_log.jsonl
    │    ├─► Read current.json for active session state
    │    ├─► Read nerve_feed.jsonl for last 10 nerve events
    │    └─► Call reactor.react()
    │         ├─► _read_all_entries() from conversation_log.jsonl
    │         ├─► _get_current_state() from current.json
    │         └─► Analyze: blockers, decisions, learnings, files, stale sessions
    │              └─► Return reactions dict
    │
    ├─► Assemble context string with sections:
    │    - "=== RUNA SESSION CONTEXT (auto-injected) ==="
    │    - Active session summary
    │    - Recent sessions list
    │    - "=== NERVE FEED ===" (last 10 events)
    │    - "=== REACTION DIRECTIVES (ACT ON THESE) ==="
    │    - "=== END CONTEXT ==="
    │
    └─► Print to STDOUT → injected into cron job's AI prompt
```

### 2.4 Control Message Flow (subscribe / ping / recent / healthcheck)

```
Client connects to runa.sock
    │
    ├─► {"nerve_type": "subscribe"}
    │    └─► Hub adds writer to self.subscribers + self.subscriber_times[writer] = time.time()
    │         └─► Send {"nerve_type":"subscribed", "seq":N, "uptime_s":T}
    │              └─► Client enters readline loop, receiving all future broadcasts
    │
    ├─► {"nerve_type": "ping"}
    │    └─► Hub updates subscriber_times[writer] = time.time()
    │    └─► Hub replies {"nerve_type":"pong", "seq":N, "uptime_s":T, "subscribers":C}
    │         └─► Connection may close (status check) or continue
    │
    ├─► {"nerve_type": "recent", "count":N}
    │    └─► Hub responds with {"nerve_type":"recent_events", "events":[...]}
    │         └─► Uses ring_buffer for fast retrieval (if hub running)
    └─► {"type":"...","data":{...},"source":"..."}
         └─► PUBLISH EVENT (see §2.2 step 3)

Healthcheck (CLI: python3 nervous_system.py healthcheck):
    ├─► Check STATE_DIR exists
    ├─► Check SOCKET_PATH exists + responsive (send ping, expect pong)
    ├─► Check PID_PATH exists + process alive (stale detection)
    ├─► Check FEED_PATH exists + parseable + size < 80% rotation threshold
    ├─► Check LOG_PATH writable
    └─► Report: ✅ ALL CHECKS PASSED or ❌ list of issues
         └─► Exit code 0 (healthy) or 1 (issues found)
```

### 2.5 Fallback Flow (hub down, post-hardening)

```
Publisher calls publish_event_sync()
    │
    ├─► Try: socket.connect(runa.sock)
    │    ├─► SUCCESS → send event → receive ACK → close
    │    └─► FAIL (ConnectionRefused / FileNotFoundError)
    │         │
    │         ▼
    │    _feed_lock_write(json.dumps(event)):
    │    ├─► FEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    │    ├─► open(FEED_PATH, 'a') as f
    │    ├─► fcntl.flock(f.fileno(), fcntl.LOCK_EX)   ← FILE LOCK ACQUIRED
    │    ├─► f.write(event_line + '\n')
    │    ├─► f.flush()
    │    ├─► os.fsync(f.fileno())                       ← DURABLE WRITE
    │    ├─► fcntl.flock(f.fileno(), fcntl.LOCK_UN)   ← FILE LOCK RELEASED
    │    │
    │    │  Event written with:
    │    │    _fallback: true
    │    │    _ts: <unix_epoch>
    │    │    _iso: "<ISO_timestamp>Z"
    │    │    NO _seq (hub is down)
    │    │
    │    └─► Return: {"nerve_type": "fallback", "note": "hub_offline_written_to_feed"}
    │
    └─► Other exceptions: return {"nerve_type": "error", "error": str(e)}
```

### 2.6 Feed Rotation Flow (NEW — self-healing)

```
Hub starts (NerveHub.serve()):
    │
    ├─► _rotate_feed_if_needed()
    │    ├─► Check FEED_PATH.stat().st_size < MAX_FEED_BYTES (10 MB)
    │    │    └─► If small enough: return immediately (no rotation needed)
    │    │
    │    └─► If feed exceeds 10 MB:
    │         ├─► Create lock file: nerve_feed.rotate.lock
    │         ├─► fcntl.flock(lock_file, LOCK_EX)    ← PREVENT CONCURRENT ROTATION
    │         ├─► Double-check size (another process may have rotated)
    │         ├─► FEED_PATH.rename(archive_path)     ← e.g., nerve_feed_2026-05-10T14-30-00.jsonl
    │         ├─► Compress archive:
    │         │    └─► gzip.open(archive_path + '.gz') → creates nerve_feed_*.jsonl.gz
    │         │    └─► Delete uncompressed archive
    │         ├─► fcntl.flock(lock_file, LOCK_UN)
    │         └─► Delete lock file (missing_ok=True)
    │
    └─► Continue with hub startup (feed_file = open(FEED_PATH, 'a'))
         └─► Load existing event_count + ring_buffer from (now fresh) feed file
```

### 2.7 Feed Write Recovery (NEW — self-healing)

```
During event persistence in handle_client():
    │
    ├─► self.feed_file.write(event_line + '\n')
    ├─► self.feed_file.flush()
    │
    └─► If OSError:
         ├─► log_msg("Feed write failed, attempting recovery...")
         ├─► Try: self.feed_file.close()
         ├─► Try: self.feed_file = open(FEED_PATH, 'a')
         ├─► Try: self.feed_file.write(event_line + '\n') + flush()
         │    └─► log_msg("Feed write recovered")
         └─► If all fail: log_msg("Feed write recovery failed")
```

---

## 3. Inter-Module Dependency Graph

### 3.1 Import Dependencies

```
nervous_system.py
├── stdlib: asyncio, json, os, signal, sys, time
├── stdlib: pathlib.Path, datetime.datetime
├── stdlib: fcntl (NEW — file locking for feed rotation + fallback writes)
├── stdlib: collections.deque (NEW — RingBuffer implementation)
└── (NO project imports — fully independent module)

conversation_logger.py
├── stdlib: argparse, json, os, sys
├── stdlib: datetime (datetime, timezone), pathlib.Path
├── LOCAL: importlib.util → dynamic import of nervous_system.py
│   (CACHED — _nerve_fire() caches module reference, refreshes if file changes on disk)
└── (NO static project imports — nervous_system loaded dynamically with caching)

context_injector.py
├── stdlib: argparse, json, sys
├── stdlib: pathlib.Path
├── LOCAL: sys.path.insert(0, ~/.hermes/state)
│   ├── from conversation_logger import cmd_start, cmd_end, cmd_event
│   ├── from conversation_logger import get_context_for_cron, get_current_state
│   └── from conversation_logger import _get_entries_for_session, _get_recent_sessions
└── (ALL logic delegates to conversation_logger and reactor)

reactor.py
├── stdlib: argparse, json, sys
├── stdlib: datetime (datetime, timezone, timedelta), pathlib.Path
└── (NO project imports — pure read-only analysis module)
```

### 3.2 Call Graph

```
┌───────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL CALLERS                              │
│                                                                       │
│  Cron Job ──► context_injector.py ──► (no subcommand)                │
│  CLI       ──► context_injector.py ──► log-start/log-event/log-end   │
│  CLI       ──► conversation_logger.py ──► start/event/update/end    │
│  CLI       ──► nervous_system.py ──► serve/publish/recent/subscribe  │
│  CLI       ──► nervous_system.py ──► status/stop/healthcheck (NEW)  │
│  CLI       ──► reactor.py ──► (default) / --format / --focus         │
│  Systemd   ──► nervous_system.py serve                                │
└───────────────────────────────┬───────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐    ┌──────────────────┐    ┌──────────────────┐
│nervous_system │    │conversation_     │    │  reactor.py      │
│    .py        │    │  logger.py       │    │                  │
│               │    │                  │    │  react() ─────────┼──► reads
│ NerveHub      │    │ cmd_start()      │    │    ├─► _read_all_entries() ──► conv_log.jsonl
│   .serve()    │    │ cmd_event()       │    │    ├─► _get_current_state()──► current.json
│   .handle_    │    │ cmd_update()      │    │    └─► analyze → reactions dict
│   client()    │    │ cmd_end()          │    │
│   ._prune_    │    │ _append() ─────────┼───► writes conv_log.jsonl
│   stale_subs  │    │   └─► _nerve_fire()│──┐ │
│               │    │      (cached dyn.) │  │ │
│ RingBuffer    │    │                   │  │ │
│   .append()  │    │ get_context_for_   │  │ │
│   .recent()   │    │   cron()           │  │ │
│               │    │   ├─► reads conv_log│  │
│publish_event_ │    │   ├─► reads current│  │
│sync() ◄───────┼─────┤                   │  │
│               │    │   ├─► reads nerve_ │  │
│_feed_lock_   │    │   │    feed          │  │
│  write()     │    │   └─► calls reactor│  │
│               │    │        .react()◄──────┘
│_rotate_feed_ │    │                   │
│  if_needed() │    │ get_current_state()│
│               │    │ get_recent_        │
│cmd_healthcheck│    │   conversations() │
│cmd_publish()  │    │ _get_entries_for_ │
│cmd_recent()   │    │   session()        │
│cmd_status()   │    │ _get_recent_       │
│cmd_stop()     │    │   sessions()       │
│               │    │ _timestamp()       │
│get_recent_    │    │ _read_all_entries()│
│  events()     │    │ _update_current()  │
│get_status()   │    │ _build_parser()    │
│log_msg()      │    │                    │
│               │    └───────┬────────────┘
└───────┬───────┘            │
        │                    │
        │    ┌───────────────┘
        │    │
        ▼    ▼
┌───────────────────┐              ┌──────────────────┐
│  runa.sock        │              │  context_         │
│  (UDS, mode 0600) │              │  injector.py      │
│                   │              │                    │
│  Hub reads/writes │              │  main() ──────────┼───► conversation_logger
│  via asyncio      │              │  ├─► imports from │───► reactor (via conv_logger)
│                   │              │  │   conversation_ │
└───────────────────┘              └──┤   logger        │
                                        └─► delegates all │
                                           logic         │
```

### 3.3 Dependency Summary Table

| Module | Imports From | Calls Into | Written By | Read By |
|--------|-------------|-----------|------------|---------|
| `nervous_system.py` | (none, + `fcntl`, `collections.deque`) | (none — standalone) | `runa.sock`, `nerve_feed.jsonl`, `nervous_system.pid`, `nervous_system.log`, `nerve_feed_*.jsonl.gz` (archives) | `nerve_feed.jsonl` (seq recovery + ring buffer + recent), PID file |
| `conversation_logger.py` | `nervous_system.py` (dynamic, **cached**) | `publish_event_sync()` via cached dynamic import | `conversation_log.jsonl`, `current.json`, `conversations/` directory | `conversation_log.jsonl`, `current.json`, `nerve_feed.jsonl` (context gen) |
| `context_injector.py` | `conversation_logger` (static) | `cmd_start`, `cmd_end`, `cmd_event`, `get_context_for_cron`, `get_current_state`, `_get_entries_for_session`, `_get_recent_sessions` | (none — pure read/delegate) | (none directly — all via imports) |
| `reactor.py` | (none) | (none — pure analysis) | (none — read-only) | `conversation_log.jsonl`, `current.json` |

### 3.4 Module Coupling Assessment

- **nervous_system.py**: Zero coupling. No project imports. Can run in complete isolation. This is by design — the "dumb pipe" that is also now self-healing (feed rotation, subscriber pruning, write recovery).
- **conversation_logger.py**: One-way dynamic coupling to `nervous_system.py` via `_nerve_fire()`. **Now uses cached module reference** — refreshes only if the .py file changes on disk. The dynamic import means: (a) no hard dependency at import time, (b) failure is caught and silenced, (c) module updates are picked up automatically. Can operate without the nervous system.
- **context_injector.py**: Strong static coupling to `conversation_logger.py`. Cannot import without it. Is a pure adapter — no logic of its own.
- **reactor.py**: Zero coupling to other project modules. Pure data reader. Can operate independently.

**Coupling direction**: All arrows point to `nervous_system.py` (publishers → hub). No module reads from the hub via imports — they either write to it (publish) or subscribe via UDS (separate process).

---

## 4. Configuration Map

### 4.1 Filesystem Paths

| Constant | Value | Module | Purpose |
|----------|-------|--------|---------|
| `STATE_DIR` | `~/.hermes/state/` | All modules | Root of Verðandi's state tree |
| `SOCKET_PATH` | `~/.hermes/state/runa.sock` | nervous_system.py | Unix domain socket for IPC (mode 0600) |
| `FEED_PATH` | `~/.hermes/state/nerve_feed.jsonl` | nervous_system.py | Append-only event feed (rotated at 10 MB) |
| `PID_PATH` | `~/.hermes/state/nervous_system.pid` | nervous_system.py | PID file for hub process (atomic write) |
| `LOG_PATH` | `~/.hermes/state/nervous_system.log` | nervous_system.py | Hub operational log (fcntl-locked writes) |
| `CONV_LOG` | `~/.hermes/state/conversation_log.jsonl` | conversation_logger.py | Session journal |
| `CURRENT_FILE` | `~/.hermes/state/current.json` | conversation_logger.py | Active session state snapshot |
| `CONV_DIR` | `~/.hermes/state/conversations/` | conversation_logger.py | Per-session logs directory |

### 4.2 Self-Healing Constants (NEW)

| Constant | Value | Module | Purpose |
|----------|-------|--------|---------|
| `MAX_FEED_BYTES` | `10 * 1024 * 1024` (10 MB) | nervous_system.py | Feed rotation threshold |
| `RING_BUFFER_SIZE` | `256` | nervous_system.py | In-memory recent events buffer |
| `SUBSCRIBER_TIMEOUT_S` | `120` (2 min) | nervous_system.py | Seconds before subscriber considered stale |
| `SUBSCRIBER_PROBE_INTERVAL` | `30` (30 s) | nervous_system.py | How often to check for stale subscribers |

### 4.3 Systemd Unit

| Property | Value |
|----------|-------|
| **Unit file path** | `~/.config/systemd/user/runa-nervous-system.service` |
| **Description** | Runa Nervous System — Unix Domain Socket Event Bus |
| **Type** | `simple` |
| **ExecStart** | `/usr/bin/python3 /home/pi/.hermes/state/nervous_system.py serve` |
| **Restart** | `always` |
| **RestartSec** | `5` |
| **WorkingDirectory** | `/home/pi/.hermes/state` |
| **After** | `network.target` |
| **WantedBy** | `default.target` |

### 4.4 Operative Commands

```bash
# Service management
systemctl --user start runa-nervous-system     # Start hub
systemctl --user stop runa-nervous-system       # Stop hub (graceful SIGTERM)
systemctl --user restart runa-nervous-system    # Restart (5s settle)
systemctl --user status runa-nervous-system      # Status check

# CLI commands (all via python3)
python3 nervous_system.py serve                 # Start hub (foreground)
python3 nervous_system.py publish <type> '<json>' [source]  # Publish event
python3 nervous_system.py recent [count]         # Show recent events (uses ring buffer if hub running)
python3 nervous_system.py subscribe              # Live event tail
python3 nervous_system.py status                 # Hub status check
python3 nervous_system.py healthcheck            # Comprehensive health check (NEW)
python3 nervous_system.py stop                   # Stop hub via SIGTERM (5s grace → SIGKILL)

python3 conversation_logger.py start --session <id> [--summary] [--model] [--platform]
python3 conversation_logger.py event --session <id> --type <type> --content <text>
python3 conversation_logger.py update --session <id> [--next] [--blockers] [--projects] [--mood] [--summary]
python3 conversation_logger.py end --session <id> [--summary] [--duration <min>]
python3 conversation_logger.py show --session <id>
python3 conversation_logger.py recent [--count <n>]
python3 conversation_logger.py context [--sessions <n>]

python3 context_injector.py                      # Default: print full context
python3 context_injector.py log-start --session <id> [--summary] [--model] [--platform]
python3 context_injector.py log-event --session <id> --type <type> --content <text>
python3 context_injector.py log-end --session <id> [--summary] [--duration <min>]
python3 context_injector.py show --session <id>
python3 context_injector.py recent [--count <n>]
python3 context_injector.py context [--sessions <n>]

python3 reactor.py [--format text|json|brief] [--focus all|blockers|learnings|files|next]
```

### 4.5 Git Configuration

| Git-tracked | Gitignored |
|-------------|-----------|
| `nervous_system.py`, `conversation_logger.py`, `context_injector.py`, `reactor.py` | `__pycache__/`, `*.pyc` |
| All `.md` documentation files | `*.pid` |
| `.gitignore` | `nervous_system.log` |
| `nerve_feed.jsonl`, `conversation_log.jsonl`, `current.json` | |

---

## 5. Event Lifecycle Diagram

### 5.1 Complete Event Lifecycle — From Creation to Persistence to Notification (Post-Hardening)

```
═══════════════════════════════════════════════════════════════════════════════
                     EVENT LIFECYCLE — FULL PATH (HARDENED)
═══════════════════════════════════════════════════════════════════════════════

PHASE 1: CREATION ──────────────────────────────────────────────────────────

  Source triggers entry creation:
  ┌────────────────────────────────────────────────────────────────────────┐
  │ CLI call → conversation_logger.cmd_{start|event|update|end}()         │
  │   OR                                                                   │
  │ Cron call → context_injector.py → cmd_{start|event|end}()            │
  │   OR                                                                   │
  │ External → python3 nervous_system.py publish <type> '<json>'        │
  └────────────────────────────────────────────────────────────────────────┘

PHASE 2: ENTRY FORMATION ───────────────────────────────────────────────────

  ┌────────────────────────────────────────────────────────────────────────┐
  │ conversation_logger builds entry dict:                                │
  │   {                                                                    │
  │     "entry_type": "event",        ← start/event/update/end           │
  │     "timestamp": "2026-05-10T...Z", ← ISO 8601 UTC                    │
  │     "session_id": "...",          ← session identifier               │
  │     "event_type": "decision",     ← decision/file_changed/...       │
  │     "content": "..."              ← what happened                    │
  │   }                                                                    │
  │                                                                        │
  │  OR (direct publish via nervous_system.py):                            │
  │   {                                                                    │
  │     "type": "thought",            ← event type                        │
  │     "data": {"insight": "..."},  ← payload dict                      │
  │     "source": "volmarr_session"  ← origin identifier                │
  │   }                                                                    │
  └────────────────────────────────────────────────────────────────────────┘

PHASE 3: PERSISTENCE — LOCAL JOURNAL ──────────────────────────────────────

  ┌────────────────────────────────────────────────────────────────────────┐
  │ conversation_logger._append(entry)                                    │
  │   ├─► Open conversation_log.jsonl in append mode                      │
  │   ├─► Write json.dumps(entry) + "\n"                                 │
  │   └─► File flush (crash-safe — each line is independent)              │
  │                                                                        │
  │ conversation_logger._update_current(entry, session_id)                │
  │   ├─► Read existing current.json (merge if same session)              │
  │   ├─► Build updated current dict                                      │
  │   └─► Write current.json (full overwrite)                             │
  └────────────────────────────────────────────────────────────────────────┘

PHASE 4: NERVE IMPULSE (HARDENED) ──────────────────────────────────────────

  ┌────────────────────────────────────────────────────────────────────────┐
  │ conversation_logger._nerve_fire(entry)                                │
  │   ├─► Check cached _nerve_module reference                            │
  │   │    └─► If None or file path changed on disk: re-import module    │
  │   │       (CACHED dynamic import — refresh only when .py file changes)│
  │   ├─► Call ns.publish_event_sync(                                     │
  │   │       event_type=f"conv_{entry_type}",                            │
  │   │       data=entry,                                                  │
  │   │       source=f"conv_logger:{session_id}")                         │
  │   │    [HUB UP]  → UDS connect → send JSON → hub processes → ACK    │
  │   │    [HUB DOWN] → _feed_lock_write() with fcntl LOCK_EX             │
  │   │                   + fsync + _fallback:true                         │
  │   └─► except: pass  (nerve failure NEVER breaks the logger)          │
  │                                                                        │
  │  OR (direct via CLI):                                                  │
  │   python3 nervous_system.py publish <type> '<json>'                   │
  │        → publish_event_sync(event_type, data, source)                  │
  └────────────────────────────────────────────────────────────────────────┘

PHASE 5: HUB PROCESSING (HARDENED) ───────────────────────────────────────

  ┌────────────────────────────────────────────────────────────────────────┐
  │ HUB UP (normal path, with self-healing):                              │
  │                                                                        │
  │   publish_event_sync()                                                  │
  │   ├─► Create Unix socket → connect to runa.sock (mode 0600)          │
  │   ├─► Send json.dumps({"type":...,"data":...,"source":...}) + "\n"   │
  │   ├─► Set 2-second timeout on socket                                  │
  │   └─► Read response (ACK or fallback)                                 │
  │                                                                        │
  │   NerveHub.handle_client(reader, writer)                              │
  │   ├─► Read with asyncio.wait_for(timeout=SUBSCRIBER_TIMEOUT_S)       │
  │   │    └─► Timeout → log + disconnect stale client                   │
  │   ├─► Parse incoming JSON                                              │
  │   ├─► Check nerve_type:                                               │
  │   │    ├─ "subscribe" → add to subscribers + subscriber_times dict   │
  │   │    ├─ "ping"      → update subscriber_times, send pong              │
  │   │    ├─ "recent"    → send ring_buffer.recent(count)                │
  │   │    └─ else         → PUBLISH EVENT                                  │
  │   │         ├─► Increment event_count → _seq                          │
  │   │         ├─► Set _ts = time.time(), _iso = datetime.utcnow()        │
  │   │         ├─► Remove nerve_type from event                           │
  │   │         ├─► Write json.dumps(event) to self.feed_file              │
  │   │         │    + flush()                                              │
  │   │         │    + ON ERROR: close+reopen+rewrite (write recovery)    │
  │   │         ├─► Append to self.ring_buffer (RingBuffer, max 256)     │
  │   │         ├─► BROADCAST to all subscribers                           │
  │   │         │    for sub in subscribers:                                │
  │   │         │        sub.write(broadcast_bytes)                        │
  │   │         │        await sub.drain()                                 │
  │   │         │    (dead subscribers removed from set + times dict)    │
  │   │         └─► Send {"nerve_type":"ack","seq":N} to publisher        │
  │                                                                        │
  │   Background tasks:                                                    │
  │   ├─► _prune_stale_subscribers() every 30s                             │
  │   │    └─► Remove subscribers inactive > 120s                        │
  │   │    └─► Log + close stale connections                              │
  │                                                                        │
  │   Hub startup:                                                         │
  │   ├─► Check for stale PID (os.kill(old_pid, 0))                       │
  │   │    └─► Clean up if process not running                            │
  │   ├─► Remove stale socket file                                        │
  │   ├─► _rotate_feed_if_needed() — archive + gzip if > 10 MB          │
  │   ├─► chmod(SOCKET_PATH, 0o600) — harden socket permissions          │
  │   ├─► Atomic PID write (tmp file + rename)                            │
  │   ├─► Load event_count from feed + ring_buffer                        │
  │   └─► Start _prune_stale_subscribers() background task                │
  │                                                                        │
  │   Graceful shutdown:                                                   │
  │   ├─► Send {"nerve_type":"shutdown"} to all subscribers               │
  │   ├─► Drain all subscriber connections                                │
  │   ├─► Close server socket                                             │
  │   ├─► Close feed_file                                                │
  │   ├─► Unlink socket file                                             │
  │   └─► Unlink PID file                                                │
  │                                                                        │
  │ HUB DOWN (fallback path, with file locking):                         │
  │                                                                        │
  │   publish_event_sync() catches ConnectionRefusedError/FileNotFoundError│
  │   ├─► Set _ts = time.time(), _iso = datetime.utcnow()                 │
  │   ├─► Set _fallback = True                                           │
  │   ├─► _feed_lock_write(json.dumps(event))                             │
  │   │    ├─► FEED_PATH.parent.mkdir(parents=True, exist_ok=True)       │
  │   │    ├─► open(FEED_PATH, 'a')                                      │
  │   │    ├─► fcntl.flock(f, LOCK_EX)  ← CONCURRENT WRITE SAFETY       │
  │   │    ├─► f.write(line + '\n')                                       │
  │   │    ├─► f.flush() + os.fsync(f)  ← DURABLE WRITE                  │
  │   │    ├─► fcntl.flock(f, LOCK_UN)                                  │
  │   │    └─► NO _seq assigned (hub is down)                            │
  │   └─► Return {"nerve_type":"fallback","note":"hub_offline_written_to_feed"}│
  └────────────────────────────────────────────────────────────────────────┘

PHASE 6: BROADCAST ──────────────────────────────────────────────────────

  ┌────────────────────────────────────────────────────────────────────────┐
  │ For each connected subscriber in self.subscribers:                    │
  │   ├─► writer.write(json.dumps(event).encode() + b"\n")                │
  │   ├─► await writer.drain()                                            │
  │   └─► On (ConnectionError/OSError/BrokenPipeError):                   │
  │        └─► Add to dead set, remove from subscribers + subscriber_times│
  │                                                                        │
  │ Subscriber receives event as:                                          │
  │   {                                                                    │
  │     "type": "conv_event",                                             │
  │     "data": { ... full entry dict ... },                              │
  │     "source": "conv_logger:2026-05-10-...",                            │
  │     "_seq": 42,                                                         │
  │     "_ts": 1778435811.736587,                                          │
  │     "_iso": "2026-05-10T17:56:51.736587Z"                              │
  │   }\n                                                                  │
  │                                                                        │
  │ On hub shutdown:                                                       │
  │   └─► {"nerve_type": "shutdown", "message": "Hub shutting down"}       │
  └────────────────────────────────────────────────────────────────────────┘

PHASE 7: PERSISTENCE — NERVE FEED (HARDENED) ───────────────────────────────

  ┌────────────────────────────────────────────────────────────────────────┐
  │ nerve_feed.jsonl — append-only log of ALL events                     │
  │                                                                        │
  │ Hub-written events have:  _seq, _ts, _iso, NO _fallback flag        │
  │ Fallback events have:      _ts, _iso, _fallback: true, NO _seq      │
  │                                                                        │
  │ Each line is self-contained JSON. No cross-line dependencies.         │
  │                                                                        │
  │ SELF-HEALING FEATURES:                                                │
  │ ├─► Feed rotation at 10 MB: archive + gzip compress                  │
  │ │    Archive naming: nerve_feed_YYYY-MM-DDTHH-MM-SS.jsonl.gz       │
  │ ├─► File locking: fcntl LOCK_EX on all fallback writes (concurrent   │
  │ │    safety when hub is down and multiple processes write directly)  │
  │ ├─► Write recovery: if feed_file.write() fails, close+reopen+retry  │
  │ ├─► Ring buffer: last 256 events held in memory for fast retrieval  │
  │ └─► Log writes also use fcntl locking for concurrent safety          │
  │                                                                        │
  │ Current growth rate: ~200-500 bytes/event → rotation at ~20K events  │
  │ Archive retention: uncompressed JSONL → gzip compression → keep .gz  │
  └────────────────────────────────────────────────────────────────────────┘

PHASE 8: CONSUMPTION ─────────────────────────────────────────────────────

  ┌────────────────────────────────────────────────────────────────────────┐
  │ CONSUMERS of nerve_feed.jsonl:                                         │
  │                                                                        │
  │ 1. NerveHub.serve() on startup                                        │
  │    └─► Reads entire feed to recover max _seq for event_count          │
  │    └─► Loads last RING_BUFFER_SIZE events into ring_buffer            │
  │                                                                        │
  │ 2. get_recent_events(count)                                            │
  │    └─► If hub running: UDS request → ring_buffer.recent(count)        │
  │    └─► If hub not running: read feed file, return last N entries      │
  │                                                                        │
  │ 3. get_context_for_cron()                                              │
  │    └─► Reads last 10 events for context injection block               │
  │                                                                        │
  │ 4. cmd_healthcheck()                                                   │
  │    └─► Verifies: state dir, socket (ping), PID, feed (size+parseable) │
  │    └─► Warns if feed > 80% of MAX_FEED_BYTES                          │
  │                                                                        │
  │ CONSUMERS of conversation_log.jsonl:                                   │
  │                                                                        │
  │ 1. conversation_logger self-query (_get_entries_for_session, etc.)    │
  │ 2. reactor.react() — analyzes ALL entries for reaction directives    │
  │                                                                        │
  │ CONSUMERS of current.json:                                             │
  │                                                                        │
  │ 1. conversation_logger (merge with same session)                      │
  │ 2. context_injector (display active state)                            │
  │ 3. reactor.react() (check active session blockers, next_actions)     │
  └────────────────────────────────────────────────────────────────────────┘

PHASE 9: REACTION (Skuld's Domain) ─────────────────────────────────────────

  ┌────────────────────────────────────────────────────────────────────────┐
  │ reactor.react() reads conversation_log.jsonl + current.json +         │
  │Produces prioritized reaction directives:                               │
  │                                                                        │
  │ Priority HIGH:   resolve_blockers — unresolved blockers               │
  │ Priority MEDIUM:  close_stale_sessions, verify_pushed, store_learnings│
  │ Priority LOW:    continue_work — next actions from last session       │
  │ Priority INFO:   celebrate — milestones achieved                      │
  │                                                                        │
  │ Output formats: text (full report), json (machine), brief (one-line)  │
  │                                                                        │
  │ reactor is READ-ONLY. It never writes. It observes and recommends.    │
  └────────────────────────────────────────────────────────────────────────┘

PHASE 10: CONTEXT INJECTION (for cron jobs) ────────────────────────────────

  ┌────────────────────────────────────────────────────────────────────────┐
  │ get_context_for_cron() assembles:                                      │
  │                                                                        │
  │ === RUNA SESSION CONTEXT (auto-injected) ===                          │
  │ [Active session state from current.json]                              │
  │ [Recent N sessions from conversation_log.jsonl]                        │
  │ [Last 10 nerve events from nerve_feed.jsonl]                          │
  │ [Reaction directives from reactor.react()]                             │
  │ === END CONTEXT ===                                                    │
  │                                                                        │
  │ This block is printed to STDOUT by:                                    │
  │   python3 context_injector.py           (default, no args)            │
  │   python3 context_injector.py context   (explicit)                    │
  │   python3 conversation_logger.py context                               │
  │                                                                        │
  │ And injected into cron job AI prompts for cross-instance awareness.    │
  └────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Observed Event Types

| Type | Source | Description |
|------|--------|-------------|
| `conv_start` | conversation_logger | Session opened |
| `conv_event` | conversation_logger | Event within a session (decision, file_changed, etc.) |
| `conv_update` | conversation_logger | State snapshot checkpoint |
| `conv_end` | conversation_logger | Session closed |
| `heartbeat` | external | Liveness check |
| `perception` | external | External observation logged |
| `milestone` | external | Achievement marker |
| `ping` | status_check | Hub status probe |
| `recent` | status_check | Request recent events via ring buffer |
| `thought` | volmarr_session | Insight or internal reasoning |
| `shutdown` | nerve_hub | Hub shutting down notification (NEW) |

### 5.3 Data Persistence Guarantees

| Write Path | Persistence | Crash Safety | Race Condition Safety |
|------------|-------------|---------------|----------------------|
| `conversation_log.jsonl` | Append-only, each line independent | Crash-safe: last line may be partial | Single writer (per process) |
| `nerve_feed.jsonl` (via hub) | Append + flush after each event | Flush ensures write to OS. Write recovery: close+reopen on error | Sequential within hub (single-threaded asyncio) |
| `nerve_feed.jsonl` (fallback) | Append + fcntl LOCK_EX + fsync | fcntl + fsync = maximum durability for direct writes | **Concurrent-safe via fcntl LOCK_EX** |
| `nerve_feed.jsonl` (rotation) | Atomic-ish: lock file + rename + gzip | Rotation lock prevents concurrent rotation. Double-check size under lock. | **Rotation lock file prevents races** |
| `current.json` | Full overwrite each operation | Old file until new write completes | Last-writer-wins |
| `nervous_system.pid` | Atomic: write .tmp + rename | Atomic rename prevents partial writes | **Atomic via tmp+rename** |
| `nervous_system.log` | Append-only, fcntl LOCK_EX | Timestamped lines | **Concurrent-safe via fcntl** |
| `runa.sock` | Created on start, mode 0600 | Clean lifecycle | Single owner (hub process) |

---

## 6. Systemd Service Topology

```
┌─────────────────────────────────────────────────────────────────────┐
│                     LINUX SYSTEM (user: pi)                         │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  systemd --user                                                │  │
│  │  ┌─────────────────────────────────────────────────────────┐  │  │
│  │  │  runa-nervous-system.service                             │  │  │
│  │  │  ExecStart: python3 nervous_system.py serve              │  │  │
│  │  │  Restart: always  RestartSec: 5                          │  │  │
│  │  │  Status: active (running)                                 │  │  │
│  │  └──────────────────────────────┬──────────────────────────┘  │  │
│  │                                 │                               │  │
│  │    ┌────────────────────────────┘                               │  │
│  │    │ Listens on                                                │  │
│  │    ▼                                                           │  │
│  │  ~/.hermes/state/runa.sock (Unix Domain Socket, mode 0600)    │  │
│  │                                                                 │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │  │
│  │  │ Publisher A  │  │ Publisher B  │  │  Publisher C      │     │  │
│  │  │ (telegram    │  │ (cron job    │  │  (CLI manual      │     │  │
│  │  │  session)    │  │  via context│  │   publish cmd)    │     │  │
│  │  │ _nerve_fire  │  │  _injector)  │  │  publish_event_  │     │  │
│  │  │  → UDS       │  │  → UDS      │  │   sync → UDS     │     │  │
│  │  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘     │  │
│  │         │                 │                   │                 │  │
│  │         └─────────────────┼───────────────────┘                 │  │
│  │                           │ connect to runa.sock                │  │
│  │                           ▼                                     │  │
│  │               ┌──────────────────────┐                         │  │
│  │               │  NERVE HUB            │                         │  │
│  │               │  asyncio event loop   │                         │  │
│  │               │  handle_client()      │                         │  │
│  │               │  RingBuffer(256)      │                         │  │
│  │               │  _prune_stale_subs()  │                         │  │
│  │               └───┬─────┬─────┬──────┘                         │  │
│  │                   │     │     │                                  │  │
│  │      nerve_feed   │     │     │ broadcast                      │  │
│  │      .jsonl +     │     │     │ (to subscribers)                │  │
│  │      .jsonl.gz    │     │     │                                  │  │
│  │      (archives)   │     │     │                                  │  │
│  │                   │     │     │                                  │  │
│  │                   ▼     ▼     ▼                                  │  │
│  │         ┌─────────┐ ┌────────┐ ┌──────────────┐              │  │
│  │         │subscriber│ │subscriber│ │  n.s.log     │              │  │
│  │         │(reactor) │ │(monitor)│ │ (fcntl-lock) │              │  │
│  │         └─────────┘ └────────┘ └──────────────┘              │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Cron Jobs (user crontab or systemd timers)                       │  │
│  │  ┌──────────────────────────────────────────────────────────┐    │  │
│  │  │  python3 context_injector.py  →  STDOUT → AI prompt      │    │  │
│  │  │  python3 context_injector.py log-start ...                │    │  │
│  │  │  python3 context_injector.py log-event ...               │    │  │
│  │  │  python3 context_injector.py log-end ...                  │    │  │
│  │  └──────────────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 7. The Three Norns — Architectural Mapping

| Norn | Domain | Component | File(s) | Function |
|------|--------|-----------|---------|----------|
| **Urðr** (Past) | What has been | Persistent feeds | `nerve_feed.jsonl`, `nerve_feed_*.jsonl.gz` (archives), `conversation_log.jsonl` | Append-only records of everything that happened. Archives compressed but retained. |
| **Verðandi** (Present) | What is becoming | Nerve Hub | `nervous_system.py`, `runa.sock` | Real-time routing, stamping, broadcasting of live events. Now self-healing with feed rotation, subscriber pruning, and write recovery. |
| **Skuld** (Future) | What shall be | Reactor | `reactor.py` | Reads past + present, generates prioritized directives for what to do next |

The loop closes: Urðr records → Verðandi routes → Skuld directs → action creates new events → Verðandi routes them → Urðr records them → Skuld reads them → repeat.

New in this cycle: Verðandi now self-heals. The feed rotates before it overflows, stale subscribers are pruned, writes are locked for concurrency, feed errors trigger recovery, and the healthcheck command verifies the whole system.

---

## 8. Function Inventory (Post-Hardening)

### 8.1 nervous_system.py

**Module-level functions:**
| Function | Lines | Purpose |
|----------|-------|---------|
| `log_msg(msg)` | ~63-74 | Append to nerve hub log with fcntl LOCK_EX for concurrent safety |
| `_feed_lock_write(event_line)` | ~77-87 | Append to feed file with fcntl LOCK_EX + flush + fsync |
| `_rotate_feed_if_needed()` | ~90-142 | Archive feed file (rename + gzip) when > 10 MB; uses lock file for atomicity |
| `publish_event_sync(event_type, data, source)` | ~438-479 | Publish event to hub via UDS; fallback to _feed_lock_write if down |
| `get_recent_events(count)` | ~482-526 | Get recent events from hub (ring buffer) or fallback to file |
| `cmd_healthcheck()` | ~529-620 | Comprehensive health check: directory, socket, PID, feed, log |
| `get_status()` | ~623-665 | Get nerve hub status dict |
| `subscribe()` | ~668-706 | Connect to hub and print live events (async) |
| `cmd_publish(args)` | ~709-730 | CLI: publish an event |
| `cmd_recent(args)` | ~733-751 | CLI: show recent events |
| `cmd_status()` | ~754-763 | CLI: show hub status |
| `cmd_stop()` | ~766-803 | CLI: stop hub gracefully (SIGTERM → 5s → SIGKILL) |
| `main()` | ~806-841 | CLI entry point with command dispatch |

**NerveHub class methods:**
| Method | Purpose |
|--------|---------|
| `__init__()` | Initialize: subscribers set, subscriber_times dict, event_count, ring_buffer, shutdown_event |
| `handle_client(reader, writer)` | Main connection handler: parse JSON, route (subscribe/ping/recent/publish), stamp, persist, broadcast, ACK |
| `_prune_stale_subscribers()` | Background task: every 30s, remove subscribers inactive > 120s |
| `serve()` | Start hub: stale PID check, socket creation (0600), feed rotation, PID write, ring buffer preload, accept connections, graceful shutdown |

**RingBuffer class methods:**
| Method | Purpose |
|--------|---------|
| `__init__(maxlen)` | Initialize deque with max length |
| `append(event)` | Add event to buffer (evicts oldest if full) |
| `recent(count)` | Return last N events from buffer |
| `__len__()` | Return buffer length |

### 8.2 conversation_logger.py

| Function | Purpose |
|----------|---------|
| `_timestamp()` | Return ISO 8601 UTC timestamp |
| `_nerve_fire(entry)` | Fire nerve impulse via cached dynamic import of nervous_system |
| `_append(entry)` | Append entry to JSONL log + update current.json + fire nerve impulse |
| `_update_current(entry, session_id)` | Update current.json with latest session state |
| `cmd_start(args)` | CLI: start a new session |
| `cmd_event(args)` | CLI: log an event |
| `cmd_update(args)` | CLI: update session state |
| `cmd_end(args)` | CLI: close a session |
| `cmd_show(args)` | CLI: show all entries for a session |
| `cmd_recent(args)` | CLI: show recent sessions |
| `cmd_context(args)` | CLI: generate context block |
| `_read_all_entries()` | Read all entries from conversation_log.jsonl |
| `_get_entries_for_session(session_id)` | Filter entries by session_id |
| `_get_recent_sessions(count)` | Get recent unique sessions |
| `get_context_for_cron(max_sessions)` | Assemble full context injection block |
| `get_current_state()` | Read current.json (public API) |
| `get_recent_conversations(n)` | Public API wrapper for _get_recent_sessions |
| `_build_parser()` | Build argparse CLI parser |

### 8.3 context_injector.py

| Function | Purpose |
|----------|---------|
| `main()` | CLI entry: dispatch log-start, log-event, log-end, show, recent, context, or default context |

### 8.4 reactor.py

| Function | Purpose |
|----------|---------|
| `_read_all_entries()` | Read all entries from conversation_log.jsonl |
| `_get_current_state()` | Read current.json |
| `_parse_timestamp(ts)` | Parse ISO timestamp string |
| `react(focus)` | Core analysis engine: produce prioritized reaction directives |
| `format_reactions(reactions, fmt)` | Format reactions for output (text/json/brief) |

---

*Map redrawn by Védis Eikleið, Cartographer of Mythic Engineering*
*Post-hardening update — reflecting 2026-05-10 Forge Worker pass*
*Under the light of Urðr, by the loom of Verðandi, for the future that Skuld obliges*
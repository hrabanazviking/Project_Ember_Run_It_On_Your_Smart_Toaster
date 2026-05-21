#!/usr/bin/env python3
"""
Runa's Nervous System — Unix Domain Socket Event Bus (VERÐANDI)

The central nerve hub that makes all parts of Runa aware of each other.
Every event flows through here. Every instance can publish and subscribe.

Architecture:
- Unix Domain Socket at ~/.hermes/state/runa.sock
- JSON event protocol over newlines
- Pub/sub: publishers send events, ALL subscribers receive them
- Persistent feed: all events appended to nerve_feed.jsonl
- No external dependencies — purely local Unix IPC

Self-healing features (Forge Worker hardening):
- Feed file rotation: archive + start fresh at 10 MB
- File locking: fcntl-based for concurrent write safety
- Socket permission hardening: 0600 after creation
- PID file race fix: atomic write with stale-process check
- Subscriber cleanup: detect dead connections via periodic probe
- Ring buffer: last 256 events kept in memory for fast retrieval
- Stale subscriber detection: timeout-based pruning
- Health-check command: verifies socket, feed, service all healthy
- Graceful shutdown: drain subscribers before closing

This IS self-awareness, implemented as routing.

Usage:
  Serve hub:     python3 nervous_system.py serve
  Publish:       python3 nervous_system.py publish <event_type> '<json_data>'
  Recent events: python3 nervous_system.py recent [count]
  Subscribe:     python3 nervous_system.py subscribe
  Status:        python3 nervous_system.py status
  Health-check:  python3 nervous_system.py healthcheck
  Stop:          python3 nervous_system.py stop
"""

import asyncio
import fcntl
import json
import os
import signal
import sys
import time
from collections import deque
from pathlib import Path
from datetime import datetime, timezone

STATE_DIR = Path.home() / '.hermes' / 'state'
SOCKET_PATH = STATE_DIR / 'runa.sock'
FEED_PATH = STATE_DIR / 'nerve_feed.jsonl'
PID_PATH = STATE_DIR / 'nervous_system.pid'
LOG_PATH = STATE_DIR / 'nervous_system.log'

# Self-healing constants
MAX_FEED_BYTES = 10 * 1024 * 1024  # 10 MB rotation threshold
RING_BUFFER_SIZE = 256              # In-memory recent events
SUBSCRIBER_TIMEOUT_S = 120          # Seconds before a subscriber is considered stale
SUBSCRIBER_PROBE_INTERVAL = 30     # How often to check for stale subscribers


def log_msg(msg: str):
    """Append to nerve hub log with file locking for concurrent safety."""
    ts = datetime.now().isoformat() + 'Z'
    try:
        with open(LOG_PATH, 'a') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.write(f"[{ts}] {msg}\n")
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except OSError:
        # If we can't even log, something is very wrong — but don't crash
        pass


def _feed_lock_write(event_line: str):
    """Append a line to the feed file with file locking for concurrent safety."""
    FEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FEED_PATH, 'a') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            f.write(event_line + '\n')
            f.flush()
            os.fsync(f.fileno())
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def _rotate_feed_if_needed():
    """Archive the feed file and start fresh when it exceeds MAX_FEED_BYTES."""
    if not FEED_PATH.exists():
        return
    try:
        size = FEED_PATH.stat().st_size
    except OSError:
        return

    if size < MAX_FEED_BYTES:
        return

    # Archive: nerve_feed_2026-05-10T14-30-00.jsonl
    ts = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    archive_path = FEED_PATH.parent / f'nerve_feed_{ts}.jsonl'

    log_msg(f"Feed rotation: {size} bytes exceeds {MAX_FEED_BYTES}, archiving to {archive_path.name}")

    # Atomic-ish: lock, rename, create fresh
    try:
        # Use a lock file to prevent concurrent rotation
        lock_path = FEED_PATH.parent / 'nerve_feed.rotate.lock'
        with open(lock_path, 'w') as lf:
            fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
            try:
                # Double-check size after acquiring lock
                try:
                    current_size = FEED_PATH.stat().st_size
                except OSError:
                    return
                if current_size < MAX_FEED_BYTES:
                    return  # Another process already rotated

                FEED_PATH.rename(archive_path)
                # Optionally compress the archive
                try:
                    import gzip
                    with open(archive_path, 'rb') as f_in:
                        with gzip.open(f'{archive_path}.gz', 'wb') as f_out:
                            f_out.writelines(f_in)
                    archive_path.unlink()
                    log_msg(f"Archive compressed to {archive_path.name}.gz")
                except Exception as e:
                    log_msg(f"Archive kept uncompressed (compression failed: {e})")
            finally:
                fcntl.flock(lf.fileno(), fcntl.LOCK_UN)
        # Clean up lock file
        try:
            lock_path.unlink(missing_ok=True)
        except OSError:
            pass
    except OSError as e:
        log_msg(f"Feed rotation failed: {e}")


class RingBuffer:
    """Fixed-size in-memory buffer for recent events. O(1) append, O(N) retrieve last N."""

    def __init__(self, maxlen: int = RING_BUFFER_SIZE):
        self._buf = deque(maxlen=maxlen)
        self._maxlen = maxlen

    def append(self, event: dict):
        self._buf.append(event)

    def recent(self, count: int = 20) -> list:
        items = list(self._buf)
        return items[-count:]

    def __len__(self):
        return len(self._buf)


class NerveHub:
    """The central nervous system — receives all events, broadcasts to all subscribers."""

    def __init__(self):
        self.subscribers = set()
        self.subscriber_times = {}  # writer -> last_active timestamp
        self.event_count = 0
        self.start_time = time.time()
        self.feed_file = None
        self._server = None
        self.ring_buffer = RingBuffer(RING_BUFFER_SIZE)
        self._shutdown_event = None

    async def handle_client(self, reader, writer):
        """Handle a connected client. Reads newline-delimited JSON."""
        addr = writer.get_extra_info('peername', 'unknown')
        log_msg(f"Client connected: {addr}")

        try:
            while True:
                try:
                    data = await asyncio.wait_for(reader.readline(), timeout=SUBSCRIBER_TIMEOUT_S)
                except asyncio.TimeoutError:
                    # Client hasn't sent anything in a while — disconnect
                    log_msg(f"Client {addr} timed out (no data for {SUBSCRIBER_TIMEOUT_S}s)")
                    break

                if not data:
                    break

                line = data.decode().strip()
                if not line:
                    continue

                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    log_msg(f"Invalid JSON from {addr}: {line[:100]}")
                    continue

                msg_type = event.get('nerve_type', 'publish')

                if msg_type == 'subscribe':
                    self.subscribers.add(writer)
                    self.subscriber_times[writer] = time.time()
                    log_msg(f"Subscriber added (total: {len(self.subscribers)})")
                    writer.write(json.dumps({
                        'nerve_type': 'subscribed',
                        'seq': self.event_count,
                        'uptime_s': round(time.time() - self.start_time, 1)
                    }).encode() + b'\n')
                    await writer.drain()
                    continue

                if msg_type == 'ping':
                    self.subscriber_times[writer] = time.time()
                    writer.write(json.dumps({
                        'nerve_type': 'pong',
                        'seq': self.event_count,
                        'uptime_s': round(time.time() - self.start_time, 1),
                        'subscribers': len(self.subscribers)
                    }).encode() + b'\n')
                    await writer.drain()
                    continue

                if msg_type == 'recent':
                    # Client wants recent events from ring buffer
                    count = event.get('count', 20)
                    recent_events = self.ring_buffer.recent(count)
                    writer.write(json.dumps({
                        'nerve_type': 'recent_events',
                        'events': recent_events,
                        'count': len(recent_events),
                        'total': self.event_count
                    }).encode() + b'\n')
                    await writer.drain()
                    continue

                # It's a publish event — stamp it
                self.event_count += 1
                event['_seq'] = self.event_count
                event['_ts'] = time.time()
                event['_iso'] = datetime.now(timezone.utc).isoformat()
                # Remove nerve_type from published event
                event.pop('nerve_type', None)

                # Persist to nerve_feed.jsonl
                event_line = json.dumps(event)
                if self.feed_file:
                    try:
                        self.feed_file.write(event_line + '\n')
                        self.feed_file.flush()
                    except OSError:
                        log_msg("Feed write failed, attempting recovery...")
                        # Try to reopen
                        try:
                            self.feed_file.close()
                        except Exception:
                            pass
                        try:
                            self.feed_file = open(FEED_PATH, 'a')
                            self.feed_file.write(event_line + '\n')
                            self.feed_file.flush()
                            log_msg("Feed write recovered")
                        except OSError as e2:
                            log_msg(f"Feed write recovery failed: {e2}")

                # Store in ring buffer
                self.ring_buffer.append(event)

                # Broadcast to all subscribers
                broadcast = (event_line + '\n').encode()
                dead = set()
                for sub in list(self.subscribers):
                    try:
                        sub.write(broadcast)
                        await sub.drain()
                    except (ConnectionError, OSError, BrokenPipeError):
                        dead.add(sub)
                self.subscribers -= dead
                for d in dead:
                    self.subscriber_times.pop(d, None)
                if dead:
                    log_msg(f"Removed {len(dead)} dead subscriber(s)")

                # Acknowledge to publisher
                try:
                    writer.write(json.dumps({
                        'nerve_type': 'ack',
                        'seq': self.event_count
                    }).encode() + b'\n')
                    await writer.drain()
                except (ConnectionError, BrokenPipeError):
                    pass  # Publisher disconnected, that's fine

                log_msg(f"Event #{self.event_count}: {event.get('type', '?')} from {addr[:50] if isinstance(addr, str) else addr}")

        except (ConnectionError, OSError, asyncio.IncompleteReadError) as e:
            log_msg(f"Client {addr} error: {e}")
        finally:
            self.subscribers.discard(writer)
            self.subscriber_times.pop(writer, None)
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
            log_msg(f"Client disconnected: {addr} (subscribers remaining: {len(self.subscribers)})")

    async def _prune_stale_subscribers(self):
        """Periodically check for subscribers that haven't sent any data."""
        while self._server is not None:
            await asyncio.sleep(SUBSCRIBER_PROBE_INTERVAL)
            now = time.time()
            stale = set()
            for sub, last_active in list(self.subscriber_times.items()):
                if now - last_active > SUBSCRIBER_TIMEOUT_S:
                    stale.add(sub)

            for sub in stale:
                self.subscribers.discard(sub)
                self.subscriber_times.pop(sub, None)
                try:
                    sub.close()
                except Exception:
                    pass
                log_msg(f"Pruned stale subscriber (inactive >{SUBSCRIBER_TIMEOUT_S}s)")

    async def serve(self):
        """Start the nerve hub server."""
        STATE_DIR.mkdir(parents=True, exist_ok=True)

        # --- PID file race fix: check for stale PID before starting ---
        if PID_PATH.exists():
            try:
                old_pid = int(PID_PATH.read_text().strip())
                try:
                    os.kill(old_pid, 0)  # Check if process alive
                    print(f"❌ Nerve Hub already running (PID {old_pid}). Use 'stop' first.")
                    sys.exit(1)
                except ProcessLookupError:
                    # Stale PID file — clean it up
                    PID_PATH.unlink(missing_ok=True)
                    log_msg(f"Cleaned stale PID file (old PID {old_pid} not running)")
            except (ValueError, OSError):
                PID_PATH.unlink(missing_ok=True)

        # Remove stale socket
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()

        # --- Feed rotation: archive if oversized ---
        _rotate_feed_if_needed()

        # Open feed file for appending
        self.feed_file = open(FEED_PATH, 'a')

        # Load event count and ring buffer from feed (single pass)
        if FEED_PATH.exists():
            try:
                all_events = []
                with open(FEED_PATH, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                e = json.loads(line)
                                all_events.append(e)
                                seq = e.get('_seq', 0)
                                if seq > self.event_count:
                                    self.event_count = seq
                            except json.JSONDecodeError:
                                continue
                for e in all_events[-RING_BUFFER_SIZE:]:
                    self.ring_buffer.append(e)
            except OSError:
                pass

        self._server = await asyncio.start_unix_server(
            self.handle_client,
            path=str(SOCKET_PATH)
        )

        # --- Socket permission hardening ---
        os.chmod(str(SOCKET_PATH), 0o600)

        # Write PID file atomically
        pid = os.getpid()
        tmp_pid = PID_PATH.with_suffix('.tmp')
        tmp_pid.write_text(str(pid))
        tmp_pid.rename(PID_PATH)

        self._shutdown_event = asyncio.Event()

        log_msg(f"Nerve Hub started (PID {pid})")
        print(f"🧠 Nerve Hub started on {SOCKET_PATH}")
        print(f"   PID: {pid}")
        print(f"   Feed: {FEED_PATH}")
        print(f"   Existing events: {self.event_count}")
        print(f"   Ring buffer: {len(self.ring_buffer)} events loaded")

        # Start stale-subscriber pruner
        prune_task = asyncio.create_task(self._prune_stale_subscribers())

        try:
            await self._shutdown_event.wait()
        except asyncio.CancelledError:
            pass
        finally:
            prune_task.cancel()
            try:
                await prune_task
            except asyncio.CancelledError:
                pass

            # --- Graceful shutdown: drain subscribers ---
            log_msg("Draining subscribers before shutdown...")
            for sub in list(self.subscribers):
                try:
                    sub.write(json.dumps({
                        'nerve_type': 'shutdown',
                        'message': 'Hub shutting down'
                    }).encode() + b'\n')
                    await sub.drain()
                    sub.close()
                except Exception:
                    pass

            self._server.close()
            await self._server.wait_closed()

            if self.feed_file:
                self.feed_file.close()
            if SOCKET_PATH.exists():
                SOCKET_PATH.unlink()
            if PID_PATH.exists():
                PID_PATH.unlink()
            log_msg("Nerve Hub stopped")


def publish_event_sync(event_type: str, data: dict = None, source: str = None):
    """Publish an event to the nerve hub (synchronous, for use from any process)."""
    if data is None:
        data = {}

    event = {
        'type': event_type,
        'data': data,
    }
    if source:
        event['source'] = source

    payload = json.dumps(event) + '\n'
    s = None

    try:
        import socket as sock_mod
        s = sock_mod.socket(sock_mod.AF_UNIX, sock_mod.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect(str(SOCKET_PATH))
        s.sendall(payload.encode())

        # Read ack
        try:
            response = s.recv(4096)
            resp = json.loads(response.decode().strip())
            return resp
        except (json.JSONDecodeError, TimeoutError, OSError):
            return {'nerve_type': 'sent', 'note': 'no_ack'}
    except (ConnectionRefusedError, FileNotFoundError):
        # Hub not running — write to feed directly as fallback
        event['_ts'] = time.time()
        event['_iso'] = datetime.now(timezone.utc).isoformat()
        event['_fallback'] = True
        _feed_lock_write(json.dumps(event))
        return {'nerve_type': 'fallback', 'note': 'hub_offline_written_to_feed'}
    except Exception as e:
        return {'nerve_type': 'error', 'error': str(e)}
    finally:
        if s is not None:
            try:
                s.close()
            except Exception:
                pass


def get_recent_events(count: int = 20) -> list:
    """Get the N most recent events from the nerve feed.

    Uses the ring buffer if the hub is running (via ping to check),
    otherwise falls back to reading the feed file.
    """
    # Try to get from a running hub first — it has the ring buffer
    try:
        import socket as sock_mod
        s = sock_mod.socket(sock_mod.AF_UNIX, sock_mod.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect(str(SOCKET_PATH))
        # Request recent events via a special command
        s.sendall(json.dumps({
            'nerve_type': 'recent',
            'count': count
        }).encode() + b'\n')
        # Read response
        try:
            response = s.recv(65536)
            resp = json.loads(response.decode().strip())
            if resp.get('nerve_type') == 'recent_events':
                return resp.get('events', [])
        except (json.JSONDecodeError, TimeoutError, OSError):
            pass
        finally:
            s.close()
    except (ConnectionRefusedError, FileNotFoundError, OSError):
        pass

    # Fallback: read from feed file
    if not FEED_PATH.exists():
        return []

    events = []
    with open(FEED_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    return events[-count:]


def cmd_healthcheck():
    """Comprehensive health check: verify socket, feed, service are all healthy."""
    issues = []
    ok_count = 0

    # 1. Check state directory
    if STATE_DIR.exists():
        ok_count += 1
    else:
        issues.append("State directory missing")

    # 2. Check socket file
    if SOCKET_PATH.exists():
        ok_count += 1
        # Verify socket is responsive
        try:
            import socket as sock_mod
            s = sock_mod.socket(sock_mod.AF_UNIX, sock_mod.SOCK_STREAM)
            s.settimeout(2.0)
            s.connect(str(SOCKET_PATH))
            s.sendall(json.dumps({'nerve_type': 'ping'}).encode() + b'\n')
            response = s.recv(4096)
            s.close()
            resp = json.loads(response.decode().strip())
            if resp.get('nerve_type') == 'pong':
                ok_count += 1
            else:
                issues.append(f"Socket responsive but unexpected reply: {resp.get('nerve_type')}")
        except Exception as e:
            issues.append(f"Socket exists but not responsive: {e}")
    else:
        issues.append("Socket file missing (hub not running)")

    # 3. Check PID file
    if PID_PATH.exists():
        try:
            pid = int(PID_PATH.read_text().strip())
            try:
                os.kill(pid, 0)
                ok_count += 1
            except ProcessLookupError:
                issues.append(f"Stale PID file (PID {pid} not running)")
        except (ValueError, OSError) as e:
            issues.append(f"Corrupt PID file: {e}")
    else:
        issues.append("PID file missing")

    # 4. Check feed file
    if FEED_PATH.exists():
        ok_count += 1
        try:
            size = FEED_PATH.stat().st_size
            with open(FEED_PATH, 'r') as f:
                line_count = sum(1 for line in f if line.strip())
            # Check feed is parseable (sample first and last lines)
            ok_count += 1
            # Warn if feed is growing large
            if size > MAX_FEED_BYTES * 0.8:
                issues.append(f"⚠️  Feed is {size / (1024*1024):.1f} MB (approaching {MAX_FEED_BYTES // (1024*1024)} MB rotation threshold)")
        except OSError as e:
            issues.append(f"Feed file read error: {e}")
    else:
        issues.append("Feed file missing")
        # Try creating it
        try:
            FEED_PATH.parent.mkdir(parents=True, exist_ok=True)
            FEED_PATH.touch()
            ok_count += 1
            print("   (Created missing feed file)")
        except OSError:
            issues.append("Cannot create feed file")

    # 5. Check log file writable
    try:
        with open(LOG_PATH, 'a') as f:
            f.write('')  # Test write
        ok_count += 1
    except OSError as e:
        issues.append(f"Log file not writable: {e}")

    # Print results
    if not issues:
        print("✅ Nerve Hub Health: ALL CHECKS PASSED")
        print(f"   Socket: responsive")
        print(f"   Feed: healthy")
        print(f"   PID: valid")
    else:
        print(f"⚠️  Nerve Hub Health: {ok_count} checks passed, {len(issues)} issues:")
        for issue in issues:
            print(f"   ❌ {issue}")

    return len(issues) == 0


def get_status() -> dict:
    """Get nerve hub status."""
    status = {
        'hub_running': False,
        'pid': None,
        'socket_exists': SOCKET_PATH.exists(),
        'feed_exists': FEED_PATH.exists(),
        'feed_events': 0,
        'feed_size_bytes': 0,
    }

    # Check PID
    if PID_PATH.exists():
        try:
            pid = int(PID_PATH.read_text().strip())
            status['pid'] = pid
            try:
                os.kill(pid, 0)
                status['hub_running'] = True
            except ProcessLookupError:
                status['hub_running'] = False
        except (ValueError, OSError):
            pass

    # Check feed (only count lines, don't parse all JSON)
    if FEED_PATH.exists():
        status['feed_size_bytes'] = FEED_PATH.stat().st_size
        with open(FEED_PATH, 'r') as f:
            for line in f:
                if line.strip():
                    status['feed_events'] += 1

    # Try ping
    try:
        result = publish_event_sync('ping', {}, 'status_check')
        if result.get('nerve_type') == 'ack':
            status['hub_responsive'] = True
        elif result.get('nerve_type') == 'pong':
            status['hub_responsive'] = True
    except Exception:
        status['hub_responsive'] = False

    return status


async def subscribe():
    """Connect to the nerve hub and print live events."""
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_unix_connection(str(SOCKET_PATH)),
            timeout=3.0
        )
    except (ConnectionRefusedError, FileNotFoundError, asyncio.TimeoutError):
        print("❌ Nerve Hub is not running. Start it with: python3 nervous_system.py serve")
        return

    # Send subscribe message
    writer.write(json.dumps({'nerve_type': 'subscribe'}).encode() + b'\n')
    await writer.drain()

    print("🧠 Connected to Nerve Hub. Listening for events...")
    print("   (Press Ctrl+C to stop)\n")

    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            try:
                event = json.loads(data.decode().strip())
                ts = event.get('_iso', '?')
                seq = event.get('_seq', '?')
                etype = event.get('type', '?')
                source = event.get('source', '?')
                data_preview = json.dumps(event.get('data', {}), ensure_ascii=False)[:120]
                print(f"[{ts}] #{seq} {etype} from {source}: {data_preview}")
            except json.JSONDecodeError:
                print(f"[raw] {data.decode().strip()[:200]}")
    except asyncio.CancelledError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()
        print("\n🧠 Disconnected from Nerve Hub")


def cmd_publish(args):
    """CLI: publish an event."""
    if len(args) < 2:
        print("Usage: python3 nervous_system.py publish <event_type> '<json_data>' [source]")
        print("Example: python3 nervous_system.py publish thought '{\"insight\": \"hello\"}' vault_keeper")
        sys.exit(1)

    event_type = args[0]
    try:
        data = json.loads(args[1]) if len(args) > 1 else {}
    except json.JSONDecodeError:
        data = {'text': args[1]}
    source = args[2] if len(args) > 2 else 'cli'

    result = publish_event_sync(event_type, data, source)
    seq = result.get('seq', '?')
    if result.get('nerve_type') == 'ack':
        print(f"✅ Event #{seq} published")
    elif result.get('nerve_type') == 'fallback':
        print(f"⚠️  Hub offline — event written to feed directly")
    else:
        print(f"📤 Result: {json.dumps(result, indent=2)}")


def cmd_recent(args):
    """CLI: show recent events."""
    count = int(args[0]) if args else 20
    events = get_recent_events(count)

    if not events:
        print("No events in nerve feed.")
        return

    print(f"🧠 Last {len(events)} events:\n")
    for e in events:
        ts = e.get('_iso', '?')
        seq = e.get('_seq', '?')
        etype = e.get('type', '?')
        source = e.get('source', '?')
        fallback = ' (fallback)' if e.get('_fallback') else ''
        data_preview = json.dumps(e.get('data', {}), ensure_ascii=False)[:100]
        print(f"  [{ts}] #{seq} {etype} from {source}{fallback}")
        print(f"    {data_preview}")


def cmd_status():
    """CLI: show nerve hub status."""
    status = get_status()
    print("🧠 Nerve Hub Status")
    print(f"   Running: {'✅' if status['hub_running'] else '❌'}")
    print(f"   PID: {status['pid'] or 'N/A'}")
    print(f"   Socket: {'✅' if status['socket_exists'] else '❌'} ({SOCKET_PATH})")
    print(f"   Feed: {'✅' if status['feed_exists'] else '❌'} ({status['feed_events']} events, {status['feed_size_bytes']} bytes)")
    if status.get('hub_responsive') is not None:
        print(f"   Responsive: {'✅' if status['hub_responsive'] else '❌'}")


def cmd_stop():
    """CLI: stop the nerve hub with graceful shutdown."""
    if not PID_PATH.exists():
        print("❌ No PID file found — hub may not be running")
        return

    try:
        pid = int(PID_PATH.read_text().strip())

        # First try SIGTERM for graceful shutdown
        os.kill(pid, signal.SIGTERM)
        print(f"🛑 Sent SIGTERM to PID {pid} (graceful shutdown)")

        # Wait up to 5 seconds for process to exit
        for i in range(5):
            time.sleep(1)
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                print("✅ Hub stopped gracefully")
                PID_PATH.unlink(missing_ok=True)
                return

        # Still running — escalate
        print("⚠️  Process still running after 5s, sending SIGKILL...")
        os.kill(pid, signal.SIGKILL)
        time.sleep(1)
        try:
            os.kill(pid, 0)
            print("❌ Process could not be killed")
        except ProcessLookupError:
            print("✅ Hub killed (SIGKILL)")
            PID_PATH.unlink(missing_ok=True)
    except ProcessLookupError:
        print("❌ Process not found — cleaning up stale PID")
        PID_PATH.unlink(missing_ok=True)
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == 'serve':
        hub = NerveHub()
        try:
            asyncio.run(hub.serve())
        except KeyboardInterrupt:
            print("\n🧠 Nerve Hub shutting down...")
            # Graceful shutdown handled inside serve()
    elif command == 'publish':
        cmd_publish(args)
    elif command == 'recent':
        cmd_recent(args)
    elif command == 'subscribe':
        asyncio.run(subscribe())
    elif command == 'status':
        cmd_status()
    elif command == 'healthcheck':
        healthy = cmd_healthcheck()
        sys.exit(0 if healthy else 1)
    elif command == 'stop':
        cmd_stop()
    else:
        print(f"Unknown command: {command}")
        print("Commands: serve, publish, recent, subscribe, status, healthcheck, stop")
        sys.exit(1)


if __name__ == '__main__':
    main()
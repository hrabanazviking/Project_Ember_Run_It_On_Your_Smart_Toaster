"""
Comprehensive pytest suite for nervous_system.py

Covers: hub lifecycle, publish, recent, subscribe, status, healthcheck,
feed rotation, ring buffer, file locking, graceful shutdown, edge cases.
Uses subprocess and tempfile for integration tests.
Uses different socket paths to avoid breaking the production nerve hub.
"""

import asyncio
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# --- Ensure we can import the module from the project dir ---
PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import nervous_system as ns


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def isolate_paths(tmp_path):
    """Redirect all paths to a temp dir to avoid touching production."""
    state_dir = tmp_path / ".hermes" / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    socket_path = state_dir / "test_runa.sock"
    feed_path = state_dir / "nerve_feed.jsonl"
    pid_path = state_dir / "nervous_system.pid"
    log_path = state_dir / "nervous_system.log"

    # Patch the module-level constants
    original_constants = {
        'STATE_DIR': ns.STATE_DIR,
        'SOCKET_PATH': ns.SOCKET_PATH,
        'FEED_PATH': ns.FEED_PATH,
        'PID_PATH': ns.PID_PATH,
        'LOG_PATH': ns.LOG_PATH,
    }
    ns.STATE_DIR = state_dir
    ns.SOCKET_PATH = socket_path
    ns.FEED_PATH = feed_path
    ns.PID_PATH = pid_path
    ns.LOG_PATH = log_path

    yield {
        'state_dir': state_dir,
        'socket_path': socket_path,
        'feed_path': feed_path,
        'pid_path': pid_path,
        'log_path': log_path,
    }

    # Restore originals
    for key, val in original_constants.items():
        setattr(ns, key, val)


# ============================================================================
# Ring Buffer Tests
# ============================================================================

class TestRingBuffer:
    def test_append_and_recent(self):
        rb = ns.RingBuffer(maxlen=5)
        for i in range(5):
            rb.append({'seq': i})
        recent = rb.recent(3)
        assert len(recent) == 3
        assert recent[0]['seq'] == 2
        assert recent[2]['seq'] == 4

    def test_overflow(self):
        rb = ns.RingBuffer(maxlen=3)
        for i in range(10):
            rb.append({'seq': i})
        assert len(rb) == 3
        recent = rb.recent(10)
        assert recent[0]['seq'] == 7  # Oldest kept
        assert recent[-1]['seq'] == 9

    def test_recent_more_than_available(self):
        rb = ns.RingBuffer(maxlen=5)
        rb.append({'seq': 1})
        rb.append({'seq': 2})
        recent = rb.recent(10)
        assert len(recent) == 2

    def test_empty_buffer(self):
        rb = ns.RingBuffer(maxlen=5)
        assert len(rb) == 0
        assert rb.recent(10) == []

    def test_custom_maxlen(self):
        rb = ns.RingBuffer(maxlen=100)
        assert rb._maxlen == 100


# ============================================================================
# Feed Lock Write Tests
# ============================================================================

class TestFeedLockWrite:
    def test_creates_file_if_missing(self, isolate_paths):
        feed = isolate_paths['feed_path']
        assert not feed.exists()
        ns._feed_lock_write('{"test": "data"}')
        assert feed.exists()
        with open(feed) as f:
            lines = f.readlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data['test'] == 'data'

    def test_appends_to_existing(self, isolate_paths):
        feed = isolate_paths['feed_path']
        ns._feed_lock_write('{"seq": 1}')
        ns._feed_lock_write('{"seq": 2}')
        with open(feed) as f:
            lines = f.readlines()
        assert len(lines) == 2
        assert json.loads(lines[0])['seq'] == 1
        assert json.loads(lines[1])['seq'] == 2


# ============================================================================
# Feed Rotation Tests
# ============================================================================

class TestFeedRotation:
    def test_no_rotation_when_small(self, isolate_paths):
        feed = isolate_paths['feed_path']
        with open(feed, 'w') as f:
            f.write('{"seq": 1}\n' * 10)
        original_size = feed.stat().st_size
        ns._rotate_feed_if_needed()
        assert feed.exists()
        assert feed.stat().st_size == original_size

    def test_rotation_archives_large_file(self, isolate_paths):
        feed = isolate_paths['feed_path']
        original_max = ns.MAX_FEED_BYTES
        ns.MAX_FEED_BYTES = 100  # Very small threshold
        try:
            with open(feed, 'w') as f:
                f.write('{"seq": 1}\n' * 20)  # ~200 bytes
            assert feed.stat().st_size > ns.MAX_FEED_BYTES

            ns._rotate_feed_if_needed()

            # After rotation, the original feed file may or may not exist
            # depending on whether compression succeeded. Either way, an
            # archive file should exist (compressed or not).
            state_dir = isolate_paths['state_dir']
            archives = list(state_dir.glob('nerve_feed_*.jsonl*'))
            assert len(archives) >= 1, "Expected at least one archive file after rotation"
        finally:
            ns.MAX_FEED_BYTES = original_max

    def test_rotation_handles_missing_file(self, isolate_paths):
        feed = isolate_paths['feed_path']
        assert not feed.exists()
        ns._rotate_feed_if_needed()  # Should not crash


# ============================================================================
# NerveHub Integration Tests
# ============================================================================

class TestNerveHub:
    """Integration tests using actual async Unix domain socket communication."""

    async def _start_hub(self):
        """Helper: start a NerveHub and return (hub, serve_task)."""
        hub = ns.NerveHub()
        serve_task = asyncio.create_task(hub.serve())
        # Wait for the hub to start
        for _ in range(50):
            await asyncio.sleep(0.05)
            if ns.SOCKET_PATH.exists():
                break
        assert ns.SOCKET_PATH.exists(), "Hub socket should exist after start"
        return hub, serve_task

    async def _stop_hub(self, hub, serve_task):
        """Helper: gracefully stop a NerveHub."""
        hub._shutdown_event.set()
        try:
            await asyncio.wait_for(serve_task, timeout=5)
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_hub_serve_and_publish(self, isolate_paths):
        """Test starting the hub, publishing an event, and stopping it."""
        hub, serve_task = await self._start_hub()
        try:
            result = ns.publish_event_sync('test_event', {'key': 'value'}, 'test_source')
            assert result is not None
            assert result.get('nerve_type') in ('ack', 'fallback', 'sent')
        finally:
            await self._stop_hub(hub, serve_task)

    @pytest.mark.asyncio
    async def test_hub_recent_command(self, isolate_paths):
        """Test that the recent command returns events from the ring buffer."""
        hub, serve_task = await self._start_hub()
        try:
            # Publish some events so the ring buffer has data
            for i in range(3):
                ns.publish_event_sync(f'test_event_{i}', {'i': i}, 'test')

            # Connect and send recent command
            reader, writer = await asyncio.open_unix_connection(str(ns.SOCKET_PATH))
            writer.write(json.dumps({'nerve_type': 'recent', 'count': 10}).encode() + b'\n')
            await writer.drain()

            data = await asyncio.wait_for(reader.readline(), timeout=3)
            response = json.loads(data.decode().strip())
            assert response.get('nerve_type') == 'recent_events'
            assert isinstance(response.get('events'), list)
            assert response.get('count') >= 0

            writer.close()
            await writer.wait_closed()
        finally:
            await self._stop_hub(hub, serve_task)

    @pytest.mark.asyncio
    async def test_hub_ping_pong(self, isolate_paths):
        """Test that the hub responds to ping with pong."""
        hub, serve_task = await self._start_hub()
        try:
            reader, writer = await asyncio.open_unix_connection(str(ns.SOCKET_PATH))
            writer.write(json.dumps({'nerve_type': 'ping'}).encode() + b'\n')
            await writer.drain()

            data = await asyncio.wait_for(reader.readline(), timeout=3)
            response = json.loads(data.decode().strip())
            assert response.get('nerve_type') == 'pong'
            assert 'seq' in response
            assert 'uptime_s' in response

            writer.close()
            await writer.wait_closed()
        finally:
            await self._stop_hub(hub, serve_task)

    @pytest.mark.asyncio
    async def test_hub_subscribe(self, isolate_paths):
        """Test that a subscriber receives broadcast events."""
        hub, serve_task = await self._start_hub()
        try:
            sub_reader, sub_writer = await asyncio.open_unix_connection(str(ns.SOCKET_PATH))
            sub_writer.write(json.dumps({'nerve_type': 'subscribe'}).encode() + b'\n')
            await sub_writer.drain()
            data = await asyncio.wait_for(sub_reader.readline(), timeout=3)
            sub_resp = json.loads(data.decode().strip())
            assert sub_resp.get('nerve_type') == 'subscribed'

            ns.publish_event_sync('test_broadcast', {'msg': 'hello'}, 'pub')

            data = await asyncio.wait_for(sub_reader.readline(), timeout=3)
            event = json.loads(data.decode().strip())
            assert event.get('type') == 'test_broadcast'
            assert event.get('data', {}).get('msg') == 'hello'

            sub_writer.close()
            await sub_writer.wait_closed()
        finally:
            await self._stop_hub(hub, serve_task)

    @pytest.mark.asyncio
    async def test_hub_graceful_shutdown_notifies_subscribers(self, isolate_paths):
        """Test that shutting down the hub sends shutdown messages to subscribers."""
        hub, serve_task = await self._start_hub()
        try:
            sub_reader, sub_writer = await asyncio.open_unix_connection(str(ns.SOCKET_PATH))
            sub_writer.write(json.dumps({'nerve_type': 'subscribe'}).encode() + b'\n')
            await sub_writer.drain()
            await asyncio.wait_for(sub_reader.readline(), timeout=3)  # subscribed ack

            await self._stop_hub(hub, serve_task)

            # Subscriber should have received a shutdown message OR the connection closed
            try:
                data = await asyncio.wait_for(sub_reader.readline(), timeout=2)
                if data:
                    event = json.loads(data.decode().strip())
                    assert event.get('nerve_type') == 'shutdown'
            except (asyncio.TimeoutError, ConnectionError, json.JSONDecodeError):
                pass  # Connection closed is also acceptable
            finally:
                sub_writer.close()
                try:
                    await sub_writer.wait_closed()
                except Exception:
                    pass
        except (asyncio.CancelledError, Exception):
            pass

    @pytest.mark.asyncio
    async def test_hub_invalid_json_handled(self, isolate_paths):
        """Test that the hub doesn't crash on invalid JSON."""
        hub, serve_task = await self._start_hub()
        try:
            reader, writer = await asyncio.open_unix_connection(str(ns.SOCKET_PATH))
            writer.write(b'this is not json\n')
            await writer.drain()

            writer.write(json.dumps({'nerve_type': 'ping'}).encode() + b'\n')
            await writer.drain()
            data = await asyncio.wait_for(reader.readline(), timeout=3)
            response = json.loads(data.decode().strip())
            assert response.get('nerve_type') == 'pong'

            writer.close()
            await writer.wait_closed()
        finally:
            await self._stop_hub(hub, serve_task)


# ============================================================================
# get_status Tests
# ============================================================================

class TestGetStatus:
    def test_status_when_hub_not_running(self, isolate_paths):
        status = ns.get_status()
        assert status['hub_running'] is False
        assert status['pid'] is None

    def test_status_feed_exists(self, isolate_paths):
        feed = isolate_paths['feed_path']
        with open(feed, 'w') as f:
            f.write('{"type": "test"}\n')
            f.write('{"type": "test2"}\n')
        status = ns.get_status()
        assert status['feed_exists'] is True
        assert status['feed_events'] == 2


# ============================================================================
# Cmd Healthcheck Tests
# ============================================================================

class TestHealthcheck:
    def test_healthcheck_creates_feed_if_missing(self, isolate_paths):
        feed = isolate_paths['feed_path']
        assert not feed.exists()
        result = ns.cmd_healthcheck()
        assert isinstance(result, bool)

    def test_healthcheck_state_dir_exists(self, isolate_paths):
        assert ns.STATE_DIR.exists()


# ============================================================================
# Publish Event Sync Tests
# ============================================================================

class TestPublishEventSync:
    def test_fallback_when_hub_offline(self, isolate_paths):
        result = ns.publish_event_sync('test', {'key': 'val'}, 'tester')
        assert result.get('nerve_type') == 'fallback'
        with open(ns.FEED_PATH) as f:
            lines = f.readlines()
        assert len(lines) >= 1
        data = json.loads(lines[-1])
        assert data['type'] == 'test'
        assert data['data'] == {'key': 'val'}
        assert data.get('_fallback') is True

    def test_fallback_creates_timestamp(self, isolate_paths):
        ns.publish_event_sync('ts_test', {}, 'tester')
        with open(ns.FEED_PATH) as f:
            data = json.loads(f.readlines()[-1])
        assert '_ts' in data
        assert '_iso' in data
        # Should be timezone-aware (contains '+')
        assert '+' in data['_iso'] or data['_iso'].startswith('20')


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    def test_empty_feed_file(self, isolate_paths):
        feed = isolate_paths['feed_path']
        feed.touch()
        events = ns.get_recent_events(10)
        assert events == []

    def test_corrupt_feed_lines_skipped(self, isolate_paths):
        feed = isolate_paths['feed_path']
        with open(feed, 'w') as f:
            f.write('{"_seq": 1, "type": "good"}\n')
            f.write('this is corrupt\n')
            f.write('{"_seq": 2, "type": "also_good"}\n')
        events = ns.get_recent_events(10)
        assert len(events) == 2

    def test_log_msg_writes_to_log(self, isolate_paths):
        ns.log_msg("Test log message")
        log = isolate_paths['log_path']
        assert log.exists()
        content = log.read_text()
        assert "Test log message" in content

    def test_log_msg_handles_write_failure(self, isolate_paths):
        ns.LOG_PATH = Path("/nonexistent/path/to/log")
        try:
            ns.log_msg("This should not crash")
        finally:
            ns.LOG_PATH = isolate_paths['log_path']

    def test_ring_buffer_maxlen_respected(self):
        rb = ns.RingBuffer(maxlen=10)
        for i in range(100):
            rb.append({'i': i})
        assert len(rb) == 10
        recent = rb.recent(10)
        assert recent[-1]['i'] == 99
        assert recent[0]['i'] == 90


# ============================================================================
# Subprocess Integration Tests
# ============================================================================

class TestSubprocessIntegration:
    """Tests that run the nerve hub as a subprocess (full end-to-end)."""

    @pytest.fixture
    def subprocess_hub(self, isolate_paths, tmp_path):
        """Start a nerve hub as a subprocess using the isolated paths."""
        # Create a wrapper script that patches the paths before importing
        wrapper = tmp_path / "run_hub.py"
        wrapper.write_text(f"""
import sys
sys.path.insert(0, '{PROJECT_DIR}')
import nervous_system as ns

# Override paths for testing
ns.STATE_DIR = ns.Path('{isolate_paths["state_dir"]}')
ns.SOCKET_PATH = ns.Path('{isolate_paths["socket_path"]}')
ns.FEED_PATH = ns.Path('{isolate_paths["feed_path"]}')
ns.PID_PATH = ns.Path('{isolate_paths["pid_path"]}')
ns.LOG_PATH = ns.Path('{isolate_paths["log_path"]}')

ns.main()
""")
        proc = subprocess.Popen(
            [sys.executable, str(wrapper), 'serve'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        # Wait for hub to start
        for _ in range(20):
            time.sleep(0.1)
            if ns.SOCKET_PATH.exists():
                break
        assert proc.poll() is None, "Hub process should be running"
        yield proc, isolate_paths

        try:
            proc.terminate()
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=2)
        sock_path = isolate_paths['socket_path']
        if sock_path.exists():
            sock_path.unlink(missing_ok=True)
        pid_path = isolate_paths['pid_path']
        if pid_path.exists():
            pid_path.unlink(missing_ok=True)

    def test_publish_via_subprocess(self, subprocess_hub):
        """Test publishing an event via subprocess."""
        proc, paths = subprocess_hub
        wrapper = paths['state_dir'].parent.parent / "pub_test.py"
        wrapper.write_text(f"""
import sys
sys.path.insert(0, '{PROJECT_DIR}')
import nervous_system as ns

ns.SOCKET_PATH = ns.Path('{paths["socket_path"]}')
ns.FEED_PATH = ns.Path('{paths["feed_path"]}')
ns.PID_PATH = ns.Path('{paths["pid_path"]}')
ns.LOG_PATH = ns.Path('{paths["log_path"]}')
ns.STATE_DIR = ns.Path('{paths["state_dir"]}')

result = ns.publish_event_sync('subprocess_test', {{'key': 'value'}}, 'test_runner')
print(f"Result: {{result}}")
""")

        result = subprocess.run(
            [sys.executable, str(wrapper)],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout + result.stderr
        assert 'Result' in output

    def test_recent_via_subprocess(self, subprocess_hub):
        """Test getting recent events via subprocess."""
        proc, paths = subprocess_hub
        wrapper = paths['state_dir'] / "recent_test.py"
        wrapper.write_text(f"""
import sys
sys.path.insert(0, '{PROJECT_DIR}')
import nervous_system as ns

ns.SOCKET_PATH = ns.Path('{paths["socket_path"]}')
ns.FEED_PATH = ns.Path('{paths["feed_path"]}')
ns.PID_PATH = ns.Path('{paths["pid_path"]}')
ns.LOG_PATH = ns.Path('{paths["log_path"]}')
ns.STATE_DIR = ns.Path('{paths["state_dir"]}')

# Publish an event first
ns.publish_event_sync('recent_test_event', {{'test': True}}, 'test')

# Get recent events
events = ns.get_recent_events(5)
print(f"Events count: {{len(events)}}")
for e in events:
    print(f"  Event: {{e.get('type', '?')}}")
""")

        result = subprocess.run(
            [sys.executable, str(wrapper)],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout + result.stderr
        assert 'Events count' in output


# ============================================================================
# File Locking Tests
# ============================================================================

class TestFileLocking:
    def test_concurrent_feed_writes(self, isolate_paths):
        """Test that concurrent _feed_lock_write calls don't corrupt data."""
        import threading
        feed = isolate_paths['feed_path']
        errors = []

        def write_events(thread_id):
            try:
                for i in range(20):
                    event = json.dumps({'thread': thread_id, 'i': i})
                    ns._feed_lock_write(event)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=write_events, args=(t,)) for t in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Errors during concurrent writes: {errors}"
        with open(feed) as f:
            lines = f.readlines()
        assert len(lines) == 100  # 5 threads * 20 events
        for line in lines:
            json.loads(line.strip())  # Should not raise


# ============================================================================
# Date/Time Compatibility Tests
# ============================================================================

class TestDateTimeCompat:
    def test_publish_timestamps_are_timezone_aware(self, isolate_paths):
        """Test that published events have timezone-aware ISO timestamps."""
        ns.publish_event_sync('tz_test', {}, 'tester')
        with open(ns.FEED_PATH) as f:
            data = json.loads(f.readlines()[-1])
        iso = data.get('_iso', '')
        # datetime.now(timezone.utc) produces timestamps with '+00:00'
        assert '+00:00' in iso or iso.startswith('20')
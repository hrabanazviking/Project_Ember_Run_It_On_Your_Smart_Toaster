"""
Comprehensive pytest suite for conversation_logger.py

Covers: conversation logging, state snapshots, nerve firing,
        session lifecycle, edge cases.
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import conversation_logger as cl


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def isolate_paths(tmp_path):
    """Redirect all paths to a temp dir to avoid touching production."""
    state_dir = tmp_path / ".hermes" / "state"
    conv_dir = state_dir / "conversations"
    state_dir.mkdir(parents=True, exist_ok=True)
    conv_dir.mkdir(parents=True, exist_ok=True)

    current_file = state_dir / "current.json"
    conv_log = state_dir / "conversation_log.jsonl"

    original_constants = {
        'STATE_DIR': cl.STATE_DIR,
        'CONV_DIR': cl.CONV_DIR,
        'CURRENT_FILE': cl.CURRENT_FILE,
        'CONV_LOG': cl.CONV_LOG,
    }
    cl.STATE_DIR = state_dir
    cl.CONV_DIR = conv_dir
    cl.CURRENT_FILE = current_file
    cl.CONV_LOG = conv_log

    yield {
        'state_dir': state_dir,
        'conv_dir': conv_dir,
        'current_file': current_file,
        'conv_log': conv_log,
    }

    for key, val in original_constants.items():
        setattr(cl, key, val)


def make_ns(command, **kwargs):
    """Helper to create an argparse Namespace for conversation_logger."""
    import argparse
    return argparse.Namespace(command=command, **kwargs)


# ============================================================================
# Session Lifecycle Tests
# ============================================================================

class TestSessionLifecycle:
    def test_start_session(self, isolate_paths):
        """Test starting a new session."""
        args = make_ns('start',
                       session='test-session-1',
                       summary='Testing session start',
                       model='test-model',
                       platform='pytest')
        entry = cl.cmd_start(args)
        assert entry['entry_type'] == 'start'
        assert entry['session_id'] == 'test-session-1'
        assert entry['summary'] == 'Testing session start'

        # Check current.json was created
        with open(isolate_paths['current_file']) as f:
            current = json.load(f)
        assert current['session_id'] == 'test-session-1'
        assert current['status'] == 'active'

    def test_log_event(self, isolate_paths):
        """Test logging an event."""
        # Start session first
        args = make_ns('start', session='test-session-2', summary='Event test',
                       model='test', platform='pytest')
        cl.cmd_start(args)

        # Log an event
        event_args = make_ns('event', session='test-session-2',
                             type='decision', content='Made a decision')
        entry = cl.cmd_event(event_args)
        assert entry['entry_type'] == 'event'
        assert entry['event_type'] == 'decision'
        assert entry['content'] == 'Made a decision'

    def test_update_state(self, isolate_paths):
        """Test updating session state."""
        # Start session
        args = make_ns('start', session='test-session-3', summary='Update test',
                       model='test', platform='pytest')
        cl.cmd_start(args)

        # Update state
        update_args = make_ns('update', session='test-session-3',
                             next=['Do thing A', 'Do thing B'],
                             blockers=['Stuck on X'],
                             projects=['Verdandi'],
                             mood='focused',
                             summary='')
        entry = cl.cmd_update(update_args)
        assert entry['entry_type'] == 'update'

        # Verify current.json was updated
        with open(isolate_paths['current_file']) as f:
            current = json.load(f)
        assert 'Do thing A' in current['next_actions']
        assert 'Stuck on X' in current['blockers']
        assert 'Verdandi' in current['projects_touched']
        assert current['mood'] == 'focused'

    def test_end_session(self, isolate_paths):
        """Test ending a session."""
        # Start session
        args = make_ns('start', session='test-session-4', summary='End test',
                       model='test', platform='pytest')
        cl.cmd_start(args)

        # End session
        end_args = make_ns('end', session='test-session-4',
                          summary='Finished testing', duration=0)
        entry = cl.cmd_end(end_args)
        assert entry['entry_type'] == 'end'
        assert entry['summary'] == 'Finished testing'

        # Verify current.json shows closed
        with open(isolate_paths['current_file']) as f:
            current = json.load(f)
        assert current['status'] == 'closed'

    def test_full_session_lifecycle(self, isolate_paths):
        """Test complete session lifecycle: start → events → update → end."""
        # Start
        start_args = make_ns('start', session='lifecycle-test',
                            summary='Full lifecycle', model='test', platform='pytest')
        cl.cmd_start(start_args)

        # Events
        for i, (etype, content) in enumerate([
            ('decision', 'Decision 1'),
            ('file_changed', 'test_file.py'),
            ('learned', 'Learned something'),
            ('milestone', 'Hit milestone'),
        ]):
            event_args = make_ns('event', session='lifecycle-test',
                               type=etype, content=content)
            cl.cmd_event(event_args)

        # Update
        update_args = make_ns('update', session='lifecycle-test',
                            next=['Next step'], blockers=['A blocker'],
                            projects=['Verdandi'], mood='productive', summary='')
        cl.cmd_update(update_args)

        # End
        end_args = make_ns('end', session='lifecycle-test',
                          summary='Lifecycle complete', duration=30)
        cl.cmd_end(end_args)

        # Verify in JSONL log
        entries = cl._read_all_entries()
        session_entries = [e for e in entries if e.get('session_id') == 'lifecycle-test']
        assert len(session_entries) >= 6  # start + 4 events + update + end
        entry_types = [e['entry_type'] for e in session_entries]
        assert 'start' in entry_types
        assert 'event' in entry_types
        assert 'update' in entry_types
        assert 'end' in entry_types


# ============================================================================
# State Snapshot Tests
# ============================================================================

class TestStateSnapshots:
    def test_current_json_accumulates_decisions(self, isolate_paths):
        """Test that decisions accumulate in current.json."""
        start_args = make_ns('start', session='accum-test',
                           summary='Accumulation test', model='test', platform='pytest')
        cl.cmd_start(start_args)

        # Log two decisions
        for content in ['Decision A', 'Decision B']:
            event_args = make_ns('event', session='accum-test',
                               type='decision', content=content)
            cl.cmd_event(event_args)

        with open(isolate_paths['current_file']) as f:
            current = json.load(f)
        assert 'Decision A' in current['decisions']
        assert 'Decision B' in current['decisions']

    def test_duplicate_decisions_not_added(self, isolate_paths):
        """Test that duplicate content is not re-added to lists."""
        start_args = make_ns('start', session='dedup-test',
                           summary='Dedup test', model='test', platform='pytest')
        cl.cmd_start(start_args)

        # Log same decision twice
        event_args = make_ns('event', session='dedup-test',
                           type='decision', content='Same decision')
        cl.cmd_event(event_args)
        cl.cmd_event(event_args)

        with open(isolate_paths['current_file']) as f:
            current = json.load(f)
        assert current['decisions'].count('Same decision') == 1

    def test_blocker_resolved_removes_from_list(self, isolate_paths):
        """Test that blocker_resolved removes the blocker from current.json."""
        start_args = make_ns('start', session='blocker-test',
                           summary='Blocker test', model='test', platform='pytest')
        cl.cmd_start(start_args)

        # Add blocker
        event_args = make_ns('event', session='blocker-test',
                           type='blocker', content='Stuck on bug X')
        cl.cmd_event(event_args)

        # Resolve blocker
        event_args2 = make_ns('event', session='blocker-test',
                             type='blocker_resolved', content='Stuck on bug X')
        cl.cmd_event(event_args2)

        with open(isolate_paths['current_file']) as f:
            current = json.load(f)
        assert 'Stuck on bug X' not in current.get('blockers', [])

    def test_mood_shift_updates_mood(self, isolate_paths):
        """Test that mood_shift events update the mood field."""
        start_args = make_ns('start', session='mood-test',
                           summary='Mood test', model='test', platform='pytest')
        cl.cmd_start(start_args)

        event_args = make_ns('event', session='mood-test',
                           type='mood_shift', content='excited')
        cl.cmd_event(event_args)

        with open(isolate_paths['current_file']) as f:
            current = json.load(f)
        assert current['mood'] == 'excited'

    def test_end_session_calcuates_duration(self, isolate_paths):
        """Test that ending a session auto-calculates duration if not provided."""
        start_args = make_ns('start', session='duration-test',
                           summary='Duration test', model='test', platform='pytest')
        entry = cl.cmd_start(start_args)

        # End with duration=0 (auto-calculate)
        end_args = make_ns('end', session='duration-test',
                          summary='Done', duration=0)
        cl.cmd_end(end_args)

        with open(isolate_paths['current_file']) as f:
            current = json.load(f)
        # Duration should be calculated (0 if instant, otherwise > 0)
        assert 'duration_minutes' in current


# ============================================================================
# Nerve Firing Tests
# ============================================================================

class TestNerveFiring:
    def test_nerve_fire_does_not_crash_on_failure(self, isolate_paths):
        """Test that _nerve_fire handles failures gracefully."""
        # Should not raise any exceptions even if the nerve hub doesn't exist
        entry = {
            'entry_type': 'event',
            'session_id': 'test-session',
            'timestamp': '2026-05-10T00:00:00+00:00',
        }
        # This should silently succeed or fail without crashing
        cl._nerve_fire(entry)

    def test_nerve_fire_catches_exceptions(self, isolate_paths):
        """Test that _nerve_fire catches exceptions from the nervous_system module."""
        # Force an import error
        original_nerve_path = cl._nerve_module_path
        cl._nerve_module_path = None
        cl._nerve_module = None
        try:
            # Point to a non-existent path
            with patch.object(cl, 'STATE_DIR', Path('/nonexistent/path')):
                entry = {'entry_type': 'event', 'session_id': 'test'}
                cl._nerve_fire(entry)  # Should not crash
        finally:
            cl._nerve_module_path = original_nerve_path

    def test_append_calls_nerve_fire(self, isolate_paths):
        """Test that _append calls _nerve_fire."""
        call_count = 0
        original_fire = cl._nerve_fire

        def mock_fire(entry):
            nonlocal call_count
            call_count += 1

        cl._nerve_fire = mock_fire
        try:
            args = make_ns('start', session='nerve-test',
                          summary='Nerve fire test', model='test', platform='pytest')
            cl.cmd_start(args)
            assert call_count >= 1, "Expected _nerve_fire to be called at least once"
        finally:
            cl._nerve_fire = original_fire


# ============================================================================
# Entry Type Validation Tests
# ============================================================================

class TestEventTypeValidation:
    def test_valid_event_types(self, isolate_paths):
        """Test that all valid event types are accepted."""
        start_args = make_ns('start', session='types-test',
                           summary='Type validation', model='test', platform='pytest')
        cl.cmd_start(start_args)

        for etype in cl.EVENT_TYPES:
            event_args = make_ns('event', session='types-test',
                               type=etype, content=f'Testing {etype}')
            entry = cl.cmd_event(event_args)
            assert entry['event_type'] == etype

    def test_invalid_event_type_exits(self, isolate_paths):
        """Test that invalid event types cause sys.exit."""
        with pytest.raises(SystemExit):
            event_args = make_ns('event', session='invalid-test',
                               type='invalid_type', content='Bad type')
            cl.cmd_event(event_args)


# ============================================================================
# JSONL Log Integrity Tests
# ============================================================================

class TestJSONLLogIntegrity:
    def test_append_creates_jsonl(self, isolate_paths):
        """Test that _append creates valid JSONL."""
        entry = {
            'entry_type': 'start',
            'session_id': 'jsonl-test',
            'timestamp': '2026-05-10T12:00:00+00:00',
        }
        cl._append(entry)

        with open(isolate_paths['conv_log']) as f:
            lines = f.readlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data['session_id'] == 'jsonl-test'

    def test_multiple_appends_are_separate_lines(self, isolate_paths):
        """Test that multiple appends produce separate lines."""
        for i in range(5):
            cl._append({'entry_type': 'event', 'session_id': 'multi-test', 'i': i})

        with open(isolate_paths['conv_log']) as f:
            lines = f.readlines()
        assert len(lines) == 5
        for line in lines:
            data = json.loads(line.strip())
            assert data['session_id'] == 'multi-test'

    def test_special_characters_in_content(self, isolate_paths):
        """Test that special characters are handled in JSON content."""
        start_args = make_ns('start', session='special-chars-test',
                           summary='Testing special chars: "quotes" and \\backslashes',
                           model='test', platform='pytest')
        entry = cl.cmd_start(start_args)
        # Verify it can be round-tripped through JSON
        with open(isolate_paths['conv_log']) as f:
            data = json.loads(f.readlines()[-1])
        # The backslash handling in JSON ensures round-trip safety
        assert 'special-chars-test' in data['session_id']


# ============================================================================
# Query Functions Tests
# ============================================================================

class TestQueryFunctions:
    def test_get_entries_for_session(self, isolate_paths):
        """Test retrieving entries for a specific session."""
        # Create multiple sessions
        for sid in ['session-A', 'session-B']:
            args = make_ns('start', session=sid, summary=f'Test {sid}',
                         model='test', platform='pytest')
            cl.cmd_start(args)

        entries_a = cl._get_entries_for_session('session-A')
        entries_b = cl._get_entries_for_session('session-B')
        assert all(e['session_id'] == 'session-A' for e in entries_a)
        assert all(e['session_id'] == 'session-B' for e in entries_b)

    def test_get_recent_sessions(self, isolate_paths):
        """Test retrieving recent sessions."""
        for i in range(5):
            args = make_ns('start', session=f'recent-test-{i}',
                         summary=f'Session {i}', model='test', platform='pytest')
            cl.cmd_start(args)

        recent = cl._get_recent_sessions(3)
        assert len(recent) <= 3
        # Should get unique session IDs
        sids = [e.get('session_id') for e in recent]
        assert len(sids) == len(set(sids))

    def test_get_current_state(self, isolate_paths):
        """Test reading current state."""
        start_args = make_ns('start', session='state-test',
                           summary='State test', model='test', platform='pytest')
        cl.cmd_start(start_args)

        state = cl.get_current_state()
        assert state is not None
        assert state['session_id'] == 'state-test'
        assert state['status'] == 'active'

    def test_get_current_state_missing_file(self, isolate_paths):
        """Test get_current_state with missing file."""
        state = cl.get_current_state()
        assert state is None

    def test_get_current_state_corrupt_file(self, isolate_paths):
        """Test get_current_state with corrupt JSON."""
        with open(isolate_paths['current_file'], 'w') as f:
            f.write('{corrupt json')
        state = cl.get_current_state()
        assert state is None

    def test_read_all_entries_with_corrupt_lines(self, isolate_paths):
        """Test that corrupt lines in JSONL are skipped."""
        with open(isolate_paths['conv_log'], 'w') as f:
            f.write('{"entry_type": "start", "session_id": "good-1"}\n')
            f.write('corrupt line\n')
            f.write('{"entry_type": "start", "session_id": "good-2"}\n')
        entries = cl._read_all_entries()
        assert len(entries) == 2
        assert entries[0]['session_id'] == 'good-1'
        assert entries[1]['session_id'] == 'good-2'


# ============================================================================
# Context Generation Tests
# ============================================================================

class TestContextGeneration:
    def test_get_context_for_cron(self, isolate_paths):
        """Test that context generation doesn't crash."""
        # Start a session
        args = make_ns('start', session='context-test',
                      summary='Context generation test', model='test', platform='pytest')
        cl.cmd_start(args)

        context = cl.get_context_for_cron(max_sessions=5)
        assert isinstance(context, str)
        assert 'RUNA SESSION CONTEXT' in context
        assert 'context-test' in context

    def test_context_includes_active_session(self, isolate_paths):
        """Test that context includes the active session."""
        args = make_ns('start', session='active-ctx',
                      summary='Active context test', model='test', platform='pytest')
        cl.cmd_start(args)

        context = cl.get_context_for_cron()
        assert 'active-ctx' in context

    def test_context_with_empty_log(self, isolate_paths):
        """Test context with no entries."""
        context = cl.get_context_for_cron()
        assert isinstance(context, str)
        assert 'RUNA SESSION CONTEXT' in context
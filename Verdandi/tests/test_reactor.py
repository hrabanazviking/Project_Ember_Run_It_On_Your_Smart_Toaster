"""
Comprehensive pytest suite for reactor.py

Covers: reaction directive generation (blockers, decisions, learnings,
        files, milestones, stale sessions), output formats, edge cases.
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import reactor as rt
import conversation_logger as cl

import argparse


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def isolate_paths(tmp_path):
    """Redirect all paths to a temp dir."""
    state_dir = tmp_path / ".hermes" / "state"
    conv_dir = state_dir / "conversations"
    state_dir.mkdir(parents=True, exist_ok=True)
    conv_dir.mkdir(parents=True, exist_ok=True)

    current_file = state_dir / "current.json"
    conv_log = state_dir / "conversation_log.jsonl"

    # Patch conversation_logger paths (imported by reactor)
    original_cl = {
        'STATE_DIR': cl.STATE_DIR,
        'CONV_DIR': cl.CONV_DIR,
        'CURRENT_FILE': cl.CURRENT_FILE,
        'CONV_LOG': cl.CONV_LOG,
    }
    cl.STATE_DIR = state_dir
    cl.CONV_DIR = conv_dir
    cl.CURRENT_FILE = current_file
    cl.CONV_LOG = conv_log

    # Patch reactor paths
    original_rt = {
        'STATE_DIR': rt.STATE_DIR,
        'CONV_LOG': rt.CONV_LOG,
        'CURRENT_FILE': rt.CURRENT_FILE,
    }
    rt.STATE_DIR = state_dir
    rt.CONV_LOG = conv_log
    rt.CURRENT_FILE = current_file

    yield {
        'state_dir': state_dir,
        'conv_dir': conv_dir,
        'current_file': current_file,
        'conv_log': conv_log,
    }

    for key, val in original_cl.items():
        setattr(cl, key, val)
    for key, val in original_rt.items():
        setattr(rt, key, val)


def make_ns(command, **kwargs):
    """Helper to create an argparse Namespace for conversation_logger."""
    return argparse.Namespace(command=command, **kwargs)


def create_session(session_id, events=None, end=True):
    """Create a complete session in the conversation log."""
    args = make_ns('start', session=session_id, summary=f'Session {session_id}',
                  model='test', platform='pytest')
    cl.cmd_start(args)

    if events:
        for etype, content in events:
            event_args = make_ns('event', session=session_id,
                               type=etype, content=content)
            cl.cmd_event(event_args)

    if end:
        end_args = make_ns('end', session=session_id,
                          summary=f'Ended {session_id}', duration=10)
        cl.cmd_end(end_args)


# ============================================================================
# Blocker Detection Tests
# ============================================================================

class TestBlockerDetection:
    def test_unresolved_blockers_detected(self, isolate_paths):
        """Test that unresolved blockers generate reactions."""
        create_session('blocker-test', [
            ('blocker', 'API rate limit hit'),
            ('decision', 'Use rate limiting middleware'),
        ])

        reactions = rt.react()
        assert len(reactions['blockers_needing_reaction']) >= 1
        assert any('API rate limit hit' in b['content'] for b in reactions['blockers_needing_reaction'])

    def test_resolved_blocker_not_in_reactions(self, isolate_paths):
        """Test that resolved blockers don't appear in reactions."""
        create_session('resolved-blocker', [
            ('blocker', 'Database migration stuck'),
            ('blocker_resolved', 'Database migration stuck'),
        ])

        reactions = rt.react()
        # The resolved blocker should not be in the active blockers list
        unresolved = [b['content'] for b in reactions['blockers_needing_reaction']]
        assert 'Database migration stuck' not in unresolved

    def test_multiple_blockers(self, isolate_paths):
        """Test detection of multiple blockers."""
        create_session('multi-blocker', [
            ('blocker', 'Bug A'),
            ('blocker', 'Bug B'),
            ('blocker', 'Bug C'),
        ])

        reactions = rt.react()
        blocker_contents = [b['content'] for b in reactions['blockers_needing_reaction']]
        assert 'Bug A' in blocker_contents
        assert 'Bug B' in blocker_contents
        assert 'Bug C' in blocker_contents


# ============================================================================
# Decision Detection Tests
# ============================================================================

class TestDecisionDetection:
    def test_decisions_tracked(self, isolate_paths):
        """Test that decisions are tracked in reactions."""
        create_session('decision-test', [
            ('decision', 'Use PostgreSQL for persistence'),
        ])

        reactions = rt.react()
        assert len(reactions['decisions_needing_followup']) >= 1
        assert any(d['content'] == 'Use PostgreSQL for persistence'
                   for d in reactions['decisions_needing_followup'])

    def test_duplicate_decisions_deduplicated(self, isolate_paths):
        """Test that duplicate decisions are deduplicated."""
        create_session('dedup-decision', [
            ('decision', 'Same decision twice'),
            ('decision', 'Same decision twice'),
        ])

        reactions = rt.react()
        contents = [d['content'] for d in reactions['decisions_needing_followup']]
        # Should only appear once
        assert contents.count('Same decision twice') == 1


# ============================================================================
# Learning Detection Tests
# ============================================================================

class TestLearningDetection:
    def test_learnings_tracked(self, isolate_paths):
        """Test that learnings are tracked in reactions."""
        create_session('learning-test', [
            ('learned', 'M-08 was stealth-fixed'),
        ])

        reactions = rt.react()
        assert len(reactions['recent_learnings_to_store']) >= 1
        assert any('M-08 was stealth-fixed' in l['content']
                   for l in reactions['recent_learnings_to_store'])

    def test_learnings_include_mimir_suggestion(self, isolate_paths):
        """Test that learnings include Mímir storage suggestions."""
        create_session('mimir-test', [
            ('learned', 'Redis passwords need rotation'),
        ])

        reactions = rt.react()
        learnings = reactions['recent_learnings_to_store']
        assert any('runa_remember' in l['reaction']
                   for l in learnings)


# ============================================================================
# File Changed Detection Tests
# ============================================================================

class TestFileChangedDetection:
    def test_files_changed_tracked(self, isolate_paths):
        """Test that file changes are tracked."""
        create_session('file-test', [
            ('file_changed', 'src/main.py'),
            ('file_changed', 'config.yaml'),
        ])

        reactions = rt.react()
        assert len(reactions['files_changed_needing_push']) >= 2
        files = [f['file'] for f in reactions['files_changed_needing_push']]
        assert 'src/main.py' in files
        assert 'config.yaml' in files


# ============================================================================
# Milestone Detection Tests
# ============================================================================

class TestMilestoneDetection:
    def test_milestones_tracked(self, isolate_paths):
        """Test that milestones are celebrated."""
        create_session('milestone-test', [
            ('milestone', 'First deployment successful'),
        ])

        reactions = rt.react()
        assert len(reactions['milestones_to_acknowledge']) >= 1
        assert any('First deployment successful' in m['content']
                   for m in reactions['milestones_to_acknowledge'])


# ============================================================================
# Stale Session Detection Tests
# ============================================================================

class TestStaleSessionDetection:
    def test_stale_sessions_detected(self, isolate_paths):
        """Test that sessions started >1h ago without an END entry are flagged."""
        # Create a session with an old timestamp and no end entry
        from datetime import datetime, timezone, timedelta
        old_ts = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        entry = {
            'entry_type': 'start',
            'session_id': 'stale-session-test',
            'timestamp': old_ts,
            'summary': 'Old session without end',
        }
        cl._append(entry)

        reactions = rt.react()
        assert len(reactions['stale_sessions_to_close']) >= 1
        assert any('stale-session-test' in s.get('session_id', '')
                   for s in reactions['stale_sessions_to_close'])

    def test_active_sessions_not_flagged(self, isolate_paths):
        """Test that properly closed sessions are not flagged as stale."""
        create_session('active-session', [
            ('decision', 'Made a decision'),
        ], end=True)

        reactions = rt.react()
        stale_ids = [s.get('session_id', '') for s in reactions['stale_sessions_to_close']]
        assert 'active-session' not in stale_ids


# ============================================================================
# Output Format Tests
# ============================================================================

class TestOutputFormats:
    def test_json_format(self, isolate_paths):
        """Test JSON format output."""
        create_session('format-json', [('decision', 'Test decision')])

        reactions = rt.react()
        output = rt.format_reactions(reactions, fmt='json')
        parsed = json.loads(output)
        assert isinstance(parsed, dict)
        assert 'blockers_needing_reaction' in parsed

    def test_brief_format(self, isolate_paths):
        """Test brief (one-line) format output."""
        create_session('format-brief', [('blocker', 'Brief blocker')])

        reactions = rt.react()
        output = rt.format_reactions(reactions, fmt='brief')
        assert isinstance(output, str)
        assert '1 blocker(s)' in output

    def test_brief_format_clean(self, isolate_paths):
        """Test brief format with no issues."""
        reactions = rt.react()
        output = rt.format_reactions(reactions, fmt='brief')
        assert 'clean' in output.lower() or 'No reactions' in output

    def test_text_format(self, isolate_paths):
        """Test full text format output."""
        create_session('format-text', [
            ('blocker', 'Text blocker'),
            ('decision', 'Text decision'),
        ])

        reactions = rt.react()
        output = rt.format_reactions(reactions, fmt='text')
        assert 'REACTION REPORT' in output
        assert 'Text blocker' in output or 'blocker' in output.lower()


# ============================================================================
# Next Actions Tests
# ============================================================================

class TestNextActions:
    def test_next_actions_from_current_state(self, isolate_paths):
        """Test that next actions from current.json are picked up."""
        # Start a session with next actions via update
        args = make_ns('start', session='next-actions-test',
                      summary='Next actions', model='test', platform='pytest')
        cl.cmd_start(args)

        update_args = make_ns('update', session='next-actions-test',
                            next=['Do task A', 'Do task B'],
                            blockers=None, projects=[], mood='', summary='')
        cl.cmd_update(update_args)

        reactions = rt.react()
        assert len(reactions['next_actions_to_pick_up']) >= 2
        action_contents = [a['content'] for a in reactions['next_actions_to_pick_up']]
        assert 'Do task A' in action_contents
        assert 'Do task B' in action_contents


# ============================================================================
# Priority Reaction Directives Tests
# ============================================================================

class TestReactionDirectives:
    def test_blocker_reactions_have_priority(self, isolate_paths):
        """Test that blockers generate HIGH priority reactions."""
        create_session('priority-test', [
            ('blocker', 'Critical blocker'),
        ])

        reactions = rt.react()
        assert len(reactions['reactions']) >= 1
        blocker_reaction = [r for r in reactions['reactions']
                           if r['action'] == 'resolve_blockers']
        assert len(blocker_reaction) >= 1
        assert blocker_reaction[0]['priority'] == 'HIGH'

    def test_milestone_reactions_are_info(self, isolate_paths):
        """Test that milestones generate INFO priority reactions."""
        create_session('milestone-priority', [
            ('milestone', 'Big milestone'),
        ])

        reactions = rt.react()
        milestone_reaction = [r for r in reactions['reactions']
                            if r['action'] == 'celebrate']
        assert len(milestone_reaction) >= 1
        assert milestone_reaction[0]['priority'] == 'INFO'


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    def test_empty_log(self, isolate_paths):
        """Test reactions with no log entries."""
        reactions = rt.react()
        assert reactions is not None
        assert reactions['blockers_needing_reaction'] == []
        assert reactions['decisions_needing_followup'] == []
        assert reactions['recent_learnings_to_store'] == []
        assert reactions['files_changed_needing_push'] == []
        assert reactions['milestones_to_acknowledge'] == []

    def test_no_current_state(self, isolate_paths):
        """Test reactions with no current.json."""
        reactions = rt.react()
        # Should still work, just no next_actions
        assert reactions['next_actions_to_pick_up'] == []

    def test_corrupt_log_lines(self, isolate_paths):
        """Test reactions with corrupt lines in the log."""
        with open(isolate_paths['conv_log'], 'w') as f:
            f.write('{"entry_type": "start", "session_id": "ok", "timestamp": "2026-05-10T12:00:00+00:00"}\n')
            f.write('corrupt line\n')
            f.write('{"entry_type": "event", "session_id": "ok", "event_type": "decision", "content": "Good decision"}\n')

        reactions = rt.react()
        # Should still work despite corrupt lines
        assert len(reactions['decisions_needing_followup']) >= 1

    def test_session_with_all_event_types(self, isolate_paths):
        """Test a session with all event types."""
        create_session('all-types', [
            ('decision', 'Made a decision'),
            ('file_changed', 'changed_file.py'),
            ('learned', 'Learned something new'),
            ('blocker', 'Hit a blocker'),
            ('blocker_resolved', 'Hit a blocker'),
            ('milestone', 'Reached a milestone'),
            ('mood_shift', 'feeling productive'),
            ('action', 'Did something'),
        ])

        reactions = rt.react()
        assert len(reactions['decisions_needing_followup']) >= 1
        assert len(reactions['files_changed_needing_push']) >= 1
        assert len(reactions['recent_learnings_to_store']) >= 1
        assert len(reactions['milestones_to_acknowledge']) >= 1
        # Resolved blocker should not be in the list
        blocker_contents = [b['content'] for b in reactions['blockers_needing_reaction']]
        assert 'Hit a blocker' not in blocker_contents

    def test_parse_timestamp(self):
        """Test the timestamp parsing utility."""
        from datetime import datetime, timezone
        # Valid ISO timestamp
        result = rt._parse_timestamp('2026-05-10T12:00:00+00:00')
        assert result is not None
        assert isinstance(result, datetime)

        # Invalid timestamp
        result = rt._parse_timestamp('invalid')
        assert result is None

        # None
        result = rt._parse_timestamp(None)
        assert result is None

    def test_get_current_state_corrupt(self, isolate_paths):
        """Test _get_current_state with corrupt JSON."""
        with open(isolate_paths['current_file'], 'w') as f:
            f.write('not valid json')
        result = rt._get_current_state()
        assert result is None

    def test_get_current_state_missing(self, isolate_paths):
        """Test _get_current_state with missing file."""
        result = rt._get_current_state()
        assert result is None
"""E-072 — The logger as memory source: logged conversations
can feed memory under the user's rule, never silently.

Pins Verdandi/memory_feed.py (the law): no rule / disabled /
non-user / invalid rules feed nothing and say so; a valid
user rule feeds only feedable event types it names, only
in-scope sessions, end summaries only when opted in; the
report is counts-only (a sentinel content string appears
nowhere in it); and live entries written by the real
conversation logger feed through the law unchanged.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from argparse import Namespace
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-072_LOGGER_AS_MEMORY_SOURCE.md"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


feed = _load("ember_memory_feed_e072", VERDANDI / "memory_feed.py")
logger = _load("ember_conversation_logger_e072", VERDANDI / "conversation_logger.py")

SENTINEL = "sentinel-learned-content-072"


def _rule(**over):
    rule = {
        "enabled": True,
        "granted_by": "user",
        "scope": "named_sessions",
        "session_ids": ["sess-a"],
        "event_types": ["learned", "decision"],
        "rule_id": "user-rule-1",
    }
    rule.update(over)
    return rule


def _entry(session="sess-a", kind="event", event_type="learned",
           content=SENTINEL, **extra):
    entry = {"entry_type": kind, "timestamp": "2026-10-31T00:00:00+00:00",
             "session_id": session}
    if kind == "event":
        entry["event_type"] = event_type
        entry["content"] = content
    elif kind == "end":
        entry["summary"] = content
        entry.update({"duration_minutes": 1, "decisions": [],
                      "things_learned": [], "files_changed": [],
                      "next_actions": [], "blockers": [],
                      "projects_touched": []})
    entry.update(extra)
    return entry


# ── The module itself ──────────────────────────────────────


def test_module_is_stdlib_only_and_standalone():
    tree = ast.parse(_source(VERDANDI / "memory_feed.py"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= set(sys.stdlib_module_names)
    assert feed.MEMORY_FEED_VERSION == 1
    assert feed.FEEDABLE_EVENT_TYPES == ("learned", "decision", "milestone")


def test_doc_states_the_rule():
    text = DOC.read_text(encoding="utf-8")
    for phrase in ("never silently", "user's rule", "Part V", "docket 104"):
        assert phrase in text


def test_feedable_vocabulary_excludes_working_state():
    for working in ("file_changed", "action", "blocker",
                    "blocker_resolved", "mood_shift"):
        assert working not in feed.FEEDABLE_EVENT_TYPES


# ── Never silently: the gate conditions ────────────────────


def test_no_rule_feeds_nothing_and_says_so():
    candidates, report = feed.feed_candidates([_entry()], None)
    assert candidates == []
    assert report["status"] == "no_rule"
    assert report["fed"] == 0 and report["withheld_no_rule"] == 1


def test_disabled_rule_feeds_nothing():
    candidates, report = feed.feed_candidates([_entry()], _rule(enabled=False))
    assert candidates == []
    assert report["status"] == "rule_disabled"
    assert report["withheld_rule_disabled"] == 1


def test_non_user_grant_feeds_nothing():
    candidates, report = feed.feed_candidates([_entry()], _rule(granted_by="program"))
    assert candidates == []
    assert report["status"] == "invalid_rule"
    assert any("granted_by" in e for e in report["errors"])


@pytest.mark.parametrize("bad", [
    {"scope": "everywhere"},
    {"scope": "named_sessions", "session_ids": []},
    {"scope": "all_sessions", "session_ids": ["sess-a"]},
    {"event_types": []},
    {"event_types": ["learned", "blocker"]},
    {"event_types": ["learned"], "surprise": True},
    {"enabled": "yes"},
])
def test_invalid_rules_fail_closed(bad):
    rule = _rule(**bad)
    if bad.get("scope") == "all_sessions":
        rule = _rule(scope="all_sessions")
        rule.pop("session_ids")
        rule["session_ids"] = ["sess-a"]
    candidates, report = feed.feed_candidates([_entry()], rule)
    assert candidates == []
    assert report["status"] == "invalid_rule"
    assert report["errors"]


def test_validate_rule_accepts_the_canonical_rule():
    assert feed.validate_rule(_rule()) == []
    assert feed.validate_rule(_rule(scope="all_sessions",
                                    session_ids=None)) != []  # key present is an error path
    all_rule = _rule(scope="all_sessions")
    del all_rule["session_ids"]
    assert feed.validate_rule(all_rule) == []


# ── What feeds, under the rule ─────────────────────────────


def test_named_scope_feeds_selected_feedable_events():
    entries = [
        _entry(content="learned one"),
        _entry(event_type="decision", content="decided one"),
        _entry(event_type="milestone", content="milestone not selected"),
        _entry(session="sess-b", content="other session"),
    ]
    candidates, report = feed.feed_candidates(entries, _rule())
    assert [c["content"] for c in candidates] == ["learned one", "decided one"]
    assert [c["category"] for c in candidates] == ["lesson", "decision"]
    assert report["fed"] == 2
    assert report["withheld_not_selected"] == 1
    assert report["withheld_out_of_scope"] == 1
    assert candidates[0]["provenance"] == {
        "log_file": "conversation_log.jsonl", "entry_type": "event",
        "event_type": "learned", "rule_id": "user-rule-1"}
    assert candidates[0]["source"] == "conversation_logger"


def test_working_state_and_headers_never_feed():
    entries = [
        _entry(event_type="blocker", content="blocked"),
        _entry(kind="start", content=""),
        _entry(kind="update", content=""),
    ]
    candidates, report = feed.feed_candidates(entries, _rule())
    assert candidates == []
    assert report["withheld_not_feedable"] == 3


def test_end_summary_only_when_opted_in():
    end = _entry(kind="end", content="closing summary")
    candidates, report = feed.feed_candidates([end], _rule())
    assert candidates == [] and report["withheld_not_selected"] == 1
    candidates, report = feed.feed_candidates(
        [end], _rule(include_end_summary=True))
    assert len(candidates) == 1
    assert candidates[0]["category"] == "session_summary"
    assert candidates[0]["provenance"]["event_type"] is None


def test_empty_and_duplicate_and_unattributable_are_counted():
    entries = [
        _entry(content="   "),
        _entry(content="once"),
        _entry(content="once"),
        {"entry_type": "event", "event_type": "learned", "content": "no session"},
        "not a dict",
    ]
    candidates, report = feed.feed_candidates(entries, _rule())
    assert [c["content"] for c in candidates] == ["once"]
    assert report["withheld_empty"] == 1
    assert report["withheld_duplicate"] == 1
    assert report["withheld_unattributable"] == 2
    assert report["total"] == 5 and report["fed"] == 1


def test_all_sessions_scope_feeds_any_session():
    rule = _rule(scope="all_sessions")
    del rule["session_ids"]
    candidates, _ = feed.feed_candidates([_entry(session="sess-z")], rule)
    assert len(candidates) == 1


def test_persona_tag_comes_from_session_owners_never_content():
    candidates, _ = feed.feed_candidates(
        [_entry()], _rule(), session_owners={"sess-a": "persona-a"})
    assert candidates[0]["persona_id"] == "persona-a"
    candidates, _ = feed.feed_candidates([_entry()], _rule())
    assert candidates[0]["persona_id"] is None


def test_report_is_counts_only_and_input_unmutated():
    entries = [_entry(), _entry(session="sess-b")]
    snapshot = json.dumps(entries, sort_keys=True)
    candidates, report = feed.feed_candidates(entries, _rule())
    assert SENTINEL not in json.dumps(report)
    assert "sess-b" not in json.dumps(report)
    assert json.dumps(entries, sort_keys=True) == snapshot
    candidates2, _ = feed.feed_log_entries(entries, _rule())
    assert candidates2 == candidates


# ── Live logger entries feed through the law ───────────────


@pytest.fixture()
def state(tmp_path, monkeypatch):
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    monkeypatch.setattr(logger, "STATE_DIR", state_dir)
    monkeypatch.setattr(logger, "CONV_DIR", state_dir / "conversations")
    monkeypatch.setattr(logger, "CURRENT_FILE", state_dir / "current.json")
    monkeypatch.setattr(logger, "CONV_LOG", state_dir / "conversation_log.jsonl")
    return state_dir


def test_live_logger_entries_feed_and_deleted_session_does_not(state):
    logger.cmd_start(Namespace(session="sess-live", summary="s",
                               model="m", platform="pytest"))
    logger.cmd_event(Namespace(session="sess-live", type="learned",
                               content=SENTINEL))
    logger.cmd_event(Namespace(session="sess-live", type="blocker",
                               content="a blocker is working state"))
    entries = logger._read_all_entries()
    rule = _rule(session_ids=["sess-live"])
    candidates, report = feed.feed_candidates(entries, rule)
    assert [c["content"] for c in candidates] == [SENTINEL]
    assert report["total"] == len(entries)
    # The E-063 delete right removes the session from the log;
    # no later feed can draw from it.
    logger.delete_session("sess-live")
    candidates, report = feed.feed_candidates(logger._read_all_entries(), rule)
    assert candidates == [] and report["total"] == 0

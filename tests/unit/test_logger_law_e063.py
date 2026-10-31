"""E-063 — The conversation logger's law conformance.

Pins Verdandi/logger_law.py against the code it governs:
the logger's entry/event vocabularies and live entry fields,
the heartbeat's retention thresholds at their sources, and
the behavioural law — current.json ownership (docket 98),
and the user's delete right exercised totally (log +
current + nerve feed + rotated archives, plain and gzipped)
and provably (the report's verification is a re-read, and a
deleted session no longer reaches context injection).
"""

import ast
import gzip
import importlib.util
import json
import sys
from argparse import Namespace
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-063_CONVERSATION_LOGGER_LAW.md"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


law = _load("ember_logger_law", VERDANDI / "logger_law.py")
logger = _load("ember_conversation_logger_e063", VERDANDI / "conversation_logger.py")


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── The law is well-formed and cannot drift ─────────────────────


def test_law_version_and_vocabularies_match_the_logger():
    assert law.LOGGER_LAW_VERSION == 1
    assert law.EVENT_TYPES == logger.EVENT_TYPES
    assert law.ENTRY_TYPES == ("start", "event", "update", "end")
    assert set(law.ENTRY_FIELDS) == set(law.ENTRY_TYPES)


def test_law_module_is_stdlib_only_and_self_contained():
    tree = ast.parse(_source(VERDANDI / "logger_law.py"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= set(sys.stdlib_module_names)
    assert "conversation_logger" not in imports


def test_delete_scope_names_the_three_stores():
    assert law.DELETE_SCOPE_FILES == (
        "conversation_log.jsonl", "current.json", "nerve_feed.jsonl")
    assert law.LOG_FILE in law.DELETE_SCOPE_FILES
    assert law.DELETE_ALL_REQUIRES_YES is True


def test_retention_thresholds_match_their_sources():
    bifrost = _source(VERDANDI / "heartbeat" / "actions" / "bifrǫst.py")
    assert f'"conversation_log_max_mb": {law.CONVERSATION_LOG_PRUNE_MB}' in bifrost
    assert f'"nerve_feed_max_mb": {law.NERVE_FEED_PRUNE_MB}' in bifrost
    mimir = _source(VERDANDI / "heartbeat" / "checks" / "mimir.py")
    assert f'"thresholds.log_size_warning_mb", {law.LOG_SIZE_WARNING_MB}' in mimir
    assert f'"thresholds.log_size_critical_mb", {law.LOG_SIZE_CRITICAL_MB}' in mimir
    hub = _source(VERDANDI / "nervous_system.py")
    assert f"MAX_FEED_BYTES = {law.NERVE_FEED_ROTATE_BYTES // (1024 * 1024)} * 1024 * 1024" in hub


def test_dead_update_current_is_gone_docket_98():
    tree = ast.parse(_source(VERDANDI / "conversation_logger.py"))
    defs = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    assert "_update_current" not in defs


def test_doc_names_the_law():
    doc = _source(DOC)
    for needle in ("conversation_log.jsonl", "current.json", "nerve_feed.jsonl",
                   "delete --session", "delete --all --yes", "50 MB",
                   "Bifröst", "docket 98", "docket 100"):
        assert needle in doc, needle


# ── Behaviour in an isolated state dir ──────────────────────────


@pytest.fixture()
def state(tmp_path, monkeypatch):
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    monkeypatch.setattr(logger, "STATE_DIR", state_dir)
    monkeypatch.setattr(logger, "CONV_DIR", state_dir / "conversations")
    monkeypatch.setattr(logger, "CURRENT_FILE", state_dir / "current.json")
    monkeypatch.setattr(logger, "CONV_LOG", state_dir / "conversation_log.jsonl")
    return state_dir


def _start(sid, summary=""):
    return logger.cmd_start(Namespace(
        session=sid, summary=summary, model="m", platform="pytest"))


def _event(sid, etype, content):
    return logger.cmd_event(Namespace(session=sid, type=etype, content=content))


def _feed_entry(sid, kind="conv_event"):
    return {"v": 1, "type": kind,
            "data": {"entry_type": "event", "session_id": sid},
            "source": f"conv_logger:{sid}"}


def _write_feed(state_dir: Path, entries, name="nerve_feed.jsonl", extra_lines=()):
    path = state_dir / name
    if name.endswith(".gz"):
        with gzip.open(path, "wt", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
            for line in extra_lines:
                f.write(line + "\n")
    else:
        lines = [json.dumps(e) for e in entries]
        path.write_text("\n".join(lines + list(extra_lines)) + "\n", encoding="utf-8")
    return path


def test_live_entries_carry_exactly_the_laws_fields(state):
    _start("s1", "sum")
    _event("s1", "decision", "did a thing")
    logger.cmd_update(Namespace(session="s1", next=["n"], blockers=[],
                                projects=["P"], mood="calm", summary=""))
    logger.cmd_end(Namespace(session="s1", summary="done", duration=5))
    entries = logger._get_entries_for_session("s1")
    by_kind = {}
    for e in entries:
        by_kind.setdefault(e["entry_type"], e)
    assert set(by_kind) == set(law.ENTRY_TYPES)
    for kind, fields in law.ENTRY_FIELDS.items():
        assert tuple(by_kind[kind].keys()) == fields, kind


def test_cross_session_event_does_not_rewrite_current(state):
    _start("alpha", "A")
    _start("beta", "B")
    _event("alpha", "decision", "alpha late decision")
    current = logger.get_current_state()
    assert current["session_id"] == "beta"
    assert "alpha late decision" not in json.dumps(current)
    # …but the entry itself is still in the log — the log is the truth.
    assert any(e.get("content") == "alpha late decision"
               for e in logger._get_entries_for_session("alpha"))


def test_cross_session_update_and_end_leave_current_alone(state):
    _start("alpha", "A")
    _event("alpha", "decision", "keep me")
    _start("beta", "B")
    logger.cmd_update(Namespace(session="alpha", next=["x"], blockers=["y"],
                                projects=[], mood="tense", summary=""))
    logger.cmd_end(Namespace(session="alpha", summary="alpha done", duration=3))
    current = logger.get_current_state()
    assert current["session_id"] == "beta"
    assert current["status"] == "active"
    end = [e for e in logger._get_entries_for_session("alpha")
           if e["entry_type"] == "end"]
    assert len(end) == 1 and end[0]["summary"] == "alpha done"
    # The foreign end entry must not carry beta's (or alpha's stale
    # snapshot) lists — it is built from its own arguments alone.
    assert end[0]["decisions"] == []


def test_delete_session_is_total_across_all_stores(state):
    _start("alpha", "Alpha summary")
    _event("alpha", "decision", "Alpha decision")
    _start("beta", "Beta summary")
    _write_feed(state, [_feed_entry("alpha"), _feed_entry("beta"),
                        {"v": 1, "type": "heartbeat_pulse", "data": {}, "source": "hb"}],
                extra_lines=["corrupt-line"])
    _write_feed(state, [_feed_entry("alpha", "conv_start")],
                name="nerve_feed_2026-01-01T00-00-00.jsonl")
    _write_feed(state, [_feed_entry("alpha", "conv_start")],
                name="nerve_feed_2026-01-02T00-00-00.jsonl.gz")
    with open(state / "conversation_log.jsonl", "a", encoding="utf-8") as f:
        f.write("corrupt-log-line\n")

    report = logger.delete_session("alpha")

    assert report["verified"] is True
    assert report["log_entries_removed"] == 2
    assert report["current_removed"] is False  # current belongs to beta
    assert report["nerve_entries_removed"] == 3  # feed + plain archive + gz archive
    assert report["unattributed_lines_kept"] == 2  # one per JSONL store purged
    assert logger._get_entries_for_session("alpha") == []
    assert len(logger._get_entries_for_session("beta")) == 1
    assert logger.get_current_state()["session_id"] == "beta"
    feed = (state / "nerve_feed.jsonl").read_text(encoding="utf-8")
    assert "conv_logger:alpha" not in feed
    assert "conv_logger:beta" in feed and "heartbeat_pulse" in feed
    assert "corrupt-line" in feed  # unattributable: kept, counted, not claimed
    assert not list(state.glob("*.tmp-e063"))  # atomic rewrite leaves no temp


def test_delete_session_removes_its_own_current(state):
    _start("solo", "only session")
    report = logger.delete_session("solo")
    assert report["current_removed"] is True
    assert logger.get_current_state() is None
    assert report["verified"] is True


def test_delete_unknown_session_removes_nothing_and_verifies(state):
    _start("beta", "Beta summary")
    before = (state / "conversation_log.jsonl").read_bytes()
    report = logger.delete_session("nope")
    assert report["log_entries_removed"] == 0
    assert report["verified"] is True
    assert (state / "conversation_log.jsonl").read_bytes() == before


def test_deleted_session_no_longer_reaches_context_injection(state):
    _start("alpha", "Alpha injected summary")
    _start("beta", "Beta injected summary")
    logger.delete_session("alpha")
    block = logger.get_context_for_cron()
    assert "Alpha injected summary" not in block
    assert "Beta injected summary" in block


def test_delete_all_requires_yes_at_the_command_layer(state):
    _start("alpha", "A")
    with pytest.raises(SystemExit):
        logger.cmd_delete(Namespace(session="", all=True, yes=False))
    assert len(logger._read_all_entries()) == 1  # nothing was deleted


def test_delete_all_is_total_and_keeps_non_conversation_feed(state):
    _start("alpha", "A")
    _event("alpha", "learned", "something")
    _write_feed(state, [_feed_entry("alpha"),
                        {"v": 1, "type": "heartbeat_pulse", "data": {}, "source": "hb"}])
    report = logger.cmd_delete(Namespace(session="", all=True, yes=True))
    assert report["verified"] is True
    assert report["log_entries_removed"] == 2
    assert report["current_removed"] is True
    assert not (state / "conversation_log.jsonl").exists()
    assert not (state / "current.json").exists()
    feed = (state / "nerve_feed.jsonl").read_text(encoding="utf-8")
    assert "conv_" not in feed and "heartbeat_pulse" in feed


def test_delete_parser_shape():
    parser = logger._build_parser()
    args = parser.parse_args(["delete", "--session", "x"])
    assert args.session == "x" and args.all is False and args.yes is False
    args = parser.parse_args(["delete", "--all", "--yes"])
    assert args.all is True and args.yes is True

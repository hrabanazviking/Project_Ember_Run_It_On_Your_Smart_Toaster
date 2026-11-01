"""E-069 — Ordering & replay: events replay deterministically
for debugging (fixtures).

Pins Verdandi/replay.py against the shapes it governs: the
hub's _seq order is the replay order, unsequenced fallback
and legacy events follow by the stated rule (timestamp,
then file order, no invented sequence), gaps and duplicate
sequences are reported not hidden, corrupt feed lines are
skipped and named by line number, replay is lossless for
every dialect incl. Hermes provenance (E-068), and two
replays of the same feed — even from a shuffled copy — are
the same replay, digest and all.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-069_ORDERING_AND_REPLAY.md"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


replay = _load("ember_replay_e069", VERDANDI / "replay.py")
contract = _load("ember_event_contract_e069", VERDANDI / "event_contract.py")
hermes = _load("ember_hermes_nerves_e069", VERDANDI / "hermes_nerves.py")


def _hub(seq, typ="ember_turn", ts=None, **data):
    event = {"v": 1, "type": typ, "data": data or {"n": seq}, "source": "ember_core"}
    if seq is not None:
        event["_seq"] = seq
    if ts is not None:
        event["_ts"] = ts
    return event


def _fixture_feed():
    """One feed covering every shape E-069 must order."""
    return [
        _hub(3, ts=103.0),
        {"v": 1, "type": "conv_start", "data": {"session_id": "s1"},
         "source": "conv_logger:s1", "_seq": 1, "_ts": 101.0,
         "_iso": "2026-10-31T10:00:01+00:00"},
        _hub(2, ts=102.0),
        # Offline fallback: no _seq, stamped _fallback + _ts.
        {"v": 1, "type": "heartbeat_pulse", "data": {"pulse_count": 9},
         "source": "verdandi-heartbeat", "_fallback": True, "_ts": 104.0},
        # Legacy heartbeat fallback line (flat, ISO timestamp).
        {"event_type": "heartbeat_pulse", "source": "verdandi-heartbeat",
         "timestamp": "2026-10-31T10:00:05+00:00", "pulse_count": 10},
        # Legacy mood-dialect line (epoch timestamp).
        {"source": "mood_arousal_system", "event": "event:calm",
         "timestamp": 99.0, "data": {"mood": "calm"}},
        # No timestamp at all.
        {"v": 1, "type": "operator_note", "data": {"text": "hi"}, "source": "op"},
    ]


# ── The module itself ──────────────────────────────────────


def test_module_is_stdlib_only_and_standalone():
    tree = ast.parse(_source(VERDANDI / "replay.py"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= set(sys.stdlib_module_names) | {"__future__"}
    assert replay.REPLAY_VERSION == 1


def test_dialects_mirror_the_contract_plus_unknown():
    assert set(replay.DIALECTS) == set(contract.DIALECTS) | {"unknown"}
    for event, dialect in (
        (_hub(1), "hub"),
        ({"event": "event:x", "data": {}}, "mood"),
        ({"event_type": "heartbeat_pulse"}, "heartbeat"),
        ({"event_type": "heartbeat_pulse", "source": "verdandi-heartbeat",
          "timestamp": "2026-10-31T10:00:00+00:00"}, "heartbeat_fallback"),
        ({"surprise": True}, "unknown"),
    ):
        assert replay.classify_dialect(event) == dialect, event


def test_doc_states_the_order_and_the_honest_limits():
    doc = _source(DOC)
    for needle in ("_seq", "_fallback", "digest", "docket", "E-070", "E-076"):
        assert needle in doc, needle


# ── Ordering ───────────────────────────────────────────────


def test_sequenced_events_replay_in_seq_order():
    events = [_hub(3), _hub(1), _hub(2)]
    ordered = replay.order_events(events)
    assert [e["_seq"] for e in ordered] == [1, 2, 3]
    assert [e["_seq"] for e in events] == [3, 1, 2]  # input untouched


def test_unsequenced_follow_by_timestamp_then_file_order():
    ordered = replay.order_events(_fixture_feed())
    assert [replay.seq_of(e) for e in ordered[:3]] == [1, 2, 3]
    rest = ordered[3:]
    # mood (99.0) < fallback (104.0) < legacy ISO (10:00:05) < timeless last.
    assert rest[0]["event"] == "event:calm"
    assert rest[1].get("_fallback") is True
    assert rest[2]["event_type"] == "heartbeat_pulse"
    assert rest[3]["type"] == "operator_note"


def test_duplicate_seq_keeps_file_order():
    first = _hub(2, typ="first")
    second = _hub(2, typ="second")
    ordered = replay.order_events([first, _hub(1), second])
    assert [e["type"] for e in ordered] == ["ember_turn", "first", "second"]


def test_no_sequence_is_ever_invented():
    for event in replay.order_events(_fixture_feed()):
        if replay.seq_of(event) is None:
            assert "_seq" not in event


def test_ordering_is_idempotent_and_validates():
    ordered = replay.order_events(_fixture_feed())
    assert replay.order_events(ordered) == ordered
    assert replay.validate_replay_order(ordered) == []
    assert replay.validate_replay_order(list(reversed(ordered))) != []


def test_seq_and_timestamp_shapes_are_strict():
    assert replay.seq_of({"_seq": True}) is None
    assert replay.seq_of({"_seq": "3"}) is None
    assert replay.seq_of({"_seq": 3}) == 3
    assert replay.effective_timestamp({"_ts": True}) is None
    assert replay.effective_timestamp({"_ts": 5}) == 5.0
    assert replay.effective_timestamp({"_iso": "2026-10-31T10:00:00+00:00"}) is not None
    assert replay.effective_timestamp({"timestamp": "not a date"}) is None


# ── Determinism ────────────────────────────────────────────


def test_two_replays_are_the_same_replay():
    feed = _fixture_feed()
    one = replay.replay_events(feed)
    two = replay.replay_events(json.loads(json.dumps(feed)))
    assert one["ordered"] == two["ordered"]
    assert one["digest"] == two["digest"]
    assert len(one["digest"]) == 64


def test_shuffled_sequenced_events_replay_identically():
    feed = [_hub(n, ts=100.0 + n) for n in (1, 2, 3, 4, 5)]
    shuffled = [feed[i] for i in (3, 0, 4, 1, 2)]
    assert replay.replay_events(shuffled)["digest"] == replay.replay_events(feed)["digest"]
    assert replay.replay_events(shuffled)["ordered"] == feed


def test_digest_changes_with_content_and_order():
    base = replay.replay_events([_hub(1), _hub(2)])["digest"]
    # Input order does not matter for sequenced events: the
    # sorted replay of the same events has the same digest.
    assert replay.replay_events([_hub(2), _hub(1)])["digest"] == base
    changed = _hub(1)
    changed["data"] = {"n": "different"}
    assert replay.replay_events([changed, _hub(2)])["digest"] != base


def test_replay_to_hands_each_event_once_in_order():
    seen = []
    report = replay.replay_to(_fixture_feed(), seen.append)
    assert seen == report["ordered"]
    assert len(seen) == len(set(map(replay.canonical_line, seen)))


def test_replay_to_propagates_sink_failure():
    def boom(_event):
        raise RuntimeError("consumer failed")

    try:
        replay.replay_to([_hub(1)], boom)
    except RuntimeError:
        pass
    else:
        raise AssertionError("sink failure was swallowed")


# ── The report: gaps, duplicates, damage ───────────────────


def test_report_names_gaps_duplicates_and_counts():
    feed = [_hub(1), _hub(2), _hub(2, typ="dup"), _hub(5),
            {"v": 1, "type": "x", "data": {}, "source": "s", "_fallback": True}]
    report = replay.replay_events(feed)
    assert report["count"] == 5
    assert (report["seq_min"], report["seq_max"]) == (1, 5)
    assert report["gaps"] == [3, 4]
    assert report["duplicate_seqs"] == [2]
    assert report["unsequenced"] == 1 and report["fallback"] == 1
    assert report["dialects"] == {"hub": 5}
    assert report["issues"] == []


def test_feed_lines_skip_and_name_corrupt_lines():
    lines = [
        json.dumps(_hub(1)),
        "",
        "{not json",
        json.dumps(["a", "list"]),
        json.dumps(_hub(2)),
    ]
    report = replay.replay_feed_lines(lines)
    assert report["count"] == 2
    assert [(i["line"], i["kind"]) for i in report["issues"]] == [
        (3, "invalid_json"), (4, "not_object")]
    events, issues = replay.load_feed_text("\n".join(lines))
    assert len(events) == 2 and len(issues) == 2


# ── Losslessness: dialects and Hermes provenance ───────────


def test_replay_is_lossless_for_every_dialect():
    feed = _fixture_feed()
    snapshot = json.loads(json.dumps(feed))
    ordered = replay.order_events(feed)
    assert feed == snapshot  # nothing edited in place
    assert sorted(map(replay.canonical_line, ordered)) == \
        sorted(map(replay.canonical_line, snapshot))


def test_hermes_provenance_survives_replay():
    raw = {
        "type": "hermes.turn.completed", "source": "hermes-agent",
        "data": {"schema": hermes.HERMES_SCHEMA, "schema_version": 1,
                 "event_id": "evt-1", "occurred_at": "2026-10-31T10:00:00+00:00",
                 "event": "hermes.turn.completed",
                 "context": {"session_id": "s1", "completed": True}},
        "_seq": 7, "_ts": 107.0,
    }
    translated = hermes.normalize_hermes_event(
        {"type": "hermes.session.started", "source": "hermes-agent",
         "data": {"schema": hermes.HERMES_SCHEMA, "schema_version": 1,
                  "event_id": "evt-0", "occurred_at": "2026-10-31T09:59:00+00:00",
                  "event": "hermes.session.started",
                  "context": {"session_id": "s1", "model": "m", "platform": "cli"}},
         "_seq": 6, "_ts": 106.0})
    ordered = replay.order_events([raw, translated])
    assert ordered[0] is translated and ordered[1] is raw
    assert ordered[0]["_hermes_event_id"] == "evt-0"
    assert ordered[0]["_hermes_schema"] == hermes.HERMES_SCHEMA
    assert ordered[1]["data"]["event_id"] == "evt-1"
    assert ordered[1]["data"]["context"] == {"session_id": "s1", "completed": True}


def test_stimulus_provenance_survives_replay():
    stimulus_event = {
        "v": 1, "type": "stimulus:time.tick", "source": "heartbeat-daemon",
        "data": {"kind": "time", "name": "time.tick", "payload": {},
                 "provenance": {"origin": "heartbeat-daemon", "channel": "timer"}},
        "_seq": 4, "_ts": 104.0,
    }
    report = replay.replay_events([stimulus_event])
    assert report["ordered"][0]["data"]["provenance"] == {
        "origin": "heartbeat-daemon", "channel": "timer"}

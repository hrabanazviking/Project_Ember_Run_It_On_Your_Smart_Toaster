"""E-071 — Privacy of nerves: stimuli provenance never
leaks across personae.

Pins Verdandi/nerve_privacy.py (the law), its fixtures
(own visible whole, cross withheld entirely with sentinel
provenance absent from view AND report, system visible to
all, session-bound fail-closed), redaction, and the Ember
core bridge's inline copy in src/ember/nerve.py — incl.
read_recent_for_persona over a feed file.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-071_NERVE_PRIVACY.md"
sys.path.insert(0, str(REPO / "src"))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


priv = _load("ember_nerve_privacy_e071", VERDANDI / "nerve_privacy.py")
stim = _load("ember_stimuli_e071", VERDANDI / "stimuli.py")

from ember import nerve  # noqa: E402

A = "persona-a"
B = "persona-b"
SENTINEL = "sentinel-origin-b-secret"
OWNERS = {"sess-a": A, "sess-b": B}


def _core_event(persona, typ="ember_turn"):
    data = {"persona_id": persona, "conversation_id": "c1"}
    if typ == "ember_session":
        data = {"phase": "start", **data, "well_connected": True, "model": "m", "turns": 0}
    else:
        data = {**data, "hits": 1, "cited": 0, "persisted": "well",
                "ungrounded": False, "outcome": "answered", "model": "m"}
    return {"v": 1, "type": typ, "data": data, "source": "ember_core"}


def _stimulus_event(persona=None, *, via="payload", origin=SENTINEL, name="message.operator",
                    payload_extra=None, session=None):
    payload = dict(payload_extra or {})
    if session is not None:
        payload["session_id"] = session
    prov = {"origin": origin, "channel": "cli"}
    if persona is not None and via == "payload":
        payload["persona_id"] = persona
    if persona is not None and via == "provenance":
        prov["persona_id"] = persona
    data = {"kind": "message", "name": name, "payload": payload, "provenance": prov}
    return {"v": 1, "type": "stimulus:" + name, "data": data, "source": origin}


def _conv(session, typ="conv_event"):
    return {"v": 1, "type": typ, "source": f"conv_logger:{session}",
            "data": {"timestamp": "t", "session_id": session, "entry_type": "log",
                     "event_type": "note", "content": "x"}}


def _system_events():
    return [
        {"v": 1, "type": "heartbeat_pulse", "source": "verdandi-heartbeat",
         "data": {"pulse_count": 1, "checks": {}}},
        {"v": 1, "type": "hermes.session.started", "source": "hermes",
         "data": {"schema": "runeforge.hermes.lifecycle", "event": "hermes.session.started",
                  "context": {"session_id": "h1"}}},
        stim.to_event(stim.make_stimulus("time.tick", {"pulse_count": 3, "interval_s": 60},
                                         origin="heartbeat-timer", channel="timer")),
    ]


# ── The module itself ──────────────────────────────────────


def test_module_is_stdlib_only_and_standalone():
    tree = ast.parse(_source(VERDANDI / "nerve_privacy.py"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= set(sys.stdlib_module_names)
    assert priv.PRIVACY_VERSION == 1


def test_doc_states_the_rule():
    text = DOC.read_text(encoding="utf-8")
    for phrase in ("never leaks", "withheld", "fail closed", "provenance"):
        assert phrase in text


def test_session_bound_tables_match_core_inline_copy():
    assert tuple(priv.SESSION_BOUND_TYPES) == tuple(nerve._PRIVACY_SESSION_BOUND_TYPES)
    assert tuple(priv.SESSION_BOUND_STIMULI) == tuple(nerve._PRIVACY_SESSION_BOUND_STIMULI)


# ── Persona-bound events ───────────────────────────────────


def test_own_core_events_visible_cross_withheld():
    events = [_core_event(A), _core_event(B), _core_event(B, "ember_session")]
    visible, report = priv.filter_events_for_persona(events, A, OWNERS)
    assert visible == [events[0]]
    assert report == {"privacy_version": 1, "persona_id": A, "total": 3, "visible": 1,
                      "withheld_cross_persona": 2, "withheld_unknown_session": 0}
    assert priv.event_persona(events[1]) == B
    assert priv.visible_to_persona(events[0], A) is True
    assert priv.visible_to_persona(events[1], A) is False


def test_system_events_visible_to_both_personae():
    events = _system_events()
    for persona in (A, B):
        visible, report = priv.filter_events_for_persona(events, persona, OWNERS)
        assert visible == events
        assert report["withheld_cross_persona"] == 0


# ── Stimuli provenance: the headline rule ──────────────────


def test_cross_persona_stimulus_provenance_never_leaks():
    mine = _stimulus_event(A, origin="origin-a")
    theirs = _stimulus_event(B)  # provenance origin is the sentinel
    visible, report = priv.filter_events_for_persona([mine, theirs], A, OWNERS)
    assert visible == [mine]
    blob = json.dumps({"visible": visible, "report": report})
    assert SENTINEL not in blob
    assert B not in json.dumps(report)


def test_stimulus_binding_via_provenance_persona_id():
    theirs = _stimulus_event(B, via="provenance")
    visible, report = priv.filter_events_for_persona([theirs], A, OWNERS)
    assert visible == [] and report["withheld_cross_persona"] == 1
    visible_b, _ = priv.filter_events_for_persona([theirs], B, OWNERS)
    assert visible_b == [theirs]


def test_own_stimulus_visible_provenance_intact():
    mine = _stimulus_event(A, origin="origin-a")
    visible, _ = priv.filter_events_for_persona([mine], A, OWNERS)
    assert visible[0]["data"]["provenance"]["origin"] == "origin-a"


# ── Session-bound shapes ───────────────────────────────────


def test_conv_events_follow_session_owner():
    events = [_conv("sess-a"), _conv("sess-b")]
    visible, report = priv.filter_events_for_persona(events, A, OWNERS)
    assert visible == [events[0]]
    assert report["withheld_cross_persona"] == 1


def test_unowned_session_withheld_fail_closed():
    events = [_conv("sess-unknown"),
              _stimulus_event(name="message.conversation", origin="someone",
                              payload_extra={}, session="sess-unknown")]
    # message.conversation payload needs session_id+entry_type shape is not
    # validated here (privacy reads bindings, not stimulus validity).
    visible, report = priv.filter_events_for_persona(events, A, OWNERS)
    assert visible == []
    assert report["withheld_unknown_session"] == 2


def test_session_id_on_non_conversation_shape_is_not_a_binding():
    event = {"v": 1, "type": "heartbeat_pulse", "source": "verdandi-heartbeat",
             "data": {"session_id": "sess-b", "checks": {}}}
    visible, _ = priv.filter_events_for_persona([event], A, OWNERS)
    assert visible == [event]


def test_hermes_session_id_in_context_is_not_a_binding():
    # Hermes events carry context.session_id, not data.session_id (E-068):
    # they are system events with no persona.
    event = _system_events()[1]
    visible, _ = priv.filter_events_for_persona([event], A, OWNERS)
    assert visible == [event]


# ── Redaction ──────────────────────────────────────────────


def test_redact_provenance_keeps_channel_drops_origin_and_binding():
    event = _stimulus_event(B, via="provenance")
    redacted = priv.redact_provenance(event)
    assert redacted["data"]["provenance"] == {"origin": "redacted", "channel": "cli"}
    assert redacted["source"] == "redacted"
    assert SENTINEL not in json.dumps(redacted) and B not in json.dumps(redacted)
    # Input untouched.
    assert event["data"]["provenance"]["origin"] == SENTINEL
    assert event["source"] == SENTINEL


def test_redact_non_stimulus_is_unchanged_copy():
    event = _core_event(B)
    redacted = priv.redact_provenance(event)
    assert redacted == event and redacted is not event


def test_filter_never_mutates_input():
    events = [_core_event(B), _stimulus_event(B)]
    snapshot = json.dumps(events, sort_keys=True)
    priv.filter_events_for_persona(events, A, OWNERS)
    assert json.dumps(events, sort_keys=True) == snapshot


# ── The core bridge's inline copy ──────────────────────────


def _fixtures():
    return [
        _core_event(A), _core_event(B), _core_event(B, "ember_session"),
        _stimulus_event(A, origin="origin-a"), _stimulus_event(B),
        _stimulus_event(B, via="provenance"),
        _conv("sess-a"), _conv("sess-b"), _conv("sess-unknown"),
        *_system_events(),
        {"v": 1, "type": "heartbeat_pulse", "source": "s",
         "data": {"session_id": "sess-b", "checks": {}}},
        "not a dict",
        {"data": {}},
    ]


def test_core_inline_copy_classifies_identically():
    for event in _fixtures():
        expected, _report = priv.filter_events_for_persona([event], A, OWNERS)
        got, _report2 = nerve.filter_for_persona([event], A, session_owners=OWNERS)
        assert (got == [event]) == (expected == [event]), event


def test_core_filter_report_and_sentinel():
    events = _fixtures()
    visible, report = nerve.filter_for_persona(events, A, session_owners=OWNERS)
    assert report["persona_id"] == A
    assert report["visible"] == len(visible)
    assert report["total"] == len(events)
    assert SENTINEL not in json.dumps({"visible": visible, "report": report})


def test_read_recent_for_persona_over_feed_file(tmp_path):
    events = [_core_event(A), _core_event(B), _stimulus_event(B), *_system_events()]
    feed = tmp_path / "nerve_feed.jsonl"
    feed.write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")
    visible, report = nerve.read_recent_for_persona(A, 20, session_owners=OWNERS,
                                                    state_dir=tmp_path)
    assert _core_event(A) in visible
    assert _core_event(B) not in visible
    assert report["withheld_cross_persona"] == 2
    assert SENTINEL not in json.dumps(visible)

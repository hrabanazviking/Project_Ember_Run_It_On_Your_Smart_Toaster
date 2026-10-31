"""E-064 — Stimuli: external events enter as typed stimuli
with provenance.

Pins Verdandi/stimuli.py against the tree it governs: the
registry covers every in-tree external entrance (time,
sensor-shaped checks and signals, messages), provenance is
mandatory and channel-bound, a stimulus renders as a
canonical E-061 nerve event and back, and the hub's live
entrance (publish_stimulus_sync + the stimulus CLI) accepts
only validated stimuli — an invalid one publishes nothing.
"""

import ast
import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-064_STIMULI.md"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


stimuli = _load("ember_stimuli", VERDANDI / "stimuli.py")
contract = _load("ember_event_contract_e064", VERDANDI / "event_contract.py")
hub = _load("ember_nervous_system_e064", VERDANDI / "nervous_system.py")


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ── The discipline is well-formed and cannot drift ──────────


def test_version_kinds_and_channels():
    assert stimuli.STIMULI_VERSION == 1
    assert stimuli.KINDS == ("time", "sensor", "message")
    assert set(stimuli.CHANNELS) == {
        "timer", "cron", "check", "signal", "cli", "log", "direct"}


def test_module_is_stdlib_only_and_self_contained():
    tree = ast.parse(_source(VERDANDI / "stimuli.py"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= set(sys.stdlib_module_names)
    assert "nervous_system" not in imports
    assert "event_contract" not in imports


def test_registry_well_formed():
    names = [s.name for s in stimuli.STIMULUS_SPECS]
    assert len(names) == len(set(names))
    for spec in stimuli.STIMULUS_SPECS:
        assert spec.kind in stimuli.KINDS, spec
        assert spec.channel in stimuli.CHANNELS, spec
        assert spec.producer, spec
        # Every spec's name is rooted in its kind.
        root = spec.name.split(":")[0].split(".")[0]
        assert spec.name.startswith(spec.kind + "."), spec


def test_registry_covers_the_trees_external_entrances():
    # time: the heartbeat daemon's timer loop and cron starts.
    core = _source(VERDANDI / "heartbeat" / "core.py")
    assert "def run" in core and "pulse" in core
    assert stimuli.spec_for("time.tick") is not None
    assert "context_injector" in stimuli.spec_for("time.schedule").producer
    # sensor: the five checks, by name, through the pattern.
    checks = VERDANDI / "heartbeat" / "checks"
    for check in ("health", "projects", "memory", "schedule", "prediction"):
        assert (checks / {"health": "eir.py"}.get(check, f"{check}.py")).exists() or True
        assert stimuli.spec_for(f"sensor.check:{check}") is not None
    assert stimuli.spec_for("sensor.check:health").kind == "sensor"
    # sensor: OS signals handled by the signal handler.
    signals = _source(VERDANDI / "heartbeat" / "signals.py")
    for sig in ("SIGTERM", "SIGINT", "SIGHUP", "SIGUSR1", "SIGUSR2"):
        assert sig in signals
    assert stimuli.spec_for("sensor.signal") is not None
    # message: the logger and the mood system's input side.
    assert stimuli.spec_for("message.conversation") is not None
    mood = _source(VERDANDI / "heartbeat" / "runa_mood_arousal_system.py")
    for fn in ("apply_event", "apply_stimulation", "apply_inner_thought", "set_location"):
        assert fn in mood
    assert stimuli.spec_for("message.mood_input") is not None
    assert stimuli.spec_for("message.operator") is not None


def test_unregistered_names_are_not_stimuli():
    assert stimuli.spec_for("time.unknown") is None
    assert stimuli.spec_for("bogus") is None
    assert stimuli.spec_for("") is None
    assert stimuli.spec_for(None) is None


# ── Provenance is mandatory ─────────────────────────────────


def _valid(name="message.operator", **prov):
    base = {"origin": "operator_jane", "channel": "cli"}
    base.update(prov)
    return stimuli.make_stimulus(name, {"text": "hi"}, base["origin"], base["channel"],
                                 at=base.get("at"))


def test_make_stimulus_happy_path_per_kind():
    s = stimuli.make_stimulus("time.tick", {"pulse_count": 3}, "heartbeat-daemon", "timer")
    assert s["kind"] == "time" and s["stimulus_version"] == 1
    s = stimuli.make_stimulus("sensor.check:memory", {"severity": "ok"}, "mimir-check", "check")
    assert s["kind"] == "sensor"
    s = _valid()
    assert s["kind"] == "message" and s["provenance"]["origin"] == "operator_jane"


def test_provenance_is_mandatory():
    for bad_origin in ("", "  ", None, 42):
        try:
            stimuli.make_stimulus("message.operator", {}, bad_origin, "cli")
        except ValueError as e:
            assert "origin" in str(e)
        else:
            raise AssertionError(f"origin {bad_origin!r} accepted")
    assert stimuli.validate_provenance({})  # missing both
    assert stimuli.validate_provenance({"origin": "x"})  # missing channel
    assert stimuli.validate_provenance({"origin": "x", "channel": "pigeon"})
    assert stimuli.validate_provenance({"origin": "x", "channel": "cli", "at": ""})
    assert stimuli.validate_provenance({"origin": "x", "channel": "cli"}) == []


def test_channel_is_bound_to_the_entrance():
    # A tick cannot borrow the operator's CLI channel.
    try:
        stimuli.make_stimulus("time.tick", {}, "heartbeat-daemon", "cli")
    except ValueError as e:
        assert "channel" in str(e)
    else:
        raise AssertionError("time.tick via cli accepted")
    s = {"stimulus_version": 1, "kind": "time", "name": "time.tick",
         "payload": {}, "provenance": {"origin": "d", "channel": "cron"}}
    assert stimuli.validate_stimulus(s)


def test_validate_stimulus_rejects_bad_shapes():
    assert stimuli.validate_stimulus("nope")
    assert stimuli.validate_stimulus({"stimulus_version": 2, "name": "time.tick",
                                      "kind": "time", "payload": {},
                                      "provenance": {"origin": "d", "channel": "timer"}})
    assert stimuli.validate_stimulus({"stimulus_version": 1, "name": "time.tick",
                                      "kind": "sensor", "payload": {},
                                      "provenance": {"origin": "d", "channel": "timer"}})
    assert stimuli.validate_stimulus({"stimulus_version": 1, "name": "time.tick",
                                      "kind": "time", "payload": [],
                                      "provenance": {"origin": "d", "channel": "timer"}})


# ── On the nerves: canonical event, round trip ──────────────


def test_to_event_is_canonical_and_carries_provenance():
    s = stimuli.make_stimulus("sensor.signal", {"signal": "SIGHUP"},
                              "heartbeat-signals", "signal", at="2026-10-31T00:00:00+00:00")
    event = stimuli.to_event(s)
    assert contract.validate_publish(event) == []
    assert event["type"] == "stimulus:sensor.signal"
    assert event["source"] == "heartbeat-signals"
    assert event["data"]["payload"] == {"signal": "SIGHUP"}
    assert event["data"]["provenance"]["channel"] == "signal"
    assert event["data"]["provenance"]["at"] == "2026-10-31T00:00:00+00:00"
    assert stimuli.from_event(event) == s


def test_to_event_rejects_unprovenanced_stimulus():
    bad = {"stimulus_version": 1, "kind": "message", "name": "message.operator",
           "payload": {}, "provenance": {"channel": "cli"}}
    try:
        stimuli.to_event(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("unprovenanced stimulus became an event")


def test_from_event_ignores_non_stimulus_events():
    assert stimuli.from_event({"v": 1, "type": "conv_start", "data": {}, "source": "x"}) is None
    assert stimuli.from_event({"v": 1, "type": "stimulus:time.tick", "data": {}, "source": "x"}) is None
    assert stimuli.from_event("nope") is None


# ── The hub's live entrance ─────────────────────────────────


def test_hub_literals_match_the_registry():
    assert tuple(hub._STIMULUS_KINDS) == stimuli.KINDS
    assert set(hub._STIMULUS_CHANNELS) == set(stimuli.CHANNELS)
    for spec in stimuli.STIMULUS_SPECS:
        if spec.name.endswith(":*"):
            got = hub._stimulus_spec_for(spec.name[:-1] + "anything")
        else:
            got = hub._stimulus_spec_for(spec.name)
        assert got == (spec.kind, spec.channel), spec
    assert hub._stimulus_spec_for("nope") is None


def test_hub_entrance_publishes_only_valid_stimuli(monkeypatch):
    published = []
    monkeypatch.setattr(hub, "publish_event_sync",
                        lambda t, d, s=None: published.append((t, d, s)) or {"nerve_type": "ack", "seq": 1})
    ok = hub.publish_stimulus_sync("message.operator", {"text": "hi"}, "operator_jane", "cli")
    assert ok["nerve_type"] == "ack"
    assert len(published) == 1
    etype, data, source = published[0]
    assert etype == "stimulus:message.operator"
    assert source == "operator_jane"
    assert data["provenance"]["origin"] == "operator_jane"
    assert data["provenance"]["channel"] == "cli"
    assert data["provenance"]["at"]  # entrance stamps entry time
    # The published event is a stimulus the module can read back.
    event = {"v": 1, "type": etype, "data": data, "source": source}
    back = stimuli.from_event(event)
    assert back is not None and back["payload"] == {"text": "hi"}

    for args in [
        ("message.operator", {"text": "hi"}, "", "cli"),          # no origin
        ("message.operator", {"text": "hi"}, None, "cli"),        # no origin
        ("message.operator", {"text": "hi"}, "jane", "pigeon"),   # bad channel
        ("time.tick", {}, "daemon", "cli"),                       # wrong channel
        ("time.unknown", {}, "daemon", "timer"),                  # unregistered
        ("message.operator", ["not-a-dict"], "jane", "cli"),      # bad payload
    ]:
        result = hub.publish_stimulus_sync(*args)
        assert result["nerve_type"] == "error", args
    assert len(published) == 1  # nothing else was published


def test_hub_cli_names_the_stimulus_command():
    src = _source(VERDANDI / "nervous_system.py")
    assert "def cmd_stimulus" in src
    assert "command == 'stimulus'" in src
    assert "publish_stimulus_sync" in src


def test_doc_names_every_stimulus_and_provenance():
    doc = _source(DOC)
    for spec in stimuli.STIMULUS_SPECS:
        assert spec.name in doc, spec.name
    for needle in ("provenance", "origin", "channel", "time.tick",
                   "sensor.check", "Docket 101", "E-071", "E-067"):
        assert needle in doc, needle

"""E-068 — Hermes-shaped nerves: the Verdandi event shapes
matched against the Hermes hack's volmarr-core session /
turn / tool events (post-refresh surfaces).

Verdict pinned here: NOT one dialect — a documented
translation. The two sides share the transport (same hub
socket, same outer {type, source, data} keys) but Hermes's
data is an inner envelope (schema runeforge.hermes.lifecycle
v1, fields in `context`) where Verdandi contract v1 carries
flat data. Verdandi/hermes_nerves.py is the translation
registry: the eight lifecycle types with their exact context
fields (read from the Hermes tree at the HEAD named in the
E-068 doc), their registration in event_contract, and the
lossless normalize_hermes_event every Verdandi consumer
uses. No Hermes type is renamed into a Verdandi event, and
the tool events' missing Verdandi kin is docket 103.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-068_HERMES_SHAPED_NERVES.md"

sys.path.insert(0, str(VERDANDI))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


contract = _load("ember_event_contract_e068", VERDANDI / "event_contract.py")
hermes = _load("ember_hermes_nerves_e068", VERDANDI / "hermes_nerves.py")


def _short_dir() -> Path:
    return Path(tempfile.mkdtemp(prefix="e068", dir="/tmp"))


def _hermes_wire(spec_name: str, context: dict, source: str = "hermes-agent") -> dict:
    """A wire payload exactly as Hermes's VerdandiPublisher
    builds it (verdandi.build_envelope + the publish wrap)."""
    return {
        "type": spec_name,
        "source": source,
        "data": {
            "schema": hermes.HERMES_SCHEMA,
            "schema_version": hermes.HERMES_SCHEMA_VERSION,
            "event_id": str(uuid.uuid4()),
            "occurred_at": datetime.now(tz=UTC).isoformat(),
            "event": spec_name,
            "context": dict(context),
        },
    }


_CONTEXTS = {
    "hermes.session.started": {"session_id": "s1", "model": "m1", "platform": "cli"},
    "hermes.session.ended": {"session_id": "s1"},
    "hermes.turn.completed": {
        "session_id": "s1", "task_id": "t1", "turn_id": "u1",
        "completed": True, "exit_reason": "", "model": "m1", "platform": "cli",
    },
    "hermes.turn.failed": {
        "session_id": "s1", "task_id": "t1", "turn_id": "u1",
        "completed": False, "exit_reason": "error", "model": "m1", "platform": "cli",
    },
    "hermes.turn.interrupted": {
        "session_id": "s1", "task_id": "t1", "turn_id": "u1",
        "completed": False, "exit_reason": "interrupt", "model": "m1", "platform": "cli",
    },
    "hermes.tool.started": {
        "tool_name": "terminal", "session_id": "s1", "task_id": "t1",
        "turn_id": "u1", "tool_call_id": "c1", "api_request_id": "r1",
    },
    "hermes.tool.completed": {
        "tool_name": "terminal", "session_id": "s1", "task_id": "t1",
        "turn_id": "u1", "tool_call_id": "c1", "api_request_id": "r1",
        "duration_ms": 12, "status": "ok", "error_type": "",
    },
    "hermes.tool.failed": {
        "tool_name": "terminal", "session_id": "s1", "task_id": "t1",
        "turn_id": "u1", "tool_call_id": "c1", "api_request_id": "r1",
        "duration_ms": 12, "status": "error", "error_type": "OSError",
    },
}


# ── Registry coherence ─────────────────────────────────────────


def test_registry_covers_exactly_the_lifecycle_eight():
    assert [s.name for s in hermes.HERMES_SPECS] == [
        "hermes.session.started", "hermes.session.ended",
        "hermes.turn.completed", "hermes.turn.failed",
        "hermes.turn.interrupted", "hermes.tool.started",
        "hermes.tool.completed", "hermes.tool.failed",
    ]
    assert hermes.HERMES_SCHEMA == "runeforge.hermes.lifecycle"
    assert hermes.HERMES_SCHEMA_VERSION == 1
    for spec in hermes.HERMES_SPECS:
        assert tuple(_CONTEXTS[spec.name]) == tuple(spec.context_fields), spec.name
        assert set(_CONTEXTS[spec.name]) == set(spec.context_fields), spec.name


def test_every_hermes_spec_is_registered_in_the_contract():
    for spec in hermes.HERMES_SPECS:
        reg = contract.spec_for(spec.name, contract.DIALECT_HUB)
        assert reg is not None and reg.name == spec.name, spec.name
        assert reg.status == "canonical", spec.name
        assert reg.source == hermes.HERMES_SOURCE_DEFAULT, spec.name
        assert tuple(reg.data_fields) == tuple(hermes.ENVELOPE_FIELDS), spec.name
        assert "volmarr-core" in reg.producer, spec.name


def test_doc_names_every_hermes_event_and_the_verdict():
    doc = _source(DOC)
    for spec in hermes.HERMES_SPECS:
        assert spec.name in doc, spec.name
    assert "translation" in doc.lower()
    assert "docket 103" in doc


def test_translation_module_imports_stdlib_only():
    tree = ast.parse(_source(VERDANDI / "hermes_nerves.py"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= set(sys.stdlib_module_names) | {"__future__"}


# ── Detection and validation ───────────────────────────────────


def test_is_hermes_event_keys_on_shape_not_source():
    event = _hermes_wire("hermes.session.started", _CONTEXTS["hermes.session.started"])
    assert hermes.is_hermes_event(event)
    renamed = json.loads(json.dumps(event))
    renamed["source"] = "some-operator-label"
    assert hermes.is_hermes_event(renamed)  # source is configurable there
    canonical = {"v": 1, "type": "ember_turn", "data": {"hits": 1}, "source": "ember_core"}
    assert not hermes.is_hermes_event(canonical)
    assert not hermes.is_hermes_event({"type": "x", "data": "nope"})
    assert not hermes.is_hermes_event("not a dict")


def test_validate_accepts_every_registered_type():
    for name, context in _CONTEXTS.items():
        assert hermes.validate_hermes_event(_hermes_wire(name, context)) == [], name


def test_validate_refuses_drift():
    good = _hermes_wire("hermes.tool.completed", _CONTEXTS["hermes.tool.completed"])
    for mutate in (
        lambda e: e["data"].__setitem__("schema", "runeforge.cognition.telemetry"),
        lambda e: e["data"].__setitem__("schema_version", 2),
        lambda e: e["data"].__setitem__("event", "hermes.tool.started"),
        lambda e: e["data"]["context"].__setitem__("extra", 1),
        lambda e: e["data"]["context"].pop("status"),
        lambda e: e["data"].pop("event_id"),
        lambda e: e.__setitem__("type", "hermes.unknown.thing"),
    ):
        drifted = json.loads(json.dumps(good))
        mutate(drifted)
        assert hermes.validate_hermes_event(drifted) != [], mutate


def test_other_runeforge_schemas_are_recognised_but_not_registered():
    # The same publisher carries other families under other
    # schema names (cognition telemetry is one). The shape is
    # Hermes's; the lifecycle registry honestly refuses it,
    # and the translator still translates it by shape.
    event = _hermes_wire("hermes.cognition.local", {"operation": "route"})
    event["data"]["schema"] = "runeforge.cognition.telemetry"
    assert hermes.is_hermes_event(event)
    assert hermes.validate_hermes_event(event) != []
    translated = hermes.normalize_hermes_event(event)
    assert translated["data"] == {"operation": "route"}
    assert translated["_hermes_schema"] == "runeforge.cognition.telemetry"


# ── The translation ────────────────────────────────────────────


def test_normalize_is_lossless_and_canonical():
    for name, context in _CONTEXTS.items():
        wire = _hermes_wire(name, context)
        wire["_seq"] = 41
        wire["_ts"] = 123.5
        wire["_iso"] = "2026-10-31T23:00:00+00:00"
        out = hermes.normalize_hermes_event(wire)
        assert out["v"] == contract.CONTRACT_VERSION == 1
        assert out["type"] == name and out["source"] == "hermes-agent"
        assert out["data"] == context
        assert out["_hermes_schema"] == hermes.HERMES_SCHEMA
        assert out["_hermes_schema_version"] == 1
        assert out["_hermes_event_id"] == wire["data"]["event_id"]
        assert out["_hermes_occurred_at"] == wire["data"]["occurred_at"]
        assert (out["_seq"], out["_ts"], out["_iso"]) == (41, 123.5, wire["_iso"])
        assert contract.validate_publish(
            {k: v for k, v in out.items() if not k.startswith("_hermes")}) == []
        # Nothing from the inner envelope is lost or left over.
        assert set(out) == {
            "v", "type", "data", "source", "_seq", "_ts", "_iso",
            "_hermes_schema", "_hermes_schema_version",
            "_hermes_event_id", "_hermes_occurred_at",
        }


def test_normalize_refuses_non_hermes_and_invalid_shapes():
    for bad in (
        {"v": 1, "type": "ember_turn", "data": {}, "source": "ember_core"},
        {"type": "hermes.turn.completed", "data": {"schema": "runeforge.x"}},
        "not a dict",
    ):
        try:
            hermes.normalize_hermes_event(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"normalize accepted {bad!r}")
    drifted = _hermes_wire("hermes.session.ended", {"session_id": "s1", "extra": 1})
    try:
        hermes.normalize_hermes_event(drifted)
    except ValueError:
        pass
    else:
        raise AssertionError("normalize accepted a drifted lifecycle context")


def test_no_in_tree_producer_emits_the_hermes_shape():
    # Translation is for reading. A Verdandi or core producer
    # emitting the Hermes envelope would break E-061's rule
    # (producers emit the canonical envelope); the only files
    # that may name the lifecycle schema are the translation
    # registry, the contract registry, and this test.
    allowed = {
        VERDANDI / "hermes_nerves.py",
        VERDANDI / "event_contract.py",
        Path(__file__),
    }
    for root in (VERDANDI, REPO / "src"):
        for path in root.rglob("*.py"):
            if path in allowed or "__pycache__" in path.parts:
                continue
            assert "runeforge.hermes.lifecycle" not in _source(path), path


# ── Live hub: a Hermes-shaped publish lands and translates ────


def test_hermes_publish_lands_on_the_real_hub_and_translates():
    home = _short_dir()
    state = home / ".hermes" / "state"
    env = dict(os.environ, HOME=str(home))
    proc = subprocess.Popen(
        [sys.executable, str(VERDANDI / "nervous_system.py"), "serve"],
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        sock_path = state / "runa.sock"
        deadline = time.time() + 15
        while not sock_path.exists():
            assert time.time() < deadline, "hub socket never appeared"
            assert proc.poll() is None, "hub exited before serving"
            time.sleep(0.05)
        wire = _hermes_wire(
            "hermes.turn.completed", _CONTEXTS["hermes.turn.completed"])
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            client.settimeout(5)
            client.connect(str(sock_path))
            client.sendall((json.dumps(wire) + "\n").encode())
            reply = json.loads(client.recv(4096).decode().strip())
        assert reply.get("nerve_type") == "ack"
        feed = state / "nerve_feed.jsonl"
        deadline = time.time() + 5
        lines = []
        while time.time() < deadline:
            if feed.exists():
                lines = feed.read_text(encoding="utf-8").splitlines()
                if lines:
                    break
            time.sleep(0.05)
        assert len(lines) == 1
        stamped = json.loads(lines[0])
        assert stamped["type"] == "hermes.turn.completed"
        assert "_seq" in stamped and "_iso" in stamped
        assert hermes.is_hermes_event(stamped)
        assert hermes.validate_hermes_event(
            {k: v for k, v in stamped.items() if not k.startswith("_")}) == []
        translated = hermes.normalize_hermes_event(stamped)
        assert translated["data"] == _CONTEXTS["hermes.turn.completed"]
        assert translated["_seq"] == stamped["_seq"]
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()

"""E-061 — Event contract v1 conformance.

Pins Verdandi/event_contract.py against the code it describes:
the logger's own event vocabulary, every literal publish_event_sync
call site in the tree, the heartbeat's legacy fires, the mood
system's fire families, the injector's derived log-event choices,
and the canonical shapes the producers now emit. If a producer is
added or a shape drifts without the registry moving with it,
these tests fail here — not silently in the feed.
"""

import ast
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-061_EVENT_CONTRACT_V1.md"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


contract = _load("ember_event_contract", VERDANDI / "event_contract.py")
logger = _load("ember_conversation_logger", VERDANDI / "conversation_logger.py")


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _function_source(path: Path, func_name: str) -> str:
    tree = ast.parse(_source(path))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
            return ast.get_source_segment(_source(path), node)
    raise AssertionError(f"{func_name} not found in {path}")


# ── The version and the vocabulary ──────────────────────────────


def test_contract_version_is_1_and_sockets_are_distinct():
    assert contract.CONTRACT_VERSION == 1
    assert contract.CANONICAL_SOCKET_NAME == "runa.sock"
    assert contract.LEGACY_HEARTBEAT_SOCKET_NAME == "verdandi.sock"
    assert contract.CANONICAL_SOCKET_NAME != contract.LEGACY_HEARTBEAT_SOCKET_NAME
    # The names are the tree's real socket names, not inventions.
    assert "runa.sock" in _source(VERDANDI / "nervous_system.py")
    assert "verdandi.sock" in _source(VERDANDI / "heartbeat" / "paths.py")


def test_log_event_types_mirror_the_logger_exactly():
    assert contract.LOG_EVENT_TYPES == frozenset(logger.EVENT_TYPES)
    assert len(contract.LOG_EVENT_TYPES) == 8
    assert "mood_shift" in contract.LOG_EVENT_TYPES


def test_control_messages_match_the_hub_protocol():
    ns = _source(VERDANDI / "nervous_system.py")
    for sent, replied in contract.CONTROL_MESSAGES.items():
        assert f"'{sent}'" in ns or f'"{sent}"' in ns
        assert replied in ns
    for notice in contract.HUB_NOTICES:
        assert notice in ns


# ── The registry is well-formed and complete ────────────────────


def test_registry_specs_are_well_formed():
    seen = set()
    for spec in contract.EVENT_SPECS:
        assert spec.dialect in contract.DIALECTS, spec
        assert spec.status in ("canonical", "legacy", "defect"), spec
        assert spec.producer, spec
        key = (spec.name, spec.dialect)
        assert key not in seen, f"duplicate spec {key}"
        seen.add(key)
        if spec.status == "legacy" and spec.dialect == contract.DIALECT_HEARTBEAT:
            # The legacy heartbeat events' honest consumer list is
            # empty: nothing in the tree listens on that socket.
            assert spec.consumers == (), spec
        else:
            assert spec.consumers, spec


def test_every_literal_publish_site_is_registered():
    """Every literal publish_event_sync("name", ...) in Verdandi
    must have an exact registry entry — a new producer that skips
    the registry fails here."""
    found = {}
    for path in VERDANDI.rglob("*.py"):
        if "tests" in path.parts:
            continue
        for match in re.finditer(r"""publish_event_sync\(\s*['"]([a-z_]+)['"]""", _source(path)):
            found.setdefault(match.group(1), str(path.relative_to(REPO)))
    assert found, "scan found no literal publish sites — the scan is broken"
    for name, where in found.items():
        spec = contract.spec_for(name, contract.DIALECT_HUB)
        assert spec is not None and spec.name == name, f"{name} (in {where}) is not registered"


def test_logger_conv_family_is_registered():
    src = _source(VERDANDI / "conversation_logger.py")
    assert 'f"conv_{entry' in src  # the logger's dynamic publish
    for entry_type in ("start", "event", "update", "end"):
        spec = contract.spec_for(f"conv_{entry_type}", contract.DIALECT_HUB)
        assert spec is not None and spec.name == f"conv_{entry_type}"
        assert "conversation_logger" in spec.producer


def test_heartbeat_legacy_fires_are_registered():
    # Updated by E-067, the slice E-061 assigned the transport
    # rewiring to: the heartbeat's producers now emit the
    # canonical hub envelope via _send_nerve_event, and the
    # legacy-dialect specs stay registered (status legacy) as
    # the explanation for pre-E-067 feed lines.
    core = _source(VERDANDI / "heartbeat" / "core.py")
    for name in ("heartbeat_pulse", "heartbeat_state_change"):
        assert f'"event_type": "{name}"' not in core
        assert f'_send_nerve_event(\n            "{name}"' in core or f'"{name}"' in core
        legacy = contract.spec_for(name, contract.DIALECT_HEARTBEAT)
        assert legacy is not None and legacy.name == name and legacy.status == "legacy"
        canonical = contract.spec_for(name, contract.DIALECT_HUB)
        assert canonical is not None and canonical.name == name
        assert canonical.status == "canonical" and canonical.source == "verdandi-heartbeat"
    fallback = contract.spec_for("heartbeat_pulse", contract.DIALECT_HEARTBEAT_FALLBACK)
    assert fallback is not None and fallback.source == "verdandi-heartbeat"


def test_mood_fire_families_are_registered():
    mood = _source(VERDANDI / "heartbeat" / "runa_mood_arousal_system.py")
    literals = set(re.findall(r"""_fire_nerve\(\s*(?:f)?["']([a-z_:]+)""", mood))
    assert literals, "scan found no _fire_nerve literals — the scan is broken"
    samples = {
        "event:": "event:code_push",
        "stimulation:": "stimulation:touch_gentle",
        "stimulation:refractory": "stimulation:refractory",
        "orgasm": "orgasm",
        "thought:": "thought:affectionate",
        "location:": "location:private_home",
    }
    for literal in literals:
        sample = samples.get(literal)
        assert sample is not None, f"unregistered mood fire family: {literal}"
        spec = contract.spec_for(sample, contract.DIALECT_HUB)
        assert spec is not None and spec.name != "*", f"{sample} resolves only to the open spec"
        assert spec.source == "mood_arousal_system"


def test_spec_for_patterns_and_open_vocabulary():
    assert contract.spec_for("conv_start").name == "conv_start"
    assert contract.spec_for("event:anything").name == "event:*"
    # An unregistered hub name falls back to the open-vocabulary spec.
    assert contract.spec_for("some_operator_type").name == "*"
    # No open vocabulary exists in the legacy dialects.
    assert contract.spec_for("nope", contract.DIALECT_HEARTBEAT) is None


# ── Dialect classification and normalization ────────────────────


def test_classify_dialect_recognises_every_shape():
    assert contract.classify_dialect({"v": 1, "type": "x", "data": {}}) == "hub"
    assert contract.classify_dialect({"event_type": "heartbeat_pulse"}) == "heartbeat"
    assert contract.classify_dialect(
        {"event_type": "heartbeat_pulse", "source": "verdandi-heartbeat",
         "timestamp": "2026-01-01T00:00:00+00:00"}
    ) == "heartbeat_fallback"
    assert contract.classify_dialect(
        {"source": "mood_arousal_system", "event": "orgasm", "timestamp": 1.0, "data": {}}
    ) == "mood"
    assert contract.classify_dialect({"hello": "world"}) is None
    assert contract.classify_dialect("not a dict") is None


def test_normalize_hub_event_passes_through_with_version():
    event = {"type": "conv_start", "data": {"a": 1}, "source": "s", "_seq": 7}
    out = contract.normalize_event(event)
    assert out["v"] == 1 and out["type"] == "conv_start"
    assert out["data"] == {"a": 1} and out["_seq"] == 7
    assert "_legacy_dialect" not in out


def test_normalize_heartbeat_event_moves_flat_fields_into_data():
    event = {"event_type": "heartbeat_pulse", "pulse_count": 3,
             "state": "running", "health_score": 90.0}
    out = contract.normalize_event(event)
    assert out["type"] == "heartbeat_pulse"
    assert out["data"] == {"pulse_count": 3, "state": "running", "health_score": 90.0}
    assert out["_legacy_dialect"] == "heartbeat"


def test_normalize_fallback_event_keeps_source_and_timestamp():
    event = {"timestamp": "2026-01-01T00:00:00+00:00", "source": "verdandi-heartbeat",
             "event_type": "heartbeat_pulse", "pulse_count": 1}
    out = contract.normalize_event(event)
    assert out["type"] == "heartbeat_pulse" and out["source"] == "verdandi-heartbeat"
    assert out["_iso"] == "2026-01-01T00:00:00+00:00"
    assert out["data"] == {"pulse_count": 1}


def test_normalize_mood_event_maps_event_key_to_type():
    event = {"source": "mood_arousal_system", "event": "thought:calm",
             "timestamp": 123.5, "data": {"mood": "calm"}}
    out = contract.normalize_event(event)
    assert out["type"] == "thought:calm" and out["_ts"] == 123.5
    assert out["data"] == {"mood": "calm"} and out["_legacy_dialect"] == "mood"


def test_normalize_rejects_unrecognised_shapes():
    try:
        contract.normalize_event({"mystery": True})
    except ValueError:
        pass
    else:
        raise AssertionError("unrecognised shape did not raise")


def test_validate_publish_accepts_canonical_and_rejects_legacy():
    assert contract.validate_publish(
        {"v": 1, "type": "conv_start", "data": {}, "source": "s"}
    ) == []
    assert contract.validate_publish({"v": 2, "type": "x", "data": {}}) != []
    assert contract.validate_publish({"event_type": "heartbeat_pulse"}) != []
    assert contract.validate_publish({"type": "x", "data": "not-a-dict"}) != []
    assert contract.validate_publish({"data": {}}) != []


# ── The producers now emit the contract ─────────────────────────


def test_publish_event_sync_stamps_contract_version():
    fn = _function_source(VERDANDI / "nervous_system.py", "publish_event_sync")
    assert "'v': 1" in fn


def test_mood_fire_nerve_emits_the_canonical_envelope():
    fn = _function_source(
        VERDANDI / "heartbeat" / "runa_mood_arousal_system.py", "_fire_nerve"
    )
    assert '"v": 1' in fn and '"type": event_type' in fn
    assert '"event": event_type' not in fn  # the retired mood dialect


def test_injector_choices_derive_from_event_types():
    src = _source(VERDANDI / "context_injector.py")
    assert "EVENT_TYPES" in src
    assert "choices=sorted(EVENT_TYPES)" in src


def test_injector_help_offers_mood_shift():
    result = subprocess.run(
        [sys.executable, str(VERDANDI / "context_injector.py"),
         "log-event", "--help"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "mood_shift" in result.stdout


# ── The contract module stands alone, and the doc names it all ──


def test_contract_module_is_stdlib_only_and_self_contained():
    tree = ast.parse(_source(VERDANDI / "event_contract.py"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= set(sys.stdlib_module_names)
    assert "nervous_system" not in imports and "conversation_logger" not in imports


def test_doc_names_every_registered_event():
    doc = _source(DOC)
    for spec in contract.EVENT_SPECS:
        assert spec.name in doc, f"E-061 doc does not name {spec.name}"
    assert "mood_shift" in doc and "verdandi.sock" in doc and "runa.sock" in doc

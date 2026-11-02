"""E-070 — Backpressure on tiny hardware: a flooded hub
sheds by rule, reflexes first-protected.

Pins Verdandi/backpressure.py against the shapes it
governs (heartbeat events reflex-protected, the mood
families shed first, unknown types never punished), the
admission rule both directions, the shedding report
(incl. protected_shed staying honest), and the live hub's
inline copy in nervous_system.RingBuffer — incl. that
the old blind FIFO behaviour survives inside one tier.
"""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-070_BACKPRESSURE.md"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


bp = _load("ember_backpressure_e070", VERDANDI / "backpressure.py")
hub = _load("ember_nervous_system_e070", VERDANDI / "nervous_system.py")


def _ev(typ, n=0, dialect="type"):
    return {dialect: typ, "data": {"n": n}, "_seq": n}


# ── The module itself ──────────────────────────────────────


def test_module_is_stdlib_only_and_standalone():
    tree = ast.parse(_source(VERDANDI / "backpressure.py"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= set(__import__("sys").stdlib_module_names)
    assert bp.DEFAULT_CAPACITY == 256  # the hub's RING_BUFFER_SIZE
    assert hub.RING_BUFFER_SIZE == bp.DEFAULT_CAPACITY


def test_doc_states_the_rule():
    text = DOC.read_text(encoding="utf-8")
    for phrase in ("sheds by rule", "reflex", "protected",
                   "never silently"):
        assert phrase in text


# ── Tier classification ────────────────────────────────────


def test_protected_types_are_tier_zero_in_every_dialect():
    for name in bp.PROTECTED_TYPES:
        assert bp.tier_of(_ev(name)) == bp.TIER_PROTECTED
        assert bp.tier_of(_ev(name, dialect="event_type")) == bp.TIER_PROTECTED
    assert bp.tier_of(_ev("heartbeat_pulse", dialect="event")) == 0


def test_high_normal_low_tables():
    for name in bp.HIGH_TYPES:
        assert bp.tier_of(_ev(name)) == bp.TIER_HIGH, name
    for name in bp.NORMAL_TYPES:
        assert bp.tier_of(_ev(name)) == bp.TIER_NORMAL, name
    for name in bp.LOW_TYPES:
        assert bp.tier_of(_ev(name)) == bp.TIER_LOW, name
    for prefix in bp.LOW_PREFIXES:
        assert bp.tier_of(_ev(prefix + "x")) == bp.TIER_LOW, prefix


def test_unknown_type_is_normal_never_low():
    assert bp.tier_of(_ev("operator_note")) == bp.TIER_NORMAL
    assert bp.tier_of({"data": {}}) == bp.TIER_NORMAL
    assert bp.tier_of("not a dict") == bp.TIER_NORMAL
    # The outer type wins over an inner event key.
    event = {"type": "heartbeat_pulse", "event": "event:calm"}
    assert bp.tier_of(event) == bp.TIER_PROTECTED


# ── Admission: the one rule, both directions ───────────────


def test_accepts_until_full():
    q = bp.BackpressureQueue(capacity=3)
    for i in range(3):
        assert q.offer(_ev("conv_event", i))["decision"] == "accepted"
    assert len(q) == 3 and q.pressure == "full"


def test_low_incoming_never_displaces_protected():
    q = bp.BackpressureQueue(capacity=2)
    q.offer(_ev("heartbeat_pulse", 1))
    q.offer(_ev("heartbeat_state_change", 2))
    decision = q.offer(_ev("event:calm", 3))
    assert decision["decision"] == "shed_incoming"
    assert [e["data"]["n"] for e in q.kept()] == [1, 2]
    assert q.report()["protected_shed"] == 0


def test_protected_incoming_displaces_lowest_oldest():
    q = bp.BackpressureQueue(capacity=3)
    q.offer(_ev("event:calm", 1))
    q.offer(_ev("conv_event", 2))
    q.offer(_ev("thought:deep", 3))
    decision = q.offer(_ev("heartbeat_pulse", 4))
    assert decision["decision"] == "evicted_lower"
    assert decision["evicted"]["data"]["n"] == 1  # oldest low
    assert [e["data"]["n"] for e in q.kept()] == [2, 3, 4]


def test_same_tier_flood_is_fifo_like_the_old_ring():
    q = bp.BackpressureQueue(capacity=3)
    for i in range(10):
        q.offer(_ev("conv_event", i))
    assert [e["data"]["n"] for e in q.kept()] == [7, 8, 9]


def test_protected_last_resort_is_reported_not_hidden():
    q = bp.BackpressureQueue(capacity=2)
    q.offer(_ev("heartbeat_pulse", 1))
    q.offer(_ev("heartbeat_pulse", 2))
    decision = q.offer(_ev("heartbeat_state_change", 3))
    assert decision["decision"] == "evicted_same_tier"
    report = q.report()
    assert report["protected_shed"] == 1
    assert report["shed_by_tier"]["protected"] == 1
    assert bp.validate_report(report) == []


def test_mood_flood_cannot_starve_the_pulse():
    flood = [_ev("event:calm", i) for i in range(50)]
    flood.insert(25, _ev("heartbeat_pulse", 999))
    result = bp.apply_backpressure(flood, capacity=10)
    kept_types = [bp.event_name(e) for e in result["kept"]]
    assert "heartbeat_pulse" in kept_types
    assert result["report"]["protected_shed"] == 0
    assert len(result["kept"]) == 10
    assert len(result["report"]["shed"]) == 41  # 51 offered, 10 kept
    assert bp.validate_report(result["report"]) == []


def test_apply_backpressure_preserves_relative_order():
    events = [_ev("conv_event", i) for i in range(6)]
    events.append(_ev("heartbeat_pulse", 100))
    result = bp.apply_backpressure(events, capacity=4)
    seqs = [e["_seq"] for e in result["kept"]]
    assert seqs == sorted(seqs)
    assert 100 in seqs


def test_pressure_levels():
    assert bp.pressure_level(0.0) == "calm"
    assert bp.pressure_level(0.69) == "calm"
    assert bp.pressure_level(0.7) == "pressured"
    assert bp.pressure_level(0.99) == "pressured"
    assert bp.pressure_level(1.0) == "full"


def test_capacity_must_be_a_real_positive_int():
    for bad in (0, -1, True, "256"):
        try:
            bp.BackpressureQueue(capacity=bad)
        except ValueError:
            continue
        raise AssertionError(f"capacity {bad!r} was accepted")


def test_validate_report_catches_broken_counts():
    q = bp.BackpressureQueue(capacity=2)
    q.offer(_ev("conv_event", 1))
    report = q.report()
    report["offered"] = 99
    assert bp.validate_report(report) != []


# ── The hub's inline copy ──────────────────────────────────


def test_hub_inline_tier_table_matches_canonical():
    assert tuple(hub._BP_PROTECTED) == tuple(bp.PROTECTED_TYPES)
    assert tuple(hub._BP_HIGH) == tuple(bp.HIGH_TYPES)
    assert tuple(hub._BP_NORMAL) == tuple(bp.NORMAL_TYPES)
    assert tuple(hub._BP_LOW) == tuple(bp.LOW_TYPES)
    assert tuple(hub._BP_LOW_PREFIXES) == tuple(bp.LOW_PREFIXES)
    for name in ("heartbeat_pulse", "conv_start", "conv_event",
                 "event:x", "orgasm", "operator_note"):
        assert hub._backpressure_tier(_ev(name)) == bp.tier_of(_ev(name))


def test_hub_ring_buffer_sheds_by_rule():
    rb = hub.RingBuffer(maxlen=3)
    rb.append(_ev("event:calm", 1))
    rb.append(_ev("conv_event", 2))
    rb.append(_ev("thought:deep", 3))
    rb.append(_ev("heartbeat_pulse", 4))  # displaces oldest low
    assert [e["data"]["n"] for e in rb.recent(10)] == [2, 3, 4]
    rb.append(_ev("event:calm", 5))  # equal-low: evicts the older low
    assert [e["data"]["n"] for e in rb.recent(10)] == [2, 4, 5]
    assert rb.shed_count == 2 and rb.protected_shed_count == 0
    rb.append(_ev("event:calm", 6))  # still cannot touch the pulse
    assert _ev("heartbeat_pulse", 4) in rb.recent(10)


def test_hub_ring_buffer_generic_events_keep_fifo_behaviour():
    rb = hub.RingBuffer(maxlen=3)
    for i in range(10):
        rb.append({"seq": i})
    assert [e["seq"] for e in rb.recent(10)] == [7, 8, 9]
    assert len(rb) == 3

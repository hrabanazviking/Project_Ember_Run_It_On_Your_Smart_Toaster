"""E-075 — Load truth: hub throughput per profile, measured.

Pins Verdandi/load_truth.py (the measuring instrument) and
its reading copy ``docs/architecture/E-075_LOAD_TRUTH.md``:

* the instrument is stdlib-only and standalone, like every
  Verdandi contract module since E-061;
* its profile table is the budget book's four profiles, in
  the book's order (``ember.budgets``), each shape sane
  (events divide evenly across its publishers);
* its statistics are honest arithmetic on synthetic samples
  (nearest-rank percentile; throughput = count / wall);
* its ring expectation matches the hub's own
  ``RING_BUFFER_SIZE`` literal;
* a live mini-run against the real hub (small shape, one
  subscriber) reports no errors: contiguous ack seqs, feed
  lines == published, ring full-or-total, subscriber heard
  everything in its window — correctness measured with the
  speed, never assumed;
* the doc records a measured row per profile and states
  the VM / simulation honesty lines.

The doc's throughput figures themselves are measurements
recorded in the slice record, not constants: no test here
re-measures hardware or pins a speed (the E-057 pattern).
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest

import ember.budgets as budgets

REPO = Path(__file__).resolve().parents[2]
VERDANDI = REPO / "Verdandi"
DOC = REPO / "docs" / "architecture" / "E-075_LOAD_TRUTH.md"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    # Register before exec: load_truth carries a @dataclass,
    # whose processing looks the module up in sys.modules.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


load_truth = _load("ember_load_truth_e075", VERDANDI / "load_truth.py")


# ── The instrument itself ────────────────────────────────


def test_module_is_stdlib_only_and_standalone():
    tree = ast.parse(_source(VERDANDI / "load_truth.py"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= set(sys.stdlib_module_names)


def test_profiles_are_the_budget_book_four_in_order():
    names = [s.name for s in load_truth.profile_shapes()]
    assert names == [b.profile.value for b in budgets.all_budgets()]
    assert names == ["toaster", "phone", "pi", "laptop"]


def test_shapes_are_sane_and_evenly_divided():
    for shape in load_truth.profile_shapes():
        assert shape.cpus >= 1
        assert shape.publishers >= 1
        assert shape.events % shape.publishers == 0
        assert shape.producer_events > 0
        assert shape.subscribers >= 0


def test_ring_size_matches_the_hubs_own_literal():
    tree = ast.parse(_source(VERDANDI / "nervous_system.py"))
    hub_ring = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "RING_BUFFER_SIZE":
                    hub_ring = ast.literal_eval(node.value)
    assert hub_ring == load_truth.RING_SIZE == 256


# ── The statistics ───────────────────────────────────────


def test_percentile_is_nearest_rank():
    samples = [float(x) for x in range(1, 101)]
    assert load_truth.percentile(samples, 0.50) == 50.0
    assert load_truth.percentile(samples, 0.95) == 95.0
    assert load_truth.percentile(samples, 1.0) == 100.0
    assert load_truth.percentile([7.0], 0.95) == 7.0
    with pytest.raises(ValueError):
        load_truth.percentile([], 0.5)


def test_summarise_arithmetic():
    report = load_truth.summarise([1.0, 2.0, 3.0, 4.0], 2.0, 200)
    assert report["events"] == 200
    assert report["throughput_per_s"] == 100.0
    assert report["latency_ms_mean"] == 2.5
    assert report["latency_ms_p50"] == 2.0
    assert report["latency_ms_max"] == 4.0


# ── The live mini-run ────────────────────────────────────


def test_live_mini_run_is_correct(tmp_path):
    shape = load_truth.ProfileShape(
        "mini", cpus=1, publishers=1, subscribers=1,
        events=40, producer_events=5)
    report = load_truth.measure_profile(shape, tmp_path)
    total = load_truth.WARMUP_EVENTS + 40 + 5
    assert report["errors"] == []
    assert report["published_total"] == total
    assert report["feed_lines"] == total
    assert report["ring_recent_count"] == total  # below the 256 cap
    assert report["persistent"]["events"] == 40
    assert report["persistent"]["throughput_per_s"] > 0
    assert report["producer"]["events"] == 5
    assert len(report["subscriber_received"]) == 1
    assert (total - load_truth.WARMUP_EVENTS
            <= report["subscriber_received"][0] <= total)
    assert report["hub_peak_rss_mib"] > 0
    assert report["feed_bytes_per_event"] > 0


# ── The reading copy ─────────────────────────────────────


def test_doc_states_the_measured_truth_and_its_limits():
    text = _source(DOC)
    for shape in load_truth.profile_shapes():
        assert f"| {shape.name} |" in text
    for needle in ("publish_event_sync", "persistent",
                   "producer", "VM", "NOT PROVEN",
                   "taskset", "contiguous"):
        assert needle in text

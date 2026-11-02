"""E-111 — Ritual-shaped time: the day's astrology as a
Verdandi stimulus.

Pins ``docs/architecture/E-111_RITUAL_SHAPED_TIME.md`` and,
behind it, ``src/ember/day_astrology.py`` at this tree:

* the record itself: the day's astrology entering as a
  registered stimulus, computed not fetched, at one stated
  moment, with a refusal publishing nothing;
* the registration: ``time.astrology`` in Verdandi's
  stimuli registry and in the hub's literal registry, kind
  ``time``, channel ``cron``, and the core module's inline
  literals pinned equal to the registry;
* the default environment (no ephemeris): the build
  refuses with the chart service's own reason and a
  publish attempt writes nothing anywhere;
* the live environment (the isolated ephemeris dir on the
  path, as at E-109/E-110): the London day at J2000 builds
  a stimulus the E-064 module itself validates, whose
  payload reproduces E-109/E-110's pinned sky (Sun
  280.3689 degrees, Ascendant 24.0146), round-trips
  through ``stimuli.from_event``, is deterministic across
  builds, and — published against a hub-less state dir —
  lands in the feed file in the hub's fallback shape,
  readable back as the same stimulus.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-111_RITUAL_SHAPED_TIME.md"
VERDANDI = REPO / "Verdandi"

sys.path.insert(0, str(REPO / "src"))

from ember import day_astrology  # noqa: E402
from ember.day_astrology import (  # noqa: E402
    build_day_stimulus,
    publish_day_stimulus,
    stimulus_event,
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


stimuli = _load("ember_stimuli_e111", VERDANDI / "stimuli.py")
hub = _load("ember_nervous_system_e111", VERDANDI / "nervous_system.py")

LIVE = importlib.util.find_spec("swisseph") is not None
LONDON = {"lat": 51.5074, "lon": -0.1278}


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


# ── The record, on file ─────────────────────────────────


def test_doc_records_the_stimulus_verdict():
    text = _flat(DOC)
    for needle in ("time.astrology", "computed, not fetched",
                   "publishes nothing", "12:00",
                   "Next: E-112"):
        assert needle in text, needle


# ── The registration ────────────────────────────────────


def test_registry_carries_the_day_stimulus():
    spec = stimuli.spec_for("time.astrology")
    assert spec is not None
    assert spec.kind == "time" and spec.channel == "cron"
    assert "day_astrology" in spec.producer
    assert hub._stimulus_spec_for("time.astrology") == ("time", "cron")


def test_core_literals_match_the_registry():
    spec = stimuli.spec_for(day_astrology.STIMULUS_NAME)
    assert day_astrology.STIMULUS_NAME == "time.astrology"
    assert day_astrology.STIMULUS_KIND == spec.kind
    assert day_astrology.STIMULUS_CHANNEL == spec.channel
    assert day_astrology.STIMULI_VERSION == stimuli.STIMULI_VERSION


def test_module_imports_only_stdlib_and_the_core():
    tree = ast.parse((REPO / "src/ember/day_astrology.py").read_text(encoding="utf-8"))
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    assert roots <= set(sys.stdlib_module_names) | {"ember", "__future__"}
    assert "Verdandi" not in roots and "astrology_engine" not in roots


# ── The default environment: a refusal, nothing built ───


@pytest.mark.skipif(LIVE, reason="the no-ephemeris shape is the default env's")
def test_day_refuses_without_ephemeris_and_publishes_nothing(tmp_path):
    built = build_day_stimulus("2000-01-01", **LONDON)
    assert built.stimulus is None
    assert "ephemeris is not available" in built.reason
    published = publish_day_stimulus("2000-01-01", state_dir=tmp_path, **LONDON)
    assert published.stimulus is None and published.status is None
    assert not (tmp_path / "nerve_feed.jsonl").exists()


# ── The live environment: the day, computed ─────────────


@pytest.mark.skipif(not LIVE, reason="needs the isolated ephemeris dir")
def test_day_stimulus_is_valid_and_carries_the_pinned_sky():
    built = build_day_stimulus("2000-01-01", **LONDON)
    assert built.reason is None
    stimulus = built.stimulus
    assert stimuli.validate_stimulus(stimulus) == []
    assert stimulus["provenance"] == {
        "origin": "ember_day_astrology", "channel": "cron"}
    payload = stimulus["payload"]
    assert payload["date"] == "2000-01-01"
    assert payload["moment"] == "12:00"
    assert payload["julian_day"] == 2451545.0
    by_name = {p["name"]: p for p in payload["positions"]}
    assert by_name["Sun"]["longitude"] == pytest.approx(280.3689, abs=0.02)
    assert payload["ascendant"] == pytest.approx(24.0146, abs=0.05)
    assert payload["day_chart"] is True
    assert payload["frame"] == "tropical"
    assert "built-in" in payload["ephemeris_model"]
    json.dumps(stimulus)  # the payload survives the feed file


@pytest.mark.skipif(not LIVE, reason="needs the isolated ephemeris dir")
def test_day_stimulus_round_trips_through_the_nerves():
    built = build_day_stimulus("2000-01-01", **LONDON)
    event = stimulus_event(built.stimulus)
    assert event["type"] == "stimulus:time.astrology"
    assert event["source"] == "ember_day_astrology"
    back = stimuli.from_event(event)
    assert back is not None
    assert back["payload"] == built.stimulus["payload"]
    assert back["provenance"]["origin"] == "ember_day_astrology"


@pytest.mark.skipif(not LIVE, reason="needs the isolated ephemeris dir")
def test_day_build_is_deterministic():
    first = build_day_stimulus("2000-01-01", **LONDON)
    second = build_day_stimulus("2000-01-01", **LONDON)
    assert first.stimulus == second.stimulus


@pytest.mark.skipif(not LIVE, reason="needs the isolated ephemeris dir")
def test_day_publish_lands_in_the_feed_when_no_hub(tmp_path):
    published = publish_day_stimulus("2000-01-01", state_dir=tmp_path, **LONDON)
    assert published.stimulus is not None
    assert published.status["nerve_type"] == "fallback"
    lines = (tmp_path / "nerve_feed.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["_fallback"] is True
    back = stimuli.from_event(event)
    assert back is not None and back["payload"]["date"] == "2000-01-01"


@pytest.mark.skipif(not LIVE, reason="needs the isolated ephemeris dir")
def test_day_city_road_and_bad_date():
    by_city = build_day_stimulus("1990-06-15", city="London", nation="UK")
    assert by_city.reason is None
    assert by_city.stimulus["payload"]["place"] == "London"
    bad = build_day_stimulus("2000-13-01", **LONDON)
    assert bad.stimulus is None and "calendar date" in bad.reason

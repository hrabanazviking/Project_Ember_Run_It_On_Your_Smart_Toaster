"""E-110 — The engines as services to the core.

Pins ``docs/architecture/E-110_ENGINES_AS_SERVICES.md``
and, behind it, the service module ``src/ember/engines.py``
at this tree:

* the record itself: typed requests/responses for both
  engines, the dockets this slice closes or carries
  (142 fixed at the source; 143, 144, 148 as contract
  notes; 153 declared in the contract; 154 ruled at the
  contract surface), and E-109's ephemeris-model answer
  travelling with every chart;
* the contract's shape: a version, the dependency
  declarations (the astrology member's five packages,
  one hard requirement; the verse member's empty set),
  and the deliberate absences — no sidereal field, no
  dead config fields on the verse request;
* the verse service in the default environment (the
  member is standard-library only): seeded requests
  byte-reproducible, the world honoured and reported,
  an unknown world refused before composing, an
  unknown form refused, ljodhattr lines served in
  reading order (pair, full line, pair, full line);
* the chart service in the default environment: with
  the ephemeris absent it refuses before computing
  (docket 148's contract note) — no empty positions,
  no fabricated cusps, ever;
* the chart service in the live environment (the
  isolated ephemeris dir on the path, as at E-109):
  the London chart at J2000 matches E-109's pinned
  fixtures (Sun 280.3689 degrees, Ascendant 24.0146),
  the city road resolves through the built-in table,
  an unresolvable place and an impossible date are
  refused in words.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-110_ENGINES_AS_SERVICES.md"

sys.path.insert(0, str(REPO / "src"))

from ember import engines  # noqa: E402
from ember.engines import (  # noqa: E402
    ASTROLOGY_DEPENDENCIES,
    SEIDR_DEPENDENCIES,
    ChartRequest,
    VerseRequest,
    compose_verse,
    ephemeris_available,
    request_chart,
)

LIVE = importlib.util.find_spec("swisseph") is not None
LONDON = {"lat": 51.5074, "lon": -0.1278}


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


# ── The record, on file ─────────────────────────────────


def test_doc_records_the_service_verdict():
    text = _flat(DOC)
    for needle in ("typed requests and responses",
                   "refuses before computing",
                   "tropical only",
                   "Next: E-111"):
        assert needle in text, needle


def test_doc_names_dockets_and_owners():
    text = _flat(DOC)
    for needle in ("Docket 142", "Docket 143", "Docket 144",
                   "Docket 148", "Docket 153", "Docket 154",
                   "E-120", "E-112", "E-113"):
        assert needle in text, needle


# ── The contract's shape ────────────────────────────────


def test_contract_version_and_dependency_declaration():
    assert engines.CONTRACT_VERSION == "1.0"
    assert SEIDR_DEPENDENCIES == ()
    assert len(ASTROLOGY_DEPENDENCIES) == 5
    required = [d for d in ASTROLOGY_DEPENDENCIES if d.required]
    assert [(d.package, d.imports) for d in required] == [
        ("pyswisseph", "swisseph")]
    assert {d.package for d in ASTROLOGY_DEPENDENCIES} == {
        "pyswisseph", "timezonefinder", "pytz", "kerykeion",
        "geopy"}


def test_requests_carry_no_dead_or_unproven_fields():
    verse_fields = {f.name for f in dataclasses.fields(VerseRequest)}
    # Docket 144's contract note: composition never
    # consults include_old_norse, and topic is a label,
    # not a hint — neither is carried by the contract.
    assert "include_old_norse" not in verse_fields
    assert "topic" not in verse_fields
    chart_fields = {f.name for f in dataclasses.fields(ChartRequest)}
    # Docket 154: the sidereal branch is dead code in the
    # member and unproven at E-109 — not served as live.
    assert "sidereal" not in chart_fields
    assert "tropical" not in chart_fields


def test_service_import_is_lazy_and_stdlib_only():
    code = (
        "import sys; import ember.engines; "
        "assert 'seidr' not in sys.modules; "
        "assert 'swisseph' not in sys.modules; "
        "print('lazy')"
    )
    proc = subprocess.run(
        [sys.executable, "-c", code],
        env={"PYTHONPATH": str(REPO / "src"), "PATH": "/usr/bin:/bin"},
        capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr
    assert "lazy" in proc.stdout


# ── The verse service ───────────────────────────────────


def test_verse_seeded_request_is_reproducible():
    first = compose_verse(VerseRequest(form="ljodhattr", seed=42))
    second = compose_verse(VerseRequest(form="ljodhattr", seed=42))
    assert first.reason is None and second.reason is None
    assert first.verse.lines == second.verse.lines
    assert first.verse.text == second.verse.text
    assert len(first.verse.lines) == 6


def test_verse_lines_come_in_reading_order():
    result = compose_verse(VerseRequest(form="ljodhattr", seed=42))
    assert result.reason is None
    # The rendered text and the served lines agree on the
    # order: each full line (indented in the rendering)
    # follows its own pair (docket 142, fixed at source).
    # The rendering's furniture (runic rules, the form
    # header) is filtered by membership in the served set.
    served = list(result.verse.lines)
    rendered = [line.strip() for line in result.verse.text.splitlines()
                if line.strip() in served]
    assert rendered == served


def test_verse_world_is_honoured_and_reported():
    result = compose_verse(VerseRequest(world="asgard", seed=7))
    assert result.reason is None
    assert result.verse.world == "asgard"
    unchosen = compose_verse(VerseRequest(seed=7))
    assert unchosen.verse.world in {
        "asgard", "vanaheim", "alfheim", "midgard",
        "jotunheim", "svartalfheim", "niflheim",
        "muspelheim", "helheim"}


def test_verse_unknown_world_refused_before_composing():
    result = compose_verse(VerseRequest(world="nosuchworld", seed=42))
    assert result.verse is None
    assert "unknown world" in result.reason
    assert "asgard" in result.reason  # the true worlds named


def test_verse_unknown_form_and_bad_counts_refused():
    assert compose_verse(VerseRequest(form="nope")).verse is None
    assert compose_verse(VerseRequest(stanzas=0)).verse is None
    bad = compose_verse(VerseRequest(alliteration_strictness=1.5))
    assert bad.verse is None and "probability" in bad.reason


def test_verse_missing_member_refuses_in_words(tmp_path):
    result = compose_verse(VerseRequest(), member_dir=tmp_path)
    assert result.verse is None
    assert "not found" in result.reason


# ── The chart service, default environment ──────────────


def test_ephemeris_availability_matches_the_environment():
    assert ephemeris_available() == LIVE


@pytest.mark.skipif(LIVE, reason="the no-ephemeris shape is the default env's")
def test_chart_refuses_before_computing_without_ephemeris():
    result = request_chart(ChartRequest(
        date="2000-01-01", time="12:00", **LONDON))
    assert result.chart is None
    assert "ephemeris is not available" in result.reason
    assert "pyswisseph" in result.reason


# ── The chart service, live environment ─────────────────


@pytest.mark.skipif(not LIVE, reason="needs the isolated ephemeris dir")
def test_chart_london_at_j2000_matches_e109_fixtures():
    result = request_chart(ChartRequest(
        date="2000-01-01", time="12:00", **LONDON))
    assert result.reason is None
    chart = result.chart
    assert chart.julian_day == 2451545.0
    assert len(chart.cusps) == 12
    assert chart.ascendant == pytest.approx(24.0146, abs=0.05)
    by_name = {b.name: b for b in chart.positions}
    assert by_name["Sun"].longitude == pytest.approx(280.3689, abs=0.02)
    assert by_name["Sun"].sign == "Capricorn"
    assert chart.day_chart is True  # noon — E-109's sect fix
    assert dict(chart.lots)["Lot of Fortune"] == pytest.approx(
        326.97, abs=0.05)
    assert chart.frame == "tropical"
    assert "built-in" in chart.ephemeris_model
    assert chart.time_known is True


@pytest.mark.skipif(not LIVE, reason="needs the isolated ephemeris dir")
def test_chart_city_road_resolves_through_the_builtin_table():
    result = request_chart(ChartRequest(
        date="1990-06-15", time="12:00", city="London", nation="UK"))
    assert result.reason is None
    assert (result.chart.lat, result.chart.lon) == (51.5074, -0.1278)


@pytest.mark.skipif(not LIVE, reason="needs the isolated ephemeris dir")
def test_chart_unresolvable_place_refuses():
    result = request_chart(ChartRequest(
        date="2000-01-01", city="Nosuchplace XYZ"))
    assert result.chart is None
    assert "could not be resolved" in result.reason


@pytest.mark.skipif(not LIVE, reason="needs the isolated ephemeris dir")
def test_chart_impossible_date_and_time_refuse():
    bad_date = request_chart(ChartRequest(
        date="2000-13-01", **LONDON))
    assert bad_date.chart is None and "calendar date" in bad_date.reason
    bad_time = request_chart(ChartRequest(
        date="2000-01-01", time="25:00", **LONDON))
    assert bad_time.chart is None and "time of day" in bad_time.reason


@pytest.mark.skipif(not LIVE, reason="needs the isolated ephemeris dir")
def test_chart_half_coordinates_and_no_place_refuse():
    half = request_chart(ChartRequest(date="2000-01-01", lat=10.0))
    assert half.chart is None and "together" in half.reason
    none = request_chart(ChartRequest(date="2000-01-01"))
    assert none.chart is None and "needs a place" in none.reason

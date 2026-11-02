"""E-109 — Astrology accuracy gate.

Pins ``docs/architecture/E-109_ASTROLOGY_ACCURACY_GATE.md``
and, behind it, the fixes and fixtures of the gate:

* dockets 149-152, 155 and 156 from E-108, closed in
  scope: the Lot of Fortune / Lot of Spirit swap, the
  never-detected fall, the misbuilt next-lunation
  search, the gazetteer defects (Tivat, Tianjin, the
  conflicting Charleston), the silent UTC convention
  of aspect-grid / antiscia, and the solar-return
  iteration that stopped ~26 degrees short;
* two findings this gate's own probes made and fixed
  in scope: docket 157 (every date printed from a
  Julian day landed 13 days early with its minutes
  zeroed — ``jd_to_dt`` called the Julian-calendar
  conversion) and docket 158 (chart sect exactly
  inverted — a London noon chart read as night);
* the real-sky fixtures: planetary longitudes at two
  epochs against the independent pyephem values
  recorded in the slice doc (epoch-of-date frame;
  the gate's standard is one arcminute), and the
  published lunation times of January 2000 and
  April 2024. These run only when the ephemeris is
  importable in the test environment (the E-108
  pattern); the search *logic* is proven in every
  environment against a synthetic ephemeris below;
* the member's re-pinned size (E-057): the fixes
  grew the one engine file, 7,477,309 B -> 7,482,898 B.

Fixtures are synthetic or published reference values
only — the roadmap's fixture law for this gate.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-109_ASTROLOGY_ACCURACY_GATE.md"
MEMBER = REPO / "astrology-engine"
ENGINE = MEMBER / "astrology_engine.py"
BOOK = REPO / "docs" / "BUDGET_BOOK.md"


def _load_engine():
    import io
    import sys

    real_stdout = sys.stdout
    sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    try:
        spec = importlib.util.spec_from_file_location(
            "ember_astrology_engine_e109", ENGINE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.stdout = real_stdout
    return module


AE = _load_engine()
SOURCE = ENGINE.read_text(encoding="utf-8")
JD0 = 2451545.0  # 2000-01-01 12:00 UTC


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _angdiff(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


# ── The record, on file ─────────────────────────────────


def test_doc_records_the_accuracy_verdict():
    text = _flat(DOC)
    for needle in ("within one arcminute",
                   "the accuracy gate passes",
                   "7,482,898 B",
                   "epoch-of-date",
                   "NOT PROVEN",
                   "Next: E-110"):
        assert needle in text, needle


def test_doc_names_dockets_closed_and_carried():
    text = _flat(DOC)
    for needle in ("Docket 149", "Docket 150", "Docket 151",
                   "Docket 152", "Docket 155", "Docket 156",
                   "Docket 157", "Docket 158",
                   "CLOSED in scope",
                   "Docket 148", "E-120", "E-110"):
        assert needle in text, needle


def test_member_size_repinned_at_e057():
    row = [line for line in BOOK.read_text(encoding="utf-8").splitlines()
           if line.startswith("| `astrology-engine/`")][0]
    assert "7,482,898 B" in row
    assert "131,621,907 bytes" in _flat(BOOK)


# ── Docket 149: the lots ────────────────────────────────


_POS = {p: {"longitude": lon} for p, lon in (
    ("Sun", 0.0), ("Moon", 90.0), ("Venus", 60.0),
    ("Mercury", 30.0), ("Mars", 120.0),
    ("Jupiter", 180.0), ("Saturn", 270.0))}


def test_lots_day_chart_traditional():
    lots = AE.calc_lots(_POS, 0.0, True)
    # Day: Fortune = ASC + Moon - Sun; Spirit = ASC + Sun - Moon;
    # the five dependent lots follow from those two.
    assert lots["Lot of Fortune"] == 90.0
    assert lots["Lot of Spirit"] == 270.0
    assert lots["Lot of Eros"] == 150.0
    assert lots["Lot of Necessity"] == 60.0
    assert lots["Lot of Courage"] == 30.0
    assert lots["Lot of Victory"] == 270.0
    assert lots["Lot of Nemesis"] == 180.0


def test_lots_night_chart_reverses_the_pair():
    lots = AE.calc_lots(_POS, 0.0, False)
    assert lots["Lot of Fortune"] == 270.0
    assert lots["Lot of Spirit"] == 90.0


# ── Docket 150: fall ────────────────────────────────────


def test_fall_table_is_the_opposite_of_exaltation():
    for planet, sign in (("Sun", "Libra"), ("Moon", "Scorpio"),
                         ("Mercury", "Pisces"), ("Venus", "Virgo"),
                         ("Mars", "Cancer"), ("Jupiter", "Capricorn"),
                         ("Saturn", "Aries")):
        assert AE.FALL[planet] == sign, planet


def test_fall_labels_land_and_exaltation_stands():
    for planet, sign in (("Sun", "Libra"), ("Moon", "Scorpio"),
                         ("Jupiter", "Capricorn")):
        score, labels = AE.essential_dignity(planet, sign, 15)
        assert any("Fall" in label for label in labels), planet
        assert score <= -4 + 3, planet  # fall -4, triplicity may add
    score, labels = AE.essential_dignity("Sun", "Aries", 19)
    assert any("Exaltation" in label for label in labels)
    assert not any("Fall" in label for label in labels)


# ── Docket 158: sect ────────────────────────────────────


def test_sect_geometry():
    # London, 2000-01-01: at noon the Sun (280) stands
    # between Descendant (204) and Ascendant (24) through
    # the MC — a day chart; at midnight it stands below.
    assert AE.is_day_chart(280.0, 24.0) is True
    assert AE.is_day_chart(280.0, 186.9) is False
    assert AE.is_day_chart(90.0, 0.0) is False   # Sun near the IC
    assert AE.is_day_chart(270.0, 0.0) is True   # Sun near the MC


# ── Docket 152: the gazetteer ───────────────────────────


def test_gazetteer_counts_and_no_conflicting_duplicates():
    seg = SOURCE[SOURCE.index("CITIES = {"):
                 SOURCE.index("result = CITIES.get")]
    pairs = re.findall(r'^\s*"([^"]+)":\s*\(([^)]*)\)', seg, re.M)
    assert len(pairs) == 426
    assert len({k for k, _ in pairs}) == 395
    by_key: dict[str, set[str]] = {}
    for key, coords in pairs:
        by_key.setdefault(key, set()).add(coords)
    conflicts = {k: v for k, v in by_key.items() if len(v) > 1}
    assert conflicts == {}, conflicts


def test_gazetteer_place_fixtures():
    # Working entries spot-pinned, plus the three
    # repaired entries. (Default env: the network
    # tiers are absent, so the table answers.) The
    # state capital of the house's state is verified
    # by this slice's probe and stands unchanged in
    # the table, but is deliberately not pinned here:
    # the E-089 canon guard forbids that state's name
    # anywhere in the test tree.
    for city, nation, want in (
            ("Reykjavik", "IS", (64.1355, -21.8954, True)),
            ("Angola", "US", (41.6337, -84.9994, True)),
            ("London", "UK", (51.5074, -0.1278, True)),
            ("Uppsala", "SE", (59.8586, 17.6389, True)),
            ("Tivat", "ME", (42.4347, 18.6998, True)),
            ("Tianjin", "CN", (39.1422, 117.1767, True)),
            ("Charleston", "US", (38.3498, -81.6326, True)),
            ("Charleston SC", "US", (32.7766, -79.9311, True))):
        assert AE.geocode_city(city, nation) == want, city


# ── Docket 155: the stated UTC convention ───────────────


def test_utc_convention_is_stated_in_both_commands():
    assert SOURCE.count("time treated as UTC (no location)") >= 2


# ── Dockets 151 + 156: the searches, synthetic sky ──────


def _fake_positions(jd, tropical=True):
    dt = jd - JD0
    sun = (280.0 + 0.9856 * dt) % 360
    moon = (290.0 + 13.1764 * dt) % 360
    return {"Sun": {"longitude": sun}, "Moon": {"longitude": moon}}


def _with_fake_ephemeris(fn):
    real_swe, real_calc = AE.SWE, AE.calc_planet_positions
    AE.SWE = True
    AE.calc_planet_positions = _fake_positions
    try:
        return fn()
    finally:
        AE.SWE, AE.calc_planet_positions = real_swe, real_calc


def test_next_lunation_finds_elongation_events():
    def run():
        new_jd, full_jd = AE.next_lunation(JD0)
        # Elongation starts at 10 degrees and grows
        # 12.1908 degrees a day: full at +170/12.1908,
        # new at +350/12.1908.
        assert abs(full_jd - (JD0 + 170.0 / 12.1908)) < 0.001
        assert abs(new_jd - (JD0 + 350.0 / 12.1908)) < 0.001
    _with_fake_ephemeris(run)


def test_solar_return_search_reaches_its_tolerance():
    def run():
        sr = AE.find_solar_return(280.0, JD0 + 365.0)
        assert sr is not None
        # The fake Sun circles in 360/0.9856 days.
        assert abs(sr - (JD0 + 360.0 / 0.9856)) < 0.01
        resid = _angdiff(
            AE.calc_planet_positions(sr)["Sun"]["longitude"], 280.0)
        assert resid < 0.0015
    _with_fake_ephemeris(run)


def test_searches_refuse_without_the_ephemeris():
    if AE.SWE:
        return  # the no-ephemeris shape is the default env's
    assert AE.next_lunation(JD0) == (None, None)
    assert AE.find_solar_return(280.0, JD0) is None


# ── Docket 157: dates printed from Julian days ──────────


def test_jd_to_dt_round_trip():
    if not AE.SWE:
        assert AE.jd_to_dt(JD0) == "JD 2451545.0000"
        return
    assert AE.jd_to_dt(JD0) == "2000-01-01 12:00 UTC"
    assert AE.jd_to_dt(2451550.259487152) == "2000-01-06 18:13 UTC"


# ── The derived maths, spot fixtures ────────────────────


def test_derived_maths_spot_fixtures():
    anti = AE.calc_antiscia({"Sun": {"longitude": 30.0}})
    assert anti["Sun"]["antiscia_lon"] == 150.0
    assert anti["Sun"]["contra_lon"] == 330.0
    comp = AE.calc_composite(
        {"Sun": {"longitude": 350.0}}, {"Sun": {"longitude": 10.0}})
    assert comp["Sun"]["longitude"] == 0.0
    name, glyph, elong, illum = AE.calc_lunar_phase(0.0, 180.0)
    assert (name, illum) == ("Full Moon", 100)


# ── Real-sky fixtures (ephemeris environments only) ─────


_REFERENCE = {
    (2000, 1, 1): {"Sun": 280.3786, "Moon": 223.3276,
                   "Mercury": 271.8989, "Venus": 241.5742,
                   "Mars": 327.9711, "Jupiter": 25.2555,
                   "Saturn": 40.3967, "Uranus": 314.8179,
                   "Neptune": 303.2024, "Pluto": 251.4628},
    (1990, 6, 15): {"Sun": 84.1316, "Moon": 345.3545,
                    "Mercury": 65.6925, "Venus": 48.7786,
                    "Mars": 11.0394, "Jupiter": 105.8911,
                    "Saturn": 294.0236, "Uranus": 278.1563,
                    "Neptune": 283.7084, "Pluto": 225.3929},
}
_ONE_ARCMIN = 1.0 / 60.0


def test_live_positions_within_one_arcminute():
    if not AE.SWE:
        return  # proven in the slice's live-shape gate run
    for (y, m, d), ref in _REFERENCE.items():
        pos = AE.calc_planet_positions(AE.julian_day(y, m, d, 12.0))
        for planet, want in ref.items():
            got = pos[planet]["longitude"]
            assert _angdiff(got, want) <= _ONE_ARCMIN, (
                planet, y, got, want)


def test_live_lunations_match_published_times():
    if not AE.SWE:
        return
    three_min = 3.0 / 1440.0
    new_jd, full_jd = AE.next_lunation(AE.julian_day(2000, 1, 1, 12.0))
    # Published: new moon 2000-01-06 18:14 UTC,
    # full moon 2000-01-21 04:40 UTC.
    assert abs(new_jd - AE.julian_day(2000, 1, 6, 18 + 14 / 60)) < three_min
    assert abs(full_jd - AE.julian_day(2000, 1, 21, 4 + 40 / 60)) < three_min
    new_jd, full_jd = AE.next_lunation(AE.julian_day(2024, 4, 1, 0.0))
    # Published: new moon 2024-04-08 18:21 UTC,
    # full moon 2024-04-23 23:49 UTC.
    assert abs(new_jd - AE.julian_day(2024, 4, 8, 18 + 21 / 60)) < three_min
    assert abs(full_jd - AE.julian_day(2024, 4, 23, 23 + 49 / 60)) < three_min


def test_live_solar_return_and_sect():
    if not AE.SWE:
        return
    jd_natal = AE.julian_day(1990, 6, 15, 12.0)
    natal_sun = AE.calc_planet_positions(jd_natal)["Sun"]["longitude"]
    sr = AE.find_solar_return(
        natal_sun, AE.julian_day(2026, 6, 15, 12.0))
    assert sr is not None
    assert AE.jd_to_dt(sr).startswith("2026-06-15")
    resid = _angdiff(
        AE.calc_planet_positions(sr)["Sun"]["longitude"], natal_sun)
    assert resid < 0.0015
    # Sect against the recorded London day: midnight is
    # night, noon is day (docket 158's altitude probe).
    for hour, want in ((0.0, False), (12.0, True)):
        jd = AE.julian_day(2000, 1, 1, hour)
        pos = AE.calc_planet_positions(jd)
        _, asc, _ = AE.calc_houses(jd, 51.5074, -0.1278)
        assert AE.is_day_chart(pos["Sun"]["longitude"], asc) is want

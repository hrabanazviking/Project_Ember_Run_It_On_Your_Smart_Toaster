"""E-108 — Astrology engine mapped.

Pins ``docs/architecture/E-108_ASTROLOGY_ENGINE_MAPPED.md``
and, behind it, the member's measured shape at this
tree (the member has no suite of its own, so the
engine file is loaded directly and probed):

* the record itself: the plain-words verdict (a
  single-file Swiss-Ephemeris chart calculator with
  no consumers in the core today), the ephemeris
  source, and dockets 148-155 each with its Part VII
  owner;
* the member's standing size: the 25 tracked files
  and their 7,477,309 B total (the E-057 row);
* the surface derived from the code: 16 CLI
  subcommands, 17 planet keys, 12 aspects, 7 lots;
* the Julian-day fallback exact at both reference
  epochs (J2000 and the Unix epoch) — pure maths,
  no ephemeris needed;
* the no-ephemeris shapes, probed in the default
  env where ``swisseph`` is absent: positions come
  back empty, houses come back as fabricated equal
  30-degree cusps with ASC/MC at 0 (docket 148;
  E-120 / E-110 re-pin when the refusal lands);
* the gazetteer: 426 entries, 394 unique keys, the
  Tivat entry carrying Cancun's coordinates and the
  ``tientSin`` key unreachable by a lower-cased
  lookup (docket 152; re-pinned at E-109, where the
  fixes landed: 395 unique keys, Tivat on its own
  coordinates, Tianjin reachable, Charleston split);
* docket 149's shape, probed on synthetic
  positions: in a day chart the Lot of Fortune
  comes out where the Lot of Spirit belongs
  (Fortune/Spirit swapped; re-pinned at E-109:
  Fortune and Spirit now stand in their traditional
  places);
* docket 150's shape, probed: the Sun in Libra —
  its traditional fall — is scored Peregrine, no
  Fall label (re-pinned at E-109: the Fall label
  now lands);
* the consumer claim: no file under ``src/``
  mentions astrology at all.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-108_ASTROLOGY_ENGINE_MAPPED.md"
MEMBER = REPO / "astrology-engine"
ENGINE = MEMBER / "astrology_engine.py"

TRACKED = (
    "1a64a630-c13b-499b-a1c9-4e6f5fc3fee0.jpg",
    "1e181307-c1c2-4ecb-912e-f88d3980e3e5.jpg",
    "544f9808-270f-4ba7-9d6a-af48d47a624e.jpg",
    "8ac34e68-f15a-4c8c-bbcb-690a689d37c5.jpg",
    "ARCHITECTURE.md",
    "CHANGELOG.md",
    "COMMANDS.md",
    "CONTRIBUTING.md",
    "IMG_0407.jpeg",
    "LEGAL-NOTICE.md",
    "LICENSE",
    "NOTICE",
    "README.md",
    "ROADMAP.md",
    "Viking_Apache_V2_1.jpg",
    "astrology_engine.py",
    "c5c058a2-a770-49b1-a58d-637db801313e.jpg",
    "ccb952ab-e824-4c94-aea9-29651672549d.jpg",
    "docs/references/engine-review-gaps.md",
    "docs/references/gaps-and-integration-notes.md",
    "docs/references/timezone-and-geocoding.md",
    "ecc1715c-605a-4575-bee5-0d91ade23108.jpg",
    "etre34gdfgd3.png",
    "ff1930e8-65c4-4214-b3ca-936e7c6d0e67.jpg",
    "image-23-RuneForgeAI.jpg",
)


def _load_engine():
    # The engine rebinds sys.stdout to a fresh wrapper at
    # import; under pytest's capture that breaks the
    # capture stream, so the import runs with a throwaway
    # buffered stdout and the real one is restored after.
    import io
    import sys

    real_stdout = sys.stdout
    sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    try:
        spec = importlib.util.spec_from_file_location(
            "ember_astrology_engine_e108", ENGINE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.stdout = real_stdout
    return module


AE = _load_engine()
SOURCE = ENGINE.read_text(encoding="utf-8")


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


# ── The record, on file ─────────────────────────────────


def test_doc_records_the_map_verdict():
    text = _flat(DOC)
    for needle in ("it calculates astrological charts",
                   "It has no consumers today",
                   "Swiss Ephemeris",
                   "25 tracked files, 7,477,309 B",
                   "16 subcommands",
                   "no test suite",
                   "Next: E-109"):
        assert needle in text, needle


def test_doc_names_dockets_and_owners():
    text = _flat(DOC)
    for needle in ("Docket 148", "Docket 149", "Docket 150",
                   "Docket 151", "Docket 152", "Docket 153",
                   "Docket 154", "Docket 155",
                   "E-109", "E-110", "E-120"):
        assert needle in text, needle


# ── The member's measured shape ─────────────────────────


def test_tracked_member_files_and_size_stand():
    total = 0
    for rel in TRACKED:
        path = MEMBER / rel
        assert path.is_file(), rel
        total += path.stat().st_size
    # 7,477,309 B at E-108; re-pinned at E-109, whose
    # accuracy fixes grew the one engine file by
    # 5,589 B (the E-057 table re-pinned likewise).
    assert total == 7482898


def test_surface_counts_derived_from_code():
    assert SOURCE.count("sub.add_parser(") == 16
    assert len(AE.PLANETS) == 17
    assert len(AE.ASPECTS) == 12
    assert len(AE.LOTS_FORMULAS) == 7
    assert len(AE.SIGNS) == 12


def test_julian_day_fallback_exact_at_references():
    # Pure maths in the engine (no ephemeris needed):
    # J2000.0 = JD 2451545.0; Unix epoch = JD 2440587.5.
    assert AE.julian_day(2000, 1, 1, 12.0) == 2451545.0
    assert AE.julian_day(1970, 1, 1, 0.0) == 2440587.5


def test_no_consumer_in_the_core():
    offenders = []
    for path in (REPO / "src").rglob("*.py"):
        if "astrology" in path.read_text(
                encoding="utf-8", errors="replace").lower():
            offenders.append(str(path.relative_to(REPO)))
    assert offenders == [], offenders


def test_member_has_no_test_suite():
    tests = [rel for rel in TRACKED
             if "test" in Path(rel).name.lower()]
    assert tests == [], tests


# ── The docketed shapes, probed ─────────────────────────


def test_docket_148_no_ephemeris_shapes():
    if AE.SWE:
        return  # the shape below is the default-env shape
    jd = AE.julian_day(2000, 1, 1, 12.0)
    assert AE.calc_planet_positions(jd) == {}
    cusps, asc, mc = AE.calc_houses(jd, 51.5074, -0.1278)
    assert cusps == [i * 30.0 for i in range(12)]
    assert asc == 0.0 and mc == 0.0


def test_docket_152_gazetteer_shape():
    # Re-pinned at E-109 (docket 152 fixed there): the
    # entry count stands, the Charleston split adds one
    # unique key, Tivat carries its own coordinates, and
    # Tianjin resolves instead of defaulting to 0,0.
    seg = SOURCE[SOURCE.index("CITIES = {"):
                 SOURCE.index("result = CITIES.get")]
    keys = re.findall(r'^\s*"([^"]+)":\s*\(', seg, re.M)
    assert len(keys) == 426
    assert len(set(keys)) == 395
    tivat = re.search(r'"tivat":\s*\(([^)]*)\)', SOURCE).group(1)
    cancun = re.search(r'"cancun":\s*\(([^)]*)\)', SOURCE).group(1)
    assert tivat != cancun
    assert tivat == "42.4347, 18.6998"
    lat, lon, resolved = AE.geocode_city("Tianjin", "CN")
    assert (lat, lon, resolved) == (39.1422, 117.1767, True)


def test_docket_149_fortune_spirit_swapped():
    pos = {p: {"longitude": lon} for p, lon in (
        ("Sun", 0.0), ("Moon", 90.0), ("Venus", 60.0),
        ("Mercury", 30.0), ("Mars", 120.0),
        ("Jupiter", 180.0), ("Saturn", 270.0))}
    lots = AE.calc_lots(pos, 0.0, True)
    # Re-pinned at E-109 (docket 149 fixed there):
    # traditional day Fortune = ASC + Moon - Sun = 90,
    # and Spirit = ASC + Sun - Moon = 270.
    assert lots["Lot of Fortune"] == 90.0
    assert lots["Lot of Spirit"] == 270.0


def test_docket_150_fall_never_detected():
    # Re-pinned at E-109 (docket 150 fixed there): the
    # textbook falls now carry the Fall label.
    score, labels = AE.essential_dignity("Sun", "Libra", 15)
    assert any("Fall" in label for label in labels)
    score, labels = AE.essential_dignity("Moon", "Scorpio", 15)
    assert any("Fall" in label for label in labels)

"""E-114 — Budget rows: both engines in the budget book.

Pins ``docs/architecture/E-114_ENGINE_BUDGET_ROWS.md`` and
the engines' subsection of ``docs/BUDGET_BOOK.md`` §7:

* the tracked breakdowns are re-derived live from
  ``git ls-files`` (the E-057 method): seiðr's weight is
  its package; the astrology member's tracked weight is
  96.6% pictures, and the engine itself is one file;
* the carrying-in judgements are re-derived from the
  recorded installed sizes against the live
  ``ember.budgets`` ceilings: the sky (engine file +
  pyswisseph as installed) fits the pi profile only;
  the local-time road as the package index serves it
  today fits no profile at all;
* the working peaks are recorded measurements (VmHWM
  medians of three fresh processes on the contended
  campaign VM, the E-057/E-103 discipline: measurements
  are pinned as printed, judgements re-derived live);
* docket 159's Part VII weighing is re-derived from
  git history: the core's tracked ``src/`` at the
  E-106 banking commit (Part VII's opening tree) and
  at this slice's tree, every grown byte attributed
  to a named file;
* the engines write nothing of their own: a verse
  composed and a chart attempted from an empty
  scratch directory leave it empty.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "docs" / "architecture" / "E-114_ENGINE_BUDGET_ROWS.md"
BOOK = REPO / "docs" / "BUDGET_BOOK.md"

sys.path.insert(0, str(REPO / "src"))

import ember.budgets as budgets  # noqa: E402

_MIB = 1024 * 1024

# Recorded measurements at the slice (E-114 doc).
SEIDR_TRACKED_FILES, SEIDR_TRACKED_BYTES = 11, 105_889
SEIDR_PACKAGE_BYTES = 88_707
ASTRO_TRACKED_FILES, ASTRO_TRACKED_BYTES = 25, 7_483_464
ASTRO_IMAGE_BYTES = 7_230_510
ASTRO_ENGINE_BYTES = 140_715
ASTRO_REST_BYTES = 112_239
PYSWISSEPH_INSTALLED = 7_639_165  # .so 7,601,904 + dist-info 37,261
SKY_CARRY_IN = 7_779_880
TIMEZONEFINDER_CLOSURE = 105_138_077
PYTZ_INSTALLED = 1_074_846
FULL_LOCAL_ROAD = 113_992_803
GEOPY_CLOSURE = 1_141_378
KERYKEION_PACKAGE = 5_339_199
KERYKEION_CLOSURE = 166_928_928  # installed alone, empty target

SEIDR_SERVICE_PEAK_MIB = 14.7
ASTRO_SKY_PEAK_MIB = 18.1
ASTRO_TIMEZONE_PEAK_MIB = 38.5

#: The E-106 banking commit — Part VII's opening tree.
E106_COMMIT = "c0befb8f4c8fe2ca4420fec2c5402d7d142f5221"
SRC_AT_E106 = 938_897
PART_VII_GROWTH = 55_122


def _ceilings() -> dict[str, budgets.ProfileBudget]:
    return {b.profile.value: b for b in budgets.all_budgets()}


def _tracked(member: str) -> dict[str, int]:
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-files", "-z", "--", member],
        capture_output=True, check=True).stdout.decode()
    return {name: (REPO / name).stat().st_size
            for name in out.split("\0") if name}


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


# ── The record, on file, and the book's rows ────────────


def test_doc_records_the_rows_and_the_growth_weighing():
    text = _flat(DOC)
    for needle in ("in plain words",
                   "105,889", "88,707",
                   "7,483,464", "7,230,510", "140,715",
                   "7,639,165", "7,779,880",
                   "105,138,077", "113,992,803",
                   "166,928,928",
                   "14.7 MiB", "18.1 MiB", "38.5 MiB",
                   "docket 159", "55,122", "263,429",
                   "NOT PROVEN", "Next: E-115"):
        assert needle in text, needle


def test_book_gained_the_engines_rows_at_the_records_numbers():
    text = BOOK.read_text(encoding="utf-8")
    assert "The engines' own costs (E-114)" in text
    for needle in ("88,707 B", "7,779,880 B", "106,212,923 B",
                   "14.7 MiB", "18.1 MiB", "38.5 MiB",
                   "7,230,510"):
        assert needle in text, needle


def test_e057_member_rows_stand_unchanged():
    # This slice moves no member file: the standing
    # E-057 rows for both engines are the tree's still.
    text = BOOK.read_text(encoding="utf-8")
    assert "| `seidr_engine/` | 11 | 105,889 B | toaster |" in text
    assert "| `astrology-engine/` | 25 | 7,483,464 B | pi |" in text


# ── Tracked breakdowns, re-derived live ─────────────────


def test_seidr_tracked_breakdown_is_its_package():
    files = _tracked("seidr_engine")
    assert len(files) == SEIDR_TRACKED_FILES
    assert sum(files.values()) == SEIDR_TRACKED_BYTES
    package = sum(size for name, size in files.items()
                  if name.startswith("seidr_engine/seidr/"))
    assert package == SEIDR_PACKAGE_BYTES


def test_astrology_tracked_breakdown_is_pictures_not_engine():
    files = _tracked("astrology-engine")
    assert len(files) == ASTRO_TRACKED_FILES
    assert sum(files.values()) == ASTRO_TRACKED_BYTES
    images = sum(size for name, size in files.items()
                 if name.rsplit(".", 1)[-1].lower()
                 in ("png", "jpg", "jpeg"))
    assert images == ASTRO_IMAGE_BYTES
    engine = files["astrology-engine/astrology_engine.py"]
    assert engine == ASTRO_ENGINE_BYTES
    rest = sum(files.values()) - images - engine
    assert rest == ASTRO_REST_BYTES
    # The finding in one line: the pictures outweigh
    # the engine itself more than fifty times over.
    assert images > 50 * engine


# ── Carrying-in judgements, re-derived ──────────────────


def test_dependency_declaration_matches_the_rows():
    from ember.engines import (
        ASTROLOGY_DEPENDENCIES,
        SEIDR_DEPENDENCIES,
    )

    assert SEIDR_DEPENDENCIES == ()
    assert len(ASTROLOGY_DEPENDENCIES) == 5
    hard = [d.package for d in ASTROLOGY_DEPENDENCIES if d.required]
    assert hard == ["pyswisseph"]


def test_sky_carry_in_is_the_engine_file_plus_the_ephemeris():
    assert ASTRO_ENGINE_BYTES + PYSWISSEPH_INSTALLED == SKY_CARRY_IN


def test_sky_carry_in_fits_the_pi_profile_only():
    ceilings = _ceilings()
    for profile in ("toaster", "phone"):
        assert SKY_CARRY_IN > ceilings[profile].install_mib * _MIB
    assert SKY_CARRY_IN <= ceilings["pi"].install_mib * _MIB
    # And it spends most of the pi ceiling doing it.
    assert SKY_CARRY_IN > 0.90 * ceilings["pi"].install_mib * _MIB


def test_full_local_road_fits_no_profile():
    assert (SKY_CARRY_IN + TIMEZONEFINDER_CLOSURE
            + PYTZ_INSTALLED) == FULL_LOCAL_ROAD
    ceilings = _ceilings()
    for budget in ceilings.values():
        assert FULL_LOCAL_ROAD > budget.install_mib * _MIB
    # The timezone dependencies alone already bust
    # every ceiling in the book.
    tz_deps = TIMEZONEFINDER_CLOSURE + PYTZ_INSTALLED
    assert tz_deps == 106_212_923
    for budget in ceilings.values():
        assert tz_deps > budget.install_mib * _MIB


def test_network_tier_closures_fit_no_profile_either():
    # The CLI road's tiers, each measured as installed
    # alone: geopy is small, kerykeion's closure busts
    # every ceiling — and the service pays neither.
    ceilings = _ceilings()
    assert GEOPY_CLOSURE < ceilings["toaster"].install_mib * _MIB
    for budget in ceilings.values():
        assert KERYKEION_CLOSURE > budget.install_mib * _MIB
    assert KERYKEION_PACKAGE < KERYKEION_CLOSURE


def test_seidr_carry_in_fits_the_toaster():
    toaster = _ceilings()["toaster"]
    assert SEIDR_PACKAGE_BYTES < toaster.install_mib * _MIB
    assert SEIDR_TRACKED_BYTES < 0.06 * toaster.install_mib * _MIB


def test_pyswisseph_installed_size_where_the_isolated_deps_stand():
    deps = (Path.home() / "workspace" / ".verify-tmp"
            / "ember-e108" / "deps")
    so = deps / "swisseph.cpython-312-x86_64-linux-gnu.so"
    dist_info = deps / "pyswisseph-2.10.3.2.dist-info"
    if not (so.exists() and dist_info.exists()):
        pytest.skip("the isolated ephemeris install is absent here")
    total = so.stat().st_size + sum(
        p.stat().st_size for p in dist_info.rglob("*") if p.is_file())
    assert total == PYSWISSEPH_INSTALLED


# ── Working peaks: judgements re-derived ────────────────


def test_recorded_working_peaks_fit_the_toaster_turn_ceiling():
    toaster = _ceilings()["toaster"]
    for peak in (SEIDR_SERVICE_PEAK_MIB, ASTRO_SKY_PEAK_MIB,
                 ASTRO_TIMEZONE_PEAK_MIB):
        assert peak < toaster.turn_ram_mib
    # The local-time shape is the one real spender:
    # it uses more than half the smallest ceiling.
    assert ASTRO_TIMEZONE_PEAK_MIB > 0.55 * toaster.turn_ram_mib
    assert ASTRO_SKY_PEAK_MIB < 0.30 * toaster.turn_ram_mib


# ── Docket 159: Part VII's growth, re-derived ───────────


def _src_total(commit: str) -> int:
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-tree", "-r", "-l", commit,
         "--", "src"],
        capture_output=True, check=True, text=True).stdout
    total = 0
    for line in out.splitlines():
        meta, _path = line.split("\t", 1)
        total += int(meta.split()[3])
    return total


def _file_size(commit: str, path: str) -> int | None:
    out = subprocess.run(
        ["git", "-C", str(REPO), "ls-tree", "-r", "-l", commit,
         "--", path],
        capture_output=True, check=True, text=True).stdout.strip()
    if not out:
        return None
    return int(out.split("\t", 1)[0].split()[3])


def test_part_vii_growth_is_every_byte_attributed():
    assert _src_total(E106_COMMIT) == SRC_AT_E106
    head = _src_total("HEAD")
    assert head - SRC_AT_E106 == PART_VII_GROWTH
    new_modules = (
        _file_size("HEAD", "src/ember/engines.py"),
        _file_size("HEAD", "src/ember/day_astrology.py"),
        _file_size("HEAD", "src/ember/seidr_conversation.py"),
    )
    assert new_modules == (26_350, 9_493, 18_868)
    budgets_growth = (
        _file_size("HEAD", "src/ember/budgets.py")
        - _file_size(E106_COMMIT, "src/ember/budgets.py"))
    assert budgets_growth == 411
    assert sum(new_modules) + budgets_growth == PART_VII_GROWTH


def test_docket_159_arithmetic_against_the_founding_measurement():
    # Founding all-in 978,843 B (E-041) -> re-measured
    # all-in 1,275,211 B (E-112); the package alone
    # 729,802 B -> 993,231 B at E-113's banking.
    assert budgets.MEASURED_INSTALL_BYTES == 1_275_211
    assert 1_275_211 - 978_843 == 296_368
    assert 993_231 - 729_802 == 263_429
    # Part VII's weighed share of the package's whole
    # growth is about a fifth; the rest pre-dates it.
    assert PART_VII_GROWTH < 0.25 * 263_429
    # The package at Part VII's opening tree, by the
    # same tracked method (src minus its README):
    assert SRC_AT_E106 - 788 == 938_109
    assert 938_109 + PART_VII_GROWTH == 993_231


# ── The engines write nothing of their own ──────────────


def test_engines_leave_an_empty_scratch_dir_empty(tmp_path):
    code = (
        "import sys; sys.path.insert(0, sys.argv[1]); "
        "sys.path.insert(0, sys.argv[2]); "
        "from ember.engines import compose_verse, VerseRequest, "
        "request_chart, ChartRequest; "
        "r = compose_verse(VerseRequest(seed=42)); "
        "assert r.reason is None, r.reason; "
        "c = request_chart(ChartRequest(date='2000-01-01', "
        "time='12:00', lat=51.5074, lon=-0.1278)); "
        "print('chart served' if c.chart is not None "
        "else 'chart refused: ' + str(c.reason))"
    )
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-c", code, str(REPO / "src"),
         str(REPO / "seidr_engine")],
        cwd=tmp_path, env=env, capture_output=True, text=True,
        timeout=120)
    assert proc.returncode == 0, proc.stderr
    assert list(tmp_path.iterdir()) == []


def test_engine_budget_rows_are_wired_into_the_gate():
    assert Path(__file__).parent.name == "unit"

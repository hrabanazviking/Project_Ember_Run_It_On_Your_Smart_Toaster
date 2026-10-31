"""E-057 — The member budget table, pinned to the tree.

E-041–E-056 priced the Ember core. E-057 prices every
other member that can run: the published table in
``docs/BUDGET_BOOK.md`` §7 (mirrored in the slice record
``docs/architecture/E-057_MEMBER_BUDGET_TABLE.md``).

These tests re-derive the table's facts live, so the
published table cannot quietly age away from the tree:

* each member's tracked file count and byte size are
  re-derived from ``git ls-files`` (the E-002/E-014
  method) and must equal the printed row;
* each member's "smallest covering profile" is recomputed
  from ``ember.budgets``' live install ceilings;
* the prose total and Verdandi's over-the-laptop margin
  are recomputed from the re-derived sizes;
* the three NOT MEASURED rows are exactly the members
  whose runtime cannot be imported or run in this
  environment, with their reasons stated in print.

RAM floors themselves are measurements recorded in the
slice record (median-of-three fresh-process probes); no
test here re-measures hardware. What is pinned is that
the two published copies of the table agree byte for
byte, row for row, and that the honesty lines stand.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import ember.budgets as budgets

_ROOT = Path(__file__).resolve().parents[2]
_BOOK = _ROOT / "docs" / "BUDGET_BOOK.md"
_RECORD = _ROOT / "docs" / "architecture" / "E-057_MEMBER_BUDGET_TABLE.md"

#: The running members: the core plus every imported
#: member of the E-002 census. (The remaining top-level
#: directories are checkout-only estate — documents,
#: assets, tests, scaffolding — priced in prose, never
#: judged against profiles.)
MEMBERS: tuple[str, ...] = (
    "src",
    "Verdandi",
    "kista",
    "mempalace",
    "mimir-well",
    "seidr_engine",
    "astrology-engine",
    "bifrost",
    "Hamr",
    "Open-VTT",
    "CloakBrowser",
    "cleasby-vigfusson-old-norse-dict",
)

#: Members with no honest RAM figure in this environment:
#: Godot absent (Open-VTT), Node dependencies absent
#: (dictionary), and CloakBrowser, whose import needs
#: uninstalled dependencies and whose real weight is a
#: proprietary binary absent from the tree.
NOT_MEASURED = {"Open-VTT", "CloakBrowser", "cleasby-vigfusson-old-norse-dict"}

_MIB = 1024 * 1024


def _rows(path: Path) -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"\| `([^`/]+)/?`", line)
        if match and "Tracked size" not in line:
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) == 5 and cells[2].endswith(" B"):
                rows[match.group(1)] = cells
    return rows


def _tracked(member: str) -> tuple[int, int]:
    out = subprocess.run(
        ["git", "-C", str(_ROOT), "ls-files", "-z", "--", member],
        capture_output=True,
        check=True,
    ).stdout.decode()
    files = [name for name in out.split("\0") if name]
    return len(files), sum((_ROOT / name).stat().st_size for name in files)


def _smallest_covering(size: int) -> str:
    for budget in budgets.all_budgets():
        if size <= budget.install_mib * _MIB:
            return budget.profile.value
    return "none"


def test_table_lists_every_running_member_exactly_once() -> None:
    rows = _rows(_BOOK)
    assert set(rows) == set(MEMBERS)
    assert len(rows) == len(MEMBERS) == 12


def test_tracked_sizes_and_counts_match_the_tree() -> None:
    rows = _rows(_BOOK)
    for member in MEMBERS:
        count, size = _tracked(member)
        assert rows[member][1] == f"{count:,}" or rows[member][1] == str(count)
        assert rows[member][2] == f"{size:,} B", member


def test_smallest_covering_profile_matches_live_ceilings() -> None:
    rows = _rows(_BOOK)
    for member in MEMBERS:
        _, size = _tracked(member)
        assert rows[member][3] == _smallest_covering(size), member


def test_prose_total_and_verdandi_margin_are_the_trees() -> None:
    text = _BOOK.read_text(encoding="utf-8")
    total = sum(_tracked(member)[1] for member in MEMBERS)
    assert f"{total:,} bytes" in text
    laptop = budgets.budget_for(budgets.ConversationProfile.LAPTOP)
    margin = _tracked("Verdandi")[1] - int(laptop.install_mib * _MIB)
    assert margin > 0  # Verdandi fits no profile — that is the finding
    assert f"{margin:,} bytes" in text


def test_ram_floors_and_not_measured_rows_are_honest() -> None:
    rows = _rows(_BOOK)
    floors: dict[str, float] = {}
    for member in MEMBERS:
        cell = rows[member][4]
        if member in NOT_MEASURED:
            assert cell == "NOT MEASURED", member
        else:
            match = re.fullmatch(r"([0-9]+\.[0-9]) MiB", cell)
            assert match, (member, cell)
            floors[member] = float(match.group(1))
    # Every floor sits above the bare interpreter's floor
    # (10.1 MiB, stated in print) and below the toaster's
    # turn ceiling — a floor outside that band is a
    # mis-measurement, not a member's weight.
    book = budgets.budget_for(budgets.ConversationProfile.TOASTER)
    for member, floor in floors.items():
        assert 10.1 <= floor < book.turn_ram_mib, member
    text = _BOOK.read_text(encoding="utf-8")
    # The floor-is-not-a-running-cost honesty lines stand.
    assert "10.1 MiB" in text
    assert "40.7 MiB" in text  # the core's running idle, E-041
    assert "21.9 MiB" in text  # Verdandi's running hub, E-041
    # The NOT MEASURED reasons are named in print.
    assert "Godot" in text
    assert "proprietary" in text


def test_the_two_published_copies_agree() -> None:
    book_rows = _rows(_BOOK)
    record_rows = _rows(_RECORD)
    assert book_rows == record_rows


def test_member_table_is_wired_into_the_gate() -> None:
    # This file lives under tests/unit/, where the slice
    # gate's Runs B/D collect it (E-042's pattern).
    assert Path(__file__).parent.name == "unit"

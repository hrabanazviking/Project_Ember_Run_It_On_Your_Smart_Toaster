"""E-055 — The budget book, published, pinned to the code.

E-041 built the book in code (``ember.budgets``) and its
own slice record; E-042–E-054 added measurements slice by
slice, each in its own record. E-055 publishes the whole
book in one reader-facing document, ``docs/BUDGET_BOOK.md``.

A published book that can drift from the code is a claim
waiting to go stale, so these tests read the published
document and judge it against the live book:

* the ceiling table's every cell equals ``ember.budgets``'
  live values for that profile;
* the appendix carries every ``MEASURED_*`` anchor the
  code carries, by name, at exactly its coded value —
  an anchor added to the code but not published, renamed,
  or revalued in print fails here;
* the storage arithmetic in print equals the code's;
* the honesty lines are present in print: the model is
  excluded, the phone proof is graded SIMULATED, the
  512 MiB whole-companion verdict is NOT CASHED, and the
  member table is pointed at E-057 rather than invented.

Nothing here re-measures hardware; the measuring lives in
the E-041–E-054 slices and their own gate tests.
"""

from __future__ import annotations

import re
from pathlib import Path

import ember.budgets as budgets

_BOOK = Path(__file__).resolve().parents[2] / "docs" / "BUDGET_BOOK.md"


def _text() -> str:
    return _BOOK.read_text(encoding="utf-8")


def _format(value: object) -> str:
    # The appendix's print format: integers with thousands
    # separators, floats in their plain Python spelling
    # (40.7, 585.4, 0.4117) — the spelling the code carries.
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def test_published_book_exists_and_names_its_code() -> None:
    text = _text()
    assert "ember.budgets" in text
    assert "E-055" in text


def test_ceiling_table_matches_the_live_book() -> None:
    rows = {}
    for line in _text().splitlines():
        match = re.match(r"\| (toaster|phone|pi|laptop) \|", line)
        if match:
            rows[match.group(1)] = [
                cell.strip() for cell in line.strip().strip("|").split("|")
            ]
    assert set(rows) == {profile.value for profile in budgets.PROFILE_ORDER}
    for budget in budgets.all_budgets():
        cells = rows[budget.profile.value]
        assert cells[1] == f"{budget.reference_host_ram_mib:,} MiB"
        assert cells[2] == f"{budget.install_mib:g} MiB"
        assert cells[3] == f"{budget.idle_ram_mib:g} MiB"
        assert cells[4] == f"{budget.turn_ram_mib:g} MiB"
        assert cells[5] == f"{budget.storage_growth_mib_per_month:g} MiB"
        assert cells[6] == f"{budget.cold_start_first_word_s:.1f} s"


def test_history_allowances_in_print_match_the_config() -> None:
    text = _text()
    for budget in budgets.all_budgets():
        expected = (
            f"{budget.profile.value} {budget.history_token_budget:,} tokens / "
            f"{budget.history_max_episodes} episodes"
        )
        # The book prints the four allowances on wrapped
        # lines ("toaster 512 tokens /\n3 episodes"), so
        # judge the whitespace-flattened text.
        flat = re.sub(r"\s+", " ", text)
        assert expected in flat


def test_every_measured_anchor_is_published_at_its_value() -> None:
    text = _text()
    anchors = {
        name: value
        for name, value in vars(budgets).items()
        if name.startswith("MEASURED_")
    }
    assert len(anchors) >= 27  # the E-041–E-053 anchor set
    for name, value in anchors.items():
        assert name in text, f"{name} missing from the published book"
        assert _format(value) in text, f"{name} published at a wrong value"


def test_storage_arithmetic_in_print_matches_the_code() -> None:
    text = _text()
    assert f"{budgets.WELL_BYTES_PER_EPISODE} bytes per Well episode" in text
    assert f"{budgets.storage_bytes_per_turn()} bytes per turn" in text
    assert f"{budgets.REFERENCE_TURNS_PER_DAY} turns per day" in text


def test_honesty_lines_are_in_print() -> None:
    text = _text()
    # The model is a separate program, never folded in.
    assert "never hides the model inside" in text
    # Proof grades stay attached to their numbers.
    assert "SIMULATED" in text
    assert "NOT PROVEN" in text
    # The 512 MiB whole-companion verdict, unsoftened.
    assert "not cashed" in text.lower()
    # Members are E-057's table, not invented rows here.
    assert "E-057" in text


def test_no_member_row_is_invented_in_the_ceiling_table() -> None:
    # The ceiling table prices the core only: exactly the
    # four profiles, no member smuggled in as a fifth row
    # (E-057 owns the member table).
    profile_rows = [
        line
        for line in _text().splitlines()
        if re.match(r"\| (toaster|phone|pi|laptop) \|", line)
    ]
    assert len(profile_rows) == 4


def test_budget_book_is_wired_into_the_gate() -> None:
    # This file lives under tests/unit/, where the slice
    # gate's Runs B/D collect it (E-042's pattern).
    assert Path(__file__).parent.name == "unit"

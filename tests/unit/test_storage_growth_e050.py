"""E-050 — Storage growth: a month of companionship, pinned.

**Verdict: within budget on every profile, no ceiling
moves, and the lifecycle rules do not tighten.** A
simulated month (30 days × 20 turns, E-041's typical-turn
fixture) run against the real Well and the real diary
grew Ember's stores by 408,566 B in all (0.39 MiB) — a
fifth of even the toaster's 2 MiB/month ceiling. Growth
was linear (4 KiB page steps, flat steady marginal of
585.4 B/episode out to 3,000 episodes), and the book's
694 B/turn statement stands unrevised: the month measured
680.9 B/turn all-in, so docket 91 closes — E-042's
808 B/turn was 30-episode page rounding plus a different
diary session shape. The one honest edge: essay-length
turns (~500 words a side, 6,144 B/episode) at the
reference rate would grow 3.51 MiB/month — over the
toaster's ceiling, inside the phone's — and that edge is
pinned here so it is never rounded into a pass; E-082's
lifecycle rules own the long-turn store. The record
lives in ``docs/architecture/E-050_STORAGE_GROWTH.md``.
"""

from __future__ import annotations

from pathlib import Path

from ember.budgets import (
    MEASURED_ESSAY_BYTES_PER_EPISODE,
    MEASURED_MONTH_DIARY_BYTES,
    MEASURED_MONTH_TOTAL_BYTES,
    MEASURED_MONTH_TURNS,
    MEASURED_MONTH_WELL_GROWTH_BYTES,
    MEASURED_WELL_STEADY_BYTES_PER_EPISODE,
    PROFILE_ORDER,
    budget_for,
    projected_monthly_growth_mib,
    storage_bytes_per_turn,
)
from ember.schemas.config import ConversationProfile

_MIB = 1024 * 1024
_TOASTER = ConversationProfile.TOASTER


def test_month_anchors_are_the_measured_record() -> None:
    # Pinned exactly: an anchor that quietly moves to fit
    # a heavier future is not an anchor. Device record:
    # docs/architecture/E-050_STORAGE_GROWTH.md.
    assert MEASURED_MONTH_TURNS == 600
    assert MEASURED_MONTH_WELL_GROWTH_BYTES == 352_256
    assert MEASURED_MONTH_DIARY_BYTES == 56_310
    assert MEASURED_MONTH_TOTAL_BYTES == 408_566
    assert MEASURED_MONTH_TOTAL_BYTES == (
        MEASURED_MONTH_WELL_GROWTH_BYTES + MEASURED_MONTH_DIARY_BYTES
    )
    assert MEASURED_WELL_STEADY_BYTES_PER_EPISODE == 585.4
    assert MEASURED_ESSAY_BYTES_PER_EPISODE == 6_144


def test_measured_month_fits_every_profiles_storage_ceiling() -> None:
    month_mib = MEASURED_MONTH_TOTAL_BYTES / _MIB
    assert month_mib < 0.5  # the whole month is under half a MiB
    for profile in PROFILE_ORDER:
        ceiling = budget_for(profile).storage_growth_mib_per_month
        assert month_mib < ceiling, profile
    # On the toaster the month uses barely a fifth of the
    # allowance — the headroom is the lifecycle's room.
    toaster = budget_for(_TOASTER).storage_growth_mib_per_month
    assert month_mib < toaster / 5


def test_book_statement_stands_unrevised_docket_91() -> None:
    # The book says 694 B/turn and projects 0.40 MiB/month.
    # The month measured 680.9 B/turn all-in — inside the
    # statement, so the statement was never optimistic and
    # E-042's 808 B/turn re-derivation is explained (small-N
    # page rounding + diary session shape), not adopted.
    measured_per_turn = MEASURED_MONTH_TOTAL_BYTES / MEASURED_MONTH_TURNS
    assert measured_per_turn < storage_bytes_per_turn()
    assert MEASURED_MONTH_TOTAL_BYTES / _MIB < projected_monthly_growth_mib()
    # And the Well's steady marginal undercuts the book's
    # per-episode constant out to 3,000 episodes.
    assert MEASURED_WELL_STEADY_BYTES_PER_EPISODE < 614


def test_toaster_break_even_is_over_a_hundred_turns_a_day() -> None:
    # At the measured all-in per-turn cost, the toaster's
    # monthly ceiling is only reached past ~100 turns a
    # day, every day — five times the reference workload.
    per_turn = MEASURED_MONTH_TOTAL_BYTES / MEASURED_MONTH_TURNS
    ceiling = budget_for(_TOASTER).storage_growth_mib_per_month * _MIB
    break_even_per_day = ceiling / per_turn / 30
    assert break_even_per_day > 100


def test_a_year_of_companionship_is_still_small() -> None:
    # Twelve reference months: under 5 MiB in a year, so
    # no profile needs pruning for budget reasons at
    # reference use — the fact E-082's lifecycle starts
    # from (its real subject is the long-turn store).
    year_mib = MEASURED_MONTH_TOTAL_BYTES * 12 / _MIB
    assert year_mib < 5.0


def test_essay_month_exceeds_the_toaster_and_fits_the_phone() -> None:
    # The honest edge, pinned in both directions: a month
    # of essay-length turns at the reference rate grows
    # past the toaster's storage ceiling (so the ceiling
    # is never quoted as a long-turn promise) and fits
    # the phone's with room.
    essay_month_mib = (
        MEASURED_ESSAY_BYTES_PER_EPISODE * MEASURED_MONTH_TURNS
        + MEASURED_MONTH_DIARY_BYTES
    ) / _MIB
    assert essay_month_mib > budget_for(_TOASTER).storage_growth_mib_per_month
    assert essay_month_mib < budget_for(
        ConversationProfile.PHONE
    ).storage_growth_mib_per_month


def test_storage_growth_proof_is_wired_into_the_gate() -> None:
    # This file lives under tests/unit/, where the slice
    # gate's Runs B/D collect it (E-042's pattern).
    assert Path(__file__).parent.name == "unit"

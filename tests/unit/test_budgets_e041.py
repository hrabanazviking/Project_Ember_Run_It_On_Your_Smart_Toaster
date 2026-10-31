"""E-041 — The budget book: per-profile ceilings, measured anchors.

The book (``ember.budgets``) is only worth anything if its
numbers cannot drift quietly. These tests pin:

1. The book covers exactly the four E-021 profiles, smallest
   first, and every ceiling grows (or holds) with the profile —
   a smaller machine never gets a larger allowance.
2. The measured core (E-041's anchors: install 978,843 B, idle
   40.7 MiB with the Well open, turn peak 40.1 MiB) fits EVERY
   profile, including the toaster — the founding fact of Part
   III, stated as a test so a future regression fails loudly
   here instead of being discovered on someone's small machine.
3. The history numbers in the book are E-021's own, read from
   the conversation config — never a second copy that can rot.
4. Storage growth is arithmetic, not rhetoric: one turn costs
   the measured 614 Well bytes + 80 diary bytes, and the
   reference workload (20 turns/day) projects to under half a
   MiB a month — inside even the toaster's ceiling with room
   for a much heavier month.
5. ``check_against`` names each broken ceiling in plain words;
   a shape that fits is judged by silence (an empty tuple).
"""

from __future__ import annotations

import pytest

from ember.budgets import (
    DIARY_BYTES_PER_TURN,
    MEASURED_IDLE_RAM_MIB,
    MEASURED_INSTALL_BYTES,
    MEASURED_TURN_RAM_MIB,
    PROFILE_ORDER,
    REFERENCE_TURNS_PER_DAY,
    WELL_BYTES_PER_EPISODE,
    all_budgets,
    budget_for,
    check_against,
    measured_shape_fits,
    projected_monthly_growth_mib,
    storage_bytes_per_turn,
)
from ember.schemas.config import ConversationConfig, ConversationProfile

_MIB = 1024 * 1024


def test_book_covers_exactly_the_four_profiles_smallest_first() -> None:
    assert PROFILE_ORDER == (
        ConversationProfile.TOASTER,
        ConversationProfile.PHONE,
        ConversationProfile.PI,
        ConversationProfile.LAPTOP,
    )
    assert [b.profile for b in all_budgets()] == list(PROFILE_ORDER)
    for profile in PROFILE_ORDER:
        assert budget_for(profile).profile is profile


def test_ceilings_never_shrink_as_profiles_grow() -> None:
    budgets = all_budgets()
    for field in (
        "reference_host_ram_mib",
        "install_mib",
        "idle_ram_mib",
        "turn_ram_mib",
        "storage_growth_mib_per_month",
    ):
        values = [getattr(b, field) for b in budgets]
        assert values == sorted(values), field
    # The toaster is the smallest in every dimension that is a cost.
    toaster = budgets[0]
    for other in budgets[1:]:
        assert toaster.install_mib < other.install_mib
        assert toaster.idle_ram_mib < other.idle_ram_mib
        assert toaster.turn_ram_mib <= other.turn_ram_mib
        assert toaster.storage_growth_mib_per_month < other.storage_growth_mib_per_month


def test_toaster_is_the_namesake_floor() -> None:
    toaster = budget_for(ConversationProfile.TOASTER)
    # The Tiny Device Profile's target (E-015 §5): a 512 MiB host.
    assert toaster.reference_host_ram_mib == 512
    # A turn never needs more than the idle shape plus headroom —
    # on the smallest profile the two ceilings meet.
    assert toaster.turn_ram_mib == toaster.idle_ram_mib


def test_measured_core_fits_every_profile() -> None:
    for profile in PROFILE_ORDER:
        assert measured_shape_fits(profile) == (), profile


def test_measured_anchors_are_the_e041_numbers() -> None:
    # Pinned so an anchor cannot be "adjusted" to make a failing
    # shape fit: changing one of these requires a new measurement
    # and a slice record, not a quiet edit.
    assert MEASURED_INSTALL_BYTES == 978_843
    assert MEASURED_IDLE_RAM_MIB == 40.7
    assert MEASURED_TURN_RAM_MIB == 40.1
    assert WELL_BYTES_PER_EPISODE == 614
    assert DIARY_BYTES_PER_TURN == 80
    assert REFERENCE_TURNS_PER_DAY == 20


def test_install_anchor_fits_the_toaster_with_room() -> None:
    install_mib = MEASURED_INSTALL_BYTES / _MIB
    assert install_mib < 1.0  # the core installs in under a MiB
    assert install_mib < budget_for(ConversationProfile.TOASTER).install_mib / 2


def test_history_numbers_come_from_e021_not_a_copy() -> None:
    for profile in PROFILE_ORDER:
        config = ConversationConfig(profile=profile)
        budget = budget_for(profile)
        assert budget.history_token_budget == config.resolved_token_budget
        assert budget.history_max_episodes == config.resolved_max_episodes
    assert budget_for(ConversationProfile.TOASTER).history_token_budget == 512
    assert budget_for(ConversationProfile.LAPTOP).history_token_budget == 4096


def test_storage_projection_is_measured_arithmetic() -> None:
    assert storage_bytes_per_turn() == 614 + 80
    monthly = projected_monthly_growth_mib()
    assert monthly == pytest.approx(694 * 20 * 30 / _MIB)
    assert monthly < 0.5  # under half a MiB a month at reference use
    # Five times the reference workload still fits the toaster;
    # ten times (200 turns a day) honestly does not — the ceiling
    # is a real bound, at ~86 turns a day on the smallest profile.
    assert projected_monthly_growth_mib(turns_per_day=100) < (
        budget_for(ConversationProfile.TOASTER).storage_growth_mib_per_month
    )
    assert projected_monthly_growth_mib(turns_per_day=200) > (
        budget_for(ConversationProfile.TOASTER).storage_growth_mib_per_month
    )


def test_check_against_names_each_broken_ceiling() -> None:
    problems = check_against(
        ConversationProfile.TOASTER,
        install_mib=99.0,
        idle_ram_mib=99.0,
        turn_ram_mib=99.0,
        storage_growth_mib_per_month=99.0,
    )
    assert len(problems) == 4
    joined = " ".join(problems)
    for word in ("install", "idle RAM", "turn RAM", "storage growth"):
        assert word in joined
    assert all("toaster" in p for p in problems)


def test_check_against_silent_when_the_shape_fits() -> None:
    assert (
        check_against(
            ConversationProfile.LAPTOP,
            install_mib=1.0,
            idle_ram_mib=40.0,
            turn_ram_mib=40.0,
            storage_growth_mib_per_month=0.4,
        )
        == ()
    )


def test_ram_ceilings_hold_the_measured_shape_with_headroom() -> None:
    # Every profile's turn ceiling is at least 1.5x the measured
    # turn peak: the book leaves room for a real model's client
    # side and a bigger history, without pretending the measured
    # fixture was the worst case.
    for budget in all_budgets():
        assert budget.turn_ram_mib >= 1.5 * MEASURED_TURN_RAM_MIB
        assert budget.idle_ram_mib >= 1.5 * MEASURED_IDLE_RAM_MIB or (
            budget.profile is ConversationProfile.TOASTER
            and budget.idle_ram_mib >= 1.5 * MEASURED_TURN_RAM_MIB
        )

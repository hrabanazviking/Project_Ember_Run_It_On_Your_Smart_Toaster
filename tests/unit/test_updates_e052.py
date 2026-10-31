"""E-052 — Update weight, pinned.

**An update is weighed before any channel exists to carry
one.** ``ember.updates`` prices a core update two ways —
the download (the package tree deflated into its wheel
shape) and the apply (peak disk = download + old + new,
the installer's moment when all three stand on disk) —
and judges it per profile against a download ceiling read
from the budget book (the profile's install ceiling: an
update may not download more than a whole install may
weigh). Metered connections are respected structurally:
:func:`decide_update` never answers "go ahead silently" —
over the ceiling is NO, metered is always ASK FIRST with
the byte price stated (at any size: smallness is not
consent), uninvited is INVITE REQUIRED, and only invited +
unmetered + within ceiling is READY. The measured anchors
live in the book (``MEASURED_UPDATE_*``: download 293,387 B
on this slice's final tree — re-pinned deliberately if the
tree's weight is re-measured, never drifted into). The
record lives in
``docs/architecture/E-052_UPDATE_WEIGHT.md``.
"""

from __future__ import annotations

from pathlib import Path

from ember.budgets import (
    MEASURED_UPDATE_APPLY_PEAK_BYTES,
    MEASURED_UPDATE_DOWNLOAD_BYTES,
    MEASURED_UPDATE_INSTALLED_BYTES,
    PROFILE_ORDER,
    budget_for,
)
from ember.schemas.config import ConversationProfile
from ember.updates import (
    UpdateDecision,
    costs_per_profile,
    decide_update,
    download_bytes_for_tree,
    download_ceiling_bytes,
    package_tree_bytes,
    plan_update,
)

_MIB = 1024 * 1024
_MEASURED = plan_update(
    download_bytes=MEASURED_UPDATE_DOWNLOAD_BYTES,
    installed_bytes=MEASURED_UPDATE_INSTALLED_BYTES,
)


def _tree(tmp_path: Path) -> Path:
    root = tmp_path / "ember"
    (root / "sub").mkdir(parents=True)
    (root / "__pycache__").mkdir()
    (root / "a.py").write_bytes(b"x" * 1000)
    (root / "sub" / "b.py").write_bytes(b"y" * 500)
    (root / "__pycache__" / "a.cpython-312.pyc").write_bytes(b"z" * 9999)
    (root / "stale.pyc").write_bytes(b"z" * 9999)
    return root


# ---------------------------------------------------------------- #
# Weighing                                                          #
# ---------------------------------------------------------------- #


def test_tree_bytes_exclude_bytecode_caches(tmp_path: Path) -> None:
    # The book's standing rule: caches are a runtime
    # artefact, not shipped weight.
    assert package_tree_bytes(_tree(tmp_path)) == 1500


def test_download_is_the_deflated_tree_and_deterministic(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    first = download_bytes_for_tree(root)
    assert first == download_bytes_for_tree(root)
    # Deflation earns its keep: the wire shape is smaller
    # than the tree it carries.
    assert 0 < first < package_tree_bytes(root)


def test_apply_peak_is_download_plus_old_plus_new() -> None:
    cost = plan_update(download_bytes=100, installed_bytes=1000)
    assert cost.apply_peak_disk_bytes == 2100


# ---------------------------------------------------------------- #
# The measured anchors                                              #
# ---------------------------------------------------------------- #


def test_measured_anchors_are_the_e052_numbers() -> None:
    # Pinned exactly (measurement method in the E-052
    # record): a re-measurement is a deliberate act that
    # re-pins here and in the book together.
    assert MEASURED_UPDATE_DOWNLOAD_BYTES == 293_387
    assert MEASURED_UPDATE_INSTALLED_BYTES == 775_675
    assert MEASURED_UPDATE_APPLY_PEAK_BYTES == 1_844_737
    assert MEASURED_UPDATE_APPLY_PEAK_BYTES == (
        MEASURED_UPDATE_DOWNLOAD_BYTES + 2 * MEASURED_UPDATE_INSTALLED_BYTES
    )


def test_measured_update_fits_every_profiles_download_ceiling() -> None:
    rows = costs_per_profile(_MEASURED)
    assert [row[0] for row in rows] == list(PROFILE_ORDER)
    assert all(fits for _, _, fits in rows)
    # The toaster, the floor: ~7x headroom under its 2 MiB.
    toaster_ceiling = download_ceiling_bytes(ConversationProfile.TOASTER)
    assert toaster_ceiling == 2 * _MIB
    assert MEASURED_UPDATE_DOWNLOAD_BYTES * 7 < toaster_ceiling


def test_download_ceiling_is_the_books_install_ceiling() -> None:
    # Derived, never a second copy: the ceiling IS the
    # budget book's install ceiling for the profile.
    for profile in PROFILE_ORDER:
        assert download_ceiling_bytes(profile) == int(
            budget_for(profile).install_mib * _MIB
        )


# ---------------------------------------------------------------- #
# The decision ladder                                               #
# ---------------------------------------------------------------- #


def test_ready_needs_invited_unmetered_and_within_ceiling() -> None:
    verdict = decide_update(
        _MEASURED, ConversationProfile.TOASTER, metered=False, user_invited=True
    )
    assert verdict.decision is UpdateDecision.READY


def test_metered_always_asks_first_and_states_the_price() -> None:
    verdict = decide_update(
        _MEASURED, ConversationProfile.LAPTOP, metered=True, user_invited=True
    )
    assert verdict.decision is UpdateDecision.ASK_FIRST
    assert f"{MEASURED_UPDATE_DOWNLOAD_BYTES:,}" in verdict.reason
    # Even a one-byte update asks on a metered wire:
    # smallness is not consent.
    tiny = plan_update(download_bytes=1, installed_bytes=1)
    assert (
        decide_update(
            tiny, ConversationProfile.TOASTER, metered=True, user_invited=True
        ).decision
        is UpdateDecision.ASK_FIRST
    )


def test_uninvited_is_never_silent() -> None:
    verdict = decide_update(
        _MEASURED, ConversationProfile.PHONE, metered=False, user_invited=False
    )
    assert verdict.decision is UpdateDecision.INVITE_REQUIRED


def test_over_ceiling_is_no_even_invited_and_unmetered() -> None:
    big = plan_update(download_bytes=3 * _MIB, installed_bytes=3 * _MIB)
    verdict = decide_update(
        big, ConversationProfile.TOASTER, metered=False, user_invited=True
    )
    assert verdict.decision is UpdateDecision.EXCEEDS_BUDGET
    # The same download fits the laptop's wider ceiling —
    # the judgement is per profile, honestly.
    assert (
        decide_update(
            big, ConversationProfile.LAPTOP, metered=False, user_invited=True
        ).decision
        is UpdateDecision.READY
    )


def test_budget_rung_speaks_before_the_metered_rung() -> None:
    # An update the profile cannot carry is refused for
    # that reason, not merely priced: the ladder's order
    # is part of the manners.
    big = plan_update(download_bytes=3 * _MIB, installed_bytes=3 * _MIB)
    verdict = decide_update(
        big, ConversationProfile.TOASTER, metered=True, user_invited=False
    )
    assert verdict.decision is UpdateDecision.EXCEEDS_BUDGET


def test_live_tree_still_fits_the_toaster_ceiling() -> None:
    # Re-derived, not re-asserted: the tree as it stands
    # today (this test included in the repo, the module
    # included in the package) still prices inside the
    # smallest profile's ceiling, so a future slice that
    # fattens the core past the line fails here loudly.
    root = Path(__file__).resolve().parents[2] / "src" / "ember"
    live = plan_update(
        download_bytes=download_bytes_for_tree(root),
        installed_bytes=package_tree_bytes(root),
    )
    assert live.download_bytes <= download_ceiling_bytes(
        ConversationProfile.TOASTER
    )
    assert (
        decide_update(
            live, ConversationProfile.TOASTER, metered=False, user_invited=True
        ).decision
        is UpdateDecision.READY
    )


def test_update_proof_is_wired_into_the_gate() -> None:
    assert Path(__file__).parent.name == "unit"

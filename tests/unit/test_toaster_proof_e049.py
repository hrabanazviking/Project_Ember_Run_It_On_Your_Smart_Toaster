"""E-049 — The Toaster Test, pinned.

**Verdict: the name is cashed for the Ember core, and
honestly NOT cashed for a whole self-contained companion
on a literal 512 MiB host.** The smallest honest target
the house can muster is a real device — Mimir, the
Raspberry Pi 5 of E-047 (no smaller computer exists in
the house; the phone/tablet were offline, E-048) — and
on it Ember ran the ``toaster`` profile end to end
through the day-one flow against the smallest real
model rung, qwen2.5:0.5b, with real embeddings. The
core's numbers fit the toaster ceilings with headroom.
The model side, measured the same day on the same
device (``ollama ps``: qwen runner 442 MB, nomic-embed
runner 565 MB), exceeds a 512 MiB host by itself — so
the whole-companion-on-512-MiB claim is graded, not
rounded into a pass. The record lives in
``docs/architecture/E-049_TOASTER_TEST.md``.

Two confusions these tests guard against:

* The toaster first word (2.18 s) is a REAL model
  thinking on REAL hardware; it is a model's cost and
  is never judged against the cold-start cap, even
  though it happens to sit inside it. The Ember-side
  number judged against the cap is ready (0.21 s).
* A Pi 5 is pi-class hardware running the toaster
  *profile*. These anchors re-anchor the toaster
  profile on a real ARM device; they do not claim a
  Pi Zero 2 W ran anything.
"""

from __future__ import annotations

from pathlib import Path

from ember.budgets import (
    MEASURED_TOASTER_PI_FIRST_WORD_REAL_MODEL_S,
    MEASURED_TOASTER_PI_INSTALLED_BYTES,
    MEASURED_TOASTER_PI_PEAK_RSS_MIB,
    MEASURED_TOASTER_PI_READY_S,
    budget_for,
    check_against,
    projected_monthly_growth_mib,
)
from ember.schemas.config import ConversationProfile

_TOASTER = ConversationProfile.TOASTER
_MIB = 1024 * 1024

# Model-side figures measured on the device by
# ``ollama ps`` during the test (E-049 doc §3) — the
# model house, charged to no Ember ceiling, recorded
# here only so the whole-host grading below is a test
# and not a paragraph.
_QWEN_RUNNER_MB = 442
_NOMIC_RUNNER_MB = 565
_OS_MB = 150  # the Tiny doc's OS figure, E-041 §2


def test_toaster_anchors_are_the_measured_record() -> None:
    # Pinned exactly: an anchor that quietly moves to fit
    # a slower future is not an anchor. Device record:
    # docs/architecture/E-049_TOASTER_TEST.md.
    assert MEASURED_TOASTER_PI_READY_S == 0.21
    assert MEASURED_TOASTER_PI_FIRST_WORD_REAL_MODEL_S == 2.18
    assert MEASURED_TOASTER_PI_PEAK_RSS_MIB == 27.2
    assert MEASURED_TOASTER_PI_INSTALLED_BYTES == 1_956_428


def test_toaster_shape_fits_the_toaster_ceilings() -> None:
    # Ember's own costs on the smallest profile — install,
    # peak RSS as both idle and turn shape, projected
    # storage growth, and Ember-side ready as the cold
    # start — fit the toaster profile, judged by the
    # book's own check. This is the half of the name
    # that is cashed.
    problems = check_against(
        _TOASTER,
        install_mib=MEASURED_TOASTER_PI_INSTALLED_BYTES / _MIB,
        idle_ram_mib=MEASURED_TOASTER_PI_PEAK_RSS_MIB,
        turn_ram_mib=MEASURED_TOASTER_PI_PEAK_RSS_MIB,
        storage_growth_mib_per_month=projected_monthly_growth_mib(),
        cold_start_first_word_s=MEASURED_TOASTER_PI_READY_S,
    )
    assert problems == ()


def test_toaster_ready_leaves_the_flat_cap_unrelaxed() -> None:
    cap = budget_for(_TOASTER).cold_start_first_word_s
    assert cap == 5.0
    assert MEASURED_TOASTER_PI_READY_S < cap


def test_real_model_first_word_is_record_not_breach() -> None:
    # The 0.5B rung's first word (2.18 s) sits inside the
    # cap numerically — and is still not the cap's
    # subject. The two anchors exist side by side so
    # nobody merges a model's thinking time into Ember's
    # startup figure, in either direction.
    assert MEASURED_TOASTER_PI_READY_S < MEASURED_TOASTER_PI_FIRST_WORD_REAL_MODEL_S
    assert MEASURED_TOASTER_PI_FIRST_WORD_REAL_MODEL_S < 5.0


def test_whole_companion_does_not_fit_a_literal_512_host() -> None:
    # Docket 66's grading, earned by measurement: the two
    # model runners the day-one shape loads sum past the
    # toaster's whole 512 MiB reference host on their own,
    # and even the chat model alone — plus the OS figure
    # and Ember's turn ceiling — does not fit. The core
    # fits (the tests above); the name's whole-companion
    # reading on a literal 512 MiB host is NOT cashed,
    # and this test keeps that verdict from softening.
    host = budget_for(_TOASTER).reference_host_ram_mib
    assert host == 512
    assert _QWEN_RUNNER_MB + _NOMIC_RUNNER_MB > host
    assert _QWEN_RUNNER_MB + _OS_MB + budget_for(_TOASTER).turn_ram_mib > host


def test_toaster_proof_is_wired_into_the_gate() -> None:
    # This file lives under tests/unit/, where the slice
    # gate's Runs B/D collect it (E-042's pattern).
    assert Path(__file__).parent.name == "unit"

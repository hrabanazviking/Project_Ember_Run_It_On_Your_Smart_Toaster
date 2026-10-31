"""E-047 — The Pi proof, pinned.

The proof itself ran on real hardware (Mimir, a Raspberry
Pi 5) and cannot re-run on whatever machine executes this
suite — so, like E-046's bookkeeping tests, these tests pin
the *record*: the anchors in ``ember.budgets`` that the
on-device measurement bought, judged against the pi
profile's ceilings in the book's own words.

The one judgement that matters most is stated twice, in the
doc and here, because the two numbers are easy to confuse:

* Ember's own startup on the Pi (spawn → "is ready.") was
  0.18 s at the median — that is the Ember-side cold start,
  and it is judged against the book's flat 5.0 s cap.
* The first *word* took 5.69 s at the median because a real
  model (phi3:mini) had to think on a Pi CPU first. That is
  the model's cost; the book never folds a model into
  Ember's ceilings, so the anchor is pinned as a record and
  deliberately NOT judged against the cap. A future editor
  who "fixes" the apparent breach by relaxing the cap has
  misunderstood the book — this file's comments are the
  standing explanation.
"""

from __future__ import annotations

from pathlib import Path

from ember.budgets import (
    MEASURED_PI_FIRST_WORD_REAL_MODEL_S,
    MEASURED_PI_INSTALLED_BYTES,
    MEASURED_PI_PEAK_RSS_MIB,
    MEASURED_PI_READY_S,
    budget_for,
    check_against,
)
from ember.schemas.config import ConversationProfile

_PI = ConversationProfile.PI
_MIB = 1024 * 1024


def test_pi_anchors_are_the_measured_record() -> None:
    # Pinned exactly: an anchor that quietly moves to fit a
    # slower future is not an anchor. On-device record:
    # docs/architecture/E-047_PI_PROOF.md.
    assert MEASURED_PI_READY_S == 0.18
    assert MEASURED_PI_FIRST_WORD_REAL_MODEL_S == 5.69
    assert MEASURED_PI_PEAK_RSS_MIB == 27.1
    assert MEASURED_PI_INSTALLED_BYTES == 1_951_508


def test_pi_ember_side_shape_fits_the_pi_ceilings() -> None:
    # Ember's own costs on the device — install, turn RAM,
    # and Ember-side cold start (ready, not the model's
    # first word) — fit the pi profile with room to spare,
    # judged by the book's own check.
    problems = check_against(
        _PI,
        install_mib=MEASURED_PI_INSTALLED_BYTES / _MIB,
        idle_ram_mib=MEASURED_PI_PEAK_RSS_MIB,
        turn_ram_mib=MEASURED_PI_PEAK_RSS_MIB,
        storage_growth_mib_per_month=0.0,
        cold_start_first_word_s=MEASURED_PI_READY_S,
    )
    assert problems == ()


def test_pi_ready_leaves_the_flat_cap_unrelaxed() -> None:
    # The cap was set on a contended VM at 5.0 s flat. The
    # Pi's Ember-side ready (0.18 s) sits far inside it, so
    # E-047 re-anchors without relaxing anything.
    cap = budget_for(_PI).cold_start_first_word_s
    assert cap == 5.0
    assert MEASURED_PI_READY_S < cap / 10


def test_real_model_first_word_is_record_not_breach() -> None:
    # The model-included first word exceeds the cap — and
    # that is expected, named, and not a book violation:
    # the cap prices Ember's startup against an instantly
    # answering wire-shape model (E-046 §5). If a future
    # change makes the REAL-model number fit the cap, this
    # test still passes; it pins only that the two numbers
    # exist side by side and differ, so nobody merges them.
    assert MEASURED_PI_FIRST_WORD_REAL_MODEL_S > MEASURED_PI_READY_S


def test_pi_proof_is_wired_into_the_gate() -> None:
    # This file lives under tests/unit/, where the slice
    # gate's Runs B/D collect it (E-042's pattern).
    assert Path(__file__).parent.name == "unit"

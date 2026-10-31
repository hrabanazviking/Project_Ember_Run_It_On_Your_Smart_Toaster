"""E-048 — The phone-class proof (SIMULATED), pinned.

**Proof grade: simulated.** No real phone ran Ember in
this slice: the house's paired phone (Galaxy S26 Ultra)
was offline when checked, and the tree holds no Android
runtime or install path for the core. What ran was the
phone conversation profile on the campaign VM under a
simulation envelope — 2 CPUs pinned, a 512 MiB RSS
watchdog, a loopback wire-shape model answering instantly
(the E-046/E-029 shape) — so the anchors below price
Ember's own behaviour in a phone-shaped room, on faster
x86 cores, and must never be quoted as a phone's numbers.
The record lives in ``docs/architecture/E-048_PHONE_PROOF.md``.

Two confusions these tests guard against:

* The simulated first word (1.79 s) is an Ember-side
  number against an instantly answering model, so it is
  judged against the book's flat 5.0 s cold-start cap —
  unlike the Pi's real-model first word (E-047), which is
  a model's cost and is never judged against the cap.
* Simulation is not a device. The Pi anchors are real
  hardware; these are not, and the test that keeps the
  two families visibly distinct is deliberate.
"""

from __future__ import annotations

from pathlib import Path

from ember.budgets import (
    MEASURED_INSTALL_BYTES,
    MEASURED_PHONE_SIM_FIRST_WORD_S,
    MEASURED_PHONE_SIM_PEAK_RSS_MIB,
    MEASURED_PHONE_SIM_READY_S,
    MEASURED_PI_FIRST_WORD_REAL_MODEL_S,
    budget_for,
    check_against,
    projected_monthly_growth_mib,
)
from ember.schemas.config import ConversationProfile

_PHONE = ConversationProfile.PHONE
_MIB = 1024 * 1024


def test_phone_sim_anchors_are_the_measured_record() -> None:
    # Pinned exactly: an anchor that quietly moves to fit a
    # slower future is not an anchor. Simulation record:
    # docs/architecture/E-048_PHONE_PROOF.md.
    assert MEASURED_PHONE_SIM_READY_S == 1.77
    assert MEASURED_PHONE_SIM_FIRST_WORD_S == 1.79
    assert MEASURED_PHONE_SIM_PEAK_RSS_MIB == 43.0


def test_phone_sim_shape_fits_the_phone_ceilings() -> None:
    # Ember's own simulated costs — the VM install anchor
    # (the install is the same bytes on any host), peak RSS
    # as both idle and turn shape, the book's projected
    # storage growth, and the simulated first word as the
    # cold start — fit the phone profile, judged by the
    # book's own check.
    problems = check_against(
        _PHONE,
        install_mib=MEASURED_INSTALL_BYTES / _MIB,
        idle_ram_mib=MEASURED_PHONE_SIM_PEAK_RSS_MIB,
        turn_ram_mib=MEASURED_PHONE_SIM_PEAK_RSS_MIB,
        storage_growth_mib_per_month=projected_monthly_growth_mib(),
        cold_start_first_word_s=MEASURED_PHONE_SIM_FIRST_WORD_S,
    )
    assert problems == ()


def test_phone_sim_first_word_leaves_the_flat_cap_unrelaxed() -> None:
    # The cap was set on a contended VM at 5.0 s flat. The
    # simulated phone-profile first word (1.79 s, wire-shape
    # model) sits inside it, so E-048 re-anchors by
    # simulation without relaxing anything.
    cap = budget_for(_PHONE).cold_start_first_word_s
    assert cap == 5.0
    assert MEASURED_PHONE_SIM_FIRST_WORD_S < cap


def test_simulation_is_not_mistaken_for_a_real_device() -> None:
    # The Pi's 5.69 s is a REAL model thinking on REAL
    # hardware; the phone-sim's 1.79 s is a wire-shape model
    # on a VM. The two anchors exist side by side precisely
    # so nobody quotes the simulated number as a phone's —
    # if a future slice runs a real phone, it adds its own
    # anchors instead of overwriting these.
    assert MEASURED_PHONE_SIM_FIRST_WORD_S < MEASURED_PI_FIRST_WORD_REAL_MODEL_S
    assert MEASURED_PHONE_SIM_READY_S != MEASURED_PHONE_SIM_FIRST_WORD_S


def test_phone_proof_is_wired_into_the_gate() -> None:
    # This file lives under tests/unit/, where the slice
    # gate's Runs B/D collect it (E-042's pattern).
    assert Path(__file__).parent.name == "unit"

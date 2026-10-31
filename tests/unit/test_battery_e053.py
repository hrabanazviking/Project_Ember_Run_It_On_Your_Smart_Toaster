"""E-053 — Battery-shaped behaviour, pinned.

**Background work is shaped by the battery; a person's
turn never is.** ``ember.battery`` reads the Linux
power-supply shape (capacity + status under
``/sys/class/power_supply``; absent or unparseable reads
``None``, never a guess — the campaign VM and the house
Pi have no battery at all), judges it into a duty plan —
FULL (charging / no battery / unknown / ≥ 50%),
CONSERVE (< 50%: bursts of 4 batches, one 5 s rest),
LOW (< 20%: a batch at a time, 15 s rests), CRITICAL
(< 10%: every batch followed by a 30 s rest) — and a
:class:`DutyCycler`, consulted *between batches* of bulk
embedding like E-051's patience hook, rests **once** per
spent burst in a single blocking sleep of the full rest:
no busy-wait, no polling, no chopped micro-sleeps. The
measured drain shape (CPU duty, the drain's cause — a
real battery's percent-per-hour drain is NOT PROVEN, no
house battery device can run Ember) is pinned in the
budget book (``MEASURED_BATTERY_*`` / ``MEASURED_DUTY_*``).
The record lives in
``docs/architecture/E-053_BATTERY_BEHAVIOUR.md``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from ember.battery import (
    CONSERVE_BELOW_PCT,
    CONSERVE_BURST_BATCHES,
    CONSERVE_REST_S,
    CRITICAL_BELOW_PCT,
    CRITICAL_BURST_BATCHES,
    CRITICAL_REST_S,
    LOW_BELOW_PCT,
    LOW_BURST_BATCHES,
    LOW_REST_S,
    BatteryReading,
    DutyCycler,
    DutyMode,
    assess,
    plan_for,
    read_battery,
)
from ember.budgets import (
    MEASURED_BATTERY_REST_CPU_S,
    MEASURED_DUTY_CONSERVE_CPU_FRACTION,
    MEASURED_DUTY_FULL_CPU_FRACTION,
)
from ember.schemas.config import EmbeddingConfig
from ember.well.smidja.embed_client import OllamaEmbedClient


def _reading(percent: float | None, charging: bool | None, present: bool = True) -> BatteryReading:
    return BatteryReading(percent=percent, charging=charging, present=present)


def _cycler(percent: float, sleeps: list[float]) -> DutyCycler:
    assessment = assess(_reading(percent, charging=False))
    return DutyCycler(assess_fn=lambda: assessment, sleep=sleeps.append)


# ---------------------------------------------------------------- #
# The policy lines                                                  #
# ---------------------------------------------------------------- #


def test_policy_lines_are_the_stated_manners() -> None:
    # Pinned exactly: a line that quietly moves is not a line.
    assert CONSERVE_BELOW_PCT == 50.0
    assert LOW_BELOW_PCT == 20.0
    assert CRITICAL_BELOW_PCT == 10.0
    assert CRITICAL_BELOW_PCT < LOW_BELOW_PCT < CONSERVE_BELOW_PCT
    assert (CONSERVE_BURST_BATCHES, CONSERVE_REST_S) == (4, 5.0)
    assert (LOW_BURST_BATCHES, LOW_REST_S) == (1, 15.0)
    assert (CRITICAL_BURST_BATCHES, CRITICAL_REST_S) == (1, 30.0)
    # FULL is the unshaped shape: no burst limit, no rest.
    full = plan_for(DutyMode.FULL)
    assert full.burst_batches is None
    assert full.rest_s == 0.0


def test_assess_charge_ladder() -> None:
    assert assess(_reading(100.0, False)).plan.mode is DutyMode.FULL
    assert assess(_reading(50.0, False)).plan.mode is DutyMode.FULL
    assert assess(_reading(49.9, False)).plan.mode is DutyMode.CONSERVE
    assert assess(_reading(20.0, False)).plan.mode is DutyMode.CONSERVE
    assert assess(_reading(19.9, False)).plan.mode is DutyMode.LOW
    assert assess(_reading(10.0, False)).plan.mode is DutyMode.LOW
    assert assess(_reading(9.9, False)).plan.mode is DutyMode.CRITICAL
    assert assess(_reading(0.0, False)).plan.mode is DutyMode.CRITICAL


def test_assess_charging_and_unknown_never_drain() -> None:
    # On the charger, even a nearly empty battery is not
    # being spent — the charger votes FULL at any gauge.
    plugged = assess(_reading(5.0, charging=True))
    assert plugged.plan.mode is DutyMode.FULL
    assert "charger" in plugged.reason
    # No battery at all (the VM, the Pi): mains-fed, stated.
    none = assess(_reading(None, None, present=False))
    assert none.plan.mode is DutyMode.FULL
    assert "no battery" in none.reason
    # An unreadable gauge never invents a crisis.
    unknown = assess(_reading(None, charging=False))
    assert unknown.plan.mode is DutyMode.FULL
    assert "cannot be read" in unknown.reason


# ---------------------------------------------------------------- #
# Reading the battery                                               #
# ---------------------------------------------------------------- #


def _supply(root: Path, name: str, **files: str) -> None:
    supply = root / name
    supply.mkdir(parents=True)
    for key, value in files.items():
        (supply / key).write_text(value, encoding="ascii")


def test_read_battery_reads_capacity_and_status(tmp_path: Path) -> None:
    _supply(tmp_path, "BAT0", type="Battery\n", capacity="42\n", status="Discharging\n")
    reading = read_battery(tmp_path)
    assert reading.present is True
    assert reading.percent == 42.0
    assert reading.charging is False


def test_read_battery_skips_mains_and_maps_charging(tmp_path: Path) -> None:
    _supply(tmp_path, "AC", type="Mains\n", online="1\n")
    _supply(tmp_path, "BAT1", type="Battery\n", capacity="88\n", status="Charging\n")
    reading = read_battery(tmp_path)
    assert reading.percent == 88.0
    assert reading.charging is True


def test_read_battery_absent_and_malformed_are_unknown(tmp_path: Path) -> None:
    # No root at all, and an empty root: no battery, stated.
    assert read_battery(tmp_path / "missing").present is False
    assert read_battery(tmp_path).percent is None
    # A battery whose capacity will not parse: present,
    # but the charge is unknown — never guessed.
    _supply(tmp_path, "BAT0", type="Battery\n", capacity="full-ish\n", status="Discharging\n")
    reading = read_battery(tmp_path)
    assert reading.present is True
    assert reading.percent is None
    # An out-of-range capacity is not a reading either.
    _supply(tmp_path, "BAT1", type="Battery\n", capacity="250\n", status="Discharging\n")
    assert read_battery(tmp_path).percent is None


def test_read_battery_on_this_machine_is_honest() -> None:
    # The campaign VM exposes no battery; whatever host
    # runs this test, the reader must agree with the
    # sysfs shape: a reading is either absent-unknown or
    # a percent inside 0–100 — never anything else.
    reading = read_battery()
    if not reading.present:
        assert reading.percent is None
    else:
        assert reading.percent is not None
        assert 0.0 <= reading.percent <= 100.0


# ---------------------------------------------------------------- #
# Duty cycling — bursts, single blocking rests, no busy-wait        #
# ---------------------------------------------------------------- #


def test_cycler_full_never_rests() -> None:
    sleeps: list[float] = []
    cycler = _cycler(90.0, sleeps)
    for _ in range(10):
        outcome = cycler.between_batches()
        assert outcome.rested_s == 0.0
    assert sleeps == []
    assert cycler.rests == 0


def test_cycler_conserve_rests_once_per_spent_burst() -> None:
    sleeps: list[float] = []
    cycler = _cycler(40.0, sleeps)
    rested = [cycler.between_batches().rested_s for _ in range(9)]
    # Bursts of 4: consultations 4 and 8 rest, each ONE
    # sleep call of the full 5 s — the no-busy-wait shape
    # (never chopped polls summing to the rest).
    assert rested == [0.0, 0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 5.0, 0.0]
    assert sleeps == [CONSERVE_REST_S, CONSERVE_REST_S]
    assert cycler.rests == 2
    assert cycler.rested_s == 10.0


def test_cycler_low_and_critical_rest_after_every_batch() -> None:
    sleeps: list[float] = []
    low = _cycler(15.0, sleeps)
    low.between_batches()
    low.between_batches()
    assert sleeps == [LOW_REST_S, LOW_REST_S]

    sleeps.clear()
    critical = _cycler(5.0, sleeps)
    outcome = critical.between_batches()
    assert sleeps == [CRITICAL_REST_S]
    assert outcome.rested_s == CRITICAL_REST_S
    assert outcome.assessment.plan.mode is DutyMode.CRITICAL


def test_cycler_rereads_the_battery_each_consultation() -> None:
    # A charger plugged in mid-job unshapes the rest of
    # the job at the next batch boundary: the cycler
    # re-reads rather than caching the first judgement.
    readings = iter(
        [
            assess(_reading(40.0, charging=False)),
            assess(_reading(40.0, charging=False)),
            assess(_reading(40.0, charging=False)),
            assess(_reading(40.0, charging=True)),
            assess(_reading(40.0, charging=True)),
        ]
    )
    sleeps: list[float] = []
    cycler = DutyCycler(assess_fn=lambda: next(readings), sleep=sleeps.append)
    for _ in range(5):
        cycler.between_batches()
    # Three CONSERVE consultations counted 1-2-3 (no rest
    # yet), then charging read FULL and the burst counter
    # is never spent under the unshaped plan.
    assert sleeps == []
    assert cycler.last_assessment is not None
    assert cycler.last_assessment.plan.mode is DutyMode.FULL


# ---------------------------------------------------------------- #
# The measured drain shape                                          #
# ---------------------------------------------------------------- #


def test_measured_drain_shape_anchors_are_the_e053_numbers() -> None:
    # Pinned exactly (method in the E-053 record): a
    # re-measurement is a deliberate act that re-pins
    # here and in the book together.
    assert MEASURED_BATTERY_REST_CPU_S == 0.0
    assert MEASURED_DUTY_FULL_CPU_FRACTION == 0.4117
    assert MEASURED_DUTY_CONSERVE_CPU_FRACTION == 0.1885
    # The shape itself: duty-cycled background work spent
    # less than half the CPU-over-wall of the unshaped
    # job run beside it under the same contention.
    assert MEASURED_DUTY_CONSERVE_CPU_FRACTION < MEASURED_DUTY_FULL_CPU_FRACTION / 2


# ---------------------------------------------------------------- #
# The wiring: bulk embedding duty-cycles between batches            #
# ---------------------------------------------------------------- #


class _MockResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._body = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _MockResponse:
        return self

    def __exit__(self, *_: object) -> None:
        return None


def _factory(req: Any, *, timeout: float = 0.0) -> _MockResponse:
    payload = json.loads(req.data)
    return _MockResponse({"embeddings": [[1.0, 0.0] for _ in payload["input"]]})


def test_embed_battery_hook_fires_between_batches_only() -> None:
    calls: list[int] = []
    cfg = EmbeddingConfig(batch_size=2)
    client = OllamaEmbedClient(
        config=cfg, max_attempts=1, battery_hook=lambda: calls.append(1)
    )
    with patch("urllib.request.urlopen", side_effect=_factory):
        vectors = client.embed(["a", "b", "c", "d", "e"])
    assert len(vectors) == 5
    assert calls == [1, 1]


def test_single_batch_embed_is_never_rested() -> None:
    calls: list[int] = []
    cfg = EmbeddingConfig(batch_size=8)
    client = OllamaEmbedClient(
        config=cfg, max_attempts=1, battery_hook=lambda: calls.append(1)
    )
    with patch("urllib.request.urlopen", side_effect=_factory):
        vectors = client.embed(["only", "turn"])
    assert len(vectors) == 2
    assert calls == []


def test_battery_proof_is_wired_into_the_gate() -> None:
    # This file lives under tests/unit/, where the slice
    # gate's Runs B/D collect it (E-042's pattern).
    assert Path(__file__).parent.name == "unit"

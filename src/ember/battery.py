"""Battery-shaped behaviour — duty cycling, no busy-wait (E-053).

Part III, slice E-053. Roadmap line: "Battery-shaped
behaviour (phone-class): duty cycling, no busy-wait,
measured drain shape."

A companion that lives on a phone-class device lives on
a battery, and a battery is a budget that refills slowly
or not at all until someone finds a charger. Until this
slice Ember's background work had no battery manners at
all — a tree-wide search for power-supply, battery, or
duty-cycle code found nothing in the core. The one bulk
background act (Smiðja's ingest embedding, hundreds of
batches back to back) would run flat-out from a full
charge to an empty one without once asking how much
charge was left. Foreground work is different: a person
waiting on a reply is the companion's whole job, and it
is never duty-cycled — this slice shapes *background*
work only, exactly as E-051's patience etiquette does.

The manners, in three parts:

* **Reading the battery (stdlib only).** The Linux
  power-supply shape under ``/sys/class/power_supply``
  (the shape Android-class and embedded Linux hosts
  expose): a battery supply's ``capacity`` percent and
  ``status``. A battery that is not there, or a reading
  that cannot be parsed, is *unknown* (``None``), never
  a guessed number — the campaign VM and the house Pi
  expose no battery at all, and on a mains-fed machine
  "no battery" is the truth, so duty there is unshaped.
* **Judging the charge (pure).** :func:`assess` folds
  one reading into a :class:`DutyPlan`: ``FULL``
  (charging, no battery, or charge at/above the conserve
  line — background work runs unshaped), ``CONSERVE``
  (below 50% and off the charger — bursts of batches
  rest between), ``LOW`` (below 20% — a batch at a
  time, long rests), ``CRITICAL`` (below 10% — one
  batch, then a proper rest, every time: the work
  crawls rather than stops, and the person can still
  interrupt it). Charging always votes FULL: a device
  on its charger is not spending its battery, whatever
  the gauge says. An unknown charge never votes either
  way — unknown is FULL's reason stated plainly, not a
  dressed-up guess.
* **Duty cycling, with no busy-wait anywhere.** A
  :class:`DutyCycler` is consulted *between batches*
  of bulk work (the E-051 hook point in the embedding
  client). It counts batches since the last rest; when
  a burst is spent it rests **once**, in a single
  blocking ``sleep`` of the plan's full rest — never a
  polling loop, never chopped micro-sleeps that wake
  the CPU to check the clock. During a rest the process
  spends ~no CPU (the drain-shape probe measured
  0.000 s of process CPU across a 5 s CONSERVE rest on
  the VM; the full measured shape lives in
  ``docs/architecture/E-053_BATTERY_BEHAVIOUR.md`` and
  its anchors are pinned in ``ember.budgets``). A
  single-batch embed — the foreground shape — never
  reaches the hook at all, so a person's turn is never
  rested.

Policy constants, not measurements: the charge lines
and rest lengths below are stated manners, pinned by
the E-053 tests so they can only change deliberately.
What a real battery's *drain* (percent per hour) would
be is NOT claimed anywhere in this slice: the house
holds no battery device that can run Ember today (the
paired phone was offline at E-048 and has no Ember
runtime), so the measured shape is the drain's *cause*
— CPU duty over wall time — and the record says so.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# --------------------------------------------------------------------- #
# Policy — the stated manners (E-053)                                   #
# --------------------------------------------------------------------- #

#: Charge (%) below which a discharging battery asks
#: background work to conserve: bursts rest between.
CONSERVE_BELOW_PCT = 50.0

#: Charge (%) below which background work slows to a
#: batch at a time with long rests.
LOW_BELOW_PCT = 20.0

#: Charge (%) below which every single batch is
#: followed by a full rest — the work crawls, stated,
#: rather than silently stopping or silently draining.
CRITICAL_BELOW_PCT = 10.0

#: CONSERVE: batches per burst, then one rest.
CONSERVE_BURST_BATCHES = 4
#: CONSERVE: the rest between bursts, seconds.
CONSERVE_REST_S = 5.0

#: LOW: batches per burst (a batch at a time), then
#: one long rest.
LOW_BURST_BATCHES = 1
#: LOW: the rest after each batch, seconds.
LOW_REST_S = 15.0

#: CRITICAL: batches per burst, then a full rest.
CRITICAL_BURST_BATCHES = 1
#: CRITICAL: the rest after each batch, seconds —
#: at this charge the battery outranks the backlog.
CRITICAL_REST_S = 30.0

#: Where Linux exposes power supplies (the phone-class
#: and embedded shape).
POWER_SUPPLY_ROOT = Path("/sys/class/power_supply")


class DutyMode(Enum):
    """How background work is shaped at one charge level."""

    FULL = "full"
    CONSERVE = "conserve"
    LOW = "low"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class BatteryReading:
    """One reading of the battery, unknowns kept unknown."""

    #: Charge percent (0–100), or ``None`` when no
    #: battery reports one — never guessed.
    percent: float | None
    #: True on the charger (charging or full), False
    #: discharging, ``None`` when the status is unknown
    #: or there is no battery to have one.
    charging: bool | None
    #: True when a battery supply exists at all.
    present: bool


@dataclass(frozen=True, slots=True)
class DutyPlan:
    """The duty shape one mode imposes on background work."""

    mode: DutyMode
    #: Batches of background work per burst before a
    #: rest; ``None`` means unshaped (no rest is ever
    #: imposed) — the FULL shape.
    burst_batches: int | None
    #: The single blocking rest after a spent burst.
    rest_s: float


@dataclass(frozen=True, slots=True)
class BatteryAssessment:
    """One reading judged: the plan, with its reason."""

    reading: BatteryReading
    plan: DutyPlan
    #: One plain sentence naming the deciding fact.
    reason: str


@dataclass(frozen=True, slots=True)
class DutyRest:
    """What one between-batches consultation did."""

    assessment: BatteryAssessment
    #: Seconds slept by this consultation (0 when the
    #: burst was not spent or the duty is FULL).
    rested_s: float
    #: Background batches completed since the last rest
    #: (the burst counter after this consultation).
    batches_since_rest: int


_PLANS: dict[DutyMode, DutyPlan] = {
    DutyMode.FULL: DutyPlan(mode=DutyMode.FULL, burst_batches=None, rest_s=0.0),
    DutyMode.CONSERVE: DutyPlan(
        mode=DutyMode.CONSERVE,
        burst_batches=CONSERVE_BURST_BATCHES,
        rest_s=CONSERVE_REST_S,
    ),
    DutyMode.LOW: DutyPlan(
        mode=DutyMode.LOW,
        burst_batches=LOW_BURST_BATCHES,
        rest_s=LOW_REST_S,
    ),
    DutyMode.CRITICAL: DutyPlan(
        mode=DutyMode.CRITICAL,
        burst_batches=CRITICAL_BURST_BATCHES,
        rest_s=CRITICAL_REST_S,
    ),
}


def plan_for(mode: DutyMode) -> DutyPlan:
    """The duty plan for one mode."""
    return _PLANS[mode]


# --------------------------------------------------------------------- #
# Reading the battery                                                   #
# --------------------------------------------------------------------- #


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="ascii").strip()
    except (OSError, ValueError):
        return None


def read_battery(root: Path = POWER_SUPPLY_ROOT) -> BatteryReading:
    """Read this machine's battery, or say plainly there is none.

    Supplies are ``<root>/*/`` directories; a supply is
    a battery when its ``type`` reads ``Battery`` (a
    type that cannot be read leaves the supply a
    candidate — phones name theirs plainly, but a
    missing type file must not hide a real battery).
    The first battery-shaped supply with a parseable
    ``capacity`` decides the reading. ``status`` maps
    Charging/Full → charging, Discharging → not
    charging, anything else → unknown. No battery
    supply at all (the VM, the Pi) reads ``present``
    False and both values ``None``.
    """
    try:
        supplies = sorted(p for p in root.iterdir() if p.is_dir())
    except OSError:
        return BatteryReading(percent=None, charging=None, present=False)

    saw_battery = False
    for supply in supplies:
        supply_type = _read_text(supply / "type")
        if supply_type is not None and supply_type != "Battery":
            continue
        saw_battery = True
        capacity = _read_text(supply / "capacity")
        if capacity is None:
            continue
        try:
            percent = float(capacity)
        except ValueError:
            continue
        if not 0.0 <= percent <= 100.0:
            continue
        status = _read_text(supply / "status")
        charging: bool | None
        if status in ("Charging", "Full"):
            charging = True
        elif status == "Discharging":
            charging = False
        else:
            charging = None
        return BatteryReading(percent=percent, charging=charging, present=True)

    return BatteryReading(percent=None, charging=None, present=saw_battery)


# --------------------------------------------------------------------- #
# Judging the charge (pure)                                             #
# --------------------------------------------------------------------- #


def assess(reading: BatteryReading) -> BatteryAssessment:
    """Judge one battery reading into a duty plan.

    Order: no battery / charging / unknown charge all
    leave background work unshaped, each with its own
    plain reason — a mains-fed machine is not asked to
    pretend it has a battery, and an unreadable gauge
    never invents a crisis. A discharging battery is
    judged by the stated lines, strictest first.
    """
    if not reading.present:
        return BatteryAssessment(
            reading=reading,
            plan=_PLANS[DutyMode.FULL],
            reason="no battery is present — this machine is mains-fed, "
            "so background work is not battery-shaped",
        )
    if reading.charging is True:
        return BatteryAssessment(
            reading=reading,
            plan=_PLANS[DutyMode.FULL],
            reason="the device is on its charger — background work "
            "is not spending the battery",
        )
    if reading.percent is None:
        return BatteryAssessment(
            reading=reading,
            plan=_PLANS[DutyMode.FULL],
            reason="the battery's charge cannot be read — unknown "
            "never votes, so background work is not battery-shaped",
        )
    percent = reading.percent
    if percent < CRITICAL_BELOW_PCT:
        mode = DutyMode.CRITICAL
        reason = (
            f"the battery is critical at {percent:.0f}% — every "
            "batch of background work is followed by a full rest"
        )
    elif percent < LOW_BELOW_PCT:
        mode = DutyMode.LOW
        reason = (
            f"the battery is low at {percent:.0f}% — background "
            "work runs a batch at a time with long rests"
        )
    elif percent < CONSERVE_BELOW_PCT:
        mode = DutyMode.CONSERVE
        reason = (
            f"the battery is at {percent:.0f}% — background work "
            "runs in bursts with rests between"
        )
    else:
        mode = DutyMode.FULL
        reason = (
            f"the battery is at {percent:.0f}% — background work "
            "runs unshaped"
        )
    return BatteryAssessment(reading=reading, plan=_PLANS[mode], reason=reason)


def assess_system(*, root: Path = POWER_SUPPLY_ROOT) -> BatteryAssessment:
    """Read this machine's battery right now and judge it."""
    return assess(read_battery(root))


# --------------------------------------------------------------------- #
# Duty cycling — between batches, one blocking rest, no busy-wait       #
# --------------------------------------------------------------------- #


class DutyCycler:
    """Shapes bulk background work to the battery.

    Consulted *between batches* (the embedding client's
    hook point). Each consultation re-reads the battery,
    so a charger plugged in mid-job unshapes the rest of
    the job at the next batch boundary, and a falling
    charge tightens the shape the same way. When the
    current plan's burst is spent, the cycler rests
    **once**: a single blocking ``sleep`` of the full
    rest — the no-busy-wait rule, pinned by the E-053
    tests (the recorded sleep calls are exactly the
    rests, one call each, full length each). Counters
    are kept so a job can state the shape it actually
    ran under: ``rests`` and ``rested_s``.
    """

    def __init__(
        self,
        *,
        assess_fn: Callable[[], BatteryAssessment] = assess_system,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._assess_fn = assess_fn
        self._sleep = sleep
        self._batches_since_rest = 0
        self.rests = 0
        self.rested_s = 0.0
        self.last_assessment: BatteryAssessment | None = None

    def between_batches(self) -> DutyRest:
        """One consultation: count a batch, rest if the burst is spent."""
        assessment = self._assess_fn()
        self.last_assessment = assessment
        plan = assessment.plan
        self._batches_since_rest += 1
        if plan.burst_batches is None or self._batches_since_rest < plan.burst_batches:
            return DutyRest(
                assessment=assessment,
                rested_s=0.0,
                batches_since_rest=self._batches_since_rest,
            )
        # The burst is spent: one blocking rest of the
        # plan's full length — never a polling loop.
        self._sleep(plan.rest_s)
        self.rests += 1
        self.rested_s += plan.rest_s
        self._batches_since_rest = 0
        return DutyRest(
            assessment=assessment,
            rested_s=plan.rest_s,
            batches_since_rest=0,
        )


__all__ = [
    "CONSERVE_BELOW_PCT",
    "CONSERVE_BURST_BATCHES",
    "CONSERVE_REST_S",
    "CRITICAL_BELOW_PCT",
    "CRITICAL_BURST_BATCHES",
    "CRITICAL_REST_S",
    "LOW_BELOW_PCT",
    "LOW_BURST_BATCHES",
    "LOW_REST_S",
    "POWER_SUPPLY_ROOT",
    "BatteryAssessment",
    "BatteryReading",
    "DutyCycler",
    "DutyMode",
    "DutyPlan",
    "DutyRest",
    "assess",
    "assess_system",
    "plan_for",
    "read_battery",
]

"""Thermal & patience etiquette — the companion yields (E-051).

Part III, slice E-051. Roadmap line: "on shared/small machines
the companion yields (load-aware throttling, the Aesir lesson)."

The Aesir lesson, in the words the campaign carries it by:
use every core the machine has, but never choke off other
running work, watch temperatures, and throttle back *before*
the danger zone. Until this slice Ember had no such manners
in code at all — a tree-wide search for load, thermal, or
throttling found nothing outside the generation
``temperature`` setting, which is a model knob, not a
machine one. Bulk work (an ingest embedding hundreds of
chunks) would happily pile onto a machine that was already
busy or running hot, on exactly the small shared machines
this project is named for.

This module is the manners, in three parts:

* **Reading the room (stdlib only).** The 1-minute load
  average per CPU (``os.getloadavg`` / ``os.cpu_count``) and
  the hottest thermal zone under ``/sys/class/thermal``
  (millidegree files, the shape a Pi exposes). A signal that
  cannot be read is *unknown* (``None``), never a guessed
  number — the campaign VM, for instance, exposes no
  thermal zones at all, and etiquette there judges load
  alone rather than inventing a temperature.
* **Judging the room (pure).** :func:`assess` folds the two
  signals into one of three levels, worst signal wins:
  ``PROCEED`` (the machine has room), ``EASE`` (busy or
  warm — pause briefly between units of background work),
  ``YIELD`` (saturated or at the thermal danger line —
  pause properly and look again). The load lines are
  per-CPU, so they mean the same thing on a 4-core Pi and
  a many-core laptop: 1.0 is "every core already has a
  job". The thermal lines sit below the point where small
  boards throttle themselves (a Pi 5 begins throttling
  around 80 °C): ease at 70 °C, yield at 80 °C — throttle
  back before the danger zone, not inside it.
* **Waiting, bounded.** :func:`wait_for_room` is for
  *background* work only. It sleeps the level's delay and
  re-assesses, but never past ``MAX_WAIT_S`` in total:
  patience is etiquette, not a deadlock — after the bound
  the work proceeds and the returned outcome says plainly
  that it waited the full bound. A person's live turn is
  never put through this gate: the one wiring in this
  slice is Smiðja's bulk embedding during ingest, where
  the gate is consulted *between batches*, so a single
  foreground embed (one batch) never waits at all.

Policy constants, not measurements: the delays and lines
below are stated manners, pinned by the E-051 tests so
they can only change deliberately. What the VM's room
actually read on measurement day lives in
``docs/architecture/E-051_THERMAL_PATIENCE_ETIQUETTE.md``.
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# --------------------------------------------------------------------- #
# Policy — the stated manners (E-051)                                   #
# --------------------------------------------------------------------- #

#: Per-CPU 1-minute load at or above which the machine is
#: busy: every core already has, on average, a job queued
#: or running. Background work eases off.
LOAD_EASE_PER_CPU = 1.0

#: Per-CPU load at or above which the machine is saturated
#: (two jobs per core). Background work yields properly.
LOAD_YIELD_PER_CPU = 2.0

#: Hottest-sensor temperature (°C) at or above which the
#: machine is warm. Background work eases off.
THERMAL_EASE_C = 70.0

#: Temperature (°C) at or above which the machine is at
#: the danger line — the point where small boards begin
#: throttling themselves. Background work yields.
THERMAL_YIELD_C = 80.0

#: The pause after an EASE judgement, and after a YIELD
#: judgement, before the room is read again.
EASE_DELAY_S = 1.0
YIELD_DELAY_S = 5.0

#: The most patience one gate call may spend in total.
#: Past this bound the work proceeds anyway and the
#: outcome records that the bound was reached — the
#: companion never starves its own background work
#: forever because a neighbour will not quieten down.
MAX_WAIT_S = 30.0

#: Where Linux exposes thermal sensors (the Pi shape).
THERMAL_ROOT = Path("/sys/class/thermal")


class PatienceLevel(Enum):
    """How much room the machine has for background work."""

    PROCEED = "proceed"
    EASE = "ease"
    YIELD = "yield"


@dataclass(frozen=True, slots=True)
class PatienceAssessment:
    """One reading of the room, with its reasons stated."""

    level: PatienceLevel
    #: 1-minute load average divided by the CPU count, or
    #: ``None`` when the platform cannot report load.
    load_per_cpu: float | None
    #: Hottest thermal sensor in °C, or ``None`` when the
    #: machine exposes no readable sensor (the VM shape).
    thermal_c: float | None
    #: One plain sentence naming the signal that decided
    #: the level (or that the room is clear).
    reason: str

    @property
    def delay_s(self) -> float:
        """The pause this judgement asks of background work."""
        if self.level is PatienceLevel.EASE:
            return EASE_DELAY_S
        if self.level is PatienceLevel.YIELD:
            return YIELD_DELAY_S
        return 0.0


@dataclass(frozen=True, slots=True)
class PatienceOutcome:
    """What one bounded wait did."""

    assessment: PatienceAssessment
    #: Total seconds actually slept.
    waited_s: float
    #: How many times the room was read.
    checks: int
    #: True when the wait gave up at ``MAX_WAIT_S`` with
    #: the room still busy/warm and the work proceeded
    #: anyway — patience bounded, stated, not hidden.
    bound_reached: bool


# --------------------------------------------------------------------- #
# Reading the room                                                      #
# --------------------------------------------------------------------- #


def system_load_per_cpu(
    loadavg: Callable[[], tuple[float, float, float]] | None = None,
    cpu_count: Callable[[], int | None] | None = None,
) -> float | None:
    """The 1-minute load average per CPU, or ``None``.

    ``None`` when the platform cannot report load or the
    CPU count is unusable — unknown, never guessed.
    """
    loadavg = loadavg or os.getloadavg
    cpu_count = cpu_count or os.cpu_count
    try:
        load_1m = loadavg()[0]
        cpus = cpu_count()
    except (OSError, IndexError):
        return None
    if not cpus or cpus < 1:
        return None
    return load_1m / cpus


def parse_thermal_celsius(root: Path = THERMAL_ROOT) -> float | None:
    """The hottest readable thermal zone in °C, or ``None``.

    Zones are ``thermal_zone*/temp`` files holding
    millidegrees. Unreadable or malformed zones are
    skipped; a machine with no zones (the campaign VM)
    reads ``None`` — no sensor, no invented temperature.
    """
    try:
        zones = sorted(root.glob("thermal_zone*/temp"))
    except OSError:
        return None
    hottest: float | None = None
    for zone in zones:
        try:
            millidegrees = int(zone.read_text(encoding="ascii").strip())
        except (OSError, ValueError):
            continue
        celsius = millidegrees / 1000.0
        if hottest is None or celsius > hottest:
            hottest = celsius
    return hottest


# --------------------------------------------------------------------- #
# Judging the room (pure)                                               #
# --------------------------------------------------------------------- #


def assess(
    *,
    load_per_cpu: float | None,
    thermal_c: float | None,
) -> PatienceAssessment:
    """Judge the room from its two signals — worst wins.

    An unknown signal never raises the level and never
    lowers it: it simply does not vote.
    """
    level = PatienceLevel.PROCEED
    reason = "the machine has room"

    if thermal_c is not None:
        if thermal_c >= THERMAL_YIELD_C:
            level = PatienceLevel.YIELD
            reason = (
                f"the machine is at {thermal_c:.0f} °C, the thermal "
                "danger line — background work yields"
            )
        elif thermal_c >= THERMAL_EASE_C:
            level = PatienceLevel.EASE
            reason = (
                f"the machine is warm at {thermal_c:.0f} °C — "
                "background work eases off"
            )

    if load_per_cpu is not None:
        if load_per_cpu >= LOAD_YIELD_PER_CPU and level is not PatienceLevel.YIELD:
            level = PatienceLevel.YIELD
            reason = (
                f"the machine is saturated at {load_per_cpu:.2f} load "
                "per CPU — background work yields"
            )
        elif load_per_cpu >= LOAD_EASE_PER_CPU and level is PatienceLevel.PROCEED:
            level = PatienceLevel.EASE
            reason = (
                f"the machine is busy at {load_per_cpu:.2f} load "
                "per CPU — background work eases off"
            )

    return PatienceAssessment(
        level=level,
        load_per_cpu=load_per_cpu,
        thermal_c=thermal_c,
        reason=reason,
    )


def assess_system(
    *,
    thermal_root: Path = THERMAL_ROOT,
) -> PatienceAssessment:
    """Read this machine's room right now and judge it."""
    return assess(
        load_per_cpu=system_load_per_cpu(),
        thermal_c=parse_thermal_celsius(thermal_root),
    )


# --------------------------------------------------------------------- #
# Waiting, bounded                                                      #
# --------------------------------------------------------------------- #


def wait_for_room(
    *,
    assess_fn: Callable[[], PatienceAssessment] = assess_system,
    sleep: Callable[[float], None] = time.sleep,
    max_wait_s: float = MAX_WAIT_S,
) -> PatienceOutcome:
    """Wait for room, for background work — never forever.

    Reads the room; while the judgement is EASE or YIELD,
    sleeps that level's delay and reads again, until the
    room clears or ``max_wait_s`` of total sleep is spent.
    Either way the caller's work then proceeds: the
    outcome states how long was waited, how often the
    room was read, and whether the bound was reached.
    """
    waited = 0.0
    checks = 0
    while True:
        assessment = assess_fn()
        checks += 1
        if assessment.level is PatienceLevel.PROCEED:
            return PatienceOutcome(
                assessment=assessment,
                waited_s=waited,
                checks=checks,
                bound_reached=False,
            )
        remaining = max_wait_s - waited
        if remaining <= 0:
            return PatienceOutcome(
                assessment=assessment,
                waited_s=waited,
                checks=checks,
                bound_reached=True,
            )
        delay = min(assessment.delay_s, remaining)
        sleep(delay)
        waited += delay


__all__ = [
    "EASE_DELAY_S",
    "LOAD_EASE_PER_CPU",
    "LOAD_YIELD_PER_CPU",
    "MAX_WAIT_S",
    "THERMAL_EASE_C",
    "THERMAL_ROOT",
    "THERMAL_YIELD_C",
    "YIELD_DELAY_S",
    "PatienceAssessment",
    "PatienceLevel",
    "PatienceOutcome",
    "assess",
    "assess_system",
    "parse_thermal_celsius",
    "system_load_per_cpu",
    "wait_for_room",
]

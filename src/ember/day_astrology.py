"""Ritual-shaped time: the day's astrology as a stimulus (E-111).

Roadmap line: "Ritual-shaped time: the companion can know
the day's astrology (the dawn-ritual pattern) as a Verdandi
stimulus (E-064) — computed, not fetched."

Until this slice the companion had no way to *know the day*
in its own terms. The astrology engine could cast a chart
(E-108), E-109 proved its maths, and E-110 made it a typed
service the core can call — but nothing turned that service
into the one thing a companion living by ritual time needs
first: a fact about *today*, arriving on the nerves the way
every other touch of the world arrives, as a typed stimulus
with provenance (E-064), where the reflex layer, the context
injector, and any future dawn rite can meet it.

This module is that turning:

- **Computed, not fetched.** The day's chart is cast locally
  through the E-110 chart service from the member engine in
  this tree. No reading is downloaded, no almanac is
  consulted, no network answer is dressed as the day's sky.
  (The place road is the service's own: explicit coordinates
  or a city the engine's built-in table carries resolve
  wholly offline; a city outside the table may fall to the
  engine's network geocoding tiers — that is the member's
  cascade, named in E-110 §4, and the offline ruling on it
  is E-113's. This module adds no fetch of its own.)
- **One stated moment.** A day has no single sky, so the
  contract states its moment: the chart is cast for
  **12:00 local time** at the place — the member's own
  day convention (its unknown-time default is noon) — and
  the payload carries that moment in words. The engine
  computes no sunrise, so no dawn instant is fabricated;
  the dawn-ritual pattern this serves is the companion
  *knowing the day* when it wakes, not a sunrise claim.
- **A registered stimulus.** The day enters as
  ``time.astrology`` — kind ``time``, channel ``cron``
  (the day's schedule is its entrance, as a scheduled
  rite's would be) — registered in ``Verdandi/stimuli.py``
  and in the hub's literal registry in this slice, with
  provenance origin :data:`STIMULUS_ORIGIN`. The literals
  below are carried inline under the core's
  no-member-imports discipline (the E-067 nerve bridge's
  pattern) and pinned equal to the Verdandi registry by
  this slice's conformance battery. The payload carries no
  persona, so under E-071's classification the stimulus is
  a system event: the day belongs to the house, not to one
  persona's private nerves.
- **A refusal publishes nothing.** When the chart service
  refuses — above all when the ephemeris is absent
  (docket 148's shape, refused before computing at E-110)
  — this module builds no stimulus and publishes nothing:
  the result carries the service's reason verbatim. A day
  the companion cannot compute is a day it says it cannot
  compute; there is no fallback sky.
- **The chart's own honesty travels with it.** The payload
  carries the service response's ``tz_label`` (how the
  input time was read, stated by the engine), its
  ``ephemeris_model`` (E-109 §3's answer), and its
  ``frame`` (tropical, docket 154) — a consumer of the
  stimulus never has to guess which sky, which clock, or
  which frame the day was cast in.
- **Publishing follows the nerve bridge's discipline**
  (E-067): :func:`publish_day_stimulus` goes through
  ``ember.nerve.publish_event``, which returns the hub's
  ack, or writes the feed file stamped as a fallback when
  no hub is reachable, or reports an error — and never
  raises. This module adds no transport of its own.

The payload is data, not interpretation: positions, angles,
and the chart's sect, exactly as the service served them.
What the day *means* is the companion's voice (E-112's
ground), never this module's.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ember import engines, nerve

#: The registered stimulus this module produces (E-064's
#: registry, Verdandi/stimuli.py — literals pinned equal by
#: the E-111 battery, the E-067 inline-literals discipline).
STIMULUS_NAME: str = "time.astrology"
STIMULUS_KIND: str = "time"
STIMULUS_CHANNEL: str = "cron"
STIMULI_VERSION: int = 1

#: The provenance origin every day stimulus carries: the
#: companion's own day computation, named so any later
#: reader can answer "where did this come from?" (E-064).
STIMULUS_ORIGIN: str = "ember_day_astrology"

#: The one stated moment of the day's chart: 12:00 local
#: time at the place — the member engine's own day
#: convention (its unknown-time default is noon). The
#: engine computes no sunrise; no dawn instant is claimed.
DAY_MOMENT: str = "12:00"


@dataclass(frozen=True, slots=True)
class DayAstrologyResult:
    """Either a built day stimulus or a plain refusal.

    ``stimulus`` is the E-064 stimulus dict (not yet on the
    nerves); ``status`` is the nerve bridge's publish status
    when :func:`publish_day_stimulus` put it there (``None``
    for a build-only result); ``reason`` is the chart
    service's refusal, verbatim, when no stimulus was built
    — in which case nothing was published, ever.
    """

    stimulus: dict | None
    status: dict | None
    reason: str | None

    @classmethod
    def built(cls, stimulus: dict, status: dict | None = None) -> DayAstrologyResult:
        return cls(stimulus=stimulus, status=status, reason=None)

    @classmethod
    def refused(cls, reason: str) -> DayAstrologyResult:
        return cls(stimulus=None, status=None, reason=reason)


def day_payload(chart: engines.Chart, *, date: str, place: str) -> dict:
    """The stimulus payload for one served chart.

    Pure shaping of the E-110 response: every value below
    is the service's own output, carried — never recomputed
    here, never interpreted. JSON-shaped throughout, so the
    payload survives the feed file exactly as built.
    """
    return {
        "date": date,
        "moment": DAY_MOMENT,
        "place": place,
        "julian_day": chart.julian_day,
        "positions": [
            {
                "name": body.name,
                "longitude": body.longitude,
                "sign": body.sign,
                "retrograde": body.retrograde,
            }
            for body in chart.positions
        ],
        "ascendant": chart.ascendant,
        "mc": chart.mc,
        "day_chart": chart.day_chart,
        "tz_name": chart.tz_name,
        "tz_label": chart.tz_label,
        "ephemeris_model": chart.ephemeris_model,
        "frame": chart.frame,
    }


def build_day_stimulus(
    date: str,
    *,
    city: str = "",
    nation: str = "",
    lat: float | None = None,
    lon: float | None = None,
) -> DayAstrologyResult:
    """Compute one day's astrology and shape it as a stimulus.

    Casts the day's chart through the E-110 service at
    :data:`DAY_MOMENT` local time. A service refusal is
    returned verbatim and no stimulus is built.
    """
    result = engines.request_chart(
        engines.ChartRequest(
            date=date, time=DAY_MOMENT, city=city, nation=nation,
            lat=lat, lon=lon,
        )
    )
    if result.chart is None:
        return DayAstrologyResult.refused(result.reason or "astrology service refused")
    place = city.strip() or (f"{lat},{lon}" if lat is not None else "")
    stimulus = {
        "stimulus_version": STIMULI_VERSION,
        "kind": STIMULUS_KIND,
        "name": STIMULUS_NAME,
        "payload": day_payload(result.chart, date=date, place=place),
        "provenance": {"origin": STIMULUS_ORIGIN, "channel": STIMULUS_CHANNEL},
    }
    return DayAstrologyResult.built(stimulus)


def stimulus_event(stimulus: dict) -> dict:
    """The canonical E-061 nerve event a day stimulus travels as.

    The E-064 ``to_event`` rendering, carried inline under
    this module's no-member-imports discipline: type
    ``stimulus:time.astrology``, source = the provenance
    origin, provenance inside the data where no copy can
    lose it.
    """
    provenance = dict(stimulus["provenance"])
    return {
        "v": 1,
        "type": "stimulus:" + stimulus["name"],
        "data": {
            "kind": stimulus["kind"],
            "name": stimulus["name"],
            "payload": dict(stimulus["payload"]),
            "provenance": provenance,
        },
        "source": provenance["origin"],
    }


def publish_day_stimulus(
    date: str,
    *,
    city: str = "",
    nation: str = "",
    lat: float | None = None,
    lon: float | None = None,
    state_dir: Path | None = None,
) -> DayAstrologyResult:
    """Compute the day's astrology and publish it on the nerves.

    A refusal publishes nothing (the result carries the
    reason and no status). A built stimulus is published
    through the E-067 nerve bridge, whose status dict —
    hub ack, feed fallback, or error — is returned as
    measured, never dressed up.
    """
    built = build_day_stimulus(date, city=city, nation=nation, lat=lat, lon=lon)
    if built.stimulus is None:
        return built
    status = nerve.publish_event(stimulus_event(built.stimulus), state_dir=state_dir)
    return DayAstrologyResult.built(built.stimulus, status=status)


__all__ = [
    "DAY_MOMENT",
    "STIMULI_VERSION",
    "STIMULUS_CHANNEL",
    "STIMULUS_KIND",
    "STIMULUS_NAME",
    "STIMULUS_ORIGIN",
    "DayAstrologyResult",
    "build_day_stimulus",
    "day_payload",
    "publish_day_stimulus",
    "stimulus_event",
]

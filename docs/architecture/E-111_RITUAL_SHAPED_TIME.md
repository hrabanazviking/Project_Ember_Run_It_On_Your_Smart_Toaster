# E-111 — Ritual-Shaped Time: the Day's Astrology as a Stimulus

*Project Ember campaign, Part VII (The Inner Life:
Seiðr Engine & Astrology Engine) — fifth slice. Filed
2026-11-02 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), on
top of E-110 banked (740a22d) + its push record
(7078dca) + this slice's IN PROGRESS marker (b65ef7b).
Every count below was measured this slice at this tree
(probes in `~/workspace/.verify-tmp/ember-e111/`); the
live chart figures were measured with the ephemeris
supplied from the isolated install E-108's correction
recorded (pyswisseph 2.10.3.2 at
`~/workspace/.verify-tmp/ember-e108/deps`), never added
to the repo. No README was touched.*

## The verdict, in plain words — read this first

**The companion can now know the day's astrology the
way it knows everything else about the world: as a
stimulus on its nerves.** A new registered stimulus,
`time.astrology`, carries the day's chart — computed,
not fetched: cast locally, at the moment this slice
states, through the typed chart service E-110 built,
from the engine whose maths E-109 proved. The
computation lives in one new core module,
`src/ember/day_astrology.py`: hand it a date and a
place and it hands back either the stimulus — ready to
publish, and publishable through the E-067 nerve
bridge — or the chart service's own refusal, verbatim.

**A refusal publishes nothing.** Where the sky cannot
be computed — above all where the ephemeris is absent,
this machine's default environment included — no
stimulus is built, no event is written, no fallback sky
is served. The day the companion cannot compute is a
day it says it cannot compute. Where the ephemeris is
present, the stimulus reproduces the proven sky
through the whole road: the London day at J2000
arrives on the nerves with the Sun at 280.3689 degrees
and the Ascendant at 24.0146 — E-109's and E-110's
pinned fixtures, now carried as a stimulus payload.

**This slice also discharges the clean Run D owed
from E-110** — see §6: the owed run, on the E-110 tree
before any E-111 file landed, stands **1757 passed, 0 failed, 12 skipped**, exit 0 — exactly
the shape E-110 §10 predicted by arithmetic from its
completed run (1769 accounted tests).

## 1. The stimulus

`time.astrology` is registered in this slice in both
places E-064's discipline keeps: `Verdandi/stimuli.py`'s
registry (producer, payload fields, channel, notes) and
the hub's literal registry in
`Verdandi/nervous_system.py`, pinned equal by the
E-064 conformance battery as extended implicitly by
its registry walk, and by this slice's battery
directly.

- **Kind `time`** — it is the clock's family: the day
  itself touching the nerves, kin to `time.tick` and
  `time.schedule`.
- **Channel `cron`** — its entrance is the day's
  schedule, as a scheduled rite's would be: the
  stimulus exists so a dawn-shaped schedule (or any
  caller standing in for one) can put the day on the
  nerves at the day's turning.
- **Provenance origin `ember_day_astrology`** — the
  companion's own day computation, named so any later
  reader can answer E-064's question — where did this
  come from? — from the event itself.
- **No persona in the payload** — under E-071's
  classification the stimulus is a system event: the
  day belongs to the house, not to one persona's
  private nerves, and its provenance carries nothing
  persona-shaped to leak.

An addendum appended to the E-064 record in this slice
names the new entrance in that record's own register
(the E-064 battery pins every registered name against
that document); the E-064 body itself is untouched.

## 2. The one stated moment

A day has no single sky, so the contract states its
moment rather than implying one: the day's chart is
cast for **12:00 local time** at the place — the
member engine's own day convention, whose unknown-time
default is noon (E-108). The payload carries the
moment in its `moment` field, and the place's own
timezone handling travels with it: the payload's
`tz_label` is the chart service response's label
verbatim, stating how the input time was read —
including, where no timezone could be resolved, that
the time was treated as UTC.

The engine computes no sunrise, and this slice claims
none: the dawn-ritual pattern the roadmap names is the
companion *knowing the day* when it wakes — the day's
sky prepared as a fact on its nerves — not a sunrise
instant fabricated from maths the member does not have.

## 3. Computed, not fetched

The day's chart is cast by the E-110 chart service
from the in-tree member engine. This module adds no
fetch of its own — no almanac, no download, no network
reading dressed as the day's sky. The place road is
the service's own, stated as E-110 §4 states it:
explicit coordinates resolve with no lookup at all,
and a city the engine's built-in table carries
resolves through that table; a city outside the table
may fall to the engine's network geocoding tiers,
which is the member's cascade — the offline ruling on
those tiers is E-113's, and this slice neither widens
nor narrows it.

Determinism follows the service's: the same date,
place, and moment build the identical stimulus,
byte for byte in the payload (pinned in the battery) —
a day, once computed, does not drift between readings.

## 4. The payload

The payload is the served chart, shaped — every value
the E-110 response's own output, carried, never
recomputed here and never interpreted:

- `date` and `moment` (the stated day and its stated
  hour), `place` (the city as given, or the explicit
  coordinates as given);
- `julian_day`, the engine's own day count;
- `positions` — every body's name, longitude, sign,
  and retrograde flag, as data;
- `ascendant` and `mc`;
- `day_chart`, the chart's sect as the engine rules it
  after E-109's fix;
- `tz_name` and `tz_label` (§2);
- `ephemeris_model` — E-109 §3's answer travelling
  with the day exactly as it travels with the chart:
  the pyswisseph built-in analytical model, the
  one-arcminute standard E-109 proved, never an
  arcsecond claim;
- `frame` — `tropical`, docket 154's ruling, stated on
  the day as on the chart.

The payload is JSON-shaped throughout, so it survives
the feed file, the ring buffer, and every reader
exactly as built (pinned). What the day *means* is
not in it: interpretation is the companion's voice —
E-112's ground — never this module's.

## 5. Publishing, and the refusal shape

`build_day_stimulus` computes and shapes only.
`publish_day_stimulus` additionally puts the stimulus
on the nerves through the E-067 core bridge
(`ember.nerve.publish_event`) as the canonical E-061
event `stimulus:time.astrology` — the E-064 `to_event`
rendering, carried inline in this module under the
core's no-member-imports discipline, its literals
pinned equal to the Verdandi registry by the battery.
The bridge's own discipline governs delivery: a hub
ack when the hub answers, the feed file stamped as a
fallback when no hub is reachable (proven in the
battery against a hub-less state dir: one feed line,
readable back through `stimuli.from_event` as the
same stimulus), an error reported as an error, and
never a raise.

On a refusal the result carries the service's reason
verbatim, `status` is `None`, and nothing is published
— no hub write, no feed fallback line. The battery
proves the negative in the default environment: a
publish attempt against a fresh state dir leaves no
feed file at all.

## 6. The owed Run D, discharged

E-110 §10 left a single clean Run D owed, its tick
directed to discharge it first. At this tick's open,
before any E-111 file landed (the IN PROGRESS marker
aside — a state file no test reads for content), the
full suite ran in the established Run D shape (the
ember-extras path of E-110's gate scripts) on the
banked E-110 tree: **1757 passed, 0 failed, 12 skipped**, exit 0 — exactly
the shape E-110 §10 predicted by arithmetic from its
completed run (1769 accounted tests). The discharge took three attempts, recorded plainly:
the first died at ~44% when the recurring home-quota
EDQUOT flap truncated its log mid-write (an
environment casualty on an unchanged tree, the
mechanism E-101/E-103/E-105 recorded), the second
met the same flap at startup, and the third — scratch
and logs on `/dev/shm`, the campaign's standing flap
pattern — completed clean in 304.00s. This slice's
own gate (§8) ran under the same flap pattern.

## 7. What this slice did not build

- **No scheduler was wired.** Nothing in the tree
  fires this stimulus at dawn — or at any hour — on
  its own. The stimulus, its registry entry, and its
  publisher are the slice; a living dawn rite that
  calls the publisher on a schedule is a consumer no
  Part VII slice has commissioned, and none is claimed
  here.
- **No consumer reacts to the stimulus yet** — the
  reflex layer and the context injector read it as an
  ordinary canonical event today, exactly as E-064 §7
  left typed reaction to later work. E-112 (seiðr in
  conversation) is the first commissioned consumer of
  Part VII's services; the day stimulus is its kin,
  not its input.
- **The member's other analyses stay unserved**
  (E-110 §9 stands): no lunation, no planetary hours,
  no transit overlay is in the payload — the day is
  the natal-shaped chart core at the stated moment,
  nothing dressed beyond it.
- NOT PROVEN at this slice: any live-hub delivery
  (the battery proves the feed-fallback shape; a
  running hub's ack path is the bridge's standing
  E-067 proof, not re-run here), any real-hardware
  figure (Part VII's budget rows are E-114), and any
  scheduled firing (§7's first bullet).

## 8. Gate re-measurement (E-017 method)

Measured this slice, VM profile (Python 3.12.3,
pytest 9.1.1); raw logs in
`~/workspace/.verify-tmp/ember-e111/`.

- **Pre-doc standing batteries** (E-057's table,
  E-043's install weight, E-089's canon guard): the
  first 20 of the focal set below.
- **Focal battery** (this slice's own, 10 tests):
  **5 passed, 5 skipped in the default shape** (the
  five live fixtures skip without the ephemeris; the
  no-ephemeris refusal and the nothing-published
  proof execute), and **9 passed, 1 skipped in the
  live shape** (the isolated ephemeris dir on the
  path; the London day reproduces E-109/E-110's
  pinned Sun and Ascendant through the stimulus,
  round-trips through `stimuli.from_event`, and
  lands in a hub-less feed file readable back as the
  same stimulus).
- **Focal set** (the standing 20 + E-107's 11 +
  E-108's 11 + E-109's 19 + E-110's 18 + E-064's 16
  + this slice's 10 = 105): **95 passed, 10
  skipped** in the default shape — the ten skips
  exactly the two Part VII batteries' live fixtures.
  Two pins were re-pinned consciously with
  attribution inside it: the E-109 battery's
  book-total pin (§8's last bullet) and the E-108
  battery's no-consumer pin, which now guards that
  exactly two core files name the astrology member —
  the service, and this slice's module as the
  service's first consumer.
- **Member suite** (seiðr, its own shape): **38
  passed, 0 failed** — unchanged. The astrology
  member has no suite (a standing fact of its map).
- **E-057 re-pinned consciously with attribution:**
  src 134 files / 972,966 B (the new day-astrology
  module), Verdandi 193 / 17,034,160 B (the stimuli
  registry entry and the hub literal), total
  131,657,131 B, Verdandi's miss of the laptop
  ceiling now 256,944 B — both published copies.
- **Run A:** **1 error, 20 skipped**, exit 2
  (docket 1, identical).
- **Run B:** **1554 passed, 6 failed, 44 skipped** —
  the 6 proven environment failures ONLY,
  name-for-name the standing set (Batch CDE \u00d73,
  G \u00d72, J \u00d71 — the sqlite_vec-missing family;
  = E-110's 1549 + 5 new in the default shape,
  skips 39 + 5, exact).
- **Run D:** attempt 1 stood at **1759 passed, 3
  failed, 17 skipped** — the 3 failures all
  integration acceptance tests killed by the
  recurring EDQUOT flap (`OSError: [Errno 122]` on
  writes under `~/.ember/state`, direct write probe
  failing the same way in the same window; both
  files then passed whole in isolation, 5 passed,
  once the flap cleared). Attempt 2, on the
  identical tree, ran **CLEAN in one run: 1762
  passed, 0 failed, 17 skipped** (= the discharged
  owed shape 1757/12 + this slice's 5 new default-
  shape passes and 5 live-fixture skips, exact).
- The gate ran through the recurring home-quota
  EDQUOT flap and one VM reboot: scratch and logs
  on `/dev/shm` (the campaign's standing flap
  pattern), the logs copied to
  `~/workspace/.verify-tmp/ember-e111/` at the close;
  nothing was deleted by this campaign.

## Carried forward

- Part VII continues. Next: E-112 (seiðr in
  conversation: what the engine offers a chat, with
  the honesty rule — the engine computes, meaning is
  the companion's voice, labelled; carrying docket
  144's member-side fate for `include_old_norse` and
  `topic`).
- Dockets 143 and 148 stand with E-120 (their
  contract notes executed at E-110; the day stimulus
  inherits the service's refusal, §5). Docket 153's
  offline ruling stands with E-113 — this slice's
  §3 states the place road exactly so that ruling
  has a fixed shape to judge.
- NOT PROVEN at this slice: a live dawn firing, a
  reacting consumer, any served lunation or transit,
  any real-hardware figure beyond E-057's rows.

*Filed by the E-111 slice, 2026-11-02. Next:
E-112 — seiðr in conversation.*

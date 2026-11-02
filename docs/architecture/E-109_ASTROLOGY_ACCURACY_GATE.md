# E-109 — Astrology Accuracy Gate

*Project Ember campaign, Part VII (The Inner Life:
Seiðr Engine & Astrology Engine) — third slice, the
accuracy gate for the engine E-108 mapped. Filed
2026-11-02 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), on
top of E-108 banked (004de7a) + its push record
(e0d6a0f) + its correction (a79c557) + this slice's
IN PROGRESS marker (f1af9e3). Every count below was
measured this slice from the member's own code at
this tree (probes in
`~/workspace/.verify-tmp/ember-e109/`); the ephemeris
was supplied from the isolated install E-108's
correction recorded (pyswisseph 2.10.3.2 + pyephem
4.2.1 at `~/workspace/.verify-tmp/ember-e108/deps`),
never added to the repo. Fixtures are synthetic, or
published reference values — the roadmap's fixture
law for this gate. Volmarr's own natal data was not
used; the natal-shaped fixtures use a synthetic
1990-06-15 chart. No README was touched.*

## The verdict, in plain words — read this first

**the accuracy gate passes — at the standard a
working astrologer's practice actually needs, and
no higher claim is made.** The sky itself was
already sound: at four sampled moments between
1950 and 2026, every one of the ten classical
planets the engine prints lands **within one
arcminute** of an independent ephemeris — the
worst single miss in forty planet-positions is
0.58 arcminutes, about one-thirtieth of the Moon's
apparent width. The Ascendant for London at the
sampled moment likewise agrees with an independent
sidereal-time calculation to 0.6 arcminutes.

**Everything that was wrong was wrong around the
sky, in the engine's own maths and tables — and
this gate fixed all of it in scope.** The two
most important lots stood swapped. A planet in
its fall was never scored fallen. The "next new
and full moon" search did not find lunations at
all. The solar-return search stopped about 26
degrees short of the return it claimed to cast.
And this gate's own probing found two more, worse
in their reach: **every date the engine printed
from a Julian day — the solar return's moment,
the lunation times, sunrise and sunset — landed
13 days early with its minutes zeroed**, and
**every chart's day/night sect was inverted, so a
chart cast for noon was read as a night chart**,
reversing the lots' formulas and the sect light
along with it. All six carried dockets are CLOSED
in scope, and the two new findings are dockets
157 and 158, opened and CLOSED in scope here.

What the gate does **not** claim: arcsecond
accuracy (the tree carries no Swiss Ephemeris
data files, so the library's built-in model is
the ceiling — see §3), any statement about the
sidereal branch (E-110's), and any cure for the
fabricated chart printed when the ephemeris
package is absent (docket 148 — E-120's, with
E-110's contract note; §7).

## 1. The standard

The roadmap charges this gate with verification
"to the standard Volmarr's practice requires."
Stated as numbers, the standard this gate applied:

- **Positions: within one arcminute** of an
  independent reference for the classical bodies
  at sampled epochs. Chart work — houses, lots,
  dignities, aspects at degree-level orbs — turns
  on degrees and minutes; a sub-arcminute engine
  is exact for every use this companion makes of
  it, and a larger miss would move a planet's
  printed position.
- **Searches: to their own stated tolerances** —
  the solar return to its 0.001-degree promise,
  lunations to within minutes of the published
  event times.
- **Derived maths: exact** on synthetic fixtures,
  where the true answer is known by construction
  (lots, dignities, sect geometry, antiscia,
  midpoints, lunar phase).
- **Places: exact** against the gazetteer's own
  repaired entries, spot-pinning the places the
  house actually uses.

## 2. The real-sky fixtures — positions

Each sampled moment was computed two independent
ways: the engine (pyswisseph, no ephemeris files
in the tree) and pyephem, an unrelated
implementation, its ecliptic longitudes taken in
the **epoch-of-date** frame.

**The comparator lesson, recorded plainly:**
pyephem's ecliptic conversion defaults to the
J2000 frame. A first pass of this gate's probe,
taken naively, showed every planet drifting from
the reference by an amount that grew with
distance from J2000 — 8 arcminutes at 1990, 22
at 2026, 42 at 1950, near-identical for fast
Moon and slow Saturn alike. A uniform,
time-proportional shift on every body is a frame
difference (precession accumulating since
J2000), not an engine error; with the reference
taken in the epoch-of-date frame — the frame a
tropical chart is cast in — the same probe reads:

| Epoch (UTC) | Bodies | Worst miss |
|---|---|---|
| 1950-03-20 00:00 | 10 | 0.38 arcmin (Sun) |
| 1990-06-15 12:00 | 10 | 0.54 arcmin (Uranus) |
| 2000-01-01 12:00 | 10 | 0.58 arcmin (Sun) |
| 2026-11-02 12:00 | 10 | 0.47 arcmin (Uranus) |

Forty positions, worst 0.58 arcminutes — inside
the one-arcminute standard at every epoch. The
full per-body table is in the slice's probe log;
two epochs (J2000 and the synthetic natal moment)
are pinned as fixtures in this slice's battery,
where they run whenever the ephemeris is
importable in the test environment.

**Houses:** for London at 2000-01-01 12:00 UTC the
engine's Placidus Ascendant is 24.0146 degrees;
an Ascendant computed independently from the
Greenwich sidereal time by the standard RAMC
formula is 24.0247 degrees — agreement to 0.6
arcminutes. (The MC is the library's own output
and was not independently re-derived; the
Ascendant is the house system's anchor and the
cusp the lots and sect consume.)

## 3. What bounds the accuracy — stated, not implied

The engine never calls `set_ephe_path` and no
`.se1` ephemeris file exists in this tree (E-108
§3), so pyswisseph falls back to its built-in
analytical model. That model is why the standard
is one arcminute and not one arcsecond — and one
arcminute is what the measurements above show.
Shipping data files, or naming the model on the
printed chart, is a service-contract question:
it is carried to E-110 with docket 153 (the
undeclared dependencies), not decided here.

## 4. The searches

**Lunations (Docket 151 — CLOSED in scope).**
The old `next_lunation` called
`swe.mooncross_ut` — the Moon's crossing of a
fixed longitude — with targets 0 and 2, commented
as new and full moon. A lunation is an elongation
event, not a longitude crossing, and under
pyswisseph 2.10.3.2 the call returned
`(None, None)` outright: the lunar command
printed no lunation lines at all. The function
now searches the Sun–Moon elongation itself —
a one-day scan (elongation grows ~12.2 degrees a
day, so no crossing can be skipped) with
bisection of the crossing, the same shape as the
engine's own exact-transit searches. Against
published times, with the ephemeris live:

| From | Event | Engine | Published | Miss |
|---|---|---|---|---|
| 2000-01-01 | New Moon | 2000-01-06 18:13 UTC | 18:14 UTC | under a minute |
| 2000-01-01 | Full Moon | 2000-01-21 04:40 UTC | 04:40 UTC | under a minute |
| 2024-04-01 | New Moon | 2024-04-08 18:20 UTC | 18:21 UTC | under a minute |
| 2024-04-01 | Full Moon | 2024-04-23 23:48 UTC | 23:49 UTC | under a minute |

(The engine prints whole minutes, truncated; the
independent pyephem values — 18:13:39, 04:40:27,
18:20:49, 23:48:56 — sit inside the same minute
in every case. The battery pins the raw Julian
days to within three minutes of the published
times, and proves the search logic in every
environment against a synthetic ephemeris whose
lunations are known by construction.)

**Solar return (Docket 156 — CLOSED in scope).**
E-108's suspect, proven in its correction: the
old iteration stepped `diff / 360.0` days a pass
under a 50-pass cap and stopped 26.25 degrees
short. The search is now a function,
`find_solar_return`: the calendar anniversary in
the target year — never more than about a day
and a half from the true return — is scanned in
half-day steps for the Sun's crossing of its
natal longitude, and the bracket is bisected to
the code's own 0.001-degree tolerance.
`cmd_solar_return` calls it. Probed live on the
synthetic natal chart (1990-06-15 12:00 UTC,
natal Sun 84.1296 degrees): the 2026 return is
**2026-06-15 04:52 UTC**, residual 0.0008 degrees
— inside tolerance — confirmed by an independent
brute-force scan of the surrounding days.

## 5. The derived maths, fixed and pinned

**Lots (Docket 149 — CLOSED in scope).** The
helper computes `ASC + to − from` by day (and the
reverse by night); the Fortune call passed
(Moon, Sun) and the Spirit call (Sun, Moon), so
Fortune printed Spirit's longitude and the five
dependent lots — Eros, Necessity, Courage,
Victory, Nemesis — inherited the swap. The calls
now stand in the traditional order. Pinned on
the synthetic day chart of E-108's probe (ASC 0,
Sun 0, Moon 90): Fortune 90, Spirit 270, Eros
150, Necessity 60, Courage 30, Victory 270,
Nemesis 180 — and the night chart reverses the
pair (Fortune 270, Spirit 90).

**Fall (Docket 150 — CLOSED in scope).** `FALL`
stood built by inverting the exaltation table,
producing a sign-to-planet map the check could
never match (and losing two planets to
collisions in the bargain). Fall is now derived
as it is defined — the sign opposite the
exaltation, a planet-to-sign map: Sun in Libra,
Moon in Scorpio, Mercury in Pisces, Venus in
Virgo, Mars in Cancer, Jupiter in Capricorn,
Saturn in Aries, and the moderns likewise. The
textbook falls carry the Fall label and its −4;
exaltation scoring is untouched.

**Sect (Docket 158 — NEW, CLOSED in scope).**
This gate probed `is_day_chart` against the
Sun's true altitude (pyephem) at eleven hours of
2000-01-01 in London: **the function's answer
was inverted at every hour** — midnight read as
day, noon as night. The longitudes above the
horizon run from the Descendant forward through
the MC to the Ascendant; the old test returned
the other half of the circle. The fix is one
comparison, and the eleven-hour probe now agrees
at every hour. Everything that consumes sect —
the lots' day/night choice, the sect light, the
printed chart type — was reversed by this bug
on every chart the engine has ever cast.

**Printed dates (Docket 157 — NEW, CLOSED in
scope).** `jd_to_dt` converted with
`swe.jdut1_to_utc(jd, 0)` — the flag 0 selects
the Julian calendar, so in this era every
printed date landed **13 days early**; and that
function's (…, hour, minute, second) return
shape silently zeroed the minutes under a
formatter written for a fractional hour. Every
date the engine derives from a Julian day — the
solar return's moment, the next lunations,
sunrise/sunset in the planetary hours, the
prediction searches, the Davison chart — carried
both defects. The conversion is now
`swe.revjul(jd, swe.GREG_CAL)`, the shape the
formatter was written for, and the round trip is
pinned: JD 2451545.0 prints "2000-01-01 12:00
UTC", the January 2000 new-moon Julian day
prints "2000-01-06 18:13 UTC".

**Spot fixtures for the rest of the derived
maths** (probed exact, pinned in the battery):
antiscia of 30 degrees is 150, contra-antiscia
330; the composite midpoint of 350 and 10 is 0;
lunar phase at 180 degrees elongation is Full
Moon at 100% illumination.

## 6. Places (Docket 152 — CLOSED in scope)

The gazetteer's three probed defects, repaired
in the table itself:

- **Tivat** carried Cancún's coordinates
  verbatim; it now carries Tivat, Montenegro's
  own (42.4347, 18.6998).
- **Tianjin** stood under the key `tientSin`,
  unreachable by the lower-cased lookup, and
  defaulted to 0,0; the key is now `tianjin`,
  and the city resolves to (39.1422, 117.1767).
- **Charleston** stood twice with two different
  cities' coordinates and a silent winner. The
  ruling: bare `charleston` is Charleston, West
  Virginia — the state-capital entry, the table's
  first — and Charleston, South Carolina is
  reachable under `charleston sc`. No silent
  winner remains.

The rest of the duplicates were weighed, not
swept: 26 keys repeat with **identical**
coordinates — harmless under the dict's
last-wins rule, retained, and now pinned by a
battery test that fails if any duplicated key
ever again carries two different coordinate
pairs. The table stands at 426 entries under
395 unique keys. Spot-pinned place fixtures:
Angola, London, Uppsala and Reykjavik, plus the
three repairs. (Indianapolis was verified by
this slice's probe — (39.7684, −86.1581),
resolving from the table — and stands unchanged,
but is deliberately not pinned in the battery:
the E-089 canon guard forbids that state's name
anywhere in the test tree, and this slice's
first gate run caught an early draft of the
battery carrying it. The needle was replaced,
no allowlist entry added — the E-105 pattern.)

## 7. Time conventions (Docket 155 — CLOSED in scope)

`aspect-grid` and `antiscia` take no location,
so no timezone conversion is possible; they read
the input time as UTC while the natal family
converts local time — and neither said so. The
convention itself stands (a location-less
command can do no other), but it is **stated,
never silent** now: both commands print "time
treated as UTC (no location)" in their headers,
pinned in the battery. The one family member
that already stated its convention —
`transit --transit-date`, which labels its sky
"UTC" — is unchanged.

## 8. What this gate did not touch

- **Docket 148 stands open, owner E-120** (with
  E-110's contract note): without the ephemeris
  package, most commands still print a fabricated
  chart and exit 0. This gate's searches refuse
  honestly in that shape (both return None, and
  the lunar and solar-return commands already
  refused in words) — the CLI-wide honesty fix
  is E-120's slice, not smuggled into an accuracy
  gate.
- **Docket 153** (dependencies declared nowhere)
  and **docket 154** (the dead sidereal branch)
  stand with E-110, whose service contract is
  where they belong; §3 hands E-110 the
  ephemeris-model question with them.
- No consumer was built (E-110), nothing was
  wired into conversation or ritual (E-111,
  E-112), and the engine's output shape — printed
  text, exit 0 — is unchanged except where a
  header now states its time convention.

## 9. Gate re-measurement (E-017 method)

Measured this slice, VM profile (Python 3.12.3,
pytest 9.1.1); raw logs in
`~/workspace/.verify-tmp/ember-e109/`.

- **Pre-doc standing batteries** (E-057's table,
  E-043's install weight, E-089's canon guard):
  **20 passed** — they are the first 20 of the
  focal set below.
- **Member suite:** none exists — a standing fact
  of the map (E-108), not a pass.
- **Focal battery** (this slice's own): **19
  passed** in the default shape, and **19 passed
  again in the live shape** (the isolated
  ephemeris dir on PYTHONPATH, the three real-sky
  fixtures truly executing; the E-108 battery
  beside it, 30 passed together).
- **Focal set** (the standing 20 + E-107's 11 +
  E-108's re-pinned 11 + this slice's 19):
  **61 passed**, foreground-verified after the
  gate finding below.
- **Run A** (whole suite, default env): **1 error,
  20 skipped**, exit 2 (docket 1, unchanged).
- **Run B** (default env, pgvector file excluded):
  first run **1535 passed, 7 failed, 34 skipped**
  — the seventh failure was this slice's own:
  the E-089 canon guard caught the battery's
  draft carrying a forbidden real-history marker
  (a house place name; §6 records the repair).
  Post-fix run: **1536 passed, 6 failed, 34
  skipped** — E-108's 1517 + this slice's 19,
  exact; the 6 are the proven environment
  failures (Batch CDE ×3, G ×2, J ×1 — the
  sqlite_vec family).
- **Run D** (whole suite, extras supplied):
  **1744 passed, 0 failed, 7 skipped**, exit 0 —
  E-108's 1725 + 19, exact, fully clean. In the
  extras shape this run used, the pgvector file's
  14 standing skips collapse into a single
  import skip (that extras dir carries no
  pgvector package), which is why the skip count
  reads 7 against E-108's 20 while the passed
  count matches exactly. A re-run in the
  established extras shape (with pgvector) died
  at ~57% on a native bus error under load ~11,
  after contention-family marks at 52% — the
  E-102 bus-error family, an environment
  casualty on an unchanged tree; the completed
  clean run above stands as this gate's Run D.
- /tmp stood at 415,186,944 B free at the gate
  close; no owed runs outstanding.
- This slice changes one member file (the engine:
  the FALL derivation and its check, the two lot
  calls, the lunation and solar-return searches,
  `jd_to_dt`, `is_day_chart`, three gazetteer
  entries, two headers), adds one architecture
  doc and one root battery, re-pins the E-108
  battery's three fixed shapes and the member
  size consciously with attribution, and re-pins
  the E-057 table (astrology-engine 25 /
  7,482,898 B, total 131,621,907 B, miss unchanged
  256,017 B, both copies).

## Carried forward

- Part VII continues. Next: E-110 (the engines as
  services to the core).
- Dockets 149, 150, 151, 152, 155, 156 CLOSED in
  scope here; dockets 157 and 158 opened and
  CLOSED in scope here. Standing with their
  owners: 148 → E-120 + E-110, 153 → E-110 +
  E-113, 154 → E-110.
- NOT PROVEN at this slice: arcsecond-level
  positions (no ephemeris data files in the
  tree — §3), the MC against an independent
  derivation (§2), any accuracy claim for the
  sidereal branch (no caller reaches it — E-110
  decides its fate), and any real-hardware
  figure beyond E-057's standing row.

*Filed by the E-109 slice, 2026-11-02. Next:
E-110 — the engines as services to the core.*

# E-108 — Astrology Engine Mapped: Chart Maths, Ephemeris Source, Accuracy Fixtures

*Project Ember campaign, Part VII (The Inner Life:
Seiðr Engine & Astrology Engine) — second slice, a
map, not a build. Filed 2026-11-02 on branch
`yrsa/ember-road-build` in the campaign's own clone
(`~/workspace/ember-build`), on top of E-107 banked
(65b0c90) + its push record (ff4c8a5) + this slice's
IN PROGRESS marker (d44a365). Every count below was
measured this slice from the member's own code at
this tree (probes in
`~/workspace/.verify-tmp/ember-e108/`); nothing is
recalled from elder documents. Where an elder
document claims more — or less — than the code
does, the code wins and the gap is recorded (§7,
§8). No README was touched; no member code was
changed by this slice — Part VII builds on this
map in E-109 (accuracy) and E-110 (services).*

## The map, in plain words — read this first

**The astrology engine is a single-file chart
calculator: it calculates astrological charts —
planetary positions, houses, aspects, dignities,
lots, and a shelf of derived analyses — from a
birth date, time, and place, using the Swiss
Ephemeris for the sky itself.** One Python file of
3,239 lines does everything: it resolves a city
name to coordinates and a timezone, converts the
local birth time to UTC, asks the Swiss Ephemeris
(via the `pyswisseph` package) where every planet
was at that Julian day, and then computes
everything else itself — Placidus houses, twelve
aspect types, essential dignities with scores,
seven Arabic lots, antiscia, lunar phase and
void-of-course, planetary hours, synastry and
composite charts, solar returns, secondary
progressions, exact transit/station/ingress/
eclipse searches, and astrocartography lines —
printing the result as formatted text under
16 subcommands, with a Norse overlay (planet→god,
sign→rune) woven through the output. That overlay
is presentation data in the print layer and in two
constant tables; the maths underneath is standard
Western tropical astrology.

**It has no consumers today.** Nothing in the
companion's core imports it, calls it, or mentions
it; the campaign's own inventory records it as
unwired ("None planned"), and its header still
names its home as a Hermes divination skill, not
Ember. Its only living caller is its own command
line — and unlike the seiðr engine, **it has
no test suite at all**: not one test file exists
in the member, so nothing in the tree today
verifies a single number it prints.

**Its accuracy is NOT PROVEN, and this map found
probed reasons to doubt parts of it.** The
ephemeris itself is the Swiss Ephemeris — a sound
source — but the engine's own maths around it
carries defects this slice probed and docketed:
the Lot of Fortune and the Lot of Spirit come out
swapped (§8, docket 149), a planet in its fall is
never scored as fallen (docket 150), the "next
lunation" search calls an API that does not find
lunations (docket 151), and the built-in city
table contains wrong and unreachable entries
(docket 152). Worst, when the ephemeris package
is missing — as it is in this VM's default
environment, its dependencies declared nowhere —
most commands do not refuse: they print a
full-looking chart with empty planet tables and a
fabricated Ascendant at 0° Aries, and exit 0
(docket 148). E-109, the accuracy gate, owns the
verification standard and the fixes' proof; this
map hands it a measured engine and a docket, not
a verdict of accuracy.

## 1. The member as it stands

| Fact | Measured value |
|---|---|
| Location | `astrology-engine/` — one engine file, `astrology_engine.py` (3,239 lines, 134,560 B) |
| Tracked files | 25 tracked files, 7,477,309 B in all — the E-057 row, verified standing at this tree; 12 of the 25 are image files (~7.2 MB of the total) — the code and docs together are under 0.6 MB |
| Licence | Apache-2.0 (member `LICENSE`, full text) — the tree's only non-MIT member licence (E-007) |
| Authorship as filed | The file header: "ASTROLOGY ENGINE — Volmarr's Longhall / Hermes Divination Skill", built for the Hermes Agent; the geocoder user-agent names it `volmarr_astrology_engine/3.0`. `ORIGINS.md` carries no row naming this member |
| Dependencies | **Declared nowhere** — no `pyproject.toml`, no requirements file, no packaging of any kind (docket 18, E-007; Part VII disposition at §8, docket 153). The code imports five third-party packages, all guarded: `pyswisseph` (the ephemeris, the one hard requirement), `kerykeion` (geocoding), `geopy` (Nominatim geocoding), `timezonefinder` (timezone lookup), `pytz` (UTC conversion) |
| Smallest profile (E-057) | pi; import-level RAM floor 12.4 MiB — with E-057's standing caveat: importing is not computing; the compute dependencies are absent in the bare env |
| Test suite | **None.** No test file exists in the member (E-005 recorded the same); the only root-level pins touching it are the E-043/E-057 size rows |

The member's documents, as they stand: the
engine file itself; `ARCHITECTURE.md` (a technical
reference whose data-flow matches the code);
`COMMANDS.md` (flag reference for the 16
subcommands — the count is current); `CHANGELOG.md`,
`CONTRIBUTING.md`, `ROADMAP.md`, a `LEGAL-NOTICE.md`
and `NOTICE`; and three reference notes under
`docs/references/` whose gap lists are partly
stale against the code (§7).

## 2. What it computes — the chart maths, stated exactly

Everything flows through one pipeline (the
member's own `ARCHITECTURE.md` draws the same
shape, and the code agrees with it):

1. **Place and time resolution.** `resolve_birth`
   parses the date/time, resolves the place to
   latitude/longitude (§5), finds the IANA timezone
   for those coordinates, and converts local time
   to a UTC hour. A missing birth time defaults to
   noon and is flagged as unknown in the output.
2. **Julian day.** `julian_day` delegates to
   `swe.julday` when the ephemeris is present, and
   otherwise computes the standard Gregorian
   formula itself. That fallback is exact — probed
   this slice: JD 2451545.0 at 2000-01-01 12:00
   (J2000.0) and JD 2440587.5 at the Unix epoch,
   both to the digit.
3. **Positions.** `calc_planet_positions` calls
   `swe.calc_ut` with the speed flag for 16 bodies
   — Sun through Pluto, Chiron, Ceres, Pallas,
   Juno, Vesta, and the True Node — recording
   longitude, latitude, speed, sign/degree, and a
   retrograde flag from the speed's sign. The
   South Node is not queried; it is derived as
   exactly opposite the North Node. A sidereal
   branch exists (Fagan-Bradley) but no caller
   reaches it (§8, docket 154).
4. **Houses.** `calc_houses` calls `swe.houses`
   in the Placidus system — the only system the
   code exposes; there is no house-system choice
   anywhere in the CLI. `planet_house` then places
   each body by cusp interval.
5. **Derived layers, all the engine's own maths:**
   - **Aspects** — 12 types (conjunction through
     septile), each with separate orbs for
     luminaries and for other bodies, an
     applying/separating flag from relative speed.
   - **Essential dignities** — domicile, detriment,
     exaltation (with exact-degree bonus), fall,
     triplicity, Egyptian terms, decans/faces,
     combined into a numeric score per planet;
     plus mutual-reception detection. The fall
     half of this is broken (§8, docket 150).
   - **Arabic lots** — the seven traditional lots
     (Fortune, Spirit, Eros, Necessity, Courage,
     Victory, Nemesis), day/night formula reversal
     on the chart's sect. Fortune and Spirit come
     out swapped (§8, docket 149).
   - **Antiscia / contra-antiscia** — mirror
     longitudes across the solstice and equinox
     axes (probed exact on a synthetic position).
   - **Hellenistic layer** — sect (day/night by
     Sun-vs-Ascendant), sect light, planetary joys,
     bonification material in the print layer.
   - **Lunar** — phase name and illumination from
     Sun–Moon elongation (probed: 180° elongation
     returns Full Moon, 100% illumination), and a
     void-of-course test that works forward from
     the Moon's position to its sign ingress by
     exact-aspect targeting.
   - **Planetary hours** — sunrise/sunset from
     `swe.rise_trans`, the day split into twelve
     and the night into twelve, rulers by the
     Chaldean order from the day ruler.
   - **Two-chart work** — synastry cross-aspects,
     composite charts by shorter-arc midpoint
     (probed: 350°/10° → 0°, correct), Davison
     charts by averaged Julian day and place,
     midpoints, and a weighted synergy score.
   - **Searches** — exact transit-to-natal aspect
     dates, retrograde/direct stations, and sign
     ingresses, each by step-scan plus bisection to
     the crossing; eclipses via the Swiss
     Ephemeris eclipse searches; and the "next
     lunation" pair, which is misbuilt (§8,
     docket 151).
   - **Astrocartography** — each planet's
     equatorial coordinates from its ecliptic ones
     (the obliquity and GMST helpers carry their
     own IAU-formula fallbacks), then MC/IC earth
     longitudes and rising/setting lines sampled
     every 5° of latitude from −60° to +60°.

## 3. The ephemeris source

The sky itself is **the Swiss Ephemeris**, reached
only through `pyswisseph`'s `swe.calc_ut`,
`swe.houses`, `swe.rise_trans`, and the eclipse
searches. Three facts bound what that means here:

- **No ephemeris data files exist in this tree**
  (no `.se1` file is tracked anywhere in the
  repo), and the engine never calls
  `set_ephe_path`. What the library falls back to
  when no data files are configured is the
  library's own business — the engine neither
  chooses nor records it, so a chart printed here
  does not state which ephemeris model produced
  it. E-109's fixtures must pin that down.
- **When `pyswisseph` is absent, there is no
  ephemeris at all** — and most commands print a
  chart-shaped answer anyway (§8, docket 148).
  The two exceptions that do refuse are `lunar`
  and `solar-return`, and even they exit 0 after
  printing "pyswisseph required".
- **The rest of the sky-adjacent data is local
  or network, never stated on the chart:** the
  built-in city table (§5) is the offline source;
  Nominatim and kerykeion's GeoNames are network
  sources tried before it. A chart's header shows
  the place label and the timezone conversion,
  but not which source resolved the place.

## 4. Inputs, outputs, and the 16 subcommands

**Inputs** are command-line arguments only: dates
(`YYYY-MM-DD`), times (`HH:MM`), city/nation
names or explicit `--lat`/`--lon`, and
command-specific options. The engine reads no
files, no environment variables, and no config;
its only outward calls are the geocoding network
requests (§5) when the earlier tiers are in play.

**Output** is printed text only — a 76-column
box-drawn report on stdout, the Norse overlay
included (planet→god correspondences, sign→rune
correspondences, both constant tables in the
engine; the member's own notes record these as
modern syncretic associations, a living-tradition
overlay, not historical attestation). No command
writes a file, returns structured data, or sets a
nonzero exit code on any failure this slice
probed — failures print and exit 0.

| Subcommand | What it computes |
|---|---|
| `natal` | The full chart: positions, houses, aspects, dignities, lots, antiscia, Hellenistic layer, Norse layer, house overview |
| `transit` | Sky positions now (or at `--transit-date`) against the natal chart, with transit-to-natal aspects |
| `synastry` | Two charts' cross-aspects, with house overlays when both places are given |
| `solar-return` | The chart for the Sun's return to its natal longitude in a target year (iterative search) |
| `progressions` | Secondary progressions (a day for a year) and progressed-to-natal aspects at a tight 1.5° orb |
| `lunar` | Current phase, void-of-course, next lunations, Moon aspects — the one family that refuses without the ephemeris |
| `planet-hours` | The 24 planetary hours for a date and place |
| `lots` | The seven Arabic lots standalone |
| `hellenistic` | Sect, joys, triplicity and related Hellenistic analysis |
| `aspect-grid` | The full aspect matrix for a chart (no place; the time is taken as-is, §8 docket 155) |
| `dignity` | The dignity table, mutual receptions, and a ranked score summary |
| `antiscia` | Antiscia/contra-antiscia with connection detection (no place; time taken as-is) |
| `composite` | Midpoint composite chart, plus a Davison chart when places are given |
| `synergy` | Synastry + composite + midpoints + the weighted synergy score in one report |
| `predict` | Exact transit dates, stations, ingresses, eclipses over a window |
| `geoastrology` | Astrocartography MC/IC/ASC/DSC lines, with optional proximity analysis for a queried place |

## 5. Place and time — the geocoding cascade

`geocode_city` resolves a place in this order:
explicit `--lat`/`--lon` first; then Nominatim
(OpenStreetMap, network, no key); then kerykeion's
GeoNames subject lookup; then a **built-in
fallback table of 426 entries under 394 unique
keys** (US state capitals, metros, and major world
cities, built into the function body); and finally
a warning on stderr with a default of 0°N 0°E,
which the caller can detect only through the
returned `city_resolved=False` flag.

The timezone then comes from `timezonefinder` at
those coordinates, and `pytz` performs the
local→UTC conversion with historical DST rules
(`is_dst=None` first, standard-time fallback).
When no timezone can be found, the input time is
treated as UTC and the header says so. When any
backend package is missing, its tier silently
drops out — the cascade degrades tier by tier
with no statement of which tiers were live.

The gazetteer itself carries probed defects
(§8, docket 152): 27 keys are duplicated (most
with identical coordinates — but `charleston`
appears with both Charleston WV's and Charleston
SC's coordinates, and the later entry silently
wins); `tivat` carries Cancún's coordinates
verbatim; and the key `tientSin` can never be
reached, because lookups lower-case the query and
the key is not lower-case — Tianjin falls through
to the 0°N 0°E default, probed this slice.

## 6. Consumers today

**None in the companion.** No file under `src/`
mentions astrology at all (probed this slice);
no other member's code imports or shells to the
engine; the root tests touch it only through the
E-043/E-057 size pins. The elder record agrees in
its own words: the campaign's `UNWIRED_INVENTORY`
row calls it a "lunar phase + planetary aspects
library" (an understatement of the code — §7),
marks it "Hermes Agent mentioned (not Ember)",
and gives its integration path as "None planned."

So the consumers today are exactly one: **the
command line, run by hand** (historically as a
Hermes divination skill on the house machines,
per the member's own reference notes). E-110
builds the first real consumer — the engines as
services to the core, under typed requests and
responses — on this map and on E-107's, and
E-111 (the day's astrology as a computed Verdandi
stimulus) is this engine's first designed use.

## 7. Elder documents vs the code

- The two `docs/references/` gap notes (May 2026)
  list as missing: `dignity` and `antiscia`
  subcommands, a custom transit date, `--lat`/
  `--lon` overrides, exaltation-degree use, and a
  larger fallback table. **All of those are built
  in the code today** (16 subcommands; the
  dignity code does use exaltation degrees) — the
  notes are a record of an older engine, kept as
  provenance, not a current gap list. Two of
  their items remain true: synastry house overlays
  are now partly built (when both places are
  given), and void-of-course no longer matches
  their description (it is exact-targeting now,
  not the 0.1° scan they describe).
- `UNWIRED_INVENTORY`'s "lunar phase + planetary
  aspects library" understates a 16-command chart
  engine; the inventory's integration verdict
  (none planned) stands — Part VII is what
  changes it.
- E-006's docket 16 stands live, re-probed this
  slice: in the default environment the real
  commands exit 0 computing nothing (§8,
  docket 148).

## 8. Findings — the docket this map opens

Each finding was probed at this tree unless it is
marked a suspect; each is assigned to the Part VII
slice whose subject it is. Nothing here is fixed
by this mapping slice; nothing is left ownerless.

- **Docket 148 — without the ephemeris, most
  commands fabricate a chart instead of refusing
  → E-120** (failure honesty), with a contract
  note for E-110. Probed in the default env
  (`pyswisseph` absent): `calc_planet_positions`
  returns an empty dict, `calc_houses` returns
  equal 30° cusps with Ascendant and MC both at
  0°, and `natal` prints the full report shape —
  ASC "Aries 0°00'", Sun and Moon shown as "?",
  empty tables, a Day-chart verdict — and exits
  0. Only `lunar` and `solar-return` print a
  refusal, and they too exit 0. E-110's service
  contract must refuse before computing when the
  ephemeris is absent; E-120 owns the CLI's
  honesty (a stated error, a nonzero exit, no
  fabricated cusps anywhere — the equal-cusp
  fallback has no honest use).
- **Docket 149 — the Lot of Fortune and the Lot
  of Spirit are swapped → E-109.** Probed on
  synthetic positions (ASC 0°, Sun 0°, Moon 90°,
  day chart): the traditional day formula gives
  Fortune = ASC + Moon − Sun = 90°; the engine
  returns 270° at Fortune — Spirit's formula — and
  90° at Spirit. The internal helper applies
  `ASC + to − from` to argument pairs ordered the
  other way. Every lot built on Fortune or Spirit
  (Eros, Necessity, Courage, Victory, Nemesis)
  inherits the swap. E-109's accuracy fixtures
  re-pin this slice's battery probe on the fix.
- **Docket 150 — a planet in its fall is never
  scored as fallen → E-109.** The `FALL` table is
  built by inverting the exaltation table, which
  maps planet→sign, so `FALL` maps the exaltation
  sign back to a planet (collisions included:
  Cancer and Aries each serve two exaltations, so
  two planets vanish from it) — and the check then
  asks whether the planet equals the planet
  exalted in this sign, which the exaltation
  branch has already claimed. Probed: Sun in
  Libra and Moon in Scorpio — the textbook falls —
  both score with no Fall label (Peregrine and
  triplicity respectively). Falls must be derived
  as the sign opposite the exaltation; E-109
  re-pins the probe.
- **Docket 151 — "next lunation" does not find
  lunations → E-109.** `next_lunation` calls
  `swe.mooncross_ut` — the Moon's crossing of a
  given longitude — passing 0 and 2 as the target,
  commented as "0=New Moon, 2=Full Moon". A new
  moon is an elongation event (Moon meets Sun), a
  full moon its opposite; neither is a fixed
  longitude crossing, and 2° is not a phase in any
  reading. What `lunar` prints as the next new and
  full moons are the Moon's next crossings of 0°
  and 2° Aries. E-109 owns the correct search
  (elongation bisection, as its own transit
  searches already do) or the label's correction.
- **Docket 152 — gazetteer defects → E-109**
  (accuracy fixtures include place fixtures).
  §5: Tivat carries Cancún's coordinates; the
  `tientSin` key is unreachable by the lower-cased
  lookup, so Tianjin defaults to 0°N 0°E; 27 keys
  are duplicated, one (`charleston`) with two
  different cities' coordinates and a silent
  winner. The table is data the charts are built
  on; E-109's fixtures spot-pin the entries the
  house actually uses and rule the duplicates.
- **Docket 153 — the dependencies are declared
  nowhere (carries docket 18 into Part VII) →
  E-110, with the offline ruling at E-113.** Five
  packages, one hard requirement, no declaration
  file of any kind: there is no honest way to
  install this engine from the repo. E-110's
  service binding must carry the declaration as
  part of the contract; E-113 rules the offline
  claim precisely — the engine is offline only
  for places its built-in table (or explicit
  coordinates) covers, because its first two
  geocoding tiers are network services.
- **Docket 154 — the sidereal path is dead code
  → E-110.** `calc_planet_positions` accepts
  `tropical=False` (setting Fagan-Bradley sidereal
  mode), but no caller in the file ever passes it
  and no CLI flag exists: every chart the engine
  can print is tropical. E-110's contract decides
  whether the service exposes a sidereal option
  truly wired, or the branch comes out of the
  contract's surface — a dead option must not be
  served as a live one.
- **Docket 155 — two commands silently treat the
  input time as UTC → E-109.** `aspect-grid` and
  `antiscia` parse the date/time and build the
  Julian day directly — no place, no timezone
  conversion (the code's own comment says so for
  aspect-grid) — while the natal family converts
  local time to UTC. The same clock time therefore
  yields different skies across commands, and
  neither header states the convention. E-109's
  fixtures pin one stated convention per command.

**One suspect, not probed, carried to E-109:**
the solar-return iteration steps the Julian day
by `diff / 360.0` days per pass (at most half a
day, typically far less) under a 50-pass cap, from
a start roughly a month before the return — on
its face that converges too slowly to reach its
own 0.001° tolerance in 50 passes. This slice
could not probe it: the ephemeris package is not
installed in this environment and could not be
fetched at this tick (the package index returned
no matching distribution), so no live chart was
computed here at all. E-109 proves or clears it
with the ephemeris supplied.

**Accuracy fixtures against known references —
the state this slice hands E-109:** the member
has no fixtures of its own (no test suite). What
exists today is this slice's battery: the
Julian-day fallback exact at both reference
epochs, and the synthetic-position probes of the
derived maths (antiscia exact, composite midpoint
exact across the wrap, lunar phase exact at full
elongation — and the lots and fall probes failing
as docketed). Real-sky accuracy — engine output
against an independent ephemeris or published
reference values — is **NOT PROVEN** at this
slice, for the environment reason above. E-109
is charged with exactly that gate, under the
roadmap's fixture law: synthetic fixtures, or
Volmarr's own published data only.

## 9. Gate re-measurement (E-017 method)

Measured this slice, VM profile (Python 3.12.3,
pytest 9.1.1); raw logs in
`~/workspace/.verify-tmp/ember-e108/`.

- **Pre-doc standing check** (the batteries that
  pin this member's standing — E-057's table,
  E-043's install weight, E-089's canon guard):
  **20 passed** before this slice's files landed.
- **Member suite:** none exists — recorded as a
  fact of the map, not a pass.
- **Focal battery** (this slice's own):
  **11 passed**.
- **Focal set** (this slice's battery + the three
  standing batteries above): **31 passed** — the
  pre-doc 20 + this slice's 11, exact.
- **Run A** (whole suite, default env): **1 error,
  20 skipped**, exit 2 (docket 1, unchanged).
- **Run B** (default env, pgvector file excluded):
  **1517 passed, 6 failed, 34 skipped** — E-107's
  1506 + this slice's 11, exact; the 6 are the
  proven environment failures (Batch CDE ×3,
  G ×2, J ×1 — the sqlite_vec family).
- **Run D** (whole suite, extras supplied from
  the isolated dir): **1725 passed, 0 failed,
  20 skipped**, exit 0 — E-107's 1714 + 11, fully
  clean.
- This slice adds one architecture doc and one
  root battery and changes no member code, so the
  E-057 table stands un-re-measured (25 files /
  7,477,309 B, the pin inside the focal set
  verifying it).

## Carried forward

- Part VII continues. Next: E-109 (astrology
  accuracy gate).
- Dockets 148–155 opened here, owners: E-120
  (148, plus E-110's contract note), E-109 (149,
  150, 151, 152, 155, and the solar-return
  suspect), E-110 (153, 154, and 148's contract
  note), E-113 (153's offline ruling).
- NOT PROVEN at this slice: any real-sky accuracy
  figure (no ephemeris in this environment —
  E-109's gate, with fixtures under the roadmap's
  fixture law), any service binding (E-110), any
  use in conversation or ritual (E-111/E-112),
  any real-hardware figure beyond E-057's
  standing row.

*Filed by the E-108 slice, 2026-11-02. Next:
E-109 — astrology accuracy gate.*

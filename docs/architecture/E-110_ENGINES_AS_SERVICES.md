# E-110 — The Engines as Services to the Core

*Project Ember campaign, Part VII (The Inner Life:
Seiðr Engine & Astrology Engine) — fourth slice, the
first build of the part. Filed 2026-11-02 on branch
`yrsa/ember-road-build` in the campaign's own clone
(`~/workspace/ember-build`), on top of E-109 banked
(552354a) + its push record (1f3c083) + this slice's
IN PROGRESS marker (42437f1). Every count below was
measured this slice at this tree (probes in
`~/workspace/.verify-tmp/ember-e110/`); the live chart
figures were measured with the ephemeris supplied
from the isolated install E-108's correction recorded
(pyswisseph 2.10.3.2 at
`~/workspace/.verify-tmp/ember-e108/deps`), never
added to the repo. No README was touched.*

## The verdict, in plain words — read this first

**Both engines are now services the companion's core
can call: typed requests and responses, in one module,
`src/ember/engines.py`.** You hand the verse service a
`VerseRequest` — a form, maybe a world, maybe a seed —
and it hands back a `Verse`: the lines in reading
order and the engine's own rendering, or a plain
reason it cannot. You hand the chart service a
`ChartRequest` — a date, a time, a place — and it
hands back a `Chart`: positions, houses, aspects,
lots, and the chart's sect as data, or a plain reason.
Neither service ever raises a member's failure at its
caller, and neither ever dresses a failure up as an
answer.

**The two services differ honestly in what they can
promise today, and the difference is the dependency
declaration this slice makes law.** The verse engine
needs nothing but the standard library, so its service
answers in every environment, seeded requests
byte-reproducible. The astrology engine needs an
ephemeris package the member never declared anywhere;
where that package is absent — this machine's default
environment included — **the chart service refuses
before computing**, in words naming the missing
requirement, rather than serving the empty-positions,
fabricated-cusps chart its command line prints. Where
the ephemeris is present, the service serves the
chart E-109 proved: the London chart at J2000 comes
back through the service with the Sun at 280.3689
degrees and the Ascendant at 24.0146 — E-109's pinned
fixtures, reproduced through the new road.

**This slice also closes the one defect its roadmap
line carried outright: ljóðaháttr's lines now stand
in their true order** — pair, full line, pair, full
line — fixed at the source in the member, so every
consumer (the service first, the member's own command
line with it) reads the verse as the form intends.

## 1. The contract

The service binds under the member contract E-037
froze, in kinship rather than by addition: the frozen
API v1 surface is unchanged (bindings are consumers
of the freeze, not entries in it — the Kista binding
at E-100 set that precedent), and the service states
its own `CONTRACT_VERSION = "1.0"` under the same
rules: within a major version the shapes may only
widen with defaults.

The module imports only the standard library, and
imports neither member at module load (a fresh-process
check in the battery pins it): a process that only
wants the contract pays for neither engine. Members
are loaded lazily, from their own homes in this
monorepo — the verse package from `seidr_engine/`, the
astrology engine from its single file
`astrology-engine/astrology_engine.py`, loaded with
the stdout guard the E-108 battery proved (the engine
rebinds `sys.stdout` at import). An installed core
without the members beside it gets a refusal naming
the missing path, never an ImportError.

Results follow the house shape (the Well resolver's
and the Kista binding's manner): a result carries the
answer or a `reason`, never both; a reason names the
source that failed and the shape of the failure, in
plain words.

## 2. The verse service

`compose_verse(VerseRequest)`:

- **The request carries exactly what composition
  honours** — form, world, stanza count, kennings,
  alliteration strictness, seed. **Docket 144's
  contract note is executed here:** the member's own
  config fields `include_old_norse` (never consulted
  by composition) and `topic` (a stored label whose
  comment promises a thematic hint the composer never
  takes) are **not carried** — a contract field that
  silently does nothing is a promise the service
  refuses to make. A battery test pins both absences.
  E-112 decides the fields' fate in the member.
- **Validation happens before composing (docket
  143's contract note).** The form is checked against
  the member's registry (its own refusal, re-stated),
  the world against the engine's nine worlds, the
  stanza count and strictness against their shapes —
  so a bad world name is refused here, naming the
  true worlds, and never reaches the composer's
  silent borrowed-words fallback. Docket 143 itself,
  the library's behaviour, remains E-120's to fix at
  the member; the contract simply never serves it.
- **The response reports the world actually used.**
  An unchosen world is picked per composition by the
  composer; the response names it, so a consumer
  never has to guess which world the words came from.
- **Determinism is stated as it is:** a seeded
  request is byte-reproducible through the service
  (pinned); an unseeded one is not claimed
  reproducible. Docket 146 — the branding words and
  the CLI's differing seed — stands with E-113.

## 3. Docket 142 — CLOSED in scope (ljóðaháttr's order)

The member's `Stanza` built a ljóðaháttr stanza as
two pairs plus two full lines, but flattened them
pairs-first, full-lines-last, and its display
formatter walked the same wrong order: the first
full line printed after the *second* pair. The form's
own shape — stated in its class description and in
the composer's docstring — is pair, full line, pair,
full line.

Fixed at the source in `seidr_engine/seidr/forms.py`:
`Stanza.lines` now interleaves each pair's full line
after its pair (any further full lines keep their
place last), and `_format_ljodhattr` renders the same
order, a blank line between the two half-stanzas.
Probed at seed 42 before banking: the flattened
order is exactly pair 1, full line 1, pair 2, full
line 2, and the service's served lines and rendered
text agree (pinned in both the E-107 re-pin and this
slice's battery). The member's own suite stands at
38 passed, unchanged in count. The E-107 battery's
docket-142 probe is re-pinned to the corrected order
with attribution, as that slice directed.

## 4. The chart service

`request_chart(ChartRequest)` serves the natal chart
core: positions for every body the engine computes
(longitude, sign, degree, minutes, retrograde flag,
house), the twelve Placidus cusps, Ascendant and MC,
the aspect list (with each aspect's applying flag,
which the member's tuples carry), the seven Arabic
lots, and the chart's sect — all the member's own
maths, at E-109's proven standard, typed.

The refusal ladder, in order — each rung a stated
reason, none a fabricated answer:

1. The member file is missing → refused, naming the
   path the contract binds to.
2. **The ephemeris is absent → refused before
   computing (docket 148's contract note).** The
   reason names the missing hard requirement. The
   member's own no-ephemeris shapes — empty
   positions, equal 30-degree cusps, Ascendant at
   0 degrees Aries — are never served. Docket 148's
   CLI-wide honesty fix remains E-120's.
3. The request's own shapes are invalid → refused:
   lat and lon together or not at all, each in
   range; a place must be given somehow; and the
   calendar shapes are validated here (see §6).
4. The place cannot be resolved → refused: the
   engine's 0°N 0°E default is never served as a
   chart (see §6 for the flag's exact meaning).
5. The ephemeris returns no positions → refused:
   no chart is served from an empty sky.

The place road is the engine's own cascade with the
contract's priorities stated: explicit coordinates
first; a city name resolves through the cascade
whose offline tier is the built-in table (the
London fixture in the battery resolves to the
table's own 51.5074, -0.1278 with the network tiers
absent). The response carries the engine's own
timezone label verbatim — including, where no
timezone could be resolved, its statement that the
input time was treated as UTC — so the time
convention of every served chart is stated on the
chart, never silent (the E-109 §7 discipline,
carried into data).

## 5. Docket 153 — the declaration, carried by the contract

The astrology member declares its dependencies
nowhere — no packaging of any kind exists in the
member (E-108 §1). Until the member gains an honest
declaration of its own, the contract carries it:
`ASTROLOGY_DEPENDENCIES` in the service module names
all five packages the engine imports, as data a
consumer can read:

| Package | Imports as | Standing |
|---|---|---|
| pyswisseph | `swisseph` | **hard requirement** — the ephemeris itself; without it the service refuses (§4) |
| timezonefinder | `timezonefinder` | optional — without it no timezone name can be found, and input times are read as UTC, stated on the chart |
| pytz | `pytz` | optional — the local-to-UTC conversion itself, with historical DST rules; same stated fallback |
| kerykeion | `kerykeion` | optional — a network geocoding tier; without it the tier drops out |
| geopy | `geopy` | optional — a network geocoding tier (Nominatim); without it the tier drops out |

The verse member's declaration is
`SEIDR_DEPENDENCIES = ()` — standard library only
(E-107 §1) — and the emptiness is pinned, so a
future dependency cannot slip into either member
undeclared without this contract's battery noticing
the count. E-113 rules the offline claim precisely
(what "offline" may honestly mean, given the two
network tiers); this slice declares the packages
and their costs, which is what an installer needs.

## 6. Two measured subtleties the contract had to learn

- **The geocoder's "resolved" flag does not mean
  what its name suggests on the coordinate road.**
  `geocode_city` returns `resolved=False` for
  explicit `--lat`/`--lon` too — the flag means "the
  city *name* did not resolve", and the member's own
  CLI reads it exactly that way (a label switch).
  `resolve_birth`'s `city_default_used` inherits the
  meaning. The service therefore treats the flag as
  proof of the 0°N 0°E fall-through **only on the
  name road**; with explicit coordinates, the
  coordinates are the place. (Probed: a London
  coordinate request was refused as "unresolved" by
  the naive reading, and serves correctly under the
  member's own reading.)
- **A member is loaded, never imported, by the core.**
  The core's import↔extra map (E-044) is exact — every
  third-party name in a core import statement must be a
  declared extra — and the verse member's package is
  not a core dependency. The service's first draft
  imported the member's submodules by statement after
  loading the package, and this slice's first gate
  run caught the orphan (`seidr`, imported-not-
  declared) in both full runs. The service now reaches
  the submodules through the loaded package object
  (`importlib.import_module` on the already-loaded
  member), so the core's import statements name only
  the standard library — the Kista binding's
  subprocess discipline, in import form.
- **The member's date parsing normalises silently.**
  Its Julian-day conversion accepts a thirteenth
  month and lands in the next year without a word.
  The contract validates calendar dates (a real
  `YYYY-MM-DD`) and times of day (`HH:MM`, hour and
  minute in range) itself, before computing — probed:
  2000-13-01, 2000-02-30, and 25:00 all refuse in
  words; the valid chart is untouched.

## 7. Docket 154 — ruled: the contract is tropical only

The member's sidereal branch (`tropical=False`,
Fagan-Bradley) is dead code: no caller passes it, no
CLI flag exists (E-108 §8), and E-109's accuracy
gate proved the tropical path only — no fixture has
ever run against a sidereal position. The contract
therefore **carries no sidereal field**: the service
always computes tropical, every chart response
states `frame = "tropical"`, and a battery test pins
the field's absence from the request. A dead option
is not served as a live one. Wiring sidereal honestly
— a reachable branch plus accuracy fixtures of its
own — is future work no slice of this roadmap has
commissioned; if it is ever commissioned, it lands
as a contract addition under §1's widening rules,
not as a silent flag.

## 8. E-109 §3's question — the model travels with the chart

E-109 handed this slice the ephemeris-model
question: the engine never sets an ephemeris path
and the tree carries no data files, so which sky
produced a chart? The contract's answer: every
`Chart` carries `ephemeris_model`, stating
"pyswisseph built-in analytical model (no
ephemeris data files configured)". That is the
model whose ceiling E-109 measured — one arcminute,
worst miss 0.58 — and the claim that travels with
the answer is exactly that standard, never an
arcsecond one.

## 9. What this slice did not build

- The member-side fixes for docket 143 (the library
  refusing a bad world itself) and docket 148 (the
  CLI's honesty) stand with **E-120**, as docketed;
  this slice is the contract half of both notes.
- The astrology member's other analyses — synastry,
  progressions, the searches, astrocartography, the
  printed Norse overlay — are **not served**: they
  stay command-line only. Serving them is not
  roadmapped in Part VII; the chart core served here
  is what E-111 (the day's astrology as a computed
  stimulus) and E-112 (seiðr in conversation)
  consume.
- No consumer in conversation or ritual was built:
  E-111 and E-112 are those slices. NOT PROVEN at
  this slice: any sidereal accuracy (ruled out of
  the contract, §7), any real-hardware figure beyond
  E-057's standing rows (Part VII's budget rows are
  E-114), and the member's own dependency file —
  the declaration lives in the contract (§5) until
  a slice gives the member packaging of its own.

## 10. Gate re-measurement (E-017 method)

Measured this slice, VM profile (Python 3.12.3,
pytest 9.1.1); raw logs in
`~/workspace/.verify-tmp/ember-e110/`.

- **Pre-doc standing batteries** (E-057's table,
  E-043's install weight, E-089's canon guard):
  the first 20 of the focal set below.
- **Focal battery** (this slice's own, 18 tests):
  **13 passed, 5 skipped in the default shape**
  (the five live-chart fixtures skip without the
  ephemeris; the no-ephemeris refusal executes),
  and **17 passed, 1 skipped in the live shape**
  (the isolated ephemeris dir on the path; the
  no-ephemeris refusal skips, the London fixtures
  truly execute).
- **Focal set** (the standing 20 + E-107's 11 +
  E-108's 11 + E-109's 19 + this slice's 18):
  **74 passed, 5 skipped** in the default shape —
  the five skips exactly this battery's live-chart
  fixtures. (Its pre-doc form stood at 71 passed,
  3 failed — the failures being this doc's two pins
  and the E-109 book-total pin this slice re-pins
  with attribution in §10's last bullet.)
- **Member suite** (seiðr, its own shape): **38
  passed, 0 failed** — unchanged in count across
  the docket-142 repair. The astrology member has
  no suite (a standing fact of its map).
- **E-057 re-pinned consciously with attribution:**
  src 133 files / 963,473 B (the new service
  module), seidr_engine 11 / 103,956 B (the
  docket-142 repair grew forms.py by 228 B), total
  131,646,711 B, miss unchanged 256,017 B — both
  published copies; the E-107 battery's member-size
  pin and the E-109 battery's book-total pin
  re-pinned likewise, and the E-107/E-108
  batteries' no-consumer pins re-pinned to name
  this service as the members' sole core consumer.
- **Run A:** **1 error, 20 skipped**, exit 2 (docket 1,
  identical).
- **Run B:** **1549 passed, 6 failed, 39 skipped** —
  the 6 proven environment failures ONLY, name-for-name
  the standing set (Batch CDE ×3, G ×2, J ×1 — the
  sqlite_vec-missing family; = E-109's 1536 + 13 new
  in the default shape, exact; the bridge test that
  flaked in two earlier runs on this tree under load
  passed here and in Run D below).
- **Run D:** NOT CLEAN IN ONE RUN — recorded honestly.
  The completed run stood at **1756 passed, 0 failed,
  12 skipped, 1 error**: the error is a fixture-setup
  `sqlite3.OperationalError: disk I/O error` in an
  E-085 memory-logger test's mimir-well init — the
  proven contention mechanism family (E-101 recorded
  the same sqlite I/O errors across unrelated
  memory/logger files under cross-campaign load), and
  that test's whole file passes in isolation in this
  same extras shape, foreground-verified this slice
  (29 passed). A further attempt died at ~61% on a
  native bus error with no failure in its completed
  portion (the mechanism E-102 and E-109 recorded
  under load; the VM stood at ~1.6 GB memory available
  with sibling campaigns' suites running). A single
  clean Run D is OWED and E-111's tick discharges it
  first, as E-103 discharged E-102's; the expected
  shape by arithmetic is 1757 passed / 0 failed /
  12 skipped (the completed run's 1769 accounted
  tests = E-109's 1751 + 18 new, exact).

## Carried forward

- Part VII continues. Next: E-111 (ritual-shaped
  time: the day's astrology as a Verdandi stimulus)
  — and E-111's tick first discharges this slice's
  owed clean Run D (§10).
- Docket 142 CLOSED in scope here. Dockets 143 and
  148 stand with E-120 (their contract notes
  executed here); docket 144's fields stand with
  E-112 (kept out of the contract here); docket
  153's offline ruling stands with E-113 (the
  declaration itself carried here); docket 154
  ruled at the contract surface here (the branch
  itself stands in the member, unserved).
- NOT PROVEN at this slice: sidereal accuracy
  (out of contract), any served form of the
  astrology member's non-natal analyses, any use
  in conversation or ritual (E-111/E-112), any
  real-hardware figure beyond E-057's rows.

*Filed by the E-110 slice, 2026-11-02. Next:
E-111 — ritual-shaped time.*

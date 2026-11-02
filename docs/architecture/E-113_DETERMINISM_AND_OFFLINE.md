# E-113 — Determinism + Offline: Both Engines Fully Local

*Project Ember campaign, Part VII (The Inner Life:
Seiðr Engine & Astrology Engine) — seventh slice.
Filed 2026-11-02 on branch `yrsa/ember-road-build`
in the campaign's own clone
(`~/workspace/ember-build`), on top of E-112 banked
(63ac30b) + its push record (a0a5ae2) + this slice's
IN PROGRESS marker (9630d79). Every count below was
measured this slice at this tree (probes in
`/dev/shm/e113/` — this tick's gate scratch lived on
/dev/shm because the recurring home-quota EDQUOT flap
was live through the slice, the campaign's standing
pattern). No README was touched.*

## The verdict, in plain words — read this first

**Both engines are now reproducible and fully local
through the roads the companion actually uses, and
the two dockets that owned the questions are ruled
and closed.**

**Determinism — one seed semantics (docket 146).** A seeded seiðr
composition is reproducible *from its seed alone* —
the same poem from a fresh Skald, from a Skald that
has already composed other poems, from a Skald seeded
only through its config, in another process under a
different hash seed, through the member's CLI, and
through the E-110 service: all of them are the one
poem the seed names. Three separate defects had to
fall to make that sentence true, each probed at this
slice's opening (§1). An unseeded composition is not
reproducible — and is no longer *called*
deterministic anywhere the member speaks for itself:
its branding now says **deterministic when seeded**.

**The offline ruling (docket 153).** Through the
E-110 service, both engines are **fully local**: the
verse engine needs nothing beyond the standard
library and composes whole under a cut network; a
chart is computed from local data only — the
ephemeris is the library's built-in model, the
timezone lookup and conversion are local data, and
the place resolves only from explicit coordinates or
the member's built-in table. The astrology member's
two network geocoding tiers (Nominatim and
GeoNames) are **never consulted through the
service**: a place they alone could find is neither
offline nor reproducible, so a city the table does
not carry is refused in words, never fetched. The
precise claim is therefore: *this engine is offline
exactly for the places its built-in table or
explicit coordinates cover* — and the member CLI's
own cascade keeps the network tiers as its own
road, by its own choice, stated in its code.

**Date-pinned charts.** A chart through the service
is a pure function of its pinned date, time, and
place: byte-equal across calls and across processes
at two pinned moments (§3), and cast whole under
the network cut with zero external attempts.

## 1. Docket 146 — the three defects under "deterministic"

E-107 §6 probed the surface claim (seeded library
composition reproducible; unseeded not; the CLI's
seed a different seed). This slice's opening probes
went further, and found the seeded claim itself
only narrowly true:

- **A reused Skald was not reproducible.** Probed:
  one `Skald(seed=42)` composing the seed-42 config
  twice gave two different poems, and a Skald seeded
  *only* through its config (`Skald()` +
  `PoemConfig(seed=42)`, fresh each time) likewise
  differed run to run. The cause: composition resets
  the Skald's own random stream from the config seed,
  but the *words* are drawn from the **lexicon's**
  stream, which nothing reset — its state was
  whatever the holder's history had made it. The
  E-110 service escaped this only by building a
  fresh Skald per request.
- **A seeded poem differed across processes.** The
  alliteration-group pick chose from `list(set(...))`
  — a string set's order follows the process's hash
  randomization, so under `PYTHONHASHSEED=0` and
  `=1` the same seed chose different groups and
  different poems. (Every earlier "reproducible"
  pin in this campaign compared within one process,
  where the order happens to be stable.)
- **The CLI's seed was not the library's seed**
  (E-107 §6, re-probed): five derived attempt seeds,
  `(seed or 42) + attempt × 7919`, failures silently
  swallowed, the highest scorer printed — a seeded
  CLI poem was the best of five *other* seeds'
  poems.

## 2. The fixes, at the source

- **The lexicon can be reseeded, and composition
  reseeds it.** `Lexicon.reseed(seed)` restarts the
  lexicon's stream; `Skald.compose` and
  `Skald.compose_poem` restart both streams (the
  Skald's own — the per-stanza seed derivation draws
  from it — and the lexicon's) at the composition's
  seed before composing. A fresh Skald's streams
  already stand at that seed, so the canonical
  fresh-holder poems are byte-unchanged; what
  changes is that every other holder now composes
  the *same* poem. Probed after the fix: fresh,
  reused, and config-only holders agree exactly, at
  one stanza and at two, and `compose` on a reused
  Skald repeats its seeded stanza.
- **The group pick is sorted.** `_pick_alliteration_group`
  now chooses from `sorted(groups)` — the seed's
  choice is the same in every process. Probed: the
  CLI at seed 42 under three hash seeds prints
  byte-identical output, and the poem in it is the
  library's seed-42 poem.
- **The CLI composes once, at its given seed.**
  The best-of-five loop is gone from
  `seidr/cli.py`, with the reason commented at the
  site: `--seed S` prints the poem the library
  composes at S (the score survives as verbose
  metadata about that one poem). A composition that
  raises now reaches the CLI's own failure words
  instead of being silently swallowed among
  attempts. The member's suite stands at 38 passed, 0 failed (§6),
  and the battery pins CLI output equal to the
  library poem across hash seeds.
- **The branding says the conditional truth.** The
  package docstring (`seidr/__init__.py`) and the
  pyproject description now read *deterministic
  when seeded*. Two surfaces stand deliberately
  untouched, named here so the accounting is whole:
  the member's README (this campaign never touches
  any README; its own seed passage already states
  the conditional form — "deterministic with a
  seed") and the elder Yggdrasil design corpus
  (kept as provenance, as at E-107/E-108; its
  unqualified word is a record of the elder design,
  and the corrected claim of record is this slice's
  and the member's live surfaces).

Docket 146 is therefore CLOSED in scope: one seed
means one poem, on every road, and nothing the
member says about itself claims more.

## 3. Determinism, the astrology side

The chart maths has no random element: a chart is
Julian-day arithmetic over the ephemeris model.
What could vary was never the sky but the *place*
(§4's network tiers) and the holder's environment.
With the place road ruled local, the battery pins
the whole claim in the live shape: the London chart
at 2000-01-01 12:00 (E-109's/E-110's fixture moment)
byte-equal across calls and across processes, and
a second pinned moment — 1990-06-15 12:00, London
through the built-in table — at Sun 84.0898°
and Ascendant 164.7423°, cast under the network
cut (§4). E-111's day stimulus and E-112's verse
offers inherit both rulings unchanged: they ride
on these services and these seeds.

## 4. Docket 153 — the offline ruling, executed

E-110 carried the declaration (five packages, one
hard requirement); this slice rules and builds the
offline claim:

- **The member gained an offline road.**
  `geocode_city(..., offline=True)` and
  `resolve_birth(..., offline=True)` in
  `astrology_engine.py` skip the Nominatim and
  kerykeion/GeoNames tiers entirely; explicit
  coordinates and the built-in table still resolve,
  anything else falls through to the member's stated
  default flag. The default road is unchanged —
  the CLI's cascade keeps its tiers, in its order.
- **The service always takes the offline road.**
  `request_chart` resolves through
  `resolve_birth(..., offline=True)`, and the
  contract's words (the module docstring, the
  request's docstring, the two network packages'
  dependency roles) now say so: the service *never
  consults* those tiers. Their packages remain
  declared — the member CLI uses them — with their
  standing corrected from "the offline road" to
  the service's refusal.
- **Proven, not argued.** The battery fakes a
  geocoder that would resolve any place, and pins:
  on the offline road a table city resolves from
  the table with the fake never called; a
  table-absent city falls to the stated default
  with the fake never called; on the default road
  the same fake *is* consulted and resolves it —
  the contrast is the ruling. In the live shape
  (every geocoding package installed) the service
  refuses Woonsocket in words — a real place the
  table does not carry — instead of fetching it,
  and casts the London day under a socket-level
  network cut with **zero** recorded attempts.

Docket 153 is therefore CLOSED in scope: the
declaration stands at E-110 as amended here, and
the offline claim stands precisely as §0 states it
— fully local for table places and explicit
coordinates, a stated refusal beyond them, through
the service; the CLI's network cascade is its own
road and makes no offline claim.

## 5. What this slice did not build

- **No change to the CLI's default cascade.** The
  member command line still tries Nominatim and
  GeoNames before its table, by design of its own
  road; only the service's road is ruled offline.
  A reader of the CLI's output still cannot tell
  which tier resolved a place — that labelling is
  not this slice's commission (E-119/E-120 own the
  member's docs and failure words).
- **No new ephemeris or data files.** The sky is
  still the library's built-in analytical model
  (E-109 §3), and the gazetteer's contents are
  E-109's ruled shape, untouched here.
- **No determinism claim for unseeded anything.**
  Unseeded verse stays irreproducible by design,
  and E-112's draw discipline (a seed is required)
  stands as the conversation layer's answer to it.
- NOT PROVEN at this slice: any real-hardware
  figure beyond E-057's standing rows (Part VII's
  budget rows are E-114, next), and any live
  conversation consuming these guarantees.

## 6. Gate re-measurement (E-017 method)

Measured this slice, VM profile (Python 3.12.3,
pytest 9.1.1); raw logs in `/dev/shm/e113/` (see
the filing note at the head of this record).

- **Pre-doc standing batteries** (E-057's table,
  E-043's install weight, E-089's canon guard):
  the first 20 of the focal set below.
- **Focal battery** (this slice's own, 15 tests): **12 passed, 3 skipped in the
  default shape** (the three live-chart fixtures
  skip without the ephemeris) and **15 passed in
  the live shape** (the isolated ephemeris dir on
  the path — every fixture executes, including the
  chart cast whole under the network cut)
- **Focal set** (the standing 20 + E-107's 11 +
  E-108's 11 + E-109's 19 + E-110's 18 + E-064's
  16 + E-111's 10 + E-112's 16 + this slice's
  15 = 136): **123 passed, 13 skipped** in the default shape — the thirteen skips exactly the live-ephemeris fixtures of the E-110 (5), E-111 (5), and E-113 (3) batteries.
- **Member suite** (seiðr, its own shape):
  **38 passed, 0 failed** — unchanged across the reseeds, the sorted pick, and the CLI rewrite.
- **E-057 re-pinned consciously with attribution:**
  src 135 files / 994,019 B (the contract words in `engines.py`), seidr_engine 11 / 105,889 B (the reseed, the sorted pick, the CLI rewrite, the branding lines), astrology-engine 25 / 7,483,464 B (the offline road in the one engine file), total 131,680,683 B, miss unchanged 256,944 B — both published copies; the E-107 battery's member-size pin, the E-108 battery's member-size pin, and the E-109 battery's book-row and book-total pins re-pinned with attribution (its doc-needle pin stands — E-109's record of its own tree).
- **Run A:** **1 error, 20 skipped**, exit 2
  (docket 1, identical).
- **Run B:** **1582 passed, 6 failed, 47 skipped**
  — the 6 proven environment failures ONLY,
  name-for-name the standing set (Batch CDE ×3,
  G ×2, J ×1 — the sqlite_vec-missing family;
  = E-112's 1570 + 12 new, exact, this slice's
  three live-chart fixtures skipping in the
  default shape). The first Run B attempt, begun
  before this record was filed, also failed its
  two doc tests (this record not yet on disk and
  E-109's book-row needle mid-re-pin at that
  hour); the banked run is the re-run on the
  filed tree.
- **Run D:** **1790 passed, 0 failed, 20 skipped**
  CLEAN (= E-112's 1778 + 12 new, exact, this
  slice's three live-chart fixtures skipping in
  this shape as in Run B's). Three earlier
  attempts on this same tree stand recorded, none
  of them a code failure: attempt 1, 1789 passed /
  1 failed (the E-067 live-socket bridge test read
  its feed fallback under load; that file passes
  whole in isolation — it and this slice's
  battery together ran 33 passed, 3 skipped in
  the continuation tick); attempt 2
  died at ~43% with its log truncated when the
  opening tick's window closed; attempt 3, 1787
  passed / 3 failed, all three integration
  acceptance failures carrying `OSError: [Errno
  122] Disk quota exceeded` on home-state writes
  — the recurring home-quota EDQUOT flap, proven
  live in the same window by a direct write probe
  to `~/.ember/state` failing with Errno 122 and
  by the same test failing in isolation on the
  same error; the flap cleared on its own and
  the banked run above is the next attempt on
  the identical tree.
- The package alone now weighs 993,231 B —
  still under the E-112 re-measured all-in anchor
  (1,275,211 B), so no anchor re-measurement was
  owed this slice; docket 159's growth accounting
  stands with E-114/E-197 as filed.

## Carried forward

- Part VII continues. Next: E-114 (budget rows:
  both engines in the budget book (E-057) — with
  docket 159 carried, Part VII's contribution to
  the core's install growth weighed there).
- Dockets 146 and 153 CLOSED in scope here.
  Dockets 143 and 148 stand with E-120 (their
  contract notes executed at E-110); docket 159
  stands with E-114 and E-197.
- NOT PROVEN at this slice: a live chat relying
  on these guarantees, any real-hardware figure
  beyond E-057's rows, the CLI cascade's tier
  labelling (§5).

*Filed by the E-113 slice, 2026-11-02. Next:
E-114 — budget rows.*

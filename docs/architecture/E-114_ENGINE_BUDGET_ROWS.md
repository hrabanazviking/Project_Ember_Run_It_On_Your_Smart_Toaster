# E-114 — Budget Rows: Both Engines in the Budget Book

*Project Ember campaign, Part VII (The Inner Life:
Seiðr Engine & Astrology Engine) — eighth slice.
Filed 2026-11-02 on branch `yrsa/ember-road-build`
in the campaign's own clone
(`~/workspace/ember-build`), on top of E-113 banked
(1e49deb) + its push record (762fb4e) + this slice's
IN PROGRESS marker (3da3804). Every count below was
measured this slice at this tree (probes and install
targets under `/dev/shm/e114/` — gate scratch on
/dev/shm, the campaign's standing pattern). No README
was touched, no member or core code was changed: this
slice measures, publishes and pins.*

## The verdict, in plain words — read this first

**The verse engine is toaster-sized in every way
there is. The astrology engine's sky is pi-sized and
works inside even the toaster's memory. What is not
small — what fits no profile in the book at all — is
knowing what o'clock a place means, at the packaging
the package index serves today.**

**Seiðr.** The whole tracked member weighs
105,889 bytes; the runnable package inside it is
88,707 bytes and it depends on *nothing* beyond the
standard library, so carrying it in costs exactly
that — about a twentieth of the toaster's install
ceiling. A seeded verse composed through the E-110
service peaked at **14.7 MiB** of memory (the member
on its own: 13.8 MiB), a few thousandths of a second
of work on a heavily contended VM. It writes nothing
and runs no resident process: at rest and standing
idle it costs exactly zero.

**Astrology.** The member's tracked weight
(7,483,464 bytes) is a mirage: **7,230,510 bytes of
it — 96.6% — is twelve loose pictures**, and the
engine itself is one file of 140,715 bytes (the
remaining 112,239 bytes are its docs and licences).
Carrying in *the sky* — that one file plus its one
hard dependency, pyswisseph as installed
(7,639,165 bytes: a 7,601,904-byte compiled module
and its 37,261-byte dist-info) — totals
**7,779,880 bytes: the pi profile only**, 92.7% of
the pi install ceiling, over the phone's and nearly
four times the toaster's. Casting a pinned chart
through the service peaked at **18.1 MiB** — inside
even the toaster's turn ceiling.

**The local-time road is the spender.** A chart's
local-time conversion rides on timezonefinder +
pytz (E-110's declaration, docket 153). Installed
fresh from the index today (timezonefinder 9.2.0,
its data package 4.2026.6, numpy 2.5.4, pytz
2026.6 — the member pins no version anywhere), the
timezonefinder closure alone weighs
105,138,077 bytes: its data now ships as a separate
33,950,543-byte package, and it hard-requires numpy
(68,409,352 bytes as installed) plus a cffi chain
(1,709,087 bytes) and flatbuffers (220,278 bytes).
With pytz (1,074,846 bytes) the full local road —
sky and all — weighs **113,992,803 bytes and fits
no profile**, 6.8 times the laptop's install
ceiling. With the road live, one chart peaked at
38.5 MiB — still inside the toaster's turn ceiling,
but 60% of it, against the sky-only shape's 28%.
And the road is *optional in exactly the way E-110
built it*: without those packages the service still
casts, reads the input time as UTC, and says so in
the answer's own words. The honest shape of the
choice is therefore: **the sky fits the pi; local
time, at today's packaging, fits nothing, and is an
extra a carrier chooses with open eyes.**

**Docket 159 — Part VII's growth, weighed.** The
core package grew 55,122 tracked bytes across Part
VII so far, and every byte is attributed below
(§5): three new core modules (54,711 bytes) plus
411 bytes of budgets.py carrying this very book's
re-measured anchor. That is about a fifth of the
package's whole growth since the founding
measurement; the rest pre-dates Part VII.

## 1. The charter and the method

- **The roadmap's E-114 line** — "Budget rows: both
  engines in the budget book (E-057)": E-057 priced
  every member's *checkout* weight; E-103 then priced
  one member (the vault) the way the core was priced
  — at rest, in use, and to carry in. This slice
  gives the two Part VII engines the E-103 treatment
  and publishes the rows in `docs/BUDGET_BOOK.md` §7.
- **Docket 159**, opened at E-112's gate (the package
  alone had outgrown E-041's all-in install anchor;
  re-measured there at 1,275,211 bytes in all) and
  carried by E-113: Part VII's contribution to that
  growth is weighed here (§5); the whole-campaign
  claims audit stands with E-197.

**Method.** Tracked sizes by the E-057 method
(`git ls-files`, on-disk bytes). Installed sizes as
the packages stand installed: pyswisseph from the
campaign's isolated deps dir (E-108's install), the
timezone and geocoding packages from fresh
`pip install --target` installs made by this slice
(bytecode caches included in a package's own tree,
the E-103 discipline; versions named wherever a
number depends on them). Memory is a fresh process's
peak resident set (VmHWM from `/proc/self/status`),
median of three runs, the E-057 method; the bare
interpreter's floor by the same method this slice is
10.8 MiB. Times are in-process medians over 21 calls
inside those processes, recorded as contended-VM
shape (load average 8–12 throughout, sibling
campaigns running) — they price the shape of the
work, never a quiet-machine promise. Judgements are
made against the live `ember.budgets` ceilings,
re-derived by this slice's battery.

## 2. Seiðr — the rows

| What | Measured |
|---|---|
| Tracked member | 11 files / 105,889 B |
| — the runnable package (`seidr/`) | 88,707 B |
| — the rest (its tests 9,753 B, README 5,826 B, licence 1,086 B, pyproject 517 B) | 17,182 B |
| Dependencies | none — the standard library only (`SEIDR_DEPENDENCIES` is empty, pinned at E-110) |
| Carrying-in total | 88,707 B — toaster (5.1% of its ceiling at the tracked weight) |
| Import-level RAM floor (E-057, standing) | 13.3 MiB |
| Peak, composing through the member itself (seeded, two stanzas) | 13.8 MiB |
| Peak, composing through the E-110 service (seeded) | 14.7 MiB |
| One composition's work | ~0.002–0.003 s (contended median) |
| At rest / standing idle | 0 B written; no resident process — zero by construction |

The lexicon is the member's data and it is *code*:
337 entries inside `lexicon.py` (32,833 B), inside
the package figure above — there is no data file to
carry separately and nothing to download, ever
(E-113's offline ruling is also this engine's budget
shape).

## 3. Astrology — the rows

| What | Measured |
|---|---|
| Tracked member | 25 files / 7,483,464 B |
| — twelve loose pictures (png/jpg/jpeg) | 7,230,510 B (96.6%) |
| — the engine itself (one file) | 140,715 B |
| — docs, licences, notices | 112,239 B |
| Its one hard dependency, pyswisseph as installed | 7,639,165 B |
| **The sky carried in (engine file + pyswisseph)** | **7,779,880 B — pi only (92.7% of the pi ceiling)** |
| Import-level RAM floor (E-057, standing, deps absent) | 12.4 MiB |
| Peak, loading the member through the service (ephemeris present) | 17.9 MiB |
| Peak, one pinned chart through the service (sky only) | 18.1 MiB |
| Peak, one chart with the local-time road live | 38.5 MiB |
| One cast's work | ~0.003–0.004 s (contended median) |
| At rest / standing idle | 0 B written; no resident process — zero by construction |

Notes the table cannot hold:

- **The pictures are not the engine's cost to a
  carrier** — they are the member directory's
  checkout weight (E-057's row, standing unchanged),
  never installed with the engine. Quoting
  7,483,464 B as "the astrology engine's size" is
  exactly the confusion this slice exists to end:
  the engine is 140,715 B of code; what a carrier
  actually pays is the carrying-in rows.
- **The timezone road, itemised** (fresh installs,
  versions as served 2026-11-02): timezonefinder
  9.2.0 itself 848,817 B; its separate data package
  33,950,543 B; numpy 2.5.4 (package + bundled libs)
  68,409,352 B; the cffi chain 1,709,087 B;
  flatbuffers 220,278 B — a closure of
  105,138,077 B before pytz's own 1,074,846 B.
  The finder *works* at this version — probed live:
  London resolves to Europe/London through the
  member's own call, and the chart's label carries
  the conversion — it is the *packaging*, not the
  function, that busts the book. An older
  timezonefinder shipped its data inside its own
  package; that shape is **not measured here** and
  no number is claimed for it. The member declares
  no version (the E-110 declaration names packages
  and roles only), so "as installed today" is the
  only honest row.
- **The network tiers are CLI-road weight, never
  the service's** (E-113): geopy + geographiclib as
  installed measure 1,141,378 B; kerykeion 6.0.5's
  own package measures 5,339,199 B, and installed
  alone into an empty target its full closure
  weighs 166,928,928 B (numpy again, a 24,094,339 B
  libephemeris, skyfield's data, zstandard — the
  GeoNames tier is the heaviest single road priced
  in this book). Each closure in this slice was
  measured as installed alone; installed together
  the two tiers would share their numpy, so their
  weights are never simply added. The service
  never consults either tier, so no companion
  carrier pays any of it unless they choose the
  member CLI's own road.

## 4. What the rows judge

- **Seiðr passes the toaster whole** — install,
  working memory, storage, idle — the first member
  besides the core itself to do so on measured
  numbers (the vault, E-103/E-106, is toaster-sized
  at rest and in use but laptop-class to install).
- **The astrology sky passes the pi for install**
  and passes even the toaster for working memory;
  a toaster-profile companion therefore *can* be
  offered charts on a pi-class carrier with room to
  spare, and the memory shape alone would fit the
  smallest machine — it is the ephemeris's compiled
  weight, not its working weight, that sets the pi
  floor. No document may call the astrology engine
  toaster-installable.
- **Local time is an open-eyed extra.** Until some
  slice re-roads the timezone lookup (a smaller
  finder, a vendored table, the host's own zoneinfo
  data — all future choices, none made here), the
  book's position is E-110's behaviour, priced: the
  service casts without it and labels the time as
  UTC in the answer. **A new standing note, not a
  docket:** if a future slice wants local time on
  small hardware, the timezonefinder closure
  measured here is the number it must beat; that
  want is recorded for E-197's audit and Part VII's
  remaining slices to see, and no slice is
  commissioned by this one.
- **Neither engine moves E-057's table.** No member
  file changed in this slice; both E-057 rows stand
  as published, and this slice's battery pins them
  verbatim beside the new rows.

## 5. Docket 159 — Part VII's share of the growth, weighed

The record under docket 159: the installed core
outgrew its founding anchor — all-in 978,843 B
(E-041) → 1,275,211 B re-measured (E-112), a
growth of 296,368 B, of which the package alone is
729,802 B → 993,231 B at E-113's banking — a
package growth of 263,429 B (the rest is dist-info
and the sqlite-vec extra's own growth, E-112 §6).

Part VII's contribution, by the tracked method
(`git ls-tree` on `src/`; the package is `src/`
minus its 788-byte README):

- At Part VII's opening tree (the E-106 banking
  commit, c0befb8): `src/` 132 files / 938,897 B —
  the package at 938,109 B.
- At E-113's banking: `src/` 135 files /
  994,019 B — the package at 993,231 B.
- **Growth across Part VII: 55,122 B**, attributed
  to the byte: `src/ember/engines.py` 26,350 B
  (E-110, grown by E-112/E-113's contract words),
  `src/ember/day_astrology.py` 9,493 B (E-111),
  `src/ember/seidr_conversation.py` 18,868 B
  (E-112) — 54,711 B of new modules — plus
  `src/ember/budgets.py` +411 B, which is the
  E-112 anchor re-measurement's own entry in this
  book. 54,711 + 411 = 55,122, exact; no other
  core file moved in Part VII.

So Part VII contributed **about a fifth (20.9%) of
the package's whole growth since the founding
measurement**; the remaining four-fifths pre-date
it (Parts II–VI). The growth bought the engines'
service binding, the day stimulus and the
conversation layer — and the re-measured all-in
figure still fits the toaster's 2 MiB install
ceiling with 39% to spare, which is why E-112
re-anchored rather than cut. **Docket 159 is
therefore CLOSED in this slice's scope — Part VII
weighed, every byte attributed — and stands with
E-197 for the whole-campaign claims audit**, which
inherits these figures and the standing rule from
E-112: no Ember document may repeat the founding
under-a-MiB install claim.

## 6. What this slice did not build

- **No re-roading of the timezone lookup.** The
  closure measured in §3 is a packaging fact about
  today's index, recorded with its versions; choosing
  a smaller road is a design act for a future slice
  (or E-197's audit to commission), not a budget
  row's patch.
- **No dependency was installed into the tree or
  the core's environment.** The fresh installs live
  in this slice's /dev/shm scratch and the isolated
  deps dir; the member's declaration is unchanged.
- **No ceiling moved, no anchor changed**, no
  member or core code touched, no README touched.
- NOT PROVEN at this slice: any figure on real
  small hardware (every number here is a VM
  measurement judged against profile ceilings — the
  E-048 discipline, not an E-049 device proof);
  any older timezonefinder's installed weight; a
  live conversation consuming these rows.

## 7. Gate re-measurement (E-017 method)

Measured this slice, VM profile (Python 3.12.3,
pytest 9.1.1); raw logs in `/dev/shm/e114/gate/`
(see the filing note at the head of this record).

- **Focal battery** (this slice's own, 17 tests):
  **17 passed** — the tracked breakdowns and the
  docket 159 growth re-derived live from git, the
  judgements re-derived against the live ceilings,
  the pyswisseph pin verified against the isolated
  deps dir, and the empty-scratch-dir proof run.
- **Focal set** (the standing 20 + E-107's 11 +
  E-108's 11 + E-109's 19 + E-110's 18 + E-064's
  16 + E-111's 10 + E-112's 16 + E-113's 15 + this
  slice's 17 = 153): **140 passed, 13 skipped** in
  the default shape — the thirteen skips exactly
  the live-ephemeris fixtures of the E-110 (5),
  E-111 (5), and E-113 (3) batteries.
- **Member suite** (seiðr, its own shape):
  **38 passed, 0 failed** — unchanged; no member
  code was touched by this slice.
- **E-057 re-pin: none owed.** No member file and
  no `src/` file moved in this slice (the book's
  new subsection lives in `docs/`, the battery in
  `tests/`); the standing rows — src 135 / 994,019 B,
  seidr_engine 11 / 105,889 B, astrology-engine
  25 / 7,483,464 B, total 131,680,683 B, miss
  unchanged 256,944 B — are verified standing by
  the focal set and by this slice's verbatim row
  pins.
- **Run A:** **1 error, 20 skipped**, exit 2
  (docket 1, identical).
- **Run B:** **1599 passed, 6 failed, 47 skipped**
  — the 6 proven environment failures ONLY,
  name-for-name the standing set (Batch CDE ×3,
  G ×2, J ×1 — the sqlite_vec-missing family;
  = E-113's 1582 + 17 new, exact). The first Run B
  attempt was killed and restarted on the final
  tree after the kerykeion install completed
  mid-gate and the battery grew from 16 to 17
  tests (§3's closure figure landed with it); the
  banked run is the re-run on the filed tree.
- **Run D:** **1807 passed, 0 failed, 33 skipped**
  CLEAN (= E-113's 1790 + 17 new in the passed
  count, exact). The 33 skips itemised from the
  log: 14 in the pgvector real-backend file (10
  podman-not-installed, 4 Gungnir-unreachable —
  that file is collected in this extras shape,
  where its import succeeds, and its tests skip
  honestly; it is the file Run A/B exclude), the
  13 live-ephemeris fixtures as in Run B, and 6
  other standing skips (funi real-model ×2, the
  wyrdforge import, MCP shapes ×2, one Batch J
  MCP-extra guard).
- The package alone still weighs 993,231 B —
  under the E-112 re-measured all-in anchor
  (1,275,211 B), so no anchor re-measurement was
  owed this slice; docket 159's Part VII weighing
  is §5.

## Carried forward

- Part VII continues. Next: E-115 (the dictionary
  binding: cleasby-vigfusson as a lookup service for
  the companion).
- Docket 159 CLOSED in scope here (Part VII
  weighed); it stands with E-197 for the claims
  audit. Dockets 143 and 148 stand with E-120.
- NOT PROVEN at this slice: any real-hardware
  figure for either engine, a smaller timezone
  road.

*Filed by the E-114 slice, 2026-11-02. Next:
E-115 — the dictionary binding.*

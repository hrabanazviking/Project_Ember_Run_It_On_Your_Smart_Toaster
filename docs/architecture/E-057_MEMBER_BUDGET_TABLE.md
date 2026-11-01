# E-057 — Member budget table: every member's cost per profile

*Part III, slice E-057. Roadmap line: "Member budget table:
every member's cost per profile — the monorepo's weight,
honestly itemised." The published table lives in
`docs/BUDGET_BOOK.md` §7; its pinning tests are
`tests/unit/test_member_budget_table_e057.py`.*

## In plain words

**The companion core is tiny; the monorepo around it is
not — and now every member's weight is on one table.**
The twelve members that can run (the core plus the eleven
imported members of the E-002 census) weigh **131,546,922
bytes (125.45 MiB) of tracked files** between them, and
almost all of that weight is three members: mempalace
(59,049,715 B), the Old Norse dictionary (24,221,782 B)
and Verdandi (17,033,233 B) — and in each case the weight
is data, not code (benchmark corpora, a test snapshot,
loose images; E-002/E-014).

Judged against the budget book's own install ceilings,
four members fit even the toaster's 2 MiB (the core,
mimir-well, seidr_engine, bifrost), kista fits the phone,
four fit the pi (astrology-engine, Hamr, Open-VTT,
CloakBrowser's tracked tree), and three fit **no profile
at all** — mempalace, the dictionary, and Verdandi, which
misses even the laptop's 16 MiB ceiling by 256,017 bytes.
*(Re-measured at E-061, which changed Verdandi's tracked
weight: at E-061's filing the totals above and the Verdandi
row read 131,211,064 bytes and 16,817,105 B / 179 files,
missing the laptop ceiling by 39,889 bytes; E-061 added
`Verdandi/event_contract.py` and touched three Verdandi
files, and this living table was updated to match the tree,
as its pinning tests require. Re-measured again at E-062,
which added `Verdandi/context_budget.py` and reworked the
conversation logger's context builder and the injector:
Verdandi then read 181 files / 16,852,579 B, the total
131,246,538 bytes, the laptop miss 75,363 bytes.
Re-measured again at E-063, which added
`Verdandi/logger_law.py` and reworked the conversation
logger (the delete right and the current.json ownership
rule): Verdandi now reads 182 files / 16,871,542 B, the
total 131,265,501 bytes, the laptop miss 94,326 bytes.
Re-measured again at E-064, which added
`Verdandi/stimuli.py` and the hub's stimulus entrance in
`nervous_system.py`: Verdandi then read 183 files /
16,889,384 B, the total 131,283,343 bytes, the laptop
miss 112,168 bytes. Re-measured again at E-065, which
added `Verdandi/reflexes.py` and repaired Vör and the
conversation reactor's focus: Verdandi then read 184 files /
16,903,436 B, the total 131,297,395 bytes, the laptop
miss 126,220 bytes. Re-measured again at E-066, which
added `Verdandi/nerve_health.py` and reworked the hub's
status probe and Skuld's pulse_metrics reading: Verdandi
then read 185 files / 16,919,924 B, the total
131,313,883 bytes, the laptop miss 142,708 bytes.
Re-measured again at E-067, which added
`Verdandi/cross_member.py` and the core's nerve bridge
`src/ember/nerve.py` and rewired the heartbeat's nerve
transport and the chat loop: Verdandi now reads 186 files /
16,935,635 B, the core 130 files / 826,913 B, the total
131,342,243 bytes, the laptop miss 158,419 bytes.
Re-measured again at E-068, which added
`Verdandi/hermes_nerves.py` and registered the Hermes
lifecycle events in `Verdandi/event_contract.py`: Verdandi
now reads 187 files / 16,956,837 B, the total 131,363,445
bytes, the laptop miss 179,621 bytes. Re-measured again at
E-069, which added `Verdandi/replay.py` (the ordering &
replay law): Verdandi then read 188 files / 16,968,259 B,
the total 131,374,867 bytes, the laptop miss 191,043
bytes. Re-measured again at E-070, which added
`Verdandi/backpressure.py` (the shedding law) and reworked
the hub ring buffer in `nervous_system.py`: Verdandi now
reads 189 files / 16,984,725 B, the total 131,391,333
bytes, the laptop miss 207,509 bytes. Re-measured again at
E-071, which added `Verdandi/nerve_privacy.py` (the nerve
privacy law) and the privacy filter in the core's nerve
bridge `src/ember/nerve.py`: Verdandi now reads 190 files /
16,996,351 B, the core 130 files / 831,437 B, the total
131,407,483 bytes, the laptop miss 219,135 bytes.
Re-measured again at E-072, which added
`Verdandi/memory_feed.py` (the logger-as-memory-source
law): Verdandi now reads 191 files / 17,009,560 B, the
total 131,420,692 bytes, the laptop miss 232,344 bytes.
Re-measured again at E-073, which added
`Verdandi/standalone.py` (the standalone law) and taught
the hub and the core's nerve bridge the VERDANDI_HOME
resolution: Verdandi now reads 192 files / 17,014,457 B,
the core 130 files / 831,912 B, the total 131,426,064
bytes, the laptop miss 237,241 bytes. Re-measured again
at E-075, which added `Verdandi/load_truth.py` (the
load-truth harness): Verdandi now reads 193 files /
17,030,199 B, the total 131,441,806 bytes, the laptop
miss 252,983 bytes. Re-measured again at E-076, which
repaired the hub's stop probe (docket 106), bounded
Verdandi's dependency declarations (docket 92, Verdandi
half), and fixed its CLI integration tests (docket 6
family): Verdandi now reads 193 files / 17,032,082 B,
the total 131,443,689 bytes, the laptop miss 254,866
bytes. Re-measured again at E-078, whose docket-111
FTS-sync fix (triggers in `schema.py`, executed at open
in `core.py`, plus the member regression tests) is
mimir-well's first change since its import: mimir-well
now reads 59 files / 614,283 B, the total 131,450,297
bytes, the laptop miss unchanged at 254,866 bytes.
Re-measured again at E-080, which added the core's
memory face `src/ember/well/memory_face.py` (the one
memory contract over Brunnr + mimir-well): the core now
reads 131 files / 857,356 B, the total 131,475,741
bytes, the laptop miss unchanged at 254,866 bytes.
Re-measured again at E-082, which grew the same face
with its lifecycle surface (growth accounting, decay
delegation, stale-index pruning): the core now reads
131 files / 864,538 B, the total 131,482,923
bytes, the laptop miss unchanged at 254,866 bytes.
Re-measured again at E-083, which enforced persona
separation on the same face (persona-id validation,
index exclusion from document search, widening scans):
the core now reads 131 files / 870,557 B, the total
131,488,942 bytes, the laptop miss unchanged at
254,866 bytes. Re-measured again at E-084, which added
the user's memory rights to the same face (inspect,
correct, export, delete — with turn tombstones in the
face's sidecar): the core now reads 131 files /
884,982 B, the total 131,503,367 bytes, the laptop
miss unchanged at 254,866 bytes. Re-measured again at
E-085, which added the logger reconciliation to the
same face (provenance-tracked feed ingest, orphan
audit, session retraction): the core now reads
131 files / 899,122 B, the total 131,517,507 bytes,
the laptop miss unchanged at 254,866 bytes.
Re-measured again at E-086, which added the
WYRD-shaped export to the same face (and the
delete-order repair its gate duty found): the core
now reads 131 files / 918,056 B, the total
131,536,441 bytes, the laptop miss unchanged at
254,866 bytes. Re-measured again at E-087, whose
drills fixed the face's index-record save (docket
122, in the core's memory face) and mimir-well's
supersede atomicity + restore path (dockets 121 and
124 — mimir-well's second and third changes since
its import): the core now reads 131 files /
918,847 B, mimir-well 59 files / 618,769 B, the
total 131,541,718 bytes, the laptop miss unchanged
at 254,866 bytes. Re-measured again at E-088, whose
long-life soak added the year's measured anchors to
the budget book (the core's only change this slice):
the core now reads 131 files / 921,884 B, the total
131,544,755 bytes, the laptop miss unchanged at
254,866 bytes. Re-measured again at E-089, whose
docket-126 fix grew `Verdandi/load_truth.py` (the
socket-path relocation): Verdandi now reads 193 files
/ 17,033,233 B, the total 131,545,906 bytes, the
laptop miss 256,017 bytes. Re-measured again at
E-092, whose docket-108 closure bounded mimir-well's
dependency declarations both ways (flask <4,
setuptools <82 — mimir-well's fourth change since
its import): mimir-well now reads 59 files /
618,776 B, the total 131,545,913 bytes, the laptop
miss unchanged at 256,017 bytes. Re-measured again at
E-093, whose docket-127 fix grew the Aesir adapter
(the custody mode-0600 refusal): the core now reads
131 files / 922,893 B, the total 131,546,922 bytes,
the laptop miss unchanged at 256,017 bytes.)*
None of this makes any member cost anything to a core
user: since E-043 the members are excluded from the
core's distribution and are never installed with it. A
member's cost is paid only by someone who carries the
whole monorepo or runs that member from a checkout — the
table prices exactly that choice, per profile.

## 1. Method (so any keeper can re-measure identically)

- **Tracked size**: `git ls-files` per top-level member
  directory, each tracked file's on-disk byte size summed
  (the E-002/E-014 method). Measured 2026-10-31 on the VM
  at the slice's opening tree. Bytecode caches and other
  untracked artefacts are not counted. The slice touches
  no member directory, so the figures are the tree's at
  banking as well; the E-057 tests re-derive them live and
  fail if the published table drifts.
- **Smallest covering profile**: the smallest profile (in
  `ember.budgets` order) whose *install ceiling* is at
  least the member's tracked size — the book's ceilings
  turned on the members, exactly as E-055 §6 promised.
  This is a checkout-weight judgement, stated as such:
  no member except the core has a measured *installed*
  weight (the core's is 978,843 B, E-041).
- **Import-level RAM floor**: a fresh Python process that
  imports the member's top package and reads its own
  VmHWM from `/proc/self/status` (the E-042 method),
  median of three runs on the VM, bare default env. The
  bare interpreter's floor is **10.1 MiB** by the same
  method, so a floor near it means "the top package is
  light", never "the running program costs this". Raw
  runs: `~/workspace/.verify-tmp/ember-e057/import_ram.json`.
  Running costs, where a prior slice measured them, are
  named in §3 — they are always the larger, truer figure.

## 2. The table (as published in `docs/BUDGET_BOOK.md` §7)

| Member | Tracked files | Tracked size | Smallest profile covering it | Import-level RAM floor |
|---|---|---|---|---|
| `src/` (ember core) | 131 | 922,893 B | toaster | 12.0 MiB |
| `Verdandi/` | 193 | 17,033,233 B | none | 12.6 MiB |
| `kista/` | 25 | 2,770,218 B | phone | 24.2 MiB |
| `mempalace/` | 257 | 59,049,715 B | none | 11.5 MiB |
| `mimir-well/` | 59 | 618,776 B | toaster | 20.8 MiB |
| `seidr_engine/` | 11 | 103,728 B | toaster | 13.3 MiB |
| `astrology-engine/` | 25 | 7,477,309 B | pi | 12.4 MiB |
| `bifrost/` | 10 | 77,916 B | toaster | 15.2 MiB |
| `Hamr/` | 168 | 6,081,769 B | pi | 40.1 MiB |
| `Open-VTT/` | 209 | 6,768,730 B | pi | NOT MEASURED |
| `CloakBrowser/` | 112 | 6,420,853 B | pi | NOT MEASURED |
| `cleasby-vigfusson-old-norse-dict/` | 170 | 24,221,782 B | none | NOT MEASURED |

## 3. Honest limits and the rows that need a second look

- **Import floors are floors.** mempalace's 11.5 MiB is
  its top package only — its search/MCP stack pulls
  ChromaDB + ONNX (E-012), which this bare env does not
  import. astrology-engine's 12.4 MiB imports a module
  whose compute dependencies (pyswisseph and kin) are
  absent and undeclared (E-006/E-007): importing is not
  computing. Verdandi's floor is its heartbeat package;
  the hub's *running* cost is E-041's live 21.9 MiB.
  The core's running idle is 40.7 MiB (E-041), not 12.0.
- **NOT MEASURED, with reasons.** Open-VTT runs on the
  Godot engine, which is absent on the VM (E-006) — no
  honest RAM figure exists here. The dictionary is a
  Next.js/Node app with `node_modules` absent (E-006) —
  likewise. CloakBrowser's import fails in the bare env
  (`ModuleNotFoundError: httpx`, its declared dependency
  shape), and its real cost is its proprietary Chromium
  binary, which is **absent from the tree** (E-007): the
  tracked 6,420,853 B is wrapper + JS only, and the
  vendored ~190 MB idle / ~200 MB binary figures are
  upstream's claims, recorded for E-179 — never adopted
  as measurements.
- **Hamr's floor is the heaviest import (40.1 MiB)** —
  still inside even the toaster's 64 MiB turn ceiling as
  an import, but Hamr *building* is governed by its own
  perf budget (peak ≤1,500 MB, E-015), a laptop-class
  act; E-146 owns its asset budgets in Part IX.
- **The rest of the estate is checkout-only.** The
  remaining tracked weight — `docs/` (~44 MiB, growing
  with this campaign), root loose files (~35 MiB of
  images and codices), `assets/` (3,406,778 B), `tests/`,
  and the small scaffolding dirs (`config/`, `deploy/`,
  `examples/`, `scripts/`, `tools/`, `vendor/`; under
  100 KB together) — totals roughly 83 MiB of the
  ~209 MiB tracked tree. None of it is installed or run
  with the companion; it is the monorepo's library and
  workshop, priced here so the whole tree is accounted
  for, and deliberately not judged against profiles.
- No ceiling moved, no anchor in `ember.budgets`
  changed, no member code touched, no README touched,
  no new docket items. Docket 62's duplication (some of
  Verdandi's image weight is triplicated, E-014) stands
  as recorded; removing anything remains Volmarr's word.

## 4. Gate

- New tests standalone (with E-055's drift armour):
  **15 passed** (7 E-057 + 8 E-055) in the default env.
- Slice gate Run B (default env, pgvector file
  excluded): **1054 passed, 6 failed, 25 skipped,
  1 warning** — 1047 E-056 baseline + 7 new; the 6 are
  the proven environment failures, identical set.
- Slice gate Run D (whole, extras): **1111 passed,
  0 failed, 19 skipped, 1 warning**, exit 0 —
  1104 + 7 new, reconciles exactly. (Logs in
  `~/workspace/.verify-tmp/ember-e057/gate/`.)
- No README touched. No code in `src/` changed — this
  slice measures, publishes and pins; it does not
  rebuild.

E-058 next — the Part III gate.

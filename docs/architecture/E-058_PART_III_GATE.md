# E-058 — Part III Gate: budgets enforced, Toaster Test verdict recorded

*Project Ember campaign, Part III (Tiny Hardware Is the Soul)
— GATE. Filed 2026-10-31 on branch `yrsa/ember-road-build`
in the campaign's own clone (`~/workspace/ember-build`), at
campaign commit 4f78bcd (E-057 banked + its push record + this
slice's IN PROGRESS marker). This gate closes Part III on the
roadmap's own criteria for E-058: "budgets enforced by tests;
Toaster Test verdict recorded with its device named; summary
filed." No production code was changed in this slice, no
README was touched. Gate re-measurements were run this slice;
raw logs live in `~/workspace/.verify-tmp/ember-e058/gate/`.*

## The gate, in plain words — read this first

**Part III is done. Ember's smallness is no longer a hope
or a slogan — it is measured, published, and guarded by
tests that fail if it ever stops being true.** The budget
book names a ceiling for each machine size, from the
smallest ("toaster") to a laptop. The companion core fits
every one of them: installed it weighs under a megabyte,
sitting idle for a full hour it spent no processor time at
all, a month of daily chatting grows its storage by under
half a megabyte, and updates, battery manners, thermal
manners and graceful shedding at the budget's edge are all
built and measured. The whole set of budget tests runs as
one permanent command, and at this gate it passes clean:
**122 passed in the bare environment, 129 passed with the
optional extras supplied.**

**The Toaster Test verdict, with its device named:** on
**Mimir — the house's Raspberry Pi 5 Model B Rev 1.1**,
the smallest real computer in the house — Ember ran its
toaster settings end to end with a real, deliberately tiny
language model, ready in about a fifth of a second and
never using more than 27.2 MiB. **The name is cashed for
Ember itself.** It is honestly **not cashed** for a whole
companion living alone on a literal 512 MiB machine: the
two model programs the normal first-day shape loads need
about a gigabyte between them by the model server's own
accounting, twice that whole host, before Ember or the
operating system take a byte. That limit belongs to today's
model programs, not to Ember, and it is recorded under its
own name — the comfortable member of the toaster class is
the 1 GB-and-up machine.

Honesty, kept plain: a real phone running Ember is
**NOT PROVEN** (the phone proof is SIMULATED — the house's
real phone was offline, and no Android shape exists in this
tree); a real battery's drain rate and the Pi's thermal
behaviour under Ember are likewise **NOT PROVEN**, each
named in §5. The full test suite, with its optional extras
present, is completely green: **1111 passed, 0 failed.**

## 1. Gate criteria — each one checked, not assumed

| # | Criterion (roadmap E-058) | Evidence | Result |
|---|---|---|---|
| G1 | Every Part III slice E-041–E-057 banked | CAMPAIGN_STATE slice ledger, E-041–E-057 all DONE; all 17 per-slice documents present under `docs/architecture/` (verified by directory listing this slice) | PASS |
| G2 | Budgets enforced by tests | §2: the permanent budget gate re-run this slice in both shapes, exit 0 both times; the armour is also inside every whole-suite gate (E-042, E-056) | PASS |
| G3 | Toaster Test verdict recorded with its device named | §3: E-049's verdict restated with its device — Mimir, Raspberry Pi 5 Model B Rev 1.1 — core cashed, whole 512 MiB host NOT CASHED | PASS — as a two-halves verdict, exactly as measured |
| G4 | Full suite green before banking | §4: Run D (whole, extras) **1111 passed, 0 failed, 19 skipped**, exit 0; Run B identical to E-057's banked counts | PASS |
| G5 | Part III's docket accounted for — nothing found, nothing lost | §5: closed items named with their closing slice; open items named with their carried-forward home | PASS — as an accounting; the open items themselves remain open |
| G6 | Summary filed | The section above ("The gate, in plain words") and §6 | PASS |
| G7 | The road below checked | §7: no re-cut demanded; Part IV (Verdandi, the nerve hub) is next and owns the items Part III hands it by name | PASS — no re-cut |

## 2. Budgets enforced by tests, re-proven at the gate

The enforcement has two layers, both re-run this slice
(VM profile, Python 3.12.3, pytest 9.1.1, TMPDIR on the
workspace overlay; logs `budget_default.log` and
`budget_extras.log` in the gate log dir):

- **The permanent budget gate** — the one command E-056
  gave the project,
  `python3 scripts/dev/run_budget_gate.py`, running the
  fifteen enrolled Part III budget files (E-041–E-055)
  as one gate:
  - default env: **122 passed, 7 skipped**, exit 0 —
    identical to E-056's banked record; the 7 skips are
    the honest extras guards (shapes that need
    `sqlite_vec` skip where it is absent);
  - extras supplied: **129 passed, 0 skipped**, exit 0 —
    identical to E-056's banked record.
- **The whole-suite gates** (§4) collect the same armour
  plus E-056's keeper tests and E-057's member-table
  tests, so a budget regression fails the campaign's
  ordinary slice gate as well as the dedicated one.

What the armour guards, in plain terms: the four
profiles' ceilings themselves (toaster 2 MiB install /
64 MiB idle / 64 MiB turn / 2 MiB a month, and the phone,
pi and laptop rows above it — `docs/BUDGET_BOOK.md` §1),
install weight, the dependency diet, the idle hour, cold
start under the flat 5.0 s cap, the three device proofs
at their graded anchors, a month of storage, thermal
patience, update weight, battery duty, graceful
shedding, the published book's drift tests, and the
member budget table. A ceiling that moves without its
measurement moving fails a test; that is what "enforced"
means here.

## 3. The Toaster Test verdict, recorded with its device

From E-049, restated at this gate without softening
either half:

- **Device: Mimir (`purpleviking1`) — Raspberry Pi 5
  Model B Rev 1.1, aarch64, 16 GiB RAM** — the smallest
  real computer in the house. No Pi Zero-class or
  older/smaller machine exists in the house; the test
  ran the **toaster profile** on pi-class hardware and
  claims exactly that, never a Pi Zero run.
- **The core half — CASHED.** Clean clone of the
  campaign head, fresh install, real chat model
  (qwen2.5:0.5b, the smallest rung) and real embedding
  model (nomic-embed-text) served by the device's own
  Ollama, real sqlite_vec Well, memory proven across
  separate processes: ready **0.21 s** (the flat cap is
  5.0 s, unrelaxed), peak Ember RSS **27.2 MiB** (the
  toaster turn ceiling is 64 MiB), installed
  **1,956,428 B** (the toaster install ceiling is
  2 MiB), storage projection 0.40 MiB/month against a
  2 MiB ceiling. Recall *quality* at the 0.5B rung is
  partial — the model's limit, recorded under its name.
- **The whole-host half — NOT CASHED.** Measured on the
  device by `ollama ps` with both day-one models loaded:
  the chat runner reports 442 MB and the embedding
  runner 565 MB — **~1,007 MB of model house on a
  512 MiB host**, before Ember (27.2 MiB) or any
  operating system. Even the chat model alone, plus the
  Tiny document's OS figure (~150 MB) and Ember's turn
  ceiling, sums to ~656 MB. A smaller serving shape
  (an embedding-free Well, a sub-0.5B rung, a different
  server) is a future road, named in E-049 and not
  claimed here or anywhere in Part III.

The same grading discipline holds for Part III's other
two device proofs: the Pi proof (E-047) is **REAL** —
Mimir again, phi3:mini, Ember ready in ~0.2 s at
27.1 MiB — and the phone proof (E-048) is **SIMULATED**
— a phone-shaped room on the VM (two cores, a hard
512 MiB limit, 43.0 MiB peak), never a real phone.

## 4. Gate re-measurement (E-017 method, part-gate shapes)

Measured this slice at HEAD 4f78bcd, VM profile
(Python 3.12.3, pytest 9.1.1), TMPDIR on the workspace
overlay; raw logs in
`~/workspace/.verify-tmp/ember-e058/gate/`
(`runA.log`, `runB.log`, `runD.log`).

| Run | Shape | Gate result |
|---|---|---|
| A | Whole suite, default env | Interrupted at collection — **1 error, 11 skipped**, exit 2 (docket 1, unchanged) |
| B | Default env, pgvector file excluded (the slice gate) | **1054 passed, 6 failed, 25 skipped, 1 warning** — identical to E-057's banked gate |
| D | Whole suite, extras supplied from the isolated dir | **1111 passed, 0 failed, 19 skipped, 1 warning**, exit 0 — identical to E-057's banked gate |

Run B's 6 failures are the proven environment failures
of docket 2/3 (optional-extra coupling), identical since
the E-001 baseline; Run D proves the same tests pass
with the extras they need. Run A's 11 skips (against the
E-017 freeze's 8) are explained at the E-040 gate: Part II
added three skip-guarded extras test files, each skipping
honestly when `sqlite_vec` is absent and passing in
Run D. No count moved at this gate, in any shape.

## 5. Part III's docket — closed, and carried forward

Closed in Part III (from E-015/E-016's archaeology
assignment and Part III's own new items 90–92):

- **20** (the core's optional `keyring` secret source
  declared in no extra) — closed E-044 (the `secrets`
  extra now declares it).
- **23, root half** (unbounded requirements) — closed
  E-044 (every root requirement bounded both ways).
- **65, measurement half** (Verdandi's six RAM figures
  conflating hub and heartbeat) — settled E-041 (hub
  21.9 MiB live, heartbeat 18.4 MiB import-level, both
  ~20 MiB-class on the VM).
- **66** (the Tiny profile's own numbers summing past
  its host) — grading closed E-049 by direct
  measurement (§3's whole-host verdict).
- **67** ("Ember itself ~50 MB RAM") — proven TRUE and
  generous at E-041 (measured worst idle 40.7 MiB);
  the companion "~50 MB installed" claim was struck
  there as written (the installed core is 0.93 MiB)
  and its front-door wording belongs to E-197.
- **69, core half** (the sibling matrix's unsourced
  round numbers) — superseded by the budget book at
  E-041; the member table that replaces them whole
  landed at E-057.
- **70** (five members stating no budget at all) —
  their rows landed at E-057 (with mempalace/mimir's
  deeper comparison at E-078 and kista's at E-103, as
  E-041 assigned).
- **90** (the book's anchors were VM measurements) —
  closed at its stated grades: Pi re-anchored REAL
  (E-047), phone SIMULATED (E-048), toaster settled
  (E-049), the closure recorded at E-055.
- **91** (E-042's storage re-derivation drifting from
  the book's estimate) — closed E-050 (a simulated
  month measured 408,566 B all-in; the book's
  694 B/turn figure stands unrevised, by measurement).

Carried forward, open, with a named home each — this
gate closes Part III on its stated criteria; it does
**not** claim these are fixed:

- **23, member half = docket 92** — member pyprojects
  still declare unbounded or undeclared dependencies.
  Each member's own part bounds it when that part works
  the member (Verdandi → Part IV, kista → Part VI,
  bifrost → Part VIII, Hamr → Part IX), alongside
  dockets 18/19/21.
- **65, wording half** — the Verdandi documents that
  mix hub and heartbeat figures are E-060's to fix in
  Part IV's concordance.
- **68** — Hamr's two budgets (perf.py's enforced
  1.5 GB build budget vs Phase 17's 7.5 GB shape) are
  recorded with their scopes and left to Part IX, as
  E-041 assigned; neither is a core cost.

Other honest limits Part III leaves on the record, each
with its owning road: a **real phone** running Ember is
NOT PROVEN (E-048 is SIMULATED; no Android shape exists
in this tree); a **real battery's drain rate** is NOT
PROVEN (E-053 shaped and measured the duty cycle's CPU
cost — 0.000 s in a rest — on the VM; no house battery
device runs Ember); **Pi thermal behaviour** under
Ember is NOT PROVEN (E-051's etiquette is VM-proven;
the Toaster Test's device sat at 45.2 °C with no thermal
pressure, which is a weather note, not a thermal proof);
**member RAM for Open-VTT, the dictionary and
CloakBrowser is NOT MEASURED** (E-057, with reasons:
Godot absent, Node deps absent, and CloakBrowser's real
weight is its proprietary binary, absent from the
tree); and essay-length turns outgrow the toaster's
storage ceiling in a month (3.51 MiB — they fit the
phone and up; Part V's lifecycle slice E-082 owns the
long-store rules, with E-050's numbers as its brief).

## 6. Plain-language summary (for the campaign record)

Part III asked: *is "runs on your smart toaster" true,
and can it stay true by itself?* Seventeen slices
answered it. The budget book (E-041) replaced every
inherited claim with a measurement and set four
profiles' ceilings; the tests (E-042) made those
ceilings fail loudly if crossed. The install got ~41×
lighter (E-043: the source package fell from 45 MB to
1.1 MB once the members stopped riding along) and its
dependencies were dieted and bounded (E-044). An idle
hour cost nothing at all (E-045); cold start is capped
at a flat five seconds (E-046). Then the proofs: a real
Raspberry Pi with a real model (E-047, REAL), a
phone-shaped room (E-048, SIMULATED), and the Toaster
Test itself (E-049) — the core cashed on Mimir, the
whole-512-MiB-host claim honestly not cashed, because
today's model programs are simply bigger than that
host. A month of storage, thermal patience, update
weight, battery duty and graceful shedding followed
(E-050–E-054), the book was published as one readable
document (E-055), its tests became one permanent
command (E-056), and every member of the monorepo was
weighed onto one table (E-057). What Part III did not
do is make a real phone, a real battery, or a literal
512 MiB whole companion proven — those stay NOT PROVEN,
named, with their roads named.

## 7. The road below — checked

Part IV (E-059–E-076, Verdandi: the nerve hub) follows
in roadmap order; nothing in Part III's evidence
demands a re-cut. Part IV inherits, by name: docket
65's wording half at E-060 (the concordance), docket
92's Verdandi half (its dependency bounds), Verdandi's
live load truth at E-075 (its hub measured 21.9 MiB at
E-041; the heartbeat's daemon load is Part IV's to
measure), and the budget book as the standing law its
own budget rows must fit. Later parts inherit likewise:
E-078/E-082 (Part V) take the memory comparison and
the long-store lifecycle from E-050/E-057's numbers;
E-103 (Part VI) takes kista's budget row; E-179
(Part XI) takes CloakBrowser's vendored cost claims,
never adopted as measurements here. The roadmap file
was not edited by this gate.

## Carried forward

- Part III is CLOSED by this gate. Next: E-059
  (Part IV) — Verdandi mapped.
- Open and carried, not lost: docket 92 (→ Parts IV /
  VI / VIII / IX, per member), 65's wording half
  (→ E-060), 68 (→ Part IX), 67's front-door wording
  remainder (→ E-197).
- NOT PROVEN at this gate: a real phone, a real
  battery's drain rate, Pi thermal behaviour, a whole
  companion on a literal 512 MiB host, member RAM for
  Open-VTT / the dictionary / CloakBrowser — each with
  its owning part or road named in §5.

*Filed by the E-058 slice, 2026-10-31. Part III gate: PASS.
Next: E-059 — Verdandi mapped (Part IV opens).*

# E-088 — Long-life soak: a simulated year of memory

*Part V, slice E-088. Roadmap line: "Long-life soak: a
simulated year of memory within budgets (accelerated
fixtures)." The soak ran against the one memory face
(E-080) and the two bounded engines behind it; the
conformance battery is
`tests/unit/test_memory_soak_e088.py`, and the year
anchors live in `ember.budgets` beside E-050's month.*

## In plain words

**We lived a year with the companion in about sixteen
minutes, and weighed everything it remembered.** A
simulated year — 365 days, twenty conversations a day,
one new fact remembered a day, a fact corrected every
month, the program restarted every month, and a full
lifecycle pass at year's end — grew every store the
companion keeps to **5,717,556 bytes in all (5.45 MiB)**.
That is inside every profile's twelve-month allowance,
including the toaster's (24 MiB), with about 4.4×
headroom, and no single month's growth came near the
toaster's 2 MiB monthly ceiling. After the year's decay
pass, **not one fact had been deleted**: all 365 daily
facts were still there and still believed, the oldest
simply worn down to the lowest importance — forgetting
here means fading, never vanishing (that honesty is
docket 113's, proven again at year scale). One real
defect of rhythm did surface: left to a monthly cadence,
the forgetting curve **compounds** — it re-applies the
whole age of a fact on every pass, so a monthly lifecycle
floors old facts about twice as fast as the stated
30-day half-life promises (docket 125, below; the
year-end single pass this soak ran is not affected).

## 1. How the year was accelerated

The simulation script lives in the slice's verify area
(`~/workspace/.verify-tmp/ember-e088/simulate_year.py`,
results in its `results.json`); the method matters more
than the machine it ran on:

- **The companion**: the real `MemoryFace` on the
  **toaster** profile (word search over facts, no fact
  index — the hardest budget), one synthetic persona,
  "mabel". Content is synthetic and canon-shaped (the
  harbour / beekeeper / garden / choir / river world of
  the earlier Part V fixtures; E-089's law applied
  early, as in E-082/E-087). No real companion history
  exists in any fixture.
- **The year**: 2026-01-01 → 2026-12-31, 365 days ×
  20 turns = **7,300 turns** at the book's reference
  workload, E-041's typical-turn fixture (~40 words a
  side). One living fact per day (**365**), and on each
  month's last day that month's first fact was
  superseded by a corrected version (**12**
  supersessions, 377 fact rows in all).
- **Acceleration is timestamp placement only.** Every
  write really happened, through the face. Episodes
  carry their simulated `started_at` (the adapter
  stores it); each fact's mimir-well timestamp was set
  to its simulated day at a month boundary, while the
  face was closed, by direct sqlite update on the
  fixture file — no product code was touched, and decay
  at year end saw honest ages (simulated day *d* aged
  365 − *d* days). Nothing was bulk-inserted, mocked,
  or skipped.
- **Restarts**: the face was closed and reopened at
  every month boundary (12 restarts) — a year of
  companionship is a year of sessions, not one process.
  Every month end also ran the growth report and the
  stale-index prune (both no-ops on the toaster's
  index-off shape, as designed), and every store was
  weighed with the face closed.
- **The diary**: the real `Diary` in chat's connected
  shape (start + memory-connected + two lines per turn
  + end, one session a day, simulated timestamps) —
  E-082 left its 365-files-a-year shape to this soak.
- **Decay ran once, at year end**, as a full
  `run_lifecycle` pass — deliberately, because of
  §4's cadence finding.

Write wall time was 967 s on the contended campaign VM
(the diary's per-entry fsync is most of it). That is a
method note, not a product figure: wall time is not
frozen (E-017) and no speed claim is made from it.

## 2. The year's weight

Every store, weighed closed at year end:

| Store | Bytes | What it holds |
|---|---:|---|
| Brunnr | 4,366,336 | 7,300 episodes (591 B/episode all-in) |
| mimir-well | 528,384 | 377 fact rows + audit trail |
| Face sidecar | 137,731 | one persona tag per turn + fact bookkeeping (~19 B/turn) |
| Diary | 685,105 | 365 daily files (~1,877 B/day) |
| **Total** | **5,717,556** | **5.45 MiB for the whole year** |

- **Against the budgets**: the toaster's storage
  ceiling is 2 MiB/month, a 24 MiB year; the year used
  5.45 MiB — headroom ×4.4. Steady monthly growth
  (months 2–12, from the monthly curve) averaged
  **446,445 B/month (~0.43 MiB)** — under the toaster's
  monthly ceiling in every month, month 1 included
  (814,849 B all-in, fixed schemas and all). The
  phone/pi/laptop years fit by the same arithmetic with
  far more room. **No ceiling moves; no lifecycle rule
  tightens.** E-050's month verdict stands at year
  scale.
- **Cross-checks against the older anchors**: Brunnr's
  591 B/episode sits beside E-050's 585.4 B steady
  marginal (same store, year scale — consistent);
  mimir-well grew ~718 B per fact row over the year
  beside E-078's 745 B anchor, its fixed schema
  (~266 KB on day one) dominating its file; the diary
  cost 685,105 B for the year (~94 B/turn all-in,
  E-050's month measured 93.85 — near-identical).
- **The sidecar is now priced.** E-050's month
  predates the face, so its 0.39 MiB never carried the
  face's bookkeeping. The soak prices it: 137,731 B a
  year, ~19 B per turn tag — small, linear, and now in
  the book (the `MEASURED_YEAR_*` anchors in
  `ember.budgets`).
- **The diary's file count, judged** (E-082's open
  question): 365 files, one per day, 0.65 MiB in all.
  Finding files is by name, reading recent days is by
  date — the count costs nothing a small machine can
  feel. **The shape stands; no diary lifecycle is
  needed.** Recorded so no future slice "fixes" it.
- **Stated, not measured**: an *indexed* year (laptop
  profile, one indexed fact a day) would price its
  index at E-078's 72,239 B/fact ≈ 27 MB of index
  growth — arithmetic from a measured anchor, offered
  only so the toaster's index-off rule (E-080) keeps
  its reason visible. This soak measured the
  index-off year; the indexed year is NOT MEASURED.

## 3. The year-end lifecycle

One `run_lifecycle` pass at year end (decay → prune →
report), on facts honestly aged up to 365 days at the
30-day half-life:

- Decay returned **decayed 78, pruned 287,
  reinforced 0** — and the words mean what E-082
  pinned: the 287 are facts whose decayed importance
  fell below the floor and were set to importance 1,
  **not deleted rows**. The arithmetic checks: facts
  older than ~77 days at importance 6 fall below the
  floor in one pass (6 × 0.5^(77/30) ≈ 1), and 287 of
  365 daily facts were older than that.
- After the pass, `inspect_memory` still showed
  **365 current facts, 12 old versions, 7,300
  turns** — counts identical to before decay.
  Importance ranged 1 (the year's elders) to 6 (the
  freshest December facts, barely decayed). Word
  search still served the year's facts (a "ferry"
  search returned 47 current facts at a limit of 50).
  Recent turns after twelve restarts were the year's
  last turns, in order.
- The prune collected 0 entries — the toaster indexes
  nothing, so there was nothing stale to collect;
  prune-at-scale on an indexed profile remains
  E-082's fixture proof, not this soak's.

## 4. The cadence finding — docket 125

The soak's cadence probe (a separate tiny fixture,
re-run live in the battery): one fact at importance
10, aged 30 days, decayed (→ **5**, the curve's own
answer), then aged to 60 days total and decayed again
(→ **1**). Its twin, given **one** pass at 60 days,
ends at **2** (10 × 0.5² = 2.5, rounded). 

The member's decay recomputes from each fact's total
age on every pass and applies that whole factor to the
*already-decayed* importance — so passes compound.
Under the monthly lifecycle cadence E-082 describes,
a fact reaches the floor roughly twice as fast as the
stated half-life implies, and the divergence grows
with every further pass. This is not this slice's to
fix: the curve's semantics belong to the member, the
honest readings are (a) decay relative to a
last-decay/access watermark, or (b) a stated cadence
the compounding is priced into — and choosing between
them shapes what "forgetting" means for the companion.
**Docket 125 — decay passes compound (each pass
re-applies the fact's full age factor); owner: the
E-092 Part V gate**, beside dockets 112/113. The
one-pass year-end reading in §3 is unaffected: a
single pass is the curve exactly as stated.

## 5. First duty — the owed Run D

This tick first re-ran the gate Run D owed since
E-085 (extras supplied, TMPDIR on the workspace
overlay, cacheprovider off; log
`~/workspace/.verify-tmp/ember-e088/gate/runD_firstduty.log`):
**1519 passed, 1 failed, 20 skipped, 27 warnings in
565.47 s** — the closest to clean yet. The one failure
is named in the log:
`test_load_truth_e075.py::test_live_mini_run_is_correct`,
the known load-truth live-hub contention artifact
(E-083/E-085/E-086/E-087 precedent; load ~6–9 during
the run, and the same test failed standalone under
load minutes later, 1 failed / 7 passed). The E-057
size pin passed — no tree edits were in flight this
time. E-085's, E-086's, and E-087's banked code stands
verified as far as this run can say it; **a fully
clean Run D is still not on record**, so the duty
passes forward once more — it heads E-089's tick, now
covering E-088's code as well.

## 6. What this slice does not do

- No product code changed except the budget book's
  new measured anchors — the soak found no defect in
  the face or the engines to fix in scope; the one
  real finding (docket 125) is a semantics choice
  docketed to the gate that owns it, with its evidence
  pinned in the battery. (The slice's first Run B did
  catch the new anchors unpublished: E-055's rule is
  that every anchor in the code stands in the printed
  book at its value, so the eight year anchors were
  published in `docs/BUDGET_BOOK.md`'s appendix in
  scope, and the re-run gate is the one on record.)
- No indexed-profile year, no live model, no real
  device: the year is a simulation on the VM profile
  with honestly-aged timestamps, and says so.
- E-089 (canon-shaped test data) is untouched: this
  slice *used* the law early, it did not audit it.

## Tests

- `tests/unit/test_memory_soak_e088.py` — the year
  anchors pinned exactly (a quietly moving anchor is
  not an anchor); the year judged against every
  profile's twelve-month allowance and every month
  against the toaster's ceiling; the diary judgement;
  a live mini-soak (30 days × 20 turns, 30 facts, a
  supersession, a restart) re-proving counts through
  the face; year-aged decay (facts backdated ~a year:
  floored at 1, still current, still served); the
  cadence probe live (two passes end lower than one —
  docket 125's evidence, pinned as measured); and this
  doc's delivery test.

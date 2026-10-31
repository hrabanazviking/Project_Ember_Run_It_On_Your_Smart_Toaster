# E-050 — Storage growth: a month of companionship, simulated

*Part III, slice E-050. Roadmap line: "Storage growth: a
month of companionship simulated; growth within budget
or the lifecycle rules (Part V) tighten." The measured
anchors live in `ember.budgets`; the gate tests are
`tests/unit/test_storage_growth_e050.py`.*

## In plain words

**A month of daily companionship costs under half a
megabyte — the budgets hold with room to spare, and no
lifecycle rule needs to tighten.** We simulated a full
month — chatting twenty times a day for thirty days —
against Ember's real memory store and its real diary,
and weighed what was on disk afterwards: **408,566 bytes
in all (0.39 MiB)**, barely a fifth of even the smallest
("toaster") profile's 2 MiB monthly allowance. The
memory store grows in a straight line with no surprises
out to five months' worth of turns added the same day,
and it still answers at the end. A whole year at this
pace is under 5 MB. The one honest edge is *long* turns:
someone who pastes essay-length writing every turn
grows about nine times faster, and a month of that
(3.51 MiB) would pass the toaster's allowance — it fits
the phone size and up, and managing a long-turn store
over its life is exactly the job Part V's lifecycle
slice (E-082) now has the numbers for.

## 1. How the month was simulated (VM profile, 2026-10-31)

Script and raw results in `~/workspace/.verify-tmp/ember-e050/`
(`simulate_month.py`, `results.json`). Everything below
is a VM number, like every Part III anchor so far
(docket 90's discipline: storage is the least
device-shaped of the costs, but no device claim is made).

- **The Well** — the real `sqlite_vec` Brunnr at the
  production default `embedding_dim=768`. Episode rows
  carry text only (schema v1 stores no per-episode
  vector), so the dimension does not price episodes; the
  empty store weighed 81,920 B, identical to E-041's
  dim-4 shape. Episodes were added one at a time through
  `add_episode` — each its own commit under the E-031
  durability settings (WAL + `synchronous=FULL`) — in
  daily batches of 20, and the store was **closed and
  its directory weighed after every day**, so every
  figure is closed on-disk bytes, WAL checkpointed.
- **The turn fixture** — E-041/E-042's typical turn:
  operator ~40 words, reply ~40 words.
- **The reference month** — 30 days × 20 turns = **600
  episodes**, timestamps spread across the simulated
  days. Then, without a break, the same store grew to
  **3,000 episodes** (a 100-turns/day month in one store)
  for the steady-state marginal.
- **The diary** — the real `Diary`, 30 daily files, one
  session a day in chat's connected shape: the session
  start line, the memory-connected line, the two
  per-turn lines chat actually writes ("A turn was
  answered." / "The turn was saved to the memory
  store."), and the session end line.
- **Essay turns** — a separate fresh Well, 60 turns of
  ~500 words a side, for the long-turn cost.
- **Scope** — a default connected turn grows exactly
  these two stores. The pending journal is transient
  (it drains into the Well, E-031) and is not growth;
  the tool audit log and file logging grow only under
  opt-in shapes (tools on / a file destination
  configured), outside the book's per-turn price as
  E-041 §3 scoped. Ingested documents remain the
  operator's own act, bounded by the ingest caps.

## 2. The month, weighed

| Day | Episodes | Well on disk | Diary (month to date) |
|---|---|---|---|
| 0 (empty schema) | 0 | 81,920 B | — |
| 1 | 20 | 94,208 B | 1,877 B (day file) |
| 7 | 140 | 163,840 B | — |
| 14 | 280 | 245,760 B | — |
| 21 | 420 | 327,680 B | — |
| 30 | 600 | **434,176 B** | **56,310 B (30 files)** |

- **Well growth over the month: 352,256 B** — 587.1
  B/episode averaged over the month. Daily increments
  were 12,288 B on most days and 8,192 B every seventh
  day: pure 4 KiB page steps, no other shape.
- **Steady state:** episodes 600 → 3,000 grew the file
  434,176 → 1,839,104 B, a marginal **585.4 B/episode**,
  flat across the whole range (1,500 episodes: 962,560 B;
  2,100: 1,310,720 B — the same line). There is no
  superlinear component — no index or side table grows
  faster than the turns themselves.
- **Diary growth over the month: 56,310 B** — 93.85
  B/turn all-in. The marginal turn is 85 B (the two
  lines at 33 B + 52 B with their timestamps); the rest
  is one file header plus three session lines per day
  (177 B/day at one session a day; more sessions a day
  add 147 B of session lines each — stated so E-082
  prices real shapes, not this one alone).
- **The month in all: 408,566 B = 0.39 MiB = 680.9
  B/turn all-in.** After the month, the store still
  served its history: `recent_episodes` returned the
  final turns in order, the last being turn 599.
- **A year at this pace: 4.68 MiB.** A decade: ~47 MiB.
  No profile needs pruning for budget reasons at
  reference use.

## 3. Judged against the book

| Profile | Storage ceiling / month | Measured month | Fits? |
|---|---|---|---|
| toaster | 2 MiB | 0.39 MiB | yes — 5.1× headroom |
| phone | 10 MiB | 0.39 MiB | yes |
| pi | 25 MiB | 0.39 MiB | yes |
| laptop | 100 MiB | 0.39 MiB | yes |

Break-even workloads at the measured 680.9 B/turn: the
toaster's ceiling is reached only past **~103 turns a
day, every day** (phone ~513, pi ~1,283, laptop
~5,133). Even the heavy continuation's shape — a
100-turns/day month — totals ~1.92 MiB, inside the
toaster's ceiling, barely and honestly stated.

**Docket 91 — CLOSED.** E-042's re-derivation (808
B/turn) against the book's 694 is now explained at
scale: its Well figure (683 B/episode over 30 episodes)
was small-N page rounding — at 600 episodes the average
is 587.1 and the steady marginal 585.4, *under* the
book's 614 — and its diary figure (126 B/turn) came from
its own session shape (ungrounded turns write a longer
line, and session notes amortise over five turns, not
twenty). The book's constants (614 + 80 = 694 B/turn,
projecting 0.40 MiB/month) are **not revised**: the
month measured 680.9 B/turn all-in, inside the
statement, so the book was never optimistic — it stands
as a slightly conservative price, and the E-050 anchors
in `ember.budgets` record the month's own numbers
beside it.

**Ceilings move: none. Lifecycle rules tighten: no** —
the roadmap's either/or resolves on the evidence to
*within budget*. What E-082 (memory lifecycle) inherits
from this slice, quantified:

1. At reference use there is nothing to prune for
   budget reasons for *years* on any profile; lifecycle
   rules written for urgency would be theatre.
2. The real lifecycle subject is the **long-turn
   store**: essay turns cost **6,144 B/episode**
   (measured at N=60, page steps included); a
   reference-rate month of them is **3.51 MiB — past the
   toaster's 2 MiB ceiling**, inside the phone's 10
   MiB. On the toaster, essay-length companionship
   breaks the storage budget past ~11 such turns a
   day. Retention/pruning/compaction for long turns is
   E-082's to design, with these prices.
3. The diary's shape is one file per day forever:
   trivial bytes (56 KB/month) but 365 files a year —
   a file-count, not a byte, consideration for E-082.

## 4. Honest limits

- **VM numbers.** Filesystem and page behaviour are
  SQLite's, which travels; the curve was not re-run on
  the Pi. Storage was the one Part III cost E-047–E-049
  did not re-anchor on device (their config roots grew
  only a few turns each); a device month is E-088's
  year-soak territory, not claimed here.
- **Fixture words.** The typical turn is ~80 words in
  all; real companionship varies, and §3 prices the
  essay end of that variation rather than hiding it.
  Pasted documents are ingest, not growth (§1 scope).
- **One session a day** shapes the diary's session-line
  overhead; the per-session price is stated in §2 so
  other shapes can be priced honestly.
- **The essay figure is N=60** — page steps are a
  larger share at that scale; it is recorded as
  measured, and the verdict it carries (past the
  toaster, inside the phone) holds under any plausible
  steady-state refinement, since even the pure text of
  an essay turn is ~5.5 KB.

## Tests

- `tests/unit/test_storage_growth_e050.py` — **7
  passed** (default env): the month's anchors pinned at
  their measured values; the measured month fitting
  every profile's storage ceiling (a fifth of the
  toaster's); the book's 694 B/turn standing unrevised
  over the measured 680.9 (docket 91's verdict as a
  test); the toaster break-even past 100 turns/day; a
  year under 5 MiB; the essay month pinned in both
  directions (past the toaster, inside the phone); and
  the gate-wiring test.

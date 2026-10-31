# E-055 — The budget book published in-repo with its measurements

*Part III, slice E-055. Roadmap line: "The budget book
published in-repo with its measurements." The published
book is `docs/BUDGET_BOOK.md`; the book in code remains
`ember.budgets`; the pinning tests are
`tests/unit/test_budget_book_e055.py`.*

## In plain words

**The budget book is now one document a person can
read.** Until now the book existed as code
(`ember.budgets`, E-041) plus a trail of slice records —
every measurement real, but scattered across fourteen
documents, each with its own method section. A reader
who wanted to know "what does Ember cost, and how do we
know?" had to reconstruct the answer from the campaign's
diary.

`docs/BUDGET_BOOK.md` is that answer, in one place, in
plain words first: the four profiles' ceilings, the
founding measurements, how the install got ~41× lighter
and the dependency diet that caught a real break, the
behaviour measurements (the idle hour, cold start,
update weight, a month of storage, battery duty,
thermal patience, the shedding ladder), and the three
device proofs with their grades kept attached — the Pi
proof REAL, the phone proof SIMULATED, the Toaster Test
REAL with its verdict in two halves (the name cashed
for the core; a whole companion on a literal 512 MiB
host NOT CASHED, by measured arithmetic). What the
numbers exclude (the model, Python's install, the
members — whose own table is E-057) and what remains
NOT PROVEN (a real phone, a real battery's drain, Pi
thermals) are stated in the book itself, in §6, before
anyone quotes a number from it.

## 1. What existed before (audited this slice)

- `ember.budgets` carried 27 `MEASURED_*` anchors at
  this slice's opening (E-041's founding three, the
  cold-start anchor, four Pi anchors, three phone-SIM
  anchors, four toaster anchors, six month anchors,
  three update anchors, three battery anchors) — each
  provenanced to its slice in the module's comments,
  none gathered in one reader-facing place.
- The ceiling table existed in exactly one prose home:
  the E-041 slice record, an architecture document
  written for the campaign, not for a reader of the
  project.
- Nothing checked any prose statement of the book
  against the code. E-041's and each later slice's tests
  pin the *code* anchors; a published summary written
  by hand could drift from them silently. That drift
  surface is what this slice closes.

## 2. The published book's shape

`docs/BUDGET_BOOK.md`, seven parts:

1. **Plain words first** — the whole story in one
   section a non-technical reader can finish.
2. **The ceilings** — the four profiles' table exactly
   as the code states it, the flat 5.0 s cold-start cap
   with its reason, and the per-profile history
   allowances read from the conversation config.
3. **The founding measurements** (E-041, VM) — install
   978,843 B, idle 40.7 MiB, turn 40.1 MiB, storage
   694 B/turn; the struck "~50 MB installed" claim and
   the generous-but-true "~50 MB RAM" claim, both with
   their verdicts.
4. **How the core got lighter** (E-043/E-044) — the
   sdist cut (127,162,419 → 3,464,529 B unpacked) and
   the dependency diet (dev extra 89,112,145 →
   7,600,880 B for the test-only set; all extras
   53,703,943 B), including the broken-extra catch.
5. **The behaviour measurements** (E-045–E-054) — one
   table, one row per slice, each row naming its record.
6. **The device proofs** (E-047/E-048/E-049) — per
   device, per grade, with the Toaster verdict's two
   halves unsoftened.
7. **Exclusions, NOT PROVEN lines, and the appendix** —
   every `MEASURED_*` anchor by its code name and value,
   so the measurements are citable from the book itself.

No number appears in the published book that does not
appear in a prior slice record or in `ember.budgets`;
this slice took no new measurements and moved no
ceiling. Docket 90 stands closed at its grades (settled
E-049); no new docket items.

## 3. The drift armour

`tests/unit/test_budget_book_e055.py` — **8 tests**,
all reading the published document against the *live*
code (no second copy of any number in the test file):

- the book exists and names its code home;
- the ceiling table's every cell (host, install, idle,
  turn, storage, cold start) equals `all_budgets()`'
  live values, per profile;
- the history allowances in print equal the
  config-derived budgets the book object computes;
- **every** `MEASURED_*` name in `ember.budgets`
  appears in the book at exactly its coded value
  (integers in the book's comma format, floats in their
  plain spelling) — an anchor added to the code but not
  published fails the gate, as does a revalued one;
- the storage arithmetic in print (614 + 80 = 694
  B/turn at 20 turns/day) equals the code's functions;
- the honesty lines are present in print: the model
  exclusion, SIMULATED and NOT PROVEN grades, the
  "not cashed" verdict, and the pointer to E-057 for
  the member table;
- the ceiling table holds exactly the four profiles —
  no member row invented ahead of E-057.

Two defects in the slice's own first draft were caught
by these tests and fixed before banking: the book's
history line abbreviated the phone/pi/laptop allowances
("1,024 / 5") where the test rightly demanded the full
spelled shape, and the test's cold-start format was
corrected to the book's print format ("5.0 s"). Both
were presentation-shape, no measurement moved.

## 4. Gate

- New tests standalone (default env): **8 passed**.
- Slice gate Run B (default env, pgvector file
  excluded): **1040 passed, 6 failed, 25 skipped,
  1 warning** — 1032 E-054 baseline + 8 new; the 6 are
  the proven environment failures, identical set.
- Slice gate Run D (whole, extras): **1097 passed,
  0 failed, 19 skipped, 1 warning**, exit 0 —
  1089 + 8 new, reconciles exactly. (Logs in
  `~/workspace/.verify-tmp/ember-e055/gate/`.)
- No README touched. No code in `src/` changed — this
  slice publishes and pins; it does not rebuild.
- E-056 next — regression armour: the budget tests join
  the permanent gate as one command.

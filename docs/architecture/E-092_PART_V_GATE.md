# E-092 — Part V Gate: One Memory Face Live; the Verdict on Record

*Project Ember campaign, Part V (Memory: Two Systems, One
Verdict) — GATE. Filed 2026-11-01 on branch
`yrsa/ember-road-build` in the campaign's own clone
(`~/workspace/ember-build`), at campaign commit 0426ea0
(E-091 banked + its push record + this slice's
IN PROGRESS marker). This gate closes Part V on the
roadmap's own criteria for E-092: "one memory face
live; migration proven; the verdict paper + Volmarr's
word (where required) on record." Like the Part IV
gate before it, this slice also lands the repairs the
gate review itself owned: docket 108 is closed in
scope, and docket 125's decay semantics are ruled in
§6. No README was touched. Gate re-measurements were
run this slice; raw logs live in
`~/workspace/.verify-tmp/ember-e092/gate/`.*

## The gate, in plain words — read this first

**Part V is done. The companion now remembers through
exactly one face, and the question Part V was opened
to answer — two memory systems under one roof, plus
the incumbent store the companion already used — is
answered on measurements, not taste.** The face is
`MemoryFace` (E-080): living facts live in mimir-well,
documents and conversation turns live in Brunnr, and
meaning search over facts works by *index, don't
merge* — a fact that has been replaced is never served
in its old shape. Around that face the part built, in
order: the lifecycle (E-082), persona separation with
five real gaps found and fixed (E-083), the user's
four rights as working operations (E-084), the lawful
crossing from the session diary (E-085), the
WYRD-shaped export (E-086), corruption and recovery
drills that found and fixed three real bugs (E-087),
a simulated year of memory that fits the smallest
machine's budget four times over (E-088), proof that
no test in the tree remembers anything real (E-089),
the memory model written for users and builders
(E-090), and the verdict's residue marked truthfully
in the project's living documents (E-091).

**The verdict, and the word.** E-079's verdict paper
stands as Part V argued it: **bound** — one face over
two bounded house engines — with mempalace's honourable
retirement **proposed, not decided**. That decision is
Volmarr's word, and **no ruling is on record** at this
gate: not in the campaign state, not in any slice
record, not in the verdict paper's own filings since.
Silence is never read as a retirement word (E-079 §6),
so the gate records the absence itself as the fact on
record, with the E-079 fallback in force: mempalace
stays in the tree, untouched, as an optional,
non-default, never-bundled laptop-class guest, excluded
from the companion's memory. If a ruling ever arrives,
the executing work is a later, separately-banked slice
under that ruling (§5).

**Migration is proven — on fixtures, which is the
proof the roadmap asked for.** The survivors need no
migration at all, and E-081 proved it: stores written
the pre-face way are served whole by the face with
schemas byte-identical and every content row unchanged.
For a palace, E-081's fixture proof shows every drawer
and knowledge-graph triple carries losslessly into the
bounded shape, with closets and embeddings rebuilt at
the destination as the derived layers they are. The
migration *tool* is not built and no real palace was
opened: executing it is ruling-gated, exactly as the
verdict ordered (§4).

**This gate's own two acts.** Docket 108 is **closed**:
mimir-well's dependency declarations — flask, and its
build-time setuptools — are now bounded above as well
as below, like every other member's the campaign has
touched (E-044's law), pinned by this slice's battery.
And docket 125 is **ruled**: the forgetting curve's
semantics are the watermark semantics (§6) — a decay
pass may apply only the age accrued since the last
pass or access, and passes never compound. The member's
current code compounds; that now stands as a named
defect against a ruled law, with its implementation
assigned, not as an ambiguity the next worker must
re-decide.

Honesty, kept plain: **chat is not yet rewired to the
face** — the contract is live and proven, and the chat
loop still opens Brunnr directly, as E-080 §7 and
E-090 §B1 state; the wiring belongs to the slices that
touch those paths. The bounded shape's speed and weight
on a **real** tiny-hardware device are **NOT PROVEN** —
every Part V number is a campaign-VM measurement, and
device proof is later parts' work, as E-079 §7 said.
An indexed-profile year is **NOT MEASURED** (E-088
measured the toaster's index-off year; the indexed
year is arithmetic from a measured anchor, stated as
such).

## 1. Gate criteria — each one checked, not assumed

| # | Criterion (roadmap E-092) | Evidence | Result |
|---|---|---|---|
| G1 | Every Part V slice E-077–E-091 banked | CAMPAIGN_STATE slice ledger, E-077–E-091 all DONE; all 16 per-slice documents E-077–E-092 present under `docs/architecture/` (pinned by this slice's battery) | PASS |
| G2 | One memory face live | §3: `MemoryFace` openable and proven across E-080–E-088's batteries; the combined Part V conformance re-run at this gate (§7) green; contract frozen at v1 (§3) | PASS — as a contract; chat rewiring is follow-on work, stated at §3 |
| G3 | Migration proven | §4: E-081's two proofs (survivors stay native, measured; palace mapping lossless on fixtures) stand, re-run inside this gate's combined conformance | PASS — on fixtures, as the roadmap line orders; execution ruling-gated |
| G4 | The verdict paper + Volmarr's word (where required) on record | §5: the verdict (E-079) and its residue (E-091) on record; the retirement word's recorded absence on record at this gate, fallback in force | PASS — as a record; the ruling itself remains Volmarr's to give |
| G5 | Part V's docket accounted for — nothing found, nothing lost | §6: items 51, 52, 100, 102, 104 and 108–126 each closed, fixed or ruled here, or carried with a named owner (cross-checked against E-077–E-091 by an independent read this slice) | PASS — as an accounting; the carried items remain open at their named homes |
| G6 | Full suite green before banking | §7: gate re-measurement (Run A / Run B / Run D + combined Part V conformance) recorded there | PASS — on the evidence stated in §7 |
| G7 | Summary filed; the road below checked | The section above ("The gate, in plain words"), §8, and §9: no re-cut demanded; Part VI inherits its named items | PASS |

## 2. Part V slice by slice — final dispositions

| Slice | What it built or proved | Disposition at this gate |
|---|---|---|
| E-077 | Both member systems (and Brunnr) mapped: storage, retrieval, consumers, test state | Stands as Part V's map; its docket 108 hygiene line is closed at this gate (§6) |
| E-078 | The comparison harness: identical workloads through all three systems | Stands as the verdict's evidence base; its numbers are §5's ground |
| E-079 | The verdict paper: bound, one face, retirement proposed | **On record** (§5); the proposal awaits its ruling |
| E-080 | The one memory contract implemented (`MemoryFace`); index-don't-merge proven; docket 51 settled for the companion; docket 110's guarantee built | Live; frozen at v1 at this gate (§3) |
| E-081 | Migration answered: survivors stay native (proven); palace mapping lossless on fixtures (proven) | Proven (§4); the executing tool is ruling-gated |
| E-082 | Lifecycle on the face: growth accounting, decay delegation, stale-index pruning | Live; its two honesty dockets (112, 113) carried at §6 |
| E-083 | Persona separation enforced at the face; five gaps (dockets 114–118) found and fixed in scope | Closed; the wall is the face's standing law |
| E-084 | The user's memory rights as working operations; dockets 119 + 120 stated | Live; docket 119 shares docket 112's root and owner (§6) |
| E-085 | Memory ↔ Verdandi reconciled: two views, one guarded crossing; docket 104 closed | Closed; docket 102's assigned review did not happen here — it is taken at this gate (§6) |
| E-086 | WYRD-shaped export on the face; a real total-delete bug found by its gate duty and fixed in scope | Closed; TF-145's boundary honoured in the bundle itself |
| E-087 | Corruption & recovery drills; three bugs fixed in scope (dockets 121, 122, 124); docket 123's boundary pinned | Closed; docket 123 weighed at this gate (§6) |
| E-088 | The simulated year: 5,717,556 B total, inside every profile's year allowance; docket 125 found | Closed as measured; docket 125 ruled at this gate (§6) |
| E-089 | Canon-shaped test data only: the audit, the one real-name shape fixed, the guard armed; docket 126 (the socket-path instrument defect) found, fixed, and the clean-Run-D duty closed | Closed; the guard gains this gate's battery as its fourteenth allowlisted file, consciously, in this slice |
| E-090 | The memory model documented for users (plain) + builders, pinned against the code (31 operations) | Stands as the model's living document |
| E-091 | The verdict's residue: mempalace marked bounded in Ember's living documents; docket 52 executed | Stands; confirmed as this gate's "docs marked truthfully" line (§5) |
| E-092 | This gate | Closes Part V |

## 3. One memory face, live — and frozen

**The memory contract v1 is FROZEN at this gate.**
The contract is `MemoryFace` in
`src/ember/well/memory_face.py`, as documented whole
in E-090 §B3 (31 public operations in six groups) and
pinned there against the class itself. Frozen means:

- The operation surface, the result shapes
  (`FactResult`, `MeaningHits`, `LifecycleReport`),
  the canonical mimir-well path (docket 51's
  settlement), the per-profile index defaults, and
  the stated-mode honesty of meaning search do not
  change under v1. Any breaking change is a
  **version bump** to v2, made as its own slice with
  its own conformance — never an edit under the v1
  name.
- Adding an operation is not a bump: it is documented
  in E-090's surface in the same change that adds it,
  and E-090's battery — which derives the operation
  list from the class — fails if it is not. That rule
  is part of the freeze.
- The face speaks to mimir-well only through
  `RunaMemory` and to Brunnr only through its handle.
  No future core code invents a path or a raw-SQL
  consumer: it opens the face (docket 109's reckoning,
  §6).

Live, stated exactly: the face opens
(`MemoryFace.open`), degrades honestly when a half is
unavailable, and every Part V battery from E-080 to
E-088 exercises it end to end; the combined conformance
at this gate (§7) re-runs that whole proof. What
"live" does **not** yet mean is also stated exactly:
no code in `src/ember/` outside `well/memory_face.py`
references the face, and the chat loop still opens
Brunnr directly. Wiring chat through the face is
follow-on work for the slices that touch those paths;
this gate does not smuggle it in, and E-204 must
present it as a named gap if it is still unbuilt
there.

## 4. Migration, proven

Two proofs, both E-081's, both re-run inside this
gate's combined conformance (§7):

1. **The survivors stay native.** Stores written the
   pre-face way — facts (including a supersession)
   through `RunaMemory` directly, a document, a chunk
   and an episode through the Brunnr handle directly —
   are served whole through the face, after which both
   stores' schemas are byte-identical to their
   pre-face snapshot and every content table's row
   count is identical. (The only deltas are mimir-well's
   own read-audit rows and its FTS shadow compaction —
   the member behaving as designed, named in E-081 §2.)
   There is nothing to migrate because the face speaks
   both native shapes; that is measured, not hoped.
2. **A palace migrates losslessly — on fixtures.**
   Drawers carry as Brunnr chunks with every metadata
   field reconstructable exactly from the destination
   document (round-tripped through a real Brunnr store
   via the face); knowledge-graph triples carry as
   living-fact records field-for-field; closets and
   stored embeddings are derived layers, rebuilt at
   the destination, never carried. The reader the proof
   stands on is the member's own stdlib-only extractor
   — a palace can be *read* without the disqualified
   ~185 MB stack, which is what makes a one-time
   migration cheap and read-compat-forever indefensible
   as the standing answer (E-081 §5–§6).

Not claimed: no migration has run on any real store;
no real palace was opened; the fixture palace holds
3 drawers, 1 closet, 2 triples, and archive-scale
behaviour (10⁴–10⁵ drawers) is the executing slice's
verification duty. The executing slice exists only
under Volmarr's retirement ruling (§5); under the
fallback, the same mapping is available as a user's
own one-way export, never automatic, never silent.
Migration copies; it never deletes.

## 5. The verdict paper, and the word — on record

- **The verdict paper**: E-079, *bound* — Brunnr keeps
  documents, chunks and turns; mimir-well keeps living
  facts, the lifecycle, the guard and the audit; the
  face owns meaning search over facts and the user's
  rights. The three single-system crowns were each
  argued and refused on E-078's measurements (E-079 §4).
- **The proposal**: mempalace's honourable retirement
  from Ember (E-079 §6), with its fallback if declined
  (bounded: optional, non-default, never-bundled,
  laptop-class only, true costs stated wherever
  offered).
- **The word**: retirement is Volmarr's word. At this
  gate, **no ruling is on record** — the campaign
  state, the slice records E-080–E-091, and the main
  session's filings carry no ruling, and this gate
  does not manufacture one from the campaign's own
  momentum. The absence is itself the record G4 asked
  for: *the verdict paper + Volmarr's word (where
  required) on record* reads, honestly, as *the paper
  on record; the word not yet given; the fallback in
  force*.
- **The residue stands** (E-091, confirmed at this
  gate as the "docs marked truthfully" line): the
  corrected UNWIRED_INVENTORY row (docket 52,
  executed), the sibling document's SUPERSEDED-IN-PART,
  BOUNDED banner, and the corpus front doors' status
  notes — the successor named in each (`MemoryFace`,
  E-080). The member itself stands present and
  unmodified, pinned by this slice's battery at
  257 tracked files / 59,049,715 B.

## 6. Part V's docket — closed, fixed or ruled here, carried

Closed during Part V (each at its slice, verified from
the state ledger): docket 51 (three mimir-well paths →
the face's one canonical default, E-080); docket 52
(the stale UNWIRED mempalace characterisation →
corrected at E-091); docket 104 (logger deletions reach
already-fed memory — explicit audit + retraction,
E-085); docket 110 (episode persona separation owned
by the face above the adapter, E-080, batteried at
E-083); docket 111 (mimir-well's FTS5 tables had no
sync triggers, so word search was blind to in-session
writes — fixed in scope at E-078, the fix behind the
harness's three-way verbatim tie); docket 114,
docket 115, docket 116, docket 117
and docket 118 (the five persona-wall gaps, all fixed
in scope at E-083); docket 120 (the member's audit
keeps content-free hashes only after a deletion — a
stated truth, closed as documentation, E-084/E-090);
docket 121, docket 122 and docket 124 (the three drill
bugs — supersede atomicity, the face's index-record
honesty, the restore road — fixed in scope at E-087);
docket 126 (the load-truth socket-path defect that had
masqueraded as a contention artifact since E-083 —
fixed in the instrument at E-089, regression-pinned).

Fixed at this gate, in scope:

- **Docket 108 — CLOSED.** mimir-well declared
  `flask>=3.0` with no upper bound — the exact shape
  E-044 proved broken at the root (an unbounded floor
  resolves a future breaking major silently) — and its
  build-time `setuptools>=61.0` carried the same shape.
  Both are now bounded both ways (`flask>=3.0,<4`,
  `setuptools>=61.0,<82`), pinned by this slice's
  battery, which fails if any requirement mimir-well
  declares loses either bound. In-scope re-measure
  (the E-057 precedent): mimir-well now reads 59 files
  / 618,776 B (+7 B), the twelve-member total
  131,545,913 bytes, the laptop miss unchanged at
  256,017 bytes — both published copies updated, and
  E-077's member-size pin re-pinned to 618,776 with
  its attribution recorded in that battery, as
  E-078/E-087 did for their own member changes. (The
  combined conformance's first run at this gate caught
  exactly that stale pin — 225 passed, 1 failed — and
  the re-run after the re-pin is the one §7 records.)

Ruled at this gate, in scope — the two semantics
questions Part V assigned here:

- **Docket 125 — RULED: the watermark semantics.**
  The law: *importance is a function of a fact's age
  since its last access, applied once.* A decay pass
  computes each fact's target from its age since the
  later of (its last access, the last pass that
  decayed it) — passes never compound, and two passes
  over unchanged facts with no time between them
  change nothing. The member's current code
  (`_decay_inner`) recomputes from total age on every
  pass and applies that whole factor to the
  already-decayed importance, so under a monthly
  cadence facts floor roughly twice as fast as the
  stated 30-day half-life (E-088 §4's probe: importance
  10 aged 60 days ends at 1 under two passes, 2 under
  one). That behaviour now stands as a **defect against
  this ruled law**, not an open question. Until the
  implementation lands, no document may quote the
  half-life as the cadence behaviour: E-090 §A6 already
  states the compounding plainly, and the face's
  lifecycle reports inherit that honesty. The
  implementation — a per-fact decay watermark in the
  member, with the E-088 cadence probe as its
  regression fixture (two passes ≡ one pass at the
  same total age, within the member's rounding) — is
  assigned to **E-204's presentation**: the gate after
  next does not exist in Part V's road, the change is
  member-semantics surgery that deserves Volmarr's
  sight, and E-204 must present it as a named candidate
  slice (with docket 112's handle delete, below) for
  his word at the E-203 push review.
- **Docket 123 — WEIGHED and bounded.** The drills
  pinned that `add_turn`'s episode write and its
  persona-tag save are not one transaction: a process
  death between them leaves one turn untagged, served
  on reopen to the face's default persona only — never
  to a named other persona, never off the machine.
  This gate accepts that as the v1 boundary: the
  blast radius is one turn filed in the wrong drawer
  of the same house, every persona here is one
  person's own, and the in-process half already fails
  loudly. Making the pair crash-atomic is a design
  change (a write-ahead tag journal, or tags inside
  Brunnr), re-weighed at **E-204** alongside the chat
  rewiring (§3), which is the work that would change
  its shape.

Carried forward, open, with a named owner each — this
gate closes Part V on its stated criteria; it does
**not** claim these are fixed:

- **Docket 100** (Bifröst's size pruning of the
  conversation log is not session-aware) — unchanged
  by Part V; E-085's retraction road restated the
  standing verdict (pruning is hygiene, never a
  privacy mechanism). Owner: **E-136** (Part VIII gate).
- **Docket 102** (no typed nerve subscriber; chat does
  not consume nerves) — E-076 assigned its first review
  to E-085, but no Part V slice took it up: no Part V
  document mentions it (verified by this gate's
  cross-check of E-077–E-091). Reviewed here instead:
  Part V's real nerve consumer turned out to be the
  face's logger crossing, which is pull-shaped
  (candidates offered to the face), not a typed
  subscription; a typed subscriber remains unbuilt.
  Backstop owner stands: **E-204**, which must present
  it to Volmarr as a named gap if still unbuilt.
- **Docket 109** (the four raw-SQL mimir-well
  consumers) — reckoned with at E-080 §6: the face is
  not a fifth; none of the four was re-pointed.
  Bifrost's two are **Part VIII's** call (its gate,
  E-136); the Eye is the member's own program;
  Verdandi's check already follows the canonical path.
- **Docket 112** (Brunnr's handle has no delete:
  stale index chunks are unreachable after pruning but
  their bytes are never reclaimed) — owner: **E-204's
  presentation**, as a named candidate slice beside
  docket 125's implementation (§6 above); the face's
  prune reports already state `physical_bytes_reclaimed:
  0` wherever it applies.
- **Docket 113** (the member decay vocabulary:
  `pruned` names importance-flooring, not deletion) —
  **closed at the face's layer**: every face report
  and both E-090 halves state the true meaning, and
  no Ember surface repeats the word unglossed. The
  member's own vocabulary is carried to **E-194**
  (builders' docs reconciled), which owns member-facing
  naming honesty at the release.
- **Docket 119** (a forgotten turn's bytes are not
  physically reclaimed — the tombstone half of the
  user's delete right) — shares docket 112's root
  (no handle-level episode delete) and its owner:
  **E-204's presentation**, same candidate slice.
  Until then the right is honoured as E-084 built it:
  a forgotten turn is unreachable forever, and every
  delete report states the bytes figure as 0.

## 7. Gate re-measurement (E-017 method, part-gate shapes)

Measured this slice at HEAD 0426ea0 plus this slice's
changes (unbanked at measurement time, banked by this
slice's commit), VM profile (Python 3.12.3, pytest
9.1.1), TMPDIR on the workspace overlay; raw logs in
`~/workspace/.verify-tmp/ember-e092/gate/` (`runA.log`,
`runB.log`, `runD.log`, `combined-extras.log`,
`combined-extras2.log`).

| Run | Shape | Gate result |
|---|---|---|
| A | Whole suite, default env | Interrupted at collection — **1 error, 20 skipped**, exit 2 (docket 1, unchanged since the E-017 freeze) |
| B | Default env, pgvector file excluded (the slice gate) | **1352 passed, 6 failed, 34 skipped, 1 warning** — E-091's 1344 + this slice's 8; the 6 are the proven environment failures, FAILED list identical |
| D | Whole suite, extras supplied from the isolated dir | **1560 passed, 0 failed, 20 skipped, 27 warnings**, exit 0 — E-091's 1552 + 8, fully clean |

Part V's own sets, same slice:

- **Combined Part V conformance** (E-057 table + E-072
  feed + E-077–E-092 batteries, 18 files, extras
  shape): **226 passed, 1 skipped**, exit 0 — the skip
  is the live-WYRD validation, as E-086–E-091. Its
  first run scored 225 passed / 1 failed, the one
  failure being E-077's member-size pin gone stale
  under this slice's own docket-108 change; the pin
  was re-pinned in scope (§6) and the re-run above is
  the gate's record.
- **Focal sets**: this slice's battery **8 passed**;
  battery + E-089 canon guard **16 passed**; after the
  re-pin, the affected focal set (E-057 + E-077 +
  E-089 + E-092) **31 passed**.
- **The live face, probed directly**: `MemoryFace`
  loads from `src/` and carries exactly **31 public
  operations** — name-for-name the surface E-090
  documented (independently cross-checked this slice).

Two method notes, recorded not hidden: this tick's
first Run B attempt was cut at ~10% by a service
restart and re-run whole — the table's Run B is the
re-run; and the whole gate ran under heavy
sibling-campaign contention (the combined re-run took
~7 minutes, Run D ~13.5), which moved wall times only —
no count in this section is a wall time, and the
load-truth class that contention once poisoned has
been closed since E-089 (docket 126).

The E-057 member budget table was re-measured for
this slice's mimir-well change (§6): mimir-well
**59 files / 618,776 B**; total **131,545,913 B**;
laptop miss unchanged **256,017 B** — both published
copies updated, as their pinning tests require (they
are inside the combined run above).

## 8. Plain-language summary (for the campaign record)

Part V asked: *two memory systems under one roof —
unify them, bound them, or retire one?* Sixteen slices
answered it with measurements. Both systems were
mapped (E-077) and run through one harness on
identical work (E-078): verbatim recall a three-way
tie, meaning belonging to Brunnr and mempalace, the
living questions — what matters, how it felt, what is
true *now* — belonging to mimir-well alone, and
mempalace fitting no tiny-hardware budget by an order
of magnitude. The verdict (E-079) bounded the two
house systems behind one face and proposed the third's
honourable retirement to Volmarr. The face was built
(E-080) with its meaning bridge priced per profile —
off on the toaster, honestly labelled — and migration
was answered (E-081): the survivors never move, and a
palace, if its day comes, moves losslessly. Then the
face grew its lifecycle (E-082), its persona wall
(E-083), the user's rights (E-084), its lawful crossing
from the diary (E-085) and its WYRD-shaped export
(E-086); drills broke it three real ways and the fixes
landed in the same slice (E-087); a simulated year
weighed the whole of memory at 5.45 MiB against the
toaster's 24 MiB year (E-088); the test tree was proven
to remember nothing real (E-089); the model was written
down for the people who will use and build it (E-090);
and the losing system's docs were marked with the
truth (E-091). This gate froze the contract, closed
the last hygiene docket, ruled the forgetting curve's
semantics, and put the verdict — and the word it still
awaits — on record. What Part V did not do is wire
chat to the face, prove memory on a real small device,
or retire anything: each is named, owned, and carried
in §3, §6 and §9, not buried.

## 9. The road below — checked

Part VI (E-093–E-106, Kista of the Toaster) follows in
roadmap order; nothing in Part V's evidence demands a
re-cut. Part VI opens with E-093, the custody law for
the whole campaign — credentials live in a Kista,
never in configs, code, or chat — and Part V hands it
a working example of the standard: the face's canonical
path discipline (docket 51) and the E-013 census's
shape defects land there first, as the roadmap ordered.
Later owners named at this gate: E-136 (docket 100,
docket 109's bifrost side), E-194 (docket 113's member
vocabulary), E-203/E-204 (the retirement ruling's
executing slice if the word arrives; docket 102's
backstop; docket 112 + docket 119's candidate slice;
docket 123's re-weigh; docket 125's implementation
candidate; the chat-rewiring gap; the v1.0.0 nerve-hub
judgement E-076 defined). The roadmap file was not
edited by this gate.

## Carried forward

- Part V is CLOSED by this gate. Next: E-093
  (Part VI) — custody law for the whole campaign.
- The mempalace retirement: proposed (E-079 §6),
  awaiting Volmarr's word; fallback in force; the
  executing migration slice exists only under that
  ruling.
- Open and carried, not lost: docket 100 (→ E-136),
  docket 102 (→ E-204 backstop), docket 109's bifrost
  side (→ Part VIII), docket 112 + docket 119
  (→ E-204 presentation, one candidate slice),
  docket 113's member half (→ E-194), docket 123
  (→ E-204 re-weigh), docket 125's implementation
  (→ E-204 presentation, candidate slice beside
  docket 112's).
- NOT PROVEN at this gate: the bounded shape on real
  tiny hardware; an indexed-profile year; chat wired
  through the face — each with its owning slice or
  presentation named above.

*Filed by the E-092 slice, 2026-11-01. Part V gate:
PASS. Next: E-093 — custody law for the whole campaign
(Part VI opens).*

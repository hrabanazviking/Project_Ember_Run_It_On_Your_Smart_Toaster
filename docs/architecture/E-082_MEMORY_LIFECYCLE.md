# E-082 — Memory lifecycle: growth, decay, pruning

*Part V, slice E-082. Roadmap line: "Memory lifecycle:
growth, decay, pruning under Part III's storage budget
(E-050 consumed)." The lifecycle lives on the one memory
face (`src/ember/well/memory_face.py`); the conformance
tests are `tests/unit/test_memory_lifecycle_e082.py`.*

## In plain words

**Memory now has a lifecycle, run through the one face —
and the honest headline is that there is no emergency to
manage.** Part III measured a month of daily
companionship at 0.39 MiB, inside even the toaster's
2 MiB monthly allowance with years of headroom (E-050).
So this slice builds accounting and hygiene, not
desperate pruning: the face can say what memory costs
today against its profile's budget, run the memory
engine's own forgetting curve, and clear away index
pointers for facts that have been replaced or removed.
Two limits are stated plainly rather than papered over:
the forgetting curve lowers a fact's importance but
never deletes the fact itself, and clearing an index
pointer makes a stale entry unreachable without yet
reclaiming its bytes in the document store — that
reclamation needs a delete operation the store's handle
does not offer yet (docket 112, below).

## 1. Growth — the accounting (E-050 consumed)

`MemoryFace.lifecycle_report()` prices the live stores
from measured anchors only:

| Quantity | Price | Anchor |
|---|---|---|
| one living fact | 745 B | E-078 harness |
| one conversation turn | 585 B | E-050 steady marginal (585.4 B) / E-078 |
| one indexed fact | 72,239 B | E-078 embedded-chunk growth |

The report carries: the profile and its monthly ceiling
(from `ember.budgets`), the facts stored, their priced
bytes, the indexed-fact count and its priced bytes,
Brunnr's own on-disk size, whether the index held today
fits the profile's monthly ceiling, and the ceiling
expressed in indexed facts (the toaster's 2 MiB ceiling
is ~29 indexed facts — exactly the E-080 pricing that
keeps the toaster on word search; the laptop's 100 MiB
is ~1,452). E-050's verdict stands unchanged: at
reference use nothing needs pruning for budget reasons
for years on any profile; the index is the only growth
that can break a small profile, and it is already
bounded per profile by E-080's rule.

Episodes are not pruned by this slice: turns are the
companion's history, E-050 priced a year of them under
5 MiB, and deleting history is the user's right
(E-084's operations), not a budget reflex.

## 2. Decay — delegated to the engine that owns it

`MemoryFace.run_decay()` calls mimir-well's own
`RunaMemory.decay()` for the asking persona only —
Ebbinghaus forgetting (30-day half-life by default),
importance lowered with time since last access,
recently accessed facts reinforced. The face
reimplements nothing.

**Read honestly:** the member's returned `pruned`
count does not mean rows were deleted. Its code (read
this slice, `mimir-well/src/mimir_well/core.py`,
`_decay_inner`) floors decayed importance at 1 and
counts a fact as "pruned" when its decayed importance
falls below the floor argument; the row stays, at
importance 1. Actual fact deletion exists only as the
member's explicit `delete_memory()` — a user-rights
operation (E-084), never a lifecycle side effect. No
report from this face will ever claim deletions that
did not happen. This naming gap is docket 113.

## 3. Pruning — the stale index

`MemoryFace.prune_stale_index()` walks the face's
fact-index sidecar and drops every pointer whose fact
no longer resolves as current for its recorded persona
(superseded, deleted, or vanished). Effects, stated
exactly:

- the stale chunk can never be served (resolution
  already refused it; now it is not even a candidate);
- the index accounting shrinks by 72,239 B per dropped
  pointer — the growth the face reports is the growth
  that can still be reached;
- **physical Brunnr bytes reclaimed: 0.** Brunnr's
  handle (`BrunnrHandle`) offers add/search/count and
  no delete for chunks, documents, or episodes, so the
  stale chunk's bytes stay in the store file until a
  handle-level delete exists. That gap is **docket
  112** (owner: Part V residue / E-092 gate to assign;
  the face's pruning is complete at the contract level
  and incomplete at the byte level, and says so in
  every prune report's `note`).

`MemoryFace.run_lifecycle()` composes one pass in
order — decay, then index pruning, then the growth
report — so the report prices the store as the pass
left it.

## 4. What this slice does not do

- No episode/document deletion (E-084 owns the user's
  delete-total right; budgets do not justify one).
- No diary lifecycle: E-050 priced the diary at
  56 KB/month and 365 files a year — a file-count
  observation, left to E-088's year soak to judge.
- Chat is not rewired to call the lifecycle on a
  schedule; the operations are live on the face and
  proven, and any cadence (session-end, like the
  member's own consolidate shape) is a wiring choice
  for the slices that wire the face into chat (E-085
  first among them).

## 5. New docket items

- **112** — Brunnr's handle has no delete (chunks,
  documents, episodes): stale fact-index chunks are
  unreachable after E-082 pruning but their bytes are
  never reclaimed. Owner: E-092 gate to assign.
- **113** — mimir-well `decay()`'s `pruned` count
  names importance-flooring, not deletion; the word
  invites false lifecycle claims. Owner: Part V
  residue (doc/naming honesty at the member or the
  face's reporting layer).

## Tests

- `tests/unit/test_memory_lifecycle_e082.py` — the
  report prices facts and index at the measured
  anchors and judges the index against each profile's
  ceiling; decay delegates per persona (another
  persona's facts untouched); a superseded fact's
  index pointer is pruned, its bytes honestly reported
  as not reclaimed, and meaning search still serves
  the current fact; `run_lifecycle` composes all
  three; an unavailable mimir half degrades honestly.

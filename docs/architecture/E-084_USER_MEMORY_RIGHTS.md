# E-084 — The user's memory rights: inspect, correct, export, delete-total

*Part V, slice E-084. Roadmap line: "The user's memory
rights: inspect, correct, export, delete-total — as
working operations, plain-worded." The operations live on
the one memory face, `src/ember/well/memory_face.py`
(E-080); the conformance battery is
`tests/unit/test_memory_rights_e084.py`.*

## In plain words

**What the companion remembers about you is yours: you
can look at all of it, fix anything that is wrong, take a
copy away with you, and have any of it — or all of it —
forgotten.** Before this slice the face could remember,
recall, and replace, but the person the memory is *about*
had no operations of their own: the probe that opened
this slice found all six rights operations missing
(`inspect_fact`, `inspect_memory`, `correct_fact`,
`export_memory`, `delete_fact`, `delete_all_memory` —
probe in `~/workspace/.verify-tmp/ember-e084/`). They
exist now, on the face, in plain words, and every one of
them is fenced by the E-083 persona wall: you can only
ever see, fix, take, or forget *your own* persona's
memory.

## 1. The four rights

- **Inspect** — `inspect_memory()` returns everything
  for one persona: the facts still believed true, the
  old versions kept as history (shown separately, so you
  can see what changed), and the remembered conversation
  turns, opening with a plain count of each.
  `inspect_fact(id)` shows one fact exactly as stored.
  Another persona's fact id shown to the wrong persona
  returns nothing — a fact you cannot see, you cannot
  act on either.
- **Correct** — `correct_fact(id, words)` fixes a fact
  *in place*: the same fact keeps its number, its words
  are replaced with yours, through the member's own
  audited update. It is not a quiet supersession (no new
  fact hiding the old one's mistake). Refusals change
  nothing and say why: another persona's fact, empty
  corrected words, a store that is unavailable. If the
  fact was indexed for meaning search, its old index
  entry is dropped and the corrected words are indexed
  afresh under the profile's usual rule — meaning search
  can never serve the wrong words under a corrected
  fact (battery-pinned).
- **Export** — `export_memory()` returns one plain
  bundle: facts (marked still-true vs old versions),
  turns in plain keys (`you_said` / `ember_replied` /
  `when`), and counts. With a path, the same bundle is
  written there as JSON, atomically, for the user to
  carry away. Nothing of anyone else's is ever in the
  bundle. Documents added as documents are shared
  grounding (the E-025/E-035 rule), not one persona's
  memory, and are never exported as if they were.
- **Delete** — `delete_fact(id)` forgets one fact for
  real: its row is removed from the memory store and its
  meaning-search entry is dropped. `delete_all_memory()`
  is the total right: **every** fact the persona owns —
  still-true and old versions alike — is removed, every
  index entry dropped, and every remembered turn
  forgotten, while every other persona's memory is
  provably untouched (the battery seeds two personae and
  verifies the survivor whole). Total deletion is
  guarded by the exact confirmation words
  `"delete everything"` (`DELETE_ALL_CONFIRMATION`):
  an empty string, a near-miss, or different casing
  refuses and deletes nothing.

## 2. Honest limits (new dockets 119–120)

- **119 — a forgotten turn's bytes stay in the store.**
  Brunnr's handle, like its fact-index sibling (docket
  112), offers no episode delete. Delete-total therefore
  tombstones a persona's turns in the face's sidecar:
  they are never served by `recent_turns`, never shown
  by inspect, never exported, and the tombstones survive
  closing and reopening the face (battery-pinned,
  including the trap where an untagged tombstoned turn
  would otherwise resurrect as a default-persona turn).
  The report states `turn_physical_bytes_reclaimed: 0`
  and names this docket — forgotten means unreachable
  and uncounted, not yet physically reclaimed. A
  handle-level episode delete is owed at or before the
  E-092 gate, alongside docket 112.
- **120 — the member's audit keeps hashes, not words.**
  mimir-well's audited delete/update log a short hash of
  the fact's number — never the content itself. After a
  total deletion the store holds no fact rows for the
  persona; what remains anywhere is those content-free
  hashes in the audit trail, which is the member's
  accountability record, stated here so no one over-claims
  "nothing remains anywhere" or under-claims what
  deletion did.
- **Corrupt sidecar caveat (restated):** the tombstones
  live in the same sidecar as the persona tags; the
  E-083 corrupt-sidecar path degrades it to empty, which
  would also lose tombstones. The sidecar is written
  atomically on every change; a store whose bookkeeping
  file was destroyed by hand is outside the drills
  E-087 owns.

## 3. What did not change

No member code was touched: inspection reads through
RunaMemory's own `get_memory`/`search_memories` (an
empty word matches every row a persona owns — that is
how current and history are enumerated without raw SQL,
keeping docket 109), correction through its audited
`update_memory`, deletion through its `delete_memory` —
each already ownership-checked in the member, and the
face checks ownership first so refusals are plain
before they are attempted. Raw-SQL consumers elsewhere
keep their stated paths; Part VIII still owns bifrost's
side. Chat is still not rewired to the face (E-085's
inheritance stands).

## 4. Gate

Conformance: `tests/unit/test_memory_rights_e084.py`
(see CAMPAIGN_STATE for the runner counts of this
slice's gate). Combined Part V conformance and the
whole-suite gate runs are recorded in CAMPAIGN_STATE.md
with this slice's banking entry.

# E-091 — The verdict's residue: the bounded system's docs, marked

*Part V, slice 11 of 16. Roadmap line: "The verdict's residue:
the retired/bounded system's docs marked truthfully
(superseded, with the successor named)."*

## In plain words

Part V judged the companion's memory and chose one face —
`MemoryFace` — over two small house engines, Brunnr and
mimir-well (the verdict, E-079; the face, E-080). The third
system in the tree, mempalace, was left in a particular
state: **bounded, not retired**. Its honourable retirement
was proposed to Volmarr and his word has not been given, so
until he rules, mempalace stays where it is — an optional,
non-default, never-bundled guest for laptop-class machines
only, never part of the companion's memory — and the
project's own documents must *say* that, wherever they
once said something else.

This slice is that saying. It marks the project's living
documents in place, censuses every other place mempalace
is named, and dispositions each one honestly — including
the places it deliberately does **not** rewrite, and why.
(§2's markings cover four of the 65; §3 dispositions the
remaining 61.)

## 1. The standing this slice marks

From E-079 §5–§6, in force since the verdict and unchanged
by this slice:

- **The successor, named:** the companion's memory is
  `MemoryFace` (`src/ember/well/memory_face.py`, E-080),
  one face over two bounded engines — Brunnr (documents,
  chunks, conversation turns) and mimir-well (living
  facts) — reached only through that face.
- **mempalace is bounded:** kept in the tree as an
  optional, non-default, never-bundled external archive
  adapter for laptop-class machines only; excluded from
  every profile's install and from the companion's
  default memory face; its true costs stated wherever it
  is offered (E-078's measurements: no profile fits it;
  ~403 MiB peak RAM; ~185 MB of dependencies + ~88 MB of
  embedding model).
- **Retirement is proposed, not decided.** E-079 §6 put
  the exact question to Volmarr — retire honourably, or
  keep bounded — and **no ruling is on record** at this
  slice's banking. Silence is never read as a retirement
  word (E-079 §6). Under the fallback, this slice marks
  documents; it does **not** remove, move, rename, or edit
  the member itself, and it does not execute E-081's
  migration (which is ruling-gated in the same way).

## 2. Marked in place this slice

Four living documents carried the stale story, in three
places. Each is marked where a reader meets it; none of
their bodies is rewritten.

### 2.1 `docs/UNWIRED_INVENTORY.md` — docket 52, executed

The inventory is the project's canonical list of what is
not wired into Ember, and its mempalace row was the
tree's single falsest sentence about the system:
"(README is scam-warning only — content unclear) …
None planned. Likely abandoned or archival." E-012 proved
that stale in fact (in-tree v3.3.5, MIT, a live upstream
project, 1,712 passing tests measured that slice) while
the row's one true claim — wired: no — stood. Docket 52
assigned the correction to this slice ("correct at
E-091", via the E-018 gate), never silently.

The row now reads truthfully: what mempalace is, that it
is not wired, that the Part V verdict bounds it, the
successor's name, the proposed-not-decided retirement,
and a pointer to this record. The file's "last updated"
line carries the correction's date and docket, so the
change is on the record, not silent. **Docket 52 is
closed by this act.**

### 2.2 `docs/yggdrasil/siblings/19_SIBLING_MEMPALACE.md`

The dedicated MemPalace document in the Yggdrasil design
tree designs an integration that was never built: a
`MemPalaceBrunnr` adapter at
`src/ember/well/brunnr/mempalace/adapter.py`, a Bifrǫst
sub-backend with fusion weights, composed dual-memory
operation. None of it exists — `src/ember/well/brunnr/`
holds only the sqlite_vec and pgvector backends, and
`src/` contains no mempalace reference at all (§3). A
reader meeting this document without a marking would
reasonably believe the integration is planned or real.

It now opens with a status banner: **superseded in part,
bounded** — the designed integration was never built and
is superseded by the E-079 verdict; the successor is
named (`MemoryFace`, E-080, over Brunnr + mimir-well);
the bounded standing and true costs are stated; the
retirement is stated as proposed, awaiting Volmarr's
word; and the document's own open licence question is
answered (MIT, verified at E-007). The body below the
banner stands unrewritten as the pre-verdict design
record, and the banner says so.

### 2.3 The corpus's two front doors

`docs/yggdrasil/siblings/10_SIBLING_MATRIX_OVERVIEW.md`
(the canonical sibling reference, whose MemPalace row
reads "Alt/companion to mimir-well" and whose phase table
lists it as a Phase 2 optional alt memory backend) and
`docs/yggdrasil/INDEX.md` (the design tree's front door,
whose sibling table and memory paragraph present
MemPalace as Mímir's alt/complement) each carry a short
**status note** at their head, scoped to MemPalace only,
stating the bounded standing, naming the successor, and
pointing to §2.2's banner and this record. Their tables
stand unrewritten — they are the corpus's design record —
and the notes govern how they are read.

## 3. The census — every other place, dispositioned

Method: a case-insensitive search for "mempalace" over
the whole tree at this slice's start (raw file list kept
with the slice's gate logs). Outside the member itself,
**65 files** carry the name. Beyond §2's four, they fall
into classes that are *records*, not residue:

- **Dated campaign records (30 files).** The audit series
  (13 files, E-002–E-018, `docs/audit/`), the architecture
  series (15 files, E-019–E-090), the campaign state file,
  and the roadmap itself. These are evidence with dates
  on them — the
  measurements, verdict, and build this slice executes.
  A dated record is not made truer by editing it after
  the fact; they stand as written, and several (E-079,
  E-081, E-090) already carry the bounded standing in
  their own words.
- **The living budget book and the devlog (2 files).**
  `docs/BUDGET_BOOK.md`'s mempalace rows are the measured
  table (257 files / 59,049,715 B; no profile fits) —
  already truthful, and the E-057 battery re-derives them
  live. `docs/DEVLOG.md` is a dated log; its one mention
  is a roll-call of siblings in a dated entry.
- **The Yggdrasil corpus interior (18 further files).**
  Architecture, cross-platform, vision, ai-capabilities,
  robustness, and invented-methods documents mention
  mempalace in passing — a fusion weight here, a profile
  flag there (`62_TIERED_DEFAULTS_BY_PROFILE.md` even
  enables it on desktop-class tiers, a pre-verdict design
  position the verdict's "no profile fits" measurement
  supersedes). These are an elder design corpus's vision
  statements, not the project's living reference docs;
  rewriting eighteen documents' interiors from a Part V
  slice would falsify the corpus as a record of what was
  designed. They are marked **by reference**: the
  corpus's front door (its INDEX) and its canonical
  sibling reference (§2.3) carry the status, the
  dedicated MemPalace document (§2.2) carries the full
  banner, and this census names the disposition openly.
  A future corpus-reconciliation slice may go further;
  this slice does not pretend it has.
- **The elder codex meta (1 file).**
  `docs/hermes_codex/meta/SHARED_CONTEXT.md` enumerates
  the siblings by name in a list; it makes no integration
  claim about mempalace. Codex reconciliation is Part X's
  road (E-161–E-168), not this slice's.
- **Packaging and instruments (2 files + the test tree).**
  `pyproject.toml`'s mentions are the E-043 sdist
  exclusion and its weight comment — mempalace is *in
  fact* never bundled, and the packaging says why; that
  is the bounded standing already executed, not residue.
  `scripts/dev/compare_memory_systems.py` is E-078's
  comparison instrument; it runs mempalace as a measured
  subject and claims nothing else. The test tree's eight
  files are Part V's and Part III's batteries pinning the
  measurements and the verdict — records again.
- **The member's own documents (not counted above).**
  mempalace's own tree — its README and the rest of its
  documentation — is **not marked and not edited**. Two
  laws meet there: no README in this repo is ever touched
  by the campaign, and the member is upstream's own
  project in its own voice (E-012 provenance: imported
  once, `f7ef473`; upstream home
  `github.com/MemPalace/mempalace`). Marking Ember's
  verdict inside upstream's documents would misattribute
  our decision to their project. The verdict lives in
  Ember's documents, where it belongs. The member stands
  present and unmodified, pinned by this slice's battery
  at its E-057/E-077 measure (257 tracked files /
  59,049,715 B).

## 4. What this slice does NOT claim

- **No ruling.** Volmarr's word on retirement is not on
  record; this slice neither seeks to manufacture one nor
  reads the campaign's own momentum as one. E-092's gate
  records the word or its absence, with the fallback in
  force — exactly as E-079 §8 assigned.
- **No removal, no migration.** The member, its stores'
  answer (E-081), and any user's palace are untouched.
  If a retirement ruling arrives, the executing work is a
  later, separately-banked slice under that ruling.
- **No corpus rewrite.** §3's by-reference disposition of
  the Yggdrasil interior is stated as a limit, not
  dressed as a completion: a reader who opens only
  `62_TIERED_DEFAULTS_BY_PROFILE.md` meets the marking
  only via the corpus's front doors.
- **Docket 108 is not this slice's act.** mimir-well's
  flask bound remains owed at or before the E-092 gate,
  as E-079 §5.5 and E-090 §B7 record; it rides to E-092
  unchanged.

## 5. Assignments this slice makes

- **E-092 (Part V gate)** — record Volmarr's word or its
  absence with the fallback in force; close docket 108
  (and rule docket 125's semantics, per E-088/E-090);
  confirm this residue stands (the three markings + this
  census) as the gate's "docs marked truthfully" line.
- **A future executing slice, only under a retirement
  ruling** — E-081's migration tool promotion and the
  member's honourable removal, with attribution kept
  (E-079 §6); until then, no slice removes, moves, or
  edits the member.

## Slice gate

Conformance: `tests/unit/test_memory_residue_e091.py` —
the three markings stand as described (the corrected
inventory row with docket 52's stale sentence gone; the
sibling banner before the document's body, naming the
successor; the two front-door notes); this record states
the standing and its limits; the member stands present
and unmodified at its pinned measure; and `src/` still
carries no mempalace reference — the face's tree is
clean. This slice's battery carries the governance
needle "Volmarr's word", so it joins E-089's canon-guard
allowlist as its thirteenth file, consciously, with its
reason recorded there — the same act E-090 performed for
its twelfth. Root-suite gate runs are recorded in
CAMPAIGN_STATE at banking. No README touched; no member
file touched; no code touched (the allowlist edit is a
test-file governance act, recorded).

*Filed by the E-091 slice, 2026-11-01. Next: E-092 —
Part V gate: one memory face live; migration proven; the
verdict paper + Volmarr's word (where required) on
record.*

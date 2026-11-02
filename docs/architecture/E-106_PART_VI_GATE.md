# E-106 — Part VI Gate: Ember's Kista, Finished as a Program

*Project Ember campaign, Part VI (Kista of the
Toaster) — GATE. Filed 2026-11-02 on branch
`yrsa/ember-road-build` in the campaign's own clone
(`~/workspace/ember-build`), on top of E-105 banked
(84a0085) + its push record (97120b0) + this slice's
IN PROGRESS marker (d421d39). This gate closes
Part VI on the roadmap's own criteria for E-106:
"core binding live; drills green; the boundary
with the ai-folder Kista documented + (E-099)
executed." Like the gates before it, this slice
also lands the rulings the gate review itself
owned: docket 140 is ruled in §5, and docket 133
is carried in the gate's verdict in the words its
own slice ordered (§5). No README was touched.
Gate re-measurements were run this slice; raw logs
live in `~/workspace/.verify-tmp/ember-e106/`.*

## The gate, in plain words — read this first

**Part VI is done. Ember's Kista — the chest that
comes with Ember, on the user's own machine — is
finished as a program in its own right, and the
companion now keeps its keys in it.** The part
built, in order: the custody law the whole
campaign now lives under (E-093 — credentials
live in a Kista, never in configs, code, or chat);
the program mapped from its own code (E-094);
an honest threat model that says what the vault
defends and what it does not (E-095); a passphrase
a normal person can survive, with the recovery
truth stated before it is set (E-096); per-program
access, so a program sees only its own entries
(E-097); the entry kinds sorted into the toaster
set, the kept kinds, and the other road's kinds
(E-098); the interop verdict — the two Kistas
cannot exchange entries, and no entry ever
crosses (E-099); the companion's own binding to
the vault, live (E-100); a carried backup a user
can hold in their hand and restore from (E-101);
the audit drills, green (E-102); the vault's true
prices on the smallest profile (E-103); the plain
user guide and the boundary's final form (E-104);
and the kind names a person can actually use
(E-105).

**Two honest limits stand in this verdict, in
plain words, because a gate that hides them is
worth nothing:**

- **Rollback is NOT DEFENDED.** If someone
  replaces the whole vault with an older copy of
  itself, the program serves the old entries with
  no warning — a rotated-away password comes back
  to life. Damage is caught; *old* is not. The
  only honest remedy is an anchor outside the
  vault folder, and building one is a product
  decision about what the companion may assume —
  recorded as a candidate for Volmarr's word, not
  smuggled in (§5, docket 133).
- **The vault is laptop-class to install.** At
  rest and in use it is toaster-sized — an empty
  vault is 764 bytes, a hundred entries cost a
  third of a megabyte, and unlocking stays inside
  the smallest machine's working memory. But
  carrying it *in* costs 15,723,450 bytes, almost
  all of it the one cryptography library, and that
  fits only the laptop's install ceiling among
  the budget book's profiles. No Ember document
  may call the vault toaster-installable, and its
  install on real toaster-class hardware is
  NOT PROVEN (§5, docket 140).

The boundary with the house Kista — the older
chest on the house computer — is final and
documented (E-104 §B), the crossing question is
answered and executed in its no-branch (E-099:
the boundary doc gained the technical reason; no
bridge was built), and the plain names keep the
two apart for any person asking for help (E-105).

## 1. Gate criteria — each one checked, not assumed

| # | Criterion (roadmap E-106) | Evidence | Result |
|---|---|---|---|
| G1 | Every Part VI slice E-093–E-105 banked | CAMPAIGN_STATE slice ledger, E-093–E-105 all DONE; all 13 per-slice documents present under `docs/architecture/` (pinned by this slice's battery) | PASS |
| G2 | Core binding live | §3: E-100's binding re-proven at this gate — inside the combined Part VI conformance (§6) and by this slice's own live probe (a scratch vault; `ember-core` fetches its own apikey, the owner's entry refuses, a missing entry answers identically) | PASS |
| G3 | Drills green | §4: E-102's drill battery inside the combined conformance, green at this gate; the member suite in its own shape 149 passed / 0 failed | PASS |
| G4 | The boundary documented + (E-099) executed | §2: E-011's boundary, final at E-104 §B with its hazard table; E-099's verdict executed in its if-no branch — the technical reason appended to the boundary doc, no crossing built, the six preconditions on record | PASS |
| G5 | The custody law in force | E-093's law battery inside the combined conformance, green; the tree-wide scan it arms stands classified at this tree | PASS |
| G6 | Part VI's docket accounted for — nothing found, nothing lost | §5: every docket Part VI opened or inherited, each closed, ruled here, or carried with a named owner | PASS — as an accounting; the carried items remain open at their named homes |
| G7 | Full suite green before banking | §6: gate re-measurement (Run A / Run B / Run D + combined Part VI conformance + member suite) recorded there | PASS — on the evidence stated in §6 |
| G8 | Summary filed; the road below checked | The section above ("The gate, in plain words"), §7, and §8: no re-cut demanded; Part VII inherits its named items | PASS |

## 2. Part VI slice by slice — final dispositions

| Slice | What it built or proved | Disposition at this gate |
|---|---|---|
| E-093 | The custody law for the whole campaign; the tree-wide credential census armed as a battery; docket 127 closed, docket 48 ruled | Stands as campaign law; its census battery is in the gate conformance |
| E-094 | The program mapped from code (one Fernet whole-vault file, 14 entry types, the surface as then counted); the default home fixed to `~/.ember/kista/` (docket 46); the member suite re-pointed at the in-tree program (docket 5) | Stands as Part VI's map |
| E-095 | The threat model sized for tiny machines: defended proven, not-defended stated; dockets 131 + 132 built closed (folder 0700, meta and plain backup 0600) | Stands; its claim discipline binds until a ruling changes it (§5) |
| E-096 | The passphrase wrap (scrypt, standard library, the key itself never changes); the copied-folder shape closed; recovery truth stated at the moment of setting; dockets 14 + 128 closed | Live; the unlock road every later slice composes with |
| E-097 | Per-program access: the `KISTA_PROGRAM` tag; another program's entry and a missing entry answer identically; whole-vault acts stay the owner's | Live; the honesty line stands — a program name is an identifier, never a credential |
| E-098 | The 14 kinds partitioned (toaster set / kept / the other road's); dead add roads found and built whole (docket 137; surface 34 → 35); docket 50 closed | Stands; the toaster set is the only set E-100 binds and E-104 documents |
| E-099 | Interop truth: NO — the two Kistas cannot exchange entries; the boundary doc gained the technical reason; the plain road named forbidden for real entries; docket 138 handed to E-101 | **Executed** (G4): the if-no branch, exactly as the roadmap ordered |
| E-100 | The core binding: `src/ember/kista_binding.py`, fetch-only, `ember-core` under E-097, the passphrase road composed; docket 134's write lock built | **Live** (§3) |
| E-101 | The carried backup: whole vault encrypted under a user-chosen backup passphrase, restore proven into a different-key vault; dockets 138 + 135 closed | Live |
| E-102 | The audit drills (wrong passphrase, tamper, partial writes, the carried envelope, the write lock); docket 139 found by the drills and fixed in scope; docket 133 weighed, not closed | **Green** (§4); docket 133 carried at §5 |
| E-103 | The budget proof: 764 B empty, 328,548 B at 100 entries, 41.3 MiB wrapped peak; the install miss measured and handed here as docket 140 | Stands as the vault's prices; docket 140 ruled at §5 |
| E-104 | The plain user guide + the boundary's final form; dockets 130 (non-README half), 49 and 141 closed; hazard H2 verified standing and carried to E-204 | Stands as the guide and the boundary's final form |
| E-105 | The naming kindness: Ember's Kista / the house Kista, applied in the guide and the member skill banner; nothing renamed | Stands; E-195 inherits the names for the member README |
| E-106 | This gate | Closes Part VI |

## 3. The core binding, live — re-proven at this gate

The binding is `src/ember/kista_binding.py`
(E-100): the companion names itself `ember-core`
at the vault, fetches only the toaster set's two
secret-bearing kinds, carries a locked vault's
passphrase by environment-variable *name* only,
and never writes — custody stays the owner's act
at the Kista's own command line. At this gate the
proof was re-run, not recalled: the combined
Part VI conformance (§6) includes E-100's battery
whole, and this slice's battery adds one direct
live probe of its own — a scratch vault built by
the program's own command line, an apikey given
to `ember-core`, an owner's credential left
untagged, and then, through the binding itself:
the companion's key comes back whole; the owner's
entry refuses; a missing entry refuses in the
same shape, its reason naming no value. Frozen
at this gate in the same sense as Part V's face:
the binding's shape (fetch-only, one verb,
program-scoped, passphrase-by-name) does not
change silently — a change to it is its own
slice, with E-100's battery re-pinned consciously.

## 4. The drills, green

E-102's drills are the part's standing proof that
the vault fails honestly: a wrong passphrase
refuses and leaves every file byte-identical; a
tampered or half-written blob heals from the
newest auto-backup or refuses plainly with the
damaged file left standing; a crashed save's
leftover is ignored; the carried envelope refuses
three stated ways under three tamperings; the
write lock holds a writer until the holder lets
go, and two racing writers both land whole. All
of it re-ran green at this gate inside the
combined conformance (§6), and the drills' own
find — docket 139, the partial-write key shapes
that once met the user as a raw traceback — stays
fixed, its plain-refusal shape re-pinned in the
member suite, also green at this gate.

## 5. Part VI's docket — closed, ruled here, carried

Closed during Part VI (each at its slice, verified
from the state ledger): docket 5 (the member suite
judged another installation → the in-tree program,
E-094); docket 14 (the import-time installer,
E-096); docket 46 (the default vault home,
decided E-093, built E-094); docket 48 (the
account ledger ruled an identifier ledger, E-093);
docket 49 (the member skill file's identity,
E-104); docket 50 (the other road's commands
judged and announced, E-098); docket 127 (the
Aesir key file's mode refused unless exactly 0600,
E-093); docket 128 (the `--password` value's loud
warning, E-096); docket 130's non-README half
(the member docs' old default, E-104); docket 131
+ docket 132 (folder and file modes, E-095);
docket 134 (the write lock, built E-100, drilled
E-102); docket 135 (github-backup's harvest shape
named, its staging owner-only, E-101); docket 137
(the dead add roads, E-098); docket 138 (the
plain restore gated, E-101); docket 139 (the
partial-write key refusals, E-102); docket 141
(the member architecture doc's stale meta line,
E-104).

Ruled at this gate, in scope:

- **Docket 140 — RULED: the vault's stated
  install floor is laptop-class.** E-103 measured
  carrying the vault in at 15,723,450 bytes —
  the program's 149,853 plus its one dependency,
  `cryptography`, as installed at 15,573,597 —
  which fits only the laptop profile's install
  ceiling in the budget book. This gate rules the
  *claim*, which is the act E-103 handed it: from
  this gate, Ember's standing words are that
  Ember's Kista is **toaster-sized at rest and in
  use** (764 B empty; 328,548 B for a hundred
  entries with their backups; a 41.3 MiB wrapped
  peak inside the toaster's 64 MiB turn ceiling)
  and **laptop-class to install**, with install on
  real toaster-class hardware **NOT PROVEN**. No
  Ember document may call the vault
  toaster-installable. The gate does not choose a
  different cryptography road: swapping the
  program's one dependency changes what the
  program *is*, and that choice — a smaller
  binding, a vendored road, or accepting this
  floor for good — is Volmarr's word, presented
  at **E-203/E-204** beside the measurement. E-104
  §A8 and the budget book's §7 already speak this
  gate's words; nothing needed correcting to
  comply, which the conformance's doc pins verify.

Carried in this gate's verdict, in its own words:

- **Docket 133 — rollback stands OPEN and
  NOT DEFENDED.** E-102 re-proved the shape as a
  drill: replace the vault file with an older
  valid copy and the rotated-away password is
  served again, with no warning; removed entries
  resurrect the same way. Every in-folder
  freshness shape fails its own claim (a counter
  inside the vault rolls back with it; a metadata
  anchor catches only the single-file swap and
  would fire on the program's own healing and
  restore roads). The only honest remedy — an
  anchor outside the folder — is a product
  decision, recorded here as the candidate remedy
  and handed to **E-204's presentation** as a
  named candidate slice for Volmarr's word. Until
  then E-095's claim discipline binds every Ember
  document: the vault may be described as
  defending its contents against damage and
  against readers without the key or the
  passphrase; it may **never** be described as
  defending against rollback to an older whole
  state.

Carried forward, open, with a named owner each —
this gate closes Part VI on its stated criteria;
it does **not** claim these are fixed:

- **Docket 129** (mimir-well's backup_repo
  credential-bearing URL shape) — owner: **E-187**
  (Part XI's security audit), as E-093 assigned.
- **Docket 136** (the mode fixes are no-ops on
  platforms without POSIX modes, unstated) —
  owner: **E-187**'s platform audit, as E-095
  assigned.
- **Hazard H2** (Verdandi's health check expects
  a `~/.kista/vault.db` shape neither Kista
  writes) — verified still standing at E-104;
  owner: **E-204's presentation**, as a candidate
  slice. No Part VI slice may quietly fix another
  part's member.
- **Docket 130's README half** (the member
  README's stale lines, under the README law) —
  owner: **E-195**, which also inherits E-105's
  plain names to correct them *to*.

## 6. Gate re-measurement (E-017 method, part-gate shapes)

Measured this slice at HEAD 97120b0 plus this
slice's changes (unbanked at measurement time,
banked by this slice's commit), VM profile
(Python 3.12.3, pytest 9.1.1), TMPDIR on /tmp
(509,460,480 bytes free at the gate window);
raw logs in `~/workspace/.verify-tmp/ember-e106/`.

| Run | Shape | Gate result |
|---|---|---|
| A | Whole suite, default env | Interrupted at collection — **1 error, 20 skipped**, exit 2 (docket 1, unchanged since the E-017 freeze) |
| B | Default env, pgvector file excluded (the slice gate) | **1495 passed, 6 failed, 34 skipped** — E-105's 1489 + this slice's 6; the 6 are the proven environment failures (Batch CDE ×3, G ×2, J ×1 — the sqlite_vec family), FAILED list identical in kind |
| D | Whole suite, extras supplied from the isolated dir | **1703 passed, 0 failed, 20 skipped**, exit 0 — E-105's 1697 + 6, fully clean |

Part VI's own sets, same slice:

- **Combined Part VI conformance** (E-057 table +
  E-089 canon guard + E-093–E-106 batteries,
  16 files, default shape): **158 passed**, exit 0 —
  E-105's focal set's 152 + this slice's 6, exact.
- **Focal sets**: this slice's battery
  **6 passed**; the pre-doc standing check of
  the same set without this slice's battery stood
  at **152 passed** — E-105's focal count, exact,
  proving the banked tree whole before the gate's
  own files landed.
- **Member suite** (kista's own tests, in its own
  shape, `PYTHONPATH=kista`): **149 passed,
  0 failed** — unchanged since E-094, as no
  program code changed in this slice.

The E-057 member budget table is unchanged by
this slice: no member file moved (this slice adds
one architecture doc and one battery, neither a
member file), so kista stands at **25 files /
2,823,610 B** and the twelve-member total at
**131,616,318 B**, the laptop miss unchanged at
**256,017 B** — verified standing by the E-057
pin inside the conformance, not re-measured.

## 7. Plain-language summary (for the campaign record)

Part VI asked: *can the smallest machine keep
secrets properly — its own chest, finished as a
program, honest about what it is and is not?*
Thirteen slices answered it. The law came first:
credentials live in a Kista, never in configs,
code, or chat, and the tree was scanned to prove
it could live under that law. The program was
read before it was judged, its worst inherited
habits fixed at the root — it now lives in its
own home, its tests judge itself, and it no
longer tries to install its own dependency from
the network. Its dangers were named in a threat
model that refuses to oversell, and the two
mode defects that model could close cheaply were
closed the same slice. Then the human shapes:
a passphrase that wraps the key without moving
a single entry, whose loss is stated plainly
before it can happen; doors per program, so the
companion holds only the keys it was given; a
backup a person can carry on a stick and restore
on a new machine with nothing but a passphrase
they chose. The kinds of thing it holds were
sorted honestly — four for the toaster, five
kept because people already trust them to it,
five recorded as the other chest's road and
never silently merged. The two chests were
proven unable to trade entries, and that answer
was written into the boundary itself. The
companion was bound to its chest. The drills
broke the vault every honest way and it failed
honestly every time — and the one break it
cannot honestly answer, rollback, is named in
this verdict rather than buried. Its prices were
measured to the byte, and the one price that
misses — the install weight — is ruled on here
rather than rounded down. The guide was written
in plain words, and the two chests were given
names a tired person at midnight can tell apart.
What Part VI did not do: defend rollback, fit
the install on a toaster, touch the other chest,
or touch any README — each is named, owned, and
carried in §5, not buried.

## 8. The road below — checked

Part VII (E-107–E-122, the inner life: seiðr
engine & astrology engine) follows in roadmap
order; nothing in Part VI's evidence demands a
re-cut. Part VII opens with E-107, the seiðr
engine mapped. Later owners named at this gate:
E-187 (dockets 129 + 136), E-195 (docket 130's
README half, with E-105's names), E-203/E-204
(docket 140's cryptography-road choice; docket
133's candidate slice; hazard H2's candidate
slice). The roadmap file was not edited by this
gate.

## Carried forward

- Part VI is CLOSED by this gate. Next: E-107
  (Part VII) — seiðr engine mapped.
- Open and carried, not lost: docket 133
  (→ E-204 presentation, NOT DEFENDED until
  then), docket 140's road choice (→ Volmarr's
  word at E-203/E-204; the claim ruled here),
  docket 129 + docket 136 (→ E-187), hazard H2
  (→ E-204 presentation), docket 130's README
  half (→ E-195, with the E-105 names).
- NOT PROVEN at this gate: the vault's install
  on real toaster-class hardware; rollback
  defence — each with its owning presentation
  named above.

*Filed by the E-106 slice, 2026-11-02. Part VI
gate: PASS. Next: E-107 — seiðr engine mapped
(Part VII opens).*

# E-105 — The Naming Kindness

*Project Ember campaign, Part VI (Kista of the
Toaster), twelfth slice. Roadmap line: "The naming
kindness: user-facing names distinguish the two
Kistas without jargon (support-confusion
prevented)". Built 2026-11-02 on branch
`yrsa/ember-road-build` in the campaign's own
clone, on top of E-104's boundary final. Method:
the names below were chosen against E-104 §B5's
final boundary and then applied at the two places
a user actually meets this program's name — the
plain user guide (E-104, which gains a naming
addendum, appended and never rewritten) and the
member skill file's identity banner (kista/SKILL.md).
The program itself was not touched: this slice
proves, by pin and by live probe, that the
command, the folder, and the vault's own printed
words stand exactly as E-104 left them. The
ai-folder Kista was not accessed, run, or read —
and, per §4, it is not renamed either: §2 gives
Ember's users a kind way to *refer* to it, nothing
more. Where this document and the code ever
disagree, the code and its batteries are the
truth and this document is the defect.*

## Headline — the two names, in plain words

There are two programs called Kista, and a person
asking for help should never have to know the
word "toaster", the name of a folder, or the
history of either program to say which one they
mean. From this slice, Ember's user-facing words
call them:

- **Ember's Kista** — *your chest.* The one that
  comes with Ember and lives on your own machine,
  in `~/.ember/kista/`. It holds your passwords,
  tokens, URLs, and notes, and Ember's companion
  reads its own entries from it (E-100, E-104).
- **The house Kista** — *the house's chest.* The
  older one, which lives on the house computer
  (purplelongship) under its own keeper and holds
  the house assistants' own credentials. No Ember
  user ever uses it, opens it, or sends anything
  to it — it is named here only so that a person
  who hears "Kista" from that side of the house
  can tell the two apart and be routed kindly:
  that is not the chest Ember can help with.

**The one sentence that carries the whole
kindness:** Ember's Kista is yours, on your
machine; the house Kista is the house's own, on
the house computer; and no entry ever crosses
between them (E-099, E-104 §B2).

## 1. Why a name was owed

E-104 §B5 settled what the two programs *are* and
left one thing unsettled in the open: "users
still have only the bare word 'Kista' for two
programs." The builders' names do distinguish
them — toaster-Kista and ai-folder Kista (E-011
rule 1) — but both are workshop words. One names
a machine class a normal person does not own
vocabulary for; the other names a folder on a
computer the user may never have seen. A support
conversation that starts "my Kista…" can be
about either program, and until this slice
nothing in Ember's user-facing words told a
helper which questions to ask. That is the whole
defect this slice repairs: not a wrong name, a
missing kind one.

## 2. The names and how to use them

- **First mention, full form.** In any guide,
  help answer, or support reply, the first
  mention of either chest carries its plain name
  and its home in the same breath: "Ember's
  Kista (the chest on your machine)" or "the
  house Kista (the assistants' chest on the
  house computer)". After that, the plain name
  alone is enough in that document or reply.
- **Never bare "Kista" where both could be
  meant.** The bare word stays fine in exactly
  two places: quoting the program's own words
  (§4 — they stand), and a passage whose subject
  is already one named chest and cannot drift.
  A fresh reader landing mid-page must never
  have to guess which chest a paragraph is about.
- **The names are descriptions, not brands.**
  Each one says whose it is and, by implication,
  where it lives. That is deliberate: the two
  questions that settle every confusion (§3) are
  already inside the names.
- **Kindness is the test.** A name fails this
  slice if a non-technical person, hearing it
  for the first time, cannot say which chest is
  meant or feels corrected for using the wrong
  one. Nobody is ever wrong for saying "Kista";
  the names exist so the *helper* can ask §3's
  questions instead of assuming.

## 3. The support road — two questions

When a request arrives about "Kista" with no
name attached, the helper asks, in this order:

1. **"Is it on your own machine, with Ember —
   or the house's one?"** Machine settles nearly
   every case: Ember's Kista lives at
   `~/.ember/kista/` on the user's machine; the
   house Kista is not on it at all.
2. **"What were you doing when it came up —
   opening your vault, or talking to one of the
   house assistants?"** Doing settles the rest:
   a person at their own command line is always
   Ember's Kista; a person who was handed the
   word by an assistant's setup is hearing about
   the house Kista, and the kind answer is the
   headline sentence plus a pointer back to that
   assistant's own keeper — never an attempt to
   open, fix, or move anything on that side
   (E-011 rules 2 and 5 stand untouched).

Worked rewrites, of the shapes E-011 feared:

| As it arrives | The kind reading |
|---|---|
| "Kista lost my password." | Which chest? Only Ember's Kista is ours to help with; its failure shapes and honest answers are E-104 §A7. |
| "Update Kista to the new version." | Neither chest is updated from the other's road (rule 6). A version string is not a name: both answer to "Kista v2.0" (hazard H6). |
| "Copy my entries into Kista." | Into *Ember's* Kista, from a file this program itself made (E-101) — never across to or from the house Kista (E-099). |
| "Kista says my folder is unlocked." | Ember's Kista, in its own standing words (E-096); the passphrase road is E-104 §A4. |

## 4. What this slice does NOT rename

The kindness is a layer of speech over a settled
boundary, not a renaming of anything Part VI
built. Standing exactly as before, each pinned
by this slice's battery:

- **The command** is still `kista`, and its 35
  subcommands are unchanged (E-098, E-104 §A3).
- **The folder** is still `~/.ember/kista/`, and
  `KISTA_DIR`, `KISTA_PROGRAM`, `KISTA_PASSPHRASE`
  keep their names and meanings (E-094, E-096,
  E-097).
- **The vault's own words stand.** The program
  still calls itself "Kista" in its help text,
  its header ("Kista v2.0 — The Vault of
  Yggdrasil"), and its status output, and still
  states the passphrase consequence in the words
  E-096 and E-104 pinned. Changing what the
  program prints about itself to match a naming
  layer would break those pins and teach nothing;
  the guide carries the names instead.
- **Builders' citations stand.** Technical
  writing keeps E-011 rule 1 — cite a Kista by
  which one, where, and when (toaster-Kista /
  ai-folder Kista). The plain names are the
  user-facing layer; neither layer rewrites the
  other, and this doc is the map between them:
  Ember's Kista = toaster-Kista; the house
  Kista = ai-folder Kista.
- **The other program is not renamed.** "The
  house Kista" is Ember's referring name for it
  in user-facing speech. Its own keeper's names
  for it are that side's business (E-011 rule 6's
  spirit), and nothing in this slice reaches
  across the boundary — no file, doc, or word on
  that side was touched or could be.

## 5. Where the names now stand

- **This document** is the naming record: the
  names, the rules for using them, and the map
  to the builders' names (§4).
- **The plain user guide (E-104)** gains a
  naming addendum, appended after its slice
  gate, carrying the two names and the one
  carrying sentence into the one document a
  user actually reads. The guide's body stands
  as banked; the addendum extends it, exactly
  as E-104 itself extended E-011.
- **The member skill file (kista/SKILL.md)**
  gains the plain names inside its existing
  identity banner, so an assistant reading that
  file meets the kind names at the same moment
  it learns there are two chests at all. Its
  machine name (`kista-toaster`, E-104 docket
  49) is a builder identifier and stands.
- **The member README is not touched.** It
  still says bare "Kista" and holds docket
  130's three stale lines; both are E-195's,
  by the owner's hand or word, under the
  standing README law. This slice hands E-195
  the names to use when that day comes (§6).

No program code changed in this slice, and no
new subcommand exists: the surface stays 35.
The E-089 canon guard needed no new allowlist
entry — this slice's battery carries no
householder name, checked not assumed.

**Gate findings, recorded plainly (found by this
slice's own gate, fixed in scope).** Two guard
catches, both in the campaign's own test tree,
neither in the program: (1) this slice's battery
first carried a real-history marker the canon
guard forbids in test files — the machine name
in a doc needle; the needle now reads the doc's
own plain phrase ("the house computer") and the
guard passes, no allowlist entry added. (2) The
custody battery (E-093) met one unclassified
credential-shaped assignment in the tracked
tree: the E-104 battery's synthetic scratch-vault
passphrase, which entered the tracked tree at
E-104's banking, after that slice's focal halves
ran. Classified consciously at this slice in the
custody battery, with attribution — the act that
battery exists to force (precedent: E-100).

## 6. Standing findings handed on

- **E-106** (the Part VI gate) inherits the two
  plain names for its own plain-word report:
  Ember's Kista, bound live to the core (E-100),
  drills green (E-102), boundary final (E-104),
  names kind (this slice) — with dockets 133
  (rollback, NOT DEFENDED) and 140 (the
  laptop-class install weight) still to carry in
  plain words, exactly as E-104 handed them on.
- **E-195** inherits, beside docket 130's README
  half, this slice's names: when the member
  README is corrected by the owner's hand or
  word, "Ember's Kista" is the name its stale
  lines should be corrected *to*.
- **Every future user-facing Ember document**
  inherits §2 as a standing rule of the house
  style E-104 named: plain words at the moment a
  thing happens, and now — a chest is never
  mentioned to a user without the name that
  says whose it is.

## Slice gate

Focal battery `tests/unit/test_kista_naming_e105.py`
pins this record: the two plain names and the
carrying sentence in this doc; the map to the
builders' names; the unchanged-things pins read
from the program file itself (its help words, its
header, the plain names' absence from the
program's own speech — the 35-command surface
itself stands under the E-098/E-104 pins in the
focal set); the naming
addendum appended to E-104 with the guide's
banked body intact; the SKILL.md banner carrying
the plain names beside its standing machine
name; and one live probe — a scratch vault's
`init` and `status` still speaking the vault's
own standing words, proving the naming layer
changed no program behaviour. Member suite and
root gates are recorded in the campaign state
file at banking; the E-057 member table is
re-measured and re-pinned there with attribution
(this slice's SKILL.md banner edit moves kista's
row; both published copies re-pinned to the
tree).

*Filed by the E-105 slice, 2026-11-02. Next: E-106 —
the Part VI gate.*

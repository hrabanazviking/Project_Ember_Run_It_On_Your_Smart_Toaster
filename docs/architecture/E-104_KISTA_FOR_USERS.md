# E-104 — Kista for Users (Plain) + the Boundary Doc Final

*Project Ember campaign, Part VI (Kista of the Toaster),
eleventh slice. Roadmap line: "Docs: Kista for users
(plain) + the boundary doc final". Built and measured
2026-11-02 on branch `yrsa/ember-road-build` in the
campaign's own clone, at campaign commit ea71996
(E-104 IN PROGRESS), on top of E-103's budget proof.
Method: every command named in Part A was run this
slice against a scratch vault holding synthetic
entries only (raw log in
`~/workspace/.verify-tmp/ember-e104/probes.log`);
every price is E-103's measured figure, re-stated,
not re-measured; every member-doc correction in §B3
was made in place and is pinned by this slice's
battery against the files themselves. The ai-folder
Kista was not accessed, run, or read — the E-011
boundary governs every word below about that side.
Where this document and the code ever disagree, the
code and its batteries are the truth and this
document is the defect.*

## Headline — read this first, in plain words

**Part A is the whole user guide to your vault, in
plain words. Part B closes the two-Kistas boundary
for the last time in this part.**

- **Your chest holds passwords, tokens, URLs, and notes.**
  That is the promise. Five more kinds stay
  in the chest so nothing you already keep is ever
  stranded, and five kinds that belong to a different
  program's road are announced out loud if you ever
  add one — never quietly absorbed (§A1).
- **It lives in one folder on your own machine,**
  `~/.ember/kista/`, costs less than a photo's
  thumbnail when empty and about a third of a
  megabyte with a hundred entries in it, and talks
  to nobody: no account, no cloud, no phone-home
  (§A2, §A8).
- **You can lock it with a passphrase only you
  know.** With one set, a copied folder is a locked
  box. Without one, the program tells you plainly —
  at the moment it matters — that a copied folder
  opens. And the recovery truth is stated before
  you choose, not after: a forgotten passphrase
  means a lost vault, because that is what makes
  the lock real (§A4).
- **The boundary is final.** There are two programs
  called Kista. They are not the same program, they
  are never synced, and no entry ever crosses
  between them — E-099 proved no honest bridge
  exists today, and Part B records the disposition
  of every confusion hazard the campaign ever found
  (§B1–§B2). What you call them to tell them apart
  in conversation is the next slice's kindness
  (E-105); what they *are* is settled here.

---

# Part A — For users, in plain words

## A1. What this is, and what it holds

Kista — the word is Old Norse for a strongbox or
chest — is a small program that keeps your secrets
in one encrypted file on your own machine. Ember's
companion uses it for the keys it needs (§A5), and
you can use it yourself from the command line. It
has no window and no account: you talk to it by
typing `kista` and a command (§A3).

**The kinds it exists to hold — the toaster set:**

| Plain word | What you keep in it | The command shape |
|---|---|---|
| passwords | a login: username, password, email, the site's address | `kista add <name>` |
| tokens | an API key or token a program uses | `kista add-apikey <name> --key …` |
| URLs | a link worth keeping, with a title | `kista add-url <name> --url …` |
| notes | a small piece of writing that must not be lost | `kista add-note <name> --content …` |

**Also in the chest, in one line:** one-time-code
secrets, licence keys, machine keys, certificates,
and identity records also work and are tested. They
stay because removing a kind would strand entries
someone already keeps. They are kept, not promised:
Ember builds nothing on them (E-098).

**The boundary sentence:** astrology charts,
character sheets, rune and tarot readings, and
documents belong to the *other* Kista's wider road
(§B1). If you add one here, the program keeps it
exactly as given — and tells you in words, at that
moment, that the kind is not one of this chest's
own. Nothing is ever merged silently.

## A2. Where it lives, and what is in the folder

Everything sits in one folder: **`~/.ember/kista/`**
by default — inside Ember's own home, nobody else's
(E-094). A person who looks after the machine can
point it elsewhere with the `KISTA_DIR` environment
variable; the override always wins.

| File | What it is |
|---|---|
| `vault.json.enc` | the whole vault, encrypted as one file |
| `.vault_key` | the key that opens it (owner-only, mode 600) |
| `vault_meta.json` | a plain index of service *names* and dates — never values (also mode 600 since E-095) |
| `backups/` | the last five automatic safety copies of the vault, kept by the program itself |
| `config.json` | the program's small settings file, if any are set |

The folder itself is owner-only (mode 700). The
encryption is Fernet (AES-128-CBC with an
HMAC-SHA256 check): change one byte of the vault
file and the check fails — tampering is detected,
never silently read (§A7).

## A3. The handful of commands you will ever need

Proven this slice, in this order, on a fresh vault:

```bash
kista init                       # make the vault (once)
kista add example-login --username you --password-file pw.txt --url https://example.invalid/login
kista add-apikey example-token --key <the token>
kista add-url example-link --url https://example.invalid/docs --title "Example docs"
kista add-note example-note --content "a note that must not be lost"
kista get example-login          # read one entry back, whole
kista list                       # every name, nothing secret shown
kista check example-login        # "do I already have this?"
kista search example             # find by part of a name or field
kista update example-login --url https://example.invalid/new   # change a field
kista remove example-login       # take an entry out
kista generate-password          # invent a strong password for you
kista status                     # the vault's health, in words
```

Three habits keep you safe, and the program helps
with all three:

- **Give secrets by file, not by typing them after
  a flag.** `--password-file` (and its kin) keeps
  the secret out of your shell history and the
  machine's process list. If you do type
  `--password <value>`, the program still honours
  it — and prints a loud warning at that moment
  naming the exposure and the safer shapes (E-096).
- **One entry per secret.** A login, its token, and
  its machine key are three entries with three
  names, not one crowded entry.
- **`status` is the honest mirror.** It tells you
  how many entries you hold, where the vault lives,
  and whether a passphrase is set — with the
  consequence in words either way (§A4).

The program has 35 commands in all (the rest are
typed shortcuts for the other kinds, and the
vault-life commands in §A4–§A7). This handful is
the whole daily road.

## A4. Locking it: the passphrase, and the honest recovery story

Out of the box the key sits in a file beside the
vault. That guards your secrets from *other
accounts* on the machine — but not from someone who
copies the whole folder. To close that gap:

```bash
kista set-passphrase             # lock the vault under a passphrase
kista remove-passphrase          # take the lock off again (it warns first)
```

Setting one changes only the key's wrapping, never
the key itself: every entry, backup, and export
keeps working exactly as before (E-096). From then
on, each command asks for the passphrase without
echoing it (or reads `KISTA_PASSPHRASE` for scripts
— never a command-line flag, and never from a
config file, per the custody law E-093).

**The recovery story, stated the way the program
states it before you set anything:** if you forget
the passphrase, nobody can open your vault. Not
you, not Ember, not anyone.
There is no reset, no recovery copy, no back door.
Write it down somewhere safe, the way you would a
house key's hiding place.
A short sentence you can remember works well; eight
characters is the floor. The vault file itself is
never touched by a failed attempt — remember later,
or find the written copy, and everything opens as
it was.

And if you choose *not* to set one, the program
says so at the moments it matters: `init` and
`status` both state that the vault has no passphrase
and that a copy of the folder opens it. Silence
about an unlocked vault is what ended at E-096; the
unlocked shape itself remains, deliberately, for
owners whose machine is locked down in other ways.

## A5. Programs get only their own entries

Your companion reads its model and API credentials
from this vault (E-100) — under a rule that keeps it
honest (E-097): a program that names itself (Ember's
core names itself `ember-core`) can add, read, list,
search, change, and remove **only its own entries**.
Asked for anyone else's entry, the vault answers
exactly as it answers for an entry that does not
exist — a program learns nothing about the rest of
your chest, not even names or counts. Whole-vault
acts — locking, backups, exports, repair — are
yours alone; a program asking for them is refused
in words before anything is touched.

The honest limit, in the open: a program's name is
an identifier, not a password. This scoping is
discipline for well-behaved programs, not a wall
against malicious code running as *you* — code that
runs as you can read what you can read. That was
E-095's verdict and it stands (E-097, E-106 carries
it to the gate).

## A6. Backups you can carry, and the two warnings that travel with them

**The carried file (the one to use).**
`kista backup --carry <file>` writes your whole
vault encrypted under a *backup passphrase you
choose then and there* — never the vault key, never
typed as a command-line argument. Carry that file
anywhere: on a stick, in a drawer, to another
machine. `kista restore <file>` recognises it and
restores into a different vault on the passphrase
alone, under that vault's own key (E-101). A wrong
passphrase is refused plainly and the destination
stays empty. The file holds no readable entries and
no key, and it is written owner-only (mode 600).

**Warning one — the plain road.**
`kista backup` without `--carry` writes your
entries *readable*. Since E-101 it is gated: a plain
backup is refused on restore unless you pass
`--allow-plaintext`, and a loud warning prints
first. Treat a plain backup file the way you would
treat a written-down list of every password you
own — because that is what it is.

**Warning two — `github-backup`.** This older road
pushes encrypted copies of the vault to a git
repository. Before writing anything it now tells
you its shape in words (E-101): every copy ever
pushed stays in that repository's history, every one
opens under the one vault key, the program cannot
check whether the repository is private, and a
working copy sits on this machine too. Encrypted
does not mean consequence-free.

`export`/`import` are the third road — a copy of
the encrypted vault itself. They only work between
vaults holding the *same* key, which is why they
are a same-vault backup shape and never a way to
move entries anywhere else (§B2).

## A7. When something goes wrong

- **Wrong passphrase:** refused in plain words,
  nothing shown, nothing changed, the vault file
  left byte-for-byte as it was (E-102).
- **A damaged or half-written vault file:** the
  program detects it (the encryption check), and
  heals from the newest of its five automatic
  backups. If no good copy is left, it refuses
  plainly, leaves the damaged file standing, and
  never mints a new key over your data — a new key
  would make the loss permanent, so the program
  will not do it (E-102). `kista repair` runs the
  same healing by hand.
- **A damaged key file** (truncated, emptied, torn):
  a plain refusal in the program's own words, the
  damaged file left exactly as it stands (E-102).
- **The one gap with no healing, stated plainly:**
  an *older* copy of the vault file, put back in
  place, opens without any warning — and a password
  you changed since that copy was made is the old
  password again inside it. Rollback is **not defended** (proven at E-102; every fix that lives
  inside the folder can be rolled back with the
  folder, and the honest remedy — an anchor outside
  the folder — is a decision the Part VI gate
  carries at E-106, not a thing this guide may
  imply exists). If a whole folder copy matters to
  you, the passphrase (§A4) is the protection that
  travels with it.

## A8. What it costs — the small print, measured

Every figure below was measured at E-103 on the
campaign machine against the smallest profile's
ceilings; they are restated here, not re-measured:

- **At rest:** an empty vault is **764 bytes** in
  all. A typical entry adds about **563 bytes**;
  a working vault of **100 entries** — vault, five
  automatic backups, key and index — weighs
  **328,548 bytes**, about a third of a megabyte,
  16% of the smallest machine's monthly
  storage-growth allowance.
- **Standing idle: exactly zero.** The vault is a
  command, not a servant — no process runs between
  commands, so it uses no memory and no processor
  while you are not using it.
- **In use:** one command peaks at **27.2 MiB** of
  memory on a 100-entry vault, and **41.3 MiB**
  with a passphrase set (the unlock's deliberate
  working set) — inside the smallest profile's
  64 MiB working ceiling, at about two-thirds
  of it.
- **Carrying the program in is the one miss, in
  the same size type:** the program file is
  **149,853 bytes**, but its one dependency, the
  `cryptography` library as installed on the
  measuring machine, is **15,573,597 bytes** —
  **15,723,450 bytes** together, which fits only
  the laptop profile's install ceiling. Until the
  Part VI gate rules (docket 140 → E-106), no
  Ember document may call this vault
  toaster-*installable* — toaster-sized at rest and
  in use is the honest claim, and it is proven.
  Small-hardware installation itself is
  **NOT PROVEN**: no install was made on
  toaster-class hardware in this campaign.

## A9. What it never does

- **No cloud, no account, no phone-home.** The
  program makes no network call in its ordinary
  life; the only network-shaped road is
  `github-backup`, and §A6 states its price.
- **No sync with the other Kista.** Ever, in
  either direction (§B1).
- **No silent anything.** A kind that is not its
  own is announced (§A1); a plain backup is warned
  (§A6); an unlocked vault is stated (§A4); a
  program is refused in words (§A5). Plain words
  at the moment a thing happens is this program's
  house style, and this guide holds it to that.

---

# Part B — The boundary doc, final form

*This part is the final form of the boundary first
drawn at E-011 (`docs/audit/E-011_TWO_KISTAS_BOUNDARY.md`).
That document stands exactly as filed, with its
E-099 addendum; a matching final addendum is
appended to it by this slice, extending and never
rewriting. What follows is the boundary as Part VI
leaves it: every fact re-stated at this tree, every
hazard given its disposition.*

## B1. The two Kistas, as they now stand

| | **Toaster-Kista** | **Ai-folder Kista** |
|---|---|---|
| What it is | the Smart Toaster's credential program, this campaign's member | the operational vault of the Hermes/Runa line, the one Heimdall uses |
| Where it lives | `kista/` in this repo; its vault defaults to `~/.ember/kista/` (E-094) | purplelongship, kept current with the standalone GitHub repo — **recorded, not measured** (E-011 §2); this campaign never accesses it |
| Custody | this campaign, under Part VI (E-093's custody law) | that side's own keeper, under the owner's word there |
| State after Part VI | mapped (E-094), threat-modelled (E-095), passphrase unlock (E-096), per-program access (E-097), entry kinds judged (E-098), core binding live (E-100), carried backup (E-101), drills green (E-102), budget proven (E-103), this guide (E-104) | untouched by this campaign in every particular |
| Sharing | a name (*kista*, a strongbox), a spirit (self-owned, encrypted, no king, no keeper), and a lineage in Runa's credential work — **not** a codebase to sync, a vault to merge, an update road, or a keeper | the same, from its side |

Both programs answer to "Kista v2.0". A version
string is not an identity (hazard H6): cite a Kista
by **which one, where, and when**, never by version
alone.

## B2. Every hazard, disposed

E-011 found six ways the two programs could be
confused. Their dispositions at this slice:

| Hazard | Disposition |
|---|---|
| **H1 — the toaster copy defaulted into the other Kista's home** (`~/.hermes/credentials`, same filenames) | **CLOSED at E-094** (docket 46): the default is `~/.ember/kista/`; `KISTA_DIR` overrides. The member docs that still stated the old default are corrected at this slice (§B3, docket 130); the root README's lines are the owner's-hand exception, owned by E-195 |
| **H2 — a third vault shape in a consumer** (Verdandi's health check expects `~/.kista/vault.db`, SQLite — a shape neither Kista writes) | **STILL STANDING, verified at this tree**: the check stands as E-011 found it. Part IV, its assigned owner, closed at E-076 without taking it. It is carried — named, not dropped — to the campaign's closing presentation (E-204), where it stands as a candidate slice beside its kin; no Part VI slice may quietly fix another part's member |
| **H3 — the toaster tests judged the other installation** | **CLOSED at E-094** (docket 5): the member suite resolves the in-tree program; 149 passed / 0 failed from that slice on |
| **H4 — the ai-side account ledger inside the toaster tree** (`kista/references/known-accounts.md`) | **RULED at E-093** (docket 48): an identifier ledger — service names and statuses, never values — not a leak. It stays; removal is the owner's word, unmade on this record |
| **H5 — an aspirational fourth shape in design docs** (the Yggdrasil corpus's `~/.ember/kista.vault`, `kista://` shapes) | **STANDS AS PROPOSAL**: design intent, never built, never a description of either program. Its stale "8 entry types" figure is elder design text; any future reader is directed to §B1 and E-098 for the counted truth |
| **H6 — same version, different programs** | **STANDS AS A CITING RULE** (above): which one, where, when |

And the crossing question itself, settled at
**E-099**: the two Kistas **cannot exchange
entries** — every encrypted road needs the same
key (sharing it would be a surrender of the whole
vault, not an exchange), no road selects only the
toaster set, and the other side's format is
unmeasured because this campaign does not inspect
it. The one road that crosses keys moves secrets
in plain text and is forbidden for real entries
under the custody law. A bridge could only be
proposed when its preconditions stand (E-099 §4) —
a measured target format, and the owner's explicit
word against rule 5 below, first of all. Until
then: **no entry ever crosses.**

## B3. Dockets closed here — 130, 49, and 141

- **Docket 130 — CLOSED (the non-README half).**
  The member's own documents stated the old
  default home in five files. Corrected in place
  at this slice, elder prose preserved: the vault
  layout in `ARCHITECTURE.md`, the key path in
  `PHILOSOPHY.md`, the default in `ENTRY_TYPES.md`
  (which also gains the E-098 partition — §B4),
  and `SYSTEM_VISION.md`'s storage/key lines, its
  path-resolution item (the `KISTA_DIR` half now
  marked built, the `--vault-dir` flag honestly
  marked *not built*, the proposal left standing
  as a proposal), and its two proposal paths,
  re-based on this program's own home. After this
  slice, the string for the other program's
  credentials directory survives in the member
  only in `kista/README.md` — which stands under
  the standing README law and is **not** this
  campaign's to edit: its three stale lines (the
  "8 entry types" feature line, the key-isolation
  path, the default) are E-195's, by the owner's
  hand or word.
- **Docket 49 — CLOSED.** `SKILL.md` described the
  Hermes deployment as this program's home. Its
  frontmatter now names this copy (`kista-toaster`,
  the Ember monorepo as its home, no Hermes skill
  metadata), its description counts the true
  **14 entry types** and names the toaster set, its
  repo line points at this copy's home and names
  the standalone repo as the *other* Kista's, its
  key path is corrected, and a banner at its head
  marks the later operational sections (Standing
  Rules, Account Discovery, Pitfalls) for what
  they are — inherited Hermes-side working text,
  kept as provenance, not instructions for a user
  of this program. Nothing was deleted.
- **Docket 141 — NEW → CLOSED in scope (found by
  this slice).** `ARCHITECTURE.md`'s file-layout
  section also stated that `vault_meta.json` "is
  intentionally readable" — stale since E-095
  made the metadata owner-only (mode 600) on every
  save. A reader trusting that line would
  misjudge what another account on the machine
  can see. Corrected in the same edit as its
  neighbouring path: the index holds names only,
  *and* it is written mode 600. This slice's
  battery pins both halves of the correction.

## B4. The member docs, reconciled as a set

After §B3, a reader who starts anywhere in the
member lands on the same truth: `ENTRY_TYPES.md`
opens its design with the E-098 partition stated
(toaster / kept / other-road), so its fourteen
types are never again read as one undifferentiated
promise; `SKILL.md` frames which Kista it describes
before describing it; the vision document's
proposals are marked built, part-built, or not
built at the lines that propose them. The member's
remaining elder documents (`BUG_REPORT.md`,
`CODE_REVIEW.md`, `DOMAIN_MAP.md`, the references)
state no vault default and were not touched — the
battery re-checks the whole member for the old
default's string, so a future stale line anywhere
in it fails loudly instead of quietly.

## B5. The custody rules, final form

E-011's eight rules stand, with three of them
carrying Part VI's amendments in the open:

1. **Name the Kista** — toaster-Kista (`kista/` in
   this repo) or ai-folder Kista (purplelongship /
   standalone GitHub). Bare "Kista" only where the
   same paragraph makes it unambiguous.
2. **This campaign works only on toaster-Kista.**
   The ai-folder side — code, vault, entries, repo,
   update road — is out of scope entirely (E-093's
   custody law is this rule's working form).
3. **Never run toaster-Kista unconfigured in
   campaign work** — `KISTA_DIR` to scratch first.
   The rule's original reason (the default resolved
   into the other program's home) is gone since
   E-094; the discipline stands, because this
   campaign never keeps real entries (E-093 §2).
4. **Never point a toaster test, fixture, or probe
   at the other installation's paths.** A test that
   needs the other copy is a defect (H3, closed —
   the rule keeps it closed).
5. **No entry ever crosses.** No exception stands
   today: E-099's preconditions (a measured target,
   the owner's word) are the only road to even
   proposing one.
6. **No sync in either direction.** A fix that
   seems to belong on both sides is written twice,
   by each side's own keeper, under separate words.
7. **Real credentials live only in the ai-folder
   Kista's custody** on the house's machines today;
   the toaster program holds no real entries
   anywhere this campaign knows of, and gains none
   outside E-093 and the owner's word.
8. **The boundary is a fact, not a merger waiting**
   — documented here in final form, bridged only
   under rule 5's preconditions, never papered over.

## Standing findings handed on

- **E-105** (the naming kindness) inherits a settled
  boundary and an unsettled vocabulary: users still
  have only the bare word "Kista" for two programs.
  The names it chooses must distinguish them without
  jargon, and must not rename anything Part VI built
  (paths, commands, and the vault's own words stand).
- **E-106** (the Part VI gate) inherits this
  boundary as final, dockets 133 (rollback, NOT
  DEFENDED, §A7) and 140 (the install weight, §A8)
  to carry in plain words, and §A5's identifier-not-
  a-credential honesty line unchanged.
- **E-195** inherits the README half of docket 130
  (§B3): three stale lines in `kista/README.md`,
  the owner's hand or word only.
- **E-204** inherits hazard H2 (§B2) as a named
  candidate, beside the campaign's other cross-part
  residue.

## Slice gate

Focal battery `tests/unit/test_kista_for_users_e104.py`
pins this record: Part A's command road proven live
on a scratch vault (init, the four toaster kinds,
get/list/check/search, the passphrase consequence in
`status`'s own words); the member-wide absence of
the old default's string outside the README the law
reserves; SKILL.md's reconciled identity; the
ENTRY_TYPES partition note; the ARCHITECTURE
meta-mode correction (docket 141); and the boundary
final's needles in this doc and in E-011's appended
addendum. Member suite and root gates are recorded
in the campaign state file at banking; the E-057
member table is re-measured and re-pinned there
with attribution (this slice's member-doc edits
move kista's row; both published copies re-pinned
to the tree).

*Filed by the E-104 slice, 2026-11-02. Next: E-105 —
the naming kindness: user-facing names distinguish
the two Kistas without jargon.*

---

## Naming addendum (E-105) — what to call the two chests

*Appended by the E-105 slice, extending this guide
and never rewriting it. The naming record stands at
`docs/architecture/E-105_NAMING_KINDNESS.md`.*

This guide's chest has a plain name now, and so
does the other one:

- **Ember's Kista** — this one: yours, the chest
  that comes with Ember and lives on your own
  machine at `~/.ember/kista/`. Everything in
  this guide is about Ember's Kista.
- **The house Kista** — the other one: the house
  assistants' own chest, on the house computer,
  under its own keeper. Ember cannot open it,
  fix it, or move anything to or from it.

The one sentence to carry: Ember's Kista is
yours, on your machine; the house Kista is the
house's own, on the house computer; and no entry ever crosses
between them. If anyone
offering help says only "Kista", it is kind —
and expected — to ask which chest they mean.

# E-097 — Per-Program Access: a Program Gets Only Its Own Entries

*Project Ember campaign, Part VI (Kista of the Toaster),
fifth slice. Roadmap line: "Per-program access: a
program gets only its own entries (the ai-folder
Kista's proven pattern, in toaster shape)". Built and
measured 2026-11-01 on branch `yrsa/ember-road-build`
in the campaign's own clone, building on E-096's
working unlock. Method: `kista/scripts/credstore.py`
extended in place; every claim below proven by
sandboxed probes against scratch vaults holding
synthetic entries only (raw logs in
`~/workspace/.verify-tmp/ember-e097/`). The ai-folder
Kista was not accessed, run, or read — the E-011
boundary governs: the *pattern* (a program reaches
its own entries, no one else's) is the house's proven
shape; the *shape built here* is the toaster's own.*

## Headline — read this first, in plain words

**Each entry in the vault now belongs to somebody —
and a program can only reach its own.** In plain
words:

- **Entries carry a name tag.** Every entry now has
  a `program` field saying which program it belongs
  to. No tag — including every entry written before
  today — means the entry is the vault owner's own.
- **A program names itself, and the vault holds it
  to that name.** A program calling the vault says
  who it is with the `KISTA_PROGRAM` environment
  variable. From then on it can add, read, list,
  search, check, change, and remove **only its own
  entries**. Another program's entry and an entry
  that does not exist get exactly the same answer,
  so a program cannot even learn what else the vault
  holds — not the values, not the names, not the
  count.
- **Whole-vault acts stay the owner's.** Exporting,
  backing up, restoring, importing, changing the
  passphrase, repairing, configuring — anything that
  touches the vault as a whole belongs to the owner
  in person, and a program caller is refused, in
  words, before anything is touched.
- **Only the owner can move an entry.** Giving an
  entry to a program (`update --program NAME`) or
  taking it back (`update --unassign-program`) is
  the owner's act. A program cannot give its entries
  away, take another's, or overwrite another's even
  with `--force`.
- **The honest limit, stated up front:** a program
  *name* is an identifier, not a credential — it is
  claimed, never proven. This is the discipline that
  keeps well-behaved programs (the companion first,
  at E-100) inside their own entries, and it stops
  accidents and casual browsing cold. It is **not** a
  wall against malicious code running as the same
  OS account (the same-account neighbour): such code
  could claim any name, or
  read the vault files directly. That was E-095's
  attacker A2, judged NOT defended then; this slice
  does not change that verdict and no Ember document
  may pretend it does.

## 1. How it works

- **The tag.** `add` stamps each new entry with its
  owner: the caller's own name when a program adds,
  or the name given with `--program` when the owner
  adds an entry *for* a program. Program names are
  small and plain — lowercase letters, digits, `.`,
  `_`, `-`, at most 64 characters — and an unusable
  name is refused in words, at the moment it is
  given, whether it arrives by `--program` or by
  `KISTA_PROGRAM`.
- **The caller.** With `KISTA_PROGRAM` unset, the
  caller is the owner personally, and the vault
  behaves exactly as it always has — every existing
  habit, script, and test stands. With it set, every
  entry-facing command works on the caller's visible
  set: for `get`, `update`, and `remove`, an entry
  outside the set answers with the program-scoped
  "not found" (never the owner's available-services
  list); for `list`, `search`, `check`, and
  `status`, the outside entries simply do not exist
  — names, counts, and type tallies are all computed
  inside the set, and `status` withholds the
  whole-vault backup/config counts from a program.
- **Composition with E-096.** The passphrase lock
  and this scoping are two different doors, and both
  hold at once — proven by probe: with a passphrase
  set, a program caller without it is refused at the
  lock; with it, it opens the vault and *still* sees
  only its own entries. The passphrase is the proof
  of the *person*; the program name is the claim of
  the *program*; neither substitutes for the other.
- **No new surface.** No new subcommand was added
  (the mapped surface stands at 34, E-094/E-096);
  the shape is one field, one environment variable,
  two flags on `update`, one flag on `add` and its
  shortcuts. Nothing new to install, nothing new to
  run at idle — the whole cost is a name comparison
  per entry, beneath notice on toaster hardware
  (E-103 still prices the vault as a whole).

## 2. What was proven (probes, synthetic entries only)

Against scratch vaults holding an owner's entry and
an `ember-core` entry:

- The owner still sees everything: both entries
  read whole, both names listed — the pre-E-097
  behaviour is untouched when no program is claimed.
- `ember-core` reads its own entry whole (its
  `program` tag shown); the owner's entry refuses,
  exit 1, no value, no available-services list; a
  missing name answers in the same words.
- A third program (`other-app`) reads neither.
- `list`, `search`, `check`, and `status` under
  `ember-core` show only `progsite`: the owner's
  name appears nowhere, and `status` counts
  **Entries: 1**.
- A program adding an entry stamps it with its own
  name; asking to stamp another program's name is
  refused and nothing is added for anyone.
- A program cannot update, remove, or
  `--force`-overwrite another program's (or the
  owner's) entry; the entry reads back whole and
  unchanged under the owner.
- A program updates and removes its own entry
  freely.
- `export`, `backup`, `config list`,
  `set-passphrase`, and `repair` under a program
  caller all refuse, exit 1, "belongs to the vault
  owner" (the battery asserts the same guard stands
  on `import`, `restore`, `github-backup`,
  `add-soul`, `add-cron-backup`, `init`, and
  `remove-passphrase` in the code).
- The owner reassigns: `update --program other-app`
  moves the entry (the old program loses it, the new
  one reads it); `--unassign-program` makes it the
  owner's own again. The same `update --program`
  from a program caller refuses, and the tag is
  unchanged afterwards.
- An unusable program name (`Bad Name!`) is refused
  from both doors, exit 1, in plain words.
- A legacy entry — its `program` field deleted
  in-process to stand exactly as a pre-E-097 entry
  stands — reads as the owner's own: the owner reads
  it, every program is refused.
- With a passphrase set (E-096): a program caller
  without the passphrase is refused at the lock;
  with it, its own entry opens and the owner's entry
  still refuses — the doors compose.

## 3. Standing findings handed on

- **E-098** inherits the tag: the toaster entry set
  is judged per kind, and the `program` field is not
  an entry kind — it is ownership metadata carried
  by every kind alike. Nothing in this slice adds,
  removes, or renames an entry type (14 stand).
- **E-100** inherits the binding shape: the
  companion will call the vault with
  `KISTA_PROGRAM=ember-core` (or its chosen name)
  and the vault passphrase through E-096's road, and
  it will receive exactly its own entries — that is
  the whole contract this slice built for it.
  Docket 134 (no inter-process lock) stands exactly
  as E-095 left it; this slice's scoping neither
  needs nor claims one.
- **E-103** inherits one more row-fact: the vault's
  cost now includes a per-entry name tag (a handful
  of bytes per entry) and no measurable runtime —
  the price is stated there, not claimed here.
- **E-104** inherits the user words: "an entry
  belongs to a program; a program can only reach
  its own; only you can move an entry between
  programs" — the doc text to carry, plainly.
- **E-187** inherits the honesty line of §headline
  for the security audit: per-program access is a
  discipline boundary inside one OS account, never
  an authentication boundary (E-095's A2 stands).

## Slice gate

Focal battery `tests/unit/test_kista_program_access_e097.py`
pins this record: the tag in the code, the caller
shape, and every probe in §2. Member suite and root
gates are recorded in the campaign state file at
banking; the E-057 member table is re-measured and
re-pinned there with attribution (the credstore's
growth moves kista's row and the twelve-member
total; both published copies re-pinned to the tree).

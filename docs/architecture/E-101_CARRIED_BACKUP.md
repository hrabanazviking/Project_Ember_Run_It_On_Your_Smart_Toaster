# E-101 — Backup & Restore of a Tiny Vault: the User-Carried File

*Project Ember campaign, Part VI (Kista of the Toaster),
ninth slice. Roadmap line: "Backup & restore of a tiny
vault (user-carried file, encrypted; restore proven)".
Built 2026-11-01 on branch `yrsa/ember-road-build` in
the campaign's own clone, carrying docket 135
(`github-backup` history + privacy, from E-095) and
docket 138 (restore's plain road is an unauthenticated
whole-vault transfer between different-key vaults,
from E-099). Method: the movement roads read in code
as E-099 left them, the missing road built into
`kista/scripts/credstore.py`, and every claim below
proven by probes between scratch vaults holding
synthetic entries only (raw logs in
`~/workspace/.verify-tmp/ember-e101/`). No real vault
was touched; the ai-folder Kista was not accessed —
E-099's verdict stands untouched by this slice: what
is built here is one vault's own backup road, not a
bridge between the two Kistas.*

## Headline — read this first, in plain words

**A person can now carry their vault to another
machine in one small encrypted file, and open it
there with a passphrase they chose — nothing else
needed, and nothing else will open it.** Until this
slice, every encrypted backup road demanded the
*same vault key* at the other end (E-099 §1), and no
road may carry the key itself — so "backup" quietly
meant "a copy for this same vault, on this same
machine". The carried file fixes exactly that:

- **`kista backup --carry`** writes the whole vault
  encrypted under a **backup passphrase** the user
  chooses for this backup alone — derived with the
  same scrypt shape E-096 built for the vault
  passphrase (standard library, no new dependency).
  The vault key never leaves home; it is not in the
  file, and the file does not need it.
- **`kista restore <file>`** recognises the carried
  shape, asks for the backup passphrase, and restores
  into whatever vault stands there — a different key,
  a fresh machine, a new folder — proven by
  probe (§3). Right passphrase: the entries arrive
  whole. Wrong passphrase, or none given: a plain
  refusal, and the destination holds **nothing**.
- **A forgotten backup passphrase means a lost
  backup** — stated in the program's own words
  *before* the passphrase is chosen, exactly as
  E-096 states it for the vault. The vault at home
  is untouched by that loss; only the carried copy
  is gone. That is the protection working as
  promised, and no Ember document may imply a
  recovery copy exists.

Two judgements ride with the build, both inherited
as dockets and both **CLOSED in scope** here:

- **Docket 138 — the plain road is gated.** A plain
  (unencrypted) backup restore no longer happens
  silently: without `--allow-plaintext` it is
  refused in plain words (§4); with that flag, a
  loud warning prints *before* anything is restored.
- **Docket 135 — `github-backup` names its price.**
  Before it writes anything, it now states in plain
  words that pushed backups live in the repository's
  history, that every one opens under the vault's
  one key, and that the program cannot check whether
  the repository is private (§5). Its staging file
  is owner-only (0600) from this slice.

## 1. The roads as E-099 left them

E-099 §1's table stands as the before-picture:
`export` (a byte-copy of the vault blob, same key or
nothing), `backup --encrypt` (the whole vault under
the vault key — same wall), `backup` plain (clear
text, keyless, the forbidden road), `github-backup`
(the same-key blob pushed into git history). Not
one of them answers the question a normal person
actually asks: *"my old machine is dying — how do I
take my passwords to the new one?"* The honest
answer before this slice was "you cannot, unless
you also hand-carry the key file" — and handing
over the key file hands over the vault's whole
life, past and future (E-099 §1). That gap is the
slice.

## 2. What was built

All in `kista/scripts/credstore.py`; no new
subcommand (the surface stays 35, E-098's count):

- **The carried format.** A small JSON envelope:
  `{"kista_carry_backup": 1, "kdf": "scrypt", "n", "r",
  "p", "salt", "encrypted"}` — KDF parameters and a
  fresh 16-byte salt in the clear, the whole export
  envelope (version, timestamp, platform, vault) as
  one Fernet token under the derived key. Mode 0600
  on disk, written atomically like the vault itself.
- **The passphrase road.** The backup passphrase
  arrives only by the `KISTA_BACKUP_PASSPHRASE`
  environment variable or a hidden terminal prompt
  (asked twice when creating, with the recovery
  truth stated first) — never from a command-line
  argument, where process listings and shell history
  would keep it (the docket 128 rule, applied to
  this secret too). Minimum length as E-096's: 8.
  No passphrase available is a plain refusal that
  changes nothing, in either direction.
- **Restore recognises the shape.** `restore` reads
  the file once and routes by what it is: carried
  envelope → the passphrase road above; plain JSON →
  the docket 138 gate (§4); anything else → the
  vault-key encrypted shape, exactly as before.
  Merge behaviour is unchanged everywhere: existing
  entries are skipped by default, `--merge` fills
  blanks, `--overwrite` replaces — the conservative
  defaults E-095 affirmed.
- **Whole-vault custody unchanged.** `backup` and
  `restore` remain owner's acts under E-097: a
  program caller (`KISTA_PROGRAM` set) is refused
  before anything is touched, carried shape included.

## 3. What was proven (probes, synthetic entries only)

Scratch vault **A** (its own key; three synthetic
entries — a credential, an apikey, a note) and
scratch vault **B** (a *different* key, proven
different in the probe). Full log in
`~/workspace/.verify-tmp/ember-e101/probes.log` and
the focal battery, which re-runs every probe:

- **The file holds nothing readable.** A's carried
  file contains neither the synthetic password nor
  the synthetic token in clear text, and does not
  contain A's vault key; it parses as the §2
  envelope and stands at mode 0600.
- **Restore proven across keys.** B restores A's
  carried file on the passphrase alone:
  "Restored 3 new", and both the credential and the
  apikey read back whole under B's own different
  key. This is the slice's headline proof — the
  user-carried file, encrypted, restored.
- **A copied file without its passphrase opens nothing.**
  With a wrong passphrase, B's restore
  exits 1 in the program's own words ("That backup
  passphrase did not open this file") and B holds
  nothing afterwards. With no passphrase available
  (no environment value, no terminal), restore
  exits 1 having changed nothing.
- **The plain road is gated (docket 138).** B's
  restore of A's plain backup without
  `--allow-plaintext` exits 1, naming the shape and
  the flag, and B holds nothing. With the flag, the
  warning prints first and the restore completes —
  the owner's explicit word, on the record, every
  time.
- **The github warning fires (docket 135).** A
  `github-backup` run against a synthetic repository
  address prints the §5 words before it writes
  anything.

## 4. Docket 138 — CLOSED in scope

E-099 found the plain road to be, mechanically, an
unauthenticated whole-vault transfer between
different-key vaults: anyone's plain file, restored
silently, its entries entering under the restoring
vault's key with no mark of where they came from —
and, the other side of the same coin, anyone who
ever held the file could read *and change* every
entry in it. The gate built here keeps the road
(it is the owner's own file, and E-095 already
judged the *writing* of a plain backup a deliberate
act) and ends the silence: the refusal states what
the file is, what restoring it would do, and the
exact command that gives the word; the word itself
prints the warning before the merge, not after.
The E-099 battery's plain-road probe is re-pinned
consciously at this slice to the new shape — refusal
first, then the flagged crossing — with its reason
recorded in that battery; E-099's *finding* stands
exactly as filed, and this slice is its remedy.
(The E-089 canon guard needed no new allowlist entry
at this slice: this slice's battery carries no
householder name — checked, not assumed.)

## 5. Docket 135 — CLOSED in scope

E-095 §3.5's harvest shape cannot be removed while
`github-backup` exists: git history keeps every
pushed blob, and every blob opens under the one
vault key, so a future key leak opens the vault's
whole pushed history. What a program owes its
person, then, is the truth **at the moment of use,
before anything is written** — and that is what is
built: every `github-backup` run first prints that
history keeps the copies, that the one key opens
them all, that the program cannot check whether
the repository is private and only a private
repository of the owner's is a fit home, and that
the working copy kept on this machine (under
`github_tmp/`) holds the same history. The staging
file it writes is owner-only from this slice. The
carried file (§2) is named in that warning as the
safer road for a backup a person carries
themselves. No Ember document may describe
`github-backup` as safe beyond the safety of the
vault key itself — E-187 inherits that line.

## 6. Standing findings handed on

- **E-102** inherits a working carried road for its
  drills: a carried file with a wrong passphrase
  and a tampered carried envelope are this slice's
  shapes to drill beside the vault's own (the
  tamper case is already Fernet's HMAC refusal —
  the same "did not open" words — but E-102 proves
  it as a drill, not an inference).
- **E-103** prices the carried road for the budget
  book: one scrypt derivation at each end (the
  E-096 cost shape) plus one small file — measured
  there, not claimed here.
- **E-104** writes the user docs against this
  slice's four toaster kinds and this road: the
  plain words for a normal person are "the file you
  carry" and "the passphrase for that file", kept
  apart — and the boundary doc's final form records
  that this road moves a vault's *own* backup, never
  an entry between the two Kistas (E-099).
- **E-105** inherits the naming consequence: the
  backup passphrase and the vault passphrase are
  different secrets with different jobs, and
  user-facing words must never blur them.
- **E-187** inherits §5's honesty line for
  `github-backup` and §4's gate as the plain road's
  standing shape.

## Slice gate

Focal battery `tests/unit/test_kista_carry_backup_e101.py`
pins this record: the carried format and its
passphrase road in code (scrypt derivation, no
vault key, no command-line passphrase shape), the
plain-restore gate, the github warning, and the §3
probes re-run — file holds no plaintext and no key,
restore proven into a different-key vault, wrong
and absent passphrases restoring nothing, the plain
road refused then warned, the github warning firing
before any write. Consciously re-pinned at this
slice, with attribution: the E-099 battery's
plain-road probe (the gate is docket 138's remedy,
which that battery itself handed here). The E-057 member
table is re-measured at banking (the kista member
grows by this slice's code); member suite and root
gates are recorded in the campaign state file.

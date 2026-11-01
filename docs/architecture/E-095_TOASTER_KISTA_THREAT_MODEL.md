# E-095 — Toaster-Kista Threat Model, Sized for Tiny Machines

*Project Ember campaign, Part VI (Kista of the Toaster),
third slice. Roadmap line: "Threat model sized for tiny
machines: what it defends, what it cannot (stated, never
implied otherwise)", judging the shape E-094 mapped:
key-file custody, no vault passphrase, plaintext
service-name meta, the github-backup and movement
shapes. Measured and written 2026-11-01 on branch
`yrsa/ember-road-build` in the campaign's own clone, at
campaign commit 47e162f (E-095 IN PROGRESS). Method:
`kista/scripts/credstore.py` re-read whole against
E-094's map, then every load-bearing claim below proven
by a sandboxed probe against a scratch vault holding
one synthetic entry (raw log in
`~/workspace/.verify-tmp/ember-e095/probes.log`; the
pre-fix permission figures were measured the same way
at this slice's opening, before §5's fixes). The
ai-folder Kista was not accessed, run, or read — the
E-011 boundary governs: this model is of the toaster
program in this tree, and of nothing else.*

## Headline — read this first, in plain words

**The toaster-Kista's encryption is real, but today it
protects the vault file, not the vault.** In plain
words:

- **What it defends, proven:** a copy of the encrypted
  vault file *on its own* — an export file, a
  github-backup blob, a stray auto-backup — gives an
  attacker nothing. The cipher is sound, tampering
  with the blob is detected, a crash mid-save cannot
  leave a half-written vault, and the program refuses
  to mint a new key over existing data (§2).
- **What it cannot defend, proven:** the device
  itself. The key is a file sitting in the same folder
  as the vault, readable by the same owner account.
  Whoever copies the *folder* — a stolen toaster, a
  pulled SD card, a synced or backed-up home directory,
  malware running as the user, a family member on the
  shared account — has everything, and the probe in §3
  shows the copied folder opening with no prompt of
  any kind. There is no passphrase, so there is nothing
  an attacker needs to know, guess, or steal beyond
  the files themselves.
- **The verdict handed to E-096:** the unlock
  experience is not a comfort feature; it is the
  missing half of the encryption. Until a passphrase
  stands between a copied folder and its contents,
  Ember may honestly claim "your vault file is
  encrypted" and must never claim "your credentials
  are safe if your device is taken." §6 states the
  requirement and the interim claim, word for word.
- **Two leaks this model found are fixed in this
  slice** (§5): the plaintext metadata file and the
  plaintext-backup file were written with no
  permission tightening at all — readable by whoever
  the machine's default sharing allowed — and the
  vault directory itself was never made owner-only.
  All three are owner-only now, proven by probe.

## 1. The attackers, sized for tiny machines

A toaster-class machine is not a data centre and is
not a phone with a secure enclave. The model assumes:
no TPM, no hardware key store, storage that can be
physically removed (an SD card, a cheap SSD), one
device often shared by a household, and an owner who
is not a system administrator. Against that reality,
the attackers that matter, in the order a tiny
machine actually meets them:

| # | Attacker | What they can reach |
|---|---|---|
| A1 | **The folder copier** — device or card stolen, lost, sold, repaired; home folder synced or backed up somewhere the owner forgot | The whole vault directory, as files |
| A2 | **The same-account neighbour** — another person or program running as the same OS user (the shared-family-account case) | Anything the owner account can read or run |
| A3 | **The other account** — a different OS user on the same machine, or a network share reader | Whatever file permissions leave open |
| A4 | **The blob holder** — someone who obtains one encrypted file alone (export, github history, an auto-backup) | That file, without the key |
| A5 | **The tamperer** — someone who can write or replace files but is never seen doing it (a bad sync, a meddling program) | The vault and backup files' contents |
| A6 | **The future key-leaker's customer** — someone who archives encrypted blobs today, waiting for a key to leak later | Every historical blob ever pushed or exported |
| A7 | **The owner themselves** — the most likely attacker of all: forgets, deletes, loses the only key | Availability of their own credentials |

Out of scope, stated so nobody inflates the model: a
nation-state, a compromised operating system kernel,
or an attacker watching the owner's screen while they
work. A program of this size cannot answer those, and
this document does not pretend otherwise.

## 2. What it defends — proven

- **A4, the blob alone: defended.** The vault is one
  Fernet blob (AES-128-CBC + HMAC-SHA256, E-094 §2)
  under a random 32-byte key. The probe copied
  `vault.json.enc` alone into a fresh directory: the
  program refused — key missing over existing data is
  a stated refusal, exit 1, and no new key is minted.
  The same refusal shape guards imports encrypted
  under a different key. Brute force against a random
  32-byte key is not a road; there is no password to
  dictionary-attack because there is no passphrase at
  all (the double edge of that fact is §3).
- **A5, silent tampering with the blob: detected.**
  The probe appended one byte to the vault file: the
  blob no longer decrypts (the HMAC does its work),
  and the program restored the entry from the newest
  valid auto-backup rather than serving altered data.
  A crash or partial write is answered the same way
  by construction: saves are atomic (temp file +
  `os.replace`), and the last five encrypted states
  are kept.
- **A3, the other account, for values: defended.**
  The key file, the vault file, the config, and every
  auto-backup are written mode 0600 (probe-verified);
  on a POSIX machine a different OS account can read
  none of them. (For *names*, this was not true when
  this slice opened — §5.)
- **Honest small defences, recorded:** generated
  passwords come from the operating system's CSPRNG
  (`secrets.choice`); a truncated or corrupt key file
  is refused with "your data is intact — do not
  regenerate" rather than silently replaced; a save's
  auto-backup failure can never crash the vault.

## 3. What it cannot defend — stated, never implied otherwise

1. **A1, the folder copy: NOT defended — the central
   finding.** Key and vault live in one directory,
   both readable by the owner account, and no
   passphrase stands anywhere in the design. The
   probe copied the whole vault directory to a new
   location and read the synthetic entry back in
   full, password included, with no prompt. Every
   realistic tiny-machine loss — theft, a pulled SD
   card, a cloud sync of the home folder, a backup
   the owner forgot they made — is this attacker.
   Fernet contributes nothing here: encryption whose
   key travels with the ciphertext is a lock whose
   key is taped to the door. This shape is defensible
   only behind compensations the program does not
   provide or check: full-disk encryption, per-person
   OS accounts, a device that never leaves the house.
   §6 hands the fix to its owner.
2. **A2, the same account: NOT defended.** The
   program has no unlock gate at all: any process or
   person running as the owner can run `get` and
   receive plaintext. Per-program access (a program
   gets only its own entries) does not exist yet —
   it is E-097's build, and until then "the companion
   can read the vault" and "anything running as you
   can read the vault" are the same sentence. Screen
   and output exposure ride with this: `get` prints
   the whole entry, secrets included, to standard
   output — terminal scrollback, captured logs, and
   shoulder-surfing are all plaintext channels the
   program makes no attempt to narrow.
3. **A7, the owner: NOT defended, by design, and the
   recovery story must say so.** Lose the key file
   and the vault is permanently unreadable — the
   program says exactly that and offers no recovery,
   because there is none. Delete the folder and the
   last five auto-backups die with it; they are
   neighbours, not a backup strategy. E-096 owns
   stating this to normal folks before it happens to
   them; E-101 owns the carried-file answer.
4. **Rollback: NOT defended (docket 133).** Nothing
   checks freshness. The probe rotated the synthetic
   entry's password, then replaced the vault file
   with the oldest auto-backup: the program served
   the rotated-away password with no warning. An A5
   tamperer — or an innocent stale sync — can
   therefore resurrect removed entries and un-rotate
   rotated credentials, and the self-healing road
   (§2) will happily "repair" a vault to an older
   state, because a backup's name order is all it
   consults. Detection of tampering exists; detection
   of *old* does not.
5. **A6, harvest-now-decrypt-later, on the
   github-backup shape: NOT defended (docket 135).**
   Each github-backup pushes a fresh timestamped blob
   into a git repository, where history keeps every
   one forever. Every blob is encrypted under the
   same vault key, so one future key leak decrypts
   the vault's whole pushed history, not just its
   present state. The program also never checks —
   and never warns — whether the configured backup
   repository is public. The shape is safe exactly as
   long as the key is, and the key is one file (§3.1).
6. **The plaintext shapes are the weakest doors in
   the house.** `backup` without `--encrypt` writes
   the entire vault as readable JSON; before this
   slice it did so with no permission tightening at
   all (§5 fixes the mode; the shape remains a
   deliberate act whose warning prints only after the
   file exists), and `restore` accepts a plaintext
   backup with no warning at all. An owner who once
   ran the plain shape and forgot the file has an
   unencrypted vault copy wherever it landed.
7. **Entry-password command-line values (docket 128,
   already E-096's):** a value typed after
   `--password` is visible in process listings and
   shell history while it is used. The custody law
   (E-093 rule 7) already forbids campaign use; the
   threat model records the exposure as designed-in
   until E-096's remedy.
8. **Platform limit, stated:** the mode-0600 defence
   is POSIX. The program's own chmod helper swallows
   failure "cross-platform safe", so on a platform
   where chmod is a no-op the files' protection is
   whatever the profile's default ACLs happen to be —
   the program neither checks nor says so
   (docket 136 → E-187's platform audit).
9. **No inter-process lock (docket 134).** Two
   writers at once share one predictable temp-file
   name and no lock of any kind; today the program is
   a single-user CLI and the race is theoretical, but
   E-100's core binding makes a second writer real.
   The lock's shape belongs to E-100; E-102 drills it.

## 4. The movement shapes, judged one by one

- **export** — a copy of the encrypted blob, mode
  0600 at its destination. Safe to carry *as a blob*
  (A4); useless for moving to a new machine, because
  import demands the same key and no shape in the
  program moves the key with any protection at all.
  The honest summary: export moves the lock, never
  the key, and says neither.
- **import / restore** — same-key only for encrypted
  input (refused plainly otherwise); plaintext
  restore accepted silently (§3.6). Merge defaults
  are conservative (skip existing; overwrite only on
  an explicit flag) — a sound default this model
  affirms.
- **backup** — the encrypted shape re-uses the vault
  key (an A4-safe blob); the plain shape is §3.6.
  E-101 builds the user-carried file properly; this
  model hands it §3.5's history warning and §3.6's
  plaintext warning as requirements, not surprises.
- **github-backup** — judged at §3.5. Additionally:
  its staging clone lives on inside the vault
  directory (`github_tmp/repo`), carrying the pushed
  history on disk — encrypted blobs, but the full
  history, kept by default and never mentioned.

## 5. Fixed in this slice — dockets 131 and 132 CLOSED

The model found the metadata and directory shapes
leaking to A3 — not values, but the service-name map
the custody law's rule 9 treats as sensitive:

- **Before (measured at this slice's opening, VM
  umask 0007):** the vault directory stood at mode
  770 — group-traversable, a mode the program never
  chose, inherited from the umask — and
  `vault_meta.json` (service names, entry count,
  timestamps, in plaintext) at 660, group-readable.
  Under a common 022 umask both would be
  world-readable. The plaintext-backup file stood at
  660 the same way.
- **Docket 131 — the directory and the meta.**
  `_ensure_dir` now makes the vault directory
  owner-only (0700, failure swallowed exactly as the
  existing chmod helper swallows it, so no platform
  regresses), and every save now chmods the metadata
  file 0600 like every other vault file.
- **Docket 132 — the plaintext backup's mode.** The
  plain `backup` shape now chmods its output 0600
  too: plaintext by the caller's explicit choice,
  never loose on disk by default.
- **After (probe-verified, probes.log):** directory
  700, meta 600, plaintext backup 600; key, vault,
  and auto-backups 600 as before. The member suite
  and the E-057 re-pin are recorded in the campaign
  state file at banking (kista 25 files / 2,770,819 B;
  twelve-member total 131,547,523 B; laptop miss
  unchanged 256,017 B).

## 6. The requirement handed to E-096, and the interim claim

**Requirement (judged here, built there):** the vault
must gain a passphrase that stands between a copied
folder and its contents — in practice, the key file
wrapped under a passphrase-derived key, so A1's copy
yields a blob and a wrapped key and nothing else.
The sizing says this is affordable on the smallest
machine: key derivation is a one-time cost at unlock,
measured in a fraction of a second even on
toaster-class hardware, and zero at every other
moment; E-103 will price whatever E-096 builds.
E-096 also inherits, already docketed to it: docket
128 (the `--password` value shape), docket 14 (the
import-time pip install — a first-run program that
executes an installer from the network at import is
both a supply-chain exposure and, as this slice's
own opening probe re-proved, a raw-traceback failure
on a PEP 668 machine), and §3.3's recovery honesty:
a forgotten passphrase with no recovery copy means a
lost vault, and normal folks must hear that *before*,
in plain words, not after.

**The interim claim, word for word, binding on every
Ember document until E-096 lands:** the toaster-Kista
keeps credentials in an encrypted vault file,
protected from other accounts on the same machine
and from anyone who obtains the vault file alone. It
does **not** protect them against loss or theft of
the device or a copy of its folders, and no Ember
document may say or imply that it does.

## 7. Standing findings this model hands on

- **Docket 133 — NEW → E-102.** Rollback and
  resurrection (§3.4): no freshness check anywhere;
  the tamper drills are E-102's charter, and a
  monotonic counter or equivalent freshness shape is
  the candidate remedy it weighs. The drills also
  inherit a wrinkle this slice's battery caught:
  auto-backup filenames are second-resolution, so
  two saves inside one second share one backup name
  and the "last five states" can be fewer than five
  distinct states.
- **Docket 134 — NEW → E-100 (drill at E-102).** No
  inter-process lock; one shared predictable temp
  name (§3.9). The binding slice makes the second
  writer real, so the lock is
...[truncated 2007 chars]
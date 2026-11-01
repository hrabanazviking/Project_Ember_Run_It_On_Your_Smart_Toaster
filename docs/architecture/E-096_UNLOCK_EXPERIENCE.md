# E-096 — The Unlock Experience for Normal Folks

*Project Ember campaign, Part VI (Kista of the Toaster),
fourth slice. Roadmap line: "The unlock experience for
normal folks: passphrase flow a non-technical user
survives; recovery story stated honestly", carrying
E-095's judged requirement — a passphrase wrapping the
key — plus docket 128 (the `--password` command-line
value shape) and docket 14 (the import-time pip
install). Built and measured 2026-11-01 on branch
`yrsa/ember-road-build` in the campaign's own clone, at
campaign commit 9bdb92c (E-096 IN PROGRESS). Method:
`kista/scripts/credstore.py` extended in place; every
claim below proven by sandboxed probes against scratch
vaults holding one synthetic entry (raw logs in
`~/workspace/.verify-tmp/ember-e096/probes.log` and
`probes2.log`). The ai-folder Kista was not accessed,
run, or read — the E-011 boundary governs.*

## Headline — read this first, in plain words

**The vault now has a lock you hold in your head.**
In plain words:

- **Setting a passphrase takes one command** —
  `kista set-passphrase` — and one honest warning,
  given *before* anything is set: if you forget the
  passphrase, nobody can open your vault. Not you,
  not Ember, not anyone. There is no reset, no
  recovery copy, no back door. That is not a scare
  tactic; it is what makes the protection real, and
  the program says it in those words at the moment
  of choosing, not after something goes wrong.
- **A copied folder is now a locked box.** E-095's
  central finding — copy the vault folder, open
  everything, no prompt — is answered for any vault
  whose owner sets a passphrase. The probes below
  copied a protected vault's folder and tried three
  ways: with no passphrase (refused, plainly, nothing
  shown), with a wrong passphrase (refused, plainly,
  nothing shown), and with the right one (opened,
  entry intact).
- **Nothing else changed under your feet.** The
  vault key itself never changes when a passphrase
  is set, changed, or removed — only its wrapping
  does. Entries, auto-backups, and exports work
  exactly as before; a passphrase can be removed
  again (`kista remove-passphrase`), with its
  consequence stated before the act.
- **A vault with no passphrase still opens the old
  way — and now says so.** Protection is a choice
  the owner makes, so the program states the choice
  at the moments it matters: `init` prints that a
  new vault has no passphrase and what that means,
  and `status` reports SET or NOT set, with the
  consequence in words either way. Silence about an
  unprotected vault is what ended; the unwrapped
  shape itself remains, deliberately, for owners
  who rely on a locked-down machine instead.

## 1. How the lock works

- The key file gains a wrapped shape: a small JSON
  document (`kista_key_wrap: 1`) holding a random
  16-byte salt, the scrypt parameters, and the vault
  key encrypted under a key derived from the
  passphrase. Derivation is `hashlib.scrypt`
  (n=16384, r=8, p=1) from the Python standard
  library — **no new dependency**, and the one-time
  cost is paid once per command run, at unlock;
  E-103 prices it on the toaster profile. Unwrapping
  is attempted at most three times interactively;
  the unwrapped key is cached in memory for that
  process only and never written anywhere.
- Reading the passphrase never echoes and never
  uses a command-line shape: a hidden terminal
  prompt (`getpass`), or the `KISTA_PASSPHRASE`
  environment variable for scripts and for the
  companion's binding (E-100's road). With neither
  available, the refusal is one plain paragraph —
  what happened, what to do, "nothing was changed" —
  never a traceback.
- A wrong passphrase can never trigger the vault's
  self-healing or key-regeneration roads: unlocking
  fails before any vault data is touched, and the
  wrapped file is left byte-for-byte as it was.
- New passphrases must be at least 8 characters,
  typed twice at a terminal, with the guidance that
  a short sentence you can remember works well.
  A too-short or mismatched attempt changes nothing.

## 2. The recovery story, stated honestly

There is no recovery. That sentence is the whole
story, and the program tells it at three moments:

1. **Before setting** (`set-passphrase` opens with
   it): forget this, and the vault is lost — write
   it down somewhere safe, the way you would a
   house key's hiding place.
2. **At creation** (`init` on an unprotected
   vault): a forgotten passphrase means a lost
   vault, with no recovery — stated in the same
   breath that offers the protection.
3. **After three failed tries**: the vault stayed
   locked, nothing was changed, and if the
   passphrase is forgotten the vault cannot be
   opened — "that is the protection working as
   promised."

What a forgotten passphrase does *not* lose: the
encrypted vault file itself is untouched, so an
owner who later remembers — or finds the written
copy — opens everything as it was. What it does
lose, forever, is any road in that does not pass
through the passphrase. E-101's carried-file backup
is the place a *separate* recovery copy could one
day live; until then, no Ember document may imply
one exists. The E-095 interim claim is therefore
superseded for protected vaults, and the honest
claim from this slice on is: **a vault with a
passphrase set keeps its credentials from anyone
who copies its folder, and from anyone who does
not know the passphrase — and its owner is the
only recovery there is.**

## 3. Docket 14 — CLOSED (no installer at import)

The credstore's first act on a machine without its
one dependency used to be running an installer from
the network — a supply-chain exposure that also
died as a raw `CalledProcessError` traceback on
PEP 668 machines (live-reproduced at E-094). That
shape is gone entirely: a missing `cryptography`
package is now one plain message — what is needed,
who can install it, and "nothing was changed, and
your vault — if you have one — is untouched" —
and a clean exit. The member suite's
`TestSubprocessInstall`, which pinned the installer
shape, was re-pinned consciously in this slice to
pin the new one: no `os.system`, no installer
invocation of any shape, the plain message present.

## 4. Docket 128 — CLOSED (the `--password` value)

A password typed after `--password` (on `add` and
`update`) was visible in process listings and shell
history while the program said nothing. The value
is still honoured — existing scripts keep working —
but the silence ended: at the moment of use the
program prints a loud, plain warning to stderr
naming the exposure and the safer shapes
(`--password-file`, `--password-env`, or no flag
and the hidden prompt). The help texts for both
flags now say "discouraged" with the reason,
instead of the old soft "insecure" aside. The
probe proves the warning fires and the update
still lands.

## 5. What was proven (probes, synthetic entries only)

From `probes.log` / `probes2.log`, scratch homes:

- `init` on a fresh vault prints the NOT-set warning
  with the `set-passphrase` road and the recovery
  truth; `status` reports NOT set with its
  consequence in words.
- `set-passphrase` (scripted shape) prints the
  recovery warning *before* confirming; the key
  file becomes the wrapped JSON shape, mode 600.
- A copied protected folder: no passphrase →
  exit 1, plain refusal, no entry data; wrong
  passphrase → exit 1, "did not unlock", no data;
  right passphrase → the entry reads back whole.
- Wrapping is transparent to the data: the entry
  added before wrapping reads identically after,
  and after `remove-passphrase` (whose consequence
  text prints before its confirmation).
- A 5-character passphrase is refused (exit 1) and
  the vault is unchanged — it still opens unwrapped.
- `update --password` prints the docket-128 warning
  and the new value lands.

## 6. Batteries re-pinned in this slice, consciously

- `kista/tests/test_credstore.py` —
  `TestSubprocessInstall` (see §3).
- `tests/unit/test_toaster_kista_map_e094.py` — the
  mapped surface grows 32 → 34 subcommands
  (`set-passphrase`, `remove-passphrase`); E-094's
  record stands as written, the battery pins the
  tree as it now is.
- `tests/unit/test_kista_threat_model_e095.py` —
  the "no derivation anywhere" pin is inverted with
  attribution: that absence was E-095's requirement
  to this slice, and this slice built it. The
  folder-copy probe stands: it describes a vault
  with no passphrase set, whose consequence init
  and status now state in words.
- E-057's member table is re-measured at banking:
  the credstore's growth moves kista's row, and
  both published copies are re-pinned to the tree.

## 7. Standing findings handed on

- **E-097** inherits a working unlock: per-program
  access builds on a vault that can now be locked;
  how a program is *given* the passphrase (never in
  a config, per E-093) is that slice's question.
- **E-100** inherits the binding shape: the
  companion unlocks through `KISTA_PASSPHRASE` or a
  prompt, and the no-lock gap (docket 134) and the
  rollback gap (docket 133, E-102) stand exactly
  as E-095 left them.
- **E-103** prices the unlock: one scrypt
  derivation per command run on the toaster
  profile; nothing in this slice claims a figure.
- **E-104** inherits the user docs: the passphrase
  flow, the recovery story above, and the SET /
  NOT-set wording are the text to carry, plainly.

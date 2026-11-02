# E-102 — Audit Fixtures: the Drills

*Part VI — Kista of the Toaster. The audit slice: the
failure shapes the threat model (E-095) named, the unlock
(E-096) and the binding (E-100) built against, and the
carried file (E-101) created — each one drilled against
a scratch vault, so the claims the program makes are
the behaviours it was measured doing, not the behaviours
its code looks like it should do.*

## Headline — read this first, in plain words

A vault program earns trust in its bad moments, not its
good ones. This slice is the bad moments, one by one,
each forced on a scratch vault holding only synthetic
entries, each answered by the program itself:

- **Wrong passphrase:** refused, in plain words, and
  every file in the vault is left byte-for-byte as it
  was. Nothing leaks, nothing changes.
- **A tampered vault:** the damage is caught — a flipped
  byte cannot pass the encryption's own integrity check
  — and the vault heals itself from its newest automatic
  backup, serving its entries whole. If the backups are
  gone too, the answer is a plain refusal: no data is
  invented, no new key is minted over the damage, and
  the damaged file is left standing for the owner.
- **A half-finished write (the partial-write shapes):**
  a vault file cut in half answers exactly like the
  tampered one; the torn-off leftover of a crashed save
  is simply ignored, because real saves land whole or
  not at all; and a torn key file — the shape that used
  to meet the user with a wall of error code — now gets
  one plain sentence saying the data is still intact
  and the key must not be regenerated (that repair is
  docket 139, below, found by these very drills).
- **A tampered carried envelope:** E-101's carried file,
  attacked three ways — a flipped character, a torn
  salt, a file cut in half — refuses three stated ways,
  and the destination vault holds nothing afterwards,
  every time.
- **Two writers at once:** the write lock E-100 built
  holds. A second writer waits until the first lets go,
  then lands whole; two writers racing both land. No
  lost update.
- **One shape still does not hold, and this record says
  so in the same size type as the rest:** roll the vault
  back to an older copy of itself and the old passwords
  come back with it, silently. That is docket 133,
  weighed in §4 and **not defended** — its verdict goes
  forward to the Part VI gate (E-106) in exactly those
  words, because no lock kept inside the same folder as
  the vault can honestly promise otherwise.

## 1. The charter

Three earlier slices handed this one its drill list:

- **E-095 §7** — the tamper drills are E-102's charter:
  wrong-passphrase, tampered-vault, and the rollback
  question (docket 133), with the candidate freshness
  remedy to be *weighed* here. The same section handed
  over a wrinkle its battery caught: auto-backup names
  are second-resolution, so two saves inside one second
  share one backup name and the "last five states" can
  be fewer than five distinct states. That wrinkle
  stands as recorded there; the drills below neither
  worsen nor hide it — the healing drill consults the
  newest backup by name order, exactly as the model
  described.
- **E-100 §2** — the write lock (docket 134, closed
  there in scope) was built for a second writer the
  core binding made real; its harder drills — a holder
  process, racing writers — were expressly left here.
- **E-101 §6** — the carried envelope's tamper case was
  proven by inference there ("the same refusal, by the
  same mechanism"); this slice proves it as a drill.

No new command, no new dependency, no new file format:
the surface stays 35 subcommands, the library stays
the standard library plus the member's one declared
dependency. The only program code this slice changes
is the docket-139 repair in §3.

## 2. The drills, and what the program did

All drills run as the slice battery
(`tests/unit/test_kista_audit_drills_e102.py`) against
scratch vaults with synthetic entries only — the
custody discipline every Part VI slice has worked
under. Measured at this slice's gate, on the VM:

| Drill | Forced shape | The program's answer |
|---|---|---|
| Wrong-passphrase | wrapped vault, wrong `KISTA_PASSPHRASE` | exit 1, "did not unlock"; every vault file byte-identical after |
| Tampered-vault, backups present | one byte flipped mid-blob | corruption named, auto-repair from the newest backup, entry served whole |
| Tampered-vault, no backups | one byte flipped, backups removed | exit 1, "Cannot decrypt vault"; damaged blob and key left exactly as they stood |
| Partial-write vault | blob truncated to half | the same plain refusal (no backups), the same healing (with them) |
| Partial-write save | a crashed save's `*.tmp` leftover beside the vault | ignored; the last whole state served; the next save lands normally |
| Partial-write key | key file truncated to 20 bytes, emptied to 0, or a wrapped key torn in half | exit 1, "Invalid vault key … do NOT regenerate the key"; no traceback; the damaged file left as it stands (§3) |
| Carried envelope, flipped token | one character changed in the carried file's encrypted token | exit 1, "did not open this file"; destination holds nothing |
| Carried envelope, torn salt | the envelope's salt replaced with non-base64 text | exit 1, "this carried backup file is damaged"; destination holds nothing |
| Carried envelope, half-written | the carried file truncated to half | exit 1, "Cannot read backup file"; no traceback; destination holds nothing |
| Lock drill | a holder process holds the vault's `flock`; a writer starts | the writer is still waiting after 2 s; when the holder lets go (5 s) the writer lands whole, exit 0 |
| Racing writers | two `add` processes at once | both exit 0; both entries present — no lost update |
| Rollback drill | the vault blob replaced with a pre-rotation snapshot | the rotated-away password is served, with no warning (§4) |

## 3. Docket 139 — NEW → CLOSED in scope (found by these drills)

The partial-write key drill failed first, and it failed
ugly: a truncated key file (20 of 44 bytes) met every
key-loading command with a **raw Python traceback** —
`ValueError: Invalid vault key: expected 44 bytes …` —
the validator's well-written words delivered as a crash
dump. An emptied key file and a torn wrapped-key file
did the same. For the corrupt-*vault* shapes the member
suite's own BUG-ERR-01 class has demanded "actionable
messages, not raw traceback" since long before this
campaign; the key shapes simply never got the same
treatment, because `_get_key` let the validator's
exception escape.

**The fix, in scope:** a `_validate_key_or_exit` wrapper
in `kista/scripts/credstore.py` — the validator's verdict,
delivered as the program's plain refusal (its own words
on stderr, exit 1). Every key-loading road now goes
through it: `_get_key` (all commands), `_unwrap_key`
(the unwrapped result of a passphrase unlock), and
`set-passphrase`'s unwrapped branch. `_validate_key`
itself is untouched — it still raises, for callers that
want the exception; the command roads no longer leak it.
Nothing is regenerated and nothing is "helpfully"
repaired: the damaged file is left exactly as it stands,
which is what the validator's words themselves advise.

**Conscious re-pins, with attribution:** the member
suite's two key-validation tests
(`TestKeyValidation::test_truncated_key_rejected`,
`test_empty_key_rejected`) pinned the old shape —
`_get_key()` raising `ValueError`. They are re-pinned
in place to the new shape — `SystemExit`, with
"Invalid vault key" proven on stderr — each carrying a
note naming this docket and the reason: the rejection
and its actionable message stand; only their delivery
shape changed, from traceback to stated refusal. The
member suite stands at 149 passed / 0 failed, as at
E-101.

**Budget consequence:** the wrapper and the re-pin notes
grew the member — E-057 re-measured at this slice:
kista 25 files / 2,820,119 B, the twelve-member total
131,612,827 bytes, the laptop miss unchanged (both
published copies of the table re-pinned).

## 4. Docket 133 — weighed, and NOT closed: rollback

The rollback drill re-proves E-095 §3.4 exactly: rotate
an entry's password, replace the vault file with the
snapshot taken before the rotation, and the program
serves the rotated-away password with no warning at
all. Removed entries resurrect the same way. Detection
of *damage* exists (the HMAC catches any flipped byte);
detection of *old* does not.

E-095 handed this slice the candidate remedy to weigh:
a monotonic counter or equivalent freshness shape.
Weighed honestly, every in-folder shape fails its own
claim:

- **A counter inside the vault** rolls back with the
  vault — it proves nothing against the very shape it
  exists to catch.
- **A counter anchored in the metadata file** catches
  the single-file swap (the drilled shape) — and only
  that shape. The anchor is itself a file in the same
  folder, replaced just as easily by anyone who can
  replace the vault; and the program's own legitimate
  roads move a vault *backwards* by design — healing
  from a backup (§2), restoring a carried file (E-101),
  the owner's own restore — so a hard freshness refusal
  would fire on the program's own first-aid, while a
  mere warning on the drilled shape would teach users
  to click past the one signal that matters.
- **An anchor outside the folder** — a remembered
  generation on another device, a companion-held
  counter, a dated external record — is the only shape
  that can honestly claim freshness, and it is a
  product decision about what the toaster companion
  *is* (what it may phone, store, or assume), not a
  patch a vault slice may smuggle in.

**Verdict:** docket 133 stands **open, not defended**,
and goes to **E-106**, the Part VI gate, to be carried
in the gate's verdict in those words; the external-
anchor shape is recorded here as the candidate remedy
if the gate — or the owner — ever commissions it. The
interim claim discipline of E-095 is unchanged and
binds every Ember document: the toaster-Kista may be
described as defending its contents against damage and
against readers without the key or the passphrase; it
may **never** be described as defending against
rollback to an older whole state.

## 5. Standing findings handed on

- **Docket 133 → E-106** (above): rollback/freshness,
  not defended, candidate external-anchor remedy
  recorded, claim discipline binding until then.
- **E-103** inherits a priced question from §2: the
  lock drill measured a writer's wait in seconds on a
  shared VM, which is contention, not cost — the
  vault's true toaster-profile costs (one scrypt at
  unlock, the lock's zero steady-state price) are
  E-103's budget proof to measure, not this slice's
  to estimate.
- The second-resolution auto-backup-name wrinkle
  (E-095 §7) stands as recorded there — noted here so
  the gate inherits it knowingly, not as this slice's
  finding.

## Slice gate

Measured on the VM at this slice's tree (runner only;
logs in `~/workspace/.verify-tmp/ember-e102/gate/`):

- **Focal battery** (this slice): **16 passed**.
- **Focal set** (the twelve Part VI batteries — E-094
  through E-102, the E-057 budget table, the E-089 canon
  guard, the E-093 custody law): **125 passed**.
- **Member suite** (kista's own): **149 passed /
  0 failed** — including the two docket-139 re-pins.
- **Run A** (whole suite, default env): **1 error /
  20 skipped**, interrupted at collection — the standing
  shape (the pgvector file's unguarded import, docket 1's
  family), unchanged.
- **Run B** (default env, pgvector file excluded):
  **1462 passed / 6 failed / 34 skipped** — the 6 are
  exactly the proven environment family (Batch CDE x3,
  G x2, J x1, all `sqlite_vec`-missing, the E-004
  family); 1462 = E-101's 1446 + this slice's 16, exact.
- **Run D** (whole suite, extras supplied): **NOT CLEAN
  IN ONE RUN — recorded honestly, not claimed.** Three
  attempts were destroyed by one recurring environment
  episode, each proven from its own log: attempt 1 ran
  failure-free through ~59% (991 passes recorded in its
  progress, no failure in the completed portion) and
  died on a native **bus error** inside a mimir-well
  sqlite init in an unrelated memory test (E-083's
  persona battery); attempt 2 died at startup, exit 120
  with an empty log, while a direct write probe proved
  the home quota was refusing writes (Errno 122, disk
  quota exceeded — the same EDQUOT flap E-101 recorded);
  attempt 3, begun after the probe passed again, died
  mid-run at ~46%, exit 120, when the flap returned.
  A single clean Run D is **OWED** and is docketed in
  the campaign state — E-103's tick discharges it first,
  as E-100 discharged E-099's and this slice meant to
  discharge E-101's. Nothing in the completed portions
  of any attempt failed; that is stated as far as it
  goes and no further.

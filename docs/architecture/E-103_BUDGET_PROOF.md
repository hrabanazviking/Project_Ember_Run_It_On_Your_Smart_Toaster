# E-103 — Budget Proof: the Vault's Cost on the Toaster Profile

*Part VI — Kista of the Toaster. The budget slice: what
the vault actually costs — at rest, in use, and to carry
in — measured against the smallest profile in the book,
the toaster (Part III, E-041): install 2 MiB, idle RAM
64 MiB, turn RAM 64 MiB, storage growth 2 MiB a month.
The budget book gains the vault's row from this record
(`docs/BUDGET_BOOK.md` §7, "The vault's own costs").*

## Headline — read this first, in plain words

**The vault itself is genuinely toaster-sized; carrying
its program in is the one place that is not — yet.**

Measured on the campaign VM, on scratch vaults holding
only synthetic entries:

- **At rest, the vault costs almost nothing.** A fresh,
  empty vault is **764 bytes** in total. Each typical
  entry adds about **563 bytes** to the encrypted vault,
  and because the program keeps its last five automatic
  backups, a whole working vault of **100 entries —
  vault, five backups, key and all — weighs 328,548
  bytes**, about a third of a megabyte. That is 16% of
  the toaster's whole monthly storage-growth allowance,
  spent once, on the vault's entire estate. The same
  arithmetic reaches that allowance at roughly **617
  typical entries**.
- **Standing idle, it costs exactly zero.** The vault
  is a command, not a servant: there is no resident
  process, no daemon, nothing listening. Between
  commands it uses no memory and no processor at all,
  so the toaster's idle ceiling is met by construction,
  not by tuning.
- **In use, one command peaks at 27.2 MiB** of memory
  on a 100-entry vault — and a passphrase-wrapped vault,
  whose unlock must run the scrypt derivation, peaks at
  **41.3 MiB**. Both fit inside the toaster's 64 MiB
  turn ceiling; the wrapped unlock spends about 65% of
  it, and §3 names where that memory goes.
- **The lock costs nothing at rest.** The write lock
  E-100 built is a 0-byte file and a kernel lock held
  only during a write; E-102 drilled what a second
  writer *waits*, and this slice closes that handed
  question: the lock's steady-state price is zero bytes
  and zero memory.
- **Carrying the program in is laptop-class on this
  machine — stated in the same size type.** The vault
  program itself is one file of **149,853 bytes**, but
  its one declared dependency, the `cryptography`
  library, stands installed at **15,573,597 bytes** in
  this VM's site-packages — one compiled Rust binding
  is 14,434,376 of those bytes. Program plus dependency
  is **15,723,450 bytes**: over the toaster's,
  phone's and pi's install ceilings alike, and inside
  the laptop's 16 MiB with 6% to spare. §4 gives the
  verdict and its caveats; docket 140 hands it to the
  Part VI gate. Nothing in this slice changes that
  shape — the dependency is the member's declared one
  (E-007/E-094), and replacing it is a product decision,
  not a budget proof's patch.

## 1. The charter

Two earlier slices handed this one its questions:

- **The roadmap's E-103 line itself** — "budget proof:
  the vault's cost on the toaster profile (Part III's
  book gains its row)".
- **E-102 §5** — the lock drill measured a writer's
  wait in seconds on a shared VM, which is contention,
  not cost; the vault's true toaster-profile costs
  (one scrypt at unlock, the lock's zero steady-state
  price) were expressly left here to measure.

**Method.** Sizes are exact byte counts from the
filesystem. Memory is a fresh process's peak resident
set (VmHWM from `/proc/self/status`), median of three
runs, the E-057 method. Times are wall-clock medians
of seven runs **on a contended VM** (load average
8–9 from sibling campaigns throughout) — they price
the shape of the work under contention, and are
recorded as contended medians, never as quiet-machine
promises. Every vault probed was a scratch vault with
synthetic entries only, under the Part VI custody
discipline. The toaster ceilings judged against are
the live `ember.budgets` values, re-derived by this
slice's battery, not copied from prose.

## 2. At rest: the vault's storage, measured

One scratch vault, grown entry by entry with typical
synthetic entries (a username, a password, a login
URL, a short note). Byte counts at each mark, the
whole vault directory:

| Entries | Vault blob | Backups (kept) | Meta | Key | Whole directory |
|---|---|---|---|---|---|
| 0 (init) | 268 B | 268 B (1) | 184 B | 44 B | **764 B** |
| 1 | 824 B | 824 B (1) | 201 B | 44 B | **1,893 B** |
| 5 | 3,084 B | 6,992 B (3) | 261 B | 44 B | **10,381 B** |
| 10 | 5,900 B | 22,144 B (5) | 337 B | 44 B | **28,425 B** |
| 25 | 14,328 B | 63,212 B (5) | 562 B | 44 B | **78,146 B** |
| 50 | 28,408 B | 133,016 B (5) | 937 B | 44 B | **162,405 B** |
| 100 | 56,524 B | 270,292 B (5) | 1,688 B | 44 B | **328,548 B** |

What the curve says:

- **Per-entry cost: ~563 bytes** in the encrypted
  blob ((56,524 − 268) / 100 = 562.6), ~15 bytes in
  the plaintext metadata (the service-name list), and
  nothing anywhere else. The growth is linear in the
  count of entries — there is no index, no journal,
  no hidden second store.
- **The estate is ~5.8 vaults, by design.** Every
  save also refreshes the automatic backups, capped
  at the last five (E-095), so once a vault has been
  saved five times its whole directory is the current
  blob plus five near-current copies of it — the
  healing copies E-102's drills rely on, priced here
  honestly instead of pretending the blob stands
  alone.
- **Wrapping the key costs 230 bytes**: a passphrase-
  wrapped vault's key file is 274 B against the bare
  key's 44 B (the 100-entry wrapped estate measured
  328,778 B in all). The carried envelope's shape was
  priced at E-101.
- **Against the toaster's storage ceiling** (2 MiB of
  growth a month): a 100-entry vault's *entire
  lifetime estate* is 328,548 B — 16% of one month's
  allowance. Solving the measured curve
  (6 × (268 + 562.6·n) + 15·n + 228 = 2 MiB) puts the
  allowance's edge at **≈617 typical entries** —
  derived arithmetic from the measured constants,
  labelled as such, not a 617-entry vault measured.

## 3. In use: memory and time, measured

Peak memory (VmHWM, median of three fresh processes):

| Shape | Peak RAM | Against the toaster's 64 MiB turn ceiling |
|---|---|---|
| Python + `cryptography` import alone | 18.2 MiB | the floor every command starts from |
| `get`, unwrapped, 1 entry | 26.7 MiB | 42% |
| `get`, unwrapped, 100 entries | 27.2 MiB | 43% |
| `get`, passphrase-wrapped, 100 entries | **41.3 MiB** | **65%** |
| `list`, passphrase-wrapped, 100 entries | 41.4 MiB | 65% |

- **The vault's size barely matters to its memory:**
  100 entries cost half a megabyte of peak over 1
  entry (26.7 → 27.2 MiB). The whole vault is read
  into memory to open it, and at these sizes that is
  small change next to the interpreter and the
  crypto library's 18.2 MiB floor.
- **The unlock is the one real memory event.** The
  wrapped `get` peaks 14.1 MiB above the unwrapped
  one on the same vault — the scrypt derivation's
  working set. The derivation's own arithmetic
  (128 × N × r at N=16384, r=8) is 16 MiB; the
  measured delta sits just under it, pages shared
  and reused. This is the deliberate price of
  E-096's passphrase: it is paid once per command,
  and it is why the wrapped peak, not the unwrapped
  one, is the row the book carries.
- **Idle is zero, by construction** — no process
  exists between commands (§0). There is also no
  lock cost at rest: the `.vault.lock` file is
  0 bytes in every mark of §2's table, and the
  flock it carries is held only for a write's
  duration (E-100/E-102).

Time (wall-clock medians of seven, contended VM —
the contention is part of this record, per §1):

| Shape | Median |
|---|---|
| `get`, unwrapped, 100 entries | 0.49 s |
| `list`, unwrapped, 100 entries | 0.43 s |
| `status`, unwrapped | 0.50 s |
| `get`, passphrase-wrapped (one scrypt unlock) | 0.68 s |
| `get`, wrong passphrase (refused) | 0.58 s |
| The scrypt derivation alone, in-process | 0.17 s |

Almost all of an unwrapped command's half-second is
process start and imports — the same shape E-046
measured for the core — not vault work: the vault's
own share is the decrypt of a 56 KB blob. A wrong
passphrase pays the same scrypt as a right one
before it is refused; that symmetry is the unlock's
design (E-096), priced here, not a new finding.

## 4. Carrying it in: the install verdict

| Piece | Installed bytes (VM) |
|---|---|
| The program: `kista/scripts/credstore.py` | 149,853 B |
| Its one dependency: `cryptography`, as installed | 15,491,145 B |
| — of which the compiled Rust binding alone | 14,434,376 B |
| The dependency's dist-info | 82,452 B |
| **Program + dependency, installed total** | **15,723,450 B** |

Judged against the book's install ceilings, that
total fits **only the laptop profile** (16 MiB, using
93.7% of it): it is 7.5× the toaster's 2 MiB ceiling,
3.7× the phone's, 1.9× the pi's. The program is not
the problem — at 149,853 B it would fit the toaster
seven times over with its key wrapped. The dependency
is the whole miss.

Caveats, in the open, because a verdict is only as
good as its edges:

- This prices **this VM's** x86_64 `cryptography`
  install, bytecode caches and all, as it stands in
  user site-packages (the same copy every Part VI
  probe has run against). Other platforms' wheels
  differ in detail; the Rust binding dominates the
  package on every platform the library ships, so
  the *shape* of the verdict is not a VM quirk —
  but the exact byte count is this machine's, and
  is recorded as such.
- The Python interpreter's own install is the host's,
  never charged — the book's standing rule (§6).
- The **tracked-checkout** row in §7's member table
  (kista 25 files / 2,820,119 B → phone) is a
  different number measuring a different thing — the
  whole member directory including its images, docs
  and tests. It stands unchanged by this slice; the
  installed weight above is what a machine actually
  carries to *run* the vault, and the two must never
  be quoted for one another.
- **NOT PROVEN on small hardware**: no kista install
  was made on the Pi or any toaster-class device in
  this slice. The RAM and storage proofs are VM
  measurements judged against toaster ceilings —
  the E-048 discipline (simulated profile, grade
  stated), not an E-049 device proof.

## 5. Docket 140 — NEW → E-106 (the install weight)

The dependency's installed weight is a true finding
and this slice does not pretend a budget proof can
fix it. The honest options are all product-shaped:
hold a different crypto road (the standard library
alone offers no authenticated-encryption shape the
custody law would accept as-is), vendor a smaller
binding, or accept the laptop-class install as the
vault's stated floor and let the *companion's* core
binding (E-100) carry the consequence. Choosing
among them belongs with the Part VI gate's verdict
and, where it changes what the program *is*, with
Volmarr. **Docket 140 records the measurement for
E-106**: until the gate rules, Ember documents may
call the vault toaster-sized at rest and in use, and
must never call it toaster-*installable*.

Standing notes handed on:

- **E-104** (docs) writes against §2–§3's numbers:
  the plain words for users are "an empty vault is
  smaller than a photo's thumbnail; a hundred
  passwords cost a third of a megabyte; unlocking
  with a passphrase briefly uses about two-thirds
  of the smallest machine's working memory."
- **E-106** inherits docket 133 (rollback, NOT
  DEFENDED, E-102) and docket 140 side by side:
  the gate's verdict carries both in plain words.
- E-057's member row is unchanged (no member file
  moved in this slice); the book's new §7 subsection
  is additive and its numbers are this record's,
  pinned by this slice's battery against both.

## Slice gate

Measured on the VM at this slice's tree (runner only;
logs in `~/workspace/.verify-tmp/ember-e103/gate/`):

- **The owed Run D, discharged first.** Before any
  E-103 file landed, the clean Run D owed since E-102
  ran whole on the E-102 tree (TMPDIR on /dev/shm,
  through the home-quota episode below): **1670
  passed / 0 failed / 20 skipped** in 490.6 s —
  exactly E-100's clean 1641 + E-101's 13 + E-102's 16.
- **Focal battery** (this slice): **10 passed**.
- **Focal set** (the thirteen Part VI batteries —
  E-094 through E-103, the E-057 budget table, the
  E-089 canon guard, the E-093 custody law): **135
  passed** (= E-102's 125 + this slice's 10, exact;
  the canon guard needed no new allowlist entry —
  this slice's battery carries no householder name,
  checked not assumed).
- **Member suite** (kista's own): **149 passed /
  0 failed**, unchanged.
- **Run A** (whole suite, default env): **1 error /
  20 skipped**, interrupted at collection — the
  standing shape (the pgvector file's unguarded
  import, docket 1's family), unchanged.
- **Run B** (default env, pgvector file excluded):
  **1467 passed / 11 failed / 34 skipped** — NOT
  CLEAN, recorded honestly. Six of the failures are
  the proven environment family (Batch CDE x3, G x2,
  J x1, the `sqlite_vec`-missing E-004 family). The
  other five are Verdandi hub tests (E-067 x3, E-068,
  E-073) failing on a mechanism proven three ways:
  their fixtures build the hub's home with
  `mkdtemp(dir="/tmp")` in the tests' own code;
  `/tmp` stood at **0 bytes free** (512 MB, 100% full
  under sibling campaigns' working dirs) for the
  entire gate window; and the same files passed whole
  in this tick's clean owed Run D hours earlier.
- **Run D** (whole suite, extras supplied): **1672
  passed / 8 failed / 20 skipped** — the same five
  hub tests, plus three integration acceptance tests
  whose failure in the log is a raw `tempfile`
  OSError (no space) at creation. 1672 + 8 = the
  expected 1680 total, exact.
- **A single clean Run B and Run D for this tree are
  OWED** and are docketed in the campaign state —
  E-104's tick discharges them first when `/tmp` has
  room, as this tick discharged E-102's. The claim
  for this slice's own code is not hung on those
  runs: the focal set, the member suite and the owed
  clean Run D on the parent tree are all green, and
  no failing test touches this slice's files.

**The environment episode, recorded plainly:** this
slice opened (01:21 EST) inside the recurring
home-quota EDQUOT flap — new files under the home
directory refused (`Errno 122`) while the disk held
39 GB free — and `/tmp` then filled completely
under sibling campaigns' work and stayed full. The
flap cleared and returned repeatedly all tick;
measurements and drafts were kept in /tmp and
/dev/shm meanwhile, gate scratch ran from /dev/shm,
and nothing was deleted by this campaign. Every
banked number above was measured on a filesystem
the episode never touched, or is labelled with the
episode where it was.

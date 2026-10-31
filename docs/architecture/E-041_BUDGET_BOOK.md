# E-041 — The budget book

*Part III, slice E-041. Roadmap line: "The budget book:
per-profile ceilings (install size, idle RAM, turn RAM,
storage growth/month) set from E-015's archaeology +
measurement; profiles: toaster (the smallest), phone-class,
pi-class, laptop." The book in code is `ember.budgets`;
this document is its evidence and its reasoning.*

## The book, in plain words

**Ember's core is much smaller than its own front door
claimed — and now that is measured, not believed.** Installed,
the whole companion core weighs **under one megabyte**
(978,843 bytes with its one default extra). Sitting idle with
its memory open it uses **about 41 MB** of RAM; answering a
turn, **about 40 MB** — the same on every profile, because at
this size the Python interpreter *is* most of the cost and the
history a bigger profile keeps is still small change. A month
of daily companionship (20 turns a day) grows its storage by
**under half a megabyte**. The old "~50 MB" claims were
generous guesses; the truth is kinder. What actually eats a
small machine was never Ember — it is the language model,
which is a separate program with its own ladder of sizes, and
this book never hides the model inside Ember's numbers.

The ceilings below are set at roughly one-and-a-half to two
times what was measured, so they are promises with headroom,
not aspirations. E-042 turns them into tests.

## The book

Ceilings for the **Ember core only** (package + default local
Well + diary + journal; model excluded — see §3):

| Profile | Reference host | Install | Idle RAM | Turn RAM | Storage growth / month |
|---|---|---|---|---|---|
| toaster | 512 MiB | 2 MiB | 64 MiB | 64 MiB | 2 MiB |
| phone | 2,048 MiB | 4 MiB | 96 MiB | 128 MiB | 10 MiB |
| pi | 4,096 MiB | 8 MiB | 128 MiB | 192 MiB | 25 MiB |
| laptop | 8,192 MiB | 16 MiB | 256 MiB | 384 MiB | 100 MiB |

Each profile also carries the history it may keep in a turn —
E-021's numbers, read from the conversation config by the
book itself so the two can never drift apart: toaster
512 tokens / 3 episodes, phone 1,024 / 5, pi 2,048 / 8,
laptop 4,096 / 12.

"Reference host" is the smallest host the profile is named
for *in this book*: the toaster's 512 MiB is the Tiny Device
Profile's own target (Pi Zero 2 W class, E-015 §5); the rest
are this book's definitions, stated so a reader can add the
model ladder to the right host size honestly.

## 1. How the core was weighed (VM profile, 2026-10-31)

Method: fresh processes, RSS from `/proc/self/status`
(VmRSS) with `ru_maxrss` as the peak cross-check; scripts and
raw logs in `~/workspace/.verify-tmp/ember-e041/`. Python
3.12.3, the campaign VM — **every number below is a VM
number**; other devices get their own measurements at
E-047–E-049, and nothing here is claimed for them.

**Install.** A fresh venv install of the package: the wheel
is 308,422 B; installed, the package directory is 729,802 B
— byte-for-byte the source tree's weight, as it should be —
plus 83,102 B of dist-info, plus the one default extra a
working install carries, `sqlite-vec` at 165,939 B with its
dist-info: **978,843 B in all (0.93 MiB)**, bytecode caches
excluded. After first run the caches add ~0.6 MB more. The
tracked monorepo (227 MiB on disk) is *not* the install —
E-015's scope warning, now settled by weighing both.

**Idle RAM.** Interpreter alone: 10.5 MiB. `import ember` +
a default config: 14.0 MiB. The full CLI/chat surface
imported, ready: **25.3 MiB** (three repeats: 25.1–25.3).
With the default Well open — the shape a running companion
actually idles in — **40.7 MiB**: the Well (SQLite +
the sqlite-vec extension) adds ~15 MiB over the bare CLI
shape, and saving twenty episodes moved it not at all.

**Turn RAM.** Five real `chat.run` turns against the real
Well, per profile, history at the profile's cap, a labelled
fake model replying ~400 tokens: **39.4–40.1 MiB peak on
every profile** — toaster and laptop within a megabyte of
each other. With a fake in-memory Well the same turns peak
at ~24 MiB, which isolates the Well's ~15 MiB share. The
honest reading: at fixture scale the core's turn cost *is*
its idle cost; profiles differ in what they *allow* (history,
drafts, members), not in what the core's turn weighs today.
Ceilings therefore grow with the profile as *allowance*,
while the measured anchor is one number for all four.

**Storage growth.** The default Well, closed and measured:
empty (schema only) 81,920 B; after 100 typical turns
(operator ~40 words, reply ~40 words) 143,360 B — **614
bytes per episode**. The diary adds ~80 B per turn (two fact
lines; a real 5-turn session file measured 660 B including
its session lines). The pending journal's 741 B per episode
is transient — it drains into the Well (E-031) — and is not
growth. Total: **694 B per turn**, projecting to **0.40
MiB/month at 20 turns a day**. A ceiling is not a prediction:
the toaster's 2 MiB/month ceiling is reached at ~86 turns a
day; the book says so rather than rounding the prediction up
into a promise.

**Verdandi, settled in shape (docket 65, measurement half).**
E-015 found six RAM figures for one member because two
programs share its name. Measured separately on the VM: the
**nerve hub, live** (`nervous_system.py serve`, status
Running, socket up) — **21.9 MiB RSS**. The **heartbeat**
(core + CLI + checks imported) — **18.4 MiB RSS**,
import-level; its daemon's live load truth is Part IV's
(E-075). So both programs are ~20 MiB-class processes on
this machine, the heartbeat's own guide figures (13–25 MiB,
Pi-measured) are the right *size* for the heartbeat, and the
hub's "~1 MB" is not a process memory figure anywhere it was
measured — it prices the hub's data, not its process. The
documents' wording is E-060's to fix; the numbers are
settled here.

## 2. Verdicts on the claims E-015 inherited

- **"Ember itself ~50 MB RAM" (docket 67) — TRUE, and
  generous.** Measured worst idle 40.7 MiB, turn peak
  40.1 MiB. The claim stands, now as a measured fact with
  the method named; E-045 re-measures idle over an hour.
- **"Ember itself + dependencies ~50 MB installed" —
  STRUCK as written.** The installed core is 0.93 MiB —
  the claim overstates Ember by ~50×. What it was reaching
  for is the *whole install story*: the ~3.5 GB "typical
  install" is Ollama (~700 MB) + models (~2.6 GB) + Ember
  (~1 MB). E-197's claims audit owns the front-door wording
  (READMEs are not this campaign's to edit); the book's
  install ceilings above are the citable truth from here.
- **"Default Well runs on a Pi 5 with 50 MB resident" —
  TRUE in shape, VM-measured at 40.7 MiB for the whole
  process** (the Well's own share ~15 MiB). Pi proof is
  E-047's; until then this row is a VM fact, not a Pi claim.
- **The Tiny profile's three numbers (docket 66) —
  SETTLED by replacement.** Its 622 MB sum priced a
  different, unbuilt architecture (TUI + in-process model);
  its 350 vs 400 MB caps contradicted each other. The book
  replaces all three for the *shipped* core: toaster host
  512 MiB, core turn ceiling 64 MiB. The honest remainder:
  OS (~150 MB, the Tiny doc's figure) + core (64) + the
  smallest model the Tiny doc itself falls back to (~300 MB
  for a 0.5B Q4) sums to ~514 MB — the toaster on a 512 MiB
  host is *marginal by arithmetic*, comfortable on the
  1 GB members of its class. E-049's Toaster Test grades
  the real thing; this book does not round 514 down to fit.
- **Hamr's two budgets (docket 68)** are recorded with
  their scopes and left to Part IX as assigned: `perf.py`'s
  enforced 1.5 GB governs avatar *builds*; Phase 17's
  7.5 GB / 143 MB describes its largest build shape. Neither
  is a core cost; neither enters the table above.
- **The sibling matrix's round numbers (docket 69)** are
  superseded for the core by this book; the measured
  *member* table that replaces them whole is E-057's, as
  assigned. Members with no budget of their own (docket 70)
  likewise get their rows at E-057 (mempalace/mimir at
  E-078, kista at E-103) — the core's book does not invent
  rows for them.

## 3. What the ceilings do not include

- **The model.** Ollama and its models are separate
  programs (the FUNI ladder: ~600 MB resident for a 0.5B on
  the smallest rung, ~2.2–2.5 GB for the default `phi3:mini`
  on an 8 GB Pi 5). A profile's reference host exists so
  this addition can be done openly, per rung.
- **Python itself.** A Python 3.12 interpreter is part of
  every RSS figure above (10.5 MiB of it) but its *install*
  is the host's, not Ember's, and is not in the install
  ceiling.
- **Members.** Verdandi's ~20 MiB class (above), and every
  other member, price into E-057's member table per profile.
  A whole-companion figure is the core's row *plus* the
  members actually enabled — never the monorepo's sum.
- **Ingested documents.** What an operator feeds the Well
  is bounded by the ingest caps (64 MiB per file, E-015 §4),
  not by the growth ceiling, which prices *conversation*.

## 4. Honest limits

- **VM numbers.** x86 VM, Python 3.12.3. ARM interpreters
  and smaller kernels will move the anchors; the ceilings'
  headroom (≥1.5×) is sized for that, and E-047–E-049
  re-anchor per device. New docket 90 records this.
- **Fixture scale.** Turn RAM was measured at each
  profile's history cap with a ~400-token fake reply.
  Longer replies cost prompt/render memory the fixture
  does not; the 1.5–2× headroom is the book's answer, and
  E-042's tests must re-derive, not just re-assert.
- **Storage scales with words.** 694 B is a *typical* turn
  (~80 words total). Pasted essays persist at their own
  size, plus the same per-row overhead.
- **No live model was served.** The model process is out of
  scope by design (§3), but that also means no end-to-end
  "companion + model on one small host" figure exists yet —
  that is exactly E-047/E-049's proof, not this book's.

## New docket items

(90) The budget book's anchors are VM measurements: the
per-profile ceilings are set from VM RSS/install/storage
figures with ≥1.5× headroom, and no toaster/phone/pi device
has re-anchored them yet. Assigned to Part III (E-047,
E-048, E-049 re-anchor on real devices; E-042's tests pin
the VM anchors and must be re-derived, not merely relaxed,
if a device anchor moves a ceiling).

## Tests

- `tests/unit/test_budgets_e041.py` — **11 passed** (default
  env): book completeness + ordering, monotonic ceilings,
  the toaster floor, the measured shape fitting every
  profile, the anchors pinned at their measured values,
  history numbers read from E-021's config (no second copy),
  storage arithmetic, and `check_against` naming each broken
  ceiling in plain words.
- Slice gate Run B (default env, pgvector file excluded):
  **929 passed, 6 failed, 18 skipped, 1 warning** — 918
  E-040 baseline + 11 new; the 6 are the proven environment
  failures. Run D (whole, extras) also run this slice (new
  core module): **979 passed, 0 failed, 19 skipped,
  1 warning**, exit 0 — 968 baseline + 11 new.

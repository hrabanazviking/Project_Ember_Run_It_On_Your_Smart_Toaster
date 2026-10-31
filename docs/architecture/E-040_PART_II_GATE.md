# E-040 — Part II Gate: day-one flow green, API frozen

*Project Ember campaign, Part II (The Ember Core: a Companion
That Works) — GATE. Filed 2026-10-31 on branch
`yrsa/ember-road-build` in the campaign's own clone
(`~/workspace/ember-build`), at campaign commit 639d96e
(E-039 banked + its push record). This gate closes Part II
on the roadmap's own criteria for E-040: "day-one flow green
end-to-end on the VM profile; API frozen; summary filed."
No production code was changed in this slice, no README was
touched. Gate re-measurements were run this slice; raw logs
live in `~/workspace/.verify-tmp/ember-e040/`.*

## The gate, in plain words — read this first

**Part II is done. The companion at the centre of Ember now
works as a small, dependable core.** A new person can install
it, answer five simple prompts, and have a first chat — that
whole path was run again at this gate and passes. The core's
promises to the other members are frozen as API version
1.0.0, checked live at this gate: all 155 frozen names are
present and the surface check comes back clean. The full
test suite, with its optional extras present, is completely
green: **968 passed, 0 failed.**

Honesty, kept plain: no real language model has yet run
behind Ember on this machine — the day-one proof uses a
loopback stand-in shaped exactly like the real model's
wire, because no model program is installed on the VM.
Proving Ember on real small hardware with a real model is
Part III's job, and it is not claimed here. Six test
failures in the bare, extras-less environment are the same
proven environment failures Part I found (they vanish with
the extras supplied), and a small set of older defects
Part II was assigned but no Part II slice was built to fix
— the bare-machine diagnostics crash and its kin — are
listed by number in §5 and carried forward with a named
home, not buried.

## 1. Gate criteria — each one checked, not assumed

| # | Criterion (roadmap E-040) | Evidence | Result |
|---|---|---|---|
| G1 | Every Part II slice E-019–E-039 banked | CAMPAIGN_STATE slice ledger, E-019–E-039 all DONE; all 21 per-slice documents present under `docs/architecture/` (verified by directory listing this slice) | PASS |
| G2 | Day-one flow green end-to-end on the VM profile | §2: targeted day-one + examples + API tests 50 passed this slice; the three runnable examples executed directly, each exit 0; E-032's clean-venv timings stand as the timed record | PASS (with the stated model limit) |
| G3 | Core API frozen (E-037) | §3: live check this slice — `API_VERSION 1.0.0`, 155 manifest entries, `verify_api_surface()` returns no problems | PASS |
| G4 | Full suite green before banking | §4: Run D (whole, extras) **968 passed, 0 failed, 19 skipped**, exit 0; Run B identical to E-039's banked counts | PASS |
| G5 | Part II's docket accounted for — nothing found, nothing lost | §5: closed items named with their closing slice; open items named with their carried-forward home | PASS — as an accounting; the open items themselves remain open |
| G6 | Summary filed | The section above ("The gate, in plain words") and §6 | PASS |
| G7 | The road below checked | §7: no re-cut demanded; Part III (tiny hardware) is next and owns the real-model / real-device proof Part II honestly lacks | PASS — no re-cut |

## 2. Day-one flow, re-proven at the gate (VM profile)

The E-032 audit ran the real flow — install into a clean
venv, wizard, first chat, second run — and timed it
(venv 26.79 s, install 19.24 s, day-one ask 1.28 s, second
run 0.93 s; `docs/architecture/E-032_DAY_ONE_FLOW.md`).
Those timings stand as the timed record; a clean-venv
re-run was not repeated at this gate, and no new timing
is claimed.

What this gate re-ran, on the VM profile, default env:

- `tests/unit/test_day_one_flow_e032.py`,
  `tests/unit/test_core_docs_examples_e039.py`, and
  `tests/unit/test_core_api_freeze_e037.py` together:
  **50 passed, 0 failed** (9 + 8 + 33 — the day-one flow's
  own tests, the runnable-examples tests, and the freeze
  tests, each at its banked count).
- The three runnable examples executed directly from the
  repo root, bare stdlib-only env, each **exit 0**:
  `examples/first_chat.py` (a turn streamed and remembered),
  `examples/member_binding.py` (frozen API only; it prints
  "frozen names: 155; surface problems: 0"), and
  `examples/offline_turns.py` (Well away → pending journal →
  clean drain, remembered on return).

The limit, stated once and plainly: the model behind every
one of these runs is a loopback wire-shape stand-in or a
labelled fake, because no Ollama daemon and no real model
exist on the VM (E-006, E-032). **A real-model day one is
NOT PROVEN.** Part III owns that proof, on a named device
(E-047/E-049).

## 3. The API freeze, checked live

Run this slice in the bare default env
(`~/workspace/.verify-tmp/ember-e040/api_check.log`):

- `ember.api.API_VERSION` = `1.0.0`, re-exported as
  `ember.API_VERSION` = `1.0.0` (package version stays
  0.2.0 — a release label, not the contract).
- `api_manifest()` = **155 entries** (63 individually
  frozen names + the 12 `ember.schemas.*` modules frozen
  wholesale, 92 names) — identical to the E-037 freeze.
- `verify_api_surface()` = `()` — no problems.
- `is_api_compatible("1.0.0")` = True;
  `is_api_compatible("2.0.0")` = False (a future major
  correctly refuses to bind).

The freeze is contract + gate tests, not import machinery
(E-037's stated limit): no member is migrated onto it yet —
Parts IV–X bind against it, as roaded.

## 4. Gate re-measurement (E-017 method, part-gate shapes)

Measured this slice at HEAD 639d96e, VM profile
(Python 3.12.3, pytest 9.1.1), TMPDIR on the workspace
overlay; raw logs in `~/workspace/.verify-tmp/ember-e040/`
(`runA.log`, `runB.log`, `runD.log`).

| Run | Shape | Gate result |
|---|---|---|
| A | Whole suite, default env | Interrupted at collection — **1 error, 11 skipped**, exit 2 (docket 1, unchanged) |
| B | Default env, pgvector file excluded (the slice gate) | **918 passed, 6 failed, 18 skipped, 1 warning** — identical to E-039's banked gate |
| D | Whole suite, extras supplied from the isolated dir | **968 passed, 0 failed, 19 skipped, 1 warning**, exit 0 — identical to E-039's banked gate |

Run A's skip count rose from the E-017 freeze's 8 to 11
because Part II added three new skip-guarded extras test
files (the E-021 episode reader, E-031 corruption, and
E-038 Well-concurrency files) — each skips honestly when
`sqlite_vec` is absent and passes in Run D. That is the
only movement in any shape, and it is explained, not a
regression. Run B's 6 failures are the proven environment
failures of docket 2/3 (optional-extra coupling), identical
since the E-001 baseline; Run D proves the same tests pass
with the extras they need.

## 5. Part II's docket — closed, and carried forward

Closed in Part II (from E-016's assignment and Part II's
own new items 81–89):

- **15** (wizard EOF crash) — closed E-032.
- **55** (`.env.example` Runa fossil) — closed E-033.
- **56** (config fragmentation) — closed E-033 (core half)
  + E-037 (member half: members bind through the frozen
  API, keep their own config shapes).
- **81** (episodes write-only) — closed E-021.
- **82** (pending-episodes journal missing) — closed E-031.
- **83** (non-streaming tool calls dropped) — closed E-028.
- **85** (silent save failure) and **86** (silent retrieval
  failure) — closed E-030.
- **87** (wizard Well path forgotten) and **88** (wizard
  wrote a config the documented install cannot read) —
  found and closed E-032.
- **84** (DATA_FLOW drift), DATA_FLOW half — closed E-039;
  the whole-docs reconciliation remains E-194's.

Carried forward, open, with a named home each — this gate
closes Part II on its stated criteria; it does **not**
claim these are fixed:

- **1, 2, 3, 4** — the root suite's guard family (pgvector
  test's unguarded import; the sqlite_vec adapter's
  top-level optional import coupling pure helpers to the
  extra; unguarded tests failing instead of skipping; the
  MCP runner's un-awaited-coroutine warning, Run B/D's
  1 warning). Part II owned them on paper (E-016) but no
  slice E-019–E-039 was built to fix them. Carried to
  **Part XII: E-187 (whole-monorepo audit — findings fixed
  or roaded) with E-200 (regression armour) as the gate
  that must show Runs A/B clean or the items re-roaded
  with Volmarr's word.** Until then Runs A/B keep reporting
  them, exactly as §4 shows.
- **13** — `ember doctor` / `well status` crash in the
  stdlib-only env (the boot face of item 2). Same home as
  item 2 above; E-029/E-032 already corrected the docs
  that over-promised doctor on a bare install.
- **20** — the core's optional `keyring` secret source is
  declared in no packaging extra (lazy and graceful in
  code). Carried to **Part III: E-044 (dependency diet)**,
  beside docket 23 (lockfiles), its packaging kin.
- **89** — the `examples/` scaffold READMEs are stale
  Runa-era text. They are README.md files, untouchable by
  this campaign; correction assigned to **E-195 (README
  care)**, as E-039 recorded.

Other honest limits Part II leaves on the record, each
with its owning part: the Brunnr adapters do not yet
persist `persona_id` / `conversation_id`, so named
personae/conversations have no cross-restart history yet
(Part V, E-080 family); ThoughtForge is bound as a
candidate only — chat is not rewired to it, and no live
ThoughtForge or Aesir turn has run (Parts III/VIII own
live proof); two-process concurrency is NOT PROVEN
(E-038 proved threads).

## 6. Plain-language summary (for the campaign record)

Part II asked: *can the companion itself be made small,
documented, and dependable?* Twenty-one slices answered
it. The turn loop is mapped and hardened — history survives
restarts, long talks are windowed to a profile's token
budget, and dropped turns are reported, never silent. Two
model backends stand under one honest contract (Ollama,
and Volmarr's own Aesir in its native shape), plus a
candidate thinking layer (ThoughtForge) bound but not
switched on. The companion has personae that cannot leak
into each other, conversations that cannot bleed, tools
that must ask in plain words and can be remembered only
where remembering is safe, and a diary a friend can read.
It works offline, says so when its memory is away, saves
what it can and journals the rest, and can be interrupted
by talking over it without losing the thread. Its public
shape is frozen at API 1.0.0 so every other member can
build against it. What Part II did not do is prove any of
this on real small hardware with a real model — that is
Part III, and it starts now.

## 7. The road below — checked

Part III (E-041–E-058, tiny hardware) follows in roadmap
order; nothing in Part II's evidence demands a re-cut.
Part III inherits, by name: the budget book to build from
E-015's archaeology (E-041), the real-device proofs
(E-047/E-049) that Part II's loopback proofs cannot
substitute for, docket 20 at E-044, and the per-profile
truth (toaster / phone / pi / laptop) that every later
part's budget rows depend on. Parts IV and V bind against
the frozen API (E-037) and inherit the persona/conversation
storage limit at E-080. The roadmap file was not edited
by this gate.

## Carried forward

- Part II is CLOSED by this gate. Next: E-041 (Part III) —
  the budget book.
- Open and carried, not lost: docket 1, 2, 3, 4, 13
  (→ E-187/E-200), 20 (→ E-044), 84's remainder (→ E-194),
  89 (→ E-195).
- NOT PROVEN at this gate: a real-model day one, a live
  Aesir turn, a live ThoughtForge turn, two-process
  concurrency — each with its owning part named above.

*Filed by the E-040 slice, 2026-10-31. Part II gate: PASS.
Next: E-041 — the budget book (Part III opens).*

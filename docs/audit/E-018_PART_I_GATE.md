# E-018 — Part I Gate: the audit published, verdicts prepared

*Project Ember campaign, Part I (The Monorepo's True State) —
GATE. Filed 2026-10-31 on branch `yrsa/ember-road-build` in
the campaign's own clone (`~/workspace/ember-build`), at
campaign commit 8cf35cc (E-017 banked + its push record).
This gate closes Part I. It executes no removal, no
retirement, and no merge: every verdict below is PREPARED
for Volmarr's word where his word is required, and assigned
to its owning part where ordinary build work is all that
remains. No code was changed in this slice, no README was
touched, and ORIGINS.md was not modified.*

## The gate, in plain words — read this first

**Part I is done, and the monorepo can be built on honestly.**
We read every member before touching anything. The companion
at the centre is real: with its optional extras present its
whole test suite passes (583 passed, 0 failed). Two things
that would actually bite a normal user were found — a part of
Verdandi (Vör) that crashes, and an astrology program that
says "success" while computing nothing — and both are
numbered, assigned, and waiting in their own parts, not
hidden. No real password or secret was ever found lying in a
plain file. Nothing in the tree needs to be thrown away on
the evidence Part I gathered, so this gate throws nothing
away: it recommends keeping every member, gives each one a
named future, and asks Volmarr's word only on the handful of
true removals and retirements (four broken placeholder
pictures, duplicated house material, a title-only stub,
empty scaffolding shells, and whether the never-written
Ragnarok codex should be written or retired). The road
below does not need to be re-drawn — Part I checked the
facts that could have forced a re-drawing, and none of them
did. Part II can start.

## 1. Gate criteria — each one checked, not assumed

| # | Criterion (roadmap E-018) | Evidence | Result |
|---|---|---|---|
| G1 | Every Part I slice E-001–E-017 banked | CAMPAIGN_STATE slice ledger, E-001–E-017 all DONE | PASS |
| G2 | Audit published in-repo | §2 below: 16 audit documents E-002–E-017 under `docs/audit/`, all present at gate HEAD (verified by directory listing this slice) | PASS |
| G3 | Verdicts prepared (not executed) for every member | §3 below: a verdict for every row of the E-002 census (21 top-level members + the root loose estate) | PASS |
| G4 | The E-018-owned docket items verdict-prepared | §4 below: items 52, 60, 62, 63, 64, 71 — each with a prepared verdict and the word it waits for | PASS |
| G5 | Bug & gap docket complete and assigned | E-016: 80 entries covering 79 distinct issues, continuous 1–71 + 72–80, owner tally sums to 80 | PASS |
| G6 | Baseline frozen as the campaign's zero line | E-017, re-measured at this gate in §5 — all three runner shapes identical to the freeze | PASS |
| G7 | Plain-language summary filed | The section above ("The gate, in plain words") and §6 | PASS |
| G8 | The road below re-cut if facts demand, changes recorded | §7: re-cut triggers checked one by one; no structural re-cut demanded; four sharpenings recorded | PASS — no re-cut |

## 2. The audit as published (Part I's complete record)

All under `docs/audit/` in this repo, on this branch:

| Slice | Document | What it proves |
|---|---|---|
| E-002 | `E-002_MEMBER_CENSUS.md` | Every member inventoried (21 top-level + root estate) |
| E-003 | `E-003_ORIGINS_CONCORDANCE.md` | ORIGINS × tree, claim by claim |
| E-004 | `E-004_FRESH_BASELINE_I.md` | Root suite whole, failures classified |
| E-005 | `E-005_FRESH_BASELINE_II.md` | Per-member truth table |
| E-006 | `E-006_BOOT_CENSUS.md` | What actually starts today |
| E-007 | `E-007_DEPENDENCY_LICENCE_AUDIT.md` | Dependencies + licence estate |
| E-008 | `E-008_CODEX_CENSUS.md` | The five elder codices counted |
| E-009 | `E-009_VERDANDI_CONCORDANCE.md` | Verdandi's own roadmap × its code |
| E-010 | `E-010_HAMR_VERIFICATION_PLAN.md` | Hamr Ph1–17 claims → proving artefacts |
| E-011 | `E-011_TWO_KISTAS_BOUNDARY.md` | The two Kistas separated, 8 custody rules |
| E-012 | `E-012_TWO_MEMORIES_CENSUS.md` | mempalace vs mimir-well, measured |
| E-013 | `E-013_CONFIG_SECRETS_CENSUS.md` | Config shapes; no real credential in plain files |
| E-014 | `E-014_DEAD_DUPLICATE_CENSUS.md` | Dead / duplicate census, byte-proven |
| E-015 | `E-015_BUDGET_ARCHAEOLOGY.md` | Every size/RAM claim classified |
| E-016 | `E-016_BUG_GAP_DOCKET.md` | 80 entries / 79 distinct issues, all assigned |
| E-017 | `E-017_BASELINE_FREEZE.md` | The zero line + keeper re-measurement method |
| E-018 | this document | The gate: verdicts prepared, road checked |

(E-001 is the campaign opening; its record is CAMPAIGN_STATE.md
itself, §E-001, plus the roadmap filed at
`docs/EMBER_ROADMAP_2026-10-30.md`.)

## 3. Verdicts prepared for every member — none executed

Verdict words: **KEEP** (stays, its part builds on it),
**KEEP — STEWARD** (vendored / held in trust; wrap, never
rewrite), **KEEP — PENDING VERDICT** (stays until a named
later verdict, which is Volmarr's word where a retirement is
proposed), **PREPARED** (a removal/retirement/fate decision
written out in §4, awaiting Volmarr's word — nothing acted
on). No verdict in this section removes, merges, moves, or
retires anything.

| Member (E-002 census) | Prepared verdict | Grounds in one line; owning part |
|---|---|---|
| `src/` — ember core | KEEP | The companion itself; root suite green with extras (E-004/E-017). Part II |
| `tests/` (root) | KEEP | The core's suite and the campaign's gate instrument (E-017 method). Part II |
| `Verdandi/` | KEEP | Nerve hub proven LIVE (E-006); v0.3.0 Skuld real (E-009); Vör broken (docket 31) is a fix, not a fate. Part IV |
| `kista/` (toaster Kista) | KEEP | A program in its own right (E-011); its default-home collision (46) is a fix. Part VI. Never merged with the ai-folder Kista (roadmap §6) |
| `mempalace/` | KEEP — PENDING VERDICT | Neither memory is retired by Part I: Part V's harness (E-078) and verdict paper (E-079) decide unify / bound / retire, and a retirement is Volmarr's word. Part V |
| `mimir-well/` | KEEP — PENDING VERDICT | Same standing as mempalace, for the same reason; the core's own Brunnr Well is the third system in that comparison (E-012). Part V |
| `seidr_engine/` | KEEP | The one fully green member (38 passed, E-005); boots and computes bare (E-006). Part VII |
| `astrology-engine/` | KEEP | One real 134,560-byte engine file; its defect is honesty + undeclared deps (16/18), both fixable in place. No suite exists (77) — fixtures first. Part VII |
| `bifrost/` | KEEP | Small bridge library, instantiates (E-006); unguarded-test and config fixes only (6). Part VIII |
| `Hamr/` | KEEP | Large real suite (2,170 passed, E-005); COMPLETE claims are verified before building, per E-010's plan — verification may re-road its remainder (E-142), it does not prejudge it. Part IX |
| `Open-VTT/` | KEEP | A real Godot project, correctly referenced (E-006); boot here NOT PROVEN (no Godot binary) — a proof gap, not a defect verdict. Part X |
| `CloakBrowser/` | KEEP — STEWARD | Vendored third-party code: licences intact, never rewritten (E-007); its compiled binary is proprietary — a release-shape constraint (25), not a violation. Part XI |
| `cleasby-vigfusson-old-norse-dict/` | KEEP | Real Next.js dictionary app; its Jest suite is NOT MEASURED (78), an open measurement for Part VII — not a pass, not a fail. Part VII (E-115/E-116) |
| `docs/` | KEEP | The written estate, incl. the dormant-by-design Stofa TUI tree and the archived Runa skeleton (E-014 §5 — explicitly NOT dead). Parts X/XII as assigned |
| `assets/` | KEEP | The canonical home proposed for the ORIGINS images in §4 (item 62); its own 11 images all present (E-003). Part XII (E-196) |
| `config/` | KEEP | Templates only; fragmentation (56) is answered by Part II's one-config-surface work (E-033/E-037), not by removing the member. Part II |
| `deploy/` | KEEP | Documents only today; Part XI replaces any container-shaped shape with native recipes (E-181/E-182) — no Docker ever. Part XI |
| `examples/`, `scripts/`, `tools/` | PREPARED — see §4, item 64 | Markdown-only shells (13 files); per-directory fates prepared there, decided together with item 73. Volmarr's word for any retirement |
| `vendor/` | KEEP (as a register question, not a tree move) | Holds only its README while CloakBrowser sits at top level (76): the correction belongs to the register at E-196; no member is moved by this campaign on that ground. Part XII / XI |
| Root loose estate (ORIGINS, codices, images, pyproject) | KEEP, with two named exceptions prepared | ORIGINS is extended, never rewritten, at E-196 (72/74/75/79). The five codices: four DONE-in-fact, Ragnarok's fate is item 26 (Volmarr's word, E-165). The 22-file root image population is register material for E-196 (79), proven NOT duplicates (E-003). The UX-codex stub is item 63, §4 |

## 4. The E-018-owned verdict preparations (docket 52, 60, 62, 63, 64, 71)

Each entry: the finding, the prepared verdict, what executing
it would mean, and whose word it waits for. **None is
executed by this gate.**

### Item 52 — UNWIRED_INVENTORY's mempalace line
- Finding: `docs/UNWIRED_INVENTORY.md` calls mempalace
  "likely abandoned or archival"; E-012 proved that false
  (v3.3.5, 1,712 passed) while its wired=no fact stands.
- Prepared verdict: **CORRECT THE CHARACTERISATION** — the
  line should read, in substance, "not wired to the core;
  a live upstream member held unwired" when the inventory
  is next truthfully updated. Execution is assigned to
  E-091 (Part V's residue slice), not done here, so the
  correction lands beside the memory verdict it depends on.
- Word required: none beyond the campaign's own — this is a
  truth-correction to our own inventory, executed by E-091.

### Item 60 — Four Verdandi 1-byte pseudo-PNGs
- Finding (E-014): `Verdandi/656lk65l.png`,
  `65765gf5645.png`, `8328732kjdjmsd.png`, `k0rai4k0rai4k0ra.png`
  — each exactly 1 byte (a newline), invalid as images,
  unreferenced in the pre-campaign tree; the pictures they
  place-held do not exist in this tree.
- Prepared verdict: **REMOVE the four placeholder files** —
  they are broken uploads, not pictures, and keeping them
  makes any future image audit lie. If the pictures exist
  outside the tree, the correct act is instead to replace
  the placeholders with the real images.
- Word required: **Volmarr's** — only he knows whether the
  originals exist outside the tree. Nothing is removed
  until he says.

### Item 62 — Cross-member duplication of house material
- Finding (E-014): 2,886,896 wasted bytes in this item —
  IMG_0665/0666 in three homes each (`assets/`, `Verdandi/`,
  `kista/`), the licence image ×2, two Hamr/astrology image
  pairs, `Volmarr_writings_philosophy.md` ×3, and
  `WORLD_MODELING_SKILL.md` ×2; no copy is marked canonical.
  (The mempalace logo's three homes are intentional static
  distribution and are excluded.)
- Prepared verdict: **ONE CANONICAL HOME PER ARTEFACT,
  the other copies removed once he approves the homes:**
  images → `assets/`; `Volmarr_writings_philosophy.md` →
  `docs/philosophy/` (its subject home); `WORLD_MODELING_SKILL.md`
  → `docs/design/` (its subject home). Member-local copies
  that a member genuinely displays should be replaced by a
  reference to the canonical home where its tooling allows,
  or recorded as intentional distribution like the logo.
  The sharp risk is the texts: unmarked copies can silently
  diverge.
- Word required: **Volmarr's** for every removal (his
  writings and his house images). The measured table itself
  also feeds E-057 (Part III's member budget table).

### Item 63 — `THE_CYBER-VIKING_UX_CODEX.md` (25-byte stub)
- Finding (E-014): the root file is its own title line and
  nothing else; the Design Lawbook it names stands complete
  at root in full (`.md` + `.pdf`).
- Prepared verdict: **POINT, DON'T WRITE OR RETIRE** — make
  the stub a short pointer naming the Lawbook as the codex's
  living body, executed with the whole docs estate in view
  at E-193–E-195 (Part XII). Writing a second UX codex
  beside the Lawbook would create exactly the two-truths
  problem item 62 names; retiring the name entirely would
  break any external reference to it.
- Word required: none for the pointer shape itself (it
  preserves, it does not remove); if Volmarr prefers the
  codex written or retired instead, his word at Part XII
  supersedes this preparation.

### Item 64 — Bootstrap scaffolding shells (`scripts/`, `tools/`, `examples/`)
- Finding (E-002/E-014): 13 Markdown-only files, 12,921
  bytes, zero code, describing contents that never arrived;
  decided together with item 73 (the never-built ORIGINS
  drift detector, whose planned home is `tools/repo/`).
- Prepared verdict, per directory: **`tools/` KEEP AND
  FILL** — it is the named home of the drift detector
  (73, executed at E-196) and of repo tooling the campaign
  itself now needs; **`scripts/` and `examples/` FOLD** —
  their README-described purposes are served by `docs/`
  (operations / examples in the builder docs, E-194) and
  nothing in the tree references them as code homes; each
  shell's own text is preserved in the fold, not deleted
  silently. `vendor/` (item 76) is not part of this item:
  it stays, as §3 records.
- Word required: **Volmarr's** for the `scripts/` /
  `examples/` fold (a retirement of two named directories);
  the `tools/` fill needs no removal word and lands at E-196.

### Item 71 — Stofa TUI's named-but-absent budget tests
- Finding (E-015): Stofa's performance-budget doc names CI
  tests (`test_stofa_launch_budget.py`,
  `test_idle_memory_under_50mb`) verified absent from the
  tracked tree, for budgets over a TUI that is itself a
  dormant design tree awaiting ADR-0015 (E-014 §5).
- Prepared verdict: **STRIKE THE CLAIM, DON'T BUILD THE
  TESTS** — there is no TUI to measure, so building budget
  tests now would prove nothing; the doc's test names are
  recorded here and in E-015 as an unbuilt proposal. If
  Stofa is ever built (Volmarr's word, ADR-0015), its
  budgets enter Part III's book the normal way, through
  E-042's budget-test gate, measured.
- Word required: none for recording the strike (the audit
  docs are the correction of record; the elder proposal doc
  itself is not edited). Building Stofa at all remains
  Volmarr's, untouched by this preparation.

## 5. Gate re-measurement (E-017 method, part-gate shapes)

Measured this slice at HEAD 8cf35cc, VM profile, TMPDIR on
the workspace overlay; raw logs in
`~/workspace/.verify-tmp/ember-e018/` (`runA.log`, `runB.log`,
`runD.log`). All three shapes are **identical to the E-017
freeze**:

| Run | Shape | Gate result |
|---|---|---|
| A | Whole suite, default env | Interrupted at collection — **1 error, 8 skipped**, exit 2 (docket 1) |
| B | Default env, pgvector file excluded (the slice gate) | **546 passed, 6 failed, 12 skipped, 1 warning** (the 6 are the proven `sqlite_vec` environment failures, docket 2/3) |
| D | Whole suite, extras supplied from the isolated dir | **583 passed, 0 failed, 19 skipped, 1 warning**, exit 0 |

No regression, no silent improvement: Part I closes exactly
on its zero line.

## 6. Plain-language summary (for the campaign record)

Part I asked one question — *what is actually in this
monorepo, and what state is it truly in?* — and answered it
with measurements, not impressions. Sixteen audit documents
stand in the repo. Eighty docket entries (79 distinct
issues) name everything found wrong, missing, stale, or
undecided, each with an owner in the parts that follow.
Every member has a prepared verdict above, and the headline
of those verdicts is that **nothing needs throwing away**:
the work ahead is fixing, wiring, and proving — Vör's crash
(Part IV), astrology's silent success (Part VII), bare-machine
diagnostics (Part II), the toaster Kista's vault home
(Part VI), two memories awaiting one evidence-based verdict
(Part V), and Hamr's claims awaiting verification (Part IX).
Six small fates genuinely need Volmarr's word before anyone
acts: the Ragnarok codex (26), the known-accounts ledger's
custody (48), and §4's removals/folds (60, 62, 64 — plus
the removal half of 61, owned by Parts IX/X). Those are
asked for once, in the Part I completion report; this gate
does not act on any of them.

## 7. The road below — re-cut check (changes recorded here)

The roadmap's §5 order was tested against Part I's facts
against five re-cut triggers. **No structural re-cut is
demanded; the order E-019 → E-204 stands as carved.** The
triggers and why each fails to force a change:

1. *A member missing or dead* would have re-cut its part —
   none is: every roadmap §2 member is PRESENT (E-002),
   and the only fully unwired code found is four Verdandi
   modules already owned by Part IV (59).
2. *A broken core* would have re-ordered Part II first —
   the core's suite is green with extras (Run D); its
   defects (1–4, 13, 15, 20, 55, 56) are exactly Part II's
   existing slices' material.
3. *A licence or provenance bar* would have stopped a part —
   none exists: the estate is permissive and intact
   (E-007); the one constraint (CloakBrowser's binary, 25)
   is already Part XI's own subject.
4. *A budget impossibility* would have re-cut Part III —
   the budget claims are unmeasured or contradictory
   (65–71), which is precisely what E-041–E-058 exist to
   settle by measurement; no measured fact yet forbids any
   profile.
5. *An elder commission already done or impossible* would
   have re-cut Part X — four codices are DONE-in-fact and
   Ragnarok's fate is a prepared question (26), both of
   which E-161–E-165 already exist to reconcile.

Four sharpenings are recorded (clarifications, not re-cuts;
the roadmap file itself is not edited by this gate):

- **S1 (Part V):** mempalace and mimir-well both stand
  KEEP — PENDING VERDICT (§3). E-079's paper is the first
  moment a retirement may be proposed, and it goes to
  Volmarr — Part V builds the comparison first (E-077/E-078).
- **S2 (Part VII/X):** astrology-engine and Open-VTT have
  no suites (77) and the dictionary's suite is unmeasured
  (78): their parts inherit a fixtures-first position —
  the first slice that needs a count from them builds the
  harness that produces it, per E-077/E-078's precedent in
  Part V and docket 54's discipline.
- **S3 (Part IX):** E-142's slice count remains unset until
  E-140's verification table lands, exactly as the roadmap
  already states; Part I adds no estimate of it.
- **S4 (gate-owned items):** items 52, 60, 62, 63, 64, 71
  are verdict-prepared in §4 and leave Part I closed as
  preparations — their executions live at E-091 (52),
  E-193–E-195 (63), E-196 (64/`tools/` + 73), E-057's table
  (62's evidence), and Volmarr's word (60, 62, 64's folds).
  No later part needs to re-prepare them.

## Carried forward

- Part I is CLOSED by this gate. Next: E-019 (Part II) —
  core loop mapped.
- Awaiting Volmarr's word (asked once, in the Part I
  completion report — not blockers for Part II): docket 26
  (Ragnarok: author or retire), 48 (known-accounts custody),
  60 (pseudo-PNG removal), 62 (canonical homes + duplicate
  removals), 64 (`scripts/` / `examples/` fold).
- Defects found in Part II onward start at docket 81 in
  their own parts' records (E-016's rule).

*Filed by the E-018 slice, 2026-10-31. Part I gate: PASS.
Next: E-019 — core loop mapped (Part II opens).*

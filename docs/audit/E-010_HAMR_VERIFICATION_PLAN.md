# E-010 — The Hamr Verification Plan

*Project Ember campaign, Part I (The Monorepo's True State).
Measured 2026-10-31 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), at campaign
commit 15c8487 (E-009 banked). Every Hamr phase claim in the
tree was inventoried from its source document; for each
claim this plan names the artefact that would prove it, the
method, the pass criterion, and the environment the proof
needs. This slice plans only: Part IX (E-138–E-140) executes
the verification and publishes the PROVEN / PARTIAL /
NOT PROVEN table (E-140). Defects in the claim set itself
are carried to the E-016 docket, continuing its numbering
(items 38–45). Raw claim sources are kept under
`~/workspace/.verify-tmp/ember-e010/`.*

## Headline

**Hamr's completion story is real in bulk and unverifiable
as written in detail.** Five phases carry dedicated
COMPLETE documents (11, 12, 13, 15, 16); Phase 15 also
claims completeness inside its plan doc, and Phase 16
inside both. But the first ten phases have **no phase
documents at all** — Phases 1–5 survive only as one-line
CHANGELOG entries, Phase 6 has no claim anywhere in the
tree that this slice could find, and Phases 7–10 are
attested only by their test files (`test_phase7.py`,
`test_phase8.py`, `test_phase9_10.py`) plus one
release-notes phrase ("Phases 7–14"). Phase 14 has **no
COMPLETE artefact**: its plan doc lists seven unchecked
tasks and the CHANGELOG details only one of them (T6, the
release candidate). Phase 17 is **not complete and does
not claim to be** — `PHASE_17.md` is a vision document
whose own success criteria describe a first end-to-end
build that has not been evidenced anywhere, and the tree
holds **no `.vrm` file at all** (the only `*.vrm` path,
`Hamr/build_output/test.vrm`, is a directory containing a
preset YAML). Three classes the COMPLETE docs name as
their headline modules — `MaterialForge`,
`CollisionForge`, `PoseLibrary` — **appear nowhere in
`src/` or `tests/`**; functionally-named equivalents exist
(`AnimeMaterialGenerator`, `CollisionMeshGenerator`, the
`poses` module), so several claims are false *as written*
even where the underlying capability may be real. And the
test-count spine of the whole story (556 → 1159 → 1569 →
~1965/~2206 → 2206) is contradicted by the campaign's own
measured baseline (E-005: 2170 passed / 28 failed /
33 skipped / 2 errors, with deps) and by the COMPLETE
docs themselves, two of which admit failures in their own
totals (Phase 12: 4; Phase 13: 7) while titled COMPLETE.

None of this says Hamr does not work. It says the marks
are not evidence — which is exactly what the roadmap
ordered Part IX to settle. The plan below makes every
claim falsifiable.

## The claim sources (what Part IX verifies against)

| Source | Phases covered | Nature |
|---|---|---|
| `Hamr/CHANGELOG.md` [0.1.0]–[0.8.0] | 1, 2, 3, 4, 5, 11, 12, 13, 14 (T6 only), 15, 16 | One-line to section-level claims per phase; the *only* source for Phases 1–5 |
| `Hamr/PHASE_11_COMPLETE.md` (159 lines) | 11 | 8 tasks, module map with line counts, 556 tests |
| `Hamr/PHASE_12_COMPLETE.md` (141 lines) | 12 | 7 tasks, 1159 tests, admits 4 failures |
| `Hamr/PHASE_13_COMPLETE.md` (118 lines) | 13 | 7 tasks with per-task test counts, 1569 passed, admits 7 failures |
| `Hamr/PHASE_14.md` (56 lines) + `ARCHITECTURE_14.md` + `DATA_FLOW_12.md` kin | 14 | Plan only: 7 tasks (14.1–14.7), none checked off; no COMPLETE doc |
| `Hamr/PHASE_15.md` (65 lines, header "✅ COMPLETE") + `PHASE_15_COMPLETE.md` (56 lines) | 15 | 7 tasks, 6 promotion checks, ~1965 collected / 0 failures |
| `Hamr/PHASE_16.md` (68 lines, header "✅ COMPLETE") + `PHASE_16_COMPLETE.md` (76 lines) | 16 | 7 tasks, 2206 passing / 0 failures / 27 skipped, v0.8.0 |
| `Hamr/PHASE_17.md` (214 lines) + `ARCHITECTURE_17.md` + `DATA_FLOW_17.md` + `AUDIT_17.md` (52 lines) | 17 | Vision + success criteria for a *future* first E2E build; AUDIT_17 is a pre-flight audit claiming 3 blockers FIXED — **no completeness claim** |
| `Hamr/RELEASE_NOTES.md` | 13–16 + "Phases 7–14" | Corroborating claims; repeats the 2206 / 0-failures spine |
| `Hamr/tests/test_phase*.py`, `test_spec.py` | 1–5 (via test_spec), 7, 8, 9–10 | The only in-tree artefacts Phases 6–10 could be judged by; Phase 6 has not even this |
| `Hamr/src/hamr/*/__init__.py` headers | 7 | Three package docstrings assert "Phase 7: Complete. The forge breathes." — a claim with no other source |

Claimed test-count spine, for the record: Phase 1: 13 ·
Phase 11: 556 · Phase 12: 1159 (4 failed, 11 skipped) ·
Phase 13: 1569 (7 pre-existing failures admitted in the
same doc's total line) · Phase 14 entry (per
`ARCHITECTURE_15.md` §0): 1814 collected, 5 fail ·
Phase 15: ~1965 collected, 0 failures — while the
CHANGELOG's Phase 15 section simultaneously says the
count was "updated to ~2206" · Phase 16 / AUDIT_17:
2206 passed, 0 failures, 27 skipped. Version spine:
0.1.0 (Ph1) → 0.2.0 (Ph3) → 0.3.0 (Ph4) → 0.4.0 (Ph11) →
0.5.0 (Ph12) → 0.6.0 (Ph13) → 0.7.0rc1 (Ph14) → 0.7.0
(Ph15) → 0.8.0 (Ph16). The tree today agrees with the
final version claim at file level: `pyproject.toml` and
`src/hamr/__init__.py` both say **0.8.0**.

## Verification method (binding on E-138–E-140)

1. **Runner counts only.** Every test claim is re-measured
   with the member's own suite in the E-005 shapes
   (default env, and with-declared-deps from an isolated
   target dir), per-file where a claim is per-file. A
   claim passes only if the runner reproduces it within
   the stated tolerance (exact where the doc is exact).
   `def test_` counts (46 test files, 2065 defs in
   `Hamr/tests/` today) are inventory, never proof —
   parametrisation makes runner counts larger.
2. **Symbol-level existence.** Every named module/class/
   function claim is checked by tree-wide symbol search.
   A claim naming a symbol that does not exist is graded
   NOT PROVEN *as written*, even if a differently-named
   equivalent exists; the equivalent is recorded beside it.
3. **Artefact-level existence.** Every named file path is
   checked at that path. A capability at another path is
   a PARTIAL with the real path named.
4. **Environment is part of the claim.** Proofs are graded
   per environment: VM-bare, VM-with-deps, Blender-host,
   Pi 5, external service (TestPyPI / GitHub / VRChat).
   A claim whose environment this house cannot supply is
   graded NOT PROVEN with the missing environment named —
   never silently passed, never silently failed.
5. **No README is touched**, no Hamr code is changed, in
   the verification slices; fixes belong to E-142's
   re-roaded remainder.

## The plan by phase

### Phases 1–5 — the CHANGELOG-only years (→ E-138)

| Claim (CHANGELOG) | Proving artefact | Pass criterion |
|---|---|---|
| Ph1 "The Spec": CharacterSpec, YAML loading, validation, round-trip, error hierarchy, **13 tests** | `src/hamr/core/spec.py`, `models.py`, `errors.py`; runner on `tests/test_spec.py` | Symbols exist; runner reproduces 13 passed (today: 13 `def test_` in that file — the one claim whose def-count already matches) |
| Ph2 "Form": Blender Bridge (runner/scene/mesh_ops), Texture Forge, Body Forge (8 presets), Export Forge | `src/hamr/blender_bridge/`, `core/textures.py`, `body/forge.py` + `body/presets.py`, `export/`; runner on `tests/test_phase2.py` (28 defs) | Symbols exist; phase file green in the with-deps shape; Blender-dependent assertions graded per environment 4 |
| Ph3 "The Quench": Blender-side build script (540 lines claimed), MB-Lab map (29 bones) + TurboSquid map (55), expression maps, HSV tinting, height scaling, VRM metadata, post-export validation | `src/hamr/scripts/build_avatar.py` (line count + map sizes counted from code); runner on `tests/test_phase3.py` (21 defs) | Counts reproduced from code, not docs; file green with-deps |
| Ph4 "Tempering": BuildPipeline orchestrator, PipelineResult, check_environment(), validate_only(), CLI commands, example specs | `core/pipeline.py`, `cli.py`, `examples/minimal.yaml` + `runa_gridweaver.yaml` (both present); runner on `tests/test_phase4.py` (20 defs) | Symbols + CLI `--help` surface match; file green with-deps |
| Ph5 "Sharpening": TURBOSQUID_EXPRESSION_MAP (14 expressions), Blender E2E integration tests, "Blender 3.4.1 + VRM addon + MB-Lab confirmed on Pi 5", CLI integration tests | Symbol + count in `face/expressions.py` kin; runner on `tests/test_phase5.py` (21 defs) | Map count reproduced; the Pi 5 environment claim is **external** — NOT PROVEN unless Pi evidence is produced in Part IX |

### Phase 6 — the missing phase (→ E-138, docket 38)

No claim for Phase 6 exists in any Hamr doc, changelog
section, or test file this slice could find (tree-wide
searches for "Phase 6" return nothing; the CHANGELOG jumps
from Phase 5 [0.2.0] to Phase 11 [0.4.0], with [0.3.0]
carrying Phases 4–5). **Verification artefact: the absence
itself**, re-proven in E-138 by the same searches. Verdict
prepared: Phase 6 is UNACCOUNTED — either it never
existed as a phase, or its record lives outside this tree
(the standalone Hamr repo is the named suspect; cf.
E-005's stale-layout finding). Part IX records it; it
does not invent a Phase 6.

### Phases 7–10 — the test-file phases (→ E-138)

The only claims are the test files themselves, three
`__init__.py` docstrings asserting Phase 7 complete, and
the RELEASE_NOTES phrase placing a working pipeline
across "Phases 7–14".

| Claim | Proving artefact | Pass criterion |
|---|---|---|
| Ph7 complete (docstrings ×3; `test_phase7.py`, 34 defs) | Runner on `tests/test_phase7.py`; the hair/clothing/face package surfaces the docstrings head | File green with-deps; docstring claim graded on that alone and recorded as docstring-grade evidence |
| Ph8 (`test_phase8.py`, 18 defs) | Runner on the file | Green with-deps |
| Ph9–10 (`test_phase9_10.py`, 21 defs; Phase 11 doc calls Ph10 "the Final Quench") | Runner on the file | Green with-deps |

### Phase 11 — Alvíssmál (→ E-139)

Eight tasks (T1 stub bones 25/25 · T2 HairForge, 5 styles ·
T3 ClothingForge, 6 patterns · T4 WeightPaintEngine ·
T5 RigVerifier + CLI · T6 PerfBudget, Pi 5 tiers ·
T7 PresetLoader, 6 presets · T8 spring bones + first-person),
a module map with per-file line counts, and **556 tests**
across 9 named test files.

- **Artefacts:** the 9 named modules under `src/hamr/`
  (all 9 exist at their claimed paths — verified as
  inventory in this slice) + the 9 named test files run
  per-file (def counts today: stub_bones 45, hair_mesh 59,
  clothing_mesh 55, weights 47, verify 64, perf 44,
  presets 53, spring_bones 45, first_person 44).
- **Pass:** per-file runner counts reproduce the doc's
  implied totals and the phase total reaches 556 in the
  with-deps shape; module line counts within rounding of
  the map; the 25/25 bone claim proven by the verifier's
  own tests plus `VRM_25_BONE_NAMES` in
  `core/constants.py` (present, line 238).
- **Environment split:** the "<45s on Pi 5" build target
  (T6) is a Pi claim — external, graded separately.

### Phase 12 — Yggdrasil (→ E-139)

Seven tasks (pipeline integration, build-avatar wiring,
CLI, anime materials, expressions, collision, perf gate),
**1159 tests with 4 admitted failures**, and three named
new modules — of which `hamr/materials/forge.py`
(`MaterialForge`) and `hamr/rigs/colliders.py`
(`CollisionForge`) **do not exist at those paths and
those class names exist nowhere** (docket 41; nearest
real symbols: `materials/anime.py`'s
`AnimeMaterialGenerator`, `rigs/collision.py`'s
`CollisionMeshGenerator`, `face/expressions.py`'s
`ExpressionBinder`). The claimed integration suite
`tests/test_e2e_pipeline.py` likewise does not exist
(nearest: `test_e2e_build.py`, `test_e2e_suite.py`,
`test_build_integration.py`).

- **Artefacts:** symbol searches (above); runner on
  `test_pipeline_integrate.py` (55 defs),
  `test_materials.py` (88), `test_expressions.py` (58),
  `test_collision.py` (55), `test_perf_gate.py` (49),
  `test_cli.py` (59); `scripts/build_avatar.py` stage
  wiring read against the T2 stage list.
- **Pass:** each task graded separately — wiring and CLI
  claims can pass while the two named-module claims are
  graded NOT PROVEN as written (rule 2). The phase total
  is re-measured whole-suite; the doc's own 4 failures
  mean "COMPLETE with known failures" is the strongest
  verdict available for its test claim.

### Phase 13 — Vǫllr Vígríðar (→ E-139)

Seven tasks with unusually falsifiable per-task counts
(regression 33 · textures 70 · validator 64 · animation
84 · docs 36 · a11y 75 · GPU profiles 51) and a total of
**1569 passed with 7 admitted pre-existing failures**.

- **Artefacts:** the 7 named modules (all exist at
  claimed paths: `core/texture_procedural.py`,
  `export/vrm_validator.py`, `export/animation_clips.py`,
  `docs/generate.py`, `core/a11y.py`,
  `core/gpu_profiles.py`, `core/validate.py`) + per-file
  runner counts (def counts today: regression 40,
  texture_procedural 71, vrm_validator 64,
  animation_clips 66, docs_generate 36, a11y 75,
  gpu_profiles 51 — three already match their claims at
  def level, animation_clips' 84 must come from
  parametrisation or not at all).
- **Pass:** per-task runner counts match claims; the
  whole-suite re-run states the failure count honestly
  against the admitted 7.

### Phase 14 — Gjallarhorn (→ E-140, docket 39)

No COMPLETE claim exists to verify — the verification
*is* that finding, plus task-level grading of the plan's
seven tasks (14.1 E2E suite · 14.2 Blender CI matrix ·
14.3 perf benchmarks · 14.4 preset rework · 14.5 PyPI
packaging · 14.6 RC 0.7.0rc1 · 14.7 docs/a11y audit)
against what the tree holds (e.g. `test_benchmark.py`,
`core/preset_versions.py` + `test_preset_versions.py`,
`test_packaging.py`, `docs/a11y_audit.py` +
`test_a11y_audit.py` — all present as inventory).
The CHANGELOG's sole detailed Phase 14 claim (T6:
RELEASE_NOTES + MIGRATION + CONTRIBUTING written,
version 0.7.0rc1) is graded on file presence — all three
docs exist — while noting the tree's version has since
moved to 0.8.0, so the rc1 version claim is historical
and can only be graded from the CHANGELOG's own record.

### Phase 15 — Vápnatak (→ E-140)

Seven tasks and **six promotion checks**, of which at
least one is already falsifiable from inventory:
check 5, "ci_configured — `.github/workflows/ci.yml`
present", names an artefact that **does not exist
anywhere under `Hamr/`** in this tree (docket 42; the
standalone-repo layout E-005 already flagged as STALE in
the release-promotion tests). Other checks: version
consistency at 0.7.0 (historical; tree now 0.8.0),
test_count ≥1900, no_failures, docs_complete (the five
named docs all exist), source_files_present.

- **Artefacts:** `.github/` search (absence re-proven);
  runner whole-suite for the ≥1900 / 0-failures claims
  against E-005's measured 2170 / 28-failed truth;
  `blender_bridge/e2e.py`, `core/regression.py`,
  `core/release.py`, `docs/api_reference.py` symbol
  checks (all present as inventory); per-file counts for
  `test_e2e_build.py` (60 defs — matches the claimed 60),
  `test_regression_baseline.py` (62 — matches 62),
  `test_release.py` (25 — matches 25).
- **External claims graded separately:** GitHub Actions
  actually running, the v0.7.0 tag on a Main branch, and
  any release pipeline execution are outside this tree
  (no `.github`, single-import git history) — NOT PROVEN
  from in-tree evidence, whatever the unit tests say.

### Phase 16 — Mjölnir (→ E-140)

Seven tasks; the spine claim **2206 passing, 0 failures,
27 skipped** at v0.8.0.

- **Artefacts:** version pair (both files say 0.8.0 —
  the claim's file-level half already holds); whole-suite
  runner in both E-005 shapes as the count's proof or
  disproof; symbol checks with the rule-2 caveat —
  `materials/mtoon.py` exists but its class is
  `MToonConfig`-headed, not the claimed `MToonShader`
  surface as named in the CHANGELOG, `rigs/spring_tuning.py`
  exists, and the claimed `rigs/pose_library.py` /
  `PoseLibrary` **do not exist** (real: `rigs/poses.py`)
  (docket 41). Per-file def counts: mtoon 88 vs "100+
  tests" claimed, spring_tuning 65 vs "80+", poses 59
  vs "90+" — parametrisation must carry all three
  claims or they fall.
- **External claims:** the TestPyPI dry-run (T5), the
  v0.7.0 merge/tag (T4), and README badges (T6 — the
  README itself is never touched by this campaign; its
  content is read-only evidence) are graded NOT PROVEN
  unless Part IX produces the external artefacts.

### Phase 17 — Hamreisa (→ E-140, docket 40)

Not a completion claim: a *proof-of-life* claim set.
`PHASE_17.md` §III states must-pass criteria (a `.vrm`
file written; parseable VRM 1.0 container; all 22 stages
complete; Blender exits 0) and should-pass criteria
(validation clean; bones + mesh present; **<60 min and
<7.5 GB on Pi 5**). `AUDIT_17.md` claims a Pi-side
pre-flight (Blender 3.4.1, VRM addon, MB-Lab 1.7.8,
324 GB free, 11 GB RAM, suite 2206/27) and three blockers
FIXED in `build_avatar.py` (FP-1 `vrm_addon_extension`
on the Object — in-tree spot-check in this slice: line
852 reads `armature.vrm_addon_extension`, the fixed
shape; FP-2 single canonical `MB_LAB_BONE_MAP` in
`core/constants.py` — present, line 238; FP-3 CANCELLED
retry-then-raise).

- **Artefacts:** for FP-1/2/3, the named code sites read
  in full in E-140 (the spot-checks above are plan-grade,
  not verdicts); for the raising itself, a real `.vrm`
  artefact + build log on a Blender host — **absent
  today**: no `.vrm` file exists in the tree, Blender is
  not installed on the VM (E-006), and the Pi environment
  is external. Prepared verdict unless Part IX gains a
  Blender host: the first full raising is **NOT PROVEN**,
  and E-143/E-154 inherit that honestly.
- AUDIT_17's own residue (`remaining_conflicts.py`:
  reverse bone maps in `animation_clips.py` / `verify.py`,
  mixed bone-name regions in three more files, "address
  in Phase 18") is carried as the seed of E-142's
  re-roaded remainder.

### Cross-cutting claims (→ E-140)

| Claim | Artefact | Note |
|---|---|---|
| Suite spine 2206 / 0 / 27 at 0.8.0 | Whole-suite runner, both shapes | E-005 measured 2170 / 28 / 33 / 2E with-deps; the gap *is* the verification |
| "Runs on Pi 5" family (<45s Ph11/12, <60min Ph17, AUDIT_17 environment) | Pi 5 hardware evidence | External; NOT PROVEN from the VM |
| VRChat upload validation (Ph11 metric, Ph12 suggestion) | VRChat session evidence | External; no in-tree artefact exists or could |
| TestPyPI dry-run (Ph15 T5 kin, Ph16 T5) | TestPyPI project page / twine log | External |
| CI configured + running (Ph15 T2, promotion check 5) | `.github/workflows/*` | **Absent in-tree** (docket 42) |

## Execution order for Part IX

- **E-138** (earliest): Phases 1–10 per this plan —
  CHANGELOG-claim grading, the Phase 6 absence, the
  phase test files. Pure-Python; no Blender needed
  except where a claim names it (graded per rule 4).
- **E-139** (middle): Phases 11–13 — the documented
  forge and the hardening pass; per-file runner counts
  against the docs' own tables.
- **E-140** (latest): Phases 14–17 + the cross-cutting
  table — the release line, the external claims, the
  Hamreisa criteria — and publication of the full
  PROVEN / PARTIAL / NOT PROVEN table the roadmap
  demands, feeding E-142's remainder and E-150's doc
  reconciliation.

## Carried to the E-016 docket

(38) Phases 1–10 have no phase documents: Phases 1–5
survive only as CHANGELOG lines, Phase 6 has **no claim
anywhere in the tree**, and Phases 7–10 rest on test
files plus three "Phase 7: Complete" docstrings. Any
future phase history written for 1–10 is reconstruction
from those artefacts, labelled as such.
(39) Phase 14 has no COMPLETE artefact: its plan's seven
tasks stand unchecked, the CHANGELOG details only T6,
and its completion is assumed by Phase 15 rather than
claimed anywhere. Part IX grades it task by task.
(40) Phase 17 is a vision, not a completion: its own
must-pass criteria (a real `.vrm`, 22 stages, clean
Blender exit, on Pi 5) are unevidenced — the tree holds
no `.vrm` file at all (`build_output/test.vrm` is a
directory holding a preset YAML) and no Blender host is
available to this campaign today. The first full raising
stands NOT PROVEN until Part IX or E-143 produces one.
(41) Named-module claims that fail as written:
`hamr/materials/forge.py` / `MaterialForge`,
`hamr/rigs/colliders.py` / `CollisionForge`,
`hamr/rigs/pose_library.py` / `PoseLibrary`, and the
suite `tests/test_e2e_pipeline.py` do not exist; real
equivalents live at `materials/anime.py`,
`rigs/collision.py`, `rigs/poses.py`,
`face/expressions.py`, and the e2e test trio. Part IX
grades the claims as written (rule 2) and names the
equivalents; E-150's reconciliation records the truth.
(42) The Phase 15 promotion check "ci_configured —
`.github/workflows/ci.yml` present" is false in this
tree: no `.github` exists anywhere under `Hamr/` (kin
to E-005's STALE release-promotion finding — those
tests judge the standalone repo's layout). The check
could only have passed in the standalone repo.
(43) The test-count spine contradicts itself across the
COMPLETE docs (Phase 15: ~1965 collected in its
COMPLETE doc, ~2206 in its CHANGELOG section, for the
same version; Phases 12 and 13 titled COMPLETE while
admitting 4 and 7 failures) and against the campaign's
measured baseline (E-005). All counts in Part IX come
from the runner only.
(44) A family of claims is unprovable from this tree —
Pi 5 timings and environment, VRChat validation,
TestPyPI publication, GitHub release/tag/CI execution.
Each is named in this plan with the external artefact
that would prove it; absent that artefact Part IX
grades it NOT PROVEN, per environment rule 4.
(45) AUDIT_17's `remaining_conflicts.py` residue —
stale reverse bone maps in `animation_clips.py` and
`verify.py`, mixed bone-name regions in `weights.py`,
`spring_bones.py`, `clothing/mesh.py` — is noted-not-
fixed by its own author and assigned to Phase 18,
which does not exist in this tree. It seeds E-142's
re-roaded remainder.

## Slice gate

Root suite re-run in the E-001 shape (pgvector file
excluded, default env) as this slice's no-change gate —
see CAMPAIGN_STATE.md for the count. Doc-only slice: no
code touched, no README touched, no push. Raw claim
sources live outside the repo under
`~/workspace/.verify-tmp/ember-e010/`.

*Filed by the E-010 slice, 2026-10-31. Next: E-011 — the
two-Kistas boundary doc.*

# E-014 — Dead / Duplicate Census

*Project Ember campaign, Part I (The Monorepo's True State).
Measured 2026-10-31 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), at campaign
commit 944af88 (E-013 banked + its push record). Method: the
tracked tree enumerated via `git ls-files -z` (3,243 files,
217,404,018 bytes); every tracked file sha256-hashed for the
exact-duplicate census; image files magic-byte-checked
(PNG/JPEG signatures); Python imports in `src/ember` AST-parsed;
module-stem reference scan over all tracked `.py`/`.md`/`.toml`/
`.yaml` text (a module whose stem appears in no other tracked
text file is a *candidate*, then hand-classified — test files
are pytest-discovered entry points, not imports, and are never
called dead for lacking a referrer). Raw inventories live in
`~/workspace/.verify-tmp/ember-e014/`. **Nothing was removed,
moved, or renamed by this slice** — removals are Volmarr's word
(roadmap §5); this census prepares the verdicts for E-018.*

## Headline — read this first, in plain words

**The tree is far less duplicated than its size suggests, and
its core has no dead modules at all.** Across 217 MB of tracked
files there are only **11 non-trivial exact-duplicate groups**
(4,312,510 wasted bytes total, ~2% of the tree), and every one
is now named below. The Ember core's 50 non-package Python
modules are *all* referenced somewhere else — zero dead core
modules by the stem scan, re-proving the UNWIRED inventory's
"zero orphans in `src/ember/`" at module level.

The real dead weight is concentrated and specific:

- **2,548 lines of unwired Runa-era reward/mood code sit in
  Verdandi's heartbeat** — four modules nothing in the tree
  references, imports, or dynamically loads. (→ docket 59.)
- **Four "PNG" files in Verdandi are not images at all** —
  each is a single newline byte, invalid as PNG, referenced
  nowhere in the pre-campaign tree. (→ docket 60.)
- **Generated artefacts are tracked as if they were source:**
  Godot editor `.tmp` files in Open-VTT and a `build_output/`
  directory in Hamr. (→ docket 61.)
- **The same house images and two house texts are filed in
  two or three member homes at once** — the triplication
  E-003 asked about, now measured. (→ docket 62.)

And two things that *look* dead are not, and are recorded
as such so no future worker "cleans" them: the Stofa TUI
design tree (74 docs, no code — dormant by design, awaiting
its ADR) and the archived Runa skeleton (48 files —
provenance, kept deliberately).

## 1. Exact duplicates — the whole list

Every sha256 group with more than one member, at HEAD
944af88 (the 15 zero-byte files — package `__init__.py`s,
`py.typed` markers, one `.gitkeep` — are one group by
construction and are *correct*, not duplicates in any
actionable sense):

| Group | Copies | Wasted bytes | Classification |
|---|---|---|---|
| `mempalace_logo.png` — mempalace `assets/` + `landing/` + `website/public/` | 3 × 696,260 | 1,392,520 | **Intentional distribution** — a website, a landing page, and an asset folder each serve the file statically; this is how static sites work. Not a defect |
| `IMG_0666.jpeg` — `assets/` + `Verdandi/` + `kista/` | 3 × 412,183 | 824,366 | Accidental triplication (→ 62) |
| `IMG_0665.jpeg` — `assets/` + `Verdandi/` + `kista/` | 3 × 384,016 | 768,032 | Accidental triplication (→ 62) |
| `MIT_license_Rune_Forge_AI.jpeg` — `assets/` + `Verdandi/` | 2 × 417,771 | 417,771 | Accidental duplication (→ 62) |
| `image-23-RuneForgeAI.jpg` — `Hamr/` + `astrology-engine/` | 2 × 398,899 | 398,899 | Accidental duplication (→ 62) |
| `IMG_0407.jpeg` — `Hamr/` + `astrology-engine/` | 2 × 381,677 | 381,677 | Accidental duplication (→ 62) |
| `Volmarr_writings_philosophy.md` — `docs/philosophy/` + `Verdandi/research/02_…` + `Hamr/` | 3 × 38,777 | 77,554 | One canonical text, three homes (→ 62) |
| Open-VTT `Cha4A8.tmp` = `ChaED65.tmp` | 2 × 31,970 | 31,970 | Generated artefacts (→ 61) |
| `WORLD_MODELING_SKILL.md` — `docs/design/` + `mempalace/` | 2 × 18,597 | 18,597 | One text, two homes (→ 62) |
| Hamr preset YAML — `build_output/` + `build_output/test.vrm/` | 2 × 1,121 | 1,121 | Generated artefacts (→ 61) |
| Verdandi 1-byte pseudo-PNGs | 4 × 1 | 3 | Broken placeholders (→ 60) |

**Totals: 12 groups (incl. the zero-byte group), 43 files in
groups, 4,312,510 wasted bytes — of which 1,392,520 are the
intentional mempalace logo distribution, leaving 2,919,990
bytes of accidental/generated/broken duplication.**

This answers E-003's open question directly: E-003 proved the
*new root* images (`IMG_0861–0879` + 3 large PNGs) duplicate
nothing in `assets/`; this census extends the comparison to
the whole tree — **those 22 root files duplicate nothing
anywhere** — while the *older* ORIGINS images (`IMG_0665`,
`IMG_0666`, the licence image) are exactly where the
cross-member duplication lives: each member import of
2026-05-21 carried its own copies of the house pictures.

Near-duplicates by *name* are not duplicates by content:
Python files sharing a basename (`__init__.py` ×many,
`config.py`, `test_*.py` across members) all differ in
content — there is **no duplicated Python code file anywhere
in the tree** (no non-empty `.py` sha256 group exists).

## 2. Broken and placeholder files

- **The four pseudo-PNGs** (→ 60): `Verdandi/656lk65l.png`,
  `65765gf5645.png`, `8328732kjdjmsd.png`, `k0rai4k0rai4k0ra.png`
  — each exactly 1 byte (`\n`), failing the PNG magic check.
  They are the *only* invalid images in the tree: every other
  `.png` passes its signature check and **all `.jpg`/`.jpeg`
  files (0 failures) are real JPEGs. Stem-reference scan:
  no pre-campaign file references any of the four names (the
  only referrers in the current tree are this campaign's own
  E-002/E-003 census docs). They arrived in the single
  Verdandi import commit (7da4077). Whatever upload produced
  them, no image ever landed — they are placeholders for
  pictures that do not exist in this tree.
- **`THE_CYBER-VIKING_UX_CODEX.md` is a 25-byte stub** (→ 63):
  its entire content is its own title line, no newline, no
  body. E-003 listed it among the unregistered root loose
  files; it is a codex that was never written, or whose body
  lives elsewhere — either way the file as tracked is a
  dead document, and the Design Lawbook it presumably meant
  to carry is separately present in full at root
  (`Volmarr_Cyber_Viking_Master_Visual_Design_Lawbook.md/.pdf`).
- **`mempalace/AGENTS.md` is a 9-byte pointer** whose whole
  content is the text `CLAUDE.md` — a redirect stub for
  agent tooling, functional as a pointer, recorded here so
  it is not mistaken for a lost document.
- **Tiny-but-live files, explicitly not dead:** `.python-version`
  files, `CloakBrowser/cloakbrowser/_version.py`, the
  dictionary's `export {};` support stub, mempalace's website
  `CNAME` — all small, all doing their one job.

## 3. Dead and unwired code

### 3.1 The core is clean; the monorepo is unwired *by design*

- **AST import census of `src/ember`:** 100 distinct import
  roots, **zero** of them any sibling member (no verdandi,
  kista, mempalace, mimir, seidr, astrology, bifrost, hamr,
  or cloakbrowser import exists in the core). This re-proves
  from the import graph what E-011/E-012 found by grep:
  the members are neighbours, not organs — exactly as
  `docs/UNWIRED_INVENTORY.md` (§3) states its design to be.
  Unwired ≠ dead: each member's own road (Parts IV–XI)
  decides its binding.
- **Core module stem scan:** all 50 non-`__init__` modules
  under `src/ember/` are referenced by at least one other
  tracked text file — **zero candidate-dead core modules**.
- **The stem scan's 76 unreferenced `.py` files tree-wide
  are overwhelmingly test files** (pytest discovers them;
  nothing imports them; that is their correct shape) plus
  the genuine items below. Calling tests dead for lacking
  importers would be a category error, and this census
  does not make it.

### 3.2 The genuine dead code: Verdandi's Runa reward/mood modules (→ 59)

Four modules in `Verdandi/heartbeat/`, **2,548 lines total**,
whose stems appear in *no* other tracked text file in the
whole tree, which no import reaches, and which Verdandi's
one dynamic loader (in `conversation_logger.py`, loading
`nervous_system` by path) does not touch:

| Module | Lines | What it holds |
|---|---|---|
| `runa_mood_arousal_system.py` | 1,105 | A standalone mood/arousal system |
| `runa_reward_system.py` | 613 | A standalone `RewardSystem` |
| `runa_negative_system.py` | 609 | Its negative-signal counterpart |
| `push_reward.py` | 221 | A reward-push helper with its own flow |

All four are Runa-named, pre-fork in spirit, and sit beside
the live heartbeat (`core.py`, `reactor.py`, `actions/`,
`checks/`) without being part of it: E-006 proved the hub
boots and serves *without* them, and E-009's concordance
found VD-RM gives them no roadmap coverage either. They are
the largest single block of provably-unwired code in the
tree. Their fate — wire them in Part IV, or verdict them —
belongs to E-059/E-060's re-cut; what Part I establishes is
that today they are carried weight: 2,548 lines the toaster
profile ships but never runs.

### 3.3 Standalone scripts — tools, generators, and one build artefact

Stem-unreferenced non-test scripts, hand-classified:

- **Generator scripts that already ran:** `docs/Open_LLM_VTuber_Mythic_Plan/gen_md.py`,
  `docs/WaifuOS_Mythic_Plan/generate_docs.py` + `generate_docs_v2.py`
  (two generations of the same generator kept side by side —
  the v1 is superseded in fact by its own v2). One-shot
  tools whose outputs are the plan corpora themselves;
  dead as *code to run again*, historical as provenance.
- **Standalone tools (live by invocation, not import):**
  `mimir-well/scripts/migrate_fact_store.py`,
  `mempalace/tools/render_jsonl.py` (referenced once in
  mempalace's own docs), `mempalace/benchmarks/mine_bench.py`.
  Unwired but not dead — a script you run by name is its
  own entry point. Recorded to prevent a false verdict.
- **A generated script tracked as source:**
  `Hamr/build_output/e2e_build_anime_girl_default.py` —
  sits in build output, referenced nowhere (→ 61).

## 4. Tracked generated artefacts and empty shells

- **Open-VTT Godot `.tmp` files** (→ 61): three tracked
  editor temp files — `Godot/UI/Cha4A8.tmp` and
  `ChaED65.tmp` (byte-identical, 31,970 B each) and
  `Godot/components/rol9FDB.tmp` (1,477 B) — 65,417 bytes
  of Godot editor working state, referenced by nothing,
  imported in the single Open-VTT commit (a01008d).
  `.tmp` files are by definition the editor's scratch,
  not the project's source.
- **Hamr `build_output/`** (→ 61): 5 tracked files,
  10,185 bytes — three default spec/preset outputs
  (one preset duplicated into the `test.vrm/` directory
  that E-010 found impersonating a VRM file), the
  generated e2e script above, and that directory. Build
  output tracked in git is weight every clone pays for
  artefacts the build itself regenerates.
- **The scaffolding shells** (→ 64): `scripts/` (4 files),
  `tools/` (4), `examples/` (5) — **13 Markdown files,
  12,921 bytes, zero code, zero non-Markdown content of
  any kind**, exactly as E-002 found them: per-directory
  READMEs describing contents that never arrived. The
  drift detector E-003 found missing (`tools/repo/…`)
  is one of the ghosts these shells describe. Beside
  them, `vendor/` (1 README, 993 B) still claims the
  vendored estate lives there while CloakBrowser sits
  at top level — E-003's standing mismatch, not
  renumbered here.
- **No `__pycache__`, `.pyc`, or `node_modules` content
  is tracked anywhere** (0 files each) — the tree's
  hygiene on the usual generated classes is clean;
  §4's items are the exceptions, not the pattern.

## 5. Dormant by design — explicitly NOT dead

- **The Stofa TUI design tree:** `docs/tui/` — 74 files,
  513,278 bytes, zero code. UNWIRED §4 states its status
  plainly: intentionally pre-implementation, awaiting a
  not-yet-drafted ADR-0015. A design tree awaiting its
  decision is dormant, not dead; the verdict on building
  it is Volmarr's, at his pace.
- **The archived Runa skeleton:** `docs/archive/` — 48
  files, 154,975 bytes, including the `src-skeleton/`
  package ghosts. An archive is kept *because* it is no
  longer live; E-003 already traced the fork lineage
  through it. Provenance, not dead weight.
- **ADR-0012's absence, resolved as far as the tree
  allows:** E-003 recorded ADR 0012 missing from the
  decisions sequence with no explanation in ORIGINS.
  UNWIRED §5.4 supplies the explanation the register
  lacked: 0012 is a *placeholder* ADR (Auga / Rödd /
  Bifröst) that "hasn't ratified" — a number reserved,
  never a document lost. The register gap stands for
  E-196 to record; the mystery does not.
- **The sibling members themselves:** §3.1 — unwired
  from the core by the monorepo's own stated design,
  each with its own part of this roadmap. E-012's
  correction stands with them: UNWIRED's mempalace
  characterisation ("likely abandoned") is stale
  (docket 52), its isolation fact is not.

## 6. Cross-references — already docketed, not renumbered

- The `.env.example` fossil (E-013, **docket 55**) is this
  census's dead-*documentation* kin: dead docs for absent
  adapters, classified there, assigned to E-033.
- Ragnarok's scaffold-without-content (E-008, docket
  26–30's kin) is the codex-shaped instance of §2's stub
  pattern; its reconciliation is E-165's, not repeated here.
- The Hamr `test.vrm/`-that-is-a-directory finding is
  E-010's (docket 38–45's kin); §4 above adds only its
  duplicated preset.
- THIRD_PARTY_NOTICES' staleness is E-003/E-007's
  (docket 18–25's kin) — a stale skeleton, not a dead file.

## 7. What the later slices inherit

- **E-015** (budget archaeology): §1's 2,919,990 accidental
  bytes and §3.2's 2,548 unwired lines are measured weight
  the budget book can cite by file.
- **E-016** (docket): items 59–64 below.
- **E-018** (Part I gate): §§1–4 are its verdict-preparation
  material — every removal proposed there is Volmarr's word.
- **Part IV (E-059/E-060):** docket 59's four modules are
  the re-cut's first wire-or-verdict decision.
- **Part X (E-157/E-158):** docket 61's Open-VTT half.
- **Part IX (E-137+):** docket 61's Hamr half.

## Carried to the E-016 docket

(59) Verdandi heartbeat carries 2,548 lines of provably
unwired Runa-era code: `runa_mood_arousal_system.py`
(1,105 lines), `runa_reward_system.py` (613),
`runa_negative_system.py` (609), `push_reward.py` (221) —
no import, no reference, no dynamic load anywhere in the
tree; the hub boots and serves without them (E-006) and
VD-RM gives them no coverage (E-009). Assigned to Part IV
(E-059/E-060): wire them deliberately under the event
contract, or verdict-prepare them — carried weight on the
toaster profile until one of those happens.
(60) Four Verdandi files named as PNGs are 1-byte newline
placeholders, invalid as images, unreferenced in the
pre-campaign tree, arrived in the Verdandi import commit:
`656lk65l.png`, `65765gf5645.png`, `8328732kjdjmsd.png`,
`k0rai4k0rai4k0ra.png`. The pictures they presumably
place-held do not exist in this tree. Assigned to E-018
(verdict preparation; removal is Volmarr's word) with
Part IV informed — if the pictures exist outside the
tree, only Volmarr knows where.
(61) Tracked generated artefacts: Open-VTT's three Godot
`.tmp` editor files (65,417 B, two byte-identical,
referenced by nothing) and Hamr's `build_output/`
(5 files, 10,185 B — regenerated outputs, one duplicated
preset, one generated e2e script, and the directory
E-010 found standing in for a `.vrm`). Assigned to
E-158 (Open-VTT) and Part IX (Hamr) for verdict
preparation; the general rule — build output and editor
scratch are not source — is E-018/E-200 material for the
campaign's own gate hygiene.
(62) Cross-member exact duplication of house material:
`IMG_0665.jpeg` ×3 and `IMG_0666.jpeg` ×3 (assets +
Verdandi + kista), the MIT licence image ×2 (assets +
Verdandi), `image-23-RuneForgeAI.jpg` + `IMG_0407.jpeg`
×2 each (Hamr + astrology-engine), `Volmarr_writings_philosophy.md`
×3 (docs/philosophy + Verdandi research + Hamr),
`WORLD_MODELING_SKILL.md` ×2 (docs/design + mempalace) —
2,886,896 wasted bytes in this item alone. No copy is
marked canonical, so the copies can silently diverge
(the texts are the sharp risk: a philosophy text edited
in one home is wrong in two others). Assigned to E-018
(verdict preparation — a canonical-home proposal per
item, removal always Volmarr's word) and E-057 (the
member budget table cites the weight). The mempalace
logo's three homes are *excluded* — intentional static
distribution, §1.
(63) `THE_CYBER-VIKING_UX_CODEX.md` at root is a 25-byte
title-only stub — a codex file with no body, while the
actual Design Lawbook it names stands complete elsewhere
at root. Dead documentation. Assigned to E-018 (verdict
preparation) / E-193–E-195 (docs and README care, where
its fate — write it, point it at the Lawbook, or retire
it — can be decided with the whole docs estate in view).
(64) Bootstrap scaffolding shells never filled:
`scripts/`, `tools/`, `examples/` hold 13 Markdown-only
files (12,921 B) describing contents that never arrived,
unchanged since the bootstrap census (E-002/E-003).
Assigned to E-018 (verdict preparation: fill, fold into
docs, or retire — per directory) — noting that E-016's
own drift-detector item already proposes one real
occupant for `tools/repo/`, so the shells' fate and the
detector's home should be decided together.

## Slice gate

Root suite re-run in the E-001 shape (pgvector file
excluded, default env; `TMPDIR` redirected to the
workspace overlay as in E-013): **546 passed, 6 failed,
12 skipped** — identical to the opening baseline; the 6
failures are the proven environment failures. Doc-only
slice, no code touched, no README touched. Push: under
Volmarr's 2026-10-31 standing go-ahead, this slice's
commit was pushed to origin `yrsa/ember-road-build`
after fetch + ancestry check and verified by
`ls-remote`: remote head = local head (recorded in the
state file).

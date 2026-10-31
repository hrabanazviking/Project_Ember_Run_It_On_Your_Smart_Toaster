# E-008 — The Codex Census

*Project Ember campaign, Part I (The Monorepo's True State).
Measured 2026-10-30 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), at campaign
commit f2b7696 (E-007 banked). Each of the five elder
`TASK_*_CODEX.md` commissions at the repo root was read in
full; its promised corpus was then counted in the tree —
file by file, by layer, with word counts — and its named
closing artefacts (manifest, index, reading order, slice-plan
revisions, decision records) checked for presence. This
slice censuses only: the verdicts on each codex (closed /
absorbed / retired) land in Part X (E-161–E-165), which
consume this census. Defects found are carried to the E-016
docket, continuing its numbering (items 26–30). Raw file /
word inventory is kept under
`~/workspace/.verify-tmp/ember-e008/`.*

## Headline

**Four of the five elder commissions were carried out in
fact; one was never authored at all.** Hermes, Chatdoll,
Super Agent Party (SAP), and Waifu all stand in the tree as
complete corpora — every content doc present, every content
doc carrying its promised `## What This Means for Ember`
closer, every content doc at or above its promised minimum
length, and each corpus closed by a Scribe meta pass (INDEX,
READING_ORDER, CROSS_AGENT_NOTES all present). **Ragnarok
stands scaffold-only: 3 meta files, zero of its 46 promised
content docs, no INDEX, no synthesis, nothing to reconcile
but the unexecuted commission itself.**

Two smaller truths ride along. First, **all five TASK files
still describe themselves as unstarted** — every one says
"Authoring (parallel)" and three say "pending agent
dispatch" — although four of the corpora they commission
were completed and committed in May 2026. The TASK files are
elder text and were not edited; their status lines are
simply stale (docket 27). Second, **no codex is consumed by
the product**: a search of `src/` finds no reference to any
codex corpus — the codices are a library the companion has
not yet drawn on, which is exactly what Part X's
reconciliations are for.

## Method

- Each TASK file's ask was taken from its own text: target
  folder, promised doc count, per-doc word range, licence
  posture, method (agents × layers), and its named Next
  Steps / closing artefacts.
- The tree was counted directly: every `*.md` under each
  `docs/<name>_codex/` (and `docs/ragnarok_codex/`), split
  content vs `meta/`, per layer folder, with whitespace
  word counts per file.
- Completeness evidence: presence of the meta set
  (SHARED_CONTEXT, MANIFEST, STYLE_GUIDE, INDEX,
  READING_ORDER, CROSS_AGENT_NOTES), presence of the
  synthesis docs each TASK names in its Next Steps, the
  Ember-closer in every content doc, and `git log` per
  corpus (authoring commits are in the imported history —
  the members arrived in this monorepo with their history
  of record, cf. E-002).
- Counting note, applied uniformly: a corpus's **content**
  count excludes its `meta/` folder; its **total** includes
  it. Sibling codices cite each other by total (e.g. "Hermes
  (58)"), while the TASK files promise content counts —
  both numbers are given for every codex below so Part X
  never has to guess which is meant.

## The census table

| Codex (TASK file, started) | Source mined (per TASK) | Licence posture (per TASK) | Promised | In tree (content + meta = total) | Content words | Verdict |
|---|---|---|---|---|---|---|
| Hermes (`TASK_HERMES_CODEX.md`, 2026-05-22) | NousResearch/hermes-agent | MIT-friendly recommendations only | 53+ docs | 50 + 8 = **58** | 140,519 | **DONE-in-fact** (counting note below) |
| Chatdoll (`TASK_CHATDOLL_CODEX.md`, 2026-05-25) | uezo/ChatdollKit (Unity, C#) | Apache-2.0 — adopt freely with attribution | 63 content docs | 63 + 6 = **69** | 224,436 | **DONE-in-fact** |
| Super Agent Party (`TASK_SUPER_AGENT_PARTY_CODEX.md`, 2026-05-24) | heshengtao/super-agent-party | AGPLv3 — cite, do not vendor | 82 docs | 77 + 6 = **83** | 201,292 | **DONE-in-fact** (manifest note below) |
| Waifu (`TASK_WAIFU_CODEX.md`, 2026-05-25) | ZeroWeight-Engineering/waifu-chat-starter-kit | **No LICENSE in source — study-only**; prefer LiveKit (MIT) upstream | 15 content docs | 15 + 6 = **21** | 47,277 | **DONE-in-fact** |
| Ragnarok (`TASK_RAGNAROK_CODEX.md`, 2026-05-25) | Serg-Norseman/NorseWorld-Ragnarok (C#, archived) | GPL-3.0 — cite + reimplement; never vendor | 46 content docs | **0 + 3 = 3** | 0 | **PARTIAL — scaffold only** (content ABSENT) |

## Per-codex evidence

### Hermes — DONE-in-fact

- Layers present: vision 5, domain 10, interface 8,
  execution 12, verification 7, synthesis 8 = 50 content
  docs; meta 8 (the usual 6 plus CONTINUATION_BACKLOG and
  HERMES_REVISION, both Hermes-specific Scribe artefacts).
- Every one of the 50 content docs carries the
  `## What This Means for Ember` closer its TASK required;
  word counts run 1,809–4,640 (median 2,787): none under
  the 1,500 floor, 2 over the 4,000 ceiling.
- Its named closing artefacts exist:
  `60_synthesis/65_SLICE_PLAN_REVISIONS.md` and
  `66_DECISION_RECORDS.md` — the two docs its Next Steps
  send Volmarr to review.
- Counting note: the TASK promises "53+ technical MD
  documents" and its agent table sums to 53, a number that
  mixes content and meta assignments (the Scribe's 3+ are
  meta). Counted strictly, the corpus is 50 content + 8
  meta = 58 total — which is the "58" its sibling codices
  cite. The corpus is complete against its own MANIFEST's
  doc list and closed by its meta pass; the ambiguity is in
  the promise's arithmetic, not in missing docs (docket
  28). Git: landed as one Wave-1 commit (d52d8c2,
  2026-05-24, "58-doc … corpus").
- Licence note for Part X (E-163): its asks are re-pointed
  at the refreshed Hermes fork where they belong there —
  that judgement is Part X's, not this census's.

### Chatdoll — DONE-in-fact

- Layers present: vision 5, domain 14, interface 10,
  execution 14, verification 8, synthesis 12 = **63 content
  docs, exactly the promised 63**; meta 6. Its MANIFEST's
  own claim (69 files = 63 + 6) matches the tree exactly.
- All 63 content docs carry the Ember closer; word counts
  1,747–6,189 (median 3,436): none under the 1,500 floor,
  18 over the 4,000 ceiling — over-length, not absence.
- The synthesis prize its TASK named — the three-corpus
  triangulation (SAP local × Waifu cloud × Chatdoll
  Unity-native) — exists as `60_synthesis/60_TRIANGULATION.md`,
  alongside the Andlit Unity tier (61) and the decision
  records (67). Git: scaffold commit plus per-layer
  completion commits closing at the meta-finalization
  commit (80cf62d, 2026-05-25).
- This is the only codex whose source licence (Apache-2.0)
  gives adopt-with-attribution freedom — a fact Part X
  (E-161) will want beside Waifu's study-only posture.

### Super Agent Party — DONE-in-fact

- Layers present: vision 5, domain 14, interface 12,
  execution 23 (incl. the per-IM-bot 35a–h and
  per-livestream 36a–c subdocs its TASK commissioned),
  verification 10, synthesis 13 = **77 content docs**;
  meta 6; total 83.
- Its MANIFEST claims "82 documents (77 content + 5
  meta)": the content count is exact, the meta count is
  one short of the tree (6 meta files stand there) — the
  corpus is one file *more* than its manifest, not one
  short (docket 29).
- All 77 content docs carry the Ember closer; word counts
  1,515–5,921 (median 2,397): none under the floor (the
  TASK's 1,200 subdoc allowance was not needed), 6 over
  the 4,000 ceiling.
- Its named closing artefacts all exist: slice-plan
  revisions (67), decision records (68), integration
  roadmap (69), invented methods (66), and the new-vows
  argument (61). Git: Wave-3 commits closing at meta
  finalization (eb700de, 2026-05-24).
- Counting fog in the TASK itself, recorded not resolved:
  its Scope says 82 docs, its "What Exists Now" describes
  a "62-doc list" MANIFEST, and its agent table sums to
  80 assignments. The tree (77 + 6) matches the MANIFEST's
  content count, which this census treats as authoritative.

### Waifu — DONE-in-fact

- Layers present: vision 2, domain 3, interface 3,
  execution 2, verification 3, synthesis 2 = **15 content
  docs, exactly the promised 15**; meta 6; total 21. Its
  MANIFEST's claim (21 = 15 + 6) matches the tree exactly.
- All 15 content docs carry the Ember closer; word counts
  2,544–3,961 (median 3,147): none under its 1,500 floor;
  9 run over its tighter 3,000 ceiling but all inside the
  SAP-range 4,000 — over-length against its own stated
  range, recorded as such.
- Its named review docs exist: `60_synthesis/60_REALTIME_TIER_FOR_ANDLIT.md`
  and `61_DECISIONS_AND_INVENTIONS.md`, and its licence
  risk is handled inside the corpus itself
  (`50_verification/52_NO_LICENSE_RISK.md`) — the
  study-only posture its TASK demanded (no LICENSE in the
  source kit; LiveKit named as the adoptable upstream).
  Git: per-layer commits closing at meta finalization
  (df47af2, 2026-05-25).

### Ragnarok — PARTIAL (scaffold only; content ABSENT)

- In tree: `docs/ragnarok_codex/meta/` holds exactly 3
  files — MANIFEST (1,270 words), SHARED_CONTEXT (1,044),
  STYLE_GUIDE (643). **No content folder exists at all**:
  0 of 46 promised content docs; no vision, domain,
  interface, execution, verification, or synthesis doc;
  no INDEX, READING_ORDER, or CROSS_AGENT_NOTES.
- Its MANIFEST promises 52 files (46 content + 6 meta);
  even its meta set is half-landed (3 of 6), and the
  MANIFEST's own status marks STYLE_GUIDE "⏳ next" although
  the file stands written beside it — the scaffold's
  bookkeeping stopped mid-pass.
- Git proves this is the whole story, not a loss in the
  monorepo import: the corpus's only commit is a6cbd81
  (2026-05-25, "scaffold — 46-doc NorseWorld-Ragnarok
  corpus (Wave 6)") — the same commit that landed the
  TASK file. No authoring wave ever followed.
- Consequence for Part X: E-165 has no findings to
  reconcile — only an unexecuted commission, whose source
  (an archived, GPL-3.0, 23-year Norse roguelike) and whose
  teaching prize (Norse systematization, per its TASK) must
  be judged as a proposal, not as evidence. Whether the
  codex is ever authored is Volmarr's word at E-165, not
  this campaign's assumption (docket 26).

## Cross-cutting findings

1. **Status lines are stale in all five TASK files**
   (docket 27): Hermes and SAP say "Authoring (parallel,
   six agents)" (SAP adds "pending user approval of
   manifest"); Chatdoll, Ragnarok, and Waifu say "pending
   agent dispatch". Four of those five states are false in
   the tree today. The TASK files are elder text — this
   census is the correction of record; the files themselves
   were not touched.
2. **Sibling citations count totals, TASKs promise
   content** (docket 28): e.g. Chatdoll's TASK cites
   "Hermes (58), SAP (84), Waifu (22)" — totals in the
   first case, and numbers matching neither count in the
   other two (SAP: 77 content / 83 total; Waifu: 15 / 21).
   Any future citation should state which count it means;
   this census's table gives both.
3. **Over-length is common, under-length is absent**: no
   content doc in any completed corpus falls under its
   promised floor; 35 docs across the four corpora exceed
   their stated ceilings (Chatdoll 18, Waifu 9, SAP 6,
   Hermes 2). Not defects for Part X to fix — a calibration
   fact about how these commissions actually ran.
4. **Licence postures are exactly as E-007 found them in
   discussion**: Apache-2.0 adopt (Chatdoll), AGPL cite-only
   (SAP), GPL-3.0 cite/reimplement-never-vendor (Ragnarok),
   no-licence study-only (Waifu), MIT-friendly (Hermes).
   No codex corpus itself carries a licence conflict; no
   vendored code from any mined source was found in the
   tree by E-007's audit.
5. **The corpora are unread by the product** (docket 30):
   `grep` over `src/` for any codex reference returns
   nothing. Every codex ends in proposals
   (slice-plan revisions + decision records, present in
   all four completed corpora); none of those proposals
   has an in-code consumer. Part X's absorptions
   (E-166–E-168) are where that changes, if Volmarr's
   verdicts say so.

## Carried to the E-016 docket

(26) The Ragnarok codex was never authored: scaffold only
(3 of 6 meta files), 0 of 46 content docs, its MANIFEST's
own status already stale inside the scaffold; E-165 must
reconcile an unexecuted commission, and authoring it (or
retiring it) is Volmarr's word. (27) All five TASK_*_CODEX
status lines are stale ("Authoring / pending dispatch" over
four completed corpora and one abandoned scaffold) — elder
text, not edited; this census is the correction of record.
(28) Codex counting ambiguity: TASKs promise content
counts, siblings cite totals, and two sibling citations
(SAP "84", Waifu "22") match neither count in the tree
(SAP 77/83, Waifu 15/21); Hermes's "53+" promise mixes
content and meta assignments against its actual 50/58.
(29) SAP's MANIFEST undercounts its own corpus by one
(claims 82 = 77 + 5 meta; tree holds 83 = 77 + 6 meta) —
the corpus exceeds its manifest; the manifest is the
stale party. (30) No codex corpus is referenced anywhere
in `src/`: the four completed corpora's proposals have no
in-code consumer — the gap Part X's reconciliation and
absorption slices (E-161–E-168) exist to close, per
Volmarr's verdicts.

## Slice gate

Root suite re-run in the E-001 shape (pgvector file
excluded, default env) as this slice's no-change gate —
see CAMPAIGN_STATE.md for the count. Doc-only slice: no
code touched, no README touched, no push. Raw inventory
lives outside the repo under
`~/workspace/.verify-tmp/ember-e008/`.

*Filed by the E-008 slice, 2026-10-30. Next: E-009 — the
Verdandi concordance.*

# E-003 — ORIGINS Concordance

*Project Ember campaign, Part I (The Monorepo's True State).
Measured 2026-10-30 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), at campaign
commit a801431 (E-002 banked). Every claim in `ORIGINS.md`
(scribe Eirwyn Rúnblóm, last updated 2026-05-21) was checked
against the tree as it stands. Verdicts use the roadmap's four
words: **PRESENT** (there, as claimed), **MOVED** (not where the
claim's first form puts it, but at the place the register itself
records), **ABSENT** (not there, and no successor in its place),
**GROWN-BEYOND** (there, but materially more / other than the
register describes — including material the register never
mentions at all). This doc is the audit's spine: E-014
(dead/duplicate census) and E-016 (the bug & gap docket) draw
their ORIGINS items from it. ORIGINS itself was not modified —
the register is extended, never rewritten, and only at E-196.*

## Method

- Each register row was resolved to a concrete path (the claimed
  root name, or the target of its recorded Status), and the path
  was tested in the working tree; byte sizes were taken from the
  files themselves and compared with the sizes the register
  states.
- Root loose images were sha256-compared against `assets/` to
  distinguish duplicates from new material.
- `git log` was used only to confirm a successor's lineage where
  a claimed name is gone (config example, bootstrap anchor).

## Headline verdict

**The register is accurate about everything it covers — and it
does not cover the monorepo's second half.** Every §1 moved or
kept file is at its recorded place (24 of 25 rows; §1 detail
below). But ORIGINS' last update (2026-05-21, "post-slice-2
ratification") predates or coincides with the member imports of
that same evening (2026-05-21 18:22–19:22 EDT, per E-002), and
**none of the eleven imported member directories is registered
anywhere in ORIGINS**: Verdandi, kista, mempalace, mimir-well,
seidr_engine, astrology-engine, bifrost, Hamr, Open-VTT,
CloakBrowser (vendored), and the cleasby-vigfusson dictionary
have no provenance rows at all. Their provenance today rests on
the roadmap §2 and their own in-tree licences/docs, not on the
register. Closing that gap is an E-196 act (register extended
with the campaign's rows, scribed truthfully); Part I only
prepares it. The same is true, at smaller scale, for a population
of root loose files (§5 below).

## §1 — Root-level files (25 rows)

| Register claim | Verdict | Evidence |
|---|---|---|
| `LICENSE`, `NOTICE`, `LEGAL-NOTICE.md` keep-at-root | PRESENT | At root; 1,069 / 367 / 3,250 bytes |
| `THIRD_PARTY_NOTICES.md` keep-at-root, "skeleton; will fill in" | PRESENT, stale | Still 743 bytes; its body still names the project "Runa Agent" and even refers to "HERETIC" — a pre-fork skeleton never updated for Ember or for the vendored CloakBrowser. Content audit is E-007 / E-185 |
| `MYTHIC_ENGINEERING.md` keep-at-root, 7-line stub pointer | GROWN-BEYOND | Now a real 7,944-byte "how we build Ember" doc — exactly the expansion its own Notes predicted ("Expanded in P9"); its header records the parent version preserved at `docs/archive/runa-inherited/MYTHIC_ENGINEERING.md` (present) |
| 3 Mythic-Engineering canon files moved-to-`docs/methodology/` | MOVED, as recorded | All three present there; sizes match the register's claims (87,293 vs "~88 KB"; 165,073 vs "170 KB"; 29,226) |
| `PHILOSOPHY.md` keep-at-root | PRESENT | 4,342 bytes vs the register's "~4 KB" |
| 3 philosophy files moved-to-`docs/philosophy/` | MOVED, as recorded | All present; 29,666 / 38,777 / 25,967 bytes vs claimed 31 / 39 / 26 KB |
| 2 ecosystem docs moved-to-`docs/architecture/` + `docs/design/` | MOVED, as recorded | `Technical_Architecture…` 53,867 (claimed 55 KB); `WORLD_MODELING_SKILL.md` 18,597 (claimed 19 KB) |
| `RULES.AI.md` keep-at-root | PRESENT | 21,214 bytes (claimed 20 KB) |
| 6 Runa-design files moved-to-`docs/architecture/`, `docs/design/`, `docs/operations/` | MOVED, as recorded | All six present at their recorded targets, sizes within the register's rounding (46,502 / 63,985 / 18,618 / 34,096 / 40,766 / 30,309 / 35,399 across the set incl. the idea-harvest files) |
| `HERMES_OPENCLAW_DESIGN_ANTI_PATTERNS.md` moved-to-`docs/decisions/` | MOVED, as recorded | Present, 24,064 bytes (claimed 25 KB) |
| `config.yaml` (empty stub) moved-to-`config/runa.example.yaml` | ABSENT under the claimed name | Neither `config.yaml` nor `config/runa.example.yaml` exists. The functional successor is present: `config/ember.example.yaml` (6,353 bytes), whose git history runs through the fork-delta commit `045fda6` ("archive Runa skeleton, build src/ember/…") — the Runa-named example was retired in the fork, not lost. Lineage confirmation is an E-014 item |
| `README.md` keep-at-root, 41 KB | GROWN-BEYOND | Present at root, now 61,857 bytes. (Not read for content, not touched — campaign law) |
| `ORIGINS.md` stub replaced by the realised register | PRESENT | The register itself, 22,070 bytes |

**§1 tally: 24 of 25 rows stand exactly as recorded (2 of them
grown in size as their own notes foresaw); 1 row (config stub)
is absent under its claimed name with a proven fork successor.**

## §2 — Images at root, moved to `assets/` in P5

All eleven named images are **PRESENT at the moved location**:
the eight UUID `.jpg`s, `IMG_0665.jpeg`, `IMG_0666.jpeg`, and
`MIT_license_Rune_Forge_AI.jpeg` all sit in `assets/` (11 images
+ its README, matching E-002). Verdict: MOVED, as recorded, and
the §5b reconciliation holds — the four images a 2026-05-17 merge
brought back to root are **not** at root today.

But the root image population has **GROWN-BEYOND** the register
again, with different files: 19 `IMG_0861–0879.jpeg` camera files
and three large PNGs (`9834u4ernk4.png`, `ekkam8ekkam8ekka.png`,
`s7dkpys7dkpys7dk.png`) sit at root now. Sha256 comparison proves
**none of the 22 duplicates any `assets/` file** — this is new,
unregistered material, not a recurrence of the §5b copies. Byte
comparison against member-directory images is E-014's question.

## §3 — Top-level directories created during bootstrap

| Claimed directory | Verdict | Evidence |
|---|---|---|
| `docs/` with 11 named subfolders | GROWN-BEYOND | All 11 claimed subfolders present; the tree now carries 34 subfolders (the Mythic-Plan dirs, the codex working dirs, `audit/` — this campaign's own home — and more) |
| `config/` | PRESENT | Templates/examples only, as claimed; plus `profiles/` |
| `src/runa/` (subpackages cli/runtime/core/services/apps/adapters/plugins/skills/schemas/migrations) | MOVED / replaced | **Absent.** The fork-delta (`045fda6`) archived the Runa skeleton to `docs/archive/runa-inherited/src-skeleton/` (present) and built `src/ember/` in its place — recorded by the register itself in §7.4. Of the claimed subpackage names only `cli/` and `schemas/` survive inside `src/ember/`; the live tree is cli / config / mcp / schemas / spark / thread / tools / well |
| `tests/` (unit/integration/e2e/fixtures/snapshots) | PRESENT | Exactly the five claimed subfolders |
| `scripts/`, `tools/`, `examples/` | PRESENT as shells | Subfolders as claimed, contents still Markdown-only (E-002 finding 5) |
| `deploy/` (systemd/docker/pi/examples) | PRESENT | All four subfolders; documents only (E-002). The `docker/` subfolder's contents stand under the campaign's no-Docker law — E-181's audit |
| `vendor/` "currently empty" | PRESENT, with a standing mismatch | Still holds only its README — while the one vendored member, CloakBrowser, sits at top level, unregistered (§5). The register's §3 shape and the tree's vendored reality have never matched |
| `assets/` | PRESENT | 12 files, as §2 above |

## §4 — Files created during bootstrap

- `TASK_runa_bootstrap.md`: **MOVED** — absent from root, present
  at `docs/archive/runa-inherited/TASK_runa_bootstrap.md`, with
  its sibling Runa task files. The register left its fate open
  ("Volmarr decides"); the fork archived it.
- Per-directory `README.md`s: present throughout (contents not
  audited here; never touched — campaign law).
- The planned drift detector, `tools/repo/check_origins_drift.py`
  (§5b lesson, §6): **ABSENT — never built.** `tools/repo/` holds
  only its README. Had it existed, §2's new root images and §5's
  unregistered members are exactly what it was meant to flag.
  Docketed for E-016.

## §5 — What the register does not cover (GROWN-BEYOND as a class)

Unregistered top-level material, all present in-tree, none with
an ORIGINS row:

1. **The eleven imported member directories** (headline, above):
   Verdandi, kista, mempalace, mimir-well, seidr_engine,
   astrology-engine, bifrost, Hamr, Open-VTT, CloakBrowser,
   cleasby-vigfusson-old-norse-dict. E-002 proved each arrived in
   a single 2026-05-21 import commit; the register, updated the
   same day for slice-2, never gained their rows.
2. **Root loose files** (beyond §2's images): the five elder
   codices (`TASK_CHATDOLL_CODEX.md`, `TASK_HERMES_CODEX.md`,
   `TASK_RAGNAROK_CODEX.md`, `TASK_SUPER_AGENT_PARTY_CODEX.md`,
   `TASK_WAIFU_CODEX.md` — their census is E-008), plus
   `HEATHEN_THIRD_PATH_AI_CANON_AND_RITUAL_MANUAL.md`,
   `HEATHEN_THIRD_PATH_CANONICAL_SYNTHESIS.md`,
   `THE_CYBER-VIKING_UX_CODEX.md` (25 bytes),
   `The_Volmarr_Codex.md`,
   `Volmarr_Cyber_Viking_Master_Visual_Design_Lawbook.md` +
   `.pdf` (~13 MB together), `Yggdrasil_and_Huginn_and_Muninn_Theory.md`,
   `pyproject.toml` (the ember-agent package definition itself),
   `.env.example`, `.gitignore`, `.python-version`.
   (`CAMPAIGN_STATE.md` is this campaign's own file, 2026-10-30 —
   registered here, in this doc, as it is created.)

## §7 — Ember-descent material (added 2026-05-19 onward)

| Register claim | Verdict | Evidence |
|---|---|---|
| §7.1 `docs/SYSTEM_VISION.md` live; Six True Names in `docs/architecture/EMBER_TRUE_NAMES.md` | PRESENT | 17,252 and 14,493 bytes |
| §7.2 Twelve slice-1/2 architecture + adapter docs, live or archived-in-place as marked | PRESENT | All twelve present at their stated paths (ARCHITECTURE, DOMAIN_MAP, DATA_FLOW, EMBER_TRUE_NAMES, EMBER_FORK_DELTA, EMBER_FIRST_SLICE_PLAN, EMBER_SECOND_SLICE_PLAN, EMBER_SECOND_SLICE_OPTIONS, BRUNNR_BACKEND_MATRIX, FUNI_LOCAL_MODEL_OPTIONS, SMIDJA_INGEST_PATTERNS, GUNGNIR_WELL_REFERENCE) |
| §7.3 Seven ADRs (0006–0011, 0013) | PRESENT, and GROWN-BEYOND | All seven present in `docs/decisions/`. The sequence around them has grown past the register: ADR `0014-mcp-bidirectional.md` exists unlisted, and **0012 is absent from the sequence** — no file, and §7.3 offers no note. Whether 0012 was skipped, retired, or never written is an open question for E-016 (register silence, not a tree defect proven here). ADRs 0001–0005 (bootstrap era) also stand in the folder, outside §7's scope by its own framing |
| §7.4 Eleven source subtrees under `src/ember/` | PRESENT, and GROWN-BEYOND | All eleven present (cli, config, schemas, spark/funi incl. ollama + tools, spark/hjarta, spark/munnr, thread/strengr, well/brunnr/sqlite_vec, well/brunnr/pgvector, well/smidja, tools). A twelfth subtree, `src/ember/mcp/`, stands unlisted — the code twin of the unlisted ADR 0014 |
| §7.5 Five operator-facing docs | PRESENT | `deploy/pi/INSTALL.md`, `docs/adapters/PGVECTOR_BRUNNR_REFERENCE.md`, `config/ember.example.yaml`, `config/storage.example.yaml`, ADR 0013 — all present. `config/sources.example.yaml` stands beside them unlisted (minor) |

## §5 (register) — Open uncertainties, re-checked

1. Kebab vs snake Runa design drafts: register-resolved (different
   documents by different models, never to be merged) — **both
   files verified present** at `docs/architecture/`, sizes
   46,502 vs 63,985 bytes, consistent with distinct documents.
2. Rune Forge AI licence image: register-resolved — image
   verified present in `assets/`.
3. README update bursts: history preserved in git log, as the
   register says; nothing further claimed.
4. `IMG_0665/0666` source: **still open** — files present in
   `assets/`, provenance still unrecorded. Carried to E-016.
5. Descriptive renames for UUID images: **still not done** — the
   `assets/` images keep their UUID names. Carried to E-016 as
   a standing register note, not a defect.

## Concordance tally

- §1 root files: 25 rows — 22 PRESENT as recorded, 2
  GROWN-BEYOND in size (foreseen by their own notes), 1 ABSENT
  under its claimed name with a proven successor.
- §2 images: 11 of 11 MOVED as recorded; a new, non-duplicate
  root image population (22 files) stands GROWN-BEYOND.
- §3 bootstrap directories: 10 — PRESENT (config, tests, deploy,
  assets), PRESENT-as-shells (scripts, tools, examples), PRESENT
  with a standing mismatch (vendor), GROWN-BEYOND (docs), and
  MOVED/replaced by the fork (src/runa → src/ember, self-recorded
  in §7.4).
- §4 bootstrap files: anchor MOVED to the archive; the promised
  drift detector ABSENT (never built).
- §7 Ember-descent: every listed item PRESENT (12 docs, 7 ADRs,
  11 subtrees, 5 operator docs, §7.1 pair); three GROWN-BEYOND
  additions stand unlisted (ADR 0014, `src/ember/mcp/`,
  `config/sources.example.yaml`) and one numbering gap (0012)
  is unexplained.
- **The register's blind spot, as a class: the eleven imported
  members + the elder codices and other root loose files have
  no ORIGINS rows.** That is the single largest concordance
  finding of Part I so far, and it is a register gap, not a tree
  defect — the members are present, licensed in-tree (E-002
  finding 7), and provenanced by the roadmap. E-196 extends the
  register; E-016 dockets the gap and the small items above
  (drift detector, IMG provenance, THIRD_PARTY staleness, the
  0012 question).

*Filed by the E-003 slice, 2026-10-30. Next: E-004 — Fresh
baseline I.*

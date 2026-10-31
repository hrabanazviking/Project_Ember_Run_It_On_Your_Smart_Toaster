# E-016 — The Bug & Gap Docket

*Project Ember campaign, Part I (The Monorepo's True State).
Filed 2026-10-31 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), at campaign
commit 1877cf7 (E-015 banked + its push record). This docket
fixes nothing: Part I prepares and assigns; the fixes land in
the owning parts named here, slice by slice, under the
campaign law that nothing found is left unfixed — in Part I
that law is discharged by this docket itself (CAMPAIGN_STATE
law: "in scope, or docketed to its part in E-016").
Removals and retirements named here are prepared for
Volmarr's word, never executed by the docket.*

## Method — how completeness is proven, not asserted

- Every `## Carried to the E-016 docket` section in the
  Part I audit docs (E-004–E-015) was extracted verbatim and
  reconciled against the CAMPAIGN_STATE ledger, slice by
  slice. The numbered sequence those slices assigned is
  **continuous 1–71, with no gap and no duplicate**:

  | Source slice | Items | Source slice | Items |
  |---|---|---|---|
  | E-004 (baseline I) | 1–4 | E-010 (Hamr plan) | 38–45 |
  | E-005 (baseline II) | 5–12 | E-011 (two Kistas) | 46–50 |
  | E-006 (boot census) | 13–17 | E-012 (two memories) | 51–54 |
  | E-007 (deps/licences) | 18–25 | E-013 (config/secrets) | 55–58 |
  | E-008 (codex census) | 26–30 | E-014 (dead/duplicate) | 59–64 |
  | E-009 (Verdandi) | 31–37 | E-015 (budgets) | 65–71 |

- Items 1–71 are **never renumbered**: every cross-reference
  in E-004–E-015 and in CAMPAIGN_STATE.md keeps its meaning.
- E-002 and E-003 predate the numbering (it began at E-004).
  The findings those two slices explicitly carried forward —
  plus the two open measurements E-005/E-006 recorded
  without a number (no-suite members; the unrun dictionary
  suite) and the vendored-suite record — receive their
  first numbers here, **72–80**, each sourced below. Nothing
  carried forward by any Part I slice is left unnumbered.
- One entry is not a distinct defect: **53 is a
  re-observation of 10** (E-012 re-proved it, unchanged).
  The docket therefore holds **80 entries covering 79
  distinct issues** — stated plainly so no count inflates.
- Classes used: **REAL** (defect in code or tests),
  **REAL/env** (REAL, triggered only when an optional extra
  or machine shape is absent), **STALE** (text/tests judging
  a tree or state that no longer exists), **GAP** (something
  promised or needed is absent), **NOT PROVEN / OPEN**
  (evidence does not exist yet; an open measurement),
  **CONSTRAINT / BOUNDARY / DISCIPLINE** (not a defect — a
  rule the owning part must respect), **VOLMARR** (the
  decision itself is his word).

## Headline — read this first, in plain words

**Part I found 79 distinct things wrong, missing, stale,
or undecided — and every one of them now has a number, a
class, and an owner.** None is a hidden catastrophe: the
root suite is green with its extras supplied (E-004), the
one fully green member (seidr_engine) needed no entry at
all, and no real credential was ever found in a plain file
(E-013). What the docket actually shows is a monorepo whose
*members* were imported once and never re-proven: one
genuinely broken code path a user would hit (Vör, item 31,
which also breaks Verdandi's pulse cycle), one program
that reports success while computing nothing (astrology,
16), first-run diagnostics that crash on a bare machine
(13), a credential store whose default home is another
program's vault (46), and then a long tail of
machine-coupled tests, undeclared dependencies, stale
elder documents, unmeasured budget claims, and register
gaps. Three entries need Volmarr's word before anyone can
act (26, 48, and the removal halves of 60/62/63/64); two
stand NOT PROVEN until hardware or artefacts exist
(40, 44). Everything else is ordinary build work, already
sliced into the parts below.

## The docket — master table

| # | Issue (short title) | Source | Class | Owner |
|---|---|---|---|---|
| 1 | pgvector real-backend test: `import psycopg` sits above its own importorskip guards — whole root suite cannot collect bare | E-004 | REAL/env | Part II |
| 2 | sqlite_vec adapter imports its optional extra at top level, coupling pure helpers (and, via its sanitiser, the pgvector adapter) to the extra | E-004 | REAL | Part II |
| 3 | Unguarded sqlite_vec-dependent root tests fail instead of skipping (Batch CDE ×3, Batch J ×1) | E-004 | REAL/env | Part II |
| 4 | MCP runner test leaks an un-awaited coroutine (1 warning, both full runs) | E-004 | REAL, minor | Part II |
| 5 | kista tests hardcode the `~/.hermes` credstore path and never touch the in-tree script | E-005 | REAL test | Part VI |
| 6 | bifrost tests import optional `muninn` unguarded and fail instead of skipping; bifrost pytest config lacks `pythonpath` (cannot collect uninstalled) | E-005 | REAL test | Part VIII |
| 7 | Verdandi `vor_action.py:69` AttributeError breaks the pulse cycle — *expanded and superseded in scope by 31; kept for E-005's references* | E-005 | REAL code | Part IV |
| 8 | Verdandi CLI integration tests hardcode `~/Verdandi` as subprocess cwd | E-005 | REAL test | Part IV |
| 9 | Verdandi YAML profile loader raises `IsADirectoryError` on a missing path instead of returning defaults | E-005 | REAL code | Part IV |
| 10 | mimir-well Eye fixture sets `DB_PATH` while the app binds `MIMIR_DB_PATH` at import over `~/.hermes` defaults — 6 Eye tests fail anywhere but the author's machine | E-005 | REAL | Part V |
| 11 | Hamr tests hardcode `/home/pi/Hamr` (×3) and the `python` binary name (×4); Hamr pytest config lacks `pythonpath`; release-promotion tests judge the standalone repo's `.github` layout (STALE ×3) | E-005 | REAL + STALE | Part IX |
| 12 | mempalace tests judge a `.claude-plugin/` directory absent from the tree (STALE ×10), plus a small UNRESOLVED residue (palace lock timeout, MCP diary/write asserts) recorded as unresolved, not guessed | E-005 | STALE + UNRESOLVED | Part V |
| 13 | ember `doctor` / `well status` crash in the stdlib-only env — the boot face of item 2 compounded by the default Well backend requiring an optional extra; first-run diagnostics must start bare | E-006 | REAL | Part II |
| 14 | kista credstore attempts an import-time `pip install cryptography` and dies with `CalledProcessError` (PEP 668) where the dep is absent, instead of a plain message | E-006 | REAL code | Part VI |
| 15 | Hjarta first-run wizard raises an `EOFError` traceback when stdin closes mid-setup (the `ask`/`chat` fresh-root path) | E-006 | REAL code | Part II |
| 16 | astrology-engine's real commands exit 0 printing "pyswisseph required" while computing nothing — silent success; its compute deps are declared nowhere (declaration half is 18) | E-006 | REAL honesty | Part VII |
| 17 | mimir-well `start-eye.sh` hardcodes `/home/pi` paths (launcher edition of the machine-coupling family); the `python -m mimir_well.eye` path works | E-006 | REAL | Part V |
| 18 | astrology-engine has no packaging file and declares none of its 5 guarded imports (pyswisseph, kerykeion, geopy, timezonefinder, pytz) — install-invisible | E-007 | GAP | Part VII |
| 19 | Verdandi `eir/layers.py` imports yaml top-level unguarded with pyyaml declared nowhere in the member (tests likewise); `heartbeat/cli.py`'s yaml fallback catches NameError where ImportError is the real failure | E-007 | REAL | Part IV |
| 20 | The core's optional `keyring` secret source (ADR 0010) is declared in no extra — lazy and graceful in code, undiscoverable from packaging | E-007 | GAP | Part II |
| 21 | Hamr imports undeclared lazy `psutil` in two core modules (guarded, /proc fallback) and undeclared `tomli` in a packaging test's <3.11 fallback | E-007 | GAP | Part IX |
| 22 | Licence-metadata gaps: kista pyproject, dictionary package.json, mempalace-website package.json declare no license field despite MIT LICENSE files standing beside two of them | E-007 | GAP | Part XI |
| 23 | No Python lockfile outside mempalace; near-universal unbounded `>=` ranges — fresh installs unreproducible by construction | E-007 | GAP | Part III (E-044) |
| 24 | Root licence estate stale for release: `THIRD_PARTY_NOTICES.md` still names "Runa Agent"/"HERETIC" and holds zero entries despite promising every dependency; root `NOTICE` likewise names Runa Agent and its old repo | E-007 | STALE | Part XI (E-185) |
| 25 | CloakBrowser's compiled binary is proprietary (CloakHQ BINARY-LICENSE): use and dependency-listing are free; redistribution/bundling into a distributed product is prohibited without an OEM/SaaS licence — a release-shape constraint, not a present violation (binary absent, never downloaded) | E-007 | CONSTRAINT | Part XI |
| 26 | Ragnarok codex never authored: scaffold only (3 of 6 meta), 0 of 46 content docs, no INDEX — authoring or retiring it is Volmarr's word; E-165 reconciles | E-008 | GAP / VOLMARR | Part X (E-165) |
| 27 | All five TASK_*_CODEX status lines are stale ("Authoring / pending dispatch" over four completed corpora and one scaffold) — elder text, not edited; E-008 is the correction of record | E-008 | STALE | Part X (E-169) |
| 28 | Codex counting ambiguity: TASKs promise content counts, siblings cite totals, two citations match neither (SAP "84" vs 77/83; Waifu "22" vs 15/21); Hermes's "53+" mixes content and meta against its actual 50/58 | E-008 | STALE | Part X (E-169) |
| 29 | SAP's MANIFEST undercounts its own corpus by one (claims 82; tree holds 83) — the manifest is the stale party | E-008 | STALE | Part X (E-169) |
| 30 | No codex corpus is referenced anywhere in `src/` — the four completed corpora's proposals have no in-code consumer | E-008 | GAP | Part X (E-161–168) |
| 31 | Vör pre-emptive action broken in three places: (a) `should_trigger` and `_get_capacity_summary` call `.get()` on Skuld's string-shaped `capacity` values (both reproduced); (b) its returns use `ActionResult(name=…, ActionSeverity.INFO)` — wrong field (`action_name`) and a nonexistent severity, on both return paths; (c) it overrides `execute()` instead of `_execute()`, bypassing BaseAction's crash wrapper so its crashes propagate into the pulse cycle (E-005's 7 integration failures). No test covers Vör | E-009 | REAL code | Part IV |
| 32 | VD-RM's v0.4.0 distributed heartbeat and REST API are ABSENT (no code; the API exists only as a docs wrapper pattern with different paths) — Part IV must decide build-or-retire; nothing downstream may assume they exist | E-009 | GAP | Part IV (E-060) |
| 33 | Emotional architecture's state count matches nothing: VD-RM claims 7, its table lists 6, `EMOTIONAL_STATES` holds 6, `classify()` can return 8 | E-009 | GAP | Part IV |
| 34 | `pulse_metrics` is WRITE-ONLY: created, indexed, inserted every pulse, pruned at 10,000 — never SELECTed anywhere; Skuld predicts from `pulse_history` state-derived scores instead | E-009 | GAP | Part IV |
| 35 | Shipped features described as planned/future in at least five sibling docs; VD-RM itself lists Prometheus and the emotional architecture as v0.4 plans after claiming them shipped in v0.3 | E-009 | STALE | Part IV (E-060/E-074) |
| 36 | VD-RM covers the heartbeat only: nerve hub, context injector, conversation logger, top-level reactor, the Eir package (own version 2.0.0), `runa_*` systems, and the 50-doc research corpus have no roadmap coverage | E-009 | GAP | Part IV (E-059/E-060) |
| 37 | VD-RM's sketches diverge from the shipped API in names, thresholds, and wiring (check `prediction` not `predictive:…`; slope −0.05 not −0.5; hard-coded Reactor rule, not the sketched YAML; static maintenance windows, not Urðr-integrated) — code is the authority; E-060's re-cut must be written from code | E-009 | STALE | Part IV (E-060) |
| 38 | Hamr Phases 1–10 have no phase documents: Phases 1–5 survive only as CHANGELOG lines, **Phase 6 has no claim anywhere in the tree**, Phases 7–10 rest on test files plus three "Phase 7: Complete" docstrings — any history written for 1–10 is reconstruction, labelled as such | E-010 | GAP | Part IX (E-138) |
| 39 | Hamr Phase 14 has no COMPLETE artefact: its plan's 7 tasks stand unchecked, the CHANGELOG details only T6, and Phase 15 assumes its completion | E-010 | GAP | Part IX (E-140) |
| 40 | Hamr Phase 17 is a vision, not a completion: its must-pass criteria (a real `.vrm`, 22 stages, clean Blender exit, on Pi 5) are unevidenced — no `.vrm` file exists in the tree and no Blender host is available to this campaign today; the first full raising stands NOT PROVEN | E-010 | NOT PROVEN | Part IX (E-140/E-143) |
| 41 | Hamr named-module claims fail as written: `materials/forge.py`/`MaterialForge`, `rigs/colliders.py`/`CollisionForge`, `rigs/pose_library.py`/`PoseLibrary`, `tests/test_e2e_pipeline.py` do not exist (real equivalents at `materials/anime.py`, `rigs/collision.py`, `rigs/poses.py`, `face/expressions.py`, the e2e trio) — Part IX grades the claims as written and names the equivalents | E-010 | STALE claims | Part IX (E-150) |
| 42 | Hamr Phase 15 promotion check "ci_configured — `.github/workflows/ci.yml` present" is false in this tree (no `.github` under Hamr/ at all; kin to item 11's STALE half) — it could only have passed in the standalone repo | E-010 | STALE | Part IX |
| 43 | Hamr test-count spine contradicts itself (Phase 15: ~1965 in its COMPLETE doc vs ~2206 in its CHANGELOG section; Phases 12/13 titled COMPLETE while admitting 4 and 7 failures) and against E-005's measured baseline — all Part IX counts come from the runner only | E-010 | STALE | Part IX |
| 44 | A family of Hamr claims is unprovable from this tree — Pi 5 timings/environment, VRChat validation, TestPyPI publication, GitHub release/tag/CI execution — each needs the external artefact named in E-010; absent that artefact, Part IX grades NOT PROVEN | E-010 | NOT PROVEN | Part IX |
| 45 | AUDIT_17's `remaining_conflicts.py` residue (stale reverse bone maps, mixed bone-name regions across five files) is noted-not-fixed by its own author and assigned to a Phase 18 that does not exist in this tree — it seeds E-142's re-roaded remainder | E-010 | REAL residue | Part IX (E-142) |
| 46 | Toaster-Kista's default vault directory is the other Kista's home: `KISTA_DIR` unset → `~/.hermes/credentials`, same filenames as the Hermes deployment — the dangerous conflation, in code; a toaster-profile default is undecided and unbuilt | E-011 | REAL code | Part VI (E-093/E-094) |
| 47 | Verdandi's Mímir check expects a Kista vault at `~/.kista/vault.db` (SQLite `entries`) that neither Kista writes — against a real credstore vault it reports not-found/error; one of the check, the config reference, or the shape is wrong | E-011 | REAL | Part IV (VI consulted) |
| 48 | `kista/references/known-accounts.md` is the ai-folder vault's operational status ledger (status only, no credential values — re-verified E-013) sitting inside the toaster tree; whether it belongs in this repo is Volmarr's word — recorded, not removed | E-011 | CUSTODY / VOLMARR | Volmarr's word |
| 49 | The toaster tree's Kista docs describe the Hermes deployment as the program's home (`SKILL.md`: skill name `runa-credentials`, Hermes metadata, standalone-repo homepage; "8 entry types" stale against the code's 14 and its own table) | E-011 | STALE | Part VI (E-104) |
| 50 | Three Hermes-shaped commands ship in the toaster copy — `add-soul`, `add-cron-backup`, `github-backup` — features of a live agent's vault in the tiny-machine program; whether they belong in the toaster set is undecided | E-011 | GAP decision | Part VI (E-098) |
| 51 | "The Mímir DB" has three default paths (library `~/.mimir_well/mimir_well.db`; Eye and bifrost bridge `~/.hermes/memory/runa_memory.db`) — stores at different defaults are mutually invisible; one canonical default, or an explicit documented divergence, is undecided and unbuilt | E-012 | GAP | Part V (E-077/E-080) |
| 52 | `docs/UNWIRED_INVENTORY.md`'s mempalace line ("likely abandoned or archival") is proven stale (v3.3.5, 1,712 passing at E-012); the wired=no fact stands, the characterisation must be corrected where the inventory is next truthfully updated — never silently | E-012 | STALE | E-018 / E-091 |
| 53 | **Re-observation of item 10, not a distinct defect:** E-012's clean mimir-well run reproduced E-005 exactly (350 passed, same 6 Eye failures) — machine-coupling stands; no code had changed | E-012 | RE-OBSERVATION | Part V (as 10) |
| 54 | mempalace suite counts are environment-volatile at scale (E-005: 1597/90/39 vs E-012: 1712/14/0; the bulk of E-005's failures shown environment-shaped, 512 MB `/tmp` pressure the proven mechanism) — E-077's harness must pin TMPDIR, disk headroom, and runner version or its numbers will move the same way | E-012 | GAP discipline | Part V (E-077) |
| 55 | Root `.env.example` is a pre-fork Runa fossil: a dozen provider/bridge secrets directed to `~/.runa/secrets/runa.env`, **zero** of its keys consumed in `src/ember` (the core's true env surface is `OLLAMA_HOST` + `EMBER_WELL_PASSWORD`); it misdescribes the product and misplaces secrets | E-013 | STALE | Part II (E-033) |
| 56 | Config fragmentation: at least seven distinct config shapes across members; no member can be configured by a method learned from another (item 51 is its sharpest single instance) | E-013 | GAP | Part II (E-033/E-037) |
| 57 | Credential-shaped test fixtures are proven synthetic but scanner-indistinguishable from leaks — any future secret-scanning gate (E-187) false-alarms on exactly these files unless fixtures stay obviously synthetic and the gate carries a classified allowlist; no fixture is to be "cleaned up" silently (the credstore tests need key-shaped data) | E-013 | DISCIPLINE | Part XII (E-187) / XI |
| 58 | CloakBrowser embeds proxy credentials in URL strings throughout its vendored docs, API, and tests — vendored, never rewritten; the boundary rule is Ember's own code must never adopt URL-embedded credentials (its proven shape is the E-013 §2 resolver; any proxy Ember configures takes credentials from custody, E-093) | E-013 | BOUNDARY | Part XI (E-178) |
| 59 | Verdandi heartbeat carries 2,548 lines of provably unwired Runa-era code (`runa_mood_arousal` 1,105, `runa_reward` 613, `runa_negative` 609, `push_reward` 221 — no import, reference, or dynamic load; the hub boots without them) — wire deliberately under the event contract, or verdict-prepare | E-014 | GAP | Part IV (E-059/E-060) |
| 60 | Four Verdandi files named as PNGs are 1-byte newline placeholders, invalid as images, unreferenced pre-campaign — the pictures they place-held do not exist in this tree; if they exist outside it, only Volmarr knows where | E-014 | GAP | E-018 (verdict prep) |
| 61 | Tracked generated artefacts: Open-VTT's three Godot `.tmp` editor files (65,417 B, two byte-identical) and Hamr's `build_output/` (5 files, 10,185 B, incl. the directory standing in for a `.vrm`) — build output and editor scratch are not source | E-014 | HYGIENE | Part X (E-158) / IX |
| 62 | Cross-member exact duplication of house material (IMG_0665/0666 ×3 each, licence image ×2, two Hamr/astrology image pairs, `Volmarr_writings_philosophy.md` ×3, `WORLD_MODELING_SKILL.md` ×2 — 2,886,896 wasted bytes in this item alone); no copy is marked canonical, so copies can silently diverge (the texts are the sharp risk). The mempalace logo's three homes are excluded — intentional distribution | E-014 | HYGIENE | E-018 (verdict prep) / E-057 |
| 63 | `THE_CYBER-VIKING_UX_CODEX.md` at root is a 25-byte title-only stub while the Design Lawbook it names stands complete elsewhere at root — dead documentation; its fate (write it, point it at the Lawbook, or retire it) is decided with the whole docs estate in view | E-014 | STALE | E-018 / E-193–195 |
| 64 | Bootstrap scaffolding shells never filled: `scripts/`, `tools/`, `examples/` hold 13 Markdown-only files (12,921 B) describing contents that never arrived — fill, fold into docs, or retire, per directory; the shells' fate and item 73's home should be decided together | E-014 | GAP | E-018 (verdict prep) |
| 65 | Verdandi's documents state six different RAM figures for overlapping scope (hub ~1 MB; heartbeat ~13 MB, 15 MB idle, ~15–25 MB Pi guide, <50 MB research target, ~30 MB proposal) with no document distinguishing hub from heartbeat; storage figures likewise mix ~5 MB total with ~22 MB/year feed growth | E-015 | STALE | Part III (E-041) + IV (E-060) |
| 66 | The Yggdrasil Tiny Device Profile is internally inconsistent and self-admittedly over budget: RAM sums to ~622 MB on a 512 MB target (annotated "over budget!" in the doc itself), fallback cap 350 MB, tiered-defaults cap 400 MB for the same TINY class — three numbers, none measured, for the roadmap's most important profile; its exclusion rules are likewise unmeasured | E-015 | GAP | Part III (E-041/E-049) |
| 67 | The core's front-door budget claims have never been measured (~50 MB disk ex-models, ~50 MB RAM, default Well 50 MB resident) and their scope is the installed core alone — never to be read as the 217 MB monorepo's cost | E-015 | GAP | Part III (E-041/E-045) |
| 68 | Hamr carries two incompatible memory budgets: perf.py's enforced 1.5 GB Pi 5 ceiling (tiers to 512 MB) vs Phase 17's peak <7.5 GB bound and 143 MB VRM bound — verification must state which budget governs which build shape | E-015 | CONTRADICTION | Part IX (E-140/E-142) |
| 69 | The Yggdrasil sibling matrix's per-member runtime estimates (bifrost ~50 MB, mimir-well ~30 MB, Verdandi ~30 MB, Seiðr ~20 MB, Kista ~10 MB, Hamr ~200 MB, CloakBrowser ~300 MB, astrology ~50 MB, dictionary ~50 MB disk) are round, unsourced, and in places at odds with E-002's measured trees — E-057's measured table replaces them as the citable source; the proposal doc itself is not edited | E-015 | UNSOURCED | Part III (E-057) |
| 70 | Five members state no size/RAM budget at all — mempalace, mimir-well, seidr_engine, bifrost, kista — so Part III has nothing to test for the majority of the monorepo's weight | E-015 | GAP | Part III (E-041/E-057) |
| 71 | Stofa TUI's performance-budget doc names CI tests that do not exist (`test_stofa_launch_budget.py`, `test_idle_memory_under_50mb` — verified absent from the tracked tree) for budgets over a TUI that is itself an unbuilt design tree | E-015 | GAP | E-018 / Part III (E-042) |
| 72 | ORIGINS' blind spot as a class: none of the eleven imported member directories has an ORIGINS row, and neither do the five elder codices or the other root loose files — a register gap, not a tree defect (the members are present and licensed in-tree); E-196 extends the register | E-003 | GAP | Part XII (E-196) |
| 73 | The register's planned drift detector, `tools/repo/check_origins_drift.py` (§5b/§6), was never built — `tools/repo/` holds only its README; had it existed, items 72/79 are exactly what it was meant to flag (decide its home together with item 64) | E-003 | GAP | Part XII (E-196) / E-018 |
| 74 | ADR sequence silence: ADR 0012 is absent with no register note (E-014 later explains it from UNWIRED §5.4 as a placeholder, never ratified — not a lost document; the register's silence remains), while ADR 0014, `src/ember/mcp/`, and `config/sources.example.yaml` stand grown-beyond, unlisted | E-003 | REGISTER | Part XII (E-196) |
| 75 | `IMG_0665/0666` provenance is still unrecorded, and the `assets/` images still keep their UUID names (descriptive renames never done) — carried by E-003 as a standing register note, not a defect | E-003 | OPEN note | Part XII (E-196) |
| 76 | Standing register-vs-tree shape mismatches: `vendor/` holds only its README while the one vendored member (CloakBrowser) sits at top level, and the §1 config stub `config/runa.example.yaml` is absent under its claimed name with a proven fork successor (`config/ember.example.yaml`) — both are register corrections for E-196, not tree defects | E-003 | REGISTER | Part XII (E-196) / XI (E-175) |
| 77 | Two members have NO test suite at all — astrology-engine (0 test files) and Open-VTT (0; its one `*_test.gd` is a debug component, and no Godot binary exists on the VM) — Parts VII and X inherit a build-the-fixtures-first position for both | E-002/E-005 | GAP | Part VII / Part X |
| 78 | The dictionary's Jest suite (67 test files) has never been run: `node_modules/` is absent and the full Next.js tree was not installed for an audit slice; the dictionary likewise cannot boot here (`next` not found) — an open measurement, not a defect, for the first part that works on the dictionary itself | E-005/E-006 | OPEN measurement | Part VII (E-115/E-116) |
| 79 | A new root image population (19 `IMG_0861–0879.jpeg` + 3 large PNGs, 22 files) stands unregistered in ORIGINS — sha256-proven NOT duplicates of any `assets/` file (E-003; the duplication E-014 found lives in the ORIGINS images, item 62) — new material whose provenance only the register can record | E-003/E-014 | GAP | Part XII (E-196) |
| 80 | Vendored-suite record (stewardship, never judged as ours): CloakBrowser's Python suite with deps supplied runs 385 passed / 39 failed / 15 errors, the residue environment-shaped (proxy-env signature, unprovisioned browser binary, DNS-dependent SSRF tests, one timing assertion, one un-root-caused group); its JS side was NOT RUN (`node_modules/` absent) — Part XI stewards; the campaign does not fix vendored code | E-005 | VENDORED / ENV | Part XI (E-175) |

## Assignment tally (primary owner; consulted owners in the table)

| Owner | Items | Count |
|---|---|---|
| Part II — Ember core | 1, 2, 3, 4, 13, 15, 20, 55, 56 | 9 |
| Part III — tiny hardware | 23, 65, 66, 67, 69, 70 | 6 |
| Part IV — Verdandi | 7, 8, 9, 19, 31, 32, 33, 34, 35, 36, 37, 47, 59 | 13 |
| Part V — memory | 10, 12, 17, 51, 53, 54 | 6 |
| Part VI — toaster Kista | 5, 14, 46, 49, 50 | 5 |
| Part VII — inner life | 16, 18, 77, 78 | 4 |
| Part VIII — Bifrost | 6 | 1 |
| Part IX — Hamr | 11, 21, 38, 39, 40, 41, 42, 43, 44, 45, 68 | 11 |
| Part X — table & codices | 26, 27, 28, 29, 30, 61 | 6 |
| Part XI — stewardship | 22, 24, 25, 58, 80 (+57 co-owned with XII) | 5 |
| Part XII — hardening/release/register | 57, 72, 73, 74, 75, 76, 79 | 7 |
| E-018 gate (Part I verdict prep) | 52, 60, 62, 63, 64, 71 | 6 |
| Volmarr's word (primary) | 48 | 1 |
| **Total** | | **80** |

(Item 61 is counted under Part X for its Open-VTT half;
its Hamr half belongs to Part IX. Item 57 is counted under
Part XII, where E-187 lives; Part XI stewardship is its
co-owner. With those two conventions the tally sums to the
80 entries exactly.)

## Cross-links the owners must not miss

- **31 expands 7** (same Vör defect, fully mapped); **13 is
  the boot face of 2**; **16 and 18 are two halves** of the
  astrology failure (silent success + undeclared deps);
  **53 re-proves 10**; **42 is kin to 11**'s STALE half (both
  judge the standalone Hamr repo's layout); **51 is the
  sharpest instance of 56**; **64 and 73 are decided
  together** (shells' fate + the drift detector's home);
  **65 is priced twice** (Part III measures, Part IV makes
  the documents name which program each number prices);
  **68 is recorded in E-041's book** whichever way Part IX
  settles it; **24 and 72/76 meet at E-196/E-185** (the
  release's licence table cannot be built from the stale
  root estate, and the register it extends is the same one
  missing the member rows).
- **The machine-coupling family** — one disease, five
  entries: 5 (kista), 8 (Verdandi), 10/53 + 17 (mimir-well),
  11 (Hamr). Suites that were green only on the machine
  that wrote them. Any part fixing one should check its fix
  pattern against the others.
- **Volmarr's word is required for:** 26 (author or retire
  Ragnarok), 48 (known-accounts custody), and every removal
  inside 60, 62, 63, 64 (verdicts are prepared at E-018;
  nothing is removed by this campaign without his word).
  Retirement-shaped decisions inside 32 (build-or-retire)
  and 59 (wire-or-verdict-prepare) likewise end at a
  prepared verdict, not a silent act.
- **NOT PROVEN, honestly:** 40 (Phase 17's first raising),
  44 (the external-artefact family), 78 (dictionary suite),
  and the unresolved residue inside 12 — none of these is
  a failure of effort; each names the artefact, device, or
  root-cause work that would settle it.

## What this docket proves for E-017 / E-018

- Part I's findings are closed as a set: E-001–E-015's
  every carried item is numbered above (1–71 preserved,
  72–80 first-numbered here), classified, and assigned.
  A defect discovered in a later part that is not in this
  table is a *new* docket item (81+) in that part's own
  record — this table is Part I's zero line, as E-017 is
  the suite's.
- E-018's verdict-preparation load is exactly: 52, 60, 62,
  63, 64, 71 (its own table above), plus the register-gap
  class (72–76, 79) whose execution is E-196's, and the
  per-member verdicts this docket's owners feed it.

## Slice gate

Root suite re-run in the E-001 shape (pgvector file
excluded, default env; `TMPDIR` redirected to the
workspace overlay as in E-013–E-015): **546 passed,
6 failed, 12 skipped, 1 warning** — identical to the
opening baseline; the 6 failures are the proven
environment failures (docket items 2/3's own subject).
Doc-only slice: no code touched, no README touched.
Push: under Volmarr's 2026-10-31 standing go-ahead, this
slice's commit is pushed to origin `yrsa/ember-road-build`
after fetch + ancestry check and verified by `ls-remote`
(recorded in the state file).

*Filed by the E-016 slice, 2026-10-31. Next: E-017 —
baseline freeze.*

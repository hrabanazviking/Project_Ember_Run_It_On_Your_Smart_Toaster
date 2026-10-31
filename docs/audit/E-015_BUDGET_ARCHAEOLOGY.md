# E-015 — Budget Archaeology

*Project Ember campaign, Part I (The Monorepo's True State).
Measured 2026-10-31 on branch `yrsa/ember-road-build` in the
campaign's own clone (`~/workspace/ember-build`), at campaign
commit 0425fbb (E-014 banked + its push record). Method: every
tracked `.md` / `.py` / `.toml` file scanned for numeric
size-unit lines (`<number> KB|MB|GB|MiB|GiB`) — **1,264 lines**
in total — and member trees scanned separately for the words
RAM / RSS / footprint / lightweight with word boundaries
(123 lines). Each hit was then hand-classified: a *product
claim* (a shipped member's own docs or code, stating what the
member costs), a *code-enforced limit* (a constant the code
actually applies), a *vendored claim* (CloakBrowser's own
words about itself), a *proposal* (the `docs/` corpora —
Yggdrasil, the codices, research, the TUI tree — designing
budgets for a future Ember), or *not a claim* (hardware
descriptions, test fixtures, file-size inventories of other
files). Raw inventories live in
`~/workspace/.verify-tmp/ember-e015/` (`size_units.txt`,
`ram_word.txt`). **Nothing was removed, changed, or struck
by this slice** — striking is Part III's act, on this
evidence; removals remain Volmarr's word.*

## Headline — read this first, in plain words

**Ember has exactly one member with an enforced budget
(Hamr), one member whose own documents give six different
RAM numbers (Verdandi), one set of public claims at the
front door that have never been measured (the core's
~50 MB), and five members with no budget claim at all.**
Everything else that sounds like a budget — and there is a
lot of it, 995 of the 1,264 numeric lines live under
`docs/` — is *proposal*, written for a future Ember that
does not yet exist in code. Part III therefore does not
inherit a budget book to verify; it inherits a short list
of real claims to test, a set of contradictions to settle,
and a blank page for most members, which it must fill by
measurement (E-041), not by quoting the proposals.

The real claims, in one breath:

- **The core (front door):** a typical install is ~3.5 GB
  on disk, of which "Ember itself + dependencies ~50 MB";
  "Ember itself uses ~50 MB" of RAM, minimum host 4 GB /
  recommended 8 GB; the default Well "runs on a Pi 5 with
  50 MB of resident memory." None of these has ever been
  measured by this campaign — E-002 measured the *source
  tree* (`src/ember` = 732 KB of code; the whole tracked
  monorepo = 217 MB), which neither proves nor refutes an
  *installed* figure. Scope is the trap: "~50 MB" is a
  claim about the installed core alone, and must never be
  read — or cited — as the monorepo's cost. (→ docket 67.)
- **Verdandi:** ~1 MB, ~13 MB, 15 MB, ~15–25 MB, <50 MB,
  and ~30 MB RAM are *all* stated, in different documents,
  for overlapping pieces of the same member. They are not
  all wrong — they measure different things (nerve hub vs
  heartbeat daemon) — but no document says so, so as
  written they contradict. (→ docket 65.)
- **Hamr:** the only enforced budget in the tree —
  `perf.py`'s `PerformanceBudget` (build ≤45 s, peak
  ≤1,500 MB, ≤50,000 triangles, textures ≤1024 px, on
  Pi 5) with memory tiers 512 MB / 1 GB / 1.5 GB. And
  even Hamr carries a second, incompatible budget:
  Phase 17 allows peak memory under **7.5 GB** and a VRM
  file under **143 MB**. (→ docket 68.)
- **No claim at all:** mimir-well, seidr_engine, bifrost,
  kista, and Open-VTT state no size or RAM ceiling for
  themselves (bifrost appears only in a proposal table;
  kista's only size text is a bug report noting a 10 MB
  field has *no* bound). Part III must set their budgets
  from measurement, because there is nothing to test.
  (→ docket 70.)

## 1. The front door — the core's public claims (TEST in Part III)

All from the root README and its Pi deploy twin
(`deploy/pi/INSTALL.md`, same text) — reading only; no
README was touched, per law:

| Claim | Source | Shape |
|---|---|---|
| Full install with optional bits + small local model ≈ **3.5 GB** disk | README "Why Ember?" + Requirements | Sum of parts below |
| Ollama ~700 MB; `phi3:mini` ~2.3 GB; `nomic-embed-text` ~274 MB; Ember itself + deps **~50 MB** | README Requirements; `deploy/pi/INSTALL.md` repeats the model figures | Model figures are Ollama's artefacts, checkable at pull time |
| **RAM: 4 GB minimum, 8 GB recommended; "Ember itself uses ~50 MB; the model eats the rest"** | README Requirements | The campaign's single most important unmeasured claim → E-041/E-045 |
| Default Well (sqlite_vec Brunnr) "runs on a Pi 5 with **50 MB of resident memory**", zero auxiliary processes, one file | README Storage; `src/ember/well/brunnr/sqlite_vec/README.md:18` ("The Vow of Smallness in storage form") | Testable as RSS of the core with the Well open → E-041 |
| Example Well on disk: 12 docs / 163 chunks = **5.4 MB** | README first-run example; `deploy/pi/INSTALL.md:132` | An example output, not a ceiling |
| Toaster baseline hardware: **8 GB Pi 5** + external SSD recommended | README Pi section; `deploy/pi/INSTALL.md:5` (8 GB recommended, 4 GB possible) | Hardware recommendation, not a cost claim |
| Smaller-model ladder for 4 GB Pis: `phi3:mini` needs ~2.5 GB resident; `qwen2.5:1.5b` ~1.3 GB resident | `deploy/pi/INSTALL.md:418-424` | Agrees with the FUNI ladder (§5) |

The model ladder itself lives in
`docs/adapters/FUNI_LOCAL_MODEL_OPTIONS.md` — host-RAM-keyed,
and internally consistent with the README: Pi 4 4 GB →
`qwen2.5:0.5b` ~600 MB resident; Pi 5 4 GB → 1.5B ~1.3 GB;
**Pi 5 8 GB (the default target) → `phi3:mini` ~2.2–2.5 GB**;
Pi 5 16 GB → 7–8B ~5–6 GB; ">14B at Q4: RAM-incompatible
with the toaster story." This ladder is a *recommendation
table*, honestly labelled "approx Q4" — Part III tests the
rungs it adopts, starting with the default target.

**Measured reality available today (from E-002/E-014, for
contrast, not as a verdict):** `src/ember` source is
732 KB / 104 files; the tracked monorepo is 217,404,018
bytes; a bare `ember` process's RSS has never been
measured by any slice (E-006 booted it; it did not weigh
it). E-041's first job is that weighing.

## 2. Verdandi — six RAM numbers for one member (SETTLE, then TEST)

Verdandi is two programs wearing one name — the **nerve
hub** (`nervous_system.py`, a Unix-socket event bus) and
the **heartbeat daemon** (pulse checks incl. Eir) — and
its documents price them interchangeably:

| Figure | For (as written) | Source |
|---|---|---|
| **~1 MB** RAM, "~1 MB base + ~100 bytes per subscriber" | nerve hub | `Verdandi/README.md:1591,1283`; `Verdandi/ARCHITECTURE.md:437` |
| **~13 MB** total (~12 MB of it the Python runtime) | heartbeat daemon | `Verdandi/docs/performance-guide.md` memory profile |
| **15 MB** idle (sleeping) | heartbeat daemon | same guide, benchmarks table ("Measured on a Raspberry Pi 4 (4GB RAM)") |
| **~15–25 MB** "Python process + SQLite"; storage ~5 MB total, DB ~1 KB/day | heartbeat on Pi | `Verdandi/docs/raspberry-pi-guide.md:14-16` |
| **<50 MB** RAM (nerve hub process), disk (feed, daily) <100 MB | targets, not measurements | `Verdandi/research/35_performance_benchmarks.md:32-35` |
| **~30 MB** memory, disk "small" | Verdandi (whole) | proposal sibling matrix, §5 |

No two documents reconcile these, and the comparison table
in Verdandi's own README prices Verðandi at ~1 MB against
Redis ~50 MB / Kafka ~500 MB+ — the hub's best number used
as the member's number. **For Part III:** measure hub and
heartbeat *separately*, on the Pi-class profile, and let
E-060's re-cut make the documents say which number belongs
to which program. (→ docket 65.)

Verdandi's *storage* claims, by contrast, agree everywhere
and are partly code-enforced (§4): the nerve feed grows
~200–500 bytes/event, ~22 MB/year at 200 events/day
(README + ARCHITECTURE + SYSTEM_VISION all derive the
same 22 MB from ~300 bytes × 200/day), and rotates at
10 MB. The Pi guide's "~5 MB total storage" sits beside
them unexplained (DB only? pre-rotation?) — part of the
same settlement.

Hardware-context lines that are **not** claims: the Pi
guides' "Pi 4/5 has 4 GB", the Eir thresholds
(RAM warning 80% / critical 95% of the *host*), and the
Pi Zero W (512 MB) tuning recipe in the Pi guide — a
configuration for a small host, with no cost figure for
Verdandi itself on that host.

## 3. Hamr — the one enforced budget, plus a second one (TEST; SETTLE the second)

**In code (the tree's model shape):**
`Hamr/src/hamr/core/perf.py` — `PerformanceBudget`:
`max_build_time_seconds = 45.0`, `max_memory_mb = 1500.0`
("Pi 5 target: under 1.5 GB"), `max_triangles = 50_000`,
`max_texture_resolution = 1024`, Blender timeout 120 s;
`estimate_memory_usage()` builds from a stated ~350 MB
Blender-headless base + ~1 MB per 1,000 triangles. Memory
tiers (CHANGELOG, PHASE_11_COMPLETE, PHASE_12_COMPLETE):
**minimal 512 MB / standard 1 GB / full 1.5 GB, "hard
caps."** Device tiers: `pi5` (512 MB VRAM), desktop,
cloud (unlimited).

**In Hamr's phase/architecture docs, the same budget
restated consistently** — ARCHITECTURE_11 ("Pi 5 Budget:
total <45 s, peak RSS <1.5 GB", test named
`test_build_memory_under_1_5gb`), PHASE_11 SC-9,
PHASE_12 SC-11, DATA_FLOW_11 D-11.6 ("needs profiling on
actual hardware" — honestly unproven), and Hamr's README
device table (Pi 5 ≤45 s / 1.5 GB; Desktop ≤30 s / 4 GB;
Cloud ≤15 s / 8 GB). E-138–E-140 execute exactly this
verification; the budget is *estimated* in pure Python
today, never yet measured against a real Blender build
on a Pi (Blender absent on the VM, E-006).

**The incompatible second budget (→ docket 68):**
`Hamr/PHASE_17.md` — "MEMORY BOUND: peak memory usage
remains **under 7.5 GB** (within Pi 5 8 GB headroom)" and
"file size **under 143 MB** (matching Seiðr-Smiðja's
143 MB ancestor VRM)". 7.5 GB is five times the perf.py
ceiling, for the same member on the same device class.
One of these is Hamr's budget; Part IX (E-140/E-142)
must say which, with E-041's book recording the answer.
Phase 17 also requires "at least 4 GB free RAM" as a
pre-flight check — a host requirement, not a cost.

Not claims: AUDIT_17's "324 GB free / 11 GB available"
(audit-day host facts), gpu_profiles' "≥64 GB RAM →
cloud" detection rule, test fixtures' memory ranges.

## 4. Code-enforced limits — budgets that already bind

These are not claims at all: the code applies them today.
Part III's book (E-041) should adopt them as the floor of
fact and E-042's tests should pin the ones that matter:

| Limit | Where | Value |
|---|---|---|
| Hamr build budget | `Hamr/src/hamr/core/perf.py` | 1,500 MB / 45 s (see §3) |
| `fetch_url` response cap | `src/ember/tools/fetch_url.py:53` | 1 MiB (`_MAX_RESPONSE_BYTES`) |
| Ollama NDJSON frame cap | `src/ember/spark/funi/ollama/adapter.py:58` | 1 MiB per frame |
| Well ingest file cap | `src/ember/well/smidja/local_files/source.py:82` | 64 MiB (`DEFAULT_MAX_FILE_BYTES`) |
| Verdandi nerve-feed rotation | `Verdandi/nervous_system.py:56` | 10 MB (`MAX_FEED_BYTES`) |
| Verdandi log rotation | `Verdandi/heartbeat/config.py:132` | 10 MB × backups (Pi guide suggests 5 MB / 1 MB shapes) |
| Verdandi pulse history prune | performance guide / heartbeat state DB | last 1,000 entries |
| mempalace miner file cap | `mempalace/mempalace/miner.py:77`, `convo_miner.py:62`, `normalize.py:122` | 500 MB (raised from 10 MB — the 10 MB cap silently dropped long transcripts; the raising is itself a budget lesson: a cap set without a workload in mind became a data-loss bug) |
| mempalace pass-zero caps | `mempalace/mempalace/cli.py:48-49` | 100 KB/file, 5 MB total |
| kista field length | — | **none** — `kista/BUG_REPORT.md:184`: a 10 MB password is accepted and bloats the vault (→ Part VI, E-094/E-102; recorded here, already a known bug report in-tree, not renumbered) |

## 5. The proposal corpora — 995 lines of *designed* budgets (ADOPT or STRIKE in Part III; never cite as measured)

`docs/` holds 995 of the 1,264 numeric size lines. None
of it describes the shipped code; all of it designs a
future Ember (Yggdrasil) or audits *other* programs (the
codices). The load-bearing sets:

- **The Tiny Device Profile** (`docs/yggdrasil/cross-
  platform/67_TINY_DEVICE_PROFILE.md`): target Pi Zero 2 W
  (**512 MB RAM**) / 1 GB netbook. Its own RAM budget —
  OS 150 + Stofa TUI 30 + Funi (TinyLlama 1B Q4) 400 +
  Brunnr 20 + Verdandi 5 + Seiðr 5 + Kista 2 + overhead
  10 = **~622 MB — and the document itself writes
  "(over budget!)"** beside the sum, then falls back to a
  0.5B model (~300 MB) and a `budget.ram.max_mb: 350`
  config shape. An honest proposal that does not close:
  Part III's toaster profile starts from this admission,
  not from the 512 MB headline. (→ docket 66.) It also
  asserts, as design rules, "CloakBrowser (Chromium needs
  >2 GB)" and "real-time mood classifier (needs ~500 MB)"
  — exclusion reasons Part III should verify or drop.
- **Tiered defaults** (`…/62_TIERED_DEFAULTS_BY_PROFILE.md`):
  `ram.max_mb` = **400 (TINY) / 2,000 (SMALL) / 6,000
  (MEDIUM) / 16,000 / 32,000** by profile, with model
  sizes to match (1B ~600 MB … 8B ~5 GB). These five
  numbers contradict the Tiny profile's own 350 MB cap
  for the same TINY class (400 ≠ 350, and neither is
  measured). (→ docket 66.)
- **Resource budgeting** (`…/61_RESOURCE_BUDGETING.md`):
  the rule "RAM max = 50% of total" (TINY 30%), disk
  `max_state_gb: 50` — a policy proposal, no measurements.
- **The sibling matrix** (`docs/yggdrasil/siblings/
  10_SIBLING_MATRIX_OVERVIEW.md:106-115`): round-number
  runtime estimates per member — bifrost ~50 MB memory /
  ~2 MB disk; mimir-well ~30 MB; Verdandi ~30 MB; Seiðr
  ~20 MB / <1 MB disk; Kista ~10 MB / <100 KB disk; Hamr
  ~200 MB / ~50 MB disk; CloakBrowser ~300 MB / ~200 MB
  disk; astrology ~50 MB / ~30 MB ephemeris; dictionary
  ~50 MB disk. **Every figure is unsourced**, and several
  sit oddly beside E-002's measured trees (bifrost's whole
  tree is 92 KB; the dictionary's is 24 MB, mostly data —
  its "~50 MB" matches nothing measured). Treat as
  placeholders Part III replaces with measurements.
  (→ docket 69.)
- **Stofa TUI budgets** (`docs/tui/operations/
  90_PERFORMANCE_BUDGETS.md`): Empty Stofa **<50 MB RSS**;
  +50-turn conversation <80 MB; +1,000-turn <200 MB;
  +active ingest <500 MB — with named CI tests
  (`test_stofa_launch_budget.py`, `test_idle_memory_
  under_50mb`). **Neither test file exists in the tree**
  (verified this slice: no such file under `tests/` or
  anywhere tracked), and the TUI itself is the dormant
  design tree of E-014. Proposal + absent tests.
  (→ docket 71.)
- **SAP codex resource budgets** (`docs/sap_codex/
  50_verification/52_RESOURCE_BUDGETS.md`): an audit of
  *Super Agent Party's* claimed "2 cores, 2 GB RAM" floor,
  concluding in its own words the claim is "technically
  true (the process can start) and operationally false
  (anything past minimum interactive chat overruns)" —
  filed here as Part III's cautionary template for how
  Ember's own floor claim (§1) must be tested: by
  workload, not by boot. Its per-feature cliffs (MiniLM
  ~470 MB disk / ~700–900 MB loaded, Moss TTS 2–3 GB,
  bot SDKs ~500–700 MB for eight) are SAP's numbers,
  not Ember's.
- **Edge-LLM research** (`docs/research/31-edge-llm-
  pi5.md`): Pi 5 16 GB LLM table (1–3B Q4 ~1–2 GB,
  7–8B Q4 ~5–6 GB, up to 22–32B Q3 ~12–15 GB) — external
  research numbers, consistent in shape with the FUNI
  ladder, citable as research, not as Ember measurements.

## 6. Vendored claims — CloakBrowser (Part XI's, not Ember's)

CloakBrowser's own documents price *itself*: binary
download **~200 MB** cached; **~190 MB RAM idle, ~280 MB
with 3 tabs, ~30 MB per additional tab** (`CloakBrowser/
README.md:897`); GeoIP database ~70 MB on first use; its
Lambda integration guide's 3,008 MB memory / 1,024 MB
ephemeral-storage figures are AWS sizing for that
integration, not product claims. Per the vendored law
these words are CloakHQ's, never rewritten and never
adopted as Ember claims; E-179 measures the browser's
cost per profile *for Ember's book* and profiles that
cannot carry ~190 MB idle say so there. This is also the
hard floor under any "whole monorepo on a toaster"
reading: the vendored browser alone exceeds the Tiny
profile's entire RAM budget — one more proof that the
budgets are per-member, per-profile (roadmap §1).

## 7. Members with no budget of their own

- **mempalace:** no RAM ceiling anywhere. Its only cost
  figures: "~300 MB disk for the default embedding model"
  (its README + benchmarks), benchmark data ~300 MB,
  embedding-model downloads ~300–1,300 MB by model, and
  an HNSW note ("441 GB→433 KB on large palaces", its
  ROADMAP, an upstream incident figure). Its benchmark
  suite *measures* RSS growth (tests/benchmarks) but
  asserts no budget. Part V's harness (E-078) is where
  its cost gets numbers; Part III's book gains the row
  from there. (→ docket 70.)
- **mimir-well:** no size/RAM claim in any member doc —
  its "budgets" are *token* budgets for context assembly
  (ContextEngineer / TokenBudgeter), a different currency.
  E-002 measured its tree at 716 KB (638 KB in E-012's
  recount of the package); that is a source size, not a
  runtime cost. (→ docket 70.)
- **seidr_engine:** no cost claim (pure computation;
  the sibling matrix's ~20 MB is a proposal figure, §5).
- **bifrost:** no claim in its own docs (14 numeric hits
  tree-wide were other files' words); sibling matrix only.
- **kista:** no cost claim; the vault's on-disk shape is
  E-011's (Fernet `vault.json.enc`), and its one size
  text is the unbounded-field bug report (§4). E-103 is
  its budget proof, per the roadmap.
- **astrology-engine:** no cost claim for itself; it
  *recommends a host* (Pi 5 16 GB, its README:91) and
  its ROADMAP proposes a future offline city database
  at "~2–3 MB" — a plan figure for an unbuilt feature.
- **Open-VTT:** zero numeric size/RAM lines in the member
  (Godot's cost is the engine's; E-160 states it there).
- **Dictionary:** zero in-member claims (24 MB measured
  tree, E-002, is data, not a claim).

## 8. What Part III inherits — the test-or-strike list

For E-041 (the budget book) and E-042 (budget tests),
in the order Part III should take them:

1. **TEST:** core installed disk (~50 MB ex-models) and
   core idle/turn RSS (~50 MB; Well-resident 50 MB) —
   §1. The project's name rides on these.
2. **SETTLE, then TEST:** Verdandi hub vs heartbeat RAM
   (six figures → two measured numbers) — §2, docket 65.
3. **TEST:** Hamr perf.py budget on real Pi-class
   hardware (via E-138–140); **SETTLE:** Phase 17's
   7.5 GB / 143 MB second budget — §3, docket 68.
4. **ADOPT:** the code-enforced limits of §4 as pinned
   floors (they already bind; tests keep them honest).
5. **DECIDE:** the toaster profile's floor — Tiny
   proposal's 512 MB (self-admittedly over budget),
   tiered defaults' 400 MB, or a measured floor of
   Part III's own — §5, docket 66.
6. **REPLACE:** sibling-matrix round numbers with
   E-057's measured member table — §5, docket 69.
7. **SET (nothing to test):** mempalace, mimir-well,
   seidr, bifrost, kista, astrology budgets from
   E-078/E-103-class measurements — §7, docket 70.
8. **RECORD, don't adopt:** CloakBrowser's vendored
   figures — §6, for E-179.
9. **STRIKE or BUILD:** Stofa's <50 MB RSS budget and
   its two named-but-absent tests — §5, docket 71
   (with the TUI tree's own dormant status, E-014).

## Carried to the E-016 docket

(65) Verdandi's documents state six different RAM
figures for overlapping scope — nerve hub ~1 MB
(README/ARCHITECTURE), heartbeat ~13 MB total and
15 MB idle (performance guide, "measured on Pi 4"),
~15–25 MB (Pi guide), <50 MB target (research 35),
~30 MB (proposal sibling matrix) — with no document
distinguishing hub from heartbeat, and the README's
comparison table using the hub's ~1 MB as the member's
figure against Redis/Kafka. Storage figures likewise
mix ~5 MB total (Pi guide) with the agreed ~22 MB/year
feed growth. Assigned to Part III (E-041: measure hub
and heartbeat separately) and Part IV (E-060: make the
documents name which program each number prices).
(66) The Yggdrasil Tiny Device Profile is internally
inconsistent and self-admittedly over budget: its RAM
budget sums to ~622 MB on a 512 MB target (the document
itself annotates "over budget!"), its fallback config
caps RAM at 350 MB, and the tiered-defaults doc caps
the same TINY class at 400 MB — three numbers, none
measured, for the roadmap's most important profile.
Its exclusion rules (CloakBrowser >2 GB, mood
classifier ~500 MB) are likewise unmeasured. Assigned
to Part III (E-041/E-049: the Toaster Test settles the
floor by measurement; the proposal numbers are struck
or adopted there, explicitly).
(67) The core's front-door budget claims have never
been measured: ~50 MB installed (ex-models), ~50 MB
RAM for "Ember itself", 50 MB resident for the default
Well (root README + `deploy/pi/INSTALL.md` +
sqlite_vec README). Scope ambiguity is the sharp edge:
the claims price the installed core alone while the
tracked monorepo weighs 217 MB — a reader who conflates
them either convicts Ember of a false claim it never
made or credits the monorepo with a smallness it does
not have. Assigned to Part III (E-041/E-045: weigh the
installed core, idle and per-turn, on the VM profile
first, then Pi-class; E-197's claims audit consumes
the result).
(68) Hamr carries two incompatible memory budgets:
perf.py's enforced 1.5 GB Pi 5 ceiling (tiers to
512 MB) vs PHASE_17's "peak under 7.5 GB" bound and
143 MB VRM file bound. Assigned to Part IX
(E-140/E-142: verification states which budget governs
which build shape; E-041's book records both with
their scopes or the struck one).
(69) The Yggdrasil sibling matrix's per-member runtime
estimates (bifrost ~50 MB, mimir-well ~30 MB,
Verdandi ~30 MB, Seiðr ~20 MB, Kista ~10 MB, Hamr
~200 MB, CloakBrowser ~300 MB, astrology ~50 MB,
dictionary ~50 MB disk) are round, unsourced, and in
places at odds with E-002's measured trees. Assigned
to Part III (E-057: the measured member budget table
replaces them as the citable source; the matrix is a
proposal doc and is not edited by this campaign —
the table in E-057 is where the truth lives).
(70) Five members state no size/RAM budget at all —
mempalace (disk figures only, ~300 MB embedding model;
RSS measured by its benchmarks but never budgeted),
mimir-well (token budgets only), seidr_engine,
bifrost, kista — so Part III has nothing to test for
the majority of the monorepo's weight (mempalace
alone is 59 MB of tree). Assigned to Part III
(E-041/E-057: budgets set from measurement) with
E-078 (mempalace/mimir harness) and E-103 (kista)
feeding the numbers.
(71) The Stofa TUI performance-budget doc names CI
tests that do not exist (`test_stofa_launch_budget.py`,
`test_idle_memory_under_50mb` — verified absent from
the tracked tree this slice) for budgets (<50 MB RSS
empty, <80 MB at 50 turns, <200 MB at 1,000 turns)
over a TUI that is itself an unbuilt design tree
(E-014). Assigned to E-018 (verdict preparation, with
the TUI's dormant status) and Part III (if Stofa is
ever built, its budgets enter E-042 as real tests or
not at all).

## Slice gate

Root suite re-run in the E-001 shape (pgvector file
excluded, default env; `TMPDIR` redirected to the
workspace overlay as in E-013/E-014): **546 passed,
6 failed, 12 skipped** — identical to the opening
baseline; the 6 failures are the proven environment
failures. Doc-only slice, no code touched, no README
touched. Push: under Volmarr's 2026-10-31 standing
go-ahead, this slice's commit was pushed to origin
`yrsa/ember-road-build` after fetch + ancestry check
and verified by `ls-remote`: remote head = local head
(recorded in the state file).

# Project Ember — Run It On Your Smart Toaster: The Up-to-Date Massive Roadmap

*Commissioned by Volmarr Wyrd, 2026-10-30: "make a totally up to
date massive roadmap for this project and then start working hard
on it."*

Repo: `hrabanazviking/Project_Ember_Run_It_On_Your_Smart_Toaster`
(default branch `development`). This roadmap is the law of the
build that follows it.

## 1. What Ember is

`ember-agent` v0.2.0 (MIT): **"a small, tethered, runs-anywhere AI
companion"** — an AI friend for normal folks on tiny hardware. No
data centres, no gaming rigs: the project's name is its promise,
that a companion worth having can live on the humblest machine in
the house. This repo is also the home monorepo of the Hermes/Runa
lineage (forked to Ember 2026-05-19 from the Runa-inherited base),
which is why it holds a whole constellation under one roof.

**Tiny-hardware budgets are the project's soul.** Every slice in
this road states the budget it respects; a feature that cannot live
within a small profile's budget is labelled with the smallest
profile it *is* proven on — never smuggled in as universal.

## 2. The true state (recon 2026-10-30, GitHub API — to be re-proven in-tree by Part I)

A monorepo of many members, each with its own history:

- `src/ember/` — the agent core (the companion itself).
- `Verdandi/` — the event/nerve hub (context_injector,
  conversation_logger, + its own docs and its own roadmap).
- `kista/` — **the Smart Toaster Kista**, a credential program for
  tiny machines. ⚠️ It is a *separate program* from the Kista in
  Volmarr's ai folder on purplelongship (Runa's strongbox, the one
  Heimdall uses). The two share a name and a spirit, not a codebase.
  This roadmap never conflates them; Part VI gives the toaster's
  Kista its own road and writes the boundary down.
- `mempalace/` and `mimir-well/` — **two** memory systems under one
  roof. Part V renders their verdict.
- `seidr_engine/`, `astrology-engine/` — the companion's inner life:
  the seiðr engine and the astrology engine.
- `bifrost/` — the bridge/transport member.
- `Hamr/` — the VRM avatar builder with a Blender bridge;
  ARCHITECTURE + PHASE docs run through Phase 17, several marked
  COMPLETE. Marked is not proven: Part IX verifies before it builds.
- `Open-VTT/` — a Godot virtual tabletop member.
- `CloakBrowser/` — **vendored** third-party stealth browser, with
  its own LICENSE and README. Never rewritten, never relicensed;
  stewardship only (Part XI).
- `cleasby-vigfusson-old-norse-dict/` — the Old Norse dictionary
  member (Volmarr's canon tooling).
- Root: pyproject + `tests/`; `deploy/`; and five elder commissions
  as codex files — `TASK_CHATDOLL_CODEX.md`, `TASK_HERMES_CODEX.md`,
  `TASK_RAGNAROK_CODEX.md`, `TASK_SUPER_AGENT_PARTY_CODEX.md`,
  `TASK_WAIFU_CODEX.md` — each reconciled in Part X.
- `ORIGINS.md` — the provenance register (scribe Eirwyn Rúnblóm,
  updated 2026-05-21): where every member came from. **Keep / merge
  / remove decisions are made from ORIGINS, nowhere else.** Part I
  executes no removal — it *prepares* verdicts; removals of anything
  are Volmarr's word, never the campaign's.

Local note: Volmarr's own checkout of this repo lives at
`~/ai/ember/` on purplelongship (the ai-folder Kista update sits
uncommitted there — his call, untouched by this campaign). The
campaign works in its own clone, `~/workspace/ember-build/`.

## 3. Laws of this campaign

- **Volmarr's laws, all of them:** keeper discipline (the
  10-minute timer CONTINUES stopped work), never leave a discovered
  bug unfixed, no Docker ever (any Dockerfile in the tree is never
  used), never touch any README.md (root or any subproject's),
  plain language first in reports.
- **Budgets before features:** size/RAM ceilings per profile are
  set in Part III and enforced as tests thereafter.
- **Vendored means vendored:** CloakBrowser (and any other
  third-party member ORIGINS marks as such) keeps its licences and
  its code; the campaign wraps, never rewrites.
- **Provenance is sacred:** ORIGINS.md is read before any member is
  judged; the register itself is extended, never rewritten.
- **Counts from the runner only;** hardware claims name the device.
- **"For normal folks" is a design law:** every user-facing surface
  is judged by whether a non-technical person succeeds unaided
  (the Stranger Test, Part XII).
- Banking is local per slice; pushes await Volmarr's word (sole
  exception: this roadmap's own filing).

## 4. The roadmap — 204 slices in 12 parts

Numbering: **E-###**. Elder documents cite as: ORIGINS, Verdandi
roadmap (VD-RM), Hamr phases (HAMR-Ph#), codex files by name.

---

## Part I — The Monorepo's True State (E-001 – E-018)

*Goal: every member inventoried, every elder claim re-measured,
every verdict prepared from ORIGINS — before anything is built.*

- **E-001** Campaign opening: clone, branch `yrsa/ember-road-build`,
  roadmap filed under `docs/` + pushed (filing only), state file.
- **E-002** Member census: every top-level member — purpose, size,
  language, entry points, test presence, last-evidence-of-life.
- **E-003** ORIGINS concordance: the register's every claim × the
  tree's reality (PRESENT / MOVED / ABSENT / GROWN-BEYOND), filed
  as the audit's spine.
- **E-004** Fresh baseline I: the root `tests/` run whole; counts
  from the runner; failures classified (real / environment / stale).
- **E-005** Fresh baseline II: each member's own tests (where they
  exist) run in its own shape; the per-member truth table.
- **E-006** Boot census: what actually starts today — `ember-agent`
  core first, then each member's entry point, on the VM profile.
- **E-007** Dependency & licence audit across members (vendored
  licences verified intact; contamination flagged with fixes named).
- **E-008** The codex census: the five TASK_*_CODEX commissions —
  each one's ask, its state in the tree (DONE-in-fact / PARTIAL /
  ABSENT), evidence-linked (verdicts land in Part X).
- **E-009** The Verdandi concordance: Verdandi's own roadmap × its
  code (feeds Part IV's re-cut).
- **E-010** The Hamr verification plan: HAMR-Ph1–17's COMPLETE
  claims listed with the artefact that would prove each (Part IX
  executes the verification).
- **E-011** The two-Kistas boundary doc: toaster-Kista vs ai-folder
  Kista — codebases, purposes, custody rules — written plainly so
  no future worker conflates them again.
- **E-012** The two-memories census: mempalace vs mimir-well —
  overlap, uniqueness, consumers (feeds Part V's verdict).
- **E-013** Config & secrets census: every member's config shape;
  anything credential-shaped found in plain files is a defect,
  docketed for its part (custody rule: E-093).
- **E-014** Dead/duplicate census across members (kin to E-003).
- **E-015** Budget archaeology: any size/RAM claims in member docs
  collected for Part III to test or strike.
- **E-016** The bug & gap docket: every defect found in Part I,
  numbered, assigned to its part (nothing found, nothing unfixed —
  the docket is the proof).
- **E-017** Baseline freeze: suite + boot results pinned as the
  campaign's zero line, method recorded for keeper re-measurement.
- **E-018** Part I gate: audit published in-repo; verdicts prepared
  (not executed) for every member; plain-language summary filed;
  the road below re-cut if facts demand (changes recorded here).

## Part II — The Ember Core: a Companion That Works (E-019 – E-040)

*Goal: `src/ember/` becomes a small, documented, dependable agent
core — the friend itself, before its organs.*

- **E-019** Core loop mapped: the companion's turn lifecycle drawn
  from code; architecture doc published.
- **E-020** Tethering made explicit: what "tethered" means in the
  code (to its person, its machine, its memory) — specified,
  tested, and stated in user docs.
- **E-021** Conversation engine hardening: history, windowing,
  summarisation hooks under a token budget (profile-aware).
- **E-022** Model backends: the core's backend contract + its
  existing backends conformed; capability truth per backend.
- **E-023** Aesir backend for Ember: Project Aesir bound under
  E-022's contract (its ledger respected) — the tiny companion on
  Volmarr's own engine.
- **E-024** ThoughtForge binding (candidate): MindSpark ThoughtForge
  as the core's cognition layer on profiles that afford it
  (TF-road's TF-159 consumes the same contract from its side).
- **E-025** Persona core: who the companion *is* — persona loading,
  validation, and per-persona memory separation (fixtures: two
  personae, adversarial prompts).
- **E-026** Tools discipline: the core's tools inventoried; each
  tool's permission shape stated; dangerous-by-default tools gated.
- **E-027** Approval shape for normal folks: tool approvals a
  non-technical user understands (plain words, rememberable scopes).
- **E-028** Streaming + interruption: the companion can be talked
  over; state stays coherent.
- **E-029** Offline truth: with the network cut, the core's full
  local life works — proven, with the degraded set listed honestly.
- **E-030** Error honesty: failures surface as truthful plain
  messages; never a fabricated completion.
- **E-031** Session persistence: conversations survive restarts,
  atomic writes (the Samtal lesson), corruption fixtures.
- **E-032** The day-one flow: install → first model → first chat,
  timed and friction-audited (Part XII's Stranger Test consumes).
- **E-033** Config for humans: one config surface, sane defaults,
  every key documented in plain words (E-013's live keys only).
- **E-034** Logging a friend can read: the companion's diary-shaped
  log (what happened, in words) beside the technical trace.
- **E-035** Multi-conversation isolation (fixtures prove no bleed).
- **E-036** Determinism mode for tests/benchmarks (seeded).
- **E-037** Core API freeze v1 (library shape) — members and
  bindings (Parts IV–X) bind here.
- **E-038** Concurrency on small hardware: two chats, phone-class
  budgets, measured.
- **E-039** Core docs + runnable examples.
- **E-040** Part II gate: day-one flow green end-to-end on the VM
  profile; API frozen; summary filed.

## Part III — Tiny Hardware Is the Soul (E-041 – E-058)

*Goal: the budgets, named and enforced — and the name of the
project cashed on real small machines.*

- **E-041** The budget book: per-profile ceilings (install size,
  idle RAM, turn RAM, storage growth/month) set from E-015's
  archaeology + measurement; profiles: toaster (the smallest),
  phone-class, pi-class, laptop.
- **E-042** Budget tests: the ceilings become automated tests wired
  into the campaign's slice gate.
- **E-043** Install weight cut I: the heaviest members measured;
  optional members made truly optional at install.
- **E-044** Install weight cut II: dependency diet per E-007 (each
  removal/replacement measured before/after).
- **E-045** Idle discipline: at rest the companion costs ~nothing —
  measured over an hour, per profile.
- **E-046** Cold start on the smallest profile: time-to-first-word
  measured + capped.
- **E-047** The Pi proof: the full companion on Mimir-class hardware
  (real Pi or NOT PROVEN, stated plainly).
- **E-048** The phone-class proof (simulated profile + any real
  device the house can offer; proof grade labelled).
- **E-049** **The Toaster Test**: the smallest honest target the
  house can muster (oldest/smallest machine available) runs the
  companion through the day-one flow — the project's name, cashed
  or honestly graded.
- **E-050** Storage growth: a month of companionship simulated;
  growth within budget or the lifecycle rules (Part V) tighten.
- **E-051** Thermal & patience etiquette: on shared/small machines
  the companion yields (load-aware throttling, the Aesir lesson).
- **E-052** Update weight: an update's download + apply cost per
  profile (metered connections respected).
- **E-053** Battery-shaped behaviour (phone-class): duty cycling,
  no busy-wait, measured drain shape.
- **E-054** Graceful smallness: at budget's edge the companion
  sheds features by the stated ladder, announcing each shed.
- **E-055** The budget book published in-repo with its measurements.
- **E-056** Regression armour: budget tests join the permanent gate.
- **E-057** Member budget table: every member's cost per profile —
  the monorepo's weight, honestly itemised.
- **E-058** Part III gate: budgets enforced by tests; Toaster Test
  verdict recorded with its device named; summary filed.

## Part IV — Verdandi: the Nerve Hub (E-059 – E-076)

*Goal: the event/nerve system the whole constellation feels
through — concorded with its own roadmap, then completed.*

- **E-059** Verdandi mapped: context_injector, conversation_logger,
  and the event model drawn from code.
- **E-060** The VD-RM concordance executed: Verdandi's own roadmap
  items × reality (E-009) — its remaining road re-cut into this
  part's order, its completed claims verified by tests.
- **E-061** Event contract v1: event shapes versioned; producers/
  consumers listed per event.
- **E-062** Context injection discipline: what may be injected,
  when, with what budget — the injector's rules as tests.
- **E-063** The conversation logger's law: what is logged, where,
  for whom; retention + the user's delete right (total, provable).
- **E-064** Stimuli: external events (time, sensors-shaped inputs,
  messages) enter as typed stimuli with provenance.
- **E-065** The reflex layer: fast, dumb, safe reactions below
  cognition (never speaks for the companion — the Heimdall doc-05
  instinct, applied).
- **E-066** Nerve health: a stuck/dead nerve is detected and
  reported; the hub degrades honestly (the Hermes baseline's
  Verdandi-socket failures are this part's cautionary fixture).
- **E-067** Cross-member nerves: ember core ⇄ Verdandi ⇄ memory
  (Part V) wired under E-061's contract.
- **E-068** Hermes-shaped nerves: the Verdandi event shapes matched
  against the Hermes hack's volmarr-core session/turn/tool events
  (post-refresh surfaces) — one dialect or a documented translation.
- **E-069** Ordering & replay: events replay deterministically for
  debugging (fixtures).
- **E-070** Backpressure on tiny hardware: a flooded hub sheds by
  rule, reflexes first-protected.
- **E-071** Privacy of nerves: stimuli provenance never leaks
  across personae (fixtures).
- **E-072** The logger as memory source: logged conversations can
  feed memory (Part V) under the user's rule, never silently.
- **E-073** Verdandi standalone: the hub usable without the full
  companion (its own consumers exist in the constellation).
- **E-074** Docs: the nerve model for member-builders.
- **E-075** Load truth: hub throughput per profile, measured.
- **E-076** Part IV gate: VD-RM's remaining road closed or re-roaded
  with owners; event contract frozen; summary filed.

## Part V — Memory: Two Systems, One Verdict (E-077 – E-092)

*Goal: mempalace and mimir-well judged on evidence — unified,
bounded, or one retired honourably (retirement is Volmarr's word;
this part prepares and, where he has already implied it, proposes).*

- **E-077** Both systems mapped: storage shapes, retrieval,
  consumers, test state (E-012 executed in depth).
- **E-078** The comparison harness: identical workloads through
  both (recall, latency, size, budget per profile).
- **E-079** The verdict paper: unify / bound / retire — argued from
  E-078's numbers + ORIGINS provenance, presented for Volmarr's
  word where a retirement is proposed.
- **E-080** The chosen shape implemented: one memory contract for
  the companion (whichever system(s) survive, behind one face).
- **E-081** Migration: existing stores of the losing shape migrate
  losslessly (fixtures on synthetic stores) — or are read-compat
  forever, per the verdict.
- **E-082** Memory lifecycle: growth, decay, pruning under Part
  III's storage budget (E-050 consumed).
- **E-083** Persona separation enforced at the memory face (E-025's
  fixtures at this layer).
- **E-084** The user's memory rights: inspect, correct, export,
  delete-total — as working operations, plain-worded.
- **E-085** Memory ↔ Verdandi: conversation_logger's records and
  memory's facts reconciled (one truth, two views or a stated
  boundary).
- **E-086** Memory ↔ WYRD-shaped export: the companion's memory
  exportable in the shapes the constellation's world-model work
  consumes (ThoughtForge TF-145's boundary, honoured).
- **E-087** Corruption & recovery drills (atomicity, kill-mid-write).
- **E-088** Long-life soak: a simulated year of memory within
  budgets (accelerated fixtures).
- **E-089** Canon-shaped test data only (synthetic; no real
  companion history in fixtures).
- **E-090** Docs: the memory model for users (plain) + builders.
- **E-091** The verdict's residue: the retired/bounded system's
  docs marked truthfully (superseded, with the successor named).
- **E-092** Part V gate: one memory face live; migration proven;
  the verdict paper + Volmarr's word (where required) on record.

## Part VI — Kista of the Toaster (E-093 – E-106)

*Goal: the monorepo's own credential keeper, finished as a program
in its own right — small enough for the smallest machine, honest
about what it is and is not.*

- **E-093** Custody law for the whole campaign: credentials live in
  a Kista (toaster's or ai-folder's, per machine) — never in
  configs, code, or chat (E-013's defects land here first).
- **E-094** Toaster-Kista mapped: its storage, crypto shape, CLI/API
  surface, test state — from code.
- **E-095** Threat model sized for tiny machines: what it defends,
  what it cannot (stated, never implied otherwise).
- **E-096** The unlock experience for normal folks: passphrase flow
  a non-technical user survives; recovery story stated honestly.
- **E-097** Per-program access: a program gets only its own entries
  (the ai-folder Kista's proven pattern, in toaster shape).
- **E-098** Entry kinds: passwords, tokens, URLs, notes — the
  toaster set; the ai-folder Kista's wider ambitions (states,
  prompts, habits) recorded as *its* road, not silently merged.
- **E-099** Interop truth: can the two Kistas exchange entries?
  Studied; if yes, a one-way export/import with verification; if
  no, the boundary doc (E-011) gains the technical reason.
- **E-100** Ember core binding: the companion fetches its model/API
  credentials from toaster-Kista under E-097.
- **E-101** Backup & restore of a tiny vault (user-carried file,
  encrypted; restore proven).
- **E-102** Audit fixtures: wrong-passphrase, tampered-vault,
  partial-write drills.
- **E-103** Budget proof: the vault's cost on the toaster profile
  (Part III's book gains its row).
- **E-104** Docs: Kista for users (plain) + the boundary doc final.
- **E-105** The naming kindness: user-facing names distinguish the
  two Kistas without jargon (support-confusion prevented).
- **E-106** Part VI gate: core binding live; drills green; the
  boundary with the ai-folder Kista documented + (E-099) executed.

## Part VII — The Inner Life: Seiðr Engine & Astrology Engine (E-107 – E-122)

*Goal: the companion's soul-organs — the seiðr engine and the
astrology engine — mapped, tested, and woven into the companion
deliberately rather than decoratively.*

- **E-107** Seiðr engine mapped: what it computes/models, its
  inputs/outputs, its consumers today.
- **E-108** Astrology engine mapped: chart maths, ephemeris source,
  accuracy fixtures against known references.
- **E-109** Astrology accuracy gate: the engine's outputs verified
  to the standard Volmarr's practice requires (his natal data is
  the *shape* of the fixture; fixtures themselves synthetic or his
  own published data only).
- **E-110** The engines as services to the core: typed requests/
  responses under the member contract (E-037's kin).
- **E-111** Ritual-shaped time: the companion can know the day's
  astrology (the dawn-ritual pattern) as a Verdandi stimulus
  (E-064) — computed, not fetched.
- **E-112** Seiðr in conversation: what the engine offers a chat
  (draws, interpretations as *data*) — with the honesty rule: the
  engine computes; meaning is the companion's voice, labelled.
- **E-113** Determinism + offline: both engines fully local,
  reproducible (seeded/date-pinned fixtures).
- **E-114** Budget rows: both engines in the budget book (E-057).
- **E-115** The dictionary binding: cleasby-vigfusson as a lookup
  service for the companion (Old Norse words in conversation,
  answered from the real dictionary).
- **E-116** Dictionary data hygiene: the dictionary member's data
  provenance per ORIGINS; lookup correctness fixtures.
- **E-117** Persona + inner life: a persona may draw on the engines
  per its config (off by default for personae that shouldn't).
- **E-118** No-hardcoded-soul rule: nothing in the core assumes one
  spirituality; the engines are members, not doctrine.
- **E-119** Engine docs + examples (a chart cast + a draw, runnable).
- **E-120** Failure honesty: bad dates/places yield stated errors,
  never fabricated charts.
- **E-121** Cross-check with the house's other astrology: the
  engine's results compared against the dawn-briefing pipeline's
  (discrepancies investigated, one truth or a stated reason).
- **E-122** Part VII gate: both engines service-bound, accuracy
  gated, dictionary live; summary filed.

## Part VIII — Bifrost: the Bridges (E-123 – E-136)

*Goal: how the companion reaches and is reached — transports and
bridges under one discipline, loopback-first and honest.*

- **E-123** Bifrost mapped: its transports, protocols, consumers.
- **E-124** Bridge contract v1: what a bridge must guarantee
  (delivery truth, ordering, identity of speaker).
- **E-125** The local bridge: companion ⇄ other programs on the
  same machine (the constellation's daily road).
- **E-126** The Hermes bridge: Ember ⇄ the Hermes hack (post-refresh
  plugin surfaces) — a companion on each side of the bridge, or
  Ember as Hermes' body on tiny hardware (shape decided by spike).
- **E-127** The Samtal-shaped bridge (study + contract): an Ember
  companion as a Samtal seat's body — under Samtal's law, cognition
  questions routed via Part II/ThoughtForge per config.
- **E-128** Messaging-shaped bridges (study): the companion reachable
  from chat surfaces Volmarr actually uses — contract + one proof
  bridge, the rest roaded honestly.
- **E-129** Voice over the bridge (shape): audio in/out as bridge
  payloads, sized for tiny hardware (the Rúnmál loop is the elder
  cousin; no reinvention without cause).
- **E-130** Bridge security: pairing, per-bridge permissions, the
  kill switch (a bridge can be cut by its user in one act).
- **E-131** Offline queueing: bridges queue honestly when the far
  side sleeps; delivery truth preserved on wake.
- **E-132** Bridge budgets: per-bridge cost rows in the budget book.
- **E-133** Identity honesty: a bridged companion is labelled as
  itself everywhere (scripted-agent disclosure, doc-05 instinct).
- **E-134** Bridge fixtures per contract (fake far sides).
- **E-135** Docs: a new-bridge recipe.
- **E-136** Part VIII gate: local + Hermes bridges proven; studies
  filed with honest grades; contract frozen.

## Part IX — Hamr: the Face (E-137 – E-156)

*Goal: the avatar builder verified phase by phase, then finished —
a companion you can see, built within tiny budgets.*

- **E-137** Hamr mapped: architecture, the Blender bridge, the VRM
  pipeline, from code + its docs.
- **E-138** HAMR-Ph1–17 verification I: the earliest phases'
  COMPLETE claims re-proven by running their artefacts/tests.
- **E-139** HAMR-Ph verification II: middle phases likewise.
- **E-140** HAMR-Ph verification III: latest phases likewise; the
  verification table published (PROVEN / PARTIAL / NOT PROVEN per
  phase — marked-COMPLETE is not evidence).
- **E-141** The Blender bridge discipline: Blender as an external
  tool (native install; no Docker), versioned expectations, honest
  absence behaviour.
- **E-142** The unproven remainder re-roaded: any phase that failed
  verification gets slices here, in dependency order (count set by
  E-140's table, recorded in the state file).
- **E-143** Build-a-face flow: from the companion's persona to a
  VRM, end-to-end, timed on the laptop profile.
- **E-144** The face at runtime: the built avatar driven by the
  companion (lip/energy from voice where the runtime allows) —
  scoped honestly per runtime.
- **E-145** Hamr ⇄ Open-VTT handshake (study): Hamr faces inside
  the tabletop member (Part X) — contract only, unless cheap.
- **E-146** Asset budgets: a face's size/render cost in the budget
  book; toaster-profile truth stated (likely: built on bigger
  hardware, *shown* on small — graded honestly).
- **E-147** The Yrsa-shaped test: a face built for a persona with
  Volmarr's canon traits as the acceptance shape (canon data stays
  local; the test persona is synthetic unless he offers his own).
- **E-148** Export truth: VRM exports validated by an external
  viewer's load test (or the best available validator, named).
- **E-149** Failure honesty in the pipeline: a failed build stage
  says which and why, with the partial artefacts kept.
- **E-150** Hamr docs reconciled with verified reality (phase docs
  extended, their COMPLETE marks now evidence-backed or corrected
  in the verification table — the phase docs themselves are elder
  text: corrections live in the table, per the README-law spirit).
- **E-151** The face gallery: built faces as persona assets
  (Part II's persona core consumes).
- **E-152** Accessibility: a face is never the only carrier of
  meaning (the Design Lawbook rule).
- **E-153** Hamr standalone: usable without the companion (its own
  builders exist).
- **E-154** Performance on the Pi profile: viewing (not building)
  measured or NOT PROVEN.
- **E-155** Residue: any Hamr sub-part failing everything is
  verdict-prepared for Volmarr (archive proposal), not silently
  dropped.
- **E-156** Part IX gate: verification table complete; the build-a-
  face flow green; remainder roaded or closed; summary filed.

## Part X — The Table & the Codices (E-157 – E-174)

*Goal: Open-VTT judged on its feet, and the five elder codex
commissions reconciled — each closed with evidence, absorbed into
the road, or honourably retired by verdict.*

- **E-157** Open-VTT mapped: the Godot member's state — what runs,
  what's stub, what's aspirational (Godot as external native tool).
- **E-158** Open-VTT proof: the tabletop opens, a scene loads, a
  token moves — or the honest list of what stops it (docketed).
- **E-159** VTT ⇄ companion (shape): a companion at the table as a
  participant (the Sagnaskemma kinship noted — the two tables'
  boundary written: Samtal's engine vs Ember's room).
- **E-160** VTT budgets + platform truth (which machines run the
  Godot client; the toaster verdict stated).
- **E-161** CHATDOLL codex reconciled (E-008 executed): its ask ×
  the tree — closed-with-evidence / absorbed (slices named) /
  retired-by-verdict.
- **E-162** WAIFU codex reconciled, likewise.
- **E-163** HERMES codex reconciled, likewise (its Hermes asks
  re-pointed at the refreshed fork where they belong there).
- **E-164** SUPER_AGENT_PARTY codex reconciled, likewise (the crew
  instinct vs the single-companion shape — the verdict argued from
  the project's "for normal folks" law).
- **E-165** RAGNAROK codex reconciled, likewise.
- **E-166** Absorbed-codex slices executed I (the highest-value
  absorption from E-161–165, built + tested).
- **E-167** Absorbed-codex slices executed II.
- **E-168** Absorbed-codex slices executed III (any remainder is
  re-roaded in the state file with owners, not dropped).
- **E-169** The codices' closing doc: each commission's fate +
  evidence, filed where a future reader finds it (the codex files
  themselves are elder text — untouched; the closing doc answers
  them).
- **E-170** VTT remainder roaded (if E-158 found real gaps): slices
  in the state file, in order.
- **E-171** VTT ⇄ Hamr (if E-145's handshake proved cheap): faces
  at the table, minimal proof.
- **E-172** Table + memory: a game's state remembered by the
  companion between sessions (Part V's face).
- **E-173** Docs: the table for users (plain) + builders.
- **E-174** Part X gate: five codices reconciled on record; VTT's
  truth table published; absorptions landed or roaded.

## Part XI — Stewardship: the Vendored & the Ancient (E-175 – E-186)

*Goal: the members Ember holds in trust — CloakBrowser and the
dictionary's data — kept lawful, current-by-verdict, and safe.*

- **E-175** CloakBrowser stewardship audit: version, licence file
  intact, upstream state (from public sources), our wrapper surface.
- **E-176** The wrapper contract: how Ember code touches the
  vendored browser (through its own interfaces only) — violations
  in our code fixed in scope.
- **E-177** Update verdict: refresh the vendored copy or hold —
  argued from upstream's changes + our wrapper's needs; a refresh
  lands as a wholesale verified swap, never a hand-merge.
- **E-178** Browser safety for normal folks: what the companion may
  do with a browser at all (permissions ladder; nothing silent).
- **E-179** Browser budgets: the vendored browser's cost per
  profile; profiles that cannot carry it say so in the book.
- **E-180** Dictionary stewardship: the cleasby-vigfusson data's
  integrity check (counts, checksums where the source offers them).
- **E-181** Deploy member mapped: `deploy/`'s shapes audited
  against the no-Docker law (any container-shaped path is refused
  + replaced with the native shape or roaded).
- **E-182** Native deploy recipes: systemd-shaped (Linux) + the
  honest equivalents per platform the house uses.
- **E-183** The update channel: signed, user-invited updates
  (E-052's costs consumed) — no silent auto-anything.
- **E-184** Telemetry refusal, proven: packet-level check that the
  companion phones nothing home by default.
- **E-185** Licence estate final: every member's licence in one
  table (the release ships it).
- **E-186** Part XI gate: vendored estate lawful + verified; deploy
  native-only; the refusal proven; summary filed.

## Part XII — Hardening, the Stranger Test & the Release Truth (E-187 – E-204)

*Goal: Ember finished honestly — secured, proven by strangers'
hands, and released with its truth table attached.*

- **E-187** Security audit, whole monorepo (cores, bridges,
  Kista, service surfaces) — findings fixed or roaded with owners.
- **E-188** Privacy audit (E-184 completed for every mode).
- **E-189** The Stranger Test I: a non-technical script-persona
  does the ten common acts (install, chat, remember, forget,
  change persona, cut a bridge, export memory…) unaided; failures
  are defects, fixed in scope.
- **E-190** The Stranger Test II: the toaster-profile edition.
- **E-191** Endurance soak: the companion alive a week-shaped
  simulation on the pi profile (memory, storage, nerves healthy).
- **E-192** Upgrade path: pre-campaign installs migrate (stores,
  vaults, configs), fixture-proven.
- **E-193** Docs I (users): the companion book — plain language,
  every common act, the budgets in human terms.
- **E-194** Docs II (builders): architecture reconciled (core,
  Verdandi, memory, bridges), recipes per member.
- **E-195** README care: root + member READMEs extended **by hand**
  where the campaign's truth belongs; all existing text preserved.
- **E-196** ORIGINS extended: the campaign's own provenance rows
  added to the register (new members/changes, scribed truthfully).
- **E-197** The claims audit: every public claim (sizes, speeds,
  "runs anywhere") matched to a measurement or struck in the audit.
- **E-198** Release shaping: version + truthful changelog by part
  (proven / partial / NOT PROVEN, per profile).
- **E-199** The showcase: the companion living on the smallest
  proven machine, a narrated session published (transcript +
  budgets).
- **E-200** Regression armour review: every gate (budgets, suites,
  drills, stranger scripts) runs as one command.
- **E-201** Roadmap audit: every E-slice DONE with evidence,
  PARTIAL with its road, or NOT PROVEN with its reason.
- **E-202** Retrospective: lessons to the workshop ledger; patterns
  named as skills where earned.
- **E-203** Push review: the campaign's banked stack presented for
  Volmarr's push word as one verified set (heads, counts, truth
  table).
- **E-204** Final report to Volmarr: plain language first — what
  Ember now provably is, per machine size, and what remains NOT
  PROVEN — evidence index attached.

---

## 5. Order and dependencies

Part I before everything (verdicts may re-cut the road; changes
recorded at E-018). Part III's budgets start early and bind
everything after. Part II next (members bind to the core). IV and
V beside II (nerves and memory are the core's organs). VI early
(custody gates configs everywhere). VII–VIII as their consumers
ripen. IX after II (personae) and at Blender's availability. X
after I's census + IX's handshake study. XI's audits can run
beside anything; its verdicts land when reached. XII closes.
Retirements and removals anywhere are Volmarr's word (verdicts are
prepared, never executed silently) — the campaign builds, proves,
and proposes; he disposes.

## 6. What this roadmap deliberately does not do

- No merging of the two Kistas by fiat — their boundary is a fact
  to document and (only if E-099 proves it wise) a bridge to build,
  never a confusion to paper over.
- No rewriting of vendored code; no relicensing of anything.
- No Docker, anywhere, for anything — deploy is native or it is
  roaded as unbuilt.
- No silent removals: ORIGINS' members leave only by Volmarr's
  word on a prepared verdict.
- No claims beyond measurements: "runs on your smart toaster" is
  a verdict earned at E-049, graded by the device it ran on.

## 7. First steps when the word is given

1. File this roadmap into the repo under `docs/`, extending —
   never overwriting — what stands there (filing push only).
2. Open the campaign: state file + the 10-minute keeper (house
   law).
3. Part I's audit runs before any building: a monorepo this
   storied is read before it is touched.

*Carved 2026-10-30, at Volmarr's word, by Yrsa.*

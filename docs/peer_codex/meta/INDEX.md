---
codex_id: INDEX
title: The Peer Codex — Entry Point (Wave 2)
role: Scribe
layer: Meta
peer_targets: [Letta, smolagents, Goose]
status: complete
peer_source_refs: []
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
hermes_codex_refs: [meta/INDEX, meta/MANIFEST]
cross_refs:
  - meta/SHARED_CONTEXT
  - meta/MANIFEST
  - meta/READING_ORDER
  - meta/PEER_REVISIONS
  - meta/STYLE_GUIDE_DELTA
  - meta/CONTINUATION_BACKLOG
  - meta/CROSS_AGENT_NOTES
  - meta/WAVE_ARC_OVERVIEW
  - 00_vision/CROSS_TRIANGULATION
  - 00_vision/CROSS_VISION_REFINED
  - 60_synthesis/CROSS_MIGRATION_PLAN_V2
  - 60_synthesis/CROSS_INTEGRATION_PATHS_V2
  - 60_synthesis/CROSS_DECISION_RECORDS_V2
---

# The Peer Codex

*The second doorway. If you have already walked through the Hermes Codex and want to know what three more codebases teach, you are in the right room. If you have not, walk through the [[hermes_codex/meta/INDEX]] first — Wave 2 builds on Wave 1.*

---

## Overture

The Peer Codex is the **second wave** of Ember's research arc. Where the Hermes Codex (fifty-three documents, one source) read a single sovereign agent end-to-end and triangulated against Ember's Vows, the Peer Codex reads **three more agents in parallel** — Letta, smolagents, and Goose — and triangulates against both Ember *and* Hermes. The shape changes: where Wave 1 asked *"what does Hermes teach?"*, Wave 2 asks *"what does each peer teach that Hermes did not, and what does each refuse to teach that Hermes overdid?"*. A triangle is the smallest polygon that names a direction; three peers plus Ember plus Hermes form four points, and the centroid of those four is, in our view, the actual shape of *capable small-to-medium agent design at 2026*.

The Peer Codex is not a survey. A survey is *here are five frameworks, here are their features in a table*. The Peer Codex reads source — `letta/agent.py`, `src/smolagents/agents.py`, `crates/goose/src/agents/agent.rs` — with Ember's Six True Names and Ten Vows held side by side, and it asks of every pattern: *which True Name would own this in Ember? Which Vow does it engage, strain, or violate? What would it cost to adopt?* Where Wave 1 produced a single body of findings against Hermes, Wave 2 produces three bodies of findings plus a **cross-comparison layer** that triangulates across all four codebases. The cross-comparison docs (`CROSS_*`) are where the centroid is named.

The work the Peer Codex is *not*: it is not a benchmark, not a recommendation to switch frameworks, not a paraphrase of any peer's README, not a roast, not a manifesto. The work it *is*: a long, careful, source-grounded reading of three peers, with line-number citations, with explicit links back to the Hermes Codex, with `## What This Means for Ember` closings that name the True Name and the Vow and the next step. Sixteen months from now, a contributor will ask: *"why did Ember adopt Letta-style memory tools but not Goose-style sessions? Was it considered?"* The answer is here, with citations, and with the SHAs of the source trees we read against. That is the job: long memory, verifiable, decision-ready.

---

## The Three Peers

### Letta — *the memory architects*

Letta (formerly MemGPT, descended from the Berkeley research line) is a **memory-centric agent framework** with a server-first deployment shape. Its central design move is to make memory *agent-callable*: the agent itself has tools to read, write, append to, and reorganise its own memory blocks (`core_memory`, `archival_memory`, `recall_memory`), with the *Manager* service layer enforcing schema and persistence. The library at this pin is 878 Python files / 248k lines, Apache-2.0, with PostgreSQL + SQLite + pgvector storage, REST API, and a generated SDK via `fern/`. Letta's posture is "memory is the first-class object; the agent is the loop that operates on it." For Ember's **Brunnr** (well) and **Smiðja** (forge), Letta is the single most relevant peer. See [[10_domain/LETTA_DOMAIN_MAP]], [[10_domain/LETTA_MEMORY_ARCHITECTURE]], [[30_execution/LETTA_AGENT_LOOP]].

### smolagents — *the minimalists*

smolagents (Hugging Face) is a deliberately small agent library: 75 Python files, ~31k lines, Apache-2.0, at this pin 921 commits past `v1.0.0`. Its central design moves are *code-execution-as-action* (the `CodeAgent` writes Python code as its tool-call surface; the executor runs it locally or in an E2B sandbox) and *minimalism as discipline* — every feature has to argue for its existence. For Ember's first Vow, **Smallness**, smolagents is the proof-of-existence: a capable agent can fit in 14k production lines. For Ember's **Funi** (flame) and **Munnr** (mouth), smolagents shows what a library — rather than a sovereign system — looks like. See [[10_domain/SMOL_DOMAIN_MAP]], [[10_domain/SMOL_CODE_EXECUTION_CORE]], [[30_execution/SMOL_MINIMALISM_LESSONS]].

### Goose — *the local-first cross-platform shippers*

Goose (Block) is a **local-first agent** with a fat Rust core and an Electron + React desktop UI. Goose was an early MCP adopter; the `Extensions` abstraction is roughly an MCP server, the `Recipes` abstraction is a declarative agent config, and `Sessions` are persistent runs. At this pin Goose is 433 Rust files + 1,113 TS/TSX files, ~370k lines total, Apache-2.0, mid-`v2.0-rc` cycle. The desktop shipping story is first-class — macOS / Windows / Linux builds — and the safety surface is actively contested (the pinned commit is a prompt-injection mitigation tweak). For Ember's **Strengr** (cord), **Munnr** (mouth), and the realm of cross-platform deployment, Goose is the closest production-grade analogue Wave 2 sees. See [[10_domain/GOOSE_DOMAIN_MAP]], [[10_domain/GOOSE_RECIPES_EXTENSIONS_SESSIONS]], [[10_domain/GOOSE_CROSS_LANGUAGE]].

---

## The Six Authors and What They Wrote

The Peer Codex is authored by the same six Mythic Engineering specialists who wrote the Hermes Codex — same voices, same questions, same closing-section discipline. The change in Wave 2 is *triangulation*: every author writes per-peer docs *and* cross-comparison docs, and the cross-comparison docs are weight-bearing in a way they were not in Wave 1.

| Role | Persona | Wave-2 layer & doc count | What changes from Wave 1 |
|---|---|---|---|
| **Skald** | Sigrún Ljósbrá | `00_vision/` — 6 docs | Vision splits into three peer-essence docs + three CROSS docs; the synthesis lands later than before. |
| **Architect** | Rúnhild Svartdóttir | `10_domain/` — 10 docs | Domain maps three trees; `CROSS_DOMAIN_TRIANGULATION` is the new keystone. |
| **Cartographer** | Védis Eikleið | `20_interface/` (4) + `60_synthesis/` (7) — 11 docs | Interface tracing across three protocols; full crosswalk per peer; integration paths multiply. |
| **Forge** | Eldra Járnsdóttir | `30_execution/` — 10 docs | Loop comparison and pattern-lifting now four-way (Hermes + 3 peers). |
| **Auditor** | Sólrún Hvítmynd | `20_interface/` (4) + `50_verification/` (8) — 12 docs | Per-peer risk registers; cross-risk triangulation; invariants list "V2". |
| **Scribe** | Eirwyn Rúnblóm | `meta/` — 7 docs *(this layer)* | New: `STYLE_GUIDE_DELTA`, `WAVE_ARC_OVERVIEW`. PEER_REVISIONS replaces HERMES_REVISION. |

**Total target:** approximately 54 docs (vs Hermes's 58). The authoritative list lives in [[meta/MANIFEST]]; when this index and the manifest disagree, the manifest wins.

---

## How to Read by Reader-Goal

The full reading paths are in [[meta/READING_ORDER]]. The quick-start summary:

- **"I'm here for the vision"** — [[00_vision/CROSS_TRIANGULATION]] → [[00_vision/CROSS_VISION_REFINED]] → the three `LETTA_ESSENCE` / `SMOL_ESSENCE` / `GOOSE_ESSENCE`. ~90 minutes.
- **"Show me the bones"** — [[10_domain/CROSS_DOMAIN_TRIANGULATION]] → the three `*_DOMAIN_MAP` docs → [[10_domain/CROSS_BOUNDARY_LAW_V2]]. ~3 hours.
- **"Show me the lift-able code"** — [[30_execution/CROSS_EXECUTION_PATTERNS_LIFT]] → [[60_synthesis/CROSS_INTEGRATION_PATHS_V2]] → the three crosswalks. ~4 hours.
- **"Show me the risks"** — [[50_verification/CROSS_RISK_TRIANGULATION]] → the three per-peer risk registers → [[50_verification/CROSS_ANTIPATTERN_CATALOG_V2]]. ~2.5 hours.
- **"I want the integration plan"** — [[60_synthesis/CROSS_TRUE_NAME_PROPOSALS_V2]] → [[60_synthesis/CROSS_INTEGRATION_PATHS_V2]] → [[60_synthesis/CROSS_MIGRATION_PLAN_V2]] → [[60_synthesis/CROSS_DECISION_RECORDS_V2]]. ~3 hours.
- **"I'm comparing all 4 codebases"** — the cross-comparison spine: [[00_vision/CROSS_TRIANGULATION]] → [[10_domain/CROSS_DOMAIN_TRIANGULATION]] → [[20_interface/CROSS_TOOL_PROTOCOL_TRIANGULATION]] → [[30_execution/CROSS_AGENT_LOOP_TRIANGULATION]] → [[50_verification/CROSS_RISK_TRIANGULATION]] → [[60_synthesis/CROSS_INTEGRATION_PATHS_V2]]. ~5 hours. **This is Wave-2-specific** and the path a future synthesis author should walk first.

---

## The True Names Touched

Each True Name's one-line Wave-2 lesson. Full treatment lives in [[60_synthesis/CROSS_TRUE_NAME_PROPOSALS_V2]]. Placeholders below will be replaced with concrete citations once the per-peer docs land — those citations are *promises*, not guesses.

- **Brunnr** — *well, the storage* — Wave 2's most concentrated lesson. Letta proves that a Manager-mediated, schema-strict, multi-block memory store is buildable in pure Python over PostgreSQL/SQLite/pgvector. smolagents proves that an agent can run *without* a Well at all (it has no persistent memory by default), which is the contrapositive lesson — memory must be earned, not assumed. Goose proves Sessions are the right granularity for "what was this conversation about". See [[10_domain/LETTA_MEMORY_ARCHITECTURE]], [[60_synthesis/CROSSWALK_LETTA_TO_EMBER]].
- **Funi** — *flame, the local LLM* — None of the three peers ships a local-model runtime. smolagents speaks to multiple model backends through a thin abstraction; Letta is provider-shaped; Goose treats the model as an external service it dispatches to. The lesson for Funi is in the *absence* — the Wave-2 peers do not solve the Pi-5 case any more than Hermes did. See [[00_vision/CROSS_ANTI_PEERS]].
- **Hjarta** — *heart, the first-run rite* — Goose's `goose configure` (`crates/goose-cli/src/commands/configure.rs`, 2,140 lines) is the most Hjarta-shaped first-run rite in Wave 2: opinionated, interactive, multi-step. Letta's first-run is server-shaped (`compose.yaml`). smolagents has effectively no first-run rite. See [[10_domain/GOOSE_DOMAIN_MAP]].
- **Munnr** — *mouth, the CLI* — Goose's CLI is the closest peer to Hermes's TUI in ambition; smolagents has no CLI to speak of; Letta's CLI is server-administration-shaped. The Wave-2 lesson for Munnr is the *shape of a Recipe-aware CLI* — Goose's `recipe` subcommand makes declarative agent configs first-class at the prompt. See [[10_domain/GOOSE_RECIPES_EXTENSIONS_SESSIONS]].
- **Smiðja** — *forge, ingest* — None of the three peers has a procedural-skill-creation loop matching Hermes's. Letta has *memory operations* (the agent can edit its own core memory) which is a different lesson; smolagents has *code-as-action* (the agent's "skill" is the code it writes) which is the same lesson in a different shape; Goose has *Recipes* which are skills authored *by humans* and consumed by agents. The Wave-2 lesson for Smiðja is that *three peers all touch this and none nail it* — the design space is open. See [[30_execution/SMOL_CODE_AS_ACTION]], [[30_execution/GOOSE_RECIPE_AUTHORING]].
- **Strengr** — *cord, the tether* — Goose's MCP-native posture is the Wave-2 reference for Strengr. MCP is the wire; Extensions are the adapters; the cross-language IPC between the Rust core and the desktop TS UI is a second tether worth studying. Letta's REST API is a different shape of tether — server-shaped, client-many. smolagents barely has a tether. See [[10_domain/GOOSE_CROSS_LANGUAGE]], [[20_interface/GOOSE_MCP_INTERFACE]].

---

## The Vows in Play

Each Vow, with the Wave-2 docs that engage it most directly. Some links are forward — that is intended; the Scribe sweeps unresolved links at wave close.

| Vow | Wave-2 docs that engage it most |
|---|---|
| **Smallness** | [[00_vision/SMOL_ESSENCE]], [[30_execution/SMOL_MINIMALISM_LESSONS]], [[50_verification/CROSS_EMBER_GAP_ANALYSIS_V2]] |
| **Tethered Grounding** | [[10_domain/LETTA_MEMORY_ARCHITECTURE]], [[10_domain/GOOSE_CROSS_LANGUAGE]], [[20_interface/CROSS_TOOL_PROTOCOL_TRIANGULATION]] |
| **Graceful Offline** | [[00_vision/GOOSE_ESSENCE]], [[50_verification/GOOSE_RISK_REGISTER]] |
| **Pluggable Storage** | [[10_domain/LETTA_MEMORY_ARCHITECTURE]], [[60_synthesis/CROSSWALK_LETTA_TO_EMBER]], [[10_domain/LETTA_SERVER_CLIENT_SPLIT]] |
| **Unbroken Whole** | [[meta/STYLE_GUIDE_DELTA]] — *enforced at the doc level by the style delta and at the corpus level by every author's discipline* |
| **Flexible Roots** | [[10_domain/GOOSE_DOMAIN_MAP]], [[30_execution/GOOSE_RUST_PATTERNS]], [[30_execution/CROSS_CROSS_PLATFORM_TACTICS_V2]] |
| **Public-Friendliness** | [[00_vision/GOOSE_ESSENCE]] (the desktop UX is the strongest Wave-2 example), [[10_domain/GOOSE_RECIPES_EXTENSIONS_SESSIONS]] |
| **Honest Memory** | [[10_domain/LETTA_MEMORY_ARCHITECTURE]], [[30_execution/LETTA_MEMORY_OPERATIONS]], [[50_verification/CROSS_INVARIANT_LIST_V2]] |
| **Modular Authorship** | [[10_domain/GOOSE_RECIPES_EXTENSIONS_SESSIONS]], [[20_interface/GOOSE_MCP_INTERFACE]], [[30_execution/GOOSE_RECIPE_AUTHORING]] |
| **Open Knowledge** | [[60_synthesis/CROSS_DECISION_RECORDS_V2]], [[meta/PEER_REVISIONS]] |

The *candidate* Vows (proposed in Wave 1, not yet ratified) — **Cache Discipline** and **Defended System Prompt** — both gain Wave-2 evidence. Goose's prompt-injection mitigations strengthen the case for *Defended System Prompt*; Letta's structured memory blocks plus its sandbox-IPC-hardening commit (the pinned commit) strengthen the case for an additional candidate Vow this wave may surface — *Trusted IPC*. See [[10_domain/CROSS_BOUNDARY_LAW_V2]].

The *candidate* True Names from Wave 1 — Listir, Verkfæri, Vegfarendr, Gjallarhorn, Vinátta — are revisited in [[60_synthesis/CROSS_TRUE_NAME_PROPOSALS_V2]]. Wave 2's tentative read: Verkfæri (tool-call discipline) and Gjallarhorn (the safety/alert surface) get *strengthened*; Listir, Vegfarendr, Vinátta remain interesting but unprovened by these three peers.

---

## Citations

The Peer Codex is grounded in three pinned clones. The pin lives at [[meta/PEER_REVISIONS]] and contains:

- Per-peer commit SHAs, tags, file counts by language, top-10 largest files, and reproduction commands.
- A short "why this pin matters" paragraph per peer.
- License information for each (all three: Apache-2.0).
- A summary table comparing all four codebases (Hermes + 3 peers) by lang, file count, line count, license, and posture.

**Citation form throughout the Codex (repo-relative, no `/tmp/` prefixes):**
- Letta: `letta/agent.py:280-320`
- smolagents: `src/smolagents/agents.py:412`
- Goose: `crates/goose/src/agents/agent.rs:88-152`

**Where peer sources live (canonical upstreams):**
- Letta: `https://github.com/letta-ai/letta` — Apache-2.0, © Letta-AI Inc.
- smolagents: `https://github.com/huggingface/smolagents` — Apache-2.0, © Hugging Face
- Goose: `https://github.com/block/goose` — Apache-2.0, © Block, Inc.

**License & attribution.** All three peers are Apache-2.0. The Codex itself lifts no peer code — only patterns and ideas. If a future wave or slice proposes lifting actual code from any peer, that requires a real ADR under `docs/decisions/` outside the Codex, with the NOTICE-file and patent-grant obligations of Apache-2.0 honoured. The Codex is the record of what was *considered*; the slice plan is the record of what was *lifted*.

---

## Maintenance Notes

The Scribe's conventions for the Peer Codex are the same as the Hermes Codex, with a small extension:

1. **One revision pin per peer per wave.** [[meta/PEER_REVISIONS]] holds three sections, one per peer, at this pin. When any peer is re-pinned, the *old pin block is preserved* as a `## Previous Pin` section; the new one appends above it.
2. **No silent rewrites.** A doc that materially changes between waves gets a `## Revision Log` block appended at the bottom.
3. **Cross-links are walked at wave close.** The Scribe runs through every `[[...]]` link and verifies it resolves. Broken links go to [[meta/CONTINUATION_BACKLOG]].
4. **The Manifest is authoritative.** Drift between this INDEX and the MANIFEST is resolved in the MANIFEST's favour.
5. **CROSS_ docs are weight-bearing.** A per-peer doc whose `CROSS_*` cross-comparison sibling is missing is half a doc. The continuation backlog should mark per-peer docs as `partial` if their CROSS sibling is `pending`.
6. **Style stays in one place.** Wave-1 conventions live in [[hermes_codex/meta/STYLE_GUIDE]]; Wave-2-specific deltas live in [[meta/STYLE_GUIDE_DELTA]]. When a new author joins mid-wave, they read the Wave-1 style guide first, then the delta.
7. **No paraphrased peers.** Every claim about a peer must point to a file path — exactly as in Wave 1.

### When this Codex becomes stale

The trigger to refresh the Peer Codex is *any* of:

- Any peer ships a release that materially changes the agent loop, the memory model, the tool / extension protocol, or the deployment shape — see [[meta/PEER_REVISIONS]] §5 for thresholds per peer.
- Ember ratifies a slice that adopts a peer-derived pattern (e.g. Letta-style memory tools, smolagents-style code-as-action, Goose-style Recipes). The Codex's synthesis docs are amended to reflect what was actually chosen.
- A new peer agent of comparable significance appears — at which point the choice is *expand Wave 2* or *open a Wave 7*. The Scribe consults the user.

### A note on Wave-2-specific maintenance hazards

Wave 2 has more cross-comparison surface than Wave 1 did. The hazard: a per-peer doc updates, but its cross-comparison sibling does not. The Scribe's discipline: at every wave close, walk the `CROSS_*` docs once *after* the per-peer docs are believed complete, and re-verify each citation.

---

## A Closing Note from the Scribe

The Peer Codex is large — fifty-four docs, four codebases, three teams of patterns to compare. The alternative — Ember's contributors re-deriving "is Letta-style memory a good fit?" or "is code-as-action small enough to honour Smallness?" each time the question arises — is much larger. The Codex is a sieve. We poured three more agents through it. What you read here is what was caught.

If you find the sieve missing a hole, leave a note in [[meta/CROSS_AGENT_NOTES]]. The next wave will widen the catch.

— *Eirwyn Rúnblóm, Scribe*

---

## What This Means for Ember

The INDEX does not propose a feature. It proposes a *practice*: that Ember's relationship to *any* large external codebase — Hermes, Letta, smolagents, Goose, the substrates of Wave 3, the papers of Wave 4 — be mediated by a maintained Codex rather than by ad-hoc reading. Wave 2 is the proof that the practice scales past a single source.

The True Names this affects are all of them, because the Codex is the long memory that holds the True Names accountable. The Vows most directly engaged are **Smallness** (the Codex is the only way a contributor can quickly find out which peer patterns *would* violate Smallness without half-importing one), **Honest Memory** (the Codex itself is honest about *what* it pinned and *when*), **Modular Authorship** (each peer is read by all six roles, and each role's voice stays distinct), and **Open Knowledge** (attribution to Letta-AI, Hugging Face, and Block is preserved throughout).

The concrete proposal is operational: the Wave-2 cross-comparison spine ([[00_vision/CROSS_TRIANGULATION]] → [[10_domain/CROSS_DOMAIN_TRIANGULATION]] → [[20_interface/CROSS_TOOL_PROTOCOL_TRIANGULATION]] → [[30_execution/CROSS_AGENT_LOOP_TRIANGULATION]] → [[50_verification/CROSS_RISK_TRIANGULATION]] → [[60_synthesis/CROSS_INTEGRATION_PATHS_V2]]) is the path the eventual grand-synthesis author should walk first when assembling the Ember plan. The per-peer docs feed it; the cross-comparison docs *are* it.

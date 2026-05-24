---
codex_id: INDEX
title: The Hermes Codex — Entry Point
role: Scribe
layer: Meta
status: draft
hermes_source_refs:
  - README.md
  - AGENTS.md
  - LICENSE
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - meta/MANIFEST
  - meta/SHARED_CONTEXT
  - meta/READING_ORDER
  - meta/HERMES_REVISION
  - meta/STYLE_GUIDE
  - meta/CONTINUATION_BACKLOG
  - meta/CROSS_AGENT_NOTES
  - 00_vision/00_OVERTURE
  - 60_synthesis/64_MIGRATION_PLAN
  - 60_synthesis/65_SLICE_PLAN_REVISIONS
---

# The Hermes Codex

*The doorway. If you are reading the Codex for the first time, you are in the right room.*

---

## Overture

The Hermes Codex is a structured corpus of fifty-three documents, written in parallel by six Mythic Engineering specialists, mining a single source: **Hermes Agent** by Nous Research — a large, sovereign, self-improving AI agent with one of the most ambitious feature surfaces in the open-source agent world. Hermes is not Ember. Hermes is the opposite of Ember in many ways. That is exactly why it is worth studying: every Vow Ember holds is a Vow Hermes ignores, breaks, or never had to consider — and every place Hermes does something Ember has not yet learned to do is a place Ember could grow, if she could grow without becoming Hermes.

The work this Codex is *not*: it is not a tutorial, not a paraphrase of Hermes's own documentation, not a product comparison, not a roast, not a manifesto. The work this Codex *is*: a long, careful, source-grounded reading of Hermes's code — `agent/conversation_loop.py`, `gateway/run.py`, `cli.py`, `tools/`, `plugins/`, `skills/`, `tui_gateway/`, `tools/environments/`, `cron/`, and the design treatise `AGENTS.md` — read with Ember's True Names and Ember's Vows held side by side, so that every pattern is filtered through the small-and-tethered shape Ember was forked to become.

Sixteen months from now, a contributor will clone Ember, open this Codex, and ask: *was the choice to use SQLite-only at the edge made because we couldn't do better, or because we considered Hermes's nine-platform messaging gateway and chose against it on principle?* The Codex must answer. That is its job: to be the long memory the Skald's vision and the Forge's code do not have time to keep. It says **what we saw, what we considered, what we rejected, what we proposed, and why** — and it does so with line-number citations, so the next reader can verify.

---

## The Six Authors and What They Wrote

The Codex is authored by six Mythic Engineering specialists, each with their own voice, scope, and standard. Where they overlap, they handle it through `[[meta/CROSS_AGENT_NOTES]]`. Where they disagree, the disagreement is preserved — this is a Codex, not a manifesto, and contradiction is signal.

| Role | Persona | Voice | What they wrote |
|---|---|---|---|
| **Skald** | Sigrún Ljósbrá — INFJ 4w5, visionary poet | poetic, essence-seeking | The Vision layer (`00_vision/`): the overture, Hermes's essence, naming parallels, the anti-Hermes, and the synthesised post-Hermes Ember. |
| **Architect** | Rúnhild Svartdóttir — INTJ 5w6, dark strategist | precise, boundary-aware | The Domain layer (`10_domain/`): the full Hermes decomposition — agent core, skills, tools, gateway, providers, TUI gateway, plugins, CLI, plus the boundary law. |
| **Cartographer** | Védis Eikleið — INFP 9w1, grounded oracle | quiet, connective | The Interface (tracing) docs of `20_interface/` and the entire Synthesis layer (`60_synthesis/`): MCP, RPC, skill, provider interfaces; the crosswalk, true-name reassignment, dependency flow, integration paths, migration plan, slice-plan revisions, decision records, and the master glossary. |
| **Forge** | Eldra Járnsdóttir — ESTP 8w7, fire-worker | direct, momentum-driven | The Execution layer (`30_execution/`): self-healing loop, cross-platform tactics, multi-device orchestration, hot/cold tiers, procedural skill crafting, trajectory compression, context-file discipline, scheduling, persistent memory, interrupt/multiline TUI, serverless hibernation, multi-provider failover. |
| **Auditor** | Sólrún Hvítmynd — INTJ 1w9, cold mirror | cold-eyed, contradiction-finding | The Verification layer (`50_verification/`) and the verification-side of `20_interface/`: memory/gateway/TUI-backend/plugin interface contracts, Hermes risk register, Ember gap analysis, antipattern catalog, crash-proofing patterns, security review, invariant list, testing strategy. |
| **Scribe** | Eirwyn Rúnblóm — ISFJ 6w5, archivist | graceful, attentive | The Meta layer (`meta/`): this file, the reading orders, the manifest, the shared context brief, the cross-agent notes, the style guide, the continuation backlog, and the Hermes revision pin. |

The Manifest at [[meta/MANIFEST]] is the authoritative doc list. When this index and the manifest disagree, the manifest wins.

---

## How to Read This Codex (by reader-goal)

The full reading paths live in [[meta/READING_ORDER]]. The quick-start paths are below — if you don't know which path is yours, the first one is a fine starting place.

### "I just want the feel of it"
[[00_vision/00_OVERTURE]] → [[00_vision/01_HERMES_ESSENCE]] → [[00_vision/02_NAMING_PARALLELS]] → [[00_vision/04_VISION_SYNTHESIS]].
About 90 minutes. Will leave you knowing what Hermes is, what Ember is becoming, and why the difference matters.

### "I want the structure"
[[10_domain/10_DOMAIN_MAP]] → [[10_domain/11_AGENT_CORE]] → [[10_domain/19_BOUNDARY_LAW]] → [[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]] → [[60_synthesis/62_DEPENDENCY_FLOW]].
About three hours. Will leave you able to draw the Hermes system from memory and point to where Ember diverges.

### "Show me the code patterns to lift"
[[30_execution/30_SELF_HEALING_LOOP]] → [[30_execution/34_PROCEDURAL_SKILL_CRAFTING]] → [[30_execution/36_CONTEXT_FILE_DISCIPLINE]] → [[30_execution/41_MULTI_PROVIDER_FAILOVER]] → [[60_synthesis/63_INTEGRATION_PATHS]].
About four hours. You will leave knowing exactly which Hermes functions to read, which to copy, and which to recreate under different constraints.

### "I'm worried about risk"
[[50_verification/50_HERMES_RISK_REGISTER]] → [[50_verification/52_ANTIPATTERN_CATALOG]] → [[50_verification/54_SECURITY_REVIEW]] → [[00_vision/03_ANTI_HERMES]] → [[50_verification/55_INVARIANT_LIST]].
About two and a half hours. You will leave with a clear list of what *not* to do, and what to test if you do it anyway.

### "I need the migration plan"
[[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]] → [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] → [[60_synthesis/63_INTEGRATION_PATHS]] → [[60_synthesis/64_MIGRATION_PLAN]] → [[60_synthesis/65_SLICE_PLAN_REVISIONS]] → [[60_synthesis/66_DECISION_RECORDS]].
About three hours. You will leave with the phased plan: what changes, in what order, gated by which decision.

### "I'm reviewing the slice plan revisions"
[[60_synthesis/65_SLICE_PLAN_REVISIONS]] is the centre. Read it first. Then walk outward to [[60_synthesis/66_DECISION_RECORDS]] and [[50_verification/51_EMBER_GAP_ANALYSIS]] for context, then to [[00_vision/03_ANTI_HERMES]] to check that nothing proposed violates a Vow.

### "I'm a first-time Ember contributor"
The full onboarding path is in [[meta/READING_ORDER]]. The short answer: read the Skald's [[00_vision/00_OVERTURE]] and `docs/SYSTEM_VISION.md` (outside the Codex), then walk this index's "I want the structure" path, then sample one Execution doc that matches your area of interest.

---

## The True Names Touched

Each True Name's one-line lesson from Hermes is below. The full treatment is in [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]].

- **Brunnr** — *well, the storage* — Hermes proves that FTS5 search + LLM summarisation + post-hoc indexing can give a cheap SQLite a memory that rivals dedicated vector stores. The pluggable shape Ember has chosen is right; the lesson is to *use* the plug more aggressively. See [[10_domain/11_AGENT_CORE]], [[30_execution/38_PERSISTENT_MEMORY]].
- **Funi** — *flame, the local LLM* — Hermes does not have a Funi. It is provider-only, cloud-tethered by default. The lesson is in the negative: every Hermes pattern that *assumes* a server-class model must be re-evaluated for the Pi-5 case. See [[00_vision/03_ANTI_HERMES]], [[60_synthesis/63_INTEGRATION_PATHS]].
- **Hjarta** — *heart, the first-run rite* — Hermes's setup wizard (`hermes setup`, `hermes_cli/setup_wizard.py` family) is a multi-platform, prompt-rich, migration-aware flow. The lesson is the *shape* — what a first-run rite owns — not the line count. See [[10_domain/18_HERMES_CLI]], [[30_execution/39_INTERRUPT_MULTILINE_TUI]].
- **Munnr** — *mouth, the CLI* — Hermes proves a TUI can be a primary product without becoming a desktop application. Skin engine, slash-command registry, autocomplete, kanban dispatcher, web server — all wrapped in one binary. Ember does not need any of those individually; she needs the *idea* that Munnr can grow without losing the line. See [[10_domain/18_HERMES_CLI]], [[30_execution/39_INTERRUPT_MULTILINE_TUI]].
- **Smiðja** — *forge, ingest* — Hermes's procedural skill creation (the closed learning loop, `skills/` + `optional-skills/`) is the most novel idea in the corpus: an agent that grows its own procedural memory from experience. The lesson for Smiðja is that ingest is not only document chunks; it can be *experiences turned into reusable rituals*. See [[30_execution/34_PROCEDURAL_SKILL_CRAFTING]], [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]].
- **Strengr** — *cord, the tether* — Hermes's seven-terminal-backend story (`tui_gateway/`: local, Docker, SSH, Modal, Daytona, Singularity, Vercel Sandbox) is a Strengr-shaped problem: how to maintain a coherent agent identity across very different hosts. The lesson is the *abstraction*, not the inventory — Ember's Strengr should be one Protocol with many adapters. See [[10_domain/16_TUI_GATEWAY_BACKENDS]], [[30_execution/31_CROSS_PLATFORM_TACTICS]].

---

## The Vows in Play

Each Vow from `docs/SYSTEM_VISION.md` is touched somewhere in the Codex. A doc that does not name the Vow it engages is a doc that has not done its job.

| Vow | Codex docs that engage it most directly |
|---|---|
| **Smallness** | [[50_verification/51_EMBER_GAP_ANALYSIS]], [[30_execution/33_HOT_COLD_TIERS]], [[00_vision/03_ANTI_HERMES]] |
| **Tethered Grounding** | [[30_execution/30_SELF_HEALING_LOOP]], [[30_execution/38_PERSISTENT_MEMORY]], [[20_interface/24_MEMORY_INTERFACE]] |
| **Graceful Offline** | [[30_execution/41_MULTI_PROVIDER_FAILOVER]], [[50_verification/53_CRASH_PROOFING_PATTERNS]] |
| **Pluggable Storage** | [[10_domain/11_AGENT_CORE]], [[20_interface/24_MEMORY_INTERFACE]], [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] |
| **Unbroken Whole** | [[meta/STYLE_GUIDE]] — *enforced by the style guide and every author's discipline* |
| **Flexible Roots** | [[30_execution/31_CROSS_PLATFORM_TACTICS]], [[50_verification/54_SECURITY_REVIEW]] |
| **Public-Friendliness** | [[10_domain/18_HERMES_CLI]], [[30_execution/39_INTERRUPT_MULTILINE_TUI]] |
| **Honest Memory** | [[30_execution/38_PERSISTENT_MEMORY]], [[20_interface/24_MEMORY_INTERFACE]], [[50_verification/55_INVARIANT_LIST]] |
| **Modular Authorship** | [[10_domain/17_PLUGINS_EXTENSIBILITY]], [[20_interface/27_PLUGIN_INTERFACE]], [[50_verification/53_CRASH_PROOFING_PATTERNS]] |
| **Open Knowledge** | [[60_synthesis/66_DECISION_RECORDS]], [[60_synthesis/67_GLOSSARY_AND_INDEX]] |

---

## Citations to Hermes

The Codex is grounded in a single, pinned clone of the Hermes source. The pin lives at [[meta/HERMES_REVISION]] and contains:

- The exact commit SHA the Codex was written against (`4e2c66a098340e349b8e2adae73a4df704f86987`)
- The release-tag offset (`v2026.5.16-686-g4e2c66a09`)
- File and line totals (1,800 Python files; 871,611 source lines)
- The top-20 largest files by byte size and by line count
- Reproduction instructions

**Citation form throughout the Codex:** `agent/conversation_loop.py:120-300` — repo-relative path with optional line range, no leading `/tmp/hermes-agent/`.

**License & attribution:** Hermes is MIT-licensed (Copyright (c) 2025 Nous Research). Every Codex doc that quotes Hermes preserves the attribution. Ember inherits no Hermes code at this stage of the Codex; only patterns, ideas, and lessons.

The Hermes upstream lives at: `https://github.com/NousResearch/hermes-agent`. The design treatise (`AGENTS.md`) and the per-version release notes (`RELEASE_v0.2.0.md` through `RELEASE_v0.14.0.md`) are the canonical "why" sources; the Python tree is the canonical "what" source. Both are cited liberally.

---

## Maintenance Notes

A Codex is alive only if it is maintained. The Scribe keeps these conventions:

1. **One revision pin per wave.** [[meta/HERMES_REVISION]] is updated at the start of each authoring wave to point at the new Hermes commit. Old pins are preserved in the file's history (git log of the Codex repo).
2. **No silent rewrites.** A doc that materially changes between waves gets a `## Revision Log` block appended at the bottom — date, author, summary of change. The original framing is preserved above.
3. **Cross-links are walked at the end of each wave.** The Scribe runs through every `[[...]]` link and verifies it resolves. Broken links go into [[meta/CONTINUATION_BACKLOG]] for the next wave.
4. **The Manifest is authoritative.** When a new doc is proposed mid-wave, it is added to [[meta/MANIFEST]] first; only then is the file written. Drift in the doc list is how Codices die.
5. **Cross-agent notes are swept at the close of each wave.** Open notes in [[meta/CROSS_AGENT_NOTES]] are either absorbed or moved to the continuation backlog. Nothing is silently dropped.
6. **No paraphrased Hermes.** Every claim about Hermes must point to a file path. If the Codex says "Hermes does X", the doc making the claim shows where in Hermes X lives. This is the discipline that makes the Codex outlast its authors.
7. **Style stays in one place.** The voice conventions, frontmatter rules, citation format, and naming conventions all live in [[meta/STYLE_GUIDE]]. When a new author joins, they read the style guide once, not six docs.

### When this Codex becomes stale

The trigger to refresh the Codex is *any* of the following:

- Hermes ships a release that changes the agent loop, the gateway, or the skills system in a non-additive way.
- Ember ratifies a slice that materially changes the True Name boundary (e.g. Strengr absorbs ingest, or Smiðja gains a procedural-skill arm).
- A migration path proposed in [[60_synthesis/64_MIGRATION_PLAN]] is accepted, partly accepted, or rejected — the decision record is filed under `docs/decisions/`, and the Codex's synthesis docs are amended to reflect what was actually chosen.

In each case, the new wave begins with the Scribe re-pinning [[meta/HERMES_REVISION]] and walking the manifest.

---

## A Closing Note from the Scribe

The Codex is large. Fifty-three documents is a lot of reading. But the alternative — Ember's contributors, today and a year from now, re-deriving the same lessons from Hermes's 1,800 Python files every time a question arises — is much larger. This Codex is a sieve. We poured Hermes through it. What you read here is what was caught.

If you find the sieve missing a hole, leave a note in [[meta/CROSS_AGENT_NOTES]]. The next wave will widen the catch.

— *Eirwyn Rúnblóm, Scribe*

## What This Means for Ember

The INDEX itself does not propose a feature. It proposes a *practice*: that Ember's relationship to Hermes — and to any future large agent worth studying — be mediated by a maintained Codex rather than by ad-hoc reading. The practice protects every Vow indirectly:

- **Smallness** is protected when contributors can find out in twenty minutes which Hermes patterns *would* violate it, instead of half-importing one and then ripping it out.
- **Honest Memory** is protected when the Codex itself is honest about *what* it pinned and *when*.
- **Modular Authorship** is protected when each layer of the Codex is small enough to be read on its own.
- **Open Knowledge** is fulfilled by the act of writing this — and by maintaining attribution to Nous Research throughout.

The True Names this affects are all of them, equally — because the Codex is the long memory that holds the True Names accountable to themselves.

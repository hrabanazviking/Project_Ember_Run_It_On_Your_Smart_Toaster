---
codex_id: READING_ORDER
title: Reading Orders — Paths Through the Codex by Reader Goal
role: Scribe
layer: Meta
status: draft
hermes_source_refs:
  - README.md
  - AGENTS.md
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - meta/INDEX
  - meta/MANIFEST
  - meta/STYLE_GUIDE
  - 00_vision/00_OVERTURE
  - 10_domain/10_DOMAIN_MAP
  - 30_execution/30_SELF_HEALING_LOOP
  - 50_verification/50_HERMES_RISK_REGISTER
  - 60_synthesis/64_MIGRATION_PLAN
  - 60_synthesis/65_SLICE_PLAN_REVISIONS
---

# Reading Orders

*Different readers come to the Codex with different questions. This file describes the paths.*

The Codex is fifty-three documents. No one reads fifty-three documents cover to cover. The Scribe's job is to lay paths through the corpus so that *the right ten or fifteen* are read in the right order for each kind of reader. Below are seven such paths, each with: the ordered sequence of docs, the reason each doc sits in that position, an honest reading-time estimate, and the key questions the path answers.

Reading times assume:
- An attentive reader on a screen, not skim-mode.
- The reader pauses to follow at least one or two cross-links per doc.
- Each Codex doc is roughly 2,000–3,000 words (15–25 minutes of careful reading).
- A reader who is also opening `/tmp/hermes-agent/` and reading source alongside should double the estimate.

If you are reading the Codex on paper or printout, double again.

---

## Path 1 — "I'm just here to feel the vision" (Skald path)

For: a stranger to Ember, a sceptic, a sibling-project author, a contributor who wants to know *why* before *how*.

| # | Doc | Why here | Time |
|---|---|---|---|
| 1 | [[meta/INDEX]] | The doorway. Sets expectations, names the layers, points to all paths. | 15 min |
| 2 | `docs/SYSTEM_VISION.md` (outside Codex) | The Skald's living vision for Ember. The Codex was written against this. | 30 min |
| 3 | [[00_vision/00_OVERTURE]] | What the Codex is, in Skald-voice — sets the emotional and conceptual stage. | 25 min |
| 4 | [[00_vision/01_HERMES_ESSENCE]] | Hermes stripped to bones — what Hermes *wants to be* before features. | 25 min |
| 5 | [[00_vision/02_NAMING_PARALLELS]] | The bridge: which Hermes concept maps to which True Name. | 25 min |
| 6 | [[00_vision/03_ANTI_HERMES]] | What Ember must refuse — the patterns the Vows forbid. | 25 min |
| 7 | [[00_vision/04_VISION_SYNTHESIS]] | Post-Hermes Ember: who she becomes after this Codex is absorbed. | 30 min |

**Total: ~2.5 hours.**

**Questions this path answers:**
- What is Ember, in one sentence?
- What is Hermes, in one sentence?
- Why are they different on purpose?
- Which Hermes ideas does Ember want, and which does she refuse?
- What does the world look like after Ember has absorbed the worthwhile lessons?

**You leave knowing:** the framing well enough to argue for Ember's small-and-tethered shape in any room, including rooms full of larger-agent advocates.

**You do not leave knowing:** the code patterns, the risks, or the migration plan. Those paths follow.

---

## Path 2 — "I'm an architect — I want the structure" (Architect path)

For: a contributor designing a new subsystem, a reviewer of a slice plan, a sibling-project architect who wants to understand Ember's decomposition by contrast with Hermes's.

| # | Doc | Why here | Time |
|---|---|---|---|
| 1 | [[meta/INDEX]] | Orientation; pointer to the Manifest. | 15 min |
| 2 | [[meta/MANIFEST]] | Authoritative doc list. Read once, refer back many times. | 15 min |
| 3 | [[00_vision/02_NAMING_PARALLELS]] | The Hermes-to-True-Name map. Read this *before* the domain layer so you know what to look for. | 25 min |
| 4 | [[10_domain/10_DOMAIN_MAP]] | The big-picture decomposition of Hermes. | 30 min |
| 5 | [[10_domain/11_AGENT_CORE]] | `agent/`: conversation loop, context engine, memory, prompts, dispatch. The heart of Hermes. | 35 min |
| 6 | [[10_domain/13_TOOLS_SUBSYSTEM]] | `tools/`, `toolsets.py`, `toolset_distributions.py` — how 40+ tools are organised. | 25 min |
| 7 | [[10_domain/14_GATEWAY_MULTI_PLATFORM]] | The biggest file in Hermes lives here (`gateway/run.py`, 18k lines). Read to understand how *not* to scope a gateway, and to understand the abstractions that make it tractable. | 30 min |
| 8 | [[10_domain/15_PROVIDERS_MULTI_MODEL]] | How 200+ models are abstracted behind a uniform interface. | 25 min |
| 9 | [[10_domain/17_PLUGINS_EXTENSIBILITY]] | The plugin contract. The shape Ember's Modular Authorship Vow wants. | 25 min |
| 10 | [[10_domain/19_BOUNDARY_LAW]] | Where Hermes's boundaries hold, where they leak — the architectural ethics. | 30 min |
| 11 | [[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]] | Concrete mapping: module-by-module. | 30 min |
| 12 | [[60_synthesis/62_DEPENDENCY_FLOW]] | The data flow drawn end-to-end. | 25 min |
| 13 | [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] | Proposed expansions/clarifications to the True Names based on what Hermes taught. | 30 min |

**Total: ~5.5 hours.**

**Questions this path answers:**
- How is Hermes decomposed, in detail?
- Where does Hermes's domain map line up with Ember's, and where does it diverge?
- What boundary failures does Hermes exhibit, and what do they cost?
- Are the six True Names still the right decomposition after seeing Hermes?
- Which Hermes subsystems would correspond to a Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr-shaped Ember evolution?

**You leave knowing:** Hermes's full architectural shape, and Ember's by contrast. You can defend (or revise) the True Name boundaries in any design review.

---

## Path 3 — "I'm an implementer — show me code patterns to lift" (Forge path)

For: a contributor about to write code in `src/ember/` who wants to know which Hermes patterns are worth borrowing and how.

| # | Doc | Why here | Time |
|---|---|---|---|
| 1 | [[meta/STYLE_GUIDE]] | The Codex's own conventions. Read before any other docs so the Forge layer's tone is parseable. | 15 min |
| 2 | [[10_domain/11_AGENT_CORE]] | Context for everything in `30_execution/` — you need to know what `agent/` is before reading what `agent/` *does*. | 35 min |
| 3 | [[30_execution/30_SELF_HEALING_LOOP]] | The closed learning loop. Hermes's signature feature. Worth understanding before deciding whether Smiðja absorbs it. | 35 min |
| 4 | [[30_execution/34_PROCEDURAL_SKILL_CRAFTING]] | How Hermes auto-creates skills from experience. Mechanism, not just framing. | 30 min |
| 5 | [[30_execution/38_PERSISTENT_MEMORY]] | FTS5 + LLM summarisation. Directly applicable to Brunnr. | 30 min |
| 6 | [[30_execution/36_CONTEXT_FILE_DISCIPLINE]] | Prompt-caching ergonomics. Applicable to Funi's prompt assembly. | 25 min |
| 7 | [[30_execution/39_INTERRUPT_MULTILINE_TUI]] | TUI patterns: interrupt-without-loss, multiline editing, slash completion. Directly applicable to Munnr. | 30 min |
| 8 | [[30_execution/41_MULTI_PROVIDER_FAILOVER]] | Provider failover, rate-limit handling, credential pool. Relevant if Funi grows a cloud-fallback arm. | 30 min |
| 9 | [[30_execution/53_CRASH_PROOFING_PATTERNS]] *(in 50_verification)* | Hermes patterns that survive partial failure. Read with the Forge head. | 30 min |
| 10 | [[60_synthesis/63_INTEGRATION_PATHS]] | Concrete paths to wire any of the above into Ember without violating Vows. | 35 min |
| 11 | [[60_synthesis/64_MIGRATION_PLAN]] | Phased plan: what's first, what's gated, what's reversible. | 30 min |

**Total: ~5.5 hours.**

**Questions this path answers:**
- Which exact Hermes functions are worth reading line-for-line?
- Which patterns have a one-to-one Ember translation, and which need redesign?
- What is the dependency order if I want to land them in Ember?
- What guardrails do I need (tests, invariants) before borrowing each?
- Where do I look in Hermes's code if I want to write the corresponding Ember version myself?

**You leave knowing:** the small set of Hermes files you'd open, the patterns you'd lift, the patterns you'd discard, and the order in which to land them.

---

## Path 4 — "I'm worried about risk and safety" (Auditor path)

For: a security-minded contributor, a reviewer concerned about scope creep, anyone reviewing a PR that proposes lifting a Hermes pattern.

| # | Doc | Why here | Time |
|---|---|---|---|
| 1 | [[00_vision/03_ANTI_HERMES]] | The Vow-violating patterns Hermes embodies. Set the moral compass first. | 25 min |
| 2 | [[50_verification/50_HERMES_RISK_REGISTER]] | What could go wrong with Hermes's patterns — operational, security, correctness. | 35 min |
| 3 | [[50_verification/52_ANTIPATTERN_CATALOG]] | The patterns Ember should NOT adopt, with reasons. | 30 min |
| 4 | [[50_verification/54_SECURITY_REVIEW]] | Multi-platform, MCP, credential-pool, container-isolation analysis. | 35 min |
| 5 | [[50_verification/51_EMBER_GAP_ANALYSIS]] | What Ember lacks vs. Hermes; what closing each gap would require. (Risk-side read: which gaps *should* stay open.) | 30 min |
| 6 | [[50_verification/53_CRASH_PROOFING_PATTERNS]] | Hermes patterns that *survive* partial failure — the ones worth keeping. | 30 min |
| 7 | [[50_verification/55_INVARIANT_LIST]] | Invariants Ember must maintain when borrowing Hermes ideas. | 25 min |
| 8 | [[50_verification/56_TESTING_STRATEGY]] | How to verify each Hermes-inspired feature. | 30 min |
| 9 | [[20_interface/24_MEMORY_INTERFACE]] | Auditor-side memory contract — the surface where Honest Memory is enforced. | 25 min |
| 10 | [[20_interface/25_GATEWAY_INTERFACE]] | The contract behind a multi-platform messaging surface; what hooks should be hardened. | 25 min |
| 11 | [[20_interface/27_PLUGIN_INTERFACE]] | Plugin contract. Where Modular Authorship lives or dies. | 25 min |

**Total: ~5 hours.**

**Questions this path answers:**
- What can go wrong with each pattern in Hermes if Ember imports it naively?
- Which Hermes features are security-critical, and what hardening does each require?
- Which invariants must hold for Ember to keep her Vows after each adoption?
- What testing is sufficient — and what *would not* be sufficient — to verify each lift?
- Where in the interface contracts is the line between "Ember keeps her shape" and "Ember became Hermes"?

**You leave knowing:** a complete checklist for reviewing any PR that proposes Hermes-inspired code, and the criteria for vetoing a proposal that would violate a Vow.

---

## Path 5 — "I want the migration plan" (Cartographer-synthesis path)

For: a planner, a roadmap contributor, anyone preparing a multi-slice proposal that touches several True Names.

| # | Doc | Why here | Time |
|---|---|---|---|
| 1 | [[meta/INDEX]] + [[meta/MANIFEST]] | The overall shape. | 30 min |
| 2 | [[00_vision/04_VISION_SYNTHESIS]] | Where the synthesis is *aimed* — the post-Hermes Ember the migration is moving toward. | 30 min |
| 3 | [[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]] | Module-by-module: where each True Name sits today, where Hermes shows it could grow. | 30 min |
| 4 | [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] | The proposed name-and-boundary adjustments. The plan needs this settled before sequencing. | 30 min |
| 5 | [[60_synthesis/62_DEPENDENCY_FLOW]] | The data flow as it will be after migration. Confirms sequencing constraints. | 30 min |
| 6 | [[50_verification/51_EMBER_GAP_ANALYSIS]] | What's missing and what each gap costs. The migration prioritises by gap-cost ratio. | 30 min |
| 7 | [[60_synthesis/63_INTEGRATION_PATHS]] | The concrete how-to for each lift. | 35 min |
| 8 | [[60_synthesis/64_MIGRATION_PLAN]] | The phased, gated, reversible plan itself. | 40 min |
| 9 | [[60_synthesis/65_SLICE_PLAN_REVISIONS]] | Proposed revisions to the ratification-gated slice plan. | 30 min |
| 10 | [[60_synthesis/66_DECISION_RECORDS]] | ADR-style records for the consequential decisions. | 30 min |
| 11 | [[60_synthesis/67_GLOSSARY_AND_INDEX]] | The master vocabulary — keep this open while planning to avoid term drift. | 20 min |

**Total: ~5.5 hours.**

**Questions this path answers:**
- What is the synthesised target Ember the plan is moving toward?
- What gaps separate today's Ember from that target?
- In what order are the gaps best closed, given the Vows?
- Which slices are proposed, and how are they gated?
- What decisions need to be ratified before any of it can start?

**You leave knowing:** a complete, defensible migration narrative — what to propose, in what order, with what gates, and which Vow each step protects.

---

## Path 6 — "I'm reviewing the slice plan revisions" (decision-maker path)

For: Volmarr or a senior reviewer evaluating whether a Codex-proposed slice revision should be ratified.

| # | Doc | Why here | Time |
|---|---|---|---|
| 1 | [[60_synthesis/65_SLICE_PLAN_REVISIONS]] | The actual proposal. Read it first — everything else is context. | 40 min |
| 2 | The current slice plan (`docs/EMBER_FIRST_SLICE_PLAN.md` or successor) | The thing being revised. Read alongside the proposal. | 30 min |
| 3 | [[60_synthesis/66_DECISION_RECORDS]] | ADR-style backing for each consequential proposed change. | 30 min |
| 4 | [[50_verification/51_EMBER_GAP_ANALYSIS]] | What gap each proposed slice closes, and the cost of leaving it open. | 30 min |
| 5 | [[00_vision/03_ANTI_HERMES]] | The Vows in their sharpest form — check each proposal against them. | 25 min |
| 6 | [[50_verification/55_INVARIANT_LIST]] | The invariants any new slice must preserve. | 25 min |
| 7 | [[60_synthesis/64_MIGRATION_PLAN]] | The wider plan the proposed revision sits inside. | 30 min |
| 8 | [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] | If a proposal expands or contracts a True Name, this is where the justification lives. | 30 min |

**Total: ~4 hours.**

**Questions this path answers:**
- What exactly is being proposed?
- What gap does each proposal close?
- Does any proposal strain or break a Vow?
- Does any proposal violate a stated invariant?
- What ADR commitment is required to ratify?

**You leave knowing:** whether to ratify, partially ratify, or reject each proposed slice revision, with traceable reasons.

---

## Path 7 — "I'm a first-time Ember contributor" (full onboarding)

For: someone newly joining Ember who wants the complete grounded picture before opening a PR.

This path is intentionally generous. It is the path a contributor should walk *once*, over the course of a week or two. Other paths above are the ones they will return to.

### Day 1 — Vision and self-knowledge (~3 hours)
1. `docs/SYSTEM_VISION.md` (outside Codex) — the Skald's living vision
2. `PHILOSOPHY.md` (outside Codex) — the wyrd of the code
3. [[meta/INDEX]] — Codex entry point
4. [[00_vision/00_OVERTURE]]
5. [[00_vision/01_HERMES_ESSENCE]]

### Day 2 — Hermes in shape (~3 hours)
6. [[00_vision/02_NAMING_PARALLELS]]
7. [[10_domain/10_DOMAIN_MAP]]
8. [[10_domain/11_AGENT_CORE]]
9. [[10_domain/19_BOUNDARY_LAW]]

### Day 3 — How Hermes works at the edges (~3 hours)
10. Pick one or two from `10_domain/12`–`18` matching your area
11. [[30_execution/30_SELF_HEALING_LOOP]]
12. [[30_execution/38_PERSISTENT_MEMORY]]

### Day 4 — Risks and what to refuse (~3 hours)
13. [[00_vision/03_ANTI_HERMES]]
14. [[50_verification/50_HERMES_RISK_REGISTER]]
15. [[50_verification/52_ANTIPATTERN_CATALOG]]
16. [[50_verification/53_CRASH_PROOFING_PATTERNS]]

### Day 5 — Synthesis and direction (~3 hours)
17. [[00_vision/04_VISION_SYNTHESIS]]
18. [[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]]
19. [[60_synthesis/64_MIGRATION_PLAN]]
20. [[60_synthesis/65_SLICE_PLAN_REVISIONS]]

### Day 6+ — Depth in your area
By now you know which True Name your work touches. Walk the relevant Path 2, 3, or 4 above for that area; sample from [[60_synthesis/67_GLOSSARY_AND_INDEX]] when you hit unfamiliar vocabulary.

**Total: ~15 hours over a week.**

**Questions this path answers:**
- All of them, eventually.
- More importantly: which questions to keep asking after you've finished reading.

---

## How to Choose a Path

| If your most pressing question is… | Walk Path |
|---|---|
| *Why does Ember exist at all?* | 1 (Skald) |
| *What is Hermes built out of?* | 2 (Architect) |
| *What should I copy or imitate?* | 3 (Forge) |
| *Will this break Ember?* | 4 (Auditor) |
| *In what order should we change things?* | 5 (Migration) |
| *Should we ratify this proposed change?* | 6 (Decision-maker) |
| *I'm new and need everything.* | 7 (Onboarding) |

When in doubt, walk Path 1. The Skald's framing is short, and it makes every later path land better.

---

## A Note on Skim Mode

The Codex *can* be skimmed. Each doc has:

- A frontmatter block (read it for `role`, `layer`, `hermes_source_refs`)
- A first paragraph that compresses the doc's claim
- A `## What This Means for Ember` closing section that names the True Names and Vows affected

A skim-mode reading is: frontmatter, first paragraph, closing section. About 5 minutes per doc. Useful for triage; insufficient for any decision that materially changes Ember. Skim to *find* the docs that deserve a full read.

---

## What This Means for Ember

Reading orders are not just convenience. They are how the Codex protects the **Vow of Public-Friendliness** at meta level: a corpus that cannot be entered by a non-expert is a corpus that has failed, regardless of its contents. By describing seven concrete paths — one for each kind of reader the Codex serves — this file ensures that no contributor, no matter their goal, is left wandering.

The paths also protect the **Vow of Honest Memory** at the project level. A new contributor walking Path 7 in a year's time will arrive at the same understanding as a contributor walking it today, *because the paths are recorded and maintained*. The institutional memory of "this is how we read our own Codex" is itself a kind of memory the Vows require Ember to keep honest.

True Names affected: none directly. Vows protected: Public-Friendliness, Honest Memory, Open Knowledge (through the explicit reading-by-goal taxonomy).

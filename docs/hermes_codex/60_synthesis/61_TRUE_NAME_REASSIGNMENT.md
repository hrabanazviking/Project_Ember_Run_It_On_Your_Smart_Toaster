---
codex_id: 61_TRUE_NAME_REASSIGNMENT
title: True Name Reassignment — Proposed Expansions and New Candidates
role: Cartographer
layer: Synthesis
status: draft
hermes_source_refs:
  - gateway/
  - cron/
  - skills/
  - plugins/memory/
  - acp_adapter/
  - mcp_serve.py
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 60_synthesis/60_HERMES_VS_EMBER_CROSSWALK
  - 60_synthesis/63_INTEGRATION_PATHS
  - 60_synthesis/64_MIGRATION_PLAN
  - 60_synthesis/66_DECISION_RECORDS
  - 00_vision/02_NAMING_PARALLELS
---

# 61 — True Name Reassignment

> *Names are pacts with the future. Add one only when keeping the existing ones honest costs more than the new pact.*
> — Védis Eikleið, carrying the proposal pile

## 0. Posture — proposals, not decisions

**This document proposes only.** No True Name is renamed, retired, or added here. The Skald owns naming. The Architect owns boundaries. This Cartographer doc gathers the cases where Hermes's findings strain Ember's existing six names, names the candidates, and surfaces the trade-offs so the Skald/Architect pair can decide later.

The defaults are conservative: when in doubt, do not add a name. The Vow of Smallness applies to the vocabulary too.

## 1. The six names today (a one-line reminder)

| Name | Realm | Owns |
|---|---|---|
| **Funi** | Spark | local LLM runtime + tool dispatch |
| **Strengr** | Thread | the tether to the Well |
| **Brunnr** | Well | pluggable storage adapter |
| **Smiðja** | Well | ingest forge (chunk + embed → Brunnr) |
| **Hjarta** | Spark | first-run rite |
| **Munnr** | Spark | CLI / interaction surface |

Each name binds a *concrete responsibility*. The Vow of Modular Authorship adds a precise rule: when a subsystem fails, only it fails. A subsystem whose responsibility has drifted from its True Name has lost its boundary.

## 2. The strain cases Hermes surfaces

Reading the crosswalk in [[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]], five concept-clusters do not fit cleanly:

| Cluster | Hermes home | Default Ember home if existing | Strain |
|---|---|---|---|
| Multi-platform messaging gateway | `gateway/`, `plugins/platforms/` | none | No existing True Name owns *outward messaging surfaces*. Munnr is the *human CLI*; not Telegram/Discord/Slack. |
| Scheduled / recurring tasks | `cron/`, `batch_runner.py` | Funi | Cron is *Funi without an operator* — but Funi-the-flame implies operator presence. Strains the name. |
| Skill / procedural memory subsystem | `skills/`, `tools/skill_manager_tool.py`, `agent/skill_*.py` | Funi | Procedurally-recallable knowledge fits awkwardly into Funi-as-runtime. |
| Memory provider plug-in API | `plugins/memory/`, `agent/memory_provider.py` | Brunnr | A "third-party brain" (Honcho, Mem0, Hindsight) is bigger than a storage adapter. |
| External peer protocol surface (MCP server, ACP server) | `mcp_serve.py`, `acp_adapter/` | Munnr | An MCP server is a *programmatic mouth*, not a *human mouth*. Same name, different audience. |

Five clusters, four candidate names, one expand-existing case. Examined one at a time below.

## 3. Candidate 1 — **Gjallarhorn** (gateway / multi-platform messaging)

Old Norse: *Gjallarhorn*, "the resounding horn" — Heimdall's instrument, blown to announce arrivals at the bridge. Used in poetry of the late saga era.

**Owns:** outward messaging surfaces. Telegram, Discord, Slack, Signal, WhatsApp, Matrix, SMS, email, webhook, ActivityPub, etc. Each platform is a plugin; the registry is filesystem-walk-shaped per Hermes's pattern. Channel directory, delivery, mirror, pairing.

**Realm:** *new fourth realm? or part of Spark?* The honest answer: **part of Spark, but only on workstation profile.** Pi-default Ember does not run Gjallarhorn at all. Gjallarhorn is the True Name that lights up when the operator opts in to a messaging-platform-extra; otherwise it sleeps. This is consistent with the Vow of Modular Authorship: missing extra → missing subsystem → no crash.

**What this would touch in Ember:**

```
src/ember/spark/gjallarhorn/
├── __init__.py          # lazy: detect extras, register what's present
├── INTERFACE.md         # the contract a platform plugin must honour
├── registry.py          # filesystem-walk plugin discovery
├── base.py              # PlatformAdapter ABC, MessageSource dataclass
├── delivery.py          # message routing
├── channel_directory.py # cached list of reachable targets
└── plugins/             # one __init__.py per platform; ships separately or via ember-gjallarhorn-telegram, etc.
```

**Why not "just put it in Munnr":**

- Munnr is *the human CLI*. Munnr's audience is a person at a terminal. Gjallarhorn's audience is *other people on platforms*. Same family of activity, but Munnr-as-CLI cannot grow Telegram delivery without losing its essence.
- Munnr is *small enough to live in `~/.ember/` and run on a Pi*. Gjallarhorn carries platform SDKs (telegram-bot-api, slack_sdk, discord.py, matrix-nio) — pip-extras territory.
- The Vow of Public-Friendliness suggests the operator should be able to *understand the difference*. "Send a message via the CLI" and "send a message via Telegram" are two distinct things; one name per activity preserves the operator's mental model.

**Why not its own realm:**

- A fourth realm would require the dependency law to be re-drawn (`schemas ← well ← thread ← spark ← cli` plus where?). Gjallarhorn's natural place is *adjacent to Munnr in Spark* — both are surfaces, both are output-side, both depend on Funi + Brunnr.
- Three realms is a memorable architecture. Four is harder to keep load-bearing.

**Vow check:**
- Smallness: ✅ as an opt-in extra; ❌ if it became default.
- Tethered Grounding: ✅ — Gjallarhorn does not fabricate; it relays.
- Graceful Offline: ✅ — Gjallarhorn that can't reach Telegram returns typed `Disconnected`.
- Pluggable Storage: ✅ — irrelevant to storage layer.
- Unbroken Whole: ✅ — code delivered whole.
- Flexible Roots: ✅ — config under `~/.ember/`.
- Public-Friendliness: ✅ — distinct name for distinct concept.
- Honest Memory: ✅ — platform-side messages stored as Episodes in Brunnr, same as CLI.
- Modular Authorship: ✅ — each platform plugin is independently failable.
- Open Knowledge: ✅.

**Recommendation:** *Propose Gjallarhorn as a True Name reservation* — name claimed in the docs, no code shipped until at least one platform extra is operator-requested. The reservation prevents the eventual implementation from getting smashed into Munnr.

## 4. Candidate 2 — **Hringja** (scheduling / cron / recurring tasks)

Old Norse: *hringja*, "to ring (a bell)" — to call to attention at appointed time. Familiar verb in saga prose.

**Owns:** scheduled agent runs. Cron-style triggers, interval-style triggers, calendar-style triggers. Hermes calls this `cron/` and `batch_runner.py`.

**Realm:** Spark. The scheduled task runs *as Ember* — same realm as Funi/Munnr/Hjarta.

**The case for a separate name:**

- Cron-driven Ember is *Ember-without-an-operator*. The Hjarta-Funi-Munnr triad assumes operator presence. A run at 03:00 against a cron schedule is a different mode.
- The audit / approval semantics shift: a cron run cannot use interactive approval; it must use *standing trust policy* (per ADR 0011) or refuse to act.
- Vow of Honest Memory has a corollary here: a cron run that ran and persisted a turn should be *visible* in the episode log with a `triggered_by: hringja(rule_id)` marker, so the operator returning to the terminal can see what happened.

**The case against:**

- It's small. Cron-driven Ember is *Funi running on a timer*. The behaviour differences are policy, not structure.
- Hermes ships `cron/` as a small directory; not a kingdom.
- The Vow of Smallness suggests resisting a name for something that could be `src/ember/spark/funi/schedule.py` (a 200-line module).

**Recommendation:** *Do not reserve a name. Implement as `funi/schedule.py` first.* If the implementation grows past ~500 lines or requires its own audit/approval semantics that don't fit Funi's existing shape, revisit. **Skald defaults to "no" here.**

## 5. Candidate 3 — **Lærdómr** (skill / procedural memory)

Old Norse: *lærdómr*, "learning, learnedness" — used in early Norse Christian writings for *acquired knowledge*. Carries the connotation of *knowing-by-having-learned*.

**Owns:** the skill subsystem. SKILL.md validator, discovery walk, two-tree storage (in-repo + user-local), skill self-creation, `skills_list` + `skill_view` tools, the `metadata.related_skills` graph.

**Realm:** Spark.

**The case for a separate name:**

- Skills are *not Funi*. Funi-the-flame is the model runtime; skills are stored procedures the runtime *consults*. Putting skills inside Funi blurs "what Funi is."
- The two-tree storage (in-repo `src/ember/skills/` + user-local `~/.ember/skills/`) feels more like a *small parallel Well* than a runtime concern.
- The skill self-creation loop (the agent writes a new SKILL.md mid-conversation) is a *Brunnr-shaped write* against a *skill-shaped store*.

**The case against:**

- The whole subsystem is ~150 lines of validator + walker + two tools. Vow of Smallness pushes hard against carving a True Name for 150 lines.
- Skills are *consumed* by Funi (the model needs them in the system prompt) and *invoked* through Funi's tool dispatch. Funi is the natural location.
- Hermes places skills in `tools/skill_manager_tool.py` (a tool) plus `agent/skill_*.py` (a Funi-internal subsystem). It is not its own subsystem.

**Recommendation:** *Do not reserve a name.* Implement as `src/ember/spark/funi/skills/` and `src/ember/skills/` (the in-repo seed). The two-tree pattern is *files on disk*, not a True Name. If skills ever grow their own retrieval / embedding / curator / pinning subsystem to the point that they're substantively a Well-shaped thing (~1500+ lines), revisit. **Skald defaults to "no" here.**

## 6. Candidate 4 — **Vinátta** (third-party brain extensions)

Old Norse: *vinátta*, "friendship, kinship-bond." Carries the connotation of *a relationship that augments without absorbing*.

**Owns:** the memory provider plug-in API. Honcho, Hindsight, Mem0, future third-party "external brains." Hermes calls this `plugins/memory/` and the `MemoryProvider` ABC at `agent/memory_provider.py`.

**Realm:** Brunnr-adjacent. Vinátta extends Brunnr without being it.

**The case for a separate name:**

- A memory provider is *not storage*. It is an external service Ember befriends. Mem0 holds embeddings for you; Honcho models the user; Hindsight tracks behaviour. These are not pluggable backends like SQLite/Postgres/Qdrant; they are *opinionated third-party agents*.
- The `MemoryProvider` ABC has hooks Brunnr doesn't (`on_turn_start`, `on_session_end`, `on_pre_compress`, `on_memory_write`, `on_delegation`). These are *behavioural*, not *storage-shaped*.
- Brunnr is *pluggable but uniform* — every backend implements the same `BrunnrHandle` Protocol. Vinátta would be *pluggable and heterogeneous* — each provider exposes its own tool schema (`get_tool_schemas` per the ABC).

**The case against:**

- For Ember v1, there is one (no) memory provider. Adding a True Name for an empty subsystem is premature.
- The Vinátta concept can live inside Brunnr's plugin API for a long time — Brunnr-the-Well-with-friends — without confusion. Brunnr is already pluggable; one more axis of plugability is not a Vow violation.

**Recommendation:** *Reserve the name in this doc. Do not implement until at least one operator requests an external memory provider.* If/when Honcho integration becomes concrete, revisit. The reservation is cheap; the implementation is post-Vows-stress-test scope.

## 7. The expand-existing case — Munnr expands to a *programmatic* surface

Hermes's `mcp_serve.py` is a 31 KB MCP server. It is *not* a CLI for humans; it is a tool-publishing surface for other agents. In Ember's vocabulary, Munnr is "the mouth" — the surface where Ember is summoned.

**The question:** when Ember speaks to a peer agent via MCP, is that still Munnr?

**Answer: yes, with a small expansion of definition.**

Munnr today (per `EMBER_TRUE_NAMES.md` and the slice-2 ratification) is *the command-line surface*. The True Name was chosen to constrain Munnr away from drifting into "everything user-facing." But MCP-server-shaped surfaces are still **surface-shaped**: they expose Ember's capabilities to a caller, mediate approval, render results. The audience changed (human → peer agent), not the function.

**Proposed expansion of Munnr's definition:**

> Munnr is the surface where Ember is summoned and answers — whether by a person at a CLI, a peer agent over MCP, or a future protocol that has not been named yet. Each modality is a *channel* in Munnr; each channel honours the same approval and audit contracts.

This expansion **does not require a new True Name** because the *function* is the same and the *boundaries* are the same. What changes is the channel; the mouth is the mouth.

**Vow check:** Vow of Public-Friendliness — the operator should be able to read "Munnr handles CLI and MCP" without confusion. The verbal symmetry of "mouth that speaks" works for both audiences. **Skald defaults to "yes, expand Munnr."**

## 8. Candidate 5 — *what about Strengr's growth?*

The Hermes `agent/credential_pool.py` is 1,955 lines of *credential routing across providers*. Multi-credential rotation, exhaustion-with-TTL, cross-provider failover, multi-source loading. In Ember's vocabulary, this is Strengr — the tether's health, auth, retry.

**Question:** does the credential pool deserve its own name *within* Strengr?

**Answer: no, but Strengr's responsibilities should be made explicit.**

Strengr today owns: connection lifecycle, health checks, auth, retry, transport selection. The credential pool adds: *multi-credential routing within a single provider*, and *cross-provider failover when a whole provider exhausts*. These extensions live inside the existing Strengr boundary — they are *more sophisticated tether*, not a new tether.

A clarifying note for `EMBER_TRUE_NAMES.md` (proposed for a future Architect edit):

> Strengr's "auth" responsibility includes the credential pool when multiple credentials per provider exist. Strengr's "transport selection" responsibility includes provider failover when multiple providers serve the same model class. The pool is internal; the contract Spark sees is one tether.

**Skald default:** ✅ keep within Strengr; clarify the docstring.

## 9. Candidate 6 — *Smiðja's role in trajectory compression*

Hermes's `trajectory_compressor.py` (65 KB) is a *training data pipeline* — read session transcripts, distil them into instruction-tuning pairs, output for fine-tuning a model. Ember's Smiðja is the ingest forge — chunk + embed → Brunnr.

**Question:** does training-data extraction belong to Smiðja?

**Answer: yes, in the future, as a Smiðja content source.**

Smiðja is *content sources → chunks → embeddings → Brunnr*. A "session transcripts as content source" Smiðja module would: walk `Episode` records in Brunnr, group into trajectories, emit training pairs, deposit somewhere appropriate. This is a *Smiðja in reverse* — instead of external content → Well, it's Well-content → training-pairs-file.

This is **a defer**, not a name change. Smiðja's responsibility already covers it; no expansion of definition is required.

## 10. The proposals — a single table

| # | Candidate | Recommendation | Rationale |
|---|---|---|---|
| 1 | **Gjallarhorn** (gateway) | **Reserve the name now; implement only when operator requests a platform extra.** | Multi-platform messaging is a distinct activity from CLI; the audience differs; Vow of Modular Authorship is satisfied via opt-in extras. |
| 2 | **Hringja** (cron) | **Do not reserve. Implement as `funi/schedule.py`.** | The behaviour difference is policy, not structure; ~200 lines does not justify a name. |
| 3 | **Lærdómr** (skills) | **Do not reserve. Implement as `funi/skills/`.** | Skills are Funi-consumed; the validator + walker is small; two-tree storage is files-on-disk, not subsystem. |
| 4 | **Vinátta** (external memory providers) | **Reserve the name now; do not implement until concrete demand.** | The `MemoryProvider` ABC has behavioural hooks Brunnr doesn't; future integration with Honcho/Mem0 is plausible; the reservation is cheap. |
| 5 | *Expand Munnr's definition to include MCP-server-shaped surfaces.* | **Yes, expand the definition.** | The function is the same (surface for summoning); the audience changed. |
| 6 | *Clarify Strengr's responsibility to include the credential pool.* | **Yes, clarify.** | Multi-credential routing is more-sophisticated tether, not a new subsystem. |
| 7 | *Affirm Smiðja's responsibility to include future training-data extraction.* | **Yes, no change needed.** | Smiðja-as-content-source pattern already covers it. |

## 11. The reservation mechanism

A **True Name reservation** is a one-paragraph commitment in this doc plus an entry in [[60_synthesis/67_GLOSSARY_AND_INDEX]]. It claims the name without implementing anything. The cost is zero. The benefit: when the implementation eventually arrives, it has a *name in waiting*, and the surrounding architecture docs have already referred to it. The Skald can ratify the reservation when the day comes; until then, the name is graffiti on a fence.

The two reservations proposed:

- **Gjallarhorn** — multi-platform messaging gateway.
- **Vinátta** — external memory provider plug-in API.

The two declined-for-now:

- **Hringja** — cron / scheduling. Lives inside Funi as `schedule.py`.
- **Lærdómr** — skills. Lives inside Funi as `skills/`.

## 12. The cross-platform reality check

Each candidate's cross-platform implications:

- **Gjallarhorn:** every platform plugin has its own SDK with its own cross-platform story. Telegram works everywhere; Signal needs `signal-cli`; WhatsApp has region restrictions. **No Gjallarhorn surface is part of the default install.** The Vow of Smallness wins.
- **Hringja (deferred):** stdlib `sched` + `threading.Timer` works cross-platform. If a future implementation uses APScheduler, it's pure-Python and works everywhere.
- **Lærdómr (declined):** pure-Python file walk + YAML parsing. Works everywhere Ember runs.
- **Vinátta (reserved):** every external memory provider has its own SDK with its own cross-platform story. Mem0 / Honcho are HTTPS; cross-platform fine. Hindsight has heavier deps. **No Vinátta integration is part of the default install.**

## What This Means for Ember

**True Names affected:** all six existing names see definition refinement (clarifications to docstrings only); two new names (**Gjallarhorn**, **Vinátta**) get *reserved* without implementation; two new-name candidates (**Hringja**, **Lærdómr**) are declined in favour of submodules inside existing True Names.

**Vows touched:**
- *Reinforced:* Vow of Smallness — vocabulary stays minimal; two declines and two reservations preserve the small mental model.
- *Reinforced:* Vow of Modular Authorship — opt-in extras for Gjallarhorn/Vinátta keep the default install lean.
- *Clarified:* Vow of Public-Friendliness — Munnr's expanded definition keeps operator-facing language consistent ("mouth" for any summoning surface).
- *Honoured:* Vow of Open Knowledge — every name is documented before any code is written.

**Specific code-level outputs (none yet — these are proposals):**

If the Skald ratifies, the docs that should change:
- `docs/architecture/EMBER_TRUE_NAMES.md` — add reserved-but-not-implemented entries for Gjallarhorn and Vinátta; expand Munnr's definition paragraph; clarify Strengr's credential-pool responsibility.
- `docs/architecture/ARCHITECTURE.md` — note that Gjallarhorn (if implemented) is opt-in extras within Spark; note that Vinátta (if implemented) is opt-in extras within Brunnr's plugin shape.
- `docs/architecture/DOMAIN_MAP.md` — same.

The actual implementation work for each ratified expansion lives in [[60_synthesis/63_INTEGRATION_PATHS]] and is sequenced by [[60_synthesis/64_MIGRATION_PLAN]].

**Cross-references:**
- [[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]] §13 lists the new-name candidates with their gap analysis.
- [[60_synthesis/66_DECISION_RECORDS]] hosts the ADR-Proposed records that formalize each reservation.
- [[00_vision/02_NAMING_PARALLELS]] is the Skald's poetic counterpart to this doc.
- [[60_synthesis/67_GLOSSARY_AND_INDEX]] hosts the etymological notes for Gjallarhorn, Hringja, Lærdómr, Vinátta.

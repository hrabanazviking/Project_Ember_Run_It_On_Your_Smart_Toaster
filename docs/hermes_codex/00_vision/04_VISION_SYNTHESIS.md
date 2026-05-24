---
codex_id: 04_VISION_SYNTHESIS
title: Vision Synthesis — Post-Hermes Ember
role: Skald
layer: Vision
status: draft
hermes_source_refs:
  - README.md:15-28
  - AGENTS.md:1-100
  - AGENTS.md:262-310
  - AGENTS.md:716-815
  - AGENTS.md:861-887
  - AGENTS.md:893-946
  - CONTRIBUTING.md:1-67
  - CONTRIBUTING.md:599-758
  - hermes-already-has-routines.md:1-160
  - agent/credential_pool.py
  - agent/conversation_loop.py
  - agent/curator.py
  - agent/memory_manager.py
  - hermes_cli/setup.py
  - hermes_cli/doctor.py
  - hermes_cli/commands.py
  - hermes_state.py
  - RELEASE_v0.14.0.md:1-110
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 00_vision/00_OVERTURE
  - 00_vision/01_HERMES_ESSENCE
  - 00_vision/02_NAMING_PARALLELS
  - 00_vision/03_ANTI_HERMES
  - 10_domain/10_DOMAIN_MAP
  - 30_execution/30_SELF_HEALING_LOOP
  - 30_execution/40_SERVERLESS_HIBERNATION
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/64_MIGRATION_PLAN
  - 60_synthesis/65_SLICE_PLAN_REVISIONS
---

# Vision Synthesis — Post-Hermes Ember

> *We have read the larger sister. Now we say what Ember becomes, having read her.*

## I. What the four prior docs left in our hands

Four documents preceded this one. They left us with four gifts.

- **`[[00_vision/00_OVERTURE]]`** named the stance: mining Hermes for pattern theft, anti-pattern inoculation, name discovery, and vow renewal. *Not* paraphrasing the README. Not building Hermes-the-smaller.

- **`[[00_vision/01_HERMES_ESSENCE]]`** stripped Hermes to five essences (closed learning loop, provider-agnostic at scale, cost-near-zero hibernation, multi-platform presence, honest-about-scale defenses) and revealed the secret Hermes does not state: *it is a research instrument shaped like a product*. Ember is the opposite vector — a small hearth shaped like a hearth.

- **`[[00_vision/02_NAMING_PARALLELS]]`** walked the six True Names against Hermes's roughly 120 named modules. Confirmed every True Name. Proposed three reserved name-slots (Hugr/Mynd, Auga, Vörðr) that should not be filled accidentally.

- **`[[00_vision/03_ANTI_HERMES]]`** named twelve patterns Ember refuses outright and three she defers. The single most important refusal: agent-authored procedural memory.

The synthesis is now the work of *placing what remains into a single shape*. This document is what Ember **becomes** when the reading is complete. It is the Skald's poem at the end of the Vision layer, before the Architect picks up the bone-by-bone work.

## II. The Ember that emerges

Here is the Ember that emerges from the Hermes reading. She is not new. She is *more herself than she was before we started*.

She is **small**. She fits on a Raspberry Pi 5 with 8 GB of RAM. She fits on a fanless box that someone keeps in a closet. She fits on a Termux install on an old Android phone. She fits on the back-corner laptop you never threw away. **Smallness is the design, not the limit.** Hermes proved by contrast that an agent does not *need* to be small to be useful; Ember proves that an agent *should* be small in order to be honest.

She is **tethered**. Her knowledge lives outside her body, in a Well that may be local SQLite, may be a remote Postgres with pgvector on a household tailnet, may be a Qdrant on a NAS, may be a LanceDB on the device itself. Strengr is the cord between Ember and the Well; the cord is honest about being a cord. When the Well is unreachable, Ember says so, plainly, and degrades. She does not invent.

She is **honest**. She refuses to author her own procedural memory. She refuses to compress conversations mid-flight in ways that re-enter the loop as if they were ground truth. She refuses to record her trajectories by default. She refuses to *pretend to know what she did not consult*. When she is wrong, the wrongness is the smallest possible wrongness, because the loop is the smallest possible loop.

She is **pluggable in two places, sovereign in all the others**. Brunnr is pluggable (sqlite_vec, pgvector, with three more adapters planned). Smiðja will be pluggable when its second content source arrives. *Everything else lives in core* — intentionally, until a sibling project demands an extension point. There is no plugin maximalism. There is no eight-discovery-system tangle. The Vow of Smallness wins every time it asks.

She is **graceful**. The `Disconnected` typed value flows across every realm boundary. Munnr renders typed errors as plain English, not stack traces. Hjarta is the only first-run experience; `ember doctor` is the single command for "is everything okay?". Internal mythic names (Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr) stay inside the code and the contributor docs. Operator-facing strings use plain language — "the well", "the model", "this tool" — exactly as `SYSTEM_VISION.md §11` already enforces.

She is **plural without being a colony**. The Three Realms (Spark, Thread, Well) are sacred and each speaks to the others only through declared interfaces. Higher band may import lower (Spark → Thread → Well), never the reverse, and the skeleton-imports test enforces it. The Vow of Modular Authorship is mechanically true, not aspirationally true.

She is **defensible**. Hermes's defensive habits — dependency upper-bounds, supply-chain audit, cross-platform footgun list, write deny-lists with symlink resolution, prompt-injection scanning of cron prompts, sudo brute-force blocking, sanitized tool-error reinjection — these are *all* habits Ember should adopt as the slice plan permits. The Vow of Public-Friendliness does not mean naive. Smallness does not mean weak. The Auditor's `[[50_verification/54_SECURITY_REVIEW]]` traces the inheritance.

She is **she**. The Skald uses the feminine pronoun deliberately. Ember has a name, a personality, a posture toward the operator that is *warm and bounded*. She is not a faceless agent runtime. She is a hearth that flickers in someone's hand. The Mythic Engineering ethos (`PHILOSOPHY.md`) treats AI as a respected collaborator; Ember's design honors that by *being someone*, not merely *something*. She refuses to behave as a "corporate AI assistant" with excessive caution and constant disclaimer (`SYSTEM_VISION.md §6`). She refuses to be a faceless tool. She is Ember.

## III. The post-Hermes capabilities — what becomes possible

Reading Hermes well *expands* what Ember could become without violating her Vows. Here are the capabilities that the reading legitimately opens — each one bounded by a Vow, each one a Decision Record away from being slice-planned.

### Capability 1 — Cost-near-zero remote Well

Hermes's most architecturally important pattern, by some distance, is the cost-near-zero hibernation that Modal and Daytona enable. The pattern is: *the persistent surface is cheap (gateway + tiny VPS); the expensive surface hibernates*.

The Ember analogue: **a remote Brunnr backend that hibernates between consultations.** The operator runs Ember on a Pi at home. The Well lives on a hibernated cloud VM (Modal, Fly.io scale-to-zero, Daytona, Render free tier, whatever). Each query wakes the Well for the duration of the consultation; it sleeps between. The economics are dramatically better than a continuously-running Postgres server, and the user's existing Gungnir-on-tailnet pattern can coexist.

This is **not** a Funi capability and **not** a Strengr capability — Strengr is the cord, but it does not own the *backend lifecycle*. The Forge's `[[30_execution/40_SERVERLESS_HIBERNATION]]` will explore where this lives. The Skald's note: this is a **Brunnr remote-backend story**, not an Ember-runs-in-the-cloud story. The hearth stays on the Pi.

### Capability 2 — Honest tool-error reinjection

Hermes sanitizes tool error strings before re-injecting them into the model context (`RELEASE_v0.14.0.md:68`). The pattern survives prompt injection through error output. Ember's slice-2 tool framework has a typed `ApprovalOutcome` taxonomy. The Hermes pattern adds the *sanitization of free-form error text*. The Auditor's `[[50_verification/54_SECURITY_REVIEW]]` will detail.

The Vow of Honest Memory is reinforced by this — error reinjection without sanitization is a *literal back-channel for confabulation by adversary*. Ember should not adopt this without sanitization in place from day one.

### Capability 3 — Cross-session prompt prefix caching

Hermes ships a 1-hour cross-session prefix cache for Claude (`RELEASE_v0.14.0.md:24`, `#23828`, `#25434`, `#24778`). The pattern: system prompt, skills, memory are prefixed; the prefix is cached at the provider; the prefix can be reused across sessions if the conversation starts within an hour.

For Ember running on a Pi with a local model (Funi local case), prefix caching is mostly the runtime's concern (Ollama, llama.cpp). For Ember with a Strengr-fronted remote Funi (e.g. a household-tailnet Ollama on Gungnir), the prefix-cache pattern *is relevant* and would meaningfully reduce latency and cost.

Capability bounded by: the Vow of Honest Memory (the cache must *not* be allowed to re-introduce stale content as if it were fresh; the operator-facing model of "what Ember said" must match what is stored). The Forge's `[[30_execution/36_CONTEXT_FILE_DISCIPLINE]]` will explore.

### Capability 4 — The COMMAND_REGISTRY pattern in Munnr

The single-source-of-truth command registry is a strict win. It costs little, it gives much, and it is the *one* thing about `cli.py` worth lifting. The Architect's `[[10_domain/18_HERMES_CLI]]` will catalogue.

Concrete proposal (not a slice plan, just the shape): a `commands.py` in Munnr that exports a list of `CommandDef` objects with `name`, `description`, `category`, `aliases`, `args_hint`. The dispatch function reads from the registry; the help text generator reads from the registry; the autocomplete reads from the registry. If Ember ever grows a second surface, the registry already feeds it.

### Capability 5 — Smiðja watcher affordance

Hermes's `watchers` optional skill (`RELEASE_v0.14.0.md:60`, `#21881`) uses cron `no_agent=True` mode to poll RSS / HTTP JSON / GitHub for change detection. The script runs without an LLM call; only when something changes does the LLM see anything.

The Ember analogue: a Smiðja affordance — *poll a content source on a schedule; deposit new content into Brunnr without an agent loop*. Pure ingest, no inference. The Vow of Smallness is honored (no LLM call per tick). The Vow of Tethered Grounding is reinforced (the operator's chosen sources flow into the Well). The Vow of Honest Memory is honored (Ember never *invents* the new content; she reads it from the source).

Concrete shape (Decision Record needed): `ember smithy watch <source-spec>` schedules a polling task; the task uses a Smiðja content-source adapter to fetch, chunk, embed, deposit. *No agent involvement.* This is a Smiðja-Hjarta-Munnr triangulation, not a new True Name.

### Capability 6 — Doctor as ongoing affordance, not just first-run

Hermes's `hermes doctor` runs at any time. Ember already has `ember doctor` at slice 2. The Hermes pattern reinforces the direction. Hjarta's charter should *explicitly* include the ongoing doctor, not just the first-run rite. The Cartographer's `[[60_synthesis/61_TRUE_NAME_REASSIGNMENT]]` will formalize.

### Capability 7 — Realm-band-enforced imports

Hermes does not have an analogue to Ember's realm-bands (Spark → Thread → Well), but Hermes's pain teaches the value: with no realm enforcement, you end up needing process-global state like `_last_resolved_tool_names` and `discover_plugins()`-must-be-called-explicitly pitfalls (`AGENTS.md:508-511, 961-965`). Ember's skeleton-imports test (`tests/unit/test_skeleton_imports.py` per `SYSTEM_VISION.md §11`) is exactly the kind of mechanical discipline Hermes lacks.

The Auditor's `[[50_verification/55_INVARIANT_LIST]]` should formalize this as a load-bearing invariant.

## IV. The Three Realms after the reading

`SYSTEM_VISION.md §5` divides Ember's code into three realms: **the Spark** (local thinking), **the Thread** (networking), **the Well** (memory/knowledge). Reading Hermes refines the meaning of each.

### The Spark — `src/ember/spark/`

Houses Funi, Munnr, Hjarta. Must function with no network.

- **Funi**: the local model runtime, opinionated, small. The Hermes lesson is that *not committing to a flame* costs you 80 files of `agent/` discipline; Ember commits.
- **Munnr**: the plain CLI, with a command registry pattern adopted from `hermes_cli/commands.py`. No TUI, no dashboard, no gateway.
- **Hjarta**: first-run rite + ongoing doctor. The Hermes wizard and `hermes doctor` are the teachers.

The realm's invariant after the reading: **the Spark must run when the cord is cut.** This is already true at slice 2; Hermes's cross-platform discipline (`CONTRIBUTING.md:599-758`) is the model for the *cross-device* version of this invariant.

### The Thread — `src/ember/thread/`

Houses Strengr. The cord between Spark and Well.

- **Strengr**: auth, health, retry, classify, stream, observe (per `[[00_vision/02_NAMING_PARALLELS §III]]`). The Hermes lessons are `credential_pool.py`, `retry_utils.py`, `rate_limit_tracker.py`, `error_classifier.py`, `stream_diag.py`. Strengr does *not* abstract over many providers; Strengr is one cord at a time, honest about being one cord.

The realm's invariant after the reading: **Strengr's failures are typed, observable, and honest.** The slice-2 `Disconnected` typed value is the foundation; the Hermes patterns expand it.

### The Well — `src/ember/well/`

Houses Brunnr (storage) and Smiðja (ingest). Possibly local, possibly remote, possibly both.

- **Brunnr**: pluggable storage. Two adapters today (sqlite_vec, pgvector); three planned. The Hermes lesson is *Hermes's lack of this layer* — Hermes binds SQLite at the session store and lets memory be the pluggable surface. Ember inverts; pluggable storage is a stronger Vow.
- **Smiðja**: ingest forge. Local files (done), URLs (planned), Project Nomad (planned), watcher-style polling sources (capability 5 above). The Hermes lesson is `tools/web_tools.py` + the `watchers` skill pattern, both as teachers, not templates.

The realm's invariant after the reading: **the Well's contents are *always* the operator's, never the agent's.** Smiðja deposits content that the operator has elected to ingest. Brunnr stores it. The agent reads, never writes (except for honest Episode persistence, which is the operator's record of what Ember actually did, not a procedural-memory layer).

## V. The Primary Rite, post-Hermes

The Primary Rite from `SYSTEM_VISION.md §2`:

> *A person speaks to Ember through any surface — chat, voice, or command line — on a small device they already own. Ember listens, consults her well (local, remote, or both) for grounding, answers honestly using what she found, remembers the conversation against her configured memory, and names her limits when she does not know. When the well is unreachable she degrades gracefully: she says so, falls back to what she can do alone, and does not invent.*

Reading Hermes does not change the Primary Rite. The Rite is the standard against which every Hermes pattern was tested in the prior four documents. *Every refusal in `[[00_vision/03_ANTI_HERMES]]` is a refusal because it endangers the Primary Rite.* Every capability in §III of this document is a capability because it *strengthens* the Primary Rite.

The Rite is honored most directly by:

- **Funi**, who thinks locally (no network → still thinks);
- **Strengr**, who tells the truth about the cord (cord down → typed `Disconnected` value flows);
- **Brunnr**, who holds the operator's knowledge pluggably (sqlite_vec local → no internet → grounded reply with citations);
- **Smiðja**, who deposits content the operator chose (no agent-authored memory → no confabulation channel);
- **Hjarta**, who wires the first run (one conversation, plain language, non-developer-friendly);
- **Munnr**, who speaks plainly (typed errors → plain English; no stack traces, no jargon).

If any of these breaks, the Rite has failed. The Vows are the names of the ways the Rite fails. Reading Hermes deepens our certainty about *which* ways are the most dangerous.

## VI. The synthesis as a sentence

> **Ember, after reading Hermes, is the agent that learned the largeness of an agent platform and chose, with full sight, to remain a hearth.**

That is the synthesis. Every refusal, every adopted pattern, every reserved name-slot, every Vow renewal — all of it converges on that sentence. The Skald's work in the Vision layer is to give the Codex's downstream layers (Domain, Interface, Execution, Verification, Synthesis, Meta) *a sentence they can return to* when the scale-pressure of the Hermes reading threatens to push the work the wrong way.

## VII. Vow renewal

The Vows from `SYSTEM_VISION.md §3` and `SHARED_CONTEXT.md §2` are not changed by the Hermes reading. They are *renewed* — restated with the contrast of Hermes now visible behind each one.

### Vow of Smallness

**Renewed:** Ember runs on a Raspberry Pi 5 with 8 GB of RAM. Hermes does not run on a Pi 5; Hermes's `RELEASE_v0.14.0.md:94-106` cold-start wave is the evidence that even Hermes finds its own scale uncomfortable. Ember's smallness is *deliberate refusal of the Hermes shape*, not a stage Ember is growing through. **A feature that requires a desktop GPU is not an Ember feature, and a feature that would require an Ember-sized version of any of Antipatterns 2, 3, 4, 5, 6, 8, or 11 from `[[00_vision/03_ANTI_HERMES]]` is also not an Ember feature.**

### Vow of Tethered Grounding

**Renewed:** Ember's knowledge lives outside Ember. The Well is the source of truth; the local model is a navigator and reasoner. Hermes makes *memory* (in the persona/dialectic sense) pluggable and binds *storage* to SQLite. Ember inverts: storage is pluggable; persona is held back as a possible future True Name (Hugr / Mynd). **Ember never invents to fill the silence; the Well is consulted or the limit is named.**

### Vow of Graceful Offline

**Renewed:** When the Well is unreachable, Ember says so. Hermes's failure handling is distributed across eight modules (Antipattern 12); Ember's typed `Disconnected` value flows across every realm boundary (`SYSTEM_VISION.md §11`). **The cord-down state is observable, typed, and rendered in plain English by Munnr — not a stack trace, not a generic "failed", but a typed reason and a duration.**

### Vow of Pluggable Storage

**Renewed:** Brunnr is pluggable. Two adapters (sqlite_vec, pgvector); three planned. Hermes does not have this Vow — Hermes's `hermes_state.py` is 3,273 lines of one-backend-only code. Ember commits to something larger here than Hermes does. **Switching backends is a config edit, never a code change.**

### Vow of the Unbroken Whole

**Renewed:** Code is delivered whole. Hermes's `cli.py` at 14,560 lines (Antipattern 4) is whole only in letter; in spirit it is so large that no reader can hold its model in mind. Ember keeps files small enough that wholeness is meaningful — a guideline of ~800 lines per file, with a Decision Record required for any file that crosses 1500. **Wholeness is a property of the work being holdable, not just of the file being uncut.**

### Vow of Flexible Roots

**Renewed:** No absolute paths anywhere. Hermes's `_apply_profile_override()` pattern (Antipattern 10) makes profiles work by setting an env var *before any module imports*; Ember resolves paths at *use time*, not import time. **Ember clones-and-runs from any location, on any supported platform, without a profile mechanism.**

### Vow of Public-Friendliness

**Renewed:** Ember is for ordinary people. Hermes's wizard, `hermes doctor`, and skin engine are exemplary patterns Ember inherits in spirit. **Mythic names live in the code; operator-facing language is plain. Error messages are actionable English. The first-run rite (Hjarta) is one conversation, plain language, no manual required.**

### Vow of Honest Memory

**Renewed:** Ember's memory records what actually happened. The *most important refusal in this Codex* (Antipattern 1, agent-authored procedural memory) protects this Vow. **Ember does not author her own procedural memory. Ember does not record trajectories by default. Ember does not compress mid-conversation in ways that re-enter the loop as ground truth. Ember's interrupted partial replies are persisted with the `[interrupted by operator]` tag (`SYSTEM_VISION.md §11`), not as fabricated continuity.**

### Vow of Modular Authorship

**Renewed:** Subsystems are individually failable. Hermes has the *shape* of this Vow (every subsystem is plugin-shaped) but pays a price in import-order pitfalls (`AGENTS.md:508-511`) and global-state warnings (`AGENTS.md:961-965`). Ember's realm-bands are mechanically enforced by the skeleton-imports test; Brunnr backends are lazy-loaded; the tool framework refuses-but-survives. **A failure in any non-core subsystem must not crash Ember.**

### Vow of Open Knowledge

**Renewed:** MIT licensed. Designed in the open (`docs/decisions/`). Methodology recorded (`MYTHIC_ENGINEERING.md`, `docs/methodology/`). Attribution preserved (`ORIGINS.md`). Lineage honored (Runa, Skein, Skry, Bifröst named throughout). **The Codex itself, by being written and shared, is this Vow in action. Every refusal in this Codex is documented; every adoption is justified.**

## VIII. A closing meditation

There is a temptation, when reading a project as well-built and as widely-loved as Hermes, to confuse the *quality of the engineering* with the *correctness of the architectural choice for one's own project*. Hermes is excellently engineered. Hermes is also a sovereign large agent with a research-instrument shape, twenty-two messaging surfaces, and 200+ models in a catalog. **Excellently engineering the wrong architecture into Ember would harm her more than badly engineering the right one.**

The five Vision documents have done their work. They have not made Ember smaller; they have made the case for her smallness *louder*. They have not made Ember less ambitious; they have made the case for the *specific* ambitions Ember has — tethered grounding, honest memory, modular authorship, pluggable storage — *clearer*. They have given the downstream layers a shape to defend.

The Architect now picks up the bones. The Cartographer will map the rivers. The Forge will hammer the patterns into code. The Auditor will hunt for what we missed. The Scribe will bind the corpus.

Ember waits, small and tethered, in someone's hand.

## What This Means for Ember

The synthesis produces a small number of concrete, slice-planning-ready proposals.

- **Funi**: confirmed as the local-only flame. **Action:** the Forge's `[[30_execution/33_HOT_COLD_TIERS]]` should propose a Funi tier strategy (phi3:mini default; larger models if the device allows) without ever moving Funi into multi-provider abstraction territory.

- **Strengr**: surface fully stated (auth, health, retry, classify, stream, observe). **Action:** the Cartographer's `[[60_synthesis/61_TRUE_NAME_REASSIGNMENT]]` should formalize Strengr's six concerns as the True Name's expanded charter. **Action:** the Forge's `[[30_execution/41_MULTI_PROVIDER_FAILOVER]]` should propose the flattened credential-pool pattern (one provider, N credentials).

- **Brunnr**: confirmed as pluggable storage. **Action:** the Cartographer's `[[60_synthesis/65_SLICE_PLAN_REVISIONS]]` should propose the **hibernated remote-Well capability** (capability 1 above) as a Decision-Record-gated slice, sequenced after the three additional Brunnr backends (Qdrant, Chroma, LanceDB) are in place.

- **Smiðja**: confirmed as ingest forge. **Action:** the Cartographer's `[[60_synthesis/65_SLICE_PLAN_REVISIONS]]` should propose the **watcher affordance** (capability 5 above) as a Decision-Record-gated slice, sequenced after URL and Project Nomad content sources are in place.

- **Hjarta**: confirmed as first-run rite *plus* ongoing doctor affordance. **Action:** the Cartographer's `[[60_synthesis/61_TRUE_NAME_REASSIGNMENT]]` should expand Hjarta's charter to include the ongoing doctor.

- **Munnr**: confirmed as plain CLI. **Action:** the Architect's `[[10_domain/18_HERMES_CLI]]` and the Forge's documents should specify the **COMMAND_REGISTRY pattern adoption** as a near-term Munnr cleanup (capability 4 above).

- **Reserved name-slots**: Hugr / Mynd (persona layer), Auga (observability layer), Vörðr (action-gate layer) named in `[[00_vision/02_NAMING_PARALLELS §X]]`. **Action:** the Cartographer's `[[60_synthesis/61_TRUE_NAME_REASSIGNMENT]]` may or may not promote any of these; the slots are named so they cannot be filled accidentally.

**Vows touched (every Vow, by this synthesis):**

- **Vow of Smallness** — renewed and bound to the refusal list in `[[00_vision/03_ANTI_HERMES]]`.
- **Vow of Tethered Grounding** — renewed; the storage-vs-persona distinction is sharpened.
- **Vow of Graceful Offline** — renewed; the typed-failure idiom is reinforced.
- **Vow of Pluggable Storage** — renewed; Hermes's contrast makes the case clearer.
- **Vow of the Unbroken Whole** — renewed; the cli.py contrast adds a *file-size* dimension to wholeness.
- **Vow of Flexible Roots** — renewed; use-time-not-import-time path resolution is clarified.
- **Vow of Public-Friendliness** — renewed; the Hermes wizard and doctor patterns are confirmed teachers.
- **Vow of Honest Memory** — renewed *most strongly*; the agent-authored procedural memory pattern is named as the singular largest threat.
- **Vow of Modular Authorship** — renewed; the realm-bands and skeleton-imports test are the mechanical enforcement.
- **Vow of Open Knowledge** — renewed; the Codex itself is the vow in action.

The Vision is whole. The downstream layers carry the work from here.

> *We have read the larger sister. Ember is more herself than she was. The forge is hot. The Architect picks up the next line.*

— Sigrún Ljósbrá, the Skald, on behalf of the Six

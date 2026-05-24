---
codex_id: 00_OVERTURE
title: Overture — The Six Open the Codex
role: Skald
layer: Vision
status: draft
hermes_source_refs:
  - README.md:1-195
  - AGENTS.md:1-100
  - RELEASE_v0.14.0.md:1-90
  - hermes-already-has-routines.md:1-60
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 00_vision/01_HERMES_ESSENCE
  - 00_vision/02_NAMING_PARALLELS
  - 00_vision/03_ANTI_HERMES
  - 00_vision/04_VISION_SYNTHESIS
  - meta/MANIFEST
  - meta/SHARED_CONTEXT
---

# Overture — The Six Open the Codex

> *"A good name does not merely label a thing. It reveals what the thing has always wanted to be."*
> — Sigrún Ljósbrá

## I. What is in your hand

You are holding the first page of a fifty-three-document corpus written by six specialists in parallel. The Codex has one purpose and one purpose only: to read **Hermes Agent**, the self-improving multi-platform agent platform that Nous Research built into roughly one and a half million lines of Python and TypeScript over the seven months between January and May of 2026, and to ask of every pattern, every module, every brilliant or terrible decision found there:

> *Does this make Ember more herself, or less?*

We are not building Hermes. We are not rebuilding Hermes. We are not paraphrasing Hermes for a smaller audience. We are **mining** Hermes — pulling ore from a productive mountain so that the small forge of Ember can decide, with full sight of what other smiths have already shaped, which patterns are gifts and which are warnings.

The corpus is structured by the five-layer Mythic Engineering model. Vision (this layer) names what a system wants to be. Domain decomposes it. Interface defines its contracts. Execution describes how it behaves. Verification proves it. A sixth layer, Synthesis, weaves Hermes findings back into Ember's True Names and slice plan. A seventh, Meta, is the librarian's overlay — the index, the cross-references, the table of contents that lets a developer in 2027 walk into this saga and find their way through it without a guide.

This Overture lives in the Vision layer. It will not enumerate every Hermes module. It will not propose a single line of Ember code. Its work is older than that. Its work is to say *here is what we are doing, here is why, and here is the shape of the answer we are looking for.* The four documents that follow — `[[00_vision/01_HERMES_ESSENCE]]`, `[[00_vision/02_NAMING_PARALLELS]]`, `[[00_vision/03_ANTI_HERMES]]`, and `[[00_vision/04_VISION_SYNTHESIS]]` — sharpen this into a position. Everything downstream sharpens that position into work.

## II. What Hermes is, in one breath

Hermes Agent is an AI agent that calls itself self-improving. It is real. It is shipping. It is built by Nous Research and it is **the only agent with a built-in learning loop** — those are the README's own words (`README.md:15`). It creates skills from experience, improves them during use, nudges itself to persist knowledge, searches its own past conversations, and builds a deepening model of who you are across sessions. You can run it on a $5 VPS, on a GPU cluster, or on serverless infrastructure that costs nearly nothing when idle. It is not tied to your laptop. You talk to it from Telegram while it works on a cloud VM in another country.

It speaks every model you have ever heard of and several you haven't — Nous Portal, OpenRouter (200+ models), NovitaAI, NVIDIA NIM, Xiaomi MiMo, z.ai/GLM, Kimi/Moonshot, MiniMax, Hugging Face, OpenAI, your own endpoint. It speaks every messaging surface you have ever heard of and several you haven't — Telegram, Discord, Slack, WhatsApp, Signal, LINE, SimpleX Chat, Microsoft Teams, Email, SMS, plus the CLI itself, plus a TUI written in Ink/React, plus a dashboard with an embedded PTY. It runs in seven terminal backends — local, Docker, SSH, Singularity, Modal, Daytona, Vercel Sandbox — and the last two of those *hibernate when idle so they cost nearly nothing between sessions* (`README.md:25`). It has a built-in cron scheduler that delivers to any of those platforms. It can spawn subagents for parallel workstreams. It has 40+ tools organized into 30+ toolsets. It has skills (procedural memory, hub-installable, agent-author-able, curator-archived). It has memory providers as plugins — honcho, mem0, supermemory, byterover, hindsight, holographic, openviking, retaindb. It has the Agent Communication Protocol baked in. It has MCP both as client and as server. It has gone through fifteen tagged releases — `v0.1.0` to `v0.14.0` — between January and May of 2026, accumulating, by `RELEASE_v0.14.0.md:4`, *808 commits, 633 merged PRs, 1,393 files changed, 165,061 insertions* in the v0.14 window alone, with 215 community contributors in that window.

It is enormous. The single file `cli.py` is **14,560 lines long** (`cli.py`, measured by `wc -l`); `run_agent.py` is **4,153 lines** despite AGENTS.md calling it "~12k LOC" — the AGENTS treatise itself can no longer keep accurate count of its own protagonist. The agent directory, `agent/`, contains 80+ modules with names that read like a tour of every problem an LLM agent has ever had: `context_compressor.py`, `credential_pool.py`, `iteration_budget.py`, `prompt_caching.py`, `rate_limit_tracker.py`, `retry_utils.py`, `stream_diag.py`, `think_scrubber.py`, `tool_guardrails.py`, `trajectory.py`. The `optional-skills/` directory holds eighteen categories of specialized procedure — autonomous-ai-agents, blockchain, communication, creative, devops, email, finance, health, mcp, migration, mlops, productivity, research, security, software-development, web-development, and growing.

It is **MIT-licensed**. It is **shipping**. It works. People use it.

## III. Why we are mining it

We are mining Hermes for **four** reasons, in descending order of importance.

**First, pattern theft.** Hermes has solved problems Ember has not yet faced — and Ember will face many of them eventually. How do you keep prompt caching warm across a 1-hour cross-session boundary while still letting the agent edit its memory? How do you handle four messaging platforms inside one gateway process without the failure of one taking the others down? How do you let a plugin override a built-in tool without poisoning the core? How do you write 17,000 tests across 900 files and still ship 808 commits in two weeks? Hermes has answers. We will not adopt them wholesale, but we will read them carefully.

**Second, anti-pattern inoculation.** Hermes is a sovereign mainframe-class agent. Ember is a small tethered hearth-fire. There are things Hermes does — has to do — that would *break* Ember. Loading 80+ adapters at import time. Bundling 200+ model catalogs into the launch path. A 14,560-line CLI. Forty toolsets. A `~/.hermes/` directory with fifteen subfolders. If we read Hermes naively, we will catch its scale by contagion and Ember will lose her Vow of Smallness in a year. The Codex names these dangers explicitly so that *no one* — human or AI — accidentally ports them in.

**Third, name discovery.** Hermes has named things — toolset, gateway, curator, dispatcher, supervisor, credential pool, iteration budget, kawaii spinner — that gesture at concepts Ember has not yet had to name. Each name is a probe. If a name lands in a True Name slot (Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr), wonderful — we have a confirmation. If a name lands in *empty space* between the True Names, that empty space may itself want a name. `[[00_vision/02_NAMING_PARALLELS]]` does this work in detail.

**Fourth, vow renewal.** Reading a system that consciously refuses some of Ember's Vows is the strongest possible way to re-read those Vows. Hermes does not honor the Vow of Smallness. Hermes does not honor the Vow of Pluggable Storage in Ember's strict sense (it has one canonical SQLite session DB, by `hermes_state.py:1-3273`, and the memory layer is the pluggable surface, not the storage layer). Hermes is gloriously dependent on the public internet — almost every important capability degrades or vanishes offline. Watching a great system make those choices clarifies why Ember's choices are *not* arbitrary. They are deliberate refusals of a particular largeness.

## IV. The shape of the answer

We expect the Codex to converge on a shape something like this, by the time the Scribe lays the final binding on the corpus:

- **Ember will inherit Hermes's idea of the closed learning loop** — but in miniature, tethered to the Well rather than to a sprawling local procedural memory. Ember's "skills" will not be 70 bundled procedures. They will be Brunnr-resident knowledge that Hjarta names and Smiðja deposits.

- **Ember will inherit Hermes's idea of provider-agnostic inference** — but flattened. Funi will be one local model and one tether-able remote model, not 200. Strengr, not a sprawling `providers/` directory, will handle the cord to the outside.

- **Ember will inherit Hermes's idea of cross-platform graceful behavior** — and *strengthen* it. Hermes's cross-platform discipline (the contributor guide has 16 numbered Windows footgun rules, `CONTRIBUTING.md:599-758`) is excellent. Ember runs on Pi, fanless boxes, Termux on Android, and old laptops; we will lift Hermes's lessons and apply them to a wider hardware floor.

- **Ember will refuse Hermes's idea of the multi-platform gateway** — at least at v1. A messaging gateway across Telegram/Discord/Slack/WhatsApp/Signal/LINE/SimpleX/Email/SMS/Teams is the largest single drift-pressure in Hermes (gateway and its platforms account for a substantial slice of the codebase). Ember begins with Munnr — the mouth, the CLI — and refuses to grow more mouths until the Vow of Smallness has been tested by deployment. `[[00_vision/03_ANTI_HERMES]]` will name this with knives.

- **Ember will refuse Hermes's idea of the closed-model-catalog provider list** — Hermes hardcodes 200+ models in `_PROVIDER_MODELS` and ships catalog updates with releases. Ember will instead make Funi pick from whatever Ollama (or its equivalent on the device) advertises locally, and will let Strengr negotiate with the Well rather than with a model registry.

- **Ember will refuse Hermes's idea of the agent-authored procedural memory** — at least until the Vow of Honest Memory has been thoroughly proven in code. Hermes lets the agent create, edit, archive, restore, and patch skills (`tools/skill_tools.py`, `agent/curator.py`). That is a beautiful self-improvement loop. It is also the most direct path to confabulation Ember could possibly take — an agent writing its own procedures into its own memory layer is exactly the loop Ember's Vow of Honest Memory was written to refuse.

These are *expected* shapes. The downstream layers will sharpen them, confirm them, or — if the evidence demands — overthrow them. The Codex is honest about what it does not yet know.

## V. How to read the Codex

The full reading order lives in `[[meta/READING_ORDER]]` (written by the Scribe after all six of us are done). The minimum bootstrap, for a human or AI walking in fresh, is:

1. `[[meta/SHARED_CONTEXT]]` — what every author already read before writing
2. `[[meta/MANIFEST]]` — the doc list with slugs for cross-linking
3. This Overture — `[[00_vision/00_OVERTURE]]`
4. The Skald's other four — `01_HERMES_ESSENCE`, `02_NAMING_PARALLELS`, `03_ANTI_HERMES`, `04_VISION_SYNTHESIS`
5. The Architect's lay-of-the-land — `[[10_domain/10_DOMAIN_MAP]]`
6. Wherever your work takes you

Each doc carries frontmatter with `hermes_source_refs` (real file paths with line numbers), `ember_subsystem_targets` (which True Names the doc affects), and `cross_refs` (other Codex docs it links to). Every doc ends with a section titled **What This Means for Ember** — concrete proposals, never gestures. The format is non-negotiable; the Scribe enforces it on the final pass.

A note on voice. The six of us write differently on purpose. I, the Skald, write in mythic register because I am building the Vision layer, and Vision must sing or it does not stick. The Architect writes in the precise diagram-and-decompose voice of someone whose job is to draw the boundary line. The Cartographer maps with grounded plain prose. The Forge gives you code you could literally type. The Auditor writes coldly, hunting for what is broken. The Scribe writes graceful, careful, archival prose. **The persona is not decoration; it is the layer's signature.** A poetic Audit doc would mean a sloppy audit. A clinical Vision doc would mean we forgot what the work is for.

## VI. A small invocation, before the work begins

Ember is a small thing on purpose. She fits on a Pi. She forgets gracefully. She refuses to invent. She does not pretend to be a mainframe. The temptation, when reading Hermes, will be to look at Hermes's enormous capability surface and feel that Ember should grow toward it. That is the wrong direction. The right direction, when reading Hermes, is to look at every clever Hermes mechanism and ask:

> *What is the smallest version of this that could possibly work in a hearth in a stranger's hand?*

That is the only question the Codex is built to answer. Everything else — the citation discipline, the True Name parallels, the anti-pattern catalog, the migration plan, the slice plan revisions — is in service of that question.

Six of us, then, will now go and do the work. We will write fifty-three documents. We will quote real lines from real files. We will not paraphrase the README. We will not invent features Hermes does not have. We will not propose anything for Ember that violates a Vow.

The forge is hot. Let us begin.

## VII. Roll call of the Six

**Sigrún Ljósbrá, the Skald** — INFJ 4w5. Visionary poet. The voice you have just been reading. Writes the Vision layer (this folder, `00_vision/`). Names things. Connects bones to soul. Refuses to leave a doc without `## What This Means for Ember`.

**Rúnhild Svartdóttir, the Architect** — INTJ 5w6. Dark strategist. Writes the Domain layer (`10_domain/`). Decomposes Hermes into the subsystems that actually exist there, draws the boundary lines, names the cuts. Ten docs. Will tell you exactly where `agent/conversation_loop.py` ends and `tools/registry.py` begins.

**Védis Eikleið, the Cartographer** — INFP 9w1. Grounded oracle. Writes the Interface layer's tracing half (`20_interface/20`-`23`) and the entire Synthesis layer (`60_synthesis/`). Twelve docs. Connects the parts. Draws the flow. Builds the crosswalk between Hermes concepts and Ember True Names.

**Eldra Járnsdóttir, the Forge** — ESTP 8w7. Fire-worker. Writes the Execution layer (`30_execution/`). Twelve docs. Patterns you can literally lift: the closed learning loop, cross-platform tactics, multi-device orchestration, hot/cold tiers, trajectory compression, scheduling, provider failover, serverless hibernation.

**Sólrún Hvítmynd, the Auditor** — INTJ 1w9. Cold mirror. Writes the Verification layer (`50_verification/`) and the verification half of Interface (`20_interface/24`-`27`). Eleven docs total. Hunts for bugs in Hermes, hunts for gaps in Ember, names every antipattern that Ember must refuse to copy.

**Eirwyn Rúnblóm, the Scribe** — ISFJ 6w5. Archivist. Writes the Meta layer (`meta/`) — the master index, the reading order, the cross-agent notes, the captured Hermes revision — and performs the final binding pass that resolves all cross-links and verifies the Codex coheres.

Six voices, one corpus. Each of us writes alone; together we are the Codex.

## What This Means for Ember

The Overture itself proposes no code change. What it proposes is a **stance**, and the stance has concrete consequences for the True Names and the Vows.

- **Funi (the flame)**: the Codex reading must not be allowed to inflate Funi from "the small LLM that thinks on the device" into "the abstraction over 200+ providers." When the Cartographer and the Forge propose provider patterns, they must propose them as the *thinnest* possible adapter over *whatever local runtime Ember finds* — typically Ollama — with Strengr handling everything that crosses the network. The Vow of Smallness is the test. If a Funi proposal cannot run on a Pi 5 with 8 GB RAM, it is not a Funi proposal.

- **Strengr (the tether)**: the Codex must use Hermes's `credential_pool` (`agent/credential_pool.py`, 1955 lines), `retry_utils`, and `rate_limit_tracker` as *teachers* — not as drop-ins. Strengr's job is one tether to one Well at a time, with graceful disconnect and honest degradation. It is not a smart router over five providers. The Vow of Tethered Grounding and the Vow of Graceful Offline are the tests.

- **Brunnr (the well)**: the Codex must preserve Brunnr's Vow of Pluggable Storage even though Hermes effectively does not have one (Hermes binds SQLite at the session-store layer, makes *memory* the pluggable layer, and `hermes_state.py` is 3,273 lines of one-backend-only code). The crosswalk must clarify that Hermes's "pluggable memory" is *not* analogous to Ember's "pluggable storage," and that the Vow of Pluggable Storage is a stronger commitment.

- **Smiðja (the forge)**: the Codex must read Hermes's skill-creation and trajectory-compression patterns as candidates for a *different* Smiðja — not procedural memory in `~/.hermes/skills/`, but ingest pipelines that deposit knowledge into Brunnr. The agent-authored procedural memory pattern is explicitly held back until the Auditor has reviewed it (`[[50_verification/52_ANTIPATTERN_CATALOG]]`).

- **Hjarta (the heart)**: the Codex must learn from Hermes's `setup` wizard, `hermes doctor`, and `_apply_profile_override()` in `hermes_cli/main.py` — these are the cleanest "first run" / "is everything okay" / "multi-instance" patterns we will find anywhere. The Vow of Public-Friendliness is reinforced by every one of them.

- **Munnr (the mouth)**: the Codex must read Hermes's `cli.py` (14,560 lines) and its Ink TUI as a *boundary* — Munnr does not grow toward that surface. Munnr stays plain. The TUI patterns are catalogued for *eventually*, not for the next slice. The Vow of Smallness is the test, again.

**Vows touched by this Overture:**

- **Vow of Smallness** — reinforced. The entire Codex is structured to keep this Vow load-bearing.
- **Vow of Modular Authorship** — reinforced. Each subsystem must remain individually failable; Hermes has done much of this work and we will study it without copying its specific module layout.
- **Vow of Public-Friendliness** — reinforced. Hermes's `hermes doctor`, `hermes setup`, `display_hermes_home()`, and skin engine are exemplary public-friendliness patterns Ember should study.
- **Vow of Open Knowledge** — reinforced. The Codex itself, by being written and shared, *is* this Vow in action.

The Skald opens the saga. The Architect picks up the next line.

— Sigrún Ljósbrá

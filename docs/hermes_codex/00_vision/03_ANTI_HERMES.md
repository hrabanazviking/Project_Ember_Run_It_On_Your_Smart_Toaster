---
codex_id: 03_ANTI_HERMES
title: Anti-Hermes — What Ember Must Not Inherit
role: Skald
layer: Vision
status: draft
hermes_source_refs:
  - README.md:15-28
  - AGENTS.md:22-65
  - AGENTS.md:262-310
  - AGENTS.md:487-585
  - AGENTS.md:698-715
  - AGENTS.md:751-781
  - AGENTS.md:861-887
  - AGENTS.md:893-946
  - AGENTS.md:947-1009
  - CONTRIBUTING.md:52-67
  - CONTRIBUTING.md:599-758
  - cli.py
  - run_agent.py
  - hermes_state.py
  - agent/curator.py
  - agent/memory_manager.py
  - agent/conversation_loop.py
  - agent/credential_pool.py
  - hermes_cli/commands.py
  - tools/registry.py
  - gateway
  - ui-tui
  - plugins/memory
  - skills
  - optional-skills
  - hermes-already-has-routines.md
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 00_vision/00_OVERTURE
  - 00_vision/01_HERMES_ESSENCE
  - 00_vision/02_NAMING_PARALLELS
  - 00_vision/04_VISION_SYNTHESIS
  - 50_verification/52_ANTIPATTERN_CATALOG
  - 50_verification/50_HERMES_RISK_REGISTER
  - 60_synthesis/63_INTEGRATION_PATHS
---

# Anti-Hermes — What Ember Must Not Inherit

> *The names of the things we refuse are as load-bearing as the names of the things we welcome. A door is only a door because the wall around it stays a wall.*

## I. Why this document exists

A naive reading of a great system is contagious. The reader catches the system's scale, its surface, its accumulated patterns — and brings them home like a virus. The reader does this *because the great system has solved real problems, and the solutions are beautiful, and beauty is contagious.*

This document is the inoculation. It names — concretely, with file paths and line citations — the patterns in Hermes that **would harm Ember** if ported in. Each pattern is matched to the Vow it violates. Some are refused outright. Some are deferred. None are adopted without surgery.

The Skald's voice is mythic; the Skald's tool here is the knife. **There will be no encouragement in this document.** That is the Forge's department. This is the document Ember reads in three months when she is tempted to grow.

## II. The patterns Ember refuses, with citations

### Antipattern 1 — Agent-authored procedural memory

**Where it lives in Hermes:**
- `skills/` — ~70 bundled skills.
- `optional-skills/` — 18 categories of niche skills.
- `~/.hermes/skills/` — agent-authored skills with `created_by: "agent"` provenance.
- `tools/skill_tools.py` — agent-callable tools to view, manage, and edit skills.
- `agent/curator.py` — background review loop that auto-archives stale agent-authored skills.
- `agent/curator_backup.py` — pre-run tar.gz snapshots so the curator's actions are reversible.
- `tools/skill_usage.py` — telemetry sidecar at `~/.hermes/skills/.usage.json`.
- `CONTRIBUTING.md:478-528` — the skill authoring standards (HARDLINE).
- `AGENTS.md:751-781` — the curator architecture and invariants.

**What it does:** Hermes lets the agent author new SKILL.md files at runtime in response to repeated tasks. The skills become procedural memory — markdown procedures the agent can re-load on a future session. The curator quietly archives skills the agent hasn't used in a configurable number of days. Pinned skills are exempt. `skill_manage(action="delete")` refuses pinned skills.

**Why Ember refuses it:** Three Vows are at risk simultaneously.

- **Vow of Honest Memory.** Ember's memory records what *actually happened*. An agent-authored skill is, by construction, a *prediction* the agent makes about future usefulness. If the agent learns wrong — and small agents *will* learn wrong — the skill encodes that wrongness into the system's procedural memory in a way that is hard to detect and harder to remove. Hermes mitigates this with the curator and with pinning. Ember mitigates it by *not having the layer at all*.
- **Vow of Tethered Grounding.** Knowledge lives outside the model. A skill the agent wrote about how to do something is *not* tethered — it is a parallel memory layer that is *not Brunnr*, that the agent is the sole author of, that the operator did not curate, that the Well does not vouch for. It is the most direct possible path to confabulation Ember could grow.
- **Vow of Smallness.** Hermes's skills system requires: a curator background loop, a usage telemetry sidecar, an archive directory, pinning state, frontmatter parsing, condition evaluation (`fallback_for_toolsets`, `requires_toolsets`, `fallback_for_tools`, `requires_tools`, `platforms`), SKILL.md format enforcement (hardline standards), 600+ lines of `prompt_builder.py` to inject skills into the system prompt, and a CLI surface (`hermes skills` + `hermes curator`). The footprint is enormous.

**What Ember does instead:** *Skills* in Ember's sense, if Ember ever has them, are **Brunnr-resident knowledge documents** that Smiðja deposits and the operator authored. They are not agent-authored. The Vow of Honest Memory holds.

**Verdict:** **REFUSE.** The Auditor's `[[50_verification/52_ANTIPATTERN_CATALOG]]` will formalize this. The Cartographer's `[[60_synthesis/63_INTEGRATION_PATHS]]` will *not* propose a path here.

---

### Antipattern 2 — The multi-platform messaging gateway

**Where it lives in Hermes:**
- `gateway/run.py` — the gateway runner.
- `gateway/platforms/` — adapters for **22 messaging surfaces**: telegram, discord, slack, whatsapp, homeassistant, signal, matrix, mattermost, email, sms, dingtalk, wecom, weixin, feishu, qqbot, bluebubbles, yuanbao, webhook, api_server, line, simplex, teams.
- `gateway/builtin_hooks/` — extension point for always-registered gateway hooks.
- `gateway/session.py` — session store, context prompts, reset policies.
- `gateway/config.py` — platform configuration resolution.
- `RELEASE_v0.14.0.md:196-238` — every platform's per-release fixes.
- `AGENTS.md:861-887` — the gateway's *two-guard* message-routing discipline (base adapter `_pending_messages` queue + gateway runner intercepting `/stop`/`/new`/etc. *both* must bypass the same way).

**What it does:** A single gateway process speaks to all 22 messaging platforms simultaneously. Each platform's adapter handles auth, message receipt, message delivery, attachment handling, native button UI (Telegram inline keyboards, Discord buttons), voice memo transcription, channel history backfill, and per-platform slash-command routing.

**Why Ember refuses it (at v1):**

- **Vow of Smallness.** This subsystem is enormous. Even if Ember adopted only Telegram, the surface includes: bot token auth, webhook receipt, polling fallback, Markdown/HTML escape rules, inline keyboard rendering, voice transcription, photo handling, error classification (Hermes has special handling for "guest mention mode"), notification mode toggles, oversized-message split-and-deliver, DM topic routing via reply fallback, and the *gateway hook system* underneath all of it.
- **Vow of Public-Friendliness.** The first-run setup *for the multi-platform gateway* is a wizard with its own state. The Hermes wizard (`hermes gateway setup`) is good; it is still a meaningful additional surface for a non-developer to navigate. Ember can be friendly with one mouth before she is friendly with twenty-two.
- **Vow of Modular Authorship.** Ember's Vow of Modular Authorship is *honored* by this refusal — the Vow requires every non-core subsystem to be individually failable; the cleanest way to ensure the gateway is individually failable is for the gateway *not to exist at v1*. When it eventually does exist, it must be wholly separable.

**What Ember does instead:** Munnr is the CLI. That is the mouth. If a user wants to reach Ember from a phone, the operator opens a terminal on the device (Termux, SSH from a laptop, etc.). The Vow of Public-Friendliness commits to "non-developers can use her" but does not commit to "non-developers can reach her from WhatsApp." That is a later Vow if it is a Vow at all.

**Verdict:** **REFUSE at v1.** **DEFER, as a sibling project** — a plausible later sibling in the monorepo would be a separate "Ember Gateway" project that uses Ember's APIs to expose her over a messaging surface. That project, if it ever exists, lives under its own True Name and its own slice plan. *Not Ember herself.*

---

### Antipattern 3 — The hardcoded multi-provider model catalog

**Where it lives in Hermes:**
- `providers/`, `plugins/model-providers/<name>/` — the per-provider plugins.
- `_PROVIDER_MODELS` (referenced in `AGENTS.md:1094-1127`) — the hardcoded model catalog. Ships in code, updates with releases.
- `agent/<provider>_adapter.py` — anthropic_adapter.py, bedrock_adapter.py, codex_responses_adapter.py, gemini_native_adapter.py, gemini_cloudcode_adapter.py, etc. — one adapter per model-shape.
- `agent/model_metadata.py`, `agent/models_dev.py` — model metadata sourced from disk cache, models.dev, and Nous Portal (the v0.14 cold-start work explicitly cached this).

**What it does:** Hermes maintains an in-code list of ~200 models across ~15 providers. The catalog is consulted at startup to populate `hermes model` pickers, to validate user model choices, to determine context-length defaults, and to drive provider routing (OpenRouter's "Pareto" router with `min_coding_score`, smart-fallback chains, etc.).

**Why Ember refuses it:**

- **Vow of Smallness.** A model catalog with 200 entries is *itself* a load-bearing data structure that must be maintained, tested (Hermes explicitly bans "change-detector" tests on it, `AGENTS.md:1094-1127`), and updated. Ember does not want this responsibility.
- **Vow of Open Knowledge.** The catalog is, in practice, a curation of *commercial provider models*. Ember's commitments lean toward local models and open weights (the user's Pi-5-friendly default is `phi3:mini` per `SYSTEM_VISION.md §11`); a commercial-model catalog is misaligned.
- **Vow of Flexible Roots.** A catalog that hardcodes provider names and endpoints is *less* flexible than a system that simply asks the local runtime "what models do you have?"

**What Ember does instead:** Funi asks the local runtime (Ollama or equivalent) via its OpenAI-compatible API: *what is here, what works, what fits the device?* No catalog. Strengr, when configured, asks the remote Well *what model is reachable* — again, no catalog. The user's `phi3:mini` is the device's choice, not Ember's prescription.

**Verdict:** **REFUSE.** Forever. No model catalog as a concept inside Ember.

---

### Antipattern 4 — The cli.py monolith

**Where it lives in Hermes:**
- `cli.py` — **14,560 lines** (measured by `wc -l`, May 2026). One file. The classic prompt_toolkit-based interactive CLI.
- The file contains: command dispatch, skin engine wiring, banner rendering, spinner orchestration, autocomplete, history, slash command handling, session persistence integration, prompt caching coordination, tool progress display, response rendering, multi-line input handling, paste detection, etc.

**What it does:** Everything the classic CLI does. Has all of it in one place.

**Why Ember refuses it:**

- **Vow of the Unbroken Whole.** The Vow says code files are delivered whole, never as fragments. A 14,560-line file is *technically* whole, but it is so large that no human or AI can hold its full mental model in one read. Whole-file delivery becomes degenerate at that scale. The Vow is honored *in letter* and broken *in spirit*.
- **Vow of Smallness.** A 14k-line CLI is not small.
- **Vow of Modular Authorship.** When one file holds the dispatch, the rendering, the autocomplete, the history, and the slash commands, no single piece is individually failable. A bug in any of those crashes the CLI.

**What Ember does instead:** Munnr is decomposed. Slash commands live in a registry (the COMMAND_REGISTRY pattern from `hermes_cli/commands.py` *is* worth adopting, see `[[00_vision/02_NAMING_PARALLELS §VII]]`). Rendering, history, autocomplete, and dispatch live in separate modules. No file in Munnr exceeds (call it) 800 lines without a Decision Record explaining why. The Vow of Modular Authorship enforces the decomposition.

**Verdict:** **REFUSE the monolith shape.** **ADOPT the COMMAND_REGISTRY single-source-of-truth pattern** in a small, decomposed Munnr.

---

### Antipattern 5 — Eager import-time discovery and registration

**Where it lives in Hermes:**
- `tools/registry.py` — central tool registry.
- `tools/<name>.py` — each tool file calls `registry.register()` *at import time*.
- `model_tools.py` — imports all tool modules via `discover_builtin_tools()` to trigger registration (`AGENTS.md:69-79`).
- `plugins/<name>/__init__.py` — plugins register hooks and tools at module load.
- `plugins/model-providers/<name>/__init__.py` — providers call `register_provider(ProviderProfile(...))` at module load.
- The v0.14.0 cold-start wave was *specifically* about clawing back what eager imports had cost: ~19 seconds shaved off launch (`RELEASE_v0.14.0.md:94-106`).

**What it does:** Modules side-effect-register themselves into a global registry at import time. Discovery is a side-effect of importing.

**Why Ember refuses it:**

- **Vow of Smallness.** The v0.14.0 cold-start work *is the evidence*. Hermes spent significant engineering effort on lazy-loading heavy adapters (`#22138`, `#22120`, `#22681`, `#22790`, `#22831`, `#22859`, `#22808`, `#22766`) because eager import-time discovery had grown the launch path to ~19 seconds longer than necessary. Ember on a Pi 5 cannot afford that growth path.
- **Vow of Modular Authorship.** Import-time side-effects are *the* canonical pattern for "one module's import failure cascades into the whole system." Hermes mitigates by lazy-loading providers (`providers/__init__.py._discover_providers()` is scanned on first call — `AGENTS.md:556-557`); Hermes has *not yet* solved this problem in `tools/registry.py`. Ember should not adopt the pattern that Hermes itself is still recovering from.

**What Ember does instead:** Adapters and tools are registered *explicitly*, in code that runs *when the user enables them*. The Vow of Modular Authorship's existing implementation in slice 2 (Brunnr backends lazy-loaded, missing pgvector extra doesn't break import per `SYSTEM_VISION.md §11`) is the correct shape.

**Verdict:** **REFUSE import-time discovery.** Use explicit registration triggered by configuration.

---

### Antipattern 6 — The pluggable-everything maximalism

**Where it lives in Hermes:**
- `plugins/memory/<name>/` — 8 memory providers.
- `plugins/model-providers/<name>/` — ~15 model providers.
- `plugins/context_engine/` — context engine plugins.
- `plugins/image_gen/` — image-gen providers.
- `plugins/kanban/` — kanban dispatcher + dashboard + systemd unit.
- `plugins/observability/`, `plugins/hermes-achievements/`, `plugins/spotify/`, `plugins/google_meet/`, `plugins/teams_pipeline/`, `plugins/disk-cleanup/`, `plugins/example-dashboard/`, `plugins/video_gen/`, `plugins/browser/`, `plugins/platforms/`, `plugins/web/`.
- `hermes_cli/plugins.py::PluginManager` — general plugin discovery.
- `AGENTS.md:487-585` — the full plugin architecture, including the explicit *policy* that "No new in-tree memory providers" — meaning the plugin maximalism has already been *checked* by the project itself.

**What it does:** Almost every subsystem is plugin-shaped. Six plugin discovery systems (general, memory, model-providers, context-engine, image-gen, dashboard) coexist with different rules. The general PluginManager records `kind: model-provider` manifests but *does not import them* (would double-instantiate). Plugins without an explicit `kind:` get auto-coerced via a source-text heuristic (`AGENTS.md:567-571`).

**Why Ember refuses it:**

- **Vow of Smallness.** Six discovery systems is *six different ways to be wrong*. Each requires its own discipline, its own tests, its own edge cases.
- **Vow of Public-Friendliness.** A non-developer who installs Ember should not need to understand what kind of plugin is what kind of plugin to make her work.
- **Vow of Modular Authorship.** Plugin systems *promise* modular authorship and *deliver* a tangle of import ordering, registration races, and silent failure modes. Hermes's *own* AGENTS.md catalogs the "Discovery timing pitfall: `discover_plugins()` only runs as a side effect of importing `model_tools.py`. Code paths that read plugin state without importing `model_tools.py` first must call `discover_plugins()` explicitly (it's idempotent)" (`AGENTS.md:508-511`). When the AGENTS document of the *authoring team* has to call out this kind of pitfall, the plugin maximalism has overshot the Vow.

**What Ember does instead:** Brunnr backends are pluggable via a clean Protocol (slice 2 already has this — `BrunnrHandle` with 14 methods, sqlite_vec + pgvector adapters). Smiðja content sources are pluggable. *Everything else is in core*, intentionally, until a second sibling project demands an extension point. **No plugin system as a v1 concept.** When a plugin system arrives in Ember, *one* discovery surface, *one* rule.

**Verdict:** **REFUSE at v1.** Brunnr's Protocol stays. Smiðja's Protocol arrives when Smiðja's adapter count exceeds 1. Beyond those two, no plugin maximalism.

---

### Antipattern 7 — Implicit context-mutation midcourse

**Where it lives in Hermes:**
- `agent/conversation_loop.py` (4,094 lines) — the conversation loop, with prompt-caching coordination, tool dispatch, context compression.
- `agent/context_compressor.py` — auto-summarization when approaching context limits.
- `agent/conversation_compression.py` — explicit compression API.
- `AGENTS.md:861-887` — the policy: "Prompt Caching Must Not Break". The doc warns: do not alter past context mid-conversation, do not change toolsets mid-conversation, do not reload memories or rebuild system prompts mid-conversation. The ONLY time we alter context is during context compression.
- The slash commands that mutate system-prompt state must be *cache-aware*: default to deferred invalidation (change takes effect next session), with an opt-in `--now` flag (`AGENTS.md:872-875`).

**What it does:** Hermes *does* mutate the prompt context, but only at carefully-named moments, with a documented discipline. The `/skills install` command, for instance, defaults to "next session" and requires `--now` to invalidate the cache immediately.

**Why this is an antipattern *for Ember* even though Hermes does it well:**

- **Vow of Honest Memory.** Hermes's discipline is correct *for Hermes's scale* — when the conversation is long, compression is required, and an honest compression boundary is the only sane way to handle it. Ember's conversations are smaller, run on smaller models, and have less context to compress. The *risk* of confabulation introduced by even a careful compression pass is higher relative to the value of the compression.
- **Vow of Tethered Grounding.** Compression summaries are *agent-authored content* that re-enters the agent's own context as if it were ground truth. Hermes handles this by labeling compression points clearly; Ember's smaller models may not respect the labels as well.

**What Ember does instead:** Ember's slice-2 streaming path persists the FINAL reply post-tool-loop, not intermediate states (`SYSTEM_VISION.md §11`). The Episode-as-persistence is post-turn. Ember does *not* compress mid-conversation; she truncates the in-memory window with a clear marker, and she trusts the Well to provide longer-term recall via retrieval. The Vow of Honest Memory holds.

**Verdict:** **REFUSE mid-conversation context mutation at v1.** Ember's truncation is honest about being truncation. No compression. No mid-conversation memory rebuild. When (and if) Ember grows toward longer conversations, the compression discipline becomes a Decision Record gated explicitly on a slice ratification.

---

### Antipattern 8 — The seven terminal backends

**Where it lives in Hermes:**
- `tools/environments/base.py` — `BaseEnvironment` ABC.
- `tools/environments/local.py`, `docker.py`, `ssh.py`, `singularity.py`, `modal.py`, `daytona.py` — six concrete backends (Vercel Sandbox is the seventh, per `README.md:25`).
- `AGENTS.md:35-37` — the terminal backend abstraction.
- `tui_gateway/` — the terminal backend abstraction *for the TUI process* (`AGENTS.md:35`).

**What it does:** The agent can execute shell commands in any of seven environments. The Modal and Daytona backends hibernate to near-zero cost between sessions.

**Why Ember refuses it:**

- **Vow of Smallness.** Six backends + the ABC + tests for each = a substantial subsystem. The Pi-5 default user has *one* environment: the Pi.
- **Vow of Public-Friendliness.** The non-developer user does not own a Modal account. They do not run a Singularity cluster. The seven-backend abstraction is for a different audience.

**What Ember should learn from this without copying:** The cost-near-zero hibernation idea (Modal, Daytona) is **the most architecturally important thing Hermes has done**, but the right place for Ember to apply it is **Brunnr-as-remote-Well**, not "Ember runs in a Modal sandbox." A Pi at home talks to a Brunnr that lives on a hibernated cloud VM and wakes on demand. *That* is the pattern. The Forge's `[[30_execution/40_SERVERLESS_HIBERNATION]]` will explore.

**Verdict:** **REFUSE the multi-backend pattern.** **ABSORB the hibernation idea into Brunnr's remote-backend story**, not into Funi's execution surface.

---

### Antipattern 9 — The `tools/registry.py` global state

**Where it lives in Hermes:**
- `tools/registry.py` — central registry with global module state.
- `model_tools.py` — process-global `_last_resolved_tool_names`. `_run_single_child()` in `delegate_tool.py` saves and restores this global around subagent execution (`AGENTS.md:961-965`).
- `AGENTS.md:947-952` — the `_last_resolved_tool_names` pitfall is documented explicitly: "If you add new code that reads this global, be aware it may be temporarily stale during child agent runs."

**What it does:** A process-global dict tracks resolved tool names. Subagent invocations swap-and-restore the global.

**Why Ember refuses it:**

- **Vow of Modular Authorship.** Process-global state that must be swapped-and-restored by callers is *the* canonical anti-modular pattern. The fact that the AGENTS doc has to *warn future contributors* about this state is proof that the abstraction has leaked.

**What Ember does instead:** Tool resolution is per-Funi-loop state, scoped to the conversation. Subagent execution is not a v1 concern. The Vow of Modular Authorship is reinforced.

**Verdict:** **REFUSE.**

---

### Antipattern 10 — Profile-specific path resolution at module-import time

**Where it lives in Hermes:**
- `hermes_cli/main.py::_apply_profile_override()` — sets `HERMES_HOME` *before any module imports* (`AGENTS.md:897-899`).
- The rule from `AGENTS.md:923-926`: "Module-level constants are fine — they cache `get_hermes_home()` at import time, which is AFTER `_apply_profile_override()` sets the env var. Just use `get_hermes_home()`, not `Path.home() / ".hermes"`."

**What it does:** A profile mechanism that depends on environment variables being set *before any module imports* in order for profile-scoped paths to resolve correctly.

**Why this is an antipattern *for Ember* even though Hermes makes it work:**

- **Vow of Flexible Roots.** Ember's Vow is satisfied by relative paths and `Path.home()` / `~` expansion at use-time, not by an env-var-before-import dance. The Hermes pattern *works* but is fragile to refactoring: any module that resolves a path at import time rather than at use time silently locks the profile to "whichever profile was active when import happened."
- **Vow of Modular Authorship.** Coupling profile state to module-import order is the kind of coupling that does not show up in tests until refactoring breaks it.

**What Ember does instead:** Ember resolves paths at *use time*, not import time. `Path.home() / ".ember"` is computed each time it's needed. The Vow of Flexible Roots is honored without a profile mechanism.

**Verdict:** **REFUSE the import-time profile pattern.** If Ember ever wants profiles, they live as a separate setup-time configuration, not as an env-var-before-import side channel.

---

### Antipattern 11 — Trajectory recording by default

**Where it lives in Hermes:**
- `trajectory_compressor.py` (65 KB at top level) — batch training data pipeline.
- `agent/trajectory.py` — per-conversation trajectory saving helpers.
- `batch_runner.py` (57 KB) — parallel batch processing for trajectory generation.
- `run_agent.py` parameter `save_trajectories: bool = False` (per `AGENTS.md:97`) — *off by default in Hermes*, but the infrastructure is present and the public surface advertises trajectory generation as a research feature (`README.md:26`).

**What it does:** Hermes can save every conversation's trajectory (the full message tree, tool calls, results, model outputs) to disk for offline training-data curation. The compressor consolidates these.

**Why Ember refuses it:**

- **Vow of Open Knowledge.** The *intent* of trajectory recording in Hermes is downstream model training (a Nous Research concern). Ember's commitments are different: the operator's data belongs to the operator, full stop.
- **Vow of Honest Memory.** A trajectory record is the *literal record of what the agent did*. If trajectory recording becomes default-on for Ember, the operator has additional surface area to audit, redact, and protect. The cleanest design is to have no such surface area.
- **Vow of Smallness.** A 65 KB compressor and a 57 KB batch runner are substantial subsystems that Ember has no use case for.

**What Ember does instead:** Conversations persist as `Episode` records via the existing slice-2 path (`SYSTEM_VISION.md §11`). Trajectory in the Hermes/training-data sense does not exist as a concept in Ember.

**Verdict:** **REFUSE.**

---

### Antipattern 12 — The "8 reasons in 8 places" pattern

**Where it lives in Hermes:**
- Failure classification is not centralized. `agent/error_classifier.py` exists, but error classification *also* happens in:
  - `agent/retry_utils.py`
  - `agent/rate_limit_tracker.py`
  - `agent/stream_diag.py`
  - `agent/conversation_loop.py`
  - Each provider adapter (`anthropic_adapter.py`, `bedrock_adapter.py`, etc.)
  - `tools/registry.py` (tool error wrapping)
  - `gateway/run.py` (gateway failure routing)
- Each of these has its own concept of what counts as which kind of failure.

**What it does:** Failure handling is distributed and each module has its own taxonomy.

**Why this is an antipattern *for Ember*:**

- **Vow of Graceful Offline.** Ember has *already* made the better choice — slice 2's pgvector adapter has an eight-reason classification, and `Disconnected` / `Unavailable` are typed values that flow across realm boundaries (`SYSTEM_VISION.md §11`). The cleanest extension is to **make Strengr the single owner of network-failure classification**, not to scatter it.
- **Vow of Modular Authorship.** Centralized classification means a failure in classification is failable in one place, not eight.

**What Ember does instead:** Strengr owns the typed failure taxonomy. Funi owns the local-runtime failure taxonomy. Brunnr owns the storage failure taxonomy. Each True Name owns its own failure shapes; no Name leaks shapes into another's territory.

**Verdict:** **REFUSE the distributed taxonomy.** Centralize at the True Name boundary.

---

## III. Patterns Ember defers but does not refuse

Three patterns are explicitly *deferred* rather than *refused*. They are real, they are good, they are not for v1.

- **The credential-pool concept** (`agent/credential_pool.py`) — Ember will adopt a *flattened* version when a real use case (multiple Gungnir tailnet IPs? multiple Nous Portal tokens?) arrives. The shape is right; the timing is later. See `[[30_execution/41_MULTI_PROVIDER_FAILOVER]]`.

- **The setup-wizard pattern** (`hermes_cli/setup.py`) — Hjarta already covers slice 1. The Hermes pattern is a teacher for slice N when Hjarta grows.

- **The COMMAND_REGISTRY single-source-of-truth pattern** (`hermes_cli/commands.py`) — Adopt the *shape* in Munnr's command table now; the Telegram/Slack/etc. consumers of the registry are deferred indefinitely.

## IV. The single most important refusal

If Ember can only refuse one pattern from Hermes, it is **Antipattern 1**: agent-authored procedural memory.

This is not because it's the largest. It is because it is the most contagious: every other antipattern is recognizable as a scale problem the Vow of Smallness already names. The agent-authored skill pattern is the only one that *masquerades as a Vow-honoring feature*. It looks like "self-improvement." It looks like "honest memory." It is neither. It is a parallel memory layer the agent is the sole author of, that the Well does not vouch for, that the operator did not curate, that grows silently in `~/.hermes/skills/`, that the curator quietly archives based on its own heuristics.

Refuse this one and the rest of the Codex's anti-patterns become easier to refuse. Accept this one and the rest cascade in — because once the agent is authoring its own procedural memory, it will want a curator, and the curator needs telemetry, and telemetry needs a sidecar, and the sidecar needs a CLI surface, and so on.

## V. A meditation on largeness

Hermes is large because the problem space it serves is large. Twenty-two messaging platforms is appropriate when your project's hypothesis is *humans live in chat*. Eight memory providers is appropriate when your project's hypothesis is *the user-modeling layer is research territory*. Seven terminal backends is appropriate when your project's hypothesis is *the agent's execution surface should be wherever compute is cheapest right now*. 200+ models is appropriate when your project's hypothesis is *the next great model could come from anywhere*.

Ember's hypothesis is *one person, one device, one Well, one mouth, honesty about the limits of all of those*. The hypothesis is small, deliberately. The smallness is not a limitation Ember will grow out of. The smallness *is the design*.

When the temptation arises — and it will arise — to inflate Ember toward Hermes's surface, the answer is *not* "Hermes has it, so Ember should too." The answer is "Ember's hypothesis does not need it." If Ember's hypothesis ever changes, the Decision Record is the place to argue. Until then, the patterns in this document stay refused.

## What This Means for Ember

The Anti-Hermes reading produces concrete refusals, codified.

- **Funi**: refuses the eager-import-time tool registry pattern (Antipattern 5), refuses the global `_last_resolved_tool_names` state pattern (Antipattern 9), refuses mid-conversation context mutation (Antipattern 7). Funi's loop is small, explicit, and local-state-only.

- **Strengr**: refuses the distributed failure taxonomy (Antipattern 12). Strengr owns network-failure classification end-to-end. Refuses the 200+ model catalog (Antipattern 3) — Strengr negotiates with the Well; there is no catalog.

- **Brunnr**: refuses the SQLite-bound session-storage pattern (the one that Hermes's `hermes_state.py` embodies at 3,273 lines). Brunnr is and remains pluggable. Refuses the seven terminal backends pattern (Antipattern 8) at Funi's layer; *absorbs the hibernation idea* into Brunnr's eventual remote-Well story.

- **Smiðja**: refuses agent-authored procedural memory (Antipattern 1). Refuses trajectory-by-default (Antipattern 11). Smiðja's job is content ingestion into Brunnr; nothing else.

- **Hjarta**: refuses the import-time profile pattern (Antipattern 10). Hjarta's first-run rite uses use-time path resolution. If profiles are ever added, they live as setup-time configuration with no env-var-before-import dance.

- **Munnr**: refuses the cli.py monolith (Antipattern 4). Refuses the multi-platform gateway (Antipattern 2). Refuses the pluggable-everything maximalism (Antipattern 6). Munnr is the plain CLI; Munnr is decomposed; Munnr adopts the COMMAND_REGISTRY pattern but not the surfaces that consume it elsewhere in Hermes.

**Vows touched (every Vow is touched by at least one refusal):**

- **Vow of Smallness** — reinforced by Antipatterns 2, 3, 4, 5, 6, 8, 11.
- **Vow of Tethered Grounding** — reinforced by Antipatterns 1, 7.
- **Vow of Graceful Offline** — reinforced by Antipattern 12.
- **Vow of Pluggable Storage** — reinforced by Antipattern 8's hibernation-into-Brunnr proposal.
- **Vow of the Unbroken Whole** — reinforced by Antipattern 4 (a file too large to hold in mind is whole only in letter).
- **Vow of Flexible Roots** — reinforced by Antipattern 10.
- **Vow of Public-Friendliness** — reinforced by Antipatterns 2, 6.
- **Vow of Honest Memory** — reinforced *most strongly* by Antipatterns 1, 7, 11.
- **Vow of Modular Authorship** — reinforced by Antipatterns 5, 6, 9, 12.
- **Vow of Open Knowledge** — reinforced by Antipatterns 3, 11.

**The Auditor's `[[50_verification/52_ANTIPATTERN_CATALOG]]` will catalogue each of these formally with severity, detection patterns, and remediation. The Cartographer's `[[60_synthesis/63_INTEGRATION_PATHS]]` will not propose paths for any of the refused patterns.**

The knives are sheathed. The synthesis comes next.

— Sigrún Ljósbrá

---
codex_id: 02_NAMING_PARALLELS
title: Naming Parallels — Hermes Modules and the True Names
role: Skald
layer: Vision
status: draft
hermes_source_refs:
  - AGENTS.md:22-65
  - AGENTS.md:83-140
  - AGENTS.md:262-310
  - AGENTS.md:487-585
  - AGENTS.md:716-815
  - agent/conversation_loop.py
  - agent/credential_pool.py
  - agent/memory_manager.py
  - agent/prompt_builder.py
  - agent/curator.py
  - hermes_cli/setup.py
  - hermes_cli/doctor.py
  - hermes_cli/commands.py
  - hermes_state.py
  - tools/registry.py
  - cli.py
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 00_vision/00_OVERTURE
  - 00_vision/01_HERMES_ESSENCE
  - 00_vision/03_ANTI_HERMES
  - 10_domain/10_DOMAIN_MAP
  - 60_synthesis/60_HERMES_VS_EMBER_CROSSWALK
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
---

# Naming Parallels — Hermes Modules and the True Names

> *To name well is to draw a circle on the ground and say: only what stands inside this circle is the thing.*

## I. Why this document exists

Ember has six True Names — **Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr** — and the Vows say those names are load-bearing. A subsystem that drifts away from its True Name has lost its boundary (`SYSTEM_VISION.md §4`). Hermes has roughly *eighty* module names in `agent/` alone, plus another forty in `tools/`, plus twenty-two messaging platforms, plus eighteen optional-skill categories. The work of this document is to walk the two namings against each other and ask:

- Which Hermes module is the **closest analogue** to each Ember True Name?
- Where does Hermes have a concept Ember has not yet named?
- Where does Ember have a True Name Hermes has not yet recognized as a distinct boundary?
- And — most importantly — **what new names does this parallel exercise propose?** (I propose, the Cartographer's `[[60_synthesis/61_TRUE_NAME_REASSIGNMENT]]` decides.)

Naming is not bureaucracy. Naming is what keeps a system from growing into a thicket. Hermes's `agent/` directory is a *cautionary instance* of what happens when names accumulate without a True-Name discipline — `chat_completion_helpers.py`, `tool_dispatch_helpers.py`, `tool_executor.py`, `tool_guardrails.py`, `tool_result_classification.py` are five different files in one directory, each with a slightly different mandate, none of which were given a load-bearing name. By the time you read this in 2027, there are probably eight of them. The Skald's instinct is to draw circles. Hermes did not.

## II. Funi — the flame, the local model runtime

**Hermes analogues:** Funi has *no exact analogue in Hermes*, and that is significant.

Hermes does not have a sharply named "the local model" subsystem because *Hermes is not opinionated about where the model runs*. The model is just whatever endpoint the active `ProviderProfile` points at — OpenRouter, Nous Portal, OpenAI, Anthropic, a custom URL, or an Ollama server. The closest things you'll find are:

- **`providers/`** (`AGENTS.md:551-563`) — the abstract base for provider profiles. Tiny.
- **`plugins/model-providers/<name>/`** — the per-provider plugins (openrouter, anthropic, gmi, deepseek, nvidia, …). One plugin per provider.
- **`agent/anthropic_adapter.py`, `agent/bedrock_adapter.py`, `agent/codex_responses_adapter.py`, `agent/gemini_native_adapter.py`, `agent/gemini_cloudcode_adapter.py`** — the model-shape adapters that translate between OpenAI-format messages and provider-specific shapes.
- **`agent/conversation_loop.py`** (4,094 lines) — the thing that *calls* the model, threaded with interrupt checks, budget tracking, tool dispatch.

Funi is the flame. Hermes does not have a flame because Hermes is the *roof over the flame* — it cares only that something burning is reachable through an OpenAI-compatible API. **That is fine for Hermes and wrong for Ember.** Ember's whole posture (small, tethered, runs on a Pi) requires Funi to be a *named, opinionated, intentionally-small* runtime that owns the local case.

**Proposed Funi posture, in light of Hermes:**

- Funi owns *one local runtime*. Default: Ollama. Probable secondary: llama.cpp via its OpenAI-compatible HTTP shim. *No more.*
- Funi may *call* a remote runtime through Strengr (the cord), but Funi does not abstract over remote runtimes. The remote case is Strengr's case. The split is sharp.
- Funi is responsible for the *streaming path* (Ember's `funi_prompt.assemble(..., well_disconnected=True)` at slice 2), for backpressure on the small device, and for refusing to load when the device cannot host the model.

The Cartographer will draw the actual line in `[[60_synthesis/61_TRUE_NAME_REASSIGNMENT]]`. The Skald's note here is: **Funi is a True Name Hermes refuses to commit to**, and that refusal is the source of much of Hermes's complexity. Ember should hold the line.

## III. Strengr — the tether, the cord, the network layer

**Hermes analogues:** Strengr is the True Name with the *most* Hermes evidence to study, because Hermes is the bigger system and has fought every battle the network layer can fight. The relevant Hermes modules are:

- **`agent/credential_pool.py`** (1,955 lines) — multiple API keys for one provider, `least_used` rotation, 401-failure rotation, thread-safe pooling. Strengr should *learn* this pattern but flatten it to one provider with N credentials.
- **`agent/retry_utils.py`** — retry behaviour for inference calls.
- **`agent/rate_limit_tracker.py`** — track and respect provider rate limits.
- **`agent/error_classifier.py`** — classify failures (transient / retryable / fatal / quota / auth / 4xx vs 5xx). This is *exactly* the eight-reason classification Ember's pgvector adapter does, generalized to the inference layer.
- **`agent/stream_diag.py`** — diagnose streaming failures: inner cause, upstream headers, bytes/elapsed on every drop (`RELEASE_v0.14.0.md:159`).
- **`agent/secret_sources/`** (a subdirectory) — credential resolution from environment, config, OS keychain, Bitwarden (the `test_bitwarden_secrets.py` file exists), etc.
- **`agent/transports/`** (a subdirectory) — the actual HTTP and SSE transport layer.

These together are Strengr's training set. The mapping is:

| Hermes module | Strengr concern |
|---|---|
| `credential_pool.py` | auth + rotation |
| `retry_utils.py` | retry |
| `rate_limit_tracker.py` | budget |
| `error_classifier.py` | typed-failure taxonomy |
| `stream_diag.py` | observable network failures |
| `secret_sources/` | credential plumbing |
| `transports/` | transport |

**Proposed Strengr expansion (proposal only — `[[60_synthesis/61_TRUE_NAME_REASSIGNMENT]]` decides):**

Strengr is currently described as "Network layer to the Well — auth, health, retry" (`SHARED_CONTEXT.md:25`). The Hermes parallel suggests Strengr's real surface is six concerns:

1. **Auth** — credential resolution and rotation
2. **Health** — known-good / known-bad / unknown state of the tether
3. **Retry** — with rate-aware backoff
4. **Classify** — typed failure modes (Ember's slice-2 pgvector adapter already has eight reasons; Strengr should generalize)
5. **Stream** — backpressure and resumable streaming where the protocol allows
6. **Observe** — every failure observable enough that Hjarta and `ember doctor` can diagnose without log-spelunking

This is not a rename. This is a *fuller statement* of what Strengr is. The True Name "cord, tether" survives unchanged.

## IV. Brunnr — the well, the pluggable storage adapter

**Hermes analogues:** This is the messy parallel, because Hermes does not have a Brunnr in Ember's sense.

What Hermes does have:

- **`hermes_state.py`** (3,273 lines) — the SQLite session database. FTS5 full-text search across past conversations. Session titles. Per-session JSON snapshots (off by default; the SQLite DB is canonical, per `CONTRIBUTING.md:213`). **One backend. SQLite-bound. Not pluggable.**
- **`agent/memory_manager.py`** (609 lines) — orchestrates the pluggable *memory providers*. **This is the pluggable layer in Hermes.**
- **`agent/memory_provider.py`** — the ABC for memory providers. `sync_turn`, `prefetch`, `shutdown`, `post_setup`.
- **`plugins/memory/<name>/`** — the eight built-in providers (honcho, mem0, supermemory, byterover, hindsight, holographic, openviking, retaindb).

**This parallel deserves a careful Skald note.** Hermes's pluggable layer is *memory*, where "memory" means *long-form persona / dialectic / fact recall about the user*. Hermes's *storage* layer is fixed (SQLite session DB) and is not designed to be swapped.

Ember's Brunnr is **storage**, not "memory." Brunnr is where chunked, embedded knowledge lives. Brunnr can be local SQLite + sqlite-vec, or remote PostgreSQL + pgvector, or Qdrant, or Chroma, or LanceDB. *Every backend is a first-class peer.* The Vow of Pluggable Storage is one of Ember's strongest commitments.

These are different abstractions. The Cartographer's `[[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]]` will lay this out in a table. For the Skald, the conclusion is:

> Hermes's "pluggable memory" is *not* a parallel to Ember's "pluggable Brunnr." They are different commitments at different layers. **Hermes is more flexible at the persona/dialectic layer and less flexible at the storage layer; Ember is the inverse.** Reading Hermes's memory plugins for Brunnr design would be a categorical error.

What Brunnr *can* learn from Hermes: the **ABC + orchestrator + per-plugin-directory** pattern (`AGENTS.md:514-573`) is exactly the shape Brunnr already has (`BrunnrHandle` Protocol + sqlite_vec / pgvector adapters per slice 2). The shape is confirmed by the parallel. The *substance* of what is being plugged in is different.

**Proposed Brunnr posture:**

- Brunnr is **storage of chunked, embedded knowledge**, period. Always pluggable. Always typed return values for failures. Currently two adapters (sqlite_vec, pgvector); three planned (Qdrant, Chroma, LanceDB).
- Whatever Hermes calls "memory" (`agent/memory_manager.py`) is *not* Brunnr. It might, eventually, be a separate True Name — see §VII below.

## V. Smiðja — the forge, the ingest pipeline

**Hermes analogues:** Smiðja parallels are scattered, because Hermes does not really have a dedicated ingest pipeline in Ember's sense. Hermes pulls knowledge in *at agent runtime*, through tool calls, into the *conversation context*. Hermes does not bulk-ingest a corpus and embed it for retrieval. The closest Hermes equivalents are:

- **`agent/context_engine.py`** + `plugins/context_engine/` — the context engine plugins. These shape what goes into the prompt at runtime, not what goes into storage.
- **`agent/context_references.py`, `agent/subdirectory_hints.py`** — heuristics about which files in a project are relevant to the current turn. *Conversational* context-building, not ingest.
- **`tools/web_tools.py`** (`web_search`, `web_extract`) — pulls web content into a tool result, which then enters the conversation. Not ingest into long-term storage.
- **`trajectory_compressor.py`** (65 KB at top level) — this is the *closest* Hermes analogue to Smiðja, but for *trajectories* (training-data transformation) rather than for *content ingestion*. The Forge will dig into this in `[[30_execution/35_TRAJECTORY_COMPRESSION]]`.
- **The "watchers" optional skill** (`RELEASE_v0.14.0.md:60`) — RSS / HTTP JSON / GitHub polling via cron `no_agent` mode for change detection. This is the closest Hermes gets to a content-watching pattern, and it's a skill, not a subsystem.

**Smiðja is a True Name Ember has, that Hermes does not have a parallel for.** This is significant. Hermes does not have a Smiðja because Hermes does not have a Brunnr-as-storage; without a Well to pour content into, there is nothing for a forge to do. Ember has both, in unity, and the symmetry is part of Ember's identity.

**Proposed Smiðja posture, sharpened by the Hermes contrast:**

- Smiðja's job is **chunk + embed + deposit into Brunnr**. Period.
- Smiðja explicitly does *not* do procedural memory in the Hermes sense. It does *not* curate. It does *not* archive. It does *not* let the agent author skills.
- Smiðja *may* eventually grow a "watcher" pattern (cron-driven content sources), but that is a Smiðja affordance, not a separate skills layer.
- Smiðja's content sources will include: local files (slice 1, done), URLs (planned), the operator's existing knowledge stores (planned), Project Nomad (planned).

## VI. Hjarta — the heart, the first-run setup rite

**Hermes analogues:** Hermes has the cleanest first-run / setup / diagnostic patterns we will find anywhere.

- **`hermes_cli/setup.py`** — the interactive setup wizard. Walks the user through provider choice, API key entry, toolset selection, gateway setup, and skill/memory provider activation in one conversation.
- **`hermes_cli/doctor.py`** — `hermes doctor`, the single command for "is everything okay?" Plain-English output, no log-spelunking required (the Hermes README says so explicitly at line 77).
- **`hermes_cli/auth.py`** — provider resolution, OAuth, Nous Portal.
- **`hermes_cli/main.py::_apply_profile_override()`** — the profile system. Each profile gets its own fully isolated `HERMES_HOME` directory (`AGENTS.md:893-946`). This is *not* what Hjarta does, but it is *adjacent to Hjarta's concerns* — Hermes's profile system is what lets you wire one Hermes installation for two different contexts (work / personal, coder / writer).
- **`hermes_cli/curses_ui.py`** — the preferred UI for new interactive menus (`AGENTS.md:954-959`).

Hjarta's current scope is "first-run setup rite — the conversation that wires Funi to Strengr to Brunnr the first time someone meets Ember" (`SHARED_CONTEXT.md:30`). The Hermes parallel suggests Hjarta's job grows over time to include:

- The first-run wizard *(current scope)*.
- An *ongoing* `ember doctor` — Ember already has this at slice 2.
- A *profile* concept — *probably out of scope for v1*, but the Hermes pattern is there as a teacher if Ember ever needs it.
- A *re-setup* — `ember setup` for "I have a new Well, rewire me." Ember currently does this via config edits; the Hermes wizard pattern is cleaner.

**Proposed Hjarta posture:**

- Hjarta's core remains the first-run rite. Confirmed.
- Hjarta's surface *grows to include the doctor* (the Vow of Public-Friendliness is reinforced by every Hermes pattern in this area).
- A `re-setup` / `repair` rite is *worth considering* in a later slice — but is not in Hjarta's slice-1/2 charter.

## VII. Munnr — the mouth, the CLI / interaction surface

**Hermes analogues:** Hermes has *many* mouths, and Ember should learn from one of them while refusing the others.

- **`cli.py`** (14,560 lines, `wc -l`) — the classic prompt_toolkit-based CLI. Hermes's CLI is a massive, feature-rich, multi-purpose surface with skin engine, slash command autocomplete, Rich-based banners, KawaiiSpinner activity feed, etc. *Munnr should not become this.*
- **`hermes_cli/commands.py::COMMAND_REGISTRY`** — the *one piece* of `cli.py`'s ecosystem Ember should study with attention. A single `CommandDef` list drives the CLI, the gateway dispatch, the Telegram BotCommand menu, the Slack `/hermes` subcommands, the autocomplete, and the help text (`AGENTS.md:152-194`). This is the single-source-of-truth pattern at its best.
- **`ui-tui/`** (Ink + React) and **`tui_gateway/`** (Python JSON-RPC backend) — the modern TUI. *Munnr does not grow here.*
- **`gateway/`** + `gateway/platforms/*` — the 22 messaging surfaces. *Munnr does not grow here.*
- **`hermes_cli/web_server.py`** + the dashboard — *Munnr does not grow here.*

Munnr in v1 is the plain CLI. That is correct. The Hermes parallel says: **whatever Munnr will eventually be, the COMMAND_REGISTRY pattern is the right shape for command-table-driven UI, and it should be in place from the start so that future surfaces inherit cleanly.**

**Proposed Munnr posture:**

- Munnr is the CLI surface, period, in v1.
- Munnr should adopt a single command-table data structure (analogous to Hermes's `COMMAND_REGISTRY`) *now*, even if it has only ten commands, because the cost is small and the future option is large.
- Munnr does *not* grow a TUI, a dashboard, a gateway, a messaging adapter, or a web server in v1. If Ember ever needs one of these, the Vow of Public-Friendliness will be the test — the new surface must be *as plain and as simple* as the existing CLI.

## VIII. The empty spaces — what Hermes has that Ember has not yet named

This is the most generative part of the document. Hermes has several conceptual loci that *do not map to any current True Name*. Each is a candidate either for (a) absorption into an existing True Name, (b) explicit refusal, or (c) a new True Name.

### (a) Iteration budget — `agent/iteration_budget.py`

Hermes tracks how many tool-calling iterations a single agent turn is allowed to take, plus a one-turn grace call (`AGENTS.md:122-136`). This is a *cognitive economy* concept. Ember will need it eventually.

**Proposal:** absorb into Funi as a constraint Funi enforces on its own loop. *Not* a new True Name. Funi already owns the local reasoning loop.

### (b) Curator — `agent/curator.py`

Hermes's background skill-maintenance system. Tracks usage on agent-authored skills and auto-archives stale ones. Specific invariants: never deletes, max destructive action is archive; only touches `created_by: "agent"` provenance (`AGENTS.md:751-781`).

**Proposal:** **explicit refusal**. The curator is the keystone of the agent-authored-procedural-memory pattern Ember has decided not to grow. No True Name. The Auditor's `[[50_verification/52_ANTIPATTERN_CATALOG]]` enumerates the consequences.

### (c) Toolsets — `toolsets.py::TOOLSETS`

Hermes groups its 40+ tools into 30+ named toolsets (browser, clarify, code_execution, cronjob, debugging, delegation, file, image_gen, kanban, memory, messaging, search, terminal, todo, web, …). Each platform's adapter picks a base toolset. Per-platform enable/disable via `tools.<platform>.enabled` (`AGENTS.md:698-714`).

**Proposal:** absorb into a *combined Funi-Munnr concern* — Funi exposes only the tools available; Munnr surfaces enable/disable. Ember's slice-2 tool framework already has this shape in nascent form ("tool framework + first three tools" per `SYSTEM_VISION.md §10`). *Not* a new True Name.

### (d) Plugins — `hermes_cli/plugins.py` + `plugins/<name>/`

Hermes's plugin manager. Discovers plugins from `~/.hermes/plugins/`, `./.hermes/plugins/`, and pip entry points. Each plugin exposes `register(ctx)` to register tools, hooks (`pre_tool_call`, `post_tool_call`, `pre_llm_call`, `post_llm_call`, `on_session_start`, `on_session_end`), and CLI subcommands.

**Proposal:** *defer*. Ember is small enough that the plugin surface is not yet required. When (and only when) the third sibling project (bifrost, etc.) needs to attach to Ember, the plugin pattern is what Ember should grow. Until then, the Vow of Smallness wins. *Not yet a True Name; possibly never one.*

### (e) Delegation — `tools/delegate_tool.py` + `agent/...`

Hermes can spawn subagents for parallel workstreams. `role="leaf"` (default) cannot itself delegate; `role="orchestrator"` can. Bounded by `delegation.max_spawn_depth` (default 2) and `delegation.max_concurrent_children` (default 3). Each subagent has an isolated context + terminal session (`AGENTS.md:716-748`).

**Proposal:** *refuse for now, study for later*. Ember is a small mind, not a colony. Multi-agent is a Runa concern (her parent project), not an Ember one. The Forge's `[[30_execution/32_MULTI_DEVICE_ORCHESTRATION]]` will note the pattern *as available teaching*, not as a roadmap item.

### (f) Cron — `cron/jobs.py` + `cron/scheduler.py`

Hermes's scheduler. Five-field cron, durations ("30m"), "every" phrases, ISO timestamps. Per-job fields include `skills`, `model`, `provider` overrides, `script` (pre-run data-collection script whose stdout is injected into the prompt; `no_agent=True` turns the script into the entire job), `context_from` chaining, `workdir`, multi-platform delivery (`AGENTS.md:784-817`).

**Proposal:** *defer, but the watchers / no_agent pattern is genuinely small and worth Smiðja consideration*. A future Smiðja affordance could be "watch this URL for changes; deposit any new content into Brunnr automatically." That is a Smiðja concern, not a new True Name. The Forge will explore in `[[30_execution/37_SCHEDULING_DELEGATION]]`.

### (g) Profiles — `hermes_cli/main.py::_apply_profile_override()`

Hermes profiles isolate multiple full Hermes instances, each with its own `HERMES_HOME` directory. `_apply_profile_override()` sets `HERMES_HOME` before any module imports. All `get_hermes_home()` references automatically scope to the active profile (`AGENTS.md:893-946`).

**Proposal:** *defer*. Ember's Vow of Flexible Roots already gives most of what profiles deliver. If a user wants two Embers, they clone the repo to two directories. Profiles add complexity. *Possibly* a future Hjarta affordance ("ember setup --as <name>") but not a v1 concern.

### (h) Approval / dangerous-command detection — `tools/approval.py`

Hermes's approval gate. Regex-based dangerous-command detection. Per-session approval. Sudo brute-force block. Symlink-resolution before access control (`AGENTS.md:785-790`, `CONTRIBUTING.md:777-801`, `RELEASE_v0.14.0.md:68`).

**Proposal:** absorb into Funi (as the agent-loop layer that gates tool invocations). Ember's slice-2 tool framework already has a refuses-but-survives shape per `SYSTEM_VISION.md §11`. The Auditor's `[[50_verification/54_SECURITY_REVIEW]]` will detail what Ember should adopt from Hermes here. *Not* a new True Name; the security concern belongs to Funi (it's part of "what the flame does when asked to act").

## IX. Summary table — Hermes modules to True Names

A consolidated map. The Cartographer's `[[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]]` will produce the full version; this is the Skald's draft.

| Hermes module/concept | Ember True Name | Notes |
|---|---|---|
| `providers/`, `agent/<provider>_adapter.py` | **Funi** (local) + **Strengr** (remote) | Hermes does not split; Ember does. |
| `agent/conversation_loop.py` | **Funi** | The local reasoning loop. |
| `agent/iteration_budget.py`, `agent/prompt_caching.py` | **Funi** | Cognitive economy concerns. |
| `tools/approval.py`, `agent/tool_guardrails.py` | **Funi** | Action-gating concerns. |
| `agent/credential_pool.py` | **Strengr** | Auth + rotation. |
| `agent/retry_utils.py`, `agent/rate_limit_tracker.py` | **Strengr** | Retry + budget. |
| `agent/error_classifier.py` | **Strengr** | Typed failure taxonomy. |
| `agent/stream_diag.py` | **Strengr** | Observable network failures. |
| `agent/secret_sources/`, `agent/transports/` | **Strengr** | Credential and transport plumbing. |
| `hermes_state.py` (SQLite) | *no direct analogue* | Hermes's session DB is one-backend; Ember has no equivalent — sessions live in Brunnr or in-memory in Ember. |
| `agent/memory_manager.py` + `plugins/memory/*` | *no direct analogue (yet)* | Hermes's "memory" is persona/dialectic. Ember has not yet named this distinct from Brunnr; **possible future True Name** if Ember grows persona modeling. |
| Brunnr-equivalent storage backends in Hermes | *none* | Hermes is SQLite-bound at the session layer. |
| `agent/context_engine.py`, `agent/context_references.py` | *cross-cuts* | Conversational context-building, not a True Name. |
| `tools/web_tools.py` | **Smiðja** (eventually) | Currently a tool, but the watcher/ingest pattern is Smiðja's. |
| `trajectory_compressor.py` | *out of scope* | Research instrument; Ember doesn't do this. |
| `hermes_cli/setup.py` | **Hjarta** | The first-run wizard pattern. |
| `hermes_cli/doctor.py` | **Hjarta** (extended) | Doctor as ongoing Hjarta affordance. |
| `cli.py` (the 14,560-line monster) | **Munnr** (in shape only, not in scale) | Munnr is plain. |
| `hermes_cli/commands.py::COMMAND_REGISTRY` | **Munnr** | The command-table pattern. |
| `ui-tui/` (Ink TUI) | *refused* | Not a Munnr concern. |
| `gateway/`, `gateway/platforms/*` | *refused* | Not an Ember concern at v1. |
| `tui_gateway/` | *refused* | Not an Ember concern at v1. |
| `agent/curator.py` | *refused* | Antipattern for Ember's Vow of Honest Memory. |
| `tools/delegate_tool.py` | *refused* | Multi-agent is a Runa concern. |
| `cron/jobs.py`, `cron/scheduler.py` | *deferred* | Possibly a Smiðja affordance later. |
| `hermes_cli/plugins.py`, `plugins/*` | *deferred* | Smallness wins until a sibling project demands it. |
| `hermes_cli/main.py::_apply_profile_override()` | *deferred* | Flexible Roots covers most cases. |
| `tools/skill_tools.py`, `skills/`, `optional-skills/` | *refused as procedural-memory pattern; **possibly** repurposed as Smiðja content sources* | The Auditor decides. |
| `acp_adapter/`, `acp_registry/` | *out of scope for v1* | Editor integration is a far-future Ember concern. |
| `mcp_serve.py`, `agent/...` MCP plumbing | *out of scope for v1* | MCP is a far-future Ember concern. |

## X. Names Ember might want, that Hermes pressure suggests

Three candidate names. **I propose; the Cartographer's `[[60_synthesis/61_TRUE_NAME_REASSIGNMENT]]` decides.**

1. **A name for the persona / dialectic / user-model layer.** Hermes's `agent/memory_manager.py` plus its pluggable memory providers occupy a real conceptual locus that is *not* Brunnr (storage) and *not* Hjarta (first-run). If Ember ever grows a persona-aware loop — and the Vow of Honest Memory does not preclude it — she will want a name. *Candidate Old Norse names: **Hugr*** (Old Norse: "mind, thought, mood"), or ***Mynd*** ("image, semblance, picture") — the inner model of the operator that Ember holds *honestly*. Held back from True-Name commitment until needed; the slot is *named in this Codex* so it does not get filled accidentally by a worse name.

2. **A name for the observability / health / diagnostic layer.** Hermes has `hermes doctor`, `hermes_logging.py`, `agent/stream_diag.py`, `agent/insights.py`. Ember has `ember doctor` and typed `Disconnected` values flowing through. There may eventually be enough here to warrant a True Name. *Candidate: **Auga*** (Old Norse: "eye, sight") — the eye that watches Ember herself. Currently absorbed into Hjarta and Strengr; held in reserve.

3. **A name for the action-gate / dangerous-command boundary.** Hermes has `tools/approval.py` and a security policy rewritten around OS-level isolation as the boundary. Ember's slice-2 tool framework has a refuses-but-survives shape. If this layer grows, a True Name might be warranted. *Candidate: **Vörðr*** (Old Norse: "warden, guardian") — the warden at the gate. Currently absorbed into Funi; held in reserve.

These three are *proposals only*. The Skald does not assign True Names unilaterally — that authority belongs to the synthesis pass (`[[60_synthesis/61_TRUE_NAME_REASSIGNMENT]]`) and ultimately to the operator. The Skald's job is to *name the slot* before something worse fills it.

## What This Means for Ember

The naming-parallel exercise yields concrete proposals.

- **Funi**: confirmed boundary. The local model runtime, period. Hermes's lack of an equivalent True Name *is* the lesson. The Vow of Smallness is reinforced by every Hermes provider abstraction we did not adopt.

- **Strengr**: confirmed boundary, with a fuller statement of surface (auth, health, retry, classify, stream, observe). The Vow of Tethered Grounding and the Vow of Graceful Offline are both reinforced. Strengr should *study* `agent/credential_pool.py`, `agent/retry_utils.py`, `agent/rate_limit_tracker.py`, `agent/error_classifier.py`, and `agent/stream_diag.py` as teachers, not templates.

- **Brunnr**: confirmed boundary. Hermes's lack of a pluggable storage layer at Brunnr's level *is* the lesson. The Vow of Pluggable Storage is reinforced.

- **Smiðja**: confirmed boundary. Hermes's lack of an ingest forge *is* the lesson. The Vow of Open Knowledge is reinforced by Smiðja's intent to ingest open content (local files, URLs, Project Nomad).

- **Hjarta**: confirmed boundary, with the doctor pattern absorbed as an ongoing Hjarta affordance. Hermes's `hermes setup` + `hermes doctor` patterns are exemplary. The Vow of Public-Friendliness is reinforced.

- **Munnr**: confirmed boundary. **Adopt the `COMMAND_REGISTRY` single-source-of-truth pattern now**, even if Munnr has only ten commands. The Vow of Public-Friendliness is reinforced by every Hermes single-registry move.

- **Three reserved name-slots** (Hugr / Mynd / Auga / Vörðr) — held back from True-Name commitment; *named* so they cannot be filled accidentally. The Cartographer decides if any are promoted.

**Vows touched:**

- **Vow of Smallness** — reinforced by every refusal in §VIII.
- **Vow of Pluggable Storage** — reinforced by the Brunnr / Hermes-memory contrast.
- **Vow of Tethered Grounding** — reinforced by the Funi / Strengr split that Hermes does not make.
- **Vow of Graceful Offline** — reinforced by the typed-failure-taxonomy proposal for Strengr.
- **Vow of Public-Friendliness** — reinforced by the Hermes `setup` and `doctor` patterns Hjarta absorbs.
- **Vow of Honest Memory** — reinforced by the explicit refusal of the `curator.py` / skill-authoring pattern.
- **Vow of Modular Authorship** — reinforced by adopting the *shape* of Hermes's plugin discipline (ABC + orchestrator + per-plugin directory) without the specific implementations.

The names are drawn. The Architect maps the territory next.

— Sigrún Ljósbrá

---
codex_id: 01_HERMES_ESSENCE
title: Hermes Essence — What It Wants to Be
role: Skald
layer: Vision
status: draft
hermes_source_refs:
  - README.md:15-28
  - AGENTS.md:83-140
  - AGENTS.md:262-310
  - AGENTS.md:487-585
  - AGENTS.md:716-815
  - AGENTS.md:861-887
  - agent/credential_pool.py
  - agent/conversation_loop.py
  - agent/curator.py
  - agent/memory_manager.py
  - hermes_state.py
  - hermes-already-has-routines.md:1-160
  - RELEASE_v0.14.0.md:1-90
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 00_vision/00_OVERTURE
  - 00_vision/02_NAMING_PARALLELS
  - 00_vision/03_ANTI_HERMES
  - 10_domain/10_DOMAIN_MAP
  - 30_execution/30_SELF_HEALING_LOOP
  - 30_execution/41_MULTI_PROVIDER_FAILOVER
---

# Hermes Essence — What It Wants to Be

> *Every system has a self it is reaching for. Read the code long enough and the self begins to show through the bones.*

## I. The seven sentences

If I had to give you the whole essence of Hermes Agent in seven sentences, this is what I would write. Everything else in this document is justification.

1. **Hermes wants to be a single agent you can reach from anywhere, that talks to any model, that runs on any computer.**
2. **Hermes wants to learn — not just per-conversation, but across conversations, by writing skills it can re-load, by curating its own procedural memory, and by training data its parent can use to fine-tune the next generation of tool-calling models.**
3. **Hermes wants to be cheap when idle and capable when active**, which is why it ships seven terminal backends, two of which (Modal, Daytona) hibernate to near-zero cost between sessions.
4. **Hermes wants to be its own laboratory**, which is why every subsystem is plugin-shaped — memory providers, model providers, context engines, image-gen providers, plugins themselves — and why the contributor docs make "build it as a plugin first" a stronger default than "patch the core."
5. **Hermes wants to be modeled provider-agnostic**, not just compatible-with, which is why `_PROVIDER_MODELS` ships hundreds of model identifiers and why a single config edit reroutes inference across vendors without code changes.
6. **Hermes wants to be present on every channel humans already use** — Telegram, Discord, Slack, WhatsApp, Signal, LINE, SimpleX, Teams, Email, SMS, plus its own CLI / TUI / dashboard — because the assumption is that *humans live in chat, so the agent should live there too*.
7. **Hermes wants to be honest about scale**, which is why it has a closed-model security boundary based on OS-level isolation, why it has prompt-injection scanners for cron jobs, why it has dependency upper-bound rules to survive supply-chain attacks, and why the project has explicitly *refused* to centralize all memory plugins into its own repo.

That is the self Hermes is reaching for. Everything else, the line counts and the toolset dicts and the 215 community contributors, is in service of those seven sentences.

The harder question — and the one the Vow-reading must answer — is: **what is Hermes hiding from itself?** What does the code know that the marketing prose doesn't say? That is what the rest of this document is for.

## II. The secret Hermes does not state

The README states the loop. The AGENTS treatise states the architecture. The release notes state the deltas. None of them states the *secret of the project*, which only becomes visible after reading a few hundred lines of `agent/` and a thousand lines of `cli.py`. The secret is this:

> **Hermes is a research instrument shaped like a product.**

It is shipped, MIT-licensed, supported with a public Discord, and used. It is also — visibly, in the code, in the directory structure, in the very existence of `trajectory_compressor.py` at 65 KB — a *trajectory generator for Nous Research's next generation of tool-calling models*.

The README admits this in one line near the bottom: *"Research-ready: Batch trajectory generation, trajectory compression for training the next generation of tool-calling models"* (`README.md:26`). The AGENTS treatise has a `batch_runner.py` (57 KB) for parallel batch processing. The `cron/` subsystem can run jobs in `no_agent=True` mode where a script *is* the entire job (used for the `watchers` skill family). The `optional-skills/autonomous-ai-agents/` and `darwinian-evolver` skill direct the agent to *evolve its own prompts and skills*.

Every brilliant piece of Hermes — the closed learning loop, the skill auto-creation, the curator that archives stale skills, the cross-session prompt caching, the agent-authored memory — *also generates data*. The agent's trajectories are recorded. Skills the agent writes are recorded. The compression pipeline transforms those trajectories into training data for the next model.

This is not a criticism. It is, in fact, the most architecturally honest thing about Hermes: it is a usefully-shaped data flywheel, and the people who built it know that. *That* is the project's animating force.

Why does this matter for Ember? Because **Ember is not a research instrument**. Ember is a personal hearth for a person on a small device. If Ember reads Hermes naively, she will absorb the data-flywheel architecture as if it were a neutral default. It isn't. It serves a specific purpose for a specific organization at a specific scale. Ember will not generate trajectories for fine-tuning. Ember will not bundle 70 skills hoping the agent uses each of them and records the outcome. Ember will not, in her first thousand commits, *curate herself*. The Vow of Honest Memory and the Vow of Smallness together refuse this entire pattern in Ember's body, and reading Hermes is what reveals why those Vows had to be written that way.

This is the secret. Now to the bones.

## III. The five essences (and their evidence)

Hermes has five essences I am willing to name explicitly. Each comes with citations.

### Essence 1 — The closed learning loop

The README leads with this and the code supports it. The loop has three observable elements:

- **Skills as procedural memory.** `skills/` ships ~70 bundled skills across 25+ categories. `optional-skills/` adds 18 more categories of niche capability (`optional-skills/DESCRIPTION.md:1-25`). Skills are markdown SKILL.md files with frontmatter, scripts, references, and templates. Agents can author skills via tools (`tools/skill_tools.py`, referenced in `CONTRIBUTING.md:478-528`).
- **Curator.** `agent/curator.py` runs a background review loop that auto-archives stale agent-authored skills (`AGENTS.md:751-781`). The invariants are sharp: never touches bundled or hub-installed skills, never deletes (max destructive action is archive), pinned skills are exempt from auto-transitions. `tools/skill_usage.py` keeps the sidecar telemetry — `use_count`, `view_count`, `patch_count`, `last_activity_at`, `state` — at `~/.hermes/skills/.usage.json`.
- **Cross-session memory.** `agent/memory_manager.py` is small (609 lines) because it orchestrates pluggable providers (`agent/memory_provider.py` ABC). The providers — `honcho, mem0, supermemory, byterover, hindsight, holographic, openviking, retaindb` (`AGENTS.md:514-520`) — implement `sync_turn(turn_messages)`, `prefetch(query)`, `shutdown()`, and optional `post_setup(hermes_home, config)`. `hermes_state.py` (3,273 lines) handles SQLite session persistence with FTS5 full-text search across past conversations.

These three together — skills, curator, memory — *are* the closed learning loop. The loop is observable, instrumented (`tools/skill_usage.py`), and self-correcting (the curator).

Ember inherits the **idea** of the loop. Ember does not inherit the *mechanism*. The Forge's `[[30_execution/30_SELF_HEALING_LOOP]]` will detail this.

### Essence 2 — Provider-agnostic at industrial scale

The README claims "200+ models" and the code makes good on it. The `providers/` directory holds the base abstraction; the actual provider profiles live as **plugins** in `plugins/model-providers/<name>/` (`AGENTS.md:549-573`), each calling `providers.register_provider(ProviderProfile(...))` at module load. The discovery is lazy — scanned on first `get_provider_profile()` or `list_providers()` call — *not* by the general PluginManager (`AGENTS.md:556-557`). Scan order is bundled, then user, then legacy (`AGENTS.md:559-562`). User plugins override bundled by last-writer-wins (`AGENTS.md:564-566`). Third parties can swap out any built-in profile without a repo patch.

Underneath that, `agent/credential_pool.py` (1,955 lines) lets the user wire **multiple API keys for the same provider** with automatic rotation (`RELEASE_v0.7.0` Highlights). The strategy is thread-safe `least_used`; 401 failures trigger automatic rotation. `agent/auxiliary_client.py::_resolve_auto` (referenced in `AGENTS.md:352`) resolves which provider handles which auxiliary task — curator, vision, embedding, title generation, session_search — each pinnable to its own provider/model/base_url/max_tokens/reasoning_effort.

The model catalog in `_PROVIDER_MODELS` is hardcoded and explicitly *not* allowed to be a snapshot in tests (`AGENTS.md:1094-1127`) — the contributor guide bans "change-detector tests" because the catalog *is expected to change*. New providers land as plugins; new models land as data; tests assert relationships, not contents.

This essence is **deeply right** at Hermes's scale and **deeply wrong** at Ember's. Ember speaks one model at a time, through one tether. The plugin-shaped provider abstraction will not be Strengr's body. Strengr is a cord, not a router.

### Essence 3 — Anywhere, including nowhere — the cost-near-zero shape

This is the most original of Hermes's essences and the one Ember can learn the most from without copying.

Hermes ships **seven terminal backends** (`AGENTS.md:35`, `README.md:25`):

- **Local** — your machine, your processes.
- **Docker** — sandboxed, capabilities-dropped, no-privilege-escalation, PID-limited, tmpfs-bounded (`CONTRIBUTING.md:790`).
- **SSH** — drive a remote box through SSH.
- **Singularity** — for HPC environments.
- **Modal** — serverless, dormant when idle.
- **Daytona** — serverless dev environments with offered persistence.
- **Vercel Sandbox** — ephemeral cloud sandboxes.

The Modal and Daytona backends are the load-bearing pieces of the "$5 VPS or GPU cluster" claim. The agent's environment **hibernates when idle** and **wakes on demand** (`README.md:25`). You pay near-zero between sessions; you pay for compute only when the agent is awake. The gateway runs perpetually somewhere (a tiny VPS, a Pi at home), and the *expensive* part (LLM calls, terminal execution) hibernates.

That separation — *cheap-and-persistent gateway + expensive-and-hibernated worker* — is **the architectural pattern Ember should study most carefully**. It is exactly the pattern that lets a Pi 5 at home talk to a remote Well (Gungnir, in the user's case) without either side carrying the full cost of the system. Strengr is the cord between those two stations; Funi is the (tiny, local) reasoner; Brunnr is the (possibly remote, possibly hibernated) Well. The Forge's `[[30_execution/40_SERVERLESS_HIBERNATION]]` will explore this in detail.

### Essence 4 — Live where the humans live — the multi-platform gateway

The README claims "Telegram, Discord, Slack, WhatsApp, Signal, and CLI — all from a single gateway process" (`README.md:21`). The code more than makes good. `gateway/platforms/` (`AGENTS.md:39-42`) lists adapters for telegram, discord, slack, whatsapp, homeassistant, signal, matrix, mattermost, email, sms, dingtalk, wecom, weixin, feishu, qqbot, bluebubbles, yuanbao, webhook, api_server, and (as of v0.14) LINE, SimpleX, and Teams (`RELEASE_v0.14.0.md:30-31, 196-204`). That is **22 messaging surfaces** plus the CLI/TUI/Dashboard.

Each platform is a plugin under `gateway/platforms/<name>.py`, implementing a common `BasePlatform` (referenced in `AGENTS.md:973-977`). The gateway runner (`gateway/run.py`) routes messages, holds session lifecycle, intercepts `/stop`, `/new`, `/queue`, `/status`, `/approve`, `/deny` before they reach `running_agent.interrupt()`. The slash-command registry (`hermes_cli/commands.py::COMMAND_REGISTRY`, `AGENTS.md:152-194`) is *the same* central registry the CLI uses — Telegram, Slack, Discord, and CLI all derive their command surfaces from one `CommandDef` list.

The cron subsystem (`cron/jobs.py`, `cron/scheduler.py`) can deliver to *any* of these platforms (`hermes-already-has-routines.md:55-65`). The `clarify` tool surfaces native button UI on Telegram and Discord (`RELEASE_v0.14.0.md:34`). The agent itself can be in a conversation on Telegram while it's working on a Modal sandbox in another continent. This is, genuinely, beautiful work.

Ember will refuse most of it in v1 — see `[[00_vision/03_ANTI_HERMES]]`. The seed of the pattern, though, the *single command registry that drives many surfaces*, is good design. Munnr begins as the CLI; when (and if) Ember grows a second surface, the registry pattern is one Ember should already have in place. The Architect's `[[10_domain/18_HERMES_CLI]]` will catalogue the registry pattern carefully.

### Essence 5 — Be honest about scale

The most overlooked Hermes essence. Read the project's *defensive* code and you will see it.

- **Supply-chain hygiene.** Every dependency must have an upper bound. The policy was established after the litellm compromise (`AGENTS.md:319-330`, `CONTRIBUTING.md:803-842`). Git URLs require commit SHAs, not tags. GitHub Actions require commit SHAs with version comments. CI-only pip pins are `==exact`. The supply-chain-audit CI workflow flags dependency manifest changes for manual review.
- **Cross-platform discipline.** `CONTRIBUTING.md` has sixteen numbered cross-platform rules (`CONTRIBUTING.md:599-758`), including the chilling note that `os.kill(pid, 0)` *is not a no-op on Windows* — it broadcasts Ctrl+C to the entire console process group. Hermes shipped `scripts/check-windows-footguns.py` as a grep-based pre-PR linter (`CONTRIBUTING.md:596-598`).
- **Prompt-injection protection.** Cron prompts are scanned for instruction-override patterns (`AGENTS.md:787`, `CONTRIBUTING.md:790`). Tool error strings are sanitized before re-injection into the model context, so a malicious file or remote service cannot pass instructions through error output (`RELEASE_v0.14.0.md:68`).
- **Write deny lists.** Protected paths like `~/.ssh/authorized_keys` and `/etc/shadow` are resolved via `os.path.realpath()` *before* access-control checks, to prevent symlink bypass (`CONTRIBUTING.md:790`).
- **Sudo brute-force block.** The approval gate now blocks `sudo -S` brute-force attempts and classifies stdin-fed or askpass-stripped sudo invocations as DANGEROUS (`RELEASE_v0.14.0.md:68`).
- **Security policy.** Rewritten around *OS-level isolation as the boundary* (`RELEASE_v0.14.0.md:385`). The agent is not trusted; the OS sandbox is.

This essence is the one Ember should inherit *most directly*. Smallness is no excuse for naivety. The Vow of Smallness and the Vow of Public-Friendliness mean Ember will have less to defend than Hermes, but everything she does have must be defended at this level of attention. The Auditor's `[[50_verification/54_SECURITY_REVIEW]]` will trace this in detail.

## IV. The triangulation — what these five essences mean *together*

Take all five at once and the secret-shape of Hermes appears:

- **Closed learning loop** + **provider-agnostic** = the system can run on whichever model gives the best signal, and the signal is captured.
- **Cost-near-zero hibernation** + **live-where-humans-live** = the system is always reachable, never expensive.
- **Honest-about-scale defenses** = the system survives in production against real-world attacks.

This triangulation is *exactly* what a research lab wants for a self-improving agent platform. It is *exactly* what Ember is not. Ember is the opposite vector: **one model**, **one tether**, **one user**, **honest about the smallness of her loop, not the largeness of it**. Reading Hermes carefully reveals the *shape of the choice Ember made by being small*. That shape is the real gift.

## V. What Ember should inherit (preview)

A quick preview of where the rest of the Codex will land. Each is justified at length elsewhere.

- **The credential-pool concept** (`agent/credential_pool.py`) → Strengr's retry/rotation layer, but flattened from N providers to 1 provider with N possible credentials.
- **The retry/rate-limit-tracker concept** (`agent/retry_utils.py`, `agent/rate_limit_tracker.py`) → Strengr's `Disconnected` typed value already in Ember's slice-2 code; the Hermes patterns confirm the design and add specific failure-mode taxonomies Strengr should adopt.
- **The single-command-registry pattern** (`hermes_cli/commands.py::COMMAND_REGISTRY`) → Munnr's eventual command table when (and only when) Munnr grows a second surface.
- **The setup-wizard pattern** (`hermes_cli/setup.py`) → Hjarta's first-run rite. Hermes's wizard is the cleanest example we will find of "wire everything in one conversation" UX.
- **The doctor pattern** (`hermes_cli/doctor.py`) → Ember's `ember doctor` already exists; Hermes confirms the design.
- **The display_hermes_home() / get_hermes_home() split** (`hermes_constants.py`) → Ember's path layer; the *two-function split* (display vs. functional) is a discipline Ember should adopt explicitly if she has not yet.
- **The cross-platform footgun list** (`CONTRIBUTING.md:599-758`) → Ember's CONTRIBUTING; nearly every footgun on Hermes's list applies to Ember verbatim.
- **The dependency-pinning policy** (`AGENTS.md:319-330`) → Ember's `pyproject.toml` discipline.

## VI. What Ember should refuse (preview)

Detailed in `[[00_vision/03_ANTI_HERMES]]`. Summary:

- **Procedural-memory skill files** — agent-authored markdown skills are exactly the wrong shape for Ember's Vow of Honest Memory.
- **The multi-platform gateway** — Munnr is one mouth at v1.
- **The 200+-model catalog** — Funi negotiates with the local runtime; Strengr negotiates with the Well; there is no model catalog as a concept in Ember.
- **The 14,560-line CLI** — Munnr is plain; the dashboard is not in scope.
- **The seven terminal backends** — Ember has one execution surface (the device); the others are *possibly* relevant to Brunnr's remote-Well story, but as Brunnr concerns, not as terminal-execution concerns.

## What This Means for Ember

The essence reading produces concrete proposals.

- **Funi**: the True Name is correct. Funi is the flame on the device, period. Provider abstraction belongs to Strengr (for the remote case) or to nothing (for the local-Ollama case). The Vow of Smallness is the test; the v0.14 cold-start work in Hermes (`RELEASE_v0.14.0.md:94-106`) is direct evidence that even a much larger system fights for every second of launch time. Ember must protect Funi's launch path with the same discipline.

- **Strengr**: lift the *typed-value* idiom for failures (Hermes uses exceptions and retries; Ember already uses typed `Disconnected`/`Unavailable` per `SYSTEM_VISION.md §11`). Lift the *credential-pool concept* but with one provider and N credentials, not N providers. Lift the eight-reason classification idea from Ember's own pgvector adapter and extend it to Strengr's full surface. The Vow of Tethered Grounding and the Vow of Graceful Offline are both reinforced; nothing weakens them.

- **Brunnr**: confirm the design. Hermes's "pluggable memory" is *not* equivalent to Ember's "pluggable storage" (the Cartographer's `[[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]]` will draw this out). The Vow of Pluggable Storage is a stronger commitment than Hermes makes and Ember is correct to make it.

- **Smiðja**: explicitly hold back the *agent-authored procedural memory* pattern. Smiðja's job is to deposit content into Brunnr — local files, URLs, Project Nomad, the operator's existing stores — chunked and embedded. **Skills, in the Hermes sense, are not Brunnr-resident knowledge.** They are a separate parallel memory layer that Ember has decided not to grow. The Auditor's `[[50_verification/52_ANTIPATTERN_CATALOG]]` will catalogue this as an explicit antipattern for Ember.

- **Hjarta**: study Hermes's `hermes setup` wizard and `hermes_cli/setup.py` carefully. The pattern of *one conversation that wires everything* is exemplary public-friendliness. Hjarta already implements this idea at slice-1; Hermes evidence confirms the direction.

- **Munnr**: study `hermes_cli/commands.py::COMMAND_REGISTRY` as the *eventual* pattern for command-table-driven UI. Do not adopt it yet. Munnr is plain in v1.

**Vows touched:**

- **Vow of Smallness** — reinforced. Reading Hermes makes the case for smallness sharper, not weaker.
- **Vow of Tethered Grounding** — reinforced. Hermes's elaborate provider-and-memory abstraction is *the price of not being tethered to a single Well*; Ember is tethered, and is simpler in consequence.
- **Vow of Graceful Offline** — reinforced. Hermes's `Disconnected`-equivalent code path is far less rigorous than Ember's typed-value approach; we are ahead here.
- **Vow of Pluggable Storage** — reinforced. Ember commits to something Hermes does not.
- **Vow of Honest Memory** — *strongly* reinforced. The agent-authored skill pattern in Hermes is the single biggest threat to this Vow if read naively.
- **Vow of Modular Authorship** — reinforced. Hermes's plugin-shaped subsystem boundaries are educational; Ember can adopt the shape of the discipline without the specifics of the implementation.

The essence has been read. The Architect now picks up the bones.

— Sigrún Ljósbrá

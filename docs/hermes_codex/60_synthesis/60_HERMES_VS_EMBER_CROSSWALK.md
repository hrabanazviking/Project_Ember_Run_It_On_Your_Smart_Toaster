---
codex_id: 60_HERMES_VS_EMBER_CROSSWALK
title: Hermes vs Ember — Module-by-Module Crosswalk
role: Cartographer
layer: Synthesis
status: draft
hermes_source_refs:
  - agent/
  - providers/
  - gateway/
  - tui_gateway/
  - plugins/
  - skills/
  - acp_adapter/
  - mcp_serve.py
  - cli.py
  - run_agent.py
  - hermes_state.py
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/62_DEPENDENCY_FLOW
  - 60_synthesis/63_INTEGRATION_PATHS
  - 60_synthesis/64_MIGRATION_PLAN
  - 60_synthesis/67_GLOSSARY_AND_INDEX
  - 10_domain/10_DOMAIN_MAP
  - 20_interface/20_MCP_INTEGRATION
  - 20_interface/21_RPC_INTERFACE
  - 20_interface/22_SKILL_INTERFACE
  - 20_interface/23_PROVIDER_INTERFACE
---

# 60 — Hermes vs Ember: Module-by-Module Crosswalk

> *Two maps of two countries, set side by side: the borders that match, the rivers that diverge, the towns that have no counterpart.*
> — Védis Eikleið, drawing the map of maps

## 1. The shape of this crosswalk

Hermes is a 200-MB-ish codebase with ~80 modules in `agent/`, sixteen plugins, thirty-odd skill categories, and a 662-KB `cli.py`. Ember is a deliberately small codebase organised around six True Names (Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr) across three Realms (Spark, Thread, Well). Most of Hermes does not map to Ember at all, and that is correct — Ember does not want to be Hermes. Some of Hermes maps cleanly. Some maps awkwardly, and the awkwardness is where the [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] proposals live.

This document is the **complete crosswalk**. Each row is a Hermes concept; the columns are: Ember True Name that owns (or would own) the concept, current state in Ember's code, and the gap or alignment.

The columns use these tags:
- **Aligned** — Ember already has this; Hermes confirms the shape is right.
- **Gap** — Ember does not have this yet, but it fits cleanly into an existing True Name.
- **New-Name** — Ember does not have this, and it does not fit into any existing True Name; a new name is proposed.
- **Reject** — Hermes has this; Ember should not adopt it (Vow violation, complexity-for-complexity's-sake, etc.).
- **Defer** — Ember does not need this in slice 3 or 4 but may want it later.

## 2. Agent core (Hermes `agent/`)

| Hermes concept | Source path | Ember True Name | Current state | Tag |
|---|---|---|---|---|
| Conversation loop | `agent/conversation_loop.py` | Funi + Munnr | Munnr has a chat REPL; tool-loop scaffold in `spark/funi/tools/` | Aligned (partial) |
| Context engine | `agent/context_engine.py`, `context_compressor.py`, `context_references.py` | Funi | Episode-window construction in slice 2; compression not yet | Gap |
| Memory manager | `agent/memory_manager.py`, `memory_provider.py` | Brunnr + Funi | Brunnr persists Episodes; no provider plug-in API yet | Gap → New-Name candidate (see 61) |
| Prompt builder | `agent/prompt_builder.py` | Funi | `funi_prompt.assemble()` exists, slice 2 | Aligned |
| Prompt caching | `agent/prompt_caching.py` | Funi | Not yet; Ollama exposes it modestly | Defer |
| Tool dispatch helpers | `agent/tool_dispatch_helpers.py` | Funi | Tool registry + descriptor framework lives in `spark/funi/tools/` | Aligned (partial) |
| Tool executor | `agent/tool_executor.py` (910 lines) | Funi | Sequential dispatch only; no thread pool | Gap |
| Tool guardrails | `agent/tool_guardrails.py` | Funi | Approval framework + audit log in slice 2 (ADR 0011) | Aligned |
| Retry utils | `agent/retry_utils.py` | Strengr | Basic backoff in Strengr; not yet typed-policy | Gap |
| Error classifier | `agent/error_classifier.py` | Strengr | `Disconnected` typed values across boundaries | Aligned |
| Credential pool | `agent/credential_pool.py` (1,955 lines) | Strengr | Single secret resolver (keyring + env + file) in pgvector adapter | Gap (large; defer multi-key rotation) |
| Credential sources | `agent/credential_sources.py` | Strengr | Same as above | Gap |
| Provider transports | `agent/transports/{base,anthropic,bedrock,chat_completions,codex,codex_app_server,types}.py` | Funi | Single `FuniHandle` Protocol; one adapter (Ollama) | Gap (refactor target; see 63) |
| Adapter files | `agent/anthropic_adapter.py`, `bedrock_adapter.py`, `codex_responses_adapter.py`, etc. | Funi | n/a | Defer (Ember v1 = Ollama only, plus OpenAI-compatible HTTP as slice-4 candidate) |
| Display / spinner | `agent/display.py` | Munnr | Plain text output; no spinner | Defer (and possibly Reject — spinners on a Pi serial console are not friendly) |
| Trajectory | `agent/trajectory.py` + `trajectory_compressor.py` (65 KB) | Brunnr + Smiðja | Episode persistence is the analogue; no training-data export | Defer (and see 65 SLICE_PLAN_REVISIONS — this is the kind of feature that earns its place much later) |
| Onboarding | `agent/onboarding.py` | Hjarta | Hjarta is the first-run rite, already done | Aligned (Hjarta is the Ember equivalent) |
| Session DB | `hermes_state.py` (140 KB) | Brunnr | Brunnr's `episode` table is the equivalent at small scale | Aligned (smaller) |
| Title generator | `agent/title_generator.py` | Funi | Not present | Defer |
| Insights | `agent/insights.py` | Brunnr | Not present | Defer |
| Curator | `agent/curator.py` + `curator_backup.py` | Brunnr | Not present | Defer (Smiðja-adjacent; might earn a place if skill corpus grows) |
| Web search provider | `agent/web_search_provider.py` + registry | Funi (tool) | Tool placeholder exists | Defer |
| Image / video gen | `agent/image_gen_*`, `video_gen_*` | n/a | Out of scope | Reject (Vow of Smallness; Pi-class doesn't have a use) |
| LSP integration | `agent/lsp/` | n/a | Out of scope | Reject |
| Browser provider | `agent/browser_provider.py` | n/a | Out of scope for Pi default | Defer (could land as opt-in tool on workstation profile) |
| Background review | `agent/background_review.py` | Funi | Not present | Defer |
| Skill commands / preprocessing / utils / bundles | `agent/skill_*.py` | Funi (new submodule) | Not present | Gap (port the validator; see 22 SKILL_INTERFACE) |
| Markdown tables / portal tags / shell hooks / i18n / redact | `agent/*.py` (various) | mixed | Various small utilities | Defer (each is a small port that earns its way in over time) |

The columns "Aligned" or "Aligned (partial)" total nine; "Gap" totals eight; "Defer" totals twelve; "Reject" totals four. Ember's actual lift from Hermes's `agent/` is manageable — port the eight gaps, defer the twelve, ignore the four.

## 3. Providers, transports, credentials

| Hermes concept | Source path | Ember True Name | Current state | Tag |
|---|---|---|---|---|
| `ProviderProfile` declarative dataclass | `providers/base.py:38-185` | Funi | One `FuniHandle` Protocol; no profile dataclass yet | Gap (high-value port; see 23 PROVIDER_INTERFACE) |
| Provider plugin discovery (filesystem walk) | `providers/__init__.py` | Funi | Hardcoded import of Ollama | Gap (phase 2 of port) |
| `ProviderTransport` ABC | `agent/transports/base.py:16-89` | Funi | None; adapter is the transport | Gap (high-value port) |
| `NormalizedResponse` + `ToolCall` + `Usage` types | `agent/transports/types.py:18-160` | Funi | Closest analogue: the `FuniReply` dataclass in slice 2 | Aligned (with rename) |
| Chat-completions transport | `agent/transports/chat_completions.py` (629 lines) | Funi | Ollama uses native API, not OpenAI-compat HTTP | Defer; might land as an LM-Studio / llama.cpp-server adapter |
| Anthropic transport | `agent/transports/anthropic.py` (179 lines) | Funi | Out of scope for Pi default | Defer |
| Bedrock / Codex transports | `agent/transports/{bedrock,codex,codex_app_server*}.py` | Funi | Out of scope | Reject (AWS-shaped; Codex-shaped — not Ember's audience) |
| Credential pool with rotation strategies | `agent/credential_pool.py:60-200` | Strengr | One credential per provider | Defer (single-credential first; pool when household sharing demands it) |
| Removal-step contract for credential sources | `agent/credential_sources.py:1-450` | Strengr | Not present | Defer (only useful once multi-source credential loading exists) |
| Per-error-code TTL exhaustion model | `agent/credential_pool.py:75-77, 199-235` | Strengr | Not present | Gap (small port; typed values already match) |
| Provider failover (cross-provider) | `agent/credential_pool.py` (`_NEXT_PROVIDER_ON_EXHAUSTION`) | Strengr | Not present | Defer (and possibly Reject for v1 — Vow of Smallness) |
| Auxiliary client (cheap model for compression / summarisation) | `agent/auxiliary_client.py` | Funi | Not present | Defer (lives behind the Ember "two-tier hot/cold" Forge will propose in 33) |

## 4. Gateway / multi-platform messaging

| Hermes concept | Source path | Ember True Name | Current state | Tag |
|---|---|---|---|---|
| Channel directory | `gateway/channel_directory.py` | n/a | Not present | New-Name candidate (Gjallarhorn — see 61) |
| Per-platform adapters (Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Mattermost, Feishu, Wecom, etc.) | `gateway/platforms/*.py` | n/a | Not present | Reject for default (Vow of Smallness); New-Name + opt-in plugin for workstation profile |
| Platform registry | `gateway/platform_registry.py` | n/a | Not present | New-Name dependent |
| Pairing / multi-device | `gateway/pairing.py` | n/a | Not present | Defer |
| Mirror (broadcast to multiple targets) | `gateway/mirror.py` | n/a | Not present | Defer |
| Delivery / runtime footer / sticker cache | `gateway/{delivery,runtime_footer,sticker_cache}.py` | n/a | Not present | Reject (Telegram-shaped polish) |
| Memory monitor | `gateway/memory_monitor.py` | Brunnr-adjacent | Not present | Defer |
| Hooks framework | `gateway/hooks.py`, `gateway/builtin_hooks/` | mixed | Not present | Defer (the hook idea is good; the gateway-specific framing is wrong for Ember) |
| Stream consumer | `gateway/stream_consumer.py` | Funi-adjacent | Slice 2 has streaming Funi | Aligned (smaller) |
| Status / shutdown forensics | `gateway/{status,shutdown_forensics}.py` | Strengr-adjacent | Not present | Defer |
| WhatsApp identity | `gateway/whatsapp_identity.py` | n/a | Not present | Reject |

The whole gateway subsystem is the strongest case for a **new True Name** in Ember. Until Ember has multi-platform messaging surfaces, it has no home. The working name is **Gjallarhorn** ("the announcing horn"), elaborated in [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]]. The Gjallarhorn case stays *Proposed* — there's no immediate need to introduce it.

## 5. TUI gateway (sandbox backends)

| Hermes concept | Source path | Ember True Name | Current state | Tag |
|---|---|---|---|---|
| Sandbox backend abstraction | `tui_gateway/server.py`, `transport.py` | n/a | Not present | Defer |
| Docker backend | `tui_gateway/...` (in broader file tree) | n/a | n/a | Defer |
| SSH / Modal / Daytona / Singularity / Vercel-Sandbox backends | `tui_gateway/...` | n/a | n/a | Reject for Pi default; Defer for workstation |
| WebSocket transport for sidecar UIs | `tui_gateway/ws.py` | n/a | n/a | Defer (sound pattern; not needed until Ember has a sidecar dashboard) |
| Event publisher | `tui_gateway/event_publisher.py` | n/a | n/a | Defer |
| TeeTransport (multi-sink) | `tui_gateway/transport.py` | n/a | n/a | Defer (pattern is portable; reference for Ember's future sidecar) |

Ember's small-and-tethered shape does not need sandbox backends. Code execution in slice 2/3 is via the operator's actual machine, gated by the approval framework. A Docker / Modal / Daytona / Vercel-Sandbox option becomes interesting only if Ember runs *agent tasks for other people* — which is not her use case. **Defer or reject.**

## 6. Plugins

| Hermes plugin | Source path | Ember True Name | Tag |
|---|---|---|---|
| `browser/` | `plugins/browser/` | Funi (tool) | Defer (workstation-profile opt-in) |
| `context_engine/` | `plugins/context_engine/` | Funi | Defer |
| `disk-cleanup/` | `plugins/disk-cleanup/` | n/a | Reject (Vow of Smallness: housekeeping is not Ember's role) |
| `example-dashboard/` | `plugins/example-dashboard/` | n/a | Defer |
| `google_meet/`, `kanban/`, `spotify/`, `teams_pipeline/` | `plugins/*/` | n/a | Reject (workplace-tool-shaped; not Ember's audience) |
| `hermes-achievements/` | `plugins/hermes-achievements/` | n/a | Reject (vanity) |
| `image_gen/`, `video_gen/` | `plugins/*/` | n/a | Reject |
| `memory/` | `plugins/memory/` | Brunnr | Aligned in concept; the `MemoryProvider` ABC is interesting — see 61 |
| `model-providers/` | `plugins/model-providers/` | Funi | Gap (port the pattern; see 23) |
| `observability/` | `plugins/observability/` | Munnr-adjacent | Defer (observability matters but Ember is small enough to print) |
| `platforms/` | `plugins/platforms/` | Gjallarhorn (proposed) | Defer |
| `web/` | `plugins/web/` | Funi (tool) | Defer |

The keepers from Hermes's plugin catalogue are **`memory/`** (the MemoryProvider ABC pattern) and **`model-providers/`** (the declarative profile pattern). Both are addressed in the interface docs above.

## 7. Skills

| Hermes concept | Source path | Ember True Name | Current state | Tag |
|---|---|---|---|---|
| `SKILL.md` validator (12 rules) | `tools/skill_manager_tool.py:217-253` | Funi (new submodule) | Not present | Gap (high-value port; ~50 lines) |
| Filesystem-as-registry discovery | `tools/skill_manager_tool.py:286-295` | Funi | Not present | Gap |
| Two-tree separation (user-local + in-repo) | `skills/...` + `~/.hermes/skills/` | Funi | Not present | Gap |
| `skills_list` + `skill_view` tools | `tools/skill_manager_tool.py` | Funi (tool) | Not present | Gap |
| `skill_manage(create/edit/patch/delete/write_file)` | `tools/skill_manager_tool.py:713-790` | Funi (tool) + Munnr (CLI) | Not present | Gap (subset only — see 22) |
| `metadata.hermes.related_skills` graph | per-skill frontmatter | Funi | Not present | Gap |
| Embedding-based skill retrieval | (implied by optional-skills/ scale) | Brunnr | Not present | Defer (use full-list injection until skill count justifies retrieval) |
| Skill self-creation | `skill_manage(action="create")` | Funi + Munnr | Not present | Gap (with audit; see 22) |
| Curator / pinning | `tools/skill_usage.py`, `agent/curator.py` | n/a | Not present | Defer |
| Security scan on user-supplied skills | `tools/skill_manager_tool.py:80-102` | n/a | n/a | Reject (Ember skills are read-only documents, no scripts; smaller threat model) |

The skills surface is **Ember's biggest "good idea to port" pile.** The validator alone is ~50 lines; the discovery walk is ~20; the two tools are ~40 each; the storage idiom is "directory plus Markdown file." All of it fits the Vow of Smallness.

## 8. MCP / ACP

| Hermes concept | Source path | Ember True Name | Current state | Tag |
|---|---|---|---|---|
| MCP server (publish) | `mcp_serve.py` (897 lines) | Munnr | Not present; ADR 0014 ratified bidirectionality intent | Gap (high-value; see 20 + 63) |
| MCP client (consume) | `tools/mcp_tool.py` + `agent/transports/hermes_tools_mcp_server.py` | Funi | Not present | Gap |
| Event bridge (mtime-poll SQLite) | `mcp_serve.py:204-444` | Brunnr-adjacent | Brunnr has the SQLite substrate | Aligned (one polling daemon away) |
| Long-poll `events_wait` | `mcp_serve.py:268-294` | Munnr | Not present | Gap |
| Approval routing over MCP | `mcp_serve.py:823-857` | Munnr + Funi (audit) | Approval framework exists in slice 2 | Aligned + Gap (the routing) |
| ACP adapter | `acp_adapter/server.py` (1,200+ lines) | n/a | Not present | Defer (MCP is the priority; ACP is parallel surface for Zed-shaped consumers) |
| Cron / scheduled subagent | `cron/` + `batch_runner.py` | Funi | Not present | Defer; possibly New-Name candidate (working: **Hringja**, "the ringer") |

## 9. State / persistence / training

| Hermes concept | Source path | Ember True Name | Current state | Tag |
|---|---|---|---|---|
| `hermes_state.py` (140 KB session DB) | root | Brunnr | Brunnr's `episode` table is the analogue | Aligned (Brunnr already does the small version) |
| FTS5-backed session search | `hermes_state.py` (search functions) | Brunnr | Brunnr's FTS5 path already shipped slice 1 | Aligned |
| Trajectory compressor (training-data pipeline) | `trajectory_compressor.py` (65 KB) | Smiðja | Not present | Defer (this is a real future — a small Smiðja content source that consumes Brunnr's episodes and emits training pairs for fine-tuning a local Funi) |
| Batch runner | `batch_runner.py` (57 KB) | Funi | Not present | Defer |
| Mini SWE runner | `mini_swe_runner.py` (28 KB) | n/a | Not present | Reject (benchmark runner; not a feature) |
| Model tools | `model_tools.py` (40 KB) | Funi | Not present | Defer (most of the work is provider/transport, addressed elsewhere) |

## 10. CLI / TUI

| Hermes concept | Source path | Ember True Name | Current state | Tag |
|---|---|---|---|---|
| Argument parsing | `cli.py` (662 KB), `hermes_cli/` | Munnr | argparse-based CLI in slice 2 | Aligned (smaller) |
| Interactive TUI (prompt_toolkit) | `cli.py` | Munnr | Plain REPL only | Defer; possibly Aligned if a slice-5 lifts Munnr to a textual TUI |
| Slash commands | `cli.py`, `hermes_cli/...` | Munnr | Subcommand-shaped (e.g., `ember doctor`) | Aligned |
| Multiline editing + history + interrupt-without-loss | `cli.py` (large) | Munnr | Plain `input()` | Defer (a small step up to readline + history is reasonable) |
| Status line / banners | `cli.py`, `gateway/runtime_footer.py` | Munnr | Disconnect banner already shipped slice 2 §11 | Aligned |
| `hermes doctor` | `hermes_cli/doctor.py` | Munnr | `ember doctor` already exists, slice 2 | Aligned |

## 11. Cron / scheduling / batch

| Hermes concept | Source path | Ember True Name | Current state | Tag |
|---|---|---|---|---|
| Cron scheduler | `cron/scheduler.py` (referenced from base.py) | n/a | Not present | New-Name candidate (**Hringja**, "the ringer"); Defer until concrete use case |
| Batch runner | `batch_runner.py` | Funi | Not present | Defer |
| Routine docs ("hermes-already-has-routines.md") | root | n/a | n/a | Defer |

## 12. Top-level files (sizes telling stories)

| Hermes file | Size | What it is | Ember True Name | Tag |
|---|---|---|---|---|
| `cli.py` | 662 KB | TUI + command surface | Munnr (much smaller) | Aligned (Ember will never be this big — Vow of Smallness) |
| `run_agent.py` | 180 KB | Main agent driver | Funi | Aligned (Ember's `spark/funi/agent.py` is ~5 KB and should stay under 20 KB) |
| `hermes_state.py` | 140 KB | State management | Brunnr | Aligned (smaller) |
| `trajectory_compressor.py` | 65 KB | Training-data pipeline | Smiðja | Defer |
| `batch_runner.py` | 57 KB | Batch execution | Funi | Defer |
| `model_tools.py` | 40 KB | Model tooling | Funi | Defer |
| `mcp_serve.py` | 31 KB | MCP server | Munnr | Gap |
| `mini_swe_runner.py` | 28 KB | SWE benchmark runner | n/a | Reject |
| `toolsets.py` | 29 KB | Toolset definitions | Funi | Aligned (Ember has a tool registry, slice 2) |
| `toolset_distributions.py` | 12 KB | Toolset packaging | Funi | Defer |

## 13. The summary table — what Ember will and will not take

**Will take (Gap → Adopt):**
1. Skill subsystem (validator + walk + two tools + two trees) — *high value, small port*
2. Provider profile + transport split — *medium port, big multiplier*
3. MCP server (the read-only subset) — *medium port, ecosystem multiplier*
4. MCP client (consume external tools) — *medium port*
5. Tool executor thread pool + parallelism rules — *small port, big quality multiplier*
6. Interrupt-fan-out + synthetic cancellation messages — *small port, correctness multiplier*
7. Memory provider plug-in ABC — *small port, Brunnr-extensibility multiplier*
8. Per-error-code TTL exhaustion model — *small port*
9. Typed retry policy with provider-supplied retry-after parsing — *small port*
10. ContextVar-routed concurrency primitives — *pattern, not port*

**Will defer (Defer):**
- Streaming improvements beyond what slice 2 already shipped
- Cross-provider failover
- Multi-credential rotation (single-credential first)
- Trajectory compression
- Curator / insights / title generator
- LSP / browser / image-gen / video-gen
- Multiple TUI sandbox backends
- ACP adapter (MCP is the priority)
- Cron / scheduled subagents
- Most plugins (`google_meet`, `spotify`, `teams_pipeline`, `hermes-achievements`, etc.)

**Will not take (Reject):**
- Workplace-tool plugins (Vow of Public-Friendliness for non-developers)
- Image/video generation (Vow of Smallness)
- Disk-cleanup / kanban / achievements (not Ember's role)
- Mini SWE runner (benchmark, not feature)
- Multi-platform messaging *by default* (would land as Gjallarhorn opt-in on workstation profile; never on Pi default)
- ANSI-heavy spinners that punish serial consoles (Pi default deployment scenario)

## 14. The new-name candidates summary

These do not fit any current True Name. They may earn their own. Final decision lives in [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] — **proposed, not decided**.

| Working name | Meaning | Owns | Status |
|---|---|---|---|
| **Gjallarhorn** | the announcing horn | Multi-platform messaging gateways (Telegram, Discord, Slack, etc.) | Proposed; opt-in only |
| **Hringja** | the ringer | Scheduled / recurring / cron-shaped agent tasks | Proposed; speculative |
| **Lærdómr** | learned-knowledge | Skill / procedural-memory subsystem (alternative to making it a Funi submodule) | Proposed; default-leaning is "no, keep skills in Funi" |
| **Vinátta** | friendship / bond | Memory provider plug-in API (the third-party brain extensions: Honcho, Mem0, Hindsight) | Proposed; default-leaning is "no, keep in Brunnr" |

## What This Means for Ember

**Big picture:**

- The crosswalk surfaces **ten high-value Gaps** (§13) that Ember should actively close, organised against [[60_synthesis/64_MIGRATION_PLAN]].
- The crosswalk surfaces **four new-name candidates** that are *proposed only*. Ember should resist new True Names until at least two of them have concrete operator pull. The Vow of Smallness wins ties.
- The crosswalk surfaces a **large defer pile** that is healthy — Ember does not need to be Hermes, and most of Hermes is not Ember-shaped.
- The crosswalk surfaces a **smaller reject pile** that is Vow-protected — these are the patterns where Ember consciously diverges, and the divergences are virtuous.

**True Names affected:** All six. Funi gets the deepest port lift (provider/transport split, skill subsystem, tool executor); Strengr gets the credential-handling lift; Brunnr is largely confirmed (its small shape matches Hermes's substrate); Smiðja stays largely unchanged (trajectory compression is a future ingest source, not a refactor); Hjarta and Munnr stay where they are (the corresponding Hermes surfaces are bigger but the *shape* is right).

**Vows touched:**
- *Reinforced:* every Vow gets a confirming check from at least one Gap or Aligned row. The biggest reinforcement is the Vow of Modular Authorship — Hermes's plugin model + lazy-import discipline maps cleanly into Ember's existing optional-extras shape.
- *Most-strained:* Vow of Smallness. The temptation reading Hermes is to *take all of it*. The crosswalk's Defer + Reject columns are the discipline that holds the line.
- *Most-clarified:* Vow of Pluggable Storage. Hermes's plugin discovery via filesystem walk + `register_*` registration is the same pattern at a different scale; Ember already uses it; the crosswalk confirms the choice.

**Concrete next step:** [[60_synthesis/64_MIGRATION_PLAN]] sequences these ten Gaps into phased, reversible work. The skill subsystem is the highest priority because it's the smallest port with the biggest qualitative change. MCP is the highest-priority *ecosystem* item.

**Cross-references:**
- [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] is the proposal doc for the four new-name candidates.
- [[60_synthesis/62_DEPENDENCY_FLOW]] traces the end-to-end data flow that this crosswalk's modules participate in.
- [[60_synthesis/63_INTEGRATION_PATHS]] gives the concrete how-to-wire-it for each Gap.
- [[60_synthesis/64_MIGRATION_PLAN]] is the phasing.
- [[60_synthesis/67_GLOSSARY_AND_INDEX]] resolves any unfamiliar term in either column.

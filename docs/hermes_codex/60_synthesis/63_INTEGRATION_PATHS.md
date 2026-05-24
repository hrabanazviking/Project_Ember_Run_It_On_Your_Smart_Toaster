---
codex_id: 63_INTEGRATION_PATHS
title: Integration Paths — Concrete How-To-Wire for Each Hermes Pattern
role: Cartographer
layer: Synthesis
status: draft
hermes_source_refs:
  - mcp_serve.py
  - providers/base.py
  - agent/transports/base.py
  - agent/tool_executor.py
  - agent/credential_pool.py
  - agent/memory_provider.py
  - tools/skill_manager_tool.py
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 60_synthesis/60_HERMES_VS_EMBER_CROSSWALK
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/62_DEPENDENCY_FLOW
  - 60_synthesis/64_MIGRATION_PLAN
  - 60_synthesis/66_DECISION_RECORDS
  - 20_interface/20_MCP_INTEGRATION
  - 20_interface/21_RPC_INTERFACE
  - 20_interface/22_SKILL_INTERFACE
  - 20_interface/23_PROVIDER_INTERFACE
---

# 63 — Integration Paths

> *A path is not a route until somebody walks it. This is the walking instructions.*
> — Védis Eikleið, with a list of doorways

## 1. The shape of an integration path

For each Hermes pattern Ember is going to adopt, this doc gives the **same five-row card**:

- **True Name** that owns it.
- **Interface** required (from the 20_interface/ docs).
- **Existing Ember code** that is the integration point.
- **Vows** that constrain the work.
- **Path** — the concrete sequence of file edits, with sizes.

The cards are arranged by **Vow-compatibility first, value-per-line second**. The reading order is the proposed implementation order. Phasing happens in [[60_synthesis/64_MIGRATION_PLAN]].

The cards cover the ten high-value Gaps listed in [[60_synthesis/60_HERMES_VS_EMBER_CROSSWALK]] §13.

---

## 2. Path 1 — Skill subsystem

**True Name:** Funi (with a small Munnr surface for `ember skills` CLI).

**Interface:** [[20_interface/22_SKILL_INTERFACE]] — the SKILL.md frontmatter contract.

**Existing Ember code:**
- `src/ember/spark/funi/handle.py` — defines `FuniHandle` Protocol; this is where the model loop lives.
- `src/ember/spark/funi/prompt.py` — assembles the system prompt; this is where skills must be surfaced.
- `src/ember/spark/munnr/chat.py` — the REPL where the operator runs `ember skills ...`.
- `pyproject.toml` — extras declaration.

**Vows that constrain:** Vow of Smallness (≤ 500 LOC initial port); Vow of the Unbroken Whole (one full module set); Vow of Flexible Roots (no absolute paths); Vow of Public-Friendliness (`ember skills list` shows operator-readable output).

**Path (sequenced edits):**

1. *New file* `src/ember/spark/funi/skills/__init__.py` — package init.
2. *New file* `src/ember/spark/funi/skills/loader.py` (~80 LOC) — port `tools/skill_manager_tool.py::_validate_frontmatter` verbatim with `HERMES_HOME` → `Path.home() / ".ember"`. Functions: `validate_frontmatter(content) -> str | None`, `read_skill_frontmatter(path) -> dict | None`, `walk_skill_roots(roots: list[Path]) -> Iterator[SkillManifest]`.
3. *New file* `src/ember/spark/funi/skills/manifest.py` (~40 LOC) — dataclass `SkillManifest(name, description, version, author, license, tags, related_skills, path)`.
4. *New file* `src/ember/spark/funi/skills/surfacer.py` (~60 LOC) — function `surface_skills(manifests, *, strategy="full_list", max_tokens=2000) -> str`. Strategy 1 only (full-list injection); leave hooks for `tags` and `embedding` strategies.
5. *New file* `src/ember/spark/funi/tools/skill_view.py` (~30 LOC) — registered tool: given a skill name, return the body of its SKILL.md (or error message).
6. *New file* `src/ember/spark/funi/tools/skill_list.py` (~30 LOC) — registered tool: list (name, description) pairs.
7. *Edit* `src/ember/spark/funi/prompt.py` — insert call to `surface_skills()` in `assemble()`, between the system text and the recent-episodes block. Wrap with config flag `skills.enabled: true` (default true).
8. *Edit* `src/ember/spark/funi/tools/__init__.py` — register `skill_view` and `skill_list` tools.
9. *New file* `src/ember/spark/munnr/skill_commands.py` (~120 LOC) — argparse subcommands for `ember skills list/view/create/edit`. The `create` subcommand is operator-facing only; agent-initiated creation lands later (Phase M-skill-write).
10. *Edit* `src/ember/cli/__init__.py` — wire `ember skills ...` to the subcommands.
11. *Edit* `pyproject.toml` — `[project.optional-dependencies]` add `skills = ["pyyaml>=6.0"]`; or roll into existing `config` extra since `pyyaml` is already there.
12. *New file* `src/ember/skills/_seed/ember-skill-authoring/SKILL.md` (~10 KB) — the meta-skill, Ember-flavoured, written from scratch (no copy of Hermes's; Ember's audience and vocabulary differ).
13. *New file* `src/ember/skills/_seed/tethered-grounding-discipline/SKILL.md` (~6 KB).
14. *New file* `src/ember/skills/_seed/graceful-offline-degradation/SKILL.md` (~5 KB).
15. *New file* `src/ember/skills/_seed/writing-plans/SKILL.md` (~6 KB) — adapted from Hermes's `writing-plans` SKILL.md, with appropriate attribution to obra/superpowers per the original; Ember keeps the attribution and adds her own.
16. *New file* `src/ember/skills/_seed/test-driven-development/SKILL.md` (~6 KB) — same.
17. *New tests* `tests/unit/test_skill_loader.py`, `tests/unit/test_skill_surfacer.py`, `tests/integration/test_skill_commands.py`. ~200 LOC test code.

**Deferred to Phase M-skill-write (later phase):** the `skill_manage(action="create")` tool that lets the agent itself write new skills. The agent-initiated path requires audit-log integration; operator-initiated `ember skills create` is simpler and ships first.

**Total LOC estimate:** ~360 LOC code + ~200 LOC tests + ~33 KB seed skills.

**Cross-platform check:** pure stdlib + `yaml.safe_load`. `Path.rglob`. No platform-specific code.

---

## 3. Path 2 — Provider profile + transport split

**True Name:** Funi.

**Interface:** [[20_interface/23_PROVIDER_INTERFACE]] — `ProviderProfile` + `ProviderTransport` two-layer split.

**Existing Ember code:**
- `src/ember/spark/funi/handle.py` — `FuniHandle` Protocol.
- `src/ember/spark/funi/ollama/adapter.py` — current concrete adapter.
- `src/ember/schemas/funi.py` — `FuniReply` dataclass.

**Vows that constrain:** Vow of Modular Authorship (one adapter failing must not crash Funi); Vow of Smallness (the refactor must reduce duplication, not add lines); Vow of the Unbroken Whole (atomic refactor — one phase).

**Path:**

1. *New file* `src/ember/spark/funi/profile.py` (~80 LOC) — `FuniProfile` dataclass mirroring `providers/base.py:ProviderProfile`. Fields: `name`, `runtime_kind` (analogue of `api_mode`), `aliases`, `display_name`, `description`, `default_model`, `default_aux_model`. Drop the Hermes hooks (`prepare_messages`, `build_extra_body`, `build_api_kwargs_extras`) for v1 — Ember has one provider per runtime_kind; provider-quirks at this scale are noise. Add them back when a second runtime arrives.
2. *New file* `src/ember/spark/funi/transports/__init__.py` — registry (`register_transport(kind, transport_cls)`, `get_transport(kind)`).
3. *New file* `src/ember/spark/funi/transports/base.py` (~80 LOC) — `FuniTransport` Protocol, mirroring `agent/transports/base.py:ProviderTransport`. Five required: `runtime_kind`, `convert_messages`, `convert_tools`, `build_kwargs`, `normalize_response`. Two optional: `validate_response`, `map_finish_reason`. Skip `extract_cache_stats` for v1 (Ollama doesn't have it).
4. *New file* `src/ember/spark/funi/transports/types.py` (~60 LOC) — `NormalizedFuniResponse`, `ToolCall` (with `tc.function` backward-compat property), `Usage`.
5. *Refactor* `src/ember/spark/funi/ollama/adapter.py` → `src/ember/spark/funi/transports/ollama.py` (~250 LOC). Same code, reorganised. The `FuniHandle.complete()` and `complete_streaming()` methods now call `transport.build_kwargs() → POST → transport.normalize_response()`. Single concrete transport.
6. *New file* `src/ember/spark/funi/plugins/ollama/__init__.py` (~20 LOC) — declares the `FuniProfile(name="ollama", runtime_kind="ollama_native", ...)` and registers it.
7. *Edit* `src/ember/spark/funi/handle.py` — `FuniHandle` is now a tiny wrapper that selects a profile + transport by name and delegates. The model-completion logic lives in the transport.
8. *Edit* `src/ember/config/loader.py` — `funi.runtime` now references a profile name; resolution is via the registry.
9. *Edit tests* — `tests/unit/test_funi_ollama.py` and friends adapt to the new structure. ~100 LOC test diff.

**Total LOC estimate:** +290 LOC, -150 LOC (Ollama adapter refactor), net +140 LOC. The future second runtime (LM Studio / llama.cpp HTTP / Anthropic) is then ~80 LOC each.

**Cross-platform check:** All stdlib + existing Ollama HTTP. No new platform considerations.

---

## 4. Path 3 — MCP server (read-only subset)

**True Name:** Munnr (publishing surface).

**Interface:** [[20_interface/20_MCP_INTEGRATION]] — FastMCP server, five read-only tools to start.

**Existing Ember code:**
- `src/ember/spark/munnr/chat.py` — REPL.
- `src/ember/well/brunnr/sqlite_vec/adapter.py` — has the SQLite substrate the event bridge needs.
- `src/ember/cli/__init__.py` — subcommand wiring.

**Vows that constrain:** Vow of Smallness (lazy `mcp` import); Vow of Modular Authorship (`mcp` missing → server unavailable, REPL unaffected); Vow of Honest Memory (MCP-initiated tool calls must record the originating client in the audit log).

**Path:**

1. *Edit* `pyproject.toml` — add `mcp = ["mcp>=1.2"]` extra.
2. *New file* `src/ember/spark/munnr/mcp/__init__.py` — lazy import of `mcp.server.fastmcp`; `_MCP_AVAILABLE` flag.
3. *New file* `src/ember/spark/munnr/mcp/server.py` (~350 LOC) — port the read-only subset from `mcp_serve.py:450-820`. Tools to publish: `sessions_list`, `session_get`, `episodes_read`, `events_poll`, `events_wait`. (Ember's analogues to Hermes's `conversations_list`, etc.) Each tool reads from Brunnr.
4. *New file* `src/ember/spark/munnr/mcp/event_bridge.py` (~150 LOC) — port `mcp_serve.py:204-444`. The bridge polls Brunnr's `episode` table mtime every 200 ms. mtime gated.
5. *New file* `src/ember/spark/munnr/mcp/coerce.py` (~15 LOC) — port `_coerce_int` verbatim.
6. *New file* `src/ember/cli/mcp.py` (~30 LOC) — `ember mcp serve` subcommand. Stdio only.
7. *Edit* `src/ember/cli/__init__.py` — wire the new subcommand.
8. *New tests* `tests/unit/test_mcp_server.py`, `tests/integration/test_mcp_event_bridge.py` (~250 LOC).

**Deferred:**
- `messages_send` (requires Gjallarhorn).
- `permissions_respond` (requires audit-log integration; ADR-proposed; see [[60_synthesis/66_DECISION_RECORDS]] ADR-Proposed-MCP-001).
- `attachments_fetch` (requires multimodal episode shape; deferred).
- HTTP transport.

**Total LOC estimate:** ~545 LOC code + ~250 LOC tests.

**Cross-platform check:** stdio is universal. The `mcp` Python package has no platform-specific deps. `threading.Event`, `contextvars` all stdlib.

---

## 5. Path 4 — MCP client (consume external MCP servers as Funi tools)

**True Name:** Funi (tool dispatch).

**Interface:** [[20_interface/20_MCP_INTEGRATION]] §5 — consuming-side patterns; also [[20_interface/22_SKILL_INTERFACE]] for "use a skill to wire an MCP server."

**Existing Ember code:**
- `src/ember/spark/funi/tools/registry.py` — `ToolRegistry` already exists, slice 2.
- `src/ember/spark/funi/tools/__init__.py` — tool registration.

**Vows that constrain:** Vow of Modular Authorship (MCP client failure does not crash Funi); Vow of Honest Memory (every MCP call recorded in audit log); Vow of Public-Friendliness (operator can list/disable MCP servers from CLI).

**Path:**

1. *Edit* `pyproject.toml` — `mcp` extra already added in Path 3.
2. *New file* `src/ember/spark/funi/tools/mcp_client.py` (~250 LOC) — implements the generic `mcp_tool` pattern from Hermes. Reads server config from `~/.ember/config/mcp_servers.yaml`. For each server: lazy connect, list tools, register each one in the global `ToolRegistry` with `mcp_<server>_<tool>` naming.
3. *New file* `src/ember/spark/funi/tools/mcp_dispatch.py` (~80 LOC) — when the model calls a `mcp_*` tool, dispatch to the right client. Wraps with audit-log entry, parallel-safety check (per [[20_interface/21_RPC_INTERFACE]] §3).
4. *New file* `src/ember/cli/mcp_servers.py` (~80 LOC) — `ember mcp-servers list/add/remove`. Manages `mcp_servers.yaml`.
5. *Edit* `config/ember.example.yaml` — add `mcp_clients:` block with examples.
6. *New tests* with a fake MCP server (one of the test fixtures spawns FastMCP over stdio with two test tools). ~200 LOC test.

**Total LOC estimate:** ~410 LOC code + ~200 LOC tests.

**Cross-platform check:** MCP-over-stdio; works everywhere.

---

## 6. Path 5 — Tool executor with parallelism and ContextVars

**True Name:** Funi.

**Interface:** [[20_interface/21_RPC_INTERFACE]] §3-§7 — concurrency rules, ContextVar propagation, interrupt fan-out.

**Existing Ember code:**
- `src/ember/spark/funi/tools/registry.py` — registry exists.
- `src/ember/spark/funi/tools/dispatch.py` — sequential dispatch lives here.

**Vows that constrain:** Vow of Modular Authorship; Vow of Smallness (8-worker pool cap, no larger); Vow of Honest Memory (synthetic cancellation messages for skipped tools).

**Path:**

1. *Edit* `src/ember/spark/funi/tools/dispatch.py` — promote to a module with two functions: `dispatch_sequential(tool_calls, ...)` (current behaviour) and `dispatch_parallel(tool_calls, ...)` (new).
2. *New constants* at top of `dispatch.py`:
   ```python
   _MAX_TOOL_WORKERS = 8
   _NEVER_PARALLEL_TOOLS = frozenset()  # Ember has no clarify-shaped tool yet
   _PARALLEL_SAFE_TOOLS = frozenset({"read_local_file", "search_well", "fetch_url"})
   _PATH_SCOPED_TOOLS = frozenset({"read_local_file"})  # write tools come later
   ```
3. *New function* `_should_parallelize_tool_batch(tool_calls) -> bool` — port from `agent/tool_dispatch_helpers.py:103-146`.
4. *New function* `_extract_parallel_scope_path` + `_paths_overlap` — port.
5. *New ceremony* in worker function — port the prologue from `agent/tool_executor.py:197-271`: thread-id registration, interrupt fan-out (when Ember adds per-thread interrupt support; for v1, use a single `interrupt_requested` flag), `contextvars.copy_context()` propagation.
6. *Edit* `src/ember/spark/funi/tools/registry.py` — add `interrupt_requested` and `interrupt()` method on the registry.
7. *Edit caller* in `src/ember/spark/funi/agent.py` or wherever the tool loop dispatches — replace direct sequential dispatch with `dispatch_parallel(...) if _should_parallelize_tool_batch(...) else dispatch_sequential(...)`.
8. *New tests* `tests/unit/test_dispatch_parallel.py` — verify path-overlap detection, parallel-safe set, interrupt propagation, ContextVar copy. ~200 LOC.

**Total LOC estimate:** ~250 LOC code + ~200 LOC tests.

**Cross-platform check:** `concurrent.futures.ThreadPoolExecutor`, `contextvars`, `threading` — all stdlib.

---

## 7. Path 6 — Memory provider plug-in ABC

**True Name:** Brunnr (with **Vinátta** name reserved for the future plug-in subsystem per [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]]).

**Interface:** Hermes's `MemoryProvider` ABC at `agent/memory_provider.py:42-280`.

**Existing Ember code:**
- `src/ember/well/brunnr/protocol.py` — `BrunnrHandle` Protocol (storage shape).
- `src/ember/spark/funi/prompt.py` — where recall context is consumed.

**Vows that constrain:** Vow of Pluggable Storage; Vow of Tethered Grounding (no provider may insert content into the prompt unaudited).

**Path (deferred to Phase M5; sketch here):**

1. *New file* `src/ember/well/memory_provider.py` (~150 LOC) — `MemoryProvider` Protocol mirroring `agent/memory_provider.py:42-280`. Core lifecycle: `name`, `is_available`, `initialize`, `system_prompt_block`, `prefetch`, `queue_prefetch`, `sync_turn`, `get_tool_schemas`, `handle_tool_call`, `shutdown`. Optional hooks: `on_turn_start`, `on_session_end`, `on_pre_compress`, `on_memory_write`, `on_delegation`.
2. *New file* `src/ember/well/memory_manager.py` (~100 LOC) — `MemoryManager` orchestrator. One-external-provider limit. Wires into prompt assembly.
3. *Edit* `src/ember/spark/funi/prompt.py` — add `memory_manager.prefetch_all(query)` integration point.
4. *Edit* `src/ember/well/brunnr/builtin_provider.py` — wrap the existing Brunnr-direct-write path in the new MemoryProvider Protocol. This is the *built-in* provider; external providers are plug-ins.
5. *Plugins* `~/.ember/plugins/memory/honcho/` etc. — operator-installed. Out of scope for slice 4.

**Total LOC estimate:** ~250 LOC code + ~120 LOC tests.

**Cross-platform check:** pure stdlib. External providers each have their own platform stories.

---

## 8. Path 7 — Per-error-code TTL exhaustion model

**True Name:** Strengr.

**Interface:** [[20_interface/23_PROVIDER_INTERFACE]] §6 — typed exhaustion with per-code TTL.

**Existing Ember code:**
- `src/ember/thread/strengr/` — the tether.

**Vows that constrain:** Vow of Graceful Offline; Vow of Smallness (single-credential first, no rotation).

**Path:**

1. *New file* `src/ember/thread/strengr/exhaustion.py` (~80 LOC) — port constants and helpers:
   ```python
   EXHAUSTED_TTL_401_SECONDS = 5 * 60
   EXHAUSTED_TTL_429_SECONDS = 60 * 60
   EXHAUSTED_TTL_DEFAULT_SECONDS = 60 * 60

   def parse_retry_after(value) -> float | None: ...  # from credential_pool._parse_absolute_timestamp + _extract_retry_delay_seconds
   def exhausted_until(last_status_at: float, error_code: int | None) -> float: ...
   ```
2. *Edit* `src/ember/spark/funi/transports/ollama.py` (or future remote provider) — on HTTP error response, classify error_code, compute exhausted_until, return typed `Unavailable(reason, until)`. Ollama-local rarely sees this (no rate limits), but the pattern is shared.
3. *Edit* `src/ember/spark/funi/transports/base.py` — `Unavailable` type already exists; add `exhausted_until` field optionally.
4. *New tests* `tests/unit/test_exhaustion.py` (~80 LOC).

**Total LOC estimate:** ~80 LOC code + ~80 LOC tests.

---

## 9. Path 8 — Typed retry policy with provider-supplied retry-after parsing

**True Name:** Strengr.

**Interface:** `agent/retry_utils.py` (referenced; not deep-read).

**Existing Ember code:** `src/ember/thread/strengr/` — basic retry exists.

**Path:**

1. *New file* `src/ember/thread/strengr/retry.py` (~100 LOC). Policy class:
   ```python
   @dataclass
   class RetryPolicy:
       max_attempts: int = 3
       base_delay: float = 0.5
       max_delay: float = 30.0
       jitter: bool = True
       respect_retry_after: bool = True

       def next_delay(self, attempt: int, retry_after: float | None) -> float: ...
   ```
2. *Edit* `src/ember/thread/strengr/handle.py` — wrap remote calls with policy. Already partly present; formalize.
3. *Tests*: `tests/unit/test_retry_policy.py` (~80 LOC).

**Total LOC estimate:** ~100 LOC code + ~80 LOC tests.

---

## 10. Path 9 — Interrupt fan-out and synthetic cancellation

**True Name:** Funi (where the tool loop lives).

**Interface:** [[20_interface/21_RPC_INTERFACE]] §4.

**Existing Ember code:** `src/ember/spark/munnr/chat.py` — Ctrl-C handler.

**Path:**

1. *New file* `src/ember/spark/funi/tools/interrupt.py` (~60 LOC) — `InterruptRegistry` class. Tracks worker tids. `request()` sets a flag; `is_set_for_thread(tid)` returns per-tid. `register_worker(tid)` and `unregister_worker(tid)`.
2. *Edit* `src/ember/spark/funi/tools/dispatch.py` — synthetic cancellation message per skipped tool call (port from `agent/tool_executor.py:75-83`):
   ```python
   def synthetic_cancellation(tool_call) -> dict:
       return {
           "role": "tool",
           "name": tool_call.name,
           "content": f"[Tool execution cancelled — {tool_call.name} was skipped due to user interrupt]",
           "tool_call_id": tool_call.id,
       }
   ```
3. *Edit* `src/ember/spark/munnr/chat.py` — on Ctrl-C, call `interrupt_registry.request()` instead of (or in addition to) raising.
4. *Tests*: `tests/unit/test_interrupt.py` (~80 LOC).

**Total LOC estimate:** ~80 LOC code + ~80 LOC tests.

---

## 11. Path 10 — Background Episode persistence (small optimisation)

**True Name:** Brunnr.

**Existing Ember code:** `src/ember/well/brunnr/sqlite_vec/adapter.py` — `add_episode` is currently blocking on the main thread.

**Vows that constrain:** Vow of Honest Memory (post-turn persistence is *guaranteed* — moving to background must keep the guarantee).

**Path (deferred to slice 5 or later):**

1. *Edit* `src/ember/well/brunnr/sqlite_vec/adapter.py` — `add_episode` queues to an internal `queue.Queue`; a daemon thread drains. On adapter close, drain blocking.
2. *Tests*: queue drain on close; in-flight episodes flushed.

**Total LOC estimate:** ~50 LOC code + ~50 LOC tests.

**Note:** the Vow of Honest Memory forbids losing an episode. Drain-on-close is non-negotiable. Crash without drain = data loss; for Ember v1, the synchronous write is more honest. Defer until persistence cost dominates turn latency on Pi-5 (it does not today).

---

## 12. Cross-cutting integration check

The ten paths above touch:
- **Funi:** Paths 1, 2, 4, 5, 9. Five paths. Funi gets the deepest lift.
- **Strengr:** Paths 7, 8. Two paths. Single-credential first.
- **Brunnr:** Paths 6 (Vinátta reservation), 10. Two paths.
- **Munnr:** Paths 3 (MCP server publishing), 1 (skill CLI subcommands). Two paths.
- **Hjarta:** none.
- **Smiðja:** none.

Total estimated lift across all ten paths: ~2,600 LOC code + ~1,500 LOC tests, ~5,000 LOC inclusive. Ember today is ~10,000 LOC (per slice-2 retrospective). After all ten paths: ~15,000 LOC. Still well within Vow-of-Smallness territory and well under Hermes's 200 MB.

## 13. Compatibility matrix

| Path | Affects Vows | Affects Cross-Platform | Affects Existing Tests | Risk |
|---|---|---|---|---|
| 1 — Skills | Smallness ✅ | None | Adds `pyyaml` requirement (already needed for config) | Low |
| 2 — Provider/transport | Modular ✅ | None | Refactors Ollama tests | Low (well-scoped) |
| 3 — MCP server | Smallness ✅ (opt-in) | Stdio universal | Adds `mcp` extra | Low |
| 4 — MCP client | Smallness ✅ (opt-in) | Stdio universal | Subprocess management | Medium (process lifecycle) |
| 5 — Parallel tools | Smallness ✅, Honest Memory ✅ | None | Adds concurrency tests | Medium (race conditions) |
| 6 — Memory provider | Pluggable Storage ✅ | None | Refactors Brunnr-write call sites | Medium (scope) |
| 7 — Exhaustion TTL | Graceful Offline ✅ | None | Adds typed-value tests | Low |
| 8 — Retry policy | Graceful Offline ✅ | None | Formalizes existing | Low |
| 9 — Interrupt | Honest Memory ✅ | None | Adds interrupt tests | Low |
| 10 — Bg persistence | Honest Memory ⚠ | None | Adds drain tests | Medium (data loss on bug) |

## What This Means for Ember

**True Names affected:** primarily Funi (five paths); Strengr (two); Brunnr (two); Munnr (two). Hjarta and Smiðja are untouched by this batch of integration paths — their shapes are confirmed by the crosswalk as already-correct-at-current-scale.

**Vows touched:**
- *Reinforced:* all ten Vows have at least one path reinforcing them. The strongest reinforcements: Vow of Smallness (every path is sized; total stays ≤ 15k LOC), Vow of Modular Authorship (every path is failable independently), Vow of Graceful Offline (paths 7, 8, 9 deepen the typed-value discipline).
- *Watched:* Vow of Honest Memory — Path 10 (background persistence) is the only one that could regress this Vow if implemented carelessly. Deferred for that reason.
- *No path violates a Vow* in its proposed form.

**Concrete next step:** [[60_synthesis/64_MIGRATION_PLAN]] arranges these ten paths into phased deliveries. The ordering is *not* strictly the order presented here — the migration plan optimises for *each phase being independently valuable and reversible*, not for *the order they were listed in this doc*.

**Cross-references:**
- [[60_synthesis/64_MIGRATION_PLAN]] — sequencing.
- [[60_synthesis/65_SLICE_PLAN_REVISIONS]] — proposed changes to Ember's existing slice plan, instantiating these paths.
- [[60_synthesis/66_DECISION_RECORDS]] — ADR-Proposed records for the most consequential adoption decisions.
- [[20_interface/20_MCP_INTEGRATION]], [[20_interface/21_RPC_INTERFACE]], [[20_interface/22_SKILL_INTERFACE]], [[20_interface/23_PROVIDER_INTERFACE]] — the contracts each path consumes.

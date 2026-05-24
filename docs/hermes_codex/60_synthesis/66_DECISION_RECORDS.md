---
codex_id: 66_DECISION_RECORDS
title: Decision Records — ADR-Proposed for the Most Consequential Adoptions
role: Cartographer
layer: Synthesis
status: draft
hermes_source_refs:
  - "(synthesises 60–65)"
ember_subsystem_targets: [Funi, Strengr, Brunnr, Munnr]
cross_refs:
  - 60_synthesis/60_HERMES_VS_EMBER_CROSSWALK
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/63_INTEGRATION_PATHS
  - 60_synthesis/64_MIGRATION_PLAN
  - 60_synthesis/65_SLICE_PLAN_REVISIONS
---

# 66 — Decision Records (ADR-Proposed)

> *Decisions outlive the people who make them. A record is a kindness to whoever comes next.*
> — Védis Eikleið, sealing the proposals into envelopes

## 0. Posture — Proposed, not Ratified

Every record below is **Status: Proposed**. None are decisions yet. They follow Ember's existing ADR style (per `docs/decisions/0001-mythic-engineering-bootstrap-2026-05-17.md` and peers) but live here under `docs/hermes_codex/60_synthesis/` to keep the actual `docs/decisions/` directory unmodified.

If the Skald + Architect + Volmarr ratify any of these, the next step is **copy the record from this doc into `docs/decisions/NNNN-<slug>.md` with the appropriate ADR number and Status: Ratified**, and reference the Hermes Codex as the source.

The records use a compact ADR shape: **Context → Decision → Consequences → Status**. Each is sized to be reviewable in 3-5 minutes.

## ADR-Proposed-Skill-001 — Skills as Markdown documents with YAML frontmatter

**Status:** Proposed (Cartographer, 2026-05-22)

**Context.** Hermes ships ~30 in-repo skill categories and a `~/.hermes/skills/` user-local tree. Each skill is a directory containing one `SKILL.md` file with YAML frontmatter and a Markdown body. The shape is enforced by a 12-rule validator at `tools/skill_manager_tool.py:217-253`. The validator is the entire contract; everything else (`metadata.hermes.related_skills`, `version`, `author`, `license`, `tags`) is convention. Skills are *procedural memory* — readable by the agent for "how to" patterns, never databases of fact.

Ember currently has no skill subsystem. Procedural patterns are encoded in the system prompt directly, which scales poorly past 3-4 patterns.

**Decision.** Adopt Hermes's skill contract verbatim — port the validator, the discovery walk, the two-tree structure (`src/ember/skills/` in-repo + `~/.ember/skills/` user-local), and the `skills_list` / `skill_view` tools. Reject the security-scan-on-scripts surface (Ember skills are read-only documents; no `scripts/` execution). Adopt the constants `MAX_NAME_LENGTH = 64`, `MAX_DESCRIPTION_LENGTH = 1024`, `MAX_SKILL_CONTENT_CHARS = 100_000`.

**Consequences.**
- Adds `src/ember/spark/funi/skills/` (~250 LOC) and 5 seed skills (~33 KB) to slice 3.
- `pyyaml` requirement remains; already present via `config` extra.
- Funi's prompt assembly gains a "Available Skills" block (~1500 tokens).
- Operator-facing CLI: `ember skills list/view`.
- Agent-initiated skill writes deferred to ADR-Proposed-Skill-002.
- Cross-platform: pure stdlib + yaml; no platform-specific code.

**Vow check:** Smallness ✅, Pluggable Storage ✅ (skills are content, not infrastructure), Modular Authorship ✅, Public-Friendliness ✅, Open Knowledge ✅ (adapted skills carry attribution to `obra/superpowers` per the original).

**Hermes references:**
- `tools/skill_manager_tool.py:107-275`
- `skills/software-development/hermes-agent-skill-authoring/SKILL.md`
- [[20_interface/22_SKILL_INTERFACE]]

---

## ADR-Proposed-Skill-002 — Agent-initiated skill writes (audited)

**Status:** Proposed (Cartographer, 2026-05-22)

**Context.** Hermes's `skill_manage(action="create", ...)` tool lets the agent itself write new skills mid-conversation. The skill becomes visible to the *next* session (loader is session-start cached). This closes the procedural-memory loop: the agent solves a problem, writes down the procedure, future sessions consult the procedure.

Ember after ADR-Proposed-Skill-001 has read-only skills. Adding agent-initiated writes is the natural next step but introduces audit and trust concerns.

**Decision.** Add `skill_create(name, content)` as a registered tool, gated by config flag `skills.allow_agent_creation: false` (default false; operator opt-in). All agent-initiated writes:
1. Land in `~/.ember/skills/<name>/SKILL.md` (user-local tree only — never in-repo).
2. Include mandatory frontmatter fields `author: ember-agent` and `provenance: session/<session_id>`.
3. Are audit-logged with the full SKILL.md content (or its SHA-256 if larger than 16 KB).
4. Are rejected if the validator fails (with a clear error returned to the agent).
5. Are visible in `ember skills list` with a `[agent-created]` marker.

**Consequences.**
- ~80 LOC code + audit-log integration.
- Operator can see, edit, delete agent-created skills.
- Operator can disable via the config flag.
- Vow of Honest Memory preserved: every write traceable.
- Vow of Public-Friendliness preserved: the operator sees what Ember learned.

**Vow check:** all ten Vows respected.

**Hermes references:**
- `tools/skill_manager_tool.py:713-790`
- [[20_interface/22_SKILL_INTERFACE]] §5

---

## ADR-Proposed-Funi-001 — Provider profile + transport split

**Status:** Proposed (Cartographer, 2026-05-22)

**Context.** Funi today has a single Protocol (`FuniHandle`) with `complete()` and `complete_streaming()` methods, and one concrete adapter (Ollama). The shape works for one provider; it does not scale to a second (LM Studio, llama.cpp HTTP, OpenAI-compatible servers).

Hermes solves this with a two-layer split: a *declarative* `ProviderProfile` dataclass (`providers/base.py:38-185`) and a *behavioural* `ProviderTransport` ABC (`agent/transports/base.py:1-90`). Adding a new provider is a ~30-line plugin file when it uses an existing api_mode; ~200 lines when it needs a new transport.

**Decision.** Refactor Funi into the two-layer pattern:
1. `FuniProfile` dataclass — declarative metadata (name, runtime_kind, env_vars, base_url, default_aux_model). Drop Hermes hooks (`prepare_messages`, `build_extra_body`, `build_api_kwargs_extras`) for v1; add them back when a second runtime arrives.
2. `FuniTransport` Protocol — five required methods (`runtime_kind`, `convert_messages`, `convert_tools`, `build_kwargs`, `normalize_response`); two optional (`validate_response`, `map_finish_reason`). Skip `extract_cache_stats` for v1.
3. `NormalizedFuniResponse`, `ToolCall` (with `function` backward-compat property), `Usage` shared types.
4. Filesystem-walk provider discovery via `src/ember/spark/funi/plugins/` mirror of Hermes's `plugins/model-providers/`.
5. Refactor existing Ollama adapter into `transports/ollama.py` and `plugins/ollama/__init__.py`.

**Consequences.**
- Net LOC change: +140.
- The future second provider (LM Studio, llama.cpp HTTP, OpenAI-compat) becomes ~80 LOC plugin + ~150 LOC transport (if a new api_mode is needed).
- `funi.runtime` config key now references profile name.
- All existing tests update to the new shape in the same PR.

**Vow check:** Modular Authorship ✅ (broken plugin doesn't crash Funi); Smallness ✅ (declarative + shared transport reduces per-provider LOC); Unbroken Whole ✅ (atomic refactor; one phase).

**Hermes references:**
- `providers/base.py:1-185`
- `agent/transports/base.py:1-90`
- `agent/transports/types.py:1-160`
- [[20_interface/23_PROVIDER_INTERFACE]]

---

## ADR-Proposed-Funi-002 — Tool batch parallelism with rules engine + interrupt fan-out

**Status:** Proposed (Cartographer, 2026-05-22)

**Context.** Funi today dispatches tool calls sequentially. For batches like "read these three files" or "search the well and the web", wall-clock is unnecessarily long.

Hermes parallelises via a rules engine at `agent/tool_dispatch_helpers.py:103-146`. The rules are declarative (three small `frozenset`s at module scope). Path-overlap is exact-prefix. The thread pool is hard-capped at 8. Worker prologue is rigorously disciplined: thread-id registration, interrupt fan-out, callback propagation, ContextVar copying, post-execution cleanup.

Interrupt handling treats user interrupt as a first-class RPC primitive: pending tools get *synthetic cancellation messages* so the wire protocol's "every tool_call has a result" invariant is preserved.

**Decision.** Adopt Hermes's parallelism rules engine and worker prologue verbatim:
1. `_MAX_TOOL_WORKERS = 8`.
2. `_NEVER_PARALLEL_TOOLS = frozenset()` (no clarify-shaped tool yet in Ember).
3. `_PARALLEL_SAFE_TOOLS = frozenset({"read_local_file", "search_well", "fetch_url"})`.
4. `_PATH_SCOPED_TOOLS = frozenset({"read_local_file"})`.
5. Path-overlap check exactly as Hermes: prefix-based, pessimistic.
6. Worker prologue: register tid, copy_context, propagate activity callback, unregister and clear interrupt on exit.
7. Synthetic cancellation message for skipped tools.
8. Config flag `tools.parallel: true` (default true) — operator can disable.

**Consequences.**
- ~250 LOC code + 200 LOC tests.
- Parallel batches see 40-70% wall-clock reduction (depending on tool I/O profile).
- Interrupt during a parallel batch produces clean cancellation messages.
- ContextVar-based concurrency is the right primitive (not threading.local).

**Vow check:** Smallness ✅ (cap at 8 workers, configurable down); Honest Memory ✅ (synthetic cancellations preserve invariant); Modular Authorship ✅ (worker failure doesn't crash dispatcher).

**Hermes references:**
- `agent/tool_dispatch_helpers.py:103-146`
- `agent/tool_executor.py:65-465` (worker prologue at 197-271)
- [[20_interface/21_RPC_INTERFACE]]

---

## ADR-Proposed-MCP-001 — Ember as MCP server (read-only subset)

**Status:** Proposed (Cartographer, 2026-05-22)

**Context.** ADR 0014 (already-ratified, in Ember's existing ADR set) commits to bidirectional MCP intent. Slice 2 did not implement it. Hermes's `mcp_serve.py` is a 31 KB, 897-line MCP server exposing 10 tools — five conversation-reading, three event-handling, two for sending and approval. It uses FastMCP over stdio with a mtime-keyed SQLite poll for events.

Ember's Brunnr already has the SQLite substrate. Adding a small MCP server is a low-cost, high-value addition.

**Decision.** Ship `ember mcp serve` as an opt-in extra (`pip install ember-agent[mcp]`). Initial surface: **five read-only tools**.
1. `sessions_list` — list Ember sessions.
2. `session_get` — detailed info for one.
3. `episodes_read` — read recent Episodes from a session.
4. `events_poll` — non-blocking event-since-cursor.
5. `events_wait` — long-poll with timeout.

Use FastMCP over stdio. Lazy `mcp` import. EventBridge polls Brunnr's `episode` table mtime every 200 ms. `_coerce_int` discipline at every tool boundary.

Reject (for now): `messages_send` (needs Gjallarhorn), `permissions_respond` (needs audit-log integration), `attachments_fetch` (multimodal future), HTTP transport (stdio is sufficient).

**Consequences.**
- ~545 LOC + 250 LOC tests.
- Ember becomes citizen of the MCP ecosystem.
- Operator can connect Claude Desktop, Cursor, or another agent to her Well.
- Default off (`mcp_server.enabled: false`); operator opt-in.

**Vow check:** Smallness ✅ (opt-in extra; lazy import); Modular Authorship ✅ (mcp absent → REPL fine); Honest Memory ✅ (read-only; no mutation); Public-Friendliness ✅ (`ember mcp serve` is a plain command).

**Hermes references:**
- `mcp_serve.py:450-859`
- [[20_interface/20_MCP_INTEGRATION]]

---

## ADR-Proposed-MCP-002 — MCP-initiated tool calls require operator opt-in

**Status:** Proposed (Cartographer, 2026-05-22)

**Context.** When Ember publishes an MCP server (ADR-Proposed-MCP-001), an external peer agent could in principle call Funi tools through Ember. This is a real surrender of authority — a peer agent gets Ember's tool surface.

**Decision.** Default `mcp_server.allow_remote_tools: false`. When `true`, every MCP-initiated tool call:
1. Carries the originating client_id in its audit-log entry.
2. Goes through the same approval framework as operator-initiated calls (per ADR 0011).
3. Cannot bypass standing-trust policy.
4. Is visible in the audit log as `triggered_by: mcp(client_id)`.

Approvals over MCP are *not* automated. The operator at the CLI must still approve, unless the standing-trust policy permits.

**Consequences.**
- Operator retains full authority.
- Peer agents get *read* tools by default (which are not gated); *write* tools require explicit opt-in.
- Audit log shows which side initiated each tool call.

**Vow check:** Honest Memory ✅ (full traceability); Public-Friendliness ✅ (operator controls authority); Modular Authorship ✅ (the boundary is mechanical).

**Hermes references:**
- `mcp_serve.py:823-857`

---

## ADR-Proposed-MCP-003 — Ember as MCP client; per-server registration

**Status:** Proposed (Cartographer, 2026-05-22)

**Context.** Hermes consumes external MCP servers via `tools/mcp_tool.py` + `agent/transports/hermes_tools_mcp_server.py`. Each external server's tools are registered with a `mcp_<server>_<tool>` namespace. Parallel-safety is determined by the server's advertised capabilities, not Hermes's guess.

For Ember, this means: an operator can install a filesystem MCP server, a sqlite MCP server, a fetch MCP server, etc., and their tools appear in Funi's tool list automatically. The ecosystem multiplier is large.

**Decision.** Ship MCP client support in slice 4 (per [[60_synthesis/65_SLICE_PLAN_REVISIONS]]). Configuration via `~/.ember/config/mcp_servers.yaml`. Each entry specifies command, args, working directory. On Ember startup, MCP clients are spawned as subprocesses (stdio). Their tools are introspected and registered with `mcp_<server>_<tool>` naming.

Parallel-safety: respect the server's advertised capability per the MCP spec.

Audit: every MCP-tool invocation records the server name in the audit log.

**Consequences.**
- ~410 LOC + 200 LOC tests.
- New CLI: `ember mcp-servers list/add/remove`.
- A flaky MCP server is contained: its tools become unavailable; other tools and Funi continue.
- Drain timeout + `os._exit(0)` fallback for stuck shutdown (per Hermes pattern).

**Vow check:** Smallness ✅ (opt-in extra); Modular Authorship ✅ (server crash contained); Honest Memory ✅ (audited).

**Hermes references:**
- `agent/tool_dispatch_helpers.py:90-100` (parallel-safety query)
- [[20_interface/20_MCP_INTEGRATION]] §5

---

## ADR-Proposed-Strengr-001 — Typed retry policy + per-error-code TTL exhaustion

**Status:** Proposed (Cartographer, 2026-05-22)

**Context.** Strengr today has basic retry with backoff. Hermes's credential pool implements per-error-code TTL exhaustion (`401 → 5min`, `429 → 1hr`, default `1hr`) and parses provider-supplied `Retry-After` values (epoch seconds, milliseconds, ISO-8601 strings, and natural-language hints like "retry after 12 seconds").

When a network or provider failure becomes a typed *Unavailable until X* rather than a generic "tried 3 times and gave up", the operator's mental model improves substantially.

**Decision.** Add to Strengr:
1. `EXHAUSTED_TTL_401_SECONDS = 5 * 60`.
2. `EXHAUSTED_TTL_429_SECONDS = 60 * 60`.
3. `EXHAUSTED_TTL_DEFAULT_SECONDS = 60 * 60`.
4. `parse_retry_after(value)` — port `_parse_absolute_timestamp` + `_extract_retry_delay_seconds` from `agent/credential_pool.py:208-248`.
5. `RetryPolicy` dataclass with `next_delay(attempt, retry_after)` method.
6. Extend the existing `Unavailable` typed value to optionally carry `until: float | None`.

**Consequences.**
- ~180 LOC code + 160 LOC tests.
- Munnr's disconnect banner can show "until ~14:30" when the provider supplies a reset time.
- `ember doctor` can report each provider's exhaustion state.

**Vow check:** Graceful Offline ✅ (the central Vow this serves); Honest Memory ✅ (typed values, not silent failures).

**Hermes references:**
- `agent/credential_pool.py:75-77, 199-248`
- `agent/retry_utils.py`

---

## ADR-Proposed-Brunnr-001 — Memory provider plug-in ABC (Vinátta reserved)

**Status:** Proposed (Cartographer, 2026-05-22)

**Context.** Hermes's `MemoryProvider` ABC at `agent/memory_provider.py:42-280` is a behavioural plug-in surface for external "brain" services (Honcho, Mem0, Hindsight). It has 10+ hooks (`prefetch`, `sync_turn`, `system_prompt_block`, `on_turn_start`, `on_session_end`, `on_pre_compress`, `on_memory_write`, `on_delegation`, `get_tool_schemas`, `handle_tool_call`, `shutdown`). Only one external provider runs at a time (enforced to prevent tool-schema bloat).

Ember today has no equivalent. Brunnr is *storage* — pluggable across SQLite-vec/pgvector/Qdrant/Chroma/LanceDB — but not *behavioural*.

The True Name **Vinátta** is reserved (per [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]]) for this future subsystem.

**Decision.** Ship the `MemoryProvider` Protocol in slice 4 (per [[60_synthesis/65_SLICE_PLAN_REVISIONS]]). Built-in provider wraps Brunnr's direct write path. External providers (Honcho, Mem0) ship as separate optional extras (`ember-agent[vinatta-honcho]` etc.) and are not part of the default install.

The Vinátta name is *reserved-but-not-yet-realized* — in documentation but not in code until an external provider lands.

Reuse Hermes's `sanitize_context` regex set (`agent/memory_manager.py:43-59`) to strip fence tags and system-note patterns from any provider-injected text. This is the Vow-of-Tethered-Grounding safety port.

**Consequences.**
- ~250 LOC code + 120 LOC tests.
- Brunnr's direct-write path becomes the built-in provider.
- Funi's prompt assembly calls `memory_manager.prefetch_all(query)`.
- Operators wanting external memory get a documented integration point.

**Vow check:** Pluggable Storage ✅ (adds an axis of plugability, consistent with the Vow); Tethered Grounding ✅ (sanitization mandatory); Smallness ✅ (no external provider in default install).

**Hermes references:**
- `agent/memory_provider.py:42-280`
- `agent/memory_manager.py:1-200`
- `plugins/memory/`

---

## ADR-Proposed-Brunnr-002 — Background Episode persistence (with mandatory drain)

**Status:** Proposed (Cartographer, 2026-05-22; requires Auditor pass)

**Context.** Ember's current Episode persistence is synchronous on the main thread. On a Pi 5 measuring run, this adds ~30-50 ms per turn. Hermes uses background persistence with a queue + daemon thread + drain-on-close.

The Vow of Honest Memory forbids losing an Episode. A crash mid-write must not lose data.

**Decision.** Defer to slice 5. When shipped:
1. Episodes go into an internal `queue.Queue` from the main thread.
2. A daemon thread drains the queue into Brunnr.
3. A small write-ahead log (`~/.ember/well/episode_wal.jsonl`) persists in-flight entries.
4. Adapter `close()` blocks until queue is drained.
5. On startup, WAL is replayed (entries that were committed to Brunnr are removed from WAL; entries that weren't are committed and then removed).
6. **Auditor (Sólrún Hvítmynd) must do a dedicated correctness pass before this ships.**

**Consequences.**
- ~120 LOC + 100 LOC tests, but the *correctness bar is the highest* of any phase.
- Average turn latency drops ~50 ms on Pi 5.
- Crash recovery preserves all Episodes.

**Vow check:** Honest Memory ⚠ — must be carefully done. Other Vows ✅.

**Hermes references:**
- `agent/memory_manager.py::sync_all` pattern.

---

## ADR-Proposed-MetaSlice-001 — Slice plan template additions

**Status:** Proposed (Cartographer, 2026-05-22)

**Context.** Hermes ships `docs/decisions/HERMES_OPENCLAW_DESIGN_ANTI_PATTERNS.md` — an explicit list of design patterns that Hermes consciously rejects from another agent project (OpenClaw). This is a healthy artefact. Ember's slice plans don't yet have an equivalent — the rejections are *implicit*.

**Decision.** Add to every future Ember slice plan template:
1. An **"Anti-Patterns Inherited"** section that enumerates the Hermes patterns the slice deliberately did *not* adopt and why.
2. A **"Cross-Platform Acceptance"** subsection that explicitly lists Pi 5, Linux, macOS, Windows, WSL verification.
3. A **"Hermes Reference"** subsection per ADR linking to Hermes source paths and Codex doc IDs.

**Consequences.**
- Slice plans grow by ~500-1000 words.
- The rejections become traceable.
- Cross-platform expectations become explicit per slice, not just in the global plan.
- The Hermes lineage stays visible in perpetuity.

**Vow check:** Open Knowledge ✅ (every decision documented).

---

## Summary table — all proposed ADRs

| ID | Topic | Slice | Affects Vows | Risk |
|---|---|---|---|---|
| Skill-001 | Skill subsystem (read-only) | 3 | none | Low |
| Skill-002 | Agent-initiated skill writes | 4 | Honest Memory (mitigated) | Low |
| Funi-001 | Provider profile + transport split | 3 | none | Low |
| Funi-002 | Tool batch parallelism + interrupt fan-out | 3 | Honest Memory (mitigated) | Medium |
| MCP-001 | Ember as MCP server (read-only) | 3 | Honest Memory (mitigated) | Low |
| MCP-002 | MCP-initiated tools require opt-in | 3 | Honest Memory ✅ | Low |
| MCP-003 | Ember as MCP client | 4 | Honest Memory (mitigated) | Medium |
| Strengr-001 | Typed retry + exhaustion TTL | 3 | none (deepens Graceful Offline) | Low |
| Brunnr-001 | Memory provider ABC (Vinátta reserved) | 4 | Tethered Grounding (sanitization mandatory) | Low |
| Brunnr-002 | Background Episode persistence | 5 | Honest Memory (auditor pass) | High |
| MetaSlice-001 | Slice plan template additions | meta | none | Low |

## What This Means for Ember

**True Names affected:** Funi (Funi-001, Funi-002), Strengr (Strengr-001), Brunnr (Brunnr-001, Brunnr-002), Munnr (MCP-001, MCP-002, MCP-003). Hjarta and Smiðja untouched in this proposal batch.

**Vows touched:**
- *Most strengthened:* Honest Memory (six ADRs touch it, all with mitigations).
- *Most reinforced:* Modular Authorship (every ADR has opt-in extras and failable subsystems).
- *Most clarified:* Graceful Offline (Strengr-001 deepens it; ADR-Proposed for typed exhaustion).
- *Most watched:* Honest Memory specifically for Brunnr-002 — the only High-risk ADR.

**Concrete next step for the keeper:**
1. Review each ADR-Proposed above.
2. For each, decide: Accept, Defer, or Reject.
3. For Accept: copy to `docs/decisions/NNNN-<slug>.md` with appropriate ADR number; status becomes Ratified; reference this Codex doc.
4. For Defer: note in a planning doc; revisit at the next slice ratification.
5. For Reject: record the rejection rationale in a brief addition to this doc (Cartographer can update on request).

**Cross-references:**
- [[60_synthesis/65_SLICE_PLAN_REVISIONS]] — the slice-shaped bundling that uses these ADRs.
- [[60_synthesis/64_MIGRATION_PLAN]] — the phase sequencing.
- [[60_synthesis/63_INTEGRATION_PATHS]] — the file-level integration details.
- [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] — the Gjallarhorn and Vinátta name reservations referenced.

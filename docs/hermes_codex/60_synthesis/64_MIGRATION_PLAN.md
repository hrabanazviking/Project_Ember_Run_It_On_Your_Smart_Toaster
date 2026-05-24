---
codex_id: 64_MIGRATION_PLAN
title: Migration Plan — Phased Evolution Toward Post-Hermes Capability
role: Cartographer
layer: Synthesis
status: draft
hermes_source_refs:
  - "(synthesises 60_HERMES_VS_EMBER_CROSSWALK + 63_INTEGRATION_PATHS)"
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 60_synthesis/60_HERMES_VS_EMBER_CROSSWALK
  - 60_synthesis/61_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/62_DEPENDENCY_FLOW
  - 60_synthesis/63_INTEGRATION_PATHS
  - 60_synthesis/65_SLICE_PLAN_REVISIONS
  - 60_synthesis/66_DECISION_RECORDS
---

# 64 — Migration Plan: Sequenced, Reversible, Vow-Honouring

> *No path becomes a road by being long. It becomes a road by being walked the same way often enough that the grass forgets to grow back.*
> — Védis Eikleið, on the cost of phase boundaries

## 0. Premise and constraints

Ember has shipped slice 1 (ADR 0007) and slice 2 (ADR 0013). She is at v0.2.0. The migration plan in this document **does not modify the existing slice plan** — that work lives in [[60_synthesis/65_SLICE_PLAN_REVISIONS]] (proposes only). Here, the plan is articulated as a *separate sequence* of post-slice-2 phases — call them **M-phases** (M for Migration) to keep them distinct from slice-numbering.

Each M-phase has:
- **Prereqs** — what must be in place before starting.
- **Deliverables** — concrete files / features / docs.
- **Exit criteria** — testable, observable conditions.
- **Rollback** — how to undo the phase without harming earlier phases or operator data.
- **Reversibility class** — see §1.

Phases are *sequenced* but **not strictly serial** — some phases can run in parallel if the team's resourcing allows. The annotations make the parallelism explicit.

## 1. Reversibility classes

Each phase is rated by how cleanly it can be rolled back:

- **Class A — Code-only revert.** Reverting the commit set fully removes the phase. No data migration, no operator-visible state.
- **Class B — Code revert + config flag.** Reverting the commits removes most of the phase; an opt-in config flag (`feature.x: false`) is the safe-default off switch for the rest.
- **Class C — Code revert + small data migration.** Reverting requires either deleting a small new SQLite table or downgrading a schema field that was added optionally.
- **Class D — Code revert + significant data migration.** Reverting could lose data or require a non-trivial migration script. (No phase below is D.)

The plan **forbids Class D** for the migration phases. If a phase would otherwise be D, it gets split until each part is A/B/C.

## 2. Phase summary at a glance

| Phase | Title | Class | Vow risk | Path # from [[60_synthesis/63_INTEGRATION_PATHS]] | Estimated effort |
|---|---|---|---|---|---|
| M1 | Skills subsystem v1 (read-only) | A | none | Path 1 (most of it) | 1-2 weeks |
| M2 | Provider/transport refactor | A | none | Path 2 | 1 week |
| M3 | MCP server (read-only) | B | Honest Memory (mitigated) | Path 3 | 1-2 weeks |
| M4 | Tool parallelism + interrupt fan-out | B | Honest Memory (mitigated) | Paths 5, 9 | 1 week |
| M5 | MCP client (consume external tools) | B | Honest Memory (mitigated via audit) | Path 4 | 1-2 weeks |
| M6 | Strengr typed retry + exhaustion TTL | A | none | Paths 7, 8 | 3-5 days |
| M7 | Memory provider plug-in ABC | C | Pluggable Storage (reinforced) | Path 6 | 1-2 weeks |
| M8 | Agent-initiated skill writes | C | Honest Memory (audited) | Path 1 (deferred portion) | 1 week |
| M9 | Background Episode persistence | C | Honest Memory (carefully) | Path 10 | 1 week |
| M10 | Strengr credential pool (multi-credential) | C | Smallness (post-stress-test) | Path beyond 7 | 1-2 weeks |

Total estimated effort: ~12-16 weeks of focused work. The plan is **not** time-boxed to that — operator pull and slice-3+ priorities will reorder.

## 3. Phase dependencies (Hasse diagram)

```
                        M1 (skills)
                          │
                          ▼
                        M2 (provider refactor)
                          │
              ┌───────────┼───────────────┐
              ▼           ▼               ▼
            M3 (MCP    M4 (parallel    M6 (retry +
            server)    tools +         exhaustion)
              │        interrupt)         │
              │           │               │
              │           ▼               │
              │         M5 (MCP client)   │
              │           │               │
              ▼           ▼               ▼
              ────── M7 (memory provider ABC) ──────
                          │
                          ▼
                        M8 (agent-initiated skill writes)
                          │
                          ▼
                        M9 (background persistence)
                          │
                          ▼
                       M10 (multi-credential pool)
```

Reading edges as "depends on":
- M2 (refactor) depends on M1 (skills) because skills surface into the prompt, and the prompt assembly path is touched by the refactor; doing them in the same edit reduces churn.
- M4 (parallel tools) depends on M2 because parallel dispatch operates on `ToolCall` instances; the refactor formalizes the shape.
- M5 (MCP client) depends on M4 because MCP tools share the parallelism infrastructure.
- M7 (memory provider) depends on the refactor (M2) for the provider-style discovery pattern.
- M8, M9, M10 are later refinements that build on the foundation.

M3 (MCP server publishing) is unusually decoupled — it depends on M2 only for shape-consistency in the data it exposes; it could ship in parallel with M4.

## 4. Phase M1 — Skills subsystem v1 (read-only)

**Prereqs:**
- Slice 2 shipped (config loader, streaming Funi, pgvector Brunnr, tool framework).
- `pyyaml` already a dependency via the `config` extra.

**Deliverables:**
- `src/ember/spark/funi/skills/{__init__.py, loader.py, manifest.py, surfacer.py}` — the four-file core (per [[60_synthesis/63_INTEGRATION_PATHS]] Path 1, items 1-4).
- `src/ember/spark/funi/tools/{skill_view.py, skill_list.py}` — two new tools.
- `src/ember/spark/munnr/skill_commands.py` — operator CLI subcommands (no `create` yet; that lands in M8).
- `src/ember/skills/_seed/*` — 5 seed skills (per [[60_synthesis/63_INTEGRATION_PATHS]] Path 1, items 12-16).
- ADR-Proposed-Skill-001: "Skills as Markdown documents with YAML frontmatter — adoption from Hermes."
- Tests: `tests/unit/test_skill_loader.py`, `tests/unit/test_skill_surfacer.py`, `tests/integration/test_skill_commands.py`.

**Exit criteria:**
- `ember skills list` shows the five seeded skills with their descriptions.
- `ember skills view writing-plans` prints the body.
- Funi's system prompt assembly includes a "Available Skills" section (~1500 tokens) with the list.
- Funi-the-model successfully calls `skill_view("writing-plans")` to read a skill mid-turn (tested manually).
- All 488 existing tests still pass.
- New tests pass.

**Rollback (Class A):**
- Revert the commits. The five seed skills directory is removed. The CLI subcommands return to absent. The prompt assembly returns to slice-2 shape. No data migration; the operator has not been writing skills yet.

**Risk notes:** none. The Vow of Smallness is satisfied (+600 LOC); the Vow of Modular Authorship is satisfied (the skill subsystem failure is silently degraded — system prompt loses the section, Ember keeps working).

---

## 5. Phase M2 — Provider/transport refactor

**Prereqs:** M1 (skills) shipped, because Funi's prompt assembly is now stable.

**Deliverables:**
- `src/ember/spark/funi/profile.py` — `FuniProfile` dataclass.
- `src/ember/spark/funi/transports/{__init__.py, base.py, types.py, ollama.py}` — the transport layer.
- `src/ember/spark/funi/plugins/ollama/__init__.py` — first provider plugin.
- `src/ember/spark/funi/handle.py` — refactored as a thin wrapper.
- ADR-Proposed-Funi-001: "Provider profile + transport split, adopted from Hermes `providers/` + `agent/transports/`."

**Exit criteria:**
- All slice-1 and slice-2 acceptance tests pass.
- The `funi.runtime` config key now references the profile name (`"ollama"`).
- Switching to a hypothetical second profile (mock OpenAI-compat HTTP) works by config edit alone — no code change. (Validated via test fixture, no real second provider yet.)
- LOC count: net +140 LOC; Funi total ≤ 2,500 LOC (under the slice-2 retrospective baseline).

**Rollback (Class A):**
- Revert the commits. The original `ollama/adapter.py` shape returns. Config edits to `funi.runtime` revert.

**Risk notes:** the refactor is the highest-churn phase by line count. The risk is *test churn* — many slice-1/2 tests reference the old shape. Mitigation: do the refactor in a single PR with test edits in the same commit; verify all tests still pass before merge.

---

## 6. Phase M3 — MCP server (read-only)

**Prereqs:** M2 (provider refactor) shipped to ensure the data shapes the MCP server exposes are stable.

**Deliverables:**
- `src/ember/spark/munnr/mcp/{__init__.py, server.py, event_bridge.py, coerce.py}`.
- `src/ember/cli/mcp.py` — `ember mcp serve` subcommand.
- `pyproject.toml` extra: `mcp = ["mcp>=1.2"]`.
- ADR-Proposed-MCP-001: "Ember as MCP server (read-only); operator opt-in; default off."
- ADR-Proposed-MCP-002: "MCP-initiated tool calls require operator opt-in via `mcp_server.allow_remote_tools: false` default."
- Tests: `tests/unit/test_mcp_server.py`, `tests/integration/test_mcp_event_bridge.py`.

**Exit criteria:**
- `pip install ember-agent[mcp]` installs cleanly on Linux, macOS, Windows.
- `ember mcp serve` starts the stdio MCP server.
- A reference MCP client (mcptools or a small test harness) lists 5 read-only tools: `sessions_list`, `session_get`, `episodes_read`, `events_poll`, `events_wait`.
- The event bridge wakes within 250 ms of a new Episode write.
- Stopping the server (Ctrl-C, parent process exits) releases all resources within 1 s.

**Rollback (Class B):**
- Revert commits removes the server code. Operators who had `mcp_server.enabled: true` in their config get a clean "unknown key" warning on next start.
- The `mcp` extra remains in pip's cache; uninstall is `pip uninstall mcp`.

**Risk notes:**
- *Vow of Honest Memory:* the read-only subset of MCP tools cannot mutate state. Approved.
- *Vow of Modular Authorship:* `mcp` extra missing → `ember mcp serve` errors with a friendly install hint, REPL unaffected. Approved.

---

## 7. Phase M4 — Tool parallelism + interrupt fan-out

**Prereqs:** M2 (transport refactor) shipped; M3 can ship in parallel.

**Deliverables:**
- `src/ember/spark/funi/tools/dispatch.py` — promoted to `dispatch_sequential` + `dispatch_parallel`.
- `src/ember/spark/funi/tools/interrupt.py` — `InterruptRegistry`.
- ADR-Proposed-Funi-002: "Tool batch parallelism with rules engine, adopted from Hermes `agent/tool_dispatch_helpers.py`."
- Tests: `tests/unit/test_dispatch_parallel.py`, `tests/unit/test_interrupt.py`.

**Exit criteria:**
- A batch of three `read_local_file` calls with disjoint paths runs in < 60% of the sequential time on the test fixture.
- A batch with overlapping paths falls back to sequential.
- A Ctrl-C during a parallel batch causes pending tools to be skipped with synthetic cancellation messages; running tools have ~3 s to exit gracefully.
- `contextvars.copy_context()` is used at every executor submit (verified via code review checklist + a unit test that asserts a context-var value is preserved in a worker).

**Rollback (Class B):**
- Revert commits removes the parallel path. The `tools.parallel: false` config flag (added in the same phase) is the safe-default off switch. Operators always get sequential dispatch.

**Risk notes:**
- *Vow of Honest Memory:* synthetic cancellation messages preserve the wire-protocol guarantee that every `tool_call` has exactly one matching result. Approved.
- *Race conditions:* the worker-tid registration race (per `agent/tool_executor.py:209-213`) is a real risk. Mitigation: port the exact Hermes ceremony, including the recheck of `_interrupt_requested` after registration.

---

## 8. Phase M5 — MCP client

**Prereqs:** M4 (parallelism) shipped, because MCP-tool dispatch uses the same parallel infrastructure.

**Deliverables:**
- `src/ember/spark/funi/tools/mcp_client.py` — generic MCP client tool.
- `src/ember/spark/funi/tools/mcp_dispatch.py` — dispatch with audit-log integration.
- `src/ember/cli/mcp_servers.py` — `ember mcp-servers list/add/remove`.
- `config/ember.example.yaml` — `mcp_clients:` block with examples.
- ADR-Proposed-MCP-003: "Ember as MCP client; each external server is operator-installed; tools registered with `mcp_<server>_<tool>` naming."
- Tests with a fake MCP server fixture.

**Exit criteria:**
- An operator can `ember mcp-servers add <name> --command "python -m mcp_test_server"` and on next REPL start, the test server's tools appear in `skills_list` (and the agent can invoke them).
- An MCP server crash is contained: Funi marks the affected tools as unavailable and continues.
- Audit-log entries for MCP tool calls include the server name.

**Rollback (Class B):**
- Revert commits removes client code. Operator's `mcp_clients` config block becomes ignored with a warning.

**Risk notes:**
- *Vow of Honest Memory:* every MCP call audited. Approved.
- *Process lifecycle:* MCP servers are subprocesses; their lifecycle (start, drain, terminate) is non-trivial. Mitigation: copy the Hermes pattern verbatim — daemon threads, drain timeouts, fallback to `os._exit(0)` on truly stuck shutdown.

---

## 9. Phase M6 — Strengr typed retry + exhaustion TTL

**Prereqs:** none (orthogonal to other phases; can ship any time after slice 2).

**Deliverables:**
- `src/ember/thread/strengr/exhaustion.py` — TTL constants + parsers.
- `src/ember/thread/strengr/retry.py` — `RetryPolicy` class.
- ADR-Proposed-Strengr-001: "Typed retry policy with provider-supplied retry-after parsing; per-error-code TTL exhaustion."
- Tests: `tests/unit/test_exhaustion.py`, `tests/unit/test_retry_policy.py`.

**Exit criteria:**
- Strengr's network call wrapper now classifies HTTP errors and produces typed `Unavailable(reason, until)` values.
- A simulated 429 with `Retry-After: 60` produces an `Unavailable` with `until ≈ now + 60`.
- All existing Strengr tests still pass.

**Rollback (Class A):**
- Revert commits. The existing typed-`Disconnected` values continue working unchanged.

**Risk notes:** none.

---

## 10. Phase M7 — Memory provider plug-in ABC

**Prereqs:** M2 (provider refactor) shipped — the pattern is consistent across model providers and memory providers.

**Deliverables:**
- `src/ember/well/memory_provider.py` — `MemoryProvider` Protocol.
- `src/ember/well/memory_manager.py` — orchestrator.
- `src/ember/well/brunnr/builtin_provider.py` — Brunnr-direct wrapped as the built-in provider.
- ADR-Proposed-Brunnr-001: "Memory provider plug-in ABC; reserved True Name **Vinátta**; default install ships only built-in."
- Tests.

**Exit criteria:**
- The Vinátta surface exists as the `MemoryProvider` Protocol.
- Brunnr's direct write path continues working as the built-in provider.
- Funi's prompt assembly calls `memory_manager.prefetch_all(query)`.

**Rollback (Class C):**
- Revert commits removes the Protocol. Brunnr's direct path returns. **No data migration required** — the Brunnr schema is unchanged; the Protocol was a code-level abstraction only.

**Risk notes:**
- *Vow of Pluggable Storage:* the Vinátta layer adds an axis of plugability; consistent with the Vow.
- *Vow of Tethered Grounding:* a memory provider can inject content into the prompt. Every injected block goes through `sanitize_context()` (port the regex from `agent/memory_manager.py:43-59`) to strip fence tags and the system-note pattern. **This is the critical safety port.**

---

## 11. Phase M8 — Agent-initiated skill writes

**Prereqs:** M1 (skills v1) shipped, plus M2 (audit log integration via the tool registry).

**Deliverables:**
- `src/ember/spark/funi/tools/skill_create.py` — registered tool: `skill_create(name, content)`.
- `src/ember/spark/funi/skills/security.py` — minimal validation (no scripts, no symlinks).
- ADR-Proposed-Skill-002: "Agent-initiated skill creation; audit-logged; written to `~/.ember/skills/` (user-local tree only)."

**Exit criteria:**
- An operator opt-in flag `skills.allow_agent_creation: false` (default false) controls availability.
- When enabled, the agent can call `skill_create(...)`.
- Every agent-created skill carries `author: ember-agent` and `provenance: session/<session_id>` in its frontmatter.
- Every creation is audit-logged.
- A SKILL.md that fails the validator is rejected with a clear message back to the model.

**Rollback (Class C):**
- Revert commits. Already-created agent skills remain on disk under `~/.ember/skills/`. Operator can delete them.

**Risk notes:**
- *Vow of Honest Memory:* every write audited. The audit log entries include the SKILL.md content (or its SHA-256).
- *Vow of Public-Friendliness:* the operator must be able to see "Ember created a skill X" in the audit log without spelunking.

---

## 12. Phase M9 — Background Episode persistence

**Prereqs:** all earlier phases shipped (this is a Brunnr optimisation, applied late).

**Deliverables:**
- `src/ember/well/brunnr/sqlite_vec/adapter.py` — queue-and-drain background writer.
- ADR-Proposed-Brunnr-002: "Background Episode persistence with mandatory drain on close."

**Exit criteria:**
- Average turn latency drops by ~50 ms on a Pi 5 measurement run.
- Crash before drain produces zero lost Episodes (a small write-ahead log persists the in-flight queue to a file; recovered at next start).

**Rollback (Class C):**
- Revert commits. The synchronous write returns. **Drain pending writes first, then revert** — operator data must not be lost.

**Risk notes:**
- *Vow of Honest Memory:* this is the riskiest Vow boundary in the plan. The crash-safety requirement (write-ahead log) is non-negotiable.
- This phase is the only one where I would recommend a **post-implementation audit** by the Auditor (Sólrún Hvítmynd) before shipping. The other phases are routine; this one touches the most sacred Vow.

---

## 13. Phase M10 — Multi-credential pool

**Prereqs:** M6 (typed retry) shipped, plus operator pull (a real-world need).

**Deliverables:**
- `src/ember/thread/strengr/credential_pool.py` — pool with rotation strategies.
- ADR-Proposed-Strengr-002: "Multi-credential pool with `fill_first`/`round_robin`/`random`/`least_used` strategies, adopted from Hermes `credential_pool.py`."

**Exit criteria:**
- An operator can configure two credentials for the same provider; the pool rotates.
- Per-error-code TTL exhaustion (already shipped in M6) drives skip-and-retry-next-credential.

**Rollback (Class C):**
- Revert commits. Single-credential resolution returns. Operator's `credential_pool: [...]` config block is ignored with a warning.

**Risk notes:**
- *Vow of Smallness:* a multi-credential pool is the boundary of what Ember v1 should carry. **Defer until two operators independently request it.** Do not pre-implement.

---

## 14. Phasing cadence and parallelism

A focused team could ship:

- **M1 + M2 + M6** in parallel (3-4 weeks).
- **M3 + M4** in parallel after M2 (1-2 weeks).
- **M5** after M4 (1-2 weeks).
- **M7** after M2 (1-2 weeks).
- **M8** after M1 + M7 (1 week).
- **M9** after M8 (1 week, with auditor pass).
- **M10** deferred indefinitely until operator pull.

End-to-end without M10: ~10-14 calendar weeks for a 1-2-person team. The plan is **incrementally valuable**: each phase, on its own, leaves Ember better than it found her.

## 15. Stop conditions

The plan stops if:
1. **Any phase fails to satisfy its Vow check** — return to design, do not ship.
2. **Test count regresses** — every phase must add tests; the baseline of 488 (slice 2) only goes up.
3. **Pi-5 acceptance test runtime exceeds 1 second** — the slice-2 test currently runs in 0.2 s; the plan keeps the small footprint.
4. **Total LOC across `src/ember/` exceeds 25k** — Vow-of-Smallness ceiling; if approaching, the next phase is *consolidation*, not addition.

The plan also stops if **operator pull dries up.** Ember is not a project that exists to consume the plan; the plan exists to serve Ember. When the operator's lived needs diverge from the plan, the operator wins.

## What This Means for Ember

**True Names affected:** every True Name across the plan, in proportion. Funi gets the most (M1, M2, M4, M5, M8 — five phases). Strengr gets two (M6, M10). Brunnr gets two (M7, M9). Munnr gets two (M3, plus skill CLI in M1). Hjarta and Smiðja are intentionally untouched — their slice-2 shape is the right size.

**Vows touched:**
- *Reinforced:* every Vow is touched by at least one phase that strengthens it.
- *Watched throughout:* Vow of Smallness — total LOC ceiling, total test runtime ceiling. The plan respects both.
- *Most consequential phase:* M9 (background Episode persistence). Honest Memory is the strictest Vow; this phase has the highest cost of getting it wrong. Auditor pass required.

**Concrete next step:**
1. Ratify [[60_synthesis/61_TRUE_NAME_REASSIGNMENT]] — the Gjallarhorn and Vinátta reservations.
2. Begin M1 (skills) — it is the highest-value, lowest-risk first phase.
3. Begin M2 (transport refactor) and M6 (retry/exhaustion) in parallel if resources allow.
4. After M2, M3 and M7 can launch.

**Cross-references:**
- [[60_synthesis/63_INTEGRATION_PATHS]] — file-level integration details for each phase.
- [[60_synthesis/65_SLICE_PLAN_REVISIONS]] — proposed revisions to Ember's official slice plan that incorporate these phases.
- [[60_synthesis/66_DECISION_RECORDS]] — ADR-Proposed records for the most consequential adoption decisions.

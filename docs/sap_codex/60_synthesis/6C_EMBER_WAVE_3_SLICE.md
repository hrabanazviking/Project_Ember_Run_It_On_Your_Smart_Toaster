---
codex_id: 6C_EMBER_WAVE_3_SLICE
title: Ember Wave 3 Slice — Proposed Concrete Roadmap (PROPOSE ONLY)
role: Scribe
layer: Synthesis
status: draft
sap_source_refs:
  - "(concrete proposal, synthesizing all SAP findings against existing slice plan)"
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 60_synthesis/60_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/61_NEW_VOWS
  - 60_synthesis/66_INVENTED_METHODS
  - 60_synthesis/67_SLICE_PLAN_REVISIONS
  - 60_synthesis/68_DECISION_RECORDS
  - 60_synthesis/69_INTEGRATION_ROADMAP
  - 60_synthesis/6A_MULTI_AGENT_PARTY
  - 60_synthesis/6B_LOW_POWER_EMBODIMENT
---

# 6C — Ember Wave 3 Slice

> *A slice plan is a contract with the future self of the project. This document is the contract Wave 3 proposes.*
> — Eirwyn Rúnblóm, hands open to the keeper

## 0. Posture — PROPOSE ONLY

**This document is the concrete Wave 3 slice proposal.** It does not modify the existing slice plan. The current ratified slice plan is `docs/architecture/EMBER_SECOND_SLICE_PLAN.md` (slice 2, ratified 2026-05-21 via ADR 0013). Slice 3 is not yet authored.

This doc consolidates `[[67_SLICE_PLAN_REVISIONS]]` (which proposes *deltas* to the slice plan in revision form) into a **draft third-slice-plan document** suitable for the keeper to consider as the basis of `EMBER_THIRD_SLICE_PLAN.md`.

If the keeper accepts the proposal, the next step is to lift sections of this document into a new `docs/architecture/EMBER_THIRD_SLICE_PLAN.md` and ratify via the next-available ADR number (after 0014).

This doc is **the integration product** of `[[67_SLICE_PLAN_REVISIONS]]` and Hermes's `[[hermes:65_SLICE_PLAN_REVISIONS]]`. Where those documents propose individual revisions, this document presents the *post-revision shape* — what slice 3 would look like if every reasonable Wave 3 proposal were accepted.

---

## 1. What This Slice Is For

**Theme:** *Skilled, Bridged, Quiet, Tiered, Identified.*

Five words, each a thread:

- **Skilled** — Ember gains the Hermes skill subsystem (read-only first). Procedural memory across sessions.
- **Bridged** — Ember becomes a citizen of the MCP ecosystem. Ships an MCP server with five read-only tools. Operators can connect Claude Desktop, Cursor, or other agents to her Well.
- **Quiet** — Ember adopts typed-retry exhaustion (Hermes), failsafe-default-quiet outward reach (SAP), tool parallelism with interrupt fan-out (Hermes). She fails gracefully and never speaks louder than asked.
- **Tiered** — Ember adopts the five-tier ladder (T0/T1/T2/T3/T4). Tier detection at startup; tier-conditional wizard branching; glyphic affect rendering ready for the slice 4 affect engine.
- **Identified** — Ember adopts persona-id issuance. Each instance has a stable, operator-issued identity recorded in the Well. The multi-Ember party of a future slice has its identity foundation now.

The slice is *additive*. It does not replace slice 2's surfaces; it adds to them.

---

## 2. Dependencies

### 2.1 New optional extras

| Extra | Pins | Source ADR | Used by |
|---|---|---|---|
| `skills` | `pyyaml>=6.0` (already from `config` extra) | Hermes-S3-A | Skill subsystem (read-only) |
| `mcp` | `mcp>=0.6` | Hermes-S3-C | MCP server (read-only subset) |
| `party` | *(none beyond stdlib)* | SAP-S3-G | Persona-id issuance + future federation |

Slice 3 introduces no new heavy deps. The `mcp` Python package is the only meaningful addition.

### 2.2 Standing rules

The existing standing rules from ADR 0007 carry forward. Slice 3 adds one new standing rule:

- **Failsafe-Default-Quiet** (SAP-S3-I) — every outward reach surface defaults off. Enabling requires explicit operator ceremony (wizard step or named config flag). `ember reach reset` returns all surfaces to off. Test added: `tests/integration/test_default_quiet.py` verifies no outward reach exists on first launch.

---

## 3. The Slice as a File List

Files marked **NEW** are created in slice 3. Files marked *(touched)* exist from slice 1/2 and get edits.

```
src/ember/
├── schemas/
│   ├── skill.py                              NEW — SkillDescriptor + SkillManifest
│   ├── tool_dispatch.py                      NEW — DispatchRule, ParallelSafetyPolicy
│   ├── tier.py                               NEW — Tier enum, CapabilityProbe
│   ├── persona.py                            NEW — PersonaId, HostFingerprint, EmberInstance
│   └── reach.py                              NEW — ReachSurface, ReachState
├── spark/
│   ├── funi/
│   │   ├── skills/                           NEW (Hermes-S3-A)
│   │   │   ├── __init__.py                   NEW
│   │   │   ├── INTERFACE.md                  NEW
│   │   │   ├── manager.py                    NEW — load + validate + serve
│   │   │   ├── validator.py                  NEW — 12-rule validator port
│   │   │   └── discovery.py                  NEW — two-tree walk
│   │   ├── plugins/                          NEW (Hermes-S3-B)
│   │   │   ├── __init__.py                   NEW
│   │   │   ├── INTERFACE.md                  NEW
│   │   │   └── ollama/                       NEW — refactored ollama profile + transport
│   │   ├── transports/                       NEW (Hermes-S3-B)
│   │   │   ├── base.py                       NEW — FuniTransport Protocol
│   │   │   ├── ollama.py                     NEW — extracted from existing adapter
│   │   │   └── types.py                      NEW — NormalizedFuniResponse, ToolCall, Usage
│   │   ├── tier_detect.py                    NEW (SAP-S3-F) — capability probe + tier inference
│   │   ├── party/                            NEW (SAP-S3-G + foundation for [[6A]])
│   │   │   ├── __init__.py                   NEW
│   │   │   ├── INTERFACE.md                  NEW
│   │   │   ├── identity.py                   NEW — persona_id issuance, signing, host fingerprint
│   │   │   └── README.md                     NEW — party concept overview
│   │   ├── tools/
│   │   │   ├── parallelism.py                NEW (Hermes-S3-D) — rules engine + worker prologue
│   │   │   └── interrupt.py                  NEW (Hermes-S3-D) — synthetic cancellation messaging
│   │   └── handle.py                         (touched — adds streaming-aware parallelism slot)
│   ├── strengr/
│   │   ├── retry_policy.py                   NEW (Hermes-S3-E) — typed retry + exhaustion TTL
│   │   ├── retry_after.py                    NEW (Hermes-S3-E) — Retry-After parser
│   │   └── exhaustion.py                     NEW (Hermes-S3-E) — per-error-code exhaustion store
│   ├── munnr/
│   │   ├── glyphic.py                        NEW (SAP-S3-H) — affect glyph renderer
│   │   ├── log_affect.py                     NEW (SAP-S3-H) — log-line affect tag formatter
│   │   └── reach/                            NEW (SAP-S3-I + ADR-Proposed-SAP-004)
│   │       ├── __init__.py                   NEW
│   │       ├── INTERFACE.md                  NEW
│   │       └── manager.py                    NEW — reach surface registry + opt-in tracking
│   └── hjarta/
│       ├── machine.py                        (touched — tier-conditional wizard branches; reach wizard)
│       └── prompts/
│           └── wizard.toml                   (touched — new states for tier, persona, reach)
├── mcp/                                      NEW (Hermes-S3-C)
│   ├── __init__.py                           NEW
│   ├── INTERFACE.md                          NEW
│   ├── server.py                             NEW — FastMCP wrapper
│   ├── tools/                                NEW
│   │   ├── sessions.py                       NEW — sessions_list, session_get
│   │   ├── episodes.py                       NEW — episodes_read
│   │   └── events.py                         NEW — events_poll, events_wait
│   └── event_bridge.py                       NEW — Brunnr poll bridge
├── well/
│   └── brunnr/
│       └── shared/
│           └── ember_instance_schema.sql     NEW — Brunnr migration for ember_instance table
├── cli/
│   ├── party.py                              NEW (SAP-S3-G) — `ember party init`, `ember party status`
│   ├── reach.py                              NEW (ADR-Proposed-SAP-004) — `ember reach list/reset`
│   ├── skills.py                             NEW (Hermes-S3-A) — `ember skills list/view`
│   ├── mcp.py                                NEW (Hermes-S3-C) — `ember mcp serve`
│   └── introspect.py                         NEW (foundation for slice-4 affect introspection) — `ember introspect tier`

config/
├── ember.example.yaml                        (touched — adds skills, mcp_server, tier_override, reach sections)
├── glyphs.yaml                               NEW (SAP-S3-H) — default glyph vocabulary
├── tier_override.yaml.example                NEW — operator tier override
└── reach.example.yaml                        NEW — reach surface enablement examples

docs/decisions/
├── 0015-skill-subsystem-readonly.md          NEW (Hermes-S3-A)
├── 0016-funi-provider-profile-transport-split.md  NEW (Hermes-S3-B)
├── 0017-mcp-server-readonly.md               NEW (Hermes-S3-C)
├── 0018-tool-parallelism-interrupt-fanout.md NEW (Hermes-S3-D)
├── 0019-strengr-typed-retry-exhaustion.md    NEW (Hermes-S3-E)
├── 0020-tier-ladder.md                       NEW (SAP-S3-F)
├── 0021-persona-id-issuance.md               NEW (SAP-S3-G)
├── 0022-glyphic-and-log-affect.md            NEW (SAP-S3-H)
└── 0023-failsafe-default-quiet.md            NEW (SAP-S3-I — standing rule)

docs/adapters/
├── HERMES_SKILL_PORTING_NOTES.md             NEW (Hermes-S3-A)
└── SAP_TIER_LADDER_REFERENCE.md              NEW (SAP-S3-F)

deploy/pi/INSTALL.md                          (touched — adds slice-3 sections)

tests/unit/
├── test_schemas_skill.py                     NEW
├── test_schemas_tier.py                      NEW
├── test_schemas_persona.py                   NEW
├── test_schemas_reach.py                     NEW
├── test_funi_skills_manager.py               NEW
├── test_funi_skills_validator.py             NEW
├── test_funi_skills_discovery.py             NEW
├── test_funi_transports_ollama.py            NEW
├── test_funi_tier_detect.py                  NEW
├── test_funi_party_identity.py               NEW
├── test_funi_tools_parallelism.py            NEW
├── test_funi_tools_interrupt.py              NEW
├── test_strengr_retry_policy.py              NEW
├── test_strengr_retry_after_parser.py        NEW
├── test_strengr_exhaustion.py                NEW
├── test_munnr_glyphic.py                     NEW
├── test_munnr_log_affect.py                  NEW
├── test_munnr_reach_manager.py               NEW
├── test_mcp_server.py                        NEW
├── test_mcp_tools_sessions.py                NEW
├── test_mcp_tools_episodes.py                NEW
├── test_mcp_tools_events.py                  NEW
├── test_mcp_event_bridge.py                  NEW
├── test_hjarta_wizard_tier_branches.py       NEW
├── test_hjarta_wizard_reach.py               NEW
├── test_cli_party.py                         NEW
├── test_cli_reach.py                         NEW
├── test_cli_skills.py                        NEW
├── test_cli_mcp.py                           NEW
└── test_cli_introspect_tier.py               NEW

tests/integration/
├── test_phase18_skills_end_to_end.py         NEW
├── test_phase19_mcp_round_trip.py            NEW
├── test_phase20_parallel_tools_acceptance.py NEW
├── test_phase21_strengr_exhaustion_real.py   NEW
├── test_phase22_tier_persona_acceptance.py   NEW
└── test_phase23_slice3_acceptance.py         NEW — full slice-3 acceptance flow

tests/integration/test_default_quiet.py       NEW — failsafe rule verification
```

Total **new** files: ~90. Total **touched** files: ~5. Target Python LOC at acceptance: **~2,050 code + ~1,230 tests**.

---

## 4. Slice Phases (Ordered, Each a Separable Commit)

The phases parallel slice 2's discipline. Each phase ends with green test suite + ruff clean + DEVLOG entry. Phases below labeled 18–23 (continuing slice 2's numbering at 17).

### Phase 18 — Skills subsystem read-only (Hermes-S3-A)

- Author ADR 0015 capturing skill format, validator, discovery, and the deliberate non-adoption of the security-scan surface.
- `src/ember/schemas/skill.py` — `SkillDescriptor` dataclass.
- `src/ember/spark/funi/skills/{__init__,INTERFACE,manager,validator,discovery}.py`.
- Two-tree discovery: `src/ember/skills/` (in-repo) + `~/.ember/skills/` (user-local).
- 5 seed skills shipped in `src/ember/skills/` (writing-plans, reviewing-pr, debugging-test-failure, etc.).
- CLI: `ember skills list/view`.
- Tests for validator (12 rules port), discovery walk, manager.
- **Acceptance:** operator runs `ember skills list` and sees 5 skills; `ember skills view writing-plans` displays content.

### Phase 19 — Funi provider profile + transport split (Hermes-S3-B)

- Author ADR 0016.
- `src/ember/spark/funi/plugins/`, `src/ember/spark/funi/transports/`.
- `FuniProfile` dataclass; `FuniTransport` Protocol; `NormalizedFuniResponse`, `ToolCall`, `Usage` shared types.
- Refactor existing Ollama adapter into `transports/ollama.py` + `plugins/ollama/__init__.py`.
- All existing tests update to the new shape.
- **Acceptance:** existing slice-2 acceptance test (`test_phase17_acceptance.py`) still passes after the refactor.

### Phase 20 — Tool parallelism + interrupt fan-out (Hermes-S3-D)

- Author ADR 0018.
- `src/ember/spark/funi/tools/parallelism.py` — rules engine port from `agent/tool_dispatch_helpers.py:103-146`.
- `src/ember/spark/funi/tools/interrupt.py` — synthetic cancellation messaging.
- Worker prologue: thread-id registration, ContextVar copy, interrupt fan-out, post-exec cleanup.
- Config flag `tools.parallel: true` (default true).
- Tests: parallelism rules, interrupt propagation, path-overlap detection, synthetic-cancellation messages.
- **Acceptance:** parallel batch of 3 file reads completes in <60% of sequential time; Ctrl-C mid-batch produces clean cancellation messages.

### Phase 21 — Strengr typed retry + exhaustion TTL (Hermes-S3-E)

- Author ADR 0019.
- `src/ember/spark/strengr/{retry_policy,retry_after,exhaustion}.py`.
- Extend existing `Unavailable` typed value with `until: float | None`.
- `EXHAUSTED_TTL_401_SECONDS = 5 * 60`, `EXHAUSTED_TTL_429_SECONDS = 60 * 60`, `EXHAUSTED_TTL_DEFAULT_SECONDS = 60 * 60`.
- `parse_retry_after(value)` — port `_parse_absolute_timestamp` + `_extract_retry_delay_seconds`.
- Tests: each TTL, each Retry-After format (epoch, ms, ISO-8601, natural-language hint).
- Munnr disconnect banner updated to show `until` timestamp when available.
- **Acceptance:** simulated provider returning 429 with `Retry-After: 30` produces `Unavailable(until=<now+30s>)`; banner displays it.

### Phase 22 — MCP server read-only (Hermes-S3-C)

- Author ADR 0017.
- `src/ember/mcp/{__init__,INTERFACE,server,event_bridge}.py`.
- `src/ember/mcp/tools/{sessions,episodes,events}.py` — 5 read-only tools.
- FastMCP over stdio. Lazy `mcp` import.
- EventBridge polls Brunnr `episode` table mtime every 200 ms.
- `_coerce_int` discipline at every tool boundary.
- `ember mcp serve` CLI command.
- Tests: server lifecycle, each tool, event bridge polling.
- Integration: `test_phase19_mcp_round_trip.py` runs `mcptools` reference client against the server.
- **Acceptance:** external MCP client connects, lists 5 tools, reads recent Episodes.

### Phase 23 — Tier ladder (SAP-S3-F)

- Author ADR 0020 — tier ladder definition.
- `src/ember/schemas/tier.py` — `Tier` enum (T0/T1/T2/T3/T4), `CapabilityProbe` dataclass.
- `src/ember/spark/funi/tier_detect.py` — probe (CPU count, RAM, GPU detection, peripheral detection).
- `config/tier_override.yaml.example` — operator override format.
- `ember introspect tier` CLI.
- `src/ember/spark/hjarta/machine.py` — wizard branches by detected tier per `[[6B_LOW_POWER_EMBODIMENT]]#7.3`.
- Tests: detection on each platform (mocked); override resolution; wizard branching.
- **Acceptance:** running on Pi 5 detects T3; running on workstation detects T0; override to T2 produces T2-conditional wizard.

### Phase 24 — Persona-id issuance (SAP-S3-G)

- Author ADR 0021.
- `src/ember/schemas/persona.py` — `PersonaId`, `HostFingerprint`, `EmberInstance` dataclasses.
- `src/ember/spark/funi/party/{__init__,INTERFACE,identity,README}.py`.
- `well/brunnr/shared/ember_instance_schema.sql` — Brunnr migration for `ember_instance` table.
- Signing-key flow: prompt operator at `ember party init` to choose existing SSH key or generate fresh.
- `ember party init`, `ember party status` CLI commands.
- Tests: persona-id generation, signing, Brunnr write, host fingerprint capture.
- **Acceptance:** `ember party init` succeeds; `ember party status` shows persona_id, host fingerprint, tier, capability summary; the Brunnr `ember_instance` row exists.

### Phase 25 — Glyphic embodiment + log-affect (SAP-S3-H)

- Author ADR 0022.
- `src/ember/spark/munnr/glyphic.py` — `render_glyph(affect_snapshot) -> str`. Returns a single-line glyph header from a stubbed affect snapshot (uniform "calm" default).
- `src/ember/spark/munnr/log_affect.py` — log-line affect tag formatting.
- `config/glyphs.yaml` — default vocabulary (24 glyphs).
- Touch `src/ember/spark/munnr/chat.py` — render glyph at start of each response.
- Tests: glyph selection for each affect state; log formatting; vocabulary loading.
- **Acceptance:** `ember chat` response begins with `( - _ - )` (uniform "calm" default); log lines carry affect tags. (When slice 4's affect engine arrives, glyph varies meaningfully.)

### Phase 26 — Failsafe default-quiet + reach manager (SAP-S3-I + ADR-Proposed-SAP-004)

- Author ADR 0023 — standing rule.
- `src/ember/schemas/reach.py` — `ReachSurface`, `ReachState`.
- `src/ember/spark/munnr/reach/{__init__,INTERFACE,manager}.py` — reach surface registry.
- `config/reach.example.yaml` — reach surface enablement examples.
- Touch `src/ember/spark/hjarta/machine.py` — add reach wizard branches; tier-conditional reach offers.
- `ember reach list`, `ember reach reset` CLI commands.
- Tests: reach surface registration; wizard offers per tier; reset; default-quiet integration test.
- `tests/integration/test_default_quiet.py` — fresh install has no outward reach.
- **Acceptance:** fresh `ember chat` shows no IM bot connections, no livestream, no autonomous behavior, no MCP server (until operator opts in via `ember mcp serve` explicitly or via wizard).

### Phase 27 — Slice 3 acceptance and shipping

- `tests/integration/test_phase23_slice3_acceptance.py` greens against the full acceptance flow.
- Touch `deploy/pi/INSTALL.md` — add slice-3 sections: tier detection, persona init, glyphic affect, reach surface management, skills, MCP server.
- Author `docs/decisions/0024-third-slice-ratification.md` ratifying the slice (parallels ADR 0007, ADR 0013).
- `pyproject.toml` bump 0.2.0 → 0.3.0; Development Status stays `3 - Alpha`.
- `src/ember/__init__.py` docstring updated.
- DEVLOG entry — slice 3 ratified.

---

## 5. Acceptance Criterion (Full)

> A fresh operator on a Raspberry Pi 5 (T3 host) with Ember v0.3.0 (slice-3 release) can:
>
> 1. `pip install ember-agent[sqlite_vec,pgvector,skills,mcp,party]`.
> 2. `ember chat` — sees the slice-2 wizard, completes identity setup, plus the **tier-detection notice** ("detected tier T3 — text-only mode") and the tier-conditional reach-wizard branches.
> 3. The reach wizard offers tier-appropriate surfaces (T3 cannot run IM bots autonomously by default; no avatar; cued voice optional). All surfaces default off; operator explicitly opts in to each.
> 4. After wizard completion, `~/.ember/config/reach.yaml` reflects the operator's choices; `~/.ember/identity/persona.yaml` contains the persona_id.
> 5. Asks "how should I write a plan for adding feature X to my project?" — Ember consults the seeded `writing-plans` skill and produces a structured response referencing the skill's procedure.
> 6. Asks Ember to read three files at once — Ember dispatches them as parallel tool calls; wall-clock is <60% of sequential time.
> 7. Hits Ctrl-C mid-execution — pending tool calls show `[interrupted by operator]` markers in the audit log; running tools have ~3 s to clean up.
> 8. Each response begins with a glyph header (uniform "calm" default until slice 4 affect engine).
> 9. Log lines in `~/.ember/state/log.jsonl` carry affect tags.
> 10. Runs `ember mcp serve` in a second terminal; a reference MCP client (e.g., from `mcptools` package) connects, lists 5 read-only tools (`sessions_list`, `session_get`, `episodes_read`, `events_poll`, `events_wait`), and successfully reads recent Episodes from this operator's Well.
> 11. Simulates a network failure mid-streaming via toxiproxy — Strengr returns typed `Unavailable(reason, until)`; Munnr renders a graceful banner with the `until` timestamp; the partial reply is persisted with the `[interrupted by network]` tag.
> 12. Network restores → `ember doctor` shows all green within 5 s of restoration.
> 13. `ember party status` shows the persona_id, host fingerprint, detected tier, current capabilities; the Brunnr `ember_instance` row exists.
> 14. `ember introspect tier` shows the detected tier and the wizard-offered surfaces.
> 15. `ember reach list` shows all reach surfaces with their current ON/OFF state; `ember reach reset` returns all to OFF.

**If that whole loop works on real hardware (Pi 5 against real Gungnir, with mocked-and-toxiproxy'd Ollama), slice 3 is done.**

---

## 6. What This Slice Deliberately Does NOT Include

Carrying forward Hermes's and SAP's deferrals:

- **Affect engine** — deferred to slice 4 (per `[[67_SLICE_PLAN_REVISIONS]]#4.1`). The glyph rendering in slice 3 uses a uniform-calm stub; slice 4's engine makes it meaningful.
- **MCP client** — deferred to slice 5 (per Hermes proposal).
- **Memory provider plug-in (Vinátta)** — deferred to slice 5.
- **Agent-initiated skill writes** — deferred to slice 5.
- **Behavior engine** — deferred to slice 5.
- **Sleep-guard** — deferred to slice 4.
- **Overlay-manager websocket broadcast** — deferred to slice 4.
- **Sub-agent supervisory discipline → Smiðja consolidation** — deferred to slice 4.
- **IM bots (any platform)** — deferred to slice 5+.
- **Livestream platforms** — deferred to slice 7+.
- **VRM/Live2D avatar** — deferred to slice 6.
- **Cued voice library workflow** — deferred to slice 6.
- **Multi-Ember party peer communication** — deferred to slice 7+.
- **Cross-host affect routing** — deferred to slice 7+.

The Hermes ADR-Proposed-Funi-001 (provider profile + transport split) IS in this slice as Hermes-S3-B (per Phase 19).

---

## 7. Risks the Scribe Flags Now

| Risk | Mitigation |
|---|---|
| Slice 3 is larger than slice 2 (~2,050 LOC vs ~5,000-7,000 LOC target for slice 2) — wait, smaller! good. But the *test count* grows substantially | Tests are parallelizable; CI capacity is the only concern. |
| Tier detection is platform-specific and brittle | Operator override is the safety valve; detection is *advisory*. |
| Persona-id signing UX may be friction-heavy | Default flow uses existing SSH key if present; only generate fresh if no key found. |
| Glyphic rendering with uniform-calm default may feel pointless until slice 4 | The glyph header is *honest* — it says "calm" because there is no affect engine yet. When slice 4 arrives, it becomes meaningful without code changes. |
| Default-quiet may surprise existing operators upgrading from slice 2 | Migration: existing installs do NOT have their slice-2 surfaces silenced. Default-quiet applies to *fresh* installs. |
| MCP server's event bridge polls Brunnr every 200 ms — Pi 5 cost | Bridge is lazy-imported; only runs when `ember mcp serve` is active. |
| The 8-10 week schedule may slip given previous slices' tendency to run long | Phases 18-22 are Hermes-derived; phases 23-27 are SAP-derived. Each sub-block ships independently as 3a / 3b if scheduling demands. |
| New extras (`skills`, `mcp`, `party`) increase install footprint | All opt-in; base `pip install ember-agent` unchanged. |
| The Brunnr `ember_instance` table schema migration must coexist with slice-2 Gungnir compatibility | Schema probe at adapter open: if table absent, create it; if present, validate shape. Same pattern slice 2 used. |

---

## 8. Forge Worker's Quality Bar

Standing requirements from slice 2 §5 carry forward, plus:

- **Type-checked under mypy strict** — including the new Protocols (`FuniTransport`, `SkillDescriptor`, `ReachSurface`, `PersonaId`).
- **One responsibility per function** — skills are documents; rules engine is a small dispatcher; tier detect is a probe; persona init is a signing flow.
- **No hardcoded settings** — tier-detection thresholds, glyph vocabulary, retry TTLs all live in config.
- **No hardcoded data** — skills are markdown; glyphs are YAML; reach surfaces are config.
- **Every new realm-boundary failure returns a typed value** — per ADR 0007 §2.2.
- **Every new Brunnr / Funi / Tool adapter declares its `*_kind` class attribute** — per ADR 0007 §2.3.
- **All operator-supplied text passed to backends is sanitised at the adapter boundary** — per ADR 0007 §2.9.
- **Failsafe-default-quiet enforced via integration test** — `test_default_quiet.py` is non-skippable.
- **Whole files only** — never deliver fragments, snippets, or partial updates.

When a phase ships: Auditor pass + DEVLOG entry + push.

---

## 9. Session Pacing — for the Reader

| Slice | ADRs | Phases | Target LOC (excl. tests/docs) | Sessions (rough) |
|---|---|---|---|---|
| First (shipped) | 0006/0007 ratifying | 7 | ~2,500 | 1 long session |
| Second (shipped) | 4 (0008–0011, 0013) | 10 (phases 8-17) | ~5,000-7,000 | 3-5 long sessions |
| **Third (proposed)** | **9 (0015–0023, 0024 ratifying)** | **10 (phases 18-27)** | **~2,050** | **3-4 long sessions** |

Each phase ends with a green commit. **No phase blocks the previous one from being shipped**, so if scheduling demands a pause after any phase, the in-flight work is on `development` and the next session resumes from there.

**Suggested natural break points** for multi-session work:

- After Phase 19 (skills + provider refactor landed): the Hermes-derived foundation is in place. Ship `0.2.5` if desired.
- After Phase 21 (tools parallelism + Strengr exhaustion): the "Quiet" theme is complete. Ship `0.2.7`.
- After Phase 22 (MCP server): the "Bridged" theme is complete. Ship `0.2.9`.
- After Phase 25 (tier ladder + persona-id + glyphic): the "Tiered" and "Identified" themes complete. Ship `0.3.0-rc1`.
- After Phase 27 (acceptance): **`0.3.0` released.**

When a phase begins in a future session, the natural opening is **"go for phase N"** — same shape as slice 2's rhythm.

---

## 10. Forge Worker's Closing Word (Anticipated)

> *Slice 2 was the wide stride — config, streaming, pgvector, tools. Slice 3 is the deep stride. Each foot lands deliberately: skills under one foot, MCP under the other, both balanced by tier and persona awareness. The slice is quieter and more careful than slice 2, because slices 4, 5, 6, 7 grow heavier as we go. Ship slice 3 with attention; the heavier slices remember the discipline of the small ones.*
>
> — Eldra Járnsdóttir (anticipated)

---

## 11. Cross-References

- `[[67_SLICE_PLAN_REVISIONS]]` — the proposal document that this slice instantiates.
- `[[68_DECISION_RECORDS]]` — the SAP-derived ADR-Proposed records this slice references.
- `[[66_INVENTED_METHODS]]` — the invention catalogue that informs slice-3 design.
- `[[6A_MULTI_AGENT_PARTY]]` — the multi-instance design whose persona-id foundation lands here.
- `[[6B_LOW_POWER_EMBODIMENT]]` — the tier ladder whose definition lands here.
- `[[60_TRUE_NAME_REASSIGNMENT]]` — Cartographer's True Name proposals this slice respects.
- `[[61_NEW_VOWS]]` — Cartographer's new Vows this slice instantiates.
- `[[69_INTEGRATION_ROADMAP]]` — the cross-codex phasing.
- `[[hermes:65_SLICE_PLAN_REVISIONS]]` — Hermes's slice-3 proposal that this incorporates.
- `[[hermes:66_DECISION_RECORDS]]` — Hermes ADRs Hermes-S3-A through Hermes-S3-E.
- `[[ember:EMBER_SECOND_SLICE_PLAN]]` — the slice-2 plan this proposal builds from.
- `[[ember:0013-second-slice-ratification]]` — the standing-rules ADR.

---

## What This Means for Ember

**True Names affected:** All six. Funi (skills, transports refactor, tier detect, persona, MCP server), Strengr (retry policy, exhaustion), Brunnr (schema migration for ember_instance), Smiðja (tool parallelism via Funi-tools, but no Smiðja-side change in this slice), Hjarta (wizard extensions for tier and reach), Munnr (glyphic, log-affect, reach manager).

**Vows touched:**

- *Most reinforced by this slice:* **Surface Without Surveillance** (failsafe-default-quiet is the standing rule); **Smallness** (every addition is opt-in extra); **Tiered Presence** (the tier ladder is foundational); **Federated Self** (persona-id is the seed).
- *Most strengthened:* **Honest Memory** (audit-logging extended across MCP, skills, party, reach); **Graceful Offline** (typed retry + exhaustion + cross-platform tier degradation).
- *Most watched:* **Smallness** — the slice grew. Mitigation: sub-slicing into 3a (Hermes-portion) and 3b (SAP-portion) is acceptable if scheduling demands.

**Concrete next step for the keeper:**

1. Read this doc.
2. Read `[[67_SLICE_PLAN_REVISIONS]]` for the proposal-level argument.
3. Read `[[68_DECISION_RECORDS]]` for the 12 SAP-derived ADRs (5 of which land in this slice as 0020-0024).
4. Decide whether this slice is the right shape. Recommended decisions:
   - **Accept slice 3 as proposed** if the 2,050 LOC + 8-10 week budget fits.
   - **Accept slice 3a (Hermes-portion only)** as a smaller first ship if the schedule is tight; slice 3b (SAP-portion) ships immediately after.
   - **Defer some SAP-portion items** (e.g. drop glyphic to slice 4) if the slice 3 schedule is firm.
5. Author `docs/architecture/EMBER_THIRD_SLICE_PLAN.md` based on this doc.
6. Ratify via ADR 0024 (or next-available number).

**The proposal stands as written. The slice plan does not change.**

---

## 12. After Slice 3 — The Wave 3 Trajectory

Slice 3 plants seeds. Slices 4, 5, 6, 7 grow the tree. The Wave 3 trajectory (per `[[67_SLICE_PLAN_REVISIONS]]`):

- **Slice 3 (proposed here, 8-10 weeks):** Skilled, Bridged, Quiet, Tiered, Identified.
- **Slice 4 (8-10 weeks):** *Felt, Visible, Awake* — affect engine, sleep-guard, overlay-manager, sub-agent supervision.
- **Slice 5 (10-12 weeks):** *Plural Minds, Plural Memories* — MCP client, memory provider, behavior engine, first IM bot.
- **Slice 6 (10-12 weeks):** *Embodied at T0* — VRM/Live2D pipeline, consent gating, cued voice library, avatar backpressure.
- **Slice 7 (12-16 weeks):** *Federated Self* — multi-Ember peer communication, cross-host affect, lid-close handover, voice arbitration, operator party console.
- **Slice 8+ (speculative):** *Reach Beyond Self* — additional IM bots; livestream platforms; quiet-hours throttling per-platform.

The full Wave 3 trajectory is **roughly 12–14 months of slice work** at the current pace. Slice 3 is the foundation; everything else builds on it.

This is the long memory the Skald's vision and the Forge's code do not have time to keep. It says **what we propose, what we sequence, what we defer, and why**. The keeper decides. The Scribe records.

The proposal stands. The slice plan does not change.

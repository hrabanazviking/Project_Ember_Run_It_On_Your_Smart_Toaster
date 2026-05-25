---
codex_id: 68_DECISION_RECORDS
title: Decision Records — ADR-Proposed for SAP-Driven Adoption Decisions
role: Scribe
layer: Synthesis
status: draft
sap_source_refs:
  - py/affection_system.py:1-64
  - py/affection_api.py:1-29
  - py/behavior_engine.py:53-225
  - py/scheduler.py:1-134
  - py/autoBehavior.py:1-97
  - py/mcp_clients.py:1-189
  - py/vts_manager.py:1-235
  - py/moss_tts.py:1-267
  - py/sleep_guard.py:1-100
  - py/overlay_router.py:1-81
  - py/live_router.py:1-546
  - py/sub_agent.py:1-367
  - py/ClaudeAsOpenAI.py
  - py/GeminiAsOpenAI.py
  - config/settings_template.json
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 60_synthesis/60_TRUE_NAME_REASSIGNMENT
  - 60_synthesis/61_NEW_VOWS
  - 60_synthesis/62_PARTY_PROTOCOL
  - 60_synthesis/63_PERFORMANCE_TIER_ENGINE
  - 60_synthesis/64_AFFECTION_ENGINE_REIMAGINED
  - 60_synthesis/66_INVENTED_METHODS
  - 60_synthesis/67_SLICE_PLAN_REVISIONS
  - 60_synthesis/6A_MULTI_AGENT_PARTY
  - 60_synthesis/6B_LOW_POWER_EMBODIMENT
  - 60_synthesis/6C_EMBER_WAVE_3_SLICE
---

# 68 — Decision Records (ADR-Proposed)

> *Decisions outlive the people who make them. A record is a kindness to whoever comes next.*
> — Eirwyn Rúnblóm, sealing the SAP-derived proposals into envelopes

## 0. Posture — Proposed, not Ratified

Every record below is **Status: Proposed**. None are decisions yet. They follow Ember's existing ADR style (per `docs/decisions/0001-mythic-engineering-bootstrap-2026-05-17.md` and peers) but live here under `docs/sap_codex/60_synthesis/` to keep `docs/decisions/` untouched.

If Volmarr ratifies any of these, the next step is **copy the record into `docs/decisions/NNNN-<slug>.md` with the appropriate ADR number and Status: Ratified**, and reference this Codex doc.

The shape is **Context → Decision → Consequences → Alternatives Considered → Status**. Each is sized to be reviewable in 4–6 minutes.

Cross-referencing convention: each ADR also lists the inventions or methods it instantiates, by reference to `[[66_INVENTED_METHODS]]` numbered sections.

---

## ADR-Proposed-SAP-001 — Adopt MCP as Primary Tool & Federation Protocol

**Status:** Proposed (Scribe, 2026-05-24)

**Context.** SAP ships `mcp_clients.py:1-189` (an MCP client manager that supervises external MCP servers as child processes) and exposes its own tools through an MCP-compatible surface. Hermes ADR-Proposed-MCP-001 already commits Ember to ship as MCP server in slice 3. SAP's analysis reinforces this from a different angle: **MCP is the substrate that federated systems converge on**. Both Hermes and SAP independently arrived at MCP as the tool boundary; the ecosystem has settled.

For Ember, MCP is also the foundation for `[[6A_MULTI_AGENT_PARTY]]` — peers in a multi-Ember swarm communicate via MCP. Treating MCP as *the* protocol (not *a* protocol) simplifies the substrate.

**Decision.** Adopt MCP as Ember's primary tool & federation protocol. Specifically:

1. Ember as MCP server (per Hermes ADR-Proposed-MCP-001) — slice 3.
2. Ember as MCP client (per Hermes ADR-Proposed-MCP-003) — slice 4.
3. Inter-instance peer communication in the multi-Ember party also uses MCP (each Ember instance is both an MCP server and an MCP client to its peers).
4. Foreign-agent A2A calls (SAP's `a2a_tool.py` shape) also tunnel through MCP — Ember does not ship a separate A2A protocol surface.

**Consequences.**

- One protocol, one set of supervisory disciplines, one audit surface.
- Inter-instance party communication inherits all the trust-chain audit machinery from `[[66_INVENTED_METHODS]]#12`.
- `mcp` Python package becomes a slice-3 dep (already proposed by Hermes); no SAP-specific MCP deps needed.
- Smithy of tool integration becomes "wrap as MCP server" universally.

**Alternatives Considered.**

- *Native A2A protocol* (per SAP's `a2a_tool.py`) — rejected. A2A is one of several agent-to-agent shapes; MCP subsumes it.
- *Direct HTTP RPC* — rejected. Loses the supervisor-and-audit shape that MCP carries.
- *gRPC* — rejected. Adds a binary protocol surface without earning it.

**Vow check:** Smallness ✅ (one protocol vs. several), Honest Memory ✅ (audit shape is uniform), Modular Authorship ✅ (each MCP server is independently failable), Public-Friendliness ✅ (one shape for operators to learn), Open Knowledge ✅ (MCP is open spec).

**Instantiates inventions:** `[[66_INVENTED_METHODS]]#12` (recursive trust audit) builds on MCP audit shape.

**SAP references:**

- `/tmp/super-agent-party/py/mcp_clients.py:1-189`
- `/tmp/super-agent-party/py/a2a_tool.py`

**Hermes references:**

- ADR-Proposed-MCP-001 — Ember as MCP server (read-only).
- ADR-Proposed-MCP-003 — Ember as MCP client; per-server registration.

---

## ADR-Proposed-SAP-002 — Reject Gacha-Style Affect; Adopt Tethered Affect with Anchoring

**Status:** Proposed (Scribe, 2026-05-24)

**Context.** SAP's affection system is gacha-shaped. `/tmp/super-agent-party/py/affection_system.py:37-65` parses regex tags `<user=name love=N familiarity=N>` from LLM output and mutates a single JSON file (`affection_data.json`) under `USER_DATA_DIR`. The state is opaque, untethered to evidence, and explicitly designed to mimic gacha-game friendship bars. The affection_api (`affection_api.py:1-29`) exposes raw read/write to the JSON via FastAPI without consent or audit ceremony.

Ember's proposed Vow of **Embodied Honesty** forbids the gacha pattern. Vow of **Affective Restraint** requires the affect state to bias behavior without overriding consent or safety. Vow of **Tethered Grounding** requires every claim to anchor in the Well.

Cartographer's `[[64_AFFECTION_ENGINE_REIMAGINED]]` provides the reimagined design. This ADR is the **decision** to adopt that reimagined design and **reject** SAP's gacha shape entirely.

**Decision.** Adopt Cartographer's reimagined affect engine, with the following commitments:

1. **No regex-tag-parsing of LLM output for affect mutation.** Affect mutations are first-class typed calls, never side effects of model output.
2. **Every mutation anchors to Well chunks** (per `[[66_INVENTED_METHODS]]#8`). Mutations carry `anchor_chunk_ids: list[str]`. Mutations decay to zero when their anchor chunks are deleted from the Well.
3. **Telemetric introspection** (per `[[66_INVENTED_METHODS]]#5`). `ember introspect affect` is a first-class CLI showing each axis, current value, last-mutation source, decay trajectory, and a `why` field captured at mutation time.
4. **Receipt-bound provisional memory** (per `[[66_INVENTED_METHODS]]#14`). Model-proposed mutations land in a pending tray until operator confirmation.
5. **Affect-gated autonomous triggers** (per `[[66_INVENTED_METHODS]]#10`). Autonomous behavior consults receptivity axis before firing.

**Consequences.**

- ~600 LOC for the affect engine + introspection + provisional tray + anchoring.
- Storage migration: affect data moves from a flat JSON to a Brunnr table with axis rows + mutation history.
- The operator can see and steer Ember's affect state, including resetting it.
- Gacha-style "unlock" milestones are explicitly out of scope.
- Memory provider plug-in (from Hermes ADR-Proposed-Brunnr-001) integrates with the affect storage as the canonical write path.

**Alternatives Considered.**

- *Keep SAP's JSON file model, add an audit log* — rejected. The audit log does not fix the opacity problem.
- *Drop affect entirely, treat Ember as stateless* — rejected. Drops a high-value relational surface that the operator wants.
- *Affect as embedding drift in the Well* — interesting but speculative; deferred to a future ADR if the typed-axis model proves inadequate.

**Vow check:** Embodied Honesty ✅, Affective Restraint ✅, Tethered Grounding ✅, Honest Memory ✅, Public-Friendliness ✅.

**Risk:** Medium. The migration from "no affect engine" (Ember today) to "tethered affect engine" is large enough to be its own slice. The Auditor pass for the migration must be deliberate.

**Instantiates inventions:** `[[66_INVENTED_METHODS]]#5`, `#8`, `#10`, `#14`, `#17`.

**SAP references:**

- `/tmp/super-agent-party/py/affection_system.py:37-65` (the regex parser)
- `/tmp/super-agent-party/py/affection_api.py:1-29` (the unsafe FastAPI surface)
- `/tmp/super-agent-party/py/autoBehavior.py:43-97` (the gacha-aligned autonomous behavior tool)

---

## ADR-Proposed-SAP-003 — Adopt the Tier Ladder (T0/T1/T2/T3/T4)

**Status:** Proposed (Scribe, 2026-05-24)

**Context.** SAP's hardware floor is 2 cores / 2 GB RAM. SAP does not formally tier its expressive surface; the VRM avatar either runs or does not. There is no per-tier vocabulary.

Ember's proposed Vow of **Tiered Presence** requires graceful degradation across host capability. Cartographer's `[[63_PERFORMANCE_TIER_ENGINE]]` defines the engine; Scribe's `[[6B_LOW_POWER_EMBODIMENT]]` defines the expressive vocabulary. This ADR ratifies the **tier ladder** as a named, stable taxonomy that other ADRs and modules can reference.

**Decision.** Adopt the five-tier ladder (T0/T1/T2/T3/T4) with the capability descriptors documented in `[[6B_LOW_POWER_EMBODIMENT]]#1`. Specifically:

| Tier | Definition |
|---|---|
| T0 | Workstation (≥8 cores, ≥16 GB RAM, GPU ≥ RTX 2060) — full VRM + MOSS TTS + ASR + camera |
| T1 | Laptop (≥4 cores, ≥8 GB RAM, integrated GPU) — Live2D + piper-tts + ASR + lid-aware suspend |
| T2 | Phone / tablet — text + voice + haptic, no avatar |
| T3 | Pi 5 / SBC — text + glyphic embodiment + cued voice clips |
| T4 | Smart toaster / headless — log-line affect + status pulse + webhook ping |

Tier is detected at startup via a small capability probe; operators can override in `~/.ember/config/tier_override.yaml`.

**Consequences.**

- Every Ember subsystem that ships per-tier behavior can reference this taxonomy stably.
- The capability probe lives in `src/ember/spark/funi/tier_detect.py` (~150 LOC).
- The first-launch wizard becomes tier-conditional.
- Documentation can refer to "T3 hosts" without ambiguity.

**Alternatives Considered.**

- *Continuous tier (e.g. a numeric "horsepower score")* — rejected. Discrete tiers are easier to communicate and to gate features against.
- *Two tiers only (workstation / lightweight)* — rejected. Insufficient resolution for Pi-and-below.
- *Per-feature gating without an overall tier concept* — rejected. The operator wants to reason about *the host*, not about *each feature*.

**Vow check:** Tiered Presence ✅, Smallness ✅ (T4 honors it), Public-Friendliness ✅ (the ladder is plain-readable).

**Instantiates inventions:** All of `[[6B_LOW_POWER_EMBODIMENT]]` plus `[[66_INVENTED_METHODS]]#2`, `#9`.

**SAP references:** SAP's silence on this is the foundation — `/tmp/super-agent-party/config/settings_template.json` does not contain a tier concept.

---

## ADR-Proposed-SAP-004 — Reject Default-On Outward Reach; Adopt Failsafe Default-Quiet

**Status:** Proposed (Scribe, 2026-05-24)

**Context.** SAP's first-launch behavior turns on many outward reach surfaces by default. `settings_template.json` ships with IM bot config sections, livestream config sections, and autonomous behavior settings that default to *available but not running*. However, the path from "available" to "running" is friction-light — a single click in the SAP UI. The implicit posture is "outward reach should be enabled once configured."

Ember's proposed Vow of **Surface Without Surveillance** plus Vow of **Smallness** require the inverse: outward reach should default *off*, and enabling requires explicit operator ceremony.

**Decision.** Adopt failsafe default-quiet mode per `[[66_INVENTED_METHODS]]#16`:

1. Fresh-installed Ember has zero outward reach surfaces enabled.
2. The first-launch wizard (Hjarta's existing wizard, extended) walks the operator through each potential surface and asks explicit consent.
3. The wizard is tier-conditional per `[[6B_LOW_POWER_EMBODIMENT]]#7.3` — T4 wizard offers only MCP-server + webhook; T0 wizard offers everything with warnings.
4. `ember reach reset` is a CLI command that returns all surfaces to off.
5. `ember reach list` shows currently-enabled surfaces with their authority assignments.

**Consequences.**

- Wizard extensions: ~200 LOC.
- Per-surface ON/OFF state lives in `~/.ember/config/reach.yaml`.
- New operators have a noticeably quieter first-launch experience than SAP users do.
- Migration from existing Ember installs (which have no reach surfaces yet) is trivial.

**Alternatives Considered.**

- *Default-off with a "quick-enable-all" command* — rejected. The convenience command undermines the discipline.
- *Default-off with per-surface "first call awaits consent" prompts (lazy enable)* — interesting but operationally noisy. Wizard upfront is cleaner.
- *Default-on for "harmless" surfaces (autonomous greeting, etc.)* — rejected. There are no harmless surfaces under Surface Without Surveillance.

**Vow check:** Surface Without Surveillance ✅, Smallness ✅, Public-Friendliness ✅.

**Instantiates inventions:** `[[66_INVENTED_METHODS]]#16`, `#13`.

**SAP references:**

- `/tmp/super-agent-party/config/settings_template.json` (the all-options-available default surface)
- `/tmp/super-agent-party/py/autoBehavior.py:1-97` (the autonomous trigger that defaults to "enabled when configured")

---

## ADR-Proposed-SAP-005 — Per-Host Federated Identity with Persona-Id Issuance

**Status:** Proposed (Scribe, 2026-05-24)

**Context.** SAP does not have a federation identity. Each SAP install on each host is independent. The multi-host case is unmanaged. SAP's user-identity concept is a *user name string* (`<user=派酱>`), keyed on conversational mention, not a stable identifier.

For `[[6A_MULTI_AGENT_PARTY]]`, Ember needs a stable per-host identity that can survive hostname changes, MAC changes, and tailnet migrations. The identity must be operator-issued (not auto-generated by the host claiming whatever name it wants) and Well-anchored (so the swarm can see and reason about peers).

**Decision.** Adopt persona-identity issuance per `[[6A_MULTI_AGENT_PARTY]]#3`:

1. Each Ember instance has exactly one `persona_id` (UUID v4, generated at `ember party init`).
2. The persona_id is signed by an operator-controlled key (the operator's existing `~/.ssh/` key or a freshly-generated Ember key).
3. The persona_id is recorded in `~/.ember/identity/persona.yaml` on the host and as a row in the `ember_instance` table in Brunnr.
4. Each instance also stores host-fingerprint metadata (hostname, MAC of primary interface, OS, tier) alongside the persona_id.
5. The persona_id is *never reissued*. Retirement is marked via `retired_at` timestamp; new hosts get new persona_ids.

**Consequences.**

- Slice-3-ready (the persona table and `ember party init` are small and additive).
- Even single-instance Ember installs benefit — the persona_id makes audit logs more meaningful (every log entry can carry the persona_id).
- The Well gains an `ember_instance` table.
- The signing-key flow needs a small operator UX (default: prompt operator at `ember party init` to choose existing SSH key or generate fresh).

**Alternatives Considered.**

- *Hostname as identity* — rejected. Hostnames change.
- *MAC address as identity* — rejected. MACs change too (and hardware changes).
- *Operator-string identity (e.g. "Volmarr's Laptop")* — rejected. Not stable across machines that may move; not unique across persons running Ember on the same host.
- *UUID without signing* — rejected. Vulnerable to copy-from-other-host identity-theft. Signing prevents that.

**Vow check:** Federated Self ✅, Honest Memory ✅ (audit log meaningfulness improves), Surface Without Surveillance ✅ (the persona is operator-issued, not auto-collected).

**Instantiates inventions:** `[[6A_MULTI_AGENT_PARTY]]#3`, `#11`.

**SAP references:** SAP's silence — there is no equivalent module to cite. The absence is the data point.

---

## ADR-Proposed-SAP-006 — Adopt Sleep-Guard for T0/T1; Reject Default-On

**Status:** Proposed (Scribe, 2026-05-24)

**Context.** SAP ships `/tmp/super-agent-party/py/sleep_guard.py:1-100` — a small, well-built cross-platform module that prevents the host from sleeping while SAP is active. It supports Windows (`SetThreadExecutionState`), macOS (`caffeinate -dims`), and Linux. The module is excellent. SAP's default behavior calls `SleepGuard.start()` whenever the app is in the foreground.

For Ember, the sleep-guard pattern is genuinely useful — at T0 or T1 during a long-running task or livestream, the operator does not want the machine to suspend mid-flow. But Ember's Vow of **Affective Restraint** plus **Surface Without Surveillance** argues against default-on. The operator should *choose* sleep-guarding, not have it imposed.

**Decision.** Adopt the SAP sleep-guard pattern with these constraints:

1. Sleep-guard is **opt-in** per session (`ember chat --keep-awake`) and per long-running task (`ember mcp serve --keep-awake`).
2. Sleep-guard is **disabled** at T2/T3/T4 — phones, Pis, and toasters should suspend on their own schedules.
3. The sleep-guard module ports the SAP cross-platform pattern (Windows ExecutionState API, macOS caffeinate, Linux DBus inhibit) verbatim.
4. The operator can see sleep-guard status via `ember introspect power`.

**Consequences.**

- ~150 LOC port (the SAP module is already small; mostly a translation of comments to English and integration with Ember's CLI).
- Sleep-guard becomes a documented surface, not a hidden behavior.
- The audit log records sleep-guard activations.

**Alternatives Considered.**

- *Always-on sleep-guard on T0/T1 (matching SAP default)* — rejected. Surprises operators whose laptop drained overnight.
- *Sleep-guard via a separate package* — rejected. Small enough to live in Ember directly.

**Vow check:** Surface Without Surveillance ✅, Public-Friendliness ✅, Affective Restraint ✅.

**Instantiates inventions:** Tier-aware power management (a small extension of `[[6B_LOW_POWER_EMBODIMENT]]#3`).

**SAP references:**

- `/tmp/super-agent-party/py/sleep_guard.py:30-100` (Windows guard)
- `/tmp/super-agent-party/py/sleep_guard.py:71-100` (macOS guard)

---

## ADR-Proposed-SAP-007 — Adopt Behavior-Engine Trigger Vocabulary; Reject Default-On Triggers

**Status:** Proposed (Scribe, 2026-05-24)

**Context.** SAP's `/tmp/super-agent-party/py/behavior_engine.py:53-225` provides a clean autonomous-trigger taxonomy: `time` (specific HH:MM trigger), `noInput` (latency-since-last-message), `cycle` (periodic). The Pydantic models (`BehaviorTrigger`, `BehaviorAction`) are well-shaped. The engine itself is a singleton with hot-reloadable config.

Ember will eventually want autonomous behavior (per `[[64_AFFECTION_ENGINE_REIMAGINED]]` and `[[66_INVENTED_METHODS]]#10`). The trigger taxonomy and the dispatch loop pattern are worth porting. The default-on enabled flag on `BehaviorSettings.enabled` is not.

**Decision.** Adopt the SAP trigger vocabulary and engine pattern with the following changes:

1. Port the three trigger types (`time`, `noInput`, `cycle`) and the Pydantic models verbatim.
2. Port the singleton + hot-reload pattern (`update_config()`, `_tick()` loop).
3. Default `behaviorSettings.enabled = False`. Operator opts in via wizard or config.
4. Gate every trigger fire with **affect-aware cooldown** per `[[66_INVENTED_METHODS]]#10` — receptivity axis check before firing.
5. Add a fourth trigger type: `affect_threshold` — fires when an affect axis crosses a configured boundary.
6. Every trigger fire is audit-logged with the trigger ID, the conditions that matched, and the resulting action.
7. T4 hosts cannot use `time` or `cycle` triggers that produce *outgoing* communication; T4 triggers can only mutate state or write to logs.

**Consequences.**

- ~400 LOC port + 200 LOC extension (affect-aware gate + affect_threshold trigger + audit hooks).
- Operators have an autonomous-behavior surface without the gacha-pattern coupling.
- The hot-reload pattern means the operator can tune triggers without restarting.

**Alternatives Considered.**

- *Adopt SAP behavior engine verbatim including default-on* — rejected. Default-on autonomous behavior surprises operators.
- *Build from scratch* — rejected. SAP's shape is good; reinventing wastes effort.
- *Cron-based instead of an in-process engine* — interesting but a layer mismatch; the engine needs in-process state visibility.

**Vow check:** Affective Restraint ✅, Honest Memory ✅ (audit-logged), Modular Authorship ✅ (engine failure doesn't crash Funi), Tiered Presence ✅ (T4 gating).

**Instantiates inventions:** `[[66_INVENTED_METHODS]]#10` (affect-aware cooldown).

**SAP references:**

- `/tmp/super-agent-party/py/behavior_engine.py:53-225`
- `/tmp/super-agent-party/py/autoBehavior.py:1-97`
- `/tmp/super-agent-party/py/scheduler.py:1-134`

---

## ADR-Proposed-SAP-008 — Reject OpenAI-Compat Simulation Layer; Prefer Direct Provider Adapters

**Status:** Proposed (Scribe, 2026-05-24)

**Context.** SAP ships `ClaudeAsOpenAI.py`, `GeminiAsOpenAI.py`, `dify_openai.py` — translation layers that present non-OpenAI providers under an OpenAI-shaped API. The translation layers are *notoriously leaky*: token counting drifts, tool-call format mismatches, system-prompt handling differs in subtle ways. The Auditor's `[[55_API_SIMULATION_TRAPS]]` will catalog these in depth.

Hermes ADR-Proposed-Funi-001 commits Ember to a profile + transport split, which is the right shape for *real* provider integration. SAP's simulation pattern is the *wrong* shape — it pretends providers are interchangeable when they are not.

**Decision.** Reject the OpenAI-compat simulation pattern. Specifically:

1. Each provider Ember supports gets its **own native transport** (Hermes-style profile + transport split per Hermes ADR-Proposed-Funi-001).
2. Ember does **not** ship a generic "OpenAI-shaped" wrapper around non-OpenAI providers.
3. If an operator's *external* tools require an OpenAI-shaped endpoint to talk to Ember, Ember can expose a *small, deliberate* OpenAI-shape MCP surface that documents its limitations explicitly. This is the inverse — Ember-as-OpenAI-shape for external consumers, not provider-as-OpenAI-shape for Ember.
4. The documented limitations include: token counting may not match upstream; tool calls translated lossily; system prompt handling normalized.

**Consequences.**

- More native transports to write (one per provider), but each is cleaner.
- Token counts and tool-call shapes are honest.
- The Ember-as-OpenAI surface (the inverted case) is a clearly-scoped, documented compatibility shim — small, deliberate, with explicit caveats.

**Alternatives Considered.**

- *Adopt SAP's simulation layer wholesale* — rejected. Leakiness is real.
- *Ship the simulation layer as opt-in extra* — rejected. Even opt-in, the leakage problems persist.
- *No OpenAI-compat surface at all* — rejected for the export case. Some operators have tools that only speak OpenAI; we should not abandon them.

**Vow check:** Honest Memory ✅ (no token-count lies), Defended System Prompt ✅ (no opaque translation), Public-Friendliness ✅ (the caveats are visible).

**SAP references:**

- `/tmp/super-agent-party/py/ClaudeAsOpenAI.py`
- `/tmp/super-agent-party/py/GeminiAsOpenAI.py`
- `/tmp/super-agent-party/py/dify_openai.py`

---

## ADR-Proposed-SAP-009 — Adopt Overlay-Manager WebSocket Pattern for Tier-Spanning Display

**Status:** Proposed (Scribe, 2026-05-24)

**Context.** SAP's `/tmp/super-agent-party/py/overlay_router.py:1-81` implements a tight, well-shaped `DanmakuOverlayManager` — a websocket connection pool with broadcast semantics. The pattern is exactly the right shape for distributing affect glyphs, presence pulses, and backpressure indicators across tier-spanning display surfaces (laptop browser tab, Pi small-display, T4 status pulse webhook).

Ember today has no equivalent.

**Decision.** Adopt the SAP overlay-manager pattern as `Munnr.tier_broadcast`:

1. Port the `DanmakuOverlayManager` shape: connection list, `broadcast(message)` method, graceful disconnect on send failure.
2. Bind it to Ember's tailnet (not just localhost) so Pi, laptop, and workstation can all subscribe.
3. Use it to publish:
   - Affect glyph updates (per `[[66_INVENTED_METHODS]]#2`, `#5`)
   - Backpressure overlays (per `[[66_INVENTED_METHODS]]#11`)
   - Stream-truncation confessions (per `[[66_INVENTED_METHODS]]#7`)
   - Presence pulse heartbeats (per `[[6B_LOW_POWER_EMBODIMENT]]#7.5`)
4. Authenticate subscribers via a small token (operator-issued, shared on the tailnet only).
5. Drop messages to slow subscribers; never block the broadcaster.

**Consequences.**

- ~150 LOC port + 80 LOC tailnet binding + ~100 LOC token auth.
- A laptop browser can open a small overlay tab and see Ember's affect glyph in real time across the swarm.
- A Pi attached display can subscribe to the same broadcast and show the same glyph.

**Alternatives Considered.**

- *MQTT for tier-spanning broadcast* — rejected. MQTT adds a broker; the SAP websocket pattern is simpler.
- *Server-Sent Events instead of websockets* — interesting; defer. Websockets are bidirectional which we may want later.
- *No tier-spanning broadcast (each tier has its own local display only)* — rejected. The multi-Ember party (`[[6A_MULTI_AGENT_PARTY]]`) wants visibility across hosts.

**Vow check:** Modular Authorship ✅ (broadcaster failure doesn't crash subscribers), Honest Memory ✅ (the broadcast is logged), Public-Friendliness ✅ (the small browser tab is plain HTML).

**Instantiates inventions:** Surface backbone for `[[66_INVENTED_METHODS]]#2`, `#7`, `#11`; foundation for `[[6B_LOW_POWER_EMBODIMENT]]#7`.

**SAP references:**

- `/tmp/super-agent-party/py/overlay_router.py:1-81`

---

## ADR-Proposed-SAP-010 — Reject Universal IM-Bot Default; Adopt Persona-Keyed Fallback

**Status:** Proposed (Scribe, 2026-05-24)

**Context.** SAP ships 8 IM bot managers, each as a standalone class. The default-on posture (per ADR-Proposed-SAP-004) plus the assumption that each IM platform's audience is *distinct* lead to a default architecture where each platform is wired independently. There is no fallback routing; when Telegram is down, the Telegram audience is unreachable until Telegram comes back.

For Ember, the operator-level reach model is *relational* — the same operator may talk on multiple platforms. Cross-platform graceful redirect (per `[[66_INVENTED_METHODS]]#3`) is the right shape.

**Decision.** Adopt:

1. Per `[[66_INVENTED_METHODS]]#3`, implement **persona-keyed fallback routing**:
   - Operator declares persona-to-platform mapping in `~/.ember/config/personas.yaml`.
   - When a platform becomes unavailable, Ember can emit signed graceful-redirect messages on adjacent platforms.
   - Cross-platform messages require persona-table validation before being treated as same-conversation.
2. Default *zero* IM bots enabled (per ADR-Proposed-SAP-004).
3. Each IM bot lives as a separate optional extra: `ember-agent[im-telegram]`, `ember-agent[im-discord]`, `ember-agent[im-slack]`, etc.
4. Each IM bot's tokens live in operator-managed secrets (not in config files — per ADR 0011's secret-resolver pattern).
5. Each IM bot can be tier-restricted: T4 hosts cannot run any IM bot; T3 hosts can run *receiver* bots only (no autonomous outgoing); T0/T1 can run full bidirectional bots.

**Consequences.**

- IM bot integration becomes a much smaller per-platform port (each adapter is ~200-400 LOC).
- Operators install only the platforms they use.
- Cross-platform graceful redirect makes Ember's reach feel more like *one Ember reachable many places* and less like *one app duplicated 8 times*.
- Persona-table maintenance is the operator's responsibility, surfaced via `ember persona list/add/remove`.

**Alternatives Considered.**

- *Port all 8 IM bots into the main package* — rejected. Bloats default install; couples failures across platforms.
- *No IM bots at all (Ember stays text-CLI only)* — rejected. The reach axis is too valuable to abandon.
- *Adopt SAP's per-platform-independent shape verbatim* — rejected. Misses the relational opportunity.

**Vow check:** Smallness ✅ (optional extras), Modular Authorship ✅ (per-platform failure contained), Graceful Offline ✅ (cross-platform fallback), Surface Without Surveillance ✅ (persona-table operator-managed).

**Instantiates inventions:** `[[66_INVENTED_METHODS]]#3`.

**SAP references:**

- `/tmp/super-agent-party/py/telegram_bot_manager.py:1-137`
- `/tmp/super-agent-party/py/discord_bot_manager.py:1-440`
- `/tmp/super-agent-party/py/slack_bot_manager.py`
- `/tmp/super-agent-party/py/qq_bot_manager.py`
- `/tmp/super-agent-party/py/wechat_bot_manager.py`
- `/tmp/super-agent-party/py/feishu_bot_manager.py`
- `/tmp/super-agent-party/py/dingtalk_bot_manager.py`
- `/tmp/super-agent-party/py/wecom_bot_manager.py`

---

## ADR-Proposed-SAP-011 — Adopt VRM/Live2D Pipeline at T0; Gate Expressions by Consent Tokens

**Status:** Proposed (Scribe, 2026-05-24)

**Context.** SAP's `vts_manager.py:1-235` provides a clean integration with VTube Studio for VRM avatar control. The pattern (websocket client, expression dispatch, model-pose synchronization) is solid. SAP also leans on Live2D for fallback rendering. The expressive vocabulary is *maximalist* — any expression the model decides to emit is emitted.

Ember at T0 wants VRM avatar embodiment, but with two changes:

1. **Composition-first vocabulary** per `[[66_INVENTED_METHODS]]#17` — the default expressive set is composed-dignified, not gacha-maximalist.
2. **Consent-token gating** per `[[66_INVENTED_METHODS]]#6` — the operator declares which expressions are permitted in which contexts.

**Decision.** Adopt SAP's VTube Studio integration pattern with these specific commitments:

1. Port the VTS websocket protocol surface from `vts_manager.py:1-235`.
2. Ship a **composition-first default expression library** at `vrm/ember_expression_library.yaml`. Operators can replace it.
3. Implement **consent-token expression gating** — the avatar emits only expressions whose tokens are granted in the current context (`~/.ember/config/expression_tokens.yaml`).
4. T1 fallback to Live2D when VRM is too heavy (per `[[6B_LOW_POWER_EMBODIMENT]]#3`).
5. T2/T3/T4 have no avatar; the affect glyph and other tier surfaces substitute.
6. The avatar surface is **opt-in** at first launch (per ADR-Proposed-SAP-004).

**Consequences.**

- ~400 LOC for the VTS integration + ~150 LOC for the consent-token gate + ~100 LOC for the default expression library loading.
- The avatar feels deliberately composed rather than emotionally reactive.
- Operators control the expressive palette per context.

**Alternatives Considered.**

- *Adopt SAP's expression vocabulary verbatim* — rejected. The gacha aesthetic is off-brand for the Cyber-Viking project.
- *No avatar at all* — rejected. T0 audience genuinely wants embodied presence.
- *Avatar without consent gating* — rejected. Vow of Surface Without Surveillance applies to outward expression.

**Vow check:** Embodied Honesty ✅, Surface Without Surveillance ✅, Affective Restraint ✅, Public-Friendliness ✅ (the YAML is readable).

**Instantiates inventions:** `[[66_INVENTED_METHODS]]#6`, `#11`, `#17`.

**SAP references:**

- `/tmp/super-agent-party/py/vts_manager.py:1-235` (the VTS websocket integration)
- `/tmp/super-agent-party/py/moss_tts.py:1-267` (voice paired with avatar)
- `/tmp/super-agent-party/vrm/` (the VRM model directory)

---

## ADR-Proposed-SAP-012 — Adopt Sub-Agent Supervisory Discipline; Bind to Smiðja

**Status:** Proposed (Scribe, 2026-05-24)

**Context.** SAP's `/tmp/super-agent-party/py/sub_agent.py:1-367` implements a sub-agent lifecycle with disciplines (graceful start, drain on close, supervisor visibility, context isolation). The pattern is sound. SAP uses it for intra-process plurality — the parent SAP spawns child agents.

For Ember, the same supervisory pattern applies in two directions:

1. **Tool worker supervision** in Smiðja (per ADR 0011 — tool execution sandbox).
2. **Peer MCP server supervision** in the multi-Ember party (per `[[6A_MULTI_AGENT_PARTY]]`).

Both are *subprocess + supervisor + audit + drain-on-close* shapes.

**Decision.** Port SAP's sub-agent supervisory disciplines into a single shared module, `src/ember/spark/smidja/supervised.py`:

1. `SupervisedProcess(command, env, drain_timeout)` — wraps a subprocess with graceful-start, health-check, drain-on-close, force-kill-on-timeout.
2. `SupervisorRegistry` — global registry of supervised processes; visible via `ember introspect supervised`.
3. Audit-log hooks — every spawn, every drain, every force-kill leaves a record.
4. Use this module for:
   - MCP client child processes (per Hermes ADR-Proposed-MCP-003).
   - Tool sandbox workers (per ADR 0011 extensions).
   - Peer MCP server processes when an Ember instance hosts multiple personas (rare).
5. Drain-timeout default: 3 seconds. Force-kill fallback: `os.kill(pid, SIGKILL)` if drain exceeds timeout.

**Consequences.**

- One supervised-subprocess module, reused across subsystems.
- Better operator visibility (`ember introspect supervised`).
- Crash containment is uniform.

**Alternatives Considered.**

- *Per-subsystem supervised-subprocess implementations* — rejected. Duplication invites drift.
- *Use systemd directly* — rejected. Couples to systemd; breaks on macOS and Windows.
- *Use Python `multiprocessing`* — rejected. The use-case is *external* subprocess management, not Python-only spawns.

**Vow check:** Modular Authorship ✅ (subprocess failure contained), Honest Memory ✅ (audit hooks), Smallness ✅ (one module, reused).

**Instantiates inventions:** Foundation for `[[66_INVENTED_METHODS]]#12` (trust-chain audit) and `[[6A_MULTI_AGENT_PARTY]]` peer process supervision.

**SAP references:**

- `/tmp/super-agent-party/py/sub_agent.py:1-367` (lifecycle disciplines)
- `/tmp/super-agent-party/py/task_center.py:1-233` (supervisor visibility shape)

---

## Summary Table — All Proposed ADRs

| ID | Topic | Slice (estimated) | Affects Vows | Risk | Inventions Instantiated |
|---|---|---|---|---|---|
| SAP-001 | Adopt MCP as primary tool & federation protocol | 3-4 | none (reinforces several) | Low | `[[66]]#12` |
| SAP-002 | Reject gacha affect; adopt tethered affect | 4-5 | Embodied Honesty, Tethered Grounding | Medium | `[[66]]#5`, `#8`, `#10`, `#14`, `#17` |
| SAP-003 | Adopt Tier Ladder (T0/T1/T2/T3/T4) | 3 | Tiered Presence, Smallness | Low | `[[6B]]` whole; `[[66]]#2`, `#9` |
| SAP-004 | Reject default-on reach; adopt failsafe quiet | 3 | Surface Without Surveillance | Low | `[[66]]#13`, `#16` |
| SAP-005 | Per-host federated identity (persona_id) | 3 | Federated Self | Low | `[[6A]]#3`, `#11` |
| SAP-006 | Adopt sleep-guard; reject default-on | 4 | Surface Without Surveillance | Low | `[[6B]]#3` extension |
| SAP-007 | Adopt behavior-engine triggers; reject default-on | 5 | Affective Restraint, Honest Memory | Medium | `[[66]]#10` |
| SAP-008 | Reject OpenAI-compat simulation; native transports | 3-4 | Honest Memory, Defended System Prompt | Low | (none — anti-pattern rejection) |
| SAP-009 | Adopt overlay-manager websocket pattern | 4 | Modular Authorship | Low | `[[66]]#2`, `#7`, `#11`; `[[6B]]#7` |
| SAP-010 | Per-persona IM fallback; reject default-on IM | 5 | Smallness, Modular Authorship, Graceful Offline | Medium | `[[66]]#3` |
| SAP-011 | Adopt VRM/Live2D at T0; gate by consent tokens | 5-6 | Embodied Honesty, Surface Without Surveillance | Medium | `[[66]]#6`, `#11`, `#17` |
| SAP-012 | Sub-agent supervisory discipline → Smiðja | 4 | Modular Authorship, Honest Memory | Low | `[[66]]#12`; `[[6A]]` support |

---

## What This Means for Ember

**True Names affected:** All six. Funi (SAP-001, SAP-005, SAP-008, SAP-012), Strengr (SAP-008), Brunnr (SAP-002, SAP-005 persona table), Smiðja (SAP-012 supervisory discipline), Hjarta (SAP-002, SAP-007 affect engine and triggers), Munnr (SAP-003, SAP-004, SAP-009, SAP-010, SAP-011 tier vocabulary, reach defaults, overlay surface, IM fallback, avatar pipeline).

**Vows touched:**

- *Most reinforced:* **Surface Without Surveillance** (SAP-004, SAP-006, SAP-010, SAP-011) — the central Vow for outward reach surfaces.
- *Most strengthened:* **Embodied Honesty** (SAP-002, SAP-011) — the central Vow for affect and avatar.
- *Most clarified:* **Tiered Presence** (SAP-003, SAP-006, SAP-010, SAP-011) — the tier ladder gives the Vow operational shape.
- *Most watched:* **Honest Memory** (SAP-002, SAP-007, SAP-008, SAP-009, SAP-012) — five ADRs touch it; the migration from SAP's untyped state to Ember's typed-and-anchored state is the highest-effort thread.

**Concrete next step for the keeper:**

1. Review each ADR-Proposed above. The 12 cluster naturally into four groups:
   - **Slice 3 candidates:** SAP-001 (already commits via Hermes ADRs), SAP-003 (tier ladder), SAP-004 (default-quiet), SAP-005 (persona-id), SAP-008 (reject OpenAI sim).
   - **Slice 4 candidates:** SAP-006 (sleep-guard), SAP-009 (overlay-manager), SAP-012 (sub-agent supervision).
   - **Slice 5+ candidates:** SAP-002 (affect engine — high effort), SAP-007 (behavior engine), SAP-010 (IM fallback).
   - **Slice 6+ candidates:** SAP-011 (VRM avatar — biggest single integration).
2. For each, decide: Accept, Defer, or Reject.
3. For Accept: copy to `docs/decisions/NNNN-<slug>.md` with appropriate ADR number; status becomes Ratified; reference this Codex doc.
4. For Defer: note in `[[67_SLICE_PLAN_REVISIONS]]` revision; revisit at next slice ratification.
5. For Reject: record the rejection rationale here.

**The proposals stand as written. The decisions record does not change the project. Each ADR becomes a project decision only on ratification.**

**Cross-references:**

- `[[60_TRUE_NAME_REASSIGNMENT]]` — Cartographer's True Name proposals that several ADRs assume.
- `[[61_NEW_VOWS]]` — Cartographer's new Vows that several ADRs reinforce.
- `[[64_AFFECTION_ENGINE_REIMAGINED]]` — the affect engine SAP-002 implements.
- `[[66_INVENTED_METHODS]]` — the catalogue of inventions these ADRs instantiate.
- `[[67_SLICE_PLAN_REVISIONS]]` — the slice-shaped bundling that uses these ADRs.
- `[[6A_MULTI_AGENT_PARTY]]` — SAP-005 and SAP-012 underpin party identity and supervision.
- `[[6B_LOW_POWER_EMBODIMENT]]` — SAP-003 ratifies the tier ladder this doc relies on.
- `[[6C_EMBER_WAVE_3_SLICE]]` — the concrete Wave 3 slice proposal.
- `[[69_INTEGRATION_ROADMAP]]` — phasing across the codex constellation.
- `[[hermes:60_HERMES_VS_EMBER_CROSSWALK]]` — the Hermes-side foundation for SAP-001, SAP-008.
- `[[hermes:Skill-001]]`, `[[hermes:Skill-002]]`, `[[hermes:MCP-001]]`, `[[hermes:MCP-003]]`, `[[hermes:Funi-001]]`, `[[hermes:Strengr-001]]` — Hermes ADRs the SAP-derived ADRs reference.

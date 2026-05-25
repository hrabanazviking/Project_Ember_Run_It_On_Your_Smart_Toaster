---
codex_id: 69_SLICE_PLAN_REVISIONS
title: Slice Plan Revisions — CDK-Derived Proposals (PROPOSE ONLY)
role: Scribe
layer: Synthesis
status: draft
chatdoll_source_refs:
  - "(synthesizes CDK-derived ADRs from [[67_DECISION_RECORDS]] and inventions from [[68_INVENTED_METHODS]] against Ember's existing and proposed slice plans)"
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr, Andlit-unity-proposed, Rödd-proposed]
cross_refs:
  - 60_synthesis/60_TRIANGULATION
  - 60_synthesis/61_ANDLIT_UNITY_TIER
  - 60_synthesis/62_MOBILE_AND_XR_TIER
  - 60_synthesis/63_MULTIMODAL_PIPELINE
  - 60_synthesis/64_FUNCTION_CALLING_FOR_EMBODIED
  - 60_synthesis/65_MEMORY_INTEGRATION
  - 60_synthesis/66_JAPANESE_VOICE_INTEGRATION
  - 60_synthesis/67_DECISION_RECORDS
  - 60_synthesis/68_INVENTED_METHODS
  - 60_synthesis/6A_INTEGRATION_ROADMAP
  - 60_synthesis/6B_EMBER_WAVE_5_SLICE
  - sap_codex/60_synthesis/67_SLICE_PLAN_REVISIONS
  - sap_codex/60_synthesis/69_INTEGRATION_ROADMAP
  - waifu_codex/60_synthesis/61_DECISIONS_AND_INVENTIONS
---

# 69 — Slice Plan Revisions (CDK-Derived)

> *A third corpus has been mined. The slice plan listens differently now — it has three teachers instead of two, and the harmony of the three says where the next foot should land.*
> — Eirwyn Rúnblóm, holding the gate against revision until the keeper opens it

## 0. Posture — PROPOSE ONLY

This document proposes revisions to Ember's ratification-gated slice plan based on the CDK Codex findings (Wave 5). **It does not modify the slice plan itself.** The current ratified slice plan stops at slice 2 (`docs/architecture/EMBER_SECOND_SLICE_PLAN.md`, ratified 2026-05-21 via ADR 0013).

Three prior codex revisions are already in flight as **proposals**:

- `[[hermes:65_SLICE_PLAN_REVISIONS]]` — *Skilled, Bridged, Quiet* (Hermes Wave 1).
- `[[sap:67_SLICE_PLAN_REVISIONS]]` — *Skilled, Bridged, Quiet, Tiered, Identified* (SAP Wave 3) + slices 4-8 sketched.
- `[[waifu:60_REALTIME_TIER_FOR_ANDLIT]]` + `[[waifu:61_DECISIONS_AND_INVENTIONS]]` — Tier-CLOUD parallel branch (Waifu Wave 4).

This doc **does not duplicate** those proposals; it **adds** CDK-shaped revisions and surfaces the *braided shape* the keeper now faces. The companion docs are `[[67_DECISION_RECORDS]]` (the twelve CDK-derived ADR-Proposed envelopes), `[[68_INVENTED_METHODS]]` (the twenty CDK-adjacent inventions), `[[6A_INTEGRATION_ROADMAP]]` (the six-codex phasing), and `[[6B_EMBER_WAVE_5_SLICE]]` (the concrete Wave-5 slice draft this doc's revisions feed into).

This doc follows the SAP-side template — *current state, what CDK findings change, proposed revisions, risk and cost* — and adds one new section: **what proposals *retire* in light of triangulation**. CDK is the *third* corpus on the embodiment axis; some prior single-source proposals deserve revisiting now that triangulated evidence exists.

Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).

---

## 1. What's Ratified, What's Proposed, What's Open

The state of the slice plan as the Scribe finds it on 2026-05-25:

**Ratified (Law of the Project):**

- *Slice 1* — six True Names, `ember chat`, `ember well ingest`, `ember doctor`, sqlite_vec + Ollama on Pi 5. Standing rules per ADR 0007.
- *Slice 2* — config loader, streaming Funi replies, pgvector Brunnr, tool-use framework (read-only). Standing rules per ADR 0013.

**Proposed by Hermes (Wave 1):**

- *Slice 3 (Hermes shape)* — skill subsystem, MCP server, provider profile + transport split, tool parallelism + interrupt fan-out, typed retry + exhaustion TTL.

**Proposed by SAP (Wave 3, revising Hermes):**

- *Slice 3 (SAP-augmented shape)* — Hermes shape + tier ladder + persona-id + glyphic + failsafe-default-quiet standing rule.
- *Slice 4* — affect engine, sleep-guard, overlay-manager broadcast, sub-agent supervisor, backpressure overlay.
- *Slice 5* — Hermes's original slice-4 (MCP client, memory provider, agent-skill writes) + behavior engine + first IM bot.
- *Slice 6* — VRM/Live2D embodiment, consent gating, composition library, cued voice library.
- *Slice 7 (speculative)* — multi-Ember party.
- *Slice 8+ (speculative)* — additional IM platforms, livestream platforms.

**Proposed by Waifu (Wave 4):**

- *Tier-CLOUD parallel branch* — LiveKit substrate; Andlit-realtime + Rödd-realtime sub-names; slice 6+ landing.

**Open (this codex's contribution):**

- *Andlit-unity tier* and *Rödd-unity* — Unity-native local rendering tier per ADR-Proposed-CDK-010.
- *Bilingual Rödd* and *VOICEVOX baseline* per ADR-Proposed-CDK-002.
- *Multimodal-pipeline-as-resource* per ADR-Proposed-CDK-012.
- *Multi-provider LLM abstraction at Strengr* per ADR-Proposed-CDK-004 + 005.
- *Three-corpus triangulation as standing discipline* per ADR-Proposed-CDK-006.
- *ChatMemory two-store pattern for Hjarta* per ADR-Proposed-CDK-007.
- *Silero VAD default* per ADR-Proposed-CDK-008.
- *Tailnet-only network default* per ADR-Proposed-CDK-011.

What the keeper has *not* yet seen is the *interaction* — how the CDK proposals revise the slices the SAP codex sketched. That is what this document supplies.

---

## 2. What CDK Findings Change

The CDK corpus reveals **five force-fields** that argue for further slice-plan adjustments beyond what the SAP-side already proposed.

### 2.1 The Multi-Provider LLM Abstraction Is Slice 3 Territory, Not Slice 5

Hermes's S3-B already proposes the provider-profile + transport-split refactor (per `[[hermes:65_SLICE_PLAN_REVISIONS]]`). The SAP slice plan honored it. CDK's `ILLMService` evidence (per `[[67_DECISION_RECORDS]]` ADR-Proposed-CDK-004 + 005, citing `/tmp/ChatdollKit/Scripts/LLM/ILLMService.cs` and six concrete provider implementations) **reinforces** the slice-3 placement and **adds** two specifics:

1. The transport split should ship with *at least two* native providers, not just Ollama. CDK's evidence is that the abstraction *only earns its keep* once a second provider proves the shape. Recommended pair: Ollama (already present) + Anthropic-direct.
2. The function-call format adapter pattern (per ADR-Proposed-CDK-005) should land in slice 3 alongside the transport split — adapter-shape-from-day-one prevents the SAP "ClaudeAsOpenAI simulation" anti-pattern from creeping in by default.

**Implication:** revise slice 3 to include *two* native providers (Hermes-S3-B + CDK-S3-J) and the per-provider function-call adapter (CDK-S3-K). Slice 3 size grows by ~400 LOC.

### 2.2 The Multimodal-Pipeline-as-Resource Is Slice 4 Territory, Not Slice 6

SAP's slice 4 (*Felt, Visible, Awake*) builds the affect engine, sleep-guard, overlay-manager. CDK's evidence (per `[[63_MULTIMODAL_PIPELINE]]` and ADR-Proposed-CDK-012) is that *the pipeline-as-resource pattern is the right substrate for affect engine integration* — the affect engine reads from pipeline events and writes affect-mutations as pipeline-coupled audit records.

If the affect engine ships in slice 4 *without* the pipeline-as-resource substrate, the affect engine has to invent its own event surface, and the pipeline substrate has to retrofit affect integration later. That is two integrations where one would do.

**Implication:** add CDK-S4-F (multimodal-pipeline-as-resource substrate) to slice 4, *before* affect engine work begins. Pipeline substrate is ~400-500 LOC; it pays for itself by simplifying the affect-engine wire-up.

### 2.3 The Voice Baseline (Rödd) Is Slice 5 Territory, Not Slice 6

SAP's slice 6 contains the cued voice library workflow (per `[[sap:67_SLICE_PLAN_REVISIONS]]#4.3`). CDK's evidence (per `[[66_JAPANESE_VOICE_INTEGRATION]]` and ADR-Proposed-CDK-002) is that the *baseline voice engine* (VOICEVOX + Piper, bilingual) is a *smaller and earlier* commitment than the cued library — the bilingual baseline is ~300 LOC of provider adapters + router; the cued library is a workflow on top of it.

Splitting them across two slices is fine if slice 5 ships the baseline and slice 6 ships the workflow. SAP collapsed them into slice 6 because SAP had no voice baseline to build *on*. CDK supplies that baseline.

**Implication:** add CDK-S5-C (bilingual Rödd baseline — VOICEVOX + Piper + router) to slice 5. Slice 5 grows by ~400 LOC. Slice 6 gains a baseline to build the cued workflow against.

### 2.4 The Unity Protocol Is a Self-Contained Sub-Slice, Not a Whole Wave

ADR-Proposed-CDK-010 splits the Unity-tier embodiment into *protocol* (a Funi-side WebSocket surface that any Unity client can speak to) and *client* (the Unity app itself, possibly community-built). The protocol is the smaller, ratification-ready piece. The client is the larger, deferrable piece.

Proposing the Unity *client* in slice 5 or 6 is too heavy — the engineering cost of a Unity client is months of C# work that does not align with Ember's Python-first identity. Proposing the *protocol* in slice 5 or 6 is *tractable* — it is a WebSocket surface, a typed event vocabulary, a handshake, and an auth flow. Maybe 600 LOC of Python.

**Implication:** propose the *protocol-only* sub-slice as CDK-S5-D or CDK-S6-D. The Unity *client* is a separate project (`ember-unity-client`) with its own release cadence, possibly authored by a community contributor.

### 2.5 The Tailnet-Default Network Posture Is Slice 3 Territory, Not Slice 7

ADR-Proposed-CDK-011 (tailnet-only network default) reinforces the standing memory at `[[ember:feedback_tailnet_access]]`. The first slice that exposes any network-bound surface should adopt this posture. Slice 3 exposes the MCP server (Hermes-S3-C). The MCP server should bind to the tailnet interface from day one, not bind permissively and patch later.

**Implication:** revise slice 3's MCP server (Hermes-S3-C) to default-bind to the tailnet interface. This is a small revision (~50 LOC of bind-discovery logic). Add CDK-S3-L as a standing rule: *every network-bound surface defaults to tailnet-bind*.

---

## 3. Proposed Revisions to SAP-Revised Slice 3 — *Skilled, Bridged, Quiet, Tiered, Identified, Multi-Provider*

The SAP proposal for slice 3 (per `[[sap:67_SLICE_PLAN_REVISIONS]]#3.5`) is the current most-comprehensive shape. The CDK findings argue for three additions and one revised standing rule.

### 3.1 Add: second native provider + function-call adapter

**ADR-Proposed-CDK-S3-J:** Add a second native Funi provider in slice 3 to validate the transport-split shape.

- `src/ember/spark/funi/transports/anthropic.py` — Anthropic-direct transport, ~250 LOC.
- `src/ember/spark/funi/plugins/anthropic/` — provider profile, ~80 LOC.
- Tests against the same shape as `transports/ollama.py`.
- The two-provider acceptance test verifies parity: same prompt → both providers produce structurally-valid responses; the response shapes diverge only in `provider_specific` metadata.

**Cost:** ~330 LOC + ~200 LOC tests.

**Risk:** Low. The Anthropic Python SDK is mature; the transport is a thin wrapper.

### 3.2 Add: per-provider function-call adapter pattern

**ADR-Proposed-CDK-S3-K:** Adopt the per-provider function-call adapter pattern at slice-3 time per ADR-Proposed-CDK-005.

- `src/ember/spark/strengr/adapters/` — base adapter Protocol + per-provider implementations.
- `adapters/openai.py`, `adapters/anthropic.py` — initial pair.
- Rich `ToolCall` representation with `provider_specific: dict[str, Any]`.
- Tests: each provider's tool-call format round-trips through the rich representation without loss.

**Cost:** ~250 LOC + ~150 LOC tests.

**Risk:** Low. The pattern is small; the divergence-handling burden is paid at adapter time, not at call time.

### 3.3 Add: tailnet-only network bind posture

**ADR-Proposed-CDK-S3-L:** Adopt tailnet-only network bind as a standing rule per ADR-Proposed-CDK-011.

- `src/ember/spark/funi/network_bind.py` — tailscale interface detection, fallback to operator-configured interface, default-deny 0.0.0.0.
- Hermes-S3-C's MCP server uses this for its bind.
- `ember status` shows the current bind interface at startup.
- Tests: tailscale-present detection; fallback to localhost when no tailscale + explicit operator config; refusal to bind 0.0.0.0 by default.

**Cost:** ~150 LOC + ~80 LOC tests.

**Risk:** Low. The standing memory at `[[ember:feedback_tailnet_access]]` is already the operator's preference; this codifies it.

### 3.4 Revise: standing rules — add **tailnet-bind-default**

Per ADR-Proposed-CDK-S3-L, add a standing rule to slice 3:

> **Tailnet-Bind-Default:** every network-bound surface defaults to the tailnet interface (when tailscale is detected) or a specific operator-configured interface; never to 0.0.0.0 by default. Operator override requires explicit configuration. Test added: `tests/integration/test_no_open_bind.py` verifies no Ember service binds 0.0.0.0 on a fresh install.

Parallel to Hermes's *Cache Discipline* and SAP's *Failsafe-Default-Quiet* — a project law that subsequent slices honor.

### 3.5 Slice 3 — Revised Shape

**Theme:** *Skilled, Bridged, Quiet, Tiered, Identified, Multi-Provider, Tailnet-Bound.*

**ADRs (combined Hermes + SAP + CDK):**

| ADR | Topic | Source |
|---|---|---|
| Hermes-S3-A | Skill subsystem v1 (read-only) | Hermes |
| Hermes-S3-B | Provider profile + transport split | Hermes |
| Hermes-S3-C | MCP server (read-only subset) | Hermes |
| Hermes-S3-D | Tool batch parallelism + interrupt fan-out | Hermes |
| Hermes-S3-E | Strengr typed retry + per-error-code exhaustion TTL | Hermes |
| SAP-S3-F | Tier ladder (detect + override + wizard branching) | SAP |
| SAP-S3-G | Persona-id issuance | SAP |
| SAP-S3-H | Glyphic embodiment + log-affect formatting | SAP |
| SAP-S3-I | Standing rule: failsafe-default-quiet | SAP |
| **CDK-S3-J** | **Second native Funi provider (Anthropic-direct)** | **CDK** |
| **CDK-S3-K** | **Per-provider function-call adapter pattern** | **CDK** |
| **CDK-S3-L** | **Standing rule: tailnet-bind-default** | **CDK** |

**Cost (revised):**

- Hermes-portion: ~1,400 LOC + ~900 tests.
- SAP-portion: ~650 LOC + ~330 tests.
- CDK-portion: ~730 LOC + ~430 tests.
- **Total revised: ~2,780 LOC code + ~1,660 LOC tests.**
- Calendar: 10-12 weeks (vs 8-10 SAP-revised; vs 6-8 Hermes-original).

**Acceptance criterion additions (over SAP-revised):**

> 11. **New (CDK-J):** `ember chat --provider anthropic` succeeds; `ember chat --provider ollama` succeeds; both produce structurally-valid responses against the same prompt.
> 12. **New (CDK-K):** A tool call emitted by Anthropic preserves Anthropic's stop-reason in the audit log's `provider_specific` field; the same tool call emitted by OpenAI-shape preserves OpenAI's `finish_reason`. Round-trip is lossless within each provider.
> 13. **New (CDK-L):** `ember mcp serve` binds to the tailscale interface; `ss -tlnp` confirms no 0.0.0.0 binding. `ember status` shows the bind interface.

**Vow check (revised):** all eleven existing Vows respected (post-Waifu addition of proposed Vows). New watch-point: **Smallness** — the slice grew further (~2,780 LOC). Mitigation: sub-slice into 3a (Hermes-portion) / 3b (SAP-portion) / 3c (CDK-portion); each ships independently.

### 3.6 What Slice 3 Still Does NOT Include (Updated)

All SAP-side deferrals stand. CDK-side additions:

- *Andlit-unity protocol* — deferred to slice 5 or 6 (per `§5` of this doc).
- *Bilingual Rödd baseline* — deferred to slice 5.
- *Multimodal-pipeline-as-resource* — deferred to slice 4.
- *ChatMemory two-store* — deferred to slice 5.
- *Silero VAD* — deferred to slice 4 (paired with first voice surface).
- *VOICEVOX adapter* — deferred to slice 5.

---

## 4. Proposed Revisions to SAP-Proposed Slice 4 — *Felt, Visible, Awake, Piped*

The SAP proposal for slice 4 (per `[[sap:67_SLICE_PLAN_REVISIONS]]#4.1`) builds the affect engine, sleep-guard, overlay-manager, sub-agent supervisor, backpressure overlay. CDK's evidence (per ADR-Proposed-CDK-012, `[[63_MULTIMODAL_PIPELINE]]`, and invention `[[68]]` #3) argues for one significant addition: **the multimodal-pipeline-as-resource substrate should land first**.

### 4.1 Add: multimodal-pipeline-as-resource substrate

**ADR-Proposed-CDK-S4-F:** Adopt the pipeline-as-resource pattern as the *substrate* for slice 4's affect engine integration.

- `src/ember/schemas/pipeline.py` — `PipelineEvent`, `PipelineLifecycle`, `PipelineHandle`.
- `src/ember/spark/funi/pipeline.py` — `Pipeline` class with `open() / progress() / barge_in() / close()` lifecycle.
- `src/ember/spark/funi/pipeline_broker.py` — typed event broker that Hugarsýn subscribes to.
- The affect engine (SAP-S4-A) reads from pipeline events; affect mutations attach as pipeline-coupled audit records.
- Tests: pipeline lifecycle, event broker, integration with affect engine.

**Cost:** ~500 LOC + ~250 LOC tests.

**Risk:** Medium. The pipeline abstraction is non-trivial; failure to get it right early means retrofit later.

**Mitigation:** ship the pipeline substrate in slice 4a (Phase 28-29) *before* affect engine work begins. Affect engine integrates against an already-stable pipeline substrate.

### 4.2 Add: Silero VAD as default voice-detection module

**ADR-Proposed-CDK-S4-G:** Adopt Silero VAD per ADR-Proposed-CDK-008. Lands in slice 4 alongside pipeline substrate as the *first voice-input surface*.

- `src/ember/spark/munnr/listener/silero_vad.py` — ONNX-runtime Silero VAD integration.
- Vendored ~1MB ONNX model in `src/ember/assets/silero_vad.onnx`.
- `voice-input` optional extra adds `onnxruntime`.
- Tests: VAD on sample audio (speech / non-speech / silence).

**Cost:** ~200 LOC + ~120 LOC tests + ~1MB asset.

**Risk:** Low. ONNX runtime is mature; the Silero model is small and battle-tested.

### 4.3 Slice 4 — Revised Shape

**Theme:** *Felt, Visible, Awake, Piped, Listening.*

**ADRs:**

| ADR | Topic | Source |
|---|---|---|
| **CDK-S4-F** | **Multimodal-pipeline-as-resource substrate** | **CDK** |
| SAP-S4-A | Tethered affect engine | SAP |
| SAP-S4-B | Sleep-guard (opt-in, tier-aware) | SAP |
| SAP-S4-C | Overlay-manager websocket broadcast | SAP |
| SAP-S4-D | Sub-agent supervisory discipline → Smiðja | SAP |
| SAP-S4-E | Backpressure overlay glyphs | SAP-derived |
| **CDK-S4-G** | **Silero VAD as default voice-detection module** | **CDK** |

**Cost (revised):** ~2,100 LOC + ~1,070 LOC tests. Calendar: 10-12 weeks.

**Acceptance criterion additions (over SAP-revised):**

> 9. **New (CDK-F):** `ember introspect pipeline <session_id>` shows the lifecycle of the current/last turn — stages, timings, events, barge-in points.
> 10. **New (CDK-F):** Affect engine mutation events appear in the pipeline event stream alongside STT/LLM/TTS events; the audit unit is the pipeline turn.
> 11. **New (CDK-G):** Voice-input enabled; Silero VAD distinguishes speech from background noise; `ember introspect vad` shows probability output per frame.

**Vow check:** Modular Authorship reinforced (pipeline failure contained); Honest Memory reinforced (pipeline is the audit unit); Embodied Honesty extended (VAD probability is visible).

---

## 5. Proposed Revisions to SAP-Proposed Slice 5 — *Plural Minds, Plural Memories, Bilingual Voice*

SAP's slice 5 (per `[[sap:67_SLICE_PLAN_REVISIONS]]#4.2`) is the *Plural Minds, Plural Memories* slice. CDK's evidence argues for three additions: the **bilingual Rödd baseline** (`[[67]]` ADR-Proposed-CDK-002), the **ChatMemory two-store pattern** for Hjarta (`[[67]]` ADR-Proposed-CDK-007), and the **Andlit-unity protocol** (smaller scope, per `§2.4` of this doc).

### 5.1 Add: bilingual Rödd baseline

**ADR-Proposed-CDK-S5-C:** Adopt the bilingual Rödd baseline per ADR-Proposed-CDK-002 + invention `[[68]]` #1.

- `src/ember/spark/rodd/router.py` — language detection + provider routing.
- `src/ember/spark/rodd/providers/voicevox.py` — VOICEVOX two-call adapter (~120 LOC).
- `src/ember/spark/rodd/providers/piper.py` — Piper English adapter (~80 LOC).
- `src/ember/spark/rodd/catalogue.py` — voice catalogue manifest loader per `[[68]]` #6 (~150 LOC).
- `~/.ember/config/voice_catalogue.yaml` — operator-curated character + license manifest.
- `~/.ember/config/rodd_fallback.yaml` — per-language fallback chains per `[[68]]` #7.
- Tests: round-trip TTS for English (Piper) + Japanese (VOICEVOX); language detection accuracy; fallback chain on simulated provider failure.

**Cost:** ~600 LOC + ~350 LOC tests + the catalogue discipline + the engine-as-vendored-service pattern.

**Risk:** Medium. Operator-side dependency on VOICEVOX engine binary; documented but real. Piper is smaller and embedded.

**Mitigation:** the voice catalogue discipline + per-engine probe ensures graceful degradation if an engine is unreachable.

### 5.2 Add: ChatMemory two-store pattern for Hjarta

**ADR-Proposed-CDK-S5-D:** Adopt the ChatMemory two-store pattern per ADR-Proposed-CDK-007.

- `src/ember/spark/hjarta/episodic.py` — episodic conversation store (~200 LOC).
- `src/ember/spark/hjarta/factual.py` — LLM-extracted assertion store (~250 LOC).
- `src/ember/spark/hjarta/extractor.py` — extraction pipeline + provisional-tray hook (~150 LOC, reuses SAP-S4-A's affect-pending-tray shape per `[[sap:66_INVENTED_METHODS]]` #14).
- Brunnr schema additions: `hjarta_episode` and `hjarta_fact` tables (~50 LOC SQL + migration).
- Tests: episodic write + recency-bias retrieval; factual extraction + provisional review; deletion cascade per Brunnr's chunk-id linkage.

**Cost:** ~650 LOC + ~400 LOC tests + Brunnr migration.

**Risk:** Medium. The extraction step is LLM-bound; cost and accuracy must be managed. Provisional tray makes errors recoverable.

### 5.3 Add: Andlit-unity protocol (protocol-only, no client)

**ADR-Proposed-CDK-S5-E:** Adopt the Andlit-unity *protocol* per ADR-Proposed-CDK-010 + invention `[[68]]` #20. Client is deferred indefinitely.

- `docs/protocols/andlit-unity-protocol.md` — protocol specification document.
- `src/ember/spark/funi/andlit_protocol/` — server-side reference implementation.
- WebSocket + signed token auth; handshake; persona sync; pipeline events.
- Token-issuance CLI: `ember andlit token issue <device_name>`, `ember andlit token revoke`.
- No Unity code in this slice. The protocol is documented; client implementations are out-of-tree.
- Tests: protocol round-trip with a Python-side reference client; token auth; replay-attack resistance.

**Cost:** ~600 LOC + ~350 LOC tests + the protocol spec document.

**Risk:** Low. The protocol is small; the spec is the deliverable; no Unity surface in tree.

### 5.4 Slice 5 — Revised Shape

**Theme:** *Plural Minds, Plural Memories, Bilingual Voice, Protocol-Bridged.*

**ADRs:**

| ADR | Topic | Source |
|---|---|---|
| Hermes-S4-A | MCP client | Hermes |
| Hermes-S4-B | Memory provider ABC (Vinátta reserved) | Hermes |
| Hermes-S4-C | Agent-initiated skill writes | Hermes |
| SAP-S5-A | Behavior engine (with affect-aware cooldown) | SAP |
| SAP-S5-B | First IM bot | SAP |
| **CDK-S5-C** | **Bilingual Rödd baseline (VOICEVOX + Piper + router + catalogue)** | **CDK** |
| **CDK-S5-D** | **ChatMemory two-store pattern for Hjarta** | **CDK** |
| **CDK-S5-E** | **Andlit-unity protocol (spec + Python reference server)** | **CDK** |

**Cost (revised):** ~3,950 LOC + ~2,100 LOC tests. Calendar: 14-16 weeks. **This slice is large**; sub-slicing into 5a/5b/5c is recommended.

**Suggested sub-slicing:**

- **5a (~6 weeks):** Hermes triplet (S4-A/B/C) + SAP behavior engine (S5-A).
- **5b (~4 weeks):** SAP first IM bot (S5-B) + CDK bilingual Rödd (S5-C).
- **5c (~4 weeks):** CDK ChatMemory two-store (S5-D) + CDK Andlit protocol (S5-E).

Each sub-slice ships independently; operators see incremental value.

**Acceptance criterion additions (over SAP-proposed):**

> 6. **New (CDK-S5-C):** `ember chat` with voice-output enabled speaks English via Piper and Japanese via VOICEVOX as detected from the LLM response's text. `ember voice catalogue` lists registered voices; `ember voice introspect <utterance_id>` shows the engine, character, and license posture.
> 7. **New (CDK-S5-D):** `ember memory pending` shows extracted facts awaiting operator confirmation; `ember memory confirm <fact_id>` lands the fact in the factual store; `ember memory recall "what do you know about me?"` returns confirmed facts.
> 8. **New (CDK-S5-E):** A reference Python client connects to Ember's `andlit-unity-protocol` WebSocket, completes handshake with a signed token, receives a `PersonaSnapshot`, and receives `PipelineEvent` updates as conversation proceeds.

---

## 6. Proposed Revisions to SAP-Proposed Slice 6 — *Embodied at T0 (Multiple Runtimes)*

SAP's slice 6 (per `[[sap:67_SLICE_PLAN_REVISIONS]]#4.3`) is the *Embodied at T0* slice — VRM/Live2D pipeline, consent gating, composition library, cued voice. The CDK findings add the **conditional uLipSync adoption** (per ADR-Proposed-CDK-009) and the **mora-level prosody Hugarsýn surface** (per invention `[[68]]` #11), both of which complete the embodiment story.

### 6.1 Add: mora-level prosody Hugarsýn surface

**ADR-Proposed-CDK-S6-F:** Adopt the mora-level prosody Hugarsýn surface per invention `[[68]]` #11.

- Extend `src/ember/spark/rodd/providers/voicevox.py` from slice 5 to capture and persist the `/audio_query` intermediate.
- `src/ember/spark/hugarsyn/voice_introspect.py` — operator-facing introspection of mora-level prosody.
- `ember introspect voice <utterance_id>` CLI — shows mora structure, pitch contour, accent positions.
- `ember voice edit <utterance_id>` — replay with edited prosody (advanced).
- Tests: mora capture, replay with edits, audit-log linkage.

**Cost:** ~200 LOC + ~100 LOC tests.

**Risk:** Low. The intermediate is captured; the introspection is presentation.

### 6.2 Add: uLipSync (conditional on Andlit-unity client adoption)

**ADR-Proposed-CDK-S6-G:** Adopt uLipSync per ADR-Proposed-CDK-009 *if* the Unity client is being built. **Conditional ADR; defer to Wave 6+ unless client work is committed.**

- Out-of-tree (lives in `ember-unity-client` repo when that exists).
- Andlit-unity-protocol carries `LipSyncFrame` events; the Unity client renders them.
- No Python-side work for uLipSync itself; the protocol already supports it via slice 5's CDK-S5-E.

**Cost:** zero in slice 6 if client work has not started.

### 6.3 Slice 6 — Revised Shape

**Theme:** *Embodied at T0 — Live2D (in-house) and VRM (in-house) and Unity (via protocol).*

**ADRs:**

| ADR | Topic | Source |
|---|---|---|
| SAP-S6-A | VRM/Live2D pipeline (T0/T1) | SAP |
| SAP-S6-B | Consent-token expression gating | SAP-derived |
| SAP-S6-C | Composition-first expression library | SAP-derived |
| SAP-S6-D | Cued voice library workflow (now built on slice-5 baseline) | SAP-derived |
| SAP-S6-E | Avatar-as-backpressure overlay | SAP-derived |
| **CDK-S6-F** | **Mora-level prosody Hugarsýn surface** | **CDK** |
| **CDK-S6-G** | **uLipSync (conditional on Unity-client adoption)** | **CDK** |

**Cost (revised):** ~2,200 LOC + ~900 LOC tests. Calendar: 10-12 weeks.

The cued voice workflow (SAP-S6-D) is *simpler in revised form* because slice 5 already supplies the baseline Rödd. The slice-6 cued library is a *layer on top* of the baseline, not a from-scratch voice engine.

---

## 7. The Triangulation-Retired Proposals

CDK is the third corpus on the embodiment axis. Some prior single-source proposals deserve revisiting in light of triangulated evidence. Per ADR-Proposed-CDK-006 (three-corpus triangulation as standing discipline), the keeper should ask: **which prior proposals were single-source and now need re-evaluation?**

### 7.1 SAP's *gacha-affect* rejection (ADR-Proposed-SAP-002) — *Reinforced*

CDK's tag protocol could have looked like SAP's affect-mutation pattern. It does not — CDK's tags drive *declared expressive surfaces*, not *hidden affect state*. The three-corpus triangulation confirms: hidden-affect-mutation-from-text remains rejected. ADR-Proposed-SAP-002 stands.

### 7.2 Waifu's *client-side LLM keys* rejection — *Reinforced into a Vow candidate*

Waifu rejected client-side keys (per `[[waifu:51_SECURITY_AND_PRIVACY]]`). CDK shows the same anti-pattern (per ADR-Proposed-CDK-003). Three independent corpora reject the same pattern. The Scribe proposes elevating *"LLM API keys never leave Funi"* from per-codex ADR to *Wave-5-ratified standing rule* — a project law that no future slice can violate.

**Proposed standing rule:** *Server-Held-Keys-Only.* LLM provider API keys live only in Funi-side configuration; never in client artifacts (electron build, Unity build, mobile build, browser build).

### 7.3 SAP's MOSS Chinese voice integration — *Re-shape with bilingual baseline as foundation*

SAP's `moss_tts.py` study informed an inferred Chinese voice integration path. CDK's bilingual Rödd baseline (English + Japanese) is *adjacent*; the same router pattern that handles JP/EN extends naturally to ZH (Chinese). Rather than a separate "Chinese voice slice", the bilingual baseline becomes a *multilingual* baseline as additional language modules are added (each ~100 LOC of language-detection rule + provider routing).

**Proposed adjustment:** rename slice 5's CDK-S5-C from *bilingual Rödd baseline* to **multilingual-extensible Rödd baseline** — ship with EN + JP; the architecture supports adding ZH (MOSS), KO, etc. as future modules.

### 7.4 Waifu's Tier-CLOUD parallel branch — *Refined with three-axis matrix*

Waifu introduced Tier-CLOUD as a parallel branch to the SAP tier ladder. CDK adds the *Unity-native local* axis. The keeper now faces a *three-axis embodiment matrix*: electron-local / cloud-streaming / Unity-native-local. The Cartographer's `[[60_TRIANGULATION]]` formalizes this.

**Proposed adjustment:** the slice 6+ embodiment work explicitly addresses *which of the three runtimes* an operator can deploy. Slice 6 ships electron-local (in-house). Slice 7+ ships Unity-native-local via the protocol. Cloud-streaming via LiveKit remains optional per Waifu's ADR-WAIFU-003.

---

## 8. The Wave 5 Triangulation Standing Rule

ADR-Proposed-CDK-006 proposes three-corpus triangulation as standing design discipline. This doc *operationalizes* the proposal as a procedural rule for slice-plan revisions:

**Proposed standing rule (slice 3 or 4 ratification):**

> **Triangulation-Before-Major-Decision.** Before any slice plan ratifies a True Name addition, a Vow proposal, or a slice-shape revision, the keeper checks whether *three independent corpora* have been studied for the relevant design space. If three corpora are not yet studied, the decision is deferred until a third corpus has been corpus-mined, or the keeper explicitly waives the discipline with rationale recorded in the slice plan ratification ADR.

This rule applies to:

- True Name additions (Andlit-unity, Rödd, etc.).
- Vow proposals (Federated Self, Embodied Honesty, etc.).
- Major slice-shape revisions.

Does not apply to:

- ADR-Proposed-level decisions (single-codex evidence is enough to propose).
- Minor refinements (typed retry parameter tweaks, etc.).
- Operator-config-shape decisions.

The discipline becomes a Scribe-checked precondition for synthesis-layer ratification.

---

## 9. The Five Proposals at a Glance

| # | Proposal | Slice | Type | Recommendation |
|---|---|---|---|---|
| 1 | Slice 3 — *Skilled, Bridged, Quiet, Tiered, Identified, Multi-Provider, Tailnet-Bound* | 3 | Revision (additive over SAP) | **Propose** |
| 2 | Slice 4 — *Felt, Visible, Awake, Piped, Listening* | 4 | Revision (adds pipeline substrate + VAD) | **Propose** |
| 3 | Slice 5 — *Plural Minds, Plural Memories, Bilingual Voice, Protocol-Bridged* | 5 | Revision (adds Rödd, ChatMemory, Andlit-unity protocol) | **Propose** (with sub-slicing) |
| 4 | Slice 6 — *Embodied at T0 — Live2D, VRM, Unity-via-protocol* | 6 | Revision (adds mora introspection, conditional uLipSync) | **Propose** |
| 5 | Standing rule — *Triangulation-Before-Major-Decision* | meta | New rule | **Propose** |

---

## 10. Risk Register

| Risk | Mitigation |
|---|---|
| Slice 3 grew from SAP's 2,050 LOC to CDK-revised 2,780 LOC; operator waits longer for slice-3 value | Sub-slice into 3a (Hermes), 3b (SAP), 3c (CDK); each ships independently. |
| Slice 5 at 3,950 LOC is genuinely large | Sub-slice into 5a/5b/5c per `§5.4`. Each sub-slice has operator-visible value. |
| Pipeline-as-resource substrate in slice 4 is non-trivial; getting it right early matters | Ship the substrate first (Phase 28-29); affect engine builds against stable substrate. Architect review of pipeline shape before code. |
| VOICEVOX engine is an external operator install | Catalogue discipline + per-engine probe + fallback chain ensures graceful degradation. |
| ChatMemory extraction step has LLM cost | Provisional tray makes errors recoverable; extraction is opt-in per session. |
| Andlit-unity protocol may be over-engineered for a client that may not arrive for a year | Protocol is small (~600 LOC); the spec is the deliverable; if no client arrives, the protocol can be revised or retired without loss. |
| The triangulation-before-major-decision rule becomes paperwork | Per ADR-Proposed-CDK-006: Scribe audits at Wave close; rule applies only to True Names, Vows, and major slice revisions — not to all ADRs. |
| Three-codex revisions to slice 3 conflict with each other | The slice-3 acceptance criterion is the integration test; if conflicts surface, the keeper resolves at ratification time. |

---

## 11. Cross-Codex Interaction

The Hermes, Peer, SAP, Waifu, and CDK codexes all propose slice-plan revisions or ADRs. Where this CDK doc adds, complements, or revises:

- **MCP** — Hermes-canonical. CDK does not contradict. Slice 3 ships the MCP server.
- **Skill subsystem** — Hermes-canonical. CDK does not contradict.
- **Memory provider plug-in** — Hermes (Vinátta) and Peer (Letta/Honcho/Mem0) converge; CDK adds the *ChatMemory two-store* pattern as a *concrete reference implementation*, not a competing abstraction. The Vinátta ABC accommodates ChatMemory as one provider shape.
- **Affect engine** — SAP-canonical. CDK's pipeline-as-resource substrate is the *plumbing* affect engine builds on.
- **Tier ladder** — SAP-canonical. Waifu adds the Tier-CLOUD parallel branch. CDK adds invention `[[68]]` #9 (tier-aware embodiment selection algorithm) as runtime selection logic.
- **Failsafe-default-quiet** — SAP-canonical. CDK reinforces.
- **Persona-id** — SAP-canonical. CDK extends with cross-runtime persona portability (`[[68]]` #10).
- **Avatar** — SAP-canonical for in-house Live2D/VRM. Waifu adds cloud-streaming. CDK adds Unity-native (via protocol).
- **Voice** — CDK-canonical for the *baseline*. SAP adds MOSS Chinese as a future module. Cued workflow remains SAP-shaped.
- **Multi-provider LLM** — Hermes-canonical at abstraction shape. CDK reinforces with `ILLMService` evidence; adds per-provider function-call adapter pattern.
- **Tailnet-bind-default** — CDK-canonical (codifies the standing memory at `[[ember:feedback_tailnet_access]]`).
- **Three-corpus triangulation discipline** — CDK-canonical (per ADR-Proposed-CDK-006).

The full braided phasing across the six codexes lives in `[[6A_INTEGRATION_ROADMAP]]`.

---

## 12. The Keeper's Checklist

If the keeper takes up these proposals:

1. Read `[[hermes:65_SLICE_PLAN_REVISIONS]]`, `[[sap:67_SLICE_PLAN_REVISIONS]]`, `[[waifu:60_REALTIME_TIER_FOR_ANDLIT]]` — the prior proposals.
2. Read this doc (`[[69_SLICE_PLAN_REVISIONS]]`) for CDK-shaped additions.
3. Read `[[67_DECISION_RECORDS]]` for the 12 CDK-derived ADR-Proposed records.
4. Read `[[68_INVENTED_METHODS]]` for the 20 CDK-adjacent inventions.
5. Read `[[6A_INTEGRATION_ROADMAP]]` for the six-codex phasing.
6. Read `[[6B_EMBER_WAVE_5_SLICE]]` for the concrete Wave-5 slice candidate that bundles these revisions.
7. Decide which proposals from `§9` (this doc) to accept, defer, or reject.
8. If accepting slice-3 revisions: edit `EMBER_THIRD_SLICE_PLAN.md` per the revised shape. Ratify via next-available ADR.
9. If accepting slice-4/5/6 revisions: author the respective slice plans per the revised shapes.
10. If accepting *Triangulation-Before-Major-Decision*: ratify as a standing rule in the next slice plan ratification ADR.

The Scribe does not perform any of these steps. The Scribe proposes the territory; the keeper draws the map.

---

## 13. What Is Explicitly NOT Proposed

- Any change to slice 1 or slice 2 ratifications.
- Any change to existing ADRs.
- Any rename of an existing True Name.
- Any modification to `docs/SYSTEM_VISION.md`, `docs/architecture/ARCHITECTURE.md`, `docs/CROSS_PLATFORM_PLAN.md`.
- The Unity client itself (only the protocol is in-tree; client is out-of-tree per CDK-S5-E).
- Any commitment to specific Unity LTS versioning, Unity-side build pipeline, Unity-side asset workflows. Those live in the future `ember-unity-client` project.
- Any commitment to specific Japanese voice characters or licenses beyond the catalogue manifest discipline.

---

## 14. Cross-References

- `[[60_TRIANGULATION]]` — Cartographer's three-axis read; the foundation these revisions build on.
- `[[61_ANDLIT_UNITY_TIER]]` — Cartographer's Andlit-unity argument that slice 5's CDK-S5-E ratifies.
- `[[63_MULTIMODAL_PIPELINE]]` — Cartographer's pipeline architecture that slice 4's CDK-S4-F ratifies.
- `[[65_MEMORY_INTEGRATION]]` — Cartographer's ChatMemory argument that slice 5's CDK-S5-D ratifies.
- `[[66_JAPANESE_VOICE_INTEGRATION]]` — Scribe's voice teaching that slice 5's CDK-S5-C builds on.
- `[[67_DECISION_RECORDS]]` — the 12 CDK-derived ADR-Proposed records (CDK-001 through CDK-012).
- `[[68_INVENTED_METHODS]]` — the 20 CDK-adjacent inventions.
- `[[6A_INTEGRATION_ROADMAP]]` — six-codex phasing.
- `[[6B_EMBER_WAVE_5_SLICE]]` — concrete Wave-5 slice proposal.
- `[[sap:67_SLICE_PLAN_REVISIONS]]` — SAP-side slice-plan proposals (the most-comprehensive prior).
- `[[sap:69_INTEGRATION_ROADMAP]]` — SAP-side cross-codex roadmap (the prior braid).
- `[[hermes:65_SLICE_PLAN_REVISIONS]]` — Hermes-side proposals.
- `[[waifu:60_REALTIME_TIER_FOR_ANDLIT]]` — Waifu-side Tier-CLOUD branch.
- `[[waifu:61_DECISIONS_AND_INVENTIONS]]` — Waifu-side ADRs and inventions.
- `[[ember:EMBER_SECOND_SLICE_PLAN]]` — the slice-2 plan all proposals build from.
- `[[ember:0013-second-slice-ratification]]` — the standing-rules ADR.
- `[[ember:feedback_tailnet_access]]` — the standing memory codified by CDK-S3-L.

---

## What This Means for Ember

**True Names affected:** All six existing, plus the proposed Andlit-unity and Rödd. Funi (slice 3 multi-provider + tailnet bind, slice 4 pipeline substrate, slice 5 Andlit protocol). Strengr (slice 3 function-call adapters). Brunnr (slice 5 ChatMemory schema). Smiðja (slice 4 sub-agent supervision, slice 5 tool-aware skill writes). Hjarta (slice 5 two-store memory). Munnr (slice 4 VAD, slice 5 Rödd baseline, slice 6 mora introspection). Andlit-unity-proposed (slice 5 protocol; slice 6+ optional client). Rödd-proposed (slice 5 baseline; slice 6 cued workflow).

**Vows touched:**

- *Most reinforced by CDK additions:* **Modular Authorship** (pipeline substrate + per-provider adapters + voice catalogue), **Pluggable Storage** (extended to LLM provider + voice provider + memory provider + embodiment runtime).
- *Most strengthened:* **Tiered Presence** (now spans electron-local / cloud-streaming / Unity-native-local).
- *Most clarified:* **Federated Self** (cross-runtime persona portability extends the persona-id foundation).
- *Most reinforced by triple-corpus rejection:* **Surface Without Surveillance** (server-held-keys-only proposed as elevated rule).
- *Most watched:* **Smallness** — slice 3 at 2,780 LOC and slice 5 at 3,950 LOC are large. Mitigation: sub-slicing per `§3.5`, `§5.4`.

**Adopt:**

- The three CDK-shape additions to slice 3 (second native provider, function-call adapter, tailnet-bind-default).
- The CDK-shape additions to slice 4 (pipeline-as-resource substrate, Silero VAD).
- The CDK-shape additions to slice 5 (bilingual Rödd, ChatMemory two-store, Andlit-unity protocol).
- The CDK-shape additions to slice 6 (mora-level prosody Hugarsýn surface).
- The standing rule *Triangulation-Before-Major-Decision* per ADR-Proposed-CDK-006.
- The standing rule *Server-Held-Keys-Only* (elevated from three-corpus rejection).

**Adapt:**

- The SAP-proposed *bilingual Rödd* becomes *multilingual-extensible Rödd baseline* — ship with EN + JP; architecture supports ZH/KO/etc. as future modules.
- The SAP-proposed cued voice workflow in slice 6 *builds on* the slice-5 baseline rather than being a from-scratch voice engine.

**Avoid:**

- Slicing the Unity *client* into Wave 5 — too heavy. Protocol-only, deferred client.
- Bundling the pipeline substrate and the affect engine into one sub-slice — the substrate must land first.
- Adding a *third* slice-3 sub-slice without sub-slicing the work — operators need incremental value.
- Treating the CDK ADR catalogue as twelve independent decisions — they cluster into slice-shaped bundles per `§9`.

**Invent:**

The keeper-procedural invention this doc contributes is **slice-plan-revision-as-triangulated-merge** — when three or more corpora propose revisions to the same slice space, the merge is not "pick the largest one" or "union all proposals" but *the smallest cohesive shape that honors all three teachings*. This is the operating principle behind every revision in this doc: SAP's affect engine + CDK's pipeline substrate, not "two competing slice 4s"; SAP's cued voice + CDK's bilingual baseline, not "two competing voice slices". The merge discipline is itself an invention worth naming.

**Concrete next step for the keeper:**

1. Read this doc.
2. Read `[[6B_EMBER_WAVE_5_SLICE]]` for the concrete slice that bundles the *most-ready* of these revisions.
3. Read `[[6A_INTEGRATION_ROADMAP]]` for how the revisions phase across the six-codex braid.
4. Decide whether to ratify the slice-3 revisions (smallest scope, fastest land) or to wait for the full Wave-5 slice proposal.
5. If ratifying slice-3 revisions: edit `EMBER_THIRD_SLICE_PLAN.md`; ratify via next-available ADR after 0024.
6. If ratifying *Triangulation-Before-Major-Decision*: include in the next slice plan ratification.

**The proposals stand as written. The slice plan does not change.**

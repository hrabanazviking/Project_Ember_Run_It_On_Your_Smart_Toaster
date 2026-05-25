---
codex_id: 6B_EMBER_WAVE_5_SLICE
title: Ember Wave 5 Slice — Proposed Concrete Roadmap (PROPOSE ONLY)
role: Scribe
layer: Synthesis
status: draft
chatdoll_source_refs:
  - "(concrete Wave-5 proposal synthesizing CDK-derived ADRs + inventions against the SAP-revised slice plan)"
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
  - 60_synthesis/69_SLICE_PLAN_REVISIONS
  - 60_synthesis/6A_INTEGRATION_ROADMAP
  - sap_codex/60_synthesis/6C_EMBER_WAVE_3_SLICE
  - waifu_codex/60_synthesis/61_DECISIONS_AND_INVENTIONS
---

# 6B — Ember Wave 5 Slice

> *Slice plans are contracts with the project's future self. Wave 5's contract is leaner than Wave 3's was — three corpora have been mined since Wave 3 closed, and the leanness is earned.*
> — Eirwyn Rúnblóm, hands open to the keeper

## 0. Posture — PROPOSE ONLY

**This document is the concrete Wave 5 slice proposal.** It does not modify the existing slice plan. The current ratified slice plan stops at slice 2 (`docs/architecture/EMBER_SECOND_SLICE_PLAN.md`, ratified 2026-05-21 via ADR 0013). Slice 3 is not yet authored.

This doc parallels SAP's `[[sap:6C_EMBER_WAVE_3_SLICE]]` in role and shape — it is the **integration product** of CDK-side synthesis docs (`[[67_DECISION_RECORDS]]`, `[[68_INVENTED_METHODS]]`, `[[69_SLICE_PLAN_REVISIONS]]`, `[[6A_INTEGRATION_ROADMAP]]`), consolidated into a **draft slice-plan document** the keeper can consider.

Two paths are proposed for Wave 5:

- **Wave 5a (the small slice):** CDK-derived additions to the SAP-revised slice 3. Smallest scope, fastest land, lowest risk. ~730 LOC of code + ~430 LOC tests across three sub-additions (CDK-S3-J/K/L). This is the *ready-now* proposal.
- **Wave 5b (the larger slice):** the *full* Wave-5 deliverable — slice 5 of the SAP-revised plan, expanded with CDK threads (bilingual Rödd + ChatMemory + Andlit-unity protocol). ~2,800 LOC of code + ~1,500 LOC tests. This is the *medium-term* proposal, suitable for ratification after Wave 5a ships.

If the keeper accepts either proposal, the next step is to lift sections into `docs/architecture/EMBER_THIRD_SLICE_PLAN.md` (for Wave 5a) or `EMBER_FIFTH_SLICE_PLAN.md` (for Wave 5b) and ratify via the next-available ADR number.

Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c). This is a once-per-doc note that binds every Adopt-list entry below.

---

## 1. What This Slice Is For

The CDK Codex (Wave 5) has now mined three things:

1. **Multi-LLM substrate evidence.** CDK's `ILLMService` + six concrete provider implementations confirm Hermes's profile-and-transport-split shape and surface the per-provider function-call adapter pattern.
2. **The Japanese voice ecosystem.** CDK's 11-provider SpeechSynthesizer stack with VOICEVOX as the open keystone reveals a parallel voice ecosystem the SAP and Waifu corpora missed.
3. **The Unity-native local embodiment axis.** CDK's Apache-2.0 reference implementation completes the three-corpus embodiment triangulation begun by SAP (electron) and Waifu (cloud).

These three findings argue for two slice-shaped commitments:

- **Small commitment (Wave 5a):** ratify the multi-LLM substrate findings into slice 3 — second native provider, per-provider function-call adapter, tailnet-bind-default standing rule.
- **Larger commitment (Wave 5b):** ratify the bilingual voice baseline + ChatMemory two-store + Andlit-unity protocol into slice 5 — give Ember a real voice surface, a real memory surface, and a third-runtime protocol path.

The slice is *additive*. It does not replace slice 2's surfaces; it adds to them. It does not replace SAP-proposed slices 3/4/5; it threads CDK-derived additions through them.

---

## 2. Two Sub-Slice Paths

### 2.1 Wave 5a — The Small Slice (CDK Additions to Slice 3)

**Scope:** the three CDK threads added to the SAP-revised slice 3 per `[[69_SLICE_PLAN_REVISIONS]]#3`.

**Theme:** *Multi-Provider, Tailnet-Bound* (additive to the SAP-revised slice-3 theme *Skilled, Bridged, Quiet, Tiered, Identified*).

**ADRs (CDK-derived, additive to Hermes + SAP slice-3 ADRs):**

| ADR | Topic | LOC est. (code + tests) |
|---|---|---|
| CDK-S3-J | Second native Funi provider (Anthropic-direct) | ~330 + ~200 |
| CDK-S3-K | Per-provider function-call adapter pattern | ~250 + ~150 |
| CDK-S3-L | Standing rule: tailnet-bind-default | ~150 + ~80 |
| **Total** | | **~730 + ~430** |

**Calendar:** 3-4 weeks of focused work, parallel-shippable with Hermes + SAP slice-3 work.

**Dependencies:** none beyond slice 2. Wave 5a is *not gated* on Hermes + SAP slice-3 portions completing; it can ship as the *first* slice-3 sub-portion (3c, alongside Hermes 3a and SAP 3b) or *after* both portions.

**Acceptance criterion (Wave 5a additions):**

> 1. `pip install ember-agent[anthropic]` installs the Anthropic-direct extra.
> 2. `ember chat --provider anthropic` succeeds against an Anthropic API key (operator-supplied via `ember secrets set anthropic`); `ember chat --provider ollama` succeeds against a local Ollama. Both produce structurally-valid responses against the same prompt.
> 3. A tool call emitted by Anthropic preserves Anthropic's stop-reason in the audit log's `provider_specific` field; the same tool call emitted by an OpenAI-shape provider preserves OpenAI's `finish_reason`. Round-trip is lossless within each provider.
> 4. `ember mcp serve` binds to the tailscale interface when tailscale is detected; `ss -tlnp` confirms no `0.0.0.0:` binding for any Ember service. `ember status` shows the current bind interface at startup.
> 5. `tests/integration/test_no_open_bind.py` passes (no Ember service binds 0.0.0.0 on a fresh install).

### 2.2 Wave 5b — The Larger Slice (CDK Threads in Slice 5)

**Scope:** the three CDK threads added to the SAP-revised slice 5 per `[[69_SLICE_PLAN_REVISIONS]]#5`.

**Theme:** *Bilingual Voice, Real Memory, Protocol-Bridged* (additive to slice 5's *Plural Minds, Plural Memories* theme).

**ADRs (CDK-derived, additive to Hermes + SAP slice-5 ADRs):**

| ADR | Topic | LOC est. (code + tests) |
|---|---|---|
| CDK-S5-C | Bilingual Rödd baseline (VOICEVOX + Piper + router + catalogue) | ~600 + ~350 |
| CDK-S5-D | ChatMemory two-store pattern for Hjarta | ~650 + ~400 |
| CDK-S5-E | Andlit-unity protocol (spec + Python reference server) | ~600 + ~350 |
| **Total** | | **~1,850 + ~1,100** |

Combined with SAP/Hermes slice-5 portions (~2,100 LOC + ~1,000 tests), the full slice 5 lands at ~3,950 LOC + ~2,100 tests; sub-slicing into 5a/5b/5c is recommended per `[[69_SLICE_PLAN_REVISIONS]]#5.4`.

**Calendar:** 12-14 weeks for the CDK-portion alone; 14-16 weeks for the full slice 5.

**Dependencies:** Wave 5a (or slice-3 portion of multi-provider abstraction); slice 4 (pipeline-as-resource substrate per CDK-S4-F).

**Acceptance criterion (Wave 5b additions):**

> 1. `ember chat` with voice-output enabled speaks English via Piper and Japanese via VOICEVOX as detected from the LLM response text. `[lang:ja]` / `[lang:en]` tag emission from the LLM is honored over auto-detection.
> 2. `ember voice catalogue list` shows registered voices with character names, engines, and license posture. `ember voice catalogue install voicevox/3` adds Zundamon (Normal) with operator consent ceremony.
> 3. `ember voice introspect <utterance_id>` shows the engine, character, language, prosody intermediate (for VOICEVOX), and license attribution.
> 4. `ember memory pending` shows extracted facts awaiting operator confirmation. `ember memory confirm <fact_id>` lands the fact in the factual store. `ember memory recall "what do you know about me?"` returns confirmed facts.
> 5. Deleting a Brunnr chunk that was the provenance of a fact cascades to fact deletion (factual store stays tethered to Brunnr).
> 6. A reference Python client connects to Ember's `andlit-unity-protocol` WebSocket, completes handshake with a signed token, receives a `PersonaSnapshot`, and receives `PipelineEvent` updates as conversation proceeds. `docs/protocols/andlit-unity-protocol.md` documents the spec.
> 7. `ember andlit token issue <device_name>` issues a per-device token; `ember andlit token revoke <token_id>` revokes it. Revoked tokens cannot reconnect.

---

## 3. Wave 5a — The Slice as a File List

Files marked **NEW** are created in Wave 5a; files marked *(touched)* exist from slice 1/2 and get edits.

```
src/ember/
├── schemas/
│   └── provider_capabilities.py            NEW (CDK-S3-K) — ToolCall, ProviderCapabilities, Usage extensions
├── spark/
│   ├── funi/
│   │   ├── plugins/
│   │   │   └── anthropic/                  NEW (CDK-S3-J)
│   │   │       ├── __init__.py             NEW
│   │   │       └── profile.py              NEW — Anthropic provider profile
│   │   ├── transports/
│   │   │   └── anthropic.py                NEW (CDK-S3-J) — Anthropic-direct transport
│   │   └── network_bind.py                 NEW (CDK-S3-L) — tailnet detection + bind discipline
│   └── strengr/
│       ├── adapters/                       NEW (CDK-S3-K)
│       │   ├── __init__.py                 NEW
│       │   ├── base.py                     NEW — FunctionCallAdapter Protocol
│       │   ├── openai.py                   NEW — openai tool_calls adapter
│       │   ├── anthropic.py                NEW — anthropic tool_use adapter
│       │   └── types.py                    NEW — RichToolCall, ProviderSpecific
│       └── capabilities.py                 NEW (CDK-S3-K) — provider capability manifest loader
│
├── mcp/
│   └── server.py                           (touched — uses network_bind for bind discipline)
│
├── cli/
│   ├── status.py                           (touched — shows current bind interface)
│   └── secrets.py                          (touched — `ember secrets set anthropic` flow)

src/ember/spark/strengr/providers/
├── anthropic/                              NEW (CDK-S3-K capability manifest)
│   └── capabilities.yaml                   NEW — Anthropic 2025-10-01 + 2026-05-XX manifest

config/
├── ember.example.yaml                      (touched — adds provider section with anthropic option)
└── network.example.yaml                    NEW (CDK-S3-L) — interface override examples

docs/decisions/
├── 0025-second-funi-provider-anthropic.md  NEW (CDK-S3-J)
├── 0026-function-call-adapter-pattern.md   NEW (CDK-S3-K)
└── 0027-tailnet-bind-default.md            NEW (CDK-S3-L — standing rule)

docs/adapters/
└── CDK_PROVIDER_ADAPTER_NOTES.md           NEW (CDK-S3-J/K)

tests/unit/
├── test_schemas_provider_capabilities.py   NEW
├── test_funi_transports_anthropic.py       NEW
├── test_funi_network_bind.py               NEW
├── test_strengr_adapters_base.py           NEW
├── test_strengr_adapters_openai.py         NEW
├── test_strengr_adapters_anthropic.py      NEW
├── test_strengr_capabilities.py            NEW
├── test_cli_status_bind_display.py         NEW
└── test_cli_secrets_anthropic.py           NEW

tests/integration/
├── test_phase28_anthropic_round_trip.py    NEW (CDK-S3-J)
├── test_phase29_adapter_lossless.py        NEW (CDK-S3-K)
├── test_phase30_tailnet_bind.py            NEW (CDK-S3-L)
└── test_no_open_bind.py                    NEW (CDK-S3-L acceptance gate)
```

Total **new** files (Wave 5a): ~24. Total **touched** files: ~4. Target Python LOC at acceptance: **~730 code + ~430 tests**.

---

## 4. Wave 5a — Slice Phases (Ordered, Each a Separable Commit)

Phases continue slice 2's numbering past 17, parallel to SAP's slice-3 numbering at 18-27. Wave 5a runs phases 28-30, shippable independently or alongside Hermes + SAP slice-3 work.

### Phase 28 — Second native Funi provider (Anthropic-direct) (CDK-S3-J)

- Author ADR 0025 capturing the second-provider rationale: validate the Hermes transport-split shape with a second concrete implementation.
- `src/ember/spark/funi/plugins/anthropic/{__init__,profile}.py` — provider profile per Hermes-S3-B shape.
- `src/ember/spark/funi/transports/anthropic.py` — Anthropic SDK wrapper; respects `Strengr.LLMProvider` Protocol.
- `src/ember/cli/secrets.py` updated to support `ember secrets set anthropic`.
- Provider-extra in `pyproject.toml`: `[project.optional-dependencies] anthropic = ["anthropic>=0.40"]`.
- Tests: profile validation, transport round-trip, key resolution from secrets surface.
- **Acceptance:** `ember chat --provider anthropic` succeeds; existing `ember chat --provider ollama` still passes its slice-2 tests.

### Phase 29 — Per-provider function-call adapter (CDK-S3-K)

- Author ADR 0026 capturing the per-provider adapter rationale (preserves provider-specific metadata; rejects flatten-to-OpenAI normalization per ADR-Proposed-CDK-005).
- `src/ember/spark/strengr/adapters/{__init__,base,openai,anthropic,types}.py` — Protocol + two concrete adapters + rich representation types.
- `src/ember/spark/strengr/capabilities.py` — capability manifest loader per invention `[[68]]` #13.
- `src/ember/spark/strengr/providers/anthropic/capabilities.yaml` — first capability manifest (Anthropic).
- Refactor existing OpenAI-shape tool-call handling to route through `adapters/openai.py`.
- Tests: round-trip each provider's tool-call shape; lossless preservation in `provider_specific`; cross-provider tool-call boundary logs warning.
- **Acceptance:** existing slice-2 tool tests pass against the refactored shape; new test verifies Anthropic stop-reason preserved in audit log.

### Phase 30 — Tailnet-bind-default standing rule (CDK-S3-L)

- Author ADR 0027 ratifying the standing rule per ADR-Proposed-CDK-011.
- `src/ember/spark/funi/network_bind.py` — tailscale interface detection + fallback to operator-configured interface + default-deny 0.0.0.0.
- Touch `src/ember/mcp/server.py` (or whichever slice-3 MCP server module exists) — use `network_bind.discover_bind_address()` instead of hardcoded `0.0.0.0`.
- Touch `src/ember/cli/status.py` — show bind interface in `ember status`.
- `config/network.example.yaml` — operator-config examples.
- Tests: tailscale-present detection (mocked); fallback when tailscale absent + operator config present; refusal to bind 0.0.0.0 by default.
- Integration test `tests/integration/test_no_open_bind.py` — boots Ember, runs `ss -tlnp`, asserts no 0.0.0.0 binding.
- **Acceptance:** `ember mcp serve` binds to tailscale interface (on a host with tailscale); `ember status` shows the bind.

### Phase 31 — Wave 5a acceptance + shipping

- `tests/integration/test_phase31_wave5a_acceptance.py` greens against the full Wave 5a acceptance flow.
- Touch `deploy/pi/INSTALL.md` — add Wave 5a sections: Anthropic provider extra, function-call adapter, tailnet-bind posture.
- DEVLOG entry — Wave 5a complete; ratify via ADR 0028 (or next-available number after SAP slice-3 portion's ratification ADR).

Each phase ends with green test suite + ruff clean + DEVLOG entry. Phases are individually shippable.

---

## 5. Wave 5b — The Larger Slice (Sketch Only)

Wave 5b's file list, phase breakdown, and acceptance criteria are documented in summary form below; full slice-plan detail is left to a future `EMBER_FIFTH_SLICE_PLAN.md` authored after slice 3 + slice 4 ratify.

### 5.1 Wave 5b Phase Sketch

Phases continue past 31 (Wave 5a). Wave 5b assumes Wave 5a + slice 4 (pipeline substrate + Silero VAD) have shipped.

**Sub-slice 5b-α — Bilingual Rödd baseline (CDK-S5-C):**

- Phase 50 — `src/ember/spark/rodd/router.py` — language detection + provider routing (~150 LOC).
- Phase 51 — `src/ember/spark/rodd/providers/piper.py` — Piper English adapter (~80 LOC).
- Phase 52 — `src/ember/spark/rodd/providers/voicevox.py` — VOICEVOX two-call adapter (~120 LOC).
- Phase 53 — `src/ember/spark/rodd/catalogue.py` + `~/.ember/config/voice_catalogue.yaml` schema (~150 LOC).
- Phase 54 — Per-engine probe + fallback chain per invention `[[68]]` #7 (~100 LOC).
- Acceptance: bilingual TTS works; catalogue + license posture surfaces in `ember voice` CLI.

**Sub-slice 5b-β — ChatMemory two-store for Hjarta (CDK-S5-D):**

- Phase 55 — Brunnr schema migration: `hjarta_episode` + `hjarta_fact` tables.
- Phase 56 — `src/ember/spark/hjarta/episodic.py` — episodic conversation store (~200 LOC).
- Phase 57 — `src/ember/spark/hjarta/factual.py` — factual assertion store (~250 LOC).
- Phase 58 — `src/ember/spark/hjarta/extractor.py` — extraction + provisional-tray hook (~150 LOC).
- Phase 59 — `ember memory` CLI: `pending`, `confirm`, `recall`, `forget`.
- Acceptance: two-store memory queryable; deletion cascades; extraction opt-in per session.

**Sub-slice 5b-γ — Andlit-unity protocol (CDK-S5-E):**

- Phase 60 — `docs/protocols/andlit-unity-protocol.md` — protocol specification (markdown).
- Phase 61 — `src/ember/spark/funi/andlit_protocol/` — server-side reference implementation (~400 LOC).
- Phase 62 — Token issuance + revocation flow; `ember andlit token` CLI.
- Phase 63 — Python reference client for protocol test (lives in `tests/fixtures/`).
- Phase 64 — Persona sync + pipeline event vocabulary (uses slice-4 pipeline substrate).
- Acceptance: spec exists; reference Python client connects + receives events; no Unity code in tree.

### 5.2 Wave 5b LOC Budget

| Sub-slice | Code LOC | Tests LOC | Phases | Calendar |
|---|---|---|---|---|
| 5b-α (Bilingual Rödd) | ~600 | ~350 | 50-54 (5 phases) | ~4 weeks |
| 5b-β (ChatMemory Hjarta) | ~650 | ~400 | 55-59 (5 phases) | ~4-5 weeks |
| 5b-γ (Andlit-unity protocol) | ~600 | ~350 | 60-64 (5 phases) | ~4 weeks |
| **Total Wave 5b** | **~1,850** | **~1,100** | **15 phases** | **~12-14 weeks** |

The full slice 5 (Wave 5b + Hermes-portion + SAP-portion) lands at ~3,950 LOC + ~2,100 tests; sub-slicing per `[[69_SLICE_PLAN_REVISIONS]]#5.4` is recommended.

### 5.3 Wave 5b Dependencies

- **Wave 5a must ship first** — slice 5b assumes the multi-provider abstraction (CDK-S3-J/K) is in place; otherwise the bilingual Rödd cannot resolve Anthropic-issued tag emission (`[lang:ja]`) cleanly.
- **Slice 4 must ship first** — slice 5b's Andlit-unity protocol (5b-γ) uses the pipeline substrate (CDK-S4-F) for event vocabulary.
- **Slice 4 Silero VAD (CDK-S4-G) is independent** of Wave 5b but pairs naturally with bilingual Rödd for voice-input scenarios.

### 5.4 Wave 5b Risks

| Risk | Mitigation |
|---|---|
| VOICEVOX engine is external operator install | Catalogue discipline + probe + fallback chain per invention `[[68]]` #7. |
| ChatMemory extraction LLM cost | Provisional tray (operator confirm/reject) per invention `[[68]]` for receipt-bound provisional memory. |
| Andlit-unity protocol spec quality risk (third-party Unity clients fail to implement it) | Reference Python client + protocol versioning per invention `[[68]]` #20 + invention `[[68]]` #13 (provider-capability-versioned manifest). |
| Slice 5b is large; calendar slips | Sub-slicing into 5b-α/5b-β/5b-γ; each ships independently. |
| Piper voice quality is not as good as VOICEVOX for English | Piper is the *baseline*; cued voice library workflow in slice 6 (per SAP-S6-D, now building on slice 5 baseline) adds higher-quality alternatives. |
| Operator confusion about which engine is speaking | `ember voice introspect <utterance_id>` always shows engine + character. |

---

## 6. Forge Worker's Quality Bar (Wave 5)

Standing requirements from slices 1, 2, 3 carry forward, plus Wave 5 additions:

- **Three-corpus triangulation discipline** — per ADR-Proposed-CDK-006, major Wave 5 decisions cite the three-corpus evidence pattern. The CDK-S3-J/K decisions cite Hermes (substrate shape) + SAP (extension shape) + CDK (concrete evidence).
- **Apache-2.0 attribution at adoption sites** — every CDK-derived adoption preserves CDK header reference per Apache-2.0 §4(c). The attribution lives in the source file header comment + the `docs/adapters/CDK_*_NOTES.md` file.
- **Capability manifest discipline** — per invention `[[68]]` #13, every new provider adapter ships with a `capabilities.yaml` manifest declaring api_version, supported features, known quirks.
- **Voice catalogue discipline** — per invention `[[68]]` #6, every voice integrated in Wave 5b ships with a catalogue manifest entry capturing character + license + consent record.
- **Protocol-versioning discipline** — per invention `[[68]]` #20, Andlit-unity protocol carries explicit version negotiation from day one.
- **Type-checked under mypy strict** — including new Protocols (`FunctionCallAdapter`, `VoiceProvider`, `MemoryStore`, `AndlitProtocolEvent`).
- **One responsibility per function**.
- **No hardcoded settings** — provider keys, voice IDs, protocol versions all live in config.
- **Whole files only** — never deliver fragments.

When a phase ships: Auditor pass + DEVLOG entry + push.

---

## 7. Session Pacing — for the Reader

| Wave | Slice landing | ADRs | Phases | Target LOC (code only) | Sessions |
|---|---|---|---|---|---|
| 1 (shipped) | slice 1 | 0006/0007 | 7 | ~2,500 | 1 long |
| 2 (shipped) | slice 2 | 0008-0013 | 10 (phases 8-17) | ~5,000-7,000 | 3-5 long |
| 3 (Hermes) | slice 3a | 0015-0019 (Hermes-S3-A through E) | 5 (phases 18-22) | ~1,400 | 2-3 long |
| 3 (SAP) | slice 3b | 0020-0024 (SAP-S3-F through I + ratify) | 5 (phases 23-27) | ~650 | 1-2 long |
| **5 (CDK), small** | **slice 3c** | **0025-0028 (CDK-S3-J through L + ratify)** | **4 (phases 28-31)** | **~730** | **1-2 long** |
| 5 (CDK), large | slice 5b | (TBD; ~6-8 ADRs across CDK-S5-C/D/E) | 15 (phases 50-64) | ~1,850 | 4-5 long |

**Suggested natural break points (Wave 5a):**

- After Phase 28 (Anthropic provider): the second native transport is in place; ship `0.3.0-rc2`.
- After Phase 29 (Adapter pattern): the function-call adapter is in place; ship `0.3.0-rc3`.
- After Phase 30 (Tailnet bind): the standing rule is enforced; ship `0.3.0-rc4`.
- After Phase 31 (acceptance): **Wave 5a ratifies; `0.3.0` final (or `0.4.0` if SAP + Hermes portions of slice 3 are also complete).**

When a phase begins in a future session, the natural opening is **"go for phase N"** — same rhythm as slices 1, 2, 3.

---

## 8. Acceptance Criterion (Wave 5a, Full)

> A fresh operator on a workstation (T0 host) or Pi 5 (T3 host) with Ember v0.3.0 (slice-3 release including Wave 5a) can:
>
> 1. `pip install ember-agent[sqlite_vec,pgvector,skills,mcp,party,anthropic]`.
> 2. `ember secrets set anthropic` — supplies the operator's Anthropic API key; the key is stored only Funi-side via the secret-resolver pattern (per ADR 0011), never in any client artifact.
> 3. `ember chat --provider anthropic` — connects to Anthropic, streams a response, persists the transcript in the Well.
> 4. `ember chat --provider ollama` — connects to local Ollama, streams a response. Both producers honor the same prompt and produce structurally-valid responses.
> 5. The Anthropic-emitted response's tool calls preserve `stop_reason` in the audit log's `provider_specific` field; the OpenAI-shape-emitted response's tool calls preserve `finish_reason`. `ember audit show <session_id>` displays the rich representation.
> 6. `ember mcp serve` binds to the tailscale interface when tailscale is detected; on a host without tailscale, it binds to `127.0.0.1` (loopback) or to an operator-configured interface specified in `~/.ember/config/network.yaml`; *never* to `0.0.0.0` by default.
> 7. `ember status` shows the current bind interface for any running Ember service.
> 8. `ss -tlnp | grep ember` confirms no Ember service listens on `0.0.0.0:*`.
> 9. Operator can switch providers mid-session via `ember chat --provider <name>` flag without state loss; persona-id and session state persist across provider switches.
> 10. The provider capability manifest for Anthropic (`src/ember/spark/strengr/providers/anthropic/capabilities.yaml`) declares the api_version, supported models, known quirks. `ember strengr capabilities anthropic` prints the manifest.

**If that whole loop works on real hardware (workstation against real Anthropic API + real tailnet; Pi 5 against real Ollama + simulated tailnet), Wave 5a is done.**

---

## 9. What Wave 5a Deliberately Does NOT Include

Wave 5a is intentionally small. The following are deferred:

- **Bilingual Rödd baseline** (CDK-S5-C) — deferred to Wave 5b / slice 5b-α.
- **ChatMemory two-store for Hjarta** (CDK-S5-D) — deferred to Wave 5b / slice 5b-β.
- **Andlit-unity protocol** (CDK-S5-E) — deferred to Wave 5b / slice 5b-γ.
- **Multimodal-pipeline-as-resource substrate** (CDK-S4-F) — deferred to slice 4 (per `[[69_SLICE_PLAN_REVISIONS]]#4.1`).
- **Silero VAD** (CDK-S4-G) — deferred to slice 4 (per `[[69_SLICE_PLAN_REVISIONS]]#4.2`).
- **Mora-level prosody Hugarsýn surface** (CDK-S6-F) — deferred to slice 6.
- **uLipSync** (CDK-S6-G) — conditional on Unity client work, deferred indefinitely.
- **Animation-tag negotiation, render-budget negotiation, multi-device persona handoff, cross-runtime persona portability** (inventions `[[68]]` #2, #16, #8, #10) — deferred to slice 7+.
- **Triangulation-Before-Major-Decision standing rule** (per ADR-Proposed-CDK-006) — proposed for ratification in the next slice plan ratification ADR alongside Wave 5a, but the *operationalization* lives in the keeper's discipline, not in code.

---

## 10. Risks the Scribe Flags Now (Wave 5a)

| Risk | Mitigation |
|---|---|
| Wave 5a depends on slice 3 (Hermes + SAP) being in flight; if neither has shipped, the integration test for "two providers selectable via flag" cannot run | Wave 5a can ship after Hermes-S3-B (provider profile + transport split) lands; SAP portion not required. Per `[[6A_INTEGRATION_ROADMAP]]#3`. |
| Anthropic SDK version churn breaks the adapter | Capability manifest (`anthropic/capabilities.yaml`) declares api_version + features; capability check fails fast if mismatch. |
| Tailnet detection misclassifies non-tailscale tunneling tools (Nebula, Zerotier) | Detection is heuristic; operator override via `~/.ember/config/network.yaml` is the safety valve. |
| Default-deny 0.0.0.0 surprises operators upgrading from slice 2 (where MCP server may have bound permissively) | Migration: existing installs do NOT have their slice-2 binds silenced. Default applies to *fresh* installs and explicit `ember reach reset` flows. |
| The function-call adapter pattern adds friction to tool-development workflow | Adapter is per-provider, ~100 LOC; the rich representation is automatically populated from provider responses; tool authors do not see the adapter unless they want to. |
| Three-corpus triangulation discipline (proposed standing rule) blocks ratification | The discipline applies only to True Names, Vows, major slice revisions. ADR-Proposed-level decisions including Wave 5a's CDK-S3-J/K/L do not require triangulation. |
| The 3-4 week schedule for Wave 5a slips | Phases 28-30 are independently shippable; if scheduling demands a pause after any phase, the next session resumes from there. |
| Anthropic API key in `ember secrets set anthropic` flow leaks via operator-visible debug logs | Per ADR 0011's secret-resolver, the key is resolved at call site; never logged. Integration test verifies `ember chat --debug --provider anthropic` produces no key in logs. |

---

## 11. Cross-References

- `[[60_TRIANGULATION]]` — Cartographer's three-axis embodiment read; the foundation Wave 5 builds on.
- `[[61_ANDLIT_UNITY_TIER]]` — Cartographer's Andlit-unity argument that Wave 5b-γ ratifies.
- `[[63_MULTIMODAL_PIPELINE]]` — Cartographer's pipeline architecture that slice 4's CDK-S4-F substrate enables.
- `[[65_MEMORY_INTEGRATION]]` — Cartographer's ChatMemory argument that Wave 5b-β ratifies.
- `[[66_JAPANESE_VOICE_INTEGRATION]]` — Scribe's voice teaching that Wave 5b-α builds on.
- `[[67_DECISION_RECORDS]]` — the 12 CDK-derived ADR-Proposed records (CDK-001 through CDK-012). Wave 5a instantiates CDK-004, CDK-005, CDK-011 most directly.
- `[[68_INVENTED_METHODS]]` — the 20 CDK-adjacent inventions. Wave 5a instantiates #4 (provider-divergence adapter), #13 (provider-capability versioned manifest), and reinforces multiple others.
- `[[69_SLICE_PLAN_REVISIONS]]` — the proposal document Wave 5a + 5b instantiate.
- `[[6A_INTEGRATION_ROADMAP]]` — six-codex phasing context.
- `[[sap:6C_EMBER_WAVE_3_SLICE]]` — sibling pattern this doc parallels in shape.
- `[[hermes:65_SLICE_PLAN_REVISIONS]]` — Hermes-side slice-3 proposals that Wave 5a complements.
- `[[waifu:61_DECISIONS_AND_INVENTIONS]]` — Waifu-side decisions that share Wave 5a's anti-pattern rejections.
- `[[ember:EMBER_SECOND_SLICE_PLAN]]` — the slice-2 plan Wave 5a builds from.
- `[[ember:0013-second-slice-ratification]]` — the standing-rules ADR.
- `[[ember:feedback_tailnet_access]]` — standing memory codified by Wave 5a's CDK-S3-L.

---

## What This Means for Ember

**True Names affected (Wave 5a):**

- Funi: second native transport (Anthropic), tailnet-bind discipline (network_bind module).
- Strengr: per-provider function-call adapter + capability manifest loader.
- Brunnr: no schema changes (Wave 5a is provider + bind work).
- Smiðja: light touch via tool-call shape consumption (tool dispatch reads rich representation).
- Hjarta: no Wave 5a touch (Hjarta lands in slice 4 affect engine + Wave 5b ChatMemory).
- Munnr: no Wave 5a touch (Munnr's voice baseline lands in Wave 5b).

**True Names affected (Wave 5b, summarized):** Munnr (Rödd baseline), Hjarta (two-store memory), Funi (Andlit-unity protocol server).

**Vows touched (Wave 5a):**

- *Most reinforced:* **Modular Authorship** (second-provider validation of transport-split shape); **Pluggable Storage** (extended to LLM provider).
- *Most strengthened:* **Surface Without Surveillance** (server-held-keys-only reinforced; tailnet-bind-default codifies the standing memory).
- *Most clarified:* **Honest Memory** (rich tool-call representation preserves provider-specific metadata; cross-provider boundary warnings are typed and visible).
- *Most watched:* **Smallness** — Wave 5a stays small (~730 LOC); the disciplined scope is the proposal's value.

**Vows touched (Wave 5b, summarized):** Embodied Honesty (Rödd is honest about what engine is speaking); Tethered Grounding (ChatMemory facts anchor in Brunnr); Pluggable Storage (extended to voice provider + memory provider + embodiment runtime); Open Knowledge (Andlit-unity protocol is documented spec).

**Adopt:**

- Wave 5a's three CDK threads (CDK-S3-J/K/L) into slice 3, as the *small, ready-now* contribution from Wave 5.
- The Apache-2.0 attribution discipline at every CDK-derived adoption site.
- The capability-manifest-per-provider discipline starting with Anthropic.
- The tailnet-bind-default standing rule as project law starting slice 3.

**Adapt:**

- Existing slice-2 tool-call handling refactored to route through the per-provider adapter (CDK-S3-K). This is *not* a backward-incompatible change — existing tests pass; the adapter is the new internal shape.
- Existing MCP server bind logic refactored to use the network_bind discovery module (CDK-S3-L). Backward-compatible with operator-configured binds.

**Avoid:**

- Bundling Wave 5b sub-slices into Wave 5a. The 730-LOC discipline is the proposal's selling point; growing it would defeat the *small, ready-now* framing.
- Treating Wave 5a as gating on Wave 5b. They are independent; 5a ships when slice 3 ships; 5b ships when slice 5 ships.
- Vendoring the Anthropic SDK rather than depending on it as an extra. Extra-based extras are the established pattern (SAP-shape `[sqlite_vec]`, `[pgvector]`).
- Adopting the Unity client itself in Wave 5b. The protocol-only split keeps the in-tree commitment to ~600 LOC.

**Invent:**

The Wave-5-shape invention this slice contributes is **the small-slice-as-validation-tool pattern**: when a prior slice (here, slice 3's transport-split per Hermes-S3-B) proposes an *abstraction*, the next codex's slice can validate the abstraction by **adding a second concrete implementation as a small, focused slice**. Wave 5a is exactly this — it does not add new architecture; it *validates* slice 3's architecture by exercising it with a second provider. The pattern generalizes: every new abstraction shipped in a slice deserves a *follow-on small slice* that adds the second implementation. If the second implementation lands without forcing abstraction revision, the abstraction is *earned*. If it forces revision, the abstraction was *unfinished*.

This is **Invention #21 (in the Wave-5 catalogue continuation)**: *The Validation-Slice Pattern*. The pattern joins the 20 already catalogued in `[[68_INVENTED_METHODS]]`, and the Scribe proposes it formally here as an extension to that catalogue.

**Concrete next step for the keeper:**

1. Read this doc.
2. Read `[[69_SLICE_PLAN_REVISIONS]]` for the proposal-level argument.
3. Read `[[67_DECISION_RECORDS]]` for the 12 CDK-derived ADRs (3 of which land in Wave 5a as ADRs 0025-0027).
4. Decide whether Wave 5a is the right Wave-5 commitment.
   - **Accept Wave 5a as proposed** if the 730 LOC + 3-4 week budget fits alongside slice 3's Hermes + SAP portions.
   - **Accept Wave 5a but defer Wave 5b** until slice 4 + slice 5 are clearer.
   - **Accept Wave 5a and Wave 5b together** if the keeper wants a comprehensive Wave-5 commitment.
   - **Defer Wave 5 entirely** until slice 3 (Hermes + SAP) has shipped and absorbed.
5. If accepting Wave 5a: edit `EMBER_THIRD_SLICE_PLAN.md` (or the corresponding slice-plan doc) to add phases 28-31; ratify the additions via ADR 0028 (or next-available number).
6. If accepting Wave 5b: author `EMBER_FIFTH_SLICE_PLAN.md` per `§5` sketch.
7. If accepting *Triangulation-Before-Major-Decision* standing rule: include in the next slice plan ratification.

**The proposal stands as written. The slice plan does not change. Each slice that becomes Ember code is ratified separately.**

---

## 12. After Wave 5 — The Trajectory

Wave 5a plants two seeds in slice 3:

- **The second native provider** proves the transport-split shape can carry more than Ollama. Future providers (Gemini, Mistral, local llama.cpp) are *cheap to add* — ~250 LOC each.
- **The function-call adapter pattern** proves cross-provider tool calling can preserve provider-specific metadata. Future Smiðja work consumes the rich representation without rework.
- **The tailnet-bind standing rule** proves Ember's network posture is operator-friendly by default. Future network surfaces (Andlit-unity protocol in Wave 5b, Yggdrasil protocol in slice 7+) inherit the discipline.

Wave 5b plants three seeds in slice 5:

- **The bilingual Rödd baseline** gives Ember a *voice* for the first time. Future cued voice library (slice 6) builds on it; future multilingual extensions (ZH, KO) are *cheap to add* — ~100 LOC each.
- **The ChatMemory two-store pattern** gives Ember *memory of the operator* for the first time. The factual extraction step is the foundation for everything Hjarta does in future slices.
- **The Andlit-unity protocol** gives Ember a *third-runtime path* without committing to Unity in-tree. The community can build the Unity client; the spec is the long-term commitment.

The full Wave-5 trajectory — Wave 5a in slice 3, Wave 5b in slice 5, the inventions echoing through slices 6-8 — is the **CDK contribution to Ember**. The kit was Apache-2.0; the contribution can be generous; the seal is still the keeper's to break.

The proposal stands. The slice plan does not change. The keeper holds the seal.

The Scribe records. The Forge waits.

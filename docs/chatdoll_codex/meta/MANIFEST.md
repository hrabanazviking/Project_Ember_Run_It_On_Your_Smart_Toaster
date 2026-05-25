---
name: chatdoll-codex-manifest
description: Authoritative list of all 69 files in the Chatdoll Codex (63 content + 6 meta), with slugs, scope, owner role, and target length
metadata:
  codex: chatdoll
  type: meta
---

# MANIFEST — Chatdoll Codex

**Total files:** 69 (63 content + 6 meta)
**Target length:** 1,500–4,000 words per content doc (SAP range; source is large)
**Citation convention:** `/tmp/ChatdollKit/<path>:line` for kit; sister-project paths with prefix
**Closer:** every content doc ends with `## What This Means for Ember`
**License:** Apache-2.0 — adopt-friendly

---

## meta/ (6 docs — orchestrator + Scribe)

| Slug | Status |
|---|---|
| (root) `TASK_CHATDOLL_CODEX.md` | ✅ written |
| meta/SHARED_CONTEXT | ✅ written |
| meta/MANIFEST | ✅ written |
| meta/STYLE_GUIDE | ⏳ next |
| meta/INDEX | Scribe final pass |
| meta/READING_ORDER | Scribe final pass |
| meta/CROSS_AGENT_NOTES | Scribe final pass |

---

## 00_vision/ (5 docs — Skald)

| # | Slug | Scope |
|---|---|---|
| 00 | `00_OVERTURE.md` | Why mine CDK after SAP + Waifu; the third position on the embodiment axis (Unity-native local); the Japanese-voice gap in Western codexes |
| 01 | `01_CDK_ESSENCE.md` | What ChatdollKit is at the level of intent: doll-as-companion in Unity's lineage of game-engine character animation |
| 02 | `02_UNITY_AS_RUNTIME.md` | Unity as Ember's potential third embodiment runtime — what it gives (cross-platform reach, mature animation), what it asks (engine commitment, learning curve, binary size) |
| 03 | `03_ANTI_CDK.md` | What CDK refuses or fails to be; Unity-monoculture risks; what Ember must refuse |
| 04 | `04_VISION_SYNTHESIS.md` | Ember's identity revised post-CDK study; how Unity-native fits Andlit + Rödd alongside SAP-electron + Waifu-cloud |

---

## 10_domain/ (14 docs — Architect)

| # | Slug | Scope |
|---|---|---|
| 10 | `10_DOMAIN_MAP.md` | Macro architecture; the 8 Scripts/ subsystems + AIAvatar top-level; dependency graph; sister-project ecosystem |
| 11 | `11_AIAVATAR_DOMAIN.md` | `AIAvatar.cs` top-level controller; dialog mode management; lifecycle |
| 12 | `12_MODEL_CONTROLLER_DOMAIN.md` | `Model/` — animation, expression, gesture sync; VRM integration; uLipSync |
| 13 | `13_DIALOG_PROCESSOR_DOMAIN.md` | `Dialog/` — state machine, intent extraction, topic routing, wakeword |
| 14 | `14_SPEECH_LISTENER_DOMAIN.md` | `SpeechListener/` — STT pipeline, multi-VAD support |
| 15 | `15_SPEECH_SYNTHESIZER_DOMAIN.md` | `SpeechSynthesizer/` — TTS, parallel/sequential prefetch modes |
| 16 | `16_LLM_SERVICE_DOMAIN.md` | `LLM/` — LLMService abstraction over 6+ providers (ChatGPT/Claude/Gemini/Dify/AIAvatarKit/Grok/Command R) |
| 17 | `17_MICROPHONE_MANAGER_DOMAIN.md` | `IO/` — audio capture, noise gate, device control |
| 18 | `18_NETWORK_DOMAIN.md` | `Network/` — SocketServer + JavaScriptMessageHandler dual remote-control |
| 19 | `19_TOOL_DOMAIN.md` | Tool/ToolBase function-calling for AI agents; comparison with SAP tool surface |
| 1A | `1A_MEMORY_DOMAIN.md` | ChatMemoryIntegrator + ChatMemory sister project; episodic + factual storage |
| 1B | `1B_ANIMATION_DOMAIN.md` | `[anim:Name]` tags + `[face:Expression]` tags + ModelRequestBroker + DialogPriorityManager |
| 1C | `1C_UNITY_LIFECYCLE_DOMAIN.md` | Unity-specific: asmdef, MonoBehaviour, ScriptableObject, prefab integration |
| 1D | `1D_MULTI_PLATFORM_DOMAIN.md` | Windows/Mac/Linux/iOS/Android/VR/AR/WebGL build targets; platform-specific deltas |

---

## 20_interface/ (10 docs — Architect: 5, Auditor: 5)

| # | Slug | Owner | Scope |
|---|---|---|---|
| 20 | `20_LLM_SERVICE_INTERFACE.md` | Architect | `ILLMService` contract; how 6+ providers conform; function-call format divergence |
| 21 | `21_TTS_INTERFACE_WESTERN.md` | Auditor | TTS providers Google/Azure/OpenAI/Watson: contract, latency, format |
| 22 | `22_TTS_INTERFACE_JAPANESE.md` | Auditor | TTS providers VOICEVOX/AivisSpeech/VOICEROID/Style-Bert-VITS2/NijiVoice: the deep Japanese stack |
| 23 | `23_STT_INTERFACE.md` | Auditor | STT providers Google/Azure/OpenAI/Silero/AIAvatarKit streaming |
| 24 | `24_VAD_INTERFACE.md` | Architect | Silero ML-based VAD; the `SileroVADProcessor`; ONNX runtime in Unity |
| 25 | `25_ANIMATION_TAG_PROTOCOL.md` | Architect | `[anim:Name]` + `[face:Expression]` tag protocol; how LLM output drives avatar |
| 26 | `26_TOOL_FUNCTION_CALL_INTERFACE.md` | Architect | `ITool` + `ToolBase`; per-provider function-call format adapters |
| 27 | `27_SOCKET_PROTOCOL.md` | Auditor | SocketServer remote control protocol; auth posture (or lack of) |
| 28 | `28_JS_BRIDGE_INTERFACE.md` | Auditor | JavaScriptMessageHandler WebGL ↔ JS bridge; message-origin verification |
| 29 | `29_VRM_INTERFACE.md` | Architect | UniVRM integration; bone/expression mapping; comparison with SAP VRM use |

---

## 30_execution/ (14 docs — Forge-A: 8 core, Forge-B: 6 sister+platform)

### 30_execution/ — Forge-A (core 8)

| # | Slug | Scope |
|---|---|---|
| 30 | `30_UNITY_BOOTSTRAP.md` | AIAvatar instantiation; MonoBehaviour lifecycle; prefab inflation |
| 31 | `31_AIAVATAR_MAIN_LOOP.md` | Dialog state machine driven by `AIAvatar.cs`; per-frame update; mode transitions |
| 32 | `32_STT_LOOP.md` | Mic capture → VAD → STT provider → text emission |
| 33 | `33_TTS_PREFETCH.md` | Parallel vs sequential prefetch; queue management; barge-in interruption |
| 34 | `34_ANIMATION_PIPELINE.md` | `[anim:]` tag extraction → state-machine transition; additive/override blending |
| 35 | `35_LIP_SYNC.md` | uLipSync integration; vowel detection; mouth-shape mapping |
| 36 | `36_FUNCTION_CALL_EXEC.md` | LLM emits function call → ITool resolution → execution → response feeding |
| 37 | `37_BARGE_IN_INTERRUPT.md` | User interrupts mid-TTS; cancel-and-replace pattern; merge-window logic |

### 30_execution/ — Forge-B (sister+platform 6)

| # | Slug | Scope |
|---|---|---|
| 38 | `38_CHATMEMORY_INTEGRATION.md` | `uezo/chatmemory` clone study; FastAPI server; episodic vs factual stores; ChatdollKit integrator pattern |
| 39 | `39_AIAVATARKIT_STREAMING.md` | `uezo/aiavatarkit` study; S2S streaming pipeline; STT server architecture |
| 3A | `3A_AITUBER_CONTROLLER.md` | `uezo/chatdollkit-aituber` study; VTuber streaming integration; comparison with SAP livestream domain |
| 3B | `3B_WEBGL_BUILD.md` | WebGL build pipeline; Emscripten; audio context; memory constraints; 5-10 minute build time |
| 3C | `3C_MOBILE_BUILD.md` | iOS + Android Unity builds; permissions; binary size; on-device LLM viability |
| 3D | `3D_XR_BUILD.md` | VR + AR target considerations; sensor data privacy; performance tier |

---

## 50_verification/ (8 docs — Auditor)

| # | Slug | Scope |
|---|---|---|
| 50 | `50_DEPENDENCY_HEALTH.md` | Burst, UniTask, uLipSync, UniVRM, JSON.NET, Newtonsoft: brittleness map; Unity version coupling |
| 51 | `51_SECURITY_REVIEW.md` | LLM API keys in client builds; socket auth; JS bridge XSS; mobile permissions; XR sensor surfaces |
| 52 | `52_PERFORMANCE_BUDGETS.md` | Unity render budget; STT latency; TTS prefetch latency; lip-sync CPU; per-platform tier |
| 53 | `53_MULTI_LLM_CONSISTENCY.md` | Function-call format divergence across providers; failure handling; provider-fallback discipline |
| 54 | `54_MULTI_TTS_QUALITY.md` | Latency vs voice character; lip-sync drift; provider-specific gotchas |
| 55 | `55_WEBGL_GOTCHAS.md` | Emscripten quirks; audio context restrictions; threading limits; memory pressure |
| 56 | `56_SISTER_INTEGRATION_RISKS.md` | ChatMemory, AIAvatarKit, AITuber version drift; breaking changes; coupling cost |
| 57 | `57_FAILURE_TAXONOMY.md` | Categorized failure modes across CDK + sister projects, ranked impact × likelihood |

---

## 60_synthesis/ (12 docs — Cartographer: 6, Scribe: 6)

| # | Slug | Owner | Scope |
|---|---|---|---|
| 60 | `60_TRIANGULATION.md` | Cartographer | SAP × Waifu × CDK comparative read; the three embodiment axes formalized; decision matrix |
| 61 | `61_ANDLIT_UNITY_TIER.md` | Cartographer | Andlit-unity as Unity-native local rendering tier; how it fits alongside Andlit-electron and Andlit-realtime |
| 62 | `62_MOBILE_AND_XR_TIER.md` | Cartographer | iOS/Android/VR/AR form-factor matrix; what Ember's tier ladder gains from CDK's reach |
| 63 | `63_MULTIMODAL_PIPELINE.md` | Cartographer | STT → LLM → TTS + animation + face tags + lip-sync + VAD: the orchestrated pipeline pattern |
| 64 | `64_FUNCTION_CALLING_FOR_EMBODIED.md` | Cartographer | Tools as voice-issued commands; consent-gated execution; comparison with SAP MCP |
| 65 | `65_MEMORY_INTEGRATION.md` | Cartographer | ChatMemory pattern for Hjarta; episodic + factual storage; tethered to Brunnr/Well |
| 66 | `66_JAPANESE_VOICE_INTEGRATION.md` | Scribe | The 10+ Japanese TTS providers; what Ember gains by adopting VOICEVOX or AivisSpeech; cultural surface |
| 67 | `67_DECISION_RECORDS.md` | Scribe | ADRs CDK-001..CDK-010 covering LLM abstraction, multi-TTS, tag protocol, etc. |
| 68 | `68_INVENTED_METHODS.md` | Scribe | Novel patterns NOT in CDK — cross-runtime persona portability, multimodal-pipeline-as-resource, animation-tag negotiation, etc. |
| 69 | `69_SLICE_PLAN_REVISIONS.md` | Scribe | Proposed slice plan revisions (propose-only) for Andlit-unity tier |
| 6A | `6A_INTEGRATION_ROADMAP.md` | Scribe | Six-codex braid: SAP × Hermes × Peer × Klóinn × Waifu × CDK; cross-codex pollination map |
| 6B | `6B_EMBER_WAVE_5_SLICE.md` | Scribe | Proposed Wave 5 slice plan based on CDK + triangulation findings |

---

## Agent Layer Assignments — final

| Agent | Role | Folders | Doc count |
|---|---|---|---|
| 1 | **Skald** | `00_vision/` | 5 |
| 2 | **Architect** | `10_domain/` (14) + Architect-owned `20_interface/` (5) | 19 |
| 3 | **Cartographer** | Cartographer-owned `60_synthesis/` (6) | 6 |
| 4 | **Forge-A** | `30_execution/` core (8) | 8 |
| 5 | **Forge-B** | `30_execution/` sister+platform (6) | 6 |
| 6 | **Auditor** | `50_verification/` (8) + Auditor-owned `20_interface/` (5) | 13 |
| 7 | **Scribe** | Scribe-owned `60_synthesis/` (6) + meta finalization (3) | 6 + 3 = 9 |

**Total dispatch:** 7 parallel agents → 63 content docs + 3 meta finalization.

**Push cadence:** orchestrator commits + pushes per layer after all agents return. Scribe writes INDEX + READING_ORDER + CROSS_AGENT_NOTES in a follow-up pass.

---

## Reading Order (preliminary — Scribe finalizes)

1. `meta/SHARED_CONTEXT`
2. `00_vision/00_OVERTURE` → `04_VISION_SYNTHESIS`
3. `10_domain/10_DOMAIN_MAP`
4. Domain doc of interest (`16_LLM_SERVICE_DOMAIN`, `15_SPEECH_SYNTHESIZER_DOMAIN`, `1A_MEMORY_DOMAIN`, etc.)
5. Matching interface + execution docs
6. `50_verification/57_FAILURE_TAXONOMY`
7. `60_synthesis/60_TRIANGULATION` — the synthesis spine
8. `60_synthesis/6A_INTEGRATION_ROADMAP` last

---

## Slug Glossary (cross-codex prefix)

- `[[hermes:<slug>]]` → `docs/hermes_codex/`
- `[[peer:<slug>]]` → `docs/peer_codex/`
- `[[sap:<slug>]]` → `docs/sap_codex/`
- `[[kloinn:<slug>]]` → `docs/kloinn/`
- `[[waifu:<slug>]]` → `docs/waifu_codex/`
- `[[chatdoll:<slug>]]` → this codex
- `[[ember:<slug>]]` → root or `docs/`

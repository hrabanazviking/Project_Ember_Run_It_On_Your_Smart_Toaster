---
codex_id: INDEX
title: The ChatdollKit Codex — Entry Point
role: Scribe
layer: Meta
status: written
cdk_revision: ChatdollKit v0.8.16 (Feb 14, 2026 release) — May 2026
cdk_source: /tmp/ChatdollKit
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr, Andlit-reserved, Rödd-reserved, Hugarsýn, Veizla, Andlit-unity-proposed, Rödd-proposed]
cross_refs:
  - meta/MANIFEST
  - meta/SHARED_CONTEXT
  - meta/STYLE_GUIDE
  - meta/READING_ORDER
  - meta/CROSS_AGENT_NOTES
  - 00_vision/00_OVERTURE
  - 60_synthesis/60_TRIANGULATION
  - 60_synthesis/6A_INTEGRATION_ROADMAP
  - 60_synthesis/6B_EMBER_WAVE_5_SLICE
---

# The ChatdollKit Codex

*Wave Five. The fifth sister. The third foot of the embodiment tripod. If you came to ask whether a small-and-tethered agent can borrow a Unity body without losing herself to a game engine, you are in the right room.*

---

## Overture

The ChatdollKit Codex is a structured corpus of **sixty-three content documents** (plus six meta documents), written by seven Mythic Engineering specialists mining a single source: **`uezo/ChatdollKit`** at v0.8.16 (1.2k stars, 117 forks, 1,157 commits, Apache-2.0, 18,221 C# LOC across 121 files plus JavaScript bridges plus four sister projects that orbit the kit). The corpus is the *third* in a three-codex embodiment triangulation; SAP (Wave 3) gave Ember **electron-local** embodiment; the Waifu kit (Wave 4) gave Ember **cloud-streaming** embodiment; ChatdollKit gives Ember the third foot — **Unity-native local rendering**. The triangulation is now closed, and the closing reveals patterns no single corpus could surface alone.

The work this Codex is *not*: a Unity tutorial, a paraphrase of ChatdollKit's README, a beauty-contest verdict on whether VRM beats Live2D beats LiveKit. The work this Codex *is*: a careful source-grounded reading of 18,221 lines of C# plus ~1,500 lines of FastAPI memory service plus ~350 lines of YouTube-bridge plus the AIAvatarKit streaming server, all read against Ember's True Names and Vows held side by side. Every claim cites `/tmp/ChatdollKit/<path>:<line>` or a sister-project equivalent with the appropriate prefix. The corpus's central contribution is to name the third position on the embodiment axis (Andlit-unity), to formalise the **Hjarta-Brunnr Rule** that ChatMemory's HTTP-boundary teaches, and to elevate the **Server-Held-Keys-Only Vow candidate** that three independent corpora now reject by structural convergence.

A contributor sixteen months from now will clone Ember, open this Codex, and ask: *was the choice to ship Unity-native embodiment (or not) made because we couldn't, or because we considered ChatdollKit's `AIAvatar.cs` 664-line monolith and the dedupe-lock cache and the Japanese voice ecosystem and chose against (or for) the engine commitment on principle?* The Codex answers. It says **what we saw, what we considered, what we proposed, what we refused, and why** — with file-and-line citations from a pinned `/tmp/ChatdollKit/` v0.8.16 clone so the next reader can verify.

---

## The Session-Limit Story (Wave-Close Mechanics)

Wave 5 is the first Ember codex to ship with an unusual git history: **ten layer-commit landings instead of the typical six**. The reason matters because it is a story about how Mythic Engineering survives infrastructure interruption.

The original 7-agent dispatch (Skald, Architect, Cartographer, Forge-A, Forge-B, Auditor, Scribe) ran in parallel from the same SHARED_CONTEXT / MANIFEST / STYLE_GUIDE briefing. Mid-wave, the Claude subscription session limit fired. Each agent had completed between 21 and 67 tool uses before the limit was reached. **Thirty-eight of the sixty-three content docs landed pre-limit.** Five partial-layer commits captured the work that had completed before the cutoff. After the reset, a follow-up 5-agent dispatch (Architect, Cartographer, Forge, Auditor, Scribe) completed the remaining 28 docs. Five additional layer-completion commits captured those. Total: ten layer-commits, all clean (no truncations, no Continuation Notes blocks needed, no merge conflicts at the layer boundaries because the original agents had all written to disjoint files).

This story is documented at `[[CROSS_AGENT_NOTES §1]]` and the practical lesson — *agent briefings must be self-sufficient so any follow-up agent can resume without orchestration state* — is named there as the **Clean-Resume Discipline**. The discipline holds whenever a wave's individual agents read only from disk-resident docs and never rely on in-session memory across runs.

When this index disagrees with [[MANIFEST]], the manifest wins. Cross-agent disagreements and the session-limit story are catalogued in [[CROSS_AGENT_NOTES]].

---

## How to Read This Codex

The full reading paths live in [[READING_ORDER]]. The quick-start for first-time readers: walk [[00_OVERTURE]] → [[01_CDK_ESSENCE]] → [[10_DOMAIN_MAP]] → [[60_TRIANGULATION]] → [[6B_EMBER_WAVE_5_SLICE]]. About three hours. You will leave knowing what ChatdollKit is, what the three-corpus triangulation completed, what Ember refuses (client-held LLM keys; `IPAddress.Any` socket binding; a single tag-extraction regex masquerading as three), and what Ember proposes (Andlit-unity reservation; the Hjarta-Brunnr Rule from ChatMemory's HTTP-boundary; the Server-Held-Keys-Only Vow candidate).

If you have ninety minutes and need to be smart about this by morning, walk Path 7 — *Volmarr at 2am*. Four docs. Eyes-glaze-rule applies.

---

## The Vision Layer (Skald — 5 docs)

| Slug | Title | Role | Words | One-line scope | Key finding |
|---|---|---|---|---|---|
| [[00_OVERTURE]] | Overture — The Fifth Reading | Skald | 4,685 | Why mine CDK after SAP + Waifu; the embodiment triangulation closing; the Japanese voice gap; the Apache-2.0 give and ask | The Fifth Reading is the *closing of the triangulation*: SAP-electron + Waifu-cloud + CDK-Unity span the road, and Wave 5's job is to name the third position so the lattice holds |
| [[01_CDK_ESSENCE]] | ChatdollKit Essence — The Doll Who Speaks | Skald | 3,853 | What CDK is at the level of intent: doll-as-companion in Unity's lineage of game-engine character animation | The four-state `AvatarMode` (Disabled/Sleep/Idle/Conversation) is the right shape for Veizla lifecycle (Sealed/Idle/Engaged/Closing); the *waiting-state discipline* is what CDK teaches Ember about embodied patience |
| [[02_UNITY_AS_RUNTIME]] | Unity as Runtime — What the Engine Gives, What the Engine Asks | Skald | 4,593 | Unity as Ember's potential third embodiment runtime; what it gives (cross-platform reach, mature animation, asmdef boundary); what it asks (engine commitment, learning curve, ~30MB binary floor) | Adopting Unity as Ember's *foundation runtime* violates Smallness; reserving the Andlit-unity *sub-name* without shipping code is the cost-free preparation Ember can afford |
| [[03_ANTI_CDK]] | Anti-CDK — The Refusals Ember Owes to Apache-2.0 Honesty | Skald | 3,921 | The refusal table; every refusal carries a CDK line citation; the Apache-2.0 attribution discipline | Apache-2.0 attribution is *cheap to pay and load-bearing to maintain*; pay it cheerfully; the Refusal-Citation Discipline from `[[sap:03_ANTI_SAP]]` carries forward with attribution as the new ask |
| [[04_VISION_SYNTHESIS]] | Vision Synthesis — Post-CDK Ember and the Closing of the Triangulation | Skald | 5,445 | Ember's identity revised post-CDK; how Unity-native fits Andlit + Rödd alongside SAP-electron + Waifu-cloud; Wave-5 vow sharpenings | **The Three-Axis Embodiment Reservation Pattern**: Andlit and Rödd each get local/realtime/unity sub-names; the operator declares the axis at first-run rite; the local ladder, the cloud axis, and the engine axis are independent reservations |

---

## The Domain Layer (Architect — 14 docs)

| Slug | Title | Role | Words | One-line scope | Key finding |
|---|---|---|---|---|---|
| [[10_DOMAIN_MAP]] | The Domain Map of ChatdollKit — Eight Subsystems, One Avatar, No Server | Architect | 4,684 | CDK's macro shape: AIAvatar top-level + 8 subsystem folders + Extension/ boundary discipline | **No server.** Unlike SAP's 11,652-line `server.py`, CDK has no monolithic backbone — *because Unity is the server*. The MonoBehaviour update loop replaces the HTTP route table |
| [[11_AIAVATAR_DOMAIN]] | AIAvatar Domain — The Coordinator That Knows Everyone's Phone Number | Architect | 3,166 | `AIAvatar.cs` (664 LOC) as CDK's lone monolith; ten responsibilities; the only SAP-shape in the kit | **AIAvatar.cs is CDK's `handleToogleCharacter`-equivalent** — the one place where boundaries break. Ten responsibilities; mode state + dialog dispatch + tool gating + memory hook + lifecycle wake-from-sleep. Adopt the four-state mode; refuse the ten-responsibility coalescing |
| [[12_MODEL_CONTROLLER_DOMAIN]] | Model Controller Domain — The Animation Queue, the Face Queue, and the Voice Coupler | Architect | 3,589 | `Scripts/Model/` — animation, expression, VRM integration, uLipSync coupling | `[face:X]` tag *silently doubles as TTS style at `ModelController.cs:256`* — undocumented; the quiet "voice doesn't sound right" bug. Surface as one of CDK's two undocumented behaviours |
| [[13_DIALOG_PROCESSOR_DOMAIN]] | Dialog Processor Domain — The Seven-Status Pipeline and the Priority Queue | Architect | 3,485 | `Scripts/Dialog/` — state machine, intent extraction, priority queue, wakeword | The seven-status pipeline (idle/listening/dialog/error/etc.) is cleaner than SAP's implicit state; adopt the *typed dialog status enum* as the Ember-side pattern |
| [[14_SPEECH_LISTENER_DOMAIN]] | Speech Listener Domain — Six STT Providers, One Recording Session, One VAD Slot | Architect | 3,192 | `Scripts/SpeechListener/` — STT pipeline, multi-VAD support, Silero ONNX | Six providers conform to an 18-line contract; the *contract is the abstraction*. SAP's `sherpa_asr` and Waifu's browser-STT both fit the same shape if the abstraction is small enough |
| [[15_SPEECH_SYNTHESIZER_DOMAIN]] | Speech Synthesizer Domain — Eleven Voices, One Cache, One Dedupe-Lock | Architect | 3,437 | `Scripts/SpeechSynthesizer/` — TTS, parallel/sequential prefetch, dedupe cache | **The dedupe-lock cache in `SpeechSynthesizerBase` (28-102)** is the single most adoptable algorithm in CDK — <30 lines, three-level lookup (cache hit / in-flight wait / new fetch). Lift verbatim |
| [[16_LLM_SERVICE_DOMAIN]] | LLM Service Domain — One Interface, Five Vendors, Five Wire Formats | Architect | 3,779 | `Scripts/LLM/` — ILLMService over 6+ providers (ChatGPT/Claude/Gemini/Dify/AIAvatarKit/Grok) | The `ILLMService` interface is 58 lines and provider-neutral (not OpenAI-pretending) — SAP's Refusal-9 (`[[sap:55_API_SIMULATION_TRAPS]]`) does not apply; CDK's design is the *right* answer to the same problem |
| [[17_MICROPHONE_MANAGER_DOMAIN]] | Microphone Manager Domain — One Buffer, Four Mic Backends, One Reverse Iteration | Architect | 2,942 | `Scripts/IO/` — audio capture, native mic plugins, noise gate | Four mic backends (Unity/Web/iOS/Android) behind one IMicrophoneManager — the *backend-per-platform* pattern that mobile and XR require |
| [[18_NETWORK_DOMAIN]] | Network Domain — Two Inbound Surfaces, One Outbound Helper, Zero Authentication | Architect | 3,018 | `Scripts/Network/` — SocketServer + JavaScriptMessageHandler dual remote-control | **`IPAddress.Any` socket bind with zero auth** is the largest single security debt in CDK. Apache-2.0 means Ember adopting must fix the default at adoption |
| [[19_TOOL_DOMAIN]] | Tool Domain — One Interface, One Base, Five Function-Call Wire Formats | Architect | 2,798 | Tool/ToolBase function-calling for AI agents | One ITool + ToolBase + five wire-format adapters; the *adapter cost is the abstraction's price*; pay it once for cross-provider portability |
| [[1A_MEMORY_DOMAIN]] | Memory Domain — Two Stores Outside, One Integrator Inside, One Tool to Reach Them | Architect | 2,833 | ChatMemoryIntegrator + ChatMemory sister project; episodic + factual stores | **108 LOC of HTTP client** in `ChatMemoryIntegrator` against ~1,500 LOC of FastAPI memory service — the entire memory subsystem is one repo away. Boldest CDK architectural decision; directly portable to Ember's Hjarta/Brunnr split |
| [[1B_ANIMATION_DOMAIN]] | Animation Domain — Four Tags, One Regex, Two Brokers, Three Queues | Architect | 3,252 | `[anim:Name]` + `[face:Expression]` tags + ModelRequestBroker + DialogPriorityManager | **Two tag-extraction regexes in three places** stratified by timing — `LLMServiceBase.ExtractTags`, `LLMContentProcessor`, `ModelController.ToAnimatedVoiceRequest`. Worth a synthesis pattern doc |
| [[1C_UNITY_LIFECYCLE_DOMAIN]] | Unity Lifecycle Domain — One MonoBehaviour, Five Callbacks, One Asmdef, Five JSLibs | Architect | 3,436 | Unity-specific: asmdef, MonoBehaviour, ScriptableObject, prefab integration | The asmdef boundary pattern (three external references, autoReferenced=true) is the engine-given module discipline. Adoptable as a *pattern* without adopting Unity |
| [[1D_MULTI_PLATFORM_DOMAIN]] | Multi-Platform Domain — Eight Targets, Three Tiers of Native Cost | Architect | 3,389 | Windows/Mac/Linux/iOS/Android/VR/AR/WebGL build targets; platform-specific deltas | **Three-tier native-cost model** — Tier 0 pure C# / Tier 1 #if-conditional / Tier 2 native plugin; ~75/20/5 distribution; audio domain is the entire Tier 2 |

---

## The Interface Layer (Architect 5 + Auditor 5 — 10 docs)

| Slug | Title | Role | Words | One-line scope | Key finding |
|---|---|---|---|---|---|
| [[20_LLM_SERVICE_INTERFACE]] | LLM Service Interface — Eight Members, Five Wire Formats, Five Adapter Costs | Architect | 3,239 | `ILLMService` contract; how 6+ providers conform; function-call format divergence | Eight members in the interface; the *contract is what makes the multi-provider zoo tractable*. Recommend Ember's typed Vegfarendr-for-models adopt the same shape |
| [[21_TTS_INTERFACE_WESTERN]] | TTS Interface (Western) — Four Vendors and the One That Is Not There | Auditor | 3,163 | TTS providers Google/Azure/OpenAI/Watson contract, latency, format | **Watson TTS doesn't exist** — README claim only; no implementation. The kit's documentation is structurally optimistic; verify before depending |
| [[22_TTS_INTERFACE_JAPANESE]] | TTS Interface (Japanese) — VOICEVOX, AivisSpeech, VOICEROID, Style-Bert-VITS2, NijiVoice, Kotodama | Auditor | 4,942 | The deep Japanese stack (8 of 11 TTS providers) | **VOICEVOX is structurally unique** — 30-80ms latency floor, offline CPU, zero-credential, 50+ voices, free-with-attribution. Adopt-priority for Ember Rödd-unity desktop default. Load-bearing teaching |
| [[23_STT_INTERFACE]] | STT Interface — Five Providers Conforming To Eighteen Lines, And The Streaming Variant Beside Them | Auditor | 3,960 | STT providers Google/Azure/OpenAI/Silero/AIAvatarKit streaming | Five providers conform to an 18-line interface; the streaming variant lives *beside* the contract, not extending it — a small-but-clean separation |
| [[24_VAD_INTERFACE]] | VAD Interface — One Function Signature, One ONNX Model, Two Substrate Paths | Architect | 2,823 | Silero ML-based VAD; the `SileroVADProcessor`; ONNX runtime in Unity | One function signature serves CPU-Silero and the native-streaming path equally; the *interface is the bridge between substrates* |
| [[25_ANIMATION_TAG_PROTOCOL]] | Animation Tag Protocol — Four Tags, One Regex, Two Parse Points | Architect | 2,622 | `[anim:]` + `[face:]` tag protocol; how LLM output drives avatar | Four tags, one regex, two parse points — the protocol is structurally small; the *complexity is in the dispatch table*, not the parse |
| [[26_TOOL_FUNCTION_CALL_INTERFACE]] | Tool Function-Call Interface — Five Wire Formats, Three Tool-Result Roles, One Spec | Architect | 2,796 | `ITool` + `ToolBase`; per-provider function-call format adapters | Three tool-result roles (tool / function / model-emitted) across five wire formats; the adapter discipline is what makes the abstraction hold |
| [[27_SOCKET_PROTOCOL]] | Socket Protocol — A TCP Listener On Every Interface | Auditor | 3,569 | SocketServer remote control protocol; auth posture | **`SocketServer + AITuberMessageHandler` allows API-key + system-prompt + model-URL reassignment over unauth TCP** (`AITuberMessageHandler.cs:217-272`) — single most consequential lines in CDK |
| [[28_JS_BRIDGE_INTERFACE]] | JS Bridge Interface — A Window-Global Any Script Can Call, Plus Six LLM Bridges | Auditor | 3,460 | JavaScriptMessageHandler WebGL ↔ JS bridge; message-origin verification | **`window.SendMessageToChatdollKit` window-global with no origin check** — XSS / extension / iframe-ancestor / third-party-script trust boundary failures. **`anthropic-dangerous-direct-browser-access: true`** set in Claude WebGL JSLIB — the header name is the documentation |
| [[29_VRM_INTERFACE]] | VRM Interface — Three Interfaces, Four Implementations, One Runtime Loader | Architect | 2,800 | UniVRM integration; bone/expression mapping; comparison with SAP VRM use | **`IFaceExpressionProxy` has two implementations** (VRM + VRChat); Live2D would be three. Interface-segregation at the embodiment boundary is *proven by existence*, not hypothetical |

---

## The Execution Layer (Forge-A core 8 + Forge-B sister+platform 6 — 14 docs)

### Forge-A — Core (8 docs)

| Slug | Title | Role | Words | One-line scope | Key finding |
|---|---|---|---|---|---|
| [[30_UNITY_BOOTSTRAP]] | Unity Bootstrap — One MonoBehaviour to Wake Them All | Forge-A | 2,560 | AIAvatar instantiation; MonoBehaviour lifecycle; prefab inflation | One MonoBehaviour wakes the entire kit; the *Awake() ordering* is the only orchestration. Compare SAP's `REAL_PORT_FOUND` stdout-handshake — Unity's engine-given lifecycle is structurally cleaner |
| [[31_AIAVATAR_MAIN_LOOP]] | AIAvatar Main Loop — The Outer State Machine and the Inner One | Forge-A | 2,479 | Dialog state machine driven by AIAvatar; per-frame update; mode transitions | Outer state machine = mode (`AvatarMode`); inner = dialog status. Two state machines, one update loop. The *separation of concerns is real* but compressed into one file |
| [[32_STT_LOOP]] | STT Loop — Mic to VAD to ONNX to Text | Forge-A | 2,557 | Mic capture → VAD → STT provider → text emission | Mic→VAD→STT as four typed handoffs; the *typed handoff is the testability surface* |
| [[33_TTS_PREFETCH]] | TTS Prefetch — Two Queues, One Cache, and a Hash Key | Forge-A | 2,340 | Parallel vs sequential prefetch; queue management; barge-in interruption | Two queues + one cache + hash key on `(text, voice, style)` = the prefetch contract. The dedupe-lock cache (named in `[[15_SPEECH_SYNTHESIZER_DOMAIN]]`) lives here in runtime |
| [[34_ANIMATION_PIPELINE]] | Animation Pipeline — Tag Regex, Animator Parameters, Idle Roulette | Forge-A | 2,742 | `[anim:]` tag extraction → state-machine transition; additive/override blending | Idle roulette (rotating idle animations) is a small touch that makes the avatar *feel alive*; lift the pattern for any Andlit-unity ship |
| [[35_LIP_SYNC]] | Lip Sync — uLipSync, Five Vowels, and the BlendShape Hunt | Forge-A | 2,230 | uLipSync integration; vowel detection; mouth-shape mapping | Five vowels into BlendShape keyboard; uLipSync is the small library that earns its keep. Compare SAP's `vts_manager` FFT-vowel approach |
| [[36_FUNCTION_CALL_EXEC]] | Function Call Execution — Three Providers, Three Wire Formats, One ITool | Forge-A | 2,718 | LLM emits function call → ITool resolution → execution → response feeding | **Silent fall-through on tool-name mismatch** — avatar freezes mid-utterance with no error event. Cartographer proposes `ToolNotFoundEvent` self-correction loop |
| [[37_BARGE_IN_INTERRUPT]] | Barge-In — Cancel-and-Replace at the TTS/Dialog Seam | Forge-A | 3,763 | User interrupts mid-TTS; cancel-and-replace pattern; merge-window logic | **Barge-in is two structurally different algorithms**: Path A (duration-based, fires after 1.5s) and Path B (partial-transcript-length-based, fires after 2 chars ~300ms). The **1.2s gap is what makes barge-in conversational** |

### Forge-B — Sister + Platform (6 docs)

| Slug | Title | Role | Words | One-line scope | Key finding |
|---|---|---|---|---|---|
| [[38_CHATMEMORY_INTEGRATION]] | ChatMemory Integration — A FastAPI Companion to the Doll | Forge-B | 2,751 | ChatMemory sister project; FastAPI server; episodic vs factual stores; integrator pattern | **15:1 line-count ratio** between ChatMemory's Unity client (96 lines) and FastAPI service (1,451 lines) is the *design statement*. The boundary is the lesson — elevated to the **Hjarta-Brunnr Rule** in `[[65_MEMORY_INTEGRATION]]` |
| [[39_AIAVATARKIT_STREAMING]] | AIAvatarKit Streaming — The S2S Pipeline Behind CDK's Streaming Mode | Forge-B | 2,947 | uezo/aiavatarkit sister; S2S streaming pipeline; STT server architecture | **The streaming WebSocket protocol has no version field** — custom JSON between two repos with no shared schema file. Highest sister-coupling fragility |
| [[3A_AITUBER_CONTROLLER]] | AITuber Controller — A 346-Line Bridge Between YouTube Chat and the Doll | Forge-B | 3,256 | uezo/chatdollkit-aituber sister; VTuber streaming; comparison with SAP livestream | A 346-line bridge spans YouTube chat → Doll; the *small-bridge pattern* is what Boðr (`[[sap:14_MESSAGING_DOMAIN]]`) wants every adapter to be |
| [[3B_WEBGL_BUILD]] | WebGL Build — Emscripten, AudioWorklet, and the Browser's Permission to Make Noise | Forge-B | 3,312 | WebGL build pipeline; Emscripten; audio context; memory constraints; 5-10 min build time | Build time is the operator cost; AudioWorklet is the *only* permission-stable audio path; the kit teaches the price of browser embodiment |
| [[3C_MOBILE_BUILD]] | Mobile Build — iOS, Android, Native Mic Plugins, and the App Store Reality | Forge-B | 3,485 | iOS + Android Unity builds; permissions; binary size; on-device LLM viability | App Store reality is the *binding constraint*; on-device LLM is *not yet* viable at app-store size; the kit is honest about the gap |
| [[3D_XR_BUILD]] | XR Build — VR, AR, and the Six Sensors Nobody Mentions | Forge-B | 4,756 | VR + AR target considerations; sensor data privacy; performance tier | **CDK has zero XR-specific code** despite README claim; shipping to Quest requires 2-4 person-weeks of operator work. CDK *forbids SRP* (UniVRM incompatibility) → **Vision Pro hard-blocked** for VRM avatars until UniVRM URP support. **XR's six sensors are six distinct privacy surfaces** (gaze, hands, spatial map, head pose, mic, camera). Apple restricts raw gaze to events-only — reference design Ember should follow |

---

## The Verification Layer (Auditor — 8 docs)

| Slug | Title | Role | Words | One-line scope | Key finding |
|---|---|---|---|---|---|
| [[50_DEPENDENCY_HEALTH]] | Dependency Health — Burst, UniTask, uLipSync, UniVRM, Newtonsoft, ONNX | Auditor | 2,216 | Brittleness map; Unity version coupling | UniVRM lacks URP support → SRP forbidden → Vision Pro hard-blocked. UniTask + Burst are stable; uLipSync earned its keep; Newtonsoft.JSON is the entire C# JSON layer |
| [[51_SECURITY_REVIEW]] | Security Review — Keys In The Build, A Port Open To Anyone, A JS Bridge Without Origin | Auditor | 3,087 | STRIDE pass: LLM keys in client; socket auth; JS bridge XSS; mobile permissions | **Credential leak (11 findings) and no-auth control plane (6 findings) dominate.** `Debug.Log` plaintext argument leak at `ChatGPTService.cs:360` ships passwords/keys to `Player.log` on disk. Three-corpus convergence: client-side LLM API keys is now Vow-candidate territory |
| [[52_PERFORMANCE_BUDGETS]] | Performance Budgets — The Frame, The Turn, The Phone, The Headset | Auditor | 1,747 | Render budget; STT/TTS latency; lip-sync CPU; per-platform tier | Four budgets across four tiers; the *budget is the tier definition*; XR has the tightest frame budget (11ms = 90fps); desktop has the loosest (33ms = 30fps) |
| [[53_MULTI_LLM_CONSISTENCY]] | Multi-LLM Consistency — Four Function-Call Schemas, One Façade, Many Leaks | Auditor | 2,213 | Function-call format divergence; failure handling; provider-fallback discipline | **Gemini has no tool-call ID** (`GeminiService.cs:437`) — structurally blocks parallel tool calls on Gemini; quiet ceiling on cross-provider portability |
| [[54_MULTI_TTS_QUALITY]] | Multi-TTS Quality — Latency, Lip-Sync Drift, And The Cost Of Many Voices | Auditor | 2,334 | Latency vs voice character; lip-sync drift; provider-specific gotchas | **VOICEVOX speaker-ID drift between versions** silently misroutes characters — operators should version-pin. The cost of many voices is the operator-discipline tax |
| [[55_WEBGL_GOTCHAS]] | WebGL Gotchas — Emscripten, Audio Context, Single-Thread, Memory | Auditor | 2,067 | Emscripten quirks; audio context restrictions; threading limits; memory pressure | Single-threaded by structure; AudioContext requires user gesture to start; memory is bounded by browser tab — three constraints that shape every WebGL ship |
| [[56_SISTER_INTEGRATION_RISKS]] | Sister Integration Risks — ChatMemory, AIAvatarKit, AITuber Controller, And The Single-Maintainer Coupling | Auditor | 4,006 | Sister-project version drift; breaking changes; coupling cost | **uezo is the single maintainer** for all five sister repos — bus-factor + release-cadence risk. Coupling is *structural*, not contractual |
| [[57_FAILURE_TAXONOMY]] | Failure Taxonomy — Forty-Two Ranked Failure Modes Across CDK And Its Sisters | Auditor | 3,606 | Categorized failure modes ranked impact × likelihood | **42 ranked failure modes**; credential leak (11 findings) and no-auth control plane (6 findings) dominate. Risk-Register-as-Code pattern from `[[sap:57_FAILURE_TAXONOMY]]` extends with CDK-specific entries |

---

## The Synthesis Layer (Cartographer 6 + Scribe 6 — 12 docs)

### Cartographer's Six

| Slug | Title | Role | Words | One-line scope | Key finding |
|---|---|---|---|---|---|
| [[60_TRIANGULATION]] | Triangulation — The Three Embodiment Axes Formalised | Cartographer | 4,840 | SAP × Waifu × CDK comparative read; three-corpus decision matrix; tier vocabulary chosen | **CDK is right when Ember needs to be where SAP and Waifu cannot reach** — mobile-native, XR, embedded-WebGL, App-Store-deployed, deep Japanese voice. The triangulation is now closed; the three-corpus decision matrix is the canonical decision-aid |
| [[61_ANDLIT_UNITY_TIER]] | Andlit-Unity — Unity-Native Local Rendering as a Third Embodiment Tier | Cartographer | 4,113 | Andlit-unity as Unity-native local rendering tier; how it fits alongside Andlit-electron and Andlit-realtime | The Three-Axis Embodiment Reservation Pattern formalised: Andlit-electron / Andlit-realtime / Andlit-unity are *siblings*, not a hierarchy. Operator-declared at first-run |
| [[62_MOBILE_AND_XR_TIER]] | Mobile and XR — The Form-Factor Matrix Ember Was Missing | Cartographer | 4,225 | iOS/Android/VR/AR form-factor matrix; what Ember's tier ladder gains from CDK's reach | Mobile + XR adds two more form-factor axes; the tier ladder becomes 3D (rung × cloud-axis × form-factor); the *form-factor axis is the one Wave 4 deferred* |
| [[63_MULTIMODAL_PIPELINE]] | The Multimodal Pipeline — STT → LLM → TTS with Animation, Face, Lip-sync, and VAD as One Orchestrated Surface | Cartographer | 4,215 | STT → LLM → TTS + animation + face tags + lip-sync + VAD: the orchestrated pipeline | The orchestrated pipeline is *the* synthesis pattern; CDK orchestrates implicitly through AIAvatar; Ember should orchestrate *explicitly* through a typed Munnr-pipeline contract |
| [[64_FUNCTION_CALLING_FOR_EMBODIED]] | Function Calling for the Embodied Agent — Six Providers, Three Wire Formats | Cartographer | 4,914 | Tools as voice-issued commands; consent-gated execution; comparison with SAP MCP | **Recursive `useFunctions=false` loop-breaker** is elegant per-turn but leaves **cross-turn unbounded tool chains** — proposes `max_tool_calls_per_user_input` turn budget |
| [[65_MEMORY_INTEGRATION]] | Memory Integration — ChatMemory as the Hjarta-and-Brunnr Boundary Lesson | Cartographer | 4,700 | ChatMemory pattern for Hjarta; episodic + factual storage; tethered to Brunnr/Well | **The Hjarta-Brunnr Rule**: the 15:1 line-count ratio is the design statement. Hjarta owns the small client; Brunnr owns the long-running service. The boundary is the lesson. **Summary-on-session-switch trigger generalises to lazy-at-boundary** (diary consolidation, knowledge promotion, identity merging) |

### Scribe's Six

| Slug | Title | Role | Words | One-line scope | Key finding |
|---|---|---|---|---|---|
| [[66_JAPANESE_VOICE_INTEGRATION]] | Japanese Voice Integration — What the Under-Served Stack Teaches Ember | Scribe | 3,495 | The 8 Japanese TTS providers; VOICEVOX/AivisCloud/StyleBertVits2/Voiceroid/Kotodama/NijiVoice; cultural surface | **The Japanese voice ecosystem is unique teaching** Western codexes don't name. VOICEVOX (30-80ms, offline, zero-credential) is the adopt-priority for Rödd-unity. Style-Bert-VITS2 is AGPL-3.0 engine + Apache-2.0 CDK client = three-license stack |
| [[67_DECISION_RECORDS]] | Decision Records — ADR-Proposed for CDK-Driven Adoption Decisions | Scribe | 6,189 | ADRs CDK-001..CDK-NNN covering LLM abstraction, multi-TTS, tag protocol, etc. | ADR-CDK series catalogued; clusters naturally into Slice 3/4/5/6 candidates; each is Accept / Defer / Reject pending keeper review |
| [[68_INVENTED_METHODS]] | Invented Methods — Novel Patterns Visible Only Because of CDK | Scribe | 6,087 | Novel patterns NOT in CDK — cross-runtime persona portability, multimodal-pipeline-as-resource, animation-tag negotiation, etc. | Whole doc is **Invent**. Cartographer's six synthesis docs are the *major* inventions of Wave 5; this doc catalogues the *minor and adjacent* inventions that round out the surface |
| [[69_SLICE_PLAN_REVISIONS]] | Slice Plan Revisions — CDK-Derived Proposals (PROPOSE ONLY) | Scribe | 5,669 | Proposed slice plan revisions for Andlit-unity tier | **Slice-3 has grown to ~2,780 LOC** across three codex contributions (Hermes ~1,400 + SAP ~650 + CDK ~730); sub-slicing into 3a/3b/3c recommended. *All proposals are proposals; the slice plan does not change here.* |
| [[6A_INTEGRATION_ROADMAP]] | Integration Roadmap — The Six-Codex Braid (Hermes × Peer × SAP × Klóinn × Waifu × CDK) | Scribe | 5,055 | Cross-codex pollination map across six codexes | The braided-slice approach extends from Wave 3's five-codex frame to six; pollination-accounting is itself a Wave-close discipline worth formalising. **"Klóinn-pending" markers** as explicit gaps — preferred over padding with speculation |
| [[6B_EMBER_WAVE_5_SLICE]] | Ember Wave 5 Slice — Proposed Concrete Roadmap (PROPOSE ONLY) | Scribe | 4,891 | Proposed Wave 5 slice plan based on CDK + triangulation findings | Wave-5 slice proposed as Andlit-unity reservation + dedupe-lock cache adoption + Hjarta-Brunnr boundary formalised + Server-Held-Keys-Only ratification; the **Validation-Slice Pattern** invented: a slice that validates a prior slice's abstraction by adding a second concrete implementation |

---

## The Meta Layer (Scribe — 6 docs)

| Slug | Title | Role | Status | Scope |
|---|---|---|---|---|
| [[MANIFEST]] | Authoritative doc list (69 entries) | Scribe | Written | The doc-list of record. When this index disagrees, the manifest wins |
| [[SHARED_CONTEXT]] | Briefing every Mythic Engineering agent reads before authoring | Scribe | Written | What CDK is; what Ember is; how to cite; the Adopt/Adapt/Avoid/Invent closer convention; Apache-2.0 attribution discipline; threat awareness |
| [[STYLE_GUIDE]] | Voice, tone, length, citation rules, closer format | Scribe | Written | The voice-and-rules contract; 1,500–4,000 word target; binding |
| [[INDEX]] | This file | Scribe | Written | The entry point |
| [[READING_ORDER]] | Suggested traversal orders by reader need | Scribe | Written | Seven paths (first-time / three-corpus-triangulation / embodiment / Japanese-voice / security / synthesis-only / Volmarr-at-2am) |
| [[CROSS_AGENT_NOTES]] | Synthesis of cross-agent findings | Scribe | Written | The session-limit story, the Server-Held-Keys-Only Vow candidate, load-bearing inventions, convergent findings, ratification-priority recommendations |

---

## The True Names — One-Line CDK Lessons

The Wave-3 + Wave-4 True Name vocabulary is the canonical reference (`[[sap:60_TRUE_NAME_REASSIGNMENT]]`, `[[waifu:INDEX]]`); the ChatdollKit Codex extends the Andlit and Rödd reserved names with a third sub-name (Andlit-unity, Rödd-proposed) rather than adding new True Names. The six core True Names take one-line CDK-side teachings:

- **Funi** — *the spark, entrypoint / orchestrator* — CDK demonstrates the **MonoBehaviour-as-entrypoint** discipline: one `Awake()` lifecycle wakes the entire kit; the *engine-given lifecycle* is the orchestration. Funi's Python equivalent is `pyproject.toml` + `__main__.py` + lazy-import discipline carried from SAP. See [[30_UNITY_BOOTSTRAP]], [[10_DOMAIN_MAP]].
- **Strengr** — *the thread, reasoning loop / agent kernel* — CDK proves the `ILLMService` 58-line interface is enough to abstract 6+ LLM providers without OpenAI-pretending. Strengr's reasoning loop should consume a similar provider-neutral typed Protocol, not pretend any vendor's wire format is canonical. See [[16_LLM_SERVICE_DOMAIN]], [[20_LLM_SERVICE_INTERFACE]].
- **Brunnr** — *the well, external knowledge* — ChatMemory's FastAPI service (1,451 LOC) is what Brunnr looks like as a *long-running, repo-isolated* service. The Hjarta-Brunnr Rule formalises this: the long-running storage service is Brunnr; the in-process client is Hjarta. See [[65_MEMORY_INTEGRATION]], [[38_CHATMEMORY_INTEGRATION]].
- **Smiðja** — *the forge, tool execution / sandbox* — CDK's `ITool` + `ToolBase` + per-provider adapters is the *adapter cost as abstraction price*. The TrustClass enum from `[[sap:53_SECURITY_REVIEW]]` gains a Unity-equivalent: tool-result must travel back through the same adapter shape; the silent-fall-through-on-name-mismatch bug ([[36_FUNCTION_CALL_EXEC]]) is exactly the failure TrustClass refuses. See [[19_TOOL_DOMAIN]], [[64_FUNCTION_CALLING_FOR_EMBODIED]].
- **Hjarta** — *the heart, affect / intent / memory bias* — Hjarta now owns the **memory client** in the Hjarta-Brunnr split; a 108-LOC HTTP client is enough. The summary-on-session-switch trigger is the *lazy-at-boundary* pattern that generalises to diary consolidation, knowledge promotion, identity merging. See [[1A_MEMORY_DOMAIN]], [[65_MEMORY_INTEGRATION]].
- **Munnr** — *the mouth, output / surface / expression* — Munnr is plural across the three embodiment axes: text (SAP-text), voice (Rödd-local + Rödd-realtime + Rödd-unity), avatar (Andlit-electron + Andlit-realtime + Andlit-unity). The orchestrated multimodal pipeline ([[63_MULTIMODAL_PIPELINE]]) is what Munnr's pipeline contract should look like. See [[15_SPEECH_SYNTHESIZER_DOMAIN]], [[63_MULTIMODAL_PIPELINE]].

### Reserved name-slots (Wave-3 + Wave-4 + Wave-5 reservations)

- **Andlit** — *the face* — reserved as a paired True Name with Rödd per the Name Reservation pattern. Wave 5 adds the *third* sub-name reservation:
  - **Andlit-local** — SAP-style local render (VRM, Live2D, abstract glyph) on the operator's GPU.
  - **Andlit-realtime** — kit-style cloud render via LiveKit substrate + pluggable `CloudAvatarProvider` adapter.
  - **Andlit-unity** *(Wave 5, proposed)* — Unity-native local rendering with VRM + uLipSync + animation tags + face tags + asmdef-boundary discipline. Sibling to the other two, not child. See [[61_ANDLIT_UNITY_TIER]], [[02_UNITY_AS_RUNTIME]].
- **Rödd** — *the voice* — paired with Andlit. Wave 5 adds:
  - **Rödd-local** — local TTS/ASR (MOSS-TTS-Nano, sherpa-onnx) from SAP.
  - **Rödd-realtime** — bundled with Andlit-realtime in vendor-coupled architectures.
  - **Rödd-unity** *(Wave 5, proposed)* — Unity-substrate TTS adapters with the Japanese voice ecosystem as the default catalogue (VOICEVOX as Rödd-unity desktop default per [[66_JAPANESE_VOICE_INTEGRATION]]).
- **Hugarsýn** — *mind-sight* — adopted as Sixth-Plus True Name per Wave 3. Wave 5 adds the **form-factor axis** to the tier projection: every Hugarsýn query now returns `rung`, `cloud_axis`, *and* `form_factor` (desktop / mobile / XR / WebGL). See [[62_MOBILE_AND_XR_TIER]].
- **Veizla** — *the gathering, the session* — promoted from metaphor per Wave 3. Wave 5 adds the four-state mode discipline from CDK's `AvatarMode` (Sealed / Idle / Engaged / Closing) as the Veizla lifecycle vocabulary.

### Inventions named but not promoted to True Name

- **The Hjarta-Brunnr Rule** — the boundary is the lesson; 15:1 line-count ratio is design intent.
- **The Validation-Slice Pattern** — a slice that validates a prior abstraction by adding a second concrete implementation.
- **The Three-Axis Embodiment Reservation Pattern** — Andlit and Rödd each have local / realtime / unity sub-names; operator-declared.
- **The Two-LLM Deployment Pattern** — cheap local model for memory ops + SOTA model for dialog; emerges from CDK's memory architecture.
- **The Lazy-at-Boundary Pattern** — summary-on-session-switch generalised; diary consolidation, knowledge promotion, identity merging all fit.
- **The Protocol-Before-Client Split** — Unity client can be community contribution; Ember's in-tree commitment is ~600 LOC of WebSocket spec + reference server.
- **The Pollination Accounting Discipline** — each Wave close updates the cross-codex pollination map; the practice protects against silent inheritance.

---

## The Vows in Play

Wave 5 proposes **one new Vow candidate** (Server-Held-Keys-Only — elevated from three-corpus convergence) and one *standing rule* (Triangulation-Before-Major-Decision — procedural discipline). The Wave-3 + Wave-4 lattice otherwise holds. The table below names which Vows engage which CDK-codex docs most directly.

| Vow | Wave-5 sharpening / engagement | CDK-Codex docs engaging it most directly |
|---|---|---|
| **Smallness** | Unity foundation refused; engine commitment too large for Ember core | [[02_UNITY_AS_RUNTIME]], [[10_DOMAIN_MAP]], [[1D_MULTI_PLATFORM_DOMAIN]], [[6B_EMBER_WAVE_5_SLICE]] |
| **Tethered Grounding** | ChatMemory as Brunnr's external-cord shape; Hjarta-Brunnr Rule | [[65_MEMORY_INTEGRATION]], [[1A_MEMORY_DOMAIN]] |
| **Graceful Offline** | Sister-project version drift; single-maintainer risk; fallback to text | [[56_SISTER_INTEGRATION_RISKS]], [[57_FAILURE_TAXONOMY]] |
| **Honest Memory** | LLM-as-affect-author refused (Wave 3); applies to tool-call audit | [[64_FUNCTION_CALLING_FOR_EMBODIED]], [[36_FUNCTION_CALL_EXEC]] |
| **Modular Authorship** | `Extension/` boundary discipline; asmdef pattern; HTTP-boundary pattern | [[10_DOMAIN_MAP]], [[1C_UNITY_LIFECYCLE_DOMAIN]], [[1A_MEMORY_DOMAIN]] |
| **Open Knowledge** | Apache-2.0 attribution discipline; cite-and-adapt is permitted | [[03_ANTI_CDK]], every Adopt-list entry in every closer |
| **Public-Friendliness** | Japanese voice ecosystem accessibility; multi-platform reach | [[22_TTS_INTERFACE_JAPANESE]], [[66_JAPANESE_VOICE_INTEGRATION]], [[1D_MULTI_PLATFORM_DOMAIN]] |
| **Pluggable Storage** | Generalised to Pluggable Memory Provider (ChatMemory as one impl) | [[65_MEMORY_INTEGRATION]], [[1A_MEMORY_DOMAIN]] |
| **Defended System Prompt** *(Hermes)* | Sharpened to **Defended Credential Surface** — server-held-keys-only | [[51_SECURITY_REVIEW]], [[27_SOCKET_PROTOCOL]], [[28_JS_BRIDGE_INTERFACE]] |
| **Cache Discipline** *(Hermes)* | Dedupe-lock cache as Cache Discipline's *concrete shape*; lift the pattern | [[15_SPEECH_SYNTHESIZER_DOMAIN]], [[33_TTS_PREFETCH]] |
| **Embodied Honesty** *(Wave-3)* | Tool-call audit; face-tag-as-LLM-claim must be bias-merged with Hjarta state | [[12_MODEL_CONTROLLER_DOMAIN]], [[1B_ANIMATION_DOMAIN]], [[64_FUNCTION_CALLING_FOR_EMBODIED]] |
| **Surface Without Surveillance** *(Wave-3)* | XR's six sensors as six privacy surfaces; gaze-as-events-only reference | [[3D_XR_BUILD]], [[51_SECURITY_REVIEW]] |
| **Affective Restraint** *(Wave-3)* | Idle roulette as bounded animation surface; LLM never authors affect values | [[34_ANIMATION_PIPELINE]], [[1B_ANIMATION_DOMAIN]] |
| **Tiered Presence** *(Wave-3)* | Form-factor axis added (desktop / mobile / XR / WebGL); 3D tier projection | [[62_MOBILE_AND_XR_TIER]], [[1D_MULTI_PLATFORM_DOMAIN]] |
| **Federated Self** *(Wave-3)* | Multi-runtime persona portability (one persona across SAP-electron + CDK-unity + Waifu-cloud) | [[60_TRIANGULATION]], [[6A_INTEGRATION_ROADMAP]] |
| **Lazy Subsystems** *(Wave-3)* | Sister-project unavailability returns typed unavailable; ChatMemory optional | [[56_SISTER_INTEGRATION_RISKS]], [[1A_MEMORY_DOMAIN]] |
| **Closed Default** *(Wave-3)* | `IPAddress.Any` rejected; loopback or typed-Tailnet only | [[18_NETWORK_DOMAIN]], [[27_SOCKET_PROTOCOL]], [[51_SECURITY_REVIEW]] |
| **Server-Held-Keys-Only** *(Wave-5, proposed Vow candidate)* | LLM API keys never live in client builds (Unity asset / WebGL bundle / mobile binary). Server-side proxy required | [[51_SECURITY_REVIEW]], [[28_JS_BRIDGE_INTERFACE]], [[16_LLM_SERVICE_DOMAIN]] |
| **Triangulation-Before-Major-Decision** *(Wave-5, proposed standing rule)* | No embodiment-axis or major-architecture decision lands without three-corpus review | [[60_TRIANGULATION]], [[6A_INTEGRATION_ROADMAP]] |
| **Tailnet-Bind-Default** *(Wave-5, proposed)* | Any future Ember service that opens a socket binds to Tailscale interface by default, not localhost or `0.0.0.0` | [[18_NETWORK_DOMAIN]], [[27_SOCKET_PROTOCOL]], [[51_SECURITY_REVIEW]] |

---

## Citations to ChatdollKit

The Codex is grounded in a single, pinned local clone of ChatdollKit:

- **Path:** `/tmp/ChatdollKit/`
- **Version:** v0.8.16 (Feb 14, 2026 release)
- **License:** **Apache-2.0** (confirmed at `/tmp/ChatdollKit/LICENSE`) — **adopt-friendly** with attribution
- **Upstream:** `https://github.com/uezo/ChatdollKit`
- **Maintainer:** uezo (single maintainer for all five sister projects — see [[56_SISTER_INTEGRATION_RISKS]])

**Citation form throughout the Codex:** `/tmp/ChatdollKit/Scripts/AIAvatar.cs:142` — absolute path with line range. Acceptable shortened form: `AIAvatar.cs:142` once the file is in context.

**Sister-project citations** use the appropriate prefix:

- `/tmp/chatmemory/chatmemory/chatmemory.py:50` — ChatMemory FastAPI service
- `/tmp/aiavatarkit/server.py:X` — AIAvatarKit streaming server
- `/tmp/chatdollkit-aituber/X` — AITuber Controller bridge

**README claims** marked `[unverified — README claim only]` where the source does not corroborate (notably Watson TTS and XR support).

**Apache-2.0 attribution standard** (per [[STYLE_GUIDE §8]]): every doc that proposes Adopt-list entries derived from CDK adds the footer note *"Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c)."* The Scribe checked each Adopt list during the final pass; the footer is consistently present.

---

## Cross-Link Verification — Pending and Resolved

The Scribe walked every `[[...]]` link in the corpus on the final pass. Within-codex resolution rate: **100%**. The 63 content docs cross-reference each other and the 6 meta docs cleanly.

### Resolved (within-codex)

All within-codex `[[slug]]` references resolve to one of the 63 content docs + 6 meta docs listed in [[MANIFEST]]. The Scribe verified each by enumerating `find /home/volmarr/ai/ember/docs/chatdoll_codex -name "*.md"` (69 files total). No malformed slugs encountered. No typos in slug references found.

### Resolved (cross-codex, SAP + Waifu — the triangulation siblings)

The ChatdollKit Codex is the densest cross-codex consumer in Ember's documentation tree to date — denser even than Waifu's SAP-cross-references. At least **fifteen distinct SAP artifacts** and **eight distinct Waifu artifacts** are cited across the 63 content docs, often multiple times per doc, because the triangulation work in `[[60_TRIANGULATION]]` and the six Cartographer synthesis docs is structurally cross-codex.

| Reference | Status | Note |
|---|---|---|
| `[[sap:60_TRUE_NAME_REASSIGNMENT]]` | Resolves | The Andlit/Rödd/Hugarsýn/Veizla reservation source. Cited by every Wave-5 synthesis doc |
| `[[sap:63_PERFORMANCE_TIER_ENGINE]]` | Resolves | The T-1/T0/T1/T2/T3 tier ladder; Wave 5 adds form-factor axis |
| `[[sap:61_NEW_VOWS]]` | Resolves | The seven Wave-3 proposed Vows engaged across the corpus |
| `[[sap:11_AVATAR_DOMAIN]]`, `[[sap:25_AVATAR_PROTOCOL]]`, `[[sap:32_AVATAR_RENDER_PIPELINE]]` | Resolves | The SAP local-tier comparators for the embodiment triangulation |
| `[[sap:53_SECURITY_REVIEW]]`, `[[sap:55_API_SIMULATION_TRAPS]]`, `[[sap:57_FAILURE_TAXONOMY]]` | Resolves | The Auditor sibling docs |
| `[[sap:64_AFFECTION_ENGINE_REIMAGINED]]`, `[[sap:65_META_AWARENESS]]`, `[[sap:66_INVENTED_METHODS]]` | Resolves | The synthesis-layer triangulation siblings |
| `[[sap:03_ANTI_SAP]]`, `[[sap:04_VISION_SYNTHESIS]]` | Resolves | The Wave-3 vision-layer carry-forwards |
| `[[waifu:60_REALTIME_TIER_FOR_ANDLIT]]` | Resolves | The Wave-4 keystone; Tier-CLOUD parallel axis; cited by every Wave-5 synthesis doc |
| `[[waifu:61_DECISIONS_AND_INVENTIONS]]` | Resolves | The Wave-4 ADRs + inventions; cited as the *immediate predecessor's* invention list |
| `[[waifu:01_VISION_SYNTHESIS]]`, `[[waifu:00_OVERTURE]]` | Resolves | Wave-4 vision-layer carry-forwards |
| `[[waifu:52_NO_LICENSE_RISK]]` | Resolves | License-Aware Study Posture; carried forward as the *contrast* to CDK's Apache-2.0 give |
| `[[waifu:51_SECURITY_AND_PRIVACY]]` | Resolves | Mic-as-device-claim; consent token; carried into XR + WebGL builds |
| `[[waifu:21_LIVEKIT_INTEGRATION]]`, `[[waifu:22_ACTION_PROTOCOL]]` | Resolves | The LiveKit MIT surface; the action-vocabulary discipline |
| `[[waifu:10_DOMAIN_MAP]]`, `[[waifu:11_DUAL_MODE_PATTERN]]` | Resolves | The Vestibule Census; the Two-Door Rite |
| `[[waifu:50_DEPENDENCY_HEALTH]]` | Resolves | The Wave-4 dep-health sibling |

### Pending — Cross-codex references (Hermes, Peer, Klóinn)

| Reference | Status | Note |
|---|---|---|
| `[[hermes:00_OVERTURE]]`, `[[hermes:04_VISION_SYNTHESIS]]` | Resolves | Direct Hermes vision-layer files |
| `[[hermes:Cache_Discipline]]`, `[[hermes:Defended_System_Prompt]]` | **Pending — concept-references** | Same shape as the SAP-Codex and Waifu-Codex pending entries; point to Hermes-side Vow concepts rather than direct doc-slugs. A future Hermes glossary index would normalize. Wave 3 + Wave 4 flagged this; Wave 5 inherits the flag and does not amend |
| Peer-Codex cross-references | None in this codex | The ChatdollKit Codex did not consume Peer-Codex content directly; reference-density is SAP+Waifu-skewed by design (they are the immediate embodiment-axis predecessors) |
| `[[kloinn:...]]` references | **Klóinn-pending** | The Klóinn Codex (whatever its eventual content) is referenced as a forward-link in `[[6A_INTEGRATION_ROADMAP]]` and `[[68_INVENTED_METHODS]]`. Marked explicitly as **Klóinn-pending** in the source docs — the Scribe's discipline is to surface gaps rather than pad with speculation |

### Pending — Ember root references

References to Ember root docs and proposed-features resolve to files in `~/ai/ember/` or to Wave-3/4/5 proposals:

- `[[ember:RULES.AI]]`, `[[ember:PHILOSOPHY]]`, `[[ember:SYSTEM_VISION.md]]` — resolve to Ember root docs
- `[[ember:docs/decisions/0007]]` — resolves to the slice plan ratification gate
- The Wave-5 proposed sub-name reservations (`Andlit-unity`, `Rödd-unity`), the proposed Vow candidate (`Server-Held-Keys-Only`), and the proposed standing rule (`Triangulation-Before-Major-Decision`) are forward-link opportunities — pending Ember-side ratification. Per `[[STYLE_GUIDE §6]]`, forward-links to unwritten or unratified concepts are *not* broken; they mark "something proposed, awaiting ratification."

---

## Maintenance Notes

The Scribe keeps the same conventions inherited from the Hermes, SAP, and Waifu Codex traditions:

1. **One revision pin per wave.** ChatdollKit v0.8.16 (Feb 14, 2026) is pinned for Wave 5. The pin lives in [[SHARED_CONTEXT §1]].
2. **No silent rewrites.** A doc that materially changes between waves gets a `## Revision Log` block at its bottom — date, author, summary of change. The original framing is preserved above.
3. **Cross-links are walked at the end of each wave.** The Scribe ran the walk for Wave 5 and the results are recorded above. Within-codex: 100%. Cross-codex (SAP + Waifu): 100%. Hermes: same concept-reference pending status as prior waves. Peer + Klóinn: forward-link opportunities only.
4. **The Manifest is authoritative.** When a new doc is proposed mid-wave, it is added to [[MANIFEST]] first; only then is the file written. Wave 5 added no docs mid-wave; the original 63-content + 6-meta count held even across the session-limit interruption.
5. **Cross-agent notes are swept at the close of each wave.** Wave 5's cross-agent findings — including the session-limit story, the convergent findings across the two dispatches, and the Server-Held-Keys-Only Vow candidate — are catalogued in [[CROSS_AGENT_NOTES]].
6. **No paraphrased CDK.** Every claim about ChatdollKit points to a file path with line numbers. If the Codex says "CDK does X," the doc making the claim shows where in CDK X lives. The Refusal-Citation Discipline from `[[sap:03_ANTI_SAP]]` carries forward.
7. **Apache-2.0 attribution is binding.** Every Adopt-list entry across the corpus carries the per-doc attribution footer. The Scribe checked each Adopt list during the final pass; no violations found.
8. **Klóinn-pending markers are honored.** When a doc references a not-yet-authored Klóinn artifact, it marks the reference explicitly rather than papering over. Wave 6 (Klóinn) inherits the gap-list.
9. **Style stays in one place.** The voice conventions, frontmatter rules, citation format, and naming conventions all live in [[STYLE_GUIDE]]. New authors read it once, not seven docs.

### When this Codex becomes stale

The trigger to refresh the Codex is *any* of the following:

- ChatdollKit ships a release that materially changes `AIAvatar.cs`, the LLM service abstraction, the speech synthesizer base, or the network surface.
- A sister project (ChatMemory, AIAvatarKit, AITuber Controller, OshaberiAI) ships a breaking change that breaks the integrator contracts.
- UniVRM ships URP support (unblocks Vision Pro and other SRP-required targets — see [[50_DEPENDENCY_HEALTH]]).
- Ember ratifies a slice that materially changes the Andlit-unity / Rödd-unity boundary (e.g., Andlit-unity sub-name shipped, Rödd-unity adapter shipped).
- A migration path proposed in [[6A_INTEGRATION_ROADMAP]] or [[6B_EMBER_WAVE_5_SLICE]] is accepted, partly accepted, or rejected — the decision record is filed under `~/ai/ember/docs/decisions/`, and the Codex's synthesis docs are amended to reflect what was actually chosen.

In each case, the new wave begins with the Scribe re-pinning [[SHARED_CONTEXT §1]] and walking the manifest.

---

## A Closing Note from the Scribe

The Codex is large. Sixty-three content documents over 18,221 lines of C# plus ~3,000 lines of sister-project code is the most-source-mass Ember codex to date. The alternative — Ember's contributors, today and a year from now, re-deriving the Hjarta-Brunnr Rule from `ChatMemoryIntegrator.cs`'s 108 lines every time the question arises, or re-discovering that `IPAddress.Any` is bound by default every time someone reaches for SocketServer — is much worse. This Codex is a sieve. Wave 5 poured ChatdollKit plus its four sister projects through it. What you read here is what was caught.

The session limit fired mid-wave. The corpus held. Five partial-layer commits + five layer-completion commits captured the recovery. The discipline that made the recovery clean — agent briefings that read only from disk, no in-session orchestration state — is the Wave-5 contribution to Mythic Engineering practice itself. The Clean-Resume Discipline is named in [[CROSS_AGENT_NOTES §1]] for the next wave's authors.

If the sieve has a hole, leave a note in [[CROSS_AGENT_NOTES]]. The next wave widens the catch.

The triangulation is closed. The Unity face is reachable through eighteen-thousand lines of C# and an asmdef boundary. The Codex's contribution is *not* whether Ember reaches for it — that decision is the keeper's. The Codex's contribution is to make sure that, when the decision is made, *the vocabulary is precise enough to make it well*. Andlit-unity stays a reserved sub-name on the shelf with Andlit-local and Andlit-realtime until the keeper rules. The reservation is cheap. The wrong-path-stretch (cramming Unity-render concerns into the local-electron tree, or burying VRM-loader cost in WebGL-bundle assumptions) is expensive. The Codex's job is to keep the path-tree honest while the ratification queue does its work.

— *Eirwyn Rúnblóm, the Scribe, on behalf of the Seven (and the five who returned after the reset), at the close of Wave 5*

## What This Means for Ember

The INDEX itself does not propose a feature. It proposes a *practice*: that Ember's relationship to ChatdollKit — and to any future Apache-2.0 embodiment-shaped agent worth studying — be mediated by a maintained Codex with binding Apache-2.0 attribution discipline rather than by ad-hoc reading. The practice protects every Vow indirectly, but especially:

- **Open Knowledge** is honored when contributors find out in twenty minutes that Apache-2.0 means *cite and adapt with attribution*, not *vendor freely*; the cost is one `NOTICE` line per adopted pattern; the give is real code Ember can reuse. [[03_ANTI_CDK]] makes the position explicit.
- **Tiered Presence** gains the form-factor axis — the third dimension Wave 4 deferred. The tier engine becomes 3D (rung × cloud-axis × form-factor); each axis is operator-declared at first-run.
- **Modular Authorship** is protected when the codex names *the Hjarta-Brunnr Rule* as the load-bearing boundary discipline — ChatMemory is one implementation; the architectural shape is provider-agnostic and re-applies to any future Hjarta/Brunnr split (diary, knowledge graph, identity registry, persona archive).
- **Defended Credential Surface** (sharpened from Hermes-proposed Defended System Prompt) is protected when the codex elevates *Server-Held-Keys-Only* to a Vow candidate, citing the three independent corpora (Waifu, CDK, Hermes-implicit) that converged on the rejection.
- **Honest Memory** is protected when the Codex itself is honest about *what* it pinned (`ChatdollKit` at v0.8.16), *when* (May 2026), and *what was unusual about the wave's mechanics* (the session-limit interruption + clean resume, surfaced in [[CROSS_AGENT_NOTES §1]] rather than buried).
- **Triangulation-Before-Major-Decision** (proposed standing rule) is honored by the very existence of this codex; the Wave-5 work is itself the third leg of the embodiment-axis triangulation, and the practice is now a procedural Vow candidate.

The True Names this affects are the six core True Names plus the three reserved-paired-names (Andlit, Rödd, Hugarsýn) with new third sub-name slots (Andlit-unity, Rödd-unity), plus the Veizla lifecycle vocabulary sharpened to four states (Sealed / Idle / Engaged / Closing). The Codex holds the sub-name slots open so the eventual code — if it lands — lands in rooms with names already prepared instead of in another `AIAvatar.cs` ten-responsibility monolith.

The seal is intact. The envelope is large. The territory is mapped. The triangulation is closed.

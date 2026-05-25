---
codex_id: 57_FAILURE_TAXONOMY
title: Failure Taxonomy — Forty-Two Ranked Failure Modes Across CDK And Its Sisters, By Impact × Likelihood
role: Auditor
layer: Verification
status: draft
chatdoll_source_refs:
  - (see per-row citations in the table below)
sister_source_refs:
  - (see per-row citations in the table below)
ember_subsystem_targets: [Funi, Munnr, Rödd, Hjarta, Strengr, Andlit]
cross_refs:
  - 50_verification/50_DEPENDENCY_HEALTH
  - 50_verification/51_SECURITY_REVIEW
  - 50_verification/52_PERFORMANCE_BUDGETS
  - 50_verification/53_MULTI_LLM_CONSISTENCY
  - 50_verification/54_MULTI_TTS_QUALITY
  - 50_verification/55_WEBGL_GOTCHAS
  - 50_verification/56_SISTER_INTEGRATION_RISKS
  - 20_interface/21_TTS_INTERFACE_WESTERN
  - 20_interface/22_TTS_INTERFACE_JAPANESE
  - 20_interface/23_STT_INTERFACE
  - 20_interface/27_SOCKET_PROTOCOL
  - 20_interface/28_JS_BRIDGE_INTERFACE
---

# Failure Taxonomy — Forty-Two Ranked Failure Modes Across CDK And Its Sisters, By Impact × Likelihood

> *Sólrún, voice cold and even: this document is the rollup of every Auditor doc in this codex (50–55 plus the five interface dossiers) reorganized as a single ranked table. The unit of analysis is the failure mode: a concrete way the kit-of-kits can fail, with a citation path and a categorical likelihood × impact score. I rank impact on a four-level scale (Catastrophic / High / Medium / Low) and likelihood the same way (Near-certain / Likely / Possible / Rare). The top-of-table entries are the rows where both axes are at the high end; these are the failures Ember must defend against first.*
>
> *Forty-two entries is the count after consolidation. I have folded duplicate findings (e.g., "API key in build artifact" is one row, not eleven per-provider rows) and listed the per-provider tail in the cited section. The table is structured for triage — read the top ten, ratify against the Ember subsystem map, decide what gets a defended-build clause and what gets an operator-tier warning.*

This document is the impact × likelihood rollup. It does not introduce new findings; it consolidates the audit layer's findings into a triage-friendly form. Each row is `(rank, finding, citation, impact, likelihood, Ember subsystem, mitigation posture)`.

**Methodology.** I read 50–56 + the five interface docs + 51's STRIDE pass. For each distinct failure mode I assigned:
- **Impact:** Catastrophic (data loss, credential leak, livestream-ending), High (privacy breach, degraded reliability, billing exposure), Medium (occasional user-visible failure, partial UX loss), Low (cosmetic, log-noise).
- **Likelihood:** Near-certain (will occur in any production deployment within a month), Likely (operator-tier mitigations exist but most operators skip), Possible (requires specific conditions or attacker presence), Rare (requires hostile actor with access).
- **Rank:** `Impact × Likelihood` lexicographic, with ties broken by the breadth of affected deployments (WebGL+desktop+mobile beats desktop-only).

The table is sorted by rank. Lower row number = higher priority for Ember to defend.

---

## 1. The Top Ten — Defend Or Die

| # | Finding | Cite | Impact | Likelihood | Ember target |
|---|---|---|---|---|---|
| 1 | **API key baked into build artifact** for every direct-vendor LLM/STT/TTS service (eleven providers). Inspector `public string ApiKey;` is serialized into scene YAML and bundled into iOS/Android/WebGL/standalone builds. Decompilable in under a minute. | `[[51_SECURITY_REVIEW §5.1]]`, `ChatGPTService.cs:15`, `ClaudeService.cs:15`, eleven other locations | Catastrophic | Near-certain | Strengr Key Vault (51 Invent) |
| 2 | **SocketServer binds `IPAddress.Any` with no auth, no TLS, no rate limit, no max message length.** Anyone on the LAN can issue any operation defined by the operator's handler, including the demo handler's `llm/activate` (reassigns LLM provider, API key, system prompt over the wire) and `model/load` (loads remote VRM from arbitrary URL). | `[[27_SOCKET_PROTOCOL §2–§4]]`, `[[51_SECURITY_REVIEW §3.1]]`, `SocketServer.cs:88`, `AITuberMessageHandler.cs:217-272` | Catastrophic | Likely (any networked deployment) | Tailnet-default control channel + bearer (27 Invent) |
| 3 | **`window.SendMessageToChatdollKit` is a window-global callable with no origin check** in WebGL builds. Any first-party script, third-party script, browser extension content script, iframe ancestor, or XSS payload on the host page can drive the avatar. | `[[28_JS_BRIDGE_INTERFACE §1, §3]]`, `[[51_SECURITY_REVIEW §3.2]]`, `Plugins/JavaScriptMessageHandler.jslib` | Catastrophic | Likely (any WebGL deploy) | postMessage + origin allowlist + bearer (28 Invent) |
| 4 | **LLM function-call name is trusted from the model.** A prompt-injected LLM can emit an arbitrary `FunctionName` and CDK dispatches against the local `ITool` registry with no consent gate. | `[[51_SECURITY_REVIEW §3.3]]`, `ChatGPTService.cs:355-371` | High to Catastrophic (depends on tools) | Possible (any production with tools) | Consent-gated tool invocation + side-effect flagging |
| 5 | **`system_prompt` reassignable over unauthenticated socket** in the AITuber demo handler. Attacker rewrites the doll's persona on the next user turn. | `[[27_SOCKET_PROTOCOL §4.1]]`, `AITuberMessageHandler.cs:261-264` | Catastrophic (during livestream) | Possible (LAN attacker present) | Defended System Prompt vow (Hermes pattern) |
| 6 | **`api_key` reassignable over unauthenticated socket** in the AITuber demo handler. Attacker routes the doll to their own LLM endpoint. | `[[27_SOCKET_PROTOCOL §4.1]]`, `AITuberMessageHandler.cs:230-258` | Catastrophic | Possible | Reject categorically; keys live in Strengr only |
| 7 | **WebGL JSLIB plug-ins ship API keys as `char*` to fetch URL/header**, visible in DevTools Network panel. | `[[28_JS_BRIDGE_INTERFACE §2.1]]`, `[[51_SECURITY_REVIEW §5.1]]`, `Plugins/GeminiServiceWebGL.jslib`, four other JSLIB files | Catastrophic | Near-certain (any WebGL with direct vendor LLM) | Strengr proxy; JSLIB never sees real key |
| 8 | **`anthropic-dangerous-direct-browser-access: true`** header set in Claude WebGL JSLIB. The header name is the documentation of the threat model; CDK opts in. | `[[28_JS_BRIDGE_INTERFACE §2.1]]`, `Plugins/ClaudeServiceWebGL.jslib` | Catastrophic (Claude billing-attached keys) | Near-certain (any Claude-WebGL deploy) | Refuse to ship the header; route through Strengr |
| 9 | **No vector index by default on ChatMemory's Postgres tables.** Vector queries degrade to seq-scan at scale. | `[[38_CHATMEMORY_INTEGRATION]]`, `[[56_SISTER_INTEGRATION_RISKS §2]]`, `chatmemory.py:239-317` | High (latency degrades over time) | Near-certain (production lifetime) | Hjarta init creates HNSW/IVFFLAT indexes |
| 10 | **Always-listening posture by default** on all STT batch listeners — `AutoStart && IsEnabled` makes the microphone hot from app launch with no push-to-talk affordance. | `[[23_STT_INTERFACE §9]]`, `SpeechListenerBase.cs:60-63, :202` | High (privacy posture) | Near-certain (default-config deploys) | Push-to-talk default + mute chord vow |

These ten alone justify the Auditor's entire pass. Each is a *load-bearing* defense Ember must address. The rest of the table is the long tail.

---

## 2. The Next Twenty — Operator-Tier Hardening

| # | Finding | Cite | Impact | Likelihood | Ember target |
|---|---|---|---|---|---|
| 11 | **Per-connection unbounded thread spawn on SocketServer.** Trivial DoS from a single attacker on the LAN. | `[[51_SECURITY_REVIEW §6.2]]`, `SocketServer.cs:106-108` | High (process unresponsive) | Possible | Bounded async accept + semaphore |
| 12 | **Unbounded `ReadLine` on SocketServer.** Multi-GB line exhausts memory before parsing. | `[[51_SECURITY_REVIEW §6.1]]`, `SocketServer.cs:165` | High | Possible | Max-line-length config |
| 13 | **Unbounded `audioCache` Dictionary on SpeechSynthesizerBase.** Long sessions leak `AudioClip` allocations until OOM, especially on mobile/WebGL. | `[[51_SECURITY_REVIEW §6.3]]`, `[[55_WEBGL_GOTCHAS §4]]`, `SpeechSynthesizerBase.cs:15` | High (mobile/WebGL) | Likely (long sessions) | LRU eviction policy |
| 14 | **`TypeNameHandling.All` on Newtonsoft** for `messageSerializationSettings`. Currently scoped to internal use; one refactor from being externally reachable. | `[[51_SECURITY_REVIEW §4.1]]`, `ChatGPTService.cs:37-40` | Catastrophic (latent) | Rare (currently) | Ember bans `TypeNameHandling.All` categorically |
| 15 | **Azure SSML constructed via string concatenation without escaping.** LLM output containing `<`/`>`/`&`/`'`/`"` produces malformed SSML; Azure may truncate or reject. | `[[21_TTS_INTERFACE_WESTERN §3]]`, `AzureSpeechSynthesizer.cs:84` | Medium (audio quality) | Likely (any LLM with markdown-like output) | `SecurityElement.Escape` in adapter |
| 16 | **Gemini API key in URL query string** (native HTTP and WebGL JSLIB). Leaks through proxy logs, referrer headers, OS network traces. | `[[51_SECURITY_REVIEW §5.2]]`, `[[28_JS_BRIDGE_INTERFACE §2.1]]`, `GeminiService.cs:214`, `Plugins/GeminiServiceWebGL.jslib` | High | Near-certain (any Gemini deploy) | Route through Strengr regardless of credential storage |
| 17 | **VOICEVOX CORS misconfig + mixed-content** blocks WebGL builds. VOICEVOX default rejects cross-origin; HTTPS page + HTTP backend triggers mixed-content blocker. | `[[22_TTS_INTERFACE_JAPANESE §2.5]]`, `[[55_WEBGL_GOTCHAS §7]]` | High (WebGL specifically) | Near-certain (untrained operator) | Document at boot; engine-side `--cors_policy_mode=all` |
| 18 | **VOICEVOX cold-start latency** (2-5s on first call). The kit's audioCache deduplication does not pre-warm; first user utterance pays the cost. | `[[22_TTS_INTERFACE_JAPANESE §2.5]]` | Medium | Near-certain | Warmup vow at boot |
| 19 | **VOICEVOX speaker-ID drift between versions.** A VOICEVOX major release renumbers speakers; CDK's `VoiceStyles` Inspector list stores literal integers. Silent misroute of "Zundamon-Normal" → wrong character. | `[[22_TTS_INTERFACE_JAPANESE §2.5]]`, `VoicevoxSpeechSynthesizer.cs:35, 183-188` | High (when it happens) | Possible (across upgrades) | Version-pin VOICEVOX in compatibility manifest |
| 20 | **Empty-result NullReferenceException on Azure STT.** `combinedPhrases[0].text` indexes without bounds check; empty response (silence misclassified as "speech") throws. | `[[23_STT_INTERFACE §4]]`, `AzureSpeechListener.cs:91` | Medium | Possible | Null-guard in adapter |
| 21 | **OpenAI Whisper response throws away word timings, confidence, detected language.** CDK uses `response_format=text` for the bare transcript. | `[[23_STT_INTERFACE §3]]`, `OpenAISpeechListener.cs:31` | Low to Medium | Near-certain | Use `response_format=verbose_json` + typed parsing |
| 22 | **Multi-VAD OR-fusion is permissive.** Energy detector triggers on noise; Silero correctly says "no speech" but kit ORs them. Recall over precision. | `[[23_STT_INTERFACE §2]]`, `SpeechListenerBase.cs:110` | Medium (noisy environments) | Likely (open-mic livestream, cafe) | Configurable fusion policy (OR/AND/MAJORITY) |
| 23 | **WebGL audio context suspended until user gesture.** Auto-greeting TTS plays silently for first 1-2 seconds after page load if no gesture. | `[[55_WEBGL_GOTCHAS §2]]`, `Plugins/WebGLMicrophone.jslib:56-60` | Medium | Near-certain (auto-open page deployments) | Click-to-begin overlay + gesture-bound resume |
| 24 | **WebGL build memory pressure.** Default 256-512MB heap; long sessions with audio cache + ONNX VAD + VRM model abort with `RuntimeError: memory access out of bounds`. | `[[55_WEBGL_GOTCHAS §4]]` | High (WebGL long sessions) | Likely | Eviction + heap monitoring + linter |
| 25 | **`UTCnow()` deprecated calls** throughout ChatMemory (Python 3.12 deprecation). | `[[38_CHATMEMORY_INTEGRATION]]`, `chatmemory.py:347, 670, 714, 796` | Low (warnings) | Near-certain (post-3.12) | `datetime.now(timezone.utc)` adaptation |
| 26 | **ChatMemory background-task silent failure.** `BackgroundTasks` swallows exceptions; session summaries can silently fail. | `[[38_CHATMEMORY_INTEGRATION]]`, `chatmemory.py:1170-1171` | Medium | Possible | Structured error logging + `/health/memory` route |
| 27 | **No auth on ChatMemory FastAPI surface.** Any process reaching the port reads/writes any user's memory. | `[[38_CHATMEMORY_INTEGRATION]]`, `[[56_SISTER_INTEGRATION_RISKS §2]]` | High | Likely (default deployment) | Middleware-layer bearer requirement |
| 28 | **No multi-user isolation at ChatMemory DB level.** Partition is `user_id` only; no RLS. Misconfigured integrator writes into wrong user's history. | `[[38_CHATMEMORY_INTEGRATION]]`, `[[56_SISTER_INTEGRATION_RISKS §2]]` | High (when it happens) | Possible | Postgres RLS at deployment |
| 29 | **AIAvatarKit WebSocket protocol has no version field.** A protocol change between AIAvatarKit and CDK silently corrupts streaming STT. | `[[56_SISTER_INTEGRATION_RISKS §3]]`, `AIAvatarKitStreamSpeechListener.cs:360-373` | High | Likely (across version upgrades) | Protocol version negotiation handshake |
| 30 | **Mobile microphone permission text is operator-supplied** and CDK ships no canonical phrasing. Users grant broad mic permission with vague rationale. | `[[51_SECURITY_REVIEW §5.4]]` | Medium (privacy posture) | Near-certain | Default privacy-conscious permission strings in Ember |

---

## 3. The Long Tail — Twelve More

| # | Finding | Cite | Impact | Likelihood | Ember target |
|---|---|---|---|---|---|
| 31 | **Debug logging echoes secrets / conversation content** when `DebugMode = true`. Default is false but operator-toggleable; reachable over the SocketServer's `llm/debug` operation. | `[[51_SECURITY_REVIEW §5.3]]`, `ChatGPTService.cs:257` | High (when enabled) | Possible | Refuse to ship `llm/debug` as a remote operation |
| 32 | **JS bridge `console.log` of every inbound message.** Sensitive content (api_keys in `llm/activate` payloads, system prompt updates) ends up in F12 console history. | `[[28_JS_BRIDGE_INTERFACE §1.1]]`, `Plugins/JavaScriptMessageHandler.jslib:6` | Medium (privacy) | Near-certain (any debug session) | Debug-gated logging |
| 33 | **Async/Await trap in WebGL.** Third-party Unity assets using stock `Task` instead of `UniTask` freeze the application silently. | `[[55_WEBGL_GOTCHAS §6]]`, `README.md:1020` | High (when triggered) | Possible (any third-party asset) | WebGL build linter |
| 34 | **Silero VAD in WebGL** has high browser processing overhead; kit recommends server-side offload but doesn't enforce. | `[[55_WEBGL_GOTCHAS §3.1]]`, `SileroVADProcessor.cs:9-30` | Medium (WebGL performance) | Likely | Force server-side VAD in WebGL builds |
| 35 | **Copy-paste of resample logic** between `SpeechListenerBase.cs:146-163` and `AIAvatarKitStreamSpeechListener.cs:228-245`. Bug-fix surface area doubled. | `[[23_STT_INTERFACE §7.5]]` | Low (maintenance) | Near-certain (someone will edit one not the other) | Shared `AudioResampler` helper |
| 36 | **Copy-paste of `」` guard** across five Japanese TTS providers. | `[[22_TTS_INTERFACE_JAPANESE §1]]` | Low (maintenance) | Near-certain | Lift to base-class `PreprocessText` default |
| 37 | **Copy-paste of style-dispatch loop** across five providers. | `[[22_TTS_INTERFACE_JAPANESE §9]]` | Low (maintenance) | Near-certain | `IStyledSpeechSynthesizer` mixin |
| 38 | **NijiVoice two-call generate-then-fetch latency** (800-1500ms). Too slow for default conversational TTS. | `[[22_TTS_INTERFACE_JAPANESE §6]]` | Medium (UX) | Near-certain (NijiVoice deploys only) | Reject as default; specialty tier only |
| 39 | **VOICEROID three-tier deployment** (Win + pyvcroid2-api + vcroid2.exe) plus PATCH-at-startup-mutates-server-state. Multi-client coexistence broken. | `[[22_TTS_INTERFACE_JAPANESE §4]]`, `VoiceroidSpeechSynthesizer.cs:54, :117-121` | Medium | Possible (multi-tenant scenarios) | Per-call settings rather than session mutation |
| 40 | **README claims Watson TTS that does not exist** in the source tree. Documentation drift. | `[[21_TTS_INTERFACE_WESTERN §7]]` | Low (operator confusion) | Near-certain (any operator reading README) | Watson-class doc discipline vow |
| 41 | **OpenAI `tts-1` model name frozen** in source. Newer models (`tts-1-hd`, `gpt-4o-mini-tts`) require source edit. | `[[21_TTS_INTERFACE_WESTERN §4]]`, `OpenAISpeechSynthesizer.cs:67` | Low (maintenance) | Near-certain (over time) | Inspector-exposed `Model` field |
| 42 | **AzureStreamSpeechListener key in WSS URL.** WebSocket subscription URL embeds `Ocp-Apim-Subscription-Key`. Same leak surface as Google's URL key. | `[[23_STT_INTERFACE §8]]`, `[[51_SECURITY_REVIEW §3.1]]` | High | Near-certain (Azure-stream deploys) | Use Azure issueToken short-lived token path |

---

## 4. The Categorical Rollup

The forty-two findings fall into eight categories. The category counts tell the architectural story:

| Category | Count | Top representatives |
|---|---|---|
| **Credential leak (build / wire / log)** | 11 | #1, #6, #7, #8, #16, #31, #32, #42 |
| **No-auth control plane** | 6 | #2, #3, #5, #11, #27, #29 |
| **Memory / resource exhaustion** | 4 | #12, #13, #24, #34 |
| **TTS / STT quality + edge cases** | 7 | #15, #17, #18, #19, #20, #21, #23 |
| **Documentation drift + operator footgun** | 4 | #22, #30, #40, #41 |
| **Sister / dependency coupling** | 5 | #25, #26, #28, #29, #39 |
| **Privacy / consent posture** | 2 | #10, #30 |
| **Code hygiene** | 3 | #35, #36, #37 |

The two largest categories are **credential leak** (11) and **no-auth control plane** (6). Combined, they are 17 of 42 findings (40%). The kit's posture is fundamentally credential-trustful and control-plane-trustful — it assumes the operator is alone with their build artifacts and alone on their network. Both assumptions fail in production.

The next largest is **TTS/STT quality** (7), which is the price of multi-provider abstraction without a strict capability registry. Each provider has its own corner cases; CDK exposes them faithfully without normalizing.

The third is **sister coupling** (5), which is the cost of the kit-of-kits architecture. Each sister adds its own failure modes.

---

## 5. The Defense Posture For Ember

Based on the categorical rollup, Ember's defense priorities are:

### 5.1 Credential Defense — The Strengr Key Vault Mandate

No credentialed surface in Ember's embodiment tier *ever* holds a real provider key. This includes:

- No `public string ApiKey;` Inspector field. Period.
- No `char*` API key argument to a JSLIB function. Period.
- No URL-query API key in any HTTP request from the embodiment tier. Period.

The Strengr Key Vault (`[[51_SECURITY_REVIEW]] Invent`) issues per-installation device tokens at install time. The embodiment tier uses only the device token to authenticate to Strengr; Strengr proxies all upstream provider calls and injects the real keys server-side. **This is the single highest-priority Ember architectural commitment from the audit layer.**

### 5.2 Control Plane Defense — Tailnet + Bearer + Capability

The Ember control plane (SocketServer-analog plus JS-bridge-analog) operates under three layered defenses:

1. **Bind on Tailnet interface by default** (not `0.0.0.0`, not even `127.0.0.1` for the network-reachable control plane). Localhost-only is a separate sub-channel for operator-typed-at-the-terminal one-time codes.
2. **Bearer token required** as the first message on every connection. Strengr-issued, short-lived, capability-scoped.
3. **Capability scoping** limits each bearer to a declared set of `(endpoint, operation)` pairs. The dispatcher refuses out-of-scope operations.

This is three independent defenses; each is sufficient against a single attacker class. Compounded, they raise the cost meaningfully.

### 5.3 Privacy + Consent — The Mute Vow

Every audio capture path defaults to *user-gestured initiation*, not always-listening. The dialog manager exposes `Munnr.MuteAll()` and a configurable mute keyboard chord. UI badges indicate "listening" state in real time. iOS / Android microphone-usage descriptions are canonical and conservative.

### 5.4 Dependency Pinning + Compatibility Manifest

Every sister project is pinned to a specific version range in `data/charts/ember_sister_compat.yaml`. Funi reads it at boot, pings each sister's `/health` endpoint, and refuses to enter the user-facing state if any sister returns an incompatible version. CDK is folkloric; Ember is single-source.

### 5.5 Forge-Ready Tooling — The WebGL Build Linter

Before any WebGL bundle ships, a build linter checks for:
- Any field of type `string` named like `ApiKey`/`Token`/`Secret`.
- Any reference to stock `System.Threading.Tasks.Task` outside `using` directives (signals non-UniTask third-party code).
- Any cache `Dictionary<...>` field without an associated eviction mechanism.
- Any `IPAddress.Any` literal in SocketServer-equivalent code.

The linter blocks the build. Each finding is a typed error with a code (`EMBER-LINT-W001` etc.) and a docs link.

---

## 6. Cross-References

This document references every other Auditor doc in the codex (50–55 + 56 + the five interface dossiers). Per-finding citations are inline in the tables above.

- `[[50_DEPENDENCY_HEALTH]]` — direct-dependency brittleness map.
- `[[51_SECURITY_REVIEW]]` — STRIDE catalog; the deepest credential and control-plane reading.
- `[[52_PERFORMANCE_BUDGETS]]` — latency and render budgets per platform tier.
- `[[53_MULTI_LLM_CONSISTENCY]]` — function-call format divergence across LLM providers.
- `[[54_MULTI_TTS_QUALITY]]` — per-provider voice quality, latency under load, lip-sync drift.
- `[[55_WEBGL_GOTCHAS]]` — Emscripten / single-thread / memory pressure / AudioContext.
- `[[56_SISTER_INTEGRATION_RISKS]]` — the four sisters' version drift and breaking-change exposure.
- `[[21_TTS_INTERFACE_WESTERN]]`, `[[22_TTS_INTERFACE_JAPANESE]]`, `[[23_STT_INTERFACE]]`, `[[27_SOCKET_PROTOCOL]]`, `[[28_JS_BRIDGE_INTERFACE]]` — interface-level dossiers.

---

## What This Means for Ember

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit and sister-project header references per Apache-2.0 §4(c).*

**Adopt:**

- **The top-ten-priority discipline.** Ember's CI runs a static check that every Auditor-flagged top-ten finding from this taxonomy has a corresponding mitigation in the code. The build fails if a mitigation is missing.
- **The four-level Impact / Likelihood scoring scale** as Ember's audit posture going forward. Future Auditor passes use the same scale and produce the same rollup. The rollup is the single triage surface for any operator before deployment.

**Adapt:**

- **The categorical taxonomy.** The eight-category split is right for CDK; Ember-specific deployments may surface additional categories (XR-sensor exfil, on-device-LLM model integrity, etc.). The taxonomy is extensible.

**Avoid:**

- **The "fix it later" temptation** for any top-ten finding. The categorical rollup makes "later" expensive: a credential-leak fix once we ship is much more painful than a credential-leak prevention at design time.
- **The "operator will handle it" pattern.** Every CDK finding that bottoms out at "operator must configure correctly" is a finding that *some* operators will miss. Ember's defaults must be secure-by-default; operator action is required to weaken, not to strengthen.

**Invent:**

- A **Failure Mode Registry** as the operational sibling to this taxonomy. Each finding has a typed code (`EMBER-FM-CREDENTIAL-001`, `EMBER-FM-CONTROL-002`, etc.), a documented mitigation, and a CI check. When a new finding is discovered, it gets a code, a registry entry, and a CI check. The registry is queried by `funi audit` (a CLI) which produces a per-deployment report. Vow tie-in: **Tethered Grounding** (the registry is the well of audit truth), **Defended Memory** (mitigations are append-only with deprecation windows).
- A **Per-Deployment Threat Model Document.** Operators deploying Ember are required to author (or accept a template) a one-page threat model: what attackers exist, what surfaces are exposed, what mitigations are in place. The document is reviewed at first deployment and on every major upgrade. CDK ships none; Ember requires it as a build artifact. Vow tie-in: **Defended System Prompt** generalized to **Defended Deployment**.
- A **Failure Mode Severity Audit Cadence.** Every six months, the Auditor role re-runs the impact × likelihood scoring against the current codebase and the current threat landscape. Findings whose severity has shifted (e.g. a previously-Rare attack becomes Likely because a new attack tool ships) are re-prioritized. The taxonomy is a living document. Vow tie-in: **Defended Builds**.
- A **Pre-Flight Checklist for Production.** Before any Ember tier ships to a production-facing channel (App Store, livestream, public WebGL URL), a pre-flight checklist is executed. The checklist is generated from the Failure Mode Registry: every top-ten finding has a corresponding question. Operators sign off on the checklist before the release pipeline grants the production tag. CDK has no equivalent; Ember requires it. Vow tie-in: **Tethered Grounding**.
- A **Failure Mode Cross-Codex Pollination.** This taxonomy is the third one in the codex set (after Hermes's vow catalog and Peer's cross-comparison). Findings that appear in *all three corpora* (credential leak in build artifacts shows up in SAP, Waifu, and CDK) get a "Universal" rating and become permanent Ember vows. Findings that appear in *only one corpus* get an "Idiosyncratic" rating and become situational defenses. Vow tie-in: **Federated Self** generalized to **Federated Threat Model**.

A final invent: a **Ratification-Gated Failure Mode Promotion.** New findings discovered between audit passes go into a `pending` state. The user (Volmarr) ratifies each one before it becomes a CI-enforced check. This prevents auditor-noise from blocking development; it also ensures every CI rule traces back to an explicit decision. CDK has no equivalent — findings live in PR comments or issue threads, with no ratification gate. Ember's failure taxonomy is the document of record. Vow tie-in: **Ratification-Gated First Slice** generalized to **Ratification-Gated Defense**.

---

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit and sister-project header references per Apache-2.0 §4(c).*

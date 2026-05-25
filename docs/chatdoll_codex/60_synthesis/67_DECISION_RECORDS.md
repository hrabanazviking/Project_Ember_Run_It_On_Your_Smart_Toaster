---
codex_id: 67_DECISION_RECORDS
title: Decision Records — ADR-Proposed for CDK-Driven Adoption Decisions
role: Scribe
layer: Synthesis
status: draft
chatdoll_source_refs:
  - Scripts/AIAvatar.cs
  - Scripts/LLM/ILLMService.cs
  - Scripts/LLM/LLMServiceBase.cs
  - Scripts/LLM/ITool.cs
  - Scripts/LLM/ToolBase.cs
  - Scripts/LLM/ChatGPT/ChatGPTService.cs
  - Scripts/LLM/Claude/ClaudeService.cs
  - Scripts/LLM/Gemini/GeminiService.cs
  - Scripts/Model/ModelController.cs
  - Scripts/SpeechListener/SileroVADProcessor.cs
  - Scripts/SpeechSynthesizer/*
  - Scripts/Network/SocketServer.cs
  - Scripts/Network/JavaScriptMessageHandler.cs
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr, Andlit-unity-proposed, Rödd-proposed]
cross_refs:
  - 60_synthesis/60_TRIANGULATION
  - 60_synthesis/61_ANDLIT_UNITY_TIER
  - 60_synthesis/62_MOBILE_AND_XR_TIER
  - 60_synthesis/63_MULTIMODAL_PIPELINE
  - 60_synthesis/64_FUNCTION_CALLING_FOR_EMBODIED
  - 60_synthesis/65_MEMORY_INTEGRATION
  - 60_synthesis/66_JAPANESE_VOICE_INTEGRATION
  - 60_synthesis/68_INVENTED_METHODS
  - 60_synthesis/69_SLICE_PLAN_REVISIONS
  - 60_synthesis/6A_INTEGRATION_ROADMAP
  - 60_synthesis/6B_EMBER_WAVE_5_SLICE
  - sap_codex/60_synthesis/68_DECISION_RECORDS
  - waifu_codex/60_synthesis/61_DECISIONS_AND_INVENTIONS
---

# 67 — Decision Records (ADR-Proposed)

> *Twelve envelopes, twelve decisions waiting. The kit is Apache-licensed, the source is mature, and the keeper can be generous with adoption — but the seal is still the keeper's to break.*
> — Eirwyn Rúnblóm, sealing the CDK-derived proposals into envelopes

## 0. Posture — Proposed, not Ratified

Every record below is **Status: Proposed**. None are decisions yet. They follow Ember's existing ADR style (per `docs/decisions/0001-mythic-engineering-bootstrap-2026-05-17.md` and peers) but live here under `docs/chatdoll_codex/60_synthesis/` to keep `docs/decisions/` untouched until Volmarr ratifies.

If Volmarr ratifies any of these, the next step is **copy the record into `docs/decisions/NNNN-<slug>.md` with the appropriate ADR number and Status: Ratified**, and reference this Codex doc.

The shape is **Context → Decision → Consequences → Alternatives Considered → Status**. Each is sized to be reviewable in 4–6 minutes.

Cross-referencing convention: each ADR also lists the inventions or methods it instantiates, by reference to `[[68_INVENTED_METHODS]]` numbered sections.

Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c). This is a once-per-doc note that binds every Adopt-list entry below.

---

## ADR-Proposed-CDK-001 — Adopt CDK's Tag-Extraction Pattern for Munnr Output

**Status:** Proposed (Scribe, 2026-05-25)

**Context.** CDK uses an in-band tag protocol to drive avatar behavior from LLM output. The LLM is prompted to emit lines such as `[face:Joy] [anim:Greet] Hello, master.` and `ModelController` extracts the tags via regex before the text is handed to the TTS layer. See `/tmp/ChatdollKit/Scripts/Model/ModelController.cs` for the tag-extraction site (Architect's `[[1B_ANIMATION_DOMAIN]]` documents the exact lines). The pattern is delightfully simple: prompt the LLM to annotate, extract before speaking, dispatch in parallel.

Ember's Munnr (per the proposed True Names) is the output surface. It currently has no tag protocol. The SAP gacha-affect rejection (per `[[sap:68_DECISION_RECORDS]]` ADR-Proposed-SAP-002) refuses *regex-parsing-for-affect-mutation*, but that rejection was about parsing tags to mutate hidden state. The CDK tag pattern parses tags to **drive declared expressive surfaces** — different teleology, different audit shape.

**Decision.** Adopt the CDK tag-extraction pattern with these constraints:

1. Ember's prompt scaffold instructs the LLM to optionally emit `[face:Name]`, `[anim:Name]`, `[voice:style]`, `[lang:code]` tags.
2. Munnr extracts the tags before TTS and animation dispatch; the visible text is the tag-stripped remainder.
3. The tag vocabulary is **declared** in `~/.ember/config/tag_vocabulary.yaml`. Unknown tags are logged (per Honest Memory) and stripped from output without affecting state.
4. Tag emission is purely *expressive*; tags **must not** mutate persistent affect, memory, or Brunnr state. The line between expressive surface and hidden state mutation is the line between the CDK pattern (adopted) and the SAP pattern (rejected).
5. The tag protocol is *negotiated*, not hardcoded — see `[[68_INVENTED_METHODS]]` #2 (Animation-Tag Negotiation) for the extension.

**Consequences.**

- ~80 LOC for the extraction + dispatch logic in `src/ember/spark/munnr/tag_protocol.py`.
- The system prompt grows by a small vocabulary block describing available tags.
- Operators can extend the vocabulary by editing the YAML.
- Avatar/voice surfaces gain a model-driven expressive channel without touching the model's output text.

**Alternatives Considered.**

- *Function-call-style tag emission* (model emits structured JSON with `face`, `anim`, `voice` fields, text in a `say` field) — viable but heavier; the in-band tag pattern is friction-light and works with any model that can follow a system-prompt convention.
- *Out-of-band tag inference* (a second LLM call analyzes the response for inferred expressions) — rejected. Extra latency; extra cost; extra opacity.
- *No tag protocol at all* — rejected. Loses the expressive surface that makes Andlit-unity (per `[[61_ANDLIT_UNITY_TIER]]`) worth shipping.

**Vow check:** Modular Authorship ✅ (tag handler is small and swappable), Honest Memory ✅ (unknown tags logged, no hidden mutation), Public-Friendliness ✅ (vocabulary YAML is operator-readable).

**Instantiates inventions:** `[[68_INVENTED_METHODS]]` #2 (Animation-Tag Negotiation), #3 (Multimodal-Pipeline-as-Resource).

**CDK references:**

- `/tmp/ChatdollKit/Scripts/Model/ModelController.cs` (tag-extraction site)
- `/tmp/ChatdollKit/Scripts/LLM/LLMContentProcessor.cs` (content-processor pipeline)

**Distinguished-from:** `[[sap:68_DECISION_RECORDS]]` ADR-Proposed-SAP-002 — that rejection was of *affect-mutating* tag parsing; this adoption is of *expressive-dispatch* tag parsing. The same regex shape; different teleology.

---

## ADR-Proposed-CDK-002 — Adopt VOICEVOX as Ember's Offline-Japanese-Voice Baseline

**Status:** Proposed (Scribe, 2026-05-25)

**Context.** The Japanese voice stack catalogued in `[[66_JAPANESE_VOICE_INTEGRATION]]` is the codex's unique gift. VOICEVOX is the keystone: open engine, local HTTP daemon, ~50 character catalogue, two-call API with editable prosody intermediate. `/tmp/ChatdollKit/Scripts/SpeechSynthesizer/VoicevoxSpeechSynthesizer.cs:55-105` shows the adapter; the engine itself is downstream (`Hiroshiba/voicevox_engine`).

Ember's Rödd (proposed) is currently undefined regarding language. Western codexes pointed at English-only stacks; SAP added Chinese via MOSS. CDK adds Japanese via the deepest local-friendly engine ecosystem the open-source voice world has produced.

**Decision.** Adopt VOICEVOX as Ember's offline-Japanese-voice baseline, with the following commitments:

1. Port the two-call adapter from `VoicevoxSpeechSynthesizer.cs:80-105` to Python at `src/ember/spark/rodd/providers/voicevox.py`. ~120 LOC.
2. The VOICEVOX engine itself is *vendored as a local service*, not embedded as a library. Operators install the engine binary; Ember speaks to its HTTP port.
3. The provider exposes `synth(text, speaker_id, style=None, prosody_overrides=None) -> AudioBytes`. The intermediate `/audio_query` JSON is preserved and exposed via `[[68_INVENTED_METHODS]]` #11 (Mora-Level Prosody Hugarsýn).
4. Speaker IDs are recorded per-utterance in the Well alongside engine version; the `[[66_JAPANESE_VOICE_INTEGRATION]]` #10 catalogue discipline applies.
5. Per-character license posture is captured in the catalogue manifest; speakers without explicit commercial-use grants are flagged before Ember speaks as them in any outward-facing context.

**Consequences.**

- ~120 LOC for the adapter + ~80 LOC for the catalogue manifest loader + ~40 LOC for the engine-version probe.
- Ember gains offline Japanese voice with mora-level prosody control.
- The catalogue manifest sets a precedent that every voice engine Ember adds must declare its characters and license posture.
- VOICEVOX engine is a deployment dependency for operators who want Japanese voice; the engine is not pulled into Ember's pip dependencies.

**Alternatives Considered.**

- *OpenAI TTS for Japanese* — rejected. Western-accent prosody, cloud-only, per-utterance leak. See `[[66_JAPANESE_VOICE_INTEGRATION]]` §7.
- *AivisSpeech as the primary Japanese baseline* — interesting; defer. Aivis is younger, smaller community catalogue, and the AIVMX bundled-license format complicates the catalogue discipline. Adopt as the *higher-quality optional layer* per ADR-Proposed-CDK-005.
- *No Japanese voice support* — rejected. The bilingual-baseline invention (per `[[68_INVENTED_METHODS]]` #1) is the codex's signature.

**Vow check:** Smallness ✅ (adapter is small; engine is downstream), Graceful Offline ✅ (local daemon, no cloud), Open Knowledge ✅ (engine is open-source), Tethered Grounding ✅ (catalogue manifest records what Ember speaks as).

**Risk:** Low. The adapter is a small port. The catalogue discipline is genuinely new but extends naturally from existing operator-config patterns.

**Instantiates inventions:** `[[68_INVENTED_METHODS]]` #1 (Bilingual-Baseline Rödd), #6 (Voice Catalogue Discipline), #7 (Offline-Japanese-Voice Fallback), #11 (Mora-Level Prosody Hugarsýn).

**CDK references:**

- `/tmp/ChatdollKit/Scripts/SpeechSynthesizer/VoicevoxSpeechSynthesizer.cs:55-105` (adapter shape)
- `/tmp/ChatdollKit/Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:1-154` (base contract)

**Downstream (not CDK):** `Hiroshiba/voicevox_engine` (the engine itself, LGPL-style, vendored by operator install).

---

## ADR-Proposed-CDK-003 — Reject Client-Side LLM API Key Pattern (Waifu Lesson Reinforced)

**Status:** Proposed (Scribe, 2026-05-25)

**Context.** Both CDK and the Waifu kit show variants of a pattern Ember has now rejected twice: **LLM API keys living in client-side configuration**. In CDK, `ChatGPTService` and `ClaudeService` both accept an `ApiKey` field as a public MonoBehaviour-serialized property — meaning the key lives in the Unity scene asset and ships with builds unless the operator manually strips it. `/tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs` (Architect cites the exact line in `[[16_LLM_SERVICE_DOMAIN]]`) holds the field; the kit's README warns about it but the warning is easy to miss.

The Waifu Codex's `[[waifu:51_SECURITY_AND_PRIVACY]]` documented the same anti-pattern in the avatar runtime. Three separate corpora (Waifu, CDK, plus the OpenAI WebRTC example) all show the client-side-key anti-pattern in the wild, and the pattern keeps getting shipped because it makes the demo work in five minutes.

**Decision.** Reject the client-side LLM API key pattern in all Ember surfaces:

1. Ember **never** stores LLM API keys in any artifact that ships to a client device (Unity build, electron build, mobile build, browser build).
2. Ember's LLM calls go through Strengr (Funi-side server) which holds keys via the secret-resolver pattern (per ADR 0011's secret-resolver shape).
3. When Ember's Unity-tier embodiment (Andlit-unity per `[[61_ANDLIT_UNITY_TIER]]`) is adopted, the Unity client talks to Ember's Funi-side server over a token-authenticated channel; the Unity client never holds an LLM key.
4. The Unity-tier authentication token is a short-lived signed session token issued by Funi to authorized Unity clients (operator's own devices on the tailnet). Per-device.
5. The ADR also forbids exposing operator-bring-your-own-key fields in mobile/Unity client UI; key entry happens server-side via `ember secrets set <provider>`.

**Consequences.**

- Unity-tier embodiment requires a Funi-side server reachable from the device. For T0 desktop where Funi runs locally, this is trivial. For T2 mobile, the device must reach Funi via tailnet or operator-configured public endpoint.
- The CDK adapter classes (`ChatGPTService`, `ClaudeService`, etc.) are studied as architecture references but their key-handling field is *not* ported; Ember's Unity client speaks to Funi instead of speaking to providers directly.
- Operators who want the CDK quickstart UX still get it via *Ember's Funi server set up locally*, which is one extra `ember serve` command but no security cost.

**Alternatives Considered.**

- *Allow client-side keys with a strong warning* — rejected. Two prior codexes refused this; the third refusal is consistent.
- *OAuth-style flow for per-device provider keys* — interesting; defer to ADR-Proposed-CDK-004 territory. Most providers do not support OAuth for inference APIs yet.
- *Encrypt keys at rest in the build* — rejected. Reverse-engineerable; false confidence.

**Vow check:** Surface Without Surveillance ✅, Defended System Prompt ✅, Honest Memory ✅, Public-Friendliness ✅ (the operator surface remains simple — operator manages keys once on Funi, not per device).

**Instantiates inventions:** Reinforces Hermes-side patterns; no new invention.

**CDK references:**

- `/tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs` (the ApiKey field — the anti-pattern site)
- `/tmp/ChatdollKit/Scripts/LLM/Claude/ClaudeService.cs` (same)

**Cross-codex:** `[[waifu:51_SECURITY_AND_PRIVACY]]`; `[[waifu:61_DECISIONS_AND_INVENTIONS]]` (Waifu-side rejection of the same anti-pattern).

---

## ADR-Proposed-CDK-004 — Adopt Multi-Provider LLM Abstraction at Strengr Layer

**Status:** Proposed (Scribe, 2026-05-25)

**Context.** CDK ships `ILLMService` at `/tmp/ChatdollKit/Scripts/LLM/ILLMService.cs` with six concrete implementations: ChatGPT, Claude, Gemini, Dify, AIAvatarKit, and Grok (via OpenAI-compat). The abstraction is well-shaped: each implementation handles its provider's specific request/response/tool-call format while exposing a uniform call surface to the rest of the kit. This is the *correct* shape for multi-provider support, and it stands in contrast to SAP's *simulation* layer (`ClaudeAsOpenAI.py`) which pretends providers are interchangeable.

Hermes's ADR-Proposed-Funi-001 already commits Ember to a profile + transport split for LLM providers. CDK's `ILLMService` is a strong evidence point for that decision; the architectural shape it documents in 18k LOC of mature, multi-provider production code says this is the right pattern.

**Decision.** Adopt the multi-provider abstraction at Ember's Strengr layer with these commitments:

1. `Strengr.LLMProvider` is the Python equivalent of `ILLMService` — a protocol that each provider implements natively, no simulation layer.
2. Providers ship as separate optional extras: `ember-agent[claude]`, `ember-agent[openai]`, `ember-agent[gemini]`, `ember-agent[dify]`, `ember-agent[ollama]`, `ember-agent[anthropic]`, etc.
3. Function-call format adaptation is *per-provider*, not flattened (per ADR-Proposed-CDK-005).
4. Provider selection is config-driven; operator declares default provider plus fallback chain in `~/.ember/config/strengr.yaml`.
5. Provider divergence is *visible* — failed-to-emit-tool-call, format-mismatch, unsupported-feature errors are typed and reach Hugarsýn introspection (per `[[sap:66_INVENTED_METHODS]]` #5 extension).

**Consequences.**

- More native transports to write (one per provider) — but each is small (~200-400 LOC).
- The Hermes profile + transport split shape is reinforced by CDK evidence.
- Token counts and tool-call shapes remain honest per provider.
- The fallback chain is visible to the operator; outages are graceful.

**Alternatives Considered.**

- *Adopt SAP's simulation pattern* — rejected (per ADR-Proposed-SAP-008).
- *Single provider with vendor lock-in* — rejected per Pluggable Storage Vow extended to LLM provider.
- *LangChain / LiteLLM as the abstraction layer* — interesting; defer. CDK's evidence is that direct adapters work; adding an extra library layer is friction without clear gain.

**Vow check:** Modular Authorship ✅, Pluggable Storage ✅ (extended to provider), Honest Memory ✅, Graceful Offline ✅ (fallback chain).

**Instantiates inventions:** `[[68_INVENTED_METHODS]]` #4 (Provider-Divergence Adapter Pattern).

**CDK references:**

- `/tmp/ChatdollKit/Scripts/LLM/ILLMService.cs` (the protocol)
- `/tmp/ChatdollKit/Scripts/LLM/LLMServiceBase.cs` (the shared base)
- `/tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs` (provider concrete)
- `/tmp/ChatdollKit/Scripts/LLM/Claude/ClaudeService.cs` (provider concrete)
- `/tmp/ChatdollKit/Scripts/LLM/Gemini/GeminiService.cs` (provider concrete)

**Hermes cross-ref:** ADR-Proposed-Funi-001 (profile + transport split).

---

## ADR-Proposed-CDK-005 — Adopt Function-Call Format Adapter Pattern (Per-Provider)

**Status:** Proposed (Scribe, 2026-05-25)

**Context.** Multi-provider LLMs disagree about tool/function-call format more than they agree. OpenAI uses `tool_calls` with `function: { name, arguments }`. Anthropic uses `tool_use` blocks with `input` field. Gemini uses `functionCall` with `args`. Older Claude versions used XML-style tags. The CDK adapters each handle their provider's format natively; `ChatGPTService` parses `tool_calls`, `ClaudeService` parses `tool_use`, and so on. The Auditor will catalog the divergence in `[[53_MULTI_LLM_CONSISTENCY]]`.

Ember's Strengr needs the same per-provider format adaptation. The naive approach is to normalize everything to one shape (say, OpenAI's) at the Strengr/Funi boundary. The CDK evidence is that the normalize-to-one-shape approach is lossy at the edges: Claude's `tool_use` carries a stop reason that OpenAI's `tool_calls` does not; Gemini's `functionCall` carries safety-block annotations that the others lack.

**Decision.** Adopt the per-provider function-call format adapter pattern:

1. Each provider's adapter parses native tool-call format into a *rich* internal representation that preserves provider-specific metadata.
2. The internal representation is a typed dataclass with `provider_specific: dict[str, Any]` for fields that don't generalize.
3. Tool dispatch downstream of Strengr consumes the rich representation; downstream callers can read the `provider_specific` block when needed.
4. When emitting back to a provider for tool result return, the adapter serializes the rich form into that provider's expected shape.
5. Cross-provider tool calling (model A on turn N → tool result → model B on turn N+1) is *supported* but the operator gets a typed warning that provider-specific metadata may be dropped at the boundary.

**Consequences.**

- ~100 LOC per provider for the adapter (in addition to the base provider port).
- Tool calls are *not* lossy unless they cross provider boundaries.
- Cross-provider warning surface is small but visible.
- Ember can choose to send the model the most-informative tool error annotation each provider supports (e.g., Anthropic's stop reasons).

**Alternatives Considered.**

- *Normalize everything to OpenAI shape* — rejected. Loses Claude stop reasons and Gemini safety annotations.
- *Normalize to Claude shape* — rejected. Same loss in the other direction.
- *Carry raw provider JSON everywhere* — rejected. Downstream code becomes brittle to provider format changes.

**Vow check:** Honest Memory ✅ (provider metadata preserved), Modular Authorship ✅ (per-provider adapter), Defended System Prompt ✅ (no opaque cross-provider normalization).

**Instantiates inventions:** `[[68_INVENTED_METHODS]]` #4 (Provider-Divergence Adapter Pattern).

**CDK references:**

- `/tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs` (function_call parsing)
- `/tmp/ChatdollKit/Scripts/LLM/Claude/ClaudeService.cs` (tool_use parsing)
- `/tmp/ChatdollKit/Scripts/LLM/Gemini/GeminiService.cs` (functionCall parsing)
- `/tmp/ChatdollKit/Scripts/LLM/ToolBase.cs` (the abstract tool surface)

---

## ADR-Proposed-CDK-006 — Three-Corpus Triangulation as Standing Design Discipline

**Status:** Proposed (Scribe, 2026-05-25)

**Context.** Ember's design has now been informed by three embodiment-axis corpora: SAP (electron desktop, Wave 3), Waifu (cloud streaming, Wave 4), and CDK (Unity-native local, Wave 5). Each contributed a different axis of evidence. The triangulation is not a one-time event; it is a *standing discipline* that should guide future codex selection and design decisions.

The Cartographer's `[[60_TRIANGULATION]]` formalized the three axes for embodiment. This ADR ratifies the *discipline* of triangulation itself.

**Decision.** Adopt three-corpus triangulation as a standing design discipline:

1. Before any major Ember subsystem decision (True Name addition, Vow proposal, major slice plan revision), the keeper checks whether **three independent corpora** have been studied for the relevant design space.
2. If three corpora are not yet studied, the decision is deferred until a third corpus has been corpus-mined or the keeper explicitly waives the discipline with rationale.
3. The three corpora must be *axis-distinct* — they must each be teaching something different about the same design space.
4. The discipline applies to design spaces beyond embodiment: memory (Hermes + ChatMemory + ??? = three corpora needed), function-calling (Hermes + SAP + CDK ✓), VAD/STT (SAP + CDK + ???), etc.
5. The Vow this discipline ratifies — informally — is **Wisdom Through Triangulation**.

**Consequences.**

- Future codex mining is targeted at *filling the triangle* rather than at random source selection.
- Slice plan revisions are gated on triangulation completion for the relevant design space.
- The discipline becomes a Scribe-checked precondition for any synthesis-layer decision.
- Documentation gains a *triangulation register* in `docs/triangulation_register.md` (or in this codex's `meta/CROSS_AGENT_NOTES.md`) tracking which design spaces have which corpora.

**Alternatives Considered.**

- *Two-corpus comparison as standard* — too thin; produces dichotomies rather than coverage.
- *Five-corpus minimum* — too heavy; slows decisions for marginal coverage gain after three.
- *No formal discipline; informal corpus reading* — rejected. Ember's slice plan ratifications already feel the value of triangulation; ratifying the discipline makes it visible.

**Vow check:** Honest Memory ✅ (the discipline says *don't pretend we know more than we do*), Open Knowledge ✅, Tethered Grounding ✅ (decisions cite corpora evidence).

**Instantiates inventions:** `[[68_INVENTED_METHODS]]` #5 (Six-Codex-Braid Discipline; this ADR is the three-corpus version, the six-codex version is the synthesis-layer extension).

**Risk:** Procedural, not technical. The risk is that the discipline becomes paperwork rather than wisdom. Mitigation: the Cartographer keeps the register honest; the Scribe audits the register at each Wave close.

---

## ADR-Proposed-CDK-007 — Adopt ChatMemory Integration Pattern for Hjarta (with Brunnr Tether)

**Status:** Proposed (Scribe, 2026-05-25)

**Context.** CDK's `ChatMemoryIntegrator` (Architect-documented in `[[1A_MEMORY_DOMAIN]]`) ties the kit to **ChatMemory** (`uezo/chatmemory`), a sister project that provides episodic + factual memory storage via a FastAPI server. The integration shape — Unity client speaks to a memory service over HTTP, the service holds two memory stores (episodic conversational and factual extracted) — is a clean example of *embodiment runtime separated from memory substrate*.

Ember's Hjarta (proposed True Name) is the memory + affect surface. The Cartographer's `[[65_MEMORY_INTEGRATION]]` proposes adopting the ChatMemory two-store pattern. This ADR is the **decision** to adopt that pattern, with the additional constraint that all ChatMemory storage tethers to Brunnr/Well so the memory is not orphaned from the canonical knowledge substrate.

**Decision.** Adopt the ChatMemory two-store pattern for Hjarta with these commitments:

1. Hjarta exposes two storage spaces:
   - **Episodic**: conversational turns with timestamps + persona_id + session_id, recent-bias retention, TTL-managed
   - **Factual**: LLM-extracted assertions about the operator (preferences, relations, schedule, declared facts) with provenance back to source episodes
2. Both stores write through Brunnr — the Well is the canonical store, Hjarta's local cache is an optimization.
3. The factual store's extraction step (the LLM call that pulls "the operator likes spicy food" out of conversation) emits **receipt-bound provisional memory** per `[[sap:66_INVENTED_METHODS]]` #14 — extracted facts land in a pending tray until operator confirms.
4. The ChatMemory FastAPI server pattern is *studied* (Forge-B's `[[38_CHATMEMORY_INTEGRATION]]` covers the architecture), but Ember's implementation lives in Hjarta directly — Ember does not run a separate ChatMemory daemon.
5. The Apache-2.0 attribution applies: the schema design and the two-store split are adopted with credit; the code is reimplemented in Python.

**Consequences.**

- ~600 LOC for the two-store implementation + ~200 LOC for the Brunnr tether + ~150 LOC for the provisional-tray hook.
- Hjarta's design crystallizes; the True Name moves from proposed to ratifiable.
- Operators can ask Ember "what do you remember about me?" and get a real answer, anchored in Well chunks.
- The factual-extraction step is opt-in per session (operator can disable).

**Alternatives Considered.**

- *Single-store memory (everything in episodic)* — rejected. The factual layer is what makes the memory queryable beyond recency.
- *Run ChatMemory daemon as separate service* — rejected. Adds operational complexity for little gain when Ember is already a Python service.
- *Embedding-only memory (no extraction step)* — interesting; the Skein/Skry methods (per `[[ember:project_skein_skry]]`) point at this direction. Defer to a future ADR; embedding-only is a complement to the two-store pattern, not a replacement.

**Vow check:** Tethered Grounding ✅ (Brunnr is canonical), Honest Memory ✅ (provisional tray gates inferred memory), Pluggable Storage ✅ (Brunnr abstraction holds), Public-Friendliness ✅ (operator-facing memory CLI).

**Instantiates inventions:** `[[68_INVENTED_METHODS]]` #8 (Multi-Device Persona Handoff — the persona-keyed memory enables this), and reinforces `[[sap:66_INVENTED_METHODS]]` #14.

**CDK references:**

- `/tmp/ChatdollKit/Scripts/AIAvatar.cs` (ChatMemoryIntegrator hook point — Architect cites exact lines)
- `https://github.com/uezo/chatmemory` (sister project, Apache-2.0)

**SAP cross-ref:** `[[sap:66_INVENTED_METHODS]]` #14 (Receipt-Bound Provisional Memory), `[[sap:66_INVENTED_METHODS]]` #8 (Tethered Affect Anchoring — applies to factual extraction).

---

## ADR-Proposed-CDK-008 — Adopt Silero VAD as Ember's Default Voice Detection

**Status:** Proposed (Scribe, 2026-05-25)

**Context.** CDK ships `/tmp/ChatdollKit/Scripts/SpeechListener/SileroVADProcessor.cs` — a Unity integration of **Silero VAD**, an ONNX-runtime ML-based voice-activity detector. Silero VAD is a small (~1MB) ONNX model that classifies 30ms audio frames as speech-or-not with low CPU cost and high accuracy. The kit treats it as the production-grade VAD, alongside simpler amplitude-threshold VAD options.

Ember's SpeechListener (will be part of Munnr's input surface, or a future True Name for the listener role) needs a VAD when voice input is enabled. SAP used MOSS's own pipeline; Waifu deferred to browser-VAD. CDK's Silero choice is the most thoughtful of the three.

**Decision.** Adopt Silero VAD as Ember's default voice-activity detector:

1. Port the Silero VAD integration pattern from `SileroVADProcessor.cs` to Python at `src/ember/spark/munnr/listener/silero_vad.py` (or a future Hlustir/listener subsystem). The Python port uses `onnxruntime` + the published Silero VAD ONNX model.
2. Silero VAD is the default for T0/T1/T2 (workstation, laptop, phone — all can run ONNX inference).
3. T3 (Pi 5) falls back to amplitude-threshold VAD if onnxruntime overhead is too high (operator-configurable).
4. T4 has no voice input; the VAD is moot.
5. The VAD's probability output is exposed via Hugarsýn introspection so the operator can see *why* Ember thinks it heard speech.

**Consequences.**

- ~150 LOC for the integration + the ~1MB ONNX model is a vendored asset.
- Speech detection is meaningfully better than amplitude-threshold.
- The kit's `onnxruntime` dependency is added to the voice-input optional extra.
- Cross-platform: works on all desktop OSes and on Pi via `onnxruntime` Linux ARM builds.

**Alternatives Considered.**

- *WebRTC VAD* — older, simpler, less accurate than Silero in noisy environments.
- *Amplitude-threshold only* — rejected as default. Used as fallback only.
- *Whisper-based VAD* — rejected. Whisper is too heavy to run as a VAD; the right tool is the small dedicated VAD model.

**Vow check:** Smallness ✅ (small ONNX model), Modular Authorship ✅ (VAD is swappable), Pluggable Storage ✅ (extended to VAD selection).

**Instantiates inventions:** None new; this is a clean adoption.

**CDK references:**

- `/tmp/ChatdollKit/Scripts/SpeechListener/SileroVADProcessor.cs` (Unity integration)
- `https://github.com/snakers4/silero-vad` (the upstream VAD model, MIT-licensed)

---

## ADR-Proposed-CDK-009 — Adopt uLipSync as Andlit-Unity Lip-Sync (Conditional on Andlit-Unity Adoption)

**Status:** Proposed (Scribe, 2026-05-25)

**Context.** uLipSync is the Unity-native lip-sync library CDK uses for vowel detection and mouth-shape synthesis. The integration (Forge-A's `[[35_LIP_SYNC]]` covers the execution path) reads the audio output of the TTS layer and drives blendshape keyframes on the VRM avatar's mouth. uLipSync's vowel-detection approach is language-agnostic — it works on any audio — though tuning differs by language.

This ADR is **conditional** on the Andlit-unity tier being adopted via ADR-Proposed-CDK-010. If Andlit-unity is not adopted, this ADR is moot.

**Decision.** *Conditional* — if Andlit-unity is adopted per ADR-Proposed-CDK-010, also adopt uLipSync as the lip-sync substrate for the Unity-tier embodiment:

1. The Unity-tier embodiment uses uLipSync verbatim from the kit (it is Apache-2.0 in its CDK distribution, though the underlying uLipSync library is MIT-licensed by hecomi/uLipSync).
2. Per-language tuning profiles live in the Unity asset bundle as `LipSyncProfile_<lang>.asset`. Default profiles for English and Japanese ship; operators can add more.
3. The lip-sync timing tethers to the TTS prefetch (per `[[33_TTS_PREFETCH]]`); audio start triggers lip-sync start.
4. T1 fallback for lip-sync (when uLipSync runs poorly on integrated GPU) is a simpler amplitude-driven open/close shape.
5. T2/T3/T4 do not run uLipSync.

**Consequences.**

- Unity-tier embodiment has production-quality lip-sync from day one.
- The asset-bundle dependency on uLipSync is added.
- Per-language profile work is a small operator-facing surface.

**Alternatives Considered.**

- *Wave2Lip or other ML-driven lip-sync* — rejected. Heavier; needs GPU inference; uLipSync is the established Unity choice.
- *No lip-sync* — rejected. The Andlit-unity tier exists *because* lip-sync + animation + voice together deliver an embodiment that the electron tier cannot.
- *Custom lip-sync* — rejected. Reinventing the wheel.

**Vow check:** Smallness ✅ (uLipSync is small), Modular Authorship ✅, Embodied Honesty ✅ (mouth shape follows real audio).

**Instantiates inventions:** None new; clean adoption pending Andlit-unity ratification.

**CDK references:**

- `/tmp/ChatdollKit/Scripts/Model/` (the lip-sync hook site)
- `https://github.com/hecomi/uLipSync` (upstream library, MIT)

---

## ADR-Proposed-CDK-010 — Unity as Ember's Optional Third-Runtime Embodiment Path (Not Primary)

**Status:** Proposed (Scribe, 2026-05-25)

**Context.** The headline question this codex exists to answer is: **should Ember adopt Unity as a third embodiment runtime, alongside electron-local (SAP) and cloud-streaming (Waifu)?** The Cartographer's `[[61_ANDLIT_UNITY_TIER]]` makes the architectural case; this ADR is the *decision* whether to take it.

The case for Unity-tier embodiment:

- Cross-platform reach unmatched by any other tier (Windows, Mac, Linux, iOS, Android, VR, AR, WebGL)
- Mature animation, expression, lip-sync ecosystem already wired (VRM, uLipSync, Animator)
- Apache-2.0 reference implementation (CDK) for the integration
- The same persona_id can speak as Ember on desktop, laptop, mobile, and headset — true cross-device companion

The case against Unity-tier embodiment:

- Engine commitment: Unity is a heavy substrate; learning curve is real
- Binary size: Unity builds are 30MB+ minimum (vs ~5MB electron, ~0 for cloud)
- Tooling stack: C#, Unity-specific patterns (MonoBehaviour, ScriptableObject), asmdef, asset pipeline
- Version coupling: Unity LTS versions move; CDK couples to specific Unity LTS
- Two-language codebase: Ember Python + Unity C# requires cross-language interface discipline

**Decision.** Adopt Unity as Ember's **optional, third-runtime** embodiment path, with these commitments:

1. Unity-tier is **never** the primary runtime. The primary runtime remains the Python core (Funi + Strengr + Brunnr + Smiðja + Hjarta + Munnr) — Unity is an optional embodiment client that talks to the core.
2. Unity-tier embodiment is named **Andlit-unity** as a sub-name of the proposed Andlit True Name (Andlit-electron = SAP-shape, Andlit-realtime = Waifu-shape, Andlit-unity = CDK-shape).
3. Unity-tier ships as a separate downloadable artifact, not in the main pip install. Operators who want it download a Unity client app from `ember-unity-client` releases.
4. The Unity client speaks to Ember's Funi-side server over WebSocket + signed token (per ADR-Proposed-CDK-003 key handling).
5. The Unity client is **stateless** except for local rendering state; all conversation state, memory, affect, persona, tool dispatch lives server-side.
6. Slice 6+ at the earliest. The Wave 5 slice (`[[6B_EMBER_WAVE_5_SLICE]]`) ratifies the *protocol* between Funi and Unity client, not the Unity client itself.
7. The smaller-but-real *next-step* is the protocol — Funi exposes a `unity-client-protocol` WebSocket surface. The Unity client can then be built by anyone (including a community contributor) without requiring Ember's core team to take on Unity expertise.

**Consequences.**

- Ember has a path to phones, headsets, and the wider game-engine ecosystem without taking on Unity as a primary engineering responsibility.
- The protocol-first split means the Unity client can be a separate project (or a community project) with its own release cadence.
- Slice 5 (Wave 5 in `[[6B_EMBER_WAVE_5_SLICE]]`) ships the *protocol*, not the *client*. The client may not arrive for another year — that's acceptable.
- The Apache-2.0 attribution applies to any CDK-derived patterns the Unity client borrows.

**Alternatives Considered.**

- *Unity as primary runtime* — rejected. Too heavy a commitment for a project where the core value is Python-side knowledge + Norse-Pagan philosophy.
- *Skip Unity entirely* — rejected. The mobile + VR + AR reach is too valuable, and the Apache-2.0 reference implementation makes the path open.
- *Godot or other open-source engine instead of Unity* — interesting; defer. Godot's mobile/XR story is younger than Unity's; CDK is Unity-only; the triangulation evidence is for Unity specifically.
- *Build Unity client in slice 5 directly* — rejected. Too much engineering surface for one slice. Protocol-first allows iteration.

**Vow check:** Smallness ✅ (core stays Python; Unity is optional), Modular Authorship ✅ (Unity is a separate artifact), Pluggable Storage ✅ (extended to embodiment runtime), Tiered Presence ✅ (Unity is a tier among tiers, not the tier).

**Risk:** Medium-high. Unity adoption — even as optional runtime — adds a learning curve for the operator who wants to extend the Unity client. The protocol-first split mitigates this by making the Unity work optional for the core team and community-buildable for those who want it.

**Instantiates inventions:** `[[68_INVENTED_METHODS]]` #8 (Multi-Device Persona Handoff), #9 (Tier-Aware Embodiment Selection), #10 (Cross-Runtime Persona Portability).

**CDK references:** The entire kit — Unity-tier embodiment as a *reference implementation* of what an Andlit-unity could look like.

---

## ADR-Proposed-CDK-011 — Reject SocketServer Default-Bind-All; Adopt Tailnet-Only Default

**Status:** Proposed (Scribe, 2026-05-25)

**Context.** CDK's `SocketServer` (`/tmp/ChatdollKit/Scripts/Network/SocketServer.cs`) opens a local TCP port for external control. The default bind is permissive — the Auditor's `[[27_SOCKET_PROTOCOL]]` will catalog the exact bind posture. The pattern is useful for development (companion apps can drive the avatar) but the default permits any process or any host that can route to the port.

Ember has a standing memory note that services should bind to the tailnet interface by default, with proper auth, rather than localhost or 0.0.0.0 (per `[[ember:feedback_tailnet_access]]`). This memory note is the keeper's standing preference.

**Decision.** When/if Ember exposes a SocketServer-like remote-control surface (likely the Funi-to-Unity-client WebSocket per ADR-Proposed-CDK-010):

1. Default bind is to the **tailscale interface** if tailscale is detected; otherwise to a specific operator-configured interface; *never* to 0.0.0.0 by default.
2. Authentication is required. The token is operator-issued; default-deny if no token configured.
3. The port number is documented in `~/.ember/config/network.yaml`. No silent default port.
4. The SocketServer surface is **opt-in** per ADR-Proposed-CDK-004 default-quiet posture (SAP-004 carried forward).
5. The bind is logged at startup; operators see the bind details in `ember status`.

**Consequences.**

- Unity-client connectivity requires tailnet (typical operator deployment) or explicit configuration.
- The exposure surface is small; only operator's own devices can reach it by default.
- Configuration is visible; no hidden defaults.

**Alternatives Considered.**

- *Localhost-only* — rejected. Defeats the multi-device case that motivates Unity-tier.
- *Default 0.0.0.0 with token* — rejected. The token is useful but the bind-default-permissive posture is contrary to the standing memory.
- *No network bind* — rejected. Unity-tier needs the path.

**Vow check:** Surface Without Surveillance ✅, Smallness ✅, Public-Friendliness ✅ (bind is visible at startup).

**Instantiates inventions:** Reinforces `[[ember:feedback_tailnet_access]]` standing preference into an ADR.

**CDK references:**

- `/tmp/ChatdollKit/Scripts/Network/SocketServer.cs` (the anti-pattern to learn from)
- `/tmp/ChatdollKit/Scripts/Network/JavaScriptMessageHandler.cs` (the WebGL bridge — separate surface)

---

## ADR-Proposed-CDK-012 — Adopt Multimodal-Pipeline-as-Resource as Hjarta+Munnr Coordination Pattern

**Status:** Proposed (Scribe, 2026-05-25)

**Context.** CDK's biggest single architectural insight — bigger than any single subsystem — is that **the STT → LLM → TTS + animation + face-tags + lip-sync pipeline is one orchestrated resource with lifecycle**, not a chain of independent calls. `AIAvatar.cs` (Architect's `[[11_AIAVATAR_DOMAIN]]` covers the dispatch logic) treats the multimodal pipeline as a coordinated resource: when the user starts speaking, the pipeline opens; when the response is fully delivered (audio finished + animation finished + state settled), the pipeline closes.

Cartographer's `[[63_MULTIMODAL_PIPELINE]]` formalizes the architecture. This ADR ratifies the *pattern* as a coordination discipline for Ember's Hjarta + Munnr interaction.

**Decision.** Adopt the multimodal-pipeline-as-resource pattern:

1. Ember defines a `Pipeline` resource that encapsulates one full turn: STT (if voice input) → LLM call → TTS + animation + face-tags (per ADR-Proposed-CDK-001).
2. The `Pipeline` has explicit lifecycle: `open()`, `progress(event)`, `barge_in(reason)`, `close(reason)`.
3. Barge-in (user interrupts mid-TTS) is a *first-class lifecycle event*, not an exception. The CDK barge-in pattern (Forge-A's `[[37_BARGE_IN_INTERRUPT]]`) is studied for the cancel-and-replace semantics.
4. The Pipeline emits typed events to Hugarsýn so the operator can introspect mid-turn.
5. The Pipeline is the unit of operator audit — each turn's pipeline lifecycle is one audit record.

**Consequences.**

- ~400 LOC for the Pipeline class + ~150 LOC for the lifecycle dispatcher + audit hooks.
- Mid-turn introspection becomes possible; the operator can see *what stage* a slow turn is stuck in.
- Barge-in is robust; the cancel-and-replace semantics are tested rather than ad-hoc.
- The Andlit-unity protocol (per ADR-Proposed-CDK-010) speaks in terms of Pipeline events, not raw socket messages.

**Alternatives Considered.**

- *Treat each stage as independent calls* — rejected. Barge-in becomes a nightmare; cross-stage coordination becomes implicit and brittle.
- *Pipeline as actor* — interesting; the actor model is heavier than needed for a single-turn lifecycle. Defer.
- *No pipeline abstraction; orchestrate ad-hoc* — rejected. The CDK evidence is clear that the orchestration pays off.

**Vow check:** Modular Authorship ✅ (pipeline failure contained), Honest Memory ✅ (audit unit is the pipeline), Public-Friendliness ✅ (introspection visible), Graceful Offline ✅ (pipeline can fail any stage gracefully).

**Instantiates inventions:** `[[68_INVENTED_METHODS]]` #3 (Multimodal-Pipeline-as-Resource).

**CDK references:**

- `/tmp/ChatdollKit/Scripts/AIAvatar.cs` (the pipeline orchestrator)
- `/tmp/ChatdollKit/Scripts/Dialog/` (state machine that the pipeline runs through)

---

## Summary Table — All Proposed ADRs

| ID | Topic | Slice (est.) | Affects Vows | Risk | Inventions |
|---|---|---|---|---|---|
| CDK-001 | Adopt tag-extraction for Munnr | 4 | Modular Authorship, Honest Memory | Low | `[[68]]` #2, #3 |
| CDK-002 | Adopt VOICEVOX baseline | 5 | Graceful Offline, Tethered Grounding | Low | `[[68]]` #1, #6, #7, #11 |
| CDK-003 | Reject client-side LLM key | 3 | Surface Without Surveillance, Defended System Prompt | Low | (reinforcement) |
| CDK-004 | Multi-provider LLM abstraction | 3-4 | Modular Authorship, Pluggable Storage | Low | `[[68]]` #4 |
| CDK-005 | Per-provider function-call adapter | 4 | Honest Memory, Defended System Prompt | Low | `[[68]]` #4 |
| CDK-006 | Three-corpus triangulation as discipline | meta | Honest Memory, Open Knowledge | Procedural | `[[68]]` #5 |
| CDK-007 | ChatMemory pattern for Hjarta | 5 | Tethered Grounding, Honest Memory | Medium | `[[68]]` #8 |
| CDK-008 | Silero VAD default | 4 | Smallness, Modular Authorship | Low | (none new) |
| CDK-009 | uLipSync for Andlit-unity (cond.) | 6+ | Smallness, Embodied Honesty | Low (conditional) | (none new) |
| CDK-010 | Unity as optional third runtime | 5 (protocol) / 6+ (client) | Smallness, Pluggable Storage, Tiered Presence | Medium-high | `[[68]]` #8, #9, #10 |
| CDK-011 | Tailnet-only network default | 4 | Surface Without Surveillance, Smallness | Low | (reinforcement) |
| CDK-012 | Multimodal-pipeline-as-resource | 4-5 | Modular Authorship, Honest Memory | Medium | `[[68]]` #3 |

---

## What This Means for Ember

**True Names affected:** All six, plus the proposed Andlit-unity sub-name.

- Funi: CDK-003, CDK-004, CDK-011, CDK-012 (the orchestration and security backbone)
- Strengr: CDK-004, CDK-005 (the LLM provider abstraction)
- Brunnr: CDK-002 (voice catalogue manifest), CDK-007 (ChatMemory two-store)
- Smiðja: (light touch via tool dispatch shape — CDK-005)
- Hjarta: CDK-007 (memory two-store), CDK-012 (pipeline coordination)
- Munnr: CDK-001 (tag protocol), CDK-002 (Rödd-Japanese), CDK-008 (VAD), CDK-009 (uLipSync conditional), CDK-012 (pipeline orchestration)
- Andlit-unity (proposed sub-name): CDK-010 (the existence ADR)

**Vows touched:**

- *Most reinforced:* **Modular Authorship** (CDK-001, CDK-004, CDK-008, CDK-010, CDK-011, CDK-012) — the architecture of "small swappable pieces" gets evidence from CDK's mature codebase.
- *Most strengthened:* **Pluggable Storage** (CDK-002, CDK-004, CDK-007, CDK-010) — the abstraction now covers voice provider, LLM provider, memory provider, *and* embodiment runtime.
- *Most clarified:* **Tiered Presence** (CDK-009, CDK-010 sub-tiers; CDK-008 VAD per-tier) — the tier ladder gains the Unity-runtime tier.
- *Most watched:* **Surface Without Surveillance** (CDK-003, CDK-011) — the key-handling discipline now spans three corpora's worth of rejection.

**Concrete next step for the keeper:**

1. Review each ADR-Proposed above. The twelve cluster naturally:
   - **Wave 5 slice candidates** (small, ready): CDK-001 (tag protocol), CDK-003 (key rejection ratification), CDK-004 (multi-provider abstraction), CDK-006 (triangulation discipline), CDK-008 (Silero VAD), CDK-011 (tailnet-only).
   - **Wave 5 / Wave 6 candidates** (medium): CDK-002 (VOICEVOX baseline), CDK-005 (function-call adapter), CDK-007 (ChatMemory pattern), CDK-012 (multimodal pipeline).
   - **Wave 6+ candidates** (larger): CDK-010 (Unity protocol; client deferred).
   - **Conditional**: CDK-009 (only if CDK-010 ratifies).
2. For each, decide: Accept, Defer, or Reject.
3. For Accept: copy to `docs/decisions/NNNN-<slug>.md` with appropriate ADR number; status becomes Ratified; reference this Codex doc.
4. For Defer: note in `[[69_SLICE_PLAN_REVISIONS]]` revision; revisit at next slice ratification.

**Adopt:** All twelve ADRs are *Proposed*, not yet Ratified. The Adopt list is empty until the keeper ratifies; on ratification, items shift to the Ember-side ADR ledger.

**Adapt:** (none — each ADR is a binary accept/reject after ratification)

**Avoid:** The anti-patterns ADRs CDK-003 and CDK-011 reject explicitly: client-side LLM keys; default-permissive network bind.

**Invent:** `[[68_INVENTED_METHODS]]` catalogues the inventions these ADRs reference. The most consequential invention these ADRs collectively *enable* is **multi-device persona portability** (`[[68]]` #8) — the property that a single Ember persona can speak through electron at the desk, Unity client on the phone, and cloud-streaming on a friend's browser without splitting identity.

---

**Cross-references:**

- `[[60_TRIANGULATION]]` — Cartographer's three-axis read; the foundation these ADRs build on.
- `[[61_ANDLIT_UNITY_TIER]]` — Cartographer's Andlit-unity argument that CDK-010 ratifies.
- `[[63_MULTIMODAL_PIPELINE]]` — Cartographer's pipeline architecture that CDK-012 ratifies.
- `[[65_MEMORY_INTEGRATION]]` — Cartographer's ChatMemory two-store argument that CDK-007 ratifies.
- `[[66_JAPANESE_VOICE_INTEGRATION]]` — Scribe's voice teaching that CDK-002 builds on.
- `[[68_INVENTED_METHODS]]` — the inventions these ADRs instantiate.
- `[[69_SLICE_PLAN_REVISIONS]]` — slice-shaped bundling.
- `[[6A_INTEGRATION_ROADMAP]]` — phasing across the codex constellation.
- `[[6B_EMBER_WAVE_5_SLICE]]` — concrete Wave 5 slice proposal.
- `[[sap:68_DECISION_RECORDS]]` — SAP-side ADR-Proposed records (the priors these extend).
- `[[waifu:61_DECISIONS_AND_INVENTIONS]]` — Waifu-side ADR-Proposed records (the immediate predecessors).
- `[[hermes:60_HERMES_VS_EMBER_CROSSWALK]]` — Hermes-side foundation for CDK-004, CDK-005.

The decisions wait on the keeper. The records preserve the reasoning so they can wait without rotting.

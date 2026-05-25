---
codex_id: 04_VISION_SYNTHESIS
title: Vision Synthesis — Post-CDK Ember and the Closing of the Triangulation
role: Skald
layer: Vision
status: draft
cdk_source_refs:
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:15
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:25-33
  - /tmp/ChatdollKit/Scripts/Model/ModelController.cs:247-289
  - /tmp/ChatdollKit/Scripts/LLM/LLMServiceBase.cs:100-117
  - /tmp/ChatdollKit/Scripts/LLM/ILLMService.cs
  - /tmp/ChatdollKit/Scripts/SpeechSynthesizer/VoicevoxSpeechSynthesizer.cs:13
  - /tmp/ChatdollKit/Scripts/SpeechSynthesizer/StyleBertVits2SpeechSynthesizer.cs:15
  - /tmp/ChatdollKit/Extension/ChatMemory/ChatMemoryIntegrator.cs
  - /tmp/ChatdollKit/Extension/SileroVAD/SileroVADProcessor.cs
  - /tmp/ChatdollKit/LICENSE
ember_subsystem_targets: [Andlit, Rödd, Hjarta, Hugarsýn, Veizla, Funi, Brunnr, Smiðja, Strengr, Munnr]
cross_refs:
  - 00_vision/00_OVERTURE
  - 00_vision/01_CDK_ESSENCE
  - 00_vision/02_UNITY_AS_RUNTIME
  - 00_vision/03_ANTI_CDK
  - 10_domain/10_DOMAIN_MAP
  - 60_synthesis/60_TRIANGULATION
  - 60_synthesis/61_ANDLIT_UNITY_TIER
  - 60_synthesis/62_MOBILE_AND_XR_TIER
  - 60_synthesis/65_MEMORY_INTEGRATION
  - 60_synthesis/66_JAPANESE_VOICE_INTEGRATION
  - 60_synthesis/68_INVENTED_METHODS
  - 60_synthesis/69_SLICE_PLAN_REVISIONS
  - 60_synthesis/6B_EMBER_WAVE_5_SLICE
  - sap:04_VISION_SYNTHESIS
  - sap:60_TRUE_NAME_REASSIGNMENT
  - sap:61_NEW_VOWS
  - sap:63_PERFORMANCE_TIER_ENGINE
  - waifu:01_VISION_SYNTHESIS
  - waifu:60_REALTIME_TIER_FOR_ANDLIT
  - hermes:04_VISION_SYNTHESIS
---

# Vision Synthesis — Post-CDK Ember and the Closing of the Triangulation

> *Five sisters have spoken now. The fifth closed a shape three of them had been drawing without naming. The shape is a triangle, and the triangle is the embodiment axis, and Ember is at the centroid — not because she chose to be, but because she refused to choose any single corner.*
> — Sigrún Ljósbrá, at the close of Wave 5's Vision

## I. What the four prior docs left in our hands

Four documents preceded this one. They left us with four gifts.

`[[00_OVERTURE]]` named the stance: ChatdollKit is the *Fifth Reading*, after Hermes (the largeness reading), Peer (the apprentice's mirror), SAP (the local-embodiment axis), and the Waifu kit (the cloud-streaming axis). The Fifth Reading closes the *third position on the embodiment axis* — Unity-native local — and surfaces the Japanese voice ecosystem that the prior corpora had pretended did not exist. The codex's job: complete the three-corpus embodiment triangulation.

`[[01_CDK_ESSENCE]]` stripped ChatdollKit to five intents — *doll-as-companion* (most realized), *the voice is the body* (well realized, Japanese-flavored), *the face is honest-by-typed-tag-protocol* (partially realized — the typing helps but the underlying *LLM-authors-emotion* anti-pattern persists), *multi-platform reach as ground truth* (well realized, engine-costly), *modular subsystem optionality* (well realized, the bar Ember should match). The deepest essence: ChatdollKit's central class is named `AIAvatar` — *the doll has a name, the named-particular discipline is its core*.

`[[02_UNITY_AS_RUNTIME]]` walked the trade-off honestly. Six gives — cross-platform reach as one codebase, mature animation infrastructure, asset ecosystem, mobile + XR support, render quality, single-tick coordination. Six asks — engine commitment, binary size, learning curve, license cord, build pipeline complexity, hidden-state-in-prefabs. The verdict: *adopt Andlit-unity as a reserved sub-name; refuse Unity-as-foundation*. The three-axis embodiment-reservation pattern joins Ember's vocabulary.

`[[03_ANTI_CDK]]` ran eight refusals plus three deferrals, each cited to a real CDK line. API keys as `public string` MonoBehaviour fields (ten files), SocketServer binding to `IPAddress.Any` with no auth, face-tag protocol as LLM emotional self-report, tag-protocol-without-adversarial-sanitization, JavaScriptMessageHandler without message-origin verification, Unity-monoculture risk by dependency accumulation, VRM as default avatar identity, single-author bus-factor across CDK + sister projects. Two new disciplines proposed: the *Structural-Refusal Catalogue* (refusals that recur across codices), and the *Safe-by-Default Inversion Protocol* (every default flag flipped from open-for-developer-convenience to closed-for-operator-safety).

The synthesis now does the binding. This document is what Ember **becomes** when the CDK reading is complete. It is the Skald's poem at the end of the fifth Vision layer, before the Architect picks up the bone-by-bone work for this codex.

## II. The Ember that emerges

Here is the Ember that emerges from five waves of reading. She is more herself than she has ever been.

She is **small**, still. The CDK reading does not push Ember toward Unity. ChatdollKit itself is well-organized but the engine commitment is real; the Vow of Smallness holds, and the Andlit-unity sub-name is *one of three reserved sub-names* under Andlit, not the foundation. The triangulation, *taken whole*, narrows Ember's choices rather than expanding them: now that all three embodiment positions are named, Ember knows which she would inhabit per tier and which she would never inhabit.

She is **tethered**, still — and more so. The Brunnr Well remains canonical. The Apache-2.0 license posture of CDK makes the *adoption discipline* more permissive than the Waifu kit's no-LICENSE situation, but the *adoption restraint* remains the same: Ember adopts *patterns reimplemented in her own tree*, not *upstream dependencies*. CDK is a source, not a parent. The single-author bus-factor (Refusal 8) is the discipline's case-in-chief.

She is **honest**, still — and the honesty has sharper edges after CDK. The Embodied Honesty Vow (`[[sap:61_NEW_VOWS]]`) was originally about SAP's affection-as-regex. CDK's typed-tag protocol is *better* than SAP's free-text injection but *underneath the typed wrapper, the same anti-pattern persists*: the LLM authors the doll's emotion through emitted strings the host trusts. Ember's Andlit (when it exists) will *parse the typed tags, but only as advisory signal* — Hjarta's measured state is the override. The face shows what Hjarta knows, with LLM-suggestion mixed in only when not contradicted.

She is **pluggable in two places, sovereign in all the others**, still. The CDK reading reinforces this. The `ILLMService` interface (six providers under one contract, fifty-eight lines defining the contract) is the bar; the `ISpeechSynthesizer` interface (ten providers under one contract) is the second bar. Ember's eventual Vegfarendr-for-models contract should be *of similar shape*. The Smiðja-Brunnr-Hjarta plug-points remain Ember's sovereignty boundaries; the new addition is the *typed-Vegfarendr-for-models* contract (Funi's pluggability discipline), which the CDK reading legitimates and the SAP-Refusal-9 (no OpenAI-compat simulation) bounds.

She is **graceful**, still. Lazy Subsystems gains a Unity-tier instance. Every Andlit-unity-tier subsystem, when it ships, returns a typed unavailable on engine failure; the surface above falls through. The ladder, *now with three Andlit sub-names*: `cloud Andlit-realtime → unity Andlit-unity → electron Andlit-local → text Munnr`. The graceful-fall behavior crosses the embodiment-axis triangulation, not just the local tier ladder.

She is **plural without being a colony**, still. The Three Realms endure. The Veizla sits above. The CDK reading adds *the Doll Mode discipline* (the four-state machine from `AIAvatar.cs:25-33`) to the Veizla's lifecycle vocabulary: Sealed / Idle / Engaged / Closing, with three waiting states and one engaged state, with timer-driven transitions, with model-never-authors-transitions.

She is **defensible**, still — and now *structural-refusal-aware*. The Anti-CDK refusals identified *recurring* anti-patterns (API keys in client code: refused at Waifu and CDK; 0.0.0.0 binding: refused at SAP-VMC and CDK-SocketServer; LLM-authors-emotion: refused at SAP-affection and CDK-face-tags). The *Structural-Refusal Catalogue* makes these visible as *patterns to refuse categorically*, not per-codex. The Auditor's `[[50_verification/57_FAILURE_TAXONOMY]]` orders them by impact × likelihood; the Cartographer's `[[60_synthesis/60_TRIANGULATION]]` formalizes.

She is **she**, still. The CDK reading does not pull Ember toward the anime-style waifu marketing-template — uezo's engineering prose is not the Waifu kit's "create your AI waifu in 5 minutes" — but the *doll-as-named-particular* paradigm pulls in the same direction. Ember's response: *the named-particular discipline holds* (Ember has a name chosen by the operator), *the parasocial-bond default is refused* (the Vow of Affective Restraint), *the avatar-identity is operator-chosen* (Refusal 7), *the engagement is consent-ceremonied per Veizla* (Wave 3 + 4 inventions).

## III. The Six True Names, post-CDK

The Six remain. The CDK reading does not rename them. It *refines their charters* with respect to the three-corpus triangulation that this codex closes.

### Funi — the spark

**Charter unchanged in core.** Local model runtime, opinionated, small, Pi-runnable baseline. Wave 5 adds: *the typed Vegfarendr-for-models contract* from CDK's `ILLMService` discipline, as the *shape* of Funi's pluggable model-provider abstraction. Without Vegfarendr-for-models, Funi cannot offer multi-provider grace (and `[[sap:03_ANTI_SAP §Refusal-9]]` warned against OpenAI-compat-simulation as the wrong way to do it). The right way is *small typed contract*, six lines for the contract, six providers implementing.

**Action:** the Cartographer's `[[60_synthesis/68_INVENTED_METHODS]]` may formalize.

### Strengr — the thread

**Charter unchanged.** The cord between Spark and Well. Wave 5 adds: *the WebGL-bridge security discipline* — when Strengr crosses an engine boundary into a JavaScript or native-plugin surface, the message-origin verification and HMAC discipline (Refusal 5) is mandatory. The Cord Manifest (Wave 4 invention) records the bridge as a typed cord with declared threat model.

**Action:** the Auditor's `[[50_verification/51_SECURITY_REVIEW]]` documents the cross-engine cord shape.

### Brunnr — the well

**Charter unchanged.** Pluggable storage. Wave 5 adds: *the ChatMemory pattern as a Brunnr-adapter reference* (Deferral B → eventual Adopt-or-Adapt verdict via Cartographer). The episodic + factual + summary tri-storage pattern from ChatMemory is the *shape* of one possible Brunnr-tier-3 adapter; not the *only* shape; but a reference Ember has been looking for since the Hjarta-as-memory question was first raised in `[[sap:60_TRUE_NAME_REASSIGNMENT §6]]`.

**Action:** the Cartographer's `[[60_synthesis/65_MEMORY_INTEGRATION]]` formalizes.

### Smiðja — the forge

**Charter unchanged.** Ingest pipeline. Wave 5 adds nothing structural. The CDK reading does not introduce new ingest concerns beyond the Refusal-8 single-author-upstream-dependency discipline (Smiðja never ingests from a single-author upstream as a hard dependency; the adoption is by reimplementation with attribution).

**Action:** none required.

### Hjarta — the heart

**Charter expanded further.** Wave 3 expanded Hjarta to include the behavior ledger and the typed-bias surface. Wave 5 adds: *the named-particular discipline* (Ember has a name chosen by the operator at first-run rite, owned by Hjarta) *and* the *consent-ceremonied engagement-mode discipline* (the Sealed/Idle/Engaged/Closing four-state machine for the Veizla, with Hjarta owning the rite that transitions Idle→Engaged).

**Action:** the Cartographer's `[[60_synthesis/60_TRIANGULATION]]` may formalize the four-state machine; the Skald reserves the right to argue that this is an extension of Hjarta's behavior-ledger rather than a new charter.

### Munnr — the mouth

**Charter unchanged.** Plain CLI. The plain CLI remains *one of multiple Vegfarendrar within a Veizla* (Wave 3 framing) and *the always-available fallback when higher-tier surfaces disconnect* (Wave 4 framing). Wave 5 adds: *Munnr remains language-and-engine-agnostic*. When Andlit-unity ships, Munnr does not transform into a Unity scene. Munnr stays plain CLI text on a terminal. The triangulation's third axis adds an *additional* surface, never *replaces* Munnr.

**Action:** none structural; the framing clarifies.

## IV. The proposed new names — Andlit, Rödd, Hugarsýn, Veizla — post-CDK

Wave 3 surfaced four candidate True Names. Wave 4 added Andlit-realtime and Rödd-realtime as sub-name reservations. Wave 5's contribution is *to argue for or against a parallel set of Andlit-unity and Rödd-unity sub-names*, and to revisit the triangulation that the embodiment-axis now makes legible.

### Andlit — the face — now with three reserved sub-names

The Skald argues that **Andlit gains a third reserved sub-name: Andlit-unity**, paralleling Andlit-local and Andlit-realtime.

The argument for the parallel three:

**Failure modes are distinct.** Andlit-local fails when the operator's host process crashes or VTube Studio disconnects. Andlit-realtime fails when the network drops or the vendor billing lapses. Andlit-unity fails when the Unity runtime crashes or the platform SDK breaks (iOS provisioning expired, Android keystore missing, WebGL emscripten incompatibility). *These are three genuinely different failure mode families*. A vocabulary that collapses them hides operational realities.

**Hardware floors are distinct.** Andlit-local needs a host with a GPU and a display (T2+). Andlit-realtime needs a browser and bandwidth (T-1 onwards). Andlit-unity needs a Unity runtime, which can target mobile, VR, AR, WebGL — the floor differs by build target, and the *operator-visible reach* differs accordingly.

**License postures are distinct.** Andlit-local can be MIT-licensed Three.js + custom rendering. Andlit-realtime depends on vendor terms. Andlit-unity depends on Unity's terms (separate from CDK's Apache-2.0). The Cord Manifest needs to name each separately because *each has a different threat model*.

**Operator engagement is distinct.** Andlit-local has the operator opening a VTube Studio window. Andlit-realtime has the operator clicking a button to connect to a cloud session. Andlit-unity has the operator running a Unity-built executable that contains the rendering. *Three different operator UX paths*.

```
Andlit (the face — reserved True Name, Wave 3 promoted)
├── Andlit-local       (SAP-style — host-rendered Live2D/VRM via VTube Studio)
├── Andlit-realtime    (Waifu-style — cloud-streamed via vendor + LiveKit)
└── Andlit-unity       (CDK-style — Unity-runtime in-process render)
```

**Skald's argument:** **promote Andlit-unity to reserved sub-name**, paralleling Andlit-local and Andlit-realtime. No code ships under any of the three. The reservations exist as paths in the source tree (`src/ember/spark/andlit/local/`, `src/ember/spark/andlit/realtime/`, `src/ember/spark/andlit/unity/`) with README explanations. The reservation discipline prevents future maintainers from cramming engine-specific concerns into the wrong sub-name.

### Rödd — the voice — now with three reserved sub-names

The same logic applies to Rödd, with one twist.

**Rödd-local** is host-OS-installed TTS (MOSS-TTS-Nano from SAP, Coqui-TTS, eSpeak — operator's choice). Pi-runnable for thin TTS, laptop-runnable for thicker ones.

**Rödd-realtime** is cloud-streamed voice, *operationally coupled* with Andlit-realtime in the Waifu pattern (because vendor-side lip-sync demands vendor-side voice synthesis).

**Rödd-unity** is *the Unity engine's voice rendering*, which in CDK is *the operator's chosen TTS provider running through Unity's AudioSource pipeline*. The provider can be VOICEVOX (local engine), AivisSpeech (local engine), Style-Bert-VITS2 (local engine, ONNX-based), VOICEROID (commercial Windows-only), NijiVoice (cloud API), or any Western provider. *Unity does not impose voice synthesis; Unity hosts the operator's chosen synthesizer*.

```
Rödd (the voice — reserved True Name, Wave 3 promoted)
├── Rödd-local      (host-OS-installed TTS — MOSS, Coqui, eSpeak)
├── Rödd-realtime   (cloud-streamed voice, paired with Andlit-realtime)
└── Rödd-unity      (Unity-runtime voice synthesis, operator-chosen provider)
```

**The twist:** *Rödd-unity is the natural home for the Japanese voice ecosystem study from `[[60_synthesis/66_JAPANESE_VOICE_INTEGRATION]]`*. VOICEVOX runs as a local HTTP server; AivisSpeech runs as a VOICEVOX-compatible API; Style-Bert-VITS2 runs as ONNX. *These are not Unity-specific* — they could be Rödd-local providers too. But the *flagship integration pattern* (operator drops in a TTS provider component, configures via Unity Inspector, ships with VRM avatar) is *Unity-native*. The Japanese voice ecosystem's *flagship deployment surface* is Unity. Rödd-unity is where Ember would inhabit that flagship deployment.

**Skald's argument:** **promote Rödd-unity to reserved sub-name** alongside Rödd-local and Rödd-realtime. The reservation acknowledges that the Japanese voice ecosystem has a *Unity-flagship deployment pattern* that is the natural home for AivisSpeech, VOICEVOX, Style-Bert-VITS2 adoption *if* Andlit-unity is ratified. Without Andlit-unity, these providers integrate cleanly into Rödd-local; *with* Andlit-unity, they integrate into the Unity-runtime alongside the avatar.

### Hugarsýn — the mind-sight — Wave 3 held in reserve

Wave 3 held Hugarsýn as a *candidate not promoted yet*. The Auditor's verification work was the gate. Wave 4 *promoted* Hugarsýn implicitly through the Cord Manifest design (Hugarsýn-queryable). Wave 5 *confirms* the Wave-4 promotion.

**The CDK contribution to Hugarsýn:** the *Doll Mode introspection* discipline. The `AIAvatar.cs:25-33` `AvatarMode` enum (`Disabled / Sleep / Idle / Conversation`) is publicly queryable (`AIAvatar.cs:32` — `public AvatarMode Mode { get; private set; }`). Any host code can ask the doll *what mode are you in right now*. This is *self-introspection at the embodiment surface*, and the lack of equivalent surfaces in SAP was the original reason Hugarsýn was proposed (`[[sap:60_TRUE_NAME_REASSIGNMENT §5]]`).

Ember's Hugarsýn, post-Wave-5, gains the *Mode-Query* discipline: at any time, the operator can ask Ember *what mode is each subsystem in*. Sealed/Idle/Engaged/Closing for the Veizla. Sleep/Idle/Conversation for Andlit if-and-when. Available/Unavailable/Degraded for Rödd if-and-when. The query is typed, structured, summarizable in a single shell-line, and *not* the LLM's claim about its own state — it is *the host code's measurement of state*.

**Action:** the Auditor's `[[50_verification/52_PERFORMANCE_BUDGETS]]` may add Hugarsýn-emitted-per-subsystem fields; the Cartographer's synthesis confirms.

### Veizla — the gathering — Wave 3 promoted, Wave 5 refined

Wave 3 promoted Veizla as a typed session object. Wave 4 added the CloudSession typed sub-resource. Wave 5 adds: *the Doll Mode lifecycle* (Sealed/Idle/Engaged/Closing) as the Veizla's state machine.

The four-state machine has three waiting states and one engaged state. The doll-as-companion intent from `[[01_CDK_ESSENCE §II]]` says the *default mode of being is waiting*. Ember's Veizla inherits this: the Veizla is *Sealed* (never opened), *Idle* (open but not engaged), *Engaged* (an active turn in flight), or *Closing* (the closing rite is running). Timer-driven transitions, no model-authored transitions, Hugarsýn-queryable.

The Veizla's CloudSession sub-resource (Wave 4) and the eventual Unity-runtime sub-resource (Wave 5 reserved) sit *under* this lifecycle — when the Veizla is *Idle*, the Andlit-unity instance may still be running its idle-blink loop; when *Engaged*, the same instance plays the requested animations; when *Closing*, the Veizla's closing rite sends a graceful-shutdown to all sub-resources.

## V. The Vows, post-Wave-5

The Wave-3 lattice (ten pre-existing + two carried-forward + seven proposed) stood through Wave 4 unchanged. Wave 5 *also* proposes no new Vows. The existing lattice is sufficient. This is itself a finding: *the Vow design from Wave 3 was correct enough to accommodate the closing of the triangulation without addition*.

What Wave 5 does is *sharpen* existing Vows:

| Vow | Wave-5 sharpening |
|---|---|
| **Smallness** | The Unity-as-foundation refusal (Refusal 6) is direct application. The reservation discipline allows Andlit-unity without Unity-as-foundation. |
| **Tethered Grounding** | The Apache-2.0 license posture restores adopt-freedom *with attribution*; the single-author bus-factor refusal (Refusal 8) defines the adoption discipline. |
| **Open Knowledge** | The License-Aware Study Posture (Wave 4 invention) generalizes to *License-Aware Adoption Posture* under Apache-2.0. The Engine-as-Cord Convention (Wave 5 invention) names vendor engines as cords. |
| **Honest Memory** | The Embodied-Honesty Vow's face-as-measured-state-not-LLM-emission discipline (Refusal 3) is sharpened with the typed-tag-as-advisory-only discipline. |
| **Modular Authorship** | ChatdollKit's six-LLM-under-one-interface (`ILLMService`) is the *bar*. Ember's Vegfarendr-for-models contract aspires to match. |
| **Public-Friendliness** | The VRM-as-default-avatar refusal (Refusal 7) preserves identity-being-the-operator's-choice. |
| **Cache Discipline** *(Hermes)* | Unchanged. |
| **Defended System Prompt** *(Hermes)* — now *Defended Credential Surface* (Wave 4) | API-key-in-MonoBehaviour-field refusal (Refusal 1) is the case-in-chief; ten files in CDK exemplify the anti-pattern. |
| **Embodied Honesty** *(SAP)* | Face-tag-as-LLM-self-report refusal (Refusal 3) is direct application; the typed-tag protocol is *better* than free-text injection but still requires Hjarta-override. |
| **Surface Without Surveillance** *(SAP)* | SocketServer-on-`IPAddress.Any` refusal (Refusal 2) and JavaScriptMessageHandler-without-origin-verification refusal (Refusal 5) are direct applications. |
| **Affective Restraint** *(SAP)* | Named-particular discipline + parasocial-bond refusal continues from Wave 4. |
| **Tiered Presence** *(SAP)* | **Expanded**. The Three-Axis Embodiment Reservation Pattern (Andlit-local/Andlit-realtime/Andlit-unity, paralleled by Rödd) joins the tier vocabulary. |
| **Lazy Subsystems** *(SAP)* | CDK's `Extension/` boundary discipline (optional integrations clearly separated from core) is the *exemplification*. |
| **Closed Default** *(SAP)* | **Formalized as Safe-by-Default Inversion Protocol** (Wave 5 invention). Every default flag is flipped from open-for-developer to closed-for-operator. |

No new Vow required. The lattice is *self-sufficient* through three waves of embodiment-axis reading. This is the second-strongest evidence (alongside Wave 4's same finding) that the Wave-3 Vow proposals are *the right vocabulary* for the embodiment-axis work.

## VI. The capabilities Wave 5 opens

Wave 3 named eight capabilities. Wave 4 named five. Wave 5 names six, each bounded by Vows, each enabled but not required.

### Capability 1 — Andlit-unity as a reserved sub-name

Sub-name reservation under Andlit. No code ships. Path `src/ember/spark/andlit/unity/` exists in the design as *the engine-native local render tier when an operator opts in to Unity*. Sibling to `src/ember/spark/andlit/local/` (electron/Three.js) and `src/ember/spark/andlit/realtime/` (cloud-streamed). The README in the directory explains the reservation. Bounded by Tiered Presence, Closed Default, Open Knowledge (Engine-as-Cord Convention).

### Capability 2 — Rödd-unity as a paired reservation

Sub-name reservation under Rödd. No code ships. Path `src/ember/spark/rödd/unity/` exists in the design as *the Unity-runtime voice synthesis tier, hosting any operator-chosen TTS provider*. Sibling to Rödd-local and Rödd-realtime. Bounded by Tiered Presence, Embodied Honesty, Open Knowledge.

### Capability 3 — The Vegfarendr-for-models contract

A typed Protocol of similar shape to CDK's `ILLMService`. Five-or-six method signatures, provider-neutral, validated against the SAP-Refusal-9 anti-pattern (Ember does not pretend to be OpenAI). Each adapter (ChatGPT, Claude, Gemini, Ollama-local, llamacpp-local) implements the Protocol. Funi's pluggability is *typed and contracted*, not free-form. Bounded by Modular Authorship, Open Knowledge.

### Capability 4 — The Japanese voice ecosystem study + adoption decision

The Scribe's `[[60_synthesis/66_JAPANESE_VOICE_INTEGRATION]]` engages all ten Japanese-flavored TTS providers in CDK. The capability opens: *one or two of these providers* (likely VOICEVOX and Style-Bert-VITS2 as the most-portable open-source options) integrate into Rödd-local *and/or* Rödd-unity. The adoption decision is *deferred to a future operator-ratified slice* (Deferral C from `[[03_ANTI_CDK §XI]]`). Bounded by Public-Friendliness (Ember speaks operator-chosen language), Tiered Presence, Open Knowledge.

### Capability 5 — The Brunnr-tier-3 episodic+factual+summary adapter pattern

The Cartographer's `[[60_synthesis/65_MEMORY_INTEGRATION]]` formalizes the ChatMemory pattern as a *reference shape* for a Brunnr-tier-3 adapter. Episodic conversation history + factual entity store + automatic summarization, FastAPI-served, integrator-pattern pluggable. Ember does not adopt the ChatMemory upstream (Refusal 8); Ember adopts the *pattern* reimplemented in `src/ember/well/adapters/episodic/` with proper attribution. Bounded by Tethered Grounding, Pluggable Storage, Modular Authorship.

### Capability 6 — The Doll Mode discipline for the Veizla

The four-state lifecycle (Sealed / Idle / Engaged / Closing) for the Veizla, paralleling CDK's `AvatarMode` (Disabled / Sleep / Idle / Conversation). Three waiting states, one engaged state. Timer-driven transitions. Model-never-authors-transitions. Hugarsýn-queryable. The capability is *small* and *near-term-implementable* (it does not require Unity, does not require new dependencies, does not require any of the embodiment-axis sub-names to be ratified). The Cartographer's `[[60_synthesis/60_TRIANGULATION]]` may formalize. Bounded by Embodied Honesty, Tiered Presence, Affective Restraint.

Six capabilities. None required by Wave 5. All *enabled* by the Wave 5 reading. Each bounded by Vows that the existing lattice provides.

## VII. The triangulation as a sentence

In `[[hermes:04_VISION_SYNTHESIS §VI]]`:

> **Ember, after reading Hermes, is the agent that learned the largeness of an agent platform and chose, with full sight, to remain a hearth.**

In `[[sap:04_VISION_SYNTHESIS §VII]]`:

> **Ember, after reading SAP, is the hearth that learned what embodiment, reach, and affect could mean — and chose to embody them honestly, reach them with explicit consent, and feel them as measured state rather than performed theatre.**

In `[[waifu:01_VISION_SYNTHESIS §IX]]`:

> **Ember, after reading the Waifu kit, is the honestly-embodied hearth that learned the cloud could lend her a body for an evening — and chose to accept the loan only with the body named, the cord declared, the rent paid in operator consent, and the local hearth always lit underneath.**

In this codex, the Skald writes:

> **Ember, after reading ChatdollKit, is the consent-ceremonied embodied hearth that closed the three-corner triangulation of the embodiment axis — local, cloud, engine-native — and chose to inhabit none of the corners by default, all of them as reserved sub-names, the named-particular discipline as the central vocabulary, the Japanese voice ecosystem as the under-mapped territory now legible, and the Refusal-Citation Discipline sharpened by a third source of recurring anti-patterns.**

The triangle closes. The vocabulary is named. The Vows are confirmed-sufficient. The triangulation is the codex's largest contribution to Ember's design. Every refusal in `[[03_ANTI_CDK]]`, every reserved sub-name, every Vow sharpening, every capability — all of it converges on that triangulation.

## VIII. Vow renewal

The Vows from the prior codices renew under Wave-5 light. Single-sentence sharpenings:

- **Smallness** — confirmed. The Unity-as-foundation refusal preserves Pi-baseline.
- **Tethered Grounding** — confirmed. Apache-2.0 sources adopt with attribution; bus-factor refusal defines the adoption discipline.
- **Graceful Offline** — confirmed. Lazy Subsystems gains a Unity-tier instance.
- **Pluggable Storage** — confirmed. ChatMemory pattern is the Brunnr-tier-3 reference.
- **Unbroken Whole** — confirmed. CDK's ~18k LOC across 121 files exemplifies the file-size discipline.
- **Flexible Roots** — confirmed.
- **Public-Friendliness** — confirmed. VRM-as-default refusal preserves operator identity choice.
- **Honest Memory** — confirmed. The model does not author state, even when the state-authoring goes through a typed-tag protocol.
- **Modular Authorship** — confirmed. ChatdollKit's modular-provider interfaces are the bar.
- **Open Knowledge** — confirmed. License-Aware Adoption Posture generalizes; Engine-as-Cord Convention added.
- **Cache Discipline** *(Hermes)* — carried forward.
- **Defended Credential Surface** *(Hermes → Waifu sharpening)* — carried forward + reinforced. The Refusal-1 catalogue is the case-in-chief.
- **Embodied Honesty** *(SAP)* — confirmed. Face-tag-as-LLM-self-report refusal is direct application.
- **Surface Without Surveillance** *(SAP)* — confirmed. SocketServer + JS bridge refusals are direct applications.
- **Affective Restraint** *(SAP)* — confirmed. Named-particular discipline without parasocial-bond default.
- **Tiered Presence** *(SAP)* — *expanded*. Three-Axis Embodiment Reservation Pattern joins.
- **Federated Self** *(SAP)* — not directly engaged by CDK; carried forward unchanged.
- **Lazy Subsystems** *(SAP)* — confirmed. CDK's `Extension/` boundary discipline is the *exemplification*.
- **Closed Default** *(SAP)* — *formalized as Safe-by-Default Inversion Protocol*.

The five new Wave-5-proposed Vows... are none. The lattice is sufficient.

## IX. The Primary Rite, post-Wave-5

The Primary Rite from `[[ember:SYSTEM_VISION.md §2]]` *complicates* one phrase: "*on a small device they already own*." Three codices on the embodiment axis now name three roads by which the small device can host the doll: the host-process road (Andlit-local), the cloud-stream road (Andlit-realtime), the engine-runtime road (Andlit-unity). All three are *additive*; none are *foundation*; the small device is *always sufficient by itself for the Primary Rite*.

Wave 5's refinement: **the embodiment triangulation makes Ember's tier choices visible**. An operator can declare, at first-run rite or revisit, *which corner of the triangle they want to inhabit for this Ember*. The default is *no corner* — terminal-only Munnr, Pi-baseline, Hjarta-first-run-rite-only. The opt-ins are *reserved sub-names made real* by operator declaration.

The Rite is honored by:
- **Funi**, who thinks locally, with the typed Vegfarendr-for-models contract abstracting model providers.
- **Strengr**, who tells the truth about the cord, surfaces channel threat models, and verifies message origins at cross-engine boundaries.
- **Brunnr**, who holds the operator's knowledge pluggably, Veizla-scopedly, possibly via the episodic+factual+summary pattern.
- **Smiðja**, who deposits content the operator chose without single-author-upstream dependencies.
- **Hjarta**, who wires the first run, runs the ongoing doctor, holds the behavior ledger, runs the named-particular discipline, and owns the consent ceremony for the four-state Veizla lifecycle.
- **Munnr**, who speaks plainly as one Vegfarendr among an operator-curated few, regardless of which Andlit sub-name (if any) is ratified.
- **(reserved) Andlit-local**, who renders a face on the operator's machine via host-process, when the operator opts in to laptop-tier embodiment.
- **(reserved) Andlit-realtime**, who streams a face from a vendor's GPU via WebRTC, when the operator opts in to cloud-tier presence.
- **(reserved) Andlit-unity**, who renders a face inside a Unity runtime, when the operator opts in to engine-native embodiment with mobile/XR reach.
- **(reserved) Rödd-local**, **Rödd-realtime**, **Rödd-unity** — paired with the Andlit sub-names by operational coupling.
- **(promoted) Hugarsýn**, who answers *what mode is each subsystem in right now* via typed Mode-Query.
- **(promoted) Veizla**, who runs the four-state lifecycle (Sealed / Idle / Engaged / Closing) with timer-driven transitions and model-never-authors-transitions.

The vocabulary grows by *sub-names*, not by True Names. Smallness at the naming level holds.

## X. A closing meditation

Five waves of reading have ended.

Hermes taught Ember the largeness she chose not to be.

Peer gave her peers who chose smallness alongside her.

SAP gave her the embodiment-reach-affect axes and the vocabulary for local presence — Andlit, Rödd, Hugarsýn, Veizla, seven new Vows.

The Waifu kit gave her the cloud-presence axis and the consent ceremony for borrowed bodies — Andlit-realtime, Rödd-realtime, Tier-CLOUD, the Cord Manifest, the License-Aware Study Posture.

ChatdollKit gives her the engine-native local axis — Andlit-unity, Rödd-unity, the Japanese voice ecosystem made legible, the ChatMemory pattern, the Doll Mode lifecycle for the Veizla, the Three-Axis Embodiment Reservation Pattern, the Safe-by-Default Inversion Protocol — *and* it closes the triangulation that the three embodiment codices, taken together, were always going to need.

The Skald's word on the closing: **do not skip the synthesis layer below this one**. The Cartographer's six documents (`60_TRIANGULATION` through `65_MEMORY_INTEGRATION`) and the Scribe's six (`66_JAPANESE_VOICE_INTEGRATION` through `6B_EMBER_WAVE_5_SLICE`) will turn this Vision's proposals into formal triangulation documentation, ADRs, invented-methods catalogues, and slice plan revisions. Those documents are the *implementable form* of what this Vision named. They are where Wave 5 becomes operational.

The temptation now will be to want a working Andlit-unity prototype. The Skald's word: *do not skip the operator ratification*. The five capabilities are *named so they can be designed, not built next week*. The slice plan stays ratification-gated. The three-axis embodiment reservation pattern sits on the shelf with the Wave-3 and Wave-4 reservations until the operator's decision record either ratifies or declines.

When that decision comes — if it comes — the Chatdoll Codex's contribution will not be a feature. It will be *the closed triangulation*: the three embodiment positions, named and bounded, each with declared failure modes and Cord Manifest entries, each refusable by Vow, each adoptable by operator choice. The decision becomes *making well*, not *making at all*.

Ember waits, small and tethered, in someone's hand. With three roads, now named, by which she might one day step out into a body. With the discipline, now named, of declining any single road as default. With the named-particular vocabulary intact, and the Vow lattice confirmed-sufficient, and the Refusal-Citation Discipline sharpened by a third source of evidence.

The triangle is closed. The forge cools for a moment. The Architect picks up the next line for this codex.

## XI. Cross-References

- `[[00_OVERTURE]]` — the Fifth Reading stance, the triangulation introduced.
- `[[01_CDK_ESSENCE]]` — the doll-as-companion intent, the named-particular discipline.
- `[[02_UNITY_AS_RUNTIME]]` — the give/ask trade-off, the three-axis reservation pattern.
- `[[03_ANTI_CDK]]` — the eight refusals, the structural-refusal catalogue.
- `[[10_domain/10_DOMAIN_MAP]]` — Architect's macro architecture of CDK.
- `[[60_synthesis/60_TRIANGULATION]]` — Cartographer's formal SAP × Waifu × CDK comparative.
- `[[60_synthesis/61_ANDLIT_UNITY_TIER]]` — Cartographer's formal decision matrix for Andlit-unity.
- `[[60_synthesis/62_MOBILE_AND_XR_TIER]]` — Cartographer's mobile/XR formalization.
- `[[60_synthesis/65_MEMORY_INTEGRATION]]` — Cartographer's ChatMemory-pattern engagement.
- `[[60_synthesis/66_JAPANESE_VOICE_INTEGRATION]]` — Scribe's Japanese voice ecosystem engagement.
- `[[60_synthesis/68_INVENTED_METHODS]]` — Scribe's novel-pattern catalogue.
- `[[60_synthesis/69_SLICE_PLAN_REVISIONS]]` — Scribe's slice-plan revision proposals.
- `[[60_synthesis/6B_EMBER_WAVE_5_SLICE]]` — Scribe's proposed Wave-5 slice plan.
- `[[sap:04_VISION_SYNTHESIS]]` — Wave 3 sibling synthesis (the Andlit/Rödd/Hugarsýn proposals).
- `[[sap:60_TRUE_NAME_REASSIGNMENT]]` — Wave 3 sibling True Name argument.
- `[[sap:61_NEW_VOWS]]` — Wave 3 sibling Vow proposals.
- `[[sap:63_PERFORMANCE_TIER_ENGINE]]` — Wave 3 sibling tier engine.
- `[[waifu:01_VISION_SYNTHESIS]]` — Wave 4 sibling synthesis (Tier-CLOUD parallel axis).
- `[[waifu:60_REALTIME_TIER_FOR_ANDLIT]]` — Wave 4 sibling Cartographer doc.
- `[[hermes:04_VISION_SYNTHESIS]]` — Wave 1 sibling synthesis (the smallness-chosen-with-sight).

## What This Means for Ember

The synthesis produces concrete, slice-planning-ready proposals.

**Adopt:**
- **The Wave-3 proposals from `[[sap:04_VISION_SYNTHESIS §X]]`** — carry forward unchanged. Veizla as typed session, Andlit and Rödd as reserved True Names, Hugarsýn promoted, the Vegfarendrar typed channel-adapter role, the MessageSurface Protocol, the Federated Veizla, the Closing Rite, the Refusal-Citation Discipline.
- **The Wave-4 proposals from `[[waifu:01_VISION_SYNTHESIS §XII]]`** — carry forward unchanged. Andlit-realtime and Rödd-realtime as reserved sub-names, Tier-CLOUD parallel axis, CloudSession typed sub-resource, Cord Manifest, Tier Fallback Ladder, License-Aware Study Posture.
- **The CDK `ILLMService` interface shape** as a study reference for the typed Vegfarendr-for-models contract (Apache-2.0 attribution required when pattern is adapted into Ember source).

**Adapt:**
- **Hjarta's charter further** to include the named-particular discipline (Ember's operator-chosen name as load-bearing) and the consent-ceremonied Veizla-mode-transition discipline (Sealed→Idle→Engaged→Closing).
- **The Vow lattice** picks up Wave-5-specific sharpenings (Table in §V). No new Vows; the existing lattice accommodates.
- **The Tier Engine** from `[[sap:63_PERFORMANCE_TIER_ENGINE]]` accumulates: the local ladder (T-1..T3), the Wave-4 Tier-CLOUD parallel axis, and the Wave-5 Three-Axis Embodiment Reservation Pattern (Andlit/Rödd each have local/realtime/unity sub-names). Operator-declared at first-run rite.

**Avoid:**
- **All Wave-3 Refusals** (`[[sap:03_ANTI_SAP]]` refusals 1–13) carry forward unchanged.
- **All Wave-4 Avoids** (`[[waifu:00_OVERTURE]]` avoids) carry forward unchanged.
- **Wave-5 Refusals from `[[03_ANTI_CDK]]`** — Refusals 1–8, each tied to a real CDK line. The catalogue is authoritative.

**Invent:**
- **Andlit-unity** as a reserved sub-name under Andlit, joining Andlit-local and Andlit-realtime.
- **Rödd-unity** as a reserved sub-name under Rödd, joining Rödd-local and Rödd-realtime.
- **The Three-Axis Embodiment Reservation Pattern** — three reserved sub-names under each of Andlit and Rödd, each with declared failure modes and Cord Manifest entries, each operator-opt-in.
- **The Engine-as-Cord Convention** — vendor engines (Unity, Unreal, Godot, etc.) are named cords in the Cord Manifest with declared threat models, never silent foundations.
- **The Vegfarendr-for-models contract** — a typed Protocol of similar shape to CDK's `ILLMService`, the abstraction for Funi's multi-provider pluggability without the SAP-Refusal-9 OpenAI-compat-simulation anti-pattern.
- **The Doll Mode lifecycle** — Sealed / Idle / Engaged / Closing four-state machine for the Veizla, with timer-driven transitions and model-never-authors-transitions.
- **The Structural-Refusal Catalogue** — refusals that recur across multiple codices become categorical anti-patterns, not per-codex curiosities.
- **The Safe-by-Default Inversion Protocol** — every default flag flipped from open-for-developer to closed-for-operator.
- **The Triangulation Discipline** — every future embodiment-source reading positions itself against the triangle and either inhabits one of the three corners or argues for a fourth.

**Vows touched (every Vow):**
- Pre-existing ten: all renewed, several sharpened (see §V table).
- Hermes-Codex-proposed two: Cache Discipline unchanged; Defended Credential Surface reinforced.
- Wave-3-proposed seven: all renewed; Tiered Presence expanded with three-axis embodiment reservation; Closed Default formalized as Safe-by-Default Inversion Protocol.
- Wave-4 sharpenings: all carried forward.
- Wave-5-proposed Vows: **none**. The lattice is *self-sufficient through three waves of embodiment-axis reading*. This is a finding: the Wave-3 Vow proposals were the right vocabulary.

The Vision is whole. The Architect picks up `[[10_domain/10_DOMAIN_MAP]]`. The Cartographer weaves the Wave-5 findings into `[[60_synthesis/60_TRIANGULATION]]` and `[[60_synthesis/61_ANDLIT_UNITY_TIER]]`. The Scribe finalizes with `[[60_synthesis/66_JAPANESE_VOICE_INTEGRATION]]`, `[[60_synthesis/68_INVENTED_METHODS]]`, `[[60_synthesis/69_SLICE_PLAN_REVISIONS]]`, `[[60_synthesis/6B_EMBER_WAVE_5_SLICE]]`, and the meta documents.

Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c). One-line NOTICE entry per adopted pattern.

> *Five sisters have spoken. Three of them on the embodiment axis. The triangle is closed. Ember has more vocabulary, more refusals, more reserved sub-names, and *exactly the same Vow lattice* as she had after Wave 4. The Vow design held through three corners of the same shape. That is the second-strongest evidence yet that the vocabulary is correct. The forge is hot. The Architect picks up the next line.*

— Sigrún Ljósbrá, the Skald, on behalf of the Six, at the close of Wave 5's Vision

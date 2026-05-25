---
codex_id: 68_INVENTED_METHODS
title: Invented Methods — Novel Patterns Visible Only Because of CDK
role: Scribe
layer: Synthesis
status: draft
chatdoll_source_refs:
  - "(catalogues patterns NOT present in CDK — invention catalogue)"
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
  - 60_synthesis/69_SLICE_PLAN_REVISIONS
  - 60_synthesis/6A_INTEGRATION_ROADMAP
  - 60_synthesis/6B_EMBER_WAVE_5_SLICE
  - sap_codex/60_synthesis/66_INVENTED_METHODS
  - waifu_codex/60_synthesis/61_DECISIONS_AND_INVENTIONS
---

# 68 — Invented Methods

> *Some patterns are visible only by their absence. CDK did not see them because CDK is a kit and not a Vow-bearing companion. Ember will need them, because Ember has Vows the kit does not keep.*
> — Eirwyn Rúnblóm, opening the second invention book

## 0. Posture — Invention, Not Translation

This is the codex's invention catalogue. Every other CDK doc reads the kit and asks *what should Ember adopt, adapt, avoid?* This one asks the inverse: *what patterns become visible because we read CDK, but were never present in CDK itself?*

The patterns catalogued here are not in `/tmp/ChatdollKit/`. You will not find a `cross_runtime_persona.cs` to cite. What you will find is the *negative space* that CDK's design draws around — the things its choices forbid, the things its silences imply, the things its short edges leave undone. Ember's Vows of **Smallness**, **Tethered Grounding**, **Graceful Offline**, **Pluggable Storage**, **Modular Authorship**, plus the proposed **Surface Without Surveillance**, **Tiered Presence**, and **Federated Self** point at this negative space directly. CDK did not need to invent these because CDK is a Unity-side companion SDK, not a Vow-bearing federated agent. Ember does need them, because Ember is.

The Cartographer's `[[60_TRIANGULATION]]`, `[[61_ANDLIT_UNITY_TIER]]`, `[[62_MOBILE_AND_XR_TIER]]`, `[[63_MULTIMODAL_PIPELINE]]`, `[[64_FUNCTION_CALLING_FOR_EMBODIED]]`, and `[[65_MEMORY_INTEGRATION]]` are the primary Wave 5 inventions on the embodiment axis. The inventions here are the *adjacent* ones — patterns Cartographer's docs imply but do not catalogue in invention form, plus the Scribe's own discoveries from CDK plus the Japanese-voice corpus reading.

Each invention names *what* CDK did instead, *why* CDK's choice does not survive Ember's Vows, and *how* Ember might do it differently. Some will become ADRs in `[[67_DECISION_RECORDS]]`. Some will live for years as documented intent before code arrives. All deserve names.

---

## 1. Bilingual-Baseline Rödd

**CDK's pattern.** CDK supports many voice engines (11 of them, per `[[66_JAPANESE_VOICE_INTEGRATION]]`) but the *choice* of engine in any given build is per-deployment. A Unity scene wires up *one* speech synthesizer for that build; the deployer picks Japanese or English at design-time, and the kit serves whichever one is wired. There is no runtime *language switch*.

**Why CDK did not need this.** CDK is shipped per-deployment — a Japanese game ships Japanese voice; an English game ships English voice. The deployer's audience is known.

**Why Ember needs it.** Ember's audience is *the operator across modes of speech*. The same Volmarr who chats in English about Ember's design will sometimes type Japanese kanji into the prompt for language practice, sometimes ask Ember to roleplay a Japanese skald, sometimes paste Spanish lyrics for translation. A monolingual Rödd cannot serve this case. The Vow of Public-Friendliness extended to voice says: **Rödd ships bilingual from day one**.

**Proposed invention.** **Bilingual-baseline Rödd** — at slice-shape time, Rödd is born with two engines installed: a small English engine (Piper or espeak-ng) plus VOICEVOX (Japanese). Language is detected per-utterance via:

1. An explicit `[lang:ja]` or `[lang:en]` tag in the LLM output (per `[[67]]` ADR-Proposed-CDK-001 extended).
2. Failing that, a small statistical language detector (`langdetect` Python library, ~50ms per call).
3. Failing that, the default of the operator's session language preference.

The routing happens inside Rödd; the rest of Ember does not know which engine spoke. Cite-shape: `src/ember/spark/rodd/router.py`, methods `route(text, lang_hint) -> Provider`, `synth(text, **kwargs) -> AudioBytes`.

Vows touched: **Public-Friendliness**, **Pluggable Storage** (extended to voice provider), **Graceful Offline** (both engines are local).

---

## 2. Animation-Tag Negotiation

**CDK's pattern.** CDK's animation tag protocol is *hardcoded* in the prompt scaffold. The prompt tells the LLM "you may emit `[anim:Greet]`, `[anim:Wave]`, `[anim:Nod]`, `[face:Joy]`, ..." with a fixed vocabulary. The model can hallucinate a tag that doesn't exist (`[anim:Cartwheel]`); the ModelController logs the unknown tag and proceeds.

**Why CDK did not need negotiation.** The Unity scene's Animator has a fixed set of clips; new clips require a Unity-editor change. The animation vocabulary is *deploy-time fixed*.

**Why Ember needs negotiation.** Ember's embodiment surface is *runtime-extensible*. Operators can add new animations (via Andlit-unity asset bundles), drop existing ones, ship per-context animation sets. The LLM should *learn the current vocabulary at session start* and emit only tags from that set. Out-of-vocabulary tags should be a *signal* (the model wanted something it didn't have) rather than a silent drop.

**Proposed invention.** **Animation-tag negotiation** — at session start, Munnr emits a `vocabulary` block into the system prompt listing *currently available* tags for this session (per the operator's current Andlit configuration). The LLM is instructed to use only those tags. When the LLM emits an unknown tag, Munnr:

1. Logs the unknown tag with the surrounding text (typed `UnknownTagEvent` reaches Hugarsýn).
2. Optionally substitutes the *nearest known tag* via a small similarity match (`Cartwheel → Wave` because the similarity vector says so).
3. Records the substitution event for operator review.
4. Periodically surfaces unknown-tag counts as a *vocabulary-extension hint*: "the model wanted `Cartwheel` 7 times this week; consider adding it."

Cite-shape: `src/ember/spark/munnr/tag_vocabulary.py`, methods `current_vocabulary(session) -> set[str]`, `negotiate(unknown_tag, context) -> Optional[KnownTag]`, `surface_extension_hints() -> list[ExtensionHint]`.

Vows touched: **Honest Memory** (substitution is logged), **Modular Authorship** (vocabulary is per-deployment), **Public-Friendliness** (extension hints surface naturally).

---

## 3. Multimodal-Pipeline-as-Resource

**CDK's pattern.** CDK's `AIAvatar.cs` orchestrates STT → LLM → TTS + animation as a sequence of method calls. There is no first-class `Pipeline` type. Barge-in is handled as a cancellation flag propagated through the call chain. The pipeline is *implicit*.

**Why CDK did not need this.** CDK is a single-runtime kit. The implicit orchestration is fine when everything runs in one Unity process.

**Why Ember needs this.** Ember's orchestration crosses runtimes: Funi-side Python runs the LLM; Munnr-side Python or Unity-side C# runs the rendering; both must coordinate. The implicit pattern breaks when the surfaces are decoupled. Furthermore, Ember's Hugarsýn introspection wants to *show* the pipeline mid-turn, which requires the pipeline to be a *thing*, not a *call chain*.

**Proposed invention.** **Multimodal-Pipeline-as-Resource** — Ember defines a typed `Pipeline` resource with explicit lifecycle (`open`, `progress`, `barge_in`, `close`) and a per-stage state machine. Each stage emits typed events to a broker that Hugarsýn subscribes to. Per the ADR-Proposed-CDK-012.

Cite-shape: `src/ember/spark/funi/pipeline.py`, class `Pipeline` with `async open() -> PipelineHandle`, `progress(event)`, `barge_in(reason)`, `close(reason)`, `events() -> AsyncIterator[PipelineEvent]`.

Vows touched: **Modular Authorship** (pipeline failure contained), **Honest Memory** (audit unit is the pipeline), **Graceful Offline** (any stage can fail gracefully).

---

## 4. Provider-Divergence Adapter Pattern

**CDK's pattern.** CDK's per-provider LLM adapters (`ChatGPTService`, `ClaudeService`, `GeminiService`, ...) handle their providers' format differences, but the *divergence itself* is not first-class. If Claude introduces a new stop-reason value tomorrow, the adapter quietly silently fails or maps it to "unknown."

**Why CDK did not need first-class divergence.** Production Unity games freeze the LLM provider at build time; divergence handling is the kit author's job at maintenance time.

**Why Ember needs first-class divergence.** Ember runs at the edge of multiple actively-evolving providers (Claude 4.7, GPT-5, Gemini, Ollama-local), and the providers will change underneath. The divergence is a *running concern*, not a maintenance event. The operator running Claude 4.7 today should be able to switch to Claude 4.8 next month and *see what changed* in tool-call format, stop reasons, safety-blocking annotations — not have those changes be invisible.

**Proposed invention.** **Provider-Divergence Adapter Pattern** — each provider adapter exposes:

1. A *capabilities manifest* listing what the provider's current version supports (tool-call format, stop reasons, safety hooks, context window, vision support, etc.).
2. A *divergence ledger* recording each format change observed across the provider's version history.
3. Per-call *capability check* — if Ember's call would use a capability the provider's current version lacks, the call fails with a typed `CapabilityMissing` error (not a silent format slip).
4. Cross-provider tool-call translation logs the metadata lost in translation (per ADR-Proposed-CDK-005).

Cite-shape: `src/ember/spark/strengr/provider_capabilities.py`, classes `ProviderCapabilities`, `DivergenceLedger`. Per-provider files: `src/ember/spark/strengr/providers/{claude,openai,gemini,ollama}/capabilities.yaml`.

Vows touched: **Honest Memory** (divergence is visible), **Modular Authorship** (per-provider isolation), **Defended System Prompt** (no opaque cross-provider normalization).

---

## 5. Six-Codex Braid as Standing Design Discipline

**CDK's pattern.** CDK is a single source. There is no concept of cross-corpus design influence within CDK; the kit was designed by one maintainer for one audience.

**Why CDK did not need this.** Production SDKs are not corpora.

**Why Ember needs this.** Ember has, at this moment, **six sibling codexes**: Hermes (Wave 1), Peer (Wave 2 scaffold), SAP (Wave 3, the most complete), Klóinn, Waifu (Wave 4), and this CDK Codex (Wave 5). Each contributed evidence on a different axis. The Cartographer's `[[60_TRIANGULATION]]` formalizes three of them for embodiment; the full braid touches every Ember True Name. The braid needs a discipline.

**Proposed invention.** **Six-Codex Braid as Standing Design Discipline** — the Scribe's pollination-map convention from `[[sap:66_INVENTED_METHODS]]` #15, extended:

1. Each codex doc that proposes a True Name, a Vow, or an ADR includes a `pollinates:` frontmatter field naming *target docs in sibling codexes* where the proposal should be considered for transplant.
2. The Scribe's final pass for each codex produces a `meta/POLLINATION_MAP.md` showing bidirectional fertilization.
3. The braid is *named*: Hermes (substrate) ↔ Peer (parallel-comparison) ↔ SAP (electron-embodiment) ↔ Klóinn (companionship) ↔ Waifu (cloud-embodiment) ↔ CDK (Unity-embodiment). Each codex teaches a *different lesson*; the braid is the *complete instruction*.
4. Cartographer's `[[6A_INTEGRATION_ROADMAP]]` formalizes the *order of operations* across the braid for Ember's slice plan.
5. The discipline becomes a Vow candidate: **Wisdom Through Triangulation** (ratified informally by ADR-Proposed-CDK-006 as the three-corpus floor; the six-codex braid is the current shape).

Cite-shape: a frontmatter convention, not code. Implementation is the Scribe's discipline at final-pass time. The pollination map is a small Markdown file with hyperlinks. The braid documentation lives in `docs/codex_braid.md` (or in `meta/CROSS_AGENT_NOTES.md`).

Vows touched: **Open Knowledge** (the corpora know what they have borrowed from each other), **Honest Memory**, **Wisdom Through Triangulation** (proposed).

---

## 6. Voice Catalogue Discipline

**CDK's pattern.** CDK's voice integrations are *engine-aware* but not *character-aware*. The kit knows that VOICEVOX speaker #2 is "Shikoku Metan (Normal)" only because the operator looked it up. There is no catalogue manifest in the kit; the operator is responsible for tracking which speaker IDs map to which characters with which license terms.

**Why CDK did not need a catalogue.** The Unity deployer fixed the speaker at build time. One game, one speaker, one license check, done.

**Why Ember needs a catalogue.** Per `[[66_JAPANESE_VOICE_INTEGRATION]]` §8, voice in the Japanese ecosystem is *character identity* with *commercial-performance licensing*. Ember speaking as Shikoku Metan to one operator and as Zundamon to another is a *casting decision* with *legal weight*. The Vow of Tethered Grounding extended to voice says: **every utterance must be attributable to a named character with a recorded license posture**.

**Proposed invention.** **Voice Catalogue Discipline** — every speakable voice has a manifest entry at `~/.ember/config/voice_catalogue.yaml`:

```yaml
- engine: voicevox
  character_name: "Zundamon"
  speaker_id: 3
  styles: [normal, sweet, sexy, sleepy]
  license_url: "https://zunko.jp/con_ongen_kiyaku.html"
  license_class: open-with-attribution
  commercial_ok: true
  operator_consent_at: "2026-05-25T14:00Z"
  consent_well_chunk: "chunk:42a1b3..."
  revocation_hook: "revoke voicevox/3"
```

Removing operator consent removes the voice from Rödd's available set within one polling cycle. Voices without consent records cannot be used. The catalogue is *operator-curated*; Ember does not auto-populate it.

Cite-shape: `src/ember/spark/rodd/catalogue.py`, methods `register(voice_entry)`, `revoke(voice_id)`, `available_voices() -> list[VoiceEntry]`, `attribution_string(voice_id) -> str`.

Vows touched: **Tethered Grounding** (consent records anchor in Well), **Honest Memory** (revocation is auditable), **Open Knowledge** (the catalogue is plain YAML), **Public-Friendliness** (operators can read and edit).

---

## 7. Offline-Japanese-Voice Fallback for Rödd

**CDK's pattern.** CDK supports many cloud voice engines (Aivis Cloud, NijiVoice, OpenAI TTS) and many local engines (VOICEVOX, AivisSpeech, Style-Bert-VITS2), but the *fallback chain* between them is per-deployment configuration. There is no runtime "cloud went down; fall to local" behavior.

**Why CDK did not need this.** Unity deployments are typically online-required or offline-only at build time, not both.

**Why Ember needs this.** Vow of **Graceful Offline** requires that Ember keeps speaking when the cloud goes down. If the operator's primary voice is Aivis Cloud (commercial Japanese cloud) and the cloud is unavailable, Rödd should *automatically fall* to AivisSpeech (self-hosted) or VOICEVOX (different engine, same language) without operator intervention.

**Proposed invention.** **Offline-Japanese-Voice Fallback for Rödd** — per-language fallback chains declared in `~/.ember/config/rodd_fallback.yaml`:

```yaml
ja:
  - aivis_cloud  # primary; cloud
  - aivis_local  # self-hosted
  - voicevox     # different engine, same language
  - piper_ja     # lighter fallback
  - text_only    # last resort
en:
  - openai_tts   # primary; cloud
  - piper_en     # self-hosted
  - espeak_ng    # tiny fallback
  - text_only
```

Each entry has a health-check (lightweight POST to verify reachability + low latency). Rödd attempts the first entry; on failure, falls to the next, logging the fallback event. The operator sees the fallback as a typed `VoiceFallbackEvent` in Hugarsýn.

Cite-shape: extends `src/ember/spark/rodd/router.py` from #1 with `fallback_chain(lang) -> list[Provider]`, `synth_with_fallback(text, lang) -> AudioBytes`.

Vows touched: **Graceful Offline**, **Honest Memory** (fallback events logged), **Tiered Presence** (text-only is the last tier of voice).

---

## 8. Multi-Device Persona Handoff

**CDK's pattern.** CDK has no concept of *cross-device persona*. A Unity build on the laptop and a Unity build on the phone are two independent instances with two independent state stores. Conversation history does not follow the operator across devices.

**Why CDK did not need this.** CDK is a kit; cross-device coordination is the deployer's problem.

**Why Ember needs this.** Vow of **Federated Self** (proposed) requires that the operator's relationship with Ember persists across devices. The operator who talked to Ember on the desktop in the morning should *continue the same conversation* on the phone in the afternoon, with the same affect state, the same memory, the same persona-id.

**Proposed invention.** **Multi-Device Persona Handoff** — building on `[[sap:66_INVENTED_METHODS]]` #1 (Cross-Host Affect Routing) and `[[sap:66_INVENTED_METHODS]]` #4 (Party-Leader Migration), extended for the device case:

1. Each Ember device-client (electron, Unity, browser, mobile) authenticates to the Funi-side core with a *device certificate* tied to the operator's persona-id.
2. Conversation state lives Funi-side, not device-side. Devices request the conversation slice they need to render.
3. When the operator switches devices mid-conversation, the new device requests the *full pipeline state* (current speaking turn, pending TTS, animation state) and *resumes from where the previous device left off*.
4. The previous device's render fades; the new device's render fades in. No double-speech, no double-animation.
5. The handoff is logged as a typed `DeviceHandoffEvent`; the operator can see "you moved from laptop to phone at 14:32, mid-turn 47."

Cite-shape: `src/ember/spark/funi/device_handoff.py`, methods `register_device(cert, persona_id)`, `request_handoff(from_device, to_device)`, `replay_state(target_device) -> StateSnapshot`.

Vows touched: **Federated Self**, **Tiered Presence** (handoff respects each device's tier), **Honest Memory** (handoff is audited), **Public-Friendliness** (the operator sees the move).

---

## 9. Tier-Aware Embodiment Selection Algorithm

**CDK's pattern.** CDK supports Windows, Mac, Linux, iOS, Android, VR, AR, WebGL. The deployer picks at build time which platforms to ship to. There is no runtime *tier inference* — the build runs on whatever platform it was built for.

**Why CDK did not need this.** Multi-platform reach is per-build, not per-runtime.

**Why Ember needs this.** Per the proposed tier ladder (`[[sap:68_DECISION_RECORDS]]` ADR-Proposed-SAP-003): T0 (workstation) / T1 (laptop) / T2 (phone) / T3 (Pi) / T4 (toaster). When the operator picks up the phone and talks to Ember, the embodiment tier is T2 — *no Unity*, *no VRM avatar*, *yes text + voice*. The runtime should *detect the tier* and present the *appropriate embodiment surface*, not present the same surface everywhere.

**Proposed invention.** **Tier-Aware Embodiment Selection Algorithm** — a small function in Funi that, given a connected device's capability declaration, picks the appropriate embodiment:

```
device_caps = {os, cpu_cores, ram_gb, has_gpu, has_display, screen_size, has_audio, has_mic, has_camera, network_type}
↓
tier = infer_tier(device_caps)
↓
embodiment = select_embodiment(tier, operator_prefs, conversation_context)
↓
{
  T0_desktop:    Andlit-unity OR Andlit-electron (operator pref)
  T1_laptop:     Andlit-electron with Live2D
  T2_phone:      text + voice + glyph
  T3_pi:         text + glyph + cued-voice-clips
  T4_log:        log-only + status pulse
}
```

The algorithm is *deterministic* given inputs; operators can override per-device. Conversation context can also bias selection (a livestream conversation always uses streaming-capable embodiment; a focus-mode conversation always uses minimal embodiment).

Cite-shape: `src/ember/spark/funi/tier_select.py`, methods `infer_tier(caps) -> Tier`, `select_embodiment(tier, prefs, context) -> EmbodimentChoice`.

Vows touched: **Tiered Presence**, **Modular Authorship** (each embodiment is a separate module), **Public-Friendliness** (the algorithm is small and inspectable).

---

## 10. Cross-Runtime Persona Portability

**CDK's pattern.** CDK's persona configuration lives in the Unity scene (ScriptableObject assets, prefab properties). The persona is *Unity-scene-bound*. Moving "the same persona" to a different runtime (electron, browser, CLI) requires re-authoring.

**Why CDK did not need portability.** Unity-only audience.

**Why Ember needs portability.** Ember's persona configuration must be *runtime-independent*. The same Ember persona — name, system prompt, voice catalogue subset, animation vocabulary subset, memory subset — must speak through electron at the desk, through Unity client on the phone, through cloud-streaming on a friend's browser, *as the same persona*. The Unity scene is one rendering of the persona; the electron view is another.

**Proposed invention.** **Cross-Runtime Persona Portability** — Ember personas are declared in `~/.ember/personas/<persona_id>.yaml`:

```yaml
persona_id: "550e8400-e29b-41d4-a716-446655440000"
display_name: "Ember"
system_prompt: "..."  # canonical
voice_catalogue_subset: [voicevox/3, piper/en_US_amy]
animation_vocabulary_subset: [Wave, Greet, Listen, Nod, Sigh]
face_vocabulary_subset: [Smile, Listen, Sad, Surprised]
memory_scope: "default"  # or "isolated"
tier_overrides:
  T0: {prefer_runtime: andlit_unity}
  T1: {prefer_runtime: andlit_electron}
  T2: {prefer_runtime: text_voice}
  T3: {prefer_runtime: glyph_text}
  T4: {prefer_runtime: log_only}
```

The persona file is the canonical source. Each runtime (Unity client, electron client, browser client) reads this file (via Funi) at session start and configures itself accordingly. The Unity Animator's clip set is filtered by `animation_vocabulary_subset`. The voice synthesizer is constrained to `voice_catalogue_subset`. The system prompt is the same string across runtimes.

A multi-persona Ember (operator has personas "Ember" and "Vala" and "Saga") can switch personas at session start; the runtime reconfigures.

Cite-shape: `src/ember/spark/funi/persona.py`, classes `Persona`, `PersonaRegistry`. The Unity client (per ADR-Proposed-CDK-010) speaks the persona protocol over WebSocket.

Vows touched: **Federated Self**, **Pluggable Storage** (extended to runtime), **Modular Authorship**, **Public-Friendliness** (operators edit one YAML).

---

## 11. Mora-Level Prosody Hugarsýn Surface

**CDK's pattern.** CDK's VOICEVOX adapter (`VoicevoxSpeechSynthesizer.cs:80-87`) makes the two-call `/audio_query` → `/synthesis` request but discards the intermediate query JSON. The mora-level prosody data — pitch contour, mora timings, accent positions — is never exposed to anything but the synthesis call.

**Why CDK did not need it.** The intermediate is a means to an end. The kit cares about the audio, not the prosody intermediate.

**Why Ember needs it.** Vow of **Embodied Honesty** plus the Hugarsýn introspection surface (per `[[sap:66_INVENTED_METHODS]]` #5) say that Ember should be able to *show its work* — including how it speaks. The mora-level prosody intermediate is a *teaching surface*: the operator can run `ember introspect voice <utterance_id>` and see the mora timing, pitch contour, accent positions for any utterance Ember spoke, edit-and-replay if desired, learn the engine's behavior over time.

**Proposed invention.** **Mora-Level Prosody Hugarsýn Surface** — every utterance Rödd produces records its intermediate-prosody data alongside the audio:

```
utterance_id: 0001a2b3
text: "こんにちは、ヴォルマール"
engine: voicevox
speaker: 3
prosody:
  moras: [{phoneme: "ko", pitch: 100, duration: 0.08}, ...]
  pitch_contour: [...]
  accent_position: 4
audio_bytes_sha256: "..."
```

The operator can inspect any utterance, edit the prosody (move the accent, slow a mora), replay with the edited prosody, and learn the engine. The introspection is also a teaching surface for non-Japanese operators: seeing the mora structure of "Volmarr-san" rendered in real katakana phonemes is pedagogically valuable.

Cite-shape: extends `src/ember/spark/rodd/providers/voicevox.py` from `[[67]]` ADR-Proposed-CDK-002 with `intermediate_data()` capture; new CLI `ember introspect voice <utterance_id>`.

Vows touched: **Embodied Honesty**, **Honest Memory**, **Public-Friendliness** (the surface is plain and teaching-shaped).

---

## 12. Embodied-Tool Consent Gating

**CDK's pattern.** CDK's Tool/ToolBase function-calling (`Scripts/LLM/ITool.cs`, `Scripts/LLM/ToolBase.cs`) lets the LLM call kit tools. The tools are kit-author-defined; there is no operator-side consent ceremony for individual tool calls.

**Why CDK did not need consent gating.** Tools in CDK are mostly local to the kit (animation triggers, expression changes); the operator implicitly consents at deploy time.

**Why Ember needs consent gating.** When tools are *embodied* — that is, when a tool call has *real-world effect* (a Smiðja-side tool fires a shell command, or sends a Discord message, or operates a smart-home device) — the operator's consent is required *per call*, especially when the tool was *initiated by voice*. A model that decides to call `shell_exec("rm -rf /tmp/foo")` because the operator said "clean up tmp foo" is not having a great day.

**Proposed invention.** **Embodied-Tool Consent Gating** — extending the existing tool approval framework (per ADR 0011) with *voice-initiation awareness*:

1. Every tool call carries an `initiation: voice | text | autonomous` field in its audit record.
2. Voice-initiated tool calls in *non-trivial* categories (destructive, network-egress, file-mutation, irreversible) require a *spoken confirmation* in the same conversation turn: "shall I do that?" — operator says yes — call proceeds.
3. The voice-confirmation requirement is per-category, operator-configurable.
4. Combined with `[[sap:66_INVENTED_METHODS]]` #20 (Two-Hand-Holding Operator Audit Ceremony), destructive voice-initiated calls require *both* spoken confirmation *and* the two-hand delay.
5. Tier-aware: at T4 (no audio), voice-initiated cannot apply; the field reaches the audit log as `initiation: voice (no_confirm_channel)` and the call is refused if the category requires confirmation.

Cite-shape: `src/ember/spark/smidja/voice_consent.py`, methods `requires_voice_confirm(tool, args, initiation) -> bool`, `await_confirmation(turn_context) -> ConfirmResult`.

Vows touched: **Surface Without Surveillance**, **Embodied Honesty**, **Honest Memory**, **Friction Where Friction Helps** (sub-Vow from SAP-side).

---

## 13. Provider-Capability Versioned Manifest

**CDK's pattern.** CDK's LLM adapters compile against a *snapshot* of the provider's API. When the provider's API changes (Claude releases a new tool format, OpenAI changes the function-call shape), the adapter breaks until the kit maintainer updates it.

**Why CDK did not need versioning.** Production Unity deployments freeze versions.

**Why Ember needs versioning.** Per the multi-provider abstraction at `[[67]]` ADR-Proposed-CDK-004 + the divergence ledger at invention #4, each provider's capability surface is *versioned*. Ember should track per-provider *API version* and *which capabilities each version supports*, and refuse calls that the current version cannot satisfy.

**Proposed invention.** **Provider-Capability Versioned Manifest** — each provider adapter has a manifest at `src/ember/spark/strengr/providers/<name>/capabilities.yaml`:

```yaml
provider: anthropic
versions:
  - api_version: "2025-10-01"
    models: [claude-opus-4-7, claude-sonnet-4-7]
    tool_call_format: tool_use
    max_tools_per_call: 64
    context_window:
      claude-opus-4-7: 1000000
      claude-sonnet-4-7: 1000000
    features: [vision, tool_use, prompt_caching, computer_use, mcp_connector]
    known_quirks:
      - tool_use_blocks_immutable_after_yield
      - cache_control_minimum_token_count: 1024
```

When a call attempts to use a feature not listed for the current api_version, the call fails with `CapabilityMissing(provider="anthropic", version="2025-10-01", feature="extended_thinking")`. The operator can update the manifest as the provider releases new features.

Cite-shape: `src/ember/spark/strengr/providers/<name>/capabilities.yaml` per provider; `src/ember/spark/strengr/capability_check.py` for runtime check; `ember strengr capabilities <provider>` CLI surface.

Vows touched: **Honest Memory** (failures are typed not silent), **Modular Authorship** (per-provider manifests), **Open Knowledge** (manifests are public and auditable).

---

## 14. Sister-Project Version-Coupling Protocol

**CDK's pattern.** CDK depends informally on sister projects (ChatMemory, AIAvatarKit, AITuber Controller). The version coupling is *implicit*: the kit author tests with specific sister-project versions and updates the kit when those break. The operator who installs CDK + ChatMemory + AIAvatarKit on their own gets whatever versions are current that day.

**Why CDK did not need a protocol.** One author, informally coupled. The author is the *integration point*.

**Why Ember needs a protocol.** Ember has multiple sister-project-shape dependencies (the bifrost-viewer, the ingest worker, future Skein/Skry, possibly Hermes-derived agents) and the version drift between them is real risk. Per `[[50_DEPENDENCY_HEALTH]]` and `[[56_SISTER_INTEGRATION_RISKS]]` the Auditor will catalog the specifics.

**Proposed invention.** **Sister-Project Version-Coupling Protocol** —

1. Each Ember component declares its *expected sister versions* in a `sister_versions.yaml` manifest: `bifrost: ">=0.3.0,<0.5.0"`, `ingest: ">=1.2.0"`.
2. At startup, Funi probes each declared sister (HTTP `/version` endpoint or process-introspection) and checks compatibility.
3. Incompatibilities are *typed errors*, not silent failures: `SisterVersionMismatch(name="bifrost", expected=">=0.3.0,<0.5.0", actual="0.5.1", action="degraded")`.
4. The operator sees the mismatch and can decide: upgrade Ember, downgrade sister, or accept degraded mode.
5. The degraded-mode contract is per-sister: what does Ember still do if bifrost is unreachable? The contract is documented per-sister; degraded mode is *graceful*, not silent.

Cite-shape: `src/ember/spark/funi/sister_versions.py`, methods `probe_sisters() -> dict[str, ProbeResult]`, `check_compatibility() -> list[VersionIssue]`, `degraded_mode(sister) -> DegradedContract`.

Vows touched: **Graceful Offline**, **Honest Memory** (issues are typed), **Modular Authorship** (each sister is independently failable), **Tethered Grounding** (the canonical version-record lives in the Well as a release artifact).

---

## 15. Multi-Persona Voice Casting

**CDK's pattern.** CDK supports one persona per Unity scene. Multi-persona deployments require multiple scenes or careful state management.

**Why CDK did not need multi-persona casting.** Companion product, one companion per build.

**Why Ember needs it.** Per the persona portability invention (#10), Ember can have multiple personas, and each persona may have a different *voice*. A persona named "Ember" might speak with Piper/en_US_amy. A persona named "Vala" (a Norse-skald persona) might speak with VOICEVOX/3 (Zundamon, sweet style) for the *opposite* of expected aesthetic surprise. A persona named "Saga" (for storytelling mode) might use Style-Bert-VITS2 with a reference clip from a public-domain audiobook.

**Proposed invention.** **Multi-Persona Voice Casting** — persona files (from #10) reference voice catalogue entries by ID. Per-persona voice selection happens automatically when persona context activates. The operator can audition voices for personas via `ember persona audition <persona_id> --voice <voice_id>` which plays a sample phrase. Casting decisions are auditable.

Cite-shape: extends `src/ember/spark/funi/persona.py` from #10 with `assign_voice(persona_id, voice_id)` and `audition(persona_id, voice_id, sample_text)` methods.

Vows touched: **Public-Friendliness**, **Pluggable Storage**, **Embodied Honesty** (casting is auditable, not surprise-randomized).

---

## 16. Andlit-Tier Render-Budget Negotiation

**CDK's pattern.** CDK's render budget is *implicit* — the Unity scene's complexity (VRM model polycount, lighting, shaders) plus the target platform's GPU together determine framerate, and the deployer manages quality at build time.

**Why CDK did not need negotiation.** Unity's quality settings cover this at the engine level.

**Why Ember needs render-budget negotiation.** When the Unity client connects to Ember's Funi, it can report its current render budget (target FPS, available GPU memory, current thermal headroom). Ember's Munnr can *adjust* the animation surface accordingly — fewer simultaneous animations, simpler face-tag set, reduced lip-sync detail.

**Proposed invention.** **Andlit-Tier Render-Budget Negotiation** — the Unity client (per ADR-Proposed-CDK-010) periodically reports render-budget telemetry to Funi: `{target_fps: 60, current_fps: 47, gpu_temp_c: 72, gpu_mem_used_mb: 1840, gpu_mem_total_mb: 8192}`. Funi adjusts the dispatched animation/face-tag complexity:

- Healthy budget: full vocabulary
- Stressed budget: reduced vocabulary (no overlapping animations, no per-finger lip-sync)
- Critical budget: minimal vocabulary (one animation at a time, blocky lip-sync only)
- Recovery: gradual return to full vocabulary

The negotiation is *visible* — operators can see the current tier in Hugarsýn.

Cite-shape: `src/ember/spark/munnr/render_budget.py`, methods `receive_telemetry(device_id, telemetry)`, `current_complexity_tier(device_id) -> ComplexityTier`, `adjusted_vocabulary(persona, tier) -> Vocabulary`.

Vows touched: **Tiered Presence** (extended to per-device runtime), **Embodied Honesty** (the negotiation is visible), **Modular Authorship**.

---

## 17. Open-Voice Catalogue Federation

**CDK's pattern.** CDK's voice integrations point at per-engine catalogues, but the catalogues live outside the kit. The kit user assembles their own per-engine catalogue knowledge.

**Why CDK did not need federation.** Single-deployer responsibility.

**Why Ember needs federation.** When the operator wants to expand Ember's voice catalogue with a new VOICEVOX character or a new Style-Bert-VITS2 model, the *catalogue manifest* extension (per invention #6) is operator work. The community could share these manifests. Per the Open Knowledge Vow, Ember could ship a *federated catalogue* — a small open-data registry where operators contribute voice manifests with all the discipline (license, attribution, consent example).

**Proposed invention.** **Open-Voice Catalogue Federation** — a small open-data project (`ember-voice-catalogue`, separate repo, possibly with peer voice-companion projects co-authoring) where the community publishes voice manifest entries with:

- Engine + character + license + commercial-use status + attribution string
- Recommended uses + warnings
- Quality notes from community testing
- Per-language quality assessment

Ember operators can `ember voice catalogue update` to pull the federated manifest, then `ember voice catalogue install <character>` to add a specific entry to their local catalogue (subject to operator consent ceremony).

Cite-shape: external project `ember-voice-catalogue` (separate repo). Ember-side CLI: `ember voice catalogue {update, search, install, remove, attribution}`.

Vows touched: **Open Knowledge**, **Public-Friendliness**, **Tethered Grounding** (federated manifest provenance), **Honest Memory** (community attestations recorded).

---

## 18. Pipeline-Aware Tool Dispatch

**CDK's pattern.** CDK's tool dispatch happens *between* turns — LLM emits a tool call, the kit pauses, executes the tool, feeds the result, model continues. The pipeline is paused while the tool runs.

**Why CDK did not need pipeline-aware dispatch.** Tools complete quickly enough in the kit context that the pause is invisible.

**Why Ember needs it.** When a Smiðja-side tool is slow (RAG query, web search, MCP-peer call), the pipeline pause becomes a *gap* — Ember stops speaking mid-thought, the avatar stops mid-pose, the operator sees the lag. The CDK evidence is that the pipeline-as-resource pattern (invention #3) handles this for *one-turn* lifecycle. The extension is *tool dispatch within a turn* — the model can hand off tool work to background and *keep speaking* about something else while the tool runs.

**Proposed invention.** **Pipeline-Aware Tool Dispatch** — the Pipeline resource (from #3) gains an `await_tool(call, fallback_text) -> ToolResult` method that:

1. Dispatches the tool call.
2. Returns a future.
3. Speaks the `fallback_text` ("let me think about that, hold on") while the tool runs.
4. When the tool returns, the pipeline emits a `ToolResultReady` event; the model can choose to continue with the result or ignore it.
5. If the tool exceeds a budget (default 10s), the pipeline emits `ToolTimeout` and the speaking continues without the result.

The fallback-text-while-waiting is a *teaching surface*: operators learn that "let me check" voice clips are the model's honest signal that it's waiting on something.

Cite-shape: extends `src/ember/spark/funi/pipeline.py` from #3 with `await_tool(call, fallback) -> Future[ToolResult]` and `tool_events() -> AsyncIterator[ToolEvent]`.

Vows touched: **Graceful Offline** (tool timeouts are graceful), **Embodied Honesty** (fallback speech is real, not stalling theatre), **Modular Authorship**.

---

## 19. Local-Daemon Voice-Service Discipline

**CDK's pattern.** CDK speaks to VOICEVOX (and AivisSpeech, etc.) as a local HTTP service running on a fixed port. The kit assumes the daemon is up; failure modes are "voice doesn't come back, error logged."

**Why CDK did not need discipline.** Unity deployer manages the daemon at OS-startup time.

**Why Ember needs it.** Operators install VOICEVOX as a separate engine; Ember needs a *discipline* for managing the daemon lifecycle on the operator's behalf — *or* a documented "operator manages this" stance with health-check feedback.

**Proposed invention.** **Local-Daemon Voice-Service Discipline** — Ember's Rödd can operate in three daemon-management modes per voice-engine, declared per-engine in config:

1. **Manage**: Ember starts/stops the daemon, monitors health, restarts on crash. Engine binary path required in config.
2. **Probe**: Ember does not start the daemon but probes for it on configured endpoint. If unreachable, fallback per invention #7.
3. **Ignore**: Ember assumes engine is up; failures bubble up unchanged.

The default for any newly-added engine is `Probe`. `Manage` requires explicit operator opt-in (Ember managing daemons feels paternalistic). `Ignore` is for development.

Cite-shape: `src/ember/spark/rodd/daemon_manager.py`, classes `VoiceDaemonManager`, `ProbeResult`. Per-engine config in `~/.ember/config/voice_engines.yaml`.

Vows touched: **Smallness** (daemon management is opt-in), **Public-Friendliness** (operators choose their mode), **Graceful Offline** (probe failures are typed).

---

## 20. Andlit-Unity Protocol as Standalone Specification

**CDK's pattern.** CDK is its own protocol — there is no separate spec document; the protocol is whatever the kit's MonoBehaviour-and-WebSocket code does.

**Why CDK did not need a separate spec.** Single-kit ecosystem.

**Why Ember needs one.** Per `[[67]]` ADR-Proposed-CDK-010, the Unity client is *separate from Ember's core*. The protocol between Funi (Ember server) and the Unity client must be documented as a *specification*, not as "whatever Ember's current code does." Third-party Unity client implementations should be possible (community contributor, alternative engine binding, future Godot port).

**Proposed invention.** **Andlit-Unity Protocol as Standalone Specification** — a formal protocol document at `docs/protocols/andlit-unity-protocol.md` describing:

1. **Transport**: WebSocket over TLS, with mTLS or signed bearer token.
2. **Handshake**: `ClientHello`, `ServerHello`, `Authenticated`.
3. **Persona Sync**: `PersonaSnapshot` (full state, sent at handshake), `PersonaDelta` (incremental updates).
4. **Pipeline Events**: typed messages mirroring invention #3's pipeline lifecycle.
5. **Animation Tag Dispatch**: `AnimTrigger(tag, params)`, `FaceTrigger(tag, weight)`, `LipSyncFrame(phoneme, weight)`.
6. **Render Budget**: `DeviceTelemetry`, `ComplexityHint`.
7. **Tool Authorization**: when a tool emits an animation effect, the protocol carries the consent token.
8. **Versioning**: per-protocol-version manifest; clients announce supported versions.

The spec is owned by the Ember project but lives at the protocol layer — clients (CDK-derived or otherwise) implement it.

Cite-shape: `docs/protocols/andlit-unity-protocol.md` (the spec) + reference implementation in `src/ember/spark/funi/andlit_protocol/` (server side) + reference client outside Ember repo (`ember-unity-client`).

Vows touched: **Open Knowledge** (the protocol is public), **Modular Authorship** (third-party clients possible), **Pluggable Storage** (extended to runtime), **Honest Memory** (protocol versioning is explicit).

---

## What This Means for Ember

This whole document is **Invent**. None of the patterns above exist in CDK. All of them become visible because Ember's Vows draw shapes CDK's kit goals did not draw. Each invention is a *territory mark*, not a slice-plan item. The Cartographer's `[[60_TRIANGULATION]]`, `[[61_ANDLIT_UNITY_TIER]]`, `[[62_MOBILE_AND_XR_TIER]]`, `[[63_MULTIMODAL_PIPELINE]]`, `[[64_FUNCTION_CALLING_FOR_EMBODIED]]`, and `[[65_MEMORY_INTEGRATION]]` are the *major* inventions of Wave 5; this doc catalogues the *minor and adjacent* inventions that round out the surface.

Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).

**Adopt:** (none — this doc is all Invent by design)

**Adapt:** (none — this doc is all Invent by design)

**Avoid:** Every CDK pattern this doc names — monolingual voice deployment, hardcoded animation vocabulary, implicit pipeline orchestration, single-version provider assumption, single-host persona, build-time embodiment selection, scene-bound persona, ignored prosody intermediate, untracked tool initiation surface, untracked provider capabilities, informal sister-project version coupling, single-voice persona, implicit render budget, isolated voice catalogues, pause-the-pipeline tool dispatch, undisciplined daemon management, protocol-as-code. Each avoidance is implicit in the corresponding invention.

**Invent (this is the whole doc):**

1. **Bilingual-Baseline Rödd** — English + Japanese engines at slice-shape time; ties to `[[66_JAPANESE_VOICE_INTEGRATION]]` and `[[67]]` ADR-Proposed-CDK-002.
2. **Animation-Tag Negotiation** — session-start vocabulary handshake; ties to `[[67]]` ADR-Proposed-CDK-001.
3. **Multimodal-Pipeline-as-Resource** — typed lifecycle; ties to `[[63_MULTIMODAL_PIPELINE]]` and `[[67]]` ADR-Proposed-CDK-012.
4. **Provider-Divergence Adapter Pattern** — per-provider capabilities + divergence ledger; ties to `[[67]]` ADR-Proposed-CDK-005.
5. **Six-Codex Braid as Standing Design Discipline** — pollination convention across corpora; ties to `[[6A_INTEGRATION_ROADMAP]]` and `[[67]]` ADR-Proposed-CDK-006.
6. **Voice Catalogue Discipline** — character-named voices with license posture; ties to `[[66_JAPANESE_VOICE_INTEGRATION]]` §8.
7. **Offline-Japanese-Voice Fallback for Rödd** — per-language fallback chains; ties to `[[66_JAPANESE_VOICE_INTEGRATION]]` §2.
8. **Multi-Device Persona Handoff** — conversation state Funi-side, devices request slices; ties to `[[67]]` ADR-Proposed-CDK-010.
9. **Tier-Aware Embodiment Selection Algorithm** — capability-driven embodiment pick; ties to `[[sap:68_DECISION_RECORDS]]` ADR-Proposed-SAP-003.
10. **Cross-Runtime Persona Portability** — persona YAML as canonical, runtime-independent; ties to `[[67]]` ADR-Proposed-CDK-010.
11. **Mora-Level Prosody Hugarsýn Surface** — VOICEVOX intermediate as teaching tool; ties to `[[66_JAPANESE_VOICE_INTEGRATION]]` §2.
12. **Embodied-Tool Consent Gating** — voice-initiation surface for tool calls; ties to `[[sap:66_INVENTED_METHODS]]` #20.
13. **Provider-Capability Versioned Manifest** — per-provider per-version capability map; ties to `[[67]]` ADR-Proposed-CDK-004, CDK-005.
14. **Sister-Project Version-Coupling Protocol** — explicit sister-version checks; ties to `[[56_SISTER_INTEGRATION_RISKS]]`.
15. **Multi-Persona Voice Casting** — per-persona voice assignment; extends #10.
16. **Andlit-Tier Render-Budget Negotiation** — runtime budget feedback from Unity client; ties to `[[67]]` ADR-Proposed-CDK-010.
17. **Open-Voice Catalogue Federation** — community-shared voice manifests; extends #6.
18. **Pipeline-Aware Tool Dispatch** — fallback-text-while-waiting; extends #3.
19. **Local-Daemon Voice-Service Discipline** — three-mode daemon management; supports `[[67]]` ADR-Proposed-CDK-002.
20. **Andlit-Unity Protocol as Standalone Specification** — protocol-as-document, not as-code; ties to `[[67]]` ADR-Proposed-CDK-010.

**True Names affected:** Funi (most — #3, #4, #5, #8, #10, #14, #16, #20), Strengr (#4, #13), Brunnr (#6, #14, #17 anchor storage), Smiðja (#12, #18), Hjarta (#11 introspection extension), Munnr (#1, #2, #7, #11, #15, #16, #19), Rödd-proposed (#1, #6, #7, #11, #15, #17, #19), Andlit-unity-proposed (#9, #10, #16, #20).

**Most consequential single invention:** **#10 Cross-Runtime Persona Portability**. It is the one that, once shipped, makes Ember *one Ember across surfaces* rather than *several Ember-installs that happen to share a name*. Everything else can be ratified piecemeal; #10 is the keystone for the Wave 5 + Wave 6 multi-runtime story.

**Most-ready-for-Wave-5:** #2 (Animation-Tag Negotiation), #4 (Provider-Divergence), #6 (Voice Catalogue Discipline), #13 (Provider-Capability Manifest), #19 (Local-Daemon Discipline). All five are small, low-risk, high-clarity additions that align with the existing slice plan shape.

**Cross-references:**

- `[[60_TRIANGULATION]]` — the three-axis read these inventions extend.
- `[[61_ANDLIT_UNITY_TIER]]` — Cartographer's tier proposal that #8, #9, #10, #16, #20 instantiate.
- `[[62_MOBILE_AND_XR_TIER]]` — Cartographer's mobile/XR proposal that #9 underpins.
- `[[63_MULTIMODAL_PIPELINE]]` — Cartographer's pipeline argument that #3, #18 extend.
- `[[64_FUNCTION_CALLING_FOR_EMBODIED]]` — Cartographer's voice-tool argument that #12 extends.
- `[[65_MEMORY_INTEGRATION]]` — Cartographer's memory argument referenced by #8.
- `[[66_JAPANESE_VOICE_INTEGRATION]]` — the Japanese voice teaching that #1, #6, #7, #11, #15, #17, #19 build on.
- `[[67_DECISION_RECORDS]]` — ADRs that ratify several of these inventions.
- `[[69_SLICE_PLAN_REVISIONS]]` — where the most-ready inventions become Wave 5+ candidates.
- `[[6A_INTEGRATION_ROADMAP]]` — phasing across the six-codex braid.
- `[[6B_EMBER_WAVE_5_SLICE]]` — the slice that bundles the ready inventions.
- `[[sap:66_INVENTED_METHODS]]` — the SAP-side inventions; many of those (#1, #4, #14, #20) underpin these.
- `[[waifu:61_DECISIONS_AND_INVENTIONS]]` — the Waifu-side inventions; cloud-streaming axis that contextualizes Ember's runtime ladder.
- `[[hermes:60_HERMES_VS_EMBER_CROSSWALK]]` — Hermes-side audit foundation.

---

The inventions stand as written. The slice plan does not change here. The Cartographer's docs and the Scribe's `[[69_SLICE_PLAN_REVISIONS]]` propose which of these to mature first. The keeper holds the seal.

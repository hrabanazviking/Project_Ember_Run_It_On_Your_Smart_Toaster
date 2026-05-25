---
codex_id: 66_JAPANESE_VOICE_INTEGRATION
title: Japanese Voice Integration — What the Under-Served Stack Teaches Ember
role: Scribe
layer: Synthesis
status: draft
chatdoll_source_refs:
  - Scripts/SpeechSynthesizer/VoicevoxSpeechSynthesizer.cs
  - Scripts/SpeechSynthesizer/AivisCloudSpeechSynthesizer.cs
  - Scripts/SpeechSynthesizer/StyleBertVits2SpeechSynthesizer.cs
  - Scripts/SpeechSynthesizer/VoiceroidSpeechSynthesizer.cs
  - Scripts/SpeechSynthesizer/NijiVoiceSpeechSynthesizer.cs
  - Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs
  - Scripts/SpeechSynthesizer/ISpeechSynthesizer.cs
ember_subsystem_targets: [Munnr, Rödd-proposed]
cross_refs:
  - 60_synthesis/63_MULTIMODAL_PIPELINE
  - 20_interface/22_TTS_INTERFACE_JAPANESE
  - 20_interface/21_TTS_INTERFACE_WESTERN
  - 50_verification/54_MULTI_TTS_QUALITY
  - sap_codex/60_synthesis/66_INVENTED_METHODS
  - waifu_codex/60_synthesis/61_DECISIONS_AND_INVENTIONS
---

# 66 — Japanese Voice Integration

> *Western codexes count three TTS providers and call it a stack. ChatdollKit counts ten and calls it a Tuesday. The missing seven are not an oversight; they are a parallel ecosystem the West forgot to look at.*
> — Eirwyn Rúnblóm, sealing the voice-character lineage of the Japanese SDKs

## 0. Posture — Teaching, Not Translating

The SAP Codex examined `moss_tts.py` and concluded that one workstation-grade Chinese voice engine existed. The Waifu Codex examined ZeroWeight's cloud TTS surface and concluded that the avatar runtime brokered Western voice through opaque APIs. Both codexes were correct about their sources and silently incomplete about the world.

ChatdollKit's `SpeechSynthesizer/` directory holds **eleven concrete implementations** alongside the abstract `SpeechSynthesizerBase`. Five of them — VOICEVOX, AivisSpeech via Aivis Cloud, Style-Bert-VITS2, VOICEROID, NijiVoice — are Japanese-first voice engines that the SAP and Waifu corpora never touched. Two more (Kotodama, SpeechGateway) are Japanese-leaning aggregators. Only four (Google, Azure, OpenAI, AIAvatarKit-streaming) come from the Western canon. The ratio is **seven Japanese-or-Japanese-leaning to four Western**, in a kit produced by a Japanese maintainer (uezo) for a Japanese-first audience.

This document teaches that ecosystem to the Ember keeper as if it were the first time the keeper had heard of it — because for this codex's purposes, it largely is. The Scribe's job here is not to translate Apache-2.0 C# into proposed Python; that work belongs in the Architect's `[[22_TTS_INTERFACE_JAPANESE]]` and the Forge-A's `[[33_TTS_PREFETCH]]`. The Scribe's job is to make the case that **Ember's Rödd True Name (proposed) should be born bilingual** — Western voice on one shoulder, Japanese voice on the other, with VOICEVOX as the offline-default baseline and one cloud option for variety.

---

## 1. The Ten-Provider Census

ChatdollKit's `SpeechSynthesizerBase` at `/tmp/ChatdollKit/Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:1-154` declares a uniform contract: each implementation overrides `DownloadAudioClipAsync(string text, Dictionary<string, object> parameters, CancellationToken token)` and returns a Unity `AudioClip`. The base class handles the parallel/sequential prefetch logic that the Forge-A documents in `[[33_TTS_PREFETCH]]`. The provider implementations differ only in *how they reach a sound file* given text.

| # | Provider | File | License of Backend | Cloud / Local | Languages |
|---|---|---|---|---|---|
| 1 | **VOICEVOX** | `VoicevoxSpeechSynthesizer.cs` (190 LOC) | LGPL-3.0 (engine); model-by-model | **Local HTTP daemon** | Japanese; 50+ characters |
| 2 | **AivisSpeech / Aivis Cloud** | `AivisCloudSpeechSynthesizer.cs` (143 LOC) | Engine MIT; AIVMX models per-model | Cloud (also self-host) | Japanese primary, English experimental |
| 3 | **Style-Bert-VITS2** | `StyleBertVits2SpeechSynthesizer.cs` (150 LOC) | AGPL-3.0 | Local Python service | Japanese, English, Chinese |
| 4 | **VOICEROID** | `VoiceroidSpeechSynthesizer.cs` (172 LOC) | Commercial (per voice) | Local (Windows daemon) | Japanese |
| 5 | **NijiVoice** | `NijiVoiceSpeechSynthesizer.cs` (192 LOC) | Proprietary SaaS | Cloud-only | Japanese; ~100 voice actors |
| 6 | **Kotodama** | `KotodamaSpeechSynthesizer.cs` (125 LOC) | Commercial SaaS | Cloud | Japanese |
| 7 | **SpeechGateway** | `SpeechGatewaySpeechSynthesizer.cs` (138 LOC) | open-source aggregator | Local or cloud | many (proxies others) |
| 8 | Google | `GoogleSpeechSynthesizer.cs` (116 LOC) | Proprietary SaaS | Cloud | many |
| 9 | Azure | `AzureSpeechSynthesizer.cs` (128 LOC) | Proprietary SaaS | Cloud | many |
| 10 | OpenAI | `OpenAISpeechSynthesizer.cs` (111 LOC) | Proprietary SaaS | Cloud | many |
| 11 | AIAvatarKit (streaming) | `AIAvatarKitSpeechSynthesizer.cs` (132 LOC) | Apache-2.0 (sister project) | Local server | many (delegates) |

Eleven providers, eleven files, the same base contract. The first lesson is structural: **the cost of supporting another TTS provider in CDK is ~130 LOC**. The architecture made the proliferation cheap, and the proliferation is what enabled the Japanese tail to be served.

Cross-link the Western/Auditor side: `[[21_TTS_INTERFACE_WESTERN]]` covers providers 8-11. Everything in this doc lives on the Japanese side, with `[[22_TTS_INTERFACE_JAPANESE]]` as the technical companion.

---

## 2. VOICEVOX — The Offline-Default Anchor

VOICEVOX is the keystone of the Japanese open-voice ecosystem. The engine repository (`Hiroshiba/voicevox_engine`, GPL-style) ships as a small HTTP daemon you run locally; ChatdollKit pokes it at two endpoints:

```csharp
// /tmp/ChatdollKit/Scripts/SpeechSynthesizer/VoicevoxSpeechSynthesizer.cs:80-98
// Convert text to query for TTS from VOICEVOX server
var queryResp = await client.PostFormAsync(
    EndpointUrl + $"/audio_query?speaker={(decimal)inlineSpeaker}&text=...",
    new Dictionary<string, string>(), cancellationToken: token);
var audioQuery = queryResp.Text;
...
// Get audio data from VOICEBOX server
var url = EndpointUrl + $"/synthesis?speaker={(decimal)inlineSpeaker}";
```

The two-call pattern — `/audio_query` to mint a JSON intermediate, `/synthesis` to render WAV — is VOICEVOX's hallmark. The intermediate query is editable: an operator can mutate pitch, intonation, accent, and pause length *between* the two calls. This is unusual in the TTS world; most Western SaaS endpoints accept SSML or nothing. VOICEVOX's intermediate JSON is the **mora-level prosody handle** the kit exposes but never uses fully. A future Rödd that wishes to do prosodic dialogue work has the substrate already.

Each VOICEVOX speaker is a *character* with one or more *styles* — `name` plus `style.name` plus `style.id` (`VoicevoxSpeechSynthesizer.cs:151-169`). At time of writing the public character catalogue exceeds 50 personae across dozens of voice actors who licensed their voices to the project. The licensing is per-character; some characters permit commercial use, some research-only, some only with attribution. Ember adopting VOICEVOX must adopt the *catalogue discipline* — a manifest of which characters Ember will speak as, what each character's license terms are, and a per-character consent record in the Well.

The case for adoption is concrete:

1. **Offline-first.** The daemon runs on the same host as Ember; no API key, no network round-trip, no quota.
2. **Open architecture.** GPL-style engine, well-documented HTTP API, reproducible builds.
3. **Tier-friendly.** The Pi 5 (T3 in the proposed tier ladder) can run the slim VOICEVOX engine if model size is bounded.
4. **Localisation through expression, not language.** VOICEVOX is a *Japanese* voice engine; an Ember speaking Japanese-only via VOICEVOX would be cosmetic. But the engine's *prosody surface* is the unusual gift. Even an English-speaking Ember can borrow the two-call pattern with a different backend (Piper, espeak-ng) and gain the same prosodic handle.

The case against adoption is the language constraint: VOICEVOX is monolingual. Ember's first voice cannot speak Japanese in a context where the operator speaks English. The mitigation is what makes this codex unique: **adopt VOICEVOX as one engine among several, gated by language detection**. When Ember speaks Japanese (operator switch, conversation language inference, or scheduled language-practice mode), Rödd hands off to VOICEVOX. When Ember speaks English, Rödd uses Piper or another English engine.

Apache-2.0 attribution applies to the *adapter code* Ember would port from `VoicevoxSpeechSynthesizer.cs`. The VOICEVOX engine itself is downstream; Ember vendors the engine like any other local service, not like a library.

---

## 3. AivisSpeech & Aivis Cloud — The Modern Successor Branch

`AivisCloudSpeechSynthesizer.cs:1-143` exposes a newer Japanese voice service that the open-voice community treats as VOICEVOX's modern cousin. The protocol shape is more SSML-like; `useSSML` is a first-class flag (`AivisCloudSpeechSynthesizer.cs:35`). Aivis ships with its own model format — AIVMX — that bundles voice model + speaker manifest + style metadata together. The Aivis Cloud API requires an `ApiKey` (line 29) and bills per-character; the self-hosted AivisSpeech engine does not.

The technical interest is in Aivis's **emotional intensity slider** at `EmotionalIntensity = 1f` (line 38) plus the rare-in-TTS-land **TempoDynamics** parameter at line 39. Most TTS providers expose pitch, rate, and volume. Aivis exposes *emotional intensity* and *tempo dynamics* as distinct from raw rate — which means an Aivis-driven Ember can render the same sentence with the same speaker at three calibrated levels of *expressive heat* without changing pitch or speed. That is a knob the gacha-affect rejection (per `[[sap:68_DECISION_RECORDS]]` ADR-Proposed-SAP-002) gives Ember nothing to do with — but the *composition-first* affect surface (per `[[sap:66_INVENTED_METHODS]]` #17) gains a *bodily* surface from it.

Aivis's commercial posture is hybrid: the cloud is paid-API; the engine is open. For Ember, this means a clean tier story:

- T0/T1 with broadband: Aivis Cloud as the high-quality Japanese voice (operator brings their own key)
- T0/T1 offline: self-hosted AivisSpeech daemon
- T2/T3: VOICEVOX (lighter), or AivisSpeech if model size permits

The adapter pattern is identical to VOICEVOX — POST text and parameters, receive audio bytes — so the Strengr-style provider-divergence cost is small. The *catalogue* discipline differs: Aivis models are AIVMX files with embedded licenses; the manifest discipline must read each AIVMX header and record the embedded terms.

---

## 4. Style-Bert-VITS2 — The Research Frontier

Style-Bert-VITS2 (`StyleBertVits2SpeechSynthesizer.cs:1-150`) is the state-of-the-art end of the Japanese open-source voice ecosystem. It is *not* a daemon designed for production; it is a model architecture (Stylized BERT-conditioned VITS, the 2024 evolution of the VITS family) with reference inference servers shipped from `litagin02/Style-Bert-VITS2`. The model can be trained on a few minutes of audio and produce stylized speech with controllable emotion via a learned style embedding.

The CDK adapter exposes the full parameter surface (`StyleBertVits2SpeechSynthesizer.cs:32-49`):

```csharp
public string Style = "Neutral";
public float StyleWeight = 1.0f;
public float SdpRatio = 0.2f;
public float Noise = 0.6f;
public float NoiseW = 0.8f;
public float Length = 1.0f;
public string Language = "JP";
public bool AutoSplit = true;
public float SplitInterval = 0.5f;
public string AssistText;
public float AssistTextWeight;
public string ReferenceAudioPath;
```

That `ReferenceAudioPath` field is the door. Style-Bert-VITS2 can *condition on a reference clip* — speak the new text in the speaking style of the reference. Combined with `AssistText` (a textual hint that biases prosody toward a stated emotional context), the engine becomes a *style-transfer voice surface*. The Ember Rödd that wants to vary expression by Hjarta affect state can use Style-Bert-VITS2 to do so without retraining: pass a `style="contemplative"` + a reference clip + `AssistTextWeight=0.7` and the voice mood shifts.

The license is **AGPL-3.0** — the strictest of the major TTS engines. AGPL means **any network-exposed Ember that ships Style-Bert-VITS2 must release its own source**. For Ember (the project is open under its existing license already), this is acceptable. For a closed downstream Ember derivative, it is a deal-breaker. The license posture must be flagged loudly in any adoption ADR.

The runtime cost is also nontrivial: Style-Bert-VITS2 inference wants a GPU; CPU-only inference is slow enough to break the prefetch budget. Tier-aware: Style-Bert-VITS2 is a T0-only engine. T1 with integrated GPU may not keep up.

---

## 5. VOICEROID — The Commercial Voice Brand Substrate

`VoiceroidSpeechSynthesizer.cs:1-172` integrates with VOICEROID-family commercial voice software via a small local daemon (typically `VoiceroidProxy` or similar bridge software running on Windows). VOICEROID itself is a commercial product line from AHS — voices like Yukari, Maki, Akari, and so on, each sold as a separate license. The kit's adapter assumes the operator has *already* purchased and installed the VOICEROID engine they want to use; the adapter just speaks to its local HTTP bridge.

For Ember the adoption story is narrow but real:

- An operator who already owns VOICEROID licenses for Japanese voice projects can plug Ember into that existing investment.
- The adapter pattern is the smallest of the Japanese set (~170 LOC), and the operator-investment-respecting posture aligns with Public-Friendliness.
- Ember does not need to ship anything VOICEROID-related; the operator brings the engine, Ember brings the adapter.

The teaching is methodological: **third-party commercial voice software has its own ecosystem of HTTP bridges**, and a kit that respects that ecosystem extends its reach without taking on licensing risk. Ember's Rödd subsystem should bake in the *bridge-adapter* shape as a first-class pattern, not an afterthought. This becomes Invention #5 in `[[68_INVENTED_METHODS]]`.

---

## 6. NijiVoice — The Cloud Variety-Pack

NijiVoice (`NijiVoiceSpeechSynthesizer.cs:1-192`) is a pure cloud SaaS with around a hundred Japanese voice actors. The pricing is per-character. The technical interest is small — the adapter does the obvious POST-with-API-key and receives an audio URL to fetch — but the **product shape** is the teaching.

NijiVoice's catalogue is wide enough that you can pick a different voice for every conversation thread without exhausting the pool. The implications for Ember are aesthetic: a multi-persona Ember (per the multi-persona discipline that Cartographer's `[[60_TRIANGULATION]]` and `[[sap:60_TRUE_NAME_REASSIGNMENT]]` propose for SAP) could speak with a different *voice actor* per persona, gated by operator consent. This is the *casting director* shape for Rödd.

The privacy cost is real: NijiVoice sees every utterance Ember speaks aloud. The operator who values privacy will not use it. The adoption case is therefore narrow: a flagship-tier, online-only, operator-explicitly-opted-in surface for *variety experiences* (storytelling, multi-character dialogue, character study). Ember at T0 only, with a hard opt-in, and never enabled by default.

---

## 7. The Western Surface — For Comparison

Western providers (Google `GoogleSpeechSynthesizer.cs:1-116`, Azure `AzureSpeechSynthesizer.cs:1-128`, OpenAI `OpenAISpeechSynthesizer.cs:1-111`) are smaller adapters because the cloud APIs they wrap are simpler. They speak many languages well, including Japanese. The temptation is to say "we'll just use OpenAI TTS for Japanese too." This document exists to refute that.

The refutation has three parts:

1. **Western TTS speaks Japanese with a Western accent on prosody.** Pitch contour, mora timing, sentence-final particle inflection — the things that distinguish *Japanese-sounding* Japanese from *Japanese as a foreign language being read by a Western model* — are systematically off. A Japanese-native operator notices immediately. A non-native operator notices once it is pointed out and never unhears it.

2. **Western TTS does not expose Japanese-specific knobs.** No mora-level prosody, no pitch-accent override, no sentence-final softening. The two-call VOICEVOX pattern is impossible because the surface is a single shot.

3. **Western TTS sees every utterance.** Even if the operator is not concerned about privacy, the cloud trip is a latency floor of ~300ms minimum. Local VOICEVOX, on the same machine, is single-digit milliseconds plus synthesis time.

Western providers belong in Ember's Rödd stack for English (and the other major Western languages), not as the Japanese fallback. The Japanese fallback must be a Japanese-native engine.

---

## 8. The Cultural Surface — Brief, Honest, Necessary

ChatdollKit was authored in Japan for a Japanese-first audience by a maintainer (uezo) who also ships an iOS app (OshaberiAI) using these voices in production. The kit's voice posture reflects assumptions that Western codexes do not share:

- **Voice as character identity.** A VOICEVOX speaker is not "voice #4"; it is **Zundamon**, a green-haired bean-fairy character with a fan-art ecosystem and recognized name. Choosing a voice in Japanese-companion software is closer to *casting an actor* than to *picking a voice profile*.
- **Voice as commercial-licensed performance.** VOICEROID, Aivis, NijiVoice are all paid in part because actors lent their voices under contract. The license terms are about *the actor's performance rights*, not just code.
- **Voice as community catalogue.** The Japanese open-voice community maintains shared character documentation; a Style-Bert-VITS2 fine-tune that mimics a public character is a community-norms question, not just a license question.

Ember adopting any of these engines inherits the *catalogue discipline* even if Ember speaks English. The Vow of Tethered Grounding extends to voice: every utterance Ember speaks aloud should be attributable to a *named character* (or to a clearly-unbranded engine) and every named character should have a recorded license posture in the Well. This becomes Invention #6 in `[[68_INVENTED_METHODS]]`.

The Cyber-Viking-aesthetic posture of `[[ember:PHILOSOPHY]]` is broadly compatible: the Norse pagan tradition has *named voices* (mead of poetry, named gods speaking with named voices through skalds). The skald discipline maps cleanly to the voice-casting discipline.

---

## 9. Where This Stack Breaks

The Auditor's `[[54_MULTI_TTS_QUALITY]]` will catalog the breaks formally. Three deserve naming here for the Scribe's record:

- **Provider drift.** VOICEVOX adds speakers between releases. The kit's `printSupportedSpeakers` flag (`VoicevoxSpeechSynthesizer.cs:33`) is a debug-only crutch. A production Ember must record the *speaker ID + engine version* used for each utterance, because the same ID can move between versions.

- **Lip-sync drift.** Japanese mora timing differs from English syllable timing. uLipSync (the kit's lip-sync at `[[35_LIP_SYNC]]`) is vowel-detection based and language-agnostic in principle, but the practical truth is that VOICEVOX vowels are *cleaner* than English vowels and the lip-sync looks better in Japanese than in English with the same configuration. Ember speaking English through an English engine and then switching to Japanese through VOICEVOX will need *per-language uLipSync tuning*.

- **License audit recursion.** A Style-Bert-VITS2 model fine-tuned on a VOICEVOX speaker's voice inherits both licenses. The audit chain can grow long quickly. Ember's catalogue discipline must record the *recursive* license posture, not just the engine-level one.

---

## 10. Cross-References

- `[[60_TRIANGULATION]]` — Cartographer's three-axis read; CDK is the axis that exposes this stack.
- `[[63_MULTIMODAL_PIPELINE]]` — the pipeline that VOICEVOX would feed if adopted.
- `[[22_TTS_INTERFACE_JAPANESE]]` — Auditor-owned technical contract for these providers.
- `[[21_TTS_INTERFACE_WESTERN]]` — companion for Google/Azure/OpenAI.
- `[[33_TTS_PREFETCH]]` — Forge-A's parallel-prefetch engine that all providers feed.
- `[[35_LIP_SYNC]]` — uLipSync drift across languages.
- `[[54_MULTI_TTS_QUALITY]]` — Auditor's quality matrix.
- `[[67_DECISION_RECORDS]]` — where the VOICEVOX adoption ADR lives (CDK-002).
- `[[68_INVENTED_METHODS]]` — inventions #5 (bridge-adapter pattern), #6 (voice catalogue discipline), #7 (offline-Japanese-voice fallback).
- `[[69_SLICE_PLAN_REVISIONS]]` — the slice where Rödd-Japanese lands.
- `[[6A_INTEGRATION_ROADMAP]]` — the six-codex braid that places voice work in sequence.
- `[[sap:66_INVENTED_METHODS]]#9` — per-tier voice substitution that this stack populates.
- `[[waifu:61_DECISIONS_AND_INVENTIONS]]` — Waifu's voice posture (cloud-only) that this stack contrasts with.

---

## What This Means for Ember

Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).

**Adopt:**

- **VOICEVOX as Ember's offline-Japanese-voice baseline.** Port the two-call adapter shape from `/tmp/ChatdollKit/Scripts/SpeechSynthesizer/VoicevoxSpeechSynthesizer.cs:55-105`. The Python equivalent is ~120 LOC. The VOICEVOX engine itself is vendored as a local service the operator installs; Ember does not embed the engine. Cite-shape: `src/ember/spark/rodd/providers/voicevox.py`, with `synth(text, speaker_id, style=None) -> AudioBytes`.
- **The provider-base abstraction shape from `SpeechSynthesizerBase.cs:1-154`.** One interface, many implementations, parallel prefetch on top. This is the right architecture for Rödd. Cite-shape: `src/ember/spark/rodd/base.py` with `Provider` Protocol and `Rodd.synth_with_prefetch(text, queue) -> AudioStream`.
- **Per-style voice mapping via the `VoiceStyle` pattern.** `VoicevoxSpeechSynthesizer.cs:184-188` shows the `VoiceStyleValue → VoiceVoxSpeaker` mapping that lets Ember define *abstract affect styles* (calm/focused/listening/troubled) and bind each to a concrete speaker ID per provider. The mapping is config; the engine is plug-in.

**Adapt:**

- **AivisSpeech / Aivis Cloud as a higher-quality optional layer.** The emotional-intensity and tempo-dynamics knobs add a *bodily* affect surface. Ember adopts Aivis as a T0-only opt-in. Aivis Cloud uses operator-brought API key per ADR-Proposed-CDK-001 secret-resolver. Self-hosted AivisSpeech is the offline variant.
- **Style-Bert-VITS2 as a research-tier feature.** AGPL-3.0 means Ember-as-network-service must remain open; acceptable for Ember itself, but the adoption ADR must say so plainly. Disabled by default; opt-in via wizard with the license note shown.
- **VOICEROID bridge pattern** — Ember ships the adapter; the operator brings the engine. This becomes Invention #5 (Bridge-Adapter Pattern) generalized beyond VOICEROID.
- **Cultural-catalogue discipline.** Every voice Ember can speak as is recorded in a catalogue manifest at `~/.ember/config/voice_catalogue.yaml` with engine, character name, license posture, operator consent record, and Well-anchor chunk for the consent moment.

**Avoid:**

- **NijiVoice by default.** Cloud-only, per-utterance API leak, no privacy story. Opt-in only, never the baseline, and flagged in the wizard.
- **OpenAI TTS for Japanese.** Western-accent prosody on Japanese; refuse via language gate. The provider table records `english_ok=true, japanese_ok=false` for OpenAI/Google/Azure.
- **Treating voice as a fungible API.** The whole Japanese stack is a teaching that voice is **character-named** and **license-trailed**. Ember's catalogue discipline embodies this; the "anonymous voice #4" pattern is rejected.

**Invent:**

- **Bilingual-baseline Rödd.** Rödd ships with two engines from day one: one English (Piper or espeak-ng as the lighter local default) and one Japanese (VOICEVOX). Language detection in the LLM output (Munnr emits language hints; or a `[lang:ja]` tag à la the kit's `[anim:]` pattern) routes to the right engine. Even an English-only operator benefits because the architecture refuses the "voice is a single endpoint" trap from day one. See `[[68_INVENTED_METHODS]]` #1 for the full statement.
- **Voice Catalogue Discipline.** Per `[[68_INVENTED_METHODS]]` #6. Every speakable voice has a manifest entry with engine, character name, license posture, operator consent timestamp, Well-anchor chunk for the consent moment, and revocation hook. Removing consent removes the voice from Rödd's available set within one cycle.
- **Mora-level prosody handle as Hugarsýn surface.** Per VOICEVOX's `/audio_query` intermediate (`VoicevoxSpeechSynthesizer.cs:80-87`). The intermediate JSON can be inspected by Hugarsýn (`ember introspect voice <utterance_id>`) so the operator can see the mora-level prosody for any utterance Ember spoke, edit-and-replay if desired, and learn the engine's behavior. This is a teaching surface, not a production knob.
- **Tier-gated voice engine chain.** Extending `[[sap:66_INVENTED_METHODS]]` #9 with Japanese-aware fallback: T0 = Aivis/Style-Bert-VITS2, T1 = VOICEVOX, T2 = piper-tts (English) / VOICEVOX-CPU (Japanese), T3 = cued clip library, T4 = text-only. Tier detection picks the chain; operator override picks specific engines.

---

The Japanese stack is the codex's gift. The Scribe's record is that **Ember adopting any companion-software discipline must learn from the source community whose discipline is deepest**, and on the voice axis that community is Japanese. The VOICEVOX baseline is the smallest adoption; the catalogue discipline is the deepest. Both are recommended. Both wait on ratification.

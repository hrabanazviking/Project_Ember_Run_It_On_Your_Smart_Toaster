---
codex_id: 22_TTS_INTERFACE_JAPANESE
title: TTS Interface (Japanese) — VOICEVOX, AivisSpeech, VOICEROID, Style-Bert-VITS2, NijiVoice, Kotodama, And The Ecosystem The Western Codexes Ignored
role: Auditor
layer: Interface
status: draft
chatdoll_source_refs:
  - Scripts/SpeechSynthesizer/VoicevoxSpeechSynthesizer.cs:13-190
  - Scripts/SpeechSynthesizer/AivisCloudSpeechSynthesizer.cs:11-143
  - Scripts/SpeechSynthesizer/VoiceroidSpeechSynthesizer.cs:13-172
  - Scripts/SpeechSynthesizer/StyleBertVits2SpeechSynthesizer.cs:15-150
  - Scripts/SpeechSynthesizer/NijiVoiceSpeechSynthesizer.cs:13-192
  - Scripts/SpeechSynthesizer/KotodamaSpeechSynthesizer.cs:11-125
  - Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:10-153
  - README.md (the Japanese-stack paragraph)
ember_subsystem_targets: [Rödd, Strengr, Funi, Hjarta]
cross_refs:
  - 20_interface/21_TTS_INTERFACE_WESTERN
  - 50_verification/51_SECURITY_REVIEW
  - 50_verification/54_MULTI_TTS_QUALITY
  - 50_verification/55_WEBGL_GOTCHAS
  - 50_verification/57_FAILURE_TAXONOMY
  - 60_synthesis/66_JAPANESE_VOICE_INTEGRATION
  - sap:22_TTS_DOMAIN
  - waifu:23_TTS_INTERFACE
---

# TTS Interface (Japanese) — VOICEVOX, AivisSpeech, VOICEROID, Style-Bert-VITS2, NijiVoice, Kotodama, And The Ecosystem The Western Codexes Ignored

> *Sólrún, voice cold and even: of the six unique TTS providers in this document, the SAP codex covered zero. The Waifu codex covered zero. The English-speaking generative-AI press writes about Eleven Labs and OpenAI TTS while a parallel ecosystem in Japan has shipped, hardened, and commercialized six distinct voice stacks with their own license posture, distribution model, latency envelope, and aesthetic. VOICEVOX alone has 50+ voices, is free for non-commercial use, runs offline on a CPU at 30-80ms latency floor, and powers a meaningful share of Japanese-language vtubing. The Western codexes' silence on this surface is the gap CDK was built to fill, and the gap I must close now in writing.*
>
> *This doc is the most teaching-heavy in the audit layer. Each provider gets a forensic treatment: contract conformance, latency, license, distribution, audio shape, the small lies. The verdict per provider is recorded. Where Ember should adopt a provider's pattern, I say so concretely; where it should reject, I show the file:line.*

This document is the verification reading of the seven Japanese-or-Japan-adjacent TTS providers in ChatdollKit's `SpeechSynthesizer/` directory: **VOICEVOX**, **AivisSpeech** (via Aivis Cloud API), **VOICEROID** (commercial, via `pyvcroid2-api`), **Style-Bert-VITS2** (open-source neural, state-of-the-art), **NijiVoice** (cloud commercial), and **Kotodama** (Spiral.AI's cloud). The Aivis local-server variant is structurally identical to VOICEVOX (uezo's design lineage), so I treat them together in §2.

Each provider produces Japanese speech with characteristically different voice timbre, prosody, license, and infrastructure. Together they form the *embodiment-axis voice stack* the Western generative-AI codex literature has never documented.

I cite where the kit gets it right, where it gets it wrong, and where the per-provider quirks bite. The Cartographer synthesis in `[[66_JAPANESE_VOICE_INTEGRATION]]` translates these findings into the actual Ember design implication. Here I stay forensic.

---

## 1. The Shape Common To All

All seven Japanese providers conform to `ISpeechSynthesizer` (`Scripts/SpeechSynthesizer/ISpeechSynthesizer.cs:8-12`) — the same two-member contract dissected in `[[21_TTS_INTERFACE_WESTERN]] §1`. The base class wrapper (cache, dedup, preprocess) is inherited unchanged.

Where they diverge: the parameter bag. Five of seven providers honor a `parameters["style"]` key for emotion/style selection, mapped through a `List<VoiceStyle> VoiceStyles` field that the operator wires in the Inspector. This is the kit's quiet convention for emotion-tagged dialog: the LLM emits `[face:Joy][style:happy]こんにちは！` and the dialog processor extracts the `style:happy` tag, passes it as `parameters["style"] = "happy"`, and the synthesizer maps `"happy"` to its provider-specific style ID (a VOICEVOX integer, a Style-Bert-VITS2 string, an AivisCloud `style_name`, etc.).

The Style protocol is undocumented at the interface level. It is documented per-provider only in code comments and the per-class `VoiceStyle` inner type. **This is the load-bearing seam between LLM-emitted emotion and TTS-rendered emotion**, and it is one of CDK's quietest patterns. See `[[25_ANIMATION_TAG_PROTOCOL]]` (Architect-owned) for the matching tag-extraction work.

The text-preprocessing convention is also consistent: every Japanese provider includes the guard `if (string.IsNullOrEmpty(textToSpeech) || textToSpeech == "」") return null;` — the literal `」` (Japanese right corner bracket) is a frequent stray-character trailer from streamed LLM tokenization in Japanese and would otherwise be synthesized into a glottal stop or silence. Five separate providers carry the same hand-rolled guard. The repetition is a smell — this should be base-class behavior — but it works.

---

## 2. VOICEVOX — The Free, Offline, Fifty-Voice CPU Synthesizer

`Scripts/SpeechSynthesizer/VoicevoxSpeechSynthesizer.cs:13-190`.

### 2.1 What It Is

VOICEVOX is a free, open-source-engine, locally-runnable Japanese TTS, originally developed by Hiroshiba (Kazuyuki Hiroshiba) and now distributed at `voicevox.hiroshiba.jp`. The engine is `voicevox_engine` — a Python+ONNX server that exposes an HTTP API on `http://127.0.0.1:50021` by default. Voice models are distributed separately from the engine; characters include Zundamon, Shikoku-Metan, Kasukabe Tsumugi, and 40+ others, each with multiple styles (normal, joyful, sweet, sad, angry).

**License posture is critical and per-voice.** The engine itself is LGPL-equivalent. Each voice has its own license — most are *free for personal and commercial use with attribution*, some require notification for commercial use, some are non-commercial only. The credit string `"VOICEVOX:ずんだもん"` (or equivalent per character) must appear in any production using that voice. This is enforced socially, not technically, but it is real.

**This is the only TTS in the entire ChatdollKit + SAP + Waifu corpora that runs offline on a CPU.** Latency floor on a 2020-era laptop CPU: 30-80ms for a one-sentence utterance. Zero network round-trip. No cloud key. No billing surface. This is structurally different from every other TTS in the embodiment-axis literature.

### 2.2 The CDK Conformance

The synthesizer surface (`:28-36`):

```csharp
public string EndpointUrl;                      // "http://127.0.0.1:50021"
public int Speaker = 2;                          // VOICEVOX speaker ID
public List<VoiceStyle> VoiceStyles;             // style-name → speaker-ID overrides
```

Two-call protocol per utterance (`:55-105`):

1. `POST /audio_query?speaker={ID}&text={URL-escaped text}` returns the synthesizable query JSON. This is VOICEVOX's intermediate format — the engine analyzes the text into phonemes, pitches, durations, and lets the caller tweak before synthesis. The CDK does not tweak; it passes through.
2. `POST /synthesis?speaker={ID}` with the query JSON as the body returns WAV audio.

The kit follows this two-call shape exactly. Cost: two round-trips per utterance instead of one. Mitigation: both round-trips are to `127.0.0.1` and complete in single-digit milliseconds.

WebGL divergence at `:100-104`: WebGL uses `client.PostBytesAsync` and `AudioConverter.PCMToAudioClip(audioResp.Data)` because Unity's standard `UnityWebRequestMultimedia.GetAudioClip` is unreliable in the browser for the VOICEVOX endpoint. Native uses `GetAudioClip(url, AudioType.WAV)`.

The `printSupportedSpeakers` Inspector toggle (`:33`) calls `ListSpeakersAsync()` at boot, which hits `GET /speakers` and logs every supported `{character}_{style} → ID` mapping. Useful debug aid. Operators check it once and disable.

### 2.3 The Style Protocol

`VoiceStyle` (`:183-188`):

```csharp
[Serializable]
public class VoiceStyle {
    public string VoiceStyleValue;   // e.g., "happy"
    public int VoiceVoxSpeaker;       // e.g., 3 (Zundamon-Amaama)
}
```

The operator pre-configures a list mapping the LLM-emitted style strings to VOICEVOX speaker IDs. Same character can have *different speaker IDs per emotion*: Zundamon-Normal=3, Zundamon-Joyful=1, Zundamon-Sad=8, etc. The kit dispatches on the matching `VoiceStyleValue`.

This is the right shape — emotion is per-character, not global — but it requires the operator to know the speaker IDs in advance. The `ListSpeakersAsync` debug print at `:141-149` is the only discovery aid. There is no `GetSpeakersForCharacter("Zundamon")` convenience.

### 2.4 The Pre-process Hook

The base class's `PreprocessText` (`SpeechSynthesizerBase.cs:21`) is the seam where romaji-to-kana or LLM-output-cleanup goes. The kit does not ship a default preprocessor for VOICEVOX; LLM output flows in raw. For most modern Japanese LLM output this is fine. For LLM output that contains English brand names (`OpenAI`, `Claude`, `GitHub`) VOICEVOX will read the English letter-by-letter as Japanese kana: "OpenAI" becomes *o-pee-ee-en-a-i*. The fix is a preprocessor that katakanizes brand names; CDK ships no such preprocessor.

### 2.5 Where It Bites

- **CORS in WebGL.** VOICEVOX defaults to no CORS headers. A CDK WebGL build pointed at `http://localhost:50021` from a hosted HTTPS page returns CORS errors *and* the mixed-content blocker fires (HTTPS page, HTTP backend). See `[[55_WEBGL_GOTCHAS §7]]`. The operator must run VOICEVOX with `--cors_policy_mode=all` and ideally behind an HTTPS reverse proxy.
- **Cold-start latency.** VOICEVOX loads voice models on first use; the first call after engine start can take 2-5 seconds. The kit's `audioCache` deduplication does not pre-warm. A common production pattern is to fire a `/audio_query` for a one-character utterance at app startup as a warmup; CDK ships no warmup hook.
- **Speaker-ID drift between versions.** VOICEVOX has, across its release history, occasionally renumbered or added speakers in a way that broke hardcoded IDs in operator scenes. The `VoiceStyles` field stores literal integers; a VOICEVOX version bump can silently misroute "Zundamon-Normal" to a different character. There is no version-pinning at the Unity scene level.
- **The `」` guard is real.** `:60`. Without it, a streamed LLM emitting "こんにちは」" (trailing bracket from a quoted-string truncation) produces a silent clip or an engine 422.

### 2.6 Verdict

**Adopt the entire pattern.** VOICEVOX is the unique provider in the corpus — offline, free, CPU-runnable, Japanese-fluent, 50+ voices — and the kit's two-call conformance is correct. The Style protocol is the right shape. The CORS and cold-start failures are operator-tier and documented. The speaker-ID drift is the one structural concern, and Ember should fix it by version-pinning.

---

## 3. AivisSpeech (Aivis Cloud) — The Newer Generation, The Sibling

`Scripts/SpeechSynthesizer/AivisCloudSpeechSynthesizer.cs:11-143`.

### 3.1 What It Is

AivisSpeech is, structurally, "next-generation VOICEVOX" — it was created by some of the same engineers and follows the same two-call AudioQuery → Synthesis shape with the same `voicevox_engine`-compatible API endpoints. The local engine is downloadable separately; the cloud variant is at `https://api.aivis-project.com/v1/tts/synthesize`. The voices are *neural* rather than the older VOICEVOX statistical models — higher quality, slightly slower compute (offset by GPU on the cloud side).

CDK's `AivisCloudSpeechSynthesizer.cs` targets the *cloud* variant specifically. The README mentions both AivisSpeech (local, VOICEVOX-compatible API) and Aivis Cloud (this implementation); the local variant is reachable through the existing `VoicevoxSpeechSynthesizer` by pointing `EndpointUrl` at the AivisSpeech engine.

### 3.2 The CDK Conformance

The surface is the most parameter-rich of any TTS in CDK (`:28-49`):

```csharp
public string EndpointUrl;
public string ApiKey;                            // Bearer auth — leaks per §5
public string ModelUUID = "a59cb814-...";        // canonical female voice
public string SpeakerUUID;
public int StyleId = 0;
public string StyleName;
public string UserDictionaryUUID;                // per-user pronunciation dictionary
public bool UseSSML = false;
public string Language = "ja";
public float SpeakingRate = 1f;
public float EmotionalIntensity = 1f;            // 0.0 to 2.0
public float TempoDynamics = 1f;
public float Pitch = 0f;
public float Volume = 1f;
public float LeadingSilenceSeconds = 0.0f;
public float TrailingSilenceSeconds = 0.3f;     // 300ms tail by default
public float LineBreakSilenceSeconds = 0.3f;
public string OutputFormat = "wav";
public int OutputBitrate = 0;
public int OutputSamplingRate = 16000;
public string OutputAudioChannels = "mono";
```

Eighteen tunable parameters. Aivis Cloud's API supports SSML, per-user pronunciation dictionaries (`UserDictionaryUUID`), and granular silence injection (leading / trailing / line-break) that no other CDK provider exposes. The kit's coverage of the API surface is thorough.

Single POST (`:96-133`):

```csharp
var payload = new Dictionary<string, object>() {
    {"text", textToSpeech},
    {"model_uuid", ModelUUID},
    {"style_id", StyleId},
    // ... eighteen keys total ...
};
var audioResp = await client.PostJsonAsync(url, payload, headers, cancellationToken: token);
return AudioConverter.PCMToAudioClip(audioResp.Data, searchDataChunk: true);
```

The `searchDataChunk: true` flag (same workaround as Azure WAV path) handles Aivis Cloud's WAV responses where Unity's WebGL audio loader does not find the `data` chunk reliably.

### 3.3 The Style Protocol

Two seams: `style_id` (integer) and `style_name` (string). The Inspector `VoiceStyles` list maps LLM-emitted style values to `style_name` strings. Aivis Cloud accepts either, but `style_name` is more readable. The kit prefers `style_name` when the operator wires it.

### 3.4 License + Cost

Aivis Cloud is a **paid commercial service**. The `ApiKey` field implies a billing-attached account. Pricing (per Aivis Cloud's docs, 2025): ~¥1.0 per 1000 characters synthesized, comparable to OpenAI tts-1. *This makes the build-bundle key leak especially expensive*: a leaked Aivis Cloud key with billing attached is a direct financial vector.

Local AivisSpeech (via the VoicevoxSpeechSynthesizer) is free.

### 3.5 Verdict

**Adopt the parameter shape**, especially `LeadingSilenceSeconds` / `TrailingSilenceSeconds` / `LineBreakSilenceSeconds` — these are the right knobs for dialog pacing. **Reject the credential storage** (Inspector-baked key). The 18-parameter surface is also a Stuffed-Inspector finding — Ember should expose the common five and group the other thirteen under an `AdvancedParameters` sub-object.

---

## 4. VOICEROID — The Commercial Desktop App Behind A Python Bridge

`Scripts/SpeechSynthesizer/VoiceroidSpeechSynthesizer.cs:13-172`.

### 4.1 What It Is

VOICEROID is AHS Co.'s commercial Japanese TTS product line — Yukari, Maki, Akane, Aoi, others — used heavily in Japanese vtubing and Nico Nico Douga commentary for over a decade. The voices are *concatenative* (sample-based with prosody overlay) rather than neural; the result is characteristic, recognizable, and aesthetically distinct from VOICEVOX's flatter statistical voices.

**Distribution is the awkward part.** VOICEROID ships as a Windows desktop application. To call it programmatically requires a bridge. uezo's `pyvcroid2-api` (`/tmp/ChatdollKit/Scripts/SpeechSynthesizer/VoiceroidSpeechSynthesizer.cs:57` cites `https://github.com/uezo/pyvcroid2-api`) is the Python wrapper around AHS's `vcroid2.exe` automation interface. CDK's synthesizer is an HTTP client for `pyvcroid2-api`.

Translation: to use VOICEROID through CDK, the operator needs:
1. A Windows machine.
2. A purchased VOICEROID license (¥10,000–15,000 per voice).
3. `pyvcroid2-api` running on that Windows machine.
4. The CDK app pointing `BaseUrl` at that machine's HTTP server.

This is a three-tier deployment — Unity client, pyvcroid2-api Python bridge, vcroid2.exe — for one voice. The friction is real. Operators who choose VOICEROID through CDK are doing it *for the voice character*, not the convenience.

### 4.2 The CDK Conformance

Surface (`:27-46`):

```csharp
public string BaseUrl;
public AudioType AudioType = AudioType.WAV;
// Eight numeric voice-tuning parameters (Volume, Speed, Pitch, Emphasis, four pause durations, MasterVolume)
```

The `[Range(...)]` attributes (`:31-46`) clamp Inspector edits — `Pitch` to `0.5–2.0`, `Speed` to `0.5–4.0`, etc. This is the only CDK provider with `[Range]` clamps on TTS parameters. The clamps reflect VOICEROID's actual valid ranges per the AHS API.

The synthesizer pushes settings updates at startup (`:54`):

```csharp
private void Start() {
    client = new ChatdollHttp(Timeout);
    _ = UpdateSettingsAsync();        // PATCH /api/settings with the eight params
}
```

`UpdateSettingsAsync` PATCHes the eight voice-tuning params to `/api/settings`. This is *global* state on the pyvcroid2-api server — the next call from any client gets the new settings. A two-client setup (CDK + another app) over the same pyvcroid2-api stomps on each other. The kit assumes single-tenant.

Per-utterance (`:59-83`):

```csharp
protected override async UniTask<AudioClip> DownloadAudioClipAsync(...) {
    var request = new VoiceroidRequest(text, AudioType == AudioType.MPEG ? "mp3" : "wav");
    var voiceParameters = new Dictionary<string, float>();
    foreach (var key in voiceParameterKeys)  // Volume, Speed, Pitch, Emphasis
    {
        if (parameters.ContainsKey(key)) voiceParameters.Add(key, (float)parameters[key]);
    }
    if (voiceParameters.Count > 0) request.VoiceParameters = voiceParameters;
    // POST /api/speech
}
```

Per-call override of `Volume/Speed/Pitch/Emphasis` is supported via the parameters bag. This is the right shape — global defaults via the Inspector, per-utterance tuning via `parameters`. But the global PATCH-at-startup means a CDK instance can leave the pyvcroid2-api server in a non-default state for *other* clients after CDK exits.

### 4.3 The Style Protocol

VOICEROID has no style/emotion API in the AHS sense. CDK omits a `VoiceStyles` list for this provider. Emotion expression for VOICEROID is via the four sliders (`Pitch`, `Speed`, `Emphasis`, `Volume`) rather than a categorical emotion ID. The LLM cannot emit `[style:happy]` and expect a coherent voice change without operator mapping; the kit provides no default mapping.

### 4.4 Verdict

**Avoid for Ember-default deployments.** The three-tier Windows-only deployment makes VOICEROID a specialty path. **Adopt the `[Range]` clamp pattern** for any numeric voice parameter in Ember — Inspector edits should refuse out-of-range values. **Adopt the global-defaults / per-call-override pattern** as the canonical voice-tuning shape. But the global-state-on-server smell is real — Ember's equivalent should make per-call overrides truly per-call, not session-state-mutating.

---

## 5. Style-Bert-VITS2 — The State-Of-The-Art Neural Open Source

`Scripts/SpeechSynthesizer/StyleBertVits2SpeechSynthesizer.cs:15-150`.

### 5.1 What It Is

Style-Bert-VITS2 is litagin02's open-source neural Japanese TTS (`https://github.com/litagin02/Style-Bert-VITS2`), built on VITS2 with BERT-based style control. As of late 2025 it represents the high-end of open-source Japanese voice quality — natural prosody, expressive emotion control, multi-speaker, multi-style. Voice character is fine-tunable on operator-supplied data.

**Local, GPU-preferred, free, open-source under AGPL-3.0**. The AGPL is significant: any operator embedding the engine in a service must offer source under AGPL terms. CDK's *client* is Apache-2.0, but the *engine* is AGPL. This is a license-stack mismatch the operator must be aware of.

### 5.2 The CDK Conformance

Surface (`:30-49`):

```csharp
public string EndpointUrl;
public string ModelName = "amitaro";      // model directory name
public int ModelId = 0;
public string SpeakerName = "あみたろ";   // displayable speaker name
public int SpeakerId = 0;
public string Style = "Neutral";          // SBV2 style names
public float StyleWeight = 1.0f;          // 0.0-1.0 emotion intensity
public float SdpRatio = 0.2f;             // stochastic duration predictor ratio
public float Noise = 0.6f;                // SBV2 noise scale
public float NoiseW = 0.8f;
public float Length = 1.0f;               // speech length factor
public string Language = "JP";
public bool AutoSplit = true;
public float SplitInterval = 0.5f;
public string AssistText;
public float AssistTextWeight;
public string ReferenceAudioPath;          // server-side reference for voice cloning
```

Sixteen parameters. The `Noise`, `NoiseW`, `SdpRatio` triplet is the SBV2-specific stochastic-synthesis control — operators tune these to balance speech naturalness vs voice consistency. CDK exposes them all.

Single GET (`:88-112`):

```csharp
var url = EndpointUrl + $"/voice?text={UnityWebRequest.EscapeURL(textToSpeech, Encoding.UTF8)}";
url += $"&model_name={...}";
url += $"&style={UnityWebRequest.EscapeURL(inlineStyle, Encoding.UTF8)}";
// ... a dozen more query params ...
return await DownloadAudioClipAsync(url, token);
```

The entire request is a GET with all parameters in the query string. This is unusual for a TTS API and is SBV2's specific design choice (the SBV2 server's `/voice` endpoint accepts GET). It works, but the URL length can grow large — a 200-character utterance plus the dozen tuning params can push past 1KB. Most HTTP stacks handle 8KB URLs without issue; mobile cellular networks sometimes have stricter limits.

### 5.3 The Style Protocol

The `Style` field is a string matching the SBV2 model's pre-defined emotion labels (`"Neutral"`, `"Joy"`, `"Anger"`, `"Sorrow"`, `"Fun"`, etc. — model-specific). The `StyleWeight` is a 0.0-1.0 intensity. The `VoiceStyles` list (`:49`) maps LLM-emitted style values to SBV2 style strings.

This is the most expressive style protocol in any CDK provider. The combination of categorical (`Style`) plus continuous (`StyleWeight`) gives the dialog manager fine control — `[style:happy:0.7]` becomes `Style="Joy", StyleWeight=0.7`.

### 5.4 The AGPL Footgun

If an operator runs the SBV2 engine as a service that Ember (or any third party) connects to, the operator owes source under AGPL-3.0. For *personal* deployments this is moot. For *commercial* deployments serving end users, this is a real license-trigger. Apache-2.0 CDK client + AGPL SBV2 engine + Ember (mixed license) is a stack with three license dimensions. Operators must verify their composition.

### 5.5 Verdict

**Adopt the style-weight pattern** (continuous intensity alongside categorical). Reject the GET-with-everything-in-querystring shape for Ember — Ember should prefer POST-with-body for any payload that may exceed 1KB. The AGPL implication is operator-tier; Ember's docs should flag the license stack explicitly.

---

## 6. NijiVoice — The Cloud Commercial, The Pop-Idol Voices

`Scripts/SpeechSynthesizer/NijiVoiceSpeechSynthesizer.cs:13-192`.

### 6.1 What It Is

NijiVoice is a Japanese cloud TTS at `api.nijivoice.com` specializing in characteristic "idol/anime voice actor" voices — distinctly different from VOICEVOX's neutral or Style-Bert-VITS2's natural shapes. The voice catalog is selectable, paid, and tied to a `VoiceActorId` GUID.

### 6.2 The CDK Conformance

Two-call protocol (`:54-77`):

1. `POST /api/platform/v1/voice-actors/{VoiceActorId}/generate-voice` returns a JSON `GeneratedVoiceResponse` containing an `audioFileUrl`.
2. `GET audioFileUrl` returns the actual audio.

Auth via `x-api-key` header (`:69`). Bearer-equivalent. Build-bundle leak applies.

The `GeneratedVoiceResponse` (`:181-189`):

```csharp
private class GeneratedVoiceResponse {
    public GeneratedVoice generatedvoice { get; set; }
}
private class GeneratedVoice {
    public string audioFileUrl { get; set; }
    public float duration { get; set; }
}
```

The audio is on a *different URL* — usually a CDN-fronted blob storage URL. The synthesizer must do a *second* network call. This is the highest-latency provider in CDK: cloud TTS compute + CDN GET = 800-1500ms for a typical utterance.

The `audioFileUrl` is unauthenticated — anyone with the URL has the audio. URLs are typically short-lived (signed for ~5 minutes) but if the URL leaks during that window, the audio is grabbable.

### 6.3 The VoiceActor Discovery

The kit ships `ListSpeakersAsync` (`:107-123`) that hits `GET /api/platform/v1/voice-actors` and populates `VoiceModelSpeeds` (cached recommended speeds per actor). Useful at boot. The actor catalog is large (hundreds of voices); the operator browses NijiVoice's web UI to pick the GUID they want, then pastes it into the Inspector.

### 6.4 Verdict

**Reject for default Ember**. Two-call latency is too high for conversational TTS. **Suitable as a specialty layer** for operators who need the specific voice character. The Bearer-equivalent header auth and per-actor GUID model are otherwise sane.

---

## 7. Kotodama — The Spiral.AI Commercial, The Multi-Lingual Style

`Scripts/SpeechSynthesizer/KotodamaSpeechSynthesizer.cs:11-125`.

### 7.1 What It Is

Kotodama is Spiral AI's TTS API (`https://tts3.spiral-ai-app.com/api/tts_generate`), pitched for *characterful* Japanese voices with Multi-emotion support. Less famous than VOICEVOX, smaller voice catalog, paid.

### 7.2 The CDK Conformance

Single POST (`:84-100`):

```csharp
var data = new Dictionary<string, string>() {
    { "text", text },
    { "speaker_id", SpeakerId },
    { "decoration_id", decorationId },  // emotion key, with "_en" suffix for English
    { "audio_format", AudioType == AudioType.MPEG ? "mp3" : "wav" },
};
```

The `decoration_id` is Kotodama's term for "emotion preset". CDK ships a default `VoiceStyles` list (`:34-41`):

```csharp
public List<VoiceStyle> VoiceStyles = new() {
    new VoiceStyle("Neutral", "neutral"),
    new VoiceStyle("Joy", "happy"),
    new VoiceStyle("Sorrow", "sad"),
    new VoiceStyle("Fun", "laughing"),
    new VoiceStyle("Surprised", "surprised"),
};
```

This is the *only* synthesizer in CDK that ships a default style mapping. Every other provider requires the operator to wire it. The Kotodama default is reasonable — it aligns with the kit's documented `[face:Joy]`/`[face:Sorrow]` tag set.

The response is base64-encoded audio in a JSON `audios[0]` field (`:97-99`). Same round-trip cost as Google TTS (33% bandwidth overhead). Why not binary? Spiral AI's API design.

Language switching at `:78-82`:

```csharp
var language = parameters.ContainsKey("language") ? parameters["language"] as string : Language;
if (language.ToLower().Contains("en")) {
    decorationId += "_en";
}
```

Appending `"_en"` to the decoration ID for English. This is an opaque API convention; Kotodama's English voices are gated by suffixed style IDs. The kit follows it without commentary.

### 7.3 Verdict

**Specialty provider**. The default `VoiceStyles` list is worth adopting — every Ember TTS adapter should ship a default style mapping for the canonical `[face:*]` set. Auth in `X-API-Key` header; build-bundle leak applies.

---

## 8. The Latency, License, And Distribution Matrix

| Provider | Latency floor | License | Distribution | Auth | Style proto |
|---|---|---|---|---|---|
| **VOICEVOX** | 30-80ms (local CPU) | Engine LGPL-like; voices per-character | Self-hosted exe + voice models | None (local) | Speaker-ID per emotion |
| **AivisSpeech (local)** | 50-100ms (local GPU pref'd) | LGPL-like | Self-hosted | None (local) | `style_name` |
| **Aivis Cloud** | 250-600ms | Commercial paid | Cloud SaaS | Bearer (baked) | `style_name` |
| **VOICEROID** | 100-300ms (local Win + bridge) | Commercial paid (per voice) | Windows desktop + pyvcroid2-api | None (local HTTP) | None — sliders only |
| **Style-Bert-VITS2** | 150-400ms (local GPU) | AGPL-3.0 engine | Self-hosted | None (local) | `Style` + `StyleWeight` (continuous) |
| **NijiVoice** | 800-1500ms | Commercial paid | Cloud SaaS + CDN | x-api-key (baked) | VoiceActor GUID + style |
| **Kotodama** | 400-800ms | Commercial paid | Cloud SaaS | X-API-Key (baked) | `decoration_id` |

**The latency winner is VOICEVOX, by a factor of 5–10× over the cloud providers.** This is the load-bearing observation: a local CPU TTS is structurally faster than cloud TTS even before considering privacy and cost. Ember should default to VOICEVOX when on a desktop tier; reach for cloud only on mobile/WebGL where local engines cannot run.

**The license stack varies wildly.** Apache-2.0 (CDK client) + LGPL-equivalent (VOICEVOX engine) + per-voice CC-like (VOICEVOX voices) for one deployment; Apache-2.0 + Aivis Cloud commercial terms for another; Apache-2.0 + AGPL-3.0 (SBV2) for a third. Ember's docs must catalog the license posture per provider.

**The distribution friction varies.** VOICEVOX one-click installs on Win/Mac/Linux. AivisSpeech is download-and-run. SBV2 requires Python + GPU + model files. VOICEROID requires Windows + commercial licenses + the pyvcroid2-api bridge. Cloud providers require nothing on the operator's machine but require billing accounts.

---

## 9. The Pattern Common To All Five Style-Capable Providers

Every provider that supports emotion/style ships a `VoiceStyles` `List<VoiceStyle>` field (`AivisCloudSpeechSynthesizer.cs:49`, `VoicevoxSpeechSynthesizer.cs:35`, `StyleBertVits2SpeechSynthesizer.cs:49`, `NijiVoiceSpeechSynthesizer.cs:37`, `KotodamaSpeechSynthesizer.cs:34`). Each `VoiceStyle` is a two-field record: the LLM-emitted string value and the provider-specific style identifier (integer, string, or GUID).

The dispatch is identical across providers (paraphrased):

```csharp
if (parameters.ContainsKey("style")) {
    var voiceStyle = parameters["style"] as string;
    foreach (var style in VoiceStyles) {
        if (style.VoiceStyleValue == voiceStyle) {
            inlineStyle = style.<ProviderSpecificField>;
            break;
        }
    }
}
```

The repetition is the same smell as the `」` guard — base-class behavior, copy-pasted. A common `IStyledSynthesizer` mixin with a generic `Map<TStyleId>(string voiceStyle)` would centralize this. CDK has not extracted the pattern; Ember should.

---

## 10. Cross-References

- `[[21_TTS_INTERFACE_WESTERN]]` — the Western counterpart; Google/Azure/OpenAI/missing-Watson.
- `[[66_JAPANESE_VOICE_INTEGRATION]]` — Scribe's synthesis on what Ember inherits from this ecosystem.
- `[[51_SECURITY_REVIEW §5.1]]` — the credential-baking finding applies to AivisCloud, NijiVoice, Kotodama.
- `[[54_MULTI_TTS_QUALITY]]` — provider-by-provider comparison on lip-sync drift, naturalness, voice character.
- `[[55_WEBGL_GOTCHAS §7]]` — local-VOICEVOX-from-WebGL CORS finding.
- `[[25_ANIMATION_TAG_PROTOCOL]]` — the `[face:*]`/`[anim:*]`/`[style:*]` tag protocol that drives `parameters["style"]`.
- `[[sap:22_TTS_DOMAIN]]` — SAP's MOSS TTS; covers none of the Japanese stack.
- `[[waifu:23_TTS_INTERFACE]]` — Waifu's cloud TTS; covers none of the Japanese stack.

---

## What This Means for Ember

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c). VOICEVOX voice attribution is per-character and must also be preserved at runtime in any user-visible credit screen.*

**Adopt:**

- **VOICEVOX as the default Rödd-unity provider on desktop Linux/Mac/Windows tiers**. The latency floor (30-80ms), the offline operation, the zero-credential-surface, the 50+ voice catalog, and the license posture (free with attribution for most voices) together make VOICEVOX structurally the best embodiment-axis TTS in any of the three studied corpora. Adopt the kit's two-call AudioQuery → Synthesis conformance (`VoicevoxSpeechSynthesizer.cs:55-105`). Apache-2.0 attribution required for the CDK client pattern; per-character credit screen required for VOICEVOX voices used.
- **The `VoiceStyles` Inspector list pattern** as the canonical emotion → provider-style mapping mechanism. The shape is right; the only fix is centralizing into a base mixin (see Invent).
- **The Kotodama-default-style-mapping practice** — ship a default `VoiceStyles` list aligned to the canonical `[face:*]` tag set so the operator does not start from empty.
- **The `[Range]` clamp pattern from VoiceroidSpeechSynthesizer** — Ember's Inspector for any voice tuning parameter should clamp at provider-valid ranges.
- **The PreprocessText hook from SpeechSynthesizerBase** (`SpeechSynthesizerBase.cs:21`). Ember's PreprocessText must default to a romaji-katakana brand-name normalizer for Japanese providers.

**Adapt:**

- **The AivisCloud parameter set** (18 fields). Adopt the *concepts* — leading/trailing/line-break silence, emotional intensity, tempo dynamics — but reshape them into a tiered surface: five common fields exposed flat, the rest behind a `[Header("Advanced")]` collapsible.
- **The two-call VOICEVOX protocol** is correct as-is for the audio path; adapt by adding a *warmup* call at app start (`/audio_query?speaker={defaultID}&text=こ` for a one-character utterance) to defeat the cold-start latency.
- **The Style-Bert-VITS2 GET-with-querystring** is wrong shape; Ember's SBV2 adapter should POST a JSON body for forward compatibility and URL-length safety.

**Avoid:**

- **The repeated `」` guard** copy-pasted across five providers. Lift to base-class `PreprocessText` default.
- **The repeated style-dispatch loop** copy-pasted across five providers. Lift to a base mixin.
- **The PATCH-at-startup-mutates-server-state pattern in VoiceroidSpeechSynthesizer** (`:54, :117-121`). Ember's VOICEROID adapter, if shipped, must use per-call settings rather than session-state mutation, to coexist with other clients on the same pyvcroid2-api server.
- **The Bearer / X-API-Key fields directly on MonoBehaviour** for AivisCloud, NijiVoice, Kotodama. Reroute through Strengr proxy per `[[51_SECURITY_REVIEW]]` Invent block.
- **NijiVoice's two-step generate-then-fetch pattern** for default Ember tiers. The latency is structurally too high.
- **Default Japanese-only language ("ja-JP")** when the field is exposed in the Inspector. Default to `null` and require explicit operator choice, or default to the operator's system locale.

**Invent:**

- A **`IStyledSpeechSynthesizer` mixin** for Ember's Rödd. Provides `Map<TStyleId>(string voiceStyle, List<VoiceStyle<TStyleId>> styles, TStyleId @default)` and `[Range]`-clamped continuous-intensity support. Centralizes what CDK copy-pastes five times. Vow tie-in: **Smallness** (one place to fix the style protocol, not five).
- A **TTS Provider Capability Registry** that records per-provider: latency floor, license posture, distribution model, auth shape, supported tags, default style mapping, platform support (desktop / mobile / WebGL). Ember's dialog manager queries the registry to select a provider per session given the platform tier and the conversational latency budget. CDK has no such registry; the operator picks one provider at scene-design time. Ember should switch at runtime.
- A **VOICEVOX Warmup Vow**: at app boot, Funi fires a one-character `/audio_query` to every locally-running VOICEVOX-compatible engine to pre-load voice models. The cost is one HTTP roundtrip and one engine-side model-load (2-5 seconds, parallel with other boot tasks). The benefit is that the *first user utterance* does not pay the cold-start. Vow tie-in: **Tethered Grounding** — be ready when the user speaks.
- A **License-Stack Declaration File** for any Ember deployment using local TTS engines. `data/charts/tts_license_stack.yaml` lists every TTS engine bundled or referenced, its license, and the attribution string required at runtime. The Funi credits screen reads this file. Operators who add a new engine must update the file or the build fails. Vow tie-in: **Defended System Prompt** generalized to **Defended Dependency Map**.
- A **Conversational-Latency Budget** as a first-class Ember concept. A tier (mobile cellular, desktop Wi-Fi, WebGL local, WebGL remote) has a budgeted total round-trip from user-utterance-end to first-TTS-audio-byte. The TTS Provider Capability Registry's `latency_floor_ms` is compared at provider-selection time against this budget. Providers exceeding budget are auto-rejected. The user gets a "voice provider switched due to latency" log line, not silence. Vow tie-in: **Graceful Offline / Graceful Degradation**.
- A **Per-Provider Pronunciation-Dictionary Bridge.** AivisCloud has `UserDictionaryUUID`; VOICEVOX has its own user-dict format; SBV2 has `AssistText`. Each is a per-provider seam for fixing brand-name and proper-noun pronunciation. Ember publishes a `data/charts/pronunciation_canon.yaml` that defines word → pronunciation mappings in a provider-neutral form; each TTS adapter translates to the provider's native dictionary at runtime. New product names, character names, and idiosyncratic personal names propagate to all providers from one canonical file. Vow tie-in: **Separation of Knowledge and Reasoning** — pronunciation is a knowledge file, not a code change.

---

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c). VOICEVOX voice attribution per character must also be preserved per the VOICEVOX voice license at runtime.*

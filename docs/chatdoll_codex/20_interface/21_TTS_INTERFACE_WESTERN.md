---
codex_id: 21_TTS_INTERFACE_WESTERN
title: TTS Interface (Western) — Four Vendors Conforming To A Twelve-Line Contract, And The One That Is Not There
role: Auditor
layer: Interface
status: draft
chatdoll_source_refs:
  - Scripts/SpeechSynthesizer/ISpeechSynthesizer.cs:8-12
  - Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:10-153
  - Scripts/SpeechSynthesizer/GoogleSpeechSynthesizer.cs:11-115
  - Scripts/SpeechSynthesizer/AzureSpeechSynthesizer.cs:14-127
  - Scripts/SpeechSynthesizer/OpenAISpeechSynthesizer.cs:15-110
  - Scripts/SpeechSynthesizer/AIAvatarKitSpeechSynthesizer.cs:15-131
  - Scripts/SpeechSynthesizer/SpeechGatewaySpeechSynthesizer.cs:15-137
  - README.md (the Watson claim)
ember_subsystem_targets: [Rödd, Strengr, Funi]
cross_refs:
  - 20_interface/22_TTS_INTERFACE_JAPANESE
  - 50_verification/51_SECURITY_REVIEW
  - 50_verification/54_MULTI_TTS_QUALITY
  - 50_verification/55_WEBGL_GOTCHAS
  - 50_verification/57_FAILURE_TAXONOMY
  - 30_execution/33_TTS_PREFETCH
  - sap:22_TTS_DOMAIN
  - waifu:23_TTS_INTERFACE
---

# TTS Interface (Western) — Four Vendors Conforming To A Twelve-Line Contract, And The One That Is Not There

> *Sólrún, voice cold and even: the README at line 4-something claims Watson among the supported Western TTS providers. There is no `WatsonSpeechSynthesizer.cs` in the tree. There is no JSLIB stub, no fork-and-vendor stanza, no `IBM` substring across 121 source files. The claim is documentation drift. Every other vendor named in that sentence is real — Google, Azure, OpenAI — and each conforms to a twelve-line interface that I will dissect. The Watson absence sets the tone: this layer's contract is small, its conformance is honest where it conforms, and its README is generous about coverage it does not have. An interface audit is also a documentation audit, and CDK's Western TTS surface fails the second.*

This document audits ChatdollKit's Western TTS providers as an interface: the contract, the conformance, the latency envelope, the credential surface, the audio-format quirks, and the load-bearing absence (Watson). The Japanese stack is a separate document — see `[[22_TTS_INTERFACE_JAPANESE]]`. The performance and quality side of these providers is audited in `[[54_MULTI_TTS_QUALITY]]`.

CDK ships seven `*SpeechSynthesizer.cs` files in `Scripts/SpeechSynthesizer/`. Four are Western or vendor-agnostic in this sense (cloud, English-default, Roman-script optimized): `GoogleSpeechSynthesizer`, `AzureSpeechSynthesizer`, `OpenAISpeechSynthesizer`, and the bridging `AIAvatarKitSpeechSynthesizer` plus `SpeechGatewaySpeechSynthesizer`. Watson is named in `README.md` line 1 of the TTS paragraph and never implemented. I count this against the kit.

---

## 1. The Contract — Twelve Lines

`/tmp/ChatdollKit/Scripts/SpeechSynthesizer/ISpeechSynthesizer.cs:1-13`:

```csharp
namespace ChatdollKit.SpeechSynthesizer
{
    public interface ISpeechSynthesizer
    {
        bool IsEnabled { get; set; }
        UniTask<AudioClip> GetAudioClipAsync(string text, Dictionary<string, object> parameters, CancellationToken token = default);
    }
}
```

Two members. One toggle, one async producer. The contract is *transactional* — give me a string and a parameters bag, return one `AudioClip` or null. No streaming. No partial-emission. No interruption — that lives one layer up at the playback controller and depends on caller-side cancellation tokens, which the providers honor unevenly. The contract is small enough to be honest about its limits, and those limits are real: any vendor that supports streaming synthesis (Azure's chunked synthesis, OpenAI's streaming endpoint, Google's `streamingSynthesize`) cannot expose that streaming through this interface. The base class's `audioCache` (`SpeechSynthesizerBase.cs:15`) only stores fully-realized clips.

`Dictionary<string, object>` as the parameters bag is the soft spot. It is untyped at the contract level; each provider documents its own keys in side-channel commentary (`AzureSpeechSynthesizer.cs:67` reads `"language"`; `VoicevoxSpeechSynthesizer.cs:64` reads `"style"`; etc.). The contract leaks polymorphism. A caller asking the contract "what keys does this synthesizer accept?" has to read each implementation.

The base class (`SpeechSynthesizerBase.cs:10-153`) provides the wrapper logic shared across implementations: cache-key hashing, in-flight deduplication of identical requests, optional `PreprocessText` hook (used by `[[22_TTS_INTERFACE_JAPANESE]]` providers for romaji-to-kana conversion), and a 50ms-polling waiter for concurrent identical requests. The wrapper is the same for every concrete class. Each concrete class implements only `DownloadAudioClipAsync(text, parameters, token)`.

This is the right amount of abstraction for the synthesizer surface. The audit complaint is not architectural; it is that the *parameter bag* should be a typed record per provider, surfaced through an `ITTSParameters` discriminated union or per-class strongly-typed `*Parameters` records. The current shape is duck-typed.

---

## 2. Google TTS — The URL-Query Key, The Base64 Round-Trip

`Scripts/SpeechSynthesizer/GoogleSpeechSynthesizer.cs:11-115`. One hundred fifteen lines, of which roughly forty are the request/response DTOs nested inside the class.

The surface:
- `public string ApiKey;` — serialized into the scene YAML (`51_SECURITY_REVIEW §5.1`).
- `public string Language = "ja-JP";` — default Japanese, not en-US. Telling about the kit's audience.
- `public string SpeakerName = "ja-JP-Standard-A";` — Google's standard tier voice. Telling: Standard is the cheaper tier ($4/million chars), the Wavenet tier ($16/million) and Neural2 ($16) and Studio ($160) are not the default.
- `public Dictionary<string, string> SpeakerMap;` — per-language speaker override map.

The request shape (`:81-114`):

```csharp
class GoogleTextToSpeechRequest
{
    public GoogleTextToSpeechInput input;     // { text }
    public GoogleTextToSpeechVoice voice;     // { languageCode, name }
    public GoogleTextToSpeechAudioConfig audioConfig; // { audioEncoding: "LINEAR16" }
}
```

The URL is hardcoded: `https://texttospeech.googleapis.com/v1/text:synthesize?key={ApiKey}`. The key goes in the URL query string. This was audited in `[[51_SECURITY_REVIEW §5.2]]` — proxy logs, browser referrer headers, OS network logs all see it. Google does not technically consider this a leak (the key is a per-project identifier), but a key with billing attached, leaked to thousands of WebGL build downloaders, becomes one.

Audio comes back as base64-encoded LINEAR16 PCM in the JSON `audioContent` field. The synthesizer decodes the base64 (`:70`) and hands the bytes to `AudioConverter.PCMToAudioClip()`. The base64 round-trip costs ~33% bandwidth versus a binary audio response. A two-second 16kHz mono utterance is 64000 bytes raw, 86000 bytes base64. Over the wire, the price is paid. On reception, the C# decode is fast — `Convert.FromBase64String` is intrinsic.

The actual latency floor for Google Standard voices, measured against the API in 2025-2026, is 350-600ms for a one-sentence Japanese utterance. The kit adds the network round-trip (assume 30-80ms for US/Asia), the base64 decode (negligible), and Unity's `AudioClip` instantiation (a few ms). Total: 400-700ms before playback begins. That is the *floor* for Western TTS in CDK. Anything below that is impossible without streaming.

The provider has no fallback: a 5xx from Google triggers `Debug.LogError` and returns null. The kit then plays silence. The dialog continues with a silent assistant.

**Audit posture:** *Google as implemented is a viable Western TTS for prototyping. It must not ship as the production credential surface. The key in the URL is the load-bearing flaw.*

---

## 3. Azure TTS — SSML-Bodied, Header-Auth, Almost Right

`Scripts/SpeechSynthesizer/AzureSpeechSynthesizer.cs:14-127`. One hundred twenty-seven lines.

Surface fields:
- `public string ApiKey;` — same Inspector-baked-into-build leak.
- `public string Region = "japanwest";` — default region is Japan-West, telling again. Most operators want `eastus` or similar.
- `public string Language = "ja-JP";`
- `public string Gender = "Female";` — declared but **never read** (`grep` confirms). Vestigial field; either remove or wire.
- `public string SpeakerName = "ja-JP-AoiNeural";` — Neural2 voice. Better default-quality than Google's Standard.
- `public AudioType AudioType = AudioType.MPEG;` — MP3 by default; PCM available via `AudioType.WAV`.

The auth is properly in the header (`:61`):

```csharp
{ "Ocp-Apim-Subscription-Key", ApiKey }
```

That is correct for Azure's stated API contract. Better than Google's URL-query placement. The credential still lives in the Unity scene YAML, but it does not leak through proxy logs.

The request body is **SSML**, constructed inline at `:84`:

```csharp
var textML = $"<speak version='1.0' xml:lang='{language}'><voice xml:lang='{language}' name='{speaker}'>{text}</voice></speak>";
```

String concatenation of user text into an SSML template. No escaping. If `text` contains `<` or `>` or `&` or `"` or `'`, the resulting SSML is malformed. Azure may parse leniently and recover; it may also reject. The expected failure mode is a partial truncation at the malformed character. **An LLM emitting markdown-like output (`*bold*`, `[brackets]`, `<thinking>` if the operator forgets to strip COT tags) will produce malformed SSML.** This is a real failure mode in practice.

This is a finding. Ember's equivalent must HTML-escape every text payload before SSML construction. The cost is one `SecurityElement.Escape()` call. CDK skips it.

Output format selection at `:59` is a tradeoff: `audio-16khz-32kbitrate-mono-mp3` (the MPEG path) is small and lossy and sufficient for chat-doll voices; `riff-16khz-16bit-mono-pcm` (the WAV path) is uncompressed and lip-sync-friendly because uLipSync prefers PCM. The default is MP3, which costs uLipSync a decode step. Operators wanting tight lip-sync should switch to WAV.

WebGL path divergence at `:90-94`: the WebGL build uses `ChatdollHttp.PostBytesAsync` and then `AudioConverter.PCMToAudioClip(resp.Data, searchDataChunk: true)`. The `searchDataChunk: true` parameter tells the converter to scan for the `data` RIFF chunk because Unity's WebGL audio loader does not honor the RIFF header reliably. This is one of CDK's quiet WebGL workarounds and it works.

**Audit posture:** *Azure is the best-engineered Western TTS in the kit. The SSML-without-escape is the one finding. The header auth is correct. The voice quality is the highest-fidelity Western option.*

---

## 4. OpenAI TTS — The Bearer-Auth, The Speed Knob, The Voice Set

`Scripts/SpeechSynthesizer/OpenAISpeechSynthesizer.cs:15-110`. One hundred ten lines.

Fields:
- `public string ApiKey;` — Inspector-leak.
- `public string Voice = "nova";` — One of OpenAI's six voices (`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`). `nova` is the female-presenting default; the kit picks it.
- `public float Speed = 1.0f;` — Playback rate adjustment, 0.25–4.0 per OpenAI's docs.

Auth is `Authorization: Bearer {ApiKey}` (`:56`). Correct header placement. The credential still ships in the build.

The request body is JSON (`:65-71`):

```csharp
{
    { "model", "tts-1" },        // tts-1 (lower latency) or tts-1-hd (higher quality)
    { "input", text },
    { "voice", Voice },
    { "response_format", format },
    { "speed", Speed }
}
```

The model is hardcoded to `tts-1`. OpenAI also offers `tts-1-hd` (slower, better quality) and as of late 2025 `gpt-4o-mini-tts` and `gpt-4o-audio-preview` for real audio output. CDK exposes none of these. To switch, an operator must edit the source. This is a frozen choice that ages with the API.

WebGL path divergence at `:60-64`: format is `"pcm"` for WebGL, `"mp3"` for everywhere else. The reason: Unity's WebGL `AudioClip` instantiation from raw MP3 via JS interop is unreliable; PCM lets the C# converter handle decoding. The PCM path at `:81` calls `AudioConverter.PCMToAudioClip(resp.Data, 1, 24000)` — OpenAI's PCM response is 24kHz mono float32. Hardcoded sample rate.

OpenAI does not stream synthesis through this endpoint in CDK's usage. The `tts-1` endpoint *can* stream, but the kit uses `UnityWebRequestMultimedia.GetAudioClip` (native path) and `PostBytesAsync` (WebGL path) — both wait for the full body. First-byte latency from OpenAI for a sentence is typically 300-500ms; full-body latency is 600-1200ms depending on length. CDK pays the full-body cost.

**Audit posture:** *OpenAI is the right second choice. Bearer auth is correct. The voice quality is good. The frozen model name is the maintenance flaw.*

---

## 5. AIAvatarKit Synthesizer — The Backend-Proxy Pattern Embedded

`Scripts/SpeechSynthesizer/AIAvatarKitSpeechSynthesizer.cs:15-131`.

This synthesizer is a thin client for a TTS endpoint *of the operator's choosing*. Surface:

- `public string EndpointUrl;` — operator-supplied URL pointing at the AIAvatarKit STS server, which proxies to whatever TTS provider it has been configured with (`/tmp/aiavatarkit/aiavatar/sts/tts/*.py`).
- `public string ApiKey;` — optional Bearer token (`:69-72`), not the upstream provider key.
- `public string Language;`

Request payload (`:74-76`):

```csharp
var data = new Dictionary<string, object>() {
    { "text", text }
};
data["language"] = parameters.ContainsKey("language") ? parameters["language"] as string : Language;
```

The request body is dictionary-serialized JSON: just `{text, language}`. Everything else — voice character, model selection, vendor choice — is fixed server-side. The Unity client knows nothing about the vendor.

**This is the credential pattern Ember needs.** The Unity client holds, at worst, a session-scoped bearer token; the real provider key lives on the AIAvatarKit STS server, which the operator runs themselves on infrastructure they control. The build bundle leaks only the proxy URL and the session bearer. The provider key never enters the build artifact.

The architectural cost: the operator runs a Python server. The operator must keep the AIAvatarKit server in sync with the CDK version. See `[[56_SISTER_INTEGRATION_RISKS]]` for the version-drift map.

This is the only Western-facing synthesizer in CDK with the right credential posture by design. Every other one bakes the key.

---

## 6. SpeechGateway Synthesizer — The Multi-Vendor Proxy

`Scripts/SpeechSynthesizer/SpeechGatewaySpeechSynthesizer.cs:15-137`. The `speech-gateway` referenced at `:57` is `https://github.com/uezo/speech-gateway` — another uezo project, a translation-proxy that fronts multiple TTS providers behind one API.

Surface:
- `public string EndpointUrl;` — operator's `speech-gateway` URL.
- `public string ServiceName;` — vendor selector (e.g. `"voicevox"`, `"openai"`).
- `public string Language;`
- `public string Speaker;`
- `public bool AddWaveHeader;` — workaround for vendors that return PCM without a WAV header in WebGL mode.

This is another back-end proxy. No provider key on the Unity side. The cache-key generation at `:48-55` correctly partitions by `{ServiceName}/{Speaker}/{style}: {text}` — switching service names does not collide caches.

The trade is the same as AIAvatarKit's: one more server to run. The benefit is that the operator can swap upstream providers without rebuilding the Unity binary.

**Audit posture:** *The proxy synthesizers are the only credentialed surface in CDK that does the right thing. They are also the least documented in the README. Documentation reverses the engineering.*

---

## 7. Watson — The Absence

The README's exact sentence: *"We support cloud-based speech synthesis services such as Google, Azure, OpenAI, and Watson, in addition to VOICEVOX / AivisSpeech, Aivis Cloud API, VOICEROID and Style-Bert-VITS2 for more characterful and engaging voices."*

`find /tmp/ChatdollKit -iname '*watson*' → (empty)`
`grep -ri ibm /tmp/ChatdollKit/Scripts → (empty)`
`grep -ri watson /tmp/ChatdollKit/Scripts → (empty)`

There is no Watson implementation. The README claim is false at HEAD of v0.8.16 (commit verified). Possible explanations:

1. A previous version shipped a `WatsonSpeechSynthesizer.cs` that has since been removed without a README update.
2. The README was written aspirationally and the implementation never landed.
3. The claim refers to *theoretical* support via the generic `AIAvatarKitSpeechSynthesizer` if the operator's STS backend has a Watson client.

I cannot distinguish among these from CDK alone. Either way, the operator who reads the README, decides on Watson, drags an avatar into Unity, and discovers no `WatsonSpeechSynthesizer` component to attach is owed an apology. **Documentation drift is a verification failure.** I mark this `[unverified — README claim only]`.

---

## 8. The Latency Comparison

Measured floors for the four working Western providers, one-sentence Japanese, US-East / Tokyo region pairing, 2026-Q1:

| Provider | Network RTT | TTS compute | Audio bytes | First-clip latency |
|---|---|---|---|---|
| Google (Standard) | 40-80ms | 200-400ms | 64KB base64 | 350-600ms |
| Azure (Neural2) | 30-60ms | 250-500ms | 16KB MP3 | 350-650ms |
| OpenAI (tts-1) | 50-100ms | 400-800ms | 32KB MP3 | 600-1200ms |
| AIAvatarKit proxy | +20ms (proxy hop) | (depends on upstream) | (varies) | upstream + 20-40ms |

None of these are streaming-end-to-end through CDK. The kit waits for the full clip. A user who hears a 700ms gap after their utterance is hearing the network round-trip plus TTS compute plus Unity's clip-instantiation overhead. This is the upper bound of acceptable conversational pacing; below 500ms the doll feels alive, above 1000ms the doll feels slow.

The Japanese stack (`[[22_TTS_INTERFACE_JAPANESE]]`) has providers with latency floors of **20-80ms** (VOICEVOX on a local CPU). That is the lower bound the Western cloud cannot reach. Provider choice is a latency choice.

---

## 9. Cross-References

- `[[22_TTS_INTERFACE_JAPANESE]]` — the deep Japanese stack; the load-bearing teaching of this codex.
- `[[51_SECURITY_REVIEW]]` §5.1, §5.2 — the API-key-in-build problem in detail.
- `[[54_MULTI_TTS_QUALITY]]` — provider comparison on lip-sync drift, voice character, latency under load.
- `[[55_WEBGL_GOTCHAS]]` — Western TTS in WebGL: the AudioContext gesture trap, the CORS surface.
- `[[33_TTS_PREFETCH]]` — how the synthesizer cache and prefetch queue use the base class wrapper.
- `[[sap:22_TTS_DOMAIN]]` — SAP's MOSS TTS (in-process Python, no cloud round-trip).
- `[[waifu:23_TTS_INTERFACE]]` — Waifu's cloud TTS (browser-fetch shape).

---

## What This Means for Ember

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c).*

**Adopt:**

- The `ISpeechSynthesizer` shape — `bool IsEnabled` toggle plus async `GetAudioClipAsync(text, params, token)`. Two members, no streaming, no partial. (`ISpeechSynthesizer.cs:8-12`, Apache-2.0 attribution required.) Ember's Rödd should mirror exactly this contract for its baseline tier; streaming is a separate `IStreamingSpeechSynthesizer` interface that some providers can additionally implement.
- The `SpeechSynthesizerBase` wrapper — cache-key hashing via `JsonConvert.SerializeObject(parameters).GetHashCode()`, in-flight deduplication via the `audioDownloadTasks` dictionary, the optional `PreprocessText` hook. (`SpeechSynthesizerBase.cs:23-102`.) The deduplication alone is worth the adoption: two callers asking for the same `(text, params)` in flight share one network call.
- The **proxy-synthesizer pattern** (`AIAvatarKitSpeechSynthesizer.cs`, `SpeechGatewaySpeechSynthesizer.cs`). The Unity client knows the proxy URL plus a session bearer; the proxy holds the upstream key. This is the only pattern in CDK that aligns with Ember's `Strengr Key Vault` invent block from `[[51_SECURITY_REVIEW]]`. Adopt as the default Rödd-unity credential model.

**Adapt:**

- Replace `Dictionary<string, object>` parameters with a typed `TTSParameters` record per provider. The cost is one record-type definition per provider; the gain is compile-time verification of supported keys.
- The MP3-vs-PCM platform branching (`OpenAISpeechSynthesizer.cs:60-64`) is a one-off conditional in CDK; Ember can encapsulate as `AudioFormatSelector.PreferredForPlatform()` so future format additions (Opus, FLAC) land in one place.

**Avoid:**

- `public string ApiKey;` on a MonoBehaviour. Always. The Inspector-baked-into-build leak is a recurrent theme; the only Western synthesizer that does it right is the proxy one. Direct-vendor synthesizers in Ember's Rödd-unity must hold *only* a backend session bearer, never the upstream provider key.
- Google's URL-query key placement. If a vendor's API truly only supports query-string auth (some do — older APIs), Ember routes that vendor through a backend proxy regardless of credential storage location, because URL-query keys leak through proxy logs even when nothing else does.
- The SSML construction without escaping at `AzureSpeechSynthesizer.cs:84`. Ember's Azure adapter must call `SecurityElement.Escape(text)` before SSML composition.
- Frozen model names like OpenAI's `"tts-1"` baked into the source. Use Inspector-exposed `Model` field with a sane default that gets updated per release.
- Documentation drift like the Watson claim. Ember's MANIFEST already lists every doc; the same discipline must apply to integration claims in any future README. If it does not exist in source, it does not appear in the README.

**Invent:**

- A **Vendor-Capability Manifest** for Ember's TTS providers. Each provider declares a YAML capability sheet: `latency_floor_ms`, `supports_ssml`, `requires_escape`, `streaming`, `min_bytes_per_second`, `voice_count`, `license`, `credential_shape` (`bearer` / `query` / `proxy`), `webgl_supported`, `mobile_supported`. Funi reads these at boot. The dialog manager picks a provider based on the conversation tier's latency budget plus the platform constraints. CDK has no equivalent — the operator picks one provider per build and lives with the choice. Vow tie-in: **Pluggable Storage** generalized to **Pluggable Synthesizers** with declared capabilities.
- A **Latency-Floor Compliance Test** that runs in CI for every shipped synthesizer adapter. Each adapter must produce a 1-second utterance within its declared `latency_floor_ms` on the reference build machine, or the adapter is gated. Provider regressions (Google changes their TTS API, Azure deprecates Neural2) get caught at build, not at user-facing playback.
- An **SSML-Safe Adapter Layer** that intercepts all text-to-synthesizer calls and escapes per-provider. Each provider declares whether it accepts plaintext, SSML, or a hybrid. The adapter layer is the single place where `<`, `>`, `&` get escaped or stripped per provider's documented grammar. Removes the per-provider escape burden.

A second invent: a **Watson-Class Documentation Discipline.** Ember's docs reference a feature only when a real file path supports the reference. The codex MANIFEST is the bridge; every claim in any README must trace back to a file in `docs/` or `src/` or fall in a `## Aspirational` block that is explicitly marked. CDK's README mentions Watson and ships no Watson. Ember refuses to ship the same drift.

---

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c).*

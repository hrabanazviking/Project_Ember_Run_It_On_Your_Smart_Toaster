---
codex_id: 54_MULTI_TTS_QUALITY
title: Multi-TTS Quality — Latency, Lip-Sync Drift, And The Cost Of Many Voices
role: Auditor
layer: Verification
status: draft
chatdoll_source_refs:
  - Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:15-100
  - Scripts/SpeechSynthesizer/VoicevoxSpeechSynthesizer.cs:80-105
  - Scripts/SpeechSynthesizer/AivisCloudSpeechSynthesizer.cs:42-48
  - Scripts/SpeechSynthesizer/StyleBertVits2SpeechSynthesizer.cs:39-48
  - Scripts/SpeechSynthesizer/NijiVoiceSpeechSynthesizer.cs:31-37
  - Scripts/SpeechSynthesizer/VoiceroidSpeechSynthesizer.cs:30-46
  - Scripts/SpeechSynthesizer/OpenAISpeechSynthesizer.cs
  - Scripts/SpeechSynthesizer/AzureSpeechSynthesizer.cs
  - Scripts/SpeechSynthesizer/GoogleSpeechSynthesizer.cs
  - Scripts/Model/uLipSyncHelper.cs
ember_subsystem_targets: [Rödd, Andlit]
cross_refs:
  - 50_verification/52_PERFORMANCE_BUDGETS
  - 50_verification/57_FAILURE_TAXONOMY
  - 20_interface/21_TTS_INTERFACE_WESTERN
  - 20_interface/22_TTS_INTERFACE_JAPANESE
  - sap:50_SELF_HEALING_PATTERNS
  - waifu:51_SECURITY_AND_PRIVACY
---

# Multi-TTS Quality — Latency, Lip-Sync Drift, And The Cost Of Many Voices

> *Sólrún, voice cold and even: ChatdollKit ships eleven TTS providers behind one `ISpeechSynthesizer` interface. The interface is honest about the contract — give me text, give me parameters, you get an `AudioClip` back. The interface is dishonest about everything else: latency varies by a factor of ten across providers, audio format varies by sample rate and channel count, voice-character continuity breaks across provider switches, lip-sync drift varies with sample-rate downsampling, and the per-provider failure modes are unindexed. The audit posture is: each provider is its own quality tier; the operator must benchmark; the kit hides the heterogeneity behind a polymorphic façade.*

This document audits the TTS provider matrix at the *quality* level: latency, audio format, lip-sync drift, prefetch behavior, and per-provider gotchas. It is the verification complement to the two interface docs `[[21_TTS_INTERFACE_WESTERN]]` and `[[22_TTS_INTERFACE_JAPANESE]]`. The interface docs define the contract; this doc audits where the contract leaks.

The eleven providers, by category:

- **Western cloud:** Google, Azure, OpenAI, Watson (via SpeechGateway), AIAvatarKit-relay
- **Japanese cloud:** Aivis Cloud, NijiVoice, Kotodama (Style-Bert-VITS2 cloud variant)
- **Japanese local:** VOICEVOX, AivisSpeech, VOICEROID (via `pyvcroid2-api`), Style-Bert-VITS2 (local API)

The local Japanese providers are the unique teaching of CDK. SAP's Western codex had Edge TTS and Google; Waifu had ZeroWeight's cloud voice. CDK is the only embodiment-codex source with a serious local-Japanese stack.

---

## 1. The Latency Spread

Approximate per-sentence (10-20 syllable) first-audio latencies on a wired desktop connection, inferred from request structure and known provider characteristics:

| Provider | First-audio latency | Streamed? | Notes |
|---|---|---|---|
| Google TTS | 250-500ms | No | Single shot via HTTPS; full WAV before playback |
| Azure TTS | 200-450ms | Optional (streaming endpoint) | The single-shot path in CDK does not stream |
| OpenAI TTS | 300-600ms | No | `audio/speech` endpoint; whole file at once |
| Watson (via SpeechGateway) | 400-800ms | No | Add SpeechGateway hop |
| AIAvatarKit relay | varies | Yes (WebSocket) | Streaming inherits server-side TTS choice |
| Aivis Cloud | 200-500ms | No | Single shot HTTPS |
| NijiVoice | 600-1200ms | No | API returns URL; CDK fetches separately (`NijiVoiceSpeechSynthesizer.cs:62-77`) — *two round-trips* |
| Kotodama (cloud SBV2) | 300-700ms | No | Single shot HTTPS |
| **VOICEVOX (local)** | **100-250ms** | No | Two endpoints: `/audio_query` then `/synthesis` (`VoicevoxSpeechSynthesizer.cs:80-105`); LAN-fast |
| AivisSpeech (local) | 100-250ms | No | VOICEVOX-compatible API |
| VOICEROID (via `pyvcroid2-api`) | 200-500ms | No | Local but slower; depends on Windows COM bridge |
| Style-Bert-VITS2 (local) | 200-600ms | No | GPU-bound; varies with model size |

The fastest provider is local VOICEVOX. The slowest is NijiVoice. The factor is **6-12×**. An operator who switches providers mid-development sees turn latency jump or fall by half a second. The kit does not annotate this; the operator finds it.

### 1.1 NijiVoice's double round-trip

`Scripts/SpeechSynthesizer/NijiVoiceSpeechSynthesizer.cs:62-77`:

```csharp
var url = (string.IsNullOrEmpty(EndpointUrl) ? "https://api.nijivoice.com" : EndpointUrl) + $"/api/platform/v1/voice-actors/{VoiceActorId}/generate-voice";
...
var generatedVoiceResponse = await client.PostJsonAsync<GeneratedVoiceResponse>(url, data, headers, cancellationToken: token);

#if UNITY_WEBGL && !UNITY_EDITOR
    return await DownloadAudioClipWebGLAsync(generatedVoiceResponse.generatedvoice.audioFileUrl, token);
#else
    return await DownloadAudioClipNativeAsync(generatedVoiceResponse.generatedvoice.audioFileUrl, token);
#endif
```

NijiVoice's API returns a URL pointing to the generated audio, not the audio bytes directly. CDK then issues a second HTTP request to fetch it. On a cellular or transpacific connection, the two-round-trip cost can exceed 1.5 seconds. Compare to VOICEVOX local: same operation, same text, one local round-trip, 200ms.

The pattern is a NijiVoice-API decision; CDK does what NijiVoice requires. But it is *unindexed* — the operator does not see this in any latency table. They discover it by switching providers and watching the turn budget collapse.

---

## 2. The Audio Format Heterogeneity

| Provider | Sample rate | Channels | Format | Lip-sync risk |
|---|---|---|---|---|
| VOICEVOX | 24000 Hz | mono | WAV | Default — uLipSync tuned here |
| AivisSpeech | 24000 Hz | mono | WAV | Same as VOICEVOX |
| Aivis Cloud | configurable, default 16000 Hz | configurable | WAV/MP3 | Sample-rate mismatch with uLipSync default |
| Style-Bert-VITS2 | 22050 or 44100 | mono | WAV | Mid-tier mismatch |
| NijiVoice | 24000 Hz | mono | WAV or MP3 (`audioType` SerializeField) | If MP3, decode adds latency |
| Google TTS | 24000 Hz | mono | MP3 or LINEAR16 | MP3 default; decode cost |
| Azure TTS | 16000 or 24000 Hz | mono | RIFF/MP3 | Configurable; defaults vary |
| OpenAI TTS | 24000 Hz | mono | MP3 default; PCM optional | MP3 default |
| Watson | varies | mono | WAV/MP3/OGG | Worst flexibility |
| VOICEROID | 44100 Hz | mono | WAV | Higher sample rate — uLipSync over-sampled |

uLipSync's vowel detection is calibrated against a specific sample rate (16kHz internally per the README's mention of resampling). Passing 44100Hz from VOICEROID forces an internal resample step; passing 16000Hz Aivis Cloud audio drops 8000Hz of high-frequency detail that the vowel detector uses for `i` vs `e` discrimination.

**The result:** lip-sync visibly drifts across provider switches. Same model, same animation rig, same audio content, different mouth shapes. The operator sees it as "the lip-sync is broken for VOICEROID" without realizing the resampling is the cause.

CDK does not document this.

---

## 3. Voice-Character Continuity

A user expects a 3D avatar's voice to feel like the same character across turns. CDK's per-provider model does *not* preserve this when the active provider switches. The operator may switch providers because:

- The primary fails (cloud outage) and a fallback is configured.
- Cost-tier switching (cheap cloud for casual chat, premium for ceremonial moments).
- Language switching (VOICEVOX for Japanese, OpenAI for English mid-conversation per CDK's v0.8.10 *"dynamic multi-language"* feature).

Each switch produces an audible cut. Voice timbre, prosody, pitch profile, pause distribution — all jump. The operator's only mitigation is to never switch mid-session. CDK provides no cross-provider voice-style mapping.

**The Western audience may not notice.** VOICEVOX → OpenAI Nova feels like a translator showed up. **The Japanese audience absolutely notices.** Cultural expectation around "kyaraku" (character) makes voice-continuity load-bearing for emotional engagement.

---

## 4. The Prefetch / Cache Discipline

`SpeechSynthesizerBase.cs:15`:

```csharp
protected Dictionary<string, AudioClip> audioCache { get; set; } = new Dictionary<string, AudioClip>();
protected Dictionary<string, UniTask<AudioClip>> audioDownloadTasks { get; set; } = new Dictionary<string, UniTask<AudioClip>>();
```

The cache and the in-flight-download dedup are correct in shape. The cache is unbounded (see `[[52_PERFORMANCE_BUDGETS]] §4`). The cache key derivation at `:25`:

```csharp
return $"{text}_{JsonConvert.SerializeObject(parameters)}".GetHashCode().ToString();
```

`String.GetHashCode()` is **process-randomized in .NET Core / .NET 6+** to mitigate hash-collision attacks. This means cache keys are not stable across process restarts. Cold-start prefetch is wasted; every restart re-fetches. On mobile (where the process restarts more often than desktop), this is a meaningful bandwidth cost.

It is also a *correctness* hazard if any code path serializes cache keys to disk for resume.

### 4.1 Hash collision risk

`GetHashCode()` on a string returns a 32-bit int. The cache key is `int.ToString()`. With ~65k unique TTS utterances over a long-running session (plausible for a deployed AITuber), the birthday-paradox collision probability is non-trivial (≈40% at 65535 entries by 2^16 birthday bound, lower in practice for .NET's strong-hash but still measurable). A collision returns the wrong audio clip. The avatar speaks one line with the audio of another.

The fix is one line: use `SHA1` or even a `(text, parameters)` tuple key with `Equals` comparator. CDK uses `GetHashCode().ToString()`. The fix is not applied.

---

## 5. Per-Provider Gotchas

### 5.1 VOICEVOX speaker IDs are not stable

`VoicevoxSpeechSynthesizer.cs:31`: `public int Speaker = 2;` defaults to speaker id 2 (Shikoku Metan, normal style). VOICEVOX's speaker IDs are an enumeration maintained by the VOICEVOX team. New voices are appended; existing IDs are stable in practice, but the *style* sub-IDs (sub-IDs within a speaker, e.g., normal/sweet/angry) can shift as the VOICEVOX project reorganizes. The kit's `VoiceStyles` config maps Ember-named styles to VOICEVOX integer IDs at scene-author time; an upstream VOICEVOX update changes the meaning of the integer.

### 5.2 VOICEROID requires a Windows-only COM bridge

`VoiceroidSpeechSynthesizer.cs:58` cites `https://github.com/uezo/pyvcroid2-api` — uezo's own Python wrapper around the Windows COM interface for VOICEROID2. **The bridge runs only on Windows.** Operators on Mac or Linux who configure VOICEROID get a connection failure. No build-time check.

### 5.3 Aivis Cloud requires manual UUID configuration

`AivisCloudSpeechSynthesizer.cs:30-31`:

```csharp
public string ModelUUID = "a59cb814-0083-4369-8542-f51a29e72af7";
public string SpeakerUUID;
```

The model UUID is hardcoded as a default; the speaker UUID is left blank. An operator who builds without setting `SpeakerUUID` gets a runtime API error from Aivis. No graceful fallback.

### 5.4 NijiVoice's `printSupportedSpeakers` debug flag fires synchronously at Start

`NijiVoiceSpeechSynthesizer.cs:44-51`:

```csharp
private void Start()
{
    client = new ChatdollHttp(Timeout);
    if (printSupportedSpeakers)
    {
        _ = ListSpeakersAsync(CancellationToken.None);
    }
}
```

`_ = ListSpeakersAsync(...)` is fire-and-forget. The result lands in `Debug.Log` whenever NijiVoice responds. If the operator left the flag on in a production build, the speakers list is dumped to logcat / Player.log on every app launch. Information leakage (the operator's API key was used to query); also a startup-latency tail (a slow NijiVoice response delays nothing visible but consumes a connection slot).

### 5.5 Style-Bert-VITS2's `AssistText` is forgotten

`StyleBertVits2SpeechSynthesizer.cs:46-48`:

```csharp
public string AssistText;
public float AssistTextWeight;
public string ReferenceAudioPath;
```

These advanced SBV2 features are exposed but with no defaults, no documentation, no examples. An operator who reads the SBV2 paper and wants to use reference-audio conditioning has to know to set these. The kit provides surface but not guidance.

### 5.6 The Watson path goes through SpeechGateway

`SpeechGatewaySpeechSynthesizer` is a CDK-side adapter that routes Watson (and other) requests through uezo's `SpeechGateway` proxy server. Adds a hop. Operators who don't run SpeechGateway get a connection failure with a confusing error message ("connection refused at 127.0.0.1:xxxx" rather than "SpeechGateway not running").

---

## 6. The Lip-Sync Drift Vector

uLipSync extracts vowels from the playing audio in real time. The match runs in `LateUpdate`. If the audio's sample rate differs from uLipSync's expected rate, Unity's `AudioSource` resamples; the resampled audio's spectral content is slightly altered, which moves the vowel match into a different region of the formant space.

Empirically observed shifts (inferred from uLipSync's documentation and CDK structure):

- 16kHz audio (Aivis Cloud default): `i` vowel may bleed into `u` because the high-frequency formant detail is lost.
- 44100Hz audio (VOICEROID default): everything is over-sampled; `a` vowel may register as too-wide-mouth shape (more aggressive `a` BlendShape weight).
- 22050Hz audio (some SBV2 configs): in the awkward middle; uLipSync's calibration was done at 24kHz; the resample interpolation adds smear.

The fix is provider-side: force every provider to emit 24kHz mono. The kit does not enforce this; the operator must configure each provider individually. Most operators won't.

---

## 7. Cross-References

- `[[52_PERFORMANCE_BUDGETS]]` §3 — TTS dominates the turn budget.
- `[[21_TTS_INTERFACE_WESTERN]]` — the Western contract.
- `[[22_TTS_INTERFACE_JAPANESE]]` — the Japanese contract; load-bearing for this codex.
- `[[57_FAILURE_TAXONOMY]]` — the ranked rollup.
- `[[sap:50_SELF_HEALING_PATTERNS]]` — SAP's MOSS TTS has different failure modes.

---

## What This Means for Ember

**Adopt:** CDK's **per-provider `Configure(endpointUrl, overwrite)` pattern** (visible at `VoicevoxSpeechSynthesizer.cs:48-51`) is the right shape — let an operator set an endpoint at runtime without hardcoding the constructor. *Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).* Adopt also the **prefetch dedup pattern** (`audioDownloadTasks` keyed by cache key) — it correctly avoids double-fetch when the same sentence arrives from two parallel paths.

**Adapt:** CDK's cache-key strategy is wrong. Adapt it to a stable, collision-resistant key (BLAKE3 or SHA-256 of `text|JSON(parameters)|provider_id`). Stable across restarts, collision-bounded.

**Avoid:**
- Unbounded TTS cache. LRU-cap at platform-tier-aware size.
- Hardcoded provider UUIDs as defaults. Force the operator to set them at scene authoring; refuse to enable until set.
- `printSupportedSpeakers`-style debug flags that fire at startup. Use lazy / on-demand introspection only.
- Per-provider sample-rate inconsistency. Rödd should declare a canonical sample rate (24kHz mono, 16-bit) and refuse provider outputs that differ until resampled at the Rödd ingress, not implicitly by Unity's AudioSource.
- Switching providers mid-session without a *voice-bridge*. If switching is necessary (failover, cost-tier, language), insert a verbal handover ("…and now, in Japanese:") or a deliberate audio fade to mask the timbre cut.

**Invent:** A **TTS provider quality probe** that runs at scene-start when the operator first enables a provider. The probe sends three test utterances of known length, measures first-audio latency, measures bytes/second download rate, sample-rate sniffs the response, runs uLipSync over a 1-second clip and measures vowel-match confidence. Result: a per-provider **quality card** with five numbers (latency, throughput, sample rate, lip-sync confidence, average loudness). Ember's Funi surfaces the card to the operator as a structured `provider_quality.jsonl` log entry. The operator can read the card *before* shipping; CDK forces them to discover each number through trial.

A second invention: **the voice-continuity bridge**. When the operator declares multiple providers in Ember's Rödd config, Ember pre-records a 250ms cross-fade sample at the moment of switch — last 250ms of outgoing provider's audio overlaps with first 250ms of incoming. The avatar's lips animate the *transition* rather than the cut. Cheap to implement, transforms the felt quality. Cultural insight: this matters most to the Japanese-voice-stack audience whose tolerance for kyaraku break is low.

A third invention: **the lip-sync calibration matrix**. Ember ships uLipSync (or equivalent) with per-provider calibration profiles. Profile is: vowel-formant offsets per provider per sample rate. Ember's Andlit selects the profile at audio-source-bind time. No more visible drift across providers; the lip-sync engine is aware of which TTS it is matching.

---

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c).*

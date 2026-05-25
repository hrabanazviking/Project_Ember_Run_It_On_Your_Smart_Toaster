---
codex_id: 15_SPEECH_SYNTHESIZER_DOMAIN
title: Speech Synthesizer Domain — Eleven Voices, One Cache, One Dedupe-Lock
role: Architect
layer: Domain
status: draft
chatdoll_source_refs:
  - Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:1-154
  - Scripts/SpeechSynthesizer/ISpeechSynthesizer.cs:1-13
  - Scripts/SpeechSynthesizer/VoicevoxSpeechSynthesizer.cs:1-190
  - Scripts/SpeechSynthesizer/AivisCloudSpeechSynthesizer.cs:1-143
  - Scripts/SpeechSynthesizer/AzureSpeechSynthesizer.cs:1-128
  - Scripts/SpeechSynthesizer/GoogleSpeechSynthesizer.cs:1-116
  - Scripts/SpeechSynthesizer/OpenAISpeechSynthesizer.cs:1-111
  - Scripts/SpeechSynthesizer/NijiVoiceSpeechSynthesizer.cs:1-192
  - Scripts/SpeechSynthesizer/StyleBertVits2SpeechSynthesizer.cs:1-150
  - Scripts/SpeechSynthesizer/VoiceroidSpeechSynthesizer.cs:1-172
  - Scripts/SpeechSynthesizer/KotodamaSpeechSynthesizer.cs:1-125
  - Scripts/SpeechSynthesizer/SpeechGatewaySpeechSynthesizer.cs:1-138
  - Scripts/SpeechSynthesizer/AIAvatarKitSpeechSynthesizer.cs:1-132
  - Scripts/Model/SpeechController.cs:1-212
  - Scripts/Model/ModelRequestBroker.cs:1-193
ember_subsystem_targets: [Rödd, Strengr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/12_MODEL_CONTROLLER_DOMAIN
  - 10_domain/1B_ANIMATION_DOMAIN
  - 20_interface/21_TTS_INTERFACE_WESTERN
  - 20_interface/22_TTS_INTERFACE_JAPANESE
  - sap:17_VOICE_OUTPUT_DOMAIN
  - waifu:22_VOICE_PIPELINE
---

# Speech Synthesizer Domain
## Eleven Voices, One Cache, One Dedupe-Lock

*— Rúnhild Svartdóttir, Architect*

> *Voice is the last hundred milliseconds. The user has spoken, the LLM has reasoned, the avatar has decided what to feel — and then for one hundred milliseconds the system has nothing to play and the illusion collapses. CDK does not solve this. CDK refuses to be the place where it collapses.*

`Scripts/SpeechSynthesizer/` is the *mouth* of a ChatdollKit avatar. Thirteen files, roughly 1,750 LOC, structured into one tiny interface (`ISpeechSynthesizer`, 13 lines), one shared base with caching and download-deduplication (`SpeechSynthesizerBase`, 154 lines), and **eleven concrete provider implementations** ranging from 111 to 192 lines each. The domain's job is short: *given text and parameters, return an `AudioClip` as fast as possible, and never download the same clip twice.* What is remarkable about this domain is not its complexity but its restraint — the base class is small, the providers are formulaic, and the latency-killing optimisations live in *the right two places only*.

This is the domain where CDK most outclasses both SAP and Waifu. SAP has `py/moss_tts.py` (one provider, no caching layer documented). Waifu pushes TTS to the cloud and accepts whatever latency the broker returns ([[waifu:22_VOICE_PIPELINE]]). CDK has *eleven providers under one contract*, **a cache and a dedupe-lock at the right layer**, and a **deep Japanese voice ecosystem** the other two corpora never even named.

---

## 1. The Subject Itself

**What the domain is:** the synthesis side of the voice pipeline. Text comes in (from the LLM stream after tag-stripping and sentence-splitting). Audio comes out (as a Unity `AudioClip` ready for `AudioSource.PlayOneShot`). Eleven different vendors can be the body of that pipeline; the contract is the same regardless.

**What it owns:**

| Layer | Files | LOC | Owns |
|---|---|---|---|
| **Interface** | `ISpeechSynthesizer.cs` | 13 | The two-method contract — `IsEnabled` flag + `GetAudioClipAsync(text, parameters, token)` |
| **Base** | `SpeechSynthesizerBase.cs` | 154 | The cache (`Dictionary<string, AudioClip>`), the download-task dedupe (`Dictionary<string, UniTask<AudioClip>>`), the cache-key hash, the preprocess hook, the timeout-watchdog for in-flight downloads |
| **Western providers** | `Google`/`Azure`/`OpenAI` | 116/128/111 | Per-provider request shape, auth, audio format negotiation |
| **Japanese providers** | `Voicevox`/`AivisCloud`/`StyleBertVits2`/`Voiceroid`/`NijiVoice`/`Kotodama` | 190/143/150/172/192/125 | Two-call query→synthesis flow (VOICEVOX-style), per-character style mapping, server URL configuration |
| **Gateway providers** | `SpeechGateway`/`AIAvatarKit` | 138/132 | Server-side broker patterns; the gateway is a single endpoint that fans out to many backends |

**What it does NOT own:**
- Audio *playback* — that's `Model/SpeechController.cs:38-169` ([[10_DOMAIN_MAP]] §2 embodiment layer).
- The decision *which sentence* to synthesize — that's `LLMContentProcessor` ([[16_LLM_SERVICE_DOMAIN]]).
- Lip-sync visuals — that's `uLipSyncHelper`/`VRMuLipSyncHelper` reading the PCM samples *after* playback starts ([[1B_ANIMATION_DOMAIN]]).
- Prefetch queue management — owned by `SpeechController` and `ModelRequestBroker` (`Scripts/Model/ModelRequestBroker.cs:104-115`), which call `GetAudioClipAsync` ahead of time and rely on this domain's *cache* to serve playback hits.

The boundary is precise: the domain answers one question — *here is text, give me audio* — and refuses to know about anything downstream.

---

## 2. How It Works

### 2.1 The two-method interface

`ISpeechSynthesizer` (`Scripts/SpeechSynthesizer/ISpeechSynthesizer.cs:8-12`) is thirteen lines and two members:

```csharp
public interface ISpeechSynthesizer
{
    bool IsEnabled { get; set; }
    UniTask<AudioClip> GetAudioClipAsync(string text, Dictionary<string, object> parameters, CancellationToken token = default);
}
```

That is the entire surface. Eleven providers conform; AIAvatar's `SelectSpeechSynthesizer` (mirroring `SelectLLMService`) picks the first with `IsEnabled = true`. Add a twelfth provider tomorrow — implement these two methods and you are done. The Japanese voice stack is *not* hardwired; it is one branch of a contract.

The `parameters` dictionary is deliberately untyped (`Dictionary<string, object>`) — providers extract what they recognise (`"style"`, `"language"`, vendor-specific keys). This is the same loose-coupling discipline used in `ILLMService.MakePromptAsync`'s `payloads` ([[16_LLM_SERVICE_DOMAIN]] §2.1) and it is exactly the right shape for an open extension point: typed enough to be discoverable, loose enough to add VOICEVOX's `speaker` integer or NijiVoice's `voice_id` GUID without changing the interface.

### 2.2 The cache + dedupe-lock pattern (the masterclass)

`SpeechSynthesizerBase.GetAudioClipAsync` (`Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:28-102`) is the single most adoptable piece of code in this codex. It implements **a three-level lookup**:

```csharp
// /tmp/ChatdollKit/Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:28-62
public async UniTask<AudioClip> GetAudioClipAsync(string text, Dictionary<string, object> parameters, CancellationToken cancellationToken)
{
    if (string.IsNullOrEmpty(text.Trim())) return null;

    var cacheKey = GetCacheKey(text, parameters);

    // Level 1: cache hit — return immediately
    if (HasCache(cacheKey)) {
        return audioCache[cacheKey];
    }

    // Level 2: in-flight download — wait, return cache when it arrives
    if (audioDownloadTasks.ContainsKey(cacheKey)) {
        await WaitDownloadingTask(cacheKey, Timeout, cancellationToken);
        if (audioCache.ContainsKey(cacheKey)) return audioCache[cacheKey];
        ...
    }

    // Level 3: start new download, register the task by cache key
    audioDownloadTasks[cacheKey] = DownloadAudioClipAsync(preprocessedText, parameters, cancellationToken);
    ...
}
```

The cache key (`Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:23-26`) hashes `text + JsonConvert.SerializeObject(parameters)` — so `"Hello"` with `{style: "Joy"}` and `"Hello"` with `{style: "Sad"}` are distinct entries; same text + same parameters return the same clip.

The **dedupe-lock** is the trick. When the LLM streams sentence-by-sentence and the prefetch path (`ModelRequestBroker.ToAnimatedVoiceRequests`, `Scripts/Model/ModelRequestBroker.cs:104-115`) fires synthesis for sentence N *while* the playback path needs sentence N, *both* calls reach `GetAudioClipAsync(text="...", parameters={...})` with the same key. Level 1 sees no cache (download still pending). Level 2 sees the in-flight download task in `audioDownloadTasks[cacheKey]`. The second caller *awaits the existing task* and reads from cache when it completes. **One HTTP request is made; both callers get the bytes.** This is the single-flight pattern done correctly in fewer than thirty lines.

Compare to a naïve implementation: prefetch fires the request, playback fires the request (no cache yet because nothing has returned), the vendor charges twice and the latency-of-first-byte is no better than no-prefetch. CDK's dedupe-lock is the difference between "prefetch saves cost" and "prefetch saves cost *and* avoids redundant network calls." Ember should adopt this verbatim.

The `WaitDownloadingTask` watcher (lines 121-152) has a configurable timeout (default 10s, `Timeout` field at line 13) — if the in-flight task hangs, the second caller breaks out and returns null rather than waiting forever. Good defensive citizenship.

### 2.3 The download-method override

Concrete providers override `DownloadAudioClipAsync` (`SpeechSynthesizerBase.cs:105-108`):

```csharp
protected virtual async UniTask<AudioClip> DownloadAudioClipAsync(string text, Dictionary<string, object> parameters, CancellationToken cancellationToken)
{
    throw new NotImplementedException("DownloadAudioClipAsync must be implemented");
}
```

That is the per-provider surface. The base class handles caching, dedupe, preprocessing, timeout watch, debug logging, and exception cleanup (the `finally` at line 96-99 removes the task entry even when download throws — preventing the dedupe-lock from becoming a permanent dead entry).

Each provider's `DownloadAudioClipAsync` is roughly thirty to seventy lines of HTTP wiring. They share idioms — `client.PostJsonAsync` / `client.PostFormAsync` / a `using var www = UnityWebRequestMultimedia.GetAudioClip` block, conditional `#if UNITY_WEBGL` paths that route through `AudioConverter.PCMToAudioClip` because WebGL cannot use `UnityWebRequestMultimedia`. The shape is so uniform that a new provider is a copy-paste-edit of the closest existing one.

### 2.4 The Japanese voice stack — eight providers Western codexes never named

This is where CDK's Japanese-first origin earns its keep. Eight of the eleven providers are Japanese-ecosystem-first:

| Provider | LOC | Pattern | Where it shines |
|---|---|---|---|
| **VOICEVOX** | 190 | Local OSS server; two-call `audio_query` → `synthesis`; per-speaker integer ID | Free, offline, 30+ character voices, GPU-accelerated; the de facto Japanese hobbyist standard |
| **AivisCloud** | 143 | Cloud API; single-call SSE-streaming synthesis | Latency-optimised cloud TTS with Japanese character pack |
| **StyleBertVits2** | 150 | Local OSS server; query+infer; emotion-vector parameter | Fine-tunable on small voice datasets — *the* hobbyist voice-cloning route |
| **Voiceroid** | 172 | Local Windows-binary controller (AI Talk Editor API on `127.0.0.1`); proprietary | Commercial Japanese voice packs (Tohoku Zunko, etc.) |
| **NijiVoice** | 192 | Cloud API; per-`voice_id` GUID; emotion/speed parameters | Pay-as-you-go cloud with anime-character voice catalogue |
| **Kotodama** | 125 | Cloud API broker | Newer mid-tier cloud option |
| **SpeechGateway** | 138 | Server-side fan-out broker; takes provider name + parameters | The `--multi-provider` gateway; one endpoint, many backends |
| **AIAvatarKit** | 132 | Sister-project broker; server-side TTS pipeline | Tethered to the AIAvatarKit speech-to-speech stack |

The VOICEVOX flow is illustrative. `VoicevoxSpeechSynthesizer.DownloadAudioClipAsync` (`Scripts/SpeechSynthesizer/VoicevoxSpeechSynthesizer.cs:55-105`):

```csharp
// Step 1: query — get a JSON describing prosody, timing, and pitch
var queryResp = await client.PostFormAsync(
    EndpointUrl + $"/audio_query?speaker={(decimal)inlineSpeaker}&text={UnityWebRequest.EscapeURL(text, Encoding.UTF8)}",
    new Dictionary<string, string>(), cancellationToken: token);
var audioQuery = queryResp.Text;

// Step 2: synthesis — POST the query JSON, get back WAV bytes
var url = EndpointUrl + $"/synthesis?speaker={(decimal)inlineSpeaker}";
var headers = new Dictionary<string, string>() { { "Content-Type", "application/json" } };
var data = Encoding.UTF8.GetBytes(audioQuery);
return await DownloadAudioClipNativeAsync(url, data, headers, token);
```

Two HTTP calls per utterance. The query gives the user a *chance to modify the prosody* between calls (CDK doesn't take this chance; the query JSON is returned and immediately posted). But the seam is there — Ember could *modify the audio_query* mid-pipeline to inject style adjustments before synthesis. That is the kind of leverage a uniform-contract abstraction does not give you for free; the Japanese stack offers it because the protocol is inherently two-phase.

The **VoiceStyle mapping** pattern (`VoicevoxSpeechSynthesizer.cs:64-78`):

```csharp
if (parameters.ContainsKey("style")) {
    var voiceStyle = parameters["style"] as string;
    foreach (var style in VoiceStyles) {
        if (style.VoiceStyleValue == voiceStyle) {
            inlineSpeaker = style.VoiceVoxSpeaker;
            break;
        }
    }
}
```

The LLM-side emits `[face:Joy]` and the tag parser puts `"style": "Joy"` into the parameters dict. This provider maps `"Joy"` → VOICEVOX speaker integer 14 (or whatever the user configured). **The same `style` parameter routes through the Western providers differently** — Azure reads it as an SSML prosody hint, OpenAI ignores it. The interface absorbs this; concrete providers translate. This is exactly the *adapter pattern's* legitimate use.

The deeper Japanese-stack analysis is in [[22_TTS_INTERFACE_JAPANESE]] (Auditor); the cross-stack synthesis is in [[66_JAPANESE_VOICE_INTEGRATION]] (Scribe).

### 2.5 The prefetch coupling with SpeechController and ModelRequestBroker

CDK has **two distinct prefetch patterns**, and the distinction matters.

**Pattern 1 — `ModelRequestBroker` synchronous prefetch.** When the user emits an external request via `SetRequest(text)` (`Scripts/Model/ModelRequestBroker.cs:66-80`), the broker splits text into sentences, generates `AnimatedVoiceRequest`s, and **immediately fires synthesis** for every voice via `speechController.PrefetchVoices` (lines 111-115). All sentences hit the cache *before* playback starts. This is the **sequential prefetch** mode — best when the request is complete and known up-front (e.g., a SocketServer broadcast message).

**Pattern 2 — `LLMContentProcessor` parallel prefetch.** When the LLM is *streaming*, sentences arrive one at a time. `LLMContentProcessor.ProcessContentStreamAsync` (`Scripts/LLM/LLMContentProcessor.cs:29-161`) detects sentence boundaries and calls `ProcessContentItemAsync` (line 134-137) per sentence — which AIAvatar wires (in its `Awake` setup) to call `SpeechController.PrefetchVoices`. *Sentence N is being synthesized while sentence N-1 is playing.* The dedupe-lock means that when playback for sentence N reaches `SpeechController.Say`, the synthesis is either already cached (cheap hit) or in-flight (Level 2 wait). This is **parallel prefetch** — the latency-killer for streaming LLMs.

Both patterns are correct. CDK *uses both* in different code paths. The discipline of having one cache + one dedupe-lock under both is what makes this work without a coordination layer.

### 2.6 The text preprocessor hook

`SpeechSynthesizerBase.PreprocessText` (line 21) is a public `Func<string, Dictionary<string, object>, CancellationToken, UniTask<string>>`. If set, every download runs the text through it first (line 70-72). Use cases:

- **Alphabet → kana conversion** for Japanese TTS that mispronounces English (the comment at line 69 calls this out explicitly).
- **Number → spoken form** ("100" → "one hundred").
- **SSML injection** based on parameters.
- **Slang/profanity filtering**.

This is application-supplied policy on a library-supplied mechanism. The same shape as `SpeechListenerBase.BargeInCondition` ([[14_SPEECH_LISTENER_DOMAIN]] §2.6). Adopt the pattern in Ember as `pre_synthesis_filter: Optional[Callable]`.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The cache has no eviction

`audioCache: Dictionary<string, AudioClip>` (line 15) grows monotonically. A long-running session in conversation mode produces hundreds of clips, each consuming memory. CDK provides `ClearCache()` (line 116-119) — but nothing calls it automatically. For a phone-deployed avatar this is a slow-burn memory leak. Ember should add an LRU bound or session-end clear.

### 3.2 The cache survives provider switches

If the user toggles `IsEnabled` between two providers mid-session, the *cache key collision* problem appears: the same `(text, parameters)` hash on Provider A is *not* an acceptable substitute for the same hash on Provider B. The cache lives on `SpeechSynthesizerBase`, which is per-component — so switching components clears the cache *as a side effect* of the component change. Tolerable, but fragile.

### 3.3 The cache-key is `GetHashCode()` of a string

`GetCacheKey` (line 23-26) returns `$"{text}_{JsonConvert.SerializeObject(parameters)}".GetHashCode().ToString()`. `.GetHashCode()` is *not guaranteed* to be stable across .NET runtime versions, and **is not collision-resistant** in a domain with many distinct strings. For typical conversation lengths, collisions are rare but possible. The cost of collision: the wrong clip plays. For Ember, use a proper hash (SHA-256 truncated, or just keep the full string as the key).

### 3.4 The `[unverified — README claim only]` provider count

The README lists eleven TTS providers. The repository has thirteen `*SpeechSynthesizer.cs` files (`AIAvatarKit`, `AivisCloud`, `Azure`, `Google`, `Kotodama`, `NijiVoice`, `OpenAI`, `SpeechGateway`, `StyleBertVits2`, `Voiceroid`, `Voicevox` — eleven concrete + `SpeechSynthesizerBase` + `ISpeechSynthesizer`). So the count matches. The README also mentions "Aivis Cloud API" separately from "AivisSpeech" — the latter is reachable via the `SpeechGateway` provider per uezo's docs but does not have its own class. The interface absorbs this; the count is honest.

### 3.5 The download-method ambiguity around null returns

Most providers return `null` on error or empty input. The base class accepts null and returns null. Downstream (`SpeechController.Say`) checks for null and skips. *But the cache is still updated* (lines 80-83): "Cache once regardless of UseCache" — actually, looking carefully, the cache is only updated if `clip != null && clip.length > 0` (line 80). So nulls are not cached. Good. But this could be made explicit; the path is reachable only by reading the condition carefully.

### 3.6 No streaming TTS

Every provider returns a single `AudioClip` for the full sentence. None of them stream audio chunks for sub-sentence playback start. The latency floor is "time to first byte of the *complete* utterance." For long sentences (>5 seconds of speech), this matters — the user sees the avatar's mouth idle for a noticeable beat before the sentence starts.

**The sentence-splitting in `LLMContentProcessor` is CDK's workaround**: split aggressively (`、`, `, `, after `MaxLengthBeforeOptionalSplit` chars) so no clip is too long. But this is a workaround, not a solution. A truly streaming TTS — AivisCloud SSE is the closest CDK has — would let playback start before synthesis finishes. CDK does not exploit this even where the protocol supports it; the `AudioClip` abstraction is the bottleneck. Ember should consider chunk-streaming TTS as a Rödd-streaming sub-tier.

### 3.7 The hidden timeout-watchdog race

`WaitDownloadingTask` (line 121-152) polls every 50ms via `UniTask.Delay(50, ...)`. If the download completes in <50ms, the wait loop still does one iteration of delay. Fine — that's 50ms of avoidable latency in the dedupe-hit-fast case. For very-fast local TTS (VOICEVOX on a fast machine, ~80ms total) this is 60% overhead. The fix: signal the wait via `TaskCompletionSource` rather than polling.

### 3.8 The crisp parts

- **Three-level lookup with dedupe-lock** (`SpeechSynthesizerBase.cs:28-99`). The reference implementation of single-flight caching.
- **The interface is two methods.** Eleven providers, two methods. A new provider is forty minutes of work.
- **The preprocess hook**. The right extension point at the right layer.
- **`#if UNITY_WEBGL` separation** done provider-by-provider, not at the interface. WebGL paths go through `AudioConverter.PCMToAudioClip` because `UnityWebRequestMultimedia.GetAudioClip` is broken on WebGL — CDK names this honestly per provider.
- **The two-phase Japanese protocol mapping** (VOICEVOX query→synthesis as two HTTP calls within one base method). The seam exists for users who need it.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 5 — SpeechSynthesizer in the macro shape
- [[12_MODEL_CONTROLLER_DOMAIN]] — `SpeechController` consumes this domain's output
- [[1B_ANIMATION_DOMAIN]] — `[face:Joy]` tag becomes the `style` parameter that VoiceStyle maps
- [[14_SPEECH_LISTENER_DOMAIN]] — symmetric STT side of the voice pipeline
- [[21_TTS_INTERFACE_WESTERN]] — Auditor's catalogue of Google/Azure/OpenAI
- [[22_TTS_INTERFACE_JAPANESE]] — Auditor's catalogue of VOICEVOX/AivisCloud/StyleBertVits2/Voiceroid/NijiVoice/Kotodama
- [[66_JAPANESE_VOICE_INTEGRATION]] — Scribe's synthesis: what Ember gains by adopting VOICEVOX
- [[sap:17_VOICE_OUTPUT_DOMAIN]] — SAP's `moss_tts.py` (single-provider) for contrast
- [[waifu:22_VOICE_PIPELINE]] — Waifu's cloud-TTS-via-broker for contrast

---

## What This Means for Ember

**Adopt:**
- The **three-level lookup pattern** (`Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:28-102`): cache → in-flight wait → new download. Apache-2.0 attribution required. This is the single most directly portable algorithm in CDK; lift verbatim into Ember's `Rödd` subsystem as `async def get_audio_clip(text, params, token) -> Optional[AudioClip]` with `_cache: dict[str, AudioClip]` + `_in_flight: dict[str, asyncio.Future[AudioClip]]`. Adopt with attribution.
- The **two-method `ISpeechSynthesizer` interface** (`Scripts/SpeechSynthesizer/ISpeechSynthesizer.cs:8-12`). Ember's `TTSProvider` Protocol: `is_enabled: bool` + `async def get_audio(text, params, token) -> Optional[AudioClip]`. Eleven CDK providers fit; Ember's providers fit the same shape.
- The **`PreprocessText` hook** (line 21). Ember's `pre_synthesis_filter: Callable[[str, dict, CancellationToken], Awaitable[str]]`. Pluggable per-provider; defaults to identity.
- The **VOICEVOX provider** as Ember's first Japanese-voice integration. Apache-2.0 attribution required. The two-call query→synthesis pattern (`VoicevoxSpeechSynthesizer.cs:80-104`) is shippable Python in a day. Ember inherits the Japanese hobbyist voice-pack catalogue for free.
- The **VoiceStyle mapping** (`VoicevoxSpeechSynthesizer.cs:64-78`) as Ember's `style_map: dict[str, ProviderStyle]` per-provider config. The `[face:Joy]` tag flows into the `style` parameter; each provider has its own translation table.

*Apache-2.0 attribution: when patterns from `ChatdollKit/Scripts/SpeechSynthesizer/` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:**
- The **`GetHashCode()` cache key.** Adapt to a SHA-256 truncated hash for collision resistance. Cost: 10µs per key; benefit: no cross-version drift, no rare-but-real collision bugs.
- The **monotonically-growing cache**. Adapt to an LRU with configurable capacity (default 200 clips ≈ 100MB at typical bitrate). Eviction emits a Sögumiðla `TTSCacheEvicted` event for observability.
- The **50ms polling-wait** for in-flight downloads. Adapt to an `asyncio.Event` or `asyncio.Future` signalled when the download completes — eliminates the worst-case 50ms latency hit on dedupe-hits.
- The **per-provider `IsEnabled` flag**. Adapt as Ember's `tts_provider: str` (config name) — only the named provider is instantiated. Reduces resident footprint (CDK runs eleven `MonoBehaviour`s even when one is active).
- The **two-phase VOICEVOX query mid-pipeline**. Adapt by exposing a `query_modifier: Optional[Callable[[AudioQuery], AudioQuery]]` hook between query and synthesis. The seam CDK leaves implicit, Ember makes explicit and reviewable.

**Avoid:**
- The **unbounded cache.** A 24-hour conversation can OOM a Pi-tier device.
- The **eleven-co-resident-providers** pattern in Python. CDK gets it free because Unity's component model is already paying for the resident cost; Python's import + class-instance overhead is meaningful at small scale.
- **String-comparison voice-style lookup** (`VoicevoxSpeechSynthesizer.cs:69-77` loops a List). Use a dict.
- **Provider-specific error handling that returns null silently** (most providers `Debug.LogError` and return null). Ember's providers raise typed exceptions; the orchestration layer decides whether to fall back to a backup provider, return a "voice failed" placeholder, or fail the turn.

**Invent:**
- **The Multi-Provider TTS Failover Vow.** Ember's `Rödd` accepts a *list* of providers in priority order. If primary fails (timeout, error), automatically retry on secondary. CDK has *enabled-flag pick one*; Ember has *prioritised list with automatic fallback*. Failover events emit on Sögumiðla. The cost is bookkeeping; the benefit is graceful degradation when (say) NijiVoice cloud is rate-limited and VOICEVOX local picks up the load.
- **Cache-Sharing Across Sessions.** CDK's cache is per-component-lifetime. Ember's cache persists to disk (one Parquet file per provider per voice-style) with content-addressed filenames (the SHA-256 hash *is* the filename). Restart-resistant. The Brunnr Well already holds chunks; adding an audio sidecar is one Parquet table.
- **The Streaming-TTS Sub-Provider Tier.** For providers that support streaming (AivisCloud SSE, potentially OpenAI's `tts-1-hd` streaming endpoint), Ember exposes a *separate* `AsyncIterator[AudioChunk]` method `get_audio_stream(...)` alongside `get_audio(...)`. The `Rödd-streaming` sub-name proposed in `[[waifu:10_DOMAIN_MAP]]` finds its concrete shape here.
- **The Japanese-First Tier-Selection Config.** Ember's TTS config has a top-level `language_preference: ja|en|auto` that routes the default provider: `ja` → VOICEVOX, `en` → OpenAI, `auto` → detect per-utterance via `[lang:]` tag and route accordingly. The Japanese stack is a first-class option, not a localisation afterthought.
- **The Prefetch Plan as a First-Class Object.** CDK's prefetch is implicit (synchronous in `ModelRequestBroker`, parallel in `LLMContentProcessor`). Ember's `PrefetchPlan` is a typed object: a list of `(text, params, deadline)` tuples that the synthesizer commits to having ready by `deadline`. Failure to meet deadline is a Sögumiðla event. Makes the latency budget *visible* and *auditable* — Volmarr can see, after the fact, which sentence's TTS missed its slot.
- **The Voice-Identity-as-Asset Vow.** Each voice (provider + style + speaker + parameters) gets a *True Name* in Ember's voice manifest: `Rödd::voicevox-zundamon-joyful` is a registered, named, version-locked identity. The `[face:Joy]` tag does not just route to a style integer; it routes to a *named voice identity* that the system has documented memory of. Audit trails reference voices by name, not by ephemeral parameter blobs.

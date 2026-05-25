---
codex_id: 33_TTS_PREFETCH
title: TTS Prefetch — Two Queues, One Cache, and a Hash Key
role: Forge-A
layer: Execution
status: draft
kit_source_refs:
  - Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:1-154
  - Scripts/SpeechSynthesizer/VoicevoxSpeechSynthesizer.cs:1-191
  - Scripts/Model/SpeechController.cs:1-213
  - Scripts/Model/ModelRequestBroker.cs:1-193
  - Scripts/LLM/LLMContentProcessor.cs:1-271 (stream-driven prefetch trigger)
  - Scripts/AIAvatar.cs:264-282 (LLMContentProcessor.ProcessContentItemAsync wiring)
ember_subsystem_targets: [Funi, Strengr, Hjarta]
cross_refs:
  - 31_AIAVATAR_MAIN_LOOP
  - 37_BARGE_IN_INTERRUPT
  - 15_SPEECH_SYNTHESIZER_DOMAIN
  - 22_TTS_INTERFACE_JAPANESE
  - sap:32_AVATAR_RENDER_PIPELINE
  - waifu:30_BASIC_MODE_FLOW
license_posture: Apache-2.0 — adopt with attribution
---

# TTS Prefetch

> *Hash the text. Cache the audio. Download in parallel. Play in order. Cancel everything if the user talks.*

Forge-A. Eldra. The TTS layer is the secret weapon of ChatdollKit. The kit talks fast and feels responsive *not* because of any one TTS provider but because of how `SpeechSynthesizerBase`, `SpeechController`, and the LLM stream parser cooperate to start downloading audio before the LLM is even done generating the sentence. Two queues, one hash-keyed cache, sequential playback. Here is exactly how each piece earns its keep.

## The Two Queues

CDK has, in essence, **two FIFO queues** in series for TTS:

1. **`voicePrefetchQueue`** — a `ConcurrentQueue<Voice>` in `SpeechController` (`/tmp/ChatdollKit/Scripts/Model/SpeechController.cs:16`). Background task pulls from it and *downloads* audio. Doesn't play it.
2. **`modelRequestQueue`** — a `Queue<AnimatedVoiceRequest>` in `ModelRequestBroker` (`/tmp/ChatdollKit/Scripts/Model/ModelRequestBroker.cs:21`). Foreground task pulls from it and *speaks* the queued request.

Backing both is a single cache: `SpeechSynthesizerBase.audioCache` (`SpeechSynthesizerBase.cs:15`), a `Dictionary<string, AudioClip>` keyed by `GetCacheKey(text, parameters)`. Cache lookups happen on both download and playback; the cache is the rendezvous.

The hash key (`SpeechSynthesizerBase.cs:23-26`):

```csharp
// /tmp/ChatdollKit/Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:23-26
protected virtual string GetCacheKey(string text, Dictionary<string, object> parameters)
{
    return $"{text}_{JsonConvert.SerializeObject(parameters)}".GetHashCode().ToString();
}
```

C#'s default `string.GetHashCode()`. 32-bit, not collision-resistant — but for a per-session cache of ~100 phrases that is fine. The key includes the TTS parameters (speaker ID, style, language) so different voicings of the same text don't collide.

## The Prefetch Trigger

The reason this works is *when* prefetch fires. Trace it from the streaming LLM downward.

In `AIAvatar.Awake`, the bootstrap wires up `LLMContentProcessor.ProcessContentItemAsync` (`AIAvatar.cs:265-282`):

```csharp
// /tmp/ChatdollKit/Scripts/AIAvatar.cs:265-282 (compressed)
LLMContentProcessor.ProcessContentItemAsync = async (contentItem, token) =>
{
    if (contentItem.Data is AnimatedVoiceRequest avreq)
    {
        // Prefetch the voice from TTS service
        foreach (var av in avreq.AnimatedVoices)
        {
            foreach (var v in av.Voices)
            {
                if (v.Text.Trim() == string.Empty) continue;

                ModelController.SpeechController.PrefetchVoices(new List<Voice>(){new Voice(
                    v.Text, 0.0f, 0.0f, v.TTSConfig, true, string.Empty
                )}, token);
            }
        }
    }
};
```

Now read `LLMContentProcessor.ProcessContentStreamAsync` (`LLMContentProcessor.cs:29-161`). This task is started concurrently with the LLM streaming task and consumes the streaming buffer character-by-character. Every time it hits a sentence-end punctuation (`。`, `！`, `？`, `. `, `!`, `?` per `:14`), it splits off a chunk, calls `HandleSplittedText` (which builds the `AnimatedVoiceRequest` via the tag parser, see [[34_ANIMATION_PIPELINE]]), then calls `ProcessContentItemAsync` — which is our prefetch trigger.

So: **every time the LLM emits a complete sentence, that sentence's audio download begins.** The LLM is still generating sentence 2 while we're already downloading sentence 1. The user sees response start in the time it takes for sentence 1's audio to download (300-800ms typical) regardless of whether the LLM has finished sentence 3.

That is the entire prefetch architecture in one sentence. It is the cleverest piece of orchestration in the whole kit.

## The Background Prefetch Task

`SpeechController.StartVoicePrefetchTask` (`SpeechController.cs:180-204`) is a `UniTaskVoid` that runs from `Start` and lives for the lifetime of the GameObject:

```csharp
// /tmp/ChatdollKit/Scripts/Model/SpeechController.cs:180-204 (compressed)
private async UniTaskVoid StartVoicePrefetchTask()
{
    voicePrefetchCancellationTokenSource = new CancellationTokenSource();
    var token = voicePrefetchCancellationTokenSource.Token;

    try
    {
        while (!token.IsCancellationRequested)
        {
            if (voicePrefetchQueue.TryDequeue(out var voice))
            {
                var parameters = voice.TTSConfig != null ? voice.TTSConfig.Params : new Dictionary<string, object>();
                await SpeechSynthesizerFunc(voice.Text, parameters, token);
            }
            else
            {
                await UniTask.Delay(10, cancellationToken: token);
            }
        }
    }
    catch (OperationCanceledException) { /* Ignore */ }
}
```

Dequeue. Call `SpeechSynthesizerFunc(text, params, token)`. Loop. The result is *discarded* — but the side effect is that `SpeechSynthesizerBase.GetAudioClipAsync` (`SpeechSynthesizerBase.cs:28-102`) populates the cache. So the next time the *foreground* task asks for the same text+params, it hits cache and gets the AudioClip instantly.

This is what makes the prefetch sequential, not parallel. One download at a time in the order they were enqueued. The trade-off: if your TTS provider supports concurrent downloads, you're leaving throughput on the table. The Win: cache hits are deterministic and the provider doesn't get hammered with parallel requests that may rate-limit.

Some providers (NijiVoice, AivisCloud) override `IsEnabled` to be falsy on WebGL or otherwise serialize differently — but the base loop is one-at-a-time.

## The Foreground Playback Task

`SpeechController.Say` (`SpeechController.cs:38-169`) is what AIAvatar invokes (via `ModelController.AnimatedSay` → `Say`) to actually play a list of voices in order:

```csharp
// /tmp/ChatdollKit/Scripts/Model/SpeechController.cs:38-62 (compressed)
public async UniTask Say(List<Voice> voices, CancellationToken token)
{
    // Stop speech
    StopSpeech();
    PrefetchVoices(voices, token);  // ← also queues for prefetch

    // Speak sequentially
    foreach (var v in voices)
    {
        if (token.IsCancellationRequested) return;

        OnSayStart?.Invoke(v, token);

        try
        {
            var downloadStartTime = Time.time;
            AudioClip clip = null;

            var parameters = v.TTSConfig != null ? v.TTSConfig.Params : new Dictionary<string, object>();
            clip = await SpeechSynthesizerFunc(v.Text, parameters, token);
            // ... PreGap wait, playback, lip-sync, PostGap wait
        }
        finally { OnSayEnd?.Invoke(); }
    }
}
```

Critical detail: `Say` re-calls `SpeechSynthesizerFunc(text, parameters, token)` per voice. If the prefetch background task has already cached the clip, `GetAudioClipAsync` returns immediately (`SpeechSynthesizerBase.cs:39-47`):

```csharp
// /tmp/ChatdollKit/Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:39-47
if (HasCache(cacheKey))
{
    var cachedClip = audioCache[cacheKey];
    if (isDebug) Debug.Log($"Return cached audio clip: {cacheKey}");
    return cachedClip;
}
```

If the prefetch task is still downloading (the request is in `audioDownloadTasks`), the foreground task waits on that in-flight task instead of starting a duplicate (`SpeechSynthesizerBase.cs:49-62`):

```csharp
// /tmp/ChatdollKit/Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:49-62 (compressed)
if (audioDownloadTasks.ContainsKey(cacheKey))
{
    await WaitDownloadingTask(cacheKey, Timeout, cancellationToken);
    if (audioCache.ContainsKey(cacheKey)) return audioCache[cacheKey];
    else { /* warning, return null */ }
}
```

This is the deduplication contract: the foreground task and the prefetch task can't double-download the same clip even if they hit `GetAudioClipAsync` simultaneously. The `audioDownloadTasks` dictionary is the rendezvous lock.

## The Playback Inner Loop

While a clip is playing, the playback path optionally drives lip-sync (`SpeechController.cs:83-126`):

```csharp
// /tmp/ChatdollKit/Scripts/Model/SpeechController.cs:97-115 (compressed)
AudioSource.PlayOneShot(clip);

while (Time.realtimeSinceStartup - startTime < clip.length && !token.IsCancellationRequested)
{
    var elapsedTime = Time.realtimeSinceStartup - startTime;
    var currentPosition = Mathf.FloorToInt(elapsedTime * clip.frequency) * clip.channels;

    while (nextPosition + bufferSize <= currentPosition &&
        nextPosition + bufferSize <= samples.Length)
    {
        System.Array.Copy(samples, nextPosition, sampleBuffer, 0, bufferSize);
        HandlePlayingSamples(sampleBuffer);
        nextPosition += bufferSize;
    }

    await UniTask.Delay(33, cancellationToken: token);  // 30FPS
}
```

Every 33ms (~30Hz) it estimates the playback position by wall-clock time × clip frequency, then pushes the corresponding sample window to `HandlePlayingSamples`. The lip-sync layer ([[35_LIP_SYNC]]) consumes those samples to drive viseme blendshapes. The buffer size is `2048` for stereo, `1024` for mono — explicitly tuned for 44100Hz ÷ 30FPS ≈ 1470, rounded to the next power-of-2.

Note that this is **wall-clock-based, not AudioSource-position-based.** If the audio output is delayed by the OS (Bluetooth audio buffer, etc.), the lip-sync runs to the wrong time. The trade is simplicity for accuracy — `AudioSource.timeSamples` would give true position but requires syncing on the audio thread.

## ModelRequestBroker — The Parallel Pipeline

`ModelRequestBroker` (`/tmp/ChatdollKit/Scripts/Model/ModelRequestBroker.cs`, 193 lines) is an *alternative* dispatcher used by the SocketServer and AITuber sister project. It queues `AnimatedVoiceRequest` objects (the post-tag-parsing output) and processes them serially via its own background `StartListening` task (`:43-64`):

```csharp
// /tmp/ChatdollKit/Scripts/Model/ModelRequestBroker.cs:43-64 (compressed)
public async UniTask StartListening()
{
    while (!isCancelled)
    {
        if (modelRequestQueue.Count > 0)
        {
            var avreq = modelRequestQueue.Dequeue();
            try
            {
                await modelController.AnimatedSay(avreq, modelTokenSource.Token);
            }
            catch (Exception ex) { Debug.LogError(...); }
        }
        else await UniTask.Delay(10);
    }
}
```

`SetRequest(text)` (`:66-80`) parses the text via `ToAnimatedVoiceRequests`, enqueues each split sentence as a separate request, and concurrently *also* triggers prefetch on each voice. The result: external systems (a Twitter listener, a YouTube chat handler) can spray text at `ModelRequestBroker.SetRequest` and the avatar speaks them in order with full TTS prefetch.

`SetRequest` calls `modelTokenSource?.Cancel()` first (`:69`) — every new SetRequest cancels the previous one. This is the **cancel-and-replace** pattern that makes barge-in fast (see [[37_BARGE_IN_INTERRUPT]]).

## Parallel vs Sequential — The Toggle That Isn't

The MANIFEST scope hints at "parallel vs sequential prefetch" being a tunable. Reading the code, this is a *design intent* not a *runtime toggle*. The sequential default lives in `StartVoicePrefetchTask`. To get parallel:

- Replace `ConcurrentQueue<Voice>` + single consumer with a thread pool over `Voice` requests.
- Add concurrent download semaphore per-provider.
- Re-handle the deduplication lock in `audioDownloadTasks`.

CDK does none of this. Its bet is that one-at-a-time matches most providers' rate limits and that the second downloaded sentence finishes before its playback turn even if parallel would have been 2x faster. For a Pi-tier deployment this bet is correct. For a cloud-tier deployment where TTS round-trip is 800ms, parallel would shave noticeable latency. The toggle is a future feature.

## Where It Breaks

- **`string.GetHashCode()` is not stable across .NET runtimes.** `SpeechSynthesizerBase.cs:25` uses C#'s default hash which is intentionally randomized per-process on some runtimes and pinned on Mono/IL2CPP. CDK relies on the pinned behavior; on a hypothetical .NET 5+ port with hash randomization, the same text would hash differently between runs, busting cross-session cache (if you ever persist the cache). Not a current bug; a future-port landmine.
- **No cache eviction.** `audioCache` grows unboundedly. `ClearCache()` exists (`:116-119`) but nothing calls it automatically. A long-running session that hears 1000 unique sentences will hold 1000 AudioClips. On mobile, this is an OOM in <1hr.
- **Cache-key collisions.** 32-bit hash → 2^32 ≈ 4 billion. For 1000 keys, birthday-paradox collision probability is non-trivial. If two different texts happen to hash-collide, the second one returns the first one's audio. Silent corruption.
- **`audioDownloadTasks.Remove(cacheKey)` in `finally` (`SpeechSynthesizerBase.cs:97-99`).** Always runs after the download attempt finishes (success or fail). If a foreground `WaitDownloadingTask` is waiting on it, the wait exits as soon as the download dictionary entry is removed — and then checks `audioCache.ContainsKey`. There's a one-tick window where the cache might not yet have the clip but the download task is gone. Race; rarely observed but real.
- **`Resample` in the playback path is wall-clock-based.** Audio output latency (Bluetooth, USB-DAC) is not compensated. Lip-sync drift on Bluetooth headsets is a known issue in Unity that CDK does not handle.

## Where It Surprises

- **`v.Text.Trim() == string.Empty` early-out (`AIAvatar.cs:274`).** Prefetch skips empty voices. Sounds obvious; matters because the tag parser can produce voices with text="" if the LLM emits `[anim:Wave]` alone on a line. Without this check the prefetch task would spam the TTS with empty-text requests.
- **Prefetch always uses `useCache = true` regardless of voice's `useCache` flag.** Look at `AIAvatar.cs:276-278` — the `Voice` constructor passes `true` for the cache flag. The actual `Voice` class might have a `useCache=false` option; the prefetch path doesn't honor it. This is intentional (we always want cache hits) but easy to miss.
- **The Voicevox synthesizer (`VoicevoxSpeechSynthesizer.cs`) does a two-stage call:** first POST `/audio_query?speaker=X&text=Y` to get a JSON query object, then POST `/synthesis?speaker=X` with that query body to get the WAV (`:81-105`). Two round-trips. Other Japanese TTS providers (NijiVoice, AivisCloud) do this in one call. Voicevox specifically pays a network penalty for its two-stage protocol — but its style/intonation control is the best of the open-source Japanese TTS stack.
- **`StopSpeech()` only calls `AudioSource.Stop()` (`SpeechController.cs:207-210`).** It does *not* cancel the download task, does *not* clear the prefetch queue. The next `Say` call will start fresh. This is the right factoring — `Say` itself handles the queue clear via `PrefetchVoices` before iterating. But it means a standalone `StopSpeech()` invocation doesn't release in-flight downloads. Memory leak on chatty cancel-loops.

## Cross-References

- [[31_AIAVATAR_MAIN_LOOP]] — the dialog state machine that fires off `ShowContentItemAsync`
- [[37_BARGE_IN_INTERRUPT]] — the cancel-and-replace pattern that builds on this prefetch
- [[15_SPEECH_SYNTHESIZER_DOMAIN]] — Architect's view of TTS as a swappable interface
- [[22_TTS_INTERFACE_JAPANESE]] — Auditor's deep dive on Voicevox/Aivis/NijiVoice
- [[sap:32_AVATAR_RENDER_PIPELINE]] — contrast: SAP renders avatar via VRM windows, TTS via `moss_tts.py`
- [[waifu:30_BASIC_MODE_FLOW]] — contrast: Waifu hides TTS entirely behind the cloud SDK

## What This Means for Ember

**Adopt:**

- **The two-queue + one-cache + hash-key topology** (`SpeechController.cs:16, 180-204` + `SpeechSynthesizerBase.cs:15, 23-26`, Apache-2.0 attribution required). This is the architecture Rödd needs. Sentence-boundary prefetch, sequential foreground playback, cache by `hash(text+params)`. Vendor wholesale into Ember's Rödd-unity tier.
- **The "trigger prefetch when sentence-end is seen in LLM stream" pattern** (`LLMContentProcessor.cs:65-141`). This is the latency reducer. Adopt as Munnr's `on_sentence_complete()` hook firing into Rödd's prefetch queue.
- **The `audioDownloadTasks` deduplication lock** (`SpeechSynthesizerBase.cs:49-62`). Prevents the foreground/background race. Adopt exactly.

**Adapt:**

- **`string.GetHashCode()` → `SHA1.Hash` first 8 bytes hex.** Stable cross-runtime, no collision worry at 100k-key scale. Same ~16-byte key size.
- **Sequential-only prefetch → tiered.** Local TTS (Voicevox running locally) supports parallel. Cloud TTS (OpenAI) often rate-limits. Ember should ship a per-provider `max_parallel_prefetch` config; default 1 for safety, configurable to 4-8 for local.
- **No cache eviction → LRU with size budget.** Default budget: 50MB or 100 clips, whichever first. Munnr exposes `cache.evict_all()` and `cache.stats()`.

**Avoid:**

- **Unbounded `audioCache` growth.** Will OOM long-running sessions. Don't ship without eviction.
- **Wall-clock lip-sync timing.** Use AudioSource sample position. Drift on Bluetooth is real.
- **Pre-warming the cache from disk on boot.** Tempting; would cause Funi to read megabytes of stale audio on every cold-start. Cache should be in-memory only, repopulated lazily.

**Invent:**

- **Hjarta TTS Cache Ledger.** Every cache write produces a `CacheEntry { key, text, params, audio_bytes, created_at, hits }`. Hjarta tracks hit-rate, surface "the avatar has said this 47 times" pattern, identifies hot phrases for explicit pre-caching at startup. CDK has no such introspection.
- **Strengr Sentence Prediction Prefetch.** When the LLM has emitted "I'd love to" with high probability of completing as "help you with that", Strengr can speculatively prefetch the predicted continuation's TTS — wasted bandwidth on misprediction, but a 200-400ms latency win on hit. Requires a small predictor model; viable on local LLMs.
- **Rödd Cross-Session Cache.** Persist `audioCache` to disk between sessions for the system-prompt-driven utterances ("Hi! How can I help?", "Sorry, I didn't catch that"). 90%+ hit rate on those. Persistent layer must be content-addressable (SHA1) and size-bounded.
- **Munnr Audio Playback Tape.** Every voice played produces a `PlaybackEvent { voice_id, started_at, duration_ms, cache_hit, prefetch_latency_ms, provider }`. Useful for latency budget analysis without external profiling tools.

---

*Apache-2.0 attribution: when adopting CDK's TTS prefetch architecture into Ember source, preserve the ChatdollKit header reference per Apache-2.0 §4(c). Each provider's protocol (Voicevox, Azure, OpenAI, etc.) has its own license — verify before vendoring.*

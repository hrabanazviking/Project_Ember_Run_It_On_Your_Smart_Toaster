---
codex_id: 14_SPEECH_LISTENER_DOMAIN
title: Speech Listener Domain — Six STT Providers, One Recording Session, One VAD Slot
role: Architect
layer: Domain
status: draft
chatdoll_source_refs:
  - Scripts/SpeechListener/SpeechListenerBase.cs:1-255
  - Scripts/SpeechListener/MicrophoneManager.cs:1-344
  - Scripts/SpeechListener/RecordingSession.cs:1-153
  - Scripts/SpeechListener/ISpeechListener.cs
  - Scripts/SpeechListener/IMicrophoneManager.cs
  - Scripts/SpeechListener/IMicrophoneProvider.cs
  - Scripts/SpeechListener/GoogleSpeechListener.cs:1-131
  - Scripts/SpeechListener/AzureSpeechListener.cs:1-119
  - Scripts/SpeechListener/AzureStreamSpeechListener.cs:1-201
  - Scripts/SpeechListener/OpenAISpeechListener.cs:1-57
  - Scripts/SpeechListener/AIAvatarKitSpeechListener.cs
  - Scripts/SpeechListener/AIAvatarKitStreamSpeechListener.cs:1-375
  - Scripts/SpeechListener/AndroidMicrophoneProvider.cs:1-19
  - Scripts/SpeechListener/IOSMicrophoneProvider.cs:1-19
  - Scripts/SpeechListener/MacMicrophoneProvider.cs:1-19
  - Extension/SileroVAD/SileroVADProcessor.cs:1-203
ember_subsystem_targets: [Munnr, Funi]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/17_MICROPHONE_MANAGER_DOMAIN
  - 20_interface/23_STT_INTERFACE
  - 20_interface/24_VAD_INTERFACE
  - sap:16_VOICE_DOMAIN
  - waifu:21_LIVEKIT_INTEGRATION
---

# Speech Listener Domain
## Six STT Providers, One Recording Session, One VAD Slot

*— Rúnhild Svartdóttir, Architect*

> *The line between hearing and listening is the line between samples and meaning. CDK draws that line cleanly. SAP smudges it. Waifu trusts the cloud to draw it for them.*

`Scripts/SpeechListener/` is *the* domain that most teaches Ember about audio-input discipline. Sixteen files, roughly 1,800 LOC, organised into three layers: **microphone capture** (the `MicrophoneManager` + platform providers), **recording session control** (the `RecordingSession` value type with preroll + silence-trigger semantics), and **speech-to-text providers** (six concrete implementations plus an extension slot for ML-based VAD).

The domain's discipline is its *separation* — capture is one concern, session-management is another, transcription is a third. Each layer is mockable, swappable, and individually small. SAP's audio capture is `py/sherpa_asr.py` (93 LOC) tightly coupled to `server.py`'s mic-control globals. Waifu has nothing on-device; the cloud handles it. CDK *has* the layers, and the layers stay separated.

---

## 1. The Subject Itself

**What the domain is:** the *ear* of a CDK avatar. The microphone hardware feeds samples in at 44.1kHz (or whatever the platform supports); some logic decides "is this speech?" and "is the user done talking?"; the bytes go to a transcription service; text comes back. The domain owns all of that.

**What it owns:**

| Layer | Files | LOC | Owns |
|---|---|---|---|
| **Mic capture** | `MicrophoneManager.cs`, `IMicrophoneManager.cs`, `IMicrophoneProvider.cs`, `AndroidMicrophoneProvider.cs`, `IOSMicrophoneProvider.cs`, `MacMicrophoneProvider.cs` | ~440 | Reads samples per-frame, computes dB volume, dispatches to active recording sessions, mutes/stops the device |
| **Recording session** | `RecordingSession.cs` | 153 | A *single utterance*: preroll buffer, silence-triggered stop, voice-detect function chain, completion callback |
| **Listener base** | `SpeechListenerBase.cs`, `ISpeechListener.cs` | ~270 | The STT abstraction — registers a session with the mic, handles completion, resamples if needed, calls provider, invokes `OnRecognized`, detects barge-in |
| **Listener providers** | `Google`/`Azure`/`AzureStream`/`OpenAI`/`AIAvatarKit`/`AIAvatarKitStream` + `Dummy` | ~900 | Per-provider PCM-to-text wire format |
| **VAD extension** | `Extension/SileroVAD/SileroVADProcessor.cs` | 203 | ONNX-based Silero VAD plugin into the listener's `DetectVoiceFunctions` chain |

**What it does NOT own:**
- The decision *what to do with* recognised text — that's AIAvatar's `OnSpeechListenerRecognized` ([[11_AIAVATAR_DOMAIN]] §2.4).
- The microphone hardware drivers — those are Unity (`UnityMicrophoneProvider`) or platform-native (`AndroidNativeMicrophone`, etc., living in `Scripts/IO/`).
- The conversation lifecycle — that's `DialogProcessor` ([[13_DIALOG_PROCESSOR_DOMAIN]]).

---

## 2. How It Works

### 2.1 Layer 1 — `MicrophoneManager` reads samples

`MicrophoneManager.cs` (344 LOC) is the per-frame mic poller. On non-WebGL targets:

```csharp
// /tmp/ChatdollKit/Scripts/SpeechListener/MicrophoneManager.cs:130-153
public void StartMicrophone()
{
    if (MicrophoneProvider == null) {
        MicrophoneProvider = new UnityMicrophoneProvider();
    }
    if (MicrophoneDevice == null) {
        MicrophoneDevice = MicrophoneProvider.devices[0];
    }
    microphoneClip = MicrophoneProvider.Start(MicrophoneDevice, true, 1, SampleRate);
    lastSamplePosition = 0;
}
```

A circular 1-second `AudioClip` buffer (line 149's `Start(..., true, 1, SampleRate)`) is started; the device records into it; `Update` (lines 81-103) reads the delta since the last poll:

```csharp
// /tmp/ChatdollKit/Scripts/SpeechListener/MicrophoneManager.cs:81-103
private void Update()
{
    var samples = GetAmplitudeData();
    CurrentVolumeDb = GetCurrentMicVolumeDb(samples);
    if (samples.Length > 0) OnSamplesReceived?.Invoke(samples);
    for (int i = activeSessions.Count - 1; i >= 0; i--)
        activeSessions[i].ProcessSamples(samples, linearNoiseGateThreshold);
    IsRecording = MicrophoneProvider.IsRecording(MicrophoneDevice);
}
```

`GetAmplitudeData` (lines 242-306) handles the *circular buffer wrap-around* arithmetic correctly: if `currentPosition >= lastSamplePosition`, simple delta; otherwise, two `GetData` calls (end-of-buffer + start-of-buffer) concatenated. This is the part most developers get wrong; CDK gets it right.

`OnSamplesReceived` (line 89) is an event for *external* listeners (e.g., a recording-to-disk module that wants raw audio). `activeSessions[i].ProcessSamples` (line 96) is the *active dispatch* — every registered `RecordingSession` gets the samples. The reverse loop (line 94, `for (int i = ... ; i >= 0; i--)`) is to handle the case where `ProcessSamples` triggers `OnRecordingComplete` which calls `StopRecording` which removes the session from `activeSessions` — *removing during forward iteration would throw*; reverse iteration is safe. CDK comments this explicitly (line 92-93). Good citizenship.

**Platform providers** (`AndroidMicrophoneProvider.cs`, `IOSMicrophoneProvider.cs`, `MacMicrophoneProvider.cs`) are 19 lines each — thin wrappers around `AndroidNativeMicrophone` / `IOSNativeMicrophone` / `MacNativeMicrophone` (in `Scripts/IO/`). The pattern: `IMicrophoneProvider` is the interface; per-platform implementations exist; `MicrophoneManager.StartMicrophone` defaults to `UnityMicrophoneProvider` but the user can override by assigning `MicrophoneProvider = new AndroidMicrophoneProvider()` before `Start()`.

WebGL is the special case (lines 26-37, 60-72, etc.). `[DllImport("__Internal")]` calls into `WebGLMicrophone.jslib` (a JS-side audio worklet). Samples are pushed in via `SetSamplingData(string)` — either as parsed `float[]` from comma-separated text *or* (the optimized path, lines 197-234) as a malloc'd pointer + length string `"<ptr>:<len>"` that's `Marshal.Copy`'d into a reusable byte buffer. This is the GC-friendly path the comments push toward (line 71's warning *"Set useMallocInWebGL = true to improve performance"*). Without it, every WebGL sampling frame allocates a fresh `float[]` and a fresh string-split — performance death.

**WebGL teaching:** the `[DllImport("__Internal")]` + JS-side worklet pattern is what makes Unity-WebGL avatars audio-capable at all. The browser's `AudioWorklet` API is the audio source; the jslib is the bridge; the C# side polls. *No async; no callbacks; pure poll-and-marshal.* This is the WebGL audio paradigm Ember inherits if it ships a WebGL-tier.

### 2.2 Layer 2 — `RecordingSession` decides when an utterance is done

`RecordingSession.cs` (153 LOC) is the single utterance's state. Construction (lines 28-38):

```csharp
public RecordingSession(
    string name,
    float silenceDurationThreshold,
    float minRecordingDuration,
    float maxRecordingDuration,
    int maxPrerollSamples,
    System.Action<float[]> onRecordingComplete,
    List<Func<float[], float, bool>> detectVoiceFunctions
)
```

The state-machine logic (`ProcessSamples`, lines 40-96):

1. **Check silence** by running every `DetectVoiceFunctions` in order — if *all* return false, `IsSilent = true`. Default: a single `IsVoiceDetectedByVolume` check (linear threshold). With SileroVAD plug-in: two checks, ML-based + volume.
2. **Start recording** if not already and not silent (lines 58-61).
3. **While recording**: if silent, increment `silenceDuration` by `Time.deltaTime`; if `silenceDuration >= SilenceDurationThreshold`, stop. If not silent, reset `silenceDuration` to 0. Append samples to `recordedSamples`. If past `MaxRecordingDuration`, stop *without* invoking the callback.
4. **When not recording**: append samples to the *preroll* circular buffer (lines 86-94) — last `maxPrerollSamples` samples held against the moment recording starts. The preroll captures the *start* of the voiced utterance that the silence-detector necessarily misses.

`StopRecording(invokeCallback)` (lines 111-134):
- Only invokes the callback if `recordingDuration >= MinRecordingDuration && <= MaxRecordingDuration`. Too-short utterances are discarded silently (the user said "uh" and didn't finish — not a question, don't transcribe).
- `GetCombinedSamples` (lines 136-151) concatenates the preroll buffer (correctly handling the circular wrap) with the recorded samples. The transcription provider receives both — voice from a fraction-of-a-second *before* the trigger.

**This is the cleanest utterance-detection logic in the three corpora.** SAP's `sherpa_asr.py` does not have preroll. Waifu hands the problem to LiveKit. CDK names every constant, exposes every threshold, and uses the right data structure (circular buffer for preroll).

The `DetectVoiceFunctions` *list* (line 14) is the **plug-in slot for VAD**. The default function (`SpeechListenerBase.IsVoiceDetectedByVolume`, lines 116-126) is a linear-threshold loop. SileroVAD plugs in as another function (`SileroVADProcessor.IsVoiced`, line 102). The chain semantics: **a sample counts as voiced if *any* detector says so** (line 49-55 — `IsSilent = !f(...)`; if `IsSilent` becomes false, break and proceed as voiced). So adding SileroVAD *broadens* the voice-detection sensitivity, never narrows it. Combined with a high volume threshold, this is the right shape: ML catches quiet voice the volume gate misses; volume catches loud noise the ML model might confuse.

### 2.3 Layer 3 — `SpeechListenerBase` orchestrates

`SpeechListenerBase.cs` (255 LOC) is the abstract STT consumer. It:

1. **Holds the session** (`session`, line 53).
2. **Starts a session** (`StartListening`, lines 86-114) — constructs a new `RecordingSession`, registers it with the `MicrophoneManager`. If `stopBeforeStart`, tears down any existing one first.
3. **Detects barge-in** (`Update`, lines 66-84) — if the session is recording, *not yet barge-in-triggered*, and either the configurable `BargeInCondition` returns true *or* `RecordDuration >= BargeInMinDuration` (default 1.5s), fires `OnBargeIn`. AIAvatar uses this to stop the avatar's own speech when the user starts talking over it ([[11_AIAVATAR_DOMAIN]] §2.1).
4. **Handles completion** (`HandleRecordingCompleteAsync`, lines 165-203) — optionally resamples to `TargetSampleRate` (most STT providers want 16kHz, not 44.1kHz), calls the provider-specific `ProcessTranscriptionAsync`, fires `OnRecognized(text)`, then restarts listening (line 202).

The **resample helper** (lines 146-163) is a hand-rolled linear-interpolation resampler. Acceptable quality for STT (which is robust to mild interpolation artifacts); not for archival audio. Cite this when Ember needs in-process resampling without an FFI dependency.

The **PCM-to-WAV helper** (`SampleToPCM`, lines 212-244) writes a RIFF/WAVE header and the 16-bit-int sample bytes. Most STT providers accept WAV directly; this is the format SpeechListenerBase produces. The header construction is by-the-spec — fields are exact (`"RIFF"`, `pcm.Length - 8` for size, etc.).

### 2.4 Layer 3b — The Six Providers

Each provider subclasses `SpeechListenerBase` and overrides `ProcessTranscriptionAsync(samples, sampleRate, token)`. They differ in wire format:

- **`GoogleSpeechListener`** (131 LOC) — POSTs Google's REST API with base64-encoded LINEAR16 audio, returns transcript from `results[0].alternatives[0].transcript`.
- **`AzureSpeechListener`** (119 LOC) — POSTs Azure's REST API with WAV, returns the `DisplayText`.
- **`AzureStreamSpeechListener`** (201 LOC) — opens a *streaming* WebSocket to Azure, sends chunked PCM, receives partial-recognition events. The largest provider because streaming has more state.
- **`OpenAISpeechListener`** (57 LOC) — POSTs OpenAI's `/audio/transcriptions` endpoint with WAV file form-data. The shortest provider; OpenAI's API is the simplest.
- **`AIAvatarKitSpeechListener`** — uses the AIAvatarKit-server endpoint (a sister-project HTTP service that wraps multiple cloud STTs).
- **`AIAvatarKitStreamSpeechListener`** (375 LOC) — streams to AIAvatarKit's WebSocket endpoint; the largest provider because it integrates streaming-STT *plus* turn-detection on the server side.

Plus `DummySpeechListener` for testing — accepts samples, returns a configurable string.

**Six providers; uniform contract; uniform integration.** A new provider is a new file + override one method. SAP has *one* provider hardcoded (`sherpa_asr.py`); Waifu has cloud-only. CDK lets you mix any of six at runtime via the enabled-flag pattern.

### 2.5 The SileroVAD plug-in

`Extension/SileroVAD/SileroVADProcessor.cs` (203 LOC) is the ML-based VAD. The pattern:

```csharp
// /tmp/ChatdollKit/Extension/SileroVAD/SileroVADProcessor.cs:102-142
public bool IsVoiced(float[] newSamples, float _)
{
    if (session == null || newSamples == null) return false;
    audioBuffer.AddRange(newSamples);

    if (audioBuffer.Count < sampleSize) return false;  // 512

    while (audioBuffer.Count >= sampleSize)
    {
        var chunkToProcess = new float[sampleSize];
        audioBuffer.CopyTo(0, chunkToProcess, 0, sampleSize);
        audioBuffer.RemoveRange(0, sampleSize);

        if (RunInference(chunkToProcess))
        {
            audioBuffer.Clear();
            ResetStates();
            return true;
        }
    }
    return false;
}
```

The buffer accumulates incoming samples; when it has ≥ 512 samples, an ONNX inference runs (at 16kHz). The model returns a probability; if > `threshold` (default 0.5), voiced. The state tensor (`state`, line 44 — a 2×1×128 float array) is the model's hidden state, preserved across inferences for temporal coherence.

The signature `IsVoiced(float[] newSamples, float linearThreshold)` matches the `DetectVoiceFunc` contract from `SpeechListenerBase` (line 32). To enable: drop a `SileroVADProcessor` component on the GameObject, add it to `DetectVoiceFunctions`. The architectural pattern: **VAD is a plug-in point in the recording-session's detection chain, not a baked-in default.**

WebGL has its own path (lines 19-31, 105-115) — calls `IsVoiceDetected` and `GetVoiceProbability` from `Plugins/SileroVAD.jslib` (a JS-side WASM-compiled Silero) and a copy of the ONNX runtime running in the browser. The architectural symmetry is preserved across platforms.

The full interface spec is at [[24_VAD_INTERFACE]].

### 2.6 The barge-in coupling with AIAvatar

`SpeechListenerBase.Update` (lines 71-83):

```csharp
if (IsRecording && !bargeInTriggered && session != null)
{
    var shouldBargeIn = BargeInCondition != null
        ? BargeInCondition(null, session.RecordDuration)
        : session.RecordDuration >= BargeInMinDuration;
    if (shouldBargeIn)
    {
        bargeInTriggered = true;
        OnBargeIn?.Invoke();
    }
}
```

`BargeInMinDuration` defaults to `1.5f` (line 49). The condition: *the user has been recording for 1.5 seconds and the avatar may still be speaking*. AIAvatar's `OnBargeIn` handler (`AIAvatar.cs:632-640`) checks `Mode >= Conversation && DialogProcessor.Status == Responding` and calls `StopChatAsync(continueDialog: true)` — interrupts the avatar's response, allows the user's interruption to be processed.

`BargeInCondition` is a `Func<string, float, bool>` (line 46) — the user can supply a custom check. Could be "if the recognized text contains 'wait'" or "if recording is >0.5s and volume is high." CDK exposes the hook; the application supplies the policy.

**Barge-in done right.** SAP has nothing equivalent; the user has to use the cancel-word. Waifu's `turnOffMicWhenAISpeaking: true` is the *opposite* — the user *cannot* barge in. CDK is the only one of the three with real barge-in.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The 1-second mic-clip buffer

`MicrophoneManager.StartMicrophone` (line 149): `MicrophoneProvider.Start(MicrophoneDevice, true, 1, SampleRate)` — *one* second circular buffer. If a frame is delayed by > 1 second (Unity main-thread stall), samples are overwritten before being read. Defensive: the `currentPosition < 0 || >= microphoneClip.samples` check (line 252) catches obviously-invalid positions and returns empty. But subtle delay-induced sample loss is silent. Ember should bound mic-frame latency.

### 3.2 The linear-interpolation resampler

`SpeechListenerBase.Resample` (lines 146-163) does linear interpolation. Acceptable for 44.1kHz → 16kHz STT *most of the time*. Down-sampling without a low-pass filter aliases high frequencies into the audible range — quiet but present. Most STT providers can handle it. Some can't (older Google models complained). Ember should use a proper resample library (e.g., `scipy.signal.resample_poly` with anti-alias filter) when not bound by FFI weight.

### 3.3 The barge-in threshold is global

`BargeInMinDuration` is a single field. If the avatar is mid-utterance of a long answer, the user *should* be able to barge in earlier (say, 0.5s). If the avatar is mid-thinking (Processing status, no audio playing yet), barge-in should be ~immediate. CDK does not adapt the threshold to the dialog status. The fix is one if; CDK doesn't do it.

### 3.4 No language detection

The `Language` field (`SpeechListenerBase.cs:36`) is hardcoded `"ja-JP"` (CDK's Japanese-first orientation). For multi-lingual users, the application must change the field per turn — no auto-detect. The `AlternativeLanguages` field (line 37) is documented in some providers (Azure) but unused in others.

### 3.5 The 19-line platform providers

`AndroidMicrophoneProvider.cs`, `IOSMicrophoneProvider.cs`, `MacMicrophoneProvider.cs` are each 19 lines — pure delegation. The pattern is *clean* but the *necessity* is a Unity quirk: the `Microphone` API has bugs on iOS/Android in certain configurations, so CDK ships native plugins (`Scripts/IO/IOSNativeMicrophone.cs`, etc.) and routes to them per-platform. This is a Unity-multi-platform tax most users don't see until they ship to iOS and the mic doesn't work.

### 3.6 The crisp parts (inventory)

- **The preroll circular buffer.** `RecordingSession`'s `maxPrerollSamples` (line 18) is a tunable that solves the "user said the first word before the VAD triggered" problem. Generic. Adoptable.
- **The detect-voice-as-list-of-callables** pattern. `DetectVoiceFunctions: List<Func<float[], float, bool>>` (line 14). Any number of detectors, OR-combined for sensitivity. SileroVAD is one; a user could add a custom "wake-word energy peak" detector. Generic.
- **The platform-mic-provider interface.** `IMicrophoneProvider` (line 13+) is a tiny interface: `IsRecording`, `Start`, `End`, `GetPosition`, `devices`. Five symbols. Per-platform implementations are 5 lines each. This is the right abstraction shape for "thing that produces samples."
- **The reverse-iterate-active-sessions** (`MicrophoneManager.cs:94-97`) for collection-modified-during-iteration safety. A small but real defensive pattern.
- **The malloc-pointer-marshal WebGL path** (lines 198-234). When GC pressure matters, allocate once and reuse; mark unsafe boundaries; comment why.
- **The barge-in `Func<string, float, bool>` policy hook** (line 46) — *the application supplies the policy*; the library supplies the mechanism.
- **The silent-rejection of too-short utterances** (lines 122-124 in `StopRecording`). Better UX than transcribing "uh."

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 4 — SpeechListener in the macro shape
- [[17_MICROPHONE_MANAGER_DOMAIN]] — the deeper read on `MicrophoneManager`
- [[23_STT_INTERFACE]] — the Auditor's full provider-by-provider catalogue
- [[24_VAD_INTERFACE]] — the SileroVAD plug-in contract
- [[sap:16_VOICE_DOMAIN]] — SAP's `sherpa_asr.py` for contrast
- [[waifu:21_LIVEKIT_INTEGRATION]] — Waifu's cloud-STT-via-LiveKit for contrast

---

## What This Means for Ember

**Adopt:**
- The **three-layer separation**: capture (`MicrophoneManager`), session (`RecordingSession`), transcription (`SpeechListenerBase` + providers). Source: `Scripts/SpeechListener/`, Apache-2.0 attribution required. Ember's audio-input subsystem (provisionally `Ember.eyra` — *ear*) follows this exact tri-layer.
- The **`RecordingSession` with preroll buffer and silence-trigger** (`Scripts/SpeechListener/RecordingSession.cs:1-153`). Lift wholesale into Python — the algorithm is unchanged; the data structure (circular buffer for preroll) translates directly. Apache-2.0 attribution required.
- The **`DetectVoiceFunctions: List<Callable>` chain** (line 14). Adopt as Ember's `voice_detectors: list[VoiceDetector]` with OR-semantics. Default detector: linear threshold. Plug-ins: SileroVAD, custom wake-word energy detector, custom keyword-energy detector.
- The **`IMicrophoneProvider` five-symbol interface** (`is_recording`, `start`, `end`, `get_position`, `devices`). Adopt as Ember's `MicrophoneProvider` Protocol. Implementations: `PyAudioProvider`, `SoundDeviceProvider`, `WebRTCProvider`. Per-platform selection at runtime.
- The **barge-in `BargeInCondition` hook** (`Scripts/SpeechListener/SpeechListenerBase.cs:46`). Adopt as Ember's `barge_in_policy: Callable[[str, float], bool]` — application supplies; library defaults to `duration >= 1.5s`.
- The **silent-rejection of too-short utterances** (`Scripts/SpeechListener/RecordingSession.cs:122-124`). Adopt the `MinRecordingDuration` check; emit a Sögumiðla `UtteranceTooShort` event for diagnostics. Apache-2.0 attribution required.

**Adapt:**
- **The 1-second mic-clip buffer.** Adapt as Ember's configurable `mic_buffer_seconds` — default 2 (more headroom for slow main-loop frames). Log warning on each near-overrun.
- **The linear-interpolation resampler.** Adapt by using `scipy.signal.resample_poly` (anti-aliased polyphase resampling) for quality. Keep the linear path as a fallback for resource-constrained Pi tier.
- **The global barge-in threshold.** Adapt as Ember's *adaptive* barge-in threshold — shorter (~0.3s) when avatar is in `Processing` (no audio yet), default 1.5s when `Responding` (audio playing). The status drives the threshold.
- **The hardcoded `ja-JP` Language default.** Adapt as Ember's `language: Optional[str]` defaulting to `None` → auto-detect via Whisper-language-id or per-provider auto-detect.

**Avoid:**
- **Linear interpolation resample without comment.** Ember's resample emits a `ResampleQuality` event noting the algorithm used; downstream observability is a feature.
- **A single `bargeInTriggered = false` flag** that hides re-arming. Ember tracks barge-in events on Sögumiðla so multiple barge-ins per utterance are visible. CDK's bool gets reset only at next `StartListening`.
- **Hardcoded provider strings** for transcription endpoints. Per-provider config lives in YAML; CDK's Inspector-fields-with-default approach is fine for Unity but not for portable Python.

**Invent:**
- **The Voice-Detector Chain as a Sögumiðla Event Stream.** Ember's voice detection emits *per-detector* events: `LinearThresholdDetector.fired`, `SileroVAD.fired`, `WakeWordEnergy.fired`. Aggregation logic (OR/AND/threshold-vote) becomes a typed Sögumiðla rule, not a `foreach` loop. Failure analysis: when a session does not trigger, the event stream shows *which detector(s) saw nothing*.
- **The Preroll-Buffer Replay Vow.** When an utterance is recognised, the preroll buffer's samples are *included* in the Sögumiðla `UtteranceTranscribed` event payload (or referenced by hash). This lets a session-post-mortem replay *exactly* what the transcription provider saw. CDK gives the provider the bytes and discards them; Ember keeps them addressable for the session's lifetime.
- **The Adaptive Barge-In Policy.** Ember's barge-in threshold *adapts* to the dialog status:
  - `Idling` → no barge-in (no avatar speech to interrupt).
  - `Processing` → 0.3s (avatar is thinking; cheap to abort).
  - `Responding (first sentence)` → 0.8s (give the avatar a chance to finish the intro).
  - `Responding (subsequent sentences)` → 0.4s (most utterance done; let user interrupt).
  Configurable per-realm; emits Sögumiðla `BargeInPolicyChanged` events on transitions.
- **The Multi-Provider STT Race.** Ember can configure two STT providers to *race* — fire both, take the first to return, log the disagreement if both return. CDK auto-selects exactly one provider; Ember can use *redundancy* for high-stakes turns (e.g., the wake-word turn) and *single-provider* for cheap turns. The race policy is per-config, not hardcoded.
- **The Preroll-Tunable-Per-Mode.** CDK's `MaxPrerollDuration` (line 30, default 0.2s) is fixed. Ember exposes per-`AvatarMode` preroll: 0.3s in idle (the user might have started a wake-word before the VAD caught up), 0.1s in conversation (the user is more aware of when to start, less preroll needed).

*Apache-2.0 attribution: when patterns from `ChatdollKit/Scripts/SpeechListener/` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

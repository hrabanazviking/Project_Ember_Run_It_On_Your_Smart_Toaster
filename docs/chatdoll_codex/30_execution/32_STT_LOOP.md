---
codex_id: 32_STT_LOOP
title: STT Loop — Mic to VAD to ONNX to Text
role: Forge-A
layer: Execution
status: draft
kit_source_refs:
  - Scripts/SpeechListener/MicrophoneManager.cs:1-344
  - Scripts/SpeechListener/SpeechListenerBase.cs:1-255
  - Scripts/SpeechListener/RecordingSession.cs:1-153
  - Scripts/SpeechListener/OpenAISpeechListener.cs:1-57
  - Extension/SileroVAD/SileroVADProcessor.cs:1-203
ember_subsystem_targets: [Funi, Munnr, Smiðja]
cross_refs:
  - 30_UNITY_BOOTSTRAP
  - 31_AIAVATAR_MAIN_LOOP
  - 24_VAD_INTERFACE
  - 23_STT_INTERFACE
  - sap:30_ELECTRON_BOOTSTRAP
  - waifu:30_BASIC_MODE_FLOW
license_posture: Apache-2.0 — adopt with attribution
---

# STT Loop

> *Microphone every frame. ONNX every 32ms. STT every utterance. The latency is the design.*

Forge-A. Eldra. The STT loop in ChatdollKit is three components stacked: `MicrophoneManager` capturing raw float samples from the OS, a `RecordingSession` slicing those samples into utterances, and an `ISpeechListener` implementation (Google / Azure / OpenAI / AIAvatarKit / Silero-gated variants) transcribing each utterance into text. Sitting next to all of this is an *optional* `SileroVADProcessor` that injects ML-based voice detection in place of the default amplitude threshold. The whole pipeline is 800-odd lines across five files and it is the most production-honest STT loop in any of the three corpora I've mined. Here is how it actually works.

## The Microphone, Every Frame

`MicrophoneManager` (`/tmp/ChatdollKit/Scripts/SpeechListener/MicrophoneManager.cs`, 344 lines) is the one component that runs every Update. Look at the per-frame work:

```csharp
// /tmp/ChatdollKit/Scripts/SpeechListener/MicrophoneManager.cs:81-103
private void Update()
{
    var samples = GetAmplitudeData();
    CurrentVolumeDb = GetCurrentMicVolumeDb(samples);

    // Stream samples to registered handler
    if (samples.Length > 0)
    {
        OnSamplesReceived?.Invoke(samples);
    }

    // NOTE: ProcessSamples may trigger OnRecordingComplete callback which calls StopRecording,
    // modifying activeSessions during iteration. Reverse loop prevents Collection modified exception.
    for (int i = activeSessions.Count - 1; i >= 0; i--)
    {
        activeSessions[i].ProcessSamples(samples, linearNoiseGateThreshold);
    }
    // platform-specific recording-state read follows
}
```

Three things per frame:

1. **Pull amplitude data.** `GetAmplitudeData()` (`:242-306` on native, `:182-194` on WebGL) reads from `Microphone.GetPosition(deviceName)` (Unity's built-in API), computes how many new samples since the last read, and copies them out of the circular AudioClip buffer. Handles wrap-around correctly. Returns an empty array if muted.
2. **Compute volume in dB.** `GetCurrentMicVolumeDb` (`:320-342`) is RMS → 20log10. Exposed on Inspector as `CurrentVolumeDb` for live debugging.
3. **Dispatch to every active RecordingSession.** Reverse-loop iteration because `ProcessSamples` may trigger `StopRecording` which removes the session from the list. The comment is honest about the bug surface.

The mic device runs from boot if `AutoStart=true` (`:42`, default). At 44100 Hz mono float, that's `44100 * 4 = 176KB/s` of audio data scanned per second, with ~30-60 calls per second to `GetPosition` and one call to `GetData`. Negligible on PC, measurable on mobile.

## WebGL Has Its Own Reality

There is a clear `#if UNITY_WEBGL && !UNITY_EDITOR` gate (`:4-8, :26-38, :60-62, :64-79, :104-128, :144-148, :181-240`). On WebGL, Unity's `Microphone` class doesn't exist — the browser handles audio capture entirely. CDK ships a JavaScript plugin (referenced via `[DllImport("__Internal")]` at `:27-36`) that calls `InitWebGLMicrophone`, `StartWebGLMicrophone`, `EndWebGLMicrophone`, `IsWebGLMicrophoneRecording`. Sample data arrives from JS into C# via a callback method (`SetSamplingData` at `:197-240`) that parses either a pointer-and-length string ("malloc mode", recommended) or a comma-separated float string ("fallback mode", `:235-239`).

The malloc/fallback split is one of those decisions that becomes important if Ember ever ships a WebGL build. The comma-separated path round-trips audio data through a C# string parse for every chunk; the malloc path uses `Marshal.Copy` from the WASM heap directly. Performance difference is roughly 10x on mid-range hardware. `[unverified — based on my reading of the code path, not measurement]`.

## The Recording Session — Where Utterances Are Born

A `RecordingSession` (`/tmp/ChatdollKit/Scripts/SpeechListener/RecordingSession.cs`, 153 lines) is the per-utterance state machine. It owns:

- A circular **preroll buffer** of `maxPrerollSamples` floats (default `~8800` samples = `0.2s` at 44.1kHz). This is the audio captured *before* voice was detected, so the start of the user's first syllable isn't clipped.
- A growing **recorded samples** `List<float>` once voice is detected.
- A list of **detect-voice functions** — `Func<float[], float, bool>` — that decide whether the current sample batch contains speech.

The state machine runs in `ProcessSamples` (`RecordingSession.cs:40-96`):

```csharp
// /tmp/ChatdollKit/Scripts/SpeechListener/RecordingSession.cs:46-84 (compressed)
IsSilent = true;
foreach (var f in DetectVoiceFunctions)
{
    IsSilent = !f(samples, linearNoiseGateThreshold);
    if (IsSilent) break;
}

if (!IsRecording && !IsSilent) StartRecording();

if (IsRecording)
{
    if (IsSilent)
    {
        silenceDuration += Time.deltaTime;
        if (silenceDuration >= SilenceDurationThreshold) StopRecording();
    }
    else silenceDuration = 0.0f;

    recordedSamples.AddRange(samples);

    if (Time.time - recordingStartTime > MaxRecordingDuration)
        StopRecording(invokeCallback: false);
}
else
{
    // Add samples to circular preroll buffer
}
```

The contract is: voice detected ⇒ start recording (with preroll attached at the front); silence > `SilenceDurationThreshold` ⇒ stop and fire callback with combined preroll + recorded samples; duration > `MaxRecordingDuration` ⇒ stop without firing (utterance too long, probably background noise). Voice detection is *any-of* — any single `DetectVoiceFunction` returning true is enough.

`StopRecording` (`:111-134`) also enforces a *minimum* duration: if the user said something for less than `MinRecordingDuration` (typically 0.2-0.3s), the recording is silently dropped. This filters out spurious clicks, lip-smacks, false-positive VAD triggers.

The list-of-detect-functions design is what lets CDK swap between amplitude-only detection (default, `SpeechListenerBase.IsVoiceDetectedByVolume` at `:116-126`) and Silero-VAD ONNX-model detection (drop in `SileroVADProcessor.IsVoiced` from the Extension folder). Stack them and you get hybrid — but the *any-of* semantics mean stacking gives you *more permissive* detection, not less. To make hybrid work as you'd intuit (both must agree), you'd need to add an `all-of` mode.

## SpeechListenerBase — The STT Driver

`SpeechListenerBase` (`/tmp/ChatdollKit/Scripts/SpeechListener/SpeechListenerBase.cs`, 255 lines) is the abstract base every concrete STT provider extends. The hot path is `HandleRecordingCompleteAsync` (`:165-203`):

```csharp
// /tmp/ChatdollKit/Scripts/SpeechListener/SpeechListenerBase.cs:165-203 (compressed)
protected async UniTask HandleRecordingCompleteAsync(float[] samples, CancellationToken token)
{
    try
    {
        float[] samplesToTranscript;
        int sampleRate;
        if (TargetSampleRate > 0 && microphoneManager.SampleRate > TargetSampleRate)
        {
            sampleRate = TargetSampleRate;
            samplesToTranscript = Resample(samples, microphoneManager.SampleRate, TargetSampleRate);
        }
        else
        {
            sampleRate = microphoneManager.SampleRate;
            samplesToTranscript = samples;
        }

        var text = await ProcessTranscriptionAsync(samplesToTranscript, sampleRate, token);
        if (OnRecognized != null) await OnRecognized(text);
    }
    // catches omitted
    StartListening(true);
}
```

Optional downsample (44100 → 16000 is the typical OpenAI Whisper preference), then provider-specific transcription, then `OnRecognized(text)` fires — which is wired to `AIAvatar.OnSpeechListenerRecognized` from the bootstrap (see [[30_UNITY_BOOTSTRAP]] Phase 6). After transcription, the listener restarts itself (`StartListening(true)`) — there is no per-call setup beyond the constructor.

The actual provider work is one virtual method. OpenAI's (`OpenAISpeechListener.cs:18-55`) is 37 lines: build a multipart form with the WAV-encoded PCM (via `SampleToPCM` at `SpeechListenerBase.cs:212-243`, which inlines a 44-byte WAV header by hand — no library dependency), POST to `https://api.openai.com/v1/audio/transcriptions`, return the text. Whisper-1 model by default. That's the entire STT integration for OpenAI.

Latency budget on this path, end-to-end on a typical conversational utterance:
- **Voice detection trigger:** ~0-33ms (one frame).
- **Recording duration:** typically 0.5-3s (user-bounded).
- **Silence wait:** `SilenceDurationThreshold = 0.4s` during conversation mode (so post-final-syllable, we wait 400ms before transcribing).
- **Optional downsample:** ~5-20ms for a 3s clip (linear interpolation, not great quality but cheap).
- **HTTP round-trip to Whisper:** 300-800ms typically.
- **`OnRecognized` invocation:** sync into AIAvatar.

Total: ~1-2s from end-of-utterance to dialog start. That's the baseline. Streaming STT (Azure / Google / AIAvatarKit) brings this down by overlapping transcription with recording, but the base `SpeechListenerBase` is post-utterance.

## Silero VAD — The ML-Based Voice Detector

`SileroVADProcessor` (`/tmp/ChatdollKit/Extension/SileroVAD/SileroVADProcessor.cs`, 203 lines) is CDK's most distinctive STT component and the one that justifies the deep dive. It runs the Silero VAD ONNX model on rolling 512-sample chunks at 16kHz, producing a per-chunk speech-probability that gates the recording session.

The native (non-WebGL) path runs Microsoft.ML.OnnxRuntime in-process:

```csharp
// /tmp/ChatdollKit/Extension/SileroVAD/SileroVADProcessor.cs:88-99
string modelPath = Path.Combine(Application.streamingAssetsPath, onnxModelName);
session = new InferenceSession(modelPath, new SessionOptions());
ResetStates();
Debug.Log($"VAD Initialized. Expecting {modelSamplingRate}Hz audio. Processing chunk size: {sampleSize}.");
```

`silero_vad.onnx` is loaded from `StreamingAssets/` (the Unity-canonical path for runtime-loaded asset blobs). The model expects 16kHz mono float audio in 512-sample chunks. CDK buffers incoming samples until it has ≥512 (`:121-137`), then runs inference:

```csharp
// /tmp/ChatdollKit/Extension/SileroVAD/SileroVADProcessor.cs:150-190 (compressed)
var inputShape = new int[] { 1, sampleSize };
var srShape = new int[] { 1 };
var stateShape = new int[] { 2, 1, 128 };

var inputTensor = new DenseTensor<float>(audioSamples, inputShape);
var srTensor = new DenseTensor<long>(new long[] { this.modelSamplingRate }, srShape);
var stateTensor = new DenseTensor<float>(this.state, stateShape);

var inputs = new List<NamedOnnxValue>
{
    NamedOnnxValue.CreateFromTensor("input", inputTensor),
    NamedOnnxValue.CreateFromTensor("sr", srTensor),
    NamedOnnxValue.CreateFromTensor("state", stateTensor)
};

using (var results = session.Run(inputs))
{
    var outputValue = results.FirstOrDefault(v => v.Name == "output");
    var stateNValue = results.FirstOrDefault(v => v.Name == "stateN");

    if (outputValue != null)
    {
        lastProbability = outputValue.AsTensor<float>().ToArray()[0];
        if (stateNValue != null)
            stateNValue.AsTensor<float>().ToArray().CopyTo(this.state, 0);
        return lastProbability > threshold;
    }
}
```

Three input tensors: the audio chunk, the sample rate, and a 2×1×128 GRU state tensor that gets fed back from the model's previous inference. The state tensor is what makes this *not* a stateless classifier — Silero VAD has memory of recent audio. The model returns `output` (speech probability ∈ [0,1]) and `stateN` (the new GRU state to carry into the next inference). CDK clobbers the local state with the new one after each inference.

The default threshold is `0.5f` (`:49`). Above that = voiced. The model file is shipped in `StreamingAssets/`; size is roughly 1.5MB per the Silero release. Inference cost per 32ms (512 samples at 16kHz) chunk is ~0.5-2ms on a modern CPU. Negligible at 30Hz update.

Android requires copying the model from `StreamingAssets` (jar-internal) to `persistentDataPath` first because ONNX Runtime can't read from inside the APK directly (`:71-87`). One of those mobile-build gotchas you only find by shipping.

WebGL drops the ONNX runtime entirely and calls into JS (`:21-30`) — a separate Silero implementation must be linked into the WebGL build. The `.jslib` for that is in the project but I haven't read it (Forge-B's WebGL slug covers this).

## Where It Breaks

- **The mic preroll buffer is 0.2s by default.** If the user begins speech while in `Sleep` mode (no active RecordingSession to consume the preroll), the first 200ms of the wake word can be missed entirely. CDK partially mitigates this by maintaining the preroll on the session itself, but the session only exists when `StartListening` has run. Sleep → wake transition has a real audio-clipping window.
- **`Microphone.GetPosition` wraparound logic at `MicrophoneManager.cs:258-295`** is correct but doesn't handle the case where `currentPosition < lastSamplePosition` AND `currentPosition - lastSamplePosition > microphoneClip.samples`. Buffer underrun (slow frame) can silently skip samples. There's no warning emitted.
- **`OperationCanceledException` is caught and silently swallowed** at `:193-195`. If transcription is cancelled mid-flight, `StartListening(true)` still runs in the finally — restarting the listener even on cancel. Generally correct behavior, but can cause restart loops if cancellation is being triggered repeatedly by an upstream component.
- **`Resample` (`:146-163`) is linear interpolation.** Not anti-aliased. Going 44.1k → 16k by linear interp introduces aliasing artifacts. For Whisper this seems to be in tolerance (the user reports work fine), but for higher-quality STT or analytical pipelines, this is a real quality hit.
- **The Silero model state (`state[256]`) is per-VADProcessor-instance, never reset on session boundary.** If the user pauses for 30 seconds and starts a new utterance, the VAD's internal GRU state still reflects audio from before the pause. The model is robust enough to recover, but a clean per-session reset would be more correct.
- **Threshold is checked with `Mathf.Abs(threshold - lastThreshold) > 0.01f`** (`:107-111`, WebGL path). 0.01 is a magic constant for change-detection. If a user tweaks the threshold from `0.5` to `0.505`, no update is sent to JS. Probably fine in practice but worth flagging.

## Where It Surprises

- **The mic device boots independent of any STT listener being ready.** `MicrophoneManager.Start` ignores SpeechListener state entirely. This is what lets multiple listeners coexist on the same scene — they all share the mic.
- **WAV header is hand-coded** (`SpeechListenerBase.cs:229-244`). No `System.IO.WaveFile` or similar. Forty-four bytes of `Encoding.ASCII.GetBytes("RIFF")` + size + `WAVE` + `fmt ` + … This is correct, well-commented, and zero-dependency. Vendor-worthy.
- **The `BargeInMinDuration` of 1.5s** (`SpeechListenerBase.cs:49`) is what gates barge-in. If recording exceeds 1.5s with non-silence, `OnBargeIn` fires. This is how CDK detects "the user is talking over the avatar" without needing to coordinate with the TTS playback layer (full discussion in [[37_BARGE_IN_INTERRUPT]]).
- **There is no centralised STT result confidence.** Whisper's text-format response doesn't include logprobs; CDK doesn't request the JSON format that would. Confidence-gated dialog logic is impossible at this surface — extend the listener to return a typed `TranscriptionResult { text, confidence, language }` if you want it.

## Cross-References

- [[30_UNITY_BOOTSTRAP]] — how `OnRecognized` and `OnBargeIn` got wired to AIAvatar
- [[31_AIAVATAR_MAIN_LOOP]] — the priority cascade that consumes the transcribed text
- [[24_VAD_INTERFACE]] — Architect's domain view of VAD as a swappable interface
- [[23_STT_INTERFACE]] — Auditor's deep dive on each STT provider
- [[sap:30_ELECTRON_BOOTSTRAP]] — contrast: SAP uses `sherpa-onnx` (k2-sherpa) running in Python, not in-process Unity
- [[waifu:30_BASIC_MODE_FLOW]] — contrast: Waifu's STT is invisible cloud, no model file, no threshold knob

## What This Means for Ember

**Adopt:**

- **The list-of-detect-functions pattern in RecordingSession** (`RecordingSession.cs:14`, Apache-2.0 attribution required). Compose voice-detection via stackable callables. Ember's Funi audio layer should ship this as `funi.audio.add_voice_detector(fn)`. Default detector is amplitude-threshold; ML detectors compose in.
- **The preroll-circular-buffer pattern.** `maxPrerollSamples` of 0.2s prevents first-syllable clipping. Standard, well-implemented in CDK (`RecordingSession.cs:88-95, 136-150`), vendor verbatim.
- **The hand-coded WAV header** (`SpeechListenerBase.cs:212-243`). Forty-four bytes, zero dependency, correct. This is the answer to "should we depend on a WAV library for one-shot encoding?" — no, write the header.
- **Silero VAD as the Hjarta-Funi quality bar.** The 1.5MB ONNX model running in-process at 0.5ms/chunk is the right tier for "local voice-activity detection that beats amplitude threshold." Ember should ship this on the Andlit-unity tier; the SAP tier should use sherpa-onnx's VAD; the cloud tier defers to provider.

**Adapt:**

- **The any-of voice detection semantics.** Adopt the stackable pattern but parameterize: `funi.audio.add_voice_detector(fn, combine="any" | "all" | "weighted")`. CDK's any-of is fine for default but not always what you want.
- **Latency budget.** CDK's ~1-2s end-to-end is acceptable for desktop but feels slow on mobile or for "wake and respond" UX. Ember should target ~500ms baseline with streaming STT as the primary path. The Whisper-via-HTTP pattern is good for fallback only.
- **WebGL `useMallocInWebGL = true` default.** CDK ships with `true` but logs a warning if false. Ember should make malloc-mode the only path for any web tier — no fallback to comma-split string parsing.

**Avoid:**

- **Silent OperationCanceledException swallow at `:193-195`.** Ember should log cancellation reasons and surface a typed event so upstream code can detect cancel-restart loops.
- **Linear resample for downsampling.** Use a real anti-aliased filter (3-tap FIR is enough). Linear is fine for prototyping, wrong for production STT.
- **Magic-number `0.5f` VAD threshold default.** Make it explicit and per-profile (quiet room / noisy room / streaming-broadcast).

**Invent:**

- **Funi Voice Probability Tape.** Instead of `IsVoiceDetected` boolean, expose a per-frame `voice_probability ∈ [0,1]` stream. Downstream consumers can choose their own threshold or do their own analysis (e.g., Hjarta correlating voice presence with affection-state). CDK has the data internally (`SileroVADProcessor.lastProbability`) but only exposes the boolean.
- **Hjarta Speech Hysteresis.** Two thresholds, not one: `enter_threshold = 0.6`, `exit_threshold = 0.4`. Once recording starts at `> 0.6`, it doesn't stop until probability `< 0.4`. Prevents flutter at marginal SNR. This is a known VAD-design pattern Silero's authors mention in their docs; CDK does not implement it.
- **Munnr Live Transcript Log.** Every `OnRecognized` invocation produces a typed `TranscriptEvent { id, text, source_listener, language, sample_rate, duration_ms, vad_probability_max, vad_probability_mean }` that Hjarta archives and Munnr can render as a live conversation log. CDK has all this data internally; nothing structured comes out.

---

*Apache-2.0 attribution: when adopting CDK's STT loop, RecordingSession, or SileroVADProcessor into Ember source, preserve the ChatdollKit header reference per Apache-2.0 §4(c). Silero VAD itself is MIT-licensed.*

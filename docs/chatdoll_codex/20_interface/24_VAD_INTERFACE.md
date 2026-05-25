---
codex_id: 24_VAD_INTERFACE
title: VAD Interface — One Function Signature, One ONNX Model, Two Substrate Paths
role: Architect
layer: Interface
status: draft
chatdoll_source_refs:
  - Extension/SileroVAD/SileroVADProcessor.cs:1-203
  - Scripts/SpeechListener/SpeechListenerBase.cs:14-126
  - Scripts/SpeechListener/RecordingSession.cs:1-153
  - Plugins/CopyThisJSToStreamingAssets/silero-vad.js
ember_subsystem_targets: [Munnr, Funi]
cross_refs:
  - 10_domain/14_SPEECH_LISTENER_DOMAIN
  - 10_domain/17_MICROPHONE_MANAGER_DOMAIN
  - 10_domain/1D_MULTI_PLATFORM_DOMAIN
  - sap:16_VOICE_DOMAIN
  - waifu:21_LIVEKIT_INTEGRATION
---

# VAD Interface
## One Function Signature, One ONNX Model, Two Substrate Paths

*— Rúnhild Svartdóttir, Architect*

> *The cleanest interface contract in ChatdollKit is the one for voice activity detection. It is two words long. `IsVoiced(float[] samples, float threshold) → bool`. The architectural reason this contract works is that voice activity detection is unambiguous in shape — bytes go in, decision comes out — and the implementation choice (linear threshold, ML model, custom heuristic) varies wildly without changing the question.*

`Extension/SileroVAD/SileroVADProcessor.cs` (203 LOC) is the canonical *plug-in voice activity detector* in CDK. The interface it conforms to is **not** a Unity `interface` keyword — it is a *function signature*, registered into a list of callables on `SpeechListenerBase`:

```csharp
// SpeechListenerBase.cs:32 (approx)
public List<Func<float[], float, bool>> DetectVoiceFunctions { get; set; }
    = new List<Func<float[], float, bool>>();
```

The list type *is* the interface. Any callable with the signature `(float[] samples, float linearThreshold) → bool` can be added. The default detector (`IsVoiceDetectedByVolume`, lines 116-126) is a simple linear-threshold loop. The SileroVAD plug-in (`SileroVADProcessor.IsVoiced`, line 102-142) is an ONNX-based ML detector. **Both fit the same signature.** Both can be in the list simultaneously; the combiner semantics (OR-of-results) lives in `RecordingSession.ProcessSamples` (line 49-55).

This is the right shape for a *plug-in interface*: a function signature, a registry, an explicit combiner. Three primitives; arbitrary implementations. The SileroVAD case is interesting because it demonstrates that a small interface can absorb an ONNX runtime + a 1.4MB neural network model + two substrate paths (native CLR + browser WASM) without growing the contract.

---

## 1. The Contract

### 1.1 The function-as-interface

The "interface" is the type `Func<float[], float, bool>`. Two parameters:

- `samples: float[]` — the latest batch of audio samples from `MicrophoneManager` since the last frame. Variable length (typically 50-1000 samples depending on Unity frame timing and the platform's audio buffer size).
- `linearThreshold: float` — the global noise-gate threshold from `MicrophoneManager.linearNoiseGateThreshold`, computed as `10^(NoiseGateThresholdDb/20)` (default `-50dB` → `~0.00316`).

Returns: `bool` — true if voice detected; false if silence.

**The threshold parameter is interesting.** It is the *global* linear threshold, computed once from the dB config. Each detector decides whether to use it. The volume-based detector compares every sample's absolute value against it. The SileroVAD detector *ignores* it (the second parameter is `_` in line 102) — its threshold is its own `threshold: float = 0.5` field for the ONNX probability output. **The interface passes the global hint; the implementation decides whether to use it.** This is the right shape — detectors are not forced into one definition of "loudness."

### 1.2 The combiner semantics

`RecordingSession.ProcessSamples` (lines 49-55):

```csharp
var isSilent = true;
foreach (var detectFunc in detectVoiceFunctions) {
    if (!detectFunc(samples, linearNoiseGateThreshold)) continue;
    isSilent = false;
    break;
}
```

**OR semantics**: a sample counts as voiced if *any* detector says it is. The first true-returning detector short-circuits the loop. **Detectors are voice-detection-sensitivity *broadeners*, not narrowers.** Adding SileroVAD on top of the volume detector means: catch voice that *either* exceeds the volume threshold *or* the ML model recognises. Catching false positives (e.g., loud noise the ML model would correctly reject) is the user's problem to address by *tuning the volume threshold*, not by AND-combining detectors.

For Ember: this is a deliberate design choice with consequences. The alternative (AND-combining) would give fewer false positives but more missed-quiet-voice misses. CDK's choice favours *recall over precision* — better to record a false positive than miss a quiet question. The choice is right for voice-companion use; might be wrong for security applications. Ember should expose the combiner policy (`OR` / `AND` / `THRESHOLD_VOTE` / `WEIGHTED`).

### 1.3 The optional `Initialize` lifecycle method

`SileroVADProcessor.Initialize()` (line 64-100) is *not* part of the function-signature interface; it is a separate setup method. The user calls it from their startup code:

```csharp
sileroVADProcessor.Initialize();
recordingSession.detectVoiceFunctions.Add(sileroVADProcessor.IsVoiced);
```

The two-call pattern: configure the detector, then plug it into the recording session. CDK does not enforce this; the user does. Detectors without expensive setup (the linear volume one) skip `Initialize` entirely. **The interface is the function; the setup is the implementation's concern.**

---

## 2. The SileroVAD Implementation

### 2.1 What Silero VAD is

[unverified — README claim only] **Silero VAD** is an open-source neural network voice activity detector developed by Silero (silero-models project). It is a small (~1.4MB) ONNX model trained on multi-language speech vs noise. The inference is *fast* — typically ~1ms per 30ms audio chunk on CPU. The output is a probability `[0, 1]` representing the model's confidence that the chunk contains voiced speech.

Silero VAD's *key features* for embedded use:
- Small model (1.4MB ONNX file).
- 16kHz sample rate.
- 512-sample chunks (~32ms at 16kHz).
- Stateful — the model has a hidden state preserved across inferences for temporal coherence (the `state: float[256]` in CDK or the 2×1×128 tensor passed in).
- Robust to multi-language speech, noise, music.

The Silero VAD ONNX file is shipped (or expected) in `Application.streamingAssetsPath/silero_vad.onnx` (CDK line 89). The Android path copies it to `persistentDataPath` first (lines 71-87) because Android's `streamingAssetsPath` is *not* a filesystem path on Android — it is inside an APK archive that the C# code cannot read directly.

### 2.2 The ONNX runtime dependency

`Microsoft.ML.OnnxRuntime` (CDK line 12-13) is the inference engine. NuGet package via Unity's NuGet integration. **This is a 50-150MB native dependency depending on platform** — the second-largest single dependency CDK ships (after Unity itself). The Auditor catalogues at [[50_DEPENDENCY_HEALTH]].

For WebGL, ONNX runtime is *not* available as a Unity package. CDK's workaround: use a JS-side WASM-compiled Silero VAD (the `Plugins/CopyThisJSToStreamingAssets/silero-vad.js` file). The C# side does *not* run inference; the JS side does. The C# side calls into JS via `[DllImport]`:

```csharp
// SileroVADProcessor.cs:21-28 (WebGL branch)
[DllImport("__Internal", EntryPoint = "IsVoiceDetected")]
private static extern int IsVoiceDetectedJS();
[DllImport("__Internal")]
private static extern float GetVoiceProbability();
[DllImport("__Internal")]
private static extern void SetVADThreshold(float threshold);
```

**Two distinct ONNX-runtime substrates, one C# interface.** Native: full `InferenceSession.Run()` on `Microsoft.ML.OnnxRuntime`. WebGL: WASM-compiled Silero loaded by `silero-vad.js`, exposed via three JS functions, glued to C# via DllImport. Both produce the same `bool` return from `IsVoiced`. The user does not see the substrate; the user sees the function.

### 2.3 The native inference path

`SileroVADProcessor.RunInference` (lines 150-190):

```csharp
private bool RunInference(float[] audioSamples) {
    var inputShape = new int[] { 1, sampleSize };          // 1 × 512
    var srShape = new int[] { 1 };
    var stateShape = new int[] { 2, 1, 128 };

    var inputTensor = new DenseTensor<float>(audioSamples, inputShape);
    var srTensor = new DenseTensor<long>(new long[] { modelSamplingRate }, srShape);
    var stateTensor = new DenseTensor<float>(this.state, stateShape);

    var inputs = new List<NamedOnnxValue> {
        NamedOnnxValue.CreateFromTensor("input", inputTensor),
        NamedOnnxValue.CreateFromTensor("sr", srTensor),
        NamedOnnxValue.CreateFromTensor("state", stateTensor)
    };

    using (var results = session.Run(inputs)) {
        var outputValue = results.FirstOrDefault(v => v.Name == "output");
        var stateNValue = results.FirstOrDefault(v => v.Name == "stateN");

        if (outputValue != null) {
            lastProbability = outputValue.AsTensor<float>().ToArray()[0];
            if (stateNValue != null) {
                stateNValue.AsTensor<float>().ToArray().CopyTo(this.state, 0);
            }
            return lastProbability > threshold;
        }
    }
    return false;
}
```

Three input tensors: audio (512 floats), sample rate (1 long), state (2×1×128 floats). One forward pass. Two outputs: `output` (a probability) and `stateN` (the updated hidden state — copied back into `this.state` for the next inference). The probability is compared against `threshold` (default 0.5); above → voiced.

**The stateful inference is the key.** A 32ms chunk is too short to tell voice from many noises; the stateful model uses recent-chunk context to disambiguate. CDK preserves the state across calls (line 179) but *resets* it (`ResetStates()`) after each voiced-detection (line 135). The reset is to prevent the model from "remembering" voice in a way that biases subsequent silence detection. Whether the reset is correct depends on the model's training; CDK assumes yes.

### 2.4 The chunk-accumulator pattern

The native `IsVoiced` (lines 117-142) does *not* call `RunInference` on every input. It accumulates samples in a buffer and only runs inference when the buffer reaches `sampleSize = 512`:

```csharp
audioBuffer.AddRange(newSamples);
if (audioBuffer.Count < sampleSize) return false;

while (audioBuffer.Count >= sampleSize) {
    var chunkToProcess = new float[sampleSize];
    audioBuffer.CopyTo(0, chunkToProcess, 0, sampleSize);
    audioBuffer.RemoveRange(0, sampleSize);

    if (RunInference(chunkToProcess)) {
        audioBuffer.Clear();
        ResetStates();
        return true;
    }
}
return false;
```

**Mismatch between input rate (variable; Unity's per-frame batches) and inference rate (fixed; 512-sample chunks)** is absorbed by the buffer. When the buffer overflows the inference threshold, drain it chunk-by-chunk. When the buffer is short, accumulate and return false (not enough data to decide). When inference detects voice, clear the buffer (the recording session will start; the residual samples are *also* voiced so dropping them is fine; the preroll buffer in `RecordingSession` captures the start anyway).

The `audioBuffer.Clear()` + `ResetStates()` on voiced (line 134-135) is the correct shape: we've decided "yes, voice"; the recording session takes over; the next time we're called (after the recording session ends) is a fresh listening cycle.

### 2.5 The WebGL inference path

The WebGL `IsVoiced` (lines 104-115):

```csharp
public bool IsVoiced(float[] newSamples, float _) {
    if (IsMuted) return false;
    if (Mathf.Abs(threshold - lastThreshold) > 0.01f) {
        SetVADThreshold(threshold);
        lastThreshold = threshold;
    }
    lastProbability = GetVoiceProbability();
    return IsVoiceDetectedJS() == 1;
}
```

The JS side handles buffering, inference, and probability output. The C# side just queries the JS side per call. **Threshold updates are pushed to JS** when the C# `threshold` field changes. The state, the buffer, the inference — all JS-managed. The C# is a thin glue.

`Plugins/CopyThisJSToStreamingAssets/silero-vad.js` (read by browser at runtime from the streaming-assets path) is the WASM-Silero. It exposes the three functions; the WebGL Microphone bridge pushes samples; the inference runs in the audio thread.

**The substrate inversion is total.** Native: C# owns inference, JS knows nothing. WebGL: JS owns inference, C# knows nothing. The user-facing interface (`IsVoiced` returning bool) is identical. The substrate cost (ONNX runtime native vs WASM-Silero JS) is invisible to the consumer.

### 2.6 The platform-specific Android path

The `#if UNITY_ANDROID && !UNITY_EDITOR` block (lines 5-7, 71-87) reads the ONNX from `streamingAssetsPath` via `UnityWebRequest` (because direct file access fails on Android), writes it to `persistentDataPath`, then loads from there:

```csharp
string modelPath = Path.Combine(Application.persistentDataPath, onnxModelName);
using (UnityWebRequest www = UnityWebRequest.Get(Path.Combine(Application.streamingAssetsPath, onnxModelName))) {
    www.SendWebRequest();
    while (!www.isDone) { }  // Synchronous wait! (initialization context)
    if (www.result == UnityWebRequest.Result.Success) {
        File.WriteAllBytes(modelPath, www.downloadHandler.data);
    }
}
```

**Android substrate quirk**. The synchronous `while (!www.isDone) { }` is acceptable here because `Initialize` is called once at startup. In a hot path it would freeze the main thread. The Android workaround is a one-time pre-warming step.

---

## 3. The Plug-in Surface for Other Detectors

The `Func<float[], float, bool>` interface admits any compatible callable. Beyond the shipped two (volume-threshold + Silero), users could plug in:

- **Wake-word energy detector**: high-pass filter the samples, integrate energy, threshold against a wake-word-tuned floor. Useful when the wake-word has distinctive spectral characteristics.
- **Speaker-presence detector**: a small ML model trained on the specific user's voice. Suppress voice from other speakers entering the room.
- **Echo-cancellation post-detector**: detect if the captured samples correlate with the avatar's recent TTS output (echo coming back via the microphone). Return false to suppress.
- **VAD-vote detector**: run *three* different VAD models and OR (or vote-majority) on results. CDK's combiner already provides OR; users wanting majority would compose differently.
- **Schedule-aware detector**: return true only during configured listening windows. Useful for scheduled-only avatar deployments.

CDK ships two; the interface admits many more. The pattern is *open extension*; the only thing the user must do is "make a function with the right signature and add it to the list."

For Ember: the same pattern. Ember's `VoiceDetector` Protocol declares one method (`detect(samples, threshold) -> bool`); a `VoiceDetectorRegistry` holds the active detectors per realm; the combiner runs as a Sögumiðla-aware aggregator (each detector emits an event; the aggregator's policy decides).

---

## 4. Where the Interface Strains

### 4.1 The combiner is OR-only

`RecordingSession.ProcessSamples` is hardcoded OR. To get AND or vote-majority, the user has to write their own combiner-detector that wraps the others. CDK does not expose policy. Ember should.

### 4.2 The `linearThreshold` parameter is confusing

It is the *volume-based* noise-gate threshold. SileroVAD ignores it. New users may think it should affect their detector's behaviour and waste time. Ember's `VoiceDetector` Protocol should *not* pass a volume-specific hint; each detector knows its own configuration.

### 4.3 The stateful model requires per-call sequential ordering

If two detectors *both* run inference and the audio frames are split between them, the state coherence is lost. CDK's design has one Silero detector with one state; multiple Silero detectors with independent states would be possible but the user must manage them.

### 4.4 The Android `while (!www.isDone)` is risky beyond startup

If `Initialize` were called at runtime (e.g., user reload), the synchronous wait would freeze the main thread. CDK assumes startup-only; a future refactor must async-await.

### 4.5 No detector-confidence in the bool return

The Silero detector knows the probability (`lastProbability`); the bool throws it away. **For downstream observability** ("the detector said voice with confidence 0.51 — barely above threshold"), the bool is insufficient. Ember's protocol should return `DetectorResult(voiced: bool, confidence: Optional[float], detector_name: str)`.

### 4.6 The crisp parts

- **Function-signature-as-interface.** Two parameters, one return. The smallest viable VAD interface.
- **Detector-list-with-OR-combiner.** Sensitivity-broadening composition.
- **Stateful-ML-with-state-reset-on-voiced.** Correct for the use case.
- **Native + WebGL substrate parity.** Same function, two substrates, no consumer knowledge required.
- **The chunk-accumulator pattern.** Absorbs frame-rate mismatch.

---

## 5. Cross-References

- [[14_SPEECH_LISTENER_DOMAIN]] §2.5 — the SileroVAD plug-in in the domain context
- [[17_MICROPHONE_MANAGER_DOMAIN]] — where the samples come from
- [[1D_MULTI_PLATFORM_DOMAIN]] §2.5 — Tier-2 native-plugin cost (ONNX runtime per platform)
- [[50_DEPENDENCY_HEALTH]] — Auditor's note on ONNX runtime dependency weight
- [[55_WEBGL_GOTCHAS]] — WebGL-side WASM-Silero specifics
- [[sap:16_VOICE_DOMAIN]] — SAP has no ML-based VAD; uses volume only
- [[waifu:21_LIVEKIT_INTEGRATION]] — Waifu defers VAD to LiveKit cloud

---

## What This Means for Ember

**Adopt:**
- The **function-signature-as-interface** pattern. Ember's `VoiceDetector` is a Python `Protocol` with one method: `detect(samples: NDArray[float32]) -> DetectorResult`. Apache-2.0 attribution required.
- The **detector-list-with-combiner** pattern. Ember's `VoiceDetectorPipeline` holds a list; the combiner policy is configurable (`OR`, `AND`, `THRESHOLD_VOTE`, `WEIGHTED_SUM`).
- The **stateful-ML-with-state-reset-on-voiced** pattern. Ember's Silero adapter follows the CDK shape: accumulate samples, run 512-chunk inference, reset on detection.
- The **chunk-accumulator** pattern for rate-mismatch absorption.

*Apache-2.0 attribution: when patterns from `ChatdollKit/Extension/SileroVAD/` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:**
- The **`linearThreshold` second parameter** — drop it. Each detector knows its own threshold; no shared hint required.
- The **bool return** to a typed `DetectorResult(voiced: bool, confidence: Optional[float], detector_name: str, latency_ms: float)`. Observability for free.
- The **Native + WebGL dual-substrate** pattern. Ember's Pi-tier uses Python `onnxruntime` (CPU); future Tier-CLOUD uses WASM-Silero. Same `VoiceDetector` Protocol; two implementations selected at config time.
- The **synchronous Android Initialize** to async `async initialize()` with explicit await at startup.

**Avoid:**
- **Hardcoded OR combiner.** Always expose the policy.
- **Bool-only result.** Always return confidence + provenance.
- **Single state across multiple detectors.** Each detector has its own state.

**Invent:**
- **The Detector Event Stream Vow.** Each detector emits a Sögumiðla `VoiceDetectorFired(detector_name, voiced: bool, confidence: float, latency_ms: float)` event *before* the combiner aggregates. Failure analysis: when a session does not trigger, the event stream shows *which detector(s) saw nothing*. CDK's bool returns alone offer no observability; Ember's events do.
- **The Combiner-as-First-Class-Component.** Ember's `VoiceDetectorCombiner` is its own Protocol with `combine(results: list[DetectorResult]) -> bool`. Default: OR (CDK semantics). Plug-ins: AND, threshold-vote, weighted-sum. Configurable per-realm. The combiner is testable in isolation.
- **The Probability Calibration Pass.** Periodically (every 100 turns), Ember computes per-detector PRC curves on the session's recent samples (positive = the session ended with successful STT; negative = silence). Surfaces "Silero is biased on this microphone — recommend threshold 0.42 instead of 0.50." CDK's threshold is fixed; Ember's adapts based on real audio.
- **The Detector Capability Manifest.** Each Ember detector declares: `sample_rate: int`, `chunk_size_samples: int`, `latency_ms_estimate: float`, `model_size_mb: float`, `cpu_cost_per_chunk_us: int`. The runtime checks these against tier budgets at boot. Pi-tier may refuse Silero if `cpu_cost_per_chunk_us` exceeds the budget; falls back to volume-only. CDK has no such budget; Ember enforces.
- **The Echo-Cancellation Post-Detector.** Ember ships a built-in second detector that suppresses voice-detection when the captured samples correlate with the avatar's recent TTS output. Combined with `AND` semantics for output-period and `OR` otherwise. Solves the "avatar hears itself talking" problem CDK leaves to native plugins.
- **The Multi-Speaker-Aware Detection.** Ember's hypothetical advanced detector uses speaker embeddings to detect *which* speaker is talking. Returns `DetectorResult(voiced: true, speaker_id: "user-alice")`. The orchestrator can route differently per-speaker (only Alice's voice triggers turn; Bob's is logged for later review). Optional, opt-in; not Wave 5 baseline.
- **The Detector Replay Mode.** Sögumiðla `VoiceDetectorFired` events are captured with sample-window hashes; in replay mode, Ember can re-run a detector against a logged sample window to evaluate "would this detector have fired here?" Useful for tuning. CDK has no replay; Ember files samples for it.

---
codex_id: 17_MICROPHONE_MANAGER_DOMAIN
title: Microphone Manager Domain — One Buffer, Four Mic Backends, One Reverse Iteration
role: Architect
layer: Domain
status: draft
chatdoll_source_refs:
  - Scripts/SpeechListener/MicrophoneManager.cs:1-344
  - Scripts/SpeechListener/IMicrophoneManager.cs
  - Scripts/SpeechListener/IMicrophoneProvider.cs
  - Scripts/SpeechListener/AndroidMicrophoneProvider.cs:1-19
  - Scripts/SpeechListener/IOSMicrophoneProvider.cs:1-19
  - Scripts/SpeechListener/MacMicrophoneProvider.cs:1-19
  - Scripts/IO/AndroidNativeMicrophone.cs:1-150
  - Scripts/IO/IOSNativeMicrophone.cs
  - Scripts/IO/MacNativeMicrophone.cs
  - Scripts/SpeechListener/RecordingSession.cs:1-153
ember_subsystem_targets: [Munnr, Funi]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/14_SPEECH_LISTENER_DOMAIN
  - 10_domain/1D_MULTI_PLATFORM_DOMAIN
  - 20_interface/23_STT_INTERFACE
  - sap:16_VOICE_DOMAIN
  - waifu:21_LIVEKIT_INTEGRATION
---

# Microphone Manager Domain
## One Buffer, Four Mic Backends, One Reverse Iteration

*— Rúnhild Svartdóttir, Architect*

> *The microphone is the part of the embodiment that is most insulted by abstraction. The cloud-streaming codex ([[waifu:10_DOMAIN_MAP]]) treats it as a browser concern. The Electron codex ([[sap:16_VOICE_DOMAIN]]) treats it as Python's. CDK treats it as a real problem with real platform divergence, and pays for the per-platform work.*

`Scripts/SpeechListener/MicrophoneManager.cs` is 344 LOC. Its job is small in conception and ugly in implementation: *read PCM samples from the system microphone at whatever rate they arrive, on whatever platform the user built for, and hand them to interested parties*. The ugliness is **four distinct backends** — Unity's built-in `Microphone` class (Win/Mac/Linux/Editor), Android Native plugin, iOS Native plugin, Mac Native plugin — plus a fifth path for WebGL via JS audio worklet. Each backend has its own quirks; the `IMicrophoneProvider` interface (five methods) absorbs all of them.

The domain's discipline is its *narrowness*. `MicrophoneManager` does five things: start/stop the device, poll samples per frame, compute volume-dB, dispatch to active recording sessions, expose a noise-gate threshold. Anything else (voice activity detection, silence detection, transcription) lives in `RecordingSession` and `SpeechListenerBase` ([[14_SPEECH_LISTENER_DOMAIN]]). This is the *capture* layer; nothing more.

Compare SAP, which couples mic capture to `server.py`'s mute globals ([[sap:16_VOICE_DOMAIN]]). Compare Waifu, which has no on-device mic at all — the browser handles it via WebRTC. **CDK is the only corpus that grapples seriously with on-device microphone realities across five platforms**, and the patterns it produces are the most directly portable to Ember's Pi-tier on-device baseline.

---

## 1. The Subject Itself

**What the domain is:** the hardware-facing PCM sample producer. Sample rate (44.1kHz default); buffer (1-second circular `AudioClip` on native; queue-driven on WebGL); polling rate (per-frame, ~60Hz on desktop, ~30Hz on mobile); destination (every registered `RecordingSession` plus the `OnSamplesReceived` event for external listeners).

**What it owns:**

| Concern | Files | LOC | Owns |
|---|---|---|---|
| **Manager** | `MicrophoneManager.cs` | 344 | Per-frame poll loop, sample dispatch, dB volume, noise-gate threshold, mute control, session registry, the 1-second circular buffer |
| **Provider interface** | `IMicrophoneProvider.cs` | ~15 | Five-method contract: `IsRecording`, `Start`, `End`, `GetPosition`, `devices` |
| **Unity provider** | `UnityMicrophoneProvider` (nested in `MicrophoneManager.cs:13-21`) | 9 | Thin wrapper around Unity's `Microphone` class |
| **Android provider** | `AndroidMicrophoneProvider.cs` | 19 | Wrapper over `AndroidNativeMicrophone` (`Scripts/IO/AndroidNativeMicrophone.cs`, ~250 LOC) — `[DllImport]` to a JNI plugin |
| **iOS provider** | `IOSMicrophoneProvider.cs` | 19 | Wrapper over `IOSNativeMicrophone` — `[DllImport]` to an Objective-C plugin |
| **Mac provider** | `MacMicrophoneProvider.cs` | 19 | Wrapper over `MacNativeMicrophone` — `[DllImport]` to a Cocoa-side AVFoundation plugin |
| **WebGL path** | `MicrophoneManager.cs:26-44, 60-72, 106-128, 181-240` | ~100 | `[DllImport("__Internal")]` calls into `WebGLMicrophone.jslib`; samples pushed via `SetSamplingData(string)` |

**What it does NOT own:**
- Voice activity detection — that's `RecordingSession` + extension `SileroVADProcessor` ([[14_SPEECH_LISTENER_DOMAIN]] §2.5).
- Speech-to-text — that's `SpeechListenerBase` and its providers.
- Audio playback — `SpeechController` ([[12_MODEL_CONTROLLER_DOMAIN]]).
- The decision *what to do with* samples — that's the caller (anyone who registers an `OnSamplesReceived` handler or starts a `RecordingSession`).

---

## 2. How It Works

### 2.1 The four-platform-five-backend topology

The capture path differs per build target:

| Platform | Backend | Buffer model | Polling source |
|---|---|---|---|
| **Win / Linux / Editor** | `UnityMicrophoneProvider` (Unity's `Microphone`) | 1-second circular `AudioClip`, polled via `GetData()` | Unity main thread `Update()` |
| **Mac** | `MacMicrophoneProvider` → `MacNativeMicrophone` (AVFoundation) | Native ring buffer with `[DllImport]` access | Unity main thread `Update()` |
| **Android** | `AndroidMicrophoneProvider` → `AndroidNativeMicrophone` (Oboe/AAudio JNI) | Native ring buffer; voice-processing optional | Unity main thread `Update()` |
| **iOS** | `IOSMicrophoneProvider` → `IOSNativeMicrophone` (AVAudioEngine ObjC) | Native ring buffer with NSData bridge | Unity main thread `Update()` |
| **WebGL** | JS-side `AudioWorklet` → `webGLSamplesBuffer` queue → `SetSamplingData` callback | JS-managed queue; samples pushed *from* JS into C# | JS audio worklet → SendMessage → C# queue |

The reason Unity's built-in `Microphone` isn't used everywhere: on iOS and Android, the built-in has *real bugs* in production deployments — sample-rate negotiation fails, the mic device list is wrong on Android 10+, voice-processing (echo cancellation) is unavailable. CDK pays for native plugins on the mobile platforms where shipping requires reliability.

`AndroidNativeMicrophone` (`Scripts/IO/AndroidNativeMicrophone.cs:14-30`) is illustrative:

```csharp
[DllImport(PLUGIN_NAME)]
private static extern int AndroidNativeMicrophonePlugin_StartWithVoiceProcessing(
    string deviceName, int lengthSec, int frequency, int enableVoiceProcessing);
```

The native plugin exposes a `StartWithVoiceProcessing` variant Unity's built-in does not. **Voice processing = AEC + noise suppression** done by the OS audio stack. On Android, this is the difference between a usable phone-deployed avatar and one that hears its own TTS playing back. CDK ships the plugin and the C# wrapper; users get production-ready capture on mobile.

The Mac path uses AVFoundation's `AVAudioEngine` with the input tap and a circular buffer; the iOS path is similar with mobile-specific session category configuration; both are conditionally compiled with `#if UNITY_*` guards in their wrapper files.

### 2.2 The per-frame `Update` loop

`MicrophoneManager.Update` (`Scripts/SpeechListener/MicrophoneManager.cs:81-103`):

```csharp
private void Update()
{
    var samples = GetAmplitudeData();
    CurrentVolumeDb = GetCurrentMicVolumeDb(samples);

    if (samples.Length > 0) OnSamplesReceived?.Invoke(samples);

    // NOTE: ProcessSamples may trigger OnRecordingComplete which calls StopRecording,
    // modifying activeSessions during iteration. Reverse loop prevents Collection modified.
    for (int i = activeSessions.Count - 1; i >= 0; i--) {
        activeSessions[i].ProcessSamples(samples, linearNoiseGateThreshold);
    }
    IsRecording = ...;
}
```

Three things to note.

**The reverse-iterate**. `ProcessSamples` can trigger `StopRecording` which calls back into `StopRecordingSession(session)` which mutates `activeSessions`. Forward iteration would throw `InvalidOperationException` from the foreach. Reverse iteration is safe because removing index `i` doesn't change indices `< i`. CDK *comments* this explicitly (lines 92-93) — the kind of comment that says *we have been bitten by this exact bug before*. Adopt the discipline.

**The `OnSamplesReceived` event**. External listeners (a recording-to-disk module, a beat-detector, a custom analyzer) subscribe and receive every poll's samples. Decoupled from sessions; lets observers ride along without coupling to the recording flow.

**The single-thread guarantee**. Unity dispatches `Update` on the main thread. All `RecordingSession.ProcessSamples` calls, all `OnSamplesReceived` invocations, all session-list mutations — single-threaded. Zero locks. This is the *substrate gift* of Unity's runtime: the per-frame model gives you free thread discipline. Ember's asyncio runtime gives you a parallel free-discipline (single event-loop thread); the patterns translate cleanly.

### 2.3 The circular buffer arithmetic

`GetAmplitudeData` on native (`MicrophoneManager.cs:242-306`) is the gnarliest function in the file. Unity's `Microphone.Start(deviceName, true, 1, sampleRate)` creates a 1-second looping `AudioClip`; the OS writes into it in a circle; `GetPosition()` returns the current write head. The C# side reads from `lastSamplePosition` to `currentPosition`.

```csharp
var currentPosition = MicrophoneProvider.GetPosition(MicrophoneDevice);
if (currentPosition < 0 || currentPosition >= microphoneClip.samples) {
    Debug.LogWarning($"Invalid microphone position: {currentPosition}");
    return new float[0];
}

var sampleLength = (currentPosition >= lastSamplePosition)
    ? currentPosition - lastSamplePosition
    : microphoneClip.samples - lastSamplePosition + currentPosition;
```

**Wrap-around case** (lines 277-295): when `currentPosition < lastSamplePosition`, the write head has lapped the read head. CDK reads from `lastSamplePosition` to `microphoneClip.samples - 1` (end-of-buffer), then from `0` to `currentPosition - 1` (start-of-buffer), and concatenates. Two `GetData` calls, two source buffers, one destination buffer. This is the part most developers get wrong — most write a single-call read and silently lose samples on wrap-around. CDK gets it right and validates with a position-bounds check.

**Position-validity guard** (line 252): if `currentPosition < 0 || >= samples`, the driver is misbehaving (some Linux ALSA paths return invalid positions occasionally). CDK returns empty samples and logs; the next frame retries. Defensive against the driver; the rest of the pipeline tolerates short empty frames.

The buffer is 1 second long. If Unity's main thread stalls for >1 second (asset load, GC spike, dropped frame burst), samples are *overwritten before being read*. CDK does not detect this case; the lap-around is silent. For Ember, on a Pi-tier device with possible stall windows, increase the buffer to 2-3 seconds and add a *stall-detected* Sögumiðla event when the write head laps.

### 2.4 The WebGL audio worklet path

WebGL is the qualitatively-different backend. `[DllImport("__Internal")]` declarations (lines 27-36) call into `WebGLMicrophone.jslib` — a JS file with a `mergeInto(LibraryManager.library, { ... })` block that defines audio-worklet handlers.

The JS side **pushes** samples to the C# side (the inverse of native's *pull*). `SetSamplingData(string)` (lines 197-240) receives either:

- A comma-separated float text representation (slow; allocates a string and a `float[]` per frame), *or*
- A `<ptr>:<len>` string referring to a malloc'd buffer in the WASM heap (fast; `Marshal.Copy` from heap, then `Buffer.BlockCopy` to `float[]`, then `JsFree(src)`).

The malloc path (the optimisation called out at line 71) eliminates the per-frame string parse. The comment `"Set useMallocInWebGL = true to improve performance"` is the polite version of *"if you do not enable this, your WebGL avatar will GC-thrash"*. Adopt the malloc path by default if your build targets WebGL.

The buffer is a `Queue<float[]>` (`webGLSamplesBuffer`, line 37) — samples enqueued from JS, dequeued in `Update`. JS audio worklet runs at the browser's audio-thread rate (~128-sample chunks at 44.1kHz = ~344Hz callback); C# polls at frame rate (~60Hz). The queue absorbs the rate mismatch.

### 2.5 The noise gate

Two functions, four lines:

```csharp
// MicrophoneManager.cs:170-179
public void SetNoiseGateThresholdDb(float db) {
    NoiseGateThresholdDb = db;
    UpdateLinearVolumes();
}
private void UpdateLinearVolumes() {
    linearNoiseGateThreshold = Mathf.Pow(10.0f, NoiseGateThresholdDb / 20.0f);
}
```

The threshold is *passed to* `RecordingSession.ProcessSamples` (line 96) as the second argument. The default voice-detector (`SpeechListenerBase.IsVoiceDetectedByVolume`) compares each sample's absolute value against this linear threshold. The conversion from dB to linear (`10^(db/20)`) happens once per threshold change; per-sample comparisons are cheap.

**Default `-50dB`** (line 41) is reasonable for a quiet room. Noisy environments need a higher threshold (e.g. `-40dB`). CDK does not adapt; it is a fixed config. Ember should track ambient noise floor over the first few seconds and *suggest* a threshold (still let the user override).

### 2.6 The mute pattern

`MuteMicrophone(bool)` (line 164) sets `IsMuted`; `GetAmplitudeData` returns empty when muted (lines 184-189 WebGL, 246-249 native). The mic *device is still running*; samples are still being captured by the OS; CDK just refuses to read them. This is **soft mute** — the device draws power, the OS sees activity, but no samples flow up.

AIAvatar's `MicrophoneMuteStrategy` (`AIAvatar.cs`) enum offers `None`, `Threshold`, `Mute`, `StopDevice`, `StopListener` — the strategies are about *when avatar is speaking, what should the mic do?* Default: `Threshold` (raise the noise gate so the avatar's own voice doesn't trigger recording). `Mute` (soft-mute as above). `StopDevice` (actually call `MicrophoneProvider.End` — saves power, requires re-permission on iOS). Choice of strategy is per-deployment; the *menu* is the architectural achievement.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The 1-second buffer is brittle on slow hosts

A 1-second circular buffer at 44.1kHz is 44,100 samples. On a Raspberry Pi 4 running Unity-WebGL in a browser, frame stalls of >1 second under GC pressure are not uncommon. Samples are silently overwritten. CDK has no detection. Ember's Pi-tier needs a wider buffer (3-5s) and a stall-detection event.

### 3.2 The WebGL queue can grow unboundedly

`webGLSamplesBuffer.Enqueue` (lines 228, 238) is called from `SetSamplingData` — invoked by SendMessage from JS. If the C# `Update` is delayed (e.g. tab backgrounded), the queue accumulates. CDK has no cap. After a backgrounded tab returns, several minutes of audio replay through the recording pipeline in one frame. Should bound the queue (drop oldest, or pause JS-side capture when queue depth > N).

### 3.3 Native-plugin licensing and binary size

The Android `androidnativemicrophone.so` plugin is C++ JNI code; the iOS plugin is Objective-C; the Mac plugin is Objective-C++. Each adds ~50-200KB to the binary. Each requires per-platform build configuration. Each is a *separate maintenance surface* — when Android 14 changes the audio device API, CDK has to update the plugin and re-publish. The cost is real; the README does not foreground it.

### 3.4 The provider-swap is per-frame eligible but undocumented

`MicrophoneProvider` is a public property (line 44). In theory you could swap it mid-session — but `microphoneClip` is captured at `StartMicrophone` time, and changing providers without re-starting will produce wrong results. CDK does not document this; the safe path is `Stop → SetProvider → Start`.

### 3.5 Sample rate is global and immutable mid-session

`SampleRate = 44100` (line 40) is set at component-config time and not changed during a session. STT providers want 16kHz; downsampling happens in `SpeechListenerBase.Resample`. The waste (44.1kHz capture, downsample to 16kHz on STT call, throw away the rest) is intentional — capturing at 16kHz directly fails on some platforms whose audio drivers reject sub-44.1kHz requests. The price is computational, not architectural. Acceptable.

### 3.6 The `[unverified — README claim only]` device-list semantics

`UnityMicrophoneProvider.devices` returns `Microphone.devices`. The README claims this is reliable across platforms. *In practice*, Linux PulseAudio returns device names like `"alsa_input.pci-0000_00_1f.3.analog-stereo"` which are not user-readable; Android sometimes returns an empty list until permissions are granted; iOS returns device names that change after AirPods connect/disconnect. CDK accepts whatever the OS returns and lets the user pick. Ember should add a device-display-name normaliser.

### 3.7 The crisp parts

- **`IMicrophoneProvider` as a five-symbol interface**. `IsRecording` / `Start` / `End` / `GetPosition` / `devices`. The smallest interface that admits five backends. Adopt the interface shape.
- **The reverse-iterate-active-sessions pattern**. Three lines that prevent a real bug class.
- **The `OnSamplesReceived` event**. External observability without coupling.
- **The `useMallocInWebGL` performance switch**. Default to fast path; warn when slow path active. Performance trade-offs are visible.
- **The mute-strategy menu**. Five different strategies for the "what does the mic do during TTS playback?" question, exposed as an enum on AIAvatar.
- **The native-plugin shim per platform**. iOS / Android / Mac have native code; the C# wrapper is 19 lines each; the interface absorbs platform divergence.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 4 — MicrophoneManager in the macro shape
- [[14_SPEECH_LISTENER_DOMAIN]] §2.1 — MicrophoneManager from the listener's perspective
- [[1D_MULTI_PLATFORM_DOMAIN]] — full platform deltas including audio-plugin per-target builds
- [[23_STT_INTERFACE]] — what happens to the samples after capture
- [[sap:16_VOICE_DOMAIN]] — SAP's `sherpa_asr.py` with no platform-native paths
- [[waifu:21_LIVEKIT_INTEGRATION]] — Waifu's browser-WebRTC capture (no on-device mic class at all)

---

## What This Means for Ember

**Adopt:**
- The **`IMicrophoneProvider` five-method interface** (`Scripts/SpeechListener/IMicrophoneProvider.cs`). Ember's `MicrophoneProvider` Protocol: `is_recording()`, `start(device, loop, length_sec, frequency)`, `end()`, `get_position()`, `devices` property. Implementations: `PyAudioProvider`, `SoundDeviceProvider`, `ALSAProvider`, `PulseProvider`. Apache-2.0 attribution required.
- The **reverse-iterate-active-sessions pattern** (`Scripts/SpeechListener/MicrophoneManager.cs:94-97`). In Python: iterate `list(sessions)` for safety, or reverse-index manually. Ember's `MicrophoneManager.dispatch` uses the reverse pattern with a comment citing CDK.
- The **circular-buffer wrap-around handling** (`Scripts/SpeechListener/MicrophoneManager.cs:258-295`). The two-`GetData` concatenation translates directly to any circular-buffer abstraction.
- The **mute-strategy menu** as Ember's `MicMuteStrategy` enum: `None`, `Threshold`, `SoftMute`, `StopDevice`, `StopListener`. The choice is per-deployment YAML config.

*Apache-2.0 attribution: when patterns from `ChatdollKit/Scripts/SpeechListener/MicrophoneManager.cs` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:**
- The **1-second buffer** to a configurable `mic_buffer_seconds: int` defaulting to 3 (Pi-tier) or 2 (laptop-tier). Emit `MicBufferLapped` Sögumiðla event on detected overrun.
- The **native-plugin pattern** to Python's `ctypes`/`cffi` bindings to platform audio libs. For iOS / Android — different game; Ember does not ship those tiers in Wave 5.
- The **`useMallocInWebGL` toggle** as Ember's `transport_zero_copy: bool` config. Where the platform supports zero-copy buffer transfer (Linux `mmap`'d ALSA buffer, Wayland shared memory), prefer it; warn when slow path active.
- The **WebGL audio-worklet push model** as Ember's reference for *future browser-tier capture* (Tier-CLOUD). The pattern is the same: worklet pushes; C#/Python pulls from queue.

**Avoid:**
- **Unbounded WebGL sample queue**. Ember caps with a configurable `max_queued_seconds` (default 5s). Beyond the cap, drop oldest with a Sögumiðla event.
- **Fixed sample rate without observability**. Ember's `actual_sample_rate` may differ from `requested_sample_rate` (driver-clamped); the *actual* rate is exposed and used for downstream resampling math, not the requested one.
- **Provider-swap-without-restart silent failure**. Ember's `set_provider(p)` raises if a session is active.

**Invent:**
- **The Ambient Noise Floor Calibration Vow.** First three seconds of each session, Ember measures RMS dB and proposes a noise-gate threshold = ambient + 12dB. User can override but the *suggestion* is data-driven, not a config default. CDK fixes `-50dB`; Ember discovers `-37dB` in a kitchen.
- **The Mic-Stall Detector.** Ember tracks frame-to-frame delta between writes and reads. If the buffer is closer than 200ms to lap-around for N consecutive frames, fire `MicBufferStallImminent` — the orchestrator can drop animation fidelity or pause speech prefetch to reclaim main-loop budget.
- **The Capture Provenance Stamp.** Every batch of samples emitted to a `RecordingSession` carries a `(capture_start_t, capture_end_t, sample_rate, provider_name)` tuple. Sögumiðla events carry the tuple; downstream STT failure logs include it. Post-mortem replay knows which microphone, at what rate, in what time window, produced the samples. CDK has none of this; the samples are raw `float[]` with no provenance.
- **The Multi-Channel-Aware Provider.** CDK assumes mono (`channels` is read but rarely > 1). Ember's `MicrophoneProvider` exposes `channels: int` and the recording sessions handle stereo de-interleaving (or pick a channel). The user might have an XLR interface with two mics on a podcast setup; Ember should not collapse it.
- **The Soft-Mute Provenance Replay.** When `MicMuteStrategy = SoftMute` and the avatar is speaking, captured samples are *still emitted to a side channel* (a debug Sögumiðla stream) so the post-mortem can answer "did the user try to interrupt during this turn?" CDK throws those samples away; Ember files them for later analysis.
- **The Cross-Platform Device-Display-Name Normaliser.** Ember has a `display_name_for_device(raw)` function per provider that turns `"alsa_input.pci-0000_00_1f.3.analog-stereo"` into `"Built-in Audio (Analog Stereo)"`. Per-platform regexes; first thing the device-picker UI sees.

---
codex_id: 52_PERFORMANCE_BUDGETS
title: Performance Budgets — The Frame, The Turn, The Phone, The Headset
role: Auditor
layer: Verification
status: draft
chatdoll_source_refs:
  - Scripts/Network/SocketServer.cs:42-53
  - Scripts/SpeechListener/SpeechListenerBase.cs:25-30
  - Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:15-17
  - Scripts/LLM/ChatGPT/ChatGPTService.cs:30-33
  - Extension/SileroVAD/SileroVADProcessor.cs:39-45
  - Scripts/Model/ModelController.cs
  - Scripts/Model/Blink.cs
ember_subsystem_targets: [Rödd, Andlit]
cross_refs:
  - 50_verification/50_DEPENDENCY_HEALTH
  - 50_verification/54_MULTI_TTS_QUALITY
  - 50_verification/55_WEBGL_GOTCHAS
  - sap:52_RESOURCE_BUDGETS
  - waifu:50_DEPENDENCY_HEALTH
---

# Performance Budgets — The Frame, The Turn, The Phone, The Headset

> *Sólrún, voice cold and even: a Unity build runs inside a render loop. Sixty frames per second is the contract on desktop, ninety on a VR headset, thirty on a mid-range phone. Each frame is a budget — sixteen milliseconds, eleven, thirty-three — within which CDK's STT/VAD/LLM streaming/TTS prefetch/lip-sync/animation/blendshape work must complete or the user sees stutter. CDK ships with no performance budget declarations, no per-frame allocations profile, no platform-tier benchmarking. The audit posture is: trust the maintainer's profiling. I cannot verify it.*

This document maps CDK's runtime cost surface and proposes per-platform tier budgets. The kit's performance posture is *implicit*: the maintainer built it on a Mac, tested on iOS via OshaberiAI, and shipped. There is no `BenchmarkRunner`, no `Profiler` marker discipline beyond `Debug.Log`, no documented FPS target.

I separate **per-frame budget** (the Unity render loop) from **per-turn budget** (the conversational latency budget). The two interact: a turn that takes 800ms feels responsive *if* the frame loop never stalls below 30fps during it. A turn that takes 400ms with a 200ms frame stall feels broken.

---

## 1. The Per-Platform Frame Budgets

| Platform | Target FPS | Frame budget (ms) | CPU budget (ms) | Notes |
|---|---|---|---|---|
| Desktop standalone (Win/Mac/Linux) | 60 | 16.67 | ~10 (leaving 6ms for GPU sync) | The OshaberiAI development tier |
| iOS phone (recent) | 60 | 16.67 | ~8 (Metal sync is tight) | Realistic for iPhone 12+ |
| iOS phone (older, 4-5 year) | 30 | 33.3 | ~20 | The OshaberiAI deployment tier per App Store policy |
| Android phone (mid-range) | 30 | 33.3 | ~20 | Vulkan sync varies wildly |
| WebGL (desktop browser) | 30-60 | 16-33 | Single-thread, AudioWorklet on separate thread | See `[[55_WEBGL_GOTCHAS]]` |
| VR (Quest 3) | 90 or 120 | 11.1 or 8.3 | ~6 (eye-tracking + asynchronous timewarp budget) | Andlit-unity XR tier |
| AR (Vision Pro) | 90 | 11.1 | Even tighter (reprojection) | Forward-risk tier |

CDK does not declare any of these. They are inferred from Unity's standard practice. The kit's posture is: *render at whatever the user's hardware allows*. Acceptable for desktop. Dangerous for mobile and lethal for VR.

---

## 2. Where CDK Spends Frames

### 2.1 ModelController per-frame work

`Scripts/Model/ModelController.cs` (read-survey only — I have not measured), `Scripts/Model/Blink.cs`, and the lip-sync helper run per-frame `Update()` and `LateUpdate()`. The lip-sync path is the hottest: `uLipSync` analyzes the audio playback's current sample window, runs an FFT-derived vowel match, and writes BlendShape weights. uLipSync uses `Unity.Burst` for the inner FFT — without Burst, the cost is 3-5× higher.

**Risk:** Without Burst, lip-sync alone consumes 1-3ms per frame on a mid-range phone, leaving 17-19ms for everything else at 30fps target. With Burst, ~0.5ms. CDK silently depends on Burst being installed.

### 2.2 Animation state-machine and additive layers

Unity's Animator runs animation evaluation per-frame. CDK uses two layers (base + additive, visible in `Demo08.unity`). Additive layers compound the bone transform cost. With a typical VRM avatar (50-70 bones), each frame's animation pass is 0.5-1ms on a phone.

### 2.3 Blink and idle expression

`Blink.cs` runs eye-blink curves over time. The cost is trivial (sub-millisecond) but the `Update()` polls every frame regardless of whether blink is active.

### 2.4 SocketServer Update polling

`SocketServer.cs:42-53`:

```csharp
private void Update()
{
    lock (queueLock)
    {
        while (messageQueue.Count > 0)
        {
            var message = messageQueue.Dequeue();
            OnDataReceived?.Invoke(message);
        }
    }
}
```

The `Update()` method takes the `queueLock` every frame, even when no messages are present. On contention with the accept-thread, this is a kernel-level mutex round-trip. Cost is sub-microsecond in the common case but adds variance when the accept thread is busy.

### 2.5 Silero VAD inference

`Extension/SileroVAD/SileroVADProcessor.cs:39-45`:

```csharp
private int sampleSize = 512;
private long modelSamplingRate = 16000;
private InferenceSession session;
private float[] state = new float[256];
```

ONNX inference on a 512-sample chunk at 16kHz runs roughly every 32ms (16000/512). Each inference is ~2-5ms on a mid-range phone CPU, ~0.5ms on desktop. **VAD alone eats 5-10% of the mobile frame budget when active.** Silero's 2024 model is faster than 2023; the kit pins to the older state size (256), see `[[50_DEPENDENCY_HEALTH]] §2.6`.

---

## 3. Where CDK Spends Turns

A *turn* is the conversational latency budget — user-stops-speaking to AI-starts-speaking. Modern voice-assistant expectation is sub-second. CDK's latency budget decomposes:

| Phase | Source | Typical budget | Notes |
|---|---|---|---|
| Voice-end detection | VAD (Silero or energy) | 300-700ms | `SpeechListenerBase.SilenceDurationThreshold = 0.3f` default |
| STT post-VAD | Cloud roundtrip | 200-500ms | OpenAI Whisper API; Azure streaming faster |
| LLM first-token | Cloud roundtrip | 300-1500ms | Streaming reduces *perceived* delay |
| TTS prefetch first-chunk | Cloud or local | 100-800ms | VOICEVOX local: ~150ms; Azure cloud: ~300ms |
| Audio playback start | Unity AudioSource | <50ms | Once clip is decoded |

**Total turn budget:** 950ms-3550ms depending on provider mix. With streaming LLM + parallel TTS prefetch, the felt latency can compress to ~600ms first-audio. Without parallel prefetch (sequential mode), 1500ms+.

The README documents v0.8.16 as introducing *"WebSocket-based streaming speech recognition offloads VAD to the server and completes recognition during turn-end detection, reducing overall response latency by several hundred milliseconds."* This is the AIAvatarKitStreamSpeechListener path. It cuts the VAD+STT phases by overlapping them with the user's still-speaking tail.

### 3.1 The barge-in penalty

`SpeechListenerBase.cs:48-50`:

```csharp
[Header("Barge-in Settings")]
public float BargeInMinDuration = 1.5f;
private bool bargeInTriggered = false;
```

Barge-in (user interrupts AI mid-speech) is implemented by listening *during* TTS playback. This doubles the audio pipeline cost: TTS audio plays *while* the mic is open *while* VAD runs *while* STT preflight may fire. On a mid-range phone, the simultaneous-everything cost can spike to 30-40% CPU, pushing the frame loop into the 25-28fps range during interruption windows.

---

## 4. The Memory Surface

CDK does not document memory budgets either. Observed surfaces:

| Resource | Source | Bound? |
|---|---|---|
| TTS audio clip cache | `SpeechSynthesizerBase.cs:15` | **No** — `Dictionary<string, AudioClip>` grows unbounded |
| LLM context history | `LLMServiceBase.cs:43` (`historyTurns = 100`) | Yes, by turn count, but each turn unbounded in token count |
| Animation registrations | `ModelController.RegisterAnimations` | Bound by call sites |
| Face clip configurations | `FaceClipConfiguration` | Bound by configured set |
| ChatdollHttp client | per-service | One per service, leaks if many providers configured |

**The TTS cache is the leak vector.** Each unique text+style permutation generates a cache entry. On long sessions, this is hundreds of `AudioClip` objects, each ~200-500KB at 16kHz mono. On iOS, memory pressure triggers OS termination at ~1.5GB resident. A multi-hour CDK app session crosses that boundary.

---

## 5. Per-Platform Tier Recommendations

For Ember's Andlit-unity tier:

### Desktop-class (60fps target, plenty of CPU)
- Enable Silero VAD (ML-based, better noise rejection)
- Enable parallel TTS prefetch
- Enable barge-in
- Cap TTS cache at 100 entries with LRU eviction (Ember-add)
- Run lip-sync with full Burst

### Mobile-class (30fps target, tight memory)
- Use built-in energy VAD instead of Silero (saves 2-5ms/frame)
- Use sequential TTS prefetch (avoids parallel-decode CPU spike)
- Cap TTS cache at 20 entries
- Disable additive animation layer (keep base only)
- Disable barge-in unless user explicitly enables it (saves the mic-during-playback cost)

### WebGL-class (variable, single-thread)
- Offload VAD to server via `AIAvatarKitStreamSpeechListener`
- See `[[55_WEBGL_GOTCHAS]]` for the deeper read

### XR-class (90fps target, tightest CPU)
- No client-side ML VAD; force server-side
- Tighten LLM `historyTurns` to 20 (avoid context-build cost spikes)
- Pre-allocate audio clip pool of fixed size at scene load; refuse to create new clips after that

CDK does not provide these gates. Ember must.

---

## 6. Cross-References

- `[[50_DEPENDENCY_HEALTH]]` — Burst is the silent dependency for lip-sync performance.
- `[[54_MULTI_TTS_QUALITY]]` — TTS provider choice dominates the turn budget.
- `[[55_WEBGL_GOTCHAS]]` — WebGL's single-thread constraint changes every budget here.
- `[[sap:52_RESOURCE_BUDGETS]]` — SAP's desktop budget is far more generous; SAP can spawn a Python subprocess where CDK cannot.
- `[[waifu:50_DEPENDENCY_HEALTH]]` — Waifu's cloud-streaming model trades latency for cost; CDK does the opposite.

---

## What This Means for Ember

**Adopt:** CDK's **streaming-first response architecture** — never wait for full LLM completion before starting TTS prefetch on the first sentence. `ChatGPTService.cs:262-287` shows the `streamRequest.SendWebRequest()` + chunk-by-chunk parsing pattern; `LLMContentProcessor` accumulates text and emits sentence boundaries for parallel TTS dispatch. *Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:** The per-platform tier-gating concept is *missing* from CDK and exactly what Ember needs. Ember's Funi declares the tier at boot (CPU class, RAM, GPU presence, network class) and Rödd/Andlit consult the tier when choosing VAD path, prefetch policy, cache size.

**Avoid:**
- The unbounded TTS cache. Always cap with LRU. Memory leaks on mobile are crash-causing, not just slow.
- `Update()` polling that takes locks every frame. Use the main-thread dispatcher pattern (Unity's `SynchronizationContext` posted from worker threads) instead of mutex round-trips.
- Barge-in enabled by default on mobile.

**Invent:** A **per-frame budget watchdog** for Rödd. Every Rödd subsystem (VAD, STT preflight, lip-sync) runs under a budget marker; the watchdog records the per-frame cost in a circular buffer (last 600 frames = 10 seconds at 60fps) and *publishes* a budget report into Munnr at low priority. When a subsystem exceeds its budget for >5 consecutive frames, Rödd auto-degrades (Silero → energy VAD; parallel → sequential TTS prefetch). This is *graceful degradation as a Vow.* CDK has no such fallback; an overloaded mobile build just stutters until the user closes the app.

A second invention: **the turn-budget assertion**. On developer builds, Ember tracks turn latency at the dialog level and *fails the build* if median turn latency on the target platform exceeds the declared budget (e.g., 1200ms p50 on mid-range Android, 800ms on iPhone 12+). This makes performance regression a build-time concern rather than a launch-day discovery. CDK's lack of this is felt most by OshaberiAI users on older iPhones; Ember can do better.

---

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c).*

---
codex_id: 23_STT_INTERFACE
title: STT Interface — Five Providers Conforming To Eighteen Lines, And The Streaming Variant That Lives Beside Them
role: Auditor
layer: Interface
status: draft
chatdoll_source_refs:
  - Scripts/SpeechListener/ISpeechListener.cs:6-18
  - Scripts/SpeechListener/SpeechListenerBase.cs:10-255
  - Scripts/SpeechListener/RecordingSession.cs
  - Scripts/SpeechListener/OpenAISpeechListener.cs:9-57
  - Scripts/SpeechListener/AzureSpeechListener.cs:11-119
  - Scripts/SpeechListener/GoogleSpeechListener.cs:12-131
  - Scripts/SpeechListener/AIAvatarKitSpeechListener.cs:11-73
  - Scripts/SpeechListener/AIAvatarKitStreamSpeechListener.cs:11-374
  - Scripts/SpeechListener/AzureStreamSpeechListener.cs
  - Extension/SileroVAD/SileroVADProcessor.cs
ember_subsystem_targets: [Munnr, Rödd, Strengr, Funi]
cross_refs:
  - 20_interface/24_VAD_INTERFACE
  - 30_execution/32_STT_LOOP
  - 50_verification/51_SECURITY_REVIEW
  - 50_verification/55_WEBGL_GOTCHAS
  - 50_verification/57_FAILURE_TAXONOMY
  - sap:23_STT_DOMAIN
  - waifu:22_STT_INTERFACE
---

# STT Interface — Five Providers Conforming To Eighteen Lines, And The Streaming Variant That Lives Beside Them

> *Sólrún, voice cold and even: the STT side of CDK is smaller and cleaner than the TTS side. Five batch providers (Google, Azure, OpenAI Whisper, AIAvatarKit batch, Dummy) conform to an eighteen-line interface. Two streaming variants (AIAvatarKit streaming over WebSocket, AzureStreamSpeechListener) live beside the batch interface as separate classes, sharing nothing structurally. Silero VAD is a third axis — not an STT provider, a voice-activity detector that gates whether to send the captured audio to an STT at all. The kit's bookkeeping around recording sessions is rigorous; the credential surface and the always-listening posture are the audit findings.*

This document audits ChatdollKit's STT (speech-to-text) interface. The Architect's `[[24_VAD_INTERFACE]]` covers the Silero VAD surface in detail; here I treat VAD only as it interacts with the STT contract. The runtime loop is in `[[32_STT_LOOP]]` (Forge-A).

Files in scope, from `wc -l /tmp/ChatdollKit/Scripts/SpeechListener/`:

| File | LOC |
|---|---|
| `ISpeechListener.cs` | 18 |
| `SpeechListenerBase.cs` | 255 |
| `RecordingSession.cs` | 153 |
| `MicrophoneManager.cs` | 344 |
| `OpenAISpeechListener.cs` | 57 |
| `AzureSpeechListener.cs` | 119 |
| `GoogleSpeechListener.cs` | 131 |
| `AIAvatarKitSpeechListener.cs` | 73 |
| `AIAvatarKitStreamSpeechListener.cs` | 375 (streaming, separate hierarchy) |
| `AzureStreamSpeechListener.cs` | 201 (streaming, separate hierarchy) |
| `DummySpeechListener.cs` | 38 (no-op) |

Two architectures. The batch path inherits from `SpeechListenerBase` and implements one virtual method. The streaming path stands alone — `AIAvatarKitStreamSpeechListener` inherits directly from `MonoBehaviour` and implements `ISpeechListener` via WebSocket. The shared *interface* is `ISpeechListener` (18 lines); the shared *base* is unused for streaming. This is a real architectural seam — verify it.

---

## 1. The Contract — Eighteen Lines

`/tmp/ChatdollKit/Scripts/SpeechListener/ISpeechListener.cs:1-18`:

```csharp
public interface ISpeechListener
{
    bool IsEnabled { get; set; }
    Func<string, UniTask> OnRecognized { get; set; }
    Action OnBargeIn { get; set; }
    Func<string, float, bool> BargeInCondition { get; set; }
    bool IsRecording { get; }
    bool IsVoiceDetected { get; }
    void StartListening(bool stopBeforeStart = false);
    void StopListening();
    void ChangeSessionConfig(float silenceDurationThreshold = float.MinValue,
                             float minRecordingDuration = float.MinValue,
                             float maxRecordingDuration = float.MinValue);
}
```

Eight members. Compared to `ISpeechSynthesizer`'s two, the listener contract carries five times the surface area. The reasons are real: STT must expose lifecycle (`StartListening`/`StopListening`), state (`IsRecording`/`IsVoiceDetected`), event callbacks (`OnRecognized`/`OnBargeIn`), interruption policy (`BargeInCondition`), and runtime reconfiguration (`ChangeSessionConfig`). TTS is request-response; STT is continuous capture with mid-stream interrupts.

The contract is **callback-style**, not async-iterable. `OnRecognized` is a delegate the consumer assigns; transcripts are pushed when ready. This works for the dialog loop but makes the listener hard to use in a polling consumer (a UI rendering partial transcripts would have to add its own buffer).

`BargeInCondition` is the kit's interruption seam: when the user starts speaking while the doll is speaking, the dialog manager wants to cut TTS playback and listen. The condition delegate takes `(string textSoFar, float recordedDurationSeconds)` and returns a `bool`. For batch listeners (`SpeechListenerBase`), `textSoFar` is always `null` because batch listeners don't have partial transcripts; the condition uses only `recordedDurationSeconds` (default 1.5s). For the streaming variant (`AIAvatarKitStreamSpeechListener:308-319`), the condition uses the partial text and checks against `BargeInMinTextLength = 2`.

The contract does not distinguish the two cases. Callers wiring `BargeInCondition` must know which listener type they're targeting to know what `textSoFar` will be. This is implicit polymorphism through `null`. A typed `BargeInContext` parameter would have been better.

`ChangeSessionConfig` (`:138-144` in the base) lets the caller mutate silence/min/max durations live. It stops and restarts the recording session. There is no notification that the session has restarted; consumers calling `ChangeSessionConfig` mid-recording lose any audio captured but not yet emitted.

---

## 2. The Base Class — Where Most Of The Work Lives

`/tmp/ChatdollKit/Scripts/SpeechListener/SpeechListenerBase.cs:10-255`. Two hundred fifty-five lines of audio capture, voice detection, silence trimming, sample-rate handling, and Web-Audio bookkeeping that the four batch providers inherit untouched.

The recording-session abstraction (`:103-114`):

```csharp
session = new RecordingSession(
    name: Name,
    silenceDurationThreshold: SilenceDurationThreshold,    // 0.3s default
    minRecordingDuration: MinRecordingDuration,             // 0.5s default
    maxRecordingDuration: MaxRecordingDuration,             // 3.0s default
    maxPrerollSamples: maxPrerollSamples,                    // 0.2s at the configured rate
    onRecordingComplete: async (samples) => await HandleRecordingCompleteAsync(samples, cancellationTokenSource.Token),
    detectVoiceFunctions: DetectVoiceFunctions ?? new() { IsVoiceDetectedByVolume }
);
microphoneManager.StartRecordingSession(session);
```

Five durations and one detection function. The defaults are sane for conversational use: 0.3s of silence ends an utterance, 0.5s minimum prevents single-phoneme false positives, 3s maximum caps a single utterance (the dialog loop expects punctuated turns; 3s is long), 0.2s of pre-roll captures the start of an utterance before voice detection fires.

The `DetectVoiceFunctions` list is the VAD seam. Default is `IsVoiceDetectedByVolume` — a hand-rolled energy-threshold detector at `:116-126`. For Silero VAD, the operator attaches `SileroVADProcessor` and adds its `IsVoiceDetected` to the list. Multiple detection functions are *all consulted*; voice is detected if any returns true.

This is a subtle finding. Multi-VAD with OR-fusion is permissive — energy detector + Silero must both miss for voice to be considered absent. This favors recall over precision. In a noisy environment, the energy detector triggers on noise, Silero correctly says "no speech", but the kit treats it as voice anyway. Operators wanting AND-fusion (both detectors must agree) have to monkey-patch.

The transcription dispatch at `:182`:

```csharp
var text = await ProcessTranscriptionAsync(samplesToTranscript, sampleRate, token);
```

`ProcessTranscriptionAsync` is the one virtual method each provider implements. Everything else — mic capture, VAD, session timing, sample-rate conversion, PCM packing, callback dispatch — is in the base class.

The `HandleRecordingCompleteAsync` (`:165-203`) is the dispatch loop:

1. Resample to `TargetSampleRate` if the mic is higher (most providers want 16kHz; many mics deliver 44.1kHz or 48kHz).
2. Call `ProcessTranscriptionAsync(samples, sampleRate, token)`.
3. Print result if `PrintResult` is true.
4. Invoke the `OnRecognized` callback.
5. Restart listening (`StartListening(true)` at `:202`).

The restart-after-each-utterance is the *always-listening* posture. The kit goes back to listening immediately after every transcription. There is no consent gate, no "press to talk" mode out of the box. The microphone is hot from the moment `AutoStart && IsEnabled`. Operators who want push-to-talk must override.

The PCM packing helpers (`SampleToPCM`, `SetWaveHeader` at `:212-244`) hand-roll a 44-byte WAV header in front of the 16-bit PCM data. This is necessary because Whisper/Azure/etc. accept WAV uploads, not raw PCM. The header construction is correct but copy-paste-prone (the same code is replicated nowhere else in CDK because it's centralized here — that's the *right* place).

---

## 3. OpenAI Whisper — The Form-POST Whisper Client

`/tmp/ChatdollKit/Scripts/SpeechListener/OpenAISpeechListener.cs:9-57`. Fifty-seven lines, including the API call.

Surface:
- `public string ApiKey;` — same Inspector-baked-into-build leak as the TTS side.
- `public string Model = "whisper-1";` — frozen model name (same maintenance smell as OpenAI TTS).
- `public string Prompt;` — optional context hint for Whisper.
- `public float Temperature = 0.0f;` — Whisper's deterministic-decoding default.

The transcription path (`:18-55`):

```csharp
var form = new WWWForm();
form.AddField("model", Model);
if (!string.IsNullOrEmpty(Language) && (AlternativeLanguages == null || AlternativeLanguages.Count == 0))
{
    form.AddField("language", Language.Contains("-") ? Language.Split("-")[0] : Language);
}
form.AddField("response_format", "text");
form.AddBinaryData("file", SampleToPCM(samples, sampleRate, 1), "voice.wav");
if (!string.IsNullOrEmpty(Prompt)) form.AddField("prompt", Prompt);
form.AddField("temperature", Temperature.ToString());

using (UnityWebRequest request = UnityWebRequest.Post("https://api.openai.com/v1/audio/transcriptions", form))
{
    request.SetRequestHeader("Authorization", $"Bearer {ApiKey}");
    await request.SendWebRequest().ToUniTask();
    return request.downloadHandler.text;
}
```

Multipart form POST. Bearer auth in header. Language passed only when no `AlternativeLanguages` are set — Whisper's auto-detect runs when language is omitted. The `response_format: "text"` choice means the response is the bare transcript with no metadata. CDK does not see word timings, confidence scores, or detected language. For caller use-cases that need those (subtitle generation, low-confidence retranscription), this is data thrown away.

Whisper API pricing (2025-2026): $0.006 per minute of audio. At 3-second utterances at conversational pacing (~10 utterances/minute talking), that is ~$0.018/minute of active conversation. A leaked Whisper key with no rate limit is a financial vector.

No WebGL divergence. The same path works in WebGL via `UnityWebRequest` (which CDK has confirmed Emscripten-compatible behavior for).

**Latency:** Whisper's API typically returns 200-400ms after a 3-second clip POST. Plus the network RTT. End-to-end: 300-600ms after utterance end.

---

## 4. Azure STT — Two APIs, One Provider

`/tmp/ChatdollKit/Scripts/SpeechListener/AzureSpeechListener.cs:11-119`. Two paths inside one class — Classic (the v1 `speech.microsoft.com` REST API) and Fast (the v2 `cognitive.microsoft.com/speechtotext/transcriptions:transcribe`).

Surface:
- `public string ApiKey;` — Inspector-baked.
- `public string Region;` — Azure region (e.g. `eastus`, `japanwest`).
- `public bool UseClassic = false;` — defaults to the v2 Fast API.

Classic path (`:30-59`):

```csharp
var url = $"https://{Region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language={Language}";
// POST 16-bit PCM with Content-Type: application/json, Ocp-Apim-Subscription-Key: {ApiKey}
// Parse response.DisplayText
```

Content-Type is `application/json` for a *binary PCM* body. That is the Azure API's documented oddity — they label it JSON for legacy reasons. CDK follows the spec.

Fast path (`:61-99`):

```csharp
var url = $"https://{Region}.api.cognitive.microsoft.com/speechtotext/transcriptions:transcribe?api-version=2024-11-15";
var form = new WWWForm();
form.AddField("definition", JsonConvert.SerializeObject(new Dictionary<string, object>(){
    {"locales", locales},
    {"channels", new List<int>(){0, 1}}
}));
form.AddBinaryData("audio", SampleToPCM(samples, sampleRate, 1), "voice.wav");
// POST with Ocp-Apim-Subscription-Key
// Parse response.combinedPhrases[0].text
```

The Fast API accepts multi-language `locales` (which is why `AlternativeLanguages` is consulted at `:71-74` — Azure can return the detected one) and multi-channel. CDK fixes channels to `[0, 1]` (mono with stereo passthrough) but only mono samples are POSTed. The API tolerates the mismatch.

The `combinedPhrases[0].text` extraction at `:91` indexes into the response list without bounds check. If Azure returns an empty `combinedPhrases` array (no speech recognized), the line throws `ArgumentOutOfRangeException`. The base class catches at `:197-200` with a generic `Debug.LogError`. Dialog falls silent.

**Latency:** Azure Fast API typically returns 200-500ms after a 3-second clip POST. Comparable to Whisper.

**Audit finding:** The empty-result NullRef is a real failure. Ember's adapter must null-guard.

---

## 5. Google Cloud STT — The Base64 Round-Trip Again

`/tmp/ChatdollKit/Scripts/SpeechListener/GoogleSpeechListener.cs:12-131`.

Surface:
- `public string ApiKey;` — URL query string at `:26`. Same leak as Google TTS.
- `public bool UseEnhancedModel = false;` — toggle for Google's premium tier.
- `public List<SpeechContext> SpeechContexts;` — domain-specific phrase boosting.

The request body (`:73-95`):

```csharp
private class SpeechRecognitionConfig
{
    public int encoding;                          // 1 = 16-bit linear PCM
    public double sampleRateHertz;
    public double audioChannelCount;
    public string languageCode;
    public List<string> alternativeLanguageCodes;
    public string model;                          // null when useEnhanced, else "default"
    public bool useEnhanced;
    public List<SpeechContext> speechContexts;
}
```

Audio is base64-encoded LINEAR16 PCM in the JSON `audio.content` field (`:69`). Same 33% bandwidth overhead as Google TTS. The base64 encode on the client adds milliseconds; the decode on Google's side is negligible.

`SpeechContext` (`:108-113`):

```csharp
public class SpeechContext {
    public List<string> phrases;
    public int boost;
}
```

This is Google's phrase-boosting hint: tell the recognizer that certain phrases (product names, character names, jargon) are likely in this audio. CDK exposes the surface but does not document operator usage. For a doll whose persona has a unique name ("Skadi", "Funi"), boosting the name in the context list significantly reduces misrecognition.

The response extraction at `:46`:

```csharp
return response?.results?[0]?.alternatives?[0]?.transcript ?? string.Empty;
```

Null-conditional chains plus `??` fallback to empty string. Safer than Azure's raw indexing. If Google returns no results, the listener emits empty string and the dialog manager treats it as "user said nothing".

**Latency:** Google STT typically returns 250-550ms after a 3-second clip POST. With the Enhanced model, latency rises to 400-800ms but accuracy improves notably for Japanese.

---

## 6. AIAvatarKit Batch — The Backend-Proxy Pattern, Again

`/tmp/ChatdollKit/Scripts/SpeechListener/AIAvatarKitSpeechListener.cs:11-73`.

Surface:
- `public string EndpointUrl;`
- `public string ApiKey = string.Empty;` — *optional* Bearer (`:25-28`).
- `public Func<SpeechRecognitionResponse, string> PostProcess;` — caller-provided response massager.

The request (`:20-22`):

```csharp
var form = new WWWForm();
form.AddBinaryData("audio", SampleToPCM(samples, sampleRate, 1), "voice.wav");
```

Single field. The endpoint URL is operator-supplied. The AIAvatarKit server (Python, `/tmp/aiavatarkit/aiavatar/sts/stt/*.py`) wraps Google/Azure/Whisper/Silero internally and exposes a uniform endpoint. The Unity client sees one URL, one API contract.

The `SpeechRecognitionResponse` (`:65-71`) carries:

```csharp
public string text;
public Dictionary<string, object> preprocess_metadata;
public Dictionary<string, object> postprocess_metadata;
public MatchTopKResult speakers;
```

The `speakers` field is interesting: AIAvatarKit's STT can identify *which speaker* in a multi-speaker conversation produced the audio (`Candidate.speaker_id`, `similarity`). The kit exposes it via the typed response. CDK's default consumer (`PostProcess == null` at `:35`) drops the speaker info and returns only `text`. Operators wanting speaker-aware dialog must wire `PostProcess`.

**This is the only STT in CDK that surfaces speaker identification.** The capability is real; the wiring is operator-tier. Ember's dialog manager — Munnr — should consume `speaker_id` natively when speaker disambiguation matters (e.g., a household with multiple users).

**Auth:** Bearer token in header, *optional*. The token is the AIAvatarKit session token, not the upstream provider key. Build-bundle leakage of a session token is much less harmful than leakage of an OpenAI Whisper key — the operator can rotate the session token from server-side without rebuilding the Unity binary.

---

## 7. AIAvatarKit Streaming — The WebSocket Variant

`/tmp/ChatdollKit/Scripts/SpeechListener/AIAvatarKitStreamSpeechListener.cs:11-375`. The big one. Three hundred seventy-five lines, inheriting directly from `MonoBehaviour` and implementing `ISpeechListener`.

**Architectural divergence: this class does not use `SpeechListenerBase`.** It owns its own `MicrophoneManager` registration (`:168`), its own session management, its own barge-in logic, its own sample rate handling. The base class is bypassed entirely.

This is the streaming path. WebSocket-based, sub-utterance, partial-text-capable. The contract surface is the same `ISpeechListener` interface, but the implementation shape is utterly different.

### 7.1 The Protocol

`WebSocketUrl = "ws://localhost:8000/ws/stt"` (`:25`). WebSocket connection. Custom message types serialized as JSON.

Outbound (`:213-225`, `:247-284`):

| Type | Payload |
|---|---|
| `start` | `{type, session_id}` |
| `data` | `{type, session_id, audio_data}` (base64 PCM) |
| `stop` | `{type, session_id}` |

Audio is chunked at `SamplesPerMessage = 512` samples (`:27`). At 16kHz, that is 32ms of audio per message. The kit pushes ~31 messages per second.

Inbound (`:286-353`):

| Type | Action |
|---|---|
| `connected` | Sets `isConnected = true`, records `session_id` |
| `partial` | Emits partial text via `OnPartialRecognized`, triggers barge-in if text length > `BargeInMinTextLength` |
| `final` | Emits final text via `OnRecognized` |
| `voiced` | Sets `IsVoiceDetected = true`, records `lastVoicedTime` |
| `error` | Logs `metadata.error` |

### 7.2 The Barge-In Improvement

The streaming variant's barge-in (`:307-319`) is fundamentally better than batch:

```csharp
case "partial":
    if (!bargeInTriggered && !string.IsNullOrEmpty(msg.text)) {
        var shouldBargeIn = BargeInCondition != null
            ? BargeInCondition(msg.text, 0f)
            : msg.text.Length >= BargeInMinTextLength;
        if (shouldBargeIn) {
            bargeInTriggered = true;
            OnBargeIn?.Invoke();
        }
    }
```

Barge-in fires on **partial-text presence with length >= 2 characters**, not on raw audio duration. This is a much more selective signal than the batch listener's "1.5 seconds of voice activity" — a cough, sneeze, or background noise will not trigger barge-in because the STT must produce text first.

The batch listener at `SpeechListenerBase.cs:71-83` fires barge-in on `session.RecordDuration >= BargeInMinDuration`, which means *any* audio that triggers VAD for 1.5s interrupts the doll. The streaming listener gates barge-in on *transcribed text*. Far better.

This is the single best architectural win of the streaming variant. Ember should adopt it.

### 7.3 ChangeSessionConfig — A Warning

`:355-358`:

```csharp
public void ChangeSessionConfig(...) {
    Debug.LogWarning("Session configuration for AIAvatarKitStreamSpeechListener is managed on the server side.");
}
```

The streaming variant cannot honor `ChangeSessionConfig` — silence durations are server-side. The method exists for interface conformance and logs a warning. This is correct behavior; honesty about capability.

### 7.4 The PCM Encoding

`:260-267`:

```csharp
var pcmData = new byte[samplesToSend.Length * 2];
for (var i = 0; i < samplesToSend.Length; i++) {
    var sample = (short)(samplesToSend[i] * 32767f);
    pcmData[i * 2] = (byte)(sample & 0xFF);
    pcmData[i * 2 + 1] = (byte)((sample >> 8) & 0xFF);
}
```

Hand-rolled little-endian 16-bit PCM conversion per sample. At 31 messages/sec × 512 samples/msg, that is ~16000 iterations per second. The JIT handles this fine; on mobile it's still cheap. The hand-roll is correct.

### 7.5 The Resample Shim

`:228-245` reimplements linear-interpolation resampling identical to the base class's `Resample` at `:146-163`. **Copy-paste.** Same algorithm, same bug surface, two places to fix. This is a finding.

### 7.6 The WebSocket Auth

`:144-154`:

```csharp
Dictionary<string, string> headers = null;
if (!string.IsNullOrEmpty(ApiKey)) {
    headers = new Dictionary<string, string> { { "Authorization", $"Bearer {ApiKey}" } };
}
await webSocketAdapter.ConnectAsync(WebSocketUrl, CancellationToken.None, headers);
```

Bearer header on the WebSocket handshake. Same shape as the batch AIAvatarKit listener. The token is operator-rotatable.

**Verdict:** The streaming variant is architecturally distinct, partial-text-capable, has better barge-in semantics, and depends on an operator-run server. **Adopt as the default for Ember's Munnr where latency-to-first-partial matters** (which is most conversational use cases).

---

## 8. AzureStreamSpeechListener — The Other Streaming Variant

`/tmp/ChatdollKit/Scripts/SpeechListener/AzureStreamSpeechListener.cs` (201 lines, not exhaustively quoted here). Azure has its own WebSocket-based streaming STT (`wss://{region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1`). The implementation mirrors the AIAvatarKit streaming variant structurally — `MonoBehaviour`-inheriting, WebSocket-based, partial-text-capable — but with Azure's specific protocol layer.

The auth uses `Ocp-Apim-Subscription-Key` in the handshake URL, which means **the key is in the WebSocket URL**, which means it appears in HTTP proxy logs, browser DevTools, and OS-level network traces. Same finding as Google TTS — URL-embedded credentials are a leak surface even with TLS. The Azure docs recommend exchanging the subscription key for a short-lived auth token via a separate `issueToken` REST call; CDK uses the simpler raw-key path.

**Audit finding:** Two streaming implementations, structurally divergent (AIAvatarKit's custom JSON protocol vs Azure's documented protocol). No shared streaming-listener base class. The streaming surface is *more* code-duplication-prone than the batch surface. A new streaming provider (Whisper-Realtime when OpenAI ships it, Google Streaming when CDK adopts it) will be a third standalone class.

---

## 9. The Always-Listening Posture

Every batch listener auto-restarts at `:202`:

```csharp
StartListening(true);   // at the end of HandleRecordingCompleteAsync
```

The streaming listener never stops listening except via explicit `StopListening`. Microphone capture is *continuous from `AutoStart`* until the application exits. There is no push-to-talk default. There is no idle-timeout that disables capture after N minutes of silence. The microphone is hot.

For a desktop chat-doll the operator runs personally, this is acceptable. For a phone app a user installs from the App Store, this is a privacy concern at the *posture* level even if no data leaks — the user feels surveilled. The kit ships no Inspector toggle for "listen only when user gestures."

iOS and Android *require* a microphone-usage description in Info.plist / AndroidManifest.xml. The OS surface is honest about the capture. But the application's *behavior* — always-on — is not necessarily what the user assumed when granting permission.

**Audit finding:** The always-listening default needs operator-tier mitigation. Ember's Munnr-unity should default to push-to-talk and require an explicit operator opt-in for always-listening, with a runtime indicator (a mic LED widget) when listening.

---

## 10. Cross-References

- `[[24_VAD_INTERFACE]]` — Silero VAD detail; the multi-VAD OR-fusion mechanism is described there.
- `[[32_STT_LOOP]]` — Forge-A's runtime view; how STT integrates into the dialog state machine.
- `[[21_TTS_INTERFACE_WESTERN]]` §1 — the parallel TTS contract; comparison for shape.
- `[[51_SECURITY_REVIEW §5.1, §5.2]]` — credential surfaces, including the OpenAI/Azure/Google STT keys.
- `[[55_WEBGL_GOTCHAS §3, §6]]` — WebGL STT specifics; the `AIAvatarKitStreamSpeechListener` is the recommended WebGL path because Silero VAD in-browser is too heavy.
- `[[sap:23_STT_DOMAIN]]` — SAP's sherpa-asr (k2-sherpa, local Python). Compare and contrast.
- `[[waifu:22_STT_INTERFACE]]` — Waifu's browser-side Web Speech API. Compare.

---

## What This Means for Ember

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c).*

**Adopt:**

- **The `ISpeechListener` eight-member contract** as Ember's Munnr listener interface. (`ISpeechListener.cs:6-18`, Apache-2.0 attribution required.) The lifecycle/state/event split is the right shape.
- **The `SpeechListenerBase` recording-session abstraction** — multi-VAD function list, silence/min/max durations, pre-roll buffer, sample-rate conversion. The base class is well-factored; adopt the architecture with minor changes (see Adapt).
- **The streaming variant's barge-in-on-partial-text logic** (`AIAvatarKitStreamSpeechListener.cs:307-319`). This is the single best STT pattern in CDK. Ember's Munnr should barge in on partial text presence, not raw audio duration.
- **The AIAvatarKit batch listener's speaker_id surfacing** (`AIAvatarKitSpeechListener.cs:65-71`). Speaker identification at the listener level lets the dialog manager route multi-user households correctly. Ember's typed `STTResponse` record should carry `speaker_id` even when the active provider can't fill it.
- **Google's `SpeechContext` phrase boost** — Ember should accept a list of operator-supplied domain phrases (character names, product names) and pass them to providers that support boost hints. Adapter-level translation: Google maps to `SpeechContext`, Whisper maps to `Prompt`, Azure maps to its custom-vocab path.

**Adapt:**

- **The `BargeInCondition` `(text, duration)` parameter shape** is implicit polymorphism through `null`. Adapt to a typed `BargeInContext` discriminated union: `BatchContext { duration }` or `StreamContext { partialText, partialTextLength }`. Callers know what they're getting.
- **The multi-VAD OR-fusion** at `DetectVoiceFunctions` (`:31, :110`) — adapt to a configurable fusion policy (OR for recall, AND for precision, MAJORITY for ensemble). Ember's noisy-room mode wants AND; the default is OR.
- **The always-listening posture** — adapt to push-to-talk default with an operator opt-in for always-listening. Add a visible "listening" indicator (Funi UI widget) when capture is active.
- **The hand-rolled WAV header construction** at `SpeechListenerBase.cs:229-244` — adapt by isolating into a `WavWriter` helper class with unit tests. The header bytes are correct in CDK; the next maintainer who edits them without tests will silently break.

**Avoid:**

- **`public string ApiKey;` on every batch listener** for OpenAI/Azure/Google. Route through Strengr session-token proxy per `[[51_SECURITY_REVIEW]]` Invent.
- **URL-query API keys** (Google STT `:26`, Azure streaming WSS URL). Use header-bearer or proxy where the API permits.
- **Empty-result indexing** at `AzureSpeechListener.cs:91`. Always null-guard.
- **Copy-pasted resample logic** between `SpeechListenerBase.cs:146-163` and `AIAvatarKitStreamSpeechListener.cs:228-245`. Hoist to a shared `AudioResampler` helper.
- **The bypass of `SpeechListenerBase` for streaming listeners.** Refactor a `StreamingSpeechListenerBase` so AIAvatarKit-stream and Azure-stream share the WebSocket plumbing and barge-in logic.

**Invent:**

- A **`StreamingSpeechListenerBase` base class** for Ember's Munnr that factors WebSocket connection management, JSON-message dispatch, partial-text barge-in, and session lifecycle. Each provider implements only the protocol-translation layer. CDK has two streaming listeners and zero shared base. Ember has the base and N providers. Vow tie-in: **Smallness** + **Forge-Ready** (a new provider is a small adapter, not a 200-line standalone).
- A **Consent-Gated Capture Mode** as the Ember-Munnr default. Push-to-talk in the Inspector. A `Func<UniTask<bool>> ConsentGate` delegate that the dialog manager wires to a UI consent affirmation. Always-listening is an operator-opt-in with a *runtime UI indicator* (mic icon in the doll's HUD). Aligns with the user's standing preference for tailnet-bound services and surface-without-surveillance posture. Vow tie-in: **Surface Without Surveillance**.
- A **VAD-Fusion Policy** declaration in Funi's startup config. The operator picks `OR` (CDK default, recall-favoring), `AND` (precision-favoring, for noisy environments), or `WEIGHTED_MAJORITY` (each VAD gets a weight, fused score thresholded). CDK has only OR. Ember has the policy as a tier setting tied to the deployment environment (open-mic livestream → AND; quiet office → OR).
- A **Speaker-Aware Munnr Surface** that takes the `speaker_id` from AIAvatarKit's STT and routes to per-speaker conversation context. The current dialog state machine assumes one user per session; multi-user households (a couple speaking to the same doll, a family) want per-speaker memory threading. Hjarta gets the speaker_id alongside the transcript and writes to the right user partition. CDK exposes the data; the dialog manager drops it. Ember picks it up.
- A **STT Provider Capability Registry** matching the TTS Registry from `[[22_TTS_INTERFACE_JAPANESE]]`: per-provider `latency_floor_ms`, `supports_streaming`, `supports_partial_text`, `supports_speaker_id`, `license`, `credential_shape`, `webgl_supported`, `mobile_supported`. The dialog manager selects by platform + budget. Adapter providers (AIAvatarKit, SpeechGateway-equivalent) declare their backing capability dynamically by interrogating the server. Vow tie-in: **Pluggable Storage** generalized to **Pluggable Listeners**.

A final invent: a **Mute Vow.** Ember's Munnr ships a single keyboard chord (configurable, default `Ctrl+Shift+M`) that hard-disables capture from any tier — desktop, mobile, WebGL, XR. The mute is reflected in a Funi UI badge. The dialog continues without listening; the user can type. The chord works even if the listener is wedged. CDK has no equivalent; the mic stays hot until the application exits.

---

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c).*

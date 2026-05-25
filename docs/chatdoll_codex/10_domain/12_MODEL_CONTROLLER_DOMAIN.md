---
codex_id: 12_MODEL_CONTROLLER_DOMAIN
title: Model Controller Domain — The Animation Queue, the Face Queue, and the Voice Coupler
role: Architect
layer: Domain
status: draft
chatdoll_source_refs:
  - Scripts/Model/ModelController.cs:1-464
  - Scripts/Model/SpeechController.cs:1-212
  - Scripts/Model/FaceController.cs:1-73
  - Scripts/Model/Animation.cs:1-24
  - Scripts/Model/AnimatedVoice.cs:1-34
  - Scripts/Model/AnimatedVoiceRequest.cs:1-55
  - Scripts/Model/Voice.cs:1-83
  - Scripts/Model/FaceExpression.cs:1-17
  - Scripts/Model/Blink.cs:1-198
  - Scripts/Model/uLipSyncHelper.cs:1-107
  - Scripts/Model/ConfigurableLipSyncHelper.cs:1-109
  - Scripts/Model/VRCFaceExpressionProxy.cs:1-144
  - Scripts/Model/ModelRequestBroker.cs:1-193
  - Extension/VRM/VRMBlink.cs:1-119
  - Extension/VRM/VRMFaceExpressionProxy.cs:1-94
  - Extension/VRM/VRMuLipSyncHelper.cs:1-27
ember_subsystem_targets: [Munnr, Hjarta]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_AIAVATAR_DOMAIN
  - 10_domain/15_SPEECH_SYNTHESIZER_DOMAIN
  - 10_domain/1B_ANIMATION_DOMAIN
  - 20_interface/25_ANIMATION_TAG_PROTOCOL
  - 20_interface/29_VRM_INTERFACE
  - sap:11_AVATAR_DOMAIN
  - waifu:20_ZEROWEIGHT_SURFACE
---

# Model Controller Domain
## The Animation Queue, the Face Queue, and the Voice Coupler

*— Rúnhild Svartdóttir, Architect*

> *A body is a coordination problem dressed up as an aesthetic one. ModelController is the rare module that admits this — and solves it by making the coordination its only job.*

The `Model/` folder is fourteen files and roughly **1,500 LOC of coordinated avatar embodiment**. It owns three independent queues — animation, face expression, and voice — plus the per-frame discipline that runs them in parallel without drifting. It is the *cleanest* subsystem in ChatdollKit and the one that most directly teaches Ember how to think about Munnr (the mouth) and the part of Hjarta (the heart) that surfaces as expression.

This doc maps what each file owns, how the three queues stay in sync, where the implementation leaks, and what survives translation to Ember's tier ladder.

---

## 1. The Subject Itself

**What the domain is:** the *visible body* layer of CDK. The LLM, the dialog state machine, and the STT pipeline all sit *above* this domain; the Unity engine sits below. In between, ModelController and its peers run three loops per frame:

- **The animation loop** (`ModelController.Update` → `UpdateAnimation`, lines 97-100, 313-341) — picks the next animation from a queue (or generates an idle), drives Unity's `Animator` parameter values.
- **The face loop** (`FaceController.Update` → `UpdateFace`, lines 16-19, 35-55) — picks the next face from a queue (or holds the current one until duration expires), drives an `IFaceExpressionProxy` impl that talks to the avatar's blend shapes.
- **The voice loop** (`SpeechController.Say` + `StartVoicePrefetchTask`, lines 38-169 + 180-204) — pulls voices from a prefetch queue, downloads audio via the active TTS, plays via `AudioSource`, samples PCM frames for lip-sync.

These loops *do not directly know about each other*. They are coupled only through the `AnimatedVoiceRequest` value type ([[#3]] below) — a frame-by-frame triple of `(Animations, Faces, Voices)` that `ModelController.AnimatedSay` walks sequentially.

**What the domain owns:**

| File | LOC | Owns |
|---|---|---|
| `ModelController.cs` | 464 | The animation queue + idle loop + registered-animation catalog; `AnimatedSay` orchestrator; `ToAnimatedVoiceRequest` regex tag parser; avatar activation/deactivation; `IdlingMode` switching |
| `SpeechController.cs` | 212 | `AudioSource` ownership; `SpeechSynthesizerFunc` delegate; voice prefetch queue (`ConcurrentQueue<Voice>`); PCM frame sampling at ~30FPS for external lip-sync; `Say` sequential player |
| `FaceController.cs` | 73 | Face expression queue; `IFaceExpressionProxy` delegation; default 7-second face duration |
| `Animation.cs` | 24 | The `Animation` value type — `ParameterKey`, `ParameterValue`, `Duration`, optional `LayeredAnimationName` + layer |
| `AnimatedVoice.cs` | 34 | One *frame* of `(Voices, Animations, Faces)` |
| `AnimatedVoiceRequest.cs` | 55 | A list of `AnimatedVoice` frames plus `StartIdlingOnEnd` / `StopIdlingOnStart` flags |
| `Voice.cs` | 83 | The `Voice` value type — `Text`, `PreGap`, `PostGap`, `TTSConfiguration`, `UseCache`, `Description`, computed `CacheKey` |
| `FaceExpression.cs` | 17 | The `FaceExpression` value type — `Name`, `Duration`, `Description` |
| `Blink.cs` | 198 | Generic blink — auto-detects blend shape by keyword (`blink`/`eye`/`close`, excluding `left`/`right`), randomised interval, `Mathf.SmoothDamp` transition |
| `uLipSyncHelper.cs` | 107 | Auto-detection of VRChat-style viseme blend shapes (`vrc.v_aa` / `vrc.v_ih` / etc.); registration with uLipSync's `uLipSyncBlendShape` |
| `ConfigurableLipSyncHelper.cs` | 109 | Same as above but with user-configurable blend-shape names |
| `VRCFaceExpressionProxy.cs` | 144 | VRChat-avatar face proxy — blend shapes by name |
| `ModelRequestBroker.cs` | 193 | A *standalone* text-to-AnimatedVoiceRequest queue runner — used independently of DialogProcessor for direct text-to-speech-with-animation paths |
| `ActionHistoryRecorder.cs` | — | Records the sequence of fired animations/faces/voices for debug/test (light, not detailed here) |

**What the domain does NOT own:**
- The VRM model itself — owned by `Extension/VRM/` ([[29_VRM_INTERFACE]]).
- The TTS engine — owned by `SpeechSynthesizer/` ([[15_SPEECH_SYNTHESIZER_DOMAIN]]).
- The LLM-streamed text — owned by `LLMContentProcessor` ([[16_LLM_SERVICE_DOMAIN]]).
- The dialog state — owned by `DialogProcessor` ([[13_DIALOG_PROCESSOR_DOMAIN]]).
- The decision *what* face/animation to play — that's the LLM's tag emission, parsed by `ModelController.ToAnimatedVoiceRequest` (lines 237-292) but originating outside the domain.

---

## 2. How It Works

### 2.1 The three queues, decoupled

`ModelController.Animate(List<Animation>)` (lines 296-303):
```csharp
public void Animate(List<Animation> animations)
{
    ResetLayers();
    animationQueue.Clear();
    animationQueue = new List<Animation>(animations);
    animationStartAt = 0;
    GetAnimation = GetQueuedAnimation;
}
```

The animation queue is replaced wholesale; previous queue is dropped. The function pointer `GetAnimation` is *re-bound* from `GetIdleAnimation` to `GetQueuedAnimation` — this is the elegant trick. `UpdateAnimation` (line 313) calls `GetAnimation()` every frame; the function pointer pattern means the per-frame code doesn't branch on "queued vs idle" — it just calls whatever is currently bound.

`GetQueuedAnimation` (lines 343-366) pops the head animation when its `Duration` has elapsed; returns `default` when the queue empties (which triggers `StartIdling(false)` at line 324). `GetIdleAnimation` (lines 368-383) returns a *random* idle animation from the weighted-index list per `IdlingMode` whenever the current idle animation times out.

`FaceController.SetFace(List<FaceExpression>)` (lines 28-33):
```csharp
public void SetFace(List<FaceExpression> faces)
{
    faceQueue.Clear();
    faceQueue = new List<FaceExpression>(faces);
    faceStartAt = 0;
}
```

Same pattern: replace, reset timer. `UpdateFace` (lines 35-55) plays the head face, ages it by `Time.realtimeSinceStartup - faceStartAt`, pops when expired. Default duration if not specified is `7.0f` seconds (line 10) — long enough that one expression covers an utterance.

`SpeechController.PrefetchVoices(List<Voice>, CancellationToken)` (lines 172-178):
```csharp
public void PrefetchVoices(List<Voice> voices, CancellationToken token)
{
    foreach (var voice in voices)
    {
        voicePrefetchQueue.Enqueue(voice);
    }
}
```

The prefetch queue is a `ConcurrentQueue<Voice>` (line 16); the prefetch *task* (`StartVoicePrefetchTask`, lines 180-204) runs forever, dequeuing one voice at a time and calling `SpeechSynthesizerFunc(voice.Text, parameters, token)`. The TTS implementation (`SpeechSynthesizerBase.GetAudioClipAsync`, [[15_SPEECH_SYNTHESIZER_DOMAIN]]) caches the result by `(text, params).GetHashCode()` — so subsequent `Say` calls find the audio already downloaded.

This is the **parallel-prefetch trick** that makes CDK feel responsive. While the LLM is still streaming sentence 2, sentence 1's audio is downloading; by the time `Say(sentence 1's voices)` runs, the audio is cached and `await SpeechSynthesizerFunc(...)` returns instantly. Compare SAP's serial TTS (`server.py:8000+` → `moss_tts.moss_generate_audio` → audio bytes), which downloads one utterance at a time per response.

### 2.2 The orchestrator: `AnimatedSay`

`ModelController.AnimatedSay(AnimatedVoiceRequest, CancellationToken)` (lines 184-235) is where the three queues meet. The pattern:

```csharp
// /tmp/ChatdollKit/Scripts/Model/ModelController.cs:184-212
public async UniTask AnimatedSay(AnimatedVoiceRequest request, CancellationToken token)
{
    foreach (var animatedVoice in request.AnimatedVoices)
    {
        if (token.IsCancellationRequested) break;

        if (animatedVoice.Animations.Count > 0)
            Animate(animatedVoice.Animations);

        if (animatedVoice.Faces != null && animatedVoice.Faces.Count > 0)
            FaceController.SetFace(animatedVoice.Faces);

        if (animatedVoice.Voices.Count > 0)
            await SpeechController.Say(animatedVoice.Voices, token);
    }
    // ... idle restart logic
}
```

**Per frame:** set animation (non-blocking — animation runs in `Update`), set face (non-blocking — face runs in `Update`), `await Say(voices)` (blocking — speech is sequential within a frame). When the voice playback finishes for this frame, advance to the next frame.

The contract: animations and faces are *parallel-non-blocking*; voice is *sequential-blocking*. The frame is the synchronisation unit. **A frame can change face without changing voice; a frame can change animation without changing face.** This is the right granularity for an LLM-driven avatar — the LLM emits one `AnimatedVoice` frame per parsed sentence (via `ModelController.ToAnimatedVoiceRequest`), and the avatar's body changes once per sentence.

### 2.3 The tag parser — text becomes embodiment

`ModelController.ToAnimatedVoiceRequest(string inputText, string language = null)` (lines 237-292) is where the LLM's intent becomes structured embodiment. The regex:

```csharp
// /tmp/ChatdollKit/Scripts/Model/ModelController.cs:247
var pattern = @"(\[.*?\])|([^[]+)";
```

Captures either `[...]` tags or plain text. For each capture:
- `[face:Joy]` — call `avreq.AddFace("Joy", duration=DefaultFaceExpressionDuration)`. Also set `ttsConfig.Params["style"] = "Joy"` — propagates the emotional style to the TTS (CDK uses this in VOICEVOX, where speaker styles include happy/sad/etc).
- `[anim:Wave]` — look up the registered animation by name (`IsAnimationRegistered(anim)`, line 261). If registered, add it. If not, `Debug.LogWarning` and skip.
- `[pause:0.5]` — parse a float; store as `preGap` to be applied to the *next* voice (line 285's `avreq.AddVoice(text, preGap, ...)`).
- `[<anything else>]` — `continue` (silently consume; line 279-282).
- Plain text — add as a Voice (line 283-287), with `preGap` from the last `[pause:]` and a `postGap` of `0` if the text ends with a Japanese period `。` or `0.3` seconds otherwise.

The protocol is documented at [[25_ANIMATION_TAG_PROTOCOL]]. The key teachings:
- **Tags are inline with text**, not at sentence boundaries — the LLM can say `Well that's [face:Surprised] surprising!` and the face changes *mid-sentence*.
- **`[face:]` doubles as TTS style** — one tag drives two embodiments (visual face + voice character).
- **`[pause:]` is a per-segment delay** — the LLM can pace its own speech.
- **The `ttsConfig` is reused across voice fragments** until a new `[face:]` resets the style — sticky-until-changed semantics.

### 2.4 Idling — the autonomic layer

`ModelController.AddIdleAnimation(Animation, weight, mode)` (lines 130-146) registers idle animations *per mode* (default mode: `"normal"`). The `idleWeightedIndexes` (line 33) is a list of indices duplicated per weight — picking a random index gives a weighted random selection without a separate weight-table. Clever, minimal, correct.

`IdlingMode` (line 35) is a string identifier. `ChangeIdlingModeAsync(mode)` (lines 160-180):
- Sets the new mode.
- Optionally runs `onBeforeChange` (a `Func<UniTask>` the caller supplies — for fade-outs).
- If the new mode has an `idleFace` registered (line 154), sets it.
- Else if mode is `"normal"`, resets to `Neutral`.
- Restarts idling.

So the avatar can be `"normal"` (default), `"focused"`, `"sleeping"`, `"excited"` — each with its own random pool of idle animations and a sticky face. The LLM doesn't drive this directly; the application code can call `ChangeIdlingModeAsync("focused")` when the user is working, etc. Ember should expose this to Hjarta (the affective layer): the *mood* selects the idling mode, and the idling mode selects which random animations play when the avatar is not speaking.

### 2.5 The blink loop

`Blink.StartBlinkAsync` (lines 122-167) and `VRMBlink.StartBlinkAsync` (lines 48-88) follow the same pattern:

```csharp
while (true) {
    // Closed-eyes interval
    var closeInterval = Random.Range(minBlinkIntervalToClose, maxBlinkIntervalToClose);  // 3-5 seconds
    await UniTask.Delay((int)(closeInterval * 1000));
    blinkAction = CloseEyesOnUpdate;  // SmoothDamp toward 1.0

    // Open-eyes interval
    var openInterval = Random.Range(minBlinkIntervalToOpen, maxBlinkIntervalToOpen);  // 0.05-0.1 seconds
    await UniTask.Delay((int)(openInterval * 1000));
    blinkAction = OpenEyesOnUpdate;  // SmoothDamp toward 0.0
}
```

`blinkAction` is a function pointer set per-phase; `LateUpdate` invokes it (`Blink.cs:36-39`). `SmoothDamp` (lines 183, 194) provides the curve so the blink doesn't pop. The transition times (`blinkTransitionToClose = 0.01f`, `blinkTransitionToOpen = 0.02f`) are short — a natural blink.

The blink interacts with the face proxy: in `VRMFaceExpressionProxy.Update` (lines 26-62), `IBlink.StartBlinkAsync` is called when the current face is `"Neutral"` and `StopBlink` is called otherwise — because a happy/surprised/etc. face expression *already drives the blink-eye blend shape* (since VRM face expressions are blend-shape composites), and re-driving it from the blink loop would conflict. This is one of the few cross-domain coordinations CDK does, and it is *done correctly*: the face proxy *owns* the decision because it owns the conflict.

### 2.6 The face expression proxy — VRM-specific smooth-damp

`VRMFaceExpressionProxy.SetExpressionSmoothly(name, value)` (lines 69-75) starts a transition; `Update` (lines 26-62) interpolates the *target* blend-shape weight from `velocityAtStart` to `value` over `smoothTime` (default 0.2s). During the transition, *other* blend shapes (that are currently > 0) are smoothly faded toward 0 (lines 56-60). This is the "smooth one-out, smooth one-in" pattern done with a single time parameter.

`VRCFaceExpressionProxy` ([[12_MODEL_CONTROLLER_DOMAIN]] doesn't deep-dive — see the file at `Scripts/Model/VRCFaceExpressionProxy.cs:1-144`) does the same for VRChat-style avatars but with named blend shapes rather than VRM's `BlendShapeKey` enum.

The lesson: face transitions are not abrupt; they are smoothed; the smoothing is *per-proxy* so different avatar formats can implement it differently. Ember should declare an `ExpressionProxy` abstract base with `setup`, `set_expression`, `set_expression_smoothly` — implementations register per supported avatar format.

### 2.7 The `ModelRequestBroker` — text-to-embodied-speech without a dialog

`Model/ModelRequestBroker.cs` (193 LOC) is a *standalone* path that bypasses DialogProcessor entirely. `SetRequest(text)` (lines 66-80):

```csharp
public void SetRequest(string text)
{
    modelTokenSource?.Cancel();
    modelTokenSource?.Dispose();
    modelRequestQueue.Clear();
    speechController.StopSpeech();

    modelTokenSource = new CancellationTokenSource();
    foreach (var avreq in ToAnimatedVoiceRequests(text))
    {
        modelRequestQueue.Enqueue(avreq);
    }
}
```

Cancels any in-flight speech, splits the text into sentences (`SplitString`, lines 127-167), converts each to an `AnimatedVoiceRequest`, queues them. `StartListening` (lines 43-64) is a perpetual coroutine that dequeues and plays.

**This is the bypass surface.** A user with a pre-canned line — `"Hello, welcome!"` with embedded tags — can call `modelRequestBroker.SetRequest("[face:Joy]Hello![anim:Wave]")` and the avatar performs it without ever invoking the LLM. Useful for greetings, scripted responses, UI feedback. Ember should expose the equivalent — a `MunnrBroker` that accepts pre-composed text-with-tags and plays it.

The pattern is also what the `[[18_NETWORK_DOMAIN]] SocketServer` interfaces with: an external process sends `{"Endpoint": "speech", "Text": "[face:Smile]Hi there!"}` and the broker performs it without consulting the LLM at all.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The animation queue is replaced wholesale

`Animate(animations)` *clears* the existing queue (line 299). Mid-utterance, a new animation request overwrites all pending ones. This is *deliberate* — the LLM's next sentence comes with its own animation choice — but it means there is no way to *append* to the queue. If a user wants "play the current animation, then play this next one when it finishes," they must wait themselves. Ember can offer both *replace* and *append* semantics with two methods.

### 3.2 The face queue silently resets to Neutral

`UpdateFace` (lines 41-46): when the queue empties and there is no `faceToSet`, it sets `Neutral` via `SetFace(new List<FaceExpression>() { new FaceExpression("Neutral", 0.0f, ...) })`. The duration `0.0f` means "permanent until replaced." This is correct, but it also means *every silence is `Neutral`* — there is no "hold the last expression for a bit then fade." For an avatar in a long pause, the face snaps back. Subtle but visible.

### 3.3 The lip-sync sampling is `Time.realtimeSinceStartup`-based

`SpeechController.Say` (lines 99-115) samples the audio clip at a 30FPS cadence by computing `currentPosition` from elapsed time (lines 104-105):

```csharp
var elapsedTime = Time.realtimeSinceStartup - startTime;
var currentPosition = Mathf.FloorToInt(elapsedTime * clip.frequency) * clip.channels;
```

This assumes the `AudioSource` plays at exactly the clip's frequency — which it does *unless* the source is pitch-shifted, the platform throttles audio, or the clip's sample rate doesn't match the AudioSource's. If any of these drift, the lip-sync samples are misaligned with the actual playback. CDK does not detect or correct for this.

### 3.4 The `ToAnimatedVoiceRequest` regex is permissive

`@"(\[.*?\])|([^[]+)"` (line 247) matches `[...]` non-greedily *or* a run of non-`[` characters. A nested `[` will confuse it (`[face:[Joy]]` matches `[face:[Joy]` as the tag and `]` as the next run). Tags are not validated at this layer — the validation happens at the registration check for animations (line 261) but *not* for faces or pauses (lines 252-257, 271-278). An LLM emitting `[face:NotARealFace]` will trigger an attempt to set a non-existent face; the face controller will pass it to the proxy; the proxy will fail to find the blend shape; the face will stay at the previous value silently.

### 3.5 The `processingId` reset race

`ModelController` uses `Time.realtimeSinceStartup` and `currentAnimation.Id` (`Animation.Id` is `Guid.NewGuid()` per-construction). When `Animate` is called rapidly (LLM streaming multiple short sentences), the GUID comparison in `UpdateAnimation` (line 328) prevents re-triggering — but the queue is *replaced*, so a brief animation can be cancelled before it fully plays. The visual effect is subtle pose-popping. SAP has the same problem in `vts_manager` (the rate-limit on hotkey triggers); CDK does not address it explicitly.

### 3.6 The crisp parts (inventory)

- **The function-pointer-for-loop-choice pattern.** `GetAnimation = GetIdleAnimation` vs `GetAnimation = GetQueuedAnimation` (lines 115, 126) is the cleanest *strategy-pattern-in-Update* I have seen in a Unity codebase. No branching in the hot path. No state flag. One function pointer.
- **The three-queue triple.** Animation, face, voice — each owned by its own component, each updated in its own `Update` — composed only through the `AnimatedVoiceRequest` value type. The composition is at the *data layer*, not the runtime layer.
- **The `AnimatedVoiceRequest` builder.** `AddVoice / AddAnimation / AddFace` with an `asNewFrame` flag (`AnimatedVoiceRequest.cs:22-47`) — frame-level composition with a simple API. No builder pattern, no fluent interface, just methods.
- **The TTS-config-as-style-coupling.** `ttsConfig.Params["style"] = face` (line 256). One tag, two effects. The TTS provider (VOICEVOX has a speaker-per-style; AivisCloud has emotion tags) reads the style and the avatar visualises the face. *Visual and aural affect from one LLM tag.*
- **The idle-modes-with-weighted-pools.** Per-mode random selection with `idleWeightedIndexes`. Different modes for different application states. Ember adopts this.
- **The blink-face conflict resolution.** `VRMFaceExpressionProxy` *knows* that blink and expressions share blend shapes and *owns* the decision to suspend the blink loop during non-Neutral faces. The owner of the conflict resolves the conflict.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 2 — Model in the macro shape
- [[11_AIAVATAR_DOMAIN]] — AIAvatar's `SpeechController.OnSayStart/OnSayEnd` callbacks
- [[15_SPEECH_SYNTHESIZER_DOMAIN]] — the TTS that SpeechController calls
- [[1B_ANIMATION_DOMAIN]] — `[anim:]` + `[face:]` tag protocol details
- [[25_ANIMATION_TAG_PROTOCOL]] — the full tag-wire-format contract
- [[29_VRM_INTERFACE]] — UniVRM-specific implementations of the three interfaces
- [[sap:11_AVATAR_DOMAIN]] — SAP's VRM+VTS+VMC scattered approach for contrast
- [[waifu:20_ZEROWEIGHT_SURFACE]] — Waifu's cloud-side `runAction` vocabulary contrast

---

## What This Means for Ember

**Adopt:**
- The **three-queue triple** (animation, face, voice) as Ember's Munnr internal structure. Source: `Scripts/Model/ModelController.cs`, `FaceController.cs`, `SpeechController.cs`. Apache-2.0 attribution required. Ember's Python implementation: three `asyncio.Queue`s, three coroutines, one orchestrator method `animated_say(request)`.
- The **`AnimatedVoiceRequest` value type** with frame-level composition. Ember's `EmbodiedUtterance` Pydantic model — `frames: list[Frame]`, each frame `(voices, animations, faces, optional_pre_gap)`. Built up by Munnr's tag parser; consumed by Munnr's playback coroutine.
- The **function-pointer strategy pattern** (`GetAnimation = GetIdleAnimation`/`GetQueuedAnimation`). Adopt as Ember's `self._animation_source: Callable[[], Animation | None]` — pluggable at runtime, no branching in the per-tick code. Source: `Scripts/Model/ModelController.cs:115, 126`.
- The **TTS-config-as-style-coupling** (`ttsConfig.Params["style"] = face` at line 256). Adopt as Ember's tag protocol where `[face:Joy]` simultaneously selects a TTS style. The unified-affect-tag idea is what SAP and Waifu both fail to express cleanly.
- The **per-mode weighted idle pools** (`idleWeightedIndexes`, line 33; `AddIdleAnimation(..., weight, mode)`). Adopt as Ember's `IdlingPool(mode: str, animations: list[(Animation, int)])`. Hjarta selects the mode based on affective state; the pool selects the animation randomly.
- The **blink-face conflict ownership pattern** (`VRMFaceExpressionProxy:32-39`). When two visual layers share a substrate (here, blend shapes), the layer-owner-of-the-conflict decides who suspends. Generalise to any Ember layered visual surface.

**Adapt:**
- **The animation-queue-replace-not-append default.** Adapt as Ember's `Munnr.set_animation_queue(replace_or_append)` with explicit choice. Default to replace (CDK's behaviour) but expose append as a typed alternative. The mid-utterance overwrite is correct for LLM-driven turns but wrong for scripted greetings that want to chain.
- **The `Neutral` face fallback.** Adapt as Ember's *previous-face-with-fade* fallback: when the face queue empties, fade the current face toward `Neutral` over a configurable `face_idle_fade_duration` (default 1.5 seconds). Avoids the snap-back.
- **The PCM-sampling at `Time.realtimeSinceStartup`.** Adapt to use *actual playback position* from the audio output layer (Pyaudio's `get_stream_position` or equivalent). Detect drift > 50ms and log a Sögumiðla `LipSyncDrift` event.
- **The tag-regex permissive matching.** Adapt to Ember's tag parser as a stricter PEG grammar (e.g., via `parsy` or `lark`). Nested brackets are *errors*, not lenient consumption. Emit a `MalformedTag` event for any unparseable tag.

**Avoid:**
- **Silent face-failure when the proxy doesn't find the blend shape.** Ember's expression proxy emits `UnknownExpression` events on miss; the orchestrator can choose to fall back to Neutral *with logging*, not silently.
- **The unbounded prefetch queue** (`SpeechController.voicePrefetchQueue` is a `ConcurrentQueue` with no size limit, line 16). On a long LLM response with many sentences, this can queue dozens of TTS calls. Ember bounds at a sensible limit (e.g., 8 ahead-of-playback) and applies back-pressure.
- **The hardcoded 30FPS lip-sync sampling rate** (line 115's `UniTask.Delay(33)`). Ember exposes the sampling rate as a configurable parameter per TTS quality tier — 60FPS for high-quality, 30FPS for pi-tier, 15FPS for power-saving.

**Invent:**
- **The Embodied Frame Value Type.** Ember's `EmbodiedFrame(voices, animations, faces, pre_gap_seconds, mood_hint)` — frame-level composition like `AnimatedVoice` but with one extension: `mood_hint` is a typed affective tuple `(valence, arousal)` from Hjarta. Frames carry not just *what to do* but *why* — and downstream surfaces can choose to log/filter/transform based on the why. This makes Ember's embodiment honest in a way CDK is not: CDK takes the LLM's word for the face; Ember's frame *records the affective basis* and can refuse to embody affect the actual state contradicts. See [[60_synthesis:65_MEMORY_INTEGRATION]] for Hjarta's link.
- **The Idle-Mode-as-Hjarta-Output Vow.** CDK's `IdlingMode` is set by application code. Ember's idling mode is *derived* from Hjarta's affective state — `valence > 0.3 and arousal > 0.5 → "excited"`; `valence < -0.2 → "subdued"`; etc. The avatar's idle behaviour is a *report* on its inner state, not a config. The Embodied Honesty Vow ([[sap:11_AVATAR_DOMAIN]] §invent) realised at the idle layer.
- **The Multi-Surface Frame Broadcast.** When Munnr emits an `EmbodiedFrame`, the frame is dispatched to *every registered avatar surface* — Unity-tier (VRM in Unity), Electron-tier (VRM in three.js via SAP-style transparent window), terminal-tier (emoji + ASCII art), log-tier (typed event for review). All surfaces receive the same typed frame; per-surface adapters render. SAP's three-WS-bus mess ([[sap:10_DOMAIN_MAP]] §5.3) avoided.
- **The Prefetch Backpressure Limit.** Ember's voice prefetch queue is bounded; on overflow, the producer (LLMContentProcessor) blocks until the consumer (SpeechController) advances. A typed `BackpressureApplied` event fires for observability. Long LLM responses do not pile up unbounded TTS work.
- **The Face-Voice-Animation Coherence Check.** Ember asserts at frame-construction time that if `[face:Sad]` and `[anim:Dance]` appear in the same frame, the combination has a registered "is this incoherent?" check. Hjarta's affective coherence module either green-lights, substitutes, or emits an `IncoherentEmbodiment` event. The avatar refuses to be a frantic-happy-dancing-sad robot unless explicitly permitted.

*Apache-2.0 attribution: when patterns from `ChatdollKit/Scripts/Model/` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

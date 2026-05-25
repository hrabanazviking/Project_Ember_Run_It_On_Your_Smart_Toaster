---
codex_id: 1B_ANIMATION_DOMAIN
title: Animation Domain — Four Tags, One Regex, Two Brokers, Three Queues
role: Architect
layer: Domain
status: draft
chatdoll_source_refs:
  - Scripts/Model/ModelController.cs:1-464
  - Scripts/Model/ModelController.cs:237-292
  - Scripts/Model/ModelRequestBroker.cs:1-193
  - Scripts/Model/FaceController.cs:1-73
  - Scripts/Model/SpeechController.cs:1-212
  - Scripts/Model/AnimatedVoice.cs
  - Scripts/Model/AnimatedVoiceRequest.cs
  - Scripts/Dialog/DialogPriorityManager.cs:1-86
  - Scripts/LLM/LLMContentProcessor.cs:124-141
ember_subsystem_targets: [Andlit, Rödd, Munnr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/12_MODEL_CONTROLLER_DOMAIN
  - 10_domain/13_DIALOG_PROCESSOR_DOMAIN
  - 10_domain/16_LLM_SERVICE_DOMAIN
  - 20_interface/25_ANIMATION_TAG_PROTOCOL
  - 20_interface/29_VRM_INTERFACE
  - sap:14_ANIMATION_VOCABULARY
  - waifu:20_ZEROWEIGHT_SURFACE
---

# Animation Domain
## Four Tags, One Regex, Two Brokers, Three Queues

*— Rúnhild Svartdóttir, Architect*

> *The avatar's body is only as expressive as the channel by which the language model can address it. ChatdollKit's channel is a regex over the LLM's text stream — four tags, parsed inline, materialised as queued frames. It is the simplest expressive channel in the three corpora and the most tightly synchronised with speech.*

The animation domain is *not* a single folder. It spans `Scripts/Model/ModelController.cs` (464 LOC — the tag parser and the animation queue), `Scripts/Model/ModelRequestBroker.cs` (193 LOC — the external-request entry point with its own queue), `Scripts/Model/FaceController.cs` (73 LOC — the face expression queue), `Scripts/Model/SpeechController.cs` (212 LOC — the voice queue with PCM sampling for lip-sync), and the consumption-side wiring in `Scripts/Dialog/DialogPriorityManager.cs` (86 LOC — the priority queue for queued utterances) and `Scripts/LLM/LLMContentProcessor.cs:124-141` (the `[lang:]` tag extraction in the stream). Total: roughly **1,000 LOC** across six files for a system whose architectural surface is *four characters*.

The four characters: `[`, `:`, `]`, and the contents in between. CDK defines four tag types — `[face:Expression]`, `[anim:Name]`, `[pause:0.5]`, `[lang:en-US]` — all parsed by one regex (`Scripts/Model/ModelController.cs:247`). The LLM emits the tags inline with speech text. The same parser splits the text into a sequence of *animated voice frames*. Each frame fires animation queue, face queue, voice queue. **Animation and speech are not coordinated — they are co-generated from a single string.** This is the architectural insight, and it is non-obvious until you see it.

Compare SAP's animation vocabulary ([[sap:14_ANIMATION_VOCABULARY]]) — out-of-band `<happy>` tags injected by the server, applied after-the-fact via a separate code path. Compare Waifu's `runAction("dance")` ([[waifu:20_ZEROWEIGHT_SURFACE]]) — typed string commands separate from speech, no inline composition. **CDK's inline-tag pattern is the tightest speech-expression coupling of the three.** It is also the most fragile (silent drop on unknown tags, no validation, regex parser).

---

## 1. The Subject Itself

**What the domain is:** the *production* side of avatar embodiment. Given a string like `Hello! [face:Joy][anim:Wave] Nice to meet you.`, produce: (a) play "Hello!" voice clip while triggering joyful face + wave animation, (b) play "Nice to meet you." voice clip with the face and animation continuing. Coordinate timing such that face changes *before* the voice clip, animation starts *with* the voice clip, and lip-sync animates *from* the voice clip's PCM samples.

**What it owns:**

| Concern | Files | LOC | Owns |
|---|---|---|---|
| **Tag parser** | `Scripts/Model/ModelController.cs:237-292` | ~55 | The single regex pattern `@"(\[.*?\])|([^[]+)"`; the four tag prefixes; the conversion to `AnimatedVoiceRequest` |
| **Animation queue** | `Scripts/Model/ModelController.cs:294-460` | ~165 | Per-frame animation queue, idle-animation loop, layered animation blending, `RegisterAnimation`/`IsAnimationRegistered` lookups |
| **Face queue** | `Scripts/Model/FaceController.cs` | 73 | Face expression queue, smooth-damp transitions, expression registry |
| **Voice queue** | `Scripts/Model/SpeechController.cs` | 212 | Voice playback queue, prefetch (`PrefetchVoices`), PCM-sample sampling for external lip-sync helpers, `OnSayStart`/`OnSayEnd` callbacks |
| **Animated-voice value types** | `AnimatedVoice.cs`, `AnimatedVoiceRequest.cs`, `Animation.cs`, `Voice.cs`, `FaceExpression.cs` | combined ~100 | The typed records — `Animation`, `FaceExpression`, `Voice`, the frame `AnimatedVoice` containing all three lists, the request bundle `AnimatedVoiceRequest` |
| **Broker** | `Scripts/Model/ModelRequestBroker.cs` | 193 | External-request entry point: splits text into sentences, generates `AnimatedVoiceRequest`s, fires synthesis prefetch, queues, dequeues per-frame, dispatches |
| **Priority queue** | `Scripts/Dialog/DialogPriorityManager.cs` | 86 | Two-level queue: priority 0 fires immediately; priority N>0 enqueues for next-idle; LLM-generated utterances at default 10; system interjections at priority 5 |

**What it does NOT own:**
- The LLM-side decision *to emit a tag* — that's prompt engineering on the application side.
- The VRM body / Live2D body — those are pluggable via `Extension/VRM/` or other model integrations ([[29_VRM_INTERFACE]]).
- The lip-sync visuals — `uLipSyncHelper` consumes PCM samples but is *not* part of this domain; it is wired by `ModelController` and runs from the audio source.

---

## 2. How It Works

### 2.1 The four tags

The LLM is prompted to emit text like:

```
Hello! [face:Joy][anim:Wave] Welcome to my house.[pause:0.5] [lang:ja-JP] こんにちは!
```

The four tag types:

| Tag | Example | Effect | Default duration |
|---|---|---|---|
| `[face:X]` | `[face:Joy]` | Activates a registered face expression `X` | `FaceController.DefaultFaceExpressionDuration` (typically 7s) |
| `[anim:X]` | `[anim:Wave]` | Triggers a registered animation `X` | the animation's own `Duration` field, set at registration |
| `[pause:N]` | `[pause:0.5]` | Inserts a 0.5-second silence before the next voice clip | (the silence itself; no other state change) |
| `[lang:X]` | `[lang:ja-JP]` | Switches subsequent voice synthesis to language `X` | sticky until next `[lang:]` |

Each tag has its own semantics: `face` and `anim` queue actions; `pause` injects timing; `lang` sets a *style modifier* that flows through to TTS via `TTSConfiguration.Params["language"]`.

**The tag set is not extensible at runtime.** Adding a fifth tag requires editing `ModelController.ToAnimatedVoiceRequest`. For Ember, the tag *vocabulary* should be a registry — adding a tag is registering a parser plus a target queue.

### 2.2 The one regex

`Scripts/Model/ModelController.cs:247-249`:

```csharp
var pattern = @"(\[.*?\])|([^[]+)";
foreach (Match match in Regex.Matches(inputText, pattern))
{
    var parsedText = match.Value.Trim();
    // ... if-else over tag prefixes
}
```

The pattern matches *either* a bracketed tag (non-greedy) *or* a run of non-bracket characters. Every chunk of the input is one of these two — there is no third match-mode. The processing loop is a switch on `parsedText.StartsWith("[face:")`, `StartsWith("[anim:")`, `StartsWith("[pause:")`, otherwise (text or `[lang:...]`-like other tag).

**The handling of unrecognised tags** (line 279-282):

```csharp
else if (parsedText.StartsWith("["))
{
    continue;  // Silent skip
}
```

If the LLM emits `[mood:thoughtful]`, the parser silently drops it. No event, no warning beyond the registered-animation case (line 268 logs unknown animations). Tags can be added by users on the LLM side without breaking parsing; they just have no effect. For Ember, the silent drop is the wrong default — emit a `UnknownTagSkipped(tag)` event so the orchestrator knows the LLM is trying things the avatar can't do.

### 2.3 The `AnimatedVoiceRequest` value type

The parser's output is an `AnimatedVoiceRequest` — a bundle of frames. Each frame is an `AnimatedVoice`:

```
AnimatedVoiceRequest
├── AnimatedVoices: List<AnimatedVoice>
│   ├── AnimatedVoice
│   │   ├── Animations: List<Animation>
│   │   ├── Faces: List<FaceExpression>
│   │   └── Voices: List<Voice>
│   └── ...
└── StartIdlingOnEnd: bool
```

Each `AnimatedVoice` is *the work for one tag-cluster + the voice clip that follows*. So `[face:Joy][anim:Wave] Hello.` becomes one frame with Faces=[Joy], Animations=[Wave], Voices=[Hello]. The next sentence (after a `.`) becomes the next frame.

The frame is the unit of synchronisation. When the frame fires, all three sub-lists fire *together* — face transitions, animation starts, voice plays. Lip-sync runs from the voice's PCM samples. **The frame is the architectural primitive of speech-body coordination.**

### 2.4 The `ModelController.AnimatedSay` dispatch

`Scripts/Model/ModelController.cs:184-235` (approximated; line numbers within the bound):

```csharp
public async UniTask AnimatedSay(AnimatedVoiceRequest avreq, CancellationToken token) {
    foreach (var av in avreq.AnimatedVoices) {
        if (av.Animations != null && av.Animations.Count > 0) Animate(av.Animations);
        if (av.Faces != null && av.Faces.Count > 0) FaceController.SetFace(av.Faces);
        if (av.Voices != null && av.Voices.Count > 0) await SpeechController.Say(av.Voices, token);
    }
    if (avreq.StartIdlingOnEnd && !token.IsCancellationRequested) StartIdling();
}
```

Three calls per frame, in order: animation, face, voice. `Animate` and `SetFace` are fire-and-forget queue mutations; they return immediately. `SpeechController.Say` *awaits* the voice clip playing to completion. So the **frame's duration is the voice clip's duration**; animation and face overlap with voice.

**Why face → animation → voice?** The frame's face change happens first (instant queue swap). Animation starts second (queue swap + Animator state transition). Voice starts third (after AudioClip play). On a fast machine the gap is single-digit milliseconds; on a slow machine the order is still right, just slower. The visual perception: face is *set* before the voice; the animation *kicks in* with the voice. Tight enough that the perception is "the avatar emoted while talking."

### 2.5 The three independent queues

Each consumer has its own queue:

- **Animation queue** (`ModelController.cs:296-308`) — `List<Animation> animationQueue`. Per-frame `UpdateAnimation()` (line 313+) dequeues based on time elapsed past `currentAnimation.Duration`. Idle-animation loop when queue empty (line 343+). Layered animations crossfade via `Animator.CrossFadeInFixedTime`.

- **Face queue** (`FaceController.cs`) — same pattern. Smooth-damp transitions between expressions; idle-face when queue empty.

- **Voice queue** (`SpeechController.cs:38-169`) — `List<Voice> voices`. Per-voice: synthesize via `SpeechSynthesizerFunc(text, params, token)`, play via `AudioSource.PlayOneShot`, sample PCM frames during playback (lines 99-127), invoke external lip-sync handlers.

Three queues, three update loops, one synchronisation source: the *voice queue's await*. If the voice queue is empty, the animation and face queues continue independently. If the voice queue is full, all three advance together.

**This is the design that makes barge-in clean.** When the user interrupts, `StopChatAsync` cancels the voice queue (`SpeechController.StopSpeech`) and the animation+face queues drift back to idle on their own timers. No coordination logic; the queues are autonomous. CDK's interruption semantics are *much* cleaner than SAP's, which has to call multiple "stop X" methods explicitly.

### 2.6 The `ModelRequestBroker` external entry

When an *external* source (`SocketServer`, a button press, a console command) wants the avatar to say something, it goes through `ModelRequestBroker`:

```csharp
// Scripts/Model/ModelRequestBroker.cs:66-80
public void SetRequest(string text) {
    modelTokenSource?.Cancel();  // Cancel any ongoing speech
    modelTokenSource?.Dispose();
    modelRequestQueue.Clear();
    speechController.StopSpeech();
    modelTokenSource = new CancellationTokenSource();
    foreach (var avreq in ToAnimatedVoiceRequests(text)) {
        modelRequestQueue.Enqueue(avreq);
    }
}
```

The broker has its **own queue** (`modelRequestQueue: Queue<AnimatedVoiceRequest>`) consumed by `StartListening` (line 43-64). Its job: handle *external* requests that don't come through the LLM pipeline. The same tag parsing happens; the same prefetch happens (lines 104-115 — fire synthesis ahead of playback); the same `AnimatedSay` dispatches.

**Two paths converge on `AnimatedSay`**: (1) `DialogProcessor` → `LLMContentProcessor` → AIAvatar-wired-callback → `AnimatedSay`, (2) `ModelRequestBroker.SetRequest` → its own queue → `AnimatedSay`. Either entry produces the same downstream behaviour. This is dual-entry-single-execution — the right shape when you have multiple producers of the same kind of work.

### 2.7 The `DialogPriorityManager`

`Scripts/Dialog/DialogPriorityManager.cs` is the *upstream* queue for *dialog* requests (not animated-voice frames). It exists because `DialogProcessor` can only handle one turn at a time, and queued requests need a place to wait.

```csharp
// DialogPriorityManager.cs:48-62
public void SetRequest(string text, Dictionary<string, object> payloads = null, int priority = 10) {
    if (priority == 0) {
        _ = dialogProcessor.StartDialogAsync(text + textToAppendNext);
    } else {
        dialogQueue.Enqueue(new DialogQueueItem() {
            Priority = priority, Text = text + textToAppendNext, Payloads = payloads
        }, priority);
    }
    textToAppendNext = string.Empty;
}
```

Priority 0 = immediate (bypass queue). Priority > 0 = enqueue. The `Update` (lines 22-46) dequeues when `DialogProcessor.Status == Idling`; the *2-frame* `idlingFrameThreshold` (line 13) prevents premature dequeue on the same frame the previous turn ended.

The two-tier (immediate vs queued) and the priority field together let multiple producers (mic, socket, JS bridge, scheduled prompts) coexist with sensible interleaving. Mic input at priority 10. Socket-driven announcements at priority 5 (more important than user speech). System notifications at priority 1 (highest, just below immediate). The user's standing utterances get queued; emergencies cut through.

For Ember: the priority pattern is portable; the `idlingFrameThreshold` is Unity-specific; Ember's asyncio version uses a `Status.Idling` event the dequeue coroutine awaits.

### 2.8 The `[lang:]` tag's special path

`[lang:]` is extracted *upstream* by `LLMContentProcessor`, not by `ModelController`:

```csharp
// Scripts/LLM/LLMContentProcessor.cs:124-128
var match = Regex.Match(processedText, @"\[lang:([a-zA-Z-]+)\]");
if (match.Success) {
    language = match.Groups[1].Value;
}
var contentItem = new LLMContentItem(processedText, isFirstWord, language);
```

The language flows into the `LLMContentItem` and through to `ModelController.ToAnimatedVoiceRequest(text, language)` as the second argument. From there into `TTSConfiguration.Params["language"]` (line 244). The TTS provider reads it and synthesises in the right voice.

**Why is `[lang:]` upstream?** Because language affects voice selection (English voice vs Japanese voice), and voice selection happens in TTS prefetch — which fires *before* `ModelController.AnimatedSay`. Putting the language extraction in `LLMContentProcessor` means the prefetch path has it. Putting it in `ModelController` would be too late. This is the kind of architectural detail that comes from running the code in production and discovering "the voice clip is in the wrong language because prefetch ran with stale config." Fix the order, move the tag extraction upstream.

For Ember: tag-extraction timing matters; not all tags are equal. A multi-pass parser (`LLMContentProcessor` for streaming tags, `ModelController` for frame tags) is correct. Document the multi-pass discipline.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The silent drop on unknown tags

The most consequential failure mode. `[anim:WaveWithBothHands]` if not registered → `Debug.LogWarning` (line 268). `[mood:thoughtful]` if not a defined tag → silent `continue` (line 281). The LLM emits tags the avatar can't honour; the user sees an avatar with less expression than the LLM tried to give it. There is **no signal back to the LLM** that its tag was ignored. The prompt-injection of available tags is the only feedback loop, and it is brittle.

### 3.2 The regex is non-greedy but matches `[]` empty tags

`@"(\[.*?\])|([^[]+)"` matches `[]` as a zero-length tag. The processing loop's StartsWith checks fail, so it silently drops. Fine in practice; brittle in theory.

### 3.3 The tag prefix string-match is N²

The if-else chain (`StartsWith("[face:")`, then `StartsWith("[anim:")`, etc.) is O(tags-per-frame × prefixes). For four prefixes it's not a problem; for a tag system with 20 types it would be. A dispatch dict (`tag_handlers: dict[str, Callable]`) is cleaner.

### 3.4 The `pause` value can be parsed but not validated

`[pause:0.5]` → 0.5s. `[pause:-1]` → -1 (interpreted as a negative pre-gap; the voice plays immediately, which is the same as 0). `[pause:9999]` → 9999s of silence. CDK does not bound; Ember should clamp.

### 3.5 The `face` style mapping leaks into TTS

Inside `ToAnimatedVoiceRequest` (line 256): `ttsConfig.Params["style"] = face;`. The face name *also* becomes the TTS style. If the face is `Joy` and the TTS provider has a `Joy` style, it speaks joyfully. If the TTS doesn't have `Joy`, it falls back to default. **The face vocabulary and the voice-style vocabulary are unified by string**. This works when the user defines both. It silently mismatches when only one is defined. Ember should separate the vocabularies but provide a default mapping.

### 3.6 No animation history beyond `ActionHistoryRecorder` debug-only

`ActionHistoryRecorder` (in `Scripts/Model/`) exists for tests. There is no *production* observability of what animations fired, in what order, with what timing. Post-mortem of "did the avatar look right during this turn?" is impossible from CDK's instrumentation alone. Ember's Sögumiðla event stream gives this for free.

### 3.7 The crisp parts

- **Inline-tag animation control.** Speech and expression in one string. Tight coupling.
- **One regex.** `@"(\[.*?\])|([^[]+)"`. Simple. Correct.
- **`AnimatedVoiceRequest` as the typed bundle.** Three lists per frame; one dispatch.
- **Three independent queues.** Animation, face, voice — autonomous; voice anchors timing.
- **`ModelRequestBroker` as the parallel external entry.** Same parser, separate queue, same dispatch.
- **`DialogPriorityManager`'s two-tier priority.** Immediate (0) vs queued (>0). Multi-producer-friendly.
- **The `[lang:]` extraction in `LLMContentProcessor`.** Tag extraction stratified by timing requirement.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 2 — Model subsystem in macro shape
- [[12_MODEL_CONTROLLER_DOMAIN]] — the queue and idle-loop deep dive
- [[13_DIALOG_PROCESSOR_DOMAIN]] — the dialog state machine that drives this domain
- [[16_LLM_SERVICE_DOMAIN]] §2.3 — `LLMContentProcessor`'s `[lang:]` extraction
- [[25_ANIMATION_TAG_PROTOCOL]] — the full wire-format specification
- [[29_VRM_INTERFACE]] — VRM-specific animation/face implementations
- [[sap:14_ANIMATION_VOCABULARY]] — SAP's out-of-band `<happy>` tags for contrast
- [[waifu:20_ZEROWEIGHT_SURFACE]] — Waifu's `runAction("dance")` typed-string for contrast

---

## What This Means for Ember

**Adopt:**
- The **inline-tag animation control** pattern. Ember's Munnr emits text with `[face:Joy][anim:Wave] Hello!` tags inline. The parser splits text and tags in one pass and produces typed frames. Apache-2.0 attribution required.
- The **single-regex pattern** `r"(\[.*?\])|([^[]+)"` for tag-split parsing. `re.finditer` in Python; same semantics. Direct lift.
- The **`AnimatedVoiceRequest` value-bundle shape**. Ember's `EmbodimentFrame` dataclass: `animations: list[Animation]`, `faces: list[FaceExpression]`, `voices: list[Voice]`, `start_idling_on_end: bool`. Apache-2.0 attribution required.
- The **three-independent-queue** model. Ember's three subsystems (Andlit-face, Andlit-anim, Rödd-voice) have autonomous queues; the voice queue's await anchors timing; the other two drift to idle on their own.
- The **two-tier priority queue** (`DialogPriorityManager`, `Scripts/Dialog/DialogPriorityManager.cs`). Apache-2.0 attribution required. Ember's `DialogQueue` has the same priority-0-immediate, priority-N-queued semantics.
- The **dual-entry-single-execution** pattern (LLM path *and* external broker, both flowing to `AnimatedSay`). Ember's `Munnr.dispatch_frame` is the single execution point; both the LLM pipeline and external broker call it.

*Apache-2.0 attribution: when patterns from `ChatdollKit/Scripts/Model/` and `ChatdollKit/Scripts/Dialog/DialogPriorityManager.cs` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:**
- The **silent-drop on unknown tags** to an explicit `UnknownTagSkipped(tag_name, position)` Sögumiðla event. The orchestrator can read the event stream to detect "LLM is trying tags the avatar cannot do" and refine the system prompt.
- The **string-prefix dispatch** to a `tag_handlers: dict[str, TagHandler]` registry. Adding a fifth tag is a `register_tag_handler("@mood:", MoodHandler)` call, not an edit to ModelController.
- The **face-style-TTS-style implicit coupling** to an explicit `face_to_tts_style_map: dict[str, str]` per-realm config. CDK's unification by string-match is fragile; Ember's explicit map is auditable.
- The **`[pause:N]` unvalidated value** to a clamped `[0, 10]` range. Out-of-range emits `PauseClamped` event.
- The **`idlingFrameThreshold = 2` Unity-frame-based debounce** to an asyncio event-based one: `await dialog_idling.wait(); await asyncio.sleep(0.1); dequeue()`. The 100ms debounce serves the same purpose; the implementation is idiomatic Python.

**Avoid:**
- **Unknown tag silent drops.** Ember's tag parser is closed-set with explicit error events.
- **`Debug.LogWarning` for unregistered animations.** Ember emits typed `UnregisteredAnimation(name)` event; the post-mortem reviewer can list all unhonoured animations across a session.
- **Tag vocabulary that requires source edits to extend.** Ember's tag registry is runtime-extensible.
- **Implicit ActionHistoryRecorder as the only audit trail.** Ember's Sögumiðla stream captures every animation/face/voice queue mutation by default.

**Invent:**
- **The Tag Negotiation Vow.** Before the LLM's first turn in each session, Ember sends the LLM a *capability declaration* listing every registered face/anim/tag/pause-range. The system prompt is auto-augmented with the declaration. The LLM cannot emit a tag the avatar cannot honour because the LLM does not know any tags except those declared. CDK has no such handshake; users hand-write the available-animations list in their prompt.
- **The Tag Round-Trip Provenance.** Every emitted tag is captured: `TagEmittedByLLM(turn_id, position, tag_name, tag_value)`. Every honoured tag is captured: `TagHonoured(tag_name, animation_id_or_face_id)`. Every dropped tag is captured: `TagDropped(reason: UnregisteredAnim | UnknownTagType | InvalidPauseValue)`. The session post-mortem can ask: of the 47 tags the LLM emitted, how many were honoured?
- **The Multi-Modal Frame.** Ember's `EmbodimentFrame` extends CDK's three-list with a fourth: `gestures: list[GestureRequest]` for non-animation embodied actions (look-at-camera, head-nod-on-yes). Hjarta-side observability of "what should the avatar do beyond animation" — extensible without breaking the three-list base.
- **The Frame-Latency Budget.** Each frame's dispatch is timed. If face-to-voice-start exceeds 100ms, emit `FrameLatencyBudgetMissed(frame_id, latency_ms, breakdown)`. The user can see which frames felt laggy. CDK has no timing observability; Ember's frames are auditable.
- **The Tag-Aware TTS Routing.** When the `[face:Joy]` tag fires, the TTS request *includes* the face as a typed `EmotionVector`, not just a `style` string. Providers that support emotion vectors (StyleBertVits2) get richer input; providers that don't (Google TTS) fall back to a style-name lookup. Same source-of-truth, different per-provider mappings.
- **The Pause-As-First-Class-Frame.** `[pause:0.5]` is currently a `preGap` field on the next voice. Ember promotes pauses to their own frame type: `PauseFrame(duration)` with its own animation/face semantics (e.g., a thoughtful-pose animation by default). The pause is a *moment of held expression*, not just silence.
- **The Speech-Animation Sync Vow.** Ember can configure per-realm whether animation is *speech-anchored* (CDK default: face/anim launch with voice play) or *pre-anchored* (face/anim launch 300ms *before* voice). The latter looks more like a human's "preparing to speak" beat. Per-realm tunable; default speech-anchored to match CDK.

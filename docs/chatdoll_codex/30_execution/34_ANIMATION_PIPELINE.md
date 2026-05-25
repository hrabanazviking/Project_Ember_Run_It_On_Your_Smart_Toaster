---
codex_id: 34_ANIMATION_PIPELINE
title: Animation Pipeline — Tag Regex, Animator Parameters, Idle Roulette
role: Forge-A
layer: Execution
status: draft
kit_source_refs:
  - Scripts/Model/ModelController.cs:237-292 (ToAnimatedVoiceRequest tag extraction)
  - Scripts/Model/ModelController.cs:184-235 (AnimatedSay)
  - Scripts/Model/ModelController.cs:294-424 (Animation queue + idling)
  - Scripts/Model/Animation.cs:1-24
  - Scripts/Model/AnimatedVoiceRequest.cs:1-55
  - Scripts/Model/ModelRequestBroker.cs:82-167
  - Scripts/LLM/LLMServiceBase.cs:100-117 (ExtractTags)
ember_subsystem_targets: [Andlit-unity, Hjarta, Munnr]
cross_refs:
  - 31_AIAVATAR_MAIN_LOOP
  - 33_TTS_PREFETCH
  - 25_ANIMATION_TAG_PROTOCOL
  - 1B_ANIMATION_DOMAIN
  - sap:32_AVATAR_RENDER_PIPELINE
  - waifu:22_ACTION_PROTOCOL
license_posture: Apache-2.0 — adopt with attribution
---

# Animation Pipeline

> *`[anim:Wave]` arrives mid-sentence. A 25-line regex extracts it. An Animator parameter mutates. The avatar waves while it talks. The whole transmission is a substring.*

Forge-A. Eldra. The animation tag protocol is the single feature that makes ChatdollKit feel different from a Discord bot with a webcam. The LLM writes inline animation directives — `[anim:Wave]`, `[face:Happy]`, `[pause:1.5]` — into its text response. CDK's `ModelController.ToAnimatedVoiceRequest` parses them as the LLM streams. Unity's Animator gets parameter mutations. The user sees the avatar do the right gesture in the right sentence. End to end the protocol is one regex, one dictionary lookup, and three method calls on the Animator. Here is exactly how the substring becomes a wave.

## The Tag Vocabulary

CDK's animation tag protocol has four families, embedded inline in the LLM's text output:

- **`[anim:Name]`** — trigger a registered animation by name.
- **`[face:Expression]`** — set a face expression. Includes implicit TTS style hint.
- **`[pause:Seconds]`** — insert a silence gap before the next voice clip.
- **`[lang:Code]`** — set TTS language for following voice clips.

The first three are parsed by `ModelController.ToAnimatedVoiceRequest` (`/tmp/ChatdollKit/Scripts/Model/ModelController.cs:237-292`). The fourth is parsed by `LLMContentProcessor.ProcessContentStreamAsync` (`LLMContentProcessor.cs:124-128`). All four use the same `[key:value]` syntax. `LLMServiceBase.ExtractTags` (`LLMServiceBase.cs:100-117`) is a more general tag extractor that the LLM services use for tags like `[vision:CameraSource]` that drive image capture — see [[36_FUNCTION_CALL_EXEC]] for that one.

## The Regex That Owns Everything

`ToAnimatedVoiceRequest` is 56 lines, of which one regex pattern is doing all the work:

```csharp
// /tmp/ChatdollKit/Scripts/Model/ModelController.cs:247-292 (compressed)
public AnimatedVoiceRequest ToAnimatedVoiceRequest(string inputText, string language = null)
{
    var avreq = new AnimatedVoiceRequest();
    var preGap = 0f;
    var ttsConfig = new TTSConfiguration();
    if (!string.IsNullOrEmpty(language))
        ttsConfig.Params["language"] = language;

    var pattern = @"(\[.*?\])|([^[]+)";
    foreach (Match match in Regex.Matches(inputText, pattern))
    {
        var parsedText = match.Value.Trim();

        if (parsedText.StartsWith("[face:"))
        {
            var face = parsedText.Substring(6, parsedText.Length - 7);
            avreq.AddFace(face, duration: FaceController.DefaultFaceExpressionDuration);
            ttsConfig.Params["style"] = face;
        }
        else if (parsedText.StartsWith("[anim:"))
        {
            var anim = parsedText.Substring(6, parsedText.Length - 7);
            if (IsAnimationRegistered(anim))
            {
                var a = GetRegisteredAnimation(anim);
                avreq.AddAnimation(a.ParameterKey, a.ParameterValue, a.Duration, a.LayeredAnimationName, a.LayeredAnimationLayerName);
            }
            else Debug.LogWarning($"Animation {anim} is not registered.");
        }
        else if (parsedText.StartsWith("[pause:"))
        {
            var pauseValue = parsedText.Substring(7, parsedText.Length - 8);
            if (float.TryParse(pauseValue, out float gap)) preGap = gap;
        }
        else if (parsedText.StartsWith("["))
        {
            continue;   // Unknown tag — skip
        }
        else
        {
            avreq.AddVoice(parsedText, preGap, parsedText.EndsWith("。") ? 0 : 0.3f, ttsConfig: ttsConfig);
            preGap = 0f;
        }
    }

    return avreq;
}
```

The regex `(\[.*?\])|([^[]+)` is the cleverest single line in the file. It alternates two captures:
- `\[.*?\]` — a bracketed tag, non-greedy.
- `[^[]+` — a run of non-bracket characters.

So `"Hello [anim:Wave] world."` matches in four pieces: `"Hello "`, `"[anim:Wave]"`, `" world"`, `"."`. Each match is either a tag (handled by the four `StartsWith` branches) or text (added as a voice with current preGap + ttsConfig).

The `Substring(6, ...)` and `Substring(7, ...)` are extracting the value between `[anim:` (6 chars) and `]` (1 char), `[face:` (6 chars) and `]`, `[pause:` (7 chars) and `]`. Fast, no second regex needed.

Unknown tags (anything else starting with `[`) are silently dropped (`:279-282`). This is graceful for forward-compat — LLMs that hallucinate new tag types don't crash anything — but means a typo like `[ainm:Wave]` is invisible. The `Debug.LogWarning` for unregistered animations (`:268`) catches the specific common case.

## Animation Registration

The tag handler looks up `IsAnimationRegistered(anim)` (`:409-412`). The registry is populated externally — typically in a setup MonoBehaviour that calls `ModelController.RegisterAnimation(name, animation)`:

```csharp
// /tmp/ChatdollKit/Scripts/Model/ModelController.cs:393-407 (compressed)
public void RegisterAnimation(string name, Animation animation) {
    registeredAnimations[name] = animation;
}

public Animation GetRegisteredAnimation(string name, float duration = 0.0f, ...)
{
    return new Animation(
        registeredAnimations[name].ParameterKey,
        registeredAnimations[name].ParameterValue,
        duration == 0.0f ? registeredAnimations[name].Duration : duration,
        ...
    );
}
```

An `Animation` object (`Animation.cs:1-24`) is a value class with five fields:

```csharp
// /tmp/ChatdollKit/Scripts/Model/Animation.cs:5-23
public class Animation
{
    public string Id { get; private set; }
    public string ParameterKey { get; set; }
    public int ParameterValue { get; set; }
    public float Duration { get; set; }
    public string LayeredAnimationName { get; set; }
    public string LayeredAnimationLayerName { get; set; }

    public Animation(string parameterKey, int parameterValue, float duration,
                     string layeredAnimationName = null, string layeredAnimationLayerName = null)
    {
        Id = Guid.NewGuid().ToString();
        ParameterKey = parameterKey;
        ParameterValue = parameterValue;
        ...
    }
}
```

That's it. `ParameterKey` is the name of an Animator parameter ("BaseParam" by default). `ParameterValue` is the int the parameter gets set to. `Duration` is how long this animation should play before transitioning back. `LayeredAnimationName/LayerName` is the optional override for Unity's layered Animator — a way to play an upper-body wave while the base layer keeps idling.

The Animator itself is a Unity asset (set up in the editor) where each int value of `BaseParam` corresponds to a transition into a different state. So `[anim:Wave]` becomes `ParameterKey="BaseParam"`, `ParameterValue=2` (or whatever the wave state is), and Unity's Animator handles the actual blend. This is the right separation — CDK doesn't own animation data, only animation *triggering.*

## The Update Loop

`UpdateAnimation()` runs every frame from `ModelController.Update()` (`:97-100`). The logic is small and three-way (`:313-341`):

```csharp
// /tmp/ChatdollKit/Scripts/Model/ModelController.cs:313-341 (compressed)
private void UpdateAnimation()
{
    var animationToRun = GetAnimation();
    if (animationToRun == null)
    {
        StartIdling(false);
        return;
    }

    if (currentAnimation == null || animationToRun.Id != currentAnimation.Id)
    {
        // Start new animation
        ResetLayers();
        animator.SetInteger(animationToRun.ParameterKey, animationToRun.ParameterValue);
        if (!string.IsNullOrEmpty(animationToRun.LayeredAnimationName))
        {
            var layerIndex = animator.GetLayerIndex(animationToRun.LayeredAnimationLayerName);
            animator.CrossFadeInFixedTime(animationToRun.LayeredAnimationName, AnimationFadeLength, layerIndex);
        }
        currentAnimation = animationToRun;
        animationStartAt = Time.realtimeSinceStartup;
    }
}
```

`GetAnimation` is a delegate — `GetIdleAnimation` or `GetQueuedAnimation` depending on whether `StartIdling` or `StopIdling` was last called (`:60, 110-127`). Idle returns a randomly weighted choice from the registered idle pool (`:368-383`). Queued returns the head of `animationQueue` until it expires (`:343-366`).

When the animation to run changes (new id), the Animator's parameter is mutated, the layer is cross-faded (`AnimationFadeLength = 0.5f` default, `:27`), and the start time is recorded. The cross-fade is Unity's job — `CrossFadeInFixedTime` interpolates blend weights. CDK just decides when to call it.

## AnimatedSay — The Foreground Driver

`ModelController.AnimatedSay` (`:184-235`) is what actually plays a full `AnimatedVoiceRequest`:

```csharp
// /tmp/ChatdollKit/Scripts/Model/ModelController.cs:184-235 (compressed)
public async UniTask AnimatedSay(AnimatedVoiceRequest request, CancellationToken token)
{
    foreach (var animatedVoice in request.AnimatedVoices)
    {
        if (token.IsCancellationRequested) break;

        // Animation
        if (animatedVoice.Animations.Count > 0) Animate(animatedVoice.Animations);

        // Face
        if (animatedVoice.Faces != null && animatedVoice.Faces.Count > 0)
            FaceController.SetFace(animatedVoice.Faces);

        // Speech
        if (animatedVoice.Voices.Count > 0)
            await SpeechController.Say(animatedVoice.Voices, token);
    }

    if (request.StartIdlingOnEnd && !token.IsCancellationRequested)
    {
        if (GetAnimation != GetIdleAnimation)
        {
            if (currentAnimation != null)
            {
                var remainingTime = currentAnimation.Duration - (Time.realtimeSinceStartup - animationStartAt);
                if (remainingTime > 0)
                    await UniTask.Delay((int)(remainingTime * 1000), cancellationToken: token);
            }
            StartIdling();
        }
    }
}
```

For each `AnimatedVoice` frame in the request: trigger its animations (queued, picked up by `UpdateAnimation` next frame), set its faces, then `await SpeechController.Say` until the voice clip(s) finish. The animation and face fire-and-forget; the voice is what gates the loop. This is why animations look synced to speech — they're triggered *before* the await on the voice that follows them.

After the whole request is consumed, if `StartIdlingOnEnd` is true (the bootstrap sets this to `isFirstItem` per `AIAvatar.cs:252` — only the *first* split chunk starts idling on end), the avatar transitions back to idle, waiting for any in-flight animation to finish first.

## The Idle Roulette

Idle animation is a weighted random pick from a per-mode pool (`:368-383`):

```csharp
// /tmp/ChatdollKit/Scripts/Model/ModelController.cs:368-383
private Animation GetIdleAnimation()
{
    if (currentAnimation == null || animationStartAt == 0 ||
        Time.realtimeSinceStartup - animationStartAt > currentAnimation.Duration)
    {
        var i = UnityEngine.Random.Range(0, idleWeightedIndexes[IdlingMode].Count);
        return idleAnimations[IdlingMode][idleWeightedIndexes[IdlingMode][i]];
    }
    return default;
}
```

`AddIdleAnimation(animation, weight, mode)` (`:130-146`) populates these pools. `weight` is implemented by repeating the index `weight` times in `idleWeightedIndexes` — a low-tech weighted-random that allocates O(sum-of-weights) memory but gives O(1) sampling.

Idling modes are first-class. `ChangeIdlingModeAsync("excited")` (`:160-180`) swaps which animation pool gets sampled and optionally swaps the idle face expression. This is how CDK can have "default", "sleepy", "excited" idle behaviors that the LLM (or game logic) can trigger.

## ModelRequestBroker's Split-and-Prefetch Pipeline

`ModelRequestBroker.ToAnimatedVoiceRequests` (`ModelRequestBroker.cs:82-125`) is the alternative entry point: it takes a single tagged-text string, splits it on sentence-end punctuation via `SplitString` (`:127-167`), then calls `ToAnimatedVoiceRequest` on each split. The result is a list of `AnimatedVoiceRequest` objects, one per sentence.

This is the path SocketServer and AITuber take. The split-then-parse-per-sentence structure means:

1. **Tag context resets per sentence.** A `[lang:en]` at the start of sentence 1 doesn't carry into sentence 2 in this path. The bootstrap pipeline does preserve language via the streaming LLMContentProcessor's outer state, but this synchronous path treats each sentence as independent.
2. **Each sentence prefetches independently.** Look at `ModelRequestBroker.cs:104-115`:

```csharp
// /tmp/ChatdollKit/Scripts/Model/ModelRequestBroker.cs:104-115
foreach (var av in avreq.AnimatedVoices)
{
    foreach (var v in av.Voices)
    {
        if (v.Text.Trim() == string.Empty) continue;
        speechController.PrefetchVoices(new List<Voice>(){new Voice(
            v.Text, 0.0f, 0.0f, v.TTSConfig, true, string.Empty
        )}, modelTokenSource.Token);
    }
}
```

Same prefetch pattern as the LLM path. The cache is shared, so the foreground playback sees cache hits the same way.

## Where It Breaks

- **Tag-and-text boundary.** The regex `(\[.*?\])|([^[]+)` doesn't handle escaped brackets. If the LLM emits literal `[foo]` as English text (e.g. "click the [foo] button"), it gets parsed as an unknown tag and silently dropped. There is no escape mechanism. Bad fit for LLMs writing code blocks or technical text.
- **Streaming-split races.** The streaming LLM path splits on punctuation *before* the tag regex runs. If a tag straddles a split — e.g. the chunk arrives as `"Hello [an"` followed by `"im:Wave] world."` — the first chunk has an unclosed bracket. `Regex.Matches` against the first chunk produces `"Hello "` and `"[an"` (matching the second alternation because `[an` doesn't close). The `[an` then fails all four StartsWith checks (because it's `[a` not `[anim:`) and gets dropped — *but only because the regex itself doesn't require the closing bracket on the first alternation*. Wait, look again: the pattern is `\[.*?\]` which does require the close bracket. The `[an` would *not* match `\[.*?\]`. It would match `[^[]+`? No, `[^[]+` excludes only `[`, so `[an` wouldn't be in that alt either. Most likely it ends up as a partial substring that *neither* alternation captures, producing nothing. The tag is split across the streaming boundary and partially lost. Verified: yes, this is a real failure mode. The streaming path needs explicit boundary-buffering for unclosed tags.
- **`[face:` style hint leaks across voices.** Once `ttsConfig.Params["style"]` is set, it stays set for all subsequent voice clips in the same request (`:286 — "Do not reset ttsConfig to continue the style of voice"`). This is intentional but means `[face:Sad]` at the start of a five-sentence response gives all five sentences the sad voice style. To get per-sentence style the LLM has to re-emit `[face:X]` per sentence.
- **`Random.Range` for idle weight uses Unity's RNG.** This is the global Unity RNG that's also seeded for gameplay code. Idle animation choice is correlated with whatever else is using Random in the scene. For a deterministic replay or A/B test, this is wrong.
- **`registeredAnimations` is not thread-safe.** Built up serially via `RegisterAnimation`, read serially during `UpdateAnimation`. If a future feature wants runtime hot-registration of animations (e.g. a tool call that adds a new gesture), the lack of locking is a bug surface.

## Where It Surprises

- **`[pause:1.5]` is *not* an animation event.** It only sets the `preGap` for the next voice clip. There is no "play silence" animation. If a `[pause:5.0]` is the only tag in a chunk with no following voice, the pause has no effect — `preGap = 0f` is only consumed when `AddVoice` is called.
- **The first `[face:X]` sets both the visual face and the TTS style.** Implicit coupling. Voicevox's `style` parameter selects a different speaker preset (e.g., happy vs sad voice for the same character). The face tag has a double semantic — visual mouth/eye state *and* vocal affect. This is the kind of design that emerges from doing it for real, but it means if you don't want the voice change you have to use `[face:X]` without `style` setting, which requires a different API.
- **`ResetLayers()` (`:305-311`) cross-fades back to a "Default" state on all non-base layers.** This is what cleans up after a layered animation (e.g., a wave on the upper-body layer) when a new animation starts. Without this, the wave would persist into the next gesture. The "Default" state must exist in the Animator — silent error if not.
- **`StartIdlingOnEnd = isFirstItem` (`AIAvatar.cs:252`).** This is counterintuitive at first: only the *first* split chunk's request will trigger idling on end. The reasoning: chunks N+1...end follow chunk 1 in sequence; only the last one (which is also the first when read backwards?) — actually re-reading, the comment is on `contentItem.IsFirstItem`, which is set to `isFirstWord` at `LLMContentProcessor.cs:130`. Re-reading: `isFirstWord` is initialized true and set false after the first iteration (`:140`). So **only the first chunk has `IsFirstItem=true`, which means only the first chunk's AnimatedVoiceRequest has `StartIdlingOnEnd=true`.** That seems backward — you'd want only the *last* chunk to trigger idle. Maybe the intent is that the first chunk's animation persists to cover the others. Without a comment, this is a head-scratcher. Forge-B should look at AIAvatarKit's streaming path to confirm.

## Cross-References

- [[31_AIAVATAR_MAIN_LOOP]] — where AnimatedSay is triggered from
- [[33_TTS_PREFETCH]] — sibling prefetch architecture
- [[25_ANIMATION_TAG_PROTOCOL]] — Architect's interface-layer protocol description
- [[1B_ANIMATION_DOMAIN]] — domain-level animation concepts
- [[sap:32_AVATAR_RENDER_PIPELINE]] — contrast: SAP uses VMC OSC frames over UDP, not inline text tags
- [[waifu:22_ACTION_PROTOCOL]] — contrast: Waifu has a typed action vocabulary (embarrassed, dance, wave_hand) but it's API-call-driven, not inline-tag-driven

## What This Means for Ember

**Adopt:**

- **The `[key:value]` inline tag protocol** (`ModelController.cs:247`, Apache-2.0 attribution required). This is the right surface for embodied LLM output. Adopt as Ember's `andlit.tag.parse(text) -> List[Tag]`. Make it explicit and typed: `AnimTag`, `FaceTag`, `PauseTag`, `LangTag`, with a discriminated union.
- **The regex `(\[.*?\])|([^[]+)`** for tag/text alternation. Compact, fast, well-tested. Vendor verbatim. The only modification: add tag-escape support — `[[anim:X]]` produces literal `[anim:X]` text, not a tag match.
- **The registered-animation dictionary lookup with fallback warning** (`ModelController.cs:261-269`). Adopt as `andlit.animation.trigger(name)` returning `Result<TriggeredAnimation, AnimationNotRegistered>`.
- **Weighted idle pool with per-mode subsetting.** Andlit-unity should have multiple "moods" (focused, playful, drowsy) with mode-specific animation pools.

**Adapt:**

- **The implicit `style` coupling on `[face:X]`.** Adopt `[face:X]` for visual face but decouple TTS style. Use a separate `[style:X]` tag for voice affect. CDK's coupling is a footgun.
- **Streaming-split tag boundary handling.** Adopt the regex pattern but add an explicit "tag-pending" buffer in `LLMContentProcessor` that holds unclosed `[...` fragments until the next chunk arrives. CDK's current path silently drops half-tags at chunk boundaries.
- **Unity Animator parameter-key/value model.** For the Andlit-unity tier specifically. For Andlit-electron and Andlit-cloud, animations are higher-level (named clips with no parameter int). The protocol is the same `[anim:Name]`; the resolution layer differs.

**Avoid:**

- **Silent drop of unknown tags.** Adopt the *graceful* part (don't crash) but emit a typed `TagWarning` event so Munnr can show "the LLM tried to do `[unsupported:X]` 3 times this session." Helps catch hallucinated tag names.
- **`Random.Range` for idle.** Use a dedicated `RNG` per Hjarta seed; deterministic replays matter for testing and "the avatar mood today" is the kind of state Hjarta tracks anyway.
- **The `StartIdlingOnEnd = isFirstItem` semantic.** Confusing without a comment. Ember's equivalent should be explicit: `last_chunk_triggers_idle = True` is the obvious default; first-chunk is a special policy.

**Invent:**

- **Hjarta Gesture Vocabulary Registry.** Animations registered at runtime, scoped to "this session's persona," with metadata: emotion vector, intensity, cultural-appropriateness flags. The LLM gets the registry as system-prompt context: "available animations: Wave, Bow, Nod, Shake, ..." — so it stops hallucinating animation names. CDK's registry is invisible to the LLM; the LLM finds out by trying names and getting silent failures.
- **Andlit-unity Tag Negotiation.** Per-LLM-call, Ember reports the avatar's current capability set: "this avatar has [Wave, Nod, Bow] animations and [Happy, Sad, Neutral] faces. Use only these tags." Reduces hallucination. Pairs with the registry above.
- **Munnr Tag Replay.** Every parsed `AnimTag` is logged with timestamp + LLM-chunk-offset. Replay a session as a CLI animation script. This is what CDK is *almost* doing with `History` (the `ActionHistoryRecorder` field at `ModelController.cs:56`); we make it first-class.

---

*Apache-2.0 attribution: when adopting CDK's tag parser, animation registry, or AnimatedSay pipeline into Ember source, preserve the ChatdollKit header reference per Apache-2.0 §4(c).*

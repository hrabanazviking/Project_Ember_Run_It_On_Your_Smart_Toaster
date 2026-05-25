---
codex_id: 25_ANIMATION_TAG_PROTOCOL
title: Animation Tag Protocol — Four Tags, One Regex, Two Parse Points
role: Architect
layer: Interface
status: draft
chatdoll_source_refs:
  - Scripts/Model/ModelController.cs:237-292
  - Scripts/LLM/LLMServiceBase.cs:100-117
  - Scripts/LLM/LLMContentProcessor.cs:124-141
  - Scripts/Model/AnimatedVoice.cs
  - Scripts/Model/AnimatedVoiceRequest.cs
  - Scripts/Model/Animation.cs
ember_subsystem_targets: [Andlit, Rödd, Munnr]
cross_refs:
  - 10_domain/1B_ANIMATION_DOMAIN
  - 10_domain/16_LLM_SERVICE_DOMAIN
  - 10_domain/12_MODEL_CONTROLLER_DOMAIN
  - sap:14_ANIMATION_VOCABULARY
  - waifu:20_ZEROWEIGHT_SURFACE
---

# Animation Tag Protocol
## Four Tags, One Regex, Two Parse Points

*— Rúnhild Svartdóttir, Architect*

> *Wire-format protocols are usually verbose because they must travel reliably. The animation tag protocol travels in the LLM's text stream — a high-volume, low-reliability medium where every byte costs latency. ChatdollKit's protocol is twenty bytes per tag at maximum. The brevity is the contract.*

The CDK animation tag protocol has four tag types, one regex, and two parse points. The protocol is in-band — embedded directly in the LLM's response text, parsed by the same pipeline that splits the text into sentences. This is the **tightest speech-expression coupling** in the three corpora. It is also the most brittle (silent drop on unknown tags). The protocol's specification follows.

The domain doc ([[1B_ANIMATION_DOMAIN]]) covered *how the system processes tags*. This doc covers *what the tags are* — the wire format, the grammar, the semantic constraints, the validation gaps. Treat this doc as the *spec* a downstream implementer would reference.

---

## 1. The Wire Format

### 1.1 The four tag types

| Tag | Wire form | Argument grammar | Effect target | Lifetime |
|---|---|---|---|---|
| `[face:X]` | `[face:Joy]` | Word characters (registered face name) | `FaceController` queue | Until next `[face:]` or `DefaultFaceExpressionDuration` (typically 7s) |
| `[anim:X]` | `[anim:Wave]` | Word characters (registered animation name) | `ModelController` animation queue | `Animation.Duration` field (per-registration) |
| `[pause:N]` | `[pause:0.5]` | Float (seconds) | Pre-gap on the *next* voice clip | One-shot |
| `[lang:X]` | `[lang:ja-JP]` | BCP-47 language tag (regex: `[a-zA-Z-]+`) | `TTSConfiguration.Params["language"]` for subsequent voice clips | Sticky until next `[lang:]` |

**Grammar in EBNF**:

```
tag         = "[" tag-type ":" tag-arg "]"
tag-type    = "face" | "anim" | "pause" | "lang"
tag-arg     = word | float | bcp47
word        = letter, { letter | digit | "_" }
float       = digit, { digit }, [ ".", digit, { digit } ]
bcp47       = letter, { letter | "-" }
```

The protocol is **case-sensitive**. `[Face:Joy]` is *not* recognised by the parser; the `StartsWith("[face:")` checks are exact-match. The argument is **stripped of leading/trailing whitespace** by `.Trim()` (`ModelController.cs:250`) but internal whitespace is *not* allowed in `word`-type args (would break the regex's tag-end detection).

### 1.2 The regex

`Scripts/Model/ModelController.cs:247`:

```csharp
var pattern = @"(\[.*?\])|([^[]+)";
```

The regex matches either:
- **Group 1**: `\[.*?\]` — a non-greedy bracketed sequence. *Any* characters between `[` and the first `]`. No nesting.
- **Group 2**: `[^[]+` — one or more non-`[` characters. A run of plain text.

Every character of the input is in exactly one match. The split is deterministic.

**Edge cases the regex handles correctly**:
- `[]` — matched as Group 1; the StartsWith checks fail; silently dropped.
- `[unknown:value]` — matched as Group 1; the StartsWith checks fail; silently dropped (the unknown-tag silent-drop is the protocol's behaviour, not the regex's).
- `Hello [face:Joy] world` — three matches: `Hello ` (text), `[face:Joy]` (tag), ` world` (text).
- `[face:Joy][anim:Wave]` — two consecutive tag matches; no text in between.

**Edge cases the regex handles ambiguously**:
- `[face:[invalid]]` — non-greedy match captures `[face:[invalid]` (up to first `]`); the `:` check succeeds; argument `face:[invalid` is parsed; `face` is treated as the tag type; the argument is `[invalid`. Likely silently fails downstream. The protocol assumes the LLM does not emit nested brackets.
- `Hello] world` — `]` is in Group 2 (the non-`[` run). No tag interpretation. Acceptable.

### 1.3 The processing branches

`Scripts/Model/ModelController.cs:250-282`:

```csharp
var parsedText = match.Value.Trim();

if (parsedText.StartsWith("[face:")) {
    var face = parsedText.Substring(6, parsedText.Length - 7);
    avreq.AddFace(face, duration: FaceController.DefaultFaceExpressionDuration);
    ttsConfig.Params["style"] = face;
}
else if (parsedText.StartsWith("[anim:")) {
    var anim = parsedText.Substring(6, parsedText.Length - 7);
    if (IsAnimationRegistered(anim)) {
        var a = GetRegisteredAnimation(anim);
        avreq.AddAnimation(...);
    } else {
        Debug.LogWarning($"Animation {anim} is not registered.");
    }
}
else if (parsedText.StartsWith("[pause:")) {
    var pauseValue = parsedText.Substring(7, parsedText.Length - 8);
    if (float.TryParse(pauseValue, out float gap)) preGap = gap;
}
else if (parsedText.StartsWith("[")) {
    continue;  // Silent drop unknown tag
}
else {
    avreq.AddVoice(parsedText, preGap, ...);
    preGap = 0f;
}
```

Substring arithmetic: `[face:X]` is 7+ chars; `parsedText.Substring(6, parsedText.Length - 7)` extracts everything between `[face:` (6 chars) and the trailing `]`. Brittle to whitespace variations but functional for the exact-match protocol.

**The four tag prefixes are hardcoded** as `StartsWith` checks. Adding a fifth is a source edit.

### 1.4 The two parse points

The protocol is parsed in **two places** at different timings:

**Parse point A — `LLMServiceBase.ExtractTags`** (`Scripts/LLM/LLMServiceBase.cs:100-117`):

```csharp
var tagPattern = @"\[(\w+):([^\]]+)\]";
var matches = Regex.Matches(text, tagPattern);
var result = new Dictionary<string, string>();
foreach (Match match in matches) {
    if (match.Groups.Count == 3) {
        result[match.Groups[1].Value] = match.Groups[2].Value;
    }
}
return result;
```

Different regex; *all* tags as key/value bag. Called *once after streaming completes* (e.g., `ChatGPTService.cs:347-351`):

```csharp
var extractedTags = ExtractTags(chatGPTSession.CurrentStreamBuffer);
if (extractedTags.Count > 0 && HandleExtractedTags != null) {
    HandleExtractedTags(extractedTags, chatGPTSession);
}
```

This is for *flag-like* tags — `[vision:camera]` triggers image capture; the flag is "did vision appear at all?", not "where in the text was it?" AIAvatar's `HandleExtractedTags` handler routes these.

**Parse point B — `ModelController.ToAnimatedVoiceRequest`** (the protocol grammar above):

The positional split-and-process pass. Called per-sentence by `LLMContentProcessor`'s sentence stream.

**The two parse points serve different needs.** Point A: "did any tag of this kind appear?" Point B: "what is the *position* of each tag, and what voice clip does it associate with?" The same tag (`[face:Joy]`) is processed by both — Point A puts it in the key/value dict (potentially used for global session state); Point B uses it to construct the per-sentence animated voice frame.

**The `[lang:]` tag is also extracted at parse point C** — inside `LLMContentProcessor.ProcessContentStreamAsync` (`Scripts/LLM/LLMContentProcessor.cs:124-128`):

```csharp
var match = Regex.Match(processedText, @"\[lang:([a-zA-Z-]+)\]");
if (match.Success) language = match.Groups[1].Value;
var contentItem = new LLMContentItem(processedText, isFirstWord, language);
```

Here it is extracted *for state propagation* (the language state flows downstream to TTS), not for queue mutation. Three parse points total, each for a different temporal need.

### 1.5 The protocol-data structures

`AnimatedVoiceRequest` (`Scripts/Model/AnimatedVoiceRequest.cs`) and `AnimatedVoice` (`Scripts/Model/AnimatedVoice.cs`) are the output of Point B:

```
AnimatedVoiceRequest {
    AnimatedVoices: List<AnimatedVoice>,
    StartIdlingOnEnd: bool
}

AnimatedVoice {
    Animations: List<Animation>,   // populated by [anim:]
    Faces: List<FaceExpression>,   // populated by [face:]
    Voices: List<Voice>            // populated by plain text
}

Animation { ParameterKey, ParameterValue, Duration, LayeredAnimationName, LayeredAnimationLayerName }
FaceExpression { Name, Duration }
Voice { Text, PreGap, PostGap, TTSConfig, ... }
```

A *frame* (`AnimatedVoice`) bundles the tags that *precede* a voice clip. `[face:Joy][anim:Wave] Hello.` → one frame with Faces=[Joy], Animations=[Wave], Voices=[Hello]. The next sentence is the next frame.

---

## 2. The Semantic Contract

### 2.1 Face-tag semantics

`[face:Joy]` does **three** things simultaneously:

1. **Adds a FaceExpression to the frame's `Faces` list** with `Name="Joy"`, duration=default. Pushed to FaceController's queue.
2. **Sets `ttsConfig.Params["style"] = "Joy"`** — the *style* parameter the TTS provider will receive. If the TTS supports a "Joy" style, it speaks joyfully.
3. **Persists `ttsConfig` to subsequent voices in the same `AnimatedVoiceRequest`** (line 286 comment: *"Do not reset ttsConfig to continue the style of voice"*).

**The face name and the TTS style name are unified by string match.** The expressivity *quietly leaks* into voice synthesis. This is **a feature** (one tag controls both visual and auditory affect) and **a bug** (the face vocabulary and TTS style vocabulary may diverge per provider). The Auditor catalogues at [[54_MULTI_TTS_QUALITY]].

If the LLM emits `[face:Joy]` and:
- The FaceController has a registered `"Joy"` expression and the TTS has a `"Joy"` style → both fire correctly.
- The FaceController has `"Joy"` but TTS has no style → face fires; voice uses default style.
- Neither registered → face is silently *added* to the queue with `Name="Joy"` (no validation that the name is registered); TTS uses default. The face will be a no-op at activation.

For Ember: explicit `face_to_tts_style_map: dict[str, str]` per realm. The map is a config; the tag name is a face name; the map decides what style (if any) routes to TTS.

### 2.2 Anim-tag semantics

`[anim:Wave]` adds an animation to the frame's `Animations` list **only if registered**:

```csharp
if (IsAnimationRegistered(anim)) {
    var a = GetRegisteredAnimation(anim);
    avreq.AddAnimation(a.ParameterKey, a.ParameterValue, a.Duration, ...);
} else {
    Debug.LogWarning($"Animation {anim} is not registered.");
}
```

Unregistered → `Debug.LogWarning`. Logged to the Unity console (visible to developers running in Editor or attached to a build's debug logs); **invisible to end users**. The LLM emits a tag the avatar cannot honour; the user sees nothing. Silent failure.

Animation duration is **per-registration**, not per-tag. The LLM cannot say "wave for 3 seconds" via tags. The registration is editor-time on the prefab. To extend, the user adds a registration entry; to vary the duration, the user creates two registrations (`WaveShort`, `WaveLong`).

For Ember: emit `UnregisteredAnimation(name, position)` Sögumiðla event so the orchestrator can surface to a post-mortem reviewer.

### 2.3 Pause-tag semantics

`[pause:0.5]` sets `preGap = 0.5f` *for the next voice clip*. The pause is **per-frame**, not per-tag-emission. If the LLM emits two `[pause:]` tags before one voice clip, the second one overwrites:

```
[pause:1.0][pause:0.5] Hello.   →   preGap=0.5 on the Hello clip
```

The pause is **reset to 0 after one voice clip**. The next sentence starts unaffected:

```
[pause:0.5] Hello. World.   →   "Hello" has preGap=0.5; "World" has preGap=0
```

Negative values are accepted by `float.TryParse` but treated as 0 (Unity's audio source clamps). Values over 10 are accepted with no cap — the avatar will sit silent for that many seconds. Ember should clamp `[0, 5]` with `PauseClamped` event on out-of-range.

### 2.4 Lang-tag semantics

`[lang:ja-JP]` is processed at parse point C (`LLMContentProcessor`) and at parse point B (`ModelController.ToAnimatedVoiceRequest(text, language)`'s second argument). The language string is set as `ttsConfig.Params["language"]` (line 244). Per-provider TTS interprets it (Google's `languageCode` field, Azure's locale, etc.).

**The language is sticky.** Once set, it persists for the rest of the response. To switch back, the LLM must emit another `[lang:]`. CDK does not auto-detect language from text content; the LLM-side prompt must instruct it to emit `[lang:]` tags before non-default-language segments.

The grammar admits BCP-47 codes (`[a-zA-Z-]+`). The TTS-provider's actual support varies. Unsupported codes → provider error or default voice. CDK does not validate against a provider-capability list.

---

## 3. The Protocol Negotiation Gap

### 3.1 No protocol versioning

The protocol has no version field. Adding a fifth tag type means *changing the source code* of the parser. Old prompts that emit unrecognised tags get silent-dropped. There is no way to say *"this prompt requires protocol v2"* or *"server, list your supported tags."*

### 3.2 No discovery mechanism

The LLM does not know which faces/animations are registered. The application-side prompt-engineer must hand-write the available-tag list in the system prompt. If the registered set changes (a new animation added in the Editor), the prompt must be updated by hand. No machinery enforces synchronisation.

CDK's documentation recommends a system prompt like *"You can use [face:X] where X is one of {Joy, Sad, Angry, ...}"*. Hand-maintained.

For Ember: the **Tag Negotiation Vow** ([[1B_ANIMATION_DOMAIN]] Invent). On session start, Ember sends the LLM a capability declaration listing every registered face/anim/tag. The system prompt is auto-augmented. The LLM cannot emit a tag the avatar cannot honour, because the LLM doesn't know any tags except those declared.

### 3.3 No error feedback to the LLM

Unregistered animations: `Debug.LogWarning` only. The LLM has no signal that its tag was ignored. Subsequent turns repeat the same unsupported tags. The feedback loop is broken.

For Ember: emit `UnknownTagEmittedByLLM(turn_id, tag_type, tag_arg)` Sögumiðla event. The orchestrator can choose to:
- Inject a corrective system message *next turn* (`The previous response used [anim:Quokka] which is not available. Available animations are {list}.`).
- Surface the unhonoured tags in the user-facing UI.
- Refuse to consume turns that emit unsupported tags above a threshold.

### 3.4 The face-and-style unification is implicit

A user reading CDK's docs sees `[face:X]` documented as "face expression." The TTS-style side effect is *not* documented; it is in code at `ModelController.cs:256`. New users discover it accidentally when their TTS provider speaks differently than expected. Ember should document the unification (and ideally make it opt-in via config).

---

## 4. Cross-References

- [[1B_ANIMATION_DOMAIN]] — the domain that consumes the protocol
- [[16_LLM_SERVICE_DOMAIN]] §2.2 — the upstream tag-extraction at `LLMServiceBase.ExtractTags`
- [[12_MODEL_CONTROLLER_DOMAIN]] — the queue consumers
- [[54_MULTI_TTS_QUALITY]] — Auditor's catalogue including the face-style unification
- [[sap:14_ANIMATION_VOCABULARY]] — SAP's `<happy>` out-of-band tags for contrast
- [[waifu:20_ZEROWEIGHT_SURFACE]] — Waifu's typed-string `runAction("dance")` for contrast

---

## What This Means for Ember

**Adopt:**
- The **inline-tag in-band protocol** as Ember's animation control surface. Tags travel with speech; the LLM emits them naturally; the parser splits text and tags in one pass. Apache-2.0 attribution required.
- The **regex pattern `r"(\[.*?\])|([^[]+)"`**. Direct lift to Python's `re.finditer`.
- The **`AnimatedVoiceRequest` / `AnimatedVoice` frame structure**. Ember's `EmbodimentFrame` mirrors with `animations`, `faces`, `voices`, `start_idling_on_end`.
- The **two-parse-point split** (key/value bag for flag tags; positional pass for queue tags). Different temporal needs; different parsers; same source.

*Apache-2.0 attribution: when patterns from `ChatdollKit/Scripts/Model/ModelController.cs` tag protocol are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:**
- The **silent drop on unknown tags** to explicit `UnknownTagEmittedByLLM(tag_type, tag_arg, position)` events.
- The **case-sensitive prefix match** to case-insensitive (`[Face:Joy]` works) with normalisation. Reduces a class of LLM-emitted-typo failures.
- The **hardcoded four-tag set** to a runtime `TagRegistry` with `register_tag(prefix, handler)` calls. Adding a fifth tag is a registration, not a source edit.
- The **implicit face-style unification** to explicit `face_to_tts_style_map: dict` configurable per-realm.

**Avoid:**
- **No protocol versioning.** Ember tags include a version (`[face/v2:Joy]` or session-level capability negotiation).
- **No LLM-side discovery.** Ember sends the available tags to the LLM at session start.
- **`Debug.LogWarning`-only error handling.** Ember emits typed events.
- **No pause clamping.** Ember caps `[pause:N]` to `[0, 5]`.

**Invent:**
- **The Tag Capability Declaration.** At session start, Ember sends the LLM a system-message block listing every registered face/anim/tag with its argument type and (where appropriate) the list of valid values. Hand-maintained prompts replaced by machine-generated capability blocks. CDK has no such mechanism.
- **The Tag Round-Trip Audit.** Every tag emitted by the LLM is captured as `TagEmittedByLLM(turn_id, position, tag_type, tag_arg)`. Every honoured tag fires `TagHonoured(...)`. Every dropped tag fires `TagDropped(reason)`. Post-session, the user can ask: of the 47 tags emitted, how many were honoured?
- **The Multi-Tag-Type Frame.** Beyond the four CDK tag types, Ember admits: `[gaze:Down]` (look-at-target), `[gesture:LookConcerned]` (cross-modal non-anim cue), `[memory_search:topic]` (LLM-triggered memory query), `[realm_switch:code-pair]` (LLM-requested context switch). Each is registered with a handler; extensibility is first-class.
- **The Tag Reliability Vow.** Tags that go to non-determinant queues (face, anim) execute exactly once even if duplicated in the stream. Tags that affect state (lang) take the latest value. Tags that affect timing (pause) accumulate or override based on per-tag policy. CDK has implicit, varied behaviour; Ember names it.
- **The Tag Cost Annotation.** Each tag has a `cost: int` (typical execution latency contribution in ms). The cost is reported in `TagHonoured` events. The orchestrator can refuse high-cost tag clusters on low-latency turns. CDK has no concept; Ember tracks.
- **The Tag-As-Side-Channel Vow.** Tags do not appear in the text the user *hears*; they are stripped from TTS input. But they appear in the *transcript* for accessibility (a hearing-impaired user reading the transcript sees `[joyful tone] Hello` rather than just `Hello`). Tags are observability for the user, not just for the avatar. CDK strips and discards; Ember preserves in the alternate channel.
- **The Wildcard Pattern Tag.** `[anim:any_wave]` matches any registered animation whose name starts with `wave_`. Reduces prompt brittleness ("the LLM doesn't have to know my exact animation name"). Each match emits `WildcardMatched(pattern, chosen)`. CDK requires exact-name registration; Ember admits patterns.

---
codex_id: 11_AIAVATAR_DOMAIN
title: AIAvatar Domain — The Coordinator That Knows Everyone's Phone Number
role: Architect
layer: Domain
status: draft
chatdoll_source_refs:
  - Scripts/AIAvatar.cs:1-664
  - Scripts/Dialog/DialogProcessor.cs:131-280
  - Scripts/Model/ModelController.cs:184-235
  - Scripts/Model/SpeechController.cs:13-30
  - Scripts/LLM/LLMContentProcessor.cs:29-161
  - Scripts/SpeechListener/MicrophoneManager.cs:130-168
  - Scripts/SpeechListener/SpeechListenerBase.cs:44-114
ember_subsystem_targets: [Funi, Strengr, Munnr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/13_DIALOG_PROCESSOR_DOMAIN
  - 10_domain/14_SPEECH_LISTENER_DOMAIN
  - 10_domain/15_SPEECH_SYNTHESIZER_DOMAIN
  - 10_domain/17_MICROPHONE_MANAGER_DOMAIN
  - sap:10_DOMAIN_MAP
  - waifu:10_DOMAIN_MAP
---

# AIAvatar Domain
## The Coordinator That Knows Everyone's Phone Number

*— Rúnhild Svartdóttir, Architect*

> *Every architecture eventually needs a hub. The question is whether the hub knows what it owns — or whether it pretends to be a domain. AIAvatar is honest about its role. It is also too big.*

`AIAvatar.cs` is the *only* file in ChatdollKit that violates the eight-clean-subsystem rule of [[10_DOMAIN_MAP]]. It is 664 lines, it imports five sibling namespaces (`Dialog`, `LLM`, `Model`, `SpeechListener`, `SpeechSynthesizer`), and it registers seventeen distinct lifecycle callbacks during its `Awake()`. It is, in CDK's structure, the coordinator — the file equivalent of a `main()` that grew tendrils.

The doc does three things: it names what AIAvatar owns (mode lifecycle, the wake/cancel/interrupt word vocabularies, mic-mute strategy selection, processing-presentation visuals); it catalogues what it merely *wires* (everything else); and it points to the architectural split Ember should make instead. This is the *first* place an Ember-bound reader meets the SAP-style anti-pattern in a far smaller form — and the place Ember decides whether to repeat it.

---

## 1. The Subject Itself

**What AIAvatar is:** the single-file *coordinator* of a CDK avatar's runtime. It is a `MonoBehaviour` (line 15: `public class AIAvatar : MonoBehaviour`), attached to the same GameObject that carries `DialogProcessor`, `ModelController`, `LLMContentProcessor`, `MicrophoneManager`, all the `ISpeechListener` implementations, all the `ISpeechSynthesizer` implementations, and all the `ITool`s. It is the *first* Unity component to wake up (via `Awake()`) and the one that *registers the callbacks* binding the eight subsystems together.

**What AIAvatar owns** (genuinely):
- The **AvatarMode** enum (lines 25-31): `Disabled / Sleep / Idle / Conversation`. Four states, one mode-timer (`modeTimer`, line 24), and the transition logic in `UpdateMode` (lines 393-424).
- The **wake/cancel/interrupt-word vocabularies** and their extraction logic (lines 66-69, 444-521). The wake-word extractor allows configurable prefix/suffix slop via the `WordWithAllowance` nested class (lines 656-662).
- The **MicrophoneMuteStrategy** selection (lines 54-62): `None / Threshold / Mute / StopDevice / StopListener` — five behavioural modes for what to do with the microphone while the avatar is speaking.
- The **error-voice presentation** (`OnErrorAsyncDefault`, lines 572-590) — composes a fallback `AnimatedVoiceRequest` with an error voice, an error face, and an error animation parameter when LLM/network/dialog calls throw.
- The **processing-presentation choice** (`ProcessingPresentations` list, line 111) — a randomly picked animation+face combination played during the LLM thinking phase, before the streamed response arrives.
- The **AudioMixer character-volume coupling** (lines 72-87, 426-442) — clamps `[-80dB, 0dB]`, exposes `IsCharacterMuted` and `MaxCharacterVolumeDb`, mutes via an `AudioMixer` parameter rather than `AudioSource.volume` (preserves the mixer routing).

**What AIAvatar does NOT own** (despite touching):
- The dialog state machine — owned by `DialogProcessor` (registered via callbacks; AIAvatar only *responds* to status changes).
- The model animation queue — owned by `ModelController`.
- The voice prefetch and playback — owned by `SpeechController`.
- The mic-sample capture — owned by `MicrophoneManager`.
- The STT call — owned by the chosen `ISpeechListener`.
- The TTS call — owned by the chosen `ISpeechSynthesizer`.
- The LLM call — owned by the chosen `ILLMService`.
- The tag extraction from streamed text — owned by `LLMContentProcessor`.

The ratio of *touches* to *owns* is roughly 3:1. That is the smell.

---

## 2. How It Works

### 2.1 The `Awake()` block — seventeen callbacks in 220 lines

`Awake` (lines 113-335) is where AIAvatar earns its label as a coordinator. It:

1. **Pulls component references** via `GetComponent<>` (lines 116-119) — `MicrophoneManager`, `ModelController`, `DialogProcessor`, `LLMContentProcessor`. Each is *optional* (the `??=` fallback): if the Inspector has them assigned, those win; otherwise auto-discover.

2. **Configures the mic noise gate** (line 122): `MicrophoneManager.SetNoiseGateThresholdDb(VoiceRecognitionThresholdDB)` — passes the avatar's UI-tunable threshold to the mic.

3. **Registers `SpeechController.OnSayStart`** (lines 125-138) — a lambda that, when the avatar is about to say a voice frame with non-empty text, waits the `PreGap` delay and then shows the spoken text in the `CharacterMessageWindow`. This is the *subtitle* layer.

4. **Registers `SpeechController.OnSayEnd`** (lines 139-142) — hides the character message window when each utterance finishes.

5. **Registers `DialogProcessor.OnRequestRecievedAsync`** (lines 146-194) — a *large* lambda. It:
   - Switches the mic strategy per `MicrophoneMuteBy` (lines 149-164). Five branches, each calling a different `MicrophoneManager` / `SpeechListener` method.
   - Picks a random processing-presentation animation+face (lines 167-173) — `ModelController.StopIdling()` + `Animate(...)` + `FaceController.SetFace(...)`.
   - Shows the user message window unless suppressed (lines 176-190) — three suppression conditions: wake-word turn, background-prefix turn, no user message window registered.
   - Resets face to `Neutral` (line 193).

6. **Registers `DialogProcessor.OnEndAsync`** (lines 197-230) — mirrors the strategy in §5: restores the mic, and if `endConversation`, transitions `Mode = Idle` and restarts idling animation.

7. **Registers `DialogProcessor.OnStopAsync`** (lines 232-242) — stops speech immediately; starts idling only if there is no successive dialog about to fire.

8. **Sets the error handler** (line 245): `DialogProcessor.OnErrorAsync = OnErrorAsyncDefault` — the default implementation defined at line 572 plays an `ErrorVoice` / `ErrorFace` / `ErrorAnimationParamKey` combination.

9. **Registers `LLMContentProcessor.HandleSplittedText`** (lines 248-262) — when LLMContentProcessor parses out a sentence-sized chunk, this converts it to an `AnimatedVoiceRequest` via `ModelController.ToAnimatedVoiceRequest`, ensures the first item resets the face to Neutral, and attaches the avreq to `contentItem.Data`.

10. **Registers `LLMContentProcessor.ProcessContentItemAsync`** (lines 265-282) — for every parsed item with an `AnimatedVoiceRequest`, fires off voice prefetches via `SpeechController.PrefetchVoices` for *every voice* in *every animated voice frame*. This is the parallel-TTS-prefetch pattern of CDK; it is the reason the avatar starts speaking the *first* sentence while the LLM is still streaming the second.

11. **Registers `LLMContentProcessor.ShowContentItemAsync`** (lines 285-291) — when the dequeue side is ready to display, calls `ModelController.AnimatedSay(avreq, token)`.

12. **Selects `ISpeechListener`** (lines 294-313) — iterates every `ISpeechListener` on the GameObject, picks the first with `IsEnabled == true`, wires `OnRecognized = OnSpeechListenerRecognized` and `OnBargeIn = OnBargeIn`, and calls `ChangeSessionConfig` with the idle-mode parameters (lower silence threshold, shorter recording window).

13. **Selects `ISpeechSynthesizer`** (lines 316-328) — same pattern, simpler: the chosen synth's `GetAudioClipAsync` becomes `SpeechController.SpeechSynthesizerFunc`.

14. **Captures the `AudioMixer`** (lines 331-334) — for character-volume control via the mixer parameter.

Seventeen callbacks. Each is straightforward in isolation. Together, they are *all of CDK's runtime wiring* in one file.

### 2.2 The Mode lifecycle — `UpdateMode` and the timer

`Update` (lines 345-391) runs every frame. The first action is `UpdateMode()` (line 347), which transitions the avatar between `Conversation`, `Idle`, and `Sleep` states based on a single countdown timer (`modeTimer`).

The state transitions (lines 393-424):
- If `DialogProcessor.Status` is *not* `Idling` or `Error`, force `Mode = Conversation` and reset the timer to `conversationTimeout`. **A dialog in flight always pins the avatar to conversation mode.**
- If `Mode == Sleep`, do nothing — sleep is a terminal state until externally woken.
- Else, decrement `modeTimer` by `Time.deltaTime`. If still positive, return.
- If timer expired *and* `Mode == Conversation`, go to `Idle` and reset to `idleTimeout`.
- If timer expired *and* `Mode == Idle`, go to `Sleep` and reset timer to zero.

Three states, two transitions, one timer. **This is the cleanest state-machine in CDK.** Compare SAP's mode handling (`server.py:11000+` with `mode_change.py`) — SAP has more states and they are managed by a separate routing module ([[sap:10_DOMAIN_MAP]] §14). CDK fits the same logic in 30 lines.

The rest of `Update` (lines 349-390) handles two side effects of mode change:
- The `UserMessageWindow` show/hide based on whether the avatar is now listening or idle.
- The `SpeechListener.ChangeSessionConfig` swap between conversation parameters (longer silence threshold, longer max recording) and idle parameters (shorter, faster).

The conversation parameters are `conversationSilenceDurationThreshold = 0.4f` / `conversationMinRecordingDuration = 0.3f` / `conversationMaxRecordingDuration = 10.0f` (lines 40-44). Idle: `0.3f / 0.2f / 3.0f` (lines 46-50). The avatar *listens harder* (longer max-record, more tolerant of pauses) once it knows it is in a conversation. This is a small, real teaching for Ember — and one neither SAP nor Waifu attempt.

### 2.3 The wake / cancel / interrupt extractors

`ExtractWakeWord` (lines 444-476), `ExtractCancelWord` (lines 478-495), `ExtractInterruptWord` (lines 497-521). All three:

1. Lowercase the input.
2. Strip the `IgnoreWords` list (`["。", "、", "？", "！"]` by default, line 69) — Japanese sentence punctuation.
3. Iterate the configured vocabulary, doing a `Contains` check against each candidate.
4. For wake/interrupt only: verify the `prefix.Length` and `suffix.Length` around the matched substring are within the `WordWithAllowance.PrefixAllowance` / `SuffixAllowance` budget (default 4 characters each).

The `WordWithAllowance` nested type (lines 656-662) is a small but useful invention: it lets the wake word "hey Alice" tolerate small filler before/after — "uhh hey Alice are you there" still triggers, "uhh hey Alice my friend over there could you" does not. SAP's wake-word logic (`server.py:2400+`) is broader and less disciplined. CDK names the slop allowance and lets the user tune it.

`WakeLength` (line 70) — if set, *any* input of length >= the configured threshold is treated as a wake. The intent: bypass wake words for long utterances. The risk: ambient chatter that happens to be long triggers conversation mode. This is configurable, off by default.

### 2.4 The `OnSpeechListenerRecognized` dispatcher

Lines 592-630: the single entry point from the STT layer. The decision tree:

```csharp
// /tmp/ChatdollKit/Scripts/AIAvatar.cs:592-630
if (string.IsNullOrEmpty(text) || Mode == AvatarMode.Disabled) return;
else if (!string.IsNullOrEmpty(ExtractCancelWord(text)))
    await StopChatAsync();
else if (!string.IsNullOrEmpty(ExtractInterruptWord(text)))
    await StopChatAsync(continueDialog: true);
else if (Mode >= AvatarMode.Conversation)
    _ = DialogProcessor.StartDialogAsync(text, payloads: GetPayloads?.Invoke());
else if (!string.IsNullOrEmpty(ExtractWakeWord(text)))
{
    // ... wake handling
    payloads["IsWakeword"] = true;
    _ = DialogProcessor.StartDialogAsync(text, payloads: payloads);
}
```

Four branches, in priority order. Cancel beats interrupt beats already-in-conversation beats wake. The fall-through (no match) silently discards the input — *this is the right behaviour* in idle mode (avoid responding to ambient noise) and the wrong behaviour with no diagnostic (the user does not know why their utterance was ignored). Ember should emit a typed event for the ignored case.

The `Mode >= AvatarMode.Conversation` comparison (line 609) is enum arithmetic — the enum values are `Disabled=0, Sleep=1, Idle=2, Conversation=3` (lines 26-30), so `>= Conversation` is the test for "in conversation right now." This is fine but implicit; an enum that uses ordering as a feature is one rename away from confusion.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 Seventeen callbacks in one Awake()

The structural problem. Every behavioural decision the avatar can make is wired in one place. To change the mic-mute strategy: edit `AIAvatar.cs`. To change the processing-presentation logic: edit `AIAvatar.cs`. To change how user messages display: edit `AIAvatar.cs`. The single file has *high blast radius* — any change risks unrelated regressions.

This is *not* the SAP pathology where one file does logic; CDK's logic is in the right places. It is the *coordination* pathology where one file does wiring. The smaller variant of the same illness.

### 3.2 The lambda captures hide ordering dependencies

Each registered callback is a lambda capturing local state. `OnRequestRecievedAsync` (lines 146-194) captures `neutralFaceRequest` (line 145). `HandleSplittedText` (lines 248-262) captures nothing but reads `contentItem.IsFirstItem`. The order of registration in `Awake` is *the* order in which they will fire — and there is no test or documentation enforcing that order. A future contributor reordering for readability can subtly break the avatar's behaviour.

### 3.3 `ProcessingPresentations` is unbounded list, randomly indexed

Line 169: `ProcessingPresentations[UnityEngine.Random.Range(0, ProcessingPresentations.Count)]`. If the list is empty, the outer `if` (line 167) skips. If the list has one item, that item plays every time. If the list has 50 items, they cycle randomly with no anti-repeat. The pattern is fine but the *anti-repeat* logic is absent — the same processing animation can play twice in a row, which feels wrong. SAP had the same problem ([[sap:11_AVATAR_DOMAIN]] §3 — different surface, same pattern); Waifu's cloud avatar likely solves it internally; CDK exposes the flaw.

### 3.4 The mic-mute strategies are not orthogonal

Five strategies (`None / Threshold / Mute / StopDevice / StopListener`, lines 54-61) are applied at both `OnRequestRecievedAsync` (lines 149-164) and `OnEndAsync` (lines 200-215). Each branch in the start handler has a matching branch in the end handler — eight times the same `if` cascade across the two callbacks. Refactoring opportunity: pull into a `MicrophoneControlStrategy` interface with `BeforeRequest()` and `AfterRequest()` methods, one class per strategy. CDK does not refactor it; the cost is 32 lines of duplicated branching.

### 3.5 The error animation parameters are flat strings

Lines 99-106: `ErrorVoice`, `ErrorFace`, `ErrorAnimationParamKey`, `ErrorAnimationParamValue` are all `[SerializeField]` strings/ints assigned in the Inspector. There is no validation that the voice exists in the TTS catalogue, that the face is a valid `FaceExpression` name, or that the animation key is registered with `ModelController.RegisterAnimation`. The error path silently fails when the configuration is wrong — and the error path is the one most likely to be misconfigured because it is exercised least.

### 3.6 The mode timer reads `Time.deltaTime` directly

Line 408: `modeTimer -= Time.deltaTime;`. This is Unity's *scaled* time — if game-time is paused (`Time.timeScale = 0`), the timer freezes. For a chat avatar this is fine; for an embedded avatar in a paused game, the conversation also pauses. The behaviour is implicit. Ember should use *unscaled* time for conversation timing, regardless of host-app pause state.

### 3.7 The crisp parts

Despite the smell, much of AIAvatar is genuinely well-formed:
- The **mode-state machine** is 30 lines and easy to read.
- The **wake-word extractor** with prefix/suffix allowance is the right shape.
- The **dialog callback registration** is *explicit* — no magic strings, no reflection.
- The **enabled-flag selection** of speech listener / synthesizer is clean.
- The **`OnWakeAsync`** hook (line 110) is the right place for a user-supplied wake handler (greeting, etc.) — extensibility done well.
- The **`GetPayloads` factory** (line 109) — a `Func<Dictionary<string, object>>` the user can set to inject contextual payloads (image bytes, camera frame, custom keys) per request. Composable.

The lesson is not "AIAvatar is bad." The lesson is "AIAvatar is *too large* to be one file even though every line inside it is correct." Ember's coordinator must split.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 0 — AIAvatar in the eight-subsystem view
- [[13_DIALOG_PROCESSOR_DOMAIN]] — the state machine AIAvatar drives
- [[14_SPEECH_LISTENER_DOMAIN]] — the STT pipeline AIAvatar registers against
- [[15_SPEECH_SYNTHESIZER_DOMAIN]] — the TTS pipeline AIAvatar selects from
- [[17_MICROPHONE_MANAGER_DOMAIN]] — the mic surface AIAvatar mutes
- [[sap:10_DOMAIN_MAP]] §5.1 — the larger `server.py` version of the same pathology
- [[waifu:10_DOMAIN_MAP]] §5.1 — the kit's choice to *have no coordinator* at all

---

## What This Means for Ember

**Adopt:**
- The **AvatarMode three-state machine** (`Sleep / Idle / Conversation`, plus `Disabled` for off). Source: `Scripts/AIAvatar.cs:25-31`, Apache-2.0 attribution required. Ember's runtime mode follows this exact shape — adding a fourth state only when there is a genuine behaviour for it. Implementation as a Python `enum.Enum`.
- The **MicrophoneMuteStrategy enum** (`None / Threshold / Mute / StopDevice / StopListener`, lines 54-61). Adopt the *taxonomy* — Ember's voice-tier configuration exposes the same five options. The `Threshold` strategy is the most teaching-rich: instead of muting, *raise the recognition threshold* while speaking, so the user can still barge in with a louder voice. SAP has nothing equivalent; Waifu has only a coarse boolean.
- The **`WordWithAllowance` pattern** (lines 656-662). Wake words with tunable prefix/suffix slop — adopt for Ember's wake-vocabulary surface. The default `4` is reasonable; expose it per-word for users with verbose habits.
- The **enabled-flag provider selection** (line 296 for speech listeners, line 318 for synthesizers) — adopt as Ember's `provider_selector(candidates: list[Provider]) -> Provider` returning the first `enabled=True`.

**Adapt:**
- **AIAvatar.cs as a two-file split.** CDK's 664-line coordinator becomes Ember's `ember_config.py` (declarative wiring loaded from `runtime.yaml`) + `ember_runtime.py` (the state-machine and lifecycle callbacks). Configuration knows nothing of runtime; runtime knows nothing of how it got configured. The split is the architectural antidote to the smell.
- The **seventeen-callback `Awake()`** — adapt as Ember's *event-bus-driven* coordinator. Instead of AIAvatar reaching into `LLMContentProcessor.HandleSplittedText = ...`, every subsystem emits typed events on the Sögumiðla bus, and Ember's coordinator *subscribes* to the events it cares about. The wiring becomes declarative subscriptions, not imperative assignments. This is the inversion that decouples without losing control.
- The **mode-timer logic** — adapt to use unscaled time, and to emit a Sögumiðla `ModeTransition` event so any downstream surface (logs, UI, broadcast) sees the transition. CDK's `previousMode != Mode` per-frame check (line 369) becomes a single transition event.
- The **`ExtractWakeWord` lower-case+strip-then-search** pattern (lines 444-476) — adapt as Ember's `wake_word_match(text: str, vocab: list[WakeWord]) -> WakeWord | None`. Unicode-correct case folding (Python's `casefold()` not `lower()`), Unicode-correct punctuation strip (the `IgnoreWords` list extended for English commas and periods).

**Avoid:**
- **A single coordinator file > 300 lines.** This is the SAP smell in CDK's form. Even at 664 lines, AIAvatar has too high a blast radius. Ember's coordinator splits *as soon as* it crosses 200 lines.
- **Lambda-based callback wiring with implicit ordering.** Each lambda is fine; the registration order is the protocol; the protocol is unwritten. Ember's subscriptions are declared with explicit ordering metadata (e.g., `@subscribe(EventType, priority=10)`).
- **Silent-drop on unmatched STT input** (line 630 — the fall-through case). Ember emits an `IgnoredUtterance` event with the text + reason (`no_match`, `wake_word_required`, `mode_disabled`) so future me knows why a turn did not happen.
- **Hardcoded animation/voice/face strings in the error-handler config** (lines 99-106). Ember validates the error-handler configuration at startup against the registered face/animation/voice catalogues; a misconfigured error handler fails *loudly* at startup, not silently when the error fires.

**Invent:**
- **The Sögumiðla Subscription Manifest.** Every Ember subsystem declares (in a `MANIFEST.yaml` per package) which Sögumiðla event types it emits and which it subscribes to. CI verifies that every subscribed event has a producer somewhere. AIAvatar.cs's seventeen callbacks become seventeen manifest entries, each individually reviewable and testable. The Boundary Census ([[sap:10_DOMAIN_MAP]] §invent) realised at the runtime layer.
- **The Coordinator Skeleton Vow.** Every Ember coordinator (= file with > 5 cross-subsystem references) ships as a *skeleton* — declarative wiring only — plus a separate state-machine. The state-machine is testable in isolation with mock subscribers. The skeleton is testable as a YAML schema.
- **The Mode Transition Audit Trail.** Every mode change (Sleep → Idle → Conversation and back) is a typed event with reason metadata: `{from: Idle, to: Conversation, reason: wake_word, payload: {wake_word: "hey ember", confidence: 0.94}}`. Sögumiðla persists transitions to a session log; the log is queryable for "why is my avatar stuck in conversation mode" diagnostics. SAP and CDK both let the user wonder; Ember refuses.
- **The MicrophoneStrategy Class Hierarchy.** AIAvatar.cs's five-branch if-cascade duplicated across two callbacks (32 lines) becomes Ember's `MicrophoneStrategy` ABC with `before_request(mic)` and `after_request(mic)` methods, five concrete subclasses, registered by name in YAML. Adding a sixth strategy is one file; no AIAvatar.cs equivalent needs to change.
- **The Conversation-Listening Tuning Pair.** CDK has two `ChangeSessionConfig` calls — one for conversation, one for idle — with implicit values. Ember exposes the pair as a typed `(IdleListeningConfig, ConversationListeningConfig)` tuple; the transition between them is automatic; the values are user-tunable per realm.

*Apache-2.0 attribution: when patterns from `ChatdollKit/AIAvatar.cs` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

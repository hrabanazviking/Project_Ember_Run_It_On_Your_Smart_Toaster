---
codex_id: 37_BARGE_IN_INTERRUPT
title: Barge-In — Cancel-and-Replace at the TTS/Dialog Seam
role: Forge-A
layer: Execution
status: draft
kit_source_refs:
  - Scripts/AIAvatar.cs:54-68 (MicrophoneMuteStrategy + StopResponseOnBargeIn + CancelWords + InterruptWords)
  - Scripts/AIAvatar.cs:144-215 (mute-on-respond / unmute-on-end via DialogProcessor callbacks)
  - Scripts/AIAvatar.cs:296-302 (OnBargeIn wired into SpeechListener)
  - Scripts/AIAvatar.cs:478-521 (ExtractCancelWord + ExtractInterruptWord)
  - Scripts/AIAvatar.cs:592-640 (OnSpeechListenerRecognized + OnBargeIn handler)
  - Scripts/SpeechListener/SpeechListenerBase.cs:45-83 (Update-loop barge-in trigger by duration)
  - Scripts/SpeechListener/AzureStreamSpeechListener.cs:38-114 (streaming-STT barge-in trigger by partial-text length)
  - Scripts/SpeechListener/ISpeechListener.cs:10-11 (OnBargeIn + BargeInCondition contract)
  - Scripts/Dialog/DialogProcessor.cs (Status, StopDialog, OnStopAsync)
ember_subsystem_targets: [Funi, Strengr, Munnr, Hjarta]
cross_refs:
  - 31_AIAVATAR_MAIN_LOOP
  - 32_STT_LOOP
  - 33_TTS_PREFETCH
  - 14_SPEECH_LISTENER_DOMAIN
  - 24_VAD_INTERFACE
  - sap:31_AVATAR_DIALOG_FLOW
  - waifu:30_BASIC_MODE_FLOW
license_posture: Apache-2.0 — adopt with attribution
---

# Barge-In Interrupt

> *Most assistants force you to wait until they're done speaking. CDK doesn't. Three knobs, two trigger paths, one cancel pulse — and the conversation feels human.*

Forge-A. Eldra. Barge-in is the single best UX affordance ChatdollKit ships, and it is the one nobody talks about because it lives at the boundary between three subsystems (SpeechListener, DialogProcessor, SpeechController) and looks small from the outside. From the user's side it is one sentence: *"I can interrupt the avatar mid-sentence and it shuts up and listens."* From inside the kit it is a five-step state transition, two independent trigger algorithms, and a cancellation token cascade. This doc traces the entire pipeline so Ember's Munnr can ship the same affordance — and so we can name where CDK falls short.

## The Three Knobs

The author surface for barge-in is three fields on `AIAvatar` (`/tmp/ChatdollKit/Scripts/AIAvatar.cs:62-68`):

```csharp
// /tmp/ChatdollKit/Scripts/AIAvatar.cs:62-68
public MicrophoneMuteStrategy MicrophoneMuteBy = MicrophoneMuteStrategy.Mute;

[Header("Conversation settings")]
public bool StopResponseOnBargeIn = true;
public List<WordWithAllowance> WakeWords;
public List<string> CancelWords;
public List<WordWithAllowance> InterruptWords;
```

Three orthogonal levers, four behavioral regimes:

1. **`MicrophoneMuteBy`** — what the kit does to the *mic input* while the avatar is responding. Five-valued enum (`AIAvatar.cs:54-61`): `None`, `Threshold`, `Mute`, `StopDevice`, `StopListener`. **`None` is the magic value that enables continuous barge-in** — the mic stays live, the STT keeps listening, the user can interrupt at any moment. The other four values block the mic during TTS and disable barge-in by construction; they exist for builds without echo cancellation where the avatar would hear itself.
2. **`StopResponseOnBargeIn`** — whether a detected barge-in actually cancels the current avatar turn (`AIAvatar.cs:65`). Default `true`. When `false`, the system *detects* the user is trying to interrupt but politely lets the avatar finish its sentence. A nuance dial: useful when the avatar is reading something critical that shouldn't be cut.
3. **`CancelWords` + `InterruptWords`** — explicit phrase triggers for *post-recognition* interruption (`AIAvatar.cs:67-68`). These are the safety net for the case where audio-level barge-in fails: the user can say "stop" or "wait wait wait" and the kit recognizes it as a cancellation signal even if the audio-level VAD didn't trip in time.

These three knobs cover everything from a museum-kiosk-grade non-interruptible avatar (`MicrophoneMuteBy = Mute`, `StopResponseOnBargeIn = false`) up to a fluent-conversation continuous-barge-in companion (`MicrophoneMuteBy = None`, `StopResponseOnBargeIn = true`, AEC-enabled mic plugin). One enum, two booleans — and the entire interaction model shifts.

## The Two Trigger Paths

Barge-in detection happens in **two structurally different places**, depending on which `SpeechListener` is active.

### Path A: Duration-based (offline VAD listeners)

For non-streaming STT — the family that buffers audio, detects silence, then submits a complete utterance to Google/OpenAI/etc. — barge-in is **purely duration-based** and lives in `SpeechListenerBase.Update`:

```csharp
// /tmp/ChatdollKit/Scripts/SpeechListener/SpeechListenerBase.cs:66-84
protected virtual void Update()
{
    IsRecording = session != null && session.IsRecording;
    IsVoiceDetected = session != null && !session.IsSilent;

    // Barge-in check
    if (IsRecording && !bargeInTriggered && session != null)
    {
        var shouldBargeIn = BargeInCondition != null
            ? BargeInCondition(null, session.RecordDuration)
            : session.RecordDuration >= BargeInMinDuration;

        if (shouldBargeIn)
        {
            bargeInTriggered = true;
            OnBargeIn?.Invoke();
        }
    }
}
```

Every frame: *if we are recording and the user has been speaking for ≥ `BargeInMinDuration` (default 1.5s), fire `OnBargeIn`.* No transcript, no semantic check. Just "user has been making noise for ≥ N seconds." This is intentionally dumb. The 1.5s default exists to filter out coughs, sneezes, ambient interjections, and the user mumbling "yeah" in agreement. Anything shorter than 1.5s is treated as listener affect; longer is treated as turn-claim.

The `bargeInTriggered` latch (`SpeechListenerBase.cs:50`) is reset at each `StartListening` call (`:97`), so once per recording session.

The `BargeInCondition` hook (`:46`) lets operators replace duration with any signal: amplitude threshold, frequency analysis, even an external model. The default is duration because duration is universally cheap.

### Path B: Partial-transcript-based (streaming STT listeners)

For streaming STT — Azure-Stream, AIAvatarKit-Stream, OpenAI-Stream — barge-in triggers on the **length of the partial transcript** instead of audio duration. From `AzureStreamSpeechListener` (`/tmp/ChatdollKit/Scripts/SpeechListener/AzureStreamSpeechListener.cs:65-82`):

```csharp
// /tmp/ChatdollKit/Scripts/SpeechListener/AzureStreamSpeechListener.cs:65-82 (compressed)
OnRecognizerRecognizing = (sender, e) =>
{
    RecognizedTextBuffer = e.Result.Text;

    // Barge-in check (runs on background thread)
    if (!bargeInTriggered && !string.IsNullOrEmpty(e.Result.Text))
    {
        var shouldBargeIn = BargeInCondition != null
            ? BargeInCondition(e.Result.Text, 0f)
            : e.Result.Text.Length >= BargeInMinTextLength;

        if (shouldBargeIn)
        {
            bargeInTriggered = true;
            bargeInPending = true;
        }
    }
};
```

This event fires on Azure's *partial* recognition stream — the rolling best-guess of what the user is saying so far. The default `BargeInMinTextLength` is 2 (`AzureStreamSpeechListener.cs:44`) — two characters of recognized text and the kit considers it a real turn-claim. That's much faster than 1.5 seconds of audio; on Azure-Stream a typical first-character latency is ~200-400ms.

The thread-hopping detail (`:78-79, :107-114`) is critical: Azure's event handlers run on background threads, but `OnBargeIn` callbacks must execute on the Unity main thread (they touch components). So `bargeInPending` is the cross-thread flag, and the next `Update()` tick on the main thread fires the callback. This is **Unity-idiomatic background→main marshalling** that Ember's Andlit-unity tier must replicate exactly.

The Path-B latency win is significant: ~300ms (Path B) vs ~1500ms (Path A) before barge-in fires. **The streaming-STT path is the path that makes barge-in feel like real conversation.** Azure-Stream + `MicrophoneMuteBy = None` + AEC-enabled mic + Path B trigger is the production-grade combination.

## The Cancel Pulse

When `OnBargeIn` fires, control returns to `AIAvatar.OnBargeIn` (`AIAvatar.cs:632-640`):

```csharp
// /tmp/ChatdollKit/Scripts/AIAvatar.cs:632-640
private void OnBargeIn()
{
    if (!StopResponseOnBargeIn) return;

    if (Mode >= AvatarMode.Conversation && DialogProcessor.Status == DialogProcessor.DialogStatus.Responding)
    {
        _ = StopChatAsync(continueDialog: true);
    }
}
```

Three guards, then the cancel pulse:

1. `StopResponseOnBargeIn` toggle off → no-op (the kit detected the user wants to interrupt but isn't authorized to act on it).
2. `Mode >= AvatarMode.Conversation` → only cancel during active conversation, not while idle or wakeword-listening.
3. `DialogProcessor.Status == Responding` → only cancel if the avatar is actually speaking right now. If we're already idle or already listening, barge-in is a no-op.

The actual cancel goes through `StopChatAsync(continueDialog: true)` (`AIAvatar.cs:546-561`), which calls `DialogProcessor.StopDialog()` and waits. The `continueDialog: true` is the **merge-window seed**: it tells the dialog state machine "we're stopping the current turn but the conversation isn't over — the next utterance from this same user is part of the same dialog."

`DialogProcessor.OnStopAsync` (wired in `AIAvatar.cs:232-242`) then does the heavy lifting:

```csharp
// /tmp/ChatdollKit/Scripts/AIAvatar.cs:232-242
DialogProcessor.OnStopAsync = async (forSuccessiveDialog) =>
{
    // Stop speaking immediately
    ModelController.SpeechController.StopSpeech();

    // Start idling only when no successive dialogs are allocated
    if (!forSuccessiveDialog)
    {
        ModelController.StartIdling();
    }
};
```

`StopSpeech()` calls `AudioSource.Stop()` (per [[33_TTS_PREFETCH]]). Mid-syllable cut. The avatar shuts up *now*. The animation continues to its frame boundary, then either continues for the rest of the gesture or transitions to idle depending on `forSuccessiveDialog`.

The cancellation token threaded through `Say` (`SpeechController.cs:38` per [[33_TTS_PREFETCH]]) trips: the playback loop sees `token.IsCancellationRequested` and exits the per-voice `await` (`SpeechController.cs:100`). The remaining queued voices in the `voicePrefetchQueue` and `audioDownloadTasks` stay around but won't play because there's no `Say` consuming them — the next `Say` call will start fresh with new voices.

That is the cancel pulse in five lines.

## The Merge Window

This is the part the MANIFEST scope calls out and the part most assistants get wrong. Here is the question: *after a barge-in cancel, what counts as the start of the next user turn?*

CDK's answer, traced through the code:

1. `StopChatAsync(continueDialog: true)` stops the *avatar's* response but does **not** stop the SpeechListener (`AIAvatar.cs:546-561`).
2. The SpeechListener continues recording. Its `bargeInTriggered` latch remains `true` until the *current* recording session completes via `OnRecognized` (`SpeechListenerBase.cs:95-97` for Path A; `AzureStreamSpeechListener.cs:95` for Path B), at which point the kit treats the captured audio as the user's next turn.
3. When `OnRecognized` finally fires (the user finishes speaking the interruption), the recognized text flows into `OnSpeechListenerRecognized` (`AIAvatar.cs:592-630`). Because `Mode >= Conversation` still holds, the recognized text goes straight to `DialogProcessor.StartDialogAsync` as a fresh user turn.

So the merge window in CDK is **implicit and unbounded**: from the moment of barge-in until the user finishes their current vocalization, everything they say is glued together into one new user turn. There is no timer that says "if the user re-speaks within N ms of cancel, merge." There is one continuous recording session, period.

This is *almost right* and has one specific failure mode: **the post-cancel double-trigger.** Consider:

- The user interrupts: "actually wait" (250ms, Path B triggers at "ac…" after ~150ms).
- Cancel pulse fires. Avatar shuts up.
- The user, finishing their thought: "...stop, I meant the other one."
- SpeechListener completes the recording session and submits the full transcript: `"actually wait stop, I meant the other one"` — correct. No double trigger.

Now consider:

- The user interrupts: "stop" (150ms, Path B triggers).
- Cancel pulse fires. Avatar shuts up. SpeechListener's `bargeInTriggered = true`.
- The user goes quiet, listening for the avatar to acknowledge.
- After `SilenceDurationThreshold` (default 0.3s, `SpeechListenerBase.cs:27`), the recording session completes. `OnRecognized` fires with `"stop"`. `bargeInTriggered` resets to false. Recording restarts.
- Now the user, two seconds later: "I meant the other one."
- A second `OnRecognized` fires with `"I meant the other one"`.

Both fire as separate user turns. The dialog processor handles each independently. There is **no logical glue** that says "the second turn is a continuation of the first." If the avatar started responding to "stop" between the two utterances, the user experiences another barge-in. Two turns where there should have been one. Awkward.

The pattern CDK *needs* and Ember *should invent* is a **time-bounded merge window**: for N milliseconds after a cancel-pulse, the next `OnRecognized` is fused with the previous one as a single dialog turn rather than treated as a fresh request. `N = 800ms` is the sweet spot from empirical literature on conversational systems. See Invent.

## The Word-Based Fallback Path

CDK's belt-and-suspenders: even with `StopResponseOnBargeIn = false`, the user can still cancel by saying a specific word. From `OnSpeechListenerRecognized` (`AIAvatar.cs:592-630`):

```csharp
// /tmp/ChatdollKit/Scripts/AIAvatar.cs:592-606 (compressed)
private async UniTask OnSpeechListenerRecognized(string text)
{
    if (string.IsNullOrEmpty(text) || Mode == AvatarMode.Disabled) return;

    // Cancel Word
    else if (!string.IsNullOrEmpty(ExtractCancelWord(text)))
    {
        await StopChatAsync();
    }

    // Interrupt Word
    else if (!string.IsNullOrEmpty(ExtractInterruptWord(text)))
    {
        await StopChatAsync(continueDialog: true);
    }
    ...
}
```

Two distinct keyword classes:

- **`CancelWord`** (`AIAvatar.cs:478-495`) — exact-match-after-punctuation-strip. Calls `StopChatAsync()` (no `continueDialog`), which fully ends the conversation. Default examples: "cancel", "never mind". The word equivalent of "exit conversation."
- **`InterruptWord`** (`AIAvatar.cs:497-521`) — substring-match-with-prefix/suffix-allowance via the `WordWithAllowance` struct (`AIAvatar.cs:656-660`). Calls `StopChatAsync(continueDialog: true)` — same as barge-in. Example: "wait wait wait" with `PrefixAllowance: 0, SuffixAllowance: 50` matches "wait wait wait sorry can you say that differently."

The allowance fields are clever. Cancel-words must match the *whole* utterance (modulo punctuation) — strict. Interrupt-words may appear anywhere in the utterance — lenient. The strictness asymmetry makes sense: "cancel" alone means cancel, but "wait" appearing mid-sentence often means "let me catch up."

This fallback path means even if Path A and Path B both miss the audio-level barge-in (rare but possible: very quiet user, very loud avatar, poor AEC), the user can still take back control by saying the magic words.

**Cost:** the keyword paths only fire after `OnRecognized` — meaning the full STT round-trip has to complete. That's 800ms-2s of avatar-still-talking after the user said "wait" before the actual cancel happens. Real-world UX: noticeable but acceptable.

## Mute Strategies — The Pre-Barge-In Hygiene

Before there can be barge-in, there has to be a microphone that can hear the user during TTS. `MicrophoneMuteBy` is the knob that controls this (`AIAvatar.cs:149-215`):

```csharp
// /tmp/ChatdollKit/Scripts/AIAvatar.cs:149-164 (the mute side of the pair)
if (MicrophoneMuteBy == MicrophoneMuteStrategy.StopDevice)
{
    MicrophoneManager.StopMicrophone();
}
else if (MicrophoneMuteBy == MicrophoneMuteStrategy.StopListener)
{
    SpeechListener.StopListening();
}
else if (MicrophoneMuteBy == MicrophoneMuteStrategy.Mute)
{
    MicrophoneManager.MuteMicrophone(true);
}
else if (MicrophoneMuteBy == MicrophoneMuteStrategy.Threshold)
{
    MicrophoneManager.SetNoiseGateThresholdDb(VoiceRecognitionRaisedThresholdDB);
}
```

Five strategies in increasing order of permissiveness toward barge-in:

| Strategy | Mic device | STT | VAD | Barge-in possible? |
|---|---|---|---|---|
| `StopDevice` | Off (OS stops capture) | Off | Off | No |
| `StopListener` | On | Off | Off | No |
| `Mute` | On (zeroed in software) | Available | Won't trigger | No |
| `Threshold` | On (high noise floor) | Available | Hard to trigger | Yes, if user is loud |
| `None` | On | On | On | **Yes — continuous barge-in** |

The default is `Mute`. For barge-in, set to `None`. The `Threshold` middle ground (`AIAvatar.cs:161-164`) raises the VAD threshold during TTS so the avatar's own voice doesn't trip the VAD but a louder user voice still can — a software-AEC for the AEC-less build. It works on desktop monitors with good speaker separation; it fails badly on headphones-as-speakers or close-coupled mobile speakers.

The pairing in `OnEndAsync` (`AIAvatar.cs:200-215`) restores the mic to whatever its default state was. The mute/unmute is per-turn, not session-wide.

## The Surprises

- **`StopChatAsync(continueDialog: true)` is the magic.** The same function services both audio-level barge-in and InterruptWord cancellation, and the boolean flag is what tells the system "this is a turn break, not a conversation break." The asymmetry between `CancelWord → StopChatAsync()` and `InterruptWord → StopChatAsync(continueDialog: true)` is what lets the system handle two semantically different cancellations through one function.
- **Path A's `bargeInTriggered` latch is reset only at `StartListening`, not at session end.** Look at `SpeechListenerBase.cs:97`. This means within a single recording session, only the first 1.5s-mark fires `OnBargeIn`. Subsequent extended speech doesn't re-trigger. If the user goes silent and the session naturally ends, the next session resets the latch. Subtle: the kit will not fire repeated barge-ins for one long utterance.
- **Path B's barge-in fires on the *first partial transcript* of ≥ 2 chars, regardless of what was actually said.** The user could be muttering nonsense. The kit cancels first, asks questions later. The rationale: the user is making intentional speech-shaped sounds during avatar speech; that's an interruption signal regardless of content.
- **`BargeInCondition` is a public hook.** Operators can replace duration-based or length-based with anything: a wake-word detector, an intent classifier, a sentiment model. This is the extension point for "only barge-in on negative/urgent affect" — a custom model returning `true` only when the user sounds frustrated.
- **There is no in-codebase reference to `StopResponseOnBargeIn` in a "but only for some content types" branch.** The toggle is global. If the avatar is mid-warning ("DON'T touch the hot stove") and the user starts speaking, the avatar still cancels. This is right for most cases but wrong for safety-critical content. Operators must build their own content-importance gating outside the kit.
- **The OnBargeIn handler bypasses `OnRecognized` entirely.** Audio-level barge-in fires *before* the STT has any transcript. The kit cancels the avatar's turn *before knowing what the user is going to say.* The next utterance's text is whatever the STT produces from the same recording session. This is the right factoring — the cancel happens at the speed of audio, and the response happens at the speed of STT.

## Where It Breaks

- **No merge window.** Two adjacent user utterances after a cancel are two distinct turns. The avatar may start responding to the first before the second arrives. UX glitch on slow re-speak.
- **No content-importance gating.** Safety-critical avatar utterances can be interrupted same as small talk.
- **`bargeInTriggered` resets only at next `StartListening`.** Edge case: if `StartListening` isn't called between sessions (e.g. external state machine bug), the latch stays stuck and the user can never barge-in again. Recoverable but not auto-healed.
- **`MicrophoneMuteBy.None` requires AEC.** Without echo cancellation, the avatar's voice loops back into its own mic and triggers barge-in on itself. Self-interruption loop. Diagnostic on shipping: if barge-in fires within 100-300ms of TTS start, AEC is broken.
- **The 1.5s default `BargeInMinDuration` is too long for streaming-STT environments.** Operators must tune per-listener. Default values are conservative.
- **Word fallback path is full-STT-round-trip latency.** Functional but laggy.
- **No way to cancel the cancel.** Once `StopSpeech()` fires, the mid-syllable cut is final. If the user said something that wasn't actually an interruption (sneezed during avatar speech, Path A's duration-based fired anyway), the avatar's response is gone. A 200ms grace window where the kit "stops the avatar but holds the cancel" pending user confirmation would be a nicer UX but doesn't exist.
- **Streaming-STT thread-marshalling is fragile.** `bargeInPending` volatile flag works but is the kind of cross-thread state that fails subtly on Unity's WebGL build (no threads) or under load. The pattern is correct; the implementation has only been smoke-tested.

## Cross-References

- [[31_AIAVATAR_MAIN_LOOP]] — where AvatarMode and DialogProcessor.Status live; the state-machine that gates barge-in
- [[32_STT_LOOP]] — the SpeechListener pipeline that runs the trigger algorithms
- [[33_TTS_PREFETCH]] — `StopSpeech()` + cancellation token cascade that the cancel pulse rides
- [[14_SPEECH_LISTENER_DOMAIN]] — Architect view of the listener subsystem
- [[24_VAD_INTERFACE]] — Silero VAD detail; relevant for `BargeInCondition` swap-ins
- [[sap:31_AVATAR_DIALOG_FLOW]] — contrast: SAP has no audio-level barge-in. Conversation is strict turn-taking gated by enter-press or wake-word. Cancel is "click the stop button." The whole barge-in affordance is absent.
- [[waifu:30_BASIC_MODE_FLOW]] — contrast: Waifu's LiveKit-based cloud stack supports barge-in at the LiveKit-agent layer (LiveKit Agents framework has VAD-driven turn detection), but the surface is hidden behind the SDK. The browser tier cannot tune `BargeInMinDuration` or swap the trigger function.

## What This Means for Ember

*Apache-2.0 attribution: when adopting CDK's barge-in pipeline into Ember source, preserve the ChatdollKit header reference per Apache-2.0 §4(c). The duration-based and partial-transcript-based trigger algorithms are CDK's specific contribution.*

**Adopt:**

- **The three-knob author surface** — `MicrophoneMuteBy` enum + `StopResponseOnBargeIn` bool + `CancelWords`/`InterruptWords` keyword lists (`AIAvatar.cs:54-68`, Apache-2.0 attribution required). This is the right API. Ember's Munnr surfaces the same three knobs with the same semantics. Vendor wholesale.
- **The two-path trigger architecture** — duration-based for non-streaming STT (`SpeechListenerBase.cs:66-84`) and partial-transcript-length-based for streaming STT (`AzureStreamSpeechListener.cs:65-82`). The pattern is sound regardless of which STT Ember adopts; the rendezvous is the `OnBargeIn` callback.
- **The `BargeInCondition` extension hook** — operators can swap the default trigger function. Adopt as Munnr's `register_barge_in_predicate(fn)`.
- **The `StopChatAsync(continueDialog)` factoring** (`AIAvatar.cs:546-561`) — one function, one boolean, two distinct cancel semantics. Adopt as Strengr's `cancel_turn(continue_dialog: bool)`.
- **The five-valued `MicrophoneMuteStrategy`** — the strategy enum cleanly covers the deployment spectrum from museum kiosk to AEC-equipped phone. Adopt as Funi's `MicMuteStrategy`.

**Adapt:**

- **`BargeInMinDuration` default 1.5s → tune per platform.** Pi/desktop: 1.5s is fine. Mobile/AEC-equipped: 0.6s is the sweet spot. Streaming-STT: ignore duration entirely and use length-based (Path B). Munnr's tier-config sets the default per build target.
- **Word-fallback as substring-match-with-allowance** — adapt to use Ember's existing intent classifier (proposed in [[ember:]] — small local NLU) rather than literal-string matching. Adds latency budget but handles "wait, hold on a sec, actually stop" naturally where CDK's literal match would miss.
- **`StopResponseOnBargeIn` boolean** → adapt to `BargeInPolicy` enum: `Always`, `Never`, `WhenNonCritical`, `WhenUserAuthorized`. Ember's safety-critical utterances are tagged at LLM emission ([[ember:PHILOSOPHY]] Vow of Truth). The barge-in handler consults the tag.
- **Path-B thread-marshalling via `bargeInPending volatile bool`** → adapt to Ember's existing event-bus pattern. Avoids Unity-specific main-thread coupling and works across Pi/Electron/Unity/cloud tiers.

**Avoid:**

- **CDK's implicit/unbounded merge window.** Two adjacent user utterances after a cancel become two turns. Don't ship this. (See Invent below.)
- **`MicrophoneMuteBy = None` without verified AEC.** On any build target without OS-level echo cancellation, this is self-interruption forever. Ember's tier-config gates `None` behind an AEC-capability check; mis-pairing throws at build time.
- **The single-fire `bargeInTriggered` latch with manual reset at `StartListening`.** Easy to bug into a stuck state. Replace with a session-scoped latch tied to the recording session lifecycle, not external state.
- **Audio-level barge-in for safety-critical content unconditionally.** Tag-aware gating only.
- **Substring-only InterruptWord matching.** False-positive rate is too high in conversational speech ("oh wait, that's perfect" should not interrupt). Use intent classification.

**Invent:**

- **Strengr Merge Window.** After a cancel pulse, Strengr opens an 800ms `merge_window` during which the next `OnRecognized` is *concatenated* with the cancel-triggering utterance into a single user turn instead of starting a new dialog. Default 800ms based on empirical conversational-AI literature; tunable per locale. If no second utterance arrives within the window, the cancel-triggering utterance becomes the new user turn alone. This is the missing piece in CDK's barge-in pipeline and the single highest-leverage UX improvement. Vow tie-in: **Mythic Conversation**.
- **Munnr Importance-Tagged TTS.** Every emitted sentence carries an `importance: {trivial, normal, critical}` tag from the LLM prompt. Barge-in handler consults the tag: `critical` content cannot be interrupted by audio-level barge-in (only by explicit CancelWord). Example: an emergency safety warning is `critical`; a small-talk response is `trivial`. Vow tie-in: **Vow of Truth**, **Vow of Care**.
- **Hjarta Barge-In Ledger.** Every cancel event produces a `BargeInEvent { triggered_at, path: A|B|word, user_utterance, avatar_was_at: sentence_idx, merge_window_used: bool }`. Hjarta surfaces patterns: "the user interrupts me 70% of the time at sentence 2; I should pause for confirmation after sentence 1." Cancel events are training signal for the avatar's pacing. CDK has no such introspection. Vow tie-in: **Open Knowledge**, **Companion-as-Reflection**.
- **Funi Per-Tier BargeIn Manifest.** `data/charts/barge_in_tiers.yaml` declares: `pi-tier { path: A, min_duration_ms: 1500 }`, `mobile-aec-tier { path: B, min_text_len: 2, merge_window_ms: 800 }`, `electron-tier { path: A, min_duration_ms: 1000 }`. CI consumes this; the build artifact ships pre-tuned. Vow tie-in: **Smallness**, **Modular Authorship**.
- **Munnr Soft-Cancel.** Instead of mid-syllable AudioSource.Stop(), fade TTS volume to zero over 80ms while the cancellation token cascades. The avatar still shuts up fast but without the audible cut artifact. Costs 80ms of perceived latency, buys conversational politeness. Toggle: `Munnr.cancel_style: hard | soft`. Vow tie-in: **Mythic Conversation**, **Care**.
- **Strengr Speculation-Aware Cancel.** Per [[33_TTS_PREFETCH]] Invent of speculative prefetch: when a cancel fires, also cancel speculative-prefetched audio that will never play. Saves bandwidth on misprediction cancels. Vow tie-in: **Smallness**, **Bandwidth Discipline**.
- **Munnr Re-Engage Signal.** After a cancel pulse, if the user falls silent for > 2× `SilenceDurationThreshold` without producing a follow-up, the avatar speaks a brief re-engage: "I'm here when you want to continue." This is the *anti-pattern* to most assistants which sit silently after interruption forever. Tag-aware: only fires when conversational mode, not for explicit cancel-words. Vow tie-in: **Mythic Conversation**, **Care**.

---

*Apache-2.0 attribution: when adopting CDK's barge-in pipeline into Ember source, preserve the ChatdollKit header reference per Apache-2.0 §4(c). Specifically the `MicrophoneMuteStrategy` enum design, the dual-path trigger architecture, and the `StopChatAsync(continueDialog)` cancel-and-replace contract.*

---
codex_id: 31_AIAVATAR_MAIN_LOOP
title: AIAvatar Main Loop — The Outer State Machine and the Inner One
role: Forge-A
layer: Execution
status: draft
kit_source_refs:
  - Scripts/AIAvatar.cs:25-32 (AvatarMode enum)
  - Scripts/AIAvatar.cs:345-391 (Update)
  - Scripts/AIAvatar.cs:393-424 (UpdateMode)
  - Scripts/AIAvatar.cs:592-630 (OnSpeechListenerRecognized)
  - Scripts/Dialog/DialogProcessor.cs:13-22 (DialogStatus)
  - Scripts/Dialog/DialogProcessor.cs:131-280 (StartDialogAsync state machine)
  - Scripts/Dialog/DialogPriorityManager.cs:1-86
ember_subsystem_targets: [Funi, Hjarta, Strengr]
cross_refs:
  - 30_UNITY_BOOTSTRAP
  - 32_STT_LOOP
  - 36_FUNCTION_CALL_EXEC
  - 11_AIAVATAR_DOMAIN
  - 13_DIALOG_PROCESSOR_DOMAIN
  - sap:3B_AFFECTION_LOOP
  - waifu:30_BASIC_MODE_FLOW
license_posture: Apache-2.0 — adopt with attribution
---

# AIAvatar Main Loop

> *Two state machines stacked, talking through bool comparisons every frame. The outer one is sleepy. The inner one is on fire.*

Forge-A. Eldra. The thing that makes ChatdollKit feel alive is not the avatar's mesh, not the LLM, not the TTS — it's the choreography between the avatar's *mode* (Disabled / Sleep / Idle / Conversation) and the dialog's *status* (seven states from Idling through Error). Two finite-state machines, stacked, with one coupling rule and one mode timer between them. Get the choreography right and the avatar feels attentive but not pushy. Get it wrong and you have either a chatterbox or a hostage. Here is exactly how CDK gets it right and where it leaks.

## The Two State Machines

**Outer (AvatarMode).** Defined at `/tmp/ChatdollKit/Scripts/AIAvatar.cs:25-32`:

```csharp
public enum AvatarMode
{
    Disabled,
    Sleep,
    Idle,
    Conversation,
}
```

Four states. `Disabled` is terminal — set externally to silence the avatar entirely. `Sleep` is "I'm here but I won't respond to anything but the wake word." `Idle` is "I'm listening loosely for a wake word." `Conversation` is "I'm in a turn — speech-listener config is tight, mic-mute is in effect during my response."

**Inner (DialogStatus).** Defined at `DialogProcessor.cs:13-22`:

```csharp
public enum DialogStatus
{
    Idling,
    Initializing,
    Routing,
    Processing,
    Responding,
    Finalizing,
    Error
}
```

Seven states. This is the per-turn machine. `Idling` is between turns. `Initializing` is the first 10ms of a new dialog — cancellation token created, processing ID generated. `Routing` is reserved (the field exists but isn't transitioned-to in the current 0.8.16 code path; it's a vestige of an earlier intent-routing layer). `Processing` is "LLM is generating; we're parsing the stream." `Responding` is "we're playing back voice/animation/face." `Finalizing` is the cleanup-and-OnEnd phase. `Error` is the unhappy path.

## The Coupling Rule

Read `AIAvatar.cs:393-401`. This is the entire bridge between the two machines:

```csharp
// /tmp/ChatdollKit/Scripts/AIAvatar.cs:393-401
private void UpdateMode()
{
    if (DialogProcessor.Status != DialogProcessor.DialogStatus.Idling
        && DialogProcessor.Status != DialogProcessor.DialogStatus.Error)
    {
        Mode = AvatarMode.Conversation;
        modeTimer = conversationTimeout;
        return;
    }
    // ... timeout countdown follows ...
}
```

If the inner machine is in *any* state except `Idling` or `Error`, the outer machine is locked at `Conversation`. The mode timer is pegged at `conversationTimeout` (10s default, `:21`). When the inner machine returns to `Idling`, the outer mode is no longer pinned; the timer counts down each frame; at zero Conversation degrades to Idle, then Idle degrades to Sleep.

Note the *omission* of `Error` from the pin condition. If the dialog fails mid-turn, the avatar is allowed to fall back to Idle immediately — error recovery doesn't keep the user trapped in a Conversation that's broken. Small detail, important UX. SAP and Waifu have nothing this explicit at this level.

## The Per-Frame Update

`Update()` runs every frame (`AIAvatar.cs:345-391`). What it does, in order:

1. **`UpdateMode()`** — recompute outer mode per the coupling rule above.
2. **User message window reconciliation** (`:349-366`) — if dialog is idling and avatar is in Conversation, show the "Listening..." placeholder. If dialog is idling and mode is no longer Conversation, hide.
3. **SpeechListener config swap on mode-transition** (`:368-387`) — if the outer mode just changed, push new silence/recording-duration parameters to the speech listener:

```csharp
// /tmp/ChatdollKit/Scripts/AIAvatar.cs:371-377
if (Mode == AvatarMode.Conversation)
{
    SpeechListener.ChangeSessionConfig(
        silenceDurationThreshold: conversationSilenceDurationThreshold,
        minRecordingDuration: conversationMinRecordingDuration,
        maxRecordingDuration: conversationMaxRecordingDuration
    );
}
```

The conversation defaults are tighter (`0.4s / 0.3s / 10s` at `:40-44`) than idle defaults (`0.3s / 0.2s / 3s` at `:46-50`). Why tighter min-recording but longer max-recording? Because mid-conversation the user is allowed to talk for a long time, but their utterances should not start being recorded after just a fragment of noise (`min`). Idle mode is the opposite: short utterances are likely wake-word candidates so the threshold is lower, but max recording is short because we're not expecting a monologue.

4. **State snapshot** (`:389-390`) — `previousDialogStatus = DialogProcessor.Status; previousMode = Mode;`. The change-detection in step 2 and 3 relies on these.

That's it. Four steps. Per-frame cost is dominated by `DialogProcessor.Status` reads, all `Time.deltaTime` subtractions, and bool comparisons. Sub-microsecond on any platform CDK targets.

## The Dialog Turn — Inside StartDialogAsync

The inner state machine doesn't live in `Update()`. It runs as an awaitable inside `DialogProcessor.StartDialogAsync` (`DialogProcessor.cs:131-280`). Trace it:

```csharp
// /tmp/ChatdollKit/Scripts/Dialog/DialogProcessor.cs:138-145 (compressed)
Status = DialogStatus.Initializing;
processingId = Guid.NewGuid().ToString();
var currentProcessingId = processingId;

if (overwrite)
{
    await StopDialog(true);
}

var token = GetDialogToken();
```

`Status` is mutated to `Initializing`. A new processing ID is minted to allow late callbacks to detect that a *newer* turn has started. If `overwrite` is true (default, from `Chat()` at `AIAvatar.cs:538`), any in-flight dialog is cancelled. A new `CancellationToken` is obtained.

Then `OnRequestRecievedAsync` is invoked (this is the lambda AIAvatar wired in Awake — mic-mute, processing-presentation, user-message-window). It returns a UniTask that we don't await yet.

```csharp
// /tmp/ChatdollKit/Scripts/Dialog/DialogProcessor.cs:170-206 (compressed)
// Configure LLMService
llmService.Tools = toolSpecs;
LLMServiceExtensions.SetExtentions(llmService);

// Call LLM
Status = DialogStatus.Processing;
var messages = await llmService.MakePromptAsync("_", text, llmPayloads, token);
var llmSession = await llmService.GenerateContentAsync(messages, llmPayloads, token: token);
```

State transitions to `Processing`. The LLM is invoked — `GenerateContentAsync` returns immediately with a session object whose `StreamingTask` runs the actual streaming on a background UniTask. The session's `StreamBuffer` fills char-by-char as the LLM emits tokens.

```csharp
// /tmp/ChatdollKit/Scripts/Dialog/DialogProcessor.cs:215-222 (compressed)
// Start parsing voices, faces and animations
var processContentStreamTask = llmContentProcessor.ProcessContentStreamAsync(llmSession, token);

// Await thinking performance before showing response
await OnRequestRecievedTask;

// Show response
Status = DialogStatus.Responding;
var showContentTask = llmContentProcessor.ShowContentAsync(llmSession, token);
```

Here's the cleverest seam in the file. `processContentStreamTask` is started but not awaited — it runs in parallel, consuming the streaming LLM buffer, splitting it on sentence-end characters (see [[33_TTS_PREFETCH]]), extracting `[anim:]` and `[face:]` tags, and prefetching TTS audio for each chunk. `OnRequestRecievedTask` is awaited (it's the "thinking presentation" — random animation + face from the configured pool); only when that finishes does the avatar transition to `Responding`. `showContentTask` then plays the queued voice/animation chunks as fast as they arrive.

```csharp
// /tmp/ChatdollKit/Scripts/Dialog/DialogProcessor.cs:225-233 (compressed)
// Wait for API stream ends
await llmSession.StreamingTask;
if (llmService.OnStreamingEnd != null)
{
    await llmService.OnStreamingEnd(text, payloads, llmSession, token);
}

// Wait parsing and performance
await processContentStreamTask;
await showContentTask;
```

Three awaits in sequence. The LLM stream ends; the parser drains; the playback drains. Only when all three complete does Status transition through `Finalizing` and back to `Idling` in the `finally` block (`:258-279`).

The whole dialog turn is one async method with three concurrent tasks orchestrated by careful await ordering. There is no explicit state-machine table. The state field is mutated at each phase boundary as a *signal* to other components (like AIAvatar.Update polling it), not as a control structure.

## OnSpeechListenerRecognized: Where Words Become Turns

When the SpeechListener fires `OnRecognized` with transcribed text, AIAvatar's handler at `:592-630` runs a priority cascade:

```csharp
// /tmp/ChatdollKit/Scripts/AIAvatar.cs:592-630 (compressed)
private async UniTask OnSpeechListenerRecognized(string text)
{
    if (string.IsNullOrEmpty(text) || Mode == AvatarMode.Disabled) return;

    else if (!string.IsNullOrEmpty(ExtractCancelWord(text)))
        await StopChatAsync();
    else if (!string.IsNullOrEmpty(ExtractInterruptWord(text)))
        await StopChatAsync(continueDialog: true);
    else if (Mode >= AvatarMode.Conversation)
        _ = DialogProcessor.StartDialogAsync(text, payloads: GetPayloads?.Invoke());
    else if (!string.IsNullOrEmpty(ExtractWakeWord(text)))
    {
        if (OnWakeAsync != null) await OnWakeAsync(text);
        var payloads = GetPayloads?.Invoke() ?? new Dictionary<string, object>();
        payloads["IsWakeword"] = true;
        _ = DialogProcessor.StartDialogAsync(text, payloads: payloads);
    }
}
```

Five-rule priority:

1. **Disabled / empty** → ignore.
2. **Cancel word** → stop the current dialog and return to idle.
3. **Interrupt word** → stop current AI response but stay in conversation (immediate barge-in by spoken keyword, separate from voice-barge-in handled in [[37_BARGE_IN_INTERRUPT]]).
4. **Already in Conversation** → treat as a continuation. Direct to LLM.
5. **Wake word match** → enter Conversation. Mark payload `IsWakeword=true` so AIAvatar can suppress the user-message window if configured (`:178-180`).

Note rule 4 takes precedence over rule 5. Once you're in Conversation, you don't need to say the wake word again — any speech becomes input. This is the right default, but it means *every transcript during Conversation gets fired into the LLM.* If the user coughs and the STT transcribes it as "uh", the LLM gets called for "uh". Cost surface.

## DialogPriorityManager — The Forgotten Half

CDK ships a second dialog driver, `DialogPriorityManager` (`Scripts/Dialog/DialogPriorityManager.cs`, 86 lines). It is *not* wired by default in `AIAvatar.Awake`. It's an optional component that wraps `DialogProcessor` with a priority queue:

```csharp
// /tmp/ChatdollKit/Scripts/Dialog/DialogPriorityManager.cs:48-62
public void SetRequest(string text, Dictionary<string, object> payloads = null, int priority = 10)
{
    if (priority == 0)
    {
        _ = dialogProcessor.StartDialogAsync(text + textToAppendNext);
    }
    else
    {
        dialogQueue.Enqueue(new DialogQueueItem() {
            Priority = priority, Text = text + textToAppendNext, Payloads = payloads
        }, priority);
    }
    textToAppendNext = string.Empty;
}
```

`priority = 0` means immediate (interrupt-style). Anything else queues. The `Update()` loop (`:23-46`) polls dialog status, and after `idlingFrameThreshold` (default 2) consecutive Idling frames, dequeues the next request.

This exists for the AITuber and SocketServer use cases — external systems pushing dialog requests asynchronously, possibly faster than the avatar can respond. Forge-B's `3A_AITUBER_CONTROLLER.md` is the canonical study. From the Forge-A side: notice that DialogPriorityManager exists as a *parallel* driver to `AIAvatar.OnSpeechListenerRecognized` — they can both call `DialogProcessor.StartDialogAsync`. If both fire in the same frame, the second overwrites the first (because `StartDialogAsync(overwrite: true)` is the default). That's a design choice, not a bug.

## Where It Breaks

- **The Routing state is dead code.** `DialogStatus.Routing` (`DialogProcessor.cs:17`) is declared but never assigned. Old intent-routing infrastructure was deprecated and the enum value was kept for binary compatibility. Reading the code, you'd think there's a routing phase between Initializing and Processing. There isn't. Strip it from any port to Ember.
- **`OnRequestRecievedAsync` is awaited after LLM stream starts.** The user's "Listening..." indicator is set *before* the LLM call begins, but the thinking-presentation animation is awaited *after*. If the LLM streams its first token in <50ms (Claude Haiku does this), the thinking animation may not have time to play. The await ordering is correct, but the UX assumption (that LLM is slow) is increasingly false on small models.
- **`previousDialogStatus` is updated unconditionally at end of Update.** If three dialog status transitions happen within a single frame (Initializing → Processing → Responding can all run in ~5ms), the change-detection only sees the last one. AIAvatar's user-message-window update misses the intermediate states. In practice this is fine for the listening/responding UI, but a future Forge agent extending the surface should know.
- **Cancel/interrupt-word matching is case-insensitive exact-match.** `ExtractCancelWord` (`:478-495`) compares stripped lowercase. If the user says "stop please" instead of "stop", and `CancelWords = ["stop"]`, no match. Wake-word matching is more forgiving (allows prefix/suffix tolerance via `WordWithAllowance`), but cancel/interrupt don't get the same affordance.

## Where It Surprises

- **The mode timer pegs but doesn't reset on every transcript.** While in Conversation mode, `modeTimer = conversationTimeout` is re-pegged every frame DialogProcessor is non-Idle (line `399`). But the moment the dialog returns to Idling, the timer starts counting from `conversationTimeout`. So after each turn, the user has 10s to start the next turn before the mode degrades to Idle. Short enough to feel attentive, long enough not to force a wake word every utterance. This is well-tuned default.
- **Conversation mode is "≥" not "==" in `OnSpeechListenerRecognized` (line `609`).** `Mode >= AvatarMode.Conversation` is true only for Conversation since Conversation is the highest enum value. Probably a defensive ordering choice in case a future mode is added higher in the enum. Brittle but harmless.
- **The `BackgroundRequestPrefix` (default `"$"`) (`:71`).** Any text starting with `$` is routed to the LLM but doesn't show in the user-message-window. This is the API surface for *programmatic* dialog requests — Strengr-style scripted prompts to the avatar that the user shouldn't see typed back. Tiny feature, surprisingly load-bearing for the AITuber sister project.

## Cross-References

- [[30_UNITY_BOOTSTRAP]] — how all the callbacks invoked here got wired
- [[32_STT_LOOP]] — what produces the `OnRecognized` text that drives the cascade
- [[36_FUNCTION_CALL_EXEC]] — what happens *inside* the LLM session when tool-calls fire
- [[13_DIALOG_PROCESSOR_DOMAIN]] — domain-level analysis of `DialogProcessor`
- [[sap:3B_AFFECTION_LOOP]] — contrast: SAP's affection state machine (driven by file I/O, not events)
- [[waifu:30_BASIC_MODE_FLOW]] — contrast: Waifu has *no* visible state machine — the cloud SDK owns it

## What This Means for Ember

**Adopt:**

- **Two-machine pattern (outer mode + inner dialog status) with one coupling rule.** This separation is genuinely good — the outer machine controls deployment-policy decisions (mic config, message-window state); the inner one controls per-turn flow. Ember's Funi should ship with this exact dual-state-machine pattern (`AIAvatar.cs:25-32` + `DialogProcessor.cs:13-22`, Apache-2.0 attribution). The coupling rule belongs in Funi as `update_mode_from_dialog_status()`.
- **The `Mode == Conversation ? tight : loose` SpeechListener config swap** (`AIAvatar.cs:368-387`). This is a tiny pattern with outsized UX value. Adopt as-is into Funi's listener config.
- **The five-rule priority cascade in `OnSpeechListenerRecognized`** (`:592-630`). The ordering (cancel > interrupt > continuation > wake) is correct. Adopt the structure, replace the string matching with a typed enum (see Adapt).

**Adapt:**

- **String-match cancel/interrupt/wake words.** Adopt the cascade, but replace `ExtractCancelWord` / `ExtractInterruptWord` / `ExtractWakeWord` with a single `Munnr.classify_intent(text) -> IntentKind` that uses fuzzy matching with the `WordWithAllowance` prefix/suffix tolerance pattern uniformly. Don't repeat the loop three times.
- **DialogPriorityManager.** Useful pattern for external dialog drivers. Re-implement in Strengr as `Strengr.queue_prompt(text, priority)` with the same "wait 2 idle frames before dequeue" guard — but make it the *only* path. Don't have two parallel drivers (`AIAvatar.OnSpeechListenerRecognized` + `DialogPriorityManager.SetRequest`) able to race for the same `StartDialogAsync`.
- **The vestigial `Routing` state.** Strip from any port. Don't carry binary-compat baggage.

**Avoid:**

- **Per-frame string comparisons in Update.** CDK is fine because Update runs at 30-60Hz on modern hardware. On a Pi-zero baseline (Ember's smallness floor), per-frame anything is a budget concern. Ember's equivalent should be event-driven, not polled.
- **Single global processingId.** `DialogProcessor.processingId` is a single string field. Concurrent dialog requests (e.g. two simultaneous tool-call resolutions) can't be disambiguated. Ember should use per-request UUIDs threaded through cancellation tokens, not a global field.

**Invent:**

- **Hjarta Turn Tape.** Every dialog turn produces a typed `TurnRecord { id, started_at, mode, status_transitions[], llm_session_id, tts_chunks[], duration_ms, outcome }`. The DialogProcessor state-machine *emits* this record at `Finalizing`. Hjarta archives it. Munnr can replay it as a transcript. This is what CDK is *almost* doing implicitly via `Debug.Log` scattered through the code; make it explicit and queryable in Ember.
- **Strengr Speculative Continuation.** When DialogStatus is `Idling` but the mode timer hasn't degraded out of Conversation, Strengr can begin speculatively pre-encoding context for the next likely turn. The `mode_timer > 0 && status == Idling` window is wasted in CDK. Ember can use it.

---

*Apache-2.0 attribution: when adopting the AIAvatar coupling pattern or DialogProcessor state machine into Ember source, preserve the ChatdollKit header reference per Apache-2.0 §4(c).*

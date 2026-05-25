---
codex_id: 13_DIALOG_PROCESSOR_DOMAIN
title: Dialog Processor Domain — The Seven-Status Pipeline and the Priority Queue
role: Architect
layer: Domain
status: draft
chatdoll_source_refs:
  - Scripts/Dialog/DialogProcessor.cs:1-346
  - Scripts/Dialog/DialogPriorityManager.cs:1-86
  - Scripts/Dialog/MessageWindow/IMessageWindow.cs
  - Scripts/Dialog/MessageWindow/MessageWindowBase.cs
  - Scripts/Dialog/MessageWindow/SimpleMessageWindow.cs
  - Scripts/LLM/LLMContentProcessor.cs:29-253
  - Scripts/AIAvatar.cs:146-243
  - Scripts/IO/PriorityQueue.cs:1-111
ember_subsystem_targets: [Funi, Strengr, Munnr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_AIAVATAR_DOMAIN
  - 10_domain/16_LLM_SERVICE_DOMAIN
  - 10_domain/19_TOOL_DOMAIN
  - 20_interface/20_LLM_SERVICE_INTERFACE
  - sap:12_AGENT_CORE_DOMAIN
  - waifu:11_DUAL_MODE_PATTERN
---

# Dialog Processor Domain
## The Seven-Status Pipeline and the Priority Queue

*— Rúnhild Svartdóttir, Architect*

> *A dialog state machine is the architectural problem most chat systems pretend they do not have. CDK admits the problem and writes the state machine down. The result is a 346-line file that does what SAP scatters across two thousand.*

`Scripts/Dialog/` is three files plus a message-window subfolder. The two architecturally interesting ones — `DialogProcessor.cs` (346 LOC) and `DialogPriorityManager.cs` (86 LOC) — own the *conversation flow* of an avatar: when an utterance is accepted, how it is processed, what happens when it is interrupted, when it ends, and what happens to a second utterance that arrives while the first is in flight. This domain is the **dialogic spine** of CDK and the closest CDK comes to having a centralised controller.

What it teaches Ember: a typed conversational state machine, written down, is short and useful. SAP refused to write the state machine down ([[sap:10_DOMAIN_MAP]] §4 had to *reconstruct* it from `server.py:2400-6000`). Waifu's kit had no state machine at all ([[waifu:10_DOMAIN_MAP]] §1). CDK puts it in 346 lines and a seven-state enum. This is the right move.

---

## 1. The Subject Itself

**What the domain is:** the *dialogic* lifecycle layer of CDK. Above it sits AIAvatar, which decides whether a new utterance should be sent here. Below it sits the LLMService, which generates the response. In between is this domain, owning *how the conversation flows*.

**What it owns:**

- The `DialogStatus` enum (`DialogProcessor.cs:13-22`): `Idling / Initializing / Routing / Processing / Responding / Finalizing / Error`. Seven states, well-named. (`Routing` is currently unused at the code level — it's vestigial from a prior version or pre-allocated for a future router; see §3.5.)
- The seven async callback hooks (`OnStartAsync`, `OnRequestRecievedAsync`, `OnBeforeProcessContentStreamAsync`, `OnResponseShownAsync`, `OnEndAsync`, `OnStopAsync`, `OnErrorAsync` — lines 28-34) that AIAvatar (and any other consumer) can register to react to lifecycle events.
- The `LLMService` auto-selection (lines 81-113) — picks the first enabled `ILLMService` component on the GameObject.
- The `toolResolver` dictionary and `toolSpecs` list (lines 39-40, 115-128) — populated from `gameObject.GetComponents<ITool>()` at `Awake`, used to build the LLM's function-calling spec and to dispatch tool calls back to their handlers.
- The cancellation-token discipline (lines 25, 326-330) — every dialog has a fresh `CancellationTokenSource`; cancelling cancels the *entire* dialog: stream, animation, voice, tool.
- The **merge-request window** (lines 45-50, 175-190) — if two requests come in within `mergeRequestThreshold` seconds, concatenate them and prepend a "previous request was cancelled, respond to this:" framing instruction.
- The **timestamp insertion** (lines 52-57, 193-202) — if more than `timestampInsertionInterval` seconds have passed since the last injection, prepend `"Current date and time: <now>\n\n"` to the next request. Lets the LLM stay aware of elapsed time without a tool call.
- The **priority queue** of pending requests (in `DialogPriorityManager`, 86 LOC) — multiple sources can enqueue requests with priorities, and the queue fires them one at a time when the dialog is `Idling`.

**What it does NOT own:**
- The actual LLM call — owned by the active `ILLMService` ([[16_LLM_SERVICE_DOMAIN]]).
- Animation, face, voice playback — owned by `ModelController` ([[12_MODEL_CONTROLLER_DOMAIN]]).
- Mic muting — owned by `MicrophoneManager` via AIAvatar's callbacks ([[17_MICROPHONE_MANAGER_DOMAIN]]).
- Wake-word / cancel-word matching — owned by AIAvatar ([[11_AIAVATAR_DOMAIN]]).
- Tool *implementations* — owned by user-supplied `ToolBase` subclasses ([[19_TOOL_DOMAIN]]).

---

## 2. How It Works

### 2.1 The seven-state lifecycle

The status enum:
```csharp
// /tmp/ChatdollKit/Scripts/Dialog/DialogProcessor.cs:13-22
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

A normal turn walks:
```
Idling
  └── StartDialogAsync invoked
        ├── Status = Initializing (line 138)
        ├── (overwrite=true) StopDialog → cancels prior dialog, cleans token source
        ├── Status = Processing (line 205)
        │     ├── llmService.MakePromptAsync (builds messages)
        │     ├── llmService.GenerateContentAsync (starts streaming task)
        │     ├── OnBeforeProcessContentStreamAsync (optional hook)
        │     └── llmContentProcessor.ProcessContentStreamAsync (parallel)
        ├── Status = Responding (line 221)
        │     └── llmContentProcessor.ShowContentAsync (drains queue → ModelController.AnimatedSay)
        ├── await llmSession.StreamingTask
        ├── (OnStreamingEnd hook from llmService)
        ├── (OnResponseShownAsync hook)
        ├── (catch) Status = Error (line 246)
        │     └── OnErrorAsync(text, payloads, ex, token)
        └── (finally) Status = Finalizing (line 260)
              ├── OnEndAsync(endConversation, token)
              └── Status = Idling (line 277)
```

Seven labelled phases, two of them (Initializing, Finalizing) bookend the substantive ones (Processing, Responding). Error is a side-state reachable from Processing or Responding via thrown exceptions. **Routing is the unused state** — see §3.5.

The status field is *publicly readable* (`public DialogStatus Status { get; private set; }`, line 23). AIAvatar reads it every frame (`AIAvatar.cs:350` checks `DialogProcessor.Status == DialogProcessor.DialogStatus.Idling` to decide whether to show "Listening..." in the user message window). `DialogPriorityManager.Update` (line 27) reads it to decide whether to dequeue the next request. **The status is an observable contract** — anyone with a reference to the `DialogProcessor` can read it.

### 2.2 The `StartDialogAsync` pipeline

`StartDialogAsync(text, payloads, overwrite, endConversation)` (lines 131-280) is the entry point. The pipeline:

1. **Guard the empty case** (lines 133-136): no text, no payloads → return without doing anything.
2. **Initialise** (lines 138-140): `Status = Initializing`; `processingId = Guid.NewGuid()`; capture `currentProcessingId` (the *id-at-time-of-call*) — this is the lock that prevents a finishing dialog from resetting status when a *second* dialog has already started after it (line 274's `if (currentProcessingId == processingId)`).
3. **Cancel prior** (lines 142-146): if `overwrite=true`, call `StopDialog(true)` which cancels the prior token source.
4. **Get a fresh token** (line 148): `GetDialogToken()` creates a new `CancellationTokenSource` and returns its token.
5. **Fire `OnRequestRecievedAsync`** (lines 154-162) — held as a `UniTask` to await later (after stream-process is set up). This is the *thinking-presentation* phase — AIAvatar uses this to start the processing animation.
6. **Wrap payloads** (line 165-168): the request `payloads` go inside a top-level `RequestPayloads` key — this is a versioning hack for older v0.7 compatibility (per the comment, line 164).
7. **Configure LLMService** (lines 171-172): set `llmService.Tools = toolSpecs`; set the extension hooks (`HandleExtractedTags`, `CaptureImage`, `OnStreamingEnd`) via `LLMServiceExtensions.SetExtentions`.
8. **Merge consecutive requests** (lines 174-190) — if the previous request was within the merge window, concatenate and prepend the framing instruction.
9. **Inject timestamp** (lines 193-202) — if interval expired, prepend `"Current date and time: <now>\n\n"`.
10. **Call LLM** (lines 205-207): `Status = Processing`; `MakePromptAsync` → `GenerateContentAsync`. The returned `llmSession` has a `StreamingTask` that runs in parallel.
11. **`OnBeforeProcessContentStreamAsync`** (lines 209-212) — pre-process hook; the only sample user is AIAvatar in some sister-project setups.
12. **Start parsing in parallel** (line 215): `llmContentProcessor.ProcessContentStreamAsync(llmSession, token)` — runs concurrently with the streaming task.
13. **Await thinking presentation** (line 218): the `OnRequestRecievedTask` from step 5 — *now* we wait for AIAvatar's processing animation to finish setting up.
14. **Show response** (lines 220-222): `Status = Responding`; `llmContentProcessor.ShowContentAsync(llmSession, token)` — drains the queue and dispatches to `ModelController.AnimatedSay`.
15. **Wait for everything to finish** (lines 225-233): stream task, optional `OnStreamingEnd`, content-process task, show task. *All four* must complete before the dialog is considered done.
16. **`OnResponseShownAsync`** (lines 237-240) — post-show hook.
17. **Catch** (lines 242-256): if any exception escaped *and* the token wasn't already cancelled, set `Status = Error`, stop, get a *new* token (because the old one was cancelled), and fire `OnErrorAsync`.
18. **Finally** (lines 258-279): `Status = Finalizing`; fire `OnEndAsync`; if `currentProcessingId == processingId` (no second dialog started in the meantime), reset `Status = Idling`.

**Sixteen distinct phases in one async method.** The orchestration is correct, but the method is long. The architectural lesson: each phase is *one statement* — the LLMService does the heavy lifting; the ContentProcessor handles parsing; the ModelController does playback. DialogProcessor is the *coordinator*, not the worker — and that makes 280 lines acceptable in a way `AIAvatar.cs`'s 664 lines is not.

### 2.3 The cancellation choreography

The most subtle piece. `dialogTokenSource` (line 25) is the *single* cancellation source for the *entire* dialog. When it cancels:
- The streaming task notices (per-provider implementations check `token.IsCancellationRequested`).
- `ProcessContentStreamAsync` notices (line 47, while loop guard).
- `ShowContentAsync` notices (line 231, while loop guard).
- `ModelController.AnimatedSay` notices (line 189, inner loop guard).
- `SpeechController.Say` notices (lines 47, 102, etc.).

A single cancel propagates through five layers of async without a single explicit `Cancel()` call past the first one. The token-passing discipline is uniform: every async method takes a `CancellationToken token` parameter; every `await` either passes the token or uses `cancelable: token`; every loop checks `token.IsCancellationRequested`.

The *re-acquire after error* pattern (line 251): `await StopDialog(true); token = GetDialogToken();`. The old token is dead; a new one is needed to actually *say* the error message (which involves its own animations/voice). This is correct and easy to get wrong — many systems try to fire side effects with a cancelled token and silently swallow the result.

### 2.4 The `DialogPriorityManager`

`DialogPriorityManager.cs` (86 LOC) is a *separate component* attached to the same GameObject. Its job: queue requests that arrive while the dialog is busy, and fire them one at a time when idling.

```csharp
// /tmp/ChatdollKit/Scripts/Dialog/DialogPriorityManager.cs:23-46
private void Update()
{
    if (dialogProcessor == null) return;

    if (dialogProcessor.Status == DialogProcessor.DialogStatus.Idling)
    {
        idlingFrameCount += 1;

        if (idlingFrameCount >= idlingFrameThreshold)  // default 2 frames
        {
            idlingFrameCount = 0;
            if (!dialogQueue.IsEmpty())
            {
                var dialogRequest = dialogQueue.Dequeue();
                _ = dialogProcessor.StartDialogAsync(dialogRequest.Text, dialogRequest.Payloads);
            }
        }
    }
    else
    {
        idlingFrameCount = 0;
    }
}
```

Two-frame idle buffer before dispatching the next queued request — this prevents a race where the *previous* dialog's finalization (status flipping briefly to Idling) immediately dispatches a queued one before any other observer (like AIAvatar) has seen the transition.

`SetRequest(text, payloads, priority)` (lines 48-62) accepts a priority. Priority `0` is the *bypass priority* — fire immediately, do not queue. Any other priority goes into the queue.

The queue is a `PriorityQueue<DialogQueueItem>` (`IO/PriorityQueue.cs:1-111`) — a `SortedList<int, Queue<T>>` where lower priority numbers fire first. Standard data structure, hand-rolled, 111 LOC, no third-party dependency. Adopt freely.

`SetRequestToAppendNext(text)` (lines 64-67) — a *side channel* to prepend extra context to the next-dispatched request. The text is concatenated with `"\n\n"` separator. Used for things like injecting a relevant memory recall before the user's next turn.

`ClearDialogRequestQueue(priority)` (lines 74-77) — clear all (priority=0) or just one priority bucket.

The Priority Manager is *small* — 86 lines — and *complete*. SAP has nothing equivalent (its bot-fan-in just hammers the server). Waifu has no priority concept. CDK's priority queue is one of the patterns Ember should lift wholesale.

### 2.5 The auto-select of `ILLMService`

`SelectLLMService(ILLMService llmService = null)` (lines 81-113):

```csharp
public void SelectLLMService(ILLMService llmService = null)
{
    var llmServices = gameObject.GetComponents<ILLMService>();

    if (llmService != null) {
        this.llmService = llmService;
        foreach (var llms in llmServices)
            llms.IsEnabled = llms == llmService;
        return;
    }
    if (llmServices.Length == 0) {
        Debug.LogError($"No LLMServices found");
        return;
    }
    foreach (var llms in llmServices) {
        if (llms.IsEnabled) {
            this.llmService = llms;
            return;
        }
    }
    Debug.LogWarning($"No enabled LLMServices found. Enable {llmServices[0]} to use.");
    llmServices[0].IsEnabled = true;
    this.llmService = llmServices[0];
}
```

Three behaviours in one function:
- Explicit (caller passed `llmService != null`): set that one, flip everyone else off.
- Implicit (no argument): scan for the first `IsEnabled == true` and use it.
- Fallback: no one enabled? Force-enable the first found.

This is the **pluggable LLM** pattern done with a checkbox per provider. To swap from ChatGPT to Claude: in the Unity Inspector, untick `IsEnabled` on `ChatGPTService` and tick it on `ClaudeService`. No config file. No rebuild. No code change.

### 2.6 The `LoadLLMTools` discovery

```csharp
// /tmp/ChatdollKit/Scripts/Dialog/DialogProcessor.cs:115-128
public void LoadLLMTools()
{
    toolResolver.Clear();
    toolSpecs.Clear();
    foreach (var tool in gameObject.GetComponents<ITool>())
    {
        if (tool.IsEnabled)
        {
            var toolSpec = tool.GetToolSpec();
            toolResolver.Add(toolSpec.name, tool);
            toolSpecs.Add(toolSpec);
        }
    }
}
```

Every `ITool` on the GameObject is registered if enabled. `toolResolver` (name → tool instance) lets the LLM's function-call response be dispatched back to the right `ITool.ExecuteAsync` call. `toolSpecs` (list of `ILLMTool`) is passed to the LLM service as the function spec.

To add a new tool: drop a `ToolBase` subclass component on the GameObject, tick `IsEnabled`. No registration code anywhere. The discovery pattern matches the LLMService selection — uniformly via component enumeration. See [[19_TOOL_DOMAIN]] for the deep dive.

### 2.7 The merge-request window

```csharp
// /tmp/ChatdollKit/Scripts/Dialog/DialogProcessor.cs:175-190
if (mergeRequestThreshold > 0)
{
    var now = DateTime.UtcNow;
    var requestInterval = (now - previousRequestAt).TotalSeconds;
    if (mergeRequestThreshold > requestInterval)
    {
        text = previousRequestText + "\n" + text;
        if (!text.StartsWith(mergeRequestPrefix))
            text = mergeRequestPrefix + "\n\n" + text;
    }
    previousRequestText = text;
    previousRequestAt = now;
}
```

The `mergeRequestPrefix` (line 48):
> "Previous user's request and your response have been canceled. Please respond again to the following request:"

A real teaching: if the user starts a question, then interrupts themselves with a correction, the LLM is told *that's what just happened* and is given both phrasings to work with. SAP and Waifu have nothing equivalent.

The cost: `mergeRequestThreshold > 0` must be configured (default is `0`, off). When on, the *previous* request that was cancelled is dragged forward — including if the user *deliberately* cancelled. Ember should tie this to the cancellation *reason*: merge if cancelled by user-correction (interrupt-word match), not if cancelled by explicit cancel-word.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The 280-line `StartDialogAsync`

The method is long. Sixteen phases, three nested try/catch/finally levels. While each phase is a simple statement, the *whole* method needs an attentive reader. Refactoring into smaller methods is straightforward (extract `MergeRequestIfNeeded`, `InjectTimestampIfNeeded`, `StreamAndPerform`, `HandleErrorIfAny`) but CDK does not do it. Ember should.

### 3.2 `Routing` status is unused

The enum has `Routing` (line 16) between `Initializing` and `Processing`. Searching `git grep "DialogStatus.Routing"` in CDK returns *zero* assignments in the codebase. It is either vestigial or pre-allocated for a future "decide which sub-agent / which LLM to route to" phase. Right now, it is documentation noise.

### 3.3 The `processingId` race window

`currentProcessingId == processingId` (line 274) is the test for "no second dialog started while we were finishing." But the assignment `processingId = Guid.NewGuid()` (line 139) happens *before* the cancel-prior (line 145). So the order is: (a) new dialog sets `processingId` to GUID-2, (b) old dialog is cancelled, (c) old dialog's `finally` runs with `currentProcessingId == GUID-1`, sees `processingId == GUID-2`, correctly *does not* reset status. Correct, but subtle.

The race window: between (a) and (b), if the old dialog finished naturally *before* the cancel propagated, its `finally` would see `currentProcessingId == GUID-1, processingId == GUID-2` — and correctly not reset. The pattern is right. But it requires the reader to trace three sequence points. Ember should comment this.

### 3.4 No state-transition validation

There is no guard against external code (or future contributors) writing `Status = SomeRandomState` from outside — `Status` has a `private set` (line 23), so external write is prevented. But *internal* writes have no transition-validity check. Going from `Idling` directly to `Responding` without passing through `Initializing` would be a bug; nothing in the code catches that. A typed state machine library (or a `TransitionTo(newStatus)` helper that validates) would help.

### 3.5 Tool-call dispatch is implicit

`toolResolver` is built by `LoadLLMTools` (lines 115-128) but the *actual dispatch* of a tool call from the LLM happens in the per-provider service (`ChatGPTService`, `ClaudeService`, etc.). Each provider has its own JSON shape for function calls; each parses out the function name; each calls `toolResolver[name].ExecuteAsync(args)`. The dispatch site is *not* in DialogProcessor. The pattern is correct (each provider knows its own format) but the *integration* with `toolResolver` is by-string and not type-checked. See [[26_TOOL_FUNCTION_CALL_INTERFACE]] for the per-provider variation.

### 3.6 The merge-window prefix is hardcoded English/Japanese-style

`"Previous user's request and your response have been canceled. Please respond again..."` (line 48). Works fine for English- and Japanese-prompt-tuned LLMs. For other languages, the prefix is a foreign-language instruction; the LLM may or may not honour it. Ember should make this `Dict[str, str]` keyed by `SystemMessageContent` language.

### 3.7 The crisp parts (inventory)

- The **`DialogStatus` enum is the right granularity.** Seven states is enough to express what's happening without exploding. The state names match the phases.
- The **callback-hook pattern** for `OnStartAsync` etc. is clean dependency-inversion. AIAvatar registers what it cares about; DialogProcessor invokes blindly. No other module needs to be edited to add a new behaviour.
- The **token-passing discipline** is uniform and correct. One cancel propagates through five async layers.
- The **`processingId` lifecycle lock** is the right pattern for "this `finally` belongs to *which* turn?"
- The **auto-select-by-enabled-flag** for both `ILLMService` and `ITool` is the simplest possible plug-in mechanism.
- The **two-frame idling buffer** in `DialogPriorityManager` is the kind of small empirical fix that takes experience to know you need.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 1 — Dialog in the macro shape
- [[11_AIAVATAR_DOMAIN]] §2.1 — AIAvatar's seven registered callbacks
- [[16_LLM_SERVICE_DOMAIN]] — the LLMService DialogProcessor selects from
- [[19_TOOL_DOMAIN]] — the ITool subsystem DialogProcessor discovers
- [[20_LLM_SERVICE_INTERFACE]] — the ILLMService contract
- [[sap:12_AGENT_CORE_DOMAIN]] — SAP's scattered equivalent (no enum, no state machine)
- [[waifu:11_DUAL_MODE_PATTERN]] — Waifu's "no dialog state machine, just two modes"

---

## What This Means for Ember

**Adopt:**
- The **seven-state `DialogStatus` enum** as Ember's `EmberConversationState`. Source: `Scripts/Dialog/DialogProcessor.cs:13-22`, Apache-2.0 attribution required. Drop the unused `Routing` state until Ember has a use for it — *do not pre-allocate*.
- The **callback-hook lifecycle** (`OnStartAsync`, `OnRequestRecievedAsync`, `OnBeforeProcessContentStreamAsync`, `OnResponseShownAsync`, `OnEndAsync`, `OnStopAsync`, `OnErrorAsync` — lines 28-34). Adopt as Ember's Sögumiðla event types — each lifecycle moment is a typed event with a versioned payload schema. Subscribers register declaratively in YAML, not imperatively in `Awake()`.
- The **`DialogPriorityManager` + `PriorityQueue<T>` pattern**. Source: `Scripts/Dialog/DialogPriorityManager.cs:1-86` + `Scripts/IO/PriorityQueue.cs:1-111`. Ember's Strengr (the scheduler) lifts this as `MessagePriorityQueue`, with priority `0` as bypass. The two-frame idling buffer becomes an explicit `idle_grace_ms` parameter (default 100ms).
- The **`SelectLLMService` enabled-flag auto-pick** (lines 81-113). Adopt as Ember's `select_first_enabled(candidates)` utility. Apache-2.0 attribution required.
- The **`LoadLLMTools` component-discovery pattern** (lines 115-128). Adopt as Ember's `discover_tools(registry)` — every `ToolBase` subclass with `enabled=True` registered at runtime; no manual list.

**Adapt:**
- **`StartDialogAsync` as a sixteen-phase async method** — adapt to Ember's six-method split: `_initialize_turn`, `_assemble_prompt`, `_call_llm`, `_stream_and_perform`, `_finalize_turn`, `_handle_error`. Each method is < 50 lines per the coding laws. The orchestration in the top-level method is a sequence of awaits, not a sprawl of logic.
- The **merge-request window** (lines 175-190). Adapt as Ember's `merge_policy: 'on_interrupt_word' | 'on_any_cancel' | 'never'` — make the *reason for cancel* part of the merge decision. Interrupt-word match → merge. Cancel-word match → discard previous. Default `'on_interrupt_word'`.
- The **timestamp injection** (lines 193-202). Adapt as Ember's `temporal_context_injector` — a Sögumiðla-event-driven module that injects time, location, recent-memory-summary, current-mood depending on configured triggers. The "current time" injection is one specialisation.
- The **`processingId` race lock** — adapt as Ember's `turn_id: UUID` carried through every Sögumiðla event for the turn. The race condition is solved the same way; Ember just makes the id visible to all observers.

**Avoid:**
- **A vestigial enum value** (`Routing`, line 16). Either implement it or remove it. Documentation noise is documentation debt.
- **A 280-line orchestrator method** even if every phase is one statement. Ember's coding laws cap methods at 50 lines. Split.
- **Implicit state transitions** without validation. Ember's `EmberConversationState` enum is paired with a typed transition guard that asserts validity (`Idling → Initializing → Processing → Responding → Finalizing → Idling`, or `* → Error → Idling` from any state).
- **Hardcoded English-style framing prefixes for LLM context.** Ember's prefixes are per-language YAML.

**Invent:**
- **The Turn ID as First-Class Identity.** Every Ember turn gets a UUID at `Initializing`. The UUID is attached to every Sögumiðla event for the turn (`TurnStarted`, `LLMRequestSent`, `LLMStreamChunk`, `ToolCallInvoked`, `EmbodimentFrameEmitted`, `TurnEnded`). Querying the session log for `turn_id == X` gives the *complete* trace. CDK has `processingId` but uses it only internally; Ember exposes it for diagnostics. The Turn Trace becomes the unit of post-hoc review.
- **The State Transition Audit Trail.** Every `Status` change emits a Sögumiðla `StateTransition(from, to, reason, turn_id)` event. Anyone (UI, log, post-mortem) can subscribe. CDK requires `previousDialogStatus` polling (`AIAvatar.cs:108, 354`); Ember pushes.
- **The Priority-Bypass Vow.** Priority `0` in Ember's queue is reserved for *system messages* — never user input. User input always has priority ≥ 1. This prevents a malformed external input from queue-jumping past pending dialogs. Combined with [[18_NETWORK_DOMAIN]]'s socket-authentication invent, the priority gate is hard.
- **The Cancellation Reason Codes.** CDK's cancellation is a single `CancellationToken` with no metadata. Ember's `TurnCancellationToken` carries a typed reason: `UserCancelWord`, `UserInterruptWord`, `Timeout`, `NewTurnPreempted`, `ToolError`, `SystemShutdown`. The reason informs the merge-window policy, the error message, and the log entry. *Cancellation is information; treat it as such.*
- **The Tool Spec Versioning.** Each `ITool.GetToolSpec()` returns a spec; Ember's equivalent additionally returns a `version: str`. The DialogProcessor logs which tool versions were available at turn time. When a regression appears, the tool-version trace tells you whether the tool changed. CDK assumes specs are stable; Ember assumes they will drift.

*Apache-2.0 attribution: when patterns from `ChatdollKit/Scripts/Dialog/` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

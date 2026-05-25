---
codex_id: 30_UNITY_BOOTSTRAP
title: Unity Bootstrap — One MonoBehaviour to Wake Them All
role: Forge-A
layer: Execution
status: draft
kit_source_refs:
  - Scripts/AIAvatar.cs:1-665
  - Scripts/AIAvatar.cs:113-335 (Awake)
  - Scripts/AIAvatar.cs:337-343 (Start)
  - Scripts/AIAvatar.cs:345-391 (Update)
  - Scripts/Dialog/DialogProcessor.cs:59-71 (DialogProcessor.Awake)
  - Scripts/Model/ModelController.cs:58-95 (ModelController.Awake/Start)
ember_subsystem_targets: [Funi, Hjarta, Munnr]
cross_refs:
  - 31_AIAVATAR_MAIN_LOOP
  - 11_AIAVATAR_DOMAIN
  - 1C_UNITY_LIFECYCLE_DOMAIN
  - sap:30_ELECTRON_BOOTSTRAP
  - waifu:30_BASIC_MODE_FLOW
license_posture: Apache-2.0 — adopt with attribution
---

# Unity Bootstrap

> *No spawn, no port, no handshake. Just `Awake()` running across a graph of MonoBehaviours that already know where each other live.*

I'm Eldra. Forge-A. Fire-instance. After mining SAP's two-process stdout-handshake bootstrap and Waifu's thirty-one-line JSX prop wall, ChatdollKit is a different animal. The Unity Player has already done the spawn. The scene graph has already done the wiring. By the time `AIAvatar.Awake()` fires at `/tmp/ChatdollKit/Scripts/AIAvatar.cs:113`, every dependency it could ever need is sitting one `GetComponent<T>()` away. Boot has become introspection. That has consequences — good ones, and ones we have to be very careful about.

## The Scene Is the Container

SAP's `main.js:498` calls `spawn()` to bring a Python child to life. Waifu's `BasicMode.tsx:19` mounts a React component that opens a WebRTC session to a cloud-hosted avatar. ChatdollKit does neither. The whole boot story is: *the user dragged a prefab into a Unity scene.* The prefab carries an `AIAvatar` MonoBehaviour, a `ModelController`, a `DialogProcessor`, an `LLMContentProcessor`, one of N enabled `ISpeechListener` implementations, one of M enabled `ISpeechSynthesizer` implementations, and a chosen `ILLMService`. They are siblings on the same GameObject. Unity's player loop calls `Awake()` on each of them in unspecified order, then `Start()`, then `Update()` every frame.

Read `AIAvatar.cs:115-119`:

```csharp
// /tmp/ChatdollKit/Scripts/AIAvatar.cs:115-119
// Get ChatdollKit components
MicrophoneManager = MicrophoneManager ?? gameObject.GetComponent<IMicrophoneManager>();
ModelController = ModelController ?? gameObject.GetComponent<ModelController>();
DialogProcessor = DialogProcessor ?? gameObject.GetComponent<DialogProcessor>();
LLMContentProcessor = LLMContentProcessor ?? gameObject.GetComponent<LLMContentProcessor>();
```

That is the entire dependency-injection ceremony. Four `GetComponent<T>()` calls, null-coalesced with optional Inspector overrides. There is no DI container. There is no service locator. There is no constructor. The scene is the container. The Inspector is the wiring diagram. Designers see the same boxes as code.

This is the Unity-native local pattern in its purest form. SAP needs a Python process to even talk to itself. Waifu needs a WebRTC room to render a face. CDK needs *a prefab with the right MonoBehaviours dropped into a scene.* The whole boot graph fits on one screen of the Unity Inspector.

## The Six Phases of Awake

`AIAvatar.Awake` is 220 lines (`AIAvatar.cs:113-335`). It is not the kind of thing you'd write by hand if you didn't have to — but Unity's lifecycle gives you exactly one place to register cross-component callbacks before the first frame, and Awake is it. Read in order, it walks through six phases:

**Phase 1 — Component resolution (`:115-119`):** the four `GetComponent` calls above. Note: every one is a sibling lookup, never a child or descendant search. The author wants the whole avatar to live on one GameObject. This is a design decision with cost — see Where It Breaks.

**Phase 2 — MicrophoneManager threshold (`:121-122`):** push the inspector-set `VoiceRecognitionThresholdDB` (default `-50.0f`) into the mic gate. The mic is already running by the time we get here, because `MicrophoneManager.Start()` (`MicrophoneManager.cs:64-79`) called `StartMicrophone()` if `AutoStart` was true. The mic boots itself; AIAvatar just configures it.

**Phase 3 — ModelController speech callbacks (`:124-142`):** subscribe `OnSayStart` and `OnSayEnd` on the SpeechController. Inline lambdas — no separate method, no event-bus indirection. When a voice is about to play, show the character message window; when it ends, hide it. This is direct callback wiring with no listener registry, which means **only one subscriber can exist per event.** That is the trade — simplicity for non-extensibility.

**Phase 4 — DialogProcessor lifecycle hooks (`:144-245`):** the heart of the boot. Six `Func<...>` properties on the DialogProcessor get assigned inline async lambdas:

- `OnRequestRecievedAsync` (`:146-194`) — fires when the user's input is accepted. Mutes the mic per the selected `MicrophoneMuteStrategy` (`Mute` / `StopDevice` / `StopListener` / `Threshold` / `None`), starts a "processing" presentation (random animation+face from a configured pool), shows the user message window, and finally resets the face to neutral.
- `OnEndAsync` (`:197-230`) — fires when the dialog turn ends. Reverses the mic mute, transitions the avatar mode to `Idle`, and restarts idle animations.
- `OnStopAsync` (`:232-242`) — fires on barge-in or explicit stop. Halts current speech, restarts idling unless a successive dialog is queued.
- `OnErrorAsync` (`:245`) — bound to the in-class `OnErrorAsyncDefault` method (`:572-590`) which plays the configured error voice/face/animation.

Phase 4 is the most load-bearing section of the whole bootstrap. Everything `AIAvatar` *does* during a conversation is configured here. Read again: it isn't *behavior*; it's *binding*. The behavior lives in `DialogProcessor`. `AIAvatar` just tells it what to do at each hook.

**Phase 5 — LLMContentProcessor callbacks (`:247-291`):** three more callbacks on the content-streaming pipeline. `HandleSplittedText` parses each split chunk into an `AnimatedVoiceRequest` via `ModelController.ToAnimatedVoiceRequest()` (`ModelController.cs:237-292`) — this is the `[anim:Name]` / `[face:Expression]` tag extraction that runs against streamed LLM tokens. `ProcessContentItemAsync` walks the voices and prefetches each from TTS. `ShowContentItemAsync` is what actually drives the avatar to speak and move. The streaming pipeline is set up here, but doesn't fire until a dialog session is open.

**Phase 6 — Speech I/O auto-selection (`:293-328`):** here is where CDK gets clever about plug-and-play. It walks every `ISpeechListener` component on the GameObject and picks the first one whose `IsEnabled` is true:

```csharp
// /tmp/ChatdollKit/Scripts/AIAvatar.cs:294-309
foreach (var speechListener in gameObject.GetComponents<ISpeechListener>())
{
    if (speechListener.IsEnabled)
    {
        Debug.Log($"SpeechListener: {speechListener.GetType().Name}");
        SpeechListener = speechListener;
        SpeechListener.OnRecognized = OnSpeechListenerRecognized;
        SpeechListener.OnBargeIn = OnBargeIn;
        SpeechListener.ChangeSessionConfig(
            silenceDurationThreshold: idleSilenceDurationThreshold,
            minRecordingDuration: idleMinRecordingDuration,
            maxRecordingDuration: idleMaxRecordingDuration
        );
        break;
    }
}
```

Then the same pattern for `ISpeechSynthesizer` (`:316-324`). The provider isn't named; the *role* is the name, and any `MonoBehaviour` implementing the right interface can fill the role. Drop a `VoicevoxSpeechSynthesizer` and a `GoogleSpeechSynthesizer` onto the same GameObject, enable one, disable the other — done. No factory, no config file, no DI binding. The Inspector toggle *is* the config.

This is one of those moments where Unity-native local feels genuinely different from the SAP and Waifu patterns. SAP has to register Python modules at runtime via an entry-point system; Waifu has to mount a different `<LiveKitAvatarSession>` component for each mode. CDK lets you ship a single scene with five TTS providers preconfigured and a checkbox per provider in the Inspector. The user picks at edit time. The runtime sees one.

## Start: One Mixer Line

`Start()` is three lines (`AIAvatar.cs:337-343`). It pushes `maxCharacterVolumeDb` into the AudioMixer, but only if `characterAudioMixer` was successfully grabbed from `ModelController.SpeechController.AudioSource.outputAudioMixerGroup` at the tail of Awake (`:331-334`). The reason `Start` and not `Awake` is the unity-canonical answer: `outputAudioMixerGroup` may not be fully resolved during Awake on all build targets. Defensive.

The mix matters because muting (`MuteCharacter` at `:426-431`) is implemented as **a -80dB mixer move**, not an AudioSource toggle. The avatar keeps generating audio while muted; only the mixer drops it to silence. That is the only way to keep TTS prefetch and lip-sync timing in sync with what the user *would have heard* if not muted. This is a real production detail that Waifu's cloud avatar hides entirely — silenced audio on the SDK side is invisible to you.

## Update: 47 Lines, One State Machine, One Mode Timer

`Update()` is two responsibilities: drive `UpdateMode()` (lines `:393-424`), and reconcile message window + speech-listener config across mode and dialog-status transitions.

`UpdateMode()` is the avatar's outer state machine — `Disabled / Sleep / Idle / Conversation` — but it is *not* the dialog state machine. The dialog state machine lives in `DialogProcessor.DialogStatus` (`DialogProcessor.cs:13-22`) and has seven states: `Idling / Initializing / Routing / Processing / Responding / Finalizing / Error`. AIAvatar's outer mode and DialogProcessor's inner status are coupled by one rule (`AIAvatar.cs:395-401`):

```csharp
if (DialogProcessor.Status != DialogProcessor.DialogStatus.Idling
    && DialogProcessor.Status != DialogProcessor.DialogStatus.Error)
{
    Mode = AvatarMode.Conversation;
    modeTimer = conversationTimeout;
    return;
}
```

While the dialog is mid-turn, the avatar is in Conversation mode. Otherwise the `modeTimer` (started at `:24` with the `idleTimeout` default of 60s) counts down each frame, and at zero Conversation degrades to Idle, then Idle degrades to Sleep. Sleep is terminal until external wake. This is detailed in [[31_AIAVATAR_MAIN_LOOP]].

The other half of Update (`:368-387`) is a *change-detector*: if the avatar mode just transitioned, update the SpeechListener's session config to use Conversation or Idle parameters (different silence thresholds, recording durations, etc). This is how the avatar can listen tightly for 0.3s of silence during a turn but loosely for 0.3s of silence when waiting for a wake word. The transition fires once per change — `previousMode` and `previousDialogStatus` are saved at the end of every Update.

## The Five Microphone-Mute Strategies

Tucked inside Phase 4 above is one of the most quietly important design surfaces in CDK: the `MicrophoneMuteStrategy` enum (`AIAvatar.cs:54-61`):

```csharp
public enum MicrophoneMuteStrategy
{
    None,
    Threshold,
    Mute,
    StopDevice,
    StopListener
}
```

Five different ways to keep the avatar from hearing itself while it speaks:

- **None** — listen to your own voice. Will cause feedback loops. Only useful in a fully-isolated audio setup or for testing.
- **Threshold** — raise the noise gate from `-50dB` to `-15dB` while speaking. Cheap, no state change, but porous to loud TTS.
- **Mute** — set a soft mute flag on the MicrophoneManager (`MicrophoneManager.cs:164-168`). The mic still spins, samples still come in, but `GetAmplitudeData` returns an empty array (`:246-249`). Default and recommended.
- **StopDevice** — actually call `Microphone.End()` (`MicrophoneManager.cs:155-161`). Heaviest. On some platforms this incurs a 100-300ms restart cost.
- **StopListener** — leave the mic running but pause the SpeechListener's recording session.

The user picks one per deployment via the Inspector. SAP's affection loop has nothing this surgical. Waifu's cloud SDK has these knobs but you can't see them. CDK exposes them on a designer-facing Inspector toggle. This is the right level of transparency for a Unity-native local stack.

## Where It Breaks

- **The single-GameObject assumption.** Every `GetComponent<T>()` in Awake is sibling-only. If a user splits responsibilities across two GameObjects — say, ModelController on the avatar mesh, AIAvatar on a controller object — the auto-wire silently returns null and components stay disconnected. The Inspector override fields exist for exactly this case but the docs don't shout about it.
- **One subscriber per callback.** `OnSayStart`, `OnEndAsync`, `OnRequestRecievedAsync` are all single-cast `Func<...>`s, not events. Anyone else who wants to hook the same lifecycle event must wrap the existing delegate. Forge-B's sister-project docs note that ChatMemory integration has to monkey-patch around this.
- **Unity component-order dependencies are silent.** `Awake()` runs in Unity's "undefined but stable" order; `Start()` runs after all Awakes. If `MicrophoneManager.Start` runs before `AIAvatar.Awake` (likely — Awake-Start-Awake-Start would violate Unity's lifecycle), the mic is already capturing when Awake configures the threshold. The current code handles this by `SetNoiseGateThresholdDb` being safe to call mid-capture, but the order isn't documented anywhere.
- **`Audio mixer group` is required for mute.** If `outputAudioMixerGroup` is null on the AudioSource (forgot to assign in Inspector), `MuteCharacter()` is a silent no-op (`:428`). The avatar will speak full-volume regardless of `IsCharacterMuted = true`.
- **No initialization-failure surface.** If `SpeechListener` is null at the end of Phase 6, the code logs `"Enabled SpeechListener not found."` (`:312`) and continues. The avatar boots into a state where it can speak but can't hear. There is no `OnInitializationFailed` callback to hook.

## Where It Surprises

- **No async in Awake.** Unity disallows it. The boot is entirely synchronous up to the first frame. `DialogProcessor.SelectLLMService` (`DialogProcessor.cs:81-113`) does no network call to verify the LLM API key — that doesn't happen until the first `GenerateContentAsync` call. CDK starts up in tens of milliseconds even with six LLM providers in the scene, because none of them touch the network at boot. Compare to SAP, which takes 8-15 seconds to load `sherpa-onnx`.
- **The `OnUpdate` is 47 lines including all change-detection.** Per-frame cost is dominated by `DialogProcessor.Status` getter + one to four bool comparisons. Sub-microsecond. The dialog state machine is *not* polled in Update — it runs as an async UniTask inside `DialogProcessor.StartDialogAsync`.
- **The `ProcessingPresentation` randomization (`:166-173`).** While the LLM is generating, the avatar plays a random "thinking" animation pulled from `ProcessingPresentations`. That list is empty by default. If you populate it, you get a UX win for free. SAP has nothing like this; Waifu's cloud avatar might internally, but it's invisible.

## Cross-References

- [[31_AIAVATAR_MAIN_LOOP]] — the per-frame update + dialog state-machine in detail
- [[11_AIAVATAR_DOMAIN]] — top-level `AIAvatar.cs` controller domain analysis
- [[1C_UNITY_LIFECYCLE_DOMAIN]] — Awake/Start/Update timing semantics
- [[sap:30_ELECTRON_BOOTSTRAP]] — contrast: two-process stdout-handshake bootstrap
- [[waifu:30_BASIC_MODE_FLOW]] — contrast: thirty-one-line cloud SDK mount

## What This Means for Ember

**Adopt:**

- **Sibling-component auto-resolution pattern.** The `GetComponent<T>() ?? gameObject.GetComponent<T>()` idiom (`AIAvatar.cs:115-119`, Apache-2.0 attribution required) is the right pattern for the Unity tier of Ember's Andlit-unity proposal. When designers compose an avatar in the editor, code should find what's there, not require explicit wiring. Bind to Andlit-unity as the canonical container pattern.
- **Five-strategy mic-mute enum (`AIAvatar.cs:54-61`).** Different deployments demand different mic-mute strategies. Vendor this enum verbatim into Funi's audio I/O layer with full Apache-2.0 attribution. SAP and Waifu have nothing equivalent at this resolution.
- **The `MicrophoneMuteStrategy.Mute` default.** Setting a soft flag while leaving the mic device running avoids platform-specific restart cost. This is the right default for Ember.

**Adapt:**

- **The single-cast `Func<...>` callbacks.** They're elegantly simple in CDK because Unity scenes are single-owner — one AIAvatar per scene. Ember's Funi must support multiple subscribers per lifecycle event (Hjarta wants to log every dialog turn; Munnr wants to mirror them to its CLI surface). Convert the `Func<...>` pattern to a typed event bus while keeping the inline-lambda registration syntax.
- **The provider auto-selection by `IsEnabled`** (`AIAvatar.cs:294-324`). The pattern is great. The "pick the first enabled, ignore the rest" rule is too soft — silent fallthrough is hard to debug. Ember's equivalent should *fail loud* if multiple providers are marked enabled, or require a typed `IsPrimary` flag.
- **The bool-toggle Inspector configuration.** Designer-friendly. Ember's equivalent (when there is a GUI) should expose per-subsystem enable toggles via a single config file. Munnr should render this surface as text when no GUI is present.

**Avoid:**

- **The 220-line Awake.** It's load-bearing and it's a wall of lambdas. Six separate `Setup<X>()` private methods would read better and unit-test better. Forge-A's recommendation: when porting any of this into Ember, factor by phase.
- **Silent boot success on missing critical components.** AIAvatar logs a warning and continues if no SpeechListener was found (`AIAvatar.cs:310-313`). For Ember, boot must fail loudly when a True Name is unreachable. Brunnr-down should produce a stack-trace-grade error, not a Debug.LogWarning.

**Invent:**

- **Funi Awake Manifest.** Borrowing the SAP Smiðja Worker Manifest idea, propose that every Ember bootable subsystem ship a declarative `funi/<subsystem>.yaml` describing: required peer-subsystems, lifecycle hooks, init order constraints, and a `fail_loud` flag. Funi reads the manifest at startup, resolves the dependency graph, fails early on missing requireds, and only then runs each subsystem's `awake()`. The CDK pattern works because Unity gives you the manifest implicitly via scene graph. Ember has no scene graph — so make the manifest explicit.
- **Hjarta Lifecycle Bus.** Replace single-cast `Func<...>` with a typed pub/sub bus *but keep the inline-lambda registration ergonomics*. The Six True Names each subscribe to events they care about; Funi never enumerates subscribers; ordering is enforced by `priority` per subscription, not by Awake() order.

---

*Apache-2.0 attribution: when adopting any of the above CDK code into Ember source, preserve the ChatdollKit header reference per Apache-2.0 §4(c). One NOTICE entry per subsystem suffices.*

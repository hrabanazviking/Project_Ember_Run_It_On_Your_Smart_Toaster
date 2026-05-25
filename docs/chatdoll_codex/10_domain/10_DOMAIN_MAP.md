---
codex_id: 10_DOMAIN_MAP
title: The Domain Map of ChatdollKit — Eight Subsystems, One Avatar, No Server
role: Architect
layer: Domain
status: draft
chatdoll_source_refs:
  - Scripts/AIAvatar.cs:1-664
  - Scripts/Dialog/DialogProcessor.cs:1-346
  - Scripts/Dialog/DialogPriorityManager.cs:1-86
  - Scripts/Model/ModelController.cs:1-464
  - Scripts/Model/ModelRequestBroker.cs:1-193
  - Scripts/Model/SpeechController.cs:1-212
  - Scripts/Model/FaceController.cs:1-73
  - Scripts/LLM/ILLMService.cs:1-58
  - Scripts/LLM/LLMServiceBase.cs:1-175
  - Scripts/LLM/LLMContentProcessor.cs:1-271
  - Scripts/SpeechListener/MicrophoneManager.cs:1-344
  - Scripts/SpeechListener/SpeechListenerBase.cs:1-255
  - Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs:1-154
  - Scripts/Network/SocketServer.cs:1-203
  - Scripts/IO/JavaScriptMessageHandler.cs:1-54
  - Scripts/IO/ExternalInboundMessage.cs:1-13
  - Scripts/ChatdollKit.asmdef
  - Extension/SileroVAD/SileroVADProcessor.cs:1-203
  - Extension/ChatMemory/ChatMemoryIntegrator.cs:1-108
  - Extension/VRM/VRMLoader.cs:1-121
ember_subsystem_targets: [Funi, Strengr, Brunnr, Smiðja, Hjarta, Munnr]
cross_refs:
  - 10_domain/11_AIAVATAR_DOMAIN
  - 10_domain/12_MODEL_CONTROLLER_DOMAIN
  - 10_domain/13_DIALOG_PROCESSOR_DOMAIN
  - 10_domain/14_SPEECH_LISTENER_DOMAIN
  - 10_domain/15_SPEECH_SYNTHESIZER_DOMAIN
  - 10_domain/16_LLM_SERVICE_DOMAIN
  - 10_domain/17_MICROPHONE_MANAGER_DOMAIN
  - 10_domain/18_NETWORK_DOMAIN
  - 10_domain/19_TOOL_DOMAIN
  - 10_domain/1A_MEMORY_DOMAIN
  - 10_domain/1B_ANIMATION_DOMAIN
  - 10_domain/1C_UNITY_LIFECYCLE_DOMAIN
  - 10_domain/1D_MULTI_PLATFORM_DOMAIN
  - sap:10_DOMAIN_MAP
  - waifu:10_DOMAIN_MAP
---

# The Domain Map of ChatdollKit
## Eight Subsystems, One Avatar, No Server

*— Rúnhild Svartdóttir, Architect*

> *A clean architecture is not one whose diagrams look pretty. It is one whose seams hold under load and whose lines tell the truth about who is responsible for what. ChatdollKit's seams hold. The lie it tells is a different lie — and a smaller one — than the one SAP told.*

ChatdollKit (CDK) is the third position on the embodiment axis after Super Agent Party (SAP) and the waifu-chat-starter-kit (Waifu). It is **18,221 lines of C# across 121 files**, organised into **eight peer subsystems plus one top-level coordinator**, all of it riding the Unity engine. It is the *first* of our three corpora that uses the engine itself as the runtime substrate — and in doing so it asks Ember a question SAP and Waifu both ducked: *what does it cost to commit to a game engine as your embodiment platform?*

This document maps what CDK *owns*, what it *defers to Unity*, what it *delegates to third-party SDKs*, and where the seams between those three are. The deep anatomies live in the thirteen sibling domain docs ([[11_AIAVATAR_DOMAIN]] through [[1D_MULTI_PLATFORM_DOMAIN]]) and the five Architect-owned interface docs ([[20_LLM_SERVICE_INTERFACE]], [[24_VAD_INTERFACE]], [[25_ANIMATION_TAG_PROTOCOL]], [[26_TOOL_FUNCTION_CALL_INTERFACE]], [[29_VRM_INTERFACE]]). Here I show you the whole shape.

---

## 1. The Eight Subsystems (And the One Above Them)

A *subsystem* in CDK is a folder under `Scripts/`, each owning one concept. The folder layout maps directly to a `namespace ChatdollKit.<Folder>`; the layout is the architecture, not a suggestion. Compare SAP, whose 14 implied domains were violated wholesale by `server.py` ([[sap:10_DOMAIN_MAP]] §1) — CDK's domains are **honored at file granularity**, every single one.

| # | Subsystem | Where it lives | What it owns | What it does NOT own |
|---|---|---|---|---|
| 0 | **AIAvatar (top-level)** | `Scripts/AIAvatar.cs` (664 LOC) | Avatar mode state machine (`Sleep/Idle/Conversation`), wake-word / cancel-word / interrupt-word extraction, microphone-mute strategy selection, error-voice presentation, the *gluing* of all eight subsystems | Reasoning (delegated to LLM), audio capture (delegated to MicrophoneManager), animation execution (delegated to ModelController) |
| 1 | **Dialog** | `Scripts/Dialog/` — `DialogProcessor` (346), `DialogPriorityManager` (86), `MessageWindow/` (3 files) | Dialog state machine (`Idling/Initializing/Routing/Processing/Responding/Finalizing/Error`), tool resolution, prompt assembly delegation, side-effect callback registration (`OnStartAsync`, `OnEndAsync`, `OnStopAsync`, `OnErrorAsync`), request-merge window, timestamp injection, priority queue for queued utterances | LLM provider selection beyond enabled-flag picking (that's the LLM subsystem), animation playback (that's ModelController) |
| 2 | **Model** | `Scripts/Model/` — `ModelController` (464), `ModelRequestBroker` (193), `SpeechController` (212), `FaceController` (73), `Animation`/`Voice`/`FaceExpression`/`AnimatedVoice`/`AnimatedVoiceRequest` value types, `Blink` (198), `uLipSyncHelper` (107) + variants, `IBlink`/`ILipSyncHelper`/`IFaceExpressionProxy` interfaces, `ActionHistoryRecorder` | Avatar animation queue + idle loop, face expression queue + smoothing, voice playback + prefetch + PCM-frame sampling for external lip-sync, `[anim:]`/`[face:]`/`[pause:]`/`[lang:]` tag parsing | The VRM avatar itself (that's `Extension/VRM/`), the TTS engine (that's the SpeechSynthesizer), the LLM (that's the LLM subsystem) |
| 3 | **LLM** | `Scripts/LLM/` — `ILLMService` (58) + `LLMServiceBase` (175) + `LLMContentProcessor` (271) + `ITool`/`ToolBase` (26+46) + 5 provider subdirs (`ChatGPT/` 661, `Claude/` 565, `Gemini/` 616, `Dify/` 405, `AIAvatarKit/` 448) each with a regular + a WebGL variant | A typed `ILLMService` contract, streaming response handling, per-provider request/response shape adapters, function-calling abstraction (`ITool`), tag extraction via regex, content-stream split-and-pipe to ModelController | Speech (that's SpeechController), animation (that's ModelController), tools' actual *implementations* (those live in user code as `ToolBase` subclasses) |
| 4 | **SpeechListener** | `Scripts/SpeechListener/` — `ISpeechListener` + `SpeechListenerBase` (255), `MicrophoneManager` (344), `IMicrophoneManager`/`IMicrophoneProvider`, `RecordingSession` (153), six providers (Google/Azure/OpenAI/AzureStream/AIAvatarKit/AIAvatarKitStream), three platform mic providers (`Android`/`iOS`/`Mac`MicrophoneProvider), dummy/null providers | STT pipeline: mic samples → noise gate → recording session → silence-trigger → STT provider call → text emission, barge-in detection (`SpeechListenerBase.Update` lines 66-84), `RecordingSession` with preroll-buffer for voice-start grace | Voice activity detection beyond a linear-threshold default (extension: `Extension/SileroVAD/`), conversation lifecycle (that's AIAvatar), the LLM call (that's Dialog → LLM) |
| 5 | **SpeechSynthesizer** | `Scripts/SpeechSynthesizer/` — `ISpeechSynthesizer` + `SpeechSynthesizerBase` (154), eleven providers: Google/Azure/OpenAI/**VOICEVOX/AivisCloud/StyleBertVits2/Voiceroid/NijiVoice/SpeechGateway/Kotodama/AIAvatarKit** | TTS pipeline: text + parameters → cache lookup → concurrent-download dedupe → `AudioClip` return, in-memory cache keyed by `(text, params).GetHashCode()`, optional text preprocessing hook | Audio playback (that's SpeechController), lip-sync visuals (that's `uLipSyncHelper`), prefetch queue (that's SpeechController + ModelRequestBroker) |
| 6 | **IO** | `Scripts/IO/` — `JavaScriptMessageHandler` (54), `ExternalInboundMessage` (13), `IExternalInboundMessageHandler`, `PriorityQueue<T>` (111), `AudioConverter` (117), `SimpleCamera` (653), platform mic natives (`AndroidNativeMicrophone`, `IOSNativeMicrophone`, `MacNativeMicrophone`) | The *external* surface: WebGL→Unity JSON bridge (`JavaScriptMessageHandler.HandleMessageFromJavaScript` at `IO/JavaScriptMessageHandler.cs:35`), typed `ExternalInboundMessage` envelope, generic priority queue, camera capture for vision-LLMs | The *transport* (TCP socket lives in `Network/`), the *handling* of the message (that's Dialog) |
| 7 | **Network** | `Scripts/Network/` — `SocketServer` (203), `SocketClient`, `ChatdollHttp` (288), `WebSocketClient` (209) | A `TcpListener` on a configurable port (`Network/SocketServer.cs:88`) reading newline-delimited JSON into `ExternalInboundMessage`s for `IExternalInboundMessageHandler.OnDataReceived`, a thread-safe queue handed to Unity's main thread via `Update()` polling (lines 42-53), an `HttpClient` wrapper for outbound REST, a `WebSocketClient` for streaming protocols | Authentication (there isn't any — see §5.4), the message *meaning* (that's IO + Dialog), TLS (it's TCP only) |
| 8 | **UI** | `Scripts/UI/` — `MessageInput`, `MicrophoneButton`, `SpeakerButton`, `MicrophoneController`, `SocketServerController`, `UIControlContainer`, `MessageWindowContainer`, `CameraButton`, `ImageButton`, `RequestInput`, `FPSManager` | Unity-side UI widgets (UGUI/uGUI components), button-to-method wiring, mic-toggle/speaker-toggle UI plumbing, message-text input | Anything else; UI knows nothing about reasoning, audio, or models beyond the events it dispatches |

Plus three named **Extensions** under `Extension/`:

| Extension | Where | Owns |
|---|---|---|
| **SileroVAD** | `Extension/SileroVAD/SileroVADProcessor.cs` (203) + `CopyThisJSToStreamingAssetsForWebGL/silero-vad.js` | ONNX Silero-VAD model loaded via `Microsoft.ML.OnnxRuntime`, 512-sample-chunk inference at 16kHz, probability + threshold-driven `IsVoiced` plug-in for `SpeechListenerBase.DetectVoiceFunctions` |
| **ChatMemory** | `Extension/ChatMemory/ChatMemoryIntegrator.cs` (108) + `ChatMemoryTool.cs` (37) | HTTP client to the external `uezo/chatmemory` FastAPI service: `AddHistory` posts user+assistant exchanges, `SearchMemory` returns episodic-store hits; the `ChatMemoryTool` is a function-calling adapter so the LLM can request memory itself |
| **VRM** | `Extension/VRM/VRMLoader.cs` (121) + `VRMBlink.cs` (119) + `VRMFaceExpressionProxy.cs` (94) + `VRMuLipSyncHelper.cs` (27) + `AIAvatarVRM.prefab` | UniVRM runtime load (`VRMLoader.LoadCharacterAsync` lines 67-119), VRM-specific blink (`BlendShapeKey.CreateFromPreset(BlendShapePreset.Blink)`), VRM-specific face expression proxy with smooth-damp transitions, VRM-specific viseme blend-shape map |

**Nine cells in the table; nine folders on disk.** This is a 1:1 between the domain map and the file system that SAP never achieved (`server.py` ate four of its fourteen domains; [[sap:10_DOMAIN_MAP]] §1). It is the *first* architectural lesson of CDK and it travels for free if Ember adopts the discipline.

---

## 2. The Layered View — Six Bands, No Server

CDK has no Python server. It has no Electron shell. It has no cloud SDK at the centre. What it has is the **Unity runtime as the implicit substrate**, and a small typed surface on top. The stack:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  USER SURFACE                                                           │
│  ┌──────────────────┐ ┌──────────────────┐ ┌─────────────────────────┐  │
│  │ UI/ widgets      │ │ MessageWindow    │ │ External (SocketServer/ │  │
│  │ (UGUI components)│ │ (Dialog/MW/*)    │ │  JavaScriptMessageHand) │  │
│  └────────┬─────────┘ └────────┬─────────┘ └──────────┬──────────────┘  │
└───────────┼────────────────────┼──────────────────────┼─────────────────┘
            │                    │                      │
┌───────────┴────────────────────┴──────────────────────┴─────────────────┐
│  COORDINATION LAYER — AIAvatar.cs (664 LOC)                             │
│    AvatarMode {Disabled, Sleep, Idle, Conversation}                     │
│    Wake/Cancel/Interrupt word extraction (lines 444-521)                │
│    MicrophoneMuteStrategy {None, Threshold, Mute, StopDevice, …}        │
│    SpeechListener selection (lines 294-313)                             │
│    SpeechSynthesizer selection (lines 316-328)                          │
│    DialogProcessor lifecycle callbacks (lines 145-243)                  │
└───────────┬─────────────────────────────────────────────────────────────┘
            │
┌───────────┴─────────────────────────────────────────────────────────────┐
│  DIALOG LAYER — DialogProcessor.cs (346 LOC)                            │
│    DialogStatus state machine                                           │
│    LLMService selection (auto-detect IsEnabled, lines 81-113)           │
│    LoadLLMTools — registers ITool components on the GameObject          │
│    StartDialogAsync — six-phase pipeline (lines 131-280)                │
│    DialogPriorityManager — separate component, priority queue           │
└───────┬──────────────────────────┬──────────────────────────────────────┘
        │                          │
┌───────┴────────────────┐  ┌──────┴────────────────────────────────────┐
│  COGNITION LAYER       │  │  CAPABILITY LAYER                         │
│  ILLMService           │  │  ITool / ToolBase                         │
│  LLMServiceBase        │  │   (user-supplied per-feature subclasses)  │
│  LLMContentProcessor   │  │  Extension/ChatMemory/ChatMemoryTool      │
│   (split-and-pipe)     │  │                                           │
│  Per-provider:         │  │  Vision: SimpleCamera + image bytes       │
│   ChatGPT / Claude /   │  │   threaded through payloads (AIAvatar.cs  │
│   Gemini / Dify /      │  │   `GetPayloads`, lines 109, 122-128 of    │
│   AIAvatarKit          │  │   per-provider MakePromptAsync)           │
└───────┬────────────────┘  └───────────────────────────────────────────┘
        │
┌───────┴─────────────────────────────────────────────────────────────────┐
│  EMBODIMENT LAYER                                                       │
│    ModelController — animation queue + idle loop                        │
│    FaceController — face expression queue                               │
│    SpeechController — voice prefetch + playback + PCM sampling          │
│    ModelRequestBroker — text→AnimatedVoiceRequest split + queue         │
│    Blink / VRMBlink — random-interval eye closure                       │
│    IFaceExpressionProxy (VRC / VRM impls)                               │
│    ILipSyncHelper (uLipSync / VRM variants)                             │
└───────┬─────────────────────────────────────────────────────────────────┘
        │
┌───────┴─────────────────────────────────────────────────────────────────┐
│  AUDIO LAYER                                                            │
│    MicrophoneManager (UnityMicrophoneProvider / WebGL DllImport)        │
│    RecordingSession (preroll + silence-trigger)                         │
│    SpeechListenerBase (barge-in detection, sample-rate resampling)      │
│    SpeechSynthesizerBase (cache + dedupe download tasks)                │
│    Extension/SileroVAD/SileroVADProcessor (ONNX inference)              │
└───────┬─────────────────────────────────────────────────────────────────┘
        │
┌───────┴─────────────────────────────────────────────────────────────────┐
│  TRANSPORT LAYER                                                        │
│    Network/SocketServer (TcpListener)                                   │
│    Network/ChatdollHttp (HttpClient wrapper)                            │
│    Network/WebSocketClient                                              │
│    IO/JavaScriptMessageHandler ([DllImport] InitJSMessageHandler)       │
└───────┬─────────────────────────────────────────────────────────────────┘
        │
┌───────┴─────────────────────────────────────────────────────────────────┐
│  UNITY RUNTIME                                                          │
│    MonoBehaviour lifecycle — Awake / Start / Update / LateUpdate /      │
│      OnDestroy — invoked by Unity per-frame                             │
│    Cysharp.Threading.UniTask (async-over-MonoBehaviour)                 │
│    AudioSource, Animator, SkinnedMeshRenderer, Microphone               │
│    Build target — Win/Mac/Linux/iOS/Android/VR/AR/WebGL                 │
└─────────────────────────────────────────────────────────────────────────┘
```

Notice the inversion: SAP's `server.py` was the gravity well at the centre ([[sap:10_DOMAIN_MAP]] §2). Waifu's gravity well was somewhere else's cloud ([[waifu:10_DOMAIN_MAP]] §2). **CDK has no gravity well at all.** What it has is a *coordinator* — `AIAvatar.cs`, 664 lines — and that coordinator delegates downward through typed contracts. The shape is closer to a healthy onion than to a planet.

The honesty cost: the substrate is the entire Unity engine. CDK is not 18,221 lines; it is 18,221 *plus the millions of lines of C++/C# under it*. That is the deal — and we will name the deal in §6.

---

## 3. The Dependency Graph — Honest Edition

CDK's intra-namespace dependencies are clean enough to render exhaustively. The notation `A ──► B` means "A depends on B" (A imports B's namespace and calls into it). External Unity APIs are denoted `[Unity:...]`; UniTask is `[UniTask]`.

```
                              [Unity: MonoBehaviour, Update, AudioSource, Animator]
                              [UniTask: async/await for Unity coroutines]
                                              │
                                              ▼
                          ┌───────────────────────────────────────────┐
                          │                AIAvatar.cs                │
                          │  (coordinator; pulls components via       │
                          │   gameObject.GetComponent<IFoo>)          │
                          └─────┬─────┬─────┬─────┬─────┬─────┬───────┘
                                │     │     │     │     │     │
            ┌───────────────────┘     │     │     │     │     └───────────────────┐
            ▼                         ▼     ▼     ▼     ▼                         ▼
  ┌─────────────────┐    ┌──────────────────┐  ┌──────────────────┐    ┌──────────────────┐
  │  Dialog/        │    │  Model/          │  │  SpeechListener/ │    │  SpeechSynth./   │
  │  DialogProc     │◄───┤  ModelController │  │  SpeechListener  │    │  SpeechSynth.    │
  │  PriorityMgr    │    │  ModelReqBroker  │  │  MicMgr          │    │  Base + 11 impls │
  └──────┬──────────┘    │  SpeechCtrl      │  └─────┬────────────┘    └──────────────────┘
         │               │  FaceCtrl        │        │
         │               │  Blink           │        │
         │               └─┬─────────┬──────┘        │
         │                 │         │               │
         ▼                 │         ▼               ▼
  ┌─────────────────┐      │   ┌──────────────┐  ┌────────────────────┐
  │  LLM/           │      │   │  IBlink      │  │  RecordingSession  │
  │  ILLMService    │      │   │  ILipSync    │  │  (no parent dep)   │
  │  LLMServiceBase │      │   │  IFaceExpr   │  └────────────────────┘
  │  + 5 providers  │      │   │  (interfaces │
  │  ITool/ToolBase │      │   │   only)      │
  │  LLMContentProc │      │   └─┬────────┬───┘
  └──────────┬──────┘      │     │        │
             │             │     ▼        ▼
             ▼             │  Extension/VRM/  (UniVRM-bound impls of
       ┌──────────────┐    │  the three interfaces above)
       │  Network/    │    │
       │  ChatdollHttp│    │
       │  SocketSrv   │◄───┘                    Extension/SileroVAD/
       │  WebSockClnt │              SileroVADProcessor
       └──────┬───────┘                        │
              │                                ▼
              ▼              (Microsoft.ML.OnnxRuntime —
       ┌──────────────┐       not bundled; Unity NuGet
       │  IO/         │       package or .dll)
       │  PriorityQ   │
       │  AudioConv   │
       │  JSMsgHandler│
       │  ExtInbound  │
       └──────────────┘
```

The graph has **no cycles**. Compare SAP's `IM bots → HTTP-loopback → server.py` self-loop ([[sap:10_DOMAIN_MAP]] §3) — CDK does not call into itself over HTTP because *it does not need to*. Cross-component invocation is in-process via interface contracts. Cross-process invocation is *inbound only* (SocketServer + JavaScriptMessageHandler accept external commands; CDK never *sends* itself a message).

The dependency edges that matter for Ember:

1. **AIAvatar → IFoo via `GetComponent<>`.** AIAvatar.cs lines 116-119 reach into the GameObject for `MicrophoneManager`, `ModelController`, `DialogProcessor`, `LLMContentProcessor`. The coupling is *by interface name*, resolved at runtime by the Unity component system. This is dependency injection without a DI framework; the substrate provides it.
2. **DialogProcessor → ILLMService via `GetComponents<>` filter.** `DialogProcessor.SelectLLMService` (lines 81-113) iterates *every* `ILLMService` on the GameObject and picks the one with `IsEnabled == true`. To swap providers, toggle a bool — no rewiring. This is the single cleanest LLM-multiplexing pattern of the three corpora.
3. **LLMServiceBase → regex tag extraction (line 100-117).** Tags like `[face:Joy]` are extracted in the *base class*, not in each provider. Every provider gets tag support free.
4. **Extension/VRM → `Scripts/Model` interfaces.** The VRM extension implements `IBlink`, `IFaceExpressionProxy`, `ILipSyncHelper` — Unity's component model resolves the bound at activation. To swap VRM for Live2D, swap the implementations.

The graph is *boring*, in the highest sense. Every edge points one way; every edge is named; every edge can be traced in fewer than three jumps. SAP and Waifu both have *interesting* dependency graphs — and "interesting" in architecture is usually a vice.

---

## 4. The Lifecycle — How One Turn Travels

Trace one user utterance from microphone to mouth, citing files:

1. **Mic samples arrive.** `MicrophoneManager.Update` (`SpeechListener/MicrophoneManager.cs:81-103`) reads the position delta from Unity's `Microphone` API (or WebGL native), invokes `OnSamplesReceived`, and dispatches to active `RecordingSession`s.
2. **RecordingSession.ProcessSamples** (`SpeechListener/RecordingSession.cs:40-96`) runs the `DetectVoiceFunctions` list (default: linear-threshold; optional: SileroVAD plug-in). If voice detected and not recording, starts recording with a preroll buffer (silence captured before voice-start). If silent for `SilenceDurationThreshold` after recording started, stops and fires `OnRecordingComplete`.
3. **SpeechListenerBase.HandleRecordingCompleteAsync** (`SpeechListener/SpeechListenerBase.cs:165-203`) resamples if `TargetSampleRate` differs, calls the provider-specific `ProcessTranscriptionAsync` (Google / Azure / OpenAI / etc.), and invokes `OnRecognized(text)`.
4. **AIAvatar.OnSpeechListenerRecognized** (`AIAvatar.cs:592-630`) decides what to do with the text:
   - If it matches a `CancelWord`, calls `StopChatAsync`.
   - If it matches an `InterruptWord`, calls `StopChatAsync(continueDialog: true)`.
   - If `Mode >= Conversation`, dispatches as a direct chat request.
   - Otherwise, tries `ExtractWakeWord` and only dispatches if a wake word (or `WakeLength`) matches.
5. **DialogProcessor.StartDialogAsync** (`Dialog/DialogProcessor.cs:131-280`) runs the six-phase pipeline:
   - **Initializing**: cancels any running dialog, assigns a fresh `processingId` (Guid), opens a `CancellationTokenSource`.
   - **Processing**: fires `OnRequestRecievedAsync` (registered by AIAvatar to handle mic-mute strategy, processing-presentation animation, user message-window display).
   - Sets `llmService.Tools = toolSpecs` (from `LoadLLMTools` at line 115-128).
   - Merges consecutive requests if within `mergeRequestThreshold` seconds (lines 175-190).
   - Injects timestamp if past `timestampInsertionInterval` (lines 193-202).
   - Calls `llmService.MakePromptAsync` → `llmService.GenerateContentAsync` → starts the streaming task.
   - **Responding**: `LLMContentProcessor.ProcessContentStreamAsync` consumes the streaming buffer in parallel; `ShowContentAsync` dequeues parsed items and dispatches to `ModelController.AnimatedSay`.
6. **LLMContentProcessor** (`LLM/LLMContentProcessor.cs:29-161`) splits the stream by punctuation (`SplitChars = ["。", "！", "？", ". ", "!", "?"]` line 14) and processes each chunk: strips `<thinking>...</thinking>` blocks, extracts `[lang:...]`, calls `HandleSplittedText` (AIAvatar registers a handler that converts to `AnimatedVoiceRequest`), and queues for downstream.
7. **ModelController.AnimatedSay** (`Model/ModelController.cs:184-235`) iterates the request's `AnimatedVoice` frames, calling `Animate(animations)`, `FaceController.SetFace(faces)`, and `SpeechController.Say(voices)` per frame.
8. **SpeechController.Say** (`Model/SpeechController.cs:38-169`) per voice: calls `SpeechSynthesizerFunc(text, params, token)` (which is the active TTS provider's `GetAudioClipAsync`), plays the returned `AudioClip` via `AudioSource.PlayOneShot`, samples PCM frames during playback (lines 99-127) and feeds them to `HandlePlayingSamples` for external lip-sync helpers.
9. **The avatar speaks.** Lip-sync runs from the audio samples via `uLipSyncHelper` (or VRM variant). Face stays on whatever `FaceController.SetFace` last set. Animation runs from `ModelController.Animate`'s queue. Blink runs on its own random-interval loop.

**Nine phases. Each phase owned by exactly one subsystem.** No subsystem reaches across more than one boundary; AIAvatar is the only thing that touches more than two. This is the lifecycle that SAP scattered across `server.py:2400-6000` ([[sap:10_DOMAIN_MAP]] §4) — CDK puts each phase in its own file.

---

## 5. Where the Bones Are Honest (and the Few Cracks)

### 5.1 The clean subsystem separation

This is the *most* honest architecture of the three corpora. SAP had `server.py` as a black hole. Waifu was a vestibule pointing at someone else's cloud ([[waifu:10_DOMAIN_MAP]] §1). CDK has eight peer subsystems, each with one job, each registered as a Unity component on the same GameObject. The pattern is:

```csharp
// /tmp/ChatdollKit/Scripts/AIAvatar.cs:116-119
MicrophoneManager = MicrophoneManager ?? gameObject.GetComponent<IMicrophoneManager>();
ModelController = ModelController ?? gameObject.GetComponent<ModelController>();
DialogProcessor = DialogProcessor ?? gameObject.GetComponent<DialogProcessor>();
LLMContentProcessor = LLMContentProcessor ?? gameObject.GetComponent<LLMContentProcessor>();
```

Each is a `MonoBehaviour` attached to the same prefab. Each is independently swappable — swap out `MicrophoneManager` for a custom one, AIAvatar still works. Swap in a different `ModelController` subclass, the dialog flow is unchanged. This is the *Unity component dependency injection* pattern — and CDK uses it for genuine architectural benefit, not just because Unity provides it.

### 5.2 The LLMService multiplex by enabled-flag

`DialogProcessor.SelectLLMService` iterates every `ILLMService` on the GameObject and picks the first with `IsEnabled == true` (lines 81-113). To switch from ChatGPT to Claude: toggle `IsEnabled` on two components. No code changes. No reconfiguration. The same pattern applies to `ISpeechListener` (AIAvatar.cs:294-313) and `ISpeechSynthesizer` (AIAvatar.cs:316-328).

This is the cleanest LLM-multiplexing pattern across our three corpora. SAP had string-switch dispatch in `server.py`. Waifu had a single cloud LLM hidden in ZeroWeight. CDK has *six co-resident providers* and the choice is a checkbox. The cost: every provider's per-frame `Update` runs even when only one is active. The Unity scheduling makes this trivial; for a Python rewrite, Ember should switch to an active-only registration.

### 5.3 The `[anim:Name]`/`[face:Expression]` tag protocol

`ModelController.ToAnimatedVoiceRequest` (`Model/ModelController.cs:237-292`) uses a regex over the LLM's streamed text:

```csharp
// /tmp/ChatdollKit/Scripts/Model/ModelController.cs:247-249
var pattern = @"(\[.*?\])|([^[]+)";
foreach (Match match in Regex.Matches(inputText, pattern))
{
    var parsedText = match.Value.Trim();
    if (parsedText.StartsWith("[face:")) { ... }
    else if (parsedText.StartsWith("[anim:")) { ... }
    else if (parsedText.StartsWith("[pause:")) { ... }
}
```

The LLM emits `Hello! [face:Joy][anim:Wave] Nice to meet you.` and CDK parses it into a face-change + animation-trigger + voice-utterance triple. This is the same pattern as SAP's `<happy>` (`server.py:2557`) and the same pattern as Waifu's `runAction("dance")` ([[waifu:20_ZEROWEIGHT_SURFACE]] §3.1) — but **CDK does it inline within the spoken text**, parsed in the same pass that splits sentences. Tighter coupling between speech and expression than either sibling corpus achieves. The full protocol is documented at [[25_ANIMATION_TAG_PROTOCOL]].

### 5.4 The SocketServer trust gap

`Network/SocketServer.cs:88` binds:

```csharp
server = new TcpListener(IPAddress.Any, port);
```

`IPAddress.Any` — meaning every interface, every IP, all comers. There is no authentication. There is no TLS. There is no message HMAC. Any process that can reach the port can send a `{"Endpoint": ..., "Operation": ..., "Text": ..., "Payloads": ...}` JSON line and trigger an `OnDataReceived` call into the dialog pipeline.

This is a real surface. On a developer machine behind a firewall it is fine. On a deployed app — particularly on mobile or in a multi-user lab — it is a gift to anyone with `netcat`. The Auditor's [[27_SOCKET_PROTOCOL]] catalogues the failure modes. For Ember the lesson is binding-by-default-to-Tailnet-only with a per-message token (Volmarr's standing preference).

### 5.5 The JavaScriptMessageHandler trust gap (WebGL)

`IO/JavaScriptMessageHandler.cs:35-51` registers `HandleMessageFromJavaScript(string message)` as the inbound bridge from page-side JS. There is **no origin check**, **no token**, **no schema validation beyond `JsonConvert.DeserializeObject<ExternalInboundMessage>`** — any script on the host page can drive the avatar. This is per-build acceptable (the WebGL build's host page is your own), but anyone embedding the build in an iframe inherits the same trust. See [[28_JS_BRIDGE_INTERFACE]] (Auditor) for the catalogue.

### 5.6 The unauthenticated `[anim:]` vocabulary

`ModelController.ToAnimatedVoiceRequest` silently drops unregistered animations (`Model/ModelController.cs:266-269`):

```csharp
if (IsAnimationRegistered(anim))
{
    var a = GetRegisteredAnimation(anim);
    avreq.AddAnimation(...);
}
else
{
    Debug.LogWarning($"Animation {anim} is not registered.");
}
```

The LLM can ask for any animation; only registered ones fire; failures are `Debug.LogWarning`s the user does not see. Combined with the prompt-injection of available animations (the user-side recommendation is to list them in the system prompt), this works *most* of the time and silently degrades when prompt and registry drift. SAP had the same problem at `server.py:2557` ([[sap:10_DOMAIN_MAP]] §5.4); CDK's version is no worse but no better. See [[25_ANIMATION_TAG_PROTOCOL]].

### 5.7 The `AIAvatar.cs` does too much

`AIAvatar.cs` is 664 lines and ten responsibilities. It is the *one* file in CDK that violates the single-responsibility line — its `Awake()` registers callbacks across `MicrophoneManager`, `ModelController.SpeechController.OnSayStart/OnSayEnd`, `DialogProcessor.OnRequestRecievedAsync/OnEndAsync/OnStopAsync/OnErrorAsync`, and `LLMContentProcessor.HandleSplittedText/ProcessContentItemAsync/ShowContentItemAsync`. The 664 lines is *not* `server.py`'s 11,652 — but it is the only place in CDK where the smell of an SAP-style coordinator appears. The lesson for Ember is to *split* this coordinator role across two pieces: a *configuration* coordinator (declarative wiring) and a *runtime* coordinator (the state machine). See [[11_AIAVATAR_DOMAIN]] for the deeper read.

---

## 6. The Unity Cost — What Commits to the Engine Mean

CDK's elegance has a price tag. The price is *Unity*. Unity is:

- **Proprietary**, with seat licensing for commercial revenue over a threshold (currently $200K/year). Apache-2.0 of CDK does not undo Unity's EULA.
- **Heavy** — the smallest Unity build is ~10MB on mobile, 30-50MB on desktop, larger with assets. Compared to a Python+TUI Ember, this is a 100x size delta.
- **Asset-pipeline-bound** — `*.prefab`, `*.asset`, `*.unity`, `*.meta` files everywhere, GUID-based references that are *not* human-mergeable. Multi-author code is fine; multi-author scenes are a coordination problem.
- **Build-target-fragmented** — Win/Mac/Linux/iOS/Android/VR/AR/WebGL all need their own build process, their own platform certs, their own QA pass. The 8 build targets ([[1D_MULTI_PLATFORM_DOMAIN]]) are a feature *and* a tax.
- **Editor-dependent** — most CDK setup involves the Unity Editor (assign references in the Inspector, drag prefabs, configure ScriptableObjects). Headless setup is possible but painful. See [[1C_UNITY_LIFECYCLE_DOMAIN]].

This is what the eight-clean-subsystem architecture *bought*. Ember's Pi-tier baseline cannot afford this. Ember's laptop-tier and workstation-tier *might* be able to — as a **Tier-UNITY** optional embodiment, not the baseline. The decision matrix is in [[60_synthesis:60_TRIANGULATION]] (Cartographer).

The honest reading: **CDK's architecture is excellent; CDK's platform is expensive.** Ember can learn the patterns without paying the platform tax — Python implementations of these subsystem boundaries work fine. The Unity-specific advantages (real-time animation blending, mature 3D pipeline, VR/AR support) are *opt-in luxuries*, not load-bearing.

---

## 7. The Sister-Project Ecosystem

CDK does not stand alone. The same author (uezo) maintains a tethered ecosystem the codex must map:

- **ChatMemory** (`github.com/uezo/chatmemory`) — FastAPI service for episodic memory; CDK integrates via `Extension/ChatMemory/ChatMemoryIntegrator.cs`. Hjarta-relevant. Forge-B writes the deep dive at [[38_CHATMEMORY_INTEGRATION]]; Architect references it at [[1A_MEMORY_DOMAIN]].
- **AIAvatarKit** (`github.com/uezo/aiavatarkit`) — Speech-to-Speech streaming pipeline; the `AIAvatarKitStreamSpeechListener` (375 LOC) and `AIAvatarKitService` (448 LOC) are CDK's integration. Rödd-streaming reference. Forge-B at [[39_AIAVATARKIT_STREAMING]].
- **AITuber Controller** (`github.com/uezo/chatdollkit-aituber`) — VTuber streaming integration. Broadcast-tier reference. Forge-B at [[3A_AITUBER_CONTROLLER]].
- **OshaberiAI** — uezo's iOS production app shipping CDK + VOICEVOX. The existence proof that CDK ships to mobile App Stores.

The sister ecosystem is **a deliberate architectural decision**: keep CDK's core small (18k LOC), push optional capabilities into sister repos with their own release cadence. This is the inverse of SAP's monorepo-mountain ([[sap:10_DOMAIN_MAP]] §5.1). It is, again, a feature *and* a tax — version drift across four repos is real (the Auditor catalogues at [[56_SISTER_INTEGRATION_RISKS]]).

---

## 8. Cross-References

- [[11_AIAVATAR_DOMAIN]] — AIAvatar coordinator (the one file too big)
- [[12_MODEL_CONTROLLER_DOMAIN]] — Model subsystem
- [[13_DIALOG_PROCESSOR_DOMAIN]] — Dialog state machine
- [[14_SPEECH_LISTENER_DOMAIN]] — STT pipeline
- [[15_SPEECH_SYNTHESIZER_DOMAIN]] — TTS pipeline + Japanese stack
- [[16_LLM_SERVICE_DOMAIN]] — LLM abstraction
- [[17_MICROPHONE_MANAGER_DOMAIN]] — Audio capture
- [[18_NETWORK_DOMAIN]] — SocketServer + JS bridge
- [[19_TOOL_DOMAIN]] — Function calling
- [[1A_MEMORY_DOMAIN]] — ChatMemory integration
- [[1B_ANIMATION_DOMAIN]] — Tag protocol details
- [[1C_UNITY_LIFECYCLE_DOMAIN]] — Unity-specific costs
- [[1D_MULTI_PLATFORM_DOMAIN]] — Eight build targets
- [[20_LLM_SERVICE_INTERFACE]] — `ILLMService` contract
- [[24_VAD_INTERFACE]] — SileroVAD plug-in
- [[25_ANIMATION_TAG_PROTOCOL]] — Tag wire format
- [[26_TOOL_FUNCTION_CALL_INTERFACE]] — `ITool` contract
- [[29_VRM_INTERFACE]] — UniVRM integration
- [[sap:10_DOMAIN_MAP]] — server-eaten Electron contrast
- [[waifu:10_DOMAIN_MAP]] — cloud-vestibule contrast
- [[60_synthesis:60_TRIANGULATION]] — three-corpus decision matrix
- [[hermes:10_DOMAIN_MAP]] — Hermes shape contrast

---

## What This Means for Ember

**Adopt:**
- The **subsystem-as-folder discipline** of `Scripts/<Subsystem>/`. Apply to Ember's Python: `ember/funi/`, `ember/strengr/`, `ember/brunnr/`, `ember/smiðja/`, `ember/hjarta/`, `ember/munnr/` — each a package with one `__init__.py`, an `INTERFACE.md`, and a `README_AI.md`. CDK source: `Scripts/ChatdollKit.asmdef` — Apache-2.0 attribution required.
- The **interface-then-implementation** pattern of `ILLMService` + `LLMServiceBase` + per-provider concrete classes (`Scripts/LLM/ILLMService.cs:8`, `Scripts/LLM/LLMServiceBase.cs:11`). Ember's `AndlitProtocol`, `RöddProtocol`, `BrunnrProtocol` follow this shape with Python `Protocol` classes and an `<Name>Base` ABC.
- The **GameObject-as-DI-container** pattern adapted to Python: a single `EmberRuntime` object exposes registered subsystems and lookups by interface name. Ember's `runtime.get(IFoo)` mirrors `gameObject.GetComponent<IFoo>()`.
- The **enabled-flag multiplex** for swappable backends (`DialogProcessor.SelectLLMService` at `Scripts/Dialog/DialogProcessor.cs:81-113`). Ember's `brunnr_config.yaml` lists candidate providers; the runtime picks the first with `enabled: true`. Switching providers is one bool flip. Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).

**Adapt:**
- **AIAvatar.cs as a two-layer coordinator.** CDK puts wiring (`Awake`) and state machine (`Update`, `UpdateMode`) in the same file. Ember splits into `ember_config.py` (declarative wiring loaded from YAML at startup) + `ember_runtime.py` (the state machine that runs per-tick). 664 lines becomes two ~300-line files with one job each.
- The **`[anim:Name]` regex extraction** (`Scripts/Model/ModelController.cs:247-249`). Adapt to Ember's Munnr as an explicit `parse_animation_tags(text: str) -> list[Tag]` function with a *typed* `Tag` enum (no `Debug.LogWarning` silent drops; missing tags raise `UnknownTagWarning` events on the Sögumiðla bus proposed in [[sap:10_DOMAIN_MAP]] §invent).
- The **per-frame `Update()` polling** of the SocketServer queue (`Scripts/Network/SocketServer.cs:42-53`). Adapt to Ember's asyncio: a dedicated coroutine awaits a `Queue.get()` instead of polling. Same architectural pattern (thread-safe enqueue, single-thread dispatch); native to the runtime.
- The **interface-segregated extensions** (`Extension/SileroVAD/`, `Extension/VRM/`, `Extension/ChatMemory/`). Adapt as Ember's `ember/extensions/<name>/` namespace, each opt-in, each with a `pyproject.toml` extras-tag (`pip install ember[silerovad]`). Modular Authorship operationalised.

**Avoid:**
- **`AIAvatar.cs` as a single-file coordinator.** It is the one file in CDK that smells like SAP. Even at 664 lines, the responsibility count is too high. Ember's coordinator splits.
- **`IPAddress.Any` socket binds without auth.** `Scripts/Network/SocketServer.cs:88` is acceptable for a developer-machine demo. It is malpractice on a deployed surface. Ember's equivalent binds to the Tailscale interface by default with a per-process token.
- **Silent-drop on unknown tags.** Logging a warning the user never sees is worse than an explicit failure. Ember's tag parser emits a typed event that *something* (a UI surface, a log review tool, a session post-mortem) can act on.
- **Unity as a baseline.** CDK proves the patterns work. Unity itself is a luxury — the patterns are portable to Python, to Rust, to anything with a component model. Do not adopt Unity to get the architecture; adopt the architecture and pick the platform on its own merits.

**Invent:**
- **The Subsystem Census Vow.** Before any Ember subsystem ships, it must declare a header comment matching the CDK folder rule: *what it owns, what it does not own, what its interface contract is, what extensions register against it*. The Boundary Census proposed at [[sap:10_DOMAIN_MAP]] §invent crystallises here as a `SUBSYSTEM.md` per package, mandatory on PR.
- **Tier-UNITY as an Optional Andlit Surface.** Ember's existing tier ladder (Pi / laptop / workstation, [[sap:60_TRUE_NAME_REASSIGNMENT]]) gets a parallel tier — `Tier-UNITY` — for users who want the full 3D embodiment. It is *opt-in*, *replaceable*, and *strictly delegated to* CDK-style components running in a Unity sub-process Ember communicates with over the SocketServer/JS-bridge surfaces. The Pi baseline does not depend on Unity at any layer.
- **The Coordinator Split Rite.** Every Ember coordinator over 200 lines splits into (configuration, state). Configuration is declarative + loadable from YAML. State is a typed FSM. This is the procedural antidote to the AIAvatar.cs smell, generalised. Apply also retroactively to any future Ember subsystem.
- **Inter-Subsystem Contract Registry.** When subsystem A calls into subsystem B, the call is *registered* in `docs/contracts/A_to_B.md` with input/output shapes and a versioned changelog. Subsystem B's owner must sign off on contract changes. SAP had no such discipline (`server.py` cross-cut everything); CDK has it implicitly (every cross-call is an interface invocation); Ember makes it explicit and reviewable.
- **The "Substrate Tax" Annotation.** Every Ember dependency carries a `# substrate-tax: <kind>, <size>` annotation. Unity's substrate tax is "proprietary engine, 10-50MB binary, 8 build targets." Ember surfaces this for every dependency added. The Vestibule Census from [[waifu:10_DOMAIN_MAP]] §invent generalises here.

*Apache-2.0 attribution: when patterns from `ChatdollKit` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

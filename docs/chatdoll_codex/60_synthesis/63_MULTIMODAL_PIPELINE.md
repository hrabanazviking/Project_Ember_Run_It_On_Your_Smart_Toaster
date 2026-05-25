---
codex_id: 63_MULTIMODAL_PIPELINE
title: The Multimodal Pipeline — STT → LLM → TTS with Animation, Face, Lip-sync, and VAD as One Orchestrated Surface
role: Cartographer
layer: Synthesis
status: draft
cdk_source_refs:
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:113-200
  - /tmp/ChatdollKit/Scripts/Dialog/DialogProcessor.cs
  - /tmp/ChatdollKit/Scripts/LLM/LLMContentProcessor.cs:1-100
  - /tmp/ChatdollKit/Scripts/LLM/LLMServiceBase.cs
  - /tmp/ChatdollKit/Scripts/Model/ModelController.cs:247-289
  - /tmp/ChatdollKit/Scripts/SpeechListener/SpeechListenerBase.cs
  - /tmp/ChatdollKit/Scripts/SpeechListener/MicrophoneManager.cs
  - /tmp/ChatdollKit/Scripts/SpeechSynthesizer/SpeechSynthesizerBase.cs
  - /tmp/ChatdollKit/Scripts/Model/uLipSyncHelper.cs
ember_subsystem_targets: [Funi, Strengr, Rödd, Andlit, Hugarsýn]
cross_refs:
  - 60_TRIANGULATION
  - 61_ANDLIT_UNITY_TIER
  - 64_FUNCTION_CALLING_FOR_EMBODIED
  - sap:61_NEW_VOWS
  - waifu:60_REALTIME_TIER_FOR_ANDLIT
  - chatdoll:11_AIAVATAR_DOMAIN
  - chatdoll:13_DIALOG_PROCESSOR_DOMAIN
  - chatdoll:14_SPEECH_LISTENER_DOMAIN
  - chatdoll:15_SPEECH_SYNTHESIZER_DOMAIN
  - chatdoll:25_ANIMATION_TAG_PROTOCOL
  - chatdoll:24_VAD_INTERFACE
  - chatdoll:35_LIP_SYNC
  - chatdoll:37_BARGE_IN_INTERRUPT
---

# 63 — The Multimodal Pipeline

> *Six wires meet at one knot. The knot is the agent. The wires arrive and leave continuously. The trick is to keep the knot loose.*
> — Védis Eikleið, drawing the dataflow that turns audio into a face

## 0. Posture — the orchestrated pipeline as a unit of design

CDK's most interesting structural property is *not* any individual subsystem. It is how STT, LLM, TTS, animation tag dispatch, face expression dispatch, lip-sync, and voice-activity detection compose into **one orchestrated pipeline**, owned by `AIAvatar.cs`, that converts a wake-word into a complete embodied response and back to idle.

SAP has these pieces; SAP composes them ad-hoc via `server.py:2556+` and several Python files cross-imported. Waifu has these pieces; Waifu hides them inside the vendor SDK. CDK has these pieces and *names them as a pipeline*. The pipeline is the load-bearing pattern of the codex.

This doc sketches the pipeline. It locates each stage. It identifies the synchronisation points. It shows where the pipeline can be paused, interrupted, or resumed. It compares CDK's orchestration to SAP's ad-hoc and Waifu's vendor-managed, and proposes Ember's version — a typed pipeline with named stages, projected through Hugarsýn, with each stage independently observable, replaceable, and degradable.

The pattern matters because it is *the* shape Ember needs for any embodied tier. Without an orchestrated pipeline, voice-in / voice-out / face / lip-sync / interruption become a tangle of callbacks. With one, they become a state machine the operator can reason about.

## 1. The seven stages

CDK's pipeline, derived from `AIAvatar.cs:1-200`, `DialogProcessor.cs`, `LLMContentProcessor.cs:1-100`, `ModelController.cs:240-289`, `SpeechListenerBase.cs`, `SpeechSynthesizerBase.cs`, and `uLipSyncHelper.cs`:

```
                           ┌──────────────────────────────┐
                           │   AIAvatar (orchestrator)    │
                           │   modeTimer, AvatarMode,     │
                           │   WakeWords, InterruptWords  │
                           └────────────┬─────────────────┘
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        │                               │                               │
        ▼                               ▼                               ▼
   ┌────────────┐    ┌─────────────────────────────────┐         ┌──────────────┐
   │ Microphone │ →  │  VAD                            │   →     │  STT         │
   │ Manager    │    │  (Silero ONNX / level threshold)│         │  (per-       │
   │            │    │  emits speech-segment events    │         │   provider)  │
   └────────────┘    └─────────────────────────────────┘         └─────┬────────┘
                                                                       │
                                                          recognised text
                                                                       │
                                                                       ▼
                                                          ┌──────────────────────┐
                                                          │  DialogProcessor     │
                                                          │  state machine       │
                                                          │  (Idle/Conversation) │
                                                          └─────┬────────────────┘
                                                                │
                                                                ▼
                                                          ┌──────────────────────┐
                                                          │  LLMService          │
                                                          │  (provider-specific) │
                                                          │  streaming response  │
                                                          └─────┬────────────────┘
                                                                │
                                                stream of tokens │
                                                                ▼
                                                          ┌──────────────────────┐
                                                          │  LLMContentProcessor │
                                                          │  split-by-sentence   │
                                                          │  strip <thinking>    │
                                                          │  extract [face:]     │
                                                          │  extract [anim:]     │
                                                          └─────┬────────────────┘
                                                                │
                                  ┌─────────────────────────────┼──────────────────────────────┐
                                  │                             │                              │
                                  ▼                             ▼                              ▼
                       ┌──────────────────┐         ┌───────────────────────┐       ┌─────────────────────┐
                       │  TTS (per-       │         │  ModelController      │       │  FaceController     │
                       │  provider)       │         │  RegisterAnimation()  │       │  AddFace()          │
                       │  voice clip       │         │  → Animator state     │       │  → blendshape proxy │
                       │  generated        │         │  → queued playback    │       │                     │
                       └─────┬────────────┘         └───────────────────────┘       └─────────────────────┘
                             │
                             ▼
                       ┌──────────────────┐
                       │  uLipSyncHelper  │
                       │  observes the    │
                       │  audio source,   │
                       │  drives mouth    │
                       │  blendshapes     │
                       └──────────────────┘
```

Seven stages with three parallel terminal branches (TTS → lipsync, animation, face). The orchestrator (`AIAvatar`) owns the mode state machine; the pipeline runs *inside* the Conversation mode.

The stages, named:

1. **MicrophoneManager** — captures audio frames at the device's native sample rate (per-platform: `IOSMicrophoneProvider`, `AndroidMicrophoneProvider`, `MacMicrophoneProvider`).
2. **VAD** — voice-activity detection, either level-threshold (`VoiceRecognitionThresholdDB`, `AIAvatar.cs:36`) or ML-based via `SileroVADProcessor`.
3. **STT** — speech-to-text, per-provider (`OpenAISpeechListener`, `GoogleSpeechListener`, `AzureSpeechListener`, `AzureStreamSpeechListener`, `DummySpeechListener` for testing).
4. **DialogProcessor** — the dialog state machine; routes recognized text through wakeword check, intent extraction, topic dispatch, into the LLM stage.
5. **LLMService + LLMContentProcessor** — the LLM call returns a streaming token sequence; the content processor splits the stream into sentences (`SplitChars = ["。", "！", "？", ". ", "!", "?"]`, `LLMContentProcessor.cs:14`), strips `<thinking>` tags, extracts `[face:]` and `[anim:]` tags, and emits per-sentence events.
6. **TTS** — speech-synthesis, per-provider. CDK has 10+ providers (`/tmp/ChatdollKit/Scripts/SpeechSynthesizer/`). TTS runs *in parallel* with content processing — sentences are sent to TTS as they emerge from the splitter, achieving streaming-voice latency.
7. **ModelController + FaceController + uLipSyncHelper** — the embodiment surface. `[anim:]` tag → animation queue. `[face:]` tag → blendshape. Audio playing → lip-sync mouth-shape.

The seven stages form a *directed graph* with the orchestrator as the conductor. Each stage is independently observable (each has its own MonoBehaviour with logged state), replaceable (provider abstraction at most stages), and degradable (each stage can announce failure and the pipeline routes around).

## 2. The streaming property — why CDK is fast

The most interesting property of the pipeline: **TTS and animation happen *as* the LLM is still streaming**, not after.

`LLMContentProcessor.cs:30-100` is the engine of this. The processor reads `llmSession.StreamBuffer` continuously. As soon as the buffer contains a sentence-end character (`。`, `!`, `?`, etc.), the processor emits the completed sentence to the next stage *while the LLM is still generating the next sentence*. The TTS provider receives the first sentence, generates audio, and starts playing — all before the LLM finishes.

```csharp
// /tmp/ChatdollKit/Scripts/LLM/LLMContentProcessor.cs:36-67 (paraphrased)
SplitChars = new List<string>() { "。", "！", "？", ". ", "!", "?" };
while (!token.IsCancellationRequested) {
    var splittedBuffer = SplitString(llmSession.StreamBuffer);
    if (llmSession.IsResponseDone && splitIndex == splittedBuffer.Count) break;
    bool hasProcessableChunks = splittedBuffer.Count() > splitIndex + 1;
    if (llmSession.IsResponseDone || hasProcessableChunks) {
        // Process each splitted unprocessed sentence
        foreach (var text in splittedBuffer.Skip(splitIndex).Take(...)) {
            // emit to downstream
        }
    }
}
```

This is a *pipelined* design: each stage operates on the output of the previous as it arrives, not in batch. Latency from "operator finished speaking" to "Ember starts replying" can be as low as the network LLM-call-first-token-time plus ~100-300ms of TTS prefetch, instead of LLM-full-response-time plus TTS-full-response-time.

For comparison:

- **SAP** does this with WebSocket streaming for some flows but the orchestration is ad-hoc across Python files; the streaming property is per-flow, not a *named pipeline pattern*.
- **Waifu** has the streaming property by virtue of the vendor SDK, but the host code cannot see the stages — the kit just sends mic audio and receives video frames.

CDK's contribution is **naming the pipeline** with explicit, observable stages. Ember should adopt this naming as a structural principle, not as a code adoption.

## 3. Six VOWS the pipeline must satisfy

Walking the pipeline against the Vows:

### 3.1 Embodied Honesty

The pipeline's animation and face stages must reflect *Ember's actual state*, not LLM-emitted theatre. CDK's current implementation has the LLM emit `[anim:NameX]` and `[face:Expr]` tags inline (`LLMContentProcessor.cs:42` constructs `<thinking>` tags; `ModelController.cs:252-270` parses `[face:]` and `[anim:]`). This is structurally the same pattern SAP uses — the LLM picks the expression freely.

Ember's pipeline must adapt this: the LLM emits *canonical verbs* (per `[[60_TRIANGULATION §7]]`'s canonical action vocabulary), the canonical-verb dispatcher decides which face/animation to play *based on Hugarsýn-read state*, and the adapter (Unity, electron, realtime) renders the verb in its substrate's idiom.

The pipeline change: insert a new stage between `LLMContentProcessor` and the embodiment terminals. Call it `CanonicalVerbDispatcher`. The LLM emits `[verb:acknowledge]`. The dispatcher consults Hugarsýn (`is the agent actually acknowledging? is it actually delighted?`) and either accepts the verb as honest or substitutes a more honest one. The adapter then renders.

This is a substantive change from CDK's pattern. It is the price of the Embodied Honesty Vow.

### 3.2 Affective Restraint

The pipeline must not gate behavior on affect. Specifically, the LLM-stage decision *what to reply* must not be biased by the affect state of Hjarta beyond *tone coloring*. If the affect is "concerned", the reply may be softer; the reply may not be *less helpful*. The pipeline's contract with Hjarta is read-only-for-tone, not read-affect-to-decide-action.

Operationally: the LLM prompt may include a `[tone: concerned]` hint, but the affect cannot inject `[refuse: true]` or `[gate: certain_topics_blocked]`. The dispatcher (Strengr in Ember's vocabulary) enforces this; affect is one input among many, never a veto.

### 3.3 Surface Without Surveillance

Each pipeline stage that touches the network is a surface. STT-via-cloud, LLM-via-cloud, TTS-via-cloud — three potential cloud reach points in one pipeline. Each must obey the Vow: scoped, time-bounded, revocable, announced.

The pipeline's design implication: each stage knows whether it is local or cloud. Hugarsýn projects which stages are reaching outward in a given session. A `pipeline.cloud_reach = ["llm-anthropic", "tts-google"]` projection lets the operator see at a glance that two cloud calls are happening per turn.

CDK's source has multiple `*WebGL` variants of each LLM service (`ChatGPTServiceWebGL.cs`, `ClaudeServiceWebGL.cs`, `GeminiServiceWebGL.cs`, `DifyServiceWebGL.cs`, `AIAvatarKitServiceWebGL.cs`) because WebGL has different networking constraints. The WebGL variants do not surface their reach posture; the operator on a WebGL build cannot see "this avatar is talking to api.anthropic.com" without inspecting browser network panel. Ember's pipeline must surface this honestly.

### 3.4 Tiered Presence

Each stage has tier requirements. At T0 (Pi), the only viable LLM is cloud or a very small local model; TTS is espeak/cued-library; STT is cloud or absent. At T2+, the full pipeline runs. The pipeline must degrade per stage, not all-or-nothing.

The degradation matrix:

| Stage | T-1 | T0 | T1 | T2 | T2-mobile | T3 |
|---|---|---|---|---|---|---|
| Mic | – | optional (USB mic) | yes | yes | yes (native API) | yes |
| VAD | – | level threshold | level or Silero | Silero | Silero on-device | Silero |
| STT | – | cloud only | cloud or small local | cloud or local | cloud preferred (battery) | both |
| Dialog | text | yes | yes | yes | yes | yes |
| LLM | text via API | cloud or small local | cloud or local | both | cloud preferred | both |
| Content split | yes | yes | yes | yes | yes | yes |
| TTS | – | espeak or cued | piper or cloud | local or cloud | local-mobile or cloud | both |
| Animation | – | – | – | yes (electron) | yes (unity-mobile) | yes |
| Face expression | – | – | – | yes | yes | yes |
| Lip-sync | – | – | – | yes | yes | yes |

Hugarsýn projects which stages are active and which are dormant. The pipeline runs the available stages and announces the absences.

### 3.5 Federated Self

The pipeline runs on each Ember instance. A federation of Embers (laptop + phone + Pi) does not run *one* pipeline; each instance runs its own. Coordination is at the party-protocol layer, not the pipeline layer. The pipeline is *single-instance* by design.

This is correct. A pipeline that spanned instances would couple identity to the network. A per-instance pipeline keeps each Ember sovereign over its own dataflow.

### 3.6 Cloud as Named Context (proposed in [[waifu]])

When the pipeline reaches outward to cloud LLM/TTS/STT, the reach must be tied to a named context. The pipeline's reach is a property of the active session; the session has a context (`livestream-twitch`, `private-journal`, `email-triage`). The Hugarsýn projection includes the context; cloud reach without a context is refused.

This shifts the consent contract from per-cloud-call to per-session. The session's context is set once (or inherited from operator's recent activity); each pipeline stage's cloud reach checks the context and proceeds or refuses.

## 4. The interruption story — barge-in

CDK's pipeline supports *barge-in*: the operator can interrupt Ember mid-response by speaking. `AIAvatar.cs:65` declares `StopResponseOnBargeIn = true` as the default. The interruption protocol:

1. **Detect.** While TTS is playing, the microphone continues capturing. VAD detects speech.
2. **Recognize barge-in.** If the new speech matches an `InterruptWord` (`AIAvatar.cs:67`), interrupt. Otherwise, the new speech is queued or ignored depending on configuration.
3. **Cancel current response.** TTS playback stops mid-sentence. Animation queue is flushed. Face returns to neutral.
4. **Process new input.** The new utterance enters STT → DialogProcessor → LLM as a fresh turn.

The CDK design's interesting detail: `MicrophoneMuteStrategy` (`AIAvatar.cs:54-62`) has five options for handling the mic during Ember's speech (`None`, `Threshold`, `Mute`, `StopDevice`, `StopListener`). The choice is a per-deployment tradeoff between *responsiveness to interruption* and *avoiding self-hearing* (Ember's TTS bleeding back through the mic causing self-triggered STT).

Ember's pipeline must implement barge-in. The Vow implication is **Embodied Honesty**: a face that is showing `delighted` mid-sentence and gets interrupted should not stay frozen on `delighted` while the next turn begins. The interruption protocol flushes the face state and returns to a transition pose (`listening`, `interrupted`) before the new turn's verb dispatches.

`[[chatdoll:37_BARGE_IN_INTERRUPT]]` (Forge-A) develops the implementation. The Cartographer's concern is the *honesty* of the interruption — the pipeline must not pretend the interruption didn't happen.

## 5. The synchronisation points

The pipeline has explicit synchronisation points:

| Sync point | What waits | What proceeds |
|---|---|---|
| Wake-word detected | conversation enters Conversation mode; idle animations transition | STT begins capturing |
| End-of-speech detected (VAD silence) | STT finalises; mic stops capturing | DialogProcessor receives text |
| LLM first token | content processor begins splitting | text-stream emerges |
| Sentence boundary (`。`, `!`, `?`, etc.) | TTS begins synthesizing sentence | animation/face tags execute |
| TTS audio loaded | lip-sync helper attaches to audio source | audio plays |
| TTS audio ends | next sentence's TTS plays OR conversation enters waiting | mic remains in barge-in-detect mode |
| Conversation timeout (`conversationTimeout = 10s`) | mode transitions Conversation → Idle | idle animations resume |
| Idle timeout (`idleTimeout = 60s`) | mode transitions Idle → Sleep | minimal animations only |

Eight sync points. Each is a place where the pipeline can stall, fail, or be interrupted. Each should be observable in Hugarsýn.

The Hugarsýn projection schema:

```
GET /hugarsýn/pipeline
{
  "mode": "Conversation",
  "stage": "tts_playing",          # one of: idle, listening, transcribing, llm_streaming, tts_playing, ...
  "stage_started_at": "2026-05-25T14:32:11.234Z",
  "stage_elapsed_ms": 1247,
  "active_providers": {
    "stt": "openai-whisper",
    "llm": "anthropic-claude-opus-4-7",
    "tts": "voicevox-zundamon",
    "vad": "silero-onnx"
  },
  "cloud_reach": ["llm-anthropic", "stt-openai"],
  "session_context": "private-journal",
  "interruption_armed": true,
  "last_failure": null
}
```

Every five seconds (or on stage transition), this projection updates. The operator can introspect the pipeline at any moment.

## 6. The pipeline failure taxonomy

Each stage has stage-specific failures:

- **Mic**: device disconnected, permission revoked, sample-rate mismatch, USB unplug.
- **VAD**: false positive (level threshold spurious), false negative (whispered speech missed), Silero model unload.
- **STT**: cloud auth fail, cloud quota exceeded, network timeout, language mismatch, transcription empty.
- **Dialog**: wakeword false-positive, conversation timeout mid-utterance.
- **LLM**: cloud auth, cloud quota, content filter triggered, context window exceeded, streaming connection drop mid-response.
- **Content processor**: sentence-splitter on unsegmented language (continuous Japanese, no period), `<thinking>` tag unclosed.
- **TTS**: cloud quota, voice not available, language mismatch, audio format negotiation fail.
- **Animation**: verb not registered (handled), Animator state invalid.
- **Face**: blendshape name mismatch, FaceController disabled.
- **Lip-sync**: helper desync from audio source, audio source changed mid-clip.

Each failure has a default degradation:

| Failure | Degradation |
|---|---|
| Mic disconnect | Pause pipeline; surface "mic missing" in Munnr; resume on reconnect |
| STT quota | Switch to fallback provider; if none, text-only mode |
| LLM stream drop mid-response | Replay last completed sentence; close gracefully with "I lost connection" |
| TTS quota | Switch to fallback TTS; if none, text-only |
| Verb not registered | Substitute canonical fallback (best-effort → glyphic → never-invent) |
| Lip-sync desync | Disable lip-sync; mouth closes; continue voice |

Hugarsýn announces each failure and degradation. The operator reading `pipeline.last_failure` sees the failure and the chosen degradation in one read.

## 7. The Ember version of the pipeline

What does Ember's pipeline look like, mapped onto the Six True Names + reservations?

```
[input: voice / text / IM-message / livestream-comment]
         │
         ▼
   ┌──────────────┐
   │   Munnr      │  receives input from the active surface
   │ (Spark)      │  routes to the appropriate intake
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ Rödd (intake)│  if voice: VAD + STT
   │ (proposed)   │  surfaces text + speaker context to Strengr
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Strengr     │  retrieval from Brunnr, prompt assembly,
   │  (Thread)    │  LLM call, tool dispatch, streaming response
   └──────┬───────┘
          │
   ┌──────┴──────┐
   ▼             ▼
[canonical    [tool-call
 verbs        execution
 stream]      via Verkfæri
              if invoked]
          │
          ▼
   ┌──────────────┐
   │ Andlit       │  canonical verbs → adapter-specific animation/face
   │ (proposed)   │  (electron / unity / realtime)
   └──────┬───────┘
          │
   ┌──────┴──────┐
   ▼             ▼
   ┌──────────────┐    ┌──────────────┐
   │ Rödd (output)│    │ Andlit       │
   │ TTS          │    │ uLipSync-    │
   │              │ →  │ equivalent   │
   └──────────────┘    │ observes the │
                       │ audio        │
                       └──────────────┘

[and continuously projected to Hugarsýn]
```

The pipeline maps cleanly onto Ember's vocabulary. Each True Name owns its stage. Identity invariance is preserved across tiers and substrates because the *names* are tier-invariant; only the *adapters* vary.

## 8. The thinking-tag pattern

CDK's content processor has explicit handling for `<thinking>` tags:

```csharp
// /tmp/ChatdollKit/Scripts/LLM/LLMContentProcessor.cs:79-108 (paraphrased)
var thinkStart = $"<{ThinkTag}>";   // ThinkTag = "thinking" by default
var thinkEnd = $"</{ThinkTag}>";

if (isInsideThinkTag) {
    var endIndex = text.IndexOf(thinkEnd);
    if (endIndex != -1) {
        isInsideThinkTag = false;
        processedText = text.Substring(endIndex + thinkEnd.Length);
    }
    else { continue; }
}
else {
    var startIndex = text.IndexOf(thinkStart);
    if (startIndex != -1) {
        // ... extract think-content + post-think content
    }
}
```

The pipeline strips `<thinking>...</thinking>` content from the TTS-bound stream. The avatar does not *say* the thinking. The thinking is logged separately and may surface in a chat-window UI for debugging, but it does not reach Rödd.

This is the right pattern for Ember. Anthropic's extended-thinking outputs (and Claude-style `<thinking>` tags more broadly) should not be spoken. The content processor strips them; Hugarsýn announces *"the agent thought before responding"* without surfacing the contents to embodiment.

Adopt this pattern wholesale. The shape is small (~30 lines), Apache-2.0 licensed, exactly what Ember needs.

## 9. The latency budget

Pipeline latency, end-to-end, at T2:

| Stage | Typical latency | Failure latency |
|---|---|---|
| Mic capture (200ms speech) | 200ms | n/a |
| VAD silence detect (0.4s) | 400ms | up to 2s if mis-tuned |
| STT (cloud, streaming) | 300-800ms after silence | 2-5s if non-streaming |
| Dialog routing | <10ms | n/a |
| LLM first token (cloud) | 400-1200ms | 5s+ on slow provider |
| First sentence emerges from splitter | ~100ms after first token | n/a |
| TTS first audio (cloud, streaming) | 200-500ms after first sentence | 1-2s non-streaming |
| Audio plays | n/a (real-time) | n/a |

End-to-end first-utterance-to-first-audible-response: roughly **1.5–3 seconds** at T2 with cloud providers. With careful provider selection and streaming-everywhere, well under 2 seconds is achievable. CDK's parallelisation makes this realistic; SAP achieves similar; Waifu's vendor pipeline can sometimes do sub-second but charges per session.

The latency budget is *not* a Vow but a Hugarsýn-projected observable:

```
GET /hugarsýn/pipeline/latency
{
  "last_turn_ms": {
    "stt": 432,
    "llm_first_token": 891,
    "tts_first_audio": 312,
    "total_first_response": 1635
  },
  "rolling_p50_ms": 1820,
  "rolling_p95_ms": 3200
}
```

Operators watching this can tune their provider mix.

## 10. The provider-swap discipline

CDK's pipeline-stage providers are pluggable but *not interchangeable mid-session*. A swap (e.g. STT provider failure → fallback) requires restarting the stage's MonoBehaviour. The pipeline cannot hot-swap mid-utterance.

Ember should adopt a more disciplined swap model:

- **Per-turn swap allowed**: between turns, the pipeline can switch providers based on health or context.
- **Mid-turn swap forbidden**: within a single turn, the active provider is the active provider; failure mid-turn ends the turn gracefully and the next turn starts fresh.
- **Provider fallback chain published**: `~/.ember/pipeline.yaml` declares `stt: [openai-whisper, azure, silero-local]`. The pipeline tries in order on each turn-start.
- **Hugarsýn projects the active providers**: per §5 schema. Every party peer sees which providers are in use.

The discipline prevents the "Ember sounded different mid-sentence" failure mode (TTS provider swap mid-utterance changing the voice timbre — a known SAP-class issue when MOSS fails and falls back).

## 11. Cross-References

- `[[60_TRIANGULATION]]` — the three-corpus matrix; CDK is the corpus that named the pipeline
- `[[61_ANDLIT_UNITY_TIER]]` — the embodiment terminal stages run through the Andlit adapter
- `[[64_FUNCTION_CALLING_FOR_EMBODIED]]` — the LLM stage's tool-call branch
- `[[65_MEMORY_INTEGRATION]]` — the Strengr stage reaches Brunnr for retrieval before the LLM call
- `[[sap:61_NEW_VOWS]]` — the Vow lattice this pipeline must satisfy
- `[[waifu:60_REALTIME_TIER_FOR_ANDLIT]]` — the canonical action vocabulary that feeds the embodiment stages
- `[[chatdoll:11_AIAVATAR_DOMAIN]]` — Architect's deep dive on `AIAvatar.cs` as orchestrator
- `[[chatdoll:13_DIALOG_PROCESSOR_DOMAIN]]` — DialogProcessor stage detail
- `[[chatdoll:14_SPEECH_LISTENER_DOMAIN]]` — STT stage detail (multi-provider)
- `[[chatdoll:15_SPEECH_SYNTHESIZER_DOMAIN]]` — TTS stage detail (10+ providers)
- `[[chatdoll:25_ANIMATION_TAG_PROTOCOL]]` — the `[anim:]`/`[face:]` tag protocol used in stage 7
- `[[chatdoll:24_VAD_INTERFACE]]` — Silero VAD detail
- `[[chatdoll:35_LIP_SYNC]]` — uLipSync detail
- `[[chatdoll:37_BARGE_IN_INTERRUPT]]` — the interruption protocol
- `[[chatdoll:53_MULTI_LLM_CONSISTENCY]]` — the multi-provider consistency story

## What This Means for Ember

**Adopt:**

- **The named-pipeline pattern itself.** Ember's runtime has a multimodal pipeline; document it as a *named* artifact with stages, sync points, and a Hugarsýn projection. Not a code adoption but a *structural* adoption.
- **CDK's streaming-everywhere shape** (`LLMContentProcessor.cs:30-100`). Sentence-by-sentence emission as the LLM streams; TTS begins on sentence 1 while LLM generates sentence 2. Adopt the pattern; reimplement against Ember's Python/Strengr architecture.
- **CDK's `<thinking>` tag stripping** (`LLMContentProcessor.cs:79-108`). About 30 lines. Apache-2.0; vendor with attribution. The pattern is exactly the right shape for handling extended-thinking outputs. *Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*
- **CDK's MicrophoneMuteStrategy enum** (`AIAvatar.cs:54-62`) — five distinct strategies for handling the mic during Ember's speech. Adopt the enum; the operator selects per-deployment in `~/.ember/pipeline.yaml`.

**Adapt:**

- **The seven-stage taxonomy** (§1) as Ember's canonical pipeline structure. Each stage is a True Name's responsibility (Mic+VAD+STT → Rödd-intake; Dialog → Munnr; LLM+content-processing → Strengr; TTS → Rödd-output; animation+face+lipsync → Andlit). The taxonomy maps cleanly onto the Six True Names + reservations.
- **CDK's per-provider abstraction at each stage** (`SpeechListenerBase`, `SpeechSynthesizerBase`, `LLMServiceBase`). Adapt the *shape* — interface with concrete implementations per provider — into Ember's Python code. The C# code does not vendor; the pattern does.
- **The interruption protocol from §4** — adapt to Ember's pipeline. Five steps: detect, recognize, cancel, flush, process. The Embodied Honesty Vow requires the flush step to return to a transition pose, not freeze on the interrupted state.
- **The canonical-verb dispatcher insertion** (§3.1). New stage between `LLMContentProcessor` and the embodiment terminals. The LLM emits canonical verbs; the dispatcher consults Hugarsýn for honesty; the adapter renders. This is a substantive structural change from CDK's pattern, motivated by Embodied Honesty.

**Avoid:**

- **All-or-nothing pipeline failure.** CDK degrades cleanly per stage; Ember must too. A failed STT does not crash the pipeline; it surfaces a typed event and the operator types instead.
- **Mid-turn provider swap.** Mid-utterance provider changes produce auditory or visual jarring. Per-turn swap is the discipline.
- **Inline `<thinking>` content reaching TTS.** The processor must strip. The avatar must not vocalize internal reasoning.
- **LLM-emitted face/animation tags as the only source of truth for the embodiment surface.** Embodied Honesty forbids this; the canonical-verb dispatcher must mediate.
- **Cloud reach without session-context.** Per `[[waifu]]`'s Cloud as Named Context refinement, the pipeline's cloud stages refuse to reach without a named session context.
- **Silent provider failure.** Every stage announces its failure to Hugarsýn. The operator reads `pipeline.last_failure` and knows which stage degraded.

**Invent:**

- **The pipeline-as-named-artifact pattern.** Ember publishes a `docs/pipeline_specification.md` enumerating the stages, sync points, latency budgets, failure modes, and Hugarsýn projections. The pipeline is a *first-class artifact*, like the slice plan. Updates are ADR-tracked.
- **The CanonicalVerbDispatcher stage** (§3.1) as a structural insertion between LLM-content-processing and embodiment terminals. The dispatcher reads Hugarsýn for state-honesty, substitutes per the canonical vocabulary's fallback cascade, and emits to the adapter. *This is the load-bearing structural finding of this doc.*
- **Hugarsýn projection of pipeline state at 5s intervals** with the schema in §5. Every operator and every party peer can introspect the pipeline. The pipeline is observable; the pipeline is honest about itself.
- **The pipeline-latency-budget projection** (§9). Operators tune their provider mix against rolling P50/P95.
- **The provider-swap discipline** (§10): per-turn swap allowed, mid-turn swap forbidden, fallback chain in `~/.ember/pipeline.yaml`, providers visible in Hugarsýn. Prevents auditory/visual jarring while permitting health-based switching.
- **The session-context tag on each pipeline turn.** Every turn carries a `session.context` string (`livestream-twitch-volmarr`, `private-journal`, `commute-conversation`, `coding-session`). The context propagates to all cloud-reach stages; the context is the unit of `Cloud as Named Context` enforcement.
- **The pipeline-failure-degradation matrix** (§6) as a typed catalog. Each failure has a default degradation; the operator can override per-deployment. The catalog ships as `docs/pipeline_failures.yaml` and is part of the pipeline specification.
- **The pipeline's *honest interruption* clause.** When barge-in flushes mid-utterance, the face transitions to a named `interrupted` verb (not freeze, not silent). The Embodied Honesty Vow's clause for interruption: *the interruption is visible; the previous state is announced as cancelled; the new state begins from a clean transition*.

---

*Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

Seven stages, eight sync points, ten failure modes, one orchestrator. The knot at the centre is the agent. The wires arrive and leave continuously. The knot stays loose because each wire is named, observable, swappable, and honest about itself. That is the pipeline pattern. That is what CDK named and what Ember inherits.

---
codex_id: 39_AIAVATARKIT_STREAMING
title: AIAvatarKit Streaming — The S2S Pipeline Behind CDK's Streaming Mode
role: Forge-B
layer: Execution
status: draft
chatdoll_source_refs:
  - /tmp/ChatdollKit/Scripts/LLM/AIAvatarKit/AIAvatarKitService.cs:75-310 (Unity client)
  - /tmp/ChatdollKit/Scripts/LLM/AIAvatarKit/AIAvatarKitServiceWebGL.cs:35-200 (WebGL flavor)
sister_source_refs:
  - /tmp/aiavatarkit/aiavatar/sts/pipeline.py:33-300 (STSPipeline constructor + handlers)
  - /tmp/aiavatarkit/aiavatar/sts/pipeline.py:305-548 (invoke + streaming generator)
  - /tmp/aiavatarkit/aiavatar/adapter/stt/server.py:1-200 (WebSocket STT server)
  - /tmp/aiavatarkit/aiavatar/adapter/websocket/server.py (S2S WS server)
  - /tmp/aiavatarkit/aiavatar/sts/vad/silero.py + vad/stream.py (Silero VAD variants)
ember_subsystem_targets: [Rödd, Munnr]
cross_refs:
  - 10_domain/14_SPEECH_LISTENER_DOMAIN
  - 10_domain/16_LLM_SERVICE_DOMAIN
  - 20_interface/23_STT_INTERFACE
  - 20_interface/24_VAD_INTERFACE
  - 60_synthesis/63_MULTIMODAL_PIPELINE
  - sap:25_STT_DOMAIN
  - waifu:21_LIVEKIT_INTEGRATION
---

# AIAvatarKit Streaming

> *Streaming STT, streaming LLM, streaming TTS, and a transaction-id that gets overwritten when the user starts talking again. AIAvatarKit is what happens when uezo refuses to let the avatar wait for the user to finish — and what CDK leans on when its own STT pipeline isn't enough.*

Forge. Eldra-iron. The CDK Unity scene can use AIAvatarKit as **both** a streaming LLM service (`Scripts/LLM/AIAvatarKit/`) **and** a streaming STT service (server-side, via `aiavatar/adapter/stt/server.py`). In both cases, AIAvatarKit is the Python sister-project that does the heavy lifting outside the Unity process. This document maps how the two halves connect, why streaming changes everything about the dialog state machine, and what Ember should learn before Rödd gets built.

The clone: `https://github.com/uezo/aiavatarkit` at `/tmp/aiavatarkit/`. The repository is **larger and more layered than chatmemory** — 8 STS subpackages (vad/stt/llm/tts/voice_recorder/performance_recorder/session_state_manager/quick_responder) and 8 adapter targets (http/websocket/local/linebot/twilio/stt/channel_context_bridge/client).

## The STSPipeline Spine

`STSPipeline` (`/tmp/aiavatarkit/aiavatar/sts/pipeline.py:33-548`) is the master orchestrator. Its constructor (lines 34-75) takes **40+ parameters** — every component is injectable, every threshold is tunable. Defaults wire to:

- **VAD:** `SileroSpeechDetector` (line 105), `volume_db_threshold=-90.0`, `silence_duration_threshold=0.5s`
- **STT:** `GoogleSpeechRecognizer` (line 16)
- **LLM:** `ChatGPTService` (line 18), default model `gpt-4o-mini`
- **TTS:** `VoicevoxSpeechSynthesizer` (line 21) at `http://127.0.0.1:50021` — Japanese voice by default
- **Session state:** PostgreSQL if a pg connection string is provided, SQLite otherwise (`pipeline.py:83-102`)
- **Performance recorder:** SQLite default

The pipeline is a **builder, not a singleton**. You instantiate one per server, register handlers, and call `invoke(STSRequest)` per turn. The handlers (`_on_accepted_handlers`, `_on_before_llm_handlers`, `_on_before_tts_handlers`, etc.) let downstream code hook the pipeline without subclassing it.

The single most important architectural fact: **VAD owns the speech-detection callback**, and the callback bridges into the pipeline:

```python
# /tmp/aiavatarkit/aiavatar/sts/pipeline.py:112-130
@self.vad.on_speech_detected
async def on_speech_detected(data: bytes, text: str, metadata: dict,
                             recorded_duration: float, session_id: str):
    async for response in self.invoke(STSRequest(
        session_id=session_id,
        user_id=self.vad.get_session_data(session_id, "user_id"),
        context_id=self.vad.get_session_data(session_id, "context_id"),
        channel=self.vad.get_session_data(session_id, "channel"),
        text=text,
        audio_data=data,
        audio_duration=recorded_duration,
    )):
        ...
```

VAD detects end-of-speech → `on_speech_detected` fires → pipeline.invoke() spins up an async generator → response chunks stream out. The VAD is the **clock** of the whole pipeline. Without it, you're back to push-to-talk.

## The Transaction-ID Overwrite Pattern

The cleverest piece of AIAvatarKit is how it handles **barge-in** (user speaks while the AI is still speaking). Inside `_invoke_direct()` (`pipeline.py:313-548`):

1. Generate a new `transaction_id = str(uuid4())` for this turn (line 320).
2. `await self.session_state_manager.update_transaction(session_id, transaction_id, ...)` (line 436) — atomically write the new transaction id as the **active** one for this session, overwriting any prior.
3. Begin streaming the LLM response.
4. **Inside the streaming loop**, every chunk:

```python
# /tmp/aiavatarkit/aiavatar/sts/pipeline.py:492-499
async for llm_stream_chunk in llm_stream:
    is_txn_active, active_txn = await self.is_transaction_active(
        request.session_id, transaction_id)
    if not is_txn_active:
        # Break when new transaction started in this session
        logger.info(f"Break llm_stream for new transaction: {active_txn} ...")
        break
```

When the user speaks again, the new turn writes a *new* transaction id. The in-flight loop sees its own transaction id is no longer active, breaks out, and stops feeding chunks. The TTS that was already mid-synthesis is canceled (`stop_response()` at line 446). The avatar shuts up; the new turn begins.

This is **cooperative cancellation through shared state** — no `CancellationToken`, no thread interrupt. The current turn polls "am I still the live one?" between every LLM chunk and bows out when it isn't. Elegant in async Python; would be painful to retrofit into sync code.

## The Merge-Request Window

If the user starts a new turn within `merge_request_threshold` seconds of the previous one, AIAvatarKit **merges** the two:

```python
# /tmp/aiavatarkit/aiavatar/sts/pipeline.py:399-410
if self.merge_request_threshold > 0 and request.allow_merge:
    if state.previous_request_timestamp:
        requests_interval = (now - state.previous_request_timestamp).total_seconds()
        if self.merge_request_threshold > requests_interval:
            logger.info(f"Merge consecutive requests: ...")
            previous_request_text = (state.previous_request_text or "").replace(
                self.merge_request_prefix, "")
            request.text = f"{self.merge_request_prefix}{previous_request_text}\n{request.text}"
            request.files = request.files or state.previous_request_files
    await self.session_state_manager.update_previous_request(...)
```

The merged text is prefixed with `merge_request_prefix` (default English: `"$Previous user's request and your response have been canceled. Please respond again to the following request:\n\n"`). The LLM sees both turns and is *told* the previous response was canceled.

The combination of transaction-id-overwrite + merge-request-window is the pattern that makes streaming speech feel responsive. CDK's own [[37_BARGE_IN_INTERRUPT]] (Forge-A's territory) covers the Unity-side reaction; AIAvatarKit is what supplies the upstream stream-cancel signal.

## The Quick-Response Pre-LLM Hook

`_on_before_llm_handlers` (lines 459-461) lets a handler set `request.quick_response_text` *before* the LLM call. If set, a chunk is yielded immediately:

```python
# /tmp/aiavatarkit/aiavatar/sts/pipeline.py:464-476
if request.quick_response_text:
    yield STSResponse(
        type="chunk",
        session_id=request.session_id,
        ...
        text=request.quick_response_text,
        voice_text=request.quick_response_voice_text,
        audio_data=request.quick_response_audio,
        metadata={"is_quick_response": True, "is_first_chunk": True}
    )
```

The avatar can say "um, let me think..." while the LLM is still composing the real answer. This is **filler-as-latency-hider**. The `aiavatar/sts/quick_responder/` subpackage has the canned responses; the handler picks one based on the request text or context.

CDK does not have this in its own LLM services; it's a feature you get when you use AIAvatarKit as the LLM backend (`AIAvatarKitService.cs:75-280`).

## The Streaming STT Server

Separately, AIAvatarKit ships a WebSocket-based streaming STT server at `/tmp/aiavatarkit/aiavatar/adapter/stt/server.py`. CDK's `SpeechListener` can connect to it for **partial transcription results** while the user is still speaking:

```python
# /tmp/aiavatarkit/aiavatar/adapter/stt/server.py:84-94
if self._is_stream_vad:
    @self.vad.on_speech_detecting
    async def on_speech_detecting(text: str, session):
        session_id = session.session_id
        if session_id in self.websockets:
            await self._send_response(STTResponse(
                type="partial",
                session_id=session_id,
                text=text,
                is_final=False
            ))
```

The `SileroStreamSpeechDetector` (`aiavatar/sts/vad/stream.py`) emits partial transcriptions as the user speaks. The WS server pushes `{type:"partial",text:"...",is_final:false}` to the connected Unity client. When the user finishes, a `{type:"final",is_final:true}` arrives.

Compare with [[sap:25_STT_DOMAIN]] where SAP's `sherpa_asr.py` runs k2-sherpa fully on-device but only emits final transcriptions. AIAvatarKit's partial-emit is the streaming pattern; sherpa's batch-emit is the local pattern. Ember will want both axes available.

## The Unity-Side AIAvatarKitService

Now the CDK side. `/tmp/ChatdollKit/Scripts/LLM/AIAvatarKit/AIAvatarKitService.cs:75-310` is the Unity client. The streaming download is the interesting bit:

```csharp
// /tmp/ChatdollKit/Scripts/LLM/AIAvatarKit/AIAvatarKitService.cs:185-201
var downloadHandler = new AIAvatarKitStreamDownloadHandler();
downloadHandler.DebugMode = DebugMode;
downloadHandler.SetReceivedChunk = (text, contextId, error) =>
{
    aakSession.CurrentStreamBuffer += text;
    aakSession.StreamBuffer += text;
    if (!string.IsNullOrEmpty(contextId))
    {
        aakSession.ContextId = contextId;
    }
    if (!string.IsNullOrEmpty(error))
    {
        aakSession.ResponseType = ResponseType.Error;
        Debug.LogError(error);
    }
};
```

`AIAvatarKitStreamDownloadHandler` is a custom `DownloadHandlerScript` that parses Server-Sent-Events-like chunks as they arrive and invokes `SetReceivedChunk` per chunk. The Unity-side does not poll a queue — UnityWebRequest pushes into the handler from the network thread.

The session carries `ContextId` (`AIAvatarKitService.cs:32-38`) which is AIAvatarKit's persistent conversation key. CDK does **not** own this id; the server issues it on first turn and the client carries it on subsequent turns. The `contextTimeout` field (used in `GetContextId()` at line 30-38) lets the Unity client decide locally to clear context after N seconds of idle, which silently restarts the server-side conversation.

## The WebGL-Specific Path

`AIAvatarKitServiceWebGL.cs:35-200` is the WebGL-only variant. Unity's WebGL build cannot use `UnityWebRequest` streaming reliably because of Emscripten/browser threading limitations — so CDK uses a **JavaScript bridge** instead:

```csharp
// /tmp/ChatdollKit/Scripts/LLM/AIAvatarKit/AIAvatarKitServiceWebGL.cs:27-30
[DllImport("__Internal")]
protected static extern void StartAIAvatarKitMessageStreamJS(
    string targetObjectName, string sessionId, string url,
    string chatCompletionRequest, string aakHeaders);
[DllImport("__Internal")]
protected static extern void AbortAIAvatarKitMessageStreamJS();
```

The JS plugin (`Plugins/AIAvatarKitServiceWebGL.jslib`) opens an EventSource/fetch-streaming request and calls back into Unity via `SendMessage(gameObject.name, "MethodName", payload)`. The session state is held in `sessions: Dictionary<string, AIAvatarKitSession>` keyed by a JS-side session id.

```csharp
// /tmp/ChatdollKit/Scripts/LLM/AIAvatarKit/AIAvatarKitServiceWebGL.cs:81-91
// TODO: Support custom headers later...
if (customHeaders.Count > 0)
{
    Debug.LogWarning("Custom headers for AIAvatarKit on WebGL is not supported for now.");
}
```

Custom headers are a known limitation. Browser fetch-streaming with custom headers requires CORS preflight; if the AIAvatarKit server isn't configured for it, the request fails. CDK punts.

The relevance for Ember: **WebGL streaming requires JS plugins**. Native Unity streaming APIs don't translate. See [[3B_WEBGL_BUILD]] for the broader implications.

## The Session State Manager

`SessionStateManager` (`aiavatar/sts/session_state_manager/`) is the cross-turn persistence. Two impls: SQLite and PostgreSQL. The fields it persists (inferred from usage in `pipeline.py:436-440`):

- `active_transaction_id` — current live transaction
- `previous_request_timestamp` / `previous_request_text` / `previous_request_files` — for merge-window detection
- `timestamp_inserted_at` — last time the pipeline auto-inserted a timestamp into the prompt

The state is **per-session**, not per-user. Multiple sessions per user are possible; barge-in only cancels within the same session.

For Ember's Rödd, this maps onto a small session-state store that lives next to Hjarta but is conceptually separate — Hjarta is for cross-session memory, the state manager is for in-session coherence.

## Where It Breaks

- **No backpressure between LLM chunks and TTS synthesis.** Inside `synthesize_stream()` (line 489), `audio_chunk = await self.tts.synthesize(...)` blocks per chunk. A slow TTS provider stalls the whole pipeline. There's no parallel-prefetch like CDK's [[33_TTS_PREFETCH]]. AIAvatarKit relies on VoiceVox being local-and-fast.
- **The transaction-id pattern requires `session_state_manager` to be transactional** for the cancel signal to be timely. SQLite `update_transaction()` is best-effort if multiple async tasks contend; PostgreSQL with `FOR UPDATE` is needed for true correctness. The default config doesn't enforce this.
- **The merge-request prefix is locale-specific.** Default English text gets injected into the prompt; multilingual deployments need to override. The Japanese alternative is commented in the source (line 57) but uncommitted as code-path.
- **The `timestamp_interval_seconds` injection** (line 426-431) silently rewrites the user's request text by prepending the current time. The LLM sees a different request than what the user said. If you're logging requests for debugging, this is confusing.
- **WebGL custom-header limitation** is unaddressed since the project's start (`TODO: Support custom headers later...`). Production deployments needing auth headers on WebGL hit this wall.
- **`StreamBuffer += text;` (line 189) is unbounded.** Long responses accumulate in memory until the session ends. For a 10-minute monologue at 100 tokens/sec, that's measurable.
- **The `ResponseType.Timeout` branch** (line 222) aborts but doesn't surface a structured error to the avatar layer — just `Debug.LogWarning`. The avatar continues silent.
- **No client-side reconnect.** If the WebSocket drops mid-streaming, the Unity client receives a `Result.ConnectionError` and gives up. No exponential-backoff retry.
- **`requirements.txt` pulls in heavyweight deps** — OpenAI SDK, websockets, fastapi, sqlalchemy variants, multiple STT/TTS provider SDKs. The full install is 200+ MB. Optional-deps are not cleanly separated.

## Where It Surprises

- **The transaction-id-overwrite cancel-via-shared-state** pattern. Async cooperative cancellation done right. Compare with `CancellationToken` chains in CDK Unity which can be brittle when nested.
- **Quick-response filler** as a first-class pipeline event with `is_first_chunk: True` metadata. The Unity client knows the first chunk is filler and can choose to display it differently.
- **The 40-parameter constructor** as documentation. Reading the constructor tells you the entire interface contract. No hidden state.
- **`use_invoke_queue` mode** (line 71, used by `_invoke_queued` at line 305-310) lets a deployment serialize all invocations through a queue with idle-timeout. For low-resource deployments where parallel LLM calls would OOM, this is the throttle.
- **The `insert_channel_tag` parameter** (line 72) wraps the recognized text in `<channel name='...' />` before the LLM sees it. Cross-platform conversational context with one parameter.
- **The SilenceStreamSpeechDetector emits partial transcriptions** — and the WebSocket server forwards them. The avatar can react (start the LLM warming up, show lip-twitch animation) before the user even finishes speaking. This is the deepest streaming pattern in any embodiment codex.
- **`voice_recorder` and `performance_recorder` are first-class injectable subsystems.** Every turn records the request voice, the response voice, and a performance record (`PerformanceRecord` at line 332). The whole pipeline is observable by default.
- **Two adapter targets we didn't expect:** `linebot/` and `twilio/`. AIAvatarKit can deploy as a LINE chatbot or a phone-call agent through Twilio. The streaming core is reusable across surfaces.

## The Two-Tier Use From CDK

CDK can use AIAvatarKit in two distinct ways:

1. **As an LLM service** (`AIAvatarKitService.cs`). Replace `ChatGPTService` with `AIAvatarKitService`, point `BaseUrl` at the AIAvatarKit server's `/chat`, get streaming LLM responses. The STT happens client-side in Unity.
2. **As a full S2S pipeline** with streaming STT. The Unity client opens a WebSocket to `aiavatar/adapter/stt/server.py`, streams mic audio up, gets partial transcriptions back, and feeds final transcriptions into a separate LLM call. Or, alternately, lets the AIAvatarKit server do everything — STT + LLM + TTS — and just streams audio back.

CDK's `Scripts/LLM/AIAvatarKit/` covers mode 1. Mode 2 is operator-assembled — there's no canonical CDK code path for "use AIAvatarKit for STT too", but the WS protocol is documented in `aiavatar/adapter/stt/server.py:1-30`.

For Ember, mode 2 is the more interesting pattern. The Pi-tier Ember would run a tiny on-device VAD/STT; the workstation-tier Ember could run AIAvatarKit as a fuller streaming pipeline.

## Cross-References

- [[10_domain/14_SPEECH_LISTENER_DOMAIN]] — CDK's domain view of STT
- [[10_domain/16_LLM_SERVICE_DOMAIN]] — CDK's LLM service abstraction (AIAvatarKitService is one impl)
- [[20_interface/23_STT_INTERFACE]] — STT provider contract; AIAvatarKit streaming is one shape
- [[20_interface/24_VAD_INTERFACE]] — Silero VAD; AIAvatarKit's streaming variant pushes partials
- [[37_BARGE_IN_INTERRUPT]] (Forge-A) — Unity-side response to mid-TTS interrupt
- [[60_synthesis/63_MULTIMODAL_PIPELINE]] — synthesis of the full STT→LLM→TTS chain
- [[sap:25_STT_DOMAIN]] — SAP's on-device k2-sherpa contrasted with AIAvatarKit's streaming server
- [[waifu:21_LIVEKIT_INTEGRATION]] — Waifu's cloud-streaming alternative

## What This Means for Ember

*Apache-2.0 attribution: ChatdollKit and aiavatarkit are both Apache-2.0. Preserve upstream header references per Apache-2.0 §4(c).*

**Adopt:**

- **The transaction-id-overwrite barge-in cancel.** Implementation pattern: `state.active_transaction_id` is written atomically on new turn; in-flight streams poll between chunks and self-cancel. Adopt into Rödd's session-state store. Provides cooperative cancel without `CancellationToken` plumbing.
- **The quick-response pre-LLM hook** (`_on_before_llm_handlers` shape). Latency-hiding filler is a first-class output, not a bolt-on. Adopt as Rödd's `quick_response` event type with `is_first_chunk=True` metadata.
- **The performance-recorder injection.** Every turn emits a `PerformanceRecord` (request voice, STT time, LLM first-chunk time, TTS first-chunk time, total time). Adopt as Rödd's required observability surface — no Rödd build ships without this.
- **The voice-recorder.** Every request/response audio archived for replay/debug. Adopt with consent-gating per [[ember:reference_ember_true_names]] Hjarta-scope.
- **The `merge_request_threshold` window.** When the user re-speaks within N seconds of the prior turn, merge the prompts and tell the LLM. Adopt; expose `merge_request_threshold` as a Rödd config knob.
- **The dual-VAD interface (batch + stream).** `SpeechDetector` interface with `SileroSpeechDetector` (batch) and `SileroStreamSpeechDetector` (partials) as siblings. Adopt; Ember's VAD interface should accommodate both shapes from day one.
- **The session-state-manager + Postgres/SQLite dual-backend.** Same code, two stores, switch by connection string. Adopt; matches Vow of Pluggable Storage.

**Adapt:**

- **The 40-parameter constructor** — adapt into Ember's typed-config pattern. `STSPipelineConfig` dataclass loaded from `data/charts/rodd_pipeline.yaml`, no Python kwargs sprawl.
- **The `merge_request_prefix` locale text** — adapt to load from `data/charts/rodd_prompts.yaml` keyed by language. CDK's hardcoded English is anti-Vow.
- **The `timestamp_interval_seconds` silent prompt rewrite** — adapt to surface the injected timestamp in the audit trail. The LLM seeing a different request than the user said must be visible to the operator.
- **The unbounded `StreamBuffer`** — adapt with a circular buffer + rotated-to-disk archive. 10-minute monologues should not blow memory.
- **The OpenAI-only LLM client in the default `ChatGPTService`** — adapt to use Ember's existing LLM service abstraction. AIAvatarKit's `LLMService` interface is good; the default impl is too narrow.
- **The WebGL custom-header limitation** — adapt by routing all WebGL builds through a tiny proxy that adds auth headers server-side. The user's browser never sees the auth token.
- **The `use_invoke_queue` throttle** — adapt as the default for Pi-tier Ember. Workstation-tier can disable.

**Avoid:**

- **The TTS-in-the-streaming-loop blocking call** (`pipeline.py:537-541`). Ember's Rödd must do parallel TTS prefetch per [[33_TTS_PREFETCH]] (Forge-A) — chunks queued, synthesized in parallel, played sequentially.
- **The silent timeout swallow.** When `ResponseType.Timeout` happens, Ember surfaces a structured error to the avatar and a log entry, not a `Debug.LogWarning`.
- **Hardcoded VoiceVox default at `127.0.0.1:50021`** — Ember does not assume VoiceVox is installed locally. Default TTS is a no-op silence-emitter; user explicitly configures the provider.
- **No client-side reconnect on WebSocket drop.** Ember's WS clients must reconnect with exponential backoff and merge pending state on reconnect.
- **Optional deps bundled into the main `requirements.txt`.** Ember splits into `core`, `provider-openai`, `provider-azure`, `provider-voicevox`, `stt-google`, etc. Install only what's used.

**Invent:**

- **Rödd Transaction-Receipt Stream.** AIAvatarKit emits per-chunk `STSResponse` objects. Ember emits per-chunk `RoddReceipt(transaction_id, chunk_index, llm_prompt_hash, vad_partial_text, tts_audio_sha, timing_ms)`. The receipt stream is parallel to the audio stream and lets Ember reconstruct any past turn deterministically. Vow tie-in: **Defended Builds** generalized to **Defended Turns**.
- **Two-Phase Quick-Response.** AIAvatarKit's quick response is text-only by default. Ember's two-phase: **phase-1** = `[anim:thinking][face:Focus]` (animation-only, zero TTS latency); **phase-2** = canned-voice filler ("um, let me see..."). The animation fires within 100 ms; the voice within 300 ms if needed. The full LLM response can take 2 seconds and the user perceives the response as immediate. Vow tie-in: **Smallness** (avatar reaction can be cheaper than speech).
- **Cross-Channel Streaming Bridge.** AIAvatarKit's `insert_channel_tag` is one direction: tell the LLM the channel. Invert: the LLM emits `<switch_channel name='...' />` to **route its response** to a different channel. The user spoke on Discord; Ember answers on Discord *and* the Unity scene mirrors silently. Vow tie-in: **Federated Self**, **Munnr Reach**.
- **Streaming-VAD Confidence Channel.** AIAvatarKit's `voice_probability` lives only in the JS-side mic (per [[3B_WEBGL_BUILD]]). Ember exposes the confidence per-chunk to the avatar so eyebrows can raise as confidence drops below 0.5 — the avatar visibly "leans in" when the mic is unsure. Vow tie-in: **Mythic Living** (UI affordances that show the system's state through embodied gesture, not text overlays).
- **Tier-Aware Pipeline Composition.** AIAvatarKit's components are uniformly injectable; Ember exposes a `pipeline_tier` config: `pi` = local VAD + cloud STT + cloud LLM + cloud TTS; `workstation` = streaming VAD + streaming STT-server + local Ollama + local TTS; `mythic` = all-local including a small local LLM. Switching tiers is one config edit. Vow tie-in: **Tiered Presence**.
- **Audit-Traced Merge.** When `merge_request_threshold` fires, Ember writes an audit row: `(timestamp, original_user_text, merged_text, prefix_used)`. The merged prompt is not a silent rewrite; it's a documented one. Vow tie-in: **Defended Memory**.

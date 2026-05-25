---
codex_id: 16_LLM_SERVICE_DOMAIN
title: LLM Service Domain — One Interface, Five Vendors, Five Wire Formats
role: Architect
layer: Domain
status: draft
chatdoll_source_refs:
  - Scripts/LLM/ILLMService.cs:1-58
  - Scripts/LLM/LLMServiceBase.cs:1-175
  - Scripts/LLM/LLMContentProcessor.cs:1-271
  - Scripts/LLM/ChatGPT/ChatGPTService.cs:1-661
  - Scripts/LLM/Claude/ClaudeService.cs:1-565
  - Scripts/LLM/Gemini/GeminiService.cs:1-616
  - Scripts/LLM/Dify/DifyService.cs:1-405
  - Scripts/LLM/AIAvatarKit/AIAvatarKitService.cs:1-448
  - Scripts/LLM/ChatGPT/ChatGPTServiceWebGL.cs:1-341
  - Scripts/Dialog/DialogProcessor.cs:81-280
ember_subsystem_targets: [Smiðja, Hugarsýn, Munnr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/13_DIALOG_PROCESSOR_DOMAIN
  - 10_domain/19_TOOL_DOMAIN
  - 20_interface/20_LLM_SERVICE_INTERFACE
  - 20_interface/26_TOOL_FUNCTION_CALL_INTERFACE
  - sap:21_OPENAI_COMPAT_API
  - waifu:21_LIVEKIT_INTEGRATION
---

# LLM Service Domain
## One Interface, Five Vendors, Five Wire Formats

*— Rúnhild Svartdóttir, Architect*

> *The lie every LLM SDK tells is that the providers are interchangeable. ChatdollKit knows they are not, builds an interface that exposes the difference rather than hides it, and pays the cost of five concrete adapters rather than the cost of one leaky abstraction. This is the right trade.*

`Scripts/LLM/` is the *cognition* of the avatar. Twenty-three files, roughly **5,300 LOC** — by far the largest subsystem and the only one that handles network protocols other than `SocketServer`. It is organised into a tiny shared surface (`ILLMService` 58 lines, `LLMServiceBase` 175 lines, `LLMContentProcessor` 271 lines, `ITool` + `ToolBase` 26+46 lines) and **five provider directories**, each with a `<Vendor>Service.cs` (300-660 LOC) and a `<Vendor>ServiceWebGL.cs` (270-340 LOC) variant.

The domain's central architectural claim — articulated in code, not in docs — is that *LLM providers cannot be unified at the wire-format level, so the unification happens at the contract level*. Each `*Service.cs` is a full per-vendor adapter that handles streaming, function-calling, multimodal payloads, context-history shape, and tool-call recursion. The cost is 5,300 LOC. The benefit is that swapping ChatGPT for Claude is a single checkbox in the Inspector, and the dialog pipeline above the interface never knows the difference.

Compare SAP, which simulates OpenAI's API over Claude/Gemini at the *wire* level ([[sap:21_OPENAI_COMPAT_API]]) — fragile, leaky, and tied to whatever OpenAI does next. Compare Waifu, which has *one* cloud LLM hidden behind ZeroWeight and no ability to see in. CDK has five real adapters and the right abstraction floor.

---

## 1. The Subject Itself

**What the domain is:** the layer between *"a user said something"* and *"a stream of text+tags is arriving."* Inputs: text, optional image bytes, conversation history, tool specifications. Outputs: a streaming `ILLMSession` carrying a `StreamBuffer` that fills incrementally, plus typed signals for `FunctionCall`, `Error`, and `Timeout`.

**What it owns:**

| Layer | Files | LOC | Owns |
|---|---|---|---|
| **Interface** | `ILLMService.cs` | 58 | The typed contract: `MakePromptAsync`, `GenerateContentAsync`, `Tools`, context, vision-capture hook, extracted-tags handler, streaming-end callback |
| **Base** | `LLMServiceBase.cs` | 175 | Context-history list + 10-minute idle timeout, `[key:value]` tag regex extraction, `IsEnabled` toggling with `OnEnabled` event, the `Tools` list-holder |
| **Content processor** | `LLMContentProcessor.cs` | 271 | The *streaming consumer* — sentence-splitting (`SplitChars` + `OptionalSplitChars`), `<thinking>` tag stripping, `[lang:]` extraction, parallel parse + dequeue loops |
| **Per-provider, native** | `ChatGPT/ChatGPTService.cs`, `Claude/ClaudeService.cs`, `Gemini/GeminiService.cs`, `Dify/DifyService.cs`, `AIAvatarKit/AIAvatarKitService.cs` | 661/565/616/405/448 | Wire-format adapter: per-vendor message shape, streaming protocol, function-call format, multimodal payload format, error recovery |
| **Per-provider, WebGL** | `*ServiceWebGL.cs` | 270-340 each | WebGL-specific reimplementation routing through `fetch` API rather than `UnityWebRequest` (which has limited streaming support in WebGL) |
| **Tool surface** | `ITool.cs`, `ToolBase.cs` | 26/46 | Function-calling contract — `GetToolSpec` + `ExecuteAsync(argumentsJson, token)` |

**What it does NOT own:**
- The dialog state machine — that's `DialogProcessor` ([[13_DIALOG_PROCESSOR_DOMAIN]]), which *calls* this domain.
- Tool *implementations* — those are user-supplied subclasses of `ToolBase` ([[19_TOOL_DOMAIN]]).
- Animation/face tag *execution* — `LLMContentProcessor` only *parses* `[face:...]` tags; `ModelController.ToAnimatedVoiceRequest` *applies* them ([[1B_ANIMATION_DOMAIN]]).
- The audio pipeline — TTS and STT are sibling domains ([[14_SPEECH_LISTENER_DOMAIN]], [[15_SPEECH_SYNTHESIZER_DOMAIN]]).

The boundary is sharp: cognition only. Body and voice belong elsewhere.

---

## 2. How It Works

### 2.1 The `ILLMService` interface

`Scripts/LLM/ILLMService.cs:8-20` declares the contract. Eight members; nine if you count the response enum:

```csharp
public interface ILLMService
{
    bool IsEnabled { get; set; }
    Action OnEnabled { get; set; }
    List<ILLMTool> Tools { get; set; }
    List<ILLMMessage> GetContext(int count);
    void ClearContext();
    UniTask<List<ILLMMessage>> MakePromptAsync(string userId, string inputText, Dictionary<string, object> payloads, CancellationToken token = default);
    UniTask<ILLMSession> GenerateContentAsync(List<ILLMMessage> messages, Dictionary<string, object> payloads = null, bool useFunctions = true, int retryCounter = 1, CancellationToken token = default);
    Func<string, Dictionary<string, object>, ILLMSession, CancellationToken, UniTask> OnStreamingEnd { get; set; }
    Action<Dictionary<string, string>, ILLMSession> HandleExtractedTags { get; set; }
    Func<string, UniTask<byte[]>> CaptureImage { get; set; }
}

public enum ResponseType { None, Content, FunctionCalling, Error, Timeout }
```

Three things to note.

**One**, `MakePromptAsync` and `GenerateContentAsync` are *separate* phases. The first builds the message list (per-vendor; ChatGPT puts the system message in the array, Claude takes it as a top-level field, Gemini fakes it with a `user`→`model` pair). The second sends the request and starts streaming. This separation lets `DialogProcessor` (`Scripts/Dialog/DialogProcessor.cs:206-207`) inject behaviour between the two — though in practice it doesn't.

**Two**, the `payloads` parameter is `Dictionary<string, object>` — the same untyped-on-purpose pattern as the speech synthesizer's `parameters`. Inside, the convention is to wrap actual payloads under a `"RequestPayloads"` key (visible in `ChatGPTService.MakePromptAsync` at `ChatGPTService.cs:118-128`). The wrapping is to keep room for sibling keys like `CustomParameterKey` and `CustomHeaderKey` (lines 32-33 of `LLMServiceBase`) that travel alongside.

**Three**, the `CaptureImage` hook is *vision as an extension*, not a baked-in capability. The LLM streams a `[vision:source]` tag; the base class fires `CaptureImage(source)` which AIAvatar wires to `SimpleCamera.CaptureImageAsync`; the bytes are fed back into the streaming session and the LLM is re-called with the image (`ChatGPTService.cs:373-399`). Recursive re-call inside the same session; the protocol absorbs it.

### 2.2 The `LLMServiceBase` shared surface

`LLMServiceBase` (175 LOC) is the abstract parent. Three things live here.

**Context history with idle timeout** (`Scripts/LLM/LLMServiceBase.cs:56-86`):

```csharp
public virtual List<ILLMMessage> GetContext(int count) {
    if (Time.time - contextUpdatedAt > contextTimeout) {  // default 600s = 10 min
        ClearContext();
    }
    if (string.IsNullOrEmpty(contextId)) {
        contextId = Guid.NewGuid().ToString();
    }
    return context.Skip(context.Count - count).ToList();
}
```

A *time-bounded* context. After ten minutes of inactivity, history is wiped. The avatar forgets. This is a deliberate design choice: the avatar is a *companion*, not a perfect-recall stenographer, and CDK lets the user tune the forgetting interval. SAP keeps unbounded history; Waifu defers to cloud. **CDK is the only one of the three corpora with explicit memory-decay.** The mechanism is crude (cliff at 10 minutes) but the *intent* is right.

**Tag extraction regex** (lines 100-117):

```csharp
protected virtual Dictionary<string, string> ExtractTags(string text)
{
    var tagPattern = @"\[(\w+):([^\]]+)\]";
    var matches = Regex.Matches(text, tagPattern);
    var result = new Dictionary<string, string>();
    foreach (Match match in matches) {
        if (match.Groups.Count == 3) {
            result[match.Groups[1].Value] = match.Groups[2].Value;
        }
    }
    return result;
}
```

Every provider gets `[face:Joy]`, `[anim:Wave]`, `[vision:camera]` extraction *free* — the regex runs once on the completed `CurrentStreamBuffer` (called from each provider's stream-end handler, e.g. `ChatGPTService.cs:347-351`). Note: this is the *non-streaming* tag extraction. The *streaming* extraction (for `[face:Joy]` to fire mid-sentence) lives in `LLMContentProcessor` via a different regex in `Scripts/Model/ModelController.cs:247-249`. Two regexes, two purposes — the base class extracts *all* tags as a key/value bag for `HandleExtractedTags` handlers (the AIAvatar-side flag carriers); ModelController extracts *positional* tags for animation-voice splitting.

**The `IsEnabled` + `OnEnabled` pattern** (lines 13-30):

```csharp
public virtual bool IsEnabled {
    get {
#if UNITY_WEBGL && !UNITY_EDITOR
        return false;  // Native LLMService is disabled on WebGL
#else
        return _IsEnabled;
#endif
    }
    set {
        _IsEnabled = value;
        if (value == true) OnEnabled?.Invoke();
    }
}
```

Native services *unconditionally disable themselves on WebGL* — because WebGL needs a different request path (the `*ServiceWebGL.cs` variants). The native and WebGL variants of the same provider co-exist on the same GameObject; the user toggles a checkbox; only one is active per build target. This is the **dual-implementation pattern** — neither subclass nor #ifdef alone could express it as cleanly.

### 2.3 The `LLMContentProcessor` streaming consumer

`LLMContentProcessor.cs` (271 LOC) is the *downstream* half of the LLM path. The LLM provider fills `ILLMSession.StreamBuffer` chunk by chunk; this processor consumes it in parallel.

**The sentence-splitter** (lines 14-19 declares config, lines 163-203 the loop):

```csharp
public List<string> SplitChars = new List<string>() { "。", "！", "？", ". ", "!", "?" };
public List<string> OptionalSplitChars = new List<string>() { "、", ", " };
public string ThinkTag = "thinking";
public int MaxLengthBeforeOptionalSplit = 0;
```

Mandatory split chars are sentence-final punctuation in both Japanese (`。！？`) and English (`. ! ?`). Optional split chars (`、`, `, `) only trigger if the buffer is over `MaxLengthBeforeOptionalSplit` characters — preventing micro-fragmenting on short sentences. The Japanese characters come first; CDK's first-class language is Japanese.

**The `<thinking>` tag stripper** (lines 79-117). Reasoning-model providers (o1, Claude with extended thinking) emit `<thinking>...thoughts...</thinking>` blocks that the user should not see *or hear*. The processor handles three cases: tag-fully-inside-chunk (strip and continue), tag-opens-in-chunk (consume the prefix, set `isInsideThinkTag = true`), tag-closes-in-later-chunk (skip everything until close tag found). State across chunks; deterministic; tested by anyone who runs CDK with o1.

**The split-pipe-process loop** (lines 47-147). Three coroutines effectively:

1. `ProcessContentStreamAsync` (line 29) — the *parser*. Reads `StreamBuffer`, splits on the latest punctuation, enqueues `LLMContentItem` for downstream. Runs until `IsResponseDone && splitIndex == count`.
2. `ShowContentAsync` (line 229) — the *consumer*. Dequeues `LLMContentItem`s and dispatches to `ShowContentItemAsync` (which AIAvatar wires to `ModelController.AnimatedSay`).
3. The third coroutine is `ProcessContentItemAsync` (called inline in the parser at line 134-137) — the *prefetch hook*. AIAvatar wires this to `SpeechController.PrefetchVoices`, so synthesis fires as soon as a sentence is parsed, *not* when it's dequeued for playback.

This is the three-coroutine pattern that makes the parallel-prefetch latency win work. The parser produces; the prefetch hook fires per-item (concurrent); the consumer plays sequentially. Three loops on one queue, all `UniTask`-scheduled, no thread synchronisation primitives — Unity's main-thread guarantee carries it.

### 2.4 The five providers and their wire-format divergence

Here is where the cost of the abstraction shows: every provider is its own substantial file.

**ChatGPT (`ChatGPT/ChatGPTService.cs`, 661 LOC)** — OpenAI's chat-completions API with `stream: true`. Messages are an array of `{role, content}`; system message goes first. Function-calling uses `tools: [{type: "function", function: {...}}]` with `tool_calls` in the assistant reply. The largest provider because OpenAI's API has the most options (`reasoning_effort`, `logprobs`, `top_logprobs`, `frequency_penalty`, `presence_penalty`, `stop`, `tool_choice`). The downloader uses a custom `DownloadHandlerScript` (line 429) that streams `data:` SSE chunks and routes either content or tool_call deltas to setter callbacks.

**Claude (`Claude/ClaudeService.cs`, 565 LOC)** — Anthropic's messages API. System message is a *top-level field*, not in the message array (`ClaudeService.cs:152`). Function-calling uses `tools: [...]` with `tool_use` content blocks containing `input` (parsed args). The reply structure is a *list* of content blocks (`text`, `tool_use`, `image`) rather than a single content string. Tool result is a `tool_result` content block in the next user message. **The shape diverges enough that the Claude adapter and ChatGPT adapter share no message classes** — `ChatGPTUserMessage` and `ClaudeMessage` are completely separate types.

**Gemini (`Gemini/GeminiService.cs`, 616 LOC)** — Google's generative-language API. Messages are called `contents`; roles are `user` and `model` (not `assistant`). System message is faked as a `user`→`model` exchange (`GeminiService.cs:91-92`). Function-calling uses `functionDeclarations` and `functionCall`/`functionResponse` parts. The **context-history gymnastics** at lines 38-46 force the first message to be a `user` role (Gemini rejects starting with `model`). Gemini also has a quirky `thinkingConfig` (line 180) for its thinking models — `{"thinkingLevel": "minimal"}`. The most awkward provider; the abstraction has to swallow it.

**Dify (`Dify/DifyService.cs`, 405 LOC)** — Dify's chat-messages API. Stateless from CDK's side; Dify holds the conversation under a `conversation_id` (`DifyService.cs:148-151`). System prompt and tool definitions live on Dify's side; CDK just streams `query` strings. Smallest "real" provider because most of the work is upstream. The context-clearing semantics differ: `ClearContext` just nulls the conversation ID (line 47-51).

**AIAvatarKit (`AIAvatarKit/AIAvatarKitService.cs`, 448 LOC)** — sister-project broker. Similar shape to Dify (server-side state, client streams `context_id` + text). Has `ProcessLastChunkImmediately = true` (line 85) — a flag the AIAvatarKit pipeline uses for ultra-low-latency turn-final handling. The integration with the sister project is documented at [[39_AIAVATARKIT_STREAMING]] (Forge-B).

**Multiplied by two for WebGL variants.** Each provider has a `*ServiceWebGL.cs` that uses the browser's `fetch` API via a small JS bridge because `UnityWebRequest.DownloadHandlerScript`'s streaming has WebGL bugs. The WebGL variants are *not* subclasses of the native ones; they re-implement `LLMServiceBase` independently. Code duplication is real (270-340 LOC each). The honest read: CDK chose duplication over a shared streaming abstraction. For the size of the divergence, that may have been correct.

### 2.5 The provider multiplex

`DialogProcessor.SelectLLMService` (`Scripts/Dialog/DialogProcessor.cs:81-113`):

```csharp
public void SelectLLMService(ILLMService llmService = null) {
    var llmServices = gameObject.GetComponents<ILLMService>();
    if (llmService != null) {
        this.llmService = llmService;
        foreach (var llms in llmServices) llms.IsEnabled = llms == llmService;
        return;
    }
    foreach (var llms in llmServices) {
        if (llms.IsEnabled) { this.llmService = llms; return; }
    }
    Debug.LogWarning(...);
    llmServices[0].IsEnabled = true;
    this.llmService = llmServices[0];
}
```

`gameObject.GetComponents<ILLMService>()` returns every component implementing the interface on the GameObject. The first with `IsEnabled = true` wins. Defaults to the first registered if none enabled. **Five providers + five WebGL variants = ten resident components**, of which exactly one is active per turn. This is wasteful — each component runs its own `Update` even when disabled — but Unity's component-update overhead at ten registered components is negligible. The architecture wins; the resource cost loses but in a regime where it does not matter.

The five-providers pattern is *the* central architectural decision of this domain. It is not a hack; it is a deliberate choice to pay 5,300 LOC of adapter code in exchange for a uniform contract upstream. Validate the choice by counting: how many lines does `DialogProcessor` spend on LLM-specific logic? Zero. How many lines does `LLMContentProcessor` spend on it? Zero. How many lines does `AIAvatar` spend on it? Zero. The cost is concentrated in one folder and the rest of the codebase is provider-agnostic. This is the discipline of *paying the cost where it belongs*.

### 2.6 Tool execution and recursion

When the LLM emits a function call (`ChatGPTService.cs:353-372`):

```csharp
if (!string.IsNullOrEmpty(chatGPTSession.ToolCallId)) {
    foreach (var tool in gameObject.GetComponents<ITool>()) {
        var toolSpec = tool.GetToolSpec();
        if (toolSpec.name == chatGPTSession.FunctionName) {
            var toolResponse = await tool.ExecuteAsync(chatGPTSession.FunctionArguments, token);
            chatGPTSession.Contexts.Add(new ChatGPTFunctionMessage(toolResponse.Body, chatGPTSession.ToolCallId));
            // Reset to prevent infinite loop
            chatGPTSession.ToolCallId = null;
            // Recursive call with tool response
            await StartStreamingAsync(chatGPTSession, customParameters, customHeaders, false, token);
        }
    }
}
```

`gameObject.GetComponents<ITool>()` finds every registered tool. Match by name. Execute. Append result to context. **Recursive call** to `StartStreamingAsync` — the same streaming session continues with the tool result, the LLM responds with text, the cycle repeats until the LLM stops calling tools. The `useFunctions: false` argument to the recursive call masks tools to prevent infinite recursion (line 369). Crude — disabling tools means the LLM cannot chain tool calls — but defensive. The detail and per-vendor variations of function-calling are at [[26_TOOL_FUNCTION_CALL_INTERFACE]].

---

## 3. Where It Breaks and Where It Surprises

### 3.1 Five providers means five edge-case sets

ChatGPT handles `[DONE]` SSE terminators; Claude handles `event: message_stop`; Gemini emits a JSON array (not SSE) that has to be re-parsed mid-stream; Dify uses `data:` SSE but with different event types. Each provider's `DownloadHandlerScript` (or WebGL fetch-reader) has its own parse loop. **A bug in Gemini's stream parsing does not affect ChatGPT** — but it also does not get *fixed* by a fix in ChatGPT. Five copies of "consume SSE deltas" exist. This is the cost CDK accepts for provider-fidelity.

### 3.2 The context-history hygiene is per-provider

`MakePromptAsync` in each provider has a loop (e.g. `ChatGPTService.cs:94-115`) that walks history backwards and removes orphaned `tool_calls`/`tool_use` messages whose response is missing — because the provider will reject a request with an unmatched function-call. The Gemini version (`GeminiService.cs:97-118`) and Claude version (`ClaudeService.cs:70-91`) and ChatGPT version are *similar but not identical*. A subtle bug in one is invisible to the others. The right refactor is a shared `RepairContextHistory<TMessage>` template; CDK does not do this.

### 3.3 Vision recursion can infinite-loop in theory

The protection: `chatGPTSession.IsVisionAvailable = false` set before the recursive call (`ChatGPTService.cs:376`). If the LLM emits `[vision:foo]` again in the recursive call, the `extractedTags.ContainsKey("vision") && chatGPTSession.IsVisionAvailable` guard at line 373 fails and the path doesn't recurse. **One** vision call per session. Good for safety; bad if the user genuinely wants two pictures from one turn (capture a flower, then a different angle). Ember should make this configurable per-turn rather than session-permanent.

### 3.4 Tool recursion can stack-overflow

The tool-call recursive `StartStreamingAsync` call (line 369) does not bound depth. A misbehaving LLM that calls tools repeatedly could recurse indefinitely. The `useFunctions: false` masking prevents single-turn recursion but does not prevent tool-result-triggers-new-tool-call patterns across recursion levels. Ember should bound tool-call depth (say, 5) and emit a Sögumiðla event when reached.

### 3.5 The WebGL #ifdef-disabling-base-service is correct but unusual

`LLMServiceBase.IsEnabled` returns `false` on WebGL builds *unconditionally for the native service*, forcing the WebGL variant to be the active one. This is the right behaviour but it makes integration testing weird — the same prefab works on both platforms by *silently swapping* which component answers `IsEnabled`. Volmarr's reviewer instinct should note this; it is not a bug but it is fragile.

### 3.6 No retry-with-different-provider

The retry logic (`ChatGPTService.cs:154-168`) calls *the same provider* on timeout. If ChatGPT is rate-limited, it fails again. **No cross-provider failover.** For Ember, the proposed `Smiðja` should have provider-list-with-failover semantics — primary ChatGPT, fall back to Claude, fall back to local Llama on Hugarsýn fallback rite.

### 3.7 The `historyTurns * 2` magic

`GetContext(historyTurns * 2)` (e.g. `ChatGPTService.cs:93`) — the `× 2` because each turn is user + assistant = two messages. This is the kind of arithmetic that's correct now and silently wrong after one refactor. A typed `TurnCount` value would prevent the bug class.

### 3.8 The crisp parts

- **The five-providers-with-WebGL-twin pattern** done at the right granularity.
- **`historyTurns` + `contextTimeout` for explicit memory decay** — the only corpus to name this.
- **The dual tag-extraction patterns** (regex on stream buffer for k/v signals; positional regex for animation/voice split) — clean separation of concerns.
- **The three-coroutine streaming pipeline** in `LLMContentProcessor` — parse, prefetch, play, all on one queue, no locks.
- **The `Tools = toolSpecs` assignment** in `DialogProcessor.StartDialogAsync` (`DialogProcessor.cs:171`) — tools are refreshed per turn from currently-enabled `ITool` components. Hot-swap tools mid-session.
- **The vision-as-recursion pattern** — `[vision:camera]` triggers a re-call with image bytes attached. The protocol absorbs multimodal as a special case of the same flow.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §1 row 3 — LLM in the macro shape
- [[13_DIALOG_PROCESSOR_DOMAIN]] — the dialog state machine that calls this domain
- [[19_TOOL_DOMAIN]] — `ITool`/`ToolBase` function-calling surface
- [[20_LLM_SERVICE_INTERFACE]] — the contract analysis, per-provider divergence catalogue
- [[26_TOOL_FUNCTION_CALL_INTERFACE]] — function-call wire formats compared
- [[sap:21_OPENAI_COMPAT_API]] — SAP's OpenAI-API simulation (contrast: wire-level vs contract-level abstraction)
- [[waifu:21_LIVEKIT_INTEGRATION]] — Waifu's single-LLM-behind-cloud (contrast: no abstraction at all)
- [[hermes:11_LISTIR_DOMAIN]] — Hermes's Listir (the listener True Name); structural sibling

---

## What This Means for Ember

**Adopt:**
- The **`ILLMService` interface shape** (`Scripts/LLM/ILLMService.cs:8-20`). Ember's `Smiðja` provider Protocol: `is_enabled`, `make_prompt(user_id, text, payloads, token)`, `generate_content(messages, payloads, use_functions, retry, token)`, `tools: list[Tool]`, plus the streaming-end and tag-extracted callbacks. Apache-2.0 attribution required.
- The **`LLMServiceBase` context + timeout pattern** (`Scripts/LLM/LLMServiceBase.cs:56-86`). Ember's history list has an explicit `idle_timeout_seconds: int` config that clears history on read after the threshold. The 10-minute default is a reasonable starting point; per-realm tunable.
- The **`LLMContentProcessor` three-coroutine pattern** (`Scripts/LLM/LLMContentProcessor.cs:29-253`): parser, prefetch-hook, consumer. Ember's `MunnrStreamPump` has the same three async coroutines on one queue. Apache-2.0 attribution required.
- The **`<thinking>` tag stripper** (`Scripts/LLM/LLMContentProcessor.cs:79-117`). Ember adopts verbatim; reasoning models will become more common; the stripper is provider-agnostic.
- The **provider-multiplex-by-enabled-flag** (`Scripts/Dialog/DialogProcessor.cs:81-113`). Ember's `brunnr_config.yaml` or `smidja_config.yaml` lists providers in order; first with `enabled: true` is chosen. *But* Ember adds priority-with-failover (see Invent).

*Apache-2.0 attribution: when patterns from `ChatdollKit/Scripts/LLM/` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:**
- The **five-providers-with-WebGL-twin** structure. Ember does not need a WebGL variant for the Pi-tier baseline — but the *separation* of "transport-bound subclass per build target" is the right shape. For Ember's `Tier-CLOUD` future (cloud streaming with WebRTC), the native + cloud-variant split mirrors CDK's native + WebGL split.
- The **per-provider message classes** (`ChatGPTUserMessage`, `ClaudeMessage`, `GeminiMessage`). Ember adapts by using `@dataclass`es per provider but routing all of them through a common `to_wire_dict() -> dict` method that the HTTP layer calls. Half the code, same separation.
- The **vision-as-tag-recursion** pattern. Adapt as Ember's `[capture:source]` tag that triggers a Hjarta-side memory lookup *or* an Andlit-side camera capture (or, on Pi-tier, a stored-image lookup). Same protocol, broader semantics.
- The **`Dictionary<string, object> payloads`** convention. Adapt as Ember's `dict[str, Any] payloads`, but document the *expected keys* per call-site in `docs/contracts/`. The untyped dict is the right shape for evolvability; the contract docs are the discipline that keeps it usable.

**Avoid:**
- **Five copies of "consume SSE deltas."** Ember writes one shared `async def stream_sse(...)` and providers parameterise it. CDK's choice is defensible at Unity scale; in Python it is gratuitous duplication.
- **Unbounded tool-call recursion.** Ember bounds depth (default 5); emits Sögumiðla `ToolDepthExceeded`.
- **Same-provider retry on timeout.** Ember retries with failover. CDK retries with the same provider, which often fails again for the same reason.
- **`historyTurns × 2` arithmetic.** Use a typed `TurnCount` and convert at the boundary.
- **The native + WebGL #ifdef-toggle base service.** Ember's transport variants are explicit subclasses chosen at config time, not at compile time, so the *active class* is always observable.

**Invent:**
- **The Smiðja Provider Failover Vow.** When a provider returns Timeout or Error, Ember automatically retries on the next-priority provider. Failover is one Sögumiðla event per attempt; the user can post-mortem which provider answered which turn. The cost is bookkeeping; the benefit is *graceful degradation across the entire provider list*.
- **The Cross-Provider Context Migration.** When Ember fails over from Claude to ChatGPT mid-session, the context history is *translated* — Claude's content-block messages become ChatGPT's string-content messages — by a `ContextTranslator` registered per-pair. CDK has no such concept (provider switch wipes context). Ember preserves continuity.
- **The Bounded-Recursion Tool Call.** Tool recursion depth is a typed bound (`tool_recursion_max: int = 5`) checked in the orchestrator, not in the provider. CDK has the bound nowhere; Ember has it once.
- **The Streaming Sentinel Event.** Every sentence parsed by `MunnrStreamPump` emits a Sögumiðla `SentenceParsed(text, position, language)` event *before* prefetch fires. Observability of the LLM stream is first-class — the user can replay-from-log what the model said, in order, with timing. CDK's stream lives only in `StreamBuffer` and is discarded.
- **The Reasoning-Trace Capture Vow.** When the `<thinking>...</thinking>` stripper fires, the stripped content is *captured* to a Sögumiðla `ReasoningTrace` event (gated by config). Not played to user; not in main history; *available* for review. CDK throws thinking away; Ember files it.
- **The Provider-Capability Registry.** Ember's provider list declares per-provider capabilities (`vision: bool`, `tools: bool`, `streaming: bool`, `max_context: int`). The dialog layer queries before sending. If a tool-using turn needs Claude but Claude is failed over to a tool-incapable provider, the orchestrator either short-circuits the tool or refuses the turn. CDK assumes every provider can do everything; Ember knows better.

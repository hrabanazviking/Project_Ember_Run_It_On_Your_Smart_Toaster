---
codex_id: 20_LLM_SERVICE_INTERFACE
title: LLM Service Interface — Eight Members, Five Wire Formats, Five Adapter Costs
role: Architect
layer: Interface
status: draft
chatdoll_source_refs:
  - Scripts/LLM/ILLMService.cs:1-58
  - Scripts/LLM/LLMServiceBase.cs:1-175
  - Scripts/LLM/ChatGPT/ChatGPTService.cs:1-661
  - Scripts/LLM/Claude/ClaudeService.cs:1-565
  - Scripts/LLM/Gemini/GeminiService.cs:1-616
  - Scripts/LLM/Dify/DifyService.cs:1-405
  - Scripts/LLM/AIAvatarKit/AIAvatarKitService.cs:1-448
ember_subsystem_targets: [Smiðja, Hugarsýn]
cross_refs:
  - 10_domain/16_LLM_SERVICE_DOMAIN
  - 10_domain/19_TOOL_DOMAIN
  - 20_interface/26_TOOL_FUNCTION_CALL_INTERFACE
  - 50_verification/53_MULTI_LLM_CONSISTENCY
  - sap:21_OPENAI_COMPAT_API
  - waifu:21_LIVEKIT_INTEGRATION
---

# LLM Service Interface
## Eight Members, Five Wire Formats, Five Adapter Costs

*— Rúnhild Svartdóttir, Architect*

> *An interface is a treaty. The five LLM providers do not agree on what an LLM should look like; ChatdollKit's `ILLMService` is the treaty they signed under coercion. The signatures of the treaty are the eight members of the interface; the small print is the five `*Service.cs` files. Both must be read to understand what the contract really means.*

`Scripts/LLM/ILLMService.cs` (58 lines) declares the contract every CDK LLM provider must conform to. The domain doc ([[16_LLM_SERVICE_DOMAIN]]) showed *what* the contract is. This doc shows *how the providers conform*, *where they diverge*, and *what the cost of unification* looks like in practice. The argument is that an LLM-provider abstraction can be honest about divergence only if the *interface is small enough to admit five wildly different wire formats* and the *adapters are visible enough to audit*. CDK manages both. The audit is unpleasant; the result is correct.

This is the deep-dive companion to [[16_LLM_SERVICE_DOMAIN]] §2.4. Five providers; per-provider divergences enumerated below; recommendations for Ember's own LLM abstraction.

---

## 1. The Contract — `ILLMService`

`Scripts/LLM/ILLMService.cs:8-20`:

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
```

Plus three companion interfaces (`ILLMSession`, `ILLMMessage`, `ILLMTool`/`ILLMToolParameters`) and one enum (`ResponseType`).

**The eight members analysed:**

| # | Member | Purpose | Per-provider override needed? |
|---|---|---|---|
| 1 | `IsEnabled` | Multiplex select | Yes (WebGL-disable override in base) |
| 2 | `OnEnabled` | Event for activation | Inherited (set by AIAvatar wiring) |
| 3 | `Tools` | Available tool specs | Inherited (list assigned per turn) |
| 4 | `GetContext(count)` | Read N messages of history | Inherited; Gemini overrides for user-first constraint |
| 5 | `ClearContext()` | Reset history | Inherited; Dify and AIAvatarKit override for server-side state |
| 6 | `MakePromptAsync(user, text, payloads, token)` | Build provider-specific message list | **Always overridden** |
| 7 | `GenerateContentAsync(messages, payloads, useFunctions, retry, token)` | Send request, start streaming | **Always overridden** |
| 8 | `OnStreamingEnd` callback | Hook fired when stream completes | Inherited (used for downstream coordination) |

Plus `HandleExtractedTags` for the `[face:Joy]`-style tag delivery and `CaptureImage` for the vision-recursion hook.

**The shape is right.** Eight members, four are pure inheritance (set by external wiring), four require provider work. The provider work concentrates in two methods (`MakePromptAsync`, `GenerateContentAsync`); everything else flows from those.

### 1.1 The `ILLMSession` companion

`Scripts/LLM/ILLMService.cs:27-40`:

```csharp
public interface ILLMSession
{
    bool IsResponseDone { get; set; }
    string StreamBuffer { get; set; }
    string CurrentStreamBuffer { get; set; }
    bool IsVisionAvailable { get; set; }
    ResponseType ResponseType { get; set; }
    UniTask StreamingTask { get; set; }
    string FunctionName { get; set; }
    string FunctionArguments { get; set; }
    List<ILLMMessage> Contexts { get; set; }
    string ContextId { get; set; }
    bool ProcessLastChunkImmediately { get; set; }
}
```

Eleven members. The session is the *mutable accumulator* of one streaming turn. `StreamBuffer` accumulates all text; `CurrentStreamBuffer` resets per recursive call (used by tool-call recursion); `FunctionName` + `FunctionArguments` accumulate function-call deltas; `IsResponseDone` flips when the stream ends.

The interface is `public` so the `LLMContentProcessor` (downstream consumer) can read it. The implementations per-provider are *concrete subclasses* (`ChatGPTSession`, `ClaudeSession`, etc.) with provider-specific extra fields (`ChatGPTSession.ToolCallId`, `ClaudeSession.ToolUseId`, `DifySession.ConversationId`).

**The cost**: per-provider session subclasses store wire-format-specific state. The consumer (`LLMContentProcessor`) sees them as `ILLMSession`. The provider casts to its concrete type internally. Type-safe enough; not quite tidy.

### 1.2 The `ILLMMessage` marker interface

```csharp
public interface ILLMMessage { }
```

Empty. A marker. Every provider has its own `<Vendor>Message` class implementing this — `ChatGPTUserMessage`, `ChatGPTSystemMessage`, `ChatGPTAssistantMessage`, `ChatGPTFunctionMessage`, `ClaudeMessage`, `GeminiMessage`, `DifyRequestMessage`, `AIAvatarKitRequestMessage`. **The messages are not interchangeable across providers.** Switching from ChatGPT to Claude mid-session means the message-list types do not match; the context is effectively wiped (which is what happens — see [[16_LLM_SERVICE_DOMAIN]] §3.2).

The marker pattern is deliberate: the interface says *"a thing that could be in a context list"*, with no shape constraint, because the shapes diverge. This is *honest* — the alternative would be a leaky abstraction that pretended the messages were equivalent.

### 1.3 The `ILLMTool` companion

`Scripts/LLM/ILLMService.cs:44-57`:

```csharp
public interface ILLMTool {
    string name { get; set; }
    string description { get; set; }
    ILLMToolParameters parameters { get; set; }
    void AddProperty(string key, Dictionary<string, object> value);
}

public interface ILLMToolParameters {
    string type { get; set; }
    Dictionary<string, Dictionary<string, object>> properties { get; set; }
}
```

A name, description, and JSON-schema-shaped parameters (`type` + `properties`). The shape is OpenAI's function-calling spec, which the other providers convert from at request build time. Detail at [[26_TOOL_FUNCTION_CALL_INTERFACE]].

---

## 2. The Five Providers' Conformance

### 2.1 ChatGPT — the *reference* implementation

`Scripts/LLM/ChatGPT/ChatGPTService.cs` (661 LOC) is the *most-OpenAI-shaped* of the five. The contract maps almost transparently:

- **MakePromptAsync** (line 82-137): builds a list of `ChatGPTSystemMessage`, history items, then a `ChatGPTUserMessage` (text-only or with image-url multimodal).
- **GenerateContentAsync** (line 140-171): wraps `StartStreamingAsync` with retry logic on `ResponseType.Timeout`.
- **StartStreamingAsync** (line 173-409): the meat. Build request dict (`model`, `temperature`, `messages`, `stream: true`, `tools`, `tool_choice`); POST to OpenAI's chat-completions endpoint with `Authorization: Bearer <key>`; consume SSE stream via custom `DownloadHandlerScript`; handle function-call deltas; handle vision tag recursion; update context.

**Wire format characteristics**:
- System message is **inside** the messages array (line 87-90).
- Function-calling: `tools: [{type: "function", function: <toolSpec>}]` (line 200-209).
- Tool result: `ChatGPTFunctionMessage` with `tool_call_id` (line 363).
- Streaming: SSE with `data:` prefix and `[DONE]` terminator (handled by `DownloadHandler.ReceiveData` at line 435-492).
- Vision: image URLs in `content` parts of user messages (line 122-128); CDK uses `data:image/jpeg;base64,...` data URLs.

This provider is the *cleanest* in the sense that the wire format and the OpenAI ecosystem align. The Azure OpenAI variant (toggled by `IsAzure` flag, line 18) changes only auth header (`api-key` instead of `Authorization`); other than that, identical. The OpenAI-compat variant (line 19) skips `frequency_penalty`/`presence_penalty` parameters for providers like Groq that don't support them. **The most general-purpose provider.**

### 2.2 Claude — the *content-block* model

`Scripts/LLM/Claude/ClaudeService.cs` (565 LOC). Same overall shape; the wire format is qualitatively different:

- System message is a **top-level field** in the request body (line 152): `{"system": SystemMessageContent, ...}`. Not in `messages` array.
- Messages are `ClaudeMessage` with `role` ("user" or "assistant") and `content` as a *list of content blocks* (text, image, tool_use, tool_result). Cannot be a string; must be a list.
- Function-calling: `tools: [<ClaudeTool>]` where `ClaudeTool` wraps the spec with Claude-specific schema fields (line 159-166).
- Tool result: `ClaudeMessage` with a `tool_result` content block containing `tool_use_id` (line 46-52).
- Streaming: SSE with `event: <type>` prefix (parsed differently from OpenAI's `data:`).
- Vision: `image` content block with `source: {type: "base64", media_type: "image/jpeg", data: <base64>}` (line 98).

**The biggest divergence is the content-block list shape.** ChatGPT messages have a string `content`; Claude messages have a *list* with at least one text block. Translating ChatGPT history to Claude format means re-wrapping every assistant message. CDK does not do this — switching providers wipes context.

The `UpdateContext` (line 30-59) carefully separates "user message" (last item, image content removed) from "assistant message" (new, may include tool_use block). The `tool_use → tool_result` *sequencing* is preserved (line 70-91 guards orphan tool_use messages).

### 2.3 Gemini — the *quirkiest* implementation

`Scripts/LLM/Gemini/GeminiService.cs` (616 LOC). Google's API has its own conventions:

- Messages are called `contents`; roles are `user` and `model` (not "assistant"). System message is faked as a `user`→`model` exchange (line 91-92).
- The first message **must be `user` role**; CDK has an *override* `GetContext` (line 30-52) that walks the context list backward to ensure the slice starts with a user message. Quirk-handling code, in the base override.
- Function-calling: `tools: [{functionDeclarations: <toolSpecsList>}]` (line 195-200). One-level deeper wrapping than OpenAI/Claude.
- Tool result: `GeminiMessage` with a `functionResponse` part (rather than a separate role).
- Streaming: a JSON *array* — not SSE — that has to be re-parsed mid-stream. The download handler (lines around 350) must accumulate brackets and parse complete JSON objects from a growing array.
- Thinking models: `generationConfig.thinkingConfig: {"thinkingLevel": "minimal"}` (line 180). Set to suppress chain-of-thought, but the LLM may still emit `<thinking>...</thinking>` blocks the stripper has to handle.

**The most awkward provider** to abstract under `ILLMService`. The user-first constraint, the JSON-array streaming, the role naming — every one of these requires per-provider workaround code. Gemini's bug-by-bug compatibility is real; CDK absorbs it.

### 2.4 Dify — the *stateless-client* implementation

`Scripts/LLM/Dify/DifyService.cs` (405 LOC). Dify is a *server-side LLM orchestration platform*; CDK is its client:

- **No client-side context.** Dify holds the conversation under `conversation_id` (line 30-38). CDK's local `context` list is empty for Dify; the `ContextId` field on the session is the Dify conversation ID.
- **No prompt assembly.** Dify holds the system prompt; CDK sends `query` strings.
- **No client-side tool list.** Dify holds the tool definitions; CDK does not pass `Tools`.
- Streaming: SSE with Dify-specific event types (`message`, `message_end`, `workflow_started`, etc.; download handler parses).
- File uploads (for vision): a separate `/files/upload` POST returns an ID; the ID is referenced in the next chat-messages POST (line 135-146).

**Dify is the *least* like a primitive LLM API and the *most* like a managed agent platform.** The conformance to `ILLMService` is partial — many methods are no-ops or trivial — because the contract assumes client-side state Dify doesn't expose. CDK paves over this by reinterpreting `ContextId` to mean "Dify conversation ID" and `ClearContext()` to mean "discard the conversation ID locally."

### 2.5 AIAvatarKit — the *sister-project* implementation

`Scripts/LLM/AIAvatarKit/AIAvatarKitService.cs` (448 LOC). Same shape as Dify (server-side orchestration), but the server is **uezo's own AIAvatarKit FastAPI service** — a separate repository for a separate avatar pipeline.

- Server-side state via `context_id` (line 30-51).
- **`ProcessLastChunkImmediately = true`** (line 85) — a flag the AIAvatarKit pipeline uses for ultra-low-latency turn-final handling. AIAvatarKit's streaming pipeline can emit a tool-call result *and* the final assistant message in the same response; CDK's content processor must process the last chunk without waiting.
- `AAKSessionId` (line 18) is the avatar-session-level identifier (separate from the per-turn context_id); used for cross-turn memory and tool-state continuity on the AIAvatarKit side.

The AIAvatarKit integration is the tightest in the codebase — it ships with WebGL variants, has explicit `HandleToolCall` and `UploadImageFunc` hooks (lines 27-28), and is the only provider with `ProcessLastChunkImmediately` semantics. Forge-B's [[39_AIAVATARKIT_STREAMING]] documents it fully.

---

## 3. The Divergence Matrix

Pulling it together — the dimensions on which the five providers diverge:

| Dimension | ChatGPT | Claude | Gemini | Dify | AIAvatarKit |
|---|---|---|---|---|---|
| **System message** | In `messages[0]` | Top-level `system` field | Faked as user→model pair | Server-side | Server-side |
| **Roles** | `user`/`assistant`/`system`/`tool` | `user`/`assistant` (list content) | `user`/`model` | (server-side) | (server-side) |
| **Streaming format** | SSE `data:` | SSE `event:` | JSON array | SSE Dify-events | SSE AAK-events |
| **Function call shape** | `tools: [{type:"function", function:{}}]` | `tools: [{ClaudeTool}]` | `tools: [{functionDeclarations: []}]` | Server-side | Server-side |
| **Function result shape** | `tool` role message | `tool_result` content block | `functionResponse` part | (server-side) | (server-side) |
| **Mask tools** | `tool_choice: "none"` | `tool_choice: {type:"none"}` | `toolConfig.functionCallingConfig.mode: "NONE"` | n/a | n/a |
| **Multimodal** | `image_url` content part | `image` content block | `inlineData.mimeType` part | Upload-then-reference | Upload-then-reference |
| **Context held** | Client | Client | Client | Server | Server |
| **Retry on timeout** | Yes, same provider | Yes, same provider | Yes, same provider | Yes, same provider | Yes, same provider |
| **WebGL variant** | Yes (341 LOC) | Yes (311 LOC) | Yes (302 LOC) | Yes (274 LOC) | Yes (308 LOC) |

**Nothing aligns except `IsEnabled` and the streaming-via-`StreamBuffer` accumulation pattern.** Every dimension has 2-3 distinct shapes. This is *not* a leaky abstraction — it is an honest one. The leakage would be pretending these are interchangeable.

---

## 4. Where the Contract Strains

### 4.1 The marker `ILLMMessage` interface

`ILLMMessage { }` (empty) is permissive enough to admit any provider's message type but provides *zero* compile-time guarantees about cross-provider compatibility. The runtime cost: switching providers loses context. The compile-time cost: the consumer (`DialogProcessor`) cannot do anything useful with a `List<ILLMMessage>` except pass it back to the same provider.

Alternative would be a *constrained* marker like `ILLMMessage { string Role { get; } string AsText(); }` — but `Role` enums diverge and `AsText` discards multimodal content. CDK's choice (empty marker) is correct given the divergence.

### 4.2 The `payloads: Dictionary<string, object>` untyped dict

Every method takes a `Dictionary<string, object>` for extension. Inside, conventions: `"RequestPayloads"` key wraps actual payload; `CustomParameters` and `CustomHeaders` are sibling keys.

**This is duct tape**, and CDK admits it. The reason it works: per-provider code knows what to extract. The reason it's bad: typos in key names are silent (the `ContainsKey` check returns false; default behaviour kicks in). Ember should use Pydantic models with typed fields.

### 4.3 The `useFunctions: bool` parameter

`GenerateContentAsync(..., bool useFunctions = true, ...)` is the only way for the recursive tool-call mask to propagate. `useFunctions: false` translates to `tool_choice: "none"` for ChatGPT, `{type: "none"}` for Claude, `mode: "NONE"` for Gemini. **Three encodings; one boolean parameter.** This is the abstraction earning its keep — the caller knows nothing about the encoding.

The cost: the recursive call has no other way to communicate intent. If a future requirement is "mask only some tools," there's no place for it in the signature. Ember's equivalent should be a `tool_mask: set[str] | Literal["all", "none"] | None` field on the request.

### 4.4 The `retryCounter` parameter is per-call

`retryCounter: int = 1` lives in the method signature. Each provider implements its own retry inside `GenerateContentAsync`. The retry behaviour is *uniform* (same provider, same call, decrement counter) but the *failure-detection logic* differs (timeout detection, error response shape). Cross-provider retry is impossible because the counter is consumed inside one provider.

For Ember: lift retry to the orchestrator. The provider raises typed exceptions; the orchestrator decides whether to retry, fall back, or fail.

### 4.5 The `OnStreamingEnd` callback is set externally

```csharp
public Func<string, Dictionary<string, object>, ILLMSession, CancellationToken, UniTask> OnStreamingEnd { get; set; }
```

The callback signature takes `(streamBuffer, payloads, session, token)`. AIAvatar wires this to a handler that updates ChatMemory (the `AddHistory` integrator call). The provider invokes it; AIAvatar handles it. Decoupling works.

But: only *one* handler can be assigned (it's a `Func`, not a multi-cast event). If a second consumer wanted to know when streaming ended (telemetry, observability), they have to wrap AIAvatar's handler. Ember's equivalent should be a proper `event_bus.subscribe(StreamingEnded)` for multi-consumer.

### 4.6 The `HandleExtractedTags` is a single-assignment too

Same shape as `OnStreamingEnd`. AIAvatar wires it to a handler that routes `[face:Joy]` style key/value tags. One handler.

### 4.7 The `CaptureImage` hook is provider-aware

`Func<string, UniTask<byte[]>>` — given an image-source string, return image bytes. AIAvatar wires it to `SimpleCamera.CaptureImageAsync` or to a memory-lookup. The provider calls it when the stream contains `[vision:source]`. Recursive re-call with image bytes attached.

**The single-handler limitation matters most here.** A user who wanted to *log* every image capture in addition to performing it has no clean way. Ember's image-capture is an event-bus event with both a *requirements* phase (subscribers can veto) and a *result* phase (subscribers see the bytes).

---

## 5. Cross-References

- [[16_LLM_SERVICE_DOMAIN]] — the domain doc this expands
- [[19_TOOL_DOMAIN]] — tools that flow through the `Tools` member
- [[26_TOOL_FUNCTION_CALL_INTERFACE]] — full per-provider function-call shapes
- [[53_MULTI_LLM_CONSISTENCY]] — Auditor's catalogue of inconsistency failures
- [[sap:21_OPENAI_COMPAT_API]] — SAP's wire-level OpenAI-compat simulation
- [[waifu:21_LIVEKIT_INTEGRATION]] — Waifu's no-abstraction single-cloud-LLM
- [[hermes:1B_LISTIR_INTERFACE]] — Hermes's Listir interface (sibling listener True Name)

---

## What This Means for Ember

**Adopt:**
- The **eight-member `ILLMService` interface shape** as Ember's `LLMProvider` Protocol. Apache-2.0 attribution required. Members: `is_enabled`, `on_enabled`, `tools`, `get_context(count)`, `clear_context()`, `make_prompt(user, text, payloads, token)`, `generate_content(messages, payloads, use_functions, retry, token)`, plus the three callback slots.
- The **separation of `MakePromptAsync` and `GenerateContentAsync`** — two phases, two methods. Lets the orchestrator inject behaviour between prompt-build and request-send.
- The **`ILLMSession` mutable-accumulator pattern** for streaming. Ember's `LLMSession` dataclass has the same fields; per-provider subclasses add provider-specific state.
- The **marker `ILLMMessage` pattern** — an empty `Protocol` admitting per-provider message types. Honest abstraction over divergence.
- The **`useFunctions: bool` recursive-mask parameter**. Translates to three different encodings per provider; one switch at the caller.

*Apache-2.0 attribution: when patterns from `ChatdollKit/Scripts/LLM/ILLMService.cs` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:**
- The **`payloads: Dictionary<string, object>` untyped dict** to Ember's Pydantic-typed `RequestPayloads` model. Lose the duct-tape feel; keep the extensibility (`Extra.allow`).
- The **single-handler `OnStreamingEnd` callback** to a proper event bus with multi-subscriber semantics.
- The **per-call `retryCounter`** to orchestrator-level retry policy. Providers raise typed exceptions; the orchestrator routes.
- The **per-provider message subclasses** to provider-specific Pydantic models that share a common `BaseLLMMessage` parent with shape-agnostic fields (`role: str`, `content: Any`) for serialisation/audit.

**Avoid:**
- **Same-provider retry without circuit-breaking.** Use the orchestrator's failover (see [[16_LLM_SERVICE_DOMAIN]]'s Smiðja Provider Failover Vow).
- **Single-handler callback slots.** Use the event bus.
- **`ILLMTool` shaped exactly like OpenAI's function calling.** Ember's `ToolSpec` is provider-neutral; per-provider codecs translate.

**Invent:**
- **The Provider Capability Manifest.** Each Ember LLM provider declares: `supports_streaming: bool`, `supports_tools: bool`, `supports_vision: bool`, `supports_thinking: bool`, `max_context: int`, `wire_format: enum`. The orchestrator queries before sending; mismatched capabilities short-circuit at the boundary, not deep in a provider's adapter.
- **The Wire Format Codec Registry.** A single declaration of message shape per provider via a `WireFormatCodec` Protocol: `to_wire(messages: list[BaseMessage]) -> dict`, `from_wire(chunk: bytes) -> StreamDelta`, `tool_spec_to_wire(spec: ToolSpec) -> dict`, `tool_result_to_wire(result: str, call_id: str) -> dict`. Five codecs; one declaration per provider; cross-provider testing via property-based tests.
- **The Cross-Provider Context Translator.** Given a context list under provider A, translate to provider B's shape: ChatGPT's `content: str` → Claude's `content: [TextBlock(text)]`; Claude's content-blocks → Gemini's parts. Lossy in some cases (Gemini's `model` role maps from `assistant`); audited via Sögumiðla `ContextTranslationLoss` events.
- **The Streaming Health Monitor.** Per-turn, track time-to-first-byte, time-to-first-sentence, total stream duration. Cross-provider comparison surfaces "ChatGPT is responding slower today" before users complain.
- **The Thinking-Strip Audit.** Every `<thinking>` block stripped is captured (gated by config) so post-mortem analysis can verify the model's reasoning. Ember filed; CDK discarded.
- **The Vision Capture Audit Trail.** Every `[vision:source]` recursion is logged: `(source, bytes_size, retrieval_latency_ms)`. The post-mortem can answer "which image did the avatar see during this turn?" CDK shows it in `Debug.Log`; Ember files it as a typed event with a content-addressed reference to the bytes.
- **The Single-Provider-Failover-Mode Switch.** Ember's provider list can be marked `failover: enabled` (try next on failure) or `failover: disabled` (fail the turn). The choice is per-realm: production realms have failover enabled; testing realms have it disabled (so the user *sees* provider failures and can debug them). CDK has neither mode explicit.

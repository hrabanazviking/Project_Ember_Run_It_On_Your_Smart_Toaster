---
codex_id: 36_FUNCTION_CALL_EXEC
title: Function Call Execution — Three Providers, Three Wire Formats, One ITool
role: Forge-A
layer: Execution
status: draft
kit_source_refs:
  - Scripts/LLM/ITool.cs:1-26
  - Scripts/LLM/ToolBase.cs:1-46
  - Scripts/LLM/LLMServiceBase.cs:1-175
  - Scripts/LLM/ChatGPT/ChatGPTService.cs:199-409 (function-call request + execution)
  - Scripts/LLM/ChatGPT/ChatGPTService.cs:476-487 (stream parser)
  - Scripts/LLM/Claude/ClaudeService.cs:159-348 (tool_use lifecycle)
  - Scripts/LLM/Claude/ClaudeService.cs:395-414 (stream parser)
  - Scripts/LLM/Gemini/GeminiService.cs (functionCall format)
  - Scripts/Dialog/DialogProcessor.cs:115-128 (LoadLLMTools)
ember_subsystem_targets: [Smiðja, Strengr, Hjarta]
cross_refs:
  - 31_AIAVATAR_MAIN_LOOP
  - 26_TOOL_FUNCTION_CALL_INTERFACE
  - 16_LLM_SERVICE_DOMAIN
  - 19_TOOL_DOMAIN
  - 53_MULTI_LLM_CONSISTENCY
  - sap:20_MCP_INTEGRATION
  - waifu:22_ACTION_PROTOCOL
license_posture: Apache-2.0 — adopt with attribution
---

# Function Call Execution

> *Three providers. Three wire formats. One C# interface. The adapter shows you exactly where your portability ends.*

Forge-A. Eldra. ChatdollKit supports tool/function calling across ChatGPT, Claude, Gemini, Dify, and any OpenAI-compatible endpoint. It does this through a single `ITool` interface in C# code and three completely different JSON wire formats on the network. Reading the three adapters side-by-side is the cleanest tutorial you'll ever get on what "LLM provider portability" actually costs. Here is the full path from "LLM emitted a function call" to "ToolBase.ExecuteAsync returned and the model spoke the result."

## The ITool Surface

Whole interface fits in twelve lines (`/tmp/ChatdollKit/Scripts/LLM/ITool.cs:1-26`):

```csharp
// /tmp/ChatdollKit/Scripts/LLM/ITool.cs:1-26
public interface ITool
{
    bool IsEnabled { get; set; }
    ILLMTool GetToolSpec();
    UniTask<ILLMSession> ProcessAsync(ILLMService llmService, ILLMSession llmSession,
                                       Dictionary<string, object> payloads, CancellationToken token);
    UniTask<ToolResponse> ExecuteAsync(string argumentsJsonString, CancellationToken token);
}

public class ToolResponse
{
    public string Body { get; protected set; }
    public string Role { get; protected set; }

    public ToolResponse(string body, string role = "function")
    {
        Body = body;
        Role = role;
    }
}
```

Three things a tool must do:

1. **Self-describe** via `GetToolSpec()` returning an `ILLMTool` (name + description + parameters).
2. **Execute** via `ExecuteAsync(argumentsJsonString, token)` returning a `ToolResponse` (body + role).
3. **(Deprecated)** `ProcessAsync` exists for v0.7.x migration compat (`ToolBase.cs:27-30` is a stub that returns null).

`ToolBase` (`/tmp/ChatdollKit/Scripts/LLM/ToolBase.cs:1-46`) implements the MonoBehaviour boilerplate. A real tool extends `ToolBase`, overrides `GetToolSpec()` and `ExecuteFunction()`. That's the entire developer surface. SAP's MCP integration is a 200-line manager class with config files; this is twelve lines of C# interface.

## Tool Discovery — `LoadLLMTools`

`DialogProcessor.LoadLLMTools` (`DialogProcessor.cs:115-128`) discovers tools at boot:

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

Same pattern as the speech-listener/synthesizer auto-selection covered in [[30_UNITY_BOOTSTRAP]]: walk every sibling MonoBehaviour implementing `ITool`, keep the `IsEnabled` ones, build a name→tool dictionary plus a spec list to pass to the LLM. Per-tool enable/disable is an Inspector toggle.

`toolSpecs` is what the LLM sees. `toolResolver` is what executes when a function call comes back. The list of specs gets passed to `llmService.Tools` before each dialog (`DialogProcessor.cs:171`):

```csharp
// /tmp/ChatdollKit/Scripts/Dialog/DialogProcessor.cs:171
llmService.Tools = toolSpecs;
```

## ChatGPT — `tools` Array with `type: function`

ChatGPT's wire format (`ChatGPTService.cs:199-216`):

```csharp
// /tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:199-216
if (Tools.Count > 0)
{
    var tools = new List<Dictionary<string, object>>();
    foreach (var tool in Tools)
    {
        tools.Add(new Dictionary<string, object>()
        {
            { "type", "function" },
            { "function", tool }
        });
    }
    data.Add("tools", tools);
    if (!useFunctions)
        data.Add("tool_choice", "none");
}
```

OpenAI's spec is `tools: [{type: "function", function: {name, description, parameters}}]`. The `useFunctions=false` case sets `tool_choice="none"` (`:214`) rather than removing the tools entirely — keeping the tool list in the prompt preserves prompt-cache hits and reduces hallucination probability on the next turn.

The streaming response handling — that's where it gets fun. ChatGPT streams tool calls as deltas (`ChatGPTService.cs:476-487`):

```csharp
// /tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:476-487
if (delta.tool_calls == null)
{
    SetReceivedChunk(delta.content);
}
else if (delta.tool_calls.Count > 0)
{
    SetToolCallInfo(
        delta.tool_calls[0].id,
        delta.tool_calls[0].function.name,
        delta.tool_calls[0].function.arguments
    );
}
```

Each streamed chunk either has text content (`delta.content`) or a tool-call fragment (`delta.tool_calls[0]`). The first fragment has the `id` and `name`; subsequent fragments arrive with `arguments` being incremental JSON pieces. The accumulator (`ChatGPTService.cs:273-286`):

```csharp
// /tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:273-286
downloadHandler.SetToolCallInfo = (id, name, arguments) =>
{
    chatGPTSession.ResponseType = ResponseType.Content;
    if (!string.IsNullOrEmpty(id))
    {
        chatGPTSession.ToolCallId = id;
        chatGPTSession.FunctionName = name;
        chatGPTSession.FunctionArguments = string.Empty;
    }
    if (!string.IsNullOrEmpty(arguments))
    {
        chatGPTSession.FunctionArguments += arguments;
    }
};
```

Critical: id+name are set *once* (when present); arguments are *appended* (the JSON streams in piece by piece). At end-of-stream, `FunctionArguments` is the complete arguments JSON string.

## Claude — `content_block_start` and `input_json_delta`

Claude's wire format is structurally different. Tools are top-level (`ClaudeService.cs:159-172`):

```csharp
// /tmp/ChatdollKit/Scripts/LLM/Claude/ClaudeService.cs:159-172 (compressed)
if (Tools.Count > 0)
{
    var claudeTools = new List<ClaudeTool>();
    foreach (var tool in Tools) claudeTools.Add(new ClaudeTool(tool));
    data.Add("tools", claudeTools);
    if (!useFunctions)
        data.Add("tool_choice", new Dictionary<string, string>(){ {"type", "none"} });
}
```

Note `tool_choice` is a `{"type": "none"}` object, not a string `"none"` like ChatGPT. That's the kind of detail that breaks naive cross-provider abstractions.

The streaming format is different too (`ClaudeService.cs:395-414`):

```csharp
// /tmp/ChatdollKit/Scripts/LLM/Claude/ClaudeService.cs:395-414 (compressed)
if (csr.type == "content_block_start")
{
    contentBlockType = csr.content_block.type;
    if (contentBlockType == "tool_use")
    {
        SetToolCallInfo(csr.content_block.id, csr.content_block.name, null);
    }
    continue;
}
else if (csr.type == "content_block_delta")
{
    if (csr.delta.type == "input_json_delta")
        SetToolCallInfo(null, null, csr.delta.partial_json);
    else
        SetReceivedChunk(csr.delta.text);
}
```

Claude's stream sends *typed event blocks*: `content_block_start` announces a new content block (text or tool_use); `content_block_delta` carries incremental data for that block; `content_block_stop` (not shown) ends the block. The accumulator pattern is the same as ChatGPT — `id+name` once, `partial_json` appended — but the *trigger* is the block-type, not the presence of a tool_calls array.

A multi-block Claude response can interleave thinking text and tool calls. CDK's single-block-at-a-time state machine handles this by tracking `contentBlockType` (the variable at `:365`); each delta is routed by the current active block type. Solid handling.

## Gemini — `functionCall` Inside `parts`

Gemini's wire format (`GeminiService.cs:194-208`):

```
// /tmp/ChatdollKit/Scripts/LLM/Gemini/GeminiService.cs:194-208 (paraphrased — read original)
// Tools are nested in a `tools` array, each tool has a `function_declarations` array
// `functionCallingConfig.mode = "NONE"` when useFunctions=false
```

The Gemini stream emits content as `candidates[0].content.parts[0]`, where each `part` can have `text`, `functionCall`, or `functionResponse` fields. The function-call extraction (`GeminiService.cs:435-440`):

```
// /tmp/ChatdollKit/Scripts/LLM/Gemini/GeminiService.cs:435-440 (paraphrased)
if (streamResponse.candidates[0].content.parts[0].functionCall != null)
{
    SetToolCallInfo(
        null, // Gemini doesn't have a tool-call id
        streamResponse.candidates[0].content.parts[0].functionCall.name,
        JsonConvert.SerializeObject(streamResponse.candidates[0].content.parts[0].functionCall.args)
    );
}
```

**Gemini has no tool-call ID.** ChatGPT and Claude both use IDs to disambiguate parallel tool calls. Gemini's protocol pre-dates this and just emits the function name + args directly. CDK passes `null` for the ID slot.

The args field is also delivered *complete*, not streamed — `streamResponse.candidates[0].content.parts[0].functionCall.args` is a JSON object that gets serialized in one shot. No incremental delta needed. Gemini either does or doesn't emit a function call per chunk; partial calls aren't represented.

## The Common Code Path — `Execute → Recursively-Call-LLM`

Once a streaming response ends and `ToolCallId` (or `ToolUseId` for Claude, or implicit "function name set" for Gemini) is non-null, the LLM service runs the tool and recursively calls itself. ChatGPT's version (`ChatGPTService.cs:353-372`):

```csharp
// /tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:353-372
if (!string.IsNullOrEmpty(chatGPTSession.ToolCallId))
{
    foreach (var tool in gameObject.GetComponents<ITool>())
    {
        var toolSpec = tool.GetToolSpec();
        if (toolSpec.name == chatGPTSession.FunctionName)
        {
            Debug.Log($"Execute tool: {toolSpec.name}({chatGPTSession.FunctionArguments})");
            var toolResponse = await tool.ExecuteAsync(chatGPTSession.FunctionArguments, token);
            chatGPTSession.Contexts.Add(new ChatGPTFunctionMessage(toolResponse.Body, chatGPTSession.ToolCallId));
            chatGPTSession.ToolCallId = null;
            chatGPTSession.FunctionName = null;
            chatGPTSession.FunctionArguments = null;
            await StartStreamingAsync(chatGPTSession, customParameters, customHeaders, false, token);
        }
    }
}
```

Five steps:
1. **Find the tool by name** via `GetComponents<ITool>()` (linear search — fine for <100 tools).
2. **Execute** with the arguments JSON and the cancel token.
3. **Append the tool result to the LLM context** as a `ChatGPTFunctionMessage` with the tool_call_id.
4. **Reset the tool-call state** to prevent infinite recursion if the same tool is somehow re-detected.
5. **Recursively call `StartStreamingAsync`** with `useFunctions=false` — the LLM gets the function result and produces a natural-language response, but cannot make another tool call this turn.

Claude's version (`ClaudeService.cs:293-311`) is structurally identical, just using `ToolUseId` and the Claude-shaped result message:

```csharp
// /tmp/ChatdollKit/Scripts/LLM/Claude/ClaudeService.cs:293-311 (compressed)
if (!string.IsNullOrEmpty(claudeSession.ToolUseId))
{
    foreach (var tool in gameObject.GetComponents<ITool>())
    {
        var toolSpec = tool.GetToolSpec();
        if (toolSpec.name == claudeSession.FunctionName)
        {
            var toolResponse = await tool.ExecuteAsync(claudeSession.FunctionArguments, token);
            claudeSession.Contexts.Add(new ClaudeMessage("user",
                tool_use_id: claudeSession.ToolUseId,
                tool_use_content: toolResponse.Body));
            claudeSession.ToolUseId = null;
            claudeSession.FunctionName = null;
            claudeSession.FunctionArguments = null;
            await StartStreamingAsync(claudeSession, customParameters, customHeaders, false, token);
        }
    }
}
```

Notice the role differs: ChatGPT wants role=`"tool"` (ChatGPTFunctionMessage at `:601`), Claude wants role=`"user"` with `tool_result` content blocks inside. Gemini wants a `functionResponse` part inside an assistant message. Three providers, three "here is your function result" formats. Each adapter handles its own.

The `useFunctions=false` on the recursive call is the loop-breaker. Without it, the LLM could keep calling functions ad infinitum. CDK's policy is "one tool call per turn, then natural response." This is conservative — some scenarios want multi-step tool use — but safe.

## The Vision Special-Case

Both ChatGPT and Claude handlers also handle `[vision:CameraSource]` extracted tags via the same recursive pattern (`ChatGPTService.cs:373-399`, `ClaudeService.cs:313-338`):

```csharp
// /tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:373-399 (compressed)
else if (CaptureImage != null && extractedTags.ContainsKey("vision") && chatGPTSession.IsVisionAvailable)
{
    chatGPTSession.IsVisionAvailable = false;  // Prevent infinite loop
    var imageSource = extractedTags["vision"];
    var imageBytes = await CaptureImage(imageSource);
    if (imageBytes != null)
    {
        chatGPTSession.Contexts.Add(new ChatGPTAssistantMessage(chatGPTSession.StreamBuffer));
        chatGPTSession.Contexts.Add(new ChatGPTUserMessage(new List<IContentPart>() {
            new ImageUrlContentPart("data:image/jpeg;base64," + Convert.ToBase64String(imageBytes)),
            new TextContentPart($"This is the image you captured. (source: {imageSource})")
        }));
    }
    await StartStreamingAsync(chatGPTSession, customParameters, customHeaders, useFunctions, token);
}
```

The `[vision:Camera]` tag is parsed by `ExtractTags` (the same regex used for `[anim:]` etc.). If `CaptureImage` is wired (it's set by `LLMServiceExtensions`), CDK invokes it, gets back JPEG bytes, appends them as a user message, and recursively calls the LLM. This is a tool-call analogue that uses the tag protocol instead of the structured `tools` field. Cute — but it means the same regex is the routing surface for animation, face, language, *and* image capture. Bear that in mind when extending.

## Where It Breaks

- **Linear `GetComponents<ITool>()` search per tool call.** With 50 tools you do 50 GetComponent walks per invocation. Fine for typical avatars; bad if a future codepath wraps a CDK avatar in an MCP-style aggregator with hundreds of tools. Cache the resolver dictionary.
- **Empty `toolSpec.name == chatGPTSession.FunctionName` not matched.** The loop silently falls through to the "no tool matched" path which is... not handled. The recursive `StartStreamingAsync` doesn't fire, the dialog `Status` stays at whatever state it was in, and `OnEndAsync` cleans up. The LLM never gets a function result. From the user's POV, the avatar said the tool name and then went silent. No error event fires.
- **`Tools = toolSpecs;` is a direct assignment.** Multiple `ILLMService` instances in the scene (e.g., ChatGPT primary + Claude fallback) all see the same `toolSpecs` list at any given moment. `DialogProcessor` swaps `llmService.Tools` on every `StartDialogAsync` (`:171`). If a tool-call is in flight on ChatGPT and the user switches to Claude mid-flight... actually CDK probably handles this via the cancellation token. But the Tools-list mutation is a shared-state race surface.
- **Function-call recursion has no depth limit.** Within a turn, only one tool call happens (because `useFunctions=false` on recursion). But across turns, an unbounded sequence is possible. If a tool's result triggers the LLM to call another tool on the next turn, you can chain indefinitely. Hjarta needs a turn-budget at the orchestration layer.
- **`Newtonsoft.Json` deserialization of `FunctionArguments`.** If the LLM emits malformed JSON in `arguments`, `JsonConvert.DeserializeObject<Dictionary<string, object>>` throws. ChatGPT's path doesn't deserialize args at all — it passes the raw string to `ExecuteAsync` and lets the tool deal with parsing. Claude's path *does* deserialize for the `assistantMessage.content.input` field (`ClaudeService.cs:48-51`). Inconsistent.
- **Gemini's no-tool-call-id model.** If Gemini ever supports parallel tool calls (it doesn't currently per my reading), CDK's `FunctionName` single-field state would conflict. ChatGPT and Claude can handle parallel by tracking multiple IDs; Gemini's adapter can't.

## Where It Surprises

- **The Apache-2.0 license posture means we can adopt these adapters directly.** SAP's `ClaudeAsOpenAI` / `GeminiAsOpenAI` files in `super-agent-party` are a different architecture (server-side translation to OpenAI shape); CDK's adapters are client-side per-provider. Both are valid; CDK's is more transparent.
- **Provider-specific message classes.** `ChatGPTFunctionMessage`, `ClaudeMessage` with tool_use, `GeminiMessage` with functionResponse — each is a strongly-typed C# class. There is no `IMessage` abstraction at this level. Serialization is per-provider, which means the JSON output is correct for each provider but means context history can't be shared across providers within a session (which is the right behavior anyway).
- **The recursive `StartStreamingAsync(..., useFunctions=false, ...)` pattern.** This is the cleanest way to "now respond naturally" — the LLM still has access to its full context including the tool result, but the tools array is masked. No special "response mode" prompt is needed.
- **`Debug.Log($"Execute tool: {toolSpec.name}({chatGPTSession.FunctionArguments})")` (`:360`).** Logs the function name and full arguments JSON to Unity's console. If a tool takes a password or API key as an argument, *it's logged in plaintext*. Production builds need to gate these `Debug.Log` calls or the credentials surface is wide open.
- **Tool execution runs synchronously w.r.t. the dialog status.** While `ExecuteAsync` is awaiting, `DialogStatus` is still `Processing`. AIAvatar shows the user the processing animation throughout. If the tool takes 30 seconds (e.g., a slow API call), the avatar holds the processing animation for 30 seconds with no progress indication. This is a UX gap.

## Cross-References

- [[31_AIAVATAR_MAIN_LOOP]] — the dialog state machine that hosts this whole flow
- [[26_TOOL_FUNCTION_CALL_INTERFACE]] — Architect's interface-layer analysis
- [[16_LLM_SERVICE_DOMAIN]] — domain view of the LLM service abstraction
- [[19_TOOL_DOMAIN]] — `ITool`/`ToolBase` as a domain concept
- [[53_MULTI_LLM_CONSISTENCY]] — Auditor's deep dive on cross-provider divergence
- [[sap:20_MCP_INTEGRATION]] — contrast: SAP uses MCP servers + A2A protocol, not in-process tools
- [[waifu:22_ACTION_PROTOCOL]] — contrast: Waifu's typed action vocabulary at the cloud SDK boundary

## What This Means for Ember

**Adopt:**

- **The `ITool` interface (twelve lines)** (`ITool.cs:7-13`, Apache-2.0 attribution required). This is the right tool surface for Smiðja's local-tool layer. Three methods: `spec()`, `execute(args)`, optional process-async. Adopt verbatim into Ember's Smiðja API.
- **The auto-discovery via component walk** pattern (`DialogProcessor.cs:119-127`). For Smiðja, replace `GetComponents<ITool>()` with `smidja.list_enabled_tools()` returning the same shape. Same auto-enable semantics.
- **The "recursively call LLM with `useFunctions=false`" loop-breaker.** Adopt as Strengr's `respond_to_tool_result(session, result)` that masks tools but preserves context.

**Adapt:**

- **Per-provider adapters as separate modules.** CDK has `LLM/ChatGPT/`, `LLM/Claude/`, `LLM/Gemini/` as sibling folders. Adopt the structure. Each provider gets its own JSON shape, its own streaming parser, its own message classes. Don't try to unify at the C# (Python) level; unify at the `ILLMService` (Strengr.ProviderProtocol) level only.
- **The `Tools = toolSpecs` direct assignment.** Adapt to immutable snapshot semantics: `llm_service.with_tools(spec_list)` returns a configured service; the original list isn't mutated. Avoids the shared-state race surface.
- **The `useFunctions=false` recursion → typed turn budget.** Replace recursive call with a turn-counter in `Hjarta.Session { turn, max_turns, tool_calls_this_turn }`. Default `max_turns_per_user_input = 4`; refuse further tool calls beyond budget.

**Avoid:**

- **`Debug.Log` of full function arguments in production.** Replace with structured event that has explicit credential-redaction. Hjarta gets the un-redacted version; Munnr only sees redacted.
- **Silent fallthrough when tool name doesn't match.** Always emit a `ToolNotFound` event with the requested name and a list of available names. The LLM should be able to see "you tried `weather` but I only have `get_weather`" and self-correct on the next turn.
- **Linear search through tool list.** Pre-build a `Dict[str, ITool]` resolver once, not on every call.
- **Conflating `[vision:X]` tag with structured tool calls.** They live in the same regex but they're semantically different. Ember should have a typed tool path *and* a typed observation-injection path; don't multiplex them through the tag regex.

**Invent:**

- **Smiðja Tool Manifest.** Every Ember tool ships a YAML manifest: `name`, `description`, `parameters` schema, `risk_class` (read-only / writes-local / writes-external / executes-code), `requires_consent: bool`, `audit_record_template`. The manifest is *what the LLM sees* as the tool spec, *and* what Hjarta's audit log uses to render the tool execution. CDK's `GetToolSpec()` returns an opaque object; Ember's must be introspectable.
- **Strengr Tool-Call Receipts.** Every executed tool emits a `ToolReceipt { tool_name, args_json, result_json, latency_ms, started_at, ended_at, success, error_message, audit_record }` to Hjarta. Auditable, replayable, debuggable.
- **Munnr Tool-Call Visualizer.** While a tool is executing, Munnr (and any GUI surface) shows: tool name, redacted arguments, elapsed time, with a progress indicator. CDK's "processing animation" is the right idea; Ember's needs to show *what* is being processed.
- **Hjarta Cross-Provider Context Mirror.** When a tool call happens with provider A, Hjarta records the canonical form (`tool_name + args_json`). If the user mid-session switches to provider B, Hjarta re-renders the historical tool calls in B's format so context is preserved. CDK can't share context across providers because of the typed message classes; Ember can if Hjarta owns the canonical form.

---

*Apache-2.0 attribution: when adopting CDK's tool-execution pattern or LLM adapter structure into Ember source, preserve the ChatdollKit header reference per Apache-2.0 §4(c). The per-provider message-class designs may also be subject to each provider's API terms — review before vendoring.*

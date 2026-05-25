---
codex_id: 26_TOOL_FUNCTION_CALL_INTERFACE
title: Tool Function-Call Interface — Five Wire Formats, Three Tool-Result Roles, One Spec
role: Architect
layer: Interface
status: draft
chatdoll_source_refs:
  - Scripts/LLM/ITool.cs:1-26
  - Scripts/LLM/ToolBase.cs:1-46
  - Scripts/LLM/ILLMService.cs:42-58
  - Scripts/LLM/ChatGPT/ChatGPTService.cs:199-216, 353-372, 429-492
  - Scripts/LLM/Claude/ClaudeService.cs:159-172
  - Scripts/LLM/Gemini/GeminiService.cs:195-210
  - Examples/WeatherTool.cs:1-42
  - Extension/ChatMemory/ChatMemoryTool.cs:1-37
ember_subsystem_targets: [Smiðja, Strengr]
cross_refs:
  - 10_domain/19_TOOL_DOMAIN
  - 10_domain/16_LLM_SERVICE_DOMAIN
  - 20_interface/20_LLM_SERVICE_INTERFACE
  - 50_verification/53_MULTI_LLM_CONSISTENCY
  - sap:19_TOOL_SURFACE
  - waifu:24_REMOTE_ACTION_API
---

# Tool Function-Call Interface
## Five Wire Formats, Three Tool-Result Roles, One Spec

*— Rúnhild Svartdóttir, Architect*

> *Function-calling is the part of LLM APIs where the vendors most loudly do not agree. Each has chosen a different JSON shape; each has chosen a different tool-result role; each handles parallel-tool-calls differently. ChatdollKit's tool interface is small enough to fit through every keyhole — which means the keyholes are all five different shapes, and the adapters do the bending.*

The CDK tool interface is two methods (`GetToolSpec` + `ExecuteFunction`) and one value class (`ToolResponse`). Total: ~70 lines. Inside the LLM service providers, the actual *function-call wire-format adapter code* spans more than 600 LOC across the five `*Service.cs` files — encoding tool specs, parsing function-call deltas, formatting tool results, handling recursion. The asymmetry is the lesson: **the tool author writes 13 lines; the codex writes 60 lines per provider; the user-facing contract is small precisely because the per-provider adapters are large**.

This doc enumerates the per-provider differences in full. It is the spec a future Ember-side `ToolSpecCodec[Provider]` template-method base class would target. The domain doc ([[19_TOOL_DOMAIN]]) covers the *user-facing* interface; this doc covers the *provider-facing* wire-format protocol.

---

## 1. The User-Facing Spec — `ITool` and `ILLMTool`

### 1.1 The author-side contract

`Scripts/LLM/ITool.cs:7-13`:

```csharp
public interface ITool
{
    bool IsEnabled { get; set; }
    ILLMTool GetToolSpec();
    UniTask<ILLMSession> ProcessAsync(...);  // legacy
    UniTask<ToolResponse> ExecuteAsync(string argumentsJsonString, CancellationToken token);
}
```

The author implements `GetToolSpec` (returns the LLM-visible function description) and `ExecuteFunction` (executes given JSON args, returns a `ToolResponse`). The `ToolBase` parent provides the migration scaffold.

### 1.2 The spec object — `ILLMTool` and `ILLMToolParameters`

`Scripts/LLM/ILLMService.cs:44-57`:

```csharp
public interface ILLMTool {
    string name { get; set; }
    string description { get; set; }
    ILLMToolParameters parameters { get; set; }
    void AddProperty(string key, Dictionary<string, object> value);
}

public interface ILLMToolParameters {
    string type { get; set; }                                      // always "object"
    Dictionary<string, Dictionary<string, object>> properties { get; set; }
}
```

The spec carries:
- `name: string` — the function name the LLM will emit.
- `description: string` — what the function does (LLM-readable).
- `parameters.type: string` — "object" (JSON Schema convention).
- `parameters.properties: dict[str, dict]` — JSON Schema property declarations.

Authors construct via `AddProperty(name, propSpec)`. `WeatherTool` example (`Examples/WeatherTool.cs:15-21`):

```csharp
public override ILLMTool GetToolSpec() {
    var func = new LLMTool(FunctionName, FunctionDescription);
    func.AddProperty("location", new Dictionary<string, object>() { { "type", "string" } });
    return func;
}
```

The result is a JSON-Schema-shaped object:

```json
{
  "name": "get_weather",
  "description": "Get current weather in the location.",
  "parameters": {
    "type": "object",
    "properties": {
      "location": { "type": "string" }
    }
  }
}
```

**This is the OpenAI function-calling shape.** The other providers convert from this shape at request time. CDK chose OpenAI's shape as the *internal canonical* and adapts outward.

### 1.3 The result object — `ToolResponse`

`Scripts/LLM/ITool.cs:15-25`:

```csharp
public class ToolResponse {
    public string Body { get; protected set; }
    public string Role { get; protected set; }
    public ToolResponse(string body, string role = "function") {
        Body = body;
        Role = role;
    }
}
```

`Body` is the *serialised JSON string* the tool returns. The LLM will see this as the function's result. `Role` defaults to `"function"` (OpenAI's convention). The role can be overridden — but in practice the per-provider adapter ignores it and substitutes the provider's required role.

---

## 2. The Five Provider Wire Formats

### 2.1 ChatGPT — `tools` array with `function` wrapper

**Sending the spec** (`ChatGPTService.cs:199-216`):

```csharp
if (Tools.Count > 0) {
    var tools = new List<Dictionary<string, object>>();
    foreach (var tool in Tools) {
        tools.Add(new Dictionary<string, object>() {
            { "type", "function" },
            { "function", tool }    // tool is ILLMTool serialised as JSON
        });
    }
    data.Add("tools", tools);
    if (!useFunctions) data.Add("tool_choice", "none");
}
```

Each tool wrapped in `{type: "function", function: <toolSpec>}`. The `tool_choice: "none"` masks tools without removing them (prevents cache invalidation, OpenAI's recommendation).

**Receiving the call** (`ChatGPTService.cs:473-487`):

```csharp
var delta = j.choices[0].delta;
if (delta.tool_calls != null && delta.tool_calls.Count > 0) {
    SetToolCallInfo(
        delta.tool_calls[0].id,
        delta.tool_calls[0].function.name,
        delta.tool_calls[0].function.arguments
    );
}
```

The SSE stream emits `tool_calls` array (with one or more entries; CDK only handles `[0]`). Each has `id`, `function.name`, `function.arguments` (a string, potentially streamed in chunks — CDK concatenates at `ChatGPTService.cs:282-285`).

**Returning the result** (`ChatGPTService.cs:363`):

```csharp
chatGPTSession.Contexts.Add(new ChatGPTFunctionMessage(toolResponse.Body, chatGPTSession.ToolCallId));
```

`ChatGPTFunctionMessage` is a context-message subclass with `role: "tool"`, `tool_call_id`, `content`. The next request includes it; the LLM sees the result and responds.

### 2.2 Claude — `tools` array with `ClaudeTool` wrapper, `tool_result` content block

**Sending the spec** (`ClaudeService.cs:159-172`):

```csharp
if (Tools.Count > 0) {
    var claudeTools = new List<ClaudeTool>();
    foreach (var tool in Tools) claudeTools.Add(new ClaudeTool(tool));
    data.Add("tools", claudeTools);
    if (!useFunctions) data.Add("tool_choice", new Dictionary<string, string>(){ {"type", "none"} });
}
```

`ClaudeTool` is a per-provider wrapper that converts the `ILLMTool`'s shape into Claude's required format (parameter rename: `parameters` → `input_schema`; field reshuffling). The `tool_choice` mask is a *dict* not a string.

**Receiving the call**: Claude's streaming protocol emits an `event: content_block_start` with `content_block.type == "tool_use"` containing `id`, `name`, then `event: content_block_delta` events with `delta.type == "input_json_delta"` chunks. CDK's `ClaudeStreamDownloadHandler` parses these and accumulates.

**Returning the result** (`ClaudeService.cs:46-52`):

```csharp
assistantMessage.content.Add(new ClaudeContent() {
    type = "tool_use",
    id = ((ClaudeSession)llmSession).ToolUseId,
    name = llmSession.FunctionName,
    input = JsonConvert.DeserializeObject<Dictionary<string, object>>(llmSession.FunctionArguments)
});
```

The tool_use is added to the assistant's content list. The tool result then appears in the next user message as a `tool_result` content block referencing the `tool_use_id`.

**Three role/format quirks vs ChatGPT**:
- Tool spec key: `input_schema` not `parameters`.
- Tool-use role: stays "assistant" (the assistant's content includes the tool_use); ChatGPT's is "assistant" with `tool_calls` separate from `content`.
- Tool-result role: "user" (with tool_result block); ChatGPT's is "tool".

### 2.3 Gemini — `tools[0].functionDeclarations` array, `functionResponse` part

**Sending the spec** (`GeminiService.cs:195-210`):

```csharp
if (Tools.Count > 0) {
    data.Add("tools", new List<Dictionary<string, object>>(){
        new Dictionary<string, object> { { "functionDeclarations", Tools } }
    });
    if (!useFunctions) data.Add("toolConfig", new Dictionary<string, Dictionary<string, string>>() {
        { "functionCallingConfig", new() { { "mode", "NONE" } } }
    });
}
```

Two levels of wrapping: `tools` is a list with one element; that element is a dict with a `functionDeclarations` key whose value is the list of specs. Mode-mask is even deeper: `toolConfig.functionCallingConfig.mode = "NONE"`.

**Receiving the call**: Gemini's streaming JSON array contains `candidates[0].content.parts[i]` where each part is either `text` or `functionCall: {name, args}`. CDK's `GeminiStreamDownloadHandler` parses parts and routes function-call parts to setter callbacks.

**Returning the result** (`GeminiService.cs:71-74`):

```csharp
assistantMessage.parts.Add(new GeminiPart(functionCall: new GeminiFunctionCall(){
    name = llmSession.FunctionName,
    args = JsonConvert.DeserializeObject<Dictionary<string, object>>(llmSession.FunctionArguments)
}));
```

The result message has `role: "user"` (not "tool", not "assistant") with a `functionResponse` part containing `name` and `response: {result: <body>}`. Gemini's tool-result is a *part inside a user message*, not its own message kind.

### 2.4 Dify — no client-side tools (server-side)

`DifyService.cs` does not implement tool spec wire-format encoding. **Tools live on the Dify server.** CDK does not pass `Tools` to Dify; the server's own tool registry handles tool calls.

For ChatdollKit-side function-calling with Dify, the recommendation in CDK's docs is: *configure tools on Dify's web UI*. The CDK side is unaware. Output: a Dify-defined response that may include tool execution traces in the workflow event stream.

The Auditor catalogues this asymmetry at [[53_MULTI_LLM_CONSISTENCY]] — Dify breaks the symmetry of "CDK has registered tools, LLM uses them" because the server holds the tools.

### 2.5 AIAvatarKit — server-side tools with client-side notification

`AIAvatarKitService.cs` has a `HandleToolCall: Action<AIAvatarKitToolCall>` callback (line 28). When the AIAvatarKit server invokes a tool, it sends a stream event the client receives; the callback fires. The client can decide what to do (log, intervene, observe), but the *execution* is server-side.

**The client-side tool registry is bypassed.** AIAvatarKit's pipeline owns tools. The CDK side observes.

### 2.6 The divergence matrix

| Dimension | ChatGPT | Claude | Gemini | Dify | AIAvatarKit |
|---|---|---|---|---|---|
| **Spec carrier** | `tools: [{type:"function", function:{}}]` | `tools: [ClaudeTool]` | `tools: [{functionDeclarations: []}]` | Server-side | Server-side |
| **Spec params key** | `parameters` | `input_schema` | `parameters` | Server-side | Server-side |
| **Mask form** | `tool_choice: "none"` | `tool_choice: {type: "none"}` | `toolConfig.functionCallingConfig.mode: "NONE"` | n/a | n/a |
| **Call shape** | `tool_calls: [{id, function: {name, arguments}}]` | `tool_use` content block with `id`, `name`, `input` | `functionCall: {name, args}` part | Server-side | Server-side |
| **Args type** | String (deltas concatenated) | JSON `input` field accumulated as `input_json_delta` | JSON `args` object directly | n/a | n/a |
| **Result role** | `"tool"` message with `tool_call_id` | `"user"` message with `tool_result` block | `"user"` message with `functionResponse` part | (server-side response) | (callback notification) |
| **Recursive cap** | `useFunctions: false` → `tool_choice: "none"` | same | same | n/a | n/a |
| **Parallel calls** | Supported (CDK uses `[0]` only) | Supported (CDK uses first only) | Supported (CDK uses first only) | n/a | n/a |

**Five providers, five wire formats, three tool-result roles** ("tool" / "user" / nothing-because-server-side). The interface absorbs this by hiding the divergence inside each provider's adapter.

---

## 3. The Recursion Protocol

When the LLM emits a function call, CDK:

1. **Parses the call** from the stream (per-provider deltas).
2. **Matches by name** to a registered `ITool` (linear scan via `gameObject.GetComponents<ITool>()`).
3. **Executes** with the JSON arguments string and a cancellation token.
4. **Appends the result** to the session's `Contexts` list as a provider-appropriate message.
5. **Recursively re-calls** `StartStreamingAsync(session, ..., useFunctions: false, token)`.

The recursive re-call **continues the same session**. The session accumulator (`StreamBuffer`, `CurrentStreamBuffer`) carries forward — but `CurrentStreamBuffer` is reset (line 175) so the new turn's text is independent. `useFunctions: false` masks tools for the *recursive* call only; new function calls cannot happen in the same recursion frame.

**The recursion is single-tool-per-frame.** Even if the LLM emits multiple tool_calls in parallel (ChatGPT supports this), CDK handles only `tool_calls[0]`. Parallel-tool support is missing.

**The recursion depth is unbounded.** The LLM can call tools, the tools' results can prompt new tool calls (across recursive frames), and CDK has no depth limit. [[16_LLM_SERVICE_DOMAIN]] §3.4 flagged this; the interface owes the fix.

---

## 4. The Specifics — One Example Per Provider

The same `WeatherTool` (`Examples/WeatherTool.cs`) declares:
- Name: `"get_weather"`
- Description: `"Get current weather in the location."`
- One parameter: `location: string`

The wire-format on the request to each provider:

**ChatGPT** (`POST https://api.openai.com/v1/chat/completions`):
```json
{
  "model": "gpt-4o-mini",
  "messages": [...],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get current weather in the location.",
        "parameters": {
          "type": "object",
          "properties": { "location": { "type": "string" } }
        }
      }
    }
  ]
}
```

**Claude** (`POST https://api.anthropic.com/v1/messages`):
```json
{
  "model": "claude-3-haiku-20240307",
  "messages": [...],
  "tools": [
    {
      "name": "get_weather",
      "description": "Get current weather in the location.",
      "input_schema": {
        "type": "object",
        "properties": { "location": { "type": "string" } }
      }
    }
  ]
}
```

**Gemini** (`POST https://generativelanguage.googleapis.com/v1beta/.../streamGenerateContent`):
```json
{
  "contents": [...],
  "tools": [
    {
      "functionDeclarations": [
        {
          "name": "get_weather",
          "description": "Get current weather in the location.",
          "parameters": {
            "type": "object",
            "properties": { "location": { "type": "string" } }
          }
        }
      ]
    }
  ]
}
```

The result shapes are similarly divergent. The tool author wrote *one* `GetToolSpec`; the wire ships three different JSON shapes.

---

## 5. Where the Interface Strains

### 5.1 The OpenAI-canonical bias

`ILLMTool.parameters` (typed as `ILLMToolParameters`) is *exactly* OpenAI's shape. Claude needs `input_schema`; the per-provider wrapper renames at request time. Gemini also calls it `parameters` (cleaner mapping). **The canonical happens to favour two of three providers and CDK accepts the per-provider rename cost for Claude.**

For Ember: choose a *provider-neutral* canonical (`tool_spec.parameter_schema: dict`) and per-provider codecs rename to `parameters` / `input_schema` etc.

### 5.2 The single-tool-per-call assumption

`ChatGPTService.cs:355-371` iterates tools but breaks on first match. `delta.tool_calls[0]` ignores indices > 0. Parallel function calls (a single LLM turn requesting *multiple* tools) are not supported. CDK assumes one call per turn.

### 5.3 The unbounded recursion

No depth limit on the recursive `StartStreamingAsync`. Tool → tool → tool can stack-overflow.

### 5.4 The match-by-name linear scan

Each tool-execution path linearly scans `gameObject.GetComponents<ITool>()` instead of using `DialogProcessor.toolResolver` (the dictionary that exists). Inconsistent; mildly wasteful.

### 5.5 The arguments-string-not-JSON-object

The function arguments arrive as a *string* (the LLM's emitted JSON, accumulated from streaming deltas). The tool author parses with `JsonConvert.DeserializeObject<Dictionary<string, string>>`. If the LLM emits malformed JSON, the tool throws — but the throw propagates and the recursion does not recover. Defensive parse + typed exception would be cleaner.

### 5.6 The role field is ignored

`ToolResponse(body, role: "function")` — the role default. The per-provider adapter overrides with its own role ("tool" for ChatGPT, "user" for Claude/Gemini). The author's role intent is discarded. Should be removed from the contract or honoured.

### 5.7 The Dify / AIAvatarKit asymmetry

Two providers don't use the local tool registry. The contract pretends they do; the runtime does not. A new author registering a tool for Dify is silently un-effective. CDK should *signal* the asymmetry — Dify mode → disable local tool registration with a warning.

---

## 6. Cross-References

- [[19_TOOL_DOMAIN]] — the user-facing tool surface
- [[16_LLM_SERVICE_DOMAIN]] — the LLM service that drives function-calling
- [[20_LLM_SERVICE_INTERFACE]] — the interface containing `Tools` member
- [[53_MULTI_LLM_CONSISTENCY]] — Auditor's catalogue of inconsistency failures
- [[sap:19_TOOL_SURFACE]] — SAP's MCP-server tool surface for contrast
- [[waifu:24_REMOTE_ACTION_API]] — Waifu's typed-string remote actions for contrast
- [[hermes:1A_VERKFAERI_INTERFACE]] — Hermes's Verkfæri (tool True Name) interface

---

## What This Means for Ember

**Adopt:**
- The **`ITool` two-method shape** (`GetToolSpec` + `ExecuteFunction`). Ember's `Tool` Protocol: `get_spec() -> ToolSpec`, `async execute(args_json: str) -> ToolResponse`. Apache-2.0 attribution required.
- The **JSON-Schema-shaped `ToolSpec`** — name, description, parameters with type + properties. Direct lift of the canonical form; per-provider codec rewrites as needed.
- The **`ToolResponse(body, role)` value type** — but Ember adds `tool_name`, `duration_ms`, `ok`, `side_effect_class` for observability.
- The **recursive re-call with `useFunctions: false` mask** for in-frame loop prevention.

*Apache-2.0 attribution: when patterns from `ChatdollKit/Scripts/LLM/ITool.cs` and `ToolBase.cs` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:**
- The **OpenAI-canonical tool spec** to provider-neutral `ToolSpec` Pydantic model with `parameter_schema: JsonSchemaModel`. Per-provider codecs translate to `parameters` (OpenAI/Gemini) or `input_schema` (Claude).
- The **single-tool-per-call assumption** to a list-aware design. `LLMSession.tool_calls: list[ToolCall]` with `[0]` for compatibility but full list available for parallel execution. Ember provides a `ParallelToolExecutor` strategy.
- The **unbounded recursion** to a typed `tool_recursion_max: int` bound (default 5). Past the bound, raise `ToolRecursionLimitExceeded`.
- The **linear scan tool resolution** to dict lookup via the registry.

**Avoid:**
- **Arguments-string-not-object.** Ember parses to a typed object in the framework; the tool receives a typed param. The author cannot trigger a parse error inside the tool.
- **Provider asymmetry (Dify/AIAvatarKit) without explicit signalling.** Ember's provider-capability manifest declares `client_side_tools_supported: bool`; if false, tool-registration emits a warning.
- **Role field on `ToolResponse` that gets ignored.** Ember omits or honours.

**Invent:**
- **The Cross-Provider Tool Spec Codec.** A `ToolSpecCodec` Protocol with `to_chatgpt_dict(spec)`, `to_claude_dict(spec)`, `to_gemini_dict(spec)`, plus inverse `from_*_call_delta` parsers. Five codecs (one per provider); zero duplication of "tool spec" semantics. Tested with property-based testing (Hypothesis) to assert round-trip integrity per provider.
- **The Parallel-Tool-Call Strategy.** Ember can configure: `parallel_tool_strategy: "first" | "all-sequential" | "all-parallel" | "vote"`. `first` matches CDK's behaviour. `all-parallel` invokes every call concurrently and feeds results back together. `vote` runs duplicate calls and takes majority. CDK has only `first`; Ember offers four.
- **The Tool-Spec Auto-Documentation Generator.** From the registered tools' `ToolSpec`s, generate Markdown docs per realm: name, description, parameters with types, side-effect class, example calls. Reviewers can audit "what can the avatar do?" without reading code. CDK has no such generator; Ember produces it on `ember audit tools`.
- **The Tool-Call Provenance Trail.** Every tool call: `ToolCallStreamed(turn_id, tool_name, args_hash, provider, latency_to_call_ms)`, `ToolExecuted(tool_name, ok, duration_ms, result_size)`, `ToolResultFedBack(turn_id, recursion_depth)`. The session post-mortem can answer "for this turn, which tools were called, in what order, with what latency."
- **The Tool-Call Defensive Parse Vow.** The framework parses `args_json` before invoking the tool. If parse fails: emit `ToolArgsParseError`, return a typed error response to the LLM ("invalid JSON, please retry"). The tool author never sees malformed JSON. CDK propagates the throw; Ember contains it.
- **The Tool-Recursion Budget.** Each turn has a `tool_recursion_budget: int = 5` consumed once per recursion. When the budget hits zero, emit `ToolRecursionExhausted`; force the LLM to respond *without* tools for the rest of the turn. Graceful, not stack-overflow.
- **The Server-Side Tool Translation.** When Ember integrates with Dify or AIAvatarKit (server-side tool platforms), the *client-side* tools are not lost — they're surfaced to the server's tool list via a server-side adapter (a Dify plugin Ember publishes; an AAK server tool registration). The user registers tools client-side; the server hosts copies. Symmetry restored. CDK lets server-side providers diverge; Ember bridges.

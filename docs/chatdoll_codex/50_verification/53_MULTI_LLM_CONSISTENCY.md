---
codex_id: 53_MULTI_LLM_CONSISTENCY
title: Multi-LLM Consistency — Four Function-Call Schemas, One Façade, Many Leaks
role: Auditor
layer: Verification
status: draft
chatdoll_source_refs:
  - Scripts/LLM/LLMServiceBase.cs:10-100
  - Scripts/LLM/ChatGPT/ChatGPTService.cs:200-216
  - Scripts/LLM/Claude/ClaudeService.cs:40-58,73-91
  - Scripts/LLM/Gemini/GeminiService.cs:194-210
  - Scripts/LLM/Dify/DifyService.cs
  - Scripts/LLM/AIAvatarKit/AIAvatarKitService.cs:378-385
  - Scripts/LLM/ChatGPT/ChatGPTService.cs:353-372
  - Scripts/LLM/ToolBase.cs
ember_subsystem_targets: [Strengr, Smiðja, Munnr]
cross_refs:
  - 50_verification/51_SECURITY_REVIEW
  - 50_verification/57_FAILURE_TAXONOMY
  - 20_interface/26_TOOL_FUNCTION_CALL_INTERFACE
  - sap:55_API_SIMULATION_TRAPS
  - waifu:51_SECURITY_AND_PRIVACY
---

# Multi-LLM Consistency — Four Function-Call Schemas, One Façade, Many Leaks

> *Sólrún, voice cold and even: ChatdollKit advertises support for six LLM providers behind a single `ILLMService` interface. The interface is honest at the message level — `MakePromptAsync` returns `List<ILLMMessage>`, every provider implements its own message type, the contract holds. The interface is dishonest at the function-call level. ChatGPT, Claude, Gemini, Dify, and AIAvatarKit emit function calls in four mutually incompatible schemas, and the kit's tool-execution dispatcher in each per-provider service has to translate from the provider's native schema into a string-and-arguments form. The translation is hand-written, per-provider, with no shared validator. Where the translations differ, the same `ITool` can be invoked successfully against ChatGPT, silently fail against Claude, hallucinate against Gemini, or be unreachable entirely on Dify. The audit posture is: each provider is its own protocol; the façade hides this from the operator until production.*

This document maps the four function-call schemas, the four dispatch paths in CDK, and the seams where they leak provider-specific behavior. The findings matter because Ember's Smiðja (tool surface) will face the same problem if Strengr (LLM access) keeps multi-provider parity. The lesson is not *"choose one provider"* — it is *"the façade is real, but the schema divergence must be acknowledged at the contract level, not papered over."*

---

## 1. The Four Schemas

### 1.1 ChatGPT (OpenAI Chat Completions, `tools` array)

`Scripts/LLM/ChatGPT/ChatGPTService.cs:200-216`:

```csharp
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
    {
        data.Add("tool_choice", "none");
    }
}
```

Request shape: `tools: [{type: "function", function: {name, description, parameters}}]` with a separate `tool_choice` field. Response shape: `tool_calls: [{id, type: "function", function: {name, arguments}}]` where `arguments` is a **string** (JSON-encoded). Each tool call has a unique `id` that must round-trip to the `tool_call_id` on the `role: "tool"` response message.

### 1.2 Claude (Anthropic Messages, `tool_use` blocks)

`Scripts/LLM/Claude/ClaudeService.cs:40-58`:

```csharp
if (!string.IsNullOrEmpty(((ClaudeSession)llmSession).ToolUseId))
{
    assistantMessage.content.Add(new ClaudeContent()
    {
        type = "tool_use",
        id = ((ClaudeSession)llmSession).ToolUseId,
        name = llmSession.FunctionName,
        input = JsonConvert.DeserializeObject<Dictionary<string, object>>(llmSession.FunctionArguments)
    });
    llmSession.Contexts.Add(assistantMessage);
}
```

Request shape: `tools: [{name, description, input_schema: {...JSON Schema...}}]` — *no* `function` wrapper. Response shape: assistant message contains `content: [..., {type: "tool_use", id, name, input}]` where `input` is a **decoded object**, not a string. Continuation requires sending `{type: "tool_result", tool_use_id, content}` blocks as the next user-role message.

The id field is `tool_use_id` on the Claude side, `tool_call_id` on the ChatGPT side. The arguments-vs-input rename is a real divergence: Claude pre-parses, ChatGPT delegates. The `Contexts` history-management code at `ClaudeService.cs:73-91` enforces a Claude-specific invariant: every `tool_use` must be followed by `tool_result` or the API rejects the request. If CDK's history pruner removes the `tool_use` without removing the matching `tool_result`, Claude 4xx's the next turn. ChatGPT is more permissive about orphaned tool calls; the same defensive pruning is overkill there and missing-data on the Claude side leads to context-state desyncs.

### 1.3 Gemini (Google generative-ai, `functionDeclarations`)

`Scripts/LLM/Gemini/GeminiService.cs:194-210`:

```csharp
if (Tools.Count > 0)
{
    data.Add("tools", new List<Dictionary<string, object>>(){
        new Dictionary<string, object> {
            { "functionDeclarations", Tools }
        }
    });
    if (!useFunctions)
    {
        data.Add("toolConfig", new Dictionary<string, Dictionary<string, string>>()
        {
            { "functionCallingConfig", new() { { "mode", "NONE" } } }
        });
    }
}
```

Request shape: `tools: [{functionDeclarations: [...]}]` — *another* wrapper layer, this time a single-element array containing an object with a `functionDeclarations` array. Response shape: `candidates[0].content.parts[].functionCall: {name, args}` where `args` is a decoded object. **No id field at all.** Continuation: send back `functionResponse: {name, response}` — keyed by `name`, which means *if the model calls the same function twice in one turn, the responses cannot be disambiguated by id*. Gemini's contract assumes idempotent or singular function use.

### 1.4 Dify (workflow nodes — no client-side tool dispatch)

`Scripts/LLM/Dify/DifyService.cs` carries no `Tools` registration logic. Dify is a workflow-runner backend; tools are defined inside the Dify workflow, executed on the Dify server, and Dify streams *the workflow's final response* to the client. CDK's Dify integration cannot use the `ITool` mechanism at all. The `Tools` list on `LLMServiceBase` is ignored by `DifyService`.

This is the loudest leak: an operator who registers `ITool` components, switches the active LLM service from ChatGPT to Dify, and expects tools to keep working will find that *they silently do not.* No warning. No fallback. The tools are effectively dead.

### 1.5 AIAvatarKit (relay protocol, `tool_call` metadata)

`Scripts/LLM/AIAvatarKit/AIAvatarKitService.cs:378-385`:

```csharp
else if (asr.type == "tool_call")
{
    var toolCall = (asr.metadata["tool_call"] as JObject).ToObject<AIAvatarKitToolCall>();
    HandleToolCall(toolCall);
}
```

AIAvatarKit relays tool calls from an upstream provider — could be ChatGPT, could be Claude, could be a custom AutoGen agent. The schema is AIAvatarKit's own wire format: a `type: "tool_call"` event with `metadata.tool_call` payload. The translation from upstream-provider format to AIAvatarKit format happens server-side, opaque to CDK. The kit's `HandleToolCall` then dispatches to the local `ITool`, but the **upstream provider's quirks** (id semantics, arg encoding) are pre-baked into the AIAvatarKit wire format and may or may not match CDK's expectations.

---

## 2. The Translation Layer: `ITool`

`Scripts/LLM/ToolBase.cs` defines the contract:

```csharp
public virtual async UniTask<ToolResponse> ExecuteAsync(string argumentsJsonString, CancellationToken token)
{
    return await ExecuteFunction(argumentsJsonString, token);
}
```

The argument is a *string*. Every provider has to coerce its native arg format (Claude's pre-parsed dict, Gemini's decoded object, ChatGPT's already-string) into a string before calling `ExecuteAsync`. Round-trip cost:

- ChatGPT: already a string, no translation needed. **0 cost, 0 risk.**
- Claude: `JsonConvert.SerializeObject(input)` to re-encode. Adds an encode/decode round-trip. **Low cost, JSON-formatting risk** — Claude's decoded `Dictionary<string, object>` may not perfectly round-trip if it contained `JArray`/`JObject` references that serialize differently than original JSON.
- Gemini: same as Claude. Plus *no id*, so multi-tool-call disambiguation is impossible.
- Dify: not reached.
- AIAvatarKit: depends on upstream.

The string-typed `argumentsJsonString` is also a security finding (see `[[51_SECURITY_REVIEW]] §4.2`) — the tool author must parse and validate.

---

## 3. The Schema Divergence Matrix

| Concern | ChatGPT | Claude | Gemini | Dify | AIAvatarKit |
|---|---|---|---|---|---|
| Tools-array wrapper | `[{type, function}]` | `[{name, input_schema}]` | `[{functionDeclarations: [...]}]` | N/A | server-defined |
| Args encoding | string | object | object | N/A | varies |
| Call id | `id` | `id` | **none** | N/A | varies |
| Disable tools | `tool_choice: "none"` | omit `tools` | `toolConfig.mode: NONE` | N/A | varies |
| Multi-call per turn | yes, by id | yes, by id | no (no id) | N/A | varies |
| History invariant | flexible | strict pair | flexible | N/A | varies |
| Streaming chunks | SSE `data:` | SSE `event:` | SSE JSON lines | SSE | WebSocket frames |
| Cache pattern | `tool_choice: "none"` mask | omit tools | mask | N/A | varies |

The kit's per-provider service handles each cell. The handling is not always equivalent — the *behavior under tools=disabled* differs: ChatGPT and Gemini explicitly mask while preserving the tools list (cache-friendly per the comment at `ChatGPTService.cs:211`); Claude requires omission. If the operator toggles `useFunctions` mid-session, the cache-hit behavior differs across providers. The operator does not see this.

---

## 4. The Dispatcher Pattern That Leaks

`Scripts/LLM/ChatGPT/ChatGPTService.cs:353-372`:

```csharp
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

Linear scan over `GetComponents<ITool>()` per turn. O(N tools × N turns). No memoization. `useFunctions: false` is passed on the recursive call — the model cannot chain tool calls within one assistant turn. This is a *deliberate guard* against infinite-loop hallucination, but it also means the model cannot decompose a task into two parallel tool calls; it must respond, wait for the human, then call the second tool.

Claude's equivalent path in `ClaudeService.cs` differs subtly — Claude permits parallel tool calls in a single assistant message (multiple `tool_use` blocks). CDK's Claude dispatcher handles only the first tool_use in the current implementation [verified by structural read]. **The model can request three tools; the kit executes one.** Silent capability degradation.

Gemini's path: no id means the kit cannot match `functionResponse.name` back to a specific call if the model called two functions with the same name. The implementation skirts this by assuming function names are unique per turn — true in single-call cases, broken in any agentic loop.

---

## 5. The Cache-Hit Anti-Pattern

The comment at `ChatGPTService.cs:211`:

> `// Mask tools if useFunctions = false. Don't remove tools to keep cache hit and to prevent hallucination`

OpenAI charges by token. They also offer prompt caching — repeated requests with identical prefixes are billed at a discount. CDK preserves the `tools` array even when masking calls (`tool_choice: "none"`) specifically to retain cache hits. Smart.

But the same pattern is *wrong* for Claude. Claude's prompt cache works at the `system` message level; tools count as part of the cacheable prefix only if the full `tools` array is identical. Toggling `tool_choice` doesn't exist on Claude — the kit's defensive masking does nothing useful, and the cache discipline differs from ChatGPT. The kit does not document this.

Multiplied across six providers: **prompt-cache economics differ per provider**, and the kit's single `useFunctions` toggle treats them uniformly. Operators saving cents on ChatGPT may be paying full freight on Claude without realizing.

---

## 6. Failure-Mode Recital

A non-exhaustive list of cases where the multi-LLM façade leaks:

1. Operator registers three `ITool` components. Switches LLM from ChatGPT to Dify. Tools silently inert.
2. Operator switches ChatGPT → Claude. Multi-tool-call turns lose all but one tool execution.
3. Operator switches Claude → Gemini. Two tools with the same name collapse to one dispatch.
4. Operator enables `historyTurns = 100`. Claude rejects the next turn because the pruner removed a `tool_use` without its `tool_result`.
5. Operator runs `useFunctions = false` to save cost. ChatGPT caches, Claude doesn't, Gemini caches differently. Bill varies wildly.
6. Operator's tool emits a non-JSON-safe character (e.g., raw byte) in its `ToolResponse.Body`. ChatGPT happily accepts; Claude rejects on JSON schema; Gemini truncates silently.
7. Operator deploys to WebGL. AIAvatarKit's WebSocket path requires NativeWebSocket UPM package (see `[[50_DEPENDENCY_HEALTH]] §2.7`); operator missed it; WebSocket path silently falls back to non-streaming HTTP; tool-call latency increases ~3×.

The first four are documented nowhere in CDK. The fifth is a billing surprise. The sixth and seventh are debugging mysteries.

---

## 7. Cross-References

- `[[51_SECURITY_REVIEW]]` §3.3 — the prompt-injection-to-tool path is the same risk surface multiplied per provider.
- `[[57_FAILURE_TAXONOMY]]` — the ranked failure list rolls these up.
- `[[26_TOOL_FUNCTION_CALL_INTERFACE]]` (Architect-owned) — the contract-level read.
- `[[sap:55_API_SIMULATION_TRAPS]]` — SAP's ClaudeAsOpenAI / GeminiAsOpenAI shims are the *opposite* approach: hide divergence by re-emitting everything as OpenAI's schema. They have their own leaks.
- `[[waifu:51_SECURITY_AND_PRIVACY]]` — Waifu has *one* LLM (the cloud avatar's hidden one), so this whole class of problem doesn't exist.

---

## What This Means for Ember

**Adopt:** CDK's pattern of **per-provider session subclasses** (`ChatGPTSession`, `ClaudeSession`) keyed to the provider's wire format is the right shape. Hide nothing in the session — let each provider have its own state surface, even if `ILLMSession` is the common base. *Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:** CDK's `ToolBase` with `string argumentsJsonString` is the wrong shape. Ember's Smiðja tool contract should accept a *typed*, validated, deserialized `Dictionary<string, JsonValue>` (or a Pydantic model in Python, or a `serde_json::Value` in Rust) with a *schema reference* the dispatcher uses to validate before calling the tool. The tool author should never see raw strings.

**Avoid:**
- Pretending six providers are interchangeable. The façade lies. Document the matrix in §3 *as part of Strengr's contract*; the operator must opt into each provider with eyes open.
- Linear `GetComponents<ITool>()` scan per turn. Build an index at registration time.
- Silent capability degradation. If Claude allows three tools and Ember dispatches one, log a warning at WARN level and continue. If Dify allows none and tools are registered, refuse to enable that provider until tools are unregistered.

**Invent:** A **Strengr Provider Capability Matrix** declared statically. Each provider plug-in declares:

```yaml
provider: claude
capabilities:
  function_calling: true
  parallel_tool_calls: true
  call_id_required: true
  history_invariant: strict_pair
  cache_discipline: full_prefix
  streaming: sse_event
```

Strengr's dispatcher consults this matrix at boot. When tools are registered, Strengr verifies the active provider supports them and emits a structured warning per capability mismatch. The operator sees the matrix in Funi's health report. No silent inertness; no surprise bills; no debugging mysteries.

A second invention: **the cross-provider test harness**. Ember ships a test suite that runs identical multi-tool conversations against every supported provider plug-in and asserts behavioral equivalence at the *observable* level (final tool side-effects). Where providers genuinely differ (multi-tool-per-turn), the harness asserts *graceful degradation* rather than equivalence. CDK ships no such harness; every operator discovers the divergence in production.

---

*Apache-2.0 attribution: when adopting CDK-derived patterns into Ember source, preserve the ChatdollKit NOTICE or header reference per Apache-2.0 §4(c).*

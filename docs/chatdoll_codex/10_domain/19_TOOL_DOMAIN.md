---
codex_id: 19_TOOL_DOMAIN
title: Tool Domain — One Interface, One Base, Five Function-Call Wire Formats
role: Architect
layer: Domain
status: draft
chatdoll_source_refs:
  - Scripts/LLM/ITool.cs:1-26
  - Scripts/LLM/ToolBase.cs:1-46
  - Scripts/LLM/ILLMService.cs:42-58
  - Scripts/LLM/LLMServiceBase.cs:54
  - Scripts/Dialog/DialogProcessor.cs:115-128
  - Scripts/LLM/ChatGPT/ChatGPTService.cs:199-216, 353-372
  - Scripts/LLM/Claude/ClaudeService.cs:159-172
  - Scripts/LLM/Gemini/GeminiService.cs:195-210
  - Extension/ChatMemory/ChatMemoryTool.cs:1-37
ember_subsystem_targets: [Smiðja, Strengr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/16_LLM_SERVICE_DOMAIN
  - 10_domain/1A_MEMORY_DOMAIN
  - 20_interface/26_TOOL_FUNCTION_CALL_INTERFACE
  - sap:19_TOOL_SURFACE
  - waifu:24_REMOTE_ACTION_API
---

# Tool Domain
## One Interface, One Base, Five Function-Call Wire Formats

*— Rúnhild Svartdóttir, Architect*

> *A tool is a verb the avatar can speak that has consequences in the world. The contract for "what is a tool" must be small. The contract for "how does each LLM ask for one" cannot be, because the LLM vendors do not agree. ChatdollKit splits these two contracts and refuses to conflate them. This is correct.*

`Scripts/LLM/ITool.cs` (26 LOC) and `Scripts/LLM/ToolBase.cs` (46 LOC) together comprise the *user-facing* function-calling surface of ChatdollKit. Seventy-two lines. The smallest domain in this codex by file count. The largest in *consequence per line of code* — because the same seventy-two lines route through five different LLM providers' function-call wire formats and integrate via Unity's `GetComponents<ITool>()` runtime discovery.

The domain teaches two architectural lessons in three classes. **One**: separate the user-supplied tool *implementation* (`ToolBase` subclass with `GetToolSpec` + `ExecuteFunction`) from the per-provider *wire-format adapter* (the function-call translation inside each `LLMService`). **Two**: discover tools at runtime by component scan; do not register them in a global table. Both decisions are downstream of Unity's substrate, but both *translate* to non-Unity runtimes if Ember chooses to keep them.

Compare SAP's tool surface ([[sap:19_TOOL_SURFACE]]) — MCP-server-based, network-mediated, language-agnostic. Compare Waifu's remote-action API ([[waifu:24_REMOTE_ACTION_API]]) — typed string commands (`dance`, `wave_hand`, `embarrassed`) with no parameters and no return value. **CDK sits between**: in-process function calls with typed JSON parameters and structured return values, but no cross-process tool model. The trade is *latency-friendly* (no network hop) and *deployment-coupled* (tools ship with the avatar binary).

---

## 1. The Subject Itself

**What the domain is:** the contract that turns *user-side application code* into *LLM-callable functions*. The user writes a `MyTool : ToolBase` class with two overridden methods. The LLM emits a function-call. The right `MyTool` instance executes. The result feeds back into the LLM's context. The avatar speaks the result.

**What it owns:**

| File | LOC | Owns |
|---|---|---|
| `ITool.cs` | 26 | The interface: `IsEnabled`, `GetToolSpec()`, `ProcessAsync(...)` (legacy), `ExecuteAsync(argsJson, token)`. Plus `ToolResponse` value class |
| `ToolBase.cs` | 46 | The abstract MonoBehaviour parent: default-true `IsEnabled`, the `ExecuteAsync → ExecuteFunction` indirection (migration scaffold), exception throws for unimplemented overrides |
| `ILLMService.Tools` property | (in ILLMService.cs:12) | The list-of-tools the active LLM service is told about per turn |
| `DialogProcessor.LoadLLMTools` | (in DialogProcessor.cs:115-128) | The tool-discovery scan: enumerate `GetComponents<ITool>()`, filter enabled, materialise specs |

**What it does NOT own:**
- The *implementations* — user code in subclasses of `ToolBase`. CDK ships *one* example tool (`Extension/ChatMemory/ChatMemoryTool.cs`, 37 LOC) and expects users to write the rest.
- The *per-provider wire format* — that's spread across the five `*Service.cs` files in `Scripts/LLM/<Vendor>/`, each translating the shared `ILLMTool` spec into the vendor's JSON shape. The full catalogue is at [[26_TOOL_FUNCTION_CALL_INTERFACE]].
- Tool *invocation policy* — when to call a tool, how to confirm side-effects, whether to gate destructive operations — none of that is in CDK. The LLM decides; CDK ferries. This is a real gap; Ember closes it (see Invent).
- Cross-process tools (no MCP, no A2A). All tools are in-process Unity components.

---

## 2. How It Works

### 2.1 The `ITool` interface

`Scripts/LLM/ITool.cs:7-14`:

```csharp
public interface ITool
{
    bool IsEnabled { get; set; }
    ILLMTool GetToolSpec();
    UniTask<ILLMSession> ProcessAsync(ILLMService llmService, ILLMSession llmSession, Dictionary<string, object> payloads, CancellationToken token);
    UniTask<ToolResponse> ExecuteAsync(string argumentsJsonString, CancellationToken token);
}

public class ToolResponse
{
    public string Body { get; protected set; }
    public string Role { get; protected set; }
    public ToolResponse(string body, string role = "function") { ... }
}
```

Three methods of substance: `GetToolSpec` returns the *typed description* the LLM sees (function name + parameters JSON schema), `ExecuteAsync` runs the tool given its JSON arguments and returns the response body, and `ProcessAsync` is a *legacy migration scaffold* (`ToolBase.cs:27-31` returns null). New tools implement `GetToolSpec` and `ExecuteFunction`; `ExecuteAsync` and `ProcessAsync` are inherited from `ToolBase` and do the right thing.

`ToolResponse.Role` defaults to `"function"` — the OpenAI convention. For Claude (which uses `"tool"` role) and Gemini (which uses `"function"` parts inside a `user` message), the per-provider adapter translates. The role string is exposed on the contract but most tools don't set it; the adapter overrides as needed.

### 2.2 The `ToolBase` abstract parent

`Scripts/LLM/ToolBase.cs:9-46`:

```csharp
public class ToolBase : MonoBehaviour, ITool {
    public bool _IsEnabled = true;
    public bool IsEnabled { get { return _IsEnabled; } set { _IsEnabled = value; } }

    public virtual ILLMTool GetToolSpec() {
        throw new NotImplementedException("ToolBase.GetToolSpec must be implemented");
    }

    public async UniTask<ILLMSession> ProcessAsync(ILLMService llmService, ILLMSession llmSession, Dictionary<string, object> payloads, CancellationToken token) {
        // Migration scaffold; v0.7.x compat
        return null;
    }

    public virtual async UniTask<ToolResponse> ExecuteAsync(string argumentsJsonString, CancellationToken token) {
        return await ExecuteFunction(argumentsJsonString, token);
    }

    protected virtual async UniTask<ToolResponse> ExecuteFunction(string argumentsJsonString, CancellationToken token) {
        throw new NotImplementedException("ToolBase.ExecuteFunction must be implemented");
    }
}
```

Two `NotImplementedException`s that compile-time mark the required overrides. The `ExecuteAsync → ExecuteFunction` two-level indirection is a v0.7.x migration scaffold — old tools overrode `ExecuteAsync` directly; new tools override `ExecuteFunction` and inherit the `ExecuteAsync` wrapper. The pattern keeps backward compatibility for one version cycle. Honest engineering; not free architecture.

`IsEnabled` defaults `true`. A tool registered on the GameObject is *active* unless explicitly disabled. Combined with `DialogProcessor.LoadLLMTools`'s `if (tool.IsEnabled)` filter (line 121), this means **tools are opt-out at the component level**. Ember's posture should be **opt-in** for any tool with side effects.

### 2.3 The runtime discovery in `DialogProcessor.LoadLLMTools`

`Scripts/Dialog/DialogProcessor.cs:115-128`:

```csharp
public void LoadLLMTools() {
    toolResolver.Clear();
    toolSpecs.Clear();
    foreach (var tool in gameObject.GetComponents<ITool>()) {
        if (tool.IsEnabled) {
            var toolSpec = tool.GetToolSpec();
            toolResolver.Add(toolSpec.name, tool);
            toolSpecs.Add(toolSpec);
        }
    }
}
```

`gameObject.GetComponents<ITool>()` returns every component implementing the interface on the same GameObject. Filter by `IsEnabled`. Build a name-to-instance dictionary (`toolResolver`) and a list of specs (`toolSpecs` — sent to the LLM). Called by `DialogProcessor.StartDialogAsync` before each turn (around line 171 — `llmService.Tools = toolSpecs`).

**Per-turn refresh.** If the user toggles a tool's `IsEnabled` mid-session, the next turn picks it up. Hot-swap tools without restart. This is the same component-scan pattern as `SelectLLMService` and `SelectSpeechSynthesizer` — Unity's component model as the registration mechanism, *consistently across the codebase*.

For Ember without Unity: the equivalent is a `tool_registry: dict[str, Tool]` populated by `@register_tool` decorators on import, with a runtime `enabled: bool` toggle per tool and a per-turn refresh. Same pattern, idiomatic Python.

### 2.4 The execution path in a provider

The tool-execution branch in `ChatGPTService.cs:353-372`:

```csharp
if (!string.IsNullOrEmpty(chatGPTSession.ToolCallId)) {
    foreach (var tool in gameObject.GetComponents<ITool>()) {
        var toolSpec = tool.GetToolSpec();
        if (toolSpec.name == chatGPTSession.FunctionName) {
            Debug.Log($"Execute tool: {toolSpec.name}({chatGPTSession.FunctionArguments})");
            var toolResponse = await tool.ExecuteAsync(chatGPTSession.FunctionArguments, token);
            chatGPTSession.Contexts.Add(new ChatGPTFunctionMessage(toolResponse.Body, chatGPTSession.ToolCallId));
            chatGPTSession.ToolCallId = null;
            chatGPTSession.FunctionName = null;
            chatGPTSession.FunctionArguments = null;
            // Call recursively with tool response, with useFunctions: false
            await StartStreamingAsync(chatGPTSession, customParameters, customHeaders, false, token);
        }
    }
}
```

Five steps: (1) detect the LLM's function-call from the stream, (2) match by name against registered tools, (3) execute with the JSON arguments string, (4) append the response to context, (5) recursively re-call the LLM with `useFunctions: false` so the model doesn't immediately re-call the same tool.

**The match-by-name scan is per-call.** Linear search over `GetComponents<ITool>()`. For ~10 tools, microseconds. For 100 tools, still microseconds. `DialogProcessor`'s `toolResolver` dictionary exists but isn't used here — the provider does its own scan. Inconsistent; the dictionary lookup would be faster *and* idiomatic. Ember should use the registry consistently.

**The `useFunctions: false` recursive mask** is a defensive measure against single-turn infinite recursion. The LLM cannot immediately re-call tools in the same recursion frame. But it *can* call new tools in subsequent turns. And the recursion has no depth bound (see [[16_LLM_SERVICE_DOMAIN]] §3.4).

### 2.5 The per-provider wire-format translation

The `ILLMTool` is a *common typed spec*; the wire format per provider differs. ChatGPT's encoding (`ChatGPTService.cs:199-216`):

```csharp
if (Tools.Count > 0) {
    var tools = new List<Dictionary<string, object>>();
    foreach (var tool in Tools) {
        tools.Add(new Dictionary<string, object>() {
            { "type", "function" },
            { "function", tool }
        });
    }
    data.Add("tools", tools);
    if (!useFunctions) data.Add("tool_choice", "none");
}
```

Claude's encoding (`ClaudeService.cs:159-172`):

```csharp
if (Tools.Count > 0) {
    var claudeTools = new List<ClaudeTool>();
    foreach (var tool in Tools) claudeTools.Add(new ClaudeTool(tool));
    data.Add("tools", claudeTools);
    if (!useFunctions) data.Add("tool_choice", new Dictionary<string, string>(){ {"type", "none"} });
}
```

Gemini's encoding (`GeminiService.cs:195-210`):

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

Three different JSON shapes. ChatGPT wraps each tool in `{type: "function", function: ...}`. Claude has a `ClaudeTool` wrapper class with provider-specific schema fields. Gemini wraps the list under `functionDeclarations` inside a `tools[0]` object. The `tool_choice: "none"` masking has three different JSON encodings. **The translation lives in each provider, not in a shared adapter.** This is the same trade as the context-history hygiene (see [[16_LLM_SERVICE_DOMAIN]] §3.2): per-provider clarity over shared-template subtlety. Ember should evaluate whether a shared `ToolSpecCodec[Provider]` template-method base class is worth the abstraction cost.

The full per-provider comparison is at [[26_TOOL_FUNCTION_CALL_INTERFACE]].

### 2.6 The one shipped tool — `ChatMemoryTool`

`Extension/ChatMemory/ChatMemoryTool.cs` (37 LOC) is CDK's only shipped tool. It serves three purposes simultaneously: documentation-by-example, an actually-useful memory search function, and a demonstration of tool-LLM-cycle:

```csharp
public override ILLMTool GetToolSpec() {
    var func = new LLMTool(FunctionName, FunctionDescription);
    func.AddProperty("query", new Dictionary<string, object>() { { "type", "string" } });
    return func;
}

protected override async UniTask<ToolResponse> ExecuteFunction(string argumentsJsonString, CancellationToken token) {
    var arguments = JsonConvert.DeserializeObject<Dictionary<string, string>>(argumentsJsonString);
    var searchResponse = await chatMemoryIntegrator.SearchMemory(arguments["query"], include_retrieved_data: IncludeRetrivedData);
    return new ToolResponse(JsonConvert.SerializeObject(searchResponse.result));
}
```

`GetToolSpec` declares one parameter (`query: string`). `ExecuteFunction` parses arguments, calls the integrator, serialises the result. **The pattern is a four-line spec + five-line execute.** Adopt this shape for Ember's first tools: declare the schema, parse args, call backing service, serialise response.

Note: the tool depends on `ChatMemoryIntegrator` being attached to the same GameObject (`gameObject.GetComponent<ChatMemoryIntegrator>()` in `Start`). The dependency is **runtime-resolved by Unity component lookup**. In Python, the equivalent is a constructor-injected `chat_memory: ChatMemoryClient` or a registry lookup. Either is cleaner than CDK's implicit binding.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 No consent gate for side-effects

A `ToolBase` subclass that deletes a file does so the moment the LLM calls it. There is **no confirmation step**. SAP's MCP has tool-level approval rules; CDK has nothing. For Ember, *consent-gated tool execution* is mandatory for any tool with side effects beyond memory-read.

### 3.2 No tool-result validation

`ToolResponse.Body` is a string the tool returns. CDK passes it back to the LLM as-is. If a tool returns 1MB of JSON, the LLM's context window is consumed. If a tool returns `null`, the assistant message ends up with empty content and the LLM may hallucinate. Ember should validate (max size, non-empty, JSON-well-formed) before re-calling.

### 3.3 The component-scan is GameObject-scoped

`gameObject.GetComponents<ITool>()` only finds tools on the *same* GameObject as the `DialogProcessor`. Tools on sibling GameObjects are invisible. This is fine for CDK's prefab-based deployment (everything lives on one AIAvatar prefab) but constrains architectural choices. Ember's tool registry should be process-global with optional scoping.

### 3.4 The `IsEnabled` flag default is wrong

Defaulting `IsEnabled = true` (`ToolBase.cs:11`) means a tool registered for testing accidentally ships enabled in production. Ember's posture: tools default disabled; `enabled: true` is explicit per deployment YAML.

### 3.5 The legacy `ProcessAsync` migration scaffold leaks

`ProcessAsync` returns `null` and is no-longer-the-recommended-override but still on the interface. Tool authors confronted with two methods waste time picking the right one. Ember should clean this up at API design time, before shipping.

### 3.6 No tool-call telemetry

CDK logs `Debug.Log($"Execute tool: ...")` and that's it. No record of arguments-vs-result, no per-tool latency tracking, no failure rates. Ember emits `ToolInvoked(name, args_hash, duration, ok)` Sögumiðla events per call. Observability of the avatar's tool use is first-class.

### 3.7 The recursive tool call has no depth bound

Documented in [[16_LLM_SERVICE_DOMAIN]] §3.4. Repeated here because it's a *tool*-domain failure too: a tool that returns "please call yourself with these new args" can stack-overflow CDK. Ember bounds depth.

### 3.8 The crisp parts

- **Two-method `ITool` contract.** `GetToolSpec` + `ExecuteFunction`. Smallest viable surface.
- **Runtime discovery via component scan.** Per-turn refresh. Hot-swap tools.
- **`ToolResponse` as the response value type.** Body + role. Translates across providers.
- **The shipped-example tool** (`ChatMemoryTool`) — small, clear, idiomatic. Documentation-by-example done right.
- **The `useFunctions: false` recursive guard.** Crude but defensive. Stops single-turn loops.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §3 — LLM subsystem includes ITool/ToolBase
- [[16_LLM_SERVICE_DOMAIN]] §2.6 — tool-call recursion in the LLM service
- [[1A_MEMORY_DOMAIN]] — `ChatMemoryTool` is the example
- [[20_LLM_SERVICE_INTERFACE]] — `Tools` property on `ILLMService`
- [[26_TOOL_FUNCTION_CALL_INTERFACE]] — full per-provider function-call format catalogue
- [[sap:19_TOOL_SURFACE]] — SAP's MCP-server tool surface (network-mediated)
- [[waifu:24_REMOTE_ACTION_API]] — Waifu's typed-string remote actions (no parameters)
- [[hermes:1A_VERKFAERI_DOMAIN]] — Hermes's Verkfæri (the tool True Name); structural sibling

---

## What This Means for Ember

**Adopt:**
- The **`ITool` two-method shape** (`Scripts/LLM/ITool.cs:7-13`). Ember's `Tool` Protocol: `is_enabled: bool`, `get_spec() -> ToolSpec`, `async execute(args_json: str, token) -> ToolResponse`. Apache-2.0 attribution required.
- The **`ToolResponse(body, role)` value class** (`Scripts/LLM/ITool.cs:15-25`). Ember's `ToolResponse` dataclass with the same two fields plus `tool_name`, `duration_ms`, `ok: bool` for observability.
- The **per-turn refresh of tool list** (`Scripts/Dialog/DialogProcessor.cs:115-128`). Ember's `DialogPipeline.before_turn(...)` reloads enabled tools from the registry; toggling `enabled` takes effect on the next turn.
- The **example-tool-as-documentation pattern**. Apache-2.0 attribution required. Ember ships `EmberToolExample` with a four-line spec and five-line execute, modelled directly on `ChatMemoryTool.cs:22-35`.

*Apache-2.0 attribution: when patterns from `ChatdollKit/Scripts/LLM/ITool.cs` and `ToolBase.cs` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:**
- The **`gameObject.GetComponents<ITool>()` discovery pattern**. Adapt as Python decorator-based registration: `@register_tool` on the class definition adds to a process-global `tool_registry: dict[str, type[Tool]]`. The registry is *the* discovery mechanism; no implicit GameObject locality.
- The **`IsEnabled = true` default**. Adapt as `enabled: bool = False` default. Explicit opt-in per deployment YAML. The blast-radius of "tool accidentally shipped active" is too large to default-on.
- The **`useFunctions: false` recursive mask**. Adapt as Ember's `tool_recursion_max: int = 5` typed bound. Hard fail past the bound; emit `ToolDepthExceeded` event.
- The **per-provider tool-spec wire-format translation**. Adapt as Ember's `ToolSpecCodec` template-method base class with `to_chatgpt_dict()`, `to_claude_dict()`, `to_gemini_dict()` overrides on a *shared* base. Reduces five copies of the wrapping JSON to one declared schema with three small translation methods.

**Avoid:**
- **Side-effect tools without consent gates.** Ember's `Tool` declares `side_effect_class: enum {None, ReadOnly, WriteScoped, WriteUnscoped, Destructive}`. The dialog orchestrator gates execution: `None`/`ReadOnly` runs free; `WriteScoped` runs with logging; `WriteUnscoped` and `Destructive` require a *consent dialog* surfaced to the user (or pre-authorised in config).
- **The legacy `ProcessAsync` slot.** Ember's `Tool` Protocol has exactly two abstract methods. No migration scaffold; no two-level indirection.
- **Logging tool execution with `Debug.Log` only.** Ember emits structured `ToolInvoked` events; the user can review every tool call after the session.
- **Linear-scan tool resolution per call.** Use the registry dict.

**Invent:**
- **The Tool Consent Class.** Every Ember `Tool` declares its side-effect class. The orchestrator routes accordingly: `None` runs immediately; `WriteScoped` runs and logs; `WriteUnscoped`/`Destructive` requires a Sögumiðla-mediated consent gate (UI prompt, voice confirmation, pre-authorised allow-list). CDK has *no* gradation; Ember has five.
- **The Tool Result Validation Vow.** Before feeding a tool result back to the LLM, the orchestrator validates: max size (default 8KB), non-empty, JSON-well-formed (if claimed), schema-compliant (if the tool declared an output schema). Failures emit `ToolResultInvalid` and become typed error responses, not silent corruption.
- **The Tool Provenance Trail.** Every `ToolInvoked` event captures: `tool_name`, `args_hash` (not args themselves — privacy), `result_size`, `duration_ms`, `ok`, `side_effect_class`, `consent_source` (auto / user-prompted / config-allowed). The session post-mortem can answer *why did the avatar do X* across every tool call.
- **The Tool Dry-Run Vow.** Every `Tool` implements `async dry_run(args_json) -> str` returning a *human-readable description* of what the execute would do. The consent dialog surfaces this. *"Send email 'Reschedule meeting' to alice@example.com"* not *"call send_email tool"*. CDK has no dry-run concept; Ember makes it mandatory for destructive tools.
- **The Cross-Provider Tool Codec.** Single `ToolSpec` declaration; three encoder methods (`to_chatgpt`, `to_claude`, `to_gemini`); zero per-provider duplication. Test once with property-based testing (Hypothesis). One declaration, all providers.
- **The Tool Capability Negotiation.** When a tool requires a feature not supported by the active LLM (Claude tool-use disabled, Gemini parallel-tool-call), the orchestrator either short-circuits the tool (fall back to a non-tool path) or fails with `ToolCapabilityMismatch`. CDK assumes every provider supports every tool; Ember knows the matrix.
- **The Tool Manifest Document.** Each Ember tool has a `docs/tools/<name>.md` that declares: purpose, parameters, side-effect class, expected output, failure modes, security considerations, version. Mandatory on PR. The `SUBSYSTEM.md` rite from [[10_DOMAIN_MAP]] §invent generalises to tools.

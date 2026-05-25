---
codex_id: 64_FUNCTION_CALLING_FOR_EMBODIED
title: Function Calling for the Embodied Agent — Tools as Voice-Issued Commands, Consent-Gated, Across Six Providers and Three Wire Formats
role: Cartographer
layer: Synthesis
status: draft
cdk_source_refs:
  - /tmp/ChatdollKit/Scripts/LLM/ITool.cs:1-26
  - /tmp/ChatdollKit/Scripts/LLM/ToolBase.cs:1-46
  - /tmp/ChatdollKit/Scripts/LLM/LLMServiceBase.cs:1-175
  - /tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:199-216
  - /tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:273-286
  - /tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:353-372
  - /tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:476-487
  - /tmp/ChatdollKit/Scripts/LLM/Claude/ClaudeService.cs:159-172
  - /tmp/ChatdollKit/Scripts/LLM/Claude/ClaudeService.cs:293-311
  - /tmp/ChatdollKit/Scripts/LLM/Claude/ClaudeService.cs:395-414
  - /tmp/ChatdollKit/Scripts/LLM/Gemini/GeminiService.cs:194-208
  - /tmp/ChatdollKit/Scripts/LLM/Gemini/GeminiService.cs:435-440
  - /tmp/ChatdollKit/Scripts/Dialog/DialogProcessor.cs:115-128
  - /tmp/ChatdollKit/Scripts/Dialog/DialogProcessor.cs:171
ember_subsystem_targets: [Smiðja, Strengr, Hjarta, Munnr, Hugarsýn]
cross_refs:
  - 60_TRIANGULATION
  - 63_MULTIMODAL_PIPELINE
  - 65_MEMORY_INTEGRATION
  - chatdoll:16_LLM_SERVICE_DOMAIN
  - chatdoll:19_TOOL_DOMAIN
  - chatdoll:20_LLM_SERVICE_INTERFACE
  - chatdoll:26_TOOL_FUNCTION_CALL_INTERFACE
  - chatdoll:36_FUNCTION_CALL_EXEC
  - chatdoll:53_MULTI_LLM_CONSISTENCY
  - sap:20_MCP_INTEGRATION
  - sap:29_TOOL_TYPE_INTERFACE
  - waifu:22_ACTION_PROTOCOL
  - hermes:Verkfæri
  - ember:RULES.AI
  - ember:PHILOSOPHY
---

# 64 — Function Calling for the Embodied Agent

> *A tool call from a doll is not the same as a tool call from a CLI. The doll says "turn off the light" and the room dims; the consent gate is the only thing between the voice in the air and the actuator in the wall.*
> — Védis Eikleið, watching three JSON schemas argue about who carries the call-id

## 0. Posture — why the embodied case is structurally different

Function calling, as an abstract LLM capability, is well-studied. *Embodied* function calling is not. The difference is the gate: when the agent has a voice and a face, the user issues commands in the spoken register, the agent's reply is *also* in the spoken register, and the side-effect — the actual tool execution — happens in physical or operational space. The call is mediated by speech on the way in and by speech on the way out. The audit trail is *the agent's voice itself*, plus whatever Hjarta logs.

This doc maps the embodied function-calling problem along two axes that the prior codexes touched but did not formalise:

1. **The format-divergence axis.** Six LLM providers, three structurally different wire formats. CDK's `LLMServiceBase` family is the cleanest tutorial I have seen on what "tool calling" actually costs to abstract.
2. **The consent-gating axis.** The Surface-Without-Surveillance Vow and the Affective-Restraint Vow both bear on tool execution. A voice command from the operator is a *request* to execute, not an *authorisation*; the consent contract sits between request and execution.

CDK names the format problem and largely solves it. CDK does not name the consent problem at all — its `Debug.Log($"Execute tool: ...")` (`ChatGPTService.cs:360`) is the entire audit surface, and the tool either runs or doesn't. SAP's MCP path (`[[sap:20_MCP_INTEGRATION]]`) names the *plumbing* (server URLs, transports) but also does not name consent in the embodied register. This doc draws the map and proposes the missing layer.

I walk the three wire formats. I name what survives abstraction and what doesn't. I propose `Smiðja.invoke()` as the Ember-side surface. I argue for `Smiðja.consent_gate` as a first-class node between Strengr's tool-call detection and the actual execution, with five named consent classes. I propose the Tool Manifest as the canonical artifact every tool ships, and I propose the Receipt as what every execution returns. I close with the question CDK does not ask: *if the user can't see the tool list, did they consent to the tool surface?*

## 1. The three wire formats, side by side

CDK's `Scripts/LLM/` tree holds three structurally different function-call wire formats and one common C# abstraction. The full comparison, derived from reading `ChatGPTService.cs:199-487`, `ClaudeService.cs:159-414`, and `GeminiService.cs:194-440`:

| Concern | ChatGPT (OpenAI-compat) | Claude (Anthropic) | Gemini (Google) |
|---|---|---|---|
| Tools wire shape | `tools: [{type: "function", function: {name, description, parameters}}]` (`ChatGPTService.cs:199-216`) | Top-level `tools: [ClaudeTool...]` (`ClaudeService.cs:159-172`) | Nested `tools: [{function_declarations: [...]}]` |
| Disable-tools shape | `tool_choice: "none"` (string) (`ChatGPTService.cs:214`) | `tool_choice: {type: "none"}` (object) (`ClaudeService.cs:172`) | `functionCallingConfig: {mode: "NONE"}` |
| Stream-event for call start | `delta.tool_calls[0]` has `id` + `function.name` (`ChatGPTService.cs:478-486`) | `content_block_start` with `content_block.type == "tool_use"` (`ClaudeService.cs:395-401`) | `candidates[0].content.parts[0].functionCall` arrives complete (`GeminiService.cs:435-440`) |
| Stream-event for arguments | `delta.tool_calls[0].function.arguments` — *incremental string fragments* (`ChatGPTService.cs:482`) | `content_block_delta` with `delta.type == "input_json_delta"`, `delta.partial_json` — *incremental string fragments* (`ClaudeService.cs:404-407`) | No streaming — args arrive *whole* as JSON object (`GeminiService.cs:439`) |
| Call ID | `tool_calls[0].id` (unique per call) | `content_block.id` (unique per call) | **No ID** — Gemini emits only name + args (`GeminiService.cs:437`) |
| Result message role | `"tool"` with `tool_call_id` reference (`ChatGPTFunctionMessage`) | `"user"` with `tool_result` content block keyed by `tool_use_id` (`ClaudeMessage` at `ClaudeService.cs:48-51`, `:293-311`) | `"function"` part with `functionResponse` containing `name` + `response` |
| Parallel tool calls | Yes — multiple `tool_calls[]` entries | Yes — multiple `tool_use` blocks | Theoretically; CDK's adapter (`FunctionName` single field) cannot represent it |
| Arguments delivery mode | streamed string, accumulated | streamed string, accumulated | atomic JSON object |
| Server-set vs client-set ID | Server-set | Server-set | None |

Three different mental models for *the same operation*:

- **ChatGPT** thinks of tool calls as *one of two streamed content kinds* (text or tool-call), with the tool-call kind carrying its own incremental JSON arguments.
- **Claude** thinks of tool calls as *content blocks* in a typed block stream, where each block has a type (`text`, `thinking`, `tool_use`) and is opened, deltaed, and closed.
- **Gemini** thinks of tool calls as *complete part objects* inside a streamed candidate, with no internal streaming of the call itself.

The C# code unifies these into a single `ILLMSession`-with-`FunctionName`/`FunctionArguments`/`ToolCallId` (`ChatGPTService.cs:282`, `ClaudeService.cs:298`) only by reducing to the lowest-common-denominator model: *one tool call per turn, name + args + optional ID*. CDK's recursive `StartStreamingAsync(..., useFunctions=false, ...)` (`ChatGPTService.cs:368`) is the loop-breaker that makes this LCD safe.

The cost of LCD: CDK cannot exercise parallel tool calls. ChatGPT and Claude both support N tool calls in one assistant turn; CDK serialises them to one. This is fine for embodied use cases (a doll rarely needs to call three tools at once) but it is a real ceiling.

## 2. The C# unifying surface — `ITool` and the adapter pattern

CDK's `ITool` interface, in full, is twelve lines (`/tmp/ChatdollKit/Scripts/LLM/ITool.cs:7-13`):

```csharp
public interface ITool
{
    bool IsEnabled { get; set; }
    ILLMTool GetToolSpec();
    UniTask<ILLMSession> ProcessAsync(ILLMService llmService, ILLMSession llmSession,
                                       Dictionary<string, object> payloads, CancellationToken token);
    UniTask<ToolResponse> ExecuteAsync(string argumentsJsonString, CancellationToken token);
}
```

Three things a tool does: *describes itself*, *executes given a JSON string*, returns a typed `ToolResponse(Body, Role)`. The `ProcessAsync` is a deprecated v0.7 migration stub (`ToolBase.cs:27-30`). Total developer surface: name, description, parameters schema, and an `ExecuteFunction(argumentsJsonString, token)` override.

The discovery side is symmetric (`DialogProcessor.cs:115-128`):

```csharp
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

A scene-level walk discovers every `ITool` MonoBehaviour, keeps the enabled ones, and assigns the spec list to the LLM service (`DialogProcessor.cs:171` — `llmService.Tools = toolSpecs;`). The operator opens the Inspector to add or remove tools; there is no central registry file.

This is the cleanest auto-discovery shape across the three codexes. SAP's MCP path requires a YAML config of MCP server URLs and an explicit handshake; Waifu has no tool surface at all (the vendor SDK owns it). CDK's "drop a MonoBehaviour into the scene" is operator-facing in a way the others are not.

Compare with `[[hermes:Verkfæri]]`'s PROPOSED True Name for tools. Hermes proposed the name; CDK shows what the *shape* looks like. The Ember-side proposal in §6 reconciles the two.

## 3. The execute-then-recurse loop — and what it costs

When a stream ends with `ToolCallId` set, CDK's LLM service finds the tool by name and runs it (`ChatGPTService.cs:353-372`):

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
            // ...
            await StartStreamingAsync(chatGPTSession, customParameters, customHeaders, false, token);
        }
    }
}
```

The recursive call with `useFunctions=false` is structurally elegant — the same code path handles "compose a natural-language response with the tool result in context" — but it carries five surfaces Ember must name:

1. **Silent fall-through on name mismatch.** If the LLM emits a tool name that doesn't match any registered tool, the loop completes without executing anything. No error event fires. The next streaming call never happens. The dialog state stays at `Processing` until `OnEndAsync` cleans up. From the operator's point of view, the doll said "I'll check the weather" and then froze. This is the most failure-prone surface in the entire pipeline.

2. **Plaintext argument logging.** `Debug.Log($"Execute tool: {toolSpec.name}({chatGPTSession.FunctionArguments})")` ships passwords, API keys, and any other sensitive arguments to Unity's console. In an editor build the operator can read them; in a player build they go to `Player.log` on disk. The audit surface and the log surface are the same surface, and the surface is unscoped.

3. **Linear `GetComponents<ITool>()` per call.** Acceptable at 5 tools; acceptable at 20; degrades at 100; pathological at 1000. The `toolResolver` dictionary built in `LoadLLMTools` is *not* consulted in the execute path — the execute path walks the components again. Easy fix; not yet fixed in v0.8.16.

4. **No per-call timeout.** `ExecuteAsync(arguments, token)` accepts a cancellation token from the dialog state machine, but the dialog state machine does not enforce a per-tool budget. A slow tool (a third-party API at the wrong moment) holds the avatar in Processing for as long as it takes. The user-visible animation is the only progress indication.

5. **No depth limit across turns.** Within a turn, only one tool runs (the recursion has `useFunctions=false`). But if the tool's result triggers the LLM to *want* another tool on the next turn, and the operator says nothing to break the cycle, the loop continues indefinitely. CDK's per-turn one-tool policy is conservative; the across-turns unlimited policy is not.

Each of these costs is a *Vow surface* for Ember. The Smiðja layer I propose in §6 names all five.

The Claude version (`ClaudeService.cs:293-311`) is structurally identical with role-shape differences. The Gemini version (similar shape, `GeminiService.cs` near `:480`) drops the call-id check because Gemini has none. Three adapters, three subtly different return-message constructors, one shared cost structure.

## 4. Cross-codex comparison — MCP, ActionAPI, Smiðja

The three corpora hold three different mental models of what a *tool* is to an embodied agent:

| Aspect | SAP (MCP path, `[[sap:20_MCP_INTEGRATION]]`) | Waifu (`[[waifu:22_ACTION_PROTOCOL]]`) | CDK (`Scripts/LLM/ITool.cs`) |
|---|---|---|---|
| Tool surface | MCP server(s) declared in config; each server exposes N tools | Closed typed enum baked into vendor SDK (`runAction("embarrassed"\|"dance"\|"wave_hand")`) | Local MonoBehaviours implementing `ITool`, scene-discovered |
| Tool execution locality | Remote — MCP server runs the tool out-of-process | Inside the vendor SDK; host code never sees the tool body | Local — in-process `ExecuteAsync` call on the same Unity scene |
| Transport | stdio, SSE, HTTP — MCP-defined | Vendor-defined; opaque | C# method call, no network involved (unless the tool itself reaches out) |
| Discovery | Server handshake on MCP connect | Hardcoded in the kit | `GetComponents<ITool>()` scene walk |
| Identity / auth | Per MCP server, varies | None (vendor handles internally) | None (in-process trust) |
| Result format | MCP-defined typed result objects | Three opaque enum values, no result | `ToolResponse(Body, Role)` — body is a string |
| Per-tool consent surface | Configurable in MCP config; opaque to user | Vendor decides; no surface | None — tool runs if registered and selected |

Three corpora, three different bets:

- **SAP bets on protocol** — MCP is an external standard. Multiple servers compose. Tools can be remote, distributed, polyglot. The cost: configuration ceremony, transport complexity, identity-and-auth-per-server.
- **Waifu bets on closure** — fixed action vocabulary at the vendor boundary. No flexibility, no surprise. The cost: cannot extend without vendor cooperation; the doll cannot turn off the light because the vendor never added a `controlLight()` action.
- **CDK bets on locality** — tools are MonoBehaviours in the same Unity scene. No transport. No discovery handshake. The cost: every tool is a Unity component; remote tools require a tool that itself proxies to an HTTP service.

Ember should *not* pick one. Ember should let the operator pick:

- For *embodiment-local* actions (animate, face, lip-sync, audio-output), use CDK's locality model. These belong inside Smiðja-as-component-host.
- For *Ember-internal* actions (search Brunnr, query Hjarta, project Hugarsýn), use a structured in-process call. Same locality model, no transport.
- For *external-world* actions (smart-home, calendar, email, web), use MCP. Out-of-process by design. Consent gating per server.
- For *vendor-baked-in* actions (the Waifu mode), refuse. The Vow of operator-extensibility forbids the closed-enum substrate from being primary.

This is the *three-mode tool surface* I propose in §6. CDK provided the local-mode template; SAP provided the remote-mode template; the three-mode composition is Ember's.

## 5. The consent-gating problem

CDK has no consent gate. A tool runs if registered and selected by the LLM. The operator's only consent surface is the act of *adding* the tool to the scene (a deploy-time choice) and the `IsEnabled` toggle in the Inspector. There is no per-call consent. There is no per-call audit beyond `Debug.Log`. There is no per-call summary in the doll's voice.

For an *unembodied* agent (a CLI tool, a backend service), the lack of per-call consent might be acceptable: the operator authored the agent's configuration and the tools that came with it. For an *embodied* agent — one with a face, a voice, and an apparent autonomy — the picture changes. The operator's *experience* of the doll is "I asked her to do something and she did it." The consent contract should match that experience: the doll *says what she's about to do*, the operator *can interrupt*, and the doll *says what she did*.

This is the **Surface-Without-Surveillance Vow** as it bears on tools, and it is the **Affective-Restraint Vow** as it bears on tools that the affect state might encourage or discourage. CDK provides neither. SAP gestures at it via MCP server-by-server permissions. Waifu sidesteps it by closing the action vocabulary. Ember needs to name it.

I propose **five consent classes** for Smiðja tools, attached as a manifest field per tool (§6.3):

1. **`silent_read`** — no consent needed per call; e.g. "what time is it", "what's on my calendar this hour". The action is read-only, idempotent, and inside the operator's own data scope.
2. **`announced_read`** — the doll says what she's reading before reading; e.g. "let me check your email subject lines". The action is read-only but the data is sensitive enough to deserve announcement.
3. **`announced_write_local`** — the doll says what she's about to write before writing; e.g. "I'll add this to your notes". The action mutates the operator's own local data.
4. **`announced_write_external`** — the doll says what she's about to do externally, *and waits for affirmative confirmation*; e.g. "should I send this email?". The action mutates state outside the operator's process.
5. **`gated_action`** — the doll names the action and requires an explicit operator confirmation phrase or button before execution; e.g. "should I turn off the front-door lock?". High-impact or irreversible actions.

Each class maps to a Strengr behaviour: a `silent_read` is invoked and the result feeds Strengr's reply with no announcement; a `gated_action` produces a Strengr-level pause where the doll speaks the intent and waits for `yes / no / cancel` before the tool ever runs.

CDK's `Debug.Log` becomes a typed Hjarta receipt. CDK's silent fall-through becomes a typed `tool_not_found` event surfaced to the operator. CDK's plaintext logging becomes redacted logging with a separate audit-only path to Hjarta.

This is a substantive addition to CDK's pattern. The Apache-2.0 license posture means we can vendor CDK's adapter code (the per-provider stream parsers, the JSON shape glue), but the consent gate is *new code* sitting between CDK's pattern and the actual execution. Smiðja owns the new layer.

## 6. Ember's pattern — `Smiðja.invoke()` with consent and audit

### 6.1 The shape

```python
# Strengr emits a typed tool-call event
tool_call = ToolCall(
    name="send_email",
    arguments={"to": "boss@work.com", "subject": "...", "body": "..."},
    requested_by="strengr",
    provider="anthropic",            # which LLM provider made the call
    provider_call_id="toolu_01ABC",  # provider-set ID where available
    session_id="2026-05-25-1402",
    context="email-triage",
)

# Smiðja routes the call
receipt = await smidja.invoke(tool_call)

# receipt is always returned — success or failure
# Strengr feeds receipt.body back to the LLM as the tool result
```

### 6.2 The pipeline inside `smidja.invoke()`

```
ToolCall
   │
   ▼
[1] resolve_tool(name) → ToolManifest    # dict lookup, no scene walk
   │
   ▼
[2] check_consent_class(manifest, args)  # five-class switch
   │
   ▼
[3] announce_if_required(manifest, args) # Strengr-driven speech
   │
   ▼
[4] await_confirmation_if_gated()        # operator yes/no/cancel
   │
   ▼
[5] redact_args(args, manifest)          # for audit log
   │
   ▼
[6] execute_with_timeout(tool, args)     # per-tool budget
   │
   ▼
[7] write_receipt(hjarta, receipt)       # always written
   │
   ▼
[8] announce_completion_if_required()    # closing speech
   │
   ▼
Return receipt
```

Eight stages. Each is observable in Hugarsýn (`/hugarsýn/smidja/in_flight`). Each can be replaced or extended per tool. The five consent classes (§5) decide which of stages 3, 4, and 8 fire.

### 6.3 The Tool Manifest

Every Ember tool ships a YAML manifest. Example:

```yaml
# tools/send_email.tool.yaml
name: send_email
description: Send an email from the operator's primary account
risk_class: announced_write_external
parameters:
  type: object
  properties:
    to: { type: string, format: email }
    subject: { type: string }
    body: { type: string }
  required: [to, subject, body]
announcement_template: "I'll send an email to {to} with the subject {subject}. Should I send it?"
completion_template: "Sent to {to}."
audit_record_template:
  fields: [to, subject_redacted, body_length, sent_at]
redaction:
  fields: [body]
  redaction: hash
provider_overrides:
  # If a provider has a peculiar shape (e.g. Gemini's no-id), declare here
  gemini:
    call_id_strategy: synth-from-hash
timeout_ms: 5000
turn_budget_consumed: 1
```

The manifest is the *single source of truth* for both the LLM-facing spec and the operator-facing audit record. CDK's `GetToolSpec()` returns an opaque object; Ember's manifest is plain YAML and introspectable from the operator's shell (`ember tools list`, `ember tools show send_email`).

### 6.4 The Receipt

Every invocation returns a typed Receipt regardless of success:

```python
@dataclass(frozen=True)
class ToolReceipt:
    tool_name: str
    arguments_redacted: dict        # post-redaction view
    consent_class: ConsentClass
    consent_granted: bool
    consent_source: str             # "manifest-silent" | "operator-confirm" | "policy-deny"
    started_at: datetime
    ended_at: datetime
    latency_ms: int
    success: bool
    body: str                       # what gets fed back to the LLM
    error_message: Optional[str]
    audit_record: dict              # per-manifest schema
    provider: str
    provider_call_id: Optional[str]
    session_id: str
    session_context: str
```

The receipt goes to Hjarta on every call. Hjarta is the audit log; Hugarsýn projects the active and recent receipts; Munnr can render a tool-call timeline to the operator on request.

### 6.5 Mapping CDK's pattern to Ember's

| CDK | Ember |
|---|---|
| `GetComponents<ITool>()` linear walk | `smidja.tools` dict, built once at boot from manifests |
| `Debug.Log($"Execute tool: ...")` | `hjarta.write_receipt(receipt)` with redacted args |
| Silent fall-through on name mismatch | `ToolNotFoundEvent(requested_name, available_names)` surfaced as a Strengr correction prompt |
| `useFunctions=false` recursion | Strengr's `respond_to_tool_result(receipt)` with masked tools and an across-turns budget |
| Per-provider message classes | Per-provider serialiser modules; canonical `ToolCall`/`ToolReceipt` types are provider-agnostic |
| No per-call consent | Five-class consent gate with announce/confirm/audit |
| No timeout | `manifest.timeout_ms` enforced by `execute_with_timeout` |
| No depth limit across turns | `session.tool_calls_this_user_input`, refuse beyond `max_tool_calls_per_user_input` (default 4) |

The mapping is structurally one-to-one for the wire-format layer (we adopt CDK's per-provider adapters under Apache-2.0 attribution) and substantively additive for the consent layer (which CDK does not have).

## 7. The provider-divergence problem stated as a thesis

The thesis CDK demonstrates: **the JSON wire format of function calling is the thinnest cross-provider abstraction layer that survives daily use**, and any abstraction *above* the wire format leaks. CDK's `ILLMService` does not pretend the three providers agree; each provider's service file (`ChatGPTService.cs`, `ClaudeService.cs`, `GeminiService.cs`) carries its own JSON-shape glue.

The corollary: **embodied tools should not be designed against a "tool-calling protocol"**. They should be designed against the *canonical* `ToolCall` and `ToolReceipt` Ember types, and Strengr's adapter layer translates per provider. The translation is per-provider serialiser code, not a unified intermediate format.

This matters for Ember's federation story. If two Embers run on different LLM providers (one on Anthropic, one on a local Ollama), and they both invoke `send_email`, the *canonical tool call* is identical between them; the *wire-format* call differs. Hjarta records the canonical form. Cross-provider context sharing (the `Hjarta Cross-Provider Context Mirror` invented in `[[chatdoll:36_FUNCTION_CALL_EXEC §What This Means]]`) works because Hjarta has the canonical form, not the wire-format form.

CDK cannot do this. CDK's `ChatGPTSession.Contexts` is a `List<ChatGPTMessage>`; the messages are typed to ChatGPT's shape. Switching to Claude mid-session would require re-serialising the entire context, and CDK doesn't try. Ember can, because Ember's canonical types are LLM-agnostic.

## 8. Where this synthesis lands — five claims

To close the synthesis tightly, five claims I am willing to defend:

1. **Tool calling for embodied agents is a five-stage pipeline, not a function invocation.** The five stages: resolve, check-consent, announce, execute, receipt. Each is observable. CDK collapses to two stages (resolve, execute); Ember must keep all five.

2. **The wire-format layer should be adopted from CDK with Apache-2.0 attribution; the consent layer is Ember-original.** Reuse the parsers; do not reuse the silent execution.

3. **Five consent classes are the right granularity.** Three is too coarse (we lose the announced/gated distinction); seven is too fine (operator fatigue). The five classes in §5 each correspond to a distinct user experience.

4. **The Tool Manifest replaces the C# Inspector toggle.** The Inspector is fine for Unity; for Ember, manifests are operator-readable, version-controllable, and machine-checkable. The Inspector model leaks at the federation boundary; the manifest model travels.

5. **The Receipt is the audit primitive, not the log line.** Every invocation, always, written to Hjarta. Hjarta is the audit log. Hugarsýn projects it. Munnr renders it. No tool execution is invisible.

## 9. Cross-References

- `[[60_TRIANGULATION]]` — the three-corpus comparison matrix; this doc develops the function-calling row
- `[[63_MULTIMODAL_PIPELINE]]` — the LLM stage of the pipeline is where tool calls emerge; the consent gate inserts between LLM and downstream
- `[[65_MEMORY_INTEGRATION]]` — Hjarta is the audit destination for receipts; the memory pattern and the receipt pattern share a backend
- `[[chatdoll:16_LLM_SERVICE_DOMAIN]]` — Architect's deep dive on `LLMServiceBase`
- `[[chatdoll:19_TOOL_DOMAIN]]` — domain view of `ITool`/`ToolBase`
- `[[chatdoll:20_LLM_SERVICE_INTERFACE]]` — interface contract across providers
- `[[chatdoll:26_TOOL_FUNCTION_CALL_INTERFACE]]` — Architect's per-provider tool-call format study
- `[[chatdoll:36_FUNCTION_CALL_EXEC]]` — Forge-A's execution-trace doc; this synthesis sits above it
- `[[chatdoll:53_MULTI_LLM_CONSISTENCY]]` — Auditor's catalog of cross-provider divergences
- `[[sap:20_MCP_INTEGRATION]]` — MCP transport pattern; this doc proposes MCP as one of three Smiðja modes
- `[[sap:29_TOOL_TYPE_INTERFACE]]` — SAP's tool-type taxonomy
- `[[waifu:22_ACTION_PROTOCOL]]` — closed action vocabulary at vendor boundary
- `[[hermes:Verkfæri]]` — PROPOSED True Name for tools; this doc grounds it
- `[[ember:RULES.AI]]`, `[[ember:PHILOSOPHY]]` — Surface-Without-Surveillance, Affective-Restraint

## What This Means for Ember

**Adopt:**

- **The `ITool` interface shape** (`/tmp/ChatdollKit/Scripts/LLM/ITool.cs:7-13`, twelve lines, Apache-2.0 attribution required). The three-method contract — `IsEnabled`, `GetToolSpec()`, `ExecuteAsync(args_json, token)` — is exactly the right shape for Smiðja's local-tool API. Adopt the contract; reimplement the body against Ember's Python idiom.
- **The auto-discovery pattern** (`DialogProcessor.cs:115-128`). For Smiðja, replace `GetComponents<ITool>()` with `smidja.scan_manifests("tools/*.tool.yaml")`. Same boot-time-discovery shape; same `IsEnabled` semantics; manifests instead of MonoBehaviours.
- **The recursive `useFunctions=false` loop-breaker** (`ChatGPTService.cs:368`, `ClaudeService.cs:308`). Adopt as Strengr's `respond_to_tool_result(receipt)`. The LLM receives the receipt body and produces a natural-language reply with tools masked. Across-turns budget enforced separately.
- **Per-provider serialiser modules** under `ember/strengr/providers/{anthropic,openai,gemini,ollama,dify,aiavatarkit}.py`. Same folder shape as CDK's `Scripts/LLM/ChatGPT/`, `Claude/`, `Gemini/`. Each module owns its JSON shape; the canonical `ToolCall`/`ToolReceipt` types are above. *Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*
- **The thesis from §7** as a design law: the wire format is the abstraction floor. Do not pretend providers agree; serialise per provider; canonicalise in Hjarta.

**Adapt:**

- **The `Tools = toolSpecs` direct assignment** (`DialogProcessor.cs:171`). Adapt to immutable snapshot semantics: `strengr.with_tools(spec_list)` returns a configured session-shaped context. Avoids the shared-state race surface CDK has when multiple `ILLMService` instances coexist.
- **The `useFunctions=false` recursion's implicit one-tool-per-turn** policy. Adapt to a *configurable* `max_tool_calls_per_user_input` (default 4) enforced at Strengr's session level. Some operator situations want chained tool use (read calendar → draft email → send); the across-turns budget is the discipline that permits it without unbounded loops.
- **CDK's `ChatGPTFunctionMessage` / `ClaudeMessage[tool_result]` / Gemini `functionResponse` part-classes** into Ember's canonical `ToolReceipt`. Adapt by adding three small serialisers (`receipt_to_chatgpt`, `receipt_to_claude`, `receipt_to_gemini`) that produce the wire-format-correct context append.
- **The CDK pattern of "tool-result-as-context-append, then recurse"** (`ChatGPTService.cs:362`, `ClaudeService.cs:300`). Adapt with an explicit between-call audit hook: `hjarta.write_receipt(receipt)` happens *before* the context append, so the audit log shows the receipt even if the recursive LLM call fails.

**Avoid:**

- **The silent fall-through on tool-name mismatch.** When the LLM emits an unknown tool name, Smiðja emits a typed `ToolNotFoundEvent(requested_name, available_names)`, feeds it back to the LLM as the call result, and lets Strengr produce a corrected reply. The user sees "I tried to call `weathr` but I have `get_weather`; let me try that" — visible self-correction, not a frozen avatar.
- **The plaintext `Debug.Log` of full function arguments** (`ChatGPTService.cs:360`). Smiðja's redaction layer is mandatory; the manifest declares which fields are sensitive; the audit log writes the redacted form; the un-redacted form goes only to Hjarta's secure-store partition (`Hjarta.sensitive_receipts`) with operator-readable but not LLM-readable access.
- **The closed action vocabulary** of the Waifu pattern. The Vow of operator-extensibility forbids a tool surface that the operator cannot extend. The vendor-baked-in mode is rejected as a primary substrate.
- **The conflation of `[vision:Camera]` tag with structured tool calls** (CDK does this in `ChatGPTService.cs:373-399`). Vision-capture and tool-invocation are semantically different operations; Ember keeps them on separate code paths. The tag protocol drives embodiment-rendering only; structured tools go through Smiðja.
- **The no-consent-by-default posture.** Every Ember tool ships with a `risk_class` field; tools without one default to `gated_action` (most-conservative). No tool can be added to the manifest tree without declaring its class.

**Invent:**

- **Smiðja as the three-mode tool surface.** Three tool modes coexist under one Smiðja: **local-component** (CDK-derived, in-process Python tools), **internal-rpc** (calls to other Ember True Names like Brunnr or Hjarta), and **mcp-remote** (out-of-process MCP servers, SAP-derived). The operator's manifest declares which mode each tool uses; Smiðja routes accordingly. This is the load-bearing structural finding of this doc.
- **The five-class consent taxonomy** (`silent_read`, `announced_read`, `announced_write_local`, `announced_write_external`, `gated_action`). Each class corresponds to a distinct user experience and a distinct announcement/confirmation behaviour from Strengr. Defaults are conservative; operator can downgrade per tool with explicit declaration. Vow tie-in: **Surface Without Surveillance** is enforced *at the tool surface*, not at the network surface.
- **The Tool Manifest as ratified artifact.** Every tool ships YAML; manifests are version-controlled; manifest changes go through the same ratification gate as slice-plan changes. The operator's `tools/` directory is the inventory of what the doll can do; auditing the directory is auditing the doll's reach. Vow tie-in: **Embodied Honesty** at the manifest level.
- **The Tool Receipt as audit primitive.** Every invocation produces a typed receipt; every receipt is written to Hjarta; every receipt is projectable through Hugarsýn. The receipt schema is canonical and provider-agnostic. Vow tie-in: **the audit trail is the agent's voice plus the receipt log**.
- **The Hjarta Cross-Provider Context Mirror.** Because Ember's canonical types are LLM-agnostic, mid-session provider switch is possible. When an operator switches from Anthropic to local Ollama mid-conversation, Hjarta re-renders the historical tool calls in the new provider's wire format and Strengr resumes. CDK cannot do this because its message classes are provider-typed; Ember can because the canonical form is the primary form. Vow tie-in: **Federated Self** extended to **Federated Across Providers**.
- **The five-stage embodied-tool pipeline as named artifact**, parallel to the seven-stage multimodal pipeline of `[[63_MULTIMODAL_PIPELINE]]`. The pipeline lives at `docs/smidja_specification.md`; updates are ADR-tracked; each stage's failure modes and degradations are catalogued. The pipeline is *first-class*, not implementation detail.
- **The Tool-Call Visualizer in Munnr.** While a tool is executing (especially during `announced_write_external` or `gated_action`), Munnr surfaces a live view: tool name, redacted arguments, elapsed time, expected timeout, current consent state. The operator sees "ember is sending an email to boss@work.com — 1.4s elapsed of 5s budget — cancel?" with a real cancel button. CDK's spinner-without-context is replaced with a context-rich progress surface.
- **The `tool_audit_thread` Hugarsýn projection.** `/hugarsýn/smidja/recent_receipts` returns the last N receipts with timestamps, consent classes, success flags, and redacted arguments. Every party peer can read which tools this Ember has invoked recently. The tool surface is *federated-visible*; cross-instance trust is buildable on a shared receipt log. Vow tie-in: **Federated Self** plus **Defended Builds** generalized to **Defended Tool Surface**.
- **The Smiðja Turn Budget.** A per-user-input budget `max_tool_calls_per_user_input` (default 4) is checked at the start of every tool invocation. Exceeding the budget halts the tool chain, surfaces a `TurnBudgetExhaustedEvent`, and Strengr produces a natural-language reply explaining the halt. Prevents the CDK-class infinite-tool-loop without forbidding multi-step tool use.
- **The Voice-Issued Command Contract.** When the operator issues a spoken command and the resolution involves a `gated_action`, the gate phrase is *also* spoken — the doll says "should I send it?" and listens for `yes / no / cancel` through the same STT pipeline. The barge-in protocol of `[[63_MULTIMODAL_PIPELINE §4]]` is reused as the cancellation pathway. The consent interaction is *in the embodied register*, not a popup dialog. Vow tie-in: **Embodied Honesty** — the doll commits to the action only in the same voice she uses to ask permission.

---

*Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c). The per-provider message-class designs may also be subject to each provider's API terms — review before vendoring.*

Three providers, three wire formats, one C# interface. CDK's adapter shows where portability ends — at the JSON shape, not above it. The consent layer is the work CDK left undone. Five classes, eight pipeline stages, one canonical receipt. The doll says what she's about to do, asks when she should ask, and writes down what she did. The audit is the agent's voice; the receipt is the proof.

---
codex_id: 03_ANTI_CDK
title: Anti-CDK — The Refusals Ember Owes to Apache-2.0 Honesty
role: Skald
layer: Vision
status: draft
cdk_source_refs:
  - /tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:15
  - /tmp/ChatdollKit/Scripts/LLM/Claude/ClaudeService.cs:15
  - /tmp/ChatdollKit/Scripts/LLM/Gemini/GeminiService.cs
  - /tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTServiceWebGL.cs:28
  - /tmp/ChatdollKit/Scripts/LLM/Claude/ClaudeServiceWebGL.cs:28
  - /tmp/ChatdollKit/Plugins/ChatGPTServiceWebGL.jslib
  - /tmp/ChatdollKit/Scripts/SpeechSynthesizer/GoogleSpeechSynthesizer.cs:26
  - /tmp/ChatdollKit/Scripts/SpeechSynthesizer/GoogleSpeechSynthesizer.cs:50
  - /tmp/ChatdollKit/Scripts/SpeechSynthesizer/AzureSpeechSynthesizer.cs:29
  - /tmp/ChatdollKit/Scripts/SpeechSynthesizer/AivisCloudSpeechSynthesizer.cs:29
  - /tmp/ChatdollKit/Scripts/SpeechListener/OpenAISpeechListener.cs:12
  - /tmp/ChatdollKit/Scripts/SpeechListener/OpenAISpeechListener.cs:41
  - /tmp/ChatdollKit/Scripts/Network/SocketServer.cs:36-39
  - /tmp/ChatdollKit/Scripts/Network/SocketServer.cs:88
  - /tmp/ChatdollKit/Scripts/IO/JavaScriptMessageHandler.cs:10-30
  - /tmp/ChatdollKit/Scripts/Model/ModelController.cs:247-289
  - /tmp/ChatdollKit/Scripts/LLM/LLMServiceBase.cs:100-117
  - /tmp/ChatdollKit/README.md:103
ember_subsystem_targets: [Andlit, Rödd, Hjarta, Brunnr, Strengr, Funi]
cross_refs:
  - 00_vision/00_OVERTURE
  - 00_vision/01_CDK_ESSENCE
  - 00_vision/02_UNITY_AS_RUNTIME
  - 00_vision/04_VISION_SYNTHESIS
  - 50_verification/51_SECURITY_REVIEW
  - 50_verification/55_WEBGL_GOTCHAS
  - 20_interface/27_SOCKET_PROTOCOL
  - 20_interface/28_JS_BRIDGE_INTERFACE
  - sap:03_ANTI_SAP
  - waifu:00_OVERTURE
---

# Anti-CDK — The Refusals Ember Owes to Apache-2.0 Honesty

> *Open source is not a moral free pass. It is an invitation to read carefully, name what is wrong, and be honest about what we choose not to copy across.*
> — Sigrún Ljósbrá, sharpening the knives

## 0. Posture

The Refusal-Citation Discipline carries forward from `[[sap:03_ANTI_SAP §What This Means]]` and the Wave-3 Refusals catalogue. Every refusal in this document names the line. The Apache-2.0 license does not insulate ChatdollKit from refusal; it *expands the obligation*, because Apache-2.0 sources can be *adopted* into Ember, and the easiest way to adopt a bad pattern is to adopt it silently.

ChatdollKit is *better-engineered* than SAP and *more honestly licensed* than the Waifu kit. Both are true. *And* — the codebase carries refusal-worthy patterns that Ember must not inherit. The Skald's job here is to walk each with the line number attached.

Wave 3 produced thirteen specific Refusals. Wave 4 produced four. Wave 5 has eight Refusals plus three Deferrals (patterns that need verification work before final adjudication). I will walk them in turn.

## I. Refusal 1 — LLM API keys as `public string` MonoBehaviour fields

The most direct refusal. Open the file:

```csharp
// /tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:13-15
public class ChatGPTService : LLMServiceBase
{
    [Header("API configuration")]
    public string ApiKey;
```

The same shape repeats:

- `ClaudeService.cs:15` — `public string ApiKey;`
- `GeminiService.cs:15` — `public string ApiKey;` (verified by the parallel WebGL bridge at `GeminiServiceWebGL.cs:27` which extern-imports an `apiKey` parameter)
- `OpenAISpeechListener.cs:12` — `public string ApiKey;`
- `GoogleSpeechSynthesizer.cs:26` — `public string ApiKey;`
- `AzureSpeechSynthesizer.cs:29` — `public string ApiKey;`
- `AivisCloudSpeechSynthesizer.cs:29` — `public string ApiKey;`
- `KotodamaSpeechSynthesizer.cs:29` — `public string ApiKey;`
- `AIAvatarKitSpeechSynthesizer.cs:31` — `public string ApiKey;`
- `AIAvatarKitSpeechListener.cs:15` — `public string ApiKey = string.Empty;`
- `AzureStreamSpeechListener.cs:32` — `public string ApiKey = string.Empty;`

Ten files (at minimum) where the credential lives as a *public field on a MonoBehaviour*.

This is *not* equivalent to "the developer remembered to set the key in their Unity Editor." A `public` MonoBehaviour field gets *serialized into the asset bundle* by Unity's editor when the component is added to a GameObject in a scene or prefab. When the Unity project is *built* to a distributable executable, the serialized field's value travels with the binary. **Any user with a copy of the built executable can extract the API key with a free decompilation tool.**

The Waifu kit had the same problem at `BasicMode.tsx:21` — `apiKey: "<your-api-key>"` — and the Skald named it as Refusal in `[[waifu:00_OVERTURE §VIII]]`. The CDK case is *worse* because (a) it appears in *more places* (ten files versus one in the Waifu kit) and (b) Unity asset bundles are *more easily extractable* than minified React bundles (the BinaryFormatter-equivalent for Unity's serialization is well-documented and free tools exist). The build that ships to the App Store contains the developer's OpenAI key in plaintext, retrievable in *minutes* by any motivated user.

The exacerbation: the WebGL bridge passes the key *directly into JavaScript*. Open the `.jslib`:

```javascript
// /tmp/ChatdollKit/Plugins/ChatGPTServiceWebGL.jslib (head, paraphrased)
ChatCompletionJS: function(targetObjectNamePtr, sessionIdPtr, urlPtr, apiKeyPtr, ...) {
    let apiKey = UTF8ToString(apiKeyPtr);
    ...
    fetch(url, {
        headers: {
            "Authorization": `Bearer ${apiKey}`,
            "api-key": `${apiKey}`
        },
```

In a WebGL build, the API key is *literally a string passed through the C#-to-JavaScript bridge, visible in the browser's network tab, visible in the browser's debugger, visible to any browser extension*. The WebGL demo at the URL the README links (`https://unagiken.blob.core.windows.net/chatdollkit/ChatdollKitDemoWebGL/index.html`) — *if it currently functions* — is either calling unagiken-provided keys (which is to say, vendor-provided keys that are billed-to-someone) or has the keys baked in.

**Refusal 1.** Ember does not put API credentials in serializable fields, in client-bundle-shipped configuration, in JavaScript-bridge parameters, or in any state that ships with the built binary. Ember's credential surface is *Hjarta-typed*, *encrypted at rest*, *runtime-fetched from operating-system credential stores* (Keychain on macOS, Credential Manager on Windows, libsecret on Linux), *never serialized into asset state*. The Defended Credential Surface (Wave 4 sharpening, `[[waifu:01_VISION_SYNTHESIS §II]]`) is the Vow.

## II. Refusal 2 — SocketServer binds to `IPAddress.Any`

```csharp
// /tmp/ChatdollKit/Scripts/Network/SocketServer.cs:88
server = new TcpListener(IPAddress.Any, port);
```

`IPAddress.Any` is `0.0.0.0`. The TCP listener accepts connections from *any* network interface, including network interfaces the operator may not know exist (the workplace Wi-Fi, the Tailscale interface, the Docker bridge, the random Bluetooth-tethering interface). The default at `SocketServer.cs:36-39`:

```csharp
[SerializeField]
private bool autoStart = true;
```

`autoStart = true`. The server *starts on Awake without operator interaction*. The README's Socket-control feature (`/tmp/ChatdollKit/README.md:103` — *External Control via Socket*) sells this as a feature: *trigger specific phrases, or control expressions and gestures, unlocking new use cases like AI Vtubers and remote customer service*. The features are real. The default exposure is *unbounded*.

There is *no authentication on the protocol*. The message types are JSON-deserialized via `Newtonsoft.Json` (`SocketServer.cs:9` — `using Newtonsoft.Json`) and dispatched to `OnDataReceived`. Any peer that can reach the port can *trigger animations, change facial expressions, send dialog inputs, drive the avatar*. On the same machine, this is fine for local development. On any machine with a real network interface, this is *the doll's body is remote-controllable by anyone who scans the LAN*.

This is the SAP Refusal-4 (`[[sap:03_ANTI_SAP §Refusal-4]]`) — VMC bound to `0.0.0.0` — recurring in a different codebase. The pattern is *culturally pervasive in voice-avatar projects* and Ember must refuse it categorically.

**Refusal 2.** Ember's typed RPC surface for *any* avatar control defaults to `IPAddress.Loopback` (127.0.0.1) or to a typed Tailnet-binding when explicitly opted in. The opt-in carries a Cord Manifest entry (Wave 4 invention) with declared threat model. Authentication is *mandatory*, not optional; the typed protocol carries a session token bound to operator-issued credentials. The README's "AI VTuber remote-customer-service use cases" are *not refused as use cases*, but their implementation goes through the typed-cord-with-auth pattern, never raw 0.0.0.0 TCP.

## III. Refusal 3 — The face-tag protocol as LLM emotional self-report

```csharp
// /tmp/ChatdollKit/Scripts/Model/ModelController.cs:252-257
if (parsedText.StartsWith("[face:"))
{
    var face = parsedText.Substring(6, parsedText.Length - 7);
    avreq.AddFace(face, duration: FaceController.DefaultFaceExpressionDuration);
    ttsConfig.Params["style"] = face;
}
```

The model emits `[face:happy]`. The host parses *happy*, looks up the `FaceClip` named *happy*, plays it, *and also tells the TTS the voice style should be "happy"*. The face is *whatever the model claimed it was*. The voice is *also whatever the model claimed*. The emotion is *the LLM's self-report* mediated through a typed parser.

This is *the same anti-pattern as SAP's affection system* (`[[sap:03_ANTI_SAP §Refusal-1]]`), in a smaller and better-typed package. The improvement: ChatdollKit's typed-tag-with-registered-vocabulary discipline is *closer to defensible* than SAP's free-text behavior-prompt injection. The unfaithfulness: the *generation* of the tag is *still the LLM authoring state about the doll's emotion*, which violates the Vow of Embodied Honesty (`[[sap:61_NEW_VOWS]]`).

The face should reflect *what the doll knows about itself* — current cognitive load (slow when the LLM is taking long), current confidence (uncertain when the retrieval failed), current attention focus (the operator's name when addressed). The face should *not* reflect *what the LLM said the face should be doing*. The LLM does not know what the doll is feeling. The LLM is *guessing* based on the prompt. The face reflecting the LLM's guess is *theater*, not honesty.

**Refusal 3.** Ember's Andlit (when it exists) does not play LLM-emitted face tags as primary signal. The face is *measured-state-driven first, LLM-suggested second, and only when the LLM suggestion does not contradict the measured state*. The implementation: a `face_priority_merge()` function that takes Hjarta's measured emotional bias and the LLM's tag suggestion, returns the measured bias if they disagree, returns the LLM suggestion only if it is consistent with measured state. The Cartographer's `[[60_synthesis/63_MULTIMODAL_PIPELINE]]` formalizes.

## IV. Refusal 4 — Tag protocol assumes well-behaved model emission

The same tag mechanism (`LLMServiceBase.cs:100-117`):

```csharp
var tagPattern = @"\[(\w+):([^\]]+)\]";
var matches = Regex.Matches(text, tagPattern);
```

What does this fail at?

- *A model that emits no tags*: the doll is mute-faced. No expression. The default-Idle face from `FaceController.DefaultFaceExpressionDuration` persists. The doll looks *catatonic* during long replies.
- *A model that emits malformed tags*: `[face:happy and excited]` (with whitespace + multi-word) gets matched as `face = happy and excited`. The lookup fails. Silent log warning. Face does not change.
- *A model that emits adversarial tags*: `[face:../../etc/passwd]` doesn't directly cause a file-system traversal here (because the lookup is dictionary-based), but `[anim:SystemReboot]` *if* an animation named `SystemReboot` exists *does* execute it. The vocabulary is operator-registered, so the surface is limited to *whatever the operator registered*, but an operator-registered debug animation that exists on Tuesday becomes an LLM-emission attack vector on Wednesday.
- *A model that emits tags inside reasoning*: `[think]The user is angry, I should [face:concerned] now[/think]` — the tag *inside* the think-block gets parsed and played. The think tag handling at `LLMContentProcessor.cs:84-108` handles `<think>` blocks but not the tag-inside-tag case the regex would still match.

The discipline is *better than SAP's untyped string injection*, but it is *not robust* against the broader class of malicious or malformed LLM output.

**Refusal 4.** Ember's typed-tag-protocol (if adopted from `[[01_CDK_ESSENCE]]`) carries *validation*, *sanitization*, *think-block stripping*, and *operator-curated vocabulary discipline* — the model's emitted tag is not directly dispatched; it is validated against a sandboxed vocabulary, sanitized for adversarial-character sequences, stripped from any think-block context, and rejected silently if it fails any check. The Hjarta-measured-state override (Refusal 3) is also active. The Auditor's `[[50_verification/53_MULTI_LLM_CONSISTENCY]]` catalogues the failure modes.

## V. Refusal 5 — JavaScriptMessageHandler as XSS surface in WebGL

```csharp
// /tmp/ChatdollKit/Scripts/IO/JavaScriptMessageHandler.cs:10-30
public class JavaScriptMessageHandler : MonoBehaviour, IExternalInboundMessageHandler
{
    public Func<ExternalInboundMessage, UniTask> OnDataReceived { get; set; }

#if UNITY_WEBGL
    [DllImport("__Internal")]
    private static extern void InitJSMessageHandler(string targetObjectName, string targetFunctionName);
    ...
    public void Start()
    {
        if (captureKeyboardInput)
        {
            WebGLInput.captureAllKeyboardInput = false;
        }
        ...
    }
```

The WebGL build's external-control surface is *JavaScript posting messages to Unity*. The JavaScriptMessageHandler exposes a Unity gameObject method as a *target* for browser JavaScript to call. There is no message-origin verification. *Any* JavaScript running in the same browser context — including third-party scripts loaded via `<script src>`, browser extensions, malicious iframes, or XSS injections — can drive the avatar's dialog inputs and animations.

For a public-deployed Unity WebGL build of an Ember-equivalent, this is *the same attack surface class as Cross-Site Scripting*. A vulnerable host page can hijack the doll. Worse: the typed protocol is *the same JSON* that the SocketServer accepts, so an attacker who compromises one side has *the same vocabulary* for the other.

**Refusal 5.** Ember's WebGL-tier external-control surface (if/when Andlit-unity ships a WebGL build) defaults to *message-origin verification* — the JavaScript bridge accepts messages only from the operator-declared parent-window origin, dispatched through `window.postMessage` with origin-checking, with a per-message HMAC signature derived from a session secret. The default is *no external control*; opt-in is per-deployment. The Auditor's `[[50_verification/55_WEBGL_GOTCHAS]]` documents the attack surface.

## VI. Refusal 6 — Unity-monoculture risk by accumulation

This is not a single-line refusal; it is a *pattern of dependencies* that, in aggregate, creates an engine-lock-in surface Ember must refuse.

ChatdollKit's `Scripts/ChatdollKit.asmdef` declares three GUID references (Unity's UPM packages by hash) plus a version-defined optional dependency on `com.endel.nativewebsocket`. The runtime depends on UniTask (Cysharp.Threading.Tasks — `AIAvatar.cs:6`), UniVRM for the VRM extension (`Extension/VRM/`), uLipSync for the lip-sync helper (`Model/uLipSyncHelper.cs`), Newtonsoft.Json (`Network/SocketServer.cs:9`). The Plugins tree has Android native + iOS native + WebGL .jslib bridges. The Extension tree has VRM-specific code, ChatMemory integration, SileroVAD with its own ONNX runtime expectations.

Each dependency is, individually, fine. *In aggregate*, the pattern is: every additional feature added to a CDK-equivalent codebase *requires another Unity package*. The asmdef GUIDs are not human-readable; the dependency on `uLipSync` (a single-author MIT-licensed package) creates a *single-author-failure-mode* surface; the dependency on `UniVRM` (a major community-maintained package) creates a *VRM-spec-evolution-tracking* obligation. The Unity ecosystem *is* the dependency graph; you do not get to use just the engine without the packages.

This is *not* refusal-worthy at the level of ChatdollKit's choices (uezo's choices are appropriate-to-the-domain). It is refusal-worthy at the level of *Ember's commitment*. Ember cannot inherit Unity-monoculture by adopting Unity-as-foundation.

**Refusal 6.** Ember does not adopt Unity as foundation. The Andlit-unity sub-name (`[[02_UNITY_AS_RUNTIME §VI]]`) is the *contained* path for Unity-derived embodiment if-and-when that materializes. The Ember core remains language-agnostic-at-the-Vow-level, Python-implemented-at-the-current-tier, and *free to migrate* to a different runtime in a future tier without inheriting the Unity ecosystem's dependency graph.

## VII. Refusal 7 — VRM as the default avatar identity

ChatdollKit ships VRM (`Extension/VRM/VRMLoader.cs`, `Extension/VRM/AIAvatarVRM.prefab`) as the *flagship* avatar format. The README's setup instructions (`/tmp/ChatdollKit/README.md:193-205`) walk through *VRM setup*. The OshaberiAI flagship app uses VRM. The community-shipping examples use VRM. The default is VRM.

VRM is *a good format*. It is the Japanese-community's open standard for character files (developed by Pixiv, maintained by VRM Consortium, openly specified). It is not refusal-worthy *as a format*. It is refusal-worthy *as Ember's default* because:

1. *VRM is culturally specific*. The format's origin in the Japanese anime-style character pipeline means most VRM-marketplace models are anime-style characters. An Ember default that is *anime-style character* is *not* Ember's chosen identity; it would be a marketing-template the codex never ratified.
2. *VRM commits Ember to a specific bone-and-blendshape model*. The format's specific bone hierarchy and blendshape names (the `aa`, `ih`, `ou`, `ee`, `oh` mouth shapes used at `uLipSyncHelper.cs`) are *the format's choice*. Ember inheriting them inherits the format's choices.
3. *VRM rendering is Unity-specific in practice*. The UniVRM package is *the* mature VRM loader; the alternatives (Three.js's VRM support, Babylon.js's VRM support) are less mature. Adopting VRM-as-default tugs Ember toward Unity-as-default (Refusal 6).

**Refusal 7.** Ember's eventual Andlit (when it exists) defaults to a *small, format-agnostic, operator-chosen* representation — possibly an ASCII glyph at Pi-tier, possibly a Live2D rig at laptop-tier, possibly VRM *only when the operator explicitly chose VRM*. The operator's choice is the default; no marketing-template imports.

## VIII. Refusal 8 — Single-author bus-factor across CDK + sister projects

This is a *risk refusal*, not a code refusal. uezo is the author of ChatdollKit, ChatMemory, AIAvatarKit, AITuber Controller, and OshaberiAI. Five projects under one mind. The same mind that shipped 1,157 commits to ChatdollKit shipped the sister projects. *This is admirable engineering*; it is also a *single-point-of-failure*.

Five years of consistent maintenance is the evidence-for. Five years of sole-author maintenance is the evidence-of-risk. If uezo stops, ChatdollKit + the sister projects + the OshaberiAI iOS app all *stop receiving updates from the canonical source*. Forks would happen; the ecosystem would continue; but the *coordination across the sister projects* — which is what makes ChatdollKit *more than the sum of its parts* — depends on a single author's continued involvement.

Ember's Vow of Modular Authorship demands that *no Ember dependency is single-author-load-bearing*. ChatdollKit's Apache-2.0 license means Ember can adopt patterns; Ember cannot *depend on the upstream* without taking on the bus-factor risk. Each adoption must be *re-implemented in Ember's tree*, attributed appropriately, and decoupled from upstream's future.

**Refusal 8.** Ember does not depend on ChatdollKit, ChatMemory, AIAvatarKit, AITuber Controller, or OshaberiAI as *upstream dependencies*. Adopt-list entries are *patterns reimplemented in Ember source with attribution*, never *imports from upstream packages*. The Apache-2.0 attribution discipline (preserving the CDK header reference per §4(c)) is the obligation; the decoupling is the discipline.

## IX. Deferral A — The function-call format divergence question

```csharp
// /tmp/ChatdollKit/Scripts/LLM/ILLMService.cs (interface)
// Each provider implements function-call adaption from its own format
```

ChatdollKit has six LLM providers. ChatGPT uses OpenAI function-call format (JSON in the `tool_calls` field). Claude uses Anthropic tool-use format (XML-like blocks in the content). Gemini uses Google function-call format (different JSON schema). Dify uses Dify's own conversation API. AIAvatarKit's backend has its own RPC.

The `ILLMService` interface abstracts the call sites but *not* the function-call format normalization. Each provider's service class handles its own format internally. The host code's `ITool`/`ToolBase` interface (`Scripts/LLM/ITool.cs`, `Scripts/LLM/ToolBase.cs`) sees a normalized `function_call_request` and `function_call_response`, but the format divergence is *handled inside the providers* without uniform error semantics.

This is *not refusal-worthy at first glance* — it is engineering pragmatism, and the alternative (one canonical function-call format that all providers transform to) is genuinely hard. But the *failure modes* across providers are *inconsistent* in ways that can break Ember's planned tool-use loop. Claude's tool-use can return *partial* tool calls in mid-stream; OpenAI's are emitted atomically; Gemini's batch differently. An Ember tool-use loop built on `ILLMService` would need to handle all three failure modes.

**Deferral A.** This is verification work, not Vision work. The Auditor's `[[50_verification/53_MULTI_LLM_CONSISTENCY]]` catalogues the divergences. The Skald reserves the option to formalize Refusal or Adopt-with-discipline after the verification.

## X. Deferral B — The ChatMemory single-vendor episodic-memory pattern

```csharp
// /tmp/ChatdollKit/Extension/ChatMemory/ChatMemoryIntegrator.cs (head)
[SerializeField]
private string BaseUrl;
public string UserId;
public string Channel;
```

ChatMemory (the sister project) is *good engineering* — a FastAPI service that stores conversation history with episodic + factual + summary scoring. The README pitches it as *the* memory backend, with mem0 and Zep as alternatives that the integrator pattern allows. The interface is *pluggable*.

The deferral: ChatMemory is *a single-vendor episodic-memory service maintained by uezo*. Adopting the *pattern* (episodic + factual + summary, FastAPI-served, pluggable via integrator) is good. Adopting the *specific service* would create another single-author dependency (Refusal 8 again). The verification needed: is the ChatMemory schema portable enough to be the *Brunnr-pluggable interface* Ember has been looking for? Or is it ChatMemory-shaped in ways that would constrain Ember's existing storage abstractions?

**Deferral B.** The Cartographer's `[[60_synthesis/65_MEMORY_INTEGRATION]]` does the deep work. Skald reserves Adopt or Adapt verdict.

## XI. Deferral C — The Japanese voice ecosystem as Ember's voice default

Ten Japanese TTS providers shipped with adapters. The pull is strong: VOICEVOX (free, ONNX-compatible), AivisSpeech (VOICEVOX-compatible API, character voicebanks), Style-Bert-VITS2 (style-controllable, open-source). The Skald named this in `[[00_OVERTURE §V]]` as the *under-mapped continent* that Wave 5 closes.

The deferral question is *not* whether Ember should engage the Japanese voice ecosystem (yes, it should). The question is *whether one or two of these providers should be Ember's Rödd-local default* — given that VOICEVOX speaks Japanese phonetics, AivisSpeech's character voices are *Japanese-character voices* (with English pronunciation that is *technically functional but accented*), and Style-Bert-VITS2 supports multi-language but with quality variation.

**Deferral C.** The Scribe's `[[60_synthesis/66_JAPANESE_VOICE_INTEGRATION]]` formalizes the engagement; the *adoption decision* for Ember's Rödd-local defaults remains for a future operator-ratified slice.

## XII. The pattern across the refusals

Eight refusals, three deferrals. The pattern that connects them:

ChatdollKit is *well-engineered* in places where engineering rigor pays off (modularity, abstraction interfaces, multi-platform discipline). It is *carelessly defaulted* in places where defaults invite operational harm (API keys in serialized fields, 0.0.0.0 sockets without auth, WebGL JS bridges without origin checks). The careless defaults are *typical of solo-author projects*, where the author knows what they meant and the consumer is expected to read the source. *That is fine for ChatdollKit's audience*. It is *not fine for Ember's audience*.

Ember's audience includes operators who *will not read the source*. The default must be *safe-by-default*, not *configurable-to-be-safe*. The Vow of Closed Default (`[[sap:61_NEW_VOWS]]`) demands this. Every CDK default Ember would inherit needs to be *flipped* from "open by default for developer convenience" to "closed by default for operator safety."

The pattern across the refusals is also *recurring*. The API key problem recurred from the Waifu kit. The 0.0.0.0 binding recurred from SAP's VMC. The LLM-authors-emotion problem recurred from SAP's affection system. *These are not unique CDK mistakes; they are pervasive embodied-AI-codebase mistakes*. Ember's refusals are not refusing CDK in particular; they are refusing *the cultural defaults of voice-avatar engineering*.

This is the value of the *triangulation*. With three codices read on the embodiment axis, the *recurring* refusals become visible as *structural* refusals — not specific to a codebase, but specific to the *practice* of embodied-AI engineering. The Cartographer's `[[60_synthesis/60_TRIANGULATION]]` will catalogue the structural pattern.

## XIII. Cross-References

- `[[00_OVERTURE]]` — the Fifth Reading stance.
- `[[01_CDK_ESSENCE]]` — what ChatdollKit wants to be (the essence that the refusals critique).
- `[[02_UNITY_AS_RUNTIME]]` — the trade-off the refusals complicate.
- `[[04_VISION_SYNTHESIS]]` — the triangulation closing with the refusals folded in.
- `[[50_verification/51_SECURITY_REVIEW]]` — Auditor's full threat model.
- `[[50_verification/55_WEBGL_GOTCHAS]]` — Auditor's WebGL-specific attack surface.
- `[[20_interface/27_SOCKET_PROTOCOL]]` — Auditor's SocketServer protocol analysis.
- `[[20_interface/28_JS_BRIDGE_INTERFACE]]` — Auditor's JavaScriptMessageHandler analysis.
- `[[sap:03_ANTI_SAP]]` — Wave 3 sibling refusals (the precedents).
- `[[waifu:00_OVERTURE]]` — Wave 4 sibling refusals (the API key precedent).

## What This Means for Ember

The Anti-CDK refusals fold into Ember's existing Refusal-Citation Discipline. Each refusal carries a file:line that grounds it.

**Adopt:**
- **The Apache-2.0 attribution discipline** as Ember's protocol for any future code adopted from CDK. Per Apache-2.0 §4(c), preserve the CDK header reference in any Ember file derived from a CDK source. Add a `NOTICE` entry listing CDK as an Apache-2.0 source consulted, with one line per adopted pattern. This is *the cost of the Apache-2.0 give*; pay it cheerfully.

**Adapt:**
- **The Refusal-Citation Discipline from Wave 3** (`[[sap:03_ANTI_SAP §What This Means]]`) is reinforced here. Every refusal in this document names file:line. The discipline carries forward to all future codex readings. Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).

**Avoid:**
- **Refusal 1** — credentials in serializable client-side fields. Hjarta-typed credential surface only.
- **Refusal 2** — `IPAddress.Any` binding for any avatar-control protocol. Loopback or typed-Tailnet only.
- **Refusal 3** — LLM-emitted face-tags as primary signal. Hjarta-measured-state-driven override.
- **Refusal 4** — tag-protocol without validation/sanitization/think-block stripping/vocabulary curation.
- **Refusal 5** — JavaScriptMessageHandler without message-origin verification and HMAC.
- **Refusal 6** — Unity-as-foundation. Andlit-unity is the *contained* path if-and-when.
- **Refusal 7** — VRM as default avatar identity. Operator-chosen format only.
- **Refusal 8** — Single-author upstream dependencies. Re-implement in Ember tree with attribution.

**Invent:**
- **The Structural-Refusal Catalogue.** Refusals that recur across multiple codices (API keys in client code: SAP-no, Waifu-yes-refused, CDK-yes-refused-worse; 0.0.0.0 binding: SAP-yes-refused, CDK-yes-refused; LLM-authors-emotion: SAP-yes-refused, CDK-yes-refused) are catalogued as *Structural Refusals* — pervasive embodied-AI-codebase anti-patterns that Ember refuses *categorically* rather than per-codex. The Cartographer's `[[60_synthesis/60_TRIANGULATION]]` formalizes the catalogue; the Auditor's `[[50_verification/57_FAILURE_TAXONOMY]]` orders by impact × likelihood.
- **The Safe-by-Default Inversion Protocol.** Every default flag in any future Ember surface is *flipped* from "open for developer convenience" to "closed for operator safety." `autoStart = true` becomes `autoStart = false`. `IPAddress.Any` becomes `IPAddress.Loopback`. `audio = true` (Waifu pattern) becomes `audio = false; requires_consent = true`. The inversion is universal; it does not require a per-feature ratification. The Vow of Closed Default is the binding.

**Vows touched by this Anti-Document:**
- **Vow of Closed Default** *(Wave 3 proposed)* — *reinforced and formalized as Safe-by-Default Inversion Protocol*.
- **Vow of Defended Credential Surface** *(Wave 4 sharpening of Hermes's Defended System Prompt)* — *reinforced*. The Refusal-1 pattern is the case-in-chief.
- **Vow of Surface Without Surveillance** *(Wave 3 proposed)* — *renewed*. The SocketServer and JS bridge are the surveillance surfaces if defaulted-open.
- **Vow of Embodied Honesty** *(Wave 3 proposed)* — *renewed*. The face-tag-as-LLM-self-report pattern is the case-in-chief.
- **Vow of Modular Authorship** — *renewed*. The single-author bus-factor refusal is direct application.
- **Vow of Smallness** — *renewed*. The Unity-as-foundation refusal preserves smallness.
- **Vow of Public-Friendliness** — *renewed*. The VRM-as-default-avatar refusal preserves Ember's identity-being-the-operator's-choice.

Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c). One-line NOTICE entry per adopted pattern.

The knives are sharpened. The next document binds.

— Sigrún Ljósbrá, the Skald, holding the dark mirror

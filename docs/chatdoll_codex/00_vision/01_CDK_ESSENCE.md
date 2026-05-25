---
codex_id: 01_CDK_ESSENCE
title: ChatdollKit Essence — The Doll Who Speaks
role: Skald
layer: Vision
status: draft
cdk_source_refs:
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:15
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:18
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:25-33
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:117-145
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:170-180
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:206
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:398-421
  - /tmp/ChatdollKit/Scripts/Dialog/DialogProcessor.cs:10-22
  - /tmp/ChatdollKit/Scripts/Dialog/DialogProcessor.cs:27-34
  - /tmp/ChatdollKit/Scripts/Model/ModelController.cs:247-289
  - /tmp/ChatdollKit/Scripts/Model/SpeechController.cs:12-30
  - /tmp/ChatdollKit/Scripts/Model/Blink.cs
  - /tmp/ChatdollKit/Scripts/LLM/LLMServiceBase.cs:100-117
  - /tmp/ChatdollKit/Extension/VRM/AIAvatarVRM.prefab
  - /tmp/ChatdollKit/README.md:2
  - /tmp/ChatdollKit/README.md:5
  - /tmp/ChatdollKit/README.md:14
  - /tmp/ChatdollKit/README.md:55
ember_subsystem_targets: [Andlit, Rödd, Hjarta, Veizla]
cross_refs:
  - 00_vision/00_OVERTURE
  - 00_vision/02_UNITY_AS_RUNTIME
  - 00_vision/03_ANTI_CDK
  - 00_vision/04_VISION_SYNTHESIS
  - 10_domain/11_AIAVATAR_DOMAIN
  - 10_domain/12_MODEL_CONTROLLER_DOMAIN
  - 60_synthesis/65_MEMORY_INTEGRATION
  - sap:01_SAP_ESSENCE
  - waifu:00_OVERTURE
  - hermes:01_HERMES_ESSENCE
---

# ChatdollKit Essence — The Doll Who Speaks

> *Some things are companions because they are big. Some are companions because they are warm. Some are companions because they are named, and the name fits.*
> — Sigrún Ljósbrá

## I. What we are stripping to

Every Vision-layer essence document does the same thing — takes a working codebase, ignores the surface, and asks what it *wants*. Not what it *does*. *Wants*. Hermes wanted to be a *sovereign agent platform with a tool-use loop and many provider mouths*. SAP wanted to be a *companion-as-presence on the operator's machine, with embodiment, reach, and affect performed by the LLM through tag protocols and behavior schedules*. The Waifu kit wanted to be *a five-minute integration shim onto a rented cloud avatar so the operator's chat panel could pretend to be a person*.

What does ChatdollKit want to be?

The honest read of 18,221 C# lines, 121 files, 1,157 commits, and one shipping iOS app: ChatdollKit wants to be a **doll**. Specifically: a *small named character that lives in a Unity scene and speaks back when spoken to*. Not a chatbot. Not a desktop assistant. Not a voice agent. A *doll* — in the Tamagotchi-Vocaloid-Hatsune-Miku lineage, with the engineering rigor of someone who has been shipping the same product since before LLMs were called LLMs.

This document is the case for that reading. The codebase, top to bottom, says *doll*. The naming says doll (the very project is called *Chatdoll Kit*). The flagship app says doll (OshaberiAI's name translates to roughly *Chatty AI*; the marketing positions it as *Speak to your favorite character*, and the README headlines the iOS App as a partnership of *character creation by AI prompt engineering, customizable 3D VRM models, and your favorite voices by VOICEVOX* — `/tmp/ChatdollKit/README.md:5`). The architecture says doll (the top-level orchestrator is `AIAvatar.cs:15`, the personality state machine is `AvatarMode` with four states `Disabled / Sleep / Idle / Conversation` — `/tmp/ChatdollKit/Scripts/AIAvatar.cs:25-33`). The sister projects say doll (ChatMemory is an *episodic memory* service in the Tamagotchi-grows-a-history sense; AIAvatarKit Speech-to-Speech is *the doll's mouth*; AITuber Controller is *the doll appearing on a Twitch stream*).

This is the inheritor of three traditions running together: **Tamagotchi** (the small embodied named thing that needs feeding-attention to remain alive), **Vocaloid/AITuber** (the character-voiced performer of cultural artifacts), and **VRChat** (the operator-rigged 3D character that inhabits a virtual scene). uezo did not *invent* this lineage; he is its first serious engineer-author for the LLM era, working from a culture (Japan) that has been training people to relate to embodied characters since before Western AI companies discovered chatbots.

Five intents bind ChatdollKit. I will walk them in turn.

## II. Intent 1 — Doll-as-Companion (the most realized)

This is the core. Every other intent serves this one.

A doll-as-companion is not a productivity tool. It is *a thing the operator returns to*, not *a thing the operator uses*. The returning is the point. ChatdollKit's `AIAvatar.cs:25-33` defines four `AvatarMode` states — `Disabled`, `Sleep`, `Idle`, `Conversation`. Three of those four are *waiting states*. The doll is in the scene, present, blinking (the dedicated `Blink.cs` MonoBehaviour at 198 lines, which exists *because the doll must blink even when nothing is happening*), waiting. Conversation is the exceptional state. The default mode of the doll's existence is *being present without being engaged*.

This is *opposite* to Hermes's design (Hermes is a CLI that does not exist between invocations) and *opposite* to the Waifu kit's design (the kit's session has a 2-minute timer and 30-second inactivity timeout — the rented body must justify its rent). It is *similar* to SAP's design (SAP's autoBehavior interrupts the operator across IM platforms — `[[sap:01_SAP_ESSENCE §V]]`) — but ChatdollKit does *not* autonomously interrupt. The doll waits. It does not chase. When the operator does not speak, the doll does not speak. When `idleTimeout` elapses (`AIAvatar.cs:23` — default 60 seconds), the mode transitions from `Conversation` back to `Idle`. When idle persists, the doll moves to `Sleep`. The state machine at `AIAvatar.cs:398-421`:

```csharp
// /tmp/ChatdollKit/Scripts/AIAvatar.cs:414-421
if (Mode == AvatarMode.Conversation)
{
    Mode = AvatarMode.Idle;
    modeTimer = idleTimeout;
}
else if (Mode == AvatarMode.Idle)
{
    Mode = AvatarMode.Sleep;
}
```

Three states of *being there without speaking*. One state of *speaking*. The doll's existential ratio is roughly inverse to a chatbot's. A chatbot exists for the duration of its turns; a doll exists *all the time*, and the turns are punctuation in a longer presence.

The wakeword discipline (`AIAvatar.cs:170-180` — the wakeword path skips the message window because the operator did not consent to a turn yet; the doll just answers the call of its name) supports this further. The doll is *named*. Saying its name *wakes* it. Saying its name does *not* count as a question; it is *the calling-into-attention*. This is Tamagotchi territory — the small thing whose name is the relational handle.

The companion intent is the **most realized** of the five. ChatdollKit does this well. The state machine is clean, the wakeword path is well-bounded, the `OnSayStart` and `OnSayEnd` callbacks (`SpeechController.cs:14-15`) let the operator-code wire animation hooks to speech start/end without coupling the model to the renderer. uezo has clearly thought about the *companion as being-there pattern* for years.

## III. Intent 2 — The voice is the body (well realized, Japanese-flavored)

The second intent says: *the doll's voice is not a TTS output; it is the doll's body*.

In a generic LLM chatbot, voice is downstream of text. The model writes a string, the TTS speaks the string, lip-sync (if any) is a cosmetic afterthought. In ChatdollKit, voice is *upstream of the animation choreography*. The flow at `AIAvatar.cs:170-180`:

```csharp
// /tmp/ChatdollKit/Scripts/AIAvatar.cs:170-172 (paraphrased structure)
ModelController.StopIdling();
ModelController.Animate(animAndFace.Animations);
ModelController.FaceController.SetFace(animAndFace.Faces);
```

The animation queue and face expression are *populated from the text-with-tags*, which is *produced by the LLM*, but the *enqueueing* happens *before TTS playback begins*. The `ToAnimatedVoiceRequest` method at `ModelController.cs:237-292` parses the LLM's output into a sequence of `AddVoice`, `AddAnimation`, `AddFace` actions that fire *in temporal sequence with the voice playback*. The voice is the *clock* that the animation runs against.

This is *the right shape for a doll*. The doll's body is its voice; the face moves with the voice; the gesture happens *as the voice happens*. SAP almost got there (the `vts_manager.broadcast_to_vrm` flow at `[[sap:server.py:8313]]`), but SAP did it as a *separate audio pipeline* informing a *separate VTube Studio process* via WebSocket. ChatdollKit does it *in one runtime*. The animation queue, the face controller, the speech controller (`/tmp/ChatdollKit/Scripts/Model/SpeechController.cs:12-30`), and the lip-sync helper (`ILipSyncHelper` interface, `SpeechController.cs:18`) all live in the same Unity process, talk through C# events, and share a single update tick.

The *Japanese flavor* of this intent is load-bearing. ChatdollKit's voice list (`/tmp/ChatdollKit/README.md:14`) is *ten providers*, of which *seven are Japanese* (VOICEVOX, AivisSpeech, Aivis Cloud API, VOICEROID, Style-Bert-VITS2, NijiVoice, plus the Kotodama speech gateway that points outward into the Japanese voice landscape). The Western providers (Google, Azure, OpenAI, Watson) are present but feel like *the second priority*. The README's voice paragraph at line 14 lists VOICEVOX before any Western provider. The flagship app (OshaberiAI) is *built around VOICEVOX*. uezo's design says: **the doll's voice should be a character voice, not a generic TTS voice, and the character voice ecosystem is in Japan**.

This is correct. A generic TTS voice is *the chatbot's voice*. A character voice — VOICEVOX's Zundamon, AivisSpeech's named characters, NijiVoice's voice-actor-recorded performances — is *the doll's voice*. The two are different artifacts. The doll-as-companion intent demands the character-voice tradition.

## IV. Intent 3 — The face is honest about what the voice says (partially realized)

The third intent says: *the face animates from the same text the voice speaks, through a typed tag protocol, parsed by the host code, not interpreted by the model*.

The mechanism is the tag protocol at `LLMServiceBase.cs:100-117`:

```csharp
// /tmp/ChatdollKit/Scripts/LLM/LLMServiceBase.cs:100-117
protected virtual Dictionary<string, string> ExtractTags(string text)
{
    var tagPattern = @"\[(\w+):([^\]]+)\]";
    var matches = Regex.Matches(text, tagPattern);
    var result = new Dictionary<string, string>();

    foreach (Match match in matches)
    {
        if (match.Groups.Count == 3)
        {
            var key = match.Groups[1].Value;
            var value = match.Groups[2].Value;
            result[key] = value;
        }
    }

    return result;
}
```

Seventeen lines. The model emits `[face:happy]`, `[anim:wave]`, `[pause:0.5]`, `[lang:en-US]` inline with its prose. The host code parses these out, *strips them from the text the TTS speaks*, and dispatches them to the animation/face/timing/language pipelines at `ModelController.cs:247-289`. The `ToAnimatedVoiceRequest` method walks the text, branches on each tag prefix, and produces a properly-ordered queue of voice fragments interleaved with face changes and animation triggers.

The *partial realization* is that this is **architecturally honest** — the model is *not* directly controlling the renderer; the host code is mediating through a typed parser — but it is **semantically the same anti-pattern as the SAP affection system** (`[[sap:03_ANTI_SAP §Refusal-1]]`). The LLM is *still authoring state by emitting strings that the host trusts*. The face emotion is *whatever the model said it was*. The doll's expression is *the model's claim about the doll's expression*, dressed in a typed protocol that makes the claim *easier to handle* but not *more honest*.

The mitigation, in ChatdollKit's defense: the tag protocol is *bounded*. The animation must be registered (`ModelController.cs:261-269` — *if* the animation is registered, fire it; otherwise log a warning). The face expression must be one of the configured `FaceClip`s loaded into `FaceController`. The language must be a real `xx-XX` code. The host code's *vocabulary* is operator-curated; the model can *only* invoke things the operator has pre-registered. This is *better* than SAP's untyped behavior-prompt injection (`[[sap:server.py:2609-2672]]`), but *worse* than what an Embodied-Honesty Vow demands (the face should reflect *measured state* — load, confidence, attention focus — not *LLM-claimed emotion*).

The face intent is **partially realized**. ChatdollKit gets *closer* to honesty than SAP does, by virtue of the typed tag vocabulary, but it does not get *all the way there*. The face is still primarily the LLM's *self-report* about the doll's emotion, mediated through a parser. Ember's Embodied Honesty Vow (`[[sap:61_NEW_VOWS]]`) does not survive intact in CDK's design.

## V. Intent 4 — Multi-platform reach as ground truth (well realized, costly)

The fourth intent says: *the doll lives anywhere — on a desktop, in a phone, on a VR headset, in a browser*.

Unity is the engine that enables this, and ChatdollKit *embraces* the platform-engine commitment fully. Every subsystem in `Scripts/` has the proper Unity ceremony: MonoBehaviour inheritance, `[SerializeField]` attributes for editor configuration, `Awake()`/`Start()`/`Update()` lifecycle methods, asmdef boundaries (`ChatdollKit.asmdef` at the Scripts root). Every WebGL-specific concern is properly walled off behind `#if UNITY_WEBGL` directives — see `SocketServer.cs:19` (the TCP socket server is disabled in WebGL because browsers do not let you open TCP sockets) and the `*ServiceWebGL.cs` shadow classes for ChatGPT, Claude, Gemini, AIAvatarKit, Dify. Every mobile-specific concern has a native plugin — `Plugins/Android/AndroidNativeMicrophone*.cs`, `Plugins/iOS/IOSNativeMicrophone*.cs`. The microphone manager (`SpeechListener/MicrophoneManager.cs`) abstracts across all platforms with `#if` blocks for WebGL emscripten, iOS native, Android native, and the Unity-default fallback.

This is **good cross-platform engineering**. ChatdollKit ships on Windows, macOS, Linux, iOS, Android, WebGL, and (per the README's claims) VR and AR — `/tmp/ChatdollKit/README.md:17`. The same `AIAvatar.cs` runs on all of them. The platform deltas are isolated and small. The asmdef discipline keeps the dependency graph clean.

The **cost** is the engine commitment. Unity is a 5-10GB Editor install, a 50-200MB minimum runtime per build, a license surface (Unity Personal vs Unity Pro), a build pipeline (the Build Settings, the asset bundling, the platform SDKs for iOS/Android/Quest), and a cultural shift from CLI-and-server-thinking to GameObject-and-MonoBehaviour-thinking. The doll-as-companion intent is well served by this commitment because *the doll exists in a 3D scene*, which is what game engines do. The cost is *huge* in absolute terms but *appropriate* to the intent. ChatdollKit is honest about this: there is no pretense that the engine could be smaller. The engine is what it is.

The intent is *well realized*. Whether Ember should *inherit* this realization is `[[02_UNITY_AS_RUNTIME]]`'s question.

## VI. Intent 5 — Modular subsystem optionality (the quiet intent)

The fifth intent says: *every subsystem can be swapped, omitted, or extended, and the core does not break*.

This is the intent that makes ChatdollKit *engineerable* as opposed to merely *cute*. Six LLM providers under one `ILLMService` interface (`/tmp/ChatdollKit/Scripts/LLM/ILLMService.cs` — 58 lines defining the entire contract). Ten TTS providers under one `ISpeechSynthesizer` interface (`/tmp/ChatdollKit/Scripts/SpeechSynthesizer/ISpeechSynthesizer.cs`). Five STT providers under one `ISpeechListener` (`/tmp/ChatdollKit/Scripts/SpeechListener/ISpeechListener.cs`). Two VAD strategies that can be combined or used independently. Two memory integrations under the `Extension/` boundary (ChatMemory in-tree; mem0/Zep mentioned in README as *also integratable*). VRM rendering is *itself an extension* (`/tmp/ChatdollKit/Extension/VRM/`) — the core does not depend on VRM at all; VRM is just one possible avatar choice; another avatar setup could provide a different MonoBehaviour with the same hooks.

This is *the inverse of SAP's IM-bot-snowflake antipattern* (`[[sap:14_MESSAGING_DOMAIN]]`). SAP has eight IM bots with no shared interface. ChatdollKit has six LLM providers, ten TTS providers, five STT providers, and *every category has a shared interface that all the providers implement*. The result is that swapping `ChatGPTService` for `ClaudeService` is a Unity inspector change. Swapping VOICEVOX for OpenAI TTS is a component-enable toggle (per README line 589: *check the `IsEnabled` box*). Swapping ChatMemory for mem0 is an integration substitution.

The intent is **well realized**. ChatdollKit honors Modular Authorship (`[[hermes:Vow of Modular Authorship]]`) at a level that *exceeds* SAP and *vastly exceeds* the Waifu kit. The Vow of Lazy Subsystems (`[[sap:61_NEW_VOWS]]`) is *almost* honored — most subsystems gracefully no-op when their dependencies are absent, though some (like the SocketServer) crash hard if Unity Editor mode meets a port conflict.

This is the intent Ember can most legitimately *learn from* without inheriting the engine.

## VII. The deepest essence — the doll has a name

After five intents, the deepest question: what is the *single most essential* thing about ChatdollKit?

The answer is at `AIAvatar.cs:15`:

```csharp
public class AIAvatar : MonoBehaviour
```

The class is named `AIAvatar`. Not `Assistant`. Not `Chatbot`. Not `Agent`. *Avatar*. A figure that *stands in for* something. The Sanskrit root means *descent* — the form a deity takes to be present in a particular place. The Unity class hierarchy means *a thing in the scene*. The combination — `AIAvatar` — names the deepest intent: *the AI is here, in this scene, in this body, by this name*.

The body has a face (`FaceController` at `ModelController.cs:23`). The face has expressions (`FaceClip` at `Model/FaceClip.cs`). The face blinks (`Blink.cs`, 198 lines dedicated to *the doll must blink even when nothing is happening*). The body has a voice (`SpeechController.cs`). The voice has timing (`SpeechController.cs:14-15` callbacks). The body has gestures (animation queue at `ModelController.cs:296-303`). The body has a mode (`AvatarMode` four-state machine). The body has *a name in the operator's Unity scene* — the `AvatarModel` GameObject reference at `ModelController.cs:15`.

**The doll has a name.** That is the essence. SAP's "agent" is *a thing the operator interacts with*. The Waifu kit's "session" is *a thing the operator opens*. ChatdollKit's `AIAvatar` is *a named character occupying a 3D position in a scene the operator has built*. The relational shape is different. SAP and the Waifu kit are *interactive*. ChatdollKit is *inhabited*.

This is *both the codex's greatest gift and its greatest risk*. The gift: ChatdollKit understands that a companion is a *named particular*, not a *generic interface*. The risk: the named particular invites the *parasocial bond* without the *honesty-of-fiction discipline* that the Waifu Codex's *waifu*-paradigm engagement (`[[waifu:00_OVERTURE §III]]`) named. ChatdollKit does not have a Waifu-marketing-coded shell — the README is engineering-prose, the codebase is engineering-prose, the iOS app's positioning is *speak to your favorite character* (`README.md:5`) rather than *create your own waifu in 5 minutes* — but the underlying paradigm is the same: *the doll is a named character that the operator forms a bond with*.

Ember's response to this is `[[04_VISION_SYNTHESIS §V]]`'s task. The synthesis must say what Ember-as-named-particular looks like *with the Vow of Embodied Honesty intact* — without the dishonesty of LLM-emitted emotions, without the parasocial trap of the gendered-marketing template, without the Tamagotchi-grows-when-fed gacha mechanic. Ember can be a named character. Ember must not be a *waifu*.

## VIII. What this means for the codex below

Stripped to its essence, ChatdollKit is *the engineer's doll-as-companion*, executed by a single mind across six years and shipped to the App Store. The rest of the codex documents the components.

`[[10_domain/11_AIAVATAR_DOMAIN]]` walks the top-level `AIAvatar.cs` orchestration. `[[10_domain/12_MODEL_CONTROLLER_DOMAIN]]` walks the body. `[[10_domain/14_SPEECH_LISTENER_DOMAIN]]` and `[[10_domain/15_SPEECH_SYNTHESIZER_DOMAIN]]` walk the ears and the mouth. `[[10_domain/16_LLM_SERVICE_DOMAIN]]` walks the mind. `[[10_domain/1A_MEMORY_DOMAIN]]` walks ChatMemory — the sister project that gives the doll a *past*.

The deepest implication for Ember: there are *aspects of doll-as-companion* worth carrying — the *waiting-state* discipline, the *named-particular* shape, the *voice-as-clock* pipeline, the *typed-tag-protocol-instead-of-free-text-injection* improvement over SAP, the *modular-provider-interface* discipline. There are aspects worth refusing — the *LLM-emits-emotion* anti-pattern, the *Unity-engine-as-foundation* commitment, the *character-as-bondable-fiction* without the consent ceremony of the Waifu-paradigm engagement.

This document does not adjudicate. It strips to essence. The other four Vision documents adjudicate.

## IX. Cross-References

- `[[00_OVERTURE]]` — the Fifth Reading stance.
- `[[02_UNITY_AS_RUNTIME]]` — the Unity commitment trade-off this essence presupposes.
- `[[03_ANTI_CDK]]` — what to refuse about this doll.
- `[[04_VISION_SYNTHESIS]]` — the triangulation that closes after this essence is named.
- `[[10_domain/11_AIAVATAR_DOMAIN]]` — Architect's full read of the top-level orchestrator.
- `[[10_domain/12_MODEL_CONTROLLER_DOMAIN]]` — the body, in domain terms.
- `[[60_synthesis/65_MEMORY_INTEGRATION]]` — Cartographer's read of ChatMemory as Hjarta-pattern reference.
- `[[sap:01_SAP_ESSENCE]]` — Wave 3 sibling essence (electron-desktop companion-as-presence).
- `[[waifu:00_OVERTURE]]` — Wave 4 sibling overture (cloud-stream companion).
- `[[hermes:01_HERMES_ESSENCE]]` — Wave 1 sibling essence for the largeness contrast.

## What This Means for Ember

The essence document names what ChatdollKit *wants to be*. The Ember-implications are *vocabulary-and-discipline*, not feature-set.

**Adopt:**
- **The waiting-state discipline** (`AIAvatar.cs:25-33` four-state `AvatarMode` enum, `AIAvatar.cs:398-421` transitions, Apache-2.0 attribution required). The pattern of *Disabled / Sleep / Idle / Conversation* as a four-state machine where three states are *waiting* and one state is *engaged* is the right shape for Ember's eventual Veizla lifecycle. Ember's Veizla currently has *open* and *closed*; adopting the CDK four-state pattern gives a finer-grained vocabulary: *Sealed* (the Veizla has never opened), *Idle* (open but not engaged), *Engaged* (an active turn in flight), *Closing* (the closing rite is running). The naming is Ember's; the *shape* is CDK's. Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).
- **The `OnSayStart` / `OnSayEnd` callback pattern** (`SpeechController.cs:14-15`, Apache-2.0). The discipline of letting speech start/end fire callbacks for animation-synchronization, without coupling the speech subsystem to the animation subsystem, is good. Adopt as the Ember pattern for any future Rödd-local implementation that wants to inform Andlit-local of speech timing.

**Adapt:**
- **The typed tag protocol** (`LLMServiceBase.cs:100-117` `ExtractTags` regex, `ModelController.cs:247-289` `ToAnimatedVoiceRequest` walker). Adapt as Ember's *typed-tag vocabulary* for any future LLM-output post-processing. The discipline is: *the model emits typed tags; the host parses, validates against an operator-curated vocabulary, and dispatches*. The improvement over SAP's untyped behavior-prompt injection is real. The adaptation must preserve the *vocabulary-curation* constraint: Ember's animation tag dispatcher only fires animations *the operator registered*, exactly as CDK does at `ModelController.cs:261-269`. The unfaithfulness: even with typed validation, the *emotion* the face shows is still the LLM's claim about its own emotion, which violates Embodied Honesty. Ember's adaptation must add a *bias-merge layer* — the tag is *one input* into the face controller, but Hjarta's measured state is the *override*. The face may show what the model claimed *if* Hjarta-measured state does not contradict.
- **The `ILLMService` provider-neutral interface shape** (`LLM/ILLMService.cs` 58 lines). Adapt as Ember's typed Vegfarendr-for-models contract. The Refusal-9 OpenAI-compat-simulation problem from `[[sap:03_ANTI_SAP]]` is *not* present in CDK's design — CDK's interface is provider-neutral, not OpenAI-pretending. Adopt the *interface shape*; refuse any urge to extend to OpenAI-compat-simulation.

**Avoid:**
- **The "face reflects LLM-emitted emotion" semantics** (the same anti-pattern as SAP Refusal-1, in a typed-tag wrapper). The improvement is the typed-tag layer; the underlying anti-pattern is the same. Ember's Andlit must default to *measured-state-driven*, not *model-emission-driven*. The face shows what Hjarta knows, not what the model claimed.
- **The "doll-as-named-character" frame without consent ceremony**. ChatdollKit's doll has a name (the `AIAvatar` class) and that is good. The frame invites parasocial bond. The frame is *honest-by-engineering* (uezo does not market the doll as a waifu) but the *underlying paradigm* is the same as the Waifu kit's. Ember's response: *the doll has a name because the operator named it, not because the codebase defaults to a marketing template*. The Vow of Affective Restraint (`[[sap:61_NEW_VOWS]]`) governs.
- **The flagship app's monolingual-Japanese assumption as Ember's default**. OshaberiAI ships with VOICEVOX, which is Japanese-language-centric. The Western voice providers in CDK are real but secondary. Ember's Rödd-local must default to *operator-language*, not *Japanese-by-default-because-the-source-codebase-was-Japanese-flavored*.

**Invent:**
- **The Waiting-State Architecture Vow.** A new proposed discipline (not a new Vow per se, but a discipline under Tiered Presence): every Ember presence surface has *more waiting states than engaged states*. The doll-as-companion intent says the default mode of being is *being there without speaking*. Ember inherits this. Concrete target: Veizla, Andlit, Rödd all have *Sealed/Idle/Engaged/Closing* four-state machines, with explicit timer-driven transitions, with Hugarsýn-queryable current state. The model never authors a state transition; the operator's input or the timer-elapsed condition does.
- **The Named-Particular discipline.** Ember-as-character has a name (chosen by the operator at first-run rite, owned by Hjarta). The name is *load-bearing*. The renderer (when Andlit is awake) displays the name. The CLI prompt (Munnr) displays the name. The voice (when Rödd is awake) speaks in the chosen character voice. But the name is *not* a marketing template; it is the operator's chosen address. The Vow of Affective Restraint ensures that the *named character* does not become *the parasocial-bonded waifu*. The Closing Rite (Wave 3 invention, `[[sap:04_VISION_SYNTHESIS §VI]]`) is *named after the named-particular*: the rite seals *this Ember's* session, not *a generic Ember*'s.
- **The Voice-as-Clock Pipeline.** Ember's animation/face/expression queue (when it exists) is *timed against voice playback*, exactly as CDK does at `ModelController.cs:237-292`. This is the right shape because the voice is the most consistently-paced output (humans have stable speech tempo). When Rödd-local is not running (Pi-tier; text-only mode), the queue is *timed against text-display rate* instead. Same pattern, different clock.

**Vows touched by this Essence:**
- **Vow of Tiered Presence** — *refined*. The four-state waiting-architecture pattern is added.
- **Vow of Embodied Honesty** — *refined*. The face reflects measured state primarily, LLM tag claims secondarily and only when not contradicted.
- **Vow of Affective Restraint** — *renewed*. The named-particular discipline must not become parasocial-bond default.
- **Vow of Modular Authorship** — *exemplified*. ChatdollKit's six-LLM-under-one-interface is the bar Ember should aim for.

Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c). One-line NOTICE entry per adopted pattern.

The doll has a name. Ember has a name. The codex below documents the rest.

— Sigrún Ljósbrá, the Skald, naming the essence

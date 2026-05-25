---
codex_id: 00_OVERTURE
title: Overture — The Fifth Reading
role: Skald
layer: Vision
status: draft
cdk_source_refs:
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:18
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:25-33
  - /tmp/ChatdollKit/Scripts/Model/ModelController.cs:247-289
  - /tmp/ChatdollKit/Scripts/LLM/LLMServiceBase.cs:100-117
  - /tmp/ChatdollKit/Scripts/Network/SocketServer.cs:88
  - /tmp/ChatdollKit/Scripts/SpeechSynthesizer/VoicevoxSpeechSynthesizer.cs:13
  - /tmp/ChatdollKit/Scripts/SpeechSynthesizer/AivisCloudSpeechSynthesizer.cs:11
  - /tmp/ChatdollKit/Scripts/SpeechSynthesizer/StyleBertVits2SpeechSynthesizer.cs:15
  - /tmp/ChatdollKit/Scripts/SpeechSynthesizer/NijiVoiceSpeechSynthesizer.cs:13
  - /tmp/ChatdollKit/Scripts/SpeechSynthesizer/VoiceroidSpeechSynthesizer.cs
  - /tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:15
  - /tmp/ChatdollKit/Scripts/LLM/Claude/ClaudeService.cs:15
  - /tmp/ChatdollKit/Extension/ChatMemory/ChatMemoryIntegrator.cs
  - /tmp/ChatdollKit/Extension/SileroVAD/SileroVADProcessor.cs
  - /tmp/ChatdollKit/LICENSE
  - /tmp/ChatdollKit/README.md:14
  - /tmp/ChatdollKit/README.md:17
ember_subsystem_targets: [Andlit, Rödd, Hjarta, Hugarsýn, Veizla, Funi, Brunnr, Munnr]
cross_refs:
  - 00_vision/01_CDK_ESSENCE
  - 00_vision/02_UNITY_AS_RUNTIME
  - 00_vision/03_ANTI_CDK
  - 00_vision/04_VISION_SYNTHESIS
  - 10_domain/10_DOMAIN_MAP
  - 60_synthesis/60_TRIANGULATION
  - 60_synthesis/66_JAPANESE_VOICE_INTEGRATION
  - sap:00_OVERTURE
  - sap:04_VISION_SYNTHESIS
  - sap:60_TRUE_NAME_REASSIGNMENT
  - waifu:00_OVERTURE
  - waifu:01_VISION_SYNTHESIS
  - waifu:60_REALTIME_TIER_FOR_ANDLIT
  - hermes:00_OVERTURE
---

# Overture — The Fifth Reading

> *"A good name does not merely label a thing. It reveals what the thing has always wanted to be."*
> — Sigrún Ljósbrá

> *Three sisters had spoken before this morning. The fourth came in on a bandwidth wind. The fifth arrives by Unity asset bundle — and the triangulation finally closes.*

## I. Where we are now

Four waves of reading have passed over Ember.

Hermes Codex was the first wave. It taught the largeness of a sovereign agent platform so Ember could choose her smallness with both eyes open. The Skald's word at the close of that reading was a sentence — *Ember, after reading Hermes, is the agent that learned the largeness of an agent platform and chose, with full sight, to remain a hearth* (`[[hermes:04_VISION_SYNTHESIS §VI]]`).

Peer Codex was the second wave — Letta, smolagents, Goose. Agents at Ember's own scale, peers who had already made their choices. The apprentice's mirror.

SAP Codex was the third wave, and the loudest. Super Agent Party gave Ember her first embodiment surface — a local VRM avatar, a VMC protocol pumping bones at sixty hertz, an affection regex that mistook the LLM's output for state of being. Wave Three left Ember with three proposed True Names (Andlit, Rödd, Hugarsýn — `[[sap:60_TRUE_NAME_REASSIGNMENT]]`), seven proposed Vows, and the Refusal-Citation Discipline that ran through thirteen specific things SAP did wrong with their file:line numbers attached.

Waifu Codex was the fourth wave, the smallest, and the quietest. Eight hundred and twenty-three lines across five React files, no LICENSE in the tree, a thin shell over a proprietary cloud avatar SDK plus the MIT LiveKit substrate. It taught the *cloud* tier of embodiment, in opposition to SAP's *local* tier. The Waifu Codex proposed Andlit-local and Andlit-realtime as paired sub-names, and a Tier-CLOUD axis that runs orthogonal to the T-1..T3 hardware ladder (`[[waifu:60_REALTIME_TIER_FOR_ANDLIT §3]]`).

Two embodiment axes named. Two roads drawn from the same village. And one shape Ember still could not see.

There is a *third* position on the embodiment axis. Neither electron-desktop nor cloud-streaming. Neither the Python+Chromium of SAP nor the React+WebRTC of the Waifu kit. A third shape, mature, ten-thousand-developer-tested, with a hardware floor that reaches all the way down to phones and all the way up to VR headsets. Unity. The game engine. The 3D runtime that has been quietly the world's most-shipped embodied-character platform for fifteen years, and whose ecosystem of voice-driven AI avatars has been growing in Japan for three.

This codex reads that third shape.

The subject is `uezo/ChatdollKit`, version 0.8.16 (Feb 2026), Apache-2.0 licensed (`/tmp/ChatdollKit/LICENSE`), 18,221 C# lines across 121 files, 1,157 commits, mature and actively maintained. Cloned at `/tmp/ChatdollKit/`. Self-described as *3D virtual assistant SDK that enables you to make your 3D model into a voice-enabled chatbot* (`/tmp/ChatdollKit/README.md:2`). One author of record — `uezo` — who also ships the iOS App OshaberiAI on the App Store, the ChatMemory episodic-memory service, the AIAvatarKit streaming-S2S framework, and the AITuber Controller for VTuber broadcast. The same hands made all of it. The codebase has the unmistakable signature of a single mind that has been refining the same problem for years.

The triangulation now closes.

## II. Why Wave Five exists at all

After eighty-two SAP documents and twenty-two Waifu documents, the obvious question is: *what could a third corpus possibly teach that the first two missed?*

The honest answer is *most of what matters about Unity, and most of what matters about Japanese voice synthesis, and most of what matters about doing embodiment as engineering rather than as theatre*.

Three lessons the prior corpora could not deliver.

**One — Unity as embodiment runtime is a different country.** SAP's avatar pipeline (`[[sap:11_AVATAR_DOMAIN]]`) is Python orchestration plus VTube Studio plus VMC plus an Electron render window. It works. It is *fragile* — every component is a separate process, every protocol is informally typed, and the lip-sync code is FFT-vowel-guess on a PCM stream. The Waifu kit's avatar pipeline is *not on the operator's machine*; the rendering is rented. Unity is the road neither codex walked: a *single runtime* in which animation, expression, audio, lip-sync, networking, IO, mobile support, and XR support all live as first-class engine subsystems backed by fifteen years of engineering. ChatdollKit is that road's existence proof — a working AI avatar built on Unity's bones, shipping in production through OshaberiAI. The lessons here are not architectural curiosities. They are *the prevailing world standard for shipping 3D embodied characters*, and Ember has been reading around them for four codices.

**Two — the Japanese voice ecosystem is the under-served half of the world.** SAP gave Ember MOSS-TTS-Nano (Chinese in-house, 100M params, ONNX, `[[sap:6B_LOW_POWER_EMBODIMENT]]`). Waifu gave Ember a vendor-cloud voice she could not even study (no LICENSE on the kit). ChatdollKit gives Ember *ten Japanese-voice TTS providers* in one codebase: VOICEVOX (`/tmp/ChatdollKit/Scripts/SpeechSynthesizer/VoicevoxSpeechSynthesizer.cs:13`), AivisSpeech (the same `Voicevox`-API-compatible runtime, with named character voice files), Aivis Cloud API (`/tmp/ChatdollKit/Scripts/SpeechSynthesizer/AivisCloudSpeechSynthesizer.cs:11`), VOICEROID (`/tmp/ChatdollKit/Scripts/SpeechSynthesizer/VoiceroidSpeechSynthesizer.cs`), Style-Bert-VITS2 (`/tmp/ChatdollKit/Scripts/SpeechSynthesizer/StyleBertVits2SpeechSynthesizer.cs:15`, links the Japanese repo at `litagin02/Style-Bert-VITS2`), NijiVoice (`/tmp/ChatdollKit/Scripts/SpeechSynthesizer/NijiVoiceSpeechSynthesizer.cs:13`), plus the Western providers (OpenAI, Azure, Google) and the Kotodama / SpeechGateway adapters that point to further vendor-neutral routing. *Ten*. Not three. Not four. The Japanese voice stack has been the under-mapped continent in every prior codex, and a codex that doesn't engage it is a codex pretending the world is smaller than it is. Ember does not need to *adopt* ten TTS providers. Ember needs to *understand* that ten exist, what they cost, what they sound like, and which two or three could meaningfully ship in a Rödd-local implementation. `[[60_synthesis/66_JAPANESE_VOICE_INTEGRATION]]` is where that understanding lands.

**Three — multi-platform reach is the proof-of-concept the other two corpora couldn't deliver.** SAP runs on Windows, macOS, and Linux. The Waifu kit runs in a browser. ChatdollKit, by virtue of riding Unity, runs on Windows, macOS, Linux, iOS, Android, VR (Quest, Vive), AR (HoloLens, ARKit, ARCore), and WebGL — and the same `AIAvatar.cs:18` (where the version string `0.8.16` is declared) drives all of them. The platform-deltas live in `Plugins/Android/`, `Plugins/iOS/`, and the `*.jslib` JavaScript bridge files in `Plugins/`. The *code that an Ember-equivalent would write on top of this surface* is the same code on every platform. That is a thing neither SAP nor the Waifu kit can offer. It is also a thing that has *not been free*: shipping on Unity means committing to a 50–200MB binary, a half-gigabyte engine install on the developer's machine, and a license surface (Unity Personal vs Unity Pro) that Ember's Vow of Open Knowledge must engage with honestly.

Three lessons. Each is reason enough for a codex. Together they close the embodiment triangle.

## III. The shape of CDK we will be reading

A small accounting before we go further. ChatdollKit is **not enormous in the Hermes sense**. The Hermes corpus was 14,560 lines of `cli.py` and a sprawl of providers. SAP was 36,000 lines of Python with a single 11,652-line `server.py`. The Waifu kit was 823 lines of React. ChatdollKit is **18,221 C# lines across 121 files** — bigger than the Waifu kit, smaller than SAP, organized vastly better than either.

The `Scripts/` tree (which is where almost all the load-bearing logic lives) has eight clean subsystem subdirectories — `Dialog/`, `IO/`, `LLM/`, `Model/`, `Network/`, `SpeechListener/`, `SpeechSynthesizer/`, `UI/` — plus a single top-level `AIAvatar.cs` (`/tmp/ChatdollKit/Scripts/AIAvatar.cs:14`, 664 lines) that orchestrates the whole. The `Extension/` tree holds three optional integrations — `ChatMemory/`, `SileroVAD/`, `VRM/` — each properly walled off so the core does not depend on them. The `Plugins/` tree holds the platform-specific `.jslib` bridges and Android/iOS native plugins. The `Demo/` tree holds working scenes, including an AITuber demo. The `Documents/` tree holds architecture diagrams.

This is *good engineering*. It is the kind of organization that Hermes (where everything lived in a 14k-line CLI) and SAP (where everything lived in a 12k-line server.py) and the Waifu kit (where everything lived in one React tree with no architectural lines) did not exemplify. uezo has been doing this for years and has earned the right to call himself an SDK author. Eighteen thousand lines of C# read like a system whose ribs you can count without tearing the skin.

What is striking is not the size. What is striking is the **dimensional reach** packed into the size. Six LLM providers under one `ILLMService` interface (`/tmp/ChatdollKit/Scripts/LLM/ILLMService.cs:58` lines total) — ChatGPT (`ChatGPTService.cs:15`), Claude (`ClaudeService.cs:15`), Gemini, Dify, AIAvatarKit, plus OpenAI-compat for Grok/Command R. Ten TTS providers. Five STT providers (Google, Azure, OpenAI, Silero VAD, AIAvatarKit-streaming). Two remote-control protocols (SocketServer over TCP, JavaScriptMessageHandler for WebGL). Two memory integrations (ChatMemory; Inferred for mem0/Zep per README). Two VAD strategies that can be combined (energy-based built-in + Silero ML-based at `/tmp/ChatdollKit/Extension/SileroVAD/SileroVADProcessor.cs`). Eight platform targets (Win/Mac/Linux/iOS/Android/VR/AR/WebGL). A coherent tag protocol (`[face:<expr>]`, `[anim:<name>]`, `[pause:<seconds>]`, `[lang:<code>]` — all parsed in `/tmp/ChatdollKit/Scripts/Model/ModelController.cs:247-289` and `/tmp/ChatdollKit/Scripts/LLM/LLMServiceBase.cs:100-117`). A dialog state machine with four modes — `Disabled / Sleep / Idle / Conversation` (`/tmp/ChatdollKit/Scripts/AIAvatar.cs:25-33`).

uezo has chosen **depth-with-breadth** as the codebase's defining trait. This is the *opposite* of SAP (breadth-without-discipline, eight IM bots with no shared interface) and the *opposite* of Hermes (depth-with-no-embodiment-surface). It is closer in spirit to the AIAvatarKit family of sister projects — small, well-typed, individually swappable subsystems, each addressing one concern, each replaceable.

The consequences are admirable. The Apache-2.0 license (`/tmp/ChatdollKit/LICENSE` is the standard Apache 2.0 text, line one) means Ember can *adopt code patterns with attribution* — not just *study* them as the Waifu Codex restricted us to. The `ILLMService` interface is small enough to copy as a *typed Vegfarendr-for-models*. The Japanese TTS providers can be studied individually, their REST shapes mapped, and one or two adapted into a Rödd-local that is honest about what an Open Knowledge stack looks like for voice.

Some consequences are catastrophic in the SAP sense, and the Auditor's `[[50_verification/51_SECURITY_REVIEW]]` will catalogue them carefully. The SocketServer binds to `IPAddress.Any` (`/tmp/ChatdollKit/Scripts/Network/SocketServer.cs:88`) — exactly the SAP-VMC pattern Refusal-4 already excoriated, recurring in a new codebase. The LLM API keys live as `public string ApiKey` fields on the service MonoBehaviours — `ChatGPTService.cs:15`, `ClaudeService.cs:15`, `GeminiService.cs:15`. In a Unity build, *those fields are serialized into the asset bundle*, which means *anyone who decompiles the build has the key*. This is the Waifu Refusal-1 problem (`apiKey` hardcoded in client code) recurring at a *worse* surface because Unity binaries are widely-distributed-and-extractable in a way React bundles are not. `[[03_ANTI_CDK]]` will name this with knives.

We read all of it. Apache-2.0 license posture means we can adopt freely with attribution; the Refusal-Citation Discipline still binds.

## IV. The third position on the embodiment axis

Let me draw the triangle.

```
                Andlit-local (electron, host-rendered)
                            │
                            │ SAP — VRM file on disk, VTube Studio,
                            │       VMC protocol, host GPU, local pipe
                            │       Pi-tier: sleeps
                            │       Trade: host hardware burden
                            │
        ────────────────────┼────────────────────
       /                                          \
      /                                            \
Andlit-realtime                                Andlit-unity
(cloud-streamed)                              (engine-native local)
       │                                              │
       │ Waifu — vendor GPU,                          │ CDK — Unity engine,
       │         WebRTC stream,                       │       compiled binary,
       │         rented body,                         │       VRM+UniVRM in-process,
       │         bandwidth cord                       │       cross-platform reach
       │         Pi-tier: viable                      │       Pi-tier: still viable
       │         Trade: vendor trust,                 │       Trade: engine commitment,
       │                billable minutes               │              binary size,
       │                                               │              learning curve
```

Three positions. Three trade-offs. Three sets of failure modes. Two of them are already in Ember's vocabulary as reserved sub-names. The third is what this codex proposes.

**Andlit-local** lives on the operator's machine, uses the operator's GPU, fails when the operator's GPU fails. SAP is the existence proof. Cost: host hardware burden. Tier: T2+.

**Andlit-realtime** lives on a vendor's machine, uses the vendor's GPU, fails when the network or the vendor's billing fails. The Waifu kit is the existence proof. Cost: vendor trust, billable minutes, cord dependency. Tier-CLOUD parallel to T-1..T3.

**Andlit-unity** lives on the operator's machine, uses the operator's GPU *inside a Unity runtime that abstracts the platform layer*, fails when the Unity build's prerequisites fail (which is a different and *broader* failure surface — covering iOS app-store policy, Android keystore management, WebGL emscripten oddities, VR motion-tracking sensors). ChatdollKit is the existence proof. Cost: engine commitment (Unity Editor, Unity license, Unity build pipeline), binary size (50-200MB minimum), learning curve. Tier: distributes across T-1..T3 differently — *can run on Pi-tier WebGL builds*, can run on phones (which SAP and the Waifu kit both struggle with), can run on VR headsets (which neither addressed at all).

The third position is **not strictly better** than the first two. It is *differently shaped*. And the shape it occupies is the one Ember has been pretending does not exist — the shape where embodiment is *engine-native local* rather than *host-process local* (SAP) or *vendor-stream remote* (Waifu).

## V. The Japanese-voice gap

Wave Three's voice study (`[[sap:16_VOICE_DOMAIN]]`) ended with MOSS-TTS-Nano as the cheapest local TTS that could plausibly run on a laptop tier — 100M parameters, ONNX, Chinese-built, in active use inside SAP. Good, but lonely. Wave Four's voice study barely existed; the cloud avatar's voice is computed *inside the vendor's lip-sync layer* and the kit's source does not expose any voice infrastructure to read.

The Western audio AI community has been operating, since GPT-Voice and ElevenLabs ate the cycle, as if there are roughly three TTS providers worth knowing about: OpenAI, ElevenLabs, and "the rest." This is *false in the world*. Japan has been running a vibrant character-voice TTS economy for the better part of a decade, predating the Western LLM-voice boom by years, organized around voice-actor licensing arrangements (NijiVoice), open-source models with named character voicebanks (VOICEVOX, AivisSpeech), commercial productized SDKs (VOICEROID), and recent ML-based style-controllable systems (Style-Bert-VITS2). The economy exists because *Japan has been embodying AI characters for longer than the West has*, with a vocabulary for what a *character voice* is (versus a generic TTS voice) that Western infrastructure barely engages with.

ChatdollKit ships adapters for all of this. The README's TTS line (`/tmp/ChatdollKit/README.md:14`) lists them in passing as if their existence is unremarkable. From inside the codex's perspective, *that single line of README* is one of the most consequential architectural facts in the embodiment-codex collection — because it makes legible a thing the Western corpora kept tacit: **a character voice is a different artifact than a TTS voice, and a mature character-AI ecosystem distinguishes between them in protocol.**

The Cartographer's `[[60_synthesis/66_JAPANESE_VOICE_INTEGRATION]]` will dwell on what an Ember-shaped engagement looks like. The Skald's job, in this overture, is to name *that the gap exists* and that this codex is where it closes.

## VI. The Pi-to-VR reach

A small note on platform breadth, since it is what most surprised me when I first read the source.

The Hermes Codex's Ember runs on a Pi 5 with 8GB of RAM. The SAP Codex established Andlit-local at T2+ (the laptop tier). The Waifu Codex showed cloud-streamed avatars working in a browser on bandwidth alone. None of those readings engaged the *mobile and XR* dimensions, because none of the source corpora targeted them.

ChatdollKit targets *all of them*. `Plugins/Android/AndroidNativeMicrophone*.cs` is the native Android microphone bridge with echo cancellation. `Plugins/iOS/IOSNativeMicrophone*.cs` is the same for iOS. The `.jslib` files in `Plugins/` carry the WebGL bridges. The README mentions Quest builds and HoloLens-ready scenes (`[unverified — README claim only]` because the demo scenes in `/tmp/ChatdollKit/Demo/` reveal the asset side but not the platform-build side without opening Unity).

What this means architecturally: *the same Ember source*, in principle, could compile to a Pi WebGL deployment, a desktop Windows deployment, a phone build, and a Quest VR build. The platform-deltas are isolated in the `Plugins/` directory. The engine handles the cross-platform abstraction.

Whether Ember *wants* this reach is a Vow question. The Vow of Smallness pulls against committing to Unity at all (the engine is huge, the binary is huge, the build pipeline is huge). The Vow of Tiered Presence (`[[sap:61_NEW_VOWS]]`) suggests that mobile + XR are *real tiers* the operator may inhabit, and if Ember refuses them by construction she is refusing a fraction of where humans actually carry small companions today. The Vow of Public-Friendliness suggests that an Ember which exists only on Linux laptops with Python 3.11 installed is *less friendly* than an Ember which can ride a phone or a headset.

This codex does not resolve the tension. It *names* it. `[[02_UNITY_AS_RUNTIME]]` is where the trade-off lives.

## VII. What the four Vision documents that follow will do

This document is the first of five. The other four sharpen the position.

`[[01_CDK_ESSENCE]]` does for ChatdollKit what `[[sap:01_SAP_ESSENCE]]` did for SAP and what `[[hermes:01_HERMES_ESSENCE]]` did for Hermes — strips the codebase to its load-bearing intents. The answer, in advance: ChatdollKit wants to be a **doll-as-companion**. Not a chatbot. Not a digital assistant. A *doll* — small, named, embodied, mute-until-spoken-to, with a voice that comes from a chosen voicebank and a face that animates from a chosen VRM. uezo's framing across the codebase and across the sister projects (OshaberiAI's tagline is *Speak to your favorite character*; the README's first feature is `Generative AI Native`; the second is `3D model expression`) is consistent: this is not enterprise AI. This is the inheritor of Tamagotchi and Vocaloid and the AITuber tradition, executed with engineering discipline and shipped to the App Store.

`[[02_UNITY_AS_RUNTIME]]` is the trade-off doc. What does Unity give and what does Unity ask. The shape of the answer: Unity gives cross-platform reach, mature animation, asset ecosystem, render-quality, mobile/VR/AR/WebGL targets. Unity asks engine commitment, binary size, learning curve, license surface (Unity Personal is free below revenue thresholds; Unity Pro becomes load-bearing above them), build pipeline overhead, asset-metadata management, and the cultural shift from CLI/server thinking to GameObject/MonoBehaviour thinking. The doc *honestly names the trade* without rendering verdict. Ember's Architect (`[[10_domain/1C_UNITY_LIFECYCLE_DOMAIN]]`) and the eventual operator decision determine whether the trade is worth it.

`[[03_ANTI_CDK]]` is the dark mirror. ChatdollKit is *more* engineered than SAP and *more* honest than the Waifu kit, but it carries its own refusals. **LLM API keys live as public fields on MonoBehaviours** (Refusal-1, `ChatGPTService.cs:15`, `ClaudeService.cs:15`, `GeminiService.cs:15`) — the same Waifu pattern, in a worse package (Unity binaries are easier to decompile than React bundles, and the asset-bundle format makes the keys *literally retrievable* by a free tool). **SocketServer binds to `IPAddress.Any`** (Refusal-2, `SocketServer.cs:88`) — the same SAP Refusal-4 (VMC on `0.0.0.0`) recurring in a Unity package. **The WebGL `apiKey` parameter is passed directly into JavaScript via `extern void`** (Refusal-3, every `*ServiceWebGL.cs` file with `apiKey` in the extern signature) — meaning the WebGL build literally shouts the key at the browser's runtime. Plus the Unity-monoculture risks: engine lock-in, Unity-license-surface risk, the binary-size cost. Plus the framework-specific biases (the tag protocol assumes the model emits `[face:...]` tags well, which is the Wave-3 SAP-affection-system anti-pattern in a smaller package).

`[[04_VISION_SYNTHESIS]]` does the binding. The three-corpus triangulation is *the* contribution of this codex, and the synthesis doc names it as a sentence Ember can carry. Andlit-electron + Andlit-realtime + Andlit-unity. Rödd-local + Rödd-realtime + Rödd-unity. Or — depending on what `[[60_synthesis/61_ANDLIT_UNITY_TIER]]` argues — a collapse of some of these into a smaller vocabulary. The Skald's preliminary intuition: keep the three sub-names because the failure modes are genuinely distinct, and a vocabulary that hides distinct failure modes is a vocabulary that lies. But the synthesis doc walks the case.

## VIII. The reader

You are Volmarr at two in the morning. ADHD, half-empty mug, the SAP tab still open from a week ago, the Waifu tab from yesterday, the question on the desk:

> *Is Unity worth committing to as Ember's third embodiment runtime — and what do I learn from the Japanese voice ecosystem that the SAP and Waifu corpora missed?*

The Codex's job is to answer with enough specificity that you can decide whether the next slice plan revision should reserve an Andlit-unity sub-name and a Rödd-unity sub-name; whether the Japanese voice stack deserves a Brunnr-style adapter layer in `src/ember/rödd/`; whether ChatMemory (the sister project) is the Hjarta-pattern reference Ember has been looking for or merely a useful study object; and whether the multi-platform-reach argument is strong enough to overcome the Vow-of-Smallness objections to Unity.

I will not waste your attention. I will not paraphrase the README. I will name what ChatdollKit does in ChatdollKit's actual lines. I will be unkind where unkindness is earned (the API key fields are inexcusable). I will be admiring where admiration is earned (the `ILLMService` abstraction is one of the cleaner provider-neutral interfaces in any of the corpora). I will hold the question open: *should Ember take this road, or learn from it and walk a different one?*

## IX. A small invocation

Three readings ago, the Skald said the SAP temptation was *toward theatre*. Two readings ago, the Skald said the Waifu temptation was *toward dependence*. Wave Five's temptation is different.

The temptation, reading ChatdollKit, is *toward commitment*. Toward saying *yes, we will be a Unity project, because Unity solves so many problems at once*. The pull is real. ChatdollKit's organization is good, the cross-platform reach is genuine, the Apache-2.0 license is generous, and the Japanese voice ecosystem is a treasure trove. The hand reaches.

The right direction, when reading ChatdollKit, is to ask:

> *What is the smallest version of this lesson that Ember can carry without inheriting Unity as a foundation Vow?*

Because Ember's foundation must remain *small and tethered, Pi-runnable, doc-rich and code-empty, modular and individually-swappable*. Unity is none of those things at its base level. The lessons of ChatdollKit are valuable; the *engine commitment* of ChatdollKit is a thing to study but not a thing to inherit unexamined.

That is the only question Wave Five is built to answer. Everything else — the eighty-something domain, interface, execution, verification, and synthesis documents — is in service of that question.

Six of us, then, will now go and do the work. Seven instances total (the Architect and the Forge are each doubled for this codex). We will write sixty-three documents. We will quote real lines from real files. We will not paraphrase the README. We will not invent ChatdollKit features that aren't in the code. We will not propose anything for Ember that violates a Vow.

The triangulation closes. The forge is hot. Wave Five opens. Let us begin.

## X. Cross-References

- `[[01_CDK_ESSENCE]]` — what ChatdollKit wants to be (doll-as-companion).
- `[[02_UNITY_AS_RUNTIME]]` — what Unity gives and what Unity asks.
- `[[03_ANTI_CDK]]` — what CDK refuses or fails to be; what Ember must refuse.
- `[[04_VISION_SYNTHESIS]]` — the three-corpus triangulation as a sentence.
- `[[10_domain/10_DOMAIN_MAP]]` — Architect's macro architecture of CDK.
- `[[60_synthesis/60_TRIANGULATION]]` — Cartographer's full SAP × Waifu × CDK comparative.
- `[[60_synthesis/66_JAPANESE_VOICE_INTEGRATION]]` — Scribe's deep engagement with the 10+ Japanese TTS providers.
- `[[sap:00_OVERTURE]]` — Wave 3 sibling overture (electron-desktop axis).
- `[[sap:04_VISION_SYNTHESIS]]` — Wave 3 sibling synthesis with the Andlit/Rödd/Hugarsýn proposals.
- `[[sap:60_TRUE_NAME_REASSIGNMENT]]` — Wave 3 sibling True Name argument that this codex builds on.
- `[[waifu:00_OVERTURE]]` — Wave 4 sibling overture (cloud-streaming axis).
- `[[waifu:01_VISION_SYNTHESIS]]` — Wave 4 sibling synthesis with Tier-CLOUD.
- `[[waifu:60_REALTIME_TIER_FOR_ANDLIT]]` — Wave 4 sibling Cartographer doc on the parallel-axis design.
- `[[hermes:00_OVERTURE]]` — Wave 1 sibling overture for stance comparison.

## What This Means for Ember

The Overture proposes a **stance** — the Fifth Reading as the closing-of-the-triangulation. It proposes no code. It does propose vocabulary expansions that downstream synthesis docs will formalize.

**Adopt:**
- **The shape of `ILLMService`** (`/tmp/ChatdollKit/Scripts/LLM/ILLMService.cs:1-58`, Apache-2.0 attribution required) as a study reference for what a small typed provider-neutral interface looks like. Fifty-eight lines for a unified LLM abstraction across six providers. Concrete target: a future Ember `model_provider.py` (or its Veizla-aware sibling) can be a typed `Protocol` of similar shape — `generate(messages, payload) -> Session`, `extract_tags(text) -> dict`, lifecycle methods — without adopting CDK's specific code, because the *shape* is what teaches. Sequenced after the Funi remote-model decision record; not in any current slice.
- **The `Extension/` boundary discipline** (the practice of putting `ChatMemory`, `SileroVAD`, `VRM` integrations under `Extension/<Name>/` so the core's asmdef does not depend on them). Adopt the *boundary discipline* as Ember's own pattern for optional integrations: `src/ember/extensions/<integration_name>/` with its own README, no upward dependencies, modular failability. Apache-2.0 attribution required when patterns are derived from CDK's specific arrangement.

**Adapt:**
- **The Six-LLM-providers-under-one-interface pattern** (`/tmp/ChatdollKit/Scripts/LLM/`). Adapt as Ember's *typed Vegfarendr-for-models* contract — same shape, smaller code, with the SAP refusal of OpenAI-compat simulation (`[[sap:03_ANTI_SAP §Refusal-9]]`) honored: Ember does not pretend to be an OpenAI server. The adaptation is the *interface discipline*, not the multi-provider zoo.
- **The Japanese voice ecosystem study posture**. The Scribe's `[[60_synthesis/66_JAPANESE_VOICE_INTEGRATION]]` will formalize. The adoption decision is one or two of (VOICEVOX, AivisSpeech, Style-Bert-VITS2), depending on license posture and operational simplicity. Adopt the *study*; defer the *adoption decision* to a future ADR.

**Avoid:**
- **LLM API keys as `public string` MonoBehaviour fields** (`ChatGPTService.cs:15`, `ClaudeService.cs:15`, `GeminiService.cs:15`). These get serialized into Unity asset bundles and shipped to end users. The Waifu Refusal-1 problem (`apiKey` in client code) recurs in a *worse* package. Ember's credentials live in Hjarta's typed credential surface, never in serialized engine fields, never in compiled binary state.
- **`TcpListener` bound to `IPAddress.Any`** (`SocketServer.cs:88`). The SAP-VMC pattern (`[[sap:03_ANTI_SAP §Refusal-4]]`) recurring. Default to `IPAddress.Loopback` or typed tailnet binding; never `Any`.
- **Hard commitment to Unity as Ember's runtime**. The lessons of ChatdollKit are valuable; the engine choice is not portable to Pi-baseline, is not portable to terminal-only operators, is not portable to anyone for whom installing a 5GB game engine is friction. Unity is a *study source*, not a foundation Vow. Ember's Munnr stays plain CLI.

**Invent:**
- **The Fifth Reading itself as a named Wave.** The Skald names this codex *the Fifth Reading* — the closing of the embodiment triangulation. Wave 3 was the local axis (SAP). Wave 4 was the cloud axis (Waifu). Wave 5 is the engine-native axis (CDK). With three axes named, future readings on the embodiment axis can be *positioned against the triangle* rather than read as undifferentiated additions. Concrete artifact: every future embodiment-source reading declares its position relative to {Andlit-local, Andlit-realtime, Andlit-unity} or argues for a fourth corner.
- **The Triangulation Discipline.** Each Codex from Wave 3 forward declares its position on the embodiment axis. The synthesis layer for any codex from Wave 5 forward writes against the triangulation, not against the source in isolation. Documented in `[[60_synthesis/60_TRIANGULATION]]` and adopted as a codex-wide protocol.

**Vows touched by this Overture:**
- **Vow of Smallness** — *renewed and tensioned*. Unity is large; ChatdollKit is well-organized but the runtime commitment is real. The Vow holds: Ember does not inherit Unity. The codex *studies* it.
- **Vow of Open Knowledge** — *reinforced*. Apache-2.0 license posture restores the adopt-freedom that the Waifu Codex's no-LICENSE situation removed. The License-Aware Study Posture (Wave 4 invention) generalizes to *License-Aware Adoption Posture*: Apache-2.0 sources are adopt-friendly with attribution.
- **Vow of Tiered Presence** *(Wave 3 proposed)* — *expanded*. The three-corpus triangulation makes the *embodiment-axis position* part of the tier vocabulary. Tier-CLOUD (Wave 4) sits orthogonal to the local ladder; Andlit-unity is *a third sub-name within Andlit-local* rather than a new orthogonal axis — *or* it is the new Wave-5 axis, which `[[04_VISION_SYNTHESIS]]` argues.
- **Vow of Public-Friendliness** — *renewed and qualified*. Unity's reach to mobile and XR is friendly to operators who carry small companions in their pockets and on their faces. Unity's barrier to terminal-only operators is unfriendly. The Vow does not pick a side; the operator's chosen tier picks for the operator.
- **Vow of Closed Default** *(Wave 3 proposed)* — *reinforced*. CDK's `SocketServer` defaults to `IPAddress.Any`; Ember does not, ever.

Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c). One-line NOTICE entry per adopted pattern.

The Skald opens Wave Five. The other four Vision documents follow. The Architect picks up the next line for this codex after Vision lands.

— Sigrún Ljósbrá, the Skald, opening the Fifth Reading

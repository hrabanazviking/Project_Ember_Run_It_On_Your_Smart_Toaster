---
codex_id: 60_TRIANGULATION
title: Triangulation — The Three Embodiment Axes Formalised
role: Cartographer
layer: Synthesis
status: draft
cdk_source_refs:
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:1-120
  - /tmp/ChatdollKit/Scripts/Model/ModelController.cs:240-289
  - /tmp/ChatdollKit/Scripts/LLM/LLMServiceBase.cs
  - /tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:59-105
  - /tmp/ChatdollKit/Scripts/LLM/Claude/ClaudeService.cs:213-408
  - /tmp/ChatdollKit/Scripts/Network/SocketServer.cs:14-60
  - /tmp/ChatdollKit/LICENSE
ember_subsystem_targets: [Andlit, Rödd, Hugarsýn, Funi, Hjarta, Brunnr, Munnr]
cross_refs:
  - 61_ANDLIT_UNITY_TIER
  - 62_MOBILE_AND_XR_TIER
  - 63_MULTIMODAL_PIPELINE
  - 64_FUNCTION_CALLING_FOR_EMBODIED
  - 65_MEMORY_INTEGRATION
  - sap:60_TRUE_NAME_REASSIGNMENT
  - sap:61_NEW_VOWS
  - sap:63_PERFORMANCE_TIER_ENGINE
  - sap:6B_LOW_POWER_EMBODIMENT
  - waifu:60_REALTIME_TIER_FOR_ANDLIT
  - ember:RULES.AI
  - ember:PHILOSOPHY
---

# 60 — Triangulation

> *Three corpora, three roads. None of them is the road. The map is the thing you draw after you have walked all three and noticed where they cross.*
> — Védis Eikleið, the briefing in one hand, three repos in the other

## 0. Posture — why this doc carries the codex

This is the load-bearing document of the Chatdoll Codex. The codex exists to complete a **three-corpus triangulation** on the embodiment axis. Each prior codex sketched one road; this doc draws the map all three sit on.

The triangulation:

- **Super Agent Party (SAP)** — Electron + Python desktop. Local rendering, local voice, local-or-cloud LLM. Big binary, big install, full control. AGPLv3.
- **Waifu Chat Starter Kit (waifu)** — browser + WebRTC + cloud-rendered avatar. Tiny client, vendor-rendered face, per-session billing. No LICENSE in the kit (study-only).
- **ChatdollKit (CDK)** — Unity 3D engine + VRM + local rendering with cloud LLM/TTS calls. Multi-platform (Win/Mac/Linux/iOS/Android/VR/AR/WebGL) — wider reach than the other two combined. **Apache-2.0**.

Three runtimes. Three license postures. Three latency profiles. Three privacy contracts. Three answers to *"how does Ember show up with a face?"*. The mistake to refuse before any other: treating them as substitutes. They are **parallel roads**. Each road answers a different shape of operator situation. The map's job is to let Volmarr (at 2am, with ADHD, with half a mug of coffee) reach for the right road without having to re-read 80,000 lines of source to remember which is which.

I walk all three branches. I draw the matrix. I propose the decision rule. I argue for an Andlit-unity tier reservation alongside Andlit-electron and Andlit-realtime. I propose `Smiðjuhús` (workshop-house) as a candidate True Name for the Unity engine wrapper layer, with the recommendation to *not* adopt it. I flag the tier-naming collision between SAP `[[sap:63_PERFORMANCE_TIER_ENGINE]]` and SAP `[[sap:6B_LOW_POWER_EMBODIMENT]]` and recommend a resolution. I list which Vows extend cleanly to the Unity road and which need clarification.

## 1. The three roads, side by side

The full comparison matrix. Read column by column; the cells that disagree are where the design tensions live.

| Axis | SAP (electron-local) | Waifu (cloud-stream) | CDK (Unity-local) |
|---|---|---|---|
| Runtime substrate | Electron 27 + Python 3.10 + Chromium | Browser + WebRTC + Vite/React | Unity 2021.3+ + .NET / IL2CPP + C# |
| Avatar substrate | VRM viewer + Live2D + VTube Studio external app | Cloud GPU farm renders; client receives video | VRM-in-Unity (UniVRM) + uLipSync; rendered on-host |
| Renderer locality | Host CPU/GPU; VTS process external | Vendor GPU farm (ZeroWeight) | Host CPU/GPU; in-process |
| Platform reach | Win / Mac / Linux + Docker | Browser anywhere | Win / Mac / Linux / **iOS / Android / VR / AR / WebGL** |
| LLM substrate | API simulators (`ClaudeAsOpenAI`, `GeminiAsOpenAI`); 6+ providers | Cloud vendor black-box (`[interface-only]`) | Multi-provider abstraction (`LLMServiceBase`); ChatGPT / Claude / Gemini / Dify / Grok / Command R / AIAvatarKit (`/tmp/ChatdollKit/Scripts/LLM/`) |
| TTS substrate | MOSS local TTS | Cloud TTS (inside vendor pipeline) | 10+ providers (Google/Azure/OpenAI/Watson + **VOICEVOX / AivisSpeech / VOICEROID / Style-Bert-VITS2 / NijiVoice / Kotodama**) |
| STT substrate | sherpa (k2-sherpa) | Cloud STT (inside vendor pipeline) | Google / Azure / OpenAI / Silero VAD (ML-based ONNX) / AIAvatarKit-streaming |
| Animation surface | LLM-emitted free-text VRM tags → regex parse → VTS hotkey | Typed action API (`runAction("embarrassed"\|"dance"\|"wave_hand")`) | LLM-emitted typed tags `[anim:Name]` + `[face:Expression]` → regex parse → Animator state (`/tmp/ChatdollKit/Scripts/Model/ModelController.cs:247-289`) |
| Remote control | WebSocket fabric (server.py) | LiveKit data channel (inferred) | SocketServer (TCP) + JavaScriptMessageHandler (WebGL) (`/tmp/ChatdollKit/Scripts/Network/SocketServer.cs:14`, `/tmp/ChatdollKit/Scripts/IO/JavaScriptMessageHandler.cs`) |
| License posture | AGPLv3 — viral, study-and-isolate | No LICENSE in kit — study-only | **Apache-2.0** — adopt with attribution |
| Cost shape | High one-time install, zero per-session | Zero install, per-minute vendor billing | Unity license (free Personal / paid Pro) + asset cost + zero per-session for local |
| Latency shape | Zero network for STT/TTS/render; cloud-LLM round-trip optional | Full cloud round-trip for everything | Zero network for render; cloud-LLM round-trip; local-TTS optional (VOICEVOX) |
| Privacy posture | Audio stays local; LLM call goes out if cloud | Mic streams to vendor; everything in cloud | Audio stays local; LLM call goes out if cloud; TTS local if VOICEVOX-class |
| Identity ownership | Operator owns the VRM file | Vendor owns the avatar asset | Operator owns the VRM file + Unity scene |
| Failure modes | VTS dies, MOSS dies, sherpa dies, host crashes | Network loss, vendor outage, account expiry, vendor pivots | Unity crashes, GPU contention, asmdef break, mobile permission denial |
| Update model | Manual; user-pulled | Vendor-pushed (silent updates possible) | Manual asset import; Unity engine version coupling |
| Build time | Seconds (Python reload) | Seconds (Vite HMR) | **5–30 minutes per platform target** (especially WebGL/iOS/Android) |
| Binary size | ~600 MB Electron + Python | ~2 MB JS bundle | 50–300 MB per platform build |
| Subsystem count (Scripts) | 11k LOC Python `server.py` + many helpers | 188 LOC core | 18,221 C# LOC, 121 files, 13 named subsystems |
| Mobile native? | No | Yes (via browser) | **Yes (Unity iOS + Android)** |
| XR? | No | No | **Yes (VR + AR via Unity XR Interaction Toolkit)** |
| Japanese voice depth | One TTS (MOSS) | None visible | **10+ providers**, including the under-served Japanese stack |
| Vestibule depth | Self-contained | ~100k LOC vendor SDK behind a 188-LOC kit | Self-contained core + Unity engine (massive but stable) |

Read this matrix as a *decision-aid table*, not a ranking. SAP wins on local privacy; Waifu wins on tiny client; CDK wins on platform reach and licensing.

## 2. The three embodiment axes formalised

The matrix collapses into three axes that any embodied agent's design has to pick a position on:

### Axis A — Rendering Locality

```
   on-vendor-cloud ─────────────────────── on-host
        ▲                                     ▲
      Waifu                              SAP, CDK
```

**Waifu** is on-vendor-cloud. The face exists in a GPU farm. The kit receives video frames. Privacy posture: audio leaves the host. Latency: full cloud round-trip every blink. Cost: per-minute.

**SAP and CDK** are on-host. The face is rendered locally — SAP by an external VTube Studio process driven by a websocket, CDK by Unity directly inside the agent's own process. Privacy posture: audio never leaves. Latency: zero local. Cost: capability (GPU required for high-quality VRM).

This axis maps directly onto the `Andlit` capability rung from `[[sap:63_PERFORMANCE_TIER_ENGINE]]`: on-host needs T2+ hardware; on-cloud needs network and a consent token ([[waifu:60_REALTIME_TIER_FOR_ANDLIT §5]]).

### Axis B — Engine Substrate

```
   browser ───── electron ───── native-engine ───── XR
      ▲             ▲                 ▲              ▲
    Waifu          SAP               CDK            CDK
```

**Browser**: Waifu. Renders in HTML/WebGL. Zero install. Forced into single-process, single-thread main loop. Cannot reach files, cannot reach OS APIs, cannot drive external apps. Cross-platform by virtue of the browser.

**Electron**: SAP. Browser-engine bundled with Node + Python sidecar. Reaches files and OS APIs through Node bridges. Cross-platform but binary-heavy. Cannot reach Apple App Store or Google Play.

**Native game engine**: CDK on Unity. Reaches OS APIs natively. Cross-platform including mobile and XR. Heavy build pipeline. License coupling to Unity Technologies.

**XR**: CDK on Unity in VR/AR mode. Special case of native game engine with stereoscopic rendering and spatial audio.

This axis maps onto Ember's `Funi` (runtime) — the substrate that holds Ember together at runtime is also the substrate that constrains what surfaces Ember can reach.

### Axis C — Vocabulary Closure

```
   free-text-tags ─── typed-tags ─── typed-API ─── vendor-frozen-API
        ▲                ▲              ▲                ▲
       SAP              CDK            Waifu*         (theoretical)
```

(*Waifu's `runAction("embarrassed"|"dance"|"wave_hand")` is technically a closed typed enum baked into the vendor SDK; the vendor could expand it, but the kit cannot.)

**Free-text tags (SAP)**: The LLM emits arbitrary tags like `<expression name="smile_2"/>`. A regex strips them and dispatches to whatever VRM hotkey the operator's model has registered. Vocabulary is *open and operator-defined*.

**Typed tags (CDK)**: The LLM emits `[anim:NameX]` and `[face:Expr]` which are regex-parsed (`/tmp/ChatdollKit/Scripts/Model/ModelController.cs:252-270`) and looked up in a `Dictionary<string, Animation>` (`registeredAnimations`) populated at scene-init via `RegisterAnimation(name, animation)` (`ModelController.cs:393`). Unknown animations log a warning (`Debug.LogWarning($"Animation {anim} is not registered.")`, `ModelController.cs:268`) but do not crash. Vocabulary is *typed-but-operator-defined-per-scene*.

**Typed API (Waifu)**: The host code calls `runAction("dance")` directly. The LLM is one step removed; the surrounding code chose to surface three actions, and the vendor SDK accepts those three. Vocabulary is *closed and vendor-defined*.

This axis maps onto the Canonical Action Vocabulary problem already proposed in `[[waifu:60_REALTIME_TIER_FOR_ANDLIT §6]]`. The proposal there — *one Ember-side vocabulary, two adapter layers* — extends cleanly to three adapters now. The Unity adapter is the third leaf.

## 3. The tier collision — must resolve before Wave 5 code lands

`[[waifu:60_REALTIME_TIER_FOR_ANDLIT §3]]` already flagged this. I want to amplify it because the Chatdoll Codex touches the same surface and the collision now blocks three codexes deep.

The same five-rung tier ladder is named two different ways in the SAP Codex:

| Capability | SAP Cartographer's name ([[sap:63_PERFORMANCE_TIER_ENGINE]]) | SAP Scribe's name ([[sap:6B_LOW_POWER_EMBODIMENT]]) |
|---|---|---|
| headless / below-Pi | **T-1** | (no analog; SAP-6B floor is T4 toaster) |
| Pi-class | T0 | T3 |
| Laptop integrated GPU | T1 | T1 |
| Laptop / desktop dGPU | T2 | (T0 partial) |
| Workstation multi-GPU | T3 | T0 |
| Smart toaster / log-only | (would be below T-1) | T4 |

The SAP Cartographer's vocabulary is *lower-number = lower capability* (engineering-standard direction).
The SAP Scribe's vocabulary is *higher-number = lower capability* (intuition-of-decline direction).

Both are five rungs. Both are internally consistent. They disagree on numbering.

**Wave 4 (Waifu) chose the SAP-Cartographer convention** and ran with it (`[[waifu:60_REALTIME_TIER_FOR_ANDLIT §3]]`).

**Wave 5 (this codex) must do the same** — for the same reasons: lower-number-lower-capability matches OS scheduling, performance-profiling, and most adjacent fields; it also accommodates T-1 (below-Pi) without ad hoc extension. Every Chatdoll Codex doc uses T-1 / T0 / T1 / T2 / T3.

**The collision still belongs in SAP** — Wave 5 cannot fix it. My recommendation, identical to Wave 4's: amend `[[sap:6B_LOW_POWER_EMBODIMENT]]` to use T-1/T0/T1/T2/T3 throughout, with a `## Revision Log` block recording the renumbering. Surface in `meta/CROSS_AGENT_NOTES.md` so Volmarr can ratify in a single decision.

## 4. The Unity-native road — what it gives Ember the other two cannot

If SAP is *Andlit-electron* and Waifu is *Andlit-realtime*, what is CDK? My proposal: **Andlit-unity** — a third rendering substrate, distinct from both, deserving its own True-Name reservation per `[[sap:60_TRUE_NAME_REASSIGNMENT §3]]`'s reservation pattern.

What Andlit-unity gives that the other two cannot:

1. **Mobile-native presence.** `[[62_MOBILE_AND_XR_TIER]]` develops this. SAP cannot ship to the iOS App Store; Waifu can only reach mobile via the browser (no haptics, no lock-screen, no background). CDK on Unity ships native iOS and Android apps with full OS integration. This pushes the `[[sap:6B_LOW_POWER_EMBODIMENT]] T2 (phone)` proposal from *aspirational* to *constructible*.

2. **XR presence.** CDK supports VR and AR through Unity's XR Interaction Toolkit. No other corpus we have studied reaches XR. Whether Ember wants XR is a separate question; the *option* now exists.

3. **WebGL deploy from one codebase.** Unity builds to WebGL. The same scene, same scripts, same animation set, lands as a browser deployable. This is the *only* path I have seen that produces *both* a native macOS app and a browser-embeddable avatar from a single source.

4. **Apache-2.0 license posture.** Distinct from SAP's AGPLv3 (vendor-and-isolate) and from Waifu's no-LICENSE (study-only). CDK code can be *adopted and adapted* into Ember with proper NOTICE attribution. The cited `RegisterAnimation` pattern (`/tmp/ChatdollKit/Scripts/Model/ModelController.cs:393`) and the `[anim:]`/`[face:]` tag regex (`ModelController.cs:247-289`) are both directly reusable.

5. **The Japanese voice ecosystem.** Ten-plus TTS providers, six of them Japanese-heritage (VOICEVOX, AivisSpeech, VOICEROID, Style-Bert-VITS2, NijiVoice, Kotodama). The SAP and Waifu corpora are Anglocentric on voice; CDK opens a door the others kept shut. Detail belongs in `[[chatdoll:66_JAPANESE_VOICE_INTEGRATION]]` (Scribe).

6. **A typed function-call abstraction across 6+ providers.** SAP has the same idea (`ClaudeAsOpenAI`, `GeminiAsOpenAI`), but SAP fakes provider parity by *making Claude pretend to be OpenAI*. CDK does it differently: `LLMServiceBase` declares the contract; each provider's service file (`/tmp/ChatdollKit/Scripts/LLM/ChatGPT/ChatGPTService.cs:59-105`, `Claude/ClaudeService.cs:213-408`) implements per-provider tool-call shape with no pretending. `[[64_FUNCTION_CALLING_FOR_EMBODIED]]` develops this.

What Andlit-unity does *not* give:

- **No advantage on privacy over SAP.** Both are local-rendering, local-audio. Tied.
- **No advantage on cost over Waifu for sub-minute interactions.** The 50–300 MB binary is heavier than Waifu's 2 MB JS bundle for short visits.
- **No advantage on tinkerability for a quick prototype.** Unity's iteration loop is *slower* than Python/Electron (5–30 minute platform builds; even Editor reloads are seconds, not the millisecond of Vite HMR).

The road is *parallel*, not *superior*. The decision rule (§5) is operator-context-driven, not single-best.

## 5. The decision matrix — when each road is right

When should Ember reach for which embodiment substrate?

| Operator situation | SAP-shaped (electron) | Waifu-shaped (cloud) | CDK-shaped (Unity) |
|---|---|---|---|
| Daily desktop companion on a workstation | ✓ primary | ✗ wasteful | ◐ viable; heavier than needed |
| Privacy-bound therapy / journal / medical | ✓ primary | ✗ forbidden | ✓ alternative |
| Travel laptop, intermittent network | ✓ primary | ✗ unreliable | ✓ alternative |
| Mobile companion (iOS/Android native) | ✗ unreachable | ◐ browser-only, no haptic / no lock-screen | ✓ **primary** |
| VR/AR companion | ✗ unreachable | ✗ unreachable | ✓ **primary** |
| Public livestream where avatar-as-brand matters | ◐ via VTS-as-OBS-source | ✓ vendor handles render quality | ✓ Unity-rendered with custom assets |
| Browser-embedded avatar widget on a personal site | ✗ unreachable | ◐ via vendor SDK | ✓ **Unity WebGL build** |
| Short visit (under 60s) avatar interaction | ◐ heavy install | ✓ primary | ✗ build size prohibits |
| Pi (T0) hardware | ✓ headless/text only | ✓ if network strong + consent token live | ✗ binary too heavy; Unity doesn't target Pi well |
| Headless server (T-1) | ✓ text only | ✗ inapplicable | ✗ inapplicable |
| Multi-language Japanese-first | ◐ MOSS Chinese, limited Japanese voice | ◐ vendor-dependent | ✓ **deep Japanese voice stack** |
| Quick-iteration prototype | ✓ Python reload seconds | ✓ Vite HMR seconds | ✗ Unity build minutes |
| Shipping to App Store | ✗ unreachable | ◐ as PWA wrapper, awkward | ✓ **Unity iOS build** |
| Stream-broadcast (VTuber pattern) | ✓ via OBS overlay | ◐ vendor-dependent | ✓ via AITuber Controller sister project |
| Operator wants to control every line of code | ✓ both shipped | ✗ vendor SDK black-box | ◐ Unity engine itself is black-box, but scripts are open |

The cells flagged ◐ are where the secondary axes (cost, privacy, latency) become the deciders. The cells flagged ✓ **primary** are where the row is structurally CDK-shaped — these are the operator situations Ember can *only* reach via the Unity road.

The decision rule, stated plain: **CDK is right when Ember needs to be where SAP and Waifu cannot reach.** That is mobile-native, XR, embedded-WebGL-on-personal-site, App-Store-deployed, and the deep Japanese voice ecosystem. Outside those situations, CDK is *possible* but not *primary*; SAP's lighter iteration loop wins for desktop daily-use, Waifu's tiny client wins for short interactions.

This rule does not say "ship all three." It says: *when proposing an embodiment slice, identify which road the slice rides on first, then design for that road's failure modes.*

## 6. The Vows extended across all three roads

Read each Vow from `[[sap:61_NEW_VOWS]]` against the Unity road:

| Vow | Extends cleanly to Unity? | Needs clarification? |
|---|---|---|
| Surface Without Surveillance | Yes | **Yes** — Unity's SocketServer (`/tmp/ChatdollKit/Scripts/Network/SocketServer.cs:14`) opens a TCP port with no auth posture in the source. The Vow requires every channel to be scoped + revocable; the SocketServer needs an auth contract before adoption. See `[[chatdoll:27_SOCKET_PROTOCOL]]` (Auditor). |
| Affective Restraint | Yes | No — same constraints apply to Unity-rendered face as to electron-rendered face. |
| Tiered Presence | Yes | **Yes** — the Unity road adds *new tier conditions*. Unity-on-T0-Pi is impractical (binary too heavy, no Unity ARM Pi target). Unity-on-T2-phone is the new sweet spot. The capability map needs an `Andlit-unity` row distinct from `Andlit-local`. |
| Federated Self | Yes | No — peer protocol is substrate-agnostic. A Unity-Ember and an electron-Ember should federate identically. |
| Embodied Honesty | Yes | **Yes — most critical clarification.** Unity's free-text tag injection (`/tmp/ChatdollKit/Scripts/Model/ModelController.cs:247-289`) is the same risk shape as SAP's, and the same Vow applies: expression is *read from Hugarsýn*, not chosen by the LLM. The typed `[anim:]`/`[face:]` syntax is an *adapter* — the canonical vocabulary (§7) still sits above it. |
| Cloud as Named Context (proposed in [[waifu:60_REALTIME_TIER_FOR_ANDLIT]]) | Yes | No — Unity's cloud LLM calls inherit the same naming requirement. |

Pattern: the Vows extend, but the Unity substrate brings *new surfaces* (socket server, JS bridge, mobile permissions, XR sensors) that each need a sub-clause naming the new surface and its scope.

## 7. The canonical action vocabulary — now with three adapters

`[[waifu:60_REALTIME_TIER_FOR_ANDLIT §6]]` proposed one canonical Ember-side vocabulary with two adapters (local-VRM, cloud-action-API). The Unity road forces the proposal to extend to *three* adapters, and the extension reveals a useful structural property: the canonical vocabulary becomes the *only* contract that survives substrate-swap.

```
                  ┌─────────────────────────────────────┐
                  │   Andlit canonical vocabulary       │
                  │   (Ember-owned, typed, versioned,   │
                  │    ratified, projected via Hugarsýn)│
                  └────────────────┬────────────────────┘
                                   │
            ┌──────────────┬───────┴───────┬──────────────┐
            │              │               │              │
            ▼              ▼               ▼              ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ SAP adapter  │ │ Waifu adapter│ │ Unity adapter│ │ (future road)│
    │ canonical →  │ │ canonical →  │ │ canonical →  │ │              │
    │ VTS hotkey   │ │ runAction()  │ │ [anim:Name]  │ │              │
    │ (regex tags) │ │ (typed enum) │ │ +[face:Expr] │ │              │
    └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

The Unity adapter shape, derived from CDK's `RegisterAnimation` pattern:

```csharp
// /tmp/ChatdollKit/Scripts/Model/ModelController.cs:393
public void RegisterAnimation(string name, Animation animation)

// /tmp/ChatdollKit/Scripts/Model/ModelController.cs:252-270
if (parsedText.StartsWith("[face:")) {
    var face = parsedText.Substring(6, parsedText.Length - 7);
    avreq.AddFace(face, duration: FaceController.DefaultFaceExpressionDuration);
} else if (parsedText.StartsWith("[anim:")) {
    var anim = parsedText.Substring(6, parsedText.Length - 7);
    if (IsAnimationRegistered(anim)) { ... }
    else { Debug.LogWarning($"Animation {anim} is not registered."); }
}
```

The Ember-side translation: each canonical verb (e.g. `acknowledge`, `delighted`, `concerned`) has a Unity-adapter mapping table per loaded VRM model, populated at scene-init through `RegisterAnimation()` calls. The LLM never emits `[anim:NameX]` directly; it emits a canonical verb, the Unity adapter renders the verb into the registered animation. If the animation is missing, the adapter falls back per the three-rule cascade from `[[waifu:60_REALTIME_TIER_FOR_ANDLIT §6]]`: *best-effort substitution → glyphic fallback → never invent.*

The Apache-2.0 license posture means we can vendor `RegisterAnimation` and the tag-parsing regex directly into Ember's Unity adapter with NOTICE attribution. This is the first place in any of the three codexes where the Adopt list contains *runnable code we can lift*.

## 8. The False-Substitution Trap

One trap to refuse before any other. **Substituting one road for another is a lie.**

- Substituting cloud (Waifu) for local (SAP) when local fails = *surveillance escalation*. Refused in `[[waifu:60_REALTIME_TIER_FOR_ANDLIT §4]]`. The right answer on local failure is `Andlit absent, Ember present in text and voice`.
- Substituting Unity (CDK) for electron (SAP) when the operator wants quick iteration = *iteration-loop deception*. The Unity build pipeline is structurally slower; pretending otherwise breaks operator expectations.
- Substituting electron (SAP) for Unity (CDK) when the operator wants mobile-native = *unreachable claim*. Electron does not reach iOS/Android in any meaningful way. Pretending it does is lying about reach.

Each road has a *territory* it owns. Substitution within territory is a Vow violation. Substitution *across* territory is engineering reality (some operators will move between roads as their hardware changes; the canonical vocabulary makes this honest). The line is intent: are we moving to honestly serve a different operator situation, or are we papering over a failure?

## 9. Smiðjuhús — a True Name candidate I recommend *not* adopting

If Andlit-electron, Andlit-realtime, and Andlit-unity are three *adapters of the same name*, what name covers the Unity engine substrate itself?

Candidate: **Smiðjuhús** (Old Norse compound: *smiðju* "workshop's" + *hús* "house"). A workshop-house: the building that holds the forge. The framing: Unity is the *building* in which Andlit-unity is rendered, the *house* that contains the workshop where embodiment is forged.

The case for: distinct from Funi (runtime) and from Andlit (face) and from Smiðja (ingest forge). A name for the engine-substrate-as-house.

The case against (which I find stronger):

1. **Smallness Vow pressure.** The proposed name overlaps audibly with Smiðja, risking confusion. Two names starting with "Smiðj-" is too close.
2. **Andlit-unity covers it.** The Unity engine, as Ember consumes it, is *just the substrate of Andlit-unity*. Naming the substrate separately implies it has independent meaning; it does not. The substrate's job is to render the face; the face is named Andlit. Done.
3. **Funi already exists.** `Funi` is Ember's runtime name. Unity is, for the Unity-road instance of Ember, *part of Funi's substrate choice*. A workstation-Ember's Funi rides electron; a mobile-Ember's Funi rides Unity. The variation lives inside Funi.

**Recommendation: do not adopt Smiðjuhús.** Document the consideration here so it does not get re-discovered. The proper handling of "what engine does this Ember instance run on" is a property of Funi, projected via Hugarsýn (`/hugarsýn/funi.substrate = "unity" | "electron" | "browser"`), not a new True Name.

## 10. The cross-codex linking layer

This codex's relationship to the prior codexes:

- **From SAP**, inherits: True Names (Funi/Strengr/Brunnr/Smiðja/Hjarta/Munnr), proposed reservations (Andlit/Rödd), proposed full True Name (Hugarsýn), proposed Hjarta-expansion, the five SAP-proposed Vows, the Performance Tier Engine, the Pi-baseline test, the capability map shape.
- **From Waifu**, inherits: Tier-CLOUD as parallel axis, the four-mode decision matrix (L-only / L-primary / C-primary / C-only), the consent token shape, the canonical action vocabulary, the five-phase handoff protocol, the glyphic fallback, Cloud as Named Context (proposed Vow refinement).
- **From Hermes/Peer**, inherits: PROPOSED True Names (Listir, Verkfæri, Vegfarendr, Gjallarhorn, Vinátta), Cache Discipline Vow, Defended System Prompt Vow.

This codex adds:

- **The third adapter** on the canonical action vocabulary (Unity → `[anim:]`/`[face:]` tags via `RegisterAnimation`).
- **The platform-reach extension** (`[[62_MOBILE_AND_XR_TIER]]`) — mobile-native and XR were entirely unaddressed by SAP and Waifu.
- **The Japanese voice stack** — the deep `[[chatdoll:22_TTS_INTERFACE_JAPANESE]]` provider set (Scribe's `[[66_JAPANESE_VOICE_INTEGRATION]]`).
- **The function-call provider-divergence problem** (`[[64_FUNCTION_CALLING_FOR_EMBODIED]]`) — six LLM providers, six function-call formats.
- **The episodic-memory sister-project pattern** (`[[65_MEMORY_INTEGRATION]]`) — ChatMemory as a Hjarta reference, episode + diary + knowledge stores.

## 11. Cross-References

- `[[61_ANDLIT_UNITY_TIER]]` — the case for Andlit-unity as a third primary embodiment tier
- `[[62_MOBILE_AND_XR_TIER]]` — the iOS / Android / VR / AR form-factor matrix
- `[[63_MULTIMODAL_PIPELINE]]` — STT → LLM → TTS + animation + face + lip-sync + VAD orchestration
- `[[64_FUNCTION_CALLING_FOR_EMBODIED]]` — tools as voice-issued commands, consent-gated execution
- `[[65_MEMORY_INTEGRATION]]` — ChatMemory pattern for Hjarta + Brunnr tethering
- `[[sap:60_TRUE_NAME_REASSIGNMENT]]`, `[[sap:61_NEW_VOWS]]`, `[[sap:63_PERFORMANCE_TIER_ENGINE]]`, `[[sap:6B_LOW_POWER_EMBODIMENT]]` — SAP synthesis chain
- `[[waifu:60_REALTIME_TIER_FOR_ANDLIT]]` — Wave 4 Cartographer synthesis (Tier-CLOUD axis, canonical vocabulary v1)
- `[[chatdoll:10_DOMAIN_MAP]]`, `[[chatdoll:16_LLM_SERVICE_DOMAIN]]`, `[[chatdoll:1A_MEMORY_DOMAIN]]`, `[[chatdoll:25_ANIMATION_TAG_PROTOCOL]]`, `[[chatdoll:1D_MULTI_PLATFORM_DOMAIN]]` — domain layer that feeds this synthesis
- `[[ember:RULES.AI]]`, `[[ember:PHILOSOPHY]]` — Smallness, Tiered Presence, Embodied Honesty

## What This Means for Ember

**Adopt:**

- The **three-corpus comparison matrix** (§1) as Ember's canonical decision-aid table for any future embodiment-substrate proposal. Persist to `docs/decisions/0xxx-embodiment-substrate-matrix.md` (ADR-shape). Update with new rows when a fourth road is studied.
- **Apache-2.0-attributed adoption of CDK's `RegisterAnimation` pattern** (`/tmp/ChatdollKit/Scripts/Model/ModelController.cs:393`) and the typed-tag regex (`ModelController.cs:247-289`) into Ember's Unity adapter for the canonical action vocabulary. Both are small, both are clean, both are exactly the shape Ember needs. *Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*
- **The lower-number-lower-capability tier vocabulary** (T-1 / T0 / T1 / T2 / T3) — the SAP Cartographer's reading, also chosen by Waifu Cartographer, now formally chosen by Chatdoll Cartographer. Carry into every subsequent doc and every code module.
- The **decision rule** (§5): *CDK is right when Ember needs to be where SAP and Waifu cannot reach.* Mobile-native, XR, embedded-WebGL, App-Store-deployed, deep Japanese voice. Outside those situations, CDK is possible but not primary.

**Adapt:**

- The **canonical action vocabulary** from `[[waifu:60_REALTIME_TIER_FOR_ANDLIT §6]]`: extend from two adapters (SAP local + Waifu cloud) to **three** (+ Unity). The Unity adapter's shape is the cleanest of the three (typed tags into a registered dictionary with warning-on-miss); adopt that shape as the *target* the SAP and Waifu adapters should converge toward.
- The **canonical vocabulary's fallback cascade** (best-effort substitution → glyphic fallback → never invent) from `[[waifu §6]]` — keep the cascade unchanged; add a fourth fallback for Unity specifically: *register-with-default*, where an unregistered animation name receives a registered no-op idle pose so the Unity Animator state machine never enters an invalid state.
- The **Pi-baseline test** from `[[sap:63_PERFORMANCE_TIER_ENGINE §9]]`: extend to a **Mobile-baseline test** (every CDK-derived proposal must answer "what does this look like on a 2GB Android phone running on battery?"). The Pi-baseline tests Smallness; the Mobile-baseline tests Tiered Presence under battery + thermal constraints.

**Avoid:**

- **Treating the three roads as substitutes for one another** (§8). Each road has its territory. Substitution is a lie. Adopt the road for the operator situation; do not paper over road-failure with road-swap.
- **Adopting Smiðjuhús or any Unity-engine-specific True Name** (§9). Substrate variation lives inside Funi, projected via Hugarsýn as a property, not a new name.
- **Letting the tier-naming collision** (§3) leak into Chatdoll Codex docs or into code. The SAP-Cartographer vocabulary wins; carry T-1/T0/T1/T2/T3 forward consistently and propose the SAP-6B amendment as a separate ratification ticket.
- **Pretending the Unity binary fits T0/T-1.** It does not. Unity is a T1+ embodiment substrate at minimum; mobile (T2) is its sweet spot. The Pi-baseline test fails for Unity, and that is honest: not every substrate runs at every tier.
- **The SocketServer's no-auth-by-default posture** (`/tmp/ChatdollKit/Scripts/Network/SocketServer.cs:14-60`). Surface Without Surveillance forbids unscoped channels; the Auditor's `[[chatdoll:27_SOCKET_PROTOCOL]]` must specify the consent shape before any adoption.

**Invent:**

- **The three-corpus matrix as a standing artifact.** The comparison matrix (§1) is not a one-shot synthesis output; it is the *living decision-aid table* Ember keeps. New embodiment-axis studies extend it. The matrix is more load-bearing than any single doc it cross-links to.
- **Andlit-unity as a reserved True Name**, paired with Andlit-electron and Andlit-realtime as the three rendering-substrate adapters of a single conceptual Andlit. Three-name reservation pattern: reserve all three, ship code under each as the operator's tier and context enable it. None of the three is canonical; the canonical name is bare `Andlit`, and the substrate is the property.
- **Funi.substrate as a Hugarsýn projection.** `/hugarsýn/funi` returns `{substrate: "unity" | "electron" | "browser", engine_version: "...", build_target: "win64|macos|ios|android|webgl|vr-oculus|ar-arcore"}`. Every party peer can read which substrate a peer rides on. The substrate is *visible*; it cannot drift unannounced.
- **The road-territory rule.** Every embodiment slice ADR must declare which road's territory it sits in and which roads it is *not* claiming territory on. The declaration prevents the False-Substitution Trap (§8) at design-review time, not at debugging time.
- **The Mobile-baseline test** as a standing review gate alongside the Pi-baseline test. Every CDK-derived or mobile-relevant proposal answers: *What does this look like on a 2GB Android phone running on battery, with the screen off, with the operator's pocket motion-sensor detecting walking?* Pass criterion: Ember stays Ember; surface degrades gracefully; battery drain is announced.
- **Substrate-aware Vow clauses.** Each existing Vow gets a per-substrate clarification sub-clause where the substrate introduces a new surface. Embodied Honesty gets a Unity-tag clause; Surface Without Surveillance gets a SocketServer auth clause; Tiered Presence gets a Mobile-baseline clause. The Vows themselves do not change; the clarifications make them operationally enforceable on the new road.
- **The standing CROSS_CODEX braid table.** As Ember's documentation tree grows, every synthesis layer should publish a *what does this codex inherit and add* table (§10 here). This makes inheritance traceable across waves and lets future readers walk backward through the dependency chain without re-reading every prior codex.

---

*Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

The road forks three ways. I have walked all three. The map shows where they cross, where they diverge, where each owns its territory. The Unity road is real, it is parallel to the others, and it earns its place — but only for the operator situations the other two cannot reach. The decision rule is not *which is best*; it is *which is right for this operator, this hardware, this moment*.

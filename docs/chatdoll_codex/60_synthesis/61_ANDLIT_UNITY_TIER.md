---
codex_id: 61_ANDLIT_UNITY_TIER
title: Andlit-Unity — Unity-Native Local Rendering as a Third Embodiment Tier
role: Cartographer
layer: Synthesis
status: draft
cdk_source_refs:
  - /tmp/ChatdollKit/Scripts/AIAvatar.cs:113-150
  - /tmp/ChatdollKit/Scripts/Model/ModelController.cs:17-39
  - /tmp/ChatdollKit/Scripts/Model/ModelController.cs:247-289
  - /tmp/ChatdollKit/Scripts/Model/ModelController.cs:385-410
  - /tmp/ChatdollKit/Scripts/Model/uLipSyncHelper.cs
  - /tmp/ChatdollKit/Scripts/Model/FaceController.cs
  - /tmp/ChatdollKit/LICENSE
ember_subsystem_targets: [Andlit, Funi, Hugarsýn]
cross_refs:
  - 60_TRIANGULATION
  - 62_MOBILE_AND_XR_TIER
  - 63_MULTIMODAL_PIPELINE
  - sap:60_TRUE_NAME_REASSIGNMENT
  - sap:63_PERFORMANCE_TIER_ENGINE
  - waifu:60_REALTIME_TIER_FOR_ANDLIT
  - chatdoll:1B_ANIMATION_DOMAIN
  - chatdoll:29_VRM_INTERFACE
  - chatdoll:50_DEPENDENCY_HEALTH
---

# 61 — Andlit-Unity

> *Two adapters were enough to draw the local↔cloud axis. Three adapters are enough to draw the actual map.*
> — Védis Eikleið, sketching a triangle that finally closes

## 0. Posture — is Andlit-unity a third primary tier, or does it absorb Andlit-electron?

This document answers a structural question the previous codexes left open: **where, exactly, does Unity-native rendering sit?**

Two readings are tempting and wrong:

- **Reading A — "Unity absorbs Andlit-electron."** SAP renders VRM through an external VTube Studio process. CDK renders VRM through Unity directly. Both end in a VRM frame on the operator's screen. If they reach the same destination, why have two names?
- **Reading B — "Unity is its own True Name."** Three rendering substrates, three names: Andlit-electron, Andlit-realtime, Andlit-unity. Clean. Symmetric. Each substrate stands on its own.

I argue against both, and for a third reading:

- **Reading C — Andlit is one True Name with three adapters.** The canonical name `Andlit` covers the embodied face surface. *Andlit-electron, Andlit-realtime, Andlit-unity* are adapter names (`Andlit.adapter ∈ {electron, realtime, unity}`), not separate True Names. Each adapter is a substrate choice; the identity is the face Ember presents to the operator, and that identity is one name across substrates.

The Smallness Vow forces this reading. Three new True Names would inflate the vocabulary; one Andlit with three adapters keeps it small. Identity invariance under tier change ([[sap:63_PERFORMANCE_TIER_ENGINE §6]]) forces it too: an Ember whose face *changes name* when the substrate swaps is an Ember whose identity broke. An Ember whose face *changes substrate* while keeping the name is an Ember being honest about how it is rendered now.

This doc walks the case. It pulls real lines from `/tmp/ChatdollKit/Scripts/Model/`. It compares them to SAP's `vts_manager.py` and the kit's `runAction()`. It draws the adapter contract that all three substrates must satisfy. And it argues for the operator situations in which the Unity adapter is the right one to wake.

## 1. The Unity substrate, from `/tmp/ChatdollKit/Scripts/Model/`

CDK's Andlit-unity surface is structured around `ModelController.cs` — a 464-line MonoBehaviour that owns animation queue, idle dispatch, the registered-animations dictionary, blendshape proxy, and lip-sync. The kit's design choices are visible at the top of the file:

```csharp
// /tmp/ChatdollKit/Scripts/Model/ModelController.cs:17-39
[Header("Animation")]
private float IdleAnimationDefaultDuration = 10.0f;
private string IdleAnimationKey = "BaseParam";
private int IdleAnimationValue;
private string layeredAnimationDefaultState = "Default";
public float AnimationFadeLength = 0.5f;

private List<Animation> animationQueue = new List<Animation>();
private Animation currentAnimation { get; set; }
private Dictionary<string, List<Animation>> idleAnimations = ...;
private Func<Animation> GetAnimation;
private Dictionary<string, Animation> registeredAnimations { get; set; } = ...;
```

Notice the shape. The face is not a stream of frames; it is a *state machine* fed by a *typed queue*. Animations are *registered by name* at scene-init. Idle behavior is a separate queue with its own dispatch function. Crossfade is a single tunable. This is the *Unity Animator* idiom — character animation as transitions between named clips — and CDK consumes it cleanly.

The lip-sync surface (`/tmp/ChatdollKit/Scripts/Model/uLipSyncHelper.cs`) attaches to the audio source rather than driving the audio source. It samples the playing voice clip, runs vowel detection, and emits blendshape coefficient updates to the VRM mouth. Compare with SAP's approach — SAP runs FFT on the *raw PCM stream before it plays*, computes a MouthOpen coefficient, sends it across a websocket to VTube Studio (`vts_manager.py:144-179`). Same problem, different solution: SAP computes externally and pushes; CDK observes internally and reacts.

This difference matters for Ember. The *external-push* shape (SAP) couples lip-sync to whatever can speak to a websocket — flexible across renderers but latency-bound by the websocket. The *internal-observe* shape (CDK) couples lip-sync to whatever can play audio inside Unity — fast and tight but locked to the Unity audio graph. The right Ember adapter for each substrate uses the substrate-native idiom.

## 2. The adapter contract that all three substrates satisfy

Pulling §1 together with the SAP and Waifu equivalents, the canonical Andlit adapter contract is:

```yaml
# Andlit adapter contract (substrate-agnostic, Ember-owned)
adapter_id: unity | electron | realtime | <future>
substrate_version: <semver of underlying engine>
build_target: win64 | macos | linux | ios | android | webgl | vr | ar | <other>

# Required surface
methods:
  render_verb:
    args: { verb: CanonicalVerb, intensity: float, duration_ms: int }
    returns: AdapterResponse  # { rendered: bool, substituted: bool, reason: string }
  render_lipsync:
    args: { pcm_frames: bytes, sample_rate: int }
    returns: AdapterResponse
  enter_idle:
    args: { idle_set: string }  # name of idle pool
    returns: void
  exit_idle:
    args: { reason: string }
    returns: void
  capture_face_state:
    args: { }
    returns: FaceStateSnapshot  # for Hugarsýn projection

# Required projections
hugarsyn:
  - andlit.substrate
  - andlit.last_rendered_verb
  - andlit.queued_verbs
  - andlit.lipsync.active
  - andlit.failure_count_24h
  - andlit.fallback_active

# Required failure announcements
failures:
  - SubstrateUnavailable    # Unity crashed, VTS process dead, network down
  - VerbNotRegistered       # canonical verb has no mapping in this substrate
  - LipSyncDesync           # audio and mouth-shape drift exceeded threshold
  - PerformanceCeilingHit   # frame budget blown; degrading
```

This is the same shape `[[waifu:60_REALTIME_TIER_FOR_ANDLIT §6]]` proposed for two adapters. The Unity adapter slots in as the third leaf without changing the contract — which is the test that the contract was the right abstraction.

For the Unity adapter specifically:

- `render_verb`: looks up the verb in a per-loaded-VRM registration table (populated at scene-init via `RegisterAnimation(name, animation)`, `/tmp/ChatdollKit/Scripts/Model/ModelController.cs:393`); emits an `Animation` into the queue; if unregistered, logs and substitutes the verb with the canonical-fallback ladder.
- `render_lipsync`: wires the active voice audio source into `uLipSyncHelper`; emits blendshape updates per `ConfigurableLipSyncHelper` (`/tmp/ChatdollKit/Scripts/Model/ConfigurableLipSyncHelper.cs`).
- `enter_idle` / `exit_idle`: pushes/pops the idle animation set; `ModelController` already owns the dispatch (`GetAnimation = GetIdleAnimation` at line 60).
- `capture_face_state`: snapshots `currentAnimation.Name`, `FaceController.CurrentFace`, blink state, and queue depth. Project to Hugarsýn at the heartbeat interval.

This is the runnable Adopt-list item from `[[60_TRIANGULATION §11]]`: CDK ships the runnable shape; Ember vendors and renames per Apache-2.0 §4(c) attribution.

## 3. Where does Andlit-unity light up in the tier ladder?

`[[sap:63_PERFORMANCE_TIER_ENGINE §2]]` defines Andlit (the SAP-electron adapter) as lighting up at **T2+**. T0 (Pi) cannot render VRM at acceptable frame rate; T1 (integrated GPU) can run Live2D but struggles with full VRM; T2+ (discrete GPU) is the floor.

Andlit-unity has a *different* tier-floor profile because Unity's renderer scales differently across hardware. The empirical readings:

| Tier | Hardware | Andlit-electron (SAP-VTS) | Andlit-unity (CDK) |
|---|---|---|---|
| T-1 | text-only | ✗ no display | ✗ no display |
| T0 | Pi 4/5, 4GB RAM | ✗ binary too heavy + no GPU | ✗ Unity does not target Pi well; no ARM Linux build out of the box |
| T1 | laptop, 8GB RAM, iGPU | ◐ Live2D viable; VRM struggles | ◐ **Unity Mobile-profile build** is the better match (the same iOS/Android-bound assets running on desktop); full PC build cumbersome |
| T2 | laptop/desktop, dGPU, 16GB | ✓ primary VRM target | ✓ primary VRM target |
| T3 | workstation, multi-GPU, 32GB+ | ✓ rich avatar + stream | ✓ rich avatar + XR + multi-target output |
| (mobile-T2 / phone) | iPhone 12+, Snapdragon 7-gen+, 6GB | ✗ not reachable | ✓ **the Unity adapter's natural home** |
| (XR / Meta Quest 3+) | Quest 3 / Vision Pro | ✗ not reachable | ✓ **only Unity reaches XR** |

The key reading: **Unity is not a strictly-better substrate at every tier; it is a substrate that opens tiers SAP cannot enter.** Mobile-T2 (phone) and XR are *new tier rows* that Andlit-unity adds. Below T2, Andlit-unity is no better than Andlit-electron, and the Unity binary's bulk arguably makes it worse for daily-driver desktop use.

The Hugarsýn projection answers the *what is rendering my face* question:

```
GET /hugarsýn/andlit
{
  "name": "Andlit",
  "active": true,
  "adapter": "unity",
  "substrate": {
    "engine": "Unity",
    "engine_version": "2022.3.21f1",
    "build_target": "ios",
    "device_class": "iphone-15-pro"
  },
  "current_verb": "acknowledge",
  "queued_verbs": ["delighted"],
  "lipsync_active": true,
  "failure_count_24h": 0,
  "tier": {
    "host_rung": "T2-mobile",
    "cloud_axis_active": false
  }
}
```

A party peer reading this knows immediately *which* face Ember is showing where. The substrate is visible. Identity is not.

## 4. The case that Unity does *not* absorb Andlit-electron

Reading A from §0: Unity could render everything SAP-VTS renders, so why keep both?

The case against absorption — five reasons:

1. **Iteration loop. ** SAP's electron-Python loop reloads in seconds. CDK's Unity loop rebuilds in 30s minimum for Editor reload, 5-30 minutes for platform builds (`[[chatdoll:3B_WEBGL_BUILD]]`, `[[chatdoll:3C_MOBILE_BUILD]]`). For a *daily-use desktop companion* where the operator iterates Ember's behavior, the electron loop wins. Unity wins where the *final build* matters more than iteration.

2. **Process-isolation posture.** SAP's external VTS process is, paradoxically, a *safety property*: VRM rendering crashes do not crash the Python agent. Ember's text channel keeps working. Unity's in-process rendering couples the avatar's failure modes to the agent's process — if the Unity scene crashes, the entire agent goes with it. Both have value; the choice is operator-dependent.

3. **VTS ecosystem integration.** VTube Studio is the *de facto* VTuber-tooling standard in 2026. Streamers have OBS scenes wired to VTS. SAP plugs into that ecosystem; CDK is a *parallel ecosystem* (the AITuber Controller sister project, `[[chatdoll:3A_AITUBER_CONTROLLER]]`). An operator already deep in VTS tooling reaches for SAP-shape; an operator starting fresh and wanting mobile/XR reaches for CDK-shape.

4. **Binary footprint.** A T0/T1 operator probably does not want a 250MB Unity binary for *just the face*. The electron approach (Python agent + external VTS) is more granular: only run VTS when avatar is wanted; agent itself is lighter. Unity-shape couples the agent to the engine.

5. **License posture difference.** SAP is AGPLv3, CDK is Apache-2.0. An Ember adoption from SAP is study-and-isolate (cite shape, do not vendor code); an Ember adoption from CDK is vendor-with-attribution. Different license postures produce different code-availability patterns; collapsing both into one adapter would erase the distinction.

Conclusion: **Andlit-unity is parallel to Andlit-electron, not a replacement.** Both are reservations; both are active when the operator's tier and context call for them; the canonical Andlit name covers both with adapter-as-property.

## 5. The case that Andlit-unity is its *own thing*

Reading B from §0: three substrates, three True Names.

The case against three names:

1. **Vocabulary inflation.** Six True Names → Hugarsýn → seven. Adding Andlit/Rödd reservations → nine. Adding *three* Andlit-substrate names → eleven. The Smallness Vow argues each step costs operator orientation, and the cost is non-linear (eleven names is much harder than nine).

2. **Identity collapse risk.** Three distinct names for the *same face* invites the question "*which* face is the real Andlit?" The right answer is "the canonical verb is the face; the adapter is how it is rendered today." Three names obscure the canonical verb behind three substrate-specific surfaces.

3. **Adapter-as-property generalises.** Funi, the runtime, already varies across electron / browser / Unity substrates. Funi did not split into three names. The substrate-as-property pattern is set; Andlit should follow it.

4. **Cross-substrate operations need a unifying name.** When an Ember moves from desktop to phone, the handoff protocol (`[[waifu §7]]`) needs *one* name to refer to the face. *"Hand off Andlit from Andlit-electron to Andlit-unity"* is awkward; *"Hand off Andlit from electron adapter to unity adapter"* is structurally clean.

Conclusion: **adapter-as-property, not adapter-as-name.** Reading C wins.

## 6. The Unity-only operator situations

When is the Unity adapter the *only* right choice? Five situations:

### 6.1 Mobile-native companion

The operator wants Ember on their phone. Not "Ember-as-PWA-in-browser" (no haptics, no lock-screen widget, no background voice). *Ember-as-iOS-app* or *Ember-as-Android-app* with full OS integration. Unity is the only studied substrate that reaches this. Detail in `[[62_MOBILE_AND_XR_TIER]]`.

### 6.2 XR companion

The operator wants Ember in their VR headset (Quest 3, Vision Pro) or as an AR overlay (ARCore, ARKit). Unity's XR Interaction Toolkit is the only door. SAP and Waifu cannot enter this territory.

### 6.3 Embedded-WebGL avatar on operator-owned site

The operator runs a personal site (a blog, a portfolio, a small documentation site for their own work) and wants an Ember avatar embedded there. WebGL build from a Unity scene gives this in one artifact. The Waifu road requires *cloud session per page-load* — billing nightmare. The SAP road requires a *full Electron app per visitor* — unworkable. Unity WebGL is the only viable path.

### 6.4 Custom-rigged VRM with operator-authored animations

The operator has commissioned a VRM model with custom animations (one-off motions specific to their persona). They want those animations *part of the Ember scene*, version-controlled with the rest of the project, not loaded as a separate VTS plugin. The Unity scene-as-project shape gives this; SAP's VTS-as-external-process keeps the animations in VTS's data directory, outside the Ember repo.

### 6.5 Multi-output rendering (avatar + same-scene UI + same-scene 3D environment)

The operator wants Ember *inside a scene* — a virtual room with a Ember avatar plus an interactive 3D environment plus on-screen UI elements, all rendered from one process. Unity is built for this. SAP requires the avatar and the environment to be in different processes (VTS for avatar, something else for environment); Waifu is video-only and cannot host a 3D environment around the avatar.

In situations outside these five, Unity is *possible but not primary*. Daily-driver desktop probably prefers electron. Short-visit browser probably prefers cloud-stream. The decision rule from `[[60_TRIANGULATION §5]]` applies.

## 7. The Unity adapter's failure modes

Each adapter has substrate-specific failure modes. Andlit-unity's, catalogued:

| Failure | Frequency | Detection | Degradation path |
|---|---|---|---|
| Unity Animator state invalid | Rare (asmdef break, missing animation) | `Debug.LogWarning` from `RegisterAnimation` miss | Substitute canonical verb's nearest registered animation; announce `VerbNotRegistered` to Hugarsýn |
| `uLipSyncHelper` desync from audio source | Occasional (Unity audio graph reorder) | Phase comparison vs `AudioSource.time` | Disable lipsync; mouth closes; announce `LipSyncDesync` |
| Mobile GPU thermal throttle | Common on phones under load | `FPSManager` (`/tmp/ChatdollKit/Scripts/UI/FPSManager.cs`) drops below 30 fps for 5s | Reduce blendshape update rate; drop to T2-mobile-degraded; announce `PerformanceCeilingHit` |
| Mobile OS interrupts (call, notification, lock-screen) | Common | `OnApplicationPause(true)` Unity callback | Suspend Andlit; preserve queued verbs; resume on `OnApplicationPause(false)` |
| iOS background audio session loss | Common | `AVAudioSession` interruption | Re-acquire on foreground; queued voice replays from interruption point |
| Android microphone permission revocation | Possible (user revokes mid-session) | `AndroidMicrophoneProvider` exception | Switch to text-only Andlit; announce `MicrophonePermissionLost` |
| WebGL build memory pressure | Common (WASM heap exhaustion) | Browser tab crash | Page-reload prompt; no auto-recovery |
| XR controller disconnect | Common in Quest sessions | XR Interaction Toolkit event | Reduce gesture vocabulary; rely on gaze + voice only |
| Unity scene unload | Rare but catastrophic | `OnDestroy` callback | Re-load scene; preserve Hjarta state from Brunnr |

This catalog is also what `[[chatdoll:57_FAILURE_TAXONOMY]]` (Auditor) develops in depth. The Cartographer notes here that **every adapter publishes its own failure catalog**, and Hugarsýn shows which catalog applies at any moment. An operator debugging *"why did Ember just freeze on my phone"* can look at `andlit.failure_count_24h` and `andlit.last_failure` and see whether it was `PerformanceCeilingHit` (thermal) or `MicrophonePermissionLost` (OS-level revocation) without grepping logs.

## 8. The operator's switching story

Walk through a realistic operator week:

- **Monday morning, desk workstation.** Tier T2; Andlit adapter `electron` lights up (SAP); avatar in OBS overlay; voice via MOSS-equivalent. Iteration loop fast.
- **Monday evening, travel laptop on the train.** Tier downgrades to T1 (no dGPU for battery). Andlit adapter `electron` *sleeps* (per `[[sap:63_PERFORMANCE_TIER_ENGINE §6]]`). Text + voice continue. Hugarsýn announces `andlit.adapter = null; reason = tier-floor unmet`.
- **Tuesday during commute, phone in hand.** Tier registers as T2-mobile (or T1-mobile under battery saver). Andlit adapter `unity` lights up (CDK build of Ember). Avatar on phone screen. Lock-screen widget shows presence pulse (`[[sap:6B_LOW_POWER_EMBODIMENT §4]]`). Hugarsýn announces `andlit.adapter = unity; substrate.build_target = ios`.
- **Wednesday afternoon, livestream session.** Operator opts into the cloud axis (`[[waifu §5]]` consent token issued). Hugarsýn announces `andlit.adapter = realtime; cloud_axis.active = true; scope.audience = livestream-twitch-volmarr`.
- **Thursday VR session.** Tier T3-XR (workstation + Quest 3). Andlit adapter `unity` lights up *for XR target*; same Ember, different rendering build. Hugarsýn announces `andlit.adapter = unity; substrate.build_target = vr-oculus`.

Across all five days, **the canonical name `Andlit` covered the same face**. The adapter changed. The substrate changed. The build target changed. Hugarsýn announced every transition. The operator never had to learn five different face names; they learned one face with five adapters.

This is the value of Reading C (§0) made concrete. Reading B (three True Names) would have forced the operator to learn three separate vocabularies. Reading A (Unity absorbs electron) would have forced the operator to use Unity *for daily desktop use*, where electron is the better iteration substrate. Reading C lets each substrate own its territory while keeping the operator-facing name singular.

## 9. The Apache-2.0 adoption shape

Andlit-unity's Apache-2.0 license posture means the Ember adapter can vendor code directly with attribution. The recommended adoption units, in order of "smallest and cleanest first":

1. **The tag-parsing regex** (`/tmp/ChatdollKit/Scripts/Model/ModelController.cs:247-270`). Twenty lines; trivially clean; the precise shape Ember needs for the canonical verb → typed-tag adaptation. Vendor as `EmberAndlitUnity.Adapters.TagParser` with header citation.

2. **The `Animation` queue + `Dictionary<string, Animation>` registry pattern** (`ModelController.cs:29-39, 385-410`). About fifty lines; the data structure of the adapter's verb-registration table. Vendor as `EmberAndlitUnity.Adapters.VerbRegistry`.

3. **The `uLipSyncHelper` interface shape** (`/tmp/ChatdollKit/Scripts/Model/ILipSyncHelper.cs`). The abstraction over different lipsync implementations. Vendor the interface; reimplement the actual helper to fit Ember's audio graph.

4. **The `IFaceExpressionProxy` interface shape** (`/tmp/ChatdollKit/Scripts/Model/IFaceExpressionProxy.cs`). Same as above: vendor the interface, write Ember's own proxy.

5. **The crossfade timing constant** (`AnimationFadeLength = 0.5f`, `ModelController.cs:27`). Trivial, but worth lifting because it is *empirically tuned* — the kit authors found 0.5s to be the natural crossfade duration. Cite the source line; copy the constant.

The full `ModelController.cs` is *not* a candidate for vendoring — it is too coupled to CDK's specific Animator setup. Vendor the shapes; reimplement the wiring.

Per `[[ember:RULES.AI]]`, every vendored file ships with a header block citing the source path, the commit hash (`/tmp/ChatdollKit/` git HEAD at clone time), the Apache-2.0 license declaration, and Ember's modifications.

## 10. The dependency exposure

Andlit-unity's substrate is Unity. The Cartographer's reading: that is the most significant dependency Ember has considered taking. Unity Technologies' licensing has changed dramatically in the past several years (the 2023 runtime-fee debacle is well-known). Unity is a *vendor* in a way that Electron or Python or the browser are not — Unity has a corporate gatekeeper that can change terms.

Mitigation paths:

1. **Pin Unity LTS.** Use Unity 2022.3 LTS (or whichever LTS is current at slice-plan time) and pin the version in `~/.ember/funi.yaml`. Do not auto-upgrade. The LTS lifecycle is two years; the version pin gives Ember a two-year planning horizon for substrate migration if Unity changes terms.

2. **Maintain Andlit-electron as the desktop primary.** The Unity dependency exposure should not extend to *daily desktop use*. The electron road is independent of Unity Technologies; pinning desktop-primary to electron means Unity-related vendor pivots only affect the mobile/XR adapters, not the operator's daily workflow.

3. **Audit the Unity Asset Store dependencies.** UniVRM is BSD-3-Clause; uLipSync is MIT; UniTask is MIT. These are studied in `[[chatdoll:50_DEPENDENCY_HEALTH]]` (Auditor). Each is its own vendor with its own risk profile.

4. **Open-source alternatives in the watchlist.** Godot 4.x has VRM support; Bevy is Rust-native and growing. Neither is at parity yet, but the watchlist exists. If Unity terms become operator-hostile, Ember has a known migration target.

This is not a Vow; it is a *prudence note*. Adopting Unity as a substrate is a real commitment that the codex should not paper over.

## 11. Cross-References

- `[[60_TRIANGULATION]]` — the three-corpus matrix this doc sits inside
- `[[62_MOBILE_AND_XR_TIER]]` — the form-factor matrix that motivates Unity's territorial claim
- `[[63_MULTIMODAL_PIPELINE]]` — the orchestrated STT→LLM→TTS+animation pipeline that Andlit-unity feeds into
- `[[sap:60_TRUE_NAME_REASSIGNMENT]]` — the Andlit reservation this doc extends
- `[[sap:63_PERFORMANCE_TIER_ENGINE]]` — the tier engine whose capability map this doc adds a row to
- `[[sap:11_AVATAR_DOMAIN]]` — SAP's local-Andlit surface analysis
- `[[waifu:60_REALTIME_TIER_FOR_ANDLIT]]` — the cloud-axis sibling synthesis; canonical vocabulary v1 lives there
- `[[chatdoll:12_MODEL_CONTROLLER_DOMAIN]]` — Architect's deep dive on `ModelController.cs`
- `[[chatdoll:1B_ANIMATION_DOMAIN]]` — the animation tag protocol's domain analysis
- `[[chatdoll:29_VRM_INTERFACE]]` — UniVRM integration interface
- `[[chatdoll:50_DEPENDENCY_HEALTH]]` — Unity LTS, UniVRM, uLipSync version-coupling map
- `[[chatdoll:57_FAILURE_TAXONOMY]]` — the catalogued Unity-specific failure modes

## What This Means for Ember

**Adopt:**

- **Reading C — Andlit as one True Name with adapter as substrate property.** Persist as ADR proposal in `[[chatdoll:67_DECISION_RECORDS]]`. The canonical name is `Andlit`; `andlit.adapter ∈ {electron, realtime, unity, ...}` is the projection axis. Three adapters today; the door stays open for future substrates.
- **CDK's `Dictionary<string, Animation>` registry pattern** (`/tmp/ChatdollKit/Scripts/Model/ModelController.cs:29, 385-410`) as the Unity adapter's verb-registration table shape. Apache-2.0 attribution required. *Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*
- **CDK's tag-parsing regex** (`/tmp/ChatdollKit/Scripts/Model/ModelController.cs:247-270`) for the Unity-adapter's canonical-verb → typed-tag conversion. Twenty lines; lift wholesale.
- **The Unity LTS pin** (`~/.ember/funi.yaml: unity_version: "2022.3-LTS"`) as a standing prudence note. Update only on operator-confirmed migration.

**Adapt:**

- **The substrate-aware Hugarsýn projection** (§3 schema). Build `/hugarsýn/andlit` to return `{name, active, adapter, substrate, current_verb, queued_verbs, lipsync_active, failure_count_24h, tier}`. The schema serves all three adapters; each adapter populates its own fields.
- **SAP's `vts_manager.py:144-179` PCM-FFT lipsync** (AGPLv3 — study only) — adapt the *shape* (PCM → vowel detection → MouthOpen coefficient) but reimplement clean for both Ember's electron adapter and as a Unity-native variant. Do not vendor SAP code; reimplement against the substrate-appropriate audio graph.
- **The handoff protocol** from `[[waifu:60_REALTIME_TIER_FOR_ANDLIT §7]]`: extend Trigger / Consent / Establish / Crossover / Stabilise to handle **adapter handoffs** as well as substrate handoffs. The protocol stays five-phase; the inputs broaden to include `adapter_from` and `adapter_to`.

**Avoid:**

- **Reading A (Unity absorbs Andlit-electron).** Electron's iteration loop and ecosystem-integration value are real. The Unity binary is too heavy for daily desktop use. Keep both adapters; each owns its territory.
- **Reading B (three separate True Names).** Vocabulary inflation; identity collapse risk. The canonical name `Andlit` with adapter-as-property is the right shape.
- **Vendor-coupling Unity at the runtime layer.** Unity's vendor pivots have history. Keep the desktop primary on electron so that Unity-related disruption only hits the mobile/XR adapters.
- **Vendoring `ModelController.cs` wholesale.** Too coupled to CDK's specific Animator setup. Vendor the *shapes* (registry, regex, queue); reimplement the wiring.
- **Auto-upgrading Unity LTS without operator consent.** A Unity version change can break asmdef and break adoption; the version pin is a Vow-of-Stability move.

**Invent:**

- **Adapter-as-property pattern for True Names that span substrates.** Andlit is the first True Name to formalize this; the pattern generalizes. Funi and Rödd are next candidates (substrate-varied runtime, substrate-varied voice). The pattern's invariant: *one canonical name, one canonical contract, multiple adapters, adapter visible in Hugarsýn*.
- **Per-adapter failure catalog as a published artifact.** Each adapter ships a catalog (§7 here is Andlit-unity's). Hugarsýn projects the active catalog and the recent failures. Operators reading `andlit.last_failure` see the failure name from the catalog, not a freeform string.
- **The five Unity-only operator situations** (§6) as the *only* set of contexts in which the Unity adapter is the primary choice. Document as a discipline gate: a slice proposal that names "Unity adapter" must locate itself in one of these five rows or argue for a sixth.
- **The Unity LTS pin as a Vow-of-Stability-shaped commitment.** Not a Vow in itself, but a documented prudence rule that the slice plan honors. Document with the version, the LTS expiry date, the migration target candidates.
- **The mobile-T2 tier-row addition to the capability map.** `[[sap:63_PERFORMANCE_TIER_ENGINE §2]]`'s capability map currently has T0/T1/T2/T3 rows. The mobile case is structurally distinct (phone-T2 is *not* laptop-T2). Propose adding a `T2-mobile` row to the capability map with its own Andlit-unity entry; the row's hardware floor is "Snapdragon 7-gen or Apple A14+, 4GB RAM, dedicated mobile GPU." This row is what `[[62_MOBILE_AND_XR_TIER]]` builds on.
- **The substrate-watchlist artifact.** A small markdown file at `docs/decisions/substrate_watchlist.md` tracking Godot 4.x, Bevy, and any other potential Unity-alternative substrates. Updated when relevant news lands. Not a commitment; a *peripheral awareness* document so a future migration is not started cold.

---

*Apache-2.0 attribution: when adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

Three adapters for one face. The map closes. Unity is parallel, not superior, not subordinate. It owns the territory the others cannot reach. The canonical name stays singular; the substrate is honest about itself; the operator never has to choose between vocabularies, only between roads.

---
codex_id: 29_VRM_INTERFACE
title: VRM Interface — Three Interfaces, Four Implementations, One Runtime Loader
role: Architect
layer: Interface
status: draft
chatdoll_source_refs:
  - Extension/VRM/VRMLoader.cs:1-121
  - Extension/VRM/VRMBlink.cs:1-119
  - Extension/VRM/VRMFaceExpressionProxy.cs:1-94
  - Extension/VRM/VRMuLipSyncHelper.cs:1-27
  - Extension/VRM/AIAvatarVRM.prefab
  - Scripts/Model/IBlink.cs
  - Scripts/Model/IFaceExpressionProxy.cs
  - Scripts/Model/ILipSyncHelper.cs
  - Scripts/Model/uLipSyncHelper.cs
  - Scripts/Model/VRCFaceExpressionProxy.cs
ember_subsystem_targets: [Andlit]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/12_MODEL_CONTROLLER_DOMAIN
  - 10_domain/1B_ANIMATION_DOMAIN
  - 20_interface/25_ANIMATION_TAG_PROTOCOL
  - sap:11_AVATAR_DOMAIN
  - waifu:20_ZEROWEIGHT_SURFACE
---

# VRM Interface
## Three Interfaces, Four Implementations, One Runtime Loader

*— Rúnhild Svartdóttir, Architect*

> *VRM is the open standard for 3D character models with semantics. UniVRM is the Unity-side runtime. ChatdollKit's integration is three Unity interfaces and four concrete implementations — a textbook case of interface-segregation paying off, twice. The cost is one substantial third-party dependency. The benefit is that swapping VRM for Live2D or for nothing-at-all is implementing three small interfaces.*

`Extension/VRM/` is **four files** (`VRMLoader.cs` 121 LOC + `VRMBlink.cs` 119 LOC + `VRMFaceExpressionProxy.cs` 94 LOC + `VRMuLipSyncHelper.cs` 27 LOC) + the prefab `AIAvatarVRM.prefab`. Combined: 361 lines of C# + one binary asset. This integrates the VRM 3D character model standard into CDK by implementing **three interfaces declared in `Scripts/Model/`** — `IBlink`, `IFaceExpressionProxy`, `ILipSyncHelper` — each one a small adapter onto VRM's `VRMBlendShapeProxy`.

The architectural lesson is **interface segregation at the embodiment boundary**. CDK's core does not depend on UniVRM; it depends on three interfaces. Anyone with a different 3D character standard (Live2D, custom rigged models, MMD) implements the same three interfaces and substitutes. The interface boundary is the surface across which CDK does *not* know what model standard is in use.

Compare SAP's VRM use ([[sap:11_AVATAR_DOMAIN]]) — VRM-specific code is mixed with avatar logic; substitution is harder. Compare Waifu's avatar ([[waifu:20_ZEROWEIGHT_SURFACE]]) — cloud-rendered; no on-device model standard. **CDK is the only corpus with a clean substitution boundary for the 3D character standard.**

---

## 1. The Three Interfaces

### 1.1 `IBlink` — eye-closing for liveness

`Scripts/Model/IBlink.cs` (the interface; ~5 LOC):

```csharp
public interface IBlink
{
    void Setup(GameObject avatarObject);
    UniTask StartBlinkAsync();
    void StopBlink();
}
```

Three methods. `Setup` is called with the loaded avatar GameObject (the VRM character, post-load). `StartBlinkAsync` begins the eye-closing loop. `StopBlink` halts it. The blink loop owns its own coroutine; the consumer just toggles.

**The interface is for *liveness*** — closing eyes at random intervals so the avatar doesn't look like a corpse. Independent of expression, animation, voice. Runs in `LateUpdate` (after animation has placed bones); blends a blendshape weight up to 1 (closed) and back to 0 (open) over short intervals.

### 1.2 `IFaceExpressionProxy` — expression-by-name

`Scripts/Model/IFaceExpressionProxy.cs`:

```csharp
public interface IFaceExpressionProxy
{
    void Setup(GameObject avatarObject);
    void SetExpression(string name, float value);
    void SetExpressionSmoothly(string name, float value);
}
```

Four methods (counting `Setup`). `SetExpression(name, value)` instantly applies a named expression (`"Joy"`, `"Sad"`, etc.) at the given blendshape weight. `SetExpressionSmoothly` does the same with a smooth-damp transition.

**The interface is by-name.** The consumer (`FaceController`) calls `SetExpressionSmoothly("Joy", 1.0f)`; the implementation knows how to translate `"Joy"` to a VRM blendshape (or whatever the underlying model standard's expression mechanism is). The face-name vocabulary is *defined by the model's content*, not by the interface — VRM models with a "Joy" blendshape support it; models without don't.

### 1.3 `ILipSyncHelper` — viseme-to-blendshape mapping

`Scripts/Model/ILipSyncHelper.cs`:

```csharp
public interface ILipSyncHelper
{
    void ConfigureViseme(GameObject avatarObject);
    void ResetViseme();
}
```

Two methods. `ConfigureViseme` is called with the avatar to set up the **viseme blendshape map** — the dictionary connecting lip-sync vowel detections (`A`, `I`, `U`, `E`, `O` for Japanese; `N`, `-` for nasal/silence) to specific blendshape indices on the avatar. `ResetViseme` zeroes all viseme blendshapes (between utterances).

The actual lip-sync *animation* happens in `uLipSync` (third-party package) which reads PCM samples and triggers blendshape updates based on detected vowels. This interface configures the *map* between uLipSync's vowel detections and the model's specific blendshape indices.

---

## 2. The VRM Implementations

### 2.1 `VRMLoader` — the runtime loader

`Extension/VRM/VRMLoader.cs` (121 LOC). The most interesting file in the extension. The `LoadCharacterAsync` (lines 67-119) is the runtime VRM-file load:

```csharp
public async UniTask LoadCharacterAsync(byte[] vrmBytes) {
    IsCharacterReady = false;
    try {
        modelController.DeactivateAvatar(() => {
            if (vrmInstance != null) Destroy(vrmInstance);
            if (characterObject != null) Destroy(characterObject);
        });

        var gltfData = new GlbBinaryParser(vrmBytes, "UserVrm").Parse();
        var vrmData = new VRMData(gltfData);
        var context = new VRMImporterContext(vrmData);
        vrmInstance = await context.LoadAsync(new RuntimeOnlyAwaitCaller());
        foreach (var renderer in vrmInstance.GetComponentsInChildren<SkinnedMeshRenderer>()) {
            renderer.receiveShadows = false;
        }
        context.Dispose();

        characterObject = vrmInstance.gameObject;
        characterObject.name = "CharacterVRM";
        var animator = characterObject.GetComponent<Animator>();
        animator.runtimeAnimatorController = animatorController;
        modelController.ActivateAvatar(characterObject, true);
        await UniTask.Delay(WaitBeforeShowCharacter);
        vrmInstance.ShowMeshes();

        OnCharacterReady?.Invoke(characterObject);
        IsCharacterReady = true;
    } catch (Exception ex) {
        Debug.LogError($"Error at LoadCharacterAsync: {ex.Message}\n{ex.StackTrace}");
    }
}
```

Steps:
1. Deactivate any current avatar; destroy old VRM instance.
2. Parse the GLB binary (VRM is a GLB-based format).
3. Construct `VRMImporterContext`; async-load via UniGLTF.
4. Disable shadow-receiving on all skinned meshes (lighting choice).
5. Apply the user-configured `animatorController` to the loaded VRM.
6. Hand the new GameObject to `ModelController.ActivateAvatar`.
7. Wait a configured delay, then show meshes (avoids first-frame flash).
8. Fire `OnCharacterReady` event.

**The interesting feature: VRM models can be loaded from URLs.** Lines 36-46:

```csharp
if (VRMFilePath.StartsWith("http://") || VRMFilePath.StartsWith("https://")) {
    _ = LoadCharacterAsync(VRMFilePath, "GET");
}
```

The avatar can be a **runtime-downloaded asset**, not a pre-baked prefab. The user can swap their avatar in a deployed app by changing a URL. This is the *VRoid Hub* integration pattern — VRoid Hub is uezo-ecosystem-friendly avatar marketplace; CDK avatars can be downloaded from it at runtime.

**The shader caution** (lines 32-34):

```csharp
Debug.LogWarning("**CAUTION** YOU MUST INCLUDE SOME SHADERS TO BUILD RUNTIME LOAD APP.");
```

Unity's build stripping removes shaders not referenced by any scene; runtime-loaded VRM models reference shaders the build couldn't predict. The user must manually include the VRM shaders (UniVRM has a documented list) in the "Always Included Shaders" project setting. **A failed shader include → bright pink avatar (the missing-shader colour).** This is a real production gotcha; CDK warns about it loudly.

### 2.2 `VRMBlink` — random-interval eye closure

`Extension/VRM/VRMBlink.cs` (119 LOC). The blink loop (lines 70-87):

```csharp
while (true) {
    if (blinkTokenSource.Token.IsCancellationRequested) break;

    // Close eyes
    blinkIntervalToClose = UnityEngine.Random.Range(minBlinkIntervalToClose, maxBlinkIntervalToClose);
    await UniTask.Delay((int)(blinkIntervalToClose * 1000));
    blinkAction = CloseEyesOnUpdate;

    // Open eyes
    blinkIntervalToOpen = UnityEngine.Random.Range(minBlinkIntervalToOpen, maxBlinkIntervalToOpen);
    await UniTask.Delay((int)(blinkIntervalToOpen * 1000));
    blinkAction = OpenEyesOnUpdate;
}
```

Two `Random.Range` intervals (3-5s closed; 0.05-0.1s open). The `blinkAction` field points to either `CloseEyesOnUpdate` or `OpenEyesOnUpdate` — called by `LateUpdate` (line 38-40) to apply blendshape weight changes via smooth-damp.

**The blink-loop pattern**: alternating delays + LateUpdate-driven blendshape updates. The delays sleep on the UniTask scheduler (off-main-frame); the actual animation runs every frame. Cooperation between async timing and per-frame rendering.

The blendshape used is `BlendShapeKey.CreateFromPreset(BlendShapePreset.Blink)` — VRM's standard "blink" preset. Every conformant VRM model has this preset; the implementation works on any VRM without per-model configuration.

### 2.3 `VRMFaceExpressionProxy` — by-name to blendshape with smooth-damp

`Extension/VRM/VRMFaceExpressionProxy.cs` (94 LOC). The smoothly-transitioning expression apply (lines 26-62):

```csharp
private void Update() {
    if (blendShapeProxy == null || blinker == null) return;

    if (changeStartAt > 0) {
        if (currentFaceName == "Neutral") {
            _ = blinker.StartBlinkAsync();   // Restart blink on neutral
        } else {
            blinker.StopBlink();             // Suppress blink during expressions
        }

        var elapsed = Time.realtimeSinceStartup - changeStartAt;
        var velocity = elapsed / smoothTime + velocityAtStart;
        if (velocity > 1) { velocity = 1; changeStartAt = 0; }

        foreach (var kv in blendShapeProxy.GetValues()) {
            if (kv.Key.ToString() == currentFaceName) {
                blendShapeProxy.ImmediatelySetValue(kv.Key, velocity * valueToApply);
            } else if (kv.Value > 0) {
                blendShapeProxy.ImmediatelySetValue(kv.Key, kv.Value * (1 - velocity));
            }
        }
    }
}
```

**Two coupled behaviours**: the target expression ramps up to its full value; all *other* currently-active expressions ramp down to zero. Crossfade by per-frame interpolation. The `Update` runs every frame while `changeStartAt > 0`; once velocity hits 1, the field resets to 0 and the loop stops.

**The blink-coupling** (lines 32-39): expressions other than `"Neutral"` *stop blinking*. Resting face = neutral + blink. Expressive face = no blink (the face's blendshapes would conflict). This is a real production decision — most expressions move the eyelids subtly; blink overlay would be janky. Stop blink for the duration of the expression; restart on return to neutral. The interplay between `IBlink` and `IFaceExpressionProxy` is *cross-interface coordination*; CDK does it via `gameObject.GetComponent<IBlink>()` (line 23).

### 2.4 `VRMuLipSyncHelper` — viseme map for the five Japanese vowels

`Extension/VRM/VRMuLipSyncHelper.cs` (27 LOC). The blendshape map (lines 11-25):

```csharp
protected override Dictionary<string, int> GetBlendShapeMap(GameObject avatarObject) {
    var blendShapeMap = new Dictionary<string, int>();
    var proxy = avatarObject.GetComponent<VRMBlendShapeProxy>();
    foreach (var clip in proxy.BlendShapeAvatar.Clips) {
        if (clip.BlendShapeName == "A" || clip.BlendShapeName == "I" || clip.BlendShapeName == "U" || clip.BlendShapeName == "E" || clip.BlendShapeName == "O") {
            blendShapeMap.Add(clip.BlendShapeName, clip.Values[0].Index);
        }
    }
    blendShapeMap.Add("N", -1);
    blendShapeMap.Add("-", -1);
    return blendShapeMap;
}
```

VRM has five mouth blendshapes — A, I, U, E, O. These map directly to uLipSync's vowel detections (which are Japanese-vowel-based). The map is constructed at avatar-setup time by enumerating the VRM's blendshape clips and matching by name.

**The `N` and `-` mapping to `-1`** — nasal and silence visemes map to "no mouth movement." The `-1` is a sentinel telling uLipSync's renderer to zero out all mouth blendshapes for these phonemes.

This is a *27-line implementation* of viseme mapping. The rest of `uLipSync` (third-party) does the heavy lifting; CDK's VRM helper just declares the bindings.

### 2.5 The `VRCFaceExpressionProxy` parallel

`Scripts/Model/VRCFaceExpressionProxy.cs` is the **VRChat avatar standard** version of `IFaceExpressionProxy`. Same interface; different implementation (VRChat models use a different blendshape arrangement). The existence of VRCFaceExpressionProxy is the **proof of the interface-segregation pattern**: CDK already has *two* implementations of `IFaceExpressionProxy` for two different model standards. Substitutability is real, not hypothetical.

The `VRCFaceExpressionProxyEditor.cs` (in `Editor/`) provides a custom Inspector for VRC-specific configuration. Editor extensions per-implementation; same runtime interface.

---

## 3. The Architectural Pattern

### 3.1 Interface segregation at the embodiment boundary

The pattern:

```
ModelController + FaceController + uLipSync
       │              │              │
       ▼              ▼              ▼
    IBlink     IFaceExpressionProxy  ILipSyncHelper
       │              │              │
       ├─VRMBlink     ├─VRMFaceExpProxy  ├─VRMuLipSyncHelper
       │              ├─VRCFaceExpProxy  │
       └─(future)     └─(future)         └─(future)
```

The core (`ModelController`, `FaceController`, `uLipSync` package) depends on **three small interfaces**. Per-model implementations attach as components. The user's prefab has one of each implementation; the substrate's `GetComponent<IFoo>` resolves to the active one.

**Adding Live2D support** is implementing three classes (`Live2DBlink : IBlink`, `Live2DFaceExpressionProxy : IFaceExpressionProxy`, `Live2DLipSyncHelper : ILipSyncHelper`). The core doesn't change. The user's prefab swaps the components.

**The substrate (Unity component model) is what makes this work cheaply.** The factory selection is built into `GetComponent<>`; no DI framework needed. For Ember in Python, the equivalent is a `register` call per implementation and a `runtime.get(IFoo)` lookup.

### 3.2 The runtime-load capability

`VRMLoader.LoadCharacterAsync` lets the user *change the avatar without rebuilding the app*. The avatar URL is config; the app downloads the GLB; the implementation hot-swaps. **This is the key feature that makes CDK feel like a real virtual-companion platform** — users can change their character mid-session. SAP cannot do this (the avatar is baked into the React build). Waifu can but only through cloud-broker negotiation.

The cost: the shader-stripping pitfall (line 32-34 warning). Real but addressable.

### 3.3 The blink × expression coordination

`VRMFaceExpressionProxy` calls `blinker.StartBlinkAsync()` / `StopBlink()` based on the current expression name (line 32-39). This is **interface-to-interface cross-call** — two embodiment helpers coordinating via their interfaces (not via shared state). The pattern is right: the coordinator (FaceProxy) decides; the actor (Blinker) responds. The dependency is unidirectional (FaceProxy depends on IBlink; not vice versa).

---

## 4. Where the Interface Strains

### 4.1 The face-name vocabulary is model-defined

The `IFaceExpressionProxy.SetExpression("Joy", 1.0f)` succeeds or silently fails depending on whether the model has a "Joy" blendshape. The interface does not query "what expressions does this model support?" The user-side prompt-engineer must hand-write the list.

For Ember: every avatar adapter exposes `available_expressions() -> set[str]`. The Tag Capability Declaration ([[25_ANIMATION_TAG_PROTOCOL]] §3.2) sends the list to the LLM. CDK has the gap; Ember closes it.

### 4.2 The blink-during-expression decision is hardcoded

`VRMFaceExpressionProxy.Update` lines 32-39: blink on for "Neutral", off for everything else. **Hardcoded by name.** If the user creates an expression that *should* still blink (a subtle "thoughtful" face), they cannot opt in to blink during it. Ember's expression registry should include `should_blink: bool` per expression.

### 4.3 The viseme map assumes Japanese-vowel-VRM models

`VRMuLipSyncHelper.GetBlendShapeMap` looks for blendshapes named "A", "I", "U", "E", "O" — the Japanese five-vowel convention. English-vowel-mapped models (using "AA", "EE", "OO", etc.) fall through silently with an empty map; lip-sync does not work. CDK does not warn.

For Ember: the viseme map should be **declared**, not auto-detected, with multiple presets (Japanese vowels, English vowels, MMD format, etc.).

### 4.4 The shader-stripping warning is the entire safety net

For runtime-loaded VRM, the *only* protection against the pink-avatar bug is `Debug.LogWarning`. Build verification should run before each WebGL/mobile build to assert "Always Included Shaders" contains the VRM list. CDK does not check; users discover the bug at runtime.

### 4.5 The `OnCharacterReady` callback is fire-and-forget

`OnCharacterReady?.Invoke(characterObject);` is a single-cast event. Multiple subscribers don't compose well; the assignment overwrites. Same as the LLM service callbacks ([[20_LLM_SERVICE_INTERFACE]]). Ember should use a proper multi-cast event.

### 4.6 The crisp parts

- **Three small interfaces** at the embodiment boundary.
- **Two existing implementations of `IFaceExpressionProxy`** prove substitutability.
- **Runtime-load capability** (VRM from URL) — the killer feature.
- **Cross-interface coordination** (Blinker × FaceProxy) via interface methods, not shared state.
- **The viseme map abstraction** — 27 lines that adapts uLipSync to VRM's blendshape names.
- **`Setup(avatarObject)` per implementation** — the avatar pointer flows in; the implementation knows how to wire to it.
- **The shader-stripping warning** — production-tested honesty about a real pitfall.

---

## 5. Cross-References

- [[10_DOMAIN_MAP]] §1 row 2, §7 — Model subsystem and VRM Extension
- [[12_MODEL_CONTROLLER_DOMAIN]] — the consumer of `IBlink`, `IFaceExpressionProxy`, `ILipSyncHelper`
- [[1B_ANIMATION_DOMAIN]] — the tag protocol that drives expressions
- [[25_ANIMATION_TAG_PROTOCOL]] — `[face:Joy]` tag fires `IFaceExpressionProxy.SetExpression("Joy", 1)`
- [[55_WEBGL_GOTCHAS]] — Auditor's catalogue including the shader-strip issue
- [[sap:11_AVATAR_DOMAIN]] — SAP's VRM use (mixed with avatar logic)
- [[waifu:20_ZEROWEIGHT_SURFACE]] — Waifu's cloud-rendered avatar for contrast

---

## What This Means for Ember

**Adopt:**
- The **interface-segregation pattern at the embodiment boundary**. Ember's Andlit defines three Protocols: `BlinkProvider`, `FaceExpressionProvider`, `LipSyncProvider`. Implementations register; the runtime resolves; substitutability is real. Apache-2.0 attribution required.
- The **runtime-load capability** as Ember's `AvatarLoader` Protocol. Loading from URL is a first-class operation, not a build-time decision. Cache to disk; address by content hash; hot-swap at runtime.
- The **viseme-map-as-declared-config** pattern. The 27-line `VRMuLipSyncHelper.GetBlendShapeMap` shows how small the adapter can be. Ember's `LipSyncAdapter` Protocol has the same shape.
- The **cross-interface coordination** pattern (Blinker × FaceProxy). Ember's coordination uses events (`ExpressionChanged(name)` published; `BlinkController` subscribes) rather than direct cross-component calls. Same intent; observability for free.

*Apache-2.0 attribution: when patterns from `ChatdollKit/Extension/VRM/` are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:**
- The **fire-and-forget `OnCharacterReady` callback** to a proper event bus.
- The **blink-on-neutral-only hardcoding** to declared per-expression `should_blink: bool`.
- The **VRM-Japanese-vowels viseme map** to a declared `VisemeMap` with multiple presets selectable per avatar.
- The **shader-stripping warning** to a build-time verification rite that asserts "Always Included Shaders" or its equivalent.

**Avoid:**
- **Avatar standards baked into the core.** Ember's core never imports VRM-specific types; only Protocols. Adding Live2D / MMD / custom rigs is implementing the Protocols.
- **Implicit expression-name vocabularies.** Avatars declare their available expressions; the LLM is told.
- **Hardcoded viseme-blendshape conventions.** The map is config, not inference.

**Invent:**
- **The Avatar Capability Manifest.** Each Ember avatar exposes: `available_expressions: list[str]`, `available_animations: list[str]`, `viseme_set: enum`, `bone_rig: enum`, `blendshape_format: enum`. The runtime queries on load; the orchestrator surfaces capabilities to the LLM (the Tag Capability Declaration).
- **The Avatar Provenance Stamp.** Loaded avatars carry: `source_url`, `content_hash`, `loaded_at`, `license`, `attribution`. Displayed in a session's about-screen; auditable. CDK has the URL in config but no provenance trail; Ember files it.
- **The Avatar Hot-Swap Vow.** Ember can swap the avatar mid-session with state preservation (current expression, animation queue, lip-sync state). The hot-swap emits `AvatarChanged(from, to)` and the queues' state is migrated where mappings exist (Joy → Happy on the new model) or reset gracefully where they don't.
- **The Cross-Standard Expression Mapping.** When the LLM emits `[face:Joy]` and the active avatar's standard maps to "Happy" instead of "Joy", an `ExpressionMap` provides the translation. Per-avatar; declared in `avatar.yaml`. CDK requires the LLM-side prompt to match the avatar's exact names; Ember does the mapping.
- **The Blendshape-Conflict Detector.** When two simultaneously-active expressions share a blendshape (e.g., "Angry" and "Joy" both move the brow), Ember detects and resolves via a priority/weight policy. CDK's `VRMFaceExpressionProxy` ramps all non-current down — works but loses the blendable-emotion case. Ember offers `blendable: bool` per expression.
- **The Build-Time Shader Verification.** Ember's deployment tooling verifies that runtime-loadable avatars' shaders are present. Refusal to deploy if missing; failing-loud beats pink-avatar.
- **The Avatar-As-Realm-Property.** In Ember's tier ladder, the avatar is a *realm property* — the voice realm has an avatar (`Tier-UNITY: VRM model`; `Tier-CLOUD: streaming render`; `Pi-tier: text only, no avatar`). The realm declares its avatar capability; the LLM-side prompt is tailored. CDK assumes Unity 3D rendering; Ember has three rendering paths and explicit fallback.

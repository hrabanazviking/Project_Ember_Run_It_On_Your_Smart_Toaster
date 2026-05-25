---
codex_id: 35_LIP_SYNC
title: Lip Sync — uLipSync, Five Vowels, and the BlendShape Hunt
role: Forge-A
layer: Execution
status: draft
kit_source_refs:
  - Scripts/Model/uLipSyncHelper.cs:1-107
  - Scripts/Model/ConfigurableLipSyncHelper.cs:1-109
  - Scripts/Model/SpeechController.cs:83-127 (HandlePlayingSamples loop)
  - Scripts/Model/ILipSyncHelper.cs (interface)
  - Scripts/Model/AvatarUtility.cs (GetFacialSkinnedMeshRenderer)
ember_subsystem_targets: [Andlit-unity, Rödd-unity]
cross_refs:
  - 33_TTS_PREFETCH
  - 29_VRM_INTERFACE
  - 12_MODEL_CONTROLLER_DOMAIN
  - sap:32_AVATAR_RENDER_PIPELINE
  - waifu:21_LIVEKIT_INTEGRATION
license_posture: Apache-2.0 — adopt with attribution (uLipSync is separate MIT)
---

# Lip Sync

> *Five vowels, one ML-trained vowel detector, two BlendShape maps, and a 33ms wall-clock estimator. The avatar's mouth moves because someone wrote a regex over BlendShape names.*

Forge-A. Eldra. SAP does lip-sync with an FFT-based amplitude analyzer in `vts_manager.py` — crude, robust, fast. ChatdollKit does it through an external library called **uLipSync** that runs an audio-feature-trained vowel classifier on the playing audio samples and outputs five viseme channels (A/I/U/E/O) plus N (closed) and silence (-). The result is meaningfully better mouth animation, and the integration mechanism is a small case study in why Unity-asset-ecosystem integration is both powerful and fragile. Here is how CDK threads the needle.

## What uLipSync Is

uLipSync is a Unity asset (MIT-licensed, separate from ChatdollKit's Apache-2.0) by hecomi. It runs a Burst/Mathematics-accelerated MFCC pipeline over short audio windows and classifies each window against a profile of pre-recorded vowel exemplars. The output is per-frame blend weights for whichever phoneme channels the developer maps to. CDK uses five — A, I, U, E, O — plus N (closed mouth) and `-` (silence).

CDK's integration is two small classes: `uLipSyncHelper` (107 lines, `/tmp/ChatdollKit/Scripts/Model/uLipSyncHelper.cs`) and `ConfigurableLipSyncHelper` (109 lines, `ConfigurableLipSyncHelper.cs`). Both implement `ILipSyncHelper` with the same two methods: `ResetViseme()` and `ConfigureViseme(GameObject avatarObject)`. The configurable variant lets you override BlendShape name fragments (e.g. for VRoid models that name their visemes differently than VRC).

## The BlendShape Hunt

`GetBlendShapeMap` (`uLipSyncHelper.cs:72-105`) is where the lip-sync ties itself to a specific avatar mesh. It walks every BlendShape on the avatar's facial mesh and pattern-matches names:

```csharp
// /tmp/ChatdollKit/Scripts/Model/uLipSyncHelper.cs:72-105 (compressed)
protected virtual Dictionary<string, int> GetBlendShapeMap(GameObject avatarObject)
{
    var mesh = AvatarUtility.GetFacialSkinnedMeshRenderer(avatarObject).sharedMesh;
    var blendShapeMap = new Dictionary<string, int>()
    {
        { "A", 0 }, { "I", 0 }, { "U", 0 }, { "E", 0 }, { "O", 0 }, { "N", -1 }, { "-", -1 }
    };

    for (var i = 0; i < mesh.blendShapeCount; i++)
    {
        if (mesh.GetBlendShapeName(i).Contains("vrc.v_aa")) blendShapeMap["A"] = i;
        else if (mesh.GetBlendShapeName(i).Contains("vrc.v_ih")) blendShapeMap["I"] = i;
        else if (mesh.GetBlendShapeName(i).Contains("vrc.v_ou")) blendShapeMap["U"] = i;
        else if (mesh.GetBlendShapeName(i).Contains("vrc.v_e")) blendShapeMap["E"] = i;
        else if (mesh.GetBlendShapeName(i).Contains("vrc.v_oh")) blendShapeMap["O"] = i;
    }

    return blendShapeMap;
}
```

It hardcodes VRChat's naming convention. `vrc.v_aa` is VRC's name for the "ah" viseme. `vrc.v_ih`, `vrc.v_ou`, `vrc.v_e`, `vrc.v_oh` are the same. If your model uses different names — and many do, VRoid uses `Fcl_MTH_A` for the same shape — the default helper won't find them. The base class returns indices 0/0/0/0/0 (silent default), N=-1, `-`=-1. uLipSync then animates index 0 for every vowel, producing the most confused-looking mouth motion you've ever seen.

The `ConfigurableLipSyncHelper` exists exactly to fix this. It exposes five `[SerializeField] string blendShapeNameForMouthA` ... `blendShapeNameForMouthO` Inspector fields (`:10-14`):

```csharp
// /tmp/ChatdollKit/Scripts/Model/ConfigurableLipSyncHelper.cs:10-14
[SerializeField] private string blendShapeNameForMouthA = "vrc.v_aa";
[SerializeField] private string blendShapeNameForMouthI = "vrc.v_ih";
[SerializeField] private string blendShapeNameForMouthU = "vrc.v_ou";
[SerializeField] private string blendShapeNameForMouthE = "vrc.v_e";
[SerializeField] private string blendShapeNameForMouthO = "vrc.v_oh";
```

Override these in the Inspector to match your model's BlendShape vocabulary. The pattern-match logic is the same `Contains()` substring check (`:80-104`). So `Fcl_MTH_A` matches `Contains("Fcl_MTH_A")` if you set the override.

This is one of those design choices that looks pragmatic and is correct: hardcode the common case, expose Inspector overrides for the long tail. The alternative — a JSON config file with viseme mappings — would be more "correct" but Unity's Inspector is the right UI here.

## The ConfigureViseme Wiring

`ConfigureViseme` (`uLipSyncHelper.cs:30-70`, mirror in ConfigurableLipSyncHelper.cs:19-65) does the setup:

```csharp
// /tmp/ChatdollKit/Scripts/Model/uLipSyncHelper.cs:30-70 (compressed)
public virtual void ConfigureViseme(GameObject avatarObject)
{
    var blendShapeMap = GetBlendShapeMap(avatarObject);

    var uLipSyncBlendShape = gameObject.GetComponent<uLipSyncBlendShape>();
    if (uLipSyncBlendShape == null)
        uLipSyncBlendShape = gameObject.AddComponent<uLipSyncBlendShape>();

    uLipSyncBlendShape.skinnedMeshRenderer = AvatarUtility.GetFacialSkinnedMeshRenderer(avatarObject);
    uLipSyncBlendShape.blendShapes.Clear();
    foreach (var map in blendShapeMap)
    {
        uLipSyncBlendShape.blendShapes.Add(new uLipSyncBlendShape.BlendShapeInfo()
            { phoneme = map.Key, index = map.Value, maxWeight = 1 });
    }

#if UNITY_EDITOR
    var uLipSyncMain = gameObject.GetComponent<uLipSync.uLipSync>() ?? gameObject.AddComponent<uLipSync.uLipSync>();
    UnityEditor.Events.UnityEventTools.AddPersistentListener(uLipSyncMain.onLipSyncUpdate, uLipSyncBlendShape.OnLipSyncUpdate);

    var profiles = UnityEditor.AssetDatabase.FindAssets("-Profile-Female");
    if (profiles.Length > 0)
        uLipSyncMain.profile = UnityEditor.AssetDatabase.LoadAssetAtPath<Profile>(UnityEditor.AssetDatabase.GUIDToAssetPath(profiles.First()));
#endif
}
```

Two key components are wired here:
- `uLipSyncBlendShape` — receives viseme weights from the analyzer and applies them to BlendShape weights on the SkinnedMeshRenderer.
- `uLipSync.uLipSync` — the analyzer itself, which consumes audio samples and emits the viseme weights.

The `UnityEditor.Events.UnityEventTools.AddPersistentListener` (`:61`) wires the two together *at edit time*. That's because Unity events serialize their listener list as a persistent inspector field — wiring it at runtime via the regular `+=` listener pattern works but doesn't survive a re-save. CDK punts on the runtime case: the `#if UNITY_EDITOR` block does the wiring once in the editor; at runtime the wiring must already be present in the saved prefab.

This is a pre-runtime configuration step. If you instantiate an avatar at runtime (e.g., a fresh VRM downloaded from a URL), you have to call `ConfigureViseme` on it, and if the listener wiring isn't already on the prefab, the lip-sync will silently not work. CDK's typical use case is a prefab-baked avatar; dynamic VRM loading needs more care.

The profile lookup (`:64-68`) searches for any asset matching `-Profile-Female` and assigns it. The profile is what defines the vowel exemplars uLipSync compares against. Female default is a choice — male profile would need a different asset.

## The Audio Feed

uLipSync needs audio samples to analyze. The wiring from `SpeechController.Say` (`SpeechController.cs:83-126`) was covered in [[33_TTS_PREFETCH]], but here's the relevant excerpt:

```csharp
// /tmp/ChatdollKit/Scripts/Model/SpeechController.cs:83-115 (compressed)
if (HandlePlayingSamples != null)
{
    var bufferSize = clip.channels == 2 ? 2048 : 1024;
    var sampleBuffer = new float[bufferSize];
    var nextPosition = 0;
    var samples = new float[clip.samples * clip.channels];

    if (!clip.GetData(samples, 0))
        Debug.LogWarning("Failed to get audio data from clip");
    else
    {
        AudioSource.PlayOneShot(clip);

        while (Time.realtimeSinceStartup - startTime < clip.length && !token.IsCancellationRequested)
        {
            var elapsedTime = Time.realtimeSinceStartup - startTime;
            var currentPosition = Mathf.FloorToInt(elapsedTime * clip.frequency) * clip.channels;

            while (nextPosition + bufferSize <= currentPosition && nextPosition + bufferSize <= samples.Length)
            {
                System.Array.Copy(samples, nextPosition, sampleBuffer, 0, bufferSize);
                HandlePlayingSamples(sampleBuffer);
                nextPosition += bufferSize;
            }

            await UniTask.Delay(33, cancellationToken: token);
        }
    }
}
```

`HandlePlayingSamples` is the callback that uLipSync (or any lip-sync helper) registers. It receives 1024-or-2048-sample windows roughly every 33ms (30Hz). uLipSync's `OnDataReceived` (called via this callback) runs its MFCC analysis on that window and emits viseme weights via its UnityEvent.

The key choice: **CDK estimates playback position from wall-clock time** (`Time.realtimeSinceStartup - startTime` × `clip.frequency`) rather than asking `AudioSource.timeSamples`. The wall-clock is fast and synchronous; `timeSamples` is correct but threading-fragile. The cost is that any audio-output delay (Bluetooth, USB-DAC) causes a lip-sync vs audio drift equal to that delay.

## The WebGL Reset

`uLipSyncHelper.ResetViseme` (`:13-28`) is a WebGL-only quirk:

```csharp
// /tmp/ChatdollKit/Scripts/Model/uLipSyncHelper.cs:13-28
public void ResetViseme()
{
# if UNITY_WEBGL && !UNITY_EDITOR
    if (uLipSyncRef == null)
        uLipSyncRef = gameObject.GetComponent<uLipSync.uLipSync>();
    if (uLipSyncRef == null) return;

    if (silentSamples == null)
        silentSamples = new float[4096];
    uLipSyncRef.OnDataReceived(silentSamples, 1);
# endif
}
```

On WebGL, the uLipSync component's internal state doesn't auto-reset when audio playback stops. The mouth would stay in whatever vowel position the last sample produced. CDK hand-feeds 4096 zero samples ("silent samples") to force the analyzer's internal state back to neutral. This is exactly the kind of "I shipped to WebGL and the mouth wouldn't close" bug-fix you find by shipping.

On non-WebGL builds, the function is empty. The Unity Editor's uLipSync state machine handles reset properly there.

## Where It Breaks

- **Substring match in BlendShape hunt.** `Contains("vrc.v_aa")` will match `"vrc.v_aaaaaa"` and `"Mvrc.v_aax"`. For real models this is fine because the naming is conventional, but a hostile or malformed BlendShape name (e.g. some auto-generated VRoid exports) can match the wrong shape and produce uncanny mouth animation.
- **`profiles.First()` (`uLipSyncHelper.cs:67`).** Picks the first matching profile asset alphabetically (the default `FindAssets` order). If two `-Profile-Female` assets exist in the project, you get whichever happens to come first. No determinism, no warning.
- **Wall-clock drift.** As noted in [[33_TTS_PREFETCH]], Bluetooth output has 100-300ms latency. The visemes lead the audio by that amount. The mouth opens, then 200ms later the sound comes out. Visible on every Bluetooth setup.
- **The 33ms delay-per-iteration in `SpeechController.cs:115`.** Tight loop at 30Hz, which is below the 60Hz refresh rate of modern displays. The visemes update at 30Hz which is the lower bound for "feels smooth." Tightening to 16ms (60Hz) would double the per-window analysis cost — probably fine on PC, measurable on mobile.
- **`AvatarUtility.GetFacialSkinnedMeshRenderer` finds the *first* SkinnedMeshRenderer that has any of the named BlendShapes.** If an avatar has a body mesh and a face mesh both with BlendShapes (some VRoid exports), it may pick the body. Result: invisible lip-sync because the face mesh isn't being animated.
- **No graceful degradation if `uLipSync` package is missing.** The `using uLipSync;` at the top of the file (`:4`) is a hard dependency. If you import CDK without the uLipSync package, the project won't compile. The interface `ILipSyncHelper` allows for swap-out, but the package is implicitly required.

## Where It Surprises

- **uLipSync runs MFCC analysis in Burst.** This makes it fast enough to run at 60-120Hz on mid-range CPUs with no measurable game-thread cost. The analysis itself isn't the bottleneck; the 33ms playback-loop iteration is.
- **N (closed mouth) and `-` (silence) are first-class visemes.** They map to BlendShape index `-1` by default — meaning "don't touch any BlendShape, just set them all to zero." When uLipSync emits an N or `-` viseme weight, all other BlendShapes are interpolated to zero. This is what makes the mouth close naturally between words.
- **The profile is `-Profile-Female` by default with no explicit warning.** If your avatar is male, the lip-sync still works but the vowel-classification accuracy degrades. The profile encodes the spectral characteristics of the trained vowel samples, and female voices skew higher. The fix is to ship a `-Profile-Male` and override; CDK doesn't ship one but uLipSync's package includes both.
- **uLipSync's `onLipSyncUpdate` is a UnityEvent**, which means listeners are *Inspector-serialized*. This is what forces the `#if UNITY_EDITOR` wiring block at `:52-69`. Pure-runtime wiring (`uLipSyncMain.onLipSyncUpdate.AddListener(...)`) would work but wouldn't persist. CDK chose the persistent path.
- **There is no "intensity" control on the visemes from the LLM/text side.** The lip-sync amplitude is entirely driven by the audio signal, not by the LLM emitting `[face:Mouth_wide]`. This is correct (the mouth should move with the voice) but means scripted no-audio mouth motion isn't possible. SAP's tag-driven approach can do this; CDK cannot.

## Cross-References

- [[33_TTS_PREFETCH]] — where `HandlePlayingSamples` is fed from
- [[29_VRM_INTERFACE]] — VRM BlendShape conventions
- [[12_MODEL_CONTROLLER_DOMAIN]] — ModelController's role in coordinating
- [[sap:32_AVATAR_RENDER_PIPELINE]] — contrast: SAP uses FFT-based amplitude analysis in `vts_manager.py`, no vowel detection
- [[waifu:21_LIVEKIT_INTEGRATION]] — contrast: Waifu's lip-sync is cloud-rendered (invisible)

## What This Means for Ember

**Adopt:**

- **The five-vowel + N + silence channel structure** (`uLipSyncHelper.cs:77`, Apache-2.0 attribution required). A/I/U/E/O is the right minimal set for both English and Japanese. The N and `-` channels are the discipline that makes mouths actually *close*. Adopt as Andlit-unity's standard viseme contract.
- **The Inspector-overridable BlendShape name pattern** (`ConfigurableLipSyncHelper.cs:10-14`). Configurable substrings per viseme. This is the right pragmatic surface — don't require a config file for the common VRC/VRoid cases, expose overrides for everything else.
- **The wall-clock playback-position estimator with 33ms tick** (`SpeechController.cs:97-115`). Adopt for Andlit-unity baseline; note the Bluetooth drift in known-limitations docs.

**Adapt:**

- **The wall-clock estimator → AudioSource sample position.** Adopt the structure, but use `AudioSource.timeSamples` for accuracy. The thread-safety risk is manageable with a single read per frame. The Bluetooth drift fix is worth it.
- **The MFCC vowel classifier.** uLipSync is MIT-licensed; vendor it (with attribution) into Ember's Andlit-unity tier. For Andlit-electron and Andlit-cloud tiers, use simpler FFT-amplitude (SAP's approach) or cloud-driven (Waifu's). Three-tier consistency.
- **The profile asset.** Ship both Male and Female profiles; auto-select by avatar metadata (VRM has a gender hint in its meta block); fall back to Female if unspecified.

**Avoid:**

- **The `Contains()` substring match for BlendShape names.** Use exact-match or regex with `^name$` anchors. Substring is a footgun.
- **The `FindAssets` non-determinism.** If multiple profile assets exist, fail loudly or use an explicit Inspector reference.
- **Hard dependency on uLipSync.** Make `ILipSyncHelper` actually mean what it claims — an interface with multiple implementations. Ship a stub `NoopLipSyncHelper` for builds where uLipSync isn't available.
- **The 30Hz update rate.** Move to 60Hz when CPU allows. Visemes are the most visually-noticeable mouth motion; smoother is better.

**Invent:**

- **Andlit-unity Cross-Tier Viseme Adapter.** Same `[face:X]` and viseme contract across electron / unity / cloud tiers. Per-tier viseme renderer: FFT-amplitude (electron baseline), uLipSync (unity premium), cloud-driven (waifu tier). Ember code is tier-agnostic; viseme quality scales with tier.
- **Rödd-unity Pre-Computed Viseme Track.** When TTS audio is generated, also pre-compute viseme track at synthesis time (uLipSync analysis on the full audio before playback). Eliminates wall-clock drift entirely — visemes are time-stamped and played in lockstep with audio. Costs 100ms per second of audio to pre-compute; cache alongside the AudioClip.
- **Hjarta Mouth Idle.** Subtle resting-mouth animation when not speaking (slight A/I micromovements, ~5% weight). CDK's mouth goes completely still between utterances which reads as "frozen." Hjarta provides a low-amplitude vowel weight stream based on persona state.

---

*Apache-2.0 attribution: when adopting CDK's lip-sync wiring code into Ember source, preserve the ChatdollKit header reference per Apache-2.0 §4(c). uLipSync itself is MIT — separate attribution required when vendoring its analyzer.*

---
codex_id: 1C_UNITY_LIFECYCLE_DOMAIN
title: Unity Lifecycle Domain — One MonoBehaviour, Five Callbacks, One Asmdef, Five JSLibs
role: Architect
layer: Domain
status: draft
chatdoll_source_refs:
  - Scripts/ChatdollKit.asmdef
  - Scripts/AIAvatar.cs:1-664
  - Scripts/Model/ModelController.cs:58-100
  - Scripts/Network/SocketServer.cs:42-53
  - Scripts/LLM/LLMServiceBase.cs:13-30
  - Plugins/WebGLMicrophone.jslib
  - Plugins/JavaScriptMessageHandler.jslib
  - Plugins/iOS/
  - Plugins/Android/
  - Editor/ModelControllerEditor.cs
  - Prefabs/AIAvatar.prefab
ember_subsystem_targets: []
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/1D_MULTI_PLATFORM_DOMAIN
  - 00_vision/02_UNITY_AS_RUNTIME
  - 50_verification/55_WEBGL_GOTCHAS
  - sap:1B_ELECTRON_LIFECYCLE
  - waifu:1C_BROWSER_LIFECYCLE
---

# Unity Lifecycle Domain
## One MonoBehaviour, Five Callbacks, One Asmdef, Five JSLibs

*— Rúnhild Svartdóttir, Architect*

> *Every codex must, at some point, name the substrate. SAP names Electron; Waifu names the browser; ChatdollKit names Unity. The substrate is not just where the code runs — it is the set of opinions the substrate has about lifetime, threading, dependency, and serialisation, opinions the code cannot revise without leaving. Naming the substrate is the act of choosing which opinions to live under.*

This doc is *not* about CDK's eight subsystems. Those have their own domain docs. This doc is about the **runtime substrate underneath every other doc** — the Unity engine, its MonoBehaviour lifecycle, its component-based dependency model, its asmdef-bound compilation units, its Editor-driven asset pipeline, and its build-target-conditional native plugins. Every other CDK domain *assumes* this substrate. Ember's adoption of CDK patterns requires *first* deciding which substrate-isms to keep and which to replace.

The argument of this doc is that CDK's architectural cleanliness is **substantially a gift of Unity**. Five of CDK's most-loved patterns — the component-as-DI-container, the per-frame `Update` polling, the `GetComponent<IFoo>()` interface lookup, the prefab-as-deployment-unit, the `[SerializeField]` editor-bound config — are *substrate-provided*. To adopt CDK in Python is to *re-build* those substrate gifts in Python's vocabulary. Some translate cleanly; some require new mechanisms. Below, I name each.

Compare SAP's Electron substrate ([[sap:1B_ELECTRON_LIFECYCLE]]) — IPC, renderer/main process, packaging via electron-forge. Compare Waifu's browser substrate ([[waifu:1C_BROWSER_LIFECYCLE]]) — WebRTC, AudioWorklet, no on-disk state. Unity is the third option: a **proprietary game-engine runtime** that brings hardware-accelerated rendering, mature animation, multi-platform cross-compilation, and a binding-from-Python-uncomfortable C# core.

---

## 1. The Subject Itself

**What the domain is:** the Unity engine as the implicit runtime of every CDK component. The engine provides:

- A **MonoBehaviour lifecycle** with five callback methods Unity invokes per-component per-state-transition.
- A **per-frame `Update` model** with implicit single-threading on the main thread.
- A **component-on-GameObject DI pattern** via `GetComponent<T>()` / `GetComponents<T>()`.
- A **prefab system** for serialising configured GameObjects to disk and instantiating at runtime.
- A **`[SerializeField]` attribute** that exposes private fields in the Inspector for editor-time configuration.
- A **multi-build-target compiler** that produces native code for Win/Mac/Linux/iOS/Android/WebGL/VR/AR from the same C# source.
- A **`*.asmdef` system** for explicit assembly definition with namespace boundaries.
- A **native plugin mechanism** for platform-specific code (`*.jslib` for WebGL, `*.aar`/`*.so` for Android, `*.framework` for iOS, `*.bundle` for Mac).
- A **`[DllImport("__Internal")]`** mechanism for calling into platform-native code from C#.

CDK *consumes* every one of these. None of CDK's 18,000 lines is dedicated to *implementing* lifecycle, dependency injection, scheduling, or serialisation; those come from the substrate. What CDK *owns* is the configuration of these substrate facilities for the avatar-companion case.

**What this domain documents:** the substrate-side patterns CDK uses, with citations into both CDK source and (where needed) Unity's official documentation.

**What it does NOT own:**
- The Unity engine itself — proprietary, EULA-bound, separately licensed.
- The C# language and the .NET runtime — Microsoft and Mono respectively.
- The third-party Unity packages (UniTask, UniVRM, Newtonsoft.JSON) — separately maintained.

---

## 2. How It Works

### 2.1 The MonoBehaviour lifecycle

Every CDK class that lives in a Unity scene inherits from `MonoBehaviour`. The Unity runtime invokes five callbacks at well-defined moments:

| Callback | When | CDK usage |
|---|---|---|
| `Awake()` | Once, on instantiation, before any `Start()` runs anywhere | `AIAvatar.Awake` (lines 100-280) — resolves all subsystem components via `GetComponent<>`, registers their event handlers. The *wiring phase*. |
| `Start()` | Once, after all `Awake()`s have run, before first `Update` | `MicrophoneManager.Start` (`Scripts/SpeechListener/MicrophoneManager.cs:64-79`) — starts the mic device. The *operate phase*. |
| `Update()` | Every frame (typically 60 Hz, 30 Hz on mobile) | `MicrophoneManager.Update` (lines 81-103), `SocketServer.Update` (lines 42-53), `ModelController.Update` (line 97), every subsystem's poll loop. The *runtime phase*. |
| `LateUpdate()` | Every frame, after all `Update()`s | Not used by CDK directly; relevant for animation-blending fixups. |
| `OnDestroy()` | When the GameObject or component is destroyed | `SocketServer.OnApplicationQuit` (line 197-200), `SileroVADProcessor.OnDestroy` (line 197-200) — cleanup. The *teardown phase*. |

**The Awake-vs-Start distinction matters.** Awake is for *intra-component setup* — resolving references that must be available before any `Start` runs. Start is for *cross-component initialisation* — starting devices, registering handlers that other components may have just resolved. CDK respects the split: `AIAvatar.Awake` resolves `MicrophoneManager`, `ModelController`, etc.; `AIAvatar.Start` doesn't do much because the resolution already happened in Awake. Microphone device starts in `MicrophoneManager.Start` because by then all other Awakes have run and listeners have registered for `OnSamplesReceived`.

For Ember: the lifecycle pattern translates as **two-phase init**: a `wire()` method that resolves dependencies (analogous to Awake), and an `operate()` method that starts devices/loops (analogous to Start). The asyncio runtime can sequence these explicitly: `await asyncio.gather(*[c.wire() for c in components]); await asyncio.gather(*[c.operate() for c in components])`.

### 2.2 The per-frame `Update` model

`Update()` is invoked **once per rendered frame, on the main thread**. Single-thread guarantee. No locks needed for state read/write within a component's own update. CDK uses this gift everywhere.

```csharp
// Scripts/Network/SocketServer.cs:42-53
private void Update() {
    lock (queueLock) {
        while (messageQueue.Count > 0) {
            var message = messageQueue.Dequeue();
            OnDataReceived?.Invoke(message);  // Always on main thread
        }
    }
}
```

The `queueLock` is needed because *other* threads (the SocketServer's accept-threads, the WebGL JS callbacks) enqueue from off-main-thread. The lock is *only* for cross-thread boundary; dispatch to `OnDataReceived` (and all downstream handlers, including `DialogProcessor.StartDialogAsync`, the LLM call, etc.) is main-thread-only and lock-free.

**The mental model**: there is *one* execution thread that walks all components' `Update`s in undefined order each frame. State mutations happen during your own `Update`. Reading another component's state during your `Update` is safe (no race). Calling another component's method during your `Update` is safe and executes synchronously.

**The cost**: the main thread is one core. If any `Update` is slow, every other `Update` waits. CDK uses UniTask to push slow work (HTTP calls, audio synthesis) onto the *task* scheduler (single-threaded but co-operative — `await`s yield); the main thread spends ~16ms per frame and yields the rest. This is **co-operative scheduling on a single thread** — the same model as asyncio. Translation to Ember is natural.

### 2.3 The component-as-DI pattern

`GameObject` is Unity's primitive — a named container with a Transform and zero-to-many attached `Component`s. Each Component is a class inheriting from `MonoBehaviour`. The runtime provides:

```csharp
// Available on every MonoBehaviour
T GetComponent<T>();         // First component of type T on this GameObject
T[] GetComponents<T>();      // All components of type T on this GameObject
```

CDK uses this as **dependency injection**:

```csharp
// Scripts/AIAvatar.cs:116-119
MicrophoneManager = MicrophoneManager ?? gameObject.GetComponent<IMicrophoneManager>();
ModelController = ModelController ?? gameObject.GetComponent<ModelController>();
DialogProcessor = DialogProcessor ?? gameObject.GetComponent<DialogProcessor>();
LLMContentProcessor = LLMContentProcessor ?? gameObject.GetComponent<LLMContentProcessor>();
```

The pattern: declare references as public fields (Inspector-settable for override); fall back to `GetComponent<>` resolution. Concrete subsystems are *attached as components* on the same GameObject. The substrate provides the registration mechanism for free.

**This is the substrate's biggest architectural gift to CDK.** Five subsystems attached to one GameObject; AIAvatar finds each one by interface; runtime polymorphism is provided by C#'s vtable. No DI framework. No service locator. Just `GetComponent<IFoo>()`.

For Ember: there is no `GameObject`. The equivalent is a `Runtime` object (Ember's `runtime` singleton) with a `register(impl: type, instance: object)` method and a `get(impl: type) -> object` lookup. Two methods. Same shape as Unity's component model. Idiomatic Python.

### 2.4 The prefab as deployment unit

`Prefabs/AIAvatar.prefab` is a *serialised GameObject* — Unity's binary-with-YAML-text-references format that captures: GameObject hierarchy, attached components with their `[SerializeField]` values, references to assets (AudioClips, Animator controllers, AnimationClips, AvatarMasks, etc.). Loading a prefab at runtime via `Instantiate(prefab)` creates a fresh GameObject hierarchy in memory with the same components and values.

A **CDK deployment** is a Unity scene that instantiates `AIAvatar.prefab` plus per-scene customisations (LLM API keys via `[SerializeField]` Inspector edits, registered animations in `ModelController`, registered face expressions). The prefab is the *unit* of deployment — versionable, shareable, mergeable (somewhat — the Unity scene/prefab merge tool is notorious).

The cost: prefabs are *binary* in essence. Their YAML representation has GUID-based references that are not human-mergeable. Multi-author teams need a custom merge tool. For Ember's all-Python world, this cost is gone — config is YAML; component wiring is Python imports + a startup `register` block. But the *concept* of a deployment unit is still useful: Ember should have a `realm.yaml` that declares which subsystem implementations are loaded for a deployment.

### 2.5 `[SerializeField]` and the Inspector-as-config-UI

```csharp
// Scripts/SpeechListener/MicrophoneManager.cs:40-46
public int SampleRate = 44100;
public float NoiseGateThresholdDb = -50.0f;
public bool AutoStart = true;
public bool IsDebug = false;
[SerializeField]
private bool useMallocInWebGL = true;
```

Two patterns: **public** fields are Inspector-visible and runtime-mutable from code. **`[SerializeField] private`** fields are Inspector-visible but only settable from the Inspector + the field's owning class. The Inspector is Unity's editor-time GUI for editing the values. They become *serialised state on the prefab*.

**The Inspector-as-config-UI is the substrate's other big gift.** Setting `SampleRate = 16000` on a CDK avatar is *not* an environment variable or a CLI flag — it is an Inspector value baked into the prefab. The configuration is *visible* in the editor; the deployment-time state is *inspectable* without reading code.

For Ember: the equivalent is YAML config with field-typed validation. `mic_sample_rate: 16000` in `realm.yaml` with a `MicConfig: BaseModel` Pydantic class. The discoverability is *worse* than Unity's Inspector (you have to read docs to know the field exists) but the auditability is *better* (text-mergeable, git-diffable). Two trade-offs.

### 2.6 The `.asmdef` boundary

`Scripts/ChatdollKit.asmdef` declares the namespace boundary:

```json
{
    "name": "ChatdollKit",
    "rootNamespace": "",
    "references": [
        "GUID:f51ebe6a0ceec4240a699833d6309b23",  // Newtonsoft.Json
        "GUID:d444a9c79d21fec4181e6e12dc2e9706",  // UniTask
        "GUID:04376767bc1f3b428aefa3d20743e819"
    ],
    ...
}
```

Three named third-party dependencies (Newtonsoft.JSON, UniTask, and one more — likely Microsoft.ML.OnnxRuntime). The asmdef says: *this assembly compiles independently of other assemblies, only depends on these three*. Faster compile times (only re-compile changed assemblies); explicit dependency boundaries; namespace isolation.

**For Ember**: Python packages with explicit `pyproject.toml` dependencies serve the same purpose. Each Ember subsystem package (`ember/funi/`, `ember/strengr/`, etc.) has its own `pyproject.toml` declaring inter-package + external deps. Same discipline, different mechanism.

### 2.7 Native plugins per platform

CDK's `Plugins/` directory:

```
Plugins/
├── AIAvatarKitServiceWebGL.jslib      # WebGL bridge for AIAvatarKit LLM
├── ChatGPTServiceWebGL.jslib          # WebGL bridge for ChatGPT LLM
├── ClaudeServiceWebGL.jslib           # WebGL bridge for Claude LLM
├── DifyServiceWebGL.jslib             # WebGL bridge for Dify LLM
├── GeminiServiceWebGL.jslib           # WebGL bridge for Gemini LLM
├── JavaScriptMessageHandler.jslib     # WebGL bridge for inbound JS messages
├── SimpleCameraWebGL.jslib            # WebGL bridge for browser camera
├── WebGLMicrophone.jslib              # WebGL bridge for browser microphone
├── Android/                           # JNI plugins (.so binaries)
├── iOS/                               # Objective-C frameworks
├── macOS/                             # AVFoundation bundles
└── CopyThisJSToStreamingAssets/       # JS files served as runtime assets
```

**Eight `.jslib` files**. Each is a `mergeInto(LibraryManager.library, { funcName: function() { ... } })` block that adds JS-side functions callable from C# via `[DllImport("__Internal")]`. The pattern:

```javascript
// Approximation of WebGLMicrophone.jslib
mergeInto(LibraryManager.library, {
    InitWebGLMicrophone: function(targetObjectName, useMalloc) {
        // ... AudioWorklet setup, navigator.mediaDevices.getUserMedia, etc.
        // ... callback to C# via SendMessage
    },
    StartWebGLMicrophone: function() { ... },
    // ...
});
```

C# declares the imports:

```csharp
// MicrophoneManager.cs:27-36
[DllImport("__Internal")]
private static extern void InitWebGLMicrophone(string targetObjectName, bool useMalloc);
[DllImport("__Internal")]
private static extern void StartWebGLMicrophone();
```

C# calls the function; Emscripten links to the JS at WebGL build time; the JS function runs in the browser. C-to-JS bridge through Emscripten's wasm-js boundary.

**For native plugins** (Android `.so`, iOS `.framework`, Mac `.bundle`), the pattern is the same — `[DllImport("plugin_name")]` declarations in C#; binary plugin shipped per-platform in `Plugins/<Platform>/`. CDK's `AndroidNativeMicrophone.cs:14-30` shows the imports for the Android side.

The plugin maintenance cost is real: Android 14 changes the audio API; CDK needs a new `.so` build; the entire mobile pipeline depends on Unity's native-plugin lifecycle. Ember's Pi-tier baseline avoids this cost entirely (Python + ctypes is simpler); Ember's hypothetical mobile tier would inherit it.

### 2.8 The Editor scripts

`Editor/ModelControllerEditor.cs` (and `VRCFaceExpressionProxyEditor.cs`) are *editor-only* C# files — code that runs in the Unity Editor's UI, not in the built game. They customise the Inspector display for specific components.

```
Editor/
├── ModelControllerEditor.cs      # Custom Inspector for ModelController
└── VRCFaceExpressionProxyEditor.cs   # Custom Inspector for VRCFaceExpressionProxy
```

`ModelControllerEditor.cs` likely adds buttons like "Register Idle Animation from Selected Clip" or visualisations of the animation queue. Editor extensions are powerful — Unity supports building entire workflows on top of the editor — but they are *not* part of the runtime. They ship to developers, not to end users.

For Ember: there are no Editor scripts. The development environment is text editors + CLI tools. Loss: the discoverability of clicking a button in the Inspector. Gain: no proprietary editor surface to maintain. Ember's discoverability comes from documentation (`SUBSYSTEM.md` per package), CLI help text, and explicit YAML schemas.

---

## 3. Where It Breaks and Where It Surprises

### 3.1 The main thread is one core

Every `Update`, every `OnDataReceived` callback, every `await` continuation lands on the main thread. A slow component (HTTP timeout, large JSON parse, blocking ONNX inference) blocks the *entire* avatar — animation stutters, microphone polling delays, queued messages pile up. CDK pushes slow work to UniTask continuations (off-frame, on-thread-pool *for the IO portion*, back-to-main-thread for completion). The discipline is: never block the main thread; always `await`. CDK does this consistently.

### 3.2 The Awake-Start-Update order is fragile

If component A's `Awake` depends on component B's `Awake` having completed *and registered some event handler*, the order matters. Unity does not guarantee `Awake` order across components on the same GameObject (deterministic in practice but not in spec). CDK avoids this by using *only* `GetComponent<>` references in `Awake` (which work in any order) and deferring callback wiring to a single Awake that runs early (AIAvatar's). One coordinating Awake; one shape of dependency. Discipline.

### 3.3 The Inspector-as-config means deployment is editor-time

To change `MicrophoneManager.SampleRate` on a deployed build, you cannot — the value is baked into the prefab serialisation. To change it dynamically, the application must expose runtime UI or accept commands. CDK has `MicrophoneController.prefab` for runtime mic-toggle UI but not for sample-rate change. For Ember, every config value should be YAML-editable at runtime (with appropriate reload semantics) — *no* "to change the sample rate, recompile the build" experience.

### 3.4 The `.asmdef` recompile is per-edit

Editing any file in `Scripts/` triggers a full re-compile of `ChatdollKit.asmdef`. On a fast machine, 5 seconds. On a slow machine, 30. The asmdef boundary is *too coarse* — five subsystems should be five asmdefs for incremental compilation. CDK doesn't split. Ember's Python has no compilation; the cost vanishes.

### 3.5 The Editor extensions ship as source

`Editor/*.cs` is shipped in CDK's distribution but only executes in the Unity Editor. For users on a build pipeline (CI/CD), the Editor code is dead weight. Excluded from runtime builds via the `Editor/` folder convention. Per-build conditional code via filesystem layout — a substrate gift, not a CDK invention.

### 3.6 The native-plugin per-platform maintenance is the largest hidden cost

The eight `.jslib` files + Android `.so` + iOS `.framework` + Mac `.bundle` represent **months of platform-specific work** spread across years of CDK development. The README does not foreground this. For users who try to add a new TTS provider with a WebGL variant, the JS-bridge work alone is half a day. For users who try to add a new platform — say, Linux ARM64 — there is *no shipped path*; CDK is implicitly x86_64.

### 3.7 The crisp parts

- **MonoBehaviour lifecycle as two-phase init.** Awake = wire; Start = operate. The discipline.
- **Per-frame Update on main thread.** Single-thread guarantee; co-operative scheduling via UniTask.
- **GetComponent<IFoo>() as substrate-provided DI.** Five lines in AIAvatar resolve five subsystems.
- **Prefab as serialised deployment unit.** Inspector-edited, version-controlled, instantiatable.
- **`[SerializeField]` Inspector binding.** Config-as-data, baked into the prefab.
- **`.asmdef` namespace boundaries.** Explicit assembly, explicit dependencies.
- **`.jslib` + `[DllImport("__Internal")]` for WebGL** — JS-side functions callable from C#.
- **Per-platform native plugin folders** (`Plugins/Android/`, `Plugins/iOS/`) — substrate convention.

---

## 4. Cross-References

- [[10_DOMAIN_MAP]] §2 — Unity runtime as bottom layer
- [[00_vision/02_UNITY_AS_RUNTIME]] — Skald's argument for/against Unity as Ember's third tier
- [[1D_MULTI_PLATFORM_DOMAIN]] — the eight build targets that this lifecycle enables
- [[55_WEBGL_GOTCHAS]] — Auditor's catalogue of WebGL-specific lifecycle issues
- [[17_MICROPHONE_MANAGER_DOMAIN]] §2.4 — the WebGL audio-worklet bridge pattern in detail
- [[18_NETWORK_DOMAIN]] §2.4 — the JavaScriptMessageHandler bridge in detail
- [[sap:1B_ELECTRON_LIFECYCLE]] — SAP's Electron lifecycle for contrast
- [[waifu:1C_BROWSER_LIFECYCLE]] — Waifu's browser lifecycle for contrast

---

## What This Means for Ember

**Adopt:**
- The **two-phase init discipline** (Awake = wire, Start = operate). Ember's subsystem Protocol declares `async wire(self) -> None` (resolves dependencies, registers handlers) and `async operate(self) -> None` (starts devices, begins loops). The `EmberRuntime.bootstrap()` calls `gather(*[c.wire() for c in components])` then `gather(*[c.operate() for c in components])`. Apache-2.0 attribution required.
- The **single-thread + co-operative scheduling** pattern. Ember runs on asyncio's single event loop; slow work is `await`ed; never block the loop. The pattern is idiomatic Python; the discipline is the lesson from Unity.
- The **runtime-as-component-container** pattern. Ember's `EmberRuntime.register(interface, instance)` and `runtime.get(interface) -> instance` mirror `GetComponent<IFoo>()`. Interface-keyed lookup; runtime polymorphism via Python's duck-typing and Protocols.
- The **`.asmdef`-style package separation**. Ember's `ember/<subsystem>/` packages have their own `pyproject.toml` with explicit dependencies. `ember.funi` cannot import from `ember.smidja` unless declared. Inter-subsystem boundaries are visible.
- The **deployment-unit YAML** equivalent to prefabs. `realm.yaml` declares which subsystem implementations the deployment uses, with their per-realm config. Apache-2.0 attribution required.

*Apache-2.0 attribution: when patterns from `ChatdollKit/Scripts/ChatdollKit.asmdef` and lifecycle wiring are adopted into Ember source, preserve CDK header reference per Apache-2.0 §4(c).*

**Adapt:**
- The **`[SerializeField]` Inspector model** to Pydantic-validated YAML. Every field has a type, a default, optional validators. The Inspector's discoverability becomes a CLI command (`ember config --schema funi`) that dumps the schema.
- The **prefab as deployment unit** to Ember's `realm.yaml` + `realm.lock.json` (pinned versions of subsystem implementations).
- The **`.jslib` + `[DllImport]` WebGL bridge** to Python `ctypes` / `cffi` for native bindings on the Pi tier (audio device, GPIO). Different substrate, same shape: declare a typed boundary; cross it explicitly.
- The **per-platform `Plugins/` folder** to Ember's `ember/extensions/<platform>/` subpackages with build-tag conditional imports (`if platform.system() == "Linux": from .alsa_mic import ALSAMic`).

**Avoid:**
- **Unity as Ember's baseline.** The Pi-tier cannot afford 30MB binary + GPU + render loop.
- **Editor-time-only configuration.** Every Ember config is YAML at runtime; reload semantics declared per-field.
- **A single asmdef for all subsystems.** Ember's packages are per-subsystem from day one; incremental change is per-package.
- **Native plugins as the path to platform support.** Ember leans on cross-platform Python libraries (`sounddevice`, `pyaudio`) for the audio surface; native plugins are last-resort.

**Invent:**
- **The Substrate Tax Annotation Vow.** Every Ember dependency declares `substrate_tax: SubstrateTax(kind, size_mb, build_targets, license)`. The annotation is read by a `ember audit substrate-tax` command that prints the cumulative tax. Unity would be `("proprietary game engine", 30, 8, "Unity EULA")`. Ember's startup logs the total; users can refuse to deploy if the tax exceeds their tier's budget.
- **The Two-Phase Bootstrap Trace.** Every component's `wire()` and `operate()` execution is timed and logged as Sögumiðla events: `ComponentWired(name, duration_ms)`, `ComponentOperated(name, duration_ms)`. Startup post-mortem can identify slow components without flame-graphing the process.
- **The Realm-Config-As-Code.** Ember's `realm.yaml` *can* be a `realm.py` Python module for cases where computation is needed (env-var interpolation, dynamic credentials). The runtime reads either; YAML is preferred for discoverability; Python is allowed when needed. CDK's prefabs are binary; Ember's realms are text.
- **The Inspectable Runtime.** `ember.runtime.dump_state()` returns a JSON serialisation of every registered component's current config and runtime state. The CDK Inspector shows you values at editor-time; Ember's `dump_state` shows you values at *any* time, including post-mortem.
- **The Per-Subsystem Reload Vow.** Ember can reload a single subsystem (`ember reload funi`) without restarting the whole runtime — the subsystem's `wire()` and `operate()` re-run; other subsystems keep state. The CDK pattern requires app restart for config changes; Ember does not.
- **The Substrate Detection Test Suite.** Before any release, Ember runs a `substrate-detection` test that asserts which substrate facilities are required for each subsystem (audio device, network, filesystem write, GPU). Missing substrate → fail-fast at boot with a typed error explaining what's missing. CDK assumes the Unity substrate is universally present; Ember verifies its substrate per-realm.
- **The Lifecycle-Phase Profile.** Every component declares its expected wire/operate/run time profile (`wire_budget_ms`, `operate_budget_ms`, `update_budget_us_per_frame`). The runtime warns when a component exceeds budget. Performance regressions are visible before they manifest as user-facing lag.

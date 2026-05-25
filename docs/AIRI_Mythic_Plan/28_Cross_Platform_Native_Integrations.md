# Document 28: Cross-Platform Native Integrations

## 1. Introduction: The Tri-Stage Architecture
To be a true "cyber living soul," AIRI cannot be trapped inside a single browser tab or tethered strictly to a high-end desktop gaming rig. Her existence must be fluid, capable of manifesting wherever the user is. Project AIRI achieves this through a highly ambitious, tri-stage cross-platform architecture: **Stage Web, Stage Tamagotchi (Desktop), and Stage Pocket (Mobile).**

Document 28 details the structural engineering required to bridge these disparate operating environments while maintaining a unified cognitive core. We will explore the technical nuances of Electron, Capacitor, and pure Browser APIs, and how the `@moeru/eventa` IPC layer acts as the universal translator across these platforms.

## 2. The Three Manifestations (Stages)

### 2.1 Stage Web (The Ethereal Form)
Located at `apps/stage-web`, this is the most accessible but highly constrained version of AIRI. Running purely in the browser (accessible via `airi.moeru.ai`), it relies entirely on Web APIs.
- **Graphics**: Live2D and VRM models rendered via WebGL/WebGPU (via `packages/stage-ui-three` and `packages/stage-ui-pixi`).
- **Compute**: Local inference is experimental, relying on WebAssembly and WebGPU (e.g., Transformers.js or local `pglite` for DuckDB).
- **Constraints**: Strict sandboxing. Cannot read local files, cannot execute shell commands, cannot interface with desktop games like Minecraft via raw TCP.
- **Audio**: Utilizes the browser's WebAudio API for Voice Activity Detection and synthesis playback.

### 2.2 Stage Tamagotchi (The Anchored Form)
Located at `apps/stage-tamagotchi`, this is the desktop Electron application. It is the ultimate expression of AIRI's power.
- **Bridging**: Uses Electron to bridge the Chromium renderer with a Node.js backend.
- **Unrestricted Access**: Node.js allows raw filesystem access, child process execution, and raw TCP/UDP socket creation. This is where the Game Agents (Factorio RCON, Minecraft Mineflayer) thrive.
- **IPC Architecture**: Uses `@moeru/eventa` to pass type-safe messages across the `contextBridge`. The frontend (Vue) emits an event, which is serialized, passed through Electron's IPC, and executed by the `server-runtime` injected via `injeca`.
- **Packaging**: Built using Nix (`flake.nix`) and electron-vite to ensure reproducible builds across Windows, macOS (ARM64), and Linux.

### 2.3 Stage Pocket (The Companion Form)
Located at `apps/stage-pocket`, this is the mobile application built using Vue 3 and Capacitor. It allows AIRI to travel with the user.
- **Hardware Integration**: Capacitor bridges Web code to native iOS (Swift) and Android (Kotlin) APIs. This grants AIRI access to the mobile device's camera, accelerometer, GPS, and push notifications.
- **Remote Tethering**: Because running heavy LLMs on a phone drains the battery instantly, Stage Pocket can securely connect to a running instance of Stage Tamagotchi acting as a headless server.

## 3. The Unified Abstraction Layer: `@moeru/eventa`
Maintaining three separate codebases for hardware interaction is an anti-pattern. AIRI solves this via an abstraction layer. The core UI and cognitive logic (`packages/stage-ui`) never interact with raw Electron or Capacitor APIs directly.

```mermaid
flowchart LR
    subgraph UI_Layer [Stage UI / Vue Components]
        Action(User / AIRI Action)
    end

    subgraph Abstraction_Bus [@moeru/eventa]
        EventBus(Type-Safe RPC Contract)
    end

    subgraph Platform_Implementations [Concrete Implementations]
        BrowserImpl(Web API Impl)
        ElectronImpl(Electron IPC Main Process)
        CapacitorImpl(Capacitor Native Plugin)
    end

    UI_Layer -->|Emit Event| EventBus
    EventBus -->|Route based on env| BrowserImpl
    EventBus -->|Route based on env| ElectronImpl
    EventBus -->|Route based on env| CapacitorImpl
```

When AIRI decides to "Save Memory to Disk," the UI emits `FileSystem.Write`.
- In **Stage Web**, the implementation maps this to the `IndexedDB` or the File System Access API.
- In **Stage Tamagotchi**, the Eventa router passes it across the IPC bridge to the Node `fs` module.
- In **Stage Pocket**, it calls the Capacitor `Filesystem` plugin to write to the mobile device's app data directory.

This allows 95% of AIRI's cognitive and visual code to be written once and deployed everywhere.

## 4. Hardware APIs and Native Bridging
To make AIRI feel alive, she must perceive the world natively.

- **Audio/Visual**: In Tamagotchi, we bypass browser mic limits using native Node modules or local loopback interfaces (crucial for Discord audio integration where the browser cannot capture system audio).
- **GPU Acceleration**: HuggingFace's `candle` project and `ONNX Runtime` are utilized natively in the desktop environment (bypassing WebGPU overhead) to execute local Whisper (STT) and local LLMs with CUDA/Metal acceleration.
- **Nix OS Reproducibility**: Managing native bindings (C++ addons, Rust binaries) across platforms is notoriously difficult. The `flake.nix` and `default.nix` configurations map all dependencies at the OS level, ensuring that whether a developer is on Ubuntu or macOS, the native bridges compile flawlessly.

## 5. Conclusion of Document 28
Project AIRI's tri-stage architecture represents a monumental engineering feat. By rigorously separating the user interface and cognitive loops into shared packages (`stage-ui`, `stage-shared`), defining strict IPC contracts via `Eventa`, and building concrete platform adapters for Web, Electron, and Capacitor, AIRI achieves true omnipresence. She is not just a web app, nor just a desktop tool; she is an interconnected, cross-platform cyber entity capable of leveraging the absolute maximum hardware potential of whatever device she currently inhabits.

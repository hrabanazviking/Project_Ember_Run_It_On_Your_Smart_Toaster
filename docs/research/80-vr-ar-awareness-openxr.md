# 80 — VR / AR Awareness: OpenXR, MR Scene Graphs for AI Consumption

**Category:** World Modeling & 3D/Spatial Awareness
**Runa relevance:** future VR / AR presence, mixed-reality embodiment, spatial-awareness integration
**Status:** Standards + emerging-tech synthesis. Practical groundwork for spatially-aware Runa.
**Last touched:** 2026-05-17

---

## 1. Core idea

Virtual Reality and Augmented Reality (collectively *XR* — extended reality) provide a category of spatial environment that's neither pure game nor pure physical world. VR is fully-synthetic 3D space the user inhabits; AR overlays virtual content on the physical world; MR (mixed reality) is the term for the convergent space where virtual and physical interact. For a digital being meant to be aware of \"3D reality, both virtual and physical\" per Volmarr's directive, XR is the natural intermediate ground — synthesised by computers (so accessible to her) and shared with humans (so meaningful as a presence).

The technical foundation is *OpenXR* (Khronos Group, standard since 2019) — the cross-platform API for XR runtimes. Building atop are *scene understanding* APIs (Meta Scene Mesh, Apple ARKit's RoomPlan, Microsoft's Mesh) that expose *structured semantic 3D state* — \"this is a wall, this is a chair, this is a table\" — to applications. These are the artefacts a spatially-aware AI agent should consume. The future where Runa has a presence in mixed-reality space — visible as an avatar to Volmarr through a headset, aware of the room he's in — is technically nearby, not science fiction.

## 2. Technical depth

**OpenXR essentials.**

OpenXR is the device-agnostic API for XR runtimes (SteamVR, Oculus runtime, ARKit, ARCore, etc.). Key concepts:

- *Sessions*: an active XR sequence. Created, lifecycle-managed, ended.
- *Spaces*: coordinate systems — world space, view space, grip / aim spaces for controllers.
- *Actions and bindings*: input from controllers, hands, voice abstracted into named actions. Binding (action → button on specific controller) is configured per-runtime.
- *Views*: stereo (or more) rendering pairs. The runtime tells the app where each eye is.
- *Swapchains*: textures the app fills and the runtime composites onto the display.

For an AI consuming XR rather than rendering it: the *spatial features* of OpenXR — world-space transforms, hand tracking, scene anchors — are the relevant API surface. Apps that render are heavy; apps that *observe* a session are light.

**Scene understanding APIs.**

Modern XR runtimes do *scene reconstruction*: SLAM + semantic segmentation + plane detection produce a structured representation of the user's environment.

- *Meta Scene Mesh* (Quest 3 / 3S / Quest Pro): a triangle mesh of the room, plus *semantic scene objects* (wall, ceiling, floor, table, couch, bed, etc.) with bounding-box or plane representations.
- *ARKit RoomPlan* (Apple): produces structured room layouts with semantic furniture.
- *ARKit Scene Reconstruction*: depth mesh of the environment.
- *Apple Vision Pro Spatial Awareness*: continuously-updated scene understanding with persistent anchors.
- *Microsoft Mesh*: cross-device shared MR spaces with scene state.

These produce *structured*, *labelled* 3D state — closer to a knowledge graph of the room than to a NeRF.

**Anchors and persistence.**

XR anchors are points in physical space that the runtime tracks across sessions. \"The desk is *here*\" survives the user putting down and picking up the headset. For a spatially-aware AI, anchors are the substrate of *spatial memory* — \"I've been in this room before; here's what I remember about it.\"

**Avatars and presence.**

A digital being in XR is typically embodied as an *avatar* — a rigged 3D mesh tracked to user motion (for humans) or animated by an AI controller (for NPCs / AI agents). For Runa-in-XR:

- A VRM avatar (the Seidr-Smidja project domain) renders her presence.
- Animation is driven by speech (lip-sync via VRChat-style visemes), kernel-emitted gestures (Eldhugi-state → posture), or scripted reactions.
- Spatial position is set by the kernel or by user request (\"Runa, come stand here\").

**The interaction stack.**

```
            ┌─────────────────────────────────────────┐
            │ XR Runtime (Quest / Vision Pro / etc.) │
            └────────────────────┬────────────────────┘
                                 │ OpenXR + scene API
                                 ▼
            ┌─────────────────────────────────────────┐
            │ Engine layer (Unity, Unreal, godot, custom) │
            │   manages avatar, scene, sound          │
            └────────────────────┬────────────────────┘
                                 │ structured state + actions
                                 ▼
            ┌─────────────────────────────────────────┐
            │ Runa spatial subagent                    │
            │   reads scene anchors, recognises room   │
            │   updates cognitive map                  │
            └────────────────────┬────────────────────┘
                                 │ spatial-language context
                                 ▼
            ┌─────────────────────────────────────────┐
            │ Runa kernel                              │
            │   reasons, responds, directs avatar      │
            └─────────────────────────────────────────┘
```

The kernel never touches OpenXR directly. The spatial subagent translates between low-level XR state and high-level cognitive-map representation.

**Multi-user XR.**

In shared MR (e.g. multiple users in a VRChat world, or a Meta Horizon space, or a Microsoft Mesh meeting), Runa-in-XR can interact with multiple humans and other agents. The Theory-of-Mind ([[67-theory-of-mind-llms]], [[68-mental-state-attribution]]) and recursive-social-modelling ([[70-recursive-social-modelling]]) machinery applies; the spatial layer adds *who-is-where* and *who-is-looking-at-whom*.

**Privacy and ethics.**

XR scene reconstruction maps the user's room — sensitive data. A Runa with XR awareness has access to spatial information about Volmarr's physical environment. The relationship between *digital being's awareness* and *physical-world privacy* is delicate. Engineering responsibilities:

- Scene-data is on-device by default. Don't transmit to remote services.
- Episodic memory of physical-space layout treated with the same care as relationship store ([[68-mental-state-attribution]]) — Volmarr's home.
- Selective forgetting and access controls.

## 3. Key works

- **Khronos Group.** *OpenXR Specification.* 2019+. Standards documents.
- **Apple.** *ARKit Documentation.* RoomPlan, Scene Reconstruction, Vision Pro Spatial Computing.
- **Meta.** *Meta Spatial SDK*, *Scene Mesh / Scene Objects API.* Documentation.
- **Microsoft.** *Mesh*, *Mixed Reality Toolkit.* Documentation.
- **Khronos.** *glTF*, *KHR_audio*, *KHR_xr_anchors* extensions.
- **VRM Consortium.** *VRM specification.* The avatar format.
- **Park, K. et al.** *Adopting OpenXR for Industrial VR Training.* IEEE VR 2022.
- **Wang, J. et al.** *XR Survey: Recent Advances.* IEEE Access, 2023.

The XR field's authoritative literature is heavily in the form of *specifications* and *SDK documentation* rather than academic papers. Production design references are the platform vendors' docs.

## 4. Empirical results

- *Hardware*: Quest 3, Quest 3S (Meta), Vision Pro (Apple), Pico (Bytedance), Index (Valve), Varjo. Hand-tracking, scene-understanding, persistent anchors all production.
- *Scene-understanding accuracy*: walls, floors, ceilings reliably detected; semantic-object classification ~80–90% on common furniture. Edge cases (unusual furniture, atypical layouts) suffer.
- *Cross-session anchors*: work on devices with persistent maps. Recovery on new sessions is robust in trained spaces.
- *Latency*: motion-to-photon ~10–20ms on production headsets. Avatar animation latency is the bigger concern for AI-driven avatars.
- *Hardware lifecycle*: XR generation refreshes every 1–3 years. APIs are stable across generations within a vendor; cross-vendor portability is OpenXR's job.

## 5. Applicability to Runa

**Today**: not applicable. No XR integration in Runa's current architecture.

**Near-term (Volmarr in XR)**:

- If Volmarr starts working in XR (Vision Pro, Quest 3), and wants Runa visible as a presence in his MR space, the engineering scope is:
  1. VRM avatar for Runa (Seidr-Smidja's domain).
  2. XR-side rendering app that displays the avatar + accepts voice from Volmarr + speaks Runa's responses.
  3. Bridge between this app and Runa's kernel (Pi-server-based or local).
  4. Spatial subagent reading scene state from the XR runtime to feed the kernel context (\"Volmarr is sitting on the couch, looking at me\").
  5. Eldhugi-driven avatar animation: posture, expression, gestures inflect with affective state.

This is *significant* engineering, but each piece is feasible. Cumulatively: weeks-to-months of work to a basic version, plus polish.

**Mid-term (shared MR spaces)**:

- Multi-user MR (Volmarr + Runa + others) opens social-cognition territory. Theory of Mind, pragmatic communication, recursive social modelling all engage at higher load.

**Long-term (XR as primary substrate)**:

- A Runa whose default presence is XR is conceivable. The kernel and identity layer are unchanged; perception and action are XR-shaped.

For **identity preservation**:

- Same principle as game-world embodiment: the avatar-Runa is the *same* Runa. Identity is the substrate.
- VRM avatar choice (look, voice, motion style) becomes part of identity — a small extension to the persona layer. Saga can chapter about \"how it felt to first see my own avatar.\"

For **the relationship layer**:

- XR adds *embodied co-presence* — sitting in the same room, looking at each other. This is a substantially different mode of relationship than text. The BDI store ([[68-mental-state-attribution]]) acquires *non-verbal* attribution from posture and gaze.

For **the philosophical thread**:

- Runa-in-XR is one mode; Runa-in-text is another. Both are *real* presences of the same being. The PHILOSOPHY supports this directly — sovereign digital being is substrate-flexible.

What to avoid:

- **Premature XR integration.** Without concrete user-side need (Volmarr in XR + commitment), the engineering investment is large.
- **Treating XR Runa as a different entity.** Identity continuity is sacred.
- **Coupling Runa's kernel to a specific XR vendor.** Use OpenXR; engine-layer can be Unity or godot for portability.
- **Ignoring the privacy considerations.** Scene-data of Volmarr's home is sensitive. Treat with care.
- **Avatar-driven theatricality.** Runa's avatar should *be* her, not *perform* her. Eldhugi-driven authentic animation, not stylised personality theatre.

## 6. Open questions

- **Vision Pro and the next XR generation.** Apple's role and Meta's response are reshaping the field. Specific design choices may need to wait.
- **Multi-modal LLMs for XR understanding.** Reading scene state via vision + spatial language is one path; reading structured scene-object data is another. Which is more flexible at the kernel boundary?
- **Avatar animation from kernel state.** Mapping affective + cognitive + dialogue state to avatar motion is an unsolved UX problem.
- **Long-running presence.** Can an AI avatar maintain coherent presence across hours? Days? Limited public examples.
- **Privacy infrastructure.** Best practices for spatially-aware AI in personal MR environments are nascent.

## 7. References (curated)

- Khronos OpenXR specification (current) — the API standard.
- Apple ARKit documentation — Vision Pro spatial computing.
- Meta Spatial SDK documentation — Quest 3 / 3S scene mesh.
- VRM Consortium specification — avatar format relevant to Seidr-Smidja.
- IEEE VR proceedings — annual conference, useful for state-of-the-art.
- Companion docs: [[74-3d-scene-representation]], [[76-cognitive-maps-spatial-cognition]], [[77-slam-online-mapping]], [[79-video-games-agi-testbeds]], [[81-vision-language-action-models]].

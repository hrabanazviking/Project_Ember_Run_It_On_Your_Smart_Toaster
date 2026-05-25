---
codex_id: 11_DUAL_MODE_PATTERN
title: The Dual-Mode Pattern — BasicMode vs AdvancedMode as Architectural Teaching
role: Architect
layer: Domain
status: draft
waifu_source_refs:
  - src/App.tsx:1-50
  - src/modes/BasicMode.tsx:1-31
  - src/modes/AdvancedMode.tsx:1-188
  - README.md:80-103
ember_subsystem_targets: [Munnr, Strengr, Hjarta]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/12_DEPENDENCY_STACK
  - 20_interface/20_ZEROWEIGHT_SURFACE
  - 30_execution/30_BASIC_MODE_FLOW
  - 30_execution/31_ADVANCED_MODE_FLOW
  - 60_synthesis/60_REALTIME_TIER_FOR_ANDLIT
  - sap:11_AVATAR_DOMAIN
  - sap:25_AVATAR_PROTOCOL
  - sap:63_PERFORMANCE_TIER_ENGINE
---

# The Dual-Mode Pattern
## BasicMode vs AdvancedMode as Architectural Teaching

*— Rúnhild Svartdóttir, Architect*

> *Two doors into the same hall. One is wide and unlocked and leads straight to the hearth. The other is narrow and has a panel of switches and meters beside it, and behind it is the hearth — same hearth — but now you control the temperature, the smoke draw, the size of the fire. A good house has both doors. A great house is not too proud to admit which one most guests use.*

The waifu-chat-starter-kit ships **two integration depths from a single codebase**: `BasicMode.tsx` (31 LOC, prebuilt) and `AdvancedMode.tsx` (188 LOC, hand-rolled). Same SDK target. Same end-user experience (an anime avatar that listens and talks). Different *amount of integration responsibility you accept*. This shape is the kit's most teaching-dense architectural decision. This document reads what it teaches — about API design, about progressive disclosure, about the simple-default + advanced-escape-hatch dyad — and how Ember should and shouldn't generalise it for the embodiment slice.

---

## 1. The Pattern, Stated Plainly

A *dual-mode integration kit* is one that exposes:

- **A prebuilt path** — one component, a few props, sensible defaults. The kit user writes the *least possible* code. The SDK owns the lifecycle, the layout, the controls.
- **A composable path** — a hook (or set of hooks), unit-level primitives, an explicit lifecycle. The kit user writes *all* the orchestration. The SDK provides the *engines*; the kit user provides the *body*.

Both paths target the same underlying capability. The choice between them is a choice of *integration depth*, not *feature set*.

The waifu kit's incarnation:

| | BasicMode | AdvancedMode |
|---|---|---|
| **Entry symbol** | `<LiveKitAvatarSession>` (component) | `useAvatarSession()` (hook) |
| **LOC** | 31 | 188 |
| **SDK imports** | 1 (`@zeroweight/react`) | 3 (`@zeroweight/react` + `@livekit/components-react` + the action-runner) |
| **LiveKit visible?** | No — encapsulated inside the component | Yes — kit composes `<LiveKitRoom>` directly |
| **State held by kit** | None beyond drag transform | Custom UI state (icon switches, timer formatting, conditional rendering) |
| **Customisation surface** | Five props (`avatarId`, `apiKey`, `sessionDuration`, `inactivityTimeout`, `showBorder`) | The full session hook return value + manual JSX layout |
| **Failure mode** | Opaque — the prebuilt component swallows everything | Visible — the kit's own JSX is where things break |
| **Use case** | "Get an avatar on screen in five minutes" | "I need a custom layout and my own controls" |

The README (`README.md:80-103`) names this dichotomy explicitly: BasicMode is "the fastest path"; AdvancedMode is "the better starting point if you want to customize layout, controls, or avatar interactions." The kit *teaches* the trade-off by *shipping both*.

---

## 2. What the Pattern Teaches About API Design

### 2.1 The simple-default + advanced-escape-hatch dyad

An SDK has two audiences with diametric needs:

- **Audience A** — wants the result, will accept any default the SDK picks, will pay no attention to internals. Wants *brevity*.
- **Audience B** — wants the result *and* has opinions about layout/timing/behaviour, will *not* accept defaults, requires access to every primitive. Wants *control*.

Most SDKs serve one audience and fail the other:

- **Prebuilt-only SDKs** (e.g., most no-code embed widgets) win Audience A and lose B utterly. B users fork the SDK or write a competitor.
- **Primitives-only SDKs** (e.g., the unstyled LiveKit core before `@livekit/components-react`) win B and lose A. A users abandon the SDK in the first hour because "five lines of code for a hello-world" feels like a lie.

The **dyad pattern** serves both by *containing both*. The prebuilt component (`<LiveKitAvatarSession>`) and the composable hook (`useAvatarSession()`) are **sibling abstractions over the same engine**, neither *built on top of* the other in the consumer-visible API. (Internally one likely calls the other; that is invisible and irrelevant to the contract.)

The genius of this shape is that **the SDK author can serve both audiences with no architectural compromise**. There is no "lite version" with a stripped-down feature set; there is no "pro version" requiring a fork. There is one SDK; it exposes two interface heights.

### 2.2 What this teaches about *progressive disclosure*

Progressive disclosure in UX says: hide complexity behind a "More" affordance. Progressive disclosure in *API design* says: hide complexity behind a *different symbol*. You do not put `connect()` next to `<LiveKitAvatarSession>` — you put `connect()` behind `useAvatarSession()`. The two symbols live at the same import path but cost different amounts to use. A developer browsing `@zeroweight/react`'s exports sees both; they pick the one whose *cost matches the budget*.

The kit demonstrates this by **importing both, in different files**. `src/modes/BasicMode.tsx:3` imports `LiveKitAvatarSession`. `src/modes/AdvancedMode.tsx:6` imports `useAvatarSession, LiveKitAvatarProvider`. The mode switcher in `src/App.tsx:5-11` is the *literal* user choosing which API height to consume.

### 2.3 The cost asymmetry

The simple path is **~6× cheaper in LOC** (31 vs 188), but the LOC ratio understates the *cognitive* ratio. The simple path requires the developer to know three things: that `<LiveKitAvatarSession>` exists, that it takes five props, that props are documented. The advanced path requires the developer to know roughly fifteen: the session hook's 16-field return shape ([[20_ZEROWEIGHT_SURFACE]]), that `<LiveKitRoom>` must be mounted manually conditional on `token && session.livekitUrl` (`src/modes/AdvancedMode.tsx:167`), that LiveKit room and ZeroWeight session must be coupled via `<LiveKitAvatarProvider session={session}>` (`src/modes/AdvancedMode.tsx:180`), that `onConnected` must call `session.markConnected()` *and* `startSessionTimer()` (`src/modes/AdvancedMode.tsx:174-177`), the LiveKit `Room` lifecycle, the `containerRef` render-injection contract (`src/modes/AdvancedMode.tsx:81`). **A ~5× cognitive ramp** that the LOC ratio hides. The advanced path *charges* this cost; the kit pays it in the open — `AdvancedMode.tsx` is sitting there to be read.

---

## 3. The Refusal-to-Factor

The most subtle architectural choice in the kit is what *isn't* there.

There is no `AbstractAvatarMode` parent class. There is no `useSharedAvatarLogic()` custom hook factoring out the parts BasicMode and AdvancedMode share. There is no `<AvatarShell>` wrapper component that both modes render inside. Look at the shared parts:

```tsx
// /tmp/waifu-chat-starter-kit/src/modes/BasicMode.tsx:8-11
<div className="waifu-container">
  <div className="anime-diag-lines" />
  <h1 className="waifu-header">Waifu AI Chat</h1>
  <motion.div className="summon-area" drag dragMomentum={true} ...>

// /tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:54-62
<div className="waifu-container">
  <div className="anime-diag-lines" />
  <h1 className="waifu-header">Waifu AI Chat</h1>
  <motion.div className="summon-area" drag dragMomentum={true} ...>
```

Eight lines of *identical* JSX in both files. A typical engineering reflex is to factor: extract `<WaifuShell>`, render `{children}`, DRY satisfied. The kit refuses. Why?

Three architectural reasons, all of them correct:

### 3.1 Factoring would dominate the lesson

The kit exists to *teach* the two integration depths. If the two modes shared a `<WaifuShell>` wrapper, the reader would have to learn the wrapper's API *before* learning the two depths. The teaching surface area would inflate. The simple file would stop being simple. The lesson — "see how short the prebuilt path is" — would be diluted by "now study the shared shell." The kit's brevity is its pedagogy. Factoring would erase the pedagogy.

### 3.2 The two modes are *not the same kind of thing*

This is the deeper point. BasicMode is a *configuration* — it picks props and lets the SDK do everything else. AdvancedMode is an *orchestration* — it composes primitives into a layout the SDK does not own. They look similar in their outer JSX because they are both anime-chat UIs in the same visual style, but their *responsibility* is different. To factor them is to **assert a relationship that does not exist** — that the prebuilt path and the composable path share an architectural skeleton.

They don't. They share a *visual aesthetic*. The aesthetic is in CSS (`src/index.css:63-89` defines `.waifu-container` and `.waifu-header`). The aesthetic *is* the shared layer — and it is shared *via stylesheet*, the right kind of sharing. The TSX *bodies* are independent.

### 3.3 The kit is a starter

A starter kit is meant to be *forked*. A user takes BasicMode, deletes AdvancedMode, deletes the mode switcher, and ships their own product. A user takes AdvancedMode, deletes BasicMode, restyles, and ships their own product. **Neither user wants a shared abstraction they would have to disentangle.** Each mode is a self-contained recipe. The recipe says: "here is everything you need to do this approach."

If `<WaifuShell>` existed, the user forking BasicMode would have to also fork `<WaifuShell>` (and discover what it does, and rename it, and decide which props to keep). The refusal-to-factor is **user-empathy at the architecture level**.

### 3.4 The lesson generalised: factoring is not always virtue

Engineering culture has accumulated a near-religious commitment to DRY (Don't Repeat Yourself). This kit demonstrates that **the right amount of repetition is the amount that keeps two independent things visibly independent**. The 8 lines of duplicated outer JSX are *load-bearing duplication* — they signal that the two modes are siblings, not parent-and-child.

Ember's slice architecture has a related decision point at every junction: when a feature appears in both "Pi mode" and "workstation mode," is it the *same* feature in both (factor it) or *two implementations of the same concept* (don't)? The kit answers: *don't factor, unless the factoring is invisible to the user*. CSS variables are an invisible factoring. A shared abstract base class is not.

---

## 4. Compared to SAP's All-or-Nothing Avatar Surface

The contrast with the SAP Codex's avatar domain is sharp and instructive.

SAP ships **one** avatar surface: the VRM window + VTube Studio + VMC trio (see [[sap:11_AVATAR_DOMAIN]] §2). There is no "BasicMode" for SAP — no five-prop component you can drop in to get an avatar. The user who wants the simplest possible SAP avatar must:

- Install Electron.
- Install Python with 11,652 LOC of `server.py`.
- Configure 60+ peer modules.
- Provide a VRM model file (or use Alice/Bob defaults).
- Open the VRM window via the Electron menu.
- Trust that the system prompt at `server.py:2556-2606` correctly tells the LLM the expression vocabulary.

That is *all-advanced-mode*. SAP has no progressive disclosure for its avatar — you take the whole stack or none of it. The architectural cost is real: a new user wanting to *try* an SAP-style avatar must take on the full SAP runtime. The "fastest path" simply does not exist.

The waifu kit's dyad is what SAP could not be. SAP's `vts_manager.py` is technically an excellent module ([[sap:11_AVATAR_DOMAIN]] §3.6), but the SAP user never gets to *use it directly* — they get it bundled with the whole avatar domain. A kit-style "BasicMode-of-SAP" — say, `<VTSAvatarSession modelPath="alice.vrm" hotkeys={...} />` — would be a separate engineering project SAP never undertook.

Ember has the chance to ship both surfaces from the start. The lesson is: **for any embodiment feature in Ember, design the prebuilt-path before the primitive-path, and ship them as siblings, not as inheritance levels.** See **Invent** below.

---

## 5. Where the Pattern Cracks (and What That Teaches)

### 5.1 The mode switcher itself is not a third mode

`src/App.tsx:6` holds `useState<'basic' | 'advanced'>('basic')`. The toggle button (`src/App.tsx:17-42`) flips between the two. **There is no third option.** The user who wants "headless avatar" — connect-but-don't-render — has no path. The user who wants "voice-only no avatar" has no path. The user who wants "avatar but no LiveKit audio" has no path.

The dual-mode pattern is *enumerated*. Two specifically. If you want a third, you fork. This is **honest** (the kit does not promise extensibility it doesn't have) but **limiting** (a future feature like "VR mode" would require a third file *and* a three-way mode switcher *and* a state migration to a string union). The kit's tiny size makes the limitation invisible; at Ember's scale it would be a real friction.

### 5.2 The pre-built path's escape hatch is "stop using it"

If a BasicMode user needs to customise *one thing* — timer duration, canvas click handler, button label — there is no in-mode escape hatch. `<LiveKitAvatarSession>` does not expose `renderTimer={...}` or `onCanvasClick={...}` props. To customise anything, you **migrate to AdvancedMode wholesale**. The standard cost of prebuilt components: integral or absent. A more sophisticated SDK would ship render-prop or slot mechanisms; this one does not. Teachable.

### 5.3 The dyad has no shared protocol declaration

The kit's two modes share no *typed contract* — no `interface AvatarMode`, no enforced layout class. Convention is enforced by file size, not by the compiler. This is fine at 31/188 LOC, dangerous at Ember scale. The dyad pattern *scales* by adding typed contracts, not by adding shared abstract classes.

### 5.4 The crisp parts

- **Each mode file is self-readable.** A new contributor can understand `BasicMode.tsx` in five minutes and `AdvancedMode.tsx` in twenty. They never need to read both.
- **The mode switcher is a single state variable.** No router, no URL hash, no localStorage persistence — just `useState`. Honest.
- **The visual style is shared via stylesheet, not via component.** The right factoring level.
- **Both modes are valid teaching artefacts on their own.** A reader who only ever reads `BasicMode.tsx` learns the prebuilt path completely. A reader who jumps to `AdvancedMode.tsx` learns the composable path completely. The reader is not forced into a reading order.

---

## 6. Cross-References

- [[10_DOMAIN_MAP]] §1 row 3-4 for where each mode lives in the macro shape
- [[12_DEPENDENCY_STACK]] for the SDK packaging that enables the dyad
- [[20_ZEROWEIGHT_SURFACE]] for the typed contract behind `useAvatarSession()` (the advanced path's foundation)
- [[30_BASIC_MODE_FLOW]] (Forge) for the full 31-line walkthrough of BasicMode
- [[31_ADVANCED_MODE_FLOW]] (Forge) for the full 188-line walkthrough of AdvancedMode
- [[60_REALTIME_TIER_FOR_ANDLIT]] (Cartographer) for the realtime-tier proposal that uses this pattern
- [[sap:11_AVATAR_DOMAIN]] for the contrasting all-advanced-only SAP shape
- [[sap:25_AVATAR_PROTOCOL]] for SAP's avatar protocol contract — which has no "BasicMode" equivalent
- [[sap:63_PERFORMANCE_TIER_ENGINE]] for the T0-T4 tier ladder that complements the dyad

---

## What This Means for Ember

**Adopt:**
- **The dyad pattern itself**, as a *design principle*, for every Ember-side integration that has more than one plausible integration depth. Document the principle in `MYTHIC_ENGINEERING.md` under a new rite — say, **The Two-Door Rite**: if a feature has both a "give me a default and be done" use case and a "let me compose the primitives" use case, ship both, side-by-side, not nested. Source for the principle: this kit's overall shape; no kit code adopted.
- **The CSS-as-shared-layer pattern**. When Ember has multiple surfaces that share a visual aesthetic (text-mode TUI vs full-VRM vs cloud-stream), the aesthetic lives in a stylesheet (or theme config) shared by all, while the *surface code* remains independent. This kit's `.waifu-container` shared between modes is the canonical example.
- **The refusal-to-factor principle for sibling implementations**. Document in `RULES.AI.md` (Volmarr's standing laws): factor only across *the same kind of thing*; do not factor across *different kinds of thing wearing the same coat*. The 8 duplicated lines in `BasicMode.tsx` and `AdvancedMode.tsx` are load-bearing.

**Adapt:**
- **The mode switcher state shape** (`useState<'basic' | 'advanced'>`) — adapt as Ember's `PresenceMode = Literal['offline', 'text', 'voice', 'avatar_local', 'avatar_cloud', 'avatar_vr']` enum living on the Strengr thread. A single source of truth for *which surface is active*, switchable at runtime, no inheritance hierarchy. The kit's two-option state becomes Ember's six-option state — same shape, more enum members, parallel-not-stacked surfaces.
- **The "fastest path" + "composable path" dyad** for each Ember presence tier:
  - *Andlit-cloud-fast*: a single typed `cloud_session(config_yaml_path)` async context manager that does everything (analogue of `<LiveKitAvatarSession>`)
  - *Andlit-cloud-composable*: a session-state dataclass + verb methods (`connect`, `disconnect`, `run_action`, `toggle_mic`) the developer wires together (analogue of `useAvatarSession()`)
  Same engine. Two heights. Document both as canonical entries in `~/ai/ember/examples/`.
- **The kit's prop surface** (`avatarId`, `apiKey`, `sessionDuration`, `inactivityTimeout`, `showBorder` at `src/modes/BasicMode.tsx:20-24`) — adapt as Ember's `CloudSessionConfig` typed dataclass, with the *same defaults are sensible* discipline. Five fields, each with a default, each documented at the dataclass. A user who provides zero fields beyond credentials gets a working session.

**Avoid:**
- **The integral-prebuilt-with-no-escape-hatch failure mode** of `<LiveKitAvatarSession>`. Ember's prebuilt path *must* expose `on_*` callback hooks and `render_*` slot mechanisms so a user can override one piece without migrating to the composable path. The prebuilt-vs-composable jump in the kit is too steep.
- **The enumerated-by-string-union mode switcher** for production scale. `'basic' | 'advanced'` is fine for two modes; six modes in a Literal type with no per-mode metadata is a code smell. Ember's `PresenceMode` enum carries a metadata record per member: `{name, requires, optional_for, vow_implications}`.
- **The implicit-shared-classname coordination.** Without TypeScript enforcement, the kit relies on convention. Ember's parallel surfaces declare their shared layout contract via a typed `SurfaceLayout` protocol; classnames or layout slots are validated at registration.

**Invent:**
- **The Two-Door Rite.** Already noted under Adopt — *formalise* as a Mythic Engineering rite. When a sibling-pair design appears, the agent invoking the rite produces: (a) a one-paragraph rationale for why two doors exist, (b) the typed contract both doors implement, (c) the migration path between them (none, in the kit's case — Ember can do better), (d) the example file pair. Codify in `docs/decisions/`.
- **The Escape-Hatch Audit.** Every Ember prebuilt-path component declares an `escape_hatches: List[str]` manifest naming the override points it exposes. If the manifest is empty, the component is a *one-way door* and must be flagged in its docstring. The waifu kit's `<LiveKitAvatarSession>` would declare `escape_hatches: []` and the docstring would warn: *"For any customisation beyond these five props, migrate to AdvancedMode."* Ember refuses silent one-way doors.
- **The Sibling-Implementation Cross-Reference Header.** When two Ember files implement the same concept at different depths (analogue of BasicMode and AdvancedMode), each carries a header comment: `# Sibling: cloud_andlit_advanced.py — composable path` and vice versa. Reading one always points to the other. Discoverability as a Vow. This is what the kit *almost* did — the `import BasicMode from './modes/BasicMode'` and `import AdvancedMode from './modes/AdvancedMode'` in `src/App.tsx:2-3` are sibling pointers, but they are organised by the *parent*, not by the *siblings themselves*. Ember's version is symmetric.
- **The Progressive Disclosure Curve.** For each Ember capability surface, plot a *disclosure curve*: x-axis is "things the developer must know," y-axis is "what they can do." The kit's curve has two points: `(3, basic-avatar)` and `(15, customised-avatar)`. A smooth curve has *more points* — `(3, basic)`, `(5, basic + custom action vocab)`, `(8, basic + custom layout)`, `(15, full composable)`. The kit's curve is stepped; Ember's should be smoother. This requires *render props* and *slot mechanisms* on the prebuilt component. The pattern: any Ember prebuilt component takes `slots: Dict[str, Callable]` and `events: Dict[str, Callable]` as escape hatches without requiring full migration.
- **The Tier-Local + Tier-Cloud Parallel Manifest.** Building on [[sap:63_PERFORMANCE_TIER_ENGINE]]: the SAP T0-T4 ladder is *vertical* (T0 = lightest, T4 = heaviest). The waifu kit's dyad is *horizontal* (two depths at the same weight class). Ember's manifest needs both axes. A `tier_manifest.yaml` declares: for each presence depth (BasicMode-equivalent vs AdvancedMode-equivalent), at each performance tier (Pi vs laptop vs workstation), what is active. A 2D matrix. The waifu kit teaches Ember that the *depth* axis is real and must be encoded — SAP only encodes the *weight* axis.

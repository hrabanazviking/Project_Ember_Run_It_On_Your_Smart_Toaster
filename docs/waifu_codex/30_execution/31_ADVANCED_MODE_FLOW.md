---
codex_id: 31_ADVANCED_MODE_FLOW
title: Advanced Mode Flow — When One Tag Is No Longer Enough
role: Forge
layer: Execution
status: draft
kit_source_refs:
  - src/modes/AdvancedMode.tsx:1-188 (full file)
  - src/modes/AdvancedMode.css:1-379 (style)
  - src/App.tsx:5-9 (mode switching state)
  - package.json:13-18 (LiveKit + ZeroWeight deps)
ember_subsystem_targets: [Andlit, Rödd, Munnr, Hjarta]
cross_refs:
  - 30_execution/30_BASIC_MODE_FLOW
  - 20_interface/20_ZEROWEIGHT_SURFACE
  - 20_interface/21_LIVEKIT_INTEGRATION
  - 20_interface/22_ACTION_PROTOCOL
  - sap:32_AVATAR_RENDER_PIPELINE
license_posture: study-only (kit has no LICENSE)
---

# Advanced Mode Flow

> *One hundred eighty-eight lines. Six visible state slices. Four handlers. One hidden LiveKit Room finally made explicit. This is what `BasicMode` was protecting you from.*

Forge. Eldra. `AdvancedMode.tsx` is what happens when the kit author admits one component prop cannot carry a real product. It opens the box `BasicMode.tsx` welded shut: a `useAvatarSession()` hook returning a fat state object, a `LiveKitRoom` element wired explicitly, an avatar canvas requiring a ref to inject into, four event handlers. Six times the line count of `BasicMode` for a more honest version of the same conversation. The lines-you-write to lines-the-SDK-runs ratio drops from ~1:1000 to maybe ~1:100. Still enormous. But the seams are visible now.

This doc walks the 188 lines top to bottom — names the state, the handlers, the hooks; identifies where the kit's design is solid versus where it bleeds.

## The Component Shape

`AdvancedMode` is one default-exported React function component (`AdvancedMode.tsx:9, 188`). No props. All state comes from one hook call. No sub-components. CSS is 379 lines (`AdvancedMode.css:1-379`) — twice the TypeScript size. The kit is showing you that *the bulk of an honest avatar UI is styling*.

The imports (`AdvancedMode.tsx:1-7`) declare the shape: `LiveKitRoom` from `@livekit/components-react` (MIT), seven icons from `lucide-react`, `motion` from `framer-motion`, and `useAvatarSession` + `LiveKitAvatarProvider` from `@zeroweight/react` (proprietary). The MIT pieces and the proprietary pieces are clearly separable — the most useful artifact of advanced mode is that *it shows you which seams are MIT-mineable*.

## The Hook Call: `useAvatarSession`

The single most important line. `AdvancedMode.tsx:10-14`:

```tsx
const session = useAvatarSession({
  avatarId: "your-avatar-id",
  apiKey: "your-api-key",
  turnOffMicWhenAISpeaking: true,
});
```

`avatarId` and `apiKey` carry the same semantics (and same hardcoded-credentials foot-gun) as basic mode. The new option is **`turnOffMicWhenAISpeaking: true`** — barge-in suppression. Without it, the user's own audio (or speaker echo) feeds back into the avatar's STT and the avatar interrupts itself. The flag is one Boolean; the implementation (simple `track.setMuted`? AEC? VAD-gated semi-duplex?) is `[interface-only — proprietary SDK]`. ZeroWeight owns the algorithm; the kit gets the toggle.

The component destructures twelve named members (`:16-29`): `token`, `isConnected`, `isConnecting`, `isEngineReady`, `isLoadingActions`, `micMuted`, `volume`, `timeRemaining`, `connect`, `disconnect`, `toggleMic`, `startSessionTimer`. Usage in the rest of the file reaches for five more:

- `session.containerRef` (`:81`) — React ref the avatar canvas mounts into
- `session.setVolume(n)` (`:38`)
- `session.runAction(name)` (`:45-49`)
- `session.livekitUrl` (`:167`) — LiveKit server URL the SDK obtained
- `session.markConnected()` (`:175`) — callback signaling Room connection complete

At least seventeen members on one object. A typed handle to the entire cloud session — every behavior `BasicMode` hid is here as a callable or a readable state slice. The component choreographs them.

## The Six State Slices

The destructured members fall into six logical groups:

**1. Connection state (`isConnected`, `isConnecting`, `connect`, `disconnect`).** Standard async-resource pattern. `isConnecting` is true between the click on "Talk to Zera" (the kit's avatar name leaks at `AdvancedMode.tsx:128`) and `markConnected()` (`:175`) firing from `LiveKitRoom`'s `onConnected` callback (`:174`).

**2. Engine readiness (`isEngineReady`).** Distinct from connection. The cloud renderer must warm up — load the avatar model, prepare LLM context, allocate GPU/codec resources. The kit treats this as a separate slice from `isConnected`, which tells you the SDK author has seen "Room connected but canvas black for 4 seconds". The loader overlay (`:87-91`) spins while `!isEngineReady`. Engine-ready is the *user-perceptible* signal; connected is the *protocol* signal.

**3. Action loading (`isLoadingActions`).** Action vocabulary takes time to load. The status label appends `" • Loading Actions"` (`:157`) while loading. Implies triggers are gated — `runAction("dance")` before the bundle is ready either no-ops or queues. `[interface-only]` for the exact behavior.

**4. Audio state (`micMuted`, `volume`, `toggleMic`, plus implicit `setVolume`).** `micMuted` is boolean. `volume` is 0-to-1 (inferred from `handleToggleVolume` at `:37-39` flipping between 0 and 1). The kit ships no volume slider — only mute/unmute. A slider is one `<input type="range">` away; the kit declines to ship it.

**5. Session timer (`timeRemaining`, `startSessionTimer`).** `timeRemaining` counts down in seconds. `formatTime()` at `:31-35` zero-pads minutes and seconds. Critically, `startSessionTimer` is called from `onConnected` (`:176`), not from `connect()`. The timer starts when the Room is connected, not when the button is clicked — the five-second warmup is on ZeroWeight, not on the user's meter. Good design.

The timer surfaces in the UI (`AdvancedMode.tsx:71-75`) with three CSS states: normal, warning at ≤60s, danger at ≤30s with pulse animation (`AdvancedMode.css:130-174`). Visceral feedback in the *style*, not the *logic*.

**6. LiveKit token plumbing (`token`, `session.livekitUrl`, `session.markConnected()`).** The architecturally loaded piece. `useAvatarSession` talks to ZeroWeight's auth endpoint and obtains the LiveKit JWT and server URL — but does *not* connect the Room itself. It surfaces the token, and the component renders an explicit `<LiveKitRoom>` (`AdvancedMode.tsx:167-181`):

```tsx
{token && session.livekitUrl && (
  <LiveKitRoom
    serverUrl={session.livekitUrl}
    token={token}
    connect={true}
    video={false}
    audio={true}
    onConnected={() => {
      session.markConnected();
      startSessionTimer();
    }}
    onDisconnected={disconnect}
  >
    <LiveKitAvatarProvider session={session} />
  </LiveKitRoom>
)}
```

Read this carefully. `LiveKitRoom` is **MIT** (`@livekit/components-react` 2.9.20, `package.json:13`). The `serverUrl` and `token` are obtained from the proprietary `useAvatarSession` hook. This is the boundary between the open and proprietary surfaces, expressed in JSX. ZeroWeight's SDK mints the credentials and orchestrates the avatar; LiveKit's MIT components carry the audio. Two libraries, two licenses, glued at this single render site.

The `connect={true}` prop makes the Room auto-connect. `video={false}` is critical — the *local user* publishes no video track. `audio={true}` publishes the user's microphone. Both flags are about the *uplink* from the user's browser. The *downlink* (the cloud avatar's audio and rendered video) is subscribed automatically when the SDK avatar publishes those tracks into the Room.

`onConnected` (`:174-177`) fires the two-line readiness handshake — tell the session it's connected, start the timer. `onDisconnected` (`:178`) drops straight back to `disconnect`, the same handler the user can invoke manually. Same code path for "user clicked End Session" and "network died" and "session timer expired" and "remote dropped us". This is the right shape — one teardown function, three triggers.

The `LiveKitAvatarProvider` (`:180`) is a context provider that gives the SDK's internal components access to both the LiveKit Room (via React context from `LiveKitRoom`) and the session state. This is how the avatar canvas, rendered into `session.containerRef`'s div (`:80-92`), gets wired to the Room's subscribed video track without an explicit `<LiveKitAvatarRenderer roomTrack={...} />` element. The provider pattern hides one more layer of subscription plumbing.

The whole `<LiveKitRoom>` element lives inside a `<div className="adv-hidden">` (`AdvancedMode.tsx:165`). `AdvancedMode.css:377-379` sets that class to `display: none`. The Room element renders nothing visible — it's purely a context provider + WebRTC plumbing host. The avatar pixels show up in a *different* div (`AdvancedMode.tsx:80-92`) via the `containerRef`. The renderer subscribes to the Room's video track and paints into the canvas it injects under the ref. This is a clever trick: the React tree has two regions, one of which is "Room context, invisible" and the other is "avatar paint surface, visible".

## The Four Event Handlers

**Handler 1: `handleToggleVolume` (`AdvancedMode.tsx:37-39`).** Three lines. Reads `session.volume`, flips to 0 or 1, calls `setVolume`. The button (`:135-145`) shows `Volume2` or `VolumeX`, and only renders when `isConnected` (`:134`) — a placeholder (`:147-149`, CSS `:360-367`) fills the grid slot when not connected to keep layout stable.

**Handler 2: `handleToogleCharacter` (`AdvancedMode.tsx:41-51`).** Note the typo — "Toogle". Lints out in any real codebase; the kit ships it.

```tsx
const handleToogleCharacter = () => {
  const randomVal = Math.random();
  if (randomVal < 0.3) { session.runAction("embarrassed") }
  else if (randomVal < 0.6) { session.runAction("dance") }
  else { session.runAction("wave_hand") }
}
```

Three hardcoded action names: `"embarrassed"`, `"dance"`, `"wave_hand"`. A random-uniform draw biases 30/30/40. Bound to the avatar canvas's `onClick` (`:84`) — the avatar is, by interaction design, a slot machine. Three loaded observations:

- Action names are **strings**, not enums. `"wave-hand"` vs `"wave_hand"` presumably no-ops silently. See [[22_ACTION_PROTOCOL]].
- The trigger is **user-initiated**, not LLM-initiated. Whether the cloud LLM can trigger actions on its own is `[interface-only]`.
- Randomization is **client-side**. The picker could live in the cloud; the kit puts it in the React component.

**Handler 3: `toggleMic` (destructured, `:28, 101`).** No body in the kit — the hook owns it. The button (`:99-106`) toggles Mic/MicOff icons and CSS classes for muted/unmuted styling (`AdvancedMode.css:269-285`). Always visible (unlike volume), so the user can mute *before* connecting. Thoughtful.

**Handler 4: The connect/disconnect dual button (`AdvancedMode.tsx:109-131`).** One button, three states: "Talk to Zera" → "Connecting..." (disabled, `Loader2` spinner) → "End Session" → back. The styling flips from gradient-purple-pink-orange (`AdvancedMode.css:322-328`) for the "connect" affordance to red-tinted (`:330-336`) for "disconnect". The appearance signals what clicking will do. The kit's strongest UX moment.

## The Hidden LiveKit Room — Why It's Hidden

The kit's pattern: visible part of the tree (controls, canvas container with `containerRef`, timer, status label); invisible part (the `LiveKitRoom` context provider + `LiveKitAvatarProvider` that subscribes to its tracks and renders into the visible canvas). The two are connected by (1) the `session` object passed via `<LiveKitAvatarProvider session={session} />`, (2) `containerRef` attached to the visible canvas div and read by the provider's internal renderer, (3) React context — `LiveKitRoom` publishes the connected Room into context, the avatar provider reads it.

Clean separation, with a price: **the React tree's structure depends on offscreen rendering working correctly**. Replace `display: none` with `display: block` and you see default LiveKit chrome. Mount `<LiveKitRoom>` in the wrong tree (different provider, error boundary above) and the canvas paints nothing. The seam runs through React context; the seam breaks if context propagation breaks. The kit uses StrictMode (`src/main.tsx:7`), which double-invokes effects in development — whether `useAvatarSession`'s cleanup is StrictMode-safe is `[interface-only]`.

## The CSS Half of the Mode

`AdvancedMode.css` is 379 lines — twice the TypeScript. It hides the `<LiveKitRoom>` plumbing via `.adv-hidden` (`:377-379`), stages an animated conic-gradient border (`:54-67`, 3s/revolution), drives the three-color timer transition (`:130-174`), provides hover-and-state variants for every button (`:269-336`), and responsive-breakpoints at 768px and 640px. The CSS does 60% of the polish-work. Replicating the kit's *aesthetic* is a separate, much larger task than replicating its logic.

## Where Advanced Mode Cracks

- **Same hardcoded API key** (`:12`). Advanced mode does not fix basic mode's worst problem.
- **Seventeen-member implicit session contract.** Twelve destructured (`:16-29`) + five reached for (`containerRef`, `setVolume`, `runAction`, `livekitUrl`, `markConnected`) — no `interface AvatarSession` in the kit. `@zeroweight/react` 0.2.38 → 0.3.0 could break any. See [[50_DEPENDENCY_HEALTH]].
- **Zero error handling.** No `catch`, no `error`, no `onError` anywhere. `connect()` throws → user sees what? `[interface-only]`.
- **Avatar-clickable-for-random-action is a toy.** Real apps tie actions to *content*. Kit uses `Math.random()` (`:42`). Right plumbing, wrong policy.
- **No mute-while-AI-speaks observability.** `turnOffMicWhenAISpeaking: true` enables it; UI never shows when active. `[interface-only]` whether `micMuted` reflects SDK-triggered mutes.
- **Volume is binary.** `setVolume(0|1)` only. Slider is one line away; kit declines.
- **No session extension.** No UI to extend without disconnect+reconnect (new auth, new billing).
- **The typo (`handleToogleCharacter`, `:41`).** ESLint config has no spell-check. Indicative of polish level.

## Where Advanced Mode Surprises

- **`startSessionTimer` decoupled from `connect`.** Timer starts on Room-connected, not button-clicked. Many SaaS get this wrong.
- **The connect/disconnect button is one element with three states.** Single affordance always means "change the current state". UX win.
- **The volume button conditionally appears with a stable-layout placeholder** (`:147-149`).
- **The session object is *the* abstraction.** One source of truth, passed by reference. No prop-drilling, no Redux slice duplication.
- **`video={false}, audio={true}`** (`:171-172`). User publishes no video; only audio uplink. Avatar pushes back video. The asymmetry that makes this "cloud avatar" rather than "video chat" — architecturally definitional, easy to miss.

## Cross-References

- [[30_BASIC_MODE_FLOW]] — what advanced mode is the unboxing of; the eight hidden behaviors made visible here
- [[20_ZEROWEIGHT_SURFACE]] — `useAvatarSession` and `LiveKitAvatarProvider` interface analysis based on the usage shown here
- [[21_LIVEKIT_INTEGRATION]] — `LiveKitRoom` (`AdvancedMode.tsx:168`) is the explicit, MIT-licensed surface — full doc on what to mine
- [[22_ACTION_PROTOCOL]] — the action contract behind `runAction("dance")` at `:46`
- [[12_DEPENDENCY_STACK]] — `lucide-react` 1.7.0 was published as ESM-only and may break with older bundlers; relevant when stripping kit-derived patterns into Ember
- [[50_DEPENDENCY_HEALTH]] — major-version brittleness of `@zeroweight/react` 0.2.x; the seventeen-member session object is a moving target
- [[51_SECURITY_AND_PRIVACY]] — the hardcoded API key persists in advanced mode (`:12`); mic capture posture; cloud audio surface
- [[sap:32_AVATAR_RENDER_PIPELINE]] — SAP's local-tier equivalent; five named subsystems vs. one fat `session` object
- [[sap:60_TRUE_NAME_REASSIGNMENT]] — Andlit/Rödd True Names that this surface should bind to

## What This Means for Ember

**Adopt:**

- **`LiveKitRoom` with `connect={true}`, `video={false}`, `audio={true}` semantics** (`AdvancedMode.tsx:168-172`). This is the MIT-licensed open-source surface that Ember should build Andlit-realtime on top of. The Room API is documented at `https://docs.livekit.io/` and the source is at `livekit/components-js` on GitHub. Bind to a typed Ember `CloudSession.audioOnly()` resource that constructs the Room with these flags as defaults.
- **`onConnected` → `markConnected()` + `startSessionTimer()` choreography** (`AdvancedMode.tsx:173-177`). Decoupling "Room is connected" from "billable session starts" is the right design and is a free MIT-shaped pattern. Adopt: Ember's CloudSession should not start meter-relevant timers until the user-facing pipeline is actually usable.
- **`onDisconnected → disconnect()` single-teardown convergence** (`AdvancedMode.tsx:178`). Wire user-disconnect, error-disconnect, timeout-disconnect, and network-disconnect to the same teardown function. Ember's CloudSession.teardown() must be idempotent and reachable from at least four triggers.
- **The "session as one object, destructured at use site" shape**. Not the proprietary content of `useAvatarSession`, but the pattern: one hook returns one big object with both state and mutators, and the component does not maintain duplicate state. Adopt as the React-binding shape for any future Ember presence components, with the hook backed by Ember-owned state (not a cloud SDK).
- **`turnOffMicWhenAISpeaking`-as-a-named-policy.** The flag is good; the implementation should be Ember's, not a vendor's. Adopt the *policy name* as a typed `BargeInPolicy` enum (`{semiDuplex, fullDuplex, vadGated, pttOnly}`) so that Ember can choose explicitly.

**Adapt:**

- **The dual-mode pattern** (one product, two integration surfaces — see [[11_DUAL_MODE_PATTERN]]) — but Ember's two modes should be **tier-local** and **tier-cloud**, not "easy" and "advanced". Local is the default for the embodiment slice; cloud is opt-in for high-fidelity. Same dual-surface architecture, different axis.
- **The three-color countdown timer** (`:71-75`, CSS `:130-174`) — adapt as a generic `BudgetIndicator` that warns at 50% and 90% of *any* tier-budgeted resource (cloud time, GPU memory, token spend). Kit ships one indicator for one budget; Ember generalizes to N.
- **The hidden-Room + visible-canvas split** (invisible `:165`, visible `:80-92`). Adapt as a typed `PresenceRenderTree` pair: `<PresencePlumbing>` carries realtime tracks/sockets, `<PresenceSurface>` is where the user looks. SAP's two-window pattern (`[[sap:32_AVATAR_RENDER_PIPELINE]]`) is the OS-level equivalent.
- **The connect/disconnect button with state-driven label** (`:109-131`) — replace `"Talk to Zera"` with configurable `presence.greetingLabel`.
- **The action-trigger-via-string-name** (`:45`). Adapt the *shape* (function takes an action name, returns a promise); names come from a typed catalog (`Action.Embarrassed`), not free-form strings. See [[22_ACTION_PROTOCOL]].

**Avoid:**

- **The seventeen-member implicit session contract.** Ember's equivalent must export a published `interface CloudSession` and follow semver. The kit gets away with implicit shape because everything is one codebase; Ember's API will be consumed by sibling projects.
- **Hardcoded `Math.random()` action selection** (`:42-50`). Actions must be content-triggered (LLM tag → action with Hjarta-state filtering — see `[[sap:1A_AFFECTION_DOMAIN]]`).
- **The avatar-as-slot-machine onClick** (`:84`). For an Ember-grade companion this feels disrespectful — pokes the body for a random response. Interaction needs intentionality.
- **Hardcoded display name in source** (`"Talk to Zera"`, `:128`). Configuration concern, not code concern.
- **No error UX.** Zero `catch` and zero error-rendering branches. Any Ember adoption must add an `errorState` slice rendered visibly. Cloud sessions fail; users deserve to know why.
- **`display: none` on the realtime-transport subtree** (`AdvancedMode.css:377-379`). Fragile — a theme accidentally re-styling `.adv-hidden` exposes default LiveKit chrome. Use React portals (`createPortal` to a non-rendered host) or a headless API instead.

**Invent:**

- **The `PresenceCanvas` resource with declared `tier` capability.** The kit binds the avatar to `containerRef` (`:81`) implicitly. Ember's equivalent should be `const canvas = createPresenceCanvas({tier: 'cloud-rendered', maxLatencyMs: 200, fallback: 'overlay-tier'})`, where the canvas resource declares the tier it expects, the latency budget it's willing to tolerate, and the *fallback* presence surface to graduate down to if the requested tier becomes unavailable. The kit collapses presence to one canvas; Ember should make the tier-graduation explicit at the canvas level — directly ties to `[[sap:63_PERFORMANCE_TIER_ENGINE]]`.
- **Named BargeInPolicy with content-derived selection** (Vow-tied to the proposed Affective Restraint Vow from Wave 3). The kit's `turnOffMicWhenAISpeaking: true` is a single Boolean. Ember should expose `BargeInPolicy.{semiDuplex, fullDuplex, vadGated, pttOnly}` and bind the active policy to *the conversation state in Hjarta* — heated conversation? Allow barge-in. Tender moment? Suppress barge-in. Confessional? Push-to-talk. This makes the avatar's listening behavior emotionally aware. Invent as a typed surface, not a Boolean.
- **The `runAction` Mediator** (Vow-tied to Affective Restraint). All `runAction(name)` calls pass through a Mediator that consults Hjarta-state and the conversation context to decide whether the action is appropriate *right now*. `runAction("dance")` during a serious conversation no-ops with a log. The kit's `Math.random()` becomes Ember's principled rejection layer. See `[[22_ACTION_PROTOCOL]]`.
- **The CloudSession-as-typed-resource pattern, formalized.** Continuation of the Invent from [[30_BASIC_MODE_FLOW]]. `useAvatarSession` is the closest the kit comes to typing this surface and it still leaks seventeen members. Ember's `CloudSession` is a single class with explicit constructor (`new CloudSession({tokenMinter, signalUrl, scope, deadline})`), explicit lifecycle (`connect()`, `disconnect()`, `extendDeadline(s)`), explicit subscription channels (`session.on('frame'|'audio'|'action-completed', cb)`), and teardown enforcement via context manager / `using` declaration that fires `disconnect()` on uncaught throws. Wraps `LiveKitRoom`; never replaces it.
- **The Andlit-Realtime Auto-Degradation Ladder.** When the cloud session fails (network, billing, outage), advanced mode just disconnects. Ember should *auto-degrade* through a declared ladder: cloud-rendered → local-VRM → text-overlay-with-voice → text-only → log-only — each rung a tier from `[[sap:63_PERFORMANCE_TIER_ENGINE]]`. Degradation is *visible* ("Andlit lost realtime; speaking via overlay now") and *reversible* when conditions improve. The kit goes "connected" → "nothing"; Ember never reaches "nothing".


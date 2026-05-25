---
codex_id: 20_ZEROWEIGHT_SURFACE
title: The ZeroWeight Surface — Hooks, Components, and the Provider Triad
role: Architect
layer: Interface
status: draft
waifu_source_refs:
  - src/modes/BasicMode.tsx:3
  - src/modes/BasicMode.tsx:19-25
  - src/modes/AdvancedMode.tsx:6
  - src/modes/AdvancedMode.tsx:10-29
  - src/modes/AdvancedMode.tsx:37-51
  - src/modes/AdvancedMode.tsx:80-93
  - src/modes/AdvancedMode.tsx:167-181
  - package.json:14-15
ember_subsystem_targets: [Munnr]
cross_refs:
  - 10_domain/10_DOMAIN_MAP
  - 10_domain/11_DUAL_MODE_PATTERN
  - 10_domain/12_DEPENDENCY_STACK
  - 20_interface/21_LIVEKIT_INTEGRATION
  - 20_interface/22_ACTION_PROTOCOL
  - 30_execution/30_BASIC_MODE_FLOW
  - 30_execution/31_ADVANCED_MODE_FLOW
  - 50_verification/51_SECURITY_AND_PRIVACY
  - 60_synthesis/60_REALTIME_TIER_FOR_ANDLIT
  - sap:25_AVATAR_PROTOCOL
---

# The ZeroWeight Surface
## Hooks, Components, and the Provider Triad

*— Rúnhild Svartdóttir, Architect*

> *The face is the part of the body that lies most easily. You can hold a face still while everything behind it is in motion. The waifu kit imports a face from somewhere else and never looks behind it; we do the looking it didn't.*

`@zeroweight/react` ^0.2.38 is the proprietary SDK at the heart of the kit. Its npm page is reachable; its **source is not** — `npm view @zeroweight/react` returns the manifest, but the published tarball's source is not openly browsable, and the company does not publish source on GitHub at the time of writing. This document catalogues what the SDK *exposes* — its visible interface — strictly from the outside, citing the kit's three usage sites. Every claim is marked `[interface-only — proprietary SDK]` unless directly verifiable from the kit. The SDK's *behaviour* is inferred from its observed surface; never from claims the SDK makes about itself.

This is the right way to study a proprietary surface. You learn the contract from the caller, not the callee. The interface is the part that *cannot lie* — if the kit imports `useAvatarSession`, the function exists with that name; if the kit destructures `{token, isConnected, isConnecting, ...}` from its return, those fields exist with at least those names. The semantics behind each field are inferred and so are marked.

---

## 1. The Three Public Symbols

`@zeroweight/react` exposes (at minimum) three symbols used by the kit:

| Symbol | Kind | Imported by | Purpose (inferred) |
|---|---|---|---|
| `LiveKitAvatarSession` | React component | `src/modes/BasicMode.tsx:3` | Self-contained avatar session embed; prebuilt path |
| `useAvatarSession` | React hook | `src/modes/AdvancedMode.tsx:6` | Composable session state + verbs; advanced path |
| `LiveKitAvatarProvider` | React component (context provider) | `src/modes/AdvancedMode.tsx:6` | Couples LiveKit Room state into the session hook |

Whether the package exports more is unknown from the kit. The kit consumes three; the package may export many more. This itself is a teaching: **the visible API of an SDK is the *intersection* of its exports and its consumers' usage**. Anything not used is not catalogued — and anything in the catalogue is grounded in usage, not in documentation claims.

Additionally, `@zeroweight/renderer` ^0.2.43 is named as a dependency in `package.json:15` but is **never imported in the kit's TypeScript**. This means it is either:

- A *peer/transitive* dependency that `@zeroweight/react` pulls in to do the actual WebGL injection — most likely.
- A direct-dep listed in the kit's `package.json` for the user's reference but never imported by the kit's own files — possible.

The kit's source resolves the question by absence: there is no `import` from `@zeroweight/renderer` anywhere in `src/`. The renderer's surface is thus *entirely indirect*; it manifests in the kit only as "the WebGL canvas that appears inside `session.containerRef.current`." We treat the renderer as a hidden engine driven by the React SDK; we do not catalogue its API because the kit does not consume it.

---

## 2. `LiveKitAvatarSession` — The Prebuilt Component

### 2.1 Visible signature

From `src/modes/BasicMode.tsx:19-25`, the component takes (at least) the following props:

```typescript
// /tmp/waifu-chat-starter-kit/src/modes/BasicMode.tsx:19-25
<LiveKitAvatarSession
  avatarId="your-avatar-id"
  apiKey="your-api-key"
  sessionDuration={120}
  inactivityTimeout={30000}
  showBorder={false}
/>
```

**Inferred TypeScript shape** `[interface-only — proprietary SDK]`:

```typescript
interface LiveKitAvatarSessionProps {
  avatarId: string;          // ZeroWeight avatar identifier
  apiKey: string;            // ZeroWeight API key (cloud-side issuer)
  sessionDuration?: number;  // seconds; the kit passes 120 (2 minutes)
  inactivityTimeout?: number; // ms; the kit passes 30000 (30 seconds)
  showBorder?: boolean;      // visual styling toggle
  // ...additional props unknown
}
```

The five props consumed by the kit are the *known* surface. The component likely accepts more — `className`, `style`, `onConnected`, `onDisconnected` are typical for a prebuilt component — but the kit does not exercise them, so we do not claim them.

### 2.2 Inferred behaviour

The component **encapsulates the entire avatar session lifecycle internally**. The kit passes only credentials and timing, and the component:

1. Issues a token request to ZeroWeight cloud (with `avatarId` + `apiKey`) `[interface-only]`
2. Receives a LiveKit URL + JWT in response `[interface-only]`
3. Internally mounts a LiveKit `Room` (using `livekit-client`, which is also in the dep list)
4. Publishes the local mic track to the room
5. Subscribes to remote tracks from the room (the avatar's audio + video)
6. Injects the avatar's WebGL canvas into its own internal DOM
7. Enforces `sessionDuration` by triggering an internal disconnect after the configured seconds
8. Enforces `inactivityTimeout` by listening for "no audio activity" signals (mic threshold + remote-track signals) and disconnecting after silence

All of this is invisible to the kit. The component's entire *interface* is the five props. The component's entire *behaviour* is what those five props parameterise. This is a **black box with a tiny surface and a large interior** — the canonical prebuilt-component shape.

### 2.3 What the prebuilt cannot do (observed by absence)

BasicMode wraps the component in `<motion.div drag>` (`src/modes/BasicMode.tsx:13`) — the drag is *external*; framer-motion repositions the parent DOM, the canvas inside is dragged passively. Inference: **the component does not own its own positioning**. By similar absence-reading: no render-props/slot mechanisms in the kit's usage, no `ref` API, no `onError` handler. Whether limitation or merely unused is unknowable; the safe Ember inference is to assume limitation and design with the missing affordances — render-props, ref-forwarding, error callbacks.

---

## 3. `useAvatarSession` — The Composable Hook

### 3.1 Visible signature

From `src/modes/AdvancedMode.tsx:10-14`:

```typescript
// /tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:10-14
const session = useAvatarSession({
  avatarId: "your-avatar-id",
  apiKey: "your-api-key",
  turnOffMicWhenAISpeaking: true,
});
```

Three known parameters: `avatarId`, `apiKey`, and `turnOffMicWhenAISpeaking`. The third is new — it does not appear in `LiveKitAvatarSession`'s prop list — and signals one of the SDK's behaviour controls: when set true, the SDK auto-mutes the user's mic while the avatar is speaking. This is a *barge-in policy*. The default value is unknown but the kit explicitly passes `true`.

### 3.2 The destructured return shape

From `src/modes/AdvancedMode.tsx:16-29`:

```typescript
// /tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:16-29
const {
  token,
  isConnected,
  isConnecting,
  isEngineReady,
  isLoadingActions,
  micMuted,
  volume,
  timeRemaining,
  connect,
  disconnect,
  toggleMic,
  startSessionTimer,
} = session;
```

Twelve fields destructured at line 16-29. Plus, observable elsewhere in the file: `session.containerRef` (`src/modes/AdvancedMode.tsx:81`), `session.runAction(name: string)` (`src/modes/AdvancedMode.tsx:45-49`), `session.setVolume(v: number)` (`src/modes/AdvancedMode.tsx:38`), `session.markConnected()` (`src/modes/AdvancedMode.tsx:175`), `session.livekitUrl` (`src/modes/AdvancedMode.tsx:167,169`).

The full known surface, organised by kind:

**State fields (read-only on session):**
| Field | Inferred type | Inferred meaning |
|---|---|---|
| `token` | `string \| null` | LiveKit JWT, populated after `connect()` succeeds |
| `livekitUrl` | `string \| null` | LiveKit server WebSocket URL, populated after `connect()` |
| `isConnected` | `boolean` | True after LiveKit room is fully connected |
| `isConnecting` | `boolean` | True during the token-issuance + room-connect handshake |
| `isEngineReady` | `boolean` | True when the WebGL renderer has finished initialising |
| `isLoadingActions` | `boolean` | True while the action vocabulary is being fetched |
| `micMuted` | `boolean` | True if the local mic is muted |
| `volume` | `number` | Remote-audio volume, observed as `>0` or `0` in the kit's binary toggle |
| `timeRemaining` | `number` | Seconds remaining in the session — counts down from `sessionDuration` (default unknown for the hook) |

**Verb methods (called by the kit):**
| Method | Inferred signature | Inferred behaviour |
|---|---|---|
| `connect()` | `() => Promise<void>` | Request token, mount room, publish mic, subscribe avatar |
| `disconnect()` | `() => void` | Tear down the room, unpublish mic, clean up |
| `toggleMic()` | `() => void` | Flip `micMuted`; emit local-track mute/unmute |
| `setVolume(v: number)` | `(v: number) => void` | Set remote-audio output volume; the kit uses 0 / 1 only |
| `runAction(name: string)` | `(name: string) => void` | Trigger a named action on the avatar (see [[22_ACTION_PROTOCOL]]) |
| `markConnected()` | `() => void` | Tell the hook "the LiveKit room is now connected" — manual handshake callback |
| `startSessionTimer()` | `() => void` | Begin the `timeRemaining` countdown — called from `onConnected` |

**Refs (passed to JSX as `ref={...}`):**
| Field | Inferred type | Inferred meaning |
|---|---|---|
| `containerRef` | `RefObject<HTMLDivElement>` | Mount point for the WebGL canvas; the renderer injects its `<canvas>` here |

That's **9 state fields + 7 verbs + 1 ref = 17 surface elements** for the hook. Plus the input config object (3+ fields). For comparison, `LiveKitAvatarSession`'s prop surface is 5 elements. The hook is ~3.5× wider — and that width is the entire reason `AdvancedMode.tsx` is 6× longer than `BasicMode.tsx` ([[11_DUAL_MODE_PATTERN]] §2.3).

### 3.3 The handshake split

The hook's most architecturally significant feature is the **explicit handshake split**. `BasicMode` does everything in one mount. `AdvancedMode` requires the developer to: call `useAvatarSession({...})`, call `connect()`, wait for `token && session.livekitUrl` truthiness (`src/modes/AdvancedMode.tsx:167`), manually mount `<LiveKitRoom>`, wrap its contents with `<LiveKitAvatarProvider session={session}>` (`src/modes/AdvancedMode.tsx:180`), and in `onConnected` manually call `session.markConnected()` and `startSessionTimer()` (`src/modes/AdvancedMode.tsx:174-177`).

The hook **issues the token but does not mount the room**; the hook **knows it should start the timer but does not start it**. Both are the developer's responsibility. This decoupling is the *cost* of the composable path and its *value* — `<LiveKitRoom>` could be swapped for a different WebRTC abstraction (custom mount, audio-only mock, test harness) without rewriting the hook.

---

## 4. `LiveKitAvatarProvider` — The Bridging Context

### 4.1 Visible signature

From `src/modes/AdvancedMode.tsx:180`:

```typescript
// /tmp/waifu-chat-starter-kit/src/modes/AdvancedMode.tsx:180
<LiveKitAvatarProvider session={session} />
```

One prop: `session` — the return value of `useAvatarSession()`. Rendered as a *void child* of `<LiveKitRoom>` (no children of its own; `/>` self-closes).

### 4.2 Inferred behaviour `[interface-only — proprietary SDK]`

The provider's role is to **bridge LiveKit Room state into the ZeroWeight session hook**. It is rendered *inside* `<LiveKitRoom>` (so it has access to the LiveKit React context) and is given `session` as a prop (so it can call session methods).

What this almost certainly does internally:

- Subscribes to LiveKit room events (track-subscribed, track-unsubscribed, participant-events, disconnected)
- Translates LiveKit track-subscribed events for the avatar's audio track into "play this audio with `session.volume`" semantics
- Translates LiveKit track-subscribed events for the avatar's video track into a sink that the WebGL renderer can consume
- Calls internal session methods to update `isEngineReady`, audio-out routing, etc.

The provider is the **glue between two SDKs**. Without it, the LiveKit room would be connected but the avatar would never render — the room is just a WebRTC pipe; something has to *interpret* the avatar-side tracks. `LiveKitAvatarProvider` is that interpreter.

### 4.3 Why this matters architecturally

The provider proves a key fact about the SDK: **it does not subsume LiveKit; it consumes LiveKit**. The two SDKs are sibling layers, glued by this component. ZeroWeight chose *not* to hide LiveKit (that is what `LiveKitAvatarSession` does for the basic path) but to *expose* it so the advanced path can compose them. Generous SDK design — the developer keeps access to LiveKit's full surface (could mount `<LiveKitRoom video={true}>` for video, could use `useTracks()` for a custom video render) at the cost of complexity. The provider is the *minimum coupling* needed.

For Ember: **adopt the bridge pattern**. Any cloud-tier coupling of two third-party SDKs is one typed object consuming both surfaces, exposing a unified internal protocol. See **Invent** below.

---

## 5. The Inferred Lifecycle State Machine

From the field set (`isConnecting`, `isConnected`, `isEngineReady`, `isLoadingActions`) we can reconstruct the SDK's internal state machine:

```
                       ┌────────────────────┐
                       │      idle          │ ← initial; token=null
                       │  isConnected:false │
                       │  isConnecting:false│
                       │  isEngineReady:false│
                       └─────────┬──────────┘
                                 │ connect()
                                 ▼
                       ┌────────────────────┐
                       │    connecting      │
                       │  isConnecting:true │
                       │  isConnected:false │
                       │  token:null→string │
                       └─────────┬──────────┘
                                 │ <LiveKitRoom> mounts;
                                 │ onConnected fires;
                                 │ markConnected() called
                                 ▼
                       ┌────────────────────┐
                       │     connected      │
                       │  isConnecting:false│
                       │  isConnected:true  │
                       │  isEngineReady:?   │
                       └─────────┬──────────┘
                                 │ renderer initialises;
                                 │ engine reports ready
                                 ▼
                       ┌────────────────────┐
                       │   engine_ready     │
                       │  isConnected:true  │
                       │  isEngineReady:true│
                       └─────┬─────┬────────┘
                             │     │ actions load
                             │     ▼
                             │  ┌────────────────────┐
                             │  │  actions_loading   │
                             │  │ isLoadingActions:T │
                             │  └─────────┬──────────┘
                             │            │
                             │            ▼
                             │  ┌────────────────────┐
                             │  │   actions_ready    │
                             │  │ isLoadingActions:F │
                             │  │ runAction() valid  │
                             │  └────────────────────┘
                             │
                             │ disconnect() OR timeRemaining=0 OR inactivity
                             ▼
                       ┌────────────────────┐
                       │     idle (reset)   │
                       └────────────────────┘
```

This state machine is **inferred entirely from the observed field set** — the contract Ember would need to implement when wrapping the SDK in a `CloudAvatarProvider` typed protocol. Transitions worth noticing: `connecting → connected` requires `markConnected()` to be called manually in the advanced path; `connected → engine_ready` is asynchronous and reported via `isEngineReady` (the kit uses this for its loader at `src/modes/AdvancedMode.tsx:87-91`); `isLoadingActions` is orthogonal to `isConnected` — actions can load after connection, as the kit's status bar acknowledges (`src/modes/AdvancedMode.tsx:155-157`).

---

## 6. Where the Surface Cracks (and What That Teaches)

### 6.1 The opaque internal — black-box failure modes

When a session fails — token error, LiveKit handshake failure, renderer crash — the kit's only signal is *state flags going false*. There is no `onError` callback or `session.lastError` field observable. The user clicks "Talk to Zera"; the button shows "Connecting..."; if it never transitions, there is no UI affordance to find out why. A significant gap. Any production user needs to wrap the hook in retry + error-surface layers. Malpractice for production, understandable for teaching.

### 6.2 The `runAction` vocabulary is implicit

Three strings: `"embarrassed"`, `"dance"`, `"wave_hand"` (`src/modes/AdvancedMode.tsx:45-49`). The SDK accepts arbitrary strings; no enum, no type-safety, no compile-time validation. See [[22_ACTION_PROTOCOL]] for the full failure surface.

### 6.3 The implicit canvas-render contract

`session.containerRef` is passed to a `<div>` (`src/modes/AdvancedMode.tsx:81`). The renderer injects a `<canvas>` via DOM manipulation. The kit cannot resize, restyle (beyond the wrapping div's CSS), or unmount the canvas. If injection fails — renderer crash, race, ref unset — the `<div>` stays empty and the loader (`src/modes/AdvancedMode.tsx:87-91`) hangs forever. The contract is implicit; Ember's equivalent must declare it explicitly.

### 6.4 The crisp parts

- **The dual entry symbols** (`<LiveKitAvatarSession>` vs `useAvatarSession()`) are a clean dual-mode shape ([[11_DUAL_MODE_PATTERN]]). Each is *minimal-for-its-purpose*.
- **The provider component** (`<LiveKitAvatarProvider session={session} />`) is a single-prop bridge — the right shape for cross-SDK glue.
- **The handshake split** between hook and LiveKit room is explicit and well-articulated. The developer knows exactly what the hook owns and what they must do.
- **The state-flag surface** (`isConnecting`, `isConnected`, `isEngineReady`, `isLoadingActions`) is a useful state-machine projection. The flags are independent enough to drive UI without false implications.

---

## 7. Cross-References

- [[10_DOMAIN_MAP]] §1 row 6 for where the ZeroWeight surface fits in the macro shape
- [[11_DUAL_MODE_PATTERN]] for how this surface enables the dual-mode integration
- [[12_DEPENDENCY_STACK]] §2.5 for the 0.x brittleness implications
- [[21_LIVEKIT_INTEGRATION]] for the MIT counterpart this SDK couples with
- [[22_ACTION_PROTOCOL]] (Auditor) for the `runAction` vocabulary analysis
- [[30_BASIC_MODE_FLOW]] (Forge) for the prebuilt-path runtime walkthrough
- [[31_ADVANCED_MODE_FLOW]] (Forge) for the composable-path runtime walkthrough
- [[51_SECURITY_AND_PRIVACY]] (Auditor) for the credential-handling failure modes
- [[60_REALTIME_TIER_FOR_ANDLIT]] (Cartographer) for the Andlit-cloud-realtime proposal
- [[sap:25_AVATAR_PROTOCOL]] for SAP's local avatar protocol contract — the local↔cloud comparison

---

## What This Means for Ember

**Adopt:**
- **The split between state-fields and verb-methods on a session object.** The shape `{isConnected, isConnecting, ..., connect, disconnect, ...}` is the right way to expose a stateful session: *state is readable; transitions are verbs*. This is a known good pattern (it appears in React Query, Zustand, the Web's `MediaRecorder` API). The kit consumes it well. Adopt the *pattern*, not kit code: Ember's `CloudSession` Python dataclass exposes the same shape, with verbs as async methods that emit Sögumiðla events.
- **The handshake-split decoupling.** The hook issues the token; the developer mounts the room; the developer calls `markConnected()` to close the loop (`src/modes/AdvancedMode.tsx:175`). This is the right shape for any cross-SDK glue — *don't auto-couple; require explicit acknowledgement*. Ember's `CloudSession.connect()` returns a coroutine that *waits* for `mark_connected()` to be called by the LiveKit-room manager; otherwise the session stays in `connecting` indefinitely.
- **The single-prop provider component** `<LiveKitAvatarProvider session={session} />` as the **bridge component pattern**. When Ember couples two third-party services, the bridge is one object that takes both surfaces and unifies them. Adopt the *shape* of the bridge, not the SDK's particular implementation.

**Adapt:**
- **The 17-element session surface** (9 fields + 7 verbs + 1 ref) — adapt by *trimming* what Ember doesn't need. Ember's `CloudSession` likely exposes 6-8 fields and 4-5 verbs; the SDK's wider surface reflects React-render-update patterns that Ember's Python doesn't have (no need for `isConnecting` and `isConnected` as separate booleans when `state: ConnectionState` enum suffices). The pattern is right; the dimensionality should be smaller.
- **The `turnOffMicWhenAISpeaking: true` config** (`src/modes/AdvancedMode.tsx:13`) — adapt as Ember's **Barge-In Policy** typed config. A boolean is too coarse. Ember declares: `barge_in_policy: 'always' | 'with_grace_period' | 'never'`, with grace period configurable (in milliseconds), and emits Sögumiðla events on barge-in suppression for audit.
- **The `containerRef` mount-point contract** — adapt to Ember's web surface (if any) as a typed `MountPoint` Pydantic model with `on_inject` / `on_cleanup` callbacks. The kit's implicit contract (provider injects, provider cleans up, no notification) is too quiet.
- **The state machine inferred in §5** — adapt as Ember's `CloudSessionState` enum with explicit transitions in code, not implicit in flag-combinations. The kit derives state from flag-tuples; Ember declares state as a typed enum and *derives* flag tuples from it (the opposite direction, with the same surface).

**Avoid:**
- **The `runAction(name: string)` with no validation.** The kit accepts any string. Ember's `CloudSession.run_action(name: ActionName)` takes a `Literal['embarrassed', 'dance', 'wave_hand', ...]` typed union populated at session-start from a capability probe. Unsafe actions are caught at the type-check, not at runtime.
- **The absent `onError` surface.** Ember's `CloudSession` exposes `on_error: Callable[[SessionError], None]` (or, in Python, emits typed `SessionError` exceptions and corresponding Sögumiðla events). Silent failure modes are forbidden.
- **The 0.x SDK as a hard dependency on the critical path.** Already addressed in [[12_DEPENDENCY_STACK]] §3.4 — Ember insulates via a typed adapter; this doc adds the *concrete shape* of that adapter.
- **The opaque WebGL injection.** Ember's avatar surface declares: *"The provider does X to mount Y at time Z, and notifies via callback Q."* No implicit DOM mutation.

**Invent:**
- **The Surface-By-Usage Catalogue.** When Ember integrates a proprietary SDK, the first step is to produce a `surface.yaml` listing every symbol the SDK exposes that Ember consumes — exactly what this doc does for `@zeroweight/react`. The catalogue is **the contract from Ember's side**; if the SDK changes, the catalogue tells us what's affected. The catalogue lives in `docs/external_surfaces/<sdk-name>.yaml`. Each entry has `name`, `kind`, `usage_site`, `inferred_signature`, `inferred_behaviour`, `breakage_blast_radius`.
- **The Bridge Component Vow.** Any Ember code that couples two external services declares a typed `Bridge` class. The bridge consumes both surfaces, exposes a unified internal protocol, and is the *only* point of coupling. `LiveKitAvatarProvider` is the kit's bridge; Ember's equivalent is `CloudAvatarBridge(zeroweight: CloudAvatarProvider, livekit: LiveKitClient) -> AndlitRealtimeSurface`. The bridge is testable; the bridge can be swapped to mock both sides for unit tests; the bridge is the seam.
- **The State-Machine Reconstruction Rite.** When Ember integrates an SDK that does not document its internal state machine, the integrating engineer produces an *inferred* state machine diagram (as in §5 above) from the observable surface — and that diagram becomes part of the SDK's surface catalogue. The kit does not provide one; we built one. Ember requires this artefact before integrating any opaque SDK.
- **The Engine-Ready Decoupling.** Ember separates "connection established" (network handshake done) from "engine ready" (the rendering or processing engine is initialised) as distinct states with distinct callbacks. The SDK's `isConnected` vs `isEngineReady` split is the right shape — generalise it: every Ember presence tier has a `connected` state separate from a `ready` state, and the gap between them is where loading UIs and patience belong.
- **The Implicit-Contract Surfacing.** When the SDK has an implicit contract (the renderer injects into `containerRef`; the kit's `<div>` is the mount point), Ember's adapter *makes the contract explicit* — typed methods like `mount_canvas(parent: Element) -> Canvas`, `dispose_canvas(canvas: Canvas)`. The kit consumes implicit contracts; Ember translates them to explicit ones at the adapter boundary.
